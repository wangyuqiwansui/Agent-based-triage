"""Replayable branch leases and deadlines / 可重放的分支租约与截止时间。

The scheduler owns only public control-plane facts. It never executes branch
work and never records private reasoning. Lease compare-and-set decisions run
inside the event-store transaction so the SQLite adapter serializes competing
writers. / 调度器只管理公开控制面事实，不执行分支工作，也不记录私密推理。租约
比较并设置决定位于事件库事务内，因此 SQLite 适配器能够串行化竞争写者。
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import time
from typing import Any, Callable, Iterable, Mapping

try:  # Package import / 包导入
    from .reasoning_parallel_factory import (
        ParallelBranchOutcome,
        ParallelPlanSession,
        ParallelPlanStateError,
    )
    from .reasoning_runtime import (
        BudgetUsage,
        WorkflowState,
        _canonical_json,
        _iso_utc,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_parallel_factory import (
        ParallelBranchOutcome,
        ParallelPlanSession,
        ParallelPlanStateError,
    )
    from reasoning_runtime import BudgetUsage, WorkflowState, _canonical_json, _iso_utc


_ACTIVE_PHASES = {"acquired", "renewed"}
_LEASE_PHASES = _ACTIVE_PHASES | {"released", "expired"}


def _copy(value: Any) -> Any:
    return json.loads(_canonical_json(value))


@dataclass(frozen=True)
class ParallelPathLease:
    """Latest replayed lease state for one branch / 单个分支最新重放租约状态。"""

    candidate_path_id: str
    lease_id: str
    worker_binding: Mapping[str, str]
    revision: int
    fencing_token: int
    phase: str
    acquired_at: str
    expires_at: str
    deadline_at: str | None

    @property
    def active(self) -> bool:
        return self.phase in _ACTIVE_PHASES


@dataclass(frozen=True)
class ParallelDeadlineOutcome:
    """Public result of one due-work sweep / 一次到期扫描的公开结果。"""

    expired_candidate_path_ids: tuple[str, ...]
    deadline_reached: bool
    next_action: str
    state: WorkflowState


class ParallelPathScheduler:
    """Coordinate branch leases and apply the compiled deadline policy.

    / 协调分支租约并执行已编译的截止时间策略。
    """

    def __init__(
        self,
        session: ParallelPlanSession,
        *,
        deadline_at: float | str | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if not isinstance(session, ParallelPlanSession):
            raise TypeError(
                "session must be ParallelPlanSession / session 必须为 ParallelPlanSession"
            )
        if clock is not None and not callable(clock):
            raise TypeError("clock must be callable / 时钟必须可调用")
        self.session = session
        self.engine = session.engine
        self.run_id = session.run_id
        self._clock = clock or time.time
        if deadline_at is None:
            self.deadline_at = None
            self._deadline_epoch = None
        else:
            self.deadline_at, self._deadline_epoch = _iso_utc(deadline_at)
        self._validate_history()

    def _now(self, value: float | str | None) -> tuple[str, float]:
        raw = self._clock() if value is None else value
        if isinstance(raw, bool):
            raise TypeError("scheduler time cannot be boolean / 调度时间不能是布尔值")
        return _iso_utc(raw)

    @staticmethod
    def _ttl(ttl_seconds: float) -> float:
        if (
            isinstance(ttl_seconds, bool)
            or not isinstance(ttl_seconds, (int, float))
            or not math.isfinite(float(ttl_seconds))
            or float(ttl_seconds) <= 0
        ):
            raise ValueError("ttl_seconds must be finite and positive / TTL 必须为有限正数")
        return float(ttl_seconds)

    def _branch(self, candidate_path_id: str) -> Mapping[str, Any]:
        try:
            return self.session._branches[candidate_path_id]
        except KeyError as exc:
            raise ParallelPlanStateError(
                f"unknown candidate path / 未知候选路径: {candidate_path_id}"
            ) from exc

    def _validate_history(self) -> None:
        for event in self.engine.events.events(self.run_id):
            if event.event_type != "parallel_path_updated":
                continue
            if event.payload.get("plan_binding") != self.session.plan_binding:
                raise ParallelPlanStateError(
                    "parallel path event plan binding drift / 并行路径事件计划绑定漂移"
                )
            if event.payload.get("deadline_at") != self.deadline_at:
                raise ParallelPlanStateError(
                    "parallel scheduler deadline drift / 并行调度截止时间漂移"
                )
        self._lease_states()

    def _path_events(self, candidate_path_id: str) -> tuple[Any, ...]:
        return tuple(
            event
            for event in self.engine.events.events(self.run_id)
            if event.as_dict().get("candidate_path_id") == candidate_path_id
        )

    def _path_started_and_open(self, candidate_path_id: str) -> bool:
        branch = self._branch(candidate_path_id)
        events = self._path_events(candidate_path_id)
        started = any(
            event.event_type == "step_started"
            and event.as_dict().get("step_id") == branch["branch_step_id"]
            for event in events
        )
        closed = any(
            event.event_type == "step_closed"
            and event.as_dict().get("step_id") == branch["branch_step_id"]
            for event in events
        )
        return started and not closed

    def _lease_states(self) -> dict[str, ParallelPathLease]:
        states: dict[str, ParallelPathLease] = {}
        for event in self.engine.events.events(self.run_id):
            if event.event_type != "parallel_path_updated":
                continue
            payload = event.payload
            phase = payload["phase"]
            if phase not in _LEASE_PHASES:
                continue
            path = event.as_dict()["candidate_path_id"]
            prior = states.get(path)
            raw_fencing_token = payload.get("fencing_token")
            if raw_fencing_token is None:
                # Backward-compatible replay for events written before fencing
                # tokens were persisted. / 兼容重放引入栅栏令牌前写入的事件。
                fencing_token = (
                    (1 if prior is None else prior.fencing_token + 1)
                    if phase == "acquired"
                    else (1 if prior is None else prior.fencing_token)
                )
            else:
                fencing_token = int(raw_fencing_token)
            candidate = ParallelPathLease(
                candidate_path_id=path,
                lease_id=payload["lease_id"],
                worker_binding=_copy(payload["worker_binding"]),
                revision=int(payload["lease_revision"]),
                fencing_token=fencing_token,
                phase=phase,
                acquired_at=payload["acquired_at"],
                expires_at=payload["expires_at"],
                deadline_at=payload["deadline_at"],
            )
            if phase == "acquired":
                expected_fencing_token = (
                    1 if prior is None else prior.fencing_token + 1
                )
                if (
                    candidate.revision != 1
                    or candidate.fencing_token != expected_fencing_token
                    or (prior is not None and prior.active)
                ):
                    raise ParallelPlanStateError(
                        "invalid acquired lease history / 获取租约历史无效"
                    )
            else:
                if (
                    prior is None
                    or not prior.active
                    or candidate.lease_id != prior.lease_id
                    or candidate.worker_binding != prior.worker_binding
                    or candidate.acquired_at != prior.acquired_at
                    or candidate.revision != prior.revision + 1
                    or candidate.fencing_token != prior.fencing_token
                ):
                    raise ParallelPlanStateError(
                        "non-contiguous lease history / 租约历史不连续"
                    )
            states[path] = candidate
        return states

    def lease(self, candidate_path_id: str) -> ParallelPathLease | None:
        """Return the latest replayed lease for a branch / 返回分支最新重放租约。"""

        self._branch(candidate_path_id)
        return self._lease_states().get(candidate_path_id)

    def _expiry(self, now_epoch: float, ttl_seconds: float) -> tuple[str, float]:
        expiry = now_epoch + self._ttl(ttl_seconds)
        if self._deadline_epoch is not None:
            expiry = min(expiry, self._deadline_epoch)
        return _iso_utc(expiry)

    def acquire(
        self,
        candidate_path_id: str,
        *,
        lease_id: str,
        worker_binding: Mapping[str, Any],
        ttl_seconds: float,
        now: float | str | None = None,
    ) -> ParallelPathLease:
        """Atomically acquire an open branch / 原子获取一个开放分支。"""

        branch = self._branch(candidate_path_id)
        observed_at, observed_epoch = self._now(now)
        if self._deadline_epoch is not None and observed_epoch >= self._deadline_epoch:
            raise ParallelPlanStateError(
                "plan deadline has been reached; sweep due work first / "
                "计划已到截止时间；请先执行到期扫描"
            )
        with self.engine.events.transaction(self.run_id):
            if not self._path_started_and_open(candidate_path_id):
                raise ParallelPlanStateError(
                    "lease requires a started open branch / 租约要求分支已启动且未关闭"
                )
            current = self._lease_states().get(candidate_path_id)
            if current is not None and current.active:
                _, expires_epoch = _iso_utc(current.expires_at)
                if expires_epoch <= observed_epoch:
                    raise ParallelPlanStateError(
                        "expired lease must be swept before reacquisition / "
                        "过期租约必须先完成到期扫描再重新获取"
                    )
                raise ParallelPlanStateError(
                    "branch already has an active lease / 分支已有活动租约"
                )
            expires_at, _ = self._expiry(observed_epoch, ttl_seconds)
            fencing_token = 1 if current is None else current.fencing_token + 1
            self.engine.record_parallel_path_update(
                self.run_id,
                candidate_path_id=candidate_path_id,
                step_id=branch["branch_step_id"],
                plan_binding=self.session.plan_binding,
                phase="acquired",
                observed_at=observed_at,
                deadline_at=self.deadline_at,
                lease_id=lease_id,
                worker_binding=worker_binding,
                lease_revision=1,
                fencing_token=fencing_token,
                acquired_at=observed_at,
                expires_at=expires_at,
                idempotency_key=f"parallel-lease:{lease_id}:1:acquired",
            )
            return self._lease_states()[candidate_path_id]

    def renew(
        self,
        candidate_path_id: str,
        *,
        lease_id: str,
        worker_binding: Mapping[str, Any],
        fencing_token: int,
        ttl_seconds: float,
        now: float | str | None = None,
    ) -> ParallelPathLease:
        """Renew only the current unexpired lease holder / 仅续约当前未过期的租约持有者。"""

        branch = self._branch(candidate_path_id)
        observed_at, observed_epoch = self._now(now)
        with self.engine.events.transaction(self.run_id):
            current = self._lease_states().get(candidate_path_id)
            if (
                current is None
                or not current.active
                or current.lease_id != lease_id
                or current.worker_binding != _copy(dict(worker_binding))
                or current.fencing_token != fencing_token
            ):
                raise ParallelPlanStateError(
                    "renewal does not match the active lease holder / "
                    "续约请求与活动租约持有者不匹配"
                )
            _, current_expiry = _iso_utc(current.expires_at)
            if current_expiry <= observed_epoch or (
                self._deadline_epoch is not None
                and observed_epoch >= self._deadline_epoch
            ):
                raise ParallelPlanStateError(
                    "expired lease cannot be renewed / 过期租约不能续约"
                )
            expires_at, _ = self._expiry(observed_epoch, ttl_seconds)
            revision = current.revision + 1
            self.engine.record_parallel_path_update(
                self.run_id,
                candidate_path_id=candidate_path_id,
                step_id=branch["branch_step_id"],
                plan_binding=self.session.plan_binding,
                phase="renewed",
                observed_at=observed_at,
                deadline_at=self.deadline_at,
                lease_id=lease_id,
                worker_binding=worker_binding,
                lease_revision=revision,
                fencing_token=current.fencing_token,
                acquired_at=current.acquired_at,
                expires_at=expires_at,
                idempotency_key=f"parallel-lease:{lease_id}:{revision}:renewed",
            )
            return self._lease_states()[candidate_path_id]

    def release(
        self,
        candidate_path_id: str,
        *,
        lease_id: str,
        worker_binding: Mapping[str, Any],
        fencing_token: int,
        reason: str = "worker released branch / 工作者释放分支",
        now: float | str | None = None,
    ) -> ParallelPathLease:
        """Release only the current lease holder / 仅允许当前租约持有者释放。"""

        branch = self._branch(candidate_path_id)
        observed_at, observed_epoch = self._now(now)
        with self.engine.events.transaction(self.run_id):
            current = self._lease_states().get(candidate_path_id)
            if (
                current is None
                or not current.active
                or current.lease_id != lease_id
                or current.worker_binding != _copy(dict(worker_binding))
                or current.fencing_token != fencing_token
            ):
                raise ParallelPlanStateError(
                    "release does not match the active lease holder / "
                    "释放请求与活动租约持有者不匹配"
                )
            _, expiry_epoch = _iso_utc(current.expires_at)
            if expiry_epoch <= observed_epoch or (
                self._deadline_epoch is not None
                and observed_epoch >= self._deadline_epoch
            ):
                raise ParallelPlanStateError(
                    "expired lease cannot be released by its stale holder / "
                    "过期租约不能由陈旧持有者释放"
                )
            revision = current.revision + 1
            self.engine.record_parallel_path_update(
                self.run_id,
                candidate_path_id=candidate_path_id,
                step_id=branch["branch_step_id"],
                plan_binding=self.session.plan_binding,
                phase="released",
                observed_at=observed_at,
                deadline_at=self.deadline_at,
                lease_id=lease_id,
                worker_binding=worker_binding,
                lease_revision=revision,
                fencing_token=current.fencing_token,
                acquired_at=current.acquired_at,
                expires_at=current.expires_at,
                reason=reason,
                idempotency_key=f"parallel-lease:{lease_id}:{revision}:released",
            )
            return self._lease_states()[candidate_path_id]

    def close_leased_branch(
        self,
        candidate_path_id: str,
        *,
        lease_id: str,
        worker_binding: Mapping[str, Any],
        fencing_token: int,
        status: str,
        candidate: Any | None = None,
        evidence_records: Iterable[Mapping[str, Any]] = (),
        criterion_results: Iterable[Mapping[str, Any]] = (),
        veto_results: Iterable[Mapping[str, Any]] = (),
        elimination_reason: str | None = None,
        resource_use: BudgetUsage | Mapping[str, Any] | None = None,
        information_gain: float | None = None,
        now: float | str | None = None,
    ) -> ParallelBranchOutcome:
        """Submit a branch terminal only for its current unexpired lease holder.

        Lease release and branch closure share one event-store transaction. A
        validation failure rolls both changes back, while a stale or reassigned
        worker cannot publish a terminal result. / 仅允许当前未过期租约的持有者提交
        分支终态。租约释放与分支关闭共享同一事件库事务；验证失败会同时回滚两者，
        陈旧或已被替换的工作者不能发布终态结果。
        """

        self._branch(candidate_path_id)
        observed_at, observed_epoch = self._now(now)
        with self.engine.events.transaction(self.run_id):
            if not self._path_started_and_open(candidate_path_id):
                raise ParallelPlanStateError(
                    "submission requires a started open branch / 提交要求分支已启动且未关闭"
                )
            current = self._lease_states().get(candidate_path_id)
            if (
                current is None
                or not current.active
                or current.lease_id != lease_id
                or current.worker_binding != _copy(dict(worker_binding))
                or current.fencing_token != fencing_token
            ):
                raise ParallelPlanStateError(
                    "submission does not match the active lease holder / "
                    "提交请求与活动租约持有者不匹配"
                )
            _, expiry_epoch = _iso_utc(current.expires_at)
            if expiry_epoch <= observed_epoch or (
                self._deadline_epoch is not None
                and observed_epoch >= self._deadline_epoch
            ):
                raise ParallelPlanStateError(
                    "expired lease cannot submit a branch result / "
                    "过期租约不能提交分支结果"
                )
            self.release(
                candidate_path_id,
                lease_id=lease_id,
                worker_binding=worker_binding,
                fencing_token=fencing_token,
                reason="branch result submitted / 分支结果已提交",
                now=observed_at,
            )
            return self.session.close_branch(
                candidate_path_id,
                status=status,
                candidate=candidate,
                evidence_records=evidence_records,
                criterion_results=criterion_results,
                veto_results=veto_results,
                elimination_reason=elimination_reason,
                resource_use=resource_use,
                information_gain=information_gain,
            )

    def _timeout_usage(self) -> BudgetUsage:
        return BudgetUsage(paths=1)

    def _timeout_gain(self) -> float | None:
        thresholds = [
            float(condition["min_information_gain"])
            for condition in self.session.contract["stop_conditions"]
            if condition["type"] == "no_progress"
        ]
        # Closing an abandoned branch advances the public join state even when
        # it yields no domain evidence. / 关闭被放弃分支会推进公开汇合状态，即使没有
        # 新增领域证据。
        return max(thresholds) if thresholds else None

    def _sweep_path(
        self,
        candidate_path_id: str,
        *,
        observed_at: str,
        observed_epoch: float,
        deadline_reached: bool,
    ) -> bool:
        branch = self._branch(candidate_path_id)
        with self.engine.events.transaction(self.run_id):
            if not self._path_started_and_open(candidate_path_id):
                return False
            current = self._lease_states().get(candidate_path_id)
            if deadline_reached:
                self.engine.record_parallel_path_update(
                    self.run_id,
                    candidate_path_id=candidate_path_id,
                    step_id=branch["branch_step_id"],
                    plan_binding=self.session.plan_binding,
                    phase="deadline_reached",
                    observed_at=observed_at,
                    deadline_at=self.deadline_at,
                    reason="parallel plan deadline reached / 并行计划到达截止时间",
                    idempotency_key=(
                        f"parallel-deadline:{self.session.plan['plan_id']}:"
                        f"{candidate_path_id}"
                    ),
                )
                reason = "plan deadline reached / 计划到达截止时间"
            else:
                if current is None or not current.active:
                    return False
                _, expiry_epoch = _iso_utc(current.expires_at)
                if expiry_epoch > observed_epoch:
                    return False
                revision = current.revision + 1
                self.engine.record_parallel_path_update(
                    self.run_id,
                    candidate_path_id=candidate_path_id,
                    step_id=branch["branch_step_id"],
                    plan_binding=self.session.plan_binding,
                    phase="expired",
                    observed_at=observed_at,
                    deadline_at=self.deadline_at,
                    lease_id=current.lease_id,
                    worker_binding=current.worker_binding,
                    lease_revision=revision,
                    fencing_token=current.fencing_token,
                    acquired_at=current.acquired_at,
                    expires_at=current.expires_at,
                    reason="branch lease expired / 分支租约已过期",
                    idempotency_key=(
                        f"parallel-lease:{current.lease_id}:{revision}:expired"
                    ),
                )
                # A worker lease is ownership, not the logical branch. TTL
                # expiry makes the open branch eligible for reassignment while
                # preserving its wave reservation. / 工作者租约只是所有权，不是
                # 逻辑分支。TTL 到期后开放分支可被重新领取，并保留波次预算预留。
                return True
            reason = "plan deadline reached / 计划到达截止时间"
            self.session.close_branch(
                candidate_path_id,
                status="timed_out",
                elimination_reason=reason,
                resource_use=self._timeout_usage(),
                information_gain=self._timeout_gain(),
            )
            return True

    def sweep_due(self, *, now: float | str | None = None) -> ParallelDeadlineOutcome:
        """Expire due leases, close deadline paths, and apply deadline policy.

        / 使到期租约失效、关闭截止分支并执行截止策略。
        """

        observed_at, observed_epoch = self._now(now)
        deadline_reached = (
            self._deadline_epoch is not None
            and observed_epoch >= self._deadline_epoch
        )
        expired: list[str] = []
        for branch in self.session.plan["branches"]:
            path = branch["candidate_path_id"]
            if self._sweep_path(
                path,
                observed_at=observed_at,
                observed_epoch=observed_epoch,
                deadline_reached=deadline_reached,
            ):
                expired.append(path)

        next_action = (
            "reassign_expired_paths" if expired and not deadline_reached
            else "continue_parallel_work"
        )
        if deadline_reached:
            policy = self.session.plan["join_policy"]["on_deadline"]
            snapshot = self.engine.snapshot(self.run_id)
            if policy == "proceed_with_quorum":
                history = self.session._branch_events()
                completed = sum(
                    entry["candidate"] is not None
                    and entry["close"].payload["local_decision"]["branch_status"]
                    == "completed"
                    for entry in history.values()
                    if entry["close"] is not None
                )
                minimum = self.session.plan["join_policy"][
                    "minimum_completed_branches"
                ]
                if completed >= minimum and snapshot.state is WorkflowState.EXECUTING:
                    next_action = "synthesize_with_quorum"
                elif snapshot.state is WorkflowState.EXECUTING:
                    self.engine.transition(
                        self.run_id,
                        WorkflowState.FAILED,
                        reason=(
                            "deadline quorum was not satisfied / "
                            "截止时间到达但法定完成数未满足"
                        ),
                    )
                    next_action = "terminal_failed_quorum"
            elif policy == "escalate":
                if snapshot.state is WorkflowState.EXECUTING:
                    self.engine.transition(
                        self.run_id,
                        WorkflowState.ESCALATED,
                        reason="parallel deadline requires authority / 并行截止需要权限裁决",
                    )
                next_action = "terminal_escalated"
            elif policy == "fail":
                if snapshot.state is WorkflowState.EXECUTING:
                    self.engine.transition(
                        self.run_id,
                        WorkflowState.FAILED,
                        reason="parallel deadline failed closed / 并行截止默认失败关闭",
                    )
                next_action = "terminal_failed_deadline"
        return ParallelDeadlineOutcome(
            expired_candidate_path_ids=tuple(expired),
            deadline_reached=deadline_reached,
            next_action=next_action,
            state=self.engine.snapshot(self.run_id).state,
        )


__all__ = [
    "ParallelDeadlineOutcome",
    "ParallelPathLease",
    "ParallelPathScheduler",
]
