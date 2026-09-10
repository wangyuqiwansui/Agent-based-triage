"""Source-formula and incomplete-data regressions / 全文算式与缺数回归。"""

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

SKILL = Path(__file__).resolve().parents[1] / "skills/harness-engineering-patterns"
sys.path.insert(0, str(SKILL / "runtime"))
from collaboration_observability import (calculate_source_metrics, IMPLEMENTED_METRICS,
                                         METRIC_UNITS, SOURCE_METRIC_IDS)
from collaboration_protocol import CollaborationContractError, digest


def dataset(rows, **metadata):
    return {"complete": True, "source_refs": ["fixture://authoritative-source"],
            "rows": rows, **metadata}


def versioned(identifier="artifact", revision=1, **extra):
    return {"id": identifier, "revision": revision, "hash": digest({"id": identifier, "revision": revision}), **extra}


def observation(**datasets):
    return {"local_profile_version": "3.0.0", "source_contract_version": "2.0.0",
            "observation_id": "observation-1", "tenant_id": "tenant-1", "run_id": "run-1",
            "plan_revision": 1, "window_start": "2026-09-09T03:00:00Z",
            "cutoff": "2026-09-09T03:10:00Z", "modes": ["adversarial_review", "fan_out_gather"],
            "datasets": datasets}


def measure(source, *keys):
    trusted = digest(source)
    return calculate_source_metrics(source, verify_observation=lambda item: digest(item) == trusted,
                                    enabled_metrics=keys)["metrics"]


def coverage_source():
    return observation(coverage=dataset([
        {"id": "a", "weight": 1, "required": True, "exclusive": True, "accepted": True},
        {"id": "b", "weight": 3, "required": True, "exclusive": True, "accepted": False}]),
        assignments=dataset([
            {"id": "assign-1", "unit_id": "a", "task_id": "task-1", "role": "primary", "active": True},
            {"id": "assign-2", "unit_id": "b", "task_id": "review-1", "role": "review", "active": True}]))


def test_weighted_coverage_and_independent_acceptance_population():
    source = coverage_source()
    result = measure(source, "CSM01", "CSM08")
    assert [result[key]["value"] for key in result] == [.25, .25]
    del source["datasets"]["assignments"]
    result = measure(source, "CSM01", "CSM08")
    assert result["CSM01"]["state"] == "not_computable"
    assert result["CSM08"]["value"] == .25


def test_duplicate_assignment_counts_relations_not_repeated_logs_or_reviews():
    source = coverage_source()
    rows = source["datasets"]["assignments"]["rows"]
    rows.extend([dict(rows[0], id="assign-3", task_id="task-2"),
                 dict(rows[0], id="assign-4", task_id="task-3"), deepcopy(rows[0])])
    assert measure(source, "CSM02")["CSM02"]["value"] == 2 / 3


@pytest.mark.parametrize("fault", ["missing", "incomplete", "conflicting", "unknown", "invalid_weight"])
def test_bad_inputs_only_degrade_dependent_metrics(fault):
    source = coverage_source()
    source["datasets"]["costs"] = dataset([
        {"id": "b", "domain": "business", "unit": "tokens", "value": 100},
        {"id": "p", "domain": "probe", "unit": "tokens", "value": 5}])
    group = source["datasets"]["coverage"]
    if fault == "missing":
        del source["datasets"]["coverage"]
    elif fault == "incomplete":
        group["complete"] = False
    elif fault == "conflicting":
        group["rows"].append(dict(group["rows"][0], weight=99))
    elif fault == "unknown":
        group["rows"][0]["required"] = None
    else:
        group["rows"][0]["weight"] = -1
    result = measure(source, "CSM01", "CSM19")
    assert result["CSM01"]["state"] == "not_computable"
    assert result["CSM01"]["sample_count"] is None
    assert result["CSM19"]["value"] == 5 / 105


def test_first_rejected_disposition_is_not_replaced_by_later_pass():
    source = observation(local_dispositions=dataset([
        {"id": "a2", "task_id": "a", "disposition_order": 2, "decision": "passed"},
        {"id": "a1", "task_id": "a", "disposition_order": 1, "decision": "rejected"},
        {"id": "b1", "task_id": "b", "disposition_order": 1, "decision": "passed"},
        {"id": "c1", "task_id": "c", "disposition_order": 1, "decision": "pending"}]))
    result = measure(source, "CSM07")["CSM07"]
    assert result["value"] == .5 and result["pending_count"] == 1


