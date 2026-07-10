# Engineering Intermediate Representation / 工程中间表示

Use this file to maintain a compact, evidence-backed EIR while analyzing workflows or Harness source. / 使用本文档在分析工作流程或 Harness 源码时维护紧凑、证据支撑的 EIR。

## Purpose / 目的

Normalize workflow nodes, source components, flows, mappings, evidence, patterns, Skill recommendations, evaluation, and governance so every later decision is traceable. / 标准化工作流节点、源码组件、各类流、映射、证据、模式、Skill 建议、评价和治理，使后续每个决策都可追踪。

Keep the EIR as a working note or report section unless the user requests a separate artifact. References must resolve inside the analysis or declare `external: true`. / 除非用户要求独立产物，否则将 EIR 作为工作记录或报告章节；引用必须在分析内可解析，或声明 `external: true`。

## EIR Header / EIR 总体结构

```yaml
eir_type: agent_engineering_analysis
version: 1.0.0
analysis_id: ANALYSIS_20260710_0001
status: draft

input:
  input_type: workflow | harness_source | mixed
  input_refs: []
  scope: "bounded analysis scope"

business_nodes: []
source_components: []
control_flows: []
state_flows: []
tool_flows: []
permission_flows: []
matrix_mappings: []
patterns: []
skills: []
evidence: []
evaluation: []
governance: []
open_verification_tasks: []
```

## Business Node / 业务节点

Use Business Node / 业务节点 for process responsibilities, not file-level details. / Business Node 用于流程职责，不用于文件级细节。

```yaml
node_id: NODE_0001
node_name: "verification gate"
node_type: workflow_step | decision_point | action_point | review_point | handoff_point
status: draft | active | superseded | deprecated | verified
description: "responsibility and boundary"
inputs: []
outputs: []
actors: []
tools: []
related_cognition_refs: [COG_REFLECTION]
related_topology_refs: [TOP_ROUTING]
matrix_coordinates: [COG_REFLECTION__TOP_ROUTING]
related_pattern_refs: []
related_skill_refs: []
risk_refs: []
evaluation_refs: []
evidence_refs: []
```

## Source Component / 源码组件

Use Source Component / 源码组件 for code units that affect context, memory, reasoning, action, reflection, collaboration, or governance. / Source Component 用于会影响上下文、记忆、推理、行动、反思、协作或治理的代码单元。

```yaml
component_id: SRC_0001
component_name: "tool dispatcher"
component_type: main_loop | context_builder | tool_dispatcher | memory_store | sandbox | permission | event_log | subagent | adapter | ui | config
status: draft | active | superseded | deprecated | verified
source_path: "src/runtime/dispatcher.py"
language: "python"
entry_points: []
public_interfaces: []
internal_dependencies: []
external_dependencies: []
related_cognition_refs: [COG_ACTION]
related_topology_refs: [TOP_ROUTING]
matrix_coordinates: [COG_ACTION__TOP_ROUTING]
first_round_reading: true
noise_level: core | support | boilerplate
reason_to_include: "changes tool execution"
reason_to_exclude: ""
related_pattern_refs: []
related_skill_refs: []
evidence_refs: []
```

## Control Flow / 控制流

Record ordering, branching, looping, delegation, and stop conditions. / 记录顺序、分支、循环、委派和停止条件。

```yaml
control_flow_id: FLOW_CONTROL_0001
status: draft | active | superseded | deprecated | verified
from_ref: NODE_0001
to_ref: NODE_0002
flow_type: sequence | branch | parallel | orchestration | loop | hierarchy | stop
condition: "tests pass"
controller_ref: SRC_0001
retry_limit: 3
stop_condition: "verified or escalated"
evidence_refs: [EVIDENCE_0001]
```

## State Flow / 状态流

Record how state is created, read, updated, invalidated, recovered, or archived. / 记录状态如何创建、读取、更新、失效、恢复或归档。

```yaml
state_flow_id: FLOW_STATE_0001
status: active
state_name: "task progress"
operation: create | read | update | invalidate | recover | archive
producer_ref: SRC_0001
consumer_refs: [NODE_0002]
storage_ref: "event_store"
consistency_rule: "append-only correction events"
recovery_rule: "rebuild from latest verified snapshot"
evidence_refs: [EVIDENCE_0002]
```

## Tool Flow / 工具流

Record tool selection, schema validation, execution boundary, result writeback, and failure handling. / 记录工具选择、Schema 校验、执行边界、结果回填和失败处理。

```yaml
tool_flow_id: FLOW_TOOL_0001
status: active
caller_ref: SRC_0001
tool_ref: "shell_command"
selection_rule: "action type and permission scope"
parameter_schema_ref: "tool schema"
execution_boundary: "sandbox"
result_target_ref: FLOW_STATE_0001
failure_route_ref: NODE_0003
evidence_refs: [EVIDENCE_0003]
```

## Permission Flow / 权限流

Record identity, scope, policy, approval, and the allowed side-effect boundary. / 记录身份、范围、策略、审批和允许的副作用边界。

```yaml
permission_flow_id: FLOW_PERMISSION_0001
status: active
subject_ref: "user_or_agent_identity"
action_ref: FLOW_TOOL_0001
scope: "workspace read and bounded write"
policy_refs: [GOV_0001]
approval_required: true
approval_ref: GOVERNANCE_0001
side_effect_class: read_only | reversible_write | irreversible | external
decision: allow | deny | gate
evidence_refs: [EVIDENCE_0004]
```

