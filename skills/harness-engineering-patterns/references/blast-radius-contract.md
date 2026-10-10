# Blast Radius Control Contract / 爆炸半径控制共享契约

Version / 版本: `0.1.0`; status / 状态: `draft`; implementation / 实现: `specification_only`.

## Purpose and Authority / 用途与权限

Use with the [execution flow](blast-radius-execution-flow.md) and [independent probes](blast-radius-observability-probes.md) for `PATTERN_0050`, `CELL_GOVERNANCE_HIERARCHY`. This specializes the [governance contract](governance-contract.md); it does not install a ledger, gateway, production probe or normative JSON Schema. Source aliases and interpretation changes live in the [source map](blast-radius-source-map.json). / 本契约用于现有爆炸半径控制模式，细化治理共享契约，与执行流程及独立探针配合使用；不代表已安装账本、网关、生产探针或规范 JSON Schema。来源别名及解释修订见来源映射。

Approval authorizes the exact proposed action; containment bounds its cumulative consequences. Sandbox isolation, business correctness and approval remain separate controls. Only the independent control plane changes hard limits, credentials and stop policy. The ledger owns balances, the gateway owns submission, and an authorized reconciler settles outcomes from independent evidence. Workers cannot directly access external privileged credentials. Probes append observations and proposals, never permissions or business truth. / 审批授权精确动作提案，遏制限制累计后果；沙箱、业务正确性和审批分别控制。仅独立管理面修改硬上限、凭据和停止策略；账本管理余额，网关提交，有权对账者依据独立证据结算。Worker 不得直取外部高权限凭据；探针只追加观察和建议，不产生权限或业务真值。

## Identity and Scope / 身份与范围

Authenticate tenant, principal and source at trusted ingress before reference resolution. Use nonempty string IDs and versions, nonnegative integer revisions and timezone-qualified timestamps; absent facts remain explicit null with a reason. Missing required control fields fail closed; empty allowlists deny all, and null never means unlimited. / 在可信接入验证租户、主体和来源后再展开引用。标识及版本用非空字符串，修订用非负整数，时间带时区；缺失事实明确为空并说明原因。必需控制字段缺失时阻断；空允许列表代表全部拒绝，null 不代表无限制。

| Binding / 绑定 | Meaning and rule / 含义与规则 |
| --- | --- |
| `tenant_id`, `principal_id`, `account_scope`, `root_envelope_id` | Trusted business subject, resource, currency/unit and policy window select aggregate accounts; renaming a run cannot reset subject/tenant exposure. / 由可信业务主体、资源、币种单位和策略窗口选择聚合账户，改运行名不能重置主体或租户暴露。 |
| `trace_id`, `run_id`, `parent_run_id`, `task_id`, `step_id`, `agent_id`, `worker_id` | Correlation only; not grants. Recovery links the original root. / 只用于关联，不授予权限；恢复关联原根信封。 |
| `envelope_id`, `parent_envelope_id`, `reservation_id` | One reservation funds exactly one child; no cycles or multiple parents. / 一个预留只供一个子信封，不允许循环或多父。 |
| `effect_intent_id`, `idempotency_key`, `parameter_digest` | One durable logical effect across attempts, callbacks, restarts and gateway delivery; uniqueness is tenant + external account/system + intent and key, not merely run-local. Bind canonical full action, object, units and proposal digest. / 跨尝试、回调、重启及网关投递稳定的逻辑效果，按租户、外部账户系统、意图和键持久唯一，不能仅运行内去重；绑定完整规范动作、对象、额度和提案摘要。 |
| `permit_id`, `holder_id`, `control_epoch`, `expires_at` | Nontransferable admission bound to an authenticated holder and current fence; at most one logical effect. / 不可转让许可绑定认证持有者及当前围栏，最多对应一个逻辑效果。 |
| `proposal_digest`, `approval_ref`, `policy_version`, `profile_version`, `envelope_revision` | Approval, envelope, permit, actual request and receipt must agree on versioned action and scope. Canonical encoding/hash version is fixed; a digest alone is not authorization. / 审批、信封、许可、实际请求和回执须匹配版本化动作及范围；固定规范编码与哈希版本，摘要本身不等于授权。 |
| `event_id`, `source_id`, `source_sequence`, `ledger_revision` | Immutable event deduplication and causal ordering, independent of effect idempotency. Same identity with divergent bytes is a conflict. / 不可变事件去重及因果排序独立于效果幂等；同标识异内容为冲突。 |

