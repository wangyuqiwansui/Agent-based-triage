"""Contract-bound Parallel Exploration factory / 契约绑定的并行探索工厂。

Compile isolated rival branches into one immutable plan, reserve each branch
wave before launch, and force an explicit evidence-aware synthesis. The module
stores public hypotheses, evidence bindings, criteria outcomes, and decisions;
it never stores private chain-of-thought. / 将隔离的竞争分支编译为不可变计划，
在启动前预留整批分支预算，并强制显式、证据感知的综合。本模块只保存公开假设、
证据绑定、判据结果和决定，绝不保存私密思维链。
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker

try:  # Package import / 包导入
    from .reasoning_artifacts import ArtifactValidationError, validate_reasoning_contract
    from .reasoning_metrics import resolve_required_probes
    from .reasoning_runtime import (
        BudgetUsage,
        ReasoningEngine,
        ReasoningRuntimeError,
        ValidationGateError,
        ValidationStatus,
        WorkflowState,
        _canonical_json,
        candidate_binding_for,
        content_fingerprint,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import ArtifactValidationError, validate_reasoning_contract
    from reasoning_metrics import resolve_required_probes
    from reasoning_runtime import (
        BudgetUsage,
        ReasoningEngine,
        ReasoningRuntimeError,
        ValidationGateError,
        ValidationStatus,
        WorkflowState,
        _canonical_json,
        candidate_binding_for,
        content_fingerprint,
    )


FACTORY_ID = "reasoning-parallel-factory"
FACTORY_VERSION = "1.0.0"
PLAN_VERSION = "1.0.0"
_BUDGET_FIELDS = (
    "reasoning_tokens",
    "latency_ms",
    "model_calls",
    "tool_calls",
    "parallel_paths",
    "iterations",
    "retries",
    "total_cost_units",
)
_CONTRACT_BUDGET_FIELDS = {
    "reasoning_tokens": "max_reasoning_tokens",
    "latency_ms": "max_latency_ms",
    "model_calls": "max_model_calls",
    "tool_calls": "max_tool_calls",
    "parallel_paths": "max_parallel_paths",
    "iterations": "max_iterations",
    "retries": "max_retries",
    "total_cost_units": "max_total_cost_units",
}
_BRANCH_TERMINALS = {"completed", "pruned", "failed", "timed_out", "cancelled"}
_DECISIONS = {"selected", "tie", "incomparable", "more_evidence_required"}


class ParallelFactoryError(ValueError):
    """Invalid blueprint, contract, or plan / 蓝图、契约或计划无效。"""

    def __init__(self, failures: str | Iterable[str]) -> None:
        self.failures = (
            [failures] if isinstance(failures, str) else [str(item) for item in failures]
        )
        super().__init__("; ".join(self.failures))


class ParallelPlanStateError(ReasoningRuntimeError):
    """The runtime cannot perform the requested plan transition / 运行时无法执行所请求的计划转换。"""


class ParallelPlanDriftError(ParallelPlanStateError):
    """Runtime history no longer matches the immutable plan / 运行历史不再匹配不可变计划。"""


@dataclass(frozen=True)
class ParallelBranchOutcome:
    """Public close result for one branch / 单个分支的公开关闭结果。"""

    candidate_path_id: str
    branch_step_id: str
    status: str
    candidate_binding: Mapping[str, str] | None
    ready_for_synthesis: bool


@dataclass(frozen=True)
class ParallelSynthesisOutcome:
    """Public result of the synthesis edge / 综合决策边的公开结果。"""

    decision: str
    selected_candidate_path_id: str | None
    next_action: str
    candidate_binding: Mapping[str, str] | None


@dataclass(frozen=True)
class ParallelFinalizationOutcome:
    """Public result of validation, release, and result sealing / 验证、放行与结果封存的公开结果。"""

    state: WorkflowState
    next_action: str
    validation_ids: tuple[str, ...]
    release_gate_failures: tuple[str, ...]
    result: Mapping[str, Any] | None


def _copy(value: Any) -> Any:
    return json.loads(_canonical_json(value))


def _binding(identifier: str, version: str, digest: str) -> dict[str, str]:
    return {"id": identifier, "version": version, "hash": digest}


def _factory_binding() -> dict[str, str]:
    digest = content_fingerprint({"id": FACTORY_ID, "version": FACTORY_VERSION})
    return _binding(FACTORY_ID, FACTORY_VERSION, digest)


def _schema_validator(kind: str) -> Draft202012Validator:
    path = (
        Path(__file__).resolve().parents[1]
        / "schemas"
        / f"reasoning-parallel-{kind}.schema.json"
    )
    schema = json.loads(path.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _schema_failures(kind: str, artifact: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for error in sorted(
        _schema_validator(kind).iter_errors(artifact), key=lambda item: list(item.path)
    ):
        location = "/".join(str(item) for item in error.path) or "$"
        failures.append(f"{kind} schema {location}: {error.message}")
    return failures


def _duplicates(records: Sequence[Mapping[str, Any]], field: str) -> list[str]:
    values = [str(record[field]) for record in records]
    return sorted({value for value in values if values.count(value) > 1})


def _sum_budget(records: Sequence[Mapping[str, Any]]) -> dict[str, int | float]:
    return {
        field: sum(record["budget_allocation"][field] for record in records)
        for field in _BUDGET_FIELDS
    }


def _add_budget(
    left: Mapping[str, int | float], right: Mapping[str, int | float]
) -> dict[str, int | float]:
    return {field: left[field] + right[field] for field in _BUDGET_FIELDS}


def _blueprint_semantic_failures(blueprint: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    branches = blueprint["branches"]
    comparison = blueprint["comparison_contract"]
    for field in ("candidate_path_id",):
        duplicates = _duplicates(branches, field)
        if duplicates:
            failures.append(
                f"duplicate {field} / 重复 {field}: {duplicates}"
            )
    hypotheses = [content_fingerprint(branch["hypothesis"]) for branch in branches]
    if len(hypotheses) != len(set(hypotheses)):
        failures.append(
            "parallel hypotheses must be materially distinct / 并行假设必须具有实质差异"
        )
    criterion_ids = [item["criterion_id"] for item in comparison["criteria"]]
    if len(criterion_ids) != len(set(criterion_ids)):
        failures.append("comparison criterion IDs must be unique / 比较判据标识必须唯一")
    veto_ids = [item["veto_id"] for item in comparison["vetoes"]]
    if len(veto_ids) != len(set(veto_ids)):
        failures.append("comparison veto IDs must be unique / 比较否决标识必须唯一")
    if not any(float(item["weight"]) > 0 for item in comparison["criteria"]):
        failures.append("at least one criterion must have positive weight / 至少一个判据权重必须大于零")
    for item in comparison["criteria"]:
        if item["evaluation_type"] == "boolean" and item["direction"] != "pass":
            failures.append(
                f"boolean criterion must use pass direction / 布尔判据必须使用 pass: {item['criterion_id']}"
            )
    declared_dimensions = set(comparison["material_difference_dimensions"])
    minimum_dimensions = comparison["minimum_material_dimensions"]
    if minimum_dimensions > len(declared_dimensions):
        failures.append(
            "minimum material dimensions exceed the declared set / 最小实质差异维度数超过声明集合"
        )
    for branch in branches:
        dimensions = {item["dimension"] for item in branch["material_difference"]}
        if not dimensions <= declared_dimensions:
            failures.append(
                f"branch uses undeclared material-difference dimensions / "
                f"分支使用未声明实质差异维度: {branch['candidate_path_id']}"
            )
        if len(dimensions) < minimum_dimensions:
            failures.append(
                f"branch does not meet material-difference minimum / "
                f"分支未达到实质差异最小维度数: {branch['candidate_path_id']}"
            )
        if branch["budget_allocation"]["parallel_paths"] != 1:
            failures.append(
                f"each branch must allocate exactly one parallel path / "
                f"每个分支必须恰好分配一条并行路径: {branch['candidate_path_id']}"
            )
    if blueprint["synthesis"]["budget_allocation"]["parallel_paths"] != 0:
        failures.append("synthesis cannot allocate a parallel path / 综合步骤不得分配并行路径")
    join = blueprint["join_policy"]
    if join["minimum_completed_branches"] > len(branches):
        failures.append("join quorum exceeds branch count / 汇合法定数超过分支数")
    if (
        join["completion_mode"] == "all_completed"
        and join["minimum_completed_branches"] != len(branches)
    ):
        failures.append(
            "all_completed requires the full branch count / all_completed 必须使用完整分支数"
        )
    return failures


def validate_parallel_blueprint(blueprint: Mapping[str, Any]) -> None:
    """Validate one author-owned blueprint / 校验一个负责人维护的蓝图。"""

    if not isinstance(blueprint, Mapping):
        raise TypeError("blueprint must be a mapping / 蓝图必须是映射")
    try:
        artifact = _copy(dict(blueprint))
    except (TypeError, ValueError) as exc:
        raise ParallelFactoryError(str(exc)) from exc
    failures = _schema_failures("blueprint", artifact)
    if not failures:
        failures.extend(_blueprint_semantic_failures(artifact))
    if failures:
        raise ParallelFactoryError(failures)


def _contract_failures(
    contract: Mapping[str, Any], blueprint: Mapping[str, Any]
) -> list[str]:
    failures: list[str] = []
    if contract["execution_mode"] != "parallel" or contract["primary_topology"] != "parallel":
        failures.append("contract must select parallel mode / 契约必须选择并行模式")
    if contract["budget"]["parallel_reservation_policy"] != "reserve_before_launch":
        failures.append(
            "reference session requires reserve_before_launch / 参考会话要求 reserve_before_launch"
        )
    normalized_binding = contract["normalized_input_binding"]
    if blueprint["isolation_policy"]["shared_input_binding"] != normalized_binding:
        failures.append(
            "isolation shared input must bind the normalized contract input / "
            "隔离策略共享输入必须绑定契约标准化输入"
        )
    all_records = [*blueprint["branches"], blueprint["synthesis"]]
    total = _sum_budget(all_records)
    for field, contract_field in _CONTRACT_BUDGET_FIELDS.items():
        limit = contract["budget"][contract_field]
        if total[field] > 0 and limit is None:
            failures.append(
                f"positive allocation uses an unconfigured budget / "
                f"正分配使用了未配置预算: {field}"
            )
        elif limit is not None and total[field] > limit:
            failures.append(
                f"allocation exceeds contract budget / 分配超过契约预算: {field}"
            )
    if len(blueprint["branches"]) > (contract["budget"]["max_parallel_paths"] or 0):
        failures.append("branch count exceeds max_parallel_paths / 分支数超过 max_parallel_paths")
    required_types = set(contract["evidence_sufficiency"]["required_evidence_types"])
    synthesis_types = set(blueprint["synthesis"]["required_evidence_types"])
    if not required_types <= synthesis_types:
        failures.append(
            "synthesis does not carry contract-required evidence types / "
            "综合步骤未承载契约要求的证据类型"
        )
    return failures


def _condition_states(
    blueprint: Mapping[str, Any], contract: Mapping[str, Any]
) -> dict[str, str]:
    requires_outcome = bool(blueprint["requires_outcome"])
    states = {
        "branch_action": "false",
        "winner_adoption_or_correctness_metric": "true" if requires_outcome else "false",
    }
    supporting = set(contract["supporting_topologies"])
    if "orchestration" in supporting:
        states.update(
            {
                "parallel_branch_exists": "true",
                "iteration_exists": "false",
                "outcome_metric": "true" if requires_outcome else "false",
            }
        )
    if "hierarchy" in supporting:
        states.update(
            {
                "delegated_action": "false",
                "parent_or_child_outcome_metric": "true" if requires_outcome else "false",
            }
        )
    return states


def _plan_semantic_failures(
    plan: Mapping[str, Any],
    contract: Mapping[str, Any] | None,
    blueprint: Mapping[str, Any] | None,
) -> list[str]:
    failures: list[str] = []
    if plan.get("plan_hash") != content_fingerprint(
        {key: value for key, value in plan.items() if key != "plan_hash"}
    ):
        failures.append("plan hash mismatch / 计划哈希不匹配")
    branches = plan["branches"]
    if _duplicates(branches, "branch_step_id"):
        failures.append("branch step IDs must be unique / 分支步骤标识必须唯一")
    wave = _sum_budget(branches)
    if wave != plan["wave_budget_allocation"]:
        failures.append("wave budget does not equal branch allocations / 波次预算不等于分支分配总和")
    total = _add_budget(wave, plan["synthesis"]["budget_allocation"])
    if total != plan["budget_allocation"]:
        failures.append("plan budget does not close / 计划预算未闭合")
    if contract is not None and blueprint is not None:
        if plan["contract_binding"] != _binding(
            contract["contract_id"], contract["contract_version"], contract["contract_hash"]
        ):
            failures.append("contract binding mismatch / 契约绑定不匹配")
        if plan["blueprint_binding"]["hash"] != content_fingerprint(blueprint):
            failures.append("blueprint binding mismatch / 蓝图绑定不匹配")
    return failures


def validate_parallel_plan(
    plan: Mapping[str, Any],
    *,
    contract: Mapping[str, Any] | None = None,
    blueprint: Mapping[str, Any] | None = None,
) -> None:
    """Validate a compiled plan and optional authoritative inputs / 校验编译计划及可选权威输入。"""

    if not isinstance(plan, Mapping):
        raise TypeError("plan must be a mapping / 计划必须是映射")
    if (contract is None) != (blueprint is None):
        raise ParallelFactoryError(
            "contract and blueprint must be supplied together / 契约与蓝图必须同时提供"
        )
    artifact = _copy(dict(plan))
    failures = _schema_failures("plan", artifact)
    if not failures:
        failures.extend(_plan_semantic_failures(artifact, contract, blueprint))
    if failures:
        raise ParallelFactoryError(failures)


class ReasoningParallelFactory:
    """Compile parallel blueprints and open guarded sessions / 编译并行蓝图并创建受守卫会话。"""

    def compile(
        self, blueprint: Mapping[str, Any], contract: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Compile one deterministic, contract-bound parallel plan / 编译确定且绑定契约的并行计划。"""

        validate_parallel_blueprint(blueprint)
        normalized_blueprint = _copy(dict(blueprint))
        normalized_contract = _copy(dict(contract))
        try:
            validate_reasoning_contract(normalized_contract)
        except (ArtifactValidationError, TypeError, ValueError) as exc:
            raise ParallelFactoryError(
                f"reasoning contract is invalid / 推理契约无效: {exc}"
            ) from exc
        failures = _contract_failures(normalized_contract, normalized_blueprint)
        if failures:
            raise ParallelFactoryError(failures)

        blueprint_hash = content_fingerprint(normalized_blueprint)
        seed = content_fingerprint(
            {
                "factory_binding": _factory_binding(),
                "blueprint_hash": blueprint_hash,
                "contract_hash": normalized_contract["contract_hash"],
            }
        )
        short = seed.removeprefix("sha256:")[:32]
        branches = []
        for index, branch in enumerate(normalized_blueprint["branches"], start=1):
            branches.append(
                {
                    "branch_step_id": f"parallel-branch-{short}-{index}",
                    **_copy(branch),
                }
            )
        synthesis = {
            "step_id": f"parallel-synthesis-{short}",
            **_copy(normalized_blueprint["synthesis"]),
        }
        comparison = normalized_blueprint["comparison_contract"]
        comparison_binding = _binding(
            comparison["comparison_id"],
            comparison["comparison_version"],
            content_fingerprint(comparison),
        )
        probe_resolution = resolve_required_probes(
            "parallel",
            supporting_topologies=normalized_contract["supporting_topologies"],
            condition_states=_condition_states(normalized_blueprint, normalized_contract),
        )
        wave_budget = _sum_budget(branches)
        plan: dict[str, Any] = {
            "schema_version": "1.0.0",
            "plan_id": f"parallel-plan-{short}",
            "plan_version": PLAN_VERSION,
            "factory_binding": _factory_binding(),
            "blueprint_binding": _binding(
                normalized_blueprint["blueprint_id"],
                normalized_blueprint["blueprint_version"],
                blueprint_hash,
            ),
            "contract_binding": _binding(
                normalized_contract["contract_id"],
                normalized_contract["contract_version"],
                normalized_contract["contract_hash"],
            ),
            "workflow_id": normalized_contract["workflow_id"],
            "task_id": normalized_contract["task_id"],
            "run_id": normalized_contract["run_id"],
            "scene_id": normalized_contract["scene_id"],
            "execution_mode": "parallel",
            "primary_topology": "parallel",
            "supporting_topologies": list(normalized_contract["supporting_topologies"]),
            "isolation_policy": _copy(normalized_blueprint["isolation_policy"]),
            "comparison_contract": _copy(comparison),
            "comparison_rule_binding": comparison_binding,
            "join_policy": _copy(normalized_blueprint["join_policy"]),
            "branches": branches,
            "synthesis": synthesis,
            "wave_budget_allocation": wave_budget,
            "budget_allocation": _add_budget(
                wave_budget, synthesis["budget_allocation"]
            ),
            "final_claim_ids": list(normalized_blueprint["final_claim_ids"]),
            "probe_plan": probe_resolution.as_dict(),
            "created_at": normalized_contract["created_at"],
        }
        plan["plan_hash"] = content_fingerprint(plan)
        validate_parallel_plan(
            plan, contract=normalized_contract, blueprint=normalized_blueprint
        )
        return _copy(plan)

    def start_session(
        self,
        engine: ReasoningEngine,
        plan: Mapping[str, Any],
        contract: Mapping[str, Any],
        blueprint: Mapping[str, Any],
        *,
        auto_start: bool = True,
    ) -> "ParallelPlanSession":
        """Create the governed run and return its parallel guard / 创建受治理运行并返回并行守卫。"""

        if not isinstance(engine, ReasoningEngine):
            raise TypeError("engine must be ReasoningEngine / engine 必须为 ReasoningEngine")
        expected = self.compile(blueprint, contract)
        if _copy(plan) != expected:
            raise ParallelFactoryError(
                "plan is not reproducible from blueprint and contract / 计划无法由蓝图与契约复现"
            )
        run_id = engine.create_run_from_contract(contract, auto_start=auto_start)
        if run_id != plan["run_id"]:
            raise ParallelPlanDriftError("run identity drift / 运行标识漂移")
        return ParallelPlanSession(
            engine, plan, blueprint=blueprint, contract=contract
        )

    def resume_session(
        self,
        engine: ReasoningEngine,
        plan: Mapping[str, Any],
        contract: Mapping[str, Any],
        blueprint: Mapping[str, Any],
        *,
        candidate_artifact: Any | None = None,
    ) -> "ParallelPlanSession":
        """Restore an event-backed session without duplicating lifecycle events.

        Plan and contract drift fail before the mutable aggregate is exposed.
        Candidate content is optional because the event stream retains only its
        binding; resupply it when validation or final-result construction needs
        the public artifact. / 从事件恢复会话且不重复生命周期事件。计划或契约漂移
        会在暴露可变聚合前失败。事件流只保留候选绑定，因此候选内容可选重供；
        验证或构造最终结果需要公开候选时应重新提供。
        """

        if not isinstance(engine, ReasoningEngine):
            raise TypeError("engine must be ReasoningEngine / engine 必须为 ReasoningEngine")
        expected = self.compile(blueprint, contract)
        if _copy(plan) != expected:
            raise ParallelFactoryError(
                "plan is not reproducible from blueprint and contract / 计划无法由蓝图与契约复现"
            )
        run_id = engine.resume_run_from_contract(
            contract,
            candidate_artifact=candidate_artifact,
        )
        if run_id != plan["run_id"]:
            raise ParallelPlanDriftError("run identity drift / 运行标识漂移")
        return ParallelPlanSession(
            engine, plan, blueprint=blueprint, contract=contract
        )


