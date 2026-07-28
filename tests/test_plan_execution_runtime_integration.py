"""Integration and failure tests for production Plan-and-Execute adapters.

计划并执行生产适配器的集成与故障测试。
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(1, str(TESTS_DIR))

from plan_execution import (  # noqa: E402
    IdempotencyStatus,
    PlanExecutionSession,
    compile_goal_contract,
    compile_workflow_plan,
)
from plan_execution_completion import (  # noqa: E402
    CompletionGateError,
    finalize_workflow_execution,
    validate_workflow_execution_result,
)
from plan_execution_events import PlanExecutionEventAdapter  # noqa: E402
from plan_execution_sqlite_store import (  # noqa: E402
    SqlitePlanExecutionStore,
    StalePlanWriterError,
)
from plan_tool_dispatch import (  # noqa: E402
    PlanDispatchBindingError,
    PlanToolDispatchCoordinator,
)
from reasoning_runtime import EventStore  # noqa: E402
from tool_dispatch import (  # noqa: E402
    ActionIntent,
    ActionRisk,
    DispatchContext,
    ExecutionClassification,
    ObservationMode,
    SideEffectClass,
    SideEffectState,
    StateEvidence,
    ToolCapability,
    ToolDispatchCoordinator,
    ToolDispatchRequest,
    ToolDispatchRuntime,
    ToolExecutionReceipt,
)
from tool_dispatch_sqlite_store import SqliteToolDispatchStore  # noqa: E402
from test_plan_execution import (  # noqa: E402
    HASH_A,
    HASH_B,
    LATER,
    NOW,
    binding,
    complete_read,
    goal_source,
    plan_blueprint,
    read_step,
    write_step,
)


def fixed_clock() -> datetime:
    return datetime(2026, 7, 28, 8, 0, tzinfo=timezone.utc)


def compiled_goal_and_plan() -> tuple[dict[str, object], dict[str, object]]:
    goal = compile_goal_contract(goal_source())
    plan = compile_workflow_plan(goal, plan_blueprint())
    return goal, plan


def complete_refund_session(
    plan: dict[str, object],
    *,
    run_id: str,
) -> PlanExecutionSession:
    session = PlanExecutionSession(plan, run_id=run_id, started_at=NOW)
    complete_read(session, "STEP_A")
    session.start_step("STEP_B", occurred_at=NOW)
    session.claim_action("STEP_B", request_digest=HASH_A, occurred_at=NOW)
    session.record_action_result(
        "STEP_B",
        status=IdempotencyStatus.SUCCEEDED,
        provider_ref="PROVIDER_REF_1",
        result_digest=HASH_B,
        occurred_at=LATER,
    )
    session.complete_step(
        "STEP_B",
        output_digest=HASH_B,
        completion_evidence=["EVIDENCE_PROVIDER"],
        occurred_at=LATER,
    )
    complete_read(session, "STEP_C", digest=HASH_B)
    return session


def completion_inputs() -> dict[str, object]:
    return {
        "criterion_results": [
            {
                "criterion_id": "CRITERION_RECEIPT",
                "satisfied": True,
                "evidence": [
                    {
                        "evidence_type": "provider_receipt",
                        "evidence_ref": "EVIDENCE_PROVIDER",
                    }
                ],
            }
        ],
        "completion_evidence": [
            {
                "evidence_type": "refund_receipt",
                "evidence_ref": "EVIDENCE_PROVIDER",
            },
            {
                "evidence_type": "order_state",
                "evidence_ref": "EVIDENCE_ORDER_STATE",
            },
        ],
        "validator_results": [
            {
                "validator_binding": binding("VALIDATOR_REFUND"),
                "status": "passed",
                "checked_at": LATER,
                "evidence_refs": ["EVIDENCE_VALIDATION"],
            }
        ],
        "probe_health": {
            "probe_binding": binding("PROBE_PLAN_EXECUTION"),
            "health": "healthy",
            "blocking_findings": 0,
            "checked_at": LATER,
        },
        "approval_checks": [
            {
                "step_id": "STEP_B",
                "approval_binding": binding("APPROVAL_REFUND"),
                "status": "valid",
                "checked_at": LATER,
            }
        ],
    }


def test_sqlite_plan_store_rejects_stale_heads_and_restores_unknown_write(
    tmp_path: Path,
) -> None:
    goal, plan = compiled_goal_and_plan()
    store = SqlitePlanExecutionStore(tmp_path / "plan.sqlite")
    session = PlanExecutionSession(plan, run_id="RUN_STORE", started_at=NOW)
    initial = store.initialize_run(
        goal,
        session,
        checkpoint_id="CHECKPOINT_INITIAL",
        created_at=NOW,
    )
    stale = PlanExecutionSession.from_checkpoint(plan, initial)

    complete_read(session, "STEP_A")
    first = store.commit_session(
        session,
        checkpoint_id="CHECKPOINT_STEP_A",
        expected_head_hash=initial["checkpoint_hash"],
        created_at=LATER,
    )
    stale.start_step("STEP_A", occurred_at=NOW)
    with pytest.raises(StalePlanWriterError):
        store.commit_session(
            stale,
            checkpoint_id="CHECKPOINT_STALE",
            expected_head_hash=initial["checkpoint_hash"],
        )

    session.start_step("STEP_B", occurred_at=NOW)
    session.claim_action("STEP_B", request_digest=HASH_A, occurred_at=NOW)
    outbox = {
        "outbox_id": "OUTBOX_CRASH",
        "step_id": "STEP_B",
        "attempt": 1,
        "action_id": "ACTION_CRASH",
        "intent_hash": HASH_A,
        "payload_binding": binding("ACTION_CRASH"),
    }
    before_dispatch = store.commit_session(
        session,
        checkpoint_id="CHECKPOINT_BEFORE_CRASH",
        expected_head_hash=first["checkpoint_hash"],
        outbox_items=[outbox],
        created_at=LATER,
    )

    _, restored, restored_head = store.restore_session("RUN_STORE")
    step_b = next(
        record
        for record in restored.step_records
        if record["step_id"] == "STEP_B"
    )
    assert step_b["state"] == "unknown"
    assert restored.events[-1]["event_type"] == "action_result_recorded"

    recovered = store.commit_session(
        restored,
        checkpoint_id="CHECKPOINT_RECOVERED",
        expected_head_hash=restored_head,
        outbox_updates=[
            {
                "outbox_id": "OUTBOX_CRASH",
                "status": "unknown",
                "result_binding": None,
            }
        ],
        created_at=LATER,
    )
    assert recovered["last_event_sequence"] == (
        before_dispatch["last_event_sequence"] + 1
    )
    assert store.outbox_items("RUN_STORE")[0]["status"] == "unknown"
    assert store.health_check()["integrity_check"] == "ok"


def dispatch_goal_and_plan() -> tuple[dict[str, object], dict[str, object]]:
    goal = compile_goal_contract(goal_source())
    step = write_step("STEP_WRITE")
    step["handler"] = {
        "kind": "tool",
        "ref": "TOOL_STEP_WRITE",
        "version": "1.0.0",
    }
    plan = compile_workflow_plan(
        goal,
        {
            "plan_id": "PLAN_DISPATCH",
            "steps": [step],
            "stop_conditions": {
                "max_replans": 1,
                "max_retries_per_step": 1,
                "deadline_at": None,
            },
            "created_at": NOW,
        },
    )
    return goal, plan


def dispatch_capability() -> ToolCapability:
    return ToolCapability(
        tool_id="TOOL_STEP_WRITE",
        tool_version="1.0.0",
        action_types=("refund_order",),
        parameter_schema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "additionalProperties": False,
            "required": ["order_id", "amount"],
            "properties": {
                "order_id": {"type": "string", "minLength": 1},
                "amount": {"type": "number", "exclusiveMinimum": 0},
            },
        },
        required_scopes=frozenset({"refund:write"}),
        allowed_tenants=frozenset({"TENANT_A"}),
        allowed_stages=frozenset({"execution"}),
        side_effect_class=SideEffectClass.REVERSIBLE_WRITE,
        priority=10,
        executor_binding=binding("EXECUTOR_REFUND"),
        authorization_policy_binding=binding("POLICY_REFUND"),
        sandbox_binding=binding("SANDBOX_REFUND"),
        compensation_binding=binding("COMPENSATE_REFUND"),
        allowed_resource_prefixes=("order:",),
    )


def dispatch_request() -> ToolDispatchRequest:
    evidence = StateEvidence(
        resource_versions={"order:ORDER_1": "7"},
        observed_at=NOW,
        evidence_binding=binding("STATE_ORDER_1"),
        content_hash=HASH_A,
    )
    intent = ActionIntent(
        workflow_id="PLAN_DISPATCH",
        workflow_version="1.0.0",
        run_id="RUN_DISPATCH",
        goal_id="GOAL_REFUND",
        node_id="STEP_WRITE",
        attempt_id="ATTEMPT_WRITE_1",
        action_id="ACTION_WRITE_1",
        parent_action_id=None,
        plan_version="1.0.0",
        correlation_id="CORRELATION_WRITE_1",
        action_type="refund_order",
        parameters={"order_id": "ORDER_1", "amount": 10.0},
        target_resources=("order:ORDER_1",),
        expected_side_effect=SideEffectClass.REVERSIBLE_WRITE,
        maximum_side_effect=SideEffectClass.REVERSIBLE_WRITE,
        risk_level=ActionRisk.MEDIUM,
        idempotency_key="refund:ORDER_1:STEP_WRITE",
        state_evidence=evidence,
        approval=None,
    )
    context = DispatchContext(
        actor_binding=binding("ACTOR_REFUND"),
        actor_scopes=frozenset({"refund:write"}),
        tenant_id="TENANT_A",
        workflow_state="executable",
        stage="execution",
        dependencies_satisfied=True,
        budget_available=True,
        concurrency_clear=True,
        current_resource_versions={"order:ORDER_1": "7"},
        action_authorization_binding=binding("AUTH_REFUND"),
        observation_mode=ObservationMode.HARD_GATE,
        critical_observability_ready=True,
        durable_idempotency_available=True,
        retry_authorized=False,
        created_at=NOW,
        permit_expires_at=LATER,
    )
    return ToolDispatchRequest(intent, context)


def test_plan_tool_dispatch_persists_both_phases_and_dual_event_streams(
    tmp_path: Path,
) -> None:
    goal, plan = dispatch_goal_and_plan()
    plan_store = SqlitePlanExecutionStore(tmp_path / "plan-dispatch.sqlite")
    session = PlanExecutionSession(plan, run_id="RUN_DISPATCH", started_at=NOW)
    plan_store.initialize_run(
        goal,
        session,
        checkpoint_id="CHECKPOINT_DISPATCH_INITIAL",
        created_at=NOW,
    )
    tool_store = SqliteToolDispatchStore(tmp_path / "tool-dispatch.sqlite")
    runtime = ToolDispatchRuntime(
        ToolDispatchCoordinator(
            [dispatch_capability()],
            authority_verifier=lambda *_: True,
        ),
        store=tool_store,
        clock=fixed_clock,
    )
    coordinator = PlanToolDispatchCoordinator(plan_store, runtime)
    calls = {"count": 0}

    def executor(*_: object) -> ToolExecutionReceipt:
        calls["count"] += 1
        return ToolExecutionReceipt(
            ExecutionClassification.SUCCESS,
            SideEffectState.CONFIRMED,
            output_binding=binding("OUTPUT_REFUND"),
            external_receipt_binding=binding("RECEIPT_REFUND"),
            actual_side_effects=(
                {
                    "resource_id": "order:ORDER_1",
                    "effect_type": "refunded",
                    "receipt_binding": binding("RECEIPT_REFUND"),
                },
            ),
        )

    run = coordinator.dispatch_step(
        session,
        dispatch_request(),
        executor,
        completion_evidence=["EVIDENCE_PROVIDER"],
    )

    assert calls["count"] == 1
    assert run.result["classification"] == "success"
    assert session.is_complete() is True
    assert plan_store.outbox_items(
        "RUN_DISPATCH",
        statuses=("acknowledged",),
    )[0]["result_binding"]["hash"] == run.result["result_hash"]
    _, restored, _ = plan_store.restore_session("RUN_DISPATCH")
    assert restored.is_complete() is True

    adapter = PlanExecutionEventAdapter(EventStore())
    batch = adapter.append_plan_events(
        plan_store.events("RUN_DISPATCH"),
        plan=plan,
        goal_contract=goal,
        step_records=session.step_records,
        tool_run=run,
    )
    assert {event.event_type for event in batch.reasoning_events} >= {
        "run_created",
        "step_started",
        "step_closed",
    }
    assert len(batch.tool_events) == len(run.events)
    assert "action_claimed" in batch.unmapped_event_types


def test_plan_tool_dispatch_rejects_handler_drift_before_execution(
    tmp_path: Path,
) -> None:
    goal, plan = dispatch_goal_and_plan()
    plan_store = SqlitePlanExecutionStore(tmp_path / "plan-drift.sqlite")
    session = PlanExecutionSession(plan, run_id="RUN_DISPATCH", started_at=NOW)
    plan_store.initialize_run(
        goal,
        session,
        checkpoint_id="CHECKPOINT_DRIFT_INITIAL",
        created_at=NOW,
    )
    drifted = replace(dispatch_capability(), tool_id="TOOL_OTHER")
    runtime = ToolDispatchRuntime(
        ToolDispatchCoordinator(
            [drifted],
            authority_verifier=lambda *_: True,
        ),
        store=SqliteToolDispatchStore(tmp_path / "tool-drift.sqlite"),
        clock=fixed_clock,
    )
    called = {"value": False}

    def executor(*_: object) -> ToolExecutionReceipt:
        called["value"] = True
        raise AssertionError("must not execute")

    with pytest.raises(PlanDispatchBindingError, match="selected tool"):
        PlanToolDispatchCoordinator(plan_store, runtime).dispatch_step(
            session,
            dispatch_request(),
            executor,
        )

    assert called["value"] is False
    assert session.step_records[0]["state"] == "todo"
    assert plan_store.outbox_items("RUN_DISPATCH") == ()


def test_completion_gate_seals_head_bound_immutable_result(
    tmp_path: Path,
) -> None:
    goal, plan = compiled_goal_and_plan()
    session = complete_refund_session(plan, run_id="RUN_COMPLETE")
    values = completion_inputs()
    result = finalize_workflow_execution(
        goal,
        session,
        result_id="RESULT_REFUND",
        completed_at=LATER,
        **values,
    )
    validate_workflow_execution_result(result)
    step_b = next(
        item for item in result["step_results"] if item["step_id"] == "STEP_B"
    )
    assert step_b["external_receipts"] == ["PROVIDER_REF_1"]

    store = SqlitePlanExecutionStore(tmp_path / "completion.sqlite")
    head = store.initialize_run(
        goal,
        session,
        checkpoint_id="CHECKPOINT_COMPLETE",
        created_at=LATER,
    )
    store.save_terminal_result(
        result,
        expected_head_hash=head["checkpoint_hash"],
    )
    assert store.run_head("RUN_COMPLETE")["terminal_result_hash"] == result["result_hash"]

    adapter = PlanExecutionEventAdapter(EventStore())
    terminal = adapter.append_completion(
        result,
        plan=plan,
        goal_contract=goal,
    )
    assert terminal.event_type == "run_ended"
    assert terminal.payload["result_binding"]["hash"] == result["result_hash"]

    invalid = completion_inputs()
    invalid["validator_results"] = []
    with pytest.raises(CompletionGateError, match="validator"):
        finalize_workflow_execution(
            goal,
            session,
            result_id="RESULT_BLOCKED",
            completed_at=LATER,
            **invalid,
        )


def test_completion_gate_rejects_mechanical_done_with_unhealthy_probe() -> None:
    goal, plan = compiled_goal_and_plan()
    session = complete_refund_session(plan, run_id="RUN_PROBE_BLOCKED")
    values = completion_inputs()
    values["probe_health"] = {
        "probe_binding": binding("PROBE_PLAN_EXECUTION"),
        "health": "degraded",
        "blocking_findings": 1,
        "checked_at": LATER,
    }
    with pytest.raises(CompletionGateError, match="probe"):
        finalize_workflow_execution(
            goal,
            session,
            result_id="RESULT_PROBE_BLOCKED",
            completed_at=LATER,
            **values,
        )
