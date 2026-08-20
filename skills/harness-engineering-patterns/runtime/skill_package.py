"""Governed Skill Package lifecycle runtime / 受治理技能包生命周期运行时。

The coordinator records public lifecycle facts and verifies authority, exact
version bindings, release stages, and real reuse receipts. It does not author a
Skill, generate evaluation truth, issue its own production authority, mutate a
route alias, or infer private chain-of-thought. / 本协调器记录公开生命周期事实，
并校验权限、精确版本绑定、发布阶段与真实复用回执；它不编写 Skill、不生成评估
真值、不自行签发生产资格、不修改路由别名，也不推断私密思维过程。
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
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


SKILL_PACKAGE_PROBES = tuple(f"PROBE_{number:04d}" for number in range(28, 34))
SKILL_PACKAGE_REQUIRED_DIMENSIONS = (
    "result",
    "activation",
    "flow",
    "incremental_value",
    "freshness",
)
SKILL_PACKAGE_REQUIRED_SECTIONS = (
    "metadata",
    "use_cases",
    "non_use_cases",
    "inputs",
    "outputs",
    "workflow",
    "tools_permissions",
    "failure_recovery",
    "verification",
    "provenance",
)
SKILL_PACKAGE_RELEASE_STAGES = ("shadow", "limited", "production")

_SHA256 = re.compile(r"^sha256:[a-f0-9]{64}$")
_CJK = re.compile(r"[\u3400-\u9fff]")
_LINEAGE_UNSET = object()


class SkillPackageRuntimeError(RuntimeError):
    """Base lifecycle error / 生命周期错误基类。"""


class SkillPackageValidationError(SkillPackageRuntimeError):
    """A public lifecycle artifact is invalid / 公开生命周期制品无效。"""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


class SkillPackageStateError(SkillPackageRuntimeError):
    """An operation is illegal in the current stage / 操作在当前阶段非法。"""


class SkillPackageAuthorizationError(SkillPackageRuntimeError):
    """An actor or assurance does not match the sealed contract / 主体或保证不匹配封存契约。"""


class SkillPackageReleaseError(SkillPackageRuntimeError):
    """A release, alias, or reuse boundary failed / 发布、别名或复用边界失败。"""


class SkillQualificationState(str, Enum):
    """Routing qualification, separate from asset status / 与资产状态分离的路由资格。"""

    UNREGISTERED = "UNREGISTERED"
    TRIAL = "TRIAL"
    VERIFIED = "VERIFIED"
    RETIRED = "RETIRED"


class SkillReleaseState(str, Enum):
    """Traffic exposure state / 流量暴露状态。"""

    UNPUBLISHED = "unpublished"
    SHADOW = "shadow"
    LIMITED = "limited"
    PRODUCTION = "production"
    SUSPENDED = "suspended"
    RETIRED = "retired"
    ARCHIVED = "archived"


class SkillPackageStage(str, Enum):
    """Coordinator stage / 协调器阶段。"""

    INITIALIZED = "initialized"
    CANDIDATE = "candidate"
    DISTILLED = "distilled"
    TRIAL = "trial"
    VERIFYING = "verifying"
    VERIFICATION_PASSED = "verification_passed"
    CREDENTIALED = "credentialed"
    VERIFIED = "verified"
    SHADOW = "shadow"
    LIMITED = "limited"
    PRODUCTION = "production"
    REVERIFYING = "reverifying"
    RETIRED = "retired"
    ARCHIVED = "archived"


def _binding_key(binding: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return binding.get("id"), binding.get("version"), binding.get("hash")


def _binding_set(bindings: Sequence[Mapping[str, Any]]) -> set[tuple[Any, Any, Any]]:
    return {_binding_key(binding) for binding in bindings}


def _same_binding(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return _binding_key(left) == _binding_key(right)


def _parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise SkillPackageValidationError(
            [f"invalid date-time {value!r} / 无效日期时间 {value!r}"]
        ) from exc
    if parsed.tzinfo is None:
        raise SkillPackageValidationError(
            [f"date-time must include a timezone: {value!r} / 日期时间必须包含时区: {value!r}"]
        )
    return parsed.astimezone(timezone.utc)


def _require_binding(value: Mapping[str, Any], *, name: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != {"id", "version", "hash"}:
        raise SkillPackageValidationError(
            [f"{name} must be a versioned binding / {name} 必须是版本化绑定"]
        )
    if not all(isinstance(value[field], str) and value[field] for field in ("id", "version", "hash")):
        raise SkillPackageValidationError(
            [f"{name} has empty binding fields / {name} 绑定字段为空"]
        )
    if _SHA256.fullmatch(str(value["hash"])) is None:
        raise SkillPackageValidationError(
            [f"{name} hash is invalid / {name} 哈希无效"]
        )
    return deepcopy(dict(value))


def _contract_binding(contract: Mapping[str, Any]) -> dict[str, str]:
    return {
        "id": str(contract["contract_id"]),
        "version": str(contract["contract_version"]),
        "hash": str(contract["contract_hash"]),
    }


def candidate_binding(candidate: Mapping[str, Any]) -> dict[str, str]:
    """Return the immutable candidate binding / 返回不可变候选绑定。"""

    return {
        "id": str(candidate["candidate_id"]),
        "version": str(candidate["candidate_version"]),
        "hash": str(candidate["candidate_hash"]),
    }


def manifest_binding(manifest: Mapping[str, Any]) -> dict[str, str]:
    """Return the exact Skill manifest binding / 返回精确 Skill 清单绑定。"""

    return {
        "id": str(manifest["skill_id"]),
        "version": str(manifest["skill_version"]),
        "hash": str(manifest["manifest_hash"]),
    }


def evaluation_binding(evaluation: Mapping[str, Any]) -> dict[str, str]:
    """Return the immutable evaluation binding / 返回不可变评估绑定。"""

    return {
        "id": str(evaluation["evaluation_id"]),
        "version": str(evaluation["evaluation_version"]),
        "hash": str(evaluation["evaluation_hash"]),
    }


def credential_binding(credential: Mapping[str, Any]) -> dict[str, str]:
    """Return the immutable credential binding / 返回不可变凭证绑定。"""

    return {
        "id": str(credential["credential_id"]),
        "version": str(credential["credential_version"]),
        "hash": str(credential["credential_hash"]),
    }


def build_skill_package_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Seal and validate one lifecycle contract / 封存并校验一个生命周期契约。"""

    sealed = build_artifact("skill_package_contract", contract)
    validate_skill_package_contract(sealed)
    return sealed


def build_skill_package_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Seal a recurrent solution nomination / 封存重复解法提名。"""

    sealed = build_artifact("skill_package_candidate", candidate)
    validate_skill_package_candidate(sealed)
    return sealed


def build_skill_package_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Seal one immutable TRIAL manifest / 封存一个不可变 TRIAL 清单。"""

    sealed = build_artifact("skill_package_manifest", manifest)
    validate_skill_package_manifest(sealed)
    return sealed


def build_skill_package_evaluation(evaluation: Mapping[str, Any]) -> dict[str, Any]:
    """Seal one exact-version evaluation / 封存一个精确版本评估。"""

    sealed = build_artifact("skill_package_evaluation", evaluation)
    validate_skill_package_evaluation(sealed)
    return sealed


def build_capability_credential(credential: Mapping[str, Any]) -> dict[str, Any]:
    """Seal one externally issued capability credential / 封存一个外部签发的能力凭证。"""

    sealed = build_artifact("capability_credential", credential)
    validate_capability_credential(sealed)
    return sealed


def build_skill_package_alias_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Seal an external compare-and-swap receipt / 封存外部比较并交换回执。"""

    sealed = build_artifact("skill_package_alias_receipt", receipt)
    validate_skill_package_alias_receipt(sealed)
    return sealed


def build_skill_package_reuse_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Seal one real reuse outcome receipt / 封存一个真实复用结果回执。"""

    sealed = build_artifact("skill_package_reuse_receipt", receipt)
    validate_skill_package_reuse_receipt(sealed)
    return sealed


