# Observability Harness / 可观测性框架

Cell / 交织点: governance-orchestration / 治理 x 编排
Capability / 能力: Governance / 治理
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Observability Harness runs a central monitor that orchestrates logging, tracing, metrics, and alerting across the whole workflow, so every action, decision, and approval leaves a replayable record and governance gates consume live evidence instead of assumptions. / 可观测性框架以中央监控编排全工作流的日志、追踪、指标与告警，让每个动作、决策与审批都留下可回放记录，治理门控消费实时证据而非假设。

### Dedicated execution specification / 专用执行规格

For the complete request-to-business-result workflow, read [the 13 execution stages](../../observability-execution-flow.md#execution-steps), [45 probes and 50 metric definitions](../../observability-probes.md#probe-catalog) and [the event, state and completion contract](../../observability-contract.md). Freeze the authoritative outcome source before dispatch, preserve raw state, reconcile unknown effects, check every public commitment and persist unresolved work across run closure. / 完整的请求到业务结果流程请读专用执行、探针指标及事件状态补全契约；派发前固定权威结果源，保留原始状态，对账未知效果，核验每项对外承诺，运行关闭后仍持久保留未解决工作。

This `0.1.0` supplement preserves `PATTERN_0049` and draft maturity. Its [source aliases and unmodified snapshots](../../observability-source-map.json) are evidence, not new patterns or executable attachment instructions. Shared `PATTERN_0052` `0.8.0` and governance `GOV_BOUNDARY_OBS` retain their own contracts. All dedicated behavior and OBM metrics are specification-only; adoption requires explicit adapters and recorded scenario acceptance. / 本扩展保留现有模式及草案成熟度；来源别名与原文快照是证据，不是新模式或可执行附件指令。共享探针及治理观测各保留自身契约；专用行为与 OBM 指标均为规格，接入须有显式适配器及场景验收证据。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Orchestration / 编排 (Orchestration / 编排).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; 矩阵列名模式 / Matrix-listed pattern; the article's lending case mandates full audit logging under regulatory requirements, grounding a central monitor that orchestrates observation across the workflow; source table maps Governance / 治理 x Orchestration / 编排 in arXiv:2605.13850. / 代表性定义 / Representative definition；矩阵列名模式 / Matrix-listed pattern；论文信贷案例在监管要求下强制全量审计日志，落定由中央监控编排全流程观测；来源表将 Governance / 治理 x Orchestration / 编排 映射到该单元。
- 问题 / Problem: When each component logs on its own terms, the record is unjoinable: incidents cannot be replayed end to end, approvals cannot be matched to the evidence they relied on, gates fire on stale or missing signals, and the audit that regulators or postmortems demand simply does not exist — non-replayable audit is the default state, not the exception. / 当各组件各自为政地记日志时，记录无法关联：事故无法端到端回放、审批对不上其依赖的证据、门控在过期或缺失的信号上触发，监管或复盘所要求的审计根本不存在——审计不可回放是默认状态而非例外。
- 架构方案 / Architectural Solution: Stand up a harness of five orchestrated components — event log, trace store, metric aggregator, alert router, audit replay — with one correlation scheme across them (every event carries actor, action, timestamp, trace id); the harness is the implementation mechanism of `GOV_0002` and exists to eliminate `FAIL_0010`, and its evidence streams feed evaluation and gates (the Gate Sufficiency Rule in governance-routing consumes them for its structural-plus-semantic dual check, and Progressive Commitment promotions consume them as soak evidence). / 立起五组件编排的支架——事件日志、追踪存储、指标聚合器、告警路由器、审计回放——五者共用一套关联方案（每条事件携带行为者、动作、时间戳、trace id）；支架是 `GOV_0002` 的实现机制、其存在就是为消灭 `FAIL_0010`，其证据流供给评估与门控（governance-routing 的门控充分性规则用它做结构加语义双重检查，渐进承诺的晋级用它做浸泡证据）。
- 工程权衡 / Engineering Trade-offs: A central harness makes evidence joinable and gates trustworthy, but it adds capture overhead to every action, can create an evidence dependency whose outage affects gates lacking required local evidence, and over-collection bloats storage while under-collection recreates the audit gaps it exists to close — capture scope follows risk class, re-derived locally per Law 5. / 中央支架让证据可关联、门控可信，但它给每个动作增加采集开销、自身故障会影响缺少必要本地证据的门控，采集过度撑爆存储、采集不足又重造它本要消灭的审计缺口——采集范围随风险等级定，按定律 5 本地重推。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when workflows must prove business outcomes, preserve raw state, reconcile asynchronous effects and bind public claims to auditable evidence. / 当工作流需要证明业务结果、保留原始状态、对账异步副作用，并把对外承诺绑定到可审计证据时使用。

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
- Monitor the harness and identify which evidence is mandatory for each action. Missing mandatory local controls or evidence blocks affected dispatches under policy; an optional probe outage records a gap while sufficiently controlled execution may continue. / 监控支架并明确每种动作的必要证据；必要本地控制或证据缺失时按策略阻断受影响派发；可选探针中断时记录缺口，控制完备的执行可继续。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Observability Harness / 可观测性框架.
- 诊断用途 / Diagnostic Use: Use when workflows must prove business outcomes, preserve raw state, reconcile asynchronous effects and bind public claims to auditable evidence. / 当工作流需要证明业务结果、保留原始状态、对账异步副作用，并把对外承诺绑定到可审计证据时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 发布交付、事故修复 / Delivery, incident repair.
- 当前症状 / Current Symptoms: Incidents cannot be replayed because each component logs incompatibly; approvals exist but nobody can show what evidence they relied on; gates pass on assumptions because live metrics are missing; a regulator or postmortem asks "who did what when" and the answer takes days of manual archaeology. / 事故无法回放因为各组件日志互不兼容；审批存在却拿不出其依赖的证据；门控因缺实时指标而基于假设放行；监管或复盘问"谁在何时做了什么"，答案要靠数天人工考古。
- 适配信号 / Fit Signals: 治理需要协调策略、审批、证据、工具和追踪 / Governance coordinates policy, approval, evidence, tools, and traceability.
- 调整方向 / Adjustment Direction: Stand up the five-component harness with one correlation scheme, and rewire gates to consume its live evidence streams. / 立起五组件支架、统一关联方案，并把门控改接其实时证据流。
- 修改方式 / How To Modify: 1) Define the correlation scheme (actor, action, timestamp, trace id on every event). 2) Stand up the five components and wire capture points at every action, decision, and approval. 3) Set capture scope by risk class per Law 5. 4) Rewire gates and Progressive Commitment promotions to consume harness evidence (Gate Sufficiency Rule dual check). 5) Monitor the harness, preserve minimum local audit, and apply configured blocking only where mandatory evidence or controls are unavailable. / 1）定义关联方案（每条事件带行为者、动作、时间戳、trace id）；2）立起五组件，在每个动作、决策、审批处接采集点；3）按定律 5 以风险等级定采集范围；4）门控与渐进承诺晋级改接支架证据（门控充分性规则双重检查）；5）监控支架、保留本地最小审计，仅在必要证据或控制不可用时按配置阻断。
- 输入 / Inputs: Workflow action and decision points, risk classification per action class, correlation scheme, storage and retention budgets, gate evidence requirements. / 工作流动作与决策点、每类动作的风险分级、关联方案、存储与保留预算、门控证据需求。
- 输出 / Outputs: Joinable event log, trace store, and metric streams; routed alerts with context; audit replay answering who-did-what-when with evidence; gate verdicts annotated with the evidence they consumed. / 可关联的事件日志、追踪存储与指标流；携上下文的路由告警；能带证据回答"谁何时做了什么"的审计回放；标注所耗证据的门控裁定。
- 风险与治理 / Risks & Governance: The harness is the implementation mechanism of `GOV_0002` and exists to eliminate `FAIL_0010` — capture gaps recreate exactly that failure, so audit the capture points themselves; an observation outage requires dependency-aware handling — retain local controls and block only affected actions missing mandatory evidence; alert floods breed `FAIL_0011` approval fatigue — route by severity with context instead of broadcasting; captured evidence contains sensitive actions, so access follows least privilege within `GOV_0003` boundaries and high-risk alert escalations go per `GOV_0001`. / 支架是 `GOV_0002` 的实现机制、其存在就是为消灭 `FAIL_0010`——采集缺口会重造这一失败，故采集点本身也要审计；观测故障应按依赖处置——保留本地控制，仅阻断缺少必要证据的受影响动作；告警洪水滋生 `FAIL_0011` 审批疲劳——按严重度携上下文路由而非广播；采集证据含敏感动作，访问在 `GOV_0003` 边界内按最小权限，高风险告警升级按 `GOV_0001`。

