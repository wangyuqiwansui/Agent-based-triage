# Blast Radius Control / 爆炸半径控制

Cell / 交织点: governance-hierarchy / 治理 x 层级
Capability / 能力: Governance / 治理
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Hierarchy / 层级 (Hierarchy / 层级).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Governance / 治理 x Hierarchy / 层级 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Governance / 治理 x Hierarchy / 层级 映射到该单元。
- 问题 / Problem: Agent actions can have outsized impact if permissions, rollout scope, or affected systems are not bounded. / 如果权限、发布范围或受影响系统没有边界，Agent 行动可能产生过大影响。
- 架构方案 / Architectural Solution: Limit impact by level: sandbox first, then narrow scope, then staged rollout, with escalation only after evidence supports it. / 按层级限制影响：先沙箱，再小范围，再分阶段发布，只有证据支持时才升级。
- 工程权衡 / Engineering Trade-offs: Contains risk and improves reversibility, but slows rollout and requires careful scope design. / 控制风险并提升可回滚性，但会放慢发布并需要谨慎设计范围。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when permissions, rollout, or impact must be limited by level. / 当权限、发布或影响范围必须按层级限制时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Blast Radius Control / 爆炸半径控制.
- 诊断用途 / Diagnostic Use: Use when permissions, rollout, or impact must be limited by level. / 当权限、发布或影响范围必须按层级限制时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 治理审查、方案设计 / Governance review, design.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 治理按风险、权限、组织或系统层级执行 / Governance executes by risk, permission, organization, or system level.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [governance-hierarchy-observability.md](governance-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
