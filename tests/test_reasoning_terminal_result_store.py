"""Durable terminal-result behavior / 持久化终态结果行为测试。"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(1, str(TESTS_DIR))

from reasoning_event_sqlite_store import SqliteEventStore  # noqa: E402
from reasoning_artifacts import build_artifact  # noqa: E402
from reasoning_runtime import (  # noqa: E402
    DuplicateEventConflictError,
    EventStore,
    EventStorePersistenceError,
    JsonlEventStore,
    ReasoningEngine,
    WorkflowState,
)
from test_reasoning_runtime_schemas import NOW, sealed_contract  # noqa: E402


def result_fields(*, content_ref: str = "result-store:failed") -> dict[str, object]:
    return {
        "claims": [],
        "final_decision": {"state": "unknown"},
        "output": {
            "format": "json",
            "content": {"state": "unknown"},
            "content_ref": content_ref,
        },
        "field_provenance": [
            {
                "field_path": "/output/content",
                "source_type": "system",
                "source_ref": "failure-controller",
                "value_state": "unknown",
            }
        ],
        "created_at": NOW,
    }


def build_failed_result(engine: ReasoningEngine, contract: dict[str, object]):
    run_id = engine.create_run_from_contract(contract)
    engine.transition(
        run_id,
        WorkflowState.FAILED,
        reason="injected terminal persistence test / 注入终态持久化测试",
    )
    return run_id, engine.build_result(run_id, **result_fields())


def test_jsonl_terminal_result_reopens_resumes_and_retries_exactly(tmp_path) -> None:
    path = tmp_path / "reasoning-events.jsonl"
    contract = sealed_contract()
    first_engine = ReasoningEngine(JsonlEventStore(path))
    run_id, first = build_failed_result(first_engine, contract)
    event_count = len(first_engine.events.events(run_id))
    assert first_engine.events.results_path.exists()

    reopened = ReasoningEngine(JsonlEventStore(path))
    assert reopened.resume_run_from_contract(contract) == run_id
    retry = reopened.build_result(run_id, **result_fields())

    assert retry == first
    assert reopened.events.load_terminal_result(run_id) == first
    assert len(reopened.events.events(run_id)) == event_count
    with pytest.raises(DuplicateEventConflictError, match="different sealed result"):
        reopened.build_result(
            run_id,
            **result_fields(content_ref="result-store:conflicting"),
        )


def test_jsonl_terminal_result_sidecar_rejects_tampering(tmp_path) -> None:
    path = tmp_path / "reasoning-events.jsonl"
    engine = ReasoningEngine(JsonlEventStore(path))
    run_id, _ = build_failed_result(engine, sealed_contract())
    sidecar = engine.events.results_path
    record = json.loads(sidecar.read_text(encoding="utf-8"))
    record["results"][run_id]["output"]["content_ref"] = "tampered"
    sidecar.write_text(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )

    with pytest.raises(EventStorePersistenceError, match="sidecar"):
        JsonlEventStore(path)


def test_jsonl_terminal_result_commit_failure_rolls_back_memory(tmp_path, monkeypatch) -> None:
    path = tmp_path / "reasoning-events.jsonl"
    store = JsonlEventStore(path)
    engine = ReasoningEngine(store)
    contract = sealed_contract()
    run_id = engine.create_run_from_contract(contract)
    engine.transition(run_id, WorkflowState.FAILED, reason="injected failure")

    def fail_commit() -> None:
        raise EventStorePersistenceError("injected result commit failure")

    monkeypatch.setattr(store, "_persist_terminal_results", fail_commit)
    with pytest.raises(EventStorePersistenceError, match="injected result commit"):
        engine.build_result(run_id, **result_fields())

    assert store.load_terminal_result(run_id) is None
    assert not store.results_path.exists()


def test_sqlite_terminal_result_reopens_resumes_and_serializes_conflicts(tmp_path) -> None:
    path = tmp_path / "reasoning-events.db"
    contract = sealed_contract()
    first_engine = ReasoningEngine(SqliteEventStore(path))
    run_id, first = build_failed_result(first_engine, contract)

    reopened = ReasoningEngine(SqliteEventStore(path))
    assert reopened.resume_run_from_contract(contract) == run_id
    assert reopened.build_result(run_id, **result_fields()) == first
    assert reopened.events.health_check()["result_count"] == 1

    competing = ReasoningEngine(SqliteEventStore(path))
    competing.resume_run_from_contract(contract)
    with pytest.raises(DuplicateEventConflictError, match="different sealed result"):
        competing.build_result(
            run_id,
            **result_fields(content_ref="result-store:conflicting"),
        )

    different = json.loads(json.dumps(first))
    different["output"]["content_ref"] = "result-store:store-conflict"
    different.pop("result_hash")
    different = build_artifact("reasoning_result", different)
    with pytest.raises(DuplicateEventConflictError, match="persisted result"):
        competing.events.save_terminal_result(run_id, different)


def test_sqlite_terminal_result_detects_column_or_json_tampering(tmp_path) -> None:
    path = tmp_path / "reasoning-events.db"
    engine = ReasoningEngine(SqliteEventStore(path))
    run_id, _ = build_failed_result(engine, sealed_contract())
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE terminal_results SET result_hash = ? WHERE run_id = ?",
            ("sha256:" + "0" * 64, run_id),
        )

    with pytest.raises(EventStorePersistenceError, match="columns differ"):
        SqliteEventStore(path).load_terminal_result(run_id)


def test_terminal_result_store_rejects_event_state_mismatch() -> None:
    contract = sealed_contract()
    cancelled_engine = ReasoningEngine(EventStore())
    cancelled_run = cancelled_engine.create_run_from_contract(contract)
    cancelled_engine.transition(
        cancelled_run,
        WorkflowState.CANCELLED,
        reason="cancelled for mismatch fixture / 为不匹配夹具取消",
    )
    cancelled_result = cancelled_engine.build_result(
        cancelled_run,
        **result_fields(content_ref="result-store:cancelled"),
    )

    failed_engine = ReasoningEngine(EventStore())
    failed_run = failed_engine.create_run_from_contract(contract)
    failed_engine.transition(
        failed_run,
        WorkflowState.FAILED,
        reason="failed event stream / 失败事件流",
    )
    with pytest.raises(EventStorePersistenceError, match="state differs"):
        failed_engine.events.save_terminal_result(failed_run, cancelled_result)


def test_sqlite_v1_event_database_migrates_to_v2_without_rewriting_events(tmp_path) -> None:
    path = tmp_path / "reasoning-events-v1.db"
    legacy_event = EventStore().append(
        run_id="run-v1",
        event_type="task_received",
        state=WorkflowState.RECEIVED,
        payload={
            "stage": "received",
            "task_binding": {
                "id": "task-binding-v1",
                "version": "1.0.0",
                "hash": "sha256:" + "a" * 64,
            },
        },
        event_id="event-v1",
        idempotency_key="command-v1",
    )
    with sqlite3.connect(path) as connection:
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
        connection.execute(
            """
            INSERT INTO reasoning_events (
                run_id, run_sequence, event_id, idempotency_key, event_type,
                workflow_state, occurred_epoch, envelope_json, payload_json,
                content_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                legacy_event.run_id,
                legacy_event.sequence,
                legacy_event.event_id,
                legacy_event.idempotency_key,
                legacy_event.event_type,
                legacy_event.state.value,
                legacy_event.timestamp,
                legacy_event.envelope_json,
                legacy_event.payload_json,
                legacy_event.content_json,
            ),
        )
        connection.execute("PRAGMA user_version = 1")

    store = SqliteEventStore(path)
    assert store.health_check() == {
        "schema_version": 2,
        "journal_mode": "wal",
        "integrity_check": "ok",
        "event_count": 1,
        "run_count": 1,
        "result_count": 0,
    }
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(terminal_results)")
        }
    assert "result_json" in columns
    assert store.events("run-v1")[0].as_dict() == legacy_event.as_dict()
