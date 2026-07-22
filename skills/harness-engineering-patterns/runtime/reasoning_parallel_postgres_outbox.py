"""PostgreSQL parallel-worker transactional outbox / PostgreSQL 并行工作者事务发件箱。

Queue consumers claim rows with ``FOR UPDATE SKIP LOCKED`` and expiring
delivery tokens. Enqueue and completion methods require the matching active
``PostgresEventStore`` transaction, keeping lease events, dispatch rows, branch
terminals, and completion state atomic. / 队列消费者使用 ``FOR UPDATE SKIP
LOCKED`` 与可过期交付令牌领取记录。入队与完成方法要求匹配的
``PostgresEventStore`` 活动事务，使租约事件、分派记录、分支终态和完成状态保持原子。
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping
import uuid

try:  # Optional deployment dependency / 可选部署依赖
    import psycopg
    from psycopg import sql
except ImportError:  # pragma: no cover
    psycopg = None
    sql = None

try:  # Package import / 包导入
    from .reasoning_event_postgres_store import PostgresEventStore
    from .reasoning_parallel_outbox import (
        ParallelDispatchClaimError,
        ParallelDispatchCompletion,
        ParallelDispatchConflictError,
        ParallelDispatchError,
        ParallelWorkDispatch,
    )
    from .reasoning_parallel_scheduler import ParallelPathLease
    from .reasoning_runtime import (
        _assert_no_private_reasoning,
        _canonical_json,
        _iso_utc,
        _normalize_versioned_bindings,
        _validate_identifier,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_event_postgres_store import PostgresEventStore
    from reasoning_parallel_outbox import (
        ParallelDispatchClaimError,
        ParallelDispatchCompletion,
        ParallelDispatchConflictError,
        ParallelDispatchError,
        ParallelWorkDispatch,
    )
    from reasoning_parallel_scheduler import ParallelPathLease
    from reasoning_runtime import (
        _assert_no_private_reasoning,
        _canonical_json,
        _iso_utc,
        _normalize_versioned_bindings,
        _validate_identifier,
    )


POSTGRES_PARALLEL_OUTBOX_SCHEMA_VERSION = 1
_OUTBOX_STATUSES = {
    "pending",
    "claimed",
    "delivered",
    "completed",
    "superseded",
    "dead_lettered",
}


class PostgresParallelDispatchOutbox:
    """Persist fenced public worker commands in PostgreSQL.

    / 在 PostgreSQL 中持久化带栅栏的公开工作者命令。
    """

    STORAGE_SCHEMA_VERSION = "1.0.0"

    def __init__(self, event_store: PostgresEventStore) -> None:
        if not isinstance(event_store, PostgresEventStore):
            raise TypeError(
                "event_store must be PostgresEventStore / "
                "event_store 必须为 PostgresEventStore"
            )
        self.event_store = event_store
        self._initialize()

    def _table(self, name: str) -> Any:
        return self.event_store._table(name)

    @staticmethod
    def _hash(value: Mapping[str, Any]) -> str:
        encoded = _canonical_json(dict(value)).encode("utf-8")
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

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

    def _initialize(self) -> None:
        connection = None
        try:
            connection = self.event_store._connect()
            with connection.transaction():
                self.event_store._set_transaction_guards(connection)
                connection.execute(
                    "SELECT pg_advisory_xact_lock(%s)",
                    (
                        self.event_store._advisory_key(
                            f"outbox-schema-init:{self.event_store.schema}"
                        ),
                    ),
                )
                connection.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {} (
                            singleton SMALLINT PRIMARY KEY CHECK (singleton = 1),
                            schema_version INTEGER NOT NULL
                        )
                        """
                    ).format(self._table("parallel_dispatch_metadata"))
                )
                version_row = connection.execute(
                    sql.SQL(
                        "SELECT schema_version FROM {} WHERE singleton = 1 FOR UPDATE"
                    ).format(self._table("parallel_dispatch_metadata"))
                ).fetchone()
                if version_row is None:
                    connection.execute(
                        sql.SQL(
                            "INSERT INTO {} (singleton, schema_version) VALUES (1, %s)"
                        ).format(self._table("parallel_dispatch_metadata")),
                        (POSTGRES_PARALLEL_OUTBOX_SCHEMA_VERSION,),
                    )
                elif int(version_row["schema_version"]) != POSTGRES_PARALLEL_OUTBOX_SCHEMA_VERSION:
                    raise ParallelDispatchError(
                        "unsupported PostgreSQL outbox schema version / "
                        "不支持的 PostgreSQL 发件箱 Schema 版本"
                    )
                connection.execute(
                    sql.SQL(
                        """
                        CREATE TABLE IF NOT EXISTS {} (
                            dispatch_id TEXT PRIMARY KEY,
                            run_id TEXT NOT NULL,
                            candidate_path_id TEXT NOT NULL,
                            step_id TEXT NOT NULL,
                            lease_id TEXT NOT NULL UNIQUE,
                            fencing_token BIGINT NOT NULL CHECK (fencing_token > 0),
                            lease_expires_epoch DOUBLE PRECISION NOT NULL,
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
                            claim_expires_epoch DOUBLE PRECISION,
                            delivered_at TEXT,
                            completed_at TEXT,
                            last_error TEXT,
                            created_at TEXT NOT NULL,
                            created_epoch DOUBLE PRECISION NOT NULL,
                            dispatch_hash TEXT NOT NULL,
                            dispatch_json TEXT NOT NULL,
                            UNIQUE (run_id, candidate_path_id, fencing_token)
                        )
                        """
                    ).format(self._table("parallel_dispatch_outbox"))
                )
                connection.execute(
                    sql.SQL(
                        "CREATE INDEX IF NOT EXISTS {} ON {} "
                        "(status, created_epoch, dispatch_id)"
                    ).format(
                        sql.Identifier("parallel_dispatch_delivery_order"),
                        self._table("parallel_dispatch_outbox"),
                    )
                )
                self._verify_schema(connection)
        except ParallelDispatchError:
            raise
        except Exception as exc:
            if psycopg is not None and isinstance(exc, psycopg.Error):
                raise ParallelDispatchError(
                    "PostgreSQL parallel outbox initialization failed / "
                    "PostgreSQL 并行发件箱初始化失败"
                ) from exc
            raise
        finally:
            if connection is not None:
                connection.close()

    def _verify_schema(self, connection: Any) -> None:
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
        rows = connection.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = %s AND table_name = 'parallel_dispatch_outbox'",
            (self.event_store.schema,),
        ).fetchall()
        actual = {str(row["column_name"]) for row in rows}
        if actual != expected:
            raise ParallelDispatchError(
                "PostgreSQL parallel outbox differs from the contract / "
                "PostgreSQL 并行发件箱与契约不一致"
            )

    def _row_to_dispatch(self, row: Mapping[str, Any]) -> ParallelWorkDispatch:
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
                "invalid PostgreSQL parallel dispatch record / "
                "PostgreSQL 并行分派记录无效: " + str(exc)
            ) from exc

    def find_acquisition(
        self,
        dispatch_id: str,
        lease_id: str,
    ) -> ParallelWorkDispatch | None:
        active = self.event_store._active_context()
        if active is None:
            raise ParallelDispatchError(
                "acquisition lookup requires an active event transaction / "
                "获取查找要求活动事件事务"
            )
        row = active.connection.execute(
            sql.SQL(
                "SELECT * FROM {} WHERE dispatch_id = %s OR lease_id = %s"
            ).format(self._table("parallel_dispatch_outbox")),
            (dispatch_id, lease_id),
        ).fetchone()
        return None if row is None else self._row_to_dispatch(row)

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
        existing_rows = active.connection.execute(
            sql.SQL(
                "SELECT * FROM {} WHERE dispatch_id = %s OR lease_id = %s OR "
                "(run_id = %s AND candidate_path_id = %s AND fencing_token = %s) "
                "FOR UPDATE"
            ).format(self._table("parallel_dispatch_outbox")),
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
        active.connection.execute(
            sql.SQL(
                "UPDATE {} SET status = 'superseded', delivery_token = NULL, "
                "delivery_owner = NULL, claimed_at = NULL, claim_expires_at = NULL, "
                "claim_expires_epoch = NULL, last_error = %s WHERE run_id = %s "
                "AND candidate_path_id = %s AND fencing_token < %s "
                "AND status NOT IN ('completed', 'superseded')"
            ).format(self._table("parallel_dispatch_outbox")),
            (
                "superseded by a newer fencing token / 被更新的栅栏令牌取代",
                run_id,
                candidate_path_id,
                lease.fencing_token,
            ),
        )
        try:
            row = active.connection.execute(
                sql.SQL(
                    """
                    INSERT INTO {} (
                        dispatch_id, run_id, candidate_path_id, step_id, lease_id,
                        fencing_token, lease_expires_epoch, status, created_at,
                        created_epoch, dispatch_hash, dispatch_json
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s, %s, %s)
                    RETURNING *
                    """
                ).format(self._table("parallel_dispatch_outbox")),
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
            ).fetchone()
        except Exception as exc:
            if psycopg is not None and isinstance(exc, psycopg.errors.UniqueViolation):
                raise ParallelDispatchConflictError(
                    "dispatch uniqueness conflict / 分派唯一性冲突"
                ) from exc
            raise
        return self._row_to_dispatch(row)

    def get(self, dispatch_id: str) -> ParallelWorkDispatch | None:
        _validate_identifier("dispatch_id", dispatch_id)
        connection = None
        try:
            connection = self.event_store._connect()
            with connection.transaction():
                row = connection.execute(
                    sql.SQL("SELECT * FROM {} WHERE dispatch_id = %s").format(
                        self._table("parallel_dispatch_outbox")
                    ),
                    (dispatch_id,),
                ).fetchone()
                return None if row is None else self._row_to_dispatch(row)
        except ParallelDispatchError:
            raise
        except Exception as exc:
            if psycopg is not None and isinstance(exc, psycopg.Error):
                raise ParallelDispatchError(
                    "PostgreSQL parallel dispatch read failed / "
                    "PostgreSQL 并行分派读取失败"
                ) from exc
            raise
        finally:
            if connection is not None:
                connection.close()

    def claim_batch(
        self,
        *,
        delivery_owner: str,
        limit: int,
        claim_ttl_seconds: float,
        now: float | str | None = None,
    ) -> tuple[ParallelWorkDispatch, ...]:
        _validate_identifier("delivery_owner", delivery_owner)
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise ValueError("limit must be within 1..1000 / limit 必须位于 1..1000")
        ttl = self._positive_seconds("claim_ttl_seconds", claim_ttl_seconds)
        observed_at, observed_epoch = _iso_utc(now)
        expires_at, expires_epoch = _iso_utc(observed_epoch + ttl)
        connection = None
        try:
            connection = self.event_store._connect()
            with connection.transaction():
                self.event_store._set_transaction_guards(connection)
                connection.execute(
                    sql.SQL(
                        "UPDATE {} SET status = 'superseded', delivery_token = NULL, "
                        "delivery_owner = NULL, claimed_at = NULL, claim_expires_at = NULL, "
                        "claim_expires_epoch = NULL, last_error = %s "
                        "WHERE status IN ('pending', 'claimed') AND lease_expires_epoch <= %s"
                    ).format(self._table("parallel_dispatch_outbox")),
                    (
                        "worker lease expired before delivery / 工作者租约在交付前过期",
                        observed_epoch,
                    ),
                )
                rows = connection.execute(
                    sql.SQL(
                        "SELECT dispatch_id FROM {} WHERE status = 'pending' OR "
                        "(status = 'claimed' AND claim_expires_epoch <= %s) "
                        "ORDER BY created_epoch, dispatch_id LIMIT %s "
                        "FOR UPDATE SKIP LOCKED"
                    ).format(self._table("parallel_dispatch_outbox")),
                    (observed_epoch, limit),
                ).fetchall()
                claimed: list[ParallelWorkDispatch] = []
                for selected in rows:
                    delivery_token = f"delivery-{uuid.uuid4().hex}"
                    row = connection.execute(
                        sql.SQL(
                            "UPDATE {} SET status = 'claimed', "
                            "delivery_attempt_count = delivery_attempt_count + 1, "
                            "delivery_token = %s, delivery_owner = %s, claimed_at = %s, "
                            "claim_expires_at = %s, claim_expires_epoch = %s, "
                            "last_error = NULL WHERE dispatch_id = %s RETURNING *"
                        ).format(self._table("parallel_dispatch_outbox")),
                        (
                            delivery_token,
                            delivery_owner,
                            observed_at,
                            expires_at,
                            expires_epoch,
                            selected["dispatch_id"],
                        ),
                    ).fetchone()
                    claimed.append(self._row_to_dispatch(row))
                return tuple(claimed)
        except ParallelDispatchError:
            raise
        except Exception as exc:
            if psycopg is not None and isinstance(exc, psycopg.Error):
                raise ParallelDispatchError(
                    "PostgreSQL parallel dispatch claim failed / "
                    "PostgreSQL 并行分派领取失败"
                ) from exc
            raise
        finally:
            if connection is not None:
                connection.close()

    def acknowledge_delivery(
        self,
        dispatch_id: str,
        *,
        delivery_token: str,
        delivery_owner: str,
        delivered_at: float | str | None = None,
    ) -> ParallelWorkDispatch:
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
        connection = None
        try:
            connection = self.event_store._connect()
            with connection.transaction():
                self.event_store._set_transaction_guards(connection)
                current_row = connection.execute(
                    sql.SQL("SELECT * FROM {} WHERE dispatch_id = %s FOR UPDATE").format(
                        self._table("parallel_dispatch_outbox")
                    ),
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
                        return current
                if next_status == "delivered":
                    row = connection.execute(
                        sql.SQL(
                            "UPDATE {} SET status = 'delivered', "
                            "delivered_at = COALESCE(%s, delivered_at), last_error = NULL "
                            "WHERE dispatch_id = %s AND status = 'claimed' "
                            "AND delivery_token = %s AND delivery_owner = %s RETURNING *"
                        ).format(self._table("parallel_dispatch_outbox")),
                        (timestamp, dispatch_id, delivery_token, delivery_owner),
                    ).fetchone()
                else:
                    row = connection.execute(
                        sql.SQL(
                            "UPDATE {} SET status = %s, delivery_token = NULL, "
                            "delivery_owner = NULL, claimed_at = NULL, "
                            "claim_expires_at = NULL, claim_expires_epoch = NULL, "
                            "last_error = %s WHERE dispatch_id = %s AND status = 'claimed' "
                            "AND delivery_token = %s AND delivery_owner = %s RETURNING *"
                        ).format(self._table("parallel_dispatch_outbox")),
                        (
                            next_status,
                            error,
                            dispatch_id,
                            delivery_token,
                            delivery_owner,
                        ),
                    ).fetchone()
                if row is None:
                    raise ParallelDispatchClaimError(
                        "delivery token is stale or not current / "
                        "交付令牌陈旧或不是当前令牌"
                    )
                return self._row_to_dispatch(row)
        except ParallelDispatchError:
            raise
        except Exception as exc:
            if psycopg is not None and isinstance(exc, psycopg.Error):
                raise ParallelDispatchError(
                    "PostgreSQL parallel delivery update failed / "
                    "PostgreSQL 并行交付更新失败"
                ) from exc
            raise
        finally:
            if connection is not None:
                connection.close()

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
        active = self.event_store._active_context()
        if active is None or active.run_id != run_id:
            raise ParallelDispatchError(
                "completion requires the matching active event transaction / "
                "完成要求匹配的活动事件事务"
            )
        timestamp, _ = _iso_utc(completed_at)
        row = active.connection.execute(
            sql.SQL("SELECT * FROM {} WHERE dispatch_id = %s FOR UPDATE").format(
                self._table("parallel_dispatch_outbox")
            ),
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
        completed_row = active.connection.execute(
            sql.SQL(
                "UPDATE {} SET status = 'completed', completed_at = %s, "
                "delivery_token = NULL, delivery_owner = NULL, claimed_at = NULL, "
                "claim_expires_at = NULL, claim_expires_epoch = NULL "
                "WHERE dispatch_id = %s RETURNING *"
            ).format(self._table("parallel_dispatch_outbox")),
            (timestamp, dispatch_id),
        ).fetchone()
        return ParallelDispatchCompletion(
            dispatch=self._row_to_dispatch(completed_row),
            exact_retry=False,
        )

    def health_check(self) -> dict[str, Any]:
        connection = None
        try:
            connection = self.event_store._connect()
            with connection.transaction():
                counts = {status: 0 for status in sorted(_OUTBOX_STATUSES)}
                rows = connection.execute(
                    sql.SQL(
                        "SELECT status, COUNT(*) AS count FROM {} GROUP BY status"
                    ).format(self._table("parallel_dispatch_outbox"))
                ).fetchall()
                for row in rows:
                    counts[str(row["status"])] = int(row["count"])
                attempt_count = connection.execute(
                    sql.SQL(
                        "SELECT COALESCE(SUM(delivery_attempt_count), 0) AS count FROM {}"
                    ).format(self._table("parallel_dispatch_outbox"))
                ).fetchone()["count"]
                return {
                    "schema_version": POSTGRES_PARALLEL_OUTBOX_SCHEMA_VERSION,
                    "schema": self.event_store.schema,
                    "total_count": sum(counts.values()),
                    "delivery_attempt_count": int(attempt_count),
                    "status_counts": counts,
                }
        except Exception as exc:
            if psycopg is not None and isinstance(exc, psycopg.Error):
                raise ParallelDispatchError(
                    "PostgreSQL parallel outbox health check failed / "
                    "PostgreSQL 并行发件箱健康检查失败"
                ) from exc
            raise
        finally:
            if connection is not None:
                connection.close()


__all__ = [
    "POSTGRES_PARALLEL_OUTBOX_SCHEMA_VERSION",
    "PostgresParallelDispatchOutbox",
]
