"""Exact-version Generator-Critic runtime / 精确版本生成评审运行时。

The coordinator records public artifacts and deterministic policy transitions.
It does not generate content, invent evidence, execute a repair, or grant a
release permission. / 本协调器记录公开制品与确定性策略转换；它不生成内容、
不虚构证据、不执行修订，也不授予发布权限。
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from enum import Enum
import re
from typing import Any, Callable, Mapping, Sequence

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


GENERATOR_CRITIC_PROBES = (
    "PROBE_0024",
    "PROBE_0025",
    "PROBE_0026",
    "PROBE_0027",
)

GENERATOR_CRITIC_SHARED_GUARD_REQUIREMENTS = {
    "initial_artifact": ("reflection_admitted", "baseline_frozen"),
    "revision": ("change_authorized",),
    "superseding_revision": ("change_authorized",),
    "receipt": ("independent_revalidation_passed", "round_closed"),
    "release": ("independent_revalidation_current", "acceptance_current"),
}

_SEMANTIC_VERSION = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$"
)
_SHA256 = re.compile(r"^sha256:[a-f0-9]{64}$")


class GeneratorCriticRuntimeError(RuntimeError):
    """Base Generator-Critic error / 生成评审错误基类。"""


class GeneratorCriticValidationError(GeneratorCriticRuntimeError):
    """A public artifact violates review semantics / 公开制品违反评审语义。"""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


class GeneratorCriticStateError(GeneratorCriticRuntimeError):
    """An operation is illegal in the current state / 操作在当前状态非法。"""


class GeneratorCriticAuthorizationError(GeneratorCriticRuntimeError):
    """An actor binding does not match the sealed authority / 主体绑定不匹配封存权限。"""


class GeneratorCriticReleaseError(GeneratorCriticRuntimeError):
    """The exact-version release gate failed / 精确版本发布门禁失败。"""


class GeneratorCriticState(str, Enum):
    """Authoritative Generator-Critic state / 权威生成评审状态。"""

    INITIALIZED = "initialized"
    ARTIFACT_UNREVIEWED = "artifact_unreviewed"
    REVIEWING = "reviewing"
    REVIEWED = "reviewed"
    NEEDS_REVISION = "needs_revision"
    ACCEPTED = "accepted"
    WAITING_EVIDENCE = "waiting_evidence"
    HUMAN_REQUIRED = "human_required"
    REJECTED = "rejected"
    RELEASED = "released"
    STOPPED = "stopped"


class GeneratorCriticDecision(str, Enum):
    """Policy decision for one reviewed revision / 单个已审修订的策略裁决。"""

    ACCEPT = "accept"
    NEEDS_REVISION = "needs_revision"
    REJECT = "reject"
    HUMAN_REQUIRED = "human_required"
    WAIT_FOR_EVIDENCE = "wait_for_evidence"


_DECISION_STATE = {
    GeneratorCriticDecision.ACCEPT: GeneratorCriticState.ACCEPTED,
    GeneratorCriticDecision.NEEDS_REVISION: GeneratorCriticState.NEEDS_REVISION,
    GeneratorCriticDecision.REJECT: GeneratorCriticState.REJECTED,
    GeneratorCriticDecision.HUMAN_REQUIRED: GeneratorCriticState.HUMAN_REQUIRED,
    GeneratorCriticDecision.WAIT_FOR_EVIDENCE: GeneratorCriticState.WAITING_EVIDENCE,
}


def _binding_key(binding: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return binding.get("id"), binding.get("version"), binding.get("hash")


def _binding_set(bindings: Sequence[Mapping[str, Any]]) -> set[tuple[Any, Any, Any]]:
    return {_binding_key(binding) for binding in bindings}


def _parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise GeneratorCriticValidationError(
            [f"invalid date-time {value!r} / 无效日期时间 {value!r}"]
        ) from exc
    if parsed.tzinfo is None:
        raise GeneratorCriticValidationError(
            [f"date-time must include a timezone: {value!r} / 日期时间必须包含时区: {value!r}"]
        )
    return parsed.astimezone(timezone.utc)


def _format_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _contract_binding(contract: Mapping[str, Any]) -> dict[str, str]:
    return {
        "id": str(contract["contract_id"]),
        "version": str(contract["contract_version"]),
        "hash": str(contract["contract_hash"]),
    }


def artifact_binding(artifact: Mapping[str, Any]) -> dict[str, Any]:
    """Return the exact immutable artifact binding / 返回精确不可变工件绑定。"""

    return {
        "artifact_id": artifact["artifact_id"],
        "revision": artifact["revision"],
        "artifact_digest": artifact["artifact_digest"],
        "artifact_record_hash": artifact["artifact_record_hash"],
    }


def reflection_subject_binding_for_artifact(
    artifact: Mapping[str, Any],
) -> dict[str, str]:
    """Map one exact Generator-Critic artifact to the shared reflection subject. / 将精确生成评审工件映射为共享反思对象。"""

    required = {"artifact_id", "revision", "artifact_record_hash"}
    if not required.issubset(artifact):
        raise GeneratorCriticValidationError(
            ["artifact binding is incomplete for reflection mapping / 工件绑定不足以映射反思对象"]
        )
    revision = artifact["revision"]
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        raise GeneratorCriticValidationError(
            ["artifact revision is invalid for reflection mapping / 工件修订号无法映射反思对象"]
        )
    record_hash = artifact["artifact_record_hash"]
    if not isinstance(record_hash, str) or _SHA256.fullmatch(record_hash) is None:
        raise GeneratorCriticValidationError(
            ["artifact record hash is invalid for reflection mapping / 工件记录哈希无法映射反思对象"]
        )
    return {
        "id": str(artifact["artifact_id"]),
        "version": f"0.0.{revision}",
        "hash": record_hash,
    }


def build_shared_reflection_guard(
    reflection_contract: Mapping[str, Any],
    *,
    events_provider: Callable[[], Sequence[Mapping[str, Any]]],
    observations_provider: Callable[[], Sequence[Mapping[str, Any]]],
) -> Callable[[str, Mapping[str, Any]], Mapping[str, Any]]:
    """Build a guard that validates the real shared reflection history. / 构建校验真实共享反思历史的闸。"""

    try:  # Lazy import avoids the reflection-runtime constant import cycle. / 延迟导入避免常量循环依赖。
        from .reflection_runtime import (
            validate_reflection_contract,
            validate_reflection_event_stream,
            validate_reflection_round_observation,
        )
    except ImportError:
        from reflection_runtime import (  # type: ignore[no-redef]
            validate_reflection_contract,
            validate_reflection_event_stream,
            validate_reflection_round_observation,
        )

    contract = deepcopy(dict(reflection_contract))
    validate_reflection_contract(contract)
    if contract["admission"]["eligibility"] != "admitted":
        raise GeneratorCriticAuthorizationError(
            "shared reflection contract is not admitted / 共享反思契约未准入"
        )
    if contract["admission"]["route"] != "generator_critic":
        raise GeneratorCriticAuthorizationError(
            "shared reflection route is not generator_critic / 共享反思路由不是 generator_critic"
        )
    expected_contract_binding = {
        "id": str(contract["contract_id"]),
        "version": str(contract["contract_version"]),
        "hash": str(contract["contract_hash"]),
    }

    def guard(stage: str, request: Mapping[str, Any]) -> Mapping[str, Any]:
        if stage not in GENERATOR_CRITIC_SHARED_GUARD_REQUIREMENTS:
            raise GeneratorCriticAuthorizationError(
                f"unknown shared reflection guard stage: {stage} / 未知共享反思闸阶段: {stage}"
            )
        if request.get("reflection_contract_binding") != expected_contract_binding:
            raise GeneratorCriticAuthorizationError(
                "Generator-Critic binds a different reflection contract / 生成评审绑定了不同反思契约"
            )
        events = [deepcopy(dict(item)) for item in events_provider()]
        observations = [deepcopy(dict(item)) for item in observations_provider()]
        validate_reflection_event_stream(events, contract=contract)
        round_numbers = [item.get("round_number") for item in observations]
        if (
            any(not isinstance(item, int) or isinstance(item, bool) for item in round_numbers)
            or round_numbers != sorted(round_numbers)
            or len(round_numbers) != len(set(round_numbers))
        ):
            raise GeneratorCriticAuthorizationError(
                "shared reflection observations must be unique and ordered / 共享反思观察包必须唯一且有序"
            )
        for observation in observations:
            validate_reflection_round_observation(
                observation,
                contract=contract,
                events=events,
            )
        artifact = request.get("artifact_binding")
        if not isinstance(artifact, Mapping):
            raise GeneratorCriticAuthorizationError(
                "shared reflection request lacks the exact artifact / 共享反思请求缺少精确工件"
            )
        subject_binding = reflection_subject_binding_for_artifact(artifact)
        context = request.get("context")
        context = context if isinstance(context, Mapping) else {}

        if stage == "initial_artifact":
            if not any(event["event_type"] == "reflection_baseline_frozen" for event in events):
                raise GeneratorCriticAuthorizationError(
                    "initial artifact requires admitted frozen baseline / 初始工件要求已准入且冻结基线"
                )
        elif stage in {"revision", "superseding_revision"}:
            if events[-1]["event_type"] != "change_authorized":
                raise GeneratorCriticAuthorizationError(
                    "revision requires a current unconsumed change authorization / 修订要求当前未消费改变授权"
                )
            round_id = events[-1]["round_id"]
            proposal_events = [
                event
                for event in events
                if event["round_id"] == round_id
                and event["event_type"] == "change_proposed"
            ]
            expected_proposal = context.get("change_proposal_binding")
            if (
                not proposal_events
                or not isinstance(expected_proposal, Mapping)
                or proposal_events[-1]["payload"].get("proposal_binding")
                != dict(expected_proposal)
            ):
                raise GeneratorCriticAuthorizationError(
                    "revision does not match the authorized shared change proposal / 修订不匹配共享已授权改变提案"
                )
        else:
            if not observations:
                raise GeneratorCriticAuthorizationError(
                    "receipt or release requires a validated round observation / 回执或发布要求已校验轮次观察"
                )
            latest = observations[-1]
            validation = latest["validation"]
            if (
                latest["outcome"] != "accepted"
                or latest["terminal"] is not True
                or latest["subject_after_binding"] != subject_binding
                or validation["status"] != "passed"
                or validation["mandatory_pass"] is not True
                or validation["regression_pass"] is not True
                or validation["candidate_binding"] != subject_binding
            ):
                raise GeneratorCriticAuthorizationError(
                    "shared reflection does not accept and revalidate the exact artifact / 共享反思未接受并复验精确工件"
                )

        assurance_material = {
            "stage": stage,
            "request": deepcopy(dict(request)),
            "reflection_contract_hash": contract["contract_hash"],
            "event_tail_hash": events[-1]["event_hash"],
            "observation_hashes": [item["observation_hash"] for item in observations],
            "subject_binding": subject_binding,
        }
        return {
            "id": f"{contract['reflection_id']}:generator-critic:{stage}:{artifact['revision']}",
            "version": "1.0.0",
            "hash": artifact_fingerprint(assurance_material),
        }

    return guard


def _record_binding(
    record: Mapping[str, Any], *, identifier_field: str, hash_field: str
) -> dict[str, str]:
    return {
        "id": str(record[identifier_field]),
        "version": "1.0.0",
        "hash": str(record[hash_field]),
    }


def _same_binding(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return dict(left) == dict(right)


def build_generator_critic_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Seal and validate one Generator-Critic contract / 封存并校验生成评审契约。"""

    sealed = build_artifact("generator_critic_contract", contract)
    validate_generator_critic_contract(sealed)
    return sealed


