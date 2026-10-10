# Handoff Chain / 交接链 Observability Metrics / 可观测性指标

Cell / 交织点: collaboration-chain / 协作 x 链式

Capability / 能力: Collaboration / 协作

Mode / 模式: Chain / 链式

Identity / 稳定标识: `PATTERN_0043`, `CELL_COLLABORATION_CHAIN`

Status / 状态: `draft`; implementation / 实现状态: `specification_only`.

Source / 来源: Existing paper coordinate / 既有论文坐标 `arXiv:2605.13850`; supplied observability draft / 用户提供的探针草稿 `35_交接链_工作流可观测性探针.md`, document version / 文档版本 `0.1.0`, source interface / 来源接口 `1.0`. The source placeholder `PATTERN_XXXX` is provenance, never a new registry identity. / 来源占位编号仅作出处，不成为新注册身份。

Description / 描述: Reconstruct the version, responsibility, evidence and external-operation chains; disclose gaps and return verifiable, scoped observation supplements without owning execution. / 重建版本、责任、证据与外部操作四条链，披露缺口并返回可验证、有范围的观测补全，不接管业务执行。

Design Pattern File / 设计模式文件: [collaboration-chain.md](collaboration-chain.md). Shared exchange contract / 共享交互契约: [handoff-chain-contract.md](../../handoff-chain-contract.md). Source mapping / 来源映射: [handoff-chain-source-map.json](../../handoff-chain-source-map.json).

## Quick Navigation / 快速导航

