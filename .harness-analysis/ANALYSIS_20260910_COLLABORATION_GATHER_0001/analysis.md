# 扇出聚合模式完善记录 / Fan-Out/Gather Pattern Revision

本次将两份用户草案接入现有 `PATTERN_0044 / CELL_COLLABORATION_PARALLEL`，补齐执行、补数、观测和验收规格，以及来源保真与同步校验。专用调度、采集、持久状态与 GM 指标计算仍未实现；不将规格验收当作生产运行验证。

This revision integrates the two supplied drafts into the existing pattern, completing execution, supplementation, observation and acceptance specifications with source-fidelity and synchronization checks. Dedicated scheduling, collection, durable state and GM calculations remain unimplemented; documentation validation is not production verification.

| 已识别缺口 / Observed gap | 本次改进 / Revision | 文档依据 / Source basis |
| --- | --- | --- |
| 泛化的 worker 输出不足以区分返回与合格 / Generic worker outputs conflated returns with qualified coverage | 冻结 R 和逐片责任，版本化尝试与工件，以最终 Q 计算覆盖 / Freeze R and obligations, version attempts/artifacts and use final Q | 执行 §4–5、§7.1–7.5；探针 M01 / Execution §4–5, §7.1–7.5; probe M01 |
| 投票选项缺少可比与来源前提 / Voting lacked comparison and lineage prerequisites | 完整比较键，分别记录会话／工作区／工具边界；默认不投票 / Full comparison key, separate isolation dimensions and default no voting | 执行 §7.6–7.8、E01/E03/E04 / Execution §7.6–7.8, E01/E03/E04 |
| “综合”没有完整收口职责 / Synthesis lacked a complete gather procedure | 盘点缺席、归一口径、结论和血缘去重、冲突处理、接缝检查 / Inventory absence, normalize, deduplicate conclusions/lineage, preserve conflicts, check seams | 执行 N04–N08 / Execution N04–N08 |
| 局部合格可能掩盖组合失败或权限不足 / Local validity could obscure failed composition or missing authority | 分离工件合格、accepted、接缝、业务准入、动作授权、实际交接 / Separate qualification, acceptance, seams, admission, authority and delivery | 执行 §7.9–7.11、E08 / Execution §7.9–7.11, E08 |
| 缺少可恢复补数与业务补证的明确边界 / Recovery and new evidence collection lacked separation | 五类消息；精确基准、字段白名单、来源与权限核验；追加派生版本并重验；按 gap 去重闭环 / Five messages, exact-base/field/source/authority validation, derived revisions, rechecks and gap-level closure | 两份文档 §6；探针 §10–11 / Both §6; probe §10–11 |
| 泛化指标缺少可信分母、参考集与空值规则 / Generic metrics lacked trustworthy denominators, reference sets and null semantics | 完整保留 GM01–GM17，区分不可计算／不适用／部分可用／可用与暂定状态 / Preserve all 17 definitions and explicit metric states | 探针 §7–9 / Probe §7–9 |
| 固定条目数和结果相同被用作过强结论 / Item counts and identical results supported overstrong conclusions | 按实测吞吐、责任、权限与成本选型；先查来源血缘及执行证据；无基线不声称因果收益 / Select from measurements and obligations; inspect lineage and execution; no causal gains without a baseline | 执行 §2；探针 M02/M04 / Execution §2; probe M02/M04 |
| 新旧协议和指标同名容易误接 / Similar protocol and metric names could imply false compatibility | 专用 0.1.0 与通用来源 2.0.0／执行配置 3.0.0 分开；GM11 耗时不等于 CSM32 收口占比，GM08 同源冗余不等于 CSM33 意外重复成本 / Keep protocol and metric semantics separate | 所供 §6；仓库共享来源映射 CSM32/33 / Supplied §6; shared source map CSM32/33 |

两份原文共享补数协议一致。来源映射逐项保留 11 个执行节点、11 个探针节点、17 项指标、16 个执行验收用例和 20 个探针验收用例，并绑定原文行范围、段落摘要和全文 SHA-256。原文的目录建议、角色提示和执行模板作为设计数据，未作为本会话的操作指令。

The supplied shared protocols match. The map preserves all 11 execution nodes, 11 probe nodes, 17 metrics, 16 execution cases and 20 probe cases with original line ranges, excerpt digests and full-source SHA-256. Source directory suggestions, role prompts and execution templates were treated as design data, not session instructions.

维护入口位于 `skills/harness-engineering-patterns`，保留原有未提交的协作与反思改动。同步脚本仅生成有标记的流程、指标、验收表和共享契约，写入前核验来源和双方标记；无效来源不能被同步成看似有效的文档。测试覆盖公式／边界误改、遗漏／重复映射、截短参考、来源或协议漂移、错误实现声明、越界来源路径以及幂等和手写正文保留。

Maintained resources stay under the existing skill. Prior uncommitted collaboration and reflection work is preserved. The synchronizer updates only generated blocks after source and peer-marker preflight. Tests cover incorrect formulas/boundaries, omitted/duplicated mappings, truncated references, source/protocol drift, false implementation claims, out-of-scope source paths, idempotency and authored-prose preservation.

原文业务验收全部保持 `pending`，专用指标保持 `specification_only`；它们与本次新增的文档工具测试是两类不同验收。后续接入宿主时应以两份模式文档中的完整用例作为业务验收清单。

All source business acceptance cases remain pending and dedicated metrics remain specification-only. These are separate from the document-tool tests added here. Host integration should use the complete source-derived acceptance tables in the two pattern documents.

最终自动校验与回归结果见同目录的 `validation.json`、`test-results.txt` 和 `trace.yaml`。 / Final automated validation and regression results are recorded in the adjacent validation, test-results and trace files.
