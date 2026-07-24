# Tool Dispatch / 工具分派 Observability Metrics / 可观测性指标

Cell / 交织点: action-routing / 行动 x 路由
Capability / 能力: Action / 行动
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [action-routing.md](action-routing.md)
Execution Reference / 执行参考: [Governed Tool Dispatch Execution / 受治理工具调度执行](../../tool-dispatch-execution.md)
Projection Runtime / 投影运行时: [`tool_dispatch_projection.py`](../../../runtime/tool_dispatch_projection.py)
Metric Registry / 指标注册表: [`metric_registry.json`](../../../runtime/metric_registry.json)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Tool Dispatch / 工具分派 improves the workflow after selection or application. / 使用以下指标观察 Tool Dispatch / 工具分派 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `dispatch_admission_coverage` measures execution starts backed by a valid admission envelope; `state_evidence_coverage` measures writes with current resource evidence; sampled `dispatch_accuracy`, `bounce_back_rate`, and `default_path_share` remain useful catalog diagnostics. / `dispatch_admission_coverage` 衡量具有有效准入信封的执行开始；`state_evidence_coverage` 衡量具有当前资源证据的写动作；抽样 `dispatch_accuracy`、`bounce_back_rate` 与 `default_path_share` 继续用于诊断能力目录。
- 时延指标 / Latency Metrics: Measure frontier construction, fourteen-check admission, lease acquisition, execution, result persistence, and reconciliation separately; retain `dispatch_decision_latency`, `misroute_round_trip`, approval wait, and unknown-result reconciliation time. / 分别测量能力前沿构建、十四项准入、租约获取、执行、结果持久化与核验时延；保留 `dispatch_decision_latency`、`misroute_round_trip`、审批等待和结果未知核验时长。
- 成本指标 / Cost Metrics: Track schema/admission CPU, durable-store operations per write, wasted invocation cost from misroutes, reconciliation effort, and catalog maintenance. / 跟踪 schema/准入计算成本、每次写动作的持久存储操作、误分派浪费、核验投入和能力目录维护成本。
- 风险指标 / Risk Metrics: `side_effect_lease_coverage`, `approval_binding_coverage`, `frontier_escape_rate`, `result_unknown_rate`, and `duplicate_side_effect_rate` directly observe the write-safety boundary. Also retain `wrong_tool_incidents`, `schema_reject_rate`, unclassified side effects, and out-of-sandbox execution. / `side_effect_lease_coverage`、`approval_binding_coverage`、`frontier_escape_rate`、`result_unknown_rate` 与 `duplicate_side_effect_rate` 直接观测写安全边界；同时保留错误工具事件、schema 拒绝率、未分类副作用与沙箱外执行。
- Trace 指标 / Trace Metrics: `dispatch_record_completeness` is computed only from a complete dispatch inventory; preserve dispatch, permit, lease, start, result, and side-effect bindings, ordered admission evidence, sequence gaps, orphan records, and projector anomalies. / `dispatch_record_completeness` 仅基于完整调度清单计算；保留调度、许可、租约、开始、结果与副作用绑定、有序准入证据、序列缺口、孤儿记录和投影器异常。

### Registered Diagnostic Metrics / 已注册诊断指标

| Metric / 指标 | Numerator / 分子 | Denominator / 分母 | Interpretation / 含义 |
| --- | --- | --- | --- |
| `dispatch_admission_coverage` | starts with valid admission / 具有有效准入的开始 | execution starts / 执行开始 | Execution without admission is an integrity incident. / 无准入执行属于完整性事件。 |
| `side_effect_lease_coverage` | write starts with valid lease / 具有有效租约的写开始 | side-effecting starts / 副作用执行开始 | Must be complete before production writes. / 生产写动作必须完整覆盖。 |
| `state_evidence_coverage` | writes with current evidence / 具有当前证据的写 | writes requiring evidence / 需要证据的写 | Detects stale-state execution. / 发现陈旧状态执行。 |
| `approval_binding_coverage` | starts with content-bound approval / 具有内容绑定审批的开始 | approval-required starts / 需审批执行开始 | Approval must bind parameters and resource versions. / 审批必须绑定参数与资源版本。 |
| `frontier_escape_rate` | starts outside frontier / 能力前沿外开始 | execution starts / 执行开始 | Any non-zero value is a hard anomaly. / 任意非零值都是硬异常。 |
| `dispatch_record_completeness` | complete records / 完整记录 | dispatch records / 调度记录 | Incomplete inventory blocks trustworthy ratios. / 清单不完整时比例不可信。 |
| `result_unknown_rate` | unknown results / 结果未知 | executed results / 已执行结果 | Requires reconciliation, never direct retry. / 必须核验，禁止直接重试。 |
| `duplicate_side_effect_rate` | duplicate effects / 重复副作用 | confirmed side effects / 已确认副作用 | Indicates idempotency failure. / 表明幂等失效。 |

These metrics are diagnostic and non-gating until an accountable owner approves thresholds, observation windows, minimum samples, and promotion evidence. Direct integrity anomalies still fail closed even when aggregate metric gates are not promoted. / 在责任人批准阈值、观测窗口、最小样本和晋升证据前，这些指标均为诊断性、非门控指标；即使聚合指标尚未晋升，直接完整性异常仍默认阻断。

### Default Gate Suggestions / 默认门控建议

- Alert when `bounce_back_rate` or `default_path_share` climbs — both mean the dispatch table no longer matches the real tool inventory and misroutes (`FAIL_0003`) will follow. / 当 `bounce_back_rate` 或 `default_path_share` 上升时告警——两者都说明分派表已与真实工具清单脱节，误分派（`FAIL_0003`）将随之而来。
- Block dispatch when schema validation fails or the target's permission requirement exceeds the caller's scope; return the diff to the caller instead of silently repairing parameters. / schema 校验失败或目标权限要求超出调用方范围时阻断分派；把差异退回调用方而不是静默修补参数。
- Block any execution start without an `allow` envelope and current permit; block any side-effecting start without a valid durable lease. / 无 `allow` 信封和当前许可时阻断执行开始；无有效持久租约时阻断任何副作用执行。
- Block writes without current state evidence or required content-bound approval, and block any selected tool outside the recorded frontier. / 写动作缺少当前状态证据或必需的内容绑定审批时阻断；所选工具不在已记录能力前沿时阻断。
- Route `unknown` to reconciliation and `partial_success` to compensation or human review; never authorize direct retry from those classifications. / 将 `unknown` 路由到核验，将 `partial_success` 路由到补偿或人工复核；不得从这些分类直接授权重试。
- Treat duplicate confirmed side effects, orphan execution events, sequence gaps, and incomplete dispatch records as integrity incidents, not ordinary performance regressions. / 将重复已确认副作用、孤儿执行事件、序列缺口和不完整调度记录视为完整性事件，而非普通性能回退。