- [Standalone use / 独立使用](#standalone)
- [Inputs and events / 输入与事件](#inputs)
- [Probe workflow / 探针流程](#probe-flow)
- [Checks / 探针检查](#checks)
- [Calculation and metrics / 计算口径与指标](#calculation)
- [Shared supplement exchange / 共享补全交换](#exchange)
- [Acceptance cases / 验收用例](#acceptance)
- [Output templates / 输出模板](#output)

<a id="standalone"></a>
## Standalone Use and Boundaries / 独立使用与边界

Use this probe with authorized contracts, events, snapshots, receipts or fixed artifacts even when the execution workflow is unavailable. It answers which version reached the next actor, who produced it from which evidence, whether acceptance became durable, where the failed attempt stopped, and which proof recovery still needs. / 即使执行流程不在线，也可用获授权契约、事件、快照、回执或固定工件独立观察。回答下一棒收到哪一版、谁根据什么产生、接收是否持久成立、失败停在哪一版，以及恢复仍缺什么证明。

The dedicated collector, metric calculators, authenticated patch receiver and deployment adapters are specifications, not implemented services. Document synchronization or structural validation does not prove runtime correctness, metric performance or source test passage. / 专属采集器、指标计算器、认证补丁接收端和部署适配器均为规格，不是已实现服务；文档同步或结构校验不证明运行正确、指标成效或来源测试通过。

### Three operating modes / 三种运行方式

| Mode / 方式 | Inputs and output / 输入与产出 | Execution effect / 对执行的影响 |
| --- | --- | --- |
| Offline independent review / 离线独立审查 | Authorized exports, contracts, snapshots, artifacts and receipts; reconstruct chains, metrics, gaps and recovery suggestions. / 授权导出、契约、快照、工件及回执；重建四链、指标、缺口和恢复建议。 | No live dependency and no replay of real effects. / 不依赖在线执行，不重放真实副作用。 |
| Real-time side observation / 实时旁路观察 | Read-only event streams and authorized references; report provisional windows, waiting ages and alerts. / 只读事件流及授权引用；报告暂定窗口、等待年龄与告警。 | No authority to block or release business actions. / 无业务阻断或放行权。 |
| Bounded interactive supplementation / 有界交互补全 | Exact request, target and allowed data; return patches, source proofs or unavailability reasons. / 精确请求、目标和允许数据；返回补丁、来源证明或无法补全原因。 | Execution independently revalidates and accepts or rejects. / 执行侧独立复验并采纳或拒绝。 |

Separate budgets and permissions for side observation and synchronous supplementation. Every request has a deadline; a report cannot justify unlimited queries or an indefinitely blocked business stage. / 旁路与同步补全分别设置预算和权限；每个请求有截止时间，不为填满报告无限查询或无限挂起业务阶段。

### Evidence sufficiency / 证据充分度

| Available material / 可用材料 | Supported conclusion / 可支持的结论 | Unsupported conclusion / 不可支持的结论 |
| --- | --- | --- |
| Process and contract only / 仅流程契约 | Static risk, field gaps and instrumentation proposals. / 静态风险、字段缺口及埋点建议。 | Actual rates, latency or incident totals. / 实际通过率、时延和事故总量。 |
| Narrative logs or course trace / 自然语言日志或课程轨迹 | Stage/version changes asserted by the text. / 文本声称的阶段与版本变化。 | Durable commit, authenticated acceptance, authority or content correctness. / 持久提交、真实接收、权限及内容正确。 |
| Trusted events, manifests and receipts / 可信事件、清单与回执 | Verifiable version, commit and responsibility relationships. / 可核验的版本、提交和责任关系。 | Whole-artifact semantic correctness without content. / 无实际内容时的全稿语义正确。 |
| Fixed artifacts, evidence and destination receipts / 固定工件、证据与目的端回执 | Scoped binding, content, lineage and effect checks. / 范围内的绑定、内容、血缘和效果检查。 | Global guarantees beyond visible material, authority or time. / 超出材料、权限和时间的全局保证。 |

### Permission scope / 权限范围

Read only explicitly authorized tenants, tasks, resources and time windows; retain source and rule versions for reproducible calculations. External status lookup additionally requires a genuinely read-only adapter, source authorization and query budget. An endpoint that retries, repairs orders or advances state is not read-only. / 仅读取明确授权的租户、任务、资源和时间窗口；计算保留来源及规则版本。外部状态查询还须有真正只读的适配器、来源授权和查询预算；会重试、补单或推进状态的接口不是只读接口。

The probe may append its own observations and propose patches. It cannot alter verified business facts, artifact content, receipts, ownership, control epochs, permissions or formal versions; it cannot repeat a payment, publication or deployment to discover whether the first one succeeded. Model inference cannot manufacture a receipt. / 探针可追加自身观测并提出补丁；不得修改已核查业务事实、工件内容、回执、责任人、控制权代次、权限或正式版本，不得靠再付款、再发布、再部署查明第一次是否成功；模型推断不能补造回执。

A detected violation and an enforced block are distinct facts. Record occurrence, detection, alert and execution-disposition times separately. A side observer reports; execution's existing gate pauses when authorized. An offline alert cannot be counted as prevention of a past violation. / 检测违规和实际阻断是不同事实；分别记录发生、发现、告警及执行处置时间。旁路负责报告，执行方依已有闸门暂停；离线告警不能算作事先阻止历史违规。

<a id="inputs"></a>
## Minimum Inputs and Event Semantics / 最小输入与事件语义

The observation contract must freeze scope (`tenant_id`, `workflow_id`, `task_id`, `chain_id`), start/end window, observation cutoff, source inventory and adapters, allowed reads, masking/retention, output destination, rule versions, query/time/cost budgets and maximum supplement rounds. Missing permissions produce a restricted report, never implicit expansion. / 观测契约必须固定安全域与业务作用域、起止窗口、观察截至点、来源清单及适配器、允许读取、脱敏保留、输出位置、规则版本、查询时间费用预算和最大补全轮数。权限不足产出受限报告，不隐式扩权。

Supply workflow/stage contracts, immutable formal manifests, receipt indexes, original events, candidate/formal artifacts, fact/evidence references, external-operation ledgers, policy/authority versions and active supplement requests where available. Contracts and independent indexes establish expected populations; collected rows alone are not completeness denominators. / 按可用范围提供工作流及阶段契约、不可变正式清单、回执索引、原始事件、候选及正式工件、事实证据引用、外部操作账本、策略授权版本和活动补全请求。契约及独立索引确定应有对象全集，不能把已采集行直接作为完整性分母。

### Business semantics / 业务语义

A formal baton is immutable. A stage proposes a candidate delta; only authorized receiver acceptance followed by durable runtime commit creates the next version and transfers control. Rejection does not advance that attempt, and replay of an already accepted candidate returns its original receipt. `v2 → v2` describes the failed attempt; if another valid commit already advanced the head, it does not instruct a head rollback. / 正式接力棒不可变；阶段提出候选增量，经有权接收者验收及运行时持久提交才产生下一版并转移控制权。拒收不推进该尝试，同一已接收候选重发返回原回执。`v2 → v2` 描述失败尝试；其他合法提交已推进头版本时，不代表应回退全局头。

Unchanged formal state does not prove absence of external effects. A sent operation whose result is unknown remains unknown until authoritative reconciliation; sending success is not confirmed business success. / 正式状态不变不证明没有外部效果；已发送而结果未知的操作须保持未知，直至权威查证；发送成功不等于业务效果成功。

| Identity / 标识 | Meaning / 语义 |
| --- | --- |
| Scope quartet / 作用域四元组 | `tenant_id`, `workflow_id`, `task_id`, `chain_id` jointly constrain every join. / 四者共同约束关联，不能跨域拼接。 |
| `stage_instance_id` | One logical stage, stable across retries; a new loop iteration has a new instance. / 一次逻辑阶段，重试不变；循环新轮次另建实例。 |
| `attempt_id` | One execution attempt, including attempts that fail before any handoff. / 一次实际执行尝试，包括交接前失败。 |
| `handoff_id` | One immutable candidate package; retransmission retains it, changed content creates another. / 一份不可变候选包；重发保留，改内容新建。 |
| `operation_id` | One external business intent, stable across network retries. / 一次外部业务意图，网络重试不变。 |
| `event_id`, `source_system`, `source_sequence` | Event identity plus registered source and authoritative stream order; never substitute arrival order for a missing sequence. / 事件身份、登记来源及权威流内顺序；缺来源序号不能用到达顺序伪造。 |
| `control_epoch`, input/output versions / 控制代次与输入输出版本 | Execution eligibility generation and the attempt's formal input/committed output, distinct from current head. / 执行资格代次与该尝试的正式输入、已提交输出，和当前头版本分开。 |

Use [the shared contract](../../handoff-chain-contract.md) for event, request, patch and adoption-receipt fields. Events bind protocol/source identity, occurrence and persistence times, scope, stage/attempt/candidate/operation, input/output versions, manifest digest, artifact and receipt references, authenticated actor/receiver, epoch, contract/policy version, reason and evidence. / 事件、请求、补丁及采纳回执字段以共享契约为准；事件绑定协议及来源身份、发生与持久化时间、作用域、阶段尝试候选操作、输入输出版本、清单摘要、工件回执引用、认证主体接收者、代次、契约策略版本、原因及证据。

IDs and versions of protocols are nonempty strings; state versions, epochs and source sequences are nonnegative integers, optional unavailable values are null. Times carry time zones, references/observations are arrays, scope/target are objects and digests declare their algorithm and fixed content. Unsupported major versions are rejected; only declared extension fields are admitted. The probe may add `ingested_at`, collection batch, normalization version and trust labels without overwriting original content or timestamps. / 身份及协议版本为非空字符串；状态版本、代次和来源序号为非负整数，可选未知值为空。时间带时区，引用观测为数组，作用域目标为对象，摘要声明算法及固定内容。未知大版本拒绝，仅接受声明的扩展字段。探针可追加采集时间、批次、归一规则和可信标签，不覆盖原内容或时间。

| Event family / 事件类别 | Events to distinguish / 必须区分的事件 |
| --- | --- |
| Stage / 阶段 | Start, candidate ready, handoff submitted. / 开始、候选完成、交接提交。 |
| Acceptance and commit / 验收提交 | Accepted/rejected/unknown verdict, durable commit, responsibility transfer. / 验收通过、拒绝、未知，持久提交及责任转移。 |
| External effect / 外部效果 | Intent prepared, sent, confirmed success/failure, unknown, reconciliation, compensation. / 意图准备、发送、确认成功失败、未知、查证和补偿。 |
| Supplement / 补全 | Request, patch return, adopted/partially adopted/rejected/expired disposition. / 请求、返回、采纳、部分采纳、拒绝及过期。 |
| Recovery and end / 恢复终结 | Retry, checkpoint recovery, human escalation, cancellation, terminal task result. / 重试、检查点恢复、人工升级、取消及任务终结。 |

<a id="probe-flow"></a>
## Probe Workflow / 探针工作流

The eight source nodes remain distinct from the business execution nodes. Every check produces a rule version, target binding, evidence references, execution time, limitations and one of `pass`, `fail`, `unknown`, `not_applicable`; these outcomes never imply business approval. / 八个来源节点与业务执行节点分开；每项检查产出规则版本、目标绑定、证据引用、执行时间、限制及通过、失败、未知、不适用四态之一，均不等于业务批准。

<!-- handoff:probe_nodes:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HP00 | Check observation authority / 检查观察资格 | Declare operating mode, tenant/task/window, authorized sources, observation cutoff and budgets. Check read permissions and disclose invisible material; do not infer authority from data availability. Do not follow cross-domain or unknown links without explicit authority or share business credentials with other models. Declare unsupported or partially observable when protocol semantics cannot be mapped.<br>固定目标安全域、任务集合、时间窗口、观察截止时间、允许来源、访问权限、脱敏策略、预算和输出目的。没有明确权限，不追踪越域引用，不抓取未知链接，不把业务凭证转交给其他模型或提供方。<br><br>静态审查可从文档开始；真实观测必须注明数据来源与采集方式。遇到未知协议或无法迁移的契约，返回不支持或部分可观察，不自行猜测字段含义。 |
| HP01 | Collect and preserve evidence / 采集与保留原始证据 | Read official manifests, authenticated receipts, immutable artifacts and external evidence. Retain provenance, identity, content digests and original timestamps; mutable material must not masquerade as a historical snapshot. Preserve pagination cursors, source watermarks and cutoffs, and separate raw evidence from normalized views. A query that triggers retry, settlement or business state changes is not an admissible read-only adapter.<br>读取原始事件、正式回执索引、版本清单与工件引用；记录分页游标、来源水位和采集截止点，避免遗漏分页或恢复后重复计算。原始证据与归一化视图分开存储。<br><br>只读适配器必须真正不产生业务副作用。查询接口若会触发重试、补单或状态迁移，就不能作为普通观察来源使用。 |
| HP02 | Deduplicate and handle time / 去重与时间处理 | Deduplicate by scoped event identity, flag same-ID conflicting payloads and track source watermarks. Reconstruct causal order and distinguish occurred, persisted and ingested time; incompatible clocks cannot yield invented precise latency. Retain provisional reports and late-event revisions. Cancellation, timeouts and long-running unresolved items must remain visible instead of disappearing from denominators.<br>按来源和 `event_id` 去重；同身份同内容是重复投递，同身份不同内容是完整性异常。业务决策按 `handoff_id` 归并，外部效果按 `operation_id` 和远端真实交易／发布身份归并，不能把多个回执副本算成多次效果。<br><br>版本和因果关系优先于日志到达顺序。跨节点时间没有可信同步或误差范围时，不计算精确跨节点时延；负时延不能直接截断为零。能够使用同一可信节点或单调时钟测量时，记录所用计时方式。<br><br>实时报告设置迟到容忍窗口和观察水位，未收齐的结果标为暂定。迟到事件到达后更新报告版本和变更原因，保留旧报告的观察截止点。取消、超时与长期未完成项单独统计，不能静默从分母消失。 |
| HP03 | Reconstruct four linked chains / 重建四条关联链 | Rebuild official versions, responsibility, evidence dependencies and external operations separately. Preserve provisional outputs, acceptance opinions, committed receipts and external business receipts as distinct facts; disclose broken or unknown links. Query official snapshots and receipt indexes before declaring gaps, but never fabricate missing commits from version differences. Reconstruct branches as a parent-linked dependency graph and recognize merges only under explicit aggregation rules.<br>&#124; 链 &#124; 重建依据 &#124; 必须发现的异常 &#124;<br>&#124;---&#124;---&#124;---&#124;<br>&#124; 版本链 &#124; 输入／输出版本、清单摘要、父版本关系、正式回执 &#124; 无权威提交的推进、缺失版本、重复后继、错误回退 &#124;<br>&#124; 责任链 &#124; 已认证接收者、正式提交、当前责任、控制权代次 &#124; 发送即转责、长期无人负责、重叠有效资格、旧资格晚到 &#124;<br>&#124; 证据链 &#124; 事实身份、生产者、来源、工件摘要、核验版本 &#124; 来源丢失、失效事实、旧审批、内容与声明不一致 &#124;<br>&#124; 外部操作链 &#124; 业务意图、载荷、发送、远端回执、查证和补偿 &#124; 同键不同载荷、重复效果、长期未知、未闭合补偿 &#124;<br><br>缺失事件时，先查正式快照和回执索引。查到原本存在的权威记录，可以追加恢复的观测引用；查不到就保留断点，不能根据版本差推测并伪造每次历史提交。<br><br>存在分支时按分支和父版本重建依赖图。只有带明确聚合规则的提交才视为合并，不能把两条分支简单排序成线性链。 |
| HP04 | Run evidence-bounded checks / 运行探针检查 | Evaluate contract, scope, version, ownership, validity, content, acceptance, recovery, idempotence, patches and collection integrity using authenticated evidence; distinguish confirmed violation, unknown and not applicable. Every check records target, rule, evidence, execution time and limitations. Trust source identity only through authenticated collection; recompute actual immutable content and read supporting facts rather than comparing two self-reported digest fields.<br>每个检查输出“通过、失败、未知、不适用”，同时记录检查规则、目标工件、证据、执行时间与限制。来源标签由可信采集路径确定，不能接受日志自称“我是权威系统”。<br><br>工件实际摘要应从固定版本内容重算。语义检查须读取实际关键内容及其支撑事实；只看到两个摘要字段相等，最多支持字段一致，不能支持稿件真实正确。标题、摘要、表格、附件和发布载荷都应按业务契约纳入范围。 |
| HP05 | Compute metrics and gaps / 计算指标并生成缺口 | Freeze scope, units, cohorts, cutoff and definitions; report numerator, denominator, unknown, pending, coverage and evidence. Unknown populations make metrics uncomputable, not zero. Interpret frequent rejection jointly with escaped errors and final outcomes: it may indicate poor upstream quality or effective gates, not a proven cause by itself.<br>先冻结指标适用对象，再计算分子、分母、未知项与覆盖率。每个比率同时返回计数；缺少分母来源时返回不可计算，不给出看似精确的百分比。<br><br>指标只描述材料支持的结论。频繁拒绝可能意味着上游质量差，也可能意味着闸门有效，必须与错误逃逸和最终结果联合解释。 |
| HP06 | Bounded supplementation / 有界补全 | Perform only authorized read-only queries or deterministic derivation for requested fields and exact targets. Stop on deadline, cost or round limits; return evidence-backed observations or explicit unknown without business effects. Prefer existing ledgers, fixed artifacts, authorized source queries and then deterministic derivation under the business contract. Preserve conflicting sources with their versions and authority scope; neither majority voting nor one authority proves facts outside that authority.<br>按“已有账本→固定工件→权威来源只读查询→确定性派生”的顺序查证，具体来源优先级由业务契约决定。不同权威在不同字段上有不同职责；银行回执不能证明审批合规，审批票不能证明钱已到账。<br><br>补全达到轮数、时间、调用数或费用限制即停止，并报告剩余缺口。冲突来源不能用多数投票硬凑成一致事实；应保留版本、时间和权威范围，交有权阶段裁定。 |
| HP07 | Deliver and track adoption / 交付并观察反馈 | Report facts, uncertainty, hypotheses, recommendations and limitations. Bind patches to target and provenance, await execution-side adoption receipts and revise reports for late evidence; reporting or patch delivery alone proves no business repair.<br>离线模式交付报告和可复算指标；实时模式交付带观察截止点的告警；交互模式返回绑定请求的补丁。仅收到执行流程的正式采纳回执后，才统计为已采纳。<br><br>执行流程如何处置，由它自己的权限和策略决定。未收到反馈应标为待确认，不写成已修复。探针发现历史错误后，修复通常需要新业务事件，而不是改写旧日志。 |
<!-- handoff:probe_nodes:end -->

### Source order, time and completeness / 来源顺序、时间与完整性

Deduplicate within the scoped registered source by `(source_system, event_id)`. Exact content replay is a delivery duplicate; divergent content under the same identity is an integrity conflict, not last-write-wins. Deduplicate decisions by immutable `handoff_id`, and effects by `operation_id` plus authenticated remote effect identity; multiple receipt copies are not multiple effects. / 在有范围的登记来源内按来源系统与事件身份去重；同内容重投是投递重复，同身份异内容是完整性冲突，不以后到者覆盖。决定按候选包归并，效果按业务意图及认证远端效果身份归并，多份回执副本不是多次效果。

Prefer authoritative sequence, parent versions and causal references to arrival time. Preserve `occurred_at`, `recorded_at` and `ingested_at` independently. Cross-host durations require synchronized clocks with known uncertainty or a common trusted monotonic clock domain; otherwise return unknown or an explicit uncertainty interval. A negative duration cannot be clamped to zero. / 权威序号、父版本和因果引用优先于到达时间；分别保留发生、持久化和采集时间。跨主机时延须时钟同步且误差已知，或使用同一可信单调时钟域；否则未知或给出明确误差区间，不能把负时延截成零。

Freeze per-source watermarks, cursor ranges, lateness tolerance and observation cutoff. Without a closed source watermark, a report remains provisional. A late/corrected record produces a new report revision and change reason while retaining the prior cutoff; it does not rewrite history. Canceled, timed-out and long-pending objects remain explicit cohorts. / 固定逐来源水位、游标范围、迟到容忍和观察截至点；没有封闭水位时报告保持暂定。迟到纠错生成新报告版本及原因，保留旧截至点，不改写历史；取消、超时、长期未决对象保留为明确队列。

### Four reconstructed chains / 四条重建链

| Chain / 链 | Required evidence / 所需证据 | Findings / 发现 |
| --- | --- | --- |
| Version / 版本 | Parent/input/output versions, actual manifest digests and authoritative commit receipts. / 父版本、输入输出版本、实际清单摘要及权威提交回执。 | Unbacked advancement, missing version, duplicate successor or erroneous rollback. / 无依据推进、缺版、重复后继及错误回退。 |
| Responsibility / 责任 | Authenticated accepting actor, commit, current owner and control epoch. / 认证验收者、提交、当前责任人及控制代次。 | Send-as-transfer, ownerless intervals, overlapping eligibility or stale actors. / 发送即转责、无人负责、资格重叠及旧资格晚到。 |
| Evidence / 证据 | Fact identity, producer, source, artifact digest, verification scope/version and withdrawal/supersession. / 事实身份、生产者、来源、工件摘要、核验范围版本及撤销替代。 | Missing lineage, invalid facts, stale approval or unsupported content. / 来源丢失、失效事实、旧审批及内容不受支持。 |
| External operation / 外部操作 | Stable intent, payload, send, remote result, reconciliation and compensation. / 稳定意图、载荷、发送、远端结果、查证及补偿。 | Same key/different payload, duplicate effect, persistent unknown or open compensation. / 同键异载荷、重复效果、长期未知及补偿未闭合。 |

When events are absent, first query authorized snapshots and receipt indexes. A recovered original receipt may be appended as an observation reference; a version gap cannot justify inventing historical commits. Branches form a dependency graph, and only explicit aggregation rules permit a merge; never sort branches into an invented linear chain. / 缺事件时先查授权快照和回执索引；恢复原回执可追加观测引用，不能凭版本差补造历史提交。分支形成依赖图，仅明确聚合规则允许合并，不能把分支强排成虚构线性链。

<a id="checks"></a>
## Probe Checks / 探针检查

Trusted ingress determines source authority; a log claiming approval is not self-authenticating. Digest equality of two declared fields proves only field agreement. Recompute from the exact fixed content; inspect titles, body, tables, attachments and outgoing payloads according to the contract. Semantic checks need actual content and its supporting facts. / 来源权威由可信接入核验，日志自称批准不自证身份。两个声明摘要相等仅证明字段一致；须读精确固定内容复算，并按契约检查标题、正文、表格、附件和发出载荷。语义检查需要实际内容及支持事实。

<!-- handoff:probe_checks:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HCP01 | Contract completeness / 契约完整性 | Inspect fixed stage input/output, receiver and failure policy with ownership rules; identify unclear boundaries, missing mandatory fields and unknown extensions.<br>阶段输入、输出、接收者、失败策略<br>固定版本契约与字段所有权规则<br>边界不明、必填缺失、未知扩展 |
| HCP02 | Scope consistency / 作用域一致性 | Compare authenticated identity and authorization with task, security domain, resource and receiver; detect cross-task joins, cross-domain reads and handoffs.<br>任务、安全域、资源、接收者<br>已认证身份与授权范围<br>跨任务拼接、越域读取或交接 |
| HCP03 | Version continuity / 版本连续性 | Use manifests, parent lineage and authoritative receipts to detect unsupported advancement, duplicate commit and incorrect rollback.<br>候选和正式提交<br>清单摘要、父版本与权威回执<br>无依据推进、双重提交、错误回退 |
| HCP04 | Field ownership / 字段所有权 | Compare authenticated producer, stage contract and delta; detect edits overriding verified facts or fabricated approval.<br>阶段增量和事实生产者<br>身份、契约、增量内容<br>编辑覆盖核查结果、伪造审批 |
| HCP05 | Fact validity / 事实有效性 | Check consumed versions, applicability, revocation and supersession records; detect obsolete or expired facts returning as current truth.<br>实际消费的事实集合<br>事实版本、适用范围、撤销和替代记录<br>旧结论复活、过期事实继续使用 |
| HCP06 | Artifact integrity / 工件完整性 | Read immutable content and recompute under declared rules against approval digests; detect replaced content or unchecked self-reported digests.<br>实际工件内容与声明摘要<br>不可变内容、重算规则和审批摘要<br>内容被替换、摘要自报未复算 |
| HCP07 | Content support / 内容支持关系 | Inspect actual titles, body, tables and payload against supporting facts and review coverage; detect old content with new digest or lost qualifications.<br>标题、正文、表格、关键载荷<br>实际内容、支撑事实、核验范围<br>新摘要配旧正文、限定条件丢失 |
| HCP08 | Established acceptance / 接收成立性 | Require authenticated acceptance, official commit and control records; distinguish successful delivery from responsibility transfer.<br>接收方签收与责任转移<br>验收身份、正式提交、控制权记录<br>把发送成功当接收成功 |
| HCP09 | Correct recovery / 恢复正确性 | Use the last committed receipt, still-valid evidence and recovery history; detect provisional recovery points or unnecessary full-chain reruns.<br>失败、检查点和重试范围<br>最后正式回执、证据有效性、恢复事件<br>从半成品恢复、不必要地全链重跑 |
| HCP10 | Idempotence and reconciliation / 幂等与查证 | Use stable business intent, payload and authoritative remote effects; detect duplicate effects, same-key changed payload or blind retry of unknown outcomes.<br>外部业务操作<br>稳定意图身份、载荷、远端效果证明<br>重复效果、同键异载荷、未知即重发 |
| HCP11 | Trustworthy supplementation / 补全可信性 | Compare request, target version, provenance, whitelist and adoption receipt; detect inference presented as fact or adopted stale patches.<br>补全请求、补丁和采纳<br>来源、目标版本、字段白名单、采纳回执<br>推断冒充事实、过期补丁被接受 |
| HCP12 | Observation completeness / 观察完整性 | Compare collection against independent authoritative index, sequences, watermarks and page ranges; disclose lost events, untreated disorder and observer blind spots.<br>采集流与应有记录<br>权威索引、序号、水位、分页范围<br>事件缺失、乱序未处理、自身失明 |
<!-- handoff:probe_checks:end -->

Record model-assisted checker version, inputs and public verifiable conclusions; do not request or store private chain-of-thought. A scoped pass is not a perpetual system-wide reliability guarantee. / 模型辅助检查记录版本、输入及可核查公开结论，不索取或保存私密思维过程；范围内通过不等于整个系统永久可靠。

<a id="calculation"></a>
## Calculation Semantics / 计算口径

Freeze tenant/task/window, workflow/contract/policy/metric versions, expected object populations and lateness rules before calculation. Do not compare mixtures of stage responsibilities or risk grades as one cohort. / 计算前固定租户任务窗口、工作流契约策略指标版本、应有对象全集和迟到规则，不把不同职责阶段或风险等级混作单一队列比较。

| Calculability / 可计算性 | Meaning / 含义 |
| --- | --- |
| `calculable` / 可计算 | Required fields and expected denominator are known for the declared population. / 声明总体的必需字段和应有分母已知。 |
| `partially_calculable` / 部分可计算 | Verified subset only; disclose subset denominator, coverage, unknown count and limitation. / 仅验证子集可算；披露子集分母、覆盖率、未知数量和限制。 |
| `not_calculable` / 不可计算 | Applicable but denominator, authority, content, association or compatible clock is missing; value is null. / 适用但缺分母、权威、内容、关联或可比时钟，数值为空。 |
| `not_applicable` / 不适用 | Contract defines no opportunity for this check, or a known applicable population is empty; explain why. / 契约无该检查机会或已知适用集合为空，须说明原因。 |

A zero denominator is not 100%; an unknown population is not an empty population. A count may be confirmed zero only with complete relevant authoritative coverage. Preserve pending, unknown, canceled, timed-out, excluded and not-applicable objects separately. Ratios over checked subsets require coverage and cannot represent unseen system-wide performance. / 零分母不是 100%，未知总体不是空总体。只有相关权威覆盖完整时才能确认计数为零。分别保留未决、未知、取消、超时、排除及不适用对象；已检查子集比率须附覆盖率，不能代表不可见的全系统表现。

The units are distinct: logical stage, execution attempt, immutable candidate, transport redelivery, external business intent, remote effect, original missing field and patch assessment. Two revised candidates are two handoff attempts; three deliveries of one candidate remain one. Execution-before-submission failures require stage-start/failure records and cannot be reconstructed from handoff logs alone. / 逻辑阶段、执行尝试、不可变候选、传输重投、外部业务意图、远端效果、原始缺失字段和补丁评估是不同单位。两份修订候选是两次交接尝试，同包投递三次仍算一次。提交前失败需要阶段开始失败记录，不能仅靠交接日志推算。

Every metric includes definition version, grain, population/snapshot, numerator/denominator where applicable, value/unit, calculability, known/unknown/pending/excluded counts, coverage, sources, cutoff, report revision and limitations. Latency includes valid sample count and a versioned median rule; p95 defaults to nearest rank `ceil(0.95 × n)`. Algorithm changes require a definition version change, and tiny samples cannot establish an SLO. / 每项指标包含口径版本、粒度、总体快照、适用分子分母、值单位、可计算性、已知未知未决排除数、覆盖率、来源、截至点、报告版本和限制。时延附有效样本数及版本化中位数规则，p95 默认最近秩 `ceil(0.95 × n)`；换算法须换定义版本，小样本不能据此立服务承诺。

## Observability Metrics / 可观测性指标

The following 30 source definitions `HCM01–HCM30` are specification-only; they do not alias other mode dictionaries or registered `CSM` calculators. / 以下 30 项来源定义均仅为规格，不是其他模式指标或已注册 `CSM` 计算器的别名。

- 质量指标 / Quality Metrics: HCM01–HCM11 describe acceptance, checked content, provenance and valid recovery. / 描述交接接收、内容核验、来源和有效恢复。
- 时延指标 / Latency Metrics: HCM20, HCM22–HCM23 and HCM28 separate reconciliation, acceptance wait, pending age and actual probe blocking. / 区分查证、接收等待、未决年龄及实际探针阻塞。
- 成本指标 / Cost Metrics: HCM04 describes submission amplification and HCM29 accounts for probe resources separately. / 分别描述提交放大及独立探针资源消耗。
- 风险指标 / Risk Metrics: HCM12–HCM21 and HCM26 retain individual safety violations and unresolved effects. / 保留单项安全违规及未决效果。
- Trace 指标 / Trace Metrics: HCM15, HCM24–HCM27 and HCM30 describe responsibility evidence, supplement adoption, source coverage and report revisions. / 描述责任证据、补全采纳、来源覆盖及报告修订。

<!-- handoff:metrics:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HCM01 | Handoff attempt acceptance rate / 交接尝试接收率 | Formally accepted unique candidates / unique candidates with final accept-or-reject decisions. Report pending counts and ages separately; acceptance opinion alone is not formal acceptance.<br>已正式接收的唯一候选包数 ÷ 已有终局接收／拒绝决定的唯一候选包数<br>Boundary / 边界：未决候选另报数量与年龄；仅有验收意见不算正式接收 |
| HCM02 | Stage first-handoff pass rate / 阶段首次交接通过率 | Stage instances whose first candidate was formally accepted / instances whose first candidate has a terminal decision. This excludes pre-submission execution failures and is not overall execution first-pass rate.<br>第一份候选就被正式接收的阶段实例数 ÷ 第一份候选已有终局决定的阶段实例数<br>Boundary / 边界：这是交接首过，不是包含提交前失败的整体执行首过 |
| HCM03 | Stage final-handoff pass rate / 阶段最终交接通过率 | Instances finally accepted within the settlement window / instances due to settle in that window. Keep failures and timeouts in the denominator and list not-yet-due work separately.<br>在指定结算窗口内最终被接收的阶段实例数 ÷ 应在窗口内结算的阶段实例数<br>Boundary / 边界：按契约截止结算，失败和超时不能被剔除；未到期另列 |
| HCM04 | Handoff submission amplification / 交接提交放大率 | Unique candidate packages / stage instances that submitted at least one candidate. Exclude transport retries; this is not model-call, compute or financial amplification.<br>唯一候选包数 ÷ 至少提交过候选包的阶段实例数<br>Boundary / 边界：不含传输重发；不能替代模型调用、算力或费用放大率 |
| HCM05 | Stale-input interception rate / 过期输入拦截率 | Confirmed stale candidates blocked before commit / all stale candidates established by independent inspection, including escapes. Report inspection coverage.<br>提交前被拦截的已确认过期候选数 ÷ 经独立核查确认过期的候选总数<br>Boundary / 边界：分母同时包含已拦截与已逃逸；必须报告核查覆盖率 |
| HCM06 | Invalid-fact escape rate / 旧事实逃逸率 | Accepted artifacts later confirmed to use invalid facts / accepted artifacts with completed fact-validity checks. List unchecked artifacts; digest-only checking does not establish content review.<br>正式接收后确认使用失效事实的工件数 ÷ 已完成事实有效性检查的正式工件数<br>Boundary / 边界：未检查工件另列；只查摘要不能当成已完成内容检查 |
| HCM07 | Content verification coverage / 内容核验覆盖率 | Critical artifacts with completed contract-required content checks / critical artifacts requiring such checks. Include declared title, attachment and payload scope.<br>已完成契约要求内容检查的关键工件数 ÷ 契约要求检查的关键工件数<br>Boundary / 边界：标题、附件和载荷等须按所声明范围覆盖 |
| HCM08 | Provenance-chain completeness / 来源链完整率 | Required facts with complete, expandable, authenticated provenance / contract-required facts. Complete provenance does not establish factual truth or content correctness.<br>具有完整、可展开且身份可验证来源链的必需事实数 ÷ 契约要求的必需事实数<br>Boundary / 边界：完整来源链不等于事实真实或内容正确 |
| HCM09 | Artifact digest recheck coverage / 工件摘要复核覆盖率 | Required artifacts whose digest was recomputed from actual fixed content / artifacts requiring recheck. Distinguish digest equality from independent recomputation.<br>从实际固定内容重算过摘要的必需工件数 ÷ 应复核的必需工件数<br>Boundary / 边界：摘要相同与摘要已复核分别统计 |
| HCM10 | Local recovery success rate / 局部恢复成功率 | Applicable recoveries settled by deadline that reused valid upstream work and redid only necessary work / applicable recoveries due to settle. Classify invalid upstream work separately rather than requiring current-stage-only recovery.<br>在时限内复用有效上游成果并只重做必要部分的恢复事件数 ÷ 已到结算期限的适用恢复事件数<br>Boundary / 边界：上游已经失效的事件单独分类，不强求只重做当前一棒 |
| HCM11 | Valid checkpoint reuse rate / 有效检查点复用率 | Still-valid prior stages actually reused during recovery / valid prior stages available for reuse. Record the eligible cohort for each recovery to avoid chain-length bias.<br>恢复时实际复用的仍有效前序阶段数 ÷ 恢复时可复用的有效前序阶段数<br>Boundary / 边界：按恢复事件记录候选集合，避免不同链长误导比较 |
| HCM12 | Illegal version advancement count / 非法版本推进数 | Count version advances confirmed to lack lawful acceptance and official commit evidence. Missing logs require unknown status and ledger lookup, not automatic conviction.<br>确认没有合法接收与正式提交依据的版本推进数量<br>Boundary / 边界：缺失日志先标未知并查账本，不直接定罪 |
| HCM13 | Duplicate official commit count / 重复正式提交数 | Count additional official commits for the same immutable candidate. Duplicate delivery of a receipt does not count.<br>同一候选包对应多次正式提交的额外提交数<br>Boundary / 边界：回执重复投递不算重复提交 |
| HCM14 | Unauthorized field commit count / 越权字段提交数 | Count formally accepted deltas confirmed to violate field ownership. Report blocked attempts separately.<br>已正式接收且确认越过字段所有权的增量数量<br>Boundary / 边界：被成功拦截的尝试另计 |
| HCM15 | Responsibility-transfer evidence completeness / 责任转移证据完整率 | Transfers with lawful acceptor, official receipt and corresponding control record / formal transfers that should occur. Planned receivers cannot replace actual receivers.<br>同时有合法验收者、提交回执和对应控制权记录的转移数 ÷ 应发生的正式转移数<br>Boundary / 边界：计划接收者不能替代实际接收者 |
| HCM16 | Ownerless handoff count and maximum age / 无主交接数量与最长年龄 | Count and age handoffs past allowed wait with no valid accountable owner. Ordinary waiting while the original owner remains responsible is not ownerlessness.<br>超过允许等待时间且找不到有效责任归属的交接数量和持续时间<br>Boundary / 边界：保留原责任人的正常等待不自动算无主 |
| HCM17 | Expired-eligibility operation count / 过期资格操作数 | Count accepted commits or external writes under an expired control epoch. Require gateway or recipient evidence, not only a local lock.<br>使用失效控制权代次仍被接收的提交或外部写入数<br>Boundary / 边界：需有网关／接收端证据，不只看本地锁 |
| HCM18 | Duplicate external-effect count / 重复外部效果数 | For each unique business intent, count confirmed remote effects beyond its allowed count. Deduplicate by real remote effect identity, not receipt copies.<br>对每个唯一业务意图，累计超出允许次数的已确认远端效果数<br>Boundary / 边界：必须识别远端真实效果身份；多个回执副本不能重复算 |
| HCM19 | Unresolved external-operation count and age / 未决外部操作数与年龄 | Count and age unique sent business operations lacking confirmed final effects. Unknown is neither success nor proven non-execution.<br>已发送但未确认最终效果的唯一业务操作数及等待年龄<br>Boundary / 边界：结果未知不计为成功，也不自动计为未执行 |
| HCM20 | Reconciliation completion latency / 查证完成时延 | Measure from first recorded unknown outcome to authoritative result confirmation. Incomparable clocks yield unknown; unresolved operations retain current age.<br>首次记录结果未知至权威结果被确认之间的时间<br>Boundary / 边界：时钟不可比较时返回未知；未完成者报告当前年龄 |
| HCM21 | Open compensation count and age / 补偿未闭合数量与年龄 | Count and age required compensation obligations without effect-completion evidence. A completed attempt does not prove compensation's effect.<br>已提出且必须完成、但尚无完成证据的补偿数量及年龄<br>Boundary / 边界：补偿尝试完成不等于补偿效果完成 |
| HCM22 | Acceptance seam latency / 接收接缝时延 | Time from candidate submission to formal acceptance commit; report median and nearest-rank p95 with sample size. Separate accepted and rejected groups and retain unfinished waits.<br>候选包提交至正式接收提交的时长，报告中位数、百分之九十五分位<br>Boundary / 边界：接收和拒绝分组；等待未结束者另列，不静默丢弃 |
| HCM23 | Pending handoff count and age / 未决交接数量与年龄 | Count and age submitted unique candidates without terminal acceptance or rejection. Interpret against observation watermarks before alleging missing decisions.<br>已提交但没有终局接收／拒绝决定的唯一候选包数及年龄<br>Boundary / 边界：结合观察水位判断，防止把迟到误判为丢失 |
| HCM24 | Evidence-backed supplement completion rate / 证据化补全完成率 | Originally requested missing observation fields adopted by deadline with qualifying evidence / requested missing fields whose deadline has arrived. Do not inflate the numerator by adding easier fields.<br>在截止前被采纳且有合格证据的缺失观测字段数 ÷ 已到截止期限的请求缺失字段数<br>Boundary / 边界：以请求最初的字段集合为准，不能补容易的新字段扩大分子 |
| HCM25 | Observation patch adoption rate / 观测补丁采纳率 | Valid evaluated patches adopted, or adopted portions counted by a fixed field unit / valid patches with completed evaluation. Fix the unit and report expired, unauthorized and pending patches separately.<br>已采纳或按字段统计已采纳部分的有效补丁数 ÷ 已完成评估的有效补丁数<br>Boundary / 边界：单位必须固定；过期、越权、待确认分别列出 |
| HCM26 | Invalid adopted patch count / 非法补丁被采纳数 | Count patches confirmed stale, unauthorized or without provenance that were nevertheless adopted. Require execution-side adoption receipts, not probe sending logs.<br>已确认过期、越权或无来源但仍被采纳的补丁数量<br>Boundary / 边界：需要执行侧采纳回执，不能只靠探针发送日志 |
| HCM27 | Event collection coverage / 事件采集覆盖率 | Collected and uniquely matched expected authoritative records / expected records from an independent authoritative index. Uncomputable without an independent index or complete sequence range.<br>已采集且唯一匹配的应有权威记录数 ÷ 独立权威索引确定的应有记录数<br>Boundary / 边界：无独立索引或完整序号范围时不可计算 |
| HCM28 | Probe blocking overhead / 探针阻塞开销 | Measure the union of execution-side intervals explicitly waiting for probes. Do not sum overlapping waits or equate all side-channel duration with business blocking.<br>执行侧明确等待探针的时间区间之并集<br>Boundary / 边界：并行请求不能简单相加；旁路耗时不全算业务阻塞 |
| HCM29 | Probe resource cost / 探针资源成本 | Report the probe's own queries, reads, computation and billing. Keep execution-model costs separate; missing rates mean monetary cost unknown.<br>探针自己的查询数、读取量、计算量和计费记录<br>Boundary / 边界：不与执行模型费用混算；费率缺失则金额未知 |
| HCM30 | Report revision volume / 报告修订量 | Count metric or finding changes caused by late evidence or corrections. Record each reason and new observation cutoff.<br>因迟到证据或纠错而改变的指标／发现数量<br>Boundary / 边界：每次变更记录原因与新观察截止时间 |
<!-- handoff:metrics:end -->

Safety counts do not disappear inside a weighted health score. A confirmed unauthorized commit cannot be offset by many ordinary handoffs. Higher rejection or lower patch-adoption rates may indicate an effective gate; interpret alongside escapes, evidence quality and final outcomes. Thresholds depend on risk, role, sample size and approved service goals, not universal pass percentages. / 安全计数不能被健康均分抵消；一次确认越权不能由许多正常交接冲淡。拒绝更多或补丁采纳率更低可能说明闸门有效，须结合逃逸、证据质量及最终结果解释。阈值取决于风险职责样本量及批准的服务目标，不设通用通过率。

### Existing shared and legacy measurements / 既有共享与旧版度量

Keep [independent collaboration probes](../../collaboration-observability-probes.md) and registered `CSM04, CSM10–CSM11, CSM27` under their existing source definitions, denominators and executable scope. Shared profile `3.0.0` is separate from dedicated handoff source interface `1.0`. A matching name does not establish metric equivalence. / 独立协作探针及已注册指标按其原定义、分母和执行范围保留；共享配置 `3.0.0` 与交接来源接口 `1.0` 分开，同名不表示口径等价。

Retain earlier diagnostic names when analyzing their original datasets: `handoff_acceptance_rate` meant first-presentation acceptance, unlike HCM01's terminal candidate cohort; `context_package_completeness` checks done criteria, open risks and decisions; `downstream_surprise_rate` needs defects independently traced to known but omitted upstream risks. / 分析旧数据时保留原诊断名：原 `handoff_acceptance_rate` 指首次提交接收，不同于 HCM01 的终局候选队列；上下文包完整率检查完成标准、未决风险及取舍；下游意外率须独立追溯到上游已知却漏交的风险缺陷。

`handoff_dwell_time` starts at sender-ready, whereas HCM22 starts at submission. Acceptance-check duration, `reject_return_cycle` (rejection-to-representation), package assembly effort, boundary rework cost and avoided `context_reconstruction_cost` require their own timestamp/cost evidence; saved cost needs a defensible comparison baseline. / 原停留时间从发送方就绪开始，HCM22 从提交开始；验收检查耗时、拒收到再提周期、包组装投入、边界返工成本及免除的上下文重建成本各需时间费用证据，节省成本还需可辩护对照基线。

Keep `naked_handoff_count`, `orphaned_work_incidents`, boundary `repeat_rejection_count`, dropped-risk incidents, `handoff_ledger_completeness`, responsibility-ledger continuity and rejection-reason closure under explicit required populations. Map naked handoffs to `FAIL_0006`, ownership loss to `FAIL_0008`, escalation to `GOV_0001`, and durable ledger coverage to `GOV_0002`. Report detected omissions separately from execution's proven blocks. / 裸交接数、无主事件、边界重复拒收、风险丢失、交接账本完整率、责任账本连续性和拒收原因闭环率须有各自应有总体。保留状态丢失、责任不明、升级和入账的既有治理映射；检测缺失与执行已阻断分别报告。

<a id="exchange"></a>
## Shared Supplement Exchange / 共享补全交换

Use the exact [shared contract](../../handoff-chain-contract.md); this section supplies the independent probe's minimum semantics. A request binds `protocol_version`, `request_id`, the scope quartet, stage/candidate, `expected_version`, `expected_manifest_digest`, artifact digests, requested field paths, purpose, allowed sources, permission reference, deterministic-derivation allowance, rounds/cost budget and deadline. A patch binds immutable `patch_id`, request identity and identical scope/target, then per-field value, evidence status/references, source digest, observation/expiry times, method and rule version. / 精确协议以共享契约为准；请求绑定协议请求身份、四元作用域、阶段候选、预期版本清单摘要、工件摘要、字段用途来源授权、派生许可、轮数费用预算及截止时间。补丁以不可变身份绑定原请求及完全一致的作用域目标，逐字段给值、证据状态引用、来源摘要、观测有效期、方法及规则版本。

| Evidence state / 证据状态 | Permitted meaning / 允许含义 |
| --- | --- |
| Direct observation / 直接观测 | Verified original event, fixed artifact or authoritative query; execution still checks authority, freshness and applicability. / 经验证原事件固定工件或权威查询；执行仍须查权威范围、时效和适用性。 |
| Deterministic derivation / 确定性派生 | Reproducible result from trustworthy inputs and fixed algorithm; supports only that derived conclusion. / 可信输入固定算法可复算结果；仅支撑对应派生结论。 |
| Inference / 推断 | Hypothesis from patterns or incomplete evidence, kept separate from established facts. / 模式或不完整材料形成的假设，与确定事实分开。 |
| Unknown / 未知 | Missing, forbidden, unsupported, conflicting or insufficient evidence; cannot authorize release. / 缺失、无权限、不支持、冲突或不足；不能授权放行。 |

Supplement existing contract metadata, recover an original receipt, recompute a fixed historical artifact digest, derive a duration from comparable original timestamps, inspect authorized reference accessibility, or query the original external intent. Never treat planned metadata as an execution event, current content as historical content, accessibility as truth, or confidence as approval. / 可补既有契约元数据、找回原回执、复算固定历史工件摘要、用可比真实时间派生耗时、查授权引用可访问性或查原外部意图。不能把计划当执行、当前内容当历史、可访问当真实或置信度当批准。

The receiver validates request activity, authenticated scope/permission, exact stage/candidate, expected version, manifest/artifact digests, allowed fields, source authority, freshness and budget. An expired request or changed target yields rejection (including `stale_probe_patch` for stale binding); old patches may support historical audit only. A patch cannot expand the request's authority. / 接收端校验请求活动性、认证作用域权限、精确阶段候选、预期版本、清单工件摘要、字段白名单、来源权威、时效及预算。请求过期或目标改变即拒绝，绑定陈旧记录 `stale_probe_patch`；旧补丁仅能用于历史审计，不能扩张请求权限。

An immutable patch replay uses `(scope, request_id, patch_id)` as its unique key, with content digest bound to that key: identical content returns the original durable disposition even after restart, divergent content conflicts. Distinguish replaying a past receipt from adopting a distinct stale patch into the current head. Partial adoption requires explicit per-field disposition and leaves all rejected/unknown fields unresolved. / 不可变补丁以范围、请求标识、补丁标识为唯一键，内容摘要作为该键的绑定值；同内容即使重启后也返回原持久处置，异内容冲突。重放旧采纳回执与把另一个旧补丁用于当前头版本有别。部分采纳须逐字段明确结果，拒绝和未知字段仍未解决。

Adoption receipts include patch identity, processing time, per-field accepted/rejected result, reason and execution-side target version. A sent patch without that receipt remains pending and contributes no completed supplement. Observation-only append does not advance the baton; changed formal business evidence goes back to its authorized producer as a new candidate delta and through acceptance/commit. / 采纳回执含补丁身份、处理时间、逐项结果、原因及执行侧目标版本。无回执只算待确认，不计补齐。纯观测追加不推进接力棒；正式业务证据变更回到有权生产阶段生成新候选增量，重新验收提交。

Anchor retries to the original request and field set. Stop at maximum rounds, time, calls or cost; retain conflict provenance instead of majority-voting a fact. Probe telemetry must not recursively generate unbounded supplements. Probe outage permits declared noncritical telemetry degradation while execution retains its own audit, evidence and authorization gates. / 重试绑定原请求及原字段集合；达到轮数时间调用费用限额即停，保留冲突来源，不投票凑事实。探针遥测不得递归触发无界补全。探针停机只允许声明非关键遥测降级，执行须保留自身审计证据授权闸门。

For example, an editing candidate rejected at v2 may receive diagnostics locating a superseded claim and its valid replacement evidence. The editor changes actual content and submits a new candidate; only receiver acceptance and commit produce v3. The probe does not edit `verified_claims`, alter the rejected receipt or increment the head. / 例如 v2 编辑候选被拒后，探针可定位过期主张及有效替代证据；编辑修改实际内容并提交新候选，经接收验收提交才进入 v3。探针不直接改已核查事实、拒绝回执或头版本。

## Findings, Adaptation and Governance / 发现、适配与治理

| Priority / 优先级 | Probe finding / 探针发现 | Execution-owned response / 执行方处置 |
| --- | --- | --- |
| Critical / 严重 | Confirmed unauthorized commit, duplicate effect, substitution or unbacked advancement; return exact objects/evidence/impact. / 确认越权提交重复效果工件替换无依据推进，返回精确对象证据影响。 | Authorized pause, reconciliation or human escalation. / 按授权暂停、查证或转人工。 |
| High / 高 | Critical evidence gap, overdue unknown operation or uncertain owner; return gap, age and allowed sources. / 关键证据缺失、未知操作超时或责任不明，返回缺口年龄允许来源。 | Pause steps dependent on unknowns while retaining an accountable owner. / 暂停依赖未知的步骤并保留责任人。 |
| Medium / 中 | Falling first-pass, excessive valid-upstream reruns or growing seam wait; group by stage and reason. / 首过下降、有效上游大量重跑或接缝等待增加，按阶段原因分组。 | Review versioned contract/context/routing/budget changes before rollout. / 评审版本化契约上下文路由预算变更后启用。 |
| Low / 低 | Missing optional metrics, collection lag or patch redelivery. / 非关键指标缺失、采集滞后或补丁重投。 | Declared telemetry degradation without disabling business hard gates. / 声明遥测降级，保留业务硬闸。 |

Priority does not grant authority. Uncertain violations are high-risk unknowns, not confirmed incidents. Deduplicate alerts by exact target, rule and root cause while retaining first/last detection, count and disposition. The probe proposes versioned improvements; it never changes production contracts, permissions, routing or risk thresholds on its own. / 严重级别不授予权限；无法确定违规时报告高风险未知，不伪称事故。告警按精确目标规则根因合并，保留首次最近发现次数及处置。探针提出版本化改进，不自行改生产契约权限路由风险阈值。

Adapters may change sources, artifacts and business rules while preserving units, unknown handling and read-only boundaries: research/publication inspects claim/content/source versions; support escalation inspects ticket/owner/result; contracts inspect body/attachment/actor bindings; builds inspect artifact/environment/deployment proof; payments inspect batch/recipient/intent/receipt; long sessions inspect formal checkpoints, unresolved operations and current owner. Approval does not prove payment, pipeline completion does not prove deployment, and a progress summary does not prove acceptance. / 适配器可改变来源工件及业务规则，保留单位未知处理和只读边界：研究发布查主张内容来源版本，客服升级查工单责任结果，合同查正文附件主体，构建查制品环境部署证据，付款查批次对象意图回执，跨会话查正式检查点未决操作及责任。审批不证明付款，流水线结束不证明部署，进度摘要不证明验收。

Collect minimal authorized identifiers, hashes, times, rules and evidence references; mask sensitive content and enforce retention. Digests are not automatically anonymous. Use bounded metric labels such as stage/reason/risk/rule version; keep task/artifact/user identities in controlled traces. Required control and external-effect records cannot rely solely on sampling. Source documents and embedded prompts are data, not authority to read secrets, change policy or act externally. / 最小化采集授权身份摘要时间规则证据引用，脱敏并落实保留期限；摘要不自动匿名。指标标签使用阶段原因风险规则版本等有限值，任务工件用户身份保留在受控追踪。关键控制及外部效果权威记录不能仅采样。来源文档与内嵌提示是数据，不授权读凭据改策略或对外操作。

<a id="acceptance"></a>
## Source Probe Acceptance Cases / 来源探针验收用例

All cases below are pending integration specifications, not executed test results. Before deployment, a future adapter must preserve versioned fixtures/results and measure false positives, false negatives, loss recovery and probe overhead. Structural documentation checks do not mark these cases passed. / 以下均为待集成规格，不是已执行测试结果；上线前适配器须保留版本化样本结果，并验证误报漏报、丢失恢复及自身开销，结构文档检查不将用例标通过。

<!-- handoff:probe_cases:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HPT01 | No runtime data / 无任何运行数据 | Return static review and instrumentation gaps; runtime metrics remain uncomputable.<br>只给契约文档<br>静态审查与埋点缺口；运行指标不可计算 |
| HPT02 | Duplicate event / 重复事件 | Leave business counts unchanged while increasing duplicate-collection diagnostics.<br>同一事件重复导入<br>业务计数不变，自身重复采集计数增加 |
| HPT03 | Conflicting event identity / 事件身份冲突 | Raise an integrity finding when identical event identity has differing content; never silently choose one.<br>同一事件身份包含不同内容<br>完整性告警，不任选一份静默覆盖 |
| HPT04 | Out-of-order and late logs / 日志乱序与迟到 | Reconstruct by version and causality, including a rejection arriving after retry success; preserve report revision history.<br>拒绝事件晚于重试成功抵达<br>按版本和因果重建；报告带修订记录 |
| HPT05 | Missing official receipt / 缺失正式回执 | Acceptance opinion without commit proof leaves acceptance unknown and triggers read-only reconciliation.<br>有验收意见，没有提交证明<br>接收状态未知，触发只读查证 |
| HPT06 | Claimed authority without authentication / 伪造权威来源 | Reject log claims of approval as authority when authentication is absent and retain the evidence gap.<br>日志自称已审批，无认证凭据<br>不承认其权威性，保留证据缺口 |
| HPT07 | Forged digest / 摘要造假 | New digest with stale body fails content validation; inaccessible content leaves the result unknown.<br>新摘要字段配旧正文<br>内容检查失败；若不能读取正文则未知 |
| HPT08 | Concurrent head advance / 并发版本变化 | A stale attempt rejected after the head advanced does not imply that the global head should roll back.<br>旧尝试拒绝时头版本已前进<br>不误判应将全局头回退 |
| HPT09 | Remote success with local timeout / 外部成功、本地超时 | Recognize that the original intent needs receipt repair from authoritative success evidence; do not recommend re-execution.<br>有原意图和远端成功证明<br>识别需要补记回执，不建议重复执行 |
| HPT10 | Remote not-found with indexing delay / 远端未找到但存在索引延迟 | Retain unknown when the remote contract cannot confirm immediate non-execution; not-found is not retry evidence.<br>查询契约不支持立即确定未执行<br>保留未知，不准把未找到当成可重发证据 |
| HPT11 | Multiple receipt copies for one effect / 相同效果多个回执副本 | Do not increase duplicate-effect counts for repeated evidence of the same real remote effect.<br>同一远端效果重复出现<br>不增加重复业务效果数 |
| HPT12 | Stale observation patch / 过期观测补丁 | Recommend rejection when target version or artifact changed; never migrate old observations into current business fact.<br>目标工件或正式版本已变化<br>建议拒绝采纳；不得迁移成当前事实 |
| HPT13 | Partially visible data / 部分可见数据 | Report coverage, unknown objects and permission limits when only part of required artifacts is readable.<br>只能读取一部分必需工件<br>报告覆盖率、未知项与权限限制 |
| HPT14 | Incomparable clocks / 不可比较的时钟 | Return unknown latency or a supported interval estimate for cross-host skew; do not clamp negative latency to zero.<br>跨主机时间偏移产生负时延<br>时延未知或区间估计，不能截断成零 |
| HPT15 | Supplement budget exhausted / 补全预算耗尽 | Stop querying and report unresolved fields plus accountable owner.<br>继续查询才能填满字段<br>停止，输出未解决字段和责任人 |
| HPT16 | Historical serious violation discovered later / 旁路发现严重历史违规 | Distinguish violation and discovery timestamps; do not claim the probe prevented it beforehand.<br>违规早于告警时间<br>明确发现与违规时间，不声称事先阻断 |
| HPT17 | Execution rejects patch / 执行侧拒绝补丁 | Do not count repair as complete; record the authoritative rejection reason.<br>返回正式拒绝回执<br>不统计为已修复；记录拒绝原因 |
<!-- handoff:probe_cases:end -->

## Illustrative Offline Trace / 离线演示轨迹

The supplied teaching trace is narrative evidence only: research `v0→v1` accepted; verification `v1→v2` accepted; editing candidate 1 `v2→v2` rejected (`stale_claim_binding`); editing candidate 2 `v2→v3` accepted; publication `v3→v4` accepted. / 来源课程轨迹仅是叙述证据：研究接收、核查接收、编辑首候选旧绑定拒绝、编辑次候选接收、发布接收。

Only under the explicit illustrative assumptions of five distinct candidates, four logical stages, terminal settlements and “accepted” meaning durable commit: HCM01 = 4/5 = 80%, HCM02 = 3/4 = 75%, HCM03 = 4/4 = 100%, HCM04 = 5/4 = 1.25; the text reports one stale-binding rejection. These are teaching calculations, not measured production results. / 仅在明确演示假设下，即五份不同候选、四个逻辑阶段、均已结算且接收代表持久提交，才有上述四项 80%、75%、100%、1.25 倍及文本一次旧绑定拒绝；这些是教学计算，不是生产测量。

The trace cannot establish actual digest recomputation, semantic coverage, complete lineage, unseen stale-input escapes, valid authority, successful or duplicate remote publication, latency or cost. One observed interception does not establish an interception-rate denominator. Old context, missing title checks or self-reported hashes are hypotheses needing manifests, actual candidates, verification records and receipts. / 轨迹不能证明真实摘要复算、语义覆盖、来源完整、未观测逃逸、权限正确、远端发布成功或重复、时延及成本。一次拦截不确立拦截率分母；旧上下文、标题漏查或摘要自报只是待核假设，需要清单、真实候选、核验记录和回执。

<a id="output"></a>
## Independent Task and Output Templates / 独立任务与输出模板

Task instruction / 任务指令: Declare mode, materials, read authority, cutoff and limits; inspect contracts statically when no runtime evidence exists. Deduplicate event/candidate/stage/intent separately, reconstruct four chains, retain uncertainty, compute only supported numerators and denominators, and return bounded source-backed patches. Separate confirmed facts, hypotheses and suggested actions; await execution adoption receipts. / 声明模式材料读取权限截至点及限制；无运行证据时只静态审契约。分别去重事件候选阶段意图，重建四链，保留未知，仅算有证据分子分母，返回有界有来源补丁。区分确定事实、假设与建议动作，等待执行采纳回执。

```yaml
# Report template only; placeholders are not production values. / 仅报告模板，占位符不是生产值。
report_id: "<identity / 唯一身份>"
report_revision: 1
run_nature: static_review # actual_observation / teaching_example / test_fixture / 静态审查等
mode: offline # side_observation / bounded_supplement / 离线等
scope: {tenant_id: "<tenant>", workflow_id: "<workflow>", task_id: "<task>", chain_id: "<chain>"}
observation_cutoff: "<timestamp with timezone / 带时区时间>"
contract_policy_versions: []
source_inventory: [] # authorization, verification and reference / 授权核验引用
source_watermarks: []
data_quality:
  coverage: null
  duplicates: null
  conflicts: []
  missing_records: []
  clock_and_lateness_limits: []
reconstruction:
  last_verified_formal_version: null
  current_owner: null
  version_breaks: []
  unresolved_external_operations: []
findings:
  confirmed_facts: []
  confirmed_violations: []
  unknowns: []
  hypotheses: []
metrics:
  - metric_id: HCM02
    definition_version: "1.0"
    grain: stage_instance
    population_ref: null
    numerator: null
    denominator: null
    value: null
    calculability: not_calculable
    known_count: null
    unknown_count: null
    pending_count: null
    excluded_count: null
    coverage: null
    evidence_refs: []
    limitations: "No authoritative acceptance receipts. / 无权威接收回执。"
gaps: [] # field, affected checks, allowed source, owner, next action / 字段影响来源责任动作
patches_and_adoption_receipts: []
suggested_actions: []
probe_cost_and_limits: []
```

A probe run is complete when scope and evidence are explicit, every feasible promised check is accounted for, unknowns are explained and budget/permission termination is recorded; every gap need not be filled. A supplement is complete only under its declared evidence and adoption rules. Neither a closed alert nor a finished probe proves business repair; verify new formal receipts or actual external effects separately. / 探针完成条件是范围证据明确、可执行的已承诺检查有交代、未知有解释、预算权限终止有记录，并不要求填满缺口。补全完成须满足声明证据与采纳规则；告警关闭或探针结束均不证明业务修复，须另查新正式回执或真实外部效果。
