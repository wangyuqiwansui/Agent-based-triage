# Iterative Hypothesis Testing / 迭代假设测试 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-loop / 推理 x 循环
Capability / 能力: Reasoning / 推理
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-loop.md](reasoning-loop.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Iterative Hypothesis Testing / 迭代假设测试 improves the workflow after selection or application. / 使用以下指标观察 Iterative Hypothesis Testing / 迭代假设测试 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `hypothesis_confirm_rate` (loops ending in a confirmed hypothesis), `probe_discrimination_rate` (probes that actually moved confidence up or down), and `post_fix_recurrence_rate` (confirmed root causes that later recur, indicating a false confirm). / `hypothesis_confirm_rate`（以假设确认收尾的循环比例）、`probe_discrimination_rate`（真正改变置信度的探测比例）、`post_fix_recurrence_rate`（确认后又复发的根因比例，提示假确认）。
- 时延指标 / Latency Metrics: `iterations_to_confirm` (median iterations before an exit condition fires), `per_iteration_latency` including probe wait time, and total loop latency versus one-shot baseline. / `iterations_to_confirm`（退出条件触发前的中位迭代数）、`per_iteration_latency`（含探测等待的单轮时延）、循环总时延对比一次性推理基线。
- 成本指标 / Cost Metrics: `tokens_per_iteration`, probe execution cost per iteration, and wasted-iteration share (iterations that added no confidence change). / `tokens_per_iteration`（单轮 token）、单轮探测执行成本、无效迭代占比（未带来任何置信度变化的轮次）。
- 风险指标 / Risk Metrics: `max_iteration_hit_rate` (loops stopped by the hard cap, watch `FAIL_0007`), `no_new_evidence_streak` (consecutive iterations repeating a probe without new evidence), and count of environment-mutating probes run outside sandbox boundaries (violates `GOV_0003`). / `max_iteration_hit_rate`（被硬上限止损的循环比例，对应 `FAIL_0007`）、`no_new_evidence_streak`（无新证据重复探测的连续轮数）、在沙箱边界外运行的环境变更型探测数量（违反 `GOV_0003`）。
- Trace 指标 / Trace Metrics: `loop_log_completeness` (probe, observation, confidence delta recorded per iteration, per `GOV_0002`), eliminated-hypothesis record coverage, and escalation package completeness on budget exhaustion. / `loop_log_completeness`（每轮探测、观察、置信度变化的记录完整率，按 `GOV_0002`）、被排除假设记录覆盖率、预算耗尽时升级包完整率。

### Default Gate Suggestions / 默认门控建议

- Alert when `no_new_evidence_streak` reaches 2 — repeating the same probe without new evidence is the runaway-retry signature of `FAIL_0007`. / 当 `no_new_evidence_streak` 达到 2 时告警——无新证据重复同一探测正是 `FAIL_0007` 失控重试的特征。
- Block further iterations at `max_iterations` and require escalation with the full evidence trail; never let the loop silently restart with a fresh budget. / 到达 `max_iterations` 即阻断后续迭代并要求携完整证据链升级；禁止循环携新预算静默重启。
