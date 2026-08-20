"""Governed reflection reference runtime / 受治理反思参考运行时。

The runtime coordinates public, externally verifiable reflection artifacts. It
does not generate a repair, execute a tool, authorize a side effect, or capture
private chain-of-thought. / 本运行时协调公开、可外部核验的反思制品；它不生成
修复、不执行工具、不授权副作用，也不采集私密思维过程。
"""

from __future__ import annotations

from copy import deepcopy
from enum import Enum
import math
from typing import Any, Mapping, Sequence

try:  # Package import / 包导入
    from .reasoning_artifacts import (
        artifact_fingerprint,
        build_artifact,
        validate_artifact_hash,
        validate_schema,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import (
        artifact_fingerprint,
        build_artifact,
        validate_artifact_hash,
        validate_schema,
    )

try:  # Package import / 包导入
    from .generator_critic import GENERATOR_CRITIC_PROBES
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from generator_critic import GENERATOR_CRITIC_PROBES

try:  # Package import / 包导入
    from .skill_package import SKILL_PACKAGE_PROBES
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from skill_package import SKILL_PACKAGE_PROBES


REFLECTION_CORE_PROBES = tuple(f"PROBE_{number:04d}" for number in range(16, 22))
REFLECTION_ATTRIBUTION_PROBE = "PROBE_0022"
REFLECTION_LEARNING_PROBE = "PROBE_0023"


class ReflectionRuntimeError(RuntimeError):
    """Base reflection coordination error / 反思协调错误基类。"""


class ReflectionValidationError(ReflectionRuntimeError):
    """Reflection artifact semantics failed / 反思制品语义校验失败。"""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


class ReflectionStateError(ReflectionRuntimeError):
    """An operation is illegal in the current state / 操作在当前状态非法。"""


class ReflectionAuthorizationError(ReflectionRuntimeError):
    """A proposed change lacks its exact authorization / 改变提案缺少精确授权。"""


class ReflectionEligibility(str, Enum):
    """Admission outcome / 准入结果。"""

    ADMITTED = "admitted"
    NEEDS_EVIDENCE = "needs_evidence"
    NOT_APPLICABLE = "not_applicable"
    BLOCKED = "blocked"
    HUMAN_REQUIRED = "human_required"


class ReflectionRoute(str, Enum):
    """Governed treatment selected after admission / 准入后选择的受治理处理路径。"""

    GENERATOR_CRITIC = "generator_critic"
    SELF_HEAL = "self_heal"
    EVIDENCE_COLLECTION = "evidence_collection"
    EXPERIENCE_REPLAY = "experience_replay"
    SKILL_LIFECYCLE = "skill_lifecycle"
    HUMAN_TRIAGE = "human_triage"
    RELEASE = "release"


class ReflectionState(str, Enum):
    """Authoritative reflection state / 权威反思状态。"""

    CANDIDATE = "candidate"
    ADMITTED = "admitted"
    NEEDS_EVIDENCE = "needs_evidence"
    NOT_APPLICABLE = "not_applicable"
    BLOCKED = "blocked"
    HUMAN_REQUIRED = "human_required"
    BASELINE_FROZEN = "baseline_frozen"
    ROUND_ACTIVE = "round_active"
    CHANGE_PROPOSED = "change_proposed"
    CHANGE_AUTHORIZED = "change_authorized"
    CHANGE_APPLIED = "change_applied"
    REVALIDATING = "revalidating"
    ROLLING_BACK = "rolling_back"
    ROLLBACK_APPLIED = "rollback_applied"
    ROLLBACK_VERIFIED = "rollback_verified"
    ROUND_CLOSED = "round_closed"
    ACCEPTED = "accepted"
    ROLLED_BACK = "rolled_back"
    HANDED_OFF = "handed_off"
    REJECTED = "rejected"
    ABORTED = "aborted"


class ReflectionOutcome(str, Enum):
    """Round outcome / 轮次结果。"""

    CONTINUE = "continue"
    ACCEPTED = "accepted"
    ROLLED_BACK = "rolled_back"
    HANDED_OFF = "handed_off"
    REJECTED = "rejected"
    ABORTED = "aborted"


class ReflectionImprovementState(str, Enum):
    """Observed improvement classification / 观测改善分类。"""

    NOT_EVALUATED = "not_evaluated"
    NO_IMPROVEMENT = "no_improvement"
    OBSERVED_UNATTRIBUTED = "observed_unattributed"
    VERIFIED_IMPROVEMENT = "verified_improvement"
    REGRESSION = "regression"


_NONADMITTED_STATE = {
    ReflectionEligibility.NEEDS_EVIDENCE: ReflectionState.NEEDS_EVIDENCE,
    ReflectionEligibility.NOT_APPLICABLE: ReflectionState.NOT_APPLICABLE,
    ReflectionEligibility.BLOCKED: ReflectionState.BLOCKED,
    ReflectionEligibility.HUMAN_REQUIRED: ReflectionState.HUMAN_REQUIRED,
}

_OUTCOME_STATE = {
    ReflectionOutcome.CONTINUE: ReflectionState.ROUND_CLOSED,
    ReflectionOutcome.ACCEPTED: ReflectionState.ACCEPTED,
    ReflectionOutcome.ROLLED_BACK: ReflectionState.ROLLED_BACK,
    ReflectionOutcome.HANDED_OFF: ReflectionState.HANDED_OFF,
    ReflectionOutcome.REJECTED: ReflectionState.REJECTED,
    ReflectionOutcome.ABORTED: ReflectionState.ABORTED,
}

_TERMINAL_STATES = frozenset(
    {
        ReflectionState.ACCEPTED,
        ReflectionState.ROLLED_BACK,
        ReflectionState.HANDED_OFF,
        ReflectionState.REJECTED,
        ReflectionState.ABORTED,
    }
)

_INDEPENDENCE_RANK = {
    "same_source": 0,
    "cross_source": 1,
    "external_validator": 2,
    "human_review": 2,
    "controlled_replay": 3,
}

_REQUIRED_INDEPENDENCE_RANK = {
    "cross_source": 1,
    "external_validator": 2,
    "human_review": 2,
    "controlled_replay": 3,
}

_ATTRIBUTION_RANK = {
    "unattributed": 0,
    "hypothesis": 1,
    "correlational": 2,
    "controlled_replay": 3,
    "intervention_verified": 4,
}

_ATTRIBUTION_EVIDENCE_KIND = {
    "unattributed": "none",
    "hypothesis": "observational",
    "correlational": "correlational",
    "controlled_replay": "controlled_replay",
    "intervention_verified": "intervention",
}

_ATTRIBUTION_AUTHORITY_FIELD = {
    "hypothesis": "observational_authority_bindings",
    "correlational": "correlational_authority_bindings",
    "controlled_replay": "controlled_replay_authority_bindings",
    "intervention_verified": "intervention_authority_bindings",
}

_NEW_SIGNAL_FIELDS = {
    "qualified",
    "independence",
    "information_gain",
    "evidence_bindings",
}

_VALIDATION_FIELDS = {
    "status",
    "candidate_binding",
    "criteria_binding",
    "environment_binding",
    "mandatory_pass",
    "regression_pass",
    "metric_id",
    "baseline_value",
    "result_value",
    "improvement_delta",
    "threshold_met",
    "independent_signal_count",
    "independent_signal_bindings",
    "comparison_state",
    "rebased_baseline",
    "validator_gaming",
    "result_progress",
    "information_progress",
    "validator_bindings",
    "evidence_bindings",
}


def _initial_attribution() -> dict[str, Any]:
    return {
        "state": "unattributed",
        "hypothesis": None,
        "falsifier": None,
        "confounders": [],
        "evidence_kind": "none",
        "evidence_authority_binding": None,
        "evidence_bindings": [],
    }


def _binding_key(binding: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return binding.get("id"), binding.get("version"), binding.get("hash")


def _binding_set(bindings: Sequence[Mapping[str, Any]]) -> set[tuple[Any, Any, Any]]:
    return {_binding_key(binding) for binding in bindings}


def _contract_binding(contract: Mapping[str, Any]) -> dict[str, str]:
    return {
        "id": str(contract["contract_id"]),
        "version": str(contract["contract_version"]),
        "hash": str(contract["contract_hash"]),
    }


def _baseline_binding(contract: Mapping[str, Any]) -> dict[str, str]:
    baseline = contract["baseline"]
    return {
        "id": f"{contract['contract_id']}:baseline",
        "version": str(contract["contract_version"]),
        "hash": artifact_fingerprint(baseline),
    }


def _event_binding(event: Mapping[str, Any]) -> dict[str, str]:
    return {
        "id": str(event["event_id"]),
        "version": "1.0.0",
        "hash": str(event["event_hash"]),
    }


def _validate_new_signal_record(
    signal: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    consumed_bindings: set[tuple[Any, Any, Any]] | None = None,
) -> dict[str, Any]:
    """Normalize and validate a public signal record / 规范化并校验公开信号记录。"""

    if set(signal) != _NEW_SIGNAL_FIELDS:
        raise ValueError(f"new_signal fields must equal {sorted(_NEW_SIGNAL_FIELDS)}")
    normalized = deepcopy(dict(signal))
    if not isinstance(normalized["qualified"], bool):
        raise TypeError("new_signal.qualified must be boolean")
    if normalized["independence"] not in _INDEPENDENCE_RANK:
        raise ValueError("new_signal.independence is invalid")
    if normalized["information_gain"] not in {
        "none",
        "confirmed_deviation",
        "eliminated_hypothesis",
        "reduced_unknown",
        "changed_route",
    }:
        raise ValueError("new_signal.information_gain is invalid")
    if not isinstance(normalized["evidence_bindings"], list):
        raise TypeError("new_signal.evidence_bindings must be a list")
    evidence_set = _binding_set(normalized["evidence_bindings"])
    if len(evidence_set) != len(normalized["evidence_bindings"]):
        raise ReflectionValidationError(
            ["new signal evidence bindings must be unique / 新信号证据绑定必须唯一"]
        )
    required_rank = _REQUIRED_INDEPENDENCE_RANK[
        contract["signal_policy"]["independence_requirement"]
    ]
    if normalized["qualified"]:
        if (
            not evidence_set
            or normalized["information_gain"] == "none"
            or _INDEPENDENCE_RANK[normalized["independence"]] < required_rank
        ):
            raise ReflectionValidationError(
                [
                    "qualified signal lacks information gain, evidence, or required independence / "
                    "有效新信号缺少信息增量、证据或所需独立性"
                ]
            )
        if consumed_bindings and evidence_set & consumed_bindings:
            raise ReflectionValidationError(
                ["new signal evidence was already consumed / 新信号证据已被先前轮次消费"]
            )
    elif (
        evidence_set
        or normalized["information_gain"] != "none"
        or normalized["independence"] != "same_source"
    ):
        raise ReflectionValidationError(
            ["unqualified signal must not claim evidence or information gain / 未获确认的信号不得声明证据或信息增量"]
        )
    return normalized


def _contract_bound_validation_errors(
    validation: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    new_signal: Mapping[str, Any],
    subject_before_binding: Mapping[str, Any],
    candidate_binding: Mapping[str, Any] | None,
    started_validator_bindings: Sequence[Mapping[str, Any]] | None = None,
    validator_changed: bool = False,
) -> list[str]:
    """Recompute public validation claims before commit / 在提交前重算公开复验声明。"""

    errors: list[str] = []
    if set(validation) != _VALIDATION_FIELDS:
        return [
            "validation field set is incomplete or extended / 复验字段集缺失或被扩展"
        ]
    normalized = deepcopy(dict(validation))
    status = normalized.get("status")
    if status not in {"not_run", "passed", "failed", "unknown"}:
        return ["validation status is invalid / 复验状态无效"]

    def binding_set(field: str) -> set[tuple[Any, Any, Any]]:
        value = normalized.get(field)
        if not isinstance(value, list) or not all(
            isinstance(binding, Mapping) for binding in value
        ):
            errors.append(f"validation {field} is not a binding list / 复验 {field} 不是绑定列表")
            return set()
        result = _binding_set(value)
        if len(result) != len(value):
            errors.append(f"validation {field} contains duplicates / 复验 {field} 包含重复绑定")
        return result

    validator_set = binding_set("validator_bindings")
    evidence_set = binding_set("evidence_bindings")
    independent_set = binding_set("independent_signal_bindings")
    try:
        signal = _validate_new_signal_record(new_signal, contract)
        signal_set = _binding_set(signal["evidence_bindings"])
        derived_information_progress = bool(
            signal["qualified"]
            and signal["information_gain"] != "none"
            and signal_set
        )
    except (TypeError, ValueError, ReflectionValidationError) as exc:
        errors.append(f"validation signal context is invalid: {exc} / 复验信号上下文无效")
        signal_set = set()
        derived_information_progress = False

    count = normalized.get("independent_signal_count")
    if isinstance(count, bool) or not isinstance(count, int) or count != len(
        independent_set
    ):
        errors.append("independent signal count cannot be reproduced / 独立信号数无法重算")
    if independent_set != signal_set:
        errors.append("independent signals differ from qualified signal evidence / 独立信号与有效信号证据不同")
    if normalized.get("information_progress") is not derived_information_progress:
        errors.append("information progress cannot be reproduced / 信息进展无法重算")

    definitive_fields = (
        "mandatory_pass",
        "regression_pass",
        "metric_id",
        "baseline_value",
        "result_value",
        "improvement_delta",
        "threshold_met",
    )
    if status == "not_run":
        if any(
            normalized.get(field) is not None
            for field in definitive_fields
            + ("candidate_binding", "criteria_binding", "environment_binding")
        ):
            errors.append("not-run validation contains verdicts or measurements / 未运行复验包含裁定或测量")
        if (
            normalized.get("comparison_state") != "not_evaluated"
            or validator_set
            or evidence_set
            or normalized.get("rebased_baseline") is not None
            or normalized.get("result_progress") is not False
        ):
            errors.append("not-run validation claims execution or result progress / 未运行复验声明已执行或结果进展")
        return errors

    if candidate_binding is not None and (
        not isinstance(normalized.get("candidate_binding"), Mapping)
        or _binding_key(normalized["candidate_binding"]) != _binding_key(candidate_binding)
    ):
        errors.append("validation candidate differs from the applied subject / 复验候选与已应用对象不同")
    if started_validator_bindings is not None and not _binding_set(
        started_validator_bindings
    ).issubset(validator_set):
        errors.append("validation omits validators recorded at start / 复验遗漏开始时记录的验证器")

    if status == "unknown":
        if any(normalized.get(field) is not None for field in definitive_fields):
            errors.append("unknown validation contains definitive verdicts or measurements / 结果未知的复验包含确定裁定或测量")
        if normalized.get("result_progress") is not False:
            errors.append("unknown validation cannot claim result progress / 结果未知的复验不得声明结果进展")
        return errors

    required_completed = (
        "candidate_binding",
        "criteria_binding",
        "mandatory_pass",
        "regression_pass",
        "metric_id",
        "baseline_value",
        "result_value",
        "improvement_delta",
        "threshold_met",
    )
    if any(normalized.get(field) is None for field in required_completed):
        errors.append("completed validation lacks measurement fields / 已完成复验缺少测量字段")
        return errors
    if not evidence_set:
        errors.append("completed validation lacks evidence / 已完成复验缺少证据")
    if status == "passed" and normalized.get("mandatory_pass") is not True:
        errors.append("passed validation requires mandatory checks / 复验通过要求必选检查通过")

    policy = contract["validation_policy"]
    required_validators = _binding_set(policy["mandatory_validator_bindings"]) | _binding_set(
        policy["regression_validator_bindings"]
    )
    if not required_validators.issubset(validator_set):
        errors.append("validation omits contract validators / 复验遗漏契约验证器")

    comparison_state = normalized.get("comparison_state")
    rebased = normalized.get("rebased_baseline")
    metric_baseline: Any = contract["baseline"]["metric_value"]
    if comparison_state == "comparable":
        if _binding_key(normalized.get("criteria_binding") or {}) != _binding_key(
            contract["baseline"]["criteria_binding"]
        ):
            errors.append("comparable validation changed criteria / 可比复验改变了判定标准")
        if _binding_key(normalized.get("environment_binding") or {}) != _binding_key(
            contract["baseline"]["environment_binding"] or {}
        ):
            errors.append("comparable validation changed environment / 可比复验改变了环境")
        if not _binding_set(contract["baseline"]["validator_bindings"]).issubset(
            validator_set
        ):
            errors.append("comparable validation omitted frozen validators / 可比复验遗漏冻结验证器")
        if rebased is not None:
            errors.append("comparable validation cannot carry a rebased baseline / 可比复验不得携带重建基线")
    elif comparison_state == "independently_rebased":
        if not validator_changed or not isinstance(rebased, Mapping):
            errors.append("independent rebase requires an approved validator change and baseline / 独立重建要求已批准验证器改变及基线")
        else:
            required_rebase_fields = {
                "baseline_binding",
                "subject_before_binding",
                "criteria_binding",
                "environment_binding",
                "validator_bindings",
                "regression_scope_bindings",
                "metric_id",
                "metric_value",
                "approval_binding",
                "evidence_bindings",
            }
            if set(rebased) != required_rebase_fields:
                errors.append("rebased baseline field set is invalid / 重建基线字段集无效")
            else:
                rebase_content = {
                    key: deepcopy(rebased[key])
                    for key in required_rebase_fields
                    if key != "baseline_binding"
                }
                if rebased["baseline_binding"].get("hash") != artifact_fingerprint(
                    rebase_content
                ):
                    errors.append("rebased baseline hash cannot be reproduced / 重建基线哈希无法重算")
                if _binding_key(rebased["subject_before_binding"]) != _binding_key(
                    subject_before_binding
                ):
                    errors.append("rebased baseline uses a different before-subject / 重建基线使用了不同改变前对象")
                if _binding_key(normalized["criteria_binding"]) != _binding_key(
                    rebased["criteria_binding"]
                ) or _binding_key(normalized.get("environment_binding") or {}) != _binding_key(
                    rebased["environment_binding"] or {}
                ):
                    errors.append("validation differs from rebased criteria or environment / 复验偏离重建标准或环境")
                if validator_set != _binding_set(rebased["validator_bindings"]):
                    errors.append("validation validators differ from rebased baseline / 复验验证器与重建基线不同")
                expected_authorizer = policy["validator_change_authorizer_binding"]
                if expected_authorizer is None or _binding_key(
                    rebased["approval_binding"]
                ) != _binding_key(expected_authorizer):
                    errors.append("rebased baseline lacks contract approval / 重建基线缺少契约审批")
                metric_baseline = rebased["metric_value"]
    elif rebased is not None:
        errors.append("rebased baseline is illegal for this comparison / 当前比较状态不得携带重建基线")

    if normalized.get("metric_id") != policy["improvement_metric_id"]:
        errors.append("validation metric differs from contract / 复验指标偏离契约")
    try:
        baseline_value = float(normalized["baseline_value"])
        result_value = float(normalized["result_value"])
        supplied_delta = float(normalized["improvement_delta"])
        frozen_value = float(metric_baseline)
        if not all(
            math.isfinite(value)
            for value in (baseline_value, result_value, supplied_delta, frozen_value)
        ):
            raise ValueError("non-finite measurement")
        if not math.isclose(baseline_value, frozen_value, rel_tol=1e-12, abs_tol=1e-12):
            errors.append("validation changed the governed metric baseline / 复验改变了受治理指标基线")
        expected_delta = (
            result_value - baseline_value
            if policy["improvement_direction"] == "higher_is_better"
            else baseline_value - result_value
        )
        if not math.isclose(supplied_delta, expected_delta, rel_tol=1e-12, abs_tol=1e-12):
            errors.append("improvement delta cannot be reproduced / 改善增量无法重算")
        expected_threshold = expected_delta >= float(policy["improvement_threshold"])
        if normalized.get("threshold_met") is not expected_threshold:
            errors.append("threshold verdict cannot be reproduced / 阈值裁定无法重算")
        if normalized.get("result_progress") is not (expected_delta > 0):
            errors.append("result progress cannot be reproduced / 结果进展无法重算")
    except (TypeError, ValueError, OverflowError):
        errors.append("validation measurements are invalid or non-finite / 复验测量无效或非有限数")
    return errors


def _validate_learning_candidate(
    candidate: Mapping[str, Any] | None,
    contract: Mapping[str, Any],
    *,
    outcome: ReflectionOutcome,
    round_id: str | None = None,
    source_subject_binding: Mapping[str, Any] | None = None,
    available_round_evidence: set[tuple[Any, Any, Any]] | None = None,
) -> dict[str, Any] | None:
    """Validate learning as a separately authorized lifecycle / 将学习校验为独立授权生命周期。"""

    policy = contract["learning_policy"]
    if candidate is None:
        if policy["promotion_enabled"] and outcome is ReflectionOutcome.ACCEPTED:
            raise ReflectionValidationError(
                ["an accepted learning-enabled round requires a learning decision / 启用学习治理的接受轮必须记录学习决定"]
            )
        return None
    normalized = deepcopy(dict(candidate))
    required = {
        "target",
        "candidate_binding",
        "source_round_id",
        "source_subject_binding",
        "round_evidence_bindings",
        "decision",
        "promotion_evidence_bindings",
        "authorization_binding",
        "owner_binding",
    }
    if set(normalized) != required:
        raise ValueError(f"learning_candidate fields must equal {sorted(required)}")
    if outcome is not ReflectionOutcome.ACCEPTED:
        raise ReflectionValidationError(
            ["learning evaluation is only legal after acceptance / 学习评估只能发生在接受之后"]
        )
    if not policy["promotion_enabled"]:
        raise ReflectionAuthorizationError("learning promotion is disabled by contract")
    if normalized["target"] not in policy["allowed_targets"]:
        raise ReflectionAuthorizationError("learning target is outside the contract")
    if _binding_key(normalized["owner_binding"]) != _binding_key(policy["owner_binding"]):
        raise ReflectionAuthorizationError("learning owner binding mismatch")
    if round_id is not None and normalized["source_round_id"] != round_id:
        raise ReflectionValidationError(
            ["learning candidate binds a different source round / 学习候选绑定了不同来源轮次"]
        )
    if source_subject_binding is not None and _binding_key(
        normalized["source_subject_binding"]
    ) != _binding_key(source_subject_binding):
        raise ReflectionValidationError(
            ["learning candidate binds a different source subject / 学习候选绑定了不同来源对象"]
        )
    round_evidence = normalized["round_evidence_bindings"]
    round_evidence_set = _binding_set(round_evidence)
    if len(round_evidence_set) != len(round_evidence):
        raise ReflectionValidationError(
            ["learning round evidence must be unique / 学习本轮证据必须唯一"]
        )
    if available_round_evidence is not None and (
        not round_evidence_set
        or not round_evidence_set.issubset(available_round_evidence)
    ):
        raise ReflectionValidationError(
            ["learning candidate is not linked to this round's evidence / 学习候选未关联本轮证据"]
        )
    evidence = normalized["promotion_evidence_bindings"]
    if len(_binding_set(evidence)) != len(evidence):
        raise ReflectionValidationError(
            ["learning promotion evidence must be unique / 学习晋升证据必须唯一"]
        )
    if normalized["decision"] == "promoted":
        if len(evidence) < policy["minimum_evidence_bindings"]:
            raise ReflectionValidationError(
                ["learning promotion lacks required evidence / 学习晋升缺少必需证据"]
            )
        if _binding_key(normalized["authorization_binding"] or {}) != _binding_key(
            policy["promotion_authorizer_binding"] or {}
        ):
            raise ReflectionAuthorizationError("learning promotion authorization mismatch")
    elif normalized["authorization_binding"] is not None:
        raise ReflectionAuthorizationError(
            "a non-promoted learning decision cannot carry promotion authority"
        )
    return normalized


def resolve_reflection_required_probes(
    *,
    attribution_claimed: bool = False,
    learning_promotion: bool = False,
    generator_critic: bool = False,
    skill_package: bool = False,
) -> tuple[str, ...]:
    """Resolve the reflection-specific probe profile / 解析反思专用探针档案。"""

    if not all(
        isinstance(value, bool)
        for value in (
            attribution_claimed,
            learning_promotion,
            generator_critic,
            skill_package,
        )
    ):
        raise TypeError("reflection probe conditions must be boolean")
    probes = set(REFLECTION_CORE_PROBES)
    if attribution_claimed:
        probes.add(REFLECTION_ATTRIBUTION_PROBE)
    if learning_promotion:
        probes.add(REFLECTION_LEARNING_PROBE)
    if generator_critic:
        probes.update(GENERATOR_CRITIC_PROBES)
    if skill_package:
        probes.add(REFLECTION_LEARNING_PROBE)
        probes.update(SKILL_PACKAGE_PROBES)
    return tuple(sorted(probes))


def build_reflection_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Seal and semantically validate a reflection contract / 封存并语义校验反思契约。"""

    sealed = build_artifact("reflection_contract", contract)
    validate_reflection_contract(sealed)
    return sealed


def validate_reflection_contract(contract: Mapping[str, Any]) -> None:
    """Validate reflection admission and governance invariants / 校验反思准入与治理不变量。"""

    validate_schema("reflection_contract", contract)
    validate_artifact_hash("reflection_contract", contract)
    errors: list[str] = []

    admission = contract["admission"]
    eligibility = ReflectionEligibility(admission["eligibility"])
    route = ReflectionRoute(admission["route"])
    expected_routes = {
        ReflectionEligibility.NEEDS_EVIDENCE: {ReflectionRoute.EVIDENCE_COLLECTION},
        ReflectionEligibility.NOT_APPLICABLE: {ReflectionRoute.RELEASE},
        ReflectionEligibility.BLOCKED: {ReflectionRoute.HUMAN_TRIAGE},
        ReflectionEligibility.HUMAN_REQUIRED: {ReflectionRoute.HUMAN_TRIAGE},
        ReflectionEligibility.ADMITTED: {
            ReflectionRoute.GENERATOR_CRITIC,
            ReflectionRoute.SELF_HEAL,
            ReflectionRoute.EXPERIENCE_REPLAY,
            ReflectionRoute.SKILL_LIFECYCLE,
        },
    }
    if route not in expected_routes[eligibility]:
        errors.append(
            f"route {route.value} is inconsistent with eligibility {eligibility.value} / "
            "反思路由与准入状态不一致"
        )

    trigger = contract["trigger"]
    if not trigger["evidence_bindings"] and trigger["evidence_plan_binding"] is None:
        errors.append(
            "trigger requires evidence or an authorized evidence plan / "
            "触发必须具备证据或已授权取证计划"
        )

    if _binding_key(contract["subject_binding"]) != _binding_key(
        contract["baseline"]["subject_before_binding"]
    ):
        errors.append("subject and frozen baseline bindings differ / 被审对象与冻结基线绑定不一致")

    if contract["baseline"]["metric_id"] != contract["validation_policy"][
        "improvement_metric_id"
    ]:
        errors.append("baseline metric differs from validation policy / 基线指标与复验策略不一致")
    if not math.isfinite(float(contract["baseline"]["metric_value"])):
        errors.append("baseline metric value must be finite / 基线指标值必须为有限数")
    if not math.isfinite(
        float(contract["validation_policy"]["improvement_threshold"])
    ):
        errors.append("improvement threshold must be finite / 改善阈值必须为有限数")

    baseline_validators = _binding_set(contract["baseline"]["validator_bindings"])
    mandatory_validators = _binding_set(
        contract["validation_policy"]["mandatory_validator_bindings"]
    )
    if not mandatory_validators.issubset(baseline_validators):
        errors.append(
            "mandatory validators are absent from the frozen baseline / "
            "必选验证器未全部纳入冻结基线"
        )

    allowed = set(contract["change_policy"]["allowed_targets"])
    forbidden = set(contract["change_policy"]["forbidden_targets"])
    overlap = sorted(allowed & forbidden)
    if overlap:
        errors.append(f"change targets are both allowed and forbidden: {overlap} / 改变范围冲突")

    change_policy = contract["change_policy"]
    validator_authorizer = contract["validation_policy"][
        "validator_change_authorizer_binding"
    ]
    if change_policy["verifier_change_policy"] == "forbidden" and "validator" in allowed:
        errors.append("validator cannot be allowed when verifier changes are forbidden / 禁止修改验证器时不得将其列为允许对象")
    if (
        change_policy["verifier_change_policy"] == "independent_approval_required"
        and "validator" in allowed
        and validator_authorizer is None
    ):
        errors.append("validator changes require a bound independent authorizer / 验证器改变缺少独立授权器绑定")
    if (
        validator_authorizer is not None
        and _binding_key(validator_authorizer)
        == _binding_key(change_policy["authorizer_binding"])
    ):
        errors.append("validator and general change authorizers must be distinct / 验证器与一般改变授权器必须不同")

    learning_policy = contract["learning_policy"]
    if learning_policy["promotion_enabled"]:
        if (
            not learning_policy["allowed_targets"]
            or learning_policy["promotion_authorizer_binding"] is None
            or learning_policy["owner_binding"] is None
        ):
            errors.append("enabled learning promotion requires targets, authorizer, and owner / 已启用学习晋升必须配置目标、授权器与责任人")
    elif (
        learning_policy["allowed_targets"]
        or learning_policy["promotion_authorizer_binding"] is not None
        or learning_policy["owner_binding"] is not None
    ):
        errors.append("disabled learning promotion must not retain active authority / 未启用学习晋升不得保留活动权限")
    if route is ReflectionRoute.SKILL_LIFECYCLE and not learning_policy[
        "promotion_enabled"
    ]:
        errors.append("skill-lifecycle route requires enabled learning promotion / Skill 生命周期路由必须启用学习晋升")

    attribution_policy = contract["attribution_policy"]
    if not attribution_policy["observational_authority_bindings"]:
        errors.append("attribution policy requires observational authority / 归因策略必须配置观察证据权威")
    for field in (
        "correlational_authority_bindings",
        "controlled_replay_authority_bindings",
        "intervention_authority_bindings",
    ):
        if len(_binding_set(attribution_policy[field])) != len(
            attribution_policy[field]
        ):
            errors.append(f"attribution authority bindings are duplicated in {field} / 归因权威绑定重复")

    if (
        contract["signal_policy"]["max_information_only_rounds"]
        > contract["stop_policy"]["max_rounds"]
    ):
        errors.append("information-only budget exceeds total round budget / 仅信息进展预算超过总轮次预算")

    if errors:
        raise ReflectionValidationError(errors)


def validate_reflection_event(event: Mapping[str, Any]) -> None:
    """Validate one sealed reflection event / 校验一个已封存反思事件。"""

    validate_schema("reflection_event", event)
    validate_artifact_hash("reflection_event", event)
    event_type = event["event_type"]
    before = ReflectionState(event["state_before"])
    after = ReflectionState(event["state_after"])
    round_id = event["round_id"]
    payload = event["payload"]
    if not isinstance(payload, Mapping):
        raise ReflectionValidationError(["reflection event payload must be an object / 反思事件载荷必须是对象"])

    rules: dict[str, tuple[set[ReflectionState], set[ReflectionState], set[str], bool]] = {
        "reflection_started": (
            {ReflectionState.CANDIDATE},
            {ReflectionState.CANDIDATE},
            {"trigger_type"},
            False,
        ),
        "reflection_eligibility_evaluated": (
            {ReflectionState.CANDIDATE},
            {
                ReflectionState.ADMITTED,
                ReflectionState.NEEDS_EVIDENCE,
                ReflectionState.NOT_APPLICABLE,
                ReflectionState.BLOCKED,
                ReflectionState.HUMAN_REQUIRED,
            },
            {"eligibility", "reason_codes"},
            False,
        ),
        "reflection_routed": (
            {
                ReflectionState.ADMITTED,
                ReflectionState.NEEDS_EVIDENCE,
                ReflectionState.NOT_APPLICABLE,
                ReflectionState.BLOCKED,
                ReflectionState.HUMAN_REQUIRED,
            },
            {
                ReflectionState.ADMITTED,
                ReflectionState.NEEDS_EVIDENCE,
                ReflectionState.NOT_APPLICABLE,
                ReflectionState.BLOCKED,
                ReflectionState.HUMAN_REQUIRED,
            },
            {"route"},
            False,
        ),
        "reflection_baseline_frozen": (
            {ReflectionState.ADMITTED},
            {ReflectionState.BASELINE_FROZEN},
            {"baseline_binding"},
            False,
        ),
        "reflection_round_started": (
            {ReflectionState.BASELINE_FROZEN, ReflectionState.ROUND_CLOSED},
            {ReflectionState.ROUND_ACTIVE},
            {"round_number", "new_signal", "baseline_binding", "attribution_before"},
            True,
        ),
        "reflection_signal_recorded": (
            {ReflectionState.ROUND_ACTIVE},
            {ReflectionState.ROUND_ACTIVE},
            {"new_signal"},
            True,
        ),
        "deviation_detected": (
            {ReflectionState.ROUND_ACTIVE},
            {ReflectionState.ROUND_ACTIVE},
            {"code", "evidence_bindings", "details"},
            True,
        ),
        "attribution_evidence_recorded": (
            {ReflectionState.ROUND_ACTIVE, ReflectionState.REVALIDATING},
            {ReflectionState.ROUND_ACTIVE, ReflectionState.REVALIDATING},
            {
                "state",
                "hypothesis",
                "falsifier",
                "confounders",
                "evidence_kind",
                "evidence_authority_binding",
                "evidence_bindings",
                "new_evidence_bindings",
            },
            True,
        ),
        "change_proposed": (
            {ReflectionState.ROUND_ACTIVE},
            {ReflectionState.CHANGE_PROPOSED},
            {"target", "proposal_binding"},
            True,
        ),
        "change_authorized": (
            {ReflectionState.CHANGE_PROPOSED},
            {ReflectionState.CHANGE_AUTHORIZED},
            {"authorization_binding", "validator_change_approval_binding"},
            True,
        ),
        "change_rejected": (
            {ReflectionState.CHANGE_PROPOSED},
            {ReflectionState.ROUND_ACTIVE},
            {"reason"},
            True,
        ),
        "change_applied": (
            {ReflectionState.CHANGE_AUTHORIZED},
            {ReflectionState.CHANGE_APPLIED},
            {"subject_after_binding"},
            True,
        ),
        "revalidation_started": (
            {ReflectionState.CHANGE_APPLIED},
            {ReflectionState.REVALIDATING},
            {"candidate_binding", "validator_bindings"},
            True,
        ),
        "revalidation_finished": (
            {ReflectionState.REVALIDATING},
            {ReflectionState.REVALIDATING},
            _VALIDATION_FIELDS,
            True,
        ),
        "rollback_started": (
            {
                ReflectionState.CHANGE_APPLIED,
                ReflectionState.REVALIDATING,
            },
            {ReflectionState.ROLLING_BACK},
            {"rollback_binding", "failed_subject_binding", "restored_subject_binding"},
            True,
        ),
        "rollback_applied": (
            {ReflectionState.ROLLING_BACK},
            {ReflectionState.ROLLBACK_APPLIED},
            {"restored_subject_binding", "apply_evidence_bindings"},
            True,
        ),
        "rollback_verified": (
            {ReflectionState.ROLLBACK_APPLIED},
            {ReflectionState.ROLLBACK_VERIFIED},
            {
                "restored_subject_binding",
                "validator_bindings",
                "verification_evidence_bindings",
                "verified",
            },
            True,
        ),
        "reflection_round_finished": (
            {
                ReflectionState.ROUND_ACTIVE,
                ReflectionState.REVALIDATING,
                ReflectionState.ROLLBACK_VERIFIED,
            },
            {
                ReflectionState.ROUND_CLOSED,
                ReflectionState.ACCEPTED,
                ReflectionState.ROLLED_BACK,
                ReflectionState.HANDED_OFF,
                ReflectionState.REJECTED,
                ReflectionState.ABORTED,
            },
            {"outcome", "improvement_state", "learning_candidate"},
            True,
        ),
        "learning_promotion_evaluated": (
            {ReflectionState.ACCEPTED},
            {ReflectionState.ACCEPTED},
            {"learning_candidate"},
            True,
        ),
        "reflection_stopped": (
            {
                ReflectionState.NEEDS_EVIDENCE,
                ReflectionState.NOT_APPLICABLE,
                ReflectionState.BLOCKED,
                ReflectionState.HUMAN_REQUIRED,
                ReflectionState.ACCEPTED,
                ReflectionState.ROLLED_BACK,
                ReflectionState.HANDED_OFF,
                ReflectionState.REJECTED,
                ReflectionState.ABORTED,
            },
            set(_TERMINAL_STATES),
            {"outcome", "stop_reason"},
            round_id is not None,
        ),
    }
    allowed_before, allowed_after, required_payload, requires_round = rules[event_type]
    errors: list[str] = []
    if before not in allowed_before or after not in allowed_after:
        errors.append(f"illegal {event_type} transition {before.value}->{after.value} / 非法反思事件状态转换")
    if requires_round != (round_id is not None):
        errors.append(f"{event_type} has invalid round binding / 反思事件轮次绑定无效")
    missing = sorted(required_payload - set(payload))
    if missing:
        errors.append(f"{event_type} payload missing {missing} / 反思事件载荷缺少字段")
    if event_type == "reflection_routed" and before is not after:
        errors.append("routing event must preserve the eligibility state / 路由事件必须保持准入状态")
    if event_type == "reflection_routed" and payload.get("route") != event["route"]:
        errors.append("routing payload differs from the event route / 路由载荷与事件路由不一致")
    if event_type == "reflection_eligibility_evaluated":
        try:
            expected = (
                ReflectionState.ADMITTED
                if ReflectionEligibility(payload["eligibility"])
                is ReflectionEligibility.ADMITTED
                else _NONADMITTED_STATE[ReflectionEligibility(payload["eligibility"])]
            )
            if after is not expected:
                errors.append("eligibility payload and target state differ / 准入载荷与目标状态不一致")
        except (KeyError, TypeError, ValueError):
            errors.append("eligibility payload is invalid / 准入载荷无效")
    if event_type == "reflection_round_finished":
        try:
            expected = _OUTCOME_STATE[ReflectionOutcome(payload["outcome"])]
            if after is not expected:
                errors.append("round outcome and target state differ / 轮次结果与目标状态不一致")
        except (KeyError, TypeError, ValueError):
            errors.append("round outcome is invalid / 轮次结果无效")
    if event_type == "reflection_round_started":
        if not isinstance(payload.get("round_number"), int) or isinstance(
            payload.get("round_number"), bool
        ) or payload.get("round_number", 0) < 1:
            errors.append("round-start number is invalid / 轮次开始序号无效")
    if event_type == "reflection_signal_recorded" and not isinstance(
        payload.get("new_signal"), Mapping
    ):
        errors.append("signal event requires a signal object / 信号事件必须携带信号对象")
    if event_type == "change_proposed" and payload.get("target") not in {
        "response",
        "artifact",
        "plan",
        "prompt",
        "tool_configuration",
        "memory_entry",
        "skill",
        "policy",
        "validator",
    }:
        errors.append("change proposal target is invalid / 改变提案目标无效")
    if event_type == "revalidation_finished" and payload.get("status") not in {
        "passed",
        "failed",
        "unknown",
    }:
        errors.append("finished revalidation has an invalid status / 已结束复验的状态无效")
    if event_type == "attribution_evidence_recorded":
        state = payload.get("state")
        new_evidence = payload.get("new_evidence_bindings")
        all_evidence = payload.get("evidence_bindings")
        if state not in _ATTRIBUTION_RANK or state == "unattributed":
            errors.append("attribution event has an invalid promoted state / 归因事件的晋升状态无效")
        elif payload.get("evidence_kind") != _ATTRIBUTION_EVIDENCE_KIND[state]:
            errors.append("attribution evidence kind differs from state / 归因证据类型与状态不一致")
        if not isinstance(payload.get("evidence_authority_binding"), Mapping):
            errors.append("attribution event lacks an evidence authority / 归因事件缺少证据权威")
        binding_lists_valid = (
            isinstance(new_evidence, list)
            and bool(new_evidence)
            and all(isinstance(binding, Mapping) for binding in new_evidence)
            and isinstance(all_evidence, list)
            and all(isinstance(binding, Mapping) for binding in all_evidence)
        )
        if not binding_lists_valid or not _binding_set(new_evidence).issubset(
            _binding_set(all_evidence)
        ):
            errors.append("attribution event lacks newly bound evidence / 归因事件缺少新增绑定证据")
        if before is not after:
            errors.append("attribution evidence must preserve runtime state / 归因证据事件必须保持运行状态")
    if event_type == "rollback_verified" and payload.get("verified") is not True:
        errors.append("rollback verification must be explicit true / 回滚验证必须明确为 true")
    if event_type == "reflection_stopped":
        try:
            outcome = ReflectionOutcome(payload["outcome"])
            expected = _OUTCOME_STATE[outcome]
            if outcome is ReflectionOutcome.CONTINUE or after is not expected:
                errors.append("stop event requires a matching terminal outcome / 停止事件必须匹配终态结果")
            if round_id is not None and before is not after:
                errors.append("post-round stop must preserve the terminal state / 轮后停止事件必须保持终态")
            if before in _TERMINAL_STATES and round_id is None:
                errors.append("post-round stop requires its round binding / 轮后停止事件必须绑定轮次")
            if before not in _TERMINAL_STATES and round_id is not None:
                errors.append("non-admitted stop cannot invent a round binding / 未准入停止事件不得虚构轮次绑定")
            if not isinstance(payload["stop_reason"], str) or not payload[
                "stop_reason"
            ].strip():
                errors.append("stop event requires a non-empty reason / 停止事件必须有非空原因")
        except (KeyError, TypeError, ValueError):
            errors.append("stop outcome is invalid / 停止结果无效")
    if event_type == "learning_promotion_evaluated":
        candidate = payload.get("learning_candidate")
        if not isinstance(candidate, Mapping) or set(candidate) != {
            "target",
            "candidate_binding",
            "source_round_id",
            "source_subject_binding",
            "round_evidence_bindings",
            "decision",
            "promotion_evidence_bindings",
            "authorization_binding",
            "owner_binding",
        }:
            errors.append("learning event lacks a complete public decision / 学习事件缺少完整公开决定")
    if event_type == "change_applied":
        subject_after = payload.get("subject_after_binding")
        if not isinstance(subject_after, Mapping) or _binding_key(
            event["subject_binding"]
        ) != _binding_key(subject_after):
            errors.append("change-applied subject does not match payload / 改变应用事件的对象与载荷不匹配")
    if errors:
        raise ReflectionValidationError(errors)


def validate_reflection_event_stream(
    events: Sequence[Mapping[str, Any]],
    *,
    contract: Mapping[str, Any] | None = None,
    require_origin: bool = True,
) -> None:
    """Replay a contiguous reflection event stream / 重放连续反思事件流。"""

    if not events:
        raise ReflectionValidationError(["reflection event stream is empty / 反思事件流为空"])
    normalized = [deepcopy(dict(event)) for event in events]
    for event in normalized:
        validate_reflection_event(event)
    errors: list[str] = []
    sequences = [int(event["sequence"]) for event in normalized]
    expected_start = 1 if require_origin else sequences[0]
    if sequences != list(range(expected_start, expected_start + len(sequences))):
        errors.append("reflection event sequence is not contiguous / 反思事件序列不连续")
    if len({event["event_id"] for event in normalized}) != len(normalized):
        errors.append("reflection event identifiers are not unique / 反思事件标识不唯一")
    if len({event["idempotency_key"] for event in normalized}) != len(normalized):
        errors.append("reflection idempotency keys are not unique / 反思幂等键不唯一")
    first = normalized[0]
    if require_origin and first["event_type"] != "reflection_started":
        errors.append("origin stream must start with reflection_started / 完整事件流必须从 reflection_started 开始")
    if require_origin:
        lifecycle_prefix = [event["event_type"] for event in normalized[:3]]
        if lifecycle_prefix != [
            "reflection_started",
            "reflection_eligibility_evaluated",
            "reflection_routed",
        ]:
            errors.append("origin stream has an invalid admission prefix / 完整事件流的准入前缀无效")
        for event_type in (
            "reflection_started",
            "reflection_eligibility_evaluated",
            "reflection_routed",
        ):
            if sum(event["event_type"] == event_type for event in normalized) != 1:
                errors.append(f"origin stream must contain exactly one {event_type} / 完整事件流的生命周期事件数量无效")
    for previous, current in zip(normalized, normalized[1:]):
        if previous["state_after"] != current["state_before"]:
            errors.append("reflection state chain is broken / 反思状态链断裂")
        if previous["reflection_id"] != current["reflection_id"]:
            errors.append("reflection identity changes inside one stream / 同一事件流内反思标识发生变化")
        if previous["contract_binding"] != current["contract_binding"]:
            errors.append("contract binding changes inside one stream / 同一事件流内契约绑定发生变化")
        if previous["route"] != current["route"]:
            errors.append("route changes inside one reflection stream / 同一反思事件流内路由发生变化")

    expected_subject: dict[str, Any] = (
        deepcopy(dict(contract["subject_binding"]))
        if contract is not None and require_origin
        else deepcopy(dict(first["subject_binding"]))
    )
    active_round: str | None = None
    last_closed_round: str | None = None
    seen_rounds: set[str] = set()
    last_round_number: int | None = 0 if require_origin else None
    consumed_signal_bindings: set[tuple[Any, Any, Any]] = set()
    round_has_qualified_signal = False
    attribution: dict[str, Any] | None = _initial_attribution() if require_origin else None
    attribution_evidence: set[tuple[Any, Any, Any]] = set()
    stop_seen = False
    seen_subjects = {_binding_key(expected_subject)}
    round_change: dict[str, Any] | None = None
    started_validators: list[dict[str, Any]] = []
    rollback_phase: str | None = None
    round_subject_before: dict[str, Any] | None = None
    replayed_rollback: dict[str, Any] | None = None
    round_evidence_bindings: set[tuple[Any, Any, Any]] = set()
    round_validation: dict[str, Any] | None = None
    round_signal: dict[str, Any] | None = None
    round_proposal_count = 0
    round_deviation_count = 0
    pending_learning_candidate: dict[str, Any] | None = None
    for event in normalized:
        if stop_seen:
            errors.append("events occur after reflection_stopped / reflection_stopped 之后仍有事件")
        if event["event_type"] == "change_applied":
            next_subject = deepcopy(dict(event["payload"]["subject_after_binding"]))
            next_key = _binding_key(next_subject)
            if next_key in seen_subjects:
                errors.append("change-applied reused a prior subject version / 改变应用重复使用了先前对象版本")
            seen_subjects.add(next_key)
            expected_subject = next_subject
        elif event["event_type"] == "rollback_applied":
            expected_subject = deepcopy(
                dict(event["payload"]["restored_subject_binding"])
            )
        if _binding_key(event["subject_binding"]) != _binding_key(expected_subject):
            errors.append(f"subject binding drift at event {event['event_id']} / 事件对象绑定漂移")
        if event["event_type"] == "reflection_round_started":
            if active_round is not None:
                errors.append("a reflection round started before the prior round closed / 前一轮未关闭又启动新轮次")
            if event["round_id"] in seen_rounds:
                errors.append("reflection round identifier was reused / 反思轮次标识被重复使用")
            active_round = event["round_id"]
            seen_rounds.add(str(event["round_id"]))
            round_number = event["payload"].get("round_number")
            if last_round_number is not None and round_number != last_round_number + 1:
                errors.append("reflection round numbers are not contiguous / 反思轮次序号不连续")
            if isinstance(round_number, int) and not isinstance(round_number, bool):
                last_round_number = round_number
            round_has_qualified_signal = False
            round_change = None
            started_validators = []
            rollback_phase = None
            round_subject_before = deepcopy(event["subject_binding"])
            replayed_rollback = None
            round_evidence_bindings = set()
            round_validation = None
            round_signal = None
            round_proposal_count = 0
            round_deviation_count = 0
            pending_learning_candidate = None
            if contract is not None:
                try:
                    signal = _validate_new_signal_record(
                        event["payload"].get("new_signal", {}),
                        contract,
                        consumed_bindings=consumed_signal_bindings,
                    )
                    if signal["qualified"]:
                        consumed_signal_bindings |= _binding_set(signal["evidence_bindings"])
                        round_evidence_bindings |= _binding_set(
                            signal["evidence_bindings"]
                        )
                        round_has_qualified_signal = True
                    round_signal = signal
                except (TypeError, ValueError, ReflectionValidationError) as exc:
                    errors.append(f"invalid round-start signal: {exc} / 轮次开始信号无效")
                if (
                    not event["payload"].get("new_signal", {}).get("qualified", False)
                    and contract["trigger"]["evidence_plan_binding"] is None
                ):
                    errors.append("unqualified round lacks the contract evidence plan / 未获有效信号的轮次缺少契约取证计划")
                if _binding_key(event["payload"].get("baseline_binding", {})) != _binding_key(
                    _baseline_binding(contract)
                ):
                    errors.append("round-start baseline differs from the sealed contract / 轮次开始基线偏离封存契约")
            attribution_before = event["payload"].get("attribution_before")
            if not isinstance(attribution_before, Mapping):
                errors.append("round start lacks an attribution checkpoint / 轮次开始缺少归因检查点")
            else:
                if attribution is None:
                    attribution = deepcopy(dict(attribution_before))
                    attribution_evidence = _binding_set(
                        attribution.get("evidence_bindings", [])
                    )
                elif dict(attribution_before) != attribution:
                    errors.append("round attribution checkpoint differs from replayed state / 轮次归因检查点与重放状态不一致")
        elif event["event_type"] == "reflection_signal_recorded":
            if contract is not None:
                try:
                    signal = _validate_new_signal_record(
                        event["payload"].get("new_signal", {}),
                        contract,
                        consumed_bindings=consumed_signal_bindings,
                    )
                    if not signal["qualified"] or round_has_qualified_signal:
                        errors.append("a round may acquire exactly one qualified signal set / 单轮只能获得一组有效新信号")
                    else:
                        consumed_signal_bindings |= _binding_set(signal["evidence_bindings"])
                        round_evidence_bindings |= _binding_set(
                            signal["evidence_bindings"]
                        )
                        round_has_qualified_signal = True
                        round_signal = signal
                except (TypeError, ValueError, ReflectionValidationError) as exc:
                    errors.append(f"invalid recorded signal: {exc} / 已记录信号无效")
        elif event["event_type"] == "deviation_detected":
            round_deviation_count += 1
            if round_deviation_count > 1:
                errors.append("one round recorded multiple governed deviations / 单轮记录了多个受治理偏差")
            evidence = event["payload"].get("evidence_bindings", [])
            if isinstance(evidence, list) and all(
                isinstance(binding, Mapping) for binding in evidence
            ):
                round_evidence_bindings |= _binding_set(evidence)
        elif event["event_type"] == "attribution_evidence_recorded":
            payload = event["payload"]
            state = payload.get("state")
            if attribution is None or state not in _ATTRIBUTION_RANK:
                errors.append("attribution event has no replayable predecessor / 归因事件缺少可重放前态")
            else:
                prior_state = attribution.get("state")
                if (
                    prior_state not in _ATTRIBUTION_RANK
                    or _ATTRIBUTION_RANK[state] != _ATTRIBUTION_RANK[prior_state] + 1
                ):
                    errors.append("attribution promotion does not advance exactly one level / 归因晋升未严格前进一级")
                new_bindings = payload.get("new_evidence_bindings", [])
                if not isinstance(new_bindings, list) or not all(
                    isinstance(binding, Mapping) for binding in new_bindings
                ):
                    errors.append("attribution evidence bindings are malformed / 归因证据绑定格式无效")
                else:
                    new_set = _binding_set(new_bindings)
                    if not new_set or len(new_set) != len(new_bindings):
                        errors.append("attribution promotion evidence is empty or duplicated / 归因晋升证据为空或重复")
                    if new_set & attribution_evidence:
                        errors.append("attribution promotion reused prior evidence / 归因晋升重复使用先前证据")
                    cumulative = payload.get("evidence_bindings", [])
                    if not isinstance(cumulative, list) or not all(
                        isinstance(binding, Mapping) for binding in cumulative
                    ) or _binding_set(cumulative) != attribution_evidence | new_set:
                        errors.append("attribution cumulative evidence cannot be reproduced / 归因累计证据无法重算")
                    attribution_evidence |= new_set
                if prior_state != "unattributed" and any(
                    payload.get(field) != attribution.get(field)
                    for field in ("hypothesis", "falsifier", "confounders")
                ):
                    errors.append("attribution promotion changed the governed hypothesis / 归因晋升篡改了受治理假设")
                attribution = {
                    field: deepcopy(payload.get(field))
                    for field in (
                        "state",
                        "hypothesis",
                        "falsifier",
                        "confounders",
                        "evidence_kind",
                        "evidence_authority_binding",
                        "evidence_bindings",
                    )
                }
        elif event["event_type"] == "change_proposed":
            round_proposal_count += 1
            round_change = {
                "target": event["payload"].get("target"),
                "proposal_binding": deepcopy(
                    event["payload"].get("proposal_binding")
                ),
                "authorization_binding": None,
                "validator_approval_binding": None,
                "subject_after_binding": None,
            }
            if contract is not None:
                target = event["payload"].get("target")
                policy = contract["change_policy"]
                if target not in policy["allowed_targets"] or target in policy[
                    "forbidden_targets"
                ]:
                    errors.append("change proposal violates the sealed contract / 改变提案违反封存契约")
                if round_proposal_count > policy["max_changes_per_round"]:
                    errors.append("event stream exceeds the per-round change budget / 事件流超过单轮改变预算")
        elif event["event_type"] == "change_authorized":
            if round_change is None:
                errors.append("change authorization lacks a replayed proposal / 改变授权缺少可重放提案")
            else:
                round_change["authorization_binding"] = deepcopy(
                    event["payload"].get("authorization_binding")
                )
                round_change["validator_approval_binding"] = deepcopy(
                    event["payload"].get("validator_change_approval_binding")
                )
                if contract is not None:
                    policy = contract["change_policy"]
                    if _binding_key(
                        round_change["authorization_binding"] or {}
                    ) != _binding_key(policy["authorizer_binding"]):
                        errors.append("change authorization violates the sealed contract / 改变授权违反封存契约")
                    validator_approval = round_change["validator_approval_binding"]
                    if round_change["target"] == "validator":
                        expected_approval = contract["validation_policy"][
                            "validator_change_authorizer_binding"
                        ]
                        if expected_approval is None or _binding_key(
                            validator_approval or {}
                        ) != _binding_key(expected_approval):
                            errors.append("validator change lacks contract approval / 验证器改变缺少契约审批")
                    elif validator_approval is not None:
                        errors.append("non-validator change carries validator approval / 非验证器改变携带验证器审批")
        elif event["event_type"] == "change_rejected":
            round_change = None
        elif event["event_type"] == "change_applied":
            if round_change is None:
                errors.append("applied change lacks a replayed proposal / 已应用改变缺少可重放提案")
            else:
                round_change["subject_after_binding"] = deepcopy(
                    event["payload"].get("subject_after_binding")
                )
        elif event["event_type"] == "revalidation_started":
            started_validators = deepcopy(
                event["payload"].get("validator_bindings", [])
            )
            if round_change is None or _binding_key(
                event["payload"].get("candidate_binding") or {}
            ) != _binding_key(round_change.get("subject_after_binding") or {}):
                errors.append("revalidation start differs from the applied candidate / 复验开始候选与已应用对象不一致")
        elif event["event_type"] == "revalidation_finished":
            round_validation = deepcopy(dict(event["payload"]))
            validation_evidence = event["payload"].get("evidence_bindings", [])
            if isinstance(validation_evidence, list) and all(
                isinstance(binding, Mapping) for binding in validation_evidence
            ):
                round_evidence_bindings |= _binding_set(validation_evidence)
            if _binding_set(started_validators) != _binding_set(
                event["payload"].get("validator_bindings", [])
            ):
                errors.append("finished revalidation differs from its started validators / 复验结束使用的验证器与开始事件不一致")
            candidate = event["payload"].get("candidate_binding")
            if round_change is not None and _binding_key(candidate or {}) != _binding_key(
                round_change.get("subject_after_binding") or {}
            ):
                errors.append("revalidation candidate differs from the applied change / 复验候选与已应用改变不一致")
            if (
                contract is not None
                and round_signal is not None
                and round_subject_before is not None
            ):
                errors.extend(
                    _contract_bound_validation_errors(
                        event["payload"],
                        contract,
                        new_signal=round_signal,
                        subject_before_binding=round_subject_before,
                        candidate_binding=(
                            round_change.get("subject_after_binding")
                            if round_change is not None
                            else None
                        ),
                        started_validator_bindings=started_validators,
                        validator_changed=bool(
                            round_change is not None
                            and round_change.get("target") == "validator"
                        ),
                    )
                )
        elif event["event_type"] == "rollback_started":
            rollback_phase = "started"
            replayed_rollback = deepcopy(dict(event["payload"]))
            if round_change is None or _binding_key(
                event["payload"].get("failed_subject_binding") or {}
            ) != _binding_key(round_change.get("subject_after_binding") or {}):
                errors.append("rollback does not bind the failed changed subject / 回滚未绑定失败的改变后对象")
            if round_subject_before is None or _binding_key(
                event["payload"].get("restored_subject_binding") or {}
            ) != _binding_key(round_subject_before):
                errors.append("rollback target differs from the round before-subject / 回滚目标与本轮改变前对象不一致")
        elif event["event_type"] == "rollback_applied":
            if rollback_phase != "started":
                errors.append("rollback apply lacks a started rollback / 回滚应用缺少回滚开始事件")
            rollback_phase = "applied"
            if replayed_rollback is None or _binding_key(
                event["payload"].get("restored_subject_binding") or {}
            ) != _binding_key(replayed_rollback.get("restored_subject_binding") or {}):
                errors.append("applied rollback differs from its start event / 已应用回滚与开始事件不一致")
        elif event["event_type"] == "rollback_verified":
            if rollback_phase != "applied":
                errors.append("rollback verification lacks an applied rollback / 回滚验证缺少已应用回滚")
            rollback_phase = "verified"
            if replayed_rollback is None or _binding_key(
                event["payload"].get("restored_subject_binding") or {}
            ) != _binding_key(replayed_rollback.get("restored_subject_binding") or {}):
                errors.append("verified rollback differs from its start event / 已验证回滚与开始事件不一致")
        elif event["event_type"] == "reflection_round_finished":
            if event["payload"].get("outcome") == "rolled_back" and rollback_phase != "verified":
                errors.append("rolled-back outcome lacks a verified recovery chain / 已回滚结果缺少已验证恢复链")
            if rollback_phase is not None and event["payload"].get("outcome") != "rolled_back":
                errors.append("verified rollback closed under a different outcome / 已验证回滚以其他结果关闭")
            if attribution is not None and attribution.get("state") in {
                "controlled_replay",
                "intervention_verified",
            } and not (
                round_validation is not None
                and round_validation.get("status") == "passed"
                and round_validation.get("mandatory_pass") is True
                and round_validation.get("regression_pass") is True
                and round_validation.get("comparison_state")
                in {"comparable", "independently_rebased"}
            ):
                errors.append("strong attribution lacks passed comparable revalidation / 强归因缺少通过且可比的复验")
            if contract is not None:
                candidate = event["payload"].get("learning_candidate")
                try:
                    pending_learning_candidate = _validate_learning_candidate(
                        candidate,
                        contract,
                        outcome=ReflectionOutcome(event["payload"].get("outcome")),
                        round_id=event["round_id"],
                        source_subject_binding=event["subject_binding"],
                        available_round_evidence=round_evidence_bindings,
                    )
                except (TypeError, ValueError, ReflectionRuntimeError) as exc:
                    errors.append(f"invalid round learning decision: {exc} / 轮次学习决定无效")
        elif event["event_type"] == "learning_promotion_evaluated" and contract is not None:
            if event["payload"].get("learning_candidate") != pending_learning_candidate:
                errors.append("learning event differs from the round decision / 学习事件与轮次决定不一致")
            try:
                _validate_learning_candidate(
                    event["payload"].get("learning_candidate"),
                    contract,
                    outcome=ReflectionOutcome.ACCEPTED,
                    round_id=event["round_id"],
                    source_subject_binding=event["subject_binding"],
                    available_round_evidence=round_evidence_bindings,
                )
            except (TypeError, ValueError, ReflectionRuntimeError) as exc:
                errors.append(f"invalid learning event: {exc} / 学习事件无效")
            pending_learning_candidate = None
        if event["round_id"] is not None and event["event_type"] not in {
            "reflection_round_started",
            "reflection_stopped",
            "learning_promotion_evaluated",
        }:
            if active_round != event["round_id"]:
                errors.append(f"event {event['event_id']} is outside its active round / 事件不属于活动轮次")
        if event["event_type"] == "reflection_round_finished":
            last_closed_round = active_round
            active_round = None
        if event["event_type"] in {"reflection_stopped", "learning_promotion_evaluated"} and event[
            "round_id"
        ] is not None and event["round_id"] != last_closed_round:
            errors.append("post-round event does not bind the closed round / 轮后事件未绑定已关闭轮次")
        if event["event_type"] == "reflection_stopped":
            stop_seen = True

    if contract is not None:
        validate_reflection_contract(contract)
        expected_contract = _contract_binding(contract)
        for event in normalized:
            if event["reflection_id"] != contract["reflection_id"]:
                errors.append("event reflection identity differs from contract / 事件反思标识与契约不同")
            if _binding_key(event["contract_binding"]) != _binding_key(expected_contract):
                errors.append("event contract binding mismatch / 事件契约绑定不匹配")
            if event["route"] != contract["admission"]["route"]:
                errors.append("event route differs from contract / 事件路由偏离契约")
        for event in normalized:
            event_type = event["event_type"]
            payload = event["payload"]
            if event_type == "reflection_started":
                if payload.get("trigger_type") != contract["trigger"]["trigger_type"]:
                    errors.append("event trigger differs from contract / 事件触发类型偏离契约")
            elif event_type == "reflection_eligibility_evaluated":
                if (
                    payload.get("eligibility") != contract["admission"]["eligibility"]
                    or payload.get("reason_codes")
                    != contract["admission"]["reason_codes"]
                ):
                    errors.append("event admission decision differs from contract / 事件准入决定偏离契约")
            elif event_type == "reflection_routed":
                if payload.get("route") != contract["admission"]["route"]:
                    errors.append("event routing decision differs from contract / 事件路由决定偏离契约")
            elif event_type == "change_proposed":
                target = payload.get("target")
                change_policy = contract["change_policy"]
                if target not in change_policy["allowed_targets"] or target in change_policy[
                    "forbidden_targets"
                ]:
                    errors.append("event stream proposes a contract-forbidden target / 事件流提议了契约禁止目标")
            elif event_type == "change_authorized":
                change_policy = contract["change_policy"]
                if _binding_key(payload.get("authorization_binding") or {}) != _binding_key(
                    change_policy["authorizer_binding"]
                ):
                    errors.append("event stream change authorization differs from contract / 事件流改变授权偏离契约")
                validator_approval = payload.get("validator_change_approval_binding")
                if validator_approval is not None and _binding_key(
                    validator_approval
                ) != _binding_key(
                    contract["validation_policy"]["validator_change_authorizer_binding"]
                    or {}
                ):
                    errors.append("event stream validator approval differs from contract / 事件流验证器审批偏离契约")
            elif event_type in {"revalidation_started", "revalidation_finished"}:
                supplied = _binding_set(payload.get("validator_bindings", []))
                required = _binding_set(
                    contract["validation_policy"]["mandatory_validator_bindings"]
                ) | _binding_set(
                    contract["validation_policy"]["regression_validator_bindings"]
                )
                if not required.issubset(supplied):
                    errors.append("event stream revalidation omits contract validators / 事件流复验遗漏契约验证器")
            elif event_type == "attribution_evidence_recorded":
                state = payload.get("state")
                if state in _ATTRIBUTION_AUTHORITY_FIELD:
                    allowed_authorities = _binding_set(
                        contract["attribution_policy"][
                            _ATTRIBUTION_AUTHORITY_FIELD[state]
                        ]
                    )
                    if _binding_key(
                        payload.get("evidence_authority_binding") or {}
                    ) not in allowed_authorities:
                        errors.append("event stream attribution authority differs from contract / 事件流归因权威偏离契约")
            elif event_type == "rollback_started":
                if _binding_key(payload.get("rollback_binding") or {}) != _binding_key(
                    contract["stop_policy"]["rollback_binding"]
                ):
                    errors.append("event stream rollback binding differs from contract / 事件流回滚绑定偏离契约")
            elif event_type == "reflection_stopped":
                if payload.get("outcome") not in contract["stop_policy"][
                    "terminal_outcomes"
                ]:
                    errors.append("event stream stop outcome is outside contract / 事件流停止结果超出契约")
        if require_origin:
            baseline_events = [
                event
                for event in normalized
                if event["event_type"] == "reflection_baseline_frozen"
            ]
            if contract["admission"]["eligibility"] == "admitted":
                if len(baseline_events) != 1:
                    errors.append("admitted stream must freeze exactly one baseline / 已准入事件流必须且只能冻结一次基线")
                elif _binding_key(baseline_events[0]["payload"].get("baseline_binding", {})) != _binding_key(
                    _baseline_binding(contract)
                ):
                    errors.append("frozen baseline event differs from contract / 基线冻结事件偏离契约")
            elif baseline_events:
                errors.append("non-admitted stream cannot freeze a baseline / 未准入事件流不得冻结基线")
    if pending_learning_candidate is not None:
        errors.append("learning decision lacks learning_promotion_evaluated / 学习决定缺少 learning_promotion_evaluated 事件")
    if errors:
        raise ReflectionValidationError(errors)


def validate_reflection_round_observation(
    observation: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    events: Sequence[Mapping[str, Any]] | None = None,
) -> None:
    """Validate closure, anti-gaming, and improvement semantics / 校验闭环、反投机与改善语义。"""

    validate_schema("reflection_round_observation", observation)
    validate_artifact_hash("reflection_round_observation", observation)
    errors: list[str] = []

    outcome = ReflectionOutcome(observation["outcome"])
    terminal = bool(observation["terminal"])
    stop_reason = observation["stop_reason"]
    validation = observation["validation"]
    change = observation["change"]
    improvement = ReflectionImprovementState(observation["improvement_state"])
    attribution = observation["attribution"]
    rollback = observation["rollback"]
    learning_candidate = observation["learning_candidate"]

    if contract is not None:
        errors.extend(
            _contract_bound_validation_errors(
                validation,
                contract,
                new_signal=observation["new_signal"],
                subject_before_binding=observation["subject_before_binding"],
                candidate_binding=(
                    rollback["failed_subject_binding"]
                    if rollback is not None
                    else observation["subject_after_binding"]
                ),
                validator_changed=bool(
                    change is not None and change["validator_changed"]
                ),
            )
        )

    if terminal != (outcome is not ReflectionOutcome.CONTINUE):
        errors.append("terminal flag does not match outcome / terminal 标记与轮次结果不一致")
    if terminal and not stop_reason:
        errors.append("terminal reflection requires a stop reason / 反思终态必须有停止原因")
    if not terminal and stop_reason is not None:
        errors.append("continuing reflection cannot carry a terminal stop reason / 继续反思不得携带终态停止原因")

    if validation["status"] == "not_run" and any(
        validation[field] is not None
        for field in (
            "mandatory_pass",
            "regression_pass",
            "criteria_binding",
            "environment_binding",
            "metric_id",
            "baseline_value",
            "result_value",
            "improvement_delta",
            "threshold_met",
            "candidate_binding",
        )
    ):
        errors.append("not-run validation cannot contain verdicts or measurements / 未运行复验不得包含裁定或测量")
    if validation["status"] == "not_run" and (
        validation["comparison_state"] != "not_evaluated"
        or validation["validator_bindings"]
        or validation["evidence_bindings"]
        or validation["result_progress"]
    ):
        errors.append("not-run validation cannot claim comparison, evidence, or result progress / 未运行复验不得声明比较、证据或结果进展")
    if validation["status"] in {"passed", "failed"} and any(
        validation[field] is None
        for field in (
            "mandatory_pass",
            "regression_pass",
            "criteria_binding",
            "metric_id",
            "baseline_value",
            "result_value",
            "improvement_delta",
            "threshold_met",
            "candidate_binding",
        )
    ):
        errors.append("completed validation requires complete measurement fields / 已完成复验必须包含完整测量字段")
    if validation["status"] == "unknown" and any(
        validation[field] is not None
        for field in (
            "mandatory_pass",
            "regression_pass",
            "metric_id",
            "baseline_value",
            "result_value",
            "improvement_delta",
            "threshold_met",
        )
    ):
        errors.append("unknown validation cannot contain definitive verdicts or measurements / 结果未知的复验不得包含确定裁定或测量")
    if validation["status"] == "unknown" and validation["result_progress"]:
        errors.append("unknown validation cannot claim result progress / 结果未知的复验不得声明结果进展")
    independent_bindings = validation["independent_signal_bindings"]
    independent_binding_set = _binding_set(independent_bindings)
    if validation["independent_signal_count"] != len(independent_binding_set):
        errors.append("independent signal count cannot be reproduced / 独立信号数无法重算")
    observable_signal_bindings = _binding_set(
        observation["new_signal"]["evidence_bindings"]
    )
    if independent_binding_set != observable_signal_bindings:
        errors.append("independent signals must equal the qualified signal evidence / 独立信号必须与有效新信号证据完全一致")
    derived_information_progress = bool(
        observation["new_signal"]["qualified"]
        and observation["new_signal"]["information_gain"] != "none"
        and observation["new_signal"]["evidence_bindings"]
    )
    if validation["information_progress"] is not derived_information_progress:
        errors.append("information-progress flag cannot be reproduced / 信息进展标记无法重算")
    if validation["status"] in {"passed", "failed"} and not validation[
        "evidence_bindings"
    ]:
        errors.append("completed validation requires evidence bindings / 已完成复验必须绑定证据")
    if validation["status"] == "passed" and validation["mandatory_pass"] is not True:
        errors.append("passed validation requires mandatory_pass=true / 复验通过要求必选检查为 true")
    if validation["validator_gaming"] and outcome in {
        ReflectionOutcome.CONTINUE,
        ReflectionOutcome.ACCEPTED,
    }:
        errors.append("validator gaming blocks acceptance and continuation / 验证器投机阻断接受与继续")
    if validation["regression_pass"] is False and outcome in {
        ReflectionOutcome.CONTINUE,
        ReflectionOutcome.ACCEPTED,
    }:
        errors.append("blocking regression requires rollback or terminal handling / 阻断级回归必须回滚或进入终态处理")

    if outcome is ReflectionOutcome.CONTINUE and not (
        validation["result_progress"] or validation["information_progress"]
    ):
        errors.append("continuation requires result or information progress / 继续循环必须存在结果进展或信息进展")

    comparable = validation["comparison_state"] in {
        "comparable",
        "independently_rebased",
    }
    rebased_baseline = validation["rebased_baseline"]
    if validation["comparison_state"] == "independently_rebased":
        if rebased_baseline is None:
            errors.append("independent rebasing requires a bound baseline record / 独立重建比较必须绑定基线记录")
        else:
            rebase_content = {
                key: deepcopy(rebased_baseline[key])
                for key in (
                    "subject_before_binding",
                    "criteria_binding",
                    "environment_binding",
                    "validator_bindings",
                    "regression_scope_bindings",
                    "metric_id",
                    "metric_value",
                    "approval_binding",
                    "evidence_bindings",
                )
            }
            if rebased_baseline["baseline_binding"]["hash"] != artifact_fingerprint(
                rebase_content
            ):
                errors.append("rebased baseline hash cannot be reproduced / 重建基线哈希无法重算")
            if _binding_key(validation["criteria_binding"] or {}) != _binding_key(
                rebased_baseline["criteria_binding"]
            ) or _binding_key(validation["environment_binding"] or {}) != _binding_key(
                rebased_baseline["environment_binding"] or {}
            ):
                errors.append("validation does not use the rebased criteria and environment / 复验未使用重建的标准与环境")
            if _binding_set(validation["validator_bindings"]) != _binding_set(
                rebased_baseline["validator_bindings"]
            ):
                errors.append("validation validators differ from the rebased baseline / 复验验证器与重建基线不同")
            if _binding_key(rebased_baseline["subject_before_binding"]) != _binding_key(
                observation["subject_before_binding"]
            ):
                errors.append("rebased baseline uses a different before-subject / 重建基线使用了不同的改变前对象")
            if validation["metric_id"] != rebased_baseline["metric_id"] or not math.isclose(
                float(validation["baseline_value"]),
                float(rebased_baseline["metric_value"]),
                rel_tol=1e-12,
                abs_tol=1e-12,
            ):
                errors.append("validation metric baseline differs from the approved rebase / 复验指标基线与获批重建基线不一致")
    elif rebased_baseline is not None:
        errors.append("rebased baseline is only legal for independently_rebased comparison / 只有独立重建比较可携带重建基线")
    if improvement is ReflectionImprovementState.VERIFIED_IMPROVEMENT:
        if not (
            validation["status"] == "passed"
            and validation["mandatory_pass"] is True
            and validation["regression_pass"] is True
            and validation["threshold_met"] is True
            and validation["result_progress"]
            and bool(validation["evidence_bindings"])
            and comparable
            and not validation["validator_gaming"]
        ):
            errors.append("verified improvement lacks comparable, regression-free validation / 已验证改善缺少可比、无回归复验")
    if improvement is ReflectionImprovementState.REGRESSION and validation[
        "regression_pass"
    ] is not False:
        errors.append("regression classification requires regression_pass=false / 回归分类要求回归检查为 false")

    if outcome is ReflectionOutcome.ACCEPTED:
        if improvement is not ReflectionImprovementState.VERIFIED_IMPROVEMENT:
            errors.append("accepted change must be a verified improvement / 接受改变必须属于已验证改善")
        if change is None or not change["applied"] or observation["subject_after_binding"] is None:
            errors.append("accepted reflection requires an applied, version-bound change / 接受反思必须绑定已应用改变与新版本")
        if observation["deviation"] is None:
            errors.append("accepted reflection requires an evidenced deviation / 接受反思必须存在有证据偏差")
        if not validation["evidence_bindings"]:
            errors.append("accepted reflection requires revalidation evidence / 接受反思必须绑定复验证据")
    if outcome is ReflectionOutcome.ROLLED_BACK:
        if rollback is None or rollback["verified"] is not True:
            errors.append("rolled-back outcome requires a verified rollback record / 已回滚结果必须有已验证回滚记录")
        elif observation["subject_after_binding"] is None or _binding_key(
            observation["subject_after_binding"]
        ) != _binding_key(rollback["restored_subject_binding"]):
            errors.append("rolled-back observation must end at the restored subject / 已回滚观察包必须以恢复对象结束")
    elif rollback is not None:
        errors.append("rollback record is only legal for a rolled-back outcome / 回滚记录只能用于已回滚结果")

    if change is not None:
        if change["validator_changed"]:
            if not change["validator_change_approved"]:
                errors.append("validator change lacks independent approval / 验证器改变缺少独立审批")
            if validation["comparison_state"] != "independently_rebased":
                errors.append("approved validator change requires independent rebasing / 已批准验证器改变必须独立重建比较基线")
        elif change["validator_change_approved"]:
            errors.append("validator approval is set without a validator change / 未改变验证器却记录了验证器审批")

    if attribution["state"] in {"hypothesis", "correlational", "controlled_replay", "intervention_verified"}:
        if not attribution["hypothesis"] or not attribution["falsifier"]:
            errors.append("attribution claims require a falsifiable hypothesis / 归因声明必须有可证伪假设")
        if not attribution["evidence_bindings"]:
            errors.append("attribution claim requires evidence bindings / 归因声明必须绑定证据")
        if attribution["evidence_authority_binding"] is None:
            errors.append("attribution claim requires an evidence authority / 归因声明必须绑定证据权威")
    elif any(
        (
            attribution["hypothesis"] is not None,
            attribution["falsifier"] is not None,
            bool(attribution["confounders"]),
            attribution["evidence_authority_binding"] is not None,
            bool(attribution["evidence_bindings"]),
        )
    ):
        errors.append("unattributed state cannot carry attribution claims / 未归因状态不得携带归因声明")
    expected_evidence_kind = _ATTRIBUTION_EVIDENCE_KIND[attribution["state"]]
    if attribution["evidence_kind"] != expected_evidence_kind:
        errors.append("attribution evidence kind does not support its state / 归因证据类型不支持声明状态")
    if attribution["state"] == "intervention_verified" and validation[
        "comparison_state"
    ] not in {"comparable", "independently_rebased"}:
        errors.append("intervention attribution requires comparable results / 干预归因要求结果可比")

    if learning_candidate is not None:
        if outcome is not ReflectionOutcome.ACCEPTED:
            errors.append("learning evaluation is only legal after an accepted round / 学习评估只能发生在已接受轮次之后")
        if learning_candidate["decision"] == "promoted":
            if not learning_candidate["promotion_evidence_bindings"]:
                errors.append("learning promotion requires evidence / 学习晋升必须绑定证据")
            if learning_candidate["authorization_binding"] is None:
                errors.append("learning promotion requires authorization / 学习晋升必须授权")
        elif learning_candidate["authorization_binding"] is not None:
            errors.append("non-promoted learning candidate cannot carry promotion authority / 未晋升学习候选不得携带晋升授权")

    if contract is not None:
        validate_reflection_contract(contract)
        try:
            _validate_new_signal_record(observation["new_signal"], contract)
        except (TypeError, ValueError, ReflectionValidationError) as exc:
            errors.append(f"invalid observation signal: {exc} / 观察包新信号无效")
        if _binding_key(observation["contract_binding"]) != _binding_key(
            _contract_binding(contract)
        ):
            errors.append("observation contract binding mismatch / 观察包契约绑定不匹配")
        if observation["reflection_id"] != contract["reflection_id"]:
            errors.append("observation reflection identity mismatch / 观察包反思标识不匹配")
        if observation["route"] != contract["admission"]["route"]:
            errors.append("observation route differs from contract / 观察包路由偏离契约")
        if observation["round_number"] > contract["stop_policy"]["max_rounds"]:
            errors.append("round number exceeds contract budget / 轮次超过契约预算")
        if _binding_key(observation["baseline_binding"]) != _binding_key(
            _baseline_binding(contract)
        ):
            errors.append("observation baseline binding differs from contract / 观察包基线绑定偏离契约")
        if outcome is not ReflectionOutcome.CONTINUE and outcome.value not in contract[
            "stop_policy"
        ]["terminal_outcomes"]:
            errors.append("terminal outcome is not allowed by contract / 终态结果不在契约允许列表")
        if outcome is ReflectionOutcome.ACCEPTED and validation[
            "independent_signal_count"
        ] < contract["signal_policy"]["min_independent_signals"]:
            errors.append("accepted result lacks required independent signals / 接受结果缺少必需独立信号")
        if validation["status"] in {"passed", "failed"}:
            policy = contract["validation_policy"]
            if validation["comparison_state"] == "comparable":
                if _binding_key(validation["criteria_binding"] or {}) != _binding_key(
                    contract["baseline"]["criteria_binding"]
                ):
                    errors.append("comparable validation changed its criteria / 可比复验改变了判定标准")
                baseline_environment = contract["baseline"]["environment_binding"]
                if _binding_key(validation["environment_binding"] or {}) != _binding_key(
                    baseline_environment or {}
                ):
                    errors.append("comparable validation changed its environment / 可比复验改变了环境绑定")
                if not _binding_set(contract["baseline"]["validator_bindings"]).issubset(
                    _binding_set(validation["validator_bindings"])
                ):
                    errors.append("comparable validation omitted frozen validators / 可比复验遗漏冻结验证器")
                if not math.isclose(
                    float(validation["baseline_value"]),
                    float(contract["baseline"]["metric_value"]),
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ):
                    errors.append("validation changed the frozen metric baseline / 复验改变了冻结指标基线")
            if validation["metric_id"] != policy["improvement_metric_id"]:
                errors.append("validation metric differs from contract / 复验指标偏离契约")
            baseline_value = float(validation["baseline_value"])
            result_value = float(validation["result_value"])
            if not all(
                math.isfinite(value)
                for value in (
                    baseline_value,
                    result_value,
                    float(validation["improvement_delta"]),
                )
            ):
                errors.append("validation measurements must be finite / 复验测量值必须为有限数")
            expected_delta = (
                result_value - baseline_value
                if policy["improvement_direction"] == "higher_is_better"
                else baseline_value - result_value
            )
            supplied_delta = float(validation["improvement_delta"])
            if not math.isclose(
                supplied_delta,
                expected_delta,
                rel_tol=1e-12,
                abs_tol=1e-12,
            ):
                errors.append("improvement delta cannot be reproduced / 改善增量无法重算")
            expected_threshold = expected_delta >= float(policy["improvement_threshold"])
            if validation["threshold_met"] is not expected_threshold:
                errors.append("threshold verdict differs from contract calculation / 阈值裁定与契约重算不一致")
            if validation["result_progress"] is not (expected_delta > 0):
                errors.append("result-progress flag differs from measured delta / 结果进展标记与测量增量不一致")

        policy = contract["change_policy"]
        if change is None:
            if observation["subject_after_binding"] is not None:
                errors.append("unchanged round cannot carry a changed subject / 未改变轮次不得携带改变后对象")
        else:
            if change["target"] not in policy["allowed_targets"] or change["target"] in policy[
                "forbidden_targets"
            ]:
                errors.append("observation change target is outside contract / 观察包改变目标超出契约")
            if _binding_key(change["authorization_binding"]) != _binding_key(
                policy["authorizer_binding"]
            ):
                errors.append("observation change authorization differs from contract / 观察包改变授权偏离契约")
            if change["validator_changed"] is not (change["target"] == "validator"):
                errors.append("validator-change flag differs from the change target / 验证器改变标记与改变目标不一致")
            applied_subject = (
                rollback["failed_subject_binding"]
                if rollback is not None
                else observation["subject_after_binding"]
            )
            if change["applied"] and (
                applied_subject is None
                or _binding_key(applied_subject)
                == _binding_key(observation["subject_before_binding"])
            ):
                errors.append("applied change must bind a distinct subject version / 已应用改变必须绑定不同对象版本")
            if not change["applied"] and observation["subject_after_binding"] is not None:
                errors.append("unapplied change cannot carry a changed subject / 未应用改变不得携带改变后对象")

        if rollback is not None:
            if _binding_key(rollback["rollback_binding"]) != _binding_key(
                contract["stop_policy"]["rollback_binding"]
            ):
                errors.append("rollback record differs from the contract path / 回滚记录偏离契约路径")
            if change is None or not change["applied"]:
                errors.append("rollback requires a previously applied change / 回滚要求先前已应用改变")
            elif validation["candidate_binding"] is not None and _binding_key(
                rollback["failed_subject_binding"]
            ) != _binding_key(validation["candidate_binding"]):
                errors.append("rollback failed-subject binding cannot be reproduced / 回滚失败对象绑定无法重算")
            elif _binding_key(rollback["failed_subject_binding"]) == _binding_key(
                observation["subject_before_binding"]
            ):
                errors.append("rollback failed-subject must be the changed version / 回滚失败对象必须是改变后版本")
            if _binding_key(rollback["restored_subject_binding"]) != _binding_key(
                observation["subject_before_binding"]
            ):
                errors.append("rollback did not restore the round's before-subject / 回滚未恢复本轮改变前对象")
            required_rollback_validators = _binding_set(
                contract["validation_policy"]["mandatory_validator_bindings"]
            ) | _binding_set(
                contract["validation_policy"]["regression_validator_bindings"]
            )
            if not required_rollback_validators.issubset(
                _binding_set(rollback["validator_bindings"])
            ):
                errors.append("rollback verification omits contract validators / 回滚验证遗漏契约验证器")

        if validation["comparison_state"] == "independently_rebased":
            validator_authorizer = contract["validation_policy"][
                "validator_change_authorizer_binding"
            ]
            if change is None or not change["validator_changed"]:
                errors.append("independent rebase requires an approved validator change / 独立重建基线要求已批准验证器改变")
            if rebased_baseline is not None:
                if validator_authorizer is None or _binding_key(
                    rebased_baseline["approval_binding"]
                ) != _binding_key(validator_authorizer):
                    errors.append("rebased baseline lacks the contract authorizer / 重建基线缺少契约授权器")
                if rebased_baseline["metric_id"] != contract["validation_policy"][
                    "improvement_metric_id"
                ]:
                    errors.append("rebased baseline metric differs from contract / 重建基线指标偏离契约")
                if not rebased_baseline["evidence_bindings"]:
                    errors.append("rebased baseline requires reconstruction evidence / 重建基线必须绑定重建证据")

        if attribution["state"] != "unattributed":
            authority_field = _ATTRIBUTION_AUTHORITY_FIELD[attribution["state"]]
            allowed_authorities = _binding_set(
                contract["attribution_policy"][authority_field]
            )
            if _binding_key(
                attribution["evidence_authority_binding"] or {}
            ) not in allowed_authorities:
                errors.append("attribution evidence authority is not contract-approved / 归因证据权威未获契约批准")
        if attribution["state"] in {"controlled_replay", "intervention_verified"} and not (
            validation["status"] == "passed"
            and validation["mandatory_pass"] is True
            and validation["regression_pass"] is True
            and validation["comparison_state"]
            in {"comparable", "independently_rebased"}
        ):
            errors.append("strong attribution requires passed comparable revalidation / 强归因要求通过且可比的复验")

        try:
            available_learning_evidence = _binding_set(
                observation["new_signal"]["evidence_bindings"]
            ) | _binding_set(validation["evidence_bindings"])
            if observation["deviation"] is not None:
                available_learning_evidence |= _binding_set(
                    observation["deviation"]["evidence_bindings"]
                )
            _validate_learning_candidate(
                learning_candidate,
                contract,
                outcome=outcome,
                round_id=observation["round_id"],
                source_subject_binding=observation["subject_after_binding"],
                available_round_evidence=available_learning_evidence,
            )
        except (TypeError, ValueError, ReflectionRuntimeError) as exc:
            errors.append(f"invalid learning decision: {exc} / 学习决定无效")

    if contract is not None and events is None:
        errors.append("contract validation requires the complete event stream / 契约级观察校验必须提供完整事件流")
    elif events is not None:
        normalized_events = [deepcopy(dict(event)) for event in events]
        try:
            validate_reflection_event_stream(
                normalized_events,
                contract=contract,
                require_origin=contract is not None,
            )
        except ReflectionValidationError as exc:
            errors.extend(f"event stream: {error}" for error in exc.errors)

        actual_round_events = [
            event
            for event in normalized_events
            if event.get("round_id") == observation["round_id"]
        ]
        expected_event_keys = [
            _binding_key(binding) for binding in observation["event_bindings"]
        ]
        actual_event_keys = [
            _binding_key(_event_binding(event)) for event in actual_round_events
        ]
        if expected_event_keys != actual_event_keys:
            errors.append("observation event bindings do not equal the recorded round / 观察包事件绑定与已记录轮次不一致")
        if not actual_round_events or actual_round_events[0]["event_type"] != "reflection_round_started":
            errors.append("bound round does not start with reflection_round_started / 已绑定轮次未从 reflection_round_started 开始")
        else:
            start_event = actual_round_events[0]
            if start_event["payload"].get("round_number") != observation["round_number"]:
                errors.append("observation round number differs from its start event / 观察包轮次序号与开始事件不一致")
            if _binding_key(start_event["subject_binding"]) != _binding_key(
                observation["subject_before_binding"]
            ):
                errors.append("observation subject-before differs from its start event / 观察包改变前对象与开始事件不一致")
            if _binding_key(start_event["payload"].get("baseline_binding", {})) != _binding_key(
                observation["baseline_binding"]
            ):
                errors.append("observation baseline differs from its start event / 观察包基线与开始事件不一致")

            signal_events = [
                event
                for event in actual_round_events
                if event["event_type"] in {
                    "reflection_round_started",
                    "reflection_signal_recorded",
                }
            ]
            last_signal = signal_events[-1]["payload"].get("new_signal")
            if last_signal != observation["new_signal"]:
                errors.append("observation signal differs from the recorded signal / 观察包新信号与已记录信号不一致")

            attribution_events = [
                event
                for event in actual_round_events
                if event["event_type"] == "attribution_evidence_recorded"
            ]
            if attribution_events:
                last_payload = attribution_events[-1]["payload"]
                recorded_attribution = {
                    field: deepcopy(last_payload.get(field))
                    for field in (
                        "state",
                        "hypothesis",
                        "falsifier",
                        "confounders",
                        "evidence_kind",
                        "evidence_authority_binding",
                        "evidence_bindings",
                    )
                }
            else:
                recorded_attribution = start_event["payload"].get(
                    "attribution_before"
                )
            if recorded_attribution != attribution:
                errors.append("observation attribution differs from the replayed events / 观察包归因与重放事件不一致")

        deviation_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "deviation_detected"
        ]
        if len(deviation_events) > 1:
            errors.append("one round cannot overwrite its deviation record / 单轮不得覆盖偏差记录")
        recorded_deviation = deviation_events[0]["payload"] if deviation_events else None
        if recorded_deviation != observation["deviation"]:
            errors.append("observation deviation differs from recorded events / 观察包偏差与已记录事件不一致")

        proposal_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "change_proposed"
        ]
        authorization_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "change_authorized"
        ]
        applied_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "change_applied"
        ]
        if len(proposal_events) > 1:
            errors.append("one round proposed more than one change / 单轮提议了多个改变")
        if change is None:
            if authorization_events or applied_events:
                errors.append("observation omitted an authorized or applied change / 观察包遗漏已授权或已应用改变")
        elif not (
            len(proposal_events) == len(authorization_events) == len(applied_events) == 1
        ):
            errors.append("observation change lacks a complete proposal-authorize-apply chain / 观察包改变缺少完整提议—授权—应用链")
        else:
            proposal_payload = proposal_events[0]["payload"]
            authorization_payload = authorization_events[0]["payload"]
            applied_payload = applied_events[0]["payload"]
            if (
                proposal_payload.get("target") != change["target"]
                or _binding_key(proposal_payload.get("proposal_binding", {}))
                != _binding_key(change["proposal_binding"])
                or _binding_key(authorization_payload.get("authorization_binding", {}))
                != _binding_key(change["authorization_binding"])
                or _binding_key(applied_payload.get("subject_after_binding", {}))
                != _binding_key(
                    rollback["failed_subject_binding"]
                    if rollback is not None
                    else observation["subject_after_binding"] or {}
                )
            ):
                errors.append("observation change bindings differ from recorded events / 观察包改变绑定与已记录事件不一致")
            recorded_validator_approval = authorization_payload.get(
                "validator_change_approval_binding"
            )
            if change["validator_change_approved"] is not (
                recorded_validator_approval is not None
            ):
                errors.append("validator approval flag differs from authorization event / 验证器审批标记与授权事件不一致")

        revalidation_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "revalidation_finished"
        ]
        if validation["status"] == "not_run":
            if revalidation_events:
                errors.append("not-run observation binds a completed revalidation / 未运行观察包却绑定了已完成复验")
        elif len(revalidation_events) != 1 or revalidation_events[0]["payload"] != validation:
            errors.append("observation validation differs from revalidation event / 观察包复验与复验事件不一致")

        rollback_started_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "rollback_started"
        ]
        rollback_applied_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "rollback_applied"
        ]
        rollback_verified_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "rollback_verified"
        ]
        if rollback is None:
            if rollback_started_events or rollback_applied_events or rollback_verified_events:
                errors.append("observation omitted a recorded rollback / 观察包遗漏已记录回滚")
        elif not (
            len(rollback_started_events)
            == len(rollback_applied_events)
            == len(rollback_verified_events)
            == 1
        ):
            errors.append("rollback observation lacks its full event chain / 回滚观察包缺少完整事件链")
        else:
            started_payload = rollback_started_events[0]["payload"]
            applied_payload = rollback_applied_events[0]["payload"]
            verified_payload = rollback_verified_events[0]["payload"]
            if (
                _binding_key(started_payload.get("rollback_binding", {}))
                != _binding_key(rollback["rollback_binding"])
                or _binding_key(started_payload.get("failed_subject_binding", {}))
                != _binding_key(rollback["failed_subject_binding"])
                or _binding_key(applied_payload.get("restored_subject_binding", {}))
                != _binding_key(rollback["restored_subject_binding"])
                or applied_payload.get("apply_evidence_bindings")
                != rollback["apply_evidence_bindings"]
                or verified_payload.get("validator_bindings")
                != rollback["validator_bindings"]
                or verified_payload.get("verification_evidence_bindings")
                != rollback["verification_evidence_bindings"]
                or verified_payload.get("verified") is not True
            ):
                errors.append("rollback record differs from its events / 回滚记录与对应事件不一致")

        finished_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "reflection_round_finished"
        ]
        if len(finished_events) != 1:
            errors.append("round must contain exactly one finish event / 轮次必须且只能包含一个结束事件")
        else:
            finish_payload = finished_events[0]["payload"]
            if (
                finish_payload.get("outcome") != observation["outcome"]
                or finish_payload.get("improvement_state")
                != observation["improvement_state"]
                or finish_payload.get("learning_candidate") != learning_candidate
            ):
                errors.append("observation closure differs from the finish event / 观察包闭环与结束事件不一致")

        learning_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "learning_promotion_evaluated"
        ]
        if learning_candidate is None:
            if learning_events:
                errors.append("learning event exists without a learning decision / 无学习决定却存在学习事件")
        elif len(learning_events) != 1 or learning_events[0]["payload"].get(
            "learning_candidate"
        ) != learning_candidate:
            errors.append("learning decision differs from its event / 学习决定与对应事件不一致")

        stop_events = [
            event
            for event in actual_round_events
            if event["event_type"] == "reflection_stopped"
        ]
        if terminal:
            if len(stop_events) != 1 or (
                stop_events[0]["payload"].get("outcome") != observation["outcome"]
                or stop_events[0]["payload"].get("stop_reason") != stop_reason
            ):
                errors.append("terminal observation differs from its stop event / 终态观察包与停止事件不一致")
        elif stop_events:
            errors.append("continuing round cannot bind a stop event / 继续轮次不得绑定停止事件")

    if errors:
        raise ReflectionValidationError(errors)


class ReflectionSession:
    """Deterministic coordinator for one sealed reflection contract / 单个封存反思契约的确定性协调器。"""

    def __init__(self, contract: Mapping[str, Any]) -> None:
        validate_reflection_contract(contract)
        self._contract = deepcopy(dict(contract))
        self._state = ReflectionState.CANDIDATE
        self._events: list[dict[str, Any]] = []
        self._observations: list[dict[str, Any]] = []
        self._round_ids: set[str] = set()
        self._round_count = 0
        self._no_result_progress_rounds = 0
        self._information_only_rounds = 0
        self._current: dict[str, Any] | None = None
        self._current_subject_binding = deepcopy(self._contract["subject_binding"])
        self._seen_subject_bindings = {_binding_key(self._current_subject_binding)}
        self._consumed_signal_bindings: set[tuple[Any, Any, Any]] = set()
        self._attribution = _initial_attribution()
        self._attribution_evidence_bindings: set[tuple[Any, Any, Any]] = set()

    @property
    def state(self) -> ReflectionState:
        return self._state

    @property
    def contract(self) -> dict[str, Any]:
        return deepcopy(self._contract)

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._events))

    @property
    def observations(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._observations))

    def _require_state(self, *states: ReflectionState) -> None:
        if self._state not in states:
            allowed = ", ".join(state.value for state in states)
            raise ReflectionStateError(
                f"state {self._state.value} does not allow this operation; expected {allowed}"
            )

    def _subject_binding(self) -> dict[str, Any]:
        return deepcopy(self._current_subject_binding)

    def _make_event(
        self,
        event_type: str,
        *,
        occurred_at: str,
        state_before: ReflectionState,
        state_after: ReflectionState,
        payload: Mapping[str, Any],
        round_id: str | None = None,
        offset: int = 0,
        subject_binding: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        sequence = len(self._events) + offset + 1
        event = {
            "schema_version": "1.0.0",
            "event_id": f"{self._contract['reflection_id']}:event:{sequence:04d}",
            "event_type": event_type,
            "reflection_id": self._contract["reflection_id"],
            "round_id": round_id,
            "sequence": sequence,
            "occurred_at": occurred_at,
            "idempotency_key": f"{self._contract['reflection_id']}:{event_type}:{sequence:04d}",
            "contract_binding": _contract_binding(self._contract),
            "subject_binding": deepcopy(
                dict(subject_binding)
                if subject_binding is not None
                else self._subject_binding()
            ),
            "state_before": state_before.value,
            "state_after": state_after.value,
            "route": self._contract["admission"]["route"],
            "payload": deepcopy(dict(payload)),
        }
        sealed = build_artifact("reflection_event", event)
        validate_reflection_event(sealed)
        return sealed

    def start(self, *, occurred_at: str) -> tuple[dict[str, Any], ...]:
        """Record admission evaluation and route selection / 记录准入评估与路由选择。"""

        self._require_state(ReflectionState.CANDIDATE)
        eligibility = ReflectionEligibility(self._contract["admission"]["eligibility"])
        target = (
            ReflectionState.ADMITTED
            if eligibility is ReflectionEligibility.ADMITTED
            else _NONADMITTED_STATE[eligibility]
        )
        pending = [
            self._make_event(
                "reflection_started",
                occurred_at=occurred_at,
                state_before=ReflectionState.CANDIDATE,
                state_after=ReflectionState.CANDIDATE,
                payload={"trigger_type": self._contract["trigger"]["trigger_type"]},
                offset=0,
            ),
            self._make_event(
                "reflection_eligibility_evaluated",
                occurred_at=occurred_at,
                state_before=ReflectionState.CANDIDATE,
                state_after=target,
                payload={
                    "eligibility": eligibility.value,
                    "reason_codes": self._contract["admission"]["reason_codes"],
                },
                offset=1,
            ),
            self._make_event(
                "reflection_routed",
                occurred_at=occurred_at,
                state_before=target,
                state_after=target,
                payload={"route": self._contract["admission"]["route"]},
                offset=2,
            ),
        ]
        self._events.extend(pending)
        self._state = target
        return tuple(deepcopy(pending))

    def close_without_round(
        self,
        *,
        outcome: ReflectionOutcome | str,
        reason: str,
        occurred_at: str,
    ) -> dict[str, Any]:
        """Close a non-admitted candidate with an explicit reason / 以明确原因关闭未准入候选。"""

        self._require_state(
            ReflectionState.NEEDS_EVIDENCE,
            ReflectionState.NOT_APPLICABLE,
            ReflectionState.BLOCKED,
            ReflectionState.HUMAN_REQUIRED,
        )
        normalized = ReflectionOutcome(outcome)
        if normalized not in {
            ReflectionOutcome.HANDED_OFF,
            ReflectionOutcome.REJECTED,
            ReflectionOutcome.ABORTED,
        }:
            raise ReflectionStateError("non-admitted reflection must hand off, reject, or abort")
        if normalized.value not in self._contract["stop_policy"]["terminal_outcomes"]:
            raise ReflectionAuthorizationError(
                "non-admitted terminal outcome is outside the sealed contract"
            )
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be a non-empty string")
        target = _OUTCOME_STATE[normalized]
        event = self._make_event(
            "reflection_stopped",
            occurred_at=occurred_at,
            state_before=self._state,
            state_after=target,
            payload={"outcome": normalized.value, "stop_reason": reason},
        )
        self._events.append(event)
        self._state = target
        return deepcopy(event)

    def freeze_baseline(self, *, occurred_at: str) -> dict[str, Any]:
        """Freeze the contract-owned comparison baseline / 冻结契约拥有的比较基线。"""

        self._require_state(ReflectionState.ADMITTED)
        event = self._make_event(
            "reflection_baseline_frozen",
            occurred_at=occurred_at,
            state_before=ReflectionState.ADMITTED,
            state_after=ReflectionState.BASELINE_FROZEN,
            payload={"baseline_binding": _baseline_binding(self._contract)},
        )
        self._events.append(event)
        self._state = ReflectionState.BASELINE_FROZEN
        return deepcopy(event)

    def start_round(
        self,
        *,
        round_id: str,
        new_signal: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Start one bounded round with an explicit signal state / 以显式信号状态启动一个有界轮次。"""

        self._require_state(ReflectionState.BASELINE_FROZEN, ReflectionState.ROUND_CLOSED)
        if not isinstance(round_id, str) or not round_id.strip() or round_id in self._round_ids:
            raise ValueError("round_id must be non-empty and unique")
        if self._round_count >= self._contract["stop_policy"]["max_rounds"]:
            raise ReflectionStateError("reflection round budget is exhausted")
        signal = _validate_new_signal_record(
            new_signal,
            self._contract,
            consumed_bindings=self._consumed_signal_bindings,
        )
        if not signal["qualified"] and self._contract["trigger"]["evidence_plan_binding"] is None:
            raise ReflectionValidationError(
                ["unqualified round requires an authorized evidence plan / 未获有效信号的轮次必须有已授权取证计划"]
            )

        round_number = self._round_count + 1
        prior_state = self._state
        current = {
            "round_id": round_id,
            "round_number": round_number,
            "new_signal": signal,
            "deviation": None,
            "attribution": deepcopy(self._attribution),
            "change": None,
            "change_proposal_count": 0,
            "rollback": None,
            "rollback_validation": None,
            "subject_before_binding": self._subject_binding(),
            "subject_after_binding": None,
            "validator_bindings": [],
            "event_start_index": len(self._events),
        }
        event = self._make_event(
            "reflection_round_started",
            occurred_at=occurred_at,
            state_before=prior_state,
            state_after=ReflectionState.ROUND_ACTIVE,
            payload={
                "round_number": round_number,
                "new_signal": signal,
                "baseline_binding": _baseline_binding(self._contract),
                "attribution_before": self._attribution,
            },
            round_id=round_id,
        )
        self._current = current
        self._events.append(event)
        if signal["qualified"]:
            self._consumed_signal_bindings |= _binding_set(
                signal["evidence_bindings"]
            )
        self._round_ids.add(round_id)
        self._round_count = round_number
        self._state = ReflectionState.ROUND_ACTIVE
        return deepcopy(event)

    def record_new_signal(
        self,
        *,
        new_signal: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Complete an evidence-only round with one qualified signal set / 用一组有效信号完成纯取证轮。"""

        self._require_state(ReflectionState.ROUND_ACTIVE)
        assert self._current is not None
        if self._current["new_signal"]["qualified"]:
            raise ReflectionStateError("the round already owns a qualified signal set")
        signal = _validate_new_signal_record(
            new_signal,
            self._contract,
            consumed_bindings=self._consumed_signal_bindings,
        )
        if not signal["qualified"]:
            raise ReflectionValidationError(
                ["recorded evidence must produce a qualified signal / 已记录取证结果必须形成有效信号"]
            )
        event = self._make_event(
            "reflection_signal_recorded",
            occurred_at=occurred_at,
            state_before=ReflectionState.ROUND_ACTIVE,
            state_after=ReflectionState.ROUND_ACTIVE,
            payload={"new_signal": signal},
            round_id=self._current["round_id"],
        )
        self._current["new_signal"] = signal
        self._consumed_signal_bindings |= _binding_set(signal["evidence_bindings"])
        self._events.append(event)
        return deepcopy(event)

    def record_deviation(
        self,
        *,
        code: str,
        evidence_bindings: Sequence[Mapping[str, Any]],
        details: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Record an observed deviation, not a root-cause claim / 记录观测偏差而非根因声明。"""

        self._require_state(ReflectionState.ROUND_ACTIVE)
        assert self._current is not None
        if self._current["deviation"] is not None:
            raise ReflectionStateError("a round can record only one governed deviation")
        if not isinstance(code, str) or not code.strip() or not evidence_bindings:
            raise ValueError("deviation requires a code and evidence bindings")
        deviation = {
            "code": code,
            "evidence_bindings": [deepcopy(dict(item)) for item in evidence_bindings],
            "details": deepcopy(dict(details)),
        }
        event = self._make_event(
            "deviation_detected",
            occurred_at=occurred_at,
            state_before=self._state,
            state_after=self._state,
            payload=deviation,
            round_id=self._current["round_id"],
        )
        self._current["deviation"] = deviation
        self._events.append(event)
        return deepcopy(event)

    def record_attribution_hypothesis(
        self,
        *,
        hypothesis: str,
        falsifier: str,
        confounders: Sequence[str],
        evidence_bindings: Sequence[Mapping[str, Any]] = (),
        evidence_authority_binding: Mapping[str, Any] | None = None,
        occurred_at: str,
    ) -> dict[str, Any]:
        """Record a falsifiable public attribution hypothesis / 记录可证伪的公开归因假设。"""

        self._require_state(
            ReflectionState.ROUND_ACTIVE,
            ReflectionState.REVALIDATING,
        )
        assert self._current is not None
        evidence = list(evidence_bindings)
        if not evidence:
            if self._current["deviation"] is not None:
                evidence = self._current["deviation"]["evidence_bindings"]
            else:
                evidence = self._current["new_signal"]["evidence_bindings"]
        return self.promote_attribution(
            state="hypothesis",
            hypothesis=hypothesis,
            falsifier=falsifier,
            confounders=confounders,
            evidence_bindings=evidence,
            evidence_authority_binding=evidence_authority_binding,
            occurred_at=occurred_at,
        )

    def promote_attribution(
        self,
        *,
        state: str,
        hypothesis: str,
        falsifier: str,
        confounders: Sequence[str],
        evidence_bindings: Sequence[Mapping[str, Any]],
        evidence_authority_binding: Mapping[str, Any] | None = None,
        occurred_at: str,
    ) -> dict[str, Any]:
        """Advance attribution exactly one level with never-reused evidence / 以不可复用证据将归因严格晋升一级。"""

        self._require_state(
            ReflectionState.ROUND_ACTIVE,
            ReflectionState.REVALIDATING,
            ReflectionState.ROLLBACK_VERIFIED,
        )
        assert self._current is not None
        current = self._current["attribution"]
        if state not in _ATTRIBUTION_RANK or state == "unattributed":
            raise ValueError("target attribution state is invalid")
        if _ATTRIBUTION_RANK[state] != _ATTRIBUTION_RANK[current["state"]] + 1:
            raise ReflectionValidationError(
                ["attribution must advance exactly one evidence level / 归因必须严格晋升一个证据等级"]
            )
        if state in {"controlled_replay", "intervention_verified"} and self._state is not ReflectionState.REVALIDATING:
            raise ReflectionStateError(
                "controlled attribution requires an active revalidation"
            )
        if not isinstance(hypothesis, str) or not hypothesis.strip() or not isinstance(
            falsifier, str
        ) or not falsifier.strip():
            raise ValueError("hypothesis and falsifier must be non-empty")
        normalized_confounders = list(confounders)
        if (
            any(not isinstance(item, str) or not item.strip() for item in normalized_confounders)
            or len(set(normalized_confounders)) != len(normalized_confounders)
        ):
            raise ValueError("confounders must be unique non-empty strings")
        if current["state"] != "unattributed" and any(
            (
                hypothesis != current["hypothesis"],
                falsifier != current["falsifier"],
                normalized_confounders != current["confounders"],
            )
        ):
            raise ReflectionValidationError(
                ["attribution promotion cannot replace its hypothesis / 归因晋升不得替换其假设"]
            )
        new_evidence = [deepcopy(dict(item)) for item in evidence_bindings]
        new_set = _binding_set(new_evidence)
        if not new_set or len(new_set) != len(new_evidence):
            raise ReflectionValidationError(
                ["attribution promotion requires unique new evidence / 归因晋升必须绑定唯一新增证据"]
            )
        if new_set & self._attribution_evidence_bindings:
            raise ReflectionValidationError(
                ["attribution evidence cannot be reused across promotions / 归因证据不得跨晋升重复使用"]
            )
        authority_field = _ATTRIBUTION_AUTHORITY_FIELD[state]
        allowed_authorities = self._contract["attribution_policy"][authority_field]
        if evidence_authority_binding is None:
            if len(allowed_authorities) != 1:
                raise ReflectionAuthorizationError(
                    "attribution evidence authority must be selected explicitly"
                )
            authority = deepcopy(allowed_authorities[0])
        else:
            authority = deepcopy(dict(evidence_authority_binding))
        if _binding_key(authority) not in _binding_set(allowed_authorities):
            raise ReflectionAuthorizationError(
                "attribution evidence authority is outside the sealed contract"
            )
        attribution = {
            "state": state,
            "hypothesis": hypothesis,
            "falsifier": falsifier,
            "confounders": normalized_confounders,
            "evidence_kind": _ATTRIBUTION_EVIDENCE_KIND[state],
            "evidence_authority_binding": authority,
            "evidence_bindings": deepcopy(current["evidence_bindings"]) + new_evidence,
        }
        payload = deepcopy(attribution)
        payload["new_evidence_bindings"] = new_evidence
        event = self._make_event(
            "attribution_evidence_recorded",
            occurred_at=occurred_at,
            state_before=self._state,
            state_after=self._state,
            payload=payload,
            round_id=self._current["round_id"],
        )
        self._current["attribution"] = attribution
        self._attribution_evidence_bindings |= new_set
        self._events.append(event)
        return deepcopy(event)

    def propose_change(
        self,
        *,
        target: str,
        proposal_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Propose one scoped change; proposal is not authorization / 提议一个受限改变；提议不等于授权。"""

        self._require_state(ReflectionState.ROUND_ACTIVE)
        assert self._current is not None
        if self._current["change_proposal_count"] >= self._contract["change_policy"][
            "max_changes_per_round"
        ]:
            raise ReflectionStateError("the per-round change budget is exhausted")
        signal = self._current["new_signal"]
        if not signal["qualified"]:
            raise ReflectionStateError("a change requires a qualified new signal")
        policy = self._contract["change_policy"]
        if target not in policy["allowed_targets"] or target in policy["forbidden_targets"]:
            raise ReflectionAuthorizationError(f"change target is outside contract: {target}")
        if target == "validator" and policy["verifier_change_policy"] == "forbidden":
            raise ReflectionAuthorizationError("validator changes are forbidden")
        change = {
            "target": target,
            "proposal_binding": deepcopy(dict(proposal_binding)),
            "authorization_binding": None,
            "applied": False,
            "validator_changed": target == "validator",
            "validator_change_approved": False,
        }
        event = self._make_event(
            "change_proposed",
            occurred_at=occurred_at,
            state_before=ReflectionState.ROUND_ACTIVE,
            state_after=ReflectionState.CHANGE_PROPOSED,
            payload={"target": target, "proposal_binding": proposal_binding},
            round_id=self._current["round_id"],
        )
        self._current["change"] = change
        self._current["change_proposal_count"] += 1
        self._events.append(event)
        self._state = ReflectionState.CHANGE_PROPOSED
        return deepcopy(event)

    def reject_change(self, *, reason: str, occurred_at: str) -> dict[str, Any]:
        """Reject a proposal and return to evidence work / 拒绝提案并返回证据工作。"""

        self._require_state(ReflectionState.CHANGE_PROPOSED)
        assert self._current is not None
        if not reason.strip():
            raise ValueError("reason must be non-empty")
        event = self._make_event(
            "change_rejected",
            occurred_at=occurred_at,
            state_before=ReflectionState.CHANGE_PROPOSED,
            state_after=ReflectionState.ROUND_ACTIVE,
            payload={"reason": reason},
            round_id=self._current["round_id"],
        )
        self._current["change"] = None
        self._events.append(event)
        self._state = ReflectionState.ROUND_ACTIVE
        return deepcopy(event)

    def authorize_change(
        self,
        *,
        authorization_binding: Mapping[str, Any],
        validator_change_approval_binding: Mapping[str, Any] | None = None,
        occurred_at: str,
    ) -> dict[str, Any]:
        """Bind exact general and, when needed, validator authorization / 绑定精确的一般授权与必要的验证器独立审批。"""

        self._require_state(ReflectionState.CHANGE_PROPOSED)
        assert self._current is not None and self._current["change"] is not None
        expected = self._contract["change_policy"]["authorizer_binding"]
        if _binding_key(authorization_binding) != _binding_key(expected):
            raise ReflectionAuthorizationError("change authorization binding mismatch")
        change = self._current["change"]
        if change["validator_changed"]:
            expected_validator = self._contract["validation_policy"][
                "validator_change_authorizer_binding"
            ]
            if (
                expected_validator is None
                or validator_change_approval_binding is None
                or _binding_key(validator_change_approval_binding)
                != _binding_key(expected_validator)
                or _binding_key(validator_change_approval_binding)
                == _binding_key(authorization_binding)
            ):
                raise ReflectionAuthorizationError(
                    "validator change requires a distinct independent approval binding"
                )
            change["validator_change_approved"] = True
        elif validator_change_approval_binding is not None:
            raise ReflectionAuthorizationError(
                "validator approval cannot be supplied for a non-validator change"
            )
        change["authorization_binding"] = deepcopy(dict(authorization_binding))
        event = self._make_event(
            "change_authorized",
            occurred_at=occurred_at,
            state_before=ReflectionState.CHANGE_PROPOSED,
            state_after=ReflectionState.CHANGE_AUTHORIZED,
            payload={
                "authorization_binding": authorization_binding,
                "validator_change_approval_binding": validator_change_approval_binding,
            },
            round_id=self._current["round_id"],
        )
        self._events.append(event)
        self._state = ReflectionState.CHANGE_AUTHORIZED
        return deepcopy(event)

    def record_change_applied(
        self,
        *,
        subject_after_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Record externally applied change and its exact new version / 记录外部已应用改变及其精确新版本。"""

        self._require_state(ReflectionState.CHANGE_AUTHORIZED)
        assert self._current is not None and self._current["change"] is not None
        subject_key = _binding_key(subject_after_binding)
        if subject_key in self._seen_subject_bindings:
            raise ReflectionValidationError(
                ["applied change must produce a new, never-reused subject binding / 已应用改变必须产生从未使用的新对象绑定"]
            )
        normalized_subject = deepcopy(dict(subject_after_binding))
        event = self._make_event(
            "change_applied",
            occurred_at=occurred_at,
            state_before=ReflectionState.CHANGE_AUTHORIZED,
            state_after=ReflectionState.CHANGE_APPLIED,
            payload={"subject_after_binding": subject_after_binding},
            round_id=self._current["round_id"],
            subject_binding=normalized_subject,
        )
        self._current["change"]["applied"] = True
        self._current["subject_after_binding"] = normalized_subject
        self._current_subject_binding = deepcopy(normalized_subject)
        self._seen_subject_bindings.add(subject_key)
        self._events.append(event)
        self._state = ReflectionState.CHANGE_APPLIED
        return deepcopy(event)

    def start_revalidation(
        self,
        *,
        validator_bindings: Sequence[Mapping[str, Any]],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Start independent validation against mandatory and regression sets / 启动覆盖必选与回归集合的独立复验。"""

        self._require_state(ReflectionState.CHANGE_APPLIED)
        assert self._current is not None
        supplied = [deepcopy(dict(item)) for item in validator_bindings]
        supplied_set = _binding_set(supplied)
        policy = self._contract["validation_policy"]
        required = _binding_set(policy["mandatory_validator_bindings"]) | _binding_set(
            policy["regression_validator_bindings"]
        )
        if not required.issubset(supplied_set):
            raise ReflectionValidationError(
                ["revalidation omits mandatory or regression validators / 复验遗漏必选或回归验证器"]
            )
        if len(supplied_set) != len(supplied):
            raise ValueError("validator_bindings cannot contain duplicates")
        self._current["validator_bindings"] = supplied
        event = self._make_event(
            "revalidation_started",
            occurred_at=occurred_at,
            state_before=ReflectionState.CHANGE_APPLIED,
            state_after=ReflectionState.REVALIDATING,
            payload={
                "candidate_binding": self._current["subject_after_binding"],
                "validator_bindings": supplied,
            },
            round_id=self._current["round_id"],
        )
        self._events.append(event)
        self._state = ReflectionState.REVALIDATING
        return deepcopy(event)

    def record_rollback(
        self,
        *,
        restored_subject_binding: Mapping[str, Any],
        apply_evidence_bindings: Sequence[Mapping[str, Any]],
        validator_bindings: Sequence[Mapping[str, Any]],
        verification_evidence_bindings: Sequence[Mapping[str, Any]],
        occurred_at: str,
        failed_validation: Mapping[str, Any] | None = None,
    ) -> tuple[dict[str, Any], ...]:
        """Record a contract-bound applied and verified rollback / 记录契约绑定、已应用且已验证的回滚。"""

        self._require_state(ReflectionState.CHANGE_APPLIED, ReflectionState.REVALIDATING)
        assert self._current is not None and self._current["change"] is not None
        if not self._current["change"]["applied"]:
            raise ReflectionStateError("rollback requires an applied change")
        if _binding_key(restored_subject_binding) != _binding_key(
            self._current["subject_before_binding"]
        ):
            raise ReflectionValidationError(
                ["rollback must restore the round's before-subject / 回滚必须恢复本轮改变前对象"]
            )
        apply_evidence = [deepcopy(dict(item)) for item in apply_evidence_bindings]
        verification_evidence = [
            deepcopy(dict(item)) for item in verification_evidence_bindings
        ]
        validators = [deepcopy(dict(item)) for item in validator_bindings]
        if (
            not apply_evidence
            or len(_binding_set(apply_evidence)) != len(apply_evidence)
            or not verification_evidence
            or len(_binding_set(verification_evidence)) != len(verification_evidence)
        ):
            raise ReflectionValidationError(
                ["rollback apply and verification require unique evidence / 回滚应用与验证必须绑定唯一证据"]
            )
        required_validators = _binding_set(
            self._contract["validation_policy"]["mandatory_validator_bindings"]
        ) | _binding_set(
            self._contract["validation_policy"]["regression_validator_bindings"]
        )
        if not required_validators.issubset(_binding_set(validators)):
            raise ReflectionValidationError(
                ["rollback verification omits contract validators / 回滚验证遗漏契约验证器"]
            )

        validation_record: dict[str, Any] | None = None
        pending: list[dict[str, Any]] = []
        initial_state = self._state
        if initial_state is ReflectionState.REVALIDATING:
            if failed_validation is None:
                raise ReflectionValidationError(
                    ["rollback after revalidation requires its failed result / 复验后回滚必须记录失败结果"]
                )
            validation_record = deepcopy(dict(failed_validation))
            if set(validation_record) != _VALIDATION_FIELDS or validation_record[
                "status"
            ] not in {"failed", "unknown"}:
                raise ReflectionValidationError(
                    ["rollback requires a failed or unknown revalidation record / 回滚要求失败或未知复验记录"]
                )
            if _binding_key(validation_record["candidate_binding"] or {}) != _binding_key(
                self._current["subject_after_binding"]
            ):
                raise ReflectionValidationError(
                    ["rollback validation candidate differs from failed subject / 回滚复验候选与失败对象不一致"]
                )
            validation_errors = _contract_bound_validation_errors(
                validation_record,
                self._contract,
                new_signal=self._current["new_signal"],
                subject_before_binding=self._current["subject_before_binding"],
                candidate_binding=self._current["subject_after_binding"],
                started_validator_bindings=self._current["validator_bindings"],
                validator_changed=bool(
                    self._current["change"]["validator_changed"]
                ),
            )
            if validation_errors:
                raise ReflectionValidationError(validation_errors)
            pending.append(
                self._make_event(
                    "revalidation_finished",
                    occurred_at=occurred_at,
                    state_before=ReflectionState.REVALIDATING,
                    state_after=ReflectionState.REVALIDATING,
                    payload=validation_record,
                    round_id=self._current["round_id"],
                    offset=len(pending),
                )
            )
        elif failed_validation is not None:
            raise ReflectionStateError(
                "failed_validation requires an active revalidation"
            )

        failed_subject = deepcopy(self._current["subject_after_binding"])
        restored_subject = deepcopy(dict(restored_subject_binding))
        rollback_record = {
            "rollback_binding": deepcopy(
                self._contract["stop_policy"]["rollback_binding"]
            ),
            "failed_subject_binding": failed_subject,
            "restored_subject_binding": restored_subject,
            "apply_evidence_bindings": apply_evidence,
            "validator_bindings": validators,
            "verification_evidence_bindings": verification_evidence,
            "verified": True,
        }
        pending.append(
            self._make_event(
                "rollback_started",
                occurred_at=occurred_at,
                state_before=initial_state,
                state_after=ReflectionState.ROLLING_BACK,
                payload={
                    "rollback_binding": rollback_record["rollback_binding"],
                    "failed_subject_binding": failed_subject,
                    "restored_subject_binding": restored_subject,
                },
                round_id=self._current["round_id"],
                offset=len(pending),
            )
        )
        pending.append(
            self._make_event(
                "rollback_applied",
                occurred_at=occurred_at,
                state_before=ReflectionState.ROLLING_BACK,
                state_after=ReflectionState.ROLLBACK_APPLIED,
                payload={
                    "restored_subject_binding": restored_subject,
                    "apply_evidence_bindings": apply_evidence,
                },
                round_id=self._current["round_id"],
                offset=len(pending),
                subject_binding=restored_subject,
            )
        )
        pending.append(
            self._make_event(
                "rollback_verified",
                occurred_at=occurred_at,
                state_before=ReflectionState.ROLLBACK_APPLIED,
                state_after=ReflectionState.ROLLBACK_VERIFIED,
                payload={
                    "restored_subject_binding": restored_subject,
                    "validator_bindings": validators,
                    "verification_evidence_bindings": verification_evidence,
                    "verified": True,
                },
                round_id=self._current["round_id"],
                offset=len(pending),
                subject_binding=restored_subject,
            )
        )
        self._events.extend(pending)
        self._current["rollback"] = rollback_record
        self._current["rollback_validation"] = validation_record
        self._current["subject_after_binding"] = restored_subject
        self._current_subject_binding = deepcopy(restored_subject)
        self._state = ReflectionState.ROLLBACK_VERIFIED
        return tuple(deepcopy(pending))

    def close_round(
        self,
        *,
        outcome: ReflectionOutcome | str,
        validation: Mapping[str, Any],
        improvement_state: ReflectionImprovementState | str,
        attribution: Mapping[str, Any] | None,
        occurred_at: str,
        stop_reason: str | None = None,
        learning_candidate: Mapping[str, Any] | None = None,
        observation_id: str | None = None,
    ) -> dict[str, Any]:
        """Close a round only after semantic gates pass / 仅在语义闸门通过后关闭轮次。"""

        self._require_state(
            ReflectionState.ROUND_ACTIVE,
            ReflectionState.REVALIDATING,
            ReflectionState.ROLLBACK_VERIFIED,
        )
        assert self._current is not None
        normalized_outcome = ReflectionOutcome(outcome)
        normalized_improvement = ReflectionImprovementState(improvement_state)
        target_state = _OUTCOME_STATE[normalized_outcome]
        if (
            normalized_outcome is not ReflectionOutcome.CONTINUE
            and normalized_outcome.value
            not in self._contract["stop_policy"]["terminal_outcomes"]
        ):
            raise ReflectionAuthorizationError(
                "terminal outcome is outside the sealed contract"
            )
        if normalized_outcome is ReflectionOutcome.CONTINUE:
            if stop_reason is not None:
                raise ValueError("a continuing round cannot carry a stop reason")
        elif not isinstance(stop_reason, str) or not stop_reason.strip():
            raise ValueError("a terminal round requires a non-empty stop reason")
        validation_record = deepcopy(dict(validation))
        if set(validation_record) != _VALIDATION_FIELDS:
            raise ValueError(
                f"validation fields must equal {sorted(_VALIDATION_FIELDS)}"
            )
        if self._state is ReflectionState.ROLLBACK_VERIFIED:
            if normalized_outcome is not ReflectionOutcome.ROLLED_BACK:
                raise ReflectionStateError(
                    "a verified rollback must close as rolled_back"
                )
            expected_validation = self._current["rollback_validation"]
            if expected_validation is None:
                if validation_record["status"] != "not_run":
                    raise ReflectionStateError(
                        "rollback without revalidation must close with not_run validation"
                    )
            elif validation_record != expected_validation:
                raise ReflectionValidationError(
                    ["rollback close validation differs from its recorded result / 回滚关闭复验与已记录结果不一致"]
                )
        elif normalized_outcome is ReflectionOutcome.ROLLED_BACK:
            raise ReflectionStateError(
                "rolled_back requires record_rollback and verified recovery"
            )
        elif self._state is ReflectionState.REVALIDATING:
            if validation_record["status"] == "not_run":
                raise ReflectionValidationError(["started revalidation cannot close as not_run / 已启动复验不得以未运行关闭"])
            if _binding_key(validation_record["candidate_binding"] or {}) != _binding_key(
                self._current["subject_after_binding"]
            ):
                raise ReflectionValidationError(["validation candidate binding mismatch / 复验候选绑定不匹配"])
            if not _binding_set(self._current["validator_bindings"]).issubset(
                _binding_set(validation_record["validator_bindings"])
            ):
                raise ReflectionValidationError(["validation result omits started validators / 复验结果遗漏已启动验证器"])
        elif validation_record["status"] != "not_run":
            raise ReflectionStateError("validation results require start_revalidation")

        current_attribution = deepcopy(self._current["attribution"])
        attribution_record = deepcopy(
            dict(attribution) if attribution is not None else current_attribution
        )
        if attribution_record != current_attribution:
            raise ReflectionValidationError(
                ["attribution changes must be recorded as evidence events / 归因改变必须先记录为证据事件"]
            )
        if _ATTRIBUTION_RANK[attribution_record["state"]] >= 3 and validation_record[
            "comparison_state"
        ] not in {
            "comparable",
            "independently_rebased",
        }:
            raise ReflectionValidationError(["controlled attribution requires comparable validation / 受控归因要求复验可比"])
        learning_record = _validate_learning_candidate(
            learning_candidate,
            self._contract,
            outcome=normalized_outcome,
            round_id=self._current["round_id"],
            source_subject_binding=self._current["subject_after_binding"],
            available_round_evidence=(
                _binding_set(self._current["new_signal"]["evidence_bindings"])
                | _binding_set(validation_record["evidence_bindings"])
                | (
                    _binding_set(self._current["deviation"]["evidence_bindings"])
                    if self._current["deviation"] is not None
                    else set()
                )
            ),
        )
        event_state = self._state
        pending: list[dict[str, Any]] = []
        if self._state is ReflectionState.REVALIDATING:
            pending.append(
                self._make_event(
                    "revalidation_finished",
                    occurred_at=occurred_at,
                    state_before=ReflectionState.REVALIDATING,
                    state_after=ReflectionState.REVALIDATING,
                    payload=validation_record,
                    round_id=self._current["round_id"],
                    offset=len(pending),
                )
            )
        pending.append(
            self._make_event(
                "reflection_round_finished",
                occurred_at=occurred_at,
                state_before=event_state,
                state_after=target_state,
                payload={
                    "outcome": normalized_outcome.value,
                    "improvement_state": normalized_improvement.value,
                    "learning_candidate": learning_record,
                },
                round_id=self._current["round_id"],
                offset=len(pending),
            )
        )
        if learning_record is not None:
            pending.append(
                self._make_event(
                    "learning_promotion_evaluated",
                    occurred_at=occurred_at,
                    state_before=target_state,
                    state_after=target_state,
                    payload={"learning_candidate": learning_record},
                    round_id=self._current["round_id"],
                    offset=len(pending),
                )
            )
        if normalized_outcome is not ReflectionOutcome.CONTINUE:
            pending.append(
                self._make_event(
                    "reflection_stopped",
                    occurred_at=occurred_at,
                    state_before=target_state,
                    state_after=target_state,
                    payload={
                        "outcome": normalized_outcome.value,
                        "stop_reason": stop_reason,
                    },
                    round_id=self._current["round_id"],
                    offset=len(pending),
                )
            )

        round_events = self._events[self._current["event_start_index"] :] + pending
        full_events = self._events + pending
        observation = {
            "schema_version": "1.0.0",
            "observation_id": observation_id
            or f"{self._contract['reflection_id']}:observation:{self._current['round_number']:04d}",
            "reflection_id": self._contract["reflection_id"],
            "round_id": self._current["round_id"],
            "round_number": self._current["round_number"],
            "contract_binding": _contract_binding(self._contract),
            "route": self._contract["admission"]["route"],
            "subject_before_binding": deepcopy(
                self._current["subject_before_binding"]
            ),
            "subject_after_binding": deepcopy(
                self._current["subject_after_binding"]
            ),
            "baseline_binding": _baseline_binding(self._contract),
            "new_signal": deepcopy(self._current["new_signal"]),
            "deviation": deepcopy(self._current["deviation"]),
            "change": deepcopy(self._current["change"]),
            "validation": validation_record,
            "improvement_state": normalized_improvement.value,
            "attribution": attribution_record,
            "rollback": deepcopy(self._current["rollback"]),
            "learning_candidate": learning_record,
            "outcome": normalized_outcome.value,
            "terminal": normalized_outcome is not ReflectionOutcome.CONTINUE,
            "stop_reason": stop_reason,
            "event_bindings": [_event_binding(event) for event in round_events],
            "created_at": occurred_at,
        }
        sealed = build_artifact("reflection_round_observation", observation)
        validate_reflection_round_observation(
            sealed,
            contract=self._contract,
            events=full_events,
        )

        result_progress = bool(validation_record["result_progress"])
        information_progress = bool(validation_record["information_progress"])
        prospective_no_result = (
            0 if result_progress else self._no_result_progress_rounds + 1
        )
        prospective_information_only = self._information_only_rounds + int(
            information_progress and not result_progress
        )
        if normalized_outcome is ReflectionOutcome.CONTINUE:
            if prospective_no_result > self._contract["stop_policy"][
                "max_no_result_progress_rounds"
            ]:
                raise ReflectionStateError("no-result-progress budget is exhausted")
            if prospective_information_only > self._contract["signal_policy"][
                "max_information_only_rounds"
            ]:
                raise ReflectionStateError("information-only round budget is exhausted")
            if self._round_count >= self._contract["stop_policy"]["max_rounds"]:
                raise ReflectionStateError("cannot continue beyond the final allowed round")

        self._events.extend(pending)
        self._observations.append(sealed)
        self._no_result_progress_rounds = prospective_no_result
        self._information_only_rounds = prospective_information_only
        self._attribution = deepcopy(attribution_record)
        self._state = target_state
        self._current = None
        return deepcopy(sealed)


__all__ = [
    "GENERATOR_CRITIC_PROBES",
    "REFLECTION_ATTRIBUTION_PROBE",
    "REFLECTION_CORE_PROBES",
    "REFLECTION_LEARNING_PROBE",
    "SKILL_PACKAGE_PROBES",
    "ReflectionAuthorizationError",
    "ReflectionEligibility",
    "ReflectionImprovementState",
    "ReflectionOutcome",
    "ReflectionRoute",
    "ReflectionRuntimeError",
    "ReflectionSession",
    "ReflectionState",
    "ReflectionStateError",
    "ReflectionValidationError",
    "build_reflection_contract",
    "resolve_reflection_required_probes",
    "validate_reflection_contract",
    "validate_reflection_event",
    "validate_reflection_event_stream",
    "validate_reflection_round_observation",
]
