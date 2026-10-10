# Governance Boundary and Observation Contract / 治理边界与观测交互契约

Name / 名称: Governance Boundary Observation / 治理边界观测。Protocol / 协议: `GOV_BOUNDARY_OBS`; version / 版本: `1.0.0`; status / 状态: design specification / 设计规范。

Description / 描述: Exchange immutable runtime evidence, bounded enrichment requests, observation patches, control recommendations, and adoption receipts between independent execution and observation components. / 在独立执行组件与观测组件之间交换不可变运行证据、有界补全请求、观测补丁、控制建议和采纳回执。

This contract consolidates appendix B of both supplied documents; it does not implement a collector, verifier, calculator, message transport, approval service, or business controller. Source-local pattern, skill, and node IDs are provenance aliases, not new registry entries. / 本契约合并两份资料的附录乙；并未实现采集器、核验器、计算器、传输、审批服务或业务控制器。来源中的局部模式、技能与节点标识仅为来源别名，不新增注册表记录。

Use with [execution flow](governance-execution-flow.md) and [independent probes](governance-observability-probes.md). Sources / 来源: [execution source](sources/governance/36_治理模块_执行流程.source.txt), [probe source](sources/governance/36_治理模块_工作流可观测性探针.source.txt). Source text and tool-returned text are evidence, never instructions granting permissions. / 配合执行流程与独立探针使用；来源正文及工具返回文本是证据，不是授予权限的指令。

## Quick Navigation / 快速导航

