"""Deterministic reasoning protocol kernel / 确定性推理协议内核。

The module turns the documentation contract into a small executable reference:
an explicit state machine, append-only events, atomic multi-dimensional budgets,
candidate-bound validation, closable steps, stop rules, and replay. It performs
no network, model, tool, or business action. All inputs are externally
verifiable artifacts; private chain-of-thought is structurally rejected. /
本模块把文档契约落成一个小型可执行参考：显式状态机、仅追加事件、原子多维预算、
候选绑定验证、可关闭步骤、停止规则与重放。它不执行网络、模型、工具或业务动作；
所有输入都必须是外部可核验产物，结构上拒绝私密思维过程。
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import re
from types import MappingProxyType
import threading
import time
from typing import Any, Callable, Iterable, Iterator, Mapping, Sequence
import uuid

from jsonschema import Draft202012Validator, FormatChecker

try:  # Package import / 包导入
    from .reasoning_artifacts import (
        build_artifact,
        evidence_sufficiency_failures,
        validate_reasoning_contract,
        validate_reasoning_result,
    )
except ImportError:  # Direct module import used by conformance tests / 一致性测试使用直接模块导入
    from reasoning_artifacts import (
        build_artifact,
        evidence_sufficiency_failures,
        validate_reasoning_contract,
        validate_reasoning_result,
    )


class ReasoningRuntimeError(RuntimeError):
    """Base runtime error / 运行时基础错误。"""


class IllegalTransitionError(ReasoningRuntimeError):
    """Raised for a state transition outside the authoritative table / 非法状态转换。"""


class DuplicateEventConflictError(ReasoningRuntimeError):
    """Raised when a deduplication key is reused for different content / 去重键内容冲突。"""


class BudgetExceededError(ReasoningRuntimeError):
    """Raised before a budget operation could exceed a configured limit / 预算越界前拒绝。"""


class ValidationGateError(ReasoningRuntimeError):
    """Raised when completion does not satisfy every mandatory validator / 必选验证闸门未通过。"""


class CandidateRequiredError(ValidationGateError):
    """Raised when completion is attempted without a candidate / 缺少候选结果。"""


class NoProgressLimitError(ReasoningRuntimeError):
    """Raised after the configured no-progress streak closes the run / 无进展阈值已关闭运行。"""


class PrivateReasoningCaptureError(ReasoningRuntimeError):
    """Raised when an input tries to persist private reasoning / 输入试图持久化私密推理。"""


class EventSchemaViolationError(ReasoningRuntimeError):
    """Raised before a non-conforming event can enter the store / 事件不符合契约时在入库前拒绝。"""


class EventStorePersistenceError(ReasoningRuntimeError):
    """Durable event storage could not be loaded or committed / 持久化事件库无法加载或提交。"""


class FeedbackBlockError(ReasoningRuntimeError):
    """Unresolved authorized probe feedback blocks a transition / 未解决的授权探针反馈阻断状态转换。"""


class FeedbackAuthorizationError(FeedbackBlockError):
    """A feedback resolution or exemption lacks live authority / 反馈解决或豁免缺少实时授权。"""


class ToolAuthorizationError(ReasoningRuntimeError):
    """A tool dispatch lacks a live verified authorization / 工具分派缺少实时验证授权。"""


class WorkflowState(str, Enum):
    """Authoritative workflow states / 权威工作流状态。"""

    RECEIVED = "received"
    NORMALIZED = "normalized"
    GOVERNANCE_PRECHECK = "governance_precheck"
    ROUTED = "routed"
    CONTRACT_ESTABLISHED = "contract_established"
    EXECUTING = "executing"
    WAITING_FOR_EVIDENCE = "waiting_for_evidence"
    MODE_SWITCHED = "mode_switched"
    CANDIDATE_READY = "candidate_ready"
    VALIDATING = "validating"
    REPAIRABLE_FAILURE = "repairable_failure"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class ValidationStatus(str, Enum):
    """Authoritative validator outcomes / 权威验证结果。"""

    NOT_RUN = "not_run"
    PASSED = "passed"
    CONDITIONALLY_PASSED = "conditionally_passed"
    REPAIRABLE_FAILURE = "repairable_failure"
    NONREPAIRABLE_FAILURE = "nonrepairable_failure"
    HUMAN_REQUIRED = "human_required"
    TIMED_OUT = "timed_out"


class RiskLevel(str, Enum):
    """Risk levels used by release and escalation gates / 放行与升级闸门使用的风险等级。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


_TERMINAL_STATES = frozenset(
    {
        WorkflowState.COMPLETED,
        WorkflowState.REJECTED,
        WorkflowState.FAILED,
        WorkflowState.ESCALATED,
        WorkflowState.CANCELLED,
        WorkflowState.TIMED_OUT,
    }
)


def _active_terminals() -> frozenset[WorkflowState]:
    return frozenset(
        {
            WorkflowState.REJECTED,
            WorkflowState.FAILED,
            WorkflowState.ESCALATED,
            WorkflowState.CANCELLED,
            WorkflowState.TIMED_OUT,
        }
    )


_ACTIVE_TERMINALS = _active_terminals()

# Every legal edge is explicit. Terminal states deliberately have no outgoing edge.
# 每条合法边均显式列出；终态刻意不允许任何出边。
ALLOWED_TRANSITIONS: Mapping[WorkflowState, frozenset[WorkflowState]] = MappingProxyType(
    {
        WorkflowState.RECEIVED: frozenset(
            {WorkflowState.NORMALIZED, WorkflowState.CANCELLED, WorkflowState.TIMED_OUT}
        ),
        WorkflowState.NORMALIZED: frozenset(
            {
                WorkflowState.GOVERNANCE_PRECHECK,
                WorkflowState.CANCELLED,
                WorkflowState.TIMED_OUT,
            }
        ),
        WorkflowState.GOVERNANCE_PRECHECK: frozenset(
            {
                WorkflowState.ROUTED,
                WorkflowState.REJECTED,
                WorkflowState.ESCALATED,
                WorkflowState.CANCELLED,
                WorkflowState.TIMED_OUT,
            }
        ),
        WorkflowState.ROUTED: frozenset(
            {
                WorkflowState.CONTRACT_ESTABLISHED,
                WorkflowState.FAILED,
                WorkflowState.ESCALATED,
                WorkflowState.CANCELLED,
                WorkflowState.TIMED_OUT,
            }
        ),
        WorkflowState.CONTRACT_ESTABLISHED: frozenset(
            {
                WorkflowState.EXECUTING,
                WorkflowState.FAILED,
                WorkflowState.ESCALATED,
                WorkflowState.CANCELLED,
                WorkflowState.TIMED_OUT,
            }
        ),
        WorkflowState.EXECUTING: frozenset(
            {
                WorkflowState.WAITING_FOR_EVIDENCE,
                WorkflowState.MODE_SWITCHED,
                WorkflowState.CANDIDATE_READY,
                *_ACTIVE_TERMINALS,
            }
        ),
        WorkflowState.WAITING_FOR_EVIDENCE: frozenset(
            {WorkflowState.EXECUTING, WorkflowState.MODE_SWITCHED, *_ACTIVE_TERMINALS}
        ),
        WorkflowState.MODE_SWITCHED: frozenset(
            {WorkflowState.EXECUTING, *_ACTIVE_TERMINALS}
        ),
        WorkflowState.CANDIDATE_READY: frozenset(
            {WorkflowState.VALIDATING, *_ACTIVE_TERMINALS}
        ),
        WorkflowState.VALIDATING: frozenset(
            {
                WorkflowState.COMPLETED,
                WorkflowState.REPAIRABLE_FAILURE,
                WorkflowState.FAILED,
                WorkflowState.ESCALATED,
                WorkflowState.CANCELLED,
                WorkflowState.TIMED_OUT,
            }
        ),
        WorkflowState.REPAIRABLE_FAILURE: frozenset(
            {WorkflowState.EXECUTING, *_ACTIVE_TERMINALS}
        ),
        WorkflowState.COMPLETED: frozenset(),
        WorkflowState.REJECTED: frozenset(),
        WorkflowState.FAILED: frozenset(),
        WorkflowState.ESCALATED: frozenset(),
        WorkflowState.CANCELLED: frozenset(),
        WorkflowState.TIMED_OUT: frozenset(),
    }
)


_PRIVATE_REASONING_KEYS = frozenset(
    {
        "chain_of_thought",
        "private_chain_of_thought",
        "private_cot",
        "hidden_reasoning",
        "internal_monologue",
        "reasoning_scratchpad",
        "scratchpad",
    }
)


