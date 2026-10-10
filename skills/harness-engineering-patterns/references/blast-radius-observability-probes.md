# Blast Radius Control Probes / 爆炸半径控制工作流可观测性探针

Version / 版本: `0.1.0`; status / 状态: `draft`; readiness / 就绪度: `specification_only`.

## Quick Navigation / 快速导航

- [Workflow / 流程](#probe-workflow)
- [Components / 组件](#components)
- [Metrics / 指标](#metric-catalog)
- [Acceptance / 验收](#acceptance)
- [Shared contract / 共享契约](blast-radius-contract.md)

## Usage, Authority and Modes / 适用场景、权限及模式

Use with the [execution flow](blast-radius-execution-flow.md) and [shared contract](blast-radius-contract.md) to reconstruct approval → envelope → permit → dispatch → receipt → reconciliation. Read the [source map](blast-radius-source-map.json) for original definitions and explicitly documented interpretation changes. The probe ID in the attachment is a source alias under existing `PATTERN_0050`; no new matrix pattern, deployed probe or metric calculator is claimed. / 与执行流程及共享契约共同重建审批、信封、许可、派发、回执及对账链。原始定义及明确解释修订见来源映射；附件探针编号为现有模式下的来源别名，不新建矩阵模式，也不宣称已部署探针或指标计算器。

| Mode / 模式 | Behavior / 行为 |
| --- | --- |
| Offline audit / 离线审计 | Read authorized snapshots, logs and independent receipts; rebuild history and report coverage gaps, without claiming real-time prevention. / 读取获准快照日志及独立回执，重建历史并报告覆盖缺口，不宣称实时阻止。 |
| Live sidecar / 实时旁路 | Consume events and append observations without execution authority. / 消费事件追加观察，不持执行权限。 |
| Interactive / 联动增强 | Return patches, alerts, stop/reconciliation suggestions and closure gaps; track execution responses. / 返回补丁告警、停止对账建议及关闭缺口，跟踪执行响应。 |
| Registered hard gate / 注册硬门禁 | Independent control plane pre-registers versioned deterministic rules; execution service applies blocks with receipts. / 独立管理面预注册版本化确定性规则，执行服务实施阻断并留回执。 |

Probes cannot enlarge limits, approve, dispatch, release unknown balances, fabricate success, overwrite raw events or infer business correctness from healthy metrics. Optional probe outage does not disable local controls. / 探针不得扩限、批准、派发、释放未知额度、伪造成功、覆盖原事件或从指标健康推断业务正确；可选探针故障不关闭本地控制。

## Sources and Data Quality / 数据源与质量

Register authoritative proposal/approval, hard-boundary and identity configuration, workflow/scheduler/queue, ledger, gateway, external receipts/settlement, stop/resume, human disposition and probe health sources. Include normal, callback, retry, recovery, compensation, manual, scheduled, worker and bypass entries. Use independent external/network/credential evidence to discover missing gateway records; a gateway-only denominator cannot prove full permit coverage. / 登记权威提案审批、硬边界身份配置、工作流调度队列、账本、网关、外部回执流水、停止恢复、人工处置及探针健康来源。覆盖正常、回调、重试、恢复、补偿、人工、定时、Worker 及旁路入口；用独立外部网络凭据证据发现网关遗漏，仅网关分母不能证明许可全覆盖。

Keep `original`, `derived`, `inferred`, `conflict`, `missing`, `unknown` at field level. Deduplicate authenticated source/event identities; quarantine same-ID divergent payloads; keep gaps and late arrivals visible. Similar object/amount/time yields an inferred retry link only, never proof of identical business intent. Preserve source time, recording time and observation time separately and report clock uncertainty. / 逐字段保留原始、派生、推断、冲突、缺失、未知；按认证来源事件去重，同标识异载荷隔离，缺口及迟到持续可见。相似对象金额时间只能推断重试关联，不能证明业务意图相同；分开保存来源、记录和采集时间并报告时钟不确定性。

<a id="probe-workflow"></a>
## Probe Workflow / 探针流程

| ID | Step / 步骤 | Output / 输出 |
| --- | --- | --- |
| BRP01 | Register sources, owners, latency and retention / 登记来源责任时延保留期 | Coverage manifest / 覆盖清单 |
| BRP02 | Collect authorized logs/events/receipts / 采集获准日志事件回执 | Immutable raw stream / 不可变原始流 |
| BRP03 | Normalize without replacing raw facts / 标准化且不覆盖原事实 | Contract-bound events / 契约事件 |
| BRP04 | Validate required fields, versions and time / 检查字段版本时间 | Missing/conflicting fields / 缺失冲突字段 |
| BRP05 | Link stable IDs / 关联稳定标识 | Tenant-scoped evidence graph / 租户内证据图 |
| BRP06 | Rebuild parent/parallel/loop/retry/recovery paths / 重建父子并行循环重试恢复 | Workflow topology / 工作流拓扑 |
| BRP07 | Recompute effective intersection / 重算有效交集 | Narrower/wider/unknown differences / 收紧扩大未知差异 |
| BRP08 | Reconstruct disjoint balances / 重建互斥余额 | Per-dimension conservation / 分维度守恒 |
| BRP09 | Verify permit before effect / 核验效果前许可 | Unpermitted/expired/mismatched records / 无许可过期不匹配记录 |
| BRP10 | Check intent/key/digest consistency / 检查意图键摘要一致 | Duplicates and conflicts / 重复及冲突 |
| BRP11 | Track occupied unknowns and age / 跟踪未知占用及年龄 | Reconciliation queue / 对账队列 |
| BRP12 | Compare stops with new grants/dispatch / 比较停止与新许可派发 | Stop failure evidence / 停止失效证据 |
| BRP13 | Propose evidence-backed enrichment / 提出有证据补全 | Immutable patches / 不可变补丁 |
| BRP14 | Apply versioned alert thresholds / 应用版本化告警阈值 | Alerts and suggestions / 告警及建议 |
| BRP15 | Track accepted/rejected/deferred/blocked responses / 跟踪采纳拒绝延期阻断 | Durable disposition history / 持久处置历史 |
| BRP16 | Publish reports and probe health / 生成报告及探针健康 | Auditable versioned view / 可审计版本视图 |

<a id="components"></a>
## Probe Components / 探针组件

| ID | Component / 组件 | Check and evidence / 检查及证据 |
| --- | --- | --- |
| BRC01 | Source discovery / 数据源发现 | Cross-check all effectful entries, owners and independent external inventory. / 交叉核查全部效果入口、责任及独立外部清单。 |
| BRC02 | Boundary completeness / 边界完整 | Missing high-risk fields, proposal/approval mismatch, stale policies; never default unlimited. / 高风险字段缺失、提案审批不符、过期策略，不能默认无限。 |
| BRC03 | Effective scope / 有效范围 | Independently recompute intersections, minimum caps and vetoes; retain unresolved differences. / 独立重算交集最小上限及否决，保留未决差异。 |
| BRC04 | Root construction / 根信封建立 | Units, allowlist version, window, hard limits and stops cover all critical dimensions. / 单位、名单版本、窗口、硬限额及停止覆盖全部关键维度。 |
| BRC05 | Parent/child conservation / 父子守恒 | Disjoint parent equation, subset, unique reservations, descendant closure; no allocation/use double counting. / 父级互斥守恒、子集、预留唯一及后代关闭，不重复计算分配和用量。 |
| BRC06 | Concurrent occupancy / 并发占用 | Transaction revisions, conflicting accepted updates, negative balances; overlapping timestamps alone only suggest a race. / 事务修订、冲突成功更新及负余额；时间重叠只能提示竞争。 |
| BRC07 | Permit lifecycle / 许可生命周期 | Authentic bound grant precedes dispatch, live expiry/fence, one logical effect per permit. / 认证绑定许可先于派发、实时有效期围栏、每许可一个逻辑效果。 |
| BRC08 | Effects without permits / 无许可效果 | Match external ledger/network/credential activity against gateway and permits. / 外部流水网络凭据活动与网关许可比对。 |
| BRC09 | Idempotency / 幂等一致 | Stable intent/key across restart; parameter conflicts, multi-key retry and original receipts. / 跨重启稳定意图键、参数冲突、换键重试及原回执。 |
| BRC10 | Loop/retry accumulation / 循环重试累计 | Same root and aggregate accounts, attempts distinct from unique committed effects. / 同根及聚合账户，区分尝试与唯一已提交效果。 |
| BRC11 | Unknown occupancy / 未知占用 | No timeout/TTL release, independent reconciliation, age/escalation and manual owner. / 不因超时有效期释放，独立对账、年龄升级及人工责任。 |
| BRC12 | Rate/time windows / 速率时间窗 | Cross-worker fixed/sliding windows, timezone, clock skew, event dedup and boundary bursts. / 跨 Worker 固定滑动窗、时区时钟偏差、事件去重及边界突发。 |
| BRC13 | Concurrency/propagation / 并发传播 | Live and peak workers, depth, downstream writes and reserved share. / 实时及峰值 Worker、深度、下游写入和预留份额。 |
| BRC14 | Stage advancement / 阶段推进 | Initial scope, health/business window, unresolved outcomes, cumulative cap and independent grant. / 初始范围、健康业务观察窗、未决结果、累计上限及独立授权。 |
| BRC15 | Stop effectiveness / 停止有效 | Trigger/effective/ack epochs, post-stop admission/dispatch and pre-stop late receipts separately. / 分开核触发生效确认代次、停止后准入派发及停止前请求的迟到回执。 |
| BRC16 | Return/close / 返还关闭 | Issued/in-flight/unknown, accepted external requests, pending callbacks and parent liability. / 已签发在途未知、外部受理、待回调及父负债。 |
| BRC17 | Enrichment / 数据补全 | Append sourced links/derived views, never approvals, business correctness or invented success. / 追加有来源关联和派生视图，不补审批、业务正确性或虚构成功。 |
| BRC18 | Probe health / 探针自观测 | Lag, gaps, duplicates, parse/rule/notification failures, last source heartbeat and version coverage. / 时延缺口重复、解析规则通知失败、来源心跳及版本覆盖。 |

<a id="metric-catalog"></a>
## Metric Catalog / 指标目录

These 39 definitions preserve source section order; `BRM` IDs are local metric-definition keys, separate from registered global probe IDs. Report per dimension/account/root/tenant/system as applicable, with original unit, numerator, denominator/population, time window, source refs, quality, rule version and unresolved items. Deduplicate events separately from requests/effects. Never combine money, recipients, rows, concurrency, time or traffic into a substitute total score. / 以下 39 项定义保持来源章节顺序，BRM 为本地定义键，与全局已注册探针编号分开。按适用维度账户根租户系统报告原始单位、分子分母总体、窗口、来源、质量、规则版本和未决项，事件去重与请求效果去重分开；不得以总分替代金额人数行数并发时长流量。

Known empty populations yield `not_applicable`; incomplete population/evidence yields `unknown`, never perfect coverage or zero violations. Zero hard caps still deny positive requests and produce an absolute breach count; a ratio is unavailable. Use window-frozen cohorts for rates, include pending/overdue items, and report unfinished ages with completed latency distributions. Thresholds are versioned per scenario/dimension; hard violations tolerate no positive count. / 已知空总体记不适用，总体证据不完整记未知，不伪造满覆盖或零违规。零硬上限仍拒绝正请求并产生绝对越界计数，比率不可用。比率采用窗口冻结总体，保留待办超期项，完成时延旁报告未完成年龄；阈值按场景维度版本化，硬违规不容正计数。

| ID | Metric / 指标 | Calculation, evidence and interpretation / 计算、证据及解释 |
| --- | --- | --- |
| BRM01 | Root utilization / 根信封利用率 | Unique committed units / root cumulative limit; use gauge/window-specific utilization for noncumulative dimensions. / 唯一提交额除根累计上限；非累计维度另用瞬时或窗口利用率。 |
| BRM02 | Root occupied ratio / 根信封占用率 | Source effect exposure = (committed + in-flight + unknown) / root limit, descendants counted once. Also report unavailable ratio including unused issued and child-held capacity. / 来源效果暴露为提交加在途加未知除根上限，后代只计一次；另报含未用已签发及子预留的不可用容量比例。 |
| BRM03 | Child reservation ratio / 子信封预留率 | Active child liabilities / parent distributable cap; cap = parent limit minus direct issued/in-flight/unknown/committed, not remaining-after-reservation balance. / 有效子负债除父可分配上限；分母为父上限减直接已签发在途未知提交，不用预留后的余额。 |
| BRM04 | Child over-allocation / 子信封超配率 | max(0, child liabilities − distributable cap) / cap; always report excess absolute units too. / 超配正差除可分配上限，并报告绝对超配额。 |
| BRM05 | Scope expansion differences / 范围扩大差异数 | Count extra resource/object/field/tool/environment memberships versus independently recomputed historical scope. / 对比独立重算历史范围，分资源对象字段工具环境计额外成员。 |
| BRM06 | Boundary version drift / 边界版本漂移率 | Runs using stale/inconsistent applicable versions / runs checked against then-effective policy. / 使用过期不一致版本运行数除按当时有效策略核验运行数。 |
| BRM07 | Permit coverage / 许可覆盖率 | Independently observed unique external effects with valid-at-dispatch permits / independently observed effects. / 独立观察效果中具派发时有效许可者除独立效果总体。 |
| BRM08 | Unpermitted effects / 无许可外部效果率 | Proven effects without valid permits / same BRM07 population; unresolved matches remain unknown. / 确证无有效许可效果除同一总体，未决关联保留未知。 |
| BRM09 | Permit refusal ratio / 许可拒绝率 | Denied distinct application attempts / all application attempts, split reason; transport duplicates excluded. / 拒绝的独立申请尝试除全部申请尝试，按原因分组，排除传输重复。 |
| BRM10 | Blocked requested units / 被拦截效果量 | Sum rejected distinct attempts' requested original units; attempted volume may repeat an intent and is not actual or avoided loss. / 累计拒绝尝试的原始请求额度，尝试量可重复意图，不等于实际或避免损失。 |
| BRM11 | Unused permit expiry / 许可过期率 | Permits expired unused / issued permits in the same cohort; dispatched TTL expiry is not unused. / 同总体未用过期许可除已签发许可，已派发后过期不算未用。 |
| BRM12 | Duplicate requests / 重复请求识别数 | Extra distinct submission attempts beyond first per authoritative effect intent; exclude telemetry redelivery. / 每权威效果意图首尝试外的独立提交尝试数，排除观测重复投递。 |
| BRM13 | Duplicate suppression / 重复抑制率 | Proven prevented duplicate sends / identified duplicate attempts, with gateway/downstream evidence. / 有网关下游证据的已阻止重复发送除识别重复尝试。 |
| BRM14 | Key/digest conflicts / 幂等参数冲突率 | Keyed request attempts conflicting with original digest / keyed request attempts. / 与原摘要冲突的带键尝试除全部带键尝试。 |
| BRM15 | Changed-key retries / 换键重试率 | Authoritatively linked retry chains with multiple keys / retry chains; inferred links reported separately. / 权威关联且多键重试链除重试链，推断关联单报。 |
| BRM16 | Unknown occupied ratio / 未知额度占比 | Unresolved occupied units / root limit by cumulative dimension. / 按累计维度未知占用除根上限。 |
| BRM17 | Unknown count / 未知结果数量 | Unresolved logical effects by system, tenant, agent, scenario and age bucket. / 按系统租户主体场景年龄分组未决逻辑效果数。 |
| BRM18 | Unknown age / 未知结果老化时间 | Trusted as-of − first unknown time; preserve original start across retries; median, upper percentile and max. / 可信观察时刻减首个未知时刻，重试不重置，报中位高分位及最大值。 |
| BRM19 | Reconciliation closure / 对账闭环率 | Independently settled success/nonexecution / frozen due-for-reconciliation cohort, including overdue unresolved. / 独立确认成功或未执行数除冻结的应对账总体，包含逾期未决。 |
| BRM20 | Premature unknown releases / 未知误释放数 | Distinct unresolved permits released before conclusive independent settlement. / 独立确定结算前被释放的未决许可数。 |
| BRM21 | Late receipts / 迟到回执率 | Unique receipts after stop/return/closure / receipts in defined window, split triggering milestone. / 窗口内停止返还关闭后唯一回执除回执总体，按触发节点分组。 |
| BRM22 | Peak concurrency / 峰值并发数 | Max reconstructed active slots by run/tenant/tool/system; retain unknown slots per policy. / 按运行租户工具系统重建活动槽位峰值，按策略保留未知槽位。 |
| BRM23 | Concurrent oversell attempts / 并发超卖尝试数 | Conflicting successful admissions from the same authoritative base revision; incomplete revisions yield suspected windows, not proven oversell. / 同一权威基线修订下冲突成功准入数，修订不全只报疑似窗口而非已证超卖。 |
| BRM24 | Spawned workers / Worker 派生数 | Distinct creations and peak concurrently active workers, separate counters. / 唯一创建总数及同时活动峰值分别计数。 |
| BRM25 | Hierarchy depth / 层级深度 | Max parent edges from root (root depth 0); unresolved ancestry unknown, cycles invalid. / 根深度为零的最大父边数，祖先缺失记未知，循环无效。 |
| BRM26 | Authority replication factor / 权力复制系数 | Concurrent active sibling allocations / parent cap; historical closed siblings are not summed. / 同时活动同级分配除父上限，不累加已关闭历史子级。 |
| BRM27 | Effect propagation factor / 效果传播系数 | Unique downstream external effects / upstream approved actions in causally matched cohort, with scenario baseline. / 因果匹配总体的唯一下游效果除上游获批动作，结合场景基线。 |
| BRM28 | Loop cumulative consumption / 循环累计消耗率 | Unique committed loop effects in original units / original root cap, across restarts. / 跨重启循环唯一提交原始额度除原根上限。 |
| BRM29 | Stop effectiveness lag / 停止生效延迟 | Last new permit issue time − trigger time, only if issue history exists; report signed value plus post-effective violations, dispatch lag and stop acknowledgements. / 有签发历史时以最后新许可时间减触发时间，保留正负并另报生效后违规、派发延迟及停止确认。 |
| BRM30 | Post-stop new effects / 停止后新效果数 | New dispatches after authoritative stop, separate from pre-stop sends with late receipts and late external arrival. / 权威停止后新派发数，与停止前发送的迟到回执及外部迟到到达分开。 |
| BRM31 | Reconciliation before resume / 恢复前对账完成率 | Settled affected unknowns at resume / affected unknown cohort requiring closure; holds remain unclosed. / 恢复时已结算受影响未知除须闭环总体，冻结项仍未闭环。 |
| BRM32 | Recurrence after resume / 恢复后复发率 | Eligible resumed runs with same anomaly in complete configured follow-up window / eligible resumed runs; incomplete windows pending. / 完整随访窗内同类复发恢复运行除合格恢复运行，窗口未完记待观察。 |
| BRM33 | Event completeness / 事件完整率 | Events with type-specific required fields / deduplicated received events; source gaps additionally reported. / 类型必需字段齐全事件除去重收到事件，来源缺口另报。 |
| BRM34 | Trace linkage / 轨迹关联率 | Events deterministically linked to run/envelope / events requiring linkage; inferred links separate. / 确定关联运行信封事件除须关联事件，推断关联单报。 |
| BRM35 | Effect traceability / 外部效果可追溯率 | External effects linked to permit, envelope and versioned proposal / independent external-effect inventory. / 关联许可信封及版本化提案的效果除独立外部效果清单。 |
| BRM36 | Freshness / 数据新鲜度 | Observed time − source recorded time by source; negative/skewed values flagged, not clamped to healthy zero. / 按来源采集时间减记录时间，负值偏差标记，不压成健康零值。 |
| BRM37 | Patch adoption / 补丁采纳率 | Unique explicitly accepted patches / unique sent patches, pending/rejected included. / 明确采纳唯一补丁除已发送唯一补丁，保留待办及拒绝。 |
| BRM38 | Alert closure / 告警闭环率 | Alerts with verified disposition / alerts due for handling; acknowledgement alone is not closure. / 核实处理结果告警除应处理告警，仅确认收到不算闭环。 |
| BRM39 | Probe silence / 探针静默时间 | As-of − last successful source heartbeat/ingestion; use source cadence to distinguish inactivity from failure. / 观察时间减最后成功来源心跳采集，结合来源节奏区分无业务与故障。 |

## Alerts, Patches and Reports / 告警、补丁与报告

Informational findings request missing fields or renewals; warnings flag refusal spikes, aging unknowns or degrading stages; high severity requests scoped pause for changed-key retries or stop anomalies; critical findings include proven unpermitted effects, over-allocation, breached hard limits or negative balances. Deduplicate by rule/target/episode, retain merge/escalation history and assign owner/due time. A rejected suggestion retains execution actor and reason without inflating severity. / 提示级请求补字段或续期；警告级覆盖拒绝突增、未知老化或阶段恶化；高危级对换键重试及停止异常建议范围暂停；严重级包括确证无许可效果、超配、硬边界突破或负余额。按规则目标事件段去重，保留合并升级历史及责任期限；建议被拒时记录执行主体理由，不为此夸大等级。

Patches may recover existing parent links, derive cumulative use/age/latency or propose inferred scene labels with confidence. They append an observation view under target/base-revision checks, never change ledger truth. Stop recommendations, reconciliation requests and closure-gap reports follow the shared contract response protocol. / 补丁可查回既有父子关联，派生累计量年龄时延，或带置信度推断场景标签；按目标及基线修订校验后追加观察视图，不改账本真值。停止建议、对账请求及关闭缺口报告遵循共享响应协议。

Each report includes report/run/trace IDs, observation window, source coverage/watermarks, boundary/envelope/permit/effect/unknown/reconciliation/stop summaries, raw metrics, issues, patches, alerts, recommendations, evidence refs, rule/probe versions and generation time. Recommend financial closure only with conserved balances, traceable effects, closed descendants, settled unknowns, handled callback window, resolved critical data conflicts and healthy mandatory sources; manual holds mean continued accounting responsibility. / 报告含报告运行链路标识、观察窗、来源覆盖水位、边界信封许可效果未知对账停止汇总、原始指标、问题补丁告警建议、证据、规则探针版本及生成时间。仅在守恒、效果可追溯、后代关闭、未知结算、回调窗处理、关键冲突解决及必需来源健康时建议账务关闭；人工冻结仍需持续记账责任。

Use the execution profile's scene dimensions. Chain focuses on ordered binding; routing on branch scope/version; parallel on aggregate transactions; orchestration on cross-system stops; loops on cumulative retry history; hierarchy on subtree liability and return. Threshold revisions apply prospectively; old reports retain their original rules. / 使用执行配置的场景维度。链式关注顺序绑定，路由关注分支范围版本，并行关注聚合事务，编排关注跨系统停止，循环关注累计重试，层级关注子树负债返还。阈值修订向前生效，旧报告保留原规则。

<a id="acceptance"></a>
## Probe Acceptance / 探针验收

All scenarios below are **not_executed** integration requirements, not evidence of installed detection. The asset validator checks provenance/coverage only. / 以下均是未执行的集成验收要求，不证明已安装检测；资产校验器仅查来源及覆盖。

| ID | Fixture / 输入场景 | Expected observation / 预期观测 |
| --- | --- | --- |
| BRQ01 | Child totals exceed parent / 子级总和超父级 | Critical conservation finding. / 严重守恒告警。 |
| BRQ02 | Child includes outside object / 子级含范围外对象 | Per-dimension scope difference. / 分维度范围差异。 |
| BRQ03 | Two workers pass on same old balance / 双 Worker 旧余额通过 | Suspected nonatomic window, prove via transaction revisions. / 疑似非原子窗口，以事务修订核实。 |
| BRQ04 | External request without permit / 外部请求无许可 | Link failure; critical when independent evidence proves missing permit. / 关联失败，独立证据确证无许可时严重告警。 |
| BRQ05 | Dispatch after permit expiry / 过期许可派发 | Lifecycle violation. / 生命周期违规。 |
| BRQ06 | Same key different parameters / 同键异参数 | Immutable idempotency conflict. / 不可变幂等冲突。 |
| BRQ07 | New key for same effect / 同效果换键 | Linked retry-chain finding; inferred links labelled. / 重试链问题，推断关联注明。 |
| BRQ08 | Timeout immediately releases quota / 超时立即释放 | Unknown misrelease. / 未知误释放。 |
| BRQ09 | Unknown without reconciliation / 未知长期未对账 | Age, overdue owner and escalation. / 年龄、逾期责任及升级。 |
| BRQ10 | New permit after stop / 停止后新许可 | Stop-boundary violation. / 停止边界违规。 |
| BRQ11 | Pre-stop send, post-stop receipt / 停止前发送后回执 | Late receipt, not post-stop new dispatch. / 迟到回执，不算停止后新派发。 |
| BRQ12 | Each loop creates new root / 每轮新根 | Quota refresh against original task/aggregate account. / 对照原任务聚合账户发现额度刷新。 |
| BRQ13 | New effect after close / 关闭后新效果 | Distinguish late arrival, pre-close send and bypass. / 区分迟到到达、关闭前派发及旁路。 |
| BRQ14 | Missing parent run / 缺失父运行 | Sourced, typed, confidence-labelled patch. / 有来源类型置信度的补丁。 |
| BRQ15 | Authoritative sources disagree / 权威源冲突 | Keep both, no favorable automatic settlement. / 保留双方，不自动择有利结算。 |
| BRQ16 | Source stops updating / 来源停更 | Silence/coverage warning with heartbeat cadence. / 结合心跳节奏静默覆盖告警。 |

Acceptance also needs entry coverage, tenant-safe reconstruction, reproducible derivations, immutable evidence, bounded probe permissions, alert disposition and probe-health detection. High refusal counts can show effective control and executor defects simultaneously; the payroll teaching example is not measured prevention or avoided-loss evidence. / 验收还需入口覆盖、租户隔离重建、可重算派生、不可变证据、受限探针权限、告警闭环及探针健康检测。高拒绝数可同时证明控制有效和执行器缺陷；工资教学示例不是实测拦截或避免损失证据。
