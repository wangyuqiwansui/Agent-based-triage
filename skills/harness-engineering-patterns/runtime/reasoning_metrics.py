"""Correct, explicit reasoning-observability metrics. / 正确且显式的推理可观测性指标。

The module keeps unavailable data distinct from an observed zero and provides
small, deterministic functions that can be used by probe collectors or tests.
/ 本模块将不可用数据与真实观测零值分开，并提供可供探针采集器或测试复用的
小型确定性函数。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import inspect
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable, Mapping


class MetricState(str, Enum):
    """Metric availability and calculation state. / 指标可用性与计算状态。"""

    OBSERVED_ZERO = "observed_zero"
    MISSING = "missing"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
    INSUFFICIENT_SAMPLE = "insufficient_sample"
    COMPUTED = "computed"


MetricValue = float | dict[str, float] | None


@dataclass(frozen=True)
class MetricResult:
    """A metric value with explicit state and audit inputs. / 带显式状态与审计输入的指标值。"""

    metric_id: str
    state: MetricState
    value: MetricValue = None
    numerator: float | None = None
    denominator: float | None = None
    sample_size: float | None = None
    reason: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Enforce value-state invariants. / 强制数值与状态不变量。"""

        if not isinstance(self.metric_id, str) or not self.metric_id.strip():
            raise ValueError("metric_id must be a non-empty string")
        if not isinstance(self.state, MetricState):
            raise TypeError("state must be MetricState")
        for name in ("numerator", "denominator", "sample_size"):
            value = getattr(self, name)
            if value is not None:
                _finite_nonnegative(name, value)
        if not isinstance(self.details, Mapping):
            raise TypeError("details must be a mapping")

        unavailable_states = {
            MetricState.MISSING,
            MetricState.UNKNOWN,
            MetricState.NOT_APPLICABLE,
            MetricState.INSUFFICIENT_SAMPLE,
        }
        if self.state in unavailable_states:
            if self.value is not None:
                raise ValueError("unavailable metric states cannot contain a value")
            if not isinstance(self.reason, str) or not self.reason.strip():
                raise ValueError("unavailable metric states require a reason")
            return

        if self.value is None:
            raise ValueError("available metric states require a value")
        if isinstance(self.value, Mapping):
            if not self.value:
                raise ValueError("metric value mappings cannot be empty")
            normalized_values = []
            for dimension, value in self.value.items():
                if not isinstance(dimension, str) or not dimension:
                    raise ValueError("metric value dimensions must be non-empty strings")
                normalized_values.append(
                    _finite_nonnegative(f"value[{dimension}]", value)
                )
        else:
            normalized_values = [_finite_nonnegative("value", self.value)]

        all_zero = all(value == 0 for value in normalized_values)
        if self.state == MetricState.OBSERVED_ZERO and not all_zero:
            raise ValueError("observed_zero metrics must contain only zero values")
        if self.state == MetricState.COMPUTED and all_zero:
            raise ValueError("zero values must use the observed_zero state")

    @property
    def is_available(self) -> bool:
        """Return whether the result contains an observed value. / 返回结果是否包含观测值。"""

        return self.state in {MetricState.OBSERVED_ZERO, MetricState.COMPUTED}


