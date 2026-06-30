# Action Cells Introduction / 行动交织点导论

## Role / 定位

Use the action row when workflow quality depends on how planned work becomes concrete state change. / 当工作流质量依赖计划如何变成具体状态变化时，使用行动行。

Execution and interaction: perform operations, invoke tools, modify artifacts, and interact with environments. / 执行与交互：执行操作、调用工具、修改产物并与环境交互。

## 论文对齐 / Article Alignment

- Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850).
- Cognitive function / 认知功能: Action / 行动.
- Article framing / 论文框架: The article treats this row as one cognitive function in a 7 x 6 matrix, crossed with six execution topologies. / 论文将本行作为 7 x 6 矩阵中的一个认知功能，并与六种执行拓扑交叉。
- Boundary / 边界: Action should be paired with verification and governance whenever mistakes have cost or irreversible effects. / 当错误有成本或不可逆影响时，行动应与验证和治理配套。

## When To Read / 何时读取

Read this introduction before choosing a specific action intersection. / 在选择具体 action 交织点前，先阅读本导论。

- Use / 使用: Use it for code edits, tool calls, deployments, ticket updates, document changes, and operational commands. / 用于代码修改、工具调用、发布、工单更新、文档变更和运维命令。
- Do not use it as the source of detailed pattern fields; open the linked pattern file for the chosen intersection. / 不要将本页作为详细模式字段来源；选择交织点后打开对应模式文件。

## 矩阵摘要 / Matrix Summary

This row currently has 4 named pattern candidates and 2 extension candidates. / 本行当前包含 4 个已命名候选模式和 2 个扩展候选。

| Mode / 模式 | Status / 状态 | Pattern Cell / 模式单元 |
| --- | --- | --- |
| Chain / 链式 | Named / 已命名 | [Prompt Chaining / 提示链](action-chain.md) |
| Routing / 路由 | Named / 已命名 | [Tool Dispatch / 工具分派](action-routing.md) |
| Parallel / 并行 | Extension / 扩展 | [Extension Candidate / 扩展候选](action-parallel.md) |
| Orchestration / 编排 | Named / 已命名 | [Plan-and-Execute / 计划并执行](action-orchestration.md) |
| Loop / 循环 | Extension / 扩展 | [Extension Candidate / 扩展候选](action-loop.md) |
| Hierarchy / 层级 | Named / 已命名 | [Guardrail Sandwich / 护栏夹层](action-hierarchy.md) |

## 选择法则 / Selection Laws

- Choose Chain when the work is a dependable sequence. / 当工作是可靠顺序流程时选择链式。
- Choose Routing when the first decision is classification or ownership. / 当第一步决策是分类或归属时选择路由。
- Choose Parallel when independent evidence or contributors can be gathered safely. / 当独立证据或贡献者可以安全汇聚时选择并行。
- Choose Orchestration when a controller must manage state, tools, dependencies, or handoffs. / 当控制器必须管理状态、工具、依赖或交接时选择编排。
- Choose Loop when feedback must change the next attempt. / 当反馈必须改变下一次尝试时选择循环。
- Choose Hierarchy when work must be delegated or constrained across levels. / 当工作必须跨层级委派或约束时选择层级。

## Trace / 追踪

Record pattern usage outcomes in [trace.md](trace.md) after applying a design pattern. / 应用设计模式之后，在 [trace.md](trace.md) 中记录使用结果。

## Navigation / 导航

| Mode / 模式 | Pattern Cell / 模式单元 |
| --- | --- |
| Chain / 链式 | [Prompt Chaining / 提示链](action-chain.md) |
| Routing / 路由 | [Tool Dispatch / 工具分派](action-routing.md) |
| Parallel / 并行 | [Extension Candidate / 扩展候选](action-parallel.md) |
| Orchestration / 编排 | [Plan-and-Execute / 计划并执行](action-orchestration.md) |
| Loop / 循环 | [Extension Candidate / 扩展候选](action-loop.md) |
| Hierarchy / 层级 | [Guardrail Sandwich / 护栏夹层](action-hierarchy.md) |

## Extension Note / 扩展说明

Extend this row only when a workflow needs a distinct execution, rollback, or tool-use behavior. / 仅当工作流需要独立的执行、回滚或工具使用行为时扩展本行。
