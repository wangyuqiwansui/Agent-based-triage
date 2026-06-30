# Parallel Exploration / 并行探索

Cell / 交织点: reasoning-parallel / 推理 x 并行
Capability / 能力: Reasoning / 推理
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reasoning / 推理 x Parallel / 并行 (Parallel / 并行).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Reasoning / 推理 x Parallel / 并行 in arXiv:2605.13850. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Reasoning / 推理 x Parallel / 并行 映射到该单元。
- 问题 / Problem: The matrix lists this named pattern for the cell; use it when Use when independent hypotheses or solution paths should be explored together. / 当多个独立假设或方案路径应同时探索时使用。 Core fit signal: 多个假设、方案或根因可以独立推理后比较 / Multiple hypotheses, designs, or causes can be reasoned about independently and compared. / 矩阵在该单元列出此命名模式；当 Use when independent hypotheses or solution paths should be explored together. / 当多个独立假设或方案路径应同时探索时使用。 时使用。核心适配信号：多个假设、方案或根因可以独立推理后比较 / Multiple hypotheses, designs, or causes can be reasoned about independently and compared。
- 架构方案 / Architectural Solution: Use Parallel Exploration / 并行探索 to run independent branches together and merge with explicit synthesis / 并行运行独立分支，并通过显式综合合并 within the Reasoning / 推理 capability. / 在 Reasoning / 推理 能力内使用 Parallel Exploration / 并行探索，run independent branches together and merge with explicit synthesis / 并行运行独立分支，并通过显式综合合并。
- 工程权衡 / Engineering Trade-offs: Parallel work increases coverage, but merge conflicts and duplicate effort must be managed. / 并行提升覆盖，但必须管理合并冲突和重复劳动。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when independent hypotheses or solution paths should be explored together. / 当多个独立假设或方案路径应同时探索时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Parallel Exploration / 并行探索.
- 诊断用途 / Diagnostic Use: Use when independent hypotheses or solution paths should be explored together. / 当多个独立假设或方案路径应同时探索时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 方案设计、事故修复 / Design, incident repair.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 多个假设、方案或根因可以独立推理后比较 / Multiple hypotheses, designs, or causes can be reasoned about independently and compared.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [reasoning-parallel-observability.md](reasoning-parallel-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
