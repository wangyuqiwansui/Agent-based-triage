# Collaboration Cells Introduction / 协作交织点导论

## Role / 定位

Use the collaboration row when workflow quality depends on how multiple humans, agents, roles, or reviewers coordinate. / 当工作流质量依赖多人、Agent、角色或评审者如何协调时，使用协作行。

Multi-agent coordination and communication: distribute tasks, exchange context, resolve disagreement, and synthesize work. / 多 Agent 协调与沟通：分配任务、交换上下文、解决分歧并综合工作。

This is the governing introduction and entry to four composable modes, not a mandatory multi-agent sequence. Intent follows messages, truth follows references, results follow artifacts, and responsibility follows acceptance. / 本页是协作总纲与四种可组合模式入口，不是固定的多 Agent 顺序流程。意图随消息、真值随引用、结果随工件、责任随验收。

## Shared Procedures / 共享规程

For handoff chains, the [dedicated execution flow](collaboration-chain.md), [independent probes](collaboration-chain-observability.md) and [protocol 1.0 contract](../../handoff-chain-contract.md) extend `PATTERN_0043` with immutable versions, receiver acceptance, atomic commitment and responsibility transfer, bounded recovery and observation-only patches. HCM01–HCM30 retain the 30 supplied metric definitions; they remain specifications and are not aliases for shared CSM calculations. Host storage and external adapters must still implement and verify these guarantees. / 交接链的专用执行、独立探针与协议 `1.0` 契约为 `PATTERN_0043` 补充不可变版本、接收验收、原子提交与责任转移、有界恢复及纯观测补丁。HCM01–HCM30 保留所供 30 项指标定义，仍为规格，不作为共享 CSM 计算的别名；宿主存储与外部适配器仍须实现并验证这些保证。

For fan-out/gather, the [dedicated execution flow](collaboration-parallel.md) and [independent probes](collaboration-parallel-observability.md) extend `PATTERN_0044` with frozen shard obligations, typed evidence cards, five aggregation checks and a version-bound supplement contract. GM01–GM17 preserve the supplied source definitions; they are not aliases for shared CSM metrics and remain specification-only. / 扇出聚合的专用执行与独立探针将冻结分片义务、类型化证据卡、五步聚合及版本绑定补数契约接入 `PATTERN_0044`；GM01–GM17 保留所供原文定义，不是共享 CSM 的别名，仍仅为规格。

For hierarchical delegation, the [dedicated execution flow](collaboration-hierarchy.md) and [dedicated probes](collaboration-hierarchy-observability.md) extend `PATTERN_0046` with a responsibility baseline, two acceptance gates, local recovery and 22 source-defined metrics. This `0.1.0` specification is separate from the shared module profile below; dedicated runtime behavior remains to be implemented by the host. / 层级委派的专用执行与探针将责任基线、两道验收闸、局部恢复及 22 项来源指标接入 `PATTERN_0046`。该 `0.1.0` 规格与下方共享模块配置分开；专用运行行为仍需宿主实现。

Read [Collaboration Boundaries and Whole Delivery / 协作边界与整体交付](../../collaboration-execution-flow.md) for 13 logical nodes and mode composition. Read [Independent Workflow Probes / 独立工作流探针](../../collaboration-observability-probes.md) for 11 probe nodes and 34 selectively enabled metrics. Both embed the same local 3.0.0 executable profile projected from the supplied source contract 2.0.0. Original nodes, formulas and cases are traceable through the full-text source map. / 执行规程包含 13 个逻辑节点与模式组合，独立探针包含 11 个节点和 34 项按需指标；两份文件内置由来源契约 2.0.0 投影而来的相同本地 3.0.0 执行配置；原节点、算式和用例均可追溯全文映射。

The supplied introduction summary is the source for this extension; detailed fields and guards are local engineering additions. Start by checking expected benefit separately from task decomposability, manageable state and verifiable results. The probe can inspect an adapted external workflow without starting this execution flow. Business-incomplete gaps return to execution, while evidence gaps may yield candidates for a fresh business recheck. / 本扩展依据所提供导论摘要，详细字段和闸门属于本地工程新增。先分别检查预期收益与任务可拆、状态可管、结果可验。探针可直接检查适配的外部工作流，无需启动配套执行；业务缺口回执行侧，证据缺口可返回候选并重新业务验收。

Keep the four existing named patterns and two extension candidates unchanged. The registered module is a draft foundation extension; reference tests do not promote a pattern to validated maturity or prove live collaboration gains. / 保留四个既有命名模式与两个扩展候选。本模块属于草案基座扩展；参考测试不能将模式晋升为已验证成熟度，也不能证明真实协作收益。

## Dedicated Adversarial Review / 专用对抗评审

For `collaboration-loop`, use [execution](collaboration-loop.md) and [independent probes](collaboration-loop-observability.md). Required risk coverage, objection disposition, current-baseline receipts and actual external effects are separate facts. The [dedicated 0.1.0 contract](../../adversarial-review-contract.md) and RM01–RM27 remain specification-only, distinct from shared CE09/profile 3.0.0 and CSM25–CSM26; quiet rounds or completed document tests do not prove safe release. / 对抗评审读取专用执行与独立探针；风险覆盖、异议处置、当前基线回执及真实外部效果分开记录。专用契约及 RM 指标仅为规格，与通用节点、执行配置和指标分开；无新发现或文档测试完成不证明发布安全。

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
