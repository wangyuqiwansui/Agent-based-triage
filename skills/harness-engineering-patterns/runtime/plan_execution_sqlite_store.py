"""Transactional SQLite store for Plan-and-Execute / 计划并执行事务型 SQLite 存储。

One commit advances the plan head, appends contiguous internal events, persists
the checkpoint (including the idempotency snapshot), and records bounded
dispatch-outbox bindings. Tool parameters are intentionally not stored here.

/ 一次提交会推进计划头、追加连续内部事件、持久化检查点（含幂等快照），并记录
有界的分派 Outbox 绑定。本存储刻意不保存工具参数。
"""

from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator, Mapping, Sequence

try:  # Package import / 包导入
    from .plan_execution import (
        PlanExecutionSession,
        PlanStateError,
        validate_goal_contract,
        validate_workflow_checkpoint,
        validate_workflow_plan,
    )
    from .plan_execution_completion import validate_workflow_execution_result
    from .reasoning_artifacts import artifact_fingerprint
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from plan_execution import (
        PlanExecutionSession,
        PlanStateError,
        validate_goal_contract,
        validate_workflow_checkpoint,
        validate_workflow_plan,
    )
    from plan_execution_completion import validate_workflow_execution_result
    from reasoning_artifacts import artifact_fingerprint


SQLITE_PLAN_EXECUTION_SCHEMA_VERSION = 1


class PlanPersistenceError(PlanStateError):
    """Durable plan state could not be committed / 持久计划状态无法提交。"""


class StalePlanWriterError(PlanPersistenceError):
    """A writer attempted to advance a stale run head / 写入者尝试推进陈旧运行头。"""


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


