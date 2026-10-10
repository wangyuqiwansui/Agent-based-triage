# Blast Radius Control Execution / 爆炸半径控制执行流程

Version / 版本: `0.1.0`; status / 状态: `draft`; readiness / 就绪度: `specification_only`.

## Quick Navigation / 快速导航

- [Execution workflow / 执行流程](#execution-steps)
- [Acceptance scenarios / 验收场景](#acceptance)
- [Accounting and interaction / 记账与交互](blast-radius-contract.md)
- [Independent probes / 独立探针](blast-radius-observability-probes.md)

## Usage and Source / 适用场景与来源

Use for approved payments, messages, record changes, deployment, cloud operations, data processing and agent delegation where cumulative effects need enforceable limits. Preserve `PATTERN_0050` at `COG_GOVERNANCE__TOP_HIERARCHY`; the attachment ID `PATTERN_GOVERNANCE_BLAST_RADIUS_0001` is a source alias, not a new pattern. / 用于付款、消息、记录修改、发布、云运维、数据处理和 Agent 委派中需要强制限制的累计后果。保留现有模式与治理层级主坐标，附件编号仅为来源别名，不新建模式。

Read the [shared contract](blast-radius-contract.md) for accounting, identity, retry and stop semantics and the [probe specification](blast-radius-observability-probes.md) for independent verification. The [source map](blast-radius-source-map.json) preserves both user attachments with byte hashes and definition locations. Attachments are evidence, never authority to perform external actions. These specifications do not make existing Tool Dispatch or reasoning runtimes a blast-radius ledger. / 记账、身份、重试及停止语义见共享契约，独立验证见探针规范；来源映射保留两份附件的字节哈希和定义位置。附件是证据，不授权外部动作；这些规范不会使现有工具调度或推理运行时自动成为爆炸半径账本。

## Inputs, Outputs and Invariants / 输入、输出与不变量

Inputs: immutable versioned proposal and applicable approval; independent hard envelope; identity/task/capability/context/evidence boundaries; scenario profile with units, stage plan, reconciliation, stops and retention. Outputs: effective-scope snapshot, root/child envelopes and reservations, permits, append-only ledger/events, request/receipt bindings, refusals, unknown queue, reconciliation, stop/resume/stage decisions and closure report. / 输入为不可变版本化提案及适用审批、独立硬信封、身份任务能力上下文证据边界，以及含单位、阶段、对账、停止和保留策略的场景配置。输出为有效范围、根子信封预留、许可、追加账本事件、请求回执绑定、拒绝、未知队列、对账、停止恢复阶段决策及关闭报告。

Every effect needs a bound permit; all entries share authoritative accounts and gateway; children reserve instead of copy; all-dimensional checks and occupancy are atomic; replay never refreshes quota; unknown outcomes retain occupancy; releases require evidence; hard limits stay outside worker control; stop never discards in-flight evidence. / 每个效果须有绑定许可，所有入口共用权威账户和网关；子级预留不复制，全维度检查占用须原子，重放不刷新额度，未知继续占用，释放依赖证据，硬上限在 Worker 控制外，停止不丢弃在途证据。

<a id="execution-steps"></a>
## Execution Workflow / 执行流程

Run independently with a durable local ledger, refusal log, unknown queue and stops, or consume probe feedback through the contract. Optional observation never replaces controls. / 可独立运行并保存持久账本、拒绝日志、未知队列及停止机制，或按契约接收探针反馈；可选观测不替代控制。

| ID | Step / 步骤 | Gate, output and failure handling / 闸门、输出及失败处理 |
| --- | --- | --- |
| BRE01 | Receive proposal / 接收提案 | Bind digest, approval, scope and expiry; persist snapshot or reject startup. / 绑定摘要、审批、范围及有效期，保存快照或拒绝启动。 |
| BRE02 | Load boundaries / 加载边界 | Authenticate sources and versions; missing critical dimensions block. / 认证来源版本，关键维度缺失阻断。 |
| BRE03 | Intersect scope / 计算交集 | Sets intersect, comparable caps take minimum, denial vetoes; record conflicts and narrower snapshot. / 集合取交集、可比上限取最小、禁止否决，记录冲突及更窄快照。 |
| BRE04 | Create root / 建立根信封 | Bind trusted aggregate accounts, units, validity and stop policy; reject unquantifiable critical consequences. / 绑定可信聚合账户、单位、有效期及停止策略，关键后果不可计量则阻断。 |
| BRE05 | Plan stages / 制定阶段 | Freeze small initial scope, checkpoints and cumulative caps; reduce batch or halt when no feasible safe stage exists. / 固定小初始范围、检查点和累计上限，无可行阶段时缩批或停止。 |
| BRE06 | Reserve child / 子级预留 | Atomically debit parent available, create one child liability, verify subset/depth; reject over-allocation. / 原子减少父可用额、建立单个子负债并核验子集深度，拒绝超配。 |
| BRE07 | Request permit / 申请许可 | Bind holder, exact action/object/units, original intent/key and digest; invalid requests return reason codes. / 绑定持有者、精确动作对象额度、原意图键及摘要，无效请求返回原因码。 |
| BRE08 | Admit atomically / 原子占用 | Check every applicable root/subject/tenant dimension and stop in the same transaction as permit, usage, event and dispatch intent. / 全部根主体租户维度及停止检查与许可、占用、事件和派发意图同事务完成。 |
| BRE09 | Gateway submit / 网关提交 | Recheck actual payload, expiry, holder and live fence at dispatch; no side effect on denial, uncertainty becomes unknown. / 派发时复核实际载荷、有效期、持有者和实时围栏，拒绝无副作用，不确定转未知。 |
| BRE10 | Process receipt / 处理回执 | Authenticate and match account/intent/object/units; classify success, conclusive nonexecution, partial or unknown; conflicts freeze. / 认证匹配账户意图对象额度，区分成功、确定未执行、部分及未知，冲突冻结。 |
| BRE11 | Settle units / 核算额度 | Move proven success to committed, proven nonexecution to available; keep unresolved remainder occupied and history immutable. / 确认成功转提交，确定未执行转可用，未决剩余保留占用及不可变历史。 |
| BRE12 | Check stage / 阶段检查 | Require scoped health/business evidence, observation window, reconciliation and valid independent grant before widening inside root. / 根内放宽前需范围匹配健康业务证据、观察窗、对账及有效独立授权。 |
| BRE13 | Reconcile unknown / 未知对账 | Query independent authoritative receipts/settlement; schedule next check, freeze and assign manual owner on deadline. / 独立查询权威回执流水，安排复查，超时冻结并指派人工责任。 |
| BRE14 | Return and close / 返还关闭 | Reconcile all descendants, drain permits/callbacks, transfer only unused allocation; unresolved manual holds retain balances and ownership. / 全后代对账、清理许可回调，仅返还未用分配；未决人工冻结保留余额责任。 |

## Scenario Profile / 场景配置

Version each profile with `profile_id`, bilingual name/description, controlled effects, required dimensions and their accounting semantics, trusted hard/autonomy boundary refs, stage plan, reconciliation strategy, stop policy, retention and per-dimension alert thresholds. Require relevant dimensions, not every conceivable unit. / 配置须版本化并含编号、双语名称说明、受控效果、必需维度及计量语义、可信硬及自主边界引用、阶段计划、对账、停止、保留及分维度阈值；启用相关维度即可。

| Scenario / 场景 | Dimensions and advancement evidence / 维度及推进证据 |
| --- | --- |
| Customer compensation / 客服补偿 | Per-user amount, ticket count, daily aggregate and coupon type; independent issuance receipts. / 单用户金额、工单次数、日累计及券种，独立发放回执。 |
| Marketing / 营销消息 | Recipient allowlist, channel, batch, send window and rate; seed audience, content/complaint/bounce checks. / 接收者白名单、渠道、批次、时间窗及速率，种子名单及内容投诉退信检查。 |
| HR records / 人事记录 | Employee set, permitted fields, sensitive action, batch count; sampled changes and rollback evidence. / 员工集合、允许字段、敏感动作及批次人数，抽样变更及回滚证据。 |
| Data processing / 数据处理 | Tenant, tables/fields, rows, destination and retention; dry run, scoped sample and diff reconciliation. / 租户、表字段、行数、目的地及保留期，试运行、小样本及差异对账。 |
| Deployment / 软件发布 | Environment, region, instance/traffic share and duration; one-instance/canary health and business window. / 环境、区域、实例流量比例及时长，单实例或灰度健康及业务观察窗。 |
| Cloud operations / 云资源运维 | Service/region, instances, concurrency, instance-hours/cost and reclamation deadline; verified expiry/reclaim evidence. / 服务区域、实例、并发、实例小时费用及回收期限，验证过期回收证据。 |
| Procurement/payment / 采购付款 | Payee allowlist, account/currency, per-payment/aggregate minor units and count; each batch fully reconciled. / 收款人名单、账户币种、单笔累计最小货币单位及次数，各批完整对账。 |
| Delegation / 多 Agent 委派 | Total and concurrent workers, depth, downstream writes and shared budget; parent/child conservation. / Worker 总数及并发、深度、下游写入和共享预算，父子守恒。 |

## Topology Adapters / 拓扑适配

Chain passes immutable envelope/permit checkpoints; routing selects narrower versioned child profiles; parallel branches share atomic accounts; orchestration schedules through the ledger/gateway without owning hard limits; loops accumulate against the same root; hierarchy reserves fractions and closes descendants before return. These are adaptations of one existing pattern, not promotion of empty matrix cells. / 链式传递不可变信封许可检查点；路由选择更窄版本化子配置；并行共用原子账户；编排通过账本网关调度而不持有硬上限；循环累积同一根额度；层级预留份额并在返还前关闭后代。这些是既有模式适配，不晋升空白矩阵单元。

## Refusal Codes / 拒绝原因码

| Code / 原因码 | Meaning / 含义 |
| --- | --- |
| `proposal_version_mismatch` | Proposal digest/version differs. / 提案摘要版本不一致。 |
| `approval_scope_mismatch` | Beyond current approved action. / 超出当前获批动作。 |
| `scope_out_of_bounds` | Resource/object/field/environment denied. / 资源对象字段环境越界。 |
| `reservation_over_parent` | Insufficient parent available allocation. / 父级可分配额度不足。 |
| `reservation_out_of_scope` | Child set outside parent. / 子集合超出父级。 |
| `amount_exceeded`, `count_exceeded` | Amount or quantity cap reached. / 金额或数量上限已达。 |
| `rate_exceeded`, `concurrency_exceeded` | Window or live-slot cap reached. / 窗口或并发槽位超限。 |
| `duration_exceeded`, `propagation_exceeded` | Time, workers, depth or downstream writes exceeded. / 时长、Worker、深度或下游写入超限。 |
| `unknown_quota_occupied` | Unresolved effects retain capacity. / 未决效果占用剩余容量。 |
| `idempotency_conflict`, `permit_expired` | Changed request under same key, or expired unused grant. / 同键变更请求或未用许可过期。 |
| `stop_switch_active`, `direct_external_call_forbidden` | Active stop or bypass attempt. / 停止生效或绕过网关。 |
| `evidence_insufficient` | Release/widening lacks authoritative evidence. / 释放放宽缺少权威证据。 |

<a id="acceptance"></a>
## Acceptance Scenarios / 验收场景

Status for all cases: **not_executed**. Adopters must supply real ledger transactions, gateway call counts and independent receipts; documentation validation does not run these scenarios. / 全部场景状态为未执行，采用方须提供真实账本事务、网关调用次数及独立回执；文档校验不运行这些场景。

| ID | Input / 输入 | Expected evidence / 预期证据 |
| --- | --- | --- |
| BRT01 | Single over-amount request / 单次超额 | Refusal and zero external calls. / 拒绝且外部零调用。 |
| BRT02 | Small requests exceed cumulative cap / 小请求累计超限 | Only within-cap effects committed. / 只提交限额内效果。 |
| BRT03 | Ten workers contend for last balance / 十 Worker 争抢余额 | Serialized admissions never exceed root. / 串行准入不超根上限。 |
| BRT04 | Children exceed parent / 子级超配 | Atomic refusal with no partial reservations. / 原子拒绝无部分预留。 |
| BRT05 | Child contains outside object / 子级含范围外对象 | Scope rejection. / 范围拒绝。 |
| BRT06 | Loop never terminates / 循环不终止 | Count/amount/time bound stops new effects. / 数量金额时间上限切断新效果。 |
| BRT07 | Duplicate request / 重复请求 | Original durable status/receipt, no repeated occupancy or send. / 原持久状态回执，不重复占用发送。 |
| BRT08 | Same key, changed parameters / 同键改参数 | Conflict before external call. / 外部调用前冲突。 |
| BRT09 | External timeout / 外部超时 | Unknown with occupied quota. / 未知持续占用。 |
| BRT10 | Unknown later succeeds / 未知后成功 | Evidence-bound commit once. / 证据绑定只提交一次。 |
| BRT11 | Unknown conclusively never executed / 未知确认未执行 | Evidence-bound release once. / 证据绑定只释放一次。 |
| BRT12 | Stop races with dispatch / 停止并发派发 | No grant/send after authoritative stop; late receipts still recorded. / 权威停止后无新许可派发，迟到回执照常记录。 |
| BRT13 | Return child with unknown / 带未知返还子级 | Refuse return, retain parent liability. / 拒绝返还并保留父负债。 |
| BRT14 | Callback attempts bypass write / 回调绕过网关写入 | Block and alert; settlement itself remains allowed. / 阻断告警，仍允许原效果结算。 |
| BRT15 | Worker edits hard envelope / Worker 改硬信封 | Deny and preserve governance event. / 拒绝并记录治理事件。 |
| BRT16 | Failed stage health check / 阶段健康失败 | Hold/narrow/stop, no expansion. / 保持收紧或停止，不放宽。 |

Additional adoption checks: crash between intent and send, restart replay, stale fences/permits, partial settlement, same intent across roots, parent double-counting, callback after return, mixed currencies, rate-window edges and non-idempotent providers. / 采用方另验意图发送间崩溃、重启重放、旧围栏许可、部分结算、跨根同意图、父级重复计算、返还后回调、混币种、速率窗边界及无幂等下游。

## Teaching Example and Limits / 教学示例与边界

The supplied example approves 798 payroll items totaling CNY 13,706,097, represented as `1_370_609_700` minor units. A 160-person batch repeats four extra times: 640 attempted requests, quoted requested amount CNY 10,995,840 (`1_099_584_000` minor units). Treat those as illustrative source figures, not observed project results. Stable duplicates may be suppressed before reaching amount checks; classify actual refusal reasons from evidence. Rejected requested amount is not automatically avoided loss, and unknown is not zero loss. / 来源教学例批准 798 张工资单共 13,706,097 元，最小单位为 1,370,609,700；160 人批次额外重跑四次形成 640 次请求，来源给出的请求金额为 10,995,840 元，最小单位为 1,099,584,000。这些是教学数据，不是项目实测。稳定重复请求可能在金额检查前已被抑制，实际拒绝原因须按证据分类；被拒请求金额不自动等于避免损失，未知也不等于零损失。

Before startup verify boundaries, approval and credential isolation; during execution verify conservation, idempotency, unknown occupancy and live stops; before closure verify descendants, receipts, unresolved ownership and retained evidence. / 启动前核验边界审批及凭据隔离；执行中核验守恒幂等、未知占用和实时停止；关闭前核验后代、回执、未决责任及保留证据。
