"""Behavioral checks for collaboration boundaries / 协作边界行为测试。

Synthetic fixtures authenticate only the hashes frozen by the test host; these
tests do not run real agents, tools, approvals or baseline experiments.
/ 合成夹具仅认证测试宿主冻结的哈希，不运行真实 Agent、工具、审批或基线实验。
"""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/harness-engineering-patterns"
NOW = "2026-09-09T03:05:00Z"
INPUT_BINDING = {"id": "input-1", "revision": 1, "hash": "sha256:" + "2" * 64}
RULE_BINDING = {"id": "rules-1", "revision": 1, "hash": "sha256:" + "3" * 64}
sys.path.insert(0, str(SKILL / "runtime"))

from collaboration_protocol import (  # noqa: E402
    CollaborationContractError, RecordInventory, assess_admission, assess_delivery,
    binding, digest, inspect_workflow, seal_record, validate_record,
    validate_supplement, validate_supplement_receipt,
)


def make(kind, identifier, payload, actor="worker", revision=1, **context):
    payload = deepcopy(payload)
    if kind in {"objection", "adjudication"}:
        payload.setdefault("raised_at" if kind == "objection" else "decided_at", "2026-09-09T03:01:00Z")
    return seal_record(kind, identifier, run_id=context.get("run_id", "run-1"),
                       scope=context.get("scope", "project/test"), actor=actor,
                       tenant_id=context.get("tenant_id", "tenant-1"), request_id="request-1", plan_revision=1,
                       revision=revision, payload=payload)


def reseal(record):
    copy = deepcopy(record)
    copy["record_hash"] = digest({key: value for key, value in copy.items() if key != "record_hash"})
    return copy


def task(*, modes=None, handoff=None):
    return make("task_card", "delivery", {
        "goal": "Deliver a verified answer / 交付已核验答案",
        "criteria": [{"id": "accuracy", "required": True, "description": "Check evidence / 核验证据"}],
        "owner": "worker", "acceptor": "lead", "reviewer": "critic", "arbiter": "arbiter",
        "separation_required": True, "coverage_units": ["answer"], "goal_binding": INPUT_BINDING,
        "rule_binding": RULE_BINDING, "deadline_at": "2026-09-09T03:30:00Z",
        "delivery_scope": "internal-draft", "final_receiver": "lead",
        "handoff_to": handoff, "modes": modes or ["hierarchical_delegation"], "input_bindings": [],
        "allowed_scope": ["report"], "forbidden_scope": ["publish"],
        "isolation": {"namespace": "delivery-1", "write_resources": ["report"], "merge_owner": "lead"},
        "budget": {"max_attempts": 2, "timeout_seconds": 60},
        "tool_policy": {"id": "readonly", "revision": 1, "hash": "sha256:" + "1" * 64},
    }, actor="lead")


def evidence(result, identifier="test-log", evidence_type="execution_record", source="ci", claim="accuracy"):
    return make("evidence", identifier, {
        "target": binding(result), "source_id": source, "claim_id": claim,
        "evidence_type": evidence_type, "source_ref": "fixture://" + identifier,
        "observed_at": "2026-09-09T03:00:00Z",
        "attempt_id": result["payload"]["attempt_id"], "input_snapshot": result["payload"]["input_snapshot"],
        "fact_time": "2026-09-09T03:00:00Z", "read_time": "2026-09-09T03:00:00Z", "record_grade": "original",
    }, actor="source-adapter")


def receipt(task_record, result, proof, stage, *, actor=None, verdict="accepted", revision=1, supplement=None):
    role = {"arrival": "receiver", "local": "lead", "global": "lead", "handoff": "receiver", "review": "critic"}
    return make("acceptance_receipt", "receipt-" + stage, {
        "task": binding(task_record), "target": binding(result), "stage": stage, "verdict": verdict,
        "criteria_results": {"accuracy": "passed"}, "evidence": [binding(proof)],
        "next_owner": "receiver" if stage == "handoff" else None,
        "supplement": binding(supplement) if supplement else None,
        "rule_binding": task_record["payload"]["rule_binding"], "accepted_at": "2026-09-09T03:01:00Z",
        "access_verified": True,
    }, actor=actor or role[stage], revision=revision)


