# Guardrail Sandwich / 护栏夹层 Observability Metrics / 可观测性指标

Pattern ID / 模式 ID: `PATTERN_0038`

Version / 版本: `0.2.0`

Status / 状态: Design metrics, not registered gates / 设计层指标，非已注册门控

Cell / 交织点: action-hierarchy / 行动 x 层级
Capability / 能力: Action / 行动
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [action-hierarchy.md](action-hierarchy.md)
Probe profile / 探针档案: [`PROBE_0007` Tool And Action / 工具与动作](../../../runtime/probe_registry.json)

Shared protocol / 共享协议: [`PATTERN_0052` Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)


## Fact And Metric Boundary / 事实与指标边界

Guardrail Sandwich reuses two validated event streams instead of inventing one universal event: the reasoning stream carries task, step, governance, and feedback facts; the tool-execution stream carries dispatch, admission, lease, execution, result, and side-effect facts. Correlate them through stable run, node or step, action, attempt, causation, correlation, idempotency, and parent identities. Schema conformance does not make a model estimate an audit fact. / 护栏夹层复用两条已校验事件流，而不另造一个万能事件：推理流承载任务、步骤、治理和反馈事实；工具执行流承载分派、准入、租约、执行、结果与副作用事实。通过稳定的运行、节点或步骤、行动、尝试、因果、关联、幂等和父级标识把两条流关联起来。符合 Schema 不会把模型估计变成审计事实。

Keep three storage and access classes separate / 分离三类存储与访问等级：

- Audit facts / 审计事实: append-only policy decisions, approvals, permits, execution intents, external-effect evidence, overrides, compensation, and policy changes; never sample them. / 追加写的策略裁定、审批、许可、执行意图、外部效果证据、人工覆盖、补偿和策略变更；绝不采样。
- Telemetry / 遥测: latency, counters, resource use, and bounded diagnostics; sampling and degradation are allowed by policy. / 时延、计数、资源使用与有界诊断；可按策略采样和降级。
- Controlled evidence / 受控证据: exceptional raw artifacts referenced by immutable identity and governed by retention, encryption, access, and deletion policy. / 通过不可变标识引用的例外原始制品，并受留存、加密、访问和删除策略治理。

All Guardrail Sandwich-specific metrics in this file are design-level. They are neither registered in `metric_registry.json` nor eligible as production gates until an owner, versioned formula, data-quality contract, minimum sample, finalized watermark, threshold evidence, and rollback policy are approved. Existing registered Tool Dispatch metrics remain the executable subset. / 本文所有护栏夹层专属指标均处于设计层；在负责人、版本化公式、数据质量契约、最小样本、封窗 watermark、阈值证据和回滚策略获批前，它们既未登记到 `metric_registry.json`，也不能作为生产门控。现有已注册的 Tool Dispatch 指标仍是可执行子集。

## Event And State Model / 事件与状态模型

Current machine events are `capability_frontier_built`, `candidate_selection_completed`, `execution_admission_completed`, `execution_lease_acquired`, `tool_execution_started`, terminal execution-result events, and `side_effect_confirmed`. Proposed Guardrail Sandwich events are `guard_pre_evaluated`, `rehearsal_completed`, `result_quarantined`, `guard_post_evaluated`, `output_released|redacted|blocked`, `effect_reconciliation_completed`, and `compensation_planned|started|completed`. Proposed events stay design-level until versioned Schemas, emitters, projection rules, and failure-path tests exist. / 当前机器事件包括能力前沿建立、候选选择完成、执行准入完成、执行租约取得、工具执行开始、各类执行终态事件和副作用确认。拟议的护栏夹层事件包括前置护栏裁定、预演完成、结果隔离、后置护栏裁定、输出放行/脱敏/阻断、效果核验完成以及补偿计划/开始/完成。拟议事件在具备版本化 Schema、发送器、投影规则与失败路径测试前保持设计层状态。

A POST decision governs returned content or recovery; it does not travel backward in time. Record admission, execution classification, side-effect state, output release, verification, and compensation as independent facts. Therefore `side_effect_state=confirmed` with `output_release=blocked` is valid and must never be counted as an action prevented. / POST 裁定治理返回内容或恢复流程，不能逆转时间；准入、执行分类、副作用状态、输出放行、核验和补偿必须作为独立事实记录。因此，`side_effect_state=confirmed` 与 `output_release=blocked` 同时成立是合法状态，绝不能计为动作已被阻止。

