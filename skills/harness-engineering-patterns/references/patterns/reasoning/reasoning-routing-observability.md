# Complexity-Based Routing / 复杂度路由 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-routing / 推理 x 路由
Capability / 能力: Reasoning / 推理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-routing.md](reasoning-routing.md)
Shared Probe Suite / 共享探针套件: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)
Metric Registry / 指标注册表: [`metric_registry.json`](../../../runtime/metric_registry.json)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Complexity-Based Routing / 复杂度路由 improves the workflow after selection or application. / 使用以下指标观察 Complexity-Based Routing / 复杂度路由 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `route_stability_rate` (no route-insufficiency switch; explicitly not accuracy), `outcome_route_accuracy` (outcome-backed or independently audited sufficiency), `underroute_rate`, `overroute_rate`, and per-tier validated acceptance rate. / `route_stability_rate`（未因路由不足而换路，明确不等于准确率）、`outcome_route_accuracy`（由真实结果或独立审计支撑的充分性）、欠路由率、过路由率和各档位验证后采纳率。
- 时延指标 / Latency Metrics: classifier decision latency, per-tier end-to-end latency, and escalation delay (time lost when a request bounces from a low tier to a higher one). / 分类器决策时延、各档位端到端时延、升级延迟（请求从低档反弹到高档损失的时间）。
- 成本指标 / Cost Metrics: token spend per tier, blended cost per request versus single-deep-path baseline (article anchor: RouteLLM ~85% reduction), and misroute cost (wasted deep-tier tokens plus rework tokens from failed cheap-tier runs). / 各档位 token 消耗、单请求混合成本对比单一深路径基线（论文锚点：RouteLLM 约降 85%）、误路由成本（浪费的深档 token 加低档失败返工 token）。
- 风险指标 / Risk Metrics: escalation-loop count (same request escalating more than once, watch `FAIL_0007`), high-impact requests served by System 1, router abstention rate, and forced-route count when required typed signals were missing or unknown. / 升级循环次数（同一请求升级超过一次，对应 `FAIL_0007`）、高影响请求被直觉档处理的数量、路由弃权率，以及必需类型化信号缺失或未知时仍强制路由的次数。
- Trace 指标 / Trace Metrics: route decision record completeness (mode, topology, typed signals, policy version, reason codes, signal fingerprint, and abstention), escalation event coverage, and misroute audit closure rate. / 路由决策记录完整率（模式、拓扑、类型化信号、策略版本、原因码、信号指纹和弃权状态）、升级事件覆盖率、误路由审计闭环率。

### Required Probe Coverage / 必需探针覆盖

Enable task identity (`PROBE_0001`), contract completeness (`PROBE_0002`), route decision (`PROBE_0003`), budget and resources (`PROBE_0004`), step closure (`PROBE_0005`), evidence chain (`PROBE_0006`), drift (`PROBE_0010`), validation (`PROBE_0011`), stop and escalation (`PROBE_0012`), outcome (`PROBE_0013`) for any accuracy, under-route, over-route, or acceptance claim, privacy and governance (`PROBE_0014`), and probe self-health (`PROBE_0015`). / 启用任务身份、契约完整性、路由决策、预算与资源、步骤闭环、证据链、漂移、验证、停止升级、结果回接（任何准确率、欠路由、过路由或采纳率判断均必需）、隐私治理和探针自健康探针。

Record initial and final modes, observable routing signals, route reason, switch trigger, budget impact, and whether a switch was caused by route insufficiency or an external environment change. If no explicit router event exists, report only `observed_mode`; do not infer design intent. / 记录初始与最终模式、可观测路由信号、路由原因、换路触发、预算影响，以及换路由路由不足还是外部环境变化引起。不存在显式路由事件时，只报告 `observed_mode`，不得推断设计意图。

Version every metric definition and bucket by scene, risk, initial/final mode, evidence grade, validator, model, tool, and outcome availability. Treat missing route reasons as missing, not as wrong or correct routes. / 每个指标口径版本化，并按场景、风险、初始/最终模式、证据等级、验证器、模型、工具和后验可用性分桶。路由原因缺失应保留为缺失，不计为正确或错误。

### Default Gate Suggestions / 默认门控建议

- Alert on gate-eligible `route_stability_rate` only as an operational stability signal, never as route correctness. / 仅将可用于门控的 `route_stability_rate` 作为运行稳定性信号告警，绝不能解释为路由正确性。
- Keep `outcome_route_accuracy` diagnostic until outcome-linkage coverage is implemented and meets an owned minimum threshold; preserve audited over-route and under-route reason labels for diagnosis. / 在后验关联覆盖率实现并达到负责人设定的最低阈值前，`outcome_route_accuracy` 仅作诊断；同时保留经审计的过路由与欠路由原因标签。
- Require a trace entry for every escalation or de-escalation. Allow an explicit switch to direct or deterministic work after critical uncertainty is resolved; block unrecorded or unsupported de-escalation. / 每次升级或降档都必须留 Trace 记录。关键不确定性解决后允许显式切换到直接或确定性工作；阻断未记录或无证据支持的降档。
