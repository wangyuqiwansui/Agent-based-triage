"""Deterministic reasoning route policy. / 确定性推理路由策略。

This module routes only on externally observable signals. Model confidence is
intentionally absent: low confidence may be converted into a missing or high-
uncertainty signal by an upstream adapter, but high confidence can never release
work. / 本模块只根据外部可观测信号路由。接口刻意不包含模型置信度：上游适配器
可以把低置信转换为缺失或高不确定性信号，但高置信绝不能直接放行任务。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
import re


_SEMANTIC_VERSION = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$"
)
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")

_SIGNAL_SCHEMA_NAMES = {
    "intent_complexity": "complexity",
    "evidence_state": "evidence_availability",
    "mechanism_uncertainty": "uncertainty",
    "risk_level": "risk",
    "environment_interaction_required": "interaction_need",
    "material_rivals_present": "parallelizability",
    "dominant_dependency_path": "dominant_dependency_path",
    "permission_granted": "permission_granted",
    "prohibited_action": "prohibited_action",
    "irreversible_action": "reversibility",
    "strong_validation_available": "external_verifiability",
}

_ROUTING_POLICY_RULE_MANIFEST = (
    "prohibited_action:reject:policy_constraint",
    "permission_denied:reject:policy_constraint",
    "required_signal_missing:escalate:missing_route_signal",
    "strong_validation_missing:escalate:external_validation_required",
    "evidence_insufficient_unavailable_or_untrusted:escalate:insufficient_evidence",
    "environment_interaction:iterative:feedback_required",
    "material_rivals_or_conflict:parallel:independent_hypotheses",
    "complete_stable_low_risk:direct:direct_low_risk_release",
    "fallback:chain:multi_step_dependency",
)


def _fingerprint(value: object) -> str:
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class IntentComplexity(str, Enum):
    """Observable intent complexity. / 可观测意图复杂度。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EvidenceState(str, Enum):
    """Evidence availability and trust state. / 证据可用性与可信状态。"""

    COMPLETE_CONSISTENT = "complete_consistent"
    MOSTLY_COMPLETE = "mostly_complete"
    CONFLICTING = "conflicting"
    INSUFFICIENT = "insufficient"
    UNAVAILABLE = "unavailable"
    UNTRUSTED = "untrusted"


class MechanismUncertainty(str, Enum):
    """Uncertainty about the governing mechanism. / 对作用机制的不确定性。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(str, Enum):
    """Action and decision risk. / 动作与决策风险。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RouteDisposition(str, Enum):
    """Governance disposition before execution. / 执行前治理处置。"""

    EXECUTE = "execute"
    REJECT = "reject"
    ESCALATE = "escalate"


class ReasoningDepth(str, Enum):
    """Reasoning depth, separate from topology. / 与拓扑分离的推理深度。"""

    DIRECT = "direct"
    DELIBERATIVE = "deliberative"


class ExecutionMode(str, Enum):
    """Runtime execution strategy. / 运行时执行策略。"""

    DIRECT = "direct"
    CHAIN = "chain"
    PARALLEL = "parallel"
    ITERATIVE = "iterative"


class PrimaryTopology(str, Enum):
    """Primary matrix topology; direct has no topology. / 主矩阵拓扑；直接处理无拓扑。"""

    CHAIN = "chain"
    PARALLEL = "parallel"
    LOOP = "loop"


