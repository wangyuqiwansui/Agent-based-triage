"""Schema and semantic guards for reasoning artifacts / 推理制品的 Schema 与语义闸门。

The JSON Schemas intentionally describe local shapes.  Cross-record bindings,
self-excluding integrity hashes, and evidence sufficiency require executable
checks; this module is the authoritative producer-side guard for those rules.
/ JSON Schema 有意只描述局部结构。跨记录绑定、排除自身字段的完整性哈希和证据充分性
需要可执行检查；本模块是这些规则的权威生产端闸门。
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker


_SCHEMA_FILES = {
    "normalized_input": "normalized-input.schema.json",
    "reasoning_contract": "reasoning-contract.schema.json",
    "reasoning_event": "reasoning-event.schema.json",
    "reasoning_result": "reasoning-result.schema.json",
    "tool_dispatch_envelope": "tool-dispatch-envelope.schema.json",
    "tool_execution_event": "tool-execution-event.schema.json",
    "tool_execution_result": "tool-execution-result.schema.json",
    "workflow_route_envelope": "workflow-route-envelope.schema.json",
    "workflow_route_revision": "workflow-route-revision.schema.json",
}

_HASH_FIELDS = {
    "normalized_input": "normalized_input_hash",
    "reasoning_contract": "contract_hash",
    "reasoning_result": "result_hash",
    "tool_dispatch_envelope": "dispatch_hash",
    "tool_execution_event": "event_hash",
    "tool_execution_result": "result_hash",
    "workflow_route_envelope": "route_envelope_hash",
    "workflow_route_revision": "revision_event_hash",
}

_TOOL_ADMISSION_CHECK_ORDER = (
    "registration",
    "frontier",
    "parameters",
    "identity_scope",
    "workflow_stage",
    "dependencies",
    "state_evidence",
    "budget_quota",
    "idempotency",
    "concurrency",
    "approval",
    "risk_environment",
    "compensation",
    "observability",
)

_TOOL_WRITE_SIDE_EFFECTS = {
    "reversible_write",
    "sensitive_write",
    "irreversible_external",
}

_TOOL_EVENT_STAGE = {
    "capability_frontier_built": "capability_frontier",
    "candidate_selection_completed": "candidate_selection",
    "execution_admission_completed": "execution_admission",
    "execution_lease_acquired": "idempotency_lease",
    "tool_execution_started": "tool_execution",
    "tool_execution_succeeded": "result_classification",
    "tool_result_reused": "result_classification",
    "tool_execution_rejected": "result_classification",
    "tool_execution_failed": "result_classification",
    "tool_execution_unknown": "result_classification",
    "tool_execution_partial": "result_classification",
    "tool_execution_waiting": "result_classification",
    "side_effect_confirmed": "side_effect_verification",
}

_WORKFLOW_ROUTE_SIGNAL_NAMES = frozenset(
    {
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
    }
)

_CONFIGURATION_FIELDS = (
    "execution_mode",
    "reasoning_depth",
    "primary_topology",
    "supporting_topologies",
)

_BUDGET_FIELDS = {
    "reasoning_tokens": "max_reasoning_tokens",
    "latency_ms": "max_latency_ms",
    "model_calls": "max_model_calls",
    "tool_calls": "max_tool_calls",
    "parallel_paths": "max_parallel_paths",
    "iterations": "max_iterations",
    "retries": "max_retries",
    "total_cost_units": "max_total_cost_units",
}


class ArtifactValidationError(ValueError):
    """One or more artifact invariants failed / 一个或多个制品不变量失败。"""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def _canonical_json(value: Any) -> str:
    """Return finite canonical JSON / 返回只含有限数值的规范 JSON。"""

    def reject_nonfinite(item: Any, path: str = "$") -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise ArtifactValidationError(
                [f"non-finite JSON number at {path} / {path} 存在非有限 JSON 数值"]
            )
        if isinstance(item, Mapping):
            for key, nested in item.items():
                reject_nonfinite(nested, f"{path}.{key}")
        elif isinstance(item, (list, tuple)):
            for index, nested in enumerate(item):
                reject_nonfinite(nested, f"{path}[{index}]")

    reject_nonfinite(value)
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ArtifactValidationError(
            [f"artifact is not canonical JSON / 制品不是规范 JSON: {exc}"]
        ) from exc


def artifact_fingerprint(value: Mapping[str, Any], hash_field: str | None = None) -> str:
    """Hash canonical JSON while omitting the artifact's own hash field.

    / 对规范 JSON 计算哈希，并排除制品自身的哈希字段。
    """

    content = dict(value)
    if hash_field is not None:
        content.pop(hash_field, None)
    canonical = _canonical_json(content)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def workflow_signal_fingerprint(
    *,
    task_atom_id: str,
    workflow_policy_binding: Mapping[str, Any],
    adapter_binding: Mapping[str, Any],
    workflow_signals: Sequence[Mapping[str, Any]],
) -> str:
    """Bind the frozen workflow signal set to its atom, policy, and adapter.

    Signal order is normalized by name; every value-state and provenance field
    remains hash-significant. / 将冻结的工作流信号集绑定到任务原子、策略与适配器；
    信号按名称规范排序，值状态与来源字段全部参与哈希。
    """

    ordered_signals = sorted(
        (deepcopy(dict(item)) for item in workflow_signals),
        key=lambda item: str(item.get("signal", "")),
    )
    return artifact_fingerprint(
        {
            "task_atom_id": task_atom_id,
            "workflow_policy_binding": dict(workflow_policy_binding),
            "adapter_binding": dict(adapter_binding),
            "workflow_signals": ordered_signals,
        }
    )


@lru_cache(maxsize=None)
def _validator(kind: str) -> Draft202012Validator:
    try:
        filename = _SCHEMA_FILES[kind]
    except KeyError as exc:
        raise ValueError(f"unknown reasoning artifact kind / 未知推理制品类型: {kind}") from exc
    path = Path(__file__).resolve().parents[1] / "schemas" / filename
    with path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_schema(kind: str, artifact: Mapping[str, Any]) -> None:
    """Validate one artifact against its Draft 2020-12 schema / 按 Draft 2020-12 校验制品。"""

    if not isinstance(artifact, Mapping):
        raise ArtifactValidationError(["artifact must be an object / 制品必须是对象"])
    errors = sorted(_validator(kind).iter_errors(artifact), key=lambda item: list(item.path))
    if errors:
        formatted = []
        for error in errors:
            path = "/" + "/".join(str(part) for part in error.absolute_path)
            formatted.append(f"{path or '/'}: {error.message}")
        raise ArtifactValidationError(formatted)


def validate_artifact_hash(kind: str, artifact: Mapping[str, Any]) -> None:
    """Reject a supplied top-level digest that cannot be reproduced / 拒绝无法重算的顶层摘要。"""

    try:
        hash_field = _HASH_FIELDS[kind]
    except KeyError as exc:
        raise ValueError(f"artifact kind has no self hash / 制品类型没有自身哈希: {kind}") from exc
    supplied = artifact.get(hash_field)
    expected = artifact_fingerprint(artifact, hash_field)
    if supplied != expected:
        raise ArtifactValidationError(
            [
                f"{hash_field} mismatch: expected {expected}, got {supplied} / "
                f"{hash_field} 不匹配"
            ]
        )


def _seal_nested_hash(
    record: dict[str, Any],
    hash_field: str,
    *,
    label: str,
) -> None:
    """Fill a missing nested digest and reject a conflicting supplied digest.

    / 填充缺失的嵌套摘要，并拒绝与记录内容冲突的外部摘要。
    """

    expected = artifact_fingerprint(record, hash_field)
    supplied = record.get(hash_field)
    if supplied is not None and supplied != expected:
        raise ArtifactValidationError(
            [f"supplied {label} does not match content / 外部提供的 {label} 与内容不匹配"]
        )
    record[hash_field] = expected


def _seal_reasoning_result_nested_hashes(result: dict[str, Any]) -> None:
    """Seal independently verifiable nested reasoning-result records.

    External source digests (``evidence_hash``) and stable step identities
    (``step_hash``) are deliberately preserved. ``record_hash`` protects the
    complete metadata envelope, while inline output content has its own
    reproducible digest.
    / 封存可独立校验的结果嵌套记录。外部来源摘要 ``evidence_hash`` 与稳定步骤身份
    ``step_hash`` 保持不变；``record_hash`` 保护完整元数据，内联输出内容另行计算摘要。
    """

    for evidence in result.get("evidence", ()):
        if isinstance(evidence, dict):
            _seal_nested_hash(evidence, "record_hash", label="evidence record_hash")
    for step in result.get("steps", ()):
        if isinstance(step, dict):
            _seal_nested_hash(step, "record_hash", label="step record_hash")
    output = result.get("output")
    if not isinstance(output, dict):
        return
    content = output.get("content")
    if not isinstance(content, Mapping) or content.get("state") not in {
        "observed",
        "observed_zero",
    }:
        return
    expected = artifact_fingerprint(content)
    supplied = output.get("content_hash")
    if supplied is not None and supplied != expected:
        raise ArtifactValidationError(
            [
                "supplied output content_hash does not match content / "
                "外部提供的输出 content_hash 与内容不匹配"
            ]
        )
    output["content_hash"] = expected


def build_artifact(kind: str, artifact: Mapping[str, Any]) -> dict[str, Any]:
    """Seal, validate, and return a detached reasoning artifact.

    An existing incorrect digest is rejected instead of silently replaced.
    / 封存、校验并返回独立的推理制品；已有错误摘要会被拒绝而不是静默覆盖。
    """

    try:
        hash_field = _HASH_FIELDS[kind]
    except KeyError as exc:
        raise ValueError(f"artifact kind is not sealable / 制品类型不可封存: {kind}") from exc
    result = deepcopy(dict(artifact))
    if kind == "reasoning_result":
        _seal_reasoning_result_nested_hashes(result)
    expected = artifact_fingerprint(result, hash_field)
    supplied = result.get(hash_field)
    if supplied is not None and supplied != expected:
        raise ArtifactValidationError(
            [f"supplied {hash_field} does not match content / 外部提供的 {hash_field} 与内容不匹配"]
        )
    result[hash_field] = expected
    if kind == "reasoning_contract":
        validate_reasoning_contract(result)
    elif kind == "reasoning_result":
        validate_reasoning_result(result)
    elif kind == "tool_dispatch_envelope":
        validate_tool_dispatch_envelope(result)
    elif kind == "tool_execution_event":
        validate_tool_execution_event(result)
    elif kind == "tool_execution_result":
        validate_tool_execution_result(result)
    elif kind == "workflow_route_envelope":
        validate_workflow_route_envelope(result)
    elif kind == "workflow_route_revision":
        validate_workflow_route_revision(result)
    else:
        validate_schema(kind, result)
        validate_artifact_hash(kind, result)
    return result


def _binding_key(binding: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return binding.get("id"), binding.get("version"), binding.get("hash")


def _content_binding(
    identifier: str,
    version: str,
    content: Mapping[str, Any],
) -> dict[str, str]:
    """Build a content-addressed binding / 构建内容寻址绑定。"""

    return {
        "id": identifier,
        "version": version,
        "hash": artifact_fingerprint(content),
    }


def _observed_binding(value: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if value.get("state") != "observed":
        return None
    nested = value.get("value")
    return nested if isinstance(nested, Mapping) else None


def _configuration(value: Mapping[str, Any]) -> dict[str, Any]:
    return {field: value.get(field) for field in _CONFIGURATION_FIELDS}


def _observed_number(value: Mapping[str, Any]) -> float | None:
    """Return a numeric state value without collapsing unknown into zero.

    / 返回显式数值状态，不把未知值折叠为零。
    """

    if value.get("state") == "observed_zero":
        return 0.0
    if value.get("state") == "observed":
        observed = value.get("value")
        if isinstance(observed, (int, float)) and not isinstance(observed, bool):
            return float(observed)
    return None


def validate_reasoning_contract(contract: Mapping[str, Any]) -> None:
    """Validate contract shape, digest, and cross-field routing authority.

    / 校验契约结构、摘要和跨字段路由权威性。
    """

    validate_schema("reasoning_contract", contract)
    validate_artifact_hash("reasoning_contract", contract)
    errors: list[str] = []
    selected = contract["routing_decision"]["selected_configuration"]
    if _configuration(contract) != _configuration(selected):
        errors.append(
            "routing selected_configuration differs from authoritative contract configuration / "
            "路由选定配置与权威契约配置不一致"
        )
    signals = contract["routing_decision"]["signals"]
    names = [signal["signal"] for signal in signals]
    if len(names) != len(set(names)):
        errors.append("routing signal names must be unique / 路由信号名称必须唯一")
    reasons = contract["routing_decision"]["reasons"]
    reason_codes = [reason["reason_code"] for reason in reasons]
    if len(reason_codes) != len(set(reason_codes)):
        errors.append("routing reason codes must be unique / 路由原因码必须唯一")
    if errors:
        raise ArtifactValidationError(errors)


def validate_workflow_route_envelope(envelope: Mapping[str, Any]) -> None:
    """Validate one composite route envelope and its cross-field safety rules.

    / 校验一个复合路由信封及其跨字段安全规则。
    """

    validate_schema("workflow_route_envelope", envelope)
    validate_artifact_hash("workflow_route_envelope", envelope)
    errors: list[str] = []

    signals = envelope["workflow_signals"]
    signal_names = [item["signal"] for item in signals]
    if len(signal_names) != len(set(signal_names)):
        errors.append(
            "workflow route signal names must be unique / 工作流路由信号名称必须唯一"
        )
    if set(signal_names) != _WORKFLOW_ROUTE_SIGNAL_NAMES:
        missing = sorted(_WORKFLOW_ROUTE_SIGNAL_NAMES - set(signal_names))
        unexpected = sorted(set(signal_names) - _WORKFLOW_ROUTE_SIGNAL_NAMES)
        errors.append(
            "workflow route signals must equal the normative set "
            f"(missing={missing}, unexpected={unexpected}) / "
            "工作流路由信号必须与规范集合完全一致"
        )

    expected_fingerprint = workflow_signal_fingerprint(
        task_atom_id=envelope["task_atom"]["task_atom_id"],
        workflow_policy_binding=envelope["workflow_policy_binding"],
        adapter_binding=envelope["adapter_binding"],
        workflow_signals=signals,
    )
    if envelope["workflow_signal_fingerprint"] != expected_fingerprint:
        errors.append(
            "workflow_signal_fingerprint does not bind the frozen signal set / "
            "workflow_signal_fingerprint 未绑定冻结信号集"
        )

    signal_by_name = {item["signal"]: item["value"] for item in signals}
    task_intent = signal_by_name.get("task_intent", {})
    if task_intent.get("state") == "observed" and task_intent.get("value") != envelope[
        "task_atom"
    ]["primary_intent"]:
        errors.append(
            "observed task intent differs from task atom primary intent / "
            "已观测任务意图与任务原子主意图不一致"
        )
    if task_intent.get("state") != "observed" and envelope[
        "execution_lane"
    ] != "clarification_human_review":
        errors.append(
            "unknown task intent must use clarification_human_review / "
            "任务意图未知时必须进入澄清或人工审核车道"
        )

    reasoning_decision = envelope["reasoning_decision"]
    decision_content = dict(reasoning_decision)
    decision_binding = decision_content.pop("decision_binding")
    expected_decision_hash = artifact_fingerprint(decision_content)
    if decision_binding["hash"] != expected_decision_hash:
        errors.append(
            "reasoning decision binding hash does not match its summary / "
            "推理决定绑定哈希与决定摘要不一致"
        )
    if decision_binding["version"] != envelope["reasoning_policy_binding"]["version"]:
        errors.append(
            "reasoning decision binding version differs from reasoning policy / "
            "推理决定绑定版本与推理策略版本不一致"
        )
    expected_workflow_decision_id = "WORKFLOW_ROUTE_" + artifact_fingerprint(
        {
            "workflow_policy_binding": envelope["workflow_policy_binding"],
            "workflow_signal_fingerprint": envelope["workflow_signal_fingerprint"],
            "reasoning_decision_binding": decision_binding,
        }
    ).removeprefix("sha256:")[:24]
    if envelope["decision_id"] != expected_workflow_decision_id:
        errors.append(
            "workflow decision_id does not match its deterministic inputs / "
            "工作流 decision_id 与确定性输入不一致"
        )

    action_risk = signal_by_name.get("action_risk", {})
    if envelope["action_allowed"]:
        if envelope["task_atom"]["risk_owner_binding"].get("state") != "observed":
            errors.append(
                "authorized action requires an observed risk owner / "
                "授权行动必须具有已观测风险负责人"
            )
        if action_risk.get("state") != "observed" or action_risk.get("value") not in {
            "reversible_write",
            "sensitive_write",
            "irreversible_external_action",
        }:
            errors.append(
                "action_allowed is valid only for an explicit write-action risk / "
                "action_allowed 仅适用于显式写行动风险"
            )
        human_gate = envelope["human_gate"]
        if human_gate is not None and (
            human_gate["status"] != "approved"
            or human_gate["authority_binding"].get("state") != "observed"
        ):
            errors.append(
                "authorized action requires an approved authoritative human gate / "
                "授权行动要求人工闸门已批准且权限已观测"
            )

    if errors:
        raise ArtifactValidationError(errors)


def validate_workflow_route_revision(revision: Mapping[str, Any]) -> None:
    """Validate one append-only workflow route revision event.

    / 校验一个追加式工作流路由修订事件。
    """

    validate_schema("workflow_route_revision", revision)
    validate_artifact_hash("workflow_route_revision", revision)
    errors: list[str] = []
    event_identity_content = dict(revision)
    event_identity_content.pop("revision_event_hash")
    event_identity_content.pop("revision_event_id")
    expected_event_id = "WORKFLOW_ROUTE_REVISION_" + artifact_fingerprint(
        event_identity_content
    ).removeprefix("sha256:")[:24]
    if revision["revision_event_id"] != expected_event_id:
        errors.append(
            "revision_event_id does not match event content / 修订事件标识与事件内容不一致"
        )

    if revision["to_revision"] != revision["from_revision"] + 1:
        errors.append(
            "route revisions must increase by exactly one / 路由修订号必须严格递增一"
        )

    if revision["previous_envelope_binding"]["id"] != revision["from_decision_id"]:
        errors.append(
            "previous envelope binding does not match from_decision_id / "
            "前序路由信封绑定与 from_decision_id 不一致"
        )
    if revision["current_envelope_binding"]["id"] != revision["to_decision_id"]:
        errors.append(
            "current envelope binding does not match to_decision_id / "
            "当前路由信封绑定与 to_decision_id 不一致"
        )

    for side in ("from_route", "to_route"):
        route = revision[side]
        should_have_configuration = route["reasoning_disposition"] == "execute"
        if should_have_configuration != (route["configuration"] is not None):
            errors.append(
                f"{side} reasoning configuration disagrees with disposition / "
                f"{side} 推理配置与处置结果不一致"
            )

    if revision["from_route"] == revision["to_route"] and revision["direction"] != "gate_only":
        errors.append(
            "route revision must change route or gate state / 路由修订必须改变路由或门禁状态"
        )

    if revision["direction"] == "deescalation" and not revision[
        "hysteresis_evidence_bindings"
    ]:
        errors.append(
            "deescalation requires hysteresis evidence / 降级必须具有迟滞证据"
        )

    if errors:
        raise ArtifactValidationError(errors)


def validate_tool_dispatch_envelope(envelope: Mapping[str, Any]) -> None:
    """Validate a tool frontier, selection, admission, and permit.

    / 校验工具能力前沿、候选选择、执行准入与许可。
    """

    validate_schema("tool_dispatch_envelope", envelope)
    validate_artifact_hash("tool_dispatch_envelope", envelope)
    errors: list[str] = []

    checks = envelope["admission_checks"]
    check_names = tuple(item["name"] for item in checks)
    if check_names != _TOOL_ADMISSION_CHECK_ORDER:
        errors.append(
            "admission checks must use the normative order / 准入检查必须使用规范顺序"
        )

    frontier = envelope["frontier"]
    frontier_content = {
        "policy_binding": frontier["policy_binding"],
        "retained_tool_bindings": frontier["retained_tool_bindings"],
        "exclusion_counts": frontier["exclusion_counts"],
    }
    expected_frontier_hash = artifact_fingerprint(frontier_content)
    if frontier["frontier_hash"] != expected_frontier_hash:
        errors.append(
            "frontier hash does not bind its content / 能力前沿哈希未绑定其内容"
        )
    expected_frontier_id = (
        "TOOL_FRONTIER_" + expected_frontier_hash.removeprefix("sha256:")[-24:]
    )
    if frontier["frontier_id"] != expected_frontier_id:
        errors.append(
            "frontier id does not match its content / 能力前沿标识与内容不一致"
        )

    retained_keys = [_binding_key(item) for item in frontier["retained_tool_bindings"]]
    if len(retained_keys) != len(set(retained_keys)):
        errors.append(
            "frontier tool bindings must be unique / 能力前沿工具绑定必须唯一"
        )
    candidates = envelope["candidate_evaluations"]
    candidate_keys = [_binding_key(item["tool_binding"]) for item in candidates]
    if len(candidate_keys) != len(set(candidate_keys)):
        errors.append("candidate tools must be unique / 候选工具必须唯一")
    if not set(candidate_keys).issubset(set(retained_keys)):
        errors.append(
            "candidate tool is outside the capability frontier / 候选工具位于能力前沿之外"
        )
    selected_candidates = [item for item in candidates if item["selected"]]
    selected_binding = _observed_binding(envelope["selected_tool_binding"])
    if selected_binding is None:
        if selected_candidates:
            errors.append(
                "candidate selected without selected_tool_binding / 候选已选中但缺少工具绑定"
            )
    elif len(selected_candidates) != 1 or _binding_key(
        selected_candidates[0]["tool_binding"]
    ) != _binding_key(selected_binding):
        errors.append(
            "selected tool does not match the unique selected candidate / "
            "所选工具与唯一选中候选不一致"
        )

    failed = [item for item in checks if item["status"] == "failed"]
    waiting = [item for item in checks if item["status"] == "waiting"]
    decision = envelope["decision"]
    expected_reasons = [
        item["code"]
        for item in checks
        if item["status"] in {"failed", "waiting"}
    ]
    if envelope["reason_codes"] != expected_reasons:
        errors.append(
            "reason codes must preserve failed/waiting admission order / "
            "原因代码必须保留失败与等待准入顺序"
        )
    if decision == "allow" and (failed or waiting):
        errors.append("allowed dispatch has failed or waiting checks / 已放行调度仍有失败或等待项")
    if decision == "reject" and not failed:
        errors.append("rejected dispatch lacks a failed check / 已拒绝调度缺少失败项")
    if decision == "wait" and (failed or not waiting):
        errors.append("waiting dispatch must have waiting and no failed checks / 等待调度必须有等待项且无失败项")
    permit = _observed_binding(envelope["permit_binding"])
    if (decision == "allow") != (permit is not None):
        errors.append("permit presence disagrees with admission decision / 许可存在性与准入决定不一致")
    if envelope["execution_contract"]["execution_ready"] != (decision == "allow"):
        errors.append("execution_ready disagrees with admission decision / execution_ready 与准入决定不一致")

    dispatch_identity = {
        "intent_binding": envelope["intent_binding"],
        "actor_binding": envelope["actor_binding"],
        "catalog_binding": envelope["catalog_binding"],
        "frontier_hash": frontier["frontier_hash"],
        "candidate_bindings": [item["tool_binding"] for item in candidates],
        "admission_checks": checks,
        "created_at": envelope["created_at"],
    }
    expected_dispatch_id = (
        "TOOL_DISPATCH_"
        + artifact_fingerprint(dispatch_identity).removeprefix("sha256:")[:24]
    )
    if envelope["dispatch_id"] != expected_dispatch_id:
        errors.append(
            "dispatch id does not match deterministic inputs / 调度标识与确定性输入不一致"
        )

    contract = envelope["execution_contract"]
    is_write = contract["side_effect_class"] in _TOOL_WRITE_SIDE_EFFECTS
    if is_write:
        if not envelope["target_resources"]:
            errors.append("write dispatch requires target resources / 写调度必须声明目标资源")
        if not contract["lease_required"]:
            errors.append("write dispatch requires an execution lease / 写调度必须取得执行租约")
        if _observed_binding(contract["idempotency_binding"]) is None:
            errors.append("write dispatch requires idempotency / 写调度必须具备幂等绑定")
        if decision == "allow" and _observed_binding(
            contract["state_evidence_binding"]
        ) is None:
            errors.append("allowed write lacks state evidence / 已放行写动作缺少状态证据")
        if decision == "allow" and _observed_binding(
            contract["sandbox_binding"]
        ) is None:
            errors.append("allowed write lacks sandbox binding / 已放行写动作缺少沙箱绑定")
    elif contract["lease_required"]:
        errors.append("read-only or draft dispatch cannot require a lease / 只读或草稿调度不得要求租约")
    if decision == "allow":
        if selected_binding is None:
            errors.append("allowed dispatch lacks a selected tool / 已放行调度缺少所选工具")
        if _observed_binding(contract["authorization_binding"]) is None:
            errors.append("allowed dispatch lacks authorization binding / 已放行调度缺少授权绑定")
        if _observed_binding(contract["executor_binding"]) is None:
            errors.append("allowed dispatch lacks executor binding / 已放行调度缺少执行器绑定")
        if contract["side_effect_class"] in {
            "sensitive_write",
            "irreversible_external",
        } and _observed_binding(contract["approval_binding"]) is None:
            errors.append("high-risk write lacks bound approval / 高风险写动作缺少绑定审批")
        if permit is not None:
            permit_content = {
                "dispatch_id": envelope["dispatch_id"],
                "intent_binding": envelope["intent_binding"],
                "tool_binding": selected_binding,
                "actor_binding": envelope["actor_binding"],
                "authorization_binding": contract["authorization_binding"],
                "approval_binding": contract["approval_binding"],
                "state_evidence_binding": contract["state_evidence_binding"],
                "idempotency_binding": contract["idempotency_binding"],
                "permit_expires_at": contract["permit_expires_at"],
            }
            expected_permit = _content_binding(
                envelope["dispatch_id"] + "_PERMIT",
                "1.0.0",
                permit_content,
            )
            if permit != expected_permit:
                errors.append(
                    "permit binding does not seal its execution context / "
                    "许可绑定未封存其执行上下文"
                )

    try:
        created = datetime.fromisoformat(
            envelope["created_at"].replace("Z", "+00:00")
        )
        expires = datetime.fromisoformat(
            contract["permit_expires_at"].replace("Z", "+00:00")
        )
        if expires <= created:
            errors.append("permit expiry must follow creation / 许可过期必须晚于创建")
    except ValueError:
        pass

    if errors:
        raise ArtifactValidationError(errors)


def validate_tool_execution_event(event: Mapping[str, Any]) -> None:
    """Validate one standard tool lifecycle event / 校验一个标准工具生命周期事件。"""

    validate_schema("tool_execution_event", event)
    validate_artifact_hash("tool_execution_event", event)
    errors: list[str] = []
    expected_event_id = (
        "TOOL_EVENT_"
        + artifact_fingerprint(
            {"run_id": event["run_id"], "event_key": event["event_key"]}
        ).removeprefix("sha256:")[:24]
    )
    if event["event_id"] != expected_event_id:
        errors.append("event id does not match run and event key / 事件标识与运行和事件键不一致")
    if event["stage"] != _TOOL_EVENT_STAGE[event["event_type"]]:
        errors.append("event type and stage disagree / 事件类型与阶段不一致")
    names = tuple(item["name"] for item in event["admission_checks"])
    if names != _TOOL_ADMISSION_CHECK_ORDER:
        errors.append("event admission checks are not normative / 事件准入检查不符合规范")
    if _observed_binding(event["dispatch_binding"]) is None:
        errors.append("tool event lacks dispatch binding / 工具事件缺少调度绑定")
    is_write = event["side_effect_class"] in _TOOL_WRITE_SIDE_EFFECTS
    if event["event_type"] == "tool_execution_started":
        if event["decision"] != "allow":
            errors.append("execution start lacks allow decision / 执行开始缺少放行决定")
        if _observed_binding(event["permit_binding"]) is None:
            errors.append("execution start lacks permit / 执行开始缺少许可")
        if is_write and _observed_binding(event["lease_binding"]) is None:
            errors.append("write execution start lacks lease / 写执行开始缺少租约")
    result_events = {
        "tool_execution_succeeded": "success",
        "tool_result_reused": "reused_success",
        "tool_execution_rejected": "rejected",
        "tool_execution_failed": "explicit_failure",
        "tool_execution_unknown": "unknown",
        "tool_execution_partial": "partial_success",
        "tool_execution_waiting": "waiting",
    }
    if event["event_type"] in result_events:
        if event["result_classification"] is None:
            errors.append("result event lacks classification / 结果事件缺少分类")
        elif event["result_classification"] != result_events[event["event_type"]]:
            errors.append(
                "result event type disagrees with classification / "
                "结果事件类型与结果分类不一致"
            )
        if _observed_binding(event["result_binding"]) is None:
            errors.append("result event lacks result binding / 结果事件缺少结果绑定")
    elif event["event_type"] != "side_effect_confirmed" and event[
        "result_classification"
    ] is not None:
        errors.append("non-result event carries result classification / 非结果事件携带结果分类")
    if event["event_type"] == "side_effect_confirmed":
        if event["result_classification"] not in {"success", "reused_success"}:
            errors.append("confirmed side effect lacks successful result / 已确认副作用缺少成功结果")
        if _observed_binding(event["result_binding"]) is None:
            errors.append("confirmed side effect lacks result binding / 已确认副作用缺少结果绑定")
    if errors:
        raise ArtifactValidationError(errors)


def validate_tool_execution_result(result: Mapping[str, Any]) -> None:
    """Validate result certainty and retry safety / 校验结果确定性与重试安全。"""

    validate_schema("tool_execution_result", result)
    validate_artifact_hash("tool_execution_result", result)
    errors: list[str] = []
    identity = {
        "dispatch_binding": result["dispatch_binding"],
        "attempt_id": result["attempt_id"],
        "classification": result["classification"],
        "completed_at": result["execution_completed_at"],
        "reused_result_binding": result["reused_result_binding"],
    }
    expected_result_id = (
        "TOOL_RESULT_"
        + artifact_fingerprint(identity).removeprefix("sha256:")[:24]
    )
    if result["result_id"] != expected_result_id:
        errors.append("result id does not match deterministic inputs / 结果标识与确定性输入不一致")
    if result["created_at"] != result["execution_completed_at"]:
        errors.append("result creation must equal completion time / 结果创建时间必须等于完成时间")
    classification = result["classification"]
    started = result["execution_started_at"]
    side_effect_class = result["side_effect_class"]
    is_write = side_effect_class in _TOOL_WRITE_SIDE_EFFECTS
    side_effect = result["side_effect_state"]
    error = result["error"]
    lease = _observed_binding(result["lease_binding"])
    permit = _observed_binding(result["permit_binding"])
    if classification in {"rejected", "reused_success"} and started is not None:
        errors.append("non-executed result cannot have start time / 未执行结果不得包含开始时间")
    if classification in {
        "success",
        "explicit_failure",
        "partial_success",
    } and started is None:
        errors.append("executed result requires start time / 已执行结果必须包含开始时间")
    if classification in {
        "success",
        "reused_success",
        "explicit_failure",
        "unknown",
        "partial_success",
    }:
        if permit is None:
            errors.append("executed result requires a permit / 已执行结果必须包含许可")
        if is_write and lease is None:
            errors.append("write result requires a durable lease / 写结果必须包含持久租约")
    if classification == "rejected" and side_effect != "none":
        errors.append("rejected result cannot claim side effect / 拒绝结果不得声称副作用")
    if not is_write:
        if side_effect != "none":
            errors.append("read-only result cannot claim a side effect / 只读结果不得声称副作用")
        if result["actual_side_effects"]:
            errors.append("read-only result cannot record side effects / 只读结果不得记录副作用")
    elif classification in {"success", "reused_success"} and side_effect != "confirmed":
        errors.append("successful write requires confirmed side effect / 写成功必须确认副作用")
    elif classification == "explicit_failure" and side_effect != "confirmed_absent":
        errors.append("explicit write failure must confirm no side effect / 写明确失败必须确认无副作用")
    elif classification == "unknown" and side_effect != "unknown":
        errors.append("unknown write result requires unknown side-effect state / 写结果未知必须标记副作用未知")
    elif classification == "partial_success" and side_effect != "partial":
        errors.append("partial write result requires partial side-effect state / 写部分成功必须标记部分副作用")
    elif classification == "waiting" and side_effect not in {"none", "unknown"}:
        errors.append("waiting write has invalid side-effect state / 写等待结果的副作用状态无效")
    if classification == "success" and error is not None:
        errors.append("successful result cannot carry error / 成功结果不得携带错误")
    if classification == "unknown":
        if result["next_action"] != "reconcile":
            errors.append("unknown result must reconcile before retry / 结果未知必须先核验再重试")
        if error is not None and error["retryable"]:
            errors.append("unknown result cannot be directly retryable / 结果未知不得直接重试")
    if classification == "partial_success" and result["next_action"] not in {
        "compensate",
        "human_review",
    }:
        errors.append("partial success requires compensation or human review / 部分成功必须补偿或人工处理")
    reused = _observed_binding(result["reused_result_binding"])
    if (classification == "reused_success") != (reused is not None):
        errors.append("reused-result binding disagrees with classification / 复用结果绑定与分类不一致")
    if result["actual_side_effects"] and side_effect not in {"confirmed", "partial"}:
        errors.append("side-effect records require confirmed or partial state / 副作用记录要求确认或部分确认状态")
    try:
        completed = datetime.fromisoformat(
            result["execution_completed_at"].replace("Z", "+00:00")
        )
        if started is not None:
            started_at = datetime.fromisoformat(started.replace("Z", "+00:00"))
            if completed < started_at:
                errors.append("execution completion predates start / 执行完成早于开始")
    except ValueError:
        pass
    if errors:
        raise ArtifactValidationError(errors)


def validate_reasoning_event(event: Mapping[str, Any]) -> None:
    """Validate one event plus cross-envelope transition invariants.

    / 校验单条事件及跨信封状态转换不变量。
    """

    validate_schema("reasoning_event", event)
    errors: list[str] = []
    if event["event_type"] == "state_transitioned":
        data = event["payload"]["data"]
        if data["from_state"] != event["previous_state"]:
            errors.append(
                "payload.from_state differs from envelope.previous_state / "
                "payload.from_state 与信封 previous_state 不一致"
            )
        if data["to_state"] != event["next_state"]:
            errors.append(
                "payload.to_state differs from envelope.next_state / "
                "payload.to_state 与信封 next_state 不一致"
            )
        if event["workflow_state"] != event["next_state"]:
            errors.append(
                "workflow_state differs from transition next_state / "
                "workflow_state 与转换 next_state 不一致"
            )
    if errors:
        raise ArtifactValidationError(errors)


def _parse_datetime(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp lacks timezone")
    return parsed.astimezone(timezone.utc)


def _evidence_sufficiency_failures(
    result: Mapping[str, Any],
    requirements: Mapping[str, Any],
    *,
    evaluated_at: datetime,
) -> list[str]:
    evidence = result["evidence"]
    claims = result["claims"]
    failures: list[str] = []
    source_refs = {item["source"]["source_ref"] for item in evidence}
    if len(source_refs) < requirements["min_independent_sources"]:
        failures.append("insufficient independent sources / 独立来源不足")
    evidence_types = {item["evidence_type"] for item in evidence}
    missing_types = set(requirements["required_evidence_types"]) - evidence_types
    if missing_types:
        failures.append(
            "missing evidence types / 缺少证据类型: " + ", ".join(sorted(missing_types))
        )
    maximum_age = requirements["max_source_age_seconds"]
    for item in evidence:
        valid_at = _parse_datetime(item["valid_at"])
        retrieved_at = _parse_datetime(item["retrieved_at"])
        captured_at = _parse_datetime(item["captured_at"])
        assessed_at = _parse_datetime(item["freshness"]["assessed_at"])
        age = (evaluated_at - valid_at).total_seconds()
        if age < -300:
            failures.append(f"future evidence / 未来证据: {item['evidence_id']}")
        elif age > maximum_age:
            failures.append(f"stale evidence / 过期证据: {item['evidence_id']}")
        for timestamp_name, timestamp_value in (
            ("retrieved_at", retrieved_at),
            ("captured_at", captured_at),
            ("freshness.assessed_at", assessed_at),
        ):
            if (timestamp_value - evaluated_at).total_seconds() > 300:
                failures.append(
                    f"future evidence audit time / 证据审计时间来自未来: "
                    f"{item['evidence_id']}:{timestamp_name}"
                )
        if item["freshness"]["status"] != "fresh":
            failures.append(
                f"freshness is not established / 新鲜度未确认: {item['evidence_id']}"
            )
        if item["integrity_score"] < requirements["min_integrity_score"]:
            failures.append(f"low-integrity evidence / 低完整性证据: {item['evidence_id']}")
    supporting_evidence: dict[str, set[tuple[str, str, str]]] = {}
    for item in evidence:
        evidence_key = (
            item["evidence_id"],
            item["evidence_version"],
            item["evidence_hash"],
        )
        for claim_binding in item["claim_bindings"]:
            if claim_binding["relation"] == "supports":
                supporting_evidence.setdefault(
                    claim_binding["claim_id"],
                    set(),
                ).add(evidence_key)
    applicable_claims = [claim for claim in claims if claim["status"] != "not_applicable"]
    supported_claims = [
        claim
        for claim in applicable_claims
        if claim["status"] == "supported"
        and any(
            _binding_key(binding)
            in supporting_evidence.get(claim["claim_id"], set())
            for binding in claim["evidence_bindings"]
        )
    ]
    coverage = 1.0 if not applicable_claims else len(supported_claims) / len(applicable_claims)
    if coverage < requirements["min_claim_coverage_ratio"]:
        failures.append("claim evidence coverage is insufficient / 声明证据覆盖率不足")
    unresolved_critical = sum(
        claim["criticality"] == "critical" and claim["status"] == "unresolved"
        for claim in claims
    )
    if unresolved_critical > requirements["max_unresolved_critical_claims"]:
        failures.append("too many unresolved critical claims / 未解决关键声明过多")
    return failures


def evidence_sufficiency_failures(
    result: Mapping[str, Any],
    requirements: Mapping[str, Any],
    *,
    evaluated_at: datetime | str | None = None,
) -> tuple[str, ...]:
    """Recompute the measurable evidence gate for a result envelope.

    / 为结果信封重算可度量的证据门。
    """

    if evaluated_at is None:
        evaluated = _parse_datetime(str(result["created_at"]))
    elif isinstance(evaluated_at, str):
        evaluated = _parse_datetime(evaluated_at)
    elif evaluated_at.tzinfo is None:
        raise ValueError("evaluated_at must carry a timezone / evaluated_at 必须包含时区")
    else:
        evaluated = evaluated_at.astimezone(timezone.utc)
    return tuple(
        _evidence_sufficiency_failures(
            result,
            requirements,
            evaluated_at=evaluated,
        )
    )


def validate_reasoning_result(
    result: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
) -> None:
    """Validate a result's schema, digest, bindings, and release-gate truth.

    Supplying the contract additionally recomputes evidence sufficiency and
    verifies identity, configuration, risk, and budget lineage.
    / 校验结果 Schema、摘要、绑定和放行门真实性；提供契约时还会重算证据充分性，
    并校验标识、配置、风险和预算血缘。
    """

    validate_schema("reasoning_result", result)
    validate_artifact_hash("reasoning_result", result)
    errors: list[str] = []
    terminal_state = result["terminal_state"]
    created_at = _parse_datetime(result["created_at"])
    release_gate_evaluated_at = (
        None
        if "release_gate_evaluated_at" not in result
        else _parse_datetime(result["release_gate_evaluated_at"])
    )
    if (
        release_gate_evaluated_at is not None
        and created_at < release_gate_evaluated_at
    ):
        errors.append(
            "result creation predates the release gate / 结果创建时间早于放行门"
        )
    contract_key = _binding_key(result["contract_binding"])
    candidate = _observed_binding(result["candidate_binding"])
    candidate_key = None if candidate is None else _binding_key(candidate)

    evidence_by_key = {
        (item["evidence_id"], item["evidence_version"], item["evidence_hash"]): item
        for item in result["evidence"]
    }
    declared_evidence = [_binding_key(item) for item in result["evidence_bindings"]]
    if declared_evidence != list(evidence_by_key):
        errors.append(
            "evidence_bindings must exactly match ordered evidence records / "
            "evidence_bindings 必须与有序证据记录完全一致"
        )
    claim_ids = [claim["claim_id"] for claim in result["claims"]]
    claims_by_id = {claim["claim_id"]: claim for claim in result["claims"]}
    if len(claim_ids) != len(set(claim_ids)):
        errors.append("duplicate claim identifiers / 声明标识重复")

    validation_keys = [
        (item["validation_id"], item["validation_version"], item["validation_hash"])
        for item in result["validations"]
    ]
    validation_by_key = {
        key: item for key, item in zip(validation_keys, result["validations"])
    }
    if len(validation_keys) != len(set(validation_keys)):
        errors.append("duplicate validation bindings / 验证绑定重复")
    for item in result["evidence"]:
        expected_record_hash = artifact_fingerprint(item, "record_hash")
        if item["record_hash"] != expected_record_hash:
            errors.append(
                f"evidence record hash mismatch / 证据记录哈希不匹配: "
                f"{item['evidence_id']}"
            )
        if _binding_key(item["contract_binding"]) != contract_key:
            errors.append(f"evidence contract binding mismatch / 证据契约绑定不匹配: {item['evidence_id']}")
        item_candidate = _observed_binding(item["candidate_binding"])
        if terminal_state == "completed" and (
            item_candidate is None or _binding_key(item_candidate) != candidate_key
        ):
            errors.append(f"evidence candidate binding mismatch / 证据候选绑定不匹配: {item['evidence_id']}")
        item_key = (
            item["evidence_id"],
            item["evidence_version"],
            item["evidence_hash"],
        )
        for claim_binding in item["claim_bindings"]:
            claim = claims_by_id.get(claim_binding["claim_id"])
            if claim is None:
                errors.append(
                    f"evidence references unknown claim / 证据引用未知声明: "
                    f"{item['evidence_id']}:{claim_binding['claim_id']}"
                )
            elif item_key not in {
                _binding_key(binding) for binding in claim["evidence_bindings"]
            }:
                errors.append(
                    f"evidence-to-claim binding is not reciprocal / "
                    f"证据到声明绑定未双向闭合: {item['evidence_id']}:{claim_binding['claim_id']}"
                )

    for validation in result["validations"]:
        expected_validation_hash = artifact_fingerprint(
            validation,
            "validation_hash",
        )
        if validation["validation_hash"] != expected_validation_hash:
            errors.append(
                f"validation hash mismatch / 验证哈希不匹配: {validation['validation_id']}"
            )
        started_at = _parse_datetime(validation["started_at"])
        ended_at = _parse_datetime(validation["ended_at"])
        checked_at = _parse_datetime(validation["checked_at"])
        if started_at > ended_at or ended_at > checked_at:
            errors.append(
                f"validation timestamps are not monotonic / 验证时间不单调: "
                f"{validation['validation_id']}"
            )
        if (
            release_gate_evaluated_at is not None
            and ended_at > release_gate_evaluated_at
        ):
            errors.append(
                f"validation ended after the release gate / 验证结束晚于放行门: "
                f"{validation['validation_id']}"
            )
        if _binding_key(validation["contract_binding"]) != contract_key:
            errors.append(
                f"validation contract binding mismatch / 验证契约绑定不匹配: {validation['validation_id']}"
            )
        if candidate_key is not None and _binding_key(validation["candidate_binding"]) != candidate_key:
            errors.append(
                f"validation candidate binding mismatch / 验证候选绑定不匹配: {validation['validation_id']}"
            )
        for binding in validation["evidence_bindings"]:
            if _binding_key(binding) not in evidence_by_key:
                errors.append(
                    f"validation references unknown evidence / 验证引用未知证据: {validation['validation_id']}"
                )

    release_gate = result["release_gate"]
    if release_gate["basis"] == "mandatory_validators":
        for gate in release_gate["validator_gates"]:
            binding = _observed_binding(gate["validation_binding"])
            if binding is None:
                if gate["result"] != "not_run":
                    errors.append("executed validator gate lacks validation binding / 已执行验证门缺少验证绑定")
                continue
            validation = validation_by_key.get(_binding_key(binding))
            if validation is None:
                errors.append("validator gate references unknown validation / 验证门引用未知验证记录")
                continue
            if _binding_key(gate["validator_binding"]) != _binding_key(validation["validator_binding"]):
                errors.append("validator gate and validation identify different validators / 验证门与验证记录的验证器不同")
            if gate["result"] != validation["result"]:
                errors.append("validator gate result differs from validation record / 验证门结果与验证记录不一致")

    step_ids = [step["step_id"] for step in result["steps"]]
    if len(step_ids) != len(set(step_ids)):
        errors.append("duplicate step identifiers / 步骤标识重复")
    for step in result["steps"]:
        expected_record_hash = artifact_fingerprint(step, "record_hash")
        if step["record_hash"] != expected_record_hash:
            errors.append(
                f"step record hash mismatch / 步骤记录哈希不匹配: "
                f"{step['step_id']}"
            )
        if _binding_key(step["contract_binding"]) != contract_key:
            errors.append(f"step contract binding mismatch / 步骤契约绑定不匹配: {step['step_id']}")
        step_candidate = _observed_binding(step["candidate_binding"])
        if terminal_state == "completed" and (
            step_candidate is None or _binding_key(step_candidate) != candidate_key
        ):
            errors.append(f"step candidate binding mismatch / 步骤候选绑定不匹配: {step['step_id']}")
        for field_name in ("input_evidence_bindings", "output_evidence_bindings"):
            for binding in step[field_name]:
                if _binding_key(binding) not in evidence_by_key:
                    errors.append(f"step references unknown evidence / 步骤引用未知证据: {step['step_id']}")
        for binding in step["validation_bindings"]:
            if _binding_key(binding) not in validation_by_key:
                errors.append(f"step references unknown validation / 步骤引用未知验证: {step['step_id']}")

    for claim in result["claims"]:
        for binding in claim["evidence_bindings"]:
            binding_key = _binding_key(binding)
            if binding_key not in evidence_by_key:
                errors.append(f"claim references unknown evidence / 声明引用未知证据: {claim['claim_id']}")
                continue
            evidence_record = evidence_by_key[binding_key]
            if claim["claim_id"] not in {
                item["claim_id"] for item in evidence_record["claim_bindings"]
            }:
                errors.append(
                    f"claim-to-evidence binding is not reciprocal / "
                    f"声明到证据绑定未双向闭合: {claim['claim_id']}"
                )

    output_content = result["output"]["content"]
    if output_content["state"] in {"observed", "observed_zero"}:
        expected_content_hash = artifact_fingerprint(output_content)
        if result["output"].get("content_hash") != expected_content_hash:
            errors.append(
                "output content hash mismatch / 输出内容哈希不匹配"
            )

    execution = result["execution"]
    current_configuration = _configuration(execution["initial_configuration"])
    switch_counts: dict[str, int] = {}
    previous_switch_time: datetime | None = None
    for switch in execution["mode_switches"]:
        switch_id = switch["switch_id"]
        switch_counts[switch_id] = switch_counts.get(switch_id, 0) + 1
        if _configuration(switch["from"]) != current_configuration:
            errors.append(
                f"mode-switch chain source mismatch / 模式切换链起点不匹配: {switch_id}"
            )
        current_configuration = _configuration(switch["to"])
        switched_at = _parse_datetime(switch["switched_at"])
        if previous_switch_time is not None and switched_at < previous_switch_time:
            errors.append(
                f"mode-switch timestamps are not monotonic / 模式切换时间不单调: {switch_id}"
            )
        if switched_at > created_at:
            errors.append(
                f"mode switch occurs after result creation / 模式切换晚于结果创建: {switch_id}"
            )
        previous_switch_time = switched_at
    if current_configuration != _configuration(execution["final_configuration"]):
        errors.append(
            "final configuration does not close the mode-switch chain / "
            "最终配置未闭合模式切换链"
        )

    accounting = result["budget_accounting"]
    expected_exhausted: set[str] = set()
    step_totals = {name: 0.0 for name in _BUDGET_FIELDS}
    step_totals_known = {name: True for name in _BUDGET_FIELDS}
    for step in result["steps"]:
        for name in _BUDGET_FIELDS:
            amount = _observed_number(step["resource_use"][name])
            if amount is None:
                step_totals_known[name] = False
            else:
                step_totals[name] += amount
    for name in _BUDGET_FIELDS:
        limit = _observed_number(accounting["limits"][name])
        used = _observed_number(accounting["used"][name])
        if limit is not None and used is not None:
            if used > limit:
                errors.append(f"budget usage exceeds limit / 预算使用超过上限: {name}")
            if used >= limit:
                expected_exhausted.add(name)
        if used is not None and step_totals_known[name] and step_totals[name] > used:
            errors.append(
                f"step resource total exceeds run accounting / "
                f"步骤资源合计超过运行核算: {name}"
            )
    if set(accounting["exhausted_dimensions"]) != expected_exhausted:
        errors.append(
            "exhausted budget dimensions differ from recomputed accounting / "
            "耗尽预算维度与重算核算不一致"
        )

    if contract is not None:
        try:
            validate_reasoning_contract(contract)
        except ArtifactValidationError as exc:
            errors.extend(f"contract: {error}" for error in exc.errors)
            raise ArtifactValidationError(errors) from exc
        expected_contract_key = (
            contract.get("contract_id"),
            contract.get("contract_version"),
            contract.get("contract_hash"),
        )
        if contract_key != expected_contract_key:
            errors.append("result does not bind the supplied contract / 结果未绑定所提供契约")
        for identity in ("workflow_id", "task_id", "run_id", "scene_id"):
            if result[identity] != contract[identity]:
                errors.append(f"{identity} differs between contract and result / 契约与结果的 {identity} 不一致")
        if result["risk_level"] != contract["governance"]["risk_level"]:
            errors.append("risk level differs between contract and result / 契约与结果风险级别不一致")
        if result["execution"]["initial_configuration"] != _configuration(contract):
            errors.append("result initial configuration differs from contract / 结果初始配置与契约不一致")
        switch_rules = {
            item["switch_id"]: item for item in contract["allowed_mode_switches"]
        }
        for switch in execution["mode_switches"]:
            switch_id = switch["switch_id"]
            declared_switch = switch_rules.get(switch_id)
            if declared_switch is None:
                errors.append(
                    f"mode switch is not declared by the contract / "
                    f"模式切换未在契约中声明: {switch_id}"
                )
                continue
            if any(
                switch[field_name] != declared_switch[field_name]
                for field_name in ("from", "to", "trigger")
            ):
                errors.append(
                    f"mode switch differs from contract rule / "
                    f"模式切换与契约规则不一致: {switch_id}"
                )
            expected_switch_binding = (
                switch_id,
                contract["contract_version"],
                artifact_fingerprint(declared_switch),
            )
            if _binding_key(switch["switch_rule_binding"]) != expected_switch_binding:
                errors.append(
                    f"mode-switch rule binding differs from contract / "
                    f"模式切换规则绑定与契约不一致: {switch_id}"
                )
            if switch_counts[switch_id] > declared_switch["max_switches"]:
                errors.append(
                    f"mode-switch count exceeds contract / "
                    f"模式切换次数超过契约: {switch_id}"
                )
        declared_validators = {
            item["validator_id"]: item for item in contract["validators"]
        }
        gate_by_validator_id: dict[str, Mapping[str, Any]] = {}
        if release_gate["basis"] == "mandatory_validators":
            for gate in release_gate["validator_gates"]:
                validator_id = gate["validator_binding"]["id"]
                if validator_id in gate_by_validator_id:
                    errors.append(
                        f"duplicate validator gate / 验证器门重复: {validator_id}"
                    )
                gate_by_validator_id[validator_id] = gate
                declared = declared_validators.get(validator_id)
                if declared is None:
                    errors.append(
                        f"validator gate is not declared by the contract / "
                        f"验证器门未在契约中声明: {validator_id}"
                    )
                    continue
                expected_binding = (
                    declared["validator_id"],
                    declared["validator_version"],
                    artifact_fingerprint(declared),
                )
                if _binding_key(gate["validator_binding"]) != expected_binding:
                    errors.append(
                        f"validator gate binding differs from contract / "
                        f"验证器门绑定与契约不一致: {validator_id}"
                    )
                if gate["required"] is not declared["required"]:
                    errors.append(
                        f"validator gate required flag differs from contract / "
                        f"验证器门必选标记与契约不一致: {validator_id}"
                    )
            for validator_id, declared in declared_validators.items():
                if declared["required"] and validator_id not in gate_by_validator_id:
                    errors.append(
                        f"mandatory validator gate is missing / 缺少必选验证器门: "
                        f"{validator_id}"
                    )

        for validation in result["validations"]:
            validator_id = validation["validator_binding"]["id"]
            declared = declared_validators.get(validator_id)
            if declared is None:
                errors.append(
                    f"validation uses an undeclared validator / 验证使用未声明验证器: "
                    f"{validator_id}"
                )
                continue
            expected_binding = (
                declared["validator_id"],
                declared["validator_version"],
                artifact_fingerprint(declared),
            )
            if _binding_key(validation["validator_binding"]) != expected_binding:
                errors.append(
                    f"validation validator binding differs from contract / "
                    f"验证记录的验证器绑定与契约不一致: {validation['validation_id']}"
                )
            expected_criteria_binding = (
                f"{declared['validator_id']}-criteria",
                declared["validator_version"],
                artifact_fingerprint(declared["pass_criteria"]),
            )
            if _binding_key(validation["criteria_binding"]) != expected_criteria_binding:
                errors.append(
                    f"validation criteria binding differs from contract / "
                    f"验证准则绑定与契约不一致: {validation['validation_id']}"
                )
            if (
                declared["validator_type"] == "human"
                and validation["result"] in {"passed", "conditionally_passed"}
                and (
                    validation["actor_binding"]["state"] != "observed"
                    or validation["authority_binding"]["state"] != "observed"
                )
            ):
                errors.append(
                    f"passing human validation lacks actor or authority / "
                    f"人工验证通过缺少执行人或权限绑定: {validation['validation_id']}"
                )
        contract_budget = contract["budget"]
        for result_name, contract_name in _BUDGET_FIELDS.items():
            expected_limit = contract_budget[contract_name]
            observed = result["budget_accounting"]["limits"][result_name]
            if expected_limit is None:
                if observed["state"] not in {"missing", "unknown", "not_applicable"}:
                    errors.append(f"budget limit mismatch / 预算上限不一致: {result_name}")
            elif observed != {"state": "observed", "value": expected_limit}:
                errors.append(f"budget limit mismatch / 预算上限不一致: {result_name}")
        direct_rule = contract.get("direct_release_rule")
        if release_gate["basis"] == "direct_release_rule" and direct_rule is None:
            errors.append("direct release result lacks contract rule / 直接放行结果的契约缺少规则")
            requirements = contract["evidence_sufficiency"]
        elif release_gate["basis"] == "direct_release_rule":
            requirements = direct_rule["required_evidence"]
        else:
            requirements = contract["evidence_sufficiency"]
        evaluated_at = release_gate_evaluated_at or created_at
        sufficiency_failures = _evidence_sufficiency_failures(
            result,
            requirements,
            evaluated_at=evaluated_at,
        )
        recomputed = not sufficiency_failures
        if release_gate["evidence_sufficiency_met"] is not recomputed:
            errors.append(
                "evidence_sufficiency_met differs from recomputed evidence gate / "
                "evidence_sufficiency_met 与重算证据门不一致: "
                + ", ".join(sufficiency_failures)
            )
        if release_gate["basis"] == "direct_release_rule":
            if direct_rule is not None:
                expected_rule = (
                    direct_rule["rule_id"],
                    direct_rule["rule_version"],
                    artifact_fingerprint(direct_rule),
                )
                if _binding_key(release_gate["direct_rule_binding"]) != expected_rule:
                    errors.append("direct release rule binding mismatch / 直接放行规则绑定不匹配")

    if errors:
        raise ArtifactValidationError(errors)


__all__ = [
    "ArtifactValidationError",
    "artifact_fingerprint",
    "build_artifact",
    "evidence_sufficiency_failures",
    "validate_artifact_hash",
    "validate_reasoning_contract",
    "validate_reasoning_event",
    "validate_reasoning_result",
    "validate_schema",
    "validate_tool_dispatch_envelope",
    "validate_tool_execution_event",
    "validate_tool_execution_result",
    "validate_workflow_route_envelope",
    "validate_workflow_route_revision",
    "workflow_signal_fingerprint",
]
