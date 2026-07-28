"""Behavior tests for recoverable Plan-and-Execute.

可恢复“计划并执行”的行为测试。
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from plan_execution import (  # noqa: E402
    IdempotencyStatus,
    PlanExecutionSession,
    PlanPatchError,
    PlanStateError,
    PlanValidationError,
    compile_goal_contract,
    compile_workflow_plan,
    compile_workflow_plan_patch,
    validate_workflow_checkpoint,
)


NOW = "2026-07-28T08:00:00Z"
LATER = "2026-07-28T08:05:00Z"
HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
HASH_C = "sha256:" + "c" * 64


def binding(identifier: str) -> dict[str, str]:
    return {"id": identifier, "version": "1.0.0", "hash": HASH_A}


def goal_source() -> dict[str, object]:
    return {
        "goal_id": "GOAL_REFUND",
        "version": 1,
        "objective": "Complete one governed refund / 完成一次受治理退款",
        "scope": {
            "in_scope": ["Order ORDER_1 / 订单 ORDER_1"],
            "out_of_scope": ["Any other order / 其他订单"],
        },
        "constraints": [
            {
                "constraint_id": "CONSTRAINT_ONCE",
                "type": "business",
                "statement": "Refund at most once / 最多退款一次",
                "hard": True,
            }
        ],
        "success_criteria": [
            {
                "criterion_id": "CRITERION_RECEIPT",
                "statement": "Provider confirms the refund / 提供方确认退款",
                "required_evidence": ["provider_receipt"],
            }
        ],
        "completion_evidence": ["refund_receipt", "order_state"],
        "recovery_policy": {
            "preserve_done": True,
            "patch_scope": "failed_and_affected_subgraph",
            "unknown_outcome_policy": "verify_before_retry",
            "checkpoint_required": True,
        },
        "permission_boundary": {
            "allowed_actions": ["read_order", "refund_order"],
            "prohibited_actions": ["refund_other_order"],
            "approval_required_for": ["refund_order"],
        },
        "created_at": NOW,
    }


def read_step(
    step_id: str,
    *,
    dependencies: list[str] | None = None,
    description: str | None = None,
) -> dict[str, object]:
    return {
        "step_id": step_id,
        "description": description or f"Read {step_id} / 读取 {step_id}",
        "handler": {
            "kind": "tool",
            "ref": f"TOOL_{step_id}",
            "version": "1.0.0",
        },
        "dependencies": dependencies or [],
        "inputs": ["order_id"],
        "outputs": [f"{step_id}_output"],
        "completion_criteria": [
            {
                "criterion_id": f"CRITERION_{step_id}",
                "statement": "Output is externally observed / 输出可外部观测",
                "evidence_types": ["tool_result"],
            }
        ],
        "checkpoint_required": True,
        "effect": {
            "class": "read_only",
            "idempotency_key": None,
            "compensation": None,
            "approval_binding": None,
        },
    }


def write_step(
    step_id: str,
    *,
    dependencies: list[str] | None = None,
    description: str | None = None,
) -> dict[str, object]:
    return {
        "step_id": step_id,
        "description": description or f"Write {step_id} / 写入 {step_id}",
        "handler": {
            "kind": "tool",
            "ref": f"TOOL_{step_id}",
            "version": "1.0.0",
        },
        "dependencies": dependencies or [],
        "inputs": ["order_id"],
        "outputs": [f"{step_id}_receipt"],
        "completion_criteria": [
            {
                "criterion_id": f"CRITERION_{step_id}",
                "statement": "Provider receipt is confirmed / 提供方回执已确认",
                "evidence_types": ["provider_receipt"],
            }
        ],
        "checkpoint_required": True,
        "effect": {
            "class": "reversible_write",
            "idempotency_key": f"refund:ORDER_1:{step_id}",
            "compensation": {
                "handler": {
                    "kind": "human",
                    "ref": "HUMAN_COMPENSATION",
                    "version": "1.0.0",
                },
                "safety_condition": "Goal owner approves / 目标负责人批准",
            },
            "approval_binding": binding("APPROVAL_REFUND"),
        },
    }


def plan_blueprint() -> dict[str, object]:
    return {
        "plan_id": "PLAN_REFUND",
        "steps": [
            read_step("STEP_A"),
            write_step("STEP_B", dependencies=["STEP_A"]),
            read_step("STEP_C", dependencies=["STEP_B"]),
        ],
        "stop_conditions": {
            "max_replans": 2,
            "max_retries_per_step": 1,
            "deadline_at": None,
        },
        "created_at": NOW,
    }


def compiled_plan() -> dict[str, object]:
    goal = compile_goal_contract(goal_source())
    return compile_workflow_plan(goal, plan_blueprint())


def record_by_id(
    session: PlanExecutionSession,
    step_id: str,
) -> dict[str, object]:
    return next(
        record for record in session.step_records if record["step_id"] == step_id
    )


def complete_read(
    session: PlanExecutionSession,
    step_id: str,
    *,
    digest: str = HASH_A,
) -> None:
    session.start_step(step_id, occurred_at=NOW)
    session.complete_step(
        step_id,
        output_digest=digest,
        completion_evidence=[f"EVIDENCE_{step_id}"],
        occurred_at=LATER,
    )


def test_compile_binds_goal_and_ready_set_is_dependency_aware() -> None:
    plan = compiled_plan()
    session = PlanExecutionSession(plan, run_id="RUN_1", started_at=NOW)

    assert plan["goal_binding"]["goal_id"] == "GOAL_REFUND"
    assert plan["revision"] == 1
    assert session.ready_step_ids() == ("STEP_A",)

    complete_read(session, "STEP_A")

    assert session.ready_step_ids() == ("STEP_B",)
    with pytest.raises(PlanStateError):
        session.start_step("STEP_C")


def test_compile_rejects_cycles_and_unsafe_write_contracts() -> None:
    goal = compile_goal_contract(goal_source())
    cycle = plan_blueprint()
    cycle["steps"][0]["dependencies"] = ["STEP_C"]
    with pytest.raises(PlanValidationError, match="cycle"):
        compile_workflow_plan(goal, cycle)

    unsafe = plan_blueprint()
    unsafe["steps"][1]["effect"]["idempotency_key"] = None
    with pytest.raises(PlanValidationError):
        compile_workflow_plan(goal, unsafe)


def test_write_requires_confirmed_idempotent_result_before_done() -> None:
    session = PlanExecutionSession(compiled_plan(), run_id="RUN_2", started_at=NOW)
    complete_read(session, "STEP_A")
    session.start_step("STEP_B", occurred_at=NOW)

    with pytest.raises(PlanStateError, match="not confirmed"):
        session.complete_step(
            "STEP_B",
            output_digest=HASH_B,
            completion_evidence=["EVIDENCE_PROVIDER"],
        )

    claim = session.claim_action("STEP_B", request_digest=HASH_A)
    assert claim.disposition == "execute"
    session.record_action_result(
        "STEP_B",
        status=IdempotencyStatus.SUCCEEDED,
        provider_ref="PROVIDER_REF_1",
        result_digest=HASH_B,
    )
    session.complete_step(
        "STEP_B",
        output_digest=HASH_B,
        completion_evidence=["EVIDENCE_PROVIDER"],
    )

    assert record_by_id(session, "STEP_B")["state"] == "done"
    assert session.ready_step_ids() == ("STEP_C",)
    assert session.idempotency_records[0]["status"] == "succeeded"


def test_unknown_action_must_verify_and_cannot_be_replayed() -> None:
    session = PlanExecutionSession(compiled_plan(), run_id="RUN_3", started_at=NOW)
    complete_read(session, "STEP_A")
    session.start_step("STEP_B")
    session.claim_action("STEP_B", request_digest=HASH_A)
    session.record_action_result(
        "STEP_B",
        status=IdempotencyStatus.UNKNOWN,
        provider_ref="PROVIDER_PENDING",
        result_digest=None,
    )

    assert record_by_id(session, "STEP_B")["state"] == "unknown"
    assert record_by_id(session, "STEP_C")["state"] == "blocked"
    with pytest.raises(PlanStateError):
        session.claim_action("STEP_B", request_digest=HASH_A)

    session.begin_verification("STEP_B")
    session.resolve_verification(
        "STEP_B",
        confirmed_succeeded=True,
        provider_ref="PROVIDER_CONFIRMED",
        result_digest=HASH_B,
        evidence_refs=["EVIDENCE_RECONCILIATION"],
    )

    assert record_by_id(session, "STEP_B")["state"] == "done"
    assert session.idempotency_records[0]["status"] == "succeeded"
    assert session.ready_step_ids() == ("STEP_C",)


def test_checkpoint_restore_turns_interrupted_write_into_unknown() -> None:
    plan = compiled_plan()
    session = PlanExecutionSession(plan, run_id="RUN_4", started_at=NOW)
    complete_read(session, "STEP_A")
    session.start_step("STEP_B")
    session.claim_action("STEP_B", request_digest=HASH_A)
    checkpoint = session.checkpoint(
        checkpoint_id="CHECKPOINT_1",
        created_at=LATER,
    )
    validate_workflow_checkpoint(checkpoint)

    restored = PlanExecutionSession.from_checkpoint(plan, checkpoint)

    assert record_by_id(restored, "STEP_A")["state"] == "done"
    assert record_by_id(restored, "STEP_B")["state"] == "unknown"
    assert restored.idempotency_records[0]["status"] == "unknown"
    with pytest.raises(PlanStateError):
        restored.start_step("STEP_B")


def test_checkpoint_restore_reuses_confirmed_write_without_redispatch() -> None:
    plan = compiled_plan()
    session = PlanExecutionSession(plan, run_id="RUN_4B", started_at=NOW)
    complete_read(session, "STEP_A")
    session.start_step("STEP_B")
    session.claim_action("STEP_B", request_digest=HASH_A)
    session.record_action_result(
        "STEP_B",
        status=IdempotencyStatus.SUCCEEDED,
        provider_ref="PROVIDER_CONFIRMED",
        result_digest=HASH_B,
    )
    checkpoint = session.checkpoint(
        checkpoint_id="CHECKPOINT_1B",
        created_at=LATER,
    )

    restored = PlanExecutionSession.from_checkpoint(plan, checkpoint)
    claim = restored.claim_action("STEP_B", request_digest=HASH_A)

    assert record_by_id(restored, "STEP_B")["state"] == "doing"
    assert claim.disposition == "reuse_succeeded"
    restored.complete_step(
        "STEP_B",
        output_digest=HASH_B,
        completion_evidence=["EVIDENCE_PROVIDER"],
    )
    assert record_by_id(restored, "STEP_B")["state"] == "done"


def test_local_patch_preserves_done_and_resets_only_affected_subgraph() -> None:
    plan = compiled_plan()
    session = PlanExecutionSession(plan, run_id="RUN_5", started_at=NOW)
    complete_read(session, "STEP_A")
    session.start_step("STEP_B")
    session.claim_action("STEP_B", request_digest=HASH_A)
    session.record_action_result(
        "STEP_B",
        status=IdempotencyStatus.FAILED,
        provider_ref="PROVIDER_REJECTED",
        result_digest=HASH_C,
    )

    assert record_by_id(session, "STEP_B")["state"] == "failed"
    assert record_by_id(session, "STEP_C")["state"] == "blocked"

    replacement_b = write_step(
        "STEP_B",
        dependencies=["STEP_A"],
        description="Retry with corrected parameters / 使用修正参数重试",
    )
    replacement_c = read_step(
        "STEP_C",
        dependencies=["STEP_B"],
        description="Verify corrected refund / 验证修正退款",
    )
    patch = compile_workflow_plan_patch(
        session.plan,
        {
            "patch_id": "PATCH_1",
            "failed_root_step_ids": ["STEP_B"],
            "affected_step_ids": ["STEP_B", "STEP_C"],
            "replacement_steps": [replacement_b, replacement_c],
            "reason": "Provider rejected the original request / 提供方拒绝原请求",
            "evidence_bindings": [binding("EVIDENCE_PROVIDER_REJECTION")],
            "created_at": LATER,
        },
    )
    session.apply_patch(patch, occurred_at=LATER)

    assert session.plan["revision"] == 2
    assert record_by_id(session, "STEP_A")["state"] == "done"
    assert record_by_id(session, "STEP_B")["state"] == "todo"
    assert record_by_id(session, "STEP_C")["state"] == "todo"
    assert session.ready_step_ids() == ("STEP_B",)


def test_patch_rejects_dependency_removal_and_nonfailed_root() -> None:
    plan = compiled_plan()
    bad_step = write_step("STEP_B", dependencies=[])
    with pytest.raises(PlanPatchError, match="remove dependencies"):
        compile_workflow_plan_patch(
            plan,
            {
                "patch_id": "PATCH_BAD",
                "failed_root_step_ids": ["STEP_B"],
                "replacement_steps": [
                    bad_step,
                    read_step("STEP_C", dependencies=["STEP_B"]),
                ],
                "reason": "Unsafe dependency removal / 不安全依赖移除",
                "evidence_bindings": [binding("EVIDENCE_BAD_PATCH")],
                "created_at": LATER,
            },
        )

    session = PlanExecutionSession(plan, run_id="RUN_6", started_at=NOW)
    replacement = [
        deepcopy(step)
        for step in plan["steps"]
    ]
    patch = compile_workflow_plan_patch(
        plan,
        {
            "patch_id": "PATCH_ROOT_NOT_FAILED",
            "failed_root_step_ids": ["STEP_A"],
            "replacement_steps": replacement,
            "reason": "No confirmed failure / 没有已确认失败",
            "evidence_bindings": [binding("EVIDENCE_NONE")],
            "created_at": LATER,
        },
    )
    with pytest.raises(PlanPatchError, match="not FAILED"):
        session.apply_patch(patch)
