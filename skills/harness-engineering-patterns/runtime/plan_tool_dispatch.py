"""Crash-safe Plan-to-Tool Dispatch coordinator / 崩溃安全的计划到工具调度协调器。

This module does not claim cross-database atomicity. It persists a bounded
dispatch intent and the plan checkpoint first, lets ``ToolDispatchRuntime`` own
the real side-effect/idempotency boundary, then atomically records the plan
result and outbox acknowledgement. A crash between phases leaves reconciliation
work and restores writes as UNKNOWN.

/ 本模块不宣称跨数据库原子性。它先持久化有界分派意图与计划检查点，再由
``ToolDispatchRuntime`` 负责真实副作用与幂等边界，最后原子记录计划结果及
Outbox 确认。阶段之间崩溃会留下对账工作，并把写动作恢复为 UNKNOWN。
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

try:  # Package import / 包导入
    from .plan_execution import (
        IdempotencyStatus,
        PlanExecutionSession,
        PlanStateError,
        StepState,
    )
    from .plan_execution_sqlite_store import SqlitePlanExecutionStore
    from .reasoning_artifacts import artifact_fingerprint
    from .tool_dispatch import (
        ExecutionClassification,
        SideEffectClass,
        ToolDispatchRequest,
        ToolDispatchRun,
        ToolDispatchRuntime,
        ToolExecutionReceipt,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from plan_execution import (
        IdempotencyStatus,
        PlanExecutionSession,
        PlanStateError,
        StepState,
    )
    from plan_execution_sqlite_store import SqlitePlanExecutionStore
    from reasoning_artifacts import artifact_fingerprint
    from tool_dispatch import (
        ExecutionClassification,
        SideEffectClass,
        ToolDispatchRequest,
        ToolDispatchRun,
        ToolDispatchRuntime,
        ToolExecutionReceipt,
    )


class PlanDispatchBindingError(PlanStateError):
    """Dispatch input drifted from the active plan / 分派输入偏离当前计划。"""


_PLAN_EFFECTS = {
    "read_only": SideEffectClass.READ_ONLY,
    "reversible_write": SideEffectClass.REVERSIBLE_WRITE,
    "irreversible_external": SideEffectClass.IRREVERSIBLE_EXTERNAL,
}


def _observed_binding(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if value.get("state") != "observed":
        return None
    nested = value.get("value")
    return nested if isinstance(nested, Mapping) else None


def _checkpoint_id(prefix: str, content: Mapping[str, Any]) -> str:
    digest = artifact_fingerprint(content).removeprefix("sha256:")[:24]
    return f"{prefix}_{digest}"


class PlanToolDispatchCoordinator:
    """Coordinate one plan step with the governed tool boundary.

    / 协调一个计划步骤与受治理工具边界。
    """

    def __init__(
        self,
        plan_store: SqlitePlanExecutionStore,
        tool_runtime: ToolDispatchRuntime,
    ) -> None:
        if not getattr(plan_store, "durable", False):
            raise PlanDispatchBindingError(
                "plan dispatch requires a durable plan store / "
                "计划分派需要持久计划存储"
            )
        self.plan_store = plan_store
        self.tool_runtime = tool_runtime

    def dispatch_step(
        self,
        session: PlanExecutionSession,
        request: ToolDispatchRequest,
        executor: Callable[..., ToolExecutionReceipt],
        *,
        completion_evidence: Sequence[str] | None = None,
    ) -> ToolDispatchRun:
        """Persist-before-dispatch, execute once, then persist the outcome.

        / 分派前持久化、执行一次，然后持久化结果。
        """

        step_id = request.intent.node_id
        step, record = self._validate_request(session, request)
        head = self.plan_store.run_head(session.run_id)
        if head is None:
            raise PlanDispatchBindingError(
                "run must be initialized in the plan store / "
                "运行必须先在计划存储中初始化"
            )
        if head["terminal_result_hash"] is not None:
            raise PlanDispatchBindingError(
                "terminal run cannot dispatch / 终态运行不能分派"
            )
        goal_contract, _, _, _ = self.plan_store.load_run(session.run_id)
        permission_boundary = goal_contract["permission_boundary"]
        if (
            request.intent.action_type
            not in set(permission_boundary["allowed_actions"])
            or request.intent.action_type
            in set(permission_boundary["prohibited_actions"])
        ):
            raise PlanDispatchBindingError(
                "tool action is outside the goal permission boundary / "
                "工具动作超出目标权限边界"
            )
        self._validate_tool_binding(
            step,
            self.tool_runtime.coordinator.preview_selected_tool_binding(request),
            required=False,
        )

        if record["state"] == StepState.TODO.value:
            session.start_step(step_id, occurred_at=request.context.created_at)
            record = next(
                item for item in session.step_records if item["step_id"] == step_id
            )
        if record["state"] != StepState.DOING.value:
            raise PlanDispatchBindingError(
                f"{step_id} is not dispatchable from {record['state']} / "
                f"{step_id} 不能从 {record['state']} 分派"
            )

        is_write = step["effect"]["class"] != "read_only"
        if is_write:
            if not getattr(self.tool_runtime.store, "durable", False):
                raise PlanDispatchBindingError(
                    "state-changing dispatch requires durable tool idempotency / "
                    "改状态分派需要持久工具幂等存储"
                )
            claim = session.claim_action(
                step_id,
                request_digest=request.intent.business_action_hash,
                occurred_at=request.context.created_at,
            )
            if claim.disposition in {
                "already_claimed",
                "verify_required",
                "reuse_succeeded",
            }:
                raise PlanDispatchBindingError(
                    f"write action must not be redispatched: {claim.disposition} / "
                    f"写动作不得重新分派：{claim.disposition}"
                )

        outbox_id = (
            "OUTBOX_"
            + artifact_fingerprint(
                {
                    "run_id": session.run_id,
                    "step_id": step_id,
                    "attempt": record["attempt"],
                    "action_id": request.intent.action_id,
                }
            ).removeprefix("sha256:")[:24]
        )
        outbox = {
            "outbox_id": outbox_id,
            "step_id": step_id,
            "attempt": record["attempt"],
            "action_id": request.intent.action_id,
            "intent_hash": request.intent.business_action_hash,
            "payload_binding": request.intent.binding,
        }
        pre_checkpoint = self.plan_store.commit_session(
            session,
            checkpoint_id=_checkpoint_id(
                "CHECKPOINT_PRE_DISPATCH",
                {"outbox_id": outbox_id, "intent": request.intent.binding},
            ),
            expected_head_hash=str(head["head_checkpoint_hash"]),
            outbox_items=(outbox,),
            created_at=request.context.created_at,
        )

        try:
            run = self.tool_runtime.execute(request, executor)
            self._validate_selected_tool(step, run)
            self._apply_result(
                session,
                step_id,
                is_write=is_write,
                run=run,
                completion_evidence=completion_evidence,
            )
        except Exception:
            self._record_boundary_exception(
                session,
                step_id,
                is_write=is_write,
            )
            self.plan_store.commit_session(
                session,
                checkpoint_id=_checkpoint_id(
                    "CHECKPOINT_DISPATCH_UNKNOWN",
                    {"outbox_id": outbox_id, "sequence": session.events[-1]["sequence"]},
                ),
                expected_head_hash=pre_checkpoint["checkpoint_hash"],
                outbox_updates=(
                    {
                        "outbox_id": outbox_id,
                        "status": "unknown",
                        "result_binding": None,
                    },
                ),
            )
            raise

        result_binding = {
            "id": run.result["result_id"],
            "version": run.result["schema_version"],
            "hash": run.result["result_hash"],
        }
        outbox_status = (
            "unknown"
            if run.result["classification"]
            in {
                ExecutionClassification.UNKNOWN.value,
                ExecutionClassification.PARTIAL_SUCCESS.value,
            }
            else "acknowledged"
        )
        self.plan_store.commit_session(
            session,
            checkpoint_id=_checkpoint_id(
                "CHECKPOINT_POST_DISPATCH",
                {
                    "outbox_id": outbox_id,
                    "result_binding": result_binding,
                    "sequence": session.events[-1]["sequence"],
                },
            ),
            expected_head_hash=pre_checkpoint["checkpoint_hash"],
            outbox_updates=(
                {
                    "outbox_id": outbox_id,
                    "status": outbox_status,
                    "result_binding": result_binding,
                },
            ),
            created_at=run.result["execution_completed_at"],
        )
        return run

    @staticmethod
    def _validate_request(
        session: PlanExecutionSession,
        request: ToolDispatchRequest,
    ) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
        intent = request.intent
        steps = {step["step_id"]: step for step in session.plan["steps"]}
        step = steps.get(intent.node_id)
        if step is None:
            raise PlanDispatchBindingError(
                f"unknown plan step {intent.node_id} / 未知计划步骤 {intent.node_id}"
            )
        if step["handler"]["kind"] != "tool":
            raise PlanDispatchBindingError(
                f"{intent.node_id} is not a tool step / "
                f"{intent.node_id} 不是工具步骤"
            )
        expected_version = f"1.0.{session.plan['revision'] - 1}"
        expected = {
            "workflow_id": session.plan["plan_id"],
            "workflow_version": expected_version,
            "run_id": session.run_id,
            "goal_id": session.plan["goal_binding"]["goal_id"],
            "plan_version": expected_version,
        }
        actual = {
            "workflow_id": intent.workflow_id,
            "workflow_version": intent.workflow_version,
            "run_id": intent.run_id,
            "goal_id": intent.goal_id,
            "plan_version": intent.plan_version,
        }
        if actual != expected:
            raise PlanDispatchBindingError(
                "tool intent identity differs from the active plan / "
                "工具意图身份与当前计划不一致"
            )
        effect = _PLAN_EFFECTS[step["effect"]["class"]]
        if (
            intent.expected_side_effect is not effect
            or intent.maximum_side_effect is not effect
            or intent.idempotency_key != step["effect"]["idempotency_key"]
        ):
            raise PlanDispatchBindingError(
                "tool effect contract differs from the plan / "
                "工具副作用契约与计划不一致"
            )
        if request.context.dependencies_satisfied is not True:
            raise PlanDispatchBindingError(
                "dispatch context says dependencies are unsatisfied / "
                "分派上下文声明依赖未满足"
            )
        record = next(
            item for item in session.step_records if item["step_id"] == intent.node_id
        )
        return step, record

    @staticmethod
    def _validate_selected_tool(
        step: Mapping[str, Any],
        run: ToolDispatchRun,
    ) -> None:
        PlanToolDispatchCoordinator._validate_tool_binding(
            step,
            run.result["tool_binding"],
            required=run.envelope["decision"] == "allow",
        )

    @staticmethod
    def _validate_tool_binding(
        step: Mapping[str, Any],
        binding_state: Mapping[str, Any],
        *,
        required: bool,
    ) -> None:
        binding = _observed_binding(binding_state)
        if binding is None:
            if required:
                raise PlanDispatchBindingError(
                    "allowed dispatch lacks a selected tool / "
                    "已放行分派缺少选中工具"
                )
            return
        handler = step["handler"]
        if (
            handler["kind"] != "tool"
            or binding["id"] != handler["ref"]
            or binding["version"] != handler["version"]
        ):
            raise PlanDispatchBindingError(
                "selected tool differs from the plan handler / "
                "选中工具与计划处理器不一致"
            )

    @staticmethod
    def _apply_result(
        session: PlanExecutionSession,
        step_id: str,
        *,
        is_write: bool,
        run: ToolDispatchRun,
        completion_evidence: Sequence[str] | None,
    ) -> None:
        result = run.result
        classification = ExecutionClassification(result["classification"])
        evidence = list(completion_evidence or (result["result_id"],))
        timestamp = result["execution_completed_at"]
        if classification in {
            ExecutionClassification.SUCCESS,
            ExecutionClassification.REUSED_SUCCESS,
        }:
            if is_write:
                receipt = _observed_binding(result["external_receipt_binding"])
                provider_ref = (
                    str(receipt["id"]) if receipt is not None else result["result_id"]
                )
                session.record_action_result(
                    step_id,
                    status=IdempotencyStatus.SUCCEEDED,
                    provider_ref=provider_ref,
                    result_digest=result["result_hash"],
                    occurred_at=timestamp,
                )
            session.complete_step(
                step_id,
                output_digest=result["result_hash"],
                completion_evidence=evidence,
                occurred_at=timestamp,
            )
            return
        if classification in {
            ExecutionClassification.UNKNOWN,
            ExecutionClassification.PARTIAL_SUCCESS,
        }:
            if is_write:
                session.record_action_result(
                    step_id,
                    status=IdempotencyStatus.UNKNOWN,
                    provider_ref=result["result_id"],
                    result_digest=result["result_hash"],
                    occurred_at=timestamp,
                )
            else:
                session.fail_step(
                    step_id,
                    error="read_result_not_certain",
                    occurred_at=timestamp,
                )
            return
        if is_write:
            session.record_action_result(
                step_id,
                status=IdempotencyStatus.FAILED,
                provider_ref=result["result_id"],
                result_digest=result["result_hash"],
                occurred_at=timestamp,
            )
        else:
            session.fail_step(
                step_id,
                error=f"tool_{classification.value}",
                occurred_at=timestamp,
            )

    @staticmethod
    def _record_boundary_exception(
        session: PlanExecutionSession,
        step_id: str,
        *,
        is_write: bool,
    ) -> None:
        record = next(
            item for item in session.step_records if item["step_id"] == step_id
        )
        if record["state"] != StepState.DOING.value:
            return
        if is_write:
            session.record_action_result(
                step_id,
                status=IdempotencyStatus.UNKNOWN,
                provider_ref=None,
                result_digest=None,
            )
        else:
            session.fail_step(step_id, error="dispatch_boundary_exception")


__all__ = [
    "PlanDispatchBindingError",
    "PlanToolDispatchCoordinator",
]
