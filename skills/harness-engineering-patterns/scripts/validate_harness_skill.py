from __future__ import annotations

import argparse
import ast
import importlib
import importlib.util
import json
import pathlib
import re
import sys
from collections import Counter
from enum import Enum
from types import ModuleType

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


DESIGN_FIELDS = (
    "状态 / Status",
    "模式清单 / Patterns",
    "诊断用途 / Diagnostic Use",
    "适用工作流节点 / Applicable Workflow Nodes",
    "当前症状 / Current Symptoms",
    "适配信号 / Fit Signals",
    "调整方向 / Adjustment Direction",
    "修改方式 / How To Modify",
    "输入 / Inputs",
    "输出 / Outputs",
    "风险与治理 / Risks & Governance",
)

OBSERVABILITY_FIELDS = (
    "质量指标 / Quality Metrics",
    "时延指标 / Latency Metrics",
    "成本指标 / Cost Metrics",
    "风险指标 / Risk Metrics",
    "Trace 指标 / Trace Metrics",
)

EIR_HEADINGS = (
    "## Control Flow / 控制流",
    "## State Flow / 状态流",
    "## Tool Flow / 工具流",
    "## Permission Flow / 权限流",
    "## Pattern Record / 模式记录",
    "## Skill Recommendation / Skill 建议",
    "## Evaluation Reference / 评价引用",
    "## Governance Item / 治理项",
)

EVALUATION_KEYS = (
    "coverage",
    "mapping_accuracy",
    "evidence",
    "reuse",
    "skill_readiness",
    "governance",
    "evaluability",
)

RUNTIME_PROTOCOLS = {
    "PATTERN_0051": {
        "reference": "references/reasoning-execution-flow.md",
        "source_draft_id": "PATTERN_0001",
        "source_version": "0.2.0",
        "name_en": "Reasoning Execution Flow",
        "name_zh": "推理执行流程",
        "matrix_coordinates": {
            "COG_REASONING__TOP_ROUTING",
            "COG_REASONING__TOP_CHAIN",
            "COG_REASONING__TOP_PARALLEL",
            "COG_REASONING__TOP_ORCHESTRATION",
            "COG_REASONING__TOP_LOOP",
            "COG_GOVERNANCE__TOP_HIERARCHY",
        },
    },
    "PATTERN_0052": {
        "reference": "references/workflow-observability-probes.md",
        "source_draft_id": "PATTERN_0002",
        "source_version": "0.7.0",
        "name_en": "Workflow Observability Probes",
        "name_zh": "工作流可观测性探针",
        "matrix_coordinates": {
            "COG_PERCEPTION__TOP_ORCHESTRATION",
            "COG_MEMORY__TOP_CHAIN",
            "COG_REFLECTION__TOP_LOOP",
            "COG_GOVERNANCE__TOP_ORCHESTRATION",
            "COG_GOVERNANCE__TOP_HIERARCHY",
        },
    },
}

REQUIRED_PROBES = tuple(f"PROBE_{number:04d}" for number in range(1, 24))

RUNTIME_SCHEMA_FILES = (
    "schemas/goal-contract.schema.json",
    "schemas/normalized-input.schema.json",
    "schemas/reasoning-chain-blueprint.schema.json",
    "schemas/reasoning-chain-checkpoint-validation.schema.json",
    "schemas/reasoning-chain-plan.schema.json",
    "schemas/reasoning-parallel-blueprint.schema.json",
    "schemas/reasoning-parallel-plan.schema.json",
    "schemas/reasoning-contract.schema.json",
    "schemas/reasoning-event.schema.json",
    "schemas/reasoning-result.schema.json",
    "schemas/reflection-contract.schema.json",
    "schemas/reflection-event.schema.json",
    "schemas/reflection-round-observation.schema.json",
    "schemas/tool-dispatch-envelope.schema.json",
    "schemas/tool-execution-event.schema.json",
    "schemas/tool-execution-result.schema.json",
    "schemas/workflow-route-envelope.schema.json",
    "schemas/workflow-route-revision.schema.json",
    "schemas/workflow-plan.schema.json",
    "schemas/workflow-plan-patch.schema.json",
    "schemas/workflow-checkpoint.schema.json",
    "schemas/workflow-execution-result.schema.json",
)

RUNTIME_IMPLEMENTATION_FILES = (
    "runtime/__init__.py",
    "runtime/plan_execution.py",
    "runtime/plan_execution_completion.py",
    "runtime/plan_execution_events.py",
    "runtime/plan_execution_sqlite_store.py",
    "runtime/plan_tool_dispatch.py",
    "runtime/reasoning_chain_factory.py",
    "runtime/reasoning_chain_compiler.py",
    "runtime/reasoning_chain_session.py",
    "runtime/reasoning_parallel_factory.py",
    "runtime/reasoning_parallel_outbox.py",
    "runtime/reasoning_parallel_postgres_outbox.py",
    "runtime/reasoning_parallel_projection.py",
    "runtime/reasoning_parallel_scheduler.py",
    "runtime/reasoning_event_postgres_store.py",
    "runtime/reasoning_event_sqlite_store.py",
    "runtime/reasoning_runtime.py",
    "runtime/reflection_runtime.py",
    "runtime/reasoning_router.py",
    "runtime/tool_dispatch.py",
    "runtime/tool_dispatch_projection.py",
    "runtime/tool_dispatch_sqlite_store.py",
    "runtime/workflow_router.py",
    "runtime/workflow_route_ledger.py",
    "runtime/workflow_route_sqlite_ledger.py",
    "runtime/reasoning_artifacts.py",
    "runtime/reasoning_metrics.py",
    "runtime/metric_registry.json",
    "runtime/probe_registry.json",
    "runtime/probe_dependency_matrix.json",
)

CHAIN_FACTORY_REFERENCE = (
    "references/reasoning-chain-factory.md"
)

CHAIN_FACTORY_MARKERS = (
    "../schemas/reasoning-chain-blueprint.schema.json",
    "../schemas/reasoning-chain-checkpoint-validation.schema.json",
    "../schemas/reasoning-chain-plan.schema.json",
    "../runtime/reasoning_chain_factory.py",
    "preflight runtime capabilities / 预检运行时能力",
    "private chain-of-thought",
    "私密思维链",
)

PARALLEL_FACTORY_REFERENCE = (
    "references/reasoning-parallel-factory.md"
)

PARALLEL_FACTORY_MARKERS = (
    "../schemas/reasoning-parallel-blueprint.schema.json",
    "../schemas/reasoning-parallel-plan.schema.json",
    "../runtime/reasoning_parallel_factory.py",
    "../runtime/reasoning_parallel_outbox.py",
    "../runtime/reasoning_parallel_postgres_outbox.py",
    "../runtime/reasoning_parallel_projection.py",
    "../runtime/reasoning_parallel_scheduler.py",
    "../runtime/reasoning_event_postgres_store.py",
    "../runtime/reasoning_event_sqlite_store.py",
    "HARNESS_POSTGRES_DSN",
    "fencing token / 栅栏令牌",
    "at-least-once / 至少一次",
    "resume_session()",
    "close_leased_branch()",
    "finalize_selected_candidate()",
    "terminal_results",
    ".results.json",
    "project_parallel_run(plan, events)",
    "All branch budgets are reserved before any branch starts.",
    "private chain-of-thought",
    "私密思维链",
)

TOOL_DISPATCH_REFERENCE = "references/tool-dispatch-execution.md"

REFLECTION_EXECUTION_REFERENCE = "references/reflection-execution-flow.md"

REFLECTION_EXECUTION_MARKERS = (
    "Version / 版本: `1.0.0`",
    "## Admission And Routing / 准入与路由",
    "## State Machine / 状态机",
    "## Baseline Change Result / 基线改变结果",
    "## Independent Revalidation And Anti-Gaming / 独立复验与反投机",
    "## Stopping Recovery And Learning / 停止恢复与学习",
    "../schemas/reflection-contract.schema.json",
    "../schemas/reflection-event.schema.json",
    "../schemas/reflection-round-observation.schema.json",
    "../runtime/reflection_runtime.py",
    "private chain-of-thought",
    "私密思维过程",
)

TOOL_DISPATCH_MARKERS = (
    "../schemas/tool-dispatch-envelope.schema.json",
    "../schemas/tool-execution-event.schema.json",
    "../schemas/tool-execution-result.schema.json",
    "../runtime/tool_dispatch.py",
    "../runtime/tool_dispatch_projection.py",
    "../runtime/tool_dispatch_sqlite_store.py",
    "## Capability Frontier / 能力前沿",
    "## Admission / 执行准入",
    "## Durable Idempotency / 持久幂等",
    "Selection and admission remain separate",
    "选择与准入仍保持分离",
    "unknown",
    "结果未知",
)

PLAN_EXECUTION_REFERENCE = (
    "references/patterns/action/action-orchestration.md"
)

PLAN_EXECUTION_OBSERVABILITY = (
    "references/patterns/action/action-orchestration-observability.md"
)

PLAN_EXECUTION_MARKERS = (
    "Version / 版本: `1.1.0`",
    "../../../schemas/goal-contract.schema.json",
    "../../../schemas/workflow-plan.schema.json",
    "../../../schemas/workflow-plan-patch.schema.json",
    "../../../schemas/workflow-checkpoint.schema.json",
    "../../../schemas/workflow-execution-result.schema.json",
    "../../../runtime/plan_execution.py",
    "../../../runtime/plan_execution_completion.py",
    "../../../runtime/plan_execution_events.py",
    "../../../runtime/plan_execution_sqlite_store.py",
    "../../../runtime/plan_tool_dispatch.py",
    "## Hard Invariants / 硬不变量",
    "## Mechanical State Machine / 机械状态机",
    "## Checkpoint And Idempotency / 检查点与幂等",
    "## Local Replanning / 局部重规划",
    "UNKNOWN → VERIFYING",
    "failed-and-affected subgraph",
    "失败节点及受影响子图",
    "persist-before-dispatch",
    "分派前持久化",
    "completion gate",
    "完成闸门",
)

CANONICAL_RUNTIME_ENUMS = {
    "workflow_state": (
        "received",
        "normalized",
        "governance_precheck",
        "routed",
        "contract_established",
        "executing",
        "waiting_for_evidence",
        "mode_switched",
        "candidate_ready",
        "validating",
        "repairable_failure",
        "completed",
        "rejected",
        "failed",
        "escalated",
        "cancelled",
        "timed_out",
    ),
    "event_processing_status": ("accepted", "duplicate", "rejected"),
    "validation_result": (
        "not_run",
        "passed",
        "conditionally_passed",
        "repairable_failure",
        "nonrepairable_failure",
        "human_required",
        "timed_out",
    ),
    "execution_mode": ("direct", "chain", "parallel", "iterative"),
    "primary_topology": ("chain", "parallel", "loop"),
    "value_state": (
        "observed",
        "observed_zero",
        "missing",
        "unknown",
        "not_applicable",
    ),
}

UNIVERSAL_REASONING_PROBES = {"PROBE_0001", "PROBE_0014", "PROBE_0015"}

