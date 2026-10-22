# Architecture Evolution Contract / 架构演化契约

Name / 名称: Architecture Evolution Exchange and Decision Contract / 架构演化交互与决策契约. Description / 说明: bind execution, evidence, evaluation, rollout and independent observation without conflating their authority or completion / 绑定执行、证据、评价、发布及独立观测，避免混淆各自权限与完成含义。

Pattern / 模式: `PATTERN_0054`; version / 版本: `0.2.0`; source version / 来源版本: `0.1.0`; status / 状态: `draft`; implementation status / 实现状态: `specification_only`; profile / 配置: `architecture_evolution/0.2.0`.

## Quick Navigation / 快速导航

[Bindings / 绑定](#bindings) · [States and completion / 状态与完成](#completion) · [Events / 事件](#events) · [Probe exchange / 探针交互](#exchange) · [Authority / 权限](#authority) · [Refinements / 细化](#refinements).

## Usage and Compatibility / 适用场景与兼容

Use with [E0–E9 execution / 执行](architecture-evolution-execution-flow.md), [AEP01–AEP10 probes / 探针](architecture-evolution-observability-probes.md) and [source map / 来源映射](architecture-evolution-source-map.json). Execution and probes can run independently. The adopting system owns actual dispatch, authorization, transactional state, metric calculations, evaluation and rollout; these documents do not implement them. / 配合执行、探针及来源映射使用，执行与探针可独立运行。采用系统负责真实派发、授权、事务状态、指标计算、评价和发布；本文档并未实现这些能力。

Keep `PATTERN_0052` and its [shared protocol / 共享协议](workflow-observability-probes.md) `0.8.0` unchanged. Namespaced `AEP*`/`AEM*` objects are dedicated specifications, not aliases for existing executable probes/calculators. Hosts must explicitly negotiate this profile and validate mappings for identities, states, evidence and control; unsupported profile/version is rejected, not silently downgraded. No existing shared runtime schema is presumed to accept the examples. / 保留既有探针及共享版本不变。专用名称空间下的探针指标是规格，不是既有可执行采集器计算器的别名。宿主须显式协商本配置并验证标识、状态、证据及控制映射；不支持的配置版本应拒绝，不得静默降级。不假定既有共享运行时结构接受本文示例。

<a id="bindings"></a>
## Required Objects and Bindings / 必需对象与绑定

Every evolution record, evaluation, probe exchange and decision carries the same six fields below. References use `{id, version, digest}` and resolve to immutable, access-controlled artifacts; digest proves bytes, not truth or authority. Explicit `null` means not created/not applicable with a reason, not successful completion. / 每条演化记录、评价、探针交互及决定均携带下列六字段。引用使用标识、版本、摘要三元组，并解析到不可变受控访问制品；摘要只证明字节，不证明事实或权限。显式空值表示未创建或有理由不适用，不表示成功。

| Field / 字段 | Meaning and gate / 含义与门槛 |
| --- | --- |
| `evolution_id` | Stable outer-loop identity; link predecessor ADR/evolution without reusing its ID. / 外环稳定标识，关联前驱 ADR 或演化但不复用其编号。 |
| `baseline_ref` | Frozen actual design and evidence; non-null by exit of E1 and before comparison. / 冻结实际设计及证据，E1 退出及对照前须非空。 |
| `candidate_ref` | Exact proposed delta and parent baseline; non-null for candidate evaluation or activation. Retain may refer to baseline with explicit no-change semantics. / 精确候选差异及父基线，候选评价或激活前须非空；保留可引用基线并明确无改动语义。 |
| `evaluation_plan_ref` | Frozen cases, criteria, uncertainty, budgets and evaluators; non-null before E6. / 冻结案例、口径、不确定性、预算及评价者，E6 前须非空。 |
| `release_ref` | Exact rollout/migration/rollback plan and authority binding; non-null before any activation. Retain with no rollout uses null plus rationale. / 精确发布迁移回退计划及权限绑定，任何激活前须非空；无发布的保留使用空值并附理由。 |
| `evidence_refs` | Sourced evidence list, allowed to be empty only while evidentiary conclusions remain unestablished. / 有来源证据清单；仅在尚未建立证据结论时允许为空。 |

Additional bindings / 补充绑定:

| Object / 对象 | Required content / 必需内容 |
| --- | --- |
| Inner run / 内环运行 | `task_id`, `run_id`, `workflow_id/version`, `scenario_id/version`, input/rule/model/prompt/tool/config versions, environment, start/end and business acceptance. Baseline and candidate cases use different run IDs. / 任务运行、工作流场景及相关输入规则模型提示工具配置版本、环境、起止和业务验收；基线候选案例使用不同运行号。 |
| Node / 节点 | Stable `node_id`, owner, structured inputs/outputs, evidence requirements, readiness, success/failure criteria, allowed effects and recovery. Each attempt has a new `attempt_id`. / 稳定节点号、责任人、结构化输入输出、证据要求、就绪成功失败条件、允许效果及恢复；每次尝试有新编号。 |
| Evidence / 证据 | `evidence_id`, source locator/identity/version, object binding, observed time, validity, method, evidence state, access scope and digest when available. Keep fact, calculation, inference, conflict, expired and unknown distinct. / 证据号、来源定位身份版本、对象绑定、观察时间、有效性、方法、证据状态、权限及可用摘要；区分事实计算推断冲突过期未知。 |
| Evaluation result / 评价结果 | `evaluation_id`, all six bindings, case and stratum, baseline/candidate run references, metric definition version, observed outcomes, exclusions, uncertainty, mandatory-gate findings and evaluator. / 评价号、六绑定、案例分层、基线候选运行、指标口径版本、实测结果、排除、不确定性、必需门发现及评价者。 |
| Release control / 发布控制 | `control_epoch`, `expected_state_revision`, current/target artifact, owner, authorization reference, cohort/exposure, admission, in-flight and migration policies, stop rules, rollback target and effect ledger. / 控制代次、预期状态修订、当前目标制品、责任人、授权引用、群组暴露、准入在途迁移策略、停止规则、回退目标及效果账本。 |
| ADR / 决策记录 | `decision_id/version`, six bindings, action, outcome, alternatives, causal hypothesis, public rationale, validation/release status, unresolved duties/owners and reevaluation time or trigger. / 决策版本、六绑定、改动类型、结果、备选、因果假设、公开理由、验证发布状态、未结职责责任人及复评时间或触发。 |

<a id="completion"></a>
## States and Completion / 状态与完成

State namespaces are separate. Node success cannot be copied into run completion, evolution phase or decision outcome. Every transition records actor, reason, evidence, previous/new state, time, revision and current control epoch where control is affected. / 状态名称空间分开，节点成功不能复制为运行完成、演化阶段或决策结果。每次迁移记录主体、原因、证据、前后状态、时间、修订，涉及控制时附当前代次。

| Namespace / 名称空间 | Values and rules / 值与规则 |
| --- | --- |
| `node_status` | `pending`, `running`, `succeeded`, `failed`, `skipped`, `waiting_data`, `waiting_approval`, `cancelled`, `rolled_back`. A justified skip must satisfy frozen rules; a rolled-back node is not business success. / 待执行、运行、成功、失败、跳过、等资料、等审批、取消、回滚；跳过须满足冻结规则，回滚节点不等于业务成功。 |
| `run_status` | `pending`, `running`, `waiting_data`, `waiting_approval`, `pending_acceptance`, `completed`, `failed`, `cancelled`, `handed_off`. Only `completed` implies passed business completion; `handed_off` requires evidence of receiver acceptance and actual responsibility transfer, and can still leave the business task incomplete. / 待启动、运行、等资料、等审批、待验收、完成、失败、取消、已交接；仅完成表示业务完成通过；已交接须有接收方接受及责任实际转移的证据，仍可能业务未完成。 |
| `evolution_stage` | `E0`–`E9`; a work location, not an outcome. / 工作阶段位置，不是结果。 |
| `evolution_status` | `open`, `investigating`, `evaluating`, `waiting_data`, `waiting_approval`, `observing`, `stopped`, `closed`. Closure requires a recorded decision and outstanding duties; it does not assert success. / 开启、调查、评价、等资料、等审批、观察、停止、关闭；关闭须有决定及剩余责任，不断言成功。 |
| `change_action` | `retain`, `repair`, `reorganize`, `simplify`, `retire`; chosen design intervention, never a pass/fail flag. / 保留、修复、重组、简化、退役；设计干预类型，不是通过失败标志。 |
| `decision_outcome` | `adopted`, `rolled_back`, `inconclusive`, or null before decision; apply the meanings below. / 已采纳、已回滚、无法定论，决定前为空；按下文解释。 |
| `effect_status` | `none_verified`, `applied`, `partial`, `unknown`, `compensated`; missing receipt alone gives no proof of no effect. / 已证实无效果、已生效、部分、未知、已补偿；缺回执不能证明无效果。 |

These are constrained state machines, not freely assignable labels. The table gives mandatory key transition guards; an adopting host defines the remaining legal transitions without bypassing these gates. Preserve frozen contracts and durable receipts at every transition. / 这些是受约束状态机，不是可任意赋值的标签。下表规定关键迁移的必需守卫，采用宿主补全其他合法迁移且不得绕过这些门；每次迁移保留冻结契约和持久回执。

| Transition / 迁移 | Required gate / 必需门 |
| --- | --- |
| Node `pending`/wait → `running` / 节点待执行或等待转运行 | Dependencies and missing conditions satisfied; live authority and budget valid; create attempt. / 依赖缺失条件满足，实时权限预算有效，创建尝试。 |
| Node `running` → `succeeded` / 节点运行转成功 | Local output/evidence/effect conditions pass; technical return alone is insufficient. / 局部输出证据效果条件通过，仅技术返回不足。 |
| Run `running` → `pending_acceptance` → `completed` / 运行转待验收再完成 | Required node inventory reconciled, then every business completion gate passes. / 先核对必需节点清单，再通过全部业务完成门。 |
| Run → `handed_off` / 运行转已交接 | Delivered version, receiving actor, acceptance and responsibility-transfer receipt agree. Sending alone leaves the current owner responsible. / 交付版本、接收主体、接受及责任转移回执一致；仅发送则原负责人继续负责。 |
| Evolution `evaluating` → `observing` / 演化评价转观察 | E6 validation passes and E7 admits the exact tested versions under current authority/epoch, including a fresh dependency-version check. Missing evidence → `waiting_data`; unsupported conclusion → close only as `inconclusive`. / E6 验证通过且 E7 在当前权限代次准入精确已测版本，含重新读取核验依赖版本；缺证据转等资料，无依据结论仅可无法定论关闭。 |
| Evolution `observing` → `stopped` → `closed` / 演化观察转停止再关闭 | Stop receipt, in-flight reconciliation/recovery ownership, then E9 outcome and duties recorded. Closing never fabricates completed effects. / 记录停止回执、在途核对恢复责任，再记录 E9 结果与职责，关闭不能伪造效果已完成。 |
| Evolution `observing` → `closed` / 演化观察转正常关闭 | E8 required observation, release and effect-closure gates pass; E9 records `adopted` with evidence and reassessment triggers. / E8 必需观察、发布及效果闭环门通过，E9 记录有证据及复评触发的已采纳决定。 |
| Evolution investigation/evaluation → `closed` without rollout / 演化调查评价不发布而关闭 | E9 records justified `retain/adopted` with rollout inapplicability, or `inconclusive` with limitations and duties; no unsupported success claim. / E9 记录有依据的保留采纳及发布不适用，或含限制职责的无法定论；不得无依据宣称成功。 |
| Any wait → prior active state / 等待恢复 | Verify the missing condition and all version/authority bindings again; changed baseline/candidate/plan returns to applicable E1/E4/E5–E6 gates. / 重新核验缺失条件及版本权限绑定；基线候选计划变化回适用的 E1/E4/E5–E6 门。 |

`adopted` means evidence supports the selected design and all applicable adoption/release gates passed. For `retain`, it means an evidence-backed decision to keep the baseline with explicitly inapplicable rollout steps. `rolled_back` means a previously activated candidate has been verifiably reverted; rejected pre-release candidates are not rolled back. `inconclusive` means available evidence does not support a defensible adoption claim; record whether the candidate was never activated, is contained or is awaiting recovery. An evaluated rejected candidate may yield `retain/adopted` only with independent evidence supporting baseline retention; otherwise use inconclusive. / 已采纳表示证据支持所选设计且全部适用采纳发布门通过；保留时表示有证据地维持基线，并明确发布步骤不适用。已回滚表示曾激活候选已确认撤回，发布前被拒候选不算回滚。无法定论表示现有证据不支持可辩护的采纳声明，须注明候选未激活、已遏制或待恢复。候选被否后，仅有独立证据支持基线时可记保留／已采纳，否则无法定论。

| Completion / 完成类型 | Necessary conditions / 必要条件 | What it does not imply / 不代表 |
| --- | --- | --- |
| Diagnostic / 诊断完成 | Bounded question, linked available events, fact/hypothesis separation, explicit gaps, reproducible metric definitions and sourced recommendations; insufficient essential reconstruction evidence yields partial, not complete. / 问题有界、可用事件关联、事实假设分开、缺口明确、指标可复算及建议有依据；缺必要重建证据则部分完成。 | Business success, confirmed root cause, validation or authority. / 业务成功、根因已确认、验证或权限。 |
| Business / 业务完成 | Required nodes completed or validly skipped; required outputs/evidence/rules/authority pass; no unresolved material conflict, high-risk exception or required external-effect uncertainty; necessary audit saved. / 必需节点完成或合法跳过，输出证据规则权限通过，无未解决重大冲突、高风险异常或必需外部效果未知，必要审计已保存。 | Pausing or handing off a high-risk exception is containment, never business completion. / 暂停或转交高风险异常只是遏制，不是业务完成。 |
| Validation / 验证完成 | Frozen comparable plan executed; old failures addressed, old successes within limits, high-risk and counterexample gates pass, uncertainty/cost/latency assessed and unresolved blockers absent. / 冻结可比计划已执行，旧失败解决、旧成功在界限内、高风险反例门通过，已评估不确定性成本延迟且无未解决阻断。 | Production deployment, observed release health or universal safety. / 生产已部署、发布健康或普遍安全。 |
| Release / 发布完成 | Authorized exact candidate effective in declared scope; migration and in-flight policies satisfied; required observation window/sample and gates pass; necessary reconciliation/compensation duties closed with receipts. / 受权精确候选在声明范围生效，迁移在途策略满足，必需观察窗口样本及门通过，必要核对补偿职责有回执关闭。 | Success of all historical or future business tasks; rollback alone cannot pass it. / 所有历史未来业务任务成功，单纯回滚不能通过。 |

Use `pending`, `passed`, `failed` or `not_applicable` plus reason/evidence for each completion gate. Mandatory business evidence missing blocks that gate, even if a probe reports complete; optional observation gaps do not invalidate independently verified business evidence. A mandatory observation requirement must be explicitly declared in the applicable frozen policy, not invented after an outage. / 各完成门使用待定、通过、失败或不适用，并带原因证据。缺必需业务证据阻断对应门，即使探针已完成；可选观测缺口不推翻独立核验业务证据。强制观测要求须在适用冻结策略明确声明，不能在探针故障后临时添加。

<a id="events"></a>
## Event Envelope and Evidence Repair / 事件包络与证据修复

Events are append-only, source-authenticated records with `profile`, `event_id`, `event_type`, six bindings, producer ID/epoch, sequence number, occurred/observed timestamps with offset and source evidence. Add run/node/attempt/span/parent-span, causal parents, workflow/rule/config versions, state revision, control epoch and safe input/output references where applicable. Pure evolution records need no fabricated business run or node ID. / 事件为仅追加且来源认证的记录，包含配置、事件号类型、六绑定、生产者身份代次、序号、带时区的发生观察时间及来源证据；按需加入运行节点尝试跨度父跨度、因果父事件、工作流规则配置版本、状态修订、控制代次及安全输入输出引用。纯演化记录无需虚构业务运行节点号。

Sequence numbers order only one producer epoch; ingestion time is not causal order. Deduplicate exact event/digest pairs within authenticated producer scope; changed content under the same ID is an integrity conflict. Preserve late evidence, clock uncertainty and competing interpretations; an unresolvable first deviation is an interval, not a fabricated node. / 序号只排序同一生产者代次，摄取时间不是因果顺序。在认证生产者范围内按事件摘要去重；同号改内容是完整性冲突。保留迟到证据、时钟不确定性及其他解释，无法定位首偏差时给区间，不伪造节点。

Corrections append a new revision with `supersedes_ref`, original source and reason; never overwrite history or reclassify inference as observed truth. Missingness distinguishes `not_collected`, `collection_failed`, `not_generated`, `not_received`, `unlinked`, `expired`, `conflict`, `unavailable`, `forbidden`, `unknown` and evidence-backed `not_applicable`; zero is a measured value. Source verification and execution-side revalidation are required before a repaired observation supports a business decision. / 更正追加带前驱引用、原来源和原因的新修订，不覆盖历史或把推断重标成实测事实。缺失区分未采集、采集失败、未生成、未收到、未关联、过期、冲突、不可获得、无权、未知及有依据不适用，零值必须实测。补全观察用于业务决定前，须核验来源并由执行侧复验。

<a id="exchange"></a>
## Probe Request and Result / 探针请求与返回

The [probe request/return templates / 探针请求返回模板](architecture-evolution-observability-probes.md#templates) are the single normative field-shape definition for this profile; this contract defines binding semantics, gates and rejection rules. They are specifications, not executable schemas. `target_ref` binds the exact artifact inspected; `expected_control_epoch` supports rejecting stale control recommendations and grants no authority. Pre-creation null bindings require per-field reasons and cannot pass a stage requiring that artifact. / 探针模板是本配置唯一规范字段形状来源，本契约规定绑定语义、门槛及拒绝规则；两者均为规格，不是可执行 Schema。目标引用绑定被查精确制品，预期控制代次用于拒绝陈旧控制建议，不授予权限。产生前空引用须逐字段说明理由，不能放行要求该制品的阶段。

Response `status` is `complete`, `partial` or `unavailable` for the requested diagnostic scope, never business/evaluation/release success. A forbidden read appears as a reason in `missing_evidence`; it cannot be retried under invented authority. Results echo all bindings; late or mismatched versions remain historical observations and cannot pass a newer gate. / 返回状态仅为请求诊断范围的完成、部分或不可得，不表示业务评价发布成功。无权读取在缺失原因中记录，不得虚构权限重试。结果回显全部绑定；迟到或版本失配只保留为历史观察，不能放行新版门。

An enrichment proposal binds request/report, target revision/digest, source, allowed observation field, value type, evidence state and method. The receiver authenticates, checks exact bindings, then appends acceptance/rejection with resulting observation revision. Exact duplicate requests reuse the receipt; same ID with different content is rejected. Enrichment cannot mutate goals, rules, plans, approvals, authority, business state, effect ledger or completion. Late contradictory evidence can reopen an observation and trigger authorized revalidation, but never silently rewrite an adopted decision. / 补全提案绑定请求报告、目标修订摘要、来源、允许观察字段、值类型、证据状态及方法。接收方认证并核对精确绑定后，追加接受拒绝及结果观察修订；完全重复幂等复用回执，同号异内容拒绝。补全不得修改目标规则计划审批权限、业务状态、效果账本或完成状态。迟到矛盾证据可重开观察并触发受权复验，但不暗改已采纳决定。

<a id="authority"></a>
## Authority, Concurrency and Recovery / 权限、并发与恢复

The probe defaults to report-only. Read permissions are independently checked at dispatch with task/tenant/source scope, expiry, query and cumulative cost limits. A recommendation to continue, pause, release, roll back, notify or compensate is not authorization. Actual control belongs to execution/governance and must match current authority, concrete target, immutable version, risk limits and control epoch; an already granted valid authorization need not be requested again. / 探针默认仅报告；读取须在派发时独立核对任务租户来源范围、有效期、查询及累计成本限制。继续、暂停、发布、回退、通知或补偿建议不是授权。真实控制归执行治理，须匹配当前权限、具体对象、不可变版本、风险限额及控制代次；已有有效授权无需重复申请。

Hosts atomically compare expected revision/epoch and commit the accepted transition, with durable action intent, idempotency and receipts. A stale worker cannot change current state. An irreversible external call already in flight may still complete after revocation; observe and reconcile its effect, preserve reservations where required, and apply authorized compensation separately. Code rollback, traffic rollback, data restoration and effect compensation have separate receipts and success conditions. / 宿主原子比较预期修订代次并提交接受的迁移，持久保存动作意图、幂等及回执。旧工作者不能改当前状态，已在途不可逆外部调用仍可能在收权后完成；须观察核对效果，按需保留预留并另行受权补偿。代码回退、流量回退、数据恢复及效果补偿分别具备回执和成功条件。

Every release declares old/new contract compatibility, migration and in-flight policies, rollback target validity and recovery ownership. Keep old readers/writers isolated until their policy finishes; never map old fields or terminal states onto new meanings without a versioned adapter and validation. If existing runtime support is absent, the deliverable remains a specification and integration gap, not a simulated successful deployment. / 每次发布明确旧新契约兼容、迁移在途策略、回退目标有效性及恢复责任。旧读写者按策略隔离至完成；未经版本适配验证，不能把旧字段终态映射成新含义。既有运行时不支持时，交付仍是规格与接入缺口，不是模拟的成功部署。

Release admission must reread actual tool/model/rule/configuration/permission versions against the frozen evaluation dependency snapshot. A relevant mismatch, even with unchanged candidate digest, sets the affected completion gate to `pending` with reason `stale_dependency` and blocks activation until newly bound evaluation or scoped compatibility revalidation passes. Keep original results immutable; a changed external dependency is not validated merely by unchanged local bytes. / 发布准入须重读实际工具模型规则配置权限版本并核对冻结评价依赖快照。相关不符即使候选摘要不变，也须将对应完成门置为待定，原因为 `stale_dependency`，在新绑定评价或范围化兼容复验通过前阻止激活。原结果不可变，外部依赖变化不能凭本地字节不变而视为已验证。

<a id="refinements"></a>
## Source Refinements and Acceptance / 来源细化与验收

| Source ambiguity / 来源歧义 | Normative refinement / 规范细化 |
| --- | --- |
| A task can complete after high-risk exceptions are paused or handed off. / 高风险异常暂停或转交后可业务完成。 | Containment/handoff is separate; unresolved high-risk exceptions block original business completion. / 遏制交接单列；未解决高风险异常阻断原业务完成。 |
| Node states and task run states share one list. / 节点状态与任务运行状态容易混用。 | Use distinct namespaces and versioned transitions; rolled-back node does not imply completed run. / 使用独立名称空间和版本化迁移，节点回滚不代表运行完成。 |
| General workflow execution and evolution appear in one sequence. / 通用执行与演化混在一组步骤中。 | Preserve inner-loop task contract; E0–E9 handles design changes across runs. / 保留内环任务契约，E0–E9 处理跨运行设计改动。 |
| “Complete evidence” may include all optional telemetry. / 补全证据可能被理解为全部可选遥测。 | Only declared mandatory evidence blocks the affected gate; record optional gaps and claim limitations. / 仅声明必需证据阻断对应门，可选缺口记录为结论限制。 |
| Old failures and successes suffice for comparison. / 仅旧失败与旧成功用于对照。 | Add high-risk and counterexample families, preregister comparability and uncertainty. / 增补高风险反例，预设可比性及不确定性。 |
| Rollback suggests reversal of every effect. / 回滚容易被理解为撤销一切效果。 | Separate design rollback, migration recovery, external-effect reconciliation and authorized compensation. / 分开设计回退、迁移恢复、外部核对及受权补偿。 |

Use [AET-01–AET-14 / 验收场景](architecture-evolution-execution-flow.md#acceptance) for adoption checks and the independent probe specifications for measurement. All scenarios remain `not_executed`. Tests of document structure, IDs, links or registry consistency establish asset quality only; host integration, control and business outcomes require separate actual evidence. / 采用检查使用执行文档 14 项验收场景，测量使用独立探针规格。全部业务场景仍未执行。文档结构、编号、链接及注册一致性检查只证明资产质量；宿主接入、控制及业务结果须另有真实证据。

Collect the minimum public evidence needed, prefer references/redacted summaries, enforce original access/retention rules and auditable deletion where required. Never collect secrets, unnecessary personal data or private chain-of-thought. / 仅采集必要公开证据，优先引用及脱敏摘要，落实原访问保留规则及必要的可审计删除；不采集秘密、无关个人信息或私密思维过程。
