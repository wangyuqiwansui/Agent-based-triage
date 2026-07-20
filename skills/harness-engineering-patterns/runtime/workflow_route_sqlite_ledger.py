"""Transactional multi-writer workflow route ledger / 事务型多写者工作流路由账本。

SQLite is the local reference database adapter. Each operation opens its own
connection, takes a database write reservation with ``BEGIN IMMEDIATE``, reloads
and validates the authoritative route chain, and commits the new record plus
the stream head in one transaction. It is not a distributed-consensus store.
/ SQLite 是本地参考数据库适配器。每次操作使用独立连接，通过
``BEGIN IMMEDIATE`` 取得数据库写预留，重新加载并校验权威路由链，再在同一
事务内提交新记录与流头。它不属于分布式共识存储。
"""

from __future__ import annotations

from contextlib import closing, contextmanager
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator, Mapping, Sequence

try:  # Package import / 包导入
    from .reasoning_artifacts import artifact_fingerprint, validate_workflow_route_envelope
    from .workflow_route_ledger import WorkflowRouteLedger, WorkflowRouteLedgerError
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import artifact_fingerprint, validate_workflow_route_envelope
    from workflow_route_ledger import WorkflowRouteLedger, WorkflowRouteLedgerError


SQLITE_ROUTE_SCHEMA_VERSION = 1
_STREAM_PREFIX = "WORKFLOW_ROUTE_STREAM_"
_STREAM_IDENTITY_FIELDS = ("workflow_id", "task_id", "run_id", "scene_id")


def _detached(value: Any) -> Any:
    return deepcopy(value)


