"""Governed tool-dispatch reference runtime / 受治理工具调度参考运行时。

The dispatcher deliberately separates discovery, frontier construction,
selection, admission, execution authorization, durable idempotency, and result
classification.  A semantic match never implies permission to execute.
Persisted artifacts contain hashes and resolvable bindings, not raw tool
parameters or raw tool output.

/ 本调度器刻意分离能力发现、能力前沿、候选选择、执行准入、执行授权、持久幂等
与结果分类。语义匹配绝不等于执行权限。持久化制品只包含摘要与可解析绑定，不保存
原始工具参数或原始工具输出。
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Mapping, Protocol, Sequence

from jsonschema import Draft202012Validator, FormatChecker

try:  # Package import / 包导入
    from .reasoning_artifacts import (
        ArtifactValidationError,
        artifact_fingerprint,
        build_artifact,
        validate_tool_dispatch_envelope,
        validate_tool_execution_event,
        validate_tool_execution_result,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import (
        ArtifactValidationError,
        artifact_fingerprint,
        build_artifact,
        validate_tool_dispatch_envelope,
        validate_tool_execution_event,
        validate_tool_execution_result,
    )


TOOL_DISPATCH_SCHEMA_VERSION = "1.0.0"
TOOL_EXECUTION_EVENT_SCHEMA_VERSION = "1.0.0"
TOOL_EXECUTION_RESULT_SCHEMA_VERSION = "1.0.0"
TOOL_DISPATCH_POLICY_ID = "TOOL_DISPATCH_DEFAULT"
TOOL_DISPATCH_POLICY_VERSION = "1.0.0"

ADMISSION_CHECK_ORDER = (
    "registration",
    "frontier",
    "parameters",
    "identity_scope",
    "workflow_stage",
    "dependencies",
    "state_evidence",
    "budget_quota",
    "idempotency",
    "concurrency",
    "approval",
    "risk_environment",
    "compensation",
    "observability",
)

_EXECUTABLE_WORKFLOW_STATES = frozenset(
    {"executable", "executing", "rereading", "retrying", "replanning"}
)


class ToolDispatchError(ValueError):
    """Base tool-dispatch failure / 工具调度基础异常。"""


class ToolDispatchConflictError(ToolDispatchError):
    """An idempotent identity was reused for different content / 幂等身份绑定了不同内容。"""


class DurableStoreRequiredError(ToolDispatchError):
    """A side effect was attempted without a durable store / 副作用动作缺少持久存储。"""


class SideEffectClass(str, Enum):
    """Declared business side-effect class / 声明的业务副作用类别。"""

    READ_ONLY = "read_only"
    DRAFT = "draft"
    REVERSIBLE_WRITE = "reversible_write"
    SENSITIVE_WRITE = "sensitive_write"
    IRREVERSIBLE_EXTERNAL = "irreversible_external"


class ActionRisk(str, Enum):
    """Action risk independent from reasoning depth / 独立于推理深度的行动风险。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ObservationMode(str, Enum):
    """How observability participates in admission / 可观测性参与准入的方式。"""

    SIDECAR = "sidecar"
    ADVISORY = "advisory"
    SOFT_GATE = "soft_gate"
    HARD_GATE = "hard_gate"


class ApprovalState(str, Enum):
    """Approval state bound to concrete action content / 绑定具体行动内容的审批状态。"""

    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class AdmissionDecision(str, Enum):
    """Only normative admission outcomes / 仅允许的规范准入结果。"""

    ALLOW = "allow"
    REJECT = "reject"
    WAIT = "wait"


class ExecutionClassification(str, Enum):
    """Result certainty after the execution boundary / 进入执行边界后的结果确定性。"""

    SUCCESS = "success"
    REUSED_SUCCESS = "reused_success"
    REJECTED = "rejected"
    EXPLICIT_FAILURE = "explicit_failure"
    UNKNOWN = "unknown"
    PARTIAL_SUCCESS = "partial_success"
    WAITING = "waiting"


class SideEffectState(str, Enum):
    """Observed side-effect certainty / 已观测副作用确定性。"""

    NONE = "none"
    CONFIRMED = "confirmed"
    CONFIRMED_ABSENT = "confirmed_absent"
    UNKNOWN = "unknown"
    PARTIAL = "partial"


class LeaseDisposition(str, Enum):
    """Durable idempotency acquisition outcome / 持久幂等租约取得结果。"""

    ACQUIRED = "acquired"
    REUSED_SUCCESS = "reused_success"
    BUSY = "busy"
    VERIFY_UNKNOWN = "verify_unknown"
    RETRY_AUTHORIZATION_REQUIRED = "retry_authorization_required"


_SIDE_EFFECT_RANK = {
    SideEffectClass.READ_ONLY: 0,
    SideEffectClass.DRAFT: 1,
    SideEffectClass.REVERSIBLE_WRITE: 2,
    SideEffectClass.SENSITIVE_WRITE: 3,
    SideEffectClass.IRREVERSIBLE_EXTERNAL: 4,
}

_WRITE_CLASSES = frozenset(
    {
        SideEffectClass.REVERSIBLE_WRITE,
        SideEffectClass.SENSITIVE_WRITE,
        SideEffectClass.IRREVERSIBLE_EXTERNAL,
    }
)

_APPROVAL_REQUIRED_CLASSES = frozenset(
    {SideEffectClass.SENSITIVE_WRITE, SideEffectClass.IRREVERSIBLE_EXTERNAL}
)


def _detached(value: Mapping[str, Any]) -> dict[str, Any]:
    return deepcopy(dict(value))


