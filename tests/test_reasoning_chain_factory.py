"""Behavior and conformance tests for the reasoning-chain factory.

推理链工厂的行为与一致性测试。
"""

from __future__ import annotations

from copy import deepcopy
import pathlib
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(1, str(TESTS_DIR))

from reasoning_artifacts import artifact_fingerprint  # noqa: E402
from reasoning_chain_factory import (  # noqa: E402
    ChainFactoryError,
    ChainPlanDriftError,
    ChainPlanStateError,
    ReasoningChainFactory,
    validate_chain_blueprint,
    validate_chain_plan,
)
from reasoning_runtime import (  # noqa: E402
    BudgetExceededError,
    ReasoningEngine,
    ReasoningRuntimeError,
    ToolAuthorizationError,
    candidate_binding_for,
    content_fingerprint,
)
from test_reasoning_runtime_schemas import (  # noqa: E402
    NOW,
    configuration,
    sealed_contract,
)


def allocation(
    *,
    reasoning_tokens: int = 20,
    latency_ms: int = 20,
    model_calls: int = 1,
    tool_calls: int = 0,
    total_cost_units: float = 0.1,
) -> dict[str, int | float]:
    return {
        "reasoning_tokens": reasoning_tokens,
        "latency_ms": latency_ms,
        "model_calls": model_calls,
        "tool_calls": tool_calls,
        "parallel_paths": 0,
        "iterations": 0,
        "retries": 0,
        "total_cost_units": total_cost_units,
    }


def blueprint_step(
    *,
    key: str,
    sequence: int,
    predecessor: str | None,
    input_claims: list[str],
    output_claim: str,
    kind: str = "inspect",
    uses_tool: bool = False,
    on_failure: str = "escalate",
) -> dict[str, object]:
    return {
        "step_key": key,
        "name_en": key.replace("-", " ").title(),
        "name_zh": "外部可核验步骤",
        "sequence_number": sequence,
        "depends_on": [] if predecessor is None else [predecessor],
        "input_claim_ids": input_claims,
        "output_claim_id": output_claim,
        "criticality": "critical",
        "claim_to_verify": f"{key} is externally supported / {key} 具有外部依据",
        "action": {
            "kind": kind,
            "instruction": f"verify {key} / 核验 {key}",
            "uses_tool": uses_tool,
            **(
                {
                    "tool_binding": {
                        "id": "readonly-test-tool",
                        "version": "1.0.0",
                        "hash": content_fingerprint(
                            {
                                "tool": "readonly-test-tool",
                                "mode": "read_only",
                            }
                        ),
                    },
                    "authorization_policy_binding": {
                        "id": "readonly-tool-policy",
                        "version": "1.0.0",
                        "hash": content_fingerprint(
                            {
                                "policy": "readonly-tool-policy",
                                "scope": "one-plan-bound-read",
                            }
                        ),
                    },
                }
                if uses_tool
                else {}
            ),
            "side_effect": False,
        },
        "required_evidence_types": ["test"],
        "checkpoint": {
            "checkpoint_id": f"checkpoint-{key}",
            "checkpoint_version": "1.0.0",
            "validator_type": "test",
            "pass_criteria": {"all_checks_pass": True},
            "on_failure": on_failure,
        },
        "data_gap_policy": "request_probe",
        "budget_allocation": allocation(tool_calls=1 if uses_tool else 0),
    }


TOOL_AUTHORIZATION_BINDING = {
    "id": "readonly-tool-grant",
    "version": "1.0.0",
    "hash": content_fingerprint(
        {
            "grant": "readonly-tool-grant",
            "subject": "test-controller",
            "scope": "one-plan-bound-read",
        }
    ),
}


def authorize_test_tool(
    authorization: dict[str, object],
    context: dict[str, object],
) -> bool:
    """Accept only the exact test grant, policy, tool, and read-only scope."""

    return (
        authorization == TOOL_AUTHORIZATION_BINDING
        and context.get("authorization_policy_binding", {}).get("id")
        == "readonly-tool-policy"
        and context.get("tool_binding", {}).get("id") == "readonly-test-tool"
        and context.get("side_effect") is False
    )


def authorized_tool_engine() -> ReasoningEngine:
    return ReasoningEngine(tool_authorizer=authorize_test_tool)


def chain_blueprint(
    *, requires_outcome: bool = False, uses_tool: bool = False
) -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "blueprint_id": "reasoning-chain-blueprint-1",
        "blueprint_version": "1.0.0",
        "name_en": "Evidence-backed verification chain",
        "name_zh": "证据驱动验证链",
        "description_en": "Verify the premise and synthesize only checked claims.",
        "description_zh": "先验证前提，再仅使用已检查命题形成综合结论。",
        "max_steps": 4,
        "requires_outcome": requires_outcome,
        "steps": [
            blueprint_step(
                key="verify-premise",
                sequence=1,
                predecessor=None,
                input_claims=[],
                output_claim="claim-premise",
                uses_tool=uses_tool,
            ),
            blueprint_step(
                key="synthesize-result",
                sequence=2,
                predecessor="verify-premise",
                input_claims=["claim-premise"],
                output_claim="claim-result",
                kind="synthesize",
                on_failure="terminate",
            ),
        ],
        "final_claim_ids": ["claim-result"],
    }


