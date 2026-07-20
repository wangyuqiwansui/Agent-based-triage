"""Append-only workflow route ledger tests / 追加式工作流路由账本测试。"""

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
TEST_DIR = ROOT / "tests"
SCHEMA_PATH = (
    ROOT
    / "skills"
    / "harness-engineering-patterns"
    / "schemas"
    / "workflow-route-revision.schema.json"
)
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(0, str(TEST_DIR))

from reasoning_artifacts import artifact_fingerprint, build_artifact  # noqa: E402
from reasoning_router import IntentComplexity  # noqa: E402
from test_workflow_router import (  # noqa: E402
    LATER,
    binding,
    observation,
    route_request,
)
from workflow_route_ledger import (  # noqa: E402
    WorkflowRouteLedger,
    WorkflowRouteLedgerError,
)
from workflow_router import WorkflowRouteCoordinator  # noqa: E402


REVISION_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
REVISION_VALIDATOR = Draft202012Validator(
    REVISION_SCHEMA,
    format_checker=FormatChecker(),
)
ACTOR = binding("ROUTE_ACTOR")
AUTHORITY = binding("ROUTE_AUTHORITY")
EVIDENCE = binding("ROUTE_EVIDENCE")
HYSTERESIS = binding("HYSTERESIS_EVIDENCE")


def routes() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    coordinator = WorkflowRouteCoordinator()
    request = route_request()
    initial = coordinator.route(request)

    upgraded_signals = dict(request.signals)
    upgraded_signals["dominant_dependency_path"] = observation(
        True,
        name="dominant_dependency_path",
        captured_at=LATER,
    )
    upgraded = coordinator.route(replace(request, signals=upgraded_signals))

    deescalated_signals = dict(request.signals)
    deescalated_signals["intent_complexity"] = observation(
        IntentComplexity.LOW,
        name="intent_complexity",
        captured_at=LATER,
    )
    deescalated = coordinator.route(replace(request, signals=deescalated_signals))
    return initial, upgraded, deescalated


def append_upgrade(
    ledger: WorkflowRouteLedger,
    candidate: dict[str, object],
    *,
    key: str = "IDEMPOTENCY_UPGRADE_0001",
) -> dict[str, object]:
    return ledger.append_revision(
        candidate,
        idempotency_key=key,
        trigger_class="route_insufficiency",
        direction="upgrade",
        trigger_reason_code="DOMINANT_DEPENDENCY_OBSERVED",
        trigger_evidence_bindings=[EVIDENCE],
        actor_binding=ACTOR,
        authority_binding=AUTHORITY,
    )


def test_revision_is_schema_valid_persisted_and_replayable(tmp_path: Path) -> None:
    Draft202012Validator.check_schema(REVISION_SCHEMA)
    assert REVISION_SCHEMA["x-contract-version"] == "1.0.0"
    initial, upgraded, _ = routes()
    path = tmp_path / "route-ledger.jsonl"
    ledger = WorkflowRouteLedger(path)
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")

    committed = append_upgrade(ledger, upgraded)
    event = ledger.revision_events[0]

    assert committed["decision_revision"] == 2
    assert REVISION_VALIDATOR.is_valid(event)
    assert event["previous_envelope_binding"]["hash"] == initial["route_envelope_hash"]
    assert event["current_envelope_binding"]["hash"] == committed["route_envelope_hash"]
    replayed = WorkflowRouteLedger(path)
    assert replayed.head == committed
    assert replayed.revision_events == ledger.revision_events


def test_retry_is_idempotent_and_conflicting_reuse_is_rejected() -> None:
    initial, upgraded, _ = routes()
    ledger = WorkflowRouteLedger()
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")

    first = append_upgrade(ledger, upgraded)
    second = append_upgrade(ledger, upgraded)

    assert second == first
    assert len(ledger.revision_events) == 1
    with pytest.raises(WorkflowRouteLedgerError, match="different content"):
        ledger.append_revision(
            upgraded,
            idempotency_key="IDEMPOTENCY_UPGRADE_0001",
            trigger_class="validator_failure",
            direction="upgrade",
            trigger_reason_code="DIFFERENT_REASON",
            trigger_evidence_bindings=[EVIDENCE],
            actor_binding=ACTOR,
            authority_binding=AUTHORITY,
        )