def fixture(*, review=False, handoff=False, outcome="complete"):
    modes = ["fan_out_gather"]
    if review:
        modes.append("adversarial_review")
    if handoff:
        modes.append("handoff_chain")
    card = task(modes=modes, handoff="receiver" if handoff else None)
    content = {"answer": 42}
    result = make("result_artifact", "answer", {"task": binding(card), "outcome": outcome,
                  "content": content, "content_digest": digest(content), "evidence": [],
                  "attempt_id": "attempt-1", "delegation_epoch": 1, "input_snapshot": INPUT_BINDING,
                  "submitted_at": "2026-09-09T03:00:00Z"})
    proof = evidence(result)
    records = [card, result, proof]
    for stage in ["local", "global"] + (["review"] if review else []) + (["handoff"] if handoff else []):
        records.append(receipt(card, result, proof, stage))
    global_receipt = next(item for item in records if item["id"] == "receipt-global")
    records.insert(3, make("delivery_receipt", "delivered", {"task": binding(card), "target": binding(result),
        "global_acceptance": binding(global_receipt), "delivery_scope": "internal-draft", "delivered_to": "lead",
        "delivered_at": "2026-09-09T03:04:00Z", "outcome": "confirmed"}, actor="host-delivery"))
    if handoff:
        transfer_receipt = next(item for item in records if item["id"] == "receipt-handoff")
        records.insert(3, make("responsibility_transfer", "transfer", {"task": binding(card), "target": binding(result),
            "handoff_acceptance": binding(transfer_receipt), "from_owner": "worker", "to_owner": "receiver",
            "responsibility_scope": "internal-draft", "previous_epoch": 1, "next_epoch": 2,
            "expected_ledger_revision": 0, "committed_ledger_revision": 1,
            "commit_ref": "fixture://atomic-commit", "committed_at": "2026-09-09T03:03:00Z"}, actor="host-ledger"))
    return card, result, proof, records


def manifest(records, *, expected=None, heads=None, completeness="complete"):
    tasks = [record for record in records if record["kind"] == "task_card"]
    results = [record for record in records if record["kind"] == "result_artifact"]
    return make("snapshot", "snapshot", {
        "source_id": "host-inventory", "completeness": completeness,
        "expected_tasks": expected if expected is not None else [binding(item) for item in tasks],
        "result_heads": heads if heads is not None else {item["payload"]["task"]["id"]: binding(item) for item in results},
        "record_bindings": list({digest(binding(item)): binding(item) for item in records}.values()),
        "business_required_bindings": list({digest(binding(item)): binding(item) for item in records
            if item["kind"] not in {"gap", "supplement_candidate", "supplement_receipt", "observation_repair_receipt"}}.values()),
        "business_completeness": completeness, "observed_at": NOW,
        "active_assignments": {item["payload"]["task"]["id"]: {"worker": item["actor"],
            "attempt_id": item["payload"]["attempt_id"], "delegation_epoch": item["payload"]["delegation_epoch"],
            "input_snapshot": item["payload"]["input_snapshot"], "revoked": False} for item in results},
        "gap_usage": {item["id"]: {"reads_used": 0, "rounds_used": 0} for item in records if item["kind"] == "gap"},
    }, actor="host-inventory")


def verifier_for(snapshot, records):
    hashes = {record["record_hash"] for record in [snapshot, *records]}
    return lambda record: record["record_hash"] in hashes


def inventory(records, snapshot=None):
    snapshot = snapshot or manifest(records)
    return RecordInventory(snapshot, records, verify_record=verifier_for(snapshot, records), now=NOW)


def test_benefit_is_separate_from_safe_operation():
    assert assess_admission(benefit_expected=False, task_decomposable=True,
                            state_manageable=True, result_verifiable=True) == {
        "benefit_expected": False, "ready": True, "route": "single_actor"}
    result = assess_admission(benefit_expected=True, task_decomposable=False,
                              state_manageable=True, result_verifiable=True)
    assert result["route"] == "blocked"


@pytest.mark.parametrize("benefit,ready,route", [(None, True, "needs_baseline"),
                         (True, None, "needs_evidence"), (True, True, "eligible")])
def test_admission_preserves_unknowns(benefit, ready, route):
    assert assess_admission(benefit_expected=benefit, task_decomposable=ready,
                            state_manageable=True, result_verifiable=True)["route"] == route


def test_strings_do_not_become_admission_permission():
    with pytest.raises(CollaborationContractError):
        assess_admission(benefit_expected="true", task_decomposable=True,
                         state_manageable=True, result_verifiable=True)


@pytest.mark.parametrize("review,handoff", [(False, False), (True, False), (False, True), (True, True)])
def test_composable_modes_can_deliver_without_forced_review(review, handoff):
    card, _, _, records = fixture(review=review, handoff=handoff)
    assert assess_delivery(inventory(records), card["id"])["allowed"]


@pytest.mark.parametrize("outcome", ["partial", "failed", "unknown"])
def test_business_incomplete_never_releases(outcome):
    card, _, _, records = fixture(outcome=outcome)
    assert "business_incomplete" in assess_delivery(inventory(records), card["id"])["reasons"]


