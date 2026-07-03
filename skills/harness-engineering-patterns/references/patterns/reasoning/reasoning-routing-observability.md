# Complexity-Based Routing / 复杂度路由 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-routing / 推理 x 路由
Capability / 能力: Reasoning / 推理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-routing.md](reasoning-routing.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Complexity-Based Routing / 复杂度路由 improves the workflow after selection or application. / 使用以下指标观察 Complexity-Based Routing / 复杂度路由 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `route_accuracy` (sampled audit of whether the chosen tier could solve the request), `underroute_rate` (hard requests sent to System 1 that later failed), `overroute_rate` (simple requests sent to deep tiers), and per-tier acceptance rate. / `route_accuracy`（抽样审计所选档位能否解决请求）、`underroute_rate`（被送入直觉档后失败的难请求比例）、`overroute_rate`（被送入深档的简单请求比例）以及各档位采纳率。
- 时延指标 / Latency Metrics: classifier decision latency, per-tier end-to-end latency, and escalation delay (time lost when a request bounces from a low tier to a higher one). / 分类器决策时延、各档位端到端时延、升级延迟（请求从低档反弹到高档损失的时间）。
- 成本指标 / Cost Metrics: token spend per tier, blended cost per request versus single-deep-path baseline (article anchor: RouteLLM ~85% reduction), and misroute cost (wasted deep-tier tokens plus rework tokens from failed cheap-tier runs). / 各档位 token 消耗、单请求混合成本对比单一深路径基线（论文锚点：RouteLLM 约降 85%）、误路由成本（浪费的深档 token 加低档失败返工 token）。
- 风险指标 / Risk Metrics: escalation-loop count (same request escalating more than once, watch `FAIL_0007`), high-impact requests served by System 1, and share of route decisions made with confidence below threshold. / 升级循环次数（同一请求升级超过一次，对应 `FAIL_0007`）、高影响请求被直觉档处理的数量、低于置信阈值仍作出的路由决策占比。
- Trace 指标 / Trace Metrics: route decision record completeness (tier, signals, confidence per request), escalation event coverage, and misroute audit closure rate. / 路由决策记录完整率（每请求含档位、信号、置信度）、升级事件覆盖率、误路由审计闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert when `underroute_rate` exceeds `overroute_rate` on high-impact request classes — failure-cost asymmetry says under-routing is the expensive direction. / 当高影响请求类别的 `underroute_rate` 超过 `overroute_rate` 时告警——失败成本不对称意味着低估方向更昂贵。
- Block tier de-escalation inside a single request; require a trace entry for every escalation. / 阻止单请求内部降档；每次升级必须留 trace 记录。
