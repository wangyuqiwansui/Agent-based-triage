"""Transactional parallel-worker outbox with fencing / 带栅栏的事务型并行工作者发件箱。

The SQLite reference couples lease acquisition and public work dispatch in one
database transaction. Delivery remains at-least-once: dispatchers claim rows
with expiring delivery tokens, while worker results are fenced by a token that
increases across path reassignments. No tool execution or network I/O occurs in
this module. / SQLite 参考实现把租约获取与公开工作分派耦合在同一数据库事务中。
交付保持至少一次：分派器用可过期交付令牌领取记录，工作者结果则由跨路径重新分配
单调递增的栅栏令牌保护。本模块不执行工具或网络 I/O。
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
import sqlite3
from typing import Any, Iterable, Mapping, Protocol
import uuid

try:  # Package import / 包导入
    from .reasoning_event_sqlite_store import SqliteEventStore
    from .reasoning_parallel_factory import ParallelBranchOutcome, ParallelPlanStateError
    from .reasoning_parallel_scheduler import ParallelPathLease, ParallelPathScheduler
    from .reasoning_runtime import (
        BudgetUsage,
        _assert_no_private_reasoning,
        _canonical_json,
        _iso_utc,
        _normalize_versioned_bindings,
        _validate_identifier,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_event_sqlite_store import SqliteEventStore
    from reasoning_parallel_factory import ParallelBranchOutcome, ParallelPlanStateError
    from reasoning_parallel_scheduler import ParallelPathLease, ParallelPathScheduler
    from reasoning_runtime import (
        BudgetUsage,
        _assert_no_private_reasoning,
        _canonical_json,
        _iso_utc,
        _normalize_versioned_bindings,
        _validate_identifier,
    )


SQLITE_PARALLEL_OUTBOX_SCHEMA_VERSION = 1
_OUTBOX_STATUSES = {
    "pending",
    "claimed",
    "delivered",
    "completed",
    "superseded",
    "dead_lettered",
}


class ParallelDispatchError(RuntimeError):
    """Base dispatch/outbox failure / 分派与发件箱基础错误。"""


class ParallelDispatchConflictError(ParallelDispatchError):
    """An immutable dispatch identity was reused differently / 不可变分派标识被异内容复用。"""


class ParallelDispatchClaimError(ParallelDispatchError):
    """A delivery acknowledgement has no current claim / 交付确认没有对应的当前领取。"""


class ParallelDispatchOutbox(Protocol):
    """Storage contract required by the dispatch coordinator / 分派协调器所需存储契约。"""

    event_store: Any

    def enqueue(self, **kwargs: Any) -> "ParallelWorkDispatch": ...

    def find_acquisition(
        self, dispatch_id: str, lease_id: str
    ) -> "ParallelWorkDispatch | None": ...

    def prepare_completion(self, **kwargs: Any) -> "ParallelDispatchCompletion": ...


@dataclass(frozen=True)
class ParallelWorkDispatch:
    """One validated public worker dispatch / 一条已校验的公开工作者分派。"""

    dispatch_id: str
    run_id: str
    candidate_path_id: str
    step_id: str
    lease_id: str
    fencing_token: int
    status: str
    delivery_attempt_count: int
    delivery_token: str | None
    delivery_owner: str | None
    claimed_at: str | None
    claim_expires_at: str | None
    delivered_at: str | None
    completed_at: str | None
    last_error: str | None
    created_at: str
    dispatch_hash: str
    dispatch_json: str = field(repr=False)

    def as_dict(self) -> dict[str, Any]:
        """Return detached immutable dispatch content / 返回独立的不可变分派内容。"""

        return json.loads(self.dispatch_json)

    @property
    def work_payload(self) -> dict[str, Any]:
        """Return detached public work payload / 返回独立的公开工作负载。"""

        return self.as_dict()["work_payload"]


@dataclass(frozen=True)
class ParallelDispatchAcquisition:
    """Atomic lease and outbox acquisition / 原子租约与发件箱获取结果。"""

    lease: ParallelPathLease
    dispatch: ParallelWorkDispatch


@dataclass(frozen=True)
class ParallelDispatchCompletion:
    """Prepared completion and exact-retry signal / 已准备的完成及完全重试标志。"""

    dispatch: ParallelWorkDispatch
    exact_retry: bool


class SqliteParallelDispatchOutbox:
    """Persist public worker commands beside one ``SqliteEventStore``.

    / 在一个 ``SqliteEventStore`` 旁持久化公开工作者命令。
    """

    STORAGE_SCHEMA_VERSION = "1.0.0"

    def __init__(self, event_store: SqliteEventStore) -> None:
        if not isinstance(event_store, SqliteEventStore):
            raise TypeError(
                "event_store must be SqliteEventStore / event_store 必须为 SqliteEventStore"
            )
        self.event_store = event_store
        self._initialize()

    @staticmethod
    def _hash(value: Mapping[str, Any]) -> str:
        encoded = _canonical_json(dict(value)).encode("utf-8")
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    def _initialize(self) -> None:
        try:
            with self.event_store._lock:
                connection = self.event_store._connect()
                try:
                    connection.execute("BEGIN IMMEDIATE")
                    connection.execute(
                        """
                        CREATE TABLE IF NOT EXISTS parallel_dispatch_metadata (
                            singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                            schema_version INTEGER NOT NULL
                        )
                        """
                    )
                    version_row = connection.execute(
                        "SELECT schema_version FROM parallel_dispatch_metadata "
                        "WHERE singleton = 1"
                    ).fetchone()
                    if version_row is None:
                        connection.execute(
                            "INSERT INTO parallel_dispatch_metadata "
                            "(singleton, schema_version) VALUES (1, ?)",
                            (SQLITE_PARALLEL_OUTBOX_SCHEMA_VERSION,),
                        )
                    elif int(version_row["schema_version"]) != SQLITE_PARALLEL_OUTBOX_SCHEMA_VERSION:
                        raise ParallelDispatchError(
                            "unsupported parallel outbox schema version / "
                            "不支持的并行发件箱 Schema 版本"
                        )
                    connection.execute(
                        """
                        CREATE TABLE IF NOT EXISTS parallel_dispatch_outbox (
                            dispatch_id TEXT PRIMARY KEY,
                            run_id TEXT NOT NULL,
                            candidate_path_id TEXT NOT NULL,
                            step_id TEXT NOT NULL,
                            lease_id TEXT NOT NULL UNIQUE,
                            fencing_token INTEGER NOT NULL CHECK (fencing_token > 0),
                            lease_expires_epoch REAL NOT NULL,
                            status TEXT NOT NULL CHECK (
                                status IN (
                                    'pending', 'claimed', 'delivered', 'completed',
                                    'superseded', 'dead_lettered'
                                )
                            ),
                            delivery_attempt_count INTEGER NOT NULL DEFAULT 0
                                CHECK (delivery_attempt_count >= 0),
                            delivery_token TEXT,
                            delivery_owner TEXT,
                            claimed_at TEXT,
                            claim_expires_at TEXT,
                            claim_expires_epoch REAL,
                            delivered_at TEXT,
                            completed_at TEXT,
                            last_error TEXT,
                            created_at TEXT NOT NULL,
                            created_epoch REAL NOT NULL,
                            dispatch_hash TEXT NOT NULL,
                            dispatch_json TEXT NOT NULL,
                            UNIQUE (run_id, candidate_path_id, fencing_token)
                        )
                        """
                    )
                    connection.execute(
                        "CREATE INDEX IF NOT EXISTS parallel_dispatch_delivery_order "
                        "ON parallel_dispatch_outbox "
                        "(status, created_epoch, dispatch_id)"
                    )
                    self._verify_schema(connection)
                    connection.commit()
                except Exception:
                    if connection.in_transaction:
                        connection.rollback()
                    raise
                finally:
                    connection.close()
        except ParallelDispatchError:
            raise
        except sqlite3.Error as exc:
            raise ParallelDispatchError(
                "SQLite parallel outbox initialization failed / "
                "SQLite 并行发件箱初始化失败"
            ) from exc

    @staticmethod
    def _verify_schema(connection: sqlite3.Connection) -> None:
        expected = {
            "dispatch_id",
            "run_id",
            "candidate_path_id",
            "step_id",
            "lease_id",
            "fencing_token",
            "lease_expires_epoch",
            "status",
            "delivery_attempt_count",
            "delivery_token",
            "delivery_owner",
            "claimed_at",
            "claim_expires_at",
            "claim_expires_epoch",
            "delivered_at",
            "completed_at",
            "last_error",
            "created_at",
            "created_epoch",
            "dispatch_hash",
            "dispatch_json",
        }
        actual = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(parallel_dispatch_outbox)"
            )
        }
        if actual != expected:
            raise ParallelDispatchError(
                "SQLite parallel outbox table differs from the contract / "
                "SQLite 并行发件箱表与契约不一致"
            )

    @staticmethod
    def _positive_seconds(name: str, value: float) -> float:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            or float(value) <= 0
        ):
            raise ValueError(f"{name} must be finite and positive / {name} 必须为有限正数")
        return float(value)

    def _row_to_dispatch(self, row: sqlite3.Row) -> ParallelWorkDispatch:
        try:
            dispatch_json = str(row["dispatch_json"])
            artifact = json.loads(dispatch_json)
            if _canonical_json(artifact) != dispatch_json:
                raise ValueError("dispatch JSON is not canonical")
            declared_hash = artifact.pop("dispatch_hash")
            if declared_hash != self._hash(artifact):
                raise ValueError("dispatch hash mismatch")
            artifact["dispatch_hash"] = declared_hash
            expected = {
                "dispatch_id": str(row["dispatch_id"]),
                "run_id": str(row["run_id"]),
                "candidate_path_id": str(row["candidate_path_id"]),
                "step_id": str(row["step_id"]),
                "lease_id": str(row["lease_id"]),
                "fencing_token": int(row["fencing_token"]),
                "created_at": str(row["created_at"]),
                "dispatch_hash": str(row["dispatch_hash"]),
            }
            if any(artifact.get(key) != value for key, value in expected.items()):
                raise ValueError("dispatch columns differ from immutable content")
            status = str(row["status"])
            if status not in _OUTBOX_STATUSES:
                raise ValueError("unknown outbox status")
            return ParallelWorkDispatch(
                dispatch_id=expected["dispatch_id"],
                run_id=expected["run_id"],
                candidate_path_id=expected["candidate_path_id"],
                step_id=expected["step_id"],
                lease_id=expected["lease_id"],
                fencing_token=expected["fencing_token"],
                status=status,
                delivery_attempt_count=int(row["delivery_attempt_count"]),
                delivery_token=row["delivery_token"],
                delivery_owner=row["delivery_owner"],
                claimed_at=row["claimed_at"],
                claim_expires_at=row["claim_expires_at"],
                delivered_at=row["delivered_at"],
                completed_at=row["completed_at"],
                last_error=row["last_error"],
                created_at=expected["created_at"],
                dispatch_hash=expected["dispatch_hash"],
                dispatch_json=dispatch_json,
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ParallelDispatchError(
                "invalid SQLite parallel dispatch record / "
                "SQLite 并行分派记录无效: " + str(exc)
            ) from exc

    def enqueue(
        self,
        *,
        run_id: str,
        candidate_path_id: str,
        step_id: str,
        plan_binding: Mapping[str, Any],
        lease: ParallelPathLease,
        work_payload: Mapping[str, Any],
        dispatch_id: str | None = None,
    ) -> ParallelWorkDispatch:
        """Insert a dispatch inside the active event transaction.

        / 在活动事件事务内插入分派。
        """

        active = self.event_store._active_context()
        if active is None or active.run_id != run_id:
            raise ParallelDispatchError(
                "outbox enqueue requires the matching active event transaction / "
                "发件箱入队要求匹配的活动事件事务"
            )
        for name, value in (
            ("run_id", run_id),
            ("candidate_path_id", candidate_path_id),
            ("step_id", step_id),
            ("lease_id", lease.lease_id),
        ):
            _validate_identifier(name, value)
        identifier = dispatch_id or f"dispatch-{lease.lease_id}"
        _validate_identifier("dispatch_id", identifier)
        if (
            lease.candidate_path_id != candidate_path_id
            or not lease.active
            or lease.fencing_token < 1
        ):
            raise ParallelDispatchError(
                "dispatch requires the matching active fenced lease / "
                "分派要求匹配的活动带栅栏租约"
            )
        normalized_plan = _normalize_versioned_bindings(
            "plan_binding", (plan_binding,)
        )[0]
        normalized_worker = _normalize_versioned_bindings(
            "worker_binding", (lease.worker_binding,)
        )[0]
        payload = json.loads(_canonical_json(dict(work_payload)))
        _assert_no_private_reasoning(payload, "$.parallel_dispatch.work_payload")
        _, lease_expires_epoch = _iso_utc(lease.expires_at)
        artifact: dict[str, Any] = {
            "schema_version": self.STORAGE_SCHEMA_VERSION,
            "dispatch_id": identifier,
            "run_id": run_id,
            "candidate_path_id": candidate_path_id,
            "step_id": step_id,
            "plan_binding": normalized_plan,
            "lease_id": lease.lease_id,
            "fencing_token": lease.fencing_token,
            "worker_binding": normalized_worker,
            "lease_expires_at": lease.expires_at,
            "deadline_at": lease.deadline_at,
            "work_payload": payload,
            "created_at": lease.acquired_at,
        }
        artifact["dispatch_hash"] = self._hash(artifact)
        dispatch_json = _canonical_json(artifact)
        connection = active.connection
        existing_rows = connection.execute(
            "SELECT * FROM parallel_dispatch_outbox "
            "WHERE dispatch_id = ? OR lease_id = ? OR "
            "(run_id = ? AND candidate_path_id = ? AND fencing_token = ?)",
            (
                identifier,
                lease.lease_id,
                run_id,
                candidate_path_id,
                lease.fencing_token,
            ),
        ).fetchall()
        if existing_rows:
            dispatches = [self._row_to_dispatch(row) for row in existing_rows]
            if len({item.dispatch_id for item in dispatches}) != 1 or any(
                item.dispatch_json != dispatch_json for item in dispatches
            ):
                raise ParallelDispatchConflictError(
                    "dispatch identity reused with different content / "
                    "分派标识被不同内容复用"
                )
            return dispatches[0]
        connection.execute(
            "UPDATE parallel_dispatch_outbox SET status = 'superseded', "
            "delivery_token = NULL, delivery_owner = NULL, claimed_at = NULL, "
            "claim_expires_at = NULL, claim_expires_epoch = NULL, "
            "last_error = ? WHERE run_id = ? AND candidate_path_id = ? "
            "AND fencing_token < ? AND status NOT IN ('completed', 'superseded')",
            (
                "superseded by a newer fencing token / 被更新的栅栏令牌取代",
                run_id,
                candidate_path_id,
                lease.fencing_token,
            ),
        )
        connection.execute(
            """
            INSERT INTO parallel_dispatch_outbox (
                dispatch_id, run_id, candidate_path_id, step_id, lease_id,
                fencing_token, lease_expires_epoch, status, created_at,
                created_epoch, dispatch_hash, dispatch_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)
            """,
            (
                identifier,
                run_id,
                candidate_path_id,
                step_id,
                lease.lease_id,
                lease.fencing_token,
                lease_expires_epoch,
                lease.acquired_at,
                _iso_utc(lease.acquired_at)[1],
                artifact["dispatch_hash"],
                dispatch_json,
            ),
        )
        row = connection.execute(
            "SELECT * FROM parallel_dispatch_outbox WHERE dispatch_id = ?",
            (identifier,),
        ).fetchone()
        if row is None:  # pragma: no cover - database invariant / 数据库不变量
            raise ParallelDispatchError("inserted dispatch is missing / 已插入分派缺失")
        return self._row_to_dispatch(row)

    def find_acquisition(
        self,
        dispatch_id: str,
        lease_id: str,
    ) -> ParallelWorkDispatch | None:
        """Find an acquisition identity inside the active event transaction.

        / 在活动事件事务内查找获取身份。
        """

        active = self.event_store._active_context()
        if active is None:
            raise ParallelDispatchError(
                "acquisition lookup requires an active event transaction / "
                "获取查找要求活动事件事务"
            )
        row = active.connection.execute(
            "SELECT * FROM parallel_dispatch_outbox "
            "WHERE dispatch_id = ? OR lease_id = ?",
            (dispatch_id, lease_id),
        ).fetchone()
        return None if row is None else self._row_to_dispatch(row)

    def get(self, dispatch_id: str) -> ParallelWorkDispatch | None:
        """Load one validated dispatch / 加载一条已校验分派。"""

        _validate_identifier("dispatch_id", dispatch_id)
        try:
            with self.event_store._lock:
                connection = self.event_store._connect()
                try:
                    row = connection.execute(
                        "SELECT * FROM parallel_dispatch_outbox WHERE dispatch_id = ?",
                        (dispatch_id,),
                    ).fetchone()
                    return None if row is None else self._row_to_dispatch(row)
                finally:
                    connection.close()
        except ParallelDispatchError:
            raise
        except sqlite3.Error as exc:
            raise ParallelDispatchError(
                "SQLite parallel dispatch read failed / SQLite 并行分派读取失败"
            ) from exc

    def claim_batch(
        self,
        *,
        delivery_owner: str,
        limit: int,
        claim_ttl_seconds: float,
        now: float | str | None = None,
    ) -> tuple[ParallelWorkDispatch, ...]:
        """Claim due deliveries with fresh attempt tokens / 用新尝试令牌领取到期交付。"""

        _validate_identifier("delivery_owner", delivery_owner)
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise ValueError("limit must be within 1..1000 / limit 必须位于 1..1000")
        ttl = self._positive_seconds("claim_ttl_seconds", claim_ttl_seconds)
        observed_at, observed_epoch = _iso_utc(now)
        expires_at, expires_epoch = _iso_utc(observed_epoch + ttl)
        try:
            with self.event_store._lock:
                connection = self.event_store._connect()
                try:
                    connection.execute("BEGIN IMMEDIATE")
                    connection.execute(
                        "UPDATE parallel_dispatch_outbox SET status = 'superseded', "
                        "delivery_token = NULL, delivery_owner = NULL, claimed_at = NULL, "
                        "claim_expires_at = NULL, claim_expires_epoch = NULL, "
                        "last_error = ? WHERE status IN ('pending', 'claimed') "
                        "AND lease_expires_epoch <= ?",
                        (
                            "worker lease expired before delivery / 工作者租约在交付前过期",
                            observed_epoch,
                        ),
                    )
                    rows = connection.execute(
                        "SELECT dispatch_id FROM parallel_dispatch_outbox "
                        "WHERE status = 'pending' OR "
                        "(status = 'claimed' AND claim_expires_epoch <= ?) "
                        "ORDER BY created_epoch, dispatch_id LIMIT ?",
                        (observed_epoch, limit),
                    ).fetchall()
                    claimed: list[ParallelWorkDispatch] = []
                    for row in rows:
                        delivery_token = f"delivery-{uuid.uuid4().hex}"
                        connection.execute(
                            "UPDATE parallel_dispatch_outbox SET status = 'claimed', "
                            "delivery_attempt_count = delivery_attempt_count + 1, "
                            "delivery_token = ?, delivery_owner = ?, claimed_at = ?, "
                            "claim_expires_at = ?, claim_expires_epoch = ?, last_error = NULL "
                            "WHERE dispatch_id = ?",
                            (
                                delivery_token,
                                delivery_owner,
                                observed_at,
                                expires_at,
                                expires_epoch,
                                row["dispatch_id"],
                            ),
                        )
                        claimed_row = connection.execute(
                            "SELECT * FROM parallel_dispatch_outbox WHERE dispatch_id = ?",
                            (row["dispatch_id"],),
                        ).fetchone()
                        claimed.append(self._row_to_dispatch(claimed_row))
                    connection.commit()
                    return tuple(claimed)
                except Exception:
                    if connection.in_transaction:
                        connection.rollback()
                    raise
                finally:
                    connection.close()
        except ParallelDispatchError:
            raise
        except sqlite3.Error as exc:
            raise ParallelDispatchError(
                "SQLite parallel dispatch claim failed / SQLite 并行分派领取失败"
            ) from exc

    def acknowledge_delivery(
        self,
        dispatch_id: str,
        *,
        delivery_token: str,
        delivery_owner: str,
        delivered_at: float | str | None = None,
    ) -> ParallelWorkDispatch:
        """Acknowledge only the current delivery attempt / 仅确认当前交付尝试。"""

        return self._finish_claim(
            dispatch_id,
            delivery_token=delivery_token,
            delivery_owner=delivery_owner,
            next_status="delivered",
            observed_at=delivered_at,
            error=None,
        )

    def abandon_delivery(
        self,
        dispatch_id: str,
        *,
        delivery_token: str,
        delivery_owner: str,
        error: str,
        retry: bool = True,
        observed_at: float | str | None = None,
    ) -> ParallelWorkDispatch:
        """Return a failed attempt to pending or dead-letter it.

        / 将失败尝试退回待处理或送入死信。
        """

        if not isinstance(error, str) or not error.strip():
            raise ValueError("error must be non-empty / error 不能为空")
        _assert_no_private_reasoning(error, "$.parallel_dispatch.delivery_error")
        return self._finish_claim(
            dispatch_id,
            delivery_token=delivery_token,
            delivery_owner=delivery_owner,
            next_status="pending" if retry else "dead_lettered",
            observed_at=observed_at,
            error=error,
        )

    def _finish_claim(
        self,
        dispatch_id: str,
        *,
        delivery_token: str,
        delivery_owner: str,
        next_status: str,
        observed_at: float | str | None,
        error: str | None,
    ) -> ParallelWorkDispatch:
        for name, value in (
            ("dispatch_id", dispatch_id),
            ("delivery_token", delivery_token),
            ("delivery_owner", delivery_owner),
        ):
            _validate_identifier(name, value)
        timestamp, _ = _iso_utc(observed_at)
        delivered_at = timestamp if next_status == "delivered" else None
        try:
            with self.event_store._lock:
                connection = self.event_store._connect()
                try:
                    connection.execute("BEGIN IMMEDIATE")
                    current_row = connection.execute(
                        "SELECT * FROM parallel_dispatch_outbox WHERE dispatch_id = ?",
                        (dispatch_id,),
                    ).fetchone()
                    if current_row is not None:
                        current = self._row_to_dispatch(current_row)
                        if (
                            next_status == "delivered"
                            and current.status == "delivered"
                            and current.delivery_token == delivery_token
                            and current.delivery_owner == delivery_owner
                        ):
                            connection.commit()
                            return current
                    if next_status == "delivered":
                        cursor = connection.execute(
                            "UPDATE parallel_dispatch_outbox SET status = 'delivered', "
                            "delivered_at = COALESCE(?, delivered_at), last_error = NULL "
                            "WHERE dispatch_id = ? AND status = 'claimed' "
                            "AND delivery_token = ? AND delivery_owner = ?",
                            (
                                delivered_at,
                                dispatch_id,
                                delivery_token,
                                delivery_owner,
                            ),
                        )
                    else:
                        cursor = connection.execute(
                            "UPDATE parallel_dispatch_outbox SET status = ?, "
                            "delivery_token = NULL, delivery_owner = NULL, claimed_at = NULL, "
                            "claim_expires_at = NULL, claim_expires_epoch = NULL, "
                            "last_error = ? WHERE dispatch_id = ? AND status = 'claimed' "
                            "AND delivery_token = ? AND delivery_owner = ?",
                            (
                                next_status,
                                error,
                                dispatch_id,
                                delivery_token,
                                delivery_owner,
                            ),
                        )
                    if cursor.rowcount != 1:
                        raise ParallelDispatchClaimError(
                            "delivery token is stale or not current / "
                            "交付令牌陈旧或不是当前令牌"
                        )
                    row = connection.execute(
                        "SELECT * FROM parallel_dispatch_outbox WHERE dispatch_id = ?",
                        (dispatch_id,),
                    ).fetchone()
                    result = self._row_to_dispatch(row)
                    connection.commit()
                    return result
                except Exception:
                    if connection.in_transaction:
                        connection.rollback()
                    raise
                finally:
                    connection.close()
        except ParallelDispatchError:
            raise
        except sqlite3.Error as exc:
            raise ParallelDispatchError(
                "SQLite parallel delivery update failed / SQLite 并行交付更新失败"
            ) from exc

    def prepare_completion(
        self,
        *,
        dispatch_id: str,
        run_id: str,
        candidate_path_id: str,
        lease_id: str,
        fencing_token: int,
        completed_at: float | str | None = None,
    ) -> ParallelDispatchCompletion:
        """Mark work complete inside the matching active event transaction.

        / 在匹配的活动事件事务内标记工作完成。
        """

        active = self.event_store._active_context()
        if active is None or active.run_id != run_id:
            raise ParallelDispatchError(
                "completion requires the matching active event transaction / "
                "完成要求匹配的活动事件事务"
            )
        timestamp, _ = _iso_utc(completed_at)
        row = active.connection.execute(
            "SELECT * FROM parallel_dispatch_outbox WHERE dispatch_id = ?",
            (dispatch_id,),
        ).fetchone()
        if row is None:
            raise ParallelDispatchError("dispatch does not exist / 分派不存在")
        dispatch = self._row_to_dispatch(row)
        if (
            dispatch.run_id != run_id
            or dispatch.candidate_path_id != candidate_path_id
            or dispatch.lease_id != lease_id
            or dispatch.fencing_token != fencing_token
        ):
            raise ParallelDispatchConflictError(
                "completion differs from the fenced dispatch / 完成与带栅栏分派不一致"
            )
        if dispatch.status == "completed":
            return ParallelDispatchCompletion(dispatch=dispatch, exact_retry=True)
        if dispatch.status in {"superseded", "dead_lettered"}:
            raise ParallelDispatchConflictError(
                "stale or dead-lettered dispatch cannot complete / "
                "陈旧或死信分派不能完成"
            )
        active.connection.execute(
            "UPDATE parallel_dispatch_outbox SET status = 'completed', "
            "completed_at = ?, delivery_token = NULL, delivery_owner = NULL, "
            "claimed_at = NULL, claim_expires_at = NULL, claim_expires_epoch = NULL "
            "WHERE dispatch_id = ?",
            (timestamp, dispatch_id),
        )
        completed_row = active.connection.execute(
            "SELECT * FROM parallel_dispatch_outbox WHERE dispatch_id = ?",
            (dispatch_id,),
        ).fetchone()
        return ParallelDispatchCompletion(
            dispatch=self._row_to_dispatch(completed_row),
            exact_retry=False,
        )

    def health_check(self) -> dict[str, Any]:
        """Return bounded queue health without payload content / 返回不含负载内容的有限队列健康信息。"""

        try:
            with self.event_store._lock:
                connection = self.event_store._connect()
                try:
                    counts = {status: 0 for status in sorted(_OUTBOX_STATUSES)}
                    for row in connection.execute(
                        "SELECT status, COUNT(*) AS count "
                        "FROM parallel_dispatch_outbox GROUP BY status"
                    ):
                        counts[str(row["status"])] = int(row["count"])
                    attempt_count = int(
                        connection.execute(
                            "SELECT COALESCE(SUM(delivery_attempt_count), 0) AS count "
                            "FROM parallel_dispatch_outbox"
                        ).fetchone()["count"]
                    )
                    return {
                        "schema_version": SQLITE_PARALLEL_OUTBOX_SCHEMA_VERSION,
                        "total_count": sum(counts.values()),
                        "delivery_attempt_count": attempt_count,
                        "status_counts": counts,
                    }
                finally:
                    connection.close()
        except sqlite3.Error as exc:
            raise ParallelDispatchError(
                "SQLite parallel outbox health check failed / "
                "SQLite 并行发件箱健康检查失败"
            ) from exc


class ParallelDispatchCoordinator:
    """Couple scheduler lease events and matching outbox rows atomically.

    / 原子耦合调度器租约事件与匹配的发件箱记录。
    """

    def __init__(
        self,
        scheduler: ParallelPathScheduler,
        outbox: ParallelDispatchOutbox,
    ) -> None:
        if not isinstance(scheduler, ParallelPathScheduler):
            raise TypeError("scheduler must be ParallelPathScheduler / scheduler 类型非法")
        if (
            not hasattr(outbox, "event_store")
            or not callable(getattr(outbox, "enqueue", None))
            or not callable(getattr(outbox, "find_acquisition", None))
            or not callable(getattr(outbox, "prepare_completion", None))
        ):
            raise TypeError("outbox contract is invalid / outbox 契约非法")
        if scheduler.engine.events is not outbox.event_store:
            raise ParallelDispatchError(
                "scheduler and outbox must share one event store / "
                "调度器与发件箱必须共享同一事件库"
            )
        self.scheduler = scheduler
        self.outbox = outbox

    def acquire_and_enqueue(
        self,
        candidate_path_id: str,
        *,
        lease_id: str,
        worker_binding: Mapping[str, Any],
        ttl_seconds: float,
        now: float | str | None = None,
        dispatch_id: str | None = None,
        work_payload: Mapping[str, Any] | None = None,
    ) -> ParallelDispatchAcquisition:
        """Acquire and enqueue as one durable commit / 在一次持久提交中获取并入队。"""

        branch = self.scheduler._branch(candidate_path_id)
        identifier = dispatch_id or f"dispatch-{lease_id}"
        with self.scheduler.engine.events.transaction(self.scheduler.run_id):
            existing = self.outbox.find_acquisition(identifier, lease_id)
            payload = (
                self.scheduler.session._branch_action(branch)
                if work_payload is None
                else json.loads(_canonical_json(dict(work_payload)))
            )
            if existing is not None:
                artifact = existing.as_dict()
                expected_worker = _normalize_versioned_bindings(
                    "worker_binding", (worker_binding,)
                )[0]
                if (
                    existing.dispatch_id != identifier
                    or existing.run_id != self.scheduler.run_id
                    or existing.candidate_path_id != candidate_path_id
                    or existing.step_id != branch["branch_step_id"]
                    or existing.lease_id != lease_id
                    or artifact["plan_binding"]
                    != self.scheduler.session.plan_binding
                    or artifact["worker_binding"] != expected_worker
                    or _canonical_json(existing.work_payload) != _canonical_json(payload)
                ):
                    raise ParallelDispatchConflictError(
                        "acquisition retry differs from the committed dispatch / "
                        "获取重试与已提交分派不一致"
                    )
                lease = ParallelPathLease(
                    candidate_path_id=candidate_path_id,
                    lease_id=lease_id,
                    worker_binding=expected_worker,
                    revision=1,
                    fencing_token=existing.fencing_token,
                    phase="acquired",
                    acquired_at=artifact["created_at"],
                    expires_at=artifact["lease_expires_at"],
                    deadline_at=artifact["deadline_at"],
                )
                return ParallelDispatchAcquisition(lease=lease, dispatch=existing)
            lease = self.scheduler.acquire(
                candidate_path_id,
                lease_id=lease_id,
                worker_binding=worker_binding,
                ttl_seconds=ttl_seconds,
                now=now,
            )
            dispatch = self.outbox.enqueue(
                run_id=self.scheduler.run_id,
                candidate_path_id=candidate_path_id,
                step_id=branch["branch_step_id"],
                plan_binding=self.scheduler.session.plan_binding,
                lease=lease,
                work_payload=payload,
                dispatch_id=identifier,
            )
            return ParallelDispatchAcquisition(lease=lease, dispatch=dispatch)

    def close_leased_branch(
        self,
        candidate_path_id: str,
        *,
        dispatch_id: str,
        lease_id: str,
        worker_binding: Mapping[str, Any],
        fencing_token: int,
        status: str,
        candidate: Any | None = None,
        evidence_records: Iterable[Mapping[str, Any]] = (),
        criterion_results: Iterable[Mapping[str, Any]] = (),
        veto_results: Iterable[Mapping[str, Any]] = (),
        elimination_reason: str | None = None,
        resource_use: BudgetUsage | Mapping[str, Any] | None = None,
        information_gain: float | None = None,
        now: float | str | None = None,
    ) -> ParallelBranchOutcome:
        """Atomically fence, consume, and close one delivered work item.

        / 原子校验栅栏、消费并关闭一条已交付工作项。
        """

        with self.scheduler.engine.events.transaction(self.scheduler.run_id):
            completion = self.outbox.prepare_completion(
                dispatch_id=dispatch_id,
                run_id=self.scheduler.run_id,
                candidate_path_id=candidate_path_id,
                lease_id=lease_id,
                fencing_token=fencing_token,
                completed_at=now,
            )
            arguments = {
                "status": status,
                "candidate": candidate,
                "evidence_records": evidence_records,
                "criterion_results": criterion_results,
                "veto_results": veto_results,
                "elimination_reason": elimination_reason,
                "resource_use": resource_use,
                "information_gain": information_gain,
            }
            if completion.exact_retry:
                # The first close and outbox completion committed together, so
                # only the session's content-idempotency check is needed here.
                # / 首次关闭与发件箱完成共同提交，此处只需会话内容幂等校验。
                return self.scheduler.session.close_branch(
                    candidate_path_id,
                    **arguments,
                )
            return self.scheduler.close_leased_branch(
                candidate_path_id,
                lease_id=lease_id,
                worker_binding=worker_binding,
                fencing_token=fencing_token,
                now=now,
                **arguments,
            )


__all__ = [
    "ParallelDispatchAcquisition",
    "ParallelDispatchClaimError",
    "ParallelDispatchCompletion",
    "ParallelDispatchConflictError",
    "ParallelDispatchCoordinator",
    "ParallelDispatchError",
    "ParallelDispatchOutbox",
    "ParallelWorkDispatch",
    "SQLITE_PARALLEL_OUTBOX_SCHEMA_VERSION",
    "SqliteParallelDispatchOutbox",
]