@dataclass(frozen=True)
class RoutingSignals:
    """Versionable observable inputs to routing. / 可版本化的路由可观测输入。"""

    task_id: str
    scene_id: str
    intent_complexity: IntentComplexity | None
    evidence_state: EvidenceState | None
    mechanism_uncertainty: MechanismUncertainty | None
    risk_level: RiskLevel | None
    environment_interaction_required: bool | None
    material_rivals_present: bool | None
    dominant_dependency_path: bool | None
    permission_granted: bool | None
    prohibited_action: bool = False
    irreversible_action: bool = False
    strong_validation_available: bool | None = None

    def __post_init__(self) -> None:
        enum_fields = {
            "intent_complexity": IntentComplexity,
            "evidence_state": EvidenceState,
            "mechanism_uncertainty": MechanismUncertainty,
            "risk_level": RiskLevel,
        }
        for field_name, enum_type in enum_fields.items():
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, enum_type):
                raise TypeError(f"{field_name} must be {enum_type.__name__} or None")
        for field_name in (
            "environment_interaction_required",
            "material_rivals_present",
            "dominant_dependency_path",
            "permission_granted",
            "strong_validation_available",
        ):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, bool):
                raise TypeError(f"{field_name} must be bool or None")
        for field_name in ("prohibited_action", "irreversible_action"):
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(f"{field_name} must be bool")

    def fingerprint(self) -> str:
        """Return a stable signal digest. / 返回稳定的信号摘要。"""

        return _fingerprint(self.as_dict())

    def as_dict(self) -> dict[str, object]:
        """Return JSON-compatible typed signals. / 返回可序列化的类型化信号。"""

        return {
            key: value.value if isinstance(value, Enum) else value
            for key, value in asdict(self).items()
        }

    def as_schema_signals(self) -> list[dict[str, object]]:
        """Return canonical contract/event routing signals / 返回契约与事件共用的规范路由信号。"""

        raw_values: dict[str, object | None] = {
            "intent_complexity": self.intent_complexity,
            "evidence_state": self.evidence_state,
            "mechanism_uncertainty": self.mechanism_uncertainty,
            "risk_level": self.risk_level,
            "environment_interaction_required": self.environment_interaction_required,
            "material_rivals_present": self.material_rivals_present,
            "dominant_dependency_path": self.dominant_dependency_path,
            "permission_granted": self.permission_granted,
            "prohibited_action": self.prohibited_action,
            "irreversible_action": (
                "irreversible" if self.irreversible_action else "reversible"
            ),
            "strong_validation_available": self.strong_validation_available,
        }
        result: list[dict[str, object]] = []
        for field_name, value in raw_values.items():
            normalized = value.value if isinstance(value, Enum) else value
            state = (
                {"state": "unknown"}
                if normalized is None
                else {"state": "observed", "value": normalized}
            )
            result.append(
                {"signal": _SIGNAL_SCHEMA_NAMES[field_name], "value": state}
            )
        return result