def _parse_rfc3339(name: str, value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ToolDispatchError(f"{name} must be RFC3339 / {name} 必须是 RFC3339 时间")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ToolDispatchError(
            f"{name} must be RFC3339 / {name} 必须是 RFC3339 时间"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ToolDispatchError(
            f"{name} must include timezone / {name} 必须包含时区"
        )
    return parsed.astimezone(timezone.utc)


def _binding(
    identifier: str,
    version: str,
    content: Mapping[str, Any],
) -> dict[str, str]:
    return {
        "id": identifier,
        "version": version,
        "hash": artifact_fingerprint(content),
    }


def _state(state: str, value: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {"state": state}
    if value is not None:
        record["value"] = _detached(value)
    return record


def _observed_binding(
    value: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    if not isinstance(value, Mapping) or value.get("state") != "observed":
        return None
    nested = value.get("value")
    return nested if isinstance(nested, Mapping) else None


def _binding_state(
    value: Mapping[str, Any] | None,
    *,
    missing_state: str = "missing",
) -> dict[str, Any]:
    if value is None:
        return _state(missing_state)
    if value.get("state") in {"observed", "missing", "unknown", "not_applicable"}:
        return _detached(value)
    return _state("observed", value)


def _parameter_hash(parameters: Mapping[str, Any]) -> str:
    return artifact_fingerprint({"parameters": _detached(parameters)})


def _resource_versions_hash(resource_versions: Mapping[str, str]) -> str:
    return artifact_fingerprint(
        {
            "resource_versions": [
                {"resource_id": resource_id, "version": str(version)}
                for resource_id, version in sorted(resource_versions.items())
            ]
        }
    )


def _idempotency_binding(key: str | None) -> dict[str, Any]:
    if key is None:
        return _state("not_applicable")
    return _state(
        "observed",
        {
            "id": "IDEMPOTENCY_" + artifact_fingerprint({"key": key})[-24:],
            "version": "1.0.0",
            "hash": artifact_fingerprint({"key": key}),
        },
    )


@dataclass(frozen=True)
class ToolCapability:
    """One registered, versioned execution capability / 一个已注册版本化执行能力。"""

    tool_id: str
    tool_version: str
    action_types: tuple[str, ...]
    parameter_schema: Mapping[str, Any]
    required_scopes: frozenset[str]
    allowed_tenants: frozenset[str]
    allowed_stages: frozenset[str]
    side_effect_class: SideEffectClass
    priority: int
    executor_binding: Mapping[str, Any]
    authorization_policy_binding: Mapping[str, Any]
    sandbox_binding: Mapping[str, Any] | None = None
    compensation_binding: Mapping[str, Any] | None = None
    manual_disposition_binding: Mapping[str, Any] | None = None
    allowed_resource_prefixes: tuple[str, ...] = ()
    enabled: bool = True

    def __post_init__(self) -> None:
        for name in ("tool_id", "tool_version"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ToolDispatchError(f"{name} must be non-empty")
        if not self.action_types or len(set(self.action_types)) != len(self.action_types):
            raise ToolDispatchError(
                "action_types must be non-empty and unique / action_types 必须非空且唯一"
            )
        if not isinstance(self.parameter_schema, Mapping):
            raise TypeError("parameter_schema must be a mapping")
        Draft202012Validator.check_schema(dict(self.parameter_schema))
        if isinstance(self.priority, bool) or not isinstance(self.priority, int):
            raise TypeError("priority must be an integer")
        if not isinstance(self.side_effect_class, SideEffectClass):
            raise TypeError("side_effect_class must be SideEffectClass")

    @property
    def manifest(self) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "tool_version": self.tool_version,
            "action_types": list(self.action_types),
            "parameter_schema_hash": artifact_fingerprint(
                {"schema": _detached(self.parameter_schema)}
            ),
            "required_scopes": sorted(self.required_scopes),
            "allowed_tenants": sorted(self.allowed_tenants),
            "allowed_stages": sorted(self.allowed_stages),
            "side_effect_class": self.side_effect_class.value,
            "priority": self.priority,
            "executor_binding": _detached(self.executor_binding),
            "authorization_policy_binding": _detached(
                self.authorization_policy_binding
            ),
            "sandbox_binding": _binding_state(
                self.sandbox_binding,
                missing_state="not_applicable",
            ),
            "compensation_binding": _binding_state(
                self.compensation_binding,
                missing_state="not_applicable",
            ),
            "manual_disposition_binding": _binding_state(
                self.manual_disposition_binding,
                missing_state="not_applicable",
            ),
            "allowed_resource_prefixes": list(self.allowed_resource_prefixes),
            "enabled": self.enabled,
        }

    @property
    def binding(self) -> dict[str, str]:
        return _binding(self.tool_id, self.tool_version, self.manifest)


@dataclass(frozen=True)
class StateEvidence:
    """Versioned pre-execution business observation / 带版本的执行前业务观察。"""

    resource_versions: Mapping[str, str]
    observed_at: str
    evidence_binding: Mapping[str, Any]
    content_hash: str

    def __post_init__(self) -> None:
        if not self.resource_versions:
            raise ToolDispatchError(
                "state evidence requires resource versions / 状态证据必须包含资源版本"
            )
        _parse_rfc3339("observed_at", self.observed_at)

    @property
    def binding(self) -> dict[str, str]:
        content = {
            "resource_versions": [
                {"resource_id": key, "version": str(value)}
                for key, value in sorted(self.resource_versions.items())
            ],
            "observed_at": self.observed_at,
            "evidence_binding": _detached(self.evidence_binding),
            "content_hash": self.content_hash,
        }
        return _binding(
            str(self.evidence_binding.get("id", "STATE_EVIDENCE")),
            str(self.evidence_binding.get("version", "1.0.0")),
            content,
        )


@dataclass(frozen=True)
class ActionApproval:
    """Approval bound to parameters and resource versions / 绑定参数与资源版本的审批。"""

    state: ApprovalState
    approval_binding: Mapping[str, Any] | None
    authority_binding: Mapping[str, Any] | None
    parameter_hash: str | None
    resource_versions_hash: str | None
    expires_at: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.state, ApprovalState):
            raise TypeError("state must be ApprovalState")
        if self.expires_at is not None:
            _parse_rfc3339("approval.expires_at", self.expires_at)

    @property
    def binding_state(self) -> dict[str, Any]:
        if self.state is ApprovalState.NOT_REQUIRED:
            return _state("not_applicable")
        if self.approval_binding is None:
            return _state("missing" if self.state is ApprovalState.PENDING else "unknown")
        return _state("observed", self.approval_binding)


@dataclass(frozen=True)
class ActionIntent:
    """One structured desire to call a capability / 一次结构化能力调用意图。"""

    workflow_id: str
    workflow_version: str
    run_id: str
    goal_id: str
    node_id: str
    attempt_id: str
    action_id: str
    parent_action_id: str | None
    plan_version: str
    correlation_id: str
    action_type: str
    parameters: Mapping[str, Any]
    target_resources: tuple[str, ...]
    expected_side_effect: SideEffectClass
    maximum_side_effect: SideEffectClass
    risk_level: ActionRisk
    idempotency_key: str | None
    state_evidence: StateEvidence | None
    approval: ActionApproval | None

    def __post_init__(self) -> None:
        required = (
            "workflow_id",
            "workflow_version",
            "run_id",
            "goal_id",
            "node_id",
            "attempt_id",
            "action_id",
            "plan_version",
            "correlation_id",
            "action_type",
        )
        for name in required:
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ToolDispatchError(f"{name} must be non-empty")
        if not isinstance(self.parameters, Mapping):
            raise TypeError("parameters must be a mapping")
        if len(set(self.target_resources)) != len(self.target_resources):
            raise ToolDispatchError("target_resources must be unique")
        if _SIDE_EFFECT_RANK[self.expected_side_effect] > _SIDE_EFFECT_RANK[
            self.maximum_side_effect
        ]:
            raise ToolDispatchError(
                "expected side effect exceeds contract maximum / 期望副作用超出契约上限"
            )
        if self.expected_side_effect in _WRITE_CLASSES and not self.target_resources:
            raise ToolDispatchError(
                "write action requires target resources / 写动作必须声明目标资源"
            )

    @property
    def parameter_hash(self) -> str:
        return _parameter_hash(self.parameters)

    @property
    def business_action_hash(self) -> str:
        """Stable logical-action hash shared by retries / 跨重试稳定的逻辑行动哈希。"""

        return artifact_fingerprint(
            {
                "workflow_id": self.workflow_id,
                "workflow_version": self.workflow_version,
                "goal_id": self.goal_id,
                "action_type": self.action_type,
                "parameter_hash": self.parameter_hash,
                "target_resources": sorted(self.target_resources),
                "expected_side_effect": self.expected_side_effect.value,
                "maximum_side_effect": self.maximum_side_effect.value,
                "risk_level": self.risk_level.value,
            }
        )

    @property
    def intent_content(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_version": self.workflow_version,
            "run_id": self.run_id,
            "goal_id": self.goal_id,
            "node_id": self.node_id,
            "attempt_id": self.attempt_id,
            "action_id": self.action_id,
            "parent_action_id": self.parent_action_id,
            "plan_version": self.plan_version,
            "correlation_id": self.correlation_id,
            "action_type": self.action_type,
            "parameter_hash": self.parameter_hash,
            "target_resources": sorted(self.target_resources),
            "expected_side_effect": self.expected_side_effect.value,
            "maximum_side_effect": self.maximum_side_effect.value,
            "risk_level": self.risk_level.value,
            "business_action_hash": self.business_action_hash,
            "idempotency_binding": _idempotency_binding(self.idempotency_key),
            "state_evidence_binding": (
                _state("not_applicable")
                if self.state_evidence is None
                else _state("observed", self.state_evidence.binding)
            ),
            "approval_binding": (
                _state("not_applicable")
                if self.approval is None
                else self.approval.binding_state
            ),
        }

    @property
    def binding(self) -> dict[str, str]:
        return _binding(self.action_id, "1.0.0", self.intent_content)


@dataclass(frozen=True)
class DispatchContext:
    """Live mechanical and governance state / 实时机械与治理状态。"""

    actor_binding: Mapping[str, Any]
    actor_scopes: frozenset[str]
    tenant_id: str
    workflow_state: str
    stage: str
    dependencies_satisfied: bool
    budget_available: bool
    concurrency_clear: bool
    current_resource_versions: Mapping[str, str]
    action_authorization_binding: Mapping[str, Any] | None
    observation_mode: ObservationMode
    critical_observability_ready: bool
    durable_idempotency_available: bool
    retry_authorized: bool
    created_at: str
    permit_expires_at: str

    def __post_init__(self) -> None:
        if not isinstance(self.observation_mode, ObservationMode):
            raise TypeError("observation_mode must be ObservationMode")
        if not self.tenant_id or not self.workflow_state or not self.stage:
            raise ToolDispatchError(
                "tenant, workflow state, and stage are required / 租户、工作流状态与阶段必填"
            )
        created = _parse_rfc3339("created_at", self.created_at)
        expires = _parse_rfc3339("permit_expires_at", self.permit_expires_at)
        if expires <= created:
            raise ToolDispatchError(
                "permit expiry must follow creation / 许可过期时间必须晚于创建时间"
            )


@dataclass(frozen=True)
class ToolDispatchRequest:
    """Frozen input to one dispatch decision / 一次调度决定的冻结输入。"""

    intent: ActionIntent
    context: DispatchContext


@dataclass(frozen=True)
class ToolDispatchPolicy:
    """Versioned deterministic frontier and admission policy / 版本化确定性前沿与准入策略。"""

    policy_id: str = TOOL_DISPATCH_POLICY_ID
    policy_version: str = TOOL_DISPATCH_POLICY_VERSION
    max_frontier_size: int = 16

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_frontier_size, bool)
            or not isinstance(self.max_frontier_size, int)
            or self.max_frontier_size < 1
        ):
            raise ToolDispatchError("max_frontier_size must be positive")

    @property
    def binding(self) -> dict[str, str]:
        content = {
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "max_frontier_size": self.max_frontier_size,
            "admission_check_order": list(ADMISSION_CHECK_ORDER),
            "executable_workflow_states": sorted(_EXECUTABLE_WORKFLOW_STATES),
            "write_classes": sorted(item.value for item in _WRITE_CLASSES),
            "approval_required_classes": sorted(
                item.value for item in _APPROVAL_REQUIRED_CLASSES
            ),
        }
        return _binding(self.policy_id, self.policy_version, content)


@dataclass(frozen=True)
class AdmissionCheck:
    """One explicit admission check / 一项显式准入检查。"""

    name: str
    status: str
    code: str
    evidence_bindings: tuple[Mapping[str, Any], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "code": self.code,
            "evidence_bindings": [_detached(item) for item in self.evidence_bindings],
        }


@dataclass(frozen=True)
class ToolExecutionReceipt:
    """Normalized executor response with no raw output / 不含原始输出的规范执行回执。"""

    classification: ExecutionClassification
    side_effect_state: SideEffectState
    output_binding: Mapping[str, Any] | None = None
    external_receipt_binding: Mapping[str, Any] | None = None
    actual_side_effects: tuple[Mapping[str, Any], ...] = ()
    error_category: str | None = None
    error_code: str | None = None
    retryable: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.classification, ExecutionClassification):
            raise TypeError("classification must be ExecutionClassification")
        if not isinstance(self.side_effect_state, SideEffectState):
            raise TypeError("side_effect_state must be SideEffectState")
        if self.classification is ExecutionClassification.SUCCESS and self.error_code:
            raise ToolDispatchError("successful receipt cannot carry an error")


