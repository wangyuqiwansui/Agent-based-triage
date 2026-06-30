# Trace Insert / Trace 插入

Use Trace as an inserted evidence layer before pattern selection. Do not run the Pattern Selection Card until the engineering node has enough current data. / 在模式选型前，将 Trace 作为插入式证据层。工程节点数据不足时，不要直接运行模式选型卡。

## Purpose / 目的

Trace Insert captures the full node picture first: trigger, actors, inputs, outputs, current behavior, risks, observed failures, and existing trace evidence. / Trace 插入先采集完整节点画像：触发、参与者、输入、输出、当前行为、风险、已观察失败和既有 Trace 证据。

Use existing `references/patterns/<capability-key>/trace.md` entries when available. If no Trace exists, mark it as initial planning and create a trace recommendation for later execution. / 如已有 `references/patterns/<capability-key>/trace.md`，必须读取并使用。若没有 Trace，则标记为初次规划，并提出后续追踪建议。

## Automatic Engineering Node Analysis / 工程节点自动分析

When a request asks to analyze an engineering node, automatically run Trace Insert / 自动运行 Trace 插入 before any Pattern Selection Card / 模式选型卡 decision. / 当请求是分析工程节点时，在任何模式选型卡决策前自动运行 Trace 插入。

Do not skip directly to matrix selection. First capture node evidence, then run ASSESS, ROUTE, and SELECT. / Do not skip directly to matrix selection. 先采集节点证据，再执行评估、判拓扑和查矩阵。

If node evidence is incomplete, return the missing evidence list and stop before final pattern selection. / 如果节点证据不完整，输出缺失证据清单，并在最终模式选择前停止。

## Node Evidence / 节点证据

Collect these fields before ASSESS, ROUTE, and SELECT: / 在 ASSESS、ROUTE、SELECT 前采集以下字段：

| Field | 中文 | What To Capture / 采集内容 |
| --- | --- | --- |
| Engineering Node / 工程节点 | 工程节点 | Node name, responsibility, owner, and boundary. / 节点名称、职责、负责人和边界。 |
| Trigger / 触发 | 触发 | What starts this node. / 什么触发该节点。 |
| Inputs / 输入 | 输入 | Required context, artifacts, signals, and constraints. / 所需上下文、产物、信号和约束。 |
| Outputs / 输出 | 输出 | Decision, artifact, state change, handoff, or trace. / 决策、产物、状态变化、交接或追踪。 |
| Current Behavior / 当前行为 | 当前行为 | How the node runs today. / 节点当前如何运行。 |
| Failure Signals / 失败信号 | 失败信号 | Delays, rework, missed risks, wrong owners, or repeated rediscovery. / 延迟、返工、风险遗漏、归属错误或重复发现。 |
| Risk Level / 风险等级 | 风险等级 | Permission, data, production, compliance, cost, or quality impact. / 权限、数据、生产、合规、成本或质量影响。 |
| Trace Evidence / Trace 证据 | Trace 证据 | Prior outcomes, logs, lessons, and repeated patterns. / 既往结果、日志、经验和重复模式。 |

## Readiness Gate / 就绪门

Proceed only when the node has enough evidence to compare current behavior with matrix fit signals. / 只有当节点证据足以与交织表适配信号比较时，才进入下一步。

- Ready / 已就绪: node responsibility, inputs, outputs, risk, and at least one observed symptom are known. / 已知节点职责、输入、输出、风险和至少一个已观察症状。
- Not ready / 未就绪: ask for or collect missing node data, then stop before pattern selection. / 缺少节点数据时，先补采数据，并在模式选型前停止。
- Initial planning / 初次规划: if no Trace exists, explicitly state that selection is based on current node evidence only. / 若无 Trace，明确说明选型仅基于当前节点证据。

## Pattern Selection Card / 模式选型卡

Run this card after Trace Insert has produced enough node data. It locates the engineering node by ASSESS, ROUTE, and SELECT, then turns the selected pattern into a plan. / 在 Trace 插入产出足够节点数据后运行本卡片。通过 ASSESS、ROUTE、SELECT 定位工程节点，再把所选模式转化为规划。

### ASSESS / 评估

Determine which cognitive capability the engineering node primarily needs. / 判断该工程节点主要需要哪类认知能力。

