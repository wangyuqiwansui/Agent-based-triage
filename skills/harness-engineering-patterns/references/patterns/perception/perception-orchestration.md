# Progressive Disclosure / 渐进披露

Cell / 交织点: perception-orchestration / 感知 x 编排
Capability / 能力: Perception / 感知
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Progressive Disclosure orchestrates observation tools, state sources, and dependency views in expanding layers — digest overview first, focused component detail on demand, raw logs and data last — where every expansion requires an explicit trigger signal instead of default full injection. / 渐进披露把观察工具、状态源与依赖视图编排成逐层展开——先摘要总览、按需聚焦组件细节、最后才是原始日志与数据——每次展开都需要显式触发信号，绝不默认全量注入。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Perception / 感知 x Orchestration / 编排 (Orchestration / 编排).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Perception / 感知 x Orchestration / 编排 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Perception / 感知 x Orchestration / 编排 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: With many observation tools and state sources, both extremes fail: injecting everything by default floods the context with irrelevant logs and metrics until the signal drowns, while hard-hiding detail starves diagnosis — the agent reasons from a summary when the defect lives three layers down in a raw log line. / 观察工具与状态源一多，两个极端都会失败：默认全量注入让无关日志与指标灌满上下文直至信号淹没，而硬性隐藏细节又饿死诊断——缺陷藏在三层之下的原始日志行里，智能体却只能对着摘要推理。
- 架构方案 / Architectural Solution: Orchestrate observation in three layers — digest (status overview across tools and dependencies), focused (detail for the component under suspicion), raw (raw logs and data) — where each expansion fires only on an explicit trigger signal (anomalous metric, diagnostic need, gate demand), each layer carries a budget cap with a reclaim rule, and expansion decisions are recorded per `GOV_0002`; Context Triage (perception-routing) decides what is visible at all and its L3 deferred-read handles are exactly this pattern's expansion mechanism — Triage governs admission, Disclosure governs when admitted material unfolds. / 把观测编排为三层——摘要层（跨工具与依赖的状态总览）、聚焦层（疑点组件的细节）、原始层（原始日志与数据）——每次展开只由显式触发信号点火（指标异常、诊断需要、门控索取），每层带预算上限与回收规则，展开决策按 `GOV_0002` 入账；上下文分诊（perception-routing）决定什么可见，其 L3 延迟读取句柄正是本模式的展开机制——分诊管准入，披露管已准入材料何时展开。
- 工程权衡 / Engineering Trade-offs: Layered disclosure keeps the context budget spent on suspects instead of background noise, but every expansion adds a round trip, trigger thresholds need tuning per Law 5, and over-tight layers starve diagnosis exactly when incidents demand breadth — the reclaim rule must return budget when suspicion clears, or the layers ratchet open and converge on full injection anyway. / 分层披露让上下文预算花在疑点而非背景噪音上，但每次展开多一次往返、触发阈值需按定律 5 调校，层收得过紧又恰在事故最需要广度时饿死诊断——回收规则必须在疑点排除后收回预算，否则层层棘轮张开、最终仍收敛于全量注入。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when context should be revealed by a controller as the workflow needs it. / 当上下文应由控制器按工作流需要逐步披露时使用。

### Disclosure Layer Model / 披露层级模型

| Layer / 层 | Content / 内容 | Expansion Trigger / 展开触发 | Budget Cap / 预算上限 | Reclaim Rule / 回收规则 |
| --- | --- | --- | --- | --- |
| Digest / 摘要层 | Status overview: health per tool, dependency state, top anomalies. / 状态总览：各工具健康度、依赖状态、头部异常。 | Always present — the resting state. / 常驻——静息状态。 | Fixed small share of context. / 固定的小份上下文。 | Refreshed in place, never grows. / 原地刷新，永不增长。 |
| Focused / 聚焦层 | Component-level detail: recent errors, metric series, config of the suspect. / 组件级细节：疑点组件的近期错误、指标序列、配置。 | Anomalous digest metric or stated diagnostic need. / 摘要指标异常或声明的诊断需要。 | Per-component allotment. / 按组件配额。 | Collapse when suspicion clears. / 疑点排除即折叠。 |
| Raw / 原始层 | Raw logs, dumps, full payloads via deferred-read handles. / 经延迟读取句柄的原始日志、转储、完整载荷。 | Focused layer insufficient for a named question. / 聚焦层不足以回答具名问题。 | Windowed reads, never whole streams. / 窗口式读取，绝不整流注入。 | Evict after the question is answered. / 问题回答后即逐出。 |