def test_closed_run_completion_keeps_failures_and_separates_open_runs():
    source = observation(closed_runs=dataset([
        {"id": "a", "state": "completed", "global_accepted": True, "delivered": True, "closed_at": "2026-09-09T03:05:00Z"},
        {"id": "b", "state": "failed", "closed_at": "2026-09-09T03:05:00Z"},
        {"id": "c", "state": "partial", "closed_at": "2026-09-09T03:05:00Z"},
        {"id": "d", "state": "running", "closed_at": None}], comparable_clock=True))
    result = measure(source, "CSM09")["CSM09"]
    assert result["value"] == 1 / 3 and result["open_count"] == 1


def test_retry_amplification_excludes_probe_attempts_and_deduplicates():
    rows = [{"id": str(i), "task_id": str(i % 3), "domain": "business", "started": True} for i in range(5)]
    rows += [deepcopy(rows[0]), {"id": "probe", "task_id": "p", "domain": "probe", "started": True}]
    assert measure(observation(attempts=dataset(rows)), "CSM13")["CSM13"]["value"] == 5 / 3


def test_independent_obligations_and_producer_cutoff_are_required():
    source = observation(record_obligations=dataset([{"id": str(i)} for i in range(10)], watermark_closed=True),
                         received_records=dataset([{"id": str(i)} for i in range(9)]))
    assert measure(source, "CSM18")["CSM18"]["value"] == .9
    source["datasets"]["record_obligations"]["watermark_closed"] = False
    assert measure(source, "CSM18")["CSM18"]["state"] == "not_computable"


def test_empty_population_unknown_data_and_disabled_mode_are_distinct():
    source = observation(coverage=dataset([]), assignments=dataset([]))
    source["modes"] = []
    result = measure(source, "CSM01", "CSM18", "CSM25", "CSM32", "CSM33")
    assert result["CSM01"]["state"] == "not_applicable"
    assert result["CSM01"]["denominator"] == 0
    assert result["CSM18"]["state"] == "not_computable"
    assert result["CSM25"]["state"] == result["CSM32"]["state"] == "not_applicable"
    assert result["CSM33"]["reason"] == "measurement_adapter_required"


def test_mixed_cost_units_are_not_added():
    source = observation(costs=dataset([
        {"id": "a", "domain": "business", "unit": "tokens", "value": 100},
        {"id": "b", "domain": "probe", "unit": "USD", "value": 5}]))
    assert measure(source, "CSM19")["CSM19"]["reason"] == "mixed_cost_units"


def test_isolation_configuration_and_execution_remain_distinct():
    source = observation(isolation=dataset([
        {"id": "a", "required": True, "check_type": "configuration", "verified": True},
        {"id": "b", "required": True, "check_type": "execution", "verified": False}]))
    result = measure(source, "CSM23")["CSM23"]
    assert result["value"] == .5
    assert result["groups"]["configuration"]["value"] == 1
    assert result["groups"]["execution"]["value"] == 0


def test_citation_repetition_requires_original_record_lineage():
    rows = [{"id": str(i), "origin_binding": versioned("original", location="p2")} for i in range(3)]
    source = observation(citations=dataset(rows))
    assert measure(source, "CSM24")["CSM24"]["value"] == 2 / 3
    rows[0]["origin_binding"] = None
    assert measure(source, "CSM24")["CSM24"]["state"] == "not_computable"


def review_source():
    row = {"id": "obj", "confirmed": True, "blocking": True, "artifact_binding": versioned(),
           "raised_at": "2026-09-09T03:01:00Z", "resolved_at": "2026-09-09T03:06:00Z"}
    return observation(objections=dataset([row], comparable_clock=True),
        conflicts=dataset([dict(row, resolved_at=None)], complete=False, comparable_clock=True),
        releases=dataset([{"id": "release", "artifact_binding": row["artifact_binding"], "released_at": "2026-09-09T03:05:00Z"}], comparable_clock=True))


def test_late_adjudication_cannot_erase_historical_release_violation():
    result = measure(review_source(), "CSM25", "CSM26")
    assert result["CSM25"]["value"] == 0
    assert result["CSM26"]["value"] == 1