@pytest.mark.parametrize("field,value", [("protocol_version", "1.0.0"), ("revision", 0),
                                      ("revision", True), ("actor", " ")])
def test_malformed_contract_rejected(field, value):
    record = task()
    record[field] = value
    with pytest.raises(CollaborationContractError):
        validate_record(reseal(record))


def test_tampered_content_fails_even_after_rehashing_envelope():
    _, result, _, _ = fixture()
    result["payload"]["content"]["answer"] = 43
    with pytest.raises(CollaborationContractError, match="content_digest"):
        validate_record(reseal(result))


def test_record_hash_and_nonfinite_numbers_are_rejected():
    card = task()
    card["payload"]["goal"] = "tampered"
    with pytest.raises(CollaborationContractError, match="record_hash"):
        validate_record(card)
    with pytest.raises(CollaborationContractError, match="non_json"):
        digest({"score": float("nan")})


@pytest.mark.parametrize("mutation", ["self_acceptance", "reviewer", "criteria", "handoff"])
def test_task_role_and_criterion_invariants(mutation):
    card = task(modes=["adversarial_review", "handoff_chain"], handoff="receiver")
    if mutation == "self_acceptance":
        card["payload"]["acceptor"] = "worker"
    elif mutation == "reviewer":
        card["payload"]["reviewer"] = "worker"
    elif mutation == "criteria":
        card["payload"]["criteria"][0]["required"] = False
    else:
        card["payload"]["handoff_to"] = None
    with pytest.raises(CollaborationContractError):
        validate_record(reseal(card))


def test_local_acceptance_and_arrival_cannot_replace_global_acceptance():
    card, result, proof, records = fixture()
    records = [item for item in records if item["id"] != "receipt-global"]
    records.append(receipt(card, result, proof, "arrival", verdict="received"))
    assert "missing_global_acceptance" in assess_delivery(inventory(records), card["id"])["reasons"]


@pytest.mark.parametrize("field,value", [("actor", "intruder"), ("criterion", "unknown"), ("evidence", [])])
def test_receipt_authority_criteria_and_evidence_are_required(field, value):
    card, _, _, records = fixture()
    target = records[-1]
    if field == "actor":
        target[field] = value
    elif field == "criterion":
        target["payload"]["criteria_results"]["accuracy"] = value
    else:
        target["payload"]["evidence"] = value
    records[-1] = reseal(target)
    assert not assess_delivery(inventory(records), card["id"])["allowed"]


def test_newer_rejection_overrides_old_pass_independently_of_arrival_order():
    card, result, proof, records = fixture()
    rejected = receipt(card, result, proof, "global", verdict="rejected", revision=2)
    for batch in [records + [rejected], [rejected] + records]:
        assert not assess_delivery(inventory(batch), card["id"])["allowed"]


def test_conflicting_active_receipts_do_not_pick_a_winner():
    card, _, _, records = fixture()
    extra = deepcopy(records[-1])
    extra["id"] = "another-global-receipt"
    records.append(reseal(extra))
    assert not assess_delivery(inventory(records), card["id"])["allowed"]


def test_old_receipts_do_not_accept_new_result_revision():
    card, result, _, records = fixture()
    new_result = deepcopy(result)
    new_result["revision"] = 2
    records.append(reseal(new_result))
    assert not assess_delivery(inventory(records), card["id"])["allowed"]


def test_expected_missing_record_is_not_silently_dropped():
    card, _, _, records = fixture()
    snapshot = manifest(records)
    missing = [record for record in records if record["id"] != "receipt-global"]
    result = assess_delivery(inventory(missing, snapshot), card["id"])
    assert "incomplete_inventory" in result["reasons"]


def test_missing_current_review_and_receiver_transfer_block():
    card, _, _, records = fixture(review=True, handoff=True)
    records = [item for item in records if item["id"] not in {"receipt-review", "receipt-handoff"}]
    result = assess_delivery(inventory(records), card["id"])
    assert {"missing_current_version_review", "missing_responsibility_transfer"} <= set(result["reasons"])


def objection_fixture():
    card, result, proof, records = fixture(review=True)
    objection = make("objection", "issue", {"task": binding(card), "target": binding(result),
        "severity": "blocking", "finding": "Counterexample / 反例", "evidence": [binding(proof)]}, actor="critic")
    records.append(objection)
    return card, result, proof, objection, records


@pytest.mark.parametrize("decision,actor,allowed", [(None, "arbiter", False),
                         ("uphold", "arbiter", False), ("dismiss", "worker", False), ("dismiss", "arbiter", True)])
