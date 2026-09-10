# Fan-Out/Gather / 扇出汇聚

Cell / 交织点: collaboration-parallel / 协作 x 并行
Capability / 能力: Collaboration / 协作
Mode / 模式: Parallel / 并行
Pattern / 模式标识: `PATTERN_0044`; alias / 别名: 扇出聚合; specification / 专用规格: `0.1.0`; maturity / 成熟度: `draft` / 草案。
Source / 来源: User-supplied execution and observability drafts / 用户提供的执行与可观测性草案。

Description / 描述: Dispatch independent obligations, gather typed evidence without flattening differences, and pass a versioned report to an authorized decision owner. / 分发独立责任，聚合类型化证据并保留差异，将版本化报告交给有权裁决者。

Observability Metrics File / 可观测性指标文件: [collaboration-parallel-observability.md](collaboration-parallel-observability.md)

## Quick Navigation / 快速导航

- [Scope and contracts / 范围与契约](#execution-contract--执行契约)
- [Execution workflow / 执行流程](#execution-procedure--执行流程)
- [Five aggregation steps / 五步聚合](#five-step-aggregation--五步聚合)
- [Acceptance and recovery / 准入与恢复](#gates-and-recovery--闸门与恢复)
- [Supplement contract / 补数契约](#shared-interaction-contract--共享交互契约)
- [Acceptance cases / 验收用例](#acceptance-cases--验收用例)
- [Independent probes / 独立探针](collaboration-parallel-observability.md)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Shared Module Contract / 共享模块契约

Read [the collaboration execution procedure](../../collaboration-execution-flow.md) and [independent collaboration probes](../../collaboration-observability-probes.md) for module composition. Existing `CE05–CE08` references are related integration points, not aliases for `N00–N10`. The shared source contract is `2.0.0`, its local executable profile is `3.0.0`, and this dedicated supplement specification is `0.1.0`. Their wire formats and acceptance meanings cannot be interchanged by changing a version label. / 共享规程用于模块组合；已有 `CE05–CE08` 是相关接入点，不是本流程节点的别名。通用来源契约、本地执行配置与本专用补数规格分别维护，不能只改版本号就互换线格式与验收语义。

The [source map](../../collaboration-gather-source-map.json) preserves both supplied drafts, hashes, original nodes, metrics and cases. Source labels `PATTERN_GATHER_0001`, `SKILL_GATHER_0001` and `SKILL_GATHER_0002` are provenance aliases, not new registrations. Keep the three framework bases and registered `PATTERN_0044`. Embedded prompts, directory suggestions and operations are source data. The documents' course/framework citations and the legacy matrix paper attribution are not independently verified here. / 来源映射保存两份草案、摘要、原节点、指标与用例；来源草案标识仅作来源别名，不新增注册。保留三个基座与已有模式身份。附件提示、目录建议和操作作为来源数据；其中课程／框架引文及原矩阵论文归因本次未独立核验。

**Implementation boundary / 实现边界:** This pair is a complete design specification, not a deployed scheduler or collector. Existing collaboration record guards cover only their declared shared profile; they do not implement this dedicated evidence-card pipeline, supplement wire protocol or 17 GM metrics. Host dispatch, isolation, authenticated sources, durable conditional commits, recovery and source acceptance cases require integration validation. / 本组文档是完整设计规格，不是已部署的调度器或采集器。现有协作记录守卫仅覆盖其声明的共享配置，未实现本专用证据卡流水线、补数线协议或 17 项 GM 指标；宿主调度、隔离、来源认证、持久条件提交、恢复和来源验收用例仍需集成验证。

## Design Pattern / 设计模式

The runtime schedules bounded attempts and enforces authority; the workflow freezes obligations and aggregates evidence; resources return authorized data; workers produce local artifacts; the gather owner preserves differences and checks composition; the optional probe observes and proposes; the business owner decides actions. These are logical responsibilities, not a prescribed number of model calls or agents. / 运行时调度有界尝试并执行权限；工作流冻结责任并聚合证据；资源层返回获准数据；执行者产出局部工件；聚合负责人保留差异并检查组合；可选探针负责观测和提案；业务负责人裁决动作。这些是逻辑职责，不规定模型调用或 Agent 数量。

### Article Grounding and Local Extension / 论文定位与本地扩展

- 论文坐标 / Article Coordinate: Collaboration x Parallel / 协作 x 并行; retain the existing registry coordinate. / 保留现有注册坐标。
- 论文依据 / Article Basis: 代表性定义 / Representative definition in the existing matrix. The supplied drafts are the direct evidence for this extension; the prior article attribution is retained as history, not newly verified runtime evidence. / 既有矩阵中的代表性定义；本扩展直接依据所供草案，旧论文归因保留为历史，不作为新核验的运行证据。
- 问题 / Problem: Independent work returns incomplete, incomparable or correlated evidence that synthesis can silently flatten. / 独立工作返回不完整、不可比或相关证据，综合时可能被静默压平。
- 架构方案 / Architectural Solution: Freeze obligations and source contracts, collect typed cards, preserve differences through five aggregation checks and deliver a versioned report. / 冻结责任与来源契约，收集类型化证据卡，经五步聚合保留差异并交付版本化报告。
- 工程权衡 / Engineering Trade-offs: Parallel execution adds scheduling, retries, verification and gather costs; value requires a comparable baseline, not an assumed linear speedup or fixed worker count. / 并行增加调度、重试、核验及聚合成本，价值须可比基线支持，不假定线性加速或固定人数。
- 工作流诊断用途 / Workflow Diagnosis Use: Diagnose coverage loss, incompatible semantics, common-source duplication, dropped conflicts and failed cross-shard invariants. / 诊断覆盖丢失、口径不兼容、同源重复、冲突遗漏及跨分片不变量失败。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Fan-Out/Gather / 扇出汇聚（扇出聚合）.
- 诊断用途 / Diagnostic Use: Use when several contributors can work independently before synthesis. / 当多个贡献者可独立工作后再综合时使用。
- 适用工作流节点 / Applicable Workflow Nodes: Research verification, batch review, data reconciliation and code scanning. / 研究核验、批次审查、数据核验与代码扫描。
- 当前症状 / Current Symptoms: Missing shards disappear, dimensions become votes, repeated sources gain extra weight, conflicts vanish, or locally valid outputs violate a global constraint. / 缺片消失、维度被当成选票、同源获得额外权重、冲突丢失，或局部合格却违反全局约束。
- 适配信号 / Fit Signals: Real independent work, typed output, comparable semantics and an accountable gather owner. / 真实独立工作面、类型化输出、可比口径与明确聚合责任人。
- 调整方向 / Adjustment Direction: Freeze obligations, separate attempts from qualified shards, preserve source lineage and apply five aggregation checks. / 冻结责任，区分尝试与合格分片，保留来源血缘并执行五步聚合。
- 修改方式 / How To Modify: Follow N00–N10 with host-enforced budgets and boundaries; recover only affected dependencies. / 按 N00–N10 执行，由宿主强制预算与边界，仅恢复受影响依赖。
- 输入 / Inputs: Task specification, scenario policy, immutable plan/inputs, authorized executors and source adapters. / 任务规范、场景政策、不可变计划与输入、获授权执行器及来源适配器。
- 输出 / Outputs: GatherReport, raw/derived artifact indices, missing obligations, conflicts, seam results, event and handoff references. / 聚合报告、原始及派生工件索引、缺失责任、冲突、接缝结果、事件与交接引用。
- 风险与治理 / Risks & Governance: Aggregation loss `FAIL_0013`, unclear executor boundaries `FAIL_0008`, source integrity and audit `GOV_0002`, actual action authority `GOV_0001`. / 防止聚合丢失与执行者边界不清，保留来源和审计，核验真实行动权限。

## Execution Contract / 执行契约

Use independent execution without a probe, optional online pairing, or export a sealed audit package. Without a probe the workflow still owns its minimum ledger and mandatory checks. Prefer a chain for strict dependencies; first resolve uncontrolled shared writes; use one executor when it meets the objective. Hierarchy manages responsibility, gather manages returned evidence, and parallel exploration compares candidate paths. / 可独立执行、可选在线联动或导出封存审计包；没有探针时仍自持最小账本和强制检查。严格依赖优先链式，失控共享写入先处理，一个执行者满足目标时采用简单流程。层级管理责任，聚合管理返回证据，并行探索比较候选路径。

Choose concurrency and hierarchy from measured bottlenecks, deadlines, authority and cost. Prior item-count examples are not universal thresholds. Identical results may reflect agreement or common sources; inspect lineage and isolation evidence before attributing a cause. Session, workspace and tool isolation must each be declared and verified; none proves the other or source independence. / 并发与层级依据实测瓶颈、截止、权限和成本选择，旧条目数示例不是通用阈值。结果相同可能来自一致事实或同源，先查血缘与隔离证据再归因。会话、工作区、工具隔离分别声明并核验，互不替代，也不证明来源独立。

### Frozen Plan / 冻结计划

Require `run_id`, task/pattern versions, stable `target_ref` and version, propositions, `required_dimensions`, expected required/optional shards and per-shard object–proposition–dimension obligations. Freeze time windows, validity time, units/currency/period/denominator/confidence semantics; artifact, normalization, entity-map, lineage, conflict and seam rule versions; output/acceptance requirements; authority and source/write scopes; concurrency, attempts, calls, deadline and cost limits; probe permissions and bounded supplement rounds. Unknown differs from explicitly inapplicable. / 必填运行与任务／模式版本、稳定对象及版本、命题、必需维度、必选／可选分片及逐片“对象—命题—维度”义务；冻结时间、有效期、单位／币种／周期／分母／置信语义，各类规则版本、输出与验收、权限及来源／写入范围、并发／尝试／调用／截止／费用上限、探针权限与补数轮数；未知区别于明确不适用。

Each shard binds responsibility, input references, target/version, required dimensions, partition or intentional-overlap keys, deadline, tool scope and resource share. Let R be frozen required logical shards and Q the subset with every required obligation locally qualified. A successful callback or one card per shard does not establish Q. Retries never enlarge R or Q. Required timeouts stay in R; only the authorized owner or rule can issue a new plan revision with old/new populations and a reason. / 每片绑定责任、输入、对象版本、维度、分区或有意重叠键、截止、工具与资源份额。R 为冻结必选逻辑分片，Q 为全部必要义务均局部合格的子集。成功回调或每片一张卡不足以进入 Q；重试不扩大 R 或 Q，必选超时不从 R 删除。仅授权负责人或规则可发布新计划版本，保留前后全集与原因。

### EvidenceCard / 证据卡

| Field group / 字段组 | Required semantics / 必需语义 |
| --- | --- |
| Identity / 身份 | `card_id, artifact_revision, content_hash, worker_id, run_id, plan_revision, shard_id, attempt_id`; exact immutable submission and attempt binding. / 绑定精确不可变提交与尝试。 |
| Claim / 主张 | `target_ref, target_version, proposition_id, dimension, value, claim`; one testable claim with qualifications per comparable object/dimension. / 每个可比对象维度下一项有条件的可检验主张。 |
| Comparison / 比较 | `unit, currency, period, denominator, valid_time, confidence, confidence_semantics`; retain original and derived values with conversion rules. / 保留原始值、派生值和换算规则。 |
| Provenance / 来源 | `source_id, source_version, source_ref, source_lineage, lineage_status, observed_at`; exact source location, lineage evidence and acquisition time. Empty lineage is not verified independence. / 精确定位、血缘证据与获取时间，血缘空列表不表示已证独立。 |
| Audit / 审计 | `evidence_kind, limitations, raw_ref, normalized_ref`; fixture/production separation and immutable originals. / 区分样例与生产，原件不可覆盖。 |

Sources may be snapshots, files, queries, logs or code; a well-formed URL does not validate content. A compound paragraph or several references does not automatically create independent evidence. Preserve subjectively stated confidence separately from model or statistical probability. / 来源可为快照、文件、查询、日志或代码，URL 格式正确不等于内容真实；混合叙述或多个引用不自动构成独立证据。主观置信、模型概率与统计概率分别保留。

### GatherReport and State Layers / 聚合报告与状态分层

Keep `cards, missing_dimensions, conflicting_dimensions, accepted, verdict`, with missing/conflict entries bound to full comparison keys. Include run/plan/rule/report revisions and hashes; R, Q, R−Q and optional dispositions; all raw, effective, rejected and quarantined cards; normalized values and duplicate/lineage mappings; both sides of conflicts and adjudication evidence; claim-to-card-to-source traceability; checks and `seam_check`; `admitted_to_business`; actual delivery references; qualifications, risks, observation gaps and resource use/unknowns. Raw cards can be referenced instead of loaded in full into one context. / 保留核心报告字段，缺失与冲突绑定完整比较键；记录全部版本与摘要、必选及可选处置、原件／有效／拒收／隔离工件、归一化与去重血缘映射、冲突双方及裁决、来源链、准入与接缝、业务通道状态、真实交接、限定／风险／观测缺口和资源用量或未知原因。原卡可用引用保留，无须全文塞入同一上下文。

Asset maturity, run progress, attempt terminal state, local artifact qualification, report `accepted`, seam pass/fail/unknown, business `verdict`, actual action authorization, delivery and observation quality are distinct. A normally completed insufficient-evidence report does not mean acceptance or business success. / 资产成熟度、运行进度、尝试终态、局部工件合格、报告准入、接缝通过／失败／未知、业务表述、实际行动授权、交接及观测质量分别记录。正常收口的证据不足报告不等于准入或业务成功。

## Execution Procedure / 执行流程

GN IDs namespace the source N nodes for cross-module references; their numbering preserves the source. A logical node need not call a model. / GN 为来源 N 节点提供跨模块命名空间，编号保持对应；逻辑节点不要求调用模型。

<!-- gather:execution_nodes:start -->
| ID / 编号 | Node / 节点 | Required behavior / 必需行为 |
| --- | --- | --- |
| GN00 / N00 | 输入与适用性校验 | Check applicability, typed output and scope; disclose missing inputs. |
| GN01 / N01 | 冻结计划 | Freeze obligations, comparison and acceptance rules, sources, budgets and authority. |
| GN02 / N02 | 分派与执行 | Dispatch bounded attempts with separately verified session, workspace and tool boundaries. |
| GN03 / N03 | 接收与局部准入 | Validate identity, version, source and obligations; commit eligible artifacts and provisional Q. |
| GN04 / N04 | 盘点缺席 | Reconcile R minus Q and optional dispositions; preserve all missing obligations. |
| GN05 / N05 | 归一口径 | Normalize only under versioned identity, time, unit and value semantics; preserve originals. |
| GN06 / N06 | 去重但不删证据 | Group duplicate conclusions and verified upstream families; retain cards and unknown lineage. |
| GN07 / N07 | 处理冲突 | Distinguish dimensional differences from real conflicts; preserve both sides and authorized adjudication. |
| GN08 / N08 | 检查接缝 | Check declared seams as pass/fail/unknown; roll up leaf populations and exceptions. |
| GN09 / N09 | 类型化报告与闸门 | Emit typed report with structural acceptance separate from seams and business authority. |
| GN10 / N10 | 补证、局部恢复、交接与封存 | Repair affected dependencies under limits, recompute Q, version reports and evidence actual handoff. |
<!-- gather:execution_nodes:end -->

## Five-Step Aggregation / 五步聚合

1. **N04 Inventory absence / 盘点缺席.** Reconcile every required and optional shard against the frozen plan and obligation-level checks. Distinguish never started, running, absent, timeout, cancellation, runtime failure, malformed output, weak provenance and missing dimensions. Refresh Q after later admission changes. / 逐片核对冻结计划与责任覆盖，区分未启动、执行中、缺席、超时、取消、执行失败、坏格式、来源不足及缺维度；后续准入改变时刷新 Q。
2. **N05 Normalize / 归一口径.** Compare object/version + proposition + dimension + validity interval + value semantics. Apply only versioned identity/unit/vocabulary mappings; retain originals and conversion evidence. Missing denominator or confidence semantics prevents averaging; no authorized exchange-rate source/time means no cross-currency sum. Noncomparable cards remain separate or pending and may lose local qualification. / 按完整比较键分组，仅使用版本化映射并保留原值与转换证据；分母或置信语义缺失不平均，缺授权汇率来源及时点不跨币种加总；不可比材料分列或待核验，并可能失去局部资格。
3. **N06 Deduplicate conclusions and lineage / 结论与血缘去重.** Group repeated conclusions and independently verify upstream source families. Different URLs, models, prompts and sessions add no independence by themselves. Similarity suggests investigation, not lineage proof. Retain every raw card, representative mapping, minority claim and limitation; unknown ancestry stays unknown. / 归并重复结论并独立核验上游来源族；网址、模型、提示与会话不同不自动增加独立性，相似度仅提示调查；保留原卡、代表映射、少数主张和限定，未知血缘保持未知。
4. **N07 Preserve real conflicts / 保留真实冲突.** Establish comparability before testing mutually exclusive values. Session isolation, shared workspace and restricted tools are different dimensions, not three votes. Preserve conflict ID, both claims, qualifications, card/source references, rules and authorized adjudication even after resolution. Necessary unresolved conflicts block structural acceptance. Optional conflicting evidence cannot silently support the main conclusion. / 先判可比再判互斥，不同边界维度不投票；保留冲突身份、双方主张／限定／工件／来源、规则及授权裁决，已裁决也不删除。必要未决冲突阻断结构准入，可选冲突不能暗中支撑主结论。
5. **N08 Check seams / 检查接缝.** Evaluate declared composition invariants such as totals, duplicated processing, version compatibility or end-to-end constraints. Output pass/fail/unknown per rule with evidence; unknown never passes. Local qualification survives a global seam failure as a distinct fact. Hierarchical gather propagates leaf populations, gaps, conflicts and lineage using set unions, not average group percentages. / 按声明检查总量、重复处理、版本兼容或端到端约束；逐条有据输出通过／失败／未知，未知不通过。组合失败不抹掉局部合格事实；分层聚合透传叶子全集、缺口、冲突及血缘，以集合并集汇总，不平均组百分比。

Voting is disabled by default. Enable only with the same object/version/proposition, compatible time/value semantics, sufficient verified source independence and an authorized voting policy. Any unknown precondition prevents voting. / 默认不投票；仅在同对象／版本／命题、兼容时间与取值语义、足够的经核验来源独立性及授权投票政策同时成立时启用，任一前提未知都不投票。

## Gates and Recovery / 闸门与恢复

```text
accepted = all required shard obligations locally qualify
           AND necessary objects/dimensions are covered
           AND effective artifacts meet identity/comparison/source contracts
           AND necessary evidence has no unresolved conflicts

admitted_to_business = accepted AND every required seam passes
business_action_authorized = authorized business decision AND live execution checks
```

Structural admission is not evidence that the proposition is universally true. A frozen empty seam set needs an explicit inapplicability reason; it cannot be emptied after failure. Rejected or seam-unknown reports are still produced for supplementary evidence or exception review, with normal business admission false. / 结构准入不证明命题无条件为真；冻结空接缝集须明确不适用理由，不能失败后清空；拒收或接缝未知仍应生成报告，进入补证或异常审查，普通业务通道保持不准入。

N10 retries only affected shards under attempt and global limits. Metadata recovery uses source-bound patches; missing claims require new evidence; entity/unit changes rerun N05 downstream, lineage changes N06 downstream, and source admission repairs N03 downstream. Recompute final Q and append report versions. Stop at deadlines, attempt/supplement limits or exhausted authorization and preserve unresolved gaps. Do not repair a seam violation by lowering its threshold or repeat the whole graph for one failed branch. / N10 在逐片和全局限制内仅重试受影响分片；元数据用来源绑定补丁，缺主张重新采证，对象／单位从 N05、血缘从 N06、来源准入从 N03 重验下游。重算 Q 并追加报告版本，到截止、尝试／补数限制或权限耗尽时停止并保留缺口；不降低阈值修复接缝，也不因一路失败重跑整图。

Only explicitly committed, version-checked artifacts enter the effective view; arrival order cannot choose authority. Quarantine late/stale results. Cancellation records actual terminal outcomes, not merely requests. A handoff requires report version, original evidence, qualifications, risks, missing/conflict lists and a verifiable send or receipt record; generation alone is not delivery. / 仅显式提交且通过版本检查的工件进入有效视图，到达顺序不能决定权威；隔离迟到与陈旧结果。取消记录实际终态，不只记录请求。交接包含报告版本、原始证据、限定风险、缺失冲突及可核验发送或回执；生成不等于交付。

### Minimum Ledger and Scenarios / 最小账本与场景

Keep plan, attempt, artifact, aggregation, supplement/revalidation and delivery ledgers without requiring a probe. Record plan frozen, attempt started/terminated, artifact committed/rejected, absence inventoried, normalization, lineage grouping, conflict, seam check, report generated, patch adopted/rejected, revalidation completed and report handed off. Log public action facts and controlled evidence references, not private reasoning or secrets. / 无探针也保留计划、尝试、工件、聚合、补数／重验及交接账本；记录各关键事件，保留公开动作事实与受控证据引用，不保存私有推理或密钥。

Keep the five steps fixed; configure partitioning, entity/version keys, allowed sources, conflict/seam rules, budgets, authority, output and retention for research, document batches, data checks, code scans or operations. A single shard may reuse evidence checks without claiming parallel gains. / 五步核心固定；研究、文档批次、数据核验、代码扫描或运维按场景配置分区、对象版本、来源、冲突／接缝、预算、权限、输出与留存。单分片可复用证据检查，但不能宣称并行收益。

## Shared Interaction Contract / 共享交互契约

Canonical maintained source / 规范维护源: [collaboration-gather-contract.md](../../collaboration-gather-contract.md). The marked block is generated identically into both peers. / 标记区块在双方文档中由同一源生成。

<!-- gather:contract:start -->
Description / 描述: Exchange observations, gaps, evidence-backed metadata and receipts without transferring business authority to a probe. / 交换观测、缺口、有据元数据与回执，不向探针转移业务权限。

Version / 版本: `0.1.0`; source protocol / 来源协议: `扇出聚合补数协议/0.1.0`; status / 状态: draft specification / 草案规格。

Usage / 适用场景: Standalone execution, optional online observation, or an independent audit of an adapted workflow. Both peers may finish independently. / 独立执行、可选在线观测或适配外部工作流的独立审计；双方可以独立完成。

This is a documentation contract. It does not extend `collaboration-record.schema.json` or implement dispatch, storage, authorization, collection or metrics. The shared source contract `2.0.0`, executable profile `3.0.0` and this dedicated `0.1.0` protocol are distinct; migration requires explicit field, identity and evidence mappings. / 本节是文档契约，不扩展现有 Schema，也不实现调度、存储、授权、采集或指标。通用来源契约 `2.0.0`、可执行配置 `3.0.0` 与本专用 `0.1.0` 协议分别维护；迁移须显式映射字段、身份与证据。

### Envelope / 消息信封

| Fields / 字段 | Meaning and validation / 含义与校验 |
| --- | --- |
| `schema_version`, `message_type`, `message_id` | Version `0.1.0`, one of the five message types below, globally unique message identity. Reject incompatible versions before processing. / 版本为 `0.1.0`，类型取下方五类之一，消息标识全局唯一；先拒绝不兼容版本。 |
| `run_id`, `plan_revision`, `probe_run_id` | Bind the business run and frozen plan. A probe uses its own run identity in addition to the target run. / 绑定业务运行与冻结计划；探针另有自身运行身份。 |
| `producer_id`, `producer_sequence` | Authenticate the producer; sequence numbers increase within that producer instance only. Cross-producer timestamps are not global order. / 认证生产者；序号仅在同一生产者实例内单调增长，跨生产者时间戳不代表全局顺序。 |
| `node_id`, `shard_id`, `attempt_id` | Bind applicable execution scope. Run-level events may use null; do not invent a shard. / 绑定适用执行范围；运行级事件可为空，不伪造分片。 |
| `artifact_ref`, `artifact_revision`, `artifact_hash` | Exact immutable artifact binding whenever an artifact is involved. A mutable latest reference is insufficient. / 涉及工件时绑定精确不可变版本；可变的最新引用不足。 |
| `occurred_at`, `observed_at` | Distinguish occurrence from collection. Unknown historical occurrence remains null with a reason. / 区分发生与采集时间；历史发生时间未知时保留空值及原因。 |
| `causation_id`, `correlation_id` | Direct cause and the complete supplement chain; an initial message may lack a direct cause. / 直接原因与完整补数链；首条消息可无直接原因。 |
| `data_origin` | Original record, source read, deterministic derivation or historical replay; model guesses are ineligible. / 原始记录、来源读取、确定性推导或历史重放；模型猜测不可采纳。 |
| `payload`, `evidence_refs` | Typed payload and controlled references to supporting snapshots, logs or artifacts. References and hashes alone do not prove authority or truth. / 类型化载荷及受控快照、日志或工件引用；引用和摘要本身不证明权限或真实性。 |

### Five Message Types / 五类消息

| Type / 类型 | Minimum payload and receiver action / 最小载荷与接收动作 |
| --- | --- |
| `observation_event` | Event name, object version, fact references and producer authority scope. Append observation; never directly update authoritative business state. / 事件名称、对象版本、事实引用与生产者权限域；追加观测，不直接改业务权威状态。 |
| `gap_request` | `gap_id`, category, target artifact/field, required semantics, time range, necessity, allowed sources, deadline and budget. Determine recoverability before reading. / 缺口标识、类别、目标工件与字段、所需语义、时间范围、必要性、允许来源、截止与预算；先判能否恢复再读取。 |
| `data_patch` | `patch_id`, `gap_id`, exact target/base hash, field path, recovered value, source, collection time and validation evidence. Validate before appending a derived revision. / 补丁与缺口标识、精确目标及基准摘要、字段路径、补充值、来源、采集时间与校验证据；通过后追加派生修订。 |
| `action_proposal` | `action_id`, gap, bounded action/shards, required authority, estimated resources and reason. Execution decides authorization and scheduling. / 动作标识、缺口、限定动作与分片、所需权限、预计资源和原因；执行侧决定授权与调度。 |
| `apply_receipt` | Patch/proposal identity, disposition, rejection reason, new artifact binding, revalidation nodes/results/evidence and gap state. Preserve submitted, adopted, revalidated and closed separately. / 补丁或建议标识、采纳状态、拒绝原因、新工件绑定、重验节点／结果／证据和缺口状态；分开记录提交、采纳、重验与关闭。 |

Source receipt dispositions / 来源采纳状态: `已采纳` (adopted), `已拒绝` (rejected), `重复消息` (duplicate), `待处理` (pending). Gap states / 缺口状态: `已发现` → `待采集` → `已补采` → `已提交` → `已采纳` → `已重验` → `已关闭`, with `不可恢复` or `已拒绝` as explicit dispositions. Transitions require evidence; a failed recheck leaves an adopted gap open. / 状态推进须有证据，重验失败的已采纳缺口仍保持未闭环。

### Allowed Data and Protected State / 允许数据与受保护状态

Recover only facts that already exist: attempt history in authoritative logs, source versions in immutable snapshots, verified source lineage, and derived conversions with exact inputs and rule versions. A current page cannot establish its historical content. / 仅恢复已经存在的事实：权威日志中的尝试历史、不可变快照中的来源版本、经核验血缘，以及有确切输入和规则版本的派生换算；当前页面不能证明历史内容。

Write supplements only to allowed derived metadata or observation records. Never overwrite raw cards, original `value` or `claim`, `verdict`, `accepted`, seam pass status, authority, budgets, expected shards or acceptance thresholds. Conflicting old and recovered values require a discrepancy record and review. New claims require execution to acquire a new evidence card; changed scope requires an authorized new plan revision. / 补数只写入允许的派生元数据或观测记录；禁止覆盖原卡、原始值和主张、业务表述、结构准入、接缝通过状态、权限、预算、预期分片或验收阈值。旧值与补采值矛盾时记录差异并复核；新主张由执行侧获取新卡，范围变更须授权并生成新计划版本。

Gap necessity comes from frozen scenario policy: business-mandatory data, metric-required observation data, or optional diagnosis. Missing business evidence blocks its gate; optional telemetry loss does not invalidate independently supported business checks. / 缺口必要性来自冻结场景政策，分为业务强制、指标计算必要和可选诊断；缺业务证据阻断相应闸门，可选观测缺失不取消独立有据的业务检查。

### Adoption and Revalidation Workflow / 采纳与重验流程

1. Detect a gap and recover within authorized sources, time and cumulative budgets; otherwise retain null and a reason or propose new evidence collection. / 发现缺口，在授权来源、时间与累计预算内恢复；否则保留空值和原因，或建议重新采证。
2. Execution authenticates sender/source/authority and checks run, plan, active attempt where applicable, exact base hash, field allowlist and derivation. Stale bases are rejected or explicitly reevaluated. / 执行侧认证发送者、来源与权限，核对运行、计划、适用的有效尝试、精确基准摘要、字段白名单与推导；过期基准拒绝或显式重新评估。
3. Append a derived version and durable adoption receipt. Use host conditional commit and a recoverable event-publication boundary; do not overwrite the original. / 追加派生版本及持久采纳回执，使用宿主条件提交与可恢复的事件发布边界，不覆盖原件。
4. Revalidate from the earliest affected node through its dependencies; recompute final qualified shards and create a new report revision. Mark a gap closed only after supported revalidation and explicit closure. / 从最早受影响节点重验依赖下游，重算最终合格分片并生成新报告；有据重验与显式关闭后才计闭环。

| Recovered information / 补充内容 | Revalidation dependency / 重验依赖 |
| --- | --- |
| Source location or version / 来源定位或版本 | `N03` local admission → `N04–N09`; recompute final Q. / 从局部准入重验至报告，重算最终 Q。 |
| Entity mapping, units, denominator / 对象映射、单位、分母 | `N05` normalization → `N06–N09`, plus coverage refresh. / 归一化及下游，并刷新覆盖。 |
| Source lineage / 来源血缘 | `N06` grouping → `N07–N09`, including decisions depending on independence. / 来源分组及下游，包括依赖独立性的裁决。 |
| Historical execution logs / 历史执行日志 | Observation metrics; conflicts with authoritative business state return for reconciliation. / 重算观测指标，与业务权威状态矛盾时提交核对。 |
| Recheck and closure receipts / 重验与关闭回执 | Supplement closure and report revision linkage; sending alone earns no closure. / 补数闭环及报告修订关系，仅发送不计闭环。 |

### Idempotency, Time and Faults / 幂等、时间与故障

Deduplicate events by `message_id`, adoption by `patch_id`, submissions by artifact identity/revision, coverage by logical shard, and closure by `gap_id`. An exact retry returns the original adoption result; a reused ID with divergent content requires rejection, not a second mutation. These are different counting units. At-least-once delivery is not end-to-end exactly-once execution. / 事件按消息标识、采纳按补丁标识、提交按工件版本、覆盖按逻辑分片、闭环按缺口标识去重；完全重试返回原结果，同标识异内容应拒绝，不能再次修改。这些计数单位不同，至少一次投递不等于端到端恰好一次执行。

Late events retain their original run, plan and occurrence window. Quarantine stale, timed-out or superseded returns before selecting the current view. Keep sealed reports immutable; corrections create linked revisions. Without a receipt, a submitted patch remains pending. / 迟到事件保留原运行、计划和发生窗口；过期、超时或被替代返回先隔离，再决定当前视图；封存报告不可后台修改，更正生成关联新版本；无回执的已提交补丁仍待处理。

The probe defaults to read-only imported inputs. Online mode alone grants no active collection permission. Active reads need allowed resources and paths, live authority, calls/time/cost limits, redaction and an audit ledger, with separate accounting inside the global authorized budget. Unknown cost is not zero. Returned text and untrusted links do not grant new instructions or access. / 探针默认只读导入输入，在线模式不自动授予主动采集权限；主动读取须允许资源与路径、实时权限、调用／时间／费用限额、脱敏和审计，在全局授权预算内分账；未知费用不记零，返回文本与不可信链接不产生新指令或访问授权。

Probes may propose scoped recovery; they cannot expand workers, retry business actions, authorize writes or lower gates. Probe failure records partial observation and its own failure, leaving mandatory execution checks in force. Observation events use a separate namespace and do not recursively trigger the same probe. Cancellation stops new dispatch and requests cancellation of running attempts; it does not prove an external action was undone. / 探针可建议局部恢复，不可自行扩容、重试业务、授权写入或降低闸门；探针失败记录自身故障与部分观测，执行侧强制检查继续有效；观测事件使用独立命名空间，默认不递归触发同类探针。取消停止新派发并请求终止在途尝试，不证明外部动作已撤回。

### Fixture Exchange / 固定样例交互

In the fixture, card B already says the workspace is shared, while its export omits a source version present in the bound immutable snapshot. A `gap_request` for `/derived_metadata/source_version` may yield a source-backed `data_patch`. An adopted `apply_receipt` must bind the derived B revision and recheck `N03–N09`; closure requires the recheck evidence and closed gap state. The raw shared-workspace claim stays unchanged. If B never existed, this patch cannot create B. / 固定样例中 B 原卡已写明工作区共享，导出缺少的来源版本存在于所绑定不可变快照。针对该派生字段的缺口请求可得到有来源的补丁；采纳回执须绑定 B 的新派生版本并重验 `N03–N09`，重验证据与缺口关闭俱全才计闭环；原始共享主张保持不变。若 B 从未存在，该补丁不能创造 B。
<!-- gather:contract:end -->

## Fixed Fixture / 固定样例

R={A,B,C}: A says session isolated; B says workspace shared; C says tools restricted. If all cards meet source/version requirements and the scenario asks for accurate disclosure, accepted may be true and the qualified verdict retains all three dimensions plus workspace risk. This does not authorize an action or prove complete isolation. / 三片分别说明会话隔离、工作区共享、工具受限；若原卡均满足来源版本要求且场景要求准确披露，结构准入可通过，但有条件表述须保留三维及共享风险，不授权动作，也不证明完全隔离。

If B has no evidence card, Q={A,C}, coverage=2/3 and accepted=false. If B exists but only its exported source version is missing, an authorized snapshot patch plus N03–N09 revalidation may restore 3/3; B's raw claim remains shared. Fixture records must never masquerade as production evidence. / B 无原卡则覆盖 2/3、准入失败；B 存在而仅导出来源版本缺失时，授权快照补丁及重验可恢复 3/3，B 原始共享主张保持不变；固定样例不得冒充生产证据。

## Acceptance Cases / 验收用例

These 16 source cases are host acceptance requirements, all pending integration. Documentation fidelity tests do not execute them. / 以下 16 项来源用例是宿主验收要求，均待集成；文档保真测试不执行这些业务用例。

<!-- gather:execution_cases:start -->
| ID / 编号 | Scenario / 场景 | Required outcome / 必需结果 |
| --- | --- | --- |
| GET01 / E01 | 三种不同边界分别为隔离、共享、受限 | Keep three boundary dimensions and shared-workspace risk; do not vote. / 不进行二对一投票；保留三维限定和共享风险 |
| GET02 / E02 | 必选三片只回来两片 | Two of three required shards means 2/3 coverage and accepted false, with missing obligations. / 覆盖 2/3，缺片与缺维度进入报告，`accepted` 为假 |
| GET03 / E03 | 同一命题三张卡引用同一上游来源 | Three same-source comparable cards form only one verified family. / 工件可齐全，但只能形成一个已核验来源族 |
| GET04 / E04 | 同一可比键下两个互斥值 | Retain both mutually exclusive claims and sources; unresolved necessary conflict blocks admission. / 原始双方、冲突标识和来源保留；未裁决时不准入 |
| GET05 / E05 | 金额的单位或币种不同 | No unit/currency sum without supported conversion. / 无明确换算依据时不加总，不凭数值相似直接归一 |
| GET06 / E06 | 分片重试或消息重复投递 | Retries/messages cannot enlarge shard denominators or repeat effective artifacts/actions. / 分片分母不变；重复消息不新增有效工件或重复业务动作 |
| GET07 / E07 | 一片永久失败 | Permanent failure remains in the plan and partial success stays partial. / 不删除预期分片，不把其余成功片包装成全量完成 |
| GET08 / E08 | 所有局部金额合格但合计越界 | Keep local qualification separate from failed total seam; block normal business admission. / 结构准入与接缝失败分别记录，正常业务裁决通道不放行 |
| GET09 / E09 | 探针补丁试图改业务结论、权限或验收阈值 | Reject verdict, authority and threshold patches and audit without mutation. / 拒绝并审计，原始状态不变 |
| GET10 / E10 | 来源版本补丁基准摘要过期 | Reject or reevaluate a stale source-version patch against the exact base. / 拒绝或重新评估，不能套用到新工件 |
| GET11 / E11 | 探针服务不可用 | Without a probe, mandatory local checks remain; optional observation can degrade. / 本地强制检查照常；关键数据缺失时不充分，非关键观测可降级 |
| GET12 / E12 | 旧计划结果或超时结果迟到 | Quarantine late old-plan/timeout results; never overwrite a sealed report. / 原计划留痕，当前已封存报告不被覆盖 |
| GET13 / E13 | 只有当前来源，无历史快照 | No historical backfill from current content without historical snapshots. / 不补造历史内容及历史发生时间 |
| GET14 / E14 | 分层聚合中某组漏一个叶子 | Expose missing leaves through hierarchical gather. / 上层仍能定位叶子缺席，不能只看到组级成功 |
| GET15 / E15 | 规则版本变化或模型替换 | Replay frozen inputs after model/rule changes and locate version-caused differences. / 用同一冻结输入回归；差异能定位到版本与规则 |
| GET16 / E16 | 固定样例被送入生产报告 | Label fixtures and reject their use as real production evidence. / 明确标注并按来源政策拒绝其冒充真实证据 |
<!-- gather:execution_cases:end -->

## Maintenance and Trace / 维护与追踪

After changes, run `python skills/harness-engineering-patterns/scripts/sync_collaboration_gather_docs.py --write`, the skill validator, relevant tests and the full suite; regenerate the HTML view. Record evidence and pending integration in `.harness-analysis/<analysis_id>/trace.yaml` using [the trace contract](../../trace-schema.md). / 修改后同步专用视图，运行技能校验、相关测试与全量测试，重新生成 HTML；按 Trace 契约在项目分析目录记录证据和待集成事项。
