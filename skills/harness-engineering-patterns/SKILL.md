---
name: harness-engineering-patterns
description: Use when Codex needs to compile a workflow, engineering node, or Agent Harness source into an Engineering Intermediate Representation (EIR), cognition x topology matrix, pattern cards, skillization recommendations, evidence table, governance gaps, or concrete pattern adjustments. / 当需要将工作流程、工程节点或 Agent Harness 源码编译为工程中间表示（EIR）、认知 x 拓扑矩阵、模式卡、Skill 化建议、证据表、治理缺口或具体模式调整时使用。
---

# Harness Engineering Patterns / Harness 工程模式

## Overview / 概览

Use this skill to compile a workflow or Agent Harness source into a reusable engineering map. The path is: Workflow / Harness Source / 工作流程 / Harness 源码 -> Engineering Intermediate Representation / 工程中间表示 -> cognition x topology matrix / 认知 x 拓扑矩阵 -> pattern cards / 模式卡 -> reusable Skills / 可复用技能 -> Evidence + Evaluation + Governance / 证据 + 评估 + 治理. / 使用本技能将工作流程或 Agent Harness 源码编译为可复用工程地图。路径是：工作流程 / Harness 源码 -> 工程中间表示 -> 认知 x 拓扑矩阵 -> 模式卡 -> 可复用技能 -> 证据 + 评估 + 治理。

The vertical capability axis, horizontal topology axis, and intersection matrix are extensible diagnostic views, not fixed taxonomies. Registries are the source data; the matrix is a view over them. / 纵轴能力、横轴拓扑和交织表是可扩展诊断视图，不是固定分类表。注册表是源数据，矩阵是视图。

## Compiler Spine / 编译主线

Start by selecting the input type, then keep an EIR and evidence trail through the whole analysis. / 先选择输入类型，再在整个分析过程中维护 EIR 和证据链。

1. Read `references/compiler-workflow.md` for the overall compiler workflow, stable-ID rules, and control-plane-first principle. / 读取 `references/compiler-workflow.md`，理解总体编译流程、稳定 ID 规则和先抓控制面的原则。
2. Classify the input as workflow, harness_source, or mixed. / 将输入分类为 workflow、harness_source 或 mixed。
3. Read `references/eir-schema.md` and maintain an Engineering Intermediate Representation / 工程中间表示 for nodes, source components, mappings, evidence, evaluation, and governance. / 读取 `references/eir-schema.md`，为节点、源码组件、映射、证据、评估和治理维护工程中间表示。
4. For workflow or engineering-node diagnosis, follow the automatic Trace Insert / Trace 插入 and Pattern Selection Card / 模式选型卡 flow below. / 对工作流或工程节点诊断，执行下方自动 Trace 插入与模式选型卡流程。
5. For Agent Harness source analysis, read `references/harness-source-analysis.md` and run Detect / Classify / Filter / Map / Verify. / 对 Agent Harness 源码分析，读取 `references/harness-source-analysis.md` 并执行找主循环、组件归类、噪声过滤、落矩阵和证据验证。
6. For pattern extraction or Skill recommendations, read `references/pattern-skill-packaging.md`. / 对模式抽取或 Skill 化建议，读取 `references/pattern-skill-packaging.md`。
7. For quality scoring, evidence checks, governance gaps, or risk controls, read `references/evaluation-governance.md` and `references/failure-modes.md`. / 对质量评分、证据检查、治理缺口或风险控制，读取 `references/evaluation-governance.md` 和 `references/failure-modes.md`。

## Automatic Engineering Node Analysis / 工程节点自动分析

Whenever the task is to analyze an engineering node, automatically run Trace Insert / 自动运行 Trace 插入 first, then run Pattern Selection Card / 模式选型卡 after node evidence is ready. / 只要任务是分析工程节点，就先自动运行 Trace 插入；节点证据就绪后，再运行模式选型卡。