MODE_REQUIRED_PROBE_BASELINES = {
    "direct": {
        "PROBE_0001",
        "PROBE_0002",
        "PROBE_0003",
        "PROBE_0004",
        "PROBE_0005",
        "PROBE_0006",
        "PROBE_0011",
        "PROBE_0012",
        "PROBE_0014",
        "PROBE_0015",
    },
    "chain": {
        "PROBE_0001",
        "PROBE_0002",
        "PROBE_0003",
        "PROBE_0004",
        "PROBE_0005",
        "PROBE_0006",
        "PROBE_0010",
        "PROBE_0011",
        "PROBE_0012",
        "PROBE_0014",
        "PROBE_0015",
    },
    "parallel": {
        "PROBE_0001",
        "PROBE_0002",
        "PROBE_0003",
        "PROBE_0004",
        "PROBE_0005",
        "PROBE_0006",
        "PROBE_0008",
        "PROBE_0010",
        "PROBE_0011",
        "PROBE_0012",
        "PROBE_0014",
        "PROBE_0015",
    },
    "iterative": {
        "PROBE_0001",
        "PROBE_0002",
        "PROBE_0003",
        "PROBE_0004",
        "PROBE_0005",
        "PROBE_0006",
        "PROBE_0007",
        "PROBE_0009",
        "PROBE_0010",
        "PROBE_0011",
        "PROBE_0012",
        "PROBE_0014",
        "PROBE_0015",
    },
    "orchestration": {
        "PROBE_0001",
        "PROBE_0002",
        "PROBE_0003",
        "PROBE_0004",
        "PROBE_0005",
        "PROBE_0006",
        "PROBE_0007",
        "PROBE_0010",
        "PROBE_0011",
        "PROBE_0012",
        "PROBE_0014",
        "PROBE_0015",
    },
    "hierarchy": {
        "PROBE_0001",
        "PROBE_0002",
        "PROBE_0004",
        "PROBE_0005",
        "PROBE_0006",
        "PROBE_0010",
        "PROBE_0011",
        "PROBE_0012",
        "PROBE_0014",
        "PROBE_0015",
    },
}

MODE_OBSERVABILITY_FILES = {
    "direct": "reasoning-routing-observability.md",
    "chain": "reasoning-chain-observability.md",
    "parallel": "reasoning-parallel-observability.md",
    "iterative": "reasoning-loop-observability.md",
    "orchestration": "reasoning-orchestration-observability.md",
    "hierarchy": "reasoning-hierarchy-observability.md",
}

SCHEMA_CANONICAL_ENUM_POINTERS = {
    "workflow_state": (
        ("schemas/reasoning-event.schema.json", "/$defs/WorkflowState"),
        ("schemas/reasoning-event.schema.json", "/properties/workflow_state"),
        ("schemas/reasoning-event.schema.json", "/properties/previous_state"),
        ("schemas/reasoning-event.schema.json", "/properties/next_state"),
    ),
    "event_processing_status": (
        ("schemas/reasoning-event.schema.json", "/$defs/EventProcessingStatus"),
        ("schemas/reasoning-event.schema.json", "/properties/event_processing_status"),
    ),
    "validation_result": (
        ("schemas/reasoning-event.schema.json", "/$defs/ValidationOutcome"),
        (
            "schemas/reasoning-event.schema.json",
            "/$defs/ValidationResult/properties/result",
        ),
        ("schemas/reasoning-result.schema.json", "/$defs/ValidationOutcome"),
        (
            "schemas/reasoning-result.schema.json",
            "/$defs/ValidationResult/properties/result",
        ),
    ),
    "execution_mode": (
        ("schemas/reasoning-contract.schema.json", "/properties/execution_mode"),
        (
            "schemas/reasoning-contract.schema.json",
            "/$defs/ReasoningConfiguration/properties/execution_mode",
        ),
        ("schemas/reasoning-event.schema.json", "/properties/execution_mode"),
        (
            "schemas/reasoning-event.schema.json",
            "/$defs/ReasoningConfiguration/properties/execution_mode",
        ),
    ),
    "primary_topology": (
        ("schemas/reasoning-contract.schema.json", "/properties/primary_topology"),
        (
            "schemas/reasoning-contract.schema.json",
            "/$defs/ReasoningConfiguration/properties/primary_topology",
        ),
        ("schemas/reasoning-event.schema.json", "/properties/primary_topology"),
        (
            "schemas/reasoning-event.schema.json",
            "/$defs/ReasoningConfiguration/properties/primary_topology",
        ),
    ),
    "value_state": (
        (
            "schemas/normalized-input.schema.json",
            "/$defs/FieldProvenance/properties/value_state",
        ),
        (
            "schemas/reasoning-event.schema.json",
            "/$defs/FieldProvenance/properties/value_state",
        ),
        (
            "schemas/reasoning-result.schema.json",
            "/$defs/FieldProvenance/properties/value_state",
        ),
    ),
}

METRIC_DIRECTIONS = {
    "closer_to_one_is_better",
    "higher_is_better",
    "lower_is_better",
}

METRIC_UTILITY_EXPORTS = {
    "bounded_ratio",
    "budget_utilization_max",
    "calculate_metric",
    "metric_publication_failures",
    "publish_metric",
    "resolve_required_probes",
    "safe_ratio",
    "unavailable_metric",
    "unbounded_ratio",
}

DOCUMENT_METRIC_ALIASES = {
    "budget_utilization": "budget_utilization_vector",
}

RUNTIME_REQUIRED_EXPORTS = {
    "package": {
        "BudgetLimits",
        "ChainPlanSession",
        "EventStore",
        "ParallelDispatchCoordinator",
        "PlanExecutionSession",
        "PostgresEventStore",
        "PostgresParallelDispatchOutbox",
        "ReasoningEngine",
        "ReasoningChainFactory",
        "ReasoningEvent",
        "ReflectionSession",
        "RUNTIME_SUPPORTED_STOP_TYPES",
        "RiskLevel",
        "SqliteParallelDispatchOutbox",
        "SqliteToolDispatchStore",
        "SqliteWorkflowRouteLedger",
        "ToolDispatchCoordinator",
        "ToolDispatchRuntime",
        "workflow_route_stream_key",
        "project_tool_dispatch_run",
        "ValidationStatus",
        "WorkflowState",
        "validate_runtime_contract_capabilities",
        "validate_reflection_contract",
        "validate_reflection_event",
        "validate_reflection_event_stream",
        "validate_reflection_round_observation",
        "validate_workflow_checkpoint",
        "validate_workflow_plan",
        "validate_workflow_plan_patch",
    },
    "reasoning_router": {
        "ExecutionMode",
        "PrimaryTopology",
        "RiskLevel",
        "RouteDecision",
        "RoutingPolicy",
        "RoutingSignals",
    },
    "reasoning_metrics": {
        "MetricEnvelope",
        "MetricResult",
        "MetricState",
        "ProbeDependencyResolution",
        "resolve_required_probes",
    },
    "reflection_runtime": {
        "ReflectionEligibility",
        "ReflectionImprovementState",
        "ReflectionOutcome",
        "ReflectionRoute",
        "ReflectionSession",
        "ReflectionState",
        "build_reflection_contract",
        "resolve_reflection_required_probes",
        "validate_reflection_contract",
        "validate_reflection_event",
        "validate_reflection_event_stream",
        "validate_reflection_round_observation",
    },
    "reasoning_chain_factory": {
        "ChainFactoryError",
        "ChainPlanDriftError",
        "ChainPlanSession",
        "ChainPlanStateError",
        "ChainStepOutcome",
        "ReasoningChainFactory",
        "validate_chain_blueprint",
        "validate_chain_plan",
    },
    "plan_execution": {
        "ActionClaim",
        "IdempotencyStatus",
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
    },
}

EXECUTION_CONTRACT_MARKERS = (
    "## Identity And Input Contract / 标识与输入契约",
    "## Machine-Readable Contracts / 机器可读契约",
    "## Reasoning Contract / 推理契约",
    "## State Machine And Main Flow / 状态机与主流程",
    "## Routing And Execution Modes / 路由与执行模式",
    "## Validation, Switching, And Stopping / 验证、换路与停止",
    "## Standalone And Interactive Operation / 独立与交互运行",
    "## Output And Acceptance / 输出与验收",
    "task_id",
    "run_id",
    "step_id",
    "parent_event_id",
    "idempotency_key",
    "workflow_state",
    "event_processing_status",
    "direct | chain | parallel | iterative",
    "private chain-of-thought",
    "私密思维过程",
)

OBSERVABILITY_CONTRACT_MARKERS = (
    "## Deployment And Probe Contract / 部署与探针契约",
    "## Identity, Event, And Provenance / 标识事件与来源",
    "## Probe Catalog / 探针目录",
    "## Standalone And Interactive Operation / 独立与交互运行",
    "## Metrics And Alerts / 指标与告警",
    "## Data Completion And Scenario Packs / 数据补全与场景包",
    "## Report And Acceptance / 报告与验收",
    "schema_version",
    "field_provenance",
    "event_processing_status",
    "workflow_state",
    "outcome_linkage_coverage",
    "underroute_rate",
    "overroute_rate",
    "route_abstention_rate",
    "route_oscillation_rate",
    "forced_route_with_missing_signal_rate",
    "missing",
    "private chain-of-thought",
    "私密思维过程",
)

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\((?P<target>[^)]+)\)")
BUNDLED_TRACE_TARGET = (
    r"(?:`?references/patterns/<capability-key>/trace\.md`?|"
    r"\[trace\.md\]\(trace\.md\))"
)
BUNDLED_TRACE_WRITE = re.compile(
    r"(?is)\b(?:add\s+an\s+entry|append|write|update|record)\b.{0,80}"
    r"\b(?:to|into|in)\s+" + BUNDLED_TRACE_TARGET
)
BUNDLED_TRACE_PATH_FIRST_WRITE = re.compile(
    r"(?is)" + BUNDLED_TRACE_TARGET
    + r".{0,60}(?:\bto\s+(?:append|write|update|record)\b|记录(?:使用)?结果|写入结果|追加记录)"
)


class ValidationReport:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, code: str, message_en: str, message_zh: str) -> None:
        self.errors.append(f"{code}: {message_en} / {message_zh}")

    def warning(self, code: str, message_en: str, message_zh: str) -> None:
        self.warnings.append(f"{code}: {message_en} / {message_zh}")


def load_registry(skill_dir: pathlib.Path) -> dict[str, object]:
    path = skill_dir / "references" / "registry.json"
    return json.loads(path.read_text(encoding="utf-8"))


def duplicate_values(records: list[dict[str, object]], field: str) -> list[str]:
    values = [str(record.get(field, "")) for record in records]
    return sorted(value for value, count in Counter(values).items() if count > 1)


def has_bundled_trace_write(content: str) -> bool:
    return bool(
        BUNDLED_TRACE_WRITE.search(content)
        or BUNDLED_TRACE_PATH_FIRST_WRITE.search(content)
    )


def is_bilingual_text(value: object) -> bool:
    """Return whether text contains English and CJK content. / 判断文本是否同时含英文与中文。"""

    return isinstance(value, str) and bool(re.search(r"[A-Za-z]", value)) and bool(
        re.search(r"[\u3400-\u9fff]", value)
    )


def is_nonempty_string(value: object) -> bool:
    """Return whether a value is a non-empty string. / 判断值是否为非空字符串。"""

    return isinstance(value, str) and bool(value.strip())


def is_string_list(value: object, *, allow_empty: bool = True) -> bool:
    """Validate a JSON string array without constructing an unsafe set. / 安全校验 JSON 字符串数组。"""

    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(is_nonempty_string(item) for item in value)
    )


def has_duplicates(values: list[str]) -> bool:
    """Return whether a validated string list contains duplicates. / 判断已校验字符串列表是否重复。"""

    return len(values) != len(set(values))


def load_json_resource(
    path: pathlib.Path,
    report: ValidationReport,
    code: str,
) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        report.error(
            code,
            f"cannot load {path.name}: {error}",
            f"无法加载 {path.name}：{error}",
        )
        return None
    if not isinstance(value, dict):
        report.error(
            code,
            f"{path.name} must contain a JSON object",
            f"{path.name} 必须包含 JSON 对象",
        )
        return None
    return value


def markdown_table_rows(content: str, header_prefix: str) -> list[list[str]]:
    """Extract one simple pipe table. / 提取一个简单管道表格。"""

    lines = content.splitlines()
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if line.strip().startswith(header_prefix)
        )
    except StopIteration:
        return []

    rows: list[list[str]] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
    return rows