def step_evidence(
    session,
    plan_step: dict[str, object],
    *,
    evidence_id: str | None = None,
    evidence_version: str = "1.0.0",
    evidence_type: str = "test",
    claim_id: str | None = None,
    freshness: str = "fresh",
    valid_at: str = NOW,
    retrieved_at: str = NOW,
    captured_at: str = NOW,
    assessed_at: str = NOW,
    age_seconds: float = 0,
    integrity_score: float = 1.0,
    source_ref: str | None = None,
    source_version: str = "1.0.0",
) -> dict[str, object]:
    identifier = evidence_id or f"evidence-{plan_step['step_key']}"
    bound_claim = claim_id or plan_step["output_claim_id"]
    record = {
        "evidence_id": identifier,
        "evidence_version": evidence_version,
        "evidence_hash": content_fingerprint(
            {
                "evidence_id": identifier,
                "claim_id": bound_claim,
                "evidence_type": evidence_type,
            }
        ),
        "candidate_binding": {"state": "not_applicable"},
        "contract_binding": session.plan["contract_binding"],
        "evidence_type": evidence_type,
        "claim_bindings": [
            {
                "claim_id": bound_claim,
                "relation": "supports",
                "criticality": "critical",
            }
        ],
        "source": {
            "source_type": "test",
            "source_ref": source_ref or f"pytest:{plan_step['step_key']}",
            "source_version": source_version,
        },
        "valid_at": valid_at,
        "retrieved_at": retrieved_at,
        "captured_at": captured_at,
        "scope": {
            "workflow_id": session.plan["workflow_id"],
            "claim_ids": [bound_claim],
        },
        "freshness": {
            "status": freshness,
            "assessed_at": assessed_at,
            "age_seconds": age_seconds,
        },
        "integrity_score": integrity_score,
        "sensitivity": "internal",
        "redaction_state": "not_required",
        "transformation_history": [],
    }
    record["record_hash"] = artifact_fingerprint(record, "record_hash")
    return record


def candidate_evidence_revision(
    candidate: object,
    predecessor: dict[str, object],
    *,
    evidence_version: str = "1.0.1",
) -> dict[str, object]:
    """Create the explicit candidate-bound revision of one step record."""

    predecessor_binding = {
        "id": predecessor["evidence_id"],
        "version": predecessor["evidence_version"],
        "hash": predecessor["record_hash"],
    }
    record = deepcopy(predecessor)
    record["evidence_version"] = evidence_version
    record["predecessor_evidence_binding"] = predecessor_binding
    record["candidate_binding"] = {
        "state": "observed",
        "value": candidate_binding_for(candidate),
    }
    record["transformation_history"] = list(
        predecessor["transformation_history"]
    ) + [
        {
            "operation": "candidate_binding_revision",
            "predecessor_evidence_binding": predecessor_binding,
        }
    ]
    record["record_hash"] = artifact_fingerprint(record, "record_hash")
    return record


def checkpoint_validation(
    session,
    plan_step: dict[str, object],
    *,
    observation: object,
    evidence_records: list[dict[str, object]] | None = None,
    evidence_refs: list[str] | None = None,
    evidence_bindings: list[dict[str, str]] | None = None,
    result: str = "passed",
    evidence_types: list[str] | None = None,
) -> dict[str, object]:
    checkpoint = plan_step["checkpoint"]
    records = evidence_records or [step_evidence(session, plan_step)]
    resolved_bindings = [
        {
            "id": evidence["evidence_id"],
            "version": evidence["evidence_version"],
            "hash": evidence["record_hash"],
        }
        for evidence in records
    ]
    checkpoint_binding = {
        "id": checkpoint["checkpoint_id"],
        "version": checkpoint["checkpoint_version"],
        "hash": checkpoint["checkpoint_hash"],
    }
    record = {
        "schema_version": "1.0.0",
        "validation_id": f"checkpoint-validation:{plan_step['step_id']}",
        "validation_version": "1.0.0",
        "plan_binding": session.plan_binding,
        "step_binding": {
            "id": plan_step["step_id"],
            "version": session.plan["plan_version"],
            "hash": content_fingerprint(plan_step),
        },
        "checkpoint_binding": checkpoint_binding,
        "validator_type": checkpoint["validator_type"],
        "validator_binding": {
            "id": checkpoint["checkpoint_id"],
            "version": checkpoint["checkpoint_version"],
            "hash": content_fingerprint(
                {
                    "checkpoint_binding": checkpoint_binding,
                    "validator_type": checkpoint["validator_type"],
                }
            ),
        },
        "criteria_binding": {
            "id": checkpoint["checkpoint_id"],
            "version": checkpoint["checkpoint_version"],
            "hash": content_fingerprint(checkpoint["pass_criteria"]),
        },
        "observation_hash": content_fingerprint(observation),
        "evidence_refs": (
            [evidence["evidence_id"] for evidence in records]
            if evidence_refs is None
            else evidence_refs
        ),
        "evidence_bindings": (
            resolved_bindings
            if evidence_bindings is None
            else evidence_bindings
        ),
        "observed_evidence_types": (
            list(dict.fromkeys(evidence["evidence_type"] for evidence in records))
            if evidence_types is None
            else evidence_types
        ),
        "result": result,
        "checked_at": NOW,
        "actor_binding": {
            "id": "test-validator-actor",
            "version": "1.0.0",
            "hash": content_fingerprint({"actor": "test-validator-actor"}),
        },
        "authority_binding": {
            "id": "test-validator-authority",
            "version": "1.0.0",
            "hash": content_fingerprint(
                {"authority": "test-validator-authority"}
            ),
        },
        "findings": [],
    }
    record["validation_hash"] = artifact_fingerprint(record, "validation_hash")
    return record


def close_usage() -> dict[str, int | float]:
    return {
        "reasoning_tokens": 1,
        "latency_ms": 1,
        "model_calls": 0,
        "tool_calls": 0,
        "parallel_paths": 0,
        "iterations": 0,
        "retries": 0,
        "total_cost_units": 0.0,
    }


def compile_plan(
    *, blueprint: dict[str, object] | None = None, contract=None
):
    selected_blueprint = blueprint or chain_blueprint()
    selected_contract = contract or sealed_contract()
    plan = ReasoningChainFactory().compile(selected_blueprint, selected_contract)
    return selected_blueprint, selected_contract, plan


