# Engineering Analysis Compiler / 工程分析编译器

Use this file to run the end-to-end compiler flow for workflows, engineering nodes, Agent Harness source, or mixed inputs. / 使用本文档对工作流程、工程节点、Agent Harness 源码或混合输入执行端到端编译流程。

## Purpose / 目的

Compile ambiguous process or source material into engineering assets that can be compared, verified, reused, and governed. / 将模糊流程或源码材料编译为可比较、可验证、可复用、可治理的工程资产。

Core path / 核心路径:

```text
Workflow / Harness Source / 工作流程 / Harness 源码
  -> Engineering Intermediate Representation / 工程中间表示
  -> Cognition x Topology Matrix / 认知 x 拓扑矩阵
  -> Engineering Pattern Cards / 工程模式卡
  -> Executable or Reusable Skills / 可执行或可复用技能
  -> Evidence + Evaluation + Governance / 证据 + 评估 + 治理
```

## Registry As Source Data / 注册表作为源数据

Do not force every fact into the 7 x 6 matrix. Treat these registries as source data and the matrix as a view. / 不要把所有事实硬塞进 7 x 6 矩阵。将以下注册表视为源数据，将矩阵视为视图。

- Cognition registry / 认知注册表
- Topology registry / 拓扑注册表
- Engineering pattern registry / 工程模式注册表
- Business node registry / 业务节点注册表
- Source component registry / 源码组件注册表
- Skill registry / Skill 注册表
- Evidence registry / 证据注册表
- Evaluation registry / 评估注册表
- Governance registry / 治理注册表

Keep IDs stable once introduced, even when definitions evolve. / 一旦引入 ID，即使定义演进也要保持稳定。

Examples / 示例: `COG_PERCEPTION`, `TOP_ROUTING`, `PATTERN_0005`, `SKILL_ANALYSIS_0003`, `NODE_0001`, `SRC_0001`, `EVIDENCE_0001`.

## Input Types / 输入类型

| Input Type / 输入类型 | Use When / 使用场景 | Primary Output / 主要输出 |
| --- | --- | --- |
| workflow / 工作流程 | SOP, PRD, delivery flow, operations flow, support flow, review flow. / SOP、PRD、交付流程、运维流程、支持流程、评审流程。 | Business node map / 业务节点图 |
| harness_source / Harness 源码 | Repository, README, tests, config, CLI, service, runtime, tool, permission, sandbox, memory, or subagent code. / 仓库、README、测试、配置、CLI、服务、runtime、工具、权限、沙箱、记忆或子 Agent 代码。 | Harness source engineering map / Harness 源码工程地图 |
| mixed / 混合输入 | A workflow plus source, traces, logs, diffs, or runtime records. / 工作流程加源码、Trace、日志、diff 或运行记录。 | EIR with node and component evidence / 带节点和组件证据的 EIR |

## Compilation Pipeline / 编译流程

1. Prepare the analysis task. / 准备分析任务。
2. Ingest input materials. / 读取输入材料。
3. Build an EIR draft using `eir-schema.md`. / 使用 `eir-schema.md` 建立 EIR 草稿。
4. Detect the main workflow or main loop. / 定位主流程或主循环。
5. Classify cognition. / 标注认知能力。
6. Classify topology. / 标注拓扑形态。
7. Filter noise and keep control-plane evidence. / 过滤噪声并保留控制面证据。
8. Map nodes and components to the cognition x topology matrix. / 将节点和组件映射到认知 x 拓扑矩阵。
9. Extract engineering patterns. / 抽取工程模式。
10. Recommend or package Skills when patterns are reusable. / 当模式可复用时建议或封装 Skill。
11. Verify claims with evidence. / 用证据验证判断。
12. Evaluate quality and governance. / 评估质量与治理。
13. Render a report, plan, or file changes. / 输出报告、规划或文件修改。

## Control Plane First / 先抓控制面

In the first pass, prioritize files or steps that change what the Agent can see, remember, decide, do, retry, audit, or govern. / 第一轮优先分析会改变 Agent 可见内容、记忆内容、决策、行动、重试、审计或治理的文件与步骤。

Ask these questions before reading details. / 先问以下问题，再读细节。

- How does context enter? / 上下文如何进入？
- How does state change? / 状态如何变化？
- How are tools executed? / 工具如何执行？
- How are permissions constrained? / 权限如何约束？
- How do results return to the next turn? / 结果如何回填到下一轮？
- How are failures retried or repaired? / 失败如何重试或修复？
- How is the process audited? / 过程如何审计？
- How are lessons retained? / 经验如何沉淀？

## Evidence Rule / 证据规则

Every architecture judgment must cite at least one evidence item. Prefer source code, tests, official documentation, config, logs, traces, runtime records, or protocol evidence. / 每个架构判断至少引用一个证据项。优先使用源码、测试、官方文档、配置、日志、Trace、运行记录或协议证据。

If evidence is missing, mark the claim as unsupported and convert it into an observation or verification task. / 如果证据缺失，将判断标记为 unsupported，并转为观察或验证任务。

## Reference Routing / 参考路由

- Use `workflow-nodes.md` for business node splitting. / 使用 `workflow-nodes.md` 拆分业务节点。
- Use `harness-source-analysis.md` for source repository reverse engineering. / 使用 `harness-source-analysis.md` 进行源码仓库逆向分析。
- Use `axes.md`, `matrix-index.md`, and `pattern-selection-card.md` for matrix mapping. / 使用 `axes.md`、`matrix-index.md` 和 `pattern-selection-card.md` 做矩阵映射。
- Use `pattern-skill-packaging.md` for pattern cards and Skill specs. / 使用 `pattern-skill-packaging.md` 生成模式卡与 Skill 规格。
- Use `evaluation-governance.md` and `failure-modes.md` for quality, risk, and governance. / 使用 `evaluation-governance.md` 和 `failure-modes.md` 做质量、风险与治理分析。

## Minimum Output / 最小输出

Return enough structure to answer: where the main flow is, which nodes or components control each cognition, which topology each one uses, which evidence supports each claim, which patterns are reusable, which Skills are worth packaging, which failures matter, and which governance gaps remain. / 输出必须足以回答：主流程在哪里、哪些节点或组件控制各类认知、各自使用什么拓扑、每个判断由什么证据支持、哪些模式可复用、哪些 Skill 值得封装、哪些失败最重要、还有哪些治理缺口。