def nested_json_keys(value: object) -> set[str]:
    """Collect object keys recursively. / 递归收集 JSON 对象键。"""

    if isinstance(value, dict):
        keys = {str(key) for key in value}
        for child in value.values():
            keys.update(nested_json_keys(child))
        return keys
    if isinstance(value, list):
        keys: set[str] = set()
        for child in value:
            keys.update(nested_json_keys(child))
        return keys
    return set()


def json_pointer_value(document: object, pointer: str) -> object:
    """Resolve an RFC 6901 JSON pointer. / 解析 RFC 6901 JSON Pointer。"""

    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    current = document
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            current = current[token]
        elif isinstance(current, list):
            current = current[int(token)]
        else:
            raise KeyError(pointer)
    return current


def schema_enum_values(
    schema: dict[str, object],
    fragment: object,
    *,
    resolving: frozenset[str] = frozenset(),
) -> list[str]:
    """Resolve local refs and collect string enum values. / 解析本地引用并收集字符串枚举值。"""

    if not isinstance(fragment, dict):
        return []
    values: list[str] = []
    reference = fragment.get("$ref")
    if isinstance(reference, str) and reference.startswith("#/"):
        if reference in resolving:
            return []
        target = json_pointer_value(schema, reference[1:])
        values.extend(
            schema_enum_values(
                schema,
                target,
                resolving=resolving | frozenset({reference}),
            )
        )
    enum_values = fragment.get("enum")
    if isinstance(enum_values, list):
        values.extend(value for value in enum_values if isinstance(value, str))
    const_value = fragment.get("const")
    if isinstance(const_value, str):
        values.append(const_value)
    for keyword in ("oneOf", "anyOf"):
        branches = fragment.get(keyword)
        if isinstance(branches, list):
            for branch in branches:
                values.extend(
                    schema_enum_values(schema, branch, resolving=resolving)
                )
    return list(dict.fromkeys(values))


def schema_enum_at(schema: dict[str, object], pointer: str) -> list[str]:
    """Read the effective string enum at a semantic pointer. / 读取语义指针处的有效字符串枚举。"""

    return schema_enum_values(schema, json_pointer_value(schema, pointer))


def markdown_section(content: str, heading: str) -> str | None:
    """Extract one Markdown section by its exact heading. / 按准确标题提取 Markdown 小节。"""

    match = re.search(
        rf"(?ms)^{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^#{{1,6}}\s|\Z)",
        content,
    )
    return match.group("body") if match else None


def document_metric_ids(content: str) -> set[str]:
    """Extract metric assignments from the normative metrics section. / 从规范指标章节提取指标赋值。"""

    match = re.search(
        r"(?ms)^## Metrics And Alerts / 指标与告警\s*$"
        r"(?P<body>.*?)"
        r"(?=^## Data Completion And Scenario Packs / 数据补全与场景包\s*$)",
        content,
    )
    body = match.group("body") if match else ""
    identifiers = set(
        re.findall(r"(?m)^\s*([a-z][a-z0-9_]*)(?:\[[^\]]+\])?\s*=", body)
    )
    return {DOCUMENT_METRIC_ALIASES.get(identifier, identifier) for identifier in identifiers}