def validate_generator_critic_contract(contract: Mapping[str, Any]) -> None:
    """Validate contract shape and cross-role invariants / 校验契约结构与跨角色不变量。"""

    validate_schema("generator_critic_contract", contract)
    validate_artifact_hash("generator_critic_contract", contract)
    errors: list[str] = []

    criteria = contract["criteria"]
    criterion_ids = [item["criterion_id"] for item in criteria]
    if len(criterion_ids) != len(set(criterion_ids)):
        errors.append("criterion ids must be unique / 判据标识必须唯一")

    roles = contract["roles"]
    critic = _binding_key(roles["critic_binding"])
    policy_gate = _binding_key(roles["policy_gate_binding"])
    release_gate = _binding_key(roles["release_gate_binding"])
    if critic == policy_gate:
        errors.append("critic and policy gate must be distinct / 评审器与策略闸必须分离")
    if critic == release_gate:
        errors.append("critic and release gate must be distinct / 评审器与发布闸必须分离")
    if policy_gate == release_gate:
        errors.append("policy gate and release gate must be distinct / 策略闸与发布闸必须分离")

    variant = contract["review_policy"]["feedback_variant"]
    generator = _binding_key(roles["generator_binding"])
    if variant in {"cross_model", "tool_grounded", "human_review"} and generator == critic:
        errors.append(
            "selected feedback variant requires a critic distinct from the generator / "
            "所选反馈变体要求评审器与生成器分离"
        )
    if variant == "self_critique" and _binding_key(
        roles["critic_configuration_binding"]
    ) == generator:
        errors.append(
            "self-critique requires a distinct critic configuration binding / "
            "自评必须绑定独立评审配置"
        )

    if contract["artifact_policy"]["max_revisions"] < 1:
        errors.append("at least one bounded revision must be available / 至少必须允许一次有界修订")

    if errors:
        raise GeneratorCriticValidationError(errors)


