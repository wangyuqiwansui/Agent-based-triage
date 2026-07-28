"""Terminal completion gate for Plan-and-Execute / 计划并执行终态完成闸门。

The gate is deliberately separate from ``PlanExecutionSession.is_complete``.
Mechanical DONE state is necessary but insufficient: goal evidence, mandatory
validators, probe health, approval freshness, and write receipts must all pass
before a terminal result can be sealed.

/ 本闸门刻意与 ``PlanExecutionSession.is_complete`` 分离。机械 DONE 只是必要条件：
目标证据、必选验证器、探针健康、审批新鲜度以及写动作回执必须全部通过，才能封存
终态结果。
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

try:  # Package import / 包导入
    from .plan_execution import (
        IdempotencyStatus,
        PlanExecutionSession,
        PlanStateError,
        StepState,
        validate_goal_contract,
    )
    from .reasoning_artifacts import (
        ArtifactValidationError,
        build_artifact,
        validate_artifact_hash,
        validate_schema,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from plan_execution import (
        IdempotencyStatus,
        PlanExecutionSession,
        PlanStateError,
        StepState,
        validate_goal_contract,
    )
    from reasoning_artifacts import (
        ArtifactValidationError,
        build_artifact,
        validate_artifact_hash,
        validate_schema,
    )


class CompletionGateError(PlanStateError):
    """The workflow is not safe to declare complete / 工作流尚不能安全宣告完成。"""


def _unique_by(
    items: Sequence[Mapping[str, Any]],
    key: str,
    label: str,
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        value = str(item.get(key, ""))
        if not value:
            raise CompletionGateError(
                f"{label} requires {key} / {label} 必须包含 {key}"
            )
        if value in indexed:
            raise CompletionGateError(
                f"duplicate {label} {value} / 重复的 {label}：{value}"
            )
        indexed[value] = deepcopy(dict(item))
    return indexed


def validate_workflow_execution_result(result: Mapping[str, Any]) -> None:
    """Validate a sealed terminal execution result / 校验已封存终态执行结果。"""

    validate_schema("workflow_execution_result", result)
    validate_artifact_hash("workflow_execution_result", result)


def finalize_workflow_execution(
    goal_contract: Mapping[str, Any],
    session: PlanExecutionSession,
    *,
    result_id: str,
    criterion_results: Sequence[Mapping[str, Any]],
    completion_evidence: Sequence[Mapping[str, Any]],
    validator_results: Sequence[Mapping[str, Any]],
    probe_health: Mapping[str, Any],
    approval_checks: Sequence[Mapping[str, Any]] = (),
    completed_at: str,
) -> dict[str, Any]:
    """Run every release check and seal the terminal result.

    Inputs contain references and hashes only; raw tool parameters, secrets,
    and private reasoning are outside this contract.

    / 执行全部放行检查并封存终态结果。输入只包含引用与哈希；原始工具参数、
    密钥和私密推理均不属于本契约。
    """

    validate_goal_contract(goal_contract)
    expected_goal = {
        "goal_id": goal_contract["goal_id"],
        "version": goal_contract["version"],
        "hash": goal_contract["goal_contract_hash"],
    }
    if session.plan["goal_binding"] != expected_goal:
        raise CompletionGateError(
            "session plan is not bound to the goal contract / "
            "会话计划未绑定目标契约"
        )
    if not session.is_complete():
        unresolved = [
            f"{record['step_id']}:{record['state']}"
            for record in session.step_records
            if record["state"] != StepState.DONE.value
        ]
        raise CompletionGateError(
            "not every step is DONE / 并非所有步骤均为 DONE: "
            + ", ".join(unresolved)
        )

    steps = {step["step_id"]: step for step in session.plan["steps"]}
    ledgers = {
        record["step_id"]: record for record in session.idempotency_records
    }
    for step_id, step in steps.items():
        if step["effect"]["class"] == "read_only":
            continue
        ledger = ledgers.get(step_id)
        if (
            ledger is None
            or ledger["status"] != IdempotencyStatus.SUCCEEDED.value
            or ledger["provider_ref"] is None
            or ledger["result_digest"] is None
        ):
            raise CompletionGateError(
                f"{step_id} lacks a confirmed durable write result / "
                f"{step_id} 缺少已确认的持久写结果"
            )

    criterion_index = _unique_by(
        criterion_results,
        "criterion_id",
        "criterion result / 成功标准结果",
    )
    expected_criteria = {
        criterion["criterion_id"]: criterion
        for criterion in goal_contract["success_criteria"]
    }
    if set(criterion_index) != set(expected_criteria):
        raise CompletionGateError(
            "criterion result inventory differs from the goal / "
            "成功标准结果清单与目标不一致"
        )
    for criterion_id, criterion in expected_criteria.items():
        result = criterion_index[criterion_id]
        if result.get("satisfied") is not True:
            raise CompletionGateError(
                f"{criterion_id} is not satisfied / {criterion_id} 尚未满足"
            )
        evidence_types = {
            str(item.get("evidence_type", ""))
            for item in result.get("evidence", ())
            if isinstance(item, Mapping)
        }
        missing = set(criterion["required_evidence"]) - evidence_types
        if missing:
            raise CompletionGateError(
                f"{criterion_id} lacks evidence types {sorted(missing)} / "
                f"{criterion_id} 缺少证据类型 {sorted(missing)}"
            )

    completion_types = {
        str(item.get("evidence_type", ""))
        for item in completion_evidence
        if isinstance(item, Mapping)
    }
    missing_completion = set(goal_contract["completion_evidence"]) - completion_types
    if missing_completion:
        raise CompletionGateError(
            f"goal completion evidence is missing {sorted(missing_completion)} / "
            f"目标完成证据缺少 {sorted(missing_completion)}"
        )

    if not validator_results:
        raise CompletionGateError(
            "at least one mandatory validator must pass / "
            "至少一个必选验证器必须通过"
        )
    validator_ids: set[str] = set()
    for result in validator_results:
        binding = result.get("validator_binding")
        validator_id = (
            str(binding.get("id", "")) if isinstance(binding, Mapping) else ""
        )
        if not validator_id or validator_id in validator_ids:
            raise CompletionGateError(
                "validator bindings must be non-empty and unique / "
                "验证器绑定必须非空且唯一"
            )
        validator_ids.add(validator_id)
        if result.get("status") != "passed" or not result.get("evidence_refs"):
            raise CompletionGateError(
                f"validator {validator_id} did not pass with evidence / "
                f"验证器 {validator_id} 未携带证据通过"
            )

    if (
        probe_health.get("health") != "healthy"
        or probe_health.get("blocking_findings") != 0
    ):
        raise CompletionGateError(
            "probe health is not release-safe / 探针健康状态不满足放行要求"
        )

    required_approvals = {
        step_id: step["effect"]["approval_binding"]
        for step_id, step in steps.items()
        if step["effect"]["approval_binding"] is not None
    }
    approval_index = _unique_by(
        approval_checks,
        "step_id",
        "approval check / 审批检查",
    )
    if set(approval_index) != set(required_approvals):
        raise CompletionGateError(
            "approval check inventory differs from the plan / "
            "审批检查清单与计划不一致"
        )
    for step_id, expected_binding in required_approvals.items():
        check = approval_index[step_id]
        if check.get("status") != "valid":
            raise CompletionGateError(
                f"{step_id} approval is not current / {step_id} 审批不是当前有效状态"
            )
        if check.get("approval_binding") != expected_binding:
            raise CompletionGateError(
                f"{step_id} approval binding drifted / {step_id} 审批绑定发生漂移"
            )

    step_results = [
        {
            "step_id": record["step_id"],
            "state": record["state"],
            "attempt": record["attempt"],
            "output_digest": record["output_digest"],
            "completion_evidence": list(record["completion_evidence"]),
            "external_receipts": list(record["external_receipts"]),
        }
        for record in session.step_records
    ]
    artifact = {
        "schema_version": "1.0.0",
        "result_id": result_id,
        "run_id": session.run_id,
        "terminal_state": "completed",
        "goal_binding": expected_goal,
        "plan_binding": {
            "plan_id": session.plan["plan_id"],
            "revision": session.plan["revision"],
            "hash": session.plan["plan_hash"],
        },
        "step_results": step_results,
        "criterion_results": [deepcopy(dict(item)) for item in criterion_results],
        "completion_evidence": [
            deepcopy(dict(item)) for item in completion_evidence
        ],
        "validator_results": [
            deepcopy(dict(item)) for item in validator_results
        ],
        "probe_health": deepcopy(dict(probe_health)),
        "approval_checks": [deepcopy(dict(item)) for item in approval_checks],
        "completed_at": completed_at,
    }
    try:
        result = build_artifact("workflow_execution_result", artifact)
        validate_workflow_execution_result(result)
        return result
    except ArtifactValidationError as error:
        raise CompletionGateError(str(error)) from error


__all__ = [
    "CompletionGateError",
    "finalize_workflow_execution",
    "validate_workflow_execution_result",
]
