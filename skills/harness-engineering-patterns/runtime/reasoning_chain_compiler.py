"""Static compiler and validators for strict reasoning chains / 严格推理链的静态编译器与校验器。

This module owns deterministic blueprint-to-plan compilation and all immutable
artifact checks. Session execution lives in reasoning_chain_session; the legacy
reasoning_chain_factory module remains the compatibility entrypoint.
/ 本模块负责蓝图到计划的确定性编译及全部不可变制品校验；会话执行位于
reasoning_chain_session，旧的 reasoning_chain_factory 保留为兼容入口。
"""

from __future__ import annotations

from functools import lru_cache
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker

try:  # Package import / 包导入
    from .reasoning_artifacts import ArtifactValidationError, validate_reasoning_contract
    from .reasoning_metrics import resolve_required_probes
    from .reasoning_runtime import (
        PrivateReasoningCaptureError,
        ReasoningEngine,
        ReasoningRuntimeError,
        content_fingerprint,
        validate_runtime_contract_capabilities,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import ArtifactValidationError, validate_reasoning_contract
    from reasoning_metrics import resolve_required_probes
    from reasoning_runtime import (
        PrivateReasoningCaptureError,
        ReasoningEngine,
        ReasoningRuntimeError,
        content_fingerprint,
        validate_runtime_contract_capabilities,
    )


FACTORY_ID = "reasoning-chain-factory"
FACTORY_VERSION = "1.4.0"
PLAN_VERSION = "1.4.0"

_SCHEMA_FILES = {
    "blueprint": "reasoning-chain-blueprint.schema.json",
    "checkpoint_validation": "reasoning-chain-checkpoint-validation.schema.json",
    "plan": "reasoning-chain-plan.schema.json",
}

_PLAN_BUDGET_FIELDS = (
    "reasoning_tokens",
    "latency_ms",
    "model_calls",
    "tool_calls",
    "parallel_paths",
    "iterations",
    "retries",
    "total_cost_units",
)

_PLAN_TO_CONTRACT_BUDGET = {
    "reasoning_tokens": "max_reasoning_tokens",
    "latency_ms": "max_latency_ms",
    "model_calls": "max_model_calls",
    "tool_calls": "max_tool_calls",
    "parallel_paths": "max_parallel_paths",
    "iterations": "max_iterations",
    "retries": "max_retries",
    "total_cost_units": "max_total_cost_units",
}

_CHECKPOINT_STATUSES = {
    "passed",
    "failed",
    "insufficient_evidence",
    "human_required",
}

_FACTORY_DEFINITION = {
    "factory_id": FACTORY_ID,
    "factory_version": FACTORY_VERSION,
    "blueprint_schema_version": "1.0.0",
    "plan_schema_version": "1.0.0",
    "semantics": [
        "strict_linear_predecessor",
        "verified_premise_only",
        "contract_bound_budget",
        "budget_reservation_before_dispatch",
        "reservation_settlement_before_close",
        "checkpoint_bound_exit",
        "checkpoint_validation_artifact",
        "resolved_versioned_evidence",
        "contract_owned_evidence_sufficiency",
        "candidate_plan_binding",
        "candidate_evidence_revision_lineage",
        "plan_bound_readonly_tool_adapter",
        "live_verified_tool_authorization",
        "runtime_capability_preflight",
        "resolved_probe_plan",
        "no_private_reasoning",
    ],
}


class ChainFactoryError(ValueError):
    """Blueprint or plan compilation failed / 蓝图或计划编译失败。"""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


class ChainPlanStateError(ReasoningRuntimeError):
    """A command violates the compiled chain state / 命令违反已编译链状态。"""


class ChainPlanDriftError(ChainPlanStateError):
    """Runtime events drifted from the immutable plan / 运行事件偏离不可变计划。"""


def _canonical_copy(value: Any) -> Any:
    """Return detached finite JSON after the shared privacy guard / 经共享隐私守卫后返回独立有限 JSON。"""

    content_fingerprint(value)
    return json.loads(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    )


@lru_cache(maxsize=None)
def _schema_validator(kind: str) -> Draft202012Validator:
    if kind == "evidence":
        path = (
            Path(__file__).resolve().parents[1]
            / "schemas"
            / "reasoning-event.schema.json"
        )
        event_schema = json.loads(path.read_text(encoding="utf-8"))
        schema = {
            "$schema": event_schema.get(
                "$schema", "https://json-schema.org/draft/2020-12/schema"
            ),
            "$ref": "#/$defs/Evidence",
            "$defs": event_schema["$defs"],
        }
        return Draft202012Validator(schema, format_checker=FormatChecker())
    try:
        filename = _SCHEMA_FILES[kind]
    except KeyError as exc:
        raise KeyError(f"unknown chain artifact kind / 未知链制品类型: {kind}") from exc
    path = Path(__file__).resolve().parents[1] / "schemas" / filename
    schema = json.loads(path.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _schema_failures(kind: str, artifact: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for error in sorted(
        _schema_validator(kind).iter_errors(dict(artifact)),
        key=lambda item: tuple(str(part) for part in item.absolute_path),
    ):
        location = "/" + "/".join(str(part) for part in error.absolute_path)
        failures.append(f"{kind} schema {location}: {error.message}")
    return failures


def _binding(identifier: str, version: str, digest: str) -> dict[str, str]:
    return {"id": identifier, "version": version, "hash": digest}


def _semver_is_strictly_greater(candidate: str, predecessor: str) -> bool:
    """Compare validated semantic versions including prerelease precedence / 比较含预发布优先级的已校验语义版本。"""

    def parse(value: str) -> tuple[tuple[int, int, int], list[str] | None]:
        core_text, separator, prerelease_text = value.partition("-")
        core = tuple(int(part) for part in core_text.split("."))
        return core, prerelease_text.split(".") if separator else None  # type: ignore[return-value]

    candidate_core, candidate_prerelease = parse(candidate)
    predecessor_core, predecessor_prerelease = parse(predecessor)
    if candidate_core != predecessor_core:
        return candidate_core > predecessor_core
    if candidate_prerelease is None:
        return predecessor_prerelease is not None
    if predecessor_prerelease is None:
        return False
    for candidate_part, predecessor_part in zip(
        candidate_prerelease, predecessor_prerelease
    ):
        if candidate_part == predecessor_part:
            continue
        candidate_numeric = candidate_part.isdigit()
        predecessor_numeric = predecessor_part.isdigit()
        if candidate_numeric and predecessor_numeric:
            return int(candidate_part) > int(predecessor_part)
        if candidate_numeric != predecessor_numeric:
            return not candidate_numeric
        return candidate_part > predecessor_part
    return len(candidate_prerelease) > len(predecessor_prerelease)


def _factory_binding() -> dict[str, str]:
    return _binding(
        FACTORY_ID,
        FACTORY_VERSION,
        content_fingerprint(_FACTORY_DEFINITION),
    )


def _has_cjk(value: Any) -> bool:
    return isinstance(value, str) and bool(re.search(r"[\u3400-\u9fff]", value))


def _has_english(value: Any) -> bool:
    return isinstance(value, str) and bool(re.search(r"[A-Za-z]", value))


def _duplicate_values(records: Sequence[Mapping[str, Any]], field: str) -> list[str]:
    values = [str(record[field]) for record in records]
    return sorted({value for value in values if values.count(value) > 1})


def _sum_budget(steps: Sequence[Mapping[str, Any]]) -> dict[str, int | float]:
    result: dict[str, int | float] = {
        field: 0.0 if field == "total_cost_units" else 0
        for field in _PLAN_BUDGET_FIELDS
    }
    for step in steps:
        allocation = step["budget_allocation"]
        for field in _PLAN_BUDGET_FIELDS:
            result[field] += allocation[field]
    return result


def _blueprint_semantic_failures(blueprint: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    steps = list(blueprint.get("steps", []))
    if not _has_english(blueprint.get("name_en")) or not _has_english(
        blueprint.get("description_en")
    ):
        failures.append("English blueprint metadata is required / 蓝图英文元数据不能为空")
    if not _has_cjk(blueprint.get("name_zh")) or not _has_cjk(
        blueprint.get("description_zh")
    ):
        failures.append("Chinese blueprint metadata is required / 蓝图中文元数据必须包含中文")
    if len(steps) > int(blueprint.get("max_steps", 0)):
        failures.append("step count exceeds max_steps / 步骤数量超过 max_steps")

    for field in ("step_key", "output_claim_id"):
        duplicates = _duplicate_values(steps, field) if steps else []
        if duplicates:
            failures.append(f"duplicate {field}: {', '.join(duplicates)}")
    checkpoints = [step.get("checkpoint", {}) for step in steps]
    checkpoint_duplicates = (
        _duplicate_values(checkpoints, "checkpoint_id")
        if checkpoints and all("checkpoint_id" in item for item in checkpoints)
        else []
    )
    if checkpoint_duplicates:
        failures.append(
            "duplicate checkpoint_id / 重复检查点标识: "
            + ", ".join(checkpoint_duplicates)
        )

    previous_step_key: str | None = None
    previous_claim_id: str | None = None
    produced_claims: set[str] = set()
    for index, step in enumerate(steps, start=1):
        if step.get("sequence_number") != index:
            failures.append(
                f"step {step.get('step_key')} sequence must be {index} / 步骤序号必须连续"
            )
        expected_dependency = [] if previous_step_key is None else [previous_step_key]
        if step.get("depends_on") != expected_dependency:
            failures.append(
                f"step {step.get('step_key')} must depend only on its immediate predecessor / "
                "步骤只能依赖直接前驱"
            )
        input_claims = set(step.get("input_claim_ids", []))
        unknown_claims = sorted(input_claims - produced_claims)
        if unknown_claims:
            failures.append(
                f"step {step.get('step_key')} consumes unproduced claims {unknown_claims} / "
                "步骤消费了尚未生成的链内命题"
            )
        if previous_claim_id is not None and previous_claim_id not in input_claims:
            failures.append(
                f"step {step.get('step_key')} does not bind the checked predecessor claim / "
                "步骤未绑定已检查的前驱命题"
            )
        if index == 1 and input_claims:
            failures.append("the first step cannot consume chain-internal claims / 首步不得消费链内命题")
        if step.get("criticality") == "critical" and not step.get(
            "required_evidence_types"
        ):
            failures.append(
                f"critical step {step.get('step_key')} needs evidence types / 关键步骤必须声明证据类型"
            )
        action = step.get("action", {})
        allocation = step.get("budget_allocation", {})
        if action.get("uses_tool") and allocation.get("tool_calls", 0) != 1:
            failures.append(
                f"tool step {step.get('step_key')} must reserve exactly one tool call / "
                "工具步骤必须且只能预留一次工具调用"
            )
        if not action.get("uses_tool") and allocation.get("tool_calls", 0) != 0:
            failures.append(
                f"non-tool step {step.get('step_key')} cannot reserve tool calls / 非工具步骤不得预留工具调用"
            )
        for dimension in ("parallel_paths", "iterations", "retries"):
            if allocation.get(dimension, 0) != 0:
                failures.append(
                    f"strict chain step {step.get('step_key')} must allocate zero {dimension} / "
                    f"严格链步骤的 {dimension} 必须为零"
                )
        previous_step_key = str(step.get("step_key"))
        previous_claim_id = str(step.get("output_claim_id"))
        produced_claims.add(previous_claim_id)

    final_claims = set(blueprint.get("final_claim_ids", []))
    unknown_final_claims = sorted(final_claims - produced_claims)
    if unknown_final_claims:
        failures.append(
            f"final claims were not produced: {unknown_final_claims} / 最终命题未由步骤生成"
        )
    if previous_claim_id is not None and previous_claim_id not in final_claims:
        failures.append("the last step claim must be final / 末步命题必须进入最终命题集合")
    return failures


def validate_chain_blueprint(blueprint: Mapping[str, Any]) -> None:
    """Validate blueprint Schema, privacy, and strict-chain semantics / 校验蓝图 Schema、隐私与严格链语义。"""

    if not isinstance(blueprint, Mapping):
        raise TypeError("blueprint must be a mapping / 蓝图必须是映射")
    try:
        artifact = _canonical_copy(dict(blueprint))
    except (PrivateReasoningCaptureError, TypeError, ValueError) as exc:
        raise ChainFactoryError([str(exc)]) from exc
    failures = _schema_failures("blueprint", artifact)
    if not failures:
        failures.extend(_blueprint_semantic_failures(artifact))
    if failures:
        raise ChainFactoryError(failures)


def _switch_available(contract: Mapping[str, Any], target_mode: str) -> bool:
    return any(
        rule.get("from", {}).get("execution_mode") == "chain"
        and rule.get("to", {}).get("execution_mode") == target_mode
        for rule in contract.get("allowed_mode_switches", [])
    )


def _contract_failures(
    contract: Mapping[str, Any],
    steps: Sequence[Mapping[str, Any]],
) -> list[str]:
    failures: list[str] = []
    try:
        validate_runtime_contract_capabilities(contract)
    except (TypeError, ValueError) as exc:
        failures.append(
            f"contract exceeds runtime capability / 契约超出运行时能力: {exc}"
        )
    if contract.get("execution_mode") != "chain" or contract.get(
        "primary_topology"
    ) != "chain":
        failures.append("factory requires a routed chain contract / 工厂要求已路由到链式的契约")
    selected = contract.get("routing_decision", {}).get("selected_configuration", {})
    if selected.get("execution_mode") != "chain" or selected.get(
        "primary_topology"
    ) != "chain":
        failures.append("routing decision is not chain-bound / 路由决定未绑定链式配置")

    totals = _sum_budget(steps)
    budget = contract.get("budget", {})
    for plan_field, contract_field in _PLAN_TO_CONTRACT_BUDGET.items():
        limit = budget.get(contract_field)
        allocated = totals[plan_field]
        if limit is None and allocated > 0:
            failures.append(
                f"{plan_field} is allocated while its contract limit is unconfigured / "
                f"{plan_field} 已分配但契约上限未配置"
            )
        elif limit is not None and allocated > limit:
            failures.append(
                f"{plan_field} allocation {allocated} exceeds contract limit {limit} / "
                f"{plan_field} 分配超过契约上限"
            )

    failure_actions = {
        str(step.get("checkpoint", {}).get("on_failure")) for step in steps
    }
    if "switch_parallel" in failure_actions and not _switch_available(
        contract, "parallel"
    ):
        failures.append(
            "parallel failure exit lacks an allowed contract switch / 并行失败出口缺少契约允许的换路规则"
        )
    if "switch_iterative" in failure_actions and not _switch_available(
        contract, "iterative"
    ):
        failures.append(
            "iterative failure exit lacks an allowed contract switch / 迭代失败出口缺少契约允许的换路规则"
        )
    if steps:
        contract_types = set(
            contract.get("evidence_sufficiency", {}).get(
                "required_evidence_types", ()
            )
        )
        final_step_types = set(steps[-1].get("required_evidence_types", ()))
        missing_final_types = sorted(contract_types - final_step_types)
        if missing_final_types:
            failures.append(
                "final step does not carry contract-required evidence types / "
                f"末步未承载契约要求的证据类型: {missing_final_types}"
            )
    return failures


def _condition_states(
    blueprint: Mapping[str, Any], contract: Mapping[str, Any]
) -> dict[str, str]:
    uses_tool = any(step["action"]["uses_tool"] for step in blueprint["steps"])
    requires_outcome = bool(blueprint["requires_outcome"])
    states: dict[str, str] = {
        "tool_or_side_effect_action": "true" if uses_tool else "false",
        "downstream_adoption_or_correctness_metric": (
            "true" if requires_outcome else "false"
        ),
    }
    supporting = set(contract["supporting_topologies"])
    if "orchestration" in supporting:
        states.update(
            {
                "parallel_branch_exists": "false",
                "iteration_exists": "false",
                "outcome_metric": "true" if requires_outcome else "false",
            }
        )
    if "hierarchy" in supporting:
        states.update(
            {
                "delegated_action": "false",
                "parent_or_child_outcome_metric": (
                    "true" if requires_outcome else "false"
                ),
            }
        )
    return states


def _no_progress_control(contract: Mapping[str, Any]) -> dict[str, Any]:
    matches = [
        condition
        for condition in contract["stop_conditions"]
        if condition["type"] == "no_progress"
    ]
    if not matches:
        return {
            "enabled": False,
            "condition_id": None,
            "consecutive_steps": None,
            "min_information_gain": None,
            "on_trigger": None,
        }
    return {
        "enabled": True,
        "condition_id": matches[0]["condition_id"],
        "consecutive_steps": matches[0]["consecutive_steps"],
        "min_information_gain": matches[0]["min_information_gain"],
        "on_trigger": matches[0]["on_trigger"],
    }


def _runtime_step_id(
    plan_seed: str, sequence_number: int, step_key: str
) -> str:
    digest = content_fingerprint(
        {
            "plan_seed": plan_seed,
            "sequence_number": sequence_number,
            "step_key": step_key,
        }
    )
    return f"chain-step-{sequence_number}-{digest.removeprefix('sha256:')[:24]}"


def _checkpoint_with_hash(checkpoint: Mapping[str, Any]) -> dict[str, Any]:
    result = _canonical_copy(dict(checkpoint))
    result["checkpoint_hash"] = content_fingerprint(result)
    return result


def _blueprint_plan_failures(
    plan: Mapping[str, Any],
    blueprint: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> list[str]:
    failures: list[str] = []
    try:
        validate_chain_blueprint(blueprint)
        source = _canonical_copy(dict(blueprint))
    except (ChainFactoryError, TypeError, ValueError) as exc:
        return [f"bound blueprint is invalid / 绑定蓝图无效: {exc}"]
    expected_binding = _binding(
        source["blueprint_id"],
        source["blueprint_version"],
        content_fingerprint(source),
    )
    if plan.get("blueprint_binding") != expected_binding:
        failures.append("plan blueprint binding mismatch / 计划蓝图绑定不匹配")
    plan_seed = content_fingerprint(
        {
            "factory_binding": _factory_binding(),
            "blueprint_hash": expected_binding["hash"],
            "contract_hash": contract["contract_hash"],
        }
    )
    expected_plan_id = f"chain-plan-{plan_seed.removeprefix('sha256:')[:32]}"
    if plan.get("plan_id") != expected_plan_id:
        failures.append(
            "plan identity is not the deterministic factory output / 计划标识不是工厂确定性输出"
        )
    plan_steps = list(plan.get("steps", []))
    source_steps = list(source["steps"])
    if len(plan_steps) != len(source_steps):
        failures.append("plan step count differs from blueprint / 计划步骤数与蓝图不一致")
        return failures
    projected_fields = {
        "step_key": "step_key",
        "name_en": "name_en",
        "name_zh": "name_zh",
        "sequence_number": "sequence_number",
        "input_claim_ids": "input_claim_ids",
        "output_claim_id": "output_claim_id",
        "criticality": "criticality",
        "claim_to_verify": "claim_to_verify",
        "required_evidence_types": "required_evidence_types",
        "data_gap_policy": "data_gap_policy",
        "budget_allocation": "budget_allocation",
    }
    expected_predecessor: str | None = None
    for compiled, declared in zip(plan_steps, source_steps):
        expected_step_id = _runtime_step_id(
            plan_seed,
            declared["sequence_number"],
            declared["step_key"],
        )
        if (
            compiled.get("step_id") != expected_step_id
            or compiled.get("predecessor_step_id") != expected_predecessor
        ):
            failures.append(
                f"compiled step identity differs from deterministic output at {declared['step_key']} / "
                "编译步骤标识与确定性输出不一致"
            )
        expected_predecessor = expected_step_id
        for plan_field, blueprint_field in projected_fields.items():
            if compiled.get(plan_field) != declared.get(blueprint_field):
                failures.append(
                    f"compiled {plan_field} differs from blueprint at {declared['step_key']} / "
                    f"编译字段 {plan_field} 与蓝图不一致"
                )
        action = declared["action"]
        if (
            compiled.get("action_kind") != action["kind"]
            or compiled.get("action_instruction") != action["instruction"]
            or compiled.get("uses_tool") is not action["uses_tool"]
            or compiled.get("tool_binding") != action.get("tool_binding")
            or compiled.get("authorization_policy_binding")
            != action.get("authorization_policy_binding")
            or compiled.get("side_effect") is not False
        ):
            failures.append(
                f"compiled action differs from blueprint at {declared['step_key']} / 编译动作与蓝图不一致"
            )
        checkpoint = dict(compiled.get("checkpoint", {}))
        checkpoint.pop("checkpoint_hash", None)
        if checkpoint != declared["checkpoint"]:
            failures.append(
                f"compiled checkpoint differs from blueprint at {declared['step_key']} / 编译检查点与蓝图不一致"
            )
    if plan.get("final_claim_ids") != source["final_claim_ids"]:
        failures.append("plan final claims differ from blueprint / 计划最终命题与蓝图不一致")
    if plan.get("control", {}).get("max_steps") != source["max_steps"]:
        failures.append("plan max_steps differs from blueprint / 计划步骤上限与蓝图不一致")
    if plan.get("control", {}).get("requires_outcome") is not source[
        "requires_outcome"
    ]:
        failures.append("plan outcome control differs from blueprint / 计划结果控制与蓝图不一致")
    return failures


def _plan_semantic_failures(
    plan: Mapping[str, Any],
    contract: Mapping[str, Any] | None,
    blueprint: Mapping[str, Any] | None,
) -> list[str]:
    failures: list[str] = []
    try:
        expected_hash = content_fingerprint(
            {key: value for key, value in plan.items() if key != "plan_hash"}
        )
    except (PrivateReasoningCaptureError, TypeError, ValueError) as exc:
        return [str(exc)]
    if plan.get("plan_hash") != expected_hash:
        failures.append("plan_hash does not match content / plan_hash 与内容不匹配")
    if plan.get("plan_version") != PLAN_VERSION:
        failures.append("plan version drift / 计划版本漂移")
    if plan.get("factory_binding") != _factory_binding():
        failures.append("factory binding drift / 工厂绑定漂移")

    steps = list(plan.get("steps", []))
    step_ids = [step.get("step_id") for step in steps]
    if len(step_ids) != len(set(step_ids)):
        failures.append("plan step IDs must be unique / 计划步骤标识必须唯一")
    previous_step_id: str | None = None
    previous_claim_id: str | None = None
    produced_claims: set[str] = set()
    for index, step in enumerate(steps, start=1):
        if step.get("sequence_number") != index:
            failures.append("plan sequence numbers are not contiguous / 计划序号不连续")
        if step.get("predecessor_step_id") != previous_step_id:
            failures.append("plan predecessor chain is invalid / 计划前驱链无效")
        input_claims = set(step.get("input_claim_ids", []))
        if input_claims - produced_claims:
            failures.append("plan consumes unproduced claims / 计划消费未生成命题")
        if previous_claim_id is not None and previous_claim_id not in input_claims:
            failures.append("plan skips its checked predecessor claim / 计划跳过已检查前驱命题")
        checkpoint = step.get("checkpoint", {})
        checkpoint_without_hash = {
            key: value for key, value in checkpoint.items() if key != "checkpoint_hash"
        }
        if checkpoint.get("checkpoint_hash") != content_fingerprint(
            checkpoint_without_hash
        ):
            failures.append(
                f"checkpoint hash mismatch at {step.get('step_key')} / 检查点摘要不匹配"
            )
        previous_step_id = str(step.get("step_id"))
        previous_claim_id = str(step.get("output_claim_id"))
        produced_claims.add(previous_claim_id)

    if plan.get("budget_allocation") != _sum_budget(steps):
        failures.append("plan budget summary does not equal step allocations / 计划预算汇总不等于逐步分配")
    final_claims = set(plan.get("final_claim_ids", []))
    if final_claims - produced_claims:
        failures.append("plan final claims are not produced / 计划最终命题未生成")
    if previous_claim_id is not None and previous_claim_id not in final_claims:
        failures.append("plan last claim is not final / 计划末步命题不是最终命题")

    try:
        resolved = resolve_required_probes(
            "chain",
            supporting_topologies=plan.get("supporting_topologies", []),
            condition_states=plan.get("probe_plan", {}).get("condition_states", {}),
        ).as_dict()
        if resolved != plan.get("probe_plan"):
            failures.append("probe plan is stale or incomplete / 探针计划过期或不完整")
    except (TypeError, ValueError, RuntimeError) as exc:
        failures.append(f"probe plan cannot be resolved / 探针计划无法解析: {exc}")

    if contract is not None:
        try:
            validate_reasoning_contract(contract)
        except (ArtifactValidationError, TypeError, ValueError) as exc:
            failures.append(f"reasoning contract is invalid / 推理契约无效: {exc}")
            return failures
        expected_binding = _binding(
            str(contract["contract_id"]),
            str(contract["contract_version"]),
            str(contract["contract_hash"]),
        )
        if plan.get("contract_binding") != expected_binding:
            failures.append("plan contract binding mismatch / 计划契约绑定不匹配")
        for identity in ("workflow_id", "task_id", "run_id", "scene_id"):
            if plan.get(identity) != contract.get(identity):
                failures.append(f"plan {identity} mismatch / 计划 {identity} 不匹配")
        if plan.get("created_at") != contract.get("created_at"):
            failures.append("plan creation time mismatch / 计划创建时间不匹配")
        if plan.get("supporting_topologies") != contract.get(
            "supporting_topologies"
        ):
            failures.append("supporting topology binding mismatch / 支撑拓扑绑定不匹配")
        failures.extend(_contract_failures(contract, steps))
        if plan.get("control", {}).get("no_progress") != _no_progress_control(
            contract
        ):
            failures.append("no-progress control drift / 无进展控制漂移")
    if blueprint is not None:
        assert contract is not None
        failures.extend(_blueprint_plan_failures(plan, blueprint, contract))
        expected_condition_states = _condition_states(blueprint, contract)
        if plan.get("probe_plan", {}).get("condition_states") != expected_condition_states:
            failures.append(
                "probe conditions differ from blueprint and contract / 探针条件与蓝图及契约不一致"
            )
    return failures


def validate_chain_plan(
    plan: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    blueprint: Mapping[str, Any] | None = None,
) -> None:
    """Validate a sealed plan, with both authority sources or neither / 校验封存计划；权威来源须同时提供或均不提供。"""

    if not isinstance(plan, Mapping):
        raise TypeError("plan must be a mapping / 计划必须是映射")
    if (contract is None) != (blueprint is None):
        raise ChainFactoryError(
            [
                "contract and blueprint must be supplied together for authoritative plan validation / "
                "权威计划校验必须同时提供契约与蓝图"
            ]
        )
    try:
        artifact = _canonical_copy(dict(plan))
    except (PrivateReasoningCaptureError, TypeError, ValueError) as exc:
        raise ChainFactoryError([str(exc)]) from exc
    failures = _schema_failures("plan", artifact)
    if not failures:
        failures.extend(_plan_semantic_failures(artifact, contract, blueprint))
    if failures:
        raise ChainFactoryError(failures)


class ReasoningChainFactory:
    """Compile strict chain blueprints and open guarded sessions / 编译严格链蓝图并创建受守卫会话。"""

    def compile(
        self,
        blueprint: Mapping[str, Any],
        contract: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Compile one deterministic contract-bound plan / 编译一个确定且绑定契约的计划。"""

        validate_chain_blueprint(blueprint)
        normalized_blueprint = _canonical_copy(dict(blueprint))
        normalized_contract = _canonical_copy(dict(contract))
        try:
            validate_reasoning_contract(normalized_contract)
        except (ArtifactValidationError, TypeError, ValueError) as exc:
            raise ChainFactoryError(
                [f"reasoning contract is invalid / 推理契约无效: {exc}"]
            ) from exc
        contract_failures = _contract_failures(
            normalized_contract, normalized_blueprint["steps"]
        )
        if contract_failures:
            raise ChainFactoryError(contract_failures)

        blueprint_hash = content_fingerprint(normalized_blueprint)
        plan_seed = content_fingerprint(
            {
                "factory_binding": _factory_binding(),
                "blueprint_hash": blueprint_hash,
                "contract_hash": normalized_contract["contract_hash"],
            }
        )
        plan_id = f"chain-plan-{plan_seed.removeprefix('sha256:')[:32]}"
        compiled_steps: list[dict[str, Any]] = []
        previous_step_id: str | None = None
        for step in normalized_blueprint["steps"]:
            step_id = _runtime_step_id(
                plan_seed, step["sequence_number"], step["step_key"]
            )
            compiled_steps.append(
                {
                    "step_id": step_id,
                    "step_key": step["step_key"],
                    "name_en": step["name_en"],
                    "name_zh": step["name_zh"],
                    "sequence_number": step["sequence_number"],
                    "predecessor_step_id": previous_step_id,
                    "input_claim_ids": list(step["input_claim_ids"]),
                    "output_claim_id": step["output_claim_id"],
                    "criticality": step["criticality"],
                    "claim_to_verify": step["claim_to_verify"],
                    "action_kind": step["action"]["kind"],
                    "action_instruction": step["action"]["instruction"],
                    "uses_tool": step["action"]["uses_tool"],
                    **(
                        {
                            "tool_binding": dict(
                                step["action"]["tool_binding"]
                            ),
                            "authorization_policy_binding": dict(
                                step["action"]["authorization_policy_binding"]
                            ),
                        }
                        if step["action"]["uses_tool"]
                        else {}
                    ),
                    "side_effect": False,
                    "required_evidence_types": list(
                        step["required_evidence_types"]
                    ),
                    "checkpoint": _checkpoint_with_hash(step["checkpoint"]),
                    "data_gap_policy": step["data_gap_policy"],
                    "budget_allocation": dict(step["budget_allocation"]),
                }
            )
            previous_step_id = step_id

        no_progress = _no_progress_control(normalized_contract)
        probe_resolution = resolve_required_probes(
            "chain",
            supporting_topologies=normalized_contract["supporting_topologies"],
            condition_states=_condition_states(
                normalized_blueprint, normalized_contract
            ),
        )
        plan: dict[str, Any] = {
            "schema_version": "1.0.0",
            "plan_id": plan_id,
            "plan_version": PLAN_VERSION,
            "factory_binding": _factory_binding(),
            "blueprint_binding": _binding(
                normalized_blueprint["blueprint_id"],
                normalized_blueprint["blueprint_version"],
                blueprint_hash,
            ),
            "contract_binding": _binding(
                normalized_contract["contract_id"],
                normalized_contract["contract_version"],
                normalized_contract["contract_hash"],
            ),
            "workflow_id": normalized_contract["workflow_id"],
            "task_id": normalized_contract["task_id"],
            "run_id": normalized_contract["run_id"],
            "scene_id": normalized_contract["scene_id"],
            "execution_mode": "chain",
            "primary_topology": "chain",
            "supporting_topologies": list(
                normalized_contract["supporting_topologies"]
            ),
            "control": {
                "max_steps": normalized_blueprint["max_steps"],
                "requires_outcome": normalized_blueprint["requires_outcome"],
                "no_progress": no_progress,
            },
            "budget_allocation": _sum_budget(compiled_steps),
            "steps": compiled_steps,
            "final_claim_ids": list(normalized_blueprint["final_claim_ids"]),
            "probe_plan": probe_resolution.as_dict(),
            "created_at": normalized_contract["created_at"],
        }
        plan["plan_hash"] = content_fingerprint(plan)
        validate_chain_plan(
            plan,
            contract=normalized_contract,
            blueprint=normalized_blueprint,
        )
        return _canonical_copy(plan)

    def start_session(
        self,
        engine: ReasoningEngine,
        plan: Mapping[str, Any],
        contract: Mapping[str, Any],
        blueprint: Mapping[str, Any],
        *,
        auto_start: bool = True,
    ) -> "ChainPlanSession":
        """Create the contract run and return its chain guard / 创建契约运行并返回链守卫。"""

        try:  # Deferred import avoids compiler/session cycles / 延迟导入避免编译器与会话循环依赖
            from .reasoning_chain_session import ChainPlanSession
        except ImportError:  # Direct test/module import / 测试与直接模块导入
            from reasoning_chain_session import ChainPlanSession

        if not isinstance(engine, ReasoningEngine):
            raise TypeError("engine must be ReasoningEngine / engine 必须为 ReasoningEngine")
        expected_plan = self.compile(blueprint, contract)
        supplied_plan = _canonical_copy(dict(plan))
        if supplied_plan != expected_plan:
            raise ChainFactoryError(
                [
                    "plan is not the deterministic output of its bound blueprint and contract / "
                    "计划不是绑定蓝图与契约的确定性编译结果"
                ]
            )
        run_id = engine.create_run_from_contract(contract, auto_start=auto_start)
        if run_id != plan["run_id"]:
            raise ChainPlanDriftError("run identity drift / 运行标识漂移")
        return ChainPlanSession(
            engine,
            plan,
            blueprint=blueprint,
            contract=contract,
        )



__all__ = [
    "ChainFactoryError",
    "ChainPlanDriftError",
    "ChainPlanStateError",
    "FACTORY_ID",
    "FACTORY_VERSION",
    "PLAN_VERSION",
    "ReasoningChainFactory",
    "validate_chain_blueprint",
    "validate_chain_plan",
]
