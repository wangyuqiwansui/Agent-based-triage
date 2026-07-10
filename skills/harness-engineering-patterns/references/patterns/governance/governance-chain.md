# Extension Candidate / 扩展候选

Cell / 交织点: governance-chain / 治理 x 链式
Capability / 能力: Governance / 治理
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 空白单元 / Empty cell; arXiv:2605.13850 leaves this intersection unnamed. / 空白单元 / Empty cell；arXiv:2605.13850 未命名该交织点。
- 问题 / Problem: The article leaves this intersection unnamed; use it only if workflow evidence shows that Governance / 治理 needs Chain / 链式. / 论文未命名该交织点；仅当工作流证据表明 Governance / 治理 需要 Chain / 链式 时使用。
- 架构方案 / Architectural Solution: Keep this as an extension candidate and define a concrete pattern only after repeated workflow evidence appears. / 将其保留为扩展候选，仅在反复出现工作流证据后再定义具体模式。
- 工程权衡 / Engineering Trade-offs: This avoids inventing taxonomy, but leaves a deliberate gap until practice justifies the pattern. / 这避免凭空发明分类，但在实践证明前会保留有意空白。
- 工作流诊断用途 / Workflow Diagnosis Use: Extension candidate / 扩展候选.

### Pattern Template / 模式模板

- 状态 / Status: 扩展候选 / Extension candidate.
- 模式清单 / Patterns: 待发现 / To be discovered.
- 诊断用途 / Diagnostic Use: Extension candidate / 扩展候选.
- 适用工作流节点 / Applicable Workflow Nodes: 治理审查、发布交付 / Governance review, delivery.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 治理门禁必须按顺序通过 / Governance gates must pass in order.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [governance-chain-observability.md](governance-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
