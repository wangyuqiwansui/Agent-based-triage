# Plan-and-Execute / 计划并执行 Observability Metrics / 可观测性指标

Cell / 交织点: action-orchestration / 行动 x 编排

Pattern ID / 模式 ID: `PATTERN_0037`

Version / 版本: `1.1.0`

Capability / 能力: Action / 行动

Mode / 模式: Orchestration / 编排

Source / 来源: arXiv:2605.13850; expanded with the user-provided Agent Workflow Execution Framework and Workflow Observability Probe Framework. / arXiv:2605.13850；并结合用户提供的《Agent 工作流执行框架》和《工作流可观测性探针框架》扩展。

Design Pattern File / 设计模式文件: [action-orchestration.md](action-orchestration.md)

Cross-cutting protocol / 跨单元协议: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)

## Quick Navigation / 快速导航

- [Observability Metrics / 可观测性指标](#observability-metrics--可观测性指标)
- [Probe Mounts / 探针挂载](#probe-mounts--探针挂载)
- [Implemented Publication-Grade Diagnostics / 已实现可发布诊断](#implemented-publication-grade-diagnostics--已实现可发布诊断)
- [Planned Diagnostics / 规划中诊断](#planned-diagnostics--规划中诊断)
- [Hard Integrity Alerts / 硬完整性告警](#hard-integrity-alerts--硬完整性告警)
- [Deployment Modes / 部署模式](#deployment-modes--部署模式)
- [Acceptance / 验收](#acceptance--验收)

## Observability Metrics / 可观测性指标

Observe Plan-and-Execute as an independent data plane. The executor produces facts; probes correlate and evaluate those facts. Probes may advise or enforce a configured gate, but they do not execute steps, infer private chain-of-thought, or decide business truth. / 将计划并执行作为独立数据面观察。执行器产生事实，探针关联并评价事实。探针可以提出建议或执行已配置门控，但不执行步骤、不推断私密思维过程，也不决定业务真相。

### Observation Questions / 观察问题

1. Is the goal contract complete, current, and bound to every plan revision? / 目标契约是否完整、当前，并绑定到每个计划修订？
2. Did the planner produce a valid, executable DAG with bounded recovery? / 规划器是否生成合法、可执行且恢复有界的 DAG？
3. Did the scheduler run only dependency-complete ready steps? / 调度器是否只运行依赖已完成的就绪步骤？
4. Does every `DONE` record have observable completion evidence? / 每条 `DONE` 记录是否具有可观测完成证据？
5. Did any completed or ambiguous state-changing action execute again? / 是否有已完成或结果不确定的改状态动作再次执行？
6. Can the run resume from a current checkpoint without losing or fabricating business facts? / 运行是否能从当前检查点恢复，且不丢失或编造业务事实？
7. Did replanning remain within the failed-and-affected subgraph? / 重规划是否保持在失败节点及受影响子图内？
8. Were authorization, approval, state evidence, idempotency, and probe health current at protected transitions? / 受保护转换发生时，权限、审批、状态证据、幂等和探针健康是否当前有效？

## Probe Mounts / 探针挂载

Reuse the stable probe IDs from `PATTERN_0052`; do not create a second incompatible event plane. / 复用 `PATTERN_0052` 的稳定探针 ID；不要创建第二套不兼容事件面。

| Plan-and-Execute concern / 计划并执行关注点 | Required probes / 必需探针 | Required facts / 必需事实 |
| --- | --- | --- |
| Identity and correlation / 身份与关联 | `PROBE_0001`, `PROBE_0015` | Goal, plan, patch, run, step, attempt, action, checkpoint, and parent identities; event sequence and probe health. / 目标、计划、补丁、运行、步骤、尝试、动作、检查点和父级标识；事件序号与探针健康。 |
| Goal and plan contract / 目标与计划契约 | `PROBE_0002`, `PROBE_0003`, `PROBE_0010` | Goal version/hash, plan revision/hash, compiler result, validation failures, route reason, drift and approved revisions. / 目标版本与哈希、计划修订与哈希、编译结果、校验失败、路由原因、漂移及获批修订。 |
| Step scheduling and closure / 步骤调度与闭环 | `PROBE_0004`, `PROBE_0005`, `PROBE_0006` | Dependency snapshot, ready time, start/close time, attempt, output digest, criteria, evidence, and terminal state. / 依赖快照、就绪时间、开始/关闭时间、尝试、输出摘要、判据、证据和终态。 |
| Tool and side effects / 工具与副作用 | `PROBE_0007` | Capability frontier, admission, live authority, state evidence, idempotency claim, request/result digest, receipt, certainty, retry, compensation. / 能力前沿、准入、实时权限、状态证据、幂等领取、请求/结果摘要、回执、确定性、重试、补偿。 |
| Recovery and patching / 恢复与补丁 | `PROBE_0005`, `PROBE_0007`, `PROBE_0010`, `PROBE_0012` | Failure roots, exact affected set, protected `DONE` set, patch revision, blast radius, checkpoint binding, unknown verification, stop/escalation. / 失败根、精确影响集、受保护 `DONE` 集、补丁修订、影响范围、检查点绑定、未知核验、停止/升级。 |
| Validation and completion / 验证与完成 | `PROBE_0011`, `PROBE_0012`, `PROBE_0013` | Mandatory validators, completion criteria, final evidence, terminal reason, real outcome and rework. / 必选验证器、完成判据、最终证据、终态原因、真实结果和返工。 |
| Governance and privacy / 治理与隐私 | `PROBE_0014`, `PROBE_0015` | Approval and authority bindings, protected transition, exemption, redaction, retention, probe loss or outage. / 审批与权限绑定、受保护转换、豁免、脱敏、保留、探针丢失或故障。 |

## Required Event Bindings / 必需事件绑定

Every applicable event carries stable `task_id`, `run_id`, `plan_id`, `plan_revision`, `plan_hash`, `goal_id`, `goal_version`, `goal_hash`, `step_id`, `attempt_id`, `event_id`, `parent_event_id`, `sequence`, and `occurred_at`. State-changing actions additionally carry `tool_call_id`, `idempotency_key`, `request_digest`, authorization and approval bindings, state-evidence binding, provider reference, result digest, and result certainty. / 每个适用事件携带稳定任务、运行、计划、计划修订、计划哈希、目标、目标版本、目标哈希、步骤、尝试、事件、父事件、序号和发生时间。改状态动作还携带工具调用、幂等键、请求摘要、授权与审批绑定、状态证据绑定、提供方引用、结果摘要和结果确定性。

Use [`plan_execution_events.py`](../../../runtime/plan_execution_events.py) to enforce the standard dual-contract adapter. It projects plan lifecycle, step start/closure, UNKNOWN reconciliation, patch recovery, and terminal completion into schema-valid `reasoning-event` records with field provenance. It validates and returns Tool Dispatch's original `tool-execution-event` records for state-changing actions. Shared reasoning `action_dispatched` and `action_observed` are read-only by contract, so never mislabel a write merely to force it into that stream. Correlate the two streams by run, step/node, attempt, action, plan, and goal bindings. / 使用 `plan_execution_events.py` 执行标准双契约适配。它把计划生命周期、步骤开始/关闭、UNKNOWN 对账、补丁恢复和终态完成投影为符合 Schema 且带字段来源的 `reasoning-event` 记录；对于改状态动作，则校验并原样返回工具分派的 `tool-execution-event` 记录。共享推理 `action_dispatched` 与 `action_observed` 按契约只读，因此绝不得为了强行进入该事件流而把写动作错误标记为只读。通过运行、步骤/节点、尝试、动作、计划和目标绑定关联两条事件流。

Persisted internal plan events remain a recovery log and are not themselves the public probe contract. The adapter is idempotent, emits stable event identities, and reports unmapped internal event types instead of silently fabricating a normative payload. / 已持久化内部计划事件是恢复日志，并非公共探针契约本身。适配器具有幂等稳定事件身份；遇到未映射内部事件类型时会明确报告，而不是静默伪造规范载荷。

Missing is not zero. A missing checkpoint, absent provider response, or broken event link remains `missing` or `unknown`; it must not become failed, successful, or a numeric zero for aggregation. / 缺失不等于零。缺失检查点、无提供方响应或事件链断裂保持为 `missing` 或 `unknown`；不得为了聚合而变成失败、成功或数值零。

## Implemented Publication-Grade Diagnostics / 已实现可发布诊断

Use only the registered formulas in [`metric_registry.json`](../../../runtime/metric_registry.json), calculate them through [`reasoning_metrics.py`](../../../runtime/reasoning_metrics.py), and publish them only through a complete metric envelope. / 只使用指标注册表中的已注册公式，通过 `reasoning_metrics.py` 计算，并且只通过完整指标信封发布。

| Metric / 指标 | Interpretation / 解释 | Required inventory / 所需清单 |
| --- | --- | --- |
| `plan_compile_success_rate` | Valid sealed plan compilations divided by compilation attempts. / 合法封存计划编译数除以编译尝试数。 | Complete compiler-attempt inventory with failure reasons. / 完整编译尝试清单及失败原因。 |
| `plan_drift_rate` | Inspected runs whose executing plan diverged from the sealed plan or approved patch chain. / 已检查运行中，执行计划偏离封存计划或获批补丁链的比例。 | Plan/patch revision chain and executed-step bindings. / 计划/补丁修订链及已执行步骤绑定。 |
| `eligible_step_closure_rate` | Eligible started steps that reached an explicit terminal record. / 符合条件的已开始步骤中到达显式终态记录的比例。 | Expected step inventory plus start/close events. / 预期步骤清单及开始/关闭事件。 |
| `closed_step_record_completeness` | Closed steps with complete action, observation, decision, time, state, and evidence fields. / 已关闭步骤中动作、观察、决定、时间、状态和证据字段完整的比例。 | Complete closed-step records. / 完整已关闭步骤记录。 |
| `event_chain_completeness` | Expected runs whose event chains are fully linkable. / 预期运行中事件链可完整关联的比例。 | Versioned expected-run and event manifest. / 版本化预期运行与事件清单。 |
| `validation_coverage` | Runs executing all mandatory validators divided by runs requiring validation. / 需要验证的运行中执行全部必选验证器的比例。 | Goal/plan validator declarations and results. / 目标/计划验证器声明及结果。 |
| `dispatch_admission_coverage` | Execution starts with valid current admission divided by all execution starts. / 全部执行启动中具备合法当前准入的比例。 | Full dispatch projection. / 完整分派投影。 |
| `side_effect_lease_coverage` | State-changing starts with valid durable execution lease divided by state-changing starts. / 改状态启动中具备合法持久执行租约的比例。 | Full side-effect start and lease inventory. / 完整副作用启动与租约清单。 |
| `state_evidence_coverage` | Writes with current state-evidence binding divided by writes requiring it. / 需要状态证据的写动作中具备当前状态证据绑定的比例。 | Write inventory and state-evidence bindings. / 写动作清单与状态证据绑定。 |
| `approval_binding_coverage` | Approval-required starts carrying current approval binding divided by all approval-required starts. / 需审批启动中携带当前审批绑定的比例。 | Approval-required action inventory. / 需审批动作清单。 |
| `result_unknown_rate` | Executed results classified `unknown` divided by executed results. / 已执行结果中被分类为未知的比例。 | Complete tool-result inventory. / 完整工具结果清单。 |
| `duplicate_side_effect_rate` | Confirmed duplicate side effects divided by confirmed side-effect results. / 已确认副作用结果中重复副作用的比例。 | Provider-backed side-effect confirmations. / 提供方支持的副作用确认。 |
| `probe_coverage` | Required Plan-and-Execute stages with healthy required probes divided by required stages. / 计划并执行必需阶段中具备健康必需探针的比例。 | Versioned probe dependency resolution and health. / 版本化探针依赖解析与健康状态。 |

These metrics remain diagnostic unless the registry marks them `gate_eligible` and an accountable owner approves threshold, minimum sample, window, buckets, drift control, and promotion evidence. / 除非注册表将指标标为 `gate_eligible`，且责任人批准阈值、最小样本、窗口、分桶、漂移控制和晋升证据，否则这些指标保持诊断用途。

## Planned Diagnostics / 规划中诊断

The following formulas directly express recovery quality but are not yet registered runtime metrics. Capture their raw facts now; do not publish numeric values, set alerts, or gate transitions until they are added to `metric_registry.json`, implemented, tested, and promoted. / 以下公式直接表达恢复质量，但尚未注册为运行时指标。现在应采集原始事实；在其加入指标注册表、实现、测试并晋升前，不得发布数值、设置告警或门控转换。

```text
plan_validation_failure_rate =
  invalid_plan_compilations / plan_compilation_attempts

plan_patch_blast_radius =
  existing_steps_in_accepted_patch / steps_in_base_plan

completed_action_replay_rate =
  confirmed_DONE_actions_dispatched_again / confirmed_DONE_actions

checkpoint_recovery_success_rate =
  recoveries_reaching_a_valid_next_state / recovery_attempts_with_valid_checkpoint

unknown_state_backlog_seconds =
  sum(seconds from UNKNOWN entry to verified terminal or window end)

ready_queue_wait_ms =
  step_start_time - first_time_all_dependencies_were_DONE

step_retry_rate =
  steps_with_attempt_greater_than_one / started_steps

checkpoint_freshness_seconds =
  checkpoint_created_at - latest_protected_state_change_at
```

Do not derive `completed_action_replay_rate` from duplicate event delivery alone. Require distinct admitted dispatches and provider or business-system evidence. Do not call a restart successful merely because a checkpoint deserialized; require a valid next state and no protected-fact regression. / 不得仅凭重复事件投递推导已完成动作重放率；必须存在不同的已准入分派及提供方或业务系统证据。检查点能反序列化不代表恢复成功；必须进入合法下一状态且受保护事实无回退。

## Metric Families / 指标族

- 质量指标 / Quality Metrics: `plan_compile_success_rate`, `plan_drift_rate`, `eligible_step_closure_rate`, `closed_step_record_completeness`, `validation_coverage`, and observed goal acceptance. / 计划编译成功率、计划漂移率、步骤闭环率、关闭记录完整率、验证覆盖率和观测到的目标验收。
- 时延指标 / Latency Metrics: planning latency, ready-queue wait, critical-path duration, replan turnaround, checkpoint recovery time, and `UNKNOWN` reconciliation duration. / 规划时延、就绪队列等待、关键路径耗时、重规划周转、检查点恢复时间和未知状态核验时长。
- 成本指标 / Cost Metrics: planner/coordinator overhead, retry amplification, discarded affected-subgraph work, compensation spend, and cost per validated completion. / 规划器与协调器开销、重试放大、受影响子图废弃工作、补偿成本和单位验证完成成本。
- 风险指标 / Risk Metrics: `plan_drift_rate`, `result_unknown_rate`, `duplicate_side_effect_rate`, missing approval/state evidence, protected-`DONE` mutation attempts, stale patches, and probe outages. / 计划漂移率、未知结果率、重复副作用率、审批/状态证据缺失、修改受保护 `DONE` 的尝试、陈旧补丁和探针故障。
- Trace 指标 / Trace Metrics: goal/plan/patch binding completeness, event-chain completeness, checkpoint freshness, idempotency lineage, affected-subgraph precision, and external-receipt coverage. / 目标/计划/补丁绑定完整性、事件链完整性、检查点新鲜度、幂等谱系、受影响子图精确度和外部回执覆盖率。

## Hard Integrity Alerts / 硬完整性告警

Raise a critical alert immediately; do not wait for a statistical baseline when / 出现以下情况时立即产生严重告警，不等待统计基线：

- A step starts before all dependencies are `DONE`. / 依赖未全部 `DONE` 时步骤启动。
- A `DONE` step is reset, removed, modified, or dispatched again. / `DONE` 步骤被重置、删除、修改或再次分派。
- A state-changing action starts without durable idempotency, current admission, or required state evidence. / 改状态动作缺少持久幂等、当前准入或必需状态证据仍启动。
- An irreversible action starts without a current approval and authority binding. / 不可逆动作缺少当前审批与权限绑定仍启动。
- An `UNKNOWN` action is directly retried without verification. / `UNKNOWN` 动作未经核验直接重试。
- A patch touches a non-affected or protected step, removes an existing dependency, changes an existing write idempotency identity, or skips a plan revision. / 补丁触碰非受影响或受保护步骤、移除已有依赖、改变已有写动作幂等身份或跳过计划修订。
- A step enters `DONE` without declared completion evidence, or a write enters `DONE` without confirmed external success. / 步骤无声明完成证据进入 `DONE`，或写动作无已确认外部成功进入 `DONE`。
- Final completion occurs while mandatory validation failed, a required step is non-`DONE`, the goal binding drifted, or probe health is unavailable. / 必选验证失败、必需步骤非 `DONE`、目标绑定漂移或探针健康不可用时仍最终完成。
- The plan head advances with a non-contiguous internal event suffix, a stale expected checkpoint hash, or an outbox acknowledgement that has no matching open item. / 计划头在内部事件后缀不连续、预期检查点哈希陈旧，或 Outbox 确认没有匹配开放项时仍被推进。
- A final `run_ended` event exists without a sealed, head-bound workflow execution result whose completion gate passed. / 存在最终 `run_ended` 事件，但没有通过完成闸门且绑定当前头的封存工作流执行结果。

Aggregate zero does not suppress a direct integrity violation. One confirmed duplicate side effect or one protected-`DONE` mutation is actionable even when the denominator is large. / 聚合值为零或很低不能压制直接完整性违规。即使分母很大，一次已确认重复副作用或一次修改受保护 `DONE` 也必须处理。

## Deployment Modes / 部署模式

| Mode / 模式 | Plan-and-Execute behavior / 计划并执行行为 |
| --- | --- |
| sidecar / 旁路 | Reconstruct plan, step, action, checkpoint, and patch timelines without changing control flow. Use for initial integration and history. / 重建计划、步骤、动作、检查点和补丁时间线，不改变控制流；用于初次接入和历史分析。 |
| advisory / 建议 | Return plan gaps, drift, large blast radius, stale checkpoint, retry risk, and instrumentation requests; record the workflow response. / 返回计划缺口、漂移、大影响范围、过期检查点、重试风险和埋点请求；记录工作流响应。 |
| inline / 内联 | Protect irreversible dispatch, `DONE`, retry after uncertainty, patch acceptance, and final completion with deterministic versioned rules. / 使用确定且版本化规则保护不可逆分派、进入 `DONE`、不确定后重试、补丁接受和最终完成。 |
| hybrid / 混合 | Use sidecar performance capture, advisory optimization, and inline integrity gates. Recommended for production. / 组合旁路性能采集、建议式优化和内联完整性门控；推荐用于生产。 |

Probe outage fails closed only for named protected high-risk transitions. Low-risk observation may continue in degraded mode while clearly reporting the blind spot. / 探针故障只对明确命名的受保护高风险转换默认阻断；低风险观测可在降级模式继续，但必须清楚报告盲区。

## Observation Report / 观察报告

Return an answer-first report with / 输出结论先行报告，包含：

1. Goal, plan, and run scope plus exact versions and hashes. / 目标、计划和运行范围及其确切版本与哈希。
2. Correlatable step/action/checkpoint counts and probe-health state. / 可关联步骤、动作、检查点数量及探针健康。
3. Highest-risk integrity finding and direct evidence. / 最高风险完整性发现及直接证据。
4. Plan compile, drift, closure, validation, dispatch, idempotency, unknown-result, duplicate-side-effect, and probe-coverage diagnostics when publishable. / 可发布时提供计划编译、漂移、闭环、验证、分派、幂等、未知结果、重复副作用和探针覆盖诊断。
5. Patch history with exact affected set, blast-radius raw values, protected facts, and acceptance result. / 补丁历史，含精确影响集、影响范围原始值、受保护事实和接受结果。
6. Recovery ledger with checkpoint, interrupted work, unknown reconciliation, and next legal state. / 恢复账，含检查点、中断工作、未知核验和下一合法状态。
7. Missing data, unsupported metrics, alert decisions, owners, and verification tasks. / 缺失数据、不支持指标、告警决定、负责人和验证任务。

## Acceptance / 验收

- Every plan and patch event binds the exact goal and predecessor plan revision. / 每个计划和补丁事件绑定确切目标与前序计划修订。
- Expected step and event inventories make missing records detectable. / 预期步骤与事件清单可检测缺失记录。
- `DONE`, `FAILED`, `UNKNOWN`, `BLOCKED`, and missing data remain distinct. / `DONE`、`FAILED`、`UNKNOWN`、`BLOCKED` 和缺失数据保持区分。
- Every state-changing action has a complete admission-to-result lineage and one durable idempotency identity. / 每个改状态动作具有完整的准入到结果谱系及一个持久幂等身份。
- Recovery proves no protected-fact regression and no silent write replay. / 恢复证明无受保护事实回退且无静默写重放。
- The plan-store health record proves WAL mode, successful integrity check, and a bounded inventory of pending or unknown outbox rows. / 计划存储健康记录证明 WAL 模式、完整性检查成功，并提供有界的待处理或未知 Outbox 清单。
- Every terminal event binds an immutable workflow execution result produced by the completion gate. / 每个终态事件都绑定一个由完成闸门生成的不可变工作流执行结果。
- Patch blast radius is reproducible from the base DAG and failure roots. / 补丁影响范围可从基线 DAG 和失败根重算。
- Published metrics carry exact inputs, exclusions, finalized windows, required buckets, expected manifests, and healthy required probes. / 发布指标携带确切输入、排除项、封窗窗口、必需分桶、预期清单和健康必需探针。
- Hard integrity violations are reported directly and are never averaged away. / 硬完整性违规直接报告，绝不被平均值掩盖。
