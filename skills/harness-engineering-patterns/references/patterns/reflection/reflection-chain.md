# Generator-Critic / 生成器-批评器

Cell / 交织点: reflection-chain / 反思 x 链式
Capability / 能力: Reflection / 反思
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reflection / 反思 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Reflection / 反思 x Chain / 链式 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Reflection / 反思 x Chain / 链式 映射到该单元。
- 问题 / Problem: A single generator may produce plausible but unchecked output. / 单一生成器可能产生看似合理但未被检查的输出。
- 架构方案 / Architectural Solution: Use a generator to produce output and a separate critic step to evaluate, identify issues, and request repair when needed. / 使用生成器产出结果，再用独立批评步骤评估、识别问题并按需请求修复。
- 工程权衡 / Engineering Trade-offs: Improves quality and catches errors, but adds cost and can inherit critic blind spots. / 提升质量并捕获错误，但增加成本，也可能继承批评器盲点。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when output should pass through a sequential critique step. / 当产出需要经过顺序批评步骤时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Generator-Critic / 生成器-批评器.
- 诊断用途 / Diagnostic Use: Use when output should pass through a sequential critique step. / 当产出需要经过顺序批评步骤时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 验证测试、知识沉淀 / Verification, knowledge memory.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 评估结果按顺序进入下一步改进 / Evaluation results feed the next improvement step in order.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [reflection-chain-observability.md](reflection-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
