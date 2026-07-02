# Diagnosis Method / 诊断方法

Use this file to move from classification to workflow modification. / 使用本文档从分类推进到工作流修改。

## Automatic Engineering Node Analysis / 工程节点自动分析

When the user asks to analyze an engineering node, automatically run Trace Insert / 自动运行 Trace 插入, then run Pattern Selection Card / 模式选型卡 after evidence is ready. / 当用户要求分析工程节点时，自动运行 Trace 插入；证据就绪后，再运行模式选型卡。

This automatic flow applies even when the user names only one node and does not explicitly mention ASSESS, ROUTE, SELECT, matrix, or Trace. / 即使用户只给出一个节点，未显式提到 ASSESS、ROUTE、SELECT、矩阵或 Trace，也适用该自动流程。

## Diagnostic Flow / 诊断流程

1. Describe the current workflow in 3-7 steps. / 用 3-7 步描述当前工作流。
2. Split those steps into business nodes from `workflow-nodes.md`. / 使用 `workflow-nodes.md` 将步骤拆成业务节点。
3. Apply Trace Insert / Trace 插入 to collect complete node evidence before selection. / 应用 Trace Insert / Trace 插入，在选型前采集完整节点证据。
4. Run the Pattern Selection Card / 模式选型卡 only after node evidence is ready. / 仅在节点证据就绪后运行 Pattern Selection Card / 模式选型卡。
5. Map each node to one primary capability and one primary orchestration mode through ASSESS / 评估 and ROUTE / 判拓扑. / 通过 ASSESS / 评估 与 ROUTE / 判拓扑，为每个节点映射一个主要能力和一个主要编排模式。
6. Inspect the matrix cell through SELECT / 查矩阵 and compare current behavior against fit signals. / 通过 SELECT / 查矩阵 检查交织点，并将当前行为与适配信号比较。
7. Identify whether the issue is missing node, wrong mode, weak capability, missing loop, poor handoff, missing memory, or weak governance. / 识别问题属于节点缺失、模式错误、能力薄弱、循环缺失、交接不良、记忆缺失或治理薄弱。
8. Recommend a concrete adjustment that changes workflow behavior. / 推荐能改变工作流行为的具体调整。
9. Define verification and observation points, then propose the Trace update. / 定义验证方式和观察点，并提出 Trace 更新。

## Trace Insert Before Selection / 选型前 Trace 插入

Use `pattern-selection-card.md` to insert Trace before any matrix decision. / 使用 `pattern-selection-card.md` 在任何矩阵决策前插入 Trace。

- First collect Engineering Node / 工程节点, Node Evidence / 节点证据, risk, current behavior, and failure signals. / 先采集工程节点、节点证据、风险、当前行为和失败信号。
- If Trace Evidence / Trace 证据 exists, use it to compare repeated outcomes and previous pattern effects. / 如果存在 Trace 证据，用它比较重复结果和既往模式效果。
- If no Trace exists, mark the analysis as initial planning and state the missing observation points. / 如果没有 Trace，将分析标记为初次规划，并说明缺失的观察点。
- Stop before ASSESS / 评估, ROUTE / 判拓扑, and SELECT / 查矩阵 when node evidence is incomplete. / 当节点证据不完整时，在 ASSESS、ROUTE、SELECT 前停止。

## Article-Informed Selection Flow / 文章启发的选型流程

Use this flow when choosing or changing a pattern. / 选择或调整模式时使用此流程。

1. Bound the workflow slice. Identify trigger, actor, decision, output, and failure cost. / 界定工作流切片：识别触发、参与者、决策、输出和失败成本。
2. Insert Trace. Gather current node evidence and read existing trace files when available. / 插入 Trace：采集当前节点证据，并在可用时读取既有追踪文件。
3. Run ASSESS / 评估. Ask which capability is truly responsible for the bottleneck. / 执行 ASSESS / 评估：判断真正造成瓶颈的是哪类能力。
4. Run ROUTE / 判拓扑. Select the simplest mode that preserves the needed dependencies. / 执行 ROUTE / 判拓扑：选择能保留必要依赖的最简单模式。
5. Run SELECT / 查矩阵. Prefer a named pattern when the cell has one; use extension rules when it does not. / 执行 SELECT / 查矩阵：若单元已有命名模式则优先使用；若没有则使用扩展规则。
6. Read the selected pattern's design pattern file and observability metrics file. / 读取已选模式的设计模式文件和可观测性指标文件。
7. Evaluate impact. Check latency, cost, ownership, risk, and observability before recommending the change. / 评估影响：提出调整前检查延迟、成本、归属、风险和可观测性。
8. Build the modification path. Convert the selected pattern into workflow changes, not just architecture labels. / 构建修改路径：将所选模式转化为工作流修改，而不只是架构标签。

