"""Guarded execution session for immutable reasoning-chain plans / 不可变推理链计划的受守卫执行会话。

The session records only externally verifiable claims, evidence, tool-call
fingerprints, checkpoint decisions, and budgets. It never stores private
chain-of-thought. / 会话只记录外部可核验命题、证据、工具调用指纹、检查点决定与预算，
绝不保存私密思维链。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, Iterable, Mapping, Sequence

try:  # Package import / 包导入
    from .reasoning_chain_compiler import (
        ChainPlanDriftError,
        ChainPlanStateError,
        ReasoningChainFactory,
        _CHECKPOINT_STATUSES,
        _PLAN_BUDGET_FIELDS,
        _binding,
        _canonical_copy,
        _schema_failures,
        _semver_is_strictly_greater,
        validate_chain_plan,
    )
    from .reasoning_runtime import (
        BudgetUsage,
        ReasoningEngine,
        StepStartRecord,
        candidate_binding_for,
        content_fingerprint,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_chain_compiler import (
        ChainPlanDriftError,
        ChainPlanStateError,
        ReasoningChainFactory,
        _CHECKPOINT_STATUSES,
        _PLAN_BUDGET_FIELDS,
        _binding,
        _canonical_copy,
        _schema_failures,
        _semver_is_strictly_greater,
        validate_chain_plan,
    )
    from reasoning_runtime import (
        BudgetUsage,
        ReasoningEngine,
        StepStartRecord,
        candidate_binding_for,
        content_fingerprint,
    )


@dataclass(frozen=True)
class ChainStepOutcome:
    """Public result of one factory-governed step close / 工厂治理下单步关闭的公开结果。"""

    step_key: str
    step_id: str
    checkpoint_status: str
    premise_accepted: bool
    next_action: str
    chain_complete: bool


class ChainPlanSession:
    """Enforce plan order and checkpoint-gated premise reuse / 强制计划顺序及检查点门控的前提复用。"""

    def __init__(
        self,
        engine: ReasoningEngine,
        plan: Mapping[str, Any],
        *,
        blueprint: Mapping[str, Any],
        contract: Mapping[str, Any],
    ) -> None:
        if not isinstance(engine, ReasoningEngine):
            raise TypeError("engine must be ReasoningEngine / engine 必须为 ReasoningEngine")
        expected_plan = ReasoningChainFactory().compile(blueprint, contract)
        supplied_plan = _canonical_copy(dict(plan))
        if supplied_plan != expected_plan:
            raise ChainPlanDriftError(
                "plan cannot be reproduced from its blueprint and contract / "
                "无法由蓝图与契约复现计划"
            )
        validate_chain_plan(plan, contract=contract, blueprint=blueprint)
        self.engine = engine
        self.plan = _canonical_copy(dict(plan))
        self.contract = _canonical_copy(dict(contract))
        self.run_id = str(self.plan["run_id"])
        snapshot = self.engine.snapshot(self.run_id)
        if (
            snapshot.task_id != self.plan["task_id"]
            or snapshot.workflow_id != self.plan["workflow_id"]
            or snapshot.scene_id != self.plan["scene_id"]
            or snapshot.contract_hash != self.plan["contract_binding"]["hash"]
            or snapshot.execution_mode != "chain"
            or snapshot.primary_topology != "chain"
        ):
            raise ChainPlanDriftError(
                "runtime identity or mode differs from the plan / 运行标识或模式与计划不一致"
            )
        self._steps_by_key = {
            step["step_key"]: step for step in self.plan["steps"]
        }
        self._steps_by_id = {step["step_id"]: step for step in self.plan["steps"]}
        self._validate_history()

    @property
    def plan_binding(self) -> dict[str, str]:
        """Return the immutable plan binding / 返回不可变计划绑定。"""

        return _binding(
            self.plan["plan_id"], self.plan["plan_version"], self.plan["plan_hash"]
        )

    @staticmethod
    def _budget_reservation_id(step: Mapping[str, Any]) -> str:
        """Return the deterministic per-step reservation identity / 返回确定性的逐步预算预留标识。"""

        return f"chain-budget-{step['step_id']}"

    @staticmethod
    def _tool_call_id(step: Mapping[str, Any]) -> str:
        """Return the sole deterministic tool-call identity for a step / 返回步骤唯一的确定性工具调用标识。"""

        return f"chain-tool-{step['step_id']}"

    @staticmethod
    def _evidence_binding(record: Mapping[str, Any]) -> dict[str, str]:
        """Bind the complete evidence record rather than only source content / 绑定完整证据记录而非仅绑定来源内容。"""

        return _binding(
            str(record["evidence_id"]),
            str(record["evidence_version"]),
            str(record["record_hash"]),
        )

    def _expected_action(
        self,
        step: Mapping[str, Any],
        evidence_bindings: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Build the exact public action envelope bound to a plan step / 构造与计划步骤精确绑定的公开动作信封。"""

        action = {
            "plan_binding": self.plan_binding,
            "logical_step_id": step["step_key"],
            "action_kind": step["action_kind"],
            "instruction": step["action_instruction"],
            "uses_tool": step["uses_tool"],
            "input_evidence_bindings": [
                _canonical_copy(dict(binding)) for binding in evidence_bindings
            ],
            "budget_reservation": {
                "reservation_id": self._budget_reservation_id(step),
                "allocation": dict(step["budget_allocation"]),
            },
            "checkpoint_binding": _binding(
                step["checkpoint"]["checkpoint_id"],
                step["checkpoint"]["checkpoint_version"],
                step["checkpoint"]["checkpoint_hash"],
            ),
            "side_effect": False,
        }
        if step["uses_tool"]:
            action["tool_binding"] = dict(step["tool_binding"])
            action["authorization_policy_binding"] = dict(
                step["authorization_policy_binding"]
            )
        return action

    def _evidence_catalog(self) -> dict[tuple[str, str], dict[str, Any]]:
        """Rebuild the immutable evidence catalog from accepted events / 从已接受事件重建不可变证据目录。"""

        catalog: dict[tuple[str, str], dict[str, Any]] = {}
        for event in self.engine.events.events(self.run_id):
            if event.event_type != "evidence_recorded":
                continue
            record = event.payload
            try:
                key = (str(record["evidence_id"]), str(record["evidence_version"]))
                declared_hash = str(record["record_hash"])
                expected_hash = content_fingerprint(
                    {
                        field: value
                        for field, value in record.items()
                        if field != "record_hash"
                    }
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ChainPlanDriftError(
                    f"evidence record is incomplete / 证据记录不完整: {exc}"
                ) from exc
            if (
                declared_hash != expected_hash
                or record.get("contract_binding") != self.plan["contract_binding"]
                or key in catalog
            ):
                raise ChainPlanDriftError(
                    f"evidence record drift / 证据记录漂移: {key[0]}@{key[1]}"
                )
            catalog[key] = _canonical_copy(record)
        return catalog

    def _validate_tool_history(
        self,
        started: Mapping[str, Any],
        closed: Mapping[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Validate plan-bound read-only action events / 校验计划绑定的只读动作事件。"""

        calls: dict[str, dict[str, Any]] = {}
        for event in self.engine.events.events(self.run_id):
            if event.event_type not in {"action_dispatched", "action_observed"}:
                continue
            envelope = event.as_dict()
            step_id = envelope.get("step_id")
            tool_call_id = envelope.get("tool_call_id")
            step = self._steps_by_id.get(step_id)
            if step is None or not step.get("uses_tool"):
                raise ChainPlanDriftError(
                    "tool action is not attached to a planned tool step / "
                    "工具动作未绑定到计划内工具步骤"
                )
            expected_call_id = self._tool_call_id(step)
            payload = event.payload
            authorization = payload.get("authorization_binding")
            if (
                tool_call_id != expected_call_id
                or payload.get("action_kind") != "tool"
                or payload.get("tool_binding") != step["tool_binding"]
                or payload.get("authorization_policy_binding")
                != step["authorization_policy_binding"]
                or not isinstance(authorization, Mapping)
                or set(authorization) != {"id", "version", "hash"}
                or re.fullmatch(
                    r"sha256:[0-9a-f]{64}", str(authorization.get("hash"))
                )
                is None
                or payload.get("authorization_verified") is not True
                or payload.get("plan_binding") != self.plan_binding
                or payload.get("side_effect") is not False
                or re.fullmatch(r"sha256:[0-9a-f]{64}", str(payload.get("input_hash")))
                is None
            ):
                raise ChainPlanDriftError(
                    f"tool action binding drift / 工具动作绑定漂移: {step_id}"
                )
            entry = calls.setdefault(step_id, {"dispatch": None, "observe": None})
            field = (
                "dispatch"
                if event.event_type == "action_dispatched"
                else "observe"
            )
            expected_phase = "started" if field == "dispatch" else "completed"
            if entry[field] is not None or payload.get("phase") != expected_phase:
                raise ChainPlanDriftError(
                    f"duplicate or invalid tool phase / 重复或无效工具阶段: {step_id}"
                )
            entry[field] = event

        for step_id, entry in calls.items():
            dispatch = entry["dispatch"]
            observe = entry["observe"]
            start = started.get(step_id)
            close = closed.get(step_id)
            if dispatch is None or start is None or dispatch.sequence <= start.sequence:
                raise ChainPlanDriftError(
                    f"tool dispatch does not follow step start / 工具分派未发生在步骤启动后: {step_id}"
                )
            if close is not None and dispatch.sequence >= close.sequence:
                raise ChainPlanDriftError(
                    f"tool dispatch follows step close / 工具分派晚于步骤关闭: {step_id}"
                )
            if observe is not None:
                dispatch_payload = dispatch.payload
                observe_payload = observe.payload
                if (
                    observe.sequence <= dispatch.sequence
                    or (close is not None and observe.sequence >= close.sequence)
                    or any(
                        observe_payload.get(field) != dispatch_payload.get(field)
                        for field in (
                            "action_kind",
                            "tool_binding",
                            "authorization_policy_binding",
                            "authorization_binding",
                            "authorization_verified",
                            "plan_binding",
                            "input_hash",
                            "side_effect",
                        )
                    )
                    or observe_payload.get("outcome")
                    not in {"succeeded", "failed", "cancelled", "timed_out"}
                    or (
                        observe_payload.get("outcome") == "succeeded"
                        and re.fullmatch(
                            r"sha256:[0-9a-f]{64}",
                            str(observe_payload.get("output_hash")),
                        )
                        is None
                    )
                ):
                    raise ChainPlanDriftError(
                        f"tool observation drift / 工具观测漂移: {step_id}"
                    )
            elif close is not None:
                raise ChainPlanDriftError(
                    f"closed tool step lacks observation / 已关闭工具步骤缺少观测: {step_id}"
                )
        return calls

    @staticmethod
    def _tool_close_failures(
        step: Mapping[str, Any],
        *,
        observation: Any,
        validation_result: str,
        actual_usage: Mapping[str, Any],
        calls: Mapping[str, Mapping[str, Any]],
    ) -> list[str]:
        """Return tool action-observation-close contract failures / 返回工具动作—观测—关闭契约失败项。"""

        entry = calls.get(str(step["step_id"]))
        if not step["uses_tool"]:
            failures = []
            if entry is not None:
                failures.append("non-tool step emitted tool actions")
            if actual_usage["tool_calls"] != 0:
                failures.append("non-tool step reported tool usage")
            return failures
        if entry is None or entry.get("dispatch") is None or entry.get("observe") is None:
            return ["tool step lacks one complete dispatch-observation pair"]
        failures = []
        if actual_usage["tool_calls"] != 1:
            failures.append("tool step must report exactly one tool call")
        observed = entry["observe"].payload
        if validation_result == "passed":
            if observed.get("outcome") != "succeeded":
                failures.append("passed tool step requires a succeeded tool outcome")
            if observed.get("output_hash") != content_fingerprint(observation):
                failures.append("step observation does not bind the tool output")
        return failures

    def _resolve_evidence_bindings(
        self,
        bindings: Sequence[Mapping[str, Any]],
        catalog: Mapping[tuple[str, str], Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        """Resolve exact record-hash bindings to evidence artifacts / 将精确记录哈希绑定解析为证据制品。"""

        records: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for binding in bindings:
            if not isinstance(binding, Mapping):
                raise ChainPlanDriftError(
                    "step evidence binding is not structured / 步骤证据绑定不是结构化记录"
                )
            try:
                identity = (
                    str(binding["id"]),
                    str(binding["version"]),
                    str(binding["hash"]),
                )
            except KeyError as exc:
                raise ChainPlanDriftError(
                    "step evidence binding is incomplete / 步骤证据绑定不完整"
                ) from exc
            if identity in seen:
                raise ChainPlanDriftError(
                    "step evidence bindings contain duplicates / 步骤证据绑定包含重复项"
                )
            seen.add(identity)
            record = catalog.get(identity[:2])
            if record is None or record.get("record_hash") != identity[2]:
                raise ChainPlanDriftError(
                    f"step evidence binding cannot be resolved / 步骤证据绑定无法解析: {identity[0]}"
                )
            records.append(_canonical_copy(record))
        return records

    def _candidate_predecessor_records(
        self,
        started: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        """Return ordered step evidence that supports a final claim / 返回支撑最终命题的有序步骤证据。"""

        final_claims = set(self.plan["final_claim_ids"])
        catalog = self._evidence_catalog()
        records: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for step in self.plan["steps"]:
            start_event = started.get(step["step_id"])
            if start_event is None:
                continue
            for record in self._resolve_evidence_bindings(
                start_event.payload["input_evidence_bindings"], catalog
            ):
                supports_final = any(
                    binding.get("relation") == "supports"
                    and binding.get("claim_id") in final_claims
                    for binding in record["claim_bindings"]
                )
                identity = (
                    record["evidence_id"],
                    record["evidence_version"],
                    record["record_hash"],
                )
                if supports_final and identity not in seen:
                    seen.add(identity)
                    records.append(record)
        return records

    def _candidate_evidence_failures(
        self,
        candidate_binding: Mapping[str, Any],
        records: Sequence[Mapping[str, Any]],
        started: Mapping[str, Any],
    ) -> list[str]:
        """Return candidate-to-step evidence lineage failures / 返回候选到步骤证据的血缘失败项。"""

        predecessors = self._candidate_predecessor_records(started)
        predecessor_by_key = {
            (
                record["evidence_id"],
                record["evidence_version"],
                record["record_hash"],
            ): record
            for record in predecessors
        }
        expected_predecessors = list(predecessor_by_key)
        observed_predecessors: list[tuple[str, str, str]] = []
        identities: set[tuple[str, str]] = set()
        failures: list[str] = []
        stable_fields = (
            "evidence_hash",
            "evidence_type",
            "claim_bindings",
            "source",
            "valid_at",
            "retrieved_at",
            "captured_at",
            "scope",
            "freshness",
            "integrity_score",
            "sensitivity",
            "redaction_state",
        )
        for record in records:
            predecessor_binding = record.get("predecessor_evidence_binding")
            if not isinstance(predecessor_binding, Mapping):
                failures.append("candidate evidence lacks predecessor binding")
                continue
            try:
                predecessor_key = (
                    str(predecessor_binding["id"]),
                    str(predecessor_binding["version"]),
                    str(predecessor_binding["hash"]),
                )
            except KeyError:
                failures.append("candidate predecessor binding is incomplete")
                continue
            observed_predecessors.append(predecessor_key)
            predecessor = predecessor_by_key.get(predecessor_key)
            if predecessor is None:
                failures.append(
                    f"candidate evidence predecessor is not a final-claim step record: {predecessor_key[0]}"
                )
                continue
            identity = (str(record["evidence_id"]), str(record["evidence_version"]))
            if identity in identities:
                failures.append(f"duplicate candidate evidence revision: {identity[0]}")
            identities.add(identity)
            if (
                record.get("evidence_id") != predecessor["evidence_id"]
                or not _semver_is_strictly_greater(
                    str(record["evidence_version"]),
                    str(predecessor["evidence_version"]),
                )
            ):
                failures.append(
                    f"candidate evidence must be a higher revision of its predecessor: {identity[0]}"
                )
            if record.get("contract_binding") != self.plan["contract_binding"]:
                failures.append(f"candidate evidence contract drift: {identity[0]}")
            if record.get("candidate_binding") != {
                "state": "observed",
                "value": dict(candidate_binding),
            }:
                failures.append(f"candidate evidence binding drift: {identity[0]}")
            if any(record.get(field) != predecessor.get(field) for field in stable_fields):
                failures.append(f"candidate evidence source content drift: {identity[0]}")
            expected_history = list(predecessor["transformation_history"]) + [
                {
                    "operation": "candidate_binding_revision",
                    "predecessor_evidence_binding": dict(predecessor_binding),
                }
            ]
            if record.get("transformation_history") != expected_history:
                failures.append(
                    f"candidate evidence transformation lineage drift: {identity[0]}"
                )

        if observed_predecessors != expected_predecessors:
            failures.append(
                "candidate evidence revisions do not exactly cover ordered final-claim step evidence"
            )
        if not predecessors:
            failures.append("final claims lack step evidence predecessors")

        requirement = self.contract["evidence_sufficiency"]
        observed_types = {str(record.get("evidence_type")) for record in records}
        missing_types = sorted(
            set(requirement["required_evidence_types"]) - observed_types
        )
        if missing_types:
            failures.append(f"candidate evidence types are incomplete: {missing_types}")
        sources = {
            (record["source"]["source_type"], record["source"]["source_ref"])
            for record in records
        }
        if len(sources) < requirement["min_independent_sources"]:
            failures.append("candidate evidence has insufficient independent sources")
        final_claims = set(self.plan["final_claim_ids"])
        supported_claims = {
            binding["claim_id"]
            for record in records
            for binding in record["claim_bindings"]
            if binding.get("relation") == "supports"
            and binding.get("claim_id") in final_claims
        }
        unresolved = len(final_claims - supported_claims)
        coverage = len(supported_claims) / len(final_claims)
        if coverage < requirement["min_claim_coverage_ratio"]:
            failures.append("candidate final-claim evidence coverage is insufficient")
        if unresolved > requirement["max_unresolved_critical_claims"]:
            failures.append("candidate has too many unresolved critical claims")
        return failures

    def _prepare_candidate_evidence(
        self,
        candidate: Any,
        supplied: Iterable[Mapping[str, Any]],
        started: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        """Validate candidate-bound revisions before mutation / 在修改运行前校验候选绑定证据修订。"""

        if isinstance(supplied, (str, bytes, Mapping)):
            raise ChainPlanStateError(
                "candidate evidence_records must be an iterable of records / "
                "候选 evidence_records 必须是记录迭代器"
            )
        records: list[dict[str, Any]] = []
        for index, item in enumerate(supplied):
            if not isinstance(item, Mapping):
                raise ChainPlanStateError(
                    f"candidate evidence record {index} must be a mapping / 候选证据记录必须是映射"
                )
            record = _canonical_copy(dict(item))
            schema_failures = _schema_failures("evidence", record)
            if schema_failures:
                raise ChainPlanStateError("; ".join(schema_failures))
            expected_hash = content_fingerprint(
                {field: value for field, value in record.items() if field != "record_hash"}
            )
            if record.get("record_hash") != expected_hash:
                raise ChainPlanStateError(
                    f"candidate evidence record hash mismatch / 候选证据记录哈希不匹配: {record.get('evidence_id')}"
                )
            records.append(record)
        failures = self._candidate_evidence_failures(
            candidate_binding_for(candidate), records, started
        )
        if failures:
            raise ChainPlanStateError(
                "candidate evidence lineage failed / 候选证据血缘失败: "
                + "; ".join(failures)
            )
        return records

    def _validate_budget_lifecycle(
        self,
        step: Mapping[str, Any],
        lifecycle_event: Any,
        *,
        actual_usage: Mapping[str, Any] | None = None,
    ) -> None:
        """Require reserve-before-start and reserved commit-before-close / 要求先预留后启动、先结算预留后关闭。"""

        reservation_id = self._budget_reservation_id(step)
        related = [
            event
            for event in self.engine.events.events(self.run_id)
            if event.payload.get("reservation_id") == reservation_id
            and event.event_type
            in {"budget_reserved", "budget_consumed", "budget_released"}
        ]
        reserved = [
            event for event in related if event.event_type == "budget_reserved"
        ]
        consumed = [
            event for event in related if event.event_type == "budget_consumed"
        ]
        released = [
            event for event in related if event.event_type == "budget_released"
        ]
        if (
            len(reserved) != 1
            or released
            or reserved[0].sequence >= lifecycle_event.sequence
            or reserved[0].payload.get("operation") != "reserve"
            or reserved[0].payload.get("delta") != step["budget_allocation"]
        ):
            raise ChainPlanDriftError(
                f"step budget was not reserved before start / 步骤预算未在启动前预留: {step['step_id']}"
            )
        if lifecycle_event.event_type == "step_closed":
            if (
                len(consumed) != 1
                or consumed[0].sequence <= reserved[0].sequence
                or consumed[0].sequence >= lifecycle_event.sequence
                or consumed[0].payload.get("operation") != "consume"
                or consumed[0].payload.get("delta") != actual_usage
                or lifecycle_event.as_dict().get("step_id") != step["step_id"]
            ):
                raise ChainPlanDriftError(
                    f"step budget reservation was not reconciled / 步骤预算预留未正确结算: {step['step_id']}"
                )

    def _step_events(self) -> tuple[dict[str, Any], dict[str, Any]]:
        evidence_catalog = self._evidence_catalog()
        started: dict[str, Any] = {}
        closed: dict[str, Any] = {}
        for event in self.engine.events.events(self.run_id):
            if event.event_type not in {"step_started", "step_closed"}:
                continue
            payload = event.payload
            step_id = event.as_dict()["step_id"]
            if step_id not in self._steps_by_id:
                raise ChainPlanDriftError(
                    f"unplanned step event / 未计划步骤事件: {step_id}"
                )
            step = self._steps_by_id[step_id]
            refs = payload.get("evidence_refs")
            bindings = payload.get("input_evidence_bindings")
            try:
                evidence_records = self._resolve_evidence_bindings(
                    bindings,
                    evidence_catalog,
                )
            except (TypeError, ChainPlanDriftError) as exc:
                raise ChainPlanDriftError(
                    f"step evidence contract drift / 步骤证据契约漂移: {step_id}: {exc}"
                ) from exc
            if (
                payload.get("step_id") != step_id
                or payload.get("contract_binding") != self.plan["contract_binding"]
                or payload.get("sequence_number") != step["sequence_number"]
                or payload.get("claim") != step["claim_to_verify"]
                or payload.get("action") != self._expected_action(step, bindings)
                or not isinstance(refs, list)
                or any(not isinstance(ref, str) or not ref for ref in refs)
                or len(refs) != len(set(refs))
                or refs != [binding["id"] for binding in bindings]
                or len(evidence_records) != len(bindings)
            ):
                raise ChainPlanDriftError(
                    f"step start contract drift / 步骤启动契约漂移: {step_id}"
                )
            target = started if event.event_type == "step_started" else closed
            if step_id in target:
                raise ChainPlanDriftError(
                    f"duplicate step lifecycle event / 重复步骤生命周期事件: {step_id}"
                )
            target[step_id] = event
            if event.event_type == "step_started":
                self._validate_budget_lifecycle(step, event)
            if event.event_type == "step_closed":
                decision = payload.get("local_decision", {})
                try:
                    validation = self._checkpoint_validation(
                        decision["checkpoint_validation"],
                        step,
                        observation=payload["observation"],
                        evidence_refs=refs,
                        evidence_bindings=bindings,
                        evidence_records=evidence_records,
                    )
                    outcome = self._outcome_for(step, validation)
                    expected_decision = {
                        "plan_binding": self.plan_binding,
                        "logical_step_id": step["step_key"],
                        "output_claim_id": step["output_claim_id"],
                        "budget_reservation_id": self._budget_reservation_id(step),
                        "checkpoint_validation": validation,
                        "premise_state": (
                            "verified" if outcome.premise_accepted else "blocked"
                        ),
                        "next_action": outcome.next_action,
                    }
                    actual_usage = self._event_usage_as_plan_budget(
                        payload["resource_use"]
                    )
                    self._validate_budget_lifecycle(
                        step,
                        event,
                        actual_usage=actual_usage,
                    )
                except (KeyError, TypeError, ValueError, ChainPlanStateError) as exc:
                    raise ChainPlanDriftError(
                        f"step close contract is invalid / 步骤关闭契约无效: {step_id}: {exc}"
                    ) from exc
                missing_types = sorted(
                    set(step["required_evidence_types"])
                    - set(validation["observed_evidence_types"])
                )
                exceeded = [
                    field
                    for field in _PLAN_BUDGET_FIELDS
                    if actual_usage[field] > step["budget_allocation"][field]
                ]
                if (
                    decision != expected_decision
                    or (validation["result"] == "passed" and missing_types)
                    or exceeded
                    or (
                        validation["result"] == "passed"
                        and step["required_evidence_types"]
                        and not refs
                    )
                ):
                    raise ChainPlanDriftError(
                        f"step close contract drift / 步骤关闭契约漂移: {step_id}"
                    )
        tool_calls = self._validate_tool_history(started, closed)
        for step_id, close_event in closed.items():
            step = self._steps_by_id[step_id]
            failures = self._tool_close_failures(
                step,
                observation=close_event.payload["observation"],
                validation_result=close_event.payload["local_decision"][
                    "checkpoint_validation"
                ]["result"],
                actual_usage=self._event_usage_as_plan_budget(
                    close_event.payload["resource_use"]
                ),
                calls=tool_calls,
            )
            if failures:
                raise ChainPlanDriftError(
                    f"tool step close contract drift / 工具步骤关闭契约漂移: {step_id}: "
                    + "; ".join(failures)
                )
        return started, closed

    def _validate_history(self) -> tuple[dict[str, Any], dict[str, Any]]:
        started, closed = self._step_events()
        blocked = False
        gap_seen = False
        open_steps = set(started) - set(closed)
        if len(open_steps) > 1:
            raise ChainPlanDriftError("strict chain has multiple open steps / 严格链存在多个打开步骤")
        for step in self.plan["steps"]:
            step_id = step["step_id"]
            has_started = step_id in started
            has_closed = step_id in closed
            if has_closed and not has_started:
                raise ChainPlanDriftError("closed step lacks start / 已关闭步骤缺少开始事件")
            if gap_seen and has_started:
                raise ChainPlanDriftError("step order is not a prefix / 步骤事件不是计划前缀")
            if not has_started:
                gap_seen = True
                continue
            if blocked:
                raise ChainPlanDriftError(
                    "downstream step reused an unverified premise / 下游步骤复用了未验证前提"
                )
            if has_closed:
                status = closed[step_id].payload["local_decision"][
                    "checkpoint_validation"
                ]["result"]
                if status not in _CHECKPOINT_STATUSES:
                    raise ChainPlanDriftError(
                        f"unknown checkpoint status / 未知检查点状态: {status}"
                    )
                blocked = status != "passed"
            else:
                gap_seen = True
        candidate_events = [
            event
            for event in self.engine.events.events(self.run_id)
            if event.event_type == "candidate_created"
        ]
        if candidate_events:
            if len(candidate_events) != 1:
                raise ChainPlanDriftError(
                    "strict chain must bind exactly one candidate / 严格链必须且只能绑定一个候选"
                )
            if len(closed) != len(self.plan["steps"]) or any(
                closed[step["step_id"]].payload["local_decision"][
                    "checkpoint_validation"
                ]["result"]
                != "passed"
                for step in self.plan["steps"]
            ):
                raise ChainPlanDriftError(
                    "candidate was created before the chain passed / 推理链通过前已创建候选"
                )
            last_close_sequence = max(event.sequence for event in closed.values())
            if any(event.sequence <= last_close_sequence for event in candidate_events):
                raise ChainPlanDriftError(
                    "candidate event precedes final step closure / 候选事件早于末步关闭"
                )
            for event in candidate_events:
                if (
                    event.payload.get("plan_binding") != self.plan_binding
                    or event.payload.get("final_claim_ids")
                    != self.plan["final_claim_ids"]
                ):
                    raise ChainPlanDriftError(
                        "candidate binding differs from the plan / 候选绑定与计划不一致"
                    )
                bindings = event.payload.get("evidence_record_bindings")
                if not isinstance(bindings, list) or not bindings:
                    raise ChainPlanDriftError(
                        "candidate lacks evidence record bindings / 候选缺少证据记录绑定"
                    )
                try:
                    records = self._resolve_evidence_bindings(
                        bindings,
                        self._evidence_catalog(),
                    )
                except (TypeError, ChainPlanDriftError) as exc:
                    raise ChainPlanDriftError(
                        "candidate evidence records cannot be resolved / "
                        f"候选证据记录无法解析: {exc}"
                    ) from exc
                failures = self._candidate_evidence_failures(
                    event.payload["candidate_binding"], records, started
                )
                expected_content_bindings = [
                    _binding(
                        record["evidence_id"],
                        record["evidence_version"],
                        record["evidence_hash"],
                    )
                    for record in records
                ]
                if (
                    failures
                    or event.payload.get("evidence_set_hash")
                    != content_fingerprint(records)
                    or event.payload.get("evidence_bindings")
                    != expected_content_bindings
                ):
                    detail = "; ".join(failures) if failures else "payload drift"
                    raise ChainPlanDriftError(
                        "candidate evidence lineage drift / "
                        f"候选证据血缘漂移: {detail}"
                    )
                evidence_events = {
                    (
                        recorded.payload.get("evidence_id"),
                        recorded.payload.get("evidence_version"),
                        recorded.payload.get("record_hash"),
                    ): recorded
                    for recorded in self.engine.events.events(self.run_id)
                    if recorded.event_type == "evidence_recorded"
                }
                if any(
                    evidence_events.get(
                        (binding["id"], binding["version"], binding["hash"])
                    )
                    is None
                    or evidence_events[
                        (binding["id"], binding["version"], binding["hash"])
                    ].sequence
                    <= event.sequence
                    for binding in bindings
                ):
                    raise ChainPlanDriftError(
                        "candidate evidence was not atomically persisted after candidate binding / "
                        "候选证据未在候选绑定后原子持久化"
                    )
        return started, closed

    def next_step(self) -> dict[str, Any] | None:
        """Return the current/open or next eligible plan step / 返回当前打开或下一可执行计划步骤。"""

        started, closed = self._validate_history()
        for step in self.plan["steps"]:
            step_id = step["step_id"]
            if step_id in closed:
                status = closed[step_id].payload["local_decision"][
                    "checkpoint_validation"
                ]["result"]
                if status != "passed":
                    return None
                continue
            return _canonical_copy(step)
        return None

    def _prepare_step_evidence(
        self,
        step: Mapping[str, Any],
        supplied: Iterable[Mapping[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        """Validate evidence records before mutating the run / 在修改运行前校验证据记录。"""

        if isinstance(supplied, (str, bytes, Mapping)):
            raise ChainPlanStateError(
                "evidence_records must be an iterable of records / evidence_records 必须是记录迭代器"
            )
        records: list[dict[str, Any]] = []
        bindings: list[dict[str, str]] = []
        identities: set[tuple[str, str]] = set()
        for index, item in enumerate(supplied):
            if not isinstance(item, Mapping):
                raise ChainPlanStateError(
                    f"evidence record {index} must be a mapping / 证据记录必须是映射"
                )
            record = _canonical_copy(dict(item))
            schema_failures = _schema_failures("evidence", record)
            if schema_failures:
                raise ChainPlanStateError("; ".join(schema_failures))
            if "record_hash" not in record:
                raise ChainPlanStateError(
                    "evidence record_hash is required / 证据必须包含 record_hash"
                )
            expected_hash = content_fingerprint(
                {
                    field: value
                    for field, value in record.items()
                    if field != "record_hash"
                }
            )
            identity = (record["evidence_id"], record["evidence_version"])
            if (
                record["record_hash"] != expected_hash
                or record["contract_binding"] != self.plan["contract_binding"]
                or identity in identities
                or record["candidate_binding"].get("state") == "observed"
            ):
                raise ChainPlanStateError(
                    f"evidence record binding drift / 证据记录绑定漂移: {identity[0]}"
                )
            identities.add(identity)
            records.append(record)
            bindings.append(self._evidence_binding(record))
        if step["criticality"] == "critical" and not records:
            raise ChainPlanStateError(
                "critical step requires structured evidence records / 关键步骤必须包含结构化证据记录"
            )
        return records, bindings

    def start_step(
        self,
        step_key: str,
        *,
        evidence_records: Iterable[Mapping[str, Any]],
    ) -> StepStartRecord:
        """Start only the next eligible compiled step / 仅启动下一可执行的已编译步骤。"""

        try:
            step = self._steps_by_key[step_key]
        except KeyError as exc:
            raise ChainPlanStateError(
                f"unknown plan step / 未知计划步骤: {step_key}"
            ) from exc
        records, bindings = self._prepare_step_evidence(step, evidence_records)
        refs = tuple(binding["id"] for binding in bindings)
        action = self._expected_action(step, bindings)
        started, _ = self._validate_history()
        existing = started.get(step["step_id"])
        if existing is not None:
            if (
                tuple(existing.payload["evidence_refs"]) != refs
                or existing.payload["input_evidence_bindings"] != bindings
                or existing.payload["action"] != action
            ):
                raise ChainPlanStateError(
                    "step start retry differs from original / 步骤开始重试与原记录不同"
                )
            return self.engine.start_step(
                self.run_id,
                step_id=step["step_id"],
                claim=step["claim_to_verify"],
                evidence_refs=refs,
                evidence_bindings=bindings,
                action=action,
            )
        eligible = self.next_step()
        if eligible is None or eligible["step_key"] != step_key:
            expected = None if eligible is None else eligible["step_key"]
            raise ChainPlanStateError(
                f"step is not next eligible; expected={expected}, received={step_key} / "
                "步骤不是下一可执行步骤"
            )
        for record in records:
            self.engine.record_evidence(self.run_id, record)
        reservation_id = self._budget_reservation_id(step)
        return self.engine.start_step_with_budget_reservation(
            self.run_id,
            step_id=step["step_id"],
            claim=step["claim_to_verify"],
            evidence_refs=refs,
            evidence_bindings=bindings,
            action=action,
            reservation_amounts=step["budget_allocation"],
            reservation_id=reservation_id,
            reservation_idempotency_key=f"budget-reserve:{reservation_id}",
        )

    def dispatch_readonly_tool(
        self,
        step_key: str,
        *,
        tool_input: Any,
        authorization_binding: Mapping[str, Any],
        idempotency_key: str | None = None,
    ) -> str:
        """Open the sole plan-bound read-only tool call for a step / 打开步骤唯一且绑定计划的只读工具调用。"""

        try:
            step = self._steps_by_key[step_key]
        except KeyError as exc:
            raise ChainPlanStateError(
                f"unknown plan step / 未知计划步骤: {step_key}"
            ) from exc
        if not step["uses_tool"]:
            raise ChainPlanStateError(
                "step does not declare a tool / 步骤未声明工具"
            )
        started, closed = self._validate_history()
        if step["step_id"] not in started or step["step_id"] in closed:
            raise ChainPlanStateError(
                "tool dispatch requires the matching open step / 工具分派要求对应步骤已打开"
            )
        tool_call_id = self._tool_call_id(step)
        self.engine.dispatch_readonly_tool(
            self.run_id,
            step_id=step["step_id"],
            tool_call_id=tool_call_id,
            tool_binding=step["tool_binding"],
            authorization_policy_binding=step[
                "authorization_policy_binding"
            ],
            authorization_binding=authorization_binding,
            tool_input=tool_input,
            plan_binding=self.plan_binding,
            idempotency_key=idempotency_key,
        )
        self._validate_history()
        return tool_call_id

    def observe_readonly_tool(
        self,
        step_key: str,
        *,
        tool_input: Any,
        authorization_binding: Mapping[str, Any],
        outcome: str,
        output: Any = None,
        idempotency_key: str | None = None,
    ) -> str | None:
        """Close the plan-bound tool call with a fingerprint-only outcome / 以仅指纹结果关闭计划绑定工具调用。"""

        try:
            step = self._steps_by_key[step_key]
        except KeyError as exc:
            raise ChainPlanStateError(
                f"unknown plan step / 未知计划步骤: {step_key}"
            ) from exc
        if not step["uses_tool"]:
            raise ChainPlanStateError(
                "step does not declare a tool / 步骤未声明工具"
            )
        started, closed = self._validate_history()
        if step["step_id"] not in started or step["step_id"] in closed:
            raise ChainPlanStateError(
                "tool observation requires the matching open step / 工具观测要求对应步骤已打开"
            )
        event = self.engine.observe_readonly_tool(
            self.run_id,
            step_id=step["step_id"],
            tool_call_id=self._tool_call_id(step),
            tool_binding=step["tool_binding"],
            authorization_policy_binding=step[
                "authorization_policy_binding"
            ],
            authorization_binding=authorization_binding,
            tool_input=tool_input,
            outcome=outcome,
            output=output,
            plan_binding=self.plan_binding,
            idempotency_key=idempotency_key,
        )
        self._validate_history()
        return event.payload.get("output_hash")

    def _checkpoint_validation(
        self,
        supplied: Mapping[str, Any],
        step: Mapping[str, Any],
        *,
        observation: Any,
        evidence_refs: Sequence[str],
        evidence_bindings: Sequence[Mapping[str, Any]],
        evidence_records: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Verify one self-hashed checkpoint-validation artifact / 验证一个自带哈希的检查点验证制品。"""

        if not isinstance(supplied, Mapping):
            raise TypeError(
                "checkpoint validation must be a mapping / 检查点验证必须是映射"
            )
        validation = _canonical_copy(dict(supplied))
        schema_failures = _schema_failures("checkpoint_validation", validation)
        if schema_failures:
            raise ChainPlanStateError("; ".join(schema_failures))

        checkpoint = step["checkpoint"]
        checkpoint_binding = _binding(
            checkpoint["checkpoint_id"],
            checkpoint["checkpoint_version"],
            checkpoint["checkpoint_hash"],
        )
        expected_bindings = {
            "plan_binding": self.plan_binding,
            "step_binding": _binding(
                step["step_id"],
                self.plan["plan_version"],
                content_fingerprint(step),
            ),
            "checkpoint_binding": checkpoint_binding,
            "validator_binding": _binding(
                checkpoint["checkpoint_id"],
                checkpoint["checkpoint_version"],
                content_fingerprint(
                    {
                        "checkpoint_binding": checkpoint_binding,
                        "validator_type": checkpoint["validator_type"],
                    }
                ),
            ),
            "criteria_binding": _binding(
                checkpoint["checkpoint_id"],
                checkpoint["checkpoint_version"],
                content_fingerprint(checkpoint["pass_criteria"]),
            ),
        }
        for field, expected in expected_bindings.items():
            if validation[field] != expected:
                raise ChainPlanStateError(
                    f"checkpoint validation binding mismatch / 检查点验证绑定不匹配: {field}"
                )
        expected_validation_id = f"checkpoint-validation:{step['step_id']}"
        if (
            validation["schema_version"] != "1.0.0"
            or validation["validation_id"] != expected_validation_id
            or validation["validation_version"] != "1.0.0"
            or validation["validator_type"] != checkpoint["validator_type"]
        ):
            raise ChainPlanStateError(
                "checkpoint validation identity or validator drift / 检查点验证标识或验证器漂移"
            )
        hash_source = dict(validation)
        declared_hash = hash_source.pop("validation_hash")
        if declared_hash != content_fingerprint(hash_source):
            raise ChainPlanStateError(
                "checkpoint validation hash mismatch / 检查点验证哈希不匹配"
            )
        if validation["observation_hash"] != content_fingerprint(observation):
            raise ChainPlanStateError(
                "checkpoint validation does not bind the observation / 检查点验证未绑定观察结果"
            )
        if validation["evidence_refs"] != list(evidence_refs):
            raise ChainPlanStateError(
                "checkpoint validation evidence differs from the step / 检查点验证证据与步骤不一致"
            )
        canonical_bindings = [
            _canonical_copy(dict(binding)) for binding in evidence_bindings
        ]
        if validation["evidence_bindings"] != canonical_bindings:
            raise ChainPlanStateError(
                "checkpoint validation evidence bindings differ from the step / "
                "检查点验证的证据绑定与步骤不一致"
            )
        observed_types = list(
            dict.fromkeys(str(record["evidence_type"]) for record in evidence_records)
        )
        if validation["observed_evidence_types"] != observed_types:
            raise ChainPlanStateError(
                "checkpoint evidence types do not match resolved records / "
                "检查点证据类型与解析记录不一致"
            )
        try:
            checked_at = datetime.fromisoformat(
                validation["checked_at"].replace("Z", "+00:00")
            )
            plan_created_at = datetime.fromisoformat(
                self.plan["created_at"].replace("Z", "+00:00")
            )
        except (AttributeError, ValueError) as exc:
            raise ChainPlanStateError(
                "checkpoint checked_at must be RFC 3339 / 检查点验证时间必须为 RFC 3339"
            ) from exc
        if checked_at.tzinfo is None or plan_created_at.tzinfo is None:
            raise ChainPlanStateError(
                "checkpoint timestamps need a timezone / 检查点时间必须包含时区"
            )
        if checked_at < plan_created_at:
            raise ChainPlanStateError(
                "checkpoint validation predates the plan / 检查点验证早于计划"
            )
        if validation["result"] == "passed":
            concrete_fields = {"id", "version", "hash"}
            if any(
                set(validation[field]) != concrete_fields
                for field in ("actor_binding", "authority_binding")
            ):
                raise ChainPlanStateError(
                    "passed checkpoint requires concrete actor and authority bindings / "
                    "通过的检查点必须包含具体执行者与授权绑定"
                )
            required_types = set(step["required_evidence_types"])
            missing_types = sorted(required_types - set(observed_types))
            requirement = self.contract["evidence_sufficiency"]
            source_keys = {
                (
                    record["source"]["source_type"],
                    record["source"]["source_ref"],
                )
                for record in evidence_records
            }
            failures: list[str] = []
            if missing_types:
                failures.append(f"missing evidence types {missing_types}")
            if len(source_keys) < requirement["min_independent_sources"]:
                failures.append("insufficient independent evidence sources")
            supports_output = any(
                claim.get("claim_id") == step["output_claim_id"]
                and claim.get("relation") == "supports"
                for record in evidence_records
                for claim in record["claim_bindings"]
            )
            coverage = 1.0 if supports_output else 0.0
            if coverage < requirement["min_claim_coverage_ratio"]:
                failures.append("output claim lacks supporting evidence coverage")
            for record in evidence_records:
                if record["freshness"]["status"] != "fresh":
                    failures.append(
                        f"evidence is not fresh: {record['evidence_id']}"
                    )
                if record["integrity_score"] < requirement["min_integrity_score"]:
                    failures.append(
                        f"evidence integrity is insufficient: {record['evidence_id']}"
                    )
                try:
                    valid_at = datetime.fromisoformat(
                        record["valid_at"].replace("Z", "+00:00")
                    )
                    retrieved_at = datetime.fromisoformat(
                        record["retrieved_at"].replace("Z", "+00:00")
                    )
                    captured_at = datetime.fromisoformat(
                        record["captured_at"].replace("Z", "+00:00")
                    )
                    assessed_at = datetime.fromisoformat(
                        record["freshness"]["assessed_at"].replace("Z", "+00:00")
                    )
                except (AttributeError, ValueError) as exc:
                    raise ChainPlanStateError(
                        "evidence timestamps must be RFC 3339 / 证据时间必须为 RFC 3339"
                    ) from exc
                timestamps = (valid_at, retrieved_at, captured_at, assessed_at)
                source_age = (checked_at - valid_at).total_seconds()
                declared_age = record["freshness"].get("age_seconds")
                if (
                    any(value.tzinfo is None for value in timestamps)
                    or not valid_at <= retrieved_at <= captured_at <= assessed_at <= checked_at
                    or source_age < 0
                    or source_age > requirement["max_source_age_seconds"]
                    or (
                        declared_age is not None
                        and (
                            declared_age > requirement["max_source_age_seconds"]
                            or abs(float(declared_age) - source_age) > 1.0
                        )
                    )
                ):
                    failures.append(
                        f"evidence time is invalid or stale: {record['evidence_id']}"
                    )
            if failures:
                raise ChainPlanStateError(
                    "passed checkpoint evidence gate failed / 通过检查点的证据门失败: "
                    + "; ".join(failures)
                )
        return validation

    @staticmethod
    def _usage_as_plan_budget(usage: BudgetUsage) -> dict[str, int | float]:
        values = usage.as_dict()
        return {
            "reasoning_tokens": values["tokens"],
            "latency_ms": values["latency_ms"],
            "model_calls": values["model_calls"],
            "tool_calls": values["tool_calls"],
            "parallel_paths": values["paths"],
            "iterations": values["iterations"],
            "retries": values["retries"],
            "total_cost_units": values["cost_units"],
        }

    @staticmethod
    def _event_usage_as_plan_budget(
        resource_use: Mapping[str, Any],
    ) -> dict[str, int | float]:
        """Decode schema-shaped event resource use / 解码 Schema 形态的事件资源用量。"""

        if not isinstance(resource_use, Mapping) or set(resource_use) != set(
            _PLAN_BUDGET_FIELDS
        ):
            raise ChainPlanStateError(
                "event resource dimensions are incomplete / 事件资源维度不完整"
            )
        values: dict[str, int | float] = {}
        for field in _PLAN_BUDGET_FIELDS:
            observed = resource_use[field]
            if not isinstance(observed, Mapping):
                raise ChainPlanStateError(
                    f"event resource {field} is invalid / 事件资源字段无效"
                )
            state = observed.get("state")
            value = observed.get("value")
            if state == "observed_zero" and value == 0:
                values[field] = 0.0 if field == "total_cost_units" else 0
            elif state == "observed" and isinstance(value, (int, float)):
                values[field] = value
            else:
                raise ChainPlanStateError(
                    f"event resource {field} is not observed / 事件资源字段未观测"
                )
        return values

    def _outcome_for(
        self, step: Mapping[str, Any], validation: Mapping[str, Any]
    ) -> ChainStepOutcome:
        status = str(validation["result"])
        passed = status == "passed"
        is_last = step["sequence_number"] == len(self.plan["steps"])
        if passed:
            next_action = "candidate_ready" if is_last else "continue"
        elif status == "insufficient_evidence":
            next_action = str(step["data_gap_policy"])
        elif status == "human_required":
            next_action = "escalate"
        else:
            next_action = str(step["checkpoint"]["on_failure"])
        return ChainStepOutcome(
            step_key=str(step["step_key"]),
            step_id=str(step["step_id"]),
            checkpoint_status=status,
            premise_accepted=passed,
            next_action=next_action,
            chain_complete=passed and is_last,
        )

    def close_step(
        self,
        step_key: str,
        *,
        observation: Any,
        checkpoint_validation: Mapping[str, Any],
        resource_use: BudgetUsage | Mapping[str, Any] | None = None,
        information_gain: float | None = None,
    ) -> ChainStepOutcome:
        """Close an open step; only a passed checkpoint unlocks its successor / 关闭打开步骤；仅检查点通过才解锁后继。"""

        try:
            step = self._steps_by_key[step_key]
        except KeyError as exc:
            raise ChainPlanStateError(
                f"unknown plan step / 未知计划步骤: {step_key}"
            ) from exc
        started, closed = self._validate_history()
        start_event = started.get(step["step_id"])
        if start_event is None:
            raise ChainPlanStateError("step must be started before close / 步骤关闭前必须先启动")
        evidence_bindings = start_event.payload["input_evidence_bindings"]
        evidence_records = self._resolve_evidence_bindings(
            evidence_bindings,
            self._evidence_catalog(),
        )
        validation = self._checkpoint_validation(
            checkpoint_validation,
            step,
            observation=observation,
            evidence_refs=start_event.payload["evidence_refs"],
            evidence_bindings=evidence_bindings,
            evidence_records=evidence_records,
        )

        usage = BudgetUsage.from_value(resource_use)
        actual = self._usage_as_plan_budget(usage)
        exceeded = [
            field
            for field in _PLAN_BUDGET_FIELDS
            if actual[field] > step["budget_allocation"][field]
        ]
        if exceeded:
            raise ChainPlanStateError(
                "step usage exceeds its allocation / 步骤用量超过分配: "
                + ", ".join(exceeded)
            )
        tool_failures = self._tool_close_failures(
            step,
            observation=observation,
            validation_result=validation["result"],
            actual_usage=actual,
            calls=self._validate_tool_history(started, closed),
        )
        if tool_failures:
            raise ChainPlanStateError(
                "tool step cannot close / 工具步骤不可关闭: "
                + "; ".join(tool_failures)
            )

        if (
            validation["result"] == "passed"
            and step["required_evidence_types"]
            and not start_event.payload["evidence_refs"]
        ):
            raise ChainPlanStateError(
                "passed checkpoint needs bound evidence refs / 通过的检查点必须绑定证据引用"
            )
        if step["step_id"] not in closed:
            eligible = self.next_step()
            if eligible is None or eligible["step_key"] != step_key:
                raise ChainPlanStateError(
                    "only the open eligible step can close / 只能关闭当前打开的可执行步骤"
                )

        control = self.plan["control"]["no_progress"]
        if control["enabled"]:
            if information_gain is None:
                raise ChainPlanStateError(
                    "contract requires measured information_gain / 契约要求实测 information_gain"
                )
            progress = information_gain >= control["min_information_gain"]
        else:
            progress = (
                validation["result"] == "passed"
                if information_gain is None
                else information_gain > 0
            )

        outcome = self._outcome_for(step, validation)
        decision = {
            "plan_binding": self.plan_binding,
            "logical_step_id": step["step_key"],
            "output_claim_id": step["output_claim_id"],
            "budget_reservation_id": self._budget_reservation_id(step),
            "checkpoint_validation": validation,
            "premise_state": "verified" if outcome.premise_accepted else "blocked",
            "next_action": outcome.next_action,
        }
        self.engine.record_step(
            self.run_id,
            step_id=step["step_id"],
            claim=step["claim_to_verify"],
            evidence_refs=start_event.payload["evidence_refs"],
            evidence_bindings=evidence_bindings,
            action=start_event.payload["action"],
            observation=observation,
            local_decision=decision,
            resource_use=usage,
            budget_reservation_id=self._budget_reservation_id(step),
            progress=progress,
            information_gain=information_gain,
        )
        self._validate_history()
        return outcome

    def set_candidate(
        self,
        candidate: Any,
        *,
        evidence_records: Iterable[Mapping[str, Any]] = (),
        idempotency_key: str | None = None,
    ) -> str:
        """Bind a candidate with derived evidence after every premise passed / 全部前提通过后以派生证据绑定候选。"""

        started, closed = self._validate_history()
        if len(closed) != len(self.plan["steps"]):
            raise ChainPlanStateError("chain is not complete / 推理链尚未完成")
        if any(
            closed[step["step_id"]].payload["local_decision"][
                "checkpoint_validation"
            ]["result"]
            != "passed"
            for step in self.plan["steps"]
        ):
            raise ChainPlanStateError(
                "candidate cannot reuse a blocked premise / 候选不得复用被阻断前提"
            )
        records = self._prepare_candidate_evidence(
            candidate,
            evidence_records,
            started,
        )
        candidate_hash = self.engine.set_candidate_with_evidence_records(
            self.run_id,
            candidate,
            evidence_records=records,
            plan_binding=self.plan_binding,
            final_claim_ids=self.plan["final_claim_ids"],
            idempotency_key=idempotency_key,
        )
        self._validate_history()
        return candidate_hash



__all__ = ["ChainPlanSession", "ChainStepOutcome"]