Do not answer with only a free-form judgment. Use the automatic flow to produce grounded node evidence, ASSESS, ROUTE, SELECT, and a modification plan. / 不要只输出自由判断；使用自动流程产出有依据的节点证据、评估、判拓扑、查矩阵和修改规划。

## Usage / 使用方式

### Workflow And Node Diagnosis / 工作流与节点诊断

1. Capture the current workflow from the user request, repository context, documents, delivery process, review process, automation flow, or operational flow. / 从用户请求、仓库上下文、文档、交付流程、评审流程、自动化流程或运维流程中采集当前工作流。
2. Read `references/workflow-nodes.md` to split the workflow into business nodes. / 读取 `references/workflow-nodes.md`，把工作流拆成业务节点。
3. Read `references/pattern-selection-card.md` for Trace Insert / Trace 插入, then gather complete node evidence before selecting patterns. / 读取 `references/pattern-selection-card.md` 中的 Trace Insert / Trace 插入，并在选型前采集完整节点证据。
4. If related trace files already contain usage evidence, read `references/patterns/<capability-key>/trace.md` before running the Pattern Selection Card / 模式选型卡. / 如果相关追踪文件已有使用证据，在运行 Pattern Selection Card / 模式选型卡 前读取 `references/patterns/<capability-key>/trace.md`。
5. Read `references/axes.md` and run ASSESS / 评估 to determine the node's needed capability. / 读取 `references/axes.md`，并执行 ASSESS / 评估 判断节点需要的能力。
6. Run ROUTE / 判拓扑 to choose the dominant topology mode using quick fit signals and risk override. / 执行 ROUTE / 判拓扑，使用快速适配信号和风险覆盖规则选择主导拓扑模式。
7. Run SELECT / 查矩阵 by reading `references/matrix-index.md`, the relevant vertical introduction at `references/patterns/<capability-key>/cell.md`, and the dedicated design pattern file at `references/patterns/<capability-key>/<cell-key>.md`. / 执行 SELECT / 查矩阵，读取 `references/matrix-index.md`、`references/patterns/<capability-key>/cell.md` 中对应纵轴导论，以及 `references/patterns/<capability-key>/<cell-key>.md` 中的独立设计模式文件。
8. For every selected pattern, also read its observability metrics file at `references/patterns/<capability-key>/<cell-key>-observability.md`. / 对每个已选模式，同时读取 `references/patterns/<capability-key>/<cell-key>-observability.md` 中的可观测性指标文件。
9. Read `references/pattern-catalog.md` when a matrix cell has named candidate patterns or when the user asks for concrete pattern options. / 当交织点已有命名候选模式，或用户要求具体模式选项时，读取 `references/pattern-catalog.md`。
10. Read `references/diagnosis-method.md` to identify mismatch, missing feedback, missing memory, over-linear flow, weak governance, unclear ownership, or poor handoff. / 读取 `references/diagnosis-method.md`，识别错配、反馈缺失、记忆缺失、过度链式、治理薄弱、归属不清或交接低效。
11. After recommending or applying a pattern, append or propose a trace entry in `references/patterns/<capability-key>/trace.md`. / 推荐或应用模式后，在 `references/patterns/<capability-key>/trace.md` 中追加或建议一条追踪记录。

### Harness Source Compilation / Harness 源码编译

1. Read `references/harness-source-analysis.md` before analyzing source files. / 分析源码文件前读取 `references/harness-source-analysis.md`。
2. Detect the main loop and control plane before inspecting peripheral implementation details. / 先定位主循环和控制面，再检查边缘实现细节。
3. Classify core source components into perception, memory, reasoning, action, reflection, collaboration, and governance. / 将核心源码组件归类到感知、记忆、推理、行动、反思、协作和治理。
4. Filter noise aggressively: first-round reading should prioritize files that change context, state, tools, permissions, execution, retry, audit, or handoff. / 主动过滤噪声：第一轮优先读取会改变上下文、状态、工具、权限、执行、重试、审计或交接的文件。
5. Map each retained component to cognition x topology coordinates and attach evidence before extracting patterns. / 将每个保留组件映射到认知 x 拓扑坐标，并在抽取模式前挂载证据。

