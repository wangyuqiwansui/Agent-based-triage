# Chain-of-Thought / 思维链 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-chain / 推理 x 链式
Capability / 能力: Reasoning / 推理
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-chain.md](reasoning-chain.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Chain-of-Thought / 思维链 improves the workflow after selection or application. / 使用以下指标观察 Chain-of-Thought / 思维链 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `step_check_pass_rate` (intermediate conclusions passing their checkpoint), `chain_acceptance_rate` (final conclusions accepted downstream), and `error_localization_rate` (share of wrong conclusions traceable to a specific step). / `step_check_pass_rate`（中间结论通过检查点的比例）、`chain_acceptance_rate`（最终结论被下游采纳的比例）、`error_localization_rate`（错误结论可定位到具体步骤的比例）。
- 时延指标 / Latency Metrics: `per_step_latency`, `chain_total_latency` versus a single-shot baseline, and `checkpoint_overhead` (time spent checking versus reasoning). / `per_step_latency`（单步时延）、`chain_total_latency`（链式总时延，对比一次性推理基线）、`checkpoint_overhead`（检查耗时占推理耗时比）。
- 成本指标 / Cost Metrics: `tokens_per_step`, total chain tokens versus single-shot baseline, and rework tokens avoided by catching errors at checkpoints. / `tokens_per_step`（单步 token）、链式总 token 对比一次性基线、检查点拦截错误而避免的返工 token。
- 风险指标 / Risk Metrics: `error_propagation_depth` (steps an undetected error traveled before being caught), `forced_single_path_rate` (chains that should have escalated to reasoning-parallel or reasoning-loop but did not), and `unrecorded_step_count` (intermediate conclusions lost between steps, watch `FAIL_0006`). / `error_propagation_depth`（未被发现的错误在被捕获前传播的步数）、`forced_single_path_rate`（本应升级到 reasoning-parallel 或 reasoning-loop 却硬撑链式的比例）、`unrecorded_step_count`（步骤间丢失的中间结论数，对应 `FAIL_0006`）。
- Trace 指标 / Trace Metrics: `step_record_completeness` (input, claim, grounding, link recorded per step, per `GOV_0002`), checkpoint result coverage, and escalation event coverage. / `step_record_completeness`（每步输入、主张、依据、衔接的记录完整率，按 `GOV_0002`）、检查点结果覆盖率、升级事件覆盖率。

### Default Gate Suggestions / 默认门控建议

- Alert when `error_propagation_depth` exceeds 1 — an error crossing more than one checkpoint means the checkpoint rule itself is too weak. / 当 `error_propagation_depth` 超过 1 时告警——错误穿过多于一个检查点说明检查点规则本身太弱。
- Block the next step when the current intermediate conclusion fails its checkpoint; require a fix or an escalation to reasoning-loop or reasoning-parallel, never a silent pass-through. / 当前中间结论未通过检查点时阻断下一步；要求修复或升级到 reasoning-loop / reasoning-parallel，禁止静默放行。