@dataclass(frozen=True)
class LeaseAcquisition:
    """Lease result returned by a durable store / 持久存储返回的租约结果。"""

    disposition: LeaseDisposition
    lease_token: str | None
    lease_binding: Mapping[str, Any] | None
    prior_result: Mapping[str, Any] | None = None
    reason_code: str | None = None


class ToolDispatchStore(Protocol):
    """Persistence required by the execution boundary / 执行边界所需持久化接口。"""

    durable: bool

    def append_event(self, event_draft: Mapping[str, Any]) -> Mapping[str, Any]:
        ...

    def acquire(
        self,
        *,
        idempotency_key: str,
        intent_hash: str,
        action_id: str,
        attempt_id: str,
        acquired_at: str,
        lease_seconds: int,
        retry_authorized: bool,
    ) -> LeaseAcquisition:
        ...

    def complete(
        self,
        *,
        idempotency_key: str,
        lease_token: str,
        result: Mapping[str, Any],
        completed_at: str,
    ) -> None:
        ...


class InMemoryToolEventStore:
    """Non-durable event collector for read-only reference use only.

    / 仅用于只读参考场景的非持久事件采集器。
    """

    durable = False

    def __init__(self) -> None:
        self._events: dict[str, list[dict[str, Any]]] = {}
        self._by_key: dict[tuple[str, str], dict[str, Any]] = {}

    def append_event(self, event_draft: Mapping[str, Any]) -> Mapping[str, Any]:
        draft = _detached(event_draft)
        run_id = str(draft["run_id"])
        event_key = str(draft["event_key"])
        key = (run_id, event_key)
        existing = self._by_key.get(key)
        if existing is not None:
            comparable = dict(existing)
            for field_name in ("event_id", "sequence", "event_hash"):
                comparable.pop(field_name, None)
            if comparable != draft:
                raise ToolDispatchConflictError(
                    "event key reused with different content / 事件键复用于不同内容"
                )
            return deepcopy(existing)
        sequence = len(self._events.setdefault(run_id, [])) + 1
        event = seal_tool_execution_event(draft, sequence=sequence)
        self._events[run_id].append(event)
        self._by_key[key] = event
        return deepcopy(event)

    def acquire(self, **_: Any) -> LeaseAcquisition:
        raise DurableStoreRequiredError(
            "side effects require a durable idempotency store / 副作用需要持久幂等存储"
        )

    def complete(self, **_: Any) -> None:
        raise DurableStoreRequiredError(
            "side effects require a durable idempotency store / 副作用需要持久幂等存储"
        )

    def events(self, run_id: str) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._events.get(run_id, [])))


AuthorityVerifier = Callable[[ToolDispatchRequest, ToolCapability], bool]
ToolExecutor = Callable[
    [Mapping[str, Any], Mapping[str, Any], Mapping[str, Any], str | None],
    ToolExecutionReceipt,
]


