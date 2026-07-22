"""PostgreSQL runtime boundaries and integration tests / PostgreSQL 运行时边界与集成测试。"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
import pathlib
import sys
import uuid

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(1, str(TESTS_DIR))

import reasoning_event_postgres_store as postgres_module  # noqa: E402
from reasoning_event_postgres_store import PostgresEventStore  # noqa: E402
from reasoning_parallel_outbox import (  # noqa: E402
    ParallelDispatchClaimError,
    ParallelDispatchConflictError,
    ParallelDispatchCoordinator,
)
from reasoning_parallel_postgres_outbox import (  # noqa: E402
    PostgresParallelDispatchOutbox,
)
from reasoning_parallel_scheduler import ParallelPathScheduler  # noqa: E402
from reasoning_runtime import (  # noqa: E402
    EventStorePersistenceError,
    ReasoningEngine,
    WorkflowState,
)
from test_reasoning_event_sqlite_store import task_event  # noqa: E402
from test_reasoning_parallel_factory import (  # noqa: E402
    close_usage,
    criterion_result,
    source_evidence,
)
from test_reasoning_parallel_scheduler import epoch, open_session, worker  # noqa: E402
from test_reasoning_runtime_schemas import NOW, sealed_contract  # noqa: E402
from test_reasoning_terminal_result_store import result_fields  # noqa: E402


POSTGRES_DSN = os.environ.get("HARNESS_POSTGRES_DSN", "").strip()


@pytest.fixture
def postgres_target():
    """Yield an isolated generated schema or skip without a real server.

    / 生成隔离 Schema；没有真实服务器时明确跳过。
    """

    if postgres_module.psycopg is None:
        pytest.skip("Psycopg 3 is not installed / 未安装 Psycopg 3")
    if not POSTGRES_DSN:
        pytest.skip(
            "HARNESS_POSTGRES_DSN is not configured; real PostgreSQL test skipped / "
            "未配置 HARNESS_POSTGRES_DSN；跳过真实 PostgreSQL 测试"
        )
    schema = f"harness_test_{uuid.uuid4().hex[:20]}"
    try:
        yield POSTGRES_DSN, schema
    finally:
        with postgres_module.psycopg.connect(
            POSTGRES_DSN,
            autocommit=True,
            connect_timeout=5,
            application_name="harness-reasoning-test-cleanup",
        ) as connection:
            connection.execute(
                postgres_module.sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    postgres_module.sql.Identifier(schema)
                )
            )


def test_postgres_advisory_keys_are_stable_distinct_signed_bigints() -> None:
    first = PostgresEventStore._advisory_key("run-a")
    assert first == PostgresEventStore._advisory_key("run-a")
    assert first != PostgresEventStore._advisory_key("run-b")
    assert -(2**63) <= first < 2**63


@pytest.mark.skipif(
    postgres_module.psycopg is None,
    reason="Psycopg 3 is not installed / 未安装 Psycopg 3",
)
def test_postgres_schema_name_fails_before_network_connection() -> None:
    with pytest.raises(ValueError, match="lowercase PostgreSQL identifier"):
        PostgresEventStore(
            "postgresql://this-host-must-not-be-contacted.invalid/example",
            schema="Unsafe-Schema",
        )


def test_postgres_cross_instance_events_resume_and_terminal_result(postgres_target) -> None:
    dsn, schema = postgres_target
    first_writer = PostgresEventStore(dsn, schema=schema)
    second_writer = PostgresEventStore(dsn, schema=schema)
    first_kwargs = task_event(
        run_id="run-postgres-shared",
        event_id="event-postgres-1",
        idempotency_key="command-postgres-1",
        task_binding_id="task-binding-postgres-1",
        parent_event_id=None,
        timestamp=NOW,
    )
    first = first_writer.append(**first_kwargs)
    stale_head = second_writer.events("run-postgres-shared")[-1]
    second_kwargs = task_event(
        run_id="run-postgres-shared",
        event_id="event-postgres-2",
        idempotency_key="command-postgres-2",
        task_binding_id="task-binding-postgres-2",
        parent_event_id=first.event_id,
        timestamp="2026-07-20T00:00:01.000Z",
    )
    second = first_writer.append(**second_kwargs)

    with pytest.raises(EventStorePersistenceError, match="stale causal parent"):
        second_writer.append(
            **task_event(
                run_id="run-postgres-shared",
                event_id="event-postgres-stale",
                idempotency_key="command-postgres-stale",
                task_binding_id="task-binding-postgres-stale",
                parent_event_id=stale_head.event_id,
                timestamp="2026-07-20T00:00:02.000Z",
            )
        )
    retry = second_writer.append(**second_kwargs)
    assert retry.as_dict() == second.as_dict()
    assert [event.sequence for event in second_writer.events("run-postgres-shared")] == [
        1,
        2,
    ]

    contract = sealed_contract()
    engine = ReasoningEngine(PostgresEventStore(dsn, schema=schema))
    run_id = engine.create_run_from_contract(contract)
    engine.transition(
        run_id,
        WorkflowState.FAILED,
        reason="PostgreSQL terminal persistence test / PostgreSQL 终态持久化测试",
    )
    result = engine.build_result(run_id, **result_fields())
    resumed = ReasoningEngine(PostgresEventStore(dsn, schema=schema))
    assert resumed.resume_run_from_contract(contract) == run_id
    assert resumed.events.load_terminal_result(run_id) == result
    health = resumed.events.health_check()
    assert health["schema"] == schema
    assert health["run_count"] == 2
    assert health["result_count"] == 1
    assert dsn not in str(health)


def test_postgres_outbox_rolls_back_and_claims_with_skip_locked(
    postgres_target,
    monkeypatch,
) -> None:
    dsn, schema = postgres_target
    store = PostgresEventStore(dsn, schema=schema)
    outbox = PostgresParallelDispatchOutbox(store)
    _, _, _, _, session = open_session(engine=ReasoningEngine(store))
    scheduler = ParallelPathScheduler(session, deadline_at=epoch(NOW) + 60)
    coordinator = ParallelDispatchCoordinator(scheduler, outbox)

    original_enqueue = outbox.enqueue

    def insert_then_fail(**kwargs):
        original_enqueue(**kwargs)
        raise RuntimeError("injected PostgreSQL outbox failure")

    monkeypatch.setattr(outbox, "enqueue", insert_then_fail)
    with pytest.raises(RuntimeError, match="injected PostgreSQL outbox"):
        coordinator.acquire_and_enqueue(
            "path-cache",
            lease_id="lease-postgres-rollback",
            worker_binding=worker("worker-rollback"),
            ttl_seconds=30,
            now=epoch(NOW),
        )
    assert scheduler.lease("path-cache") is None
    assert outbox.get("dispatch-lease-postgres-rollback") is None
    monkeypatch.setattr(outbox, "enqueue", original_enqueue)

    coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-postgres-cache",
        worker_binding=worker("worker-a"),
        ttl_seconds=30,
        now=epoch(NOW),
    )
    coordinator.acquire_and_enqueue(
        "path-parser",
        lease_id="lease-postgres-parser",
        worker_binding=worker("worker-b"),
        ttl_seconds=30,
        now=epoch(NOW),
    )
    first = PostgresParallelDispatchOutbox(
        PostgresEventStore(dsn, schema=schema)
    )
    second_outbox = PostgresParallelDispatchOutbox(
        PostgresEventStore(dsn, schema=schema)
    )

    def claim(selected_outbox, owner):
        return selected_outbox.claim_batch(
            delivery_owner=owner,
            limit=1,
            claim_ttl_seconds=5,
            now=epoch(NOW) + 1,
        )[0]

    with ThreadPoolExecutor(max_workers=2) as executor:
        claims = tuple(
            future.result()
            for future in (
                executor.submit(claim, first, "dispatcher-a"),
                executor.submit(claim, second_outbox, "dispatcher-b"),
            )
        )
    assert len({item.dispatch_id for item in claims}) == 2

    reclaimed = outbox.claim_batch(
        delivery_owner="dispatcher-recovery",
        limit=1,
        claim_ttl_seconds=5,
        now=epoch(NOW) + 7,
    )[0]
    stale = next(item for item in claims if item.dispatch_id == reclaimed.dispatch_id)
    assert reclaimed.delivery_token != stale.delivery_token
    with pytest.raises(ParallelDispatchClaimError, match="stale"):
        outbox.acknowledge_delivery(
            stale.dispatch_id,
            delivery_token=stale.delivery_token,
            delivery_owner=stale.delivery_owner,
            delivered_at=epoch(NOW) + 8,
        )
    assert outbox.acknowledge_delivery(
        reclaimed.dispatch_id,
        delivery_token=reclaimed.delivery_token,
        delivery_owner="dispatcher-recovery",
        delivered_at=epoch(NOW) + 8,
    ).status == "delivered"


def test_postgres_outbox_fencing_rejects_reassigned_worker_result(
    postgres_target,
) -> None:
    dsn, schema = postgres_target
    store = PostgresEventStore(dsn, schema=schema)
    outbox = PostgresParallelDispatchOutbox(store)
    _, _, _, _, session = open_session(engine=ReasoningEngine(store))
    scheduler = ParallelPathScheduler(session, deadline_at=epoch(NOW) + 60)
    coordinator = ParallelDispatchCoordinator(scheduler, outbox)
    old = coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-postgres-old",
        worker_binding=worker("worker-old"),
        ttl_seconds=5,
        now=epoch(NOW),
    )
    scheduler.sweep_due(now=epoch(NOW) + 6)
    new = coordinator.acquire_and_enqueue(
        "path-cache",
        lease_id="lease-postgres-new",
        worker_binding=worker("worker-new"),
        ttl_seconds=20,
        now=epoch(NOW) + 7,
    )
    assert (old.lease.fencing_token, new.lease.fencing_token) == (1, 2)
    assert outbox.get(old.dispatch.dispatch_id).status == "superseded"
    evidence = source_evidence(session, path="path-cache", claim_id="claim-cache")
    with pytest.raises(ParallelDispatchConflictError, match="cannot complete"):
        coordinator.close_leased_branch(
            "path-cache",
            dispatch_id=old.dispatch.dispatch_id,
            lease_id=old.lease.lease_id,
            worker_binding=worker("worker-old"),
            fencing_token=old.lease.fencing_token,
            status="completed",
            candidate={"answer": "stale"},
            evidence_records=[evidence],
            criterion_results=criterion_result(),
            resource_use=close_usage(),
            information_gain=0.2,
            now=epoch(NOW) + 8,
        )