def validate_generator_critic_artifact(
    artifact: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    parent: Mapping[str, Any] | None = None,
) -> None:
    """Validate an immutable artifact revision / 校验不可变工件修订。"""

    validate_schema("generator_critic_artifact", artifact)
    validate_artifact_hash("generator_critic_artifact", artifact)
    errors: list[str] = []
    if contract is not None:
        policy = contract["artifact_policy"]
        if artifact["artifact_id"] != policy["artifact_id"]:
            errors.append("artifact id differs from contract / 工件标识与契约不一致")
        if artifact["artifact_type"] != policy["artifact_type"]:
            errors.append("artifact type differs from contract / 工件类型与契约不一致")
        initial = policy["initial_revision"]
        if (
            parent is None
            and artifact["parent_binding"] is None
            and artifact["revision"] != initial
        ):
            errors.append("initial artifact revision differs from contract / 初始工件修订号与契约不一致")
        if artifact["revision"] - initial > policy["max_revisions"]:
            errors.append("artifact revision budget exceeded / 工件修订预算已超出")
        if artifact["revision"] == initial and artifact["parent_binding"] is not None:
            errors.append("initial artifact cannot have a parent / 初始工件不得具有父版本")
        if artifact["revision"] > initial and artifact["parent_binding"] is None:
            errors.append("revised artifact requires a parent binding / 修订工件必须绑定父版本")
    if parent is not None:
        validate_generator_critic_artifact(parent, contract=contract)
        if artifact["revision"] != parent["revision"] + 1:
            errors.append("artifact revisions must be contiguous / 工件修订号必须连续")
        if artifact["parent_binding"] != artifact_binding(parent):
            errors.append("artifact parent binding mismatch / 工件父版本绑定不匹配")
        if artifact["artifact_digest"] == parent["artifact_digest"]:
            errors.append("a revision must change content / 修订必须改变内容")
    if artifact["review_status"] != "unreviewed":
        errors.append("every new artifact revision must be unreviewed / 每个新工件修订必须为未评审")
    if errors:
        raise GeneratorCriticValidationError(errors)


def _snapshot_index(review: Mapping[str, Any]) -> dict[tuple[Any, Any, Any], Mapping[str, Any]]:
    return {
        _binding_key(snapshot["binding"]): snapshot
        for snapshot in review["evidence_snapshots"]
    }


def validate_generator_critic_review(
    review: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    artifact: Mapping[str, Any] | None = None,
) -> None:
    """Validate evidence buckets and exact review bindings / 校验证据分桶与精确评审绑定。"""

    validate_schema("generator_critic_review", review)
    validate_artifact_hash("generator_critic_review", review)
    errors: list[str] = []
    reviewed_at = _parse_datetime(review["reviewed_at"])
    snapshots = _snapshot_index(review)
    if len(snapshots) != len(review["evidence_snapshots"]):
        errors.append("evidence snapshot bindings must be unique / 证据快照绑定必须唯一")

    trusted_snapshot_keys: set[tuple[Any, Any, Any]] = set()
    for key, snapshot in snapshots.items():
        acquired_at = _parse_datetime(snapshot["acquired_at"])
        if acquired_at > reviewed_at:
            errors.append("evidence cannot be acquired after review / 证据不得在评审之后获取")
        expires_at = snapshot["expires_at"]
        if expires_at is not None and _parse_datetime(expires_at) < reviewed_at:
            errors.append("stale evidence cannot support a review / 过期证据不得支撑评审")
        if (
            snapshot["source_kind"] != "statistical_inference"
            and snapshot["authority_level"] != "diagnostic_only"
        ):
            trusted_snapshot_keys.add(key)

    supported = review["supported_findings"]
    opinions = review["unsupported_opinions"]
    supported_ids = [item["issue_id"] for item in supported]
    opinion_ids = [item["opinion_id"] for item in opinions]
    if len(supported_ids) != len(set(supported_ids)):
        errors.append("supported issue ids must be unique / 有据问题标识必须唯一")
    if len(opinion_ids) != len(set(opinion_ids)):
        errors.append("opinion ids must be unique / 意见标识必须唯一")
    if set(supported_ids) & set(opinion_ids):
        errors.append("supported findings and opinions must use separate ids / 有据问题与意见必须使用不同标识")

    criterion_map: dict[str, Mapping[str, Any]] = {}
    if contract is not None:
        validate_generator_critic_contract(contract)
        criterion_map = {item["criterion_id"]: item for item in contract["criteria"]}
        if review["contract_binding"] != _contract_binding(contract):
            errors.append("review contract binding mismatch / 评审契约绑定不匹配")
        roles = contract["roles"]
        if not _same_binding(review["critic_binding"], roles["critic_binding"]):
            errors.append("review critic binding mismatch / 评审器绑定不匹配")
        if not _same_binding(
            review["critic_configuration_binding"], roles["critic_configuration_binding"]
        ):
            errors.append("review critic configuration mismatch / 评审器配置绑定不匹配")
        if review["feedback_variant"] != contract["review_policy"]["feedback_variant"]:
            errors.append("review feedback variant mismatch / 评审反馈变体不匹配")
        result_ids = [item["criterion_id"] for item in review["criteria_results"]]
        if len(result_ids) != len(set(result_ids)):
            errors.append("criterion results must be unique / 判据结果必须唯一")
        if set(result_ids) != set(criterion_map):
            errors.append("review must cover every sealed criterion exactly once / 评审必须逐项覆盖全部封存判据")
        expected_risks = {
            risk
            for criterion in contract["criteria"]
            for risk in criterion["risk_refs"]
        }
        if not expected_risks.issubset(set(review["risk_refs_checked"])):
            errors.append("review risk coverage is incomplete / 评审风险覆盖不完整")
    if artifact is not None:
        validate_generator_critic_artifact(artifact, contract=contract)
        if review["artifact_binding"] != artifact_binding(artifact):
            errors.append("review binds a different artifact revision / 评审绑定了不同工件修订")

    supported_by_id = {item["issue_id"]: item for item in supported}
    for finding in supported:
        criterion = criterion_map.get(finding["criterion_id"])
        if contract is not None and criterion is None:
            errors.append(f"unknown finding criterion {finding['criterion_id']} / 未知问题判据")
        elif criterion is not None and finding["check_id"] != criterion["check_id"]:
            errors.append(f"finding {finding['issue_id']} check id mismatch / 问题检查标识不匹配")
        evidence_keys = _binding_set(finding["evidence_bindings"])
        if not evidence_keys.issubset(trusted_snapshot_keys):
            errors.append(
                f"finding {finding['issue_id']} lacks fresh auditable evidence / "
                f"问题 {finding['issue_id']} 缺少新鲜可审计证据"
            )

    for opinion in opinions:
        if opinion["criterion_id"] is not None and contract is not None:
            if opinion["criterion_id"] not in criterion_map:
                errors.append(f"unknown opinion criterion {opinion['criterion_id']} / 未知意见判据")
        if not opinion["preserved_non_gating"]:
            errors.append("unsupported opinions must remain non-gating / 无据意见必须保持不参与门控")

    for result in review["criteria_results"]:
        criterion = criterion_map.get(result["criterion_id"])
        if criterion is not None and result["check_id"] != criterion["check_id"]:
            errors.append(f"criterion {result['criterion_id']} check id mismatch / 判据检查标识不匹配")
        result_evidence = _binding_set(result["evidence_bindings"])
        if not result_evidence.issubset(trusted_snapshot_keys):
            errors.append(f"criterion {result['criterion_id']} uses untrusted evidence / 判据使用不可信证据")
        if criterion is not None and criterion["evidence_required"]:
            if result["status"] in {"pass", "fail"} and not result_evidence:
                errors.append(f"criterion {result['criterion_id']} requires evidence / 判据要求证据")
        finding_refs = result["finding_refs"]
        if any(ref not in supported_by_id for ref in finding_refs):
            errors.append(f"criterion {result['criterion_id']} references an unknown finding / 判据引用未知问题")
        if any(
            supported_by_id[ref]["criterion_id"] != result["criterion_id"]
            for ref in finding_refs
            if ref in supported_by_id
        ):
            errors.append(f"criterion {result['criterion_id']} references a finding from another criterion / 判据引用其他判据的问题")
        if result["status"] == "fail" and not finding_refs:
            errors.append(f"failed criterion {result['criterion_id']} requires a supported finding / 失败判据必须引用有据问题")
        if result["status"] in {"pass", "not_applicable"} and finding_refs:
            errors.append(f"non-failing criterion {result['criterion_id']} cannot own findings / 非失败判据不得挂载问题")

    score = review["score"]
    score_evidence = _binding_set(score["evidence_bindings"])
    if not score_evidence.issubset(trusted_snapshot_keys):
        errors.append("score uses stale or diagnostic-only evidence / 评分使用过期或仅诊断证据")
    if score["value"] is None and (score["evidence_bindings"] or score["rationale"] is not None):
        errors.append("an absent score cannot claim rationale or evidence / 缺失评分不得声明依据或证据")
    if score["value"] is not None and not score["rationale"]:
        errors.append("a score requires an explicit rationale / 评分必须有明确依据说明")

    if errors:
        raise GeneratorCriticValidationError(errors)