Effective scope is the intersection of hard, identity, task, capability, context, applicable approval and evidence-supported scopes. Set restrictions intersect; comparable numeric caps take the minimum; explicit denial vetoes. Noncomparable units or unresolved critical conflicts block admission. Evidence may narrow autonomy; widening requires a valid scoped independent grant and never changes the hard envelope. / 有效范围取硬边界、身份、任务、能力、上下文、适用审批及证据范围交集；集合取交集，可比数值上限取最小值，显式禁止一票否决。单位不可比或关键冲突未决时阻断；证据可收紧自主范围，放宽须有有效独立范围授权且不能改硬信封。

## Accounting Model / 记账模型

Keep money in integer minor units with currency, quantities in named original units and percentages as fixed-point ratios. No binary floating-point money or exchange between dimensions. Each dimension declares `cumulative`, `windowed`, `gauge`, `set` or `depth` semantics, scope and window. / 金额按币种用最小单位整数，数量保留具名原始单位，比例使用定点数；禁止浮点金额和维度间兑换。每个维度声明累计、窗口、瞬时、集合或深度语义、作用域与窗口。

For each additive cumulative dimension at each envelope, maintain mutually exclusive buckets: / 对每个信封的每个可加累计维度，维护互斥账户：

```text
limit = available + child_allocated + issued + in_flight + unknown + committed
all buckets >= 0
child_allocated = sum(active child liabilities)
```

`issued` is already occupied. A parent's `child_allocated` includes each child's whole unreturned allocation, including descendant use; parent direct buckets exclude that child use. Never add child allocation and descendant consumption again when reporting root exposure. On child close, atomically replace its liability by unused `available` plus settled `committed` at the parent; never return spent quota. `released` is a historical delta, not another balance bucket. Proven nonexecution releases only unconsumed effect quota; already spent tokens, API fees, attempt counts and compute remain charged in their own dimensions. / 已签发许可已占额度。父级子预留包含子级整个未返还分配及后代用量，父级直接账户不再包含这些用量；汇总根暴露时不可重复相加。子级关闭时原子将其负债替换为父级未使用可用额及已结算提交额，已消费额度不能返还；释放额是历史增量而非额外余额账户。确定未执行只能释放未消费效果额度；已消费 token、API 费用、尝试次数及算力在各自维度保持记账。

Example / 示例: root 100 → child 60 + available 40; child commits 20 → root still holds child liability 60; child closes → root committed 20 + available 80. / 根额度 100 预留子级 60 后余 40，子级消费 20 时根仍承担 60 子负债；关闭后根已提交 20、可用 80。

Rates are checked on authoritative fixed/sliding windows; concurrency is a live gauge, duration is elapsed time, depth is an ancestor bound, and object membership is set containment. Do not apply the additive equation to them or reset them on retry. In-flight/unknown requests retain execution slots until the configured authority proves they have ceased; quota release does not erase consumed dispatch rate. / 速率按权威固定或滑动窗检查，并发是瞬时值，时长是经过时间，深度约束祖先链，对象校验集合包含。不得套用累计守恒式或在重试时刷新；在途和未知请求按配置保持执行槽位，直至权威确认已停止；释放额度不抹去已消耗派发速率。

## Atomic Admission and External Submission / 原子准入与外部提交

In one serializable transaction/equivalent, lock every affected envelope and aggregate account in a stable order, recheck live scope/stops/versions, check all dimensions, reserve usage, persist the permit, idempotency binding, ledger event and durable dispatch intent. Reject any dimension without partial admission or external calls. A database rollback cannot roll back an external API. / 在一个可串行化事务或等价边界中，以稳定顺序锁定全部受影响信封与聚合账户，复核实时范围、停止及版本，检查全部维度，预占用量，并持久化许可、幂等绑定、账本事件及派发意图。任一维度失败不得部分放行或调用外部 API；数据库回滚不能回滚外部 API。

