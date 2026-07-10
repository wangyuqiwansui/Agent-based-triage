# Hierarchical Delegation / 层级委派

Cell / 交织点: collaboration-hierarchy / 协作 x 层级
Capability / 能力: Collaboration / 协作
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Hierarchical Delegation lets a manager obtain specialized expertise from domain-specific sub-agents: goals decompose downward as self-contained briefs, each layer decides only at its own abstraction, and structured results roll upward with evidence. / 层级委派让管理者从领域专精的子智能体获取专业能力：目标以自足任务书逐层下发，每层只在自己的抽象层做决策，结构化结果携证据逐层上卷。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Collaboration / 协作 x Hierarchy / 层级 (Hierarchy / 层级).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; 矩阵列名模式 / Matrix-listed pattern; the article's legal case runs partner to associate to clause-level review over 500 contracts in 8 hours, and Environmental Constraint Law 4 stacks this pattern on Fan-Out/Gather at 100-500 items; source table maps Collaboration / 协作 x Hierarchy / 层级 in arXiv:2605.13850. / 代表性定义 / Representative definition；矩阵列名模式 / Matrix-listed pattern；论文法律案例以合伙人-律师-条款级评审的层级在 8 小时内处理 500 份合同，环境约束定律 4 规定 100-500 项规模在扇出汇集之上叠加本模式；来源表将 Collaboration / 协作 x Hierarchy / 层级 映射到该单元。
- 问题 / Problem: A single coordinator directly driving hundreds of work items drowns in detail it lacks expertise to judge: flat fan-out returns more results than one aggregator can absorb, generalist review misses domain-specific defects, and nobody holds a view of the whole above the item level. / 单一协调者直接驱动数百工作项会淹死在它无专业能力判断的细节里：扁平扇出返回的结果超出单个聚合者的吸收极限、通才评审漏掉领域特有缺陷、条目层之上没有任何人持有全局视图。
- 架构方案 / Architectural Solution: Organize work as delegation layers — manager, domain leads, item-level workers — where briefs travel down self-contained (goal, constraints, acceptance criteria, no implicit context) and results travel up structured (verdict, evidence, exceptions); each layer decides only at its abstraction, sizes per Law 4 (stack hierarchy on Fan-Out/Gather at 100-500 items, re-derive locally per Law 5), and each layer's gather point is treated as its own aggregation bottleneck. / 把工作组织为委派层——管理者、领域负责人、条目级执行者——任务书自足下发（目标、约束、验收标准、无隐式上下文），结果结构化上卷（裁定、证据、例外）；每层只在自己的抽象层决策，规模按定律 4 定（100-500 项在扇出汇集上叠加层级，按定律 5 本地重推），每层汇集点都当作独立的聚合瓶颈对待。
- 工程权衡 / Engineering Trade-offs: Hierarchy buys specialization and scale beyond a flat gather's absorption limit, but every layer adds handoff latency, an aggregation point that can drop minority findings, and a longer audit chain — under 100 items flat Fan-Out/Gather (collaboration-parallel) is cheaper, and sequential single-owner flows belong in Handoff Chain (collaboration-chain). / 层级买来专业化与超出扁平汇集吸收极限的规模，但每层都增加交接时延、一个可能丢弃少数派发现的聚合点和更长的审计链——100 项以下扁平扇出汇集（collaboration-parallel）更便宜，顺序单负责人流程则归交接链（collaboration-chain）。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when work should be delegated from high-level goals to subteams or subagents. / 当工作应从高层目标委派到子团队或子 Agent 时使用。

### Delegation Layer Model / 委派层级模型

| Layer / 层 | Role / 角色 | Decision Scope / 决策范围 | Downward Input / 下发输入 | Upward Output / 上卷输出 |
| --- | --- | --- | --- | --- |
| Manager / 管理者 | Goal owner (e.g., partner). / 目标负责人（如合伙人）。 | Priorities, risk acceptance, final verdict. / 优先级、风险接受、最终裁定。 | Self-contained briefs to domain leads. / 给领域负责人的自足任务书。 | Portfolio verdict with rolled-up evidence. / 带上卷证据的整体裁定。 |
| Domain lead / 领域负责人 | Specialist coordinator (e.g., associate). / 专精协调者（如律师）。 | Domain method, item assignment, exception triage. / 领域方法、条目分配、例外分诊。 | Item briefs with acceptance criteria. / 带验收标准的条目任务书。 | Domain summary, exceptions, minority findings. / 领域摘要、例外、少数派发现。 |
| Item worker / 条目执行者 | Narrow-scope executor (e.g., clause reviewer). / 窄域执行者（如条款评审）。 | Single-item verdicts only. / 仅单条目裁定。 | One item plus its criteria. / 单条目及其标准。 | Structured verdict with evidence. / 带证据的结构化裁定。 |

