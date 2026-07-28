"""Observability adapter for Plan-and-Execute / 计划并执行可观测性适配器。

Plan lifecycle and step closure are projected into the shared
``reasoning-event`` contract. Governed tool execution remains in the stricter
``tool-execution-event`` contract because shared reasoning tool events are
intentionally read-only. Both streams are returned as one adapter batch.

/ 计划生命周期与步骤闭环被投影到共享 ``reasoning-event`` 契约。受治理工具执行
仍保留在更严格的 ``tool-execution-event`` 契约中，因为共享推理工具事件被刻意
限制为只读。适配器会在一个批次中返回两条事件流。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

try:  # Package import / 包导入
    from .plan_execution import StepState, validate_goal_contract, validate_workflow_plan
    from .reasoning_artifacts import (
        artifact_fingerprint,
        validate_reasoning_event,
        validate_tool_execution_event,
    )
    from .plan_execution_completion import validate_workflow_execution_result
    from .reasoning_runtime import EventStore, ReasoningEvent, WorkflowState
    from .tool_dispatch import ToolDispatchRun
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from plan_execution import StepState, validate_goal_contract, validate_workflow_plan
    from reasoning_artifacts import (
        artifact_fingerprint,
        validate_reasoning_event,
        validate_tool_execution_event,
    )
    from plan_execution_completion import validate_workflow_execution_result
    from reasoning_runtime import EventStore, ReasoningEvent, WorkflowState
    from tool_dispatch import ToolDispatchRun


@dataclass(frozen=True)
class PlanObservabilityBatch:
    """Validated dual-stream adapter output / 已校验双流适配输出。"""

    reasoning_events: tuple[ReasoningEvent, ...]
    tool_events: tuple[Mapping[str, Any], ...]
    unmapped_event_types: tuple[str, ...]


def _binding(identifier: str, revision: int, digest: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "version": f"1.0.{revision - 1}",
        "hash": digest,
    }


def _resource_use() -> dict[str, Any]:
    return {
        name: {"state": "not_applicable"}
        for name in (
            "reasoning_tokens",
            "latency_ms",
            "model_calls",
            "tool_calls",
            "parallel_paths",
            "iterations",
            "retries",
            "total_cost_units",
        )
    }


class PlanExecutionEventAdapter:
    """Idempotently project plan records into normative observability events.

    / 将计划记录幂等投影为规范可观测事件。
    """

    def __init__(self, event_store: EventStore) -> None:
        self.event_store = event_store

    def append_plan_events(
        self,
        events: Sequence[Mapping[str, Any]],
        *,
        plan: Mapping[str, Any],
        goal_contract: Mapping[str, Any],
        step_records: Sequence[Mapping[str, Any]],
        tool_run: ToolDispatchRun | None = None,
    ) -> PlanObservabilityBatch:
        """Append mapped events and validate an optional tool stream.

        / 追加映射事件并校验可选工具事件流。
        """

        validate_workflow_plan(plan)
        validate_goal_contract(goal_contract)
        if plan["goal_binding"] != {
            "goal_id": goal_contract["goal_id"],
            "version": goal_contract["version"],
            "hash": goal_contract["goal_contract_hash"],
        }:
            raise ValueError(
                "goal and plan binding mismatch / 目标与计划绑定不一致"
            )
        records = {
            str(record["step_id"]): deepcopy(dict(record))
            for record in step_records
        }
        steps = {str(step["step_id"]): step for step in plan["steps"]}
        projected: list[ReasoningEvent] = []
        unmapped: set[str] = set()
        for internal in sorted(events, key=lambda item: int(item["sequence"])):
            specs = self._specs_for(
                internal,
                plan=plan,
                goal_contract=goal_contract,
                steps=steps,
                records=records,
            )
            if not specs:
                unmapped.add(str(internal["event_type"]))
                continue
            for suffix, spec in specs:
                projected.append(
                    self._append_one(
                        internal,
                        suffix=suffix,
                        plan=plan,
                        goal_contract=goal_contract,
                        **spec,
                    )
                )

        tool_events: tuple[Mapping[str, Any], ...] = ()
        if tool_run is not None:
            detached = tuple(deepcopy(dict(event)) for event in tool_run.events)
            for event in detached:
                validate_tool_execution_event(event)
            tool_events = detached
        return PlanObservabilityBatch(
            tuple(projected),
            tool_events,
            tuple(sorted(unmapped)),
        )

    def append_completion(
        self,
        result: Mapping[str, Any],
        *,
        plan: Mapping[str, Any],
        goal_contract: Mapping[str, Any],
    ) -> ReasoningEvent:
        """Append the normative terminal event / 追加规范终态事件。"""

        validate_workflow_execution_result(result)
        synthetic = {
            "sequence": 0,
            "event_type": "workflow_completed",
            "run_id": result["run_id"],
            "occurred_at": result["completed_at"],
        }
        return self._append_one(
            synthetic,
            suffix="terminal",
            plan=plan,
            goal_contract=goal_contract,
            event_type="run_ended",
            state=WorkflowState.COMPLETED,
            payload={
                "terminal_state": "completed",
                "reason_code": "plan_completion_gate_passed",
                "result_binding": {
                    "id": result["result_id"],
                    "version": result["schema_version"],
                    "hash": result["result_hash"],
                },
            },
            step_id=None,
            previous_state=None,
            next_state=None,
            transition_id=None,
        )

    def _append_one(
        self,
        internal: Mapping[str, Any],
        *,
        suffix: str,
        plan: Mapping[str, Any],
        goal_contract: Mapping[str, Any],
        event_type: str,
        state: WorkflowState,
        payload: Mapping[str, Any],
        step_id: str | None,
        previous_state: WorkflowState | None,
        next_state: WorkflowState | None,
        transition_id: str | None,
    ) -> ReasoningEvent:
        identity = {
            "run_id": internal["run_id"],
            "plan_event_sequence": internal["sequence"],
            "event_type": event_type,
            "suffix": suffix,
        }
        digest = artifact_fingerprint(identity).removeprefix("sha256:")[:24]
        event_id = f"PLANOBS_{digest}"
        idempotency_key = f"plan-observability:{digest}"
        existing = self.event_store.find_idempotency(
            str(internal["run_id"]),
            idempotency_key,
        )
        if existing is not None:
            return existing
        current = self.event_store.events(str(internal["run_id"]))
        parent = current[-1].event_id if current else None
        maximum_effect = {
            "read_only": 0,
            "reversible_write": 1,
            "irreversible_external": 2,
        }
        risk = (
            "critical"
            if max(
                maximum_effect[step["effect"]["class"]]
                for step in plan["steps"]
            )
            == 2
            else "medium"
        )
        event = self.event_store.append(
            run_id=str(internal["run_id"]),
            event_type=event_type,
            state=state,
            payload=payload,
            event_id=event_id,
            idempotency_key=idempotency_key,
            timestamp=str(internal["occurred_at"]),
            task_id=f"TASK_{goal_contract['goal_id']}",
            workflow_id=str(plan["plan_id"]),
            step_id=step_id,
            attempt_id=f"ATTEMPT_{digest}",
            causation_id=parent,
            parent_event_id=parent,
            contract_binding=_binding(
                str(goal_contract["goal_id"]),
                int(goal_contract["version"]),
                str(goal_contract["goal_contract_hash"]),
            ),
            scene_id="PLAN_EXECUTION",
            risk_level=risk,
            reasoning_depth="deliberative",
            execution_mode="chain",
            primary_topology="chain",
            supporting_topologies=("orchestration",),
            snapshot_versions={
                "goal": int(goal_contract["version"]),
                "constraints": int(goal_contract["version"]),
                "verified_facts": int(plan["revision"]),
            },
            previous_state=previous_state,
            next_state=next_state,
            transition_id=transition_id,
        )
        validate_reasoning_event(event.as_dict())
        return event

    def _specs_for(
        self,
        internal: Mapping[str, Any],
        *,
        plan: Mapping[str, Any],
        goal_contract: Mapping[str, Any],
        steps: Mapping[str, Mapping[str, Any]],
        records: Mapping[str, Mapping[str, Any]],
    ) -> list[tuple[str, dict[str, Any]]]:
        event_type = str(internal["event_type"])
        payload = internal.get("payload", {})
        if event_type == "run_created":
            return [
                (
                    "run",
                    {
                        "event_type": "run_created",
                        "state": WorkflowState.EXECUTING,
                        "payload": {
                            "normalized_input_binding": _binding(
                                str(goal_contract["goal_id"]),
                                int(goal_contract["version"]),
                                str(goal_contract["goal_contract_hash"]),
                            )
                        },
                        "step_id": None,
                        "previous_state": None,
                        "next_state": None,
                        "transition_id": None,
                    },
                )
            ]
        if event_type == "step_started":
            step_id = str(payload["step_id"])
            return [
                (
                    "step-started",
                    {
                        "event_type": "step_started",
                        "state": WorkflowState.EXECUTING,
                        "payload": self._step_record(
                            steps[step_id],
                            records[step_id],
                            plan=plan,
                            event=internal,
                            status="running",
                            attempt=int(payload["attempt"]),
                        ),
                        "step_id": step_id,
                        "previous_state": None,
                        "next_state": None,
                        "transition_id": None,
                    },
                )
            ]
        if event_type == "step_closed":
            step_id = str(payload["step_id"])
            state = str(payload["state"])
            return [
                (
                    "step-closed",
                    {
                        "event_type": "step_closed",
                        "state": (
                            WorkflowState.EXECUTING
                            if state == StepState.DONE.value
                            else WorkflowState.REPAIRABLE_FAILURE
                        ),
                        "payload": self._step_record(
                            steps[step_id],
                            records[step_id],
                            plan=plan,
                            event=internal,
                            status=(
                                "completed"
                                if state == StepState.DONE.value
                                else "failed"
                            ),
                            attempt=int(records[step_id]["attempt"]),
                        ),
                        "step_id": step_id,
                        "previous_state": None,
                        "next_state": None,
                        "transition_id": None,
                    },
                )
            ]
        if (
            event_type == "action_result_recorded"
            and payload.get("status") == "unknown"
        ):
            return [
                self._transition(
                    internal,
                    "unknown",
                    WorkflowState.EXECUTING,
                    WorkflowState.WAITING_FOR_EVIDENCE,
                    "write_outcome_unknown",
                )
            ]
        if event_type == "verification_started":
            return [
                self._transition(
                    internal,
                    "verification-started",
                    WorkflowState.WAITING_FOR_EVIDENCE,
                    WorkflowState.VALIDATING,
                    "side_effect_reconciliation_started",
                )
            ]
        if event_type == "verification_completed":
            succeeded = payload.get("confirmed_succeeded") is True
            step_id = str(payload["step_id"])
            transition = self._transition(
                internal,
                "verification-completed",
                WorkflowState.VALIDATING,
                (
                    WorkflowState.EXECUTING
                    if succeeded
                    else WorkflowState.REPAIRABLE_FAILURE
                ),
                (
                    "side_effect_reconciliation_succeeded"
                    if succeeded
                    else "side_effect_reconciliation_failed"
                ),
            )
            closure = (
                "verification-step-closed",
                {
                    "event_type": "step_closed",
                    "state": (
                        WorkflowState.EXECUTING
                        if succeeded
                        else WorkflowState.REPAIRABLE_FAILURE
                    ),
                    "payload": self._step_record(
                        steps[step_id],
                        records[step_id],
                        plan=plan,
                        event=internal,
                        status="completed" if succeeded else "failed",
                        attempt=int(records[step_id]["attempt"]),
                    ),
                    "step_id": step_id,
                    "previous_state": None,
                    "next_state": None,
                    "transition_id": None,
                },
            )
            return [transition, closure]
        if event_type == "plan_patched":
            return [
                self._transition(
                    internal,
                    "plan-patched",
                    WorkflowState.REPAIRABLE_FAILURE,
                    WorkflowState.EXECUTING,
                    "local_plan_patch_applied",
                )
            ]
        return []

    @staticmethod
    def _transition(
        internal: Mapping[str, Any],
        suffix: str,
        previous: WorkflowState,
        next_state: WorkflowState,
        reason_code: str,
    ) -> tuple[str, dict[str, Any]]:
        transition_id = (
            "TRANSITION_"
            + artifact_fingerprint(
                {
                    "run_id": internal["run_id"],
                    "sequence": internal["sequence"],
                    "suffix": suffix,
                }
            ).removeprefix("sha256:")[:24]
        )
        return (
            suffix,
            {
                "event_type": "state_transitioned",
                "state": next_state,
                "payload": {
                    "from_state": previous.value,
                    "to_state": next_state.value,
                    "reason_code": reason_code,
                },
                "step_id": None,
                "previous_state": previous,
                "next_state": next_state,
                "transition_id": transition_id,
            },
        )

    @staticmethod
    def _step_record(
        step: Mapping[str, Any],
        record: Mapping[str, Any],
        *,
        plan: Mapping[str, Any],
        event: Mapping[str, Any],
        status: str,
        attempt: int,
    ) -> dict[str, Any]:
        contract_binding = _binding(
            str(plan["plan_id"]),
            int(plan["revision"]),
            str(plan["plan_hash"]),
        )
        input_bindings = []
        for dependency in step["dependencies"]:
            # Dependency evidence is bound by the declared input edge. The
            # detailed digest remains in the plan checkpoint.
            # / 依赖证据由声明的输入边绑定；详细摘要保留在计划检查点中。
            input_bindings.append(
                {
                    "id": f"STEP_OUTPUT_{dependency}",
                    "version": "1.0.0",
                    "hash": artifact_fingerprint(
                        {"dependency_step_id": dependency}
                    ),
                }
            )
        output_bindings = [
            {
                "id": evidence_ref,
                "version": "1.0.0",
                "hash": artifact_fingerprint({"evidence_ref": evidence_ref}),
            }
            for evidence_ref in record["completion_evidence"]
        ]
        result = {
            "step_id": step["step_id"],
            "step_version": f"1.0.{plan['revision'] - 1}",
            "step_hash": artifact_fingerprint(step),
            "contract_binding": contract_binding,
            "sequence_number": int(event["sequence"]),
            "attempt_number": attempt,
            "status": status,
            "summary": step["description"],
            "input_evidence_bindings": input_bindings,
            "output_evidence_bindings": output_bindings,
            "validation_bindings": [],
            "started_at": record["started_at"] or event["occurred_at"],
        }
        if status in {"completed", "failed"}:
            result.update(
                {
                    "claim": {
                        "criterion_ids": [
                            criterion["criterion_id"]
                            for criterion in step["completion_criteria"]
                        ]
                    },
                    "evidence_refs": list(record["completion_evidence"]),
                    "action": {"handler": deepcopy(dict(step["handler"]))},
                    "observation": {
                        "output_digest": record["output_digest"],
                        "error": record["error"],
                    },
                    "local_decision": {"step_state": record["state"]},
                    "resource_use": _resource_use(),
                    "progress": status == "completed",
                    "ended_at": event["occurred_at"],
                }
            )
        return result


__all__ = [
    "PlanExecutionEventAdapter",
    "PlanObservabilityBatch",
]
