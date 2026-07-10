# Matrix Index / 交织表总览

Use this index to locate the diagnostic cell for a capability and orchestration mode. The initial matrix is 7x6, but rows and columns are extensible. Pattern names are adapted from arXiv:2605.13850. / 使用本索引定位能力与编排模式对应的诊断单元。初始矩阵为 7x6，但行和列都可扩展。模式名称参考 arXiv:2605.13850 并调整为诊断用途。

Provenance summary / 来源摘要: 28 upstream named patterns / 上游 28 个命名模式, 14 upstream blank cells / 上游 14 个空白单元, two local promotions / 2 个本地晋升模式 (`Progressive Discovery`, `Layered Retention`), and 12 remaining extension candidates / 剩余 12 个扩展候选。Use `registry.json` for authoritative IDs, source names, local aliases, status, and maturity. / 权威 ID、来源名称、本地别名、状态和成熟度以 `registry.json` 为准。

## Initial Matrix / 初始交织表

| Capability / 能力 | Chain / 链式 | Routing / 路由 | Parallel / 并行 | Orchestration / 编排 | Loop / 循环 | Hierarchy / 层级 |
| --- | --- | --- | --- | --- | --- | --- |
| Perception / 感知 | [Semantic Compaction / 语义压缩](patterns/perception/perception-chain.md) | [Context Triage / 上下文分诊](patterns/perception/perception-routing.md) | [Multi-Modal Fusion / 多模态融合](patterns/perception/perception-parallel.md) | [Progressive Disclosure / 渐进披露](patterns/perception/perception-orchestration.md) | [Progressive Discovery / 渐进式发现](patterns/perception/perception-loop.md) | [Extension Candidate / 扩展候选](patterns/perception/perception-hierarchy.md) |
| Memory / 记忆 | [RAG Pipeline / RAG 管线](patterns/memory/memory-chain.md) | [Hierarchical Retrieval / 层级检索](patterns/memory/memory-routing.md) | [Extension Candidate / 扩展候选](patterns/memory/memory-parallel.md) | [Progress Tracking / 进度追踪](patterns/memory/memory-orchestration.md) | [Failure Diary / 失败日记](patterns/memory/memory-loop.md) | [Layered Retention / 分层保留](patterns/memory/memory-hierarchy.md) |
| Reasoning / 推理 | [Chain-of-Thought / 思维链](patterns/reasoning/reasoning-chain.md) | [Complexity-Based Routing / 复杂度路由](patterns/reasoning/reasoning-routing.md) | [Parallel Exploration / 并行探索](patterns/reasoning/reasoning-parallel.md) | [Extension Candidate / 扩展候选](patterns/reasoning/reasoning-orchestration.md) | [Iterative Hypothesis Testing / 迭代假设测试](patterns/reasoning/reasoning-loop.md) | [Extension Candidate / 扩展候选](patterns/reasoning/reasoning-hierarchy.md) |
| Action / 行动 | [Prompt Chaining / 提示链](patterns/action/action-chain.md) | [Tool Dispatch / 工具分派](patterns/action/action-routing.md) | [Extension Candidate / 扩展候选](patterns/action/action-parallel.md) | [Plan-and-Execute / 计划并执行](patterns/action/action-orchestration.md) | [Extension Candidate / 扩展候选](patterns/action/action-loop.md) | [Guardrail Sandwich / 护栏夹层](patterns/action/action-hierarchy.md) |
| Reflection / 反思 | [Generator-Critic / 生成器-批评器](patterns/reflection/reflection-chain.md) | [Skill Package / 技能包](patterns/reflection/reflection-routing.md) | [Extension Candidate / 扩展候选](patterns/reflection/reflection-parallel.md) | [Extension Candidate / 扩展候选](patterns/reflection/reflection-orchestration.md) | [Self-Heal Loop / 自愈循环](patterns/reflection/reflection-loop.md) | [Experience Replay / 经验回放](patterns/reflection/reflection-hierarchy.md) |
| Collaboration / 协作 | [Handoff Chain / 交接链](patterns/collaboration/collaboration-chain.md) | [Extension Candidate / 扩展候选](patterns/collaboration/collaboration-routing.md) | [Fan-Out/Gather / 扇出汇聚](patterns/collaboration/collaboration-parallel.md) | [Extension Candidate / 扩展候选](patterns/collaboration/collaboration-orchestration.md) | [Adversarial Review / 对抗评审](patterns/collaboration/collaboration-loop.md) | [Hierarchical Delegation / 层级委派](patterns/collaboration/collaboration-hierarchy.md) |
| Governance / 治理 | [Extension Candidate / 扩展候选](patterns/governance/governance-chain.md) | [Approval Gate / 审批门禁](patterns/governance/governance-routing.md) | [Progressive Commitment / 渐进承诺](patterns/governance/governance-parallel.md) | [Observability Harness / 可观测性框架](patterns/governance/governance-orchestration.md) | [Extension Candidate / 扩展候选](patterns/governance/governance-loop.md) | [Blast Radius Control / 爆炸半径控制](patterns/governance/governance-hierarchy.md) |

## Reading A Cell / 阅读单元格

- Use the link to inspect symptoms, fit signals, and modification guidance. / 使用链接查看症状、适配信号和修改建议。
- Use `references/patterns/<capability-key>/cell.md` as the vertical introduction before opening a specific pattern file. / 打开具体模式文件前，使用 `references/patterns/<capability-key>/cell.md` 作为纵轴导论。
- Use `references/patterns/<capability-key>/trace.md` to record outcomes after a pattern is applied. / 应用模式后，使用 `references/patterns/<capability-key>/trace.md` 记录结果。
- Use `pattern-catalog.md` for compact pattern selection across the whole matrix. / 使用 `pattern-catalog.md` 快速跨矩阵选择模式。
- Treat extension candidates as prompts for future pattern discovery, not as missing work. / 将扩展候选视为未来模式发现入口，而不是当前遗漏。

## Maintenance Rules / 维护规则

- Keep every link pointing to a real dedicated file in `references/patterns/`. / 保证每个链接指向 `references/patterns/` 中真实存在的独立文件。
- Keep every vertical capability backed by a guide in `references/patterns/<capability-key>/cell.md`. / 保证每个纵轴能力都有 `references/patterns/<capability-key>/cell.md` 下的导论文件。
- Keep every vertical capability backed by a trace log in `references/patterns/<capability-key>/trace.md`. / 保证每个纵轴能力都有 `references/patterns/<capability-key>/trace.md` 下的追踪日志。
- When a vertical capability is added, add a row, one folder, one guide file, one trace file, and one pattern file for each horizontal mode. / 新增纵轴能力时，增加一行、一个文件夹、一个导论文件、一个追踪文件，并为每个横轴模式创建一个模式文件。
- When a horizontal mode is added, add a column, update every guide file, and create one pattern file in every capability folder. / 新增横轴模式时，增加一列、更新每个导论文件，并在每个能力文件夹中创建一个模式文件。
- Keep existing keys stable unless a migration is explicitly requested. / 除非明确要求迁移，否则保持现有 key 稳定。
