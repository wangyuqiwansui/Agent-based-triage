# Memory Cells Introduction / 记忆交织点导论

## Role / 定位

Use the memory row when workflow quality depends on retrieving, grounding, updating, or reusing previous context. / 当工作流质量依赖检索、扎根、更新或复用既有上下文时，使用记忆行。

Information storage and retrieval: maintain persistent knowledge, context retention, and organized recall across work sessions. / 信息存储与检索：跨工作会话维护持久知识、上下文保留和有组织的回忆。

## 论文对齐 / Article Alignment

- Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850).
- Cognitive function / 认知功能: Memory / 记忆.
- Article framing / 论文框架: The article treats this row as one cognitive function in a 7 x 6 matrix, crossed with six execution topologies. / 论文将本行作为 7 x 6 矩阵中的一个认知功能，并与六种执行拓扑交叉。
- Boundary / 边界: Do not use memory for temporary sensing alone; memory implies persistence, retrieval, or feedback into later work. / 不要将纯临时感知归入记忆；记忆意味着持久化、检索或反馈到后续工作。

## When To Read / 何时读取

Read this introduction before choosing a specific memory intersection. / 在选择具体 memory 交织点前，先阅读本导论。

- Use / 使用: Use it when decisions vanish, failures repeat, context is reacquired manually, or knowledge must survive between attempts. / 当决策消失、失败重复、上下文反复手工采集或知识必须跨尝试保留时使用。
- Do not use it as the source of detailed pattern fields; open the linked pattern file for the chosen intersection. / 不要将本页作为详细模式字段来源；选择交织点后打开对应模式文件。

## 矩阵摘要 / Matrix Summary

This row currently has 4 named pattern candidates and 2 extension candidates. / 本行当前包含 4 个已命名候选模式和 2 个扩展候选。

| Mode / 模式 | Status / 状态 | Pattern Cell / 模式单元 |
| --- | --- | --- |
| Chain / 链式 | Named / 已命名 | [RAG Pipeline / RAG 管线](memory-chain.md) |
| Routing / 路由 | Named / 已命名 | [Hierarchical Retrieval / 层级检索](memory-routing.md) |
| Parallel / 并行 | Extension / 扩展 | [Extension Candidate / 扩展候选](memory-parallel.md) |
| Orchestration / 编排 | Named / 已命名 | [Progress Tracking / 进度追踪](memory-orchestration.md) |
| Loop / 循环 | Named / 已命名 | [Failure Journal / 失败日志](memory-loop.md) |
| Hierarchy / 层级 | Extension / 扩展 | [Extension Candidate / 扩展候选](memory-hierarchy.md) |

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
| Chain / 链式 | [RAG Pipeline / RAG 管线](memory-chain.md) |
| Routing / 路由 | [Hierarchical Retrieval / 层级检索](memory-routing.md) |
| Parallel / 并行 | [Extension Candidate / 扩展候选](memory-parallel.md) |
| Orchestration / 编排 | [Progress Tracking / 进度追踪](memory-orchestration.md) |
| Loop / 循环 | [Failure Journal / 失败日志](memory-loop.md) |
| Hierarchy / 层级 | [Extension Candidate / 扩展候选](memory-hierarchy.md) |

## Extension Note / 扩展说明

Extend this row only when a workflow needs a new persistence, recall, forgetting, or knowledge-refresh behavior. / 仅当工作流需要新的持久化、回忆、遗忘或知识刷新行为时扩展本行。
