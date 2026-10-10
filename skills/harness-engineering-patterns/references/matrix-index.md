# Matrix Index / 交织表总览

Use this index to locate the diagnostic cell for a capability and orchestration mode. The initial matrix is 7x6, but rows and columns are extensible. Pattern names are adapted from arXiv:2605.13850. / 使用本索引定位能力与编排模式对应的诊断单元。初始矩阵为 7x6，但行和列都可扩展。模式名称参考 arXiv:2605.13850 并调整为诊断用途。

Provenance summary / 来源摘要: 28 upstream named patterns / 上游 28 个命名模式, 14 upstream blank cells / 上游 14 个空白单元, two local promotions / 2 个本地晋升模式 (`Progressive Discovery`, `Layered Retention`), and 12 remaining extension candidates / 剩余 12 个扩展候选。 Use `registry.json` for authoritative IDs, source names, local aliases, status, and maturity. / 权威 ID、来源名称、本地别名、状态和成熟度以 `registry.json` 为准。

## Initial Matrix / 初始交织表

Start composition with the [selection card](pattern-selection-card.md) and [S0–S10 execution](pattern-selection-execution-flow.md), then use [selection probes](pattern-selection-observability-probes.md) to define evidence. Retain a sufficient baseline; select matrix cells only for demonstrated gaps. / 组合设计从选型卡与完整执行流程开始，以选型探针定义证据；基线足够则保留，仅为已证实缺口选择矩阵单元。

| Capability / 能力 | Chain / 链式 | Routing / 路由 | Parallel / 并行 | Orchestration / 编排 | Loop / 循环 | Hierarchy / 层级 |
| --- | --- | --- | --- | --- | --- | --- |
| Perception / 感知 | [Semantic Compaction / 语义压缩](patterns/perception/perception-chain.md) | [Context Triage / 上下文分诊](patterns/perception/perception-routing.md) | [Multi-Modal Fusion / 多模态融合](patterns/perception/perception-parallel.md) | [Progressive Disclosure / 渐进披露](patterns/perception/perception-orchestration.md) | [Progressive Discovery / 渐进式发现](patterns/perception/perception-loop.md) | [Extension Candidate / 扩展候选](patterns/perception/perception-hierarchy.md) |
| Memory / 记忆 | [RAG Pipeline / RAG 管线](patterns/memory/memory-chain.md) | [Hierarchical Retrieval / 层级检索](patterns/memory/memory-routing.md) | [Extension Candidate / 扩展候选](patterns/memory/memory-parallel.md) | [Progress Tracking / 进度追踪](patterns/memory/memory-orchestration.md) | [Failure Diary / 失败日记](patterns/memory/memory-loop.md) | [Layered Retention / 分层保留](patterns/memory/memory-hierarchy.md) |
| Reasoning / 推理 | [Chain-of-Thought / 思维链](patterns/reasoning/reasoning-chain.md) | [Complexity-Based Routing / 复杂度路由](patterns/reasoning/reasoning-routing.md) | [Parallel Exploration / 并行探索](patterns/reasoning/reasoning-parallel.md) | [Extension Candidate / 扩展候选](patterns/reasoning/reasoning-orchestration.md) | [Iterative Hypothesis Testing / 迭代假设测试](patterns/reasoning/reasoning-loop.md) | [Extension Candidate / 扩展候选](patterns/reasoning/reasoning-hierarchy.md) |
| Action / 行动 | [Prompt Chaining / 提示链](patterns/action/action-chain.md) | [Tool Dispatch / 工具分派](patterns/action/action-routing.md) | [Extension Candidate / 扩展候选](patterns/action/action-parallel.md) | [Plan-and-Execute / 计划并执行](patterns/action/action-orchestration.md) | [Extension Candidate / 扩展候选](patterns/action/action-loop.md) | [Guardrail Sandwich / 护栏夹层](patterns/action/action-hierarchy.md) |
| Reflection / 反思 | [Generator-Critic / 生成器-批评器](patterns/reflection/reflection-chain.md) | [Skill Package / 技能包](patterns/reflection/reflection-routing.md) | [Extension Candidate / 扩展候选](patterns/reflection/reflection-parallel.md) | [Extension Candidate / 扩展候选](patterns/reflection/reflection-orchestration.md) | [Self-Heal Loop / 自愈循环](patterns/reflection/reflection-loop.md) | [Experience Replay / 经验回放](patterns/reflection/reflection-hierarchy.md) |
| Collaboration / 协作 | [Handoff Chain / 交接链](patterns/collaboration/collaboration-chain.md) | [Extension Candidate / 扩展候选](patterns/collaboration/collaboration-routing.md) | [Fan-Out/Gather / 扇出汇聚](patterns/collaboration/collaboration-parallel.md) | [Extension Candidate / 扩展候选](patterns/collaboration/collaboration-orchestration.md) | [Adversarial Review / 对抗评审](patterns/collaboration/collaboration-loop.md) | [Hierarchical Delegation / 层级委派](patterns/collaboration/collaboration-hierarchy.md) |
| Governance / 治理 | [Extension Candidate / 扩展候选](patterns/governance/governance-chain.md) | [Approval Gate / 审批门禁](patterns/governance/governance-routing.md) | [Progressive Commitment / 渐进承诺](patterns/governance/governance-parallel.md) | [Observability Harness / 可观测性框架](patterns/governance/governance-orchestration.md) | [Extension Candidate / 扩展候选](patterns/governance/governance-loop.md) | [Blast Radius Control / 爆炸半径控制](patterns/governance/governance-hierarchy.md) |

