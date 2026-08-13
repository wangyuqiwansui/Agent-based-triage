# Workflow Observability Probes / 工作流可观测性探针

Pattern ID / 模式 ID: `PATTERN_0052`

Version / 版本: `0.7.0`

Status / 状态: Draft / 草案
Related patterns / 关联模式: `PATTERN_0051` Reasoning Execution Flow / 推理执行流程; `PATTERN_0036` Tool Dispatch / 工具分派; `PATTERN_0038` Guardrail Sandwich / 护栏夹层

This reference turns workflow observability into a deployable probe suite that can reconstruct execution, detect gaps, preserve data provenance, compute reproducible metrics, and return authorized advice or blocks. It complements [Reasoning Execution Flow / 推理执行流程](reasoning-execution-flow.md) and can also inspect unrelated workflows in standalone mode. / 本参考将工作流可观测性实现为一套可部署探针，用于重建执行链、发现缺口、保留数据来源、计算可复现指标，并返回有权限的建议或阻断。它与[推理执行流程](reasoning-execution-flow.md)互补，也可独立检查其他工作流。

Compatibility note / 兼容说明: the source draft used `PATTERN_0002`, which is already the stable registry ID for Context Assembly / 上下文装配模式. Preserve that historical ID and register this protocol as `PATTERN_0052`; do not rewrite existing registry or Trace history. / 来源草案使用了 `PATTERN_0002`，但该稳定 ID 已分配给上下文装配模式。应保留历史 ID，并将本协议登记为 `PATTERN_0052`；不得改写既有注册表或 Trace 历史。

## Quick Navigation / 快速导航