### Module Attachment / 模块工程挂载

Identity / 身份: `CELL_GOVERNANCE_ORCHESTRATION; PATTERN_0049`. Existing names and maturity stay unchanged. / 保持现有名称与成熟度不变。

Coordinate proposal, policy, approval, reservation, dispatch, verification, and evidence collection while leaving final business authority at the execution entry point. / 编排提案、策略、审批、预留、派发、核验与证据采集，同时将最终业务控制权留在执行入口。

Read the maintained [execution flow / 执行流程](../../governance-execution-flow.md#execution-steps) (执01–16、探01–12) and [shared contract / 共享契约](../../governance-contract.md). These are specification-only engineering extensions from the supplied lesson-36 documents; this card does not provide a dedicated production runtime or make an existing runtime implement `GOV_BOUNDARY_OBS`. / 阅读维护版执行流程与共享契约。这些内容是用户第 36 讲资料的规范级工程扩展；本卡不提供专用生产运行时，也不表示既有运行时已实现 `GOV_BOUNDARY_OBS`。

| Attachment point / 落点 | Required behavior and evidence / 必要行为与证据 |
| --- | --- |
| Evidence graph / 证据关联图 | Correlate tenant, run, logical action, attempt, proposal/policy digests, event identity, and source references. Preserve occurred_at separately from ingested_at; trace IDs alone do not prove causality. / 关联租户、运行、逻辑动作、尝试、提案与策略摘要、事件身份及来源引用；区分发生与采集时间，trace ID 本身不证明因果。 |
| Probe feedback / 探针反馈 | Accept only validated append-only observation_enrichment fields with source, target version, expiry, and per-field acknowledgement; stale or cross-tenant patches conflict or are rejected. / 仅接受经过校验的追加式 observation_enrichment 字段，附来源、目标版本、有效期和逐字段回执；过期或跨租户补丁应冲突或拒绝。 |
| Re-entry / 重新进入 | If recovered evidence affects an unmet execution condition, send it back through governance decision and final checks. A control recommendation is not a stop, approval, rollback, or business result. / 补回证据影响未满足执行条件时，重新进入治理裁决与最终检查；控制建议不等于已停止、已批准、已回滚或业务结果。 |

Boundary / 边界: The observation service is optional; execution retains local identity, policy, budget, idempotency, final checks, and minimum durable audit. Its outage alone does not halt every flow. Missing necessary controls or evidence blocks affected operations under the configured policy; offline probes only report findings and candidate patches. / 观测服务可选；执行侧保留本地身份、策略、预算、幂等、最终检查及最小持久审计。探针离线本身不阻断所有流程；必要控制或证据缺失时按配置策略阻断受影响操作，离线探针只输出发现与候选补丁。

Acceptance references / 验收引用: 执验17–21、探验03–08、12–21、26–28; use the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These are expected checks, not claims that production tests passed. / 这些是待验证的预期，不代表生产测试已通过。

Metric references / 指标引用: 指18–30、35–36; definitions, denominators, and unavailable states live in the [metric catalog / 指标目录](../../governance-observability-probes.md#metric-catalog). Permission and verified business success are separate results. / 口径、分母及不可用状态由指标目录统一定义；合规许可与已核实业务成功分开记录。

Observability Metrics File / 可观测性指标文件: [governance-orchestration-observability.md](governance-orchestration-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
