"""Executable tests for governed reflection / 受治理反思可执行测试。"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "harness-engineering-patterns"
SCHEMA_DIR = SKILL_DIR / "schemas"
RUNTIME_DIR = SKILL_DIR / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from reasoning_artifacts import ArtifactValidationError, artifact_fingerprint  # noqa: E402
from reflection_runtime import (  # noqa: E402
    ReflectionAuthorizationError,
    ReflectionImprovementState,
    ReflectionOutcome,
    ReflectionSession,
    ReflectionState,
    ReflectionStateError,
    ReflectionValidationError,
    build_reflection_contract,
    resolve_reflection_required_probes,
    validate_reflection_event,
    validate_reflection_event_stream,
    validate_reflection_round_observation,
)


NOW = "2026-08-12T08:00:00Z"
HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
HASH_C = "sha256:" + "c" * 64
HASH_D = "sha256:" + "d" * 64


def binding(identifier: str, digest: str = HASH_A) -> dict[str, str]:
    return {"id": identifier, "version": "1.0.0", "hash": digest}


def contract_example(
    *,
    eligibility: str = "admitted",
    route: str = "self_heal",
    evidence_plan: bool = False,
    validator_change: bool = False,
    min_independent_signals: int = 1,
    terminal_outcomes: list[str] | None = None,
    learning_enabled: bool = False,
) -> dict[str, object]:
    subject = binding("artifact-1", HASH_A)
    main_validator = binding("validator-main", HASH_B)
    regression_validator = binding("validator-regression", HASH_C)
    general_authorizer = binding("change-authorizer", HASH_D)
    contract: dict[str, object] = {
        "schema_version": "1.0.0",
        "contract_id": "reflection-contract-1",
        "contract_version": "1.0.0",
        "reflection_id": "reflection-1",
        "run_binding": binding("run-1", HASH_B),
        "subject_binding": subject,
        "admission": {
            "eligibility": eligibility,
            "route": route,
            "reason_codes": ["validator-failed"],
        },
        "trigger": {
            "trigger_type": "validation_failure",
            "evidence_bindings": [binding("failure-report", HASH_C)],
            "evidence_plan_binding": (
                binding("evidence-plan", HASH_D) if evidence_plan else None
            ),
        },
        "baseline": {
            "subject_before_binding": subject,
            "criteria_binding": binding("acceptance-criteria", HASH_B),
            "validator_bindings": [main_validator, regression_validator],
            "regression_scope_bindings": [binding("passing-suite", HASH_D)],
            "environment_binding": binding("fixture", HASH_A),
            "metric_id": "target-pass-rate",
            "metric_value": 0.7,
            "measurement_evidence_bindings": [
                binding("baseline-measurement", HASH_B)
            ],
            "frozen_at": NOW,
        },
        "signal_policy": {
            "independence_requirement": "external_validator",
            "min_independent_signals": min_independent_signals,
            "max_information_only_rounds": 1,
        },
        "change_policy": {
            "allowed_targets": ["validator"] if validator_change else ["artifact"],
            "forbidden_targets": [] if validator_change else ["validator"],
            "authorizer_binding": general_authorizer,
            "verifier_change_policy": (
                "independent_approval_required" if validator_change else "forbidden"
            ),
            "max_changes_per_round": 1,
        },
        "validation_policy": {
            "mandatory_validator_bindings": [main_validator],
            "regression_validator_bindings": [regression_validator],
            "improvement_metric_id": "target-pass-rate",
            "improvement_direction": "higher_is_better",
            "improvement_threshold": 0.1,
            "comparison_policy": "fixed_baseline",
            "validator_change_authorizer_binding": (
                binding("validator-authorizer", HASH_C) if validator_change else None
            ),
        },
        "attribution_policy": {
            "observational_authority_bindings": [
                binding("observational-authority", HASH_A)
            ],
            "correlational_authority_bindings": [
                binding("correlational-authority", HASH_B)
            ],
            "controlled_replay_authority_bindings": [
                binding("controlled-replay-authority", HASH_C)
            ],
            "intervention_authority_bindings": [
                binding("intervention-authority", HASH_D)
            ],
        },
        "learning_policy": {
            "promotion_enabled": learning_enabled,
            "allowed_targets": ["skill"] if learning_enabled else [],
            "minimum_evidence_bindings": 1,
            "promotion_authorizer_binding": (
                binding("learning-authorizer", HASH_A)
                if learning_enabled
                else None
            ),
            "owner_binding": (
                binding("learning-owner", HASH_B) if learning_enabled else None
            ),
        },
        "stop_policy": {
            "max_rounds": 3,
            "max_no_result_progress_rounds": 1,
            "terminal_outcomes": terminal_outcomes
            or ["accepted", "rolled_back", "handed_off", "rejected", "aborted"],
            "rollback_binding": binding("rollback-plan", HASH_A),
            "handoff_binding": binding("handoff-plan", HASH_B),
        },
        "governance_binding": binding("reflection-policy", HASH_D),
        "created_at": NOW,
    }
    return build_reflection_contract(contract)


def qualified_signal() -> dict[str, object]:
    return {
        "qualified": True,
        "independence": "external_validator",
        "information_gain": "confirmed_deviation",
        "evidence_bindings": [binding("fresh-test-result", HASH_C)],
    }


def passing_validation(candidate: dict[str, str]) -> dict[str, object]:
    return {
        "status": "passed",
        "candidate_binding": candidate,
        "criteria_binding": binding("acceptance-criteria", HASH_B),
        "environment_binding": binding("fixture", HASH_A),
        "mandatory_pass": True,
        "regression_pass": True,
        "metric_id": "target-pass-rate",
        "baseline_value": 0.7,
        "result_value": 0.9,
        "improvement_delta": 0.2,
        "threshold_met": True,
        "independent_signal_count": 1,
        "independent_signal_bindings": [binding("fresh-test-result", HASH_C)],
        "comparison_state": "comparable",
        "rebased_baseline": None,
        "validator_gaming": False,
        "result_progress": True,
        "information_progress": True,
        "validator_bindings": [
            binding("validator-main", HASH_B),
            binding("validator-regression", HASH_C),
        ],
        "evidence_bindings": [binding("revalidation-report", HASH_D)],
    }


def not_run_validation(
    *,
    information_progress: bool,
    signal_bindings: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    signals = signal_bindings or []
    return {
        "status": "not_run",
        "candidate_binding": None,
        "criteria_binding": None,
        "environment_binding": None,
        "mandatory_pass": None,
        "regression_pass": None,
        "metric_id": None,
        "baseline_value": None,
        "result_value": None,
        "improvement_delta": None,
        "threshold_met": None,
        "independent_signal_count": len(signals),
        "independent_signal_bindings": signals,
        "comparison_state": "not_evaluated",
        "rebased_baseline": None,
        "validator_gaming": False,
        "result_progress": False,
        "information_progress": information_progress,
        "validator_bindings": [],
        "evidence_bindings": [],
    }


def prepare_revalidating_session(
    contract: dict[str, object],
    *,
    round_id: str = "round-1",
    changed: dict[str, str] | None = None,
) -> tuple[ReflectionSession, dict[str, str]]:
    session = ReflectionSession(contract)
    candidate = changed or binding("artifact-2", HASH_D)
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    session.start_round(
        round_id=round_id,
        new_signal=qualified_signal(),
        occurred_at=NOW,
    )
    session.record_deviation(
        code="schema-mismatch",
        evidence_bindings=[binding("fresh-test-result", HASH_C)],
        details={"failed_checks": 1},
        occurred_at=NOW,
    )
    target = "validator" if contract["change_policy"]["allowed_targets"] == ["validator"] else "artifact"
    session.propose_change(
        target=target,
        proposal_binding=binding("patch-1", HASH_B),
        occurred_at=NOW,
    )
    session.authorize_change(
        authorization_binding=binding("change-authorizer", HASH_D),
        validator_change_approval_binding=(
            binding("validator-authorizer", HASH_C)
            if target == "validator"
            else None
        ),
        occurred_at=NOW,
    )
    session.record_change_applied(
        subject_after_binding=candidate,
        occurred_at=NOW,
    )
    session.start_revalidation(
        validator_bindings=[
            binding("validator-main", HASH_B),
            binding("validator-regression", HASH_C),
        ],
        occurred_at=NOW,
    )
    return session, candidate


@pytest.mark.parametrize(
    "name",
    ("reflection-contract", "reflection-event", "reflection-round-observation"),
)
def test_reflection_schemas_are_draft_2020_12_and_bilingual(name: str) -> None:
    schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["x-contract-version"] == "1.0.0"
    for field in ("title", "description"):
        assert "/" in schema[field]
        assert any("\u4e00" <= char <= "\u9fff" for char in schema[field])


def test_happy_path_closes_with_comparable_regression_free_improvement() -> None:
    contract = contract_example()
    session = ReflectionSession(contract)
    changed = binding("artifact-2", HASH_D)

    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    session.start_round(round_id="round-1", new_signal=qualified_signal(), occurred_at=NOW)
    session.record_deviation(
        code="schema-mismatch",
        evidence_bindings=[binding("fresh-test-result", HASH_C)],
        details={"failed_checks": 1},
        occurred_at=NOW,
    )
    session.record_attribution_hypothesis(
        hypothesis="the artifact schema is stale",
        falsifier="the same failure persists after a schema-only correction",
        confounders=["fixture drift"],
        occurred_at=NOW,
    )
    session.propose_change(
        target="artifact",
        proposal_binding=binding("patch-1", HASH_B),
        occurred_at=NOW,
    )
    session.authorize_change(
        authorization_binding=binding("change-authorizer", HASH_D),
        occurred_at=NOW,
    )
    session.record_change_applied(subject_after_binding=changed, occurred_at=NOW)
    session.start_revalidation(
        validator_bindings=[
            binding("validator-main", HASH_B),
            binding("validator-regression", HASH_C),
        ],
        occurred_at=NOW,
    )
    observation = session.close_round(
        outcome=ReflectionOutcome.ACCEPTED,
        validation=passing_validation(changed),
        improvement_state=ReflectionImprovementState.VERIFIED_IMPROVEMENT,
        attribution=None,
        occurred_at=NOW,
        stop_reason="contract threshold passed without regression",
    )

    assert session.state is ReflectionState.ACCEPTED
    assert observation["terminal"] is True
    assert observation["outcome"] == "accepted"
    assert observation["observation_hash"] == artifact_fingerprint(
        observation, "observation_hash"
    )
    assert [event["sequence"] for event in session.events] == list(
        range(1, len(session.events) + 1)
    )
    assert session.events[-1]["event_type"] == "reflection_stopped"
    for event in session.events:
        validate_reflection_event(event)
    validate_reflection_event_stream(session.events, contract=contract)
    validate_reflection_round_observation(
        observation,
        contract=contract,
        events=session.events,
    )

    forged = deepcopy(observation)
    forged["validation"]["improvement_delta"] = 0.05
    forged["validation"]["threshold_met"] = False
    forged["observation_hash"] = artifact_fingerprint(forged, "observation_hash")
    with pytest.raises(ReflectionValidationError, match="improvement|threshold"):
        validate_reflection_round_observation(
            forged,
            contract=contract,
            events=session.events,
        )


def test_contract_rejects_route_inconsistent_with_eligibility() -> None:
    contract = contract_example()
    drifted = deepcopy(contract)
    drifted["admission"]["route"] = "release"
    drifted["contract_hash"] = artifact_fingerprint(drifted, "contract_hash")

    with pytest.raises(ReflectionValidationError, match="route"):
        ReflectionSession(drifted)


def test_private_reasoning_is_rejected_recursively_from_event_payload() -> None:
    session = ReflectionSession(contract_example())
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    session.start_round(round_id="round-private", new_signal=qualified_signal(), occurred_at=NOW)

    with pytest.raises(ArtifactValidationError):
        session.record_deviation(
            code="unsafe-payload",
            evidence_bindings=[binding("fresh-test-result", HASH_C)],
            details={"outer": [{"chain_of_thought": "must not persist"}]},
            occurred_at=NOW,
        )

    for private_key in (
        "private_reasoning",
        "internal_thoughts",
        "private_chain_of_thought",
        "chainOfThought",
        "PrivateReasoning",
        "internalThought",
        "hiddenReasoning",
        "thought_process",
        "reasoning_trace",
        "hidden-thoughts",
        "cot",
        "COT",
        "inner_monologue",
        "innerMonologue",
        "deliberation",
        "思维链",
        "内部推理",
    ):
        with pytest.raises(ArtifactValidationError):
            session.record_deviation(
                code="unsafe-payload",
                evidence_bindings=[binding("fresh-test-result", HASH_C)],
                details={private_key: "must not persist"},
                occurred_at=NOW,
            )


def test_qualified_signal_requires_real_information_gain() -> None:
    session = ReflectionSession(contract_example())
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    no_gain = qualified_signal()
    no_gain["information_gain"] = "none"

    with pytest.raises(ReflectionValidationError, match="information gain"):
        session.start_round(
            round_id="round-no-gain",
            new_signal=no_gain,
            occurred_at=NOW,
        )


def test_validator_gaming_and_regression_cannot_continue_or_accept() -> None:
    session = ReflectionSession(contract_example())
    changed = binding("artifact-2", HASH_D)
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    session.start_round(round_id="round-gaming", new_signal=qualified_signal(), occurred_at=NOW)
    session.propose_change(
        target="artifact",
        proposal_binding=binding("patch-1", HASH_B),
        occurred_at=NOW,
    )
    session.authorize_change(
        authorization_binding=binding("change-authorizer", HASH_D),
        occurred_at=NOW,
    )
    session.record_change_applied(subject_after_binding=changed, occurred_at=NOW)
    session.start_revalidation(
        validator_bindings=[
            binding("validator-main", HASH_B),
            binding("validator-regression", HASH_C),
        ],
        occurred_at=NOW,
    )
    invalid = passing_validation(changed)
    invalid["validator_gaming"] = True
    invalid["regression_pass"] = False

    with pytest.raises(ReflectionValidationError):
        session.close_round(
            outcome="accepted",
            validation=invalid,
            improvement_state="verified_improvement",
            attribution=None,
            occurred_at=NOW,
            stop_reason="invalid acceptance",
        )
    assert session.state is ReflectionState.REVALIDATING
    assert session.events[-1]["event_type"] == "revalidation_started"


def test_acceptance_requires_deviation_and_revalidation_evidence() -> None:
    session = ReflectionSession(contract_example())
    changed = binding("artifact-2", HASH_D)
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    session.start_round(round_id="round-no-deviation", new_signal=qualified_signal(), occurred_at=NOW)
    session.propose_change(
        target="artifact",
        proposal_binding=binding("patch-1", HASH_B),
        occurred_at=NOW,
    )
    session.authorize_change(
        authorization_binding=binding("change-authorizer", HASH_D),
        occurred_at=NOW,
    )
    session.record_change_applied(subject_after_binding=changed, occurred_at=NOW)
    session.start_revalidation(
        validator_bindings=[
            binding("validator-main", HASH_B),
            binding("validator-regression", HASH_C),
        ],
        occurred_at=NOW,
    )
    invalid = passing_validation(changed)
    invalid["evidence_bindings"] = []

    with pytest.raises(ReflectionValidationError, match="deviation|evidence"):
        session.close_round(
            outcome="accepted",
            validation=invalid,
            improvement_state="verified_improvement",
            attribution=None,
            occurred_at=NOW,
            stop_reason="must not accept",
        )


def test_attribution_cannot_skip_from_hypothesis_to_intervention_verified() -> None:
    session = ReflectionSession(contract_example())
    changed = binding("artifact-2", HASH_D)
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    session.start_round(round_id="round-attribution", new_signal=qualified_signal(), occurred_at=NOW)
    session.record_deviation(
        code="schema-mismatch",
        evidence_bindings=[binding("fresh-test-result", HASH_C)],
        details={"failed_checks": 1},
        occurred_at=NOW,
    )
    session.record_attribution_hypothesis(
        hypothesis="the artifact schema is stale",
        falsifier="the failure persists after a schema-only correction",
        confounders=["fixture drift"],
        occurred_at=NOW,
    )
    session.propose_change(
        target="artifact",
        proposal_binding=binding("patch-1", HASH_B),
        occurred_at=NOW,
    )
    session.authorize_change(
        authorization_binding=binding("change-authorizer", HASH_D),
        occurred_at=NOW,
    )
    session.record_change_applied(subject_after_binding=changed, occurred_at=NOW)
    session.start_revalidation(
        validator_bindings=[
            binding("validator-main", HASH_B),
            binding("validator-regression", HASH_C),
        ],
        occurred_at=NOW,
    )

    with pytest.raises(ReflectionValidationError, match="evidence events"):
        session.close_round(
            outcome="accepted",
            validation=passing_validation(changed),
            improvement_state="verified_improvement",
            attribution={
                "state": "intervention_verified",
                "hypothesis": "the artifact schema was stale",
                "falsifier": "the failure persists after correction",
                "confounders": [],
                "evidence_kind": "intervention",
                "evidence_bindings": [binding("ordinary-report", HASH_D)],
            },
            occurred_at=NOW,
            stop_reason="must not accept attribution skip",
        )


def test_continuation_requires_progress_and_information_only_budget() -> None:
    session = ReflectionSession(contract_example(evidence_plan=True))
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    signal = {
        "qualified": False,
        "independence": "same_source",
        "information_gain": "none",
        "evidence_bindings": [],
    }
    session.start_round(round_id="round-evidence-1", new_signal=signal, occurred_at=NOW)
    with pytest.raises(ReflectionValidationError, match="progress"):
        session.close_round(
            outcome="continue",
            validation=not_run_validation(information_progress=False),
            improvement_state="not_evaluated",
            attribution=None,
            occurred_at=NOW,
        )

    evidence_signal = qualified_signal()
    session.record_new_signal(new_signal=evidence_signal, occurred_at=NOW)
    observation = session.close_round(
        outcome="continue",
        validation=not_run_validation(
            information_progress=True,
            signal_bindings=evidence_signal["evidence_bindings"],
        ),
        improvement_state="not_evaluated",
        attribution=None,
        occurred_at=NOW,
    )
    assert observation["terminal"] is False
    assert session.state is ReflectionState.ROUND_CLOSED

    session.start_round(round_id="round-evidence-2", new_signal=signal, occurred_at=NOW)
    second_signal = qualified_signal()
    second_signal["evidence_bindings"] = [binding("fresh-test-result-2", HASH_D)]
    session.record_new_signal(new_signal=second_signal, occurred_at=NOW)
    with pytest.raises(ReflectionStateError, match="budget is exhausted"):
        session.close_round(
            outcome="continue",
            validation=not_run_validation(
                information_progress=True,
                signal_bindings=second_signal["evidence_bindings"],
            ),
            improvement_state="not_evaluated",
            attribution=None,
            occurred_at=NOW,
        )


def test_validator_change_requires_distinct_independent_approval() -> None:
    session = ReflectionSession(contract_example(validator_change=True))
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    session.start_round(round_id="round-validator", new_signal=qualified_signal(), occurred_at=NOW)
    session.propose_change(
        target="validator",
        proposal_binding=binding("validator-patch", HASH_B),
        occurred_at=NOW,
    )

    with pytest.raises(ReflectionAuthorizationError, match="distinct"):
        session.authorize_change(
            authorization_binding=binding("change-authorizer", HASH_D),
            occurred_at=NOW,
        )

    event = session.authorize_change(
        authorization_binding=binding("change-authorizer", HASH_D),
        validator_change_approval_binding=binding("validator-authorizer", HASH_C),
        occurred_at=NOW,
    )
    assert event["event_type"] == "change_authorized"
    assert session.state is ReflectionState.CHANGE_AUTHORIZED


def test_nonadmitted_candidate_closes_without_manufactured_round() -> None:
    contract = contract_example(eligibility="needs_evidence", route="evidence_collection")
    session = ReflectionSession(contract)
    session.start(occurred_at=NOW)
    session.close_without_round(
        outcome="handed_off",
        reason="external evidence owner must supply the missing signal",
        occurred_at=NOW,
    )

    assert session.state is ReflectionState.HANDED_OFF
    assert not session.observations
    assert {event["event_type"] for event in session.events} == {
        "reflection_started",
        "reflection_eligibility_evaluated",
        "reflection_routed",
        "reflection_stopped",
    }


def test_reflection_probe_profile_is_explicit_and_conditional() -> None:
    assert resolve_reflection_required_probes() == tuple(
        f"PROBE_{number:04d}" for number in range(16, 22)
    )
    assert resolve_reflection_required_probes(
        attribution_claimed=True, learning_promotion=True
    ) == tuple(f"PROBE_{number:04d}" for number in range(16, 24))


def test_independent_signal_count_is_recomputed_from_qualified_signal_evidence() -> None:
    contract = contract_example(min_independent_signals=5)
    session, changed = prepare_revalidating_session(contract)
    forged = passing_validation(changed)
    forged["independent_signal_count"] = 5

    with pytest.raises(ReflectionValidationError, match="signal count"):
        session.close_round(
            outcome="accepted",
            validation=forged,
            improvement_state="verified_improvement",
            attribution=None,
            occurred_at=NOW,
            stop_reason="self-reported count must not pass",
        )


def test_comparable_baseline_value_is_contract_owned_not_self_reported() -> None:
    contract = contract_example()
    session, changed = prepare_revalidating_session(contract)
    forged = passing_validation(changed)
    forged["baseline_value"] = 0.6
    forged["result_value"] = 0.8
    forged["improvement_delta"] = 0.2

    with pytest.raises(ReflectionValidationError, match="metric baseline"):
        session.close_round(
            outcome="accepted",
            validation=forged,
            improvement_state="verified_improvement",
            attribution=None,
            occurred_at=NOW,
            stop_reason="self-selected baseline must not pass",
        )


def test_impossible_event_transition_is_rejected_after_rehash() -> None:
    session = ReflectionSession(contract_example())
    session.start(occurred_at=NOW)
    forged = deepcopy(session.events[0])
    forged.update(
        {
            "event_type": "change_applied",
            "round_id": "fake-round",
            "state_before": "candidate",
            "state_after": "accepted",
            "payload": {},
        }
    )
    forged["event_hash"] = artifact_fingerprint(forged, "event_hash")

    with pytest.raises(ReflectionValidationError, match="illegal|missing"):
        validate_reflection_event(forged)


def test_observation_tampering_cannot_replace_cross_bound_events() -> None:
    contract = contract_example()
    session, changed = prepare_revalidating_session(contract)
    observation = session.close_round(
        outcome="accepted",
        validation=passing_validation(changed),
        improvement_state="verified_improvement",
        attribution=None,
        occurred_at=NOW,
        stop_reason="valid closure",
    )
    forged = deepcopy(observation)
    forged["subject_before_binding"] = binding("forged-before", HASH_B)
    forged["baseline_binding"] = binding("forged-baseline", HASH_C)
    forged["change"]["authorization_binding"] = binding("forged-authority", HASH_A)
    forged["event_bindings"] = [
        binding("forged-event-1", HASH_A),
        binding("forged-event-2", HASH_B),
    ]
    forged["observation_hash"] = artifact_fingerprint(forged, "observation_hash")

    with pytest.raises(ReflectionValidationError, match="baseline|authorization|event"):
        validate_reflection_round_observation(
            forged,
            contract=contract,
            events=session.events,
        )


def test_information_progress_cannot_be_self_reported_without_acquired_signal() -> None:
    session = ReflectionSession(contract_example(evidence_plan=True))
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    empty_signal = {
        "qualified": False,
        "independence": "same_source",
        "information_gain": "none",
        "evidence_bindings": [],
    }
    session.start_round(
        round_id="evidence-only",
        new_signal=empty_signal,
        occurred_at=NOW,
    )

    with pytest.raises(ReflectionValidationError, match="information-progress"):
        session.close_round(
            outcome="continue",
            validation=not_run_validation(information_progress=True),
            improvement_state="not_evaluated",
            attribution=None,
            occurred_at=NOW,
        )


def test_attribution_evidence_is_persistent_and_never_reused() -> None:
    session = ReflectionSession(contract_example())
    session.start(occurred_at=NOW)
    session.freeze_baseline(occurred_at=NOW)
    session.start_round(
        round_id="attribution-evidence",
        new_signal=qualified_signal(),
        occurred_at=NOW,
    )
    evidence = [binding("attribution-evidence-1", HASH_A)]
    session.record_attribution_hypothesis(
        hypothesis="schema drift caused the failure",
        falsifier="a schema-only correction does not remove the failure",
        confounders=["fixture drift"],
        evidence_bindings=evidence,
        occurred_at=NOW,
    )

    with pytest.raises(ReflectionValidationError, match="reused"):
        session.promote_attribution(
            state="correlational",
            hypothesis="schema drift caused the failure",
            falsifier="a schema-only correction does not remove the failure",
            confounders=["fixture drift"],
            evidence_bindings=evidence,
            occurred_at=NOW,
        )


def test_controlled_and_intervention_attribution_are_reachable_via_distinct_events() -> None:
    contract = contract_example()
    session, changed = prepare_revalidating_session(contract)
    hypothesis = "schema drift caused the failure"
    falsifier = "a schema-only correction does not remove the failure"
    confounders = ["fixture drift"]
    session.record_attribution_hypothesis(
        hypothesis=hypothesis,
        falsifier=falsifier,
        confounders=confounders,
        evidence_bindings=[binding("observation-evidence", HASH_A)],
        occurred_at=NOW,
    )
    session.promote_attribution(
        state="correlational",
        hypothesis=hypothesis,
        falsifier=falsifier,
        confounders=confounders,
        evidence_bindings=[binding("correlation-evidence", HASH_B)],
        occurred_at=NOW,
    )
    session.promote_attribution(
        state="controlled_replay",
        hypothesis=hypothesis,
        falsifier=falsifier,
        confounders=confounders,
        evidence_bindings=[binding("controlled-replay-evidence", HASH_C)],
        occurred_at=NOW,
    )
    session.promote_attribution(
        state="intervention_verified",
        hypothesis=hypothesis,
        falsifier=falsifier,
        confounders=confounders,
        evidence_bindings=[binding("intervention-evidence", HASH_D)],
        occurred_at=NOW,
    )
    observation = session.close_round(
        outcome="accepted",
        validation=passing_validation(changed),
        improvement_state="verified_improvement",
        attribution=None,
        occurred_at=NOW,
        stop_reason="controlled intervention verified",
    )

    assert observation["attribution"]["state"] == "intervention_verified"
    assert len(observation["attribution"]["evidence_bindings"]) == 4
    validate_reflection_event_stream(session.events, contract=contract)


def test_multi_round_subject_and_signal_state_do_not_reset_or_reuse() -> None:
    contract = contract_example()
    session, changed = prepare_revalidating_session(contract)
    session.close_round(
        outcome="continue",
        validation=passing_validation(changed),
        improvement_state="verified_improvement",
        attribution=None,
        occurred_at=NOW,
    )

    with pytest.raises(ReflectionValidationError, match="consumed"):
        session.start_round(
            round_id="round-reused-signal",
            new_signal=qualified_signal(),
            occurred_at=NOW,
        )

    signal_two = qualified_signal()
    signal_two["evidence_bindings"] = [binding("fresh-test-result-2", HASH_A)]
    started = session.start_round(
        round_id="round-2",
        new_signal=signal_two,
        occurred_at=NOW,
    )
    assert started["subject_binding"] == changed
    session.propose_change(
        target="artifact",
        proposal_binding=binding("patch-2", HASH_C),
        occurred_at=NOW,
    )
    session.authorize_change(
        authorization_binding=binding("change-authorizer", HASH_D),
        occurred_at=NOW,
    )

    with pytest.raises(ReflectionValidationError, match="never-reused"):
        session.record_change_applied(
            subject_after_binding=binding("artifact-1", HASH_A),
            occurred_at=NOW,
        )


def test_nonadmitted_closure_obeys_contract_terminal_outcomes() -> None:
    contract = contract_example(
        eligibility="needs_evidence",
        route="evidence_collection",
        terminal_outcomes=["rejected"],
    )
    session = ReflectionSession(contract)
    session.start(occurred_at=NOW)

    with pytest.raises(ReflectionAuthorizationError, match="outside"):
        session.close_without_round(
            outcome="handed_off",
            reason="not authorized by this contract",
            occurred_at=NOW,
        )

    session.close_without_round(
        outcome="rejected",
        reason="the sealed contract permits rejection",
        occurred_at=NOW,
    )


def test_validator_authorizers_must_be_distinct_at_contract_seal_time() -> None:
    contract = contract_example(validator_change=True)
    forged = deepcopy(contract)
    forged["validation_policy"]["validator_change_authorizer_binding"] = deepcopy(
        forged["change_policy"]["authorizer_binding"]
    )
    forged["contract_hash"] = artifact_fingerprint(forged, "contract_hash")

    with pytest.raises(ReflectionValidationError, match="distinct"):
        ReflectionSession(forged)


def test_validator_change_requires_approved_rebased_baseline_evidence() -> None:
    contract = contract_example(validator_change=True)
    session, changed = prepare_revalidating_session(contract)
    validation = passing_validation(changed)
    rebase_content = {
        "subject_before_binding": binding("artifact-1", HASH_A),
        "criteria_binding": binding("acceptance-criteria", HASH_B),
        "environment_binding": binding("fixture", HASH_A),
        "validator_bindings": [
            binding("validator-main", HASH_B),
            binding("validator-regression", HASH_C),
        ],
        "regression_scope_bindings": [binding("passing-suite", HASH_D)],
        "metric_id": "target-pass-rate",
        "metric_value": 0.7,
        "approval_binding": binding("validator-authorizer", HASH_C),
        "evidence_bindings": [binding("rebase-replay", HASH_A)],
    }
    validation["comparison_state"] = "independently_rebased"
    validation["rebased_baseline"] = {
        "baseline_binding": {
            "id": "rebase-1",
            "version": "1.0.0",
            "hash": artifact_fingerprint(rebase_content),
        },
        **rebase_content,
    }
    observation = session.close_round(
        outcome="accepted",
        validation=validation,
        improvement_state="verified_improvement",
        attribution=None,
        occurred_at=NOW,
        stop_reason="independent rebase verified",
    )
    assert observation["validation"]["comparison_state"] == "independently_rebased"

    forged = deepcopy(observation)
    forged["validation"]["rebased_baseline"]["approval_binding"] = binding(
        "unapproved-rebase",
        HASH_D,
    )
    forged["observation_hash"] = artifact_fingerprint(forged, "observation_hash")
    with pytest.raises(ReflectionValidationError, match="hash|authorizer"):
        validate_reflection_round_observation(
            forged,
            contract=contract,
            events=session.events,
        )


def test_learning_promotion_is_a_producible_separately_authorized_event() -> None:
    contract = contract_example(learning_enabled=True)
    session, changed = prepare_revalidating_session(contract)
    learning_candidate = {
        "target": "skill",
        "candidate_binding": binding("skill-candidate", HASH_C),
        "source_round_id": "round-1",
        "source_subject_binding": changed,
        "round_evidence_bindings": [binding("revalidation-report", HASH_D)],
        "decision": "promoted",
        "promotion_evidence_bindings": [binding("promotion-evidence", HASH_D)],
        "authorization_binding": binding("learning-authorizer", HASH_A),
        "owner_binding": binding("learning-owner", HASH_B),
    }
    observation = session.close_round(
        outcome="accepted",
        validation=passing_validation(changed),
        improvement_state="verified_improvement",
        attribution=None,
        learning_candidate=learning_candidate,
        occurred_at=NOW,
        stop_reason="learning promotion separately authorized",
    )

    assert observation["learning_candidate"] == learning_candidate
    learning_events = [
        event
        for event in session.events
        if event["event_type"] == "learning_promotion_evaluated"
    ]
    assert len(learning_events) == 1
    assert learning_events[0]["payload"]["learning_candidate"] == learning_candidate


def test_rolled_back_outcome_requires_applied_and_verified_recovery_events() -> None:
    contract = contract_example()
    session, changed = prepare_revalidating_session(contract)
    failed = passing_validation(changed)
    failed.update(
        {
            "status": "failed",
            "mandatory_pass": False,
            "regression_pass": False,
            "result_value": 0.6,
            "improvement_delta": -0.1,
            "threshold_met": False,
            "result_progress": False,
        }
    )

    with pytest.raises(ReflectionStateError, match="record_rollback"):
        session.close_round(
            outcome="rolled_back",
            validation=failed,
            improvement_state="regression",
            attribution=None,
            occurred_at=NOW,
            stop_reason="text is not a rollback",
        )

    recovery_events = session.record_rollback(
        restored_subject_binding=binding("artifact-1", HASH_A),
        apply_evidence_bindings=[binding("rollback-apply-receipt", HASH_B)],
        validator_bindings=[
            binding("validator-main", HASH_B),
            binding("validator-regression", HASH_C),
        ],
        verification_evidence_bindings=[
            binding("rollback-verification-report", HASH_C)
        ],
        failed_validation=failed,
        occurred_at=NOW,
    )
    assert [event["event_type"] for event in recovery_events] == [
        "revalidation_finished",
        "rollback_started",
        "rollback_applied",
        "rollback_verified",
    ]
    observation = session.close_round(
        outcome="rolled_back",
        validation=failed,
        improvement_state="regression",
        attribution=None,
        occurred_at=NOW,
        stop_reason="baseline restored and independently verified",
    )
    assert observation["subject_after_binding"] == binding("artifact-1", HASH_A)
    assert observation["rollback"]["failed_subject_binding"] == changed
    assert observation["rollback"]["verified"] is True
    validate_reflection_event_stream(session.events, contract=contract)


def test_record_rollback_rejects_invalid_validation_atomically() -> None:
    contract = contract_example()
    session, changed = prepare_revalidating_session(contract)
    invalid = passing_validation(changed)
    invalid.update(
        {
            "status": "failed",
            "mandatory_pass": False,
            "regression_pass": False,
            "result_value": 0.6,
            "improvement_delta": 999,
            "threshold_met": False,
            "result_progress": False,
        }
    )
    before_events = session.events

    with pytest.raises(ReflectionValidationError, match="delta"):
        session.record_rollback(
            restored_subject_binding=binding("artifact-1", HASH_A),
            apply_evidence_bindings=[binding("rollback-apply-receipt", HASH_B)],
            validator_bindings=[
                binding("validator-main", HASH_B),
                binding("validator-regression", HASH_C),
            ],
            verification_evidence_bindings=[
                binding("rollback-verification-report", HASH_C)
            ],
            failed_validation=invalid,
            occurred_at=NOW,
        )

    assert session.state is ReflectionState.REVALIDATING
    assert session.events == before_events


def test_event_stream_validator_enforces_contract_authority_and_validators() -> None:
    contract = contract_example()
    session, changed = prepare_revalidating_session(contract)
    session.close_round(
        outcome="accepted",
        validation=passing_validation(changed),
        improvement_state="verified_improvement",
        attribution=None,
        occurred_at=NOW,
        stop_reason="valid closure",
    )
    forged = [deepcopy(event) for event in session.events]
    attacker = binding("attacker-validator", HASH_A)
    for event in forged:
        if event["event_type"] == "change_proposed":
            event["payload"]["target"] = "validator"
        elif event["event_type"] == "change_authorized":
            event["payload"]["authorization_binding"] = binding(
                "intruder",
                HASH_B,
            )
        elif event["event_type"] in {
            "revalidation_started",
            "revalidation_finished",
        }:
            event["payload"]["validator_bindings"] = [attacker]
        event["event_hash"] = artifact_fingerprint(event, "event_hash")

    with pytest.raises(ReflectionValidationError, match="contract|forbidden|validator"):
        validate_reflection_event_stream(forged, contract=contract)


def test_strong_attribution_requires_contract_authority_and_passed_validation() -> None:
    contract = contract_example()
    session, changed = prepare_revalidating_session(contract)
    hypothesis = "schema drift caused the failure"
    falsifier = "a schema-only correction does not remove the failure"
    confounders = ["fixture drift"]
    with pytest.raises(ReflectionAuthorizationError, match="outside"):
        session.record_attribution_hypothesis(
            hypothesis=hypothesis,
            falsifier=falsifier,
            confounders=confounders,
            evidence_bindings=[binding("observation-evidence", HASH_A)],
            evidence_authority_binding=binding("self-asserted-authority", HASH_D),
            occurred_at=NOW,
        )

    session.record_attribution_hypothesis(
        hypothesis=hypothesis,
        falsifier=falsifier,
        confounders=confounders,
        evidence_bindings=[binding("observation-evidence", HASH_A)],
        occurred_at=NOW,
    )
    session.promote_attribution(
        state="correlational",
        hypothesis=hypothesis,
        falsifier=falsifier,
        confounders=confounders,
        evidence_bindings=[binding("correlation-evidence", HASH_B)],
        occurred_at=NOW,
    )
    session.promote_attribution(
        state="controlled_replay",
        hypothesis=hypothesis,
        falsifier=falsifier,
        confounders=confounders,
        evidence_bindings=[binding("controlled-replay-evidence", HASH_C)],
        occurred_at=NOW,
    )
    session.promote_attribution(
        state="intervention_verified",
        hypothesis=hypothesis,
        falsifier=falsifier,
        confounders=confounders,
        evidence_bindings=[binding("intervention-evidence", HASH_D)],
        occurred_at=NOW,
    )
    unknown = passing_validation(changed)
    unknown.update(
        {
            "status": "unknown",
            "mandatory_pass": None,
            "regression_pass": None,
            "metric_id": None,
            "baseline_value": None,
            "result_value": None,
            "improvement_delta": None,
            "threshold_met": None,
            "comparison_state": "not_comparable",
            "result_progress": False,
        }
    )

    with pytest.raises(ReflectionValidationError, match="controlled attribution|strong attribution"):
        session.close_round(
            outcome="handed_off",
            validation=unknown,
            improvement_state="not_evaluated",
            attribution=None,
            occurred_at=NOW,
            stop_reason="strong attribution cannot survive unknown validation",
        )
