# Tool Dispatch / 工具分派 Observability Metrics / 可观测性指标

Cell / 交织点: action-routing / 行动 x 路由
Capability / 能力: Action / 行动
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [action-routing.md](action-routing.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Tool Dispatch / 工具分派 improves the workflow after selection or application. / 使用以下指标观察 Tool Dispatch / 工具分派 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `dispatch_accuracy` (sampled audit of whether the chosen tool could serve the action), `bounce_back_rate` (dispatches rejected by the target tool), and `default_path_share` (unknown action types landing on the safe path — high values mean the table lags reality). / `dispatch_accuracy`（抽样审计所选工具能否承接动作）、`bounce_back_rate`（被目标工具拒收的分派比例）、`default_path_share`（落入默认安全路径的未知动作类型占比——过高说明分派表落后于现实）。
- 时延指标 / Latency Metrics: `dispatch_decision_latency` (classify plus validate time), `misroute_round_trip` (time lost when a bounced action is re-dispatched), and approval-hook wait time for gated actions. / `dispatch_decision_latency`（分类加校验耗时）、`misroute_round_trip`（弹回动作重新分派损失的时间）、需审批动作在审批挂钩处的等待时间。
- 成本指标 / Cost Metrics: `schema_validation_cost` per dispatch, wasted invocation cost from misroutes, and table maintenance effort (entries updated per tool change). / 每次分派的 `schema_validation_cost`（schema 校验成本）、误分派浪费的调用成本、分派表维护投入（每次工具变更需更新的表项数）。
- 风险指标 / Risk Metrics: `wrong_tool_incidents` (`FAIL_0003`), `schema_reject_rate` (parameter hallucinations caught before execution, `FAIL_0004`), `unclassified_side_effect_count` (actions dispatched with an underestimated side-effect class, watch `FAIL_0005`), and out-of-sandbox execution count (violates `GOV_0003`). / `wrong_tool_incidents`（`FAIL_0003` 工具选择错误事件数）、`schema_reject_rate`（执行前被拦截的参数幻觉比例，`FAIL_0004`）、`unclassified_side_effect_count`（副作用等级被低估仍被分派的动作数，对应 `FAIL_0005`）、沙箱外执行数量（违反 `GOV_0003`）。
- Trace 指标 / Trace Metrics: `dispatch_record_completeness` (action, target, rule hit, result recorded per `GOV_0002`), approval-hook event coverage per `GOV_0001`, and rejected-dispatch reason coverage. / `dispatch_record_completeness`（动作、目标、命中规则、结果的记录完整率，按 `GOV_0002`）、审批挂钩事件覆盖率（按 `GOV_0001`）、拒绝分派的原因覆盖率。

### Default Gate Suggestions / 默认门控建议

- Alert when `bounce_back_rate` or `default_path_share` climbs — both mean the dispatch table no longer matches the real tool inventory and misroutes (`FAIL_0003`) will follow. / 当 `bounce_back_rate` 或 `default_path_share` 上升时告警——两者都说明分派表已与真实工具清单脱节，误分派（`FAIL_0003`）将随之而来。
- Block dispatch when schema validation fails or the target's permission requirement exceeds the caller's scope; return the diff to the caller instead of silently repairing parameters. / schema 校验失败或目标权限要求超出调用方范围时阻断分派；把差异退回调用方而不是静默修补参数。
