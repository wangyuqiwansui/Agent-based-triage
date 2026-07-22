"""Behavior tests for governed Parallel Exploration / 受治理并行探索的行为测试。"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import pathlib
import sys
import tempfile

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(1, str(TESTS_DIR))

from reasoning_artifacts import artifact_fingerprint, validate_reasoning_result  # noqa: E402
from reasoning_parallel_factory import (  # noqa: E402
    ParallelFactoryError,
    ParallelPlanStateError,
    ReasoningParallelFactory,
    validate_parallel_blueprint,
    validate_parallel_plan,
)
from reasoning_runtime import (  # noqa: E402
    BudgetExceededError,
    JsonlEventStore,
    PrivateReasoningCaptureError,
    ReasoningEngine,
    WorkflowState,
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
    reasoning_tokens: int = 5,
    latency_ms: int = 5,
    model_calls: int = 1,
    parallel_paths: int = 1,
    total_cost_units: float = 0.1,
) -> dict[str, int | float]:
    return {
        "reasoning_tokens": reasoning_tokens,
        "latency_ms": latency_ms,
        "model_calls": model_calls,
        "tool_calls": 0,
        "parallel_paths": parallel_paths,
        "iterations": 0,
        "retries": 0,
        "total_cost_units": total_cost_units,
    }


def parallel_contract() -> dict[str, object]:
    contract = sealed_contract()
    selected = configuration("parallel")
    contract.update(selected)
    contract["routing_decision"]["selected_configuration"] = selected
    contract["routing_decision"]["reasons"] = [
        {
            "reason_code": "independent_hypotheses",
            "source_binding": {"state": "not_applicable"},
        }
    ]
    contract["routing_decision"]["signals"] = [
        {"signal": "parallelizability", "value": {"state": "observed", "value": "high"}}
    ]
    contract["routing_decision"]["signal_fingerprint"] = content_fingerprint(
        contract["routing_decision"]["signals"]
    )
    contract["budget"].update(
        {
            "max_reasoning_tokens": 30,
            "max_latency_ms": 30,
            "max_model_calls": 6,
            "max_tool_calls": 1,
            "max_parallel_paths": 2,
            "max_iterations": 1,
            "max_retries": 1,
            "max_total_cost_units": 1.0,
            "parallel_reservation_policy": "reserve_before_launch",
        }
    )
    contract.pop("contract_hash")
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
    return contract


def parallel_blueprint(contract: dict[str, object] | None = None) -> dict[str, object]:
    selected = contract or parallel_contract()
    return {
        "schema_version": "1.0.0",
        "blueprint_id": "parallel-blueprint-1",
        "blueprint_version": "1.0.0",
        "name_en": "Independent rival diagnosis",
        "name_zh": "独立竞争诊断",
        "description_en": "Compare two materially different root-cause hypotheses.",
        "description_zh": "比较两个具有实质差异的根因假设。",
        "requires_outcome": False,
        "isolation_policy": {
            "policy_id": "parallel-isolation-1",
            "policy_version": "1.0.0",
            "strategy": "shared_input_only",
            "shared_input_binding": deepcopy(selected["normalized_input_binding"]),
            "intermediate_visibility": "branch_private_until_closed",
            "namespace_per_branch": True,
        },
        "comparison_contract": {
            "comparison_id": "parallel-comparison-1",
            "comparison_version": "1.0.0",
            "material_difference_dimensions": ["hypothesis"],
            "minimum_material_dimensions": 1,
            "criteria": [
                {
                    "criterion_id": "evidence-fit",
                    "name_en": "Evidence fit",
                    "name_zh": "证据匹配",
                    "description_en": "Candidate explains the observed evidence.",
                    "description_zh": "候选能够解释已观测证据。",
                    "evaluation_type": "boolean",
                    "direction": "pass",
                    "required": True,
                    "weight": 1.0,
                }
            ],
            "vetoes": [],
            "tie_policy": "escalate",
        },
        "join_policy": {
            "completion_mode": "all_completed",
            "minimum_completed_branches": 2,
            "on_deadline": "escalate",
        },
        "branches": [
            {
                "candidate_path_id": "path-cache",
                "name_en": "Cache hypothesis",
                "name_zh": "缓存假设",
                "hypothesis": "A stale cache produced the mismatch / 陈旧缓存导致不一致",
                "material_difference": [
                    {"dimension": "hypothesis", "statement": "Cache invalidation mechanism"}
                ],
                "claim_ids": ["claim-cache"],
                "required_evidence_types": ["test"],
                "data_gap_policy": "request_probe",
                "budget_allocation": allocation(),
            },
            {
                "candidate_path_id": "path-parser",
                "name_en": "Parser hypothesis",
                "name_zh": "解析器假设",
                "hypothesis": "A parser regression produced the mismatch / 解析器回归导致不一致",
                "material_difference": [
                    {"dimension": "hypothesis", "statement": "Parser transformation mechanism"}
                ],
                "claim_ids": ["claim-parser"],
                "required_evidence_types": ["test"],
                "data_gap_policy": "request_probe",
                "budget_allocation": allocation(),
            },
        ],
        "synthesis": {
            "step_key": "compare-rivals",
            "name_en": "Compare rival hypotheses",
            "name_zh": "比较竞争假设",
            "claim_to_verify": "One candidate best fits the common criteria / 一个候选最符合统一判据",
            "action_instruction": "Compare all branch evidence and preserve minority findings / 比较全部分支证据并保留少数派发现",
            "required_evidence_types": ["test"],
            "budget_allocation": allocation(parallel_paths=0),
        },
        "final_claim_ids": ["claim-final"],
    }


def source_evidence(session, *, path: str, claim_id: str) -> dict[str, object]:
    record = {
        "evidence_id": f"evidence-{path}",
        "evidence_version": "1.0.0",
        "evidence_hash": content_fingerprint({"path": path, "claim": claim_id}),
        "candidate_binding": {"state": "not_applicable"},
        "contract_binding": session.plan["contract_binding"],
        "evidence_type": "test",
        "claim_bindings": [
            {"claim_id": claim_id, "relation": "supports", "criticality": "critical"}
        ],
        "source": {
            "source_type": "test",
            "source_ref": f"pytest:{path}",
            "source_version": "1.0.0",
        },
        "valid_at": NOW,
        "retrieved_at": NOW,
        "captured_at": NOW,
        "scope": {"workflow_id": session.plan["workflow_id"], "claim_ids": [claim_id]},
        "freshness": {"status": "fresh", "assessed_at": NOW, "age_seconds": 0},
        "integrity_score": 1.0,
        "sensitivity": "internal",
        "redaction_state": "not_required",
        "transformation_history": [],
    }
    record["record_hash"] = artifact_fingerprint(record, "record_hash")
    return record


def final_evidence(session, candidate: object, predecessor: dict[str, object]) -> dict[str, object]:
    record = deepcopy(predecessor)
    record["evidence_id"] = "evidence-final"
    record["evidence_version"] = "1.0.0"
    record["candidate_binding"] = {
        "state": "observed",
        "value": candidate_binding_for(candidate),
    }
    record["claim_bindings"] = [
        {"claim_id": "claim-final", "relation": "supports", "criticality": "critical"}
    ]
    record["scope"]["claim_ids"] = ["claim-final"]
    record["transformation_history"] = [
        {"operation": "synthesis_candidate_binding", "source_path": "path-cache"}
    ]
    record["record_hash"] = artifact_fingerprint(record, "record_hash")
    return record


def close_usage() -> dict[str, int | float]:
    return allocation(
        reasoning_tokens=1,
        latency_ms=1,
        model_calls=0,
        parallel_paths=1,
        total_cost_units=0.0,
    )


def synthesis_usage() -> dict[str, int | float]:
    usage = close_usage()
    usage["parallel_paths"] = 0
    return usage


def criterion_result() -> list[dict[str, object]]:
    return [
        {
            "criterion_id": "evidence-fit",
            "status": "passed",
            "value": True,
            "evidence_refs": [],
        }
    ]


def compiled_session():
    contract = parallel_contract()
    blueprint = parallel_blueprint(contract)
    plan = ReasoningParallelFactory().compile(blueprint, contract)
    engine = ReasoningEngine()
    session = ReasoningParallelFactory().start_session(
        engine, plan, contract, blueprint
    )
    return blueprint, contract, plan, engine, session


def close_two_branches(session, *, same_candidate: bool = False):
    session.launch_wave()
    records = {}
    candidates = {}
    for path, claim in (("path-cache", "claim-cache"), ("path-parser", "claim-parser")):
        record = source_evidence(session, path=path, claim_id=claim)
        candidate = {"path": "same" if same_candidate else path, "verified": True}
        session.close_branch(
            path,
            status="completed",
            candidate=candidate,
            evidence_records=[record],
            criterion_results=criterion_result(),
            veto_results=[],
            resource_use=close_usage(),
            information_gain=1.0,
        )
        records[path] = record
        candidates[path] = candidate
    return records, candidates


def synthesized_session():
    contract = parallel_contract()
    blueprint = parallel_blueprint(contract)
    plan = ReasoningParallelFactory().compile(blueprint, contract)
    evaluated_at = datetime.fromisoformat(NOW.replace("Z", "+00:00")).timestamp()
    engine = ReasoningEngine(clock=lambda: evaluated_at)
    session = ReasoningParallelFactory().start_session(
        engine, plan, contract, blueprint
    )
    records, candidates = close_two_branches(session)
    record = final_evidence(session, candidates["path-cache"], records["path-cache"])
    session.synthesize(
        decision="selected",
        reviewed_candidate_path_ids=["path-cache", "path-parser"],
        elimination_reasons={"path-parser": "weaker evidence"},
        minority_findings=[],
        synthesis_basis={"criterion": "evidence-fit"},
        selected_candidate_path_id="path-cache",
        selected_candidate=candidates["path-cache"],
        selected_evidence_records=[record],
        resource_use=synthesis_usage(),
        information_gain=1.0,
    )
    return session, record


def finalization_arguments(record):
    evidence_binding = {
        "id": record["evidence_id"],
        "version": record["evidence_version"],
        "hash": record["evidence_hash"],
    }
    claims = [
        {
            "claim_id": "claim-final",
            "claim_type": "fact",
            "statement": "selected parallel candidate passed the release gate",
            "criticality": "critical",
            "status": "supported",
            "evidence_bindings": [evidence_binding],
        }
    ]
    human_binding = {
        "state": "observed",
        "value": {
            "id": "human-reviewer-1",
            "version": "1.0.0",
            "hash": "sha256:" + "c" * 64,
        },
    }
    authority_binding = {
        "state": "observed",
        "value": {
            "id": "approval-authority-1",
            "version": "1.0.0",
            "hash": "sha256:" + "d" * 64,
        },
    }
    outcomes = [
        {"validator_id": "validator-1", "status": "passed"},
        {
            "validator_id": "human-reviewer-1",
            "status": "passed",
            "actor_binding": human_binding,
            "authority_binding": authority_binding,
        },
    ]
    result_fields = {
        "claims": claims,
        "final_decision": {
            "state": "observed",
            "value": {"decision": "release_selected_parallel_candidate"},
        },
        "output": {
            "format": "json",
            "content": {
                "state": "observed",
                "value": {"status": "verified"},
            },
        },
        "field_provenance": [
            {
                "field_path": "/output/content",
                "source_type": "validator",
                "source_ref": "parallel-final-validation",
                "value_state": "observed",
            }
        ],
        "evaluated_at": NOW,
        "created_at": NOW,
    }
    return outcomes, result_fields


def test_parallel_plan_compiles_deterministically_with_required_probe() -> None:
    contract = parallel_contract()
    blueprint = parallel_blueprint(contract)

    first = ReasoningParallelFactory().compile(blueprint, contract)
    second = ReasoningParallelFactory().compile(blueprint, contract)

    assert first == second
    assert first["execution_mode"] == "parallel"
    assert first["wave_budget_allocation"]["parallel_paths"] == 2
    assert "PROBE_0008" in first["probe_plan"]["required_probes"]
    validate_parallel_blueprint(blueprint)
    validate_parallel_plan(first, contract=contract, blueprint=blueprint)


def test_parallel_blueprint_rejects_false_declared_diversity() -> None:
    contract = parallel_contract()
    blueprint = parallel_blueprint(contract)
    blueprint["branches"][1]["hypothesis"] = blueprint["branches"][0]["hypothesis"]

    with pytest.raises(ParallelFactoryError, match="materially distinct"):
        ReasoningParallelFactory().compile(blueprint, contract)


def test_parallel_plan_rejects_branch_count_beyond_contract() -> None:
    contract = parallel_contract()
    contract["budget"]["max_parallel_paths"] = 1
    contract.pop("contract_hash")
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
    blueprint = parallel_blueprint(contract)

    with pytest.raises(ParallelFactoryError, match="branch count"):
        ReasoningParallelFactory().compile(blueprint, contract)


def test_wave_budget_is_reserved_before_branch_start_events() -> None:
    _, _, plan, engine, session = compiled_session()

    session.launch_wave()
    events = engine.events.events(plan["run_id"])
    reserve_index = next(i for i, event in enumerate(events) if event.event_type == "budget_reserved")
    branch_starts = [
        i
        for i, event in enumerate(events)
        if event.event_type == "step_started"
        and event.as_dict().get("candidate_path_id") is not None
    ]

    assert len(branch_starts) == 2
    assert all(reserve_index < index for index in branch_starts)
    assert {events[index].as_dict()["candidate_path_id"] for index in branch_starts} == {
        "path-cache",
        "path-parser",
    }


def test_wave_budget_reservation_is_atomic_under_runtime_contention() -> None:
    _, _, plan, engine, session = compiled_session()
    engine.reserve_budget(
        session.run_id,
        allocation(
            reasoning_tokens=21,
            latency_ms=0,
            model_calls=0,
            parallel_paths=0,
            total_cost_units=0.0,
        ),
        reservation_id="competing-reservation",
        idempotency_key="competing-reservation",
    )

    with pytest.raises(BudgetExceededError):
        session.launch_wave()

    branch_reservations = {
        session.branch_reservation_id(path)
        for path in ("path-cache", "path-parser")
    }
    events = engine.events.events(plan["run_id"])
    assert not any(
        event.event_type == "budget_reserved"
        and event.payload.get("reservation_id") in branch_reservations
        for event in events
    )
    assert not any(
        event.event_type == "step_started"
        and event.as_dict().get("candidate_path_id") is not None
        for event in events
    )
    assert engine.snapshot(session.run_id).budget.reservation_count == 1


def test_branch_candidate_events_retain_path_and_plan_bindings() -> None:
    _, _, _, engine, session = compiled_session()
    close_two_branches(session)

    branch_candidates = [
        event
        for event in engine.events.events(session.run_id)
        if event.event_type == "candidate_created"
        and event.as_dict().get("candidate_path_id") is not None
    ]

    assert {event.as_dict()["candidate_path_id"] for event in branch_candidates} == {
        "path-cache",
        "path-parser",
    }
    assert all(event.payload["plan_binding"] == session.plan_binding for event in branch_candidates)


def test_jsonl_session_resumes_mid_wave_without_duplicate_events() -> None:
    contract = parallel_contract()
    blueprint = parallel_blueprint(contract)
    factory = ReasoningParallelFactory()
    plan = factory.compile(blueprint, contract)
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "parallel-events.jsonl"
        engine = ReasoningEngine(JsonlEventStore(path))
        session = factory.start_session(engine, plan, contract, blueprint)
        session.launch_wave()
        cache_record = source_evidence(session, path="path-cache", claim_id="claim-cache")
        cache_candidate = {"path": "path-cache", "verified": True}
        session.close_branch(
            "path-cache",
            status="completed",
            candidate=cache_candidate,
            evidence_records=[cache_record],
            criterion_results=criterion_result(),
            veto_results=[],
            resource_use=close_usage(),
            information_gain=1.0,
        )
        event_count = len(engine.events.events(session.run_id))

        reopened = ReasoningEngine(JsonlEventStore(path))
        resumed = factory.resume_session(reopened, plan, contract, blueprint)

        snapshot = reopened.snapshot(resumed.run_id)
        assert len(reopened.events.events(resumed.run_id)) == event_count
        assert snapshot.state is WorkflowState.EXECUTING
        assert snapshot.candidate_hash is None
        assert snapshot.step_count == 1
        assert snapshot.open_step_count == 1
        assert snapshot.budget.reservation_count == 1

        retry = resumed.close_branch(
            "path-cache",
            status="completed",
            candidate=cache_candidate,
            evidence_records=[cache_record],
            criterion_results=criterion_result(),
            veto_results=[],
            resource_use=close_usage(),
            information_gain=1.0,
        )
        assert retry.ready_for_synthesis is False
        assert len(reopened.events.events(resumed.run_id)) == event_count

        parser_record = source_evidence(
            resumed, path="path-parser", claim_id="claim-parser"
        )
        parser_candidate = {"path": "path-parser", "verified": True}
        resumed.close_branch(
            "path-parser",
            status="completed",
            candidate=parser_candidate,
            evidence_records=[parser_record],
            criterion_results=criterion_result(),
            veto_results=[],
            resource_use=close_usage(),
            information_gain=1.0,
        )
        outcome = resumed.synthesize(
            decision="selected",
            reviewed_candidate_path_ids=["path-cache", "path-parser"],
            elimination_reasons={"path-parser": "weaker evidence"},
            minority_findings=[],
            synthesis_basis={"criterion": "evidence-fit"},
            selected_candidate_path_id="path-cache",
            selected_candidate=cache_candidate,
            selected_evidence_records=[
                final_evidence(resumed, cache_candidate, cache_record)
            ],
            resource_use=synthesis_usage(),
            information_gain=1.0,
        )
        assert outcome.next_action == "validate_selected_candidate"


def test_jsonl_session_replays_completed_synthesis_without_new_events() -> None:
    contract = parallel_contract()
    blueprint = parallel_blueprint(contract)
    factory = ReasoningParallelFactory()
    plan = factory.compile(blueprint, contract)
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "parallel-synthesis-events.jsonl"
        engine = ReasoningEngine(JsonlEventStore(path))
        session = factory.start_session(engine, plan, contract, blueprint)
        records, candidates = close_two_branches(session)
        arguments = {
            "decision": "selected",
            "reviewed_candidate_path_ids": ["path-cache", "path-parser"],
            "elimination_reasons": {"path-parser": "weaker evidence"},
            "minority_findings": [],
            "synthesis_basis": {"criterion": "evidence-fit"},
            "selected_candidate_path_id": "path-cache",
            "selected_candidate": candidates["path-cache"],
            "selected_evidence_records": [
                final_evidence(
                    session, candidates["path-cache"], records["path-cache"]
                )
            ],
            "resource_use": synthesis_usage(),
            "information_gain": 1.0,
        }
        first = session.synthesize(**arguments)
        event_count = len(engine.events.events(session.run_id))

        reopened = ReasoningEngine(JsonlEventStore(path))
        resumed = factory.resume_session(reopened, plan, contract, blueprint)
        second = resumed.synthesize(**arguments)

        assert second == first
        assert len(reopened.events.events(resumed.run_id)) == event_count
        assert reopened.snapshot(resumed.run_id).state is WorkflowState.CANDIDATE_READY


def test_synthesis_requires_every_branch_terminal_and_review() -> None:
    _, _, _, _, session = compiled_session()
    session.launch_wave()
    record = source_evidence(session, path="path-cache", claim_id="claim-cache")
    session.close_branch(
        "path-cache",
        status="completed",
        candidate={"path": "cache", "verified": True},
        evidence_records=[record],
        criterion_results=criterion_result(),
        resource_use=close_usage(),
        information_gain=1.0,
    )

    with pytest.raises(ParallelPlanStateError, match="explicit terminal"):
        session.synthesize(
            decision="selected",
            reviewed_candidate_path_ids=["path-cache", "path-parser"],
            elimination_reasons={"path-parser": "not closed"},
            minority_findings=[],
            synthesis_basis={"criterion": "evidence-fit"},
            selected_candidate_path_id="path-cache",
            selected_candidate={"path": "cache", "verified": True},
            resource_use=synthesis_usage(),
            information_gain=1.0,
        )


def test_selected_synthesis_preserves_loser_and_promotes_only_final_candidate() -> None:
    _, _, _, engine, session = compiled_session()
    records, candidates = close_two_branches(session)
    final_record = final_evidence(session, candidates["path-cache"], records["path-cache"])

    outcome = session.synthesize(
        decision="selected",
        reviewed_candidate_path_ids=["path-cache", "path-parser"],
        elimination_reasons={"path-parser": "parser hypothesis has weaker evidence"},
        minority_findings=[
            {"candidate_path_id": "path-parser", "finding": "parser risk remains monitorable"}
        ],
        synthesis_basis={"criterion": "evidence-fit", "winner": "path-cache"},
        selected_candidate_path_id="path-cache",
        selected_candidate=candidates["path-cache"],
        selected_evidence_records=[final_record],
        resource_use=synthesis_usage(),
        information_gain=1.0,
    )

    assert outcome.next_action == "validate_selected_candidate"
    assert engine.snapshot(session.run_id).state is WorkflowState.CANDIDATE_READY
    compared = [
        event for event in engine.events.events(session.run_id) if event.event_type == "candidate_compared"
    ]
    assert len(compared) == 1
    assert compared[0].payload["decision"] == "selected"
    synthesis_close = next(
        event
        for event in engine.events.events(session.run_id)
        if event.event_type == "step_closed"
        and event.as_dict().get("step_id") == session.plan["synthesis"]["step_id"]
    )
    assert synthesis_close.payload["local_decision"]["elimination_reasons"] == {
        "path-parser": "parser hypothesis has weaker evidence"
    }


def test_selected_synthesis_exact_retry_is_idempotent() -> None:
    _, _, _, engine, session = compiled_session()
    records, candidates = close_two_branches(session)
    arguments = {
        "decision": "selected",
        "reviewed_candidate_path_ids": ["path-cache", "path-parser"],
        "elimination_reasons": {"path-parser": "weaker evidence"},
        "minority_findings": [],
        "synthesis_basis": {"criterion": "evidence-fit"},
        "selected_candidate_path_id": "path-cache",
        "selected_candidate": candidates["path-cache"],
        "selected_evidence_records": [
            final_evidence(session, candidates["path-cache"], records["path-cache"])
        ],
        "resource_use": synthesis_usage(),
        "information_gain": 1.0,
    }

    first = session.synthesize(**arguments)
    event_count = len(engine.events.events(session.run_id))
    branch_retry = session.close_branch(
        "path-cache",
        status="completed",
        candidate=candidates["path-cache"],
        evidence_records=[records["path-cache"]],
        criterion_results=criterion_result(),
        veto_results=[],
        resource_use=close_usage(),
        information_gain=1.0,
    )
    second = session.synthesize(**arguments)

    assert branch_retry.ready_for_synthesis is True
    assert second == first
    assert len(engine.events.events(session.run_id)) == event_count


def test_material_tie_escalates_and_preserves_all_elimination_reasons() -> None:
    _, _, _, engine, session = compiled_session()
    close_two_branches(session)

    outcome = session.synthesize(
        decision="tie",
        reviewed_candidate_path_ids=["path-cache", "path-parser"],
        elimination_reasons={
            "path-cache": "material tie",
            "path-parser": "material tie",
        },
        minority_findings=[],
        synthesis_basis={"tie": True},
        resource_use=synthesis_usage(),
        information_gain=1.0,
    )

    assert outcome.next_action == "escalate_material_tie"
    assert engine.snapshot(session.run_id).state is WorkflowState.ESCALATED


def test_selected_candidate_validation_closes_to_normative_terminal_result() -> None:
    session, record = synthesized_session()
    outcomes, result_fields = finalization_arguments(record)

    first = session.finalize_selected_candidate(outcomes, **result_fields)
    assert first.state is WorkflowState.COMPLETED
    assert first.next_action == "terminal_result_sealed"
    assert len(first.validation_ids) == 2
    assert first.release_gate_failures == ()
    assert first.result is not None
    validate_reasoning_result(first.result, contract=session.contract)
    event_count = len(session.engine.events.events(session.run_id))

    retry = session.finalize_selected_candidate(outcomes, **result_fields)
    assert retry.result == first.result
    assert retry.validation_ids == first.validation_ids
    assert len(session.engine.events.events(session.run_id)) == event_count


def test_finalization_reports_missing_gate_then_resumes_with_remaining_validator() -> None:
    session, record = synthesized_session()
    outcomes, result_fields = finalization_arguments(record)

    blocked = session.finalize_selected_candidate(outcomes[:1], **result_fields)
    assert blocked.state is WorkflowState.VALIDATING
    assert blocked.next_action == "repair_release_gate"
    assert any("human-reviewer-1" in item for item in blocked.release_gate_failures)
    assert blocked.result is None

    completed = session.finalize_selected_candidate(outcomes[1:], **result_fields)
    assert completed.state is WorkflowState.COMPLETED
    assert completed.result is not None


def test_repairable_final_validator_stops_before_terminal_result() -> None:
    session, record = synthesized_session()
    _, result_fields = finalization_arguments(record)

    outcome = session.finalize_selected_candidate(
        [
            {
                "validator_id": "validator-1",
                "status": "repairable_failure",
                "details": {"failed_check": "candidate consistency"},
            }
        ],
        **result_fields,
    )
    assert outcome.state is WorkflowState.REPAIRABLE_FAILURE
    assert outcome.next_action == "repair_selected_candidate"
    assert outcome.result is None


def test_material_tie_exact_retry_is_idempotent() -> None:
    _, _, _, engine, session = compiled_session()
    close_two_branches(session)
    arguments = {
        "decision": "tie",
        "reviewed_candidate_path_ids": ["path-cache", "path-parser"],
        "elimination_reasons": {
            "path-cache": "material tie",
            "path-parser": "material tie",
        },
        "minority_findings": [],
        "synthesis_basis": {"tie": True},
        "resource_use": synthesis_usage(),
        "information_gain": 1.0,
    }

    first = session.synthesize(**arguments)
    event_count = len(engine.events.events(session.run_id))
    second = session.synthesize(**arguments)

    assert second == first
    assert len(engine.events.events(session.run_id)) == event_count


def test_identical_candidate_outputs_remain_observable_as_false_diversity() -> None:
    _, _, _, engine, session = compiled_session()
    close_two_branches(session, same_candidate=True)

    outcome = session.synthesize(
        decision="tie",
        reviewed_candidate_path_ids=["path-cache", "path-parser"],
        elimination_reasons={"path-cache": "identical result", "path-parser": "identical result"},
        minority_findings=[],
        synthesis_basis={"false_diversity": True},
        resource_use=synthesis_usage(),
        information_gain=1.0,
    )

    compared = next(
        event for event in engine.events.events(session.run_id) if event.event_type == "candidate_compared"
    )
    assert outcome.decision == "tie"
    assert compared.payload["candidate_bindings"][0] == compared.payload["candidate_bindings"][1]


def test_private_reasoning_fields_are_rejected_at_blueprint_boundary() -> None:
    contract = parallel_contract()
    blueprint = parallel_blueprint(contract)
    blueprint["branches"][0]["private_chain_of_thought"] = "do not persist"

    with pytest.raises((ParallelFactoryError, PrivateReasoningCaptureError)):
        ReasoningParallelFactory().compile(blueprint, contract)
