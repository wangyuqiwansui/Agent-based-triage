---
name: harness-engineering-patterns
description: Use when Codex needs to analyze an engineering node or diagnose a current engineering workflow's business pattern, map workflow nodes to extensible capability and orchestration axes, identify pattern mismatches, or recommend concrete workflow adjustments. / 当需要分析工程节点、诊断当前工程工作流业务模式、映射可扩展纵横轴、识别模式错配或提出具体调整建议时使用。
---

# Harness Engineering Patterns / Harness 工程模式

## Overview / 概览

Use this skill to analyze how a current engineering workflow should change. The vertical capability axis, horizontal orchestration axis, and intersection matrix are all extensible diagnostic tools, not fixed taxonomies. / 使用本技能分析当前工程工作流应该如何调整。纵轴能力、横轴模式和交织表都是可扩展的诊断工具，不是固定分类表。

## Automatic Engineering Node Analysis / 工程节点自动分析

Whenever the task is to analyze an engineering node, automatically run Trace Insert / 自动运行 Trace 插入 first, then run Pattern Selection Card / 模式选型卡 after node evidence is ready. / 只要任务是分析工程节点，就先自动运行 Trace 插入；节点证据就绪后，再运行模式选型卡。

Do not answer with only a free-form judgment. Use the automatic flow to produce grounded node evidence, ASSESS, ROUTE, SELECT, and a modification plan. / 不要只输出自由判断；使用自动流程产出有依据的节点证据、评估、判拓扑、查矩阵和修改规划。

## Usage / 使用方式

1. Capture the current workflow from the user request, repository context, documents, delivery process, review process, automation flow, or operational flow. / 从用户请求、仓库上下文、文档、交付流程、评审流程、自动化流程或运维流程中采集当前工作流。
2. Read `references/workflow-nodes.md` to split the workflow into business nodes. / 读取 `references/workflow-nodes.md`，把工作流拆成业务节点。
3. Read `references/pattern-selection-card.md` for Trace Insert / Trace 插入, then gather complete node evidence before selecting patterns. / 读取 `references/pattern-selection-card.md` 中的 Trace Insert / Trace 插入，并在选型前采集完整节点证据。
4. If related trace files already contain usage evidence, read `references/patterns/<capability-key>/trace.md` before running the Pattern Selection Card / 模式选型卡. / 如果相关追踪文件已有使用证据，在运行 Pattern Selection Card / 模式选型卡 前读取 `references/patterns/<capability-key>/trace.md`。
5. Read `references/axes.md` and run ASSESS / 评估 to determine the node's needed capability. / 读取 `references/axes.md`，并执行 ASSESS / 评估 判断节点需要的能力。
6. Run ROUTE / 判拓扑 to choose the dominant orchestration mode using quick fit signals and risk override. / 执行 ROUTE / 判拓扑，使用快速适配信号和风险覆盖规则选择主导编排模式。
7. Run SELECT / 查矩阵 by reading `references/matrix-index.md`, the relevant vertical introduction at `references/patterns/<capability-key>/cell.md`, and the dedicated design pattern file at `references/patterns/<capability-key>/<cell-key>.md`. / 执行 SELECT / 查矩阵，读取 `references/matrix-index.md`、`references/patterns/<capability-key>/cell.md` 中对应纵轴导论，以及 `references/patterns/<capability-key>/<cell-key>.md` 中的独立设计模式文件。
8. For every selected pattern, also read its observability metrics file at `references/patterns/<capability-key>/<cell-key>-observability.md`. / 对每个已选模式，同时读取 `references/patterns/<capability-key>/<cell-key>-observability.md` 中的可观测性指标文件。
9. Read `references/pattern-catalog.md` when a matrix cell has named candidate patterns or when the user asks for concrete pattern options. / 当交织点已有命名候选模式，或用户要求具体模式选项时，读取 `references/pattern-catalog.md`。
10. Read `references/diagnosis-method.md` to identify mismatch, missing feedback, missing memory, over-linear flow, weak governance, unclear ownership, or poor handoff. / 读取 `references/diagnosis-method.md`，识别错配、反馈缺失、记忆缺失、过度链式、治理薄弱、归属不清或交接低效。
11. After recommending or applying a pattern, append or propose a trace entry in `references/patterns/<capability-key>/trace.md`. / 推荐或应用模式后，在 `references/patterns/<capability-key>/trace.md` 中追加或建议一条追踪记录。
12. Read `references/extension-rules.md` when the current axes or matrix cannot express the workflow accurately. / 当当前轴或交织表无法准确表达工作流时，读取 `references/extension-rules.md`。

## Output Contract / 输出约定

Always return a practical adjustment proposal, not only a classification. / 始终输出可执行的调整建议，而不只是分类结果。

Include these sections when diagnosing a workflow: / 诊断工作流时包含以下部分：

- Current workflow summary / 当前工作流摘要
- Business node breakdown / 业务节点拆解
- Trace Insert and node evidence / Trace 插入与节点证据
- Pattern Selection Card: ASSESS, ROUTE, SELECT / 模式选型卡：评估、判拓扑、查矩阵
- Axis and matrix mapping / 纵横轴与交织表映射
- Diagnosed problems / 诊断出的问题
- Recommended pattern adjustments / 推荐的模式调整
- Observability metrics for selected patterns / 已选模式的可观测性指标
- Concrete modification steps / 具体修改步骤
- Trace entry or logging recommendation / 追踪记录或日志建议
- Extension needs for axes or matrix / 纵轴、横轴或交织表扩展需求
- Risks, verification, and observation points / 风险、验证方式和观察点

## Constraints / 约束

- Keep all skill content bilingual in Chinese and English. / 所有技能内容保持中英双语。
- Treat the initial 7x6 matrix as a starting framework only. / 将初始 7x6 交织表视为起始框架。
- Prefer a controlled extension over forcing a workflow into an inaccurate existing axis. / 当现有轴无法准确表达工作流时，优先提出受控扩展，而不是强行归类。
- Do not fill every cell with invented patterns. Add concrete patterns only when the user supplies or requests a specific workflow case. / 不要凭空填满所有交织点；仅在用户提供或要求具体工作流案例时补充具体模式。
- Keep every matrix cell represented by two linked Markdown files: one design pattern file and one observability metrics file. / 每个交织点都由两个互相链接的 Markdown 文件表示：一个设计模式文件，一个可观测性指标文件。
- When adding a vertical or horizontal axis, update axes, grouped cell folders, trace files, matrix index, and affected pattern files together. / 新增纵轴或横轴时，同步更新轴定义、按 cell 分组的文件夹、追踪文件、矩阵索引和受影响的模式文件。
