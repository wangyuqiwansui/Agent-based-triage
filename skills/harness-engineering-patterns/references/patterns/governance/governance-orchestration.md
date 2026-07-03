# Observability Harness / 可观测性框架

Cell / 交织点: governance-orchestration / 治理 x 编排
Capability / 能力: Governance / 治理
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Observability Harness runs a central monitor that orchestrates logging, tracing, metrics, and alerting across the whole workflow, so every action, decision, and approval leaves a replayable record and governance gates consume live evidence instead of assumptions. / 可观测性框架以中央监控编排全工作流的日志、追踪、指标与告警，让每个动作、决策与审批都留下可回放记录，治理门控消费实时证据而非假设。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Orchestration / 编排 (Orchestration / 编排).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; 矩阵列名模式 / Matrix-listed pattern; the article's lending case mandates full audit logging under regulatory requirements, grounding a central monitor that orchestrates observation across the workflow; source table maps Governance / 治理 x Orchestration / 编排 in arXiv:2605.13850. / 代表性定义 / Representative definition；矩阵列名模式 / Matrix-listed pattern；论文信贷案例在监管要求下强制全量审计日志，落定由中央监控编排全流程观测；来源表将 Governance / 治理 x Orchestration / 编排 映射到该单元。
- 问题 / Problem: When each component logs on its own terms, the record is unjoinable: incidents cannot be replayed end to end, approvals cannot be matched to the evidence they relied on, gates fire on stale or missing signals, and the audit that regulators or postmortems demand simply does not exist — non-replayable audit is the default state, not the exception. / 当各组件各自为政地记日志时，记录无法关联：事故无法端到端回放、审批对不上其依赖的证据、门控在过期或缺失的信号上触发，监管或复盘所要求的审计根本不存在——审计不可回放是默认状态而非例外。
- 架构方案 / Architectural Solution: Stand up a harness of five orchestrated components — event log, trace store, metric aggregator, alert router, audit replay — with one correlation scheme across them (every event carries actor, action, timestamp, trace id); the harness is the implementation mechanism of `GOV_0002` and exists to eliminate `FAIL_0010`, and its evidence streams feed evaluation and gates (the Gate Sufficiency Rule in governance-routing consumes them for its structural-plus-semantic dual check, and Progressive Commitment promotions consume them as soak evidence). / 立起五组件编排的支架——事件日志、追踪存储、指标聚合器、告警路由器、审计回放——五者共用一套关联方案（每条事件携带行为者、动作、时间戳、trace id）；支架是 `GOV_0002` 的实现机制、其存在就是为消灭 `FAIL_0010`，其证据流供给评估与门控（governance-routing 的门控充分性规则用它做结构加语义双重检查，渐进承诺的晋级用它做浸泡证据）。
- 工程权衡 / Engineering Trade-offs: A central harness makes evidence joinable and gates trustworthy, but it adds capture overhead to every action, becomes a single point whose outage blinds all gates, and over-collection bloats storage while under-collection recreates the audit gaps it exists to close — capture scope follows risk class, re-derived locally per Law 5. / 中央支架让证据可关联、门控可信，但它给每个动作增加采集开销、自身故障会致盲所有门控，采集过度撑爆存储、采集不足又重造它本要消灭的审计缺口——采集范围随风险等级定，按定律 5 本地重推。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when governance requires coordinated evidence, traces, metrics, and review. / 当治理需要协调证据、追踪、指标和评审时使用。

### Harness Component Map / 支架组件图

| Component / 组件 | Captured Content / 采集内容 | Consumers / 消费方 | Missing Consequence / 缺失后果 |
| --- | --- | --- | --- |
| Event log / 事件日志 | Every action, decision, approval with actor and timestamp. / 每个动作、决策、审批及行为者与时间戳。 | Gates, audit replay, Experience Replay (reflection-hierarchy). / 门控、审计回放、经验回放（reflection-hierarchy）。 | Actions become deniable and unreviewable. / 动作变得不可追认、不可复审。 |
| Trace store / 追踪存储 | Causal chains linking events by trace id. / 以 trace id 关联事件的因果链。 | Incident diagnosis, delegation-chain audits. / 事故诊断、委派链审计。 | Incidents cannot be replayed end to end. / 事故无法端到端回放。 |
| Metric aggregator / 指标聚合器 | Pattern observability metrics, gate inputs, soak evidence. / 各模式可观测性指标、门控输入、浸泡证据。 | Gates, Progressive Commitment promotions, evaluation. / 门控、渐进承诺晋级、评估。 | Gates fire on stale or missing signals. / 门控在过期或缺失信号上触发。 |
| Alert router / 告警路由器 | Threshold breaches routed to owners with context. / 携上下文路由给负责人的阈值突破。 | On-call owners, approval escalation per `GOV_0001`. / 值守负责人、按 `GOV_0001` 的审批升级。 | Breaches discovered by accident, after damage. / 突破靠偶然发现、损害已成。 |
| Audit replay / 审计回放 | Reconstruction of any past decision with its evidence. / 任一历史决策及其证据的重建。 | Regulators, postmortems, dispute resolution. / 监管方、复盘、争议裁决。 | `FAIL_0010` — the audit exists but cannot answer questions. / `FAIL_0010`——审计虽在却答不了问题。 |

