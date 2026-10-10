# Handoff Chain / 交接链

Cell / 交织点: collaboration-chain / 协作 x 链式

Capability / 能力: Collaboration / 协作

Mode / 模式: Chain / 链式

Identity / 稳定标识: `PATTERN_0043`, `CELL_COLLABORATION_CHAIN`

Source / 来源: Existing paper coordinate / 既有论文坐标: arXiv:2605.13850; dedicated engineering inputs / 专用工程输入: 《35_交接链_执行流程.md》与《35_交接链_工作流可观测性探针.md》, version / 版本 `0.1.0`.

Description / 描述: Transfer an accepted immutable version together with responsibility, evidence and an explicit recovery point. / 把已验收的不可变版本与责任、证据和明确恢复位置一起交给下一棒。

## Quick Navigation / 快速导航

- [Design and applicability / 设计与适用](#design)
- [Roles and state / 角色与状态](#roles)
- [Objects and contracts / 对象与契约](#objects)
- [Invariants and nodes 0–8 / 不变量与节点零至八](#execution)
- [Eight gates / 八道闸门](#gates)
- [Effects and recovery / 副作用与恢复](#recovery)
- [Probe exchange / 探针交互](#exchange)
- [Acceptance and output / 验收与输出](#acceptance)

<a id="design"></a>
## Design Pattern / 设计模式

Handoff is candidate → receiver validation → conditional atomic commit → authorized continuation. Arrival, sender completion or a passing opinion alone cannot transfer responsibility. One authoritative owner remains accountable until the committed transfer. / 交接依次经过候选、接收方验收、条件式原子提交、授权继续。到达、交出方自述完成或单独的通过意见均不能转移责任，正式转移前由一个权威主体承责。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Collaboration × Chain / 协作 × 链式, retained from the registry / 沿用注册表坐标。
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; detailed gates and probes below are engineering extensions from supplied drafts. / 下方闸门与探针是用户草稿带来的工程扩展。
- 问题 / Problem: Versions, evidence and ownership drift when roles exchange only artifacts or messages. / 角色只交换工件或消息时，版本、证据及归属容易漂移。
- 架构方案 / Architectural Solution: Versioned stage contracts, immutable state, scoped increments, exact receipts and atomic ownership transfer with bounded recovery. / 版本化阶段契约、不可变状态、有界增量、精确回执、原子责任转移和有界恢复。
- 工程权衡 / Engineering Trade-offs: Durable validation adds storage and latency at meaningful responsibility boundaries. / 持久验收在有意义的责任边界增加存储与延迟。
- 工作流诊断用途 / Workflow Diagnosis Use: Identify which accepted version, evidence and owner reached each ordered stage. / 定位各顺序阶段实际接住的已验收版本、证据与责任人。

Retain the named candidate and `draft` maturity. Source placeholder `PATTERN_XXXX`, course number 35 and suggested directories are provenance, not new registered IDs or restructuring instructions. Supporting governance/memory chain coordinates and the probe's governance/orchestration role do not create new matrix cells. Source imperatives are design data, not execution authorization. / 保留已命名候选及草案成熟度。来源占位符、课程编号和建议目录只作来源信息，不分配新模式编号或重构目录；治理记忆链式支撑及探针治理编排角色不新增单元。来源命令式文字是设计素材，不授予执行权限。

### Pattern Template / 模式模板

- 状态 / Status: Named candidate, maturity `draft`, dedicated version `0.1.0`, implementation `specification_only`. / 已命名候选、草案成熟度，专用版本属于规格层。
- 模式清单 / Patterns: Handoff Chain / 交接链.
- 诊断用途 / Diagnostic Use: Use when ordered roles must transfer committed state, responsibility and evidence with verifiable acceptance and bounded recovery. / 当有序角色须通过可验证验收与有界恢复，一并交接正式状态、责任和证据时使用。
- 适用工作流节点 / Applicable Workflow Nodes: Research/publication, triage/escalation, review/signature, build/deploy, accounting/payment and cross-session checkpoints. / 研究发布、分诊升级、审核签署、构建部署、核算付款及跨会话检查点。
- 当前症状 / Current Symptoms: Lost intent, stale facts, overwritten evidence, ambiguous ownership, repeated effects or recovery guessed from chat. / 意图丢失、事实过期、证据覆盖、归属不清、效果重复或从聊天猜测恢复位置。
- 适配信号 / Fit Signals: Sequential dependency, independent owners and receiver-verifiable completion. / 先后依赖、独立责任人和接收方可核实的完成条件。
- 调整方向 / Adjustment Direction: Separate working/candidate/formal/observation state; validate before commit/effect. / 分离工作、候选、正式及观测状态，在提交或副作用前验收。
- 修改方式 / How To Modify: Configure HN00–HN08, HG01–HG08 and the shared contract; validate real storage, authority and remote reconciliation. / 配置节点、八闸门及共享契约，验证真实存储、授权与远端查证。
- 输入 / Inputs: Goal/scope, ordered contracts, initial state, final acceptance, adapters, authority/risk policies, budgets and escalation owner. / 目标范围、阶段契约、初态、最终验收、适配器、权限风险、预算及升级责任。
- 输出 / Outputs: Artifact/version, receipt chain, responsibility ledger, confirmed/unknown effects, gaps and owned recovery checkpoint. / 工件版本、回执链、责任账本、确认或未知效果、缺口及有责任人的恢复点。
- 风险与治理 / Risks & Governance: `FAIL_0006` motivates state preservation; `FAIL_0008` motivates ownership/context separation; `GOV_0001` bounds recovery; `GOV_0002` preserves receipts. / 保留状态、明确归属及上下文边界、约束恢复、保存权威回执。

One actor doing sequential steps usually needs a prompt chain. Independent work can run in parallel before accepted aggregation; branching/revision may compose routing/loops. Concurrent writers require branches, ownership and merges. Add a stage only for meaningful responsibility, authority or acceptance value; one stage may contain many internal steps. / 同一主体顺序工作通常使用提示链；独立工作可并行后验收汇聚，分支修订可组合路由循环；并发写入须明确分支权属及合并。仅在有责任、权限或验收价值时增设一棒，一棒内部可有多个步骤。

## Shared Module Contract / 共享模块契约

The [shared collaboration procedure](../../collaboration-execution-flow.md) integrates handoff at `CE11`, source contract `2.0.0`, executable profile `3.0.0`. Its read-only reference validates exact acceptance and authenticated atomic-transfer attestations; the host performs and persists conditional owner/epoch updates. It does not supply the dedicated intent ledger, full semantic checks, durable handoff receiver or remote reconciliation below. / 通用协作规程在 CE11 接入交接，来源契约为 2.0.0、执行配置为 3.0.0。其只读参考核验精确验收及认证转移证明，宿主负责持久化责任代次条件更新；并不提供下方专用意图账本、完整语义检查、持久交接接收端或远端查证。

The [Handoff Chain Exchange Contract](../../handoff-chain-contract.md) is authoritative for identity, transport, observations and patch adoption. Protocol `1.0` is distinct from the common collaboration contract/profile; adapters must explicitly map fields and prove their guarantees. Neither this document nor documentation checks prove a deployed runtime. / 专用共享契约是身份、传输、观测及补丁采纳的权威规范；协议 1.0 与通用协作契约配置分开，适配器须显式映射并验证保证。本文及文档检查不证明运行时已部署。

<a id="roles"></a>
## Roles and State Boundaries / 角色与状态边界

| Role / 角色 | Authority and boundary / 权限与边界 |
| --- | --- |
| Executor / 执行者 | Reads authorized snapshots and submits allowed increments; cannot edit formal state or fabricate approval/acceptance/external success. / 读取授权快照并提交获准增量，不改正式状态或伪造批准签收外部成功。 |
| Receiver / 接收方 | Validates exact candidate; starts business only after confirmed commit and new authorization. / 验收精确候选，确认提交并取得新授权后才开始业务。 |
| State authority/orchestrator / 状态权威或编排器 | Checks contracts; atomically commits manifest/receipt/owner/epoch/outbox and issues bound grants. / 校验契约，原子提交清单回执责任代次通知并签发绑定授权。 |
| Authority service / 权限服务 | Authenticates actors/resources/approval validity/human owner; upstream permission is not inherited. / 核验主体资源审批时效及人工责任，上游权限不默认继承。 |
| External system / 外部系统 | Executes authorized intents and supplies real query/receipt evidence; local timeout cannot determine its result. / 执行授权意图并提供真实查询回执，本地超时不决定远端结果。 |
| Probe / 探针 | Reads/reconstructs/computes/proposes observations; cannot commit versions, transfer ownership or perform business effects. / 读取重建计算并提观测，不提交版本、转责或执行业务副作用。 |

Four state domains / 四类状态: working memory is disposable; submitted candidate state is immutable but unaccepted; formal state is committed and authoritative; observation state is an append-only side table with its own adoption receipts. Only formal state feeds downstream business execution. / 工作记忆可丢弃；候选提交后不可变但未接收；正式状态已提交且具权威；观测状态是追加旁表并有独立采纳回执。下游业务执行只消费正式状态。

`current_owner` is the formal owner, `assigned_executor` its authorized instance, and `proposed_receiver` only a candidate successor. Arrival, availability or lease expiry never transfers ownership. Takeover increases `control_epoch`; state storage and tool gateways/destinations must reject stale epochs. Local locking alone does not establish remote fencing. / 三字段分别表示正式责任人、授权执行实例及候选接收者；到达在线或租约到期不转责。接管提升控制权代次，状态库及网关目的端拒绝旧代次；本地锁不证明远端防旧写。

<a id="objects"></a>
## Objects and Stage Contracts / 对象与阶段契约

| Object / 对象 | Minimum contents and ownership / 最小内容及权属 |
| --- | --- |
| Stage contract / 阶段契约 | Versioned required/optional inputs/outputs, extension policy, field ownership, binding, receiver, permission, effects and failure policy; freeze per run and reject undeclared fields. / 版本化必需可选输入输出、扩展、权属绑定、接收权限、副作用失败策略；运行时固定，拒绝未声明字段。 |
| Fact / 事实 | `fact_id`, `fact_version`, `value` or `value_ref`, authenticated producer/stage, versioned `evidence_refs`, creation/validity/scope and `supersedes`; append successors, never overwrite verified facts. / 保存标识版本、值或引用、认证生产者阶段、版本证据、创建有效范围及替代关系，追加后继不覆盖核查事实。 |
| Artifact / 工件 | Immutable ID/version/content reference/digest and consumed fact manifest; references resolvable under authorization. / 不可变标识版本内容引用摘要及所用事实清单，授权下可展开。 |
| Baton / 接力棒 | Scope, formal version, parent/current manifest digests, contract, accepted facts/artifacts, owner/epoch, last receipt and open issues. / 范围、正式版本、父当前摘要、契约、已接收事实工件、责任代次、最近回执及未决项。 |
| Candidate package / 候选包 | Scope/stage/attempt/handoff, expected input version/digest, sender/receiver/epoch, consumed refs, allowed delta, evidence/permission/deadline/recovery; edits create new `handoff_id`. / 范围阶段尝试交接、预期输入版本摘要、双方代次、所用引用、获准增量、证据权限期限恢复点；改动即新交接标识。 |
| Receipt / 回执 | Immutable `receipt_id`, handoff/scope/stage, input/output versions, observed head, verdict/reason, authenticated acceptor, artifact/rule bindings, owner transition and time; rejection also appends history. / 不可变回执、交接范围阶段、输入输出版本、观察头、结论原因、认证验收者、工件规则绑定、责任变化及时间；拒绝也追加历史。 |

Candidate output, acceptance opinion, formal commit receipt and external business receipt are distinct facts. A rejected `v2→v2` attempt creates no successor: use `output_version: null` for no commit. If the global head is already v3, separately record `observed_head_version: 3`; never roll shared state back. / 候选、接收意见、正式提交及外部业务回执分别记录。拒绝的 v2→v2 不建后继，输出版本为空表示未提交；全局头若为 v3 则另记观察头版本，绝不倒退共享状态。

An editing contract may require `verified_claims`, `verified_claim_set_digest`; allow only `draft_artifact_ref`, `draft_artifact_digest`, `consumed_claim_refs`, `semantic_review_ref`; forbid `verified_claims`, `approval_status`, `publication_status` writes. Explicit optional fields are legal. Ownership comes from trusted contracts/identity services, never executor claims. / 编辑契约可要求已核查主张及集合摘要，只准写稿件引用摘要、所用主张与语义核验引用，禁改事实批准发布状态；显式可选字段合法，权属由可信契约身份服务确定。

Two checks are mandatory: independently recompute the complete actual-content digest with fixed algorithm/encoding/canonicalization, then verify claims against valid facts, including title, summary, tables, units, objects, validity and qualifiers. Bind semantic review to artifact digest, fact-set digest and rule version. Self-reported `draft_claim_digest == verified_claim_digest` is insufficient; hashes prove neither truth nor source identity. Model judgement is evidence; insufficient evidence stays unknown. / 两层检查缺一不可：固定算法编码规范独立重算实际完整内容摘要，再核对有效事实及标题摘要表格、单位对象时效限定；语义核验绑定工件事实集合和规则。自报摘要相等不足以验收，哈希不证明事实或来源真实；模型判断只是证据，缺证保持未知。

Revocations append records and invalidate affected dependencies for revalidation, without rewriting old snapshots. Deprecated claims stay outside current facts. Changed bytes, facts or approvals require fresh validation of coverage. / 撤销追加记录并使受影响依赖重验，不改旧快照；废弃主张与当前事实隔离，字节事实审批变化须重新判断覆盖有效性。

<a id="execution"></a>
## Execution Invariants and Workflow / 执行不变量与流程

Initialize goal/scope/stages/contracts, final acceptance, adapters, risk policy and human owner. Configure attempts, supplement rounds, cost/deadline, evidence/approval/call expiry, idempotency retention, cancellation and human-response limits. Example retry counts are not universal thresholds. Without real adapters, report static review or simulation. / 初始化目标范围阶段契约、最终验收、适配器风险人工责任；配置尝试补全次数、成本期限、证据审批调用时效、幂等保留及取消人工响应边界。示例重试次数非普适阈值，无真实适配器只报告静态审查或演练。

<!-- handoff:invariants:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HI01 | Committed input only / 执一 | Only committed versions may become downstream business input; quarantine provisional state and stop invalid consumption.<br>只有已提交版本能成为后续业务输入<br>隔离候选状态，暂停错误消费 |
| HI02 | Current authorized base / 执二 | A new commit must match the permitted official input version and manifest; reject stale commits and reload state.<br>新提交的输入版本和摘要必须匹配允许使用的正式头状态<br>拒绝过期提交；重新获取快照 |
| HI03 | Single successor per handoff / 执三 | One newly accepted candidate creates exactly one successor; rejection and duplicate delivery never advance the version.<br>一次新接收只创建一个后继版本；拒绝和重复投递不推进版本<br>报告提交一致性故障 |
| HI04 | Scope and epoch agreement / 执四 | Task, security domain, receiver and control epoch must agree; reject cross-domain, unauthorized or late execution.<br>任务、安全域、接收者和控制权代次必须同时匹配<br>拒绝越域、越权或迟到执行 |
| HI05 | Owned output fields / 执五 | A stage may submit only fields it is authorized to produce; reject ownership violations.<br>阶段只提交自己有权生产的字段<br>返回字段所有权违规 |
| HI06 | Actual-content evidence binding / 执六 | Artifacts, facts, approvals and semantic reviews must bind real versions and content; reject stale approval, false binding or semantic conflict.<br>工件、事实、审批与语义核验绑定实际版本和内容<br>拒绝旧审批、假绑定或内容冲突 |
| HI07 | Acceptance plus commit transfers ownership / 执七 | Transfer responsibility only after receiver acceptance and controlled commit; retain the original or predesignated custodian until then.<br>接收方验收与受控提交完成后才转移责任<br>原责任人或预设托管责任人继续负责 |
| HI08 | Pre-effect authorization / 执八 | External effects require pre-operation acceptance and authorization; never publish first and check afterward.<br>外部副作用必须先经过操作前验收和授权<br>禁止“先发布再验收” |
| HI09 | Unknown is not unexecuted / 执九 | Unknown outcome does not authorize a new operation key or replay; reconcile before recording, retrying, compensating or escalating.<br>结果未知不等于未执行；不可自动生成新业务键重发<br>先查证、再补记／重试／补偿／转人工 |
| HI10 | Evidence-bound probe adoption / 执十 | Probe supplements need provenance, target version and adoption receipt; reject unauthenticated or stale patches.<br>探针补全有来源、有目标版本、有采纳回执<br>拒绝无来源或过期补丁 |
| HI11 | Bounded recoverable failures / 执十一 | Every failure has a recovery point, retry limit, deadline and owner; escalate or terminate with evidence instead of looping forever.<br>每条失败路径有恢复点、次数限制、截止时间和责任人<br>升级或有证据地终止，不无限循环 |
| HI12 | Verified final completion / 执十二 | Final completion requires artifact acceptance and confirmation of required external effects; otherwise report partial or pending status.<br>最终完成要求工件验收与必要外部效果均已确认<br>输出部分完成或待确认，不虚报成功 |
<!-- handoff:invariants:end -->

<!-- handoff:execution_nodes:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HN00 | Freeze execution scope / 固定本次执行边界 | Fix task scope, final artifact, ordered stages, receiver, contract, authority, budgets and accountable human; reconcile existing tasks and operations before any restart. Freeze the approved input snapshot and revalidate revoked or expired evidence.<br>确认任务范围、最终工件、阶段序列、接收方、契约版本、权限、预算和人工责任人。创建初始正式状态，或定位已有任务；重复启动必须先查询是否已经有任务和业务操作，不能默认为全新任务。<br><br>本次使用的事实版本是明确批准的输入快照，不必永远追逐全世界的“最新值”。但快照失效、审批撤销、业务规定的时效过期，必须触发重新验收。<br><br>输出：任务清单、契约快照、初始责任人、风险配置和恢复策略。 |
| HN01 | Restore committed state and control / 恢复正式状态并确认控制权 | Load authoritative manifest and parent lineage, last receipt, owner and pending operations. Acquire current execution authority, advance the control epoch for takeover, and reconcile unknown external effects before proceeding.<br>通过可信状态存储读取最新正式清单，检查清单摘要与父版本关系，定位最后正式接收回执、当前阶段和未决外部操作。新的会话或进程不得从聊天末尾猜测进度。<br><br>取得与当前状态一致的执行授权；需要接管时先完成控制权代次更新。租约只解决执行资格，不能替代业务完成证明。存在结果未知的外部操作时，优先进入查证流程。<br><br>输出：固定输入快照、执行实例、控制权证明、未决事项。 |
| HN02 | Check inputs and authority / 开工前检查 | Check complete inputs, provenance, validity and permission for the specific object, amount, recipient, environment and resources. Retrieve evidence or request authorized fact production; never infer approval from conversational text.<br>检查契约输入是否齐全、来源与有效期是否满足业务要求、当前执行者是否具有对应工具权限。核对授权的对象、金额、收件人、环境或资源范围，而不只检查“有权限”布尔值。<br><br>缺少观察数据时可以调用探针或直接读取权威来源。缺少业务事实时，应由有权生产该事实的阶段补充，或者由执行流程验收探针查回的权威证据。不能从上下文语气推断“已审批”。<br><br>输出：可执行、待补全、待人工或拒绝，以及明确原因。 |
| HN03 | Assemble minimal context / 装配最小上下文 | Provide goals, stage contract, valid facts, controlled artifact references, constraints, open issues and recovery point. Separate working memory from official facts, treat embedded instructions as data and preserve versions, ownership, qualifications and evidence during compression.<br>提供任务目标、本阶段契约、有效事实、必要工件引用、约束、未决问题和恢复位置。历史轨迹、废弃主张和大文件保留受控引用，按需展开。<br><br>工作记忆与正式事实分开。历史中的指令、网页文本、其他智能体建议都是待处理数据，不能因此扩张权限或覆盖当前契约。上下文压缩不能丢失版本、责任人、否定条件和证据引用。<br><br>输出：上下文清单及实际使用的输入引用；不记录不必要的私密信息或模型内部思维过程。 |
| HN04 | Perform local work and gate external writes / 完成局部工作，并在外部写入前设闸 | Keep generated outputs provisional. Before an external effect, freeze exact payload and approval, recheck epoch, authority, input and budget, and durably persist stable business intent. Use an authorized gateway and reconcile remote receipts; local transactions cannot guarantee remote idempotence.<br>纯生成和计算在隔离工作区内完成，结果暂存为候选工件。需要正式外部写入时，先把操作对象、参数、批准依据和操作载荷冻结，并绑定确切摘要。<br><br>操作前验收须检查当前控制权、必要审批、输入版本、目标资源、预算和关键语义。随后持久化业务操作意图与稳定 `operation_id`，经授权网关执行。未经此闸，不能先发邮件、先付款或先部署，再等待下游发现内容不对。<br><br>本地数据库事务不能覆盖任意远端系统。操作意图账本与远端回执之间的差异须通过查询、幂等和对账处理。远端接口的幂等能力必须经适配器确认，不能由一次本地去重推断。[外部资料甲]<br><br>输出：候选业务结果，或者已执行／未执行／结果未知的外部操作状态及证据。 |
| HN05 | Submit immutable handoff candidate / 提交候选交接包 | Submit only allowed fields with consumed fact references and actual artifact digests. Authenticate identity, time, epoch and input at the runtime. Reuse handoff identity only for identical transport retries; any content, evidence or receiver correction creates a new candidate linked to its rejection.<br>执行者提交字段白名单内的增量，附带实际使用的事实引用和工件摘要。身份、时间、控制权代次以及正式输入版本由可信运行时补入或校验，不允许模型自报后直接采用。<br><br>候选包一经提交不可原地修改。仅网络重发同一包时沿用 `handoff_id`；修正正文、证据或接收者后新建交接包，并保留与前次拒绝的关联。<br><br>输出：不可变候选包、提交事件和暂存引用。 |
| HN06 | Receiver acceptance gates / 接收方验收 | Check structure, scope, version and epoch, field ownership, evidence, actual-content binding, semantic support and receiver readiness. Bind every verdict to the same candidate, input and rules. Preserve pass, reject, unknown and justified not-applicable; recheck conditions changed before commit.<br>&#124; 闸门 &#124; 检查内容 &#124; 失败结果 &#124;<br>&#124;---&#124;---&#124;---&#124;<br>&#124; 结构闸 &#124; 必填、类型、允许字段、协议与契约版本 &#124; 结构拒绝 &#124;<br>&#124; 对象闸 &#124; 安全域、任务、阶段实例、接收者、资源范围 &#124; 对象或接收者不匹配 &#124;<br>&#124; 版本闸 &#124; 输入版本、输入摘要、当前允许快照及控制权代次 &#124; 过期输入或失效控制权 &#124;<br>&#124; 所有权闸 &#124; 生产者身份、字段写入范围、事实替代权限 &#124; 越权写入 &#124;<br>&#124; 证据闸 &#124; 来源身份、可展开性、真实性检查、有效期与适用范围 &#124; 证据缺失、失效或不支持 &#124;<br>&#124; 绑定闸 &#124; 实际内容摘要、所用事实与审批覆盖的版本 &#124; `stale_claim_binding` 等绑定错误 &#124;<br>&#124; 内容闸 &#124; 标题、正文、表格、关键主张和约束是否一致 &#124; 语义冲突或未知 &#124;<br>&#124; 接收闸 &#124; 接收主体可承接，下一棒前置条件成立，签收对象明确 &#124; 暂缓接收或转人工 &#124;<br><br>验收意见至少有“通过、拒绝、未知、不适用”四种状态。不适用需要契约依据。关键条件未知时按风险策略暂停，不得用“未发现错误”替代已通过。<br><br>所有验收结果均绑定同一候选工件、输入快照和规则版本。检查完成至提交之间如状态变化，必须重新检查相关条件，不能使用过期的验收票。 |
| HN07 | Conditionally commit atomically / 受控原子提交 | The sole state authority compares input version, manifest, owner and epoch, then atomically persists next manifest, official receipt, ownership and notification outbox. Query official commit and execution authority before downstream work. Duplicate identical handoffs return their receipt; identity conflicts or unavailable audit durability block commit.<br>接收意见通过后，由唯一状态权威完成条件式提交：预期输入版本、清单摘要、当前责任人和控制权代次仍须匹配。在同一个本地原子边界中，持久化下一版清单、正式阶段回执、责任归属变化，以及待发送通知记录。<br><br>数据库内可使用条件更新和唯一约束；其他存储须提供等价的并发和持久化语义。先写入不可变大工件、再提交其引用时，失败遗留的孤立工件应由生命周期策略清理，不能把它们当作已接收输出。<br><br>多系统之间不能假设共享同一事务。可先取得绑定候选包的持久接收意见，再由唯一协调权威提交并通知。接收方必须能查询正式提交结果，且只能在查询到有效提交及执行授权后启动下一棒。通知丢失可重发，但不得产生第二次责任转移。<br><br>同一 `handoff_id` 的重复请求返回原回执；同一标识对应不同内容属于完整性冲突。失败时保留原正式状态，写拒绝原因。若正式审计账本无法持久化，禁止假装已经提交。 |
| HN08 | Transfer control and finish or continue / 转移控制权，继续或结束 | Issue execution authority bound to the committed successor and revoke the old executor's write eligibility. Obtain final business acceptance; distinguish complete, partial, pending reconciliation, human review, cancellation and failure. Report artifacts, versions, acceptance chain, effect evidence, owner and recovery point.<br>提交成功后，下一棒获得绑定新版本的执行授权。旧执行者仍可承担交接问题的解释与修复责任，但不得继续持有该阶段的正式写入资格。<br><br>终点由业务指定接收服务或人工责任人签收。最终状态须区分完成、部分完成、待查证、待人工、取消和失败；只有全部最终条件满足才标记完成。<br><br>输出：最终工件、最终版本、完整接收链、外部结果证明、未决事项、责任人和恢复位置。 |
<!-- handoff:execution_nodes:end -->

HN07 uses CAS or equivalent serialization over `(scope, expected_version, expected_manifest_digest, current_owner, control_epoch)` and current acceptance/authority validity. Durable uniqueness of `(scope, handoff_id)` binds one package digest to its original result across restarts. Exact replay returns the original receipt without work or another transfer. Distinct stale candidates reload and revalidate, never overwrite the head. / HN07 对范围、预期版本摘要、责任代次及当前验收授权有效性做 CAS 或等价串行化。范围与交接标识持久唯一绑定包摘要和原结果，跨重启有效；重复返回原回执不重做或再转责，新的陈旧候选重载复验不覆盖头。

Atomicity is local to one authority, not arbitrary remote systems. Persist bound receiver opinion before coordination, then commit manifest, audit receipt, owner/epoch and outbox in one transaction. Missing base-audit persistence blocks commit and protected external writes. Prewritten immutable blobs orphaned on failure are not accepted outputs. Receivers query commits before starting even when notices repeat or disappear. Old executors may explain/repair under new scoped authorization, without retaining old control. / 原子性限于一个状态权威，不覆盖任意远端；协调前持久接收意见，再同事务提交清单审计回执责任代次及通知。基础审计不可持久化时阻止提交和受保护写入；预写孤儿工件不是接收成果。通知重发或丢失时接收方仍先查提交，旧执行者可新授权解释修复但不保留旧控制权。

<a id="gates"></a>
## Eight Acceptance Gates / 八道验收闸门

<!-- handoff:gates:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HG01 | Structure gate / 结构闸 | Validate required fields, types, allowed output fields and protocol/contract versions; reject malformed packages.<br>必填、类型、允许字段、协议与契约版本<br>结构拒绝 |
| HG02 | Object and scope gate / 对象闸 | Authenticate security domain, task, stage instance, receiver and resource scope; reject mismatched objects or receivers.<br>安全域、任务、阶段实例、接收者、资源范围<br>对象或接收者不匹配 |
| HG03 | Version and epoch gate / 版本闸 | Match input version and manifest to the allowed snapshot and current control epoch; reject stale input or expired authority.<br>输入版本、输入摘要、当前允许快照及控制权代次<br>过期输入或失效控制权 |
| HG04 | Field ownership gate / 所有权闸 | Verify producer identity, writable fields and fact-supersession authority; reject unauthorized writes.<br>生产者身份、字段写入范围、事实替代权限<br>越权写入 |
| HG05 | Evidence gate / 证据闸 | Verify source identity, retrievability, authenticity, validity and applicability; missing, stale or unsupported evidence blocks acceptance.<br>来源身份、可展开性、真实性检查、有效期与适用范围<br>证据缺失、失效或不支持 |
| HG06 | Actual artifact binding gate / 绑定闸 | Check actual content digest, consumed facts and approval coverage for the exact version; reject stale or false binding.<br>实际内容摘要、所用事实与审批覆盖的版本<br>`stale_claim_binding` 等绑定错误 |
| HG07 | Semantic content gate / 内容闸 | Check title, body, tables, critical claims and qualifications for consistency; preserve semantic conflicts or unknown results.<br>标题、正文、表格、关键主张和约束是否一致<br>语义冲突或未知 |
| HG08 | Receiver readiness gate / 接收闸 | Confirm an authorized receiver can assume responsibility and the next stage's prerequisites hold; otherwise defer or escalate.<br>接收主体可承接，下一棒前置条件成立，签收对象明确<br>暂缓接收或转人工 |
<!-- handoff:gates:end -->

Each gate returns `passed`, `rejected`, `unknown` or `not_applicable`; inapplicability needs a versioned contract reason. Critical unknown does not pass. Opinions bind candidate digest, input manifest, policy/rules and expiry; relevant changes before commit require revalidation. Acceptance never substitutes for separately required action authorization. / 各闸返回通过、拒绝、未知或不适用，不适用须版本化契约理由；关键未知不通过。意见绑定候选摘要、输入清单、策略规则及有效期，提交前相关变化须复验；验收不能替代动作授权。

<a id="recovery"></a>
## External Effects and Local Recovery / 外部效果与局部恢复

```text
unplanned / 未计划 → prepared / 已准备 → sent / 已发送
  → confirmed_success / 已成功 → record receipt / 记回执
  → confirmed_no_effect / 已确认未执行 → authorized retry or stop / 授权重试或停止
  → unknown / 结果未知 → reconciling / 查证中
      → confirmed_success / 已成功 → recover receipt, do not repeat / 补记不重复
      → confirmed_no_effect / 未执行已确认 → same-intent controlled retry / 同意图受控重试
      → unknown / 仍未知 → wait or human owner / 等待或转人工
```

Keep `operation_id`, original payload digest and destination stable across attempts/restarts/baton versions; retain historical authorization and result evidence without overwriting it. Revalidate current authorization before retry, and append reconciliation evidence to resolve unknown results. Same key/different payload conflicts; identical parameters alone do not establish identical intent. Changed intent requires fresh authorization after resolving pending old intent. Verify destination idempotency/retention; local deduplication never proves exactly-once effects. / 跨尝试重启接力棒版本保持操作标识、原载荷摘要及目的端，保留历史授权与结果证据而不覆盖。重试前核验当前授权，以追加查证记录解决未知结果。同键异载荷冲突，相同参数不证明同意图；改变意图先处理旧未决并获新授权，核验目的端幂等保留，本地去重不证明严格一次效果。

Timeout, missing receipt or “not found” does not prove non-execution unless remote consistency/retention warrants it. Unknown outside the safe replay window stays unknown pending reconciliation/escalation. Confirmed failure with possible partial effects also needs reconciliation. Compensation is a new authorized operation with its own ID/results, never deletion of history; rejecting a handoff does not erase remote effects. / 超时缺回执或未找到均不证明未执行，除非远端一致性保留契约支持；安全重放窗口外未知仍须查证升级，失败若可能有部分效果也先核对。补偿是有自己标识结果的新授权操作，不删除历史；拒绝交接不抹除远端效果。

<!-- handoff:recovery:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HR01 | Missing input / `missing_input` | Resume from the last official stage input, retrieve authoritative data or return upstream; never fabricate required facts.<br>当前阶段的最后正式输入<br>从权威来源补齐或返回上游<br>编造必填事实 |
| HR02 | Stale fact binding / `stale_claim_binding` | Resume from the allowed fact version and revise actual content plus bindings in a new candidate; changing only digest fields is forbidden.<br>当前允许使用的事实版本<br>修正实际内容和绑定，提交新候选包<br>只修改摘要字段 |
| HR03 | Semantic conflict / `semantic_conflict` | Revise the failed stage under the same valid input using precise conflict locations and independent review when needed; do not retry indefinitely without changing conditions.<br>相同输入快照下的失败阶段<br>针对冲突位置修订；必要时独立复核<br>不改条件地无限重试 |
| HR04 | Version conflict / `version_conflict` | Reload the official head, recompute affected outputs and recheck authority; never roll back the global head.<br>重新读取的正式头版本<br>重算受影响输出、复核授权<br>将全局头指针回退 |
| HR05 | Field ownership violation / `field_ownership_violation` | Return the field to its authorized producer; do not widen model permissions to bypass ownership.<br>当前阶段<br>交回有权生产字段的主体<br>提升模型角色权限绕过 |
| HR06 | Authorization denied / `authorization_denied` | Resume at authority confirmation, obtain explicit authorization or escalate; never automatically expand permissions.<br>权限确认节点<br>申请明确授权或转人工<br>自动扩大权限后重试 |
| HR07 | Receiver unavailable / `receiver_unavailable` | The original owner retains official state; resend the identical package or use an approved substitute, without equating delivery to acceptance.<br>原责任人持有的正式状态<br>重发相同包、选择已批准替代者<br>发送成功即视为接收 |
| HR08 | Receipt unknown / `receipt_unknown` | Query the authoritative ledger by original handoff or operation identity and restore its receipt; do not create a new business operation.<br>交接或操作身份对应的账本记录<br>查询已提交回执并恢复本地记录<br>直接新建业务操作 |
| HR09 | External status unknown / `external_status_unknown` | Reconcile the pending operation through authoritative remote state, accounting or human review; never infer failure and repeat the effect.<br>未决外部操作<br>查询远端真实状态、对账、人工处理<br>假定失败后重复执行 |
| HR10 | Evidence revoked / `evidence_revoked` | Resume at the earliest affected fact-production or verification stage; invalidate dependencies and recheck locally, without reusing revoked approvals.<br>最早受影响的事实生产或核验阶段<br>标记依赖失效，局部重核<br>重用撤销前的审批 |
| HR11 | Budget exhausted / `budget_exhausted` | Stop at the last official checkpoint, report partial completion and escalate; never extend budgets indefinitely.<br>最后正式检查点<br>输出部分完成并升级<br>无限追加预算 |
| HR12 | Cancelled / `cancelled` | Revoke future execution eligibility at the confirmed cancellation boundary and reconcile in-flight operations; cancellation does not erase remote effects.<br>已确认取消边界<br>撤销未来执行资格，查清在途操作<br>假定取消已抹除远端效果 |
<!-- handoff:recovery:end -->

Each failure records resume stage/version, attempts/cost remaining, deadline and owner. Upstream work is reusable only while its evidence and authority remain valid; revocation or changed intent may expand recovery. No infinite loops or silent ownership gaps. / 每条失败记录恢复阶段版本、剩余次数成本、期限及责任；上游仅在证据授权有效时复用，撤销或意图变化可扩大范围，不无限循环或无人承责。

<a id="exchange"></a>
## Probe Exchange / 探针交互

Use the [authoritative shared contract](../../handoff-chain-contract.md) for events, bounded requests, patches and adoption receipts. Execution runs independently with source retrieval and durable audit; probes independently observe online or reconstruct offline; bounded interaction is optional. / 事件有界请求补丁及采纳回执按权威共享契约；执行可独立取证审计，探针可独立在线旁路或离线重建，有界交互可选。

Pure observation appends to a side table without advancing the baton. Formal evidence promotion requires an authorized producer, new evidence delta, business gates and commit. A v2 patch arriving after v3 is `stale_probe_patch`, rejected for current use but may remain historical evidence. Probe outage degrades optional telemetry only; critical evidence must be recovered or dependent work paused. Offline discovery records discovery time, never claims a historical block. / 纯观测追加旁表不推进接力棒；正式证据晋升须有权主体新证据增量并过业务闸门提交。v3 后到达的 v2 补丁当前拒收，可留历史；探针停机仅降级可选遥测，关键证据须取得或暂停；离线发现记录发现时间，不声称当时拦截。

<a id="acceptance"></a>
## Acceptance and Output / 验收与输出

All scenarios below are `pending`, not passed runtime tests. Documentation checks prove source coverage/view consistency only. Validate against actual storage, authenticated gateways and external adapters before claiming deployment guarantees. / 以下场景均待实施，不是已通过运行时测试；文档检查只证明来源覆盖视图一致，部署保证须在真实存储认证网关及外部适配器验证。

<!-- handoff:execution_cases:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HET01 | Normal four-stage handoff / 正常四棒交接 | Official versions advance in order and acceptance binds the authenticated receiver and artifact.<br>正式版本有序前进，接收人与工件绑定 |
| HET02 | Missing or forbidden fields and forged producer / 少字段、非法字段、伪造生产者 | Reject before commit, leaving official state and responsibility unchanged.<br>在提交前拒绝，责任与正式状态不变 |
| HET03 | Stale facts or approvals and changed artifact / 旧事实、旧审批、修改过的工件 | Reject at version or content acceptance and identify the conflicting object.<br>版本或内容验收拒绝，并给出冲突对象 |
| HET04 | Failed acceptance, lost notification and duplicate delivery / 接收失败、通知丢失、重复投递 | Preserve accountable ownership and prevent duplicate commits.<br>无静默责任丢失、无重复提交 |
| HET05 | Concurrent commit, expired lease and late old executor / 并发提交、失效租约、旧执行者晚到 | State authority and the tool boundary reject expired execution eligibility.<br>状态权威和工具边界拒绝过期资格 |
| HET06 | Remote success with local timeout / 外部成功但本地超时 | Query the original operation, restore its receipt and create no additional effect.<br>先查询，再补记，不产生额外副作用 |
| HET07 | Same business key with changed payload or expired deduplication / 同业务键不同载荷、幂等记录过期 | Reject conflicting parameters or escalate for reconciliation; never replay blindly.<br>参数冲突或查证升级，不盲目重发 |
| HET08 | Revoked upstream fact / 上游事实撤销 | Invalidate affected dependencies and require renewed acceptance.<br>受影响依赖被标记并重新验收 |
| HET09 | Probe disabled / 探针关闭 | Execution's baseline audit and hard gates remain effective independently.<br>执行流程基础闸门仍有效 |
| HET10 | Unproven, unauthorized or stale probe patch / 探针返回无来源、越权或过期补丁 | Reject adoption and retain the rejection receipt.<br>拒绝采纳，并保留拒绝回执 |
| HET11 | Historical violation discovered offline / 探针离线发现历史违规 | Distinguish violation time from discovery time; do not claim earlier prevention.<br>报告违规与发现时间，不声称当时已阻断 |
| HET12 | Audit failure and cancellation racing in-flight operations / 审计存储故障、取消与在途操作并发 | Do not fabricate a commit; keep an accountable owner reconciling in-flight effects.<br>禁止虚假提交；在途状态有人负责查证 |
<!-- handoff:execution_cases:end -->

Illustrative source trace: research `v0→v1`, verification `v1→v2`, rejected editing `v2→v2` (`stale_claim_binding`), repaired editing `v2→v3`, publication `v3→v4`. It illustrates local recovery, not a course run performed here or proof of deployed authority, semantics, atomicity or external confirmation. / 来源示例研究核查编辑拒绝修复发布轨迹说明局部恢复，不代表本次运行课程或证明权限语义原子性外部确认已部署。

<!-- handoff:variants:start -->
| ID / 编号 | Item / 条目 | Definition and evidence / 定义与证据 |
| --- | --- | --- |
| HEV01 | Correct digest with incorrect body / 正文仍错误，但复制正确事实摘要字段 | Reject through the content gate; equality of self-reported digest fields cannot prove the actual body is correct.<br>内容闸拒绝，不能只看字段相等 |
| HEV02 | Correct body with exaggerated title / 正文正确，标题夸大已核查事实 | Include the title in semantic verification and reject or revise unsupported claims.<br>标题纳入内容闸，拒绝或修订 |
| HEV03 | Successful commit with lost sender receipt / 第一次提交已成功，但发送方没收到回执 | Query or resend the same handoff identity and return the original receipt; never create another version.<br>相同交接身份查询／重发返回原回执，不新建版本 |
| HEV04 | Concurrent candidates from version two / 两个执行者都基于 v2 提交 | Accept only the candidate that still meets authoritative state and control-epoch conditions.<br>只有满足当前状态与控制权的提交被接受 |
| HEV05 | Publication succeeded but receipt timed out / 发布已完成但回执超时 | Record unknown outcome and query the original publishing intent; do not publish again.<br>记录结果未知，查询原发布意图；不得重复发布 |
| HEV06 | Version-two patch arrives at version three / 探针对 v2 的补丁在状态变为 v3 后返回 | Reject current adoption while preserving the patch for historical version-two audit.<br>当前采纳拒绝，保留旧版本审计用途 |
<!-- handoff:variants:end -->

Adapters change contracts, evidence authority, permissions, artifacts, final conditions and recovery policy, preserving candidate → validation → commit → transfer. Research binds claims/title/body; triage binds case/object/escalation scope; contracts bind text/attachments/signers; deployment binds bytes/environment; payment binds payee/amount/currency/intent; long tasks bind checkpoint/owner/pending effects. / 场景适配替换契约证据权威权限工件最终条件恢复策略，保持候选验收提交转责。研究绑定主张标题正文；分诊绑定对象个案升级范围；合同绑定正文附件签署者；部署绑定字节环境；付款绑定收款方金额币种意图；长任务绑定检查点责任未决效果。

```yaml
execution_kind: static_review # real_run | static_review | simulation / 真实运行、静态审查、演练
scope: {} # tenant/workflow/task/chain / 安全域、工作流、任务、交接链
status: awaiting_supplement # completed | partial | awaiting_supplement | awaiting_verification | awaiting_human | cancelled | failed
last_formal_version: null
last_manifest_digest: null
current_owner: null
final_artifact_refs: []
stage_receipt_refs: []
external_operations:
  confirmed_success: []
  confirmed_no_effect_or_failure: []
  unknown: []
evidence_gaps: []
patch_and_adoption_receipt_refs: []
resume_from:
  stage_instance_id: null
  version: null
  required_conditions: []
next_owner: null
budget_used_and_remaining: null # unknown without evidence / 无依据时未知
limitations_and_unverified_items: []
```

Output distinguishes complete, partial, awaiting supplement/verification/human, cancelled and failed. Complete only when all final artifact, receiver and necessary effects satisfy acceptance. State which version, who accepted, what evidence supports it, whether effects are confirmed and who resumes where. / 输出区分完成、部分、待补全查证人工、取消失败。最终工件签收及必需效果全达标才完成；明确哪版、谁签收、何证据、效果是否确认、谁从哪里继续。

Observability Metrics File / 可观测性指标文件: [collaboration-chain-observability.md](collaboration-chain-observability.md)

## Trace Hook / 追踪钩子

Use `references/trace-schema.md` to record project evidence at `.harness-analysis/<analysis_id>/trace.yaml`. Distinguish proposed specification, verified documentation and verified runtime outcomes; bundled historical traces are not current execution state. / 按 Trace 契约在项目本地记录证据，区分设计规格、已验证文档与已验证运行效果，内置历史 Trace 不是当前执行状态。