def validate_generator_critic_decision(
    decision: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    review: Mapping[str, Any] | None = None,
) -> None:
    """Validate one policy-owned decision / 校验单个策略所有的裁决。"""

    validate_schema("generator_critic_decision", decision)
    validate_artifact_hash("generator_critic_decision", decision)
    errors: list[str] = []
    if contract is not None:
        validate_generator_critic_contract(contract)
        if decision["contract_binding"] != _contract_binding(contract):
            errors.append("decision contract binding mismatch / 裁决契约绑定不匹配")
        if not _same_binding(
            decision["policy_gate_binding"], contract["roles"]["policy_gate_binding"]
        ):
            errors.append("decision policy gate mismatch / 裁决策略闸绑定不匹配")
    if review is not None:
        validate_generator_critic_review(review, contract=contract)
        expected_review = _record_binding(
            review, identifier_field="review_id", hash_field="review_hash"
        )
        if decision["review_binding"] != expected_review:
            errors.append("decision review binding mismatch / 裁决评审绑定不匹配")
        if decision["artifact_binding"] != review["artifact_binding"]:
            errors.append("decision artifact binding mismatch / 裁决工件绑定不匹配")
        supported_ids = {item["issue_id"] for item in review["supported_findings"]}
        opinion_ids = {item["opinion_id"] for item in review["unsupported_opinions"]}
        if not set(decision["gating_issue_refs"]).issubset(supported_ids):
            errors.append("decision gates on a non-supported issue / 裁决使用了非有据问题门控")
        if set(decision["retained_opinion_refs"]) != opinion_ids:
            errors.append("decision must preserve every unsupported opinion / 裁决必须保留全部无据意见")
    if errors:
        raise GeneratorCriticValidationError(errors)


def validate_generator_critic_receipt(
    receipt: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    review: Mapping[str, Any] | None = None,
    decision: Mapping[str, Any] | None = None,
) -> None:
    """Validate a receipt binding the accepted exact version / 校验绑定已接受精确版本的回执。"""

    validate_schema("generator_critic_receipt", receipt)
    validate_artifact_hash("generator_critic_receipt", receipt)
    errors: list[str] = []
    issued_at = _parse_datetime(receipt["issued_at"])
    if receipt["expires_at"] is not None and _parse_datetime(receipt["expires_at"]) <= issued_at:
        errors.append("receipt expiry must be after issue time / 回执过期时间必须晚于签发时间")
    if contract is not None:
        validate_generator_critic_contract(contract)
        if receipt["contract_binding"] != _contract_binding(contract):
            errors.append("receipt contract binding mismatch / 回执契约绑定不匹配")
        roles = contract["roles"]
        for field in ("critic_binding", "policy_gate_binding", "release_gate_binding"):
            if not _same_binding(receipt[field], roles[field]):
                errors.append(f"receipt {field} mismatch / 回执 {field} 绑定不匹配")
    if review is not None:
        validate_generator_critic_review(review, contract=contract)
        if receipt["review_binding"] != _record_binding(
            review, identifier_field="review_id", hash_field="review_hash"
        ):
            errors.append("receipt review binding mismatch / 回执评审绑定不匹配")
        if receipt["artifact_binding"] != review["artifact_binding"]:
            errors.append("receipt artifact binding mismatch / 回执工件绑定不匹配")
        expected_evidence = [snapshot["binding"] for snapshot in review["evidence_snapshots"]]
        if _binding_set(receipt["evidence_snapshot_bindings"]) != _binding_set(expected_evidence):
            errors.append("receipt evidence snapshot set mismatch / 回执证据快照集合不匹配")
    if decision is not None:
        validate_generator_critic_decision(decision, contract=contract, review=review)
        if decision["decision"] != GeneratorCriticDecision.ACCEPT.value:
            errors.append("only an accepted decision can receive a receipt / 仅接受裁决可签发回执")
        if receipt["decision_binding"] != _record_binding(
            decision, identifier_field="decision_id", hash_field="decision_hash"
        ):
            errors.append("receipt decision binding mismatch / 回执裁决绑定不匹配")
    if errors:
        raise GeneratorCriticValidationError(errors)


def validate_generator_critic_event(event: Mapping[str, Any]) -> None:
    """Validate one self-hashed public event / 校验单个自哈希公开事件。"""

    validate_schema("generator_critic_event", event)
    validate_artifact_hash("generator_critic_event", event)


def validate_generator_critic_event_stream(events: Sequence[Mapping[str, Any]]) -> None:
    """Validate contiguous sequence and state continuity / 校验连续顺序与状态连续性。"""

    errors: list[str] = []
    prior_state: str | None = None
    seen_ids: set[str] = set()
    seen_keys: set[str] = set()
    for index, event in enumerate(events, start=1):
        try:
            validate_generator_critic_event(event)
        except Exception as exc:  # Preserve all stream failures / 保留全部流错误
            errors.append(str(exc))
            continue
        if event["sequence"] != index:
            errors.append(f"event sequence must be contiguous at {index} / 事件序列在 {index} 处不连续")
        if event["event_id"] in seen_ids:
            errors.append("event ids must be unique / 事件标识必须唯一")
        if event["idempotency_key"] in seen_keys:
            errors.append("event idempotency keys must be unique / 事件幂等键必须唯一")
        if prior_state is not None and event["state_before"] != prior_state:
            errors.append(f"event state discontinuity at {index} / 事件状态在 {index} 处不连续")
        seen_ids.add(event["event_id"])
        seen_keys.add(event["idempotency_key"])
        prior_state = event["state_after"]
    if errors:
        raise GeneratorCriticValidationError(errors)