def test_blocking_dissent_changes_release(decision, actor, allowed):
    card, result, proof, objection, records = objection_fixture()
    if decision:
        records.append(make("adjudication", "decision", {"objection": binding(objection),
            "target": binding(result), "decision": decision, "rationale": "Verified counterexample / 核验反例",
            "evidence": [binding(proof)]}, actor=actor))
    assert assess_delivery(inventory(records), card["id"])["allowed"] is allowed


def test_conflicting_adjudications_block_even_if_one_dismisses():
    card, result, proof, objection, records = objection_fixture()
    for decision in ("dismiss", "uphold"):
        records.append(make("adjudication", decision, {"objection": binding(objection),
            "target": binding(result), "decision": decision, "rationale": "Source checked / 来源已核验",
            "evidence": [binding(proof)]}, actor="arbiter"))
    assert not assess_delivery(inventory(records), card["id"])["allowed"]


def test_post_acceptance_dismissal_requires_new_business_acceptance():
    card, result, proof, objection, records = objection_fixture()
    decision = make("adjudication", "decision", {"objection": binding(objection), "target": binding(result),
        "decision": "dismiss", "rationale": "Later decision / 后续裁决", "evidence": [binding(proof)],
        "decided_at": "2026-09-09T03:04:30Z"}, actor="arbiter")
    assert not assess_delivery(inventory(records + [decision]), card["id"])["allowed"]


@pytest.mark.parametrize("stage", ["local", "review"])
def test_global_acceptance_must_follow_its_prerequisite_receipts(stage):
    card, _, _, records = fixture(review=True)
    earlier = next(item for item in records if item["id"] == "receipt-" + stage)
    earlier["payload"]["accepted_at"] = "2026-09-09T03:02:00Z"
    records = [reseal(item) if item["id"] == earlier["id"] else item for item in records]
    assert "global_acceptance_precedes_" + stage in assess_delivery(inventory(records), card["id"])["reasons"]


@pytest.mark.parametrize("failure", ["snapshot", "record", "exception", "truthy"])
def test_host_authority_is_required_and_fails_closed(failure):
    _, _, _, records = fixture()
    snapshot = manifest(records)
    def verifier(record):
        if failure == "exception":
            raise RuntimeError("identity service unavailable")
        if failure == "truthy":
            return "true"
        return record["kind"] != ("snapshot" if failure == "snapshot" else "evidence")
    with pytest.raises(CollaborationContractError, match="untrusted"):
        RecordInventory(snapshot, records, verify_record=verifier, now=NOW)


def test_scope_and_unlisted_record_rejected():
    _, _, _, records = fixture()
    snapshot = manifest(records)
    extra = deepcopy(records[2])
    extra["scope"] = "another-project"
    with pytest.raises(CollaborationContractError, match="cross_scope"):
        inventory(records + [reseal(extra)], snapshot)
    extra = deepcopy(records[2])
    extra["id"] = "unlisted"
    with pytest.raises(CollaborationContractError, match="unlisted"):
        inventory(records + [reseal(extra)], snapshot)


def test_conflicting_duplicate_cannot_rewrite_authoritative_inventory():
    _, _, _, records = fixture()
    snapshot = manifest(records)
    extra = deepcopy(records[-1])
    extra["payload"]["verdict"] = "rejected"
    with pytest.raises(CollaborationContractError, match="conflicting"):
        inventory(records + [reseal(extra)], snapshot)


def supplement_fixture(*, gap_type="business_evidence", acquisition="archive_read",
                       evidence_type="execution_record", source="ci", required="accuracy:execution_record"):
    card, result, proof, records = fixture()
    proof = evidence(result, evidence_type=evidence_type, source=source)
    records = records[:2] + [proof]
    gap = make("gap", "gap", {"target": binding(result), "gap_type": gap_type,
               "required_claims": [required], "allowed_sources": ["ci"], "reason": "Missing proof / 缺少证明",
               "attempt_id": "attempt-1", "input_snapshot": INPUT_BINDING, "active_read_authorized": True,
               "authorization_binding": RULE_BINDING, "allowed_paths": ["/verification_candidates/accuracy"],
               "deadline_at": "2026-09-09T03:10:00Z", "max_reads": 2, "max_rounds": 1, "receiver": "lead"}, actor="lead")
    candidate = make("supplement_candidate", "candidate", {"gap": binding(gap), "target": binding(result),
                      "acquisition": acquisition, "evidence": [binding(proof)], "observation_run_id": "probe-run-1",
                      "idempotency_key": "gap-answer-v1", "candidate_path": "/verification_candidates/accuracy",
                      "generated_at": "2026-09-09T03:00:00Z", "expires_at": "2026-09-09T03:10:00Z",
                      "reads_used": 1, "rounds_used": 1}, actor="probe")
    records += [gap, candidate]
    return card, result, proof, candidate, records


