# Runtime Action Governance Execution Flow / 运行时行动权治理执行流程

Name / 名称: Runtime Action Governance / 运行时行动权治理

Description / 描述: Compose existing approval, impact, commitment and audit controls around each concrete external action. / 围绕每个具体外部动作组合现有审批、影响范围、承诺与审计控制。

Source document version / 来源文档版本: `0.1.0`; shared protocol / 共享协议: `GOV_BOUNDARY_OBS` `1.0.0`.

Status / 状态: **Specification only; no live identity, approval, payment or budget-ledger adapters. / 仅为规格；未接入真实身份、审批、支付或预算账本适配器。**

## Quick Navigation / 快速导航

- [Scope and identity / 范围与身份](#scope-and-identity--范围与身份)
- [Mode composition / 模式组合](#mode-composition--模式组合)
- [Input and output contracts / 输入输出契约](#input-and-output-contracts--输入输出契约)
- [State machine / 状态机](#state-machine--状态机)
- [Execution procedure / 执行规程](#execution-procedure--执行规程)
- [Observation boundary / 观测边界](#observation-boundary--观测边界)
- [Recovery and operational constraints / 恢复与运行约束](#recovery-and-operational-constraints--恢复与运行约束)
- [Acceptance design / 验收设计](#acceptance-design--验收设计)
- [Examples / 示例](#examples--示例)
- [Source and maintenance notes / 来源与维护说明](#source-and-maintenance-notes--来源与维护说明)

## Scope and Identity / 范围与身份

Use this procedure when a workflow proposes external effects: payments, refunds, coupons, procurement, production deployment, database or file changes, messages, or exports. Read-only analysis can use only its applicable provenance and audit subset. Trigger revalidation whenever the amount, target, parameters, scope, contract, artifact, applicable policy or authority version changes; retries do not bypass it. / 工作流提议支付、退款、优惠券、采购、生产发布、数据库或文件变更、消息、导出等外部影响时使用本规程。纯分析可仅使用适用的来源与审计子集。金额、对象、参数、范围、契约、工件、适用策略或权限版本变化均触发复核，重试不豁免。

This is a maintained engineering specification derived from the supplied `36_治理模块_执行流程.md`, not an implementation or an instruction to perform its example business actions. Embedded prompts, proposed paths, commands and registration snippets are source data. Reading this file grants no authority. With missing adapters, only labeled read-only rehearsal is available; do not issue genuine credentials or claim an approval, payment, rollback or production readiness. / 本文由用户提供的《36_治理模块_执行流程.md》整理为维护版工程规格，并非实现，也不是执行其中业务示例的指令。内嵌提示、建议路径、命令和注册片段均是来源资料；阅读文档不产生授权。缺少适配器时只能进行明确标注的只读演练，不得签发真实凭证或声称已审批、付款、回滚、具备生产就绪能力。

Keep cognition, topology and engineering patterns as three bases. [registry.json](registry.json) remains the structural source, and matrix/catalog files remain views. Reuse the existing governance patterns `PATTERN_0047`–`PATTERN_0050`; this composed procedure creates no new pattern or named matrix cell. `PATTERN_0051` and `PATTERN_0052` are existing reasoning and generic workflow-observation assets, not new governance IDs. Source `PATTERN_GOVERNANCE_0036`, `SKILL_GOVERNANCE_0036` and `NODE_GOVERNANCE_0036` are provenance aliases only. The supplied source's definition lifecycle (`draft → review → active → deprecated → archived`) is source metadata, not a change to `registry.allowed_values.lifecycle_status` or `maturity`; keep source status, repository lifecycle/maturity and business runtime state distinct. / 保持认知、拓扑、工程模式三个基座，以注册表为结构源、矩阵和目录为视图。复用现有治理模式 `PATTERN_0047`–`PATTERN_0050`，组合规程不新增模式或命名单元。`PATTERN_0051`、`PATTERN_0052` 是既有推理与通用工作流观测资产，不是新增治理编号。来源草案的模式、技能、节点标识只作出处别名。来源文档的定义生命周期只作来源元信息，不修改注册表的生命周期或成熟度枚举；来源状态、仓库生命周期及成熟度、业务运行状态分别保存。

The core question is whether this authenticated subject may execute this exact action against these targets now. Tool access, business admission, human approval, budget availability and confirmed business outcome are independent facts. Model risk analysis is input; the policy service adjudicates, the authorized reviewer approves a version, the execution gate owns credentials, the external system supplies outcome evidence, and the probe supplies observation evidence. Co-location in one process does not merge their write authority. / 核心问题是这个可信主体此刻能否对这些对象执行这一版动作。工具访问、业务准入、人工批准、预算可用及业务结果已确认是独立事实。模型风险分析只是输入；策略服务裁决，有权审批者批准具体版本，执行入口持有凭证，外部系统提供结果，探针提供观测证据；部署在同一进程不合并写权限。

## Mode Composition / 模式组合

| Existing pattern / 既有模式 | Procedure responsibility / 本规程职责 | Constraint / 约束 |
| --- | --- | --- |
| `PATTERN_0047` [Approval Gate / 审批门禁](patterns/governance/governance-routing.md) | Route to allow, deny or human review for the exact content. / 针对精确内容决定允许、拒绝或转人工。 | Approval cannot increase a hard budget or substitute a target. / 批准不能增加硬预算或替换对象。 |
| `PATTERN_0048` [Progressive Commitment / 渐进承诺](patterns/governance/governance-parallel.md) | Merge required independent checks before commitment; use verified evidence for scoped promotion. / 承诺前合并必选独立检查，以核验证据支持范围明确的晋升。 | Earlier success does not grant permanent or cross-domain authority; existing cell-specific ladder rules still apply. / 历史成功不授予永久或跨域权限，仍须遵守该单元已有阶梯规则。 |
| `PATTERN_0049` [Observability Harness / 可观测性框架](patterns/governance/governance-orchestration.md) | Connect proposal, policy, approval, execution and outcome evidence. / 关联提案、策略、审批、执行、结果证据。 | Observation cannot create approval, change balances or relax rules. / 观测不能创造批准、改余额或放宽规则。 |
| `PATTERN_0050` [Blast Radius Control / 爆炸半径控制](patterns/governance/governance-hierarchy.md) | Enforce subject, parent, resource, time-window and concurrency bounds. / 约束主体、父级、资源、时间窗与并发。 | Child authority is the intersection of parent and own grants; allocations cannot multiply the parent budget. / 子权限取父级和自身授权交集，分配不能倍增父预算。 |

Topology placement is composition guidance, not a taxonomy promotion: chain gates each effect; routing cannot shop for weaker policy; parallel branches share parent limits; orchestration cannot bypass the credential-owning gate; loops retain cumulative usage and stable business identity; hierarchy keeps concrete child approval and delegation checks. Governance-chain and governance-loop remain extension candidates where the registry leaves them unnamed. / 拓扑挂载是组合指导，不是分类晋升：链式为每次副作用设闸；路由不能挑较弱规则；并行共享父级限额；编排不得绕过持有凭证的入口；循环保留累计消耗与稳定业务身份；层级保留具体子动作批准和委托核验。注册表未命名的治理链式、循环仍为扩展候选。

Use only the controls applicable to the concrete task. Automatic scope must be configured in advance; absent configuration is not unlimited permission. Human review is required by current risk policy, not by model confidence or a blanket demand to approve every reversible action. / 仅应用具体任务需要的控制。自动执行范围须预先配置，未配置不代表无限权限。是否人工由当前风险策略决定，不由模型信心或对所有可逆动作一概审批决定。

## Input and Output Contracts / 输入输出契约

### Required inputs / 必需输入

| Object / 对象 | Minimum content and missing-data behavior / 最低内容与缺失处理 |
| --- | --- |
| Task contract / 任务契约 | Goal, prohibitions, accountable owner, completion criteria and expiry; no genuine action proposal without a task boundary. / 目标、禁行事项、责任人、完成标准与有效期；无边界不形成真实动作提案。 |
| Identity and delegation / 身份与委托 | Verified user, executor and approver identities, scopes and expiry; self-reported names are insufficient. / 已核验的用户、执行者、审批者身份及范围、期限；自报姓名不足。 |
| Artifact snapshot / 工件快照 | ID, version, full digest, origin and verification status; no unknown content behind a mutable alias. / 标识、版本、完整摘要、来源与核验状态；不得操作可变别名后未知内容。 |
| Action proposal / 动作提案 | Concrete parameters, targets, scope, impact and business idempotency; do not guess missing amounts or targets. / 具体参数、对象、范围、影响与业务幂等身份；不猜缺失金额或对象。 |
| Policy set / 策略集合 | Current effective content, versions, provenance and change approvals; a stale cache is not evidence of current validity. / 当前生效内容、版本、来历与变更批准；旧缓存不证明当前有效。 |
| Capability credential / 权限凭证 | Allowed actions/resources, limits, expiry and revocation version; no effect without current authority. / 可执行动作及资源、限额、期限与撤销版本；无当前权限不产生副作用。 |
| Budget ledger / 预算账本 | Limits, confirmed consumption, pending reservations and unknown-outcome exposure; do not derive spendable funds from logs. / 上限、确认消耗、待执行预留与未知结果占用；不得由日志估算可支出余额。 |
| Tool adapter / 工具适配器 | Allowed operations/parameters, idempotency scope and retention, outcome-query consistency and terminal semantics; missing capability means rehearsal or human handling. / 动作及参数边界、幂等作用域与保留期、结果查询一致性与终态语义；能力缺失则演练或人工处理。 |
| Environment / 运行环境 | Tenant, trusted clock, stop control and durable audit; unavailable mandatory controls block relevant effects. / 租户、可信时间、停止控制与持久审计；必需控制不可用即阻断相关副作用。 |

### Separate proposal, policy and receipt / 分开提案、策略和回执

| Independent object / 独立对象 | Required binding / 必需绑定 |
| --- | --- |
| Proposal / 提案 | ID/version, task/artifact digests, requesting subject, action, normalized parameters, targets/scope, business operation/idempotency identity, impact, risk and its provenance, reversibility, resource precondition version, expiry. / 标识及版本、任务及工件摘要、请求主体、动作、规范参数、对象范围、业务操作及幂等身份、影响、风险及来源、可逆性、资源前置版本、期限。 |
| Policy reference / 策略引用 | ID/version, full content digest, tenant/scope, effective/expiry times, priority and trusted immutable content location. Use every applicable rule. / 标识及版本、完整内容摘要、租户范围、生效及失效时间、优先级与可信不可变内容位置；使用全部适用规则。 |
| Governance receipt / 治理回执 | Receipt ID/control type, proposal digest, policy-set digest, decision-context digest, authenticated decision subject, allow/deny/human-required verdict, reason, issue/expiry times and revocation state. Retain all verdict types. / 回执标识及控制类型、提案摘要、策略集合摘要、裁决上下文摘要、可信裁决主体、允许／拒绝／需人工结论、原因、签发及失效时间、撤销状态；所有结论都留存。 |

Approval records, credentials, reservations, dispatch intents and business results remain separate objects. A valid receipt is not an approval signature, a budget reservation, or proof of success. / 审批记录、权限凭证、额度预留、派发意图和业务结果仍为独立对象。有效回执不等于审批签名、预算预留或成功证明。

Content bindings differ from dynamic conditions. Changes to proposal, applicable policies, material authority or resource preconditions require re-adjudication. Keep decision-time budget snapshots, but validate the current limit and this operation's valid reservation at the final gate; an unrelated balance change does not mechanically invalidate every receipt. Model the automatic-review threshold separately from hard available resources: human approval cannot override the hard budget, and raising a threshold adds no funds. / 内容绑定与动态条件不同。提案、适用策略、关键授权或资源前置版本改变须重新裁决。保留裁决时预算快照，但最终入口验证当前限额和本动作有效预留；无关余额变化不机械否定所有回执。自动审批阈值与硬资源上限分别建模：人工同意不能突破硬预算，提高阈值不增加资金。

### Canonical content and defaults / 规范内容与默认值

Bind the actual payload: amount/currency, payee or target, resource scope, parameters, artifact content, task contract, idempotency identity and preconditions. Represent money as integer minor units or explicit-precision decimals. Fix encoding, key order, null semantics, timestamps and expanded defaults. Sort only business-unordered sets, never ordered operation lists. Approval display and actual dispatch consume the same immutable snapshot. Full digests verify content; short digests are display-only; neither authenticates a sender or approver. / 绑定实际载荷：金额币种、收款人或对象、资源范围、参数、工件内容、任务契约、幂等身份及前置条件。金额用最小单位整数或显式精度十进制。固定编码、字段顺序、空值、时间及默认值展开。只能排序业务无序集合，不能重排有序操作。审批展示和实际派发读取同一不可变快照。完整摘要核验内容，短摘要只供展示；两者均不证明发送者或审批者身份。

The following is illustrative configuration, not a runnable adapter or production authorization. Nulls mean unconnected components. / 以下为示意配置，不是可执行适配器或生产授权；空值表示尚未接入。

```yaml
mode: read_only_rehearsal
allow_external_writes: false
identity_adapter: null
policy_adapter: null
business_adapter: null
budget_ledger_adapter: null
audit_store: null
unknown_policy: block_relevant_writes
unknown_outcome: retain_exposure_and_query_original
promotion: independent_approval_then_new_credential
probe: optional
patch_write_namespaces: [observation_enrichment]
```

Authorized operators configure adapters, budget dimensions, approval routing, retry/query caps, evidence freshness and stop policy before production. The model cannot fill missing values and call them approved. / 生产前由有权主体配置适配器、预算维度、审批路由、重试查询上限、证据时效和停止策略；模型不能自行填值并称其已批准。

### Output package / 输出包

Each result binds task status, item statuses, final valid checkpoint, evidence references, outstanding reservations/exposure, unresolved issues, current owner and next permitted action. Distinguish `pending_approval`, `needs_evidence`, `insufficient_budget`, `unknown_outcome`, `reconciling`, `partial` and `stopped`; a generic failure must not hide effects already produced. / 每份结果绑定任务及分项状态、最后有效检查点、证据引用、未决预留或暴露、未解决问题、当前责任人和下一步允许动作。区分待审批、待证据、预算不足、结果未知、对账中、部分完成、已停止；不得用笼统失败掩盖已产生影响。

Keep adjudication, execution, verification, audit, authority-change and observation-enrichment packages distinct. A call result is not final external confirmation; an audit package does not prove every policy was appropriate; an authority change applies only to its stated scope and term; observation adoption does not rewrite original facts. / 分开裁决、执行、核验、审计、权限调整和观测补全包。调用结果不是外部终态确认，审计包不证明所有规则合理，权限变更只在声明范围和期限内有效，观测采纳不改写原事实。

## State Machine / 状态机

These descriptive state labels specify transitions, not newly registered wire enums or an implemented runtime. / 以下描述性状态规定转换，不是新增线格式枚举，也不代表已有运行时实现。

```text
accepted / 已受理 -> needs_input / 待补输入 | proposal_frozen / 已冻结提案
proposal_frozen / 已冻结提案 -> pending_decision / 待裁决
pending_decision / 待裁决 -> denied / 已拒绝 | pending_approval / 待审批 | pending_budget / 待额度
pending_approval / 待审批 -> denied / 已拒绝 | expired / 已过期 | pending_decision / 重新裁决
pending_budget / 待额度 -> insufficient_budget / 额度不足 | reserved / 已预留
reserved / 已预留 -> final_check / 待最终检查 -> blocked / 已阻断 | intent_recorded / 已建立派发意图
intent_recorded / 已建立派发意图 -> submitted / 已提交 | dispatch_uncertain / 派发状态待查
submitted / 已提交 -> verified_success / 已核实成功 | verified_failure / 已核实失败 | unknown_outcome / 结果未知 | partial / 部分完成
dispatch_uncertain / 派发状态待查 -> reconciling / 对账中
unknown_outcome / 结果未知 -> reconciling / 对账中 -> verified_success / 已核实成功 | verified_failure / 已核实失败 | unknown_outcome / 仍未知
partial / 部分完成 -> item_reconciliation / 分项核验与处置 -> closed / 已关闭 | human_required / 待人工
verified_failure / 已核实失败 -> closed / 已关闭 | separately_authorized_compensation / 独立批准补偿
any stoppable phase / 任一可停止阶段 -> stopped_pending_resolution / 已停止待处置
```

An allow verdict is not a business terminal. Stop prevents new dispatch and does not guarantee recall of requests already sent. A compensation is a separately proposed and authorized business action that may itself fail; it preserves original history. / 允许裁决不是业务终态。停止禁止新派发，不保证撤回已发请求。补偿是单独提案并授权的业务动作，本身可能失败，并保留原操作历史。

<a id="execution-steps"></a>

## Execution Procedure / 执行规程

Source IDs `执01`–`执16` are preserved for traceability. Each node must produce its accountable public result and evidence; a logical node does not require a model call. Never request or record private chain-of-thought. / 保留来源 `执01`–`执16` 编号以便追溯。每节点产出可问责的公开结果和证据，逻辑节点不意味着模型调用；不得请求或记录私密思维过程。

### 执01 — Admit and check environment / 受理与环境自检

Validate tenant, user, executor and delegation; inspect trusted clock, stop control and audit persistence. Register task/run identities and rehearsal versus real mode. Record admission and input gaps. If identity, policy or the final execution gate cannot be verified, produce read-only diagnostics and required connections rather than business writes. / 核验租户、用户、执行者、委托，检查可信时间、停止控制与审计持久化。登记任务和运行身份、演练或真实模式，产出受理事件和输入缺口。身份、策略或最终入口不可核验时输出只读诊断与接入要求，不进行业务写入。

### 执02 — Freeze task and combined boundaries / 建立任务契约和组合边界

Declare goal, permitted/prohibited actions, targets, budgets, completion criteria and failure owner. A batch binds total scope and item IDs; tasks sharing a business subject share applicable budget accounts. Assess the whole action sequence, including cumulative export, repeated compensation and aggregate child spending. Mark unknown impact explicitly; pause or use only a previously approved conservative bound. / 明确目标、允许及禁止动作、对象、预算、完成条件和失败责任人。批次绑定总范围及分项标识，同一业务主体共享适用额度账户。检查整串动作，包括累计导出、重复补偿、子任务总支出。未知影响明确标注，暂停或仅使用预先批准的保守上界。

### 执03 — Freeze the concrete proposal / 冻结具体提案

Build actual parameters from trusted artifacts, verify targets and resource preconditions, then freeze the proposal. Assign one stable business-operation/idempotency identity per logical intent; technical retries retain it. Amount, target or semantic changes create a new proposal version and re-adjudication. A genuinely new business obligation needs new grounds and the previous operation's resolved or explicitly handled status; a new key cannot conceal a retry. / 从可信工件形成实际参数，核验对象和资源前置条件后冻结提案。每个逻辑业务意图有稳定操作及幂等身份，技术重试保留该身份。金额、对象或语义变化形成新提案版本并重裁决。真正新义务须有新依据并处理前次状态，不能以新键掩盖重试。

### 执04 — Resolve current applicable policy / 解析当前生效策略

Fetch immutable current rules from trusted storage and verify scope, version, approval provenance, effective times and revocation. Bind policy-set and decision-context digests. Check budget, approval, authority, resource limits and emergency stop independently. This specification uses mandatory-deny precedence and unmet-human-review blocking; alternative composition algorithms must be explicitly versioned and tested. Conflicting content under one policy ID/version is quarantined. / 从可信存储取得当前不可变规则，核验范围、版本、审批来历、生效时间与撤销，绑定策略集合和裁决上下文摘要。分别检查预算、审批、权限、资源限额及紧急停止。本规格采用强制拒绝优先、必需人工未满足即阻断；其他组合算法须显式版本化并测试。同一策略标识版本出现不同内容时隔离冲突。

### 执05 — Process a separate policy-change branch / 独立处理策略变更

Enter only for an explicit policy-change task submitted by an eligible requester. Record before/after versions, scope, rationale, expiry, proposer, approver and rollback plan. Verify distinct real proposer/approver subjects and the approver's authority; display-name differences do not establish independence. Apply organization rules for common control and reviewer independence where required. A business over-limit result cannot automatically request a wider rule. / 仅在收到明确策略变更任务且申请者有权时进入。记录前后版本、范围、理由、期限、提出者、批准者和回退方案。核验提出及批准者为不同真实主体，且批准者具备相应权限；显示名不同不证明独立。适用时按组织规则检查共同控制人和审批独立性。业务超限不能自动要求放宽规则。

Publish an approved new version while retaining the old one, honor effective times, and return the business proposal to 执04 for a fresh decision. Old receipts do not transfer to new policy. Temporary relaxations expire; emergency exceptions also need independent authority and a record. / 发布合法批准的新版本并保留旧版，遵守生效时间，业务提案回执04重新裁决。旧回执不能迁移到新策略；临时放宽到期失效，紧急例外也须独立授权和记录。

### 执06 — Check authority and impact / 核验行动权与影响范围

Check authenticated credentials, action/resource scope, rule-derived risk, reversibility, per-action limit, target count, concurrency, time window and cumulative usage. Executor self-labeling as low risk is insufficient. Policy owns account keys across tenant, real business subject, resource domain, time window and parent plan; an agent cannot choose weaker accounts by renaming tasks. Child authority intersects parent and own grants; allocated child budgets stay within parent limits. This is feasibility checking, not a reservation. / 检查可信凭证、动作资源范围、规则推导风险、可逆性、单次限额、对象数量、并发、时间窗及累计使用。执行者自标低风险不足。策略决定跨租户、真实业务主体、资源域、时间窗、父计划的账户键，Agent 不能改任务名选择更松账户。子权限取父级及自身交集，子预算分配受父限额限制。此处只预检，不等于已预留。

### 执07 — Decide and obtain required approval / 裁决与人工审批

Issue allow, deny or human-required receipts bound to proposal and policies. Approval displays the actual version's targets, amounts/impact, cumulative exposure, irreversible risks, anomalies and changes, not only a model summary. Verify reviewer authority and bind approval to content, policy context, expiry and identity. Changes while waiting require new review; an old click never approves a new request. After approval, return to the decision service for a current allow receipt. Record denial, timeout and revocation; silence or generated summaries are not approval. / 生成绑定提案与策略的允许、拒绝或需人工回执。审批展示实际版本的对象、金额或影响、累计占用、不可逆风险、异常及差异，不只展示模型摘要。核验审批权限，批准绑定内容、策略上下文、期限及身份。等待期变更须重新审查，旧点击不批准新请求。人工同意后回裁决服务生成当前允许回执；拒绝、超时和撤销留痕，沉默或自动总结不是批准。

### 执08 — Reserve budget atomically / 原子预留额度

Use authoritative conditional ledger updates across every applicable dimension. All branches, executors and retries share the logical operation's reservation; do not reserve twice or independently subtract stale balances. Admit only if the following holds for each dimension under the current limit. / 在每个适用维度使用权威账本条件更新。所有分支、执行者和重试共享逻辑操作占用，不重复预留，也不分别按旧余额扣减。每个维度均满足当前上限后才准入。

```text
confirmed_consumption + pending_reservations + unknown_outcome_exposure <= current_admission_limit
已确认消耗 + 待执行预留 + 结果未知占用 <= 当前准入上限
allocatable = current_admission_limit - confirmed_consumption - pending_reservations - unknown_outcome_exposure
可分配额度 = 当前准入上限 - 已确认消耗 - 待执行预留 - 结果未知占用
```

The three buckets are mutually exclusive transitions for the same exposure. Keep currencies and units separate. A new time window does not erase unsettled exposure: retain the original account and apply a configured cross-window in-flight bound. On reservation failure, wait, revise scope and re-review, or transfer to a human; never take another task's reservation. If limits fall below existing exposure, stop new admissions and handle that exposure separately; do not rewrite historically lawful spending as a past violation or dispatch new work under the old limit. / 三类占用对同一暴露互斥迁移，币种和单位分别核算。新时间窗不抹去未决暴露，保留原账户并应用已配置的跨窗口在途限制。预留失败则等待、缩小范围重审或转人工，不能夺用其他任务占用。限额下调至既有暴露之下时停止新准入并单独处置，不能把历史合法支出改写为过去违规，也不能按旧限额派发新动作。

### 执09 — Revalidate and persist dispatch intent / 最终复核与持久化派发意图

At the sole credential-owning execution gate, recompute actual payload binding and validate current policies, allow receipt, required human approval, credential validity/revocation, reservation, resource preconditions, idempotency and stop state. Changed content or missing mandatory evidence blocks dispatch with an explicit re-adjudication, evidence or human route. Prior UI, prompt or upstream checks do not replace this gate. / 在唯一持有业务凭证的执行入口重算实际载荷绑定，核验当前策略、允许回执、必需人工批准、凭证有效撤销、额度预留、资源前置状态、幂等及停止状态。内容改变或必需证据缺失阻断派发，明确转重裁决、补证或人工。页面、提示词或上游检查不替代最终闸。

Atomically commit the locally transactional final validation, reservation association and durable intent. The intent binds immutable payload reference, stable business identity, fence version, receipt and reservation. Failure to persist the intent blocks the external send. This local transaction does not include the remote business system. / 在本地可事务化范围内原子提交最终校验、占用关联及持久意图，绑定不可变载荷引用、稳定业务身份、围栏版本、回执及预留。意图写入失败即阻断外发；本地事务不包含远端业务系统。

### 执10 — Dispatch with current fences / 受限派发与当前围栏

Conditionally claim the intent, then enforce current fence, stop, policy and credential versions. Policy activation, revocation and stop update relevant fences; mismatched queued intent returns to checking. Policy/dispatch services define activation and acknowledgment ordering; inability to establish the current version blocks high-risk writes. Never reread a mutable artifact to replace the approved payload after validation. Retain recoverable submission intent before network I/O and attach the external request ID afterward. / 条件认领意图后核验当前围栏、停止、策略和凭证版本。策略生效、撤销、停止更新相应围栏，队列意图版本不一致则退回复核。策略和派发服务明确生效及确认顺序，无法确定当前版本即阻断高风险写入。检查后不得重读可变工件替换批准载荷。网络调用前保留可恢复提交意图，随后关联外部请求标识。

Revocation effective before local dispatch permission blocks the new request; work already permitted and submitted is in flight. Cross-process check-then-send cannot remove every race or instantly recall an accepted external request. Use stable server-side idempotency within its documented scope/retention. Without reliable idempotency or outcome queries, do not automatically retry non-idempotent writes; require authorized reconciliation. / 本地派发许可生效前的撤销阻断新请求，已获许可并提交的动作属于在途。跨进程先查后发不能消除全部竞态或瞬间撤回外部已接收请求。按记录的作用域及保留期使用稳定服务端幂等。无可靠幂等或结果查询能力时，非幂等写入不自动重试，交由授权对账处理。

### 执11 — Verify the business outcome / 观察并核实业务结果

Distinguish transport failure, request acceptance, processing and terminal outcomes from actual business-object changes. Adapter semantics determine what a success response proves; accepted is not paid. Read authoritative transaction/order state, deployed version, database result or equivalent evidence. Verify batches item by item, retaining success, failure and unknown; a batch return code cannot justify replaying successful items. / 将传输失败、请求接收、处理中、终态与业务对象实际变化分开。成功响应能证明什么由适配器语义决定，已接收不等于已付款。读回权威交易订单、部署版本、数据库结果或等价证据。批次逐项核验并保留成功、失败及未知，不能因总返回码重做成功项。

### 执12 — Reconcile uncertainty and govern compensation / 未知结果对账与受控补偿

Timeout, disconnection, crash, uninterpretable response or conflicting local/external records creates `unknown_outcome` and retains exposure. Query the original operation identity first; if unavailable, hand off to an authorized owner. Confirmed success settles with outcome evidence. Release or retry only when non-execution and inability of the original request to execute later are established under adapter consistency/terminal rules. A temporary not-found response is not that proof. / 超时、断线、崩溃、无法解释的返回或内外记录冲突均形成结果未知并保留占用。先查原业务身份，无法查询则交有权责任人。确认成功后补证并结算；只有按适配器一致性及终态规则确认未执行且原请求以后不会继续执行，才可释放或重试。暂时查无记录不构成该证明。

Lease expiry revokes executor ownership only; idempotency-retention expiry never authorizes a new key for unresolved work. Rollback requires actual capability and authorization. Refund, cancel or data restoration uses a new governed proposal and evidence trail; compensation does not erase history. / 租约到期仅撤销执行者资格，幂等保留期到期不能授权未知动作换键重发。回滚要求真实能力与授权；退款、撤单、数据恢复采用新受治理提案并留痕，补偿不抹除历史。

### 执13 — Settle exposure and assemble audit / 结算占用与形成审计

For verified successful items, move pending or unknown exposure into confirmed consumption; release only failures proven side-effect-free and terminal; retain unresolved portions. Settle idempotently by business operation ID, with no duplicate debit or release. Define lifetime consumption separately from reusable in-flight capacity; a refund does not automatically reset annual compensation counts or historical risk. Link request, proposal, rules, approval, reservations, submission, external results, verification, anomalies and owner. / 已核实成功项把预留或未知占用迁为确认消耗；仅对确认无副作用且不会继续执行的失败释放，未决部分保留。按业务操作标识幂等结算，不重复扣减或释放。累计消耗与可复用在途额度分别定义，退款不自动重置全年补偿次数或历史风险。关联请求、提案、规则、审批、占用、提交、外部结果、核验、异常及责任人。

### 执14 — Evaluate promotion, restriction and revocation / 评估晋升、缩权与撤销

Use independently verified outcomes, incidents, scenario coverage, observation windows and evidence completeness. No incident is not proof of no risk; low-risk success cannot buy high-risk authority. Promotion normally requires independent approval and a newly issued credential with explicit scope, limits and term. Preauthorized control services, not probes, execute automatic restriction or stop. Revocation covers queued work, children and delegation credentials; already dispatched effects remain tracked. / 使用独立核验结果、事故、场景覆盖、观察窗口和证据完整性。无事故不证明无风险，低风险成功不能换取高风险权限。晋升通常须独立审批并签发范围、限额、期限明确的新凭证。自动缩权及停止由预先授权控制服务执行，不由探针执行。撤销覆盖队列、子任务及委托凭证，已派发影响继续追踪。

### 执15 — Adopt observation enrichment and revalidate / 采纳观测补全并复核

Validate patches using the [shared contract](governance-contract.md) and append only to `observation_enrichment`. Missing evidence can point to a legitimate record that existed at the relevant time. An event that never occurred needs a new business step; it cannot be patched into existence. Evidence used to resume work returns to 执04, 执07 or 执09. Adoption alone never jumps to a tool call; conflicts, stale approval or mismatched versions keep the gate blocked. / 按共享契约校验补丁，只追加至观测补全层。缺失证据可指向当时确已存在的合法记录；尚未发生的事实须新业务步骤，不能以补丁凭空生成。用于恢复工作的证据回执04、执07或执09复核，采纳不直接跳工具调用；来源冲突、过期审批或版本不符继续阻断。

### 执16 — Close, continue or hand off / 关闭、继续或交接

Report fully complete, partially complete, denied, stopped or still unknown accurately. Include the last valid checkpoint, item inventory, unresolved exposure, next accountable subject and allowed actions. Bind handoff to exact artifacts, proposals, policies and evidence versions and obtain receiver acknowledgment. Transfer of responsibility does not automatically transfer the former executor's permissions; validate the receiver's own delegation and credentials. / 如实区分全部完成、部分完成、拒绝、停止或仍未知，输出最后有效检查点、分项清单、未决占用、后续责任人及允许动作。交接绑定精确工件、提案、策略和证据版本并取得接收确认。责任转移不自动转移前执行者权限，须核验接收者自身委托和凭证。

## Observation Boundary / 观测边界

Use [governance-contract.md](governance-contract.md) as the single maintained full contract for `GOV_BOUNDARY_OBS` `1.0.0`, and [governance-observability-probes.md](governance-observability-probes.md) for optional independent probes. The supplied documents embed the same full shared appendix; this maintained set centralizes it to avoid divergent copies. Do not silently rename fields, drop unknown incompatible fields, or imply wire compatibility with other reasoning/reflection/collaboration protocols. / 以共享契约文档为 `GOV_BOUNDARY_OBS` `1.0.0` 完整契约的单一维护来源，以观测探针文档为可选独立探针入口。来源两文均内置完整共享附录，维护版集中保存以避免副本漂移。不得静默改字段、丢弃不兼容字段或暗示与其他推理、反思、协作协议线格式兼容。

| Message / 消息 | Authority and meaning / 权限及含义 |
| --- | --- |
| Runtime event / 运行事件 | Execution publishes facts; original records cannot be overwritten. / 执行发布事实，原记录不可覆盖。 |
| Enrichment request / 补全请求 | Either side requests named fields for an exact action version and deadline; it authorizes no business action. / 任一侧请求具体动作版本及期限的字段，不授权业务动作。 |
| Observation patch / 观测补丁 | Probe supplies sourced facts, deterministic derivations or explicitly unverified leads. / 探针提交来源事实、确定性派生或明确待核验线索。 |
| Control recommendation / 控制建议 | Probe suggests pause/review/restriction/reconciliation to authorized governance; it is not a credential. / 探针向有权治理方建议暂停、复核、缩权、对账，本身不是凭证。 |
| Adoption receipt / 采纳回执 | Receiver records per-field adoption, rejection, conflict, expiry or human handling and reason. / 接收方逐字段记录采纳、拒绝、冲突、过期或待人工及原因。 |

Authenticate sender, tenant and calling permissions separately from content digests. Require compatible major versions, exact run/action/proposal/policy/artifact/base-revision binding, source version and freshness, expiration and request budget. Distinguish not-yet-created, access-denied and collection-failed values; record occurrence and ingestion separately. Event timestamps from independent sources are not a total causal order. See the shared contract for the complete envelope, event fields, requests, patches and receipts. / 内容摘要之外单独认证发送者、租户和调用权限。要求主版本兼容、精确运行动作提案策略工件及基线修订绑定、来源版本及时效、有效期与请求预算。区分尚未产生、无权读取、采集失败；分开发生和采集时间，独立来源时间不是严格全局因果序。完整信封、事件字段、请求、补丁和回执见共享契约。

Apply this adoption order / 按以下顺序采纳：

1. Validate origin, authority, protocol and tenant. / 校验来源、权限、协议和租户。
2. Deduplicate patch ID plus content digest: identical retry returns the original receipt; reused ID with changed content is rejected. / 按补丁标识及内容摘要去重，相同重传返回原回执，同标识异内容拒绝。
3. Validate exact target and base revision; stale state returns conflict, requiring a newly generated patch against the new state. / 核验精确目标及基线修订，陈旧状态返回冲突，必须基于新状态重新生成补丁。
4. Check expiry, `observation_enrichment` allowlist, source version, retrieval time, applicability, quality and derivation rule/formula versions. / 核验有效期、观测命名空间白名单、来源版本、采集时间、适用范围、质量及派生规则公式版本。
5. Append enrichment while preserving original gaps, facts and audit times; issue per-field adoption results with the new observation revision. / 追加补全并保留原缺口、事实及审计时间，生成逐项结果和新观测版本。
6. Reenter current adjudication and final gate if evidence affects an execution condition; only receiver-verified evidence satisfying the original criterion closes a gap. / 补证影响执行条件时重入当前裁决及最终入口，仅接收方核验且满足原验收标准的证据可关闭缺口。

A probe's verified-source quality means it checked origin/content, not that the record authorizes the current action. Patches may not alter goal, amount, target, proposal, policy, approval, execution state, balance, credential, original event or audit time. Model confidence cannot produce authoritative approval, success or balances. Historical enrichment binds a named historical snapshot, never overwrites the current view or restores authority, and never backdates a later approval; preserve when older evidence was discovered. / 探针标记来源已核验只表示来源内容经其核查，不表示能授权当前动作。补丁不得改变目标、金额、对象、提案、策略、审批、执行状态、余额、凭证、原事件或审计时间。模型信心不能生成权威审批、成功或余额。历史补全绑定明确历史快照，不覆盖当前视图或恢复权限，不倒填事后批准，保留旧证据的发现时间。

Each request has retry/query caps, a deduplication key and deadline. Mark receipt causation to prevent probes from endlessly treating their outputs as new gaps. Exhausted requests remain unresolved with a named owner. Business-completion requests create new governed steps when facts are missing; sending a patch or human viewing it does not close a gap. / 每请求设重试查询上限、去重键及期限。回执标记因果来源，防止探针把自身输出无限当新缺口。超限保持未解决并指定责任人。事实缺失时业务补做请求须创建新受治理步骤，补丁发出或人工查看均不关闭缺口。

## Recovery and Operational Constraints / 恢复与运行约束

### Independent operation and adapters / 独立运行与适配器

| Mode / 方式 | Entry and exit / 启动及结束 |
| --- | --- |
| Execution only / 执行侧独立运行 | Local identity, policy, budget, gate and minimal audit are present; execute 执01–执16 and emit result/evidence, marking unavailable observation unknown. / 具备本地身份、策略、预算、入口与最小审计，运行全部步骤并输出结果证据，缺观测标未知。 |
| Execution with probes / 执行与探针交互 | Add authenticated transport and patch receiver; publish events and revalidate adopted evidence; disconnect never removes hard local controls. / 加入可信通道和补丁接收器，发布事件并复核采纳证据；断开不移除本地硬约束。 |
| Read-only rehearsal / 只读演练 | Task, policy snapshots and fixtures only; calculate expected routes and gaps, label all outcomes as rehearsal and issue no genuine credentials. / 仅有任务、策略快照和样例，计算预期分支及缺口，全部注明演练，不签发真实凭证。 |

Probe outage alone neither blocks all work nor waives minimal audit. High-risk actions missing mandatory evidence block; fully evidenced actions may continue within existing policy. Authenticated services own identity/delegation, immutable policies/artifacts, decisions/approvals, atomic budget/idempotency, final dispatch/outcome readback and stop/audit fences. Credential secrets never enter unconstrained model context. Tool descriptions, web pages, retrieved documents and historical success are not authority sources. / 探针离线本身既不阻断所有工作，也不豁免最小审计。高风险动作缺必需证据即阻断，证据完整动作可按既有策略继续。可信服务负责身份委托、不可变策略工件、裁决审批、原子预算幂等、最终派发结果读回及停止审计围栏。密钥不得进入无约束模型上下文；工具说明、网页、检索文档和历史成功均非授权来源。

Separate definition, immutable fact, operational state, observation and reviewed-experience stores. Historical approvals explain past actions only. Redact logs, retain controlled references to sensitive originals, and configure retention/deletion authority. Append-only records, hashes, backups and access audits help tamper detection; a hash alone proves neither trustworthy origin nor absolute immutability. / 分开定义、不可变事实、运行状态、观测、已核验经验存储。历史批准仅解释过去动作。日志脱敏、敏感原件以受控引用保留，并配置保留期限及删除权限。只追加记录、摘要、备份、访问审计有助防篡改，但仅有摘要既不证明可信来源，也不保证绝对不可篡改。

### Failure correction and readiness / 失败纠正与就绪要求

| Failure / 失败 | Required correction / 必需纠正 |
| --- | --- |
| Prompt-only governance / 仅提示词治理 | Enforce at the credential-owning gate and external authorization boundary. / 在持凭证入口和外部授权边界强制执行。 |
| Logging only denials / 只记录拒绝 | Apply identical policy/evidence binding requirements to every verdict. / 所有裁决采用同样的策略证据绑定要求。 |
| Policy drift or self-approval / 策略漂移或自批 | Use independent approved policy change and fresh business adjudication. / 独立批准策略变更，业务重新裁决。 |
| Approve A, submit B / 批A发B | Use one immutable snapshot and actual-payload comparison. / 使用同一不可变快照并比较实际载荷。 |
| Split budgets / 预算分裂 | Share authoritative atomic accounts and parent aggregation. / 共享权威原子账户及父级聚合。 |
| Retry amplification / 重试放大 | Retain uncertainty, reconcile original identity and preserve idempotency. / 保留未知，按原身份对账并保留幂等。 |
| Retrospective approval / 事后补批准 | Preserve timing and the original violation; never claim prior authority. / 保留时序及原违规事实，不称事前已授权。 |
| Observation overreach / 观测越权 | Isolate enrichment, reject forbidden writes and reenter the execution gate. / 隔离补全，拒绝禁写字段并重入执行闸。 |
| Approval fatigue / 审批疲劳 | Use explicit preapproved low-risk scope without deleting necessary gates. / 使用明确预批准低风险范围，保留必需闸门。 |
| One-click rollback fiction / 一键回滚幻觉 | Confirm external state and separately govern any compensating effect. / 确认外部状态并单独治理补偿副作用。 |

Before production, demonstrate real identity and separation of duties, traceable policy history, rejection of stale receipts/payload mismatch, concurrent-budget safety, timeout reconciliation/handoff, pre-send durable intent, queue/child revocation, in-flight inventory, protected evidence access and recovery without duplicate effects. Each adapter supplies idempotency, query consistency, terminal semantics and permission-test evidence. Documentation checks, sample data, local databases and single-process tests do not establish these live capabilities. / 生产前须证明真实身份与职责分离、策略历史、旧回执及载荷错配拒绝、预算并发安全、超时对账交接、发送前意图持久化、队列子任务撤销、在途清单、受控证据访问及无重复副作用恢复。每适配器提供幂等、查询一致性、终态语义、权限测试证据。文档检查、样例、本地数据库或单进程测试不证明这些生产能力。

<a id="acceptance"></a>

## Acceptance Design / 验收设计

**All 26 cases below are source-preserved acceptance designs and have not been executed as business or adapter integration tests.** Progress from static contract review to fixed-fixture replay, concurrency/fault injection, isolated adapter integration and preproduction drills; record actual evidence for each stage. / **以下全部 26 项保留来源验收设计，尚未作为业务或适配器集成测试执行。** 按静态契约检查、固定样例回放、并发故障注入、隔离适配器集成、生产前演练逐步验证，各阶段记录实际证据。

| Source ID / 来源编号 | Input or fault / 输入或故障 | Required result / 必需结果 |
| --- | --- | --- |
| 执验01 | Allow receipt lacks policy version. / 允许回执缺策略版本。 | Block and record policy-evidence gap. / 阻断并记录策略证据缺口。 |
| 执验02 | Deny receipt lacks reason or policy. / 拒绝回执缺原因或策略。 | Mark incomplete; do not claim accountable traceability. / 标记不完整，不宣称可追责。 |
| 执验03 | Amount changes after approval. / 批准后金额变化。 | Old receipt invalid; new proposal and decision. / 旧回执失效，新提案重裁决。 |
| 执验04 | Target/artifact changes after approval. / 批准后对象或工件变化。 | Digest mismatch blocks dispatch. / 摘要错配阻断派发。 |
| 执验05 | Same policy ID/version, different content. / 同策略标识版本对应不同内容。 | Quarantine conflict; never choose arbitrarily. / 隔离冲突，不任选。 |
| 执验06 | Same real subject proposes and approves relaxation. / 同一真实主体提出并批准放宽。 | Reject policy publication. / 拒绝策略发布。 |
| 执验07 | Different approver lacks required authority. / 不同审批者无相应权限。 | Reject approval. / 拒绝批准。 |
| 执验08 | Temporary rule expires. / 临时规则过期。 | New actions cannot use it. / 新动作不得沿用。 |
| 执验09 | Two branches each request 80 from 100 remaining. / 两分支各申请80，余额100。 | At most one reservation succeeds; no 160 new exposure. / 最多一笔预留成功，不新增160占用。 |
| 执验10 | New task ID requests the same compensation. / 换任务标识再申请同笔补偿。 | Subject cumulative limits and business idempotency still apply. / 仍受主体累计额度及业务幂等约束。 |
| 执验11 | Child requests outside parent authority. / 子执行者申请父授权外动作。 | Reject; no unlimited inheritance. / 拒绝，不无限继承。 |
| 执验12 | Timeout after external success. / 超时但外部已成功。 | Reconcile success; never resubmit. / 对账确认成功，不重复提交。 |
| 执验13 | Not found while delayed external write remains possible. / 查无记录但可能延迟写入。 | Stay unknown; no release or new key. / 保持未知，不释放或换键。 |
| 执验14 | Idempotency retention expires while outcome unknown. / 幂等保留期到期且结果未知。 | Human reconciliation; no blind retry. / 人工对账，禁止盲重试。 |
| 执验15 | Batch partially succeeds. / 批次部分成功。 | Item settlement; no whole-batch replay. / 分项结算，不整批重做。 |
| 执验16 | Crash around dispatch. / 派发前后崩溃。 | Recover intent and query original operation, not memory. / 恢复意图查原操作，不凭内存判定。 |
| 执验17 | Intent cannot be persisted. / 关键意图无法落盘。 | Block dispatch. / 阻断派发。 |
| 执验18 | Probe offline; all local mandatory controls present. / 探针离线且本地必需控制完备。 | Existing authority may continue; record observation gap. / 可按原授权继续，单记观测缺口。 |
| 执验19 | Patch writes approval or budget. / 补丁写审批结果或预算。 | Reject and alert. / 拒绝并告警。 |
| 执验20 | Expired patch or changed base state. / 补丁过期或基线已变。 | Expired/conflict receipt; no restored authority. / 返回过期或冲突，不恢复资格。 |
| 执验21 | Identical patch retransmission. / 同补丁重复发送。 | Return original result; no duplicate view mutation. / 返回原结果，不重复改视图。 |
| 执验22 | Revocation precedes local dispatch permission. / 撤销早于本地派发许可。 | New send blocked, including queued intents. / 阻断新发及队列意图。 |
| 执验23 | Stop with external work already in flight. / 停止时已有外部在途动作。 | Produce pending-verification inventory, not a recalled-success claim. / 输出待核验清单，不称撤回成功。 |
| 执验24 | Low-risk successes offered for high-risk promotion. / 以低风险成功申请高风险晋升。 | No promotion without scenario evidence and independent approval. / 无场景证据和独立批准不晋升。 |
| 执验25 | Only sample data, no real tool. / 仅样例无真实工具。 | Rehearsal expectations only; no genuine success receipt. / 仅演练预期，不生成真实成功回执。 |
| 执验26 | Approval created after business completion. / 业务完成后才产生批准。 | Preserve violation; never backfill prior approval. / 保留违规，不倒填事前批准。 |

Retain raw inputs sufficient to assess policy-bound allows, final-gate evidence, cumulative exposure, duplicate effects, unknown results, audit completeness and revocation effectiveness even without probes. See the companion probe definitions for measurement denominators, quality and evidence; monitoring absence never excuses missing approvals. / 即使无探针也保留足以评估放行策略绑定、最终检查证据、累计暴露、重复副作用、未知结果、审计完整性、撤销生效的原数据。指标分母、质量及证据见配套探针；监控未接入不豁免审批记录。

## Examples / 示例

### Payroll source illustration / 薪酬来源示例

The supplied execution document attributes to a lecture a test ledger with **798 paid and 2 reversed payslips**, a checklist total of **CNY 13,706,097**, and automatic-check thresholds **CNY 13,000,000** then **CNY 30,000,000**. Under the reported fixture, raising the threshold changed human review to pass; the reported old allow receipt lacked policy provenance. These are supplied-document assertions, not independently verified lecture facts or results of this change. We did not obtain or execute its cited `governance/payroll-lab/ungoverned_policy_lab.py` or `governance/boundary_contract.py`. / 来源执行文档援引讲义描述测试账本含 **798 张已付款、2 张已冲正工资单**，检查总额 **13,706,097 元**，自动检查阈值先后为 **13,000,000 元、30,000,000 元**。其报告在该样例下调高阈值使转人工变为通过，旧式放行回执缺策略来历。这些是附件中的主张，并非本次独立核验的讲义事实或修改运行结果；本次未取得或执行其引用的两个程序。

| Illustration / 场景 | Required interpretation / 要求解释 |
| --- | --- |
| Lower threshold / 低阈值 | Human review with recorded rule. / 转人工并记录规则。 |
| Lawfully published higher threshold / 合法发布高阈值 | Checklist receipt binds the exact policy; this is not payment or a new payable obligation. / 清单检查回执绑定精确策略，不代表付款或新增应付义务。 |
| Same-subject threshold self-approval / 同主体自批提阈值 | Reject policy publication and preserve original business decision. / 拒绝发布并保留原业务裁决。 |
| Changed payee after approval / 批准后收款对象变化 | Final gate rejects the stale binding and requires fresh review. / 最终入口拒绝旧绑定并重新审查。 |

Thresholds control review routing, not cash availability or hard budget. Paid entries must never be paid again merely because the checklist passes. In minor units the total is `1,370,609,700` fen and thresholds are `1,300,000,000` and `3,000,000,000` fen; this changes representation only. / 阈值控制审批路由，不代表现金或硬预算。清单通过不能使已付款项目再次付款。以分表示，总额为 `1,370,609,700`，阈值为 `1,300,000,000` 及 `3,000,000,000`，仅改变单位表示。

### Coupon idempotency / 优惠券幂等

A task permits one CNY 100 coupon for a specific ticket. Bind ticket, recipient, coupon rule and amount; derive the business identity from the ticket and compensation matter. After timeout, query that request: success closes with evidence, unknown retains exposure. Ten retries, a new executor or a new run cannot create ten coupons. Additional compensation requires new business grounds while retaining user, ticket and time-window cumulative bounds. / 指定工单任务仅允许发一次100元券，绑定工单、接收用户、券规则及金额，以工单与补偿事项形成业务身份。超时查原请求，成功补证关闭，未知保留占用。十次重试、换执行者或新运行不能发十张券；追加补偿须新依据，并继续遵守用户、工单及时间窗累计上限。

### Nonfinancial substitutions / 非资金替换项

| Scenario / 场景 | Proposal and bounds / 提案与边界 | Outcome evidence / 结果证据 |
| --- | --- | --- |
| Deployment / 发布 | Build digest, environment, service/config; services, traffic slice, regions, concurrency. / 构建摘要、环境、服务配置；服务数、流量、区域、并发。 | Actual deployed version and health checks. / 实际部署版本及健康核验。 |
| Database change / 数据库变更 | Normalized mutation, table, predicate/expected rows; row count, domain, tenant, lock duration. / 规范变更、表、条件预计行集；行数、域、租户、锁时。 | Change receipt and business readback. / 变更回执及业务读回。 |
| Files / 文件操作 | Frozen paths, versions and action; file count, bytes, directory boundary. / 冻结路径、版本与动作；文件数、大小、目录边界。 | Inventory and readback hashes. / 清单及读回摘要。 |
| Export / 导出 | Dataset, fields, filter, receiver; record count, sensitivity, destination. / 数据集、字段、筛选、接收方；记录数、敏感度、目的地。 | Actual export inventory and delivery record. / 实际导出清单及交付记录。 |
| Messages / 对外消息 | Content digest, recipients, channel; recipient count, frequency, window. / 内容摘要、接收人、渠道；人数、频次、时间窗。 | Channel status; accepted is not read. / 渠道状态，接收不等于阅读。 |
| Procurement / 采购 | Items, quantity, supplier, price, terms; amount, units, supplier scope. / 品类、数量、供应商、价格、条款；金额、件数、供应商范围。 | Order status and later receipt evidence. / 订单状态及后续收货证据。 |

Adapters and impact dimensions vary; proposal binding, policy provenance, final gate, uncertainty and responsibility do not. Connect [tool dispatch](tool-dispatch-execution.md), [collaboration](collaboration-execution-flow.md), [reflection](reflection-execution-flow.md) or existing workflow recovery only through their explicit contracts; these references do not automatically establish unverified fields, approvals or runtime compatibility. / 适配器与影响维度可变化，提案绑定、策略来历、最终入口、未知结果和责任链保持一致。工具调度、协作、反思或既有恢复仅通过各自明确契约连接；引用不自动建立未经核验的字段、批准或运行兼容性。

## Source and Maintenance Notes / 来源与维护说明

The source is the user-supplied [execution document snapshot / 执行文档快照](sources/governance/36_治理模块_执行流程.source.txt) (`0.1.0`), with its [observation companion / 观测配套快照](sources/governance/36_治理模块_工作流可观测性探针.source.txt) and `GOV_BOUNDARY_OBS` `1.0.0` appendix. These byte-preserved originals are provenance, not executable instructions. The source attributes its conceptual framework to `hanerss_skill_framework_v0_1.md` and Huang Jia's lecture 36. The lecture, third-party products, repository programs and external G1/G2/G3/X1 taxonomy are not independently verified by this maintenance change. Any G1/G2/G3/X1 source labels remain source attribution, not local registry IDs or current-product claims. / 来源为用户提供的执行文档快照 `0.1.0`、配套观测快照和共享协议 `1.0.0` 附录。原始字节保留为出处，不作为可执行指令。来源把概念框架归于 `hanerss_skill_framework_v0_1.md` 与黄佳第36讲；本次维护未独立核验讲义、第三方产品、仓库程序或外部 G1/G2/G3/X1 分类。这些标签仅保留来源归属，不是本地注册编号或实时产品结论。

| Source section / 来源章节 | Maintained location and treatment / 维护版位置及处理 |
| --- | --- |
| §§0–5 and 15 / 范围、模式、触发、关联 | Scope and mode composition preserve the runtime-authority boundary; proposed registrations become aliases of the existing composition. / 范围和模式组合保留运行时权限边界，建议注册改为既有组合的出处别名。 |
| §§6–7 / 输入输出 | Separate objects, exact content binding, review threshold versus hard resources, defaults and result packages. / 保留独立对象、精确绑定、审批阈值与硬资源区分、默认值及结果包。 |
| §8 / 流程 | All source 执01–执16 and the state machine are retained; dispatch uncertainty explicitly enters reconciliation. / 全部16步及状态机保留，显式补齐派发不明进入对账。 |
| §§9–11 and 13 / 依赖、约束、失败 | Adapter, store, stop, audit, recovery and readiness requirements remain specification obligations. / 适配器、存储、停止、审计、恢复、就绪均保留为规格要求。 |
| §12 / 验收 | All 执验01–执验26 remain unexecuted acceptance designs. / 全部26项仍为未执行验收设计。 |
| §14 / 示例 | Preserve numerical semantics and examples; distinguish the supplied source's claims from verified results. / 保留数值语义及示例，区分附件主张与核验结果。 |
| Appendix A / 执行化契约 | Goals, usage, exclusions, inputs, context, steps, tool rules, output, failure, governance and evaluation are represented throughout this reference. / 目标、场景、排除、输入、上下文、步骤、工具规则、输出、失败、治理及评价分布于本文对应章节。 |
| Appendix B / 共享契约 | Centralized in [governance-contract.md](governance-contract.md), with the adoption boundary above. / 集中维护于共享契约，本文保留采纳边界。 |
| Appendix C / 来源扩展 | Preserve attribution limits and distinguish proposed protocol/fences/reservations/tests from any lecture implementation. / 保留归属边界，区分所提协议、围栏、预留、测试与讲义实现。 |

Key engineering extensions in the source—node IDs, shared messages, observation patches, dispatch fences, atomic reservation, cross-window exposure and acceptance cases—remain design proposals requiring adapter implementation and evidence. This maintenance adds bilingual wording, local identity mapping and one shared reference; it does not claim these safeguards are already enforced by the repository runtime. / 来源中的节点编号、共享消息、观测补丁、派发围栏、原子预留、跨窗口暴露及验收案例均仍是待适配实现并举证的工程设计。维护版增加双语表述、本地身份映射和单一共享引用，不声称仓库运行时已强制实施这些控制。

For the detailed `PATTERN_0050` specialization, follow [Blast Radius Control execution](blast-radius-execution-flow.md) and its [shared contract](blast-radius-contract.md). Parent reservations include descendant use once, unused issued permits occupy quota, and financial closure cannot return unknown balances. / 现有爆炸半径模式的细化执行见专用流程与共享契约；父预留只计一次后代用量，未用已签发许可占额度，账务关闭不能返还未知余额。
