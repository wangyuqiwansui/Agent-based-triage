# Skill Package / 技能包 Observability Metrics / 可观测性指标

Cell / 交织点: reflection-routing / 反思 x 路由
Capability / 能力: Reflection / 反思
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reflection-routing.md](reflection-routing.md)

Shared Probe Contract / 共享探针契约: use [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md), especially `PROBE_0016` through `PROBE_0023`, with the round observation pack defined by the governed [Reflection Execution Flow / 反思执行流程](../../reflection-execution-flow.md). / 使用共享工作流可观测性探针，重点使用 `PROBE_0016` 至 `PROBE_0023`，并采用受治理反思执行流程定义的轮次观察包。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Skill Package / 技能包 improves the workflow after selection or application. / 使用以下指标观察 Skill Package / 技能包 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `routing_accuracy` (sampled audit of verdicts landing on the right path), `skill_reuse_success_rate` (packaged Skills solving their target problem class on invocation), and `triage_default_share` (unclassified verdicts falling to human triage — high values mean the verdict taxonomy lags reality). / `routing_accuracy`（抽样审计裁定是否落到正确路径）、`skill_reuse_success_rate`（封装技能被调用时解决目标问题类的比例）、`triage_default_share`（落入人工分诊的未分类裁定占比——过高说明裁定分类法落后于现实）。
- 时延指标 / Latency Metrics: `routing_decision_latency` (verdict to dispatched route), rework and escalation queue wait per route, and time-to-skill (recurrence threshold hit to packaged Skill shipped). / `routing_decision_latency`（裁定到路径派发的耗时）、各路径的返工与升级排队等待、技能化周期（达到复现阈值到技能发布的时间）。
- 成本指标 / Cost Metrics: repeated-solution cost avoided per packaged Skill, misroute rework cost (release-ready work sent to rework and vice versa), and routing-table maintenance effort per taxonomy change. / 每个封装技能避免的重复求解成本、误路由返工成本（可发布工作被送返工及其反向）、每次分类法变更的路由表维护投入。
- 风险指标 / Risk Metrics: `silent_absorption_count` (escalation-worthy findings routed to rework instead of `GOV_0001` approval), `premature_skillization_count` (Skills shipped below the recurrence threshold or scoring anchor — structural-only caps at 89), and `stale_skill_incidents` (packaged Skills failing on a drifted problem class). / `silent_absorption_count`（本应按 `GOV_0001` 升级却被路由去返工消化的发现数）、`premature_skillization_count`（未达复现阈值或评分锚点即发布的技能数——仅结构完整最高 89 分）、`stale_skill_incidents`（问题类漂移后封装技能失效的事件数）。
- Trace 指标 / Trace Metrics: `routing_record_completeness` (verdict, route, rule hit, outcome recorded per `GOV_0002`), recurrence-trace completeness on skill proposals, and routed-work closure rate per path. / `routing_record_completeness`（裁定、路径、命中规则、结果的记录完整率，按 `GOV_0002`）、技能提议的复现追踪完整率、各路径已路由工作的闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert when `silent_absorption_count` rises above zero or `triage_default_share` climbs — the former means high-risk findings are bypassing `GOV_0001`, the latter means the routing table no longer covers real verdict classes. / `silent_absorption_count` 大于零或 `triage_default_share` 上升即告警——前者说明高风险发现正绕过 `GOV_0001`，后者说明路由表已覆盖不了真实裁定类。
- Block skill packaging when the recurrence trace is incomplete or the packaging evidence scores below the anchor; return the proposal with the gap list instead of shipping a structurally complete but unproven Skill. / 复现追踪不完整或封装证据低于评分锚点时阻断技能封装；把提议连同缺口清单退回，而不是发布一个结构完整却未经验证的技能。
