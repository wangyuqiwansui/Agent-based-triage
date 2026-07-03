# Hierarchical Retrieval / 层级检索 Observability Metrics / 可观测性指标

Cell / 交织点: memory-routing / 记忆 x 路由
Capability / 能力: Memory / 记忆
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [memory-routing.md](memory-routing.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Hierarchical Retrieval / 层级检索 improves the workflow after selection or application. / 使用以下指标观察 Hierarchical Retrieval / 层级检索 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `tier_hit_rate` per tier (queries answered at their entry tier), `answer_tier_accuracy` (sampled audit that the answering tier held the best available answer), and `short_circuit_incidents` (shallow answers accepted while a better answer lived below). / 各层 `tier_hit_rate`（在入口层即获答的查询比例）、`answer_tier_accuracy`（作答层确实持有最佳可得答案的抽样审计）、`short_circuit_incidents`（浅层答案被接受而更优答案在下层的事件数）。
- 时延指标 / Latency Metrics: `retrieval_latency_by_tier`, `fall_through_round_trip` (miss verdict to next-tier answer), and hot-path latency versus the flat-store baseline. / `retrieval_latency_by_tier`（各层检索时延）、`fall_through_round_trip`（未命中裁定到下一层作答的往返）、热路径时延对比扁平库基线。
- 成本指标 / Cost Metrics: query cost by tier, `unnecessary_cold_dive_cost` (cold queries whose answer existed warm or hot), and re-derivation work avoided (decisions reused from warm records instead of re-argued). / 各层查询成本、`unnecessary_cold_dive_cost`（答案本在温热层却下潜冷层的查询成本）、避免的重推工作（决策从温层记录复用而非重新论证）。
- 风险指标 / Risk Metrics: `retrieval_miss_rate` (true answer existed but was never surfaced, `FAIL_0002`), `unfiltered_cold_injection_count` (cold material entering context without relevance filtering, `FAIL_0001`), `provenance_gap_rate` (injected results lacking tier and source tags), and stale-promotion incidents (outdated entries promoted and treated as current). / `retrieval_miss_rate`（真答案存在却从未浮出，`FAIL_0002`）、`unfiltered_cold_injection_count`（未经相关性过滤入上下文的冷层材料数，`FAIL_0001`）、`provenance_gap_rate`（注入结果缺层级与来源标注的比例）、过期晋升事件（陈旧条目被晋升并被当作现行知识）。
- Trace 指标 / Trace Metrics: `routing_log_completeness` (query intent, entry tier, misses, answering tier recorded per `GOV_0002`), promotion and demotion event coverage with provenance, and miss-verdict recording rate before fall-through stops. / `routing_log_completeness`（查询意图、入口层、未命中、作答层的记录完整率，按 `GOV_0002`）、带出处的晋升降级事件覆盖率、停止下探前未命中裁定的记录率。

### Default Gate Suggestions / 默认门控建议

- Alert when `short_circuit_incidents` or `retrieval_miss_rate` climbs — both mean intent classification or miss verdicts are letting shallow tiers eat queries whose answers live below (`FAIL_0002`), and tier boundaries need re-derivation per Law 5. / `short_circuit_incidents` 或 `retrieval_miss_rate` 上升即告警——两者都说明意图分类或未命中裁定正让浅层吞掉答案在下层的查询（`FAIL_0002`），层边界需按定律 5 重推。
- Block injection of cold-tier results that lack provenance tags or skipped relevance filtering, and block promotions without source and date; return them for filtering instead of letting archive material masquerade as current knowledge (`FAIL_0001`). / 缺出处标注或跳过相关性过滤的冷层结果禁止注入，无来源与日期的晋升同样阻断；退回过滤而不是任由归档材料冒充现行知识（`FAIL_0001`）。
