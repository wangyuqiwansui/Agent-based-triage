# Self-Heal Loop / 自愈循环 Observability Metrics / 可观测性指标

Cell / 交织点: reflection-loop / 反思 x 循环
Capability / 能力: Reflection / 反思
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reflection-loop.md](reflection-loop.md)

Shared Probe Contract / 共享探针契约: use [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md), especially `PROBE_0016` through `PROBE_0023`, with the round observation pack defined by the governed [Reflection Execution Flow / 反思执行流程](../../reflection-execution-flow.md). / 使用共享工作流可观测性探针，重点使用 `PROBE_0016` 至 `PROBE_0023`，并采用受治理反思执行流程定义的轮次观察包。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Self-Heal Loop / 自愈循环 improves the workflow after selection or application. / 使用以下指标观察 Self-Heal Loop / 自愈循环 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `heal_success_rate` (loops exiting on verifier pass within budget), `first_attempt_fix_rate`, and `regression_guard_pass_rate` (fixes that kept previously passing items green). / `heal_success_rate`（预算内以验证器通过退出的循环比例）、`first_attempt_fix_rate`（首次尝试即修复的比例）、`regression_guard_pass_rate`（未破坏已通过项的修复比例）。
- 时延指标 / Latency Metrics: `verify_fix_round_time` (one verify-diagnose-fix cycle), `attempts_to_green` (rounds until verifier pass), and escalation hand-over latency when the budget is exhausted. / `verify_fix_round_time`（一轮验证-诊断-修复耗时）、`attempts_to_green`（到验证器通过的轮数）、预算耗尽时的升级交接时延。
- 成本指标 / Cost Metrics: tokens and compute per repair round, verifier execution cost per round, and human repair effort avoided by successful self-heals. / 每轮修复的 token 与计算成本、每轮验证器执行成本、自愈成功所避免的人工修复投入。
- 风险指标 / Risk Metrics: `max_attempt_hit_rate` (loops exhausting their budget, watch `FAIL_0007`), `verifier_weakening_attempts` (loop-side edits to tests or schemas — must be zero), `regression_break_count` (fixes that broke passing items), and out-of-sandbox repair count (violates `GOV_0003`). / `max_attempt_hit_rate`（耗尽预算的循环比例，对应 `FAIL_0007`）、`verifier_weakening_attempts`（循环侧修改测试或 schema 的次数——必须为零）、`regression_break_count`（破坏已通过项的修复数）、沙箱外修复数量（违反 `GOV_0003`）。
- Trace 指标 / Trace Metrics: `loop_log_completeness` (failure signature, fix, verdict recorded per round, per `GOV_0002`), escalation-package completeness (attempt history attached), and escalated-loop closure rate. / `loop_log_completeness`（每轮失败特征、修复、裁定的记录完整率，按 `GOV_0002`）、升级包完整率（附带尝试历史）、升级循环的闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert on any `verifier_weakening_attempts` above zero and when `max_attempt_hit_rate` climbs — the former means the loop is gaming its own exit, the latter means failure classes beyond mechanical repair are being routed into the loop. / `verifier_weakening_attempts` 一旦大于零即告警，`max_attempt_hit_rate` 上升同样告警——前者说明循环在博弈自己的退出条件，后者说明超出机械修复能力的失败类被错误路由进循环。
- Block the loop from continuing past its attempt budget or after a regression-guard failure; the only legal continuations are rollback of the offending fix and escalation with full attempt history. / 超出尝试预算或回归护栏失败后阻断循环继续；唯一合法的继续方式是回滚肇事修复并带全部尝试历史升级。
