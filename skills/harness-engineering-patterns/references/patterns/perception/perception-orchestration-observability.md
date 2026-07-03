# Progressive Disclosure / 渐进披露 Observability Metrics / 可观测性指标

Cell / 交织点: perception-orchestration / 感知 x 编排
Capability / 能力: Perception / 感知
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [perception-orchestration.md](perception-orchestration.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Progressive Disclosure / 渐进披露 improves the workflow after selection or application. / 使用以下指标观察 Progressive Disclosure / 渐进披露 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `digest_anomaly_recall` (real incidents whose first signal was visible in the digest layer), `expansion_precision` (expansions that contributed to the eventual answer), and `drill_down_rate` (share of diagnoses needing focused or raw layers — stable and modest means the digest is doing its job). / `digest_anomaly_recall`（首个信号在摘要层可见的真实事故比例）、`expansion_precision`（对最终答案有贡献的展开比例）、`drill_down_rate`（需要聚焦或原始层的诊断占比——稳定且适中说明摘要层称职）。
- 时延指标 / Latency Metrics: `expansion_round_trip` (trigger to disclosed detail), `time_to_first_evidence` during incidents versus the full-injection baseline, and reclaim lag (suspicion cleared to budget returned). / `expansion_round_trip`（触发到细节披露的往返耗时）、事故中 `time_to_first_evidence`（对比全量注入基线）、回收滞后（疑点排除到预算收回）。
- 成本指标 / Cost Metrics: `context_budget_share` per layer (resting digest share versus expanded peaks), tokens saved versus default full injection, and orchestration overhead per expansion decision. / 每层 `context_budget_share`（静息摘要占比对比展开峰值）、相对默认全量注入节省的 token、每次展开决策的编排开销。
- 风险指标 / Risk Metrics: `triggerless_expansion_count` (expansions with no named signal — drift toward `FAIL_0001`), `starvation_incidents` (diagnoses that stalled because needed detail was hidden, `FAIL_0012`), `ratchet_leak_count` (expanded layers never reclaimed), and digest-blind incidents (anomalies invisible at the digest layer until damage). / `triggerless_expansion_count`（无具名信号的展开数——向 `FAIL_0001` 漂移）、`starvation_incidents`（因所需细节被隐藏而卡住的诊断数，`FAIL_0012`）、`ratchet_leak_count`（展开后从未回收的层数）、摘要盲区事故（异常在摘要层不可见直至损害发生）。
- Trace 指标 / Trace Metrics: `expansion_log_completeness` (trigger, layer, budget, reclaim recorded per expansion, per `GOV_0002`), visible-context reconstructability (post-incident review can replay what was visible when), and reclaim event closure rate. / `expansion_log_completeness`（每次展开的触发、层级、预算、回收记录完整率，按 `GOV_0002`）、可见上下文可重建性（事后复盘可回放何时什么可见）、回收事件闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert when `triggerless_expansion_count` rises or `starvation_incidents` recur — the former is drift back toward full injection (`FAIL_0001`), the latter means layers are tuned too tight and thresholds need re-derivation per Law 5 (`FAIL_0012`). / `triggerless_expansion_count` 上升或 `starvation_incidents` 复发即告警——前者是向全量注入回漂（`FAIL_0001`），后者说明层收得过紧、阈值需按定律 5 重推（`FAIL_0012`）。
- Block raw-layer injection when it lacks a named question or would exceed the layer cap as an unwindowed stream; the legal path is a windowed deferred read scoped to the question. / 原始层注入缺具名问题或以未开窗整流超出层上限时阻断；合法路径是围绕问题限窗的延迟读取。
