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
}

_HASH_FIELDS = {
    "normalized_input": "normalized_input_hash",
    "reasoning_contract": "contract_hash",
    "reasoning_result": "result_hash",
}

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
    else:
        validate_schema(kind, result)
        validate_artifact_hash(kind, result)
    return result


def _binding_key(binding: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return binding.get("id"), binding.get("version"), binding.get("hash")


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
]
