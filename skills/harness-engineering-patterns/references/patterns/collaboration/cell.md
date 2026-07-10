# Collaboration Cells Introduction / 协作交织点导论

## Role / 定位

Use the collaboration row when workflow quality depends on how multiple humans, agents, roles, or reviewers coordinate. / 当工作流质量依赖多人、Agent、角色或评审者如何协调时，使用协作行。

Multi-agent coordination and communication: distribute tasks, exchange context, resolve disagreement, and synthesize work. / 多 Agent 协调与沟通：分配任务、交换上下文、解决分歧并综合工作。

## 论文对齐 / Article Alignment

- Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850).
- Cognitive function / 认知功能: Collaboration / 协作.
- Article framing / 论文框架: The article treats this row as one cognitive function in a 7 x 6 matrix, crossed with six execution topologies. / 论文将本行作为 7 x 6 矩阵中的一个认知功能，并与六种执行拓扑交叉。
- Boundary / 边界: Simple messaging is not enough; collaboration requires interdependent actors or shared decisions. / 简单消息传递不足以构成协作；协作需要参与者依赖或共同决策。

## When To Read / 何时读取

Read this introduction before choosing a specific collaboration intersection. / 在选择具体 collaboration 交织点前，先阅读本导论。

- Use / 使用: Use it when handoffs stall, contributors duplicate work, independent work must be merged, or conflict needs structured resolution. / 当交接卡住、贡献者重复劳动、独立工作需要合并或冲突需要结构化解决时使用。
- Do not use it as the source of detailed pattern fields; open the linked pattern file for the chosen intersection. / 不要将本页作为详细模式字段来源；选择交织点后打开对应模式文件。

## 矩阵摘要 / Matrix Summary

This row currently has 4 named pattern candidates and 2 extension candidates. / 本行当前包含 4 个已命名候选模式和 2 个扩展候选。

| Mode / 模式 | Status / 状态 | Pattern Cell / 模式单元 |
| --- | --- | --- |
| Chain / 链式 | Named / 已命名 | [Handoff Chain / 交接链](collaboration-chain.md) |
| Routing / 路由 | Extension / 扩展 | [Extension Candidate / 扩展候选](collaboration-routing.md) |
| Parallel / 并行 | Named / 已命名 | [Fan-Out/Gather / 扇出汇聚](collaboration-parallel.md) |
| Orchestration / 编排 | Extension / 扩展 | [Extension Candidate / 扩展候选](collaboration-orchestration.md) |
| Loop / 循环 | Named / 已命名 | [Adversarial Review / 对抗评审](collaboration-loop.md) |
| Hierarchy / 层级 | Named / 已命名 | [Hierarchical Delegation / 层级委派](collaboration-hierarchy.md) |

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
| Chain / 链式 | [Handoff Chain / 交接链](collaboration-chain.md) |
| Routing / 路由 | [Extension Candidate / 扩展候选](collaboration-routing.md) |
| Parallel / 并行 | [Fan-Out/Gather / 扇出汇聚](collaboration-parallel.md) |
| Orchestration / 编排 | [Extension Candidate / 扩展候选](collaboration-orchestration.md) |
| Loop / 循环 | [Adversarial Review / 对抗评审](collaboration-loop.md) |
| Hierarchy / 层级 | [Hierarchical Delegation / 层级委派](collaboration-hierarchy.md) |

## Extension Note / 扩展说明

Extend this row only when a workflow needs a new coordination, delegation, negotiation, or synthesis behavior. / 仅当工作流需要新的协调、委派、协商或综合行为时扩展本行。
