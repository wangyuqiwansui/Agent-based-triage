# Trace Insert / Trace 插入

Use Trace as an inserted evidence layer before pattern selection. Incomplete evidence permits a preliminary card with gaps and verification tasks, but not final adoption. / 在模式选型前，将 Trace 作为插入式证据层。证据不足时可形成带缺口与验证任务的初步卡片，但不能作最终采用结论。

## Quick Navigation / 快速导航

Read this card for the quick entrypoint, [execution](pattern-selection-execution-flow.md) for S0–S10, [independent probes](pattern-selection-observability-probes.md) for evidence and metrics, and the [shared contract](pattern-selection-contract.md) for namespaces and append-only supplements. The [source map](pattern-selection-source-map.json) preserves both supplied drafts. / 本卡提供快捷入口，执行流程定义 S0–S10，独立探针定义证据及指标，共享契约统一命名空间和追加补全，来源映射保留两份提供的草案。

## Purpose / 目的

Trace Insert captures the full node picture first: trigger, actors, inputs, outputs, current behavior, risks, observed failures, and existing trace evidence. / Trace 插入先采集完整节点画像：触发、参与者、输入、输出、当前行为、风险、已观察失败和既有 Trace 证据。

Use existing `references/patterns/<capability-key>/trace.md` entries when available. If no Trace exists, mark it as initial planning and create a trace recommendation for later execution. / 如已有 `references/patterns/<capability-key>/trace.md`，必须读取并使用。若没有 Trace，则标记为初次规划，并提出后续追踪建议。

## Automatic Engineering Node Analysis / 工程节点自动分析

When a request asks to analyze an engineering node, automatically run Trace Insert / 自动运行 Trace 插入 before any Pattern Selection Card / 模式选型卡 decision. / 当请求是分析工程节点时，在任何模式选型卡决策前自动运行 Trace 插入。

Do not skip directly to matrix selection. First capture node evidence, then run ASSESS, ROUTE, and SELECT. / Do not skip directly to matrix selection. 先采集节点证据，再执行评估、判拓扑和查矩阵。

If node evidence is incomplete, return useful preliminary diagnosis plus missing evidence and validation work; stop only final adoption of unsupported patterns. / 如果节点证据不完整，返回有用的初步诊断、缺失证据及验证工作，仅停止无依据的最终模式采用。

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

This gate governs proposed pattern adoption, not whether a node can be reviewed. A workflow audit may use the evidence, correctness and baseline sections and retain an adequate node without entering selection. Static evidence can establish a concrete mismatch without a live incident; label the proof and do not infer observed frequency or runtime validation from it. / 此门判断拟采用模式是否就绪，不判断节点能否接受审查。工作流审计可使用证据、正确性及基线部分，直接保留已足够节点而不进入选型。静态证据可以在没有线上事故时证明具体偏差，但须注明证明性质，不能据此推断实际发生频率或运行验证结果。

Finalize only when the node has enough evidence to compare current behavior with candidate fit and acceptance criteria. / 只有节点证据足以比较当前行为、候选适配及验收标准时，才能定稿。

- Ready / 已就绪: node responsibility, inputs, outputs, risk, and at least one observed symptom or demonstrated behavioral mismatch are known. / 已知节点职责、输入、输出、风险，以及至少一个已观察症状或已证明的行为偏差。
- Not ready / 未就绪: collect missing data and label recommendations preliminary; do not claim successful validation. / 缺少节点数据时补采并将建议标为初步，不宣称验证成功。
- Initial planning / 初次规划: no historical Trace or observed symptom is required to propose a design; disclose assumptions and create a baseline validation task before adoption. / 初步设计不要求已有历史 Trace 或故障症状；披露假设，并在采用前建立基线验证任务。

## Minimum Solution First / 最小方案优先

Before ASSESS, define correct completion, correct safe exits, prohibited effects and authoritative verification (S0–S1), then actually evaluate the existing program, rules, workflow or template (S2). A sufficient baseline goes directly to S8 validation and S9 recording; `selected_patterns: []` is a valid outcome. / 评估前先定义正确完成、正确安全出口、禁止效果和权威验证（S0–S1），再实际评估现有程序、规则、流程或模板（S2）。基线足够可直达 S8 验证及 S9 归档；已选模式列表允许为空。

When gaps remain, diagnose D1–D12 and separate program, model and human responsibilities (S3–S4). Missing facts require authoritative queries or verification, not repeated model speculation. Every added call, role or topology needs an evidenced purpose and a comparison against the simpler alternative. / 有缺口时诊断 D1–D12 并拆分程序、模型与人工职责（S3–S4）。缺事实应查询权威源或核实，不能重复模型猜测。每次新增调用、角色或拓扑都需有据目的，并与更简单替代方案比较。

## Pattern Selection Card / 模式选型卡

After Trace Insert and the baseline check, use ASSESS, ROUTE and SELECT to design only the required changes. These are a quick view of S3–S7, not a substitute for S8 comparison or S10 reselection. / Trace 插入与基线检查后，通过评估、判拓扑及查矩阵设计必要改动；它们是 S3–S7 的快捷视图，不替代 S8 比较及 S10 重选型。

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