def completed_chain_session(*, final_evidence_version: str = "1.0.0"):
    """Build a passed chain and retain its exact step-evidence records."""

    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    evidence_by_step = {}
    for step in plan["steps"]:
        evidence = step_evidence(
            session,
            step,
            evidence_version=(
                final_evidence_version
                if step["step_key"] == "synthesize-result"
                else "1.0.0"
            ),
        )
        evidence_by_step[step["step_key"]] = evidence
        observation = {"verified": True}
        session.start_step(step["step_key"], evidence_records=[evidence])
        session.close_step(
            step["step_key"],
            observation=observation,
            checkpoint_validation=checkpoint_validation(
                session,
                step,
                observation=observation,
                evidence_records=[evidence],
            ),
            resource_use=close_usage(),
            information_gain=0.5,
        )
    return source, contract, plan, engine, session, evidence_by_step


def test_factory_compiles_a_deterministic_schema_valid_plan() -> None:
    source, contract, plan = compile_plan()
    duplicate = ReasoningChainFactory().compile(source, contract)

    assert duplicate == plan
    assert plan["execution_mode"] == "chain"
    assert plan["primary_topology"] == "chain"
    assert [step["sequence_number"] for step in plan["steps"]] == [1, 2]
    assert plan["steps"][0]["predecessor_step_id"] is None
    assert (
        plan["steps"][1]["predecessor_step_id"]
        == plan["steps"][0]["step_id"]
    )
    assert plan["budget_allocation"]["reasoning_tokens"] == 40
    assert "PROBE_0005" in plan["probe_plan"]["required_probes"]
    validate_chain_plan(plan, contract=contract, blueprint=source)


def test_compatibility_entrypoint_exposes_split_compiler_and_session() -> None:
    assert ReasoningChainFactory.__module__.endswith("reasoning_chain_compiler")
    from reasoning_chain_factory import ChainPlanSession

    assert ChainPlanSession.__module__.endswith("reasoning_chain_session")


def test_blueprint_rejects_non_linear_or_unbound_claim_dependencies() -> None:
    source = chain_blueprint()
    source["steps"][1]["depends_on"] = []
    source["steps"][1]["input_claim_ids"] = []

    with pytest.raises(ChainFactoryError, match="immediate predecessor"):
        validate_chain_blueprint(source)


def test_blueprint_rejects_missing_critical_evidence_and_private_fields() -> None:
    source = chain_blueprint()
    source["steps"][0]["required_evidence_types"] = []
    with pytest.raises(ChainFactoryError, match="needs evidence types"):
        validate_chain_blueprint(source)

    source = chain_blueprint()
    source["steps"][0]["checkpoint"]["pass_criteria"] = {
        "hidden_reasoning": "forbidden"
    }
    with pytest.raises(ChainFactoryError, match="private reasoning field"):
        validate_chain_blueprint(source)


def test_blueprint_requires_tool_identity_only_for_tool_steps() -> None:
    source = chain_blueprint(uses_tool=True)
    del source["steps"][0]["action"]["tool_binding"]
    with pytest.raises(ChainFactoryError, match="tool_binding"):
        validate_chain_blueprint(source)

    source = chain_blueprint(uses_tool=True)
    del source["steps"][0]["action"]["authorization_policy_binding"]
    with pytest.raises(ChainFactoryError, match="authorization_policy_binding"):
        validate_chain_blueprint(source)

    source = chain_blueprint()
    source["steps"][0]["action"]["tool_binding"] = {
        "id": "unexpected-tool",
        "version": "1.0.0",
        "hash": "sha256:" + "a" * 64,
    }
    with pytest.raises(ChainFactoryError, match="tool_binding"):
        validate_chain_blueprint(source)

    source = chain_blueprint()
    source["steps"][0]["action"]["authorization_policy_binding"] = {
        "id": "unexpected-policy",
        "version": "1.0.0",
        "hash": "sha256:" + "b" * 64,
    }
    with pytest.raises(ChainFactoryError, match="authorization_policy_binding"):
        validate_chain_blueprint(source)


def test_factory_rejects_non_chain_contract_and_budget_overallocation() -> None:
    contract = sealed_contract()
    parallel = configuration("parallel")
    contract.update(parallel)
    contract["routing_decision"]["selected_configuration"] = parallel
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
    with pytest.raises(ChainFactoryError, match="routed chain contract"):
        ReasoningChainFactory().compile(chain_blueprint(), contract)

    source = chain_blueprint()
    source["steps"][0]["budget_allocation"]["reasoning_tokens"] = 4096
    source["steps"][1]["budget_allocation"]["reasoning_tokens"] = 4096
    with pytest.raises(ChainFactoryError, match="exceeds contract limit"):
        ReasoningChainFactory().compile(source, sealed_contract())


def test_switch_exit_requires_an_allowlisted_contract_rule() -> None:
    source = chain_blueprint()
    source["steps"][0]["checkpoint"]["on_failure"] = "switch_parallel"
    contract = sealed_contract()
    with pytest.raises(ChainFactoryError, match="allowed contract switch"):
        ReasoningChainFactory().compile(source, contract)

    contract["allowed_mode_switches"] = [
        {
            "switch_id": "switch-to-parallel",
            "from": configuration("chain"),
            "to": configuration("parallel"),
            "trigger": "conflicting_evidence",
            "max_switches": 1,
            "preserve_budget": True,
            "requires_validation": True,
        }
    ]
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
    plan = ReasoningChainFactory().compile(source, contract)
    assert plan["steps"][0]["checkpoint"]["on_failure"] == "switch_parallel"


