"""Behavior tests for governed tool dispatch / 受治理工具调度行为测试。"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from reasoning_artifacts import (  # noqa: E402
    ArtifactValidationError,
    artifact_fingerprint,
    validate_tool_dispatch_envelope,
    validate_tool_execution_event,
    validate_tool_execution_result,
)
from tool_dispatch import (  # noqa: E402
    ADMISSION_CHECK_ORDER,
    ActionApproval,
    ActionIntent,
    ActionRisk,
    ApprovalState,
    DispatchContext,
    ExecutionClassification,
    ObservationMode,
    SideEffectClass,
    SideEffectState,
    StateEvidence,
    ToolCapability,
    ToolDispatchCoordinator,
    ToolDispatchConflictError,
    ToolDispatchRequest,
    ToolDispatchRuntime,
    ToolExecutionReceipt,
)
from tool_dispatch_sqlite_store import SqliteToolDispatchStore  # noqa: E402


NOW = "2026-07-24T08:00:00Z"
LATER = "2026-07-24T08:05:00Z"
HASH_A = "sha256:" + "a" * 64


def binding(identifier: str, version: str = "1.0.0") -> dict[str, str]:
    return {"id": identifier, "version": version, "hash": HASH_A}


def read_capability(**changes: object) -> ToolCapability:
    values: dict[str, object] = {
        "tool_id": "TOOL_READ",
        "tool_version": "1.0.0",
        "action_types": ("read_record",),
        "parameter_schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "additionalProperties": False,
            "required": ["record_id"],
            "properties": {"record_id": {"type": "string", "minLength": 1}},
        },
        "required_scopes": frozenset({"record:read"}),
        "allowed_tenants": frozenset({"TENANT_A"}),
        "allowed_stages": frozenset({"execution"}),
        "side_effect_class": SideEffectClass.READ_ONLY,
        "priority": 10,
        "executor_binding": binding("EXECUTOR_READ"),
        "authorization_policy_binding": binding("POLICY_READ"),
    }
    values.update(changes)
    return ToolCapability(**values)


def write_capability(
    side_effect: SideEffectClass = SideEffectClass.REVERSIBLE_WRITE,
) -> ToolCapability:
    return ToolCapability(
        tool_id="TOOL_WRITE",
        tool_version="1.0.0",
        action_types=("update_record",),
        parameter_schema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "additionalProperties": False,
            "required": ["record_id", "value"],
            "properties": {
                "record_id": {"type": "string", "minLength": 1},
                "value": {"type": "string"},
            },
        },
        required_scopes=frozenset({"record:write"}),
        allowed_tenants=frozenset({"TENANT_A"}),
        allowed_stages=frozenset({"execution"}),
        side_effect_class=side_effect,
        priority=20,
        executor_binding=binding("EXECUTOR_WRITE"),
        authorization_policy_binding=binding("POLICY_WRITE"),
        sandbox_binding=binding("SANDBOX_WRITE"),
        compensation_binding=(
            binding("TOOL_COMPENSATE")
            if side_effect is not SideEffectClass.IRREVERSIBLE_EXTERNAL
            else None
        ),
        manual_disposition_binding=(
            binding("MANUAL_QUEUE")
            if side_effect is SideEffectClass.IRREVERSIBLE_EXTERNAL
            else None
        ),
        allowed_resource_prefixes=("record:",),
    )


def state_evidence(version: str = "7") -> StateEvidence:
    return StateEvidence(
        resource_versions={"record:1": version},
        observed_at=NOW,
        evidence_binding=binding("STATE_EVIDENCE"),
        content_hash=HASH_A,
    )


def approval(
    parameters: dict[str, object],
    evidence: StateEvidence,
    *,
    state: ApprovalState = ApprovalState.APPROVED,
) -> ActionApproval:
    resource_hash = artifact_fingerprint(
        {
            "resource_versions": [
                {"resource_id": key, "version": str(value)}
                for key, value in sorted(evidence.resource_versions.items())
            ]
        }
    )
    return ActionApproval(
        state=state,
        approval_binding=binding("APPROVAL"),
        authority_binding=binding("APPROVER_AUTHORITY"),
        parameter_hash=artifact_fingerprint({"parameters": parameters}),
        resource_versions_hash=resource_hash,
        expires_at=LATER,
    )


def read_request(**context_changes: object) -> ToolDispatchRequest:
    intent = ActionIntent(
        workflow_id="WORKFLOW_1",
        workflow_version="1.0.0",
        run_id="RUN_1",
        goal_id="GOAL_1",
        node_id="NODE_1",
        attempt_id="ATTEMPT_1",
        action_id="ACTION_1",
        parent_action_id=None,
        plan_version="PLAN_1",
        correlation_id="CORR_1",
        action_type="read_record",
        parameters={"record_id": "record:1"},
        target_resources=("record:1",),
        expected_side_effect=SideEffectClass.READ_ONLY,
        maximum_side_effect=SideEffectClass.READ_ONLY,
        risk_level=ActionRisk.LOW,
        idempotency_key=None,
        state_evidence=None,
        approval=None,
    )
    context_values: dict[str, object] = {
        "actor_binding": binding("ACTOR"),
        "actor_scopes": frozenset({"record:read"}),
        "tenant_id": "TENANT_A",
        "workflow_state": "executable",
        "stage": "execution",
        "dependencies_satisfied": True,
        "budget_available": True,
        "concurrency_clear": True,
        "current_resource_versions": {},
        "action_authorization_binding": binding("AUTHORIZATION"),
        "observation_mode": ObservationMode.SIDECAR,
        "critical_observability_ready": True,
        "durable_idempotency_available": False,
        "retry_authorized": False,
        "created_at": NOW,
        "permit_expires_at": LATER,
    }
    context_values.update(context_changes)
    return ToolDispatchRequest(intent, DispatchContext(**context_values))


def write_request(
    *,
    action_id: str = "ACTION_WRITE_1",
    attempt_id: str = "ATTEMPT_WRITE_1",
    parent_action_id: str | None = None,
    retry_authorized: bool = False,
    side_effect: SideEffectClass = SideEffectClass.REVERSIBLE_WRITE,
    current_version: str = "7",
) -> ToolDispatchRequest:
    parameters = {"record_id": "record:1", "value": "updated"}
    evidence = state_evidence()
    intent = ActionIntent(
        workflow_id="WORKFLOW_1",
        workflow_version="1.0.0",
        run_id="RUN_WRITE",
        goal_id="GOAL_1",
        node_id="NODE_WRITE",
        attempt_id=attempt_id,
        action_id=action_id,
        parent_action_id=parent_action_id,
        plan_version="PLAN_1",
        correlation_id="CORR_WRITE",
        action_type="update_record",
        parameters=parameters,
        target_resources=("record:1",),
        expected_side_effect=side_effect,
        maximum_side_effect=side_effect,
        risk_level=(
            ActionRisk.MEDIUM
            if side_effect is SideEffectClass.REVERSIBLE_WRITE
            else ActionRisk.CRITICAL
        ),
        idempotency_key="goal-1:record-1:update",
        state_evidence=evidence,
        approval=(
            None
            if side_effect is SideEffectClass.REVERSIBLE_WRITE
            else approval(parameters, evidence)
        ),
    )
    context = DispatchContext(
        actor_binding=binding("ACTOR"),
        actor_scopes=frozenset({"record:write"}),
        tenant_id="TENANT_A",
        workflow_state="executable",
        stage="execution",
        dependencies_satisfied=True,
        budget_available=True,
        concurrency_clear=True,
        current_resource_versions={"record:1": current_version},
        action_authorization_binding=binding("AUTHORIZATION"),
        observation_mode=ObservationMode.HARD_GATE,
        critical_observability_ready=True,
        durable_idempotency_available=True,
        retry_authorized=retry_authorized,
        created_at=NOW,
        permit_expires_at=LATER,
    )
    return ToolDispatchRequest(intent, context)


def allow(_: ToolDispatchRequest, __: ToolCapability) -> bool:
    return True


def fixed_clock() -> datetime:
    return datetime(2026, 7, 24, 8, 0, 1, tzinfo=timezone.utc)


def test_read_only_dispatch_builds_minimal_frontier_and_sealed_permit() -> None:
    unauthorized = read_capability(
        tool_id="TOOL_ADMIN",
        required_scopes=frozenset({"admin"}),
        priority=100,
    )
    coordinator = ToolDispatchCoordinator(
        [unauthorized, read_capability()],
        authority_verifier=allow,
    )

    envelope = coordinator.prepare(read_request())

    validate_tool_dispatch_envelope(envelope)
    assert envelope["decision"] == "allow"
    assert envelope["selected_tool_binding"]["value"]["id"] == "TOOL_READ"
    assert envelope["frontier"]["exclusion_counts"]["permission"] == 1
    assert len(envelope["frontier"]["retained_tool_bindings"]) == 1
    assert [item["name"] for item in envelope["admission_checks"]] == list(
        ADMISSION_CHECK_ORDER
    )
    assert "parameters" not in envelope
    assert envelope["parameter_hash"].startswith("sha256:")
    assert envelope["permit_binding"]["state"] == "observed"


def test_selection_never_overrides_parameter_or_live_authorization_failure() -> None:
    coordinator = ToolDispatchCoordinator(
        [read_capability()],
        authority_verifier=lambda _request, _capability: False,
    )
    malformed = read_request()
    malformed = replace(
        malformed,
        intent=replace(malformed.intent, parameters={"record_id": 7}),
    )

    envelope = coordinator.prepare(malformed)

    assert envelope["decision"] == "reject"
    checks = {item["name"]: item for item in envelope["admission_checks"]}
    assert checks["parameters"]["status"] == "failed"
    assert checks["identity_scope"]["code"] == "LIVE_AUTHORIZATION_DENIED"
    assert envelope["permit_binding"] == {"state": "not_applicable"}


def test_unknown_action_uses_safe_rejection_without_guessing_a_tool() -> None:
    coordinator = ToolDispatchCoordinator(
        [read_capability()],
        authority_verifier=allow,
    )
    request = read_request()
    request = replace(
        request,
        intent=replace(request.intent, action_type="delete_everything"),
    )

    envelope = coordinator.prepare(request)

    assert envelope["decision"] == "reject"
    assert envelope["candidate_evaluations"] == []
    assert envelope["selected_tool_binding"] == {"state": "missing"}
    assert envelope["reason_codes"][:2] == [
        "NO_REGISTERED_CAPABILITY",
        "NO_FRONTIER_CANDIDATE",
    ]


def test_stale_state_evidence_waits_and_never_reaches_executor() -> None:
    coordinator = ToolDispatchCoordinator(
        [write_capability()],
        authority_verifier=allow,
    )
    request = write_request(current_version="8")
    calls = {"count": 0}

    def executor(*_: object) -> ToolExecutionReceipt:
        calls["count"] += 1
        raise AssertionError("executor must not be called")

    run = ToolDispatchRuntime(
        coordinator,
        clock=fixed_clock,
    ).execute(request, executor)

    assert run.envelope["decision"] == "wait"
    assert run.result["classification"] == "waiting"
    assert calls["count"] == 0
    assert not any(
        event["event_type"] == "tool_execution_started" for event in run.events
    )


def test_missing_current_state_inventory_waits_before_write() -> None:
    coordinator = ToolDispatchCoordinator(
        [write_capability()],
        authority_verifier=allow,
    )
    request = write_request()
    request = replace(
        request,
        context=replace(request.context, current_resource_versions={}),
    )

    envelope = coordinator.prepare(request)

    assert envelope["decision"] == "wait"
    state_check = next(
        item
        for item in envelope["admission_checks"]
        if item["name"] == "state_evidence"
    )
    assert state_check["code"] == "CURRENT_STATE_VERSION_INVENTORY_INCOMPLETE"


def test_write_requires_durable_runtime_store_even_after_admission() -> None:
    coordinator = ToolDispatchCoordinator(
        [write_capability()],
        authority_verifier=allow,
    )
    called = {"value": False}

    def executor(*_: object) -> ToolExecutionReceipt:
        called["value"] = True
        raise AssertionError

    run = ToolDispatchRuntime(
        coordinator,
        clock=fixed_clock,
    ).execute(write_request(), executor)

    assert run.envelope["decision"] == "allow"
    assert run.result["classification"] == "rejected"
    assert run.result["error"]["code"] == "DURABLE_STORE_REQUIRED"
    assert called["value"] is False


def test_durable_write_executes_once_and_reuses_prior_success(
    tmp_path: Path,
) -> None:
    store = SqliteToolDispatchStore(tmp_path / "dispatch.sqlite")
    coordinator = ToolDispatchCoordinator(
        [write_capability()],
        authority_verifier=allow,
    )
    runtime = ToolDispatchRuntime(
        coordinator,
        store=store,
        clock=fixed_clock,
    )
    calls = {"count": 0}

    def executor(
        tool: dict[str, object],
        parameters: dict[str, object],
        permit: dict[str, object],
        idempotency_key: str | None,
    ) -> ToolExecutionReceipt:
        calls["count"] += 1
        assert tool["id"] == "TOOL_WRITE"
        assert parameters["value"] == "updated"
        assert permit["id"].endswith("_PERMIT")
        assert idempotency_key == "goal-1:record-1:update"
        return ToolExecutionReceipt(
            ExecutionClassification.SUCCESS,
            SideEffectState.CONFIRMED,
            output_binding=binding("OUTPUT"),
            external_receipt_binding=binding("WRITE_RECEIPT"),
            actual_side_effects=(
                {
                    "resource_id": "record:1",
                    "effect_type": "updated",
                    "receipt_binding": binding("WRITE_RECEIPT"),
                },
            ),
        )

    first = runtime.execute(write_request(), executor)
    retry = runtime.execute(
        write_request(
            action_id="ACTION_WRITE_2",
            attempt_id="ATTEMPT_WRITE_2",
            parent_action_id="ACTION_WRITE_1",
        ),
        executor,
    )

    assert first.result["classification"] == "success"
    assert first.executor_called is True
    assert retry.result["classification"] == "reused_success"
    assert retry.executor_called is False
    assert retry.result["reused_result_binding"]["value"]["id"] == first.result["result_id"]
    assert calls["count"] == 1
    assert store.idempotency_status("goal-1:record-1:update")["status"] == "succeeded"
    assert all(
        event["sequence"] == index
        for index, event in enumerate(store.events("RUN_WRITE"), 1)
    )
    for event in store.events("RUN_WRITE"):
        validate_tool_execution_event(event)
    validate_tool_execution_result(first.result)
    validate_tool_execution_result(retry.result)


def test_write_exception_becomes_unknown_and_is_not_directly_retried(
    tmp_path: Path,
) -> None:
    store = SqliteToolDispatchStore(tmp_path / "unknown.sqlite")
    coordinator = ToolDispatchCoordinator(
        [write_capability()],
        authority_verifier=allow,
    )
    runtime = ToolDispatchRuntime(
        coordinator,
        store=store,
        clock=fixed_clock,
    )
    calls = {"count": 0}

    def crashing_executor(*_: object) -> ToolExecutionReceipt:
        calls["count"] += 1
        raise TimeoutError("receipt lost")

    first = runtime.execute(write_request(), crashing_executor)
    retry = runtime.execute(
        write_request(
            action_id="ACTION_WRITE_2",
            attempt_id="ATTEMPT_WRITE_2",
            parent_action_id="ACTION_WRITE_1",
            retry_authorized=True,
        ),
        crashing_executor,
    )

    assert first.result["classification"] == "unknown"
    assert first.result["next_action"] == "reconcile"
    assert first.result["error"]["retryable"] is False
    assert retry.result["classification"] == "unknown"
    assert retry.executor_called is False
    assert calls["count"] == 1


def test_sensitive_write_requires_approval_bound_to_current_version() -> None:
    capability = write_capability(SideEffectClass.SENSITIVE_WRITE)
    coordinator = ToolDispatchCoordinator(
        [capability],
        authority_verifier=allow,
    )
    request = write_request(side_effect=SideEffectClass.SENSITIVE_WRITE)
    drifted = replace(
        request,
        intent=replace(
            request.intent,
            approval=replace(
                request.intent.approval,
                resource_versions_hash=artifact_fingerprint(
                    {
                        "resource_versions": [
                            {"resource_id": "record:1", "version": "6"}
                        ]
                    }
                ),
            ),
        ),
    )

    allowed = coordinator.prepare(request)
    waiting = coordinator.prepare(drifted)

    assert allowed["decision"] == "allow"
    assert waiting["decision"] == "wait"
    approval_check = next(
        item for item in waiting["admission_checks"] if item["name"] == "approval"
    )
    assert approval_check["code"] == "APPROVAL_RESOURCE_VERSION_DRIFT"


def test_permit_never_outlives_bound_approval() -> None:
    coordinator = ToolDispatchCoordinator(
        [write_capability(SideEffectClass.SENSITIVE_WRITE)],
        authority_verifier=allow,
    )
    request = write_request(side_effect=SideEffectClass.SENSITIVE_WRITE)
    request = replace(
        request,
        intent=replace(
            request.intent,
            approval=replace(
                request.intent.approval,
                expires_at="2026-07-24T08:00:30Z",
            ),
        ),
    )
    called = {"value": False}

    envelope = coordinator.prepare(request)
    run = ToolDispatchRuntime(
        coordinator,
        clock=lambda: datetime(
            2026,
            7,
            24,
            8,
            1,
            tzinfo=timezone.utc,
        ),
    ).execute(
        request,
        lambda *_: called.__setitem__("value", True),
    )

    assert envelope["decision"] == "allow"
    assert envelope["execution_contract"]["permit_expires_at"] == (
        "2026-07-24T08:00:30Z"
    )
    assert run.result["classification"] == "rejected"
    assert run.result["error"]["code"] == "EXECUTION_PERMIT_EXPIRED"
    assert called["value"] is False


def test_tampered_permit_is_rejected_even_with_recomputed_envelope_hash() -> None:
    coordinator = ToolDispatchCoordinator(
        [read_capability()],
        authority_verifier=allow,
    )
    envelope = deepcopy(coordinator.prepare(read_request()))
    envelope["permit_binding"]["value"]["hash"] = "sha256:" + "b" * 64
    envelope["dispatch_hash"] = artifact_fingerprint(envelope, "dispatch_hash")

    with pytest.raises(ArtifactValidationError, match="permit binding"):
        validate_tool_dispatch_envelope(envelope)


def test_result_and_event_certainty_tampering_fails_closed(
    tmp_path: Path,
) -> None:
    store = SqliteToolDispatchStore(tmp_path / "certainty.sqlite")
    coordinator = ToolDispatchCoordinator(
        [write_capability()],
        authority_verifier=allow,
    )
    run = ToolDispatchRuntime(
        coordinator,
        store=store,
        clock=fixed_clock,
    ).execute(
        write_request(),
        lambda *_: ToolExecutionReceipt(
            ExecutionClassification.SUCCESS,
            SideEffectState.CONFIRMED,
            output_binding=binding("OUTPUT"),
            external_receipt_binding=binding("RECEIPT"),
            actual_side_effects=(
                {
                    "resource_id": "record:1",
                    "effect_type": "updated",
                    "receipt_binding": binding("RECEIPT"),
                },
            ),
        ),
    )

    result = deepcopy(run.result)
    result["side_effect_state"] = "unknown"
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="confirmed side effect"):
        validate_tool_execution_result(result)

    result_event = deepcopy(
        next(
            event
            for event in run.events
            if event["event_type"] == "tool_execution_succeeded"
        )
    )
    result_event["event_type"] = "tool_execution_failed"
    result_event["event_hash"] = artifact_fingerprint(result_event, "event_hash")
    with pytest.raises(ArtifactValidationError, match="classification"):
        validate_tool_execution_event(result_event)


def test_completion_after_lease_expiry_persists_unknown(
    tmp_path: Path,
) -> None:
    store = SqliteToolDispatchStore(tmp_path / "expired-completion.sqlite")
    coordinator = ToolDispatchCoordinator(
        [write_capability()],
        authority_verifier=allow,
    )
    clock_values = iter(
        (
            datetime(2026, 7, 24, 8, 0, 1, tzinfo=timezone.utc),
            datetime(2026, 7, 24, 8, 2, 0, tzinfo=timezone.utc),
        )
    )
    runtime = ToolDispatchRuntime(
        coordinator,
        store=store,
        clock=lambda: next(clock_values),
        lease_seconds=30,
    )

    with pytest.raises(ToolDispatchConflictError, match="expired"):
        runtime.execute(
            write_request(),
            lambda *_: ToolExecutionReceipt(
                ExecutionClassification.SUCCESS,
                SideEffectState.CONFIRMED,
                output_binding=binding("OUTPUT"),
                external_receipt_binding=binding("RECEIPT"),
            ),
        )

    assert store.idempotency_status("goal-1:record-1:update")["status"] == "unknown"
