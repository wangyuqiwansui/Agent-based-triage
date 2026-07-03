# Approval Gate / 审批门禁 Observability Metrics / 可观测性指标

Cell / 交织点: governance-routing / 治理 x 路由
Capability / 能力: Governance / 治理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-routing.md](governance-routing.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Approval Gate / 审批门禁 improves the workflow after selection or application. / 使用以下指标观察 审批门禁 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `gate_precision` (blocked actions that were genuinely unsafe) and `gate_recall` (unsafe actions that were caught), stage distribution (deny/allow/gate hit ratios), and semantic-companion coverage (structural gates that also ran a semantic consistency check). / `gate_precision`（被阻断动作中确属不安全的比例）与 `gate_recall`（不安全动作被捕获的比例）、三段命中分布（拒绝/放行/门比率）、语义配套覆盖率（同时执行语义一致性检查的结构门占比）。
- 时延指标 / Latency Metrics: rule-stage decision latency (should be near-zero), human-gate waiting time, and share of workflow wall-clock spent blocked at gates. / 规则段决策时延（应接近零）、人工门等待时间、工作流墙钟中被门禁阻塞的占比。
- 成本指标 / Cost Metrics: human review effort per gated action, evidence-preparation cost for gate requests, and rework avoided by pre-execution blocking. / 每个受门动作的人工评审投入、门禁请求的证据准备成本、执行前阻断避免的返工。
- 风险指标 / Risk Metrics: approval-fatigue signals — stage-3 fire rate per reviewer per day and time-to-approve trending toward zero (instant approvals mean rubber-stamping); `FAIL_0005` permission-bypass incidents (actions misrouted into allow rules); structural-pass-semantic-fail escapes (repository-evidenced failure class, 2026-07-03). / 审批疲劳信号——每评审人每日第三段触发次数、审批耗时趋近于零（秒批意味着无脑放行）；`FAIL_0005` 权限绕过事件（动作被误路由进放行规则）；结构通过但语义失败的漏网数（本仓库 2026-07-03 实证失败类）。
- Trace 指标 / Trace Metrics: gate decision record completeness (stage, rule hit, decision, approver identity), blocked-action reason coverage, and superseded-output audit chain (bad approvals must stay replayable, not deleted). / 门禁决策记录完整率（段、命中规则、决定、审批人身份）、阻断原因覆盖率、废弃产物审计链（错误批准必须可回放，不得删除）。

### Default Gate Suggestions / 默认门控建议

- Alert when stage-3 (human gate) fire rate exceeds a per-reviewer daily budget — tighten allow rules before reviewers start clicking through. / 第三段（人工门）触发率超过每评审人日预算时告警——在评审人开始无脑点击前收紧放行规则。
- Alert when median time-to-approve falls below a floor (e.g. a few seconds) — approvals are no longer decisions. / 审批耗时中位数低于下限（如数秒）时告警——审批已不再是决策。
- Block downstream routing when a structural gate passed but its semantic consistency companion was skipped or failed. / 结构门通过但语义一致性配套被跳过或失败时，阻断向下游路由。