## Cross-Cell Composition / 跨单元模式组合

Use [Pattern Combination / 模式组合](pattern-combination-execution-flow.md) (`PATTERN_0053`) to connect existing cells with explicit evidence, versions, dependencies, budgets and acceptance. Its [14 independent probes / 十四类独立探针](pattern-combination-observability-probes.md) extend the usage of `PATTERN_0052` without replacing the shared runtime protocol. A composition facet may reference an extension candidate without naming or promoting that cell. / 使用模式组合连接既有单元，明确证据、版本、依赖、预算及验收。配套探针扩展既有模式的用法，不替换共享运行协议；组合视角引用扩展候选不代表命名或晋升该单元。

## Reading A Cell / 阅读单元格

The governance row shares a [source-backed execution flow](governance-execution-flow.md), [independent probe catalog](governance-observability-probes.md) and [exchange contract](governance-contract.md). These are draft specifications for the existing cells, not additional named patterns or deployed controls. / 治理行共用有来源的执行流程、独立探针目录与交互契约；它们是现有单元的草案规格，不新增命名模式，也不代表控制已经部署。

- Use the link to inspect symptoms, fit signals, and modification guidance. / 使用链接查看症状、适配信号和修改建议。
- Use `references/patterns/<capability-key>/cell.md` as the vertical introduction before opening a specific pattern file. / 打开具体模式文件前，使用 `references/patterns/<capability-key>/cell.md` 作为纵轴导论。
- After a pattern is applied, produce the runtime Trace in the analyzed project at `.harness-analysis/<analysis_id>/trace.yaml` using `trace-schema.md`. / 应用模式后，依据 `trace-schema.md` 在被分析项目的 `.harness-analysis/<analysis_id>/trace.yaml` 生成运行时 Trace。
- Use `pattern-catalog.md` for compact pattern selection across the whole matrix. / 使用 `pattern-catalog.md` 快速跨矩阵选择模式。
- Treat extension candidates as prompts for future pattern discovery, not as missing work. / 将扩展候选视为未来模式发现入口，而不是当前遗漏。

## Maintenance Rules / 维护规则

- Keep every link pointing to a real dedicated file in `references/patterns/`. / 保证每个链接指向 `references/patterns/` 中真实存在的独立文件。
- Keep every vertical capability backed by a guide in `references/patterns/<capability-key>/cell.md`. / 保证每个纵轴能力都有 `references/patterns/<capability-key>/cell.md` 下的导论文件。
- Treat any bundled `references/patterns/<capability-key>/trace.md` as curated historical evidence, not a runtime write target. / 将 Skill 内置的 `references/patterns/<capability-key>/trace.md` 视为精选历史证据，而不是运行时写入目标。
- When a vertical capability is added, add a row, one folder, one guide file, and one pattern file for each horizontal mode; add curated Trace history only when explicitly requested. / 新增纵轴能力时，增加一行、一个文件夹、一个导论文件，并为每个横轴模式创建一个模式文件；仅在明确要求时增加精选 Trace 历史。
- When a horizontal mode is added, add a column, update every guide file, and create one pattern file in every capability folder. / 新增横轴模式时，增加一列、更新每个导论文件，并在每个能力文件夹中创建一个模式文件。
- Keep existing keys stable unless a migration is explicitly requested. / 除非明确要求迁移，否则保持现有 key 稳定。

Blast Radius Control / 爆炸半径控制 remains `COG_GOVERNANCE__TOP_HIERARCHY`, `PATTERN_0050`; its [execution](blast-radius-execution-flow.md) and [independent probes](blast-radius-observability-probes.md) adapt across the six topologies without filling extension-candidate cells. / 爆炸半径控制保留治理层级主坐标及现有编号，执行与独立探针适配六类拓扑，不填充扩展候选单元。

Observability Harness / 可观测性框架 keeps `COG_GOVERNANCE__TOP_ORCHESTRATION`, `PATTERN_0049`; its [execution](observability-execution-flow.md) and [independent probes](observability-probes.md) cover business-result verification across six topologies without changing cell identities or shared `PATTERN_0052`. / 可观测性框架保留治理编排主坐标和现有编号，执行与独立探针跨六类拓扑覆盖业务结果核验，不改动单元身份或共享探针模式。

Progressive Commitment / 渐进承诺 remains `COG_GOVERNANCE__TOP_PARALLEL`, `PATTERN_0048`; its [execution](progressive-commitment-execution-flow.md) and [probes](progressive-commitment-observability-probes.md) add sequential task stages and cross-run evidence feedback while preserving independent parallel checks. Source chain/loop coordinates do not rename or fill cells. / 渐进承诺保留治理并行坐标及编号；执行与探针补充顺序任务阶段及跨运行证据反馈，同时保留独立并行检查，来源链式循环坐标不改名或填充单元。
