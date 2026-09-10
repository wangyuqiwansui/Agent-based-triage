"""Collaboration contract guards and independent probes / 协作契约闸门与独立探针。

This local reference validates public records; it neither dispatches agents nor
performs business work. The host must verify identities and the authoritative
snapshot inventory. Hashes prove integrity, not authority or factual truth.
/ 本地参考实现只校验公开记录，不派发 Agent、不执行业务。宿主必须核验身份和
权威快照清单；哈希只能证明完整性，不能证明权限或事实为真。
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker


VERSION = "3.0.0"
SOURCE_CONTRACT_VERSION = "2.0.0"
VerifyRecord = Callable[[Mapping[str, Any]], bool]
CORE_METRICS = ("CM01", "CM08", "CM09", "CM30", "CM31", "CM34")


class CollaborationContractError(ValueError):
    """Invalid or conflicting public contract / 公开契约非法或冲突。"""


def _time(value: str) -> datetime:
    """Require an explicit clock with timezone / 要求显式带时区时钟。"""
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError("timezone missing")
        return result
    except (ValueError, TypeError, AttributeError) as error:
        raise CollaborationContractError("invalid_clock") from error


def digest(value: Any) -> str:
    """Hash canonical JSON, rejecting non-finite numbers / 哈希规范 JSON，拒绝非有限数。"""
    try:
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise CollaborationContractError("non_json_record") from error
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    path = Path(__file__).resolve().parents[1] / "schemas/collaboration-record.schema.json"
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_record(record: Mapping[str, Any]) -> None:
    """Validate shape, integrity and local semantics / 校验结构、完整性和局部语义。"""
    errors = sorted(_validator().iter_errors(record), key=lambda e: str(e.path))
    if errors:
        raise CollaborationContractError("schema: " + errors[0].message)
    if record["record_hash"] != digest({k: v for k, v in record.items() if k != "record_hash"}):
        raise CollaborationContractError("record_hash_mismatch")
    payload = record["payload"]
    if record["kind"] == "result_artifact" and payload["content_digest"] != digest(payload["content"]):
        raise CollaborationContractError("content_digest_mismatch")
    if record["kind"] == "task_card":
        criteria = [item["id"] for item in payload["criteria"]]
        if len(criteria) != len(set(criteria)) or not any(item["required"] for item in payload["criteria"]):
            raise CollaborationContractError("invalid_criteria")
        if payload["separation_required"] and payload["owner"] == payload["acceptor"]:
            raise CollaborationContractError("self_acceptance")
        if "adversarial_review" in payload["modes"]:
            roles = [payload["owner"], payload["reviewer"], payload["arbiter"]]
            if None in roles or len(set(roles)) != 3:
                raise CollaborationContractError("review_roles_not_independent")
        if "handoff_chain" in payload["modes"] and not payload["handoff_to"]:
            raise CollaborationContractError("missing_handoff_owner")


def seal_record(kind: str, record_id: str, *, run_id: str, scope: str, actor: str,
                tenant_id: str, request_id: str, plan_revision: int,
                payload: Mapping[str, Any], revision: int = 1) -> dict[str, Any]:
    """Seal a public record without granting authority / 封存公开记录，不授予权限。"""
    record = dict(protocol_version=VERSION, kind=kind, id=record_id, revision=revision,
                  source_contract_version=SOURCE_CONTRACT_VERSION,
                  tenant_id=tenant_id, request_id=request_id, plan_revision=plan_revision,
                  run_id=run_id, scope=scope, actor=actor, payload=deepcopy(dict(payload)))
    record["record_hash"] = digest(record)
    validate_record(record)
    return record


def binding(record: Mapping[str, Any]) -> dict[str, Any]:
    """Exact immutable revision binding / 精确不可变修订绑定。"""
    return {"id": record["id"], "revision": record["revision"], "hash": record["record_hash"]}


def assess_admission(*, benefit_expected: bool | None, task_decomposable: bool | None,
                     state_manageable: bool | None, result_verifiable: bool | None) -> dict[str, Any]:
    """Keep expected benefit separate from readiness / 分开判断预期收益和运行条件。"""
    signals = [benefit_expected, task_decomposable, state_manageable, result_verifiable]
    if any(value is not None and type(value) is not bool for value in signals):
        raise CollaborationContractError("admission_requires_boolean_or_unknown")
    readiness = signals[1:]
    safe = False if False in readiness else (None if None in readiness else True)
    route = ("blocked" if safe is False else "needs_evidence" if safe is None
             else "single_actor" if benefit_expected is False
             else "needs_baseline" if benefit_expected is None else "eligible")
    return {"benefit_expected": benefit_expected, "ready": safe, "route": route}


class RecordInventory:
    """Verified, scoped snapshot with an explicit expected set / 带预期集合的已核验范围快照。

    The verifier receives a defensive copy and must consult host-owned identity,
    provenance and inventory authority. Missing evidence remains missing.
    / 核验器接收防御性副本，必须查询宿主维护的身份、来源和清单权威；缺失证据保持缺失。
    """

    def __init__(self, snapshot: Mapping[str, Any], records: Sequence[Mapping[str, Any]],
                 *, verify_record: VerifyRecord, now: str):
        self.now = _time(now)
        self._snapshot = deepcopy(dict(snapshot))
        validate_record(self._snapshot)
        if self._snapshot["kind"] != "snapshot":
            raise CollaborationContractError("snapshot_required")
        if not self._verified(verify_record, self._snapshot):
            raise CollaborationContractError("untrusted_snapshot")
        if _time(self._snapshot["payload"]["observed_at"]) > self.now:
            raise CollaborationContractError("future_snapshot")
        self._records: dict[tuple[str, int], dict[str, Any]] = {}
        self.duplicates = 0
        self._errors: list[str] = []
        expected = self._snapshot["payload"]["record_bindings"]
        expected_keys = [(ref["id"], ref["revision"]) for ref in expected]
        if len(set(expected_keys)) != len(expected_keys):
            raise CollaborationContractError("conflicting_inventory")
        for original in records:
            record = deepcopy(dict(original))
            validate_record(record)
            if any(record[key] != self._snapshot[key] for key in ("tenant_id", "request_id", "run_id", "scope", "plan_revision")):
                raise CollaborationContractError("cross_scope_record")
            if binding(record) not in expected:
                raise CollaborationContractError("unlisted_or_conflicting_record")
            key = (record["id"], record["revision"])
            if key in self._records:
                if self._records[key] != record:
                    raise CollaborationContractError("conflicting_duplicate")
                self.duplicates += 1
                continue
            if not self._verified(verify_record, record):
                raise CollaborationContractError("untrusted_record: " + record["id"])
            self._records[key] = record
        for ref in expected:
            if self.resolve(ref) is None:
                self._errors.append("missing_record:" + ref["id"])
        task_keys = [(ref["id"], ref["revision"]) for ref in self._snapshot["payload"]["expected_tasks"]]
        if len(set(key[0] for key in task_keys)) != len(task_keys):
            raise CollaborationContractError("duplicate_expected_task")
        for ref in self._snapshot["payload"]["expected_tasks"]:
            if ref not in expected:
                raise CollaborationContractError("task_missing_from_inventory")
        heads = self._snapshot["payload"]["result_heads"]
        if set(heads) - {key[0] for key in task_keys}:
            raise CollaborationContractError("unknown_task_head")
        if any(ref not in expected for ref in heads.values()):
            raise CollaborationContractError("head_missing_from_inventory")
        required = self._snapshot["payload"]["business_required_bindings"]
        if any(ref not in expected for ref in required):
            raise CollaborationContractError("unlisted_business_obligation")
        if any(ref not in required for ref in [*self._snapshot["payload"]["expected_tasks"], *heads.values()]):
            raise CollaborationContractError("missing_business_obligation")
        seen_keys = {}
        for record in self.records_of("supplement_candidate"):
            key = record["payload"]["idempotency_key"]
            if key in seen_keys and seen_keys[key] != record["record_hash"]:
                raise CollaborationContractError("supplement_idempotency_conflict")
            seen_keys[key] = record["record_hash"]

    @staticmethod
    def _verified(verifier: VerifyRecord, record: Mapping[str, Any]) -> bool:
        try:
            return verifier(deepcopy(record)) is True
        except Exception:
            return False

    @property
    def snapshot(self) -> dict[str, Any]:
        """Detached authoritative manifest / 与内部状态分离的权威清单。"""
        return deepcopy(self._snapshot)

    @property
    def records(self) -> dict[tuple[str, int], dict[str, Any]]:
        """Detached verified records / 与内部状态分离的已核验记录。"""
        return deepcopy(self._records)

    @property
    def errors(self) -> list[str]:
        """Detached missing-record diagnostics / 与内部状态分离的记录缺失诊断。"""
        return list(self._errors)

    @property
    def complete(self) -> bool:
        return self._snapshot["payload"]["completeness"] == "complete" and not self._errors

    @property
    def business_gaps(self) -> list[str]:
        """Business obligations are independent of optional telemetry / 业务义务与可选观测独立。"""
        return ["missing_business_record:" + ref["id"] for ref in self._snapshot["payload"]["business_required_bindings"]
                if self.resolve(ref) is None]

    @property
    def business_complete(self) -> bool:
        return self._snapshot["payload"]["business_completeness"] == "complete" and not self.business_gaps

    def resolve(self, ref: Mapping[str, Any], kind: str | None = None) -> dict[str, Any] | None:
        """Resolve the exact identity, revision, digest and optional kind / 解析精确标识、修订、摘要及类型。"""
        record = self._records.get((ref["id"], ref["revision"]))
        if record is None or binding(record) != ref or (kind is not None and record["kind"] != kind):
            return None
        return deepcopy(record)

    def records_of(self, kind: str) -> list[dict[str, Any]]:
        """Return detached typed records / 返回隔离副本的类型化记录。"""
        return [deepcopy(record) for record in self._records.values() if record["kind"] == kind]


def _evidence_ok(inventory: RecordInventory, refs: Sequence[Mapping[str, Any]],
                 target: Mapping[str, Any]) -> bool:
    result = inventory.resolve(target, "result_artifact")
    return bool(refs) and all(
        (evidence := inventory.resolve(ref, "evidence")) is not None
        and evidence["payload"]["target"] == target
        and evidence["payload"]["record_grade"] in {"original", "derived"}
        and _time(evidence["payload"]["fact_time"]) <= _time(evidence["payload"]["read_time"]) <= inventory.now
        and (result is None or all(evidence["payload"][field] == result["payload"][field]
                                  for field in ("attempt_id", "input_snapshot"))) for ref in refs
    )


def _accepted_receipts(inventory: RecordInventory, task: Mapping[str, Any],
                       result: Mapping[str, Any], stage: str) -> list[dict[str, Any]]:
    roles = {"local": "acceptor", "global": "acceptor", "review": "reviewer", "handoff": "handoff_to"}
    required = {c["id"] for c in task["payload"]["criteria"] if c["required"]}
    active: dict[str, dict[str, Any]] = {}
    for receipt in inventory.records_of("acceptance_receipt"):
        payload = receipt["payload"]
        if payload["task"] == binding(task) and payload["target"] == binding(result) and payload["stage"] == stage:
            current = active.get(receipt["id"])
            if current is None or current["revision"] < receipt["revision"]:
                active[receipt["id"]] = receipt
    if len(active) != 1:
        return []
    receipts = []
    for receipt in active.values():
        payload = receipt["payload"]
        if payload["supplement"] is not None:
            candidate = inventory.resolve(payload["supplement"], "supplement_candidate")
            try:
                if candidate is None:
                    continue
                _validate_supplement_at(inventory, candidate, _time(payload["accepted_at"]))
            except CollaborationContractError:
                continue
        if (payload["task"] == binding(task) and payload["target"] == binding(result)
                and payload["stage"] == stage and payload["verdict"] == "accepted"
                and receipt["actor"] == task["payload"][roles[stage]]
                and payload["rule_binding"] == task["payload"]["rule_binding"]
                and payload["access_verified"] is True
                and _time(result["payload"]["submitted_at"]) <= _time(payload["accepted_at"]) <= inventory.now
                and required <= set(payload["criteria_results"])
                and all(payload["criteria_results"][key] == "passed" for key in required)
                and _evidence_ok(inventory, payload["evidence"], binding(result))
                and all(_time(inventory.resolve(ref, "evidence")["payload"]["fact_time"]) <= _time(payload["accepted_at"])
                        for ref in payload["evidence"])
                and (stage != "handoff" or payload["next_owner"] == task["payload"]["handoff_to"])):
            receipts.append(receipt)
    return receipts


def assess_delivery(inventory: RecordInventory, task_id: str) -> dict[str, Any]:
    """Gate the current artifact head without mutating execution / 对当前工件版本做闸门判断，不修改执行状态。"""
    reasons = list(inventory.business_gaps)
    if not inventory.business_complete:
        reasons.append("incomplete_inventory")
    task_ref = next((ref for ref in inventory.snapshot["payload"]["expected_tasks"] if ref["id"] == task_id), None)
    task = inventory.resolve(task_ref, "task_card") if task_ref else None
    head = inventory.snapshot["payload"]["result_heads"].get(task_id)
    result = inventory.resolve(head, "result_artifact") if head else None
    if task is None or result is None:
        return {"allowed": False, "acceptance_ready": False,
                "reasons": sorted(set(reasons + ["missing_task_or_result"])), "target": head}
    if result["payload"]["task"] != binding(task) or result["actor"] != task["payload"]["owner"]:
        reasons.append("result_task_or_owner_mismatch")
    if result["payload"]["outcome"] != "complete":
        reasons.append("business_incomplete")
    assignment = inventory.snapshot["payload"]["active_assignments"].get(task_id)
    if (not assignment or assignment["revoked"] or assignment["worker"] != result["actor"]
            or any(assignment[field] != result["payload"][field] for field in ("attempt_id", "delegation_epoch", "input_snapshot"))):
        reasons.append("stale_or_revoked_attempt")
    if _time(result["payload"]["submitted_at"]) > inventory.now:
        reasons.append("future_result")
    for ref in task["payload"]["input_bindings"]:
        if inventory.resolve(ref) is None:
            reasons.append("unresolved_input")
    for ref in result["payload"]["evidence"]:
        if inventory.resolve(ref, "evidence") is None:
            reasons.append("unresolved_result_evidence")
    for stage in ("local", "global"):
        if not _accepted_receipts(inventory, task, result, stage):
            reasons.append("missing_" + stage + "_acceptance")
    global_receipts = _accepted_receipts(inventory, task, result, "global")
    for stage in ["local"] + (["review"] if "adversarial_review" in task["payload"]["modes"] else []):
        earlier = _accepted_receipts(inventory, task, result, stage)
        if earlier and global_receipts and _time(earlier[0]["payload"]["accepted_at"]) > _time(global_receipts[0]["payload"]["accepted_at"]):
            reasons.append("global_acceptance_precedes_" + stage)
    if "adversarial_review" in task["payload"]["modes"]:
        if not _accepted_receipts(inventory, task, result, "review"):
            reasons.append("missing_current_version_review")
    for objection in inventory.records_of("objection"):
        payload = objection["payload"]
        if payload["task"] != binding(task) or payload["target"] != head or payload["severity"] != "blocking":
            continue
        decisions = [d for d in inventory.records_of("adjudication")
                     if d["payload"]["objection"] == binding(objection) and d["payload"]["target"] == head]
        # Conflicting decisions fail closed; arrival order cannot pick a winner.
        # / 冲突裁决默认阻断，不能按到达顺序选胜者。
        if (len(decisions) != 1 or decisions[0]["payload"]["decision"] != "dismiss"
                or decisions[0]["actor"] != task["payload"]["arbiter"]
                or not (_time(payload["raised_at"]) <= _time(decisions[0]["payload"]["decided_at"]) <= inventory.now)
                or (global_receipts and _time(decisions[0]["payload"]["decided_at"]) > _time(global_receipts[0]["payload"]["accepted_at"]))
                or not _evidence_ok(inventory, decisions[0]["payload"]["evidence"], head)):
            reasons.append("unresolved_blocking_objection:" + objection["id"])
    if task["payload"]["handoff_to"] and not _accepted_receipts(inventory, task, result, "handoff"):
        reasons.append("missing_responsibility_transfer")
    if task["payload"]["handoff_to"]:
        handoffs = _accepted_receipts(inventory, task, result, "handoff")
        transfers = [record for record in inventory.records_of("responsibility_transfer")
                     if record["payload"]["task"] == binding(task) and record["payload"]["target"] == head]
        valid = False
        if len(transfers) == 1 and handoffs:
            transfer = transfers[0]["payload"]
            valid = (transfer["handoff_acceptance"] == binding(handoffs[0])
                     and transfer["from_owner"] == task["payload"]["owner"]
                     and transfer["to_owner"] == task["payload"]["handoff_to"]
                     and transfer["responsibility_scope"] == task["payload"]["delivery_scope"]
                     and transfer["previous_epoch"] == result["payload"]["delegation_epoch"]
                     and transfer["next_epoch"] == transfer["previous_epoch"] + 1
                     and transfer["committed_ledger_revision"] == transfer["expected_ledger_revision"] + 1
                     and _time(handoffs[0]["payload"]["accepted_at"]) <= _time(transfer["committed_at"]) <= inventory.now)
        if not valid:
            reasons.append("missing_atomic_transfer_receipt")
    acceptance_ready = not reasons
    global_receipts = _accepted_receipts(inventory, task, result, "global")
    delivered = any(record["payload"]["task"] == binding(task) and record["payload"]["target"] == head
                    and record["payload"]["global_acceptance"] in [binding(item) for item in global_receipts]
                    and record["payload"]["delivery_scope"] == task["payload"]["delivery_scope"]
                    and record["payload"]["delivered_to"] == task["payload"]["final_receiver"]
                    and record["payload"]["outcome"] == "confirmed"
                    and _time(record["payload"]["delivered_at"]) <= inventory.now
                    and any(record["payload"]["global_acceptance"] == binding(item)
                            and _time(item["payload"]["accepted_at"]) <= _time(record["payload"]["delivered_at"])
                            for item in global_receipts)
                    and all(_time(item["payload"]["committed_at"]) <= _time(record["payload"]["delivered_at"])
                            for item in inventory.records_of("responsibility_transfer")
                            if item["payload"]["task"] == binding(task) and item["payload"]["target"] == head)
                    for record in inventory.records_of("delivery_receipt"))
    if not delivered:
        reasons.append("missing_actual_delivery")
    return {"allowed": not reasons, "acceptance_ready": acceptance_ready,
            "reasons": sorted(set(reasons)), "target": deepcopy(head)}


def validate_supplement(inventory: RecordInventory, candidate: Mapping[str, Any]) -> None:
    """Verify an evidence-only candidate; do not accept business work / 核验纯补证候选，不执行业务验收。"""
    _validate_supplement_at(inventory, candidate, inventory.now)


def _validate_supplement_at(inventory: RecordInventory, candidate: Mapping[str, Any], at: datetime) -> None:
    """Audit validity at intake or recorded adoption time / 按接入或已记录的采纳时刻审计有效性。"""
    validate_record(candidate)
    if inventory.resolve(binding(candidate), "supplement_candidate") is None:
        raise CollaborationContractError("unverified_supplement")
    payload = candidate["payload"]
    gap = inventory.resolve(payload["gap"], "gap")
    if gap is None or gap["payload"]["gap_type"] in {"business_incomplete", "unclassified"}:
        raise CollaborationContractError("business_work_requires_execution")
    if payload["target"] != gap["payload"]["target"]:
        raise CollaborationContractError("supplement_target_mismatch")
    target = inventory.resolve(payload["target"], "result_artifact")
    if target is None or inventory.snapshot["payload"]["result_heads"].get(target["payload"]["task"]["id"]) != payload["target"]:
        raise CollaborationContractError("stale_supplement_target")
    assignment = inventory.snapshot["payload"]["active_assignments"].get(target["payload"]["task"]["id"])
    if (not assignment or assignment["revoked"] or assignment["worker"] != target["actor"]
            or any(assignment[field] != target["payload"][field] for field in ("attempt_id", "delegation_epoch", "input_snapshot"))):
        raise CollaborationContractError("stale_or_revoked_supplement_attempt")
    detail = gap["payload"]
    if not (_time(payload["generated_at"]) <= at <= inventory.now
            and at < _time(payload["expires_at"]) <= _time(detail["deadline_at"])):
        raise CollaborationContractError("expired_or_invalid_supplement_window")
    if payload["candidate_path"] not in detail["allowed_paths"]:
        raise CollaborationContractError("unauthorized_candidate_path")
    if payload["observation_run_id"] == candidate["run_id"]:
        raise CollaborationContractError("probe_run_must_be_independent")
    if payload["acquisition"] != "offline" and not detail["active_read_authorized"]:
        raise CollaborationContractError("active_read_not_authorized")
    if payload["acquisition"] == "offline" and payload["reads_used"] != 0:
        raise CollaborationContractError("offline_candidate_cannot_claim_active_reads")
    previous = inventory.snapshot["payload"]["gap_usage"].get(gap["id"])
    if previous is None:
        raise CollaborationContractError("missing_gap_budget_ledger")
    if (previous["reads_used"] + payload["reads_used"] > detail["max_reads"]
            or previous["rounds_used"] + payload["rounds_used"] > detail["max_rounds"]):
        raise CollaborationContractError("supplement_budget_exhausted")
    if any(detail[field] != target["payload"][field] for field in ("attempt_id", "input_snapshot")):
        raise CollaborationContractError("gap_attempt_or_input_mismatch")
    allowed = gap["payload"]["allowed_sources"]
    claims = set(gap["payload"]["required_claims"])
    supplied = set()
    for ref in payload["evidence"]:
        evidence = inventory.resolve(ref, "evidence")
        if (evidence is None or evidence["payload"]["target"] != payload["target"]
                or evidence["payload"]["source_id"] not in allowed):
            raise CollaborationContractError("unauthorized_or_mismatched_evidence")
        detail = evidence["payload"]
        if (any(detail[field] != target["payload"][field] for field in ("attempt_id", "input_snapshot"))
                or detail["record_grade"] not in {"original", "derived"}
                or not (_time(detail["fact_time"]) <= _time(detail["read_time"]) <= _time(payload["generated_at"]))):
            raise CollaborationContractError("evidence_attempt_time_or_grade_mismatch")
        if payload["acquisition"] == "current_state" and detail["evidence_type"] != "current_state":
            raise CollaborationContractError("cannot_reconstruct_historical_decision")
        # A claim id carries its declared evidence type, so a current reading cannot
        # stand in for a historical test or decision. / 声明绑定证据类型，当前读数不能冒充历史测试或决策。
        supplied.add(detail["claim_id"] + ":" + detail["evidence_type"])
    if not claims <= supplied:
        raise CollaborationContractError("missing_requested_evidence")


def validate_supplement_receipt(inventory: RecordInventory, receipt: Mapping[str, Any]) -> None:
    """Require a separate exact-version business recheck before adoption / 采纳前要求独立的精确版本业务复验。"""
    validate_record(receipt)
    if inventory.resolve(binding(receipt), "supplement_receipt") is None:
        raise CollaborationContractError("unverified_supplement_receipt")
    payload = receipt["payload"]
    candidate = inventory.resolve(payload["candidate"], "supplement_candidate")
    if candidate is None or candidate["payload"]["target"] != payload["target"]:
        raise CollaborationContractError("receipt_candidate_mismatch")
    result = inventory.resolve(payload["target"], "result_artifact")
    task = inventory.resolve(result["payload"]["task"], "task_card") if result else None
    gap = inventory.resolve(candidate["payload"]["gap"], "gap")
    receiver = gap["payload"]["receiver"] if gap else None
    if task is None or receiver is None or receipt["actor"] != receiver:
        raise CollaborationContractError("unauthorized_supplement_receipt")
    if not (_time(candidate["payload"]["generated_at"]) <= _time(payload["disposed_at"]) <= inventory.now):
        raise CollaborationContractError("invalid_disposition_time")
    if payload["decision"] != "adopted":
        return
    _validate_supplement_at(inventory, candidate, _time(payload["disposed_at"]))
    if gap["payload"]["gap_type"] == "authorization":
        raise CollaborationContractError("authorization_requires_authority_workflow")
    if gap["payload"]["gap_type"] == "observation_record":
        repair = inventory.resolve(payload["recheck"], "observation_repair_receipt") if payload["recheck"] else None
        if (repair is None or repair["actor"] != receiver or repair["payload"]["candidate"] != binding(candidate)
                or repair["payload"]["target"] != payload["target"]
                or not (_time(candidate["payload"]["generated_at"]) <= _time(repair["payload"]["repaired_at"]) <= _time(payload["disposed_at"]))):
            raise CollaborationContractError("missing_observation_repair_receipt")
        return
    if receiver != task["payload"]["acceptor"]:
        raise CollaborationContractError("business_gap_receiver_must_be_acceptor")
    acceptance = inventory.resolve(payload["recheck"], "acceptance_receipt") if payload["recheck"] else None
    if acceptance is None or acceptance not in _accepted_receipts(inventory, task, result, "global"):
        raise CollaborationContractError("missing_business_recheck")
    if acceptance["payload"]["supplement"] != binding(candidate):
        raise CollaborationContractError("recheck_did_not_consume_candidate")
    if not (_time(candidate["payload"]["generated_at"]) <= _time(acceptance["payload"]["accepted_at"]) <= _time(payload["disposed_at"])):
        raise CollaborationContractError("recheck_outside_disposition_window")
    if not set(digest(ref) for ref in candidate["payload"]["evidence"]) <= set(digest(ref) for ref in acceptance["payload"]["evidence"]):
        raise CollaborationContractError("recheck_missing_candidate_evidence")


def inspect_workflow(snapshot: Mapping[str, Any], records: Sequence[Mapping[str, Any]],
                     *, verify_record: VerifyRecord,
                     now: str,
                     enabled_metrics: Sequence[str] = CORE_METRICS) -> dict[str, Any]:
    """Run independently on an adapted snapshot; unknown is never zero / 对适配快照独立运行，未知绝不记零。"""
    if len(set(enabled_metrics)) != len(enabled_metrics) or any(
            key not in {f"CM{i:02d}" for i in range(1, 35)} for key in enabled_metrics):
        raise CollaborationContractError("unknown_or_duplicate_metric")
    inventory = RecordInventory(snapshot, records, verify_record=verify_record, now=now)
    expected_tasks = inventory.snapshot["payload"]["expected_tasks"]
    findings = {ref["id"]: assess_delivery(inventory, ref["id"]) for ref in expected_tasks}
    metrics = {key: {"value": None, "status": "unknown", "reason": "adapter_measurement_required",
                     "numerator": None, "denominator": None} for key in enabled_metrics}

    def ratio(key: str, numerator: int, denominator: int, complete: bool = True) -> None:
        if key in metrics:
            known = complete and denominator > 0
            metrics[key] = {"value": numerator / denominator if known else None,
                            "status": "known" if known else "not_computable" if not complete else "not_applicable",
                            "reason": None if known else "incomplete_inventory" if not complete else "empty_population",
                            "numerator": numerator, "denominator": denominator}

    task_count = sum(inventory.resolve(ref, "task_card") is not None for ref in expected_tasks)
    local_count = 0
    for ref in expected_tasks:
        task = inventory.resolve(ref, "task_card")
        head = inventory.snapshot["payload"]["result_heads"].get(ref["id"])
        result = inventory.resolve(head, "result_artifact") if head else None
        if task and result and result["payload"]["task"] == ref and _accepted_receipts(inventory, task, result, "local"):
            local_count += 1
    # Coverage can be measured against the trusted manifest even if records are missing.
    # / 即使记录缺失，覆盖率仍可对可信预期清单计量。
    ratio("CM01", task_count, len(expected_tasks))
    ratio("CM08", local_count, len(expected_tasks), inventory.complete)
    ratio("CM09", sum(item["allowed"] for item in findings.values()), len(expected_tasks), inventory.complete)
    ratio("CM30", len(inventory.records), len(inventory.snapshot["payload"]["record_bindings"]))
    ratio("CM31", inventory.duplicates, len(records))
    peers = [metric for key, metric in metrics.items() if key != "CM34"]
    ratio("CM34", sum(metric["status"] in {"unknown", "not_computable"} for metric in peers), len(peers))
    return {"protocol_version": VERSION, "snapshot": binding(inventory.snapshot),
            "delivery_ready": inventory.business_complete and bool(findings) and all(item["allowed"] for item in findings.values()),
            "complete": inventory.complete, "findings": findings,
            "inventory_gaps": list(inventory.errors), "metrics": metrics}