class SqlitePlanExecutionStore:
    """Single-node WAL reference store / 单节点 WAL 参考存储。"""

    durable = True

    def __init__(
        self,
        path: str | Path,
        *,
        timeout_seconds: float = 5.0,
    ) -> None:
        self.path = Path(path).resolve()
        if self.path.exists() and self.path.is_dir():
            raise PlanPersistenceError("SQLite path cannot be a directory")
        if timeout_seconds <= 0:
            raise PlanPersistenceError("timeout_seconds must be positive")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = float(timeout_seconds)
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
            mode = connection.execute("PRAGMA journal_mode = WAL").fetchone()[0]
            if str(mode).lower() != "wal":
                raise PlanPersistenceError("SQLite WAL mode is required")
            connection.execute("PRAGMA synchronous = FULL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS plan_store_metadata (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    schema_version INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS goal_contracts (
                    goal_hash TEXT PRIMARY KEY,
                    goal_id TEXT NOT NULL,
                    goal_version INTEGER NOT NULL,
                    goal_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS workflow_plans (
                    plan_hash TEXT PRIMARY KEY,
                    plan_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    goal_hash TEXT NOT NULL,
                    plan_json TEXT NOT NULL,
                    FOREIGN KEY(goal_hash) REFERENCES goal_contracts(goal_hash)
                );
                CREATE TABLE IF NOT EXISTS plan_runs (
                    run_id TEXT PRIMARY KEY,
                    goal_hash TEXT NOT NULL,
                    plan_hash TEXT NOT NULL,
                    head_checkpoint_hash TEXT NOT NULL,
                    last_event_sequence INTEGER NOT NULL CHECK(last_event_sequence >= 0),
                    terminal_result_hash TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(goal_hash) REFERENCES goal_contracts(goal_hash),
                    FOREIGN KEY(plan_hash) REFERENCES workflow_plans(plan_hash)
                );
                CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                    checkpoint_hash TEXT PRIMARY KEY,
                    checkpoint_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    plan_hash TEXT NOT NULL,
                    last_event_sequence INTEGER NOT NULL CHECK(last_event_sequence >= 0),
                    checkpoint_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(run_id, checkpoint_id),
                    UNIQUE(run_id, last_event_sequence),
                    FOREIGN KEY(run_id) REFERENCES plan_runs(run_id),
                    FOREIGN KEY(plan_hash) REFERENCES workflow_plans(plan_hash)
                );
                CREATE TABLE IF NOT EXISTS plan_internal_events (
                    run_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL CHECK(sequence >= 1),
                    event_type TEXT NOT NULL,
                    event_hash TEXT NOT NULL,
                    event_json TEXT NOT NULL,
                    PRIMARY KEY(run_id, sequence),
                    FOREIGN KEY(run_id) REFERENCES plan_runs(run_id)
                );
                CREATE TABLE IF NOT EXISTS plan_dispatch_outbox (
                    outbox_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    attempt INTEGER NOT NULL CHECK(attempt >= 1),
                    action_id TEXT NOT NULL,
                    intent_hash TEXT NOT NULL,
                    payload_binding_json TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(
                        status IN ('pending', 'acknowledged', 'unknown')
                    ),
                    result_binding_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(run_id, step_id, attempt),
                    FOREIGN KEY(run_id) REFERENCES plan_runs(run_id)
                );
                CREATE TABLE IF NOT EXISTS workflow_terminal_results (
                    result_hash TEXT PRIMARY KEY,
                    result_id TEXT NOT NULL,
                    run_id TEXT NOT NULL UNIQUE,
                    result_json TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES plan_runs(run_id)
                );
                CREATE INDEX IF NOT EXISTS idx_plan_events_run
                    ON plan_internal_events(run_id, sequence);
                CREATE INDEX IF NOT EXISTS idx_plan_outbox_status
                    ON plan_dispatch_outbox(run_id, status, attempt);
                """
            )
            row = connection.execute(
                "SELECT schema_version FROM plan_store_metadata WHERE singleton = 1"
            ).fetchone()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO plan_store_metadata(singleton, schema_version)
                    VALUES (1, ?)
                    """,
                    (SQLITE_PLAN_EXECUTION_SCHEMA_VERSION,),
                )
            elif int(row["schema_version"]) != SQLITE_PLAN_EXECUTION_SCHEMA_VERSION:
                raise PlanPersistenceError(
                    "unsupported plan-store schema version / "
                    "不支持的计划存储 Schema 版本"
                )
        finally:
            connection.close()

    def run_head(self, run_id: str) -> Mapping[str, Any] | None:
        """Return the current optimistic-concurrency head / 返回当前乐观并发头。"""

        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT head_checkpoint_hash, last_event_sequence,
                       plan_hash, terminal_result_hash
                FROM plan_runs WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
            return None if row is None else dict(row)
        finally:
            connection.close()

    def initialize_run(
        self,
        goal_contract: Mapping[str, Any],
        session: PlanExecutionSession,
        *,
        checkpoint_id: str,
        created_at: str | None = None,
    ) -> Mapping[str, Any]:
        """Create a run with its first atomic checkpoint / 创建含首个原子检查点的运行。"""

        return self.commit_session(
            session,
            checkpoint_id=checkpoint_id,
            expected_head_hash=None,
            goal_contract=goal_contract,
            created_at=created_at,
        )

    def commit_session(
        self,
        session: PlanExecutionSession,
        *,
        checkpoint_id: str,
        expected_head_hash: str | None,
        goal_contract: Mapping[str, Any] | None = None,
        outbox_items: Sequence[Mapping[str, Any]] = (),
        outbox_updates: Sequence[Mapping[str, Any]] = (),
        created_at: str | None = None,
    ) -> Mapping[str, Any]:
        """Atomically advance checkpoint, events, idempotency snapshot and outbox.

        / 原子推进检查点、事件、幂等快照与 Outbox。
        """

        validate_workflow_plan(session.plan)
        checkpoint = session.checkpoint(
            checkpoint_id=checkpoint_id,
            created_at=created_at,
        )
        validate_workflow_checkpoint(checkpoint)
        if goal_contract is not None:
            validate_goal_contract(goal_contract)
            if session.plan["goal_binding"] != {
                "goal_id": goal_contract["goal_id"],
                "version": goal_contract["version"],
                "hash": goal_contract["goal_contract_hash"],
            }:
                raise PlanPersistenceError(
                    "goal does not bind the session plan / 目标未绑定会话计划"
                )

        with self._transaction() as connection:
            row = connection.execute(
                "SELECT * FROM plan_runs WHERE run_id = ?",
                (session.run_id,),
            ).fetchone()
            if row is None:
                if expected_head_hash is not None or goal_contract is None:
                    raise StalePlanWriterError(
                        "new run requires a goal and no expected head / "
                        "新运行必须提供目标且不得提供预期头"
                    )
                current_sequence = 0
                goal_hash = str(goal_contract["goal_contract_hash"])
                connection.execute(
                    """
                    INSERT OR IGNORE INTO goal_contracts(
                        goal_hash, goal_id, goal_version, goal_json
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        goal_hash,
                        goal_contract["goal_id"],
                        goal_contract["version"],
                        _canonical_json(goal_contract),
                    ),
                )
                self._insert_plan(connection, session.plan, goal_hash)
                connection.execute(
                    """
                    INSERT INTO plan_runs(
                        run_id, goal_hash, plan_hash, head_checkpoint_hash,
                        last_event_sequence, terminal_result_hash,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 0, NULL, ?, ?)
                    """,
                    (
                        session.run_id,
                        goal_hash,
                        session.plan["plan_hash"],
                        checkpoint["checkpoint_hash"],
                        checkpoint["created_at"],
                        checkpoint["created_at"],
                    ),
                )
            else:
                if expected_head_hash is None:
                    raise StalePlanWriterError(
                        "existing run requires expected_head_hash / "
                        "既有运行必须提供 expected_head_hash"
                    )
                if row["head_checkpoint_hash"] != expected_head_hash:
                    raise StalePlanWriterError(
                        "stale checkpoint head / 陈旧检查点头"
                    )
                if row["terminal_result_hash"] is not None:
                    raise PlanPersistenceError(
                        "terminal run cannot advance / 终态运行不能继续推进"
                    )
                current_sequence = int(row["last_event_sequence"])
                goal_hash = str(row["goal_hash"])
                self._insert_plan(connection, session.plan, goal_hash)

            new_events = sorted(
                (
                    deepcopy(dict(event))
                    for event in session.events
                    if int(event["sequence"]) > current_sequence
                ),
                key=lambda event: int(event["sequence"]),
            )
            expected_sequences = list(
                range(current_sequence + 1, checkpoint["last_event_sequence"] + 1)
            )
            actual_sequences = [int(event["sequence"]) for event in new_events]
            if actual_sequences != expected_sequences:
                raise PlanPersistenceError(
                    "session event suffix is not contiguous / "
                    "会话事件后缀不连续"
                )
            for event in new_events:
                if event["run_id"] != session.run_id:
                    raise PlanPersistenceError(
                        "event run binding mismatch / 事件运行绑定不一致"
                    )
                event_hash = artifact_fingerprint(event)
                connection.execute(
                    """
                    INSERT INTO plan_internal_events(
                        run_id, sequence, event_type, event_hash, event_json
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        session.run_id,
                        event["sequence"],
                        event["event_type"],
                        event_hash,
                        _canonical_json(event),
                    ),
                )

            self._insert_outbox_items(
                connection,
                session.run_id,
                outbox_items,
                checkpoint["created_at"],
            )
            self._apply_outbox_updates(
                connection,
                session.run_id,
                outbox_updates,
                checkpoint["created_at"],
            )
            connection.execute(
                """
                INSERT INTO workflow_checkpoints(
                    checkpoint_hash, checkpoint_id, run_id, plan_hash,
                    last_event_sequence, checkpoint_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checkpoint["checkpoint_hash"],
                    checkpoint["checkpoint_id"],
                    session.run_id,
                    session.plan["plan_hash"],
                    checkpoint["last_event_sequence"],
                    _canonical_json(checkpoint),
                    checkpoint["created_at"],
                ),
            )
            connection.execute(
                """
                UPDATE plan_runs
                SET plan_hash = ?,
                    head_checkpoint_hash = ?,
                    last_event_sequence = ?,
                    updated_at = ?
                WHERE run_id = ?
                """,
                (
                    session.plan["plan_hash"],
                    checkpoint["checkpoint_hash"],
                    checkpoint["last_event_sequence"],
                    checkpoint["created_at"],
                    session.run_id,
                ),
            )
        return deepcopy(checkpoint)

    @staticmethod
    def _insert_plan(
        connection: sqlite3.Connection,
        plan: Mapping[str, Any],
        goal_hash: str,
    ) -> None:
        if plan["goal_binding"]["hash"] != goal_hash:
            raise PlanPersistenceError(
                "plan goal hash differs from run goal / 计划目标哈希与运行目标不同"
            )
        connection.execute(
            """
            INSERT OR IGNORE INTO workflow_plans(
                plan_hash, plan_id, revision, goal_hash, plan_json
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                plan["plan_hash"],
                plan["plan_id"],
                plan["revision"],
                goal_hash,
                _canonical_json(plan),
            ),
        )

    @staticmethod
    def _insert_outbox_items(
        connection: sqlite3.Connection,
        run_id: str,
        items: Sequence[Mapping[str, Any]],
        timestamp: str,
    ) -> None:
        for source in items:
            item = dict(source)
            required = {
                "outbox_id",
                "step_id",
                "attempt",
                "action_id",
                "intent_hash",
                "payload_binding",
            }
            if set(item) != required or not isinstance(
                item.get("payload_binding"), Mapping
            ):
                raise PlanPersistenceError(
                    "invalid outbox item / 非法 Outbox 项"
                )
            connection.execute(
                """
                INSERT INTO plan_dispatch_outbox(
                    outbox_id, run_id, step_id, attempt, action_id,
                    intent_hash, payload_binding_json, status,
                    result_binding_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', NULL, ?, ?)
                """,
                (
                    item["outbox_id"],
                    run_id,
                    item["step_id"],
                    item["attempt"],
                    item["action_id"],
                    item["intent_hash"],
                    _canonical_json(item["payload_binding"]),
                    timestamp,
                    timestamp,
                ),
            )

    @staticmethod
    def _apply_outbox_updates(
        connection: sqlite3.Connection,
        run_id: str,
        updates: Sequence[Mapping[str, Any]],
        timestamp: str,
    ) -> None:
        for source in updates:
            update = dict(source)
            if set(update) != {"outbox_id", "status", "result_binding"}:
                raise PlanPersistenceError(
                    "invalid outbox update / 非法 Outbox 更新"
                )
            if update["status"] not in {"acknowledged", "unknown"}:
                raise PlanPersistenceError(
                    "outbox update status is invalid / Outbox 更新状态非法"
                )
            binding = update["result_binding"]
            if binding is not None and not isinstance(binding, Mapping):
                raise PlanPersistenceError(
                    "outbox result binding must be a mapping / "
                    "Outbox 结果绑定必须是对象"
                )
            cursor = connection.execute(
                """
                UPDATE plan_dispatch_outbox
                SET status = ?, result_binding_json = ?, updated_at = ?
                WHERE outbox_id = ? AND run_id = ?
                  AND status IN ('pending', 'unknown')
                """,
                (
                    update["status"],
                    None if binding is None else _canonical_json(binding),
                    timestamp,
                    update["outbox_id"],
                    run_id,
                ),
            )
            if cursor.rowcount != 1:
                raise PlanPersistenceError(
                    "outbox update did not match one open item / "
                    "Outbox 更新未匹配唯一开放项"
                )

    def load_run(
        self,
        run_id: str,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], str]:
        """Load goal, current plan, checkpoint and head hash / 加载目标、当前计划、检查点与头哈希。"""

        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT r.head_checkpoint_hash, g.goal_json, p.plan_json,
                       c.checkpoint_json
                FROM plan_runs r
                JOIN goal_contracts g ON g.goal_hash = r.goal_hash
                JOIN workflow_plans p ON p.plan_hash = r.plan_hash
                JOIN workflow_checkpoints c
                  ON c.checkpoint_hash = r.head_checkpoint_hash
                WHERE r.run_id = ?
                """,
                (run_id,),
            ).fetchone()
            if row is None:
                raise PlanPersistenceError(
                    f"unknown run_id {run_id} / 未知 run_id：{run_id}"
                )
            goal = json.loads(row["goal_json"])
            plan = json.loads(row["plan_json"])
            checkpoint = json.loads(row["checkpoint_json"])
            validate_goal_contract(goal)
            validate_workflow_plan(plan)
            validate_workflow_checkpoint(checkpoint)
            return goal, plan, checkpoint, str(row["head_checkpoint_hash"])
        finally:
            connection.close()

    def restore_session(
        self,
        run_id: str,
    ) -> tuple[dict[str, Any], PlanExecutionSession, str]:
        """Restore with interrupted-write UNKNOWN semantics / 按中断写 UNKNOWN 语义恢复。"""

        goal, plan, checkpoint, head_hash = self.load_run(run_id)
        return goal, PlanExecutionSession.from_checkpoint(plan, checkpoint), head_hash

    def outbox_items(
        self,
        run_id: str,
        *,
        statuses: Sequence[str] = ("pending", "unknown"),
    ) -> tuple[dict[str, Any], ...]:
        """Return bounded reconciliation work; never raw parameters.

        / 返回有界对账工作，绝不返回原始参数。
        """

        allowed = {"pending", "acknowledged", "unknown"}
        if not statuses or any(status not in allowed for status in statuses):
            raise PlanPersistenceError("invalid outbox status filter")
        placeholders = ",".join("?" for _ in statuses)
        connection = self._connect()
        try:
            rows = connection.execute(
                f"""
                SELECT * FROM plan_dispatch_outbox
                WHERE run_id = ? AND status IN ({placeholders})
                ORDER BY attempt, outbox_id
                """,
                (run_id, *statuses),
            ).fetchall()
            return tuple(
                {
                    "outbox_id": row["outbox_id"],
                    "run_id": row["run_id"],
                    "step_id": row["step_id"],
                    "attempt": row["attempt"],
                    "action_id": row["action_id"],
                    "intent_hash": row["intent_hash"],
                    "payload_binding": json.loads(row["payload_binding_json"]),
                    "status": row["status"],
                    "result_binding": (
                        None
                        if row["result_binding_json"] is None
                        else json.loads(row["result_binding_json"])
                    ),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
                for row in rows
            )
        finally:
            connection.close()

    def save_terminal_result(
        self,
        result: Mapping[str, Any],
        *,
        expected_head_hash: str,
    ) -> Mapping[str, Any]:
        """Persist the final artifact exactly once / 精确一次持久化终态制品。"""

        validate_workflow_execution_result(result)
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT * FROM plan_runs WHERE run_id = ?",
                (result["run_id"],),
            ).fetchone()
            if row is None or row["head_checkpoint_hash"] != expected_head_hash:
                raise StalePlanWriterError(
                    "terminal result used a stale run head / "
                    "终态结果使用了陈旧运行头"
                )
            if (
                result["goal_binding"]["hash"] != row["goal_hash"]
                or result["plan_binding"]["hash"] != row["plan_hash"]
            ):
                raise PlanPersistenceError(
                    "terminal result bindings differ from the current run / "
                    "终态结果绑定与当前运行不一致"
                )
            if row["terminal_result_hash"] is not None:
                if row["terminal_result_hash"] == result["result_hash"]:
                    return deepcopy(dict(result))
                raise PlanPersistenceError(
                    "terminal result is immutable / 终态结果不可变"
                )
            connection.execute(
                """
                INSERT INTO workflow_terminal_results(
                    result_hash, result_id, run_id, result_json, completed_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    result["result_hash"],
                    result["result_id"],
                    result["run_id"],
                    _canonical_json(result),
                    result["completed_at"],
                ),
            )
            connection.execute(
                """
                UPDATE plan_runs
                SET terminal_result_hash = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (
                    result["result_hash"],
                    result["completed_at"],
                    result["run_id"],
                ),
            )
        return deepcopy(dict(result))

    def events(self, run_id: str) -> tuple[dict[str, Any], ...]:
        """Return persisted internal events in order / 按序返回已持久化内部事件。"""

        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT event_json FROM plan_internal_events
                WHERE run_id = ? ORDER BY sequence
                """,
                (run_id,),
            ).fetchall()
            return tuple(json.loads(row["event_json"]) for row in rows)
        finally:
            connection.close()

    def health_check(self) -> Mapping[str, Any]:
        """Return bounded operational health / 返回有界运行健康状态。"""

        connection = self._connect()
        try:
            return {
                "schema_version": SQLITE_PLAN_EXECUTION_SCHEMA_VERSION,
                "journal_mode": str(
                    connection.execute("PRAGMA journal_mode").fetchone()[0]
                ).lower(),
                "integrity_check": str(
                    connection.execute("PRAGMA integrity_check").fetchone()[0]
                ),
                "run_count": int(
                    connection.execute("SELECT COUNT(*) FROM plan_runs").fetchone()[0]
                ),
                "open_outbox_count": int(
                    connection.execute(
                        """
                        SELECT COUNT(*) FROM plan_dispatch_outbox
                        WHERE status IN ('pending', 'unknown')
                        """
                    ).fetchone()[0]
                ),
            }
        finally:
            connection.close()


__all__ = [
    "PlanPersistenceError",
    "SQLITE_PLAN_EXECUTION_SCHEMA_VERSION",
    "SqlitePlanExecutionStore",
    "StalePlanWriterError",
]