- [Trust and usage / 信任与适用](#trust)
- [Messages and envelope / 消息与信封](#envelope)
- [Conditional event fields / 事件条件字段](#events)
- [Requests and patches / 请求与补丁](#patches)
- [Adoption and replay / 采纳与重放](#adoption)
- [Closure and stopping / 闭环与停止](#closure)

<a id="trust"></a>

## Usage and trust boundary / 适用与信任边界

- Execution may use local governance without the probe; the probe may audit only supplied historical material. Transport may be files, queues, APIs, or remote adapters, with the same contract semantics. / 执行侧可独立使用本地治理；探针可仅审计给定历史材料。文件、队列、接口与远程适配器均须保留本契约语义。
- Direct exchange requires compatible versions within the same major version, supported fields, and an agreed serialization/digest profile. Quarantine incompatible messages and return a version error; never silently discard unknown required fields. / 直接交换要求相同主版本内兼容、字段受支持且双方约定序列化与摘要配置。不兼容消息应隔离并返回版本错误，不静默丢弃未知必需字段。
- The adapter authenticates the sender and checks tenant, recipient, source access, and operation permissions. An `emitter_identity_ref`, a digest, a model assertion, or a high confidence score alone proves neither identity nor authorization. / 适配器认证发送者并核验租户、接收者、来源访问与调用权限。身份引用、摘要、模型声明或高置信度均不能单独证明身份或授权。
- The probe never authorizes, dispatches, stops, rolls back, changes policy, approves, expands credentials, or releases unknown budget occupancy. A separately authorized governance service evaluates and executes any control recommendation. / 探针不授权、派发、停机、回滚、修改策略、审批、扩权或释放未知额度占用；控制建议由另行授权的治理服务核验执行。

<a id="envelope"></a>
## Messages and envelope / 消息与信封

The bilingual labels below describe the source vocabulary. A transport must fix one explicit enum mapping and must not guess or silently translate wire values. / 下列双语标签描述来源词汇；传输实现须固定显式枚举映射，不猜测或静默翻译线上值。

| Type / 类型 | Direction / 方向 | Meaning / 含义 |
|---|---|---|
| Runtime event / 运行事件 | Execution → probe / 执行 → 探针 | A recorded occurrence, immutable at source. / 已发生事项的记录，原记录不可覆盖。 |
| Enrichment request / 补全请求 | Either component → peer / 任一侧 → 对侧 | Named missing evidence and bounded retrieval; no business authority. / 指定缺证与有界检索，不授予业务权限。 |
| Observation patch / 观测补丁 | Probe → execution / 探针 → 执行 | Source-backed facts, deterministic derivations, or explicitly unverified leads. / 有来源的事实、确定性推导或明确待核验线索。 |
| Control recommendation / 控制建议 | Probe → authorized governance service / 探针 → 授权治理服务 | Proposed pause, review, restriction, or reconciliation; not an execution credential. / 建议暂停、复核、缩权或对账，不是执行凭证。 |
| Adoption receipt / 采纳回执 | Receiver → sender / 接收方 → 发起方 | Per-field outcome and reasons; no implied business completion. / 逐字段结果与原因，不隐含业务完成。 |

All messages carry these envelope fields. / 所有消息携带以下信封字段。

| Field / 字段 | Requirement / 要求 |
|---|---|
| `protocol_id`, `protocol_version` | `GOV_BOUNDARY_OBS`, `1.0.0`; validate compatibility. / 核验协议与版本兼容性。 |
| `message_id`, `message_type` | Unique message identity within tenant and fixed type mapping; reuse only for identical retransmission. / 租户内唯一消息身份与固定类型映射，仅相同内容重传可复用。 |
| `tenant_id`, `trace_id`, `run_id`, `step_id` | Tenant and correlation; step identifies an instance, not a node definition. / 租户与关联；步骤指实例，不指节点定义。 |
| `skill_id`, `skill_version` | Executed definition and version, not a source-local alias presented as a registered asset. / 实际执行定义与版本，不冒用来源局部别名为已注册资产。 |
| `emitter_identity_ref`, `emitted_at` | Authenticated sender reference and timezone-bearing emission time. / 经适配器认证的发送者引用与带时区发送时间。 |
| `causation_id` | Upstream message/event; distinguish a root event from unavailable causal evidence. / 上游消息或事件；区分根事件与因果证据不可取得。 |
| `content_digest`, `payload` | Digest over the canonical message and complete typed payload. / 规范化消息的完整摘要与类型化载荷。 |

An object not yet created may have a null identifier with a field-specific reason. Distinguish `not_created` / 尚未产生, `access_denied` / 无权读取, `collection_failed` / 采集失败, and justified `not_applicable` / 不适用. Absence of required evidence is a gap, not a fabricated object or arbitrary exemption. Tenant, protocol, sender, and message identity cannot be omitted to bypass validation. / 对象尚未产生时，其标识可为空但须给出逐字段原因。必需证据缺失是缺口，不能造出对象或任意豁免；不得省略租户、协议、发送者及消息身份来绕过校验。

Digest computation excludes only the envelope's own `content_digest` and transport signature fields; it includes message type, all correlation fields, and the complete payload, including nested evidence digests. Bind serialization/digest profile and version in adapter configuration. Define decimal amounts and units, timezone representation, null semantics, object-key ordering, and ordered arrays consistently; do not round values or sort semantically ordered arrays independently. Preserve the original digest and content on retransmission. No executable canonicalizer or authentication implementation is supplied here. / 摘要仅排除信封自身的 `content_digest` 与传输签名字段，纳入消息类型、全部关联字段和完整载荷，包括嵌套证据摘要。适配器配置绑定序列化、摘要配置与版本；统一金额精度及单位、时区表示、空值语义、对象键序与有序数组，不各自舍入或重排语义有序数组。重传保留原内容及摘要；本文件未提供可执行规范化器或认证实现。

Record source occurrence time separately from ingestion and retrieval time; use timezone-bearing timestamps or UTC. Source sequence is ordered only within its producer. Cross-source wall clocks never establish strict causality alone. / 来源发生时间与接收、查询时间分别记录；使用带时区时间或 UTC。来源序号只在生产者内部有序，不仅凭跨来源时钟确定严格因果。

<a id="events"></a>
## Conditional event contract / 事件条件字段契约

A versioned node/event contract determines applicability before validation. Preserve missing fields and their reasons; do not discard incomplete events from audit denominators. / 验证前由版本化节点与事件契约判定适用性；保留缺失字段及原因，不从审计分母丢弃不完整事件。

| Fields / 字段 | Conditions and semantics / 条件与语义 |
|---|---|
| `event_id`, `event_type`, `node_id` | Every event; ID cannot be recycled, node points to the definition. / 每个事件必备；标识不可回收复用，节点指向定义。 |
| `task_id`, `action_id`, `attempt_id` | Separate task, logical action, and attempted call; a retry changes attempt identity without inventing another business request. Pre-attempt stages state why attempt ID is absent. / 区分任务、逻辑动作与调用尝试；重试更换尝试标识但不伪装新业务需求。尝试前说明缺少尝试标识的原因。 |
| `proposal_id`, `proposal_version`, `proposal_digest` | All decisions, dispatches, and results bind the exact frozen proposal. / 所有裁决、派发与结果绑定精确冻结提案。 |
| `artifact_id`, `artifact_digest`, `contract_digest` | Bind the actual artifact snapshot and task boundary where applicable, never a mutable filename alias. / 适用时绑定真实工件快照与任务边界，不绑定可变文件别名。 |
| `policy_refs`, `policy_set_digest` | Allow and deny decisions both require policy ID, version, full content digest, and policy-set digest. Missing policy is a decision gap. / 放行与拒绝均要求策略标识、版本、完整内容摘要及集合摘要；裁决缺策略即为缺口。 |
| `decision_context_digest`, `receipt_id` | Decisions bind authorization identities and resource precondition versions; preserve the original receipt in protected storage. / 裁决绑定身份授权、资源前置版本；原回执保存在受保护存储。 |
| `credential_id`, `credential_version` | Record the actual credential used for execution, without secret material; pre-execution absence needs an explicit reason. / 记录实际执行凭证但不记录密钥；执行前缺失须说明原因。 |
| `reservation_id`, `business_operation_id`, `idempotency_key` | Budget-controlled dispatch binds reservation; effectful operations bind durable business and idempotency identities consistently across retries. / 受额度控制的派发绑定预留；副作用操作跨重试保持正确的持久业务与幂等身份。 |
| `external_request_id` | Distinguish never submitted from submitted but ID unavailable; do not invent either an ID or a failure result. / 区分尚未提交与已提交但未取得标识；不编造标识或失败结果。 |
| `occurred_at`, `ingested_at`, `emitter_sequence` | Preserve occurrence, receipt time, and producer-local sequence or explicit collection gaps. / 保留发生、接收时间及来源内部序号，或明确采集缺口。 |
| `result_status`, `reason_code` | Distinguish allowed, denied, submitted, verified success, verified failure, and unknown; API acceptance is not business success. / 区分允许、拒绝、已提交、已核实成功、已核实失败与未知；接口接收不等于业务成功。 |
| `evidence_refs`, `quality_state` | Every fact references evidence and quality; verification events require authoritative business-result evidence. / 每项事实附证据与质量；结果核验事件须有权威业务结果来源。 |
| Policy change fields / 策略变更字段 | Policy changes additionally require before/after versions, proposer, approver, effective time, and reason. / 策略变更额外要求前后版本、提出者、批准者、生效时间与原因。 |

Quality mapping: `verified` / 已核验, `pending_verification` / 待核验, `missing` / 缺失, `conflict` / 冲突, `expired` / 已过期, `not_applicable` / 不适用. Value kinds: `source_fact` / 来源事实, `deterministic_derivation` / 确定性推导, `model_hypothesis` / 模型假设. These are distinct from business status and metric result status. A source fact is not automatically verified. / 质量状态、值类别、业务状态与指标结果状态分别保存；来源事实不自动成为已核验事实。

<a id="patches"></a>
## Enrichment requests and patches / 补全请求与补丁

Each request includes `request_id`, target tenant/run/action/fields, expected proposal and policy digests, gap type, permitted source list, deadline, evidence requirements, query budget, retry limit, and deduplication key. Gap types are missing evidence / 证据缺失, fact not performed / 事实未发生, source conflict / 来源冲突, stale evidence / 时效失效, denied access / 权限不足, and ambiguous association / 关联不明. A missing record alone does not prove that an approval never existed. / 每个请求绑定目标及版本、缺口分类、来源白名单、期限、证据要求、查询预算、重试上限与去重键；仅未找到记录不能证明审批从未存在。

Patch shape, with illustrative placeholders only / 补丁结构，值均为示意占位符：

```yaml
patch_id: unique-patch-id
request_id: original-request-id
mode: current_run_enrichment
target:
  tenant_id: tenant-id
  run_id: run-id
  action_id: logical-action-id
  base_state_revision: 12
  proposal_digest: exact-proposal-digest
  policy_set_digest: exact-policy-set-digest
  artifact_digest: exact-artifact-digest
expires_at: '2026-09-22T07:05:00Z'
fields:
  - path: observation_enrichment.receipt_verification_lead
    value:
      receipt_ref: protected-original-record-ref
      verification_status: requires_execution_gate_revalidation
    source_version: original-source-version
    retrieved_at: '2026-09-22T07:01:00Z'
    applicable_target_ref: exact-target-snapshot-ref
    evidence_refs:
      - source_id: approval-store
        record_id: original-record-id
        content_digest: original-record-digest
        occurred_at: '2026-09-22T06:55:00Z'
        retrieved_at: '2026-09-22T07:01:00Z'
    value_kind: source_fact
    derivation: null
    quality_state: verified
```

Map `current_run_enrichment` to 当前运行补全 and `historical_audit_enrichment` to 历史审计补全 in the adapter profile. These example aliases do not silently replace the source vocabulary. / 适配器配置明确映射当前运行补全与历史审计补全；示例英文别名不静默替换来源词汇。

- Each field retains source reference, source version, retrieval time, exact applicability, and quality; derived values add formula/rule version and input versions. Hypotheses remain unverified diagnostic leads, never authoritative approvals, payment outcomes, or balances. / 每个字段保留来源、来源版本、采集时间、精确适用对象及质量；派生值增加公式或规则版本与输入版本。假设仅作为待核验诊断线索，不生成权威审批、付款终态或余额。
- Whitelist only explicitly registered paths under `observation_enrichment`. Reject paths outside this namespace, path escapes, whole-object replacement, and hidden business writes. Prohibit modification of goals, amounts, recipients, proposals, policies, approval decisions, execution state, balances, credentials, original events, or audit times. / 白名单仅允许 `observation_enrichment` 下显式登记路径；拒绝外部路径、路径逃逸、整个对象替换及隐含业务写入。禁止改任务目标、金额、对象、提案、策略、审批结果、执行状态、余额、凭证、原始事件或审计时间。
- `verified` means the probe verified the source/content for its observation purpose. The execution gate must independently verify authority, identities, all bindings, freshness, revocation, and current policy before deciding whether execution may proceed. / `已核验` 仅表示探针为观测目的核验了来源与内容；执行入口须独立复核授权、身份、绑定、时效、撤销及当前策略后才能决定执行。
- Offline analysis without an exact target revision produces a non-applicable candidate package, not a currently applicable patch. Historical mode binds one immutable historical snapshot and cannot overwrite the current view or restore execution eligibility. / 缺少精确目标版本的离线分析只能产生不可直接应用的候选包；历史模式绑定明确的不可变历史快照，不覆盖当前视图或恢复执行资格。

<a id="adoption"></a>
## Adoption and replay workflow / 采纳与重放流程

1. Authenticate sender and recipient context; validate protocol, permissions, and tenant before any replay response or mutation. / 先认证发送者与接收上下文，核验协议、权限和租户，再返回重放结果或写入。
2. Validate the actual digest and check durable tenant-scoped `message_id`, `event_id`, and `patch_id` records as applicable. Identical replay returns the stored result without reapplying; the same ID with different content is rejected and quarantined as a conflict, never treated as latest-wins. / 核验实际摘要并按需检查租户内持久消息、事件及补丁标识。相同内容重放返回原结果且不重复应用；同标识异内容拒绝并隔离为冲突，不保留最新版冒充正常。
3. For a new patch, exactly match tenant, run, action, proposal digest, policy-set digest, artifact digest, and `base_state_revision`. Any changed binding returns conflict; obtain the new snapshot and reanalyze before issuing a new patch. Do not merely substitute a fresh digest. / 新补丁精确核对租户、运行、动作、提案、策略集合、工件摘要及基线状态版本；变化即返回冲突。应取得新快照重新分析后生成新补丁，不仅替换摘要。
4. Validate patch expiry and the explicit path whitelist, then revalidate source identity, source version, evidence age, applicability, and derivation. A newly emitted patch never rejuvenates expired evidence. / 核验补丁有效期和显式字段白名单，再复核来源身份、版本、证据时效、适用范围与派生规则；新发补丁不能让旧证据重新有效。
5. Append only eligible observation enrichment, retaining originals, original gaps, and prior observation versions. Apply the revision precondition atomically with the append; persist replay identity and adoption outcome consistently to prevent crash/retry double application. This is an adapter implementation requirement, not a supplied runtime feature. / 仅追加合格观测补全，保留原件、原缺口及历史观测版本。版本前置条件与追加应原子完成，去重身份与采纳结果一致持久化，避免崩溃重试重复写入；这是适配器待实现要求，不是现成运行能力。
6. Return a per-field receipt including receipt ID, patch ID and digest, receiver identity, validation time, field outcomes and reasons, and resulting observation revision. States: accepted / 已采纳, partially accepted / 部分采纳, rejected / 拒绝, conflict / 冲突, expired / 已过期, pending human / 待人工. / 返回包含回执标识、补丁标识及摘要、接收主体、核验时间、逐字段结果与原因、采纳后观测版本的回执，并区分六种状态。
7. If accepted evidence affects execution prerequisites, the execution component re-enters governance adjudication and final execution checks. Patch acceptance, partial acceptance, transport delivery, or a human acknowledgement is never execution authorization or gap closure by itself. / 采纳证据影响执行前提时，执行侧重新进入治理裁决与最终检查；采纳、部分采纳、送达或人工知悉均不单独构成执行授权或缺口关闭。

For a genuinely identical replay, return the original stored receipt even if the target has since advanced; this reports the historical application and does not apply it again. For a new patch against an advanced revision, return conflict. Authentication remains mandatory in either case. / 真正相同的重放即使目标版本已推进也返回原存储回执，仅说明历史采纳且不重复写入；新补丁针对过期基线则返回冲突，两者均须认证。

<a id="closure"></a>
## Closure, integrity, and stopping / 闭环、完整性与停止

Close a gap only after the receiver verifies evidence against the original acceptance condition. Track per-field unresolved gaps after partial acceptance; rejected recommendations may close communication while their risks remain open. A fact never performed requires a new business step or proposal and new applicable approval on the execution side. / 仅当接收方核验的证据满足原验收条件才关闭缺口；部分采纳后逐字段保留未解决项。建议被拒绝可结束沟通但风险仍开放；事实未发生时，执行侧须建立新业务步骤或提案并重新取得适用审批。

An approval created after the action cannot become prior approval. An earlier genuine record discovered later retains both occurrence and discovery times. Report original record completeness separately from later reconstructability, and preserve both calculation revisions instead of rewriting historical scores. / 操作后形成的批准不能改成事前批准；事后找到当时真实存在的记录也保留发生与发现时间。原始记录完整性与事后可还原程度分开报告，保留计算版本，不改写历史分数。

Tag outputs and receipts with their source request, use durable deduplication, and bound queries, retries, and deadlines to prevent recursive self-enrichment. Stop automated queries on exhausted budget, denied access, unavailable evidence, or timeout; preserve unresolved items, an owner, the next permitted action, and closure evidence required. Missing configuration is never unlimited permission or infinite validity. / 输出及回执关联来源请求，通过持久去重与查询、重试、期限边界避免自补全递归。预算耗尽、权限不足、无证可补或超时后停止自动查询，保留未解决项、负责人、允许下一步与关闭依据；配置缺失不等于无限权限或永久有效。

Probe outage preserves cursors, sequence gaps, and pending requests. Execution still enforces local identity, policy, budgets, idempotency, and minimum audit; configured risk policy determines whether missing mandatory evidence requires blocking. Report a control as executed only with a verified receipt from the authorized controller. / 探针故障保留游标、序号缺口及未闭环请求；执行侧持续执行本地身份、策略、预算、幂等及最小审计，由已配置风险策略决定缺少必需证据时是否阻断。只有取得授权控制服务的有效执行回执才能报告控制已生效。