def test_tool_and_outcome_conditions_are_resolved_into_probe_plan() -> None:
    source = chain_blueprint(requires_outcome=True, uses_tool=True)
    _, _, plan = compile_plan(blueprint=source)

    assert "tool_or_side_effect_action" in plan["probe_plan"]["active_conditions"]
    assert (
        "downstream_adoption_or_correctness_metric"
        in plan["probe_plan"]["active_conditions"]
    )
    assert plan["steps"][0]["tool_binding"] == source["steps"][0]["action"][
        "tool_binding"
    ]
    assert plan["steps"][0]["authorization_policy_binding"] == source[
        "steps"
    ][0]["action"]["authorization_policy_binding"]
    assert "PROBE_0007" in plan["probe_plan"]["required_probes"]
    assert "PROBE_0013" in plan["probe_plan"]["required_probes"]


def test_tool_step_reserves_exactly_one_readonly_call() -> None:
    source = chain_blueprint(uses_tool=True)
    source["steps"][0]["budget_allocation"]["tool_calls"] = 2

    with pytest.raises(ChainFactoryError, match="exactly one tool call"):
        ReasoningChainFactory().compile(source, sealed_contract())


def test_readonly_tool_adapter_binds_dispatch_output_and_close() -> None:
    source, contract, plan = compile_plan(blueprint=chain_blueprint(uses_tool=True))
    authorization_checks: list[tuple[dict[str, object], dict[str, object]]] = []

    def capture_authorization(
        authorization: dict[str, object], context: dict[str, object]
    ) -> bool:
        authorization_checks.append((authorization, context))
        return authorize_test_tool(authorization, context)

    engine = ReasoningEngine(tool_authorizer=capture_authorization)
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    step = plan["steps"][0]
    evidence = step_evidence(session, step)
    session.start_step(step["step_key"], evidence_records=[evidence])

    tool_input = {"query": "lookup-public-record-42"}
    tool_output = {"record": "public-result-42", "verified": True}
    tool_call_id = session.dispatch_readonly_tool(
        step["step_key"],
        tool_input=tool_input,
        authorization_binding=TOOL_AUTHORIZATION_BINDING,
    )
    with pytest.raises(ValueError, match="non-empty observation"):
        session.observe_readonly_tool(
            step["step_key"],
            tool_input=tool_input,
            authorization_binding=TOOL_AUTHORIZATION_BINDING,
            outcome="succeeded",
            output=None,
        )
    with pytest.raises(ReasoningRuntimeError, match="does not match one dispatch"):
        session.observe_readonly_tool(
            step["step_key"],
            tool_input={"query": "different-query"},
            authorization_binding=TOOL_AUTHORIZATION_BINDING,
            outcome="succeeded",
            output=tool_output,
        )
    output_hash = session.observe_readonly_tool(
        step["step_key"],
        tool_input=tool_input,
        authorization_binding=TOOL_AUTHORIZATION_BINDING,
        outcome="succeeded",
        output=tool_output,
    )
    assert output_hash == content_fingerprint(tool_output)

    usage = close_usage()
    usage["tool_calls"] = 1
    outcome = session.close_step(
        step["step_key"],
        observation=tool_output,
        checkpoint_validation=checkpoint_validation(
            session,
            step,
            observation=tool_output,
            evidence_records=[evidence],
        ),
        resource_use=usage,
        information_gain=0.5,
    )
    assert outcome.premise_accepted is True

    relevant = [
        event
        for event in engine.events.events(contract["run_id"])
        if event.event_type
        in {"step_started", "action_dispatched", "action_observed", "step_closed"}
    ]
    assert [event.event_type for event in relevant] == [
        "step_started",
        "action_dispatched",
        "action_observed",
        "step_closed",
    ]
    dispatch, observed = relevant[1:3]
    assert dispatch.as_dict()["tool_call_id"] == tool_call_id
    assert observed.as_dict()["tool_call_id"] == tool_call_id
    assert dispatch.payload["tool_binding"] == step["tool_binding"]
    assert dispatch.payload["authorization_policy_binding"] == step[
        "authorization_policy_binding"
    ]
    assert dispatch.payload["authorization_binding"] == TOOL_AUTHORIZATION_BINDING
    assert dispatch.payload["authorization_verified"] is True
    assert dispatch.payload["plan_binding"] == session.plan_binding
    assert dispatch.payload["side_effect"] is False
    assert dispatch.payload["input_hash"] == content_fingerprint(tool_input)
    assert observed.payload["output_hash"] == content_fingerprint(tool_output)
    assert "lookup-public-record-42" not in dispatch.payload_json
    assert "public-result-42" not in observed.payload_json
    assert len(authorization_checks) == 1
    checked_grant, checked_context = authorization_checks[0]
    assert checked_grant == TOOL_AUTHORIZATION_BINDING
    assert checked_context["input_hash"] == content_fingerprint(tool_input)
    assert "lookup-public-record-42" not in str(checked_context)


def test_tool_step_fails_closed_without_successful_observation() -> None:
    for observed_outcome in (None, "failed"):
        source, contract, plan = compile_plan(
            blueprint=chain_blueprint(uses_tool=True)
        )
        engine = authorized_tool_engine()
        session = ReasoningChainFactory().start_session(
            engine, plan, contract, source
        )
        step = plan["steps"][0]
        evidence = step_evidence(session, step)
        tool_input = {"query": "readonly"}
        observation = {"status": "unavailable"}
        session.start_step(step["step_key"], evidence_records=[evidence])
        session.dispatch_readonly_tool(
            step["step_key"],
            tool_input=tool_input,
            authorization_binding=TOOL_AUTHORIZATION_BINDING,
        )
        if observed_outcome is not None:
            session.observe_readonly_tool(
                step["step_key"],
                tool_input=tool_input,
                authorization_binding=TOOL_AUTHORIZATION_BINDING,
                outcome=observed_outcome,
            )
        usage = close_usage()
        usage["tool_calls"] = 1
        with pytest.raises(ChainPlanStateError, match="tool step cannot close"):
            session.close_step(
                step["step_key"],
                observation=observation,
                checkpoint_validation=checkpoint_validation(
                    session,
                    step,
                    observation=observation,
                    evidence_records=[evidence],
                ),
                resource_use=usage,
                information_gain=0.5,
            )


