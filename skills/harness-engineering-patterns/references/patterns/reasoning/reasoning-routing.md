# Complexity-Based Routing / 复杂度路由

Cell / 交织点: reasoning-routing / 推理 x 路由
Capability / 能力: Reasoning / 推理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reasoning / 推理 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Reasoning / 推理 x Routing / 路由 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Reasoning / 推理 x Routing / 路由 映射到该单元。
- 问题 / Problem: Tasks vary widely in difficulty, so treating every request with the same reasoning depth wastes cost or under-solves hard cases. / 任务难度差异很大，对所有请求使用同样推理深度会浪费成本或低估困难案例。
- 架构方案 / Architectural Solution: Classify complexity first, then route simple cases to lightweight reasoning and hard cases to deeper planning, search, or review. / 先判断复杂度，再将简单案例路由到轻量推理，将困难案例路由到更深规划、搜索或评审。
- 工程权衡 / Engineering Trade-offs: Balances cost and capability, but misclassification can under-resource hard tasks or over-process simple ones. / 平衡成本与能力，但误分类会让难任务资源不足或让简单任务过度处理。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when problem complexity should determine the reasoning path. / 当问题复杂度应决定推理路径时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Complexity-Based Routing / 复杂度路由.
- 诊断用途 / Diagnostic Use: Use when problem complexity should determine the reasoning path. / 当问题复杂度应决定推理路径时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 需求进入、事故修复 / Intake, incident repair.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 需要通过判断把问题送往不同策略或专家路径 / Judgement routes the problem to different strategies or specialist paths.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [reasoning-routing-observability.md](reasoning-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
