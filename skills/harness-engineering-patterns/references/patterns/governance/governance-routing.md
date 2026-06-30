# Approval Gate / 审批门禁

Cell / 交织点: governance-routing / 治理 x 路由
Capability / 能力: Governance / 治理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Governance / 治理 x Routing / 路由 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Governance / 治理 x Routing / 路由 映射到该单元。
- 问题 / Problem: Autonomous work sometimes crosses risk, permission, or policy boundaries where continuation requires explicit approval. / 自主工作有时会跨越风险、权限或策略边界，继续推进需要明确审批。
- 架构方案 / Architectural Solution: Route decisions through a policy gate that approves, blocks, escalates, or requests more evidence based on risk. / 通过策略门禁路由决策，根据风险批准、阻断、升级或请求更多证据。
- 工程权衡 / Engineering Trade-offs: Improves safety and accountability, but introduces bottlenecks and requires calibrated thresholds. / 提升安全和问责，但引入瓶颈并需要校准阈值。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when risk or permission determines whether work can continue. / 当风险或权限决定工作能否继续时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Approval Gate / 审批门禁.
- 诊断用途 / Diagnostic Use: Use when risk or permission determines whether work can continue. / 当风险或权限决定工作能否继续时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 需求进入、治理审查 / Intake, governance review.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 风险、权限或合规等级决定路径 / Risk, permission, or compliance level determines the path.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [governance-routing-observability.md](governance-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
