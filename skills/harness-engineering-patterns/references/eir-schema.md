# Engineering Intermediate Representation / 工程中间表示

Use this file to maintain a compact, evidence-backed EIR while analyzing workflows or Harness source. / 使用本文档在分析工作流程或 Harness 源码时维护紧凑、证据支撑的 EIR。

## Purpose / 目的

The EIR normalizes workflow nodes, source components, mappings, evidence, evaluation, and governance so later matrix mapping and pattern extraction are traceable. / EIR 将工作流节点、源码组件、映射、证据、评估和治理标准化，使后续矩阵映射与模式抽取可追踪。

Keep the EIR as a working note or report section unless the user asks for a separate file. / 除非用户要求单独文件，否则将 EIR 作为工作记录或报告章节维护。

## EIR Header / EIR 总体结构

```yaml
eir_type: agent_engineering_analysis
version: 0.1.0
analysis_id: ANALYSIS_YYYYMMDD_XXXX
status: draft

input:
  input_type: workflow | harness_source | mixed
  input_refs: []
  scope: TODO

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
```

## Business Node / 业务节点

Use Business Node / 业务节点 for process responsibilities, not file-level details. / Business Node / 业务节点用于流程职责，而不是文件级细节。

```yaml
node_id: NODE_0001
node_name: TODO
node_type: workflow_step | decision_point | action_point | review_point | handoff_point
status: draft

description: TODO
inputs: []
outputs: []
actors: []
tools: []

related_cognition_refs:
  - COG_PERCEPTION
related_topology_refs:
  - TOP_CHAIN
matrix_coordinates:
  - COG_PERCEPTION__TOP_CHAIN

related_pattern_refs: []
related_skill_refs: []
risks: []
evaluation: []
evidence_refs: []
```

## Source Component / 源码组件

Use Source Component / 源码组件 for code units that affect context, memory, reasoning, action, reflection, collaboration, or governance. / Source Component / 源码组件用于会影响上下文、记忆、推理、行动、反思、协作或治理的代码单元。

```yaml
component_id: SRC_0001
component_name: TODO
component_type: main_loop | context_builder | tool_dispatcher | memory_store | sandbox | permission | event_log | subagent | adapter | ui | config
status: draft

source_path: TODO
language: TODO
entry_points: []
public_interfaces: []
internal_dependencies: []
external_dependencies: []

related_cognition_refs:
  - COG_ACTION
related_topology_refs:
  - TOP_ROUTING
matrix_coordinates:
  - COG_ACTION__TOP_ROUTING

first_round_reading: true
noise_level: core | support | boilerplate
reason_to_include: TODO
reason_to_exclude: TODO

related_pattern_refs: []
related_skill_refs: []
evidence_refs: []
```

## Evidence Item / 证据项

Use Evidence Item / 证据项 for every architecture claim. / 对每个架构判断使用 Evidence Item / 证据项。

```yaml
evidence_id: EVIDENCE_0001
evidence_type: source_code | test | official_doc | config | log | trace | runtime_record | protocol
status: active

claim: TODO
source_ref: TODO
file_path: TODO
line_start: null
line_end: null
symbol: TODO
snippet_summary: TODO
confidence: high | medium | low
notes: TODO
```

## Matrix Mapping / 矩阵映射

Use Matrix Mapping / 矩阵映射 to connect a node, component, pattern, or Skill to cognition and topology. / 使用 Matrix Mapping / 矩阵映射 将节点、组件、模式或 Skill 连接到认知与拓扑。

```yaml
mapping_id: MAP_0001
subject_type: business_node | source_component | pattern | skill
subject_ref: SRC_0001

cognition_refs:
  - COG_ACTION
topology_refs:
  - TOP_ROUTING
matrix_coordinates:
  - COG_ACTION__TOP_ROUTING

mapping_reason: TODO
failure_modes:
  - TODO
evidence_refs:
  - EVIDENCE_0001
confidence: high | medium | low
```

## ID Rules / ID 规则

- Allocate IDs once and keep them stable. / 一旦分配 ID，就保持稳定。
- Prefer sequential IDs inside the current analysis when no registry exists. / 没有注册表时，在当前分析内使用顺序 ID。
- Do not rename IDs only because wording changes. / 不要因为措辞变化而重命名 ID。
- Mark deprecated IDs instead of reusing them. / 标记废弃 ID，不要复用。

## EIR Readiness / EIR 就绪标准

An EIR is ready for pattern extraction when the main flow is known, core nodes or components have inputs and outputs, mappings have reasons, and key claims have evidence. / 当主流程已知、核心节点或组件有输入输出、映射有理由、关键判断有证据时，EIR 才适合进入模式抽取。
