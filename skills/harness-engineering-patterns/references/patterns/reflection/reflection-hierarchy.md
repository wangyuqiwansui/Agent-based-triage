# Experience Replay / 经验回放

Cell / 交织点: reflection-hierarchy / 反思 x 层级
Capability / 能力: Reflection / 反思
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reflection / 反思 x Hierarchy / 层级 (Hierarchy / 层级).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Reflection / 反思 x Hierarchy / 层级 in arXiv:2605.13850. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Reflection / 反思 x Hierarchy / 层级 映射到该单元。
- 问题 / Problem: The matrix lists this named pattern for the cell; use it when Use when reflection needs replay across levels of past attempts or lessons. / 当反思需要跨多层历史尝试或经验回放时使用。 Core fit signal: 评估需要按任务、模块、版本或风险层级进行 / Evaluation happens by task, module, version, or risk level. / 矩阵在该单元列出此命名模式；当 Use when reflection needs replay across levels of past attempts or lessons. / 当反思需要跨多层历史尝试或经验回放时使用。 时使用。核心适配信号：评估需要按任务、模块、版本或风险层级进行 / Evaluation happens by task, module, version, or risk level。
- 架构方案 / Architectural Solution: Use Experience Replay / 经验回放 to delegate or constrain work across levels with roll-up evidence / 跨层级委派或约束工作，并向上汇总证据 within the Reflection / 反思 capability. / 在 Reflection / 反思 能力内使用 Experience Replay / 经验回放，delegate or constrain work across levels with roll-up evidence / 跨层级委派或约束工作，并向上汇总证据。
- 工程权衡 / Engineering Trade-offs: Hierarchy scales depth, but level boundaries can hide context or accountability. / 层级可扩展深度，但层级边界可能隐藏上下文或责任。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when reflection needs replay across levels of past attempts or lessons. / 当反思需要跨多层历史尝试或经验回放时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Experience Replay / 经验回放.
- 诊断用途 / Diagnostic Use: Use when reflection needs replay across levels of past attempts or lessons. / 当反思需要跨多层历史尝试或经验回放时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 治理审查、知识沉淀 / Governance review, knowledge memory.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 评估需要按任务、模块、版本或风险层级进行 / Evaluation happens by task, module, version, or risk level.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [reflection-hierarchy-observability.md](reflection-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