The gateway verifies authenticity, holder, expiry, epoch, actual canonical payload and live stop immediately at its serialized dispatch boundary. Claim the permit and durably record intent before sending. A lost response or crash after intent may have crossed the boundary: retain occupancy as unknown and reconcile. An expired/cancelled unused permit releases only after proving no dispatch claim could have sent it. / 网关在串行派发边界即时校验真实性、持有者、有效期、代次、实际规范载荷和实时停止；发送前领取许可并持久记录意图。意图写入后崩溃或响应丢失可能已越界，保留未知占用并对账。未用许可过期或取消，须证明不存在可能已发送的领取才能释放。

Exact replay returns the original durable status/receipt without new occupancy or dispatch; the same key with a changed digest is rejected. Same-intent retries keep their key even across new permits after proven nonexecution. A genuinely new authorized business intent needs its own identity and predecessor link; calling a retry “new” does not bypass deduplication. Downstream idempotency must cover the retry horizon; without it, gateway deduplication alone cannot guarantee exactly-once effects across crashes. Freeze ambiguous sends and reconcile rather than blindly redelivering. / 精确重放返回原持久状态或回执，不重复占用或派发；同键异摘要拒绝。已证明未执行后重新许可，同意图重试仍保留原键；真正新的获批业务意图才用新身份及前驱关联，重试改名不能绕过去重。下游幂等须覆盖重试期限；缺少此能力时，仅网关去重无法保证崩溃下严格一次效果，模糊提交须冻结对账，不能盲重发。

## State, Stop and Closure / 状态、停止与关闭

| Transition / 转换 | Required evidence and accounting / 必需证据及记账 |
| --- | --- |
| `issued → in_flight` | Gateway dispatch claim under current fence; move occupied units, do not debit twice. / 当前围栏下网关领取派发，移动占用额，不二次扣减。 |
| `in_flight → committed` | Authenticated matching external receipt/query; same intent, object, units and account. / 认证匹配外部回执或查询，意图、对象、额度及账户相同。 |
| `in_flight → unknown` | Timeout, lost receipt, crash, partial or conflicting result; keep unresolved exposure. / 超时、丢回执、崩溃、部分或冲突结果，保留未决暴露。 |
| `unknown → committed / released` | Independent evidence of success or conclusive nonexecution, including no later settlement; absence in an eventually consistent query is insufficient. / 独立证据确认成功或确定未执行且不会迟后结算；最终一致查询暂查无记录不够。 |
| `issued → expired / cancelled → released` | Atomically invalidate dispatch rights and prove unused; TTL alone never releases in-flight/unknown quota. / 原子失效派发权并证明未使用；TTL 不释放在途或未知额度。 |
| `unknown → manual_hold` | Operational disposition only: keep unknown ledger balance, named owner, next review and evidence requirements. / 仅改变处置状态，保留未知账额、负责人、复核时间及证据要求。 |

Partial success commits the proven portion and holds the unresolved remainder; never retry the entire batch as a fresh effect. Conflicting terminal evidence is appended and freezes further activity; never silently reverse committed history. Compensation is a separately authorized, metered effect and does not erase gross historic consumption. / 部分成功只提交已证部分，未决剩余继续占用；不得将整批作为新效果重试。终态证据冲突追加记录并冻结后续活动，不静默倒改提交历史；补偿是另行授权和计量的效果，不抹去历史总消费。

Stops cover permit, envelope descendants, run, principal, tenant, tool/system or global scope. Serialize stop-epoch advancement with admission and gateway dispatch. No new grant or dispatch after that authoritative boundary; already dispatched requests remain tracked. Distinguish trigger time, durable stop time, gateway acknowledgement and external arrival; clock order alone cannot prove dispatch order. / 停止覆盖许可、信封后代、运行、主体、租户、工具系统或全局。停止代次推进与准入及网关派发串行化；权威生效边界后不再发新许可或派发，已发送请求继续追踪。区分触发、持久生效、网关确认及外部到达时间；仅凭时钟不能证明派发先后。

