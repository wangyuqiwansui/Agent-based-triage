"""Harness-level workflow route coordinator / Harness 层工作流路由协调器。

This module binds one task atom, workflow/action gates, and the deterministic
reasoning subroute into a strict workflow-route envelope. Reasoning execution
never authorizes a side effect. / 本模块将一个任务原子、工作流/行动门禁与确定性
推理子路由绑定为严格的工作流路由信封；推理执行绝不授权副作用。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

try:  # Package import / 包导入
    from .reasoning_artifacts import (
        artifact_fingerprint,
        build_artifact,
        workflow_signal_fingerprint,
    )
    from .reasoning_router import (
        EvidenceState,
        IntentComplexity,
        MechanismUncertainty,
        RiskLevel,
        RouteDecision,
        RouteDisposition,
        RoutingPolicy,
        RoutingSignals,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import (
        artifact_fingerprint,
        build_artifact,
        workflow_signal_fingerprint,
    )
    from reasoning_router import (
        EvidenceState,
        IntentComplexity,
        MechanismUncertainty,
        RiskLevel,
        RouteDecision,
        RouteDisposition,
        RoutingPolicy,
        RoutingSignals,
    )


WORKFLOW_ROUTE_SCHEMA_VERSION = "1.0.0"
WORKFLOW_ROUTE_POLICY_ID = "WORKFLOW_ROUTE_DEFAULT"
WORKFLOW_ROUTE_POLICY_VERSION = "1.0.0"
WORKFLOW_SIGNAL_ADAPTER_ID = "WORKFLOW_TO_REASONING_SIGNAL_ADAPTER"
WORKFLOW_SIGNAL_ADAPTER_VERSION = "1.0.0"

_SIGNAL_ORDER = (
    "task_intent",
    "evidence_state",
    "mechanical_state",
    "action_risk",
    "intent_complexity",
    "mechanism_uncertainty",
    "environment_interaction_required",
    "material_rivals_present",
    "dominant_dependency_path",
    "permission_granted",
    "prohibited_action",
    "irreversible_action",
    "strong_validation_available",
    "accountable_owner_present",
    "approval_state",
)

_WORKFLOW_POLICY_MANIFEST = (
    "unknown_task_intent:clarification_human_review",
    "query:direct_answer",
    "read_only_analysis:read_only_analysis",
    "structured_judgment:structured_judgment",
    "draft:structured_judgment",
    "business_action:planned_execution",
    "missing_or_unknown_critical_signal:block",
    "write_action_requires_mechanical_permission_owner_validation_and_approval",
    "reasoning_execute_never_implies_action_allowed",
)

_ADAPTER_MANIFEST = {
    "intent_complexity": "intent_complexity",
    "evidence_state": "evidence_state",
    "mechanism_uncertainty": "mechanism_uncertainty",
    "risk_level": "derived_from_action_risk",
    "environment_interaction_required": "environment_interaction_required",
    "material_rivals_present": "material_rivals_present",
    "dominant_dependency_path": "dominant_dependency_path",
    "permission_granted": "permission_granted",
    "prohibited_action": "prohibited_action",
    "irreversible_action": "irreversible_action",
    "strong_validation_available": "strong_validation_available",
}


class WorkflowRouteError(ValueError):
    """The workflow route request violates a fail-closed invariant.

    / 工作流路由请求违反默认阻断不变量。
    """


class SignalState(str, Enum):
    """Explicit workflow signal state / 显式工作流信号状态。"""

    OBSERVED = "observed"
    MISSING = "missing"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class TaskIntent(str, Enum):
    """One primary business intent per task atom / 每个任务原子的唯一主业务意图。"""

    QUERY = "query"
    READ_ONLY_ANALYSIS = "read_only_analysis"
    STRUCTURED_JUDGMENT = "structured_judgment"
    DRAFT = "draft"
    BUSINESS_ACTION = "business_action"


class ExecutionLane(str, Enum):
    """Business execution lane, separate from reasoning topology / 与推理拓扑分离的业务车道。"""

    DIRECT_ANSWER = "direct_answer"
    READ_ONLY_ANALYSIS = "read_only_analysis"
    STRUCTURED_JUDGMENT = "structured_judgment"
    PLANNED_EXECUTION = "planned_execution"
    CLARIFICATION_HUMAN_REVIEW = "clarification_human_review"


class MechanicalState(str, Enum):
    """External action readiness / 外部行动机械就绪状态。"""

    READY = "ready"
    BLOCKED = "blocked"


class ActionRisk(str, Enum):
    """Action-risk class independent from reasoning depth / 独立于推理深度的行动风险类别。"""

    READ_ONLY = "read_only"
    DRAFT = "draft"
    REVERSIBLE_WRITE = "reversible_write"
    SENSITIVE_WRITE = "sensitive_write"
    IRREVERSIBLE_EXTERNAL_ACTION = "irreversible_external_action"


class ApprovalState(str, Enum):
    """Authoritative approval state / 权威审批状态。"""

    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


def _detached(value: Mapping[str, Any]) -> dict[str, Any]:
    return deepcopy(dict(value))


def _binding(identifier: str, version: str, content: Mapping[str, Any]) -> dict[str, str]:
    return {
        "id": identifier,
        "version": version,
        "hash": artifact_fingerprint(content),
    }


@dataclass(frozen=True)
class SignalObservation:
    """One typed value-state plus field-level provenance / 一个类型化值状态及字段级来源。"""

    state: SignalState
    value: object | None
    source_binding: Mapping[str, Any]
    source_field: str
    valid_at: str | None
    captured_at: str
    method: str
    integrity_hash: str

    def __post_init__(self) -> None:
        if not isinstance(self.state, SignalState):
            raise TypeError("state must be SignalState")
        if self.state is SignalState.OBSERVED and self.value is None:
            raise WorkflowRouteError(
                "observed signal requires a value / 已观测信号必须包含值"
            )
        if self.state is not SignalState.OBSERVED and self.value is not None:
            raise WorkflowRouteError(
                "non-observed signal cannot carry a value / 非已观测信号不得携带值"
            )

    def as_record(self, signal: str) -> dict[str, Any]:
        value: dict[str, Any] = {"state": self.state.value}
        if self.state is SignalState.OBSERVED:
            raw_value = self.value.value if isinstance(self.value, Enum) else self.value
            value["value"] = raw_value
        return {
            "signal": signal,
            "value": value,
            "provenance": {
                "source_binding": _detached(self.source_binding),
                "source_field": self.source_field,
                "valid_at": self.valid_at,
                "captured_at": self.captured_at,
                "method": self.method,
                "integrity_hash": self.integrity_hash,
            },
        }


@dataclass(frozen=True)
class TaskAtom:
    """Independently closable business unit / 可独立闭环的业务单元。"""

    task_atom_id: str
    task_atom_version: str
    primary_intent: TaskIntent
    input_binding: Mapping[str, Any]
    output_contract_binding: Mapping[str, Any]
    dependency_atom_ids: tuple[str, ...]
    risk_owner_binding: Mapping[str, Any]
    includes_read_only_judgment: bool
    includes_write_action: bool

    def __post_init__(self) -> None:
        if self.includes_read_only_judgment and self.includes_write_action:
            raise WorkflowRouteError(
                "judgment and write action must be split into separate atoms / "
                "判断与写动作必须拆为不同任务原子"
            )
        if not isinstance(self.primary_intent, TaskIntent):
            raise TypeError("primary_intent must be TaskIntent")

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_atom_id": self.task_atom_id,
            "task_atom_version": self.task_atom_version,
            "primary_intent": self.primary_intent.value,
            "input_binding": _detached(self.input_binding),
            "output_contract_binding": _detached(self.output_contract_binding),
            "dependency_atom_ids": list(self.dependency_atom_ids),
            "risk_owner_binding": _detached(self.risk_owner_binding),
            "includes_read_only_judgment": self.includes_read_only_judgment,
            "includes_write_action": self.includes_write_action,
        }


@dataclass(frozen=True)
class WorkflowRouteRequest:
    """Frozen input to one composite route decision / 一次复合路由决定的冻结输入。"""

    workflow_id: str
    task_id: str
    run_id: str
    scene_id: str
    task_atom: TaskAtom
    signals: Mapping[str, SignalObservation]
    budget_profile_binding: Mapping[str, Any]
    validator_profile_binding: Mapping[str, Any]
    created_at: str
    human_gate: Mapping[str, Any] | None = None
    route_confidence: float | None = None
    route_confidence_source_binding: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class WorkflowRoutingPolicy:
    """Versioned deterministic workflow-lane and action-gate policy.

    / 版本化确定性工作流车道与行动门禁策略。
    """

    policy_id: str = WORKFLOW_ROUTE_POLICY_ID
    policy_version: str = WORKFLOW_ROUTE_POLICY_VERSION

    @property
    def binding(self) -> dict[str, str]:
        return _binding(
            self.policy_id,
            self.policy_version,
            {
                "policy_id": self.policy_id,
                "policy_version": self.policy_version,
                "ordered_rule_manifest": _WORKFLOW_POLICY_MANIFEST,
            },
        )

    @staticmethod
    def lane(task_intent: object | None) -> ExecutionLane:
        mapping = {
            TaskIntent.QUERY.value: ExecutionLane.DIRECT_ANSWER,
            TaskIntent.READ_ONLY_ANALYSIS.value: ExecutionLane.READ_ONLY_ANALYSIS,
            TaskIntent.STRUCTURED_JUDGMENT.value: ExecutionLane.STRUCTURED_JUDGMENT,
            TaskIntent.DRAFT.value: ExecutionLane.STRUCTURED_JUDGMENT,
            TaskIntent.BUSINESS_ACTION.value: ExecutionLane.PLANNED_EXECUTION,
        }
        return mapping.get(task_intent, ExecutionLane.CLARIFICATION_HUMAN_REVIEW)


class WorkflowSignalAdapter:
    """Versioned provenance-preserving adapter to ``RoutingSignals``.

    / 保留来源的版本化 ``RoutingSignals`` 适配器。
    """

    adapter_id = WORKFLOW_SIGNAL_ADAPTER_ID
    adapter_version = WORKFLOW_SIGNAL_ADAPTER_VERSION

    @property
    def binding(self) -> dict[str, str]:
        return _binding(
            self.adapter_id,
            self.adapter_version,
            {
                "adapter_id": self.adapter_id,
                "adapter_version": self.adapter_version,
                "mapping_manifest": _ADAPTER_MANIFEST,
            },
        )

    def freeze(self, request: WorkflowRouteRequest) -> list[dict[str, Any]]:
        names = set(request.signals)
        expected = set(_SIGNAL_ORDER)
        if names != expected:
            raise WorkflowRouteError(
                "workflow signals must match the normative set "
                f"(missing={sorted(expected - names)}, unexpected={sorted(names - expected)}) / "
                "工作流信号必须与规范集合完全一致"
            )
        return [request.signals[name].as_record(name) for name in _SIGNAL_ORDER]

    @staticmethod
    def _observed(request: WorkflowRouteRequest, name: str) -> object | None:
        observation = request.signals[name]
        if observation.state is not SignalState.OBSERVED:
            return None
        return observation.value.value if isinstance(observation.value, Enum) else observation.value

    def to_reasoning_signals(self, request: WorkflowRouteRequest) -> RoutingSignals:
        missing_or_unknown = [
            name
            for name, observation in request.signals.items()
            if observation.state in {SignalState.MISSING, SignalState.UNKNOWN}
        ]
        complexity = self._observed(request, "intent_complexity")
        if missing_or_unknown:
            complexity = None

        action_risk = self._observed(request, "action_risk")
        risk_map = {
            ActionRisk.READ_ONLY.value: RiskLevel.LOW,
            ActionRisk.DRAFT.value: RiskLevel.LOW,
            ActionRisk.REVERSIBLE_WRITE.value: RiskLevel.MEDIUM,
            ActionRisk.SENSITIVE_WRITE.value: RiskLevel.HIGH,
            ActionRisk.IRREVERSIBLE_EXTERNAL_ACTION.value: RiskLevel.CRITICAL,
        }
        return RoutingSignals(
            task_id=request.task_atom.task_atom_id,
            scene_id=request.scene_id,
            intent_complexity=(
                None if complexity is None else IntentComplexity(str(complexity))
            ),
            evidence_state=(
                None
                if self._observed(request, "evidence_state") is None
                else EvidenceState(str(self._observed(request, "evidence_state")))
            ),
            mechanism_uncertainty=(
                None
                if self._observed(request, "mechanism_uncertainty") is None
                else MechanismUncertainty(
                    str(self._observed(request, "mechanism_uncertainty"))
                )
            ),
            risk_level=risk_map.get(str(action_risk)),
            environment_interaction_required=self._as_bool(
                request, "environment_interaction_required"
            ),
            material_rivals_present=self._as_bool(request, "material_rivals_present"),
            dominant_dependency_path=self._as_bool(request, "dominant_dependency_path"),
            permission_granted=self._as_bool(request, "permission_granted"),
            prohibited_action=self._as_bool(request, "prohibited_action") is True,
            irreversible_action=self._as_bool(request, "irreversible_action") is True,
            strong_validation_available=self._as_bool(
                request, "strong_validation_available"
            ),
        )

    def _as_bool(self, request: WorkflowRouteRequest, name: str) -> bool | None:
        value = self._observed(request, name)
        if value is None:
            return None
        if not isinstance(value, bool):
            raise WorkflowRouteError(f"{name} must be boolean / {name} 必须是布尔值")
        return value


class WorkflowRouteCoordinator:
    """Produce one sealed two-level route decision / 生成一个封存的两级路由决定。"""

    def __init__(
        self,
        *,
        workflow_policy: WorkflowRoutingPolicy | None = None,
        reasoning_policy: RoutingPolicy | None = None,
        adapter: WorkflowSignalAdapter | None = None,
    ) -> None:
        self.workflow_policy = workflow_policy or WorkflowRoutingPolicy()
        self.reasoning_policy = reasoning_policy or RoutingPolicy()
        self.adapter = adapter or WorkflowSignalAdapter()

    def route(self, request: WorkflowRouteRequest) -> dict[str, Any]:
        frozen_signals = self.adapter.freeze(request)
        workflow_policy_binding = self.workflow_policy.binding
        adapter_binding = self.adapter.binding
        workflow_fingerprint = workflow_signal_fingerprint(
            task_atom_id=request.task_atom.task_atom_id,
            workflow_policy_binding=workflow_policy_binding,
            adapter_binding=adapter_binding,
            workflow_signals=frozen_signals,
        )
        reasoning_signals = self.adapter.to_reasoning_signals(request)
        reasoning_decision = self.reasoning_policy.route(reasoning_signals)
        blockers = self._blockers(request, reasoning_decision)
        task_intent = self.adapter._observed(request, "task_intent")
        lane = self.workflow_policy.lane(task_intent)
        if blockers and any(item["severity"] == "critical" for item in blockers):
            lane = ExecutionLane.CLARIFICATION_HUMAN_REVIEW
        reasoning_summary = self._reasoning_summary(
            reasoning_decision,
            request.task_atom.risk_owner_binding,
        )
        action_allowed = self._action_allowed(
            request,
            lane,
            reasoning_decision,
            blockers,
        )
        confidence = self._confidence_telemetry(request)
        decision_id = "WORKFLOW_ROUTE_" + artifact_fingerprint(
            {
                "workflow_policy_binding": workflow_policy_binding,
                "workflow_signal_fingerprint": workflow_fingerprint,
                "reasoning_decision_binding": reasoning_summary["decision_binding"],
            }
        ).removeprefix("sha256:")[:24]
        envelope = {
            "schema_version": WORKFLOW_ROUTE_SCHEMA_VERSION,
            "decision_id": decision_id,
            "decision_revision": 1,
            "workflow_id": request.workflow_id,
            "task_id": request.task_id,
            "run_id": request.run_id,
            "scene_id": request.scene_id,
            "task_atom": request.task_atom.as_dict(),
            "workflow_policy_binding": workflow_policy_binding,
            "adapter_binding": adapter_binding,
            "reasoning_policy_binding": {
                "id": reasoning_decision.route_policy_id,
                "version": reasoning_decision.route_policy_version,
                "hash": reasoning_decision.route_policy_hash,
            },
            "workflow_signals": frozen_signals,
            "workflow_signal_fingerprint": workflow_fingerprint,
            "execution_lane": lane.value,
            "action_allowed": action_allowed,
            "human_gate": (
                None if request.human_gate is None else _detached(request.human_gate)
            ),
            "blockers": blockers,
            "reasoning_decision": reasoning_summary,
            "budget_profile_binding": _detached(request.budget_profile_binding),
            "validator_profile_binding": _detached(request.validator_profile_binding),
            "run_graph_binding": {"state": "not_applicable"},
            "abstained": reasoning_decision.abstained,
            "route_confidence_telemetry": confidence,
            "created_at": request.created_at,
        }
        return build_artifact("workflow_route_envelope", envelope)

    @staticmethod
    def _reasoning_summary(
        decision: RouteDecision,
        risk_owner_binding: Mapping[str, Any],
    ) -> dict[str, Any]:
        raw = decision.as_dict()
        configuration = None
        if decision.disposition is RouteDisposition.EXECUTE:
            configuration = {
                "execution_mode": raw["execution_mode"],
                "reasoning_depth": raw["reasoning_depth"],
                "primary_topology": raw["primary_topology"],
                "supporting_topologies": raw["supporting_topologies"],
            }
        handoff = None
        if decision.disposition is not RouteDisposition.EXECUTE:
            reason_codes = list(decision.reason_codes)
            if "insufficient_evidence" in reason_codes:
                target = "evidence_completion"
            elif any(
                item in reason_codes
                for item in ("external_validation_required", "human_judgment_required")
            ):
                target = "human_review"
            elif decision.disposition is RouteDisposition.REJECT:
                target = "policy_owner"
            else:
                target = "orchestration"
            handoff = {
                "target": target,
                "reason_codes": reason_codes,
                "authority_binding": _detached(risk_owner_binding),
            }
        content = {
            "disposition": decision.disposition.value,
            "configuration": configuration,
            "reason_codes": list(decision.reason_codes),
            "missing_signals": list(decision.missing_signals),
            "signal_fingerprint": decision.signal_fingerprint,
            "escalation_handoff": handoff,
        }
        return {
            "decision_binding": {
                "id": "REASONING_DECISION_"
                + artifact_fingerprint(content).removeprefix("sha256:")[:24],
                "version": decision.route_policy_version,
                "hash": artifact_fingerprint(content),
            },
            **content,
        }

    def _blockers(
        self,
        request: WorkflowRouteRequest,
        reasoning_decision: RouteDecision,
    ) -> list[dict[str, Any]]:
        blockers: list[dict[str, Any]] = []
        for name in _SIGNAL_ORDER:
            observation = request.signals[name]
            if observation.state in {SignalState.MISSING, SignalState.UNKNOWN}:
                blockers.append(self._blocker("MISSING_ROUTE_SIGNAL", "signal", "critical", name))

        observed = lambda name: self.adapter._observed(request, name)
        action_risk = observed("action_risk")
        write_action = action_risk in {
            ActionRisk.REVERSIBLE_WRITE.value,
            ActionRisk.SENSITIVE_WRITE.value,
            ActionRisk.IRREVERSIBLE_EXTERNAL_ACTION.value,
        }
        if observed("prohibited_action") is True:
            blockers.append(self._blocker("PROHIBITED_ACTION", "policy", "critical", "prohibited_action"))
        if observed("permission_granted") is False:
            blockers.append(self._blocker("PERMISSION_DENIED", "permission", "critical", "permission_granted"))
        if write_action and observed("mechanical_state") != MechanicalState.READY.value:
            blockers.append(self._blocker("MECHANICAL_STATE_NOT_READY", "mechanical", "critical", "mechanical_state"))
        if write_action and observed("accountable_owner_present") is not True:
            blockers.append(self._blocker("ACCOUNTABLE_OWNER_MISSING", "owner", "critical", "accountable_owner_present"))
        if action_risk in {
            ActionRisk.SENSITIVE_WRITE.value,
            ActionRisk.IRREVERSIBLE_EXTERNAL_ACTION.value,
        } and observed("strong_validation_available") is not True:
            blockers.append(self._blocker("STRONG_VALIDATION_MISSING", "reasoning", "critical", "strong_validation_available"))
        if action_risk in {
            ActionRisk.SENSITIVE_WRITE.value,
            ActionRisk.IRREVERSIBLE_EXTERNAL_ACTION.value,
        } and observed("approval_state") != ApprovalState.APPROVED.value:
            blockers.append(self._blocker("HUMAN_APPROVAL_REQUIRED", "approval", "critical", "approval_state"))
        if action_risk in {
            ActionRisk.SENSITIVE_WRITE.value,
            ActionRisk.IRREVERSIBLE_EXTERNAL_ACTION.value,
        } and (
            request.human_gate is None
            or request.human_gate.get("status") != "approved"
            or request.human_gate.get("authority_binding", {}).get("state")
            != "observed"
        ):
            blockers.append(
                self._blocker(
                    "AUTHORITATIVE_HUMAN_GATE_REQUIRED",
                    "approval",
                    "critical",
                    "approval_state",
                )
            )
        if reasoning_decision.disposition is not RouteDisposition.EXECUTE:
            blockers.append(self._blocker("REASONING_ROUTE_NON_EXECUTABLE", "reasoning", "error", None))
        return sorted(blockers, key=lambda item: (item["severity"], item["code"], str(item["source_signal"])))

    @staticmethod
    def _blocker(
        code: str,
        category: str,
        severity: str,
        source_signal: str | None,
    ) -> dict[str, Any]:
        return {
            "code": code,
            "category": category,
            "severity": severity,
            "source_signal": source_signal,
            "evidence_bindings": [],
        }

    def _action_allowed(
        self,
        request: WorkflowRouteRequest,
        lane: ExecutionLane,
        decision: RouteDecision,
        blockers: list[dict[str, Any]],
    ) -> bool:
        if lane is not ExecutionLane.PLANNED_EXECUTION:
            return False
        if decision.disposition is not RouteDisposition.EXECUTE or blockers:
            return False
        observed = lambda name: self.adapter._observed(request, name)
        action_risk = observed("action_risk")
        if action_risk not in {
            ActionRisk.REVERSIBLE_WRITE.value,
            ActionRisk.SENSITIVE_WRITE.value,
            ActionRisk.IRREVERSIBLE_EXTERNAL_ACTION.value,
        }:
            return False
        if not (
            observed("mechanical_state") == MechanicalState.READY.value
            and observed("permission_granted") is True
            and observed("prohibited_action") is False
            and observed("accountable_owner_present") is True
        ):
            return False
        approval = observed("approval_state")
        if approval not in {ApprovalState.NOT_REQUIRED.value, ApprovalState.APPROVED.value}:
            return False
        if request.human_gate is not None and not (
            request.human_gate.get("status") == "approved"
            and request.human_gate.get("authority_binding", {}).get("state") == "observed"
        ):
            return False
        return True

    @staticmethod
    def _confidence_telemetry(request: WorkflowRouteRequest) -> dict[str, Any]:
        if request.route_confidence is None:
            return {"state": "not_applicable"}
        if not isinstance(request.route_confidence, (int, float)) or isinstance(
            request.route_confidence, bool
        ):
            raise TypeError("route_confidence must be a number")
        if not 0 <= float(request.route_confidence) <= 1:
            raise WorkflowRouteError(
                "route confidence must be between zero and one / 路由置信度必须在零到一之间"
            )
        if request.route_confidence_source_binding is None:
            raise WorkflowRouteError(
                "observed route confidence requires a source binding / "
                "已观测路由置信度必须包含来源绑定"
            )
        return {
            "state": "observed",
            "value": float(request.route_confidence),
            "source_binding": _detached(request.route_confidence_source_binding),
        }


__all__ = [
    "ActionRisk",
    "ApprovalState",
    "ExecutionLane",
    "MechanicalState",
    "SignalObservation",
    "SignalState",
    "TaskAtom",
    "TaskIntent",
    "WorkflowRouteCoordinator",
    "WorkflowRouteError",
    "WorkflowRouteRequest",
    "WorkflowRoutingPolicy",
    "WorkflowSignalAdapter",
]
