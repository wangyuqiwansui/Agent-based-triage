"""Recoverable Plan-and-Execute reference kernel / 可恢复“计划并执行”参考内核。

The kernel keeps the goal and plan immutable, stores mutable execution truth in
checkpoint records, protects completed business facts, and permits replanning
only through a versioned patch over the failed-and-affected subgraph.

/ 本内核保持目标与计划不可变，将可变执行真值存入检查点记录，保护已完成的业务
事实，并且只允许通过版本化补丁修改“失败节点及受影响下游子图”。

This is a deterministic single-process reference. Production deployments must
atomically persist checkpoints, events, idempotency claims, and external
receipts in a transactional store before dispatching side effects.

/ 这是确定性的单进程参考实现。生产部署必须在副作用分派前，使用事务存储原子
持久化检查点、事件、幂等领取和外部回执。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence

try:  # Package import / 包导入
    from .reasoning_artifacts import (
        ArtifactValidationError,
        build_artifact,
        validate_artifact_hash,
        validate_schema,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import (
        ArtifactValidationError,
        build_artifact,
        validate_artifact_hash,
        validate_schema,
    )


class PlanExecutionError(ValueError):
    """Base Plan-and-Execute failure / “计划并执行”基础异常。"""


class PlanValidationError(PlanExecutionError):
    """A goal or plan violates structural semantics / 目标或计划违反结构语义。"""


class PlanStateError(PlanExecutionError):
    """An execution transition is illegal / 执行状态转换非法。"""


class PlanPatchError(PlanExecutionError):
    """A plan patch exceeds its recovery boundary / 计划补丁越过恢复边界。"""


class IdempotencyConflictError(PlanExecutionError):
    """An idempotency identity was reused with divergent content / 幂等身份被不同内容复用。"""


class StepState(str, Enum):
    """Mechanical step states / 步骤机械状态。"""

    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"
    VERIFYING = "verifying"


class IdempotencyStatus(str, Enum):
    """Durable action-result states / 持久动作结果状态。"""

    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ActionClaim:
    """Decision returned before a state-changing action / 改状态动作前的领取决定。"""

    disposition: str
    idempotency_key: str
    prior_status: str | None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _require_unique(values: Sequence[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise PlanValidationError(f"{label} must be unique / {label} 必须唯一")


def _require_sha256(value: str, label: str) -> None:
    valid = (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value) == 71
        and all(character in "0123456789abcdef" for character in value[7:])
    )
    if not valid:
        raise PlanStateError(
            f"{label} must be a lowercase sha256 digest / "
            f"{label} 必须是小写 sha256 摘要"
        )


def _step_map(plan: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(step["step_id"]): deepcopy(dict(step))
        for step in plan.get("steps", ())
        if isinstance(step, Mapping) and "step_id" in step
    }


def _descendants(
    steps: Mapping[str, Mapping[str, Any]],
    roots: Sequence[str],
) -> set[str]:
    affected = set(roots)
    changed = True
    while changed:
        changed = False
        for step_id, step in steps.items():
            dependencies = set(step.get("dependencies", ()))
            if step_id not in affected and dependencies & affected:
                affected.add(step_id)
                changed = True
    return affected


def _validate_goal_semantics(goal: Mapping[str, Any]) -> None:
    constraints = [
        str(item.get("constraint_id"))
        for item in goal.get("constraints", ())
        if isinstance(item, Mapping)
    ]
    criteria = [
        str(item.get("criterion_id"))
        for item in goal.get("success_criteria", ())
        if isinstance(item, Mapping)
    ]
    _require_unique(constraints, "constraint_id")
    _require_unique(criteria, "criterion_id")


def _validate_plan_semantics(plan: Mapping[str, Any]) -> None:
    steps = list(plan.get("steps", ()))
    step_ids = [
        str(step.get("step_id"))
        for step in steps
        if isinstance(step, Mapping)
    ]
    _require_unique(step_ids, "step_id")
    if len(step_ids) != len(steps):
        raise PlanValidationError("every step must be an object / 每个步骤都必须是对象")

    known = set(step_ids)
    graph: dict[str, tuple[str, ...]] = {}
    for step in steps:
        step_id = str(step["step_id"])
        dependencies = tuple(str(item) for item in step.get("dependencies", ()))
        missing = sorted(set(dependencies) - known)
        if missing:
            raise PlanValidationError(
                f"{step_id} has missing dependencies {missing} / "
                f"{step_id} 存在缺失依赖 {missing}"
            )
        if step_id in dependencies:
            raise PlanValidationError(
                f"{step_id} depends on itself / {step_id} 依赖自身"
            )
        graph[step_id] = dependencies

        effect = step.get("effect", {})
        effect_class = effect.get("class")
        if effect_class != "read_only" and not effect.get("idempotency_key"):
            raise PlanValidationError(
                f"{step_id} state-changing action lacks idempotency_key / "
                f"{step_id} 改状态动作缺少 idempotency_key"
            )
        if effect_class == "reversible_write" and not effect.get("compensation"):
            raise PlanValidationError(
                f"{step_id} reversible write lacks compensation / "
                f"{step_id} 可逆写动作缺少补偿"
            )
        if effect_class == "irreversible_external" and not effect.get(
            "approval_binding"
        ):
            raise PlanValidationError(
                f"{step_id} irreversible action lacks approval binding / "
                f"{step_id} 不可逆动作缺少审批绑定"
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(step_id: str) -> None:
        if step_id in visiting:
            raise PlanValidationError(
                f"plan contains a dependency cycle at {step_id} / "
                f"计划在 {step_id} 存在依赖环"
            )
        if step_id in visited:
            return
        visiting.add(step_id)
        for dependency in graph[step_id]:
            visit(dependency)
        visiting.remove(step_id)
        visited.add(step_id)

    for step_id in graph:
        visit(step_id)


def validate_goal_contract(goal: Mapping[str, Any]) -> None:
    """Validate the sealed goal contract / 校验已封存目标契约。"""

    validate_schema("goal_contract", goal)
    validate_artifact_hash("goal_contract", goal)
    _validate_goal_semantics(goal)


def validate_workflow_plan(plan: Mapping[str, Any]) -> None:
    """Validate the sealed plan and DAG semantics / 校验已封存计划及 DAG 语义。"""

    validate_schema("workflow_plan", plan)
    validate_artifact_hash("workflow_plan", plan)
    _validate_plan_semantics(plan)


def validate_workflow_plan_patch(patch: Mapping[str, Any]) -> None:
    """Validate the sealed patch shape / 校验已封存计划补丁结构。"""

    validate_schema("workflow_plan_patch", patch)
    validate_artifact_hash("workflow_plan_patch", patch)
    if patch["target_revision"] != patch["base_revision"] + 1:
        raise PlanPatchError(
            "target_revision must equal base_revision + 1 / "
            "target_revision 必须等于 base_revision + 1"
        )


def validate_workflow_checkpoint(checkpoint: Mapping[str, Any]) -> None:
    """Validate a sealed recovery checkpoint / 校验已封存恢复检查点。"""

    validate_schema("workflow_checkpoint", checkpoint)
    validate_artifact_hash("workflow_checkpoint", checkpoint)
    step_ids = [str(item["step_id"]) for item in checkpoint["step_records"]]
    keys = [
        str(item["idempotency_key"])
        for item in checkpoint["idempotency_records"]
    ]
    _require_unique(step_ids, "checkpoint step_id")
    _require_unique(keys, "checkpoint idempotency_key")


def compile_goal_contract(source: Mapping[str, Any]) -> dict[str, Any]:
    """Seal an externalized goal baseline / 封存外部化目标基线。"""

    artifact = deepcopy(dict(source))
    artifact.setdefault("schema_version", "1.0.0")
    try:
        sealed = build_artifact("goal_contract", artifact)
        _validate_goal_semantics(sealed)
    except ArtifactValidationError as error:
        raise PlanValidationError(str(error)) from error
    return sealed


def compile_workflow_plan(
    goal_contract: Mapping[str, Any],
    blueprint: Mapping[str, Any],
) -> dict[str, Any]:
    """Compile and seal a plan DAG bound to one goal version.

    / 编译并封存绑定到一个目标版本的计划 DAG。
    """

    validate_goal_contract(goal_contract)
    artifact = deepcopy(dict(blueprint))
    artifact.setdefault("schema_version", "1.0.0")
    artifact.setdefault("revision", 1)
    artifact["goal_binding"] = {
        "goal_id": goal_contract["goal_id"],
        "version": goal_contract["version"],
        "hash": goal_contract["goal_contract_hash"],
    }
    try:
        _validate_plan_semantics(artifact)
        sealed = build_artifact("workflow_plan", artifact)
    except ArtifactValidationError as error:
        raise PlanValidationError(str(error)) from error
    return sealed


def _candidate_plan_from_patch(
    plan: Mapping[str, Any],
    patch: Mapping[str, Any],
) -> dict[str, Any]:
    affected = set(str(item) for item in patch["affected_step_ids"])
    replacement = {
        str(step["step_id"]): deepcopy(dict(step))
        for step in patch["replacement_steps"]
    }
    retained = [
        deepcopy(dict(step))
        for step in plan["steps"]
        if step["step_id"] not in affected
    ]
    candidate = deepcopy(dict(plan))
    candidate["revision"] = patch["target_revision"]
    candidate["steps"] = retained + list(replacement.values())
    candidate.pop("plan_hash", None)
    _validate_plan_semantics(candidate)
    try:
        return build_artifact("workflow_plan", candidate)
    except ArtifactValidationError as error:
        raise PlanPatchError(str(error)) from error


def compile_workflow_plan_patch(
    plan: Mapping[str, Any],
    source: Mapping[str, Any],
) -> dict[str, Any]:
    """Compile a local patch over the failed-and-affected subgraph.

    The patch cannot delete an existing affected step or remove one of its
    dependencies. New steps must remain connected to the affected subgraph.
    / 编译失败节点及受影响下游子图的局部补丁。补丁不得删除已有受影响步骤，
    不得移除其既有依赖；新增步骤必须与受影响子图相连。
    """

    validate_workflow_plan(plan)
    artifact = deepcopy(dict(source))
    artifact.setdefault("schema_version", "1.0.0")
    artifact["plan_id"] = plan["plan_id"]
    artifact["base_revision"] = plan["revision"]
    artifact["target_revision"] = plan["revision"] + 1
    artifact["base_plan_hash"] = plan["plan_hash"]

    roots = [str(item) for item in artifact.get("failed_root_step_ids", ())]
    step_map = _step_map(plan)
    missing_roots = sorted(set(roots) - set(step_map))
    if missing_roots:
        raise PlanPatchError(
            f"patch roots are absent from plan: {missing_roots} / "
            f"补丁根节点不在计划中：{missing_roots}"
        )
    affected = _descendants(step_map, roots)
    supplied_affected = set(
        str(item) for item in artifact.get("affected_step_ids", ())
    )
    if supplied_affected and supplied_affected != affected:
        raise PlanPatchError(
            f"affected_step_ids must equal {sorted(affected)} / "
            f"affected_step_ids 必须等于 {sorted(affected)}"
        )
    artifact["affected_step_ids"] = sorted(affected)

    replacement_items = [
        deepcopy(dict(step))
        for step in artifact.get("replacement_steps", ())
        if isinstance(step, Mapping)
    ]
    replacement_ids = [str(step.get("step_id")) for step in replacement_items]
    _require_unique(replacement_ids, "replacement step_id")
    replacements = {
        str(step.get("step_id")): deepcopy(dict(step))
        for step in replacement_items
    }
    missing_replacements = sorted(affected - set(replacements))
    if missing_replacements:
        raise PlanPatchError(
            f"patch cannot delete affected steps: {missing_replacements} / "
            f"补丁不得删除受影响步骤：{missing_replacements}"
        )
    collisions = sorted((set(replacements) - affected) & (set(step_map) - affected))
    if collisions:
        raise PlanPatchError(
            f"new patch steps collide with retained steps: {collisions} / "
            f"新增补丁步骤与保留步骤冲突：{collisions}"
        )

    for step_id in affected:
        original_dependencies = set(step_map[step_id]["dependencies"])
        replacement_dependencies = set(replacements[step_id]["dependencies"])
        if not original_dependencies.issubset(replacement_dependencies):
            removed = sorted(original_dependencies - replacement_dependencies)
            raise PlanPatchError(
                f"patch cannot remove dependencies from {step_id}: {removed} / "
                f"补丁不得移除 {step_id} 的依赖：{removed}"
            )
        original_effect = step_map[step_id]["effect"]
        replacement_effect = replacements[step_id]["effect"]
        if (
            original_effect["class"] != "read_only"
            and original_effect["idempotency_key"]
            != replacement_effect["idempotency_key"]
        ):
            raise PlanPatchError(
                f"patch cannot change idempotency identity for {step_id} / "
                f"补丁不得改变 {step_id} 的幂等身份"
            )

    candidate = deepcopy(dict(plan))
    candidate["steps"] = [
        deepcopy(dict(step))
        for step in plan["steps"]
        if step["step_id"] not in affected
    ] + list(replacements.values())
    candidate["revision"] = artifact["target_revision"]
    candidate.pop("plan_hash", None)
    _validate_plan_semantics(candidate)

    new_ids = set(replacements) - affected
    if new_ids:
        adjacency: dict[str, set[str]] = {
            step_id: set(step["dependencies"])
            for step_id, step in _step_map(candidate).items()
        }
        for step_id, dependencies in tuple(adjacency.items()):
            for dependency in dependencies:
                adjacency.setdefault(dependency, set()).add(step_id)
        connected = set(affected)
        frontier = list(affected)
        while frontier:
            current = frontier.pop()
            for neighbor in adjacency.get(current, ()):
                if neighbor not in connected:
                    connected.add(neighbor)
                    frontier.append(neighbor)
        disconnected = sorted(new_ids - connected)
        if disconnected:
            raise PlanPatchError(
                f"new patch steps are outside the affected subgraph: {disconnected} / "
                f"新增补丁步骤位于受影响子图之外：{disconnected}"
            )

    try:
        sealed = build_artifact("workflow_plan_patch", artifact)
        validate_workflow_plan_patch(sealed)
    except ArtifactValidationError as error:
        raise PlanPatchError(str(error)) from error
    _candidate_plan_from_patch(plan, sealed)
    return sealed


class PlanExecutionSession:
    """Guarded execution state for one compiled workflow plan.

    / 一份已编译工作流计划的受保护执行状态。
    """

    def __init__(
        self,
        plan: Mapping[str, Any],
        *,
        run_id: str,
        started_at: str | None = None,
    ) -> None:
        validate_workflow_plan(plan)
        if not run_id:
            raise PlanValidationError("run_id is required / run_id 必填")
        self.plan = deepcopy(dict(plan))
        self.run_id = run_id
        initial_time = started_at or _now()
        self._records: dict[str, dict[str, Any]] = {
            step["step_id"]: {
                "step_id": step["step_id"],
                "state": StepState.TODO.value,
                "attempt": 0,
                "started_at": None,
                "updated_at": initial_time,
                "output_digest": None,
                "completion_evidence": [],
                "error": None,
                "external_receipts": [],
            }
            for step in self.plan["steps"]
        }
        self._idempotency: dict[str, dict[str, Any]] = {}
        self._events: list[dict[str, Any]] = []
        self._sequence = 0
        self.replan_count = 0
        self._emit("run_created", occurred_at=initial_time)

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._events))

    @property
    def step_records(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            deepcopy(self._records[step["step_id"]])
            for step in self.plan["steps"]
        )

    @property
    def idempotency_records(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            deepcopy(self._idempotency[key])
            for key in sorted(self._idempotency)
        )

    def _emit(
        self,
        event_type: str,
        *,
        occurred_at: str | None = None,
        **payload: Any,
    ) -> None:
        self._sequence += 1
        self._events.append(
            {
                "sequence": self._sequence,
                "event_type": event_type,
                "run_id": self.run_id,
                "plan_id": self.plan["plan_id"],
                "plan_revision": self.plan["revision"],
                "occurred_at": occurred_at or _now(),
                "payload": deepcopy(payload),
            }
        )

    def _steps(self) -> dict[str, dict[str, Any]]:
        return _step_map(self.plan)

    def _record(self, step_id: str) -> dict[str, Any]:
        try:
            return self._records[step_id]
        except KeyError as error:
            raise PlanStateError(
                f"unknown step_id: {step_id} / 未知 step_id：{step_id}"
            ) from error

    def ready_step_ids(self) -> tuple[str, ...]:
        """Return deterministic ready steps / 返回确定性就绪步骤。"""

        steps = self._steps()
        ready = []
        for step_id, step in steps.items():
            if self._records[step_id]["state"] != StepState.TODO.value:
                continue
            if all(
                self._records[dependency]["state"] == StepState.DONE.value
                for dependency in step["dependencies"]
            ):
                ready.append(step_id)
        return tuple(sorted(ready))

    def start_step(self, step_id: str, *, occurred_at: str | None = None) -> None:
        record = self._record(step_id)
        if record["state"] != StepState.TODO.value:
            raise PlanStateError(
                f"{step_id} is not TODO / {step_id} 不是 TODO 状态"
            )
        if step_id not in self.ready_step_ids():
            raise PlanStateError(
                f"{step_id} dependencies are not DONE / {step_id} 的依赖尚未 DONE"
            )
        maximum = self.plan["stop_conditions"]["max_retries_per_step"] + 1
        if record["attempt"] >= maximum:
            raise PlanStateError(
                f"{step_id} retry limit reached / {step_id} 已达到重试上限"
            )
        timestamp = occurred_at or _now()
        record.update(
            {
                "state": StepState.DOING.value,
                "attempt": record["attempt"] + 1,
                "started_at": timestamp,
                "updated_at": timestamp,
                "error": None,
            }
        )
        self._emit(
            "step_started",
            occurred_at=timestamp,
            step_id=step_id,
            attempt=record["attempt"],
        )

    def claim_action(
        self,
        step_id: str,
        *,
        request_digest: str,
        occurred_at: str | None = None,
    ) -> ActionClaim:
        """Claim a state-changing action without replaying uncertain work.

        / 领取改状态动作，并阻止不确定动作被重放。
        """

        record = self._record(step_id)
        if record["state"] != StepState.DOING.value:
            raise PlanStateError(
                f"{step_id} must be DOING before action claim / "
                f"{step_id} 领取动作前必须处于 DOING"
            )
        step = self._steps()[step_id]
        effect = step["effect"]
        if effect["class"] == "read_only":
            raise PlanStateError(
                f"{step_id} is read-only and needs no idempotency claim / "
                f"{step_id} 是只读步骤，无需幂等领取"
            )
        _require_sha256(request_digest, "request_digest")
        key = effect["idempotency_key"]
        existing = self._idempotency.get(key)
        if existing is not None:
            if (
                existing["step_id"] != step_id
                or existing["request_digest"] != request_digest
            ):
                raise IdempotencyConflictError(
                    f"idempotency key {key} has divergent content / "
                    f"幂等键 {key} 存在分歧内容"
                )
            status = existing["status"]
            if status == IdempotencyStatus.SUCCEEDED.value:
                return ActionClaim("reuse_succeeded", key, status)
            if status == IdempotencyStatus.UNKNOWN.value:
                return ActionClaim("verify_required", key, status)
            if status == IdempotencyStatus.IN_PROGRESS.value:
                return ActionClaim("already_claimed", key, status)
            existing.update(
                {
                    "status": IdempotencyStatus.IN_PROGRESS.value,
                    "provider_ref": None,
                    "result_digest": None,
                }
            )
            disposition = "retry_allowed"
        else:
            self._idempotency[key] = {
                "idempotency_key": key,
                "step_id": step_id,
                "request_digest": request_digest,
                "status": IdempotencyStatus.IN_PROGRESS.value,
                "provider_ref": None,
                "result_digest": None,
            }
            status = None
            disposition = "execute"
        self._emit(
            "action_claimed",
            occurred_at=occurred_at,
            step_id=step_id,
            idempotency_key=key,
            disposition=disposition,
        )
        return ActionClaim(disposition, key, status)

    def record_action_result(
        self,
        step_id: str,
        *,
        status: IdempotencyStatus | str,
        provider_ref: str | None,
        result_digest: str | None,
        occurred_at: str | None = None,
    ) -> None:
        step = self._steps()[step_id]
        key = step["effect"]["idempotency_key"]
        if not key or key not in self._idempotency:
            raise PlanStateError(
                f"{step_id} has no action claim / {step_id} 没有动作领取记录"
            )
        normalized = IdempotencyStatus(status).value
        if normalized == IdempotencyStatus.IN_PROGRESS.value:
            raise PlanStateError(
                "action result cannot remain in_progress / 动作结果不能仍为 in_progress"
            )
        ledger = self._idempotency[key]
        if ledger["status"] == IdempotencyStatus.SUCCEEDED.value:
            if (
                normalized != IdempotencyStatus.SUCCEEDED.value
                or ledger["provider_ref"] != provider_ref
                or ledger["result_digest"] != result_digest
            ):
                raise IdempotencyConflictError(
                    f"successful result for {key} is immutable / "
                    f"{key} 的成功结果不可变"
                )
            return
        record = self._record(step_id)
        if record["state"] != StepState.DOING.value:
            raise PlanStateError(
                f"{step_id} must be DOING when recording an action result / "
                f"{step_id} 记录动作结果时必须处于 DOING"
            )
        if result_digest is not None:
            _require_sha256(result_digest, "result_digest")
        ledger.update(
            {
                "status": normalized,
                "provider_ref": provider_ref,
                "result_digest": result_digest,
            }
        )
        if provider_ref:
            record["external_receipts"] = sorted(
                set(record["external_receipts"]) | {provider_ref}
            )
        if normalized == IdempotencyStatus.UNKNOWN.value:
            timestamp = occurred_at or _now()
            record["state"] = StepState.UNKNOWN.value
            record["updated_at"] = timestamp
            self._block_descendants(step_id, timestamp)
        elif normalized == IdempotencyStatus.FAILED.value:
            self.fail_step(
                step_id,
                error="action_failed",
                occurred_at=occurred_at,
            )
        self._emit(
            "action_result_recorded",
            occurred_at=occurred_at,
            step_id=step_id,
            idempotency_key=key,
            status=normalized,
        )

    def complete_step(
        self,
        step_id: str,
        *,
        output_digest: str,
        completion_evidence: Sequence[str],
        occurred_at: str | None = None,
    ) -> None:
        record = self._record(step_id)
        if record["state"] != StepState.DOING.value:
            raise PlanStateError(
                f"{step_id} must be DOING before DONE / "
                f"{step_id} 进入 DONE 前必须处于 DOING"
            )
        if not completion_evidence:
            raise PlanStateError(
                f"{step_id} completion needs observable evidence / "
                f"{step_id} 完成需要可观测证据"
            )
        _require_sha256(output_digest, "output_digest")
        step = self._steps()[step_id]
        if step["effect"]["class"] != "read_only":
            ledger = self._idempotency.get(step["effect"]["idempotency_key"])
            if ledger is None or ledger["status"] != IdempotencyStatus.SUCCEEDED.value:
                raise PlanStateError(
                    f"{step_id} side effect is not confirmed succeeded / "
                    f"{step_id} 的副作用尚未确认成功"
                )
        timestamp = occurred_at or _now()
        record.update(
            {
                "state": StepState.DONE.value,
                "updated_at": timestamp,
                "output_digest": output_digest,
                "completion_evidence": sorted(set(completion_evidence)),
                "error": None,
            }
        )
        self._release_dependency_blocks(timestamp)
        self._emit(
            "step_closed",
            occurred_at=timestamp,
            step_id=step_id,
            state=StepState.DONE.value,
            evidence_count=len(record["completion_evidence"]),
        )

    def _block_descendants(self, step_id: str, occurred_at: str) -> None:
        for descendant in _descendants(self._steps(), [step_id]) - {step_id}:
            record = self._records[descendant]
            if record["state"] == StepState.TODO.value:
                record["state"] = StepState.BLOCKED.value
                record["updated_at"] = occurred_at

    def _release_dependency_blocks(self, occurred_at: str) -> None:
        """Release only blocks whose dependencies are now all DONE.

        / 仅解除全部依赖现已 DONE 的阻塞。
        """

        steps = self._steps()
        changed = True
        while changed:
            changed = False
            for step_id, step in steps.items():
                record = self._records[step_id]
                if record["state"] != StepState.BLOCKED.value:
                    continue
                if all(
                    self._records[dependency]["state"] == StepState.DONE.value
                    for dependency in step["dependencies"]
                ):
                    record["state"] = StepState.TODO.value
                    record["updated_at"] = occurred_at
                    changed = True

    def fail_step(
        self,
        step_id: str,
        *,
        error: str,
        occurred_at: str | None = None,
    ) -> None:
        record = self._record(step_id)
        if record["state"] not in {
            StepState.DOING.value,
            StepState.VERIFYING.value,
        }:
            raise PlanStateError(
                f"{step_id} cannot fail from {record['state']} / "
                f"{step_id} 不能从 {record['state']} 进入 FAILED"
            )
        timestamp = occurred_at or _now()
        record.update(
            {
                "state": StepState.FAILED.value,
                "updated_at": timestamp,
                "error": error,
            }
        )
        self._block_descendants(step_id, timestamp)
        self._emit(
            "step_closed",
            occurred_at=timestamp,
            step_id=step_id,
            state=StepState.FAILED.value,
            error=error,
        )

    def begin_verification(
        self,
        step_id: str,
        *,
        occurred_at: str | None = None,
    ) -> None:
        record = self._record(step_id)
        if record["state"] != StepState.UNKNOWN.value:
            raise PlanStateError(
                f"{step_id} must be UNKNOWN before VERIFYING / "
                f"{step_id} 进入 VERIFYING 前必须处于 UNKNOWN"
            )
        timestamp = occurred_at or _now()
        record["state"] = StepState.VERIFYING.value
        record["updated_at"] = timestamp
        self._emit(
            "verification_started",
            occurred_at=timestamp,
            step_id=step_id,
        )

    def resolve_verification(
        self,
        step_id: str,
        *,
        confirmed_succeeded: bool,
        provider_ref: str,
        result_digest: str | None,
        evidence_refs: Sequence[str],
        error: str | None = None,
        occurred_at: str | None = None,
    ) -> None:
        record = self._record(step_id)
        if record["state"] != StepState.VERIFYING.value:
            raise PlanStateError(
                f"{step_id} must be VERIFYING / {step_id} 必须处于 VERIFYING"
            )
        if not evidence_refs:
            raise PlanStateError(
                "verification needs evidence / 核验必须提供证据"
            )
        step = self._steps()[step_id]
        key = step["effect"]["idempotency_key"]
        ledger = self._idempotency.get(key)
        if ledger is None or ledger["status"] != IdempotencyStatus.UNKNOWN.value:
            raise PlanStateError(
                f"{step_id} has no UNKNOWN action ledger / "
                f"{step_id} 没有 UNKNOWN 动作账"
            )
        timestamp = occurred_at or _now()
        if confirmed_succeeded and result_digest is None:
            raise PlanStateError(
                "confirmed success needs result_digest / "
                "确认成功必须提供 result_digest"
            )
        if result_digest is not None:
            _require_sha256(result_digest, "result_digest")
        ledger.update(
            {
                "status": (
                    IdempotencyStatus.SUCCEEDED.value
                    if confirmed_succeeded
                    else IdempotencyStatus.FAILED.value
                ),
                "provider_ref": provider_ref,
                "result_digest": result_digest,
            }
        )
        record["external_receipts"] = sorted(
            set(record["external_receipts"]) | {provider_ref}
        )
        if confirmed_succeeded:
            record.update(
                {
                    "state": StepState.DONE.value,
                    "updated_at": timestamp,
                    "output_digest": result_digest,
                    "completion_evidence": sorted(set(evidence_refs)),
                    "error": None,
                }
            )
            self._release_dependency_blocks(timestamp)
        else:
            record.update(
                {
                    "state": StepState.FAILED.value,
                    "updated_at": timestamp,
                    "error": error or "verification_confirmed_failure",
                    "completion_evidence": sorted(set(evidence_refs)),
                }
            )
            self._block_descendants(step_id, timestamp)
        self._emit(
            "verification_completed",
            occurred_at=timestamp,
            step_id=step_id,
            confirmed_succeeded=confirmed_succeeded,
        )

    def apply_patch(
        self,
        patch: Mapping[str, Any],
        *,
        occurred_at: str | None = None,
    ) -> None:
        """Apply a validated local patch without rewriting DONE facts.

        / 应用已校验局部补丁，且不改写 DONE 事实。
        """

        validate_workflow_plan_patch(patch)
        if (
            patch["plan_id"] != self.plan["plan_id"]
            or patch["base_revision"] != self.plan["revision"]
            or patch["base_plan_hash"] != self.plan["plan_hash"]
        ):
            raise PlanPatchError(
                "patch base does not match current plan / 补丁基线与当前计划不匹配"
            )
        if self.replan_count >= self.plan["stop_conditions"]["max_replans"]:
            raise PlanPatchError(
                "maximum replans reached / 已达到最大重规划次数"
            )
        for root in patch["failed_root_step_ids"]:
            if self._record(root)["state"] != StepState.FAILED.value:
                raise PlanPatchError(
                    f"patch root {root} is not FAILED / 补丁根节点 {root} 不是 FAILED"
                )
        for step_id in patch["affected_step_ids"]:
            state = self._record(step_id)["state"]
            if state in {
                StepState.DONE.value,
                StepState.DOING.value,
                StepState.UNKNOWN.value,
                StepState.VERIFYING.value,
            }:
                raise PlanPatchError(
                    f"patch cannot overwrite {step_id} in {state} / "
                    f"补丁不得覆盖处于 {state} 的 {step_id}"
                )

        candidate = _candidate_plan_from_patch(self.plan, patch)
        old_records = deepcopy(self._records)
        affected = set(patch["affected_step_ids"])
        timestamp = occurred_at or _now()
        self.plan = candidate
        self._records = {}
        for step in self.plan["steps"]:
            step_id = step["step_id"]
            if step_id in old_records and step_id not in affected:
                self._records[step_id] = old_records[step_id]
            else:
                attempt = old_records.get(step_id, {}).get("attempt", 0)
                self._records[step_id] = {
                    "step_id": step_id,
                    "state": StepState.TODO.value,
                    "attempt": attempt,
                    "started_at": None,
                    "updated_at": timestamp,
                    "output_digest": None,
                    "completion_evidence": [],
                    "error": None,
                    "external_receipts": deepcopy(
                        old_records.get(step_id, {}).get("external_receipts", [])
                    ),
                }
        self.replan_count += 1
        self._emit(
            "plan_patched",
            occurred_at=timestamp,
            patch_id=patch["patch_id"],
            affected_step_ids=list(patch["affected_step_ids"]),
            blast_radius=len(affected) / len(old_records),
        )

    def checkpoint(
        self,
        *,
        checkpoint_id: str,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """Seal a portable recovery snapshot / 封存可移植恢复快照。"""

        artifact = {
            "schema_version": "1.0.0",
            "checkpoint_id": checkpoint_id,
            "run_id": self.run_id,
            "plan_binding": {
                "plan_id": self.plan["plan_id"],
                "revision": self.plan["revision"],
                "hash": self.plan["plan_hash"],
            },
            "goal_binding": deepcopy(self.plan["goal_binding"]),
            "step_records": list(self.step_records),
            "idempotency_records": list(self.idempotency_records),
            "replan_count": self.replan_count,
            "last_event_sequence": self._sequence,
            "created_at": created_at or _now(),
        }
        try:
            return build_artifact("workflow_checkpoint", artifact)
        except ArtifactValidationError as error:
            raise PlanStateError(str(error)) from error

    @classmethod
    def from_checkpoint(
        cls,
        plan: Mapping[str, Any],
        checkpoint: Mapping[str, Any],
    ) -> "PlanExecutionSession":
        """Restore safely; never replay an interrupted write implicitly.

        Interrupted read-only work returns to TODO. Interrupted writes become
        UNKNOWN and require verification.
        / 安全恢复：绝不隐式重放中断写动作。中断只读步骤回到 TODO，中断写步骤
        进入 UNKNOWN 并必须核验。
        """

        validate_workflow_plan(plan)
        validate_workflow_checkpoint(checkpoint)
        binding = checkpoint["plan_binding"]
        if (
            binding["plan_id"] != plan["plan_id"]
            or binding["revision"] != plan["revision"]
            or binding["hash"] != plan["plan_hash"]
            or checkpoint["goal_binding"] != plan["goal_binding"]
        ):
            raise PlanStateError(
                "checkpoint does not bind the supplied plan / "
                "检查点未绑定所提供计划"
            )
        session = cls(
            plan,
            run_id=checkpoint["run_id"],
            started_at=checkpoint["created_at"],
        )
        session._events = []
        session._sequence = checkpoint["last_event_sequence"]
        session.replan_count = checkpoint["replan_count"]
        session._records = {
            record["step_id"]: deepcopy(dict(record))
            for record in checkpoint["step_records"]
        }
        session._idempotency = {
            record["idempotency_key"]: deepcopy(dict(record))
            for record in checkpoint["idempotency_records"]
        }
        steps = session._steps()
        if set(session._records) != set(steps):
            raise PlanStateError(
                "checkpoint step inventory differs from plan / "
                "检查点步骤清单与计划不一致"
            )
        timestamp = checkpoint["created_at"]
        for step_id, record in session._records.items():
            if record["state"] != StepState.DOING.value:
                continue
            if steps[step_id]["effect"]["class"] == "read_only":
                record["state"] = StepState.TODO.value
                record["started_at"] = None
                record["updated_at"] = timestamp
                session._emit(
                    "step_recovered",
                    occurred_at=timestamp,
                    step_id=step_id,
                    from_state=StepState.DOING.value,
                    to_state=StepState.TODO.value,
                    reason_code="interrupted_read_safe_to_retry",
                )
            else:
                key = steps[step_id]["effect"]["idempotency_key"]
                ledger = session._idempotency.get(key)
                if ledger is None:
                    raise PlanStateError(
                        f"interrupted write {step_id} lacks idempotency record / "
                        f"中断写步骤 {step_id} 缺少幂等记录"
                    )
                if ledger["status"] == IdempotencyStatus.SUCCEEDED.value:
                    # Keep DOING so completion can consume the confirmed result;
                    # a repeated claim returns reuse_succeeded.
                    # / 保持 DOING，以便完成步骤消费已确认结果；重复领取会返回复用成功。
                    record["updated_at"] = timestamp
                else:
                    record["state"] = StepState.UNKNOWN.value
                    ledger["status"] = IdempotencyStatus.UNKNOWN.value
                    record["updated_at"] = timestamp
                    session._emit(
                        "action_result_recorded",
                        occurred_at=timestamp,
                        step_id=step_id,
                        idempotency_key=key,
                        status=IdempotencyStatus.UNKNOWN.value,
                        reason_code="interrupted_write_requires_reconciliation",
                    )
        return session

    def is_complete(self) -> bool:
        """Return true only when every step is DONE / 仅当所有步骤均 DONE 时返回真。"""

        return all(
            record["state"] == StepState.DONE.value
            for record in self._records.values()
        )


__all__ = [
    "ActionClaim",
    "IdempotencyConflictError",
    "IdempotencyStatus",
    "PlanExecutionError",
    "PlanExecutionSession",
    "PlanPatchError",
    "PlanStateError",
    "PlanValidationError",
    "StepState",
    "compile_goal_contract",
    "compile_workflow_plan",
    "compile_workflow_plan_patch",
    "validate_goal_contract",
    "validate_workflow_checkpoint",
    "validate_workflow_plan",
    "validate_workflow_plan_patch",
]
