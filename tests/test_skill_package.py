"""Executable tests for governed Skill Package engineering / 受治理技能包工程可执行测试。"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "harness-engineering-patterns"
SCHEMA_DIR = SKILL_DIR / "schemas"
RUNTIME_DIR = SKILL_DIR / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

import reflection_runtime  # noqa: E402
from reasoning_artifacts import build_artifact  # noqa: E402
from skill_package import (  # noqa: E402
    SKILL_PACKAGE_REQUIRED_DIMENSIONS,
    SKILL_PACKAGE_REQUIRED_SECTIONS,
    SkillPackageAuthorizationError,
    SkillPackageReleaseError,
    SkillPackageSession,
    SkillPackageStage,
    SkillPackageStateError,
    SkillPackageValidationError,
    SkillQualificationState,
    SkillReleaseState,
    build_capability_credential,
    build_skill_lifecycle_reflection_guard,
    build_skill_package_alias_receipt,
    build_skill_package_candidate,
    build_skill_package_contract,
    build_skill_package_evaluation,
    build_skill_package_manifest,
    build_skill_package_reuse_receipt,
    candidate_binding,
    credential_binding,
    evaluation_binding,
    manifest_binding,
    validate_skill_package_event_stream,
)


HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
HASH_C = "sha256:" + "c" * 64
HASH_D = "sha256:" + "d" * 64
HASH_E = "sha256:" + "e" * 64
HASH_F = "sha256:" + "f" * 64
T0 = "2026-08-18T08:00:00Z"


def binding(
    identifier: str,
    digest: str = HASH_A,
    *,
    version: str = "1.0.0",
) -> dict[str, str]:
    return {"id": identifier, "version": version, "hash": digest}


def contract_binding(contract: dict[str, object]) -> dict[str, str]:
    return {
        "id": str(contract["contract_id"]),
        "version": str(contract["contract_version"]),
        "hash": str(contract["contract_hash"]),
    }


def contract_example() -> dict[str, object]:
    return build_skill_package_contract(
        {
            "schema_version": "1.0.0",
            "contract_id": "skill-lifecycle-contract-1",
            "contract_version": "1.0.0",
            "lifecycle_id": "skill-lifecycle-1",
            "reflection_contract_binding": binding("reflection-contract", HASH_B),
            "target": {
                "skill_id": "triage-skill",
                "skill_version": "1.0.0",
                "route_alias": "triage/current",
            },
            "roles": {
                "nominator_binding": binding("nominator", HASH_A),
                "packager_binding": binding("packager", HASH_B),
                "verifier_binding": binding("independent-verifier", HASH_C),
                "credential_issuer_binding": binding("credential-issuer", HASH_D),
                "publisher_binding": binding("publisher", HASH_E),
                "lifecycle_owner_binding": binding("lifecycle-owner", HASH_F),
            },
            "recurrence_policy": {
                "minimum_distinct_runs": 2,
                "minimum_verified_contributions": 2,
                "minimum_distinct_environments": 2,
                "require_external_success": True,
                "require_same_problem_class": True,
                "require_same_solution_signature": True,
            },
            "package_policy": {
                "immutable_versions": True,
                "require_bilingual_core": True,
                "required_core_sections": list(SKILL_PACKAGE_REQUIRED_SECTIONS),
                "require_parameter_origin_binding": True,
                "require_supply_chain_inventory": True,
            },
            "verification_policy": {
                "required_dimensions": list(SKILL_PACKAGE_REQUIRED_DIMENSIONS),
                "minimum_cases_per_dimension": 2,
                "require_failure_path": True,
                "require_counterexample": True,
                "allow_partial_pass": False,
            },
            "release_policy": {
                "required_stages": ["shadow", "limited", "production"],
                "maximum_limited_traffic_fraction": 0.25,
                "require_valid_credential": True,
                "require_exact_manifest_digest": True,
                "require_atomic_alias_switch": True,
                "require_prewithdrawal_on_reverification": True,
            },
            "reuse_policy": {
                "require_real_router_selection": True,
                "require_external_outcome": True,
                "require_attribution_state": True,
                "minimum_observations_before_rate_decision": 5,
                "maximum_outcome_lag_seconds": 3600,
            },
            "governance_policy_binding": binding("skill-governance", HASH_F),
            "created_at": T0,
        }
    )


def candidate_example(contract: dict[str, object]) -> dict[str, object]:
    target = contract["target"]
    signature = HASH_E
    occurrences = []
    for index, digest in enumerate((HASH_A, HASH_B), start=1):
        occurrences.append(
            {
                "run_binding": binding(f"source-run-{index}", digest),
                "environment_binding": binding(f"source-env-{index}", digest),
                "problem_class": "recurrent-triage-gap",
                "solution_signature": signature,
                "external_outcome_binding": binding(f"source-outcome-{index}", digest),
                "outcome_status": "success",
                "contribution_state": "verified_contribution",
                "observed_at": f"2026-08-18T07:0{index}:00Z",
            }
        )
    return build_skill_package_candidate(
        {
            "schema_version": "1.0.0",
            "candidate_id": "skill-candidate-1",
            "candidate_version": "1.0.0",
            "reflection_candidate_binding": binding("reflection-skill-candidate", HASH_C),
            "skill_id": target["skill_id"],
            "proposed_skill_version": target["skill_version"],
            "problem_class": "recurrent-triage-gap",
            "solution_signature": signature,
            "occurrences": occurrences,
            "nomination_evidence_bindings": [
                binding("recurrence-analysis", HASH_D),
                binding("contribution-analysis", HASH_E),
            ],
            "nominator_binding": deepcopy(contract["roles"]["nominator_binding"]),
            "created_at": T0,
        }
    )


def reflection_assurance(
    stage: str, request: dict[str, object]
) -> dict[str, str]:
    assert stage == "candidate_nomination"
    assert request["candidate"]["candidate_id"] == "skill-candidate-1"
    return binding("reflection-skill-assurance", HASH_D)


def distillation_example() -> dict[str, object]:
    return {
        "distillation_binding": binding("distillation-1", HASH_B),
        "stable_step_ids": ["inspect", "classify", "route", "verify"],
        "parameter_names": ["risk_threshold"],
        "hidden_assumptions": ["input schema remains versioned"],
        "boundary_evidence_bindings": [binding("boundary-replay", HASH_C)],
    }


def manifest_example(
    contract: dict[str, object],
    candidate: dict[str, object],
) -> dict[str, object]:
    package_content = binding("triage-skill-package", HASH_E)
    core_sections = [
        {
            "section": section,
            "content_binding": binding(f"skill-core/{section}", HASH_E),
            "bilingual_verification_binding": binding(
                f"bilingual-check/{section}", HASH_D
            ),
        }
        for section in SKILL_PACKAGE_REQUIRED_SECTIONS
    ]
    tool = binding("readonly-triage-tool", HASH_A)
    return build_skill_package_manifest(
        {
            "schema_version": "1.0.0",
            "package_id": "triage-skill-package",
            "package_content_binding": package_content,
            "skill_id": contract["target"]["skill_id"],
            "skill_version": contract["target"]["skill_version"],
            "qualification_state": "TRIAL",
            "candidate_binding": candidate_binding(candidate),
            "reflection_assurance_binding": binding(
                "reflection-skill-assurance", HASH_D
            ),
            "distillation_binding": binding("distillation-1", HASH_B),
            "core_sections": core_sections,
            "discovery": {
                "name_en": "Recurrent Triage Skill",
                "name_zh": "重复分诊技能",
                "description_en": "Classify and route a bounded recurrent triage gap.",
                "description_zh": "对有界的重复分诊缺口进行分类与路由。",
                "use_cases_en": ["Repeated triage gap with evidence."],
                "use_cases_zh": ["具有证据的重复分诊缺口。"],
                "non_use_cases_en": ["One-off or unbounded incidents."],
                "non_use_cases_zh": ["一次性或无界事故。"],
                "trigger_examples": ["triage-gap:v1"],
            },
            "contracts": {
                "input_schema_binding": binding("skill-input-schema", HASH_A),
                "output_schema_binding": binding("skill-output-schema", HASH_B),
                "failure_contract_binding": binding("skill-failure-contract", HASH_C),
                "verification_entrypoint_binding": binding("skill-verification", HASH_D),
            },
            "parameterization": {
                "parameter_names": ["risk_threshold"],
                "parameter_origin_bindings": [binding("risk-threshold-origin", HASH_A)],
                "unresolved_assumptions": ["policy remains compatible"],
                "boundary_evidence_bindings": [binding("boundary-replay", HASH_C)],
                "instance_constants_removed": True,
            },
            "execution": {
                "step_refs": ["inspect", "classify", "route", "verify"],
                "tool_contract_bindings": [tool],
                "permission_scopes": ["triage:read"],
                "side_effect_class": "readonly",
                "rollback_binding": None,
            },
            "resources": [
                {
                    "path": "SKILL.md",
                    "kind": "reference",
                    "digest": package_content["hash"],
                    "trust_state": "reviewed",
                },
                {
                    "path": "scripts/check.py",
                    "kind": "script",
                    "digest": HASH_F,
                    "trust_state": "reviewed",
                },
            ],
            "dependencies": {
                "runtime_bindings": [binding("python-runtime", HASH_B)],
                "tool_contract_bindings": [tool],
                "policy_bindings": [binding("skill-governance", HASH_F)],
                "environment_constraints": ["python>=3.12"],
            },
            "source": {
                "source_type": "distilled_trace",
                "source_run_bindings": [
                    deepcopy(item["run_binding"]) for item in candidate["occurrences"]
                ],
                "trust_state": "reviewed",
                "provenance_evidence_bindings": [
                    binding("recurrence-analysis", HASH_D)
                ],
            },
            "governance_policy_binding": deepcopy(
                contract["governance_policy_binding"]
            ),
            "created_at": "2026-08-18T08:02:00Z",
        }
    )


def evaluation_example(
    contract: dict[str, object],
    manifest: dict[str, object],
    *,
    identifier: str = "skill-evaluation-1",
    version: str = "1.0.0",
    started_at: str = "2026-08-18T08:04:00Z",
    completed_at: str = "2026-08-18T08:05:00Z",
    suite: dict[str, str] | None = None,
) -> dict[str, object]:
    dimensions = [
        {
            "dimension": dimension,
            "total_cases": 2,
            "passed_cases": 2,
            "status": "passed",
            "counterexample_checked": True,
            "failure_path_checked": True,
            "evidence_bindings": [binding(f"evidence-{dimension}", HASH_C)],
        }
        for dimension in SKILL_PACKAGE_REQUIRED_DIMENSIONS
    ]
    return build_skill_package_evaluation(
        {
            "schema_version": "1.0.0",
            "evaluation_id": identifier,
            "evaluation_version": version,
            "contract_binding": contract_binding(contract),
            "manifest_binding": manifest_binding(manifest),
            "evaluation_suite_binding": suite
            or binding("skill-evaluation-suite", HASH_B),
            "environment_binding": binding("verification-environment", HASH_C),
            "evaluator_binding": deepcopy(contract["roles"]["verifier_binding"]),
            "validator_configuration_binding": binding("validator-config", HASH_D),
            "independent_from_candidate_producers": True,
            "dimensions": dimensions,
            "regression_free": True,
            "validator_gaming_detected": False,
            "overall_status": "passed",
            "started_at": started_at,
            "completed_at": completed_at,
        }
    )


def credential_example(
    contract: dict[str, object],
    manifest: dict[str, object],
    evaluation: dict[str, object],
    *,
    identifier: str = "skill-credential-1",
    version: str = "1.0.0",
    supersedes: dict[str, str] | None = None,
    issued_at: str = "2026-08-18T08:06:00Z",
    expires_at: str = "2026-08-19T08:06:00Z",
) -> dict[str, object]:
    return build_capability_credential(
        {
            "schema_version": "1.0.0",
            "credential_id": identifier,
            "credential_version": version,
            "contract_binding": contract_binding(contract),
            "manifest_binding": manifest_binding(manifest),
            "evaluation_binding": evaluation_binding(evaluation),
            "issuer_binding": deepcopy(
                contract["roles"]["credential_issuer_binding"]
            ),
            "policy_binding": deepcopy(contract["governance_policy_binding"]),
            "tool_contract_bindings": deepcopy(
                manifest["dependencies"]["tool_contract_bindings"]
            ),
            "runtime_bindings": deepcopy(
                manifest["dependencies"]["runtime_bindings"]
            ),
            "environment_binding": deepcopy(evaluation["environment_binding"]),
            "permission_scopes": deepcopy(manifest["execution"]["permission_scopes"]),
            "status": "issued",
            "supersedes_credential_binding": supersedes,
            "issued_at": issued_at,
            "expires_at": expires_at,
            "evidence_bindings": [binding(f"{identifier}-evidence", HASH_E)],
        }
    )


def trial_session() -> tuple[
    SkillPackageSession,
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    contract = contract_example()
    candidate = candidate_example(contract)
    manifest = manifest_example(contract, candidate)
    session = SkillPackageSession(contract, reflection_guard=reflection_assurance)
    session.nominate_candidate(
        candidate,
        actor_binding=contract["roles"]["nominator_binding"],
        occurred_at="2026-08-18T08:01:00Z",
    )
    session.record_distillation(
        distillation_example(),
        actor_binding=contract["roles"]["packager_binding"],
        occurred_at="2026-08-18T08:02:00Z",
    )
    session.register_trial(
        manifest,
        actor_binding=contract["roles"]["packager_binding"],
        occurred_at="2026-08-18T08:03:00Z",
    )
    return session, contract, candidate, manifest


def production_session() -> tuple[
    SkillPackageSession,
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    session, contract, _, manifest = trial_session()
    session.start_verification(
        evaluation_suite_binding=binding("skill-evaluation-suite", HASH_B),
        environment_binding=binding("verification-environment", HASH_C),
        actor_binding=contract["roles"]["verifier_binding"],
        occurred_at="2026-08-18T08:04:00Z",
    )
    evaluation = evaluation_example(contract, manifest)
    session.complete_verification(
        evaluation,
        actor_binding=contract["roles"]["verifier_binding"],
        occurred_at="2026-08-18T08:05:00Z",
    )
    credential = credential_example(contract, manifest, evaluation)
    session.issue_credential(
        credential,
        actor_binding=contract["roles"]["credential_issuer_binding"],
        occurred_at="2026-08-18T08:06:00Z",
    )
    session.promote_verified(
        actor_binding=contract["roles"]["lifecycle_owner_binding"],
        occurred_at="2026-08-18T08:07:00Z",
    )
    session.advance_release_stage(
        "shadow",
        traffic_fraction=0,
        evidence_bindings=[binding("shadow-evidence", HASH_A)],
        actor_binding=contract["roles"]["publisher_binding"],
        occurred_at="2026-08-18T08:08:00Z",
    )
    session.advance_release_stage(
        "limited",
        traffic_fraction=0.1,
        evidence_bindings=[binding("limited-evidence", HASH_B)],
        actor_binding=contract["roles"]["publisher_binding"],
        occurred_at="2026-08-18T08:09:00Z",
    )
    alias = build_skill_package_alias_receipt(
        {
            "schema_version": "1.0.0",
            "alias_event_id": "alias-switch-1",
            "alias": contract["target"]["route_alias"],
            "previous_manifest_binding": None,
            "next_manifest_binding": manifest_binding(manifest),
            "credential_binding": credential_binding(credential),
            "publisher_binding": deepcopy(contract["roles"]["publisher_binding"]),
            "expected_revision": 0,
            "new_revision": 1,
            "compare_and_swap_succeeded": True,
            "traffic_fraction": 1,
            "evidence_bindings": [binding("alias-cas-evidence", HASH_C)],
            "switched_at": "2026-08-18T08:10:00Z",
        }
    )
    session.switch_route_alias(
        alias,
        actor_binding=contract["roles"]["publisher_binding"],
        occurred_at="2026-08-18T08:10:00Z",
    )
    return session, contract, manifest, credential


def reuse_example(
    manifest: dict[str, object],
    credential: dict[str, object],
    *,
    identifier: str = "skill-reuse-1",
    route_selected_at: str = "2026-08-18T08:10:10Z",
    run_completed_at: str = "2026-08-18T08:10:30Z",
    observed_at: str = "2026-08-18T08:11:00Z",
) -> dict[str, object]:
    return build_skill_package_reuse_receipt(
        {
            "schema_version": "1.0.0",
            "reuse_id": identifier,
            "run_binding": binding(f"{identifier}-run", HASH_A),
            "route_decision_binding": binding(f"{identifier}-route", HASH_B),
            "manifest_binding": manifest_binding(manifest),
            "credential_binding": credential_binding(credential),
            "release_stage": "production",
            "router_selected": True,
            "test_run": False,
            "shadow_run": False,
            "external_outcome": {
                "status": "success",
                "binding": binding(f"{identifier}-outcome", HASH_C),
            },
            "attribution_status": "skill_logic",
            "evidence_bindings": [binding(f"{identifier}-evidence", HASH_D)],
            "route_selected_at": route_selected_at,
            "run_completed_at": run_completed_at,
            "observed_at": observed_at,
        }
    )


@pytest.mark.parametrize(
    "name",
    (
        "skill-package-contract",
        "skill-package-candidate",
        "skill-package-manifest",
        "skill-package-evaluation",
        "capability-credential",
        "skill-package-alias-receipt",
        "skill-package-reuse-receipt",
        "skill-package-event",
    ),
)
def test_skill_package_schemas_are_2020_12_and_bilingual(name: str) -> None:
    schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["x-contract-version"] == "1.0.0"
    assert "/" in schema["title"] and "/" in schema["description"]
    assert any("\u4e00" <= char <= "\u9fff" for char in schema["description"])


def test_end_to_end_trial_verified_staged_release_and_real_reuse() -> None:
    session, contract, manifest, credential = production_session()
    receipt = reuse_example(manifest, credential)
    event = session.record_reuse(
        receipt,
        actor_binding=contract["roles"]["lifecycle_owner_binding"],
        occurred_at=receipt["observed_at"],
    )

    assert event["event_type"] == "skill.reuse_recorded"
    assert session.stage is SkillPackageStage.PRODUCTION
    assert session.qualification_state is SkillQualificationState.VERIFIED
    assert session.release_state is SkillReleaseState.PRODUCTION
    assert len(session.reuse_receipts) == 1
    assert [item["sequence"] for item in session.events] == list(
        range(1, len(session.events) + 1)
    )
    validate_skill_package_event_stream(session.events, contract=contract)


def test_recurrence_and_authority_collapse_fail_closed() -> None:
    contract = contract_example()
    candidate = candidate_example(contract)
    duplicate = deepcopy(candidate)
    duplicate.pop("candidate_hash")
    duplicate["occurrences"][1]["run_binding"] = deepcopy(
        duplicate["occurrences"][0]["run_binding"]
    )
    with pytest.raises(SkillPackageValidationError, match="distinct runs"):
        build_skill_package_candidate(duplicate)

    collapsed = deepcopy(contract)
    collapsed.pop("contract_hash")
    collapsed["roles"]["verifier_binding"] = deepcopy(
        collapsed["roles"]["packager_binding"]
    )
    with pytest.raises(SkillPackageValidationError, match="verifier must be independent"):
        build_skill_package_contract(collapsed)


def test_manifest_requires_exact_core_sections_and_skill_content_binding() -> None:
    contract = contract_example()
    candidate = candidate_example(contract)
    manifest = manifest_example(contract, candidate)
    forged = deepcopy(manifest)
    forged.pop("manifest_hash")
    forged["core_sections"][-1]["section"] = "metadata"
    with pytest.raises(SkillPackageValidationError, match="core section"):
        build_skill_package_manifest(forged)

    forged = deepcopy(manifest)
    forged.pop("manifest_hash")
    forged["resources"][0]["digest"] = HASH_A
    with pytest.raises(SkillPackageValidationError, match="SKILL.md digest"):
        build_skill_package_manifest(forged)


def test_verification_requires_all_dimensions_and_started_suite() -> None:
    session, contract, _, manifest = trial_session()
    session.start_verification(
        evaluation_suite_binding=binding("skill-evaluation-suite", HASH_B),
        environment_binding=binding("verification-environment", HASH_C),
        actor_binding=contract["roles"]["verifier_binding"],
        occurred_at="2026-08-18T08:04:00Z",
    )
    incomplete = evaluation_example(contract, manifest)
    incomplete = deepcopy(incomplete)
    incomplete.pop("evaluation_hash")
    incomplete["dimensions"].pop()
    incomplete = build_skill_package_evaluation(incomplete)
    with pytest.raises(SkillPackageValidationError, match="exact five dimensions"):
        session.complete_verification(
            incomplete,
            actor_binding=contract["roles"]["verifier_binding"],
            occurred_at="2026-08-18T08:05:00Z",
        )

    mismatch = evaluation_example(
        contract,
        manifest,
        identifier="skill-evaluation-mismatch",
        suite=binding("different-suite", HASH_A),
    )
    with pytest.raises(SkillPackageValidationError, match="started verification"):
        session.complete_verification(
            mismatch,
            actor_binding=contract["roles"]["verifier_binding"],
            occurred_at="2026-08-18T08:05:00Z",
        )


def test_credential_binds_runtime_and_alias_rejects_wrong_version() -> None:
    session, contract, _, manifest = trial_session()
    session.start_verification(
        evaluation_suite_binding=binding("skill-evaluation-suite", HASH_B),
        environment_binding=binding("verification-environment", HASH_C),
        actor_binding=contract["roles"]["verifier_binding"],
        occurred_at="2026-08-18T08:04:00Z",
    )
    evaluation = evaluation_example(contract, manifest)
    session.complete_verification(
        evaluation,
        actor_binding=contract["roles"]["verifier_binding"],
        occurred_at="2026-08-18T08:05:00Z",
    )
    credential = credential_example(contract, manifest, evaluation)
    forged = deepcopy(credential)
    forged.pop("credential_hash")
    forged["runtime_bindings"] = [binding("different-runtime", HASH_A)]
    forged = build_capability_credential(forged)
    with pytest.raises(SkillPackageValidationError, match="runtime scope"):
        session.issue_credential(
            forged,
            actor_binding=contract["roles"]["credential_issuer_binding"],
            occurred_at="2026-08-18T08:06:00Z",
        )

    session.issue_credential(
        credential,
        actor_binding=contract["roles"]["credential_issuer_binding"],
        occurred_at="2026-08-18T08:06:00Z",
    )
    session.promote_verified(
        actor_binding=contract["roles"]["lifecycle_owner_binding"],
        occurred_at="2026-08-18T08:07:00Z",
    )
    session.advance_release_stage(
        "shadow",
        traffic_fraction=0,
        evidence_bindings=[binding("shadow-evidence", HASH_A)],
        actor_binding=contract["roles"]["publisher_binding"],
        occurred_at="2026-08-18T08:08:00Z",
    )
    session.advance_release_stage(
        "limited",
        traffic_fraction=0.1,
        evidence_bindings=[binding("limited-evidence", HASH_B)],
        actor_binding=contract["roles"]["publisher_binding"],
        occurred_at="2026-08-18T08:09:00Z",
    )
    wrong_manifest = manifest_binding(manifest)
    wrong_manifest["version"] = "9.9.9"
    alias = build_skill_package_alias_receipt(
        {
            "schema_version": "1.0.0",
            "alias_event_id": "alias-switch-wrong-version",
            "alias": contract["target"]["route_alias"],
            "previous_manifest_binding": None,
            "next_manifest_binding": wrong_manifest,
            "credential_binding": credential_binding(credential),
            "publisher_binding": deepcopy(contract["roles"]["publisher_binding"]),
            "expected_revision": 0,
            "new_revision": 1,
            "compare_and_swap_succeeded": True,
            "traffic_fraction": 1,
            "evidence_bindings": [binding("alias-cas-evidence", HASH_C)],
            "switched_at": "2026-08-18T08:10:00Z",
        }
    )
    with pytest.raises(SkillPackageValidationError, match="different manifest"):
        session.switch_route_alias(
            alias,
            actor_binding=contract["roles"]["publisher_binding"],
            occurred_at="2026-08-18T08:10:00Z",
        )


def test_expired_credential_cannot_promote_or_release() -> None:
    session, contract, _, manifest = trial_session()
    session.start_verification(
        evaluation_suite_binding=binding("skill-evaluation-suite", HASH_B),
        environment_binding=binding("verification-environment", HASH_C),
        actor_binding=contract["roles"]["verifier_binding"],
        occurred_at="2026-08-18T08:04:00Z",
    )
    evaluation = evaluation_example(contract, manifest)
    session.complete_verification(
        evaluation,
        actor_binding=contract["roles"]["verifier_binding"],
        occurred_at="2026-08-18T08:05:00Z",
    )
    credential = credential_example(
        contract,
        manifest,
        evaluation,
        expires_at="2026-08-18T08:06:30Z",
    )
    session.issue_credential(
        credential,
        actor_binding=contract["roles"]["credential_issuer_binding"],
        occurred_at="2026-08-18T08:06:00Z",
    )
    with pytest.raises(SkillPackageAuthorizationError, match="expired"):
        session.promote_verified(
            actor_binding=contract["roles"]["lifecycle_owner_binding"],
            occurred_at="2026-08-18T08:07:00Z",
        )


def test_real_reuse_rejects_pre_alias_and_excessive_outcome_lag() -> None:
    session, contract, manifest, credential = production_session()
    pre_alias = reuse_example(
        manifest,
        credential,
        identifier="pre-alias-reuse",
        route_selected_at="2026-08-18T08:09:59Z",
    )
    with pytest.raises(SkillPackageReleaseError, match="predates"):
        session.record_reuse(
            pre_alias,
            actor_binding=contract["roles"]["lifecycle_owner_binding"],
            occurred_at=pre_alias["observed_at"],
        )

    late = reuse_example(
        manifest,
        credential,
        identifier="late-outcome-reuse",
        route_selected_at="2026-08-18T08:10:10Z",
        run_completed_at="2026-08-18T08:10:20Z",
        observed_at="2026-08-18T09:10:21Z",
    )
    with pytest.raises(SkillPackageValidationError, match="outcome-lag"):
        session.record_reuse(
            late,
            actor_binding=contract["roles"]["lifecycle_owner_binding"],
            occurred_at=late["observed_at"],
        )


def test_reverification_withdraws_before_testing_and_requires_supersession() -> None:
    session, contract, manifest, old_credential = production_session()
    events = session.start_reverification(
        reason_code="dependency_drift",
        evidence_bindings=[binding("dependency-drift", HASH_A)],
        actor_binding=contract["roles"]["lifecycle_owner_binding"],
        occurred_at="2026-08-18T09:00:00Z",
    )
    assert [event["event_type"] for event in events] == [
        "skill.credential_suspended",
        "skill.demoted_trial",
        "skill.reverification_started",
    ]
    assert session.qualification_state is SkillQualificationState.TRIAL
    assert session.release_state is SkillReleaseState.SUSPENDED

    session.start_verification(
        evaluation_suite_binding=binding("skill-evaluation-suite", HASH_B),
        environment_binding=binding("verification-environment", HASH_C),
        actor_binding=contract["roles"]["verifier_binding"],
        occurred_at="2026-08-18T09:01:00Z",
    )
    evaluation = evaluation_example(
        contract,
        manifest,
        identifier="skill-evaluation-2",
        version="2.0.0",
        started_at="2026-08-18T09:01:00Z",
        completed_at="2026-08-18T09:02:00Z",
    )
    session.complete_verification(
        evaluation,
        actor_binding=contract["roles"]["verifier_binding"],
        occurred_at="2026-08-18T09:02:00Z",
    )
    missing_lineage = credential_example(
        contract,
        manifest,
        evaluation,
        identifier="skill-credential-2",
        version="2.0.0",
        issued_at="2026-08-18T09:03:00Z",
    )
    with pytest.raises(SkillPackageValidationError, match="supersede"):
        session.issue_credential(
            missing_lineage,
            actor_binding=contract["roles"]["credential_issuer_binding"],
            occurred_at="2026-08-18T09:03:00Z",
        )

    replacement = credential_example(
        contract,
        manifest,
        evaluation,
        identifier="skill-credential-2",
        version="2.0.0",
        supersedes=credential_binding(old_credential),
        issued_at="2026-08-18T09:03:00Z",
    )
    session.issue_credential(
        replacement,
        actor_binding=contract["roles"]["credential_issuer_binding"],
        occurred_at="2026-08-18T09:03:00Z",
    )
    session.promote_verified(
        actor_binding=contract["roles"]["lifecycle_owner_binding"],
        occurred_at="2026-08-18T09:04:00Z",
    )
    assert session.qualification_state is SkillQualificationState.VERIFIED
    validate_skill_package_event_stream(session.events, contract=contract)


def test_retirement_revokes_credential_before_immutable_archive() -> None:
    session, contract, _, _ = production_session()
    retirement = session.retire(
        reason="superseded_version",
        evidence_bindings=[binding("retirement-evidence", HASH_F)],
        actor_binding=contract["roles"]["lifecycle_owner_binding"],
        occurred_at="2026-08-18T09:00:00Z",
    )
    assert [event["event_type"] for event in retirement] == [
        "skill.credential_revoked",
        "skill.retired",
    ]
    assert session.qualification_state is SkillQualificationState.RETIRED
    assert session.release_state is SkillReleaseState.RETIRED

    archived = session.archive(
        actor_binding=contract["roles"]["lifecycle_owner_binding"],
        occurred_at="2026-08-18T09:01:00Z",
    )
    assert archived["payload"]["immutable_history_retained"] is True
    assert session.stage is SkillPackageStage.ARCHIVED
    assert session.release_state is SkillReleaseState.ARCHIVED
    validate_skill_package_event_stream(session.events, contract=contract)


def test_event_replay_rejects_backward_time_even_with_valid_hash() -> None:
    session, contract, _, _ = trial_session()
    events = [deepcopy(item) for item in session.events[:2]]
    events[1]["occurred_at"] = "2026-08-18T08:00:30Z"
    events[1].pop("event_hash")
    events[1] = build_artifact("skill_package_event", events[1])
    with pytest.raises(SkillPackageValidationError, match="time moves backward"):
        validate_skill_package_event_stream(events, contract=contract)


def test_shared_reflection_guard_allows_candidate_not_promotion(monkeypatch) -> None:
    contract = contract_example()
    candidate = candidate_example(contract)
    reflection_contract = {
        "contract_id": "reflection-contract",
        "contract_version": "1.0.0",
        "contract_hash": HASH_B,
        "reflection_id": "reflection-run-1",
        "admission": {
            "eligibility": "admitted",
            "route": "skill_lifecycle",
            "reason_codes": ["recurrent-success"],
        },
    }
    learning = {
        "target": "skill",
        "candidate_binding": deepcopy(candidate["reflection_candidate_binding"]),
        "source_round_id": "round-1",
        "source_subject_binding": binding("subject-v2", HASH_C),
        "round_evidence_bindings": [binding("round-evidence", HASH_D)],
        "decision": "candidate",
    }
    observation = {
        "observation_id": "observation-1",
        "schema_version": "1.0.0",
        "observation_hash": HASH_E,
        "outcome": "accepted",
        "terminal": True,
        "learning_candidate": learning,
    }
    monkeypatch.setattr(reflection_runtime, "validate_reflection_contract", lambda value: None)
    monkeypatch.setattr(
        reflection_runtime,
        "validate_reflection_event_stream",
        lambda events, contract: None,
    )
    monkeypatch.setattr(
        reflection_runtime,
        "validate_reflection_round_observation",
        lambda value, contract, events: None,
    )
    guard = build_skill_lifecycle_reflection_guard(
        reflection_contract,
        events_provider=lambda: [],
        observations_provider=lambda: [observation],
    )
    assurance = guard(
        "candidate_nomination",
        {
            "reflection_contract_binding": binding("reflection-contract", HASH_B),
            "candidate": candidate,
        },
    )
    assert assurance["id"].startswith("reflection-run-1:skill-candidate-assurance")

    observation["learning_candidate"]["decision"] = "promoted"
    with pytest.raises(SkillPackageAuthorizationError, match="cannot grant"):
        guard(
            "candidate_nomination",
            {
                "reflection_contract_binding": binding("reflection-contract", HASH_B),
                "candidate": candidate,
            },
        )