def validate_skill_package_contract(contract: Mapping[str, Any]) -> None:
    """Validate authority and lifecycle invariants / 校验权限与生命周期不变量。"""

    validate_schema("skill_package_contract", contract)
    validate_artifact_hash("skill_package_contract", contract)
    errors: list[str] = []
    recurrence = contract["recurrence_policy"]
    if recurrence["minimum_verified_contributions"] > recurrence["minimum_distinct_runs"]:
        errors.append(
            "minimum verified contributions exceed distinct runs / 最少已验证贡献数超过不同运行数"
        )
    if set(contract["package_policy"]["required_core_sections"]) != set(
        SKILL_PACKAGE_REQUIRED_SECTIONS
    ):
        errors.append("required Skill core sections drifted / Skill 必需核心章节发生漂移")
    if tuple(contract["verification_policy"]["required_dimensions"]) != SKILL_PACKAGE_REQUIRED_DIMENSIONS:
        errors.append("verification dimensions or order drifted / 验证维度或顺序发生漂移")
    if tuple(contract["release_policy"]["required_stages"]) != SKILL_PACKAGE_RELEASE_STAGES:
        errors.append("release stages or order drifted / 发布阶段或顺序发生漂移")

    roles = contract["roles"]
    nominator = _binding_key(roles["nominator_binding"])
    packager = _binding_key(roles["packager_binding"])
    verifier = _binding_key(roles["verifier_binding"])
    issuer = _binding_key(roles["credential_issuer_binding"])
    publisher = _binding_key(roles["publisher_binding"])
    if verifier in {nominator, packager}:
        errors.append("verifier must be independent from nomination and packaging / 验证者必须独立于提名与打包")
    if issuer in {nominator, packager, verifier}:
        errors.append("credential issuer must be a separate authority / 凭证签发者必须是独立权限主体")
    if publisher in {nominator, packager, verifier, issuer}:
        errors.append("publisher must be separate from candidate, verification, and credential authorities / 发布者必须独立于候选、验证和凭证权限")
    _parse_datetime(contract["created_at"])
    if errors:
        raise SkillPackageValidationError(errors)


def validate_skill_package_candidate(
    candidate: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
) -> None:
    """Validate recurrent, externally successful source evidence / 校验重复且外部成功的来源证据。"""

    validate_schema("skill_package_candidate", candidate)
    validate_artifact_hash("skill_package_candidate", candidate)
    errors: list[str] = []
    occurrences = candidate["occurrences"]
    run_keys = _binding_set([item["run_binding"] for item in occurrences])
    environment_keys = _binding_set([item["environment_binding"] for item in occurrences])
    outcome_keys = _binding_set([item["external_outcome_binding"] for item in occurrences])
    if len(run_keys) != len(occurrences):
        errors.append("candidate occurrences must use distinct runs / 候选发生记录必须来自不同运行")
    if len(outcome_keys) != len(occurrences):
        errors.append("candidate occurrences must use distinct external outcomes / 候选发生记录必须使用不同外部结果")
    for occurrence in occurrences:
        if occurrence["problem_class"] != candidate["problem_class"]:
            errors.append("occurrence problem class differs from candidate / 发生记录问题类别与候选不一致")
        if occurrence["solution_signature"] != candidate["solution_signature"]:
            errors.append("occurrence solution signature differs from candidate / 发生记录解法签名与候选不一致")
        _parse_datetime(occurrence["observed_at"])
    if len(_binding_set(candidate["nomination_evidence_bindings"])) != len(
        candidate["nomination_evidence_bindings"]
    ):
        errors.append("nomination evidence must be unique / 提名证据必须唯一")
    _parse_datetime(candidate["created_at"])

    if contract is not None:
        validate_skill_package_contract(contract)
        target = contract["target"]
        policy = contract["recurrence_policy"]
        if candidate["skill_id"] != target["skill_id"] or candidate["proposed_skill_version"] != target["skill_version"]:
            errors.append("candidate targets a different Skill version / 候选指向不同 Skill 版本")
        if not _same_binding(candidate["nominator_binding"], contract["roles"]["nominator_binding"]):
            errors.append("candidate nominator is not contract-authorized / 候选提名者未获契约授权")
        if len(run_keys) < policy["minimum_distinct_runs"]:
            errors.append("candidate lacks distinct recurrence runs / 候选缺少不同复现运行")
        verified = sum(
            item["contribution_state"] == "verified_contribution"
            for item in occurrences
        )
        if verified < policy["minimum_verified_contributions"]:
            errors.append("candidate lacks verified solution contributions / 候选缺少已验证解法贡献")
        if len(environment_keys) < policy["minimum_distinct_environments"]:
            errors.append("candidate lacks required environment diversity / 候选缺少所需环境多样性")
    if errors:
        raise SkillPackageValidationError(errors)


def validate_skill_package_manifest(
    manifest: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    candidate: Mapping[str, Any] | None = None,
    reflection_assurance_binding: Mapping[str, Any] | None = None,
) -> None:
    """Validate bilingual packaging and supply-chain boundaries / 校验双语打包与供应链边界。"""

    validate_schema("skill_package_manifest", manifest)
    validate_artifact_hash("skill_package_manifest", manifest)
    errors: list[str] = []
    discovery = manifest["discovery"]
    for field in ("name_zh", "description_zh"):
        if _CJK.search(discovery[field]) is None:
            errors.append(f"{field} must contain Chinese content / {field} 必须包含中文内容")
    for field in ("use_cases_zh", "non_use_cases_zh"):
        if not all(_CJK.search(item) for item in discovery[field]):
            errors.append(f"{field} must be Chinese or bilingual / {field} 必须为中文或双语")
    parameterization = manifest["parameterization"]
    if parameterization["parameter_names"] and not parameterization["parameter_origin_bindings"]:
        errors.append("parameterized values require origin bindings / 参数化值必须绑定来源")
    execution_tools = _binding_set(manifest["execution"]["tool_contract_bindings"])
    dependency_tools = _binding_set(manifest["dependencies"]["tool_contract_bindings"])
    if execution_tools != dependency_tools:
        errors.append("execution and dependency tool inventories differ / 执行与依赖工具清单不一致")
    if manifest["execution"]["side_effect_class"] in {"reversible_write", "sensitive_write"} and manifest["execution"]["rollback_binding"] is None:
        errors.append("reversible or sensitive writes require rollback binding / 可逆或敏感写入必须绑定回滚")
    if any(item["trust_state"] == "untrusted" for item in manifest["resources"]) and manifest["execution"]["side_effect_class"] not in {"none", "readonly"}:
        errors.append("untrusted resources cannot receive write authority / 不可信资源不得获得写权限")
    package_content = manifest["package_content_binding"]
    if package_content["id"] != manifest["package_id"] or package_content["version"] != manifest["skill_version"]:
        errors.append("package content binding must identify the exact package and Skill version / 技能包内容绑定必须标识精确包与 Skill 版本")
    section_names = [item["section"] for item in manifest["core_sections"]]
    if len(set(section_names)) != len(section_names) or set(section_names) != set(
        SKILL_PACKAGE_REQUIRED_SECTIONS
    ):
        errors.append("manifest must bind every required core section exactly once / 清单必须对每个必需核心章节精确绑定一次")
    skill_files = [
        item
        for item in manifest["resources"]
        if item["path"].replace("\\", "/").split("/")[-1].lower() == "skill.md"
    ]
    if len(skill_files) != 1:
        errors.append("manifest must inventory exactly one SKILL.md / 清单必须且只能盘点一个 SKILL.md")
    elif skill_files[0]["digest"] != package_content["hash"]:
        errors.append("SKILL.md digest differs from package content binding / SKILL.md 摘要与技能包内容绑定不一致")
    elif skill_files[0]["trust_state"] == "untrusted":
        errors.append("the normative SKILL.md cannot remain untrusted / 规范 SKILL.md 不得保持不可信状态")
    _parse_datetime(manifest["created_at"])

    if contract is not None:
        validate_skill_package_contract(contract)
        target = contract["target"]
        if manifest["skill_id"] != target["skill_id"] or manifest["skill_version"] != target["skill_version"]:
            errors.append("manifest targets a different Skill version / 清单指向不同 Skill 版本")
        if not _same_binding(manifest["governance_policy_binding"], contract["governance_policy_binding"]):
            errors.append("manifest governance binding differs from contract / 清单治理绑定与契约不一致")
    if candidate is not None:
        validate_skill_package_candidate(candidate, contract=contract)
        if not _same_binding(manifest["candidate_binding"], candidate_binding(candidate)):
            errors.append("manifest binds a different candidate / 清单绑定了不同候选")
        candidate_runs = _binding_set(
            [item["run_binding"] for item in candidate["occurrences"]]
        )
        manifest_runs = _binding_set(manifest["source"]["source_run_bindings"])
        if manifest_runs != candidate_runs:
            errors.append("manifest source runs differ from candidate evidence / 清单来源运行与候选证据不一致")
    if reflection_assurance_binding is not None and not _same_binding(
        manifest["reflection_assurance_binding"], reflection_assurance_binding
    ):
        errors.append("manifest binds a different reflection assurance / 清单绑定了不同反思保证")
    if errors:
        raise SkillPackageValidationError(errors)


