# Plan-and-Execute / 计划并执行

Cell / 交织点: action-orchestration / 行动 x 编排
Capability / 能力: Action / 行动
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Action / 行动 x Orchestration / 编排 (Orchestration / 编排).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Action / 行动 x Orchestration / 编排 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Action / 行动 x Orchestration / 编排 映射到该单元。
- 问题 / Problem: Direct execution can be brittle when tasks require multiple dependent actions and changing state. / 当任务需要多个相互依赖的行动和变化状态时，直接执行会很脆弱。
- 架构方案 / Architectural Solution: Separate planning from execution: create a plan, execute steps under coordination, observe results, and adjust when needed. / 将计划与执行分离：先制定计划，在协调下执行步骤，观察结果并按需调整。
- 工程权衡 / Engineering Trade-offs: Improves transparency and control, but plans can become stale and orchestration adds overhead. / 提升透明度和控制力，但计划可能过期，编排也会增加开销。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when actions need explicit planning, execution, and coordination. / 当行动需要明确计划、执行和协调时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Plan-and-Execute / 计划并执行.
- 诊断用途 / Diagnostic Use: Use when actions need explicit planning, execution, and coordination. / 当行动需要明确计划、执行和协调时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 发布交付、事故修复 / Delivery, incident repair.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 行动涉及多个工具、系统状态、依赖和回滚路径 / Actions involve tools, system state, dependencies, and rollback paths.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [action-orchestration-observability.md](action-orchestration-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