def _canonical_text(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _stream_identity(envelope: Mapping[str, Any]) -> dict[str, str]:
    return {
        **{field: envelope[field] for field in _STREAM_IDENTITY_FIELDS},
        "task_atom_id": envelope["task_atom"]["task_atom_id"],
    }


def workflow_route_stream_key(envelope: Mapping[str, Any]) -> str:
    """Derive the stable database stream key from immutable route identity.

    / 从不可变路由身份派生稳定数据库流键。
    """

    validate_workflow_route_envelope(envelope)
    digest = artifact_fingerprint(_stream_identity(envelope)).removeprefix("sha256:")
    return _STREAM_PREFIX + digest


def _validate_stream_key(stream_key: str) -> None:
    if (
        not isinstance(stream_key, str)
        or not stream_key.startswith(_STREAM_PREFIX)
        or len(stream_key) != len(_STREAM_PREFIX) + 64
        or any(character not in "0123456789abcdef" for character in stream_key[-64:])
    ):
        raise WorkflowRouteLedgerError(
            "invalid workflow route stream key / 工作流路由流键无效"
        )


class SqliteWorkflowRouteLedger:
    """Own many route streams with atomic multi-writer commit and replay.

    / 以原子多写者提交与重放方式管理多条路由流。
    """

    def __init__(
        self,
        database_path: str | Path,
        *,
        max_switches: int = 8,
        busy_timeout_ms: int = 5_000,
    ) -> None:
        if max_switches < 1:
            raise ValueError("max_switches must be positive / max_switches 必须为正整数")
        if busy_timeout_ms < 1:
            raise ValueError(
                "busy_timeout_ms must be positive / busy_timeout_ms 必须为正整数"
            )
        self.database_path = Path(database_path)
        if str(database_path) == ":memory:":
            raise ValueError(
                "connection-local :memory: databases are unsupported / "
                "不支持连接私有的 :memory: 数据库"
            )
        self.max_switches = max_switches
        self.busy_timeout_ms = busy_timeout_ms
        self._initialize()

    def register_initial(
        self,
        envelope: Mapping[str, Any],
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Atomically create a stream with its immutable first route.

        / 原子创建路由流及其不可变第一版路由。
        """

        sealed = _detached(dict(envelope))
        validate_workflow_route_envelope(sealed)
        stream_key = workflow_route_stream_key(sealed)
        with self._transaction(write=True) as connection:
            stream, core = self._load_core(connection, stream_key)
            if core is None:
                core = WorkflowRouteLedger(max_switches=self.max_switches)
            before_count = len(core.committed_records)
            result = core.register_initial(sealed, idempotency_key=idempotency_key)
            if len(core.committed_records) == before_count:
                return result
            record = core.committed_records[-1]
            if stream is not None:
                raise WorkflowRouteLedgerError(
                    "route stream exists without an idempotent initial record / "
                    "路由流已存在但没有幂等初始记录"
                )
            self._insert_stream(connection, stream_key, record)
            self._insert_record(connection, stream_key, record)
            return result

    def append_revision(
        self,
        candidate_envelope: Mapping[str, Any],
        *,
        idempotency_key: str,
        trigger_class: str,
        direction: str,
        trigger_reason_code: str,
        trigger_evidence_bindings: Sequence[Mapping[str, Any]],
        actor_binding: Mapping[str, Any],
        authority_binding: Mapping[str, Any],
        hysteresis_evidence_bindings: Sequence[Mapping[str, Any]] = (),
        budget_impact: Mapping[str, Any] | None = None,
        unfinished_step_ids: Sequence[str] = (),
        switch_event_binding: Mapping[str, Any] | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """Serialize, validate, and commit one route revision.

        / 串行化、校验并提交一条路由修订。
        """

        candidate = _detached(dict(candidate_envelope))
        validate_workflow_route_envelope(candidate)
        stream_key = workflow_route_stream_key(candidate)
        with self._transaction(write=True) as connection:
            stream, core = self._load_core(connection, stream_key)
            if stream is None or core is None:
                raise WorkflowRouteLedgerError(
                    "initial route is required / 必须先登记初始路由"
                )
            before_count = len(core.committed_records)
            result = core.append_revision(
                candidate,
                idempotency_key=idempotency_key,
                trigger_class=trigger_class,
                direction=direction,
                trigger_reason_code=trigger_reason_code,
                trigger_evidence_bindings=trigger_evidence_bindings,
                actor_binding=actor_binding,
                authority_binding=authority_binding,
                hysteresis_evidence_bindings=hysteresis_evidence_bindings,
                budget_impact=budget_impact,
                unfinished_step_ids=unfinished_step_ids,
                switch_event_binding=switch_event_binding,
                created_at=created_at,
            )
            if len(core.committed_records) == before_count:
                return result
            record = core.committed_records[-1]
            self._insert_record(connection, stream_key, record)
            self._advance_head(connection, stream, record)
            return result

    def bind_run_graph(
        self,
        stream_key: str,
        run_graph_binding: Mapping[str, Any],
        *,
        idempotency_key: str,
        actor_binding: Mapping[str, Any],
        authority_binding: Mapping[str, Any],
        created_at: str,
    ) -> dict[str, Any]:
        """Atomically bind a sealed graph without changing the reasoning route.

        / 原子绑定封存运行图且不改变推理路由。
        """

        _validate_stream_key(stream_key)
        with self._transaction(write=True) as connection:
            stream, core = self._load_core(connection, stream_key)
            if stream is None or core is None:
                raise WorkflowRouteLedgerError(
                    "initial route is required / 必须先登记初始路由"
                )
            before_count = len(core.committed_records)
            result = core.bind_run_graph(
                run_graph_binding,
                idempotency_key=idempotency_key,
                actor_binding=actor_binding,
                authority_binding=authority_binding,
                created_at=created_at,
            )
            if len(core.committed_records) == before_count:
                return result
            record = core.committed_records[-1]
            self._insert_record(connection, stream_key, record)
            self._advance_head(connection, stream, record)
            return result

    def replay(self, stream_key: str) -> dict[str, Any] | None:
        """Validate the complete persisted chain and return its head.

        / 校验完整持久化链并返回权威头部。
        """

        _validate_stream_key(stream_key)
        with self._transaction(write=False) as connection:
            stream, core = self._load_core(connection, stream_key)
            if stream is None or core is None:
                return None
            return core.head

    def revision_events(self, stream_key: str) -> tuple[dict[str, Any], ...]:
        """Return detached revision events after full-chain validation.

        / 完整链校验后返回脱离式修订事件。
        """

        _validate_stream_key(stream_key)
        with self._transaction(write=False) as connection:
            stream, core = self._load_core(connection, stream_key)
            if stream is None or core is None:
                return ()
            return core.revision_events

    def migrate_jsonl(self, source_path: str | Path) -> dict[str, Any]:
        """Atomically import one validated legacy JSONL route stream.

        An exact retry is idempotent; a partial or conflicting destination fails
        closed. / 原子导入一条已校验的旧 JSONL 路由流。完全相同的重试保持幂等；
        目标部分存在或内容冲突时默认阻断。
        """

        source = WorkflowRouteLedger(source_path, max_switches=self.max_switches)
        records = source.committed_records
        if not records:
            raise WorkflowRouteLedgerError(
                "JSONL migration source has no committed route / JSONL 迁移源没有已提交路由"
            )
        stream_key = workflow_route_stream_key(records[0]["envelope"])
        with self._transaction(write=True) as connection:
            stream, existing = self._load_core(connection, stream_key)
            if existing is not None:
                if existing.committed_records != records:
                    raise WorkflowRouteLedgerError(
                        "JSONL migration conflicts with the existing route stream / "
                        "JSONL 迁移与已有路由流冲突"
                    )
                return existing.head  # type: ignore[return-value]
            if stream is not None:
                raise WorkflowRouteLedgerError(
                    "route stream metadata exists without records / 路由流元数据存在但记录缺失"
                )
            self._insert_stream(
                connection,
                stream_key,
                records[-1],
                stream_created_at=records[0]["envelope"]["created_at"],
            )
            for record in records:
                self._insert_record(connection, stream_key, record)
            return _detached(records[-1]["envelope"])

    def health_check(self) -> dict[str, Any]:
        """Return bounded storage self-health without route content.

        / 返回不含路由内容的有限存储自健康信息。
        """

        try:
            with closing(self._connect()) as connection:
                integrity = connection.execute("PRAGMA quick_check").fetchone()[0]
                foreign_key_violations = len(
                    connection.execute("PRAGMA foreign_key_check").fetchall()
                )
                journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
                stream_count = connection.execute(
                    "SELECT COUNT(*) FROM route_streams"
                ).fetchone()[0]
                record_count = connection.execute(
                    "SELECT COUNT(*) FROM route_records"
                ).fetchone()[0]
        except sqlite3.Error as exc:
            raise WorkflowRouteLedgerError(
                "SQLite route ledger health check failed / SQLite 路由账本健康检查失败"
            ) from exc
        return {
            "schema_version": SQLITE_ROUTE_SCHEMA_VERSION,
            "journal_mode": journal_mode,
            "integrity_check": integrity,
            "foreign_key_violations": foreign_key_violations,
            "stream_count": stream_count,
            "record_count": record_count,
        }

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=self.busy_timeout_ms / 1000,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms}")
        connection.execute("PRAGMA synchronous = FULL")
        return connection

    @contextmanager
    def _transaction(self, *, write: bool) -> Iterator[sqlite3.Connection]:
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield connection
            connection.commit()
        except WorkflowRouteLedgerError:
            if connection is not None and connection.in_transaction:
                connection.rollback()
            raise
        except sqlite3.Error as exc:
            if connection is not None and connection.in_transaction:
                connection.rollback()
            raise WorkflowRouteLedgerError(
                "SQLite route ledger transaction failed / SQLite 路由账本事务失败"
            ) from exc
        finally:
            if connection is not None:
                connection.close()

    def _initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with closing(self._connect()) as connection:
                connection.execute("PRAGMA journal_mode = WAL")
                connection.execute("PRAGMA synchronous = FULL")
                connection.execute("BEGIN IMMEDIATE")
                version = connection.execute("PRAGMA user_version").fetchone()[0]
                if version == 0:
                    user_tables = {
                        row[0]
                        for row in connection.execute(
                            "SELECT name FROM sqlite_master "
                            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
                        )
                    }
                    if user_tables:
                        raise WorkflowRouteLedgerError(
                            "unversioned SQLite database is not empty / "
                            "未版本化的 SQLite 数据库不是空库"
                        )
                    self._create_schema(connection)
                    connection.execute(
                        f"PRAGMA user_version = {SQLITE_ROUTE_SCHEMA_VERSION}"
                    )
                elif version != SQLITE_ROUTE_SCHEMA_VERSION:
                    raise WorkflowRouteLedgerError(
                        f"unsupported SQLite route schema version {version} / "
                        f"不支持的 SQLite 路由 Schema 版本 {version}"
                    )
                self._verify_schema(connection)
                connection.commit()
        except WorkflowRouteLedgerError:
            raise
        except sqlite3.Error as exc:
            raise WorkflowRouteLedgerError(
                "SQLite route ledger initialization failed / SQLite 路由账本初始化失败"
            ) from exc

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE route_streams (
                stream_key TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                scene_id TEXT NOT NULL,
                task_atom_id TEXT NOT NULL,
                max_switches INTEGER NOT NULL CHECK (max_switches > 0),
                head_sequence INTEGER NOT NULL CHECK (head_sequence > 0),
                head_revision INTEGER NOT NULL CHECK (head_revision > 0),
                head_record_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE route_records (
                stream_key TEXT NOT NULL,
                record_sequence INTEGER NOT NULL CHECK (record_sequence > 0),
                decision_revision INTEGER NOT NULL CHECK (decision_revision > 0),
                record_type TEXT NOT NULL CHECK (
                    record_type IN ('initial_route', 'route_revision_commit')
                ),
                idempotency_key TEXT NOT NULL,
                request_fingerprint TEXT NOT NULL,
                decision_id TEXT NOT NULL,
                envelope_hash TEXT NOT NULL,
                record_hash TEXT NOT NULL,
                record_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (stream_key, record_sequence),
                UNIQUE (stream_key, decision_revision),
                UNIQUE (stream_key, idempotency_key),
                FOREIGN KEY (stream_key) REFERENCES route_streams(stream_key)
                    ON DELETE RESTRICT
            )
            """
        )

    @staticmethod
    def _verify_schema(connection: sqlite3.Connection) -> None:
        expected = {
            "route_streams": {
                "stream_key": ("TEXT", 0, 1),
                "workflow_id": ("TEXT", 1, 0),
                "task_id": ("TEXT", 1, 0),
                "run_id": ("TEXT", 1, 0),
                "scene_id": ("TEXT", 1, 0),
                "task_atom_id": ("TEXT", 1, 0),
                "max_switches": ("INTEGER", 1, 0),
                "head_sequence": ("INTEGER", 1, 0),
                "head_revision": ("INTEGER", 1, 0),
                "head_record_hash": ("TEXT", 1, 0),
                "created_at": ("TEXT", 1, 0),
                "updated_at": ("TEXT", 1, 0),
            },
            "route_records": {
                "stream_key": ("TEXT", 1, 1),
                "record_sequence": ("INTEGER", 1, 2),
                "decision_revision": ("INTEGER", 1, 0),
                "record_type": ("TEXT", 1, 0),
                "idempotency_key": ("TEXT", 1, 0),
                "request_fingerprint": ("TEXT", 1, 0),
                "decision_id": ("TEXT", 1, 0),
                "envelope_hash": ("TEXT", 1, 0),
                "record_hash": ("TEXT", 1, 0),
                "record_json": ("TEXT", 1, 0),
                "created_at": ("TEXT", 1, 0),
            },
        }
        for table, expected_columns in expected.items():
            actual_columns = {
                row["name"]: (str(row["type"]).upper(), row["notnull"], row["pk"])
                for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
            }
            if actual_columns != expected_columns:
                raise WorkflowRouteLedgerError(
                    f"SQLite route table {table} does not match schema / "
                    f"SQLite 路由表 {table} 与 Schema 不一致"
                )

        unique_columns = {
            tuple(
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM pragma_index_info(?) ORDER BY seqno",
                    (index["name"],),
                ).fetchall()
            )
            for index in connection.execute("PRAGMA index_list(route_records)").fetchall()
            if index["unique"]
        }
        if unique_columns != {
            ("stream_key", "record_sequence"),
            ("stream_key", "decision_revision"),
            ("stream_key", "idempotency_key"),
        }:
            raise WorkflowRouteLedgerError(
                "SQLite route record uniqueness does not match schema / "
                "SQLite 路由记录唯一约束与 Schema 不一致"
            )
        foreign_keys = [
            (
                row["table"],
                row["from"],
                row["to"],
                row["on_update"],
                row["on_delete"],
            )
            for row in connection.execute(
                "PRAGMA foreign_key_list(route_records)"
            ).fetchall()
        ]
        if foreign_keys != [
            ("route_streams", "stream_key", "stream_key", "NO ACTION", "RESTRICT")
        ]:
            raise WorkflowRouteLedgerError(
                "SQLite route record foreign key does not match schema / "
                "SQLite 路由记录外键与 Schema 不一致"
            )

    def _load_core(
        self,
        connection: sqlite3.Connection,
        stream_key: str,
    ) -> tuple[sqlite3.Row | None, WorkflowRouteLedger | None]:
        stream = connection.execute(
            "SELECT * FROM route_streams WHERE stream_key = ?",
            (stream_key,),
        ).fetchone()
        if stream is None:
            return None, None
        if stream["max_switches"] != self.max_switches:
            raise WorkflowRouteLedgerError(
                "route stream max_switches differs from adapter configuration / "
                "路由流最大换路次数与适配器配置不一致"
            )
        rows = connection.execute(
            "SELECT * FROM route_records WHERE stream_key = ? ORDER BY record_sequence",
            (stream_key,),
        ).fetchall()
        if not rows:
            raise WorkflowRouteLedgerError(
                "route stream has no committed records / 路由流没有已提交记录"
            )
        records: list[dict[str, Any]] = []
        for row in rows:
            try:
                record = json.loads(row["record_json"])
            except (TypeError, json.JSONDecodeError) as exc:
                raise WorkflowRouteLedgerError(
                    "persisted route record is not valid JSON / 持久化路由记录不是有效 JSON"
                ) from exc
            envelope = record.get("envelope", {})
            projection = {
                "record_sequence": record.get("record_sequence"),
                "decision_revision": envelope.get("decision_revision"),
                "record_type": record.get("record_type"),
                "idempotency_key": record.get("idempotency_key"),
                "request_fingerprint": record.get("request_fingerprint"),
                "decision_id": envelope.get("decision_id"),
                "envelope_hash": envelope.get("route_envelope_hash"),
                "record_hash": record.get("record_hash"),
                "created_at": envelope.get("created_at"),
            }
            if any(row[field] != value for field, value in projection.items()):
                raise WorkflowRouteLedgerError(
                    "route record projection mismatch / 路由记录投影不一致"
                )
            records.append(record)
        core = WorkflowRouteLedger.from_records(records, max_switches=self.max_switches)
        head_record = records[-1]
        head = head_record["envelope"]
        identity = _stream_identity(head)
        if workflow_route_stream_key(head) != stream_key or any(
            stream[field] != value for field, value in identity.items()
        ):
            raise WorkflowRouteLedgerError(
                "route stream identity mismatch / 路由流身份不一致"
            )
        if (
            stream["head_sequence"] != head_record["record_sequence"]
            or stream["head_revision"] != head["decision_revision"]
            or stream["head_record_hash"] != head_record["record_hash"]
            or stream["updated_at"] != head["created_at"]
            or stream["created_at"] != records[0]["envelope"]["created_at"]
        ):
            raise WorkflowRouteLedgerError(
                "route stream head metadata mismatch / 路由流头部元数据不一致"
            )
        return stream, core

    def _insert_stream(
        self,
        connection: sqlite3.Connection,
        stream_key: str,
        head_record: Mapping[str, Any],
        *,
        stream_created_at: str | None = None,
    ) -> None:
        envelope = head_record["envelope"]
        identity = _stream_identity(envelope)
        connection.execute(
            """
            INSERT INTO route_streams (
                stream_key, workflow_id, task_id, run_id, scene_id, task_atom_id,
                max_switches, head_sequence, head_revision, head_record_hash,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stream_key,
                identity["workflow_id"],
                identity["task_id"],
                identity["run_id"],
                identity["scene_id"],
                identity["task_atom_id"],
                self.max_switches,
                head_record["record_sequence"],
                envelope["decision_revision"],
                head_record["record_hash"],
                stream_created_at or envelope["created_at"],
                envelope["created_at"],
            ),
        )

    @staticmethod
    def _insert_record(
        connection: sqlite3.Connection,
        stream_key: str,
        record: Mapping[str, Any],
    ) -> None:
        envelope = record["envelope"]
        connection.execute(
            """
            INSERT INTO route_records (
                stream_key, record_sequence, decision_revision, record_type,
                idempotency_key, request_fingerprint, decision_id, envelope_hash,
                record_hash, record_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stream_key,
                record["record_sequence"],
                envelope["decision_revision"],
                record["record_type"],
                record["idempotency_key"],
                record["request_fingerprint"],
                envelope["decision_id"],
                envelope["route_envelope_hash"],
                record["record_hash"],
                _canonical_text(record),
                envelope["created_at"],
            ),
        )

    @staticmethod
    def _advance_head(
        connection: sqlite3.Connection,
        previous_stream: sqlite3.Row,
        record: Mapping[str, Any],
    ) -> None:
        envelope = record["envelope"]
        cursor = connection.execute(
            """
            UPDATE route_streams
            SET head_sequence = ?, head_revision = ?, head_record_hash = ?, updated_at = ?
            WHERE stream_key = ? AND head_sequence = ? AND head_record_hash = ?
            """,
            (
                record["record_sequence"],
                envelope["decision_revision"],
                record["record_hash"],
                envelope["created_at"],
                previous_stream["stream_key"],
                previous_stream["head_sequence"],
                previous_stream["head_record_hash"],
            ),
        )
        if cursor.rowcount != 1:
            raise WorkflowRouteLedgerError(
                "route stream head changed during commit / 提交期间路由流头部发生变化"
            )


__all__ = [
    "SQLITE_ROUTE_SCHEMA_VERSION",
    "SqliteWorkflowRouteLedger",
    "workflow_route_stream_key",
]