class ProbeHealthState(str, Enum):
    """Publication-time probe health. / 发布时探针健康状态。"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class ProbeConditionState(str, Enum):
    """Tri-state applicability of one conditional probe. / 单个条件探针的三态适用性。"""

    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


_RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
_TIME_BASES = {"occurred_at", "emitted_at", "received_at"}


def _parse_rfc3339(name: str, value: str) -> datetime:
    """Parse a timezone-bearing RFC 3339 timestamp. / 解析带时区的 RFC 3339 时间。"""

    if not isinstance(value, str) or _RFC3339_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be a timezone-bearing RFC3339 timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid RFC3339 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{name} must carry a timezone")
    return parsed.astimezone(timezone.utc)


def _canonical_json(value: Any) -> str:
    """Return deterministic JSON for persisted metric inputs. / 返回指标输入的确定性 JSON。"""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


@dataclass(frozen=True)
class MetricEnvelope:
    """Publication metadata required around a numeric metric core. / 数值指标核心外必需的发布元数据。"""

    result: MetricResult
    registry_version: str
    metric_version: str
    calculation_inputs: Mapping[str, Any]
    window_start: str
    window_end: str
    time_basis: str
    watermark: str
    allowed_lateness_seconds: float
    window_revision: int
    window_finalized: bool
    buckets: Mapping[str, str]
    exclusion_counts: Mapping[str, float]
    completeness: float
    source_mix: Mapping[str, float]
    observed_probes: tuple[str, ...]
    probe_health: ProbeHealthState
    expected_manifest_version: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.result, MetricResult):
            raise TypeError("result must be MetricResult")
        for name in (
            "registry_version",
            "metric_version",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.calculation_inputs, Mapping):
            raise TypeError("calculation_inputs must be a mapping")
        if any(not isinstance(name, str) or not name for name in self.calculation_inputs):
            raise TypeError("calculation input names must be non-empty strings")
        try:
            normalized_inputs = json.loads(_canonical_json(dict(self.calculation_inputs)))
        except (TypeError, ValueError) as exc:
            raise ValueError("calculation_inputs must be finite JSON values") from exc
        object.__setattr__(self, "calculation_inputs", normalized_inputs)

        start = _parse_rfc3339("window_start", self.window_start)
        end = _parse_rfc3339("window_end", self.window_end)
        _parse_rfc3339("watermark", self.watermark)
        if start >= end:
            raise ValueError("metric window start must precede end")
        if self.time_basis not in _TIME_BASES:
            raise ValueError(
                "time_basis must be occurred_at, emitted_at, or received_at"
            )
        _finite_nonnegative("allowed_lateness_seconds", self.allowed_lateness_seconds)
        if (
            isinstance(self.window_revision, bool)
            or not isinstance(self.window_revision, int)
            or self.window_revision < 1
        ):
            raise ValueError("window_revision must be a positive integer")
        if not isinstance(self.window_finalized, bool):
            raise TypeError("window_finalized must be boolean")
        if not isinstance(self.buckets, Mapping) or not self.buckets:
            raise ValueError("buckets must be a non-empty mapping")
        if any(
            not isinstance(key, str)
            or not key
            or not isinstance(value, str)
            or not value
            for key, value in self.buckets.items()
        ):
            raise ValueError("bucket names and values must be non-empty strings")
        if not isinstance(self.exclusion_counts, Mapping):
            raise TypeError("exclusion_counts must be a mapping")
        for name, value in self.exclusion_counts.items():
            if not isinstance(name, str) or not name:
                raise ValueError("exclusion names must be non-empty strings")
            _finite_nonnegative(f"exclusion_counts[{name}]", value)
        normalized_completeness = _finite_nonnegative(
            "completeness", self.completeness
        )
        if normalized_completeness > 1:
            raise ValueError("completeness must be between zero and one")
        if not isinstance(self.source_mix, Mapping) or not self.source_mix:
            raise ValueError("source_mix must be a non-empty mapping")
        source_total = 0.0
        for name, value in self.source_mix.items():
            if not isinstance(name, str) or not name:
                raise ValueError("source names must be non-empty strings")
            source_total += _finite_nonnegative(f"source_mix[{name}]", value)
        if source_total == 0:
            raise ValueError("source_mix must contain observed contribution")
        if not isinstance(self.observed_probes, tuple) or any(
            not isinstance(probe_id, str) or not probe_id
            for probe_id in self.observed_probes
        ):
            raise TypeError("observed_probes must be a tuple of probe identifiers")
        if len(set(self.observed_probes)) != len(self.observed_probes):
            raise ValueError("observed_probes cannot contain duplicates")
        if not isinstance(self.probe_health, ProbeHealthState):
            raise TypeError("probe_health must be ProbeHealthState")
        if self.expected_manifest_version is not None and (
            not isinstance(self.expected_manifest_version, str)
            or not self.expected_manifest_version.strip()
        ):
            raise ValueError("expected_manifest_version must be null or non-empty")

    def as_dict(self) -> dict[str, Any]:
        """Return a persistence-ready representation. / 返回可持久化表示。"""

        canonical_inputs = _canonical_json(dict(self.calculation_inputs))
        return {
            "metric_id": self.result.metric_id,
            "metric_state": self.result.state.value,
            "value": self.result.value,
            "numerator": self.result.numerator,
            "denominator": self.result.denominator,
            "sample_size": self.result.sample_size,
            "uncomputable_reason": self.result.reason,
            "details": dict(self.result.details),
            "registry_version": self.registry_version,
            "metric_version": self.metric_version,
            "calculation_inputs": dict(self.calculation_inputs),
            "calculation_inputs_hash": "sha256:"
            + hashlib.sha256(canonical_inputs.encode("utf-8")).hexdigest(),
            "time_window": {
                "start": self.window_start,
                "end": self.window_end,
                "time_basis": self.time_basis,
                "watermark": self.watermark,
                "allowed_lateness_seconds": self.allowed_lateness_seconds,
                "revision": self.window_revision,
                "finalized": self.window_finalized,
            },
            "buckets": dict(self.buckets),
            "exclusion_counts": dict(self.exclusion_counts),
            "completeness": self.completeness,
            "source_mix": dict(self.source_mix),
            "observed_probes": list(self.observed_probes),
            "probe_health": self.probe_health.value,
            "expected_manifest_version": self.expected_manifest_version,
        }


class MetricPublicationError(ValueError):
    """Raised when a metric envelope is not publishable. / 指标信封不可发布时抛出。"""


@dataclass(frozen=True)
class ProbeDependencyResolution:
    """Resolved probes for one executable reasoning configuration. / 单个可执行推理配置解析出的探针。"""

    execution_mode: str
    supporting_topologies: tuple[str, ...]
    condition_states: tuple[tuple[str, str], ...]
    required_probes: tuple[str, ...]
    required_probe_bindings: tuple[tuple[str, str], ...]
    activated_conditionals: tuple[tuple[str, str], ...]

    @property
    def active_conditions(self) -> tuple[str, ...]:
        """Return conditions explicitly evaluated true. / 返回明确评估为真的条件。"""

        return tuple(
            condition_id
            for condition_id, state in self.condition_states
            if state == ProbeConditionState.TRUE.value
        )

    def as_dict(self) -> dict[str, Any]:
        """Return an audit-ready representation. / 返回可审计表示。"""

        return {
            "execution_mode": self.execution_mode,
            "supporting_topologies": list(self.supporting_topologies),
            "active_conditions": list(self.active_conditions),
            "condition_states": {
                condition_id: state for condition_id, state in self.condition_states
            },
            "required_probes": list(self.required_probes),
            "required_probe_bindings": [
                {"probe_id": probe_id, "version": version}
                for probe_id, version in self.required_probe_bindings
            ],
            "activated_conditionals": [
                {"probe_id": probe_id, "condition_id": condition_id}
                for probe_id, condition_id in self.activated_conditionals
            ],
        }


_UNAVAILABLE_STATES = {
    MetricState.MISSING,
    MetricState.UNKNOWN,
    MetricState.NOT_APPLICABLE,
}


def unavailable_metric(
    metric_id: str,
    state: MetricState,
    reason: str,
    *,
    numerator: float | None = None,
    denominator: float | None = None,
    sample_size: float | None = None,
    details: Mapping[str, Any] | None = None,
) -> MetricResult:
    """Create an unavailable result without inventing zero. / 创建不可用结果且不伪造零值。"""

    if state not in _UNAVAILABLE_STATES | {MetricState.INSUFFICIENT_SAMPLE}:
        raise ValueError("unavailable_metric requires an unavailable metric state")
    return MetricResult(
        metric_id=metric_id,
        state=state,
        numerator=numerator,
        denominator=denominator,
        sample_size=sample_size,
        reason=reason,
        details=details or {},
    )


def _finite_nonnegative(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return normalized


def safe_ratio(
    metric_id: str,
    numerator: float | None,
    denominator: float | None,
    *,
    min_sample: float = 1,
    sample_size: float | None = None,
    unavailable_state: MetricState | None = None,
    unavailable_reason: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> MetricResult:
    """Calculate a ratio without collapsing missing or zero-denominator cases. / 安全计算比率，不混淆缺失与零分母。"""

    minimum = _finite_nonnegative("min_sample", min_sample)
    normalized_numerator = (
        None if numerator is None else _finite_nonnegative("numerator", numerator)
    )
    normalized_denominator = (
        None
        if denominator is None
        else _finite_nonnegative("denominator", denominator)
    )
    normalized_sample = (
        None
        if sample_size is None
        else _finite_nonnegative("sample_size", sample_size)
    )
    if unavailable_state is not None:
        if unavailable_state not in _UNAVAILABLE_STATES:
            raise ValueError(
                "unavailable_state must be missing, unknown, or not_applicable"
            )
        return unavailable_metric(
            metric_id,
            unavailable_state,
            unavailable_reason or unavailable_state.value,
            numerator=normalized_numerator,
            denominator=normalized_denominator,
            sample_size=normalized_sample,
            details=details,
        )

    if normalized_numerator is None or normalized_denominator is None:
        return unavailable_metric(
            metric_id,
            MetricState.MISSING,
            "numerator_or_denominator_missing",
            numerator=normalized_numerator,
            denominator=normalized_denominator,
            sample_size=normalized_sample,
            details=details,
        )

    effective_sample = (
        normalized_denominator
        if normalized_sample is None
        else normalized_sample
    )

    if normalized_denominator == 0:
        return unavailable_metric(
            metric_id,
            MetricState.NOT_APPLICABLE,
            "zero_denominator",
            numerator=normalized_numerator,
            denominator=normalized_denominator,
            sample_size=effective_sample,
            details=details,
        )

    if effective_sample < minimum:
        return unavailable_metric(
            metric_id,
            MetricState.INSUFFICIENT_SAMPLE,
            "sample_below_minimum",
            numerator=normalized_numerator,
            denominator=normalized_denominator,
            sample_size=effective_sample,
            details={**(details or {}), "minimum_sample": minimum},
        )

    value = normalized_numerator / normalized_denominator
    state = MetricState.OBSERVED_ZERO if value == 0 else MetricState.COMPUTED
    return MetricResult(
        metric_id=metric_id,
        state=state,
        value=value,
        numerator=normalized_numerator,
        denominator=normalized_denominator,
        sample_size=effective_sample,
        details=details or {},
    )


def _bounded_rate(
    metric_id: str,
    numerator: float | None,
    denominator: float | None,
    *,
    min_sample: float,
    unavailable_state: MetricState | None,
) -> MetricResult:
    if numerator is not None and denominator is not None:
        normalized_numerator = _finite_nonnegative("numerator", numerator)
        normalized_denominator = _finite_nonnegative("denominator", denominator)
        if normalized_numerator > normalized_denominator:
            raise ValueError("rate numerator cannot exceed denominator")
    return safe_ratio(
        metric_id,
        numerator,
        denominator,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def bounded_ratio(
    metric_id: str,
    numerator: float | None,
    denominator: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Calculate a ratio constrained to the inclusive range 0..1. / 计算限制在 0 到 1 闭区间内的比率。"""

    return _bounded_rate(
        metric_id,
        numerator,
        denominator,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def unbounded_ratio(
    metric_id: str,
    numerator: float | None,
    denominator: float | None,
    *,
    min_sample: float = 1,
    sample_size: float | None = None,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Calculate a non-negative ratio that may exceed one. / 计算可大于一的非负比率。"""

    return safe_ratio(
        metric_id,
        numerator,
        denominator,
        min_sample=min_sample,
        sample_size=sample_size,
        unavailable_state=unavailable_state,
    )


def eligible_step_closure_rate(
    closed_eligible_steps: float | None,
    eligible_started_steps: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Closed eligible steps divided by started steps whose close deadline was reached. / 已关闭合格步骤除以已达到关闭期限的启动步骤。"""

    return _bounded_rate(
        "eligible_step_closure_rate",
        closed_eligible_steps,
        eligible_started_steps,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def closed_step_record_completeness(
    complete_closed_step_records: float | None,
    closed_steps: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Complete closed-step records divided by all closed steps. / 完整闭环记录除以全部已关闭步骤。"""

    return _bounded_rate(
        "closed_step_record_completeness",
        complete_closed_step_records,
        closed_steps,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def route_stability_rate(
    runs_without_route_insufficiency_switch: float | None,
    runs_with_valid_initial_route: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Measure route stability, explicitly not route accuracy. / 衡量路由稳定性，明确不代表路由准确率。"""

    return _bounded_rate(
        "route_stability_rate",
        runs_without_route_insufficiency_switch,
        runs_with_valid_initial_route,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def outcome_route_accuracy(
    correct_routes_with_outcome: float | None,
    routed_runs_with_outcome: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Correct routes divided by routed runs with known outcomes. / 正确路由除以已有真实后验的路由运行。"""

    return _bounded_rate(
        "outcome_route_accuracy",
        correct_routes_with_outcome,
        routed_runs_with_outcome,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def outcome_linkage_coverage(
    trustworthy_linked_route_outcomes: float | None,
    completed_route_atoms_eligible_for_outcome_linkage: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Trustworthy route outcomes divided by eligible completed atoms.

    / 可信路由后验数除以符合后验关联条件的已完成任务原子数。
    """

    return _bounded_rate(
        "outcome_linkage_coverage",
        trustworthy_linked_route_outcomes,
        completed_route_atoms_eligible_for_outcome_linkage,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def underroute_rate(
    atoms_succeeding_only_after_route_insufficiency_upgrade: float | None,
    completed_atoms_with_auditable_route_outcome: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Outcome-audited atoms that required a route-insufficiency upgrade.

    / 经后验审计且必须因路由不足升级后才成功的任务原子比例。
    """

    return _bounded_rate(
        "underroute_rate",
        atoms_succeeding_only_after_route_insufficiency_upgrade,
        completed_atoms_with_auditable_route_outcome,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def overroute_rate(
    audited_atoms_where_lighter_route_meets_same_validators: float | None,
    atoms_in_valid_counterfactual_audit_sample: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Counterfactually audited atoms for which a lighter route is sufficient.

    / 反事实审计中更轻路由仍满足同一验证器的任务原子比例。
    """

    return _bounded_rate(
        "overroute_rate",
        audited_atoms_where_lighter_route_meets_same_validators,
        atoms_in_valid_counterfactual_audit_sample,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def route_abstention_rate(
    abstained_route_decisions: float | None,
    route_decisions_with_complete_identity: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Explicit abstentions among identity-complete route decisions.

    / 身份完整路由决定中的显式弃权比例。
    """

    return _bounded_rate(
        "route_abstention_rate",
        abstained_route_decisions,
        route_decisions_with_complete_identity,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def route_oscillation_rate(
    atoms_exceeding_scene_switch_or_reversal_threshold: float | None,
    atoms_with_complete_switch_chain: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Atoms whose complete route history crosses the owned oscillation threshold.

    / 完整路由历史超过场景换路或往返阈值的任务原子比例。
    """

    return _bounded_rate(
        "route_oscillation_rate",
        atoms_exceeding_scene_switch_or_reversal_threshold,
        atoms_with_complete_switch_chain,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def forced_route_with_missing_signal_rate(
    executable_routes_with_required_signal_missing_or_unknown: float | None,
    executable_routes: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Executable routes that violated the required-signal fail-closed rule.

    / 违反必需信号缺失即阻断规则的可执行路由比例。
    """

    return _bounded_rate(
        "forced_route_with_missing_signal_rate",
        executable_routes_with_required_signal_missing_or_unknown,
        executable_routes,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def hypothesis_elimination_per_iteration(
    hypotheses_eliminated_by_valid_evidence: float | None,
    completed_iterations: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Valid hypothesis eliminations per iteration. / 每轮迭代的有效假设淘汰数。"""

    return safe_ratio(
        "hypothesis_elimination_per_iteration",
        hypotheses_eliminated_by_valid_evidence,
        completed_iterations,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def hypothesis_elimination_per_cost_unit(
    hypotheses_eliminated_by_valid_evidence: float | None,
    observed_cost_units: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Valid hypothesis eliminations per cost unit. / 每单位成本的有效假设淘汰数。"""

    return safe_ratio(
        "hypothesis_elimination_per_cost_unit",
        hypotheses_eliminated_by_valid_evidence,
        observed_cost_units,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def budget_utilization_vector(
    actual_use: Mapping[str, float | None] | None,
    configured_limits: Mapping[str, float | None] | None,
    *,
    min_sample: float = 1,
) -> MetricResult:
    """Return per-dimension utilization without mixing units. / 返回不混合单位的分维度预算利用率。"""

    metric_id = "budget_utilization_vector"
    if actual_use is None or configured_limits is None:
        return unavailable_metric(
            metric_id,
            MetricState.MISSING,
            "actual_use_or_limits_missing",
        )
    if not configured_limits:
        return unavailable_metric(
            metric_id,
            MetricState.NOT_APPLICABLE,
            "no_configured_budget_dimensions",
        )

    minimum = _finite_nonnegative("min_sample", min_sample)
    values: dict[str, float] = {}
    states: dict[str, str] = {}
    reasons: dict[str, str] = {}
    configured_dimensions: set[str] = set()
    for dimension in sorted(configured_limits):
        configured_limit = configured_limits[dimension]
        if configured_limit is None:
            states[dimension] = MetricState.NOT_APPLICABLE.value
            reasons[dimension] = "unconfigured_limit"
            continue
        normalized_limit = _finite_nonnegative(
            f"configured_limits[{dimension}]",
            configured_limit,
        )
        if normalized_limit == 0:
            raise ValueError(f"configured_limits[{dimension}] must be greater than zero")
        configured_dimensions.add(dimension)
        result = safe_ratio(
            f"{metric_id}.{dimension}",
            actual_use.get(dimension),
            normalized_limit,
            min_sample=0,
        )
        states[dimension] = result.state.value
        if result.reason is not None:
            reasons[dimension] = result.reason
        if isinstance(result.value, float):
            values[dimension] = result.value

    details: dict[str, Any] = {
        "dimension_states": states,
        "dimension_reasons": reasons,
        "partial_utilization_vector": values,
        "unconfigured_actual_dimensions": sorted(
            set(actual_use) - configured_dimensions
        ),
    }
    configured_states = {states[dimension] for dimension in configured_dimensions}
    if not configured_dimensions:
        state = MetricState.NOT_APPLICABLE
        reason = "no_configured_budget_dimensions"
    elif len(configured_dimensions) < minimum:
        state = MetricState.INSUFFICIENT_SAMPLE
        reason = "sample_below_minimum"
        details["minimum_sample"] = minimum
        details["sample_size"] = len(configured_dimensions)
    elif MetricState.MISSING.value in configured_states:
        state = MetricState.MISSING
        reason = "one_or_more_budget_dimensions_missing"
    elif MetricState.UNKNOWN.value in configured_states:
        state = MetricState.UNKNOWN
        reason = "one_or_more_budget_dimensions_unknown"
    elif values and all(value == 0 for value in values.values()):
        state = MetricState.OBSERVED_ZERO
        reason = None
    else:
        state = MetricState.COMPUTED
        reason = None

    return MetricResult(
        metric_id=metric_id,
        state=state,
        value=(
            values
            if state in {MetricState.OBSERVED_ZERO, MetricState.COMPUTED}
            else None
        ),
        sample_size=float(len(configured_dimensions)),
        reason=reason,
        details=details,
    )


def max_budget_utilization(
    actual_use: Mapping[str, float | None] | None,
    configured_limits: Mapping[str, float | None] | None,
    *,
    min_sample: float = 1,
) -> MetricResult:
    """Return the maximum valid budget-dimension utilization. / 返回有效预算维度中的最大利用率。"""

    vector = budget_utilization_vector(
        actual_use,
        configured_limits,
        min_sample=min_sample,
    )
    metric_id = "max_budget_utilization"
    if not vector.is_available or not isinstance(vector.value, dict):
        return MetricResult(
            metric_id=metric_id,
            state=vector.state,
            sample_size=vector.sample_size,
            reason=vector.reason,
            details={"vector": vector.details},
        )
    maximum_dimension, maximum = max(vector.value.items(), key=lambda item: item[1])
    state = MetricState.OBSERVED_ZERO if maximum == 0 else MetricState.COMPUTED
    return MetricResult(
        metric_id=metric_id,
        state=state,
        value=maximum,
        sample_size=vector.sample_size,
        details={
            "maximum_dimension": maximum_dimension,
            "utilization_vector": vector.value,
        },
    )


def event_chain_completeness(
    linkable_expected_runs: float | None,
    expected_runs: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Linkable runs divided by the external inventory of expected runs. / 可关联运行除以外部清单中的预期运行。"""

    return _bounded_rate(
        "event_chain_completeness",
        linkable_expected_runs,
        expected_runs,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def validation_coverage(
    runs_executing_all_mandatory_validators: float | None,
    runs_requiring_validation: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Runs with all mandatory validators divided by runs requiring validation. / 完成全部必选验证的运行除以需验证运行。"""

    return _bounded_rate(
        "validation_coverage",
        runs_executing_all_mandatory_validators,
        runs_requiring_validation,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def false_release_rate(
    confirmed_false_releases: float | None,
    auto_released_runs_with_outcome: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Confirmed false releases among auto-releases with known outcomes. / 已知后验自动放行中的确认误放行率。"""

    return _bounded_rate(
        "false_release_rate",
        confirmed_false_releases,
        auto_released_runs_with_outcome,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def event_loss_rate(
    expected_but_missing_events: float | None,
    expected_events: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Expected but missing events divided by expected events. / 预期但缺失事件除以预期事件。"""

    return _bounded_rate(
        "event_loss_rate",
        expected_but_missing_events,
        expected_events,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def duplicate_event_rate(
    duplicate_events: float | None,
    received_events: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Duplicate events divided by received events. / 重复事件除以接收事件。"""

    return _bounded_rate(
        "duplicate_event_rate",
        duplicate_events,
        received_events,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def parse_failure_rate(
    version_unparseable_events: float | None,
    received_events: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Version-unparseable events divided by received events. / 版本不可解析事件除以接收事件。"""

    return _bounded_rate(
        "parse_failure_rate",
        version_unparseable_events,
        received_events,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def validation_pass_rate(
    runs_passing_all_mandatory_validators: float | None,
    runs_with_valid_validation_results: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return the mandatory-validator pass rate. / 返回必选验证器通过率。"""

    return bounded_ratio(
        "validation_pass_rate",
        runs_passing_all_mandatory_validators,
        runs_with_valid_validation_results,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def cost_per_validated_success(
    total_cost_units: float | None,
    validated_completed_runs: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return cost units per validated completed run. / 返回每个验证成功运行的成本单位。"""

    return unbounded_ratio(
        "cost_per_validated_success",
        total_cost_units,
        validated_completed_runs,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def reasoning_drift_rate(
    long_runs_with_unapproved_goal_constraint_or_fact_drift: float | None,
    long_runs_with_comparable_snapshots: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return unapproved goal, constraint, or fact drift rate. / 返回未经批准的目标、约束或事实漂移率。"""

    return bounded_ratio(
        "reasoning_drift_rate",
        long_runs_with_unapproved_goal_constraint_or_fact_drift,
        long_runs_with_comparable_snapshots,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def contract_completeness(
    runs_with_all_required_contract_fields: float | None,
    runs_requiring_contract: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return complete reasoning contracts among required runs. / 返回需建契约运行中的完整契约率。"""

    return bounded_ratio(
        "contract_completeness",
        runs_with_all_required_contract_fields,
        runs_requiring_contract,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def evidence_traceability(
    evidence_with_source_version_or_time_and_location: float | None,
    referenced_evidence: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return traceable referenced evidence rate. / 返回引用证据的可追踪率。"""

    return bounded_ratio(
        "evidence_traceability",
        evidence_with_source_version_or_time_and_location,
        referenced_evidence,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def stop_reason_completeness(
    terminal_runs_with_valid_stop_or_escalation_reason: float | None,
    terminal_runs: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return valid stop-or-escalation reason coverage. / 返回有效停止或升级原因覆盖率。"""

    return bounded_ratio(
        "stop_reason_completeness",
        terminal_runs_with_valid_stop_or_escalation_reason,
        terminal_runs,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def probe_completion_rate(
    reliably_completed_fields: float | None,
    fields_classified_as_completable: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return reliable completion among completable fields. / 返回可补全字段中的可靠补全率。"""

    return bounded_ratio(
        "probe_completion_rate",
        reliably_completed_fields,
        fields_classified_as_completable,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def evidence_coverage(
    key_claims_with_valid_support: float | None,
    key_claims: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return valid-evidence coverage of key claims. / 返回关键主张的有效证据覆盖率。"""

    return bounded_ratio(
        "evidence_coverage",
        key_claims_with_valid_support,
        key_claims,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def unsupported_conclusion_rate(
    key_conclusions_without_evidence_and_not_labeled_inference: float | None,
    key_conclusions: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return unsupported, unlabeled key-conclusion rate. / 返回无证据且未标注推断的关键结论率。"""

    return bounded_ratio(
        "unsupported_conclusion_rate",
        key_conclusions_without_evidence_and_not_labeled_inference,
        key_conclusions,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def unverified_premise_propagation(
    unverified_premises_reused_as_fact: float | None,
    reused_premises: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return propagation of unverified premises reused as facts. / 返回未验证前提被当作事实复用的传播率。"""

    return bounded_ratio(
        "unverified_premise_propagation",
        unverified_premises_reused_as_fact,
        reused_premises,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def material_candidate_difference(
    materially_distinct_candidates: float | None,
    all_candidates: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return materially distinct candidates among all candidates. / 返回全部候选中的实质差异候选率。"""

    return bounded_ratio(
        "material_candidate_difference",
        materially_distinct_candidates,
        all_candidates,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def candidate_completion_rate(
    candidate_paths_with_terminal_record: float | None,
    planned_candidate_paths: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return planned candidate paths with an auditable terminal. / 返回具有可审计终态的计划候选路径比例。"""

    return bounded_ratio(
        "candidate_completion_rate",
        candidate_paths_with_terminal_record,
        planned_candidate_paths,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def branch_diversity(
    distinct_candidate_bindings: float | None,
    completed_candidate_paths: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return distinct candidate bindings among completed paths. / 返回完成路径中不同候选绑定的比例。"""

    return bounded_ratio(
        "branch_diversity",
        distinct_candidate_bindings,
        completed_candidate_paths,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def branch_record_completeness(
    complete_terminal_branch_records: float | None,
    terminal_branch_records: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return complete branch records among explicit terminals. / 返回显式终态中完整分支记录的比例。"""

    return bounded_ratio(
        "branch_record_completeness",
        complete_terminal_branch_records,
        terminal_branch_records,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def path_convergence_rate(
    parallel_runs_selecting_a_validated_path: float | None,
    parallel_runs_completing_comparison: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return validated-path convergence among completed comparisons. / 返回完成比较运行中的有效路径收敛率。"""

    return bounded_ratio(
        "path_convergence_rate",
        parallel_runs_selecting_a_validated_path,
        parallel_runs_completing_comparison,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def no_progress_loop_rate(
    iterative_runs_hitting_configured_no_progress_streak: float | None,
    iterative_runs: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return runs reaching the configured no-progress streak. / 返回达到配置无进展连续阈值的运行率。"""

    return bounded_ratio(
        "no_progress_loop_rate",
        iterative_runs_hitting_configured_no_progress_streak,
        iterative_runs,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def budget_overrun_rate(
    runs_exceeding_any_budget_dimension: float | None,
    runs_with_budget_record: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return runs exceeding at least one budget dimension. / 返回至少一个预算维度越界的运行率。"""

    return bounded_ratio(
        "budget_overrun_rate",
        runs_exceeding_any_budget_dimension,
        runs_with_budget_record,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def tool_success_rate(
    successful_structurally_valid_tool_calls: float | None,
    tool_calls: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return structurally valid tool-call success rate. / 返回结构有效的工具调用成功率。"""

    return bounded_ratio(
        "tool_success_rate",
        successful_structurally_valid_tool_calls,
        tool_calls,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def retry_amplification(
    actual_calls_including_retries: float | None,
    deduplicated_logical_calls: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return physical calls per deduplicated logical call. / 返回每个去重逻辑调用对应的实际调用数。"""

    if actual_calls_including_retries is not None and deduplicated_logical_calls is not None:
        actual = _finite_nonnegative(
            "actual_calls_including_retries",
            actual_calls_including_retries,
        )
        logical = _finite_nonnegative(
            "deduplicated_logical_calls",
            deduplicated_logical_calls,
        )
        if actual < logical:
            raise ValueError("actual calls cannot be fewer than logical calls")
    return unbounded_ratio(
        "retry_amplification",
        actual_calls_including_retries,
        deduplicated_logical_calls,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def probe_coverage(
    required_stages_with_required_probes: float | None,
    required_stages: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return required workflow-stage probe coverage. / 返回必需工作流阶段的探针覆盖率。"""

    return bounded_ratio(
        "probe_coverage",
        required_stages_with_required_probes,
        required_stages,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def alert_delivery_rate(
    delivered_alerts: float | None,
    alerts_due: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return delivered alerts among alerts due. / 返回应送达告警中的实际送达率。"""

    return bounded_ratio(
        "alert_delivery_rate",
        delivered_alerts,
        alerts_due,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def plan_compile_success_rate(
    successful_plan_compilations: float | None,
    plan_compilation_attempts: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return successful sealed-plan compilations. / 返回密封计划编译成功率。"""

    return bounded_ratio(
        "plan_compile_success_rate",
        successful_plan_compilations,
        plan_compilation_attempts,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def plan_drift_rate(
    chain_runs_with_plan_drift: float | None,
    inspected_chain_runs: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return inspected chain runs with detected plan drift. / 返回已检查链式运行中的计划漂移率。"""

    return bounded_ratio(
        "plan_drift_rate",
        chain_runs_with_plan_drift,
        inspected_chain_runs,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def checkpoint_validation_binding_rate(
    checkpoint_validations_with_complete_bindings: float | None,
    checkpoint_validations: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return checkpoint validations with complete immutable bindings. / 返回不可变绑定完整的检查点验证率。"""

    return bounded_ratio(
        "checkpoint_validation_binding_rate",
        checkpoint_validations_with_complete_bindings,
        checkpoint_validations,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def budget_pre_reservation_coverage(
    steps_reserved_before_start: float | None,
    started_chain_steps: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return chain steps whose allocation was reserved before start. / 返回启动前已预留分配预算的链式步骤覆盖率。"""

    return bounded_ratio(
        "budget_pre_reservation_coverage",
        steps_reserved_before_start,
        started_chain_steps,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def evidence_resolution_rate(
    resolved_step_evidence_bindings: float | None,
    step_evidence_bindings: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return step evidence bindings resolved to immutable records. / 返回解析到不可变记录的步骤证据绑定率。"""

    return bounded_ratio(
        "evidence_resolution_rate",
        resolved_step_evidence_bindings,
        step_evidence_bindings,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def candidate_evidence_lineage_integrity_rate(
    candidates_with_complete_revision_lineage: float | None,
    inspected_plan_bound_candidates: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return inspected candidates with complete exact evidence lineage. / 返回具备完整精确证据血缘的已检查候选比例。"""

    return bounded_ratio(
        "candidate_evidence_lineage_integrity_rate",
        candidates_with_complete_revision_lineage,
        inspected_plan_bound_candidates,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def readonly_tool_lifecycle_completion_rate(
    readonly_tool_dispatches_with_one_matching_observation: float | None,
    readonly_tool_dispatches_due_for_observation: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return read-only dispatches closed by one matching observation. / 返回由唯一匹配观测关闭的只读工具分派比例。"""

    return bounded_ratio(
        "readonly_tool_lifecycle_completion_rate",
        readonly_tool_dispatches_with_one_matching_observation,
        readonly_tool_dispatches_due_for_observation,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def dispatch_admission_coverage(
    executions_with_valid_admission: float | None,
    execution_starts: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return execution starts backed by sealed admission / 返回具有封存准入的执行开始比例。"""

    return bounded_ratio(
        "dispatch_admission_coverage",
        executions_with_valid_admission,
        execution_starts,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def side_effect_lease_coverage(
    side_effecting_executions_with_valid_lease: float | None,
    side_effecting_execution_starts: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return side-effect starts holding durable leases / 返回持有持久租约的副作用执行比例。"""

    return bounded_ratio(
        "side_effect_lease_coverage",
        side_effecting_executions_with_valid_lease,
        side_effecting_execution_starts,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def state_evidence_coverage(
    write_executions_with_current_state_evidence: float | None,
    write_executions_requiring_state_evidence: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return writes with current version evidence / 返回具备当前版本证据的写执行比例。"""

    return bounded_ratio(
        "state_evidence_coverage",
        write_executions_with_current_state_evidence,
        write_executions_requiring_state_evidence,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def approval_binding_coverage(
    approval_bound_execution_starts: float | None,
    approval_required_execution_starts: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return approval-required starts with exact bindings / 返回具备精确审批绑定的执行比例。"""

    return bounded_ratio(
        "approval_binding_coverage",
        approval_bound_execution_starts,
        approval_required_execution_starts,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def frontier_escape_rate(
    frontier_escape_executions: float | None,
    execution_starts: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return executions outside their sealed frontier / 返回封存能力前沿外执行比例。"""

    return bounded_ratio(
        "frontier_escape_rate",
        frontier_escape_executions,
        execution_starts,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def dispatch_record_completeness(
    complete_dispatch_records: float | None,
    dispatch_records: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return dispatch records with complete lifecycle linkage / 返回生命周期关联完整的调度记录比例。"""

    return bounded_ratio(
        "dispatch_record_completeness",
        complete_dispatch_records,
        dispatch_records,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def result_unknown_rate(
    unknown_results: float | None,
    executed_results: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return executed actions with unknown results / 返回已执行动作的结果未知比例。"""

    return bounded_ratio(
        "result_unknown_rate",
        unknown_results,
        executed_results,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def duplicate_side_effect_rate(
    duplicate_side_effects: float | None,
    confirmed_side_effect_results: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return duplicate confirmed side effects / 返回重复已确认副作用比例。"""

    return bounded_ratio(
        "duplicate_side_effect_rate",
        duplicate_side_effects,
        confirmed_side_effect_results,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def reflection_admission_compliance(
    compliant_admitted_reflections: float | None,
    auto_reflection_instances: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return contract-complete automatic reflection admissions / 返回契约完整的自动反思准入率。"""

    return bounded_ratio(
        "reflection_admission_compliance",
        compliant_admitted_reflections,
        auto_reflection_instances,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def reflection_closure_rate(
    closed_reflection_rounds: float | None,
    started_reflection_rounds: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return rounds with complete event and terminal closure / 返回事件链与终态完整的反思轮次闭环率。"""

    return bounded_ratio(
        "reflection_closure_rate",
        closed_reflection_rounds,
        started_reflection_rounds,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def independent_revalidation_coverage(
    independently_revalidated_rounds: float | None,
    rounds_requiring_revalidation: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return version-bound independent revalidation coverage / 返回绑定版本的独立复验覆盖率。"""

    return bounded_ratio(
        "independent_revalidation_coverage",
        independently_revalidated_rounds,
        rounds_requiring_revalidation,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def improvement_comparability_coverage(
    comparable_improvement_assessments: float | None,
    improvement_assessments: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return baseline-comparable improvement assessments / 返回基线可比的改善评估覆盖率。"""

    return bounded_ratio(
        "improvement_comparability_coverage",
        comparable_improvement_assessments,
        improvement_assessments,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def regression_free_verified_improvement_rate(
    regression_free_verified_improvements: float | None,
    completed_revalidation_rounds: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return verified improvements that preserve regression guards / 返回保持回归护栏的已验证改善率。"""

    return bounded_ratio(
        "regression_free_verified_improvement_rate",
        regression_free_verified_improvements,
        completed_revalidation_rounds,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def validator_gaming_rate(
    validator_gaming_rounds: float | None,
    changed_rounds: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return rounds that game or weaken their verifier / 返回投机或削弱验证器的改变轮次比例。"""

    return bounded_ratio(
        "validator_gaming_rate",
        validator_gaming_rounds,
        changed_rounds,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def qualified_new_signal_rate(
    rounds_with_qualified_new_signal: float | None,
    admitted_reflection_rounds: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return admitted rounds with a qualified new result signal / 返回具备有效新结果信号的已准入轮次比例。"""

    return bounded_ratio(
        "qualified_new_signal_rate",
        rounds_with_qualified_new_signal,
        admitted_reflection_rounds,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def attribution_overclaim_rate(
    overclaimed_attribution_records: float | None,
    attribution_claim_records: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return attribution claims stronger than their evidence / 返回归因强度超过证据等级的记录比例。"""

    return bounded_ratio(
        "attribution_overclaim_rate",
        overclaimed_attribution_records,
        attribution_claim_records,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def learning_promotion_evidence_completeness(
    complete_learning_promotion_records: float | None,
    learning_promotion_records: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return evidence-complete memory or Skill promotions / 返回证据完整的记忆或 Skill 晋升记录比例。"""

    return bounded_ratio(
        "learning_promotion_evidence_completeness",
        complete_learning_promotion_records,
        learning_promotion_records,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def generator_critic_review_version_match_rate(
    exact_version_review_records: float | None,
    review_records: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return reviews bound to the exact artifact version / 返回绑定精确工件版本的评审比例。"""

    return bounded_ratio(
        "generator_critic_review_version_match_rate",
        exact_version_review_records,
        review_records,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def generator_critic_revision_rereview_compliance_rate(
    rereviewed_revised_artifacts: float | None,
    revised_artifacts_entering_release: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return revised artifacts explicitly re-reviewed before release / 返回发布前已显式复审修订工件比例。"""

    return bounded_ratio(
        "generator_critic_revision_rereview_compliance_rate",
        rereviewed_revised_artifacts,
        revised_artifacts_entering_release,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def generator_critic_receipt_coverage_rate(
    accepted_versions_with_valid_receipt: float | None,
    accepted_versions_entering_release: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return accepted versions carrying a valid release receipt / 返回具有有效发布回执的接受版本比例。"""

    return bounded_ratio(
        "generator_critic_receipt_coverage_rate",
        accepted_versions_with_valid_receipt,
        accepted_versions_entering_release,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def generator_critic_version_escape_rate(
    released_version_escapes: float | None,
    released_reviewed_artifacts: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return releases that escape their reviewed artifact binding / 返回逃逸已评审工件绑定的发布比例。"""

    return bounded_ratio(
        "generator_critic_version_escape_rate",
        released_version_escapes,
        released_reviewed_artifacts,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def generator_critic_evidenced_finding_rate(
    evidenced_findings: float | None,
    reported_findings_and_opinions: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return reported findings backed by auditable evidence / 返回具有可审计证据的已报告问题比例。"""

    return bounded_ratio(
        "generator_critic_evidenced_finding_rate",
        evidenced_findings,
        reported_findings_and_opinions,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def generator_critic_opinion_retention_rate(
    retained_non_gating_opinions: float | None,
    unsupported_opinions: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return unsupported opinions retained as non-gating records / 返回作为非门控记录留存的无据意见比例。"""

    return bounded_ratio(
        "generator_critic_opinion_retention_rate",
        retained_non_gating_opinions,
        unsupported_opinions,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def generator_critic_risk_evidence_coverage_rate(
    risk_items_with_check_and_evidence: float | None,
    declared_material_risk_items: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return material risks covered by checks and evidence / 返回由检查与证据覆盖的重大风险比例。"""

    return bounded_ratio(
        "generator_critic_risk_evidence_coverage_rate",
        risk_items_with_check_and_evidence,
        declared_material_risk_items,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def generator_critic_rubber_stamp_escape_rate(
    accepted_artifacts_with_downstream_covered_defect: float | None,
    accepted_artifacts_with_outcome_evidence: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return accepted artifacts with later in-scope defects / 返回后续发现范围内缺陷的接受工件比例。"""

    return bounded_ratio(
        "generator_critic_rubber_stamp_escape_rate",
        accepted_artifacts_with_downstream_covered_defect,
        accepted_artifacts_with_outcome_evidence,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def generator_critic_pass_budget_compliance_rate(
    sessions_within_critique_pass_budget: float | None,
    generator_critic_sessions: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return sessions closed within the sealed critique-pass budget / 返回在封存评审批次预算内闭环的会话比例。"""

    return bounded_ratio(
        "generator_critic_pass_budget_compliance_rate",
        sessions_within_critique_pass_budget,
        generator_critic_sessions,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def skill_candidate_recurrence_evidence_rate(
    candidates_meeting_recurrence_policy: float | None,
    nominated_skill_candidates: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return nominations backed by recurrent successful runs / 返回由重复成功运行支撑的提名比例。"""

    return bounded_ratio(
        "skill_candidate_recurrence_evidence_rate",
        candidates_meeting_recurrence_policy,
        nominated_skill_candidates,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def skill_package_contract_completeness_rate(
    complete_skill_package_contracts: float | None,
    registered_trial_packages: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return TRIAL packages with complete sealed boundaries / 返回具有完整封存边界的 TRIAL 技能包比例。"""

    return bounded_ratio(
        "skill_package_contract_completeness_rate",
        complete_skill_package_contracts,
        registered_trial_packages,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def skill_package_five_dimension_verification_rate(
    packages_passing_all_five_dimensions: float | None,
    completed_skill_package_evaluations: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return evaluations passing all five independent dimensions / 返回通过全部五个独立维度的评估比例。"""

    return bounded_ratio(
        "skill_package_five_dimension_verification_rate",
        packages_passing_all_five_dimensions,
        completed_skill_package_evaluations,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def trial_to_verified_rate(
    trial_versions_promoted_verified: float | None,
    trial_versions_with_completed_evaluation: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return evaluated TRIAL versions promoted to VERIFIED / 返回已评估 TRIAL 版本中晋升 VERIFIED 的比例。"""

    return bounded_ratio(
        "trial_to_verified_rate",
        trial_versions_promoted_verified,
        trial_versions_with_completed_evaluation,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def credential_exact_binding_rate(
    credentials_with_exact_binding: float | None,
    issued_skill_credentials: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return credentials matching contract, manifest, evaluation, and scope / 返回精确匹配契约、清单、评估与权限范围的凭证比例。"""

    return bounded_ratio(
        "credential_exact_binding_rate",
        credentials_with_exact_binding,
        issued_skill_credentials,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def alias_switch_integrity_rate(
    valid_atomic_alias_switches: float | None,
    production_alias_switch_attempts: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return production switches with valid exact-version CAS receipts / 返回具有有效精确版本 CAS 回执的生产切换比例。"""

    return bounded_ratio(
        "alias_switch_integrity_rate",
        valid_atomic_alias_switches,
        production_alias_switch_attempts,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def skill_reuse_success_rate(
    successful_real_skill_reuses: float | None,
    real_skill_reuses_with_determined_outcome: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return real production reuses with successful external outcomes / 返回外部结果成功的真实生产复用比例。"""

    return bounded_ratio(
        "skill_reuse_success_rate",
        successful_real_skill_reuses,
        real_skill_reuses_with_determined_outcome,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def version_window_integrity_rate(
    real_reuses_with_valid_version_window: float | None,
    real_skill_reuses: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return reuses inside the exact credential and alias window / 返回位于精确凭证与别名时间窗内的复用比例。"""

    return bounded_ratio(
        "version_window_integrity_rate",
        real_reuses_with_valid_version_window,
        real_skill_reuses,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def reverification_prewithdrawal_compliance_rate(
    reverifications_with_prior_withdrawal: float | None,
    skill_reverifications_started: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return re-verifications preceded by suspension and demotion / 返回开始前已暂停凭证并降级的复验比例。"""

    return bounded_ratio(
        "reverification_prewithdrawal_compliance_rate",
        reverifications_with_prior_withdrawal,
        skill_reverifications_started,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def stale_credential_use_rate(
    reuses_with_stale_or_inactive_credential: float | None,
    real_skill_reuses: float | None,
    *,
    min_sample: float = 1,
    unavailable_state: MetricState | None = None,
) -> MetricResult:
    """Return real reuses using stale, suspended, expired, or revoked credentials / 返回使用过时、暂停、过期或撤销凭证的真实复用比例。"""

    return bounded_ratio(
        "stale_credential_use_rate",
        reuses_with_stale_or_inactive_credential,
        real_skill_reuses,
        min_sample=min_sample,
        unavailable_state=unavailable_state,
    )


def budget_utilization_max(
    actual_use: Mapping[str, float | None] | None,
    configured_limits: Mapping[str, float | None] | None,
    *,
    min_sample: float = 1,
) -> MetricResult:
    """Compatibility alias for maximum budget utilization. / 最大预算利用率的兼容别名。"""

    return max_budget_utilization(
        actual_use,
        configured_limits,
        min_sample=min_sample,
    )


_METRIC_FUNCTIONS = {
    "eligible_step_closure_rate": eligible_step_closure_rate,
    "closed_step_record_completeness": closed_step_record_completeness,
    "route_stability_rate": route_stability_rate,
    "outcome_route_accuracy": outcome_route_accuracy,
    "outcome_linkage_coverage": outcome_linkage_coverage,
    "underroute_rate": underroute_rate,
    "overroute_rate": overroute_rate,
    "route_abstention_rate": route_abstention_rate,
    "route_oscillation_rate": route_oscillation_rate,
    "forced_route_with_missing_signal_rate": forced_route_with_missing_signal_rate,
    "hypothesis_elimination_per_iteration": hypothesis_elimination_per_iteration,
    "hypothesis_elimination_per_cost_unit": hypothesis_elimination_per_cost_unit,
    "budget_utilization_vector": budget_utilization_vector,
    "max_budget_utilization": max_budget_utilization,
    "event_chain_completeness": event_chain_completeness,
    "validation_coverage": validation_coverage,
    "false_release_rate": false_release_rate,
    "event_loss_rate": event_loss_rate,
    "duplicate_event_rate": duplicate_event_rate,
    "parse_failure_rate": parse_failure_rate,
    "validation_pass_rate": validation_pass_rate,
    "cost_per_validated_success": cost_per_validated_success,
    "reasoning_drift_rate": reasoning_drift_rate,
    "contract_completeness": contract_completeness,
    "evidence_traceability": evidence_traceability,
    "stop_reason_completeness": stop_reason_completeness,
    "probe_completion_rate": probe_completion_rate,
    "evidence_coverage": evidence_coverage,
    "unsupported_conclusion_rate": unsupported_conclusion_rate,
    "unverified_premise_propagation": unverified_premise_propagation,
    "material_candidate_difference": material_candidate_difference,
    "candidate_completion_rate": candidate_completion_rate,
    "branch_diversity": branch_diversity,
    "branch_record_completeness": branch_record_completeness,
    "path_convergence_rate": path_convergence_rate,
    "no_progress_loop_rate": no_progress_loop_rate,
    "budget_overrun_rate": budget_overrun_rate,
    "tool_success_rate": tool_success_rate,
    "retry_amplification": retry_amplification,
    "probe_coverage": probe_coverage,
    "alert_delivery_rate": alert_delivery_rate,
    "plan_compile_success_rate": plan_compile_success_rate,
    "plan_drift_rate": plan_drift_rate,
    "checkpoint_validation_binding_rate": checkpoint_validation_binding_rate,
    "budget_pre_reservation_coverage": budget_pre_reservation_coverage,
    "evidence_resolution_rate": evidence_resolution_rate,
    "candidate_evidence_lineage_integrity_rate": candidate_evidence_lineage_integrity_rate,
    "readonly_tool_lifecycle_completion_rate": readonly_tool_lifecycle_completion_rate,
    "dispatch_admission_coverage": dispatch_admission_coverage,
    "side_effect_lease_coverage": side_effect_lease_coverage,
    "state_evidence_coverage": state_evidence_coverage,
    "approval_binding_coverage": approval_binding_coverage,
    "frontier_escape_rate": frontier_escape_rate,
    "dispatch_record_completeness": dispatch_record_completeness,
    "result_unknown_rate": result_unknown_rate,
    "duplicate_side_effect_rate": duplicate_side_effect_rate,
    "reflection_admission_compliance": reflection_admission_compliance,
    "reflection_closure_rate": reflection_closure_rate,
    "independent_revalidation_coverage": independent_revalidation_coverage,
    "improvement_comparability_coverage": improvement_comparability_coverage,
    "regression_free_verified_improvement_rate": regression_free_verified_improvement_rate,
    "validator_gaming_rate": validator_gaming_rate,
    "qualified_new_signal_rate": qualified_new_signal_rate,
    "attribution_overclaim_rate": attribution_overclaim_rate,
    "learning_promotion_evidence_completeness": learning_promotion_evidence_completeness,
    "generator_critic_review_version_match_rate": generator_critic_review_version_match_rate,
    "generator_critic_revision_rereview_compliance_rate": generator_critic_revision_rereview_compliance_rate,
    "generator_critic_receipt_coverage_rate": generator_critic_receipt_coverage_rate,
    "generator_critic_version_escape_rate": generator_critic_version_escape_rate,
    "generator_critic_evidenced_finding_rate": generator_critic_evidenced_finding_rate,
    "generator_critic_opinion_retention_rate": generator_critic_opinion_retention_rate,
    "generator_critic_risk_evidence_coverage_rate": generator_critic_risk_evidence_coverage_rate,
    "generator_critic_rubber_stamp_escape_rate": generator_critic_rubber_stamp_escape_rate,
    "generator_critic_pass_budget_compliance_rate": generator_critic_pass_budget_compliance_rate,
    "skill_candidate_recurrence_evidence_rate": skill_candidate_recurrence_evidence_rate,
    "skill_package_contract_completeness_rate": skill_package_contract_completeness_rate,
    "skill_package_five_dimension_verification_rate": skill_package_five_dimension_verification_rate,
    "trial_to_verified_rate": trial_to_verified_rate,
    "credential_exact_binding_rate": credential_exact_binding_rate,
    "alias_switch_integrity_rate": alias_switch_integrity_rate,
    "skill_reuse_success_rate": skill_reuse_success_rate,
    "version_window_integrity_rate": version_window_integrity_rate,
    "reverification_prewithdrawal_compliance_rate": reverification_prewithdrawal_compliance_rate,
    "stale_credential_use_rate": stale_credential_use_rate,
}


def _load_metric_registry() -> dict[str, Any]:
    path = Path(__file__).with_name("metric_registry.json")
    registry = json.loads(path.read_text(encoding="utf-8"))
    records = registry.get("metrics")
    if not isinstance(records, list):
        raise RuntimeError("metric registry must contain a metrics list")
    identifiers = [record.get("metric_id") for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError("metric registry contains duplicate metric identifiers")
    required_buckets = registry.get("required_bucket_dimensions")
    if (
        not isinstance(required_buckets, list)
        or not required_buckets
        or any(not isinstance(name, str) or not name for name in required_buckets)
        or len(required_buckets) != len(set(required_buckets))
    ):
        raise RuntimeError(
            "metric registry must declare unique required_bucket_dimensions"
        )
    for record in records:
        minimum_sample = record.get("minimum_sample")
        if (
            isinstance(minimum_sample, bool)
            or not isinstance(minimum_sample, (int, float))
            or not math.isfinite(float(minimum_sample))
            or float(minimum_sample) < 1
        ):
            raise RuntimeError(
                f"metric minimum_sample must be finite and at least one: "
                f"{record.get('metric_id')}"
            )
    return registry


def _condition_id(description: Any) -> str:
    """Extract the stable machine token from bilingual condition text. / 从双语条件文本提取稳定机器标记。"""

    if not isinstance(description, str) or " / " not in description:
        raise RuntimeError(
            "probe condition must use '<condition_id> / <Chinese description>'"
        )
    condition_id = description.split(" / ", 1)[0].strip()
    if not condition_id or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789_"
        for character in condition_id
    ):
        raise RuntimeError(f"invalid probe condition identifier: {condition_id!r}")
    return condition_id


def _load_probe_registry() -> dict[str, Any]:
    """Load deployable versioned probe definitions. / 加载可部署的版本化探针定义。"""

    path = Path(__file__).with_name("probe_registry.json")
    registry = json.loads(path.read_text(encoding="utf-8"))
    records = registry.get("probes")
    if not isinstance(records, list) or not records:
        raise RuntimeError("probe registry must contain probe definitions")
    required_fields = {
        "probe_id",
        "version",
        "name_en",
        "name_zh",
        "owner",
        "trigger_event_types",
        "required_capture_fields",
        "output_event_type",
        "disposition",
    }
    identifiers: list[str] = []
    for record in records:
        if not isinstance(record, Mapping) or not required_fields <= set(record):
            raise RuntimeError("probe registry contains an incomplete definition")
        probe_id = record["probe_id"]
        if not isinstance(probe_id, str) or re.fullmatch(r"PROBE_\d{4}", probe_id) is None:
            raise RuntimeError(f"invalid probe identifier: {probe_id!r}")
        if (
            not isinstance(record["version"], str)
            or re.fullmatch(r"\d+\.\d+\.\d+", record["version"]) is None
        ):
            raise RuntimeError(f"invalid probe version: {probe_id}")
        for field_name in ("name_en", "name_zh", "owner", "output_event_type", "disposition"):
            if not isinstance(record[field_name], str) or not record[field_name]:
                raise RuntimeError(f"invalid probe {field_name}: {probe_id}")
        for field_name in ("trigger_event_types", "required_capture_fields"):
            values = record[field_name]
            if (
                not isinstance(values, list)
                or not values
                or any(not isinstance(value, str) or not value for value in values)
                or len(values) != len(set(values))
            ):
                raise RuntimeError(f"invalid probe {field_name}: {probe_id}")
        identifiers.append(probe_id)
    if len(identifiers) != len(set(identifiers)):
        raise RuntimeError("probe registry contains duplicate probe identifiers")
    return registry


def _load_probe_dependency_matrix() -> dict[str, Any]:
    path = Path(__file__).with_name("probe_dependency_matrix.json")
    matrix = json.loads(path.read_text(encoding="utf-8"))
    entries = matrix.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("probe dependency matrix must contain entries")
    modes = [entry.get("mode") for entry in entries if isinstance(entry, Mapping)]
    if len(modes) != len(entries) or len(modes) != len(set(modes)):
        raise RuntimeError("probe dependency matrix contains invalid or duplicate modes")
    for entry in entries:
        required = entry.get("required_probes")
        conditional = entry.get("conditional_probes")
        if (
            not isinstance(required, list)
            or not required
            or any(not isinstance(probe_id, str) or not probe_id for probe_id in required)
            or not isinstance(conditional, Mapping)
        ):
            raise RuntimeError(f"invalid probe dependency entry: {entry.get('mode')}")
        for probe_id, condition in conditional.items():
            if not isinstance(probe_id, str) or not probe_id:
                raise RuntimeError("conditional probe identifier must be non-empty")
            _condition_id(condition)
    return matrix


METRIC_REGISTRY = _load_metric_registry()
METRIC_DEFINITIONS = {
    record["metric_id"]: record for record in METRIC_REGISTRY["metrics"]
}
PROBE_REGISTRY = _load_probe_registry()
PROBE_DEFINITIONS = {
    record["probe_id"]: record for record in PROBE_REGISTRY["probes"]
}
PROBE_DEPENDENCY_MATRIX = _load_probe_dependency_matrix()
PROBE_DEPENDENCIES = {
    entry["mode"]: entry for entry in PROBE_DEPENDENCY_MATRIX["entries"]
}
UNIVERSAL_REQUIRED_PROBES = tuple(
    METRIC_REGISTRY.get("universal_required_probes", ())
)
_REFERENCED_PROBES = set(UNIVERSAL_REQUIRED_PROBES)
for _definition in METRIC_DEFINITIONS.values():
    _REFERENCED_PROBES.update(_definition.get("required_probes", ()))
for _entry in PROBE_DEPENDENCY_MATRIX["entries"]:
    _REFERENCED_PROBES.update(_entry["required_probes"])
    _REFERENCED_PROBES.update(_entry["conditional_probes"])
_UNKNOWN_PROBES = sorted(_REFERENCED_PROBES - set(PROBE_DEFINITIONS))
if _UNKNOWN_PROBES:
    raise RuntimeError(
        "metric and dependency registries reference undefined probes: "
        + ", ".join(_UNKNOWN_PROBES)
    )
_MANIFEST_REQUIRED_METRICS = {
    "event_chain_completeness",
    "event_loss_rate",
}


def _identifier_tuple(name: str, values: Iterable[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be an iterable of identifiers")
    normalized = tuple(values)
    if any(not isinstance(value, str) or not value for value in normalized):
        raise TypeError(f"{name} must contain non-empty strings")
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{name} cannot contain duplicates")
    return normalized


def resolve_required_probes(
    execution_mode: str,
    *,
    supporting_topologies: Iterable[str] = (),
    condition_states: Mapping[str, ProbeConditionState | str] | None = None,
) -> ProbeDependencyResolution:
    """Resolve probes only after every applicable condition is explicitly assessed.

    Missing, unknown, or inapplicable conditions fail closed so an unevaluated
    feature cannot silently suppress collection. / 仅在每个适用条件被显式评估后解析
    探针；缺失、未知或不适用条件默认阻断，避免漏评条件静默漏采。
    """

    runtime_modes = {"direct", "chain", "parallel", "iterative"}
    supporting_modes = {"orchestration", "hierarchy"}
    if execution_mode not in runtime_modes:
        raise ValueError(f"unknown execution mode: {execution_mode}")
    topologies = _identifier_tuple("supporting_topologies", supporting_topologies)
    unknown_topologies = sorted(set(topologies) - supporting_modes)
    if unknown_topologies:
        raise ValueError(f"unknown supporting topologies: {unknown_topologies}")
    selected_modes = (execution_mode, *topologies)
    entries = [PROBE_DEPENDENCIES[mode] for mode in selected_modes]

    applicable_conditions = {
        _condition_id(description)
        for entry in entries
        for description in entry["conditional_probes"].values()
    }
    if condition_states is None:
        raise ValueError(
            "condition_states must explicitly assess every applicable condition"
        )
    if not isinstance(condition_states, Mapping):
        raise TypeError("condition_states must be a mapping")
    supplied_conditions = set(condition_states)
    if any(not isinstance(name, str) or not name for name in supplied_conditions):
        raise TypeError("condition state names must be non-empty strings")
    missing_conditions = sorted(applicable_conditions - supplied_conditions)
    inapplicable = sorted(supplied_conditions - applicable_conditions)
    if missing_conditions or inapplicable:
        raise ValueError(
            "condition states do not match the applicable configuration; "
            f"missing={missing_conditions}, inapplicable={inapplicable}"
        )
    normalized_states: dict[str, str] = {}
    for condition_id in sorted(applicable_conditions):
        try:
            normalized_states[condition_id] = ProbeConditionState(
                condition_states[condition_id]
            ).value
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"invalid tri-state condition value: {condition_id}"
            ) from exc
    unknown_conditions = sorted(
        condition_id
        for condition_id, state in normalized_states.items()
        if state == ProbeConditionState.UNKNOWN.value
    )
    if unknown_conditions:
        raise ValueError(
            "conditional probe applicability is unknown: "
            + ", ".join(unknown_conditions)
        )

    required = set(PROBE_DEPENDENCY_MATRIX["universal_required_probes"])
    activated: list[tuple[str, str]] = []
    for entry in entries:
        required.update(entry["required_probes"])
        for probe_id, description in entry["conditional_probes"].items():
            condition_id = _condition_id(description)
            if normalized_states[condition_id] == ProbeConditionState.TRUE.value:
                required.add(probe_id)
                activated.append((probe_id, condition_id))
    return ProbeDependencyResolution(
        execution_mode=execution_mode,
        supporting_topologies=topologies,
        condition_states=tuple(sorted(normalized_states.items())),
        required_probes=tuple(sorted(required)),
        required_probe_bindings=tuple(
            (probe_id, PROBE_DEFINITIONS[probe_id]["version"])
            for probe_id in sorted(required)
        ),
        activated_conditionals=tuple(sorted(activated)),
    )


def calculate_metric(metric_id: str, inputs: Mapping[str, Any]) -> MetricResult:
    """Dispatch a registered metric using canonical keyword inputs. / 使用规范关键字输入调度已注册指标。"""

    if not isinstance(metric_id, str) or not metric_id:
        raise ValueError("metric_id must be a non-empty string")
    if not isinstance(inputs, Mapping):
        raise TypeError("inputs must be a mapping")
    if any(not isinstance(name, str) or not name for name in inputs):
        raise TypeError("metric input names must be non-empty strings")
    definition = METRIC_DEFINITIONS.get(metric_id)
    function = _METRIC_FUNCTIONS.get(metric_id)
    if definition is None or function is None:
        raise KeyError(f"unknown or unimplemented metric: {metric_id}")
    expected_inputs = tuple(definition.get("inputs", ()))
    supplied_inputs = set(inputs)
    missing = sorted(set(expected_inputs) - supplied_inputs)
    unexpected = sorted(supplied_inputs - set(expected_inputs))
    if missing or unexpected:
        raise ValueError(
            f"metric inputs do not match registry; missing={missing}, unexpected={unexpected}"
        )
    minimum_sample = definition.get("minimum_sample")
    if (
        isinstance(minimum_sample, bool)
        or not isinstance(minimum_sample, (int, float))
        or not math.isfinite(float(minimum_sample))
        or float(minimum_sample) < 1
    ):
        raise RuntimeError(
            f"metric registry contains an invalid minimum_sample: {metric_id}"
        )
    if "min_sample" not in inspect.signature(function).parameters:
        raise RuntimeError(
            f"metric function cannot enforce registry minimum_sample: {metric_id}"
        )
    result = function(
        **{name: inputs[name] for name in expected_inputs},
        min_sample=float(minimum_sample),
    )
    if result.metric_id != metric_id:
        raise RuntimeError("metric function returned a mismatched metric identifier")
    return result


def metric_publication_failures(envelope: MetricEnvelope) -> tuple[str, ...]:
    """Return deterministic publication-guard failures. / 返回确定性的发布门控失败项。"""

    if not isinstance(envelope, MetricEnvelope):
        raise TypeError("envelope must be MetricEnvelope")
    failures: list[str] = []
    definition = METRIC_DEFINITIONS.get(envelope.result.metric_id)
    if definition is None:
        return ("metric_not_registered",)
    if envelope.registry_version != METRIC_REGISTRY.get("schema_version"):
        failures.append("registry_version_mismatch")
    if envelope.metric_version != definition.get("version"):
        failures.append("metric_version_mismatch")
    try:
        recomputed = calculate_metric(
            envelope.result.metric_id,
            envelope.calculation_inputs,
        )
    except (KeyError, TypeError, ValueError, RuntimeError) as exc:
        failures.append(f"calculation_inputs_invalid:{type(exc).__name__}")
    else:
        result_fields = {
            "state": (envelope.result.state, recomputed.state),
            "value": (envelope.result.value, recomputed.value),
            "numerator": (envelope.result.numerator, recomputed.numerator),
            "denominator": (envelope.result.denominator, recomputed.denominator),
            "sample_size": (envelope.result.sample_size, recomputed.sample_size),
            "reason": (envelope.result.reason, recomputed.reason),
            "details": (dict(envelope.result.details), dict(recomputed.details)),
        }
        for field_name, (observed, expected) in result_fields.items():
            if observed != expected:
                failures.append(f"calculation_mismatch:{field_name}")

    required_buckets = set(METRIC_REGISTRY["required_bucket_dimensions"])
    missing_buckets = sorted(required_buckets - set(envelope.buckets))
    if missing_buckets:
        failures.append("missing_required_buckets:" + ",".join(missing_buckets))
    declared_exclusions = set(definition.get("exclusions", ()))
    supplied_exclusions = set(envelope.exclusion_counts)
    missing_exclusions = sorted(declared_exclusions - supplied_exclusions)
    unknown_exclusions = sorted(supplied_exclusions - declared_exclusions)
    if missing_exclusions:
        failures.append(
            "missing_declared_exclusions:" + ",".join(missing_exclusions)
        )
    if unknown_exclusions:
        failures.append(
            "unknown_exclusion_counts:" + ",".join(unknown_exclusions)
        )

    end = _parse_rfc3339("window_end", envelope.window_end)
    watermark = _parse_rfc3339("watermark", envelope.watermark)
    finalization_threshold = end + timedelta(
        seconds=float(envelope.allowed_lateness_seconds)
    )
    if watermark < finalization_threshold:
        failures.append("watermark_before_finalization_threshold")
    if not envelope.window_finalized:
        failures.append("window_not_finalized")
    required_probes = set(UNIVERSAL_REQUIRED_PROBES) | set(
        definition.get("required_probes", ())
    )
    missing_probes = sorted(required_probes - set(envelope.observed_probes))
    if missing_probes:
        failures.append("missing_required_probes:" + ",".join(missing_probes))
    if envelope.probe_health != ProbeHealthState.HEALTHY:
        failures.append("probe_health_not_healthy")
    if not envelope.result.is_available:
        failures.append("metric_value_unavailable")
    if envelope.result.is_available and envelope.completeness == 0:
        failures.append("available_value_has_zero_completeness")
    if (
        envelope.result.metric_id in _MANIFEST_REQUIRED_METRICS
        and envelope.expected_manifest_version is None
    ):
        failures.append("expected_manifest_version_required")
    return tuple(failures)


def publish_metric(envelope: MetricEnvelope) -> dict[str, Any]:
    """Guard and serialize a reportable metric. / 门控并序列化可报告指标。"""

    failures = metric_publication_failures(envelope)
    if failures:
        raise MetricPublicationError(
            "metric envelope is not publishable: " + "; ".join(failures)
        )
    return envelope.as_dict()


__all__ = [
    "METRIC_DEFINITIONS",
    "METRIC_REGISTRY",
    "PROBE_DEPENDENCIES",
    "PROBE_DEPENDENCY_MATRIX",
    "PROBE_DEFINITIONS",
    "PROBE_REGISTRY",
    "MetricEnvelope",
    "MetricPublicationError",
    "MetricResult",
    "MetricState",
    "ProbeHealthState",
    "ProbeConditionState",
    "ProbeDependencyResolution",
    "UNIVERSAL_REQUIRED_PROBES",
    "alert_delivery_rate",
    "alias_switch_integrity_rate",
    "bounded_ratio",
    "budget_overrun_rate",
    "budget_pre_reservation_coverage",
    "budget_utilization_max",
    "budget_utilization_vector",
    "candidate_evidence_lineage_integrity_rate",
    "candidate_completion_rate",
    "attribution_overclaim_rate",
    "branch_diversity",
    "branch_record_completeness",
    "calculate_metric",
    "closed_step_record_completeness",
    "checkpoint_validation_binding_rate",
    "contract_completeness",
    "credential_exact_binding_rate",
    "cost_per_validated_success",
    "dispatch_admission_coverage",
    "dispatch_record_completeness",
    "duplicate_event_rate",
    "duplicate_side_effect_rate",
    "eligible_step_closure_rate",
    "evidence_coverage",
    "evidence_resolution_rate",
    "evidence_traceability",
    "event_chain_completeness",
    "event_loss_rate",
    "false_release_rate",
    "frontier_escape_rate",
    "generator_critic_evidenced_finding_rate",
    "generator_critic_opinion_retention_rate",
    "generator_critic_pass_budget_compliance_rate",
    "generator_critic_receipt_coverage_rate",
    "generator_critic_review_version_match_rate",
    "generator_critic_revision_rereview_compliance_rate",
    "generator_critic_risk_evidence_coverage_rate",
    "generator_critic_rubber_stamp_escape_rate",
    "generator_critic_version_escape_rate",
    "hypothesis_elimination_per_cost_unit",
    "hypothesis_elimination_per_iteration",
    "material_candidate_difference",
    "improvement_comparability_coverage",
    "independent_revalidation_coverage",
    "learning_promotion_evidence_completeness",
    "max_budget_utilization",
    "no_progress_loop_rate",
    "outcome_route_accuracy",
    "outcome_linkage_coverage",
    "underroute_rate",
    "overroute_rate",
    "route_abstention_rate",
    "route_oscillation_rate",
    "forced_route_with_missing_signal_rate",
    "parse_failure_rate",
    "path_convergence_rate",
    "plan_compile_success_rate",
    "plan_drift_rate",
    "probe_completion_rate",
    "probe_coverage",
    "publish_metric",
    "reasoning_drift_rate",
    "reflection_admission_compliance",
    "reflection_closure_rate",
    "regression_free_verified_improvement_rate",
    "reverification_prewithdrawal_compliance_rate",
    "readonly_tool_lifecycle_completion_rate",
    "result_unknown_rate",
    "resolve_required_probes",
    "retry_amplification",
    "route_stability_rate",
    "safe_ratio",
    "side_effect_lease_coverage",
    "skill_candidate_recurrence_evidence_rate",
    "skill_package_contract_completeness_rate",
    "skill_package_five_dimension_verification_rate",
    "skill_reuse_success_rate",
    "stale_credential_use_rate",
    "state_evidence_coverage",
    "stop_reason_completeness",
    "tool_success_rate",
    "trial_to_verified_rate",
    "unbounded_ratio",
    "unsupported_conclusion_rate",
    "unavailable_metric",
    "unverified_premise_propagation",
    "validation_coverage",
    "validation_pass_rate",
    "validator_gaming_rate",
    "version_window_integrity_rate",
    "qualified_new_signal_rate",
    "approval_binding_coverage",
    "metric_publication_failures",
]