def _normalized_key(value: object) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _assert_no_private_reasoning(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = _normalized_key(key)
            if normalized in _PRIVATE_REASONING_KEYS:
                raise PrivateReasoningCaptureError(
                    f"private reasoning field is forbidden / 禁止私密推理字段: {path}.{key}"
                )
            _assert_no_private_reasoning(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _assert_no_private_reasoning(nested, f"{path}[{index}]")


def _json_default(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "as_dict") and callable(value.as_dict):
        return value.as_dict()
    raise TypeError(f"value is not JSON serializable / 值不可 JSON 序列化: {type(value)!r}")


def _canonical_json(value: Any) -> str:
    _assert_no_private_reasoning(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=_json_default,
    )


def content_fingerprint(value: Any) -> str:
    """Return a stable SHA-256 hash for JSON-compatible content / 返回 JSON 内容的稳定 SHA-256。"""

    digest = hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def candidate_fingerprint(candidate: Any) -> str:
    """Fingerprint a candidate without recording private reasoning / 对候选产物生成指纹且不记录私密推理。"""

    return content_fingerprint(candidate)


def _artifact_id(prefix: str, digest: str) -> str:
    """Create a short stable identifier from a SHA-256 digest / 从 SHA-256 摘要创建短稳定标识。"""

    return f"{prefix}-{digest.removeprefix('sha256:')[:24]}"


def _versioned_binding(identifier: str, digest: str, version: str = "1.0.0") -> dict[str, str]:
    return {"id": identifier, "version": version, "hash": digest}


def candidate_binding_for(candidate: Any) -> dict[str, str]:
    """Return the deterministic public binding for a candidate / 返回候选产物的确定性公开绑定。"""

    digest = candidate_fingerprint(candidate)
    return _versioned_binding(_artifact_id("candidate", digest), digest)


def _observed_number(value: int | float | None) -> dict[str, Any]:
    if value is None:
        return {"state": "missing"}
    if value == 0:
        return {"state": "observed_zero", "value": 0}
    return {"state": "observed", "value": value}


def _positive_limit(value: int | float | None) -> dict[str, Any]:
    if value is None:
        return {"state": "missing"}
    return {"state": "observed", "value": value}


_BUDGET_FIELDS = (
    "tokens",
    "latency_ms",
    "model_calls",
    "tool_calls",
    "paths",
    "iterations",
    "retries",
    "cost_units",
)

_EVENT_BUDGET_NAMES = {
    "tokens": "reasoning_tokens",
    "latency_ms": "latency_ms",
    "model_calls": "model_calls",
    "tool_calls": "tool_calls",
    "paths": "parallel_paths",
    "iterations": "iterations",
    "retries": "retries",
    "cost_units": "total_cost_units",
}

_BUDGET_ALIASES = {
    "reasoning_tokens": "tokens",
    "end_to_end_latency_ms": "latency_ms",
    "parallel_paths": "paths",
    "step_retries": "retries",
    "total_cost_units": "cost_units",
    "max_reasoning_tokens": "tokens",
    "max_latency_ms": "latency_ms",
    "max_end_to_end_latency_ms": "latency_ms",
    "max_model_calls": "model_calls",
    "max_tool_calls": "tool_calls",
    "max_parallel_paths": "paths",
    "max_iterations": "iterations",
    "max_retries": "retries",
    "max_step_retries": "retries",
    "max_total_cost_units": "cost_units",
}

RUNTIME_SUPPORTED_STOP_TYPES = frozenset(
    {"validated_success", "all_critical_claims_resolved", "no_progress"}
)


def validate_runtime_contract_capabilities(
    contract: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Fail before execution when a normative contract exceeds runtime capability.

    / 当规范契约超出运行时能力时，在执行前失败。
    """

    if not isinstance(contract, Mapping):
        raise TypeError("contract must be a mapping / 契约必须是映射")
    stop_conditions = contract.get("stop_conditions")
    if not isinstance(stop_conditions, list):
        raise ValueError("contract stop_conditions are required / 契约必须声明停止条件")
    unsupported_stop_types = sorted(
        {
            item.get("type")
            for item in stop_conditions
            if isinstance(item, Mapping)
            and item.get("type") not in RUNTIME_SUPPORTED_STOP_TYPES
        }
    )
    if unsupported_stop_types:
        raise ValueError(
            "normative stop condition is not executable by this runtime; refusing to ignore it / "
            "规范停止条件尚不能由本运行时执行，拒绝静默忽略: "
            + ", ".join(str(item) for item in unsupported_stop_types)
        )
    no_progress_conditions = [
        dict(item)
        for item in stop_conditions
        if isinstance(item, Mapping) and item.get("type") == "no_progress"
    ]
    if len(no_progress_conditions) > 1:
        raise ValueError(
            "multiple no-progress conditions require an explicit composition rule / "
            "多个无进展条件必须提供显式组合规则"
        )
    budget = contract.get("budget")
    if isinstance(budget, Mapping) and budget.get("on_exhaustion") == "degrade":
        raise ValueError(
            "budget on_exhaustion=degrade requires a declared degradation plan / "
            "预算耗尽动作 degrade 必须声明降级方案"
        )
    return no_progress_conditions[0] if no_progress_conditions else None


def _budget_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for supplied_key, supplied_value in value.items():
        key = _BUDGET_ALIASES.get(supplied_key, supplied_key)
        if key not in _BUDGET_FIELDS:
            raise ValueError(f"unknown budget dimension / 未知预算维度: {supplied_key}")
        if key in result:
            raise ValueError(f"duplicate budget dimension / 重复预算维度: {key}")
        result[key] = supplied_value
    return result


def _validate_number(name: str, value: Any, *, allow_none: bool, positive: bool) -> None:
    if value is None and allow_none:
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric / 必须为数值")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite / 必须为有限数")
    if positive and value <= 0:
        raise ValueError(f"{name} must be positive / 必须大于 0")
    if not positive and value < 0:
        raise ValueError(f"{name} cannot be negative / 不得小于 0")
    if name != "cost_units" and not isinstance(value, int):
        raise TypeError(f"{name} must be an integer / 必须为整数")


@dataclass(frozen=True)
class BudgetLimits:
    """Hard limits; ``None`` means unconfigured, never unlimited / 硬上限；``None`` 表示未配置，绝非无限。"""

    tokens: int | None = 8_000
    latency_ms: int | None = 12_000
    model_calls: int | None = 4
    tool_calls: int | None = 8
    paths: int | None = 3
    iterations: int | None = 6
    retries: int | None = 2
    cost_units: float | None = None

    def __post_init__(self) -> None:
        for name in _BUDGET_FIELDS:
            _validate_number(
                name,
                getattr(self, name),
                allow_none=True,
                positive=True,
            )

    @classmethod
    def from_value(cls, value: BudgetLimits | Mapping[str, Any] | None) -> BudgetLimits:
        """Normalize limits and schema aliases / 标准化预算上限与协议别名。"""

        if value is None:
            return cls()
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            raise TypeError("budget limits must be a mapping / 预算上限必须是映射")
        return cls(**_budget_mapping(value))

    def as_dict(self) -> dict[str, int | float | None]:
        """Return a detached mapping / 返回独立映射。"""

        return {name: getattr(self, name) for name in _BUDGET_FIELDS}


@dataclass(frozen=True)
class BudgetUsage:
    """Non-negative resource delta / 非负资源增量。"""

    tokens: int = 0
    latency_ms: int = 0
    model_calls: int = 0
    tool_calls: int = 0
    paths: int = 0
    iterations: int = 0
    retries: int = 0
    cost_units: float = 0.0

    def __post_init__(self) -> None:
        for name in _BUDGET_FIELDS:
            _validate_number(
                name,
                getattr(self, name),
                allow_none=False,
                positive=False,
            )

    @classmethod
    def from_value(cls, value: BudgetUsage | Mapping[str, Any] | None) -> BudgetUsage:
        """Normalize a usage delta / 标准化资源增量。"""

        if value is None:
            return cls()
        if isinstance(value, cls):
            return value
        if not isinstance(value, Mapping):
            raise TypeError("budget usage must be a mapping / 预算用量必须是映射")
        return cls(**_budget_mapping(value))

    def as_dict(self) -> dict[str, int | float]:
        """Return a detached mapping / 返回独立映射。"""

        return {name: getattr(self, name) for name in _BUDGET_FIELDS}

    def plus(self, other: BudgetUsage) -> BudgetUsage:
        """Add usage vectors / 相加用量向量。"""

        return BudgetUsage(
            **{name: getattr(self, name) + getattr(other, name) for name in _BUDGET_FIELDS}
        )

    def minus(self, other: BudgetUsage) -> BudgetUsage:
        """Subtract a contained vector / 减去已包含的向量。"""

        values = {name: getattr(self, name) - getattr(other, name) for name in _BUDGET_FIELDS}
        return BudgetUsage(**values)

    def contains(self, other: BudgetUsage) -> bool:
        """Return whether every dimension contains ``other`` / 判断每一维是否均包含 ``other``。"""

        return all(getattr(self, name) >= getattr(other, name) for name in _BUDGET_FIELDS)


@dataclass(frozen=True)
class BudgetSnapshot:
    """Immutable ledger view / 不可变预算账本视图。"""

    limits: Mapping[str, int | float | None]
    used: Mapping[str, int | float]
    reserved: Mapping[str, int | float]
    available: Mapping[str, int | float | None]
    reservation_count: int


class BudgetLedger:
    """Thread-safe atomic budget ledger / 线程安全的原子预算账本。

    Reservations count against capacity immediately. A failed reserve or consume
    changes no dimension, which provides fail-closed multi-dimensional accounting.
    / 预留会立即占用容量；失败的预留或消费不会改变任何维度，从而实现多维原子拒绝。
    """

    def __init__(self, limits: BudgetLimits | Mapping[str, Any] | None = None) -> None:
        self._limits = BudgetLimits.from_value(limits)
        self._used = BudgetUsage()
        self._reservations: dict[str, BudgetUsage] = {}
        self._lock = threading.RLock()

    @property
    def limits(self) -> BudgetLimits:
        """Configured immutable limits / 已配置的不可变上限。"""

        return self._limits

    def _reserved_total(self) -> BudgetUsage:
        total = BudgetUsage()
        for usage in self._reservations.values():
            total = total.plus(usage)
        return total

    def _assert_fits(self, delta: BudgetUsage, *, include_reserved: bool = True) -> None:
        projected = self._used.plus(delta)
        if include_reserved:
            projected = projected.plus(self._reserved_total())
        exceeded: list[str] = []
        for name in _BUDGET_FIELDS:
            limit = getattr(self._limits, name)
            actual = getattr(projected, name)
            if limit is None and actual > 0:
                exceeded.append(f"{name}={actual}>unconfigured")
            elif limit is not None and actual > limit:
                exceeded.append(
                    f"{name}={actual}>{limit}"
                )
        if exceeded:
            raise BudgetExceededError(
                "budget would be exceeded / 预算将越界: " + ", ".join(exceeded)
            )

    def reserve(
        self,
        amounts: BudgetUsage | Mapping[str, Any],
        reservation_id: str | None = None,
    ) -> str:
        """Atomically reserve all dimensions or none / 原子预留全部维度，否则全部不变。"""

        usage = BudgetUsage.from_value(amounts)
        identifier = reservation_id or f"reservation-{uuid.uuid4().hex}"
        if not identifier:
            raise ValueError("reservation_id is required / 预留标识不能为空")
        with self._lock:
            existing = self._reservations.get(identifier)
            if existing is not None:
                if existing == usage:
                    return identifier
                raise DuplicateEventConflictError(
                    f"reservation id reused with different amounts / 预留标识内容冲突: {identifier}"
                )
            self._assert_fits(usage)
            self._reservations[identifier] = usage
            return identifier

    def reserve_many(
        self,
        reservations: Mapping[str, BudgetUsage | Mapping[str, Any]],
    ) -> tuple[str, ...]:
        """Atomically reserve a named batch or change nothing / 原子预留具名批次，否则全部不变。"""

        if not isinstance(reservations, Mapping) or not reservations:
            raise ValueError(
                "reservations must be a non-empty mapping / 预留批次必须是非空映射"
            )
        normalized: list[tuple[str, BudgetUsage]] = []
        for identifier, amounts in reservations.items():
            if not isinstance(identifier, str) or not identifier:
                raise ValueError(
                    "reservation IDs must be non-empty strings / 预留标识必须为非空字符串"
                )
            normalized.append((identifier, BudgetUsage.from_value(amounts)))

        with self._lock:
            new_total = BudgetUsage()
            pending: list[tuple[str, BudgetUsage]] = []
            for identifier, usage in normalized:
                existing = self._reservations.get(identifier)
                if existing is not None:
                    if existing != usage:
                        raise DuplicateEventConflictError(
                            "reservation id reused with different amounts / "
                            f"预留标识内容冲突: {identifier}"
                        )
                    continue
                pending.append((identifier, usage))
                new_total = new_total.plus(usage)
            self._assert_fits(new_total)
            for identifier, usage in pending:
                self._reservations[identifier] = usage
            return tuple(identifier for identifier, _ in normalized)

    def consume(
        self,
        amounts: BudgetUsage | Mapping[str, Any] | None = None,
        *,
        reservation_id: str | None = None,
    ) -> BudgetSnapshot:
        """Atomically consume direct or reserved capacity / 原子消费直接或已预留容量。

        Supplying a reservation commits the requested actual usage and releases
        the unused remainder. Actual usage may not exceed any reserved dimension.
        / 指定预留时提交实际用量并释放余量；实际用量任一维都不得超过预留。
        """

        with self._lock:
            if reservation_id is not None:
                if reservation_id not in self._reservations:
                    raise KeyError(f"unknown reservation / 未知预留: {reservation_id}")
                reserved = self._reservations[reservation_id]
                usage = reserved if amounts is None else BudgetUsage.from_value(amounts)
                if not reserved.contains(usage):
                    raise BudgetExceededError(
                        f"actual usage exceeds reservation / 实际用量超过预留: {reservation_id}"
                    )
                # The committed reservation is excluded from the remaining-reservation check.
                del self._reservations[reservation_id]
                try:
                    self._assert_fits(usage)
                except Exception:
                    self._reservations[reservation_id] = reserved
                    raise
                self._used = self._used.plus(usage)
                return self.snapshot()

            if amounts is None:
                raise ValueError("amounts are required / 必须提供消费用量")
            usage = BudgetUsage.from_value(amounts)
            self._assert_fits(usage)
            self._used = self._used.plus(usage)
            return self.snapshot()

    def release(self, reservation_id: str) -> BudgetSnapshot:
        """Release an unconsumed reservation / 释放尚未消费的预留。"""

        with self._lock:
            if reservation_id not in self._reservations:
                raise KeyError(f"unknown reservation / 未知预留: {reservation_id}")
            del self._reservations[reservation_id]
            return self.snapshot()

    def reservation(self, reservation_id: str) -> BudgetUsage:
        """Return one immutable reservation amount / 返回一项不可变预留用量。"""

        with self._lock:
            try:
                return self._reservations[reservation_id]
            except KeyError as exc:
                raise KeyError(f"unknown reservation / 未知预留: {reservation_id}") from exc

    def _checkpoint(self) -> tuple[BudgetUsage, dict[str, BudgetUsage]]:
        """Capture rollback state for the coordinator transaction / 捕获协调器事务的回滚状态。"""

        with self._lock:
            return self._used, dict(self._reservations)

    def _restore(self, checkpoint: tuple[BudgetUsage, dict[str, BudgetUsage]]) -> None:
        """Restore a coordinator checkpoint after event persistence fails / 事件持久化失败后恢复协调器检查点。"""

        used, reservations = checkpoint
        with self._lock:
            self._used = used
            self._reservations = dict(reservations)

    def snapshot(self) -> BudgetSnapshot:
        """Return a detached consistent snapshot / 返回独立且一致的快照。"""

        with self._lock:
            reserved = self._reserved_total()
            available: dict[str, int | float | None] = {}
            for name in _BUDGET_FIELDS:
                limit = getattr(self._limits, name)
                available[name] = (
                    None
                    if limit is None
                    else limit - getattr(self._used, name) - getattr(reserved, name)
                )
            return BudgetSnapshot(
                limits=MappingProxyType(self._limits.as_dict()),
                used=MappingProxyType(self._used.as_dict()),
                reserved=MappingProxyType(reserved.as_dict()),
                available=MappingProxyType(available),
                reservation_count=len(self._reservations),
            )


_EVENT_PAYLOAD_KINDS = {
    "run_created": "lifecycle",
    "task_received": "lifecycle",
    "task_normalized": "lifecycle",
    "contract_established": "lifecycle",
    "run_ended": "lifecycle",
    "state_transitioned": "state_transition",
    "route_selected": "route",
    "mode_switched": "mode",
    "step_started": "step",
    "step_closed": "step",
    "evidence_recorded": "evidence",
    "action_dispatched": "tool",
    "action_observed": "tool",
    "candidate_created": "candidate",
    "candidate_compared": "candidate",
    "parallel_path_updated": "parallel_path",
    "iteration_closed": "iteration",
    "no_progress_limit_reached": "iteration",
    "validation_started": "validation",
    "validation_completed": "validation",
    "budget_reserved": "budget",
    "budget_consumed": "budget",
    "budget_released": "budget",
    "budget_exhausted": "budget",
    "human_work_updated": "human_work",
    "outcome_recorded": "outcome",
    "governance_decided": "governance",
    "feedback_updated": "feedback",
    "probe_health_reported": "probe_health",
}

_ALLOWED_PAYLOAD_KINDS = frozenset(_EVENT_PAYLOAD_KINDS.values())
_MODE_EVENT_CONTEXT = {
    "direct": ("direct", None),
    "chain": ("deliberative", "chain"),
    "parallel": ("deliberative", "parallel"),
    "iterative": ("deliberative", "loop"),
}

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_SEMANTIC_VERSION_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$"
)


@lru_cache(maxsize=1)
def _direct_release_rule_schema_validator() -> Draft202012Validator:
    """Load the normative DirectReleaseRule definition once / 仅加载一次规范直接放行定义。"""

    schema_path = (
        Path(__file__).resolve().parents[1]
        / "schemas"
        / "reasoning-contract.schema.json"
    )
    contract_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    definition_schema = {
        "$schema": contract_schema.get(
            "$schema", "https://json-schema.org/draft/2020-12/schema"
        ),
        "$ref": "#/$defs/DirectReleaseRule",
        "$defs": contract_schema["$defs"],
    }
    Draft202012Validator.check_schema(definition_schema)
    return Draft202012Validator(
        definition_schema,
        format_checker=FormatChecker(),
    )


@lru_cache(maxsize=1)
def _binding_state_schema_validator() -> Draft202012Validator:
    """Load the normative audit-binding definition once / 仅加载一次规范审计绑定定义。"""

    schema_path = (
        Path(__file__).resolve().parents[1]
        / "schemas"
        / "reasoning-result.schema.json"
    )
    result_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    definition_schema = {
        "$schema": result_schema.get(
            "$schema", "https://json-schema.org/draft/2020-12/schema"
        ),
        "$ref": "#/$defs/BindingState",
        "$defs": result_schema["$defs"],
    }
    Draft202012Validator.check_schema(definition_schema)
    return Draft202012Validator(
        definition_schema,
        format_checker=FormatChecker(),
    )


def _validate_binding_state(name: str, value: Any) -> None:
    errors = sorted(
        _binding_state_schema_validator().iter_errors(value),
        key=lambda error: "/".join(str(part) for part in error.absolute_path),
    )
    if errors:
        detail = " | ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in errors[:5]
        )
        raise ValueError(
            f"{name} violates the normative binding state / {name} 不符合规范绑定状态: {detail}"
        )


def _normalize_versioned_bindings(
    name: str,
    values: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, str], ...]:
    """Normalize unique versioned bindings with the normative Schema / 依据规范 Schema 标准化唯一版本绑定。"""

    if isinstance(values, (str, bytes, Mapping)):
        raise TypeError(f"{name} must be an iterable of bindings / {name} 必须是绑定迭代器")
    normalized: list[dict[str, str]] = []
    identities: set[tuple[str, str, str]] = set()
    for index, value in enumerate(values):
        if not isinstance(value, Mapping):
            raise TypeError(
                f"{name}[{index}] must be a mapping / {name}[{index}] 必须是映射"
            )
        binding = json.loads(_canonical_json(dict(value)))
        _validate_binding_state(
            f"{name}[{index}]",
            {"state": "observed", "value": binding},
        )
        identity = (binding["id"], binding["version"], binding["hash"])
        if identity in identities:
            raise ValueError(
                f"{name} cannot contain duplicate bindings / {name} 不得包含重复绑定"
            )
        identities.add(identity)
        normalized.append(binding)
    return tuple(normalized)


def _validate_identifier(name: str, value: str | None, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value or len(value) > 160:
        raise ValueError(f"{name} must be a non-empty identifier / {name} 必须是非空标识")
    if _IDENTIFIER_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} contains invalid characters / {name} 包含非法字符: {value}")


def _validate_direct_release_rule(
    rule: Any,
    *,
    execution_mode: str,
    risk_level: RiskLevel,
) -> None:
    """Validate the narrow validator exemption boundary / 验证严格限定的验证器豁免边界。"""

    if not isinstance(rule, Mapping):
        raise TypeError("direct_release_rule must be an object / 直接放行规则必须是对象")
    schema_errors = sorted(
        _direct_release_rule_schema_validator().iter_errors(dict(rule)),
        key=lambda error: "/".join(str(part) for part in error.absolute_path),
    )
    if schema_errors:
        detail = " | ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
            for error in schema_errors[:5]
        )
        raise ValueError(
            "direct_release_rule violates reasoning-contract.schema.json / "
            f"直接放行规则不符合推理契约: {detail}"
        )
    if execution_mode != "direct" or risk_level is not RiskLevel.LOW:
        raise ValueError(
            "direct release is limited to low-risk direct execution / 直接放行仅限低风险直接执行"
        )
    required = {
        "rule_id",
        "rule_version",
        "allowed_risk_levels",
        "predicate",
        "criteria_version",
        "required_evidence",
        "validator_exemption_basis",
    }
    if set(rule) != required:
        raise ValueError(
            "direct release rule fields must match the normative contract / 直接放行规则字段必须符合规范契约"
        )
    _validate_identifier("direct_release_rule.rule_id", rule["rule_id"])
    for name in ("rule_version", "criteria_version"):
        value = rule[name]
        if not isinstance(value, str) or _SEMANTIC_VERSION_PATTERN.fullmatch(value) is None:
            raise ValueError(f"direct_release_rule.{name} must be semantic version text")
    if rule["allowed_risk_levels"] != ["low"]:
        raise ValueError("direct release allowed_risk_levels must be ['low']")
    predicate = rule["predicate"]
    if (
        not isinstance(predicate, Mapping)
        or not isinstance(predicate.get("field_path"), str)
        or not predicate["field_path"].startswith("/")
        or predicate.get("operator")
        not in {"eq", "ne", "lt", "lte", "gt", "gte", "in", "not_in", "exists", "matches"}
    ):
        raise ValueError("direct release predicate is invalid / 直接放行谓词非法")
    if predicate.get("operator") != "exists" and "expected" not in predicate:
        raise ValueError("direct release predicate requires expected / 直接放行谓词缺少期望值")
    if predicate.get("operator") == "matches":
        expected_pattern = predicate.get("expected")
        if not isinstance(expected_pattern, str):
            raise ValueError(
                "direct release matches predicate requires a text pattern / "
                "直接放行 matches 谓词要求文本正则"
            )
        try:
            re.compile(expected_pattern)
        except re.error as exc:
            raise ValueError(
                "direct release matches predicate has an invalid pattern / "
                "直接放行 matches 谓词包含非法正则"
            ) from exc
    if not isinstance(rule["required_evidence"], Mapping):
        raise TypeError("direct release required_evidence must be an object")
    exemption = rule["validator_exemption_basis"]
    if (
        not isinstance(exemption, Mapping)
        or exemption.get("basis")
        not in {"deterministic_rule", "low_risk_reversible", "prevalidated_input"}
        or not isinstance(exemption.get("policy_binding"), Mapping)
    ):
        raise ValueError("direct release validator exemption is invalid / 直接放行验证器豁免非法")


def _resolve_json_pointer(value: Any, pointer: str) -> tuple[bool, Any]:
    current = value
    if pointer == "":
        return True, current
    if not pointer.startswith("/"):
        return False, None
    for raw_part in pointer[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping) and part in current:
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return False, None
    return True, current


def _predicate_matches(value: Any, predicate: Mapping[str, Any]) -> bool:
    exists, actual = _resolve_json_pointer(value, predicate["field_path"])
    operator = predicate["operator"]
    if operator == "exists":
        return exists
    if not exists:
        return False
    expected = predicate["expected"]
    if operator == "eq":
        return actual == expected
    if operator == "ne":
        return actual != expected
    if operator == "in":
        return isinstance(expected, (list, tuple, set)) and actual in expected
    if operator == "not_in":
        return isinstance(expected, (list, tuple, set)) and actual not in expected
    if operator == "matches":
        return isinstance(actual, str) and isinstance(expected, str) and re.search(expected, actual) is not None
    try:
        return {
            "lt": actual < expected,
            "lte": actual <= expected,
            "gt": actual > expected,
            "gte": actual >= expected,
        }[operator]
    except (KeyError, TypeError):
        return False


def _iso_utc(value: float | str | None = None) -> tuple[str, float]:
    if value is None:
        moment = datetime.now(timezone.utc)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        moment = datetime.fromtimestamp(value, tz=timezone.utc)
    elif isinstance(value, str):
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        moment = datetime.fromisoformat(normalized)
        if moment.tzinfo is None:
            raise ValueError("timestamp must include a timezone / 时间戳必须包含时区")
        moment = moment.astimezone(timezone.utc)
    else:
        raise TypeError("timestamp must be epoch seconds or ISO text / 时间戳必须为纪元秒或 ISO 文本")
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z"), moment.timestamp()


def _direct_evidence_failures(
    evidence: Any,
    requirement: Mapping[str, Any],
    *,
    evaluated_at_epoch: float,
    max_future_skew_seconds: float,
) -> list[str]:
    """Fail closed on incomplete direct-release evidence metadata / 直接放行证据元数据不完整时默认关闭。"""

    failures: list[str] = []
    if not isinstance(evidence, (list, tuple)) or not evidence:
        return ["direct release evidence is missing / 直接放行证据缺失"]
    records: list[Mapping[str, Any]] = []
    for item in evidence:
        if not isinstance(item, Mapping):
            failures.append(
                "direct release evidence must be structured / 直接放行证据必须结构化"
            )
        else:
            records.append(item)
    if failures:
        return failures

    unknown_policy = requirement.get("unknown_source_policy", "reject")
    eligible: list[Mapping[str, Any]] = []
    source_keys: set[str] = set()
    for record in records:
        source_key: str | None = None
        source = record.get("source")
        if isinstance(source, Mapping) and isinstance(source.get("source_ref"), str):
            source_key = source["source_ref"]
        elif isinstance(record.get("source_id"), str):
            source_key = record["source_id"]
        else:
            source_binding = record.get("source_binding")
            if isinstance(source_binding, Mapping) and isinstance(
                source_binding.get("id"), str
            ):
                source_key = source_binding["id"]
        if source_key is None:
            if unknown_policy == "exclude":
                continue
            failures.append(
                "direct release evidence source is unknown / 直接放行证据来源未知"
            )
            continue
        source_keys.add(source_key)
        eligible.append(record)

    minimum_sources = int(requirement.get("min_independent_sources", 0))
    if len(source_keys) < minimum_sources:
        failures.append(
            "direct release evidence has insufficient independent sources / "
            "直接放行证据的独立来源不足"
        )
    required_types = set(requirement.get("required_evidence_types", ()))
    observed_types = {
        record.get("evidence_type")
        for record in eligible
        if isinstance(record.get("evidence_type"), str)
    }
    if not required_types.issubset(observed_types):
        failures.append(
            "direct release evidence types are incomplete / 直接放行证据类型不完整"
        )

    max_age = requirement.get("max_source_age_seconds")
    min_integrity = requirement.get("min_integrity_score")
    min_coverage = requirement.get("min_claim_coverage_ratio")
    max_unresolved = requirement.get("max_unresolved_critical_claims")
    for record in eligible:
        captured_at = record.get("captured_at", record.get("observed_at"))
        try:
            captured_epoch = _iso_utc(captured_at)[1]
        except (TypeError, ValueError, OverflowError, OSError):
            failures.append(
                "direct release evidence capture time is missing / "
                "直接放行证据缺少采集时间"
            )
        else:
            if captured_epoch > evaluated_at_epoch + max_future_skew_seconds:
                failures.append(
                    "direct release evidence capture time is in the future / "
                    "直接放行证据采集时间超出允许的未来偏差"
                )
            elif max_age is not None and evaluated_at_epoch - captured_epoch > float(max_age):
                failures.append(
                    "direct release evidence is stale / 直接放行证据已过期"
                )
        integrity = record.get("integrity_score")
        if min_integrity is not None and (
            isinstance(integrity, bool)
            or not isinstance(integrity, (int, float))
            or integrity < float(min_integrity)
        ):
            failures.append(
                "direct release evidence integrity is insufficient / "
                "直接放行证据完整性不足"
            )
        coverage = record.get("claim_coverage_ratio")
        if min_coverage is not None and (
            isinstance(coverage, bool)
            or not isinstance(coverage, (int, float))
            or coverage < float(min_coverage)
        ):
            failures.append(
                "direct release evidence claim coverage is insufficient / "
                "直接放行证据声明覆盖不足"
            )
        unresolved = record.get("unresolved_critical_claims")
        if max_unresolved is not None and (
            isinstance(unresolved, bool)
            or not isinstance(unresolved, int)
            or unresolved > int(max_unresolved)
        ):
            failures.append(
                "direct release has unresolved critical claims / 直接放行仍有未解决关键声明"
            )
    return list(dict.fromkeys(failures))


def _resource_value(value: int | float | None, *, known: bool) -> dict[str, Any]:
    if not known:
        return {"value_state": "missing", "value": None}
    if value == 0:
        return {"value_state": "observed_zero", "value": 0}
    return {"value_state": "observed", "value": value}


def _default_event_resources() -> dict[str, dict[str, Any]]:
    return {
        "model_calls": _resource_value(0, known=True),
        "tool_calls": _resource_value(0, known=True),
        "reasoning_tokens": _resource_value(None, known=False),
        "input_tokens": _resource_value(None, known=False),
        "output_tokens": _resource_value(None, known=False),
        "cost_units": _resource_value(None, known=False),
        "latency_ms": _resource_value(None, known=False),
    }


@dataclass(frozen=True)
class ReasoningEvent:
    """Immutable, schema-ready append-only event / 不可变且符合 Schema 的仅追加事件。"""

    schema_version: str
    sequence: int
    event_id: str
    idempotency_key: str
    run_id: str
    event_type: str
    state: WorkflowState
    timestamp: float
    payload_json: str = field(repr=False)
    envelope_json: str = field(repr=False)
    content_json: str = field(repr=False)

    @property
    def payload(self) -> dict[str, Any]:
        """Return a fresh payload copy / 返回新的负载副本。"""

        return json.loads(self.payload_json)

    def as_dict(self) -> dict[str, Any]:
        """Return a fresh schema-compatible event envelope / 返回新的 Schema 兼容事件信封。"""

        return json.loads(self.envelope_json)


class EventStore:
    """In-memory append-only event store with strict deduplication / 严格去重的内存仅追加事件库。"""

    SCHEMA_VERSION = "1.0.0"

    def __init__(self, *, validate_schema: bool = True) -> None:
        self._events: list[ReasoningEvent] = []
        self._by_run: dict[str, list[ReasoningEvent]] = {}
        self._by_event_id: dict[str, ReasoningEvent] = {}
        self._by_idempotency: dict[tuple[str, str], ReasoningEvent] = {}
        self._terminal_results: dict[str, str] = {}
        self._terminal_result_ids: dict[str, str] = {}
        self._lock = threading.RLock()
        self._schema_validator: Draft202012Validator | None = None
        if validate_schema:
            schema_path = Path(__file__).resolve().parents[1] / "schemas" / "reasoning-event.schema.json"
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            self._schema_validator = Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            )

    @staticmethod
    def _same_content(
        existing: ReasoningEvent,
        *,
        content_json: str,
    ) -> bool:
        return existing.content_json == content_json

    def append(
        self,
        *,
        run_id: str,
        event_type: str,
        state: WorkflowState | str,
        payload: Mapping[str, Any] | None = None,
        event_id: str | None = None,
        idempotency_key: str | None = None,
        timestamp: float | str | None = None,
        task_id: str | None = None,
        workflow_id: str | None = None,
        step_id: str | None = None,
        attempt_id: str | None = None,
        causation_id: str | None = None,
        parent_event_id: str | None = None,
        candidate_path_id: str | None = None,
        tool_call_id: str | None = None,
        human_work_id: str | None = None,
        contract_binding: Mapping[str, Any] | None = None,
        scene_id: str = "default",
        risk_level: RiskLevel | str = RiskLevel.LOW,
        reasoning_depth: str = "direct",
        execution_mode: str = "direct",
        primary_topology: str | None = None,
        supporting_topologies: Iterable[str] = (),
        snapshot_versions: Mapping[str, int] | None = None,
        resources: Mapping[str, Any] | None = None,
        field_provenance: Mapping[str, Any] | None = None,
        privacy_class: str = "internal",
        redaction_state: str = "not_required",
        previous_state: WorkflowState | str | None = None,
        next_state: WorkflowState | str | None = None,
        transition_id: str | None = None,
        stop_reason: str | None = None,
        escalation_reason: str | None = None,
        payload_kind: str | None = None,
    ) -> ReasoningEvent:
        """Append a unified-schema event once; exact duplicates return the original / 仅追加一次统一事件；完全重复时返回原事件。"""

        if not run_id or not event_type:
            raise ValueError("run_id and event_type are required / 运行与事件类型不能为空")
        workflow_state = WorkflowState(state)
        data = dict(payload or {})
        payload_json = _canonical_json(data)
        identifier = event_id or f"event-{uuid.uuid4().hex}"
        dedup_key = idempotency_key or identifier
        if not identifier or not dedup_key:
            raise ValueError("event identities are required / 事件标识不能为空")
        if len(dedup_key) > 256:
            raise ValueError("idempotency_key is too long / 幂等键过长")
        expected_kind = _EVENT_PAYLOAD_KINDS.get(event_type)
        if expected_kind is None:
            raise ValueError(f"unknown event_type / 未知事件类型: {event_type}")
        kind = payload_kind or expected_kind
        if kind != expected_kind:
            raise ValueError(
                f"payload kind conflicts with event type / 载荷类别与事件类型冲突: {event_type} -> {kind}"
            )
        if kind not in _ALLOWED_PAYLOAD_KINDS:
            raise ValueError(f"unknown payload kind / 未知载荷类别: {kind}")
        expected_mode_context = _MODE_EVENT_CONTEXT.get(execution_mode)
        if expected_mode_context is None:
            raise ValueError(f"unknown execution mode / 未知执行模式: {execution_mode}")
        if (reasoning_depth, primary_topology) != expected_mode_context:
            raise ValueError(
                "reasoning depth/topology conflicts with execution mode / 推理深度或拓扑与执行模式冲突"
            )
        topology_values = tuple(supporting_topologies)
        if len(set(topology_values)) != len(topology_values) or any(
            topology not in {"orchestration", "hierarchy"}
            for topology in topology_values
        ):
            raise ValueError("invalid supporting topology / 支撑拓扑非法")
        if privacy_class not in {"public", "internal", "sensitive", "restricted"}:
            raise ValueError("invalid privacy_class / 隐私分类非法")
        if redaction_state not in {"untreated", "redacted", "not_required"}:
            raise ValueError("invalid redaction_state / 脱敏状态非法")
        resolved_task_id = task_id or f"task-{run_id}"
        resolved_workflow_id = workflow_id or f"workflow-{run_id}"
        resolved_attempt_id = attempt_id or f"attempt-{run_id}"
        for identity_name, identity_value, nullable in (
            ("event_id", identifier, False),
            ("task_id", resolved_task_id, False),
            ("workflow_id", resolved_workflow_id, False),
            ("run_id", run_id, False),
            ("step_id", step_id, True),
            ("attempt_id", resolved_attempt_id, False),
            ("causation_id", causation_id, True),
            ("parent_event_id", parent_event_id, True),
            ("candidate_path_id", candidate_path_id, True),
            ("tool_call_id", tool_call_id, True),
            ("human_work_id", human_work_id, True),
            ("scene_id", scene_id, False),
            ("transition_id", transition_id, True),
        ):
            _validate_identifier(identity_name, identity_value, nullable=nullable)
        occurred_at, epoch = _iso_utc(timestamp)
        context = {
            "event_type": event_type,
            "workflow_state": workflow_state.value,
            "task_id": resolved_task_id,
            "workflow_id": resolved_workflow_id,
            "run_id": run_id,
            "step_id": step_id,
            "attempt_id": resolved_attempt_id,
            "causation_id": causation_id,
            "parent_event_id": parent_event_id,
            "candidate_path_id": candidate_path_id,
            "tool_call_id": tool_call_id,
            "human_work_id": human_work_id,
            "scene_id": scene_id,
            "risk_level": RiskLevel(risk_level).value,
            "reasoning_depth": reasoning_depth,
            "execution_mode": execution_mode,
            "primary_topology": primary_topology,
            "supporting_topologies": list(topology_values),
            "snapshot_versions": dict(
                snapshot_versions
                or {"goal": 1, "constraints": 1, "verified_facts": 1}
            ),
            "payload": {"kind": kind, "data": data},
            "resources": dict(resources or _default_event_resources()),
            "field_provenance": dict(
                field_provenance
                or {
                    "payload.data": {
                        "value_state": "observed",
                        "source_type": "system_report",
                        "source_id": "reasoning-runtime",
                        "source_version": self.SCHEMA_VERSION,
                        "valid_at": occurred_at,
                        "captured_at": occurred_at,
                        "method": "deterministic_runtime_event",
                        "confidence": 1.0,
                    }
                }
            ),
            "privacy_class": privacy_class,
            "redaction_state": redaction_state,
            "previous_state": None if previous_state is None else WorkflowState(previous_state).value,
            "next_state": None if next_state is None else WorkflowState(next_state).value,
            "transition_id": transition_id,
            "stop_reason": stop_reason,
            "escalation_reason": escalation_reason,
        }
        if contract_binding is not None:
            context["contract_binding"] = json.loads(
                _canonical_json(dict(contract_binding))
            )
        # Deduplication compares caller-visible logical content. Generated clock
        # values inside default provenance must not make an exact retry conflict.
        # / 去重比较调用方可见的逻辑内容；默认来源中的生成时钟不得让完全重试产生冲突。
        dedup_context = dict(context)
        dedup_context["occurred_at_input"] = (
            occurred_at if timestamp is not None else "generated"
        )
        if field_provenance is None:
            dedup_context["field_provenance"] = {"default_provenance": True}
        content_json = _canonical_json(dedup_context)

        with self._lock:
            candidates: list[ReasoningEvent] = []
            by_id = self._by_event_id.get(identifier)
            if by_id is not None:
                if by_id.idempotency_key != dedup_key:
                    raise DuplicateEventConflictError(
                        f"event_id reused with a different idempotency key / 事件标识对应不同幂等键: {identifier}"
                    )
                candidates.append(by_id)
            by_key = self._by_idempotency.get((run_id, dedup_key))
            if by_key is not None and by_key not in candidates:
                candidates.append(by_key)
            if candidates:
                if len(candidates) > 1 and candidates[0] is not candidates[1]:
                    raise DuplicateEventConflictError(
                        "event_id and idempotency_key identify different events / 事件标识与幂等键指向不同事件"
                    )
                existing = candidates[0]
                if not self._same_content(
                    existing,
                    content_json=content_json,
                ):
                    raise DuplicateEventConflictError(
                        f"deduplication identity reused with different content / 去重标识内容冲突: {dedup_key}"
                    )
                return existing

            prior_events = self._by_run.get(run_id, ())
            if prior_events and prior_events[-1].state in _TERMINAL_STATES:
                prior_event = prior_events[-1]
                is_immediate_terminal_receipt = (
                    event_type == "run_ended"
                    and prior_event.event_type == "state_transitioned"
                    and workflow_state is prior_event.state
                    and parent_event_id == prior_event.event_id
                )
                if not is_immediate_terminal_receipt:
                    raise ReasoningRuntimeError(
                        "terminal event stream is sealed / 终态事件流已封存"
                    )

            sequence = len(self._by_run.get(run_id, ())) + 1
            envelope = {
                "schema_version": self.SCHEMA_VERSION,
                "event_version": self.SCHEMA_VERSION,
                "event_id": identifier,
                "event_type": event_type,
                "event_processing_status": "accepted",
                "sequence": sequence,
                "idempotency_key": dedup_key,
                "occurred_at": occurred_at,
                "emitted_at": occurred_at,
                "received_at": occurred_at,
                **context,
            }
            if self._schema_validator is not None:
                errors = sorted(
                    self._schema_validator.iter_errors(envelope),
                    key=lambda error: list(error.absolute_path),
                )
                if errors:
                    detail = " | ".join(
                        f"{list(error.absolute_path)}: {error.message}"
                        for error in errors[:5]
                    )
                    raise EventSchemaViolationError(
                        f"event violates reasoning-event.schema.json / 事件不符合推理事件契约: {detail}"
                    )
            envelope_json = _canonical_json(envelope)
            event = ReasoningEvent(
                schema_version=self.SCHEMA_VERSION,
                sequence=sequence,
                event_id=identifier,
                idempotency_key=dedup_key,
                run_id=run_id,
                event_type=event_type,
                state=workflow_state,
                timestamp=epoch,
                payload_json=payload_json,
                envelope_json=envelope_json,
                content_json=content_json,
            )
            self._events.append(event)
            self._by_run.setdefault(run_id, []).append(event)
            self._by_event_id[identifier] = event
            self._by_idempotency[(run_id, dedup_key)] = event
            return event

    def _index_restored_event(self, event: ReasoningEvent) -> None:
        """Validate and index one authoritative persisted event / 校验并索引一条权威持久化事件。"""

        if event.event_id in self._by_event_id:
            raise EventStorePersistenceError(
                f"duplicate persisted event_id / 持久化事件标识重复: {event.event_id}"
            )
        key = (event.run_id, event.idempotency_key)
        if key in self._by_idempotency:
            raise EventStorePersistenceError(
                "duplicate persisted idempotency key / 持久化幂等键重复: "
                + event.idempotency_key
            )
        expected_sequence = len(self._by_run.get(event.run_id, ())) + 1
        if event.sequence != expected_sequence:
            raise EventStorePersistenceError(
                "persisted run sequence is not contiguous / 持久化运行序列不连续: "
                f"expected {expected_sequence}, got {event.sequence}"
            )
        prior_events = self._by_run.get(event.run_id, ())
        if prior_events and prior_events[-1].state in _TERMINAL_STATES:
            prior = prior_events[-1]
            envelope = event.as_dict()
            if not (
                event.event_type == "run_ended"
                and prior.event_type == "state_transitioned"
                and event.state is prior.state
                and envelope.get("parent_event_id") == prior.event_id
            ):
                raise EventStorePersistenceError(
                    "persisted terminal stream contains trailing events / "
                    "持久化终态事件流包含尾随事件"
                )
        self._events.append(event)
        self._by_run.setdefault(event.run_id, []).append(event)
        self._by_event_id[event.event_id] = event
        self._by_idempotency[key] = event

    def _remove_events(self, appended: Sequence[ReasoningEvent]) -> None:
        """Remove an uncommitted suffix from every index / 从所有索引移除未提交后缀。"""

        if not appended:
            return
        appended_ids = {id(event) for event in appended}
        self._events[:] = [
            event for event in self._events if id(event) not in appended_ids
        ]
        affected_runs = {event.run_id for event in appended}
        for affected_run in affected_runs:
            retained = [
                event
                for event in self._by_run.get(affected_run, ())
                if id(event) not in appended_ids
            ]
            if retained:
                self._by_run[affected_run] = retained
            else:
                self._by_run.pop(affected_run, None)
        for event in appended:
            if self._by_event_id.get(event.event_id) is event:
                self._by_event_id.pop(event.event_id, None)
            key = (event.run_id, event.idempotency_key)
            if self._by_idempotency.get(key) is event:
                self._by_idempotency.pop(key, None)

    @contextmanager
    def transaction(self, run_id: str) -> Iterator[None]:
        """Atomically append a run-local event group / 原子追加一组运行内事件。"""

        with self._lock:
            checkpoint = len(self._by_run.get(run_id, ()))
            try:
                yield
            except Exception:
                run_events = self._by_run.get(run_id, [])
                appended = list(run_events[checkpoint:])
                self._remove_events(appended)
                raise

    def events(self, run_id: str | None = None) -> tuple[ReasoningEvent, ...]:
        """Return events in append order / 按追加顺序返回事件。"""

        with self._lock:
            source = self._events if run_id is None else self._by_run.get(run_id, ())
            return tuple(source)

    def find_idempotency(self, run_id: str, key: str) -> ReasoningEvent | None:
        """Find an event by run-scoped idempotency key / 按运行域幂等键查找事件。"""

        with self._lock:
            return self._by_idempotency.get((run_id, key))

    def replay(
        self,
        run_id: str,
        reducer: Callable[[Any, ReasoningEvent], Any] | None = None,
        initial: Any = None,
    ) -> tuple[ReasoningEvent, ...] | Any:
        """Replay ordered events, optionally through a reducer / 重放有序事件，可选归约器。"""

        events = self.events(run_id)
        for expected, event in enumerate(events, start=1):
            if event.sequence != expected:
                raise ReasoningRuntimeError(
                    f"non-contiguous sequence / 事件序列不连续: expected {expected}, got {event.sequence}"
                )
        if reducer is None:
            return events
        state = initial
        for event in events:
            state = reducer(state, event)
        return state

    @staticmethod
    def _terminal_result_json(
        run_id: str,
        result: Mapping[str, Any],
    ) -> str:
        """Validate and canonicalize one immutable terminal result.

        / 校验并规范化一份不可变终态结果。
        """

        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id is required / 运行标识不能为空")
        if not isinstance(result, Mapping):
            raise TypeError("terminal result must be a mapping / 终态结果必须为映射")
        artifact = json.loads(_canonical_json(dict(result)))
        validate_reasoning_result(artifact)
        if artifact["run_id"] != run_id:
            raise EventStorePersistenceError(
                "terminal result run binding mismatch / 终态结果运行绑定不匹配"
            )
        return _canonical_json(artifact)

    def _assert_terminal_result_stream(self, run_id: str, result_json: str) -> None:
        events = self._by_run.get(run_id, ())
        if not events or events[-1].state not in _TERMINAL_STATES:
            raise EventStorePersistenceError(
                "terminal result requires a terminal event stream / "
                "终态结果要求事件流已进入终态"
            )
        result = json.loads(result_json)
        if result["terminal_state"] != events[-1].state.value:
            raise EventStorePersistenceError(
                "terminal result state differs from the event stream / "
                "终态结果状态与事件流不一致"
            )

    def _index_restored_terminal_result(
        self,
        run_id: str,
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        result_json = self._terminal_result_json(run_id, result)
        self._assert_terminal_result_stream(run_id, result_json)
        artifact = json.loads(result_json)
        result_id = artifact["result_id"]
        existing_run = self._terminal_result_ids.get(result_id)
        if existing_run is not None and existing_run != run_id:
            raise EventStorePersistenceError(
                "terminal result_id is bound to another run / "
                "终态结果标识已绑定到其他运行"
            )
        existing = self._terminal_results.get(run_id)
        if existing is not None and existing != result_json:
            raise EventStorePersistenceError(
                "multiple terminal results exist for one run / 单个运行存在多个终态结果"
            )
        self._terminal_results[run_id] = result_json
        self._terminal_result_ids[result_id] = run_id
        return artifact

    def _remove_terminal_result(self, run_id: str) -> None:
        result_json = self._terminal_results.pop(run_id, None)
        if result_json is None:
            return
        result_id = json.loads(result_json)["result_id"]
        if self._terminal_result_ids.get(result_id) == run_id:
            self._terminal_result_ids.pop(result_id, None)

    def save_terminal_result(
        self,
        run_id: str,
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Immutably save one result after its event stream reaches terminal.

        Exact retries return the stored result; divergent content fails closed.
        / 在事件流进入终态后不可变地保存结果。完全重试返回原结果，内容分歧则
        默认阻断。
        """

        result_json = self._terminal_result_json(run_id, result)
        with self._lock:
            existing = self._terminal_results.get(run_id)
            if existing is not None:
                if existing != result_json:
                    raise DuplicateEventConflictError(
                        "terminal run already has a different persisted result / "
                        "终态运行已有不同的持久化结果"
                    )
                return json.loads(existing)
            self._assert_terminal_result_stream(run_id, result_json)
            artifact = json.loads(result_json)
            result_id = artifact["result_id"]
            existing_run = self._terminal_result_ids.get(result_id)
            if existing_run is not None and existing_run != run_id:
                raise DuplicateEventConflictError(
                    "terminal result_id is already used by another run / "
                    "终态结果标识已被其他运行使用"
                )
            self._terminal_results[run_id] = result_json
            self._terminal_result_ids[result_id] = run_id
            return artifact

    def load_terminal_result(self, run_id: str) -> dict[str, Any] | None:
        """Load a detached immutable terminal result / 加载独立副本形式的不可变终态结果。"""

        with self._lock:
            result_json = self._terminal_results.get(run_id)
            return None if result_json is None else json.loads(result_json)


class JsonlEventStore(EventStore):
    """Crash-consistent JSONL reference store with atomic transactions.

    The file is a self-hashed snapshot of the logical append-only stream. A
    commit writes and fsyncs a sibling temporary file, then atomically replaces
    the prior snapshot. This is a reference adapter for modest local workloads;
    production databases should preserve the same commit and replay contract. /
    使用自哈希 JSONL 快照实现崩溃一致的参考事件库。提交时先写入并 fsync 同目录
    临时文件，再原子替换旧快照。它适合轻量本地负载；生产数据库应保持相同的提交与
    重放契约。
    """

    STORAGE_SCHEMA_VERSION = "1.0.0"

    def __init__(
        self,
        path: str | Path,
        *,
        validate_schema: bool = True,
    ) -> None:
        self._path = Path(path).resolve()
        self._results_path = self._path.with_name(self._path.name + ".results.json")
        self._transaction_depth = 0
        super().__init__(validate_schema=validate_schema)
        self._load_snapshot()
        self._load_terminal_results()

    @property
    def path(self) -> Path:
        """Return the resolved durable snapshot path / 返回已解析的持久化快照路径。"""

        return self._path

    @property
    def results_path(self) -> Path:
        """Return the terminal-result sidecar path / 返回终态结果伴随文件路径。"""

        return self._results_path

    @staticmethod
    def _record_hash(record: Mapping[str, Any]) -> str:
        encoded = _canonical_json(dict(record)).encode("utf-8")
        return f"sha256:{hashlib.sha256(encoded).hexdigest()}"

    def _storage_record(self, event: ReasoningEvent) -> dict[str, Any]:
        record: dict[str, Any] = {
            "storage_schema_version": self.STORAGE_SCHEMA_VERSION,
            "envelope": event.as_dict(),
            "content_json": event.content_json,
        }
        record["record_hash"] = self._record_hash(record)
        return record

    def _load_snapshot(self) -> None:
        if not self._path.exists():
            return
        try:
            lines = self._path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise EventStorePersistenceError(
                f"cannot read durable event snapshot / 无法读取持久化事件快照: {self._path}"
            ) from exc
        expected_keys = {
            "storage_schema_version",
            "envelope",
            "content_json",
            "record_hash",
        }
        for line_number, line in enumerate(lines, start=1):
            try:
                if not line:
                    raise ValueError("blank storage record")
                record = json.loads(line)
                if not isinstance(record, dict) or set(record) != expected_keys:
                    raise ValueError("storage record fields differ from the contract")
                declared_hash = record.pop("record_hash")
                if declared_hash != self._record_hash(record):
                    raise ValueError("storage record hash mismatch")
                if record["storage_schema_version"] != self.STORAGE_SCHEMA_VERSION:
                    raise ValueError("storage schema version mismatch")
                envelope = record["envelope"]
                content_json = record["content_json"]
                if not isinstance(envelope, dict) or not isinstance(content_json, str):
                    raise TypeError("storage envelope or content JSON is invalid")
                if _canonical_json(json.loads(content_json)) != content_json:
                    raise ValueError("content JSON is not canonical")
                if (
                    envelope.get("schema_version") != self.SCHEMA_VERSION
                    or envelope.get("event_version") != self.SCHEMA_VERSION
                ):
                    raise ValueError("event schema version mismatch")
                if self._schema_validator is not None:
                    errors = sorted(
                        self._schema_validator.iter_errors(envelope),
                        key=lambda error: list(error.absolute_path),
                    )
                    if errors:
                        raise ValueError(errors[0].message)
                occurred_at = envelope["occurred_at"]
                _, epoch = _iso_utc(occurred_at)
                payload_json = _canonical_json(envelope["payload"]["data"])
                event = ReasoningEvent(
                    schema_version=str(envelope["schema_version"]),
                    sequence=int(envelope["sequence"]),
                    event_id=str(envelope["event_id"]),
                    idempotency_key=str(envelope["idempotency_key"]),
                    run_id=str(envelope["run_id"]),
                    event_type=str(envelope["event_type"]),
                    state=WorkflowState(envelope["workflow_state"]),
                    timestamp=epoch,
                    payload_json=payload_json,
                    envelope_json=_canonical_json(envelope),
                    content_json=content_json,
                )
                self._index_restored_event(event)
            except EventStorePersistenceError:
                raise
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise EventStorePersistenceError(
                    "invalid durable event snapshot record / 持久化事件快照记录无效: "
                    f"line {line_number}: {exc}"
                ) from exc

    def _persist_snapshot(self) -> None:
        temporary = self._path.with_name(
            f".{self._path.name}.{uuid.uuid4().hex}.tmp"
        )
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with temporary.open("w", encoding="utf-8", newline="\n") as handle:
                for event in self._events:
                    handle.write(_canonical_json(self._storage_record(event)))
                    handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self._path)
        except (OSError, TypeError, ValueError) as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise EventStorePersistenceError(
                f"durable event commit failed / 持久化事件提交失败: {self._path}"
            ) from exc

    def _terminal_results_record(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "storage_schema_version": self.STORAGE_SCHEMA_VERSION,
            "results": {
                run_id: json.loads(result_json)
                for run_id, result_json in self._terminal_results.items()
            },
        }
        record["record_hash"] = self._record_hash(record)
        return record

    def _load_terminal_results(self) -> None:
        if not self._results_path.exists():
            return
        try:
            text = self._results_path.read_text(encoding="utf-8")
            record = json.loads(text)
            if _canonical_json(record) != text:
                raise ValueError("terminal result sidecar is not canonical")
            if not isinstance(record, dict) or set(record) != {
                "storage_schema_version",
                "results",
                "record_hash",
            }:
                raise ValueError("terminal result sidecar fields differ from the contract")
            declared_hash = record["record_hash"]
            body = {key: value for key, value in record.items() if key != "record_hash"}
            if declared_hash != self._record_hash(body):
                raise ValueError("terminal result sidecar hash mismatch")
            if record["storage_schema_version"] != self.STORAGE_SCHEMA_VERSION:
                raise ValueError("terminal result storage schema version mismatch")
            results = record["results"]
            if not isinstance(results, dict):
                raise TypeError("terminal result index is not an object")
            for run_id, result in results.items():
                self._index_restored_terminal_result(run_id, result)
        except EventStorePersistenceError:
            raise
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise EventStorePersistenceError(
                "invalid durable terminal result sidecar / "
                f"持久化终态结果伴随文件无效: {self._results_path}: {exc}"
            ) from exc

    def _persist_terminal_results(self) -> None:
        temporary = self._results_path.with_name(
            f".{self._results_path.name}.{uuid.uuid4().hex}.tmp"
        )
        try:
            self._results_path.parent.mkdir(parents=True, exist_ok=True)
            with temporary.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(_canonical_json(self._terminal_results_record()))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self._results_path)
        except (OSError, TypeError, ValueError) as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise EventStorePersistenceError(
                "durable terminal result commit failed / "
                f"持久化终态结果提交失败: {self._results_path}"
            ) from exc

    def save_terminal_result(
        self,
        run_id: str,
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Atomically persist the immutable terminal-result sidecar.

        / 原子持久化不可变终态结果伴随文件。
        """

        with self._lock:
            existed = run_id in self._terminal_results
            saved = super().save_terminal_result(run_id, result)
            if existed:
                return saved
            try:
                self._persist_terminal_results()
            except Exception:
                self._remove_terminal_result(run_id)
                raise
            return saved

    def append(self, **kwargs: Any) -> ReasoningEvent:
        """Append and durably commit unless inside a wider transaction / 追加事件；若不在外层事务中则持久提交。"""

        run_id = kwargs.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id is required / 运行标识不能为空")
        with self._lock:
            if self._transaction_depth:
                return super().append(**kwargs)
            with self.transaction(run_id):
                return super().append(**kwargs)

    @contextmanager
    def transaction(self, run_id: str) -> Iterator[None]:
        """Commit every event in the boundary as one durable snapshot / 把边界内全部事件作为一个持久快照提交。"""

        if not isinstance(run_id, str) or not run_id:
            raise ValueError("run_id is required / 运行标识不能为空")
        with self._lock:
            checkpoint = len(self._events)
            outermost = self._transaction_depth == 0
            self._transaction_depth += 1
            try:
                yield
                if outermost and len(self._events) != checkpoint:
                    self._persist_snapshot()
            except Exception:
                self._remove_events(list(self._events[checkpoint:]))
                raise
            finally:
                self._transaction_depth -= 1


@dataclass(frozen=True)
class ValidatorSpec:
    """Versioned validator contract / 带版本的验证器契约。"""

    validator_id: str
    version: str = "1.0.0"
    kind: str = "rule"
    required: bool = True
    pass_criteria: str = "explicit deterministic pass / 显式确定性通过"
    independent: bool = False
    timeout_ms: int = 30_000
    definition_hash: str | None = field(default=None, repr=False)
    criteria_hash: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.validator_id or not self.version or not self.kind or not self.pass_criteria:
            raise ValueError("validator fields cannot be empty / 验证器字段不能为空")
        _validate_identifier("validator_id", self.validator_id)
        if _SEMANTIC_VERSION_PATTERN.fullmatch(self.version) is None:
            raise ValueError(
                "validator version must use semantic versioning / 验证器版本必须使用语义版本"
            )
        if isinstance(self.timeout_ms, bool) or not isinstance(self.timeout_ms, int) or self.timeout_ms < 1:
            raise ValueError("validator timeout_ms must be positive / 验证器 timeout_ms 必须为正整数")
        if self.definition_hash is not None and not re.fullmatch(
            r"sha256:[0-9a-f]{64}", self.definition_hash
        ):
            raise ValueError(
                "validator definition_hash must be SHA-256 / 验证器 definition_hash 必须为 SHA-256"
            )
        if self.criteria_hash is not None and not re.fullmatch(
            r"sha256:[0-9a-f]{64}", self.criteria_hash
        ):
            raise ValueError(
                "validator criteria_hash must be SHA-256 / 验证器 criteria_hash 必须为 SHA-256"
            )

    def as_dict(self) -> dict[str, Any]:
        """Return contract content / 返回契约内容。"""

        return {
            "validator_id": self.validator_id,
            "version": self.version,
            "kind": self.kind,
            "required": self.required,
            "pass_criteria": self.pass_criteria,
            "independent": self.independent,
            "timeout_ms": self.timeout_ms,
        }


@dataclass(frozen=True)
class ValidationRecord:
    """Validator outcome bound to exact inputs / 绑定精确输入的验证结果。"""

    verification_id: str
    validator_id: str
    validator_version: str
    status: ValidationStatus
    candidate_hash: str
    contract_hash: str
    evidence_hash: str
    timestamp: float
    details_json: str = field(repr=False)

    @property
    def details(self) -> dict[str, Any]:
        """Return a fresh details copy / 返回新的详情副本。"""

        return json.loads(self.details_json)


@dataclass(frozen=True)
class StepStartRecord:
    """Externally visible start of a closable step / 可关闭步骤的外部可见开始记录。"""

    step_id: str
    claim: Any
    evidence_refs: tuple[str, ...]
    evidence_bindings: tuple[Mapping[str, str], ...]
    action: Any
    step_hash: str
    sequence_number: int
    timestamp: float


@dataclass(frozen=True)
class StepRecord:
    """Externally checkable closable step; never private reasoning / 外部可核验的闭环步骤，不含私密推理。"""

    step_id: str
    claim: Any
    evidence_refs: tuple[str, ...]
    evidence_bindings: tuple[Mapping[str, str], ...]
    budget_reservation_id: str | None
    action: Any
    observation: Any
    local_decision: Any
    resource_use: BudgetUsage
    progress: bool
    information_gain: float | None
    no_progress_streak: int
    timestamp: float


@dataclass(frozen=True)
class RunSnapshot:
    """Read-only public run view / 只读运行视图。"""

    task_id: str
    workflow_id: str
    run_id: str
    scene_id: str
    risk_level: RiskLevel
    state: WorkflowState
    execution_mode: str
    reasoning_depth: str
    primary_topology: str | None
    supporting_topologies: tuple[str, ...]
    mode_switch_count: int
    blocking_feedback_count: int
    contract_hash: str
    candidate_hash: str | None
    evidence_hash: str | None
    step_count: int
    open_step_count: int
    validation_count: int
    no_progress_streak: int
    terminal_reason: str | None
    release_gate_evaluated_at: str | None
    budget: BudgetSnapshot


@dataclass(frozen=True)
class ReplaySnapshot:
    """State reconstructed solely from the event stream / 仅由事件流重建的状态。"""

    run_id: str
    state: WorkflowState
    event_count: int
    last_sequence: int
    terminal_reason: str | None
    candidate_hash: str | None
    evidence_hash: str | None
    no_progress_streak: int
    validation_count: int
    open_step_count: int
    release_gate_evaluated_at: str | None


@dataclass
class _Run:
    task_id: str
    workflow_id: str
    run_id: str
    risk_level: RiskLevel
    state: WorkflowState
    contract: dict[str, Any]
    contract_hash: str
    validators: dict[str, ValidatorSpec]
    budget: BudgetLedger
    max_no_progress_steps: int | None
    escalate_on_limit: bool
    budget_on_exhaustion: str
    no_progress_min_information_gain: float | None
    no_progress_on_trigger: str | None
    attempt_id: str
    scene_id: str
    reasoning_depth: str
    execution_mode: str
    primary_topology: str | None
    supporting_topologies: tuple[str, ...]
    snapshot_versions: dict[str, int]
    normalized_input_binding: dict[str, str]
    contract_binding: dict[str, str]
    candidate: Any = None
    evidence: Any = None
    candidate_hash: str | None = None
    evidence_hash: str | None = None
    evidence_bindings: list[dict[str, str]] = field(default_factory=list)
    evidence_records: dict[tuple[str, str], dict[str, Any]] = field(
        default_factory=dict
    )
    validations: list[ValidationRecord] = field(default_factory=list)
    step_starts: dict[str, StepStartRecord] = field(default_factory=dict)
    steps: dict[str, StepRecord] = field(default_factory=dict)
    no_progress_streak: int = 0
    last_information_gain: float | None = None
    terminal_reason: str | None = None
    release_gate_evaluated_at: str | None = None
    release_claims: list[dict[str, Any]] | None = None
    sealed_result_json: str | None = None
    mode_switch_counts: dict[str, int] = field(default_factory=dict)
    mode_switch_records: list[dict[str, Any]] = field(default_factory=list)
    feedback_latest: dict[str, dict[str, Any]] = field(default_factory=dict)
    conditionally_blocked_bindings: set[tuple[str, str, str]] = field(
        default_factory=set
    )


class ReasoningEngine:
    """Reference coordinator for state, budget, validation and replay / 状态、预算、验证与重放参考协调器。"""

    def __init__(
        self,
        event_store: EventStore | None = None,
        *,
        clock: Callable[[], float] | None = None,
        feedback_authorizer: Callable[
            [Mapping[str, Any], Mapping[str, Any]], bool
        ]
        | None = None,
        tool_authorizer: Callable[
            [Mapping[str, Any], Mapping[str, Any]], bool
        ]
        | None = None,
        max_future_evidence_skew_seconds: float = 300.0,
    ) -> None:
        if clock is not None and not callable(clock):
            raise TypeError("clock must be callable / 时钟必须可调用")
        if feedback_authorizer is not None and not callable(feedback_authorizer):
            raise TypeError(
                "feedback_authorizer must be callable / 反馈授权器必须可调用"
            )
        if tool_authorizer is not None and not callable(tool_authorizer):
            raise TypeError(
                "tool_authorizer must be callable / 工具授权器必须可调用"
            )
        if (
            isinstance(max_future_evidence_skew_seconds, bool)
            or not isinstance(max_future_evidence_skew_seconds, (int, float))
            or not math.isfinite(float(max_future_evidence_skew_seconds))
            or max_future_evidence_skew_seconds < 0
        ):
            raise ValueError(
                "max_future_evidence_skew_seconds must be finite and non-negative / "
                "证据未来时间允许偏差必须是有限非负数"
            )
        self.events = event_store or EventStore()
        self._clock = clock or time.time
        self._feedback_authorizer = feedback_authorizer
        self._tool_authorizer = tool_authorizer
        self._max_future_evidence_skew_seconds = float(
            max_future_evidence_skew_seconds
        )
        self._runs: dict[str, _Run] = {}
        self._lock = threading.RLock()

    def _evaluation_time(
        self,
        value: float | str | None = None,
    ) -> tuple[str, float]:
        """Resolve an explicit or injected release-gate clock / 解析显式或注入的放行闸门时钟。"""

        raw_value: Any = self._clock() if value is None else value
        if isinstance(raw_value, bool):
            raise TypeError("evaluation time cannot be boolean / 评估时间不能是布尔值")
        if isinstance(raw_value, (int, float)) and not math.isfinite(float(raw_value)):
            raise ValueError("evaluation time must be finite / 评估时间必须是有限值")
        try:
            return _iso_utc(raw_value)
        except (OverflowError, OSError) as exc:
            raise ValueError("evaluation time is outside the supported range / 评估时间超出支持范围") from exc

    @staticmethod
    def _normalize_validators(validators: Iterable[ValidatorSpec]) -> dict[str, ValidatorSpec]:
        result: dict[str, ValidatorSpec] = {}
        for spec in validators:
            if not isinstance(spec, ValidatorSpec):
                raise TypeError("validators must be ValidatorSpec / 验证器必须为 ValidatorSpec")
            if spec.validator_id in result:
                raise ValueError(f"duplicate validator / 重复验证器: {spec.validator_id}")
            result[spec.validator_id] = spec
        return result

    @staticmethod
    def _mode_context(execution_mode: str) -> tuple[str, str | None, tuple[str, ...]]:
        mapping = {
            "direct": ("direct", None, ()),
            "chain": ("deliberative", "chain", ("orchestration",)),
            "parallel": ("deliberative", "parallel", ("orchestration",)),
            "iterative": ("deliberative", "loop", ("orchestration",)),
        }
        try:
            return mapping[execution_mode]
        except KeyError as exc:
            raise ValueError(f"unknown execution mode / 未知执行模式: {execution_mode}") from exc

    @staticmethod
    def _event_resources(usage: BudgetUsage | None = None) -> dict[str, dict[str, Any]]:
        if usage is None:
            return _default_event_resources()
        return {
            "model_calls": _resource_value(usage.model_calls, known=True),
            "tool_calls": _resource_value(usage.tool_calls, known=True),
            "reasoning_tokens": _resource_value(usage.tokens, known=True),
            "input_tokens": _resource_value(None, known=False),
            "output_tokens": _resource_value(None, known=False),
            "cost_units": _resource_value(usage.cost_units, known=True),
            "latency_ms": _resource_value(usage.latency_ms, known=True),
        }

    @staticmethod
    def _schema_budget_delta(usage: BudgetUsage) -> dict[str, int | float]:
        values = usage.as_dict()
        return {
            schema_name: values[runtime_name]
            for runtime_name, schema_name in _EVENT_BUDGET_NAMES.items()
        }

    @classmethod
    def _schema_step_resource_use(cls, usage: BudgetUsage) -> dict[str, dict[str, Any]]:
        return {
            name: _observed_number(value)
            for name, value in cls._schema_budget_delta(usage).items()
        }

    @classmethod
    def _budget_event_payload(
        cls,
        run: _Run,
        *,
        operation: str,
        delta: BudgetUsage,
        reservation_id: str | None,
    ) -> dict[str, Any]:
        snapshot = run.budget.snapshot()
        dimensions: dict[str, Any] = {}
        for runtime_name, schema_name in _EVENT_BUDGET_NAMES.items():
            dimensions[schema_name] = {
                "limit": _positive_limit(snapshot.limits[runtime_name]),
                "consumed": _observed_number(snapshot.used[runtime_name]),
                "remaining": _observed_number(snapshot.available[runtime_name]),
            }
        return {
            "operation": operation,
            "reservation_id": reservation_id,
            "delta": cls._schema_budget_delta(delta),
            "dimensions": dimensions,
        }

    @staticmethod
    def _step_summary(claim: Any) -> str:
        if isinstance(claim, str) and claim.strip():
            return claim.strip()[:500]
        return "externally checkable step / 外部可核验步骤"

    @staticmethod
    def _candidate_binding(candidate_hash: str) -> dict[str, str]:
        return _versioned_binding(_artifact_id("candidate", candidate_hash), candidate_hash)

    @staticmethod
    def _evidence_bindings(evidence_hash: str) -> list[dict[str, str]]:
        return [
            _versioned_binding(_artifact_id("evidence", evidence_hash), evidence_hash)
        ]

    @classmethod
    def _evidence_bindings_for(
        cls,
        evidence: Any,
        evidence_hash: str,
    ) -> list[dict[str, str]]:
        """Use record-level bindings when structured evidence is supplied.

        Arbitrary legacy evidence remains bound as one aggregate artifact.
        / 提供结构化证据记录时使用逐记录绑定；任意旧式证据仍绑定为一个聚合制品。
        """

        if isinstance(evidence, list) and evidence and all(
            isinstance(item, Mapping)
            and {"evidence_id", "evidence_version", "evidence_hash"} <= set(item)
            for item in evidence
        ):
            return [
                _versioned_binding(
                    str(item["evidence_id"]),
                    str(item["evidence_hash"]),
                    str(item["evidence_version"]),
                )
                for item in evidence
            ]
        return cls._evidence_bindings(evidence_hash)

    @staticmethod
    def _evidence_record_bindings_for(
        evidence: Any,
    ) -> list[dict[str, str]]:
        """Bind complete structured evidence records by record hash / 使用记录哈希绑定完整结构化证据。"""

        if not isinstance(evidence, list) or not evidence:
            return []
        if not all(
            isinstance(item, Mapping)
            and {"evidence_id", "evidence_version", "record_hash"} <= set(item)
            for item in evidence
        ):
            return []
        return [
            _versioned_binding(
                str(item["evidence_id"]),
                str(item["record_hash"]),
                str(item["evidence_version"]),
            )
            for item in evidence
        ]

    @staticmethod
    def _validator_binding(spec: ValidatorSpec) -> dict[str, str]:
        validator_hash = spec.definition_hash or content_fingerprint(spec.as_dict())
        return _versioned_binding(spec.validator_id, validator_hash, spec.version)

    @staticmethod
    def _criteria_binding(spec: ValidatorSpec) -> dict[str, str]:
        criteria_hash = spec.criteria_hash or content_fingerprint(spec.pass_criteria)
        return _versioned_binding(
            f"{spec.validator_id}-criteria",
            criteria_hash,
            spec.version,
        )

    @staticmethod
    def _independence_class(spec: ValidatorSpec) -> str:
        if spec.kind == "human":
            return "human"
        if spec.kind in {"deterministic", "rule", "schema", "test"}:
            return "deterministic"
        if spec.independent:
            return "independent"
        return "same_executor"

    @staticmethod
    def _step_event_payload(
        run: _Run,
        start: StepStartRecord,
        *,
        status: str,
        observation: Any | None = None,
        local_decision: Any | None = None,
        resource_use: BudgetUsage | None = None,
        progress: bool | None = None,
        information_gain: float | None = None,
        no_progress_streak: int | None = None,
        ended_at: float | None = None,
    ) -> dict[str, Any]:
        started_at, _ = _iso_utc(start.timestamp)
        payload: dict[str, Any] = {
            "step_id": start.step_id,
            "step_version": "1.0.0",
            "step_hash": start.step_hash,
            "contract_binding": dict(run.contract_binding),
            "sequence_number": start.sequence_number,
            "attempt_number": 1,
            "status": status,
            "summary": ReasoningEngine._step_summary(start.claim),
            "input_evidence_bindings": [
                dict(binding) for binding in start.evidence_bindings
            ],
            "output_evidence_bindings": [],
            "validation_bindings": [],
            "claim": start.claim,
            "evidence_refs": list(start.evidence_refs),
            "action": start.action,
            "started_at": started_at,
        }
        if observation is not None:
            payload["observation"] = observation
        if local_decision is not None:
            payload["local_decision"] = local_decision
        if resource_use is not None:
            payload["resource_use"] = ReasoningEngine._schema_step_resource_use(resource_use)
        if progress is not None:
            payload["progress"] = progress
        if information_gain is not None:
            payload["information_gain"] = information_gain
        if no_progress_streak is not None:
            payload["no_progress_streak"] = no_progress_streak
        if ended_at is not None:
            payload["ended_at"] = _iso_utc(ended_at)[0]
        return payload

    def _append_event(
        self,
        run: _Run,
        *,
        event_type: str,
        payload: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
        state: WorkflowState | None = None,
        step_id: str | None = None,
        candidate_path_id: str | None = None,
        tool_call_id: str | None = None,
        human_work_id: str | None = None,
        previous_state: WorkflowState | None = None,
        next_state: WorkflowState | None = None,
        transition_id: str | None = None,
        resources: Mapping[str, Any] | None = None,
        timestamp: float | str | None = None,
        stop_reason: str | None = None,
        escalation_reason: str | None = None,
    ) -> ReasoningEvent:
        """Emit one run-context event / 发出一条携带运行上下文的事件。"""

        prior = self.events.events(run.run_id)
        parent_event_id = prior[-1].event_id if prior else None
        return self.events.append(
            run_id=run.run_id,
            task_id=run.task_id,
            workflow_id=run.workflow_id,
            event_type=event_type,
            state=state or run.state,
            payload=payload,
            idempotency_key=idempotency_key,
            step_id=step_id,
            candidate_path_id=candidate_path_id,
            tool_call_id=tool_call_id,
            human_work_id=human_work_id,
            attempt_id=run.attempt_id,
            causation_id=parent_event_id,
            parent_event_id=parent_event_id,
            scene_id=run.scene_id,
            risk_level=run.risk_level,
            reasoning_depth=run.reasoning_depth,
            execution_mode=run.execution_mode,
            primary_topology=run.primary_topology,
            supporting_topologies=run.supporting_topologies,
            snapshot_versions=run.snapshot_versions,
            contract_binding=run.contract_binding,
            resources=resources,
            timestamp=timestamp,
            previous_state=previous_state,
            next_state=next_state,
            transition_id=transition_id,
            stop_reason=stop_reason,
            escalation_reason=escalation_reason,
        )

    @staticmethod
    def _usage_from_step_resources(resources: Mapping[str, Any]) -> BudgetUsage:
        """Reconstruct a runtime usage vector from StepRecord resources / 从步骤资源重建运行时用量向量。"""

        values: dict[str, int | float] = {}
        for runtime_name, schema_name in _EVENT_BUDGET_NAMES.items():
            state = resources.get(schema_name)
            value_state = (
                None
                if not isinstance(state, Mapping)
                else state.get("value_state", state.get("state"))
            )
            if value_state not in {"observed", "observed_zero", "computed"}:
                raise ReasoningRuntimeError(
                    "step resource use is not reconstructable / 步骤资源用量不可重建"
                )
            value = state.get("value")
            if value is None:
                raise ReasoningRuntimeError(
                    "step resource value is missing / 步骤资源值缺失"
                )
            values[runtime_name] = (
                float(value) if runtime_name == "cost_units" else value
            )
        return BudgetUsage(**values)

    def _rehydrate_run_from_events(
        self,
        run: _Run,
        events: Sequence[ReasoningEvent],
        *,
        candidate_artifact: Any | None,
    ) -> None:
        """Rebuild one mutable aggregate from its authoritative events.

        The event stream restores control state, budgets, public step records,
        evidence, candidates, and validator outcomes. Raw candidate content is
        restored only when the caller resupplies content matching the recorded
        candidate binding. / 从权威事件重建一个可变聚合，包括控制状态、预算、公开
        步骤记录、证据、候选绑定和验证结果；候选原文只有在调用方重新提供且哈希
        与记录绑定一致时才恢复。
        """

        if not events:
            raise ReasoningRuntimeError(
                "resume requires an existing event stream / 恢复要求已有事件流"
            )
        replayed = self.replay(run.run_id)
        budget_by_step: dict[str, str | None] = {}
        candidate_evidence_hashes: dict[str, str] = {}
        final_evidence_record_bindings: list[dict[str, str]] = []

        first_envelope = events[0].as_dict()
        run.attempt_id = first_envelope["attempt_id"]
        for event in events:
            envelope = event.as_dict()
            expected_context = {
                "task_id": run.task_id,
                "workflow_id": run.workflow_id,
                "run_id": run.run_id,
                "scene_id": run.scene_id,
                "risk_level": run.risk_level.value,
                "reasoning_depth": run.reasoning_depth,
                "execution_mode": run.execution_mode,
                "primary_topology": run.primary_topology,
                "supporting_topologies": list(run.supporting_topologies),
                "contract_binding": run.contract_binding,
            }
            if any(envelope.get(key) != value for key, value in expected_context.items()):
                raise ReasoningRuntimeError(
                    "event context differs from the sealed contract / 事件上下文与封存契约不一致"
                )
            if envelope.get("attempt_id") != run.attempt_id:
                raise ReasoningRuntimeError(
                    "event attempt identity drift / 事件尝试标识漂移"
                )

            payload = event.payload
            if event.event_type == "budget_reserved":
                run.budget.reserve(
                    BudgetUsage.from_value(payload["delta"]),
                    payload["reservation_id"],
                )
            elif event.event_type == "budget_consumed":
                reservation_id = payload.get("reservation_id")
                run.budget.consume(
                    BudgetUsage.from_value(payload["delta"]),
                    reservation_id=reservation_id,
                )
                step_id = envelope.get("step_id")
                if step_id is not None:
                    budget_by_step[step_id] = reservation_id
            elif event.event_type == "budget_released":
                run.budget.release(payload["reservation_id"])
            elif event.event_type == "step_started":
                step_id = payload["step_id"]
                if step_id in run.step_starts:
                    raise ReasoningRuntimeError(
                        f"duplicate step start during resume / 恢复时步骤启动重复: {step_id}"
                    )
                run.step_starts[step_id] = StepStartRecord(
                    step_id=step_id,
                    claim=json.loads(_canonical_json(payload["claim"])),
                    evidence_refs=tuple(payload.get("evidence_refs", ())),
                    evidence_bindings=tuple(
                        json.loads(_canonical_json(item))
                        for item in payload["input_evidence_bindings"]
                    ),
                    action=json.loads(_canonical_json(payload["action"])),
                    step_hash=payload["step_hash"],
                    sequence_number=payload["sequence_number"],
                    timestamp=event.timestamp,
                )
            elif event.event_type == "step_closed":
                step_id = payload["step_id"]
                start = run.step_starts.get(step_id)
                if start is None or step_id in run.steps:
                    raise ReasoningRuntimeError(
                        f"invalid step closure during resume / 恢复时步骤关闭非法: {step_id}"
                    )
                resource_use = self._usage_from_step_resources(payload["resource_use"])
                record = StepRecord(
                    step_id=step_id,
                    claim=json.loads(_canonical_json(payload["claim"])),
                    evidence_refs=tuple(payload.get("evidence_refs", ())),
                    evidence_bindings=tuple(
                        json.loads(_canonical_json(item))
                        for item in payload["input_evidence_bindings"]
                    ),
                    budget_reservation_id=budget_by_step.get(step_id),
                    action=json.loads(_canonical_json(payload["action"])),
                    observation=json.loads(_canonical_json(payload["observation"])),
                    local_decision=json.loads(_canonical_json(payload["local_decision"])),
                    resource_use=resource_use,
                    progress=payload["progress"],
                    information_gain=payload.get("information_gain"),
                    no_progress_streak=payload["no_progress_streak"],
                    timestamp=event.timestamp,
                )
                run.steps[step_id] = record
                run.last_information_gain = record.information_gain
            elif event.event_type == "evidence_recorded":
                identity = (payload["evidence_id"], payload["evidence_version"])
                existing = run.evidence_records.get(identity)
                if existing is not None and existing != payload:
                    raise ReasoningRuntimeError(
                        "evidence identity conflict during resume / 恢复时证据标识冲突"
                    )
                run.evidence_records[identity] = json.loads(_canonical_json(payload))
            elif (
                event.event_type == "candidate_created"
                and envelope.get("candidate_path_id") is None
            ):
                run.candidate_hash = payload["candidate_binding"]["hash"]
                run.evidence_hash = payload.get("evidence_set_hash")
                if run.evidence_hash is not None:
                    candidate_evidence_hashes[run.candidate_hash] = run.evidence_hash
                run.evidence_bindings = json.loads(
                    _canonical_json(payload.get("evidence_bindings", []))
                )
                final_evidence_record_bindings = json.loads(
                    _canonical_json(payload.get("evidence_record_bindings", []))
                )
            elif event.event_type == "validation_completed":
                candidate_binding = payload["candidate_binding"]
                evidence_bindings = payload["evidence_bindings"]
                run.validations.append(
                    ValidationRecord(
                        verification_id=payload["validation_id"],
                        validator_id=payload["validator_binding"]["id"],
                        validator_version=payload["validator_binding"]["version"],
                        status=ValidationStatus(payload["result"]),
                        candidate_hash=candidate_binding["hash"],
                        contract_hash=run.contract_hash,
                        evidence_hash=candidate_evidence_hashes.get(
                            candidate_binding["hash"],
                            content_fingerprint(evidence_bindings),
                        ),
                        timestamp=event.timestamp,
                        details_json=_canonical_json(
                            {"reconstructed_details_hash": payload["details_hash"]}
                        ),
                    )
                )

        if final_evidence_record_bindings:
            indexed = {
                (record["evidence_id"], record["evidence_version"], record["record_hash"]): record
                for record in run.evidence_records.values()
            }
            try:
                run.evidence = [
                    indexed[(item["id"], item["version"], item["hash"])]
                    for item in final_evidence_record_bindings
                ]
            except KeyError as exc:
                raise ReasoningRuntimeError(
                    "final candidate evidence is missing during resume / 恢复时最终候选证据缺失"
                ) from exc
        if candidate_artifact is not None:
            if run.candidate_hash is None or candidate_fingerprint(candidate_artifact) != run.candidate_hash:
                raise ReasoningRuntimeError(
                    "resupplied candidate does not match the event binding / 重供候选与事件绑定不一致"
                )
            run.candidate = json.loads(_canonical_json(candidate_artifact))

        run.state = replayed.state
        run.terminal_reason = replayed.terminal_reason
        run.no_progress_streak = replayed.no_progress_streak
        run.release_gate_evaluated_at = replayed.release_gate_evaluated_at
        persisted_result = self.events.load_terminal_result(run.run_id)
        if persisted_result is not None:
            validate_reasoning_result(persisted_result, contract=run.contract)
            if persisted_result["terminal_state"] != run.state.value:
                raise ReasoningRuntimeError(
                    "persisted terminal result differs from replayed state / "
                    "持久化终态结果与重放状态不一致"
                )
            run.sealed_result_json = _canonical_json(persisted_result)

    def resume_run_from_contract(
        self,
        contract: Mapping[str, Any],
        *,
        candidate_artifact: Any | None = None,
    ) -> str:
        """Resume an event-backed run without re-emitting establishment events.

        The caller must supply the same sealed contract. Candidate content is
        optional because events intentionally retain only its immutable binding.
        / 使用相同封存契约恢复事件支持的运行，不重复发出建链事件。事件有意只
        保留候选不可变绑定，因此候选内容可选重供。
        """

        return self.create_run_from_contract(
            contract,
            auto_start=False,
            _restore_existing=True,
            _candidate_artifact=candidate_artifact,
        )

    def create_run_from_contract(
        self,
        contract: Mapping[str, Any],
        *,
        auto_start: bool = True,
        _restore_existing: bool = False,
        _candidate_artifact: Any | None = None,
    ) -> str:
        """Create a run from the normative reasoning-contract artifact.

        The fully validated contract is the sole authority for identity,
        routing, budget, validators, stop limits, governance, and its binding
        hash. Reject or escalate route decisions never satisfy the contract
        Schema and therefore cannot enter execution through this method.
        / 从规范推理契约制品创建运行。经过完整校验的契约是标识、路由、预算、
        验证器、停止上限、治理和绑定哈希的唯一权威；拒绝或升级路由不满足契约
        Schema，因此无法通过本方法进入执行态。
        """

        artifact = json.loads(_canonical_json(dict(contract)))
        validate_reasoning_contract(artifact)
        budget = artifact["budget"]
        limits = BudgetLimits.from_value(
            {
                "max_reasoning_tokens": budget["max_reasoning_tokens"],
                "max_latency_ms": budget["max_latency_ms"],
                "max_model_calls": budget["max_model_calls"],
                "max_tool_calls": budget["max_tool_calls"],
                "max_parallel_paths": budget["max_parallel_paths"],
                "max_iterations": budget["max_iterations"],
                "max_retries": budget["max_retries"],
                "max_total_cost_units": budget["max_total_cost_units"],
            }
        )
        validator_specs = tuple(
            ValidatorSpec(
                validator_id=item["validator_id"],
                version=item["validator_version"],
                kind=item["validator_type"],
                required=item["required"],
                pass_criteria=_canonical_json(item["pass_criteria"]),
                independent=item["validator_type"]
                in {"deterministic", "simulation", "human"},
                timeout_ms=item["timeout_ms"],
                definition_hash=content_fingerprint(item),
                criteria_hash=content_fingerprint(item["pass_criteria"]),
            )
            for item in artifact["validators"]
        )
        no_progress_condition = validate_runtime_contract_capabilities(artifact)
        budget_policy = budget["on_exhaustion"]
        return self.create_run(
            task_id=artifact["task_id"],
            workflow_id=artifact["workflow_id"],
            risk_level=artifact["governance"]["risk_level"],
            contract=artifact,
            budget_limits=limits,
            validators=validator_specs,
            max_no_progress_steps=(
                no_progress_condition["consecutive_steps"]
                if no_progress_condition is not None
                else None
            ),
            run_id=artifact["run_id"],
            auto_start=auto_start,
            escalate_on_limit=budget_policy == "escalate",
            budget_on_exhaustion=budget_policy,
            no_progress_min_information_gain=(
                no_progress_condition["min_information_gain"]
                if no_progress_condition is not None
                else None
            ),
            no_progress_on_trigger=(
                no_progress_condition["on_trigger"]
                if no_progress_condition is not None
                else None
            ),
            scene_id=artifact["scene_id"],
            execution_mode=artifact["execution_mode"],
            supporting_topologies=artifact["supporting_topologies"],
            _restore_existing=_restore_existing,
            _candidate_artifact=_candidate_artifact,
        )

    def create_run(
        self,
        *,
        task_id: str,
        workflow_id: str | None = None,
        risk_level: RiskLevel | str = RiskLevel.LOW,
        contract: Mapping[str, Any] | None = None,
        budget_limits: BudgetLimits | Mapping[str, Any] | None = None,
        validators: Iterable[ValidatorSpec] = (),
        max_no_progress_steps: int | None = 2,
        run_id: str | None = None,
        auto_start: bool = True,
        escalate_on_limit: bool = False,
        budget_on_exhaustion: str | None = None,
        no_progress_min_information_gain: float | None = None,
        no_progress_on_trigger: str | None = None,
        scene_id: str = "default",
        execution_mode: str = "direct",
        supporting_topologies: Iterable[str] | None = None,
        _restore_existing: bool = False,
        _candidate_artifact: Any | None = None,
    ) -> str:
        """Create a run and optionally establish it through ``executing`` / 创建运行并可自动建立到执行态。"""

        if _restore_existing and auto_start:
            raise ValueError(
                "restored runs cannot auto-start / 恢复运行不得自动建链"
            )

        if not task_id:
            raise ValueError("task_id is required / 任务标识不能为空")
        if max_no_progress_steps is not None:
            if isinstance(max_no_progress_steps, bool) or not isinstance(max_no_progress_steps, int):
                raise TypeError("max_no_progress_steps must be an integer or null / 无进展上限必须为整数或空")
            if max_no_progress_steps <= 0:
                raise ValueError("max_no_progress_steps must be positive / 无进展上限必须大于 0")
        if no_progress_min_information_gain is not None:
            if (
                isinstance(no_progress_min_information_gain, bool)
                or not isinstance(no_progress_min_information_gain, (int, float))
                or not math.isfinite(float(no_progress_min_information_gain))
                or not 0 <= float(no_progress_min_information_gain) <= 1
            ):
                raise ValueError(
                    "no-progress minimum information gain must be within [0, 1] / "
                    "无进展最小信息增益必须位于 [0, 1]"
                )
            no_progress_min_information_gain = float(
                no_progress_min_information_gain
            )
        if no_progress_on_trigger not in {None, "fail", "escalate"}:
            raise ValueError(
                "no-progress on_trigger must be fail or escalate / "
                "无进展触发动作必须为 fail 或 escalate"
            )
        if (
            no_progress_min_information_gain is not None
            or no_progress_on_trigger is not None
        ) and (
            max_no_progress_steps is None
            or no_progress_min_information_gain is None
            or no_progress_on_trigger is None
        ):
            raise ValueError(
                "no-progress threshold, information gain, and action must be configured together / "
                "无进展步数、信息增益与动作必须成组配置"
            )
        resolved_budget_policy = budget_on_exhaustion or (
            "escalate" if escalate_on_limit else "stop"
        )
        if resolved_budget_policy not in {"stop", "escalate", "reject"}:
            raise ValueError(
                "budget exhaustion policy must be stop, escalate, or reject; degrade needs a plan / "
                "预算耗尽策略必须为 stop、escalate 或 reject；degrade 需要显式方案"
            )
        if escalate_on_limit and resolved_budget_policy != "escalate":
            raise ValueError(
                "escalate_on_limit conflicts with budget_on_exhaustion / "
                "escalate_on_limit 与 budget_on_exhaustion 冲突"
            )
        identifier = run_id or f"run-{uuid.uuid4().hex}"
        resolved_workflow_id = workflow_id or task_id
        _validate_identifier("task_id", task_id)
        _validate_identifier("workflow_id", resolved_workflow_id)
        _validate_identifier("run_id", identifier)
        _validate_identifier("scene_id", scene_id)
        risk = RiskLevel(risk_level)
        reasoning_depth, primary_topology, default_supporting_topologies = self._mode_context(
            execution_mode
        )
        supporting_topology_values = (
            default_supporting_topologies
            if supporting_topologies is None
            else tuple(supporting_topologies)
        )
        if len(set(supporting_topology_values)) != len(supporting_topology_values) or any(
            topology not in {"orchestration", "hierarchy"}
            for topology in supporting_topology_values
        ):
            raise ValueError("invalid supporting topology / 支撑拓扑非法")
        limits = BudgetLimits.from_value(budget_limits)
        specs = self._normalize_validators(validators)
        supplied_contract = json.loads(_canonical_json(dict(contract or {})))
        is_normative_contract = {
            "schema_version",
            "contract_hash",
            "routing_decision",
            "governance",
            "normalized_input_binding",
        } <= set(supplied_contract)
        if is_normative_contract:
            validate_reasoning_contract(supplied_contract)
            for key, expected in (
                ("task_id", task_id),
                ("workflow_id", resolved_workflow_id),
                ("run_id", identifier),
                ("scene_id", scene_id),
            ):
                if supplied_contract[key] != expected:
                    raise ValueError(f"contract {key} mismatch / 契约 {key} 不匹配")
            if supplied_contract["governance"]["risk_level"] != risk.value:
                raise ValueError("contract risk level mismatch / 契约风险级别不匹配")
            declared_budget = supplied_contract["budget"]
            if declared_budget["on_exhaustion"] != resolved_budget_policy:
                raise ValueError(
                    "contract budget exhaustion action must exactly match runtime policy / "
                    "契约预算耗尽动作必须与运行时策略完全一致"
                )
            expected_limits = BudgetLimits.from_value(
                {
                    key: declared_budget[key]
                    for key in (
                        "max_reasoning_tokens",
                        "max_latency_ms",
                        "max_model_calls",
                        "max_tool_calls",
                        "max_parallel_paths",
                        "max_iterations",
                        "max_retries",
                        "max_total_cost_units",
                    )
                }
            )
            if limits != expected_limits:
                raise ValueError(
                    "contract budget must exactly match the authoritative ledger limits / "
                    "契约预算必须与权威账本上限完全一致"
                )
            contract_validators = {item["validator_id"]: item for item in supplied_contract["validators"]}
            if set(contract_validators) != set(specs):
                raise ValueError(
                    "contract validators must exactly match the authoritative release gate / "
                    "契约验证器必须与权威放行闸门完全一致"
                )
            bound_specs: dict[str, ValidatorSpec] = {}
            for validator_id, spec in specs.items():
                declared = contract_validators[validator_id]
                expected_definition_hash = content_fingerprint(declared)
                expected_criteria_hash = content_fingerprint(
                    declared["pass_criteria"]
                )
                if (
                    declared["validator_version"] != spec.version
                    or declared["validator_type"] != spec.kind
                    or declared["required"] is not spec.required
                    or _canonical_json(declared["pass_criteria"]) != spec.pass_criteria
                    or declared["timeout_ms"] != spec.timeout_ms
                    or spec.definition_hash
                    not in {None, expected_definition_hash}
                    or spec.criteria_hash not in {None, expected_criteria_hash}
                ):
                    raise ValueError(
                        f"contract validator drift / 契约验证器漂移: {validator_id}"
                    )
                bound_specs[validator_id] = replace(
                    spec,
                    definition_hash=expected_definition_hash,
                    criteria_hash=expected_criteria_hash,
                )
            specs = bound_specs
            declared_no_progress_condition = validate_runtime_contract_capabilities(
                supplied_contract
            )
            expected_no_progress = (
                None
                if declared_no_progress_condition is None
                else (
                    declared_no_progress_condition["consecutive_steps"],
                    float(declared_no_progress_condition["min_information_gain"]),
                    declared_no_progress_condition["on_trigger"],
                )
            )
            runtime_no_progress = (
                None
                if max_no_progress_steps is None
                else (
                    max_no_progress_steps,
                    no_progress_min_information_gain,
                    no_progress_on_trigger,
                )
            )
            if expected_no_progress != runtime_no_progress:
                raise ValueError(
                    "contract no-progress threshold, information gain, and action must exactly match runtime / "
                    "契约无进展阈值、信息增益与动作必须与运行时完全一致"
                )
            for field_name, runtime_value in (
                ("execution_mode", execution_mode),
                ("reasoning_depth", reasoning_depth),
                ("primary_topology", primary_topology),
                ("supporting_topologies", list(supporting_topology_values)),
            ):
                if supplied_contract[field_name] != runtime_value:
                    raise ValueError(
                        f"contract {field_name} must match runtime routing / "
                        f"契约 {field_name} 必须与运行时路由一致"
                    )
            contract_hash = supplied_contract["contract_hash"]
        else:
            for key, expected in (
                ("task_id", task_id),
                ("run_id", identifier),
                ("risk_level", risk.value),
            ):
                if key in supplied_contract and supplied_contract[key] != expected:
                    raise ValueError(f"contract {key} mismatch / 契约 {key} 不匹配")
                supplied_contract[key] = expected
            supplied_contract.setdefault("contract_version", "1.0.0")
            runtime_budget = limits.as_dict()
            if "budget" in supplied_contract and supplied_contract["budget"] != runtime_budget:
                raise ValueError(
                    "contract budget must exactly match the authoritative ledger limits / "
                    "契约预算必须与权威账本上限完全一致"
                )
            supplied_contract["budget"] = runtime_budget
            runtime_validators = [spec.as_dict() for spec in specs.values()]
            if (
                "validators" in supplied_contract
                and supplied_contract["validators"] != runtime_validators
            ):
                raise ValueError(
                    "contract validators must exactly match the authoritative release gate / "
                    "契约验证器必须与权威放行闸门完全一致"
                )
            supplied_contract["validators"] = runtime_validators
            if (
                "max_no_progress_steps" in supplied_contract
                and supplied_contract["max_no_progress_steps"] != max_no_progress_steps
            ):
                raise ValueError(
                    "contract no-progress limit must match the runtime limit / "
                    "契约无进展上限必须与运行时上限一致"
                )
            supplied_contract["max_no_progress_steps"] = max_no_progress_steps
            for field_name, runtime_value in (
                ("execution_mode", execution_mode),
                ("reasoning_depth", reasoning_depth),
                ("primary_topology", primary_topology),
                ("supporting_topologies", list(supporting_topology_values)),
            ):
                if (
                    field_name in supplied_contract
                    and supplied_contract[field_name] != runtime_value
                ):
                    raise ValueError(
                        f"contract {field_name} must match runtime routing / "
                        f"契约 {field_name} 必须与运行时路由一致"
                    )
                supplied_contract[field_name] = runtime_value
            contract_hash = content_fingerprint(supplied_contract)
        if "direct_release_rule" in supplied_contract:
            _validate_direct_release_rule(
                supplied_contract["direct_release_rule"],
                execution_mode=execution_mode,
                risk_level=risk,
            )
        raw_normalized_binding = supplied_contract.get("normalized_input_binding")
        if isinstance(raw_normalized_binding, Mapping) and {
            "id",
            "version",
            "hash",
        } <= set(raw_normalized_binding):
            normalized_input_binding = {
                "id": str(raw_normalized_binding["id"]),
                "version": str(raw_normalized_binding["version"]),
                "hash": str(raw_normalized_binding["hash"]),
            }
        else:
            normalized_hash = content_fingerprint(
                {"task_id": task_id, "scene_id": scene_id}
            )
            normalized_input_binding = _versioned_binding(
                _artifact_id("normalized-input", normalized_hash),
                normalized_hash,
            )
        contract_identifier = supplied_contract.get("contract_id")
        if not isinstance(contract_identifier, str) or not contract_identifier:
            contract_identifier = _artifact_id("contract", contract_hash)
        contract_version = supplied_contract.get("contract_version", "1.0.0")
        if (
            not isinstance(contract_version, str)
            or _SEMANTIC_VERSION_PATTERN.fullmatch(contract_version) is None
        ):
            raise ValueError("contract_version must be semantic version text / 契约版本必须是语义版本文本")
        contract_binding = _versioned_binding(
            contract_identifier,
            contract_hash,
            contract_version,
        )
        raw_snapshots = dict(
            supplied_contract.get(
                "snapshot_versions",
                supplied_contract.get("snapshots", {}),
            )
        )
        snapshot_versions = {
            "goal": int(raw_snapshots.get("goal", raw_snapshots.get("goal_version", 1))),
            "constraints": int(
                raw_snapshots.get("constraints", raw_snapshots.get("constraint_version", 1))
            ),
            "verified_facts": int(
                raw_snapshots.get(
                    "verified_facts",
                    raw_snapshots.get("verified_fact_version", 1),
                )
            ),
        }
        if any(version <= 0 for version in snapshot_versions.values()):
            raise ValueError("snapshot versions must be positive / 快照版本必须大于 0")

        with self._lock:
            if identifier in self._runs:
                raise ValueError(f"run_id already exists / 运行标识已存在: {identifier}")
            run = _Run(
                task_id=task_id,
                workflow_id=resolved_workflow_id,
                run_id=identifier,
                risk_level=risk,
                state=WorkflowState.RECEIVED,
                contract=supplied_contract,
                contract_hash=contract_hash,
                validators=specs,
                budget=BudgetLedger(limits),
                max_no_progress_steps=max_no_progress_steps,
                escalate_on_limit=escalate_on_limit,
                budget_on_exhaustion=resolved_budget_policy,
                no_progress_min_information_gain=no_progress_min_information_gain,
                no_progress_on_trigger=no_progress_on_trigger,
                attempt_id=f"attempt-{uuid.uuid4().hex}",
                scene_id=scene_id,
                reasoning_depth=reasoning_depth,
                execution_mode=execution_mode,
                primary_topology=primary_topology,
                supporting_topologies=supporting_topology_values,
                snapshot_versions=snapshot_versions,
                normalized_input_binding=normalized_input_binding,
                contract_binding=contract_binding,
            )
            if _restore_existing:
                existing_events = self.events.replay(identifier)
                self._rehydrate_run_from_events(
                    run,
                    existing_events,
                    candidate_artifact=_candidate_artifact,
                )
                self._runs[identifier] = run
                return identifier
            self._runs[identifier] = run
            self._append_event(
                run,
                event_type="run_created",
                state=run.state,
                idempotency_key="run_created",
                payload={"normalized_input_binding": normalized_input_binding},
            )
            if auto_start:
                task_binding = _versioned_binding(
                    task_id,
                    content_fingerprint(
                        {
                            "task_id": task_id,
                            "normalized_input_binding": normalized_input_binding,
                        }
                    ),
                )
                if is_normative_contract:
                    self._append_event(
                        run,
                        event_type="task_received",
                        state=run.state,
                        idempotency_key="protocol:task-received",
                        payload={
                            "stage": "received",
                            "task_binding": task_binding,
                        },
                    )
                self._transition(
                    run,
                    WorkflowState.NORMALIZED,
                    reason="automatic establishment: normalized",
                )
                if is_normative_contract:
                    self._append_event(
                        run,
                        event_type="task_normalized",
                        state=run.state,
                        idempotency_key="protocol:task-normalized",
                        payload={
                            "stage": "normalized",
                            "task_binding": task_binding,
                            "normalized_input_binding": normalized_input_binding,
                        },
                    )
                self._transition(
                    run,
                    WorkflowState.GOVERNANCE_PRECHECK,
                    reason="automatic establishment: governance_precheck",
                )
                self._transition(
                    run,
                    WorkflowState.ROUTED,
                    reason="automatic establishment: routed",
                )
                if is_normative_contract:
                    routing = supplied_contract["routing_decision"]
                    self._append_event(
                        run,
                        event_type="route_selected",
                        state=run.state,
                        idempotency_key="protocol:route-selected",
                        payload={
                            "routing_policy_binding": routing["policy_binding"],
                            "disposition": routing["disposition"],
                            "configuration": routing["selected_configuration"],
                            "signals": routing["signals"],
                            "reasons": routing["reasons"],
                            "signal_fingerprint": routing["signal_fingerprint"],
                            "missing_signals": routing["missing_signals"],
                            "abstained": routing["abstained"],
                        },
                    )
                self._transition(
                    run,
                    WorkflowState.CONTRACT_ESTABLISHED,
                    reason="automatic establishment: contract_established",
                )
                if is_normative_contract:
                    self._append_event(
                        run,
                        event_type="contract_established",
                        state=run.state,
                        idempotency_key="protocol:contract-established",
                        payload={
                            "contract_binding": contract_binding,
                            "normalized_input_binding": normalized_input_binding,
                        },
                    )
                self._transition(
                    run,
                    WorkflowState.EXECUTING,
                    reason="automatic establishment: executing",
                )
        return identifier

    def _get(self, run_id: str) -> _Run:
        try:
            return self._runs[run_id]
        except KeyError as exc:
            raise KeyError(f"unknown run / 未知运行: {run_id}") from exc

    def _record_release_gate_evaluation(
        self,
        run: _Run,
        *,
        evaluated_at_iso: str,
        evaluated_at_epoch: float,
        failures: Iterable[str],
    ) -> None:
        """Persist the authoritative gate decision and its clock / 持久化权威闸门决策及时钟。"""

        failure_values = tuple(failures)
        direct_rule = run.contract.get("direct_release_rule")
        if isinstance(direct_rule, Mapping):
            policy_binding = _versioned_binding(
                str(direct_rule["rule_id"]),
                content_fingerprint(direct_rule),
                str(direct_rule["rule_version"]),
            )
        else:
            policy_binding = dict(run.contract_binding)
        self._append_event(
            run,
            event_type="governance_decided",
            state=run.state,
            timestamp=evaluated_at_epoch,
            payload={
                "risk_level": run.risk_level.value,
                "decision": "block" if failure_values else "allow",
                "policy_binding": policy_binding,
                "reason_code": (
                    "release_gate_blocked" if failure_values else "release_gate_passed"
                ),
            },
        )
        run.release_gate_evaluated_at = evaluated_at_iso

    def _feedback_authorization_context(
        self,
        run: _Run,
        *,
        transition_id: str | None = None,
        source: WorkflowState | None = None,
        target: WorkflowState | None = None,
    ) -> dict[str, Any]:
        """Build the bounded public context supplied to a live authorizer.

        The callback never receives the mutable internal run object. / 构造传给实时授权器的
        有界公开上下文；回调不会拿到可变的内部运行对象。
        """

        candidate_binding: dict[str, Any] = (
            {"state": "missing"}
            if run.candidate_hash is None
            else {
                "state": "observed",
                "value": self._candidate_binding(run.candidate_hash),
            }
        )
        context: dict[str, Any] = {
            "workflow_id": run.workflow_id,
            "task_id": run.task_id,
            "run_id": run.run_id,
            "scene_id": run.scene_id,
            "workflow_state": run.state.value,
            "normalized_input_binding": dict(run.normalized_input_binding),
            "contract_binding": dict(run.contract_binding),
            "candidate_binding": candidate_binding,
        }
        if transition_id is not None and source is not None and target is not None:
            context["transition"] = {
                "transition_id": transition_id,
                "from_state": source.value,
                "to_state": target.value,
            }
        return json.loads(_canonical_json(context))

    def _feedback_is_live_authorized(
        self,
        run: _Run,
        feedback: Mapping[str, Any],
        *,
        transition_id: str | None = None,
        source: WorkflowState | None = None,
        target: WorkflowState | None = None,
    ) -> bool:
        """Fail closed unless the injected authority source returns exactly true.

        / 除非注入的授权源明确返回 true，否则默认关闭。
        """

        if self._feedback_authorizer is None:
            return False
        detached_feedback = json.loads(_canonical_json(dict(feedback)))
        context = self._feedback_authorization_context(
            run,
            transition_id=transition_id,
            source=source,
            target=target,
        )
        try:
            decision = self._feedback_authorizer(detached_feedback, context)
        except Exception:
            return False
        return decision is True

    def _assert_feedback_update_authorized(
        self,
        run: _Run,
        feedback: Mapping[str, Any],
    ) -> None:
        if feedback.get("phase") not in {"resolved", "exempted"}:
            return
        if not self._feedback_is_live_authorized(run, feedback):
            raise FeedbackAuthorizationError(
                "feedback resolution or exemption is not live-authorized / "
                f"反馈解决或豁免未获实时授权: {feedback.get('feedback_id', 'unknown')}"
            )

    def record_feedback(
        self,
        run_id: str,
        payload: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> ReasoningEvent:
        """Append one strictly revisioned probe-feedback lifecycle event.

        / 追加一条严格修订的探针反馈生命周期事件。
        """

        content = json.loads(_canonical_json(dict(payload)))
        required = {
            "phase",
            "feedback_id",
            "revision",
            "probe_binding",
            "severity",
            "feedback_type",
            "finding_code",
            "related_event_id",
            "rule_binding",
            "protected_transition",
            "blocking",
            "validity",
            "lifecycle_status",
        }
        missing = required - set(content)
        if missing:
            raise ValueError(
                "feedback fields are missing / 反馈字段缺失: " + ", ".join(sorted(missing))
            )
        feedback_id = str(content["feedback_id"])
        _validate_identifier("feedback_id", feedback_id)
        revision = content["revision"]
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise ValueError("feedback revision must be positive / 反馈修订号必须为正整数")
        event_key = f"feedback:{feedback_id}:{revision}"
        if idempotency_key is not None and idempotency_key != event_key:
            raise ValueError(
                "feedback idempotency_key must derive from id and revision / "
                "反馈幂等键必须由标识与修订号派生"
            )
        with self._lock:
            run = self._get(run_id)
            if run.state in _TERMINAL_STATES:
                raise ReasoningRuntimeError("terminal run cannot accept feedback / 终态运行不能接收反馈")
            previous_event = self.events.find_idempotency(run_id, event_key)
            if previous_event is not None:
                if previous_event.event_type == "feedback_updated" and previous_event.payload == content:
                    return previous_event
                raise DuplicateEventConflictError(
                    f"feedback revision conflict / 反馈修订冲突: {event_key}"
                )
            previous = run.feedback_latest.get(feedback_id)
            if previous is None:
                if revision != 1 or content["phase"] != "raised":
                    raise ReasoningRuntimeError(
                        "feedback lifecycle must start with raised revision 1 / "
                        "反馈生命周期必须从 raised 修订 1 开始"
                    )
            else:
                if revision != previous["revision"] + 1:
                    raise ReasoningRuntimeError(
                        "feedback revisions must be contiguous / 反馈修订号必须连续"
                    )
                allowed_phases = {
                    "raised": {"acknowledged", "resolved", "exempted"},
                    "acknowledged": {"resolved", "exempted"},
                    "resolved": {"raised"},
                    "exempted": {"raised"},
                }
                if content["phase"] not in allowed_phases[previous["phase"]]:
                    raise ReasoningRuntimeError(
                        f"illegal feedback phase / 非法反馈阶段: {previous['phase']} -> {content['phase']}"
                    )
                stable_fields = {
                    "probe_binding",
                    "severity",
                    "feedback_type",
                    "finding_code",
                    "rule_binding",
                    "protected_transition",
                    "blocking",
                    "validity",
                }
                drift = [name for name in stable_fields if content[name] != previous[name]]
                if drift:
                    raise ReasoningRuntimeError(
                        "feedback lifecycle binding drift / 反馈生命周期绑定漂移: "
                        + ", ".join(sorted(drift))
                    )
            self._assert_feedback_update_authorized(run, content)
            event = self._append_event(
                run,
                event_type="feedback_updated",
                state=run.state,
                payload=content,
                idempotency_key=event_key,
            )
            run.feedback_latest[feedback_id] = content
            return event

    def _feedback_exemption_is_valid(
        self,
        run: _Run,
        feedback: Mapping[str, Any],
        *,
        transition_id: str,
        source: WorkflowState,
        target: WorkflowState,
    ) -> bool:
        if feedback["phase"] != "exempted":
            return False
        exemption = feedback["exemption"]
        try:
            _, approved_at = _iso_utc(exemption["approved_at"])
            _, expires_at = _iso_utc(exemption["expires_at"])
            _, now = self._evaluation_time()
        except (KeyError, TypeError, ValueError):
            return False
        if approved_at > now or approved_at >= expires_at or now > expires_at:
            return False
        if exemption["normalized_input_binding"] != run.normalized_input_binding:
            return False
        if exemption["contract_binding"] != run.contract_binding:
            return False
        if exemption["rule_binding"] != feedback["rule_binding"]:
            return False
        expected_candidate: dict[str, Any] = (
            {"state": "missing"}
            if run.candidate_hash is None
            else {
                "state": "observed",
                "value": self._candidate_binding(run.candidate_hash),
            }
        )
        if exemption["candidate_binding"] != expected_candidate:
            return False
        scope = set(exemption["scope"])
        scope_matches = bool(
            {
                transition_id,
                f"transition:{source.value}->{target.value}",
                f"transition:{source.value}:{target.value}",
            }
            & scope
        )
        return scope_matches and self._feedback_is_live_authorized(
            run,
            feedback,
            transition_id=transition_id,
            source=source,
            target=target,
        )

    def _assert_feedback_allows_transition(
        self,
        run: _Run,
        *,
        transition_id: str,
        source: WorkflowState,
        target: WorkflowState,
    ) -> None:
        for feedback in run.feedback_latest.values():
            if not feedback["blocking"]:
                continue
            protected = feedback["protected_transition"]
            if protected["from_state"] != source.value or protected["to_state"] != target.value:
                continue
            protected_id = protected["transition_id"]
            if protected_id is not None and protected_id != transition_id:
                continue
            if feedback["phase"] == "resolved" and self._feedback_is_live_authorized(
                run,
                feedback,
                transition_id=transition_id,
                source=source,
                target=target,
            ):
                continue
            if self._feedback_exemption_is_valid(
                run,
                feedback,
                transition_id=transition_id,
                source=source,
                target=target,
            ):
                continue
            raise FeedbackBlockError(
                f"protected transition blocked by feedback / 受保护转换被反馈阻断: "
                f"{feedback['feedback_id']}"
            )

    def _feedback_is_currently_blocking(
        self,
        run: _Run,
        feedback: Mapping[str, Any],
    ) -> bool:
        """Evaluate snapshot blocking state against the declared transition.

        / 针对反馈声明的受保护转换评估快照中的实时阻断状态。
        """

        if not feedback["blocking"]:
            return False
        protected = feedback["protected_transition"]
        try:
            source = WorkflowState(protected["from_state"])
            target = WorkflowState(protected["to_state"])
        except (KeyError, TypeError, ValueError):
            return True
        transition_id = protected["transition_id"] or (
            f"transition:{source.value}:{target.value}"
        )
        if feedback["phase"] == "resolved":
            return not self._feedback_is_live_authorized(
                run,
                feedback,
                transition_id=transition_id,
                source=source,
                target=target,
            )
        if feedback["phase"] == "exempted":
            return not self._feedback_exemption_is_valid(
                run,
                feedback,
                transition_id=transition_id,
                source=source,
                target=target,
            )
        return True

    def _transition(
        self,
        run: _Run,
        target: WorkflowState,
        *,
        reason: str | None,
        payload: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
        evaluated_at: float | str | None = None,
    ) -> None:
        source = run.state
        if idempotency_key:
            existing = self.events.find_idempotency(run.run_id, idempotency_key)
            if existing is not None:
                existing_payload = existing.payload
                requested_payload = dict(payload or {})
                requested_transition_id = requested_payload.pop("transition_id", None)
                same_command = (
                    existing.event_type == "state_transitioned"
                    and existing_payload.get("to_state") == target.value
                    and existing_payload.get("reason_code") == (reason or target.value)
                    and not requested_payload
                    and (
                        requested_transition_id is None
                        or existing.as_dict().get("transition_id")
                        == requested_transition_id
                    )
                )
                if same_command and run.state is target:
                    return
                raise DuplicateEventConflictError(
                    f"transition idempotency conflict / 转换幂等键冲突: {idempotency_key}"
                )
        if target not in ALLOWED_TRANSITIONS[source]:
            raise IllegalTransitionError(
                f"illegal transition / 非法转换: {source.value} -> {target.value}"
            )
        if target in _TERMINAL_STATES and (not reason or not reason.strip()):
            raise ValueError("terminal transition requires a reason / 终态转换必须提供原因")
        supplied_payload = dict(payload or {})
        transition_id = str(
            supplied_payload.pop("transition_id", f"transition-{uuid.uuid4().hex}")
        )
        _validate_identifier("transition_id", transition_id)
        if supplied_payload:
            raise ValueError(
                "state transition payload accepts only transition_id; use external events for additional artifacts / "
                "状态转换载荷只接受 transition_id；其他制品应使用外部事件"
            )
        self._assert_feedback_allows_transition(
            run,
            transition_id=transition_id,
            source=source,
            target=target,
        )
        transition_timestamp: float | None = None
        if target is WorkflowState.COMPLETED:
            evaluated_at_iso, transition_timestamp = self._evaluation_time(evaluated_at)
            failures = self._completion_failures(
                run,
                evaluated_at_epoch=transition_timestamp,
            )
            self._record_release_gate_evaluation(
                run,
                evaluated_at_iso=evaluated_at_iso,
                evaluated_at_epoch=transition_timestamp,
                failures=failures,
            )
            if failures:
                raise ValidationGateError("; ".join(failures))
        event_payload = {
            "from_state": source.value,
            "to_state": target.value,
            "reason_code": reason or target.value,
        }
        with self.events.transaction(run.run_id):
            self._append_event(
                run,
                event_type="state_transitioned",
                state=target,
                payload=event_payload,
                idempotency_key=idempotency_key,
                previous_state=source,
                next_state=target,
                transition_id=transition_id,
                timestamp=transition_timestamp,
                stop_reason=(
                    reason
                    if target in _TERMINAL_STATES
                    and target is not WorkflowState.ESCALATED
                    else None
                ),
                escalation_reason=(
                    reason if target is WorkflowState.ESCALATED else None
                ),
            )
            if target in _TERMINAL_STATES:
                self._append_event(
                    run,
                    event_type="run_ended",
                    state=target,
                    payload={
                        "terminal_state": target.value,
                        "reason_code": reason or target.value,
                    },
                    idempotency_key=f"run-ended:{transition_id}",
                    timestamp=transition_timestamp,
                    stop_reason=(
                        reason if target is not WorkflowState.ESCALATED else None
                    ),
                    escalation_reason=(
                        reason if target is WorkflowState.ESCALATED else None
                    ),
                )
        run.state = target
        if target in _TERMINAL_STATES:
            run.terminal_reason = reason

    def transition(
        self,
        run_id: str,
        target: WorkflowState | str,
        *,
        reason: str | None = None,
        payload: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
        evaluated_at: float | str | None = None,
    ) -> RunSnapshot:
        """Apply one legal transition and emit its event / 应用一次合法转换并发出事件。"""

        with self._lock:
            run = self._get(run_id)
            resolved_target = WorkflowState(target)
            if evaluated_at is not None and resolved_target is not WorkflowState.COMPLETED:
                raise ValueError(
                    "evaluated_at is only valid for completion / evaluated_at 仅适用于完成转换"
                )
            self._transition(
                run,
                resolved_target,
                reason=reason,
                payload=payload,
                idempotency_key=idempotency_key,
                evaluated_at=evaluated_at,
            )
            return self._snapshot(run)

    def switch_mode(
        self,
        run_id: str,
        *,
        switch_id: str,
        trigger: str,
        trigger_evidence_bindings: Iterable[Mapping[str, Any]] = (),
        unfinished_step_ids: Iterable[str] | None = None,
        budget_impact: BudgetUsage | Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
        switched_at: float | str | None = None,
    ) -> RunSnapshot:
        """Apply one contract-allowlisted, count-limited mode switch.

        The command preserves the atomic budget ledger, records unfinished
        work and triggering evidence, invalidates a candidate when the rule
        requires revalidation, and resumes execution under the new config.
        / 应用一次契约允许且有次数上限的模式切换。命令保留原子预算账本，记录
        未完成工作与触发证据，在规则要求重新验证时使候选失效，并按新配置恢复执行。
        """

        _validate_identifier("switch_id", switch_id)
        evidence_bindings = json.loads(
            _canonical_json([dict(item) for item in trigger_evidence_bindings])
        )
        impact = BudgetUsage.from_value(budget_impact)
        with self._lock:
            run = self._get(run_id)
            event_key = idempotency_key or (
                f"mode-switch:{switch_id}:{run.mode_switch_counts.get(switch_id, 0) + 1}"
            )
            previous = self.events.find_idempotency(run_id, event_key)
            if previous is not None:
                if (
                    previous.event_type == "mode_switched"
                    and previous.payload.get("switch_id") == switch_id
                    and previous.payload.get("trigger") == trigger
                ):
                    return self._snapshot(run)
                raise DuplicateEventConflictError(
                    f"mode-switch idempotency conflict / 模式切换幂等冲突: {event_key}"
                )
            if run.state not in {
                WorkflowState.EXECUTING,
                WorkflowState.WAITING_FOR_EVIDENCE,
                WorkflowState.REPAIRABLE_FAILURE,
            }:
                raise ReasoningRuntimeError(
                    "mode switch requires an active repair/execution state / "
                    "模式切换要求活动执行或修复状态"
                )
            validate_reasoning_contract(run.contract)
            rules = {
                item["switch_id"]: item
                for item in run.contract["allowed_mode_switches"]
            }
            try:
                rule = rules[switch_id]
            except KeyError as exc:
                raise ReasoningRuntimeError(
                    f"mode switch is not allowed by contract / 契约未允许模式切换: {switch_id}"
                ) from exc
            if rule["trigger"] != trigger:
                raise ReasoningRuntimeError(
                    "mode-switch trigger differs from contract / 模式切换触发原因与契约不一致"
                )
            current_configuration = {
                "execution_mode": run.execution_mode,
                "reasoning_depth": run.reasoning_depth,
                "primary_topology": run.primary_topology,
                "supporting_topologies": list(run.supporting_topologies),
            }
            if rule["from"] != current_configuration:
                raise ReasoningRuntimeError(
                    "mode-switch source differs from current configuration / "
                    "模式切换来源与当前配置不一致"
                )
            count = run.mode_switch_counts.get(switch_id, 0) + 1
            if count > rule["max_switches"]:
                raise ReasoningRuntimeError(
                    f"mode-switch limit reached / 模式切换次数已达上限: {switch_id}"
                )
            actual_unfinished = sorted(set(run.step_starts) - set(run.steps))
            declared_unfinished = (
                actual_unfinished
                if unfinished_step_ids is None
                else sorted(set(unfinished_step_ids))
            )
            if declared_unfinished != actual_unfinished:
                raise ReasoningRuntimeError(
                    "unfinished_step_ids must exactly match open steps / "
                    "unfinished_step_ids 必须与未关闭步骤完全一致"
                )
            for step_id in declared_unfinished:
                _validate_identifier("unfinished_step_id", step_id)
            switched_at_iso, switched_at_epoch = self._evaluation_time(switched_at)
            if impact != BudgetUsage():
                self.consume_budget(
                    run_id,
                    impact,
                    idempotency_key=f"{event_key}:budget",
                )
            self._transition(
                run,
                WorkflowState.MODE_SWITCHED,
                reason=f"mode switch requested: {switch_id}",
                idempotency_key=f"{event_key}:enter",
            )
            target = rule["to"]
            run.execution_mode = target["execution_mode"]
            run.reasoning_depth = target["reasoning_depth"]
            run.primary_topology = target["primary_topology"]
            run.supporting_topologies = tuple(target["supporting_topologies"])
            if rule["requires_validation"] and run.candidate_hash is not None:
                run.candidate = None
                run.evidence = None
                run.candidate_hash = None
                run.evidence_hash = None
                run.evidence_bindings = []
            switch_rule_binding = _versioned_binding(
                switch_id,
                content_fingerprint(rule),
                run.contract["contract_version"],
            )
            payload = {
                "switch_id": switch_id,
                "from": current_configuration,
                "to": json.loads(_canonical_json(target)),
                "trigger": trigger,
                "switch_count": count,
                "switch_rule_binding": switch_rule_binding,
                "trigger_evidence_bindings": evidence_bindings,
                "budget_impact": self._schema_budget_delta(impact),
                "unfinished_step_ids": declared_unfinished,
                "requires_validation": rule["requires_validation"],
                "switched_at": switched_at_iso,
            }
            self._append_event(
                run,
                event_type="mode_switched",
                state=run.state,
                payload=payload,
                idempotency_key=event_key,
                timestamp=switched_at_epoch,
            )
            run.mode_switch_counts[switch_id] = count
            run.mode_switch_records.append(
                {
                    "switch_id": switch_id,
                    "from": current_configuration,
                    "to": json.loads(_canonical_json(target)),
                    "trigger": trigger,
                    "switch_rule_binding": switch_rule_binding,
                    "switched_at": switched_at_iso,
                }
            )
            self._transition(
                run,
                WorkflowState.EXECUTING,
                reason=f"mode switch applied: {switch_id}",
                idempotency_key=f"{event_key}:resume",
            )
            return self._snapshot(run)

    def _limit_target(self, run: _Run, event_type: str) -> WorkflowState:
        """Resolve the exact declared limit action / 解析精确声明的限制动作。"""

        if event_type == "budget_exhausted":
            return {
                "stop": WorkflowState.FAILED,
                "escalate": WorkflowState.ESCALATED,
                "reject": WorkflowState.REJECTED,
            }[run.budget_on_exhaustion]
        if event_type == "no_progress_limit_reached":
            if run.no_progress_on_trigger is not None:
                return {
                    "fail": WorkflowState.FAILED,
                    "escalate": WorkflowState.ESCALATED,
                }[run.no_progress_on_trigger]
            if run.escalate_on_limit or run.risk_level in {
                RiskLevel.HIGH,
                RiskLevel.CRITICAL,
            }:
                return WorkflowState.ESCALATED
            return WorkflowState.FAILED
        raise ValueError(f"unsupported limit event / 不支持的限制事件: {event_type}")

    def _close_for_limit(
        self,
        run: _Run,
        reason: str,
        event_type: str,
        *,
        attempted_usage: BudgetUsage | None = None,
    ) -> None:
        target = self._limit_target(run, event_type)
        if event_type == "budget_exhausted":
            snapshot = run.budget.snapshot()
            payload: dict[str, Any] = {
                "reason_code": "budget_limit_exceeded",
                "attempted_delta": self._schema_budget_delta(
                    attempted_usage or BudgetUsage()
                ),
                "budget_snapshot": {
                    "limits": dict(snapshot.limits),
                    "used": dict(snapshot.used),
                    "reserved": dict(snapshot.reserved),
                    "available": dict(snapshot.available),
                    "reservation_count": snapshot.reservation_count,
                },
                "on_exhaustion": run.budget_on_exhaustion,
            }
        elif event_type == "no_progress_limit_reached":
            payload = {
                "consecutive_steps": run.no_progress_streak,
                "configured_limit": run.max_no_progress_steps,
                "minimum_information_gain": (
                    run.no_progress_min_information_gain or 0.0
                ),
                "observed_information_gain": _observed_number(
                    run.last_information_gain or 0.0
                ),
                "on_trigger": (
                    "escalate" if target is WorkflowState.ESCALATED else "stop"
                ),
            }
        else:
            raise ValueError(f"unsupported limit event / 不支持的限制事件: {event_type}")
        with self.events.transaction(run.run_id):
            self._append_event(
                run,
                event_type=event_type,
                state=run.state,
                payload=payload,
                stop_reason=(reason if target is WorkflowState.FAILED else None),
                escalation_reason=(
                    reason if target is WorkflowState.ESCALATED else None
                ),
            )
            self._transition(run, target, reason=reason)

    def consume_budget(
        self,
        run_id: str,
        amounts: BudgetUsage | Mapping[str, Any],
        *,
        reservation_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> BudgetSnapshot:
        """Consume budget once; overrun closes the run fail-closed / 幂等消费预算；越界时关闭运行。"""

        usage = BudgetUsage.from_value(amounts)
        key = idempotency_key
        if usage == BudgetUsage() and reservation_id is None:
            with self._lock:
                return self._get(run_id).budget.snapshot()
        if key is None:
            raise ValueError(
                "positive budget consumption requires idempotency_key / "
                "正向预算消费必须提供 idempotency_key"
            )
        with self._lock:
            run = self._get(run_id)
            if run.state in _TERMINAL_STATES:
                raise ReasoningRuntimeError("terminal run cannot consume budget / 终态运行不能消费预算")
            if run.state not in {
                WorkflowState.EXECUTING,
                WorkflowState.WAITING_FOR_EVIDENCE,
                WorkflowState.MODE_SWITCHED,
                WorkflowState.CANDIDATE_READY,
                WorkflowState.VALIDATING,
                WorkflowState.REPAIRABLE_FAILURE,
            }:
                raise ReasoningRuntimeError(
                    "budget consumption requires an active execution state / 预算消费要求活动执行状态"
                )
            previous = self.events.find_idempotency(run_id, key)
            if previous is not None:
                expected_delta = self._schema_budget_delta(usage)
                if (
                    previous.event_type != "budget_consumed"
                    or previous.payload.get("delta") != expected_delta
                    or previous.payload.get("reservation_id") != reservation_id
                ):
                    raise DuplicateEventConflictError(
                        f"budget idempotency conflict / 预算幂等键冲突: {key}"
                    )
                return run.budget.snapshot()
            checkpoint = run.budget._checkpoint()
            try:
                snapshot = run.budget.consume(usage, reservation_id=reservation_id)
            except BudgetExceededError:
                self._close_for_limit(
                    run,
                    "budget limit exceeded / 预算上限已触发",
                    "budget_exhausted",
                    attempted_usage=usage,
                )
                raise
            try:
                self._append_event(
                    run,
                    event_type="budget_consumed",
                    state=run.state,
                    payload=self._budget_event_payload(
                        run,
                        operation="consume",
                        delta=usage,
                        reservation_id=reservation_id,
                    ),
                    idempotency_key=key,
                    resources=self._event_resources(usage),
                )
            except Exception:
                run.budget._restore(checkpoint)
                raise
            return snapshot

    def reserve_budget(
        self,
        run_id: str,
        amounts: BudgetUsage | Mapping[str, Any],
        *,
        reservation_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> str:
        """Atomically reserve capacity and emit its audit event / 原子预留容量并发出审计事件。"""

        usage = BudgetUsage.from_value(amounts)
        with self._lock:
            run = self._get(run_id)
            identifier = reservation_id or f"reservation-{uuid.uuid4().hex}"
            event_key = idempotency_key or f"budget-reserve:{identifier}"
            previous = self.events.find_idempotency(run_id, event_key)
            if previous is not None:
                payload = previous.payload
                if (
                    previous.event_type == "budget_reserved"
                    and payload.get("delta") == self._schema_budget_delta(usage)
                    and payload.get("reservation_id") == identifier
                ):
                    return identifier
                raise DuplicateEventConflictError(
                    f"budget reservation idempotency conflict / 预算预留幂等冲突: {event_key}"
                )
            if run.state is not WorkflowState.EXECUTING:
                raise ReasoningRuntimeError("budget reservation requires executing state / 预算预留要求执行态")
            checkpoint = run.budget._checkpoint()
            try:
                run.budget.reserve(usage, identifier)
            except BudgetExceededError:
                self._close_for_limit(
                    run,
                    "budget reservation limit exceeded / 预算预留上限已触发",
                    "budget_exhausted",
                    attempted_usage=usage,
                )
                raise
            try:
                self._append_event(
                    run,
                    event_type="budget_reserved",
                    state=run.state,
                    payload=self._budget_event_payload(
                        run,
                        operation="reserve",
                        delta=usage,
                        reservation_id=identifier,
                    ),
                    idempotency_key=event_key,
                )
            except Exception:
                run.budget._restore(checkpoint)
                raise
            return identifier

    def reserve_budget_batch(
        self,
        run_id: str,
        reservations: Mapping[str, BudgetUsage | Mapping[str, Any]],
        *,
        idempotency_key: str,
    ) -> tuple[str, ...]:
        """Atomically reserve one named wave and emit one event per member.

        Either every new reservation and audit event commits, or the ledger and
        event stream both return to their prior state. Exact retries return the
        original identifiers even after individual reservations are consumed.
        / 原子预留一个具名波次并为每个成员发出事件。全部新预留与审计事件共同
        提交，否则账本和事件流均恢复原状；即使部分预留随后已消费，完全相同的
        重试仍返回原标识。
        """

        if not isinstance(idempotency_key, str) or not idempotency_key:
            raise ValueError("idempotency_key is required / 幂等键不能为空")
        if not isinstance(reservations, Mapping) or not reservations:
            raise ValueError(
                "reservations must be a non-empty mapping / 预留批次必须是非空映射"
            )
        normalized = [
            (str(identifier), BudgetUsage.from_value(amounts))
            for identifier, amounts in reservations.items()
        ]
        if any(not identifier for identifier, _ in normalized):
            raise ValueError(
                "reservation IDs must be non-empty strings / 预留标识必须为非空字符串"
            )
        event_keys = [
            f"{idempotency_key}:{index}:{identifier}"
            for index, (identifier, _) in enumerate(normalized, start=1)
        ]

        with self._lock:
            run = self._get(run_id)
            existing = [self.events.find_idempotency(run_id, key) for key in event_keys]
            if any(event is not None for event in existing):
                if not all(event is not None for event in existing):
                    raise DuplicateEventConflictError(
                        "budget batch has a partial event history / 预算批次存在部分事件历史"
                    )
                for event, (identifier, usage) in zip(existing, normalized):
                    assert event is not None
                    if (
                        event.event_type != "budget_reserved"
                        or event.payload.get("reservation_id") != identifier
                        or event.payload.get("delta") != self._schema_budget_delta(usage)
                    ):
                        raise DuplicateEventConflictError(
                            "budget batch idempotency conflict / 预算批次幂等冲突"
                        )
                return tuple(identifier for identifier, _ in normalized)
            if run.state is not WorkflowState.EXECUTING:
                raise ReasoningRuntimeError(
                    "budget reservation requires executing state / 预算预留要求执行态"
                )

            checkpoint = run.budget._checkpoint()
            try:
                with self.events.transaction(run_id):
                    identifiers = run.budget.reserve_many(
                        {identifier: usage for identifier, usage in normalized}
                    )
                    for event_key, (identifier, usage) in zip(event_keys, normalized):
                        self._append_event(
                            run,
                            event_type="budget_reserved",
                            state=run.state,
                            payload=self._budget_event_payload(
                                run,
                                operation="reserve",
                                delta=usage,
                                reservation_id=identifier,
                            ),
                            idempotency_key=event_key,
                        )
            except BudgetExceededError:
                run.budget._restore(checkpoint)
                attempted = BudgetUsage()
                for _, usage in normalized:
                    attempted = attempted.plus(usage)
                self._close_for_limit(
                    run,
                    "budget batch reservation limit exceeded / 预算批次预留上限已触发",
                    "budget_exhausted",
                    attempted_usage=attempted,
                )
                raise
            except Exception:
                run.budget._restore(checkpoint)
                raise
            return identifiers

    def release_budget(
        self,
        run_id: str,
        reservation_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> BudgetSnapshot:
        """Release only unconsumed reserved capacity / 仅释放尚未消费的预留容量。"""

        with self._lock:
            run = self._get(run_id)
            if run.state in _TERMINAL_STATES:
                raise ReasoningRuntimeError("terminal run cannot release budget / 终态运行不能释放预算")
            event_key = idempotency_key or f"budget-release:{reservation_id}"
            previous = self.events.find_idempotency(run_id, event_key)
            if previous is not None:
                if (
                    previous.event_type == "budget_released"
                    and previous.payload.get("reservation_id") == reservation_id
                ):
                    return run.budget.snapshot()
                raise DuplicateEventConflictError(
                    f"budget release idempotency conflict / 预算释放幂等冲突: {event_key}"
                )
            usage = run.budget.reservation(reservation_id)
            checkpoint = run.budget._checkpoint()
            snapshot = run.budget.release(reservation_id)
            try:
                self._append_event(
                    run,
                    event_type="budget_released",
                    state=run.state,
                    payload=self._budget_event_payload(
                        run,
                        operation="release",
                        delta=usage,
                        reservation_id=reservation_id,
                    ),
                    idempotency_key=event_key,
                )
            except Exception:
                run.budget._restore(checkpoint)
                raise
            return snapshot

    def start_step_with_budget_reservation(
        self,
        run_id: str,
        *,
        step_id: str,
        claim: Any,
        evidence_refs: Iterable[str],
        evidence_bindings: Iterable[Mapping[str, Any]] = (),
        action: Any,
        reservation_amounts: BudgetUsage | Mapping[str, Any],
        reservation_id: str,
        reservation_idempotency_key: str | None = None,
        step_idempotency_key: str | None = None,
        candidate_path_id: str | None = None,
    ) -> StepStartRecord:
        """Atomically reserve capacity and start one step / 原子预留容量并启动一个步骤。"""

        _validate_identifier("reservation_id", reservation_id)
        with self._lock:
            run = self._get(run_id)
            budget_checkpoint = run.budget._checkpoint()
            budget_error: BudgetExceededError | None = None
            record: StepStartRecord | None = None
            try:
                with self.events.transaction(run_id):
                    try:
                        self.reserve_budget(
                            run_id,
                            reservation_amounts,
                            reservation_id=reservation_id,
                            idempotency_key=reservation_idempotency_key,
                        )
                    except BudgetExceededError as exc:
                        # The shared limit handler deliberately closes the run.  Keep
                        # that terminal event group and re-raise after the transaction.
                        # 共享限额处理器会有意关闭运行；提交终态事件组后再抛出异常。
                        budget_error = exc
                    else:
                        record = self.start_step(
                            run_id,
                            step_id=step_id,
                            claim=claim,
                            evidence_refs=evidence_refs,
                            evidence_bindings=evidence_bindings,
                            action=action,
                            idempotency_key=step_idempotency_key,
                            candidate_path_id=candidate_path_id,
                        )
            except Exception:
                run.budget._restore(budget_checkpoint)
                raise
            if budget_error is not None:
                raise budget_error
            if record is None:  # Defensive invariant / 防御性不变量
                run.budget._restore(budget_checkpoint)
                raise ReasoningRuntimeError(
                    "reserved step did not start / 已预留步骤未能启动"
                )
            return record

    def record_evidence(
        self,
        run_id: str,
        evidence: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Record one immutable versioned evidence artifact / 记录一个不可变的版本化证据制品。"""

        if not isinstance(evidence, Mapping):
            raise TypeError("evidence must be a mapping / 证据必须是映射")
        record = json.loads(_canonical_json(dict(evidence)))
        required_identity = {
            "evidence_id",
            "evidence_version",
            "evidence_hash",
            "record_hash",
            "contract_binding",
            "candidate_binding",
        }
        missing = sorted(required_identity - set(record))
        if missing:
            raise ValueError(
                f"evidence identity is incomplete / 证据标识不完整: {missing}"
            )
        expected_record_hash = content_fingerprint(
            {key: value for key, value in record.items() if key != "record_hash"}
        )
        if record["record_hash"] != expected_record_hash:
            raise ValueError("evidence record hash mismatch / 证据记录哈希不匹配")
        _validate_identifier("evidence_id", record["evidence_id"])
        identity = (record["evidence_id"], record["evidence_version"])

        with self._lock:
            run = self._get(run_id)
            if run.state not in {
                WorkflowState.EXECUTING,
                WorkflowState.WAITING_FOR_EVIDENCE,
                WorkflowState.CANDIDATE_READY,
                WorkflowState.VALIDATING,
                WorkflowState.REPAIRABLE_FAILURE,
            }:
                raise ReasoningRuntimeError(
                    "evidence recording requires an active run / 证据记录要求运行处于活动状态"
                )
            if record["contract_binding"] != run.contract_binding:
                raise ValueError(
                    "evidence contract binding mismatch / 证据契约绑定不匹配"
                )
            candidate_binding = record["candidate_binding"]
            _validate_binding_state("candidate_binding", candidate_binding)
            if candidate_binding.get("state") == "observed":
                candidate_value = candidate_binding["value"]
                if (
                    run.candidate_hash is None
                    or candidate_value.get("hash") != run.candidate_hash
                ):
                    raise ValueError(
                        "evidence candidate binding is not current / 证据候选绑定不是当前候选"
                    )
            existing = run.evidence_records.get(identity)
            if existing is not None:
                if existing == record:
                    return json.loads(_canonical_json(existing))
                raise DuplicateEventConflictError(
                    "evidence identity reused with different content / 证据标识被不同内容复用"
                )
            event_key = idempotency_key or (
                f"evidence:{record['evidence_id']}:{record['evidence_version']}"
            )
            previous = self.events.find_idempotency(run_id, event_key)
            if previous is not None:
                if previous.event_type == "evidence_recorded" and previous.payload == record:
                    run.evidence_records[identity] = record
                    return json.loads(_canonical_json(record))
                raise DuplicateEventConflictError(
                    f"evidence idempotency conflict / 证据幂等冲突: {event_key}"
                )
            self._append_event(
                run,
                event_type="evidence_recorded",
                state=run.state,
                payload=record,
                idempotency_key=event_key,
            )
            run.evidence_records[identity] = record
            return json.loads(_canonical_json(record))

    def _tool_authorization_context(
        self,
        run: _Run,
        *,
        step_id: str,
        tool_call_id: str,
        tool_binding: Mapping[str, Any],
        authorization_policy_binding: Mapping[str, Any],
        input_hash: str,
        plan_binding: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        """Build bounded public context for the live tool authorizer / 构造实时工具授权器使用的有界公开上下文。"""

        context: dict[str, Any] = {
            "workflow_id": run.workflow_id,
            "task_id": run.task_id,
            "run_id": run.run_id,
            "scene_id": run.scene_id,
            "risk_level": run.risk_level.value,
            "workflow_state": run.state.value,
            "step_id": step_id,
            "tool_call_id": tool_call_id,
            "tool_binding": dict(tool_binding),
            "authorization_policy_binding": dict(
                authorization_policy_binding
            ),
            "input_hash": input_hash,
            "side_effect": False,
        }
        if plan_binding is not None:
            context["plan_binding"] = dict(plan_binding)
        return json.loads(_canonical_json(context))

    def _assert_tool_authorized(
        self,
        run: _Run,
        *,
        step_id: str,
        tool_call_id: str,
        tool_binding: Mapping[str, Any],
        authorization_policy_binding: Mapping[str, Any],
        authorization_binding: Mapping[str, Any],
        input_hash: str,
        plan_binding: Mapping[str, Any] | None,
    ) -> None:
        """Fail closed unless the injected authorizer returns exactly true / 除非注入授权器精确返回 true，否则默认阻断。"""

        if self._tool_authorizer is None:
            raise ToolAuthorizationError(
                "tool dispatch has no live authorizer / 工具分派未配置实时授权器"
            )
        authorization = json.loads(
            _canonical_json(dict(authorization_binding))
        )
        context = self._tool_authorization_context(
            run,
            step_id=step_id,
            tool_call_id=tool_call_id,
            tool_binding=tool_binding,
            authorization_policy_binding=authorization_policy_binding,
            input_hash=input_hash,
            plan_binding=plan_binding,
        )
        try:
            decision = self._tool_authorizer(authorization, context)
        except Exception as exc:
            raise ToolAuthorizationError(
                "tool authorization source failed closed / 工具授权源异常并默认阻断"
            ) from exc
        if decision is not True:
            raise ToolAuthorizationError(
                "tool dispatch authorization was not verified / 工具分派授权未通过验证"
            )

    def dispatch_readonly_tool(
        self,
        run_id: str,
        *,
        step_id: str,
        tool_call_id: str,
        tool_binding: Mapping[str, Any],
        authorization_policy_binding: Mapping[str, Any],
        authorization_binding: Mapping[str, Any],
        tool_input: Any,
        plan_binding: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> ReasoningEvent:
        """Record a read-only tool dispatch without persisting raw input / 记录只读工具分派且不持久化原始输入。"""

        _validate_identifier("step_id", step_id)
        _validate_identifier("tool_call_id", tool_call_id)
        _assert_no_private_reasoning(tool_input, "$.tool_input")
        normalized_tool = dict(
            _normalize_versioned_bindings("tool_binding", [tool_binding])[0]
        )
        normalized_policy = dict(
            _normalize_versioned_bindings(
                "authorization_policy_binding", [authorization_policy_binding]
            )[0]
        )
        normalized_authorization = dict(
            _normalize_versioned_bindings(
                "authorization_binding", [authorization_binding]
            )[0]
        )
        normalized_plan = None
        if plan_binding is not None:
            normalized_plan = dict(
                _normalize_versioned_bindings("plan_binding", [plan_binding])[0]
            )
        input_hash = content_fingerprint(tool_input)
        payload: dict[str, Any] = {
            "phase": "started",
            "action_kind": "tool",
            "tool_binding": normalized_tool,
            "authorization_policy_binding": normalized_policy,
            "authorization_binding": normalized_authorization,
            "authorization_verified": True,
            "input_hash": input_hash,
            "side_effect": False,
        }
        if normalized_plan is not None:
            payload["plan_binding"] = normalized_plan
        event_key = idempotency_key or f"tool-dispatch:{tool_call_id}"
        with self._lock:
            run = self._get(run_id)
            if run.state is not WorkflowState.EXECUTING:
                raise ReasoningRuntimeError(
                    "tool dispatch requires executing state / 工具分派要求处于执行态"
                )
            if step_id not in run.step_starts or step_id in run.steps:
                raise ReasoningRuntimeError(
                    "tool dispatch requires an open step / 工具分派要求存在打开步骤"
                )
            self._assert_tool_authorized(
                run,
                step_id=step_id,
                tool_call_id=tool_call_id,
                tool_binding=normalized_tool,
                authorization_policy_binding=normalized_policy,
                authorization_binding=normalized_authorization,
                input_hash=input_hash,
                plan_binding=normalized_plan,
            )
            previous = self.events.find_idempotency(run_id, event_key)
            if previous is not None:
                envelope = previous.as_dict()
                if (
                    previous.event_type == "action_dispatched"
                    and envelope.get("step_id") == step_id
                    and envelope.get("tool_call_id") == tool_call_id
                    and previous.payload == payload
                ):
                    return previous
                raise DuplicateEventConflictError(
                    f"tool dispatch idempotency conflict / 工具分派幂等冲突: {event_key}"
                )
            if any(
                event.event_type == "action_dispatched"
                and event.as_dict().get("tool_call_id") == tool_call_id
                for event in self.events.events(run_id)
            ):
                raise DuplicateEventConflictError(
                    f"tool_call_id was already dispatched / 工具调用标识已分派: {tool_call_id}"
                )
            return self._append_event(
                run,
                event_type="action_dispatched",
                state=run.state,
                payload=payload,
                idempotency_key=event_key,
                step_id=step_id,
                tool_call_id=tool_call_id,
            )

    def observe_readonly_tool(
        self,
        run_id: str,
        *,
        step_id: str,
        tool_call_id: str,
        tool_binding: Mapping[str, Any],
        authorization_policy_binding: Mapping[str, Any],
        authorization_binding: Mapping[str, Any],
        tool_input: Any,
        outcome: str,
        output: Any = None,
        plan_binding: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> ReasoningEvent:
        """Record a read-only tool outcome using fingerprints only / 仅用指纹记录只读工具结果。"""

        if outcome not in {"succeeded", "failed", "cancelled", "timed_out"}:
            raise ValueError(
                "unknown tool outcome / 未知工具结果: " + str(outcome)
            )
        if outcome == "succeeded" and (output is None or output == ""):
            raise ValueError(
                "succeeded tool output must be a closable non-empty observation / "
                "成功工具输出必须是可关闭步骤使用的非空观察"
            )
        _validate_identifier("step_id", step_id)
        _validate_identifier("tool_call_id", tool_call_id)
        _assert_no_private_reasoning(tool_input, "$.tool_input")
        _assert_no_private_reasoning(output, "$.tool_output")
        normalized_tool = dict(
            _normalize_versioned_bindings("tool_binding", [tool_binding])[0]
        )
        normalized_policy = dict(
            _normalize_versioned_bindings(
                "authorization_policy_binding", [authorization_policy_binding]
            )[0]
        )
        normalized_authorization = dict(
            _normalize_versioned_bindings(
                "authorization_binding", [authorization_binding]
            )[0]
        )
        normalized_plan = None
        if plan_binding is not None:
            normalized_plan = dict(
                _normalize_versioned_bindings("plan_binding", [plan_binding])[0]
            )
        payload: dict[str, Any] = {
            "phase": "completed",
            "action_kind": "tool",
            "tool_binding": normalized_tool,
            "authorization_policy_binding": normalized_policy,
            "authorization_binding": normalized_authorization,
            "authorization_verified": True,
            "input_hash": content_fingerprint(tool_input),
            "outcome": outcome,
            "side_effect": False,
        }
        if outcome == "succeeded" or output is not None:
            payload["output_hash"] = content_fingerprint(output)
        if normalized_plan is not None:
            payload["plan_binding"] = normalized_plan
        event_key = idempotency_key or f"tool-observe:{tool_call_id}"
        with self._lock:
            run = self._get(run_id)
            if run.state is not WorkflowState.EXECUTING:
                raise ReasoningRuntimeError(
                    "tool observation requires executing state / 工具观测要求处于执行态"
                )
            if step_id not in run.step_starts or step_id in run.steps:
                raise ReasoningRuntimeError(
                    "tool observation requires an open step / 工具观测要求存在打开步骤"
                )
            dispatches = [
                event
                for event in self.events.events(run_id)
                if event.event_type == "action_dispatched"
                and event.as_dict().get("tool_call_id") == tool_call_id
            ]
            expected_dispatch = {
                key: value
                for key, value in payload.items()
                if key not in {"phase", "outcome", "output_hash"}
            }
            expected_dispatch["phase"] = "started"
            if (
                len(dispatches) != 1
                or dispatches[0].as_dict().get("step_id") != step_id
                or dispatches[0].payload != expected_dispatch
            ):
                raise ReasoningRuntimeError(
                    "tool observation does not match one dispatch / 工具观测未匹配唯一分派"
                )
            previous = self.events.find_idempotency(run_id, event_key)
            if previous is not None:
                envelope = previous.as_dict()
                if (
                    previous.event_type == "action_observed"
                    and envelope.get("step_id") == step_id
                    and envelope.get("tool_call_id") == tool_call_id
                    and previous.payload == payload
                ):
                    return previous
                raise DuplicateEventConflictError(
                    f"tool observation idempotency conflict / 工具观测幂等冲突: {event_key}"
                )
            if any(
                event.event_type == "action_observed"
                and event.as_dict().get("tool_call_id") == tool_call_id
                for event in self.events.events(run_id)
            ):
                raise DuplicateEventConflictError(
                    f"tool_call_id was already observed / 工具调用标识已观测: {tool_call_id}"
                )
            return self._append_event(
                run,
                event_type="action_observed",
                state=run.state,
                payload=payload,
                idempotency_key=event_key,
                step_id=step_id,
                tool_call_id=tool_call_id,
            )

    def record_step(
        self,
        run_id: str,
        *,
        step_id: str,
        claim: Any,
        evidence_refs: Iterable[str],
        evidence_bindings: Iterable[Mapping[str, Any]] = (),
        action: Any,
        observation: Any,
        local_decision: Any,
        resource_use: BudgetUsage | Mapping[str, Any] | None = None,
        budget_reservation_id: str | None = None,
        progress: bool,
        information_gain: float | None = None,
        idempotency_key: str | None = None,
        candidate_path_id: str | None = None,
    ) -> StepRecord:
        """Record one closable external step and enforce progress stops / 记录一个外部闭环步骤并执行进展停止规则。"""

        if not step_id:
            raise ValueError("step_id is required / 步骤标识不能为空")
        _validate_identifier("step_id", step_id)
        if not isinstance(progress, bool):
            raise TypeError("progress must be boolean / 进展标记必须是布尔值")
        if information_gain is not None and (
            isinstance(information_gain, bool)
            or not isinstance(information_gain, (int, float))
            or not math.isfinite(float(information_gain))
            or not 0 <= float(information_gain) <= 1
        ):
            raise ValueError(
                "information_gain must be within [0, 1] / 信息增益必须位于 [0, 1]"
            )
        if information_gain is not None:
            information_gain = float(information_gain)
        refs = tuple(evidence_refs)
        if (
            any(not isinstance(ref, str) or not ref for ref in refs)
            or len(refs) != len(set(refs))
        ):
            raise ValueError(
                "evidence refs must be unique non-empty strings / 证据引用必须为唯一非空字符串"
            )
        bindings = _normalize_versioned_bindings(
            "evidence_bindings", evidence_bindings
        )
        if bindings and refs != tuple(binding["id"] for binding in bindings):
            raise ValueError(
                "evidence refs must match evidence bindings / 证据引用必须与证据绑定一致"
            )
        if budget_reservation_id is not None:
            _validate_identifier("budget_reservation_id", budget_reservation_id)
        for name, value in {
            "claim": claim,
            "action": action,
            "observation": observation,
            "local_decision": local_decision,
        }.items():
            if value is None or value == "":
                raise ValueError(f"{name} is required / {name} 不能为空")
            _assert_no_private_reasoning(value, f"$.{name}")
        usage = BudgetUsage.from_value(resource_use)
        payload_base = {
            "step_id": step_id,
            "claim": claim,
            "evidence_refs": refs,
            "evidence_bindings": bindings,
            "budget_reservation_id": budget_reservation_id,
            "action": action,
            "observation": observation,
            "local_decision": local_decision,
            "resource_use": usage.as_dict(),
            "progress": progress,
            "information_gain": information_gain,
        }
        fingerprint = content_fingerprint(payload_base)

        with self._lock:
            run = self._get(run_id)
            existing = run.steps.get(step_id)
            if existing is not None:
                existing_fingerprint = content_fingerprint(
                    {
                        "step_id": existing.step_id,
                        "claim": existing.claim,
                        "evidence_refs": existing.evidence_refs,
                        "evidence_bindings": existing.evidence_bindings,
                        "budget_reservation_id": existing.budget_reservation_id,
                        "action": existing.action,
                        "observation": existing.observation,
                        "local_decision": existing.local_decision,
                        "resource_use": existing.resource_use.as_dict(),
                        "progress": existing.progress,
                        "information_gain": existing.information_gain,
                    }
                )
                if existing_fingerprint == fingerprint:
                    return existing
                raise DuplicateEventConflictError(
                    f"step_id reused with different content / 步骤标识内容冲突: {step_id}"
                )
            if run.no_progress_min_information_gain is not None:
                if information_gain is None:
                    raise ValueError(
                        "normative no-progress rule requires measured information_gain / "
                        "规范无进展规则要求提供实测 information_gain"
                    )
                expected_progress = (
                    information_gain >= run.no_progress_min_information_gain
                )
                if progress is not expected_progress:
                    raise ValueError(
                        "progress conflicts with the normative information-gain threshold / "
                        "progress 与规范信息增益阈值冲突"
                    )
            self.start_step(
                run_id,
                step_id=step_id,
                claim=claim,
                evidence_refs=refs,
                evidence_bindings=bindings,
                action=action,
                candidate_path_id=candidate_path_id,
            )
            dedup_key = idempotency_key or f"step:{step_id}"
            previous = self.events.find_idempotency(run_id, dedup_key)
            if previous is not None:
                raise DuplicateEventConflictError(
                    f"step idempotency key already belongs to another event / 步骤幂等键已被其他事件占用: {dedup_key}"
                )
            if run.state is not WorkflowState.EXECUTING:
                raise ReasoningRuntimeError("steps require executing state / 步骤要求处于执行态")
            streak = 0 if progress else run.no_progress_streak + 1
            record = StepRecord(
                step_id=step_id,
                claim=json.loads(_canonical_json(claim)),
                evidence_refs=refs,
                evidence_bindings=tuple(
                    json.loads(_canonical_json(binding)) for binding in bindings
                ),
                budget_reservation_id=budget_reservation_id,
                action=json.loads(_canonical_json(action)),
                observation=json.loads(_canonical_json(observation)),
                local_decision=json.loads(_canonical_json(local_decision)),
                resource_use=usage,
                progress=progress,
                information_gain=information_gain,
                no_progress_streak=streak,
                timestamp=time.time(),
            )
            event_payload = self._step_event_payload(
                run,
                run.step_starts[step_id],
                status="completed",
                observation=record.observation,
                local_decision=record.local_decision,
                resource_use=record.resource_use,
                progress=record.progress,
                information_gain=record.information_gain,
                no_progress_streak=record.no_progress_streak,
                ended_at=record.timestamp,
            )
            budget_checkpoint = run.budget._checkpoint()
            try:
                with self.events.transaction(run_id):
                    if usage != BudgetUsage() or budget_reservation_id is not None:
                        budget_event_key = f"budget:step:{step_id}"
                        if self.events.find_idempotency(run_id, budget_event_key) is not None:
                            raise DuplicateEventConflictError(
                                f"step budget event already exists / 步骤预算事件已存在: {step_id}"
                            )
                        run.budget.consume(
                            usage,
                            reservation_id=budget_reservation_id,
                        )
                        self._append_event(
                            run,
                            event_type="budget_consumed",
                            state=run.state,
                            payload=self._budget_event_payload(
                                run,
                                operation="consume",
                                delta=usage,
                                reservation_id=budget_reservation_id,
                            ),
                            idempotency_key=budget_event_key,
                            step_id=step_id,
                            resources=self._event_resources(usage),
                        )
                    self._append_event(
                        run,
                        event_type="step_closed",
                        state=run.state,
                        payload=event_payload,
                        idempotency_key=dedup_key,
                        step_id=step_id,
                        candidate_path_id=candidate_path_id,
                        resources=self._event_resources(usage),
                    )
            except BudgetExceededError:
                run.budget._restore(budget_checkpoint)
                self._close_for_limit(
                    run,
                    "step budget limit exceeded / 步骤预算上限已触发",
                    "budget_exhausted",
                    attempted_usage=usage,
                )
                raise
            except Exception:
                run.budget._restore(budget_checkpoint)
                raise
            run.steps[step_id] = record
            run.no_progress_streak = streak
            run.last_information_gain = information_gain
            if (
                run.max_no_progress_steps is not None
                and streak >= run.max_no_progress_steps
            ):
                reason = (
                    f"no progress for {streak} consecutive steps / "
                    f"连续 {streak} 个步骤无进展"
                )
                self._close_for_limit(run, reason, "no_progress_limit_reached")
                raise NoProgressLimitError(reason)
            return record

    def start_step(
        self,
        run_id: str,
        *,
        step_id: str,
        claim: Any,
        evidence_refs: Iterable[str],
        evidence_bindings: Iterable[Mapping[str, Any]] = (),
        action: Any,
        idempotency_key: str | None = None,
        candidate_path_id: str | None = None,
    ) -> StepStartRecord:
        """Start a closable step so overdue open work remains observable / 启动可关闭步骤，使逾期未关闭工作保持可观测。"""

        _validate_identifier("step_id", step_id)
        refs = tuple(evidence_refs)
        if (
            any(not isinstance(ref, str) or not ref for ref in refs)
            or len(refs) != len(set(refs))
        ):
            raise ValueError(
                "evidence refs must be unique non-empty strings / 证据引用必须为唯一非空字符串"
            )
        bindings = _normalize_versioned_bindings(
            "evidence_bindings", evidence_bindings
        )
        _validate_identifier(
            "candidate_path_id", candidate_path_id, nullable=True
        )
        if bindings and refs != tuple(binding["id"] for binding in bindings):
            raise ValueError(
                "evidence refs must match evidence bindings / 证据引用必须与证据绑定一致"
            )
        for name, value in {"claim": claim, "action": action}.items():
            if value is None or value == "":
                raise ValueError(f"{name} is required / {name} 不能为空")
            _assert_no_private_reasoning(value, f"$.{name}")
        content = {
            "step_id": step_id,
            "claim": claim,
            "evidence_refs": refs,
            "evidence_bindings": bindings,
            "action": action,
        }
        fingerprint = content_fingerprint(content)
        with self._lock:
            run = self._get(run_id)
            existing = run.step_starts.get(step_id)
            if existing is not None:
                existing_events = [
                    event
                    for event in self.events.events(run_id)
                    if event.event_type == "step_started"
                    and event.as_dict().get("step_id") == step_id
                ]
                if (
                    not existing_events
                    or existing_events[-1].as_dict().get("candidate_path_id")
                    != candidate_path_id
                ):
                    raise DuplicateEventConflictError(
                        "step start candidate path conflicts with the existing event / "
                        "步骤开始的候选路径与既有事件冲突"
                    )
                existing_fingerprint = content_fingerprint(
                    {
                        "step_id": existing.step_id,
                        "claim": existing.claim,
                        "evidence_refs": existing.evidence_refs,
                        "evidence_bindings": existing.evidence_bindings,
                        "action": existing.action,
                    }
                )
                if existing_fingerprint == fingerprint:
                    return existing
                raise DuplicateEventConflictError(
                    f"step start reused with different content / 步骤开始标识内容冲突: {step_id}"
                )
            if step_id in run.steps:
                raise DuplicateEventConflictError(
                    f"closed step cannot be restarted / 已关闭步骤不能重新启动: {step_id}"
                )
            if run.state is not WorkflowState.EXECUTING:
                raise ReasoningRuntimeError("steps require executing state / 步骤要求处于执行态")
            dedup_key = idempotency_key or f"step-start:{step_id}"
            previous = self.events.find_idempotency(run_id, dedup_key)
            if previous is not None:
                raise DuplicateEventConflictError(
                    f"step-start idempotency key is already used / 步骤开始幂等键已被占用: {dedup_key}"
                )
            record = StepStartRecord(
                step_id=step_id,
                claim=json.loads(_canonical_json(claim)),
                evidence_refs=refs,
                evidence_bindings=tuple(
                    json.loads(_canonical_json(binding)) for binding in bindings
                ),
                action=json.loads(_canonical_json(action)),
                step_hash=fingerprint,
                sequence_number=len(run.step_starts) + 1,
                timestamp=time.time(),
            )
            self._append_event(
                run,
                event_type="step_started",
                state=run.state,
                payload=self._step_event_payload(run, record, status="running"),
                idempotency_key=dedup_key,
                step_id=step_id,
                candidate_path_id=candidate_path_id,
            )
            run.step_starts[step_id] = record
            return record

    def set_candidate(
        self,
        run_id: str,
        candidate: Any,
        *,
        evidence: Any = (),
        plan_binding: Mapping[str, Any] | None = None,
        final_claim_ids: Iterable[str] = (),
        idempotency_key: str | None = None,
    ) -> str:
        """Set or replace the external candidate; replacement invalidates old validation / 设置或替换外部候选；替换会使旧验证失效。"""

        _assert_no_private_reasoning(candidate, "$.candidate")
        _assert_no_private_reasoning(evidence, "$.evidence")
        candidate_hash = candidate_fingerprint(candidate)
        evidence_hash = content_fingerprint(evidence)
        evidence_bindings = self._evidence_bindings_for(evidence, evidence_hash)
        evidence_record_bindings = self._evidence_record_bindings_for(evidence)
        claims = tuple(final_claim_ids)
        if any(not isinstance(claim, str) or not claim for claim in claims) or len(
            claims
        ) != len(set(claims)):
            raise ValueError(
                "final claim IDs must be unique non-empty strings / 最终命题标识必须为唯一非空字符串"
            )
        if plan_binding is None:
            normalized_plan_binding = None
            if claims:
                raise ValueError(
                    "final claim IDs require a plan binding / 最终命题标识必须绑定计划"
                )
        elif not isinstance(plan_binding, Mapping):
            raise TypeError("plan binding must be a mapping / 计划绑定必须是映射")
        else:
            normalized_plan_binding = json.loads(_canonical_json(dict(plan_binding)))
        candidate_payload = {
            "candidate_binding": self._candidate_binding(candidate_hash),
            "contract_binding": None,
            "evidence_set_hash": evidence_hash,
            "evidence_bindings": evidence_bindings,
        }
        if evidence_record_bindings:
            candidate_payload["evidence_record_bindings"] = evidence_record_bindings
        if normalized_plan_binding is not None:
            candidate_payload["plan_binding"] = normalized_plan_binding
            candidate_payload["final_claim_ids"] = list(claims)
        with self._lock:
            run = self._get(run_id)
            candidate_payload["contract_binding"] = dict(run.contract_binding)
            if idempotency_key:
                previous = self.events.find_idempotency(run_id, idempotency_key)
                if previous is not None:
                    previous_payload = previous.payload
                    if (
                        previous.event_type == "candidate_created"
                        and previous_payload.get("candidate_binding", {}).get("hash")
                        == candidate_hash
                        and previous_payload.get("evidence_set_hash")
                        == evidence_hash
                        and previous_payload.get("evidence_bindings")
                        == evidence_bindings
                        and previous_payload.get("evidence_record_bindings", [])
                        == evidence_record_bindings
                        and previous_payload.get("plan_binding")
                        == normalized_plan_binding
                        and previous_payload.get("final_claim_ids", [])
                        == list(claims)
                    ):
                        run.candidate = json.loads(_canonical_json(candidate))
                        run.evidence = json.loads(_canonical_json(evidence))
                        run.candidate_hash = candidate_hash
                        run.evidence_hash = evidence_hash
                        run.evidence_bindings = json.loads(
                            _canonical_json(evidence_bindings)
                        )
                        return candidate_hash
                    raise DuplicateEventConflictError(
                        f"candidate idempotency conflict / 候选幂等键冲突: {idempotency_key}"
                    )
            if run.state not in {
                WorkflowState.EXECUTING,
                WorkflowState.CANDIDATE_READY,
                WorkflowState.VALIDATING,
            }:
                raise ReasoningRuntimeError(
                    "candidate can only be set during execution or validation / 只能在执行或验证阶段设置候选"
                )
            self._append_event(
                run,
                event_type="candidate_created",
                state=run.state,
                payload=candidate_payload,
                idempotency_key=idempotency_key,
            )
            run.candidate = json.loads(_canonical_json(candidate))
            run.evidence = json.loads(_canonical_json(evidence))
            run.candidate_hash = candidate_hash
            run.evidence_hash = evidence_hash
            run.evidence_bindings = json.loads(_canonical_json(evidence_bindings))
            if run.state is WorkflowState.EXECUTING:
                self._transition(
                    run,
                    WorkflowState.CANDIDATE_READY,
                    reason="candidate artifact is ready / 候选产物已形成",
                )
            return candidate_hash

    def set_candidate_with_evidence_records(
        self,
        run_id: str,
        candidate: Any,
        *,
        evidence_records: Iterable[Mapping[str, Any]],
        plan_binding: Mapping[str, Any] | None = None,
        final_claim_ids: Iterable[str] = (),
        idempotency_key: str | None = None,
    ) -> str:
        """Atomically bind a candidate and persist its evidence records / 原子绑定候选并持久化其证据记录。"""

        if isinstance(evidence_records, (str, bytes, Mapping)):
            raise TypeError(
                "evidence_records must be an iterable of mappings / "
                "evidence_records 必须是映射迭代器"
            )
        records: list[dict[str, Any]] = []
        for index, record in enumerate(evidence_records):
            if not isinstance(record, Mapping):
                raise TypeError(
                    f"evidence record {index} must be a mapping / "
                    f"证据记录 {index} 必须是映射"
                )
            records.append(json.loads(_canonical_json(dict(record))))
        with self._lock:
            run = self._get(run_id)
            prior = {
                "candidate": run.candidate,
                "evidence": run.evidence,
                "candidate_hash": run.candidate_hash,
                "evidence_hash": run.evidence_hash,
                "evidence_bindings": json.loads(
                    _canonical_json(run.evidence_bindings)
                ),
                "evidence_records": dict(run.evidence_records),
                "state": run.state,
            }
            try:
                with self.events.transaction(run_id):
                    candidate_hash = self.set_candidate(
                        run_id,
                        candidate,
                        evidence=records,
                        plan_binding=plan_binding,
                        final_claim_ids=final_claim_ids,
                        idempotency_key=idempotency_key,
                    )
                    for record in records:
                        self.record_evidence(run_id, record)
            except Exception:
                run.candidate = prior["candidate"]
                run.evidence = prior["evidence"]
                run.candidate_hash = prior["candidate_hash"]
                run.evidence_hash = prior["evidence_hash"]
                run.evidence_bindings = prior["evidence_bindings"]
                run.evidence_records = prior["evidence_records"]
                run.state = prior["state"]
                raise
            return candidate_hash

    def record_parallel_candidate(
        self,
        run_id: str,
        *,
        candidate_path_id: str,
        candidate: Any,
        evidence_records: Iterable[Mapping[str, Any]],
        plan_binding: Mapping[str, Any],
        claim_ids: Iterable[str],
        idempotency_key: str | None = None,
    ) -> dict[str, str]:
        """Record one branch candidate without replacing the run candidate.

        Branch candidates remain immutable comparison inputs. Only the later
        synthesis owner may promote one candidate through ``set_candidate``.
        / 记录一个分支候选，但不替换运行级候选。分支候选保持为不可变比较输入；
        只有后续综合责任方可以通过 ``set_candidate`` 晋升候选。
        """

        _validate_identifier("candidate_path_id", candidate_path_id)
        _assert_no_private_reasoning(candidate, "$.candidate")
        normalized_plan_binding = _normalize_versioned_bindings(
            "plan_binding", (plan_binding,)
        )[0]
        claims = tuple(claim_ids)
        if (
            not claims
            or any(not isinstance(claim, str) or not claim for claim in claims)
            or len(claims) != len(set(claims))
        ):
            raise ValueError(
                "branch claim IDs must be unique non-empty strings / "
                "分支命题标识必须为唯一非空字符串"
            )
        if isinstance(evidence_records, (str, bytes, Mapping)):
            raise TypeError(
                "evidence_records must be an iterable of mappings / "
                "evidence_records 必须是映射迭代器"
            )
        records: list[dict[str, Any]] = []
        for index, record in enumerate(evidence_records):
            if not isinstance(record, Mapping):
                raise TypeError(
                    f"evidence record {index} must be a mapping / "
                    f"证据记录 {index} 必须是映射"
                )
            normalized = json.loads(_canonical_json(dict(record)))
            candidate_state = normalized.get("candidate_binding", {})
            if candidate_state.get("state") == "observed":
                raise ValueError(
                    "branch source evidence must precede candidate selection / "
                    "分支来源证据必须先于候选选择"
                )
            records.append(normalized)

        candidate_hash = candidate_fingerprint(candidate)
        candidate_binding = self._candidate_binding(candidate_hash)
        evidence_hash = content_fingerprint(records)
        evidence_bindings = self._evidence_bindings_for(records, evidence_hash)
        evidence_record_bindings = self._evidence_record_bindings_for(records)
        payload = {
            "candidate_binding": candidate_binding,
            "contract_binding": None,
            "plan_binding": normalized_plan_binding,
            "final_claim_ids": list(claims),
            "evidence_set_hash": evidence_hash,
            "evidence_bindings": evidence_bindings,
            "evidence_record_bindings": evidence_record_bindings,
        }
        event_key = idempotency_key or f"parallel-candidate:{candidate_path_id}"

        with self._lock:
            run = self._get(run_id)
            if run.execution_mode != "parallel" or run.primary_topology != "parallel":
                raise ReasoningRuntimeError(
                    "parallel candidates require parallel execution mode / "
                    "并行候选要求并行执行模式"
                )
            payload["contract_binding"] = dict(run.contract_binding)
            previous = self.events.find_idempotency(run_id, event_key)
            if previous is not None:
                if (
                    previous.event_type == "candidate_created"
                    and previous.as_dict().get("candidate_path_id") == candidate_path_id
                    and previous.payload == payload
                ):
                    return dict(candidate_binding)
                raise DuplicateEventConflictError(
                    f"parallel candidate idempotency conflict / "
                    f"并行候选幂等冲突: {event_key}"
                )
            if run.state is not WorkflowState.EXECUTING:
                raise ReasoningRuntimeError(
                    "parallel candidates require executing state / "
                    "并行候选要求执行态"
                )
            prior_records = dict(run.evidence_records)
            try:
                with self.events.transaction(run_id):
                    for record in records:
                        self.record_evidence(run_id, record)
                    self._append_event(
                        run,
                        event_type="candidate_created",
                        state=run.state,
                        payload=payload,
                        idempotency_key=event_key,
                        candidate_path_id=candidate_path_id,
                    )
            except Exception:
                run.evidence_records = prior_records
                raise
            return dict(candidate_binding)

    def record_parallel_path_update(
        self,
        run_id: str,
        *,
        candidate_path_id: str,
        step_id: str,
        plan_binding: Mapping[str, Any],
        phase: str,
        observed_at: float | str,
        deadline_at: float | str | None,
        lease_id: str | None = None,
        worker_binding: Mapping[str, Any] | None = None,
        lease_revision: int | None = None,
        fencing_token: int | None = None,
        acquired_at: float | str | None = None,
        expires_at: float | str | None = None,
        reason: str | None = None,
        idempotency_key: str | None = None,
    ) -> ReasoningEvent:
        """Record one public lease or deadline transition for a branch.

        / 记录一条分支公开租约或截止时间转换。
        """

        _validate_identifier("candidate_path_id", candidate_path_id)
        _validate_identifier("step_id", step_id)
        if phase not in {
            "acquired",
            "renewed",
            "released",
            "expired",
            "deadline_reached",
        }:
            raise ValueError(f"invalid parallel path phase / 并行路径阶段非法: {phase}")
        normalized_plan = _normalize_versioned_bindings(
            "plan_binding", (plan_binding,)
        )[0]
        observed_iso, _ = self._evaluation_time(observed_at)
        deadline_iso = None if deadline_at is None else _iso_utc(deadline_at)[0]
        payload: dict[str, Any] = {
            "plan_binding": normalized_plan,
            "phase": phase,
            "observed_at": observed_iso,
            "deadline_at": deadline_iso,
        }
        lease_phase = phase in {"acquired", "renewed", "released", "expired"}
        lease_values = (
            lease_id,
            worker_binding,
            lease_revision,
            fencing_token,
            acquired_at,
            expires_at,
        )
        if lease_phase and any(value is None for value in lease_values):
            raise ValueError(
                "lease transitions require identity, worker, revision, acquisition, and expiry / "
                "租约转换必须提供标识、工作者、修订、获取时间和过期时间"
            )
        if lease_id is not None:
            _validate_identifier("lease_id", lease_id)
            payload["lease_id"] = lease_id
        if worker_binding is not None:
            payload["worker_binding"] = _normalize_versioned_bindings(
                "worker_binding", (worker_binding,)
            )[0]
        if lease_revision is not None:
            if (
                isinstance(lease_revision, bool)
                or not isinstance(lease_revision, int)
                or lease_revision < 1
            ):
                raise ValueError(
                    "lease_revision must be positive / lease_revision 必须为正整数"
                )
            payload["lease_revision"] = lease_revision
        if fencing_token is not None:
            if (
                isinstance(fencing_token, bool)
                or not isinstance(fencing_token, int)
                or fencing_token < 1
            ):
                raise ValueError(
                    "fencing_token must be positive / fencing_token 必须为正整数"
                )
            payload["fencing_token"] = fencing_token
        if acquired_at is not None:
            payload["acquired_at"] = _iso_utc(acquired_at)[0]
        if expires_at is not None:
            payload["expires_at"] = _iso_utc(expires_at)[0]
        if reason is not None:
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError("reason must be non-empty / 原因不能为空")
            _assert_no_private_reasoning(reason, "$.parallel_path_reason")
            payload["reason"] = reason
        if phase == "deadline_reached" and reason is None:
            raise ValueError(
                "deadline transition requires a reason / 截止时间转换必须提供原因"
            )
        event_key = idempotency_key or (
            f"parallel-path:{candidate_path_id}:{phase}:"
            f"{lease_revision or observed_iso}"
        )
        with self._lock:
            run = self._get(run_id)
            if run.execution_mode != "parallel" or run.primary_topology != "parallel":
                raise ReasoningRuntimeError(
                    "parallel path updates require parallel execution mode / "
                    "并行路径更新要求并行执行模式"
                )
            existing = self.events.find_idempotency(run_id, event_key)
            if existing is not None:
                if (
                    existing.event_type == "parallel_path_updated"
                    and existing.as_dict().get("candidate_path_id") == candidate_path_id
                    and existing.as_dict().get("step_id") == step_id
                    and existing.payload == payload
                ):
                    return existing
                raise DuplicateEventConflictError(
                    f"parallel path idempotency conflict / 并行路径幂等冲突: {event_key}"
                )
            if run.state is not WorkflowState.EXECUTING:
                raise ReasoningRuntimeError(
                    "parallel path updates require executing state / "
                    "并行路径更新要求执行态"
                )
            return self._append_event(
                run,
                event_type="parallel_path_updated",
                state=run.state,
                payload=payload,
                idempotency_key=event_key,
                step_id=step_id,
                candidate_path_id=candidate_path_id,
                timestamp=observed_iso,
            )

    def compare_parallel_candidates(
        self,
        run_id: str,
        *,
        candidate_bindings: Iterable[Mapping[str, Any]],
        comparison_rule_binding: Mapping[str, Any],
        decision: str,
        selected_candidate_binding: Mapping[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> ReasoningEvent:
        """Emit an auditable comparison over registered branch candidates.

        The richer elimination and minority-finding ledger belongs to the
        synthesis step; this event is the compact, probe-facing decision edge.
        / 对已登记分支候选发出可审计比较事件。更完整的淘汰与少数派台账保存在
        综合步骤中；本事件是面向探针的紧凑决策边。
        """

        if isinstance(candidate_bindings, (str, bytes, Mapping)):
            raise TypeError(
                "candidate_bindings must be an iterable of bindings / "
                "candidate_bindings 必须是绑定迭代器"
            )
        normalized_candidates = tuple(
            _normalize_versioned_bindings(
                f"candidate_bindings[{index}]", (binding,)
            )[0]
            for index, binding in enumerate(candidate_bindings)
        )
        if len(normalized_candidates) < 2:
            raise ValueError(
                "parallel comparison requires at least two candidates / "
                "并行比较至少需要两个候选"
            )
        normalized_rule = _normalize_versioned_bindings(
            "comparison_rule_binding", (comparison_rule_binding,)
        )[0]
        if decision not in {
            "selected",
            "tie",
            "incomparable",
            "more_evidence_required",
        }:
            raise ValueError(f"invalid comparison decision / 比较决定非法: {decision}")
        normalized_selected = None
        if selected_candidate_binding is not None:
            normalized_selected = _normalize_versioned_bindings(
                "selected_candidate_binding", (selected_candidate_binding,)
            )[0]
        if decision == "selected":
            if normalized_selected is None or normalized_selected not in normalized_candidates:
                raise ValueError(
                    "selected decision requires one compared candidate / "
                    "选中决定必须绑定一个已比较候选"
                )
        elif normalized_selected is not None:
            raise ValueError(
                "non-selected decisions cannot carry a selected candidate / "
                "非选中决定不得携带胜出候选"
            )

        payload: dict[str, Any] = {
            "candidate_bindings": list(normalized_candidates),
            "comparison_rule_binding": normalized_rule,
            "decision": decision,
        }
        if normalized_selected is not None:
            payload["selected_candidate_binding"] = normalized_selected
        event_key = idempotency_key or "parallel-candidates-compared"
        with self._lock:
            run = self._get(run_id)
            if run.execution_mode != "parallel" or run.primary_topology != "parallel":
                raise ReasoningRuntimeError(
                    "candidate comparison requires parallel execution mode / "
                    "候选比较要求并行执行模式"
                )
            registered = [
                event.payload.get("candidate_binding")
                for event in self.events.events(run_id)
                if event.event_type == "candidate_created"
                and event.as_dict().get("candidate_path_id") is not None
            ]
            if any(binding not in registered for binding in normalized_candidates):
                raise CandidateRequiredError(
                    "comparison references an unregistered branch candidate / "
                    "比较引用了未登记的分支候选"
                )
            previous = self.events.find_idempotency(run_id, event_key)
            if previous is not None:
                if previous.event_type == "candidate_compared" and previous.payload == payload:
                    return previous
                raise DuplicateEventConflictError(
                    f"candidate comparison idempotency conflict / "
                    f"候选比较幂等冲突: {event_key}"
                )
            if run.state is not WorkflowState.EXECUTING:
                raise ReasoningRuntimeError(
                    "candidate comparison requires executing state / "
                    "候选比较要求执行态"
                )
            return self._append_event(
                run,
                event_type="candidate_compared",
                state=run.state,
                payload=payload,
                idempotency_key=event_key,
            )

    def record_validation(
        self,
        run_id: str,
        *,
        validator_id: str,
        status: ValidationStatus | str,
        details: Mapping[str, Any] | None = None,
        verification_id: str | None = None,
        actor_binding: Mapping[str, Any] | None = None,
        authority_binding: Mapping[str, Any] | None = None,
        attempt: int = 1,
        idempotency_key: str | None = None,
    ) -> ValidationRecord:
        """Record an externally obtained validator outcome / 记录外部获得的验证器结果。"""

        outcome = ValidationStatus(status)
        if outcome is ValidationStatus.NOT_RUN:
            raise ValueError("not_run is not an executed validation / not_run 不是已执行验证")
        detail_values = dict(details or {})
        _assert_no_private_reasoning(detail_values, "$.validation_details")
        if isinstance(attempt, bool) or not isinstance(attempt, int) or attempt < 1:
            raise ValueError("validation attempt must be positive / 验证尝试次数必须为正整数")
        actor_state = json.loads(
            _canonical_json(
                {"state": "unknown"} if actor_binding is None else actor_binding
            )
        )
        authority_state = json.loads(
            _canonical_json(
                {"state": "unknown"}
                if authority_binding is None
                else authority_binding
            )
        )
        _assert_no_private_reasoning(actor_state, "$.actor_binding")
        _assert_no_private_reasoning(authority_state, "$.authority_binding")
        _validate_binding_state("actor_binding", actor_state)
        _validate_binding_state("authority_binding", authority_state)
        conditional_obligations: list[dict[str, Any]] | None = None
        if outcome is ValidationStatus.CONDITIONALLY_PASSED:
            raw_obligations = detail_values.get("conditional_obligations")
            if not isinstance(raw_obligations, list) or not raw_obligations:
                raise ValueError(
                    "conditionally passed validation requires conditional_obligations / "
                    "条件通过必须提供 conditional_obligations"
                )
            conditional_obligations = []
            for obligation in raw_obligations:
                if not isinstance(obligation, Mapping) or set(obligation) != {
                    "obligation_id",
                    "due_state",
                }:
                    raise ValueError(
                        "conditional obligations require obligation_id and due_state / "
                        "条件义务必须包含 obligation_id 与 due_state"
                    )
                obligation_id = str(obligation["obligation_id"])
                _validate_identifier("obligation_id", obligation_id)
                due_state = WorkflowState(obligation["due_state"]).value
                conditional_obligations.append(
                    {"obligation_id": obligation_id, "due_state": due_state}
                )
        details_hash = content_fingerprint(detail_values)
        with self._lock:
            run = self._get(run_id)
            if run.candidate_hash is None or run.evidence_hash is None:
                raise CandidateRequiredError("candidate must exist before validation / 验证前必须存在候选")
            try:
                spec = run.validators[validator_id]
            except KeyError as exc:
                raise KeyError(f"unknown validator / 未知验证器: {validator_id}") from exc
            if (
                spec.kind == "human"
                and outcome
                in {
                    ValidationStatus.PASSED,
                    ValidationStatus.CONDITIONALLY_PASSED,
                }
                and (
                    actor_state.get("state") != "observed"
                    or authority_state.get("state") != "observed"
                )
            ):
                raise ValidationGateError(
                    "a passing human validation requires observed actor and authority bindings / "
                    "人工验证通过必须记录可观测的执行人与权限绑定"
                )
            if idempotency_key:
                existing_event = self.events.find_idempotency(run_id, idempotency_key)
                if existing_event is not None:
                    payload = existing_event.payload
                    matches = (
                        existing_event.event_type == "validation_completed"
                        and payload.get("validator_binding")
                        == self._validator_binding(spec)
                        and payload.get("result") == outcome.value
                        and payload.get("candidate_binding")
                        == self._candidate_binding(run.candidate_hash)
                        and payload.get("contract_binding") == run.contract_binding
                        and payload.get("evidence_bindings")
                        == run.evidence_bindings
                        and payload.get("details_hash") == details_hash
                        and payload.get("attempt") == attempt
                        and payload.get("actor_binding") == actor_state
                        and payload.get("authority_binding") == authority_state
                        and (
                            verification_id is None
                            or payload.get("validation_id") == verification_id
                        )
                    )
                    if not matches:
                        raise DuplicateEventConflictError(
                            f"validation idempotency conflict / 验证幂等键冲突: {idempotency_key}"
                        )
                    for existing_record in run.validations:
                        if existing_record.verification_id == payload["validation_id"]:
                            return existing_record
                    raise ReasoningRuntimeError(
                        "validation event exists without its record / 验证事件缺少运行记录"
                    )
            current_binding = (
                validator_id,
                run.candidate_hash,
                run.evidence_hash,
            )
            if (
                outcome is ValidationStatus.PASSED
                and current_binding in run.conditionally_blocked_bindings
            ):
                raise ValidationGateError(
                    "conditional obligations require a revised candidate or evidence binding / "
                    "条件义务要求修订候选或证据绑定后再验证"
                )
            identifier = verification_id or f"verification-{uuid.uuid4().hex}"
            _validate_identifier("verification_id", identifier)
            if run.state is WorkflowState.CANDIDATE_READY:
                self._transition(
                    run,
                    WorkflowState.VALIDATING,
                    reason="validation started / 验证开始",
                )
            elif run.state is not WorkflowState.VALIDATING:
                raise ReasoningRuntimeError("validation requires validating state / 验证要求处于验证态")
            validator_binding = self._validator_binding(spec)
            candidate_binding = self._candidate_binding(run.candidate_hash)
            evidence_bindings = json.loads(_canonical_json(run.evidence_bindings))
            checked_at, checked_at_epoch = self._evaluation_time()
            started_payload = {
                "validation_id": identifier,
                "validator_binding": validator_binding,
                "candidate_binding": candidate_binding,
                "contract_binding": dict(run.contract_binding),
                "evidence_bindings": evidence_bindings,
            }
            self._append_event(
                run,
                event_type="validation_started",
                state=run.state,
                payload=started_payload,
                idempotency_key=f"validation-start:{identifier}",
            )
            record = ValidationRecord(
                verification_id=identifier,
                validator_id=validator_id,
                validator_version=spec.version,
                status=outcome,
                candidate_hash=run.candidate_hash,
                contract_hash=run.contract_hash,
                evidence_hash=run.evidence_hash,
                timestamp=checked_at_epoch,
                details_json=_canonical_json(detail_values),
            )
            result_content: dict[str, Any] = {
                "validation_id": identifier,
                "validation_version": "1.0.0",
                "validator_binding": validator_binding,
                "candidate_binding": candidate_binding,
                "contract_binding": dict(run.contract_binding),
                "evidence_bindings": evidence_bindings,
                "criteria_binding": self._criteria_binding(spec),
                "independence_class": self._independence_class(spec),
                "started_at": checked_at,
                "ended_at": checked_at,
                "timeout_ms": spec.timeout_ms,
                "attempt": attempt,
                "actor_binding": actor_state,
                "authority_binding": authority_state,
                "result": outcome.value,
                "checked_at": checked_at,
                "findings": [],
                "details_hash": details_hash,
            }
            if outcome is ValidationStatus.CONDITIONALLY_PASSED:
                result_content["conditional_obligations"] = conditional_obligations
            payload = {
                **result_content,
                "validation_hash": content_fingerprint(result_content),
            }
            self._append_event(
                run,
                event_type="validation_completed",
                state=run.state,
                payload=payload,
                idempotency_key=idempotency_key,
            )
            run.validations.append(record)
            if outcome is ValidationStatus.CONDITIONALLY_PASSED:
                run.conditionally_blocked_bindings.add(current_binding)
                self._transition(
                    run,
                    WorkflowState.REPAIRABLE_FAILURE,
                    reason=(
                        "conditional obligations require explicit re-execution / "
                        "条件义务要求显式重新执行"
                    ),
                )
            elif outcome is ValidationStatus.REPAIRABLE_FAILURE:
                self._transition(
                    run,
                    WorkflowState.REPAIRABLE_FAILURE,
                    reason="validator reported a repairable failure / 验证器报告可修复失败",
                )
            elif outcome is ValidationStatus.NONREPAIRABLE_FAILURE:
                self._transition(
                    run,
                    WorkflowState.FAILED,
                    reason="validator reported a nonrepairable failure / 验证器报告不可修复失败",
                )
            elif outcome is ValidationStatus.HUMAN_REQUIRED:
                self._transition(
                    run,
                    WorkflowState.ESCALATED,
                    reason="validator requires authorized human review / 验证器要求有权限的人工复核",
                )
            elif outcome is ValidationStatus.TIMED_OUT:
                self._transition(
                    run,
                    WorkflowState.TIMED_OUT,
                    reason="validator timed out / 验证器超时",
                )
            return record

    # Friendly alias: this method records a result; it does not execute a validator.
    # 友好别名：该方法记录结果，并不实际执行验证器。
    validate = record_validation

    def _completion_failures(
        self,
        run: _Run,
        *,
        evaluated_at_epoch: float,
    ) -> list[str]:
        failures: list[str] = []
        if run.candidate_hash is None or run.evidence_hash is None:
            return ["candidate is missing / 缺少候选产物"]
        open_steps = set(run.step_starts) - set(run.steps)
        if open_steps:
            failures.append(
                "open steps must be closed before completion / 完成前必须关闭所有步骤: "
                + ", ".join(sorted(open_steps))
            )
        if run.budget.snapshot().reservation_count:
            failures.append(
                "active budget reservations must be consumed or released before completion / "
                "完成前必须消费或释放所有活动预算预留"
            )
        required = [spec for spec in run.validators.values() if spec.required]
        has_direct_release = "direct_release_rule" in run.contract
        if not required and not has_direct_release:
            failures.append(
                "completion requires a mandatory validator or a valid low-risk direct-release rule / "
                "完成必须配置必选验证器或有效的低风险直接放行规则"
            )
        if has_direct_release and not _predicate_matches(
            {"candidate": run.candidate},
            run.contract["direct_release_rule"]["predicate"],
        ):
            failures.append(
                "direct-release predicate did not pass / 直接放行谓词未通过"
            )
        normative_contract = {
            "schema_version",
            "contract_hash",
            "evidence_sufficiency",
            "validators",
        } <= set(run.contract)
        if normative_contract:
            if run.release_claims is None:
                failures.append(
                    "normative completion requires release-bound claims / "
                    "规范完成必须提供绑定到放行的声明"
                )
            elif not isinstance(run.evidence, list) or any(
                not isinstance(item, Mapping) for item in run.evidence
            ):
                failures.append(
                    "normative completion requires structured evidence records / "
                    "规范完成必须提供结构化证据记录"
                )
            else:
                requirements = (
                    run.contract["direct_release_rule"]["required_evidence"]
                    if has_direct_release
                    else run.contract["evidence_sufficiency"]
                )
                try:
                    failures.extend(
                        evidence_sufficiency_failures(
                            {
                                "evidence": run.evidence,
                                "claims": run.release_claims,
                                "created_at": _iso_utc(evaluated_at_epoch)[0],
                            },
                            requirements,
                            evaluated_at=datetime.fromtimestamp(
                                evaluated_at_epoch,
                                tz=timezone.utc,
                            ),
                        )
                    )
                except (KeyError, TypeError, ValueError) as exc:
                    failures.append(
                        "evidence sufficiency cannot be evaluated / "
                        f"无法评估证据充分性: {exc}"
                    )
        elif has_direct_release:
            failures.extend(
                _direct_evidence_failures(
                    run.evidence,
                    run.contract["direct_release_rule"]["required_evidence"],
                    evaluated_at_epoch=evaluated_at_epoch,
                    max_future_skew_seconds=self._max_future_evidence_skew_seconds,
                )
            )
        for spec in required:
            matches = [
                record
                for record in run.validations
                if record.validator_id == spec.validator_id
                and record.validator_version == spec.version
                and record.candidate_hash == run.candidate_hash
                and record.contract_hash == run.contract_hash
                and record.evidence_hash == run.evidence_hash
            ]
            if not matches:
                failures.append(
                    f"mandatory validator is missing or stale / 必选验证缺失或已失效: {spec.validator_id}"
                )
            elif matches[-1].status is not ValidationStatus.PASSED:
                failures.append(
                    f"mandatory validator did not pass / 必选验证未通过: {spec.validator_id}={matches[-1].status.value}"
                )
            elif matches[-1].timestamp > (
                evaluated_at_epoch + self._max_future_evidence_skew_seconds
            ):
                failures.append(
                    f"mandatory validation is timestamped after the release gate / "
                    f"必选验证时间晚于放行门: {spec.validator_id}"
                )
        return failures

    def completion_failures(
        self,
        run_id: str,
        *,
        evaluated_at: float | str | None = None,
    ) -> tuple[str, ...]:
        """Return current release-gate failures without mutation / 无副作用返回当前放行失败项。"""

        with self._lock:
            _, evaluated_at_epoch = self._evaluation_time(evaluated_at)
            return tuple(
                self._completion_failures(
                    self._get(run_id),
                    evaluated_at_epoch=evaluated_at_epoch,
                )
            )

    def finalize(
        self,
        run_id: str,
        *,
        reason: str = "validated completion / 验证完成",
        evaluated_at: float | str | None = None,
        claims: Iterable[Mapping[str, Any]] | None = None,
    ) -> RunSnapshot:
        """Complete only after the exact current candidate passes every gate / 仅当当前候选通过全部闸门时完成。"""

        release_claims = (
            None
            if claims is None
            else json.loads(_canonical_json([dict(claim) for claim in claims]))
        )
        if release_claims is not None:
            _assert_no_private_reasoning(release_claims, "$.release_claims")
        with self._lock:
            run = self._get(run_id)
            if release_claims is not None:
                run.release_claims = release_claims
            _, evaluated_at_epoch = self._evaluation_time(evaluated_at)
            if run.state is WorkflowState.CANDIDATE_READY:
                self._transition(
                    run,
                    WorkflowState.VALIDATING,
                    reason="completion gate evaluation / 评估完成闸门",
                )
            if run.state is not WorkflowState.VALIDATING:
                raise IllegalTransitionError(
                    f"finalize requires validating state / 完成要求验证态: {run.state.value}"
                )
            self._transition(
                run,
                WorkflowState.COMPLETED,
                reason=reason,
                evaluated_at=evaluated_at_epoch,
            )
            return self._snapshot(run)

    def cancel(self, run_id: str, *, reason: str) -> RunSnapshot:
        """Explicitly cancel a non-terminal run / 显式取消非终态运行。"""

        return self.transition(run_id, WorkflowState.CANCELLED, reason=reason)

    def timeout(self, run_id: str, *, reason: str) -> RunSnapshot:
        """Close a non-terminal run as timed out / 将非终态运行关闭为超时。"""

        return self.transition(run_id, WorkflowState.TIMED_OUT, reason=reason)

    @staticmethod
    def _result_budget_accounting(run: _Run) -> dict[str, Any]:
        snapshot = run.budget.snapshot()
        limits = {
            _EVENT_BUDGET_NAMES[name]: _positive_limit(value)
            for name, value in snapshot.limits.items()
        }
        used = {
            _EVENT_BUDGET_NAMES[name]: _observed_number(value)
            for name, value in snapshot.used.items()
        }
        exhausted = [
            _EVENT_BUDGET_NAMES[name]
            for name, limit in snapshot.limits.items()
            if limit is not None and snapshot.used[name] >= limit
        ]
        return {
            "limits": limits,
            "used": used,
            "exhausted_dimensions": exhausted,
        }

    @staticmethod
    def _default_terminal_reason(run: _Run, release_basis: str) -> dict[str, Any]:
        reasons = {
            WorkflowState.COMPLETED: (
                "success",
                "completed_direct_release"
                if release_basis == "direct_release_rule"
                else "completed_validated",
            ),
            WorkflowState.REJECTED: ("policy", "policy_rejected"),
            WorkflowState.FAILED: ("execution", "execution_failed"),
            WorkflowState.ESCALATED: ("human", "human_escalation"),
            WorkflowState.CANCELLED: ("cancellation", "user_cancelled"),
            WorkflowState.TIMED_OUT: ("timeout", "execution_timed_out"),
        }
        category, code = reasons[run.state]
        return {
            "category": category,
            "code": code,
            "source_binding": {
                "state": "observed",
                "value": dict(run.contract_binding),
            },
        }

    def _result_validations(self, run: _Run) -> list[dict[str, Any]]:
        allowed = {
            "validation_id",
            "validation_version",
            "validation_hash",
            "validator_binding",
            "candidate_binding",
            "contract_binding",
            "evidence_bindings",
            "criteria_binding",
            "independence_class",
            "started_at",
            "ended_at",
            "timeout_ms",
            "attempt",
            "actor_binding",
            "authority_binding",
            "result",
            "checked_at",
            "findings",
            "details_hash",
            "conditional_obligations",
        }
        return [
            {key: value for key, value in event.payload.items() if key in allowed}
            for event in self.events.events(run.run_id)
            if event.event_type == "validation_completed"
        ]

    def _result_release_gate(
        self,
        run: _Run,
        validations: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        direct_rule = run.contract.get("direct_release_rule")
        if isinstance(direct_rule, Mapping):
            return {
                "basis": "direct_release_rule",
                "evidence_sufficiency_met": False,
                "direct_rule_binding": _versioned_binding(
                    str(direct_rule["rule_id"]),
                    content_fingerprint(direct_rule),
                    str(direct_rule["rule_version"]),
                ),
            }
        gates: list[dict[str, Any]] = []
        for spec in run.validators.values():
            validator_binding = self._validator_binding(spec)
            matches = [
                item
                for item in validations
                if item["validator_binding"] == validator_binding
                and (
                    run.candidate_hash is None
                    or item["candidate_binding"] == self._candidate_binding(run.candidate_hash)
                )
                and item["contract_binding"] == run.contract_binding
                and item["evidence_bindings"] == run.evidence_bindings
            ]
            latest = matches[-1] if matches else None
            gates.append(
                {
                    "validator_binding": validator_binding,
                    "validation_binding": (
                        {"state": "missing"}
                        if latest is None
                        else {
                            "state": "observed",
                            "value": _versioned_binding(
                                latest["validation_id"],
                                latest["validation_hash"],
                                latest["validation_version"],
                            ),
                        }
                    ),
                    "required": spec.required,
                    "result": "not_run" if latest is None else latest["result"],
                }
            )
        return {
            "basis": "mandatory_validators",
            "evidence_sufficiency_met": False,
            "validator_gates": gates,
        }

    def _result_steps(self, run: _Run) -> list[dict[str, Any]]:
        candidate_binding: dict[str, Any] = (
            {"state": "missing"}
            if run.candidate_hash is None
            else {
                "state": "observed",
                "value": self._candidate_binding(run.candidate_hash),
            }
        )
        result: list[dict[str, Any]] = []
        for event in self.events.events(run.run_id):
            if event.event_type != "step_closed":
                continue
            record = event.payload
            record.pop("evidence_refs", None)
            record["candidate_binding"] = json.loads(_canonical_json(candidate_binding))
            result.append(record)
        return result

    def build_result(
        self,
        run_id: str,
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
        created_at: float | str | None = None,
    ) -> dict[str, Any]:
        """Build and seal the normative terminal result for a governed run.

        Identity, terminal state, contract/candidate bindings, execution,
        budgets, steps, validations, evidence, and release gates are derived
        from the run. Callers provide only domain claims, decision, output,
        follow-up records, limitations, and provenance.
        / 为受治理运行构造并封存规范终态结果。标识、终态、契约/候选绑定、执行、
        预算、步骤、验证、证据和放行门均从运行派生；调用方只提供领域声明、决定、
        输出、后续记录、限制与来源。
        """

        provided = {
            "claims": list(claims),
            "final_decision": dict(final_decision),
            "output": dict(output),
            "field_provenance": list(field_provenance),
            "unresolved_items": list(unresolved_items),
            "next_actions": list(next_actions),
            "limitations": list(limitations),
            "terminal_reason": None if terminal_reason is None else dict(terminal_reason),
        }
        _assert_no_private_reasoning(provided, "$.result")
        with self._lock:
            run = self._get(run_id)
            if run.state not in _TERMINAL_STATES:
                raise ReasoningRuntimeError(
                    "result can only be built for a terminal run / 只能为终态运行构造结果"
                )
            validate_reasoning_contract(run.contract)
            if run.state is WorkflowState.COMPLETED:
                if run.release_claims is None:
                    raise ReasoningRuntimeError(
                        "completed run lacks release-bound claims / 已完成运行缺少放行绑定声明"
                    )
                if _canonical_json(provided["claims"]) != _canonical_json(
                    run.release_claims
                ):
                    raise ValidationGateError(
                        "result claims differ from the release-gate claim set / "
                        "结果声明与放行门声明集合不一致"
                    )
            if _SEMANTIC_VERSION_PATTERN.fullmatch(result_version) is None:
                raise ValueError("result_version must be semantic / 结果版本必须符合语义版本")
            persisted_result = self.events.load_terminal_result(run_id)
            if persisted_result is not None:
                validate_reasoning_result(persisted_result, contract=run.contract)
                if persisted_result["terminal_state"] != run.state.value:
                    raise ReasoningRuntimeError(
                        "persisted terminal result differs from runtime state / "
                        "持久化终态结果与运行状态不一致"
                    )
                run.sealed_result_json = _canonical_json(persisted_result)
            if run.sealed_result_json is not None:
                sealed_result = json.loads(run.sealed_result_json)
                conflicts = [
                    field_name
                    for field_name in (
                        "claims",
                        "final_decision",
                        "field_provenance",
                        "unresolved_items",
                        "next_actions",
                        "limitations",
                    )
                    if _canonical_json(provided[field_name])
                    != _canonical_json(sealed_result[field_name])
                ]
                saved_output = dict(sealed_result["output"])
                if "content_hash" not in provided["output"]:
                    saved_output.pop("content_hash", None)
                if _canonical_json(provided["output"]) != _canonical_json(saved_output):
                    conflicts.append("output")
                if (
                    provided["terminal_reason"] is not None
                    and _canonical_json(provided["terminal_reason"])
                    != _canonical_json(sealed_result["terminal_reason"])
                ):
                    conflicts.append("terminal_reason")
                if result_id is not None and result_id != sealed_result["result_id"]:
                    conflicts.append("result_id")
                if result_version != sealed_result["result_version"]:
                    conflicts.append("result_version")
                if created_at is not None:
                    retry_created_at, _ = self._evaluation_time(created_at)
                    if retry_created_at != sealed_result["created_at"]:
                        conflicts.append("created_at")
                if conflicts:
                    raise DuplicateEventConflictError(
                        "terminal run already has a different sealed result / "
                        "终态运行已有不同的封存结果: "
                        + ", ".join(sorted(set(conflicts)))
                    )
                return sealed_result
            identifier = result_id or f"result-{uuid.uuid4().hex}"
            _validate_identifier("result_id", identifier)
            created_at_iso, _ = self._evaluation_time(created_at)
            evidence = (
                []
                if run.evidence is None
                else json.loads(_canonical_json(run.evidence))
            )
            if not isinstance(evidence, list) or any(
                not isinstance(item, Mapping) for item in evidence
            ):
                raise ReasoningRuntimeError(
                    "normative results require structured evidence records / "
                    "规范结果要求结构化证据记录"
                )
            candidate_binding: dict[str, Any] = (
                {"state": "missing"}
                if run.candidate_hash is None
                else {
                    "state": "observed",
                    "value": self._candidate_binding(run.candidate_hash),
                }
            )
            configuration = {
                "execution_mode": run.execution_mode,
                "reasoning_depth": run.reasoning_depth,
                "primary_topology": run.primary_topology,
                "supporting_topologies": list(run.supporting_topologies),
            }
            initial_configuration = {
                field_name: json.loads(_canonical_json(run.contract[field_name]))
                for field_name in (
                    "execution_mode",
                    "reasoning_depth",
                    "primary_topology",
                    "supporting_topologies",
                )
            }
            validations = self._result_validations(run)
            release_gate = self._result_release_gate(run, validations)
            artifact: dict[str, Any] = {
                "schema_version": "1.0.0",
                "result_id": identifier,
                "result_version": result_version,
                "workflow_id": run.workflow_id,
                "task_id": run.task_id,
                "run_id": run.run_id,
                "scene_id": run.scene_id,
                "terminal_state": run.state.value,
                "terminal_reason": provided["terminal_reason"]
                or self._default_terminal_reason(run, release_gate["basis"]),
                "risk_level": run.risk_level.value,
                "contract_binding": dict(run.contract_binding),
                "candidate_binding": candidate_binding,
                "execution": {
                    "initial_configuration": initial_configuration,
                    "final_configuration": configuration,
                    "mode_switches": json.loads(
                        _canonical_json(run.mode_switch_records)
                    ),
                },
                "budget_accounting": self._result_budget_accounting(run),
                "release_gate": release_gate,
                "evidence_bindings": json.loads(_canonical_json(run.evidence_bindings)),
                "evidence": evidence,
                "steps": self._result_steps(run),
                "validations": validations,
                "claims": provided["claims"],
                "final_decision": provided["final_decision"],
                "unresolved_items": provided["unresolved_items"],
                "next_actions": provided["next_actions"],
                "output": provided["output"],
                "limitations": provided["limitations"],
                "field_provenance": provided["field_provenance"],
                "created_at": created_at_iso,
            }
            if run.release_gate_evaluated_at is not None:
                artifact["release_gate_evaluated_at"] = (
                    run.release_gate_evaluated_at
                )
            requirements = (
                run.contract["direct_release_rule"]["required_evidence"]
                if release_gate["basis"] == "direct_release_rule"
                else run.contract["evidence_sufficiency"]
            )
            release_gate["evidence_sufficiency_met"] = not evidence_sufficiency_failures(
                artifact,
                requirements,
                evaluated_at=(run.release_gate_evaluated_at or created_at_iso),
            )
            sealed = build_artifact("reasoning_result", artifact)
            validate_reasoning_result(sealed, contract=run.contract)
            persisted = self.events.save_terminal_result(run_id, sealed)
            run.sealed_result_json = _canonical_json(persisted)
            return json.loads(run.sealed_result_json)

    def _snapshot(self, run: _Run) -> RunSnapshot:
        return RunSnapshot(
            task_id=run.task_id,
            workflow_id=run.workflow_id,
            run_id=run.run_id,
            scene_id=run.scene_id,
            risk_level=run.risk_level,
            state=run.state,
            execution_mode=run.execution_mode,
            reasoning_depth=run.reasoning_depth,
            primary_topology=run.primary_topology,
            supporting_topologies=run.supporting_topologies,
            mode_switch_count=sum(run.mode_switch_counts.values()),
            blocking_feedback_count=sum(
                self._feedback_is_currently_blocking(run, item)
                for item in run.feedback_latest.values()
            ),
            contract_hash=run.contract_hash,
            candidate_hash=run.candidate_hash,
            evidence_hash=run.evidence_hash,
            step_count=len(run.steps),
            open_step_count=len(set(run.step_starts) - set(run.steps)),
            validation_count=len(run.validations),
            no_progress_streak=run.no_progress_streak,
            terminal_reason=run.terminal_reason,
            release_gate_evaluated_at=run.release_gate_evaluated_at,
            budget=run.budget.snapshot(),
        )

    def snapshot(self, run_id: str) -> RunSnapshot:
        """Return a consistent run snapshot / 返回一致运行快照。"""

        with self._lock:
            return self._snapshot(self._get(run_id))

    def replay(self, run_id: str) -> ReplaySnapshot:
        """Rebuild terminal and validation state from events only / 仅从事件重建终态与验证状态。"""

        events = self.events.replay(run_id)
        if not events:
            raise KeyError(f"no events for run / 运行无事件: {run_id}")
        if events[0].event_type != "run_created":
            raise ReasoningRuntimeError(
                "replay requires run_created as the first event / 重放要求首事件为 run_created"
            )
        state = events[0].state
        terminal_reason: str | None = None
        candidate_hash: str | None = None
        evidence_hash: str | None = None
        no_progress_streak = 0
        validation_count = 0
        open_steps: set[str] = set()
        release_gate_evaluated_at: str | None = None
        terminal_transition_seen = False
        terminal_receipt_seen = False
        for event in events:
            payload = event.payload
            if terminal_receipt_seen:
                raise ReasoningRuntimeError(
                    "event found after terminal receipt / 终态回执后仍存在事件"
                )
            if event.event_type == "state_transitioned":
                source = WorkflowState(payload["from_state"])
                target = WorkflowState(payload["to_state"])
                if source != state or target not in ALLOWED_TRANSITIONS[source] or event.state != target:
                    raise IllegalTransitionError(
                        f"invalid transition in replay / 重放发现非法转换 at sequence {event.sequence}"
                    )
                state = target
                if target in _TERMINAL_STATES:
                    if terminal_transition_seen:
                        raise ReasoningRuntimeError(
                            "multiple terminal transitions / 存在多个终态转换"
                        )
                    terminal_transition_seen = True
                    terminal_reason = payload.get("reason_code")
            elif event.state != state:
                raise ReasoningRuntimeError(
                    f"event state mismatch / 事件状态不一致 at sequence {event.sequence}"
                )
            if (
                event.event_type == "candidate_created"
                and event.as_dict().get("candidate_path_id") is None
            ):
                candidate_hash = payload["candidate_binding"]["hash"]
                evidence_bindings = payload["evidence_bindings"]
                evidence_hash = (
                    payload.get("evidence_set_hash")
                    or (evidence_bindings[0]["hash"] if evidence_bindings else None)
                )
            elif event.event_type == "step_closed":
                open_steps.discard(payload["step_id"])
                no_progress_streak = payload["no_progress_streak"]
            elif event.event_type == "step_started":
                open_steps.add(payload["step_id"])
            elif event.event_type == "validation_completed":
                validation_count += 1
            elif (
                event.event_type == "governance_decided"
                and payload.get("reason_code")
                in {"release_gate_passed", "release_gate_blocked"}
            ):
                release_gate_evaluated_at = _iso_utc(event.timestamp)[0]
            elif event.event_type == "run_ended":
                if not terminal_transition_seen or event.state not in _TERMINAL_STATES:
                    raise ReasoningRuntimeError(
                        "run_ended must follow one terminal transition / "
                        "run_ended 必须紧随一次终态转换"
                    )
                if payload.get("terminal_state") != state.value:
                    raise ReasoningRuntimeError(
                        "run_ended state mismatch / run_ended 终态不一致"
                    )
                terminal_receipt_seen = True
        if terminal_transition_seen and not terminal_receipt_seen:
            raise ReasoningRuntimeError(
                "terminal transition is missing run_ended / 终态转换缺少 run_ended"
            )
        return ReplaySnapshot(
            run_id=run_id,
            state=state,
            event_count=len(events),
            last_sequence=events[-1].sequence,
            terminal_reason=terminal_reason,
            candidate_hash=candidate_hash,
            evidence_hash=evidence_hash,
            no_progress_streak=no_progress_streak,
            validation_count=validation_count,
            open_step_count=len(open_steps),
            release_gate_evaluated_at=release_gate_evaluated_at,
        )
