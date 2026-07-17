"""Conformance tests for the governed reasoning runtime JSON Schemas.

推理运行时 JSON Schema 的一致性测试。
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import sys

import pytest
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "skills" / "harness-engineering-patterns" / "schemas"
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from reasoning_artifacts import (  # noqa: E402
    ArtifactValidationError,
    artifact_fingerprint,
    build_artifact,
    validate_reasoning_contract,
    validate_reasoning_event,
    validate_reasoning_result,
)
from reasoning_runtime import (  # noqa: E402
    DuplicateEventConflictError,
    FeedbackAuthorizationError,
    FeedbackBlockError,
    ReasoningEngine,
    ValidationGateError,
    ValidationStatus,
    WorkflowState,
    candidate_fingerprint,
)

SCHEMA_NAMES = (
    "normalized-input",
    "reasoning-contract",
    "reasoning-event",
    "reasoning-result",
)
SCHEMAS = {
    name: json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
    for name in SCHEMA_NAMES
}
VALIDATORS = {
    name: Draft202012Validator(schema, format_checker=FormatChecker())
    for name, schema in SCHEMAS.items()
}

NOW = "2026-07-15T08:00:00Z"
LATER = "2026-07-16T08:00:00Z"
HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
HASH_C = "sha256:" + "c" * 64


def binding(identifier: str, digest: str = HASH_A) -> dict[str, object]:
    return {"id": identifier, "version": "1.0.0", "hash": digest}


def observed_binding(identifier: str, digest: str = HASH_A) -> dict[str, object]:
    return {"state": "observed", "value": binding(identifier, digest)}


def configuration(mode: str = "chain") -> dict[str, object]:
    if mode == "direct":
        return {
            "execution_mode": "direct",
            "reasoning_depth": "direct",
            "primary_topology": None,
            "supporting_topologies": ["orchestration"],
        }
    topology = {"chain": "chain", "parallel": "parallel", "iterative": "loop"}[mode]
    return {
        "execution_mode": mode,
        "reasoning_depth": "deliberative",
        "primary_topology": topology,
        "supporting_topologies": ["orchestration"],
    }


def evidence_sufficiency() -> dict[str, object]:
    return {
        "min_independent_sources": 1,
        "required_evidence_types": ["test"],
        "max_source_age_seconds": 3600,
        "min_integrity_score": 0.9,
        "min_claim_coverage_ratio": 1.0,
        "max_unresolved_critical_claims": 0,
        "unknown_source_policy": "reject",
    }


def normalized_input_example() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "normalized_input_id": "normalized-input-1",
        "normalized_input_version": "1.0.0",
        "normalized_input_hash": HASH_A,
        "workflow_id": "workflow-1",
        "request_id": "request-1",
        "received_at": NOW,
        "request": {
            "content_state": {"state": "observed", "value": "核验推理执行流程"},
            "language": "zh-CN",
            "channel": "chat",
        },
        "task": {
            "task_type": "verification",
            "objectives": [
                {
                    "objective_id": "objective-1",
                    "description": "生成可审计结果",
                    "priority": "required",
                }
            ],
            "constraints": [
                {
                    "constraint_id": "constraint-1",
                    "field_path": "/output/format",
                    "operator": "eq",
                    "value": "json",
                    "severity": "hard",
                }
            ],
            "expected_output": {
                "format": "json",
                "must_include_evidence": True,
                "locale": "zh-CN",
            },
        },
        "risk": {
            "level": "high",
            "dimensions": ["operational"],
            "reversibility": "partially_reversible",
            "requires_human_review": True,
        },
        "reasoning_context": {
            "known_facts": {
                "state": "observed",
                "items": [
                    {
                        "fact_id": "fact-1",
                        "value": {"state": "observed", "value": {"schema_count": 4}},
                        "source_binding": observed_binding("source-1"),
                    },
                    {
                        "fact_id": "fact-zero",
                        "value": {"state": "observed_zero", "value": 0},
                        "source_binding": observed_binding("source-2", HASH_B),
                    },
                ],
            },
            "assumptions": {
                "state": "observed",
                "items": [
                    {
                        "assumption_id": "assumption-1",
                        "statement": {"state": "observed", "value": "输入结构保持稳定"},
                        "status": "unverified",
                        "source_binding": {"state": "unknown"},
                    }
                ],
            },
            "claims_to_verify": {
                "state": "observed",
                "items": [
                    {
                        "claim_id": "claim-1",
                        "statement": {"state": "observed", "value": "所有强制验证器均通过"},
                        "criticality": "critical",
                        "required_evidence_types": ["test"],
                    }
                ],
            },
            "preferences": {
                "state": "observed",
                "items": [
                    {
                        "preference_id": "preference-1",
                        "field_path": "/output/locale",
                        "desired_value": {"state": "observed", "value": "zh-CN"},
                        "strength": "preferred",
                    }
                ],
            },
            "evidence_requirement": {
                "state": "observed",
                "value": {
                    "required_evidence_types": ["test"],
                    "min_independent_sources": 1,
                    "max_source_age_seconds": 3600,
                    "min_integrity_score": 0.9,
                    "unknown_source_policy": "reject",
                },
            },
            "deadline": {"state": "unknown"},
        },
        "permission_context": {
            "actor": {
                "state": "observed",
                "value": {
                    "actor_id": "agent-1",
                    "actor_type": "agent",
                    "actor_version": "runtime-1.0.0",
                },
            },
            "grant": observed_binding("grant-1"),
            "allowed_actions": {
                "state": "observed",
                "items": ["read", "validate"],
            },
            "resource_scope": {
                "state": "observed",
                "items": ["workspace:schemas"],
            },
            "expires_at": {"state": "observed", "value": LATER},
        },
        "available_capabilities": [
            {
                "capability_id": "validator-1",
                "kind": "validator",
                "availability": "available",
                "version": "1.0.0",
            }
        ],
        "field_provenance": [
            {
                "field_path": "/request/content_state",
                "source_type": "user",
                "source_ref": "request-1",
                "observed_at": NOW,
                "integrity_hash": HASH_A,
                "value_state": "observed",
            }
        ],
    }


def validator_spec(*, required: bool = True, on_error: str = "fail_closed") -> dict[str, object]:
    return {
        "validator_id": "validator-1",
        "validator_version": "1.0.0",
        "validator_type": "deterministic",
        "required": required,
        "applicability": {"aggregation": "all", "predicates": []},
        "pass_criteria": {
            "aggregation": "all",
            "checks": [
                {
                    "check_id": "check-1",
                    "predicate": {
                        "field_path": "/candidate/valid",
                        "operator": "eq",
                        "expected": True,
                    },
                    "severity": "fatal",
                    "weight": 1.0,
                }
            ],
        },
        "timeout_ms": 1000,
        "on_error": on_error,
    }


def human_validator_spec() -> dict[str, object]:
    spec = validator_spec()
    spec["validator_id"] = "human-reviewer-1"
    spec["validator_type"] = "human"
    spec["pass_criteria"]["checks"][0]["check_id"] = "human-approval"
    spec["pass_criteria"]["checks"][0]["predicate"] = {
        "field_path": "/candidate/human_approved",
        "operator": "eq",
        "expected": True,
    }
    return spec


def reasoning_contract_example(risk_level: str = "high") -> dict[str, object]:
    selected = configuration("chain")
    validators = [validator_spec()]
    if risk_level in {"high", "critical"}:
        validators.append(human_validator_spec())
    return {
        "schema_version": "1.0.0",
        "contract_id": "contract-1",
        "contract_version": "1.0.0",
        "contract_hash": HASH_B,
        "workflow_id": "workflow-1",
        "task_id": "task-1",
        "run_id": "run-1",
        "scene_id": "scene-1",
        "normalized_input_binding": binding("normalized-input-1", HASH_A),
        "created_at": NOW,
        "routing_decision": {
            "decision_id": "route-decision-1",
            "policy_binding": binding("routing-policy-1"),
            "disposition": "execute",
            "signals": [
                {"signal": "complexity", "value": {"state": "observed", "value": "high"}},
                {
                    "signal": "evidence_availability",
                    "value": {"state": "observed", "value": "available"},
                },
            ],
            "reasons": [
                {
                    "reason_code": "multi_step_dependency",
                    "source_binding": binding("routing-policy-1"),
                }
            ],
            "selected_configuration": selected,
            "signal_fingerprint": HASH_A,
            "missing_signals": [],
            "abstained": False,
        },
        "snapshot_versions": {"goal": 1, "constraints": 1, "verified_facts": 1},
        **selected,
        "budget": {
            "max_reasoning_tokens": 4096,
            "max_latency_ms": 30000,
            "max_model_calls": 8,
            "max_tool_calls": 8,
            "max_parallel_paths": 2,
            "max_iterations": 6,
            "max_retries": 2,
            "max_total_cost_units": 10.0,
            "cost_unit": "compute_credit",
            "enforcement": "hard",
            "parallel_reservation_policy": "reserve_before_launch",
            "on_exhaustion": "escalate",
        },
        "validators": validators,
        "evidence_sufficiency": evidence_sufficiency(),
        "stop_conditions": [
            {
                "condition_id": "stop-success",
                "type": "validated_success",
                "on_trigger": "complete",
            },
            {
                "condition_id": "stop-no-progress",
                "type": "no_progress",
                "consecutive_steps": 2,
                "min_information_gain": 0.01,
                "on_trigger": "escalate",
            },
        ],
        "escalation_conditions": [
            {
                "condition_id": "escalate-evidence",
                "trigger": "insufficient_evidence",
                "severity": "error",
                "threshold": {
                    "metric": "evidence_coverage",
                    "operator": "lt",
                    "value": 1.0,
                },
                "action": "request_evidence",
            }
        ],
        "allowed_mode_switches": [],
        "governance": {
            "risk_level": risk_level,
            "validator_failure_policy": "fail_closed",
            "probe_failure_policy": "degrade_and_alert",
            "human_review_required": risk_level in {"high", "critical"},
        },
    }


def evidence_record() -> dict[str, object]:
    record: dict[str, object] = {
        "evidence_id": "evidence-1",
        "evidence_version": "1.0.0",
        "evidence_hash": HASH_C,
        "candidate_binding": observed_binding("candidate-1", HASH_B),
        "contract_binding": binding("contract-1", HASH_B),
        "evidence_type": "test",
        "claim_bindings": [
            {"claim_id": "claim-1", "relation": "supports", "criticality": "critical"}
        ],
        "source": {
            "source_type": "test",
            "source_ref": "pytest:test_release_gate",
            "source_version": "1.0.0",
        },
        "valid_at": NOW,
        "retrieved_at": NOW,
        "captured_at": NOW,
        "scope": {"workflow_id": "workflow-1", "claim_ids": ["claim-1"]},
        "freshness": {"status": "fresh", "assessed_at": NOW, "age_seconds": 0},
        "integrity_score": 1.0,
        "sensitivity": "internal",
        "redaction_state": "not_required",
        "transformation_history": [],
    }
    record["record_hash"] = artifact_fingerprint(record, "record_hash")
    return record


def validation_record(result: str = "passed") -> dict[str, object]:
    record: dict[str, object] = {
        "validation_id": "validation-1",
        "validation_version": "1.0.0",
        "validation_hash": HASH_A,
        "details_hash": HASH_C,
        "validator_binding": binding("validator-1"),
        "criteria_binding": binding("validator-criteria-1", HASH_C),
        "candidate_binding": binding("candidate-1", HASH_B),
        "contract_binding": binding("contract-1", HASH_B),
        "evidence_bindings": [binding("evidence-1", HASH_C)],
        "independence_class": "deterministic",
        "started_at": NOW,
        "ended_at": NOW,
        "timeout_ms": 1000,
        "attempt": 1,
        "actor_binding": {"state": "unknown"},
        "authority_binding": {"state": "unknown"},
        "result": result,
        "checked_at": NOW,
        "findings": [],
    }
    if result == "conditionally_passed":
        record["conditional_obligations"] = [
            {"obligation_id": "obligation-1", "due_state": "completed"}
        ]
    return record


def step_record(status: str = "completed") -> dict[str, object]:
    record: dict[str, object] = {
        "step_id": "step-1",
        "step_version": "1.0.0",
        "step_hash": HASH_B,
        "candidate_binding": observed_binding("candidate-1", HASH_B),
        "contract_binding": binding("contract-1", HASH_B),
        "sequence_number": 1,
        "attempt_number": 1,
        "status": status,
        "summary": "执行外部可核验检查",
        "claim": "候选必须通过确定性验证",
        "action": "执行确定性测试",
        "observation": {"passed": 8, "failed": 0},
        "local_decision": "候选可以进入放行闸门",
        "resource_use": {
            dimension: {"state": "observed_zero", "value": 0}
            for dimension in BUDGET_DIMENSIONS
        },
        "progress": True,
        "no_progress_streak": 0,
        "input_evidence_bindings": [],
        "output_evidence_bindings": [binding("evidence-1", HASH_C)],
        "validation_bindings": [binding("validation-1", HASH_A)],
        "started_at": NOW,
    }
    if status in {"completed", "failed", "cancelled", "timed_out"}:
        record["ended_at"] = NOW
    record["record_hash"] = artifact_fingerprint(record, "record_hash")
    return record


BUDGET_DIMENSIONS = (
    "reasoning_tokens",
    "latency_ms",
    "model_calls",
    "tool_calls",
    "parallel_paths",
    "iterations",
    "retries",
    "total_cost_units",
)


def budget_accounting() -> dict[str, object]:
    return {
        "limits": {
            dimension: {"state": "observed", "value": 10}
            for dimension in BUDGET_DIMENSIONS
        },
        "used": {
            dimension: {"state": "observed_zero", "value": 0}
            for dimension in BUDGET_DIMENSIONS
        },
        "exhausted_dimensions": [],
    }


def reasoning_result_example() -> dict[str, object]:
    initial = configuration("parallel")
    final = configuration("chain")
    return {
        "schema_version": "1.0.0",
        "result_id": "result-1",
        "result_version": "1.0.0",
        "result_hash": HASH_C,
        "workflow_id": "workflow-1",
        "task_id": "task-1",
        "run_id": "run-1",
        "scene_id": "scene-1",
        "terminal_state": "completed",
        "terminal_reason": {
            "category": "success",
            "code": "completed_validated",
            "source_binding": observed_binding("validator-policy-1"),
        },
        "risk_level": "high",
        "contract_binding": binding("contract-1", HASH_B),
        "candidate_binding": observed_binding("candidate-1", HASH_B),
        "execution": {
            "initial_configuration": initial,
            "final_configuration": final,
            "mode_switches": [
                {
                    "switch_id": "switch-1",
                    "from": initial,
                    "to": final,
                    "trigger": "conflicting_evidence",
                    "switch_rule_binding": binding("switch-rule-1"),
                    "switched_at": NOW,
                }
            ],
        },
        "budget_accounting": budget_accounting(),
        "release_gate": {
            "basis": "mandatory_validators",
            "evidence_sufficiency_met": True,
            "validator_gates": [
                {
                    "validator_binding": binding("validator-1"),
                    "validation_binding": observed_binding("validation-1", HASH_A),
                    "required": True,
                    "result": "passed",
                }
            ],
        },
        "release_gate_evaluated_at": NOW,
        "evidence_bindings": [binding("evidence-1", HASH_C)],
        "evidence": [evidence_record()],
        "steps": [step_record()],
        "validations": [validation_record()],
        "claims": [
            {
                "claim_id": "claim-1",
                "claim_type": "fact",
                "statement": "强制验证器已通过",
                "criticality": "critical",
                "status": "supported",
                "evidence_bindings": [binding("evidence-1", HASH_C)],
            }
        ],
        "final_decision": {
            "state": "observed",
            "value": {"decision": "release_validated_candidate"},
        },
        "unresolved_items": [],
        "next_actions": [],
        "output": {
            "format": "json",
            "content": {"state": "observed", "value": {"status": "verified"}},
            "content_hash": artifact_fingerprint(
                {"state": "observed", "value": {"status": "verified"}}
            ),
        },
        "limitations": [],
        "field_provenance": [
            {
                "field_path": "/output/content",
                "source_type": "validator",
                "source_ref": "validation-1",
                "source_version": "1.0.0",
                "observed_at": NOW,
                "integrity_hash": HASH_A,
                "value_state": "observed",
            }
        ],
        "created_at": NOW,
    }


def failed_before_candidate_result() -> dict[str, object]:
    result = reasoning_result_example()
    result.update(
        {
            "terminal_state": "failed",
            "terminal_reason": {
                "category": "execution",
                "code": "execution_failed",
                "source_binding": {"state": "missing"},
            },
            "risk_level": "medium",
            "candidate_binding": {"state": "missing"},
            "execution": {
                "initial_configuration": configuration("chain"),
                "final_configuration": configuration("chain"),
                "mode_switches": [],
            },
            "release_gate": {
                "basis": "mandatory_validators",
                "evidence_sufficiency_met": False,
                "validator_gates": [],
            },
            "evidence_bindings": [],
            "evidence": [],
            "steps": [],
            "validations": [],
            "claims": [],
            "final_decision": {"state": "unknown"},
            "unresolved_items": [
                {
                    "item_id": "open-execution-failure",
                    "statement": "执行失败原因仍需调查",
                    "criticality": "critical",
                    "blocking": True,
                    "evidence_bindings": [],
                }
            ],
            "next_actions": [
                {
                    "action_id": "investigate-execution-failure",
                    "description": "调查失败事件并补充外部证据",
                    "action_type": "gather_evidence",
                    "authorization_required": False,
                }
            ],
            "output": {
                "format": "json",
                "content": {"state": "unknown"},
                "content_ref": "result-store:failed-before-candidate",
            },
        }
    )
    return result


def resource_values() -> dict[str, object]:
    return {
        name: {"value_state": "observed_zero", "value": 0}
        for name in (
            "model_calls",
            "tool_calls",
            "reasoning_tokens",
            "input_tokens",
            "output_tokens",
            "cost_units",
            "latency_ms",
        )
    }


def human_work_payload(phase: str = "requested") -> dict[str, object]:
    payload: dict[str, object] = {
        "phase": phase,
        "work_type": "review",
        "authority_scope": ["approve_release"],
    }
    if phase == "requested":
        payload.update(
            {
                "recipient": {
                    "queue": "risk-review",
                    "required_capability": "approve-release",
                },
                "service_objective": {
                    "service_level_id": "risk-review-24h",
                    "respond_by": LATER,
                },
                "expires_at": LATER,
                "resume_token_hash": HASH_C,
                "normalized_input_binding": binding("normalized-input-1"),
                "candidate_binding": observed_binding("candidate-1", HASH_B),
                "evidence_bindings": [binding("evidence-1", HASH_C)],
                "unfinished_step_ids": ["step-2"],
                "allowed_decisions": ["approved", "rejected"],
            }
        )
    elif phase == "completed":
        payload.update(
            {
                "decision": "approved",
                "decision_hash": HASH_C,
                "decided_at": LATER,
                "decision_maker_binding": binding("human-reviewer-1"),
                "authority_binding": binding("approval-authority-1"),
            }
        )
    elif phase == "expired":
        payload.update(
            {
                "expired_at": LATER,
                "expiration_reason_code": "service_objective_expired",
                "fallback_action": "fail_closed",
            }
        )
    elif phase == "resumed":
        payload.update(
            {
                "resume_token_hash": HASH_C,
                "normalized_input_binding": binding("normalized-input-1"),
                "candidate_binding": observed_binding("candidate-1", HASH_B),
                "approval_event_id": "event-human-approval-1",
                "resumed_from_run_id": "run-previous",
                "resumed_at": LATER,
                "refreshed_contract_binding": binding("contract-2", HASH_C),
                "refreshed_permission_binding": binding("permission-snapshot-2"),
                "refreshed_budget_binding": binding("budget-snapshot-2"),
                "refreshed_validator_bindings": [binding("validator-2")],
                "refreshed_snapshot_versions": {
                    "goal": 2,
                    "constraints": 2,
                    "verified_facts": 2,
                },
            }
        )
    else:
        raise ValueError(f"unsupported human-work phase: {phase}")
    return payload


def feedback_payload(phase: str = "raised") -> dict[str, object]:
    payload: dict[str, object] = {
        "phase": phase,
        "feedback_id": "feedback-1",
        "revision": 1,
        "probe_binding": binding("probe-1"),
        "severity": "critical",
        "feedback_type": "governance_block",
        "finding_code": "missing_required_validator",
        "related_event_id": "event-validation-completed",
        "rule_binding": binding("feedback-rule-1"),
        "protected_transition": {
            "transition_id": None,
            "from_state": "validating",
            "to_state": "completed",
            "owner_binding": binding("release-orchestrator-1"),
        },
        "blocking": True,
        "validity": "current_run",
    }
    if phase == "raised":
        payload.update(
            {
                "lifecycle_status": "open",
                "finding": "必选验证器尚未产生通过结果",
                "evidence_bindings": [binding("validation-evidence-1")],
                "suggested_actions": ["block", "complete_data"],
                "raised_at": NOW,
            }
        )
    elif phase == "acknowledged":
        payload.update(
            {
                "lifecycle_status": "accepted",
                "response": "accept",
                "response_code": "remediation_scheduled",
                "responded_at": LATER,
                "actor_binding": binding("workflow-owner-1"),
            }
        )
    elif phase == "resolved":
        payload.update(
            {
                "lifecycle_status": "resolved",
                "resolution_code": "validator_completed",
                "resolved_at": LATER,
                "actor_binding": binding("workflow-owner-1"),
                "resolution_evidence_bindings": [binding("validation-evidence-2")],
                "resolution_authority_binding": binding("feedback-resolver-grant-1"),
            }
        )
    elif phase == "exempted":
        payload.update(
            {
                "lifecycle_status": "exempted",
                "exempted_at": LATER,
                "exemption": {
                    "exemption_id": "exemption-1",
                    "approver_binding": binding("human-reviewer-1"),
                    "authority_binding": binding("approval-authority-1"),
                    "scope": ["transition:validating:completed"],
                    "approved_at": NOW,
                    "expires_at": LATER,
                    "compensating_controls": [binding("control-1")],
                    "normalized_input_binding": binding("normalized-input-1"),
                    "contract_binding": binding("contract-1", HASH_B),
                    "candidate_binding": observed_binding("candidate-1", HASH_B),
                    "rule_binding": binding("feedback-rule-1"),
                },
            }
        )
    else:
        raise ValueError(f"unsupported feedback phase: {phase}")
    return payload


def probe_health_payload() -> dict[str, object]:
    zero = {"state": "observed_zero", "value": 0}
    return {
        "probe_binding": binding("probe-1"),
        "health": "healthy",
        "window": {"started_at": NOW, "ended_at": LATER},
        "reconstruction_status": "complete",
        "unreconstructable_reasons": [],
        "received_events": {"state": "observed", "value": 10},
        "expected_events": {"state": "observed", "value": 10},
        "missing_events": deepcopy(zero),
        "duplicate_events": deepcopy(zero),
        "out_of_order_events": deepcopy(zero),
        "parse_failures": deepcopy(zero),
        "calculation_failures": deepcopy(zero),
        "alerts_due": {"state": "observed", "value": 1},
        "alerts_delivered": {"state": "observed", "value": 1},
        "alert_delivery_failures": deepcopy(zero),
        "event_loss_rate": deepcopy(zero),
        "policy_action": "continue",
    }


def event_example(event_type: str = "route_selected") -> dict[str, object]:
    kinds = event_payload_kinds()
    data = event_payload_data()[event_type]
    event: dict[str, object] = {
        "schema_version": "1.0.0",
        "event_version": "1.0.0",
        "event_id": f"event-{event_type}",
        "workflow_id": "workflow-1",
        "contract_binding": binding("contract-1", HASH_B),
        "event_type": event_type,
        "event_processing_status": "accepted",
        "workflow_state": "executing",
        "task_id": "task-1",
        "run_id": "run-1",
        "step_id": None,
        "attempt_id": "attempt-1",
        "sequence": 1,
        "causation_id": None,
        "parent_event_id": None,
        "candidate_path_id": None,
        "tool_call_id": None,
        "human_work_id": None,
        "occurred_at": NOW,
        "emitted_at": NOW,
        "received_at": NOW,
        "idempotency_key": f"run-1:{event_type}:1",
        "scene_id": "scene-1",
        "risk_level": "high",
        "reasoning_depth": "deliberative",
        "execution_mode": "chain",
        "primary_topology": "chain",
        "supporting_topologies": ["orchestration"],
        "snapshot_versions": {"goal": 1, "constraints": 1, "verified_facts": 1},
        "payload": {"kind": kinds[event_type], "data": data},
        "resources": resource_values(),
        "field_provenance": {
            "/event_type": {
                "value_state": "observed",
                "source_type": "system_report",
                "source_id": "reasoning-runtime-1",
                "source_version": "1.0.0",
                "captured_at": NOW,
            }
        },
        "privacy_class": "internal",
        "redaction_state": "not_required",
    }
    if event_type in {"step_started", "step_closed"}:
        event["step_id"] = "step-1"
    if event_type in {"action_dispatched", "action_observed"}:
        event["step_id"] = "step-1"
        event["tool_call_id"] = "tool-call-1"
    if event_type == "state_transitioned":
        event["previous_state"] = "contract_established"
        event["next_state"] = "executing"
        event["transition_id"] = "transition-1"
    if event_type == "human_work_updated":
        event["human_work_id"] = "human-work-1"
    if event_type == "feedback_updated":
        event["idempotency_key"] = "feedback:feedback-1:1"
    if event_type == "run_ended":
        event["workflow_state"] = "completed"
    return event


def event_payload_kinds() -> dict[str, str]:
    return {
        "run_created": "lifecycle",
        "task_received": "lifecycle",
        "task_normalized": "lifecycle",
        "route_selected": "route",
        "contract_established": "lifecycle",
        "state_transitioned": "state_transition",
        "step_started": "step",
        "action_dispatched": "tool",
        "action_observed": "tool",
        "step_closed": "step",
        "evidence_recorded": "evidence",
        "candidate_created": "candidate",
        "candidate_compared": "candidate",
        "iteration_closed": "iteration",
        "mode_switched": "mode",
        "validation_started": "validation",
        "validation_completed": "validation",
        "budget_reserved": "budget",
        "budget_consumed": "budget",
        "budget_released": "budget",
        "budget_exhausted": "budget",
        "no_progress_limit_reached": "iteration",
        "human_work_updated": "human_work",
        "outcome_recorded": "outcome",
        "governance_decided": "governance",
        "feedback_updated": "feedback",
        "probe_health_reported": "probe_health",
        "run_ended": "lifecycle",
    }


def event_payload_data() -> dict[str, dict[str, object]]:
    route_data = {
        "routing_policy_binding": binding("routing-policy-1"),
        "disposition": "execute",
        "configuration": configuration("chain"),
        "signals": [
            {"signal": "complexity", "value": {"state": "observed", "value": "high"}}
        ],
        "reasons": [
            {
                "reason_code": "multi_step_dependency",
                "source_binding": {"state": "not_applicable"},
            }
        ],
        "signal_fingerprint": HASH_A,
        "missing_signals": [],
        "abstained": False,
    }
    budget_base = {
        "dimension": "model_calls",
        "limit": {"state": "observed", "value": 8},
        "consumed": {"state": "observed_zero", "value": 0},
        "remaining": {"state": "observed", "value": 8},
    }
    tool_base = {
        "action_kind": "tool",
        "tool_binding": binding("tool-1"),
        "authorization_policy_binding": binding("tool-policy-1"),
        "authorization_binding": binding("tool-authorization-1"),
        "authorization_verified": True,
        "input_hash": HASH_A,
        "side_effect": False,
    }
    return {
        "run_created": {"normalized_input_binding": binding("normalized-input-1")},
        "task_received": {"stage": "received", "task_binding": binding("task-1")},
        "task_normalized": {
            "stage": "normalized",
            "task_binding": binding("task-1"),
            "normalized_input_binding": binding("normalized-input-1"),
        },
        "route_selected": route_data,
        "contract_established": {
            "contract_binding": binding("contract-1", HASH_B),
            "normalized_input_binding": binding("normalized-input-1"),
        },
        "state_transitioned": {
            "from_state": "contract_established",
            "to_state": "executing",
            "reason_code": "execution_started",
        },
        "step_started": step_record("running"),
        "action_dispatched": {"phase": "started", **tool_base},
        "action_observed": {
            "phase": "completed",
            **tool_base,
            "output_hash": HASH_B,
            "outcome": "succeeded",
        },
        "step_closed": step_record("completed"),
        "evidence_recorded": evidence_record(),
        "candidate_created": {
            "candidate_binding": binding("candidate-1", HASH_B),
            "contract_binding": binding("contract-1", HASH_B),
            "evidence_bindings": [binding("evidence-1", HASH_C)],
        },
        "candidate_compared": {
            "candidate_bindings": [
                binding("candidate-1", HASH_B),
                binding("candidate-2", HASH_C),
            ],
            "comparison_rule_binding": binding("comparison-rule-1"),
            "decision": "selected",
            "selected_candidate_binding": binding("candidate-1", HASH_B),
        },
        "iteration_closed": {
            "iteration_number": 1,
            "candidate_binding": binding("candidate-1", HASH_B),
            "information_gain": {"state": "observed", "value": 0.5},
            "decision": "candidate_ready",
        },
        "mode_switched": {
            "switch_id": "switch-1",
            "from": configuration("parallel"),
            "to": configuration("chain"),
            "trigger": "conflicting_evidence",
            "switch_count": 1,
            "switch_rule_binding": binding("switch-1"),
            "trigger_evidence_bindings": [binding("evidence-1", HASH_C)],
            "budget_impact": {dimension: 0 for dimension in BUDGET_DIMENSIONS},
            "unfinished_step_ids": [],
            "requires_validation": True,
            "switched_at": NOW,
        },
        "validation_started": {
            "validation_id": "validation-1",
            "validator_binding": binding("validator-1"),
            "candidate_binding": binding("candidate-1", HASH_B),
            "contract_binding": binding("contract-1", HASH_B),
            "evidence_bindings": [binding("evidence-1", HASH_C)],
        },
        "validation_completed": validation_record(),
        "budget_reserved": {"operation": "reserve", **budget_base},
        "budget_consumed": {"operation": "consume", **budget_base},
        "budget_released": {"operation": "release", **budget_base},
        "budget_exhausted": {
            "dimension": "model_calls",
            "limit": {"state": "observed", "value": 8},
            "consumed": {"state": "observed", "value": 8},
            "on_exhaustion": "stop",
        },
        "no_progress_limit_reached": {
            "consecutive_steps": 2,
            "configured_limit": 2,
            "minimum_information_gain": 0.01,
            "observed_information_gain": {"state": "observed_zero", "value": 0},
            "on_trigger": "escalate",
        },
        "human_work_updated": human_work_payload("requested"),
        "outcome_recorded": {
            "result_binding": binding("result-1", HASH_C),
            "outcome_state": "correct",
            "source_binding": binding("outcome-source-1"),
            "observed_at": NOW,
        },
        "governance_decided": {
            "risk_level": "high",
            "decision": "human_review",
            "policy_binding": binding("governance-policy-1"),
            "reason_code": "high_risk",
        },
        "feedback_updated": feedback_payload("raised"),
        "probe_health_reported": probe_health_payload(),
        "run_ended": {
            "terminal_state": "completed",
            "reason_code": "completed_validated",
            "result_binding": binding("result-1", HASH_C),
        },
    }


def assert_valid(schema_name: str, instance: object) -> None:
    errors = sorted(VALIDATORS[schema_name].iter_errors(instance), key=lambda error: list(error.path))
    assert not errors, "\n".join(
        f"{list(error.absolute_path)}: {error.message}" for error in errors
    )


def assert_invalid(schema_name: str, instance: object) -> None:
    assert not VALIDATORS[schema_name].is_valid(instance)


@pytest.mark.parametrize("schema_name", SCHEMA_NAMES)
def test_schema_is_draft_2020_12_and_bilingual(schema_name: str) -> None:
    schema = SCHEMAS[schema_name]
    Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["x-contract-version"] == "1.0.0"
    for field in ("title", "description"):
        value = schema[field]
        assert "/" in value
        assert any("\u4e00" <= char <= "\u9fff" for char in value)
        assert any(char.isascii() and char.isalpha() for char in value)


def test_complete_normalized_input_example_is_valid() -> None:
    assert_valid("normalized-input", normalized_input_example())


def test_normalized_input_requires_stateful_unknowns_and_permissions() -> None:
    instance = normalized_input_example()
    instance["reasoning_context"]["deadline"] = None
    assert_invalid("normalized-input", instance)

    instance = normalized_input_example()
    instance["permission_context"]["allowed_actions"] = ["read"]
    assert_invalid("normalized-input", instance)

    instance = normalized_input_example()
    instance["reasoning_context"]["known_facts"] = {"state": "unknown", "items": []}
    assert_invalid("normalized-input", instance)

    instance = normalized_input_example()
    instance["reasoning_context"]["evidence_requirement"] = {"state": "unknown"}
    assert_valid("normalized-input", instance)


def test_normalized_input_observed_zero_is_not_missing() -> None:
    instance = normalized_input_example()
    fact = instance["reasoning_context"]["known_facts"]["items"][1]
    fact["value"] = {"state": "missing", "value": 0}
    assert_invalid("normalized-input", instance)

    instance = normalized_input_example()
    fact = instance["reasoning_context"]["known_facts"]["items"][1]
    fact["value"] = {"state": "observed", "value": 0}
    assert_invalid("normalized-input", instance)


def test_complete_reasoning_contract_example_is_valid() -> None:
    assert_valid("reasoning-contract", reasoning_contract_example())


@pytest.mark.parametrize(
    "budget_field",
    (
        "max_reasoning_tokens",
        "max_latency_ms",
        "max_model_calls",
        "max_tool_calls",
        "max_parallel_paths",
        "max_iterations",
        "max_retries",
        "max_total_cost_units",
    ),
)
def test_numeric_budget_rejects_zero_and_accepts_null(budget_field: str) -> None:
    zero = reasoning_contract_example()
    zero["budget"][budget_field] = 0
    assert_invalid("reasoning-contract", zero)

    unconfigured = reasoning_contract_example()
    unconfigured["budget"][budget_field] = None
    assert_valid("reasoning-contract", unconfigured)


@pytest.mark.parametrize("risk_level", ("high", "critical"))
def test_high_risk_requires_required_fail_closed_validator(risk_level: str) -> None:
    valid = reasoning_contract_example(risk_level)
    assert_valid("reasoning-contract", valid)

    missing_required = reasoning_contract_example(risk_level)
    missing_required["validators"] = [validator_spec(required=False)]
    assert_invalid("reasoning-contract", missing_required)

    fail_open = reasoning_contract_example(risk_level)
    fail_open["validators"] = [validator_spec(on_error="fail_open")]
    assert_invalid("reasoning-contract", fail_open)


def test_routing_decision_rejects_free_text_confidence() -> None:
    instance = reasoning_contract_example()
    instance["routing_decision"]["confidence"] = "very confident"
    assert_invalid("reasoning-contract", instance)


def test_direct_release_rule_is_versioned_and_low_risk_only() -> None:
    contract = reasoning_contract_example("low")
    direct = configuration("direct")
    contract.update(direct)
    contract["routing_decision"]["selected_configuration"] = direct
    contract["routing_decision"]["reasons"] = [
        {
            "reason_code": "direct_low_risk_release",
            "source_binding": binding("routing-policy-1"),
        }
    ]
    contract["validators"] = []
    contract["direct_release_rule"] = {
        "rule_id": "direct-release-rule-1",
        "rule_version": "1.0.0",
        "allowed_risk_levels": ["low"],
        "predicate": {"field_path": "/risk/level", "operator": "eq", "expected": "low"},
        "criteria_version": "1.0.0",
        "required_evidence": evidence_sufficiency(),
        "validator_exemption_basis": {
            "basis": "low_risk_reversible",
            "policy_binding": binding("direct-release-policy-1"),
        },
    }
    assert_valid("reasoning-contract", contract)

    contract["governance"]["risk_level"] = "high"
    contract["governance"]["human_review_required"] = True
    assert_invalid("reasoning-contract", contract)


@pytest.mark.parametrize("event_type", tuple(event_payload_kinds()))
def test_every_event_type_has_one_valid_unified_payload(event_type: str) -> None:
    assert_valid("reasoning-event", event_example(event_type))


@pytest.mark.parametrize("event_type", tuple(event_payload_kinds()))
def test_event_type_rejects_mismatched_payload_kind(event_type: str) -> None:
    event = event_example(event_type)
    expected = event_payload_kinds()[event_type]
    event["payload"]["kind"] = "governance" if expected != "governance" else "route"
    assert_invalid("reasoning-event", event)


@pytest.mark.parametrize(
    "field",
    ("claim", "action", "observation", "local_decision", "resource_use", "progress", "ended_at"),
)
def test_step_closed_requires_a_complete_closure_record(field: str) -> None:
    event = event_example("step_closed")
    del event["payload"]["data"][field]
    assert_invalid("reasoning-event", event)


@pytest.mark.parametrize("field", ("claim", "action", "observation", "local_decision"))
def test_step_closed_rejects_null_or_empty_closure_values(field: str) -> None:
    event = event_example("step_closed")
    event["payload"]["data"][field] = None
    assert_invalid("reasoning-event", event)

    event["payload"]["data"][field] = ""
    assert_invalid("reasoning-event", event)


def test_running_step_rejects_an_end_timestamp() -> None:
    event = event_example("step_started")
    event["payload"]["data"]["ended_at"] = LATER
    assert_invalid("reasoning-event", event)


@pytest.mark.parametrize(
    "event_type",
    ("step_started", "step_closed", "action_dispatched", "action_observed"),
)
def test_step_and_action_events_require_a_non_null_step_id(event_type: str) -> None:
    event = event_example(event_type)
    event["step_id"] = None
    assert_invalid("reasoning-event", event)


def test_action_observed_requires_outcome_and_success_output_hash() -> None:
    event = event_example("action_observed")
    del event["payload"]["data"]["outcome"]
    assert_invalid("reasoning-event", event)

    event = event_example("action_observed")
    del event["payload"]["data"]["output_hash"]
    assert_invalid("reasoning-event", event)

    event = event_example("action_observed")
    event["payload"]["data"]["outcome"] = "failed"
    del event["payload"]["data"]["output_hash"]
    assert_valid("reasoning-event", event)


def test_action_dispatched_rejects_a_premature_outcome() -> None:
    event = event_example("action_dispatched")
    event["payload"]["data"]["outcome"] = "succeeded"
    event["payload"]["data"]["output_hash"] = HASH_B
    assert_invalid("reasoning-event", event)


def test_tool_action_rejects_side_effects() -> None:
    event = event_example("action_dispatched")
    event["payload"]["data"]["side_effect"] = True
    assert_invalid("reasoning-event", event)


@pytest.mark.parametrize(
    "field",
    (
        "authorization_policy_binding",
        "authorization_binding",
        "authorization_verified",
    ),
)
def test_tool_action_requires_verified_authorization_bindings(field: str) -> None:
    event = event_example("action_dispatched")
    del event["payload"]["data"][field]
    assert_invalid("reasoning-event", event)

    event = event_example("action_dispatched")
    event["payload"]["data"]["authorization_verified"] = False
    assert_invalid("reasoning-event", event)


@pytest.mark.parametrize("field", ("previous_state", "next_state", "transition_id"))
def test_state_transition_requires_non_null_transition_envelope(field: str) -> None:
    event = event_example("state_transitioned")
    event[field] = None
    assert_invalid("reasoning-event", event)


def test_candidate_selection_requires_exactly_a_selected_candidate_field() -> None:
    event = event_example("candidate_compared")
    del event["payload"]["data"]["selected_candidate_binding"]
    assert_invalid("reasoning-event", event)

    event = event_example("candidate_compared")
    event["payload"]["data"]["decision"] = "tie"
    assert_invalid("reasoning-event", event)

    del event["payload"]["data"]["selected_candidate_binding"]
    assert_valid("reasoning-event", event)


@pytest.mark.parametrize("phase", ("requested", "completed", "expired", "resumed"))
def test_every_human_work_phase_has_a_valid_strict_payload(phase: str) -> None:
    event = event_example("human_work_updated")
    event["payload"]["data"] = human_work_payload(phase)
    assert_valid("reasoning-event", event)


@pytest.mark.parametrize(
    ("phase", "required_field"),
    (
        ("requested", "resume_token_hash"),
        ("requested", "recipient"),
        ("completed", "decision_hash"),
        ("completed", "authority_binding"),
        ("expired", "fallback_action"),
        ("resumed", "approval_event_id"),
        ("resumed", "resumed_from_run_id"),
        ("resumed", "refreshed_permission_binding"),
    ),
)
def test_human_work_phase_rejects_an_incomplete_escalation_package(
    phase: str, required_field: str
) -> None:
    event = event_example("human_work_updated")
    event["payload"]["data"] = human_work_payload(phase)
    del event["payload"]["data"][required_field]
    assert_invalid("reasoning-event", event)


def test_human_work_rejects_fields_from_another_lifecycle_phase() -> None:
    event = event_example("human_work_updated")
    event["payload"]["data"] = human_work_payload("completed")
    event["payload"]["data"]["recipient"] = {
        "queue": "risk-review",
        "required_capability": "approve-release",
    }
    assert_invalid("reasoning-event", event)


@pytest.mark.parametrize("phase", ("raised", "acknowledged", "resolved", "exempted"))
def test_every_feedback_phase_has_a_valid_strict_payload(phase: str) -> None:
    event = event_example("feedback_updated")
    event["payload"]["data"] = feedback_payload(phase)
    event["idempotency_key"] = f"feedback:feedback-1:{event['payload']['data']['revision']}"
    assert_valid("reasoning-event", event)


@pytest.mark.parametrize(
    "required_field",
    ("feedback_id", "revision", "rule_binding", "protected_transition"),
)
def test_feedback_requires_identity_revision_rule_and_protected_transition(
    required_field: str,
) -> None:
    event = event_example("feedback_updated")
    del event["payload"]["data"][required_field]
    assert_invalid("reasoning-event", event)


def test_feedback_rejects_fields_from_another_lifecycle_phase() -> None:
    event = event_example("feedback_updated")
    event["payload"]["data"]["response_code"] = "not_yet_acknowledged"
    assert_invalid("reasoning-event", event)


def test_feedback_acknowledgement_status_must_match_response() -> None:
    event = event_example("feedback_updated")
    event["payload"]["data"] = feedback_payload("acknowledged")
    event["payload"]["data"]["lifecycle_status"] = "ignored"
    assert_invalid("reasoning-event", event)


def test_feedback_resolution_requires_explicit_authority_binding() -> None:
    event = event_example("feedback_updated")
    event["payload"]["data"] = feedback_payload("resolved")
    del event["payload"]["data"]["resolution_authority_binding"]

    assert_invalid("reasoning-event", event)

    event = event_example("feedback_updated")
    event["payload"]["data"] = feedback_payload("resolved")
    event["payload"]["data"]["resolution_evidence_bindings"] = []
    assert_invalid("reasoning-event", event)


def test_feedback_info_cannot_block_and_only_critical_feedback_can_block() -> None:
    event = event_example("feedback_updated")
    event["payload"]["data"]["severity"] = "info"
    assert_invalid("reasoning-event", event)

    event = event_example("feedback_updated")
    event["payload"]["data"]["severity"] = "warning"
    assert_invalid("reasoning-event", event)

    event["payload"]["data"]["blocking"] = False
    assert_valid("reasoning-event", event)


@pytest.mark.parametrize(
    "required_field",
    ("authority_binding", "expires_at", "compensating_controls", "rule_binding"),
)
def test_feedback_exemption_requires_scoped_authorized_version_bindings(
    required_field: str,
) -> None:
    event = event_example("feedback_updated")
    event["payload"]["data"] = feedback_payload("exempted")
    del event["payload"]["data"]["exemption"][required_field]
    assert_invalid("reasoning-event", event)


@pytest.mark.parametrize(
    "counter",
    (
        "received_events",
        "expected_events",
        "missing_events",
        "duplicate_events",
        "out_of_order_events",
        "parse_failures",
        "calculation_failures",
        "alerts_due",
        "alerts_delivered",
        "alert_delivery_failures",
    ),
)
def test_probe_health_requires_every_reconstruction_counter(counter: str) -> None:
    event = event_example("probe_health_reported")
    del event["payload"]["data"][counter]
    assert_invalid("reasoning-event", event)


def test_probe_health_complete_window_rejects_unknown_or_ambiguous_zero_counts() -> None:
    event = event_example("probe_health_reported")
    event["payload"]["data"]["duplicate_events"] = {"state": "unknown"}
    assert_invalid("reasoning-event", event)

    event = event_example("probe_health_reported")
    event["payload"]["data"]["duplicate_events"] = {
        "state": "observed",
        "value": 0,
    }
    assert_invalid("reasoning-event", event)


def test_probe_health_partial_window_names_what_cannot_be_reconstructed() -> None:
    event = event_example("probe_health_reported")
    data = event["payload"]["data"]
    data["health"] = "degraded"
    data["reconstruction_status"] = "partial"
    data["duplicate_events"] = {"state": "unknown"}
    data["unreconstructable_reasons"] = ["duplicate_state_missing"]
    data["policy_action"] = "degrade_and_alert"
    assert_valid("reasoning-event", event)

    data["unreconstructable_reasons"] = []
    assert_invalid("reasoning-event", event)


def test_event_rejects_legacy_bare_payload() -> None:
    event = event_example("route_selected")
    event["payload"] = event["payload"]["data"]
    assert_invalid("reasoning-event", event)


def test_event_processing_status_is_separate_from_workflow_state() -> None:
    event = event_example()
    event["event_processing_status"] = "completed"
    assert_invalid("reasoning-event", event)

    event = event_example()
    event["workflow_state"] = "accepted"
    assert_invalid("reasoning-event", event)


def test_event_resource_missing_unknown_and_zero_are_distinct() -> None:
    event = event_example()
    event["resources"]["model_calls"] = {"value_state": "missing", "value": 0}
    assert_invalid("reasoning-event", event)

    event = event_example()
    event["resources"]["model_calls"] = {"value_state": "observed", "value": 0}
    assert_invalid("reasoning-event", event)

    event = event_example()
    event["resources"]["model_calls"] = {"value_state": "observed_zero"}
    assert_invalid("reasoning-event", event)

    event = event_example()
    event["resources"]["model_calls"] = {"value_state": "observed", "value": -1}
    assert_invalid("reasoning-event", event)


def test_event_budget_limit_must_be_positive_or_explicitly_unconfigured() -> None:
    event = event_example("budget_reserved")
    event["payload"]["data"]["limit"] = {"state": "observed_zero", "value": 0}
    assert_invalid("reasoning-event", event)

    event = event_example("budget_reserved")
    event["payload"]["data"]["limit"] = {"state": "not_applicable"}
    assert_valid("reasoning-event", event)


@pytest.mark.parametrize("schema_name", SCHEMA_NAMES)
@pytest.mark.parametrize(
    "private_key",
    (
        "chain_of_thought",
        "Private_CoT",
        "HIDDEN_REASONING",
        "internal_monologue",
        "Reasoning_Scratchpad",
        "SCRATCHPAD",
    ),
)
def test_safe_external_value_recursively_rejects_private_reasoning_keys(
    schema_name: str, private_key: str
) -> None:
    schema = SCHEMAS[schema_name]
    fragment = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "#/$defs/SafeExternalValue",
        "$defs": schema["$defs"],
    }
    validator = Draft202012Validator(fragment)
    assert validator.is_valid({"outer": [{"safe": True}]})
    assert not validator.is_valid({"outer": [{private_key: "secret"}]})


def test_complete_mandatory_validator_result_is_valid() -> None:
    assert_valid("reasoning-result", reasoning_result_example())


def test_completed_direct_release_result_is_valid_only_for_low_risk() -> None:
    result = reasoning_result_example()
    result["risk_level"] = "low"
    result["terminal_reason"]["code"] = "completed_direct_release"
    result["release_gate"] = {
        "basis": "direct_release_rule",
        "evidence_sufficiency_met": True,
        "direct_rule_binding": binding("direct-release-rule-1"),
    }
    result["validations"] = []
    assert_valid("reasoning-result", result)

    result["risk_level"] = "medium"
    assert_invalid("reasoning-result", result)


@pytest.mark.parametrize(
    ("terminal_state", "category", "code"),
    (
        ("rejected", "policy", "policy_rejected"),
        ("failed", "execution", "execution_failed"),
        ("escalated", "human", "human_escalation"),
        ("cancelled", "cancellation", "user_cancelled"),
        ("timed_out", "timeout", "execution_timed_out"),
    ),
)
def test_noncompleted_result_before_candidate_is_valid(
    terminal_state: str, category: str, code: str
) -> None:
    result = failed_before_candidate_result()
    result["terminal_state"] = terminal_state
    result["terminal_reason"] = {
        "category": category,
        "code": code,
        "source_binding": {"state": "missing"},
    }
    assert_valid("reasoning-result", result)


def test_completed_result_requires_candidate_and_evidence_gate() -> None:
    result = reasoning_result_example()
    result["candidate_binding"] = {"state": "missing"}
    assert_invalid("reasoning-result", result)

    result = reasoning_result_example()
    result["release_gate"]["evidence_sufficiency_met"] = False
    assert_invalid("reasoning-result", result)

    result = reasoning_result_example()
    del result["release_gate_evaluated_at"]
    assert_invalid("reasoning-result", result)


def test_conditionally_passed_never_substitutes_for_required_pass() -> None:
    result = reasoning_result_example()
    gate = result["release_gate"]["validator_gates"][0]
    gate["result"] = "conditionally_passed"
    assert_invalid("reasoning-result", result)

    result = reasoning_result_example()
    result["release_gate"]["validator_gates"].append(
        {
            "validator_binding": binding("optional-validator-1"),
            "validation_binding": observed_binding("optional-validation-1"),
            "required": False,
            "result": "conditionally_passed",
        }
    )
    assert_valid("reasoning-result", result)


def test_result_requires_structured_terminal_reason() -> None:
    result = reasoning_result_example()
    del result["terminal_reason"]
    assert_invalid("reasoning-result", result)

    result = reasoning_result_example()
    result["terminal_reason"] = "looks good"
    assert_invalid("reasoning-result", result)

    result = failed_before_candidate_result()
    result["terminal_reason"] = {
        "category": "success",
        "code": "completed_validated",
        "source_binding": {"state": "missing"},
    }
    assert_invalid("reasoning-result", result)


def test_result_budget_limit_and_usage_states_are_strict() -> None:
    result = reasoning_result_example()
    result["budget_accounting"]["limits"]["model_calls"] = {
        "state": "observed",
        "value": 0,
    }
    assert_invalid("reasoning-result", result)

    result = reasoning_result_example()
    result["budget_accounting"]["used"]["model_calls"] = {
        "state": "observed",
        "value": 0,
    }
    assert_invalid("reasoning-result", result)


def test_result_output_rejects_nested_private_reasoning() -> None:
    result = reasoning_result_example()
    result["output"]["content"] = {
        "state": "observed",
        "value": {"public": {"internal_monologue": "secret"}},
    }
    assert_invalid("reasoning-result", result)


def test_completed_result_requires_an_observed_final_decision() -> None:
    result = reasoning_result_example()
    result["final_decision"] = {"state": "unknown"}
    assert_invalid("reasoning-result", result)


def test_completed_result_rejects_a_blocking_critical_unresolved_item() -> None:
    result = reasoning_result_example()
    result["unresolved_items"] = [
        {
            "item_id": "critical-open-item",
            "statement": "关键证据尚未闭合",
            "criticality": "critical",
            "blocking": True,
            "evidence_bindings": [],
        }
    ]
    assert_invalid("reasoning-result", result)


def test_supported_fact_requires_evidence_and_explicit_claim_type() -> None:
    result = reasoning_result_example()
    result["claims"][0]["evidence_bindings"] = []
    assert_invalid("reasoning-result", result)

    result = reasoning_result_example()
    del result["claims"][0]["claim_type"]
    assert_invalid("reasoning-result", result)


def sealed_contract(*, minimum_sources: int = 1) -> dict[str, object]:
    contract = reasoning_contract_example()
    contract["evidence_sufficiency"]["min_independent_sources"] = minimum_sources
    contract.pop("contract_hash")
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
    return contract


def sealed_direct_contract() -> dict[str, object]:
    contract = reasoning_contract_example("low")
    direct = configuration("direct")
    contract.update(direct)
    contract["routing_decision"]["selected_configuration"] = direct
    contract["routing_decision"]["reasons"] = [
        {
            "reason_code": "direct_low_risk_release",
            "source_binding": binding("routing-policy-1"),
        }
    ]
    contract["validators"] = []
    contract["direct_release_rule"] = {
        "rule_id": "direct-release-rule-1",
        "rule_version": "1.0.0",
        "allowed_risk_levels": ["low"],
        "predicate": {
            "field_path": "/candidate/verified",
            "operator": "eq",
            "expected": True,
        },
        "criteria_version": "1.0.0",
        "required_evidence": evidence_sufficiency(),
        "validator_exemption_basis": {
            "basis": "low_risk_reversible",
            "policy_binding": binding("direct-release-policy-1"),
        },
    }
    contract.pop("contract_hash")
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
    return contract


def sealed_result(contract: dict[str, object]) -> dict[str, object]:
    result = reasoning_result_example()
    contract_binding = binding(
        contract["contract_id"],
        contract["contract_hash"],
    )
    result["contract_binding"] = contract_binding
    for evidence in result["evidence"]:
        evidence["contract_binding"] = deepcopy(contract_binding)
    for step in result["steps"]:
        step["contract_binding"] = deepcopy(contract_binding)
    for validation in result["validations"]:
        validation["contract_binding"] = deepcopy(contract_binding)
    configuration_value = {
        field: deepcopy(contract[field])
        for field in (
            "execution_mode",
            "reasoning_depth",
            "primary_topology",
            "supporting_topologies",
        )
    }
    result["execution"] = {
        "initial_configuration": deepcopy(configuration_value),
        "final_configuration": deepcopy(configuration_value),
        "mode_switches": [],
    }
    budget_names = {
        "reasoning_tokens": "max_reasoning_tokens",
        "latency_ms": "max_latency_ms",
        "model_calls": "max_model_calls",
        "tool_calls": "max_tool_calls",
        "parallel_paths": "max_parallel_paths",
        "iterations": "max_iterations",
        "retries": "max_retries",
        "total_cost_units": "max_total_cost_units",
    }
    result["budget_accounting"]["limits"] = {
        result_name: (
            {"state": "missing"}
            if contract["budget"][contract_name] is None
            else {"state": "observed", "value": contract["budget"][contract_name]}
        )
        for result_name, contract_name in budget_names.items()
    }
    validations = []
    validator_gates = []
    for index, declared in enumerate(contract["validators"], start=1):
        validation = validation_record()
        validation_id = f"validation-{index}"
        validator_hash = artifact_fingerprint(declared)
        validation["validation_id"] = validation_id
        validation["validator_binding"] = binding(
            declared["validator_id"],
            validator_hash,
        )
        validation["criteria_binding"] = binding(
            f"{declared['validator_id']}-criteria",
            artifact_fingerprint(declared["pass_criteria"]),
        )
        validation["contract_binding"] = deepcopy(contract_binding)
        validation["independence_class"] = (
            "human"
            if declared["validator_type"] == "human"
            else "deterministic"
        )
        validation["timeout_ms"] = declared["timeout_ms"]
        if declared["validator_type"] == "human":
            validation["actor_binding"] = observed_binding("human-reviewer-1")
            validation["authority_binding"] = observed_binding(
                "approval-authority-1"
            )
        validation["validation_hash"] = artifact_fingerprint(
            validation,
            "validation_hash",
        )
        validations.append(validation)
        validator_gates.append(
            {
                "validator_binding": deepcopy(validation["validator_binding"]),
                "validation_binding": observed_binding(
                    validation_id,
                    validation["validation_hash"],
                ),
                "required": declared["required"],
                "result": "passed",
            }
        )
    result["validations"] = validations
    result["release_gate"]["validator_gates"] = validator_gates
    result["steps"][0]["validation_bindings"] = [
        binding(item["validation_id"], item["validation_hash"])
        for item in validations
    ]
    for evidence in result["evidence"]:
        evidence["record_hash"] = artifact_fingerprint(evidence, "record_hash")
    for step in result["steps"]:
        step["record_hash"] = artifact_fingerprint(step, "record_hash")
    result.pop("result_hash")
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    return result


def test_semantic_contract_guard_rejects_two_routing_authorities() -> None:
    contract = sealed_contract()
    validate_reasoning_contract(contract)

    contract["routing_decision"]["selected_configuration"] = configuration("parallel")
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
    with pytest.raises(ArtifactValidationError, match="selected_configuration"):
        validate_reasoning_contract(contract)


def test_semantic_event_guard_binds_transition_payload_to_envelope() -> None:
    event = event_example("state_transitioned")
    validate_reasoning_event(event)

    event["payload"]["data"]["from_state"] = "routed"
    assert_valid("reasoning-event", event)
    with pytest.raises(ArtifactValidationError, match="previous_state"):
        validate_reasoning_event(event)


def test_semantic_result_guard_resolves_gate_bindings_and_evidence_truth() -> None:
    contract = sealed_contract()
    result = sealed_result(contract)
    validate_reasoning_result(result, contract=contract)

    result["release_gate"]["validator_gates"][0]["validation_binding"]["value"][
        "id"
    ] = "missing-validation"
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="unknown validation"):
        validate_reasoning_result(result, contract=contract)

    insufficient_contract = sealed_contract(minimum_sources=2)
    insufficient_result = sealed_result(insufficient_contract)
    with pytest.raises(ArtifactValidationError, match="recomputed evidence gate"):
        validate_reasoning_result(insufficient_result, contract=insufficient_contract)


def test_semantic_result_guard_rejects_missing_human_gate_and_nested_hash_drift() -> None:
    contract = sealed_contract()
    result = sealed_result(contract)
    result["release_gate"]["validator_gates"] = [
        gate
        for gate in result["release_gate"]["validator_gates"]
        if gate["validator_binding"]["id"] != "human-reviewer-1"
    ]
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="mandatory validator gate is missing"):
        validate_reasoning_result(result, contract=contract)

    result = sealed_result(contract)
    result["validations"][0]["details_hash"] = HASH_B
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="validation hash mismatch"):
        validate_reasoning_result(result, contract=contract)


def test_semantic_result_guard_requires_human_actor_and_authority() -> None:
    contract = sealed_contract()
    result = sealed_result(contract)
    human = next(
        validation
        for validation in result["validations"]
        if validation["validator_binding"]["id"] == "human-reviewer-1"
    )
    human["authority_binding"] = {"state": "unknown"}
    human["validation_hash"] = artifact_fingerprint(human, "validation_hash")
    gate = next(
        gate
        for gate in result["release_gate"]["validator_gates"]
        if gate["validator_binding"]["id"] == "human-reviewer-1"
    )
    gate["validation_binding"] = observed_binding(
        human["validation_id"],
        human["validation_hash"],
    )
    result["steps"][0]["validation_bindings"] = [
        binding(validation["validation_id"], validation["validation_hash"])
        for validation in result["validations"]
    ]
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="human validation lacks"):
        validate_reasoning_result(result, contract=contract)


def test_semantic_evidence_gate_requires_supporting_relation() -> None:
    contract = sealed_contract()
    result = sealed_result(contract)
    result["evidence"][0]["claim_bindings"][0]["relation"] = "refutes"
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="recomputed evidence gate"):
        validate_reasoning_result(result, contract=contract)


def test_semantic_result_cannot_backdate_creation_before_release_gate() -> None:
    contract = sealed_contract()
    result = sealed_result(contract)
    result["release_gate_evaluated_at"] = LATER
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="creation predates"):
        validate_reasoning_result(result, contract=contract)


def test_artifact_builder_rejects_supplied_digest_drift() -> None:
    contract = reasoning_contract_example()
    with pytest.raises(ArtifactValidationError, match="does not match content"):
        build_artifact("reasoning_contract", contract)

    contract.pop("contract_hash")
    built = build_artifact("reasoning_contract", contract)
    validate_reasoning_contract(built)


def test_semantic_result_guard_rejects_result_hash_drift() -> None:
    contract = sealed_contract()
    result = sealed_result(contract)
    result["output"]["content"] = {"state": "observed", "value": {"status": "changed"}}
    with pytest.raises(ArtifactValidationError, match="result_hash mismatch"):
        validate_reasoning_result(result, contract=contract)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda result: result["evidence"][0]["scope"].update(
                {"workflow_id": "tampered-workflow"}
            ),
            "evidence record hash mismatch",
        ),
        (
            lambda result: result["steps"][0].update(
                {"observation": {"passed": 0, "failed": 8}}
            ),
            "step record hash mismatch",
        ),
        (
            lambda result: result["output"].update(
                {
                    "content": {
                        "state": "observed",
                        "value": {"status": "tampered"},
                    }
                }
            ),
            "output content hash mismatch",
        ),
    ],
)
def test_semantic_result_guard_recomputes_nested_integrity_hashes(
    mutate: object,
    message: str,
) -> None:
    contract = sealed_contract()
    result = sealed_result(contract)
    mutate(result)
    result["result_hash"] = artifact_fingerprint(result, "result_hash")

    with pytest.raises(ArtifactValidationError, match=message):
        validate_reasoning_result(result, contract=contract)


def test_result_builder_seals_missing_nested_integrity_hashes() -> None:
    contract = sealed_contract()
    result = sealed_result(contract)
    result.pop("result_hash")
    result["evidence"][0].pop("record_hash")
    result["steps"][0].pop("record_hash")
    result["output"].pop("content_hash")

    sealed = build_artifact("reasoning_result", result)

    validate_reasoning_result(sealed, contract=contract)
    assert sealed["evidence"][0]["record_hash"] == artifact_fingerprint(
        sealed["evidence"][0], "record_hash"
    )
    assert sealed["steps"][0]["record_hash"] == artifact_fingerprint(
        sealed["steps"][0], "record_hash"
    )
    assert sealed["output"]["content_hash"] == artifact_fingerprint(
        sealed["output"]["content"]
    )


def test_semantic_result_guard_closes_mode_switch_chain_and_budget_accounting() -> None:
    contract = sealed_contract()
    result = sealed_result(contract)
    result["execution"]["final_configuration"] = configuration("parallel")
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="mode-switch chain"):
        validate_reasoning_result(result, contract=contract)

    result = sealed_result(contract)
    result["budget_accounting"]["used"]["reasoning_tokens"] = {
        "state": "observed",
        "value": contract["budget"]["max_reasoning_tokens"] + 1,
    }
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="budget usage exceeds"):
        validate_reasoning_result(result, contract=contract)

    result = sealed_result(contract)
    result["budget_accounting"]["used"]["reasoning_tokens"] = {
        "state": "observed",
        "value": contract["budget"]["max_reasoning_tokens"],
    }
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="exhausted budget dimensions"):
        validate_reasoning_result(result, contract=contract)


def test_semantic_result_guard_binds_mode_switch_to_contract_rule() -> None:
    contract = sealed_contract()
    switch_rule = {
        "switch_id": "switch-to-parallel",
        "from": configuration("chain"),
        "to": configuration("parallel"),
        "trigger": "conflicting_evidence",
        "max_switches": 1,
        "preserve_budget": True,
        "requires_validation": True,
    }
    contract["allowed_mode_switches"] = [switch_rule]
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
    result = sealed_result(contract)
    result["execution"]["final_configuration"] = deepcopy(switch_rule["to"])
    result["execution"]["mode_switches"] = [
        {
            "switch_id": switch_rule["switch_id"],
            "from": deepcopy(switch_rule["from"]),
            "to": deepcopy(switch_rule["to"]),
            "trigger": switch_rule["trigger"],
            "switch_rule_binding": binding(
                switch_rule["switch_id"],
                artifact_fingerprint(switch_rule),
            ),
            "switched_at": NOW,
        }
    ]
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    validate_reasoning_result(result, contract=contract)

    result["execution"]["mode_switches"][0]["switch_rule_binding"]["hash"] = HASH_B
    result["result_hash"] = artifact_fingerprint(result, "result_hash")
    with pytest.raises(ArtifactValidationError, match="rule binding differs"):
        validate_reasoning_result(result, contract=contract)


def test_runtime_is_created_from_the_normative_contract_without_binding_drift() -> None:
    contract = sealed_contract()
    engine = ReasoningEngine()

    run_id = engine.create_run_from_contract(contract)

    snapshot = engine.snapshot(run_id)
    assert snapshot.state is WorkflowState.EXECUTING
    assert snapshot.contract_hash == contract["contract_hash"]
    assert snapshot.task_id == contract["task_id"]
    assert all(event.as_dict()["workflow_id"] == contract["workflow_id"] for event in engine.events.events(run_id))

    drifted = deepcopy(contract)
    drifted["routing_decision"]["selected_configuration"] = configuration("parallel")
    drifted["contract_hash"] = artifact_fingerprint(drifted, "contract_hash")
    with pytest.raises(ArtifactValidationError, match="selected_configuration"):
        engine.create_run_from_contract(drifted)


def test_runtime_mode_switch_is_allowlisted_audited_and_idempotent() -> None:
    contract = reasoning_contract_example()
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
    contract.pop("contract_hash")
    contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
    evaluated_at = datetime.fromisoformat(NOW.replace("Z", "+00:00")).timestamp()
    engine = ReasoningEngine(clock=lambda: evaluated_at)
    run_id = engine.create_run_from_contract(contract)

    snapshot = engine.switch_mode(
        run_id,
        switch_id="switch-to-parallel",
        trigger="conflicting_evidence",
        trigger_evidence_bindings=[binding("evidence-1", HASH_C)],
        idempotency_key="switch-command-1",
        switched_at=NOW,
    )
    duplicate = engine.switch_mode(
        run_id,
        switch_id="switch-to-parallel",
        trigger="conflicting_evidence",
        trigger_evidence_bindings=[binding("evidence-1", HASH_C)],
        idempotency_key="switch-command-1",
        switched_at=NOW,
    )

    assert snapshot.state is WorkflowState.EXECUTING
    assert duplicate.state is WorkflowState.EXECUTING
    switch_events = [
        event.as_dict()
        for event in engine.events.events(run_id)
        if event.event_type == "mode_switched"
    ]
    assert len(switch_events) == 1
    assert switch_events[0]["execution_mode"] == "parallel"
    assert switch_events[0]["payload"]["data"]["unfinished_step_ids"] == []
    assert switch_events[0]["payload"]["data"]["switch_count"] == 1


def test_runtime_feedback_lifecycle_blocks_and_then_releases_named_transition() -> None:
    contract = sealed_contract()
    evaluated_at = datetime.fromisoformat(NOW.replace("Z", "+00:00")).timestamp()
    authorization_active = {"value": True}

    def authorize_feedback(
        feedback: dict[str, object],
        context: dict[str, object],
    ) -> bool:
        authority = feedback.get("resolution_authority_binding", {})
        return bool(
            authorization_active["value"]
            and feedback["phase"] == "resolved"
            and authority.get("id") == "feedback-resolver-grant-1"
            and context["contract_binding"]["hash"] == contract["contract_hash"]
        )

    engine = ReasoningEngine(
        clock=lambda: evaluated_at,
        feedback_authorizer=authorize_feedback,
    )
    run_id = engine.create_run_from_contract(contract)
    candidate = {"valid": True, "human_approved": True}
    candidate_hash = candidate_fingerprint(candidate)
    record = evidence_record()
    record["candidate_binding"] = {
        "state": "observed",
        "value": ReasoningEngine._candidate_binding(candidate_hash),
    }
    record["contract_binding"] = binding(contract["contract_id"], contract["contract_hash"])
    record["record_hash"] = artifact_fingerprint(record, "record_hash")
    engine.set_candidate(run_id, candidate, evidence=[record])
    for validator_id in ("validator-1", "human-reviewer-1"):
        human_audit = (
            {
                "actor_binding": observed_binding("human-reviewer-1"),
                "authority_binding": observed_binding("approval-authority-1"),
            }
            if validator_id == "human-reviewer-1"
            else {}
        )
        engine.record_validation(
            run_id,
            validator_id=validator_id,
            status=ValidationStatus.PASSED,
            **human_audit,
        )

    raised = feedback_payload("raised")
    first = engine.record_feedback(run_id, raised)
    retry = engine.record_feedback(run_id, raised)
    assert retry.event_id == first.event_id
    release_claims = [
        {
            "claim_id": "claim-1",
            "claim_type": "fact",
            "statement": "强制验证器已通过",
            "criticality": "critical",
            "status": "supported",
            "evidence_bindings": [binding("evidence-1", HASH_C)],
        }
    ]
    with pytest.raises(FeedbackBlockError, match="feedback-1"):
        engine.finalize(run_id, evaluated_at=NOW, claims=release_claims)

    resolved = feedback_payload("resolved")
    resolved["revision"] = 2
    engine.record_feedback(run_id, resolved)
    authorization_active["value"] = False
    assert engine.snapshot(run_id).blocking_feedback_count == 1
    with pytest.raises(FeedbackBlockError, match="feedback-1"):
        engine.finalize(run_id, evaluated_at=NOW, claims=release_claims)

    authorization_active["value"] = True
    assert engine.snapshot(run_id).blocking_feedback_count == 0
    snapshot = engine.finalize(run_id, evaluated_at=NOW, claims=release_claims)
    assert snapshot.state is WorkflowState.COMPLETED


@pytest.mark.parametrize("terminal_phase", ("resolved", "exempted"))
def test_runtime_feedback_resolution_and_exemption_fail_closed_without_live_authorizer(
    terminal_phase: str,
) -> None:
    contract = sealed_contract()
    evaluated_at = datetime.fromisoformat(NOW.replace("Z", "+00:00")).timestamp()
    engine = ReasoningEngine(clock=lambda: evaluated_at)
    run_id = engine.create_run_from_contract(contract)
    engine.record_feedback(run_id, feedback_payload("raised"))
    terminal_update = feedback_payload(terminal_phase)
    terminal_update["revision"] = 2

    with pytest.raises(FeedbackAuthorizationError, match="not live-authorized"):
        engine.record_feedback(run_id, terminal_update)

    assert engine.snapshot(run_id).blocking_feedback_count == 1


def test_runtime_builds_a_schema_and_semantically_valid_terminal_result() -> None:
    contract = sealed_contract()
    evaluated_at = datetime.fromisoformat(NOW.replace("Z", "+00:00")).timestamp()
    engine = ReasoningEngine(clock=lambda: evaluated_at)
    run_id = engine.create_run_from_contract(contract)
    candidate = {"valid": True, "human_approved": True}
    candidate_hash = candidate_fingerprint(candidate)
    candidate_binding = ReasoningEngine._candidate_binding(candidate_hash)
    record = evidence_record()
    record["candidate_binding"] = {
        "state": "observed",
        "value": deepcopy(candidate_binding),
    }
    record["contract_binding"] = binding(contract["contract_id"], contract["contract_hash"])
    record["record_hash"] = artifact_fingerprint(record, "record_hash")

    engine.set_candidate(run_id, candidate, evidence=[record])
    for validator_id in ("validator-1", "human-reviewer-1"):
        human_audit = (
            {
                "actor_binding": observed_binding("human-reviewer-1"),
                "authority_binding": observed_binding("approval-authority-1"),
            }
            if validator_id == "human-reviewer-1"
            else {}
        )
        engine.record_validation(
            run_id,
            validator_id=validator_id,
            status=ValidationStatus.PASSED,
            **human_audit,
        )
    with pytest.raises(ValidationGateError, match="release-bound claims"):
        engine.finalize(run_id, evaluated_at=NOW)
    release_claims = [
        {
            "claim_id": "claim-1",
            "claim_type": "fact",
            "statement": "强制验证器已通过",
            "criticality": "critical",
            "status": "supported",
            "evidence_bindings": [binding("evidence-1", HASH_C)],
        }
    ]
    engine.finalize(run_id, evaluated_at=NOW, claims=release_claims)

    result = engine.build_result(
        run_id,
        claims=release_claims,
        final_decision={"state": "observed", "value": {"decision": "release"}},
        output={
            "format": "json",
            "content": {"state": "observed", "value": {"status": "verified"}},
        },
        field_provenance=[
            {
                "field_path": "/output/content",
                "source_type": "validator",
                "source_ref": "validation-1",
                "value_state": "observed",
            }
        ],
        created_at=NOW,
    )

    assert result["terminal_state"] == "completed"
    assert result["result_hash"] == artifact_fingerprint(result, "result_hash")
    assert len(result["validations"]) == 2
    validate_reasoning_result(result, contract=contract)

    retry = engine.build_result(
        run_id,
        claims=release_claims,
        final_decision={"state": "observed", "value": {"decision": "release"}},
        output={
            "format": "json",
            "content": {"state": "observed", "value": {"status": "verified"}},
        },
        field_provenance=[
            {
                "field_path": "/output/content",
                "source_type": "validator",
                "source_ref": "validation-1",
                "value_state": "observed",
            }
        ],
        created_at=NOW,
    )
    assert retry == result

    with pytest.raises(DuplicateEventConflictError, match="different sealed result"):
        engine.build_result(
            run_id,
            claims=release_claims,
            final_decision={"state": "observed", "value": {"decision": "release"}},
            output={
                "format": "json",
                "content": {"state": "observed", "value": {"status": "changed"}},
            },
            field_provenance=[
                {
                    "field_path": "/output/content",
                    "source_type": "validator",
                    "source_ref": "validation-1",
                    "value_state": "observed",
                }
            ],
            created_at=NOW,
        )


def test_normative_direct_release_uses_schema_evidence_without_aggregate_hacks() -> None:
    contract = sealed_direct_contract()
    evaluated_at = datetime.fromisoformat(NOW.replace("Z", "+00:00")).timestamp()
    engine = ReasoningEngine(clock=lambda: evaluated_at)
    run_id = engine.create_run_from_contract(contract)
    candidate = {"verified": True}
    candidate_hash = candidate_fingerprint(candidate)
    record = evidence_record()
    record["candidate_binding"] = {
        "state": "observed",
        "value": ReasoningEngine._candidate_binding(candidate_hash),
    }
    record["contract_binding"] = binding(
        contract["contract_id"],
        contract["contract_hash"],
    )
    record["record_hash"] = artifact_fingerprint(record, "record_hash")
    engine.set_candidate(run_id, candidate, evidence=[record])
    claims = [
        {
            "claim_id": "claim-1",
            "claim_type": "fact",
            "statement": "候选满足直接放行规则",
            "criticality": "critical",
            "status": "supported",
            "evidence_bindings": [binding("evidence-1", HASH_C)],
        }
    ]
    engine.finalize(run_id, evaluated_at=NOW, claims=claims)

    result = engine.build_result(
        run_id,
        claims=claims,
        final_decision={"state": "observed", "value": {"decision": "release"}},
        output={
            "format": "json",
            "content": {"state": "observed", "value": {"status": "verified"}},
        },
        field_provenance=[
            {
                "field_path": "/output/content",
                "source_type": "derived",
                "source_ref": "direct-release-rule-1",
                "value_state": "observed",
            }
        ],
        created_at=NOW,
    )

    assert result["release_gate"]["basis"] == "direct_release_rule"
    assert datetime.fromisoformat(
        result["release_gate_evaluated_at"].replace("Z", "+00:00")
    ) == datetime.fromisoformat(NOW.replace("Z", "+00:00"))
    validate_reasoning_result(result, contract=contract)
