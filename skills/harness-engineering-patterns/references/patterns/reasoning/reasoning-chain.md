# Chain-of-Thought / 思维链

Cell / 交织点: reasoning-chain / 推理 x 链式
Capability / 能力: Reasoning / 推理
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reasoning / 推理 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Reasoning / 推理 x Chain / 链式 in arXiv:2605.13850. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Reasoning / 推理 x Chain / 链式 映射到该单元。
- 问题 / Problem: The matrix lists this named pattern for the cell; use it when reasoning should proceed through ordered intermediate conclusions. Core fit signal: Reasoning steps have clear ordered dependencies. / 矩阵在该单元列出此命名模式；当推理需要经过有序中间结论时使用。核心适配信号：推理步骤存在明确前后依赖。
- 架构方案 / Architectural Solution: Use Chain-of-Thought / 思维链 to apply the pattern as an ordered sequence whose outputs feed the next step / 将模式作为输出逐步传递的有序序列应用 within the Reasoning / 推理 capability. / 在 Reasoning / 推理 能力内使用 Chain-of-Thought / 思维链，apply the pattern as an ordered sequence whose outputs feed the next step / 将模式作为输出逐步传递的有序序列应用。
- 工程权衡 / Engineering Trade-offs: Sequential flow is easy to audit, but weak when branching or feedback dominates. / 顺序流程易审计，但当分支或反馈占主导时较弱。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when reasoning should proceed through ordered intermediate conclusions. / 当推理需要经过有序中间结论时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Chain-of-Thought / 思维链.
- 诊断用途 / Diagnostic Use: Use when reasoning should proceed through ordered intermediate conclusions. / 当推理需要经过有序中间结论时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 问题拆解、方案设计 / Decomposition, design.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 推理步骤存在明确前后依赖 / Reasoning steps have clear ordered dependencies.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [reasoning-chain-observability.md](reasoning-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
