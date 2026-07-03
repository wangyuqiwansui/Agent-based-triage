# Prompt Chaining / 提示链 Observability Metrics / 可观测性指标

Cell / 交织点: action-chain / 行动 x 链式
Capability / 能力: Action / 行动
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [action-chain.md](action-chain.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Prompt Chaining / 提示链 improves the workflow after selection or application. / 使用以下指标观察 Prompt Chaining / 提示链 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `step_contract_pass_rate` (step outputs passing their output contract on first try), `final_artifact_acceptance_rate`, and `error_catch_locality` (share of defects caught at the step that produced them rather than downstream). / `step_contract_pass_rate`（步骤输出首轮通过输出契约的比例）、`final_artifact_acceptance_rate`（最终产物采纳率）、`error_catch_locality`（缺陷在产生步骤即被捕获而非流到下游的比例）。
- 时延指标 / Latency Metrics: `per_step_latency`, `handoff_overhead` (validation time between steps), and end-to-end chain latency versus the monolithic-prompt baseline. / `per_step_latency`（单步时延）、`handoff_overhead`（步骤间校验耗时）、端到端链式时延对比巨型提示基线。
- 成本指标 / Cost Metrics: `tokens_per_step`, retry tokens per step, and full-rerun cost avoided by catching defects at handoffs. / `tokens_per_step`（单步 token）、每步重试 token、因交接处拦截缺陷而避免的整链重跑成本。
- 风险指标 / Risk Metrics: `error_propagation_incidents` (defects that crossed one or more contract gates before detection), `implicit_state_break_count` (steps that failed because expected context was not explicitly passed, watch `FAIL_0006`), and `retry_exhaustion_rate` (steps hitting their retry bound, watch `FAIL_0007`). / `error_propagation_incidents`（被发现前穿过一个以上契约门的缺陷数）、`implicit_state_break_count`（因期望上下文未显式传递而失败的步骤数，对应 `FAIL_0006`）、`retry_exhaustion_rate`（触及重试上限的步骤比例，对应 `FAIL_0007`）。
- Trace 指标 / Trace Metrics: `step_ledger_completeness` (input, output, validation result recorded per step, per `GOV_0002`), on-failure action record coverage, and escalation event closure rate. / `step_ledger_completeness`（每步输入、输出、校验结果的记录完整率，按 `GOV_0002`）、失败动作记录覆盖率、升级事件闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert when `error_catch_locality` drops — defects passing contract gates mean the output contracts are too loose to stop propagation. / 当 `error_catch_locality` 下降时告警——缺陷能穿过契约门说明输出契约已松到无法阻止传播。
- Block the next step whenever the current output fails its contract; the only legal continuations are the declared on-failure actions (retry within bound, rollback, or escalate). / 当前输出未通过契约即阻断下一步；唯一合法的继续方式是声明的失败动作（限内重试、回滚或升级）。