@dataclass(frozen=True)
class RouteDecision:
    """Auditable route decision without business truth. / 不替代业务事实的可审计路由决定。"""

    route_policy_id: str
    route_policy_version: str
    route_policy_hash: str
    disposition: RouteDisposition
    reasoning_depth: ReasoningDepth | None
    execution_mode: ExecutionMode | None
    primary_topology: PrimaryTopology | None
    supporting_topologies: tuple[str, ...]
    reason_codes: tuple[str, ...]
    missing_signals: tuple[str, ...]
    signal_fingerprint: str
    abstained: bool

    def _assert_signal_binding(self, signals: RoutingSignals) -> None:
        if signals.fingerprint() != self.signal_fingerprint:
            raise ValueError(
                "routing signals do not match the decision fingerprint / "
                "路由信号与决策指纹不一致"
            )

    def _configuration(self) -> dict[str, object] | None:
        if self.execution_mode is None:
            return None
        return {
            "execution_mode": self.execution_mode.value,
            "reasoning_depth": self.reasoning_depth.value,
            "primary_topology": (
                None if self.primary_topology is None else self.primary_topology.value
            ),
            "supporting_topologies": list(self.supporting_topologies),
        }

    def _reasons(self) -> list[dict[str, object]]:
        return [
            {
                "reason_code": reason_code,
                "source_binding": {"state": "not_applicable"},
            }
            for reason_code in self.reason_codes
        ]

    def to_contract_routing_decision(
        self, signals: RoutingSignals
    ) -> dict[str, object]:
        """Build a schema-valid contract routing decision / 构造符合 Schema 的契约路由决策。"""

        configuration = self._configuration()
        self._assert_signal_binding(signals)
        if self.disposition is not RouteDisposition.EXECUTE or configuration is None:
            raise ValueError(
                "only executable routes can establish a reasoning contract / "
                "只有可执行路由才能建立推理契约"
            )
        return {
            "decision_id": "route-decision-"
            + _fingerprint(
                {
                    "policy_hash": self.route_policy_hash,
                    "signal_fingerprint": self.signal_fingerprint,
                }
            ).removeprefix("sha256:")[:24],
            "policy_binding": {
                "id": self.route_policy_id,
                "version": self.route_policy_version,
                "hash": self.route_policy_hash,
            },
            "disposition": self.disposition.value,
            "signals": signals.as_schema_signals(),
            "reasons": self._reasons(),
            "selected_configuration": configuration,
            "signal_fingerprint": self.signal_fingerprint,
            "missing_signals": [
                _SIGNAL_SCHEMA_NAMES[name] for name in self.missing_signals
            ],
            "abstained": self.abstained,
        }

    def to_route_event_payload(self, signals: RoutingSignals) -> dict[str, object]:
        """Build a schema-valid route-selected payload / 构造符合 Schema 的路由选择事件载荷。"""

        self._assert_signal_binding(signals)
        return {
            "routing_policy_binding": {
                "id": self.route_policy_id,
                "version": self.route_policy_version,
                "hash": self.route_policy_hash,
            },
            "disposition": self.disposition.value,
            "configuration": self._configuration(),
            "signals": signals.as_schema_signals(),
            "reasons": self._reasons(),
            "signal_fingerprint": self.signal_fingerprint,
            "missing_signals": [
                _SIGNAL_SCHEMA_NAMES[name] for name in self.missing_signals
            ],
            "abstained": self.abstained,
        }

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible auditable decision. / 返回可序列化的审计决定。"""

        return {
            "route_policy_id": self.route_policy_id,
            "route_policy_version": self.route_policy_version,
            "route_policy_hash": self.route_policy_hash,
            "disposition": self.disposition.value,
            "reasoning_depth": (
                None if self.reasoning_depth is None else self.reasoning_depth.value
            ),
            "execution_mode": (
                None if self.execution_mode is None else self.execution_mode.value
            ),
            "primary_topology": (
                None if self.primary_topology is None else self.primary_topology.value
            ),
            "supporting_topologies": list(self.supporting_topologies),
            "reason_codes": list(self.reason_codes),
            "missing_signals": list(self.missing_signals),
            "signal_fingerprint": self.signal_fingerprint,
            "abstained": self.abstained,
        }


@dataclass(frozen=True)
class RoutingPolicy:
    """Deterministic precedence and abstention policy. / 确定性优先级与弃权策略。"""

    route_policy_id: str = "REASONING_ROUTE_DEFAULT"
    route_policy_version: str = "1.1.0"

    def __post_init__(self) -> None:
        if not isinstance(self.route_policy_id, str):
            raise TypeError("route_policy_id must be text")
        if (
            not self.route_policy_id
            or len(self.route_policy_id) > 160
            or _IDENTIFIER.fullmatch(self.route_policy_id) is None
        ):
            raise ValueError(
                "route_policy_id must satisfy the contract Identifier definition"
            )
        if not isinstance(self.route_policy_version, str):
            raise TypeError("route_policy_version must be text")
        if _SEMANTIC_VERSION.fullmatch(self.route_policy_version) is None:
            raise ValueError("route_policy_version must be semantic version text")

    def route(self, signals: RoutingSignals) -> RouteDecision:
        """Apply hard gates, abstention, then topology precedence. / 依次应用硬门槛、弃权与拓扑优先级。"""

        if not signals.task_id or not signals.scene_id:
            raise ValueError("task_id and scene_id must be non-empty")

        common = {
            "route_policy_id": self.route_policy_id,
            "route_policy_version": self.route_policy_version,
            "route_policy_hash": _fingerprint(
                {
                    "route_policy_id": self.route_policy_id,
                    "route_policy_version": self.route_policy_version,
                    "ordered_rule_manifest": _ROUTING_POLICY_RULE_MANIFEST,
                }
            ),
            "signal_fingerprint": signals.fingerprint(),
        }

        if signals.prohibited_action:
            return RouteDecision(
                **common,
                disposition=RouteDisposition.REJECT,
                reasoning_depth=None,
                execution_mode=None,
                primary_topology=None,
                supporting_topologies=(),
                reason_codes=("policy_constraint",),
                missing_signals=(),
                abstained=False,
            )

        if signals.permission_granted is False:
            return RouteDecision(
                **common,
                disposition=RouteDisposition.REJECT,
                reasoning_depth=None,
                execution_mode=None,
                primary_topology=None,
                supporting_topologies=(),
                reason_codes=("policy_constraint",),
                missing_signals=(),
                abstained=False,
            )

        required = (
            "intent_complexity",
            "evidence_state",
            "mechanism_uncertainty",
            "risk_level",
            "environment_interaction_required",
            "material_rivals_present",
            "dominant_dependency_path",
            "permission_granted",
        )
        missing = tuple(name for name in required if getattr(signals, name) is None)
        if missing:
            return RouteDecision(
                **common,
                disposition=RouteDisposition.ESCALATE,
                reasoning_depth=None,
                execution_mode=None,
                primary_topology=None,
                supporting_topologies=("orchestration",),
                reason_codes=("missing_route_signal",),
                missing_signals=missing,
                abstained=True,
            )

        if (
            signals.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
            or signals.irreversible_action
        ) and signals.strong_validation_available is not True:
            return RouteDecision(
                **common,
                disposition=RouteDisposition.ESCALATE,
                reasoning_depth=ReasoningDepth.DELIBERATIVE,
                execution_mode=None,
                primary_topology=None,
                supporting_topologies=("orchestration", "hierarchy"),
                reason_codes=("external_validation_required",),
                missing_signals=(
                    ("strong_validation_available",)
                    if signals.strong_validation_available is None
                    else ()
                ),
                abstained=True,
            )

        if signals.evidence_state in {
            EvidenceState.INSUFFICIENT,
            EvidenceState.UNAVAILABLE,
            EvidenceState.UNTRUSTED,
        }:
            return RouteDecision(
                **common,
                disposition=RouteDisposition.ESCALATE,
                reasoning_depth=ReasoningDepth.DELIBERATIVE,
                execution_mode=None,
                primary_topology=None,
                supporting_topologies=("orchestration",),
                reason_codes=("insufficient_evidence",),
                missing_signals=(),
                abstained=True,
            )

        if signals.environment_interaction_required:
            return self._execute(
                common,
                ExecutionMode.ITERATIVE,
                PrimaryTopology.LOOP,
                ("feedback_required",),
            )

        if (
            signals.material_rivals_present
            or signals.evidence_state is EvidenceState.CONFLICTING
        ):
            return self._execute(
                common,
                ExecutionMode.PARALLEL,
                PrimaryTopology.PARALLEL,
                ("independent_hypotheses",),
            )

        direct_allowed = (
            signals.intent_complexity is IntentComplexity.LOW
            and signals.evidence_state is EvidenceState.COMPLETE_CONSISTENT
            and signals.mechanism_uncertainty is MechanismUncertainty.LOW
            and signals.risk_level is RiskLevel.LOW
            and not signals.dominant_dependency_path
        )
        if direct_allowed:
            return self._execute(
                common,
                ExecutionMode.DIRECT,
                None,
                ("direct_low_risk_release",),
                depth=ReasoningDepth.DIRECT,
            )

        return self._execute(
            common,
            ExecutionMode.CHAIN,
            PrimaryTopology.CHAIN,
            ("multi_step_dependency",),
        )

    @staticmethod
    def _execute(
        common: dict[str, object],
        mode: ExecutionMode,
        topology: PrimaryTopology | None,
        reasons: tuple[str, ...],
        *,
        depth: ReasoningDepth = ReasoningDepth.DELIBERATIVE,
    ) -> RouteDecision:
        return RouteDecision(
            **common,
            disposition=RouteDisposition.EXECUTE,
            reasoning_depth=depth,
            execution_mode=mode,
            primary_topology=topology,
            supporting_topologies=("orchestration",),
            reason_codes=reasons,
            missing_signals=(),
            abstained=False,
        )


__all__ = [
    "EvidenceState",
    "ExecutionMode",
    "IntentComplexity",
    "MechanismUncertainty",
    "PrimaryTopology",
    "ReasoningDepth",
    "RiskLevel",
    "RouteDecision",
    "RouteDisposition",
    "RoutingPolicy",
    "RoutingSignals",
]
