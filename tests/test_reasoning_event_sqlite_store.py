"""Behavior tests for the SQLite reasoning event adapter / SQLite 推理事件适配器行为测试。"""

from __future__ import annotations

import pathlib
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(1, str(TESTS_DIR))

from reasoning_event_sqlite_store import SqliteEventStore  # noqa: E402
from reasoning_runtime import (  # noqa: E402
    EventStorePersistenceError,
    ReasoningEngine,
    WorkflowState,
)
from test_reasoning_runtime_schemas import sealed_contract  # noqa: E402


NOW = "2026-07-20T00:00:00.000Z"
HASH = "sha256:" + "a" * 64


def task_event(
    *,
    run_id: str,
    event_id: str,
    idempotency_key: str,
    task_binding_id: str,
    parent_event_id: str | None,
    timestamp: str,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "event_type": "task_received",
        "state": WorkflowState.RECEIVED,
        "payload": {
            "stage": "received",
            "task_binding": {
                "id": task_binding_id,
                "version": "1.0.0",
                "hash": HASH,
            },
        },
        "event_id": event_id,
        "idempotency_key": idempotency_key,
        "timestamp": timestamp,
        "task_id": f"task-{run_id}",
        "workflow_id": f"workflow-{run_id}",
        "attempt_id": f"attempt-{run_id}",
        "causation_id": parent_event_id,
        "parent_event_id": parent_event_id,
        "scene_id": "default",
        "risk_level": "low",
        "reasoning_depth": "direct",
        "execution_mode": "direct",
        "primary_topology": None,
        "supporting_topologies": (),
    }


def test_sqlite_store_serializes_heads_and_rejects_stale_causal_writers(tmp_path) -> None:
    path = tmp_path / "reasoning-events.db"
    first_writer = SqliteEventStore(path)
    second_writer = SqliteEventStore(path)
    first = first_writer.append(
        **task_event(
            run_id="run-shared",
            event_id="event-1",
            idempotency_key="command-1",
            task_binding_id="task-binding-1",
            parent_event_id=None,
            timestamp=NOW,
        )
    )
    stale_head = second_writer.events("run-shared")[-1]

    second = first_writer.append(
        **task_event(
            run_id="run-shared",
            event_id="event-2",
            idempotency_key="command-2",
            task_binding_id="task-binding-2",
            parent_event_id=first.event_id,
            timestamp="2026-07-20T00:00:01.000Z",
        )
    )
    with pytest.raises(EventStorePersistenceError, match="stale causal parent"):
        second_writer.append(
            **task_event(
                run_id="run-shared",
                event_id="event-3",
                idempotency_key="command-3",
                task_binding_id="task-binding-3",
                parent_event_id=stale_head.event_id,
                timestamp="2026-07-20T00:00:02.000Z",
            )
        )

    third = second_writer.append(
        **task_event(
            run_id="run-shared",
            event_id="event-3",
            idempotency_key="command-3",
            task_binding_id="task-binding-3",
            parent_event_id=second.event_id,
            timestamp="2026-07-20T00:00:02.000Z",
        )
    )
    assert [event.sequence for event in second_writer.events("run-shared")] == [1, 2, 3]
    assert third.sequence == 3


def test_sqlite_store_preserves_cross_instance_idempotency_and_rolls_back_groups(tmp_path) -> None:
    path = tmp_path / "reasoning-events.db"
    first_writer = SqliteEventStore(path)
    second_writer = SqliteEventStore(path)
    kwargs = task_event(
        run_id="run-idempotent",
        event_id="event-idempotent",
        idempotency_key="command-idempotent",
        task_binding_id="task-binding-idempotent",
        parent_event_id=None,
        timestamp=NOW,
    )
    original = first_writer.append(**kwargs)
    retry = second_writer.append(**kwargs)
    assert retry.event_id == original.event_id
    assert len(second_writer.events("run-idempotent")) == 1

    with pytest.raises(RuntimeError, match="rollback"):
        with second_writer.transaction("run-idempotent"):
            second_writer.append(
                **task_event(
                    run_id="run-idempotent",
                    event_id="event-rollback",
                    idempotency_key="command-rollback",
                    task_binding_id="task-binding-rollback",
                    parent_event_id=original.event_id,
                    timestamp="2026-07-20T00:00:01.000Z",
                )
            )
            raise RuntimeError("rollback")

    assert [event.event_id for event in first_writer.events("run-idempotent")] == [
        original.event_id
    ]


def test_sqlite_store_supports_engine_resume_and_reports_bounded_health(tmp_path) -> None:
    path = tmp_path / "reasoning-events.db"
    contract = sealed_contract()
    first_engine = ReasoningEngine(SqliteEventStore(path))
    run_id = first_engine.create_run_from_contract(contract)

    resumed_engine = ReasoningEngine(SqliteEventStore(path))
    assert resumed_engine.resume_run_from_contract(contract) == run_id
    assert resumed_engine.snapshot(run_id).state is WorkflowState.EXECUTING
    health = resumed_engine.events.health_check()
    assert health == {
        "schema_version": 2,
        "journal_mode": "wal",
        "integrity_check": "ok",
        "event_count": len(resumed_engine.events.events(run_id)),
        "run_count": 1,
        "result_count": 0,
    }