## Observability Metrics / 可观测性指标

Use these metrics only after inventory completeness, fact provenance, label quality, and finalized windows satisfy their declared contracts. / 仅在清单完整性、事实来源、标签质量与封窗条件满足已声明契约后使用这些指标。

| Metric / 指标 | Versioned formula / 版本化公式 | Interpretation and guard / 含义与约束 |
| --- | --- | --- |
| `precheck_block_precision` | `adjudicated_true_unsafe_preblocks / adjudicated_preblocks` | Measures precision, not recall; publish with `adjudication_coverage = adjudicated_preblocks / all_preblocks`. / 衡量精确率而非召回率；必须同时发布裁定覆盖率。 |
| `rehearsal_accuracy` | `matched_effect_items / union(rehearsed_effect_items, verified_actual_effect_items)` | Compute only for actions whose verification window is complete; report missing rehearsal and unverified effects separately. / 仅对核验窗口完整的动作计算；分别报告缺失预演与未核验效果。 |
| `postverify_pass_rate` | `confirmed_postverify_passes / completed_postverify_decisions` | A verification quality signal, not proof that execution was safe or side effects were absent. / 核验质量信号，不证明执行安全或副作用未发生。 |
| `post_output_block_rate` | `post_output_blocks / completed_output_release_decisions` | Measures quarantined output disposition; never call it action-block rate. / 衡量隔离输出处置；不得称为行动阻断率。 |
| `verified_action_success_rate` | `confirmed_intended_effects_without_unapproved_effects / completed_effect_verification_windows` | Requires authoritative effect evidence and complete verification windows. / 需要权威效果证据与完整核验窗口。 |
| `unknown_effect_rate` | `unresolved_unknown_or_partial_effects_at_deadline / actions_requiring_effect_verification_at_deadline` | Bucket by action and sink class; one missing read does not prove absence. / 按行动类与 sink 类分桶；一次未读到不证明未发生。 |
| `layer_verdict_completeness` | `actions_with_all_required_layer_facts / actions_requiring_full_sandwich` | Separate absent, late, invalid, and uncorrelated facts. / 分开统计缺失、迟到、无效与无法关联的事实。 |
| `sandwich_overhead` | `(pre_guard_ms + quarantine_and_post_ms) / controlled_execution_ms` | Publish percentiles and action-class buckets; do not average incompatible actions. / 发布分位数并按行动类分桶；不得混合不相容动作求平均。 |
| `sandwich_bypass_count` | Count of independently evidenced protected effects without a matching admitted execution path. / 有独立证据表明受保护效果发生、却不存在匹配准入执行路径的数量。 | Direct integrity anomaly; reconcile duplicate or late events before alerting. / 直接完整性异常；告警前核验重复或迟到事件。 |

Production block rates cannot estimate security recall because unsafe actions that were never labeled are absent from the denominator. Estimate recall only from controlled red-team cases, replay suites, incident adjudication, or other labeled counterfactual datasets. / 生产阻断率不能估计安全召回率，因为未被标注的不安全行动不在分母中；召回率只能基于受控红队案例、回放套件、事故裁定或其他带标签的反事实数据估计。

Continue to observe quality, latency, cost, risk, and Trace dimensions / 继续观察质量、时延、成本、风险与 Trace 维度：

- 质量指标 / Quality Metrics: pre-check precision and coverage, rehearsal accuracy, post-verification pass, verified action success, and output-release disposition. / 前置检查精确率与覆盖率、预演准确度、后置核验通过率、已核验行动成功率和输出放行处置。
- 时延指标 / Latency Metrics: sandwich overhead percentiles, verification-window age, and bounded compensation latency. / 夹层开销分位数、核验窗口时龄和有界补偿时延。
- 成本指标 / Cost Metrics: rehearsal compute and evidence-retention cost by action and risk class, plus cost per verified action success. / 按行动类与风险等级划分的预演计算和证据留存成本，以及每次已核验成功的成本。
- 风险指标 / Risk Metrics: bypasses, sandbox escapes, rehearsal gaps, unresolved unknown or partial effects, and untested compensation. / 旁路、沙箱逃逸、预演缺口、未解决的未知或部分效果，以及未经测试的补偿。
- Trace 指标 / Trace Metrics: layer-fact completeness, approval-escalation coverage, output-release linkage, reconciliation closure, compensation closure, and probe health. / 分层事实完整率、审批升级覆盖率、输出放行关联、核验闭环、补偿闭环与探针健康。