def validate_skill_package_evaluation(
    evaluation: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
) -> None:
    """Validate independently reproducible five-dimension evaluation / 校验可独立复算的五维评估。"""

    validate_schema("skill_package_evaluation", evaluation)
    validate_artifact_hash("skill_package_evaluation", evaluation)
    errors: list[str] = []
    dimensions = evaluation["dimensions"]
    names = [item["dimension"] for item in dimensions]
    if len(set(names)) != len(names):
        errors.append("evaluation dimensions must be unique / 评估维度必须唯一")
    for item in dimensions:
        if item["passed_cases"] > item["total_cases"]:
            errors.append(f"passed cases exceed total for {item['dimension']} / {item['dimension']} 通过数超过总数")
        expected_status = "passed" if item["passed_cases"] == item["total_cases"] else "failed"
        if item["status"] not in {expected_status, "incomplete"}:
            errors.append(f"dimension verdict cannot be reproduced for {item['dimension']} / {item['dimension']} 维度裁定无法重算")
    if _parse_datetime(evaluation["completed_at"]) < _parse_datetime(evaluation["started_at"]):
        errors.append("evaluation completed before it started / 评估完成时间早于开始时间")

    if contract is not None:
        validate_skill_package_contract(contract)
        if not _same_binding(evaluation["contract_binding"], _contract_binding(contract)):
            errors.append("evaluation binds a different lifecycle contract / 评估绑定了不同生命周期契约")
        if not _same_binding(evaluation["evaluator_binding"], contract["roles"]["verifier_binding"]):
            errors.append("evaluation actor is not the independent verifier / 评估主体不是独立验证者")
        required = tuple(contract["verification_policy"]["required_dimensions"])
        if evaluation["overall_status"] == "passed":
            if tuple(names) != required:
                errors.append("passing evaluation lacks the exact five dimensions / 通过评估缺少精确五维")
            minimum = contract["verification_policy"]["minimum_cases_per_dimension"]
            for item in dimensions:
                if item["total_cases"] < minimum or item["status"] != "passed":
                    errors.append(f"passing evaluation has insufficient {item['dimension']} cases / 通过评估的 {item['dimension']} 用例不足")
                if contract["verification_policy"]["require_counterexample"] and not item["counterexample_checked"]:
                    errors.append(f"{item['dimension']} lacks counterexample check / {item['dimension']} 缺少反例检查")
                if contract["verification_policy"]["require_failure_path"] and not item["failure_path_checked"]:
                    errors.append(f"{item['dimension']} lacks failure-path check / {item['dimension']} 缺少失败路径检查")
            if not evaluation["regression_free"]:
                errors.append("passing evaluation contains a regression / 通过评估包含回归")
            if evaluation["validator_gaming_detected"]:
                errors.append("validator gaming blocks verification / 验证器投机阻断验证")
    if manifest is not None:
        validate_skill_package_manifest(manifest, contract=contract)
        if not _same_binding(evaluation["manifest_binding"], manifest_binding(manifest)):
            errors.append("evaluation targets a different manifest / 评估指向不同清单")
    if errors:
        raise SkillPackageValidationError(errors)


def validate_capability_credential(
    credential: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
    evaluation: Mapping[str, Any] | None = None,
    previous_credential: Mapping[str, Any] | None | object = _LINEAGE_UNSET,
) -> None:
    """Validate exact external qualification binding / 校验精确外部资格绑定。"""

    validate_schema("capability_credential", credential)
    validate_artifact_hash("capability_credential", credential)
    errors: list[str] = []
    issued = _parse_datetime(credential["issued_at"])
    if credential["expires_at"] is not None and _parse_datetime(credential["expires_at"]) <= issued:
        errors.append("credential expires at or before issuance / 凭证在签发时或之前过期")
    if contract is not None:
        if not _same_binding(credential["contract_binding"], _contract_binding(contract)):
            errors.append("credential binds a different contract / 凭证绑定了不同契约")
        if not _same_binding(credential["issuer_binding"], contract["roles"]["credential_issuer_binding"]):
            errors.append("credential issuer is not authorized / 凭证签发者未获授权")
        if not _same_binding(credential["policy_binding"], contract["governance_policy_binding"]):
            errors.append("credential policy binding drifted / 凭证策略绑定漂移")
    if manifest is not None:
        if not _same_binding(credential["manifest_binding"], manifest_binding(manifest)):
            errors.append("credential binds a different manifest / 凭证绑定了不同清单")
        manifest_tools = _binding_set(manifest["dependencies"]["tool_contract_bindings"])
        if _binding_set(credential["tool_contract_bindings"]) != manifest_tools:
            errors.append("credential tool scope differs from manifest / 凭证工具范围与清单不一致")
        if _binding_set(credential["runtime_bindings"]) != _binding_set(
            manifest["dependencies"]["runtime_bindings"]
        ):
            errors.append("credential runtime scope differs from manifest / 凭证运行时范围与清单不一致")
        if set(credential["permission_scopes"]) != set(manifest["execution"]["permission_scopes"]):
            errors.append("credential permission scope differs from manifest / 凭证权限范围与清单不一致")
    if evaluation is not None:
        if evaluation["overall_status"] != "passed":
            errors.append("credential requires a passed evaluation / 凭证要求评估通过")
        if not _same_binding(credential["evaluation_binding"], evaluation_binding(evaluation)):
            errors.append("credential binds a different evaluation / 凭证绑定了不同评估")
        if not _same_binding(credential["environment_binding"], evaluation["environment_binding"]):
            errors.append("credential environment differs from evaluation / 凭证环境与评估不一致")
        if issued < _parse_datetime(evaluation["completed_at"]):
            errors.append("credential was issued before evaluation completion / 凭证在评估完成前签发")
    # A standalone artifact validator cannot know whether a credential is the
    # first issuance or a replacement. The lifecycle session always passes an
    # explicit ``None`` or the previous credential, making lineage mandatory at
    # the authority boundary. / 单独制品校验器无法知道凭证是首次签发
    # 还是替换签发；生命周期会话会显式传入 ``None`` 或上一凭证，因而在
    # 权限边界强制谱系校验。
    if previous_credential is not _LINEAGE_UNSET:
        if previous_credential is None:
            if credential["supersedes_credential_binding"] is not None:
                errors.append("first credential cannot supersede an unknown credential / 首个凭证不得替代未知凭证")
        elif not _same_binding(
            credential["supersedes_credential_binding"] or {},
            credential_binding(previous_credential),
        ):
            errors.append("replacement credential does not supersede the previous credential / 替换凭证未指向上一凭证")
    if errors:
        raise SkillPackageValidationError(errors)


def validate_skill_package_alias_receipt(
    receipt: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    manifest: Mapping[str, Any] | None = None,
    credential: Mapping[str, Any] | None = None,
) -> None:
    """Validate atomic exact-version alias evidence / 校验原子精确版本别名证据。"""

    validate_schema("skill_package_alias_receipt", receipt)
    validate_artifact_hash("skill_package_alias_receipt", receipt)
    errors: list[str] = []
    if receipt["new_revision"] != receipt["expected_revision"] + 1:
        errors.append("alias revision is not a compare-and-swap successor / 别名修订不是比较并交换的后继")
    _parse_datetime(receipt["switched_at"])
    if contract is not None:
        if receipt["alias"] != contract["target"]["route_alias"]:
            errors.append("alias receipt targets a different route alias / 别名回执指向不同路由别名")
        if not _same_binding(receipt["publisher_binding"], contract["roles"]["publisher_binding"]):
            errors.append("alias publisher is not authorized / 别名发布者未获授权")
    if manifest is not None and not _same_binding(receipt["next_manifest_binding"], manifest_binding(manifest)):
        errors.append("alias switched to a different manifest / 别名切换到不同清单")
    if credential is not None and not _same_binding(receipt["credential_binding"], credential_binding(credential)):
        errors.append("alias switched with a different credential / 别名使用了不同凭证")
    if errors:
        raise SkillPackageValidationError(errors)