| Capability / 能力 | Use When / 何时选择 |
| --- | --- |
| Perception / 感知 | The node must collect, inspect, parse, normalize, or classify signals. / 节点需要采集、检查、解析、标准化或分类信号。 |
| Memory / 记忆 | The node depends on retained context, lessons, decisions, history, or retrieval. / 节点依赖保留上下文、经验、决策、历史或检索。 |
| Reasoning / 推理 | The node must infer, compare, decompose, diagnose, or choose. / 节点需要推断、比较、拆解、诊断或选择。 |
| Action / 行动 | The node changes code, data, documents, tickets, systems, or operational state. / 节点改变代码、数据、文档、工单、系统或运行状态。 |
| Reflection / 反思 | The node evaluates output quality, learns from results, or revises assumptions. / 节点评估产出质量、从结果学习或修正假设。 |
| Collaboration / 协作 | The node coordinates actors, reviewers, roles, owners, or handoffs. / 节点协调参与者、评审者、角色、负责人或交接。 |
| Governance / 治理 | The node controls permission, policy, auditability, safety, quality, or compliance. / 节点控制权限、策略、审计、安全、质量或合规。 |

### ROUTE / 判拓扑

Judge the main running shape quickly. Do not calculate precisely; use the dominant operating shape and risk override. / 快速判断系统主运行形态，不需要精确计算；使用主导运行形态和风险覆盖规则。

| Signal / 信号 | Candidate Modes / 候选模式 |
| --- | --- |
| 低协作 + 短任务 / Low collaboration + short task | Chain / Route |
| 中等复杂 + 多步骤 / Medium complexity + multi-step | Orchestration / Loop |
| 多专家 + 宽任务 / Many experts + broad task | Parallel / Hierarchy |
| 高风险动作 / High-risk action | Governance Routing / Chain / Hierarchy first / 治理路由、链式或层级优先 |

Use Chain for ordered steps, Routing for conditional paths, Parallel for independent streams, Orchestration for controller-managed dependencies, Loop for feedback and exit criteria, and Hierarchy for recursive or layered decomposition. / 有序步骤用链式，条件路径用路由，独立流用并行，控制器管理依赖用编排，反馈与退出条件用循环，递归或分层拆解用层级。

### SELECT / 查矩阵

Inspect `matrix-index.md`, then read the vertical introduction and the dedicated pattern file. Select at least one pattern; use a hybrid when the node needs more than one capability or mode. / 检查 `matrix-index.md`，再读取纵轴导论和独立模式文件。至少选择一个模式；当节点需要多个能力或模式时使用混合模式。

Every selected pattern has two required Markdown files: `<cell-key>.md` for `Design Pattern / 设计模式` and `<cell-key>-observability.md` for `Observability Metrics / 可观测性指标`. / 每个已选模式都有两个必读 Markdown 文件：`<cell-key>.md` 存放 `Design Pattern / 设计模式`，`<cell-key>-observability.md` 存放 `Observability Metrics / 可观测性指标`。

Selection order / 选择顺序：

1. Read `references/patterns/<capability-key>/cell.md`. / 读取对应纵轴导论。
2. Read `references/patterns/<capability-key>/<capability-key>-<mode-key>.md`. / 读取对应交织点设计模式文件。
3. Read `references/patterns/<capability-key>/<capability-key>-<mode-key>-observability.md`. / 读取对应交织点可观测性指标文件。
4. Use the design file to understand the workflow adjustment. / 使用设计文件理解工作流调整方式。
5. Use the observability file to define quality, latency, cost, risk, and Trace observation. / 使用可观测性文件定义质量、时延、成本、风险和 Trace 观察。
6. If the cell is an extension candidate, read `extension-rules.md` before inventing a new pattern. / 若单元是扩展候选，先读扩展规则，再提出新模式。
7. For multi-mode plans, name the primary pattern first and supporting patterns second. / 多模式规划中，先列主模式，再列支撑模式。

## Plan / 规划

Turn the selected pattern into workflow changes. / 将所选模式转化为工作流修改。

Use this output shape: / 使用以下输出结构：

- Engineering Node / 工程节点
- Node Evidence / 节点证据
- ASSESS Result / 评估结果
- ROUTE Result / 拓扑判断
- SELECT Result / 查矩阵结果
- Selected Patterns / 已选模式
- Observability Metrics / 可观测性指标
- Trace Evidence / Trace 证据
- Plan / 规划
- Risks And Governance / 风险与治理
- Verification / 验证
- Trace Update / Trace 更新

## Constraints / 约束

- Do not use the Pattern Selection Card before Trace Insert has enough node data. / Trace 插入尚未获得足够节点数据前，不要使用模式选型卡。
- Do not force a node into the 7x6 matrix when an extension candidate better explains the workflow. / 当扩展候选更能解释工作流时，不要强行塞入 7x6 交织表。
- Treat Trace as evidence, not as an automatic decision rule. / 将 Trace 视为证据，而不是自动决策规则。
- For high-risk actions, consider governance before finalizing the mode. / 对高风险动作，最终确定模式前优先考虑治理。