class GeneratorCriticSession:
    """Deterministic exact-version review coordinator / 确定性精确版本评审协调器。"""

    def __init__(
        self,
        contract: Mapping[str, Any],
        *,
        session_id: str,
        shared_reflection_guard: Callable[
            [str, Mapping[str, Any]], Mapping[str, Any]
        ],
    ) -> None:
        validate_generator_critic_contract(contract)
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if not callable(shared_reflection_guard):
            raise TypeError("shared_reflection_guard must be callable")
        self._contract = deepcopy(dict(contract))
        self._session_id = session_id
        self._shared_reflection_guard = shared_reflection_guard
        self._state = GeneratorCriticState.INITIALIZED
        self._artifacts: list[dict[str, Any]] = []
        self._reviews: list[dict[str, Any]] = []
        self._decisions: list[dict[str, Any]] = []
        self._receipts: list[dict[str, Any]] = []
        self._events: list[dict[str, Any]] = []
        self._review_pass_count = 0
        self._pending_review_id: str | None = None
        self._review_ids: set[str] = set()
        self._receipt_ids: set[str] = set()

    def _require_shared_reflection_assurance(
        self,
        stage: str,
        *,
        artifact: Mapping[str, Any],
        context: Mapping[str, Any] | None = None,
    ) -> dict[str, str]:
        """Fail closed unless shared reflection returns an auditable assurance binding. / 共享反思未返回可审计保证绑定时默认阻断。"""

        requirements = GENERATOR_CRITIC_SHARED_GUARD_REQUIREMENTS[stage]
        request = {
            "generator_critic_contract_binding": _contract_binding(self._contract),
            "reflection_contract_binding": deepcopy(
                self._contract["reflection_contract_binding"]
            ),
            "run_binding": deepcopy(self._contract["run_binding"]),
            "artifact_binding": artifact_binding(artifact),
            "required_shared_reflection_facts": list(requirements),
            "context": deepcopy(dict(context or {})),
        }
        try:
            result = self._shared_reflection_guard(stage, deepcopy(request))
        except Exception as exc:
            raise GeneratorCriticAuthorizationError(
                f"shared reflection guard failed at {stage} / 共享反思闸在 {stage} 失败"
            ) from exc
        if not isinstance(result, Mapping) or set(result) != {"id", "version", "hash"}:
            raise GeneratorCriticAuthorizationError(
                "shared reflection guard must return one exact assurance binding / "
                "共享反思闸必须返回一个精确保证绑定"
            )
        assurance = deepcopy(dict(result))
        if (
            not isinstance(assurance["id"], str)
            or not assurance["id"]
            or not isinstance(assurance["version"], str)
            or _SEMANTIC_VERSION.fullmatch(assurance["version"]) is None
            or not isinstance(assurance["hash"], str)
            or _SHA256.fullmatch(assurance["hash"]) is None
        ):
            raise GeneratorCriticAuthorizationError(
                "shared reflection assurance binding is invalid / 共享反思保证绑定无效"
            )
        return assurance

    @property
    def state(self) -> GeneratorCriticState:
        return self._state

    @property
    def contract(self) -> dict[str, Any]:
        return deepcopy(self._contract)

    @property
    def artifacts(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._artifacts))

    @property
    def reviews(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._reviews))

    @property
    def decisions(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._decisions))

    @property
    def receipts(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._receipts))

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._events))

    @property
    def current_artifact(self) -> dict[str, Any] | None:
        return deepcopy(self._artifacts[-1]) if self._artifacts else None

    def _require_state(self, *states: GeneratorCriticState) -> None:
        if self._state not in states:
            allowed = ", ".join(state.value for state in states)
            raise GeneratorCriticStateError(
                f"state {self._state.value} does not allow this operation; expected {allowed} / "
                f"状态 {self._state.value} 不允许此操作；预期 {allowed}"
            )

    def _require_actor(self, actual: Mapping[str, Any], role_field: str) -> None:
        expected = self._contract["roles"][role_field]
        if not _same_binding(actual, expected):
            raise GeneratorCriticAuthorizationError(
                f"{role_field} binding mismatch / {role_field} 绑定不匹配"
            )

    def _make_event(
        self,
        event_type: str,
        *,
        state_before: GeneratorCriticState,
        state_after: GeneratorCriticState,
        artifact: Mapping[str, Any],
        occurred_at: str,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        sequence = len(self._events) + 1
        event = {
            "schema_version": "1.0.0",
            "event_id": f"{self._session_id}:event:{sequence:04d}",
            "event_type": event_type,
            "session_id": self._session_id,
            "sequence": sequence,
            "occurred_at": occurred_at,
            "idempotency_key": f"{self._session_id}:{event_type}:{sequence:04d}",
            "contract_binding": _contract_binding(self._contract),
            "artifact_binding": artifact_binding(artifact),
            "state_before": state_before.value,
            "state_after": state_after.value,
            "payload": deepcopy(dict(payload)),
        }
        sealed = build_artifact("generator_critic_event", event)
        validate_generator_critic_event(sealed)
        return sealed

    def create_initial_artifact(
        self,
        *,
        content: Any,
        content_ref: str,
        producer_binding: Mapping[str, Any],
        created_at: str,
    ) -> dict[str, Any]:
        """Create revision zero or the configured initial revision / 创建零号或契约配置的初始修订。"""

        self._require_state(GeneratorCriticState.INITIALIZED)
        self._require_actor(producer_binding, "generator_binding")
        _parse_datetime(created_at)
        if not isinstance(content_ref, str) or not content_ref.strip():
            raise ValueError("content_ref must be a non-empty string")
        policy = self._contract["artifact_policy"]
        artifact = {
            "schema_version": "1.0.0",
            "artifact_id": policy["artifact_id"],
            "artifact_type": policy["artifact_type"],
            "revision": policy["initial_revision"],
            "artifact_digest": artifact_fingerprint({"content": content}),
            "parent_binding": None,
            "content_ref": content_ref,
            "producer_binding": deepcopy(dict(producer_binding)),
            "review_status": "unreviewed",
            "created_at": created_at,
        }
        sealed = build_artifact("generator_critic_artifact", artifact)
        validate_generator_critic_artifact(sealed, contract=self._contract)
        assurance = self._require_shared_reflection_assurance(
            "initial_artifact", artifact=sealed
        )
        event = self._make_event(
            "artifact_revision_created",
            state_before=self._state,
            state_after=GeneratorCriticState.ARTIFACT_UNREVIEWED,
            artifact=sealed,
            occurred_at=created_at,
            payload={
                "revision": sealed["revision"],
                "parent_binding": None,
                "shared_reflection_assurance_binding": assurance,
            },
        )
        self._artifacts.append(sealed)
        self._events.append(event)
        self._state = GeneratorCriticState.ARTIFACT_UNREVIEWED
        return deepcopy(sealed)

    def start_review(
        self,
        *,
        review_id: str,
        artifact: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Start an explicit review of the current exact revision / 显式开始评审当前精确修订。"""

        self._require_state(
            GeneratorCriticState.ARTIFACT_UNREVIEWED,
            GeneratorCriticState.WAITING_EVIDENCE,
        )
        if not isinstance(review_id, str) or not review_id.strip() or review_id in self._review_ids:
            raise ValueError("review_id must be non-empty and unique")
        if self._review_pass_count >= self._contract["review_policy"]["max_critique_passes"]:
            raise GeneratorCriticStateError("critique pass budget is exhausted / 评审批次预算已耗尽")
        current = self._artifacts[-1]
        if dict(artifact) != artifact_binding(current):
            raise GeneratorCriticStateError("review must bind the current exact artifact / 评审必须绑定当前精确工件")
        _parse_datetime(occurred_at)
        event = self._make_event(
            "artifact_review_started",
            state_before=self._state,
            state_after=GeneratorCriticState.REVIEWING,
            artifact=current,
            occurred_at=occurred_at,
            payload={"review_id": review_id, "review_pass": self._review_pass_count + 1},
        )
        self._pending_review_id = review_id
        self._review_ids.add(review_id)
        self._review_pass_count += 1
        self._events.append(event)
        self._state = GeneratorCriticState.REVIEWING
        return deepcopy(event)

    def record_review(
        self,
        *,
        evidence_snapshots: Sequence[Mapping[str, Any]],
        criteria_results: Sequence[Mapping[str, Any]],
        supported_findings: Sequence[Mapping[str, Any]],
        unsupported_opinions: Sequence[Mapping[str, Any]],
        score: Mapping[str, Any],
        risk_refs_checked: Sequence[str],
        reviewed_at: str,
    ) -> dict[str, Any]:
        """Record critic output without granting a decision / 记录评审器输出但不授予裁决权。"""

        self._require_state(GeneratorCriticState.REVIEWING)
        assert self._pending_review_id is not None
        current = self._artifacts[-1]
        review = {
            "schema_version": "1.0.0",
            "review_id": self._pending_review_id,
            "contract_binding": _contract_binding(self._contract),
            "artifact_binding": artifact_binding(current),
            "critic_binding": deepcopy(self._contract["roles"]["critic_binding"]),
            "critic_configuration_binding": deepcopy(
                self._contract["roles"]["critic_configuration_binding"]
            ),
            "feedback_variant": self._contract["review_policy"]["feedback_variant"],
            "evidence_snapshots": [deepcopy(dict(item)) for item in evidence_snapshots],
            "criteria_results": [deepcopy(dict(item)) for item in criteria_results],
            "supported_findings": [deepcopy(dict(item)) for item in supported_findings],
            "unsupported_opinions": [deepcopy(dict(item)) for item in unsupported_opinions],
            "score": deepcopy(dict(score)),
            "risk_refs_checked": list(risk_refs_checked),
            "reviewed_at": reviewed_at,
        }
        sealed = build_artifact("generator_critic_review", review)
        validate_generator_critic_review(
            sealed, contract=self._contract, artifact=current
        )
        event = self._make_event(
            "artifact_review_recorded",
            state_before=self._state,
            state_after=GeneratorCriticState.REVIEWED,
            artifact=current,
            occurred_at=reviewed_at,
            payload={
                "review_binding": _record_binding(
                    sealed, identifier_field="review_id", hash_field="review_hash"
                ),
                "supported_finding_count": len(sealed["supported_findings"]),
                "unsupported_opinion_count": len(sealed["unsupported_opinions"]),
            },
        )
        self._reviews.append(sealed)
        self._events.append(event)
        self._pending_review_id = None
        self._state = GeneratorCriticState.REVIEWED
        return deepcopy(sealed)

    def _derive_decision(self, review: Mapping[str, Any]) -> tuple[GeneratorCriticDecision, list[str], list[str]]:
        policy = self._contract["decision_policy"]
        blocking = set(policy["blocking_severities"])
        gating = [
            item["issue_id"]
            for item in review["supported_findings"]
            if item["severity"] in blocking
        ]
        rules: list[str] = []
        candidate: GeneratorCriticDecision
        if gating:
            candidate = GeneratorCriticDecision.NEEDS_REVISION
            rules.append("POLICY_SUPPORTED_BLOCKING")
        elif any(item["status"] == "unknown" for item in review["criteria_results"]):
            candidate = GeneratorCriticDecision(policy["unknown_action"])
            rules.append("POLICY_UNKNOWN_CRITERION")
        elif any(
            item["severity"] == "warning"
            for item in review["supported_findings"]
        ):
            candidate = GeneratorCriticDecision(policy["warning_action"])
            rules.append("POLICY_SUPPORTED_WARNING")
        else:
            candidate = GeneratorCriticDecision.ACCEPT
            rules.append("POLICY_NO_GATING_FINDING")

        score = review["score"]
        minimum_score = policy["minimum_score"]
        if (
            minimum_score is not None
            and score["value"] is not None
            and score["value"] < minimum_score
        ):
            if score["evidence_bindings"]:
                candidate = GeneratorCriticDecision(
                    policy["below_minimum_score_action"]
                )
                rules.append("POLICY_EVIDENCED_SCORE_BELOW_MINIMUM")
            else:
                rules.append("POLICY_UNEVIDENCED_SCORE_NON_GATING")

        if (
            candidate is GeneratorCriticDecision.NEEDS_REVISION
            and self._review_pass_count >= self._contract["review_policy"]["max_critique_passes"]
        ):
            candidate = GeneratorCriticDecision(policy["exhausted_action"])
            rules.append("POLICY_REVIEW_BUDGET_EXHAUSTED")
        return candidate, rules, gating

    def decide(self, *, decided_at: str) -> dict[str, Any]:
        """Derive the policy decision; never accept a critic-supplied verdict / 派生策略裁决，绝不接受评审器自报裁决。"""

        self._require_state(GeneratorCriticState.REVIEWED)
        _parse_datetime(decided_at)
        review = self._reviews[-1]
        normalized, rules, gating = self._derive_decision(review)
        decision = {
            "schema_version": "1.0.0",
            "decision_id": f"{self._session_id}:decision:{len(self._decisions) + 1:04d}",
            "contract_binding": _contract_binding(self._contract),
            "review_binding": _record_binding(
                review, identifier_field="review_id", hash_field="review_hash"
            ),
            "artifact_binding": deepcopy(review["artifact_binding"]),
            "policy_gate_binding": deepcopy(
                self._contract["roles"]["policy_gate_binding"]
            ),
            "decision": normalized.value,
            "triggered_rules": rules,
            "gating_issue_refs": gating,
            "retained_opinion_refs": [
                item["opinion_id"] for item in review["unsupported_opinions"]
            ],
            "decided_at": decided_at,
        }
        sealed = build_artifact("generator_critic_decision", decision)
        validate_generator_critic_decision(
            sealed, contract=self._contract, review=review
        )
        target = _DECISION_STATE[normalized]
        current = self._artifacts[-1]
        event = self._make_event(
            "review_decision_recorded",
            state_before=self._state,
            state_after=target,
            artifact=current,
            occurred_at=decided_at,
            payload={
                "decision_binding": _record_binding(
                    sealed, identifier_field="decision_id", hash_field="decision_hash"
                ),
                "decision": normalized.value,
                "triggered_rules": rules,
            },
        )
        self._decisions.append(sealed)
        self._events.append(event)
        self._state = target
        return deepcopy(sealed)

    def create_revision(
        self,
        *,
        content: Any,
        content_ref: str,
        producer_binding: Mapping[str, Any],
        resolved_issue_refs: Sequence[str],
        created_at: str,
    ) -> dict[str, Any]:
        """Create a new unreviewed revision from adopted issues only / 仅基于已采纳问题创建新的未评审修订。"""

        self._require_state(GeneratorCriticState.NEEDS_REVISION)
        self._require_actor(producer_binding, "reviser_binding")
        _parse_datetime(created_at)
        if not isinstance(content_ref, str) or not content_ref.strip():
            raise ValueError("content_ref must be a non-empty string")
        decision = self._decisions[-1]
        allowed = set(decision["gating_issue_refs"])
        provided = set(resolved_issue_refs)
        if not provided or not provided.issubset(allowed):
            raise GeneratorCriticAuthorizationError(
                "revision may use only policy-adopted gating issues / 修订只能使用策略采纳的门控问题"
            )
        parent = self._artifacts[-1]
        policy = self._contract["artifact_policy"]
        if parent["revision"] - policy["initial_revision"] >= policy["max_revisions"]:
            raise GeneratorCriticStateError("artifact revision budget is exhausted / 工件修订预算已耗尽")
        artifact = {
            "schema_version": "1.0.0",
            "artifact_id": parent["artifact_id"],
            "artifact_type": parent["artifact_type"],
            "revision": parent["revision"] + 1,
            "artifact_digest": artifact_fingerprint({"content": content}),
            "parent_binding": artifact_binding(parent),
            "content_ref": content_ref,
            "producer_binding": deepcopy(dict(producer_binding)),
            "review_status": "unreviewed",
            "created_at": created_at,
        }
        sealed = build_artifact("generator_critic_artifact", artifact)
        validate_generator_critic_artifact(
            sealed, contract=self._contract, parent=parent
        )
        assurance = self._require_shared_reflection_assurance(
            "revision",
            artifact=sealed,
            context={
                "parent_artifact_binding": artifact_binding(parent),
                "change_proposal_binding": _record_binding(
                    decision,
                    identifier_field="decision_id",
                    hash_field="decision_hash",
                ),
                "adopted_issue_refs": sorted(provided),
            },
        )
        event = self._make_event(
            "artifact_revision_created",
            state_before=self._state,
            state_after=GeneratorCriticState.ARTIFACT_UNREVIEWED,
            artifact=sealed,
            occurred_at=created_at,
            payload={
                "revision": sealed["revision"],
                "parent_binding": sealed["parent_binding"],
                "resolved_issue_refs": sorted(provided),
                "shared_reflection_assurance_binding": assurance,
            },
        )
        self._artifacts.append(sealed)
        self._events.append(event)
        self._state = GeneratorCriticState.ARTIFACT_UNREVIEWED
        return deepcopy(sealed)

    def issue_receipt(
        self,
        *,
        receipt_id: str,
        release_gate_binding: Mapping[str, Any],
        issued_at: str,
        expires_at: str | None = None,
    ) -> dict[str, Any]:
        """Issue a receipt only for the accepted exact revision / 仅为已接受的精确修订签发回执。"""

        self._require_state(GeneratorCriticState.ACCEPTED)
        if not isinstance(receipt_id, str) or not receipt_id.strip() or receipt_id in self._receipt_ids:
            raise ValueError("receipt_id must be non-empty and unique")
        self._require_actor(release_gate_binding, "release_gate_binding")
        issued = _parse_datetime(issued_at)
        if expires_at is None:
            ttl = self._contract["release_policy"]["default_receipt_ttl_seconds"]
            if ttl is not None:
                expires_at = _format_datetime(issued + timedelta(seconds=ttl))
        review = self._reviews[-1]
        decision = self._decisions[-1]
        assurance = self._require_shared_reflection_assurance(
            "receipt",
            artifact=self._artifacts[-1],
            context={
                "review_binding": _record_binding(
                    review, identifier_field="review_id", hash_field="review_hash"
                ),
                "decision_binding": _record_binding(
                    decision,
                    identifier_field="decision_id",
                    hash_field="decision_hash",
                ),
            },
        )
        receipt = {
            "schema_version": "1.0.0",
            "receipt_id": receipt_id,
            "contract_binding": _contract_binding(self._contract),
            "review_binding": _record_binding(
                review, identifier_field="review_id", hash_field="review_hash"
            ),
            "decision_binding": _record_binding(
                decision, identifier_field="decision_id", hash_field="decision_hash"
            ),
            "artifact_binding": deepcopy(decision["artifact_binding"]),
            "critic_binding": deepcopy(self._contract["roles"]["critic_binding"]),
            "policy_gate_binding": deepcopy(
                self._contract["roles"]["policy_gate_binding"]
            ),
            "release_gate_binding": deepcopy(dict(release_gate_binding)),
            "evidence_snapshot_bindings": [
                deepcopy(snapshot["binding"])
                for snapshot in review["evidence_snapshots"]
            ],
            "shared_reflection_assurance_binding": assurance,
            "issued_at": issued_at,
            "expires_at": expires_at,
        }
        sealed = build_artifact("generator_critic_receipt", receipt)
        validate_generator_critic_receipt(
            sealed,
            contract=self._contract,
            review=review,
            decision=decision,
        )
        event = self._make_event(
            "review_receipt_issued",
            state_before=self._state,
            state_after=self._state,
            artifact=self._artifacts[-1],
            occurred_at=issued_at,
            payload={
                "receipt_binding": _record_binding(
                    sealed, identifier_field="receipt_id", hash_field="receipt_hash"
                ),
                "expires_at": expires_at,
                "shared_reflection_assurance_binding": assurance,
            },
        )
        self._receipts.append(sealed)
        self._receipt_ids.add(receipt_id)
        self._events.append(event)
        return deepcopy(sealed)

    def create_superseding_revision(
        self,
        *,
        content: Any,
        content_ref: str,
        producer_binding: Mapping[str, Any],
        change_proposal_binding: Mapping[str, Any],
        change_reason: str,
        created_at: str,
    ) -> dict[str, Any]:
        """Invalidate an accepted version by creating new unreviewed content / 以新未评审内容使旧接受版本失效。"""

        self._require_state(GeneratorCriticState.ACCEPTED)
        self._require_actor(producer_binding, "reviser_binding")
        _parse_datetime(created_at)
        if not isinstance(content_ref, str) or not content_ref.strip():
            raise ValueError("content_ref must be a non-empty string")
        if not isinstance(change_reason, str) or not change_reason.strip():
            raise ValueError("change_reason must be a non-empty string")
        parent = self._artifacts[-1]
        policy = self._contract["artifact_policy"]
        if parent["revision"] - policy["initial_revision"] >= policy["max_revisions"]:
            raise GeneratorCriticStateError("artifact revision budget is exhausted / 工件修订预算已耗尽")
        artifact = {
            "schema_version": "1.0.0",
            "artifact_id": parent["artifact_id"],
            "artifact_type": parent["artifact_type"],
            "revision": parent["revision"] + 1,
            "artifact_digest": artifact_fingerprint({"content": content}),
            "parent_binding": artifact_binding(parent),
            "content_ref": content_ref,
            "producer_binding": deepcopy(dict(producer_binding)),
            "review_status": "unreviewed",
            "created_at": created_at,
        }
        sealed = build_artifact("generator_critic_artifact", artifact)
        validate_generator_critic_artifact(
            sealed, contract=self._contract, parent=parent
        )
        assurance = self._require_shared_reflection_assurance(
            "superseding_revision",
            artifact=sealed,
            context={
                "parent_artifact_binding": artifact_binding(parent),
                "change_proposal_binding": deepcopy(dict(change_proposal_binding)),
                "change_reason": change_reason,
            },
        )
        event = self._make_event(
            "artifact_revision_created",
            state_before=self._state,
            state_after=GeneratorCriticState.ARTIFACT_UNREVIEWED,
            artifact=sealed,
            occurred_at=created_at,
            payload={
                "revision": sealed["revision"],
                "parent_binding": sealed["parent_binding"],
                "change_reason": change_reason,
                "invalidated_receipt_bindings": [
                    _record_binding(
                        item, identifier_field="receipt_id", hash_field="receipt_hash"
                    )
                    for item in self._receipts
                    if item["artifact_binding"] == artifact_binding(parent)
                ],
                "shared_reflection_assurance_binding": assurance,
            },
        )
        self._artifacts.append(sealed)
        self._events.append(event)
        self._state = GeneratorCriticState.ARTIFACT_UNREVIEWED
        return deepcopy(sealed)

    def verify_release(
        self,
        *,
        artifact: Mapping[str, Any],
        receipt: Mapping[str, Any],
        current_governance_policy_binding: Mapping[str, Any],
        released_at: str,
    ) -> dict[str, Any]:
        """Verify receipt, digest, policy, and evidence freshness / 校验回执、摘要、策略与证据新鲜度。"""

        self._require_state(GeneratorCriticState.ACCEPTED)
        now = _parse_datetime(released_at)
        current = self._artifacts[-1]
        if dict(artifact) != artifact_binding(current):
            raise GeneratorCriticReleaseError(
                "release artifact is not the current exact revision / 发布工件不是当前精确修订"
            )
        if not self._receipts or dict(receipt) != self._receipts[-1]:
            raise GeneratorCriticReleaseError(
                "release must use the session-issued current receipt / 发布必须使用会话签发的当前回执"
            )
        review = self._reviews[-1]
        decision = self._decisions[-1]
        validate_generator_critic_receipt(
            receipt,
            contract=self._contract,
            review=review,
            decision=decision,
        )
        if receipt["artifact_binding"] != artifact_binding(current):
            raise GeneratorCriticReleaseError(
                "receipt does not bind the release artifact / 回执未绑定发布工件"
            )
        if not _same_binding(
            current_governance_policy_binding,
            self._contract["governance_policy_binding"],
        ):
            raise GeneratorCriticReleaseError(
                "governance policy changed after review / 评审后治理策略已变化"
            )
        if receipt["expires_at"] is not None and _parse_datetime(receipt["expires_at"]) < now:
            raise GeneratorCriticReleaseError("review receipt expired / 评审回执已过期")
        if self._contract["release_policy"]["require_fresh_evidence"]:
            for snapshot in review["evidence_snapshots"]:
                if snapshot["expires_at"] is not None and _parse_datetime(snapshot["expires_at"]) < now:
                    raise GeneratorCriticReleaseError(
                        f"evidence snapshot expired: {snapshot['binding']['id']} / "
                        f"证据快照已过期: {snapshot['binding']['id']}"
                    )
        assurance = self._require_shared_reflection_assurance(
            "release",
            artifact=current,
            context={
                "receipt_binding": _record_binding(
                    receipt, identifier_field="receipt_id", hash_field="receipt_hash"
                ),
                "governance_policy_binding": deepcopy(
                    dict(current_governance_policy_binding)
                ),
            },
        )
        event = self._make_event(
            "artifact_release_verified",
            state_before=self._state,
            state_after=GeneratorCriticState.RELEASED,
            artifact=current,
            occurred_at=released_at,
            payload={
                "receipt_binding": _record_binding(
                    receipt, identifier_field="receipt_id", hash_field="receipt_hash"
                ),
                "governance_policy_binding": deepcopy(
                    dict(current_governance_policy_binding)
                ),
                "shared_reflection_assurance_binding": assurance,
            },
        )
        self._events.append(event)
        self._state = GeneratorCriticState.RELEASED
        validate_generator_critic_event_stream(self._events)
        return deepcopy(event)

    def stop(self, *, reason: str, occurred_at: str) -> dict[str, Any]:
        """Close an unreleased terminal or interrupted session / 关闭未发布终态或中断会话。"""

        if self._state in {GeneratorCriticState.RELEASED, GeneratorCriticState.STOPPED}:
            raise GeneratorCriticStateError("session is already terminal / 会话已终止")
        if not self._artifacts:
            raise GeneratorCriticStateError("cannot stop before an artifact exists / 工件创建前不得结束")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be a non-empty string")
        _parse_datetime(occurred_at)
        event = self._make_event(
            "generator_critic_stopped",
            state_before=self._state,
            state_after=GeneratorCriticState.STOPPED,
            artifact=self._artifacts[-1],
            occurred_at=occurred_at,
            payload={"stop_reason": reason},
        )
        self._events.append(event)
        self._state = GeneratorCriticState.STOPPED
        validate_generator_critic_event_stream(self._events)
        return deepcopy(event)


__all__ = [
    "GENERATOR_CRITIC_PROBES",
    "GENERATOR_CRITIC_SHARED_GUARD_REQUIREMENTS",
    "GeneratorCriticAuthorizationError",
    "GeneratorCriticDecision",
    "GeneratorCriticReleaseError",
    "GeneratorCriticRuntimeError",
    "GeneratorCriticSession",
    "GeneratorCriticState",
    "GeneratorCriticStateError",
    "GeneratorCriticValidationError",
    "artifact_binding",
    "build_shared_reflection_guard",
    "build_generator_critic_contract",
    "reflection_subject_binding_for_artifact",
    "validate_generator_critic_artifact",
    "validate_generator_critic_contract",
    "validate_generator_critic_decision",
    "validate_generator_critic_event",
    "validate_generator_critic_event_stream",
    "validate_generator_critic_receipt",
    "validate_generator_critic_review",
]
