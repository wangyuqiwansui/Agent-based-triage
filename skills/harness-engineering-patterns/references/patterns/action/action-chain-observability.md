# Prompt Chaining / 提示链 Observability Metrics / 可观测性指标

Cell / 交织点: action-chain / 行动 x 链式
Capability / 能力: Action / 行动
Mode / 模式: Chain / 链式
Pattern ID / 模式 ID: `PATTERN_0035`
Cell ID / 单元 ID: `CELL_ACTION_CHAIN`
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Engineering Extension Basis / 工程扩展依据: “提示链 Workflow 可观测性探针” (user-provided design draft, 2026-08-04, external descriptive evidence rather than runtime proof). / 《提示链 Workflow 可观测性探针》（用户提供的设计草案，2026-08-04，属于外部描述性证据，不等同于运行证明）。

Use this file as the observability source for this 7x6 matrix intersection. Design Pattern File / 设计模式文件: [action-chain.md](action-chain.md). Shared Probe Protocol / 共享探针协议: [workflow-observability-probes.md](../../workflow-observability-probes.md). / 将本文档作为该 7x6 交织点的可观测性来源；设计模式文件见 [action-chain.md](action-chain.md)，共享探针协议见 [workflow-observability-probes.md](../../workflow-observability-probes.md)。

## Quick Navigation / 快速导航