Resume requires resolved cause, reconciliation, current authorization, a narrower/same scope and a new fence; retain the original root and cumulative use. Independent new-root authorization still shares applicable subject/tenant aggregate caps. Financial closure/return requires no issued, in-flight or unknown liabilities, no active descendants, consistent external settlement and a drained callback window. Administrative closure with manual holds keeps balances frozen, responsibility and late-receipt collection; it is not financial closure. / 恢复须解决原因、完成对账、核验当前授权、使用相同或更窄范围及新围栏，保留原根和累计消费；独立授权新根仍共享适用主体租户总上限。账务关闭返还须无已签发、在途、未知负债及活动后代，账实一致且回调窗口结束。人工冻结下行政关闭仍冻结账额，保留责任和迟到采集，不等于账务关闭。

## Observation and Interaction / 观测与交互

Events carry the preceding IDs as applicable, `event_type`, `requested_units`, `observed_units`, before/after snapshots, status, reason code, proposal/policy/profile versions, source/evidence refs, `occurred_at`, `recorded_at`, `observed_at`, and field-level quality (`original`, `derived`, `inferred`, `conflict`, `missing`, `unknown`). Record authenticated authority and derivation rule/version; confidence never makes inferred data authoritative. / 事件包含适用身份字段、类型、请求及观察额度、前后快照、状态原因、提案策略配置版本、来源证据、发生记录采集时间及字段质量。记录认证权威和派生规则版本，置信度不能使推断变成权威事实。

Canonical event types / 规范事件类型: `boundary_loaded`, `scope_computed`, `root_created`, `reservation_requested`, `reservation_granted`, `reservation_denied`, `permit_requested`, `permit_issued`, `permit_denied`, `request_submitted`, `receipt_received`, `result_unknown`, `quota_committed`, `quota_released`, `envelope_frozen`, `envelope_returned`, `stop_triggered`, `reconciliation_started`, `reconciliation_completed`, `stage_requested`, `stage_granted`, `stage_denied`, `close_requested`, `run_closed`. Local extensions / 本地扩展: `dispatch_claimed`, `permit_expired`, `permit_cancelled`, `stop_effective`, `resume_authorized`, `probe_response`.

All probe objects carry immutable ID, tenant/run scope, target type/ID, base revision, rule/version, evidence refs, creation/expiry times and actor. Patches additionally carry field path, proposed value, quality, source refs, derivation, confidence and conflict policy. Alerts carry severity, deduplication key, owner and lifecycle; stop suggestions carry scope and reason; reconciliation requests carry intent/key, unknown age, occupied units and required evidence; closure reports enumerate unresolved gaps. / 所有探针对象携带不可变标识、租户运行范围、目标类型标识、基线修订、规则版本、证据、生成有效期及主体。补丁另含字段、建议值、质量、来源、推导、置信度及冲突策略；告警含严重度、去重键、负责人及生命周期；停止建议含范围原因；对账请求含意图键、未知年龄、占用及所需证据；关闭报告列未决缺口。

The execution service authenticates scope, target, base revision and expiry, and writes a durable response with object ID/digest, `accepted / rejected / deferred / auto_blocked`, reason, actor, resulting action refs and response time. Exact delivery reuses the response; stale or changed payloads conflict. Observation enrichment appends a view only: it cannot set approval, limits, balances, permit state, external success or historical timestamps. Critical source conflicts remain visible. / 执行服务校验范围、目标、基线及有效期，持久返回对象标识摘要、采纳拒绝延期自动阻断、理由、主体、动作引用及响应时间。精确重发复用响应，过期或内容变更进入冲突。观测补全仅追加视图，不修改审批、限额、余额、许可状态、外部成功或历史时间；关键来源冲突持续可见。

Only a deterministic rule registered and enabled by the independent control plane before the run may automatically block. The authorized execution service applies it and records the response; the probe cannot acquire control authority at runtime. Optional probe failure leaves core local controls intact; missing mandatory admission evidence blocks the affected action. / 只有运行前经独立管理面登记启用的确定性规则可自动阻断，由有权执行服务实施并记录响应；探针不能运行时取得控制权。可选探针故障不取消本地强制控制；准入必需证据缺失阻断受影响动作。

Retain append-only raw evidence separately from derived views, with tenant isolation, redacted object references, access control and a versioned retention policy. External callbacks authenticate and settle the original intent; any callback-triggered new write must obtain its own permit. / 原始追加证据与派生视图分离，实行租户隔离、对象引用脱敏、访问控制及版本化保留策略。外部回调认证后结算原意图，回调触发新写入须另获许可。