def test_existing_historical_evidence_can_be_returned_without_changing_success():
    card, _, _, candidate, records = supplement_fixture()
    state = inventory(records)
    before = assess_delivery(state, card["id"])
    validate_supplement(state, candidate)
    assert not before["allowed"]
    assert assess_delivery(state, card["id"]) == before


@pytest.mark.parametrize("kwargs,error", [
    ({"gap_type": "business_incomplete"}, "business_work"),
    ({"source": "unapproved"}, "unauthorized"),
    ({"acquisition": "current_state"}, "historical"),
    ({"acquisition": "current_state", "evidence_type": "approval"}, "historical"),
    ({"acquisition": "current_state", "evidence_type": "adjudication"}, "historical"),
    ({"acquisition": "current_state", "evidence_type": "current_state"}, "missing_requested"),
])
def test_probe_cannot_repair_business_or_fabricate_history(kwargs, error):
    _, _, _, candidate, records = supplement_fixture(**kwargs)
    with pytest.raises(CollaborationContractError, match=error):
        validate_supplement(inventory(records), candidate)


def test_current_state_is_accepted_only_for_requested_current_state_claim():
    _, _, _, candidate, records = supplement_fixture(acquisition="current_state",
                            evidence_type="current_state", required="accuracy:current_state")
    validate_supplement(inventory(records), candidate)


def test_stale_supplement_is_rejected():
    _, result, _, candidate, records = supplement_fixture()
    result = deepcopy(result)
    result["revision"] = 2
    records.append(reseal(result))
    with pytest.raises(CollaborationContractError, match="stale"):
        validate_supplement(inventory(records), candidate)


@pytest.mark.parametrize("recheck_kind,allowed", [("missing", False), ("unrelated", False), ("consumed", True)])
def test_adoption_requires_candidate_bound_business_recheck(recheck_kind, allowed):
    card, result, proof, candidate, records = supplement_fixture()
    recheck = None
    if recheck_kind != "missing":
        recheck = receipt(card, result, proof, "global", supplement=candidate if recheck_kind == "consumed" else None)
        records.append(recheck)
    disposition = make("supplement_receipt", "disposition", {"candidate": binding(candidate),
        "target": binding(result), "decision": "adopted", "reason": "Evidence checked / 证据已核验",
        "recheck": binding(recheck) if recheck else None, "disposed_at": "2026-09-09T03:02:00Z", "business_state_changed": False}, actor="lead")
    records.append(disposition)
    if allowed:
        validate_supplement_receipt(inventory(records), disposition)
    else:
        with pytest.raises(CollaborationContractError):
            validate_supplement_receipt(inventory(records), disposition)


def test_rejection_receipt_does_not_require_fabricated_revalidation():
    _, result, _, candidate, records = supplement_fixture()
    disposition = make("supplement_receipt", "disposition", {"candidate": binding(candidate),
        "target": binding(result), "decision": "rejected", "reason": "Not sufficient / 不充分", "recheck": None, "disposed_at": "2026-09-09T03:02:00Z", "business_state_changed": False}, actor="lead")
    records.append(disposition)
    validate_supplement_receipt(inventory(records), disposition)


def test_low_risk_role_sharing_requires_explicit_policy():
    card = task()
    card["payload"].update(acceptor="worker", separation_required=False)
    validate_record(reseal(card))
    card["payload"]["separation_required"] = True
    with pytest.raises(CollaborationContractError, match="self_acceptance"):
        validate_record(reseal(card))


@pytest.mark.parametrize("field,value", [("attempt_id", "attempt-2"), ("delegation_epoch", 2),
                                        ("worker", "new-worker"), ("revoked", True),
                                        ("input_snapshot", RULE_BINDING)])
def test_reassignment_revokes_old_result_and_supplement(field, value):
    card, _, _, candidate, records = supplement_fixture()
    snapshot = manifest(records)
    snapshot["payload"]["active_assignments"][card["id"]][field] = value
    state = inventory(records, reseal(snapshot))
    assert "stale_or_revoked_attempt" in assess_delivery(state, card["id"])["reasons"]
    with pytest.raises(CollaborationContractError, match="revoked"):
        validate_supplement(state, candidate)