def exported_metric_function_names(path: pathlib.Path) -> set[str]:
    """Read exported metric functions without executing the module. / 不执行模块地读取已导出指标函数。"""

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError):
        return set()
    functions = {
        node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    exported: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue
        if is_string_list(value):
            exported.update(value)
    return (exported & functions) - METRIC_UTILITY_EXPORTS


def validate_budget_profile_table(execution: str, report: ValidationReport) -> None:
    rows = markdown_table_rows(execution, "| Profile / 档位")
    if len(rows) != 6:
        report.error(
            "reasoning_budget_table",
            "budget profile table must contain one header, separator, and four profiles",
            "预算档位表必须包含一个表头、分隔行和四个档位",
        )
        return

    expected_header = [
        "Profile / 档位",
        "Reasoning tokens / 推理令牌",
        "Latency / 延迟",
        "Model calls / 模型调用",
        "Tool calls / 工具调用",
        "Paths / 路径",
        "Iterations / 轮次",
        "Typical use / 常见用途",
    ]
    expected_columns = len(expected_header)
    if rows[0] != expected_header or any(
        len(row) != expected_columns for row in rows
    ):
        report.error(
            "reasoning_budget_table",
            "budget table header and every row must contain the canonical eight columns",
            "预算表头及每行必须包含规范的八列",
        )
        return

    if any(not re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        report.error(
            "reasoning_budget_table",
            "budget table must contain a valid Markdown separator row",
            "预算表必须包含有效的 Markdown 分隔行",
        )

    expected_profiles = {
        "light / 轻量",
        "standard / 标准",
        "deep / 深入",
        "controlled-high-risk / 受控高风险",
    }
    observed_profiles = [row[0] for row in rows[2:]]
    if (
        set(observed_profiles) != expected_profiles
        or len(observed_profiles) != len(set(observed_profiles))
    ):
        report.error(
            "reasoning_budget_table",
            f"budget profiles are invalid: {observed_profiles}",
            f"预算档位无效：{observed_profiles}",
        )

    def positive_integer(cell: str) -> int | None:
        normalized = cell.replace(",", "").strip()
        if not re.fullmatch(r"[0-9]+", normalized):
            return None
        value = int(normalized)
        return value if value > 0 else None

    def positive_latency(cell: str) -> float | None:
        match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*(ms|s)", cell.strip())
        if not match:
            return None
        value = float(match.group(1))
        return value if value > 0 else None

    numeric_labels = (
        "reasoning tokens",
        "latency",
        "model calls",
        "tool calls",
        "paths",
        "iterations",
    )
    for row in rows[2:]:
        parsed = (
            positive_integer(row[1]),
            positive_latency(row[2]),
            positive_integer(row[3]),
            positive_integer(row[4]),
            positive_integer(row[5]),
            positive_integer(row[6]),
        )
        invalid = [
            label for label, value in zip(numeric_labels, parsed) if value is None
        ]
        if invalid or not is_bilingual_text(row[7]):
            report.error(
                "reasoning_budget_table",
                f"{row[0]} has invalid positive dimensions {invalid} or non-bilingual use text",
                f"{row[0]} 的正数维度 {invalid} 无效或常见用途不是双语",
            )

    expected_iterations = {
        "light / 轻量": 1,
        "standard / 标准": 6,
        "deep / 深入": 12,
        "controlled-high-risk / 受控高风险": 8,
    }
    observed = {row[0]: positive_integer(row[6]) for row in rows[2:]}
    if observed != expected_iterations:
        report.error(
            "reasoning_budget_table",
            f"budget iteration values are invalid: {observed}",
            f"预算迭代次数无效：{observed}",
        )


def validate_reasoning_schemas(
    skill_dir: pathlib.Path, report: ValidationReport
) -> dict[str, dict[str, object]]:
    schemas: dict[str, dict[str, object]] = {}
    for relative in RUNTIME_SCHEMA_FILES:
        path = skill_dir / relative
        schema = load_json_resource(path, report, "reasoning_schema")
        if schema is None:
            continue
        schemas[relative] = schema
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as error:
            report.error(
                "reasoning_schema",
                f"{relative} is not a valid Draft 2020-12 schema: {error.message}",
                f"{relative} 不是有效的 Draft 2020-12 Schema：{error.message}",
            )
        if (
            schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("x-contract-version") != "1.0.0"
            or not is_bilingual_text(schema.get("title"))
            or not is_bilingual_text(schema.get("description"))
        ):
            report.error(
                "reasoning_schema",
                f"{relative} lacks Draft 2020-12, version 1.0.0, or bilingual metadata",
                f"{relative} 缺少 Draft 2020-12、1.0.0 版本或双语元数据",
            )
        forbidden_reasoning_fields = {
            "chain_of_thought",
            "private_reasoning",
            "hidden_reasoning",
            "internal_thoughts",
        }
        found_forbidden = sorted(forbidden_reasoning_fields & nested_json_keys(schema))
        if found_forbidden:
            report.error(
                "reasoning_schema_privacy",
                f"{relative} exposes private reasoning fields {found_forbidden}",
                f"{relative} 暴露私密推理字段 {found_forbidden}",
            )

    event_schema = schemas.get("schemas/reasoning-event.schema.json")
    canonical = event_schema.get("x-canonical-enums") if event_schema else None
    if not isinstance(canonical, dict):
        report.error(
            "reasoning_schema_enums",
            "reasoning event schema must declare x-canonical-enums",
            "推理事件 Schema 必须声明 x-canonical-enums",
        )
        return schemas
    for name, expected in CANONICAL_RUNTIME_ENUMS.items():
        observed = canonical.get(name)
        if observed != list(expected):
            report.error(
                "reasoning_schema_enums",
                f"canonical enum {name} expected {list(expected)}, observed {observed}",
                f"权威枚举 {name} 应为 {list(expected)}，实际为 {observed}",
            )

    for name, locations in SCHEMA_CANONICAL_ENUM_POINTERS.items():
        expected = list(CANONICAL_RUNTIME_ENUMS[name])
        for relative, pointer in locations:
            schema = schemas.get(relative)
            if schema is None:
                continue
            try:
                observed = schema_enum_at(schema, pointer)
            except (KeyError, TypeError, ValueError) as error:
                report.error(
                    "reasoning_schema_enums",
                    f"cannot resolve canonical enum {name} at {relative}#{pointer}: {error}",
                    f"无法解析 {relative}#{pointer} 的权威枚举 {name}：{error}",
                )
                continue
            if observed != expected:
                report.error(
                    "reasoning_schema_enums",
                    f"{relative}#{pointer} expected {name}={expected}, observed {observed}",
                    f"{relative}#{pointer} 的 {name} 应为 {expected}，实际为 {observed}",
                )
    return schemas


def validate_metric_registry(skill_dir: pathlib.Path, report: ValidationReport) -> None:
    path = skill_dir / "runtime" / "metric_registry.json"
    registry = load_json_resource(path, report, "reasoning_metric_registry")
    if registry is None:
        return
    if (
        registry.get("schema_version") != "1.0.0"
        or not is_nonempty_string(registry.get("name_en"))
        or not is_nonempty_string(registry.get("name_zh"))
        or not re.search(r"[\u3400-\u9fff]", str(registry.get("name_zh", "")))
        or not is_nonempty_string(registry.get("description_en"))
        or not is_nonempty_string(registry.get("description_zh"))
        or not re.search(
            r"[\u3400-\u9fff]", str(registry.get("description_zh", ""))
        )
    ):
        report.error(
            "reasoning_metric_registry",
            "metric registry metadata must use schema 1.0.0 and non-empty bilingual fields",
            "指标注册表元数据必须使用 1.0.0 Schema 和非空双语字段",
        )

    records = registry.get("metrics")
    if not isinstance(records, list):
        report.error(
            "reasoning_metric_registry",
            "metric registry must contain a metrics array",
            "指标注册表必须包含 metrics 数组",
        )
        return

    required_fields = {
        "metric_id",
        "version",
        "name_en",
        "name_zh",
        "formula",
        "inputs",
        "unit",
        "direction",
        "required_probes",
        "denominator",
        "exclusions",
        "minimum_sample",
        "owner",
    }
    observed_ids: list[str] = []
    for record in records:
        if not isinstance(record, dict) or not required_fields.issubset(record):
            report.error(
                "reasoning_metric_registry",
                f"metric record lacks required fields: {record}",
                f"指标记录缺少必需字段：{record}",
            )
            continue

        metric_id = record.get("metric_id")
        if not isinstance(metric_id, str) or not re.fullmatch(
            r"[a-z][a-z0-9_]*", metric_id
        ):
            report.error(
                "reasoning_metric_registry",
                f"metric record has invalid metric_id: {metric_id}",
                f"指标记录的 metric_id 无效：{metric_id}",
            )
            continue
        observed_ids.append(metric_id)

        scalar_fields_valid = (
            isinstance(record.get("version"), str)
            and bool(
                re.fullmatch(
                    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
                    r"(?:-[0-9A-Za-z.-]+)?",
                    str(record.get("version")),
                )
            )
            and is_nonempty_string(record.get("name_en"))
            and is_nonempty_string(record.get("name_zh"))
            and bool(re.search(r"[\u3400-\u9fff]", str(record.get("name_zh"))))
            and is_nonempty_string(record.get("formula"))
            and not re.search(r"[a-z]-[a-z]", str(record.get("formula")))
            and is_string_list(record.get("inputs"), allow_empty=False)
            and not has_duplicates(record.get("inputs"))
            and all(
                bool(re.fullmatch(r"[a-z][a-z0-9_]*", input_name))
                for input_name in record.get("inputs", [])
            )
            and is_nonempty_string(record.get("unit"))
            and record.get("direction") in METRIC_DIRECTIONS
            and is_nonempty_string(record.get("denominator"))
            and is_nonempty_string(record.get("owner"))
            and isinstance(record.get("minimum_sample"), int)
            and not isinstance(record.get("minimum_sample"), bool)
            and int(record.get("minimum_sample", 0)) > 0
            and is_string_list(record.get("exclusions"))
        )
        if not scalar_fields_valid:
            report.error(
                "reasoning_metric_registry",
                f"{metric_id} has invalid version, text, direction, exclusions, or minimum_sample",
                f"{metric_id} 的版本、文本、方向、排除项或 minimum_sample 无效",
            )

        probes = record.get("required_probes")
        probes_valid = (
            is_string_list(probes, allow_empty=False)
            and not has_duplicates(probes)
            and set(probes).issubset(set(REQUIRED_PROBES))
        )
        if not probes_valid:
            report.error(
                "reasoning_metric_registry",
                f"{metric_id} references invalid, duplicate, or empty probes",
                f"{metric_id} 引用了无效、重复或空探针",
            )
        elif (
            "outcome" in metric_id
            or "false_release" in metric_id
            or "correctness" in metric_id
        ) and "PROBE_0013" not in probes:
            report.error(
                "reasoning_metric_registry",
                f"outcome-backed metric {metric_id} must require PROBE_0013",
                f"后验支撑指标 {metric_id} 必须依赖 PROBE_0013",
            )

    duplicates = sorted(
        metric_id for metric_id, count in Counter(observed_ids).items() if count > 1
    )
    universal = registry.get("universal_required_probes")
    required_buckets = registry.get("required_bucket_dimensions")
    coverage = registry.get("coverage")
    coverage_valid = (
        is_string_list(universal, allow_empty=False)
        and not has_duplicates(universal)
        and set(universal) == UNIVERSAL_REASONING_PROBES
        and is_string_list(required_buckets, allow_empty=False)
        and not has_duplicates(required_buckets)
        and set(required_buckets)
        == {"scene_id", "risk_level", "execution_mode"}
        and isinstance(coverage, dict)
        and coverage.get("profile") == "mvp_core"
        and is_nonempty_string(coverage.get("profile_en"))
        and is_nonempty_string(coverage.get("profile_zh"))
        and bool(re.search(r"[\u3400-\u9fff]", str(coverage.get("profile_zh", ""))))
        and all(
            is_string_list(coverage.get(field), allow_empty=False)
            and not has_duplicates(coverage.get(field))
            for field in ("implemented", "planned", "gate_eligible")
        )
        and set(coverage.get("implemented", [])) == set(observed_ids)
        and set(coverage.get("gate_eligible", [])).issubset(set(observed_ids))
        and not set(coverage.get("planned", [])) & set(observed_ids)
    )
    if not coverage_valid:
        report.error(
            "reasoning_metric_registry",
            "metric registry universal probes or MVP coverage declaration is invalid",
            "指标注册表通用探针或 MVP 覆盖声明无效",
        )
    probes_path = skill_dir / RUNTIME_PROTOCOLS["PATTERN_0052"]["reference"]
    probe_document = (
        probes_path.read_text(encoding="utf-8") if probes_path.is_file() else ""
    )
    documented_ids = document_metric_ids(probe_document)
    exported_ids = exported_metric_function_names(
        skill_dir / "runtime" / "reasoning_metrics.py"
    )
    expected_ids = documented_ids | exported_ids
    missing = sorted(expected_ids - set(observed_ids))
    unknown = sorted(set(observed_ids) - expected_ids)
    if duplicates or missing or unknown:
        report.error(
            "reasoning_metric_registry",
            f"metric IDs duplicates={duplicates}, missing={missing}, unknown={unknown}",
            f"指标 ID 重复={duplicates}，缺失={missing}，未知={unknown}",
        )


def validate_probe_registry(
    skill_dir: pathlib.Path, report: ValidationReport
) -> None:
    path = skill_dir / "runtime" / "probe_registry.json"
    registry = load_json_resource(path, report, "reasoning_probe_registry")
    if registry is None:
        return
    metadata_valid = (
        registry.get("schema_version") == "1.0.0"
        and is_nonempty_string(registry.get("name_en"))
        and is_nonempty_string(registry.get("name_zh"))
        and bool(re.search(r"[\u3400-\u9fff]", str(registry.get("name_zh", ""))))
        and is_nonempty_string(registry.get("description_en"))
        and is_nonempty_string(registry.get("description_zh"))
        and bool(
            re.search(r"[\u3400-\u9fff]", str(registry.get("description_zh", "")))
        )
    )
    if not metadata_valid:
        report.error(
            "reasoning_probe_registry",
            "probe registry metadata is invalid",
            "探针注册表元数据无效",
        )
    records = registry.get("probes")
    if not isinstance(records, list):
        report.error(
            "reasoning_probe_registry",
            "probe registry must contain probes",
            "探针注册表必须包含 probes",
        )
        return
    required_fields = {
        "probe_id",
        "version",
        "name_en",
        "name_zh",
        "owner",
        "trigger_event_types",
        "required_capture_fields",
        "output_event_type",
        "disposition",
    }
    observed: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            report.error(
                "reasoning_probe_registry",
                f"invalid probe definition {record}",
                f"无效探针定义 {record}",
            )
            continue
        probe_id = str(record.get("probe_id", ""))
        observed.append(probe_id)
        valid = (
            required_fields <= set(record)
            and re.fullmatch(r"PROBE_\d{4}", probe_id) is not None
            and re.fullmatch(r"\d+\.\d+\.\d+", str(record.get("version", "")))
            is not None
            and is_nonempty_string(record.get("name_en"))
            and is_nonempty_string(record.get("name_zh"))
            and bool(re.search(r"[\u3400-\u9fff]", str(record.get("name_zh", ""))))
            and is_nonempty_string(record.get("owner"))
            and is_string_list(record.get("trigger_event_types"), allow_empty=False)
            and not has_duplicates(record.get("trigger_event_types"))
            and is_string_list(record.get("required_capture_fields"), allow_empty=False)
            and not has_duplicates(record.get("required_capture_fields"))
            and is_nonempty_string(record.get("output_event_type"))
            and is_nonempty_string(record.get("disposition"))
        )
        if not valid:
            report.error(
                "reasoning_probe_registry",
                f"probe definition is incomplete or invalid: {probe_id}",
                f"探针定义不完整或无效：{probe_id}",
            )
    if set(observed) != set(REQUIRED_PROBES) or has_duplicates(observed):
        report.error(
            "reasoning_probe_registry",
            "probe registry IDs must exactly match the canonical probe catalog",
            "探针注册表 ID 必须与规范探针目录完全一致",
        )


def validate_probe_dependency_matrix(
    skill_dir: pathlib.Path, report: ValidationReport
) -> None:
    path = skill_dir / "runtime" / "probe_dependency_matrix.json"
    matrix = load_json_resource(path, report, "reasoning_probe_dependencies")
    if matrix is None:
        return
    universal = matrix.get("universal_required_probes")
    universal_valid = (
        is_string_list(universal, allow_empty=False)
        and not has_duplicates(universal)
        and set(universal) == UNIVERSAL_REASONING_PROBES
    )
    if (
        matrix.get("schema_version") != "1.0.0"
        or not is_nonempty_string(matrix.get("name_en"))
        or not is_nonempty_string(matrix.get("name_zh"))
        or not re.search(r"[\u3400-\u9fff]", str(matrix.get("name_zh", "")))
        or not is_nonempty_string(matrix.get("description_en"))
        or not is_nonempty_string(matrix.get("description_zh"))
        or not re.search(
            r"[\u3400-\u9fff]", str(matrix.get("description_zh", ""))
        )
        or not universal_valid
    ):
        report.error(
            "reasoning_probe_dependencies",
            "probe dependency matrix metadata or universal probes are invalid",
            "探针依赖矩阵元数据或通用探针无效",
        )

    entries = matrix.get("entries")
    if not isinstance(entries, list):
        report.error(
            "reasoning_probe_dependencies",
            "probe dependency matrix must contain entries",
            "探针依赖矩阵必须包含 entries",
        )
        return
    expected_modes = set(MODE_REQUIRED_PROBE_BASELINES)
    observed_modes: list[str] = []
    mode_requirements: dict[str, set[str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            report.error(
                "reasoning_probe_dependencies",
                f"invalid dependency entry {entry}",
                f"无效依赖记录 {entry}",
            )
            continue
        mode = str(entry.get("mode", ""))
        observed_modes.append(mode)
        required = entry.get("required_probes")
        conditional = entry.get("conditional_probes")
        valid_required = (
            is_string_list(required, allow_empty=False)
            and not has_duplicates(required)
            and set(required).issubset(set(REQUIRED_PROBES))
        )
        valid_conditional = (
            isinstance(conditional, dict)
            and all(
                isinstance(probe_id, str)
                and probe_id in REQUIRED_PROBES
                and is_bilingual_text(condition)
                for probe_id, condition in conditional.items()
            )
        )
        required_set = set(required) if valid_required else set()
        conditional_set = set(conditional) if valid_conditional else set()
        baseline = MODE_REQUIRED_PROBE_BASELINES.get(mode, set())
        if (
            not valid_required
            or not valid_conditional
            or not baseline.issubset(required_set)
            or bool(required_set & conditional_set)
            or not is_nonempty_string(entry.get("name_en"))
            or not is_nonempty_string(entry.get("name_zh"))
            or not re.search(r"[\u3400-\u9fff]", str(entry.get("name_zh", "")))
        ):
            report.error(
                "reasoning_probe_dependencies",
                f"invalid probe dependency entry for {mode}",
                f"{mode} 的探针依赖记录无效",
            )
        elif mode in expected_modes:
            mode_requirements[mode] = required_set
    if set(observed_modes) != expected_modes or len(observed_modes) != len(
        expected_modes
    ):
        report.error(
            "reasoning_probe_dependencies",
            f"dependency modes expected {sorted(expected_modes)}, observed {observed_modes}",
            f"依赖模式应为 {sorted(expected_modes)}，实际为 {observed_modes}",
        )

    observability_root = skill_dir / "references" / "patterns" / "reasoning"
    for mode, filename in MODE_OBSERVABILITY_FILES.items():
        path = observability_root / filename
        content = path.read_text(encoding="utf-8") if path.is_file() else ""
        section = markdown_section(
            content, "### Required Probe Coverage / 必需探针覆盖"
        )
        documented = set(re.findall(r"PROBE_\d{4}", section or ""))
        required_for_mode = mode_requirements.get(mode)
        if section is None or required_for_mode is None:
            report.error(
                "reasoning_probe_dependencies",
                f"cannot validate matrix-driven probe coverage for {mode} in {filename}",
                f"无法校验 {filename} 中 {mode} 的矩阵驱动探针覆盖",
            )
            continue
        missing = sorted(required_for_mode - documented)
        if missing:
            report.error(
                "reasoning_probe_dependencies",
                f"{filename} lacks matrix-required probes for {mode}: {missing}",
                f"{filename} 缺少 {mode} 的矩阵必需探针：{missing}",
            )


def validate_registry_shape(
    registry: dict[str, object],
    skill_dir: pathlib.Path,
    report: ValidationReport,
) -> None:
    required = {
        "schema_version",
        "skill",
        "upstream_sources",
        "allowed_values",
        "maturity_requirements",
        "governance_rules",
        "failure_mode_refs",
        "capabilities",
        "topologies",
        "patterns",
        "cells",
    }
    missing = sorted(required - set(registry))
    if missing:
        report.error(
            "registry_shape",
            f"missing top-level keys {missing}",
            f"缺少顶层键 {missing}",
        )
        return

    capabilities = registry.get("capabilities", [])
    topologies = registry.get("topologies", [])
    patterns = registry.get("patterns", [])
    cells = registry.get("cells", [])
    governance_rules = registry.get("governance_rules", [])
    failure_mode_refs = registry.get("failure_mode_refs", [])
    collections = (
        capabilities,
        topologies,
        patterns,
        cells,
        governance_rules,
        failure_mode_refs,
    )
    if not all(isinstance(items, list) for items in collections):
        report.error(
            "registry_shape",
            "registry record collections must be arrays",
            "注册表记录集合必须是数组",
        )
        return

    expected_counts = (
        ("capabilities", capabilities, 7),
        ("topologies", topologies, 6),
        ("cells", cells, 42),
    )
    for label, records, expected in expected_counts:
        if len(records) != expected:
            report.error(
                "registry_shape",
                f"{label} expected {expected}, observed {len(records)}",
                f"{label} 应为 {expected}，实际为 {len(records)}",
            )

    for label, records, code in (
        ("capability", capabilities, "duplicate_capability_id"),
        ("topology", topologies, "duplicate_topology_id"),
        ("pattern", patterns, "duplicate_pattern_id"),
        ("cell", cells, "duplicate_cell_id"),
        ("governance rule", governance_rules, "registry_shape"),
        ("failure mode", failure_mode_refs, "registry_shape"),
    ):
        for duplicate in duplicate_values(records, "id"):
            report.error(
                code,
                f"duplicate {label} id {duplicate}",
                f"重复的 {label} ID {duplicate}",
            )

    if len(governance_rules) < 3:
        report.error(
            "registry_shape",
            "at least three explicit governance rules are required",
            "至少需要三条明确治理规则",
        )

    for field in ("coordinate", "cell_key", "design_path", "observability_path"):
        for duplicate in duplicate_values(cells, field):
            report.error(
                "registry_shape",
                f"duplicate cell {field} {duplicate}",
                f"重复的单元字段 {field}: {duplicate}",
            )

    allowed_values = registry.get("allowed_values", {})
    allowed_status = set(allowed_values.get("cell_status", []))
    allowed_maturity = set(allowed_values.get("maturity", []))
    allowed_source_kind = set(allowed_values.get("source_kind", []))
    maturity_requirements = registry.get("maturity_requirements", {})
    if (
        not isinstance(maturity_requirements, dict)
        or set(maturity_requirements) != allowed_maturity
    ):
        report.error(
            "registry_shape",
            "maturity requirements must cover every allowed maturity value",
            "成熟度要求必须覆盖每个允许的成熟度值",
        )
        maturity_requirements = {}
    pattern_ids = {pattern.get("id") for pattern in patterns}
    capability_by_id = {item.get("id"): item for item in capabilities}
    topology_by_id = {item.get("id"): item for item in topologies}
    expected_pairs = {
        (capability_id, topology_id)
        for capability_id in capability_by_id
        for topology_id in topology_by_id
    }
    observed_pairs: Counter[tuple[object, object]] = Counter()

    for cell in cells:
        cell_id = str(cell.get("id", "<missing>"))
        status = cell.get("status")
        maturity = cell.get("maturity")
        source_kind = cell.get("source_kind")
        if (
            status not in allowed_status
            or maturity not in allowed_maturity
            or source_kind not in allowed_source_kind
        ):
            report.error(
                "registry_shape",
                f"{cell_id} has invalid status, maturity, or source kind",
                f"{cell_id} 的状态、成熟度或来源类型无效",
            )

        capability_ref = cell.get("capability_ref")
        topology_ref = cell.get("topology_ref")
        capability = capability_by_id.get(capability_ref)
        topology = topology_by_id.get(topology_ref)
        if capability is None or topology is None:
            report.error(
                "registry_shape",
                f"{cell_id} references unknown capability or topology",
                f"{cell_id} 引用了未知能力或拓扑",
            )
        else:
            observed_pairs[(capability_ref, topology_ref)] += 1
            capability_key = str(capability.get("key"))
            topology_key = str(topology.get("key"))
            expected_fields = {
                "id": f"CELL_{capability_key.upper()}_{topology_key.upper()}",
                "coordinate": f"{capability_ref}__{topology_ref}",
                "cell_key": f"{capability_key}-{topology_key}",
                "design_path": (
                    f"references/patterns/{capability_key}/"
                    f"{capability_key}-{topology_key}.md"
                ),
                "observability_path": (
                    f"references/patterns/{capability_key}/"
                    f"{capability_key}-{topology_key}-observability.md"
                ),
            }
            for field, expected in expected_fields.items():
                if cell.get(field) != expected:
                    report.error(
                        "registry_shape",
                        f"{cell_id} {field} expected {expected}",
                        f"{cell_id} 的 {field} 应为 {expected}",
                    )

        for numeric_field in ("local_evidence_count", "domain_count"):
            value = cell.get(numeric_field)
            if type(value) is not int or value < 0:
                report.error(
                    "registry_shape",
                    f"{cell_id} {numeric_field} must be a non-negative integer",
                    f"{cell_id} 的 {numeric_field} 必须是非负整数",
                )
        requirement = maturity_requirements.get(maturity, {})
        minimum_cases = requirement.get("minimum_independent_cases", 0)
        if type(minimum_cases) is not int or minimum_cases < 0:
            report.error(
                "registry_shape",
                f"invalid maturity requirement for {maturity}",
                f"成熟度 {maturity} 的要求无效",
            )
            minimum_cases = 0
        if maturity in {"validated", "operational"}:
            evidence_count = cell.get("local_evidence_count", 0)
            independent_case_count = cell.get("independent_case_count", 0)
            promotion_ready = (
                type(evidence_count) is int
                and evidence_count >= minimum_cases
                and type(independent_case_count) is int
                and independent_case_count >= minimum_cases
                and (
                    not requirement.get("failure_path_check_required")
                    or cell.get("failure_path_checked") is True
                )
            )
            if maturity == "operational":
                promotion_ready = (
                    promotion_ready
                    and (
                        not requirement.get("recurring_monitoring_required")
                        or cell.get("recurring_monitoring") is True
                    )
                    and (
                        not requirement.get("owned_thresholds_required")
                        or bool(str(cell.get("threshold_owner", "")).strip())
                    )
                )
            if not promotion_ready:
                report.error(
                    "registry_shape",
                    f"{cell_id} does not satisfy {maturity} promotion gates",
                    f"{cell_id} 不满足 {maturity} 晋升门槛",
                )

        design_path = skill_dir / str(cell.get("design_path", ""))
        observability_path = skill_dir / str(cell.get("observability_path", ""))
        if not design_path.is_file():
            report.error(
                "missing_design_file",
                f"{cell_id} design file not found: {design_path}",
                f"{cell_id} 的设计文件不存在：{design_path}",
            )
        if not observability_path.is_file():
            report.error(
                "missing_observability_file",
                f"{cell_id} observability file not found: {observability_path}",
                f"{cell_id} 的可观测性文件不存在：{observability_path}",
            )

        if status == "named":
            if source_kind not in {"paper_v2", "local_extension"}:
                report.error(
                    "registry_shape",
                    f"{cell_id} named cell has invalid source kind {source_kind}",
                    f"{cell_id} 命名单元的来源类型 {source_kind} 无效",
                )
            if not source_kind or not cell.get("source_name_en") and source_kind == "paper_v2":
                report.error(
                    "missing_provenance",
                    f"{cell_id} is missing named-pattern provenance",
                    f"{cell_id} 缺少命名模式来源",
                )
            if cell.get("pattern_ref") not in pattern_ids:
                report.error(
                    "registry_shape",
                    f"{cell_id} references an unknown pattern id {cell.get('pattern_ref')}",
                    f"{cell_id} 引用了未知模式 ID {cell.get('pattern_ref')}",
                )
        else:
            if source_kind != "paper_blank" or maturity != "seed":
                report.error(
                    "registry_shape",
                    f"{cell_id} extension candidate must be a paper_blank seed",
                    f"{cell_id} 扩展候选必须是 paper_blank 种子",
                )
            if cell.get("pattern_ref") is not None:
                report.error(
                    "registry_shape",
                    f"{cell_id} extension candidate must not have a pattern id",
                    f"{cell_id} 扩展候选不得拥有模式 ID",
                )

    missing_pairs = expected_pairs - set(observed_pairs)
    duplicate_pairs = sorted(pair for pair, count in observed_pairs.items() if count > 1)
    if missing_pairs or duplicate_pairs:
        report.error(
            "registry_shape",
            f"7x6 coverage has missing pairs {sorted(missing_pairs)} or duplicates {duplicate_pairs}",
            f"7x6 覆盖存在缺失坐标 {sorted(missing_pairs)} 或重复坐标 {duplicate_pairs}",
        )

    upstream_sources = registry.get("upstream_sources", [])
    if len(upstream_sources) != 1 or not isinstance(upstream_sources[0], dict):
        report.error(
            "registry_shape",
            "exactly one pinned upstream source is required",
            "必须且只能有一个固定上游来源",
        )
    else:
        upstream = upstream_sources[0]
        named_count = upstream.get("named_pattern_count")
        blank_count = upstream.get("blank_cell_count")
        source_counts = Counter(cell.get("source_kind") for cell in cells)
        valid_counts = type(named_count) is int and type(blank_count) is int
        if (
            upstream.get("version") != "v2"
            or not valid_counts
            or named_count != 28
            or blank_count != 14
            or source_counts["paper_v2"] != named_count
            or source_counts["local_extension"] != 2
            or source_counts["paper_blank"] + source_counts["local_extension"] != blank_count
        ):
            report.error(
                "registry_shape",
                "provenance counts must remain 28 named, 14 blank, 2 promoted, and 12 candidates",
                "来源统计必须保持 28 个命名、14 个空白、2 个晋升和 12 个候选",
            )

    known_coordinates = {str(cell.get("coordinate")) for cell in cells}
    for rule in governance_rules:
        reference = skill_dir / str(rule.get("reference", ""))
        if (
            not re.fullmatch(r"GOV_RULE_\d{4}", str(rule.get("id", "")))
            or not rule.get("name_en")
            or not rule.get("name_zh")
            or not reference.is_file()
        ):
            report.error(
                "registry_shape",
                f"invalid governance rule {rule.get('id')}",
                f"治理规则 {rule.get('id')} 无效",
            )

    failure_file = skill_dir / "references" / "failure-modes.md"
    failure_text = failure_file.read_text(encoding="utf-8") if failure_file.is_file() else ""
    declared_failures = {str(item.get("id")) for item in failure_mode_refs}
    documented_failures = set(re.findall(r"FAIL_\d{4}", failure_text))
    if declared_failures != documented_failures:
        report.error(
            "registry_shape",
            "failure-mode references do not match failure-modes.md",
            "失败模式引用与 failure-modes.md 不一致",
        )
    for item in failure_mode_refs:
        reference = skill_dir / str(item.get("reference", ""))
        if item.get("coordinate") not in known_coordinates or not reference.is_file():
            report.error(
                "registry_shape",
                f"invalid failure-mode reference {item.get('id')}",
                f"失败模式引用 {item.get('id')} 无效",
            )


def parse_matrix_records(
    matrix: str,
    capabilities: list[dict[str, object]],
    topologies: list[dict[str, object]],
) -> dict[tuple[object, object], tuple[str, str]]:
    capability_labels = {
        f"{item.get('name_en')} / {item.get('name_zh')}": item.get("id")
        for item in capabilities
    }
    records: dict[tuple[object, object], tuple[str, str]] = {}
    for line in matrix.splitlines():
        if not line.startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) != len(topologies) + 1:
            continue
        capability_id = capability_labels.get(columns[0])
        if capability_id is None:
            continue
        for topology, raw_cell in zip(topologies, columns[1:]):
            match = re.fullmatch(r"\[(?P<label>.+)\]\((?P<path>[^)]+)\)", raw_cell)
            if match:
                records[(capability_id, topology.get("id"))] = (
                    match.group("label"),
                    match.group("path"),
                )
    return records


def parse_catalog_records(catalog: str) -> tuple[dict[str, tuple[str, str]], set[str]]:
    named: dict[str, tuple[str, str]] = {}
    extensions: set[str] = set()
    for line in catalog.splitlines():
        if line.startswith("|"):
            columns = [column.strip() for column in line.strip().strip("|").split("|")]
            if len(columns) == 3:
                cell_key = columns[0].split(" / ", 1)[0]
                if re.fullmatch(r"[a-z]+-[a-z]+", cell_key):
                    named[cell_key] = (columns[1], columns[2])
        match = re.match(r"^- (?P<cell_key>[a-z]+-[a-z]+) / ", line)
        if match:
            extensions.add(match.group("cell_key"))
    return named, extensions


def parse_guide_records(
    guide: str,
    topologies: list[dict[str, object]],
) -> dict[object, tuple[str, str, str]]:
    topology_labels = {
        f"{item.get('name_en')} / {item.get('name_zh')}": item.get("id")
        for item in topologies
    }
    records: dict[object, tuple[str, str, str]] = {}
    for line in guide.splitlines():
        if not line.startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) != 3:
            continue
        topology_id = topology_labels.get(columns[0])
        match = re.fullmatch(r"\[(?P<label>.+)\]\((?P<path>[^)]+)\)", columns[2])
        if topology_id is not None and match:
            records[topology_id] = (
                columns[1],
                match.group("label"),
                match.group("path"),
            )
    return records


def validate_markdown_views(
    registry: dict[str, object],
    skill_dir: pathlib.Path,
    report: ValidationReport,
) -> None:
    matrix = (skill_dir / "references" / "matrix-index.md").read_text(encoding="utf-8")
    catalog = (skill_dir / "references" / "pattern-catalog.md").read_text(encoding="utf-8")
    capabilities = registry.get("capabilities", [])
    topologies = registry.get("topologies", [])
    capability_by_id = {item.get("id"): item for item in capabilities}
    topology_by_id = {item.get("id"): item for item in topologies}
    matrix_records = parse_matrix_records(matrix, capabilities, topologies)
    catalog_named, catalog_extensions = parse_catalog_records(catalog)

    for cell in registry.get("cells", []):
        cell_key = str(cell.get("cell_key", ""))
        capability = capability_by_id.get(cell.get("capability_ref"), {})
        topology = topology_by_id.get(cell.get("topology_ref"), {})
        expected_label = f"{cell.get('local_name_en')} / {cell.get('local_name_zh')}"
        expected_path = str(cell.get("design_path", "")).removeprefix("references/")
        matrix_record = matrix_records.get(
            (cell.get("capability_ref"), cell.get("topology_ref"))
        )
        if matrix_record != (expected_label, expected_path):
            report.error(
                "matrix_drift",
                f"{cell_key} does not match matrix-index.md",
                f"{cell_key} 与 matrix-index.md 不一致",
            )

        if cell.get("status") == "named":
            catalog_record = catalog_named.get(cell_key)
            catalog_matches = bool(
                catalog_record
                and catalog_record[0].startswith(expected_label)
                and str(cell.get("diagnostic_use_en")) in catalog_record[1]
                and str(cell.get("diagnostic_use_zh")) in catalog_record[1]
            )
        else:
            catalog_matches = cell_key in catalog_extensions and cell_key not in catalog_named
        if not catalog_matches:
            report.error(
                "catalog_drift",
                f"{cell_key} does not match pattern-catalog.md",
                f"{cell_key} 与 pattern-catalog.md 不一致",
            )

        design_path = skill_dir / str(cell.get("design_path", ""))
        if design_path.is_file():
            content = design_path.read_text(encoding="utf-8")
            for field in DESIGN_FIELDS:
                if field not in content:
                    report.error(
                        "missing_design_field",
                        f"{cell_key} missing {field}",
                        f"{cell_key} 缺少 {field}",
                    )
            expected_header = f"# {expected_label}"
            expected_cell = (
                f"Cell / 交织点: {cell_key} / {capability.get('name_zh')} x "
                f"{topology.get('name_zh')}"
            )
            expected_capability = (
                f"Capability / 能力: {capability.get('name_en')} / "
                f"{capability.get('name_zh')}"
            )
            expected_mode = (
                f"Mode / 模式: {topology.get('name_en')} / {topology.get('name_zh')}"
            )
            status_match = re.search(r"(?m)^- 状态 / Status:\s*(.*)$", content)
            expected_status = (
                "Named candidate"
                if cell.get("status") == "named"
                else "Extension candidate"
            )
            header_matches = (
                content.startswith(expected_header + "\n")
                and expected_cell in content
                and expected_capability in content
                and expected_mode in content
                and status_match is not None
                and expected_status in status_match.group(1)
            )
            aliases = list(cell.get("aliases_en", [])) + list(cell.get("aliases_zh", []))
            if not header_matches or any(alias not in content for alias in aliases):
                report.error(
                    "catalog_drift",
                    f"{cell_key} design header or aliases drift from registry",
                    f"{cell_key} 的设计文件头或别名与注册表不一致",
                )

        observability_path = skill_dir / str(cell.get("observability_path", ""))
        if observability_path.is_file():
            content = observability_path.read_text(encoding="utf-8")
            for field in OBSERVABILITY_FIELDS:
                if field not in content:
                    report.error(
                        "missing_observability_field",
                        f"{cell_key} missing {field}",
                        f"{cell_key} 缺少 {field}",
                    )

    for capability in capabilities:
        guide_path = skill_dir / str(capability.get("guide_path", ""))
        expected_title = (
            f"# {capability.get('name_en')} Cells Introduction / "
            f"{capability.get('name_zh')}交织点导论"
        )
        guide = guide_path.read_text(encoding="utf-8") if guide_path.is_file() else ""
        guide_records = parse_guide_records(guide, topologies)
        capability_cells = {
            cell.get("topology_ref"): cell
            for cell in registry.get("cells", [])
            if cell.get("capability_ref") == capability.get("id")
        }
        guide_matches = len(guide_records) == len(topologies)
        for topology in topologies:
            cell = capability_cells.get(topology.get("id"), {})
            expected_status = (
                "Named / 已命名"
                if cell.get("status") == "named"
                else "Extension / 扩展"
            )
            expected_record = (
                expected_status,
                f"{cell.get('local_name_en')} / {cell.get('local_name_zh')}",
                pathlib.PurePosixPath(str(cell.get("design_path", ""))).name,
            )
            if guide_records.get(topology.get("id")) != expected_record:
                guide_matches = False
        named_count = sum(
            cell.get("status") == "named" for cell in capability_cells.values()
        )
        extension_count = len(topologies) - named_count
        summary = (
            f"This row currently has {named_count} named pattern candidates and "
            f"{extension_count} extension candidate"
        )
        if extension_count != 1:
            summary += "s"
        summary += "."
        if (
            not guide.startswith(expected_title + "\n")
            or not guide_matches
            or summary not in guide
        ):
            report.error(
                "catalog_drift",
                f"{capability.get('id')} guide does not match registry",
                f"{capability.get('id')} 的导论与注册表不一致",
            )


def validate_relative_links(skill_dir: pathlib.Path, report: ValidationReport) -> None:
    for path in sorted(skill_dir.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(content):
            target = match.group("target").strip().strip("<>")
            if re.match(r"^(?:https?://|mailto:|#)", target):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = path.parent / target
            if not resolved.exists():
                line = content.count("\n", 0, match.start()) + 1
                relative = path.relative_to(skill_dir).as_posix()
                report.error(
                    "broken_link",
                    f"{relative}:{line} -> {target}",
                    f"{relative}:{line} 指向不存在的 {target}",
                )


def validate_analysis_contracts(skill_dir: pathlib.Path, report: ValidationReport) -> None:
    eir_path = skill_dir / "references" / "eir-schema.md"
    eir = eir_path.read_text(encoding="utf-8")
    for heading in EIR_HEADINGS:
        if heading not in eir:
            report.error(
                "eir_contract",
                f"missing heading {heading}",
                f"缺少标题 {heading}",
            )

    evaluation_path = skill_dir / "references" / "evaluation-governance.md"
    evaluation = evaluation_path.read_text(encoding="utf-8")
    for key in EVALUATION_KEYS:
        if not re.search(rf"(?m)^\s{{2}}{re.escape(key)}:\s*$", evaluation):
            report.error(
                "evaluation_contract",
                f"evaluation output missing {key}",
                f"评价输出缺少 {key}",
            )

    for path in sorted(skill_dir.rglob("*.md")):
        if path.name == "trace.md":
            continue
        content = path.read_text(encoding="utf-8")
        if has_bundled_trace_write(content):
            relative = path.relative_to(skill_dir).as_posix()
            report.error(
                "bundled_trace_write",
                f"{relative} writes normal-use Trace to bundled history",
                f"{relative} 将普通运行 Trace 写入 Skill 内置历史",
            )


def validate_runtime_imports(
    skill_dir: pathlib.Path, report: ValidationReport
) -> dict[str, ModuleType]:
    """Import the reference runtime in an isolated package namespace. / 在隔离包名下导入参考运行时。"""

    runtime_dir = skill_dir / "runtime"
    init_path = runtime_dir / "__init__.py"
    package_name = "_harness_reasoning_runtime_validation"
    modules: dict[str, ModuleType] = {}
    previous_bytecode_setting = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        for name in list(sys.modules):
            if name == package_name or name.startswith(package_name + "."):
                sys.modules.pop(name, None)
        importlib.invalidate_caches()
        spec = importlib.util.spec_from_file_location(
            package_name,
            init_path,
            submodule_search_locations=[str(runtime_dir)],
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot create package spec for {init_path}")
        package = importlib.util.module_from_spec(spec)
        sys.modules[package_name] = package
        spec.loader.exec_module(package)
        modules["package"] = package
        for module_name in (
            "reasoning_router",
            "reasoning_metrics",
            "reasoning_chain_factory",
            "plan_execution",
        ):
            modules[module_name] = importlib.import_module(
                f"{package_name}.{module_name}"
            )
    except Exception as error:
        report.error(
            "reasoning_runtime_import",
            f"reference runtime import smoke failed: {type(error).__name__}: {error}",
            f"参考运行时导入冒烟失败：{type(error).__name__}：{error}",
        )
    finally:
        sys.dont_write_bytecode = previous_bytecode_setting
        for name in list(sys.modules):
            if name == package_name or name.startswith(package_name + "."):
                sys.modules.pop(name, None)

    for module_name, required_exports in RUNTIME_REQUIRED_EXPORTS.items():
        module = modules.get(module_name)
        if module is None:
            continue
        declared = getattr(module, "__all__", None)
        declared_valid = isinstance(declared, (list, tuple)) and all(
            isinstance(item, str) for item in declared
        )
        declared_set = set(declared) if declared_valid else set()
        missing_required = sorted(
            export
            for export in required_exports
            if export not in declared_set or not hasattr(module, export)
        )
        missing_declared = sorted(
            export for export in declared_set if not hasattr(module, export)
        )
        if missing_required or missing_declared:
            report.error(
                "reasoning_runtime_import",
                f"runtime module {module_name} lacks required exports {missing_required} or declared exports {missing_declared}",
                f"运行时模块 {module_name} 缺少必需导出 {missing_required} 或已声明导出 {missing_declared}",
            )
    return modules


def enum_class_values(value: object) -> list[str] | None:
    """Return string Enum values or None for a non-enum. / 返回字符串枚举值，非枚举返回 None。"""

    if not isinstance(value, type) or not issubclass(value, Enum):
        return None
    values = [member.value for member in value]
    if not all(isinstance(item, str) for item in values):
        return None
    return values


def validate_runtime_schema_enums(
    modules: dict[str, ModuleType],
    schemas: dict[str, dict[str, object]],
    report: ValidationReport,
) -> None:
    """Cross-check imported runtime enums against normative schemas. / 将运行时枚举与规范 Schema 交叉校验。"""

    bindings = (
        ("package", "WorkflowState", "workflow_state"),
        ("package", "ValidationStatus", "validation_result"),
        ("reasoning_router", "ExecutionMode", "execution_mode"),
        ("reasoning_router", "PrimaryTopology", "primary_topology"),
    )
    for module_name, export_name, canonical_name in bindings:
        module = modules.get(module_name)
        if module is None:
            continue
        observed = enum_class_values(getattr(module, export_name, None))
        expected = list(CANONICAL_RUNTIME_ENUMS[canonical_name])
        if observed != expected:
            report.error(
                "reasoning_runtime_schema_enums",
                f"{module_name}.{export_name} expected {expected}, observed {observed}",
                f"{module_name}.{export_name} 应为 {expected}，实际为 {observed}",
            )

    risk_locations = (
        (
            "schemas/normalized-input.schema.json",
            "/$defs/RiskAssessment/properties/level",
        ),
        (
            "schemas/reasoning-contract.schema.json",
            "/$defs/Governance/properties/risk_level",
        ),
        ("schemas/reasoning-event.schema.json", "/properties/risk_level"),
    )
    risk_values: list[list[str]] = []
    for relative, pointer in risk_locations:
        schema = schemas.get(relative)
        if schema is None:
            continue
        try:
            risk_values.append(schema_enum_at(schema, pointer))
        except (KeyError, TypeError, ValueError) as error:
            report.error(
                "reasoning_runtime_schema_enums",
                f"cannot resolve risk enum at {relative}#{pointer}: {error}",
                f"无法解析 {relative}#{pointer} 的风险枚举：{error}",
            )
    if risk_values:
        expected_risk = risk_values[0]
        if any(values != expected_risk for values in risk_values[1:]):
            report.error(
                "reasoning_runtime_schema_enums",
                f"risk enums drift across schemas: {risk_values}",
                f"不同 Schema 的风险枚举漂移：{risk_values}",
            )
        for module_name in ("package", "reasoning_router"):
            module = modules.get(module_name)
            if module is None:
                continue
            observed = enum_class_values(getattr(module, "RiskLevel", None))
            if observed != expected_risk:
                report.error(
                    "reasoning_runtime_schema_enums",
                    f"{module_name}.RiskLevel expected {expected_risk}, observed {observed}",
                    f"{module_name}.RiskLevel 应为 {expected_risk}，实际为 {observed}",
                )


def validate_runtime_protocols(
    registry: dict[str, object],
    skill_dir: pathlib.Path,
    report: ValidationReport,
) -> None:
    patterns = {
        str(pattern.get("id")): pattern
        for pattern in registry.get("patterns", [])
        if isinstance(pattern, dict)
    }

    for pattern_id, expected in RUNTIME_PROTOCOLS.items():
        pattern = patterns.get(pattern_id)
        reference = skill_dir / expected["reference"]
        if (
            pattern is None
            or pattern.get("name_en") != expected["name_en"]
            or pattern.get("name_zh") != expected["name_zh"]
            or pattern.get("source_kind") != "local_seed"
            or pattern.get("status") != "draft"
            or pattern.get("reference") != expected["reference"]
            or pattern.get("source_version") != expected["source_version"]
            or pattern.get("source_draft_id") != expected["source_draft_id"]
            or set(pattern.get("matrix_coordinates", []))
            != expected["matrix_coordinates"]
            or not reference.is_file()
        ):
            report.error(
                "runtime_protocol_registry",
                f"{pattern_id} runtime protocol registration is invalid",
                f"{pattern_id} 运行协议注册无效",
            )

    execution_path = skill_dir / RUNTIME_PROTOCOLS["PATTERN_0051"]["reference"]
    execution = execution_path.read_text(encoding="utf-8") if execution_path.is_file() else ""
    for marker in EXECUTION_CONTRACT_MARKERS:
        if marker not in execution:
            report.error(
                "reasoning_execution_contract",
                f"reasoning execution protocol missing {marker}",
                f"推理执行协议缺少 {marker}",
            )

    execution_version = RUNTIME_PROTOCOLS["PATTERN_0051"]["source_version"]
    if f"Version / 版本: `{execution_version}`" not in execution:
        report.error(
            "reasoning_execution_contract",
            f"reasoning execution protocol must declare version {execution_version}",
            f"推理执行协议必须声明版本 {execution_version}",
        )
    validate_budget_profile_table(execution, report)
    forbidden_execution_phrases = {
        "Answer emitted with confidence above threshold.": "confidence-only release",
        "max_iterations: 0": "zero iteration limit",
        "report best surviving hypothesis / 迭代或 token 预算触顶": (
            "unverified hypothesis release on exhaustion"
        ),
    }
    for phrase, meaning in forbidden_execution_phrases.items():
        if phrase in execution:
            report.error(
                "reasoning_execution_semantics",
                f"reasoning protocol retains unsafe {meaning}",
                f"推理协议仍包含不安全语义：{meaning}",
            )

    probes_path = skill_dir / RUNTIME_PROTOCOLS["PATTERN_0052"]["reference"]
    probes = probes_path.read_text(encoding="utf-8") if probes_path.is_file() else ""
    for marker in OBSERVABILITY_CONTRACT_MARKERS:
        if marker not in probes:
            report.error(
                "observability_probe_contract",
                f"observability probe protocol missing {marker}",
                f"可观测性探针协议缺少 {marker}",
            )

    probes_version = RUNTIME_PROTOCOLS["PATTERN_0052"]["source_version"]
    if f"Version / 版本: `{probes_version}`" not in probes:
        report.error(
            "observability_probe_contract",
            f"observability probe protocol must declare version {probes_version}",
            f"可观测性探针协议必须声明版本 {probes_version}",
        )

    catalog_rows = markdown_table_rows(probes, "| ID and name / ID 与名称")
    documented_probe_ids: list[str] = []
    catalog_structure_valid = (
        len(catalog_rows) == len(REQUIRED_PROBES) + 2
        and bool(catalog_rows)
        and catalog_rows[0]
        == [
            "ID and name / ID 与名称",
            "Trigger and required capture / 触发与必采集",
            "Signals and gates / 信号与门控",
            "Primary metrics / 主要指标",
        ]
        and all(len(row) == 4 for row in catalog_rows)
        and all(
            re.fullmatch(r":?-{3,}:?", cell) for cell in catalog_rows[1]
        )
    )
    if catalog_structure_valid:
        for row in catalog_rows[2:]:
            match = re.fullmatch(
                r"`(PROBE_\d{4})`\s+.+",
                row[0],
            )
            if match and is_bilingual_text(row[0]):
                documented_probe_ids.append(match.group(1))
            else:
                catalog_structure_valid = False
    documented_probes = Counter(documented_probe_ids)
    expected_probe_counts = Counter({probe_id: 1 for probe_id in REQUIRED_PROBES})
    if not catalog_structure_valid or documented_probes != expected_probe_counts:
        report.error(
            "observability_probe_catalog",
            f"probe catalog first column must declare every stable probe exactly once: {documented_probes}",
            f"探针目录首列必须准确且仅声明一次每个稳定探针：{documented_probes}",
        )

    stale_formulas = (
        "first_route_hit_rate =",
        "step_closure_rate = closed_steps",
        "hypothesis_elimination_efficiency =",
        "budget_utilization = actual_use / configured_limit",
    )
    if any(formula in probes for formula in stale_formulas):
        report.error(
            "reasoning_metric_semantics",
            "observability protocol retains a biased or unit-mixing formula",
            "可观测性协议仍包含有偏或混合单位的公式",
        )

    plan_execution_path = skill_dir / PLAN_EXECUTION_REFERENCE
    plan_execution = (
        plan_execution_path.read_text(encoding="utf-8")
        if plan_execution_path.is_file()
        else ""
    )
    if not plan_execution:
        report.error(
            "plan_execution_reference",
            f"missing Plan-and-Execute reference {PLAN_EXECUTION_REFERENCE}",
            f"缺少计划并执行参考文档 {PLAN_EXECUTION_REFERENCE}",
        )
    else:
        for marker in PLAN_EXECUTION_MARKERS:
            if marker not in plan_execution:
                report.error(
                    "plan_execution_reference",
                    f"Plan-and-Execute reference missing {marker}",
                    f"计划并执行参考文档缺少 {marker}",
                )

    plan_observability_path = skill_dir / PLAN_EXECUTION_OBSERVABILITY
    plan_observability = (
        plan_observability_path.read_text(encoding="utf-8")
        if plan_observability_path.is_file()
        else ""
    )
    for marker in (
        "Version / 版本: `1.1.0`",
        "../../workflow-observability-probes.md",
        "## Probe Mounts / 探针挂载",
        "## Hard Integrity Alerts / 硬完整性告警",
        "completed_action_replay_rate",
        "checkpoint_recovery_success_rate",
        "unknown_state_backlog_seconds",
    ):
        if marker not in plan_observability:
            report.error(
                "plan_execution_observability",
                f"Plan-and-Execute observability missing {marker}",
                f"计划并执行可观测性文档缺少 {marker}",
            )

    for relative in RUNTIME_IMPLEMENTATION_FILES:
        path = skill_dir / relative
        if not path.is_file():
            report.error(
                "reasoning_runtime_implementation",
                f"missing reference runtime file {relative}",
                f"缺少参考运行时文件 {relative}",
            )
        elif path.suffix == ".py":
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except (OSError, UnicodeError, SyntaxError) as error:
                report.error(
                    "reasoning_runtime_implementation",
                    f"cannot compile {relative}: {error}",
                    f"无法编译 {relative}：{error}",
                )

    schemas = validate_reasoning_schemas(skill_dir, report)
    runtime_modules = validate_runtime_imports(skill_dir, report)
    validate_runtime_schema_enums(runtime_modules, schemas, report)
    validate_metric_registry(skill_dir, report)
    validate_probe_registry(skill_dir, report)
    validate_probe_dependency_matrix(skill_dir, report)

    factory_path = skill_dir / CHAIN_FACTORY_REFERENCE
    factory_reference = (
        factory_path.read_text(encoding="utf-8") if factory_path.is_file() else ""
    )
    if not factory_reference:
        report.error(
            "reasoning_chain_factory_reference",
            f"missing chain factory reference {CHAIN_FACTORY_REFERENCE}",
            f"缺少推理链工厂参考文档 {CHAIN_FACTORY_REFERENCE}",
        )
    else:
        for marker in CHAIN_FACTORY_MARKERS:
            if marker not in factory_reference:
                report.error(
                    "reasoning_chain_factory_reference",
                    f"chain factory reference missing {marker}",
                    f"推理链工厂参考文档缺少 {marker}",
                )

    reflection_path = skill_dir / REFLECTION_EXECUTION_REFERENCE
    reflection_reference = (
        reflection_path.read_text(encoding="utf-8")
        if reflection_path.is_file()
        else ""
    )
    if not reflection_reference:
        report.error(
            "reflection_execution_reference",
            f"missing reflection execution reference {REFLECTION_EXECUTION_REFERENCE}",
            f"缺少反思执行参考文档 {REFLECTION_EXECUTION_REFERENCE}",
        )
    else:
        for marker in REFLECTION_EXECUTION_MARKERS:
            if marker not in reflection_reference:
                report.error(
                    "reflection_execution_reference",
                    f"reflection execution reference missing {marker}",
                    f"反思执行参考文档缺少 {marker}",
                )

    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    for marker in (
        PLAN_EXECUTION_REFERENCE,
        "schemas/goal-contract.schema.json",
        "schemas/workflow-plan.schema.json",
        "schemas/workflow-plan-patch.schema.json",
        "schemas/workflow-checkpoint.schema.json",
        "runtime/plan_execution.py",
        "PlanExecutionSession",
    ):
        if marker not in skill_text:
            report.error(
                "plan_execution_entrypoint",
                f"SKILL.md does not route Plan-and-Execute through {marker}",
                f"SKILL.md 未将计划并执行路由到 {marker}",
            )

    for marker in (
        CHAIN_FACTORY_REFERENCE,
        "runtime/reasoning_chain_factory.py",
        "ChainPlanSession",
    ):
        if marker not in skill_text:
            report.error(
                "reasoning_chain_factory_entrypoint",
                f"SKILL.md does not route chain execution through {marker}",
                f"SKILL.md 未将链式执行路由到 {marker}",
            )

    for marker in (
        REFLECTION_EXECUTION_REFERENCE,
        "schemas/reflection-contract.schema.json",
        "schemas/reflection-event.schema.json",
        "schemas/reflection-round-observation.schema.json",
        "runtime/reflection_runtime.py",
        "ReflectionSession",
    ):
        if marker not in skill_text:
            report.error(
                "reflection_execution_entrypoint",
                f"SKILL.md does not route reflection through {marker}",
                f"SKILL.md 未将反思执行路由到 {marker}",
            )

    if "reasoning-chain-factory.md" not in execution:
        report.error(
            "reasoning_chain_factory_entrypoint",
            "reasoning execution protocol does not link the chain factory",
            "推理执行协议未链接推理链工厂",
        )

    parallel_factory_path = skill_dir / PARALLEL_FACTORY_REFERENCE
    parallel_factory_reference = (
        parallel_factory_path.read_text(encoding="utf-8")
        if parallel_factory_path.is_file()
        else ""
    )
    if not parallel_factory_reference:
        report.error(
            "reasoning_parallel_factory_reference",
            f"missing parallel factory reference {PARALLEL_FACTORY_REFERENCE}",
            f"缺少推理并行工厂参考文档 {PARALLEL_FACTORY_REFERENCE}",
        )
    else:
        for marker in PARALLEL_FACTORY_MARKERS:
            if marker not in parallel_factory_reference:
                report.error(
                    "reasoning_parallel_factory_reference",
                    f"parallel factory reference missing {marker}",
                    f"推理并行工厂参考文档缺少 {marker}",
                )

    for marker in (
        PARALLEL_FACTORY_REFERENCE,
        "runtime/reasoning_parallel_factory.py",
        "runtime/reasoning_parallel_projection.py",
        "runtime/reasoning_parallel_scheduler.py",
        "runtime/reasoning_event_sqlite_store.py",
        "ParallelPlanSession",
        "ParallelPathScheduler",
        "resume_session()",
        "close_leased_branch()",
        "finalize_selected_candidate()",
        "project_parallel_run(plan, events)",
    ):
        if marker not in skill_text:
            report.error(
                "reasoning_parallel_factory_entrypoint",
                f"SKILL.md does not route parallel execution through {marker}",
                f"SKILL.md 未将并行执行路由到 {marker}",
            )

    if "reasoning-parallel-factory.md" not in execution:
        report.error(
            "reasoning_parallel_factory_entrypoint",
            "reasoning execution protocol does not link the parallel factory",
            "推理执行协议未链接推理并行工厂",
        )

    tool_dispatch_path = skill_dir / TOOL_DISPATCH_REFERENCE
    tool_dispatch_reference = (
        tool_dispatch_path.read_text(encoding="utf-8")
        if tool_dispatch_path.is_file()
        else ""
    )
    if not tool_dispatch_reference:
        report.error(
            "tool_dispatch_reference",
            f"missing tool dispatch reference {TOOL_DISPATCH_REFERENCE}",
            f"缺少工具调度参考文档 {TOOL_DISPATCH_REFERENCE}",
        )
    else:
        if "Version / 版本: `1.0.0`" not in tool_dispatch_reference:
            report.error(
                "tool_dispatch_reference",
                "tool dispatch reference must declare version 1.0.0",
                "工具调度参考文档必须声明版本 1.0.0",
            )
        for marker in TOOL_DISPATCH_MARKERS:
            if marker not in tool_dispatch_reference:
                report.error(
                    "tool_dispatch_reference",
                    f"tool dispatch reference missing {marker}",
                    f"工具调度参考文档缺少 {marker}",
                )

    for marker in (
        TOOL_DISPATCH_REFERENCE,
        "runtime/tool_dispatch.py",
        "runtime/tool_dispatch_projection.py",
        "runtime/tool_dispatch_sqlite_store.py",
        "Selection is not authorization",
        "选中不等于授权",
    ):
        if marker not in skill_text:
            report.error(
                "tool_dispatch_entrypoint",
                f"SKILL.md does not route action execution through {marker}",
                f"SKILL.md 未将行动执行路由到 {marker}",
            )

    for cell in registry.get("cells", []):
        if cell.get("capability_ref") != "COG_REASONING":
            continue
        cell_key = str(cell.get("cell_key", ""))
        design_path = skill_dir / str(cell.get("design_path", ""))
        observability_path = skill_dir / str(cell.get("observability_path", ""))
        design = design_path.read_text(encoding="utf-8") if design_path.is_file() else ""
        observability = (
            observability_path.read_text(encoding="utf-8")
            if observability_path.is_file()
            else ""
        )
        if (
            "../../reasoning-execution-flow.md" not in design
            or "../../workflow-observability-probes.md" not in design
        ):
            report.error(
                "reasoning_protocol_link",
                f"{cell_key} design does not link both runtime protocols",
                f"{cell_key} 设计未同时链接两个运行协议",
            )
        if "../../workflow-observability-probes.md" not in observability:
            report.error(
                "reasoning_probe_link",
                f"{cell_key} observability does not link the shared probe suite",
                f"{cell_key} 可观测性文件未链接共享探针套件",
            )
        if cell_key == "reasoning-chain":
            for document_name, document in (
                ("design", design),
                ("observability", observability),
            ):
                if "reasoning-chain-factory.md" not in document:
                    report.error(
                        "reasoning_chain_factory_entrypoint",
                        f"reasoning-chain {document_name} does not link the chain factory",
                        f"reasoning-chain {document_name} 未链接推理链工厂",
                    )
        if cell_key == "reasoning-parallel":
            for document_name, document in (
                ("design", design),
                ("observability", observability),
            ):
                if "reasoning-parallel-factory.md" not in document:
                    report.error(
                        "reasoning_parallel_factory_entrypoint",
                        f"reasoning-parallel {document_name} does not link the parallel factory",
                        f"reasoning-parallel {document_name} 未链接推理并行工厂",
                    )

    for cell in registry.get("cells", []):
        if cell.get("capability_ref") != "COG_REFLECTION":
            continue
        cell_key = str(cell.get("cell_key", ""))
        design_path = skill_dir / str(cell.get("design_path", ""))
        observability_path = skill_dir / str(cell.get("observability_path", ""))
        design = design_path.read_text(encoding="utf-8") if design_path.is_file() else ""
        observability = (
            observability_path.read_text(encoding="utf-8")
            if observability_path.is_file()
            else ""
        )
        if "../../reflection-execution-flow.md" not in design:
            report.error(
                "reflection_protocol_link",
                f"{cell_key} design does not link governed reflection execution",
                f"{cell_key} 设计未链接受治理反思执行协议",
            )
        if (
            "../../reflection-execution-flow.md" not in observability
            or "../../workflow-observability-probes.md" not in observability
        ):
            report.error(
                "reflection_probe_link",
                f"{cell_key} observability does not link reflection execution and probes",
                f"{cell_key} 可观测性文件未链接反思执行与共享探针",
            )


    for cell in registry.get("cells", []):
        if cell.get("cell_key") != "action-routing":
            continue
        design_path = skill_dir / str(cell.get("design_path", ""))
        observability_path = skill_dir / str(cell.get("observability_path", ""))
        design = design_path.read_text(encoding="utf-8") if design_path.is_file() else ""
        observability = (
            observability_path.read_text(encoding="utf-8")
            if observability_path.is_file()
            else ""
        )
        if "../../tool-dispatch-execution.md" not in design:
            report.error(
                "tool_dispatch_link",
                "action-routing design does not link the execution reference",
                "action-routing 设计未链接工具调度执行参考",
            )
        if "../../tool-dispatch-execution.md" not in observability:
            report.error(
                "tool_dispatch_link",
                "action-routing observability does not link the execution reference",
                "action-routing 可观测性文件未链接工具调度执行参考",
            )


def validate_navigation(skill_dir: pathlib.Path, report: ValidationReport) -> None:
    references = skill_dir / "references"
    for path in sorted(references.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        line_count = len(content.splitlines())
        has_navigation = "## Quick Navigation / 快速导航" in content
        relative = path.relative_to(skill_dir).as_posix()
        if line_count > 500 and not has_navigation:
            report.error(
                "missing_navigation",
                f"{relative} has {line_count} lines and no quick navigation",
                f"{relative} 有 {line_count} 行但缺少快速导航",
            )
        elif line_count > 100 and not has_navigation:
            report.warning(
                "missing_navigation",
                f"{relative} has {line_count} lines and no quick navigation",
                f"{relative} 有 {line_count} 行但缺少快速导航",
            )


def validate_skill(skill_dir: pathlib.Path) -> ValidationReport:
    skill_dir = pathlib.Path(skill_dir).resolve()
    report = ValidationReport()
    try:
        registry = load_registry(skill_dir)
    except (OSError, json.JSONDecodeError) as error:
        report.error(
            "registry_shape",
            f"cannot load registry: {error}",
            f"无法加载注册表：{error}",
        )
        return report

    validate_registry_shape(registry, skill_dir, report)
    validate_markdown_views(registry, skill_dir, report)
    validate_relative_links(skill_dir, report)
    validate_analysis_contracts(skill_dir, report)
    validate_runtime_protocols(registry, skill_dir, report)
    validate_navigation(skill_dir, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Harness Engineering Patterns / 校验 Harness 工程模式 Skill"
    )
    parser.add_argument(
        "skill_dir",
        nargs="?",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args(argv)
    report = validate_skill(args.skill_dir)

    for error in report.errors:
        print(f"ERROR / 错误: {error}")
    for warning in report.warnings:
        print(f"WARNING / 警告: {warning}")
    if report.errors:
        print(
            f"Validation failed / 校验失败: {len(report.errors)} error(s), "
            f"{len(report.warnings)} warning(s)"
        )
        return 1
    print(
        f"Validation passed / 校验通过: 0 errors, "
        f"{len(report.warnings)} warning(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