def test_incomplete_conflict_ledger_reports_lower_bound_without_exact_total():
    result = measure(review_source(), "CSM12")["CSM12"]
    assert result["state"] == "partial_observation" and result["value"] is None
    assert result["confirmed_lower_bound"] == 1


def test_handoff_rejection_stays_in_denominator_and_pending_separate():
    source = observation(handoffs=dataset([
        {"id": "a", "disposition": "accepted", "artifact_binding": versioned(), "acceptance_binding": versioned()},
        {"id": "b", "disposition": "rejected", "artifact_binding": versioned(hash=digest("changed-content")), "acceptance_binding": versioned()},
        {"id": "c", "disposition": "pending"}]))
    result = measure(source, "CSM27")["CSM27"]
    assert result["value"] == .5 and result["pending_count"] == 1


def timing_source():
    return observation(timing=dataset([{"id": "run-1", "endpoint": "global_acceptance",
        "started_at": "2026-09-09T03:00:00Z", "accepted_at": "2026-09-09T03:07:00Z",
        "delivered_at": "2026-09-09T03:08:00Z", "branches": [
            {"id": "a", "required": True, "used_in_final": True, "ready_at": "2026-09-09T03:04:00Z"},
            {"id": "b", "required": True, "used_in_final": True, "ready_at": "2026-09-09T03:05:00Z"},
            {"id": "unused", "required": False, "used_in_final": False, "ready_at": "2026-09-09T03:06:00Z"}]}], comparable_clock=True))


def test_wall_clock_and_post_parallel_convergence_follow_distinct_endpoints():
    source = timing_source()
    result = measure(source, "CSM28", "CSM32")
    assert result["CSM28"]["value"] == 420
    assert result["CSM32"]["value"] == 120 / 420
    source["datasets"]["timing"]["rows"][0]["endpoint"] = "delivery"
    result = measure(source, "CSM28", "CSM32")
    assert result["CSM28"]["value"] == 480
    assert result["CSM32"]["value"] == 120 / 420


@pytest.mark.parametrize("fault", ["open", "clock", "branch_before_start", "branch_after_end"])
def test_incomplete_or_incomparable_timing_never_becomes_finished_duration(fault):
    source = timing_source()
    group = source["datasets"]["timing"]
    row = group["rows"][0]
    if fault == "open":
        row["accepted_at"] = None
    elif fault == "clock":
        group["comparable_clock"] = False
    elif fault == "branch_before_start":
        row["branches"][0]["ready_at"] = "2026-09-09T02:59:00Z"
    else:
        row["branches"][0]["ready_at"] = "2026-09-09T03:09:00Z"
    result = measure(source, "CSM32")["CSM32"]
    assert result["value"] is None
    assert result["state"] == ("partial_observation" if fault == "open" else "not_computable")


def baseline_source():
    cohort = [{"id": str(i), "input_binding": versioned(f"input-{i}"), "criteria_binding": versioned("rule-1")} for i in range(3)]
    runs = []
    for arm, durations, costs, scores in [("baseline", [600, 500, 700], [10000, 9000, 11000], [82, 84, 83]),
                                          ("collaboration", [420, 400, 500], [15000, 12500, 16000], [86, 85, 87])]:
        for i, member in enumerate(cohort):
            runs.append({**member, "id": arm + str(i), "task_id": str(i), "arm": arm,
                "state": "completed", "global_accepted": True, "delivered": True,
                "duration_seconds": durations[i], "resource_value": costs[i], "resource_unit": "tokens",
                "costs_complete": True, "quality_score": scores[i], "quality_unit": "score_points", "quality_verified": True})
    source = observation(cohort=dataset(cohort), comparison_runs=dataset(runs, comparable_clock=True))
    source["comparison"] = {"statistic": "mean", "duration_endpoint": "delivery",
                            "resource_unit": "tokens", "quality_unit": "score_points"}
    return source


def test_source_baseline_example_arithmetic():
    result = measure(baseline_source(), "CSM29", "CSM30", "CSM31", "CSM34")
    assert result["CSM29"]["value"] == pytest.approx(600 / 440)
    assert result["CSM30"]["value"] == 1.45
    assert result["CSM31"]["value"] == 3
    assert result["CSM34"]["value"] == 0