def test_optional_observation_missing_does_not_cancel_business_acceptance():
    card, result, _, records = fixture()
    gap = supplement_fixture()[4][-2]
    snapshot = manifest(records + [gap])
    state = inventory(records, snapshot)
    assert not state.complete and state.business_complete
    assert assess_delivery(state, card["id"])["allowed"]
    # A missing required proof still blocks even if telemetry is optional.
    missing = [item for item in records if item["kind"] != "evidence"]
    assert not assess_delivery(inventory(missing, snapshot), card["id"])["allowed"]


def test_global_acceptance_and_actual_delivery_are_separate_facts():
    card, _, _, records = fixture()
    records = [item for item in records if item["kind"] != "delivery_receipt"]
    result = assess_delivery(inventory(records), card["id"])
    assert result["acceptance_ready"] and not result["allowed"]
    assert result["reasons"] == ["missing_actual_delivery"]


@pytest.mark.parametrize("field,value", [("delivered_at", "2026-09-09T03:00:00Z"),
                                        ("delivered_at", "2026-09-09T04:00:00Z"),
                                        ("delivered_to", "wrong-recipient"), ("delivery_scope", "wrong-scope")])
def test_delivery_requires_correct_recipient_scope_and_causal_time(field, value):
    card, _, _, records = fixture()
    target = next(item for item in records if item["kind"] == "delivery_receipt")
    target["payload"][field] = value
    records = [reseal(item) if item["id"] == target["id"] else item for item in records]
    result = assess_delivery(inventory(records), card["id"])
    assert result["acceptance_ready"] and not result["allowed"]


@pytest.mark.parametrize("field,value", [("next_epoch", 1), ("committed_ledger_revision", 2),
                                        ("to_owner", "wrong-recipient"), ("committed_at", "2026-09-09T03:00:00Z")])
def test_handoff_acceptance_needs_trusted_atomic_transfer_attestation(field, value):
    card, _, _, records = fixture(handoff=True)
    target = next(item for item in records if item["kind"] == "responsibility_transfer")
    target["payload"][field] = value
    records = [reseal(item) if item["id"] == target["id"] else item for item in records]
    assert "missing_atomic_transfer_receipt" in assess_delivery(inventory(records), card["id"])["reasons"]


@pytest.mark.parametrize("field,value", [("access_verified", False), ("rule_binding", INPUT_BINDING)])
def test_receiver_access_and_frozen_acceptance_rules_are_required(field, value):
    card, _, _, records = fixture()
    records[-1]["payload"][field] = value
    records[-1] = reseal(records[-1])
    assert "missing_global_acceptance" in assess_delivery(inventory(records), card["id"])["reasons"]


def revise_candidate(records, candidate, **changes):
    revised = deepcopy(candidate)
    revised["payload"].update(changes)
    revised = reseal(revised)
    return revised, [revised if item["id"] == candidate["id"] else item for item in records]


@pytest.mark.parametrize("change,error", [
    ({"expires_at": "2026-09-09T03:04:00Z"}, "window"),
    ({"generated_at": "2026-09-09T03:06:00Z"}, "window"),
    ({"candidate_path": "/verification_candidates/unauthorized"}, "path"),
    ({"candidate_path": "/status"}, "path"),
    ({"reads_used": 3}, "budget"), ({"rounds_used": 2}, "budget"),
    ({"observation_run_id": "run-1"}, "independent"),
])
def test_supplement_window_path_budget_and_observer_identity(change, error):
    _, _, _, candidate, records = supplement_fixture()
    candidate, records = revise_candidate(records, candidate, **change)
    with pytest.raises(CollaborationContractError, match=error):
        validate_supplement(inventory(records), candidate)


def test_supplement_budget_includes_prior_rounds():
    _, _, _, candidate, records = supplement_fixture()
    snapshot = manifest(records)
    snapshot["payload"]["gap_usage"]["gap"]["rounds_used"] = 1
    with pytest.raises(CollaborationContractError, match="budget"):
        validate_supplement(inventory(records, reseal(snapshot)), candidate)


def test_offline_inspection_does_not_grant_active_read_permission():
    _, _, _, candidate, records = supplement_fixture()
    gap = deepcopy(records[-2])
    gap["payload"]["active_read_authorized"] = False
    gap = reseal(gap)
    records[-2] = gap
    candidate, records = revise_candidate(records, candidate, gap=binding(gap))
    with pytest.raises(CollaborationContractError, match="not_authorized"):
        validate_supplement(inventory(records), candidate)
    candidate, records = revise_candidate(records, candidate, acquisition="offline", reads_used=0)
    validate_supplement(inventory(records), candidate)


