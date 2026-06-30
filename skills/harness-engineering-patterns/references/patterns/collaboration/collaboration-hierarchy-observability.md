# Hierarchical Delegation / 层级委派 Observability Metrics / 可观测性指标

Cell / 交织点: collaboration-hierarchy / 协作 x 层级
Capability / 能力: Collaboration / 协作
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [collaboration-hierarchy.md](collaboration-hierarchy.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Hierarchical Delegation / 层级委派 improves the workflow after selection or application. / 使用以下指标观察 Hierarchical Delegation / 层级委派 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: Track output acceptance, defect or rework rate, and whether the fit signal is satisfied. / 跟踪产出采纳率、缺陷或返工率，以及适配信号是否满足。
- 时延指标 / Latency Metrics: Track time from node trigger to usable output, including waiting, routing, iteration, and handoff time. / 跟踪从节点触发到可用输出的耗时，包括等待、路由、迭代和交接时间。
- 成本指标 / Cost Metrics: Track tool calls, token or compute spend, human review effort, and repeated work avoided. / 跟踪工具调用、Token 或计算成本、人工评审投入，以及避免的重复工作。
- 风险指标 / Risk Metrics: Track policy violations, permission escalations, unsafe actions, missed checks, and blast-radius changes. / 跟踪策略违规、权限升级、不安全动作、遗漏检查和影响范围变化。
- Trace 指标 / Trace Metrics: Track trace completeness, evidence freshness, outcome comparison, and whether follow-up actions are closed. / 跟踪 Trace 完整性、证据新鲜度、结果对比和后续动作是否关闭。
