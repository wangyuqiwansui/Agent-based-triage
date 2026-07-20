"""Behavior and conformance tests for the two-level workflow router.

/ 两级工作流路由器的行为与一致性测试。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
SCHEMA_PATH = (
    ROOT
    / "skills"
    / "harness-engineering-patterns"
    / "schemas"
    / "workflow-route-envelope.schema.json"
)
sys.path.insert(0, str(RUNTIME_DIR))

from reasoning_artifacts import (  # noqa: E402
    ArtifactValidationError,
    build_artifact,
    validate_workflow_route_envelope,
)
from reasoning_router import (  # noqa: E402
    EvidenceState,
    IntentComplexity,
    MechanismUncertainty,
)
from workflow_router import (  # noqa: E402
    ActionRisk,
    ApprovalState,
    MechanicalState,
    SignalObservation,
    SignalState,
    TaskAtom,
    TaskIntent,
    WorkflowRouteCoordinator,
    WorkflowRouteError,
    WorkflowRouteRequest,
)


HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
NOW = "2026-07-17T08:00:00Z"
LATER = "2026-07-17T08:01:00Z"

SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def binding(identifier: str, digest: str = HASH_A) -> dict[str, str]:
    return {"id": identifier, "version": "1.0.0", "hash": digest}


def observed_binding(identifier: str) -> dict[str, object]:
    return {"state": "observed", "value": binding(identifier)}


def observation(
    value: object | None,
    *,
    state: SignalState = SignalState.OBSERVED,
    name: str = "signal",
    captured_at: str = NOW,
) -> SignalObservation:
    return SignalObservation(
        state=state,
        value=value,
        source_binding=binding("WORKFLOW_SIGNAL_SOURCE"),
        source_field=f"/signals/{name}",
        valid_at=NOW,
        captured_at=captured_at,
        method="workflow_report",
        integrity_hash=HASH_B,
    )


def base_signals() -> dict[str, SignalObservation]:
    return {
        "task_intent": observation(TaskIntent.STRUCTURED_JUDGMENT, name="task_intent"),
        "evidence_state": observation(
            EvidenceState.COMPLETE_CONSISTENT, name="evidence_state"
        ),
        "mechanical_state": observation(
            None,
            state=SignalState.NOT_APPLICABLE,
            name="mechanical_state",
        ),
        "action_risk": observation(ActionRisk.READ_ONLY, name="action_risk"),
        "intent_complexity": observation(IntentComplexity.LOW, name="intent_complexity"),
        "mechanism_uncertainty": observation(
            MechanismUncertainty.LOW, name="mechanism_uncertainty"
        ),
        "environment_interaction_required": observation(
            False, name="environment_interaction_required"
        ),
        "material_rivals_present": observation(False, name="material_rivals_present"),
        "dominant_dependency_path": observation(False, name="dominant_dependency_path"),
        "permission_granted": observation(True, name="permission_granted"),
        "prohibited_action": observation(False, name="prohibited_action"),
        "irreversible_action": observation(False, name="irreversible_action"),
        "strong_validation_available": observation(
            True, name="strong_validation_available"
        ),
        "accountable_owner_present": observation(
            True, name="accountable_owner_present"
        ),
        "approval_state": observation(ApprovalState.NOT_REQUIRED, name="approval_state"),
    }


def task_atom(
    intent: TaskIntent = TaskIntent.STRUCTURED_JUDGMENT,
    *,
    judgment: bool = True,
    write: bool = False,
) -> TaskAtom:
    return TaskAtom(
        task_atom_id="ATOM_0001",
        task_atom_version="1.0.0",
        primary_intent=intent,
        input_binding=binding("ATOM_INPUT"),
        output_contract_binding=binding("ATOM_OUTPUT"),
        dependency_atom_ids=(),
        risk_owner_binding=observed_binding("RISK_OWNER"),
        includes_read_only_judgment=judgment,
        includes_write_action=write,
    )


def route_request(**changes: object) -> WorkflowRouteRequest:
    values: dict[str, object] = {
        "workflow_id": "WORKFLOW_0001",
        "task_id": "TASK_0001",
        "run_id": "RUN_0001",
        "scene_id": "SCENE_TEST",
        "task_atom": task_atom(),
        "signals": base_signals(),
        "budget_profile_binding": binding("BUDGET_STANDARD"),
        "validator_profile_binding": binding("VALIDATOR_STANDARD"),
        "created_at": NOW,
    }
    values.update(changes)
    return WorkflowRouteRequest(**values)


def write_request(
    risk: ActionRisk = ActionRisk.REVERSIBLE_WRITE,
    *,
    approval: ApprovalState = ApprovalState.NOT_REQUIRED,
    human_gate: dict[str, object] | None = None,
) -> WorkflowRouteRequest:
    signals = base_signals()
    signals.update(
        {
            "task_intent": observation(TaskIntent.BUSINESS_ACTION, name="task_intent"),
            "mechanical_state": observation(MechanicalState.READY, name="mechanical_state"),
            "action_risk": observation(risk, name="action_risk"),
            "approval_state": observation(approval, name="approval_state"),
        }
    )
    return route_request(
        task_atom=task_atom(TaskIntent.BUSINESS_ACTION, judgment=False, write=True),
        signals=signals,
        human_gate=human_gate,
    )


def approved_gate() -> dict[str, object]:
    return {
        "placement": "before_action",
        "status": "approved",
        "gate_binding": binding("HUMAN_GATE"),
        "authority_binding": observed_binding("APPROVAL_AUTHORITY"),
    }


def test_coordinator_builds_a_sealed_schema_valid_composite_envelope() -> None:
    Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA["x-contract-version"] == "1.0.0"
    envelope = WorkflowRouteCoordinator().route(route_request())

    assert VALIDATOR.is_valid(envelope)
    validate_workflow_route_envelope(envelope)
    assert envelope["execution_lane"] == "structured_judgment"
    assert envelope["reasoning_decision"]["disposition"] == "execute"
    assert envelope["action_allowed"] is False
    assert envelope["route_envelope_hash"].startswith("sha256:")


def test_reversible_write_requires_all_mechanical_gates_but_not_reasoning_alone() -> None:
    envelope = WorkflowRouteCoordinator().route(write_request())

    assert envelope["execution_lane"] == "planned_execution"
    assert envelope["reasoning_decision"]["disposition"] == "execute"
    assert envelope["reasoning_decision"]["configuration"]["execution_mode"] == "chain"
    assert envelope["action_allowed"] is True
    assert envelope["blockers"] == []


def test_sensitive_write_requires_an_authoritative_human_gate() -> None:
    without_gate = WorkflowRouteCoordinator().route(
        write_request(ActionRisk.SENSITIVE_WRITE, approval=ApprovalState.APPROVED)
    )
    with_gate = WorkflowRouteCoordinator().route(
        write_request(
            ActionRisk.SENSITIVE_WRITE,
            approval=ApprovalState.APPROVED,
            human_gate=approved_gate(),
        )
    )

    assert without_gate["action_allowed"] is False
    assert without_gate["execution_lane"] == "clarification_human_review"
    assert "AUTHORITATIVE_HUMAN_GATE_REQUIRED" in {
        item["code"] for item in without_gate["blockers"]
    }
    assert with_gate["action_allowed"] is True


def test_missing_workflow_signal_forces_abstention_and_clarification() -> None:
    request = route_request()
    signals = dict(request.signals)
    signals["task_intent"] = observation(
        None,
        state=SignalState.UNKNOWN,
        name="task_intent",
    )

    envelope = WorkflowRouteCoordinator().route(replace(request, signals=signals))

    assert envelope["abstained"] is True
    assert envelope["execution_lane"] == "clarification_human_review"
    assert envelope["reasoning_decision"]["disposition"] == "escalate"
    assert envelope["action_allowed"] is False
    assert "MISSING_ROUTE_SIGNAL" in {item["code"] for item in envelope["blockers"]}


def test_insufficient_evidence_preserves_explicit_escalation_handoff() -> None:
    request = route_request()
    signals = dict(request.signals)
    signals["evidence_state"] = observation(
        EvidenceState.INSUFFICIENT,
        name="evidence_state",
    )

    envelope = WorkflowRouteCoordinator().route(replace(request, signals=signals))

    decision = envelope["reasoning_decision"]
    assert decision["disposition"] == "escalate"
    assert decision["configuration"] is None
    assert decision["escalation_handoff"]["target"] == "evidence_completion"
    assert decision["escalation_handoff"]["reason_codes"] == ["insufficient_evidence"]


def test_confidence_telemetry_cannot_change_the_route_or_decision_identity() -> None:
    coordinator = WorkflowRouteCoordinator()
    without_confidence = coordinator.route(route_request())
    with_confidence = coordinator.route(
        route_request(
            route_confidence=0.99,
            route_confidence_source_binding=binding("LEGACY_CLASSIFIER"),
        )
    )

    assert with_confidence["route_confidence_telemetry"]["value"] == 0.99
    assert without_confidence["decision_id"] == with_confidence["decision_id"]
    assert (
        without_confidence["workflow_signal_fingerprint"]
        == with_confidence["workflow_signal_fingerprint"]
    )
    assert (
        without_confidence["reasoning_decision"]
        == with_confidence["reasoning_decision"]
    )


def test_legacy_confidence_migration_cannot_fill_a_missing_typed_signal() -> None:
    request = route_request(
        route_confidence=0.99,
        route_confidence_source_binding=binding("LEGACY_CLASSIFIER"),
    )
    signals = dict(request.signals)
    signals["intent_complexity"] = observation(
        None,
        state=SignalState.UNKNOWN,
        name="intent_complexity",
    )

    envelope = WorkflowRouteCoordinator().route(replace(request, signals=signals))

    assert envelope["route_confidence_telemetry"]["value"] == 0.99
    assert envelope["abstained"] is True
    assert envelope["action_allowed"] is False
    assert envelope["execution_lane"] == "clarification_human_review"
    assert "intent_complexity" in {
        blocker["source_signal"] for blocker in envelope["blockers"]
    }


def test_provenance_change_creates_a_new_workflow_decision() -> None:
    coordinator = WorkflowRouteCoordinator()
    first_request = route_request()
    signals = dict(first_request.signals)
    signals["intent_complexity"] = observation(
        IntentComplexity.LOW,
        name="intent_complexity",
        captured_at=LATER,
    )

    first = coordinator.route(first_request)
    second = coordinator.route(replace(first_request, signals=signals))

    assert first["workflow_signal_fingerprint"] != second["workflow_signal_fingerprint"]
    assert first["decision_id"] != second["decision_id"]


def test_schema_and_semantic_guard_reject_reasoning_based_action_authorization() -> None:
    envelope = WorkflowRouteCoordinator().route(route_request())
    tampered = deepcopy(envelope)
    tampered.pop("route_envelope_hash")
    tampered["action_allowed"] = True

    with pytest.raises(ArtifactValidationError):
        build_artifact("workflow_route_envelope", tampered)


def test_semantic_guard_rejects_a_content_inconsistent_workflow_decision_id() -> None:
    envelope = WorkflowRouteCoordinator().route(route_request())
    tampered = deepcopy(envelope)
    tampered.pop("route_envelope_hash")
    tampered["decision_id"] = "WORKFLOW_ROUTE_DELIBERATELY_WRONG"

    with pytest.raises(ArtifactValidationError, match="decision_id"):
        build_artifact("workflow_route_envelope", tampered)


def test_task_atom_cannot_mix_judgment_and_write_action() -> None:
    with pytest.raises(WorkflowRouteError, match="must be split"):
        task_atom(TaskIntent.BUSINESS_ACTION, judgment=True, write=True)