def test_tool_adapter_rejects_non_tool_steps_and_binding_bypass() -> None:
    source, contract, plan = compile_plan()
    engine = authorized_tool_engine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    session.start_step(
        first["step_key"], evidence_records=[step_evidence(session, first)]
    )
    with pytest.raises(ChainPlanStateError, match="does not declare a tool"):
        session.dispatch_readonly_tool(
            first["step_key"],
            tool_input={"query": "x"},
            authorization_binding=TOOL_AUTHORIZATION_BINDING,
        )

    source, contract, plan = compile_plan(blueprint=chain_blueprint(uses_tool=True))
    engine = ReasoningEngine(tool_authorizer=lambda authorization, context: True)
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    session.start_step(
        first["step_key"], evidence_records=[step_evidence(session, first)]
    )
    engine.dispatch_readonly_tool(
        contract["run_id"],
        step_id=first["step_id"],
        tool_call_id=f"chain-tool-{first['step_id']}",
        tool_binding={
            "id": "substituted-tool",
            "version": "1.0.0",
            "hash": "sha256:" + "d" * 64,
        },
        authorization_policy_binding=first["authorization_policy_binding"],
        authorization_binding=TOOL_AUTHORIZATION_BINDING,
        tool_input={"query": "x"},
        plan_binding=session.plan_binding,
    )
    with pytest.raises(ChainPlanDriftError, match="tool action binding drift"):
        session.next_step()


def test_tool_dispatch_fails_closed_without_live_verified_authority() -> None:
    source, contract, plan = compile_plan(blueprint=chain_blueprint(uses_tool=True))
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    step = plan["steps"][0]
    session.start_step(
        step["step_key"], evidence_records=[step_evidence(session, step)]
    )
    with pytest.raises(ToolAuthorizationError, match="no live authorizer"):
        session.dispatch_readonly_tool(
            step["step_key"],
            tool_input={"query": "protected"},
            authorization_binding=TOOL_AUTHORIZATION_BINDING,
        )
    assert not any(
        event.event_type == "action_dispatched"
        for event in engine.events.events(contract["run_id"])
    )

    engine = authorized_tool_engine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    session.start_step(
        step["step_key"], evidence_records=[step_evidence(session, step)]
    )
    wrong_grant = {
        "id": "untrusted-tool-grant",
        "version": "1.0.0",
        "hash": "sha256:" + "e" * 64,
    }
    with pytest.raises(ToolAuthorizationError, match="not verified"):
        session.dispatch_readonly_tool(
            step["step_key"],
            tool_input={"query": "protected"},
            authorization_binding=wrong_grant,
        )
    assert not any(
        event.event_type == "action_dispatched"
        for event in engine.events.events(contract["run_id"])
    )

    engine = ReasoningEngine(
        tool_authorizer=lambda authorization, context: 1  # type: ignore[arg-type,return-value]
    )
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    session.start_step(
        step["step_key"], evidence_records=[step_evidence(session, step)]
    )
    with pytest.raises(ToolAuthorizationError, match="not verified"):
        session.dispatch_readonly_tool(
            step["step_key"],
            tool_input={"query": "truthy-is-not-authority"},
            authorization_binding=TOOL_AUTHORIZATION_BINDING,
        )


def test_plan_hash_and_probe_plan_tampering_are_rejected() -> None:
    source, contract, plan = compile_plan()
    tampered = deepcopy(plan)
    tampered["steps"][0]["claim_to_verify"] = "tampered / 已篡改"
    with pytest.raises(ChainFactoryError, match="plan_hash"):
        validate_chain_plan(tampered, contract=contract, blueprint=source)

    tampered = deepcopy(plan)
    tampered["probe_plan"]["required_probes"].remove("PROBE_0005")
    tampered["plan_hash"] = artifact_fingerprint(tampered, "plan_hash")
    with pytest.raises(ChainFactoryError, match="probe plan"):
        validate_chain_plan(tampered, contract=contract, blueprint=source)


def test_rehashed_plan_cannot_drift_from_its_bound_blueprint() -> None:
    source, contract, plan = compile_plan()
    forged = deepcopy(plan)
    forged["steps"][0]["claim_to_verify"] = "forged claim / 伪造命题"
    forged["plan_hash"] = artifact_fingerprint(forged, "plan_hash")

    with pytest.raises(ChainFactoryError, match="supplied together"):
        validate_chain_plan(forged, contract=contract)
    with pytest.raises(ChainFactoryError, match="differs from blueprint"):
        validate_chain_plan(forged, contract=contract, blueprint=source)
    with pytest.raises(ChainFactoryError, match="deterministic output"):
        ReasoningChainFactory().start_session(
            ReasoningEngine(), forged, contract, source
        )

    forged = deepcopy(plan)
    forged["plan_id"] = "chain-plan-forged"
    forged["plan_hash"] = artifact_fingerprint(forged, "plan_hash")
    with pytest.raises(ChainFactoryError, match="deterministic factory output"):
        validate_chain_plan(forged, contract=contract, blueprint=source)


