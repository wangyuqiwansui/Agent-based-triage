"""Executable tests for exact-version Generator-Critic / 精确版本生成评审可执行测试。"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from generator_critic import (  # noqa: E402
    GeneratorCriticAuthorizationError,
    GeneratorCriticReleaseError,
    GeneratorCriticSession,
    GeneratorCriticState,
    GeneratorCriticStateError,
    GeneratorCriticValidationError,
    artifact_binding,
    build_generator_critic_contract,
    validate_generator_critic_contract,
    validate_generator_critic_event_stream,
)
from reflection_runtime import resolve_reflection_required_probes  # noqa: E402


HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
HASH_C = "sha256:" + "c" * 64
HASH_D = "sha256:" + "d" * 64
T0 = "2026-08-13T08:00:00Z"


def binding(identifier: str, digest: str = HASH_A) -> dict[str, str]:
    return {"id": identifier, "version": "1.0.0", "hash": digest}


def allow_shared_reflection(
    stage: str, context: dict[str, object]
) -> dict[str, str]:
    revision = context["artifact_binding"]["revision"]  # type: ignore[index]
    return binding(f"shared-assurance-{stage}-{revision}", HASH_D)


def contract_example(
    *,
    max_passes: int = 2,
    minimum_score: float | None = 0.8,
    warning_action: str = "needs_revision",
) -> dict[str, object]:
    contract: dict[str, object] = {
        "schema_version": "1.0.0",
        "contract_id": "generator-critic-contract-1",
        "contract_version": "1.0.0",
        "reflection_contract_binding": binding("reflection-contract-1", HASH_B),
        "run_binding": binding("run-1", HASH_C),
        "artifact_policy": {
            "artifact_id": "artifact-1",
            "artifact_type": "report",
            "initial_revision": 0,
            "max_revisions": 2,
            "immutable_append_only": True,
        },
        "roles": {
            "generator_binding": binding("generator", HASH_A),
            "critic_binding": binding("critic", HASH_B),
            "critic_configuration_binding": binding("critic-config", HASH_C),
            "reviser_binding": binding("reviser", HASH_D),
            "policy_gate_binding": binding("policy-gate", HASH_A),
            "release_gate_binding": binding("release-gate", HASH_B),
        },
        "criteria": [
            {
                "criterion_id": "criterion-accuracy",
                "description": "Claims must match the evidence. / 论断必须匹配证据。",
                "check_id": "check-accuracy",
                "default_severity": "blocking",
                "evidence_required": True,
                "risk_refs": ["risk-factual-error"],
                "validator_binding": binding("accuracy-validator", HASH_C),
            },
            {
                "criterion_id": "criterion-style",
                "description": "Output must follow the requested style. / 输出必须符合指定风格。",
                "check_id": "check-style",
                "default_severity": "warning",
                "evidence_required": False,
                "risk_refs": ["risk-usability"],
                "validator_binding": None,
            },
        ],
        "review_policy": {
            "feedback_variant": "cross_model",
            "max_critique_passes": max_passes,
            "require_full_criteria_coverage": True,
            "preserve_unsupported_opinions": True,
            "require_clean_context": True,
        },
        "decision_policy": {
            "blocking_severities": ["blocking"],
            "warning_action": warning_action,
            "unknown_action": "wait_for_evidence",
            "minimum_score": minimum_score,
            "below_minimum_score_action": "needs_revision",
            "exhausted_action": "human_required",
        },
        "release_policy": {
            "require_receipt": True,
            "require_exact_artifact_digest": True,
            "require_current_policy": True,
            "require_fresh_evidence": True,
            "default_receipt_ttl_seconds": 86400,
        },
        "governance_policy_binding": binding("governance-policy", HASH_D),
        "created_at": T0,
    }
    return build_generator_critic_contract(contract)


def snapshot(
    identifier: str = "evidence-1",
    *,
    expires_at: str | None = "2026-08-14T08:00:00Z",
) -> dict[str, object]:
    return {
        "binding": binding(identifier, HASH_C),
        "source_kind": "system_query",
        "authority_level": "primary",
        "content_summary": "Independent validator result. / 独立验证器结果。",
        "acquired_at": "2026-08-13T08:01:00Z",
        "expires_at": expires_at,
    }


def passing_results(evidence: dict[str, str]) -> list[dict[str, object]]:
    return [
        {
            "criterion_id": "criterion-accuracy",
            "check_id": "check-accuracy",
            "status": "pass",
            "finding_refs": [],
            "evidence_bindings": [evidence],
            "notes": "Verified. / 已验证。",
        },
        {
            "criterion_id": "criterion-style",
            "check_id": "check-style",
            "status": "pass",
            "finding_refs": [],
            "evidence_bindings": [],
            "notes": "Conforms. / 符合。",
        },
    ]


def failing_results(evidence: dict[str, str]) -> list[dict[str, object]]:
    return [
        {
            "criterion_id": "criterion-accuracy",
            "check_id": "check-accuracy",
            "status": "fail",
            "finding_refs": ["issue-accuracy-1"],
            "evidence_bindings": [evidence],
            "notes": "Mismatch found. / 发现不匹配。",
        },
        {
            "criterion_id": "criterion-style",
            "check_id": "check-style",
            "status": "pass",
            "finding_refs": [],
            "evidence_bindings": [],
            "notes": "Conforms. / 符合。",
        },
    ]


def supported_finding(evidence: dict[str, str]) -> dict[str, object]:
    return {
        "issue_id": "issue-accuracy-1",
        "severity": "blocking",
        "description": "A claim conflicts with the system result. / 论断与系统结果冲突。",
        "location": "section-2",
        "criterion_id": "criterion-accuracy",
        "check_id": "check-accuracy",
        "evidence_bindings": [evidence],
        "evidence_summary": "Expected A, observed B. / 预期 A，实际 B。",
        "risk_refs": ["risk-factual-error"],
    }


def unsupported_opinion() -> dict[str, object]:
    return {
        "opinion_id": "opinion-tone-1",
        "description": "The tone feels flat. / 语气似乎平淡。",
        "proposed_severity": "warning",
        "criterion_id": "criterion-style",
        "reason": "unverifiable",
        "evidence_bindings": [],
        "preserved_non_gating": True,
    }


def create_session(
    contract: dict[str, object] | None = None,
    *,
    shared_reflection_guard=allow_shared_reflection,
) -> GeneratorCriticSession:
    session = GeneratorCriticSession(
        contract or contract_example(),
        session_id="generator-critic-session-1",
        shared_reflection_guard=shared_reflection_guard,
    )
    session.create_initial_artifact(
        content={"text": "draft-0"},
        content_ref="memory://artifact-1/revision-0",
        producer_binding=binding("generator", HASH_A),
        created_at=T0,
    )
    return session


def record_pass(
    session: GeneratorCriticSession,
    *,
    review_id: str,
    evidence_id: str,
    reviewed_at: str,
    score_value: float = 0.95,
    score_evidence: bool = True,
    opinions: list[dict[str, object]] | None = None,
    expires_at: str | None = "2026-08-14T08:00:00Z",
) -> dict[str, object]:
    evidence = binding(evidence_id, HASH_C)
    session.start_review(
        review_id=review_id,
        artifact=artifact_binding(session.current_artifact or {}),
        occurred_at=reviewed_at,
    )
    return session.record_review(
        evidence_snapshots=[snapshot(evidence_id, expires_at=expires_at)],
        criteria_results=passing_results(evidence),
        supported_findings=[],
        unsupported_opinions=opinions or [],
        score={
            "value": score_value,
            "evidence_bindings": [evidence] if score_evidence else [],
            "rationale": "Rubric score. / 量表评分。",
        },
        risk_refs_checked=["risk-factual-error", "risk-usability"],
        reviewed_at=reviewed_at,
    )


def test_end_to_end_revision_re_review_receipt_and_release() -> None:
    session = create_session()
    original = session.current_artifact
    assert original is not None and original["review_status"] == "unreviewed"

    evidence = binding("evidence-draft-0", HASH_C)
    session.start_review(
        review_id="review-0",
        artifact=artifact_binding(original),
        occurred_at="2026-08-13T08:02:00Z",
    )
    review0 = session.record_review(
        evidence_snapshots=[snapshot("evidence-draft-0")],
        criteria_results=failing_results(evidence),
        supported_findings=[supported_finding(evidence)],
        unsupported_opinions=[unsupported_opinion()],
        score={
            "value": 0.5,
            "evidence_bindings": [evidence],
            "rationale": "Blocking factual mismatch. / 存在阻断事实错误。",
        },
        risk_refs_checked=["risk-factual-error", "risk-usability"],
        reviewed_at="2026-08-13T08:03:00Z",
    )
    decision0 = session.decide(decided_at="2026-08-13T08:04:00Z")
    assert decision0["decision"] == "needs_revision"
    assert decision0["gating_issue_refs"] == ["issue-accuracy-1"]
    assert decision0["retained_opinion_refs"] == ["opinion-tone-1"]
    assert review0["artifact_binding"] == artifact_binding(original)

    revised = session.create_revision(
        content={"text": "draft-1-corrected"},
        content_ref="memory://artifact-1/revision-1",
        producer_binding=binding("reviser", HASH_D),
        resolved_issue_refs=["issue-accuracy-1"],
        created_at="2026-08-13T08:05:00Z",
    )
    assert revised["revision"] == 1
    assert revised["parent_binding"] == artifact_binding(original)
    assert revised["review_status"] == "unreviewed"

    record_pass(
        session,
        review_id="review-1",
        evidence_id="evidence-draft-1",
        reviewed_at="2026-08-13T08:06:00Z",
    )
    decision1 = session.decide(decided_at="2026-08-13T08:07:00Z")
    assert decision1["decision"] == "accept"
    receipt = session.issue_receipt(
        receipt_id="receipt-1",
        release_gate_binding=binding("release-gate", HASH_B),
        issued_at="2026-08-13T08:08:00Z",
    )
    assert receipt["shared_reflection_assurance_binding"]["id"].startswith(
        "shared-assurance-receipt-1"
    )
    event = session.verify_release(
        artifact=artifact_binding(revised),
        receipt=receipt,
        current_governance_policy_binding=binding("governance-policy", HASH_D),
        released_at="2026-08-13T08:09:00Z",
    )
    assert event["event_type"] == "artifact_release_verified"
    assert event["payload"]["shared_reflection_assurance_binding"]["id"].startswith(
        "shared-assurance-release-1"
    )
    assert session.state is GeneratorCriticState.RELEASED
    validate_generator_critic_event_stream(session.events)


def test_shared_reflection_guard_fails_closed_at_protected_boundary() -> None:
    session = GeneratorCriticSession(
        contract_example(),
        session_id="generator-critic-session-denied",
        shared_reflection_guard=lambda stage, context: True,  # type: ignore[return-value]
    )
    with pytest.raises(
        GeneratorCriticAuthorizationError,
        match="exact assurance binding",
    ):
        session.create_initial_artifact(
            content={"text": "draft-0"},
            content_ref="memory://artifact-1/revision-0",
            producer_binding=binding("generator", HASH_A),
            created_at=T0,
        )
    assert session.artifacts == ()
    assert session.events == ()


def test_receipt_requires_shared_independent_revalidation_assurance() -> None:
    def deny_receipt(stage: str, context: dict[str, object]):
        if stage == "receipt":
            return None
        return allow_shared_reflection(stage, context)

    session = create_session(shared_reflection_guard=deny_receipt)
    record_pass(
        session,
        review_id="review-assurance",
        evidence_id="evidence-assurance",
        reviewed_at="2026-08-13T08:02:00Z",
    )
    session.decide(decided_at="2026-08-13T08:03:00Z")
    with pytest.raises(
        GeneratorCriticAuthorizationError,
        match="exact assurance binding",
    ):
        session.issue_receipt(
            receipt_id="receipt-denied",
            release_gate_binding=binding("release-gate", HASH_B),
            issued_at="2026-08-13T08:04:00Z",
        )
    assert session.receipts == ()
    assert session.state is GeneratorCriticState.ACCEPTED


def test_unsupported_opinion_and_unevidenced_score_do_not_gate() -> None:
    session = create_session()
    review = record_pass(
        session,
        review_id="review-opinion",
        evidence_id="evidence-opinion",
        reviewed_at="2026-08-13T08:02:00Z",
        score_value=0.2,
        score_evidence=False,
        opinions=[unsupported_opinion()],
    )
    decision = session.decide(decided_at="2026-08-13T08:03:00Z")
    assert review["unsupported_opinions"][0]["preserved_non_gating"] is True
    assert decision["decision"] == "accept"
    assert "POLICY_UNEVIDENCED_SCORE_NON_GATING" in decision["triggered_rules"]
    assert decision["gating_issue_refs"] == []
    assert decision["retained_opinion_refs"] == ["opinion-tone-1"]


def test_review_must_bind_current_exact_revision() -> None:
    session = create_session()
    original = session.current_artifact
    assert original is not None
    evidence = binding("evidence-0", HASH_C)
    session.start_review(
        review_id="review-0",
        artifact=artifact_binding(original),
        occurred_at="2026-08-13T08:01:30Z",
    )
    session.record_review(
        evidence_snapshots=[snapshot("evidence-0")],
        criteria_results=failing_results(evidence),
        supported_findings=[supported_finding(evidence)],
        unsupported_opinions=[],
        score={"value": 0.4, "evidence_bindings": [evidence], "rationale": "Failed. / 失败。"},
        risk_refs_checked=["risk-factual-error", "risk-usability"],
        reviewed_at="2026-08-13T08:02:00Z",
    )
    session.decide(decided_at="2026-08-13T08:03:00Z")
    session.create_revision(
        content={"text": "draft-1"},
        content_ref="memory://artifact-1/revision-1",
        producer_binding=binding("reviser", HASH_D),
        resolved_issue_refs=["issue-accuracy-1"],
        created_at="2026-08-13T08:04:00Z",
    )
    with pytest.raises(GeneratorCriticStateError, match="current exact artifact"):
        session.start_review(
            review_id="review-stale",
            artifact=artifact_binding(original),
            occurred_at="2026-08-13T08:05:00Z",
        )


def test_new_content_invalidates_old_receipt_and_requires_explicit_re_review() -> None:
    session = create_session()
    record_pass(
        session,
        review_id="review-accepted",
        evidence_id="evidence-accepted",
        reviewed_at="2026-08-13T08:02:00Z",
    )
    session.decide(decided_at="2026-08-13T08:03:00Z")
    receipt = session.issue_receipt(
        receipt_id="receipt-old",
        release_gate_binding=binding("release-gate", HASH_B),
        issued_at="2026-08-13T08:04:00Z",
    )
    new_artifact = session.create_superseding_revision(
        content={"text": "accepted-but-edited"},
        content_ref="memory://artifact-1/revision-1",
        producer_binding=binding("reviser", HASH_D),
        change_proposal_binding=binding("post-review-edit-proposal", HASH_C),
        change_reason="Post-review content edit. / 评审后内容变更。",
        created_at="2026-08-13T08:05:00Z",
    )
    assert new_artifact["review_status"] == "unreviewed"
    assert session.state is GeneratorCriticState.ARTIFACT_UNREVIEWED
    invalidated = session.events[-1]["payload"]["invalidated_receipt_bindings"]
    assert invalidated[0]["hash"] == receipt["receipt_hash"]
    with pytest.raises(GeneratorCriticStateError):
        session.verify_release(
            artifact=artifact_binding(new_artifact),
            receipt=receipt,
            current_governance_policy_binding=binding("governance-policy", HASH_D),
            released_at="2026-08-13T08:06:00Z",
        )


def test_second_blocking_review_escalates_at_chain_budget() -> None:
    session = create_session()
    for index in range(2):
        evidence_id = f"evidence-fail-{index}"
        evidence = binding(evidence_id, HASH_C)
        session.start_review(
            review_id=f"review-fail-{index}",
            artifact=artifact_binding(session.current_artifact or {}),
            occurred_at=f"2026-08-13T08:0{index * 3 + 1}:00Z",
        )
        session.record_review(
            evidence_snapshots=[snapshot(evidence_id)],
            criteria_results=failing_results(evidence),
            supported_findings=[supported_finding(evidence)],
            unsupported_opinions=[],
            score={"value": 0.4, "evidence_bindings": [evidence], "rationale": "Failed. / 失败。"},
            risk_refs_checked=["risk-factual-error", "risk-usability"],
            reviewed_at=f"2026-08-13T08:0{index * 3 + 2}:00Z",
        )
        decision = session.decide(
            decided_at=f"2026-08-13T08:0{index * 3 + 3}:00Z"
        )
        if index == 0:
            assert decision["decision"] == "needs_revision"
            session.create_revision(
                content={"text": "still-wrong"},
                content_ref="memory://artifact-1/revision-1",
                producer_binding=binding("reviser", HASH_D),
                resolved_issue_refs=["issue-accuracy-1"],
                created_at="2026-08-13T08:04:00Z",
            )
        else:
            assert decision["decision"] == "human_required"
            assert "POLICY_REVIEW_BUDGET_EXHAUSTED" in decision["triggered_rules"]
    assert session.state is GeneratorCriticState.HUMAN_REQUIRED


def test_only_policy_adopted_issues_can_drive_automatic_revision() -> None:
    session = create_session()
    evidence = binding("evidence-guard", HASH_C)
    session.start_review(
        review_id="review-guard",
        artifact=artifact_binding(session.current_artifact or {}),
        occurred_at="2026-08-13T08:01:30Z",
    )
    session.record_review(
        evidence_snapshots=[snapshot("evidence-guard")],
        criteria_results=failing_results(evidence),
        supported_findings=[supported_finding(evidence)],
        unsupported_opinions=[unsupported_opinion()],
        score={"value": 0.4, "evidence_bindings": [evidence], "rationale": "Failed. / 失败。"},
        risk_refs_checked=["risk-factual-error", "risk-usability"],
        reviewed_at="2026-08-13T08:02:00Z",
    )
    session.decide(decided_at="2026-08-13T08:03:00Z")
    with pytest.raises(GeneratorCriticAuthorizationError, match="policy-adopted"):
        session.create_revision(
            content={"text": "changed-for-opinion"},
            content_ref="memory://artifact-1/revision-1",
            producer_binding=binding("reviser", HASH_D),
            resolved_issue_refs=["opinion-tone-1"],
            created_at="2026-08-13T08:04:00Z",
        )


def test_release_fails_for_stale_evidence_or_changed_policy() -> None:
    session = create_session()
    record_pass(
        session,
        review_id="review-expiring",
        evidence_id="evidence-expiring",
        reviewed_at="2026-08-13T08:02:00Z",
        expires_at="2026-08-13T09:00:00Z",
    )
    session.decide(decided_at="2026-08-13T08:03:00Z")
    receipt = session.issue_receipt(
        receipt_id="receipt-expiring",
        release_gate_binding=binding("release-gate", HASH_B),
        issued_at="2026-08-13T08:04:00Z",
    )
    with pytest.raises(GeneratorCriticReleaseError, match="policy changed"):
        session.verify_release(
            artifact=artifact_binding(session.current_artifact or {}),
            receipt=receipt,
            current_governance_policy_binding=binding("governance-policy-v2", HASH_A),
            released_at="2026-08-13T08:30:00Z",
        )
    with pytest.raises(GeneratorCriticReleaseError, match="snapshot expired"):
        session.verify_release(
            artifact=artifact_binding(session.current_artifact or {}),
            receipt=receipt,
            current_governance_policy_binding=binding("governance-policy", HASH_D),
            released_at="2026-08-13T10:00:00Z",
        )


def test_review_requires_full_criteria_and_trusted_fresh_evidence() -> None:
    session = create_session()
    evidence = binding("evidence-incomplete", HASH_C)
    session.start_review(
        review_id="review-incomplete",
        artifact=artifact_binding(session.current_artifact or {}),
        occurred_at="2026-08-13T08:01:30Z",
    )
    incomplete = passing_results(evidence)[:1]
    with pytest.raises(GeneratorCriticValidationError, match="every sealed criterion"):
        session.record_review(
            evidence_snapshots=[snapshot("evidence-incomplete")],
            criteria_results=incomplete,
            supported_findings=[],
            unsupported_opinions=[],
            score={"value": 0.9, "evidence_bindings": [evidence], "rationale": "Partial. / 不完整。"},
            risk_refs_checked=["risk-factual-error"],
            reviewed_at="2026-08-13T08:02:00Z",
        )


def test_contract_role_separation_failure_is_explicit() -> None:
    contract = contract_example()
    broken = deepcopy(contract)
    broken.pop("contract_hash")
    broken["roles"]["policy_gate_binding"] = deepcopy(
        broken["roles"]["critic_binding"]
    )
    with pytest.raises(GeneratorCriticValidationError, match="critic and policy gate"):
        build_generator_critic_contract(broken)


def test_generator_critic_probe_profile_adds_exact_version_probes() -> None:
    probes = resolve_reflection_required_probes(generator_critic=True)
    assert set(f"PROBE_{number:04d}" for number in range(16, 22)).issubset(probes)
    assert set(f"PROBE_{number:04d}" for number in range(24, 28)).issubset(probes)