## Evidence Item / 证据项

Use Evidence Item / 证据项 for every architecture claim. / 对每个架构判断使用 Evidence Item。

```yaml
evidence_id: EVIDENCE_0001
evidence_type: source_code | test | official_doc | config | log | trace | runtime_record | protocol
status: active | superseded | deprecated | verified
claim: "dispatcher validates tool parameters"
source_ref: "repository@commit"
file_path: "src/runtime/dispatcher.py"
line_start: 42
line_end: 61
symbol: "dispatch"
snippet_summary: "validates schema before execution"
confidence: high | medium | low
freshness_checked_at: "2026-07-10T00:00:00Z"
external: false
notes: ""
```

## Matrix Mapping / 矩阵映射

Connect a node, component, pattern, or Skill to registry-backed cognition and topology IDs. / 将节点、组件、模式或 Skill 连接到注册表中的认知与拓扑 ID。

```yaml
mapping_id: MAP_0001
subject_type: business_node | source_component | pattern | skill
subject_ref: SRC_0001
cognition_refs: [COG_ACTION]
topology_refs: [TOP_ROUTING]
matrix_coordinates: [COG_ACTION__TOP_ROUTING]
cell_refs: [CELL_ACTION_ROUTING]
mapping_reason: "dispatches actions by type and permission"
failure_mode_refs: [FAIL_0003, FAIL_0004]
evidence_refs: [EVIDENCE_0001]
confidence: high | medium | low
```

## Pattern Record / 模式记录

Use a local Pattern Record for a selected, observed, or proposed pattern. Global identity comes from `registry.json`. / 对已选、已观察或拟议模式使用本地 Pattern Record；全局身份来自 `registry.json`。

```yaml
pattern_record_id: PATTERN_RECORD_0001
pattern_ref: PATTERN_0036
cell_ref: CELL_ACTION_ROUTING
status: proposed | selected | applied | observed | rejected
subject_refs: [SRC_0001]
parameterization:
  approval_threshold: "high risk"
local_evidence_refs: [EVIDENCE_0001]
failure_mode_refs: [FAIL_0003]
verification_tasks: []
```

## Skill Recommendation / Skill 建议

Record a Skillization decision without creating a Skill automatically. / 记录 Skill 化决策，不自动创建 Skill。

```yaml
skill_recommendation_id: SKILL_ANALYSIS_0001
skill_name: "route-controlled-tools"
status: proposed | accepted | rejected | implemented
goal: "dispatch actions through validated tool and permission routes"
pattern_refs: [PATTERN_0036]
input_contract: "typed action request"
output_contract: "dispatch decision and result record"
governance_refs: [GOV_0001, GOV_0003]
evaluation_refs: [EVAL_0001]
evidence_refs: [EVIDENCE_0001]
```

## Evaluation Reference / 评价引用

Reference the seven-dimension evaluation in `evaluation-governance.md`. / 引用 `evaluation-governance.md` 中的七维评价。

```yaml
evaluation_ref_id: EVAL_REF_0001
evaluation_id: EVAL_0001
target_ref: SRC_0001
lowest_dimension: evidence
aggregate_score: 72
confidence: medium
open_verification_tasks: []
external: false
```

## Governance Item / 治理项

Record a concrete permission, safety, audit, rollback, retention, or compliance requirement. / 记录具体权限、安全、审计、回滚、留存或合规要求。

```yaml
governance_item_id: GOVERNANCE_0001
governance_rule_refs: [GOV_0001]
status: proposed | active | superseded | deprecated | verified
target_refs: [FLOW_TOOL_0001]
requirement: "high-risk actions require explicit approval"
enforcement_point: "before tool execution"
rollback_or_recovery: "do not execute before approval"
audit_record: "approval decision event"
evidence_refs: [EVIDENCE_0004]
```

## ID Rules / ID 规则

- Global registry IDs: `COG_*`, `TOP_*`, `CELL_*`, `PATTERN_*`. / 全局注册表 ID：`COG_*`、`TOP_*`、`CELL_*`、`PATTERN_*`。
- Analysis IDs: `ANALYSIS_*`, `NODE_*`, `SRC_*`, `FLOW_CONTROL_*`, `FLOW_STATE_*`, `FLOW_TOOL_*`, `FLOW_PERMISSION_*`, `EVIDENCE_*`, `MAP_*`, `PATTERN_RECORD_*`, `SKILL_*`, `EVAL_*`, `GOV_*`, `GOVERNANCE_*`, `FAIL_*`, `PROBE_*`. / 分析 ID 使用这些前缀。
- Allocate once, keep stable, and mark deprecated instead of reusing. / 一次分配、保持稳定，使用废弃标记而不复用。
- Resolve every reference locally or declare it external. / 每个引用都在本地解析，或声明为外部引用。

## EIR Readiness / EIR 就绪标准

An EIR is ready for pattern selection when the main flow is known, core nodes or components have inputs and outputs, flows expose control and state boundaries, mappings have reasons, and key claims have evidence. / 当主流程已知、核心节点或组件有输入输出、各类流暴露控制与状态边界、映射有理由、关键判断有证据时，EIR 才适合进入模式选型。

An EIR may remain preliminary when evidence gaps are explicit. Pattern promotion requires verified evidence and failure-path checks. / 证据缺口明确时，EIR 可以保持初步状态；模式晋升必须具备已验证证据和失败路径检查。