Harness rules / 支架规则:

- One correlation scheme everywhere: an event that cannot be joined to its trace and actor is a capture defect, not a formatting preference. / 全域一套关联方案：无法关联到 trace 与行为者的事件是采集缺陷，不是格式偏好。
- Capture scope follows risk class: irreversible and approval-gated actions get full capture; trivial reversible actions get summary capture — re-derive the split locally per Law 5. / 采集范围随风险等级：不可逆与需审批动作全量采集，琐碎可逆动作摘要采集——按定律 5 本地重推分界。
- The harness itself is monitored: gates that depend on its evidence must fail closed when the harness is degraded, not fire on silence. / 支架自身也被监控：依赖其证据的门控在支架降级时必须失效关闭，而不是在静默上照常触发。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Observability Harness / 可观测性框架.
- 诊断用途 / Diagnostic Use: Use when governance requires coordinated evidence, traces, metrics, and review. / 当治理需要协调证据、追踪、指标和评审时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 发布交付、事故修复 / Delivery, incident repair.
- 当前症状 / Current Symptoms: Incidents cannot be replayed because each component logs incompatibly; approvals exist but nobody can show what evidence they relied on; gates pass on assumptions because live metrics are missing; a regulator or postmortem asks "who did what when" and the answer takes days of manual archaeology. / 事故无法回放因为各组件日志互不兼容；审批存在却拿不出其依赖的证据；门控因缺实时指标而基于假设放行；监管或复盘问"谁在何时做了什么"，答案要靠数天人工考古。
- 适配信号 / Fit Signals: 治理需要协调策略、审批、证据、工具和追踪 / Governance coordinates policy, approval, evidence, tools, and traceability.
- 调整方向 / Adjustment Direction: Stand up the five-component harness with one correlation scheme, and rewire gates to consume its live evidence streams. / 立起五组件支架、统一关联方案，并把门控改接其实时证据流。
- 修改方式 / How To Modify: 1) Define the correlation scheme (actor, action, timestamp, trace id on every event). 2) Stand up the five components and wire capture points at every action, decision, and approval. 3) Set capture scope by risk class per Law 5. 4) Rewire gates and Progressive Commitment promotions to consume harness evidence (Gate Sufficiency Rule dual check). 5) Monitor the harness itself and make dependent gates fail closed on degradation. / 1）定义关联方案（每条事件带行为者、动作、时间戳、trace id）；2）立起五组件，在每个动作、决策、审批处接采集点；3）按定律 5 以风险等级定采集范围；4）门控与渐进承诺晋级改接支架证据（门控充分性规则双重检查）；5）监控支架自身，依赖门控在降级时失效关闭。
- 输入 / Inputs: Workflow action and decision points, risk classification per action class, correlation scheme, storage and retention budgets, gate evidence requirements. / 工作流动作与决策点、每类动作的风险分级、关联方案、存储与保留预算、门控证据需求。
- 输出 / Outputs: Joinable event log, trace store, and metric streams; routed alerts with context; audit replay answering who-did-what-when with evidence; gate verdicts annotated with the evidence they consumed. / 可关联的事件日志、追踪存储与指标流；携上下文的路由告警；能带证据回答"谁何时做了什么"的审计回放；标注所耗证据的门控裁定。
- 风险与治理 / Risks & Governance: The harness is the implementation mechanism of `GOV_0002` and exists to eliminate `FAIL_0010` — capture gaps recreate exactly that failure, so audit the capture points themselves; harness outage blinds every dependent gate — monitor it and fail closed rather than firing on silence; alert floods breed `FAIL_0011` approval fatigue — route by severity with context instead of broadcasting; captured evidence contains sensitive actions, so access follows least privilege within `GOV_0003` boundaries and high-risk alert escalations go per `GOV_0001`. / 支架是 `GOV_0002` 的实现机制、其存在就是为消灭 `FAIL_0010`——采集缺口会重造这一失败，故采集点本身也要审计；支架故障致盲所有依赖门控——监控它并失效关闭，而非在静默上照常触发；告警洪水滋生 `FAIL_0011` 审批疲劳——按严重度携上下文路由而非广播；采集证据含敏感动作，访问在 `GOV_0003` 边界内按最小权限，高风险告警升级按 `GOV_0001`。

Observability Metrics File / 可观测性指标文件: [governance-orchestration-observability.md](governance-orchestration-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
