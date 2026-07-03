# Pattern And Skill Packaging / 模式与 Skill 化

Use this file when turning matrix mappings into engineering pattern cards, Skill specifications, or Skillization / Skill 化 recommendations. / 当需要把矩阵映射转化为工程模式卡、Skill 规格或 Skill 化建议时使用本文档。

## Pattern Extraction / 模式抽取

An engineering pattern is a reusable solution for a stable engineering problem. / 工程模式是针对稳定工程问题的可复用解决方案。

A candidate pattern should describe / 候选模式应描述:

- Problem solved / 解决的问题
- Applicable context / 适用上下文
- Trigger conditions / 触发条件
- Inputs and outputs / 输入与输出
- Workflow structure / 工作流结构
- Tool and memory dependencies / 工具与记忆依赖
- Governance constraints / 治理约束
- Evaluation method / 评估方式
- Failure modes / 失败模式
- Source or workflow evidence / 源码或流程证据

Extract a pattern only when the structure repeats across tasks or workflows, solves a stable problem, has clear inputs and outputs, maps to cognition x topology coordinates, has evidence, has known failure modes, can be evaluated, and could become a Skill or tool. / 只有当某结构跨任务或流程重复出现、解决稳定问题、输入输出清楚、能映射到认知 x 拓扑坐标、有证据、有明确失败模式、可评估且可 Skill 化或工具化时，才抽取为模式。

## Pattern Card Contract / 模式卡契约

Use this compact shape unless the user requests a full separate card. / 除非用户要求完整单独模式卡，否则使用以下紧凑结构。

- Pattern ID and name / 模式 ID 与名称
- Cognition refs and topology refs / 认知引用与拓扑引用
- Matrix coordinates / 矩阵坐标
- Business node refs or source component refs / 业务节点引用或源码组件引用
- Problem and context / 问题与上下文
- Trigger, inputs, outputs / 触发、输入、输出
- Workflow structure / 工作流结构
- Tool dependencies and memory dependencies / 工具依赖与记忆依赖
- Governance requirements / 治理要求
- Evaluation method / 评估方式
- Failure modes and anti-patterns / 失败模式与反模式
- Evidence refs / 证据引用
- Related patterns / 关联模式

## Skillization / Skill 化

Skill is the executable packaging of an engineering pattern. / Skill 是工程模式的执行化包装。

A pattern is worth Skillization / Skill 化 when it is frequent, stable, clear in input and output, callable by an Agent, testable, bounded in risk, and able to produce reusable assets. / 当模式高频、流程稳定、输入输出明确、可被 Agent 调用、可测试、风险边界清楚且能产出可复用资产时，值得 Skill 化。

## Skill Spec Contract / Skill 规格契约

When recommending a Skill, include / 推荐 Skill 时包含:

- Skill goal / Skill 目标
- Use cases / 适用场景
- Non-use cases / 不适用场景
- Input requirements / 输入要求
- Context requirements / 上下文要求
- Execution workflow / 执行流程
- Tool invocation rules / 工具调用规则
- Output format / 输出格式
- Failure handling / 失败处理
- Governance requirements / 治理要求
- Evaluation cases / 评估用例

When creating or updating actual Skill files, keep key metadata and core sections bilingual and store newly created Skill files under `.\skills`. / 创建或更新实际 Skill 文件时，关键元信息和核心章节保持中英双语，新建 Skill 文件统一放在 `.\skills` 下。

## Initial Harness Pattern Seeds / 初始 Harness 模式种子

Use these seeds as candidates, not as forced labels. / 将这些种子作为候选模式，而不是强制标签。