def test_factory_rejects_schema_valid_but_unsupported_runtime_stop() -> None:
    contract = sealed_contract()
    contract["stop_conditions"].append(
        {
            "condition_id": "stop-deadline",
            "type": "deadline_reached",
            "deadline": "2030-01-01T00:00:00Z",
            "on_trigger": "timeout",
        }
    )
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")

    with pytest.raises(ChainFactoryError, match="not executable"):
        ReasoningChainFactory().compile(chain_blueprint(), contract)


def test_session_enforces_order_then_accepts_a_fully_checked_candidate() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)

    with pytest.raises(ChainPlanStateError, match="next eligible"):
        second = plan["steps"][1]
        session.start_step(
            "synthesize-result",
            evidence_records=[step_evidence(session, second)],
        )

    evidence_by_step = {}
    for step in plan["steps"]:
        evidence = step_evidence(session, step)
        evidence_by_step[step["step_key"]] = evidence
        session.start_step(
            step["step_key"], evidence_records=[evidence]
        )
        outcome = session.close_step(
            step["step_key"],
            observation={"verified": True},
            checkpoint_validation=checkpoint_validation(
                session,
                step,
                observation={"verified": True},
                evidence_records=[evidence],
            ),
            resource_use=close_usage(),
            information_gain=0.5,
        )

    assert outcome.chain_complete is True
    assert outcome.next_action == "candidate_ready"
    candidate = {"valid": True, "summary": "public candidate / 公开候选"}
    candidate_evidence = candidate_evidence_revision(
        candidate,
        evidence_by_step["synthesize-result"],
    )
    candidate_hash = session.set_candidate(
        candidate,
        evidence_records=[candidate_evidence],
        idempotency_key="candidate-final",
    )
    assert session.set_candidate(
        candidate,
        evidence_records=[candidate_evidence],
        idempotency_key="candidate-final",
    ) == candidate_hash
    assert candidate_hash == engine.snapshot(contract["run_id"]).candidate_hash
    candidate_event = next(
        event
        for event in engine.events.events(contract["run_id"])
        if event.event_type == "candidate_created"
    )
    assert candidate_event.payload["plan_binding"] == session.plan_binding
    assert candidate_event.payload["final_claim_ids"] == plan["final_claim_ids"]
    assert candidate_event.payload["evidence_record_bindings"] == [
        {
            "id": candidate_evidence["evidence_id"],
            "version": candidate_evidence["evidence_version"],
            "hash": candidate_evidence["record_hash"],
        }
    ]
    candidate_evidence_event = next(
        event
        for event in engine.events.events(contract["run_id"])
        if event.event_type == "evidence_recorded"
        and event.payload["evidence_version"] == "1.0.1"
    )
    assert candidate_event.sequence < candidate_evidence_event.sequence
    assert len(
        [
            event
            for event in engine.events.events(contract["run_id"])
            if event.event_type == "candidate_created"
        ]
    ) == 1


@pytest.mark.parametrize(
    ("variant", "message"),
    [
        ("missing", "exactly cover"),
        ("wrong_predecessor", "not a final-claim step record"),
        ("wrong_candidate", "candidate evidence binding drift"),
        ("mutated_source", "source content drift"),
    ],
)
def test_candidate_evidence_requires_exact_revision_lineage(
    variant: str,
    message: str,
) -> None:
    _, _, _, _, session, evidence_by_step = completed_chain_session()
    candidate = {"valid": True, "summary": "lineage candidate / 血缘候选"}
    record = candidate_evidence_revision(
        candidate,
        evidence_by_step["synthesize-result"],
    )
    records = [record]
    if variant == "missing":
        records = []
    elif variant == "wrong_predecessor":
        record["predecessor_evidence_binding"]["hash"] = "sha256:" + "f" * 64
        record["transformation_history"][-1][
            "predecessor_evidence_binding"
        ] = deepcopy(record["predecessor_evidence_binding"])
        record["record_hash"] = artifact_fingerprint(record, "record_hash")
    elif variant == "wrong_candidate":
        record["candidate_binding"] = {
            "state": "observed",
            "value": candidate_binding_for({"different": True}),
        }
        record["record_hash"] = artifact_fingerprint(record, "record_hash")
    else:
        record["evidence_hash"] = "sha256:" + "e" * 64
        record["record_hash"] = artifact_fingerprint(record, "record_hash")

    with pytest.raises(ChainPlanStateError, match=message):
        session.set_candidate(candidate, evidence_records=records)


def test_candidate_evidence_uses_semver_prerelease_precedence() -> None:
    _, _, _, _, session, evidence_by_step = completed_chain_session(
        final_evidence_version="1.0.0-rc.1"
    )
    candidate = {"valid": True, "summary": "semver candidate / 语义版本候选"}
    predecessor = evidence_by_step["synthesize-result"]
    release_revision = candidate_evidence_revision(
        candidate,
        predecessor,
        evidence_version="1.0.0",
    )
    assert session.set_candidate(
        candidate,
        evidence_records=[release_revision],
    ) == candidate_binding_for(candidate)["hash"]

    _, _, _, _, session, evidence_by_step = completed_chain_session(
        final_evidence_version="1.0.0-rc.1"
    )
    lower_revision = candidate_evidence_revision(
        candidate,
        evidence_by_step["synthesize-result"],
        evidence_version="1.0.0-beta.2",
    )
    with pytest.raises(ChainPlanStateError, match="higher revision"):
        session.set_candidate(candidate, evidence_records=[lower_revision])


def test_session_rejects_plan_bound_candidate_without_record_lineage() -> None:
    _, contract, plan, engine, session, _ = completed_chain_session()
    engine.set_candidate(
        contract["run_id"],
        {"forged": True, "summary": "plan-bound bypass / 计划绑定绕过"},
        evidence=["unstructured-evidence"],
        plan_binding=session.plan_binding,
        final_claim_ids=plan["final_claim_ids"],
    )

    with pytest.raises(ChainPlanDriftError, match="evidence record bindings"):
        session.next_step()


