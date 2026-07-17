# Extension Candidate / 扩展候选

Cell / 交织点: reasoning-hierarchy / 推理 x 层级
Capability / 能力: Reasoning / 推理
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

Runtime Protocols / 运行协议: [Reasoning Execution Flow / 推理执行流程](../../reasoning-execution-flow.md); [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md).

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reasoning / 推理 x Hierarchy / 层级 (Hierarchy / 层级).
- 论文依据 / Article Basis: 空白单元 / Empty cell; arXiv:2605.13850 leaves this intersection unnamed. / 空白单元 / Empty cell；arXiv:2605.13850 未命名该交织点。
- 问题 / Problem: The article leaves this intersection unnamed; use it only if workflow evidence shows that Reasoning / 推理 needs Hierarchy / 层级. / 论文未命名该交织点；仅当工作流证据表明 Reasoning / 推理 需要 Hierarchy / 层级 时使用。
- 架构方案 / Architectural Solution: Keep this as an extension candidate and define a concrete pattern only after repeated workflow evidence appears. / 将其保留为扩展候选，仅在反复出现工作流证据后再定义具体模式。
- 工程权衡 / Engineering Trade-offs: This avoids inventing taxonomy, but leaves a deliberate gap until practice justifies the pattern. / 这避免凭空发明分类，但在实践证明前会保留有意空白。
- 工作流诊断用途 / Workflow Diagnosis Use: Extension candidate / 扩展候选.

### Shared Protocol Role, Not Promotion / 共享协议角色，不构成晋升

The multi-agent scene in `PATTERN_0051` uses hierarchy to propagate task identity, parent events, goals, constraints, evidence requirements, budget shares, authority, and child results. The source draft primarily maps the authority aspect to governance x hierarchy; do not reclassify it as a named reasoning-hierarchy pattern without repeated evidence. / `PATTERN_0051` 的多智能体场景使用层级传播任务标识、父事件、目标、约束、证据要求、预算份额、权限和子结果。来源草案主要将权限方面映射到治理 x 层级；缺少反复证据时，不得将其重新分类为命名的推理 x 层级模式。

### Pattern Template / 模式模板

- 状态 / Status: 扩展候选 / Extension candidate.
- 模式清单 / Patterns: 待发现 / To be discovered.
- 诊断用途 / Diagnostic Use: Extension candidate / 扩展候选.
- 适用工作流节点 / Applicable Workflow Nodes: 问题拆解、方案设计 / Decomposition, design.
- 当前症状 / Current Symptoms: Parent and child tasks disagree on goals or hard constraints, lose evidence provenance, duplicate work, exceed the parent budget, or return conclusions without a responsible validation owner. / 父子任务对目标或硬约束理解不一致、丢失证据来源、重复工作、超出父预算，或在缺少验证责任方时返回结论。
- 适配信号 / Fit Signals: 推理需要从目标拆到方案、任务和检查点 / Reasoning decomposes goals into designs, tasks, and checkpoints.
- 调整方向 / Adjustment Direction: Keep the cell as an extension candidate while making parent-child contracts, identity propagation, authority, budget allocation, evidence handoff, and final validation ownership explicit. / 保持本单元为扩展候选，同时显式化父子契约、标识传播、权限、预算分配、证据交接和最终验证责任。
- 修改方式 / How To Modify: 1) Assign one bounded child objective. 2) Propagate task and parent-event IDs plus snapshot versions. 3) Allocate child budget and allowed actions. 4) Require external claims, evidence refs, unresolved items, and stop reason in the return package. 5) Let the parent reconcile conflicts and run the final validator. / 1）分配一个有边界的子目标；2）传播任务和父事件 ID 及快照版本；3）分配子预算与允许动作；4）要求返回外部命题、证据引用、未解决项和停止原因；5）由父级解决冲突并运行最终验证器。
- 输入 / Inputs: Parent contract, child objective, inherited snapshots, authority scope, budget share, evidence requirement, and validation responsibility. / 父级契约、子目标、继承快照、权限范围、预算份额、证据要求和验证责任。
- 输出 / Outputs: Correlated child result with evidence and limits, remaining budget, unresolved conflicts, and parent-owned synthesis and validation. / 带关联标识、证据和限制的子结果、剩余预算、未解决冲突，以及由父级负责的综合与验证。
- 风险与治理 / Risks & Governance: Delegation can dilute constraints, fragment audit chains, duplicate work, and hide failure. Require parent-event propagation, least authority, budget conservation, explicit handoff fields, conflict preservation, and outcome validation at the accountable level. / 委派可能弱化约束、打断审计链、重复工作并隐藏失败。应强制父事件传播、最小权限、预算守恒、显式交接字段、冲突保留和责任层级的结果验证。

Observability Metrics File / 可观测性指标文件: [reasoning-hierarchy-observability.md](reasoning-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
