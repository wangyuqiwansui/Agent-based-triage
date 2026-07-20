# Complexity-Based Routing / 复杂度路由 Observability Metrics / 可观测性指标

Pattern ID / 模式 ID: `PATTERN_0032`

Observability revision / 可观测性修订: `0.4.0`

Cell / 交织点: reasoning-routing / 推理 x 路由
Capability / 能力: Reasoning / 推理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-routing.md](reasoning-routing.md)
Shared Probe Suite / 共享探针套件: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)
Metric Registry / 指标注册表: [`metric_registry.json`](../../../runtime/metric_registry.json)

## Quick Navigation / 快速导航

- [Observability Metrics / 可观测性指标](#observability-metrics--可观测性指标)
- [Observation Contract / 观测契约](#observation-contract--观测契约)
- [Field State And Completion / 字段状态与补全](#field-state-and-completion--字段状态与补全)
- [Metric Semantics / 指标语义](#metric-semantics--指标语义)
- [Alerts And Control / 告警与控制](#alerts-and-control--告警与控制)
- [Counterfactual Audit / 反事实审计](#counterfactual-audit--反事实审计)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Complexity-Based Routing / 复杂度路由 improves the workflow after selection or application. / 使用以下指标观察 Complexity-Based Routing / 复杂度路由 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `route_stability_rate` (no route-insufficiency switch; explicitly not accuracy), `outcome_route_accuracy` (outcome-backed or independently audited sufficiency), `underroute_rate`, `overroute_rate`, and per-tier validated acceptance rate. / `route_stability_rate`（未因路由不足而换路，明确不等于准确率）、`outcome_route_accuracy`（由真实结果或独立审计支撑的充分性）、欠路由率、过路由率和各档位验证后采纳率。
- 时延指标 / Latency Metrics: classifier decision latency, per-tier end-to-end latency, and escalation delay (time lost when a request bounces from a low tier to a higher one). / 分类器决策时延、各档位端到端时延、升级延迟（请求从低档反弹到高档损失的时间）。
- 成本指标 / Cost Metrics: token spend per tier, blended cost per request versus single-deep-path baseline (article anchor: RouteLLM ~85% reduction), and misroute cost (wasted deep-tier tokens plus rework tokens from failed cheap-tier runs). / 各档位 token 消耗、单请求混合成本对比单一深路径基线（论文锚点：RouteLLM 约降 85%）、误路由成本（浪费的深档 token 加低档失败返工 token）。
- 风险指标 / Risk Metrics: escalation-loop count (same request escalating more than once, watch `FAIL_0007`), high-impact requests served by System 1, router abstention rate, and forced-route count when required typed signals were missing or unknown. / 升级循环次数（同一请求升级超过一次，对应 `FAIL_0007`）、高影响请求被直觉档处理的数量、路由弃权率，以及必需类型化信号缺失或未知时仍强制路由的次数。
- Trace 指标 / Trace Metrics: route decision record completeness (mode, topology, typed signals, policy version, reason codes, signal fingerprint, and abstention), escalation event coverage, and misroute audit closure rate. / 路由决策记录完整率（模式、拓扑、类型化信号、策略版本、原因码、信号指纹和弃权状态）、升级事件覆盖率、误路由审计闭环率。

### Required Probe Coverage / 必需探针覆盖

Enable task identity (`PROBE_0001`), contract completeness (`PROBE_0002`), route decision (`PROBE_0003`), budget and resources (`PROBE_0004`), step closure (`PROBE_0005`), evidence chain (`PROBE_0006`), drift (`PROBE_0010`), validation (`PROBE_0011`), stop and escalation (`PROBE_0012`), outcome (`PROBE_0013`) for any accuracy, under-route, over-route, or acceptance claim, privacy and governance (`PROBE_0014`), and probe self-health (`PROBE_0015`). / 启用任务身份、契约完整性、路由决策、预算与资源、步骤闭环、证据链、漂移、验证、停止升级、结果回接（任何准确率、欠路由、过路由或采纳率判断均必需）、隐私治理和探针自健康探针。

Record initial and final modes, observable routing signals, route reason, switch trigger, budget impact, and whether a switch was caused by route insufficiency or an external environment change. If no explicit router event exists, report only `observed_mode`; do not infer design intent. / 记录初始与最终模式、可观测路由信号、路由原因、换路触发、预算影响，以及换路由路由不足还是外部环境变化引起。不存在显式路由事件时，只报告 `observed_mode`，不得推断设计意图。

Version every metric definition and bucket by scene, risk, initial/final mode, evidence grade, validator, model, tool, and outcome availability. Treat missing route reasons as missing, not as wrong or correct routes. / 每个指标口径版本化，并按场景、风险、初始/最终模式、证据等级、验证器、模型、工具和后验可用性分桶。路由原因缺失应保留为缺失，不计为正确或错误。

## Observation Contract / 观测契约

Observe the task atom and the run separately. One run may contain several task atoms with different workflow lanes and reasoning routes; never use run count as the denominator for an atom metric without an explicit aggregation rule. / 分别观测任务原子与运行。一次运行可能包含多个具有不同流程车道和推理路由的任务原子；没有显式聚合规则时，禁止用运行数作为原子指标分母。

| Stage / 阶段 | Required events / 必需事件 | Required route fields / 必需路由字段 |
| --- | --- | --- |
| Normalization / 标准化 | `task_normalized` | Task/run identity, task-atom identity when available, frozen input and policy bindings. / 任务/运行标识、可用时的任务原子标识、冻结输入与策略绑定。 |
| Initial route / 首次路由 | Committed `workflow_route_envelope` plus `route_selected` for the reasoning subset / 已提交工作流路由信封及推理子集的路由已选择事件 | Workflow/task/run/scene and task-atom identity, workflow/reasoning policy and adapter bindings, all 15 typed signals with provenance, fingerprints, lane, action gate, blockers, disposition, reasons, abstention, configuration, budgets, validators, and optional run-graph binding. / 工作流/任务/运行/场景及任务原子标识、流程/推理策略与适配器绑定、15 项带来源信号、指纹、车道、行动门禁、阻断项、处置、原因、弃权、配置、预算、验证器及可选运行图绑定。 |
| Contract binding / 契约绑定 | `contract_established` for executable routes / 可执行路由发送契约已建立 | Exact route-decision and normalized-input bindings. / 精确路由决定与标准化输入绑定。 |
| Switch or gate revision / 换路或门禁修订 | Committed parent `workflow_route_revised`; additionally `mode_switched` when reasoning topology changes / 已提交父级工作流路由修订；推理拓扑变化时另发换路事件 | Previous/current envelope hashes and revisions, trigger class/direction/reason/evidence, hysteresis, budget impact, unfinished work, actor/authority, route states, and optional switch-event binding. / 前后信封哈希与修订号、触发类别/方向/原因/证据、迟滞、预算影响、未完成工作、执行者/权限、路由状态及可选换路事件绑定。 |
| Advice response / 建议响应 | `feedback_updated` | Advice binding, accepted/partially accepted/rejected/expired response, authority, reason. / 建议绑定、采纳/部分采纳/拒绝/过期响应、权限、原因。 |
| Validation / 验证 | `validation_completed` | Candidate/contract/evidence/validator bindings, authoritative result and time. / 候选/契约/证据/验证器绑定、权威结果与时间。 |
| Outcome / 后验 | `outcome_recorded` | Trustworthy outcome identity, source, time, original route and validators, rework or false release. / 可信后验标识、来源、时间、原路由与验证器、返工或错误放行。 |
| Terminal / 终态 | `run_ended` | Initial/final configuration, switch chain, stop/escalation reason, terminal state, budget settlement. / 初始/最终配置、换路链、停止/升级原因、终态、预算结算。 |

Use [`reasoning-event.schema.json`](../../../schemas/reasoning-event.schema.json) for the strict reasoning subroute, [`workflow-route-envelope.schema.json`](../../../schemas/workflow-route-envelope.schema.json) for the composite workflow decision, and [`workflow-route-revision.schema.json`](../../../schemas/workflow-route-revision.schema.json) for the append-only parent revision. [`workflow_route_ledger.py`](../../../runtime/workflow_route_ledger.py) provides crash-safe single-writer JSONL, while [`workflow_route_sqlite_ledger.py`](../../../runtime/workflow_route_sqlite_ledger.py) provides transaction-backed multi-writer commit, recovery, migration, and bounded storage health for a single-node deployment. Both persist the same envelope and revision atomically; never add undeclared workflow fields to the strict reasoning event. / 严格推理子路由使用推理事件 Schema，复合工作流决定使用工作流路由信封 Schema，追加式父修订使用工作流路由修订 Schema。JSONL 路由账本提供崩溃安全单写者能力，SQLite 路由账本为单节点部署提供事务型多写者提交、恢复、迁移与有限存储健康检查；二者均以相同语义原子持久化信封与修订。不得向严格推理事件添加未声明工作流字段。

### Field State And Completion / 字段状态与补全

- Preserve `observed`, `observed_zero`, `missing`, `unknown`, `not_applicable`, `computed`, and `insufficient_sample` semantics; never collapse them into null or zero. / 保留已观测、观测零值、缺失、未知、不适用、已计算与样本不足语义；不得压缩成 null 或零。
- Route reason can be completed only from router I/O or a signed workflow report. If unavailable, keep `observed_mode` and missing reason; topology reconstruction never proves design intent. / 路由原因只能从路由器输入输出或已签名流程报告补全；不可得时保留观测模式与缺失原因，拓扑重建不能证明设计意图。
- Policy, permission, approval, target identity/version, action confirmation, and compensation success cannot be completed from statistics or model estimates. / 策略、权限、审批、目标标识/版本、动作确认和补偿成功不得通过统计或模型估计补全。
- A completion record carries source, version, method, valid/capture time, input references, confidence, merge rule, conflict state, and reversibility. Derived data never overwrites confirmed source facts. / 补全记录携带来源、版本、方法、有效/采集时间、输入引用、置信度、合并规则、冲突状态和可撤销性；推导数据绝不覆盖已确认源事实。

## Metric Semantics / 指标语义

Implemented definitions remain authoritative in [`metric_registry.json`](../../../runtime/metric_registry.json). The routing metrics below are implemented diagnostics and are not gate eligible by default. / 已实现定义以指标注册表为准；下列路由指标均已实现为诊断指标，默认不可用于门控。

```text
route_stability_rate
= runs_without_route_insufficiency_switch
  / runs_with_valid_initial_route

outcome_route_accuracy
= correct_routes_with_outcome
  / routed_runs_with_outcome

outcome_linkage_coverage
= trustworthy_linked_route_outcomes
  / completed_route_atoms_eligible_for_outcome_linkage

underroute_rate
= atoms_succeeding_only_after_route_insufficiency_upgrade
  / completed_atoms_with_auditable_route_outcome

overroute_rate
= audited_atoms_where_a_lighter_route_meets_the_same_validators
  / atoms_in_a_valid_counterfactual_audit_sample

route_abstention_rate
= abstained_route_decisions
  / route_decisions_with_complete_identity

route_oscillation_rate
= atoms_exceeding_scene_switch_or_reversal_threshold
  / atoms_with_complete_switch_chain

forced_route_with_missing_signal_rate
= executable_routes_with_required_signal_missing_or_unknown
  / executable_routes
```

Interpretation rules / 解释规则：

1. `route_stability_rate` is operational stability, not correctness. A stable route may still be wrong. / 路由稳定率是运行稳定性而非正确性；稳定路由仍可能错误。
2. `outcome_linkage_coverage` measures diagnostic completeness; `outcome_route_accuracy`, `underroute_rate`, and `overroute_rate` additionally require `PROBE_0013`, trustworthy outcome linkage or independent audit, finalized windows, and explicit exclusions. / `outcome_linkage_coverage` 衡量诊断完整度；后验路由准确率、欠路由率和过路由率还要求结果回接探针、可信后验关联或独立审计、封窗及显式排除项。
3. Over-route audit must replay or compare against the same input, evidence, policy, validator set, and outcome boundary. A cheaper token count alone does not prove over-routing. / 过路由审计必须在相同输入、证据、策略、验证器集合和结果边界下回放或对照；token 更少本身不能证明过路由。
4. Under-route labeling distinguishes route insufficiency from later external-state changes, stale evidence, tool outage, and policy revision. / 欠路由标签必须区分路由不足与后续外部状态变化、证据过期、工具故障和策略修订。
5. Route confidence calibration, if captured from a legacy or upstream classifier, is diagnostic telemetry only. It cannot release, authorize, prove evidence sufficiency, or replace an outcome. / 若从遗留或上游分类器采集路由置信度，其仅为诊断遥测，不得放行、授权、证明证据充分或替代后验。

### Required Buckets And Publication / 必需分桶与发布

Bucket by `scene_id`, workflow and route-policy version, task intent, execution lane when available, risk, action-risk class when available, initial/final execution mode, evidence state/grade, validator profile, model/tool version, human-gate involvement, outcome availability, and observation deployment mode. / 按场景标识、流程与路由策略版本、任务意图、可用时的执行车道、风险、可用时的动作风险类别、初始/最终执行模式、证据状态/等级、验证器档位、模型/工具版本、人工闸门参与、后验可用性和观测部署模式分桶。

Published metrics require a reproducible envelope: metric ID/version, exact calculation inputs and hash, numerator, denominator, exclusion counts, buckets, finalized watermark window, sample size, completeness, source mix, required probe health, and uncomputable reason. Mixed policy versions are separate buckets, never silently averaged. / 发布指标需要可复现信封：指标标识/版本、精确计算输入及哈希、分子、分母、排除计数、分桶、已封窗 watermark、样本量、完整性、来源构成、必需探针健康及不可计算原因。混合策略版本必须分桶，禁止静默平均。

## Alerts And Control / 告警与控制

Hard alerts or authorized inline blocks require no statistical baseline for: prohibited or permission-denied work routed to execute; required signal missing/unknown on an executable route; insufficient/unavailable/untrusted critical evidence falling through to reasoning; high-risk or irreversible action missing validator, approval, or owner; action proceeding from a reasoning decision without mechanical checks; same fingerprint producing different routes; unsupported de-escalation; switch cap or budget exceeded; or terminal state missing a reason. / 以下情况无需统计基线即可产生严重告警或已授权内联阻断：禁止或权限拒绝任务被路由为执行；可执行路由缺少/未知必需信号；关键证据不足/不可得/不可信却落入推理；高风险或不可逆动作缺少验证器、审批或责任人；仅凭推理决定、未做机械检查就行动；相同指纹产生不同路由；无依据降档；换路或预算越界；终态缺少原因。

Probe advice may request complement evidence, wait, retry collection, revalidate the object, switch mode, lower concurrency, escalate, stop, or compensate. The workflow records accepted, partially accepted, rejected, human-pending, or expired response. Advice never directly changes business state. / 探针建议可以请求补证、等待、重试采集、重验对象、切换模式、降低并发、升级、停止或补偿。流程记录采纳、部分采纳、拒绝、待人工或过期响应。建议绝不直接改变业务状态。

## Counterfactual Audit / 反事实审计

Sample routed-low and routed-high atoms by scene and risk. Freeze the original input, evidence, policy, validators, tool/model versions, and outcome boundary; replay only in an isolated evaluation environment with no side effects. Label `underroute`, `overroute`, `appropriate`, or `indeterminate`, preserve reviewer/authority and rationale, and keep indeterminate samples out of accuracy numerators. Policy auto-tuning remains disabled until outcome-linkage coverage, sample minimum, drift controls, and an accountable owner are approved. / 按场景与风险抽样低档和高档原子。冻结原输入、证据、策略、验证器、工具/模型版本和结果边界；只在无副作用的隔离评估环境回放。标注欠路由、过路由、合适或不可判定，保留评审者/权限和理由，并将不可判定样本排除在准确率分子之外。在后验关联覆盖率、最小样本、漂移控制和责任人获批前，禁用策略自动调优。

### Default Gate Suggestions / 默认门控建议

- Monitor diagnostic `route_stability_rate` only as operational stability; promotion requires an owned threshold, minimum sample, and approval evidence. / 仅将诊断性 `route_stability_rate` 解释为运行稳定性；晋升门控要求负责人阈值、最小样本与审批证据。
- Keep `outcome_route_accuracy`, `underroute_rate`, and `overroute_rate` diagnostic until implemented `outcome_linkage_coverage` meets an owned minimum threshold; keep coverage itself diagnostic until promotion is approved. / 在已实现的 `outcome_linkage_coverage` 达到负责人最低阈值前，`outcome_route_accuracy`、`underroute_rate` 与 `overroute_rate` 仅作诊断；覆盖率本身在晋升获批前也保持诊断。
- Require a trace entry for every escalation or de-escalation. Allow an explicit switch to direct or deterministic work after critical uncertainty is resolved; block unrecorded or unsupported de-escalation. / 每次升级或降档都必须留 Trace 记录。关键不确定性解决后允许显式切换到直接或确定性工作；阻断未记录或无证据支持的降档。
