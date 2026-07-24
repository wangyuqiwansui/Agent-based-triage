"""Observability projection tests for tool dispatch / 工具调度可观测投影测试。"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

from tool_dispatch import seal_tool_execution_event  # noqa: E402
from tool_dispatch_projection import project_tool_dispatch_run  # noqa: E402
from test_tool_dispatch import (  # noqa: E402
    ToolDispatchCoordinator,
    ToolDispatchRuntime,
    ToolExecutionReceipt,
    ExecutionClassification,
    SideEffectState,
    SqliteToolDispatchStore,
    allow,
    binding,
    fixed_clock,
    write_capability,
    write_request,
)


def test_projection_derives_dispatch_governance_inputs(tmp_path: Path) -> None:
    store = SqliteToolDispatchStore(tmp_path / "projection.sqlite")
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

    projection = project_tool_dispatch_run(
        [run.envelope],
        [run.result],
        list(store.events("RUN_WRITE")),
    )

    assert projection.action_count == 1
    assert projection.metric_inputs["execution_starts"] == 1
    assert projection.metric_inputs["executions_with_valid_admission"] == 1
    assert projection.metric_inputs["side_effecting_executions_with_valid_lease"] == 1
    assert projection.metric_inputs["write_executions_with_current_state_evidence"] == 1
    assert projection.metric_inputs["complete_dispatch_records"] == 1
    assert projection.metric_inputs["unknown_results"] == 0
    assert projection.anomalies == ()
    assert projection.projection_hash.startswith("sha256:")


def test_projection_preserves_orphan_event_as_anomaly(tmp_path: Path) -> None:
    store = SqliteToolDispatchStore(tmp_path / "orphan.sqlite")
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
    events = list(store.events("RUN_WRITE"))
    draft = deepcopy(events[0])
    for field in ("event_id", "sequence", "event_hash"):
        draft.pop(field)
    draft["event_key"] = "ORPHAN:frontier"
    draft["action_id"] = "ORPHAN_ACTION"
    events.append(seal_tool_execution_event(draft, sequence=len(events) + 1))

    projection = project_tool_dispatch_run(
        [run.envelope],
        [run.result],
        events,
    )

    assert any(item.code == "ORPHAN_EVENT" for item in projection.anomalies)