def test_failed_checkpoint_blocks_downstream_and_returns_declared_exit() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    session.start_step(
        first["step_key"], evidence_records=[step_evidence(session, first)]
    )
    validation = checkpoint_validation(
        session,
        first,
        observation={"verified": False},
        result="failed",
    )
    outcome = session.close_step(
        first["step_key"],
        observation={"verified": False},
        checkpoint_validation=validation,
        resource_use=close_usage(),
        information_gain=0.5,
    )

    assert outcome.premise_accepted is False
    assert outcome.next_action == "escalate"
    assert session.next_step() is None
    with pytest.raises(ChainPlanStateError, match="next eligible"):
        second = plan["steps"][1]
        session.start_step(
            "synthesize-result",
            evidence_records=[step_evidence(session, second)],
        )
    with pytest.raises(ChainPlanStateError, match="chain is not complete"):
        session.set_candidate({"valid": False})


def test_passed_checkpoint_requires_evidence_types_and_step_budget() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    session.start_step(
        first["step_key"], evidence_records=[step_evidence(session, first)]
    )

    with pytest.raises(ChainPlanStateError, match="do not match resolved records"):
        session.close_step(
            first["step_key"],
            observation={"verified": True},
            checkpoint_validation=checkpoint_validation(
                session,
                first,
                observation={"verified": True},
                evidence_types=[],
            ),
            resource_use=close_usage(),
            information_gain=0.5,
        )

    too_expensive = close_usage()
    too_expensive["reasoning_tokens"] = 21
    with pytest.raises(ChainPlanStateError, match="exceeds its allocation"):
        session.close_step(
            first["step_key"],
            observation={"verified": True},
            checkpoint_validation=checkpoint_validation(
                session, first, observation={"verified": True}
            ),
            resource_use=too_expensive,
            information_gain=0.5,
        )


def test_critical_step_requires_structured_evidence_records() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    with pytest.raises(ChainPlanStateError, match="structured evidence records"):
        session.start_step(first["step_key"], evidence_records=[])


def test_step_budget_is_reserved_before_start_and_reconciled_on_close() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    session.start_step(
        first["step_key"], evidence_records=[step_evidence(session, first)]
    )

    started_snapshot = engine.snapshot(contract["run_id"])
    assert started_snapshot.budget.used["tokens"] == 0
    assert started_snapshot.budget.reserved["tokens"] == first["budget_allocation"][
        "reasoning_tokens"
    ]
    events = engine.events.events(contract["run_id"])
    reserve = next(event for event in events if event.event_type == "budget_reserved")
    started = next(event for event in events if event.event_type == "step_started")
    assert reserve.sequence < started.sequence

    observation = {"verified": True}
    session.close_step(
        first["step_key"],
        observation=observation,
        checkpoint_validation=checkpoint_validation(
            session, first, observation=observation
        ),
        resource_use=close_usage(),
        information_gain=0.5,
    )
    closed_snapshot = engine.snapshot(contract["run_id"])
    assert closed_snapshot.budget.reserved["tokens"] == 0
    assert closed_snapshot.budget.used["tokens"] == 1
    events = engine.events.events(contract["run_id"])
    consumed = next(event for event in events if event.event_type == "budget_consumed")
    closed = next(event for event in events if event.event_type == "step_closed")
    assert reserve.sequence < consumed.sequence < closed.sequence
    assert consumed.payload["reservation_id"] == f"chain-budget-{first['step_id']}"


def test_budget_shortage_fails_before_step_start() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    engine.consume_budget(
        contract["run_id"],
        {"tokens": contract["budget"]["max_reasoning_tokens"] - 1},
        idempotency_key="consume-before-chain-step",
    )
    first = plan["steps"][0]

    with pytest.raises(BudgetExceededError, match="budget"):
        session.start_step(
            first["step_key"], evidence_records=[step_evidence(session, first)]
        )
    assert not any(
        event.event_type == "step_started"
        for event in engine.events.events(contract["run_id"])
    )


def test_evidence_hash_freshness_integrity_and_claim_coverage_fail_closed() -> None:
    variants = [
        {"tamper_hash": True},
        {"freshness": "stale"},
        {
            "valid_at": "2026-07-15T06:00:00Z",
            "age_seconds": 0,
        },
        {"integrity_score": 0.1},
        {"claim_id": "unrelated-claim"},
    ]
    for variant in variants:
        source, contract, plan = compile_plan()
        engine = ReasoningEngine()
        session = ReasoningChainFactory().start_session(
            engine, plan, contract, source
        )
        first = plan["steps"][0]
        evidence_options = {
            key: value for key, value in variant.items() if key != "tamper_hash"
        }
        evidence = step_evidence(session, first, **evidence_options)
        if variant.get("tamper_hash"):
            evidence["scope"]["claim_ids"] = ["tampered-claim"]
            with pytest.raises(ChainPlanStateError, match="binding drift"):
                session.start_step(first["step_key"], evidence_records=[evidence])
            continue

        session.start_step(first["step_key"], evidence_records=[evidence])
        observation = {"verified": True}
        with pytest.raises(ChainPlanStateError, match="evidence gate failed"):
            session.close_step(
                first["step_key"],
                observation=observation,
                checkpoint_validation=checkpoint_validation(
                    session,
                    first,
                    observation=observation,
                    evidence_records=[evidence],
                ),
                resource_use=close_usage(),
                information_gain=0.5,
            )


