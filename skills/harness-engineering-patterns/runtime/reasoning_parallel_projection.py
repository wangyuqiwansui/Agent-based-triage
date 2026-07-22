"""Deterministic Parallel Exploration event projection / 确定性并行探索事件投影。

Project an immutable parallel plan plus its public event stream into a complete
branch inventory and registered metric inputs. The projector records no private
reasoning and never guesses missing terminals, candidates, or comparison data.
/ 将不可变并行计划及其公开事件流投影为完整分支清单和已注册指标输入。投影器
不记录私密推理，也不猜测缺失的终态、候选或比较数据。
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Iterable, Mapping

try:  # Package import / 包导入
    from .reasoning_metrics import MetricResult, calculate_metric
    from .reasoning_parallel_factory import validate_parallel_plan
    from .reasoning_runtime import ReasoningEvent, content_fingerprint
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_metrics import MetricResult, calculate_metric
    from reasoning_parallel_factory import validate_parallel_plan
    from reasoning_runtime import ReasoningEvent, content_fingerprint


PROJECTION_VERSION = "1.0.0"
_TERMINALS = {"completed", "pruned", "failed", "timed_out", "cancelled"}


class ParallelProjectionError(ValueError):
    """The event stream conflicts with its immutable plan / 事件流与不可变计划冲突。"""


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, sort_keys=True))


def _binding(identifier: str, version: str, digest: str) -> dict[str, str]:
    return {"id": identifier, "version": version, "hash": digest}


def _binding_key(binding: Mapping[str, Any]) -> str:
    return json.dumps(binding, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class ParallelBranchProjection:
    """One planned path reconstructed from public events / 从公开事件重建的一条计划路径。"""

    candidate_path_id: str
    branch_step_id: str
    started: bool
    terminal_state: str | None
    candidate_binding: Mapping[str, str] | None
    evidence_record_bindings: tuple[Mapping[str, str], ...]
    criterion_results: tuple[Mapping[str, Any], ...]
    veto_results: tuple[Mapping[str, Any], ...]
    elimination_reason: str | None
    record_complete: bool

    def as_dict(self) -> dict[str, Any]:
        """Return one detached branch record / 返回独立分支记录。"""

        return {
            "candidate_path_id": self.candidate_path_id,
            "branch_step_id": self.branch_step_id,
            "started": self.started,
            "terminal_state": self.terminal_state,
            "candidate_binding": _copy(self.candidate_binding),
            "evidence_record_bindings": _copy(self.evidence_record_bindings),
            "criterion_results": _copy(self.criterion_results),
            "veto_results": _copy(self.veto_results),
            "elimination_reason": self.elimination_reason,
            "record_complete": self.record_complete,
        }


@dataclass(frozen=True)
class ParallelRunProjection:
    """Audit-ready projection and registered metric denominators / 可审计投影与已注册指标分母。"""

    run_id: str
    plan_binding: Mapping[str, str]
    contract_binding: Mapping[str, str]
    branches: tuple[ParallelBranchProjection, ...]
    comparison_decision: str | None
    selected_candidate_path_id: str | None
    synthesis_recorded: bool
    last_sequence: int
    anomalies: tuple[str, ...]

    @property
    def metric_inputs(self) -> dict[str, dict[str, int]]:
        """Return complete registered numerator and denominator inputs / 返回完整注册分子与分母输入。"""

        terminal = [branch for branch in self.branches if branch.terminal_state is not None]
        completed = [
            branch
            for branch in self.branches
            if branch.terminal_state == "completed" and branch.candidate_binding is not None
        ]
        distinct = len(
            {_binding_key(branch.candidate_binding) for branch in completed if branch.candidate_binding}
        )
        return {
            "candidate_completion_rate": {
                "candidate_paths_with_terminal_record": len(terminal),
                "planned_candidate_paths": len(self.branches),
            },
            "branch_diversity": {
                "distinct_candidate_bindings": distinct,
                "completed_candidate_paths": len(completed),
            },
            "branch_record_completeness": {
                "complete_terminal_branch_records": sum(
                    branch.record_complete for branch in terminal
                ),
                "terminal_branch_records": len(terminal),
            },
        }

    def metric_results(self) -> dict[str, MetricResult]:
        """Calculate registered diagnostics without inventing missing values / 计算注册诊断且不伪造缺失值。"""

        return {
            metric_id: calculate_metric(metric_id, inputs)
            for metric_id, inputs in self.metric_inputs.items()
        }

    def as_dict(self) -> dict[str, Any]:
        """Return a deterministic hash-bound projection artifact / 返回确定且哈希绑定的投影制品。"""

        artifact = {
            "schema_version": "1.0.0",
            "projection_version": PROJECTION_VERSION,
            "run_id": self.run_id,
            "plan_binding": _copy(self.plan_binding),
            "contract_binding": _copy(self.contract_binding),
            "branches": [branch.as_dict() for branch in self.branches],
            "comparison_decision": self.comparison_decision,
            "selected_candidate_path_id": self.selected_candidate_path_id,
            "synthesis_recorded": self.synthesis_recorded,
            "last_sequence": self.last_sequence,
            "metric_inputs": self.metric_inputs,
            "anomalies": list(self.anomalies),
        }
        artifact["projection_hash"] = content_fingerprint(artifact)
        return artifact


def project_parallel_run(
    plan: Mapping[str, Any],
    events: Iterable[ReasoningEvent],
) -> ParallelRunProjection:
    """Project one parallel event stream under its exact immutable plan.

    Structural conflicts fail closed. Operational incompleteness remains an
    explicit anomaly so missing paths do not become failures or zeros.
    / 按确切不可变计划投影一条并行事件流。结构冲突默认失败；运行不完整性保留为
    显式异常，使缺失路径不会被改写为失败或零值。
    """

    validate_parallel_plan(plan)
    normalized_plan = _copy(dict(plan))
    event_list = tuple(events)
    if not event_list:
        raise ParallelProjectionError(
            "parallel projection requires events / 并行投影要求事件"
        )
    if any(not isinstance(event, ReasoningEvent) for event in event_list):
        raise TypeError(
            "events must contain ReasoningEvent values / events 必须包含 ReasoningEvent"
        )
    run_id = normalized_plan["run_id"]
    if any(event.run_id != run_id for event in event_list):
        raise ParallelProjectionError(
            "projection contains another run / 投影包含其他运行"
        )
    sequences = [event.sequence for event in event_list]
    if sequences != list(range(1, len(event_list) + 1)):
        raise ParallelProjectionError(
            "projection requires a complete ordered event stream / 投影要求完整有序事件流"
        )

    plan_binding = _binding(
        normalized_plan["plan_id"],
        normalized_plan["plan_version"],
        normalized_plan["plan_hash"],
    )
    contract_binding = _copy(normalized_plan["contract_binding"])
    branch_specs = {
        branch["candidate_path_id"]: branch for branch in normalized_plan["branches"]
    }
    state: dict[str, dict[str, Any]] = {
        path: {"started": False, "close": None, "candidate": None, "candidate_sequence": None}
        for path in branch_specs
    }
    synthesis_event: ReasoningEvent | None = None
    comparison_event: ReasoningEvent | None = None

    for event in event_list:
        envelope = event.as_dict()
        path = envelope.get("candidate_path_id")
        step_id = envelope.get("step_id")
        if path is not None:
            if path not in branch_specs:
                raise ParallelProjectionError(
                    f"event references an unplanned path / 事件引用未计划路径: {path}"
                )
            expected_step = branch_specs[path]["branch_step_id"]
            if step_id is not None and step_id != expected_step:
                raise ParallelProjectionError(
                    f"branch step binding drift / 分支步骤绑定漂移: {path}"
                )
            if event.event_type == "step_started":
                if state[path]["started"]:
                    raise ParallelProjectionError(
                        f"duplicate branch start / 分支启动重复: {path}"
                    )
                state[path]["started"] = True
            elif event.event_type == "step_closed":
                if state[path]["close"] is not None:
                    raise ParallelProjectionError(
                        f"duplicate branch terminal / 分支终态重复: {path}"
                    )
                state[path]["close"] = event
            elif event.event_type == "candidate_created":
                if event.payload.get("plan_binding") != plan_binding:
                    raise ParallelProjectionError(
                        f"candidate plan binding drift / 候选计划绑定漂移: {path}"
                    )
                if state[path]["candidate"] is not None:
                    raise ParallelProjectionError(
                        f"duplicate branch candidate / 分支候选重复: {path}"
                    )
                state[path]["candidate"] = event
                state[path]["candidate_sequence"] = event.sequence
        elif event.event_type == "step_closed" and step_id == normalized_plan["synthesis"]["step_id"]:
            if synthesis_event is not None:
                raise ParallelProjectionError(
                    "duplicate synthesis record / 综合记录重复"
                )
            synthesis_event = event
        elif event.event_type == "candidate_compared":
            if comparison_event is not None:
                raise ParallelProjectionError(
                    "duplicate candidate comparison / 候选比较重复"
                )
            if event.payload.get("comparison_rule_binding") != normalized_plan[
                "comparison_rule_binding"
            ]:
                raise ParallelProjectionError(
                    "comparison rule binding drift / 比较规则绑定漂移"
                )
            comparison_event = event

    expected_criteria = {
        item["criterion_id"] for item in normalized_plan["comparison_contract"]["criteria"]
    }
    expected_vetoes = {
        item["veto_id"] for item in normalized_plan["comparison_contract"]["vetoes"]
    }
    branch_projections: list[ParallelBranchProjection] = []
    anomalies: list[str] = []
    candidate_bindings: list[dict[str, str]] = []
    for path, spec in branch_specs.items():
        entry = state[path]
        close = entry["close"]
        candidate = entry["candidate"]
        terminal_state = None
        close_candidate = None
        evidence_bindings: tuple[Mapping[str, str], ...] = ()
        criteria: tuple[Mapping[str, Any], ...] = ()
        vetoes: tuple[Mapping[str, Any], ...] = ()
        elimination_reason = None
        record_complete = False
        candidate_binding = None if candidate is None else candidate.payload["candidate_binding"]

        if not entry["started"]:
            anomalies.append(f"path_not_started:{path}")
        if close is None:
            anomalies.append(f"path_terminal_missing:{path}")
        else:
            if not entry["started"]:
                raise ParallelProjectionError(
                    f"branch closes without a start / 分支未启动却已关闭: {path}"
                )
            if close.sequence < next(
                event.sequence
                for event in event_list
                if event.event_type == "step_started"
                and event.as_dict().get("candidate_path_id") == path
            ):
                raise ParallelProjectionError(
                    f"branch closes before start / 分支关闭早于启动: {path}"
                )
            observation = close.payload["observation"]
            local_decision = close.payload["local_decision"]
            terminal_state = local_decision.get("branch_status")
            if terminal_state not in _TERMINALS:
                raise ParallelProjectionError(
                    f"invalid branch terminal / 分支终态非法: {path}"
                )
            close_candidate = observation.get("candidate_binding")
            evidence_bindings = tuple(observation.get("evidence_record_bindings", ()))
            criteria = tuple(observation.get("criterion_results", ()))
            vetoes = tuple(observation.get("veto_results", ()))
            elimination_reason = local_decision.get("elimination_reason")
            if candidate is not None and entry["candidate_sequence"] <= close.sequence:
                raise ParallelProjectionError(
                    f"branch candidate must follow terminal record / 分支候选必须晚于终态记录: {path}"
                )
            if close_candidate != candidate_binding:
                raise ParallelProjectionError(
                    f"branch candidate binding mismatch / 分支候选绑定不一致: {path}"
                )
            criterion_ids = [item.get("criterion_id") for item in criteria]
            veto_ids = [item.get("veto_id") for item in vetoes]
            if terminal_state == "completed":
                record_complete = (
                    candidate_binding is not None
                    and bool(evidence_bindings)
                    and set(criterion_ids) == expected_criteria
                    and len(criterion_ids) == len(expected_criteria)
                    and set(veto_ids) == expected_vetoes
                    and len(veto_ids) == len(expected_vetoes)
                )
                if candidate_binding is not None:
                    candidate_bindings.append(_copy(candidate_binding))
            else:
                record_complete = (
                    candidate_binding is None
                    and isinstance(elimination_reason, str)
                    and bool(elimination_reason.strip())
                )
            if not record_complete:
                anomalies.append(f"branch_record_incomplete:{path}")

        branch_projections.append(
            ParallelBranchProjection(
                candidate_path_id=path,
                branch_step_id=spec["branch_step_id"],
                started=entry["started"],
                terminal_state=terminal_state,
                candidate_binding=_copy(candidate_binding),
                evidence_record_bindings=tuple(_copy(item) for item in evidence_bindings),
                criterion_results=tuple(_copy(item) for item in criteria),
                veto_results=tuple(_copy(item) for item in vetoes),
                elimination_reason=elimination_reason,
                record_complete=record_complete,
            )
        )

    decision = None if comparison_event is None else comparison_event.payload["decision"]
    selected_path = None
    if synthesis_event is not None:
        observation = synthesis_event.payload["observation"]
        manifest = observation.get("branch_manifest", [])
        if {item.get("candidate_path_id") for item in manifest} != set(branch_specs) or len(
            manifest
        ) != len(branch_specs):
            raise ParallelProjectionError(
                "synthesis manifest does not cover the plan / 综合清单未覆盖计划"
            )
        manifest_by_path = {
            item["candidate_path_id"]: item for item in manifest
        }
        for branch in branch_projections:
            item = manifest_by_path[branch.candidate_path_id]
            if (
                item.get("status") != branch.terminal_state
                or item.get("candidate_binding") != branch.candidate_binding
                or item.get("evidence_record_bindings")
                != list(branch.evidence_record_bindings)
                or item.get("criterion_results") != list(branch.criterion_results)
                or item.get("veto_results") != list(branch.veto_results)
            ):
                raise ParallelProjectionError(
                    "synthesis manifest differs from branch records / 综合清单与分支记录不一致"
                )
        if comparison_event is not None and observation.get("decision") != decision:
            raise ParallelProjectionError(
                "synthesis and comparison decisions differ / 综合与比较决定不一致"
            )
        selected_path = observation.get("selected_candidate_path_id")
        if selected_path is not None and selected_path not in branch_specs:
            raise ParallelProjectionError(
                "synthesis selects an unplanned path / 综合选择了未计划路径"
            )
        expected_unselected = set(branch_specs) - (
            {selected_path} if selected_path is not None else set()
        )
        elimination_reasons = synthesis_event.payload["local_decision"].get(
            "elimination_reasons", {}
        )
        if set(elimination_reasons) != expected_unselected or any(
            not isinstance(reason, str) or not reason.strip()
            for reason in elimination_reasons.values()
        ):
            raise ParallelProjectionError(
                "synthesis elimination ledger is incomplete / 综合淘汰台账不完整"
            )
    elif all(branch.terminal_state is not None for branch in branch_projections):
        anomalies.append("synthesis_missing")

    if comparison_event is None:
        if all(branch.terminal_state is not None for branch in branch_projections):
            anomalies.append("comparison_missing")
    elif comparison_event.payload["candidate_bindings"] != candidate_bindings:
        raise ParallelProjectionError(
            "comparison candidate inventory differs from completed paths / 比较候选清单与完成路径不一致"
        )
    elif decision == "selected":
        if selected_path is None:
            raise ParallelProjectionError(
                "selected comparison has no selected path / 选中比较缺少选中路径"
            )
        selected_branch = next(
            branch for branch in branch_projections
            if branch.candidate_path_id == selected_path
        )
        if comparison_event.payload.get("selected_candidate_binding") != selected_branch.candidate_binding:
            raise ParallelProjectionError(
                "selected path and candidate binding differ / 选中路径与候选绑定不一致"
            )
    elif selected_path is not None:
        raise ParallelProjectionError(
            "non-selected comparison carries a selected path / 非选中比较携带选中路径"
        )

    return ParallelRunProjection(
        run_id=run_id,
        plan_binding=plan_binding,
        contract_binding=contract_binding,
        branches=tuple(branch_projections),
        comparison_decision=decision,
        selected_candidate_path_id=selected_path,
        synthesis_recorded=synthesis_event is not None,
        last_sequence=event_list[-1].sequence,
        anomalies=tuple(anomalies),
    )


__all__ = [
    "PROJECTION_VERSION",
    "ParallelBranchProjection",
    "ParallelProjectionError",
    "ParallelRunProjection",
    "project_parallel_run",
]
