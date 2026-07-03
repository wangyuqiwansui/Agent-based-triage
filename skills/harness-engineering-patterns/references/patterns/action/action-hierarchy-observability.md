# Guardrail Sandwich / 护栏夹层 Observability Metrics / 可观测性指标

Cell / 交织点: action-hierarchy / 行动 x 层级
Capability / 能力: Action / 行动
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [action-hierarchy.md](action-hierarchy.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Guardrail Sandwich / 护栏夹层 improves the workflow after selection or application. / 使用以下指标观察 Guardrail Sandwich / 护栏夹层 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `precheck_block_precision` (blocked actions that were genuinely unsafe, by sampled audit), `rehearsal_accuracy` (rehearsed impact list matching actual side effects), and `postverify_pass_rate`. / `precheck_block_precision`（被阻断动作确属不安全的比例，抽样审计）、`rehearsal_accuracy`（预演影响清单与实际副作用的吻合度）、`postverify_pass_rate`（后置验证通过率）。
- 时延指标 / Latency Metrics: `sandwich_overhead` (pre-check plus post-verify time relative to execution time), rehearsal latency per action class, and rollback execution time when triggered. / `sandwich_overhead`（前置检查加后置验证耗时相对执行耗时）、各动作类的预演时延、触发回滚时的回滚执行时间。
- 成本指标 / Cost Metrics: rehearsal compute cost per irreversible action, `full_sandwich_share` (actions receiving all three layers versus total — over-sandwiching trivial actions wastes throughput), and incident cost avoided by pre-execution blocks. / 每个不可逆动作的预演计算成本、`full_sandwich_share`（配齐三层的动作占比——对琐碎动作过度夹层浪费吞吐）、执行前阻断避免的事故成本。
- 风险指标 / Risk Metrics: `sandwich_bypass_count` (irreversible actions executed outside the sandwich path, `FAIL_0005`), `sandbox_escape_events` (`FAIL_0009`), `rehearsal_gap_incidents` (actual side effects absent from the rehearsed list), and untested-rollback share. / `sandwich_bypass_count`（绕开夹层路径执行的不可逆动作数，`FAIL_0005`）、`sandbox_escape_events`（沙箱逃逸事件，`FAIL_0009`）、`rehearsal_gap_incidents`（实际副作用未出现在预演清单中的事件数）、回滚预案未经验证的占比。
- Trace 指标 / Trace Metrics: `layer_verdict_completeness` (pre-check, execution, post-verify verdicts recorded per action, per `GOV_0002`), approval-escalation event coverage per `GOV_0001`, and rollback event closure rate. / `layer_verdict_completeness`（每个动作的前置、执行、后置三层裁定记录完整率，按 `GOV_0002`）、审批升级事件覆盖率（按 `GOV_0001`）、回滚事件闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert on any `sandwich_bypass_count` above zero for irreversible action classes — a single bypass means the sandwich is not the only execution path and `FAIL_0005` is live. / 不可逆动作类的 `sandwich_bypass_count` 一旦大于零即告警——出现一次绕过就说明夹层不是唯一执行路径，`FAIL_0005` 已成现实。
- Block execution when the impact rehearsal fails, is skipped for an irreversible class, or the rollback plan is missing or untested; escalate to approval per `GOV_0001` instead of proceeding. / 影响面预演失败、不可逆动作类跳过预演、或回滚预案缺失/未经验证时阻断执行；按 `GOV_0001` 升级审批而不是继续。
