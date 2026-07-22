"""Network multi-writer reasoning event store for PostgreSQL / PostgreSQL 网络多写者推理事件库。

Each run-local write transaction takes a transaction-scoped advisory lock,
reloads the authoritative event stream, and commits a contiguous suffix plus
optional immutable terminal result. The adapter uses Psycopg 3 and performs no
connection pooling; deployments should inject a service-appropriate DSN and
pooling layer. / 每个运行域写事务获取事务级 advisory lock，重载权威事件流，并
提交连续事件后缀及可选不可变终态结果。适配器使用 Psycopg 3，不自行提供连接池；
部署方应注入适合服务的 DSN 与连接池层。
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import re
import threading
from typing import Any, Callable, Iterator, Mapping

try:  # Optional deployment dependency / 可选部署依赖
    import psycopg
    from psycopg import sql
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - exercised in dependency-light deployments
    psycopg = None
    sql = None
    dict_row = None

try:  # Package import / 包导入
    from .reasoning_runtime import (
        DuplicateEventConflictError,
        EventStore,
        EventStorePersistenceError,
        ReasoningEvent,
        WorkflowState,
        _TERMINAL_STATES,
        _canonical_json,
        _iso_utc,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_runtime import (
        DuplicateEventConflictError,
        EventStore,
        EventStorePersistenceError,
        ReasoningEvent,
        WorkflowState,
        _TERMINAL_STATES,
        _canonical_json,
        _iso_utc,
    )


POSTGRES_EVENT_SCHEMA_VERSION = 1
_SCHEMA_NAME = re.compile(r"[a-z_][a-z0-9_]{0,62}")


@dataclass
class _PostgresTransactionContext:
    connection: Any
    mirror: EventStore
    run_id: str
    depth: int = 1


class PostgresEventStore(EventStore):
    """Persist reasoning events and results with PostgreSQL serialization.

    / 使用 PostgreSQL 串行化持久化推理事件与结果。
    """

    def __init__(
        self,
        dsn: str,
        *,
        schema: str = "harness_reasoning",
        validate_schema: bool = True,
        connect_timeout_seconds: int = 5,
        lock_timeout_ms: int = 5_000,
        application_name: str = "harness-reasoning-runtime",
    ) -> None:
        if psycopg is None:
            raise EventStorePersistenceError(
                "Psycopg 3 is required for PostgresEventStore / "
                "PostgresEventStore 需要 Psycopg 3"
            )
        if not isinstance(dsn, str) or not dsn.strip():
            raise ValueError("dsn is required / dsn 不能为空")
        if not isinstance(schema, str) or _SCHEMA_NAME.fullmatch(schema) is None:
            raise ValueError(
                "schema must be a lowercase PostgreSQL identifier / "
                "schema 必须为小写 PostgreSQL 标识符"
            )
        for name, value in (
            ("connect_timeout_seconds", connect_timeout_seconds),
            ("lock_timeout_ms", lock_timeout_ms),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be positive / {name} 必须为正整数")
        if not isinstance(application_name, str) or not application_name.strip():
            raise ValueError("application_name is required / application_name 不能为空")
        self.dsn = dsn
        self.schema = schema
        self.connect_timeout_seconds = connect_timeout_seconds
        self.lock_timeout_ms = lock_timeout_ms
        self.application_name = application_name
        self._validate_schema_enabled = validate_schema
        self._local = threading.local()
        super().__init__(validate_schema=validate_schema)
        self._initialize()

    def _table(self, name: str) -> Any:
        return sql.Identifier(self.schema, name)

    def _connect(self) -> Any:
        return psycopg.connect(
            self.dsn,
            autocommit=True,
            row_factory=dict_row,
            connect_timeout=self.connect_timeout_seconds,
            application_name=self.application_name,
        )

    @staticmethod
    def _advisory_key(run_id: str) -> int:
        raw = int.from_bytes(
            hashlib.sha256(run_id.encode("utf-8")).digest()[:8],
            byteorder="big",
            signed=False,
        )
        return raw if raw < 2**63 else raw - 2**64

    def _set_transaction_guards(self, connection: Any) -> None:
        connection.execute(
            "SELECT set_config('lock_timeout', %s, true)",
            (f"{self.lock_timeout_ms}ms",),
        )

    def _initialize(self) -> None:
        connection = None
        try:
            connection = self._connect()
            with connection.transaction():
                self._set_transaction_guards(connection)
                connection.execute(
                    "SELECT pg_advisory_xact_lock(%s)",
                    (self._advisory_key(f"schema-init:{self.schema}"),),
                )
                connection.execute(
                    sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                        sql.Identifier(self.schema)
                    )
                )
                connection.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {} (
                            singleton SMALLINT PRIMARY KEY CHECK (singleton = 1),
                            schema_version INTEGER NOT NULL
                        )
                        """
                    ).format(self._table("reasoning_store_metadata"))
                )
                version_row = connection.execute(
                    sql.SQL(
                        "SELECT schema_version FROM {} WHERE singleton = 1 FOR UPDATE"
                    ).format(self._table("reasoning_store_metadata"))
                ).fetchone()
                if version_row is None:
                    existing = connection.execute(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = %s AND table_type = 'BASE TABLE' "
                        "AND table_name <> 'reasoning_store_metadata'",
                        (self.schema,),
                    ).fetchall()
                    if existing:
                        raise EventStorePersistenceError(
                            "unversioned PostgreSQL reasoning schema is not empty / "
                            "未版本化的 PostgreSQL 推理 Schema 不是空的"
                        )
                    self._create_schema(connection)
                    connection.execute(
                        sql.SQL(
                            "INSERT INTO {} (singleton, schema_version) VALUES (1, %s)"
                        ).format(self._table("reasoning_store_metadata")),
                        (POSTGRES_EVENT_SCHEMA_VERSION,),
                    )
                elif int(version_row["schema_version"]) != POSTGRES_EVENT_SCHEMA_VERSION:
                    raise EventStorePersistenceError(
                        "unsupported PostgreSQL reasoning schema version / "
                        "不支持的 PostgreSQL 推理 Schema 版本"
                    )
                self._verify_schema(connection)
        except EventStorePersistenceError:
            raise
        except Exception as exc:
            if psycopg is not None and isinstance(exc, psycopg.Error):
                raise EventStorePersistenceError(
                    "PostgreSQL event store initialization failed / "
                    "PostgreSQL 事件库初始化失败"
                ) from exc
            raise
        finally:
            if connection is not None:
                connection.close()

    def _create_schema(self, connection: Any) -> None:
        connection.execute(
            sql.SQL(
                """
                CREATE TABLE {} (
                    global_sequence BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    run_sequence BIGINT NOT NULL CHECK (run_sequence > 0),
                    event_id TEXT NOT NULL UNIQUE,
                    idempotency_key TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    workflow_state TEXT NOT NULL,
                    occurred_epoch DOUBLE PRECISION NOT NULL,
                    envelope_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    content_json TEXT NOT NULL,
                    UNIQUE (run_id, run_sequence),
                    UNIQUE (run_id, idempotency_key)
                )
                """
            ).format(self._table("reasoning_events"))
        )
        connection.execute(
            sql.SQL("CREATE INDEX {} ON {} (run_id, run_sequence)").format(
                sql.Identifier("reasoning_events_run_order"),
                self._table("reasoning_events"),
            )
        )
        connection.execute(
            sql.SQL(
                """
                CREATE TABLE {} (
                    run_id TEXT PRIMARY KEY,
                    result_id TEXT NOT NULL UNIQUE,
                    result_hash TEXT NOT NULL,
                    terminal_state TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            ).format(self._table("terminal_results"))
        )

    def _verify_schema(self, connection: Any) -> None:
        expected = {
            "reasoning_store_metadata": {"singleton", "schema_version"},
            "reasoning_events": {
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
            },
            "terminal_results": {
                "run_id",
                "result_id",
                "result_hash",
                "terminal_state",
                "result_json",
                "created_at",
            },
        }
        rows = connection.execute(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = %s",
            (self.schema,),
        ).fetchall()
        actual: dict[str, set[str]] = {}
        for row in rows:
            actual.setdefault(str(row["table_name"]), set()).add(
                str(row["column_name"])
            )
        for table_name, columns in expected.items():
            if actual.get(table_name) != columns:
                raise EventStorePersistenceError(
                    f"PostgreSQL table differs from the contract: {table_name} / "
                    f"PostgreSQL 表与契约不一致: {table_name}"
                )

    def _row_to_event(self, row: Mapping[str, Any]) -> ReasoningEvent:
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
                "invalid PostgreSQL event record / PostgreSQL 事件记录无效: "
                + str(exc)
            ) from exc

    def _load_mirror(self, connection: Any) -> EventStore:
        mirror = EventStore(validate_schema=self._validate_schema_enabled)
        rows = connection.execute(
            sql.SQL("SELECT * FROM {} ORDER BY global_sequence").format(
                self._table("reasoning_events")
            )
        ).fetchall()
        for row in rows:
            mirror._index_restored_event(self._row_to_event(row))
        return mirror

    def _active_context(self) -> _PostgresTransactionContext | None:
        value = getattr(self._local, "transaction", None)
        return value if isinstance(value, _PostgresTransactionContext) else None

    @contextmanager
    def transaction(self, run_id: str) -> Iterator[None]:
        """Serialize a run-local write group with an advisory xact lock.

        / 使用事务级 advisory lock 串行化运行域写组。
        """

        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id is required / 运行标识不能为空")
        with self._lock:
            active = self._active_context()
            if active is not None:
                if active.run_id != run_id:
                    raise EventStorePersistenceError(
                        "nested PostgreSQL transactions must use one run / "
                        "嵌套 PostgreSQL 事务必须属于同一运行"
                    )
                active.depth += 1
                try:
                    yield
                finally:
                    active.depth -= 1
                return
            connection = None
            try:
                connection = self._connect()
                with connection.transaction():
                    self._set_transaction_guards(connection)
                    connection.execute(
                        "SELECT pg_advisory_xact_lock(%s)",
                        (self._advisory_key(run_id),),
                    )
                    context = _PostgresTransactionContext(
                        connection=connection,
                        mirror=self._load_mirror(connection),
                        run_id=run_id,
                    )
                    self._local.transaction = context
                    yield
            except (EventStorePersistenceError, DuplicateEventConflictError):
                raise
            except Exception as exc:
                if psycopg is not None and isinstance(exc, psycopg.errors.UniqueViolation):
                    raise DuplicateEventConflictError(
                        "PostgreSQL uniqueness conflict / PostgreSQL 唯一性冲突"
                    ) from exc
                if psycopg is not None and isinstance(exc, psycopg.Error):
                    raise EventStorePersistenceError(
                        "PostgreSQL event transaction failed / "
                        "PostgreSQL 事件事务失败"
                    ) from exc
                raise
            finally:
                if hasattr(self._local, "transaction"):
                    del self._local.transaction
                if connection is not None:
                    connection.close()

    def _append_in_context(
        self,
        context: _PostgresTransactionContext,
        kwargs: dict[str, Any],
    ) -> ReasoningEvent:
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
            sql.SQL(
                """
                INSERT INTO {} (
                    run_id, run_sequence, event_id, idempotency_key, event_type,
                    workflow_state, occurred_epoch, envelope_json, payload_json,
                    content_json
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            ).format(self._table("reasoning_events")),
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
        """Append under the advisory-locked authoritative head.

        / 在 advisory lock 保护的权威流头下追加。
        """

        run_id = kwargs.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id is required / 运行标识不能为空")
        active = self._active_context()
        if active is not None:
            if active.run_id != run_id:
                raise EventStorePersistenceError(
                    "active PostgreSQL transaction belongs to another run / "
                    "活动 PostgreSQL 事务属于另一运行"
                )
            return self._append_in_context(active, dict(kwargs))
        with self.transaction(run_id):
            active = self._active_context()
            if active is None:  # pragma: no cover - context invariant / 上下文不变量
                raise EventStorePersistenceError(
                    "PostgreSQL transaction context is missing / PostgreSQL 事务上下文缺失"
                )
            return self._append_in_context(active, dict(kwargs))

    def events(self, run_id: str | None = None) -> tuple[ReasoningEvent, ...]:
        """Return one validated network snapshot / 返回一份已校验的网络快照。"""

        active = self._active_context()
        if active is not None:
            return active.mirror.events(run_id)
        with self._lock:
            connection = None
            try:
                connection = self._connect()
                with connection.transaction():
                    result = self._load_mirror(connection).events(run_id)
                return result
            except EventStorePersistenceError:
                raise
            except Exception as exc:
                if psycopg is not None and isinstance(exc, psycopg.Error):
                    raise EventStorePersistenceError(
                        "PostgreSQL event read failed / PostgreSQL 事件读取失败"
                    ) from exc
                raise
            finally:
                if connection is not None:
                    connection.close()

    def find_idempotency(self, run_id: str, key: str) -> ReasoningEvent | None:
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
        events = self.events(run_id)
        if reducer is None:
            return events
        state = initial
        for event in events:
            state = reducer(state, event)
        return state

    def _assert_result_stream(
        self,
        connection: Any,
        run_id: str,
        terminal_state: str,
    ) -> None:
        row = connection.execute(
            sql.SQL(
                "SELECT workflow_state FROM {} WHERE run_id = %s "
                "ORDER BY run_sequence DESC LIMIT 1"
            ).format(self._table("reasoning_events")),
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
        connection: Any,
        run_id: str,
        result_json: str,
    ) -> dict[str, Any]:
        artifact = json.loads(result_json)
        self._assert_result_stream(connection, run_id, artifact["terminal_state"])
        existing = connection.execute(
            sql.SQL("SELECT result_json FROM {} WHERE run_id = %s FOR UPDATE").format(
                self._table("terminal_results")
            ),
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
            sql.SQL("SELECT run_id FROM {} WHERE result_id = %s FOR UPDATE").format(
                self._table("terminal_results")
            ),
            (artifact["result_id"],),
        ).fetchone()
        if conflicting is not None:
            raise DuplicateEventConflictError(
                "terminal result_id is already used by another run / "
                "终态结果标识已被其他运行使用"
            )
        connection.execute(
            sql.SQL(
                "INSERT INTO {} (run_id, result_id, result_hash, terminal_state, "
                "result_json, created_at) VALUES (%s, %s, %s, %s, %s, %s)"
            ).format(self._table("terminal_results")),
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
        result_json = self._terminal_result_json(run_id, result)
        active = self._active_context()
        if active is not None:
            if active.run_id != run_id:
                raise EventStorePersistenceError(
                    "active PostgreSQL transaction belongs to another run / "
                    "活动 PostgreSQL 事务属于另一运行"
                )
            return self._save_terminal_result_in_connection(
                active.connection, run_id, result_json
            )
        with self.transaction(run_id):
            active = self._active_context()
            if active is None:  # pragma: no cover
                raise EventStorePersistenceError(
                    "PostgreSQL transaction context is missing / PostgreSQL 事务上下文缺失"
                )
            return self._save_terminal_result_in_connection(
                active.connection, run_id, result_json
            )

    def _load_terminal_result_in_connection(
        self,
        connection: Any,
        run_id: str,
    ) -> dict[str, Any] | None:
        row = connection.execute(
            sql.SQL("SELECT * FROM {} WHERE run_id = %s").format(
                self._table("terminal_results")
            ),
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
            self._terminal_result_json(run_id, artifact)
            self._assert_result_stream(connection, run_id, artifact["terminal_state"])
            return artifact
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise EventStorePersistenceError(
                "invalid PostgreSQL terminal result record / "
                "PostgreSQL 终态结果记录无效: " + str(exc)
            ) from exc

    def load_terminal_result(self, run_id: str) -> dict[str, Any] | None:
        active = self._active_context()
        if active is not None:
            return self._load_terminal_result_in_connection(active.connection, run_id)
        with self._lock:
            connection = None
            try:
                connection = self._connect()
                with connection.transaction():
                    result = self._load_terminal_result_in_connection(connection, run_id)
                return result
            except EventStorePersistenceError:
                raise
            except Exception as exc:
                if psycopg is not None and isinstance(exc, psycopg.Error):
                    raise EventStorePersistenceError(
                        "PostgreSQL terminal result read failed / "
                        "PostgreSQL 终态结果读取失败"
                    ) from exc
                raise
            finally:
                if connection is not None:
                    connection.close()

    def health_check(self) -> dict[str, Any]:
        """Return bounded database health without DSN or event content.

        / 返回不含 DSN 或事件内容的有限数据库健康信息。
        """

        connection = None
        try:
            connection = self._connect()
            with connection.transaction():
                server_version = connection.execute(
                    "SELECT current_setting('server_version') AS version"
                ).fetchone()["version"]
                event_count = connection.execute(
                    sql.SQL("SELECT COUNT(*) AS count FROM {}").format(
                        self._table("reasoning_events")
                    )
                ).fetchone()["count"]
                run_count = connection.execute(
                    sql.SQL("SELECT COUNT(DISTINCT run_id) AS count FROM {}").format(
                        self._table("reasoning_events")
                    )
                ).fetchone()["count"]
                result_count = connection.execute(
                    sql.SQL("SELECT COUNT(*) AS count FROM {}").format(
                        self._table("terminal_results")
                    )
                ).fetchone()["count"]
            return {
                "schema_version": POSTGRES_EVENT_SCHEMA_VERSION,
                "schema": self.schema,
                "server_version": str(server_version),
                "event_count": int(event_count),
                "run_count": int(run_count),
                "result_count": int(result_count),
            }
        except Exception as exc:
            if psycopg is not None and isinstance(exc, psycopg.Error):
                raise EventStorePersistenceError(
                    "PostgreSQL event health check failed / "
                    "PostgreSQL 事件健康检查失败"
                ) from exc
            raise
        finally:
            if connection is not None:
                connection.close()


__all__ = ["POSTGRES_EVENT_SCHEMA_VERSION", "PostgresEventStore"]