def validate_skill_package_reuse_receipt(
    receipt: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any] | None = None,
    credential: Mapping[str, Any] | None = None,
    contract: Mapping[str, Any] | None = None,
) -> None:
    """Validate a real, outcome-bound production use / 校验真实且绑定结果的生产复用。"""

    validate_schema("skill_package_reuse_receipt", receipt)
    validate_artifact_hash("skill_package_reuse_receipt", receipt)
    errors: list[str] = []
    outcome = receipt["external_outcome"]
    if outcome["status"] in {"success", "failure"} and outcome["binding"] is None:
        errors.append("determined external outcome requires a binding / 已判定外部结果必须有绑定")
    if outcome["status"] in {"pending", "unknown"} and outcome["binding"] is not None:
        errors.append("pending or unknown outcome cannot carry a definitive binding / 待定或未知结果不得携带确定绑定")
    route_selected = _parse_datetime(receipt["route_selected_at"])
    run_completed = _parse_datetime(receipt["run_completed_at"])
    observed = _parse_datetime(receipt["observed_at"])
    if not route_selected <= run_completed <= observed:
        errors.append("reuse time order must be route, completion, then outcome observation / 复用时间顺序必须是路由、完成、再结果观察")
    if contract is not None:
        validate_skill_package_contract(contract)
        maximum_lag = contract["reuse_policy"]["maximum_outcome_lag_seconds"]
        if outcome["status"] in {"success", "failure"} and (
            observed - run_completed
        ).total_seconds() > maximum_lag:
            errors.append("determined outcome exceeds the sealed outcome-lag window / 已判定结果超出封存结果滞后窗口")
    if manifest is not None and not _same_binding(receipt["manifest_binding"], manifest_binding(manifest)):
        errors.append("reuse receipt binds a different manifest / 复用回执绑定了不同清单")
    if credential is not None:
        if not _same_binding(receipt["credential_binding"], credential_binding(credential)):
            errors.append("reuse receipt binds a different credential / 复用回执绑定了不同凭证")
        if observed < _parse_datetime(credential["issued_at"]):
            errors.append("reuse predates credential issuance / 复用早于凭证签发")
        if credential["expires_at"] is not None and observed > _parse_datetime(credential["expires_at"]):
            errors.append("reuse used an expired credential / 复用使用了过期凭证")
    if errors:
        raise SkillPackageValidationError(errors)


def validate_skill_package_event(
    event: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
) -> None:
    """Validate one immutable lifecycle event / 校验一个不可变生命周期事件。"""

    validate_schema("skill_package_event", event)
    validate_artifact_hash("skill_package_event", event)
    errors: list[str] = []
    _parse_datetime(event["occurred_at"])
    if contract is not None:
        if event["lifecycle_id"] != contract["lifecycle_id"]:
            errors.append("event lifecycle ID differs from contract / 事件生命周期 ID 与契约不一致")
        if not _same_binding(event["contract_binding"], _contract_binding(contract)):
            errors.append("event contract binding differs / 事件契约绑定不一致")
        actor_roles = {
            "skill.candidate_nominated": "nominator_binding",
            "skill.distillation_completed": "packager_binding",
            "skill.registered_trial": "packager_binding",
            "skill.verification_started": "verifier_binding",
            "skill.verification_completed": "verifier_binding",
            "skill.credential_issued": "credential_issuer_binding",
            "skill.promoted_verified": "lifecycle_owner_binding",
            "skill.release_stage_changed": "publisher_binding",
            "skill.route_alias_switched": "publisher_binding",
            "skill.reuse_recorded": "lifecycle_owner_binding",
            "skill.credential_suspended": "lifecycle_owner_binding",
            "skill.credential_revoked": "lifecycle_owner_binding",
            "skill.demoted_trial": "lifecycle_owner_binding",
            "skill.reverification_started": "lifecycle_owner_binding",
            "skill.retired": "lifecycle_owner_binding",
            "skill.archived": "lifecycle_owner_binding",
        }
        role = actor_roles[event["event_type"]]
        if not _same_binding(event["actor_binding"], contract["roles"][role]):
            errors.append(f"event actor lacks {role} authority / 事件主体缺少 {role} 权限")
    if errors:
        raise SkillPackageValidationError(errors)


def validate_skill_package_event_stream(
    events: Sequence[Mapping[str, Any]],
    *,
    contract: Mapping[str, Any] | None = None,
) -> None:
    """Replay event identity, hash chain, and state continuity / 重放事件标识、哈希链与状态连续性。"""

    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        raise SkillPackageValidationError(["event stream must be a sequence / 事件流必须是序列"])
    errors: list[str] = []
    previous_hash: str | None = None
    previous_time: datetime | None = None
    qualification: str | None = None
    release: str | None = None
    seen_types: list[str] = []
    for index, event in enumerate(events, start=1):
        try:
            validate_skill_package_event(event, contract=contract)
        except SkillPackageValidationError as exc:
            errors.extend(f"event {index}: {item}" for item in exc.errors)
            continue
        if event["sequence"] != index:
            errors.append(f"event sequence must be contiguous at {index} / 事件序号在 {index} 处不连续")
        if event["previous_event_hash"] != previous_hash:
            errors.append(f"event hash chain breaks at {index} / 事件哈希链在 {index} 处断裂")
        event_time = _parse_datetime(event["occurred_at"])
        if previous_time is not None and event_time < previous_time:
            errors.append(f"event time moves backward at {index} / 事件时间在 {index} 处倒退")
        if qualification is not None and event["qualification_before"] != qualification:
            errors.append(f"qualification state is discontinuous at {index} / 资格状态在 {index} 处不连续")
        if release is not None and event["release_before"] != release:
            errors.append(f"release state is discontinuous at {index} / 发布状态在 {index} 处不连续")
        qualification = event["qualification_after"]
        release = event["release_after"]
        previous_hash = event["event_hash"]
        previous_time = event_time
        seen_types.append(event["event_type"])

        event_type = event["event_type"]
        qb, qa = event["qualification_before"], event["qualification_after"]
        rb, ra = event["release_before"], event["release_after"]
        if event_type == "skill.registered_trial" and (qb, qa) != ("UNREGISTERED", "TRIAL"):
            errors.append("TRIAL registration has an invalid qualification transition / TRIAL 注册资格转换无效")
        if event_type == "skill.promoted_verified" and (qb, qa) != ("TRIAL", "VERIFIED"):
            errors.append("VERIFIED promotion has an invalid qualification transition / VERIFIED 晋升资格转换无效")
        if event_type == "skill.demoted_trial" and (qb, qa) != ("VERIFIED", "TRIAL"):
            errors.append("TRIAL demotion has an invalid qualification transition / TRIAL 降级资格转换无效")
        if event_type == "skill.release_stage_changed" and (rb, ra) not in {
            ("unpublished", "shadow"),
            ("suspended", "shadow"),
            ("shadow", "limited"),
            ("limited", "production"),
        }:
            errors.append("release stage transition is invalid / 发布阶段转换无效")
        if event_type == "skill.credential_suspended" and ra != "suspended":
            errors.append("credential suspension must stop release traffic / 凭证暂停必须停止发布流量")
        if event_type == "skill.reuse_recorded" and (rb != "production" or ra != "production"):
            errors.append("real reuse is legal only in production / 真实复用仅可发生于生产态")
        if event_type == "skill.retired" and qa != "RETIRED":
            errors.append("retirement must remove qualification / 退役必须移除资格")
        if event_type == "skill.archived" and (rb, ra) != ("retired", "archived"):
            errors.append("archive requires retired release state / 归档要求已退役发布态")

    if events and seen_types[0] != "skill.candidate_nominated":
        errors.append("lifecycle must start with candidate nomination / 生命周期必须从候选提名开始")
    for index, event_type in enumerate(seen_types):
        if event_type == "skill.reverification_started":
            if index < 2 or seen_types[index - 2 : index] != [
                "skill.credential_suspended",
                "skill.demoted_trial",
            ]:
                errors.append("re-verification must suspend then demote before starting / 复验开始前必须先暂停凭证再降级")
        if event_type == "skill.route_alias_switched" and (
            index == 0 or seen_types[index - 1] != "skill.release_stage_changed"
        ):
            errors.append("alias switch must follow the production stage transition / 别名切换必须紧随生产阶段转换")
    if errors:
        raise SkillPackageValidationError(errors)