- [Probe Positioning / 探针定位](#probe-positioning--探针定位)
- [Deployment Modes / 部署模式](#deployment-modes--部署模式)
- [Probe Mounts / 探针挂载](#probe-mounts--探针挂载)
- [Trace Contract / Trace 契约](#trace-contract--trace-契约)
- [Registered Diagnostics / 已注册诊断](#registered-diagnostics--已注册诊断)
- [Planned Prompt-Chain Diagnostics / 规划中提示链诊断](#planned-prompt-chain-diagnostics--规划中提示链诊断)
- [Hard Integrity Alerts / 硬完整性告警](#hard-integrity-alerts--硬完整性告警)
- [Optimization Loop / 优化闭环](#optimization-loop--优化闭环)
- [Observation Report / 观察报告](#observation-report--观察报告)
- [Acceptance / 验收](#acceptance--验收)

## Probe Positioning / 探针定位

Workflow observability is not ordinary logging. It is an independently governed runtime component that reconstructs execution, artifact lineage, gate decisions, failure propagation, recovery, cost, and probe health so the workflow can be evaluated and improved. / 工作流可观测性不是普通日志。它是独立治理的运行组件，用于重建执行过程、工件谱系、闸门决定、错误传播、恢复、成本和探针健康，从而评估并优化工作流。

The chain owns how work executes. The probe owns what was observed, where quality degraded, which facts are missing, and which versioned optimization should be proposed. Observation alone does not grant authority to mutate the chain. / 提示链负责“如何执行”；探针负责“观测到了什么、质量在哪里下降、缺失哪些事实、应提出哪项版本化优化”。仅有观察能力不授予修改提示链的权限。

```text
Prompt Chain / 提示链
  -> Probe events / 探针事件
  -> Reconstructed run / 重建运行
  -> Diagnostics and alerts / 诊断与告警
  -> Versioned optimization proposal / 版本化优化建议
  -> Review, test, approve, deploy / 评审、测试、批准、部署
```

## Deployment Modes / 部署模式

| Mode / 模式 | Behavior / 行为 | Appropriate Use / 适用场景 |
| --- | --- | --- |
| `sidecar` / 旁路分析 | Consume copied or streamed events, reconstruct runs, and emit reports without changing control flow. / 消费复制或流式事件，重建运行并输出报告，不改变控制流。 | Existing workflow tests, historical baselines, initial integration. / 现有流程测试、历史基线、初次接入。 |
| `design_assist` / 设计辅助 | Simulate steps, artifacts, gates, failure paths, and expected events before deployment; return design gaps and instrumentation requests. / 部署前模拟步骤、工件、闸门、失败路径和预期事件，返回设计缺口与埋点请求。 | Chain design, contract review, gate tuning. / 链路设计、契约评审、闸门调优。 |
| `inline` / 在线运行 | Evaluate named, deterministic, versioned integrity rules before protected transitions; emit the decision into the same causal trace. / 在受保护转换前评估命名、确定性、版本化的完整性规则，并把决定写入同一因果 Trace。 | Production gates for unsafe handoff, protected action, retry, and completion. / 生产中的不安全交接、受保护动作、重试和完成门控。 |
| `hybrid` / 混合 | Combine sidecar performance capture, design/advisory optimization, and inline integrity protection. / 组合旁路性能采集、设计/建议式优化和内联完整性保护。 | Recommended production posture after staged rollout. / 分阶段上线后的推荐生产形态。 |

Probe outage fails closed only for explicitly named high-risk protected transitions. Low-risk observation may continue in a declared degraded mode, but the blind spot and affected interval must remain visible. / 探针故障只对显式命名的高风险受保护转换默认阻断。低风险观测可在声明的降级模式继续，但必须保留盲区和受影响时间段。

## Probe Mounts / 探针挂载

Resolve the required shared probes from [`probe_dependency_matrix.json`](../../../runtime/probe_dependency_matrix.json). For chain topology, require identity, contract, budget, step closure, evidence, drift, validation, stop/escalation, privacy/governance, and probe self-health; add tool/action and outcome probes when applicable. / 通过 [`probe_dependency_matrix.json`](../../../runtime/probe_dependency_matrix.json) 解析必需共享探针。对链式拓扑，要求身份、契约、预算、步骤闭环、证据、漂移、验证、停止/升级、隐私治理和探针自健康；适用时增加工具/行动与结果回接探针。

| Boundary / 边界 | Shared Probes / 共享探针 | Required Facts / 必需事实 |
| --- | --- | --- |
| Run and chain identity / 运行与链身份 | `PROBE_0001`, `PROBE_0015` | Workflow, chain, run, contract version/hash, expected step/event manifests, sequence head, probe version and health. / 工作流、链、运行、契约版本/哈希、预期步骤/事件清单、序号头、探针版本与健康。 |
| Contract and budget / 契约与预算 | `PROBE_0002`, `PROBE_0004`, `PROBE_0010` | Initial/final contracts, step contract versions, token/time/model/tool budgets, constraint drift, approved revisions. / 初始/最终契约、步骤契约版本、Token/时间/模型/工具预算、约束漂移、获批修订。 |
| Step execution / 步骤执行 | `PROBE_0005` | Step and attempt IDs, declared inputs, start/close time, model or executor version, input/output sizes, status, terminal reason. / 步骤与尝试 ID、声明输入、开始/关闭时间、模型或执行器版本、输入/输出规模、状态、终态原因。 |
| Artifact lineage / 工件谱系 | `PROBE_0006` | Artifact ID/type/schema, digest, producer, parents, sources, trust/sensitivity classes, lifecycle, propagation path. / 工件 ID/类型/Schema、摘要、生产者、父工件、来源、信任/敏感等级、生命周期、传播路径。 |
| Gate evaluation / 闸门评估 | `PROBE_0011` | Gate and rule versions, artifact digest, executed layers and validators, result, failure reason, recovery action. / 闸门与规则版本、工件摘要、已执行层与验证器、结果、失败原因、恢复动作。 |
| Tool or protected action / 工具或受保护动作 | `PROBE_0007`, `PROBE_0014` | Capability frontier, admission, authorization/approval, state evidence, idempotency, request/result digests, receipt, certainty, redaction. / 能力前沿、准入、授权/审批、状态证据、幂等、请求/结果摘要、回执、确定性、脱敏。 |
| Recovery and terminal / 恢复与终态 | `PROBE_0012`, `PROBE_0013` | Prior failure, information-gain class and reference, new attempt, remaining budget, escalation, final acceptance, downstream outcome. / 前次失败、信息增益类别与引用、新尝试、剩余预算、升级、最终验收、下游结果。 |

Emit events at run start/end, step ready/start/close, artifact candidate/validated/registered/rejected/superseded, gate start/decision, recovery proposed/start/end, tool admission/start/result, escalation, and probe-health transitions. / 在运行开始/结束、步骤就绪/开始/关闭、工件候选/已验证/已注册/已拒绝/已取代、闸门开始/决定、恢复提出/开始/结束、工具准入/开始/结果、升级和探针健康转换时发出事件。

## Trace Contract / Trace 契约

Use the shared event protocol for machine events. The following is the Prompt Chaining observation report envelope, not a replacement for the normative event Schema. / 机器事件使用共享事件协议。以下是提示链观察报告信封，不替代规范事件 Schema。

```yaml
prompt_chain_observation:
  schema_version: "1.0.0"
  workflow_id: "WORKFLOW_..."
  chain_id: "CHAIN_..."
  chain_version: "1.0.0"
  run_id: "RUN_..."
  deployment_mode: "sidecar | design_assist | inline | hybrid"
  event_schema_version: "..."
  probe_registry_version: "..."
  metric_registry_version: "..."
  observation_window:
    started_at: "RFC3339 timestamp"
    ended_at: "RFC3339 timestamp"
    finalized: true
  steps:
    - step_id: "STEP_..."
      attempt_id: "ATTEMPT_..."
      status: "..."
      input_artifact_ids: []
      output_artifact_ids: []
      gate_decision_id: "GATE_DECISION_..."
      latency_ms: 0
      model_or_executor_ref: "..."
  artifacts: []
  gates: []
  recoveries: []
  protected_actions: []
  terminal:
    status: "completed | failed | escalated | cancelled"
    final_artifact_id: null
    reason: "..."
  risk_score:
    value: null
    method_version: null
  diagnostics: []
  hard_alerts: []
  optimization_proposals: []
  probe_health: {}
  limitations: []
```

Every event carries stable workflow, chain, run, step, attempt, artifact/gate/action identifiers as applicable; `event_id`, `parent_event_id`, `sequence`, `occurred_at`, producer version, and field provenance. Use digests and resolvable references instead of raw prompt, model reasoning, secrets, or unnecessary sensitive payloads. / 每个事件按适用范围携带稳定的工作流、链、运行、步骤、尝试、工件/闸门/动作标识，以及 `event_id`、`parent_event_id`、`sequence`、`occurred_at`、生产者版本和字段来源。使用摘要与可解析引用替代原始 Prompt、模型推理、密钥或不必要的敏感载荷。

Missing, unknown, not-applicable, observed zero, and computed values remain distinct. A missing gate event is not a failed gate, and a missing defect label is not proof that no error escaped. / 缺失、未知、不适用、观测零值和计算值保持区分。缺失闸门事件不等于闸门失败，缺失缺陷标签也不证明没有错误逃逸。

## Observability Metrics / 可观测性指标

Use registered metrics for publication-grade diagnostics and capture raw facts for planned Prompt Chaining metrics. Never invent a denominator, coerce missing values to zero, or convert a descriptive formula into a gate. / 发布级诊断使用已注册指标；规划中的提示链指标只采集原始事实。不得虚构分母、把缺失强制记零，或把描述性公式直接变成闸门。

## Registered Diagnostics / 已注册诊断

Calculate only metrics present in [`metric_registry.json`](../../../runtime/metric_registry.json) through the governed metrics runtime. Publish them only with a finalized window, exact inputs and exclusions, required buckets, minimum sample, registry version, and healthy required probes. / 仅通过受治理指标运行时计算 [`metric_registry.json`](../../../runtime/metric_registry.json) 中存在的指标。只有具备已封窗窗口、确切输入与排除项、必需分桶、最小样本、注册表版本和健康必需探针时，才能发布。

| Metric / 指标 | Prompt-Chain Interpretation / 提示链解释 |
| --- | --- |
| `contract_completeness` | Runs carrying every required chain, step, artifact, gate, recovery, and terminal contract field. / 具备全部必需链、步骤、工件、闸门、恢复与终态契约字段的运行。 |
| `eligible_step_closure_rate` | Eligible started steps reaching an explicit terminal record. / 符合条件的已启动步骤到达显式终态记录的比例。 |
| `closed_step_record_completeness` | Closed steps with complete action, observation, decision, time, state, and evidence facts. / 已关闭步骤中动作、观察、决定、时间、状态和证据事实完整的比例。 |
| `event_chain_completeness` | Expected runs whose event chains are fully linkable. / 预期运行中事件链可完整关联的比例。 |
| `evidence_traceability` | Referenced evidence with resolvable source version/time and location. / 引用证据具备可解析来源版本/时间与位置的比例。 |
| `validation_coverage` | Runs executing all declared mandatory validators. / 执行全部声明必选验证器的运行比例。 |
| `stop_reason_completeness` | Terminal runs carrying a valid stop or escalation reason. / 终态运行具备合法停止或升级原因的比例。 |
| `tool_success_rate` | Structurally valid successful tool calls divided by applicable calls. / 结构合法且成功的工具调用占适用调用的比例。 |
| `retry_amplification` | Actual attempts including retries divided by deduplicated logical attempts. / 含重试的实际尝试数除以去重逻辑尝试数。 |
| `probe_coverage` | Required chain stages with healthy required probes divided by required stages. / 具备健康必需探针的链式必需阶段占比。 |
| `event_loss_rate`, `duplicate_event_rate`, `parse_failure_rate`, `alert_delivery_rate` | Probe self-health and delivery integrity. / 探针自健康与投递完整性。 |

These metrics remain diagnostic unless the registry marks them `gate_eligible` and an accountable owner approves threshold, minimum sample, window, buckets, drift controls, and promotion evidence. / 除非注册表将指标标为 `gate_eligible`，且责任人批准阈值、最小样本、窗口、分桶、漂移控制和晋升证据，否则这些指标保持诊断用途。

## Planned Prompt-Chain Diagnostics / 规划中提示链诊断

The following formulas capture the supplied engineering model but are not registered runtime metrics. Capture their raw facts now; do not publish official values, set statistical alerts, or gate transitions until each metric is registered, implemented, tested, assigned an owner, and promoted with evidence. / 以下公式承接用户提供的工程模型，但尚未注册为运行时指标。现在只采集原始事实；在指标完成注册、实现、测试、责任人指定和证据晋升前，不得发布官方数值、设置统计告警或用于门控转换。

### Execution Stability / 执行稳定性

```text
chain_segment_success_rate =
  passed_step_attempts / closed_step_attempts

first_pass_chain_success_rate =
  accepted_runs_without_retry_recovery_or_gate_rejection / terminal_eligible_runs
```

Define “eligible,” “closed,” and “accepted” in a versioned scene contract. Keep cancellation, escalation, missing terminal records, and excluded test traffic visible. / 在版本化场景契约中定义“符合条件”“已关闭”和“已验收”。取消、升级、终态记录缺失和排除的测试流量必须保持可见。

### Artifact Quality / 工件质量

```text
artifact_completeness =
  registered_artifacts_with_all_required_contract_fields / registered_artifacts

source_trace_completeness =
  artifacts_with_resolvable_required_source_lineage / artifacts_requiring_source_lineage

schema_drift_rate =
  incompatible_or_undeclared_schema_handoffs / inspected_artifact_handoffs
```

Do not count a field as complete when it is present but empty, unparseable, stale, or bound to a different artifact digest. / 字段虽然存在但为空、不可解析、陈旧或绑定到另一工件摘要时，不得计为完整。

### Gate Quality / 闸门质量

```text
gate_pass_rate =
  pass_decisions / closed_gate_evaluations

error_escape_rate =
  downstream_confirmed_defects_after_prior_gate_pass / prior_gate_passes_with_outcome_labels

false_rejection_rate =
  adjudicated_valid_artifacts_rejected / rejected_artifacts_with_adjudicated_labels
```

`error_escape_rate` and `false_rejection_rate` require independent adjudication or outcome labels; gate self-judgment cannot label its own false pass or false rejection. / `error_escape_rate` 与 `false_rejection_rate` 需要独立裁决或后验标签；闸门不能自行判定自己的误放行或误拒绝。

### Safety / 安全

```text
untrusted_input_propagation_distance =
  distribution(boundaries_crossed_from_untrusted_ingress_to_detection_or_protected_action)

high_risk_action_validation_coverage =
  high_risk_action_starts_with_all_mandatory_validation_and_authorization / high_risk_action_starts

data_contamination_rate =
  adjudicated_validated_artifacts_with_untrusted_content_treated_as_trusted / adjudicated_validated_artifacts
```

Report propagation distance as a distribution by chain version, input trust class, artifact type, and protected-action class. A single direct untrusted-to-action path is a hard integrity violation even when the aggregate is small. / 按链版本、输入信任等级、工件类型和受保护动作类别报告传播距离分布。即使聚合值很小，一条“不可信输入直达动作”路径也属于硬完整性违规。

### Recovery / 恢复

```text
retry_information_gain_rate =
  retries_with_new_evidence_constraint_scope_deterministic_check_or_human_input / retries

automatic_recovery_success_rate =
  automatic_recoveries_reaching_a_valid_next_state / automatic_recovery_attempts

human_intervention_rate =
  eligible_runs_requiring_human_recovery_or_decision / eligible_runs
```

Deserialization or model regeneration alone is not successful recovery. Require a legal next state, no accepted-artifact regression, and no unsafe side-effect replay. / 仅能反序列化或重新生成模型输出不等于恢复成功。必须到达合法下一状态、已接受工件无回退、且不存在不安全副作用重放。

### Cost And Latency / 成本与时延

```text
model_call_amplification =
  actual_model_calls / versioned_baseline_model_calls

context_growth_rate =
  (last_step_context_units - first_step_context_units) / max(first_step_context_units, 1)

chain_latency_distribution =
  distribution(run_terminal_time - run_start_time)

handoff_latency_distribution =
  distribution(next_step_start_time - producer_step_close_time)
```

Version the baseline and keep model, step count, payload class, deployment mode, cache status, and retry class as buckets. Do not sum tokens, time, calls, and currency into one “cost” scalar. / 基线必须版本化，并按模型、步骤数、载荷类别、部署模式、缓存状态和重试类别分桶。不得把 Token、时间、调用次数和货币成本累加成一个“成本”标量。

## Metric Families / 指标族

- 质量指标 / Quality Metrics: `contract_completeness`, `validation_coverage`, `evidence_traceability`, planned `artifact_completeness`, `source_trace_completeness`, `schema_drift_rate`, `error_escape_rate`, and final artifact acceptance. / 契约完整度、验证覆盖、证据可追踪性，以及规划中的工件完整度、来源追踪完整度、Schema 漂移率、错误逃逸率和最终工件验收。
- 时延指标 / Latency Metrics: Per-step execution, gate evaluation, handoff, recovery, protected-action, and end-to-end chain latency distributions. / 单步执行、闸门评估、交接、恢复、受保护动作和端到端链路时延分布。
- 成本指标 / Cost Metrics: Model/tool calls, tokens or context units, retry amplification, validation overhead, avoided full reruns, and cost per validated success. / 模型/工具调用、Token 或上下文单位、重试放大、验证开销、避免的整链重跑和单位验证成功成本。
- 风险指标 / Risk Metrics: Error escape, false rejection, schema drift, untrusted propagation, missing high-risk validation, contamination, unknown side effects, and probe outage. / 错误逃逸、误拒绝、Schema 漂移、不可信输入传播、高风险验证缺失、数据污染、副作用未知和探针故障。
- Trace 指标 / Trace Metrics: Step ledger completeness, artifact-lineage completeness, gate-decision binding, recovery information gain, event-chain completeness, terminal-reason completeness, and probe self-health. / 步骤台账完整度、工件谱系完整度、闸门决定绑定、恢复信息增益、事件链完整度、终态原因完整度和探针自健康。

## Hard Integrity Alerts / 硬完整性告警

Raise a critical alert immediately; do not wait for a statistical baseline when / 出现以下情况时立即产生严重告警，不等待统计基线：

- A step starts before all required input artifacts are registered and gate-passed. / 必需输入工件尚未全部注册并通过闸门时，步骤已经启动。
- A rejected, unknown, schema-incompatible, or digest-mismatched artifact enters a downstream step. / 已拒绝、未知、Schema 不兼容或摘要不匹配的工件进入下游步骤。
- A gate failure is rewritten as pass, or an artifact is registered without the required four-layer decision record. / 闸门失败被改写为通过，或工件在缺少必需四层决定记录时被注册。
- Untrusted content directly selects or parameterizes a protected action without independent validation, dispatch admission, and authorization. / 不可信内容在缺少独立验证、分派准入和授权时直接选择受保护动作或为其提供参数。
- A high-risk action starts without every mandatory validator, current approval/authority binding, or probe health. / 高风险动作在缺少任一必选验证器、当前审批/权限绑定或探针健康时启动。
- An `unknown` side-effect result is directly retried, or one idempotency identity produces multiple confirmed side effects. / `unknown` 副作用结果被直接重试，或同一幂等身份产生多个已确认副作用。
- A retry has no recorded information gain, exceeds its attempt budget, resets a passed step, or overwrites a registered artifact. / 重试没有记录信息增益、超过尝试预算、重置已通过步骤或覆盖已注册工件。
- Final completion occurs while the final gate is non-pass, a required step is non-terminal, a protected action is unresolved, or the terminal reason is missing. / 最终闸门未通过、必需步骤非终态、受保护动作未决或终态原因缺失时仍完成。
- Identity linkage is irrecoverably broken, sensitive data is emitted without required redaction, or private chain-of-thought is captured. / 标识链不可恢复、敏感数据未按要求脱敏输出，或采集了私密思维过程。
- An inline probe outage silently releases a named protected transition. / 内联探针故障却静默放行命名的受保护转换。

Aggregate values never suppress a direct integrity violation. One confirmed escaped high-risk artifact or duplicate side effect remains actionable regardless of the denominator. / 聚合值不能压制直接完整性违规。无论分母多大，一次已确认的高风险工件逃逸或重复副作用都必须处理。

## Default Gate Suggestions / 默认门控建议

- Block continuation on a failed or unknown required gate; legal continuations are only the declared bounded recovery, verification, escalation, cancellation, or failure routes. / 必需闸门失败或未知时阻断继续；合法后续只有已声明的有界恢复、核验、升级、取消或失败路由。
- Fail closed on missing identity, artifact digest, contract/schema version, or authorization binding at a protected transition. / 受保护转换缺少身份、工件摘要、契约/Schema 版本或授权绑定时默认阻断。
- Keep statistical thresholds advisory until an accountable owner approves formula, denominator, exclusions, buckets, minimum sample, sustained window, baseline version, drift control, and promotion evidence. / 在责任人批准公式、分母、排除项、分桶、最小样本、持续窗口、基线版本、漂移控制和晋升证据前，统计阈值保持建议用途。
- Return `insufficient_sample` rather than a trend judgment when the registered minimum sample is not met. / 未达到注册最小样本时返回 `insufficient_sample`，不得强行判断趋势。

## Optimization Loop / 优化闭环

The probe may recommend splitting or merging steps, tightening or relaxing a validator, adding evidence, changing a recovery route, reducing context, or adding instrumentation. Every proposal binds the observed chain version, evidence window, affected steps/gates, expected benefit, risk, owner, verification case, and rollback plan. / 探针可以建议拆分或合并步骤、收紧或放松验证器、补充证据、改变恢复路由、缩减上下文或增加埋点。每条建议都必须绑定已观测链版本、证据窗口、受影响步骤/闸门、预期收益、风险、负责人、验证用例和回滚计划。

Never let the probe silently edit the active chain. Apply an optimization only as a new contract or gate version after review, failure-path testing, and approval; compare the new version against a declared baseline. / 不得让探针静默编辑正在运行的链。优化只有在评审、失败路径测试和批准后，才能以新契约或闸门版本应用；并且必须与声明的基线比较。

## Observation Report / 观察报告

Return an answer-first report with / 输出结论先行报告，包含：

1. Workflow, chain, run, contract, event, probe, and metric versions plus the finalized observation window. / 工作流、链、运行、契约、事件、探针和指标版本，以及已封窗观察窗口。
2. Expected versus correlatable steps, artifacts, gates, recoveries, protected actions, and events; include probe-health state. / 预期与可关联的步骤、工件、闸门、恢复、受保护动作和事件，并包含探针健康状态。
3. Highest-risk integrity finding, exact evidence, affected artifacts/actions, and legal containment. / 最高风险完整性发现、确切证据、受影响工件/动作和合法止损措施。
4. Registered diagnostics that are actually publishable, including raw numerator, denominator, exclusions, buckets, and confidence. / 实际可发布的已注册诊断，包括原始分子、分母、排除项、分桶和置信度。
5. Planned metric raw facts without fabricated official values or thresholds. / 规划中指标的原始事实，不伪造官方数值或阈值。
6. Failure-propagation path, gate decision, recovery information gain, remaining budget, and terminal result. / 错误传播路径、闸门决定、恢复信息增益、剩余预算和终态结果。
7. One highest-priority versioned optimization proposal with owner, test, risk, and rollback. / 一条最高优先级版本化优化建议，含负责人、测试、风险和回滚。
8. Missing data, unsupported conclusions, degraded intervals, and follow-up verification tasks. / 缺失数据、不受支持结论、降级时间段和后续验证任务。

## Acceptance / 验收

- Stable identities and causal parents connect run, step, attempt, artifact, gate, recovery, action, and terminal events. / 稳定身份和因果父事件连接运行、步骤、尝试、工件、闸门、恢复、动作和终态事件。
- Expected manifests make missing steps, artifacts, gates, and events detectable. / 预期清单使缺失步骤、工件、闸门和事件可检测。
- Artifact lineage preserves type, schema, digest, source, producer, parents, trust, sensitivity, lifecycle, and propagation path. / 工件谱系保留类型、Schema、摘要、来源、生产者、父工件、信任、敏感等级、生命周期和传播路径。
- Gate traces preserve rule versions, executed layers, validator evidence, decisions, reasons, and recovery routes. / 闸门 Trace 保留规则版本、已执行层、验证器证据、决定、原因和恢复路由。
- Recovery traces prove new information, positive remaining budget, legal next state, and no accepted-artifact or side-effect regression. / 恢复 Trace 证明新信息、剩余正数预算、合法下一状态，且已接受工件或副作用无回退。
- Missing, unknown, not-applicable, observed zero, computed, rejected, and failed remain distinct. / 缺失、未知、不适用、观测零值、计算值、拒绝和失败保持区分。
- Published metrics use registered formulas, finalized windows, exact inputs/exclusions, required buckets, minimum samples, and healthy required probes. / 已发布指标使用已注册公式、已封窗窗口、确切输入/排除项、必需分桶、最小样本和健康必需探针。
- Hard integrity violations are direct alerts and are never averaged away. / 硬完整性违规直接告警，绝不被平均值掩盖。
- Probe events contain no private chain-of-thought, secrets, or unnecessary raw sensitive payloads. / 探针事件不包含私密思维过程、密钥或不必要的原始敏感载荷。
- Every optimization proposal is evidence-bound, versioned, owned, testable, reversible where applicable, and separate from the active chain. / 每条优化建议都绑定证据、具备版本和负责人、可测试、适用时可回滚，并与活动链分离。