### Extension And Packaging / 扩展与封装

1. Read `references/extension-rules.md` when the current axes or matrix cannot express the workflow accurately. / 当当前轴或交织表无法准确表达工作流时，读取 `references/extension-rules.md`。
2. Read `references/pattern-skill-packaging.md` before producing pattern cards, Skill specs, or Skillization / Skill 化 recommendations. / 生成模式卡、Skill 规格或 Skill 化建议前读取 `references/pattern-skill-packaging.md`。
3. Read `references/evaluation-governance.md` before finalizing evidence, evaluation, governance, and verification sections. / 最终确定证据、评估、治理和验证章节前读取 `references/evaluation-governance.md`。
4. Read `references/failure-modes.md` when naming risks, failure modes, mitigations, or observability probes. / 命名风险、失败模式、缓解方式或可观测性探针时读取 `references/failure-modes.md`。

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

Include these sections when compiling Harness source: / 编译 Harness 源码时包含以下部分：

- Analysis scope and input references / 分析范围与输入引用
- Main loop map / 主循环图
- Source component classification / 源码组件归类
- Noise filter table / 噪声过滤表
- Cognition x topology matrix mapping / 认知 x 拓扑矩阵映射
- Pattern candidates and Skillization recommendations / 模式候选与 Skill 化建议
- Evidence verification table / 证据验证表
- Failure modes and mitigations / 失败模式与缓解方式
- Governance gaps / 治理缺口
- Evaluation scores or readiness notes / 评估分数或就绪说明

## Constraints / 约束

- Keep all skill content bilingual in Chinese and English. / 所有技能内容保持中英双语。
- Keep new Skill files under `.\skills`. / 新建 Skill 文件统一放在 `.\skills` 下。
- Treat registries as source data and the matrix as a generated or maintained view. / 将注册表视为源数据，将矩阵视为生成或维护的视图。
- Keep IDs stable after introduction: COG_*, TOP_*, PATTERN_*, SKILL_*, NODE_*, SRC_*, EVIDENCE_*. / 引入后保持 ID 稳定：COG_*、TOP_*、PATTERN_*、SKILL_*、NODE_*、SRC_*、EVIDENCE_*。
- Capture the control plane before implementation details. / 先捕捉控制面，再分析实现细节。
- Every architecture judgment must cite source, test, official documentation, config, log, trace, runtime record, or protocol evidence. / 每个架构判断必须引用源码、测试、官方文档、配置、日志、Trace、运行记录或协议证据。
- Treat README evidence as supporting evidence, not the strongest proof. / 将 README 证据视为辅助证据，而不是最强证明。
- Treat the initial 7x6 matrix as a starting framework only. / 将初始 7x6 交织表视为起始框架。
- Prefer a controlled extension over forcing a workflow into an inaccurate existing axis. / 当现有轴无法准确表达工作流时，优先提出受控扩展，而不是强行归类。
- Do not fill every cell with invented patterns. Add concrete patterns only when the user supplies or requests a specific workflow case. / 不要凭空填满所有交织点；仅在用户提供或要求具体工作流案例时补充具体模式。
- Keep every matrix cell represented by two linked Markdown files: one design pattern file and one observability metrics file. / 每个交织点都由两个互相链接的 Markdown 文件表示：一个设计模式文件，一个可观测性指标文件。
- When adding a vertical or horizontal axis, update axes, grouped cell folders, trace files, matrix index, and affected pattern files together. / 新增纵轴或横轴时，同步更新轴定义、按 cell 分组的文件夹、追踪文件、矩阵索引和受影响的模式文件。