## Reliability, Sampling, And Backpressure / 可靠性、采样与背压

Use transactional outbox or equivalent write-ahead persistence for audit facts and deliver them at least once with deterministic `event_id` or `event_key` deduplication. Do not claim exactly-once delivery; build idempotent consumers and replayable projections. / 审计事实使用事务 Outbox 或等价预写持久化，采用至少一次投递，并以确定性 `event_id` 或 `event_key` 去重；不得宣称恰好一次投递，应构建幂等消费者与可回放投影。

Prioritize under pressure / 背压时按优先级处置：

1. Admission, permit, execution-intent, effect, override, compensation, and policy-change facts are non-sampled. If required persistence fails before a high-risk side-effect boundary, fail closed; after the boundary, quarantine output and enter reconciliation rather than claiming the action was blocked. / 准入、许可、执行意图、效果、人工覆盖、补偿与策略变更事实不采样。高风险副作用边界前若必需持久化失败则默认阻断；越界后则隔离输出并进入核验，不得声称行动已阻止。
2. Lifecycle correlation and probe-health events are buffered with bounded delay and explicit loss counters. / 生命周期关联与探针自健康事件采用有界延迟缓冲，并显式记录丢失计数。
3. Performance telemetry may be sampled or dropped by declared policy, while recording the sampling policy and effective rate. / 性能遥测可按已声明策略采样或丢弃，同时记录采样策略和实际采样率。

## Privacy And Cardinality / 隐私与基数

Never place credentials, raw parameters, prompts, tool output, free text, URLs, resource IDs, action IDs, user IDs, or other unbounded values in metric labels. Use bounded enums and versioned classes. Events carry hashes and controlled evidence references; for low-entropy or guessable values use a keyed HMAC rather than a bare hash. Apply field-level classification, redaction, access control, retention, and deletion before persistence. / 指标标签不得包含凭据、原始参数、提示词、工具输出、自由文本、URL、资源 ID、行动 ID、用户 ID 或其他无界值；使用有界枚举和版本化类别。事件只携带摘要与受控证据引用；低熵或可猜值使用带密钥 HMAC 而非裸哈希。持久化前执行字段级分类、脱敏、访问控制、留存与删除策略。

## Controlled Feedback / 受控反馈

Observability may create a versioned change proposal, never a self-executing policy mutation. The minimum route is telemetry and adjudicated evidence -> data-quality review -> offline replay and adversarial evaluation -> authorized approval -> shadow evaluation -> bounded canary -> staged rollout -> monitored steady state, with stop criteria and rollback at every deployment stage. Preserve the old policy and attribution window so regressions can be identified and reversed. / 可观测数据只能生成版本化变更建议，不能自行修改策略。最小路径为：遥测与已裁定证据 -> 数据质量检查 -> 离线回放与对抗评估 -> 有权限审批 -> 影子评估 -> 有界金丝雀 -> 分阶段发布 -> 受监控稳态；每个部署阶段都具备停止条件与回滚。保留旧策略和归因窗口，以便识别并回退退化。

### Default Gate Suggestions / 默认门控建议

These are design suggestions, not registered gates. Only direct, independently evidenced integrity anomalies may deterministically invoke an already configured named transition; aggregate metric thresholds remain advisory until formal promotion. / 以下为设计建议，并非已注册门控。只有具备独立直接证据的完整性异常，才能确定性触发已配置的具名转换；聚合指标阈值在正式晋升前保持建议性质。

- Alert and reconcile any `sandwich_bypass_count` above zero for protected action classes. A confirmed bypass means the guarded executor is not the only side-effect path. / 受保护行动类的 `sandwich_bypass_count` 一旦大于零即告警并核验；确认旁路意味着受控执行器并非唯一副作用路径。
- Block before execution when a required rehearsal fails, is skipped, or its bound compensation recipe is unavailable. Escalate through a named, authorized exemption path; never let an aggregate model-derived score create the hard block. / 必需预演失败、被跳过或其绑定补偿配方不可用时，在执行前阻断；通过具名且有权限的豁免路径升级，绝不让模型推导的聚合分数自行创建硬阻断。