def build_skill_lifecycle_reflection_guard(
    reflection_contract: Mapping[str, Any],
    *,
    events_provider: Callable[[], Sequence[Mapping[str, Any]]],
    observations_provider: Callable[[], Sequence[Mapping[str, Any]]],
) -> Callable[[str, Mapping[str, Any]], Mapping[str, Any]]:
    """Bind Skill nomination to a real accepted reflection candidate / 将 Skill 提名绑定到真实已接受反思候选。"""

    try:
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
    admission = contract["admission"]
    if admission["eligibility"] != "admitted" or admission["route"] != "skill_lifecycle":
        raise SkillPackageAuthorizationError(
            "shared reflection contract must be admitted to skill_lifecycle / 共享反思契约必须准入 skill_lifecycle"
        )
    expected_contract_binding = _contract_binding(contract)

    def guard(stage: str, request: Mapping[str, Any]) -> Mapping[str, Any]:
        if stage != "candidate_nomination":
            raise SkillPackageAuthorizationError(
                f"unknown reflection guard stage: {stage} / 未知反思闸阶段: {stage}"
            )
        if request.get("reflection_contract_binding") != expected_contract_binding:
            raise SkillPackageAuthorizationError(
                "Skill lifecycle binds a different reflection contract / Skill 生命周期绑定了不同反思契约"
            )
        candidate = request.get("candidate")
        if not isinstance(candidate, Mapping):
            raise SkillPackageAuthorizationError("candidate is missing / 缺少候选")
        events = [deepcopy(dict(item)) for item in events_provider()]
        observations = [deepcopy(dict(item)) for item in observations_provider()]
        validate_reflection_event_stream(events, contract=contract)
        matches: list[Mapping[str, Any]] = []
        for observation in observations:
            validate_reflection_round_observation(observation, contract=contract, events=events)
            learning = observation.get("learning_candidate")
            if not isinstance(learning, Mapping):
                continue
            if _same_binding(
                learning.get("candidate_binding", {}),
                candidate.get("reflection_candidate_binding", {}),
            ):
                matches.append(observation)
        if len(matches) != 1:
            raise SkillPackageAuthorizationError(
                "exactly one reflection observation must nominate the candidate / 必须且只能有一个反思观察包提名候选"
            )
        observation = matches[0]
        learning = observation["learning_candidate"]
        if observation["outcome"] != "accepted" or not observation["terminal"]:
            raise SkillPackageAuthorizationError("source reflection is not accepted and closed / 来源反思未接受并闭合")
        if learning["target"] != "skill" or learning["decision"] != "candidate":
            raise SkillPackageAuthorizationError(
                "reflection may nominate only a Skill candidate; it cannot grant production promotion / 反思只能提名 Skill 候选，不能授予生产晋升"
            )
        assurance = {
            "reflection_contract_binding": expected_contract_binding,
            "observation_binding": {
                "id": observation["observation_id"],
                "version": observation["schema_version"],
                "hash": observation["observation_hash"],
            },
            "source_round_id": learning["source_round_id"],
            "source_subject_binding": learning["source_subject_binding"],
            "candidate_binding": learning["candidate_binding"],
            "round_evidence_bindings": learning["round_evidence_bindings"],
        }
        return {
            "id": f"{contract['reflection_id']}:skill-candidate-assurance:{learning['source_round_id']}",
            "version": "1.0.0",
            "hash": artifact_fingerprint(assurance),
        }

    return guard


