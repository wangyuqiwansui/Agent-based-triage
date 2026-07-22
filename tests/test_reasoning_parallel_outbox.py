"""Parallel worker outbox and fencing tests / 并行工作者发件箱与栅栏测试。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
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
from reasoning_parallel_factory import ParallelPlanStateError  # noqa: E402
from reasoning_parallel_outbox import (  # noqa: E402
    ParallelDispatchClaimError,
    ParallelDispatchConflictError,
    ParallelDispatchCoordinator,
    ParallelDispatchError,
    SqliteParallelDispatchOutbox,
)
from reasoning_parallel_scheduler import ParallelPathScheduler  # noqa: E402
from reasoning_runtime import ReasoningEngine  # noqa: E402
from test_reasoning_parallel_factory import (  # noqa: E402
    close_usage,
    criterion_result,
    source_evidence,
)
from test_reasoning_parallel_scheduler import epoch, open_session, worker  # noqa: E402
from test_reasoning_runtime_schemas import NOW  # noqa: E402


def dispatch_runtime(tmp_path):
    path = tmp_path / "parallel-dispatch.db"
    store = SqliteEventStore(path)
    outbox = SqliteParallelDispatchOutbox(store)
    _, _, _, _, session = open_session(engine=ReasoningEngine(store))
    scheduler = ParallelPathScheduler(session, deadline_at=epoch(NOW) + 60)
    coordinator = ParallelDispatchCoordinator(scheduler, outbox)
    return path, store, outbox, session, scheduler, coordinator


def test_acquire_and_enqueue_commit_together_or_roll_back_together(
    tmp_path, monkeypatch
) -> None:
    _, _, outbox, session, scheduler, coordinator = dispatch_runtime(tmp_path)
    first = coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-dispatch-cache",
        worker_binding=worker("worker-a"),
        ttl_seconds=20,
        now=epoch(NOW),
    )
    assert first.lease.fencing_token == 1
    assert first.dispatch.status == "pending"
    assert first.dispatch.work_payload["candidate_path_id"] == "path-cache"
    assert scheduler.lease("path-cache").lease_id == "lease-dispatch-cache"

    def fail_enqueue(**_kwargs):
        raise ParallelDispatchError("injected outbox failure")

    monkeypatch.setattr(outbox, "enqueue", fail_enqueue)
    with pytest.raises(ParallelDispatchError, match="injected outbox"):
        coordinator.acquire_and_enqueue(
            "path-parser",
            lease_id="lease-dispatch-parser",
            worker_binding=worker("worker-b"),
            ttl_seconds=20,
            now=epoch(NOW),
        )

    assert scheduler.lease("path-parser") is None
    assert outbox.get("dispatch-lease-dispatch-parser") is None
    acquired_paths = [
        event.as_dict()["candidate_path_id"]
        for event in session.engine.events.events(session.run_id)
        if event.event_type == "parallel_path_updated"
        and event.payload["phase"] == "acquired"
    ]
    assert acquired_paths == ["path-cache"]


def test_acquire_and_enqueue_exact_retry_returns_committed_outcome(tmp_path) -> None:
    _, _, outbox, session, _, coordinator = dispatch_runtime(tmp_path)
    arguments = {
        "lease_id": "lease-acquire-retry",
        "worker_binding": worker("worker-a"),
        "ttl_seconds": 20,
        "now": epoch(NOW),
    }
    first = coordinator.acquire_and_enqueue("path-cache", **arguments)
    event_count = len(session.engine.events.events(session.run_id))
    retry = coordinator.acquire_and_enqueue("path-cache", **arguments)

    assert retry == first
    assert len(session.engine.events.events(session.run_id)) == event_count
    assert outbox.health_check()["total_count"] == 1
    with pytest.raises(ParallelDispatchConflictError, match="differs"):
        coordinator.acquire_and_enqueue(
            "path-cache",
            **arguments,
            work_payload={"candidate_path_id": "path-cache", "changed": True},
        )


def test_delivery_claim_reclaims_after_crash_and_fences_old_ack(tmp_path) -> None:
    _, _, outbox, _, _, coordinator = dispatch_runtime(tmp_path)
    acquisition = coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-delivery",
        worker_binding=worker("worker-a"),
        ttl_seconds=30,
        now=epoch(NOW),
    )
    dispatch_id = acquisition.dispatch.dispatch_id

    first = outbox.claim_batch(
        delivery_owner="dispatcher-a",
        limit=1,
        claim_ttl_seconds=5,
        now=epoch(NOW) + 1,
    )[0]
    assert first.delivery_attempt_count == 1
    assert outbox.claim_batch(
        delivery_owner="dispatcher-b",
        limit=1,
        claim_ttl_seconds=5,
        now=epoch(NOW) + 2,
    ) == ()

    second = outbox.claim_batch(
        delivery_owner="dispatcher-b",
        limit=1,
        claim_ttl_seconds=5,
        now=epoch(NOW) + 7,
    )[0]
    assert second.delivery_attempt_count == 2
    assert second.delivery_token != first.delivery_token
    with pytest.raises(ParallelDispatchClaimError, match="stale"):
        outbox.acknowledge_delivery(
            dispatch_id,
            delivery_token=first.delivery_token,
            delivery_owner="dispatcher-a",
            delivered_at=epoch(NOW) + 8,
        )
    delivered = outbox.acknowledge_delivery(
        dispatch_id,
        delivery_token=second.delivery_token,
        delivery_owner="dispatcher-b",
        delivered_at=epoch(NOW) + 8,
    )
    retry = outbox.acknowledge_delivery(
        dispatch_id,
        delivery_token=second.delivery_token,
        delivery_owner="dispatcher-b",
        delivered_at=epoch(NOW) + 9,
    )
    assert delivered.status == "delivered"
    assert retry == delivered
    assert outbox.health_check()["delivery_attempt_count"] == 2


def test_reassignment_supersedes_old_dispatch_and_fences_late_result(tmp_path) -> None:
    _, _, outbox, session, scheduler, coordinator = dispatch_runtime(tmp_path)
    old = coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-old-dispatch",
        worker_binding=worker("worker-a"),
        ttl_seconds=5,
        now=epoch(NOW),
    )
    scheduler.sweep_due(now=epoch(NOW) + 6)
    new = coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-new-dispatch",
        worker_binding=worker("worker-b"),
        ttl_seconds=20,
        now=epoch(NOW) + 7,
    )
    assert old.lease.fencing_token == 1
    assert new.lease.fencing_token == 2
    assert outbox.get(old.dispatch.dispatch_id).status == "superseded"

    evidence = source_evidence(session, path="path-cache", claim_id="claim-cache")
    with pytest.raises(ParallelDispatchConflictError, match="cannot complete"):
        coordinator.close_leased_branch(
            "path-cache",
            dispatch_id=old.dispatch.dispatch_id,
            lease_id=old.lease.lease_id,
            worker_binding=worker("worker-a"),
            fencing_token=old.lease.fencing_token,
            status="completed",
            candidate={"answer": "stale"},
            evidence_records=[evidence],
            criterion_results=criterion_result(),
            resource_use=close_usage(),
            information_gain=0.2,
            now=epoch(NOW) + 8,
        )

    arguments = {
        "dispatch_id": new.dispatch.dispatch_id,
        "lease_id": new.lease.lease_id,
        "worker_binding": worker("worker-b"),
        "fencing_token": new.lease.fencing_token,
        "status": "completed",
        "candidate": {"answer": "fresh"},
        "evidence_records": [evidence],
        "criterion_results": criterion_result(),
        "resource_use": close_usage(),
        "information_gain": 0.2,
        "now": epoch(NOW) + 8,
    }
    first = coordinator.close_leased_branch("path-cache", **arguments)
    event_count = len(session.engine.events.events(session.run_id))
    retry = coordinator.close_leased_branch("path-cache", **arguments)
    assert first == retry
    assert outbox.get(new.dispatch.dispatch_id).status == "completed"
    assert len(session.engine.events.events(session.run_id)) == event_count


def test_invalid_result_rolls_back_prepared_outbox_completion(tmp_path) -> None:
    _, _, outbox, _, _, coordinator = dispatch_runtime(tmp_path)
    acquisition = coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-invalid-result",
        worker_binding=worker("worker-a"),
        ttl_seconds=20,
        now=epoch(NOW),
    )
    with pytest.raises(ParallelPlanStateError, match="evidence types are incomplete"):
        coordinator.close_leased_branch(
            "path-cache",
            dispatch_id=acquisition.dispatch.dispatch_id,
            lease_id=acquisition.lease.lease_id,
            worker_binding=worker("worker-a"),
            fencing_token=acquisition.lease.fencing_token,
            status="completed",
            candidate={"answer": "invalid"},
            evidence_records=[],
            criterion_results=criterion_result(),
            resource_use=close_usage(),
            information_gain=0.2,
            now=epoch(NOW) + 1,
        )
    assert outbox.get(acquisition.dispatch.dispatch_id).status == "pending"


def test_separate_dispatchers_claim_distinct_rows_under_contention(tmp_path) -> None:
    path, _, _, _, _, coordinator = dispatch_runtime(tmp_path)
    coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-claim-cache",
        worker_binding=worker("worker-a"),
        ttl_seconds=30,
        now=epoch(NOW),
    )
    coordinator.acquire_and_enqueue(
        "path-parser",
        lease_id="lease-claim-parser",
        worker_binding=worker("worker-b"),
        ttl_seconds=30,
        now=epoch(NOW),
    )
    first = SqliteParallelDispatchOutbox(SqliteEventStore(path))
    second = SqliteParallelDispatchOutbox(SqliteEventStore(path))

    def claim(outbox, owner):
        return outbox.claim_batch(
            delivery_owner=owner,
            limit=1,
            claim_ttl_seconds=10,
            now=epoch(NOW) + 1,
        )[0]

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(
            future.result()
            for future in (
                executor.submit(claim, first, "dispatcher-a"),
                executor.submit(claim, second, "dispatcher-b"),
            )
        )
    assert len({item.dispatch_id for item in results}) == 2
    assert all(item.status == "claimed" for item in results)


def test_outbox_rejects_tampering_and_reports_bounded_health(tmp_path) -> None:
    path, _, outbox, _, _, coordinator = dispatch_runtime(tmp_path)
    acquisition = coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-tamper",
        worker_binding=worker("worker-a"),
        ttl_seconds=20,
        now=epoch(NOW),
    )
    health = outbox.health_check()
    assert health["status_counts"]["pending"] == 1
    assert health["delivery_attempt_count"] == 0
    with sqlite3.connect(path) as connection:
        record = json.loads(
            connection.execute(
                "SELECT dispatch_json FROM parallel_dispatch_outbox "
                "WHERE dispatch_id = ?",
                (acquisition.dispatch.dispatch_id,),
            ).fetchone()[0]
        )
        record["work_payload"]["candidate_path_id"] = "tampered-path"
        connection.execute(
            "UPDATE parallel_dispatch_outbox SET dispatch_json = ? "
            "WHERE dispatch_id = ?",
            (
                json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                acquisition.dispatch.dispatch_id,
            ),
        )
    with pytest.raises(ParallelDispatchError, match="hash mismatch"):
        outbox.get(acquisition.dispatch.dispatch_id)