def test_other_attempt_success_evidence_cannot_repair_current_attempt():
    _, _, proof, candidate, records = supplement_fixture()
    proof["payload"]["attempt_id"] = "different-attempt"
    proof = reseal(proof)
    records[2] = proof
    candidate, records = revise_candidate(records, candidate, evidence=[binding(proof)])
    with pytest.raises(CollaborationContractError, match="evidence_attempt"):
        validate_supplement(inventory(records), candidate)


def test_authorization_evidence_does_not_auto_grant_permission():
    card, result, proof, candidate, records = supplement_fixture(gap_type="authorization")
    recheck = receipt(card, result, proof, "global", supplement=candidate)
    disposition = make("supplement_receipt", "disposition", {"candidate": binding(candidate),
        "target": binding(result), "decision": "adopted", "reason": "Requested / 已请求",
        "recheck": binding(recheck), "disposed_at": "2026-09-09T03:02:00Z", "business_state_changed": False}, actor="lead")
    with pytest.raises(CollaborationContractError, match="authority_workflow"):
        validate_supplement_receipt(inventory(records + [recheck, disposition]), disposition)


def test_supplement_idempotency_preserves_identical_package_and_rejects_conflict():
    _, _, _, candidate, records = supplement_fixture()
    state = inventory(records + [candidate])
    assert state.duplicates == 1
    validate_supplement(state, candidate)
    changed = deepcopy(candidate)
    changed["id"] = "another-package"
    with pytest.raises(CollaborationContractError, match="idempotency_conflict"):
        inventory(records + [reseal(changed)])


def test_adopted_observation_repair_does_not_require_or_create_business_acceptance():
    card, result, _, candidate, records = supplement_fixture(gap_type="observation_record")
    repair = make("observation_repair_receipt", "repair", {"candidate": binding(candidate),
        "target": binding(result), "view_ref": "fixture://repaired-observation",
        "repaired_at": "2026-09-09T03:01:00Z"}, actor="lead")
    disposition = make("supplement_receipt", "disposition", {"candidate": binding(candidate),
        "target": binding(result), "decision": "adopted", "reason": "Observation repaired / 观测已修复",
        "recheck": binding(repair), "disposed_at": "2026-09-09T03:02:00Z", "business_state_changed": False}, actor="lead")
    state = inventory(records + [repair, disposition])
    validate_supplement_receipt(state, disposition)
    assert not assess_delivery(state, card["id"])["allowed"]


def test_historical_adoption_survives_later_expiry_but_new_intake_fails():
    card, result, proof, candidate, records = supplement_fixture()
    recheck = receipt(card, result, proof, "global", supplement=candidate)
    disposition = make("supplement_receipt", "disposition", {"candidate": binding(candidate),
        "target": binding(result), "decision": "adopted", "reason": "Verified / 已核验",
        "recheck": binding(recheck), "disposed_at": "2026-09-09T03:02:00Z", "business_state_changed": False}, actor="lead")
    records += [recheck, disposition]
    snapshot = manifest(records)
    state = RecordInventory(snapshot, records, verify_record=verifier_for(snapshot, records), now="2026-09-09T03:20:00Z")
    validate_supplement_receipt(state, disposition)
    with pytest.raises(CollaborationContractError, match="window"):
        validate_supplement(state, candidate)
    disposition["payload"]["disposed_at"] = "2026-09-09T03:00:30Z"
    revised = reseal(disposition)
    with pytest.raises(CollaborationContractError, match="disposition_window"):
        validate_supplement_receipt(inventory(records[:-1] + [revised]), revised)


@pytest.mark.parametrize("field,value", [("tenant_id", "tenant-2"), ("request_id", "request-2"), ("plan_revision", 2)])
def test_shared_ids_do_not_cross_tenant_request_or_plan_boundaries(field, value):
    _, _, _, records = fixture()
    snapshot = manifest(records)
    record = deepcopy(records[-1])
    record[field] = value
    with pytest.raises(CollaborationContractError, match="cross_scope"):
        inventory(records[:-1] + [reseal(record)], snapshot)


def test_old_contract_cannot_migrate_by_changing_version_label_only():
    record = task()
    record["protocol_version"] = "2.0.0"
    with pytest.raises(CollaborationContractError, match="schema"):
        validate_record(reseal(record))
    record["protocol_version"] = "3.0.0"
    del record["payload"]["goal_binding"]
    with pytest.raises(CollaborationContractError, match="schema"):
        validate_record(reseal(record))


def test_independent_probe_deduplicates_and_preserves_unsupported_metrics():
    _, _, _, records = fixture()
    snapshot = manifest(records)
    batch = records + [records[0], records[0]]
    report = inspect_workflow(snapshot, batch, verify_record=verifier_for(snapshot, records), now=NOW,
                               enabled_metrics=["CM01", "CM09", "CM25", "CM31", "CM34"])
    assert report["delivery_ready"]
    assert report["metrics"]["CM01"]["value"] == 1
    assert report["metrics"]["CM09"]["value"] == 1
    assert report["metrics"]["CM25"]["value"] is None
    assert report["metrics"]["CM31"]["value"] == 2 / len(batch)
    assert report["metrics"]["CM34"]["value"] == 1 / 4


