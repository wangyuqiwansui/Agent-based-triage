"""Transactional multi-writer reasoning event store / 事务型多写者推理事件库。

SQLite is the local multi-writer reference adapter. Each outer transaction
uses ``BEGIN IMMEDIATE``, reloads and validates the authoritative event stream,
and commits a contiguous suffix atomically. A stale causal parent fails closed;
callers must reload the aggregate before retrying. This adapter is not a
distributed-consensus system. / SQLite 是本地多写者参考适配器。每个最外层事务
通过 ``BEGIN IMMEDIATE`` 取得写预留，重新加载并校验权威事件流，再原子提交连续
后缀。陈旧因果父事件默认阻断，调用方必须重载聚合后重试。本适配器不是分布式
共识系统。
"""

from __future__ import annotations

from contextlib import closing, contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
import threading
from typing import Any, Callable, Iterator, Mapping

try:  # Package import / 包导入
    from .reasoning_runtime import (
        EventStore,
        EventStorePersistenceError,
        DuplicateEventConflictError,
        ReasoningEvent,
        WorkflowState,
        _TERMINAL_STATES,
        _canonical_json,
        _iso_utc,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_runtime import (
        EventStore,
        EventStorePersistenceError,
        DuplicateEventConflictError,
        ReasoningEvent,
        WorkflowState,
        _TERMINAL_STATES,
        _canonical_json,
        _iso_utc,
    )


SQLITE_EVENT_SCHEMA_VERSION = 2


@dataclass
class _TransactionContext:
    connection: sqlite3.Connection
    mirror: EventStore
    run_id: str
    depth: int = 1


class SqliteEventStore(EventStore):
    """Persist event streams with database-serialized multi-writer commits.

    / 以数据库串行化的多写者提交方式持久化事件流。
    """

    def __init__(
        self,
        database_path: str | Path,
        *,
        validate_schema: bool = True,
        busy_timeout_ms: int = 5_000,
    ) -> None:
        if str(database_path) == ":memory:":
            raise ValueError(
                "connection-local :memory: databases are unsupported / "
                "不支持连接私有的 :memory: 数据库"
            )
        if (
            isinstance(busy_timeout_ms, bool)
            or not isinstance(busy_timeout_ms, int)
            or busy_timeout_ms < 1
        ):
            raise ValueError(
                "busy_timeout_ms must be positive / busy_timeout_ms 必须为正整数"
            )
        self.database_path = Path(database_path).resolve()
        self.busy_timeout_ms = busy_timeout_ms
        self._validate_schema_enabled = validate_schema
        self._local = threading.local()
        super().__init__(validate_schema=validate_schema)
        self._initialize()

    @property
    def path(self) -> Path:
        """Return the resolved database path / 返回已解析的数据库路径。"""

        return self.database_path

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
                        raise EventStorePersistenceError(
                            "unversioned SQLite database is not empty / "
                            "未版本化的 SQLite 数据库不是空库"
                        )
                    self._create_schema(connection)
                    connection.execute(
                        f"PRAGMA user_version = {SQLITE_EVENT_SCHEMA_VERSION}"
                    )
                elif version == 1:
                    self._migrate_v1_to_v2(connection)
                    connection.execute(
                        f"PRAGMA user_version = {SQLITE_EVENT_SCHEMA_VERSION}"
                    )
                elif version != SQLITE_EVENT_SCHEMA_VERSION:
                    raise EventStorePersistenceError(
                        f"unsupported SQLite event schema version {version} / "
                        f"不支持的 SQLite 事件 Schema 版本 {version}"
                    )
                self._verify_schema(connection)
                connection.commit()
        except EventStorePersistenceError:
            raise
        except sqlite3.Error as exc:
            raise EventStorePersistenceError(
                "SQLite event store initialization failed / SQLite 事件库初始化失败"
            ) from exc

    @staticmethod
    def _create_schema(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE reasoning_events (
                global_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                run_sequence INTEGER NOT NULL CHECK (run_sequence > 0),
                event_id TEXT NOT NULL UNIQUE,
                idempotency_key TEXT NOT NULL,
                event_type TEXT NOT NULL,
                workflow_state TEXT NOT NULL,
                occurred_epoch REAL NOT NULL,
                envelope_json TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                content_json TEXT NOT NULL,
                UNIQUE (run_id, run_sequence),
                UNIQUE (run_id, idempotency_key)
            )
            """
        )
        connection.execute(
            "CREATE INDEX reasoning_events_run_order "
            "ON reasoning_events (run_id, run_sequence)"
        )
        SqliteEventStore._create_terminal_results_table(connection)

    @staticmethod
    def _create_terminal_results_table(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE terminal_results (
                run_id TEXT PRIMARY KEY,
                result_id TEXT NOT NULL UNIQUE,
                result_hash TEXT NOT NULL,
                terminal_state TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

    @staticmethod
    def _migrate_v1_to_v2(connection: sqlite3.Connection) -> None:
        """Add immutable terminal results without rewriting v1 events.

        / 在不重写 v1 事件的前提下增加不可变终态结果表。
        """

        SqliteEventStore._create_terminal_results_table(connection)

    @staticmethod
    def _verify_schema(connection: sqlite3.Connection) -> None:
        expected_events = {
            "global_sequence",
            "run_id",
            "run_sequence",
            "event_id",
            "idempotency_key",
            "event_type",
            "workflow_state",
            "occurred_epoch",
            "envelope_json",
            "payload_json",
            "content_json",
        }
        actual_events = {
            row[1]
            for row in connection.execute("PRAGMA table_info(reasoning_events)")
        }
        if actual_events != expected_events:
            raise EventStorePersistenceError(
                "SQLite event table differs from the contract / "
                "SQLite 事件表与契约不一致"
            )
        expected_results = {
            "run_id",
            "result_id",
            "result_hash",
            "terminal_state",
            "result_json",
            "created_at",
        }
        actual_results = {
            row[1]
            for row in connection.execute("PRAGMA table_info(terminal_results)")
        }
        if actual_results != expected_results:
            raise EventStorePersistenceError(
                "SQLite terminal result table differs from the contract / "
                "SQLite 终态结果表与契约不一致"
            )

    def _row_to_event(self, row: sqlite3.Row) -> ReasoningEvent:
        try:
            envelope_text = str(row["envelope_json"])
            payload_text = str(row["payload_json"])
            content_text = str(row["content_json"])
            envelope = json.loads(envelope_text)
            payload = json.loads(payload_text)
            if _canonical_json(envelope) != envelope_text:
                raise ValueError("event envelope is not canonical")
            if _canonical_json(payload) != payload_text:
                raise ValueError("event payload is not canonical")
            if _canonical_json(json.loads(content_text)) != content_text:
                raise ValueError("event logical content is not canonical")
            if envelope.get("payload", {}).get("data") != payload:
                raise ValueError("payload column differs from the envelope")
            if (
                envelope.get("schema_version") != self.SCHEMA_VERSION
                or envelope.get("event_version") != self.SCHEMA_VERSION
            ):
                raise ValueError("event schema version mismatch")
            expected_columns = {
                "run_id": str(row["run_id"]),
                "sequence": int(row["run_sequence"]),
                "event_id": str(row["event_id"]),
                "idempotency_key": str(row["idempotency_key"]),
                "event_type": str(row["event_type"]),
                "workflow_state": str(row["workflow_state"]),
            }
            if any(envelope.get(name) != value for name, value in expected_columns.items()):
                raise ValueError("indexed columns differ from the envelope")
            _, occurred_epoch = _iso_utc(envelope["occurred_at"])
            # The normative envelope is millisecond-precision while the runtime
            # retains the source epoch for ordering. / 规范事件信封为毫秒精度，运行时
            # 保留源 epoch 以用于排序。
            if abs(occurred_epoch - float(row["occurred_epoch"])) >= 0.001:
                raise ValueError("event timestamp column differs from the envelope")
            if self._schema_validator is not None:
                errors = sorted(
                    self._schema_validator.iter_errors(envelope),
                    key=lambda error: list(error.absolute_path),
                )
                if errors:
                    raise ValueError(errors[0].message)
            return ReasoningEvent(
                schema_version=self.SCHEMA_VERSION,
                sequence=int(row["run_sequence"]),
                event_id=str(row["event_id"]),
                idempotency_key=str(row["idempotency_key"]),
                run_id=str(row["run_id"]),
                event_type=str(row["event_type"]),
                state=WorkflowState(row["workflow_state"]),
                timestamp=float(row["occurred_epoch"]),
                payload_json=payload_text,
                envelope_json=envelope_text,
                content_json=content_text,
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise EventStorePersistenceError(
                "invalid SQLite event record / SQLite 事件记录无效: " + str(exc)
            ) from exc

    def _load_mirror(self, connection: sqlite3.Connection) -> EventStore:
        mirror = EventStore(validate_schema=self._validate_schema_enabled)
        rows = connection.execute(
            "SELECT * FROM reasoning_events ORDER BY global_sequence"
        )
        for row in rows:
            mirror._index_restored_event(self._row_to_event(row))
        return mirror

    def _active_context(self) -> _TransactionContext | None:
        value = getattr(self._local, "transaction", None)
        return value if isinstance(value, _TransactionContext) else None

    @contextmanager
    def transaction(self, run_id: str) -> Iterator[None]:
        """Serialize and atomically commit a run-local event group.

        / 串行化并原子提交一组运行内事件。
        """

        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id is required / 运行标识不能为空")
        with self._lock:
            active = self._active_context()
            if active is not None:
                if active.run_id != run_id:
                    raise EventStorePersistenceError(
                        "nested SQLite event transactions must use one run / "
                        "嵌套 SQLite 事件事务必须属于同一运行"
                    )
                active.depth += 1
                try:
                    yield
                finally:
                    active.depth -= 1
                return

            connection: sqlite3.Connection | None = None
            try:
                connection = self._connect()
                connection.execute("BEGIN IMMEDIATE")
                context = _TransactionContext(
                    connection=connection,
                    mirror=self._load_mirror(connection),
                    run_id=run_id,
                )
                self._local.transaction = context
                yield
                connection.commit()
            except EventStorePersistenceError:
                if connection is not None and connection.in_transaction:
                    connection.rollback()
                raise
            except sqlite3.Error as exc:
                if connection is not None and connection.in_transaction:
                    connection.rollback()
                raise EventStorePersistenceError(
                    "SQLite event transaction failed / SQLite 事件事务失败"
                ) from exc
            except Exception:
                if connection is not None and connection.in_transaction:
                    connection.rollback()
                raise
            finally:
                if hasattr(self._local, "transaction"):
                    del self._local.transaction
                if connection is not None:
                    connection.close()

    def _append_in_context(self, context: _TransactionContext, kwargs: dict[str, Any]) -> ReasoningEvent:
        before = context.mirror.events(context.run_id)
        prior = before[-1] if before else None
        event = context.mirror.append(**kwargs)
        after = context.mirror.events(context.run_id)
        if len(after) == len(before):
            return event
        supplied_parent = kwargs.get("parent_event_id")
        supplied_cause = kwargs.get("causation_id")
        expected_parent = None if prior is None else prior.event_id
        if (
            ("parent_event_id" in kwargs and supplied_parent != expected_parent)
            or ("causation_id" in kwargs and supplied_cause != expected_parent)
        ):
            context.mirror._remove_events((event,))
            raise EventStorePersistenceError(
                "stale causal parent; reload before retry / "
                "因果父事件已陈旧；请重载后重试"
            )
        context.connection.execute(
            """
            INSERT INTO reasoning_events (
                run_id, run_sequence, event_id, idempotency_key, event_type,
                workflow_state, occurred_epoch, envelope_json, payload_json,
                content_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.run_id,
                event.sequence,
                event.event_id,
                event.idempotency_key,
                event.event_type,
                event.state.value,
                event.timestamp,
                event.envelope_json,
                event.payload_json,
                event.content_json,
            ),
        )
        return event

    def append(self, **kwargs: Any) -> ReasoningEvent:
        """Append under the authoritative database head / 在权威数据库流头下追加事件。"""

        run_id = kwargs.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id is required / 运行标识不能为空")
        active = self._active_context()
        if active is not None:
            if active.run_id != run_id:
                raise EventStorePersistenceError(
                    "active SQLite transaction belongs to another run / "
                    "活动 SQLite 事务属于另一运行"
                )
            return self._append_in_context(active, dict(kwargs))
        with self.transaction(run_id):
            active = self._active_context()
            if active is None:  # pragma: no cover - context invariant / 上下文不变量
                raise EventStorePersistenceError(
                    "SQLite transaction context is missing / SQLite 事务上下文缺失"
                )
            return self._append_in_context(active, dict(kwargs))

    def events(self, run_id: str | None = None) -> tuple[ReasoningEvent, ...]:
        """Return a validated authoritative snapshot / 返回已校验的权威快照。"""

        active = self._active_context()
        if active is not None:
            return active.mirror.events(run_id)
        with self._lock:
            connection: sqlite3.Connection | None = None
            try:
                connection = self._connect()
                connection.execute("BEGIN")
                result = self._load_mirror(connection).events(run_id)
                connection.commit()
                return result
            except EventStorePersistenceError:
                if connection is not None and connection.in_transaction:
                    connection.rollback()
                raise
            except sqlite3.Error as exc:
                if connection is not None and connection.in_transaction:
                    connection.rollback()
                raise EventStorePersistenceError(
                    "SQLite event read failed / SQLite 事件读取失败"
                ) from exc
            finally:
                if connection is not None:
                    connection.close()

    def find_idempotency(self, run_id: str, key: str) -> ReasoningEvent | None:
        """Find a run-scoped idempotent event in the current snapshot.

        / 在当前快照中查找运行域幂等事件。
        """

        return next(
            (event for event in self.events(run_id) if event.idempotency_key == key),
            None,
        )

    def replay(
        self,
        run_id: str,
        reducer: Callable[[Any, ReasoningEvent], Any] | None = None,
        initial: Any = None,
    ) -> tuple[ReasoningEvent, ...] | Any:
        """Replay a validated contiguous run stream / 重放已校验的连续运行流。"""

        events = self.events(run_id)
        if reducer is None:
            return events
        state = initial
        for event in events:
            state = reducer(state, event)
        return state

    @staticmethod
    def _assert_result_stream(
        connection: sqlite3.Connection,
        run_id: str,
        terminal_state: str,
    ) -> None:
        row = connection.execute(
            "SELECT workflow_state FROM reasoning_events "
            "WHERE run_id = ? ORDER BY run_sequence DESC LIMIT 1",
            (run_id,),
        ).fetchone()
        if row is None:
            raise EventStorePersistenceError(
                "terminal result requires an event stream / 终态结果要求已有事件流"
            )
        state = WorkflowState(row["workflow_state"])
        if state not in _TERMINAL_STATES or state.value != terminal_state:
            raise EventStorePersistenceError(
                "terminal result state differs from the event stream / "
                "终态结果状态与事件流不一致"
            )

    def _save_terminal_result_in_connection(
        self,
        connection: sqlite3.Connection,
        run_id: str,
        result_json: str,
    ) -> dict[str, Any]:
        artifact = json.loads(result_json)
        self._assert_result_stream(connection, run_id, artifact["terminal_state"])
        existing = connection.execute(
            "SELECT result_json FROM terminal_results WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        if existing is not None:
            saved_json = str(existing["result_json"])
            if saved_json != result_json:
                raise DuplicateEventConflictError(
                    "terminal run already has a different persisted result / "
                    "终态运行已有不同的持久化结果"
                )
            return json.loads(saved_json)
        conflicting = connection.execute(
            "SELECT run_id FROM terminal_results WHERE result_id = ?",
            (artifact["result_id"],),
        ).fetchone()
        if conflicting is not None:
            raise DuplicateEventConflictError(
                "terminal result_id is already used by another run / "
                "终态结果标识已被其他运行使用"
            )
        connection.execute(
            """
            INSERT INTO terminal_results (
                run_id, result_id, result_hash, terminal_state, result_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                artifact["result_id"],
                artifact["result_hash"],
                artifact["terminal_state"],
                result_json,
                artifact["created_at"],
            ),
        )
        return artifact

    def save_terminal_result(
        self,
        run_id: str,
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Serialize one immutable result with competing SQLite writers.

        / 在竞争 SQLite 写者之间串行化一份不可变结果。
        """

        result_json = self._terminal_result_json(run_id, result)
        active = self._active_context()
        if active is not None:
            if active.run_id != run_id:
                raise EventStorePersistenceError(
                    "active SQLite transaction belongs to another run / "
                    "活动 SQLite 事务属于另一运行"
                )
            return self._save_terminal_result_in_connection(
                active.connection, run_id, result_json
            )
        with self._lock:
            connection: sqlite3.Connection | None = None
            try:
                connection = self._connect()
                connection.execute("BEGIN IMMEDIATE")
                saved = self._save_terminal_result_in_connection(
                    connection, run_id, result_json
                )
                connection.commit()
                return saved
            except (EventStorePersistenceError, DuplicateEventConflictError):
                if connection is not None and connection.in_transaction:
                    connection.rollback()
                raise
            except sqlite3.Error as exc:
                if connection is not None and connection.in_transaction:
                    connection.rollback()
                raise EventStorePersistenceError(
                    "SQLite terminal result commit failed / "
                    "SQLite 终态结果提交失败"
                ) from exc
            finally:
                if connection is not None:
                    connection.close()

    def _load_terminal_result_in_connection(
        self,
        connection: sqlite3.Connection,
        run_id: str,
    ) -> dict[str, Any] | None:
        row = connection.execute(
            "SELECT * FROM terminal_results WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        try:
            result_json = str(row["result_json"])
            if _canonical_json(json.loads(result_json)) != result_json:
                raise ValueError("terminal result JSON is not canonical")
            artifact = json.loads(result_json)
            expected = {
                "run_id": run_id,
                "result_id": str(row["result_id"]),
                "result_hash": str(row["result_hash"]),
                "terminal_state": str(row["terminal_state"]),
                "created_at": str(row["created_at"]),
            }
            if any(artifact.get(key) != value for key, value in expected.items()):
                raise ValueError("terminal result columns differ from the artifact")
            # Reuse the normative Schema/hash validator. / 复用规范 Schema/哈希校验器。
            self._terminal_result_json(run_id, artifact)
            self._assert_result_stream(connection, run_id, artifact["terminal_state"])
            return artifact
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise EventStorePersistenceError(
                "invalid SQLite terminal result record / "
                "SQLite 终态结果记录无效: " + str(exc)
            ) from exc

    def load_terminal_result(self, run_id: str) -> dict[str, Any] | None:
        """Load a validated authoritative terminal result / 加载已校验的权威终态结果。"""

        active = self._active_context()
        if active is not None:
            return self._load_terminal_result_in_connection(active.connection, run_id)
        with self._lock:
            connection: sqlite3.Connection | None = None
            try:
                connection = self._connect()
                connection.execute("BEGIN")
                result = self._load_terminal_result_in_connection(connection, run_id)
                connection.commit()
                return result
            except EventStorePersistenceError:
                if connection is not None and connection.in_transaction:
                    connection.rollback()
                raise
            except sqlite3.Error as exc:
                if connection is not None and connection.in_transaction:
                    connection.rollback()
                raise EventStorePersistenceError(
                    "SQLite terminal result read failed / SQLite 终态结果读取失败"
                ) from exc
            finally:
                if connection is not None:
                    connection.close()

    def health_check(self) -> dict[str, Any]:
        """Return bounded database self-health without event content.

        / 返回不含事件内容的有限数据库自健康信息。
        """

        try:
            with closing(self._connect()) as connection:
                integrity = connection.execute("PRAGMA quick_check").fetchone()[0]
                journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
                event_count = connection.execute(
                    "SELECT COUNT(*) FROM reasoning_events"
                ).fetchone()[0]
                run_count = connection.execute(
                    "SELECT COUNT(DISTINCT run_id) FROM reasoning_events"
                ).fetchone()[0]
                result_count = connection.execute(
                    "SELECT COUNT(*) FROM terminal_results"
                ).fetchone()[0]
        except sqlite3.Error as exc:
            raise EventStorePersistenceError(
                "SQLite event health check failed / SQLite 事件健康检查失败"
            ) from exc
        return {
            "schema_version": SQLITE_EVENT_SCHEMA_VERSION,
            "journal_mode": journal_mode,
            "integrity_check": integrity,
            "event_count": event_count,
            "run_count": run_count,
            "result_count": result_count,
        }


__all__ = ["SQLITE_EVENT_SCHEMA_VERSION", "SqliteEventStore"]
