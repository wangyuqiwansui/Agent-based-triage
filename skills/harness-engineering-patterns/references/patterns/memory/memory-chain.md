# RAG Pipeline / RAG 管线

Cell / 交织点: memory-chain / 记忆 x 链式
Capability / 能力: Memory / 记忆
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Memory / 记忆 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Memory / 记忆 x Chain / 链式 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Memory / 记忆 x Chain / 链式 映射到该单元。
- 问题 / Problem: Model-internal knowledge is stale, incomplete, or unverifiable for the current task. / 模型内部知识对当前任务而言过期、不完整或无法验证。
- 架构方案 / Architectural Solution: Retrieve external sources, rank or filter them, ground the answer or plan in retrieved evidence, and pass the grounded context forward. / 检索外部来源，排序或过滤，再基于检索证据生成回答或计划并传递扎根上下文。
- 工程权衡 / Engineering Trade-offs: Improves freshness and provenance, but retrieval quality, latency, and source trust become part of system quality. / 提升新鲜度和来源可追溯性，但检索质量、延迟和来源可信度也成为系统质量的一部分。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when retrieval, grounding, and answer construction form a sequence. / 当检索、扎根和回答构成顺序管线时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: RAG Pipeline / RAG 管线.
- 诊断用途 / Diagnostic Use: Use when retrieval, grounding, and answer construction form a sequence. / 当检索、扎根和回答构成顺序管线时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 知识沉淀、上下文感知 / Knowledge memory, context sensing.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 上一步知识沉淀直接服务下一步执行或判断 / Prior captured knowledge directly feeds the next step.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [memory-chain-observability.md](memory-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