class ParallelPlanSession:
    """Enforce isolation, wave reservation, join, and synthesis / 强制隔离、波次预留、汇合与综合。"""

    def __init__(
        self,
        engine: ReasoningEngine,
        plan: Mapping[str, Any],
        *,
        blueprint: Mapping[str, Any],
        contract: Mapping[str, Any],
    ) -> None:
        expected = ReasoningParallelFactory().compile(blueprint, contract)
        if _copy(plan) != expected:
            raise ParallelPlanDriftError(
                "plan cannot be reproduced from its inputs / 计划无法由输入复现"
            )
        self.engine = engine
        self.plan = _copy(plan)
        self.contract = _copy(contract)
        self.run_id = self.plan["run_id"]
        snapshot = self.engine.snapshot(self.run_id)
        if (
            snapshot.workflow_id != self.plan["workflow_id"]
            or snapshot.task_id != self.plan["task_id"]
            or snapshot.scene_id != self.plan["scene_id"]
            or snapshot.contract_hash != self.plan["contract_binding"]["hash"]
            or snapshot.execution_mode != "parallel"
            or snapshot.primary_topology != "parallel"
        ):
            raise ParallelPlanDriftError(
                "runtime identity or mode differs from plan / 运行标识或模式与计划不一致"
            )
        self._branches = {
            branch["candidate_path_id"]: branch for branch in self.plan["branches"]
        }
        self._validate_history()

    @property
    def plan_binding(self) -> dict[str, str]:
        return _binding(
            self.plan["plan_id"], self.plan["plan_version"], self.plan["plan_hash"]
        )

    @property
    def wave_reservation_id(self) -> str:
        return f"parallel-wave-{self.plan['plan_id']}"

    def branch_reservation_id(self, candidate_path_id: str) -> str:
        """Return one deterministic reservation within the prelaunch wave / 返回启动前波次中的确定性分支预留。"""

        return f"{self.wave_reservation_id}-{candidate_path_id}"

    @property
    def synthesis_reservation_id(self) -> str:
        return f"parallel-synthesis-{self.plan['plan_id']}"

    def _branch_action(self, branch: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "plan_binding": self.plan_binding,
            "candidate_path_id": branch["candidate_path_id"],
            "hypothesis": branch["hypothesis"],
            "comparison_rule_binding": self.plan["comparison_rule_binding"],
            "shared_input_binding": self.plan["isolation_policy"]["shared_input_binding"],
            "isolation_strategy": self.plan["isolation_policy"]["strategy"],
            "intermediate_visibility": "branch_private_until_closed",
            "budget_allocation": branch["budget_allocation"],
            "side_effect": False,
        }

    def _validate_history(self) -> None:
        planned = set(self._branches)
        step_by_path = {
            branch["candidate_path_id"]: branch["branch_step_id"]
            for branch in self.plan["branches"]
        }
        for event in self.engine.events.events(self.run_id):
            envelope = event.as_dict()
            candidate_path_id = envelope.get("candidate_path_id")
            step_id = envelope.get("step_id")
            if candidate_path_id is not None:
                if candidate_path_id not in planned:
                    raise ParallelPlanDriftError(
                        "event references an unplanned branch / 事件引用未计划分支"
                    )
                if step_id is not None and step_id != step_by_path[candidate_path_id]:
                    raise ParallelPlanDriftError(
                        "branch event step binding drift / 分支事件步骤绑定漂移"
                    )
            if event.event_type == "candidate_created" and candidate_path_id is not None:
                if event.payload.get("plan_binding") != self.plan_binding:
                    raise ParallelPlanDriftError(
                        "branch candidate plan binding drift / 分支候选计划绑定漂移"
                    )
            if event.event_type == "parallel_path_updated":
                if event.payload.get("plan_binding") != self.plan_binding:
                    raise ParallelPlanDriftError(
                        "parallel path plan binding drift / 并行路径计划绑定漂移"
                    )
            if event.event_type == "candidate_compared":
                if event.payload.get("comparison_rule_binding") != self.plan["comparison_rule_binding"]:
                    raise ParallelPlanDriftError(
                        "comparison rule binding drift / 比较规则绑定漂移"
                    )

    def launch_wave(self) -> tuple[Any, ...]:
        """Reserve the complete branch wave before starting any branch / 在启动任何分支前预留完整波次。"""

        self.engine.reserve_budget_batch(
            self.run_id,
            {
                self.branch_reservation_id(branch["candidate_path_id"]): branch[
                    "budget_allocation"
                ]
                for branch in self.plan["branches"]
            },
            idempotency_key=f"parallel-wave-reserve:{self.plan['plan_id']}",
        )
        started = []
        for branch in self.plan["branches"]:
            started.append(
                self.engine.start_step(
                    self.run_id,
                    step_id=branch["branch_step_id"],
                    claim=branch["hypothesis"],
                    evidence_refs=(),
                    action=self._branch_action(branch),
                    idempotency_key=f"parallel-branch-start:{branch['candidate_path_id']}",
                    candidate_path_id=branch["candidate_path_id"],
                )
            )
        return tuple(started)

    def _branch_events(self) -> dict[str, dict[str, Any]]:
        records: dict[str, dict[str, Any]] = {}
        for event in self.engine.events.events(self.run_id):
            path = event.as_dict().get("candidate_path_id")
            if path is None or path not in self._branches:
                continue
            entry = records.setdefault(path, {"close": None, "candidate": None})
            if event.event_type == "step_closed":
                if entry["close"] is not None:
                    raise ParallelPlanDriftError(
                        f"duplicate branch closure / 重复分支关闭: {path}"
                    )
                entry["close"] = event
            elif event.event_type == "candidate_created":
                if entry["candidate"] is not None:
                    raise ParallelPlanDriftError(
                        f"duplicate branch candidate / 重复分支候选: {path}"
                    )
                entry["candidate"] = event
        return records

    def _progress(self, information_gain: float | None, status: str) -> tuple[bool, float | None]:
        rules = [
            item for item in self.contract["stop_conditions"] if item["type"] == "no_progress"
        ]
        if not rules:
            return status == "completed", information_gain
        if information_gain is None:
            raise ParallelPlanStateError(
                "parallel branch closure requires information_gain under no-progress control / "
                "启用无进展控制时关闭并行分支必须提供 information_gain"
            )
        threshold = max(float(item["min_information_gain"]) for item in rules)
        return float(information_gain) >= threshold, float(information_gain)

    @staticmethod
    def _evidence_binding(record: Mapping[str, Any]) -> dict[str, str]:
        return _binding(
            str(record["evidence_id"]),
            str(record["evidence_version"]),
            str(record["record_hash"]),
        )

    def _normalize_branch_assessment(
        self,
        *,
        status: str,
        criterion_results: Iterable[Mapping[str, Any]],
        veto_results: Iterable[Mapping[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        criteria = [_copy(dict(item)) for item in criterion_results]
        vetoes = [_copy(dict(item)) for item in veto_results]
        if status != "completed":
            return criteria, vetoes
        expected_criteria = {
            item["criterion_id"] for item in self.plan["comparison_contract"]["criteria"]
        }
        observed_criteria = {item.get("criterion_id") for item in criteria}
        if observed_criteria != expected_criteria or len(criteria) != len(expected_criteria):
            raise ParallelPlanStateError(
                "completed branch must report every common criterion exactly once / "
                "完成分支必须逐项且仅一次报告全部统一判据"
            )
        required = {
            item["criterion_id"]
            for item in self.plan["comparison_contract"]["criteria"]
            if item["required"]
        }
        if any(
            item.get("criterion_id") in required
            and item.get("status") == "not_applicable"
            for item in criteria
        ):
            raise ParallelPlanStateError(
                "required criterion cannot be not_applicable / 必需判据不得标记为不适用"
            )
        expected_vetoes = {
            item["veto_id"] for item in self.plan["comparison_contract"]["vetoes"]
        }
        observed_vetoes = {item.get("veto_id") for item in vetoes}
        if observed_vetoes != expected_vetoes or len(vetoes) != len(expected_vetoes):
            raise ParallelPlanStateError(
                "completed branch must report every common veto exactly once / "
                "完成分支必须逐项且仅一次报告全部统一否决规则"
            )
        return criteria, vetoes

    def close_branch(
        self,
        candidate_path_id: str,
        *,
        status: str,
        candidate: Any | None = None,
        evidence_records: Iterable[Mapping[str, Any]] = (),
        criterion_results: Iterable[Mapping[str, Any]] = (),
        veto_results: Iterable[Mapping[str, Any]] = (),
        elimination_reason: str | None = None,
        resource_use: BudgetUsage | Mapping[str, Any] | None = None,
        information_gain: float | None = None,
    ) -> ParallelBranchOutcome:
        """Close one branch with an explicit terminal and optional candidate / 以显式终态和可选候选关闭一个分支。"""

        branch = self._branches.get(candidate_path_id)
        if branch is None:
            raise ParallelPlanStateError(
                f"unknown candidate path / 未知候选路径: {candidate_path_id}"
            )
        if status not in _BRANCH_TERMINALS:
            raise ParallelPlanStateError(f"invalid branch status / 分支状态非法: {status}")
        if status == "completed" and candidate is None:
            raise ParallelPlanStateError("completed branch requires candidate / 完成分支必须提供候选")
        if status != "completed" and (candidate is not None or not elimination_reason):
            raise ParallelPlanStateError(
                "non-completed branch requires an elimination reason and no candidate / "
                "未完成分支必须提供淘汰原因且不得提供候选"
            )
        records = [_copy(dict(record)) for record in evidence_records]
        if status == "completed":
            observed_types = {record.get("evidence_type") for record in records}
            required_types = set(branch["required_evidence_types"])
            if not required_types <= observed_types:
                raise ParallelPlanStateError(
                    "branch evidence types are incomplete / 分支证据类型不完整"
                )
        criteria, vetoes = self._normalize_branch_assessment(
            status=status,
            criterion_results=criterion_results,
            veto_results=veto_results,
        )
        usage = BudgetUsage.from_value(resource_use)
        usage_map = ReasoningEngine._schema_budget_delta(usage)
        if any(
            usage_map[field] > branch["budget_allocation"][field]
            for field in _BUDGET_FIELDS
        ):
            raise ParallelPlanStateError(
                "branch usage exceeds its allocation / 分支用量超过自身分配"
            )
        candidate_binding = candidate_binding_for(candidate) if candidate is not None else None
        progress, gain = self._progress(information_gain, status)
        observation = {
            "branch_status": status,
            "candidate_binding": candidate_binding,
            "evidence_record_bindings": [self._evidence_binding(record) for record in records],
            "criterion_results": criteria,
            "veto_results": vetoes,
        }
        local_decision = {
            "branch_status": status,
            "elimination_reason": elimination_reason,
            "data_gap_policy": branch["data_gap_policy"],
            "material_difference": branch["material_difference"],
        }
        self.engine.record_step(
            self.run_id,
            step_id=branch["branch_step_id"],
            claim=branch["hypothesis"],
            evidence_refs=(),
            action=self._branch_action(branch),
            observation=observation,
            local_decision=local_decision,
            resource_use=usage,
            budget_reservation_id=self.branch_reservation_id(candidate_path_id),
            progress=progress,
            information_gain=gain,
            idempotency_key=f"parallel-branch-close:{candidate_path_id}",
            candidate_path_id=candidate_path_id,
        )
        if candidate is not None:
            candidate_binding = self.engine.record_parallel_candidate(
                self.run_id,
                candidate_path_id=candidate_path_id,
                candidate=candidate,
                evidence_records=records,
                plan_binding=self.plan_binding,
                claim_ids=branch["claim_ids"],
                idempotency_key=f"parallel-candidate:{candidate_path_id}",
            )
        history = self._branch_events()
        ready = all(item.get("close") is not None for item in history.values()) and len(history) == len(self._branches)
        return ParallelBranchOutcome(
            candidate_path_id=candidate_path_id,
            branch_step_id=branch["branch_step_id"],
            status=status,
            candidate_binding=candidate_binding,
            ready_for_synthesis=ready,
        )

    def synthesize(
        self,
        *,
        decision: str,
        reviewed_candidate_path_ids: Iterable[str],
        elimination_reasons: Mapping[str, str],
        minority_findings: Iterable[Mapping[str, Any]],
        synthesis_basis: Mapping[str, Any],
        selected_candidate_path_id: str | None = None,
        selected_candidate: Any | None = None,
        selected_evidence_records: Iterable[Mapping[str, Any]] = (),
        resource_use: BudgetUsage | Mapping[str, Any] | None = None,
        information_gain: float | None = None,
    ) -> ParallelSynthesisOutcome:
        """Join every branch terminal, compare completed candidates, and apply tie policy / 汇合全部分支终态、比较完成候选并执行并列策略。"""

        if decision not in _DECISIONS:
            raise ParallelPlanStateError(f"invalid synthesis decision / 综合决定非法: {decision}")
        reviewed = tuple(reviewed_candidate_path_ids)
        planned_paths = tuple(branch["candidate_path_id"] for branch in self.plan["branches"])
        if len(reviewed) != len(set(reviewed)) or set(reviewed) != set(planned_paths):
            raise ParallelPlanStateError(
                "synthesis owner must review every planned branch / 综合责任方必须审阅全部计划分支"
            )
        history = self._branch_events()
        if set(history) != set(planned_paths) or any(
            entry["close"] is None for entry in history.values()
        ):
            raise ParallelPlanStateError(
                "every branch requires an explicit terminal before synthesis / "
                "综合前每个分支都必须有显式终态"
            )
        completed_paths = [
            path
            for path in planned_paths
            if history[path]["candidate"] is not None
            and history[path]["close"].payload["local_decision"]["branch_status"] == "completed"
        ]
        if len(completed_paths) < self.plan["join_policy"]["minimum_completed_branches"]:
            raise ParallelPlanStateError(
                "completed branch count does not meet the join policy / 完成分支数不满足汇合策略"
            )
        deadline_quorum_override = (
            self.plan["join_policy"]["on_deadline"] == "proceed_with_quorum"
            and any(
                event.event_type == "parallel_path_updated"
                and event.payload.get("phase") == "deadline_reached"
                for event in self.engine.events.events(self.run_id)
            )
        )
        if (
            self.plan["join_policy"]["completion_mode"] == "all_completed"
            and len(completed_paths) != len(planned_paths)
            and not deadline_quorum_override
        ):
            raise ParallelPlanStateError("all_completed join is not satisfied / all_completed 汇合未满足")
        if len(completed_paths) < 2:
            raise ParallelPlanStateError("synthesis needs two completed candidates / 综合至少需要两个完成候选")
        if decision == "selected":
            if (
                selected_candidate_path_id not in completed_paths
                or selected_candidate is None
            ):
                raise ParallelPlanStateError(
                    "selected synthesis requires a completed path and candidate / "
                    "选中综合必须提供已完成路径及候选"
                )
            expected_binding = history[selected_candidate_path_id]["candidate"].payload[
                "candidate_binding"
            ]
            if candidate_binding_for(selected_candidate) != expected_binding:
                raise ParallelPlanDriftError(
                    "selected candidate content differs from branch record / "
                    "选中候选内容与分支记录不一致"
                )
        elif selected_candidate_path_id is not None or selected_candidate is not None:
            raise ParallelPlanStateError(
                "non-selected synthesis cannot carry a winner / 非选中综合不得携带胜出者"
            )
        losing_paths = set(planned_paths) - (
            {selected_candidate_path_id} if selected_candidate_path_id is not None else set()
        )
        if set(elimination_reasons) != losing_paths or any(
            not isinstance(reason, str) or not reason.strip()
            for reason in elimination_reasons.values()
        ):
            raise ParallelPlanStateError(
                "every non-selected path requires one elimination reason / "
                "每条未选路径必须有且只有一个淘汰原因"
        )
        usage = BudgetUsage.from_value(resource_use)
        usage_map = ReasoningEngine._schema_budget_delta(usage)
        allocation = self.plan["synthesis"]["budget_allocation"]
        if any(usage_map[field] > allocation[field] for field in _BUDGET_FIELDS):
            raise ParallelPlanStateError(
                "synthesis usage exceeds allocation / 综合用量超过分配"
            )
        action = {
            "plan_binding": self.plan_binding,
            "comparison_rule_binding": self.plan["comparison_rule_binding"],
            "instruction": self.plan["synthesis"]["action_instruction"],
            "reviewed_candidate_path_ids": list(reviewed),
            "budget_allocation": allocation,
            "side_effect": False,
        }
        self.engine.start_step_with_budget_reservation(
            self.run_id,
            step_id=self.plan["synthesis"]["step_id"],
            claim=self.plan["synthesis"]["claim_to_verify"],
            evidence_refs=(),
            action=action,
            reservation_amounts=allocation,
            reservation_id=self.synthesis_reservation_id,
            reservation_idempotency_key=f"parallel-synthesis-reserve:{self.plan['plan_id']}",
            step_idempotency_key=f"parallel-synthesis-start:{self.plan['plan_id']}",
        )
        manifest = []
        candidate_bindings = []
        for path in planned_paths:
            close = history[path]["close"]
            candidate_event = history[path]["candidate"]
            candidate_binding = (
                None if candidate_event is None else candidate_event.payload["candidate_binding"]
            )
            if candidate_binding is not None:
                candidate_bindings.append(candidate_binding)
            manifest.append(
                {
                    "candidate_path_id": path,
                    "status": close.payload["local_decision"]["branch_status"],
                    "candidate_binding": candidate_binding,
                    "evidence_record_bindings": close.payload["observation"]["evidence_record_bindings"],
                    "criterion_results": close.payload["observation"]["criterion_results"],
                    "veto_results": close.payload["observation"]["veto_results"],
                }
            )
        progress, gain = self._progress(information_gain, "completed")
        self.engine.record_step(
            self.run_id,
            step_id=self.plan["synthesis"]["step_id"],
            claim=self.plan["synthesis"]["claim_to_verify"],
            evidence_refs=(),
            action=action,
            observation={
                "branch_manifest": manifest,
                "decision": decision,
                "selected_candidate_path_id": selected_candidate_path_id,
            },
            local_decision={
                "synthesis_basis": _copy(dict(synthesis_basis)),
                "elimination_reasons": _copy(dict(elimination_reasons)),
                "minority_findings": [_copy(dict(item)) for item in minority_findings],
            },
            resource_use=usage,
            budget_reservation_id=self.synthesis_reservation_id,
            progress=progress,
            information_gain=gain,
            idempotency_key=f"parallel-synthesis-close:{self.plan['plan_id']}",
        )
        selected_binding = (
            None
            if selected_candidate_path_id is None
            else history[selected_candidate_path_id]["candidate"].payload["candidate_binding"]
        )
        self.engine.compare_parallel_candidates(
            self.run_id,
            candidate_bindings=candidate_bindings,
            comparison_rule_binding=self.plan["comparison_rule_binding"],
            decision=decision,
            selected_candidate_binding=selected_binding,
            idempotency_key=f"parallel-compare:{self.plan['plan_id']}",
        )
        final_binding = None
        next_action = "validate_selected_candidate"
        if decision == "selected":
            final_records = [_copy(dict(record)) for record in selected_evidence_records]
            final_binding = candidate_binding_for(selected_candidate)
            for record in final_records:
                state = record.get("candidate_binding", {})
                if state.get("state") != "observed" or state.get("value") != final_binding:
                    raise ParallelPlanStateError(
                        "final evidence revision must bind the selected candidate / "
                        "最终证据修订必须绑定选中候选"
                    )
            self.engine.set_candidate_with_evidence_records(
                self.run_id,
                selected_candidate,
                evidence_records=final_records,
                plan_binding=self.plan_binding,
                final_claim_ids=self.plan["final_claim_ids"],
                idempotency_key=f"parallel-final-candidate:{self.plan['plan_id']}",
            )
        else:
            tie_policy = self.plan["comparison_contract"]["tie_policy"]
            if decision == "more_evidence_required" or tie_policy == "request_more_evidence":
                if self.engine.snapshot(self.run_id).state is not WorkflowState.WAITING_FOR_EVIDENCE:
                    self.engine.transition(
                        self.run_id,
                        WorkflowState.WAITING_FOR_EVIDENCE,
                        reason="parallel synthesis requires more evidence / 并行综合需要更多证据",
                    )
                next_action = "request_more_evidence"
            elif tie_policy == "escalate":
                if self.engine.snapshot(self.run_id).state is not WorkflowState.ESCALATED:
                    self.engine.transition(
                        self.run_id,
                        WorkflowState.ESCALATED,
                        reason="material parallel tie requires authority / 实质并列需要有权限的裁决",
                    )
                next_action = "escalate_material_tie"
            else:
                next_action = "return_conditional_alternatives"
        return ParallelSynthesisOutcome(
            decision=decision,
            selected_candidate_path_id=selected_candidate_path_id,
            next_action=next_action,
            candidate_binding=final_binding,
        )

    def finalize_selected_candidate(
        self,
        validation_outcomes: Iterable[Mapping[str, Any]],
        *,
        claims: Iterable[Mapping[str, Any]],
        final_decision: Mapping[str, Any],
        output: Mapping[str, Any],
        field_provenance: Iterable[Mapping[str, Any]],
        unresolved_items: Iterable[Mapping[str, Any]] = (),
        next_actions: Iterable[Mapping[str, Any]] = (),
        limitations: Iterable[Mapping[str, Any]] = (),
        terminal_reason: Mapping[str, Any] | None = None,
        result_id: str | None = None,
        result_version: str = "1.0.0",
        evaluated_at: float | str | None = None,
        created_at: float | str | None = None,
    ) -> ParallelFinalizationOutcome:
        """Record final validators, apply the release gate, and seal a result.

        Validator execution remains external. This method accepts only public
        outcomes, stops at the first state-changing failure, and constructs a
        normative result whenever the run reaches a terminal state. / 验证器仍由
        外部执行。本方法只接收公开结果，在首个改变状态的失败处停止，并在运行进入
        终态时构造规范结果。
        """

        if isinstance(validation_outcomes, (str, bytes, Mapping)):
            raise TypeError(
                "validation_outcomes must be an iterable of mappings / "
                "validation_outcomes 必须是映射迭代器"
            )
        allowed_fields = {
            "validator_id",
            "status",
            "details",
            "verification_id",
            "actor_binding",
            "authority_binding",
            "attempt",
            "idempotency_key",
        }
        outcomes: dict[str, dict[str, Any]] = {}
        for index, value in enumerate(validation_outcomes):
            if not isinstance(value, Mapping):
                raise TypeError(
                    f"validation outcome {index} must be a mapping / "
                    f"验证结果 {index} 必须是映射"
                )
            item = _copy(dict(value))
            unexpected = set(item) - allowed_fields
            if unexpected or not {"validator_id", "status"} <= set(item):
                raise ParallelPlanStateError(
                    "validation outcome fields differ from the contract / "
                    "验证结果字段与契约不一致"
                )
            validator_id = item["validator_id"]
            if not isinstance(validator_id, str) or not validator_id:
                raise ParallelPlanStateError(
                    "validator_id must be non-empty / validator_id 不能为空"
                )
            if validator_id in outcomes:
                raise ParallelPlanStateError(
                    f"duplicate validation outcome / 重复验证结果: {validator_id}"
                )
            outcomes[validator_id] = item

        declared = {
            item["validator_id"]: item for item in self.contract["validators"]
        }
        unknown = set(outcomes) - set(declared)
        if unknown:
            raise ParallelPlanStateError(
                "unknown final validator / 未知最终验证器: "
                + ", ".join(sorted(unknown))
            )
        selected = any(
            event.event_type == "candidate_compared"
            and event.payload.get("decision") == "selected"
            for event in self.engine.events.events(self.run_id)
        )
        snapshot = self.engine.snapshot(self.run_id)
        if not selected or snapshot.candidate_hash is None:
            raise ParallelPlanStateError(
                "finalization requires a synthesized selected candidate / "
                "最终闭环要求已有综合选中的候选"
            )

        claim_records = [_copy(dict(item)) for item in claims]
        provenance_records = [_copy(dict(item)) for item in field_provenance]
        unresolved_records = [_copy(dict(item)) for item in unresolved_items]
        action_records = [_copy(dict(item)) for item in next_actions]
        limitation_records = [_copy(dict(item)) for item in limitations]
        validation_ids: list[str] = []

        terminal_states = {
            WorkflowState.COMPLETED,
            WorkflowState.FAILED,
            WorkflowState.ESCALATED,
            WorkflowState.TIMED_OUT,
            WorkflowState.REJECTED,
            WorkflowState.CANCELLED,
        }

        def seal_terminal(current: WorkflowState) -> ParallelFinalizationOutcome:
            result = self.engine.build_result(
                self.run_id,
                claims=claim_records,
                final_decision=_copy(dict(final_decision)),
                output=_copy(dict(output)),
                field_provenance=provenance_records,
                unresolved_items=unresolved_records,
                next_actions=action_records,
                limitations=limitation_records,
                terminal_reason=(
                    None if terminal_reason is None else _copy(dict(terminal_reason))
                ),
                result_id=result_id,
                result_version=result_version,
                created_at=created_at,
            )
            actions = {
                WorkflowState.COMPLETED: "terminal_result_sealed",
                WorkflowState.FAILED: "terminal_failed_result_sealed",
                WorkflowState.ESCALATED: "terminal_escalated_result_sealed",
                WorkflowState.TIMED_OUT: "terminal_timed_out_result_sealed",
                WorkflowState.REJECTED: "terminal_rejected_result_sealed",
                WorkflowState.CANCELLED: "terminal_cancelled_result_sealed",
            }
            return ParallelFinalizationOutcome(
                state=current,
                next_action=actions[current],
                validation_ids=tuple(validation_ids),
                release_gate_failures=(),
                result=result,
            )

        initially_terminal = snapshot.state in terminal_states
        if not initially_terminal and snapshot.state not in {
            WorkflowState.CANDIDATE_READY,
            WorkflowState.VALIDATING,
        }:
            raise ParallelPlanStateError(
                "selected candidate is not ready for final validation / "
                "选中候选尚未进入最终验证状态"
            )

        for validator_id in declared:
            item = outcomes.get(validator_id)
            if item is None:
                continue
            attempt = item.get("attempt", 1)
            verification_id = item.get("verification_id")
            if verification_id is None:
                digest = content_fingerprint(
                    {
                        "plan_id": self.plan["plan_id"],
                        "validator_id": validator_id,
                        "attempt": attempt,
                    }
                ).removeprefix("sha256:")[:32]
                verification_id = f"parallel-validation-{digest}"
            record = self.engine.record_validation(
                self.run_id,
                validator_id=validator_id,
                status=ValidationStatus(item["status"]),
                details=item.get("details"),
                verification_id=verification_id,
                actor_binding=item.get("actor_binding"),
                authority_binding=item.get("authority_binding"),
                attempt=attempt,
                idempotency_key=item.get("idempotency_key")
                or (
                    f"parallel-final-validation:{self.plan['plan_id']}:"
                    f"{validator_id}:{attempt}"
                ),
            )
            validation_ids.append(record.verification_id)
            current = self.engine.snapshot(self.run_id).state
            if initially_terminal:
                continue
            if current in terminal_states:
                return seal_terminal(current)
            if current is WorkflowState.REPAIRABLE_FAILURE:
                return ParallelFinalizationOutcome(
                    state=current,
                    next_action="repair_selected_candidate",
                    validation_ids=tuple(validation_ids),
                    release_gate_failures=self.engine.completion_failures(
                        self.run_id, evaluated_at=evaluated_at
                    ),
                    result=None,
                )

        if initially_terminal:
            return seal_terminal(snapshot.state)

        try:
            completed = self.engine.finalize(
                self.run_id,
                evaluated_at=evaluated_at,
                claims=claim_records,
                reason=(
                    "parallel selected candidate validated / "
                    "并行选中候选验证完成"
                ),
            )
        except ValidationGateError:
            return ParallelFinalizationOutcome(
                state=self.engine.snapshot(self.run_id).state,
                next_action="repair_release_gate",
                validation_ids=tuple(validation_ids),
                release_gate_failures=self.engine.completion_failures(
                    self.run_id, evaluated_at=evaluated_at
                ),
                result=None,
            )
        return seal_terminal(completed.state)


__all__ = [
    "FACTORY_ID",
    "FACTORY_VERSION",
    "PLAN_VERSION",
    "ParallelBranchOutcome",
    "ParallelFactoryError",
    "ParallelFinalizationOutcome",
    "ParallelPlanDriftError",
    "ParallelPlanSession",
    "ParallelPlanStateError",
    "ParallelSynthesisOutcome",
    "ReasoningParallelFactory",
    "validate_parallel_blueprint",
    "validate_parallel_plan",
]
