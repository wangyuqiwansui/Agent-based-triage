# Iterative Hypothesis Testing / 迭代假设测试 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-loop / 推理 x 循环
Capability / 能力: Reasoning / 推理
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-loop.md](reasoning-loop.md)
Shared Probe Suite / 共享探针套件: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)
Metric Registry / 指标注册表: [`metric_registry.json`](../../../runtime/metric_registry.json)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Iterative Hypothesis Testing / 迭代假设测试 improves the workflow after selection or application. / 使用以下指标观察 Iterative Hypothesis Testing / 迭代假设测试 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `hypothesis_confirm_rate` (loops ending in a validator-confirmed hypothesis), `probe_discrimination_rate` (probes that add valid evidence, eliminate a hypothesis, or materially change an evidence-weighted ranking), and `post_fix_recurrence_rate` (confirmed root causes that later recur, indicating a false confirm). / `hypothesis_confirm_rate`（以验证器确认的假设收尾的循环比例）、`probe_discrimination_rate`（新增有效证据、淘汰假设或实质改变证据加权排序的探测比例）、`post_fix_recurrence_rate`（确认后又复发的根因比例，提示假确认）。
- 时延指标 / Latency Metrics: `iterations_to_confirm` (median iterations before an exit condition fires), `per_iteration_latency` including probe wait time, and total loop latency versus one-shot baseline. / `iterations_to_confirm`（退出条件触发前的中位迭代数）、`per_iteration_latency`（含探测等待的单轮时延）、循环总时延对比一次性推理基线。
- 成本指标 / Cost Metrics: `tokens_per_iteration`, probe execution cost per iteration, and wasted-iteration share (iterations that add no valid evidence, eliminate no hypothesis, and cause no material decision change). / `tokens_per_iteration`（单轮 token）、单轮探测执行成本、无效迭代占比（未新增有效证据、未淘汰假设且未实质改变决定的轮次）。
- 风险指标 / Risk Metrics: `max_iteration_hit_rate` (loops stopped by the hard cap, watch `FAIL_0007`), `no_new_evidence_streak` (consecutive iterations repeating a probe without new evidence), and count of environment-mutating probes run outside sandbox boundaries (violates `GOV_0003`). / `max_iteration_hit_rate`（被硬上限止损的循环比例，对应 `FAIL_0007`）、`no_new_evidence_streak`（无新证据重复探测的连续轮数）、在沙箱边界外运行的环境变更型探测数量（违反 `GOV_0003`）。
- Trace 指标 / Trace Metrics: `loop_log_completeness` (probe, observation, evidence and hypothesis delta recorded per iteration, per `GOV_0002`), eliminated-hypothesis record coverage, and escalation package completeness on budget exhaustion. / `loop_log_completeness`（每轮探测、观察、证据与假设变化的记录完整率，按 `GOV_0002`）、被排除假设记录覆盖率、预算耗尽时升级包完整率。

### Required Probe Coverage / 必需探针覆盖

Enable task identity (`PROBE_0001`), contract completeness (`PROBE_0002`), route decision and switch reasons (`PROBE_0003`), budget and resources (`PROBE_0004`), step closure (`PROBE_0005`), evidence chain (`PROBE_0006`), tool and action (`PROBE_0007`), iteration progress (`PROBE_0009`), drift (`PROBE_0010`), validation (`PROBE_0011`), stop and escalation (`PROBE_0012`), outcome (`PROBE_0013`) for recurrence or correctness claims, privacy and governance (`PROBE_0014`), and probe self-health (`PROBE_0015`). / 启用任务身份、契约完整性、路由决定与换路原因、预算与资源、步骤闭环、证据链、工具与动作、迭代进展、漂移、验证、停止升级、结果回接（用于复发或正确性判断）、隐私治理和探针自健康探针。

Per round, record the key unknown, expected information gain, action, observation, retained/eliminated/added hypotheses, snapshot versions, progress state, cost, and stop evaluation. Define progress as new valid evidence, hypothesis elimination, or a material decision change. / 每轮记录关键未知、预期信息增益、动作、观察、保留/淘汰/新增假设、快照版本、进展状态、成本和停止判断。进展定义为新增有效证据、淘汰假设或实质改变决定。

Version metric definitions and bucket by scene, risk, iteration and no-progress limits, probe type, validator, model, tool, and outcome availability. A round with missing observation is incomplete, not evidence of no progress. / 指标口径版本化，并按场景、风险、迭代与无进展上限、探测类型、验证器、模型、工具和后验可用性分桶。观察缺失的轮次属于不完整，不应直接视为无进展证据。

### Default Gate Suggestions / 默认门控建议

- Alert when gate-eligible `no_progress_loop_rate` exceeds its owned, bucketed threshold. At run time, use the configured no-progress streak and its emitted limit event; planned diagnostics remain non-gating. / 当可用于门控的 `no_progress_loop_rate` 超过有负责人且按桶配置的阈值时告警。单次运行使用已配置的无进展连续阈值及其限制事件；规划中的诊断指标不得用于门控。
- Block further iterations at `max_iterations` and require escalation with the full evidence trail; never let the loop silently restart with a fresh budget. / 到达 `max_iterations` 即阻断后续迭代并要求携完整证据链升级；禁止循环携新预算静默重启。
