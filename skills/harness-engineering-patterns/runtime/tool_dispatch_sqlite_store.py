"""SQLite WAL store for governed tool dispatch / 受治理工具调度 SQLite WAL 存储。

The adapter is a single-node, multi-writer reference.  It atomically owns one
idempotency identity, fences stale completions with a secret lease token, turns
an expired in-flight write into ``unknown`` rather than retrying it, preserves
immutable successful results, and allocates contiguous per-run event sequences.

/ 本适配器是单节点多写者参考实现。它原子占有一个幂等身份，使用秘密租约令牌隔离
陈旧完成；进行中的写租约过期后转为“结果未知”而不是直接重试；成功结果保持不可变；
并分配单运行连续事件序号。
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
from typing import Any, Iterator, Mapping

try:  # Package import / 包导入
    from .reasoning_artifacts import (
        artifact_fingerprint,
        validate_tool_execution_event,
        validate_tool_execution_result,
    )
    from .tool_dispatch import (
        ExecutionClassification,
        LeaseAcquisition,
        LeaseDisposition,
        ToolDispatchConflictError,
        ToolDispatchError,
        seal_tool_execution_event,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import (
        artifact_fingerprint,
        validate_tool_execution_event,
        validate_tool_execution_result,
    )
    from tool_dispatch import (
        ExecutionClassification,
        LeaseAcquisition,
        LeaseDisposition,
        ToolDispatchConflictError,
        ToolDispatchError,
        seal_tool_execution_event,
    )


SQLITE_TOOL_DISPATCH_SCHEMA_VERSION = 1


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _parse_time(name: str, value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ToolDispatchError(f"{name} must be RFC3339")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ToolDispatchError(f"{name} must be RFC3339") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ToolDispatchError(f"{name} must include timezone")
    return parsed.astimezone(timezone.utc)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _token_hash(token: str) -> str:
    return "sha256:" + hashlib.sha256(token.encode("utf-8")).hexdigest()


def _key_hash(key: str) -> str:
    return artifact_fingerprint({"idempotency_key": key})


def _observed_binding(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if value.get("state") != "observed":
        return None
    nested = value.get("value")
    return nested if isinstance(nested, Mapping) else None


class SqliteToolDispatchStore:
    """Transactional event and idempotency store / 事务型事件与幂等存储。"""

    durable = True

    def __init__(
        self,
        path: str | Path,
        *,
        timeout_seconds: float = 5.0,
        token_factory: Any | None = None,
    ) -> None:
        self.path = Path(path).resolve()
        if self.path.exists() and self.path.is_dir():
            raise ToolDispatchError("SQLite path cannot be a directory")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if timeout_seconds <= 0:
            raise ToolDispatchError("timeout_seconds must be positive")
        self.timeout_seconds = float(timeout_seconds)
        self._token_factory = token_factory or (lambda: secrets.token_urlsafe(32))
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            str(self.path),
            timeout=self.timeout_seconds,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            f"PRAGMA busy_timeout = {max(1, int(self.timeout_seconds * 1000))}"
        )
        return connection

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        connection = self._connect()
        try:
            journal_mode = connection.execute("PRAGMA journal_mode = WAL").fetchone()[0]
            if str(journal_mode).lower() != "wal":
                raise ToolDispatchError("SQLite WAL mode is required")
            connection.execute("PRAGMA synchronous = FULL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS store_metadata (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    schema_version INTEGER NOT NULL
                )
                """
            )
            row = connection.execute(
                "SELECT schema_version FROM store_metadata WHERE singleton = 1"
            ).fetchone()
            if row is None:
                connection.execute(
                    "INSERT INTO store_metadata(singleton, schema_version) VALUES (1, ?)",
                    (SQLITE_TOOL_DISPATCH_SCHEMA_VERSION,),
                )
            elif int(row["schema_version"]) != SQLITE_TOOL_DISPATCH_SCHEMA_VERSION:
                raise ToolDispatchError(
                    "unsupported SQLite tool-dispatch schema version / "
                    "不支持的 SQLite 工具调度 Schema 版本"
                )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS action_idempotency (
                    idempotency_hash TEXT PRIMARY KEY,
                    intent_hash TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    attempt_id TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('executing', 'succeeded', 'explicit_failure', 'unknown', 'partial')
                    ),
                    lease_revision INTEGER NOT NULL CHECK (lease_revision >= 0),
                    lease_token_hash TEXT,
                    lease_binding_json TEXT,
                    lease_expires_at TEXT,
                    result_json TEXT,
                    result_hash TEXT,
                    updated_at TEXT NOT NULL,
                    CHECK (
                        (status = 'executing' AND lease_token_hash IS NOT NULL
                         AND lease_binding_json IS NOT NULL AND lease_expires_at IS NOT NULL)
                        OR status <> 'executing'
                    ),
                    CHECK (
                        (status = 'succeeded' AND result_json IS NOT NULL AND result_hash IS NOT NULL)
                        OR status <> 'succeeded'
                    )
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tool_events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    event_key TEXT NOT NULL,
                    sequence INTEGER NOT NULL CHECK (sequence >= 1),
                    draft_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    UNIQUE(run_id, event_key),
                    UNIQUE(run_id, sequence)
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_tool_events_run ON tool_events(run_id, sequence)"
            )
        finally:
            connection.close()

    def append_event(self, event_draft: Mapping[str, Any]) -> Mapping[str, Any]:
        """Idempotently append an event with a contiguous per-run sequence.

        / 幂等追加事件并分配单运行连续序号。
        """

        draft = deepcopy(dict(event_draft))
        for forbidden in ("event_id", "sequence", "event_hash"):
            if forbidden in draft:
                raise ToolDispatchError(
                    f"event draft cannot supply {forbidden} / 事件草稿不得提供 {forbidden}"
                )
        run_id = str(draft.get("run_id", ""))
        event_key = str(draft.get("event_key", ""))
        if not run_id or not event_key:
            raise ToolDispatchError("event draft requires run_id and event_key")
        draft_hash = artifact_fingerprint(draft)
        with self._transaction() as connection:
            existing = connection.execute(
                """
                SELECT draft_hash, event_json
                FROM tool_events
                WHERE run_id = ? AND event_key = ?
                """,
                (run_id, event_key),
            ).fetchone()
            if existing is not None:
                if existing["draft_hash"] != draft_hash:
                    raise ToolDispatchConflictError(
                        "event key reused with different content / 事件键复用于不同内容"
                    )
                event = json.loads(existing["event_json"])
                validate_tool_execution_event(event)
                return event
            sequence = int(
                connection.execute(
                    "SELECT COALESCE(MAX(sequence), 0) + 1 FROM tool_events WHERE run_id = ?",
                    (run_id,),
                ).fetchone()[0]
            )
            event = seal_tool_execution_event(draft, sequence=sequence)
            connection.execute(
                """
                INSERT INTO tool_events(
                    event_id, run_id, event_key, sequence,
                    draft_hash, event_hash, event_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["event_id"],
                    run_id,
                    event_key,
                    sequence,
                    draft_hash,
                    event["event_hash"],
                    _canonical_json(event),
                ),
            )
            return deepcopy(event)

    def acquire(
        self,
        *,
        idempotency_key: str,
        intent_hash: str,
        action_id: str,
        attempt_id: str,
        acquired_at: str,
        lease_seconds: int,
        retry_authorized: bool,
    ) -> LeaseAcquisition:
        """Atomically acquire or inspect one business idempotency identity.

        / 原子取得或检查一个业务幂等身份。
        """

        if not idempotency_key:
            raise ToolDispatchError("idempotency_key must be non-empty")
        if (
            isinstance(lease_seconds, bool)
            or not isinstance(lease_seconds, int)
            or lease_seconds < 1
        ):
            raise ToolDispatchError("lease_seconds must be positive")
        acquired = _parse_time("acquired_at", acquired_at)
        idempotency_hash = _key_hash(idempotency_key)
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT * FROM action_idempotency WHERE idempotency_hash = ?",
                (idempotency_hash,),
            ).fetchone()
            if row is None:
                return self._insert_lease(
                    connection,
                    idempotency_hash=idempotency_hash,
                    intent_hash=intent_hash,
                    action_id=action_id,
                    attempt_id=attempt_id,
                    revision=1,
                    acquired=acquired,
                    lease_seconds=lease_seconds,
                )
            if row["intent_hash"] != intent_hash:
                raise ToolDispatchConflictError(
                    "idempotency key conflicts with another action intent / "
                    "幂等键与另一行动意图冲突"
                )
            status = str(row["status"])
            prior_binding = (
                None
                if row["lease_binding_json"] is None
                else json.loads(row["lease_binding_json"])
            )
            if status == "succeeded":
                prior_result = json.loads(row["result_json"])
                validate_tool_execution_result(prior_result)
                return LeaseAcquisition(
                    LeaseDisposition.REUSED_SUCCESS,
                    None,
                    prior_binding,
                    prior_result=prior_result,
                    reason_code="PRIOR_SUCCESS_REUSED",
                )
            if status == "executing":
                expires_at = _parse_time(
                    "lease_expires_at",
                    str(row["lease_expires_at"]),
                )
                if expires_at > acquired:
                    return LeaseAcquisition(
                        LeaseDisposition.BUSY,
                        None,
                        prior_binding,
                        reason_code="LEASE_HELD",
                    )
                connection.execute(
                    """
                    UPDATE action_idempotency
                    SET status = 'unknown',
                        lease_token_hash = NULL,
                        lease_expires_at = NULL,
                        updated_at = ?
                    WHERE idempotency_hash = ?
                    """,
                    (_format_time(acquired), idempotency_hash),
                )
                return LeaseAcquisition(
                    LeaseDisposition.VERIFY_UNKNOWN,
                    None,
                    prior_binding,
                    reason_code="EXPIRED_LEASE_RESULT_UNKNOWN",
                )
            if status in {"unknown", "partial"}:
                return LeaseAcquisition(
                    LeaseDisposition.VERIFY_UNKNOWN,
                    None,
                    prior_binding,
                    reason_code=(
                        "PRIOR_RESULT_UNKNOWN"
                        if status == "unknown"
                        else "PRIOR_RESULT_PARTIAL"
                    ),
                )
            if status == "explicit_failure" and not retry_authorized:
                return LeaseAcquisition(
                    LeaseDisposition.RETRY_AUTHORIZATION_REQUIRED,
                    None,
                    prior_binding,
                    reason_code="EXPLICIT_FAILURE_REQUIRES_AUTHORIZED_RETRY",
                )
            return self._replace_lease(
                connection,
                idempotency_hash=idempotency_hash,
                intent_hash=intent_hash,
                action_id=action_id,
                attempt_id=attempt_id,
                revision=int(row["lease_revision"]) + 1,
                acquired=acquired,
                lease_seconds=lease_seconds,
            )

    def _new_lease(
        self,
        *,
        idempotency_hash: str,
        intent_hash: str,
        action_id: str,
        attempt_id: str,
        revision: int,
        acquired: datetime,
        lease_seconds: int,
    ) -> tuple[str, dict[str, Any], str]:
        token = str(self._token_factory())
        if not token:
            raise ToolDispatchError("token factory returned an empty token")
        token_digest = _token_hash(token)
        expires_at = _format_time(acquired + timedelta(seconds=lease_seconds))
        lease_id = (
            "TOOL_LEASE_"
            + artifact_fingerprint(
                {
                    "idempotency_hash": idempotency_hash,
                    "intent_hash": intent_hash,
                    "revision": revision,
                }
            ).removeprefix("sha256:")[:24]
        )
        content = {
            "lease_id": lease_id,
            "revision": revision,
            "idempotency_hash": idempotency_hash,
            "intent_hash": intent_hash,
            "action_id": action_id,
            "attempt_id": attempt_id,
            "token_hash": token_digest,
            "acquired_at": _format_time(acquired),
            "expires_at": expires_at,
        }
        binding = {
            "id": lease_id,
            "version": f"1.0.{revision - 1}",
            "hash": artifact_fingerprint(content),
        }
        return token, binding, expires_at

    def _insert_lease(
        self,
        connection: sqlite3.Connection,
        **values: Any,
    ) -> LeaseAcquisition:
        token, binding, expires_at = self._new_lease(**values)
        connection.execute(
            """
            INSERT INTO action_idempotency(
                idempotency_hash, intent_hash, action_id, attempt_id,
                status, lease_revision, lease_token_hash,
                lease_binding_json, lease_expires_at, result_json,
                result_hash, updated_at
            ) VALUES (?, ?, ?, ?, 'executing', ?, ?, ?, ?, NULL, NULL, ?)
            """,
            (
                values["idempotency_hash"],
                values["intent_hash"],
                values["action_id"],
                values["attempt_id"],
                values["revision"],
                _token_hash(token),
                _canonical_json(binding),
                expires_at,
                _format_time(values["acquired"]),
            ),
        )
        return LeaseAcquisition(
            LeaseDisposition.ACQUIRED,
            token,
            binding,
            reason_code="LEASE_ACQUIRED",
        )

    def _replace_lease(
        self,
        connection: sqlite3.Connection,
        **values: Any,
    ) -> LeaseAcquisition:
        token, binding, expires_at = self._new_lease(**values)
        connection.execute(
            """
            UPDATE action_idempotency
            SET action_id = ?,
                attempt_id = ?,
                status = 'executing',
                lease_revision = ?,
                lease_token_hash = ?,
                lease_binding_json = ?,
                lease_expires_at = ?,
                result_json = NULL,
                result_hash = NULL,
                updated_at = ?
            WHERE idempotency_hash = ? AND intent_hash = ?
            """,
            (
                values["action_id"],
                values["attempt_id"],
                values["revision"],
                _token_hash(token),
                _canonical_json(binding),
                expires_at,
                _format_time(values["acquired"]),
                values["idempotency_hash"],
                values["intent_hash"],
            ),
        )
        return LeaseAcquisition(
            LeaseDisposition.ACQUIRED,
            token,
            binding,
            reason_code="AUTHORIZED_RETRY_LEASE_ACQUIRED",
        )

    def complete(
        self,
        *,
        idempotency_key: str,
        lease_token: str,
        result: Mapping[str, Any],
        completed_at: str,
    ) -> None:
        """Fence the active holder and persist one classified result.

        / 隔离非当前持有者并持久化一个分类结果。
        """

        validate_tool_execution_result(result)
        completed = _parse_time("completed_at", completed_at)
        idempotency_hash = _key_hash(idempotency_key)
        token_digest = _token_hash(lease_token)
        status_map = {
            ExecutionClassification.SUCCESS.value: "succeeded",
            ExecutionClassification.EXPLICIT_FAILURE.value: "explicit_failure",
            ExecutionClassification.UNKNOWN.value: "unknown",
            ExecutionClassification.PARTIAL_SUCCESS.value: "partial",
            ExecutionClassification.WAITING.value: "unknown",
        }
        try:
            status = status_map[str(result["classification"])]
        except KeyError as exc:
            raise ToolDispatchError(
                "active lease can only complete with an executed result / "
                "活跃租约只能以已执行结果完成"
            ) from exc
        expired_before_completion = False
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT * FROM action_idempotency WHERE idempotency_hash = ?",
                (idempotency_hash,),
            ).fetchone()
            if row is None:
                raise ToolDispatchConflictError("idempotency record does not exist")
            if row["status"] != "executing":
                if (
                    row["status"] == "succeeded"
                    and row["result_hash"] == result["result_hash"]
                ):
                    return
                raise ToolDispatchConflictError(
                    "completion does not own an executing record / 完成操作未持有执行中记录"
                )
            if row["lease_token_hash"] != token_digest:
                raise ToolDispatchConflictError(
                    "stale or foreign lease token / 陈旧或外部租约令牌"
                )
            current_lease_binding = json.loads(str(row["lease_binding_json"]))
            result_lease_binding = _observed_binding(result["lease_binding"])
            if (
                result_lease_binding != current_lease_binding
                or result["action_id"] != row["action_id"]
                or result["attempt_id"] != row["attempt_id"]
            ):
                raise ToolDispatchConflictError(
                    "result does not bind the active lease attempt / "
                    "结果未绑定当前活动租约尝试"
                )
            expires = _parse_time("lease_expires_at", str(row["lease_expires_at"]))
            if completed > expires:
                connection.execute(
                    """
                    UPDATE action_idempotency
                    SET status = 'unknown',
                        lease_token_hash = NULL,
                        lease_expires_at = NULL,
                        updated_at = ?
                    WHERE idempotency_hash = ?
                    """,
                    (_format_time(completed), idempotency_hash),
                )
                expired_before_completion = True
            else:
                connection.execute(
                    """
                    UPDATE action_idempotency
                    SET status = ?,
                        lease_token_hash = NULL,
                        lease_expires_at = NULL,
                        result_json = ?,
                        result_hash = ?,
                        updated_at = ?
                    WHERE idempotency_hash = ?
                    """,
                    (
                        status,
                        _canonical_json(dict(result)),
                        result["result_hash"],
                        _format_time(completed),
                        idempotency_hash,
                    ),
                )
        if expired_before_completion:
            raise ToolDispatchConflictError(
                "lease expired before completion; result requires reconciliation / "
                "租约在完成前已过期，结果需要核验"
            )

    def events(self, run_id: str) -> tuple[dict[str, Any], ...]:
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT event_json
                FROM tool_events
                WHERE run_id = ?
                ORDER BY sequence
                """,
                (run_id,),
            ).fetchall()
        finally:
            connection.close()
        events = tuple(json.loads(row["event_json"]) for row in rows)
        for event in events:
            validate_tool_execution_event(event)
        return events

    def idempotency_status(self, idempotency_key: str) -> dict[str, Any] | None:
        """Return bounded metadata without the raw key or lease token.

        / 返回不含原始幂等键或租约令牌的有界元数据。
        """

        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT idempotency_hash, intent_hash, action_id, attempt_id,
                       status, lease_revision, lease_binding_json,
                       lease_expires_at, result_hash, updated_at
                FROM action_idempotency
                WHERE idempotency_hash = ?
                """,
                (_key_hash(idempotency_key),),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        return {
            "idempotency_hash": row["idempotency_hash"],
            "intent_hash": row["intent_hash"],
            "action_id": row["action_id"],
            "attempt_id": row["attempt_id"],
            "status": row["status"],
            "lease_revision": row["lease_revision"],
            "lease_binding": (
                None
                if row["lease_binding_json"] is None
                else json.loads(row["lease_binding_json"])
            ),
            "lease_expires_at": row["lease_expires_at"],
            "result_hash": row["result_hash"],
            "updated_at": row["updated_at"],
        }

    def health_check(self) -> dict[str, Any]:
        """Report storage mechanics, not business correctness.

        / 仅报告存储机械健康，不证明业务正确。
        """

        connection = self._connect()
        try:
            quick_check = str(connection.execute("PRAGMA quick_check").fetchone()[0])
            foreign_key_violations = len(
                connection.execute("PRAGMA foreign_key_check").fetchall()
            )
            journal_mode = str(
                connection.execute("PRAGMA journal_mode").fetchone()[0]
            ).lower()
            action_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM action_idempotency"
                ).fetchone()[0]
            )
            event_count = int(
                connection.execute("SELECT COUNT(*) FROM tool_events").fetchone()[0]
            )
            unknown_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM action_idempotency WHERE status IN ('unknown', 'partial')"
                ).fetchone()[0]
            )
            schema_version = int(
                connection.execute(
                    "SELECT schema_version FROM store_metadata WHERE singleton = 1"
                ).fetchone()[0]
            )
        finally:
            connection.close()
        return {
            "healthy": (
                quick_check == "ok"
                and foreign_key_violations == 0
                and journal_mode == "wal"
                and schema_version == SQLITE_TOOL_DISPATCH_SCHEMA_VERSION
            ),
            "schema_version": schema_version,
            "journal_mode": journal_mode,
            "quick_check": quick_check,
            "foreign_key_violations": foreign_key_violations,
            "action_count": action_count,
            "event_count": event_count,
            "unknown_or_partial_count": unknown_count,
        }


__all__ = [
    "SQLITE_TOOL_DISPATCH_SCHEMA_VERSION",
    "SqliteToolDispatchStore",
]
