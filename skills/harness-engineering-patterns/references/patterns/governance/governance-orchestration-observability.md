# Observability Harness / 可观测性框架 Observability Metrics / 可观测性指标

Cell / 交织点: governance-orchestration / 治理 x 编排
Capability / 能力: Governance / 治理
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-orchestration.md](governance-orchestration.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Observability Harness / 可观测性框架 improves the workflow after selection or application. / 使用以下指标观察 Observability Harness / 可观测性框架 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `replay_answerability` (sampled audit questions — who did what when, on what evidence — answered fully from the harness), `evidence_join_rate` (events joinable to trace and actor), and `gate_evidence_freshness` (age of evidence consumed by gate verdicts). / `replay_answerability`（抽样审计问题——谁何时凭何证据做了什么——可完全由支架回答的比例）、`evidence_join_rate`（可关联到 trace 与行为者的事件比例）、`gate_evidence_freshness`（门控裁定所耗证据的新鲜度）。
- 时延指标 / Latency Metrics: `capture_overhead` (per-action logging cost relative to action time), `alert_routing_latency` (breach to owner notification), and `replay_reconstruction_time` (audit question to evidenced answer, versus the manual-archaeology baseline). / `capture_overhead`（单动作日志成本相对动作耗时）、`alert_routing_latency`（突破到负责人收到通知的时延）、`replay_reconstruction_time`（审计提问到带证据回答的耗时，对比人工考古基线）。
- 成本指标 / Cost Metrics: storage and retention spend per risk class, `capture_scope_efficiency` (full-capture share of trivial reversible actions — over-collection signal), and postmortem or regulatory-response effort avoided. / 每风险等级的存储与保留开销、`capture_scope_efficiency`（琐碎可逆动作被全量采集的占比——采集过度信号）、避免的复盘或监管响应投入。
- 风险指标 / Risk Metrics: `capture_gap_count` (actions, decisions, or approvals with no event record — each is live `FAIL_0010`), `harness_blind_window` (time gates ran while the harness was degraded), `alert_flood_rate` (alerts per owner per day, watch `FAIL_0011` fatigue), and unauthorized evidence access (violates least privilege within `GOV_0003`). / `capture_gap_count`（无事件记录的动作、决策或审批数——每个都是现行 `FAIL_0010`）、`harness_blind_window`（支架降级期间门控仍在运行的时长）、`alert_flood_rate`（每负责人每日告警量，对应 `FAIL_0011` 疲劳）、越权访问证据事件（违反 `GOV_0003` 内最小权限）。
- Trace 指标 / Trace Metrics: `correlation_scheme_conformance` (events carrying actor, action, timestamp, trace id — the `GOV_0002` implementation measure), gate-verdict evidence annotation coverage, and alert-to-resolution closure rate. / `correlation_scheme_conformance`（事件携带行为者、动作、时间戳、trace id 的合规率——`GOV_0002` 的实现度量）、门控裁定的证据标注覆盖率、告警到解决的闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert on `capture_gap_count` above zero for irreversible or approval-gated action classes and on any `harness_blind_window` — gaps in those classes are live `FAIL_0010`, and a blind window means gates fired on silence. / 不可逆或需审批动作类的 `capture_gap_count` 大于零即告警，任何 `harness_blind_window` 同样告警——这些类别的缺口就是现行 `FAIL_0010`，盲窗意味着门控在静默上触发过。
- Block gate verdicts and Progressive Commitment promotions when their required evidence streams are degraded, stale, or unjoinable — dependent gates fail closed per the harness rules instead of passing on assumptions. / 所需证据流降级、过期或不可关联时，阻断门控裁定与渐进承诺晋级——依赖门控按支架规则失效关闭，而不是基于假设放行。