def test_switch_budget_must_be_positive() -> None:
    with pytest.raises(ValueError, match="positive"):
        WorkflowRouteLedger(max_switches=0)


def test_total_switch_budget_is_enforced_across_revision_ids() -> None:
    initial, upgraded, deescalated = routes()
    ledger = WorkflowRouteLedger(max_switches=1)
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    append_upgrade(ledger, upgraded)

    with pytest.raises(WorkflowRouteLedgerError, match="budget exhausted"):
        ledger.append_revision(
            deescalated,
            idempotency_key="IDEMPOTENCY_DEESCALATE_0001",
            trigger_class="external_state_change",
            direction="deescalation",
            trigger_reason_code="DEPENDENCY_RESOLVED",
            trigger_evidence_bindings=[EVIDENCE],
            hysteresis_evidence_bindings=[HYSTERESIS],
            actor_binding=ACTOR,
            authority_binding=AUTHORITY,
        )


def test_same_frozen_inputs_cannot_produce_a_different_route() -> None:
    initial, upgraded, _ = routes()
    ledger = WorkflowRouteLedger()
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    conflicting = deepcopy(initial)
    conflicting.pop("route_envelope_hash")
    conflicting["reasoning_decision"]["configuration"] = deepcopy(
        upgraded["reasoning_decision"]["configuration"]
    )
    decision = conflicting["reasoning_decision"]
    binding_value = decision.pop("decision_binding")
    binding_value["hash"] = artifact_fingerprint(decision)
    decision["decision_binding"] = binding_value
    conflicting["decision_id"] = "WORKFLOW_ROUTE_" + artifact_fingerprint(
        {
            "workflow_policy_binding": conflicting["workflow_policy_binding"],
            "workflow_signal_fingerprint": conflicting["workflow_signal_fingerprint"],
            "reasoning_decision_binding": binding_value,
        }
    ).removeprefix("sha256:")[:24]
    conflicting = build_artifact("workflow_route_envelope", conflicting)

    with pytest.raises(WorkflowRouteLedgerError, match="same frozen inputs"):
        append_upgrade(ledger, conflicting)


def test_deescalation_requires_hysteresis_and_rejects_budget_only_trigger() -> None:
    initial, upgraded, deescalated = routes()
    ledger = WorkflowRouteLedger()
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    append_upgrade(ledger, upgraded)

    with pytest.raises(Exception, match="hysteresis"):
        ledger.append_revision(
            deescalated,
            idempotency_key="IDEMPOTENCY_DEESCALATE_NO_HYSTERESIS",
            trigger_class="external_state_change",
            direction="deescalation",
            trigger_reason_code="DEPENDENCY_RESOLVED",
            trigger_evidence_bindings=[EVIDENCE],
            actor_binding=ACTOR,
            authority_binding=AUTHORITY,
        )
    with pytest.raises(Exception):
        ledger.append_revision(
            deescalated,
            idempotency_key="IDEMPOTENCY_DEESCALATE_BUDGET_ONLY",
            trigger_class="budget_pressure",
            direction="deescalation",
            trigger_reason_code="BUDGET_PRESSURE_ONLY",
            trigger_evidence_bindings=[EVIDENCE],
            hysteresis_evidence_bindings=[HYSTERESIS],
            actor_binding=ACTOR,
            authority_binding=AUTHORITY,
        )