Determine who decides the next step, which dependencies are real and which responsibilities are independent. The following size signals are candidate prompts only; neither task size nor risk automatically requires orchestration or multiple Agents. / 判断谁决定下一步、实际依赖及独立责任。下方规模信号仅提示候选，任务大小和风险均不自动要求编排或多个 Agent。

| Signal / 信号 | Candidate Modes / 候选模式 |
| --- | --- |
| 低协作 + 短任务 / Low collaboration + short task | Chain / Route |
| 中等复杂 + 多步骤 / Medium complexity + multi-step | Orchestration / Loop |
| 多专家 + 宽任务 / Many experts + broad task | Parallel / Hierarchy |
| 高风险动作 / High-risk action | Review Governance Routing / Chain / Hierarchy controls without replacing the task topology by default. / 评估治理路由、链式或层级控制，不默认替换任务拓扑。 |

Use Chain for ordered steps, Routing for conditional paths, Parallel for independent streams, Orchestration for controller-managed dependencies, Loop for feedback and exit criteria, and Hierarchy for recursive or layered decomposition. / 有序步骤用链式，条件路径用路由，独立流用并行，控制器管理依赖用编排，反馈与退出条件用循环，递归或分层拆解用层级。

After the shape judgement, check the Environmental Constraint Laws / 环境约束定律 in `diagnosis-method.md`: time pressure bounds topology depth, action authority picks the governance pattern, failure-cost asymmetry tunes reflection, volume sizes collaboration, and parameters must be re-derived locally. / 形态判断后，对照 `diagnosis-method.md` 中的环境约束定律：时间压力限定拓扑深度，行动权限决定治理模式，失败成本不对称调校反思，处理量确定协作规模，参数必须本地重推。

### SELECT / 查矩阵

Inspect `matrix-index.md`, then read the relevant vertical introduction and dedicated pattern files. Select only patterns supported by the diagnosed gap; zero additional patterns is valid. For composition, choose one primary topology and scope each auxiliary to specific steps, dependencies, ownership, acceptance and failure routes. / 检查交织表、相关纵轴导论和模式文件，仅选择有诊断缺口支持的模式，允许不新增模式。组合时选一个主拓扑，每个辅助拓扑限定步骤、依赖、责任、验收与失败出口。

Every selected pattern has two required Markdown files: `<cell-key>.md` for `Design Pattern / 设计模式` and `<cell-key>-observability.md` for `Observability Metrics / 可观测性指标`. / 每个已选模式都有两个必读 Markdown 文件：`<cell-key>.md` 存放 `Design Pattern / 设计模式`，`<cell-key>-observability.md` 存放 `Observability Metrics / 可观测性指标`。

Selection order / 选择顺序：

1. Read `references/patterns/<capability-key>/cell.md`. / 读取对应纵轴导论。
2. Read `references/patterns/<capability-key>/<capability-key>-<mode-key>.md`. / 读取对应交织点设计模式文件。
3. Read `references/patterns/<capability-key>/<capability-key>-<mode-key>-observability.md`. / 读取对应交织点可观测性指标文件。
4. Use the design file to understand the workflow adjustment. / 使用设计文件理解工作流调整方式。
5. Use the observability file to define quality, latency, cost, risk, and Trace observation. / 使用可观测性文件定义质量、时延、成本、风险和 Trace 观察。
6. If the cell is an extension candidate, read `extension-rules.md` before inventing a new pattern. / 若单元是扩展候选，先读扩展规则，再提出新模式。
7. For multi-mode plans, name the primary pattern first and supporting patterns second, with scope, rationale, controls and prohibited combinations. Record why rejected candidates were unnecessary. / 多模式规划先列主模式再列支撑模式，说明范围、理由、控制及禁止组合，并记录未选候选为何不必要。

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

Link the card to the workflow specification, control checklist, same-set validation report and observation manifest. Record selected and rejected candidates, model necessity, actual business status and unverified items. Approval, submission and technical success do not imply business completion. / 卡片关联工作流说明、控制清单、同集验证报告与观测清单；记录已选和未选候选、模型必要性、实际业务状态及未验证项。批准、提交及技术成功不代表业务完成。

## Constraints / 约束

- Do not finalize a selection without current evidence and baseline validation; preliminary analysis remains useful. / 无当前证据与基线验证不得定稿选型，仍可提供初步分析。
- Do not force a node into the 7x6 matrix when an extension candidate better explains the workflow. / 当扩展候选更能解释工作流时，不要强行塞入 7x6 交织表。
- Treat Trace as evidence, not as an automatic decision rule. / 将 Trace 视为证据，而不是自动决策规则。
- For high-risk actions, consider governance before finalizing the mode. / 对高风险动作，最终确定模式前优先考虑治理。
- Observe through optional probes or manual records; append-only supplements cannot change business state, authorize effects or turn unknowns into facts. / 可通过可选探针或手工记录观察；追加补丁不能改业务状态、授权效果或把未知变成事实。
