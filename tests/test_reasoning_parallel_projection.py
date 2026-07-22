"""Event projection tests for Parallel Exploration / 并行探索事件投影测试。"""

from __future__ import annotations

import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(1, str(TESTS_DIR))

from reasoning_parallel_projection import project_parallel_run  # noqa: E402
from test_reasoning_parallel_factory import (  # noqa: E402
    close_two_branches,
    close_usage,
    compiled_session,
    criterion_result,
    final_evidence,
    source_evidence,
    synthesis_usage,
)


def test_incomplete_projection_preserves_missing_path_denominator() -> None:
    _, _, _, engine, session = compiled_session()
    session.launch_wave()
    record = source_evidence(session, path="path-cache", claim_id="claim-cache")
    session.close_branch(
        "path-cache",
        status="completed",
        candidate={"path": "path-cache"},
        evidence_records=[record],
        criterion_results=criterion_result(),
        veto_results=[],
        resource_use=close_usage(),
        information_gain=1.0,
    )

    projection = project_parallel_run(
        session.plan, engine.events.events(session.run_id)
    )
    results = projection.metric_results()

    assert projection.metric_inputs["candidate_completion_rate"] == {
        "candidate_paths_with_terminal_record": 1,
        "planned_candidate_paths": 2,
    }
    assert results["candidate_completion_rate"].value == 0.5
    assert "path_terminal_missing:path-parser" in projection.anomalies


def test_complete_projection_calculates_false_diversity_from_bindings() -> None:
    _, _, _, engine, session = compiled_session()
    close_two_branches(session, same_candidate=True)
    session.synthesize(
        decision="tie",
        reviewed_candidate_path_ids=["path-cache", "path-parser"],
        elimination_reasons={
            "path-cache": "identical result",
            "path-parser": "identical result",
        },
        minority_findings=[],
        synthesis_basis={"false_diversity": True},
        resource_use=synthesis_usage(),
        information_gain=1.0,
    )

    projection = project_parallel_run(
        session.plan, engine.events.events(session.run_id)
    )
    results = projection.metric_results()

    assert projection.synthesis_recorded is True
    assert projection.comparison_decision == "tie"
    assert projection.anomalies == ()
    assert results["candidate_completion_rate"].value == 1.0
    assert results["branch_diversity"].value == 0.5
    assert results["branch_record_completeness"].value == 1.0
    assert projection.as_dict()["projection_hash"].startswith("sha256:")


def test_selected_projection_binds_path_manifest_and_candidate() -> None:
    _, _, _, engine, session = compiled_session()
    records, candidates = close_two_branches(session)
    session.synthesize(
        decision="selected",
        reviewed_candidate_path_ids=["path-cache", "path-parser"],
        elimination_reasons={"path-parser": "weaker evidence"},
        minority_findings=[],
        synthesis_basis={"criterion": "evidence-fit"},
        selected_candidate_path_id="path-cache",
        selected_candidate=candidates["path-cache"],
        selected_evidence_records=[
            final_evidence(session, candidates["path-cache"], records["path-cache"])
        ],
        resource_use=synthesis_usage(),
        information_gain=1.0,
    )

    projection = project_parallel_run(
        session.plan, engine.events.events(session.run_id)
    )

    assert projection.comparison_decision == "selected"
    assert projection.selected_candidate_path_id == "path-cache"
    assert projection.anomalies == ()


def test_projection_marks_crash_between_synthesis_and_comparison_as_incomplete() -> None:
    _, _, _, engine, session = compiled_session()
    close_two_branches(session)
    session.synthesize(
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
    events = engine.events.events(session.run_id)
    comparison_index = next(
        index for index, event in enumerate(events)
        if event.event_type == "candidate_compared"
    )

    projection = project_parallel_run(session.plan, events[:comparison_index])

    assert projection.synthesis_recorded is True
    assert projection.comparison_decision is None
    assert "comparison_missing" in projection.anomalies