Disclosure rules / 披露规则:

- Every expansion names its trigger: "expand X because signal Y" — expansion without a recorded trigger is drift back toward full injection. / 每次展开点名触发信号："因信号 Y 展开 X"——无记录触发的展开就是向全量注入回漂。
- Boundary with Context Triage (perception-routing): Triage decides what is admissible at all; Disclosure decides when admitted material unfolds — its raw layer rides Triage's L3 deferred-read handles. / 与上下文分诊（perception-routing）的边界：分诊决定什么可准入，披露决定已准入材料何时展开——原始层复用分诊的 L3 延迟读取句柄。
- Incident mode may pre-widen the focused layer for the affected subsystem, but the reclaim rule still applies when the incident closes. / 事故模式可为受影响子系统预先放宽聚焦层，但事故关闭后回收规则照常生效。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Progressive Disclosure / 渐进披露.
- 诊断用途 / Diagnostic Use: Use when context should be revealed by a controller as the workflow needs it. / 当上下文应由控制器按工作流需要逐步披露时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 运行监控、事故修复 / Monitoring, incident repair.
- 当前症状 / Current Symptoms: Monitoring context is dominated by healthy-system noise while the one anomalous signal scrolls past unnoticed; diagnosis stalls because raw evidence was summarized away; every incident starts by dumping all logs into context and the budget is gone before reasoning starts. / 监控上下文被健康系统的噪音占满，唯一异常信号却无人注意地滚过；诊断因原始证据被摘要掉而卡住；每次事故都以把全部日志灌进上下文开场，推理还没开始预算已耗尽。
- 适配信号 / Fit Signals: 多个观察工具、状态和依赖需要统一协调 / Multiple observation tools, states, and dependencies need coordination.
- 调整方向 / Adjustment Direction: Orchestrate observation into digest-focused-raw layers with explicit expansion triggers, budget caps, and reclaim rules. / 把观测编排为摘要-聚焦-原始三层，配显式展开触发、预算上限与回收规则。
- 修改方式 / How To Modify: 1) Build the digest layer: per-tool health, dependency state, top anomalies in a fixed budget. 2) Define focused-layer views per component and their expansion triggers (anomaly thresholds, diagnostic needs). 3) Wire the raw layer through deferred-read handles (perception-routing L3) with windowed reads. 4) Set budget caps and reclaim rules per layer; tune thresholds per Law 5. 5) Record every expansion decision and trigger per `GOV_0002`. / 1）建摘要层：固定预算内的各工具健康度、依赖状态、头部异常；2）按组件定义聚焦层视图及其展开触发（异常阈值、诊断需要）；3）原始层经延迟读取句柄（perception-routing L3）窗口式接入；4）为每层设预算上限与回收规则，阈值按定律 5 调校；5）每次展开决策与触发按 `GOV_0002` 入账。
- 输入 / Inputs: Observation tool inventory and state sources, dependency map, anomaly thresholds per signal, layer budget caps, deferred-read handle mechanism. / 观察工具清单与状态源、依赖图、每信号异常阈值、层预算上限、延迟读取句柄机制。
- 输出 / Outputs: Resting digest view, expansion events with named triggers, focused and raw disclosures within caps, reclaim events, expansion decision log. / 静息摘要视图、带具名触发的展开事件、上限内的聚焦与原始披露、回收事件、展开决策日志。
- 风险与治理 / Risks & Governance: Default full injection is `FAIL_0001` context pollution — require a named trigger for every expansion and audit triggerless ones; over-tight layers starve diagnosis into `FAIL_0012` — monitor how often answers required raw-layer reads and loosen thresholds per Law 5 when starvation shows; ratchet drift (layers that open but never reclaim) converges on full injection — enforce reclaim on suspicion clearing; expansion decisions are recorded per `GOV_0002` so post-incident review can see what was visible when. / 默认全量注入是 `FAIL_0001` 上下文污染——每次展开必须具名触发，审计无触发展开；层收过紧把诊断饿成 `FAIL_0012`——监控回答问题需要原始层读取的频率，饥饿显现时按定律 5 放宽阈值；棘轮漂移（只开不收的层）终将收敛于全量注入——疑点排除即强制回收；展开决策按 `GOV_0002` 入账，事后复盘可见何时什么可见。

Observability Metrics File / 可观测性指标文件: [perception-orchestration-observability.md](perception-orchestration-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