class ToolDispatchCoordinator:
    """Build a minimal frontier and one sealed admission decision.

    / 构建最小能力前沿并生成一个封存准入决定。
    """

    def __init__(
        self,
        capabilities: Sequence[ToolCapability],
        *,
        policy: ToolDispatchPolicy | None = None,
        authority_verifier: AuthorityVerifier | None = None,
    ) -> None:
        if not capabilities:
            raise ToolDispatchError(
                "capability catalog cannot be empty / 能力目录不能为空"
            )
        self.policy = policy or ToolDispatchPolicy()
        self.authority_verifier = authority_verifier
        indexed: dict[tuple[str, str], ToolCapability] = {}
        for capability in capabilities:
            key = (capability.tool_id, capability.tool_version)
            if key in indexed:
                raise ToolDispatchError(
                    f"duplicate tool capability {key} / 重复工具能力 {key}"
                )
            indexed[key] = capability
        self._capabilities = tuple(
            sorted(indexed.values(), key=lambda item: (item.tool_id, item.tool_version))
        )

    @property
    def catalog_binding(self) -> dict[str, str]:
        content = {
            "capabilities": [item.binding for item in self._capabilities],
            "policy_binding": self.policy.binding,
        }
        return _binding("TOOL_CAPABILITY_CATALOG", "1.0.0", content)

    def prepare(self, request: ToolDispatchRequest) -> dict[str, Any]:
        """Return a sealed dispatch envelope without invoking a tool.

        / 返回封存调度信封，不调用真实工具。
        """

        retained, exclusion_counts = self._frontier(request)
        candidates = [
            capability
            for capability in retained
            if request.intent.action_type in capability.action_types
        ]
        candidates.sort(key=lambda item: (-item.priority, item.tool_id, item.tool_version))
        selected = candidates[0] if candidates else None
        checks = self._admission_checks(request, selected, retained)
        decision = self._decision(checks)
        reason_codes = [
            check.code
            for check in checks
            if check.status in {"failed", "waiting"}
        ]
        frontier_content = {
            "policy_binding": self.policy.binding,
            "retained_tool_bindings": [item.binding for item in retained],
            "exclusion_counts": exclusion_counts,
        }
        frontier_id = "TOOL_FRONTIER_" + artifact_fingerprint(frontier_content)[-24:]
        frontier = {
            "frontier_id": frontier_id,
            "frontier_version": "1.0.0",
            **frontier_content,
            "frontier_hash": artifact_fingerprint(frontier_content),
        }
        candidate_records = [
            {
                "tool_binding": candidate.binding,
                "priority": candidate.priority,
                "action_type_match": True,
                "selected": selected is candidate,
            }
            for candidate in candidates
        ]
        selected_binding = (
            _state("missing")
            if selected is None
            else _state("observed", selected.binding)
        )
        execution_contract = self._execution_contract(request, selected, decision)
        dispatch_identity = {
            "intent_binding": request.intent.binding,
            "actor_binding": _detached(request.context.actor_binding),
            "catalog_binding": self.catalog_binding,
            "frontier_hash": frontier["frontier_hash"],
            "candidate_bindings": [item["tool_binding"] for item in candidate_records],
            "admission_checks": [check.as_dict() for check in checks],
            "created_at": request.context.created_at,
        }
        dispatch_id = (
            "TOOL_DISPATCH_"
            + artifact_fingerprint(dispatch_identity).removeprefix("sha256:")[:24]
        )
        permit_binding = _state("not_applicable")
        if decision is AdmissionDecision.ALLOW and selected is not None:
            permit_content = {
                "dispatch_id": dispatch_id,
                "intent_binding": request.intent.binding,
                "tool_binding": selected.binding,
                "actor_binding": _detached(request.context.actor_binding),
                "authorization_binding": _binding_state(
                    request.context.action_authorization_binding
                ),
                "approval_binding": execution_contract["approval_binding"],
                "state_evidence_binding": execution_contract[
                    "state_evidence_binding"
                ],
                "idempotency_binding": execution_contract["idempotency_binding"],
                "permit_expires_at": execution_contract["permit_expires_at"],
            }
            permit_binding = _state(
                "observed",
                _binding(dispatch_id + "_PERMIT", "1.0.0", permit_content),
            )
        envelope = {
            "schema_version": TOOL_DISPATCH_SCHEMA_VERSION,
            "dispatch_id": dispatch_id,
            "decision_revision": 1,
            "workflow_id": request.intent.workflow_id,
            "workflow_version": request.intent.workflow_version,
            "run_id": request.intent.run_id,
            "goal_id": request.intent.goal_id,
            "node_id": request.intent.node_id,
            "attempt_id": request.intent.attempt_id,
            "action_id": request.intent.action_id,
            "parent_action_id": request.intent.parent_action_id,
            "plan_version": request.intent.plan_version,
            "correlation_id": request.intent.correlation_id,
            "intent_binding": request.intent.binding,
            "actor_binding": _detached(request.context.actor_binding),
            "parameter_hash": request.intent.parameter_hash,
            "target_resources": sorted(request.intent.target_resources),
            "catalog_binding": self.catalog_binding,
            "frontier": frontier,
            "candidate_evaluations": candidate_records,
            "selected_tool_binding": selected_binding,
            "admission_checks": [check.as_dict() for check in checks],
            "decision": decision.value,
            "reason_codes": reason_codes,
            "execution_contract": execution_contract,
            "permit_binding": permit_binding,
            "created_at": request.context.created_at,
        }
        return build_artifact("tool_dispatch_envelope", envelope)

    def _frontier(
        self,
        request: ToolDispatchRequest,
    ) -> tuple[list[ToolCapability], dict[str, int]]:
        retained: list[ToolCapability] = []
        counts = {
            "disabled": 0,
            "tenant": 0,
            "permission": 0,
            "stage": 0,
            "side_effect": 0,
            "resource_scope": 0,
            "frontier_limit": 0,
        }
        for capability in self._capabilities:
            reason: str | None = None
            if not capability.enabled:
                reason = "disabled"
            elif capability.allowed_tenants and (
                request.context.tenant_id not in capability.allowed_tenants
            ):
                reason = "tenant"
            elif not capability.required_scopes.issubset(request.context.actor_scopes):
                reason = "permission"
            elif capability.allowed_stages and (
                request.context.stage not in capability.allowed_stages
            ):
                reason = "stage"
            elif _SIDE_EFFECT_RANK[capability.side_effect_class] > _SIDE_EFFECT_RANK[
                request.intent.maximum_side_effect
            ]:
                reason = "side_effect"
            elif capability.allowed_resource_prefixes and any(
                not any(
                    resource.startswith(prefix)
                    for prefix in capability.allowed_resource_prefixes
                )
                for resource in request.intent.target_resources
            ):
                reason = "resource_scope"
            if reason is not None:
                counts[reason] += 1
                continue
            retained.append(capability)
        retained.sort(key=lambda item: (-item.priority, item.tool_id, item.tool_version))
        if len(retained) > self.policy.max_frontier_size:
            counts["frontier_limit"] = len(retained) - self.policy.max_frontier_size
            retained = retained[: self.policy.max_frontier_size]
        return retained, counts

    def _admission_checks(
        self,
        request: ToolDispatchRequest,
        selected: ToolCapability | None,
        retained: Sequence[ToolCapability],
    ) -> list[AdmissionCheck]:
        checks: dict[str, AdmissionCheck] = {}

        def add(
            name: str,
            status: str,
            code: str,
            *evidence_bindings: Mapping[str, Any],
        ) -> None:
            checks[name] = AdmissionCheck(
                name,
                status,
                code,
                tuple(_detached(item) for item in evidence_bindings),
            )

        if selected is None:
            add("registration", "failed", "NO_REGISTERED_CAPABILITY")
            add("frontier", "failed", "NO_FRONTIER_CANDIDATE")
            for name in ADMISSION_CHECK_ORDER[2:]:
                add(name, "not_applicable", "NO_SELECTED_TOOL")
            return [checks[name] for name in ADMISSION_CHECK_ORDER]

        add("registration", "passed", "REGISTERED", selected.binding)
        if selected in retained:
            add("frontier", "passed", "IN_FRONTIER", selected.binding)
        else:
            add("frontier", "failed", "OUTSIDE_FRONTIER", selected.binding)

        validator = Draft202012Validator(
            dict(selected.parameter_schema),
            format_checker=FormatChecker(),
        )
        parameter_errors = sorted(
            validator.iter_errors(dict(request.intent.parameters)),
            key=lambda item: list(item.absolute_path),
        )
        if parameter_errors:
            paths = [
                "/" + "/".join(str(part) for part in error.absolute_path)
                for error in parameter_errors
            ]
            add(
                "parameters",
                "failed",
                "PARAMETER_SCHEMA_REJECTED:" + ",".join(paths),
            )
        else:
            add("parameters", "passed", "PARAMETERS_VALID")

        authority_binding = _binding_state(
            request.context.action_authorization_binding
        )
        authority = _observed_binding(authority_binding)
        live_authorized = False
        if authority is not None and self.authority_verifier is not None:
            try:
                live_authorized = (
                    self.authority_verifier(request, selected) is True
                )
            except Exception:
                live_authorized = False
        if not selected.required_scopes.issubset(request.context.actor_scopes):
            add("identity_scope", "failed", "SCOPE_DENIED")
        elif authority is None:
            add("identity_scope", "failed", "AUTHORIZATION_BINDING_MISSING")
        elif not live_authorized:
            add(
                "identity_scope",
                "failed",
                "LIVE_AUTHORIZATION_DENIED",
                authority,
            )
        else:
            add(
                "identity_scope",
                "passed",
                "IDENTITY_SCOPE_AUTHORIZED",
                authority,
            )

        if request.context.workflow_state in _EXECUTABLE_WORKFLOW_STATES:
            add("workflow_stage", "passed", "WORKFLOW_STAGE_EXECUTABLE")
        else:
            add("workflow_stage", "failed", "WORKFLOW_STAGE_BLOCKED")

        if request.context.dependencies_satisfied:
            add("dependencies", "passed", "DEPENDENCIES_SATISFIED")
        else:
            add("dependencies", "waiting", "DEPENDENCIES_PENDING")

        is_write = selected.side_effect_class in _WRITE_CLASSES
        evidence = request.intent.state_evidence
        if not is_write:
            add("state_evidence", "not_applicable", "READ_ONLY_OR_DRAFT")
        elif evidence is None:
            add("state_evidence", "waiting", "STATE_EVIDENCE_MISSING")
        else:
            evidence_versions = {
                key: str(value) for key, value in evidence.resource_versions.items()
            }
            current_versions = {
                key: str(value)
                for key, value in request.context.current_resource_versions.items()
            }
            targets = set(request.intent.target_resources)
            if set(evidence_versions) != targets:
                add(
                    "state_evidence",
                    "failed",
                    "STATE_EVIDENCE_SCOPE_MISMATCH",
                    evidence.binding,
                )
            elif not targets.issubset(set(current_versions)):
                add(
                    "state_evidence",
                    "waiting",
                    "CURRENT_STATE_VERSION_INVENTORY_INCOMPLETE",
                    evidence.binding,
                )
            elif any(
                current_versions.get(resource) != evidence_versions.get(resource)
                for resource in targets
            ):
                add(
                    "state_evidence",
                    "waiting",
                    "STATE_VERSION_CONFLICT",
                    evidence.binding,
                )
            else:
                add(
                    "state_evidence",
                    "passed",
                    "STATE_EVIDENCE_CURRENT",
                    evidence.binding,
                )

        if request.context.budget_available:
            add("budget_quota", "passed", "BUDGET_AVAILABLE")
        else:
            add("budget_quota", "failed", "BUDGET_EXHAUSTED")

        if not is_write:
            add("idempotency", "not_applicable", "READ_ONLY_OR_DRAFT")
        elif not request.intent.idempotency_key:
            add("idempotency", "failed", "IDEMPOTENCY_KEY_MISSING")
        elif not request.context.durable_idempotency_available:
            add("idempotency", "waiting", "DURABLE_IDEMPOTENCY_UNAVAILABLE")
        else:
            idempotency = _observed_binding(
                _idempotency_binding(request.intent.idempotency_key)
            )
            add(
                "idempotency",
                "passed",
                "IDEMPOTENCY_READY",
                *(() if idempotency is None else (idempotency,)),
            )

        if request.context.concurrency_clear:
            add("concurrency", "passed", "CONCURRENCY_CLEAR")
        else:
            add("concurrency", "waiting", "RESOURCE_CONFLICT")

        approval = request.intent.approval
        if selected.side_effect_class not in _APPROVAL_REQUIRED_CLASSES:
            add("approval", "not_applicable", "APPROVAL_NOT_REQUIRED")
        elif approval is None or approval.state is ApprovalState.PENDING:
            add("approval", "waiting", "APPROVAL_PENDING")
        elif approval.state is ApprovalState.DENIED:
            add("approval", "failed", "APPROVAL_DENIED")
        elif approval.state is not ApprovalState.APPROVED:
            add("approval", "failed", "APPROVAL_INVALID")
        else:
            expected_versions_hash = _resource_versions_hash(
                {}
                if evidence is None
                else {
                    key: str(value)
                    for key, value in evidence.resource_versions.items()
                }
            )
            expired = (
                approval.expires_at is None
                or _parse_rfc3339("approval.expires_at", approval.expires_at)
                <= _parse_rfc3339("created_at", request.context.created_at)
            )
            binding = approval.approval_binding
            authority_value = approval.authority_binding
            if binding is None or authority_value is None:
                add("approval", "failed", "APPROVAL_BINDING_MISSING")
            elif expired:
                add("approval", "waiting", "APPROVAL_EXPIRED", binding)
            elif approval.parameter_hash != request.intent.parameter_hash:
                add("approval", "failed", "APPROVAL_PARAMETER_DRIFT", binding)
            elif approval.resource_versions_hash != expected_versions_hash:
                add("approval", "waiting", "APPROVAL_RESOURCE_VERSION_DRIFT", binding)
            else:
                add(
                    "approval",
                    "passed",
                    "APPROVAL_BOUND_AND_VALID",
                    binding,
                    authority_value,
                )

        if selected.side_effect_class is not request.intent.expected_side_effect:
            add("risk_environment", "failed", "SIDE_EFFECT_CLASS_MISMATCH")
        elif is_write and _observed_binding(
            _binding_state(selected.sandbox_binding, missing_state="missing")
        ) is None:
            add("risk_environment", "failed", "SANDBOX_BINDING_MISSING")
        else:
            evidence_bindings = [selected.executor_binding]
            if selected.sandbox_binding is not None:
                evidence_bindings.append(selected.sandbox_binding)
            add(
                "risk_environment",
                "passed",
                "RISK_ENVIRONMENT_SATISFIED",
                *evidence_bindings,
            )

        if selected.side_effect_class in {
            SideEffectClass.READ_ONLY,
            SideEffectClass.DRAFT,
        }:
            add("compensation", "not_applicable", "NO_BUSINESS_WRITE")
        elif selected.side_effect_class is SideEffectClass.REVERSIBLE_WRITE:
            if selected.compensation_binding is None:
                add("compensation", "failed", "COMPENSATION_BINDING_MISSING")
            else:
                add(
                    "compensation",
                    "passed",
                    "COMPENSATION_AVAILABLE",
                    selected.compensation_binding,
                )
        elif (
            selected.compensation_binding is None
            and selected.manual_disposition_binding is None
        ):
            add("compensation", "failed", "DISPOSITION_PATH_MISSING")
        else:
            evidence_bindings = [
                item
                for item in (
                    selected.compensation_binding,
                    selected.manual_disposition_binding,
                )
                if item is not None
            ]
            add(
                "compensation",
                "passed",
                "DISPOSITION_PATH_AVAILABLE",
                *evidence_bindings,
            )

        if (
            request.context.observation_mode is ObservationMode.HARD_GATE
            and is_write
            and not request.context.critical_observability_ready
        ):
            add("observability", "waiting", "CRITICAL_OBSERVABILITY_NOT_READY")
        elif (
            request.context.observation_mode is ObservationMode.SOFT_GATE
            and is_write
            and not request.context.critical_observability_ready
        ):
            add("observability", "passed", "OBSERVABILITY_SOFT_WARNING")
        else:
            add("observability", "passed", "OBSERVABILITY_POLICY_SATISFIED")

        return [checks[name] for name in ADMISSION_CHECK_ORDER]

    @staticmethod
    def _decision(checks: Sequence[AdmissionCheck]) -> AdmissionDecision:
        if any(check.status == "failed" for check in checks):
            return AdmissionDecision.REJECT
        if any(check.status == "waiting" for check in checks):
            return AdmissionDecision.WAIT
        return AdmissionDecision.ALLOW

    @staticmethod
    def _execution_contract(
        request: ToolDispatchRequest,
        selected: ToolCapability | None,
        decision: AdmissionDecision,
    ) -> dict[str, Any]:
        side_effect = (
            request.intent.expected_side_effect
            if selected is None
            else selected.side_effect_class
        )
        lease_required = side_effect in _WRITE_CLASSES
        evidence_binding = (
            _state("not_applicable")
            if request.intent.state_evidence is None
            else _state("observed", request.intent.state_evidence.binding)
        )
        approval_binding = (
            _state("not_applicable")
            if request.intent.approval is None
            else request.intent.approval.binding_state
        )
        permit_expires_at = request.context.permit_expires_at
        approval = request.intent.approval
        if (
            approval is not None
            and approval.state is ApprovalState.APPROVED
            and approval.expires_at is not None
            and _parse_rfc3339(
                "approval.expires_at",
                approval.expires_at,
            )
            < _parse_rfc3339(
                "permit_expires_at",
                permit_expires_at,
            )
        ):
            permit_expires_at = approval.expires_at
        return {
            "side_effect_class": side_effect.value,
            "risk_level": request.intent.risk_level.value,
            "lease_required": lease_required,
            "idempotency_binding": _idempotency_binding(
                request.intent.idempotency_key
            ),
            "state_evidence_binding": evidence_binding,
            "resource_versions_hash": (
                _resource_versions_hash({})
                if request.intent.state_evidence is None
                else _resource_versions_hash(
                    {
                        key: str(value)
                        for key, value in request.intent.state_evidence.resource_versions.items()
                    }
                )
            ),
            "approval_binding": approval_binding,
            "authorization_binding": _binding_state(
                request.context.action_authorization_binding
            ),
            "authorization_policy_binding": (
                _state("missing")
                if selected is None
                else _state("observed", selected.authorization_policy_binding)
            ),
            "executor_binding": (
                _state("missing")
                if selected is None
                else _state("observed", selected.executor_binding)
            ),
            "sandbox_binding": (
                _state("not_applicable")
                if selected is None or selected.sandbox_binding is None
                else _state("observed", selected.sandbox_binding)
            ),
            "compensation_binding": (
                _state("not_applicable")
                if selected is None or selected.compensation_binding is None
                else _state("observed", selected.compensation_binding)
            ),
            "manual_disposition_binding": (
                _state("not_applicable")
                if selected is None or selected.manual_disposition_binding is None
                else _state("observed", selected.manual_disposition_binding)
            ),
            "observation_mode": request.context.observation_mode.value,
            "permit_expires_at": permit_expires_at,
            "execution_ready": decision is AdmissionDecision.ALLOW,
        }


