# Handoff Chain Exchange Contract / 交接链交互契约

Name / 名称: Handoff Chain Exchange Contract / 交接链交互契约.

Description / 描述: Bind formal handoffs, events and bounded evidence supplements without giving a probe business-state authority. / 绑定正式交接、事件和有界证据补全，同时保持探针无业务状态决定权。

Identity / 稳定标识: `PATTERN_0043`, `CELL_COLLABORATION_CHAIN`.

Specification version / 规格版本: `0.1.0`; protocol_version / 协议版本: `1.0`; maturity / 成熟度: `draft`; implementation / 实现: `specification_only`.

## Quick Navigation / 快速导航

- [Identity, types and binding / 身份、类型与绑定](#identity-types-and-binding--身份类型与绑定)
- [Handoff and commit rules / 交接与提交规则](#handoff-and-commit-rules--交接与提交规则)
- [Event envelope / 事件信封](#event-envelope--事件信封)
- [Bounded supplement request / 有界补全请求](#bounded-supplement-request--有界补全请求)
- [Observation patch / 观测补丁](#observation-patch-and-evidence-grades--观测补丁与证据等级)
- [Adoption and receipts / 采纳与回执](#adoption-workflow-and-receipts--采纳流程与回执)
- [External intent and recovery / 外部意图与恢复](#external-intent-and-recovery-constraints--外部意图与恢复约束)

## Usage and Authority / 适用与权威边界

This is the normative dedicated exchange contract for the [execution design](patterns/collaboration/collaboration-chain.md) and [independent probe](patterns/collaboration/collaboration-chain-observability.md). Use it for standalone execution, offline reconstruction, online observation or bounded evidence recovery. Neither side requires the other to run. It is distinct from the common collaboration source contract `2.0.0`, executable profile `3.0.0`, `CE11` and its CSM metrics; adapters require explicit mappings. / 本文是执行设计及独立探针的专用交互权威规范，适用于独立执行、离线重建、在线旁路或有界补证；双方均可独立运行。它与通用协作来源契约 2.0.0、执行配置 3.0.0、CE11 及 CSM 指标分开，适配器须显式映射。

No dedicated service, database transaction, authorizer, remote gateway or metric calculator is implemented by this document. Examples contain placeholders and are not runtime records or directly executable common-profile payloads. Source drafts and imperative examples are design material, never permission to send, publish, pay or deploy. / 本文不实现专用服务、数据库事务、鉴权器、远端网关或指标计算器；示例占位值不是运行记录或可直接投递通用配置的载荷。来源草稿及命令式示例是设计资料，不授权发送发布付款部署。

Execution owns contracts, formal versions, business facts, authorization, acceptance, commit receipts, effects and responsibility. The probe owns observations, quality findings and proposed patches. It may retrieve existing authoritative records but cannot manufacture historical evidence or directly set approval, payment, publication, acceptance or fact correctness. / 执行方持有契约、正式版本、业务事实、权限、验收、提交回执、副作用及责任；探针持有观测、质量发现和补丁提案。探针可查回已有权威记录，不得制造历史证据或直接设置批准付款发布签收及事实正确状态。

Working memory, immutable submitted candidates, committed formal state and append-only observation state are separate. An acceptance opinion is not a commit; a commit is not proof of an external effect. Only formal accepted state may feed downstream business work. / 工作记忆、不可变已提交候选、正式提交状态及追加观测状态分开。接收意见不等于提交，提交不证明外部效果；下游业务只消费正式接收状态。

## Identity, Types and Binding / 身份、类型与绑定

| Field / 字段 | Required semantics / 必需语义 |
| --- | --- |
| `tenant_id` | Authenticated tenant/security boundary included in reads, acceptance and deduplication. / 经认证安全域，参与读取、验收和去重。 |
| `workflow_id`, `task_id`, `chain_id` | Workflow definition, business task and exact handoff-chain identity; together with tenant form `scope`. / 工作流定义、业务任务及具体链身份，与安全域组成范围。 |
| `stage_instance_id` | One logical stage; retained on retry, new on a new loop entry. / 一次逻辑阶段重试保持，循环新轮新建。 |
| `attempt_id` | One actual execution attempt; retry obtains a new ID. / 一次实际执行，重新执行产生新标识。 |
| `handoff_id` | One immutable candidate; unchanged only for exact transport redelivery, new for content/evidence/receiver edits. / 一个不可变候选，仅同包传输重发保持，内容证据接收者改动新建。 |
| `operation_id` | Stable external business intent across attempts, restart and baton versions; not inferred from equal parameters. / 跨尝试重启接力棒版本稳定的外部业务意图，不能从参数相等推断。 |
| `event_id` | Event identity used for duplicate delivery, never a substitute for operation idempotency. / 事件投递去重标识，不替代业务操作幂等身份。 |
| `control_epoch` | Nonnegative monotonic control generation; takeover/transfer invalidates older grants and increases it. / 非负单调控制代次，接管转移使旧授权失效并增加代次。 |
| `current_owner`, `assigned_executor`, `proposed_receiver` | Formal responsible actor, authorized executing instance and proposed successor; the last becomes owner only after commit. / 正式责任人、授权执行实例及候选接收者，后者提交后才成为责任人。 |
| `request_id`, `patch_id`, `receipt_id` | Stable supplement request, immutable patch and durable disposition record. / 稳定补全请求、不可变补丁及持久处置记录。 |

IDs and protocol/contract versions are nonempty strings. State versions, epochs and source sequence are nonnegative integers; optional not-yet-created/inapplicable values are explicit null. `scope` and `target` are objects; reference/observation collections are arrays; times use timezone-qualified standard timestamps. Unknown historical times remain null with an explicit reason, never filled from collection time. / 标识及协议契约版本为非空字符串，状态版本代次来源序号为非负整数；未产生或不适用的可选值明确为空。范围目标是对象，引用观测是数组，时间带时区；历史时间未知时为空并注明原因，不用采集时间冒充。

Reject unknown protocol major versions; compatible changes require declared capabilities and an explicit extension area. Never silently ignore unknown control fields. Authenticate actors/source systems/sequence at trusted ingress; self-reported names are not proof. Verify tenant and permissions before resolving references. / 未知协议大版本拒绝，兼容变更须声明能力及扩展区，不能静默忽略未知控制字段。可信接入核验主体、来源及序号，自报名称不证明身份；展开引用前先核安全域和权限。

Fix digest algorithm/version, character encoding, canonical field order, time/number formats and content boundary. Digests bind complete immutable bytes/content, including meaningful title/body/table/attachment content; do not substitute summaries. Bind artifact and allowed fact-set digests plus rule/approval versions independently. A digest proves neither source truth nor authorization. / 固定摘要算法版本、编码、字段顺序、数值时间格式及内容边界，绑定完整不可变字节内容，包括标题正文表格附件，不能以概要代替。分别绑定工件、允许事实集合及规则审批版本；摘要不证明来源真实或权限。

## Handoff and Commit Rules / 交接与提交规则

A candidate includes scope, stage/attempt/handoff IDs, exact input version/manifest digest, sender, proposed receiver, epoch, contract, consumed refs, allowed delta, evidence, permission, deadline and recovery point. Receiver opinions bind this exact candidate, input snapshot and rule version; gate verdicts are `passed`, `rejected`, `unknown`, `not_applicable`. Inapplicability needs contract grounds; critical unknowns pause. / 候选含范围阶段尝试交接、精确输入版本摘要、双方代次契约、所用引用、获准增量、证据权限期限恢复点。意见绑定该候选、输入及规则，闸门返回通过拒绝未知不适用；不适用有契约依据，关键未知暂停。

Only the state authority commits. CAS/equivalent checks scope, expected head/digest, owner, epoch and current acceptance/authorization. In one atomic boundary persist successor manifest, commit/audit receipt, owner/epoch transition and notification intent. A takeover and a commit cannot both use the same stale control generation. Downstream workers query confirmed commit and receive a new bound grant before starting. / 仅状态权威提交；CAS 或等价校验范围、预期头摘要、责任、代次及当前验收授权。同一原子边界持久化后继清单、提交审计回执、责任代次和通知意图。接管与提交不能都持旧代次获准；下游先查提交并获新绑定授权再工作。

Durable `(scope, handoff_id)` uniqueness binds the immutable package digest and original receipt. Exact replay, including after restart, returns the same result without new version or transfer; same key/different content is an integrity conflict. Check existing committed identity before classifying that exact replay as stale. A distinct candidate with stale input fails without head rollback. / 范围与交接标识持久唯一绑定包摘要及原回执，重启后精确重放仍返原结果而不新建版本转责；同键异内容为完整性冲突。应先识别已提交同包，避免将其误判新过期候选；新的过期候选失败，不倒退全局头。

A formal receipt records `receipt_id`, scope, handoff/stage IDs, input version, output version, observed head version, verdict/reason, authenticated acceptor, actual artifact digests, rule version, owner/epoch changes and commit time. No commit means `output_version: null`; any observed newer head is separate. Successful and rejected receipts append history. / 正式回执含标识范围交接阶段、输入输出版本、观察头、结论原因、认证验收者、实际工件摘要、规则、责任代次变化及提交时间；未提交时输出版本为空，较新的观察头另记，成功拒绝均追加历史。

Local transactions cannot cover arbitrary external systems. Prewritten immutable blobs may remain orphaned and unaccepted after failure. Lost/duplicate notifications query or replay the commit, never create a second ownership transfer. Failure to persist foundational audit blocks formal commit and protected writes. / 本地事务不覆盖任意外部系统，预写工件失败后可能为未接收孤儿；丢失重复通知通过查回重放提交恢复，不二次转责。基础审计不可持久化阻止正式提交及受保护写入。

## Event Envelope / 事件信封

The following structural example lists the minimum envelope; replace placeholders and enforce the preceding type rules. Event scope is flat; supplement scope is nested under `scope`, with equivalent semantics. / 以下结构示例列出最小信封，生产须替换占位值并执行类型约束；事件范围平铺、补全范围嵌入 scope，语义相同。

```yaml
protocol_version: "1.0"
event_id: "<event>"
event_type: handoff_submitted
source_system: "<registered-authenticated-source>"
source_sequence: 12
occurred_at: "<timestamp-with-timezone>"
recorded_at: "<timestamp-with-timezone>"
tenant_id: "<tenant>"
workflow_id: "<workflow>"
task_id: "<task>"
chain_id: "<chain>"
stage_instance_id: "<stage>"
attempt_id: "<attempt>"
handoff_id: "<handoff>"
operation_id: null
input_version: 2
output_version: null
input_manifest_digest: "<algorithm:actual-input-digest>"
artifact_refs: []
receipt_ref: null
actor_identity: "<authenticated-actor>"
receiver_identity: "<authorized-receiver>"
control_epoch: 7
contract_version: "1.0"
policy_version: "<policy-version>"
reason_code: null
evidence_refs: []
```

Required lifecycle coverage: stage start; candidate ready and handoff submitted; acceptance pass/reject/unknown; formal commit; responsibility transfer; external intent prepared, operation sent, result confirmed/unknown, reconciliation and compensation; supplement requested/returned/adopted/partially adopted/rejected/expired/pending verification; checkpoint recovery; escalation; cancellation; task terminal. Record only applicable events, never invent an operation or compensation to complete the inventory. A gate's inapplicability is preserved in its result. / 生命周期覆盖阶段开始、候选就绪及交接提交、验收通过拒绝未知、正式提交、责任转移、外部意图准备、操作发出、结果确认未知、查证及补偿、补全请求返回采纳部分采纳拒绝过期待确认、检查点恢复、升级、取消及终结。仅记录实际适用事件，不为补齐清单虚构操作或补偿；闸门不适用保留在结果中。

`source_sequence` orders a declared authenticated source stream, not all systems globally. Source metadata must define that stream's scope; merge with causal handoff/operation/receipt references. `occurred_at` is event occurrence and `recorded_at` is source persistence; probe collection time is separate. Deduplicate `(tenant_id, source_system, event_id)` only when content matches; divergent content conflicts. Gaps, late events and unknown ordering remain explicit. / 来源序号只排序已声明认证来源流，不给全系统全序；来源元数据明确流范围，以交接操作回执因果引用合并。发生时间、来源持久化及探针采集时间分开；租户来源事件同键同内容去重，异内容冲突；缺口迟到未知顺序明确保留。

Business transitions and base-audit records are durably consistent; probe exports may arrive late without replacing the original record. Do not infer absence of work from absence of telemetry, or infer completed responsibility transfer from a send event. / 业务转换与基础审计保持持久一致，探针导出可迟到但不替代原记录；无遥测不推断未工作，发送事件不证明转责完成。

## Bounded Supplement Request / 有界补全请求

A request names exactly what is missing, the immutable target, permitted read-only sources/operations, authority and stopping bounds. Business work missing must return to its authorized producer; a probe can retrieve evidence of completed work, not complete the business operation itself. / 请求明确缺什么、不可变目标、获准只读来源操作、权限与停止边界。业务未完成须回有权生产者；探针可查已完成工作的证据，不能替业务执行。

```yaml
protocol_version: "1.0"
request_id: "<request>"
scope:
  tenant_id: "<tenant>"
  workflow_id: "<workflow>"
  task_id: "<task>"
  chain_id: "<chain>"
target:
  stage_instance_id: "<stage>"
  handoff_id: "<handoff>"
  expected_version: 2
  expected_manifest_digest: "<algorithm:target-digest>"
  artifact_digests: ["<algorithm:artifact-digest>"]
field_paths: [observations.artifact_integrity, observations.evidence_availability]
purpose: "<acceptance-evidence-gap>"
allowed_sources: ["<registered-artifact-store>", "<registered-audit-ledger>"]
permission_ref: "<read-only-authorization>"
allow_deterministic_derivation: true
max_rounds: 2
max_cost: 1 # configured unit/bound, not a universal default / 配置单位及上限，非普适默认值
deadline_at: "<timestamp-with-timezone>"
```

The stage instance is required; handoff may be explicit null at a pre-candidate checkpoint. Target version and manifest always identify the formal decision basis. A stage/attempt/target change requires a new scoped request, not editing an active request in place. Freeze allowed sources, cost unit, timeout and round budget; no unbounded recursive collection of the probe's own telemetry. / 阶段实例必需，候选前检查点的交接标识可显式为空；目标版本清单始终绑定正式判断依据。阶段尝试目标变化需新范围请求，不能原地修改活动请求。固定来源成本单位超时及轮数，探针自身遥测不得无限递归补全。

## Observation Patch and Evidence Grades / 观测补丁与证据等级

```yaml
protocol_version: "1.0"
patch_id: "<patch>"
request_id: "<request>"
scope:
  tenant_id: "<tenant>"
  workflow_id: "<workflow>"
  task_id: "<task>"
  chain_id: "<chain>"
target:
  stage_instance_id: "<stage>"
  handoff_id: "<handoff>"
  expected_version: 2
  expected_manifest_digest: "<algorithm:target-digest>"
  artifact_digests: ["<algorithm:artifact-digest>"]
observations:
  - field_path: observations.artifact_integrity
    value: null
    evidence_status: unknown
    evidence_refs: []
    source_digest: null
    observed_at: "<timestamp-with-timezone>"
    valid_until: "<timestamp-with-timezone>"
    method: "<read-denied-or-other-explicit-reason>"
    rule_version: "1.0"
recommendation: "<pause-dependent-check-and-route-to-authorized-owner>"
```

| `evidence_status` / 证据状态 | Requirements / 要求 |
| --- | --- |
| `direct` / 直接观测 | Authenticated source, immutable source/version reference, actual observation time and applicability. / 认证来源、不可变来源版本、实际观测时间及适用范围。 |
| `derived` / 确定性派生 | Retain input evidence/digests and reproducible method/rule version; request must allow derivation. / 保存输入证据摘要及可复算规则版本，请求须允许派生。 |
| `inferred` / 推断 | Mark uncertainty and separate from authoritative facts; never fill approval/payment/acceptance/correctness. / 标明不确定并与权威事实分离，不补批准付款签收正确状态。 |
| `unknown` / 未知 | Keep absent value null and state missing/access/expiry reason; never synthesize history or success. / 缺值为空并记缺失权限过期原因，不合成历史或成功。 |

A present source, accessible source, supported claim and currently applicable claim are distinct checks. Current observations cannot prove past conditions; immutable historical records are required for historical claims. Observed time is not historical event time. / 来源存在、可访问、支持主张及当前适用是不同检查；当前观测不证明过去条件，历史结论需不可变历史记录；观测时间不是历史发生时间。

## Adoption Workflow and Receipts / 采纳流程与回执

Receiver order: compatible protocol → authenticated actor/permission → scope → active request → exact stage/handoff/version/manifest/artifacts → source allowlist/authenticity → validity → requested field allowlist → durable idempotency and atomic side-table decision. An exact prior result is replayed after identity/integrity checks; new stale patches do not apply to the current head. / 接收顺序为协议、身份权限、范围、活动请求、精确阶段交接版本清单工件、来源许可真实性、时效、请求字段白名单及持久幂等原子旁表决定；身份完整性核验后同包可重放原结果，新的陈旧补丁不得应用当前头。

Use durable `(scope, request_id, patch_id)` as the unique idempotency key. Store the content digest as an immutable value bound to that key, not as another key component. Exact replay returns the original disposition even after restart; the same key with a different digest conflicts. A new patch for changed target or observations gets a new ID. Target changes return `stale_probe_patch`; retain historical audit if appropriate. Concurrent adoption must not silently overwrite earlier observations; append values and explicit correction links under authority-controlled serialization. / 以范围、请求和补丁标识组成唯一持久幂等键，内容摘要是该键下不可变绑定值，不是键的附加组成部分。同包重启后返原处置，同键异摘要冲突；目标或观测变化建新标识。目标过期记录指定原因，可留历史；并发采纳不静默覆盖旧观测，经权威串行控制追加值及更正关系。

| Disposition / 处置 | Effect / 效果 |
| --- | --- |
| `accepted` / 采纳 | Append validated observation and its source; resume the same check only if its decision basis remains valid. / 追加已核验观测来源，仅判断依据仍有效时恢复原检查。 |
| `partially_accepted` / 部分采纳 | Permit only independently validated requested fields; record per-field decisions and unresolved gaps atomically. A scope/identity/target failure rejects the whole patch. / 仅准独立核验字段，原子记录逐字段处置及缺口；范围身份目标失败整包拒绝。 |
| `rejected` / 拒绝 | Persist reason and no proposed updates; unauthorized/unsourced/incorrect fields cannot become evidence. / 留原因且不应用提议，无权无来源错误字段不得成证据。 |
| `expired` / 过期 | Preserve old-target/expired proposal as history; do not resume current dependent work. / 保留旧目标过期提案历史，不恢复当前依赖工作。 |
| `pending_verification` / 待确认 | Preserve unresolved patch without accepted credit; critical dependent work stays paused. / 未决补丁不计已补齐，关键依赖保持暂停。 |

Persist an adoption receipt with `receipt_id`, `request_id`, `patch_id`, scope/target, patch digest, disposition, per-field decisions, reason codes, authenticated adopter, source refs, adopted time and resume point. Commit receipt and observation append together; missing receiver confirmation remains pending. Partial adoption requires every field's disposition, never silent partial writing. / 采纳回执持久记录标识请求补丁范围目标、包摘要、总体及逐字段处置原因、认证采纳者、来源时间和恢复点；回执与观测追加共同提交，无接收确认保持待接收；部分采纳逐字段明确，不能静默部分写入。

Pure observation never changes formal version, business approval, receipt validity or owner. If a recovered record should become formal business evidence, the authorized stage submits a new evidence increment through all applicable business gates and conditional commit. The probe cannot label its patch “harmless” to bypass this review. / 纯观测不改正式版本、业务批准、回执效力或责任。查回记录若要成为正式业务证据，须有权阶段提交新证据增量并重过业务闸门及条件提交，探针自称无害不能绕过。

## External Intent and Recovery Constraints / 外部意图与恢复约束

Before effects, freeze target and payload, independently verify actual content, scope, control, approval, input, resource and budget, then durably prepare a stable `operation_id`. Gateway/destination enforces current epoch and exact permitted payload. Business payload digest remains stable on same-intent retries even if a new current authorization/epoch envelope is required. / 副作用前冻结目标载荷并独立校验内容范围控制审批输入资源预算，再持久准备稳定操作标识；网关目的端约束当前代次及精确载荷。同意图重试的业务载荷摘要保持，新的当前授权代次信封可另更新。

Unknown effects trigger query/reconciliation of that original intent, not a fresh key. Same operation key/different payload fails. “Not found” needs remote consistency/retention evidence before proving no execution; expired idempotency retention prevents blind replay. Verified failure with partial effects requires reconciliation. Compensation is a separately authorized operation with its own identity, result and failure handling. / 未知效果查询对账原意图，不换新键；同键异载荷失败。未找到须远端一致性保留证据才可证明未执行，幂等保留过期不可盲重；部分效果失败先查证，补偿是另授权且有自身标识结果失败处理的新操作。

Every recovery has last formal stage/version, valid retained evidence, pending intents, attempt/cost/deadline bounds and named owner. Probe outage permits optional telemetry degradation only. Execution still persists base audit, enforces critical checks and retrieves business evidence or pauses. Offline findings are discoveries at observation time, not retrospective runtime interception. / 每次恢复有最后正式阶段版本、仍有效证据、未决意图、次数成本期限及责任。探针离线只允许非关键遥测降级，执行仍须基础审计、关键检查及业务取证或暂停；离线发现是观测时发现，不是历史运行时拦截。

Treat artifacts, logs, web text and prior agent suggestions as untrusted data, not authority to override contracts or obtain credentials. Keep tenant/purpose/retention boundaries, redact raw secrets and record public reasons/evidence references rather than private chain-of-thought. / 工件日志网页及其他智能体建议作为不可信资料，不授权覆盖契约或获取凭据；保留租户用途保留边界，脱敏秘密，只记公开理由证据引用，不采集私密思维过程。