| Pattern ID / 模式 ID | Name / 名称 | Primary Coordinate / 主坐标 | Problem / 解决的问题 |
| --- | --- | --- | --- |
| `PATTERN_0001` | Main Loop Progression / 主循环推进模式 | `COG_REASONING__TOP_LOOP` | Advance Agent work across turns until stop. / 让 Agent 多轮推进任务直到停止。 |
| `PATTERN_0002` | Context Assembly / 上下文装配模式 | `COG_PERCEPTION__TOP_CHAIN` | Control what the model sees each turn. / 控制模型每轮看到什么。 |
| `PATTERN_0003` | Repository Map Sensing / 仓库地图感知模式 | `COG_PERCEPTION__TOP_ROUTING` | Compress repo structure and route to relevant files. / 压缩仓库结构并路由到相关文件。 |
| `PATTERN_0004` | LSP Sensing / 语言服务器感知模式 | `COG_PERCEPTION__TOP_ROUTING` | Use symbols and language intelligence for code understanding. / 用符号和语言服务增强代码理解。 |
| `PATTERN_0005` | Memory Retrieval Routing / 记忆检索路由模式 | `COG_MEMORY__TOP_ROUTING` | Select history, preferences, or lessons by task. / 根据任务选择历史、偏好或经验。 |
| `PATTERN_0006` | Multi-Source Observation / 多源并行观察模式 | `COG_PERCEPTION__TOP_PARALLEL` | Gather multiple information sources and merge them. / 并行采集多源信息后聚合。 |
| `PATTERN_0007` | Routed Tool Dispatch / 路由式工具调度模式 | `COG_ACTION__TOP_ROUTING` | Route action intent to controlled tools. / 将行动意图路由到受控工具。 |
| `PATTERN_0008` | Permission Approval / 权限审批模式 | `COG_GOVERNANCE__TOP_ROUTING` | Send high-risk actions through confirmation or policy branches. / 将高风险动作送入确认或策略分支。 |
| `PATTERN_0009` | Sandbox Isolation / 沙箱隔离执行模式 | `COG_GOVERNANCE__TOP_ORCHESTRATION` | Limit file, command, network, or external writes inside boundaries. / 将文件、命令、网络或外部写入限制在边界内。 |
| `PATTERN_0010` | Event Ledger / 事件账本模式 | `COG_MEMORY__TOP_CHAIN` | Support replay, audit, and recovery through append-only events. / 用追加式事件支持回放、审计和恢复。 |
| `PATTERN_0011` | Failure Repair Loop / 失败修复循环模式 | `COG_REFLECTION__TOP_LOOP` | Repair repeatedly based on feedback. / 基于反馈反复修正。 |
| `PATTERN_0012` | Evaluation Gate / 评估闸门模式 | `COG_REFLECTION__TOP_ROUTING` | Decide continuation by tests, rules, or evaluation results. / 根据测试、规则或评估结果决定是否继续。 |
| `PATTERN_0013` | Subagent Delegation / 子 Agent 委派模式 | `COG_COLLABORATION__TOP_HIERARCHY` | Delegate bounded tasks from a lead Agent. / 主 Agent 将有边界任务委派出去。 |
| `PATTERN_0014` | Multi-Agent Fan-Out Gather / 多 Agent 并行聚合模式 | `COG_COLLABORATION__TOP_PARALLEL` | Run multiple Agents concurrently and synthesize. / 多个 Agent 同时执行再汇总。 |
| `PATTERN_0015` | Skill Loading Orchestration / 技能加载编排模式 | `COG_ACTION__TOP_ORCHESTRATION` | Load, order, and execute Skills by task. / 根据任务加载、排序和执行 Skill。 |
| `PATTERN_0016` | Procedural Memory Packaging / 程序性记忆沉淀模式 | `COG_MEMORY__TOP_HIERARCHY` | Turn lessons into callable skills or procedures. / 将经验沉淀成可调用技能或流程。 |
| `PATTERN_0017` | Multi-Channel Gateway / 多通道网关模式 | `COG_ACTION__TOP_ROUTING` | Bring different entrypoints into one control plane. / 将不同入口统一进入控制面。 |
| `PATTERN_0018` | Identity Permission Binding / 身份与权限绑定模式 | `COG_GOVERNANCE__TOP_HIERARCHY` | Bind user, device, channel, and scope. / 绑定用户、设备、channel 与权限范围。 |
| `PATTERN_0019` | Protocol Bridge / 协议桥接模式 | `COG_ACTION__TOP_ORCHESTRATION` | Connect CLI, IDE, web, and remote services through protocols. / 通过协议层连接 CLI、IDE、Web 和远程服务。 |
| `PATTERN_0020` | Trace Replay Debugging / Trace Replay 调试模式 | `COG_REFLECTION__TOP_CHAIN` | Replay historical events for debugging and review. / 重放历史事件用于调试与复盘。 |
| `PATTERN_0021` | Multi-Modal Fusion / 多模态融合模式 | `COG_PERCEPTION__TOP_PARALLEL` | Fuse text, image, log, and structured sources into one perception result. / 将文本、图像、日志和结构化来源融合为一个感知结果。 |
| `PATTERN_0022` | Layered Retention / 分层保留模式 | `COG_MEMORY__TOP_HIERARCHY` | Route memory writes and recalls through scoped retention layers. / 将记忆写入与召回路由到分域保留层。 |

Scope note / 范围说明: arXiv:2605.13850 deliberately excludes the outer reason-act main loop from its pattern catalog and treats it as runtime substrate. `PATTERN_0001` Main Loop Progression is kept here because Harness source analysis must still name the main loop as a component; treat it as a source-analysis anchor, not an article-matrix cell pattern. / arXiv:2605.13850 明确将外层"推理-行动"主循环排除在模式目录之外，视为运行时基座。这里保留 `PATTERN_0001` 主循环推进模式，是因为 Harness 源码分析仍需将主循环作为组件命名；应将其视为源码分析锚点，而不是论文矩阵单元模式。