def seal_tool_execution_event(
    event_draft: Mapping[str, Any],
    *,
    sequence: int,
) -> dict[str, Any]:
    """Assign per-run sequence and seal one event / 分配单运行序号并封存事件。"""

    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        raise ToolDispatchError("event sequence must be positive")
    event = _detached(event_draft)
    identity = {
        "run_id": event["run_id"],
        "event_key": event["event_key"],
    }
    event["event_id"] = (
        "TOOL_EVENT_"
        + artifact_fingerprint(identity).removeprefix("sha256:")[:24]
    )
    event["sequence"] = sequence
    return build_artifact("tool_execution_event", event)


def _event_draft(
    request: ToolDispatchRequest,
    envelope: Mapping[str, Any],
    *,
    event_key_suffix: str,
    event_type: str,
    stage: str,
    status: str,
    occurred_at: str,
    decision: str | None = None,
    result_classification: str | None = None,
    lease_binding: Mapping[str, Any] | None = None,
    result_binding: Mapping[str, Any] | None = None,
    reason_codes: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "schema_version": TOOL_EXECUTION_EVENT_SCHEMA_VERSION,
        "event_version": "1.0.0",
        "event_key": f"{request.intent.action_id}:{event_key_suffix}",
        "event_type": event_type,
        "event_processing_status": "accepted",
        "workflow_id": request.intent.workflow_id,
        "workflow_version": request.intent.workflow_version,
        "run_id": request.intent.run_id,
        "goal_id": request.intent.goal_id,
        "node_id": request.intent.node_id,
        "attempt_id": request.intent.attempt_id,
        "action_id": request.intent.action_id,
        "parent_action_id": request.intent.parent_action_id,
        "plan_version": request.intent.plan_version,
        "correlation_id": request.intent.correlation_id,
        "stage": stage,
        "status": status,
        "decision": decision,
        "reason_codes": list(reason_codes),
        "dispatch_binding": _state(
            "observed",
            {
                "id": envelope["dispatch_id"],
                "version": envelope["schema_version"],
                "hash": envelope["dispatch_hash"],
            },
        ),
        "frontier_binding": _state(
            "observed",
            {
                "id": envelope["frontier"]["frontier_id"],
                "version": envelope["frontier"]["frontier_version"],
                "hash": envelope["frontier"]["frontier_hash"],
            },
        ),
        "tool_binding": _detached(envelope["selected_tool_binding"]),
        "permit_binding": _detached(envelope["permit_binding"]),
        "idempotency_binding": _detached(
            envelope["execution_contract"]["idempotency_binding"]
        ),
        "lease_binding": _binding_state(
            lease_binding,
            missing_state="not_applicable",
        ),
        "result_binding": _binding_state(
            result_binding,
            missing_state="not_applicable",
        ),
        "side_effect_class": envelope["execution_contract"]["side_effect_class"],
        "result_classification": result_classification,
        "admission_checks": deepcopy(envelope["admission_checks"]),
        "occurred_at": occurred_at,
        "data_semantics": "original",
    }


