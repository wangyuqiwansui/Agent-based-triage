"""Transactional workflow route ledger tests / 事务型工作流路由账本测试。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
TEST_DIR = ROOT / "tests"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(0, str(TEST_DIR))

from test_workflow_route_ledger import (  # noqa: E402
    ACTOR,
    AUTHORITY,
    append_upgrade,
    routes,
)
from test_workflow_router import LATER, binding, route_request  # noqa: E402
from workflow_route_ledger import WorkflowRouteLedger, WorkflowRouteLedgerError  # noqa: E402
from workflow_route_sqlite_ledger import (  # noqa: E402
    SQLITE_ROUTE_SCHEMA_VERSION,
    SqliteWorkflowRouteLedger,
    workflow_route_stream_key,
)
from workflow_router import WorkflowRouteCoordinator  # noqa: E402


def test_sqlite_bootstrap_commit_replay_and_health(tmp_path: Path) -> None:
    initial, upgraded, _ = routes()
    database = tmp_path / "routes.sqlite3"
    ledger = SqliteWorkflowRouteLedger(database)
    stream_key = workflow_route_stream_key(initial)

    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    committed = append_upgrade(ledger, upgraded)

    reopened = SqliteWorkflowRouteLedger(database)
    assert reopened.replay(stream_key) == committed
    assert len(reopened.revision_events(stream_key)) == 1
    health = reopened.health_check()
    assert health == {
        "schema_version": SQLITE_ROUTE_SCHEMA_VERSION,
        "journal_mode": "wal",
        "integrity_check": "ok",
        "foreign_key_violations": 0,
        "stream_count": 1,
        "record_count": 2,
    }
    with sqlite3.connect(database) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1


def test_same_revision_retry_is_idempotent_across_concurrent_writers(
    tmp_path: Path,
) -> None:
    initial, upgraded, _ = routes()
    database = tmp_path / "routes.sqlite3"
    SqliteWorkflowRouteLedger(database).register_initial(
        initial,
        idempotency_key="IDEMPOTENCY_INITIAL_0001",
    )
    ledgers = [SqliteWorkflowRouteLedger(database) for _ in range(8)]

    with ThreadPoolExecutor(max_workers=8) as executor:
        committed = list(executor.map(lambda item: append_upgrade(item, upgraded), ledgers))

    assert {item["decision_revision"] for item in committed} == {2}
    assert len({item["route_envelope_hash"] for item in committed}) == 1
    stream_key = workflow_route_stream_key(initial)
    assert len(SqliteWorkflowRouteLedger(database).revision_events(stream_key)) == 1


def test_distinct_concurrent_gate_writers_serialize_monotonic_revisions(
    tmp_path: Path,
) -> None:
    initial, _, _ = routes()
    database = tmp_path / "routes.sqlite3"
    ledger = SqliteWorkflowRouteLedger(database)
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    stream_key = workflow_route_stream_key(initial)
    graph_bindings = [binding("RUN_GRAPH_A"), binding("RUN_GRAPH_B")]

    def bind_graph(index: int) -> dict[str, object]:
        writer = SqliteWorkflowRouteLedger(database)
        return writer.bind_run_graph(
            stream_key,
            graph_bindings[index],
            idempotency_key=f"IDEMPOTENCY_GRAPH_{index}",
            actor_binding=ACTOR,
            authority_binding=AUTHORITY,
            created_at=LATER,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        committed = list(executor.map(bind_graph, range(2)))

    assert {item["decision_revision"] for item in committed} == {2, 3}
    reopened = SqliteWorkflowRouteLedger(database)
    assert [event["to_revision"] for event in reopened.revision_events(stream_key)] == [2, 3]
    assert reopened.health_check()["record_count"] == 3


def test_conflicting_idempotency_key_rolls_back_without_advancing_head(
    tmp_path: Path,
) -> None:
    initial, _, _ = routes()
    database = tmp_path / "routes.sqlite3"
    ledger = SqliteWorkflowRouteLedger(database)
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    stream_key = workflow_route_stream_key(initial)
    committed = ledger.bind_run_graph(
        stream_key,
        binding("RUN_GRAPH_A"),
        idempotency_key="IDEMPOTENCY_GRAPH_CONFLICT",
        actor_binding=ACTOR,
        authority_binding=AUTHORITY,
        created_at=LATER,
    )

    with pytest.raises(WorkflowRouteLedgerError, match="different content"):
        SqliteWorkflowRouteLedger(database).bind_run_graph(
            stream_key,
            binding("RUN_GRAPH_B"),
            idempotency_key="IDEMPOTENCY_GRAPH_CONFLICT",
            actor_binding=ACTOR,
            authority_binding=AUTHORITY,
            created_at=LATER,
        )

    reopened = SqliteWorkflowRouteLedger(database)
    assert reopened.replay(stream_key) == committed
    assert len(reopened.revision_events(stream_key)) == 1


def test_tampered_record_or_head_fails_closed_on_replay(tmp_path: Path) -> None:
    initial, upgraded, _ = routes()
    database = tmp_path / "routes.sqlite3"
    ledger = SqliteWorkflowRouteLedger(database)
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    append_upgrade(ledger, upgraded)
    stream_key = workflow_route_stream_key(initial)
    with sqlite3.connect(database) as connection:
        stored = connection.execute(
            "SELECT record_json FROM route_records "
            "WHERE stream_key = ? AND record_sequence = 2",
            (stream_key,),
        ).fetchone()[0]
        record = json.loads(stored)
        record["request_fingerprint"] = "sha256:" + "f" * 64
        connection.execute(
            "UPDATE route_records SET record_json = ? "
            "WHERE stream_key = ? AND record_sequence = 2",
            (json.dumps(record, sort_keys=True, separators=(",", ":")), stream_key),
        )

    with pytest.raises(WorkflowRouteLedgerError, match="projection mismatch"):
        SqliteWorkflowRouteLedger(database).replay(stream_key)


def test_jsonl_migration_is_atomic_replayable_and_idempotent(tmp_path: Path) -> None:
    initial, upgraded, _ = routes()
    jsonl_path = tmp_path / "legacy-route-ledger.jsonl"
    legacy = WorkflowRouteLedger(jsonl_path)
    legacy.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    committed = append_upgrade(legacy, upgraded)
    database = tmp_path / "routes.sqlite3"
    ledger = SqliteWorkflowRouteLedger(database)

    first = ledger.migrate_jsonl(jsonl_path)
    second = SqliteWorkflowRouteLedger(database).migrate_jsonl(jsonl_path)

    assert first == committed
    assert second == committed
    assert ledger.replay(workflow_route_stream_key(initial)) == committed
    assert ledger.health_check()["record_count"] == 2


def test_multiple_streams_are_isolated_even_when_idempotency_keys_match(
    tmp_path: Path,
) -> None:
    coordinator = WorkflowRouteCoordinator()
    first = coordinator.route(route_request())
    second = coordinator.route(route_request(task_id="TASK_0002", run_id="RUN_0002"))
    database = tmp_path / "routes.sqlite3"
    ledger = SqliteWorkflowRouteLedger(database)

    ledger.register_initial(first, idempotency_key="IDEMPOTENCY_SHARED")
    ledger.register_initial(second, idempotency_key="IDEMPOTENCY_SHARED")

    first_key = workflow_route_stream_key(first)
    second_key = workflow_route_stream_key(second)
    assert first_key != second_key
    assert ledger.replay(first_key) == first
    assert ledger.replay(second_key) == second
    assert ledger.health_check()["stream_count"] == 2


def test_unknown_or_unversioned_nonempty_database_fails_closed(tmp_path: Path) -> None:
    unknown = tmp_path / "unknown.sqlite3"
    with sqlite3.connect(unknown) as connection:
        connection.execute("PRAGMA user_version = 99")
    with pytest.raises(WorkflowRouteLedgerError, match="unsupported"):
        SqliteWorkflowRouteLedger(unknown)

    unversioned = tmp_path / "unversioned.sqlite3"
    with sqlite3.connect(unversioned) as connection:
        connection.execute("CREATE TABLE unrelated (value TEXT)")
    with pytest.raises(WorkflowRouteLedgerError, match="not empty"):
        SqliteWorkflowRouteLedger(unversioned)


def test_versioned_database_with_wrong_constraints_fails_closed(tmp_path: Path) -> None:
    malformed = tmp_path / "malformed.sqlite3"
    with sqlite3.connect(malformed) as connection:
        connection.execute(
            """
            CREATE TABLE route_streams (
                stream_key TEXT, workflow_id TEXT, task_id TEXT, run_id TEXT,
                scene_id TEXT, task_atom_id TEXT, max_switches TEXT,
                head_sequence TEXT, head_revision TEXT, head_record_hash TEXT,
                created_at TEXT, updated_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE route_records (
                stream_key TEXT, record_sequence TEXT, decision_revision TEXT,
                record_type TEXT, idempotency_key TEXT, request_fingerprint TEXT,
                decision_id TEXT, envelope_hash TEXT, record_hash TEXT,
                record_json TEXT, created_at TEXT
            )
            """
        )
        connection.execute("PRAGMA user_version = 1")

    with pytest.raises(WorkflowRouteLedgerError, match="does not match schema"):
        SqliteWorkflowRouteLedger(malformed)