class SkillPackageSession:
    """Deterministic coordinator for one immutable Skill version / 一个不可变 Skill 版本的确定性协调器。"""

    def __init__(
        self,
        contract: Mapping[str, Any],
        *,
        reflection_guard: Callable[[str, Mapping[str, Any]], Mapping[str, Any]],
    ) -> None:
        validate_skill_package_contract(contract)
        if not callable(reflection_guard):
            raise TypeError("reflection_guard must be callable")
        self._contract = deepcopy(dict(contract))
        self._reflection_guard = reflection_guard
        self._stage = SkillPackageStage.INITIALIZED
        self._qualification = SkillQualificationState.UNREGISTERED
        self._release = SkillReleaseState.UNPUBLISHED
        self._candidate: dict[str, Any] | None = None
        self._reflection_assurance: dict[str, str] | None = None
        self._distillation: dict[str, Any] | None = None
        self._manifest: dict[str, Any] | None = None
        self._verification_request: dict[str, Any] | None = None
        self._evaluations: list[dict[str, Any]] = []
        self._credentials: list[dict[str, Any]] = []
        self._credential_active = False
        self._alias_receipts: list[dict[str, Any]] = []
        self._reuse_receipts: list[dict[str, Any]] = []
        self._events: list[dict[str, Any]] = []

    @property
    def stage(self) -> SkillPackageStage:
        return self._stage

    @property
    def qualification_state(self) -> SkillQualificationState:
        return self._qualification

    @property
    def release_state(self) -> SkillReleaseState:
        return self._release

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._events))

    @property
    def reuse_receipts(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._reuse_receipts))

    def _require_stage(self, *stages: SkillPackageStage) -> None:
        if self._stage not in stages:
            allowed = ", ".join(stage.value for stage in stages)
            raise SkillPackageStateError(
                f"stage {self._stage.value} is not one of {allowed} / 当前阶段不允许该操作"
            )

    def _require_actor(self, role: str, actor: Mapping[str, Any]) -> dict[str, str]:
        normalized = _require_binding(actor, name=role)
        expected = self._contract["roles"][role]
        if not _same_binding(normalized, expected):
            raise SkillPackageAuthorizationError(
                f"actor does not match {role} / 主体不匹配 {role}"
            )
        return normalized

    def _current_manifest_binding(self) -> dict[str, str] | None:
        return manifest_binding(self._manifest) if self._manifest is not None else None

    def _current_credential_binding(self) -> dict[str, str] | None:
        return credential_binding(self._credentials[-1]) if self._credentials else None

    def _require_current_credential_at(self, occurred_at: str) -> None:
        """Fail when the latest credential is inactive or outside its window / 最新凭证非活跃或超出窗口时阻断。"""

        if not self._credentials or not self._credential_active:
            raise SkillPackageAuthorizationError("credential is not active / 凭证未激活")
        credential = self._credentials[-1]
        moment = _parse_datetime(occurred_at)
        if moment < _parse_datetime(credential["issued_at"]):
            raise SkillPackageAuthorizationError("credential is not yet valid / 凭证尚未生效")
        if credential["expires_at"] is not None and moment > _parse_datetime(
            credential["expires_at"]
        ):
            raise SkillPackageAuthorizationError("credential is expired / 凭证已过期")

    def _make_event(
        self,
        event_type: str,
        *,
        actor: Mapping[str, Any],
        occurred_at: str,
        payload: Mapping[str, Any],
        qualification_before: SkillQualificationState | None = None,
        qualification_after: SkillQualificationState | None = None,
        release_before: SkillReleaseState | None = None,
        release_after: SkillReleaseState | None = None,
        manifest_record: Mapping[str, Any] | None = None,
        credential_record: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        _parse_datetime(occurred_at)
        sequence = len(self._events) + 1
        event = {
            "schema_version": "1.0.0",
            "event_id": f"{self._contract['lifecycle_id']}:event:{sequence:04d}",
            "event_type": event_type,
            "lifecycle_id": self._contract["lifecycle_id"],
            "sequence": sequence,
            "occurred_at": occurred_at,
            "idempotency_key": f"skill-package:{self._contract['lifecycle_id']}:{sequence:04d}",
            "previous_event_hash": self._events[-1]["event_hash"] if self._events else None,
            "contract_binding": _contract_binding(self._contract),
            "manifest_binding": (
                manifest_binding(manifest_record)
                if manifest_record is not None
                else self._current_manifest_binding()
            ),
            "credential_binding": (
                credential_binding(credential_record)
                if credential_record is not None
                else self._current_credential_binding()
            ),
            "actor_binding": deepcopy(dict(actor)),
            "qualification_before": (qualification_before or self._qualification).value,
            "qualification_after": (qualification_after or self._qualification).value,
            "release_before": (release_before or self._release).value,
            "release_after": (release_after or self._release).value,
            "payload": deepcopy(dict(payload)),
        }
        return build_artifact("skill_package_event", event)

    def _append(self, *events: Mapping[str, Any]) -> None:
        prospective = self._events + [deepcopy(dict(event)) for event in events]
        validate_skill_package_event_stream(prospective, contract=self._contract)
        self._events = prospective

    def nominate_candidate(
        self,
        candidate: Mapping[str, Any],
        *,
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Admit a recurrent solution only as a candidate / 仅将重复解法准入为候选。"""

        self._require_stage(SkillPackageStage.INITIALIZED)
        actor = self._require_actor("nominator_binding", actor_binding)
        validate_skill_package_candidate(candidate, contract=self._contract)
        assurance = self._reflection_guard(
            "candidate_nomination",
            {
                "reflection_contract_binding": deepcopy(
                    self._contract["reflection_contract_binding"]
                ),
                "candidate": deepcopy(dict(candidate)),
            },
        )
        assurance_binding = _require_binding(assurance, name="reflection_assurance")
        event = self._make_event(
            "skill.candidate_nominated",
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "candidate_binding": candidate_binding(candidate),
                "reflection_assurance_binding": assurance_binding,
                "distinct_run_count": len(
                    _binding_set([item["run_binding"] for item in candidate["occurrences"]])
                ),
                "verified_contribution_count": sum(
                    item["contribution_state"] == "verified_contribution"
                    for item in candidate["occurrences"]
                ),
            },
        )
        self._append(event)
        self._candidate = deepcopy(dict(candidate))
        self._reflection_assurance = assurance_binding
        self._stage = SkillPackageStage.CANDIDATE
        return deepcopy(event)

    def record_distillation(
        self,
        distillation: Mapping[str, Any],
        *,
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Record stable steps, parameters, and unresolved assumptions / 记录稳定步骤、参数和未确认假设。"""

        self._require_stage(SkillPackageStage.CANDIDATE)
        actor = self._require_actor("packager_binding", actor_binding)
        required = {
            "distillation_binding",
            "stable_step_ids",
            "parameter_names",
            "hidden_assumptions",
            "boundary_evidence_bindings",
        }
        if not isinstance(distillation, Mapping) or set(distillation) != required:
            raise SkillPackageValidationError(
                [f"distillation fields must equal {sorted(required)} / 蒸馏字段不完整"]
            )
        normalized = deepcopy(dict(distillation))
        _require_binding(normalized["distillation_binding"], name="distillation_binding")
        for field in ("stable_step_ids", "parameter_names", "hidden_assumptions"):
            values = normalized[field]
            if not isinstance(values, list) or any(
                not isinstance(value, str) or not value.strip() for value in values
            ) or len(values) != len(set(values)):
                raise SkillPackageValidationError(
                    [f"{field} must be a unique string list / {field} 必须是唯一字符串列表"]
                )
        if not normalized["stable_step_ids"]:
            raise SkillPackageValidationError(["distillation needs stable steps / 蒸馏需要稳定步骤"])
        evidence = normalized["boundary_evidence_bindings"]
        if not isinstance(evidence, list) or not evidence:
            raise SkillPackageValidationError(["distillation needs boundary evidence / 蒸馏需要边界证据"])
        for index, binding in enumerate(evidence):
            _require_binding(binding, name=f"boundary_evidence_bindings[{index}]")
        if len(_binding_set(evidence)) != len(evidence):
            raise SkillPackageValidationError(["distillation evidence must be unique / 蒸馏证据必须唯一"])
        event = self._make_event(
            "skill.distillation_completed",
            actor=actor,
            occurred_at=occurred_at,
            payload=normalized,
        )
        self._append(event)
        self._distillation = normalized
        self._stage = SkillPackageStage.DISTILLED
        return deepcopy(event)

    def register_trial(
        self,
        manifest: Mapping[str, Any],
        *,
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Register every source as TRIAL, never directly VERIFIED / 所有来源统一注册为 TRIAL，绝不直接 VERIFIED。"""

        self._require_stage(SkillPackageStage.DISTILLED)
        actor = self._require_actor("packager_binding", actor_binding)
        assert self._candidate is not None and self._reflection_assurance is not None
        assert self._distillation is not None
        validate_skill_package_manifest(
            manifest,
            contract=self._contract,
            candidate=self._candidate,
            reflection_assurance_binding=self._reflection_assurance,
        )
        if not _same_binding(
            manifest["distillation_binding"],
            self._distillation["distillation_binding"],
        ):
            raise SkillPackageValidationError(
                ["manifest binds a different distillation / 清单绑定了不同蒸馏记录"]
            )
        event = self._make_event(
            "skill.registered_trial",
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "candidate_binding": candidate_binding(self._candidate),
                "distillation_binding": self._distillation["distillation_binding"],
                "qualification_state": "TRIAL",
            },
            qualification_after=SkillQualificationState.TRIAL,
            manifest_record=manifest,
        )
        self._append(event)
        self._manifest = deepcopy(dict(manifest))
        self._qualification = SkillQualificationState.TRIAL
        self._stage = SkillPackageStage.TRIAL
        return deepcopy(event)

    def start_verification(
        self,
        *,
        evaluation_suite_binding: Mapping[str, Any],
        environment_binding: Mapping[str, Any],
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Start independent verification of the exact manifest / 启动精确清单的独立验证。"""

        self._require_stage(SkillPackageStage.TRIAL, SkillPackageStage.REVERIFYING)
        actor = self._require_actor("verifier_binding", actor_binding)
        suite = _require_binding(evaluation_suite_binding, name="evaluation_suite_binding")
        environment = _require_binding(environment_binding, name="environment_binding")
        event_type = "skill.verification_started"
        event = self._make_event(
            event_type,
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "evaluation_suite_binding": suite,
                "environment_binding": environment,
                "reverification": self._stage is SkillPackageStage.REVERIFYING,
            },
        )
        self._append(event)
        self._verification_request = {
            "evaluation_suite_binding": suite,
            "environment_binding": environment,
            "started_at": occurred_at,
        }
        self._stage = SkillPackageStage.VERIFYING
        return deepcopy(event)

    def complete_verification(
        self,
        evaluation: Mapping[str, Any],
        *,
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Record a complete external evaluation / 记录完整外部评估。"""

        self._require_stage(SkillPackageStage.VERIFYING)
        actor = self._require_actor("verifier_binding", actor_binding)
        assert self._manifest is not None
        validate_skill_package_evaluation(
            evaluation,
            contract=self._contract,
            manifest=self._manifest,
        )
        if self._verification_request is None:
            raise SkillPackageStateError("verification request is missing / 缺少验证请求")
        if not _same_binding(
            evaluation["evaluation_suite_binding"],
            self._verification_request["evaluation_suite_binding"],
        ):
            raise SkillPackageValidationError(
                ["evaluation suite differs from the started verification / 评估套件与已启动验证不一致"]
            )
        if not _same_binding(
            evaluation["environment_binding"],
            self._verification_request["environment_binding"],
        ):
            raise SkillPackageValidationError(
                ["evaluation environment differs from the started verification / 评估环境与已启动验证不一致"]
            )
        if evaluation["started_at"] != self._verification_request["started_at"]:
            raise SkillPackageValidationError(
                ["evaluation start time differs from the verification event / 评估开始时间与验证事件不一致"]
            )
        if _parse_datetime(occurred_at) < _parse_datetime(evaluation["completed_at"]):
            raise SkillPackageValidationError(
                ["verification completion event predates the evaluation / 验证完成事件早于评估完成"]
            )
        event = self._make_event(
            "skill.verification_completed",
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "evaluation_binding": evaluation_binding(evaluation),
                "overall_status": evaluation["overall_status"],
                "dimensions": [item["dimension"] for item in evaluation["dimensions"]],
                "regression_free": evaluation["regression_free"],
                "validator_gaming_detected": evaluation["validator_gaming_detected"],
            },
        )
        self._append(event)
        self._evaluations.append(deepcopy(dict(evaluation)))
        self._verification_request = None
        self._stage = (
            SkillPackageStage.VERIFICATION_PASSED
            if evaluation["overall_status"] == "passed"
            else SkillPackageStage.TRIAL
        )
        return deepcopy(event)

    def issue_credential(
        self,
        credential: Mapping[str, Any],
        *,
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Accept only an independently issued exact credential / 只接受独立签发的精确凭证。"""

        self._require_stage(SkillPackageStage.VERIFICATION_PASSED)
        actor = self._require_actor("credential_issuer_binding", actor_binding)
        assert self._manifest is not None and self._evaluations
        previous = self._credentials[-1] if self._credentials else None
        validate_capability_credential(
            credential,
            contract=self._contract,
            manifest=self._manifest,
            evaluation=self._evaluations[-1],
            previous_credential=previous,
        )
        if _parse_datetime(occurred_at) < _parse_datetime(credential["issued_at"]):
            raise SkillPackageValidationError(
                ["credential event predates issuance / 凭证事件早于签发时间"]
            )
        event = self._make_event(
            "skill.credential_issued",
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "credential_binding": credential_binding(credential),
                "evaluation_binding": evaluation_binding(self._evaluations[-1]),
                "supersedes_credential_binding": credential["supersedes_credential_binding"],
            },
            credential_record=credential,
        )
        self._append(event)
        self._credentials.append(deepcopy(dict(credential)))
        self._credential_active = True
        self._stage = SkillPackageStage.CREDENTIALED
        return deepcopy(event)

    def promote_verified(
        self,
        *,
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Promote only after a current credential exists / 仅在当前凭证存在后晋升。"""

        self._require_stage(SkillPackageStage.CREDENTIALED)
        actor = self._require_actor("lifecycle_owner_binding", actor_binding)
        self._require_current_credential_at(occurred_at)
        event = self._make_event(
            "skill.promoted_verified",
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "evaluation_binding": evaluation_binding(self._evaluations[-1]),
                "credential_binding": credential_binding(self._credentials[-1]),
            },
            qualification_after=SkillQualificationState.VERIFIED,
        )
        self._append(event)
        self._qualification = SkillQualificationState.VERIFIED
        self._stage = SkillPackageStage.VERIFIED
        return deepcopy(event)

    def advance_release_stage(
        self,
        stage: str,
        *,
        traffic_fraction: float,
        evidence_bindings: Sequence[Mapping[str, Any]],
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Advance through shadow then limited traffic / 依次推进影子与有限流量。"""

        actor = self._require_actor("publisher_binding", actor_binding)
        self._require_current_credential_at(occurred_at)
        if stage == "shadow":
            self._require_stage(SkillPackageStage.VERIFIED)
            if traffic_fraction != 0:
                raise SkillPackageReleaseError("shadow traffic fraction must be zero / 影子流量比例必须为零")
            next_release = SkillReleaseState.SHADOW
            next_stage = SkillPackageStage.SHADOW
        elif stage == "limited":
            self._require_stage(SkillPackageStage.SHADOW)
            maximum = self._contract["release_policy"]["maximum_limited_traffic_fraction"]
            if not isinstance(traffic_fraction, (int, float)) or isinstance(traffic_fraction, bool) or not (0 < float(traffic_fraction) <= maximum):
                raise SkillPackageReleaseError("limited traffic fraction exceeds contract / 有限流量比例超出契约")
            next_release = SkillReleaseState.LIMITED
            next_stage = SkillPackageStage.LIMITED
        else:
            raise ValueError("stage must be shadow or limited; production requires an alias receipt")
        evidence = [_require_binding(item, name="release_evidence") for item in evidence_bindings]
        if not evidence or len(_binding_set(evidence)) != len(evidence):
            raise SkillPackageReleaseError("release evidence must be non-empty and unique / 发布证据必须非空且唯一")
        event = self._make_event(
            "skill.release_stage_changed",
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "stage": stage,
                "traffic_fraction": float(traffic_fraction),
                "evidence_bindings": evidence,
            },
            release_after=next_release,
        )
        self._append(event)
        self._release = next_release
        self._stage = next_stage
        return deepcopy(event)

    def switch_route_alias(
        self,
        receipt: Mapping[str, Any],
        *,
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Validate external CAS then enter production / 校验外部 CAS 后进入生产。"""

        self._require_stage(SkillPackageStage.LIMITED)
        actor = self._require_actor("publisher_binding", actor_binding)
        assert self._manifest is not None and self._credentials
        self._require_current_credential_at(occurred_at)
        if self._qualification is not SkillQualificationState.VERIFIED:
            raise SkillPackageReleaseError("Skill lacks current VERIFIED qualification / Skill 缺少当前 VERIFIED 资格")
        validate_skill_package_alias_receipt(
            receipt,
            contract=self._contract,
            manifest=self._manifest,
            credential=self._credentials[-1],
        )
        if receipt["switched_at"] != occurred_at:
            raise SkillPackageReleaseError("alias receipt and event times differ / 别名回执与事件时间不一致")
        stage_event = self._make_event(
            "skill.release_stage_changed",
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "stage": "production",
                "traffic_fraction": 1.0,
                "alias_receipt_binding": {
                    "id": receipt["alias_event_id"],
                    "version": receipt["schema_version"],
                    "hash": receipt["alias_receipt_hash"],
                },
            },
            release_after=SkillReleaseState.PRODUCTION,
        )
        alias_event = self._make_event(
            "skill.route_alias_switched",
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "alias": receipt["alias"],
                "previous_manifest_binding": receipt["previous_manifest_binding"],
                "next_manifest_binding": receipt["next_manifest_binding"],
                "credential_binding": receipt["credential_binding"],
                "expected_revision": receipt["expected_revision"],
                "new_revision": receipt["new_revision"],
                "compare_and_swap_succeeded": True,
            },
            release_before=SkillReleaseState.PRODUCTION,
            release_after=SkillReleaseState.PRODUCTION,
        )
        alias_event["sequence"] = stage_event["sequence"] + 1
        alias_event["event_id"] = f"{self._contract['lifecycle_id']}:event:{alias_event['sequence']:04d}"
        alias_event["idempotency_key"] = f"skill-package:{self._contract['lifecycle_id']}:{alias_event['sequence']:04d}"
        alias_event["previous_event_hash"] = stage_event["event_hash"]
        alias_event.pop("event_hash", None)
        alias_event = build_artifact("skill_package_event", alias_event)
        self._append(stage_event, alias_event)
        self._alias_receipts.append(deepcopy(dict(receipt)))
        self._release = SkillReleaseState.PRODUCTION
        self._stage = SkillPackageStage.PRODUCTION
        return deepcopy(stage_event), deepcopy(alias_event)

    def record_reuse(
        self,
        receipt: Mapping[str, Any],
        *,
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Record only real production router use / 只记录真实生产路由复用。"""

        self._require_stage(SkillPackageStage.PRODUCTION)
        actor = self._require_actor("lifecycle_owner_binding", actor_binding)
        assert self._manifest is not None and self._credentials
        validate_skill_package_reuse_receipt(
            receipt,
            manifest=self._manifest,
            credential=self._credentials[-1],
            contract=self._contract,
        )
        self._require_current_credential_at(receipt["observed_at"])
        if not self._alias_receipts or _parse_datetime(
            receipt["route_selected_at"]
        ) < _parse_datetime(self._alias_receipts[-1]["switched_at"]):
            raise SkillPackageReleaseError(
                "reuse route selection predates the current production alias / 复用路由选择早于当前生产别名"
            )
        if receipt["observed_at"] != occurred_at:
            raise SkillPackageValidationError(["reuse receipt and event times differ / 复用回执与事件时间不一致"])
        run_key = _binding_key(receipt["run_binding"])
        if any(_binding_key(item["run_binding"]) == run_key for item in self._reuse_receipts):
            raise SkillPackageValidationError(["reuse run is already recorded / 复用运行已记录"])
        event = self._make_event(
            "skill.reuse_recorded",
            actor=actor,
            occurred_at=occurred_at,
            payload={
                "reuse_receipt_binding": {
                    "id": receipt["reuse_id"],
                    "version": receipt["schema_version"],
                    "hash": receipt["reuse_receipt_hash"],
                },
                "external_outcome_status": receipt["external_outcome"]["status"],
                "attribution_status": receipt["attribution_status"],
            },
        )
        self._append(event)
        self._reuse_receipts.append(deepcopy(dict(receipt)))
        return deepcopy(event)

    def start_reverification(
        self,
        *,
        reason_code: str,
        evidence_bindings: Sequence[Mapping[str, Any]],
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        """Withdraw qualification before re-verification / 复验前先撤回资格。"""

        self._require_stage(
            SkillPackageStage.VERIFIED,
            SkillPackageStage.SHADOW,
            SkillPackageStage.LIMITED,
            SkillPackageStage.PRODUCTION,
        )
        actor = self._require_actor("lifecycle_owner_binding", actor_binding)
        if not isinstance(reason_code, str) or not reason_code.strip():
            raise ValueError("reason_code must be non-empty")
        evidence = [_require_binding(item, name="reverification_evidence") for item in evidence_bindings]
        if not evidence:
            raise SkillPackageValidationError(["re-verification requires evidence / 复验需要证据"])
        suspended = self._make_event(
            "skill.credential_suspended",
            actor=actor,
            occurred_at=occurred_at,
            payload={"reason_code": reason_code, "evidence_bindings": evidence},
            release_after=SkillReleaseState.SUSPENDED,
        )
        demoted = self._make_event(
            "skill.demoted_trial",
            actor=actor,
            occurred_at=occurred_at,
            payload={"reason_code": reason_code},
            qualification_before=SkillQualificationState.VERIFIED,
            qualification_after=SkillQualificationState.TRIAL,
            release_before=SkillReleaseState.SUSPENDED,
            release_after=SkillReleaseState.SUSPENDED,
        )
        demoted["sequence"] = suspended["sequence"] + 1
        demoted["event_id"] = f"{self._contract['lifecycle_id']}:event:{demoted['sequence']:04d}"
        demoted["idempotency_key"] = f"skill-package:{self._contract['lifecycle_id']}:{demoted['sequence']:04d}"
        demoted["previous_event_hash"] = suspended["event_hash"]
        demoted.pop("event_hash", None)
        demoted = build_artifact("skill_package_event", demoted)
        reverification = self._make_event(
            "skill.reverification_started",
            actor=actor,
            occurred_at=occurred_at,
            payload={"reason_code": reason_code, "old_credential_binding": self._current_credential_binding()},
            qualification_before=SkillQualificationState.TRIAL,
            qualification_after=SkillQualificationState.TRIAL,
            release_before=SkillReleaseState.SUSPENDED,
            release_after=SkillReleaseState.SUSPENDED,
        )
        reverification["sequence"] = demoted["sequence"] + 1
        reverification["event_id"] = f"{self._contract['lifecycle_id']}:event:{reverification['sequence']:04d}"
        reverification["idempotency_key"] = f"skill-package:{self._contract['lifecycle_id']}:{reverification['sequence']:04d}"
        reverification["previous_event_hash"] = demoted["event_hash"]
        reverification.pop("event_hash", None)
        reverification = build_artifact("skill_package_event", reverification)
        self._append(suspended, demoted, reverification)
        self._credential_active = False
        self._qualification = SkillQualificationState.TRIAL
        self._release = SkillReleaseState.SUSPENDED
        self._stage = SkillPackageStage.REVERIFYING
        return deepcopy(suspended), deepcopy(demoted), deepcopy(reverification)

    def retire(
        self,
        *,
        reason: str,
        evidence_bindings: Sequence[Mapping[str, Any]],
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> tuple[dict[str, Any], ...]:
        """Revoke any credential and remove the version from routing / 撤销凭证并将版本移出路由。"""

        if self._stage in {SkillPackageStage.INITIALIZED, SkillPackageStage.ARCHIVED, SkillPackageStage.RETIRED}:
            raise SkillPackageStateError("retirement is not legal in the current stage")
        actor = self._require_actor("lifecycle_owner_binding", actor_binding)
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be non-empty")
        evidence = [_require_binding(item, name="retirement_evidence") for item in evidence_bindings]
        if not evidence:
            raise SkillPackageValidationError(["retirement requires evidence / 退役需要证据"])
        pending: list[dict[str, Any]] = []
        if self._credentials:
            revoked = self._make_event(
                "skill.credential_revoked",
                actor=actor,
                occurred_at=occurred_at,
                payload={"reason": reason, "evidence_bindings": evidence},
            )
            pending.append(revoked)
        retired = self._make_event(
            "skill.retired",
            actor=actor,
            occurred_at=occurred_at,
            payload={"reason": reason, "evidence_bindings": evidence},
            qualification_after=SkillQualificationState.RETIRED,
            release_after=SkillReleaseState.RETIRED,
        )
        if pending:
            retired["sequence"] = pending[-1]["sequence"] + 1
            retired["event_id"] = f"{self._contract['lifecycle_id']}:event:{retired['sequence']:04d}"
            retired["idempotency_key"] = f"skill-package:{self._contract['lifecycle_id']}:{retired['sequence']:04d}"
            retired["previous_event_hash"] = pending[-1]["event_hash"]
            retired.pop("event_hash", None)
            retired = build_artifact("skill_package_event", retired)
        pending.append(retired)
        self._append(*pending)
        self._credential_active = False
        self._qualification = SkillQualificationState.RETIRED
        self._release = SkillReleaseState.RETIRED
        self._stage = SkillPackageStage.RETIRED
        return tuple(deepcopy(pending))

    def archive(
        self,
        *,
        actor_binding: Mapping[str, Any],
        occurred_at: str,
    ) -> dict[str, Any]:
        """Archive only after retirement / 仅在退役后归档。"""

        self._require_stage(SkillPackageStage.RETIRED)
        actor = self._require_actor("lifecycle_owner_binding", actor_binding)
        event = self._make_event(
            "skill.archived",
            actor=actor,
            occurred_at=occurred_at,
            payload={"immutable_history_retained": True},
            qualification_before=SkillQualificationState.RETIRED,
            qualification_after=SkillQualificationState.RETIRED,
            release_before=SkillReleaseState.RETIRED,
            release_after=SkillReleaseState.ARCHIVED,
        )
        self._append(event)
        self._release = SkillReleaseState.ARCHIVED
        self._stage = SkillPackageStage.ARCHIVED
        return deepcopy(event)


__all__ = [
    "SKILL_PACKAGE_PROBES",
    "SKILL_PACKAGE_RELEASE_STAGES",
    "SKILL_PACKAGE_REQUIRED_DIMENSIONS",
    "SKILL_PACKAGE_REQUIRED_SECTIONS",
    "SkillPackageAuthorizationError",
    "SkillPackageReleaseError",
    "SkillPackageRuntimeError",
    "SkillPackageSession",
    "SkillPackageStage",
    "SkillPackageStateError",
    "SkillPackageValidationError",
    "SkillQualificationState",
    "SkillReleaseState",
    "build_capability_credential",
    "build_skill_lifecycle_reflection_guard",
    "build_skill_package_alias_receipt",
    "build_skill_package_candidate",
    "build_skill_package_contract",
    "build_skill_package_evaluation",
    "build_skill_package_manifest",
    "build_skill_package_reuse_receipt",
    "candidate_binding",
    "credential_binding",
    "evaluation_binding",
    "manifest_binding",
    "validate_capability_credential",
    "validate_skill_package_alias_receipt",
    "validate_skill_package_candidate",
    "validate_skill_package_contract",
    "validate_skill_package_evaluation",
    "validate_skill_package_event",
    "validate_skill_package_event_stream",
    "validate_skill_package_manifest",
    "validate_skill_package_reuse_receipt",
]
