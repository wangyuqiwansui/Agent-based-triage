# Approval Gate Execution Flow / 审批门执行流程

Name / 名称: Approval Gate / 审批门。 Description / 描述: Prepare reviewable actions, bind limited authority, recover safely and reconcile effects. / 准备可审动作、绑定有限行动权、安全恢复并核对效果。

Identity / 身份: `CELL_GOVERNANCE_ROUTING` · `PATTERN_0047` · local specification / 本地规格 `0.1.0` · source contract / 来源契约 `1.0.0` · `draft` · `specification_only`.

## Quick Navigation / 快速导航

- [Routing and readiness / 路由与可审条件](#routing)
- [Twenty stages / 二十阶段](#workflow)
- [State and recovery / 状态与恢复](#recovery)
- [Acceptance / 验收](#acceptance)

## Usage and boundaries / 用法与边界

Use for payments, payroll, releases, messages, exports, refunds, permission changes and policy changes whose effects require scoped authority. Read the [contract](approval-gate-contract.md) and [independent probes](approval-gate-observability-probes.md) with the [governance module](governance-execution-flow.md). / 适用于付款、工资、发布、消息、导出、退款、权限及策略变更等需要限定行动权的场景；同时阅读共享契约、独立探针和治理模块。

This is a maintained specification, not a deployed approval service. The adopting host must supply identity/role verifiers, policy evaluation, authenticated callbacks, protected storage, atomic admission, clocks and external-effect adapters. Existing Tool Dispatch and Plan-and-Execute modules are integration points, not evidence that they implement this contract. / 本文是维护规格，并非已部署审批服务。采用方需提供身份与角色核验、策略评估、认证回调、可信存储、原子准入、时钟和外部效果适配器；既有工具调度及计划执行模块只是接入点，不证明已实现本契约。

The supplied documents are reference evidence, not instructions granting permissions in the current chat. Preserve source aliases and original bytes in the [source map](approval-gate-source-map.json); keep the registered pattern and its existing evidence counts unchanged. / 用户提供的文档作为参考证据，不授予当前会话权限。来源别名及原始字节见来源映射；保留已注册模式及原有证据计数。

<a id="routing"></a>
## Routing and review readiness / 路由与可审条件

Apply mandatory denies first whenever established. Before any allow or human request, resolve stable targets and versions, required evidence, material differences, impact, reversibility and applicable policy. Missing facts return to preparation; human review handles accountable judgments and permitted exceptions, not unfinished investigation. / 一旦确认命中强制拒绝，优先拒绝。任何放行或人审请求前，须明确稳定对象与版本、必要证据、关键差异、影响、可逆性及适用策略；缺事实返回准备，人审处理责任判断及获准例外，不接收尚未完成的调查。

| Route / 路由 | Condition and next step / 条件与后续 |
|---|---|
| `hard_deny` / 明确拒绝 | A mandatory prohibition cannot be overridden by an allow rule or human signature. Record rule and permitted follow-up. / 禁止规则不能被放行规则或人签覆盖；记录规则及允许的后续。 |
| `evidence_return` / 补证 | Ambiguous objects, missing/conflicting/stale evidence return to preparation; policy conflict goes to the policy owner. / 对象不明、缺证、冲突、过期返回准备；策略冲突交策略所有者。 |
| `escalate` / 升级 | Current roles lack authority; recompute role, headcount and independence requirements. No implied allow. / 当前角色权限不足，重算角色、人数及独立性；不隐含放行。 |
| `human_approval` / 人审 | Reviewable proposal exceeds explicit automatic authority; create a bound card and durable waiting checkpoint. / 可审提案超出明确自动权限，建立绑定审批卡及持久等待检查点。 |
| `auto_allow` / 自动放行 | An explicit current rule covers the complete action with all controls satisfied. Issue a limited machine receipt and revalidate before execution. / 当前明确规则覆盖完整动作且控制满足，签发有限机器回执并在执行前重检。 |
| `wait_external` / 等待外部条件 | A permitted action awaits a window, balance or ticket condition. Persist the dependency and re-evaluate on wake-up. / 获准动作需等待窗口、余额或工单条件，持久化依赖并在唤醒时重新评估。 |

Precedence / 优先级: `hard_deny > evidence/policy conflict > escalation > human_approval > auto_allow`; `wait_external` grants no authority and is evaluated before dispatch. This refines the original deny/allow/gate overview without changing the matrix coordinate. / 等待外部条件不授予权限，派发前必须满足；这是对原拒绝/放行/人工门概览的细化，不改变矩阵坐标。

The approval card shows actor/delegation, action/tool/version/environment, target manifest, amount/count/currency, highlighted changes, verified evidence and freshness, unresolved permitted risks, impact/reversal cost, exact scope/expiry/use limit/conditions, required roles and recommendation reasons. Minimize sensitive plaintext. / 审批卡展示主体与委托、动作工具版本环境、对象清单、金额数量币种、突出差异、已核验证据与时效、允许人判的未决风险、影响和撤销成本、精确范围及期限次数条件、所需角色与建议依据；最小化敏感明文。

<a id="workflow"></a>
## Workflow / 执行流程

`AGE01–AGE20` map source stages 13.1–13.20. The workflow owns state and authorization; probes only observe and propose. / 这些编号对应来源 13.1–13.20 阶段；流程掌握状态和行动权，探针只观测与建议。

<!-- approval:execution_steps:start -->
| ID | Source / 来源 | Definition / 定义 |
|---|---|---|
| AGE01 | ## 13.1 阶段一：接收业务意图 | Capture intent and immutable origin, create trace/run/intent identities, record actor and delegation, distinguish advice from effects. / 接收并冻结原始意图引用，创建链路、运行与意图标识，记录主体委托，区分建议查询与外部动作。 |
| AGE02 | ## 13.2 阶段二：规范化动作 | Normalize action type, tool/version/environment, defaults and implicit scope; calculate quantity/value and flag policy or privilege changes. / 规范动作类型、工具版本环境，展开默认值和隐式范围，计算数量金额，识别策略变更及权限扩大。 |
| AGE03 | ## 13.3 阶段三：确认对象与版本 | Resolve stable object IDs, versions and digests; freeze batch manifests and query/result snapshots; reject ambiguous names and ineligible targets. / 解析稳定对象标识、版本和摘要，冻结批量清单及查询结果快照，拒绝模糊名称并检查对象可操作性。 |
| AGE04 | ## 13.4 阶段四：收集证据 | Load required evidence, independently verify high-risk changes, record sources/versions/times/expiry, and retain missing/conflicting/untrusted items. / 加载必需证据，对高风险变化独立核验，记录来源版本时间及有效期，保留缺失冲突和低可信证据。 |
| AGE05 | ## 13.5 阶段五：计算差异和影响 | Compare the baseline, highlight additions/removals/replacements/scope expansion, and calculate impact, external visibility and reversal cost. / 与基线比较新增删除替换及扩围，计算金额数量、外部可见性、潜在影响和撤销补偿成本，突出关键差异。 |
| AGE06 | ## 13.6 阶段六：检查可审条件 | Require clear targets, complete evidence, visible impact/differences/reversibility and determinable policy; otherwise supplement, clarify, resolve policy or stop. / 要求对象明确、证据完整、影响差异可逆性可见、策略可确定；否则补证、澄清、处置策略冲突或停止。 |
| AGE07 | ## 13.7 阶段七：策略匹配与风险路由 | Snapshot current policy, apply denies first, determine automatic authority or roles/counts/hierarchy, separation, expiry, usage and rechecks; explain the route. / 冻结当前策略，先匹配拒绝规则，再确定自动权限或角色人数层级、职责分离、有效期次数和重检项，解释路由原因。 |
| AGE08 | ## 13.8 阶段八：生成审批卡 | For human review bind the card/request to proposal and policy digests; show differences, evidence, consequences and exact scope with minimal sensitive data. / 人审时将审批卡请求绑定提案及策略摘要，展示差异证据影响和精确范围，最小化敏感披露。 |
| AGE09 | ## 13.9 阶段九：分配审批者 | Select by current role and authority; verify conflicts, separation and substitution/delegation, document assignments and set timeout/escalation. / 按当前角色权限分配，核验利益冲突、职责分离及代班委托，记录分配理由并设置超时升级路线。 |
| AGE10 | ## 13.10 阶段十：持久化等待状态 | Durably save run, proposal/policy digests, request/decisions/missing roles, expiry, resume point, preconditions, state version and replay keys before waiting. / 等待前持久化运行、提案策略摘要、请求决定及缺失角色、期限、恢复点、业务前提、状态版本及重放幂等信息。 |
| AGE11 | ## 13.11 阶段十一：接收审批决定 | Authenticate each callback and current role, request binding, expiry/revocation and separation; deduplicate decisions; record allow/deny/conditions/evidence return. / 认证回调身份与当前角色，核验请求绑定、期限撤权及职责分离，幂等记录允许拒绝附条件或补证决定。 |
| AGE12 | ## 13.12 阶段十二：计算会签结果 | Count valid distinct identities and required roles, enforce all counts, veto/withdrawal and compatible conditions; wait, allow, deny, invalidate, escalate or re-propose. / 统计有效不同身份及所需角色人数，检查拒绝撤回与条件相容，决定继续等待、允许、拒绝、失效、升级或重建提案。 |
| AGE13 | ## 13.13 阶段十三：签发治理回执 | Issue only a policy-compliant trusted signed receipt binding decision, proposal/policy, decision references, scope, expiry, usage and conditions. / 仅在策略满足时签发可信签名回执，绑定最终决定、提案策略、决定引用、范围、期限、次数及条件。 |
| AGE14 | ## 13.14 阶段十四：恢复运行 | Load the latest trusted checkpoint, bind the resume request to the run, fetch current proposal/policy/business facts and enter revalidation rather than tool execution. / 加载最新可信检查点，核验恢复请求和运行，重读当前提案策略与业务事实，从重新验证恢复而非直接调用工具。 |
| AGE15 | ## 13.15 阶段十五：执行前重新验证 | Recheck trusted allow receipt, exact proposal/policy bindings, expiry/usage, current quorum, business conditions, object/environment/scope and idempotency; refuse on failure. / 重检可信允许回执、提案策略精确绑定、期限次数、当前会签、业务前提、对象环境范围及幂等状态；失败不得执行。 |
| AGE16 | ## 13.16 阶段十六：原子消费许可 | Atomically compare receipt/state versions, verify availability, consume usage, reserve idempotency and persist an execution attempt; concurrent losers do not dispatch. / 原子比较回执与状态版本、确认可用、消费次数、预留幂等键并持久化执行尝试；并发失败方不能再次派发。 |
| AGE17 | ## 13.17 阶段十七：执行受控动作 | Execute only approved tool/version, environment, parameters, objects, amount/count, identity and time window; never append targets at runtime. / 只执行已批工具版本、环境、参数、对象、金额数量、身份及窗口，不得临时追加对象或扩大范围。 |
| AGE18 | ## 13.18 阶段十八：核对实际效果 | Query destination effects, compare requested/actual digests and scope, record partial/duplicate/excess/missing results and external IDs; success requires reconciliation. / 查询目的端效果，比较请求与实际摘要范围，记录部分成功、重复、超额、遗漏及外部引用；核对一致才标记成功。 |
| AGE19 | ## 13.19 阶段十九：失败与补偿 | Reconcile uncertain outcomes before retry, retry only unperformed effects within authority, govern compensation and escalate unresolved incidents. / 不确定结果先对账再重试，仅在有效权限内重试未发生效果；补偿另行受治理，未决事故升级处置。 |
| AGE20 | ## 13.20 阶段二十：归档与学习 | Archive all intent/proposal/evidence/policy/approval/receipt/checkpoint/attempt/effect/compensation/supplement versions, final state and reason; policy learning is separately governed. / 归档意图、提案、证据、策略、决定回执、检查点、尝试效果补偿与补全版本及最终原因；策略学习另走治理流程。 |
<!-- approval:execution_steps:end -->

<a id="recovery"></a>
## State, recovery and concurrency / 状态、恢复与并发

```text
draft -> preparing -> ready_for_gate
preparing -> evidence_incomplete | policy_conflict
ready_for_gate -> auto_allowed | pending | rejected | escalated
pending -> partially_approved -> allowed
pending | partially_approved -> rejected | expired | invalidated
allowed | auto_allowed -> revalidating -> executing
revalidating -> evidence_incomplete | invalidated | expired | rejected
executing -> succeeded | failed
failed -> compensating | escalated | closed
compensating -> compensated | escalated
succeeded | compensated | rejected | expired -> closed
```

Arrows require verified guards; they are not unconditional transitions. `pending` and `partially_approved` never jump to `executing`. `wait_external` is a checkpointed wait reason, not a seventh allow state. Record `unknown` and `partial` as effect certainty independent of workflow state, and retain unresolved obligations if a run is administratively closed. / 箭头均需核验条件，不是无条件转移；待审批及部分批准不得直达执行。等待外部条件是检查点等待原因，不是另一放行状态。效果未知和部分成功作为独立效果确定性保存；管理性关闭仍须保留未决责任。

Verify each callback against the bound request, current identity/role/delegation, request expiry and segregation rules. Deduplicate by decision identity and authenticated actor; two accounts for one person do not satisfy distinct-person quorum. Preserve invalid, late, duplicate and withdrawn decisions for audit without counting them. Reject/veto takes precedence; conflicting conditions escalate. Sequential roles require prior-stage completion. / 回调核验绑定请求、当前身份角色委托、请求时效及职责分离；按决定身份和认证主体去重，同一人的两个账号不满足不同人员会签。无效、迟到、重复、撤回决定保留审计但不计票；拒绝优先，条件冲突升级；分阶段审批须完成前序。

Persist the proposal/policy digests, received decisions, missing roles, expiry, resume node, business preconditions, state version and deduplication keys **before waiting**. On restart load the latest trusted checkpoint, verify run/tenant/version, re-read live facts and resume at revalidation. A missing or corrupt checkpoint requires explicit recovery, never guessed execution. / 等待前持久化提案策略摘要、已收决定、缺失角色、期限、恢复节点、业务条件、状态版本及去重键；重启加载最新可信检查点，核验运行租户版本，重读当前事实并从重检恢复；检查点缺失或损坏需明确恢复，不猜测执行。

At admission, atomically compare current state/receipt versions and revocation, consume the allowance, reserve the durable business idempotency key and create the execution intent/attempt. A losing concurrent call returns the existing attempt or a structured rejection; it never dispatches again. The executor binds the final payload to the proposal and fences current authority immediately before the side-effect boundary. Where live resource versions cannot be locked, require adapter preconditions/conditional writes or explicit residual-risk handling; a prior check alone does not eliminate TOCTOU. / 准入时原子比较状态与回执版本及撤销状态、消费许可、预留持久业务幂等键并创建执行意图及尝试。并发失败方返回已有尝试或结构化拒绝，不再派发。执行器把最终载荷绑定提案，并在副作用边界前核验实时权限；资源无法锁定时须有适配器条件写或明确剩余风险处置，先前检查本身不能消除检查与使用的时间差。

A crash after consumption may occur before or after external submission. Recover the durable attempt and query the destination using the original business key; do not reset the receipt counter or create a fresh key to retry. Retry only confirmed unperformed effects within valid authority; record the retry as the same admitted operation. For partial success reconcile per object, never repeat confirmed successes. Compensation is a new governed action with its own scope and receipt where required. / 消费后崩溃可能发生在外部提交前后；恢复持久尝试并用原业务键查询目的端，不能重置回执计数或换键重试。只在权限仍有效时重试已确认未发生的效果，并归属同一已准入操作；部分成功逐对象对账，不重复已成功对象。补偿是新的受治理动作，需要时有独立范围和回执。

## Validation and drift / 验证与漂移

Require trusted receipt signature/issuer, allowed decision, no revocation, current proposal and policy digest/version bindings, valid time/use limits, current approver quorum and separation, matching actor/tool/environment/targets/conditions, and fresh business preconditions. Automatic receipts prove an applicable machine rule instead of fabricated human decisions. / 必须核验可信回执签名与签发者、允许决定、未撤销、当前提案策略摘要版本、期限次数、当前会签及职责分离、匹配主体工具环境对象条件和新鲜业务前提；机器回执证明适用自动规则，不能伪造人工签字。

Structured reasons / 结构化原因: `proposal_digest_mismatch`, `policy_digest_mismatch`, `receipt_expired`, `usage_limit_exhausted`, `approver_role_invalid`, `business_precondition_changed`, `environment_mismatch`, `tool_version_mismatch`, `target_scope_changed`, `receipt_revoked`, `idempotency_key_consumed`. Adapter extensions include `untrusted_receipt`, `checkpoint_invalid`, `effect_unknown`; version their mapping. / 后三项是本地适配扩展，须版本化映射。

Changing targets, count, amount/currency, destination/account/recipient, tool/version, environment, permissions, execution order/window, business conditions, policy, reversibility or visibility invalidates the old authorization. Generate a new proposal/version, calculate the difference and route again. Pure layout or non-executing commentary can be excluded only by a declared canonicalization profile. / 对象、数量、金额币种、目的地账户收件人、工具版本、环境、权限、执行顺序窗口、业务条件、策略、可逆性或可见性改变，旧授权失效；生成新提案或版本、计算差异并重新路由。只有声明的规范化配置才能排除纯排版及不参与执行的注释。

Policy changes use independent proposals showing old/new rules, historical simulation, expanded automatic exposure, worst-case impact, rollout time/scope, observation and rollback. A beneficiary cannot unilaterally relax a rule and approve the affected action. An approval threshold does not create account balance or shared budget; apply [governance controls](governance-execution-flow.md) separately. / 策略变更独立提案，展示前后规则、历史模拟、新增自动暴露、最坏影响、生效时间范围、观察及回滚。受益者不得单独放宽规则并批准受益动作。审批阈值不创造余额或共享预算，另行执行治理控制。

## Scenarios and output / 场景与输出

| Scenario / 场景 | Bind and recheck / 绑定与重检 |
|---|---|
| Supplier payment / 供应商付款 | Vendor, invoice/order, amount/currency, account-change evidence and independent callback verification. / 供应商、发票订单、金额币种、账户变化证据及独立回拨核验。 |
| Payroll / 工资 | Batch version, employee manifest, amount, reversals/leavers, payroll and treasury roles. / 批次版本、人员清单、金额、冲正离职状态及薪酬资金角色。 |
| Release / 发布 | Commit/build digest, environment, tests, dependencies, change ticket, window and rollback. / 代码构建摘要、环境、测试依赖、变更单、窗口及回滚。 |
| Message / 消息 | Body, attachment, recipient set, channel, schedule and sensitive disclosures. / 正文附件、收件人集合、渠道、定时及敏感披露。 |
| Export / 导出 | Query and result snapshot, fields, rows, classification, recipient/destination, encryption and retention. / 查询与结果快照、字段行数、分级、接收方目的地、加密及保留期。 |
| Refund / 退款 | Order set, per-item and total amount, eligibility, fraud signals and duplicate-effect checks. / 订单集合、单笔总额、资格、欺诈信号和重复效果检查。 |
| Permission / 权限 | Subject, resource, role, exact privileges, environment, duration and duty conflicts. / 主体资源角色、精确权限、环境期限及职责冲突。 |
| Policy / 策略 | Before/after rule, scope/threshold/role/expiry/use-limit changes and independent governance approval. / 前后规则、范围阈值角色期限次数变化及独立治理批准。 |

Source payroll counterexample / 来源工资反例: `798 / CNY 13,706,097.00` becomes `800 / CNY 13,744,541.00`; delta / 差额 `38,444.00`. Old receipt binds the old digest; refuse it, show the added people/delta and route the new proposal. This example produces **no payment** and is not an executed test. / 旧回执绑定旧摘要，拒用并展示新增人员及差额，重新路由；该示例不产生付款，也不是已执行测试。

Always output `run_id`, `trace_id`, proposal and policy references, route, final state/decision, receipt, execution/effect/compensation references, supplement references and close time/reason. A non-executed run records why; `allowed` means permission only, and `succeeded` requires authoritative effect reconciliation. Preserve all versions, invalidated receipts and failed attempts. / 始终输出运行链路、提案策略引用、路由、最终状态决定、回执、执行效果补偿引用、补全引用及关闭时间原因；未执行明确原因。允许仅代表许可，成功需权威效果核对；保留所有版本、失效回执和失败尝试。

<a id="acceptance"></a>
## Acceptance / 验收

All cases are integration requirements with `not_executed` status. Documentation synchronization tests establish asset fidelity, not receipt security, crash recovery or external-effect correctness. / 所有用例均为未执行的集成要求；文档同步测试验证资产保真，不验证回执安全、崩溃恢复或外部效果正确性。

<!-- approval:execution_cases:start -->
| ID | Source / 来源 | Definition / 定义 |
|---|---|---|
| AGET01 | 同一提案在满足策略时能够正确自动放行或进入人审； | Route the same complete proposal correctly under the applicable automatic or human policy. / 同一提案在满足策略时能够正确自动放行或进入人审；<br>`not_executed` / 未执行 |
| AGET02 | 多人会签未满足前不能签发允许回执； | Never issue an allow receipt before required quorum is met. / 多人会签未满足前不能签发允许回执；<br>`not_executed` / 未执行 |
| AGET03 | 无权限审批者的决定不计入通过； | Do not count an unauthorized approver toward approval. / 无权限审批者的决定不计入通过；<br>`not_executed` / 未执行 |
| AGET04 | 提案任一语义字段变化后旧回执失效； | Invalidate old authorization after any semantic proposal change. / 提案任一语义字段变化后旧回执失效；<br>`not_executed` / 未执行 |
| AGET05 | 策略版本变化后旧回执按规则失效； | Invalidate old authorization according to policy-version rules. / 策略版本变化后旧回执按规则失效；<br>`not_executed` / 未执行 |
| AGET06 | 回执过期后执行器拒绝执行； | Refuse executor use after receipt expiry. / 回执过期后执行器拒绝执行；<br>`not_executed` / 未执行 |
| AGET07 | 一次性回执不能被并发消费两次； | Allow only one concurrent consumption of a single-use receipt. / 一次性回执不能被并发消费两次；<br>`not_executed` / 未执行 |
| AGET08 | 恢复时会重新检查业务前置条件； | Recheck business preconditions on resume. / 恢复时会重新检查业务前置条件；<br>`not_executed` / 未执行 |
| AGET09 | 部分成功能够生成可核对的实际效果记录； | Produce reconcilable per-object effects for partial success. / 部分成功能够生成可核对的实际效果记录；<br>`not_executed` / 未执行 |
| AGET10 | 探针补全包可被采纳、部分采纳或拒绝，并保留记录。 | Record accepted, partially accepted and rejected supplements. / 探针补全包可被采纳、部分采纳或拒绝，并保留记录。<br>`not_executed` / 未执行 |
| AGET11 | 发起者不能绕过职责分离； | Prevent proposer bypass of separation of duties. / 发起者不能绕过职责分离；<br>`not_executed` / 未执行 |
| AGET12 | 审批者不能批准超出角色权限的范围； | Prevent approvers from authorizing beyond their role scope. / 审批者不能批准超出角色权限的范围；<br>`not_executed` / 未执行 |
| AGET13 | 执行器不接受未签名、已撤销或来源不可信的回执； | Reject unsigned, revoked or untrusted receipts. / 执行器不接受未签名、已撤销或来源不可信的回执；<br>`not_executed` / 未执行 |
| AGET14 | 工具版本、环境和对象范围与批准不一致时拒绝执行； | Refuse mismatched tool/version, environment or target scope. / 工具版本、环境和对象范围与批准不一致时拒绝执行；<br>`not_executed` / 未执行 |
| AGET15 | 规则变更不能由受益代理单独批准； | Prevent beneficiary-only approval of rule changes. / 规则变更不能由受益代理单独批准；<br>`not_executed` / 未执行 |
| AGET16 | 所有高风险执行均可追溯到有效回执。 | Trace every high-risk execution to a valid receipt. / 所有高风险执行均可追溯到有效回执。<br>`not_executed` / 未执行 |
| AGET17 | 服务重启后能够恢复等待状态； | Restore durable waiting state after service restart. / 服务重启后能够恢复等待状态；<br>`not_executed` / 未执行 |
| AGET18 | 重复审批回调不会重复计数； | Duplicate approval callbacks do not double count. / 重复审批回调不会重复计数；<br>`not_executed` / 未执行 |
| AGET19 | 重复恢复请求不会重复执行； | Duplicate resume requests do not duplicate execution. / 重复恢复请求不会重复执行；<br>`not_executed` / 未执行 |
| AGET20 | 外部调用超时后能先查状态再决定重试； | Query external state after a timeout before deciding to retry. / 外部调用超时后能先查状态再决定重试；<br>`not_executed` / 未执行 |
| AGET21 | 检查点损坏时系统选择停止，而不是猜测继续。 | Stop on corrupt checkpoints instead of guessing continuation. / 检查点损坏时系统选择停止，而不是猜测继续。<br>`not_executed` / 未执行 |
| AGET22 | 每个关键阶段均有事件； | Emit events at every critical stage. / 每个关键阶段均有事件；<br>`not_executed` / 未执行 |
| AGET23 | 事件可通过 `trace_id`、`run_id` 和对象标识关联； | Correlate events with trace/run and object identities. / 事件可通过 `trace_id`、`run_id` 和对象标识关联；<br>`not_executed` / 未执行 |
| AGET24 | 提案、策略、回执和实际效果摘要可比对； | Compare proposal, policy, receipt and actual-effect digests. / 提案、策略、回执和实际效果摘要可比对；<br>`not_executed` / 未执行 |
| AGET25 | 审批等待时间、失效率、漂移率和绕过尝试可计算； | Derive waiting, invalidation, drift and bypass-attempt measures from evidence. / 审批等待时间、失效率、漂移率和绕过尝试可计算；<br>`not_executed` / 未执行 |
| AGET26 | 数据缺口可由探针形成补全包； | Generate source-backed supplement packages for data gaps. / 数据缺口可由探针形成补全包；<br>`not_executed` / 未执行 |
| AGET27 | 补全包不覆盖原始记录。 | Never overwrite original records with supplements. / 补全包不覆盖原始记录。<br>`not_executed` / 未执行 |
<!-- approval:execution_cases:end -->

## Source coverage / 来源覆盖

Each complete source chapter is fingerprinted, including non-goals, templates, failure handling and pattern composition; exact excerpts are in the immutable snapshot. The maintained sections above interpret the source with the explicit refinements in the contract. / 完整来源章节均有指纹，覆盖非目标、模板、失败处理及模式组合；精确原文在不可变副本中，维护内容按共享契约中的明确细化解释来源。

Display headings normalize the source's framework spelling to Harness; original titles and bytes remain in the source map and snapshots. / 展示标题统一使用 Harness 的规范拼写；来源映射及副本保留原始标题与字节。

<!-- approval:execution_sections:start -->
| ID | Source / 来源 | Definition / 定义 |
|---|---|---|
| AGES01 | # 1. 文档目的 | Purpose / 文档目的 |
| AGES02 | # 2. Harness 框架映射 | Framework mapping / Harness 框架映射 |
| AGES03 | # 3. 模式目标 | Pattern goals / 模式目标 |
| AGES04 | # 4. 非目标 | Non-goals / 非目标 |
| AGES05 | # 5. 核心原则 | Core principles / 核心原则 |
| AGES06 | # 6. 角色与责任 | Roles and responsibilities / 角色与责任 |
| AGES07 | # 7. 稳定标识 | Stable identifiers / 稳定标识 |
| AGES08 | # 8. 共享数据契约 | Shared object contracts / 共享数据契约 |
| AGES09 | # 9. 风险输入模型 | Risk inputs / 风险输入模型 |
| AGES10 | # 10. 路由结果 | Routing outcomes / 路由结果 |
| AGES11 | # 11. 审批卡结构 | Approval card / 审批卡结构 |
| AGES12 | # 12. 状态机 | State machine / 状态机 |
| AGES13 | # 13. 标准执行流程 | Twenty execution stages / 标准执行流程 |
| AGES14 | # 14. 治理回执验证规则 | Receipt validation / 治理回执验证规则 |
| AGES15 | # 15. 提案漂移处理 | Proposal drift / 提案漂移处理 |
| AGES16 | # 16. 多人会签与层级审批 | Quorum and hierarchical approval / 多人会签与层级审批 |
| AGES17 | # 17. 等待、恢复与并发 | Waiting, recovery and concurrency / 等待、恢复与并发 |
| AGES18 | # 18. 自动放行 | Automatic allowance / 自动放行 |
| AGES19 | # 19. 明确拒绝 | Mandatory denial / 明确拒绝 |
| AGES20 | # 20. 策略变更的审批门 | Governance of policy changes / 策略变更的审批门 |
| AGES21 | # 21. 与工作流可观测性探针的交互 | Probe interaction / 与工作流可观测性探针的交互 |
| AGES22 | # 22. 标准事件输出 | Standard events / 标准事件输出 |
| AGES23 | # 23. 不同场景的配置轮廓 | Scenario profiles / 不同场景的配置轮廓 |
| AGES24 | # 24. 失败处理 | Failure handling / 失败处理 |
| AGES25 | # 25. 反模式 | Anti-patterns / 反模式 |
| AGES26 | # 26. 最小可用实现 | Minimum implementation / 最小可用实现 |
| AGES27 | # 27. 验收标准 | Acceptance requirements / 验收标准 |
| AGES28 | # 28. 示例：工资清单在批准后变化 | Payroll drift example / 示例：工资清单在批准后变化 |
| AGES29 | # 29. 配置模板 | Configuration example / 配置模板 |
| AGES30 | # 30. 输出契约 | Run output / 输出契约 |
| AGES31 | # 31. 与其他工程模式的组合 | Pattern composition / 与其他工程模式的组合 |
| AGES32 | # 32. 总结 | Summary / 总结 |
<!-- approval:execution_sections:end -->