## Pattern Selection Laws / 模式选择规律

- Heterogeneity drives routing. / 异质性推动路由：输入、任务或风险差异越大，越需要路由。
- Independence drives parallelism. / 独立性推动并行：子任务相互独立且可合并时，优先考虑并行。
- Feedback drives loops. / 反馈推动循环：结果会改变下一步判断时，需要循环而非单向链式。
- Coordination burden drives orchestration. / 协调负担推动编排：工具、状态、角色或依赖越多，越需要控制器。
- Depth drives hierarchy. / 深度推动层级：目标需要递归拆解或分层授权时，使用层级。
- Risk can override topology. / 风险可以覆盖拓扑：高风险场景优先加入治理门禁、审计和爆炸半径控制。

## Problem Types / 问题类型

| Problem | 中文 | Symptom / 症状 | Typical Adjustment / 常见调整 |
| --- | --- | --- | --- |
| missing-node | 节点缺失 | A necessary responsibility never happens. / 必要职责没有发生。 | Add a workflow node with input, output, and owner. / 增加有输入、输出和负责人的工作流节点。 |
| wrong-mode | 模式错配 | The flow is too linear, too manual, too scattered, or too centralized. / 流程过度线性、过度人工、过度分散或过度集中。 | Change chain to loop, routing, parallel, orchestration, or hierarchy. / 将链式调整为循环、路由、并行、编排或层级。 |
| weak-capability | 能力薄弱 | The node exists but lacks sensing, memory, reasoning, action, reflection, collaboration, or governance. / 节点存在但缺少某类能力。 | Add the missing capability to the node. / 为节点补充缺失能力。 |
| missing-loop | 循环缺失 | Failures appear late, repeated fixes are manual, or quality depends on memory. / 失败发现太晚、重复修复依赖人工或质量依赖记忆。 | Add explicit check, feedback, and exit criteria. / 增加明确检查、反馈和退出条件。 |
| poor-handoff | 交接不良 | Ownership or next action is unclear. / 负责人或下一步不清。 | Add routing, handoff contract, or collaboration checkpoint. / 增加路由、交接契约或协作检查点。 |
| missing-memory | 记忆缺失 | Decisions, context, or lessons are repeatedly rediscovered. / 决策、上下文或经验被反复重新发现。 | Add memory capture and retrieval. / 增加记忆沉淀与检索。 |
| weak-governance | 治理薄弱 | Risk, permission, audit, or quality gates are implicit. / 风险、权限、审计或质量门禁是隐性的。 | Add explicit governance gate or trace. / 增加明确治理门禁或追踪。 |

## Mode Shift Playbook / 模式调整手册

| Current Symptom / 当前症状 | Likely Shift / 可能调整 | Example Pattern / 示例模式 |
| --- | --- | --- |
| Every request follows the same slow path. / 所有请求都走同一条慢路径。 | Chain to routing / 链式转路由 | Context Triage, Complexity-Based Routing, Tool Dispatch / 上下文分诊、复杂度路由、工具分派 |
| Work waits even though subtasks are independent. / 子任务独立却仍互相等待。 | Chain to parallel / 链式转并行 | Fan-Out/Gather, Parallel Exploration, Multi-Modal Fusion / 扇出汇聚、并行探索、多模态融合 |
| The workflow loses context between attempts. / 多次尝试之间上下文丢失。 | Chain to memory loop / 链式转记忆循环 | Failure Diary, Self-Heal Loop / 失败日记、自愈循环 |
| Many tools and roles must stay consistent. / 多个工具和角色必须保持一致。 | Chain or parallel to orchestration / 链式或并行转编排 | Progressive Disclosure, Plan-and-Execute, Observability Harness / 渐进披露、计划并执行、可观测性框架 |
| Failures are discovered too late. / 失败发现太晚。 | Add reflection or governance gate / 增加反思或治理门禁 | Generator-Critic, Approval Gate, Self-Heal Loop / 生成器-批评器、审批门禁、自愈循环 |
| Work scope is too large for one actor. / 工作范围过大，单一参与者无法承担。 | Add hierarchy / 增加层级 | Hierarchical Delegation, Blast Radius Control, Experience Replay / 层级委派、爆炸半径控制、经验回放 |

## Recommendation Shape / 建议输出格式

For every recommended change, include: / 每条修改建议包含：

- What to change / 改什么
- Why it is needed / 为什么需要
- How to modify the workflow / 如何修改工作流
- Affected nodes and matrix cells / 影响的节点和交织点
- Observability metrics / 可观测性指标
- Verification method / 验证方式
- Risk or tradeoff / 风险或取舍