Sizing and boundary rules / 规模与边界规则:

- Law 4 sizing: under 10 items no collaboration pattern, 10-50 flat Fan-Out/Gather (collaboration-parallel), 100-500 stack this hierarchy on top, continuous streams add routing and autoscaling; thresholds re-derive locally per Law 5. / 定律 4 规模：10 项以下不用协作模式，10-50 项用扁平扇出汇集（collaboration-parallel），100-500 项在其上叠加本层级，持续流再加路由与自动扩缩；阈值按定律 5 本地重推。
- Briefs are self-contained: a sub-agent needing to ask upward for missing context signals a boundary defect, not a communication style. / 任务书必须自足：子智能体需要向上追问缺失上下文即边界缺陷，而非沟通风格问题。
- Layers never skip: the manager reads domain summaries, not item verdicts — but each layer's gather preserves exceptions and minority findings verbatim. / 层级不可跨越：管理者读领域摘要而非条目裁定——但每层汇集须原样保留例外与少数派发现。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Hierarchical Delegation / 层级委派.
- 诊断用途 / Diagnostic Use: Use when work should be delegated from high-level goals to subteams or subagents. / 当工作应从高层目标委派到子团队或子 Agent 时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 问题拆解、治理审查 / Decomposition, governance review.
- 当前症状 / Current Symptoms: One coordinator drowns driving hundreds of items directly and becomes the throughput ceiling; generalist review misses domain-specific defects; sub-agents constantly ask upward for missing context; item-level exceptions vanish before reaching the decision maker. / 单一协调者直接驱动数百条目而淹没，成为吞吐天花板；通才评审漏掉领域特有缺陷；子智能体不断向上追问缺失上下文；条目级例外在到达决策者之前就消失。
- 适配信号 / Fit Signals: 协作需要按角色、权限、责任或任务层级组织 / Collaboration is organized by role, permission, responsibility, or task level.
- 调整方向 / Adjustment Direction: Insert domain-lead layers between the goal owner and item workers: self-contained briefs down, structured evidence up, each layer deciding only at its abstraction. / 在目标负责人与条目执行者之间插入领域负责人层：自足任务书下发、结构化证据上卷、每层只在自己的抽象层决策。
- 修改方式 / How To Modify: 1) Confirm scale justifies hierarchy per Law 4 (100-500 items; below that use collaboration-parallel). 2) Define layers, roles, and each layer's decision scope. 3) Template the downward brief (goal, constraints, acceptance criteria) and upward result (verdict, evidence, exceptions). 4) Treat each gather point as an aggregation bottleneck with explicit exception preservation. 5) Record layer boundaries and roll-ups per `GOV_0002`. / 1）按定律 4 确认规模值得层级（100-500 项；以下用 collaboration-parallel）；2）定义层、角色与每层决策范围；3）模板化下发任务书（目标、约束、验收标准）与上卷结果（裁定、证据、例外）；4）把每个汇集点当聚合瓶颈处理，显式保留例外；5）层边界与上卷按 `GOV_0002` 入账。
- 输入 / Inputs: Goal and portfolio of items, layer and role definitions, brief and result templates, Law 4 sizing verdict, per-layer permission scopes. / 目标与条目组合、层与角色定义、任务书与结果模板、定律 4 规模裁定、每层权限范围。
- 输出 / Outputs: Delegation tree with recorded briefs, per-layer structured results with evidence, exception and minority-finding ledger, portfolio verdict with an auditable roll-up chain. / 带任务书记录的委派树、每层带证据的结构化结果、例外与少数派发现台账、带可审计上卷链的整体裁定。
- 风险与治理 / Risks & Governance: Unclear layer boundaries are `FAIL_0008` — every brief declares decision scope and a sub-agent asking upward flags a boundary defect; each layer's gather is a mini `FAIL_0013` aggregation bottleneck — preserve exceptions and minority findings verbatim through every roll-up; deeper hierarchy lengthens the audit chain toward `FAIL_0010` — record briefs, verdicts, and roll-ups per `GOV_0002` at every boundary; cross-layer permission jumps route through approval per `GOV_0001`. / 层边界不清是 `FAIL_0008`——每份任务书声明决策范围，子智能体向上追问即边界缺陷；每层汇集是小型 `FAIL_0013` 聚合瓶颈——例外与少数派发现须原样穿过每次上卷；层级越深审计链越长、越逼近 `FAIL_0010`——每个边界的任务书、裁定与上卷按 `GOV_0002` 入账；跨层权限跃迁按 `GOV_0001` 走审批。

Observability Metrics File / 可观测性指标文件: [collaboration-hierarchy-observability.md](collaboration-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
