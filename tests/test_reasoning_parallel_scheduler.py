"""Behavior tests for parallel leases and deadlines / 并行租约与截止时间行为测试。"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import pathlib
import sys

from jsonschema import Draft202012Validator, FormatChecker
import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(1, str(TESTS_DIR))

from reasoning_artifacts import artifact_fingerprint  # noqa: E402
from reasoning_event_sqlite_store import SqliteEventStore  # noqa: E402
from reasoning_parallel_factory import (  # noqa: E402
    ParallelPlanStateError,
    ReasoningParallelFactory,
)
from reasoning_parallel_scheduler import ParallelPathScheduler  # noqa: E402
from reasoning_runtime import ReasoningEngine, WorkflowState  # noqa: E402
from test_reasoning_parallel_factory import (  # noqa: E402
    close_usage,
    criterion_result,
    parallel_blueprint,
    parallel_contract,
    source_evidence,
)
from test_reasoning_runtime_schemas import NOW  # noqa: E402


def epoch(iso_text: str) -> float:
    return datetime.fromisoformat(iso_text.replace("Z", "+00:00")).timestamp()


def worker(worker_id: str) -> dict[str, str]:
    binding = {
        "id": worker_id,
        "version": "1.0.0",
        "hash": "sha256:" + "b" * 64,
    }
    return binding


def open_session(*, engine: ReasoningEngine | None = None, contract=None, blueprint=None):
    factory = ReasoningParallelFactory()
    selected_contract = contract or parallel_contract()
    selected_blueprint = blueprint or parallel_blueprint(selected_contract)
    plan = factory.compile(selected_blueprint, selected_contract)
    session = factory.start_session(
        engine or ReasoningEngine(),
        plan,
        selected_contract,
        selected_blueprint,
    )
    session.launch_wave()
    return factory, selected_contract, selected_blueprint, plan, session


def test_lease_acquire_renew_release_is_replayable_and_schema_valid() -> None:
    _, _, _, _, session = open_session()
    deadline = epoch(NOW) + 60
    scheduler = ParallelPathScheduler(session, deadline_at=deadline)
    acquired = scheduler.acquire(
        "path-cache",
        lease_id="lease-cache-1",
        worker_binding=worker("worker-a"),
        ttl_seconds=10,
        now=epoch(NOW),
    )
    assert acquired.phase == "acquired"
    assert acquired.revision == 1
    assert acquired.fencing_token == 1

    renewed = scheduler.renew(
        "path-cache",
        lease_id="lease-cache-1",
        worker_binding=worker("worker-a"),
        fencing_token=1,
        ttl_seconds=20,
        now=epoch(NOW) + 5,
    )
    assert renewed.phase == "renewed"
    assert renewed.revision == 2
    with pytest.raises(ParallelPlanStateError, match="active lease holder"):
        scheduler.release(
            "path-cache",
            lease_id="lease-cache-1",
            worker_binding=worker("worker-b"),
            fencing_token=1,
            now=epoch(NOW) + 6,
        )
    released = scheduler.release(
        "path-cache",
        lease_id="lease-cache-1",
        worker_binding=worker("worker-a"),
        fencing_token=1,
        now=epoch(NOW) + 6,
    )
    assert not released.active
    assert released.revision == 3

    schema = json.loads(
        (ROOT / "skills/harness-engineering-patterns/schemas/reasoning-event.schema.json")
        .read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    lease_events = [
        event
        for event in session.engine.events.events(session.run_id)
        if event.event_type == "parallel_path_updated"
    ]
    assert [event.payload["phase"] for event in lease_events] == [
        "acquired",
        "renewed",
        "released",
    ]
    assert all(not list(validator.iter_errors(event.as_dict())) for event in lease_events)


def test_sqlite_store_serializes_competing_branch_lease_writers(tmp_path) -> None:
    path = tmp_path / "parallel-events.db"
    first_store = SqliteEventStore(path)
    factory, contract, blueprint, plan, first_session = open_session(
        engine=ReasoningEngine(first_store)
    )
    second_engine = ReasoningEngine(SqliteEventStore(path))
    second_session = factory.resume_session(
        second_engine,
        plan,
        contract,
        blueprint,
    )
    deadline = epoch(NOW) + 60
    first_scheduler = ParallelPathScheduler(first_session, deadline_at=deadline)
    second_scheduler = ParallelPathScheduler(second_session, deadline_at=deadline)

    first_scheduler.acquire(
        "path-cache",
        lease_id="lease-winner",
        worker_binding=worker("worker-a"),
        ttl_seconds=30,
        now=epoch(NOW),
    )
    with pytest.raises(ParallelPlanStateError, match="active lease"):
        second_scheduler.acquire(
            "path-cache",
            lease_id="lease-loser",
            worker_binding=worker("worker-b"),
            ttl_seconds=30,
            now=epoch(NOW),
        )
    assert second_scheduler.lease("path-cache").lease_id == "lease-winner"


def test_expired_lease_can_be_reassigned_and_global_deadline_escalates() -> None:
    _, _, _, _, session = open_session()
    deadline = epoch(NOW) + 20
    scheduler = ParallelPathScheduler(session, deadline_at=deadline)
    scheduler.acquire(
        "path-cache",
        lease_id="lease-expiring",
        worker_binding=worker("worker-a"),
        ttl_seconds=5,
        now=epoch(NOW),
    )

    lease_sweep = scheduler.sweep_due(now=epoch(NOW) + 6)
    assert lease_sweep.expired_candidate_path_ids == ("path-cache",)
    assert not lease_sweep.deadline_reached
    assert lease_sweep.next_action == "reassign_expired_paths"
    assert lease_sweep.state is WorkflowState.EXECUTING
    assert session._branch_events()["path-cache"]["close"] is None

    replacement = scheduler.acquire(
        "path-cache",
        lease_id="lease-replacement",
        worker_binding=worker("worker-b"),
        ttl_seconds=10,
        now=epoch(NOW) + 7,
    )
    assert replacement.lease_id == "lease-replacement"
    assert replacement.phase == "acquired"

    deadline_sweep = scheduler.sweep_due(now=deadline)
    assert deadline_sweep.expired_candidate_path_ids == ("path-cache", "path-parser")
    assert deadline_sweep.deadline_reached
    assert deadline_sweep.next_action == "terminal_escalated"
    assert deadline_sweep.state is WorkflowState.ESCALATED


def test_only_current_unexpired_lease_holder_can_submit_branch_result() -> None:
    _, _, _, _, session = open_session()
    deadline = epoch(NOW) + 60
    scheduler = ParallelPathScheduler(session, deadline_at=deadline)
    scheduler.acquire(
        "path-cache",
        lease_id="lease-submit",
        worker_binding=worker("worker-a"),
        ttl_seconds=30,
        now=epoch(NOW),
    )
    evidence = source_evidence(session, path="path-cache", claim_id="claim-cache")

    with pytest.raises(ParallelPlanStateError, match="active lease holder"):
        scheduler.close_leased_branch(
            "path-cache",
            lease_id="lease-submit",
            worker_binding=worker("worker-b"),
            fencing_token=1,
            status="completed",
            candidate={"answer": "cache"},
            evidence_records=[evidence],
            criterion_results=criterion_result(),
            resource_use=close_usage(),
            information_gain=0.2,
            now=epoch(NOW) + 1,
        )

    outcome = scheduler.close_leased_branch(
        "path-cache",
        lease_id="lease-submit",
        worker_binding=worker("worker-a"),
        fencing_token=1,
        status="completed",
        candidate={"answer": "cache"},
        evidence_records=[evidence],
        criterion_results=criterion_result(),
        resource_use=close_usage(),
        information_gain=0.2,
        now=epoch(NOW) + 1,
    )
    assert outcome.status == "completed"
    assert scheduler.lease("path-cache").phase == "released"
    assert session._branch_events()["path-cache"]["close"] is not None


def test_expired_or_reassigned_worker_cannot_submit() -> None:
    _, _, _, _, session = open_session()
    scheduler = ParallelPathScheduler(session, deadline_at=epoch(NOW) + 60)
    scheduler.acquire(
        "path-cache",
        lease_id="lease-old",
        worker_binding=worker("worker-a"),
        ttl_seconds=5,
        now=epoch(NOW),
    )
    with pytest.raises(ParallelPlanStateError, match="expired lease"):
        scheduler.release(
            "path-cache",
            lease_id="lease-old",
            worker_binding=worker("worker-a"),
            fencing_token=1,
            now=epoch(NOW) + 6,
        )
    with pytest.raises(ParallelPlanStateError, match="expired lease"):
        scheduler.close_leased_branch(
            "path-cache",
            lease_id="lease-old",
            worker_binding=worker("worker-a"),
            fencing_token=1,
            status="cancelled",
            elimination_reason="worker stopped / 工作者停止",
            resource_use=close_usage(),
            information_gain=0.2,
            now=epoch(NOW) + 6,
        )
    scheduler.sweep_due(now=epoch(NOW) + 6)
    scheduler.acquire(
        "path-cache",
        lease_id="lease-new",
        worker_binding=worker("worker-b"),
        ttl_seconds=20,
        now=epoch(NOW) + 7,
    )
    assert scheduler.lease("path-cache").fencing_token == 2
    with pytest.raises(ParallelPlanStateError, match="active lease holder"):
        scheduler.close_leased_branch(
            "path-cache",
            lease_id="lease-old",
            worker_binding=worker("worker-a"),
            fencing_token=1,
            status="cancelled",
            elimination_reason="stale result / 陈旧结果",
            resource_use=close_usage(),
            information_gain=0.2,
            now=epoch(NOW) + 8,
        )


def test_deadline_fail_policy_transitions_to_failed() -> None:
    contract = parallel_contract()
    blueprint = parallel_blueprint(contract)
    blueprint["join_policy"] = deepcopy(blueprint["join_policy"])
    blueprint["join_policy"]["on_deadline"] = "fail"
    # Blueprint content changed but the contract remains authoritative; only
    # the compiled plan hash changes. / 蓝图内容变化但契约仍为权威；仅计划哈希变化。
    assert artifact_fingerprint(contract, "contract_hash") == contract["contract_hash"]
    _, _, _, _, session = open_session(contract=contract, blueprint=blueprint)
    deadline = epoch(NOW) + 5
    outcome = ParallelPathScheduler(session, deadline_at=deadline).sweep_due(
        now=deadline
    )
    assert outcome.next_action == "terminal_failed_deadline"
    assert outcome.state is WorkflowState.FAILED
