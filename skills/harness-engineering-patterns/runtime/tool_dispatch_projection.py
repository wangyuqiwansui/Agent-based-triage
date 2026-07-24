"""Deterministic tool-dispatch observability projection / 确定性工具调度可观测投影。

The projector consumes complete dispatch, result, and event inventories.  It
never turns missing records into zero and never treats an executor success as
goal completion.  Its counters are suitable inputs to the shared metric
registry; anomalies remain evidence-backed diagnostics.

/ 投影器消费完整的调度、结果与事件清单；绝不把缺失记录折叠为零，也不把执行器成功
视为目标完成。其计数可作为共享指标注册表输入；异常保持为有证据的诊断结果。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

try:  # Package import / 包导入
    from .reasoning_artifacts import (
        artifact_fingerprint,
        validate_tool_dispatch_envelope,
        validate_tool_execution_event,
        validate_tool_execution_result,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import (
        artifact_fingerprint,
        validate_tool_dispatch_envelope,
        validate_tool_execution_event,
        validate_tool_execution_result,
    )


TOOL_DISPATCH_PROJECTION_VERSION = "1.0.0"
_WRITE_CLASSES = {
    "reversible_write",
    "sensitive_write",
    "irreversible_external",
}
_APPROVAL_CLASSES = {"sensitive_write", "irreversible_external"}
_RESULT_EVENT_TYPES = {
    "tool_execution_succeeded",
    "tool_result_reused",
    "tool_execution_rejected",
    "tool_execution_failed",
    "tool_execution_unknown",
    "tool_execution_partial",
    "tool_execution_waiting",
}


class ToolDispatchProjectionError(ValueError):
    """Projection input is incomplete or contradictory / 投影输入不完整或矛盾。"""


@dataclass(frozen=True)
class ToolDispatchAnomaly:
    """One evidence-backed dispatch anomaly / 一条有证据的调度异常。"""

    code: str
    severity: str
    run_id: str
    action_id: str | None
    evidence_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "run_id": self.run_id,
            "action_id": self.action_id,
            "evidence_ids": list(self.evidence_ids),
        }


@dataclass(frozen=True)
class ToolDispatchProjection:
    """Bounded reconstructed view and metric inputs / 有界重建视图与指标输入。"""

    projection_version: str
    run_id: str
    action_count: int
    metric_inputs: Mapping[str, int]
    anomalies: tuple[ToolDispatchAnomaly, ...]
    projection_hash: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "projection_version": self.projection_version,
            "run_id": self.run_id,
            "action_count": self.action_count,
            "metric_inputs": dict(self.metric_inputs),
            "anomalies": [item.as_dict() for item in self.anomalies],
            "projection_hash": self.projection_hash,
        }


def _observed_binding(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    nested = value.get("value")
    return nested if value.get("state") == "observed" and isinstance(nested, Mapping) else None


def _binding_key(binding: Mapping[str, Any] | None) -> tuple[Any, Any, Any] | None:
    if binding is None:
        return None
    return binding.get("id"), binding.get("version"), binding.get("hash")


def _check_status(envelope: Mapping[str, Any], name: str) -> str:
    return next(
        item["status"]
        for item in envelope["admission_checks"]
        if item["name"] == name
    )


def project_tool_dispatch_run(
    envelopes: Sequence[Mapping[str, Any]],
    results: Sequence[Mapping[str, Any]],
    events: Sequence[Mapping[str, Any]],
) -> ToolDispatchProjection:
    """Reconstruct one run from complete immutable inventories.

    / 从完整不可变清单重建一次运行。
    """

    if not envelopes:
        raise ToolDispatchProjectionError(
            "dispatch envelope inventory cannot be empty / 调度信封清单不能为空"
        )
    detached_envelopes = [deepcopy(dict(item)) for item in envelopes]
    detached_results = [deepcopy(dict(item)) for item in results]
    detached_events = [deepcopy(dict(item)) for item in events]
    for envelope in detached_envelopes:
        validate_tool_dispatch_envelope(envelope)
    for result in detached_results:
        validate_tool_execution_result(result)
    for event in detached_events:
        validate_tool_execution_event(event)

    run_ids = {
        str(item["run_id"])
        for item in (*detached_envelopes, *detached_results, *detached_events)
    }
    if len(run_ids) != 1:
        raise ToolDispatchProjectionError(
            "projection inputs must belong to one run / 投影输入必须属于同一次运行"
        )
    run_id = next(iter(run_ids))
    envelope_by_id: dict[str, dict[str, Any]] = {}
    envelope_by_action: dict[str, dict[str, Any]] = {}
    for envelope in detached_envelopes:
        if envelope["dispatch_id"] in envelope_by_id:
            raise ToolDispatchProjectionError("duplicate dispatch_id")
        if envelope["action_id"] in envelope_by_action:
            raise ToolDispatchProjectionError(
                "one action may have only one dispatch envelope / 一个行动只能有一个调度信封"
            )
        envelope_by_id[envelope["dispatch_id"]] = envelope
        envelope_by_action[envelope["action_id"]] = envelope

    result_by_id: dict[str, dict[str, Any]] = {}
    result_by_action: dict[str, dict[str, Any]] = {}
    for result in detached_results:
        if result["result_id"] in result_by_id:
            raise ToolDispatchProjectionError("duplicate result_id")
        if result["action_id"] in result_by_action:
            raise ToolDispatchProjectionError(
                "one action may have only one terminal result / 一个行动只能有一个终态结果"
            )
        dispatch = envelope_by_id.get(result["dispatch_binding"]["id"])
        if dispatch is None or result["dispatch_binding"]["hash"] != dispatch["dispatch_hash"]:
            raise ToolDispatchProjectionError(
                "result dispatch binding cannot resolve / 结果调度绑定不可解析"
            )
        result_by_id[result["result_id"]] = result
        result_by_action[result["action_id"]] = result

    ordered_events = sorted(detached_events, key=lambda item: item["sequence"])
    sequences = [item["sequence"] for item in ordered_events]
    anomalies: list[ToolDispatchAnomaly] = []
    if sequences != list(range(1, len(sequences) + 1)):
        anomalies.append(
            ToolDispatchAnomaly(
                "EVENT_SEQUENCE_GAP",
                "warning",
                run_id,
                None,
                tuple(item["event_id"] for item in ordered_events),
            )
        )
    event_keys = [item["event_key"] for item in ordered_events]
    if len(event_keys) != len(set(event_keys)):
        raise ToolDispatchProjectionError(
            "event inventory contains duplicate keys / 事件清单包含重复键"
        )

    events_by_action: dict[str, list[dict[str, Any]]] = {
        action_id: [] for action_id in envelope_by_action
    }
    for event in ordered_events:
        action_id = event["action_id"]
        if action_id not in events_by_action:
            anomalies.append(
                ToolDispatchAnomaly(
                    "ORPHAN_EVENT",
                    "warning",
                    run_id,
                    action_id,
                    (event["event_id"],),
                )
            )
            continue
        dispatch_binding = _observed_binding(event["dispatch_binding"])
        envelope = envelope_by_action[action_id]
        if (
            dispatch_binding is None
            or dispatch_binding["id"] != envelope["dispatch_id"]
            or dispatch_binding["hash"] != envelope["dispatch_hash"]
        ):
            anomalies.append(
                ToolDispatchAnomaly(
                    "EVENT_DISPATCH_BINDING_MISMATCH",
                    "severe",
                    run_id,
                    action_id,
                    (event["event_id"], envelope["dispatch_id"]),
                )
            )
        events_by_action[action_id].append(event)

    execution_starts = 0
    executions_with_valid_admission = 0
    side_effecting_execution_starts = 0
    side_effecting_executions_with_valid_lease = 0
    write_executions_requiring_state_evidence = 0
    write_executions_with_current_state_evidence = 0
    approval_required_execution_starts = 0
    approval_bound_execution_starts = 0
    frontier_escape_executions = 0
    dispatch_records = len(detached_envelopes)
    complete_dispatch_records = 0
    executed_results = 0
    unknown_results = 0
    confirmed_side_effect_results = 0
    confirmed_by_idempotency: dict[tuple[Any, Any, Any], int] = {}

    for action_id, envelope in envelope_by_action.items():
        action_events = events_by_action[action_id]
        event_types = {item["event_type"] for item in action_events}
        starts = [
            item for item in action_events if item["event_type"] == "tool_execution_started"
        ]
        result_events = [
            item for item in action_events if item["event_type"] in _RESULT_EVENT_TYPES
        ]
        result = result_by_action.get(action_id)
        if (
            {"capability_frontier_built", "candidate_selection_completed", "execution_admission_completed"}
            <= event_types
            and len(result_events) == 1
            and result is not None
        ):
            complete_dispatch_records += 1
        else:
            evidence = tuple(
                [envelope["dispatch_id"]]
                + [item["event_id"] for item in action_events]
            )
            anomalies.append(
                ToolDispatchAnomaly(
                    "INCOMPLETE_DISPATCH_RECORD",
                    "warning",
                    run_id,
                    action_id,
                    evidence,
                )
            )

        if len(starts) > 1:
            anomalies.append(
                ToolDispatchAnomaly(
                    "MULTIPLE_EXECUTION_STARTS",
                    "emergency",
                    run_id,
                    action_id,
                    tuple(item["event_id"] for item in starts),
                )
            )
        if starts:
            execution_starts += len(starts)
            if envelope["decision"] == "allow":
                executions_with_valid_admission += len(starts)
            else:
                anomalies.append(
                    ToolDispatchAnomaly(
                        "EXECUTION_WITHOUT_ALLOW",
                        "emergency",
                        run_id,
                        action_id,
                        tuple(
                            [envelope["dispatch_id"]]
                            + [item["event_id"] for item in starts]
                        ),
                    )
                )
            selected = _observed_binding(envelope["selected_tool_binding"])
            retained = {
                _binding_key(item)
                for item in envelope["frontier"]["retained_tool_bindings"]
            }
            if _binding_key(selected) not in retained:
                frontier_escape_executions += len(starts)
                anomalies.append(
                    ToolDispatchAnomaly(
                        "FRONTIER_ESCAPE_EXECUTION",
                        "emergency",
                        run_id,
                        action_id,
                        tuple(item["event_id"] for item in starts),
                    )
                )
            side_effect_class = envelope["execution_contract"]["side_effect_class"]
            if side_effect_class in _WRITE_CLASSES:
                side_effecting_execution_starts += len(starts)
                write_executions_requiring_state_evidence += len(starts)
                if _check_status(envelope, "state_evidence") == "passed":
                    write_executions_with_current_state_evidence += len(starts)
                for start in starts:
                    if _observed_binding(start["lease_binding"]) is not None:
                        side_effecting_executions_with_valid_lease += 1
                    else:
                        anomalies.append(
                            ToolDispatchAnomaly(
                                "WRITE_EXECUTION_WITHOUT_LEASE",
                                "emergency",
                                run_id,
                                action_id,
                                (start["event_id"],),
                            )
                        )
            if side_effect_class in _APPROVAL_CLASSES:
                approval_required_execution_starts += len(starts)
                if _check_status(envelope, "approval") == "passed":
                    approval_bound_execution_starts += len(starts)

        if result is None:
            continue
        if result["classification"] in {
            "success",
            "explicit_failure",
            "unknown",
            "partial_success",
        }:
            executed_results += 1
        if result["classification"] == "unknown":
            unknown_results += 1
        if (
            result["side_effect_state"] == "confirmed"
            and result["classification"] in {"success", "reused_success"}
        ):
            confirmed_side_effect_results += 1
            idempotency = _observed_binding(
                envelope["execution_contract"]["idempotency_binding"]
            )
            if idempotency is not None and result["classification"] == "success":
                key = _binding_key(idempotency)
                assert key is not None
                confirmed_by_idempotency[key] = confirmed_by_idempotency.get(key, 0) + 1

    duplicate_side_effects = sum(
        max(0, count - 1) for count in confirmed_by_idempotency.values()
    )
    if duplicate_side_effects:
        anomalies.append(
            ToolDispatchAnomaly(
                "DUPLICATE_CONFIRMED_SIDE_EFFECT",
                "emergency",
                run_id,
                None,
                tuple(
                    str(key[0])
                    for key, count in confirmed_by_idempotency.items()
                    if count > 1
                ),
            )
        )

    metric_inputs = {
        "executions_with_valid_admission": executions_with_valid_admission,
        "execution_starts": execution_starts,
        "side_effecting_executions_with_valid_lease": side_effecting_executions_with_valid_lease,
        "side_effecting_execution_starts": side_effecting_execution_starts,
        "write_executions_with_current_state_evidence": write_executions_with_current_state_evidence,
        "write_executions_requiring_state_evidence": write_executions_requiring_state_evidence,
        "approval_bound_execution_starts": approval_bound_execution_starts,
        "approval_required_execution_starts": approval_required_execution_starts,
        "frontier_escape_executions": frontier_escape_executions,
        "complete_dispatch_records": complete_dispatch_records,
        "dispatch_records": dispatch_records,
        "unknown_results": unknown_results,
        "executed_results": executed_results,
        "duplicate_side_effects": duplicate_side_effects,
        "confirmed_side_effect_results": confirmed_side_effect_results,
    }
    content = {
        "projection_version": TOOL_DISPATCH_PROJECTION_VERSION,
        "run_id": run_id,
        "action_count": len(envelope_by_action),
        "metric_inputs": metric_inputs,
        "anomalies": [item.as_dict() for item in anomalies],
        "source_bindings": {
            "dispatches": [
                {
                    "id": item["dispatch_id"],
                    "version": item["schema_version"],
                    "hash": item["dispatch_hash"],
                }
                for item in detached_envelopes
            ],
            "results": [
                {
                    "id": item["result_id"],
                    "version": item["schema_version"],
                    "hash": item["result_hash"],
                }
                for item in detached_results
            ],
            "events": [
                {
                    "id": item["event_id"],
                    "version": item["event_version"],
                    "hash": item["event_hash"],
                }
                for item in ordered_events
            ],
        },
    }
    return ToolDispatchProjection(
        projection_version=TOOL_DISPATCH_PROJECTION_VERSION,
        run_id=run_id,
        action_count=len(envelope_by_action),
        metric_inputs=metric_inputs,
        anomalies=tuple(anomalies),
        projection_hash=artifact_fingerprint(content),
    )


__all__ = [
    "TOOL_DISPATCH_PROJECTION_VERSION",
    "ToolDispatchAnomaly",
    "ToolDispatchProjection",
    "ToolDispatchProjectionError",
    "project_tool_dispatch_run",
]