def test_independent_sources_are_counted_by_source_not_version() -> None:
    contract = sealed_contract()
    contract["evidence_sufficiency"]["min_independent_sources"] = 2
    contract.pop("contract_hash")
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")

    for distinct_sources in (False, True):
        source, selected_contract, plan = compile_plan(contract=deepcopy(contract))
        engine = ReasoningEngine()
        session = ReasoningChainFactory().start_session(
            engine, plan, selected_contract, source
        )
        first = plan["steps"][0]
        records = [
            step_evidence(
                session,
                first,
                evidence_id="evidence-source-a",
                source_ref="pytest:shared-source",
                source_version="1.0.0",
            ),
            step_evidence(
                session,
                first,
                evidence_id="evidence-source-b",
                source_ref=(
                    "pytest:independent-source"
                    if distinct_sources
                    else "pytest:shared-source"
                ),
                source_version="2.0.0",
            ),
        ]
        session.start_step(first["step_key"], evidence_records=records)
        observation = {"verified": True}
        close = lambda: session.close_step(
            first["step_key"],
            observation=observation,
            checkpoint_validation=checkpoint_validation(
                session,
                first,
                observation=observation,
                evidence_records=records,
            ),
            resource_use=close_usage(),
            information_gain=0.5,
        )

        if distinct_sources:
            assert close().premise_accepted is True
        else:
            with pytest.raises(ChainPlanStateError, match="independent evidence"):
                close()


def test_checkpoint_validation_cannot_rebind_evidence_or_observation() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    observation = {"verified": True}
    session.start_step(
        first["step_key"], evidence_records=[step_evidence(session, first)]
    )

    forged = checkpoint_validation(
        session,
        first,
        observation=observation,
        evidence_refs=["invented-evidence"],
    )
    with pytest.raises(ChainPlanStateError, match="evidence differs"):
        session.close_step(
            first["step_key"],
            observation=observation,
            checkpoint_validation=forged,
            resource_use=close_usage(),
            information_gain=0.5,
        )

    forged = checkpoint_validation(session, first, observation={"verified": False})
    with pytest.raises(ChainPlanStateError, match="does not bind the observation"):
        session.close_step(
            first["step_key"],
            observation=observation,
            checkpoint_validation=forged,
            resource_use=close_usage(),
            information_gain=0.5,
        )


def test_passed_checkpoint_requires_accountable_actor_and_authority() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    observation = {"verified": True}
    session.start_step(
        first["step_key"], evidence_records=[step_evidence(session, first)]
    )
    validation = checkpoint_validation(session, first, observation=observation)
    validation["actor_binding"] = {"state": "unknown"}
    validation["authority_binding"] = {"state": "missing"}
    validation["validation_hash"] = artifact_fingerprint(
        validation, "validation_hash"
    )

    with pytest.raises(ChainPlanStateError, match="actor_binding"):
        session.close_step(
            first["step_key"],
            observation=observation,
            checkpoint_validation=validation,
            resource_use=close_usage(),
            information_gain=0.5,
        )


def test_step_close_is_idempotent_for_identical_content() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    session.start_step(
        first["step_key"], evidence_records=[step_evidence(session, first)]
    )
    arguments = {
        "observation": {"verified": True},
        "checkpoint_validation": checkpoint_validation(
            session, first, observation={"verified": True}
        ),
        "resource_use": close_usage(),
        "information_gain": 0.5,
    }

    original = session.close_step(first["step_key"], **arguments)
    duplicate = session.close_step(first["step_key"], **arguments)

    assert duplicate == original
    close_events = [
        event
        for event in engine.events.events(contract["run_id"])
        if event.event_type == "step_closed"
    ]
    assert len(close_events) == 1


def test_session_detects_direct_engine_bypass_as_plan_drift() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    engine.start_step(
        contract["run_id"],
        step_id="rogue-step",
        claim="rogue public claim / 越界公开命题",
        evidence_refs=[],
        action="rogue read / 越界读取",
    )

    with pytest.raises(ChainPlanDriftError, match="unplanned step"):
        session.next_step()


def test_session_detects_bound_but_mutated_step_bypass_as_plan_drift() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    first = plan["steps"][0]
    engine.start_step(
        contract["run_id"],
        step_id=first["step_id"],
        claim=first["claim_to_verify"],
        evidence_refs=["evidence-1"],
        action={
            "plan_binding": session.plan_binding,
            "logical_step_id": first["step_key"],
            "action_kind": first["action_kind"],
            "instruction": "mutated instruction / 被篡改指令",
            "uses_tool": first["uses_tool"],
            "checkpoint_binding": {
                "id": first["checkpoint"]["checkpoint_id"],
                "version": first["checkpoint"]["checkpoint_version"],
                "hash": first["checkpoint"]["checkpoint_hash"],
            },
            "side_effect": False,
        },
    )

    with pytest.raises(ChainPlanDriftError, match="start contract drift"):
        session.next_step()


def test_session_detects_candidate_created_before_chain_completion() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    engine.set_candidate(
        contract["run_id"],
        {"unbound": True, "summary": "premature candidate / 过早候选"},
    )

    with pytest.raises(ChainPlanDriftError, match="before the chain passed"):
        session.next_step()


def test_session_rejects_unbound_candidate_after_chain_completion() -> None:
    source, contract, plan = compile_plan()
    engine = ReasoningEngine()
    session = ReasoningChainFactory().start_session(engine, plan, contract, source)
    for step in plan["steps"]:
        observation = {"verified": True}
        session.start_step(
            step["step_key"], evidence_records=[step_evidence(session, step)]
        )
        session.close_step(
            step["step_key"],
            observation=observation,
            checkpoint_validation=checkpoint_validation(
                session, step, observation=observation
            ),
            resource_use=close_usage(),
            information_gain=0.5,
        )

    engine.set_candidate(
        contract["run_id"],
        {"unbound": True, "summary": "generic runtime bypass / 通用运行时绕过"},
    )
    with pytest.raises(ChainPlanDriftError, match="candidate binding differs"):
        session.next_step()