def test_enrolled_completion_does_not_drop_failure_or_unfinished_runs():
    source = baseline_source()
    rows = source["datasets"]["comparison_runs"]["rows"]
    rows[3]["state"] = "failed"
    rows[4]["state"] = "running"
    result = measure(source, "CSM29", "CSM30", "CSM34")
    assert result["CSM34"]["value"] == pytest.approx(-200 / 3)
    assert result["CSM34"]["enrolled_per_arm"] == 3
    assert result["CSM29"]["sample_count"] == 1
    assert result["CSM29"]["common_pair_share"] == 1 / 3
    assert result["CSM30"]["value"] == 1.45


@pytest.mark.parametrize("fault", ["missing_arm", "input", "criteria", "duplicate_arm", "statistic"])
def test_baseline_rejects_incomparable_or_selectively_missing_samples(fault):
    source = baseline_source()
    rows = source["datasets"]["comparison_runs"]["rows"]
    if fault == "missing_arm":
        rows.pop()
    elif fault == "duplicate_arm":
        rows.append(dict(rows[0], id="extra"))
    elif fault == "statistic":
        source["comparison"].pop("statistic")
    else:
        rows[0][fault + "_binding"] = "changed"
    assert measure(source, "CSM34")["CSM34"]["state"] == "not_computable"


def test_unverified_quality_and_incomplete_costs_do_not_invalidate_completion():
    source = baseline_source()
    row = source["datasets"]["comparison_runs"]["rows"][0]
    row["quality_verified"] = False
    row["costs_complete"] = False
    result = measure(source, "CSM30", "CSM31", "CSM34")
    assert result["CSM30"]["state"] == result["CSM31"]["state"] == "not_computable"
    assert result["CSM34"]["value"] == 0


def test_ratio_quality_difference_is_percentage_points():
    source = baseline_source()
    source["comparison"]["quality_unit"] = "ratio"
    for row in source["datasets"]["comparison_runs"]["rows"]:
        row["quality_unit"] = "ratio"
        row["quality_score"] /= 100
    result = measure(source, "CSM31")["CSM31"]
    assert result["value"] == pytest.approx(3) and result["unit"] == "percentage_points"
    source["datasets"]["comparison_runs"]["rows"][0]["quality_score"] = 80
    assert measure(source, "CSM31")["CSM31"]["state"] == "not_computable"


@pytest.mark.parametrize("verifier", [lambda _: False, lambda _: "true", lambda _: 1])
def test_metric_input_requires_host_attestation(verifier):
    with pytest.raises(CollaborationContractError, match="untrusted"):
        calculate_source_metrics(coverage_source(), verify_observation=verifier)


def test_measurements_are_read_only_and_keep_source_rule_provenance():
    source = coverage_source()
    before = deepcopy(source)
    result = measure(source, "CSM01")["CSM01"]
    result["scope"]["plan_revision"] = 99
    assert source == before
    assert result["source_id"] == "指01" and result["rule_version"] == "1"
    assert result["evidence_refs"] == ["fixture://authoritative-source"]


def test_source_catalog_support_and_units_match_runtime_exactly():
    source = json.loads((SKILL / "references/collaboration-fulltext-source-map.json").read_text("utf-8"))
    metrics = source["source_metrics"]
    assert tuple(row["id"] for row in metrics) == SOURCE_METRIC_IDS
    assert tuple(row["id"] for row in metrics if row["implementation"] == "reference") == IMPLEMENTED_METRICS
    assert {row["id"]: row["unit"] for row in metrics} == METRIC_UNITS


@pytest.mark.parametrize("fault", ["label", "missing_digest", "missing_revision"])
def test_matching_adapter_labels_cannot_replace_versioned_evidence(fault):
    ref = versioned()
    if fault == "label":
        ref = "looks-matched"
    else:
        del ref["hash" if fault == "missing_digest" else "revision"]
    source = observation(handoffs=dataset([{"id": "a", "disposition": "accepted",
                          "artifact_binding": ref, "acceptance_binding": deepcopy(ref)}]))
    assert measure(source, "CSM27")["CSM27"]["state"] == "not_computable"


@pytest.mark.parametrize("modes", [["unknown-mode"], ["adversarial_review", "adversarial_review"], [None]])
def test_unknown_or_duplicated_mode_cannot_silently_disable_review(modes):
    source = coverage_source()
    source["modes"] = modes
    with pytest.raises(CollaborationContractError, match="modes"):
        measure(source, "CSM25")
