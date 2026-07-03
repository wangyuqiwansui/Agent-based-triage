# Hierarchical Delegation / 层级委派 Observability Metrics / 可观测性指标

Cell / 交织点: collaboration-hierarchy / 协作 x 层级
Capability / 能力: Collaboration / 协作
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [collaboration-hierarchy.md](collaboration-hierarchy.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Hierarchical Delegation / 层级委派 improves the workflow after selection or application. / 使用以下指标观察 Hierarchical Delegation / 层级委派 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `rollup_fidelity` (sampled audit of layer summaries against underlying item verdicts), `exception_survival_rate` (item-level exceptions and minority findings reaching the manager verbatim), and `domain_defect_catch_rate` versus the generalist-review baseline. / `rollup_fidelity`（层摘要对照底层条目裁定的抽样审计吻合度）、`exception_survival_rate`（条目级例外与少数派发现原样到达管理者的比例）、`domain_defect_catch_rate`（领域缺陷捕获率对比通才评审基线）。
- 时延指标 / Latency Metrics: `per_layer_handoff_latency` (brief down plus result up per boundary), `portfolio_completion_time` versus the flat-coordination baseline (article anchor: 500 contracts in 8 hours), and gather-point queue time per layer. / `per_layer_handoff_latency`（每边界任务书下发加结果上卷耗时）、`portfolio_completion_time`（整体完成时间对比扁平协调基线，论文锚点：8 小时 500 份合同）、每层汇集点排队时间。
- 成本指标 / Cost Metrics: coordination tokens per layer, `upward_clarification_cost` (spend on sub-agents asking for missing context — brief-quality signal), and layer-maintenance overhead versus throughput gained. / 每层协调 token、`upward_clarification_cost`（子智能体向上追问缺失上下文的开销——任务书质量信号）、层级维护开销对比换得的吞吐。
- 风险指标 / Risk Metrics: `boundary_dispute_count` (work claimed by no layer or two layers, watch `FAIL_0008`), `layer_skip_count` (managers reading item verdicts directly or workers reporting past their lead), `exception_drop_incidents` at gather points (each is a mini `FAIL_0013`), and cross-layer permission jumps without `GOV_0001` approval. / `boundary_dispute_count`（无层认领或两层争抢的工作数，对应 `FAIL_0008`）、`layer_skip_count`（管理者直读条目裁定或执行者越级上报的次数）、汇集点 `exception_drop_incidents`（每个都是小型 `FAIL_0013`）、未经 `GOV_0001` 审批的跨层权限跃迁。
- Trace 指标 / Trace Metrics: `delegation_chain_completeness` (brief, verdict, roll-up recorded at every boundary, per `GOV_0002` — deeper hierarchy raises `FAIL_0010` exposure), brief self-containment rate (briefs needing no upward clarification), and escalation closure rate per layer. / `delegation_chain_completeness`（每边界的任务书、裁定、上卷记录完整率，按 `GOV_0002`——层级越深 `FAIL_0010` 暴露越大）、任务书自足率（无需向上追问的任务书比例）、每层升级闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert when `exception_survival_rate` falls or `upward_clarification_cost` climbs — the former means gather points are flattening minority findings (`FAIL_0013`), the latter means briefs are no longer self-contained and layer boundaries are eroding (`FAIL_0008`). / `exception_survival_rate` 下降或 `upward_clarification_cost` 上升即告警——前者说明汇集点正在抹平少数派发现（`FAIL_0013`），后者说明任务书不再自足、层边界正在侵蚀（`FAIL_0008`）。
- Block a layer's roll-up from promoting upward when its audit records are incomplete per `GOV_0002` or open exceptions lack dispositions; under 100 items, recommend dismantling the layer per Law 4 rather than paying its overhead. / 层的审计记录按 `GOV_0002` 不完整或未决例外缺处置时，阻断其上卷晋级；条目不足 100 时按定律 4 建议撤层而非继续支付其开销。