- [Scope And Safety Boundary / 范围与安全边界](#scope-and-safety-boundary--范围与安全边界)
- [Cognition And Topology Mounts / 认知与拓扑挂载](#cognition-and-topology-mounts--认知与拓扑挂载)
- [Deployment And Probe Contract / 部署与探针契约](#deployment-and-probe-contract--部署与探针契约)
- [Identity, Event, And Provenance / 标识事件与来源](#identity-event-and-provenance--标识事件与来源)
- [Guardrail Sandwich Action Profile / 护栏夹层行动档案](#guardrail-sandwich-action-profile--护栏夹层行动档案)
- [Probe Catalog / 探针目录](#probe-catalog--探针目录)
- [Standalone And Interactive Operation / 独立与交互运行](#standalone-and-interactive-operation--独立与交互运行)
- [Metrics And Alerts / 指标与告警](#metrics-and-alerts--指标与告警)
- [Data Completion And Scenario Packs / 数据补全与场景包](#data-completion-and-scenario-packs--数据补全与场景包)
- [Report And Acceptance / 报告与验收](#report-and-acceptance--报告与验收)

## Scope And Safety Boundary / 范围与安全边界

Deploy probes at intake, routing, contract creation, step execution, evidence use, tool calls, branch creation, iteration, validation, terminal transition, and outcome return. Use them with agent workflows, retrieval, analysis, approval, batch processing, multi-agent systems, code repair, and legacy log reconstruction. / 在入口、路由、契约建立、步骤执行、证据使用、工具调用、分支创建、迭代、验证、终态转换和结果回接处部署探针。适用于智能体、检索、分析、审批、批处理、多智能体、代码修复及遗留日志重建流程。

Enforce these invariants / 强制以下不变量:

1. Establish stable correlation before aggregation. / 先建立稳定关联，再做聚合。
2. Keep raw observations, system reports, deterministic calculations, rule derivations, human confirmations, model estimates, and missing values distinct. / 区分原始观测、系统上报、确定性计算、规则推导、人工确认、模型估计和缺失。
3. Missing does not mean zero, false, success, or passed. / 缺失不等于零、否、成功或通过。
4. Complete only data with a traceable method; never invent evidence, approval, or validation results. / 仅用可追踪方法补全数据；不得编造证据、审批或验证结果。
5. Version metric definitions and bucket by scene, risk, mode, model, tool, validator, evidence grade, human involvement, node, and time window. / 指标口径版本化，并按场景、风险、模式、模型、工具、验证器、证据等级、人工参与、节点和时间窗口分桶。
6. Capture externally verifiable events, never private chain-of-thought. / 采集外部可核验事件，不采集私密思维过程。
7. Observe probe coverage, loss, duplication, parsing, latency, persistence, metric calculation, and alert delivery. / 监控探针覆盖、丢失、重复、解析、延迟、持久化、指标计算和告警送达。
8. Probes report and enforce configured governance gates; they do not decide business truth. / 探针报告并执行已配置治理门槛，不决定业务事实。

## Cognition And Topology Mounts / 认知与拓扑挂载

The probe suite observes through perception, retains event chains and baselines through memory, diagnoses drift and no-progress through reflection, enforces privacy and protected transitions through governance, and uses reasoning only for labeled suggestions or estimates. / 探针套件通过感知采集，通过记忆保留事件链与基线，通过反思诊断漂移与无进展，通过治理执行隐私与受保护转换，只将推理用于已标注的建议或估计。

| Probe responsibility / 探针职责 | Matrix mount / 矩阵挂载 |
| --- | --- |
| Coordinate event capture across workflow stages. / 跨工作流阶段协调事件采集。 | `COG_PERCEPTION__TOP_ORCHESTRATION` |
| Preserve an ordered, correlatable event ledger. / 保留有序且可关联的事件账本。 | `COG_MEMORY__TOP_CHAIN` |
| Feed observed gaps, drift, validation, and no-progress signals back into execution. / 将缺口、漂移、验证和无进展信号反馈给执行。 | `COG_REFLECTION__TOP_LOOP` |
| Coordinate evidence, metrics, alerts, privacy, and protected transitions. / 协调证据、指标、告警、隐私和受保护转换。 | `COG_GOVERNANCE__TOP_ORCHESTRATION` |
| Propagate identity, authority, retention, and accountability across parent-child work. / 在父子工作间传播标识、权限、保留与问责。 | `COG_GOVERNANCE__TOP_HIERARCHY` |

Parallel and iterative probes observe their matching runtime topology, but the suite remains a cross-cutting protocol rather than a replacement for cell-specific pattern identity. / 并行与迭代探针观察其对应运行拓扑，但整套探针仍是跨单元协议，不替代单元特定模式身份。

## Deployment And Probe Contract / 部署与探针契约

### Deployment modes / 部署模式

When route history uses [`workflow_route_sqlite_ledger.py`](../runtime/workflow_route_sqlite_ledger.py), treat its stream identity, immutable switch cap, Schema version, WAL mode, commit/replay failures, migration results, `quick_check`, foreign-key violations, and record backlog as `PROBE_0001`, `PROBE_0003`, `PROBE_0014`, and `PROBE_0015` inputs. A healthy SQLite file proves storage mechanics only; it does not prove route correctness, action authorization, distributed failover, backup recovery, or trustworthy outcome linkage. / 路由历史使用 SQLite 路由账本时，将流身份、不可变换路上限、Schema 版本、WAL 模式、提交/重放失败、迁移结果、`quick_check`、外键违规和记录积压作为任务身份、路由决策、隐私治理与探针自健康探针的输入。SQLite 文件健康只证明存储机制，不证明路由正确、行动授权、分布式故障切换、备份恢复或可信后验关联。

When governed action dispatch uses [`tool_dispatch.py`](../runtime/tool_dispatch.py), [`tool_dispatch_sqlite_store.py`](../runtime/tool_dispatch_sqlite_store.py), and [`tool_dispatch_projection.py`](../runtime/tool_dispatch_projection.py), capture the sealed capability frontier, selected-tool binding, fourteen ordered admission checks, execution permit, durable idempotency lease, result certainty, side-effect confirmation, and projection anomalies through `PROBE_0007`. Treat an expired write lease as result-unknown and reconcile it before retry. SQLite health proves local storage mechanics only; horizontal execution still requires a deployment-owned network store with equivalent serialization, fencing, immutable-success reuse, backup, and fail-closed behavior. / 受治理行动调度使用 [`tool_dispatch.py`](../runtime/tool_dispatch.py)、[`tool_dispatch_sqlite_store.py`](../runtime/tool_dispatch_sqlite_store.py) 与 [`tool_dispatch_projection.py`](../runtime/tool_dispatch_projection.py) 时，通过 `PROBE_0007` 采集封存能力前沿、所选工具绑定、十四项有序准入检查、执行许可、持久幂等租约、结果确定性、副作用确认和投影异常。写租约过期必须视为结果未知，并在重试前核验。SQLite 健康只证明本地存储机械能力；水平执行仍需部署方提供具备等价串行化、栅栏、成功结果不可变复用、备份与默认阻断语义的网络存储。

| Mode / 模式 | Behavior / 行为 | Use / 用途 |
| --- | --- | --- |
| sidecar / 旁路观测 | Read logs or events without changing control flow. / 读取日志或事件，不改变控制流。 | Initial integration, history, and low-risk observation. / 初次接入、历史分析与低风险观测。 |
| advisory / 建议反馈 | Return warnings and data requests; the workflow records accept, ignore, or alternative action. / 返回预警和补数请求；主流程记录采纳、忽略或替代动作。 | Routing, budget, drift, and quality guidance. / 路由、预算、漂移与质量建议。 |
| inline / 内联阻断 | Guard a protected transition with deterministic, auditable, configurable rules. / 用确定、可审计、可配置规则保护状态转换。 | High-risk completion, approval, validation, evidence, and irreversible action. / 高风险完成、审批、验证、证据和不可逆动作。 |
| hybrid / 混合 | Combine sidecar performance capture, advisory diagnosis, and inline governance. / 组合旁路性能采集、建议诊断和内联治理。 | Most production workflows. / 多数生产工作流。 |

An inline block must have rule identity, rule version, evidence, target transition, owner, and authorized exemption path; model judgment alone cannot create a hard block. / 内联阻断必须包含规则标识、规则版本、证据、受保护转换、负责人和有权限的豁免路径；不得只凭模型判断创建硬阻断。

### Probe definition / 探针定义

```yaml
probe:
  probe_id: PROBE_XXXX
  name: "English / 中文"
  version: 1
  trigger_points: []
  capture_fields: []
  capture_method: inject | wrap | subscribe | query | correlate | calculate | request
  source_types: []
  completeness_rules: []
  quality_rules: []
  outputs: []
  disposition: record | advise | block
  scenes: []
  owner: null
```

## Identity, Event, And Provenance / 标识事件与来源

Reuse `task_id`, `run_id`, `step_id`, `event_id`, `parent_event_id`, `candidate_path_id`, `evidence_id`, and `verification_id` from the reasoning protocol. Add `tool_call_id` for request-response-retry-cost linkage and `human_work_id` for escalation-approval-outcome linkage. / 复用推理协议中的任务、运行、步骤、事件、父事件、候选路径、证据和验证标识；增加 `tool_call_id` 关联请求、响应、重试和成本，增加 `human_work_id` 关联升级、审批和结果。

Also propagate `attempt_id`, `idempotency_key`, `causation_id`, `transition_id`, and a monotonic per-run `sequence`. The normative event contract is [Reasoning Event Schema](../schemas/reasoning-event.schema.json); the YAML below is a compact explanatory view. / 同时传播 `attempt_id`、`idempotency_key`、`causation_id`、`transition_id` 和单次运行内单调递增的 `sequence`。规范事件契约见[推理事件 Schema](../schemas/reasoning-event.schema.json)；以下 YAML 仅为紧凑解释视图。

Correlation precedence is explicit identity, propagated parent context, deterministic key, then time-window or attribute inference. Mark inferred linkage with method and confidence; never overwrite explicit linkage. / 关联优先级为显式标识、父子上下文传播、确定性键、时间窗或属性推断。推断关联必须标记方法和可信度，且不得覆盖显式关联。

### Unified event / 统一事件

```yaml
schema_version: 1.0.0
event_version: 1.0.0
event_id: EVENT_XXXX
event_type: state_transitioned
event_processing_status: accepted
workflow_state: normalized
previous_state: received
next_state: normalized
transition_id: TRANSITION_XXXX
task_id: TASK_XXXX
run_id: RUN_XXXX
step_id: null
attempt_id: ATTEMPT_XXXX
sequence: 1
idempotency_key: IDEMPOTENCY_XXXX
causation_id: COMMAND_XXXX
parent_event_id: EVENT_PARENT_XXXX
candidate_path_id: null
tool_call_id: null
human_work_id: null
occurred_at: "2026-07-15T09:00:00Z"
emitted_at: "2026-07-15T09:00:00Z"
received_at: "2026-07-15T09:00:01Z"
scene_id: SCENE_XXXX
risk_level: medium
reasoning_depth: deliberative
execution_mode: chain
primary_topology: chain
supporting_topologies: [orchestration]
snapshot_versions:
  goal: 1
  constraints: 1
  verified_facts: 1
payload:
  kind: state_transition
  data:
    from_state: received
    to_state: normalized
    reason_code: input_normalized
resources:
  model_calls: {value_state: observed_zero, value: 0}
  tool_calls: {value_state: observed_zero, value: 0}
  reasoning_tokens: {value_state: missing, value: null}
  input_tokens: {value_state: missing, value: null}
  output_tokens: {value_state: missing, value: null}
  cost_units: {value_state: missing, value: null}
  latency_ms: {value_state: missing, value: null}
stop_reason: null
escalation_reason: null
field_provenance:
  payload.data.to_state:
    value_state: observed
    source_type: system_report
    source_id: reasoning-runtime
    source_version: 1.0.0
    valid_at: "2026-07-15T09:00:00Z"
    captured_at: "2026-07-15T09:00:00Z"
    method: deterministic_runtime_event
    confidence: 1.0
privacy_class: internal
redaction_state: not_required
```

The Schema fixes every `event_type` to exactly one payload kind: lifecycle, state transition, route, step, evidence, tool, candidate, iteration, mode, validation, budget, human work, outcome, governance, feedback, or probe health. Do not omit schema and event versions, identity, sequence, idempotency, event-processing status, workflow state, occurrence time, payload kind, or field-level provenance for required payload values. Require parent identity for multi-node flows. `event_processing_status` never substitutes for `workflow_state`; `observed_zero` never substitutes for `missing`, `unknown`, or `not_applicable`. / Schema 将每个 `event_type` 固定映射到唯一载荷类型：生命周期、状态转换、路由、步骤、证据、工具、候选、迭代、模式、验证、预算、人工工作、结果、治理、反馈或探针健康。不得省略 Schema 与事件版本、标识、序号、幂等、事件处理状态、工作流状态、发生时间、载荷类型，以及必需载荷值的字段级来源。多节点流程必须包含父级标识。`event_processing_status` 不得替代 `workflow_state`；`observed_zero` 不得替代 `missing`、`unknown` 或 `not_applicable`。

### Provenance and completion precedence / 来源与补全优先级

Use source-system capture, workflow report, stable-identity correlation, deterministic calculation, explicit rule derivation, human confirmation, clearly labeled model estimate, then `missing`. Attach provenance to each completed field, not only to the event envelope, and preserve method, input, source/version, valid time, capture time, and confidence. An audit-grade required field is not complete when supplied only by model estimate. Resource values default to `missing`, never numeric zero, until observed. / 依次使用源系统采集、主流程上报、稳定标识关联、确定性计算、明确规则推导、人工确认、显著标注的模型估计，最后保留为缺失。来源信息必须附着到每个已补全字段，而不能只附着在事件信封上，并保留方法、输入、来源/版本、有效时间、采集时间和可信度。审计级必填字段仅有模型估计时不算完整。资源值在观测前默认为 `missing`，绝不能默认为数值零。

## Guardrail Sandwich Action Profile / 护栏夹层行动档案

For `PATTERN_0038`, `PROBE_0007` accepts both the reasoning-event and tool-execution-event Schemas. This is a correlated dual stream, not one universal event envelope: reasoning events carry task, step, governance, human-work, and feedback facts; tool events carry frontier, selection, admission, lease, execution, result, and side-effect facts. Join them with stable run, node or step, action, attempt, parent, correlation, causation, and idempotency identities; mark inferred links and never overwrite explicit ones. / 对 `PATTERN_0038`，`PROBE_0007` 同时接受推理事件与工具执行事件 Schema。这是两条可关联事件流，而非一个万能信封：推理事件承载任务、步骤、治理、人工工作和反馈事实；工具事件承载能力前沿、选择、准入、租约、执行、结果与副作用事实。使用稳定的运行、节点或步骤、行动、尝试、父级、关联、因果和幂等标识连接两条流；推断关联必须标记，且不得覆盖显式关联。

Observe PRE and POST with different semantics. PRE facts decide whether the side-effect boundary may be crossed and bind the exact action, approval, permit, policy, input hash, resource version, source lineage, and expiry. POST facts independently describe execution classification, external-effect certainty, output quarantine or release, verification, and recovery. `output_release=blocked` never implies that an already confirmed external effect was prevented. / PRE 与 POST 必须采用不同语义观测。PRE 事实决定能否跨越副作用边界，并绑定精确行动、审批、许可、策略、输入摘要、资源版本、来源血缘与有效期。POST 事实分别描述执行分类、外部效果确定性、输出隔离或放行、核验和恢复。`output_release=blocked` 绝不意味着已经确认的外部效果被阻止。

Use three data classes: non-sampled append-only audit facts for authority and effects; policy-sampled telemetry for performance and diagnostics; controlled evidence references for exceptional raw artifacts. Do not collect private chain-of-thought, credentials, raw parameters, or raw tool output in normal events. A probe outage before a configured high-risk persistence gate fails closed; after the side-effect boundary it causes quarantine and reconciliation, not a false pre-execution block. / 使用三类数据：权限与效果采用不采样的追加写审计事实；性能与诊断采用按策略采样的遥测；例外原始制品采用受控证据引用。普通事件不得采集私密思维过程、凭据、原始参数或原始工具输出。已配置的高风险持久化门禁在副作用边界前遇到探针故障时默认阻断；越界后则进入隔离与核验，不得伪装成执行前阻断。

Propagate source trust and data classification through transformations and evaluate the complete lineage at sensitive sinks. Missing lineage remains `missing` and cannot be silently treated as trusted. The repository has no MCP adapter today; a future adapter should bind trusted server identity, negotiated protocol, schemas, descriptions, annotations, execution metadata, and a normalized contract digest. Unknown security-relevant drift fails closed, and remote annotations never widen local authorization. / 来源可信度和数据等级随转换传播，并在敏感 sink 处检查完整血缘。血缘缺失保持为 `missing`，不得静默视为可信。仓库目前没有 MCP 适配器；未来适配器应绑定可信服务器身份、协商协议、Schema、描述、annotations、执行元数据与规范化契约摘要。未知的安全相关漂移默认阻断，远程 annotations 绝不扩大本地授权。

Guardrail-specific rehearsal, quarantine-release, effect-reconciliation, and compensation events and metrics remain design-level until registered with versioned contracts and tested emitters. Observations may open a policy-change proposal only; require data-quality review, offline replay or adversarial evaluation, authorization, shadow mode, bounded canary, staged rollout, monitoring, and rollback before deployment. / 护栏专属的预演、隔离放行、效果核验、补偿事件与指标，在拥有版本化登记契约和经测试发送器前保持设计层状态。观测数据只能发起策略变更建议；部署前必须经过数据质量检查、离线回放或对抗评估、有权限审批、影子模式、有界金丝雀、分阶段发布、监控和回滚。

## Probe Catalog / 探针目录

Every applicable probe must declare a version, trigger, fields, output, disposition, and owner. The deployable definitions are authoritative in [`probe_registry.json`](../runtime/probe_registry.json); the following table is the human-readable catalog. The IDs are stable and must not be reused. / 每个适用探针必须声明版本、触发点、字段、输出、处置级别和负责人。可部署定义以 [`probe_registry.json`](../runtime/probe_registry.json) 为准；下表是面向人的目录。以下 ID 稳定且不得复用。

| ID and name / ID 与名称 | Trigger and required capture / 触发与必采集 | Signals and gates / 信号与门控 | Primary metrics / 主要指标 |
| --- | --- | --- | --- |
| `PROBE_0001` Task Identity / 任务身份 | Intake, rerun, child task, branch; task/run/step/event/parent IDs. / 入口、重跑、子任务、分支；任务/运行/步骤/事件/父事件 ID。 | Missing, duplicate, broken parent chain, retry misclassified as new task. / 缺失、重复、父子链断裂、重试误记新任务。 | Correlation success, event-chain completeness, duplicate-ID rate. / 关联成功率、事件链完整率、重复 ID 率。 |
| `PROBE_0002` Contract Completeness / 任务契约完整性 | After normalization; goal, output, constraints, risk, reversibility, evidence, validators, budget, stop. / 标准化后；目标、输出、约束、风险、可逆性、证据、验证器、预算、停止。 | Block high-risk execution missing risk, evidence requirement, or mandatory validator. / 高风险任务缺少风险、证据要求或必选验证器时阻断。 | Contract completeness, default-use rate, critical missing rate. / 契约完整率、默认值使用率、关键缺失率。 |
| `PROBE_0003` Route Decision / 路由决策 | Initial route, switch, end; route signals, selected modes, reasons. / 首次路由、换路、结束；路由信号、模式、原因。 | Over/under-reasoning, unexplained switch, observed topology mislabeled as design intent. / 过度/欠推理、无原因换路、将观测拓扑冒充设计意图。 | First-route hit, upgrade, over-reasoning, under-reasoning. / 首次路由命中率、升级率、过度推理率、欠推理率。 |
| `PROBE_0004` Budget And Resources / 预算与资源 | Run, every model/tool call, step close, end; limits and actual use. / 运行、每次模型/工具调用、步骤关闭、结束；上限与实耗。 | Near limit, overrun, anomalous step, retry amplification, low-value parallelism. / 接近上限、越界、单步异常、重试放大、低价值并行。 | Utilization, overrun, cost per validated success, tail latency. / 利用率、越界率、单位验证成功成本、尾部延迟。 |
| `PROBE_0005` Step Closure / 步骤闭环 | Step start and close; claim, action, observation, decision, timestamps, state. / 步骤开始与关闭；命题、动作、观察、决定、时间、状态。 | Action without observation, observation without decision, hanging step, unclosed premise reused. / 有动作无观察、有观察无决定、悬挂步骤、复用未关闭前提。 | Step-closure rate, hanging rate, duration, unverified-premise propagation. / 步骤闭环率、悬挂率、时长、未验证前提传播率。 |
| `PROBE_0006` Evidence Chain / 证据链 | Evidence intake, local and final decision; source, location, version/time, scope, integrity, claim relation. / 证据进入、局部及最终决定；来源、位置、版本/时间、范围、完整性、主张关系。 | Missing, stale, conflicting, unsupported, or untraceable evidence. / 证据缺失、过期、冲突、不支持或不可追踪。 | Coverage, traceability, conflict, stale-use, unsupported-conclusion rate. / 覆盖率、可追踪率、冲突率、过期使用率、无依据结论率。 |
| `PROBE_0007` Tool And Action / 工具与动作 | Before/after tool or action, retry, compensation; tool and plan versions, input fingerprint, authorization policy/grant bindings, live-verification state, outcome, idempotency, and reversibility. / 工具或动作前后、重试、补偿；工具与计划版本、输入指纹、授权策略与授权绑定、实时验证状态、结果、幂等和可逆性。 | Missing/unverified/revoked authority, tool or policy substitution, action without observation, unsafe retry, invalid response, or business-result mismatch. / 授权缺失、未验证或已撤销，工具或策略替换，有动作无观测，不安全重试，响应无效或业务结果不一致。 | Authorization verification, lifecycle completion, success, timeout, retry, duplicate execution, compensation, and outcome consistency. / 授权验证、生命周期完成率、成功率、超时率、重试率、重复执行率、补偿率和结果一致率。 |
| `PROBE_0008` Parallel Path / 并行路径 | Plan inventory, candidate create/close/compare/select, `parallel_path_updated` lease/deadline phases; hypothesis, evidence, worker binding, lease revision, fencing token and expiry, dispatch ID/status, delivery attempts, method version, terminal, validation, elimination, selection, projection hash and anomalies. / 计划清单、候选创建/关闭/比较/选择、`parallel_path_updated` 租约/截止阶段；假设、证据、工作者绑定、租约修订、栅栏令牌与过期时间、分派标识/状态、交付尝试、方法版本、终态、验证、淘汰、选择、投影哈希与异常。 | Partial wave, competing or stale lease holder, stale fencing or delivery token, expired open path or claim, dead-letter growth, paraphrase candidates, shared unverified premise, missing terminal or common criteria, projection drift, score-selection conflict, no validation gain. / 部分波次、竞争或陈旧租约持有者、陈旧栅栏或交付令牌、过期未关闭路径或领取、死信增长、同义改写、共享未验证前提、终态或统一标准缺失、投影漂移、评分与选择冲突、无验证收益。 | Material difference, candidate completion, lease expiry and reassignment, handoff latency, delivery retry amplification, dead-letter count, branch diversity, branch-record completeness, convergence, winner validation, invalid parallel cost. / 实质差异率、候选完成率、租约过期与重分配、接管时延、交付重试放大、死信数量、分支多样性、分支记录完整率、收敛率、胜出验证率、无效并行成本。 |
| `PROBE_0009` Iteration Progress / 迭代进展 | Every round; hypothesis set, key unknown, action and expected gain, observation, hypothesis delta, cost. / 每轮；假设集、关键未知、动作及预期增益、观察、假设变化、成本。 | No new evidence, unbounded hypothesis growth, repeated call, no decision change, risk exceeds expected gain. / 无新证据、假设无边界扩张、重复调用、决定不变、风险高于预期收益。 | Elimination efficiency, information gain, no-progress rate, convergence rounds, round cost. / 淘汰效率、信息增益、无进展率、收敛轮次、单轮成本。 |
| `PROBE_0010` Goal And Constraint Drift / 目标与约束漂移 | Contract, key step close, switch, final output; initial/current snapshots and revision records. / 契约、关键步骤关闭、换路、最终输出；初始/当前快照和修订记录。 | Goal, hard-constraint, or verified-fact drift; missing revision approval. / 目标、硬约束或已验证事实漂移；缺少修订批准。 | Drift rate, legal-revision rate, detection delay, affected steps. / 漂移率、合法修订率、发现延迟、受影响步骤数。 |
| `PROBE_0011` Validation / 验证 | Candidate, validator start/end, pre-completion; validator identity/version/input/criteria/result/independence. / 候选、验证开始/结束、完成前；验证器标识/版本/输入/标准/结果/独立性。 | Block missing mandatory validator, failed validation entering completed, self-review-only release, candidate-input mismatch. / 缺少必选验证、验证失败却完成、仅自评放行、候选与验证输入不一致时阻断。 | Pass, coverage, repairable failure, disagreement, post-validation rework. / 通过率、覆盖率、可修复失败率、分歧率、验证后返工率。 |
| `PROBE_0012` Stop And Escalation / 停止与升级 | Switch, budget alert, terminal transition, human escalation; reason, trigger, evidence, remaining budget, unfinished work, recipient. / 换路、预算告警、终态、人工升级；原因、触发、证据、剩余预算、未完成工作、接收方。 | Missing stop reason, work after exhaustion, missed escalation, context-free escalation, premature escalation. / 停止原因缺失、耗尽后继续、漏升级、无上下文升级、过早升级。 | Stop-reason completeness, stop quality, escalation appropriateness, exhaustion-stop rate. / 停止原因完整率、停止质量、升级适当率、耗尽停止率。 |
| `PROBE_0013` Outcome Return / 结果回接 | Real outcome, human review, reopened task, discovered error; original IDs, outcome, source, time, original route and validators, rework. / 真实结果、人工复核、任务重开、错误发现；原 ID、结果、来源、时间、原路由与验证器、返工。 | Preserve unmatched outcomes instead of guessing linkage. / 无法可靠关联时保留未匹配，不猜测。 | Correctness, rework, false release, false escalation, calibration, per-mode outcome. / 正确率、返工率、误放行率、误升级率、校准、分模式后验。 |
| `PROBE_0014` Privacy And Governance / 隐私与治理 | Event create/write/query/export/expiry; classification, access, redaction, retention, export, approval. / 事件产生/写入/查询/导出/到期；分类、访问、脱敏、保留、导出、审批。 | Unredacted sensitive data, unauthorized access, expired retention, deleted audit field, captured private reasoning. / 敏感数据未脱敏、越权访问、超期保留、审计字段删除、采集私密推理。 | Redaction coverage, unauthorized events, expiry rate, governance blocks, leakage. / 脱敏覆盖率、越权事件、超期率、治理阻断、泄露率。 |
| `PROBE_0015` Probe Self-Health / 探针自健康 | Receive, process, persist, calculate, alert; received/dropped/duplicate counts, latency, parse/calc/send result. / 接收、处理、持久化、计算、告警；接收/丢弃/重复数、延迟、解析/计算/发送结果。 | Backlog, loss, disorder, duplication, parsing failure, outage. / 积压、丢失、乱序、重复、解析失败、不可用。 | Coverage, loss, duplicate, observation latency, availability, completion success. / 覆盖率、丢失率、重复率、观测延迟、可用率、补全成功率。 |
| `PROBE_0016` Reflection Admission And Routing / 反思准入与路由 | Reflection candidate, eligibility decision, route; trigger, reviewed version, baseline, signal or evidence plan, change scope, revalidation, stop policy. / 反思候选、准入决定、路由；触发、被审版本、基线、新信号或取证计划、改变范围、复验、停止策略。 | Block automatic reflection when its contract is incomplete or its route contradicts eligibility. / 契约不完整或路由与准入矛盾时阻断自动反思。 | Admission compliance, qualified-new-signal rate, route consistency. / 准入合规率、有效新信号率、路由一致率。 |
| `PROBE_0017` Reflection Baseline Comparability / 反思基线可比性 | Baseline freeze and round close; subject, criteria, validators, regression scope, environment, premeasured metric, reconstruction approval/evidence, comparison state. / 基线冻结与轮次关闭；对象、标准、验证器、回归范围、环境、预测指标、重建审批/证据、可比状态。 | Block verified-improvement claims without a fixed measured baseline or an independently approved, evidence-bound rebase. / 缺少固定已测基线或独立批准且绑定证据的重建基线时阻断已验证改善声明。 | Improvement-comparability coverage. / 改善可比覆盖率。 |
| `PROBE_0018` Independent Reflection Revalidation / 反思独立复验 | Changed version and revalidation start/end; exact candidate, validator set, validation evidence, qualified-signal evidence bindings, recomputed unique count, verdict. / 改变版本与复验起止；精确候选、验证器集合、复验证据、有效信号证据绑定、重算唯一数量、裁定。 | Block acceptance when mandatory validators, candidate binding, or non-reused independent-signal bindings are missing. / 缺少必选验证器、候选绑定或未复用独立信号绑定时阻断接受。 | Independent-revalidation coverage, verified-improvement rate. / 独立复验覆盖率、验证改善率。 |
| `PROBE_0019` Validator Gaming / 验证器投机 | Change proposal, authorization, application, revalidation; tests, rules, scorer, denominator, approvals. / 改变提议、授权、应用、复验；测试、规则、评分器、分母、审批。 | Fail closed on deleted failures, skipped checks, narrowed denominators, candidate mismatch, or unapproved validator changes. / 删除失败项、跳检查、缩分母、候选错配或未审批验证器改变时默认阻断。 | Validator-gaming rate and direct integrity incidents. / 验证器投机率与直接完整性事件。 |
| `PROBE_0020` Reflection Regression And Recovery Guard / 反思回归与恢复保护 | Revalidation and rollback events; passing set, hard constraints, failed/restored subjects, contract rollback binding, apply and verification evidence. / 复验与回滚事件；通过集合、硬约束、失败/恢复对象、契约回滚绑定、应用与验证证据。 | Any blocking regression prevents continuation and acceptance; `rolled_back` requires applied and independently verified recovery. / 阻断级回归阻止继续与接受；`rolled_back` 要求恢复已应用并独立验证。 | Regression-free verified-improvement rate. / 无回归验证改善率。 |
| `PROBE_0021` Reflection Closure / 反思闭环 | Round start/end and reflection stop; contract-valid sequence, state, outcome, progress, budgets, verified recovery, stop reason. / 轮次起止与反思停止；符合契约的序列、状态、结果、进展、预算、已验证恢复、停止原因。 | Detect hanging rounds, continuation without progress, textual-only rollback, work beyond budget, or missing terminal reason. / 发现悬空轮次、无进展继续、仅文本回滚、预算后工作或终态原因缺失。 | Reflection-closure rate, qualified-new-signal rate. / 反思闭环率、有效新信号率。 |
| `PROBE_0022` Reflection Confounder And Attribution / 反思混杂因素与归因 | Attribution promotion and close; falsifier, confounders, evidence kind, contract-approved authority, never-reused evidence, validation and comparison state. / 归因晋升与关闭；反证条件、混杂因素、证据类型、契约批准权威、不可复用证据、复验与可比状态。 | Downgrade causal claims whose authority or revalidation supports only observation, correlation, or unknown results. / 权威或复验只支持观察、相关或未知结果时降低因果声明等级。 | Attribution-overclaim rate. / 归因越级率。 |
| `PROBE_0023` Reflection Learning Promotion / 反思学习晋升 | Learning candidate and promotion decision; source round/subject/evidence, task distribution, sample, baseline, success/risk, version, rollback, expiry, owner. / 学习候选与晋升决定；来源轮次/对象/证据、任务分布、样本、基线、成功/风险、版本、回滚、有效期、责任人。 | Block persistent promotion when evidence is incomplete or unrelated to the source round. / 证据不完整或与来源轮次无关时阻断持久晋升。 | Learning-promotion evidence completeness and later recurrence. / 学习晋升证据完整率与后续复发率。 |

## Standalone And Interactive Operation / 独立与交互运行

### Standalone workflow / 独立流程

Accept a workflow definition, event stream, logs, run records, or tables plus scene, risk, expected stages, mandatory fields and validators, service objectives, privacy policy, and deployment mode. Reconstruct the state machine and timeline; map fields and events; establish correlation; run identity and completeness probes first; complete only deterministic data; run applicable quality and governance probes; compute supported metrics; mark unsupported metrics with reasons; then emit gaps, instrumentation, alerts, and a report. / 接收工作流定义、事件流、日志、运行记录或数据表，以及场景、风险、预期阶段、必填字段与验证器、服务目标、隐私策略和部署模式。重建状态机与时间线，映射字段和事件，建立关联，先运行身份与完整性探针，只补全确定性数据，再运行适用的质量与治理探针，计算有数据支持的指标，对不可计算项标明原因，最后输出缺口、埋点、告警与报告。

Classify each gap as automatically completable, workflow-report required, human-confirmation required, or unavailable. / 将每个缺口分类为可自动补全、需主流程上报、需人工确认或不可获得。

### Interactive handshake / 交互握手

```yaml
handshake:
  task_id: TASK_XXXX
  run_id: RUN_XXXX
  scene_id: SCENE_XXXX
  risk_level: medium
  observation_level: minimal | standard | audit
  deployment_mode: advisory
  event_schema_version: 1.0.0
  contract_summary:
    initial_mode: chain
    budget_profile: standard
    mandatory_validators: []
    stop_condition_version: 1
handshake_result:
  status: accepted | degraded | rejected
  enabled_probes: []
  missing_capabilities: []
  required_fields: []
  block_rules: []
```

### Feedback contract / 反馈契约

Feedback is an immutable revisioned event stream, not a mutable side record. Emit `feedback_updated` with exactly one of `raised`, `acknowledged`, `resolved`, or `exempted`; use the same `feedback_id` across the lifecycle and increase `revision` for every accepted state change. The event-envelope `idempotency_key` is `feedback:<feedback_id>:<revision>`; a retry of the same revision reuses that key, while different content under the same key is rejected. / 反馈是不可变、带修订号的事件流，不是可原地修改的旁路记录。统一发出 `feedback_updated`，且阶段只能是 `raised`、`acknowledged`、`resolved` 或 `exempted`；整个生命周期沿用同一 `feedback_id`，每次被接受的状态变化递增 `revision`。事件信封的 `idempotency_key` 为 `feedback:<feedback_id>:<revision>`；同一修订重试必须复用该键，同键不同内容必须拒绝。

```yaml
event_type: feedback_updated
idempotency_key: feedback:FEEDBACK_XXXX:1
payload:
  kind: feedback
  data:
    phase: raised | acknowledged | resolved | exempted
    feedback_id: FEEDBACK_XXXX
    revision: 1
    probe_binding: {id: PROBE_XXXX, version: 1.0.0, hash: "sha256:..."}
    severity: info | warning | critical
    feedback_type: data_gap | route_risk | budget_risk | drift | evidence_gap | validation_gap | no_progress | governance_block
    finding_code: MISSING_REQUIRED_VALIDATOR
    related_event_id: EVENT_XXXX | null
    rule_binding: {id: RULE_XXXX, version: 1.0.0, hash: "sha256:..."}
    protected_transition:
      transition_id: TRANSITION_XXXX | null
      from_state: validating
      to_state: completed
      owner_binding: {id: OWNER_XXXX, version: 1.0.0, hash: "sha256:..."}
    blocking: true
    validity: current_step | current_run | persistent_config
    lifecycle_status: open | accepted | ignored | alternative_applied | resolved | exempted
```

| Phase / 阶段 | Required phase fields / 阶段必填字段 | Status rule / 状态规则 |
| --- | --- | --- |
| `raised` / 提出 | `finding`, `evidence_bindings`, `suggested_actions`, `raised_at` | `lifecycle_status=open`; response, resolution, and exemption fields are absent. / 状态为 `open`；不得出现响应、解决和豁免字段。 |
| `acknowledged` / 确认 | `response`, `response_code`, `responded_at`, `actor_binding` | `accept→accepted`, `ignore→ignored`, `alternative_action→alternative_applied`. / 响应与状态严格对应。 |
| `resolved` / 解决 | `resolution_code`, `resolved_at`, `actor_binding`, `resolution_evidence_bindings`, `resolution_authority_binding` | `lifecycle_status=resolved`; a blocking transition reopens only after remediation evidence and a current authority grant are accepted. / 状态为 `resolved`；补救证据与当前权限授予均被接受后才解除阻断。 |
| `exempted` / 豁免 | `exempted_at`, `exemption` | `lifecycle_status=exempted`; the exemption includes approver, authority, scope, approval/expiry times, compensating controls, and bound input/contract/candidate/rule versions. / 状态为 `exempted`；豁免必须包含批准人、权限、范围、批准与过期时间、补偿控制及绑定的输入、契约、候选和规则版本。 |

An info signal records only and cannot block. A warning requires an acknowledged accept, ignore, or alternative-action event. A non-blocking critical signal stops low-value work and triggers reassessment. A blocking critical signal prevents only its named protected transition until a live-authorized resolution or a scoped, unexpired, live-authorized exemption. Exemptions are non-transferable: input, contract, candidate, rule version, authority, scope, or expiry change invalidates them and requires a new revision and approval. Probe outage or unavailable authorization fails closed for protected high-risk transitions. / 提示信号只记录且不得阻断。警告信号必须产生已确认的采纳、忽略或替代动作事件。非阻断严重信号停止低价值工作并触发重评。阻断型严重信号只阻止明确命名的受保护转换，直至解决记录通过实时授权，或获得限定范围、未过期且通过实时授权的豁免。豁免不可转移：输入、契约、候选、规则版本、权限、范围或有效期变化时立即失效，必须用新修订重新审批。探针故障或授权源不可用时，对受保护高风险转换默认阻断。

The reference kernel implements this control path through `ReasoningEngine.record_feedback()` and an injected `feedback_authorizer`: it enforces `feedback:<id>:<revision>` idempotency, contiguous revisions, legal phase transitions, stable rule/probe/protected-transition bindings, and transition-specific blocking. Resolution and exemption are checked when recorded and checked again immediately before the protected transition. The authorizer receives only a detached feedback record and bounded public run context; absence, exception, revocation, or any value other than exact `true` fails closed. An exemption additionally requires its scope, approval/expiry interval, normalized input, contract, candidate, and rule bindings to remain current. / 参考内核通过 `ReasoningEngine.record_feedback()` 与注入的 `feedback_authorizer` 实现该控制路径：强制 `feedback:<id>:<revision>` 幂等键、连续修订、合法阶段转换、稳定的规则/探针/受保护转换绑定及面向具体转换的阻断。解决与豁免在记录时校验，并在真正跨越受保护转换前再次校验。授权器只接收脱离内部状态的反馈记录与有界公开运行上下文；授权器缺失、异常、授权撤销或返回值不是精确 `true` 均默认阻断。豁免还要求其范围、批准/过期区间、标准化输入、契约、候选和规则绑定持续有效。

## Metrics And Alerts / 指标与告警

Every metric record includes metric ID and version, immutable calculation inputs and their digest, numerator, denominator, the complete declared exclusion-count map, required buckets, completeness, source mix, and uncomputable reason. Its RFC 3339 time window also records `time_basis`, watermark, allowed lateness, positive revision, and finalized state. Never merge low-risk lookup with high-risk approval, direct processing with root-cause investigation, outcome-known with outcome-unknown, sidecar with inline, or complete data with inference-heavy data. / 每个指标记录指标 ID 与版本、不可变计算输入及其摘要、分子、分母、完整的声明式排除计数、必需分桶、完整性、来源构成和不可计算原因。RFC 3339 时间窗还必须记录时间基准、watermark、允许迟到量、正整数修订号和封窗状态。不得混合低风险查询与高风险审批、直接处理与根因调查、已有后验与无后验、旁路与内联、字段完整与大量推断补全的数据。

The machine-readable metric definitions and reference calculations live in [`metric_registry.json`](../runtime/metric_registry.json) and [`reasoning_metrics.py`](../runtime/reasoning_metrics.py); deployable probe definitions live in [`probe_registry.json`](../runtime/probe_registry.json), and mode-to-probe coverage is authoritative in [`probe_dependency_matrix.json`](../runtime/probe_dependency_matrix.json). Before collection, call `resolve_required_probes` with execution mode, supporting topologies, and a complete `condition_states` map for every applicable conditional feature. For an admitted reflection, additionally call `resolve_reflection_required_probes`; its core profile is `PROBE_0016` through `PROBE_0021`, with `PROBE_0022` activated for attribution claims and `PROBE_0023` for learning promotion. Each tri-state mode condition is `true`, `false`, or `unknown`; missing or `unknown` fails closed, while only `true` activates the conditional probe. Persist the resolved versioned bindings with the collector plan. Metric state must distinguish computed values, observed zero, missing, unknown, not applicable, and insufficient sample. / 机器可读指标定义和参考计算位于 [`metric_registry.json`](../runtime/metric_registry.json) 与 [`reasoning_metrics.py`](../runtime/reasoning_metrics.py)；可部署探针定义位于 [`probe_registry.json`](../runtime/probe_registry.json)，模式到探针覆盖以 [`probe_dependency_matrix.json`](../runtime/probe_dependency_matrix.json) 为准。采集前必须以执行模式、支撑拓扑和覆盖全部适用条件特征的 `condition_states` 映射调用 `resolve_required_probes`。对已准入反思，还必须调用 `resolve_reflection_required_probes`；其核心档案为 `PROBE_0016` 至 `PROBE_0021`，声明归因时启用 `PROBE_0022`，晋升学习时启用 `PROBE_0023`。每个模式条件只能是 `true`、`false` 或 `unknown`；缺失或 `unknown` 默认阻断，只有 `true` 才激活条件探针。将解析后的版本化绑定与采集计划一同持久化。指标状态必须区分已计算值、观测零值、缺失、未知、不适用和样本不足。

The reference functions calculate the numeric core only. Before persistence or publication, wrap each `MetricResult` with its exact `calculation_inputs`, registry version, finalized time window, required buckets, declared exclusion counts, completeness, source mix, expected-event or expected-run manifest version where applicable, and probe-health status. A bare ratio without that envelope is diagnostic scratch data, not a reportable metric. / 参考函数只计算数值核心。持久化或发布前，必须为每个 `MetricResult` 补充精确的 `calculation_inputs`、注册表版本、已封窗时间窗、必需分桶、声明式排除计数、完整性、来源构成，并在适用时补充预期事件或预期运行清单版本及探针健康状态。缺少该信封的裸比率只能作为诊断草稿，不能作为可发布指标。

The reference runtime implements this boundary with `MetricEnvelope`, `metric_publication_failures`, and `publish_metric`. The strict publication guard re-runs `calculate_metric` from persisted inputs using the registry-owned `minimum_sample`, compares state/value/numerator/denominator/sample/reason/details, validates the finalized watermark window, exact exclusion keys and required buckets, and requires healthy universal and metric-specific probes plus an expected-inventory manifest where applicable. An unavailable or inconsistent envelope may still be serialized as diagnostic status, but it must not be presented as a published numeric metric. / 参考运行时通过 `MetricEnvelope`、`metric_publication_failures` 与 `publish_metric` 实现该边界。严格发布门控从持久化输入重新调用 `calculate_metric`，使用注册表拥有的 `minimum_sample`，比较状态、数值、分子、分母、样本、原因和详情，并校验封窗 watermark、精确排除键、必需分桶、健康的通用与指标专用探针，以及适用时的预期清单。不可用或不一致信封仍可序列化为诊断状态，但不得作为已发布数值指标展示。

### MVP core coverage / MVP 核心覆盖

The 65 registered formulas are the implemented MVP core, not the complete long-term metric catalog. The authoritative `coverage` declaration in `metric_registry.json` separates `implemented`, `planned`, and `gate_eligible` identifiers. Implemented metrics that are not `gate_eligible` remain publication-grade diagnostics only; planned metrics may be used as design candidates only. Neither class may drive a statistical alert, block, release, or protected transition until promoted to `gate_eligible` with source-backed threshold evidence. Direct per-instance integrity rules—such as validator gaming or an accepted change without independent revalidation—remain hard guards rather than aggregate metric thresholds. / 已注册的 65 项公式是已实现的 MVP 核心，而不是长期指标目录的全集。`metric_registry.json` 中权威的 `coverage` 声明将指标区分为 `implemented`、`planned` 与 `gate_eligible`。已实现但不在 `gate_eligible` 中的指标仍只可作为可发布诊断；规划中指标只能作为设计候选。两者在基于数据来源与阈值证据晋升为 `gate_eligible` 前，均不得驱动统计告警、阻断、放行或受保护转换。验证器投机、缺少独立复验却接受改变等逐实例完整性规则仍是硬闸门，而不是聚合指标阈值。

The planned set retains important follow-up work such as synthesis fidelity, minority preservation, validation disagreement and rework, result correctness, end-to-end latency, stop and escalation quality, governance blocking, probe availability, and observation latency. Candidate terminal completion, observed branch diversity, and branch-record completeness are implemented diagnostics. / 规划集合保留综合保真度、少数结论保留、验证器分歧与返工、结果正确性、端到端时延、停止与升级质量、治理阻断、探针可用率和观测延迟等重要后续能力。候选终态完成率、观测分支多样性和分支记录完整率已经实现为诊断指标。

### Core formulas / 核心公式

```text
validation_pass_rate = runs_passing_all_mandatory_validators / runs_with_valid_validation_results
route_stability_rate = runs_without_route_insufficiency_switch / runs_with_valid_initial_route
outcome_route_accuracy = correct_routes_with_outcome / routed_runs_with_outcome
outcome_linkage_coverage = trustworthy_linked_route_outcomes / completed_route_atoms_eligible_for_outcome_linkage
underroute_rate = atoms_succeeding_only_after_route_insufficiency_upgrade / completed_atoms_with_auditable_route_outcome
overroute_rate = audited_atoms_where_lighter_route_meets_same_validators / atoms_in_valid_counterfactual_audit_sample
route_abstention_rate = abstained_route_decisions / route_decisions_with_complete_identity
route_oscillation_rate = atoms_exceeding_scene_switch_or_reversal_threshold / atoms_with_complete_switch_chain
forced_route_with_missing_signal_rate = executable_routes_with_required_signal_missing_or_unknown / executable_routes
cost_per_validated_success = total_cost_units / validated_completed_runs
reasoning_drift_rate = long_runs_with_unapproved_goal_constraint_or_fact_drift / long_runs_with_comparable_snapshots
```

### Integrity and reasoning formulas / 完整性与推理质量公式

```text
contract_completeness = runs_with_all_required_contract_fields / runs_requiring_contract
event_chain_completeness = linkable_expected_runs / expected_runs
eligible_step_closure_rate = closed_eligible_steps / eligible_started_steps
closed_step_record_completeness = complete_closed_step_records / closed_steps
evidence_traceability = evidence_with_source_version_or_time_and_location / referenced_evidence
validation_coverage = runs_executing_all_mandatory_validators / runs_requiring_validation
stop_reason_completeness = terminal_runs_with_valid_stop_or_escalation_reason / terminal_runs
probe_completion_rate = reliably_completed_fields / fields_classified_as_completable
evidence_coverage = key_claims_with_valid_support / key_claims
unsupported_conclusion_rate = key_conclusions_without_evidence_and_not_labeled_inference / key_conclusions
unverified_premise_propagation = unverified_premises_reused_as_fact / reused_premises
```

### Topology, cost, governance, and health formulas / 拓扑、成本、治理与健康公式

```text
material_candidate_difference = materially_distinct_candidates / all_candidates
candidate_completion_rate = candidate_paths_with_terminal_record / planned_candidate_paths
branch_diversity = distinct_candidate_bindings / completed_candidate_paths
branch_record_completeness = complete_terminal_branch_records / terminal_branch_records
path_convergence_rate = parallel_runs_selecting_a_validated_path / parallel_runs_completing_comparison
no_progress_loop_rate = iterative_runs_hitting_configured_no_progress_streak / iterative_runs
hypothesis_elimination_per_iteration = hypotheses_eliminated_by_valid_evidence / completed_iterations
hypothesis_elimination_per_cost_unit = hypotheses_eliminated_by_valid_evidence / observed_cost_units
budget_utilization_vector = actual_use[dimension] / configured_limits[dimension]
max_budget_utilization = max(budget_utilization_vector.values)
budget_overrun_rate = runs_exceeding_any_budget_dimension / runs_with_budget_record
tool_success_rate = successful_structurally_valid_tool_calls / tool_calls
retry_amplification = actual_calls_including_retries / deduplicated_logical_calls
false_release_rate = confirmed_false_releases / auto_released_runs_with_outcome
probe_coverage = required_stages_with_required_probes / required_stages
event_loss_rate = expected_but_missing_events / expected_events
duplicate_event_rate = duplicate_events / received_events
parse_failure_rate = version_unparseable_events / received_events
alert_delivery_rate = delivered_alerts / alerts_due
plan_compile_success_rate = successful_plan_compilations / plan_compilation_attempts
plan_drift_rate = chain_runs_with_plan_drift / inspected_chain_runs
checkpoint_validation_binding_rate = checkpoint_validations_with_complete_bindings / checkpoint_validations
budget_pre_reservation_coverage = steps_reserved_before_start / started_chain_steps
evidence_resolution_rate = resolved_step_evidence_bindings / step_evidence_bindings
candidate_evidence_lineage_integrity_rate = candidates_with_complete_revision_lineage / inspected_plan_bound_candidates
readonly_tool_lifecycle_completion_rate = readonly_tool_dispatches_with_one_matching_observation / readonly_tool_dispatches_due_for_observation
dispatch_admission_coverage = executions_with_valid_admission / execution_starts
side_effect_lease_coverage = side_effecting_executions_with_valid_lease / side_effecting_execution_starts
state_evidence_coverage = write_executions_with_current_state_evidence / write_executions_requiring_state_evidence
approval_binding_coverage = approval_bound_execution_starts / approval_required_execution_starts
frontier_escape_rate = frontier_escape_executions / execution_starts
dispatch_record_completeness = complete_dispatch_records / dispatch_records
result_unknown_rate = unknown_results / executed_results
duplicate_side_effect_rate = duplicate_side_effects / confirmed_side_effect_results
reflection_admission_compliance = compliant_admitted_reflections / auto_reflection_instances
reflection_closure_rate = closed_reflection_rounds / started_reflection_rounds
independent_revalidation_coverage = independently_revalidated_rounds / rounds_requiring_revalidation
improvement_comparability_coverage = comparable_improvement_assessments / improvement_assessments
regression_free_verified_improvement_rate = regression_free_verified_improvements / completed_revalidation_rounds
validator_gaming_rate = validator_gaming_rounds / changed_rounds
qualified_new_signal_rate = rounds_with_qualified_new_signal / admitted_reflection_rounds
attribution_overclaim_rate = overclaimed_attribution_records / attribution_claim_records
learning_promotion_evidence_completeness = complete_learning_promotion_records / learning_promotion_records
```

`route_stability_rate` is not route accuracy and remains diagnostic without an owned threshold and promotion evidence. Only outcome-backed or independently audited labels may populate `outcome_route_accuracy`, `underroute_rate`, or `overroute_rate`. `outcome_linkage_coverage` is implemented as diagnostic completeness, but outcome-backed correctness metrics remain non-gating until that coverage meets an owned threshold. `candidate_completion_rate`, `branch_diversity`, and `branch_record_completeness` are implemented diagnostics; they do not become gates merely because the formula exists. `path_convergence_rate` remains diagnostic until an owner enforces a candidate-completion threshold and approves minimum samples, drift controls, and promotion evidence. The seven chain-factory metrics, three parallel-factory diagnostics, eight tool-dispatch diagnostics, and nine reflection diagnostics remain non-gating until owned thresholds and promotion evidence are approved. A zero aggregate does not suppress per-instance emergency anomalies: execution without admission, write execution without a lease, frontier escape, duplicate confirmed side effects, reflection without admission, validator gaming, acceptance without independent revalidation, or a blocking regression are direct integrity violations. Budget utilization is a vector over tokens, latency, model calls, tool calls, paths, iterations, retries, and cost; never sum heterogeneous units. Identity, privacy/governance, and probe self-health are universal dependencies. / `route_stability_rate` 不是路由准确率；在缺少负责人阈值与晋升证据时仅作诊断。只有真实后验或独立审计标签才能进入 `outcome_route_accuracy`、`underroute_rate` 或 `overroute_rate`。`outcome_linkage_coverage` 已作为诊断完整度实现，但在其达到负责人阈值前，后验正确性指标仍不可门控。`candidate_completion_rate`、`branch_diversity` 与 `branch_record_completeness` 已实现为诊断指标；公式存在不等于可以门控。只有负责人强制候选完成阈值，并批准最小样本、漂移控制和晋升证据后，`path_convergence_rate` 才可超越诊断用途。七项链工厂指标、三项并行工厂诊断、八项工具调度诊断与九项反思诊断在负责人阈值和晋升证据获批前仍不可门控。聚合指标为零也不能压制逐实例紧急异常：未经准入执行、写执行无租约、能力前沿逃逸、重复已确认副作用、未准入即反思、验证器投机、缺少独立复验却接受或发生阻断级回归，均属于直接完整性违规。预算利用率是令牌、延迟、模型调用、工具调用、路径、迭代、重试和成本的向量，禁止累加异构单位。身份、隐私治理和探针自健康是通用依赖。

### Hard alerts / 硬告警

Raise a critical alert without waiting for a statistical baseline when a high-risk run lacks a mandatory validator; failed validation enters `completed`; an irreversible action lacks permission or approval; a tool starts without a sealed allow decision; a write starts without a current state-evidence binding and durable execution lease; a selected tool escapes the sealed capability frontier; a result-unknown action is directly retried; the same idempotency identity has multiple confirmed side effects; a key factual conclusion has no evidence; execution continues after budget overrun; a hard constraint drifts without approval; a terminal run lacks a reason; identity linkage is irrecoverably broken; sensitive data is not redacted; private chain-of-thought is captured; a change is applied before reflection admission, baseline freeze, or authorization; an accepted reflection lacks exact-version independent revalidation; a validator is weakened or changed without independent approval and rebasing; a blocking regression continues or is accepted; attribution exceeds its evidence; or a reflection ends without a closed round and stop reason. / 出现以下情况时无需等待统计基线，直接产生严重告警：高风险运行缺少必选验证器；验证失败却进入完成态；不可逆动作缺少权限或审批；工具在缺少封存放行决定时启动；写动作在缺少当前状态证据绑定和持久执行租约时启动；所选工具逃逸封存能力前沿；结果未知动作被直接重试；同一幂等身份出现多个已确认副作用；关键事实结论无证据；预算越界后仍继续；硬约束未经批准发生漂移；终态缺少原因；标识链不可恢复；敏感数据未脱敏；采集私密思维过程；反思未准入、未冻结基线或未授权就应用改变；接受反思缺少改变后精确版本的独立复验；验证器未经独立审批与基线重建被削弱或修改；存在阻断级回归却继续或接受；归因强度超过证据；或反思结束时轮次与停止原因未闭合。

For statistical alerts define target, warning, critical, registry-owned minimum sample, sustained window, buckets, and baseline version. `calculate_metric` must enforce that registered minimum; return `insufficient_sample` instead of a trend judgment when the sample is too small. / 统计告警必须定义目标值、警戒值、严重值、由注册表拥有的最小样本、持续窗口、分桶和基线版本。`calculate_metric` 必须执行该注册最小样本；样本不足时返回 `insufficient_sample`，不得强行判断趋势。

## Data Completion And Scenario Packs / 数据补全与场景包

| Missing field / 缺失字段 | Allowed completion / 允许补全 | If unavailable / 不可得时 |
| --- | --- | --- |
| Task/run/step/parent IDs / 任务、运行、步骤、父标识 | Generate at boundary and propagate. / 在边界生成并传播。 | Mark correlation broken; block cross-node aggregation. / 标记关联断裂；阻止跨节点聚合。 |
| Stage time / 阶段时间 | Wrap start/end or calculate from raw timestamps. / 包裹开始结束或用原始时间戳计算。 | Mark latency uncomputable. / 标记延迟不可计算。 |
| Route reason / 路由原因 | Capture router I/O or request workflow report. / 采集路由器输入输出或请求主流程上报。 | Record observed mode only, not design intent. / 只记录观测模式，不冒充设计意图。 |
| Budget limit and use / 预算上限与消耗 | Read scene config; wrap calls or link billing. / 读取场景配置；包裹调用或关联账单。 | Separate unknown limit from incomplete actual cost. / 区分上限未知与实际成本不完整。 |
| Claim, evidence, local decision / 命题、证据、局部决定 | Require step events; assign evidence identity to retrievable sources. / 要求步骤事件；为可取回来源分配证据 ID。 | Fail step closure; never infer a pass. / 步骤闭环失败；不得推断为通过。 |
| Validation and stop / 验证与停止 | Wrap validators; require terminal reason before transition. / 包裹验证器；终态转换前强制原因。 | High-risk completion blocked; terminal integrity fails. / 阻断高风险完成；终态完整性失败。 |
| Outcome / 真实结果 | Link business key, task ID, or human work ID. / 用业务键、任务 ID 或人工处理 ID 关联。 | Preserve unmatched or outcome-pending. / 保留未匹配或待回接。 |
| Goal/constraint versions / 目标与约束版本 | Snapshot and deterministically compare. / 建立快照并确定性比较。 | Mark drift metrics uncomputable. / 标记漂移指标不可计算。 |

Default scene packs / 默认场景包:

- Real-time query / 实时查询: identity, routing, budget, evidence, stop, self-health; sidecar plus advisory. / 身份、路由、预算、证据、停止、自健康；旁路加建议。
- Approval and risk / 审批与风控: contract, evidence, validation, stop/escalation, privacy, outcome; inline protected transitions. / 契约、证据、验证、停止升级、隐私、结果；关键转换内联阻断。
- Root-cause investigation / 根因调查: step closure, iteration progress, drift, budget, tools; block configurable no-progress and overrun. / 步骤闭环、迭代进展、漂移、预算、工具；无进展和越界可配置阻断。
- Multi-policy comparison / 多口径比较: parallel path, evidence, validation, budget; advisory candidate-completeness checks. / 并行路径、证据、验证、预算；候选完整性建议。
- Batch / 批处理: identity, step, tool, budget, stop, self-health; inline idempotency and duplicate-execution protection. / 身份、步骤、工具、预算、停止、自健康；内联幂等与重复执行保护。
- Multi-agent / 多智能体: identity, parent chain, evidence, step closure, drift, validation; mandatory parent propagation. / 身份、父子链、证据、步骤闭环、漂移、验证；强制父标识传播。
- Code repair / 代码修复: contract, tools, validation, budget, outcome; tests gate completion. / 契约、工具、验证、预算、结果；测试作为完成闸门。
- Retrieval augmented / 检索增强: evidence, tools, routing, validation; audit completion requires evidence refs for factual output. / 证据、工具、路由、验证；审计级事实输出必须有证据引用。

## Report And Acceptance / 报告与验收

Return an answer-first report with scope, workflow and event versions, covered and correlatable runs, deployment mode, health state, most important finding, most important data gap, highest-priority instrumentation change, four core metrics, integrity metrics, issues with evidence and action, completion ledger, alerts, and limitations. / 输出结论先行的报告，包含范围、工作流与事件版本、覆盖与可关联运行数、部署模式、健康状态、最重要发现、最重要数据缺口、最高优先级埋点改造、四项核心指标、完整性指标、带证据和动作的问题、补数记录、告警与限制。

Acceptance checklist / 验收清单:

- Identities propagate across retries, tools, processes, branches, and child tasks. / 标识可跨重试、工具、进程、分支和子任务传播。
- Event schema versions are compatible; missing, zero, and not-applicable remain distinct. / 事件版本兼容；缺失、零和不适用保持区分。
- Route, budget, step, evidence, tool, drift, validation, stop, outcome, privacy, and probe-health stages have applicable probes. / 路由、预算、步骤、证据、工具、漂移、验证、停止、结果、隐私和探针健康阶段都有适用探针。
- Conflict data is preserved; inferred correlation never replaces explicit correlation. / 冲突数据被保留；推断关联不覆盖显式关联。
- Completion records retain source type, method, time, version, and confidence. / 补全记录保留来源类型、方法、时间、版本和可信度。
- Metric calculations are reproducible and return insufficient data instead of false certainty. / 指标计算可复现；数据不足时返回不足，不制造确定性。
- Inline blocks, exemptions, alert delivery, event loss, duplication, ordering, parsing, and probe outages are auditable. / 内联阻断、豁免、告警送达、事件丢失、重复、乱序、解析与探针故障均可审计。
- Probe failure cannot silently release protected high-risk work. / 探针故障不能静默放行受保护的高风险工作。
- No business truth, evidence, approval, validation pass, or private chain-of-thought is fabricated or inferred as observed. / 不将业务事实、证据、审批、验证通过或私密思维过程伪造或推断为已观测。