@dataclass(frozen=True)
class ToolDispatchRun:
    """Complete dispatcher handoff / 完整调度器交接结果。"""

    envelope: Mapping[str, Any]
    result: Mapping[str, Any]
    events: tuple[Mapping[str, Any], ...]
    executor_called: bool


class ToolDispatchRuntime:
    """Guard the real execution boundary and classify its outcome.

    / 守护真实执行边界并分类执行结果。
    """

    def __init__(
        self,
        coordinator: ToolDispatchCoordinator,
        *,
        store: ToolDispatchStore | None = None,
        clock: Callable[[], datetime] | None = None,
        lease_seconds: int = 60,
    ) -> None:
        if (
            isinstance(lease_seconds, bool)
            or not isinstance(lease_seconds, int)
            or lease_seconds < 1
        ):
            raise ToolDispatchError("lease_seconds must be positive")
        self.coordinator = coordinator
        self.store = store or InMemoryToolEventStore()
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.lease_seconds = lease_seconds

    def execute(
        self,
        request: ToolDispatchRequest,
        executor: ToolExecutor,
    ) -> ToolDispatchRun:
        """Prepare, admit, lease, execute, and classify one action.

        / 准备、准入、取租约、执行并分类一个行动。
        """

        envelope = self.coordinator.prepare(request)
        validate_tool_dispatch_envelope(envelope)
        events: list[Mapping[str, Any]] = []
        now = self._now()
        for suffix, event_type, stage in (
            ("frontier", "capability_frontier_built", "capability_frontier"),
            ("candidate", "candidate_selection_completed", "candidate_selection"),
            ("admission", "execution_admission_completed", "execution_admission"),
        ):
            events.append(
                self.store.append_event(
                    _event_draft(
                        request,
                        envelope,
                        event_key_suffix=suffix,
                        event_type=event_type,
                        stage=stage,
                        status="completed",
                        occurred_at=now,
                        decision=(
                            envelope["decision"]
                            if stage == "execution_admission"
                            else None
                        ),
                        reason_codes=envelope["reason_codes"],
                    )
                )
            )

        if envelope["decision"] != AdmissionDecision.ALLOW.value:
            classification = (
                ExecutionClassification.REJECTED
                if envelope["decision"] == AdmissionDecision.REJECT.value
                else ExecutionClassification.WAITING
            )
            result = self._build_nonexecuted_result(
                request,
                envelope,
                classification=classification,
                reason_codes=envelope["reason_codes"],
                created_at=now,
            )
            events.append(self._record_result_event(request, envelope, result, now))
            return ToolDispatchRun(envelope, result, tuple(events), False)

        selected = self._selected_capability(envelope)
        if not self._live_authorized(request, selected):
            result = self._build_nonexecuted_result(
                request,
                envelope,
                classification=ExecutionClassification.REJECTED,
                reason_codes=("LIVE_AUTHORIZATION_REVOKED",),
                created_at=now,
            )
            events.append(self._record_result_event(request, envelope, result, now))
            return ToolDispatchRun(envelope, result, tuple(events), False)

        if _parse_rfc3339("now", now) >= _parse_rfc3339(
            "permit_expires_at",
            envelope["execution_contract"]["permit_expires_at"],
        ):
            result = self._build_nonexecuted_result(
                request,
                envelope,
                classification=ExecutionClassification.REJECTED,
                reason_codes=("EXECUTION_PERMIT_EXPIRED",),
                created_at=now,
            )
            events.append(self._record_result_event(request, envelope, result, now))
            return ToolDispatchRun(envelope, result, tuple(events), False)

        is_write = selected.side_effect_class in _WRITE_CLASSES
        lease: LeaseAcquisition | None = None
        if is_write:
            if not getattr(self.store, "durable", False):
                result = self._build_nonexecuted_result(
                    request,
                    envelope,
                    classification=ExecutionClassification.REJECTED,
                    reason_codes=("DURABLE_STORE_REQUIRED",),
                    created_at=now,
                )
                events.append(self._record_result_event(request, envelope, result, now))
                return ToolDispatchRun(envelope, result, tuple(events), False)
            if request.intent.idempotency_key is None:
                raise ArtifactValidationError(
                    ["allowed write lacks idempotency key / 已放行写动作缺少幂等键"]
                )
            lease = self.store.acquire(
                idempotency_key=request.intent.idempotency_key,
                intent_hash=request.intent.business_action_hash,
                action_id=request.intent.action_id,
                attempt_id=request.intent.attempt_id,
                acquired_at=now,
                lease_seconds=self.lease_seconds,
                retry_authorized=request.context.retry_authorized,
            )
            if lease.disposition is not LeaseDisposition.ACQUIRED:
                result = self._result_for_existing_lease(
                    request,
                    envelope,
                    lease,
                    created_at=now,
                )
                events.append(self._record_result_event(request, envelope, result, now))
                return ToolDispatchRun(envelope, result, tuple(events), False)
            events.append(
                self.store.append_event(
                    _event_draft(
                        request,
                        envelope,
                        event_key_suffix=f"lease:{request.intent.attempt_id}",
                        event_type="execution_lease_acquired",
                        stage="idempotency_lease",
                        status="completed",
                        occurred_at=now,
                        decision="allow",
                        lease_binding=lease.lease_binding,
                    )
                )
            )

        events.append(
            self.store.append_event(
                _event_draft(
                    request,
                    envelope,
                    event_key_suffix=f"execution-start:{request.intent.attempt_id}",
                    event_type="tool_execution_started",
                    stage="tool_execution",
                    status="started",
                    occurred_at=now,
                    decision="allow",
                    lease_binding=None if lease is None else lease.lease_binding,
                )
            )
        )

        try:
            receipt = executor(
                selected.binding,
                deepcopy(dict(request.intent.parameters)),
                deepcopy(envelope["permit_binding"]["value"]),
                request.intent.idempotency_key,
            )
            if not isinstance(receipt, ToolExecutionReceipt):
                raise TypeError("executor must return ToolExecutionReceipt")
        except Exception as exc:
            receipt = ToolExecutionReceipt(
                classification=(
                    ExecutionClassification.UNKNOWN
                    if is_write
                    else ExecutionClassification.EXPLICIT_FAILURE
                ),
                side_effect_state=(
                    SideEffectState.UNKNOWN
                    if is_write
                    else SideEffectState.NONE
                ),
                error_category="executor_exception",
                error_code=type(exc).__name__,
                retryable=not is_write,
            )
        normalized = self._normalize_receipt(selected, receipt)
        completed_at = self._now()
        result = self._build_executed_result(
            request,
            envelope,
            normalized,
            lease=lease,
            started_at=now,
            completed_at=completed_at,
        )
        if is_write:
            assert request.intent.idempotency_key is not None
            assert lease is not None and lease.lease_token is not None
            self.store.complete(
                idempotency_key=request.intent.idempotency_key,
                lease_token=lease.lease_token,
                result=result,
                completed_at=completed_at,
            )
        events.append(
            self._record_result_event(request, envelope, result, completed_at)
        )
        if (
            result["side_effect_state"] == SideEffectState.CONFIRMED.value
            and result["actual_side_effects"]
        ):
            events.append(
                self.store.append_event(
                    _event_draft(
                        request,
                        envelope,
                        event_key_suffix=f"side-effect:{request.intent.attempt_id}",
                        event_type="side_effect_confirmed",
                        stage="side_effect_verification",
                        status="completed",
                        occurred_at=completed_at,
                        decision="allow",
                        result_classification=result["classification"],
                        lease_binding=None if lease is None else lease.lease_binding,
                        result_binding=self._result_binding(result),
                    )
                )
            )
        return ToolDispatchRun(envelope, result, tuple(events), True)

    def _now(self) -> str:
        value = self.clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ToolDispatchError("clock must return timezone-aware datetime")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    def _selected_capability(
        self,
        envelope: Mapping[str, Any],
    ) -> ToolCapability:
        selected = _observed_binding(envelope["selected_tool_binding"])
        if selected is None:
            raise ArtifactValidationError(
                ["allowed dispatch lacks selected tool / 已放行调度缺少所选工具"]
            )
        for capability in self.coordinator._capabilities:
            if capability.binding == selected:
                return capability
        raise ArtifactValidationError(
            ["selected tool no longer exists in catalog / 所选工具已不在目录"]
        )

    def _live_authorized(
        self,
        request: ToolDispatchRequest,
        capability: ToolCapability,
    ) -> bool:
        verifier = self.coordinator.authority_verifier
        if verifier is None:
            return False
        try:
            return verifier(request, capability) is True
        except Exception:
            return False

    @staticmethod
    def _normalize_receipt(
        capability: ToolCapability,
        receipt: ToolExecutionReceipt,
    ) -> ToolExecutionReceipt:
        is_write = capability.side_effect_class in _WRITE_CLASSES
        classification = receipt.classification
        side_effect_state = receipt.side_effect_state
        error_category = receipt.error_category
        error_code = receipt.error_code
        retryable = receipt.retryable

        if not is_write and side_effect_state is not SideEffectState.NONE:
            return replace(
                receipt,
                classification=ExecutionClassification.UNKNOWN,
                side_effect_state=SideEffectState.UNKNOWN,
                error_category="contract_violation",
                error_code="READ_ONLY_REPORTED_SIDE_EFFECT",
                retryable=False,
            )
        if (
            is_write
            and classification is ExecutionClassification.SUCCESS
            and side_effect_state is not SideEffectState.CONFIRMED
        ):
            classification = ExecutionClassification.UNKNOWN
            side_effect_state = SideEffectState.UNKNOWN
            error_category = "result_certainty"
            error_code = "SUCCESS_WITHOUT_CONFIRMED_SIDE_EFFECT"
            retryable = False
        if (
            is_write
            and classification is ExecutionClassification.EXPLICIT_FAILURE
            and side_effect_state is not SideEffectState.CONFIRMED_ABSENT
        ):
            classification = ExecutionClassification.UNKNOWN
            side_effect_state = SideEffectState.UNKNOWN
            error_category = "result_certainty"
            error_code = "FAILURE_WITH_UNCERTAIN_SIDE_EFFECT"
            retryable = False
        if (
            capability.side_effect_class
            is SideEffectClass.IRREVERSIBLE_EXTERNAL
            and classification is ExecutionClassification.SUCCESS
            and receipt.external_receipt_binding is None
        ):
            classification = ExecutionClassification.UNKNOWN
            side_effect_state = SideEffectState.UNKNOWN
            error_category = "result_certainty"
            error_code = "EXTERNAL_RECEIPT_MISSING"
            retryable = False
        if classification is ExecutionClassification.UNKNOWN:
            retryable = False
        return replace(
            receipt,
            classification=classification,
            side_effect_state=side_effect_state,
            error_category=error_category,
            error_code=error_code,
            retryable=retryable,
        )

    def _build_nonexecuted_result(
        self,
        request: ToolDispatchRequest,
        envelope: Mapping[str, Any],
        *,
        classification: ExecutionClassification,
        reason_codes: Sequence[str],
        created_at: str,
    ) -> dict[str, Any]:
        next_action = (
            "replan"
            if classification is ExecutionClassification.REJECTED
            else "wait"
        )
        result = self._base_result(
            request,
            envelope,
            classification=classification,
            side_effect_state=SideEffectState.NONE,
            started_at=None,
            completed_at=created_at,
            lease_binding=None,
            output_binding=None,
            external_receipt_binding=None,
            actual_side_effects=(),
            error={
                "category": "admission",
                "code": reason_codes[0] if reason_codes else "NOT_EXECUTED",
                "retryable": classification is ExecutionClassification.WAITING,
            },
            next_action=next_action,
            reused_result_binding=None,
        )
        return build_artifact("tool_execution_result", result)

    def _result_for_existing_lease(
        self,
        request: ToolDispatchRequest,
        envelope: Mapping[str, Any],
        lease: LeaseAcquisition,
        *,
        created_at: str,
    ) -> dict[str, Any]:
        if lease.disposition is LeaseDisposition.REUSED_SUCCESS:
            if lease.prior_result is None:
                raise ToolDispatchError(
                    "reused success lacks prior result / 复用成功缺少原结果"
                )
            prior_binding = self._result_binding(lease.prior_result)
            result = self._base_result(
                request,
                envelope,
                classification=ExecutionClassification.REUSED_SUCCESS,
                side_effect_state=SideEffectState.CONFIRMED,
                started_at=None,
                completed_at=created_at,
                lease_binding=lease.lease_binding,
                output_binding=None,
                external_receipt_binding=None,
                actual_side_effects=(),
                error=None,
                next_action="none",
                reused_result_binding=prior_binding,
            )
        elif lease.disposition is LeaseDisposition.VERIFY_UNKNOWN:
            result = self._base_result(
                request,
                envelope,
                classification=ExecutionClassification.UNKNOWN,
                side_effect_state=SideEffectState.UNKNOWN,
                started_at=None,
                completed_at=created_at,
                lease_binding=lease.lease_binding,
                output_binding=None,
                external_receipt_binding=None,
                actual_side_effects=(),
                error={
                    "category": "idempotency",
                    "code": lease.reason_code or "PRIOR_RESULT_UNKNOWN",
                    "retryable": False,
                },
                next_action="reconcile",
                reused_result_binding=None,
            )
        else:
            result = self._base_result(
                request,
                envelope,
                classification=ExecutionClassification.WAITING,
                side_effect_state=SideEffectState.NONE,
                started_at=None,
                completed_at=created_at,
                lease_binding=lease.lease_binding,
                output_binding=None,
                external_receipt_binding=None,
                actual_side_effects=(),
                error={
                    "category": "idempotency",
                    "code": lease.reason_code or lease.disposition.value,
                    "retryable": False,
                },
                next_action=(
                    "human_review"
                    if lease.disposition
                    is LeaseDisposition.RETRY_AUTHORIZATION_REQUIRED
                    else "wait"
                ),
                reused_result_binding=None,
            )
        return build_artifact("tool_execution_result", result)

    def _build_executed_result(
        self,
        request: ToolDispatchRequest,
        envelope: Mapping[str, Any],
        receipt: ToolExecutionReceipt,
        *,
        lease: LeaseAcquisition | None,
        started_at: str,
        completed_at: str,
    ) -> dict[str, Any]:
        next_action_map = {
            ExecutionClassification.SUCCESS: "none",
            ExecutionClassification.EXPLICIT_FAILURE: (
                "retry" if receipt.retryable else "replan"
            ),
            ExecutionClassification.UNKNOWN: "reconcile",
            ExecutionClassification.PARTIAL_SUCCESS: "compensate",
            ExecutionClassification.WAITING: "wait",
        }
        error = None
        if receipt.error_code is not None:
            error = {
                "category": receipt.error_category or "executor",
                "code": receipt.error_code,
                "retryable": receipt.retryable,
            }
        result = self._base_result(
            request,
            envelope,
            classification=receipt.classification,
            side_effect_state=receipt.side_effect_state,
            started_at=started_at,
            completed_at=completed_at,
            lease_binding=None if lease is None else lease.lease_binding,
            output_binding=receipt.output_binding,
            external_receipt_binding=receipt.external_receipt_binding,
            actual_side_effects=receipt.actual_side_effects,
            error=error,
            next_action=next_action_map.get(
                receipt.classification,
                "human_review",
            ),
            reused_result_binding=None,
        )
        return build_artifact("tool_execution_result", result)

    @staticmethod
    def _base_result(
        request: ToolDispatchRequest,
        envelope: Mapping[str, Any],
        *,
        classification: ExecutionClassification,
        side_effect_state: SideEffectState,
        started_at: str | None,
        completed_at: str,
        lease_binding: Mapping[str, Any] | None,
        output_binding: Mapping[str, Any] | None,
        external_receipt_binding: Mapping[str, Any] | None,
        actual_side_effects: Sequence[Mapping[str, Any]],
        error: Mapping[str, Any] | None,
        next_action: str,
        reused_result_binding: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        dispatch_binding = {
            "id": envelope["dispatch_id"],
            "version": envelope["schema_version"],
            "hash": envelope["dispatch_hash"],
        }
        identity = {
            "dispatch_binding": dispatch_binding,
            "attempt_id": request.intent.attempt_id,
            "classification": classification.value,
            "completed_at": completed_at,
            "reused_result_binding": _binding_state(
                reused_result_binding,
                missing_state="not_applicable",
            ),
        }
        result_id = (
            "TOOL_RESULT_"
            + artifact_fingerprint(identity).removeprefix("sha256:")[:24]
        )
        return {
            "schema_version": TOOL_EXECUTION_RESULT_SCHEMA_VERSION,
            "result_id": result_id,
            "dispatch_binding": dispatch_binding,
            "workflow_id": request.intent.workflow_id,
            "workflow_version": request.intent.workflow_version,
            "run_id": request.intent.run_id,
            "goal_id": request.intent.goal_id,
            "node_id": request.intent.node_id,
            "attempt_id": request.intent.attempt_id,
            "action_id": request.intent.action_id,
            "plan_version": request.intent.plan_version,
            "tool_binding": _detached(envelope["selected_tool_binding"]),
            "permit_binding": _detached(envelope["permit_binding"]),
            "lease_binding": _binding_state(
                lease_binding,
                missing_state="not_applicable",
            ),
            "side_effect_class": envelope["execution_contract"][
                "side_effect_class"
            ],
            "classification": classification.value,
            "side_effect_state": side_effect_state.value,
            "execution_started_at": started_at,
            "execution_completed_at": completed_at,
            "output_binding": _binding_state(
                output_binding,
                missing_state=(
                    "not_applicable"
                    if classification
                    in {
                        ExecutionClassification.REJECTED,
                        ExecutionClassification.WAITING,
                    }
                    else "unknown"
                ),
            ),
            "external_receipt_binding": _binding_state(
                external_receipt_binding,
                missing_state="not_applicable",
            ),
            "actual_side_effects": [deepcopy(dict(item)) for item in actual_side_effects],
            "error": None if error is None else deepcopy(dict(error)),
            "next_action": next_action,
            "reused_result_binding": _binding_state(
                reused_result_binding,
                missing_state="not_applicable",
            ),
            "created_at": completed_at,
        }

    def _record_result_event(
        self,
        request: ToolDispatchRequest,
        envelope: Mapping[str, Any],
        result: Mapping[str, Any],
        occurred_at: str,
    ) -> Mapping[str, Any]:
        event_type_map = {
            ExecutionClassification.SUCCESS.value: "tool_execution_succeeded",
            ExecutionClassification.REUSED_SUCCESS.value: "tool_result_reused",
            ExecutionClassification.REJECTED.value: "tool_execution_rejected",
            ExecutionClassification.EXPLICIT_FAILURE.value: "tool_execution_failed",
            ExecutionClassification.UNKNOWN.value: "tool_execution_unknown",
            ExecutionClassification.PARTIAL_SUCCESS.value: "tool_execution_partial",
            ExecutionClassification.WAITING.value: "tool_execution_waiting",
        }
        lease_binding = _observed_binding(result["lease_binding"])
        return self.store.append_event(
            _event_draft(
                request,
                envelope,
                event_key_suffix=f"result:{request.intent.attempt_id}",
                event_type=event_type_map[result["classification"]],
                stage="result_classification",
                status="completed",
                occurred_at=occurred_at,
                decision=envelope["decision"],
                result_classification=result["classification"],
                lease_binding=lease_binding,
                result_binding=self._result_binding(result),
                reason_codes=envelope["reason_codes"],
            )
        )

    @staticmethod
    def _result_binding(result: Mapping[str, Any]) -> dict[str, Any]:
        validate_tool_execution_result(result)
        return {
            "id": result["result_id"],
            "version": result["schema_version"],
            "hash": result["result_hash"],
        }


__all__ = [
    "ADMISSION_CHECK_ORDER",
    "ActionApproval",
    "ActionIntent",
    "ActionRisk",
    "AdmissionCheck",
    "AdmissionDecision",
    "ApprovalState",
    "DispatchContext",
    "DurableStoreRequiredError",
    "ExecutionClassification",
    "InMemoryToolEventStore",
    "LeaseAcquisition",
    "LeaseDisposition",
    "ObservationMode",
    "SideEffectClass",
    "SideEffectState",
    "StateEvidence",
    "ToolCapability",
    "ToolDispatchConflictError",
    "ToolDispatchCoordinator",
    "ToolDispatchError",
    "ToolDispatchPolicy",
    "ToolDispatchRequest",
    "ToolDispatchRun",
    "ToolDispatchRuntime",
    "ToolDispatchStore",
    "ToolExecutionReceipt",
    "seal_tool_execution_event",
    "validate_tool_dispatch_envelope",
    "validate_tool_execution_event",
    "validate_tool_execution_result",
]
