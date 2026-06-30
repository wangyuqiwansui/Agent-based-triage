# Progress Tracking / 进度追踪

Cell / 交织点: memory-orchestration / 记忆 x 编排
Capability / 能力: Memory / 记忆
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Memory / 记忆 x Orchestration / 编排 (Orchestration / 编排).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Memory / 记忆 x Orchestration / 编排 in arXiv:2605.13850. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Memory / 记忆 x Orchestration / 编排 映射到该单元。
- 问题 / Problem: The matrix lists this named pattern for the cell; use it when Use when memory must coordinate status, milestones, and task state. / 当记忆需要协调状态、里程碑和任务状态时使用。 Core fit signal: 多个记忆来源、更新策略和使用点需要协调 / Multiple memory sources, refresh strategies, and use points need coordination. / 矩阵在该单元列出此命名模式；当 Use when memory must coordinate status, milestones, and task state. / 当记忆需要协调状态、里程碑和任务状态时使用。 时使用。核心适配信号：多个记忆来源、更新策略和使用点需要协调 / Multiple memory sources, refresh strategies, and use points need coordination。
- 架构方案 / Architectural Solution: Use Progress Tracking / 进度追踪 to let a controller coordinate state, tools, dependencies, and handoffs / 由控制器协调状态、工具、依赖和交接 within the Memory / 记忆 capability. / 在 Memory / 记忆 能力内使用 Progress Tracking / 进度追踪，let a controller coordinate state, tools, dependencies, and handoffs / 由控制器协调状态、工具、依赖和交接。
- 工程权衡 / Engineering Trade-offs: Orchestration improves coordination, but controller complexity and latency can grow. / 编排提升协调，但控制器复杂度和延迟可能增长。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when memory must coordinate status, milestones, and task state. / 当记忆需要协调状态、里程碑和任务状态时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Progress Tracking / 进度追踪.
- 诊断用途 / Diagnostic Use: Use when memory must coordinate status, milestones, and task state. / 当记忆需要协调状态、里程碑和任务状态时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 方案设计、事故修复 / Design, incident repair.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 多个记忆来源、更新策略和使用点需要协调 / Multiple memory sources, refresh strategies, and use points need coordination.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [memory-orchestration-observability.md](memory-orchestration-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