def test_route_oscillation_requires_changed_evidence_and_hysteresis() -> None:
    initial, upgraded, deescalated = routes()
    ledger = WorkflowRouteLedger()
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    append_upgrade(ledger, upgraded)

    with pytest.raises(WorkflowRouteLedgerError, match="oscillation"):
        ledger.append_revision(
            deescalated,
            idempotency_key="IDEMPOTENCY_OSCILLATION_UNSAFE",
            trigger_class="external_state_change",
            direction="lateral",
            trigger_reason_code="DEPENDENCY_RESOLVED",
            trigger_evidence_bindings=[EVIDENCE],
            actor_binding=ACTOR,
            authority_binding=AUTHORITY,
        )

    committed = ledger.append_revision(
        deescalated,
        idempotency_key="IDEMPOTENCY_OSCILLATION_SAFE",
        trigger_class="external_state_change",
        direction="deescalation",
        trigger_reason_code="DEPENDENCY_RESOLVED",
        trigger_evidence_bindings=[EVIDENCE],
        hysteresis_evidence_bindings=[HYSTERESIS],
        actor_binding=ACTOR,
        authority_binding=AUTHORITY,
    )
    assert committed["decision_revision"] == 3


def test_route_revision_binds_optional_reasoning_mode_switch_event() -> None:
    initial, upgraded, _ = routes()
    ledger = WorkflowRouteLedger()
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    switch_binding = binding("MODE_SWITCH_EVENT_0001")

    committed = ledger.append_revision(
        upgraded,
        idempotency_key="IDEMPOTENCY_MODE_SWITCH_0001",
        trigger_class="route_insufficiency",
        direction="upgrade",
        trigger_reason_code="DOMINANT_DEPENDENCY_OBSERVED",
        trigger_evidence_bindings=[EVIDENCE],
        actor_binding=ACTOR,
        authority_binding=AUTHORITY,
        switch_event_binding={"state": "observed", "value": switch_binding},
    )

    event = ledger.revision_events[0]
    assert event["switch_event_binding"]["value"] == switch_binding
    assert event["current_envelope_binding"]["hash"] == committed["route_envelope_hash"]


def test_revision_semantic_guard_rejects_a_content_inconsistent_event_id() -> None:
    initial, upgraded, _ = routes()
    ledger = WorkflowRouteLedger()
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    append_upgrade(ledger, upgraded)
    event = deepcopy(ledger.revision_events[0])
    event.pop("revision_event_hash")
    event["revision_event_id"] = "WORKFLOW_ROUTE_REVISION_DELIBERATELY_WRONG"

    with pytest.raises(Exception, match="revision_event_id"):
        build_artifact("workflow_route_revision", event)


def test_replay_rejects_a_rehashed_record_with_wrong_request_fingerprint(
    tmp_path: Path,
) -> None:
    initial, _, _ = routes()
    path = tmp_path / "route-ledger.jsonl"
    ledger = WorkflowRouteLedger(path)
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    record = json.loads(path.read_text(encoding="utf-8").strip())
    record["request_fingerprint"] = "sha256:" + "f" * 64
    record_content = deepcopy(record)
    record_content.pop("record_hash")
    record["record_hash"] = artifact_fingerprint(record_content)
    path.write_text(
        json.dumps(
            record,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(WorkflowRouteLedgerError, match="request fingerprint"):
        WorkflowRouteLedger(path)


def test_partial_final_record_fails_closed_during_replay(tmp_path: Path) -> None:
    initial, _, _ = routes()
    path = tmp_path / "route-ledger.jsonl"
    ledger = WorkflowRouteLedger(path)
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")
    with path.open("ab") as stream:
        stream.write(b'{"record_type":"partial"')

    with pytest.raises(WorkflowRouteLedgerError, match="partial record"):
        WorkflowRouteLedger(path)


def test_run_graph_binding_is_an_append_only_gate_revision() -> None:
    initial, _, _ = routes()
    ledger = WorkflowRouteLedger()
    ledger.register_initial(initial, idempotency_key="IDEMPOTENCY_INITIAL_0001")

    committed = ledger.bind_run_graph(
        binding("RUN_GRAPH_0001"),
        idempotency_key="IDEMPOTENCY_RUN_GRAPH_0001",
        actor_binding=ACTOR,
        authority_binding=AUTHORITY,
        created_at=LATER,
    )

    assert committed["decision_revision"] == 2
    assert committed["run_graph_binding"]["state"] == "observed"
    assert committed["action_allowed"] is initial["action_allowed"]
    assert ledger.revision_events[0]["direction"] == "gate_only"
    assert ledger.switch_count == 0
