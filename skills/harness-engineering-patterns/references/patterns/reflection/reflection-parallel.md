# Extension Candidate / 扩展候选

Cell / 交织点: reflection-parallel / 反思 x 并行
Capability / 能力: Reflection / 反思
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

Runtime Contract / 运行时契约: extension work in this cell must still use [Governed Reflection Execution Flow / 受治理反思执行流程](../../reflection-execution-flow.md); parallel candidates do not weaken shared admission, authorization, comparison, regression, or stopping gates. / 本单元的扩展工作仍必须使用共享反思执行流程；并行候选不得削弱共享的准入、授权、比较、回归或停止闸门。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reflection / 反思 x Parallel / 并行 (Parallel / 并行).
- 论文依据 / Article Basis: 空白单元 / Empty cell; arXiv:2605.13850 leaves this intersection unnamed but hypothesizes a future pattern: Parallel Reflection / 并行反思 — multiple critics evaluate the same output simultaneously along different dimensions, then merge findings. Treat this as a literature hypothesis, not a named pattern; naming still requires repeated workflow evidence. / 空白单元 / Empty cell；arXiv:2605.13850 未命名该交织点，但给出未来模式假设：Parallel Reflection / 并行反思——多个批评器沿不同维度同时评估同一产出，再合并发现。此为文献假设而非命名模式；命名仍需反复的工作流证据。
- 问题 / Problem: The article leaves this intersection unnamed; use it only if workflow evidence shows that Reflection / 反思 needs Parallel / 并行. / 论文未命名该交织点；仅当工作流证据表明 Reflection / 反思 需要 Parallel / 并行 时使用。
- 架构方案 / Architectural Solution: Keep this as an extension candidate and define a concrete pattern only after repeated workflow evidence appears. / 将其保留为扩展候选，仅在反复出现工作流证据后再定义具体模式。
- 工程权衡 / Engineering Trade-offs: This avoids inventing taxonomy, but leaves a deliberate gap until practice justifies the pattern. / 这避免凭空发明分类，但在实践证明前会保留有意空白。
- 工作流诊断用途 / Workflow Diagnosis Use: Extension candidate / 扩展候选.

### Pattern Template / 模式模板

- 状态 / Status: 扩展候选 / Extension candidate.
- 模式清单 / Patterns: 待发现 / To be discovered.
- 诊断用途 / Diagnostic Use: Extension candidate / 扩展候选.
- 适用工作流节点 / Applicable Workflow Nodes: 验证测试、方案设计 / Verification, design.
- 当前症状 / Current Symptoms: 待根据当前工作流诊断 / Diagnose from the current workflow.
- 适配信号 / Fit Signals: 多个评估维度可独立检查后汇总 / Multiple evaluation dimensions can be checked independently and merged.
- 调整方向 / Adjustment Direction: 待根据当前工作流补充 / Add based on the current workflow.
- 修改方式 / How To Modify: 待根据当前工作流补充 / Add based on the current workflow.
- 输入 / Inputs: 待根据当前工作流补充 / Add based on the current workflow.
- 输出 / Outputs: 待根据当前工作流补充 / Add based on the current workflow.
- 风险与治理 / Risks & Governance: 待根据当前工作流补充 / Add based on the current workflow.

Observability Metrics File / 可观测性指标文件: [reflection-parallel-observability.md](reflection-parallel-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
