# Hierarchical Retrieval / 层级检索

Cell / 交织点: memory-routing / 记忆 x 路由
Capability / 能力: Memory / 记忆
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Memory / 记忆 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Memory / 记忆 x Routing / 路由 in arXiv:2605.13850. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Memory / 记忆 x Routing / 路由 映射到该单元。
- 问题 / Problem: The matrix lists this named pattern for the cell; use it when the workflow must route retrieval through levels of memory. Core fit signal: History, project knowledge, or decisions choose the path. / 矩阵在该单元列出此命名模式；当工作流必须按记忆层级路由检索时使用。核心适配信号：需要按历史案例、项目知识或决策记录选择路径。
- 架构方案 / Architectural Solution: Use Hierarchical Retrieval / 层级检索 to classify first, then route to the right path, owner, tool, or depth / 先分类，再路由到合适路径、负责人、工具或深度 within the Memory / 记忆 capability. / 在 Memory / 记忆 能力内使用 Hierarchical Retrieval / 层级检索，classify first, then route to the right path, owner, tool, or depth / 先分类，再路由到合适路径、负责人、工具或深度。
- 工程权衡 / Engineering Trade-offs: Routing saves effort, but wrong classification can send work down the wrong path. / 路由节省成本，但错误分类会把工作送到错误路径。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when the workflow must route retrieval through levels of memory. / 当工作流必须按记忆层级路由检索时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Hierarchical Retrieval / 层级检索.
- 诊断用途 / Diagnostic Use: Use when the workflow must route retrieval through levels of memory. / 当工作流必须按记忆层级路由检索时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 需求进入、协作交接 / Intake, collaboration handoff.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 需要按历史案例、项目知识或决策记录选择路径 / History, project knowledge, or decisions choose the path.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [memory-routing-observability.md](memory-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
