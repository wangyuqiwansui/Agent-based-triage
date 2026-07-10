# Reasoning Cells Introduction / 推理交织点导论

## Role / 定位

Use the reasoning row when workflow quality depends on choosing, decomposing, testing hypotheses, or explaining a decision path. / 当工作流质量依赖选择、拆解、测试假设或解释决策路径时，使用推理行。

Cognitive processing and decision-making: perform inference, planning, comparison, decomposition, and problem solving. / 认知处理与决策：执行推断、规划、比较、拆解和问题求解。

## 论文对齐 / Article Alignment

- Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850).
- Cognitive function / 认知功能: Reasoning / 推理.
- Article framing / 论文框架: The article treats this row as one cognitive function in a 7 x 6 matrix, crossed with six execution topologies. / 论文将本行作为 7 x 6 矩阵中的一个认知功能，并与六种执行拓扑交叉。
- Boundary / 边界: Do not confuse reasoning with action; reasoning decides and structures, action changes state. / 不要混淆推理与行动；推理负责决定和组织，行动负责改变状态。

## When To Read / 何时读取

Read this introduction before choosing a specific reasoning intersection. / 在选择具体 reasoning 交织点前，先阅读本导论。

- Use / 使用: Use it when execution starts too early, alternatives are missing, hypotheses are not tested, or complexity is routed poorly. / 当过早执行、缺少备选方案、假设未被测试或复杂度路由不佳时使用。
- Do not use it as the source of detailed pattern fields; open the linked pattern file for the chosen intersection. / 不要将本页作为详细模式字段来源；选择交织点后打开对应模式文件。

## 矩阵摘要 / Matrix Summary

This row currently has 4 named pattern candidates and 2 extension candidates. / 本行当前包含 4 个已命名候选模式和 2 个扩展候选。

| Mode / 模式 | Status / 状态 | Pattern Cell / 模式单元 |
| --- | --- | --- |
| Chain / 链式 | Named / 已命名 | [Chain-of-Thought / 思维链](reasoning-chain.md) |
| Routing / 路由 | Named / 已命名 | [Complexity-Based Routing / 复杂度路由](reasoning-routing.md) |
| Parallel / 并行 | Named / 已命名 | [Parallel Exploration / 并行探索](reasoning-parallel.md) |
| Orchestration / 编排 | Extension / 扩展 | [Extension Candidate / 扩展候选](reasoning-orchestration.md) |
| Loop / 循环 | Named / 已命名 | [Iterative Hypothesis Testing / 迭代假设测试](reasoning-loop.md) |
| Hierarchy / 层级 | Extension / 扩展 | [Extension Candidate / 扩展候选](reasoning-hierarchy.md) |

## 选择法则 / Selection Laws

- Choose Chain when the work is a dependable sequence. / 当工作是可靠顺序流程时选择链式。
- Choose Routing when the first decision is classification or ownership. / 当第一步决策是分类或归属时选择路由。
- Choose Parallel when independent evidence or contributors can be gathered safely. / 当独立证据或贡献者可以安全汇聚时选择并行。
- Choose Orchestration when a controller must manage state, tools, dependencies, or handoffs. / 当控制器必须管理状态、工具、依赖或交接时选择编排。
- Choose Loop when feedback must change the next attempt. / 当反馈必须改变下一次尝试时选择循环。
- Choose Hierarchy when work must be delegated or constrained across levels. / 当工作必须跨层级委派或约束时选择层级。

## Trace / 追踪

After applying a design pattern, produce a project-local runtime Trace at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 应用设计模式后，依据 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地运行时 Trace。

## Navigation / 导航

| Mode / 模式 | Pattern Cell / 模式单元 |
| --- | --- |
| Chain / 链式 | [Chain-of-Thought / 思维链](reasoning-chain.md) |
| Routing / 路由 | [Complexity-Based Routing / 复杂度路由](reasoning-routing.md) |
| Parallel / 并行 | [Parallel Exploration / 并行探索](reasoning-parallel.md) |
| Orchestration / 编排 | [Extension Candidate / 扩展候选](reasoning-orchestration.md) |
| Loop / 循环 | [Iterative Hypothesis Testing / 迭代假设测试](reasoning-loop.md) |
| Hierarchy / 层级 | [Extension Candidate / 扩展候选](reasoning-hierarchy.md) |

## Extension Note / 扩展说明

Extend this row only when a workflow needs a distinct decision protocol or reasoning shape not captured by the current modes. / 仅当工作流需要当前模式无法表达的独立决策协议或推理形态时扩展本行。
