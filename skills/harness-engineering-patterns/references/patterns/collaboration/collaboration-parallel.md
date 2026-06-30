# Fan-Out/Gather / 扇出汇聚

Cell / 交织点: collaboration-parallel / 协作 x 并行
Capability / 能力: Collaboration / 协作
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Collaboration / 协作 x Parallel / 并行 (Parallel / 并行).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Collaboration / 协作 x Parallel / 并行 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Collaboration / 协作 x Parallel / 并行 映射到该单元。
- 问题 / Problem: One actor cannot cover all perspectives or independent subtasks quickly enough. / 单一参与者无法足够快地覆盖所有视角或独立子任务。
- 架构方案 / Architectural Solution: Fan out independent work to multiple agents or contributors, then gather results into a synthesis step. / 将独立工作扇出给多个 Agent 或贡献者，再将结果汇聚到综合步骤。
- 工程权衡 / Engineering Trade-offs: Improves speed and diversity, but requires de-duplication, conflict resolution, and synthesis ownership. / 提升速度和多样性，但需要去重、冲突解决和综合责任。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when several contributors can work independently before synthesis. / 当多个贡献者可独立工作后再综合时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Fan-Out/Gather / 扇出汇聚.
- 诊断用途 / Diagnostic Use: Use when several contributors can work independently before synthesis. / 当多个贡献者可独立工作后再综合时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 方案设计、执行实现 / Design, implementation.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 多个参与者可独立工作并在约定点合并 / Multiple participants can work independently and merge at agreed points.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [collaboration-parallel-observability.md](collaboration-parallel-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