def test_missing_expected_task_stays_in_denominator():
    card, _, _, records = fixture()
    snapshot = manifest(records)
    missing = [record for record in records if record != card]
    report = inspect_workflow(snapshot, missing, verify_record=verifier_for(snapshot, records), now=NOW)
    assert report["metrics"]["CM01"]["value"] == 0
    assert report["metrics"]["CM01"]["denominator"] == 1
    assert report["metrics"]["CM09"]["value"] is None
    assert not report["delivery_ready"]


def test_empty_population_is_unknown_and_cannot_deliver():
    snapshot = manifest([])
    report = inspect_workflow(snapshot, [], verify_record=verifier_for(snapshot, []), now=NOW)
    assert report["metrics"]["CM01"]["value"] is None
    assert report["metrics"]["CM01"]["reason"] == "empty_population"
    assert not report["delivery_ready"]


@pytest.mark.parametrize("completeness", ["partial", "unknown"])
def test_incomplete_source_does_not_prove_completion(completeness):
    _, _, _, records = fixture()
    snapshot = manifest(records, completeness=completeness)
    report = inspect_workflow(snapshot, records, verify_record=verifier_for(snapshot, records), now=NOW)
    assert report["metrics"]["CM09"]["value"] is None
    assert not report["delivery_ready"]


def load_sync():
    spec = importlib.util.spec_from_file_location("sync_collaboration_docs", SKILL / "scripts/sync_collaboration_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_registered_contract_views_and_metric_dependencies_are_consistent():
    assert load_sync().validate_collaboration_assets(SKILL) == []


@pytest.mark.parametrize("mutation", ["version", "metric_probe", "shared_contract", "mode_cell",
                                     "source_snapshot", "source_formula", "test_reference"])
def test_drift_is_detected_against_registered_sources(tmp_path, mutation):
    target = tmp_path / "skills/harness-engineering-patterns"
    # Only the files needed by this validator are copied. / 仅复制本校验器实际需要的文件。
    paths = ["references/registry.json", "references/collaboration-protocol.json",
             "schemas/collaboration-record.schema.json", "runtime/collaboration_protocol.py",
             "references/collaboration-execution-flow.md", "references/collaboration-observability-probes.md",
             "references/collaboration-fulltext-source-map.json", "runtime/collaboration_observability.py"]
    paths.append("references/collaboration-observation-adapter.md")
    for relative in paths:
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SKILL / relative, path)
    source = json.loads((SKILL / "references/collaboration-fulltext-source-map.json").read_text("utf-8"))
    extra_paths = [item["snapshot_path"] for item in source["sources"]]
    extra_paths += ["tests/test_collaboration_protocol.py", "tests/test_collaboration_observability.py"]
    for relative in extra_paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, path)
    assert load_sync().validate_collaboration_assets(target) == []
    if mutation in {"version", "metric_probe"}:
        path = target / "references/collaboration-protocol.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        if mutation == "version":
            value["protocol_version"] = "99.0.0"
        else:
            value["metrics"][0]["probe_ref"] = "CP99"
        path.write_text(json.dumps(value), encoding="utf-8")
    elif mutation == "shared_contract":
        path = target / "references/collaboration-observability-probes.md"
        path.write_text(path.read_text(encoding="utf-8").replace("`record_hash`", "`wrong_hash`"), encoding="utf-8")
    elif mutation == "mode_cell":
        path = target / "references/registry.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["module_protocols"][0]["mode_cells"]["handoff_chain"] = "CELL_COLLABORATION_ROUTING"
        path.write_text(json.dumps(value), encoding="utf-8")
    elif mutation == "source_snapshot":
        path = tmp_path / source["sources"][0]["snapshot_path"]
        path.write_bytes(path.read_bytes() + b"\nchanged\n")
    else:
        path = target / "references/collaboration-fulltext-source-map.json"
        value = json.loads(path.read_text("utf-8"))
        if mutation == "source_formula":
            value["source_metrics"][0]["formula_zh"] = "Invented formula / 虚构算式"
        else:
            value["execution_cases"][0]["reference_tests"] = ["tests/test_collaboration_protocol.py::test_nonexistent"]
        path.write_text(json.dumps(value), encoding="utf-8")
    assert load_sync().validate_collaboration_assets(target)
