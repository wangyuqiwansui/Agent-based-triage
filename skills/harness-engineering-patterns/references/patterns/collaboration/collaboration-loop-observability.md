# Adversarial Review / 对抗评审 Observability Metrics / 可观测性指标

Cell / 交织点: collaboration-loop / 协作 x 循环

Capability / 能力: Collaboration / 协作

Mode / 模式: Loop / 循环

Identity / 稳定标识: `PATTERN_0045`, `CELL_COLLABORATION_LOOP`

Source / 来源: Existing paper coordinate / 既有论文坐标: arXiv:2605.13850; supplied observability and execution drafts / 用户提供的观测与执行草稿 `0.1.0`.

Description / 描述: Reconstruct version/control evidence, disclose gaps, compute supported metrics and return scoped supplement proposals. Produce data-quality and control-observation conclusions, never approval. / 重建版本控制证据、披露缺口、计算有据指标并返回有范围补数提案；输出数据质量及控制观察结论，不批准。

Design Pattern File / 设计模式文件: [collaboration-loop.md](collaboration-loop.md)

## Quick Navigation / 快速导航

- [Standalone use / 独立运行](#standalone)
- [Probe workflow / 探针流程](#probe-flow)
- [Shared exchange contract / 共享交互契约](#exchange)
- [Calculation semantics / 计算口径](#calculation)
- [Metric dictionary / 指标字典](#metrics)
- [Findings and report / 发现与报告](#report)
- [Acceptance / 验收](#acceptance)

<a id="standalone"></a>
## Standalone Use and Boundaries / 独立运行与边界

| Mode / 方式 | Input and result / 输入与结果 |
| --- | --- |
| Offline / 离线 | Authorized exports, snapshots and known rules within an explicit scope; report metrics, gaps and pending proposals without requiring online execution. / 范围明确的授权导出、快照及已知规则；执行方无需在线即可报告指标、缺口及待接收提案。 |
| Online side observation / 在线旁路 | Read-only subscription/query, source/field adapter and permissions; observe without mandatory interception of every business node. / 只读订阅查询、来源字段适配及权限；旁路观测，不强制拦截每个业务节点。 |
| Requested recovery / 按需补数 | Exact request, allowed sources, grade, deadline and budget; only execution-confirmed gap resolution counts as completion. / 精确请求、来源白名单、等级、截止和预算；仅执行方确认缺口解决后计补齐。 |

Candidate text alone supports a missing-evidence report, not enforcement or publication-safety conclusions. The generic core also supports chain, routing, parallel and data workflows through adapters; review metrics are not applicable only where the scenario actually lacks review objects. / 只有候选正文可报告缺口，不能判断真实阻断或发布安全。通用核心可适配链式、路由、并行及数据流程；仅场景确实不含评审对象时，评审指标才不适用。

## Shared Probe Integration / 共享探针接入

Keep [shared collaboration probes](../../collaboration-observability-probes.md) and registered `CSM25–CSM26` separate from dedicated `RM01–RM27`. Shared executable profile `3.0.0` is not dedicated contract `0.1.0`; RM collection/calculation, an authenticated receiver and destination reconciliation remain specification-only. Structural validation is not business-effectiveness evidence. / 通用探针及已注册 CSM25–CSM26 与专用 RM01–RM27 分开；通用执行配置 `3.0.0` 不等于专用契约 `0.1.0`，RM 采集计算、认证接收端及目的端核对仍为规格；结构校验不是业务效果证据。

<a id="probe-flow"></a>
## Probe Workflow / 探针流程

Minimum inputs: source/file inventory, adapter, tenant/run/window and purpose, read authority, output destination and budget. Missing control or destination evidence disables affected metrics, not the report. Output observations, metrics, gaps, risk findings, proposals and probe self-records with cutoff, source coverage, definition version and report revision. / 最小输入为来源文件清单、适配器、租户运行窗口用途、读取权限、输出位置和预算。缺控制或目的端证据只影响相关指标，不阻止报告。输出观测指标、缺口发现、提案及自身记录，附截至点、来源覆盖、定义及报告版本。

<!-- review:probe_nodes:start -->
| ID / 编号 | Node / 节点 | Action, output and recovery / 动作、产出与恢复 |
| --- | --- | --- |
| RP00 / 探针-00 | Admission / 受理 | Check observation scope, purpose, tenant, permissions and adapter; produce a restricted report when reads are unavailable without expanding authority.<br>确认数据范围、用途、租户、权限与适配器；禁止隐式扩权。<br>产出 / Output: 观测任务契约。<br>恢复 / Recovery: 无读取权限则输出受限报告，不扩大来源。 |
| RP01 / 探针-01 | Freeze observation window / 固定范围 | Freeze ledger cutoff, source watermarks, rule and metric versions; mark the window provisional when an end watermark is absent.<br>记录截止账本序号、源系统水位、规则与指标定义版本。<br>产出 / Output: 观察快照与来源清单。<br>恢复 / Recovery: 无结束水位则标为暂定窗口。 |
| RP02 / 探针-02 | Collect / 采集 | Read authorized events, snapshots, reviews and destination results with source verification; bounded retrieval failure is missing data, never observed zero.<br>读取已授权事件、快照、评审结果及外部结果；记录来源验证方式。<br>产出 / Output: 原始观测包。<br>恢复 / Recovery: 有限重试；失败记录不伪装为零事件。 |
| RP03 / 探针-03 | Normalize / 标准化 | Validate contract, event identities, times and types while retaining originals and mapping evidence; quarantine malformed records.<br>校验契约、事件唯一键、时间与类型；保留原始值和映射依据。<br>产出 / Output: 规范事件、隔离错误记录。<br>恢复 / Recovery: 不合法记录进入隔离区，不静默丢弃。 |
| RP04 / 探针-04 | Reconstruct associations / 关联重建 | Join exact run, version, baseline, round and operation identities into version and release chains; ambiguous associations stay unlinked.<br>按运行、版本、基线、轮次、操作标识关联；识别父子版本与因果。<br>产出 / Output: 版本图、责任清单、发布链。<br>恢复 / Recovery: 无可靠关联键就标无法关联，不凭相似文本强连。 |
| RP05 / 探针-05 | Check data quality / 质量检查 | Compare with expected populations to find missing, conflicting, stale, duplicate and misordered records; distinguish errors from missing proof.<br>对照预期对象检查缺失、冲突、时效、重复与异常顺序。<br>产出 / Output: 字段级缺口与来源质量结果。<br>恢复 / Recovery: 区分事实错误与缺少证明。 |
| RP06 / 探针-06 | Recover evidence / 补数取证 | Retrieve allowed original records and verify scope and content; produce proposals or explicit unavailability and never fabricate history.<br>按白名单读取原始记录，验证内容和作用域。<br>产出 / Output: 补数提案、无法补齐原因。<br>恢复 / Recovery: 无法取回历史证据就保持缺失。 |
| RP07 / 探针-07 | Inspect controls / 控制检查 | Check blockers, risk coverage, version receipts, closure evidence and actual effects; unknown never passes and suspected issues return to execution for validation.<br>核对阻断、风险覆盖、版本回执、异议关闭和实际发布。<br>产出 / Output: 检查结论与证据引用。<br>恢复 / Recovery: 未知不能转成通过；疑似问题交执行方核实。 |
| RP08 / 探针-08 | Compute metrics / 指标计算 | Use fixed definitions, populations and denominators; output verified values and unknown counts; missing inputs disable only affected metrics.<br>使用固定定义、样本范围与分母，输出已验证值与未知数量。<br>产出 / Output: 指标记录和可计算性状态。<br>恢复 / Recovery: 所需输入不足则停止该指标，不停止全部探针。 |
| RP09 / 探针-09 | Organize findings / 发现与建议 | Produce scoped risk findings, gaps and precise recovery-node suggestions; label semantic inference as a candidate, not established fact.<br>按规则组织风险发现、缺口、建议恢复节点。<br>产出 / Output: 风险发现与节点级建议。<br>恢复 / Recovery: 语义推断必须标为候选，不冒充确定事实。 |
| RP10 / 探针-10 | Deliver and receive / 交付回流 | Deliver reports/proposals and verify online acceptance records; proposals without confirmation remain pending and do not count as filled gaps.<br>输出报告和提案；在线时验证执行方的接受／拒收记录。<br>产出 / Output: 可审计交付结果。<br>恢复 / Recovery: 没有确认就维持待接收，不计算为补齐。 |
| RP11 / 探针-11 | Monitor and archive probe / 自监控归档 | Record retrieval errors, latency, budget, duplicates, report revisions and cursors; stop on probe budget exhaustion while execution maintains its own controls.<br>记录采集错误、处理延迟、预算、重复事件及报告修订。<br>产出 / Output: 探针运行记录、恢复点。<br>恢复 / Recovery: 超预算暂停探针，业务控制仍由执行方维持。 |
<!-- review:probe_nodes:end -->

### Evidence and Instrumentation / 证据与埋点

| Source / 来源 | Proves and cannot prove alone / 可证明及单独不能证明的内容 |
| --- | --- |
| Authenticated control ledger / 经验证控制账本 | Decisions, actors, contemporaneous baselines and sequence; not actual external effects. / 决定主体、当时基线与序号，不能单独证明外部生效。 |
| Immutable artifact/evidence store / 不可变工件证据库 | Reviewed content, versions and source bindings; not the truth of every semantic claim. / 被审内容、版本及来源绑定，不能证明每个语义主张真实。 |
| Destination result ledger / 目的端结果账本 | Actual effects, external objects and operation/idempotency IDs; not prior internal approval. / 实际效果、外部对象及操作幂等标识，不能证明此前内部批准。 |

Cross-check all three to inspect bypass releases. Missing complete destination records forbids a system-wide zero-violation claim; sampled telemetry cannot replace complete control/authority records. / 三类交叉核对才可检查旁路发布；目的端记录不完整不得宣称系统零违规，抽样遥测不能替代完整控制授权记录。

Expected events: admission, baseline freeze, assignment, review completion, objection creation/disposition, gap registration, sealing, gate decisions, receipt issuance/revocation, pre-release check, intent, external confirmation, baseline changes, supplement disposition and node-attempt start/end. Derive slots from the frozen plan and actual branch, with reasons for skips; never invent past events. / 必需事件含受理、冻结、分工、评审完成、异议及处置、缺口、封口、闸门决定、回执签发撤销、发布复核意图、外部确认、基线变化、补数结果及尝试开始结束；由冻结计划和实际分支推导，跳过注明原因，不补造历史。

Gate records carry type, decision-time control sequence, contemporaneous blocker/coverage snapshots, result and reasons. Field-level provenance includes original source, acquisition, verification, collection time, applicable binding and inference flag; distinguish verified, unverified, conflict, stale and unavailable. / 闸门记录含类型、当时控制序号、阻断覆盖快照、结果原因；逐字段保留原来源、取得方式、验证、采集时间、绑定及推断标志，区分已验证、未验证、冲突、过时和不可取得。

### Gap Recovery / 缺口恢复

Association gaps require unique authoritative mappings; telemetry needs real historical measurement; sources need original snapshots; control gaps need actual historical decisions, otherwise a new execution review; conflicts preserve both values; freshness follows the required time semantics. / 关联缺口须唯一权威映射，遥测须真实历史计量，来源须原始快照，控制须真实历史决定否则重走评审；冲突保留双方值，时效遵守对应时点要求。

Grades: authoritative fact, reproducible derivation, inferred candidate, unavailable. Verified facts/derivations can resolve suitable fields only after acceptance; inferred history stays separate. Stop on authority/scope failure, budget/retry bounds, expiry, unverifiable evidence or changed target. / 分级为权威事实、可复算派生值、推断候选和未取得；事实派生须验证接收后才解决适用字段，推断历史单列。越权越界、预算重试触顶、过期、证据不可验或对象变化均停止。

<a id="exchange"></a>
## Shared Exchange Contract / 共享交互契约

Embedded for independent operation. Maintain [the shared source](../../adversarial-review-contract.md) and synchronize both peers. / 为独立运行内嵌；维护共享来源并同步两份规约。

<!-- review:contract:start -->
Description / 描述: Exchange control observations, scoped evidence requests and proposals while execution retains adjudication and release authority. / 交换控制观测、有范围的取证请求与提案，裁决和放行权限始终属于执行方。

Version / 版本: `0.1.0`; status / 状态: draft specification / 草案规格。

Usage / 适用场景: Standalone execution, independent offline observation, optional online observation or checkpoint evidence recovery. Neither peer requires the other to be running. / 独立执行、独立离线观测、可选在线旁路或检查点补证；双方均不要求对方必须在线。

Implementation boundary / 实现边界: This dedicated contract is specification-only. It is distinct from collaboration source contract `2.0.0`, executable profile `3.0.0`, CE09 and CSM25–CSM26. No dedicated service, authorization, durable proposal receiver, receipt signer or RM calculator is supplied by this document. An adapter must explicitly map fields and demonstrate its own validation and failure paths. / 本专用契约仅为规格，与协作来源契约、可执行配置、CE09 和 CSM25–CSM26 分开；本文不提供专用服务、鉴权、持久补数接收端、回执签发器或 RM 计算器。适配器须显式映射字段并验证校验与失败路径。

### Identity and bindings / 身份与绑定

| Fields / 字段 | Required semantics / 必需语义 |
| --- | --- |
| `contract_version`, `tenant_id`, `run_id` | Require compatible `0.1.0` semantics and authenticated tenant scope. A transport retry retains its run; a new business request starts another run. / 校验兼容版本与经认证租户；传输重试保留运行标识，重新发起业务任务另建运行。 |
| `artifact_id`, `artifact_version`, `baseline_digest`, `review_round` | Bind the immutable candidate and the exact review basis; new evidence or rules start a new baseline and round even without a body edit. / 绑定不可变候选与精确审查依据；正文未变但证据或规则改变仍须新基线、新轮次。 |
| `node_id`, `task_id`, `attempt` | Distinguish logical work from its bounded retries. Do not count attempts as independent tasks or risk coverage. / 区分逻辑任务及有限重试，不把尝试数当任务数或风险覆盖。 |
| `event_id`, `ledger_sequence`, `related_event_ids` | Unique event identity, authoritative order within a run and causal references. Exact redelivery is deduplicated; same ID with different content is quarantined as conflict. / 事件唯一键、运行内权威顺序与因果引用；同内容重投去重，同标识异内容隔离为冲突。 |
| `occurred_at`, `collected_at`, `unknown_time_reason` | Occurrence and collection are separate. Unknown historical occurrence is null with a reason, never copied from collection time. / 发生与采集时间分开；历史发生时间未知时为空并注明原因，不用采集时间冒充。 |
| `actor_id`, `source_type`, `source_refs`, `data_classification` | Trusted ingress verifies actor, authority, source and sequence; payload assertions cannot authenticate themselves. Unverified exports remain unverified. / 可信接入验证主体、权限、来源和序号；载荷自述无法自证身份，未验证导出保持未验证。 |
| `observation_revision`, `control_revision`, `report_revision` | Independent concurrency domains for side observations, release control and reports; none equals the artifact version. / 分别控制旁路观测、放行控制与报告的并发版本，不等同工件版本。 |

Baseline digest / 基线摘要 = canonical binding of candidate content, versioned evidence manifest, rules, required risks, reviewer plan and action boundary. Final review-package digest / 最终评审包摘要 = sealed results, objection disposition evidence and closure record. The receipt binds both digests plus adjudication, control revision and authority. Do not include future review results in the baseline hash. / 基线规范绑定正文、版本化证据清单、规则、必审风险、评审计划和动作边界；最终评审包绑定封存结果、异议处置证据和封口记录；回执绑定两者及裁决、控制修订与授权。基线哈希不得包含未来才产生的评审结果。

Fix encoding, field ordering, numeric/time formats and digest algorithm/version; preserve exact candidate text, including whitespace and punctuation. A digest detects binding changes; it proves neither source truth nor issuer identity. / 固定编码、字段排序、数值和时间格式、摘要算法及版本；保留正文原貌，包括空白和标点。摘要证明绑定变化，不证明来源真实或签发身份。

### Exchange workflow / 交换流程

| Message / 消息 | Minimum content and handling / 最小内容与处理 |
| --- | --- |
| Control event / 控制事件 | Full identity envelope, event type, authority-backed payload and immutable source references. Observation cannot rewrite the underlying control fact. / 完整身份信封、事件类型、有权威依据的载荷和不可变来源引用；观测不得改写底层控制事实。 |
| Supplement request / 补数请求 | `request_id`, `gap_id`, exact run/artifact/baseline/round, `field_path`, `expected_observation_revision`, evidence grade, allowed sources/operations, authorization reference, deadline, attempt budget and resume node. / 请求与缺口标识、精确对象绑定、字段路径、预期观测修订、证据等级、来源及操作白名单、授权引用、截止、尝试预算和恢复节点。 |
| Supplement proposal / 补数提案 | `proposal_id`, request and gap bindings, proposed value, evidence grade, source references/digest, collection/expiry times and claimed baseline impact. Submission alone changes no business fact. / 提案标识、请求与缺口绑定、提议值、证据等级、来源引用及摘要、采集与过期时间、声明的基线影响；提交本身不改变业务事实。 |
| Acceptance result / 接受结果 | Request/proposal identity, one disposition below, reason, old/new observation and control revisions, exact resulting baseline and resume node. Persist and replay the result with the application decision. / 请求与提案标识、下列一种处置、原因、新旧观测和控制修订、结果基线与恢复节点；接受决定及其结果须持久保存、可重放。 |
| Risk finding / 风险发现 | Affected scope, evidence, uncertainty and suspected violated rule; execution validates the finding and owns any pause, objection or new adjudication. / 受影响范围、证据、不确定性及疑似违反规则；执行方核验并负责暂停、异议或重新裁决。 |

Receiver order / 接收顺序: contract → authenticated identity/permission → tenant → correlated object → active request → current baseline/round → source authenticity → evidence freshness → field allowlist → expected observation revision. Any failure records a rejection with no partial update. / 依次校验契约、身份权限、租户、关联对象、请求有效性、当前基线轮次、来源真实性、证据时效、字段白名单、预期观测修订；任一失败只记拒收，不部分更新。

Use `(tenant_id, request_id, proposal_id)` as the durable idempotency key. Same key and same content returns the original result, including after restart; divergent content conflicts. A distinct stale proposal is rejected or filed under its historical version and never applied to the current head. / 以租户、请求、提案组成持久幂等键；同键同内容即使重启后也返回原结果，异内容冲突；新的陈旧提案拒收或归历史，不应用于当前版本。

| Disposition / 接受结果 | Execution-owned transition / 执行方状态转换 |
| --- | --- |
| `accepted_observation` / 已接受为观测补充 | Append source-backed telemetry and conditionally increment observation revision; resume the original check if its decision basis is unchanged. / 追加有来源遥测，条件更新观测修订；判断依据未变时恢复原检查。 |
| `accepted_re_review` / 已接受并触发重新评审 | Register new evidence/configuration, create a new baseline, invalidate current use of the old receipt and complete every required risk again. / 登记新证据或配置，建新基线，使旧回执当前不可用，再完成全部必审项。 |
| `pending_human_verification` / 待人工核实 | Preserve the proposal as unconfirmed; affected release conditions remain paused. / 保存未确认提案，受影响放行条件保持暂停。 |
| `rejected` / 已拒绝 | Persist reason such as wrong scope/version, expiry, authority, conflict or source failure; do not advance. / 记录范围或版本不符、过期、权限、冲突或来源失败等原因，不推进。 |

Execution recomputes baseline impact from the actual field/value and current dependencies; never trust `changes_baseline: false` supplied by a probe. Candidate edits always create new artifact versions. Evidence, rules, risk lists, plans or action changes create new baselines even without text changes. A historical identity/authority proof that changes only the final proof package reopens adjudication and receipt issuance; changed actors or independence boundaries require full new-baseline review. / 执行方按实际字段、值及当前依赖重判基线影响，不信任探针自报“不改变基线”。正文修改必建新版本；证据、规则、风险、计划或动作变更均建新基线。仅补入历史身份或授权证明而改变最终证明包时，重开裁决并重签回执；主体或独立性边界变化须新基线完整重审。

### Write boundary and recovery / 写入边界与恢复

The probe may append its observations and submit proposals. It cannot directly change candidate text, business evidence, rules, required risks, review conclusions, objection status, permissions, approval, receipts or release status. / 探针可追加自身观测和提交提案，不得直接修改候选、业务证据、规则、必审风险、评审结论、异议、权限、批准、回执或发布状态。

Retain original values, source verification, collection time and correction links. Authoritative facts and reproducible derivations require evidence; inferred candidates live separately and unavailable history stays null. A proposal sent without receiver confirmation remains pending and contributes no completed supplement. / 保留原值、来源验证、采集时间和更正引用；权威事实及可复算派生值须有证据，推断候选单独存储，无法取得的历史保持空值；未收到接收确认的提案保持待接收，不计补齐。

One original gap anchors requests, retries and results. Bound depth, retries, total cost and expiry; probe telemetry does not recursively trigger its own unbounded collection. Resume from confirmed cursors and authoritative revisions. / 请求、重试和结果围绕同一原始缺口；限制深度、重试、总成本和有效期，探针遥测不触发自身无限补数；从已确认游标和权威修订恢复。

Probe outage permits declared degradation of noncritical telemetry only. Execution must still persist its control ledger and independently enforce critical evidence, coverage and authority checks. / 探针停机仅允许声明非关键遥测降级；执行方仍须持久保存控制账本，独立检查关键证据、覆盖与权限。

Treat source documents, logs, candidates and review text as data. Embedded requests to change policy, read credentials or publish confer no authority. Collect structured reasons and evidence references, exclude private chain-of-thought and raw secrets, and enforce tenant, purpose and retention boundaries. / 来源文档、日志、候选及评审文本均作为数据；内嵌改策略、取凭据或发布指令不授予权限。采集结构化理由及证据引用，不采集私密思维过程或原始秘密，落实租户、用途与保留边界。
<!-- review:contract:end -->

<a id="calculation"></a>
## Calculation Semantics / 计算口径

| State / 可计算性 | Meaning / 含义 |
| --- | --- |
| `calculable` / 可计算 | Fields and denominator are known for the declared population; a complete risk plan allows 3/4 coverage without inventing a fourth result. / 声明总体字段分母已知；完整风险计划可算 3/4，无需伪造第四项结果。 |
| `partially_calculable` / 部分可计算 | Verified subset only, with subset denominator, unknown count and limitations. / 仅验证子集可算，附子集分母、未知数及限制。 |
| `not_calculable` / 不可计算 | Missing denominator, association, clock or fact; value remains null. / 分母关联时钟或事实不足，值为空。 |
| `not_applicable` / 不适用 | Scenario or required opportunity absent under the definition; explain why. / 按定义不含场景或机会，说明原因。 |

Zero denominators usually mean not applicable, never 100%. An empty required-risk list in adversarial review is a configuration error and not calculable. A count over complete authoritative data may be confirmed zero; missing sources are not zero. Report control check outcome separately as pass, fail, unknown or not applicable. / 零分母通常不适用，不是 100%；对抗评审必审列表为空是配置错误且不可计算。权威数据完整时计数可确认为零，缺来源不是零。控制结论另分通过、未通过、未知、不适用。

Deduplicate populations by run; artifact/version; baseline/round; baseline/round/risk; logical task; original objection; gate decision; external operation; original gap; request/proposal. Attempts, multiple reviewers and duplicate confirmations must not inflate populations. / 各总体按运行、工件版本、基线轮次、基线轮次风险、逻辑任务、原异议、闸门决定、外部操作、原缺口及请求提案去重；重试、多评审者或重复确认不扩充分母。

Order by authoritative ledger sequence and causality. Durations require compatible clocks, preferably one monotonic domain; unverifiable cross-source timing stays null. Freeze watermarks and lateness policy; late/corrected evidence creates report revisions. Yesterday's gates use yesterday's snapshots: today's repairs cannot sanitize prior release, and today's new risk is not automatically a previously known blocker. / 用权威序号与因果排序；耗时需相容时钟，优先单一单调时钟域，跨源无法核实时为空。冻结水位与迟到策略，迟到纠正产生报告修订；历史闸门按历史快照，今日修复不洗白此前发布，今日新风险不自动算此前已知阻断。

Each metric records ID/name, definition version, grain, population/snapshot, applicable numerator/denominator, value/unit, calculability, unknown/excluded counts and reasons, sources, cutoff and report revision. Distributions include sample count; default median and nearest-rank p95 require a version change when algorithms change. Missing paired baselines or independent labels preclude causal overhead or semantic accuracy claims. / 每项记录编号名称、定义版本粒度、总体快照、适用分子分母、值单位、可计算性、未知排除数量原因、来源截至点及报告修订；分布附样本数，默认中位数及最近秩 p95，换算法须改版本。缺成对基线或独立标注不能宣称因果开销或语义准确率。

<a id="metrics"></a>
## Observability Metrics / 可观测性指标

- 质量指标 / Quality Metrics: RM01–RM08 cover event/evidence completeness, binding, missing fields, comparable conflict, freshness, risk coverage and structural independence. / 控制证据完整、绑定缺失、可比冲突、时效、风险覆盖及结构独立性。
- 时延指标 / Latency Metrics: RM19, RM22, RM26–RM27 separate review, accepted recovery, probe processing and paired overhead. / 分离评审、接受补数、探针处理及成对增量耗时。
- 成本指标 / Cost Metrics: RM17–RM20 measure terminal tasks, retry amplification and dimension-specific use; separate execution and probe accounts. / 计量终态任务、重试放大及分维用量，执行与探针账分开。
- 风险指标 / Risk Metrics: RM09–RM14 and RM24 inspect blockers, actual violations, receipt interception/match, re-review, closure and effective probe writes. / 检查阻断、真实违规、回执拦截匹配、重审关闭及探针写入生效。
- Trace 指标 / Trace Metrics: RM15–RM16 and RM21–RM25 provide contextual approval, release lineage, supplement outcomes and delivery diagnostics. / 提供批准背景、发布责任链、补数结果及投递诊断。

All 27 metrics are source-mapped specifications, not runtime calculators or measured results. Definitions remain distinct from CSM even when names seem similar. / 27 项均为来源映射规格，不是运行时计算器或测量结果；即使名称相似也与 CSM 分开。

<!-- review:metrics:start -->
| ID / 编号 | Metric / 指标 | Definition and limits / 定义与边界 |
| --- | --- | --- |
| RM01 / 指标-01 | Required control event completeness / 必需控制事件完整率 | Verified required event slots / slots expected from the actual branch and admission plan. Skips need reasons; an unknown expected inventory is not calculable.<br>已取得且可验证的必需事件槽位数 ÷ 按实际分支应产生的必需事件槽位数。<br>使用受理计划、实际分支记录和事件清单推导槽位；跳过节点要有理由。无法知道应有集合则不可计算。 |
| RM02 / 指标-02 | Evidence lineage completeness / 来源链完整率 | Required evidence items with original source, version/snapshot, locator, content verification and applicable object / all evidence items required by the baseline. Traceability does not establish truth.<br>具有原始来源、版本／快照、定位、内容校验和适用对象的必要证据项数 ÷ 本基线要求的证据项数。<br>分母来自审批证据要求，不是实际采到几条就算几条；只能证明可追溯，不能证明事实一定正确。 |
| RM03 / 指标-03 | Version binding consistency / 版本绑定一致率 | Required objects consistent with their baseline, artifact and round / expected required objects, including reviews, dispositions, receipts and release references. Missing objects are unmet; unknown denominator is not calculable.<br>与其声明基线、工件和轮次一致的必需绑定对象数 ÷ 预期必需绑定对象数。<br>对象包括评审结果、处置证明、回执和发布引用；缺对象计未满足，分母未知则不可计算。 |
| RM04 / 指标-04 | Critical field missing rate / 关键字段缺失率 | Missing or unverifiable critical field instances / all applicable critical field instances under a versioned field list. Count per object and field; disclose unverifiable sources separately.<br>缺失或无法验证的关键字段实例数 ÷ 适用的关键字段实例总数。<br>实例按对象与字段计数；关键字段清单需版本化。未知来源归入未满足，并单列原因。 |
| RM05 / 指标-05 | Comparable fact conflict rate / 可比较事实冲突率 | Fact fields with unresolved contradictions / fields with at least two comparable evidence chains for the same object, definition and time. Different times or definitions are not conflicts; no comparable pairs is not applicable.<br>存在未解决矛盾的事实字段数 ÷ 同一对象、口径和时点下具有至少两条可比较证据的事实字段数。<br>不把不同时点、不同口径当矛盾；没有双源可比字段则不适用，不代表不存在错误。 |
| RM06 / 指标-06 | Evidence freshness compliance / 证据时效满足率 | Required evidence satisfying its freshness or historical-snapshot rule / required evidence subject to that rule. Require rule, data time and use time; unknown evidence is excluded from the numerator and reported.<br>满足对应时效或历史快照要求的证据项数 ÷ 所有适用时效要求的必要证据项数。<br>需有规则、数据时点和使用时点；无法证明满足的项不计分子，另列未知。 |
| RM07 / 指标-07 | Effective required risk coverage / 必审风险有效覆盖率 | Distinct required risks with valid completion results for the current baseline and round / configured required risks. Each completion needs rules, evidence and a valid reviewer; duplicate reviewers add no coverage; an empty required list is a configuration error.<br>当前基线与轮次下，具有有效完成结果的不同必审风险项数 ÷ 配置的必审风险项总数。<br>完成结果要有规则、证据与有效主体；“无异议”不是完成证明。多名评审者重复覆盖不加分。 |
| RM08 / 指标-08 | Structural independence evidence / 结构独立性证据满足率 | Independence checks satisfied by runtime evidence / checks required by the current policy. Identity, context, source lineage and authority evidence measure structural separation, not a probability of cognitive independence.<br>已用运行时证据证明满足的独立性检查项数 ÷ 当前策略要求的独立性检查项数。<br>检查身份、上下文、来源链和权限等结构；不把该比率解释为认知独立的概率。 |
| RM09 / 指标-09 | Blocking enforcement / 阻断执行率 | Gate attempts rejected while contemporaneous evidence proves an open blocker / attempts proven to have an open blocker. Compute approval and release gates separately; disclose unknown attempts and do not claim full coverage from a verified subset.<br>已证实当时存在未关闭阻断，且实际被闸门拒绝的尝试数 ÷ 已证实当时存在未关闭阻断的闸门尝试数。<br>需要同一时点的阻断快照和决定；批准闸、发布闸分开统计。未知状态尝试单列，不能隐形排除后宣称全量100%。 |
| RM10 / 指标-10 | Confirmed noncompliant releases / 已确认违规发布数 | Count distinct externally confirmed effects verified to violate at least one hard release condition. Multiple violation labels count once per operation; missing complete destination records cannot establish a total of zero.<br>已实际生效且经核验违反至少一项放行硬条件的不同发布操作数。<br>按外部实际发布去重；无回执、错版、未关闭阻断等可多标签，但一次操作只计一次。没有目的端完整记录时不能证明总数为零。 |
| RM11 / 指标-11 | Invalid receipt interception / 无效回执拦截率 | Requests proven to lack a required receipt or use an invalid receipt and rejected before effects / requests proven to lack or misuse a receipt. Include forged, wrong-version, expired, revoked and wrong-scope receipts; require verification and effect records; interception does not exclude bypasses.<br>证实缺少必需回执或使用无效回执，且在产生副作用前被拒绝的发布请求数 ÷ 证实缺少必需回执或使用无效回执的发布请求数。<br>无效包括伪造、错版、过期、撤销、错范围；缺少必需回执也纳入此指标；需要验证材料和实际执行记录。拦截成功不等于整个系统没有旁路。 |
| RM12 / 指标-12 | Actual release receipt match / 实际发布回执匹配率 | Actual releases proven to hold a current, valid, scope-matching receipt at controlled submission / actual releases in the destination-defined population. Missing historical approval evidence means unverifiable, not proof approval never existed.<br>能证明在受控提交时持有当前有效、范围匹配回执的实际发布操作数 ÷ 范围内实际发布操作总数。<br>分母由目的端或等效完整结果账本确定。缺少对应审批记录只证明无法验证，不直接推定历史上从未审批。 |
| RM13 / 指标-13 | New baseline re-review completion / 新基线重审完成率 | Changed baselines with all required risks re-reviewed at their first renewed approval request / distinct changed baselines that reapply. It measures submission readiness; denied requests need not meet 100 percent, but approved baselines require complete re-review.<br>变更后重新申请批准的基线中，申请时全部必审项已针对新基线完成的数量 ÷ 变更后重新申请批准的不同基线数量。<br>同一基线多次申请以首次申请为该指标取点。用于诊断提交准备度，不要求每个被拒请求都达100%；实际获批基线必须满足完整重审。 |
| RM14 / 指标-14 | Objection closure evidence completeness / 异议关闭证据完整率 | Declared closure records with authorized independent reviewer, rule, evidence, target version and reason / all declared closure records. Separate repaired-in-successor from disproven-original objections; reviser self-closure is ineligible.<br>具有合法复核主体、规则、证据、目标版本和理由的关闭记录数 ÷ 已声明关闭的异议处置记录数。<br>“后继版本已修复”和“原异议不成立”分开统计；修订者自报关闭不计分子。 |
| RM15 / 指标-15 | First-round approval / 首轮批准率 | Runs approved at the first complete adjudication of their first version/round / runs with such a complete adjudication. Include revise, escalate and terminate decisions in the denominator; pending review/evidence stays separate. This is not a safety objective.<br>首版首轮完整裁决即获批的运行数 ÷ 已有首版首轮完整裁决的运行数。<br>完整裁决包括批准、要求修改、升级或终止；尚待评审或待补证的运行单列。此指标不是安全目标。 |
| RM16 / 指标-16 | Release responsibility traceability / 发布责任链可追溯率 | Actual operations traceable through intent, receipt, adjudication, review results and original evidence / actual operations in scope. Every link needs a real object; complete links do not prove correct judgment.<br>能从实际发布追溯到发布意图、回执、裁决、评审结果与原始证据的操作数 ÷ 范围内实际发布操作总数。<br>关联链条齐全仍不证明每个判断正确；需要每一环的真实对象而非拼接文本。 |
| RM17 / 指标-17 | Node first-attempt success / 节点首尝试成功率 | Logical tasks succeeding on their first attempt / started tasks terminal in success or failure. Identity includes run, baseline, round, node and task; report unstarted, skipped and externally canceled tasks separately.<br>首次尝试即成功的逻辑节点任务数 ÷ 终态为成功或失败且实际启动过的逻辑节点任务数。<br>逻辑任务按运行、基线、轮次、节点及任务标识区分；未启动、条件跳过、外部取消不进分母，须单列数量，不悄悄并入成功。 |
| RM18 / 指标-18 | Retry amplification / 重试放大系数 | Actual attempts for success/failure-terminal logical tasks / those tasks. One means no retries; revised-baseline reviews are new tasks, not transport retries; report open tasks provisionally and separately.<br>终态为成功或失败的逻辑节点任务的实际尝试总数 ÷ 这些逻辑节点任务的数量。<br>无重试时为1；修订后的新评审属于新逻辑任务，不当作传输重试。未结束任务另列暂定统计。 |
| RM19 / 指标-19 | Review-round duration / 单轮评审时长 | Complete adjudication time minus first dispatch time for the round; report median and nearest-rank p95, sample count and clock basis. Include evidence waiting but split execution/waiting; unfinished rounds contribute age, not completed duration.<br>本轮完整裁决时点－本轮首次分发评审时点；输出中位数和第95百分位。<br>包含该轮等待取证时间，另拆等待与执行；未完成轮次以当前年龄另列，不塞入已完成分布。 |
| RM20 / 指标-20 | Metered budget consumption / 已计量预算消耗率 | Confirmed use / approved budget within each measurement dimension. Never mix calls, tokens and duration; absent metering gives a known lower bound or null; positive use against zero budget is an anomaly.<br>同一计量维度的已确认消耗量 ÷ 当前任务批准的该维度预算。<br>调用数、输入输出用量、处理时长等分别统计，不混单位；缺计量数据时只报已知下限或不可计算。预算为零却有消耗时作为配置／预算异常。 |
| RM21 / 指标-21 | Terminal gap completion / 已终结缺口补齐率 | Distinct supplement gaps confirmed resolved with valid facts by execution / distinct requested gaps terminal or past deadline. Include rejection, unavailable and timeout in the denominator; pre-deadline pending gaps are separate. Offline proposals without acceptance never count as resolved.<br>已由执行方确认使用有效事实解决的缺口数 ÷ 已进入补数且已终结或截止时间已到的不同缺口数。<br>成功、拒绝、无法取得、超时均保留；截止前尚在处理的缺口单列。独立离线、没有接收方确认时，不把提案计作已补齐。 |
| RM22 / 指标-22 | Accepted supplement duration / 已接受补数耗时 | Confirmed acceptance and gap-resolution time minus the first valid request time for that gap. Compute only for resolved gaps and also report failures and unresolved ages to expose survivor bias.<br>执行方接受并确认缺口解决时点－该缺口首次有效请求时点。<br>仅对已解决缺口计算分布，同时报告失败数和未决年龄，避免只看幸存成功样本。 |
| RM23 / 指标-23 | Supplement proposal rejection / 补数提案拒收率 | Distinct rejected proposals / distinct proposals with terminal acceptance results. Pending proposals are reported outside the denominator; split version, authority, expiry, conflict and source reasons. Rejection may demonstrate working boundaries.<br>被执行方拒绝的不同提案数 ÷ 已有终态接受结果的不同提案数。<br>待接收不计分母但必须显示数量；按错版、越权、过期、冲突、来源不足分解。高拒收率可能证明边界在起作用，不能一味压低。 |
| RM24 / 指标-24 | Effective unauthorized probe writes / 探针越权写入生效数 | Count authority-confirmed direct probe writes to protected business fields that actually took effect. Blocked attempts are separate; incomplete write logs cannot establish zero; execution-applied authorized proposals are not direct probe writes.<br>经权威记录确认，由探针身份直接修改受保护业务字段且已生效的次数。<br>被成功拦截的尝试另外统计，不计生效数。写权限日志不全时不能声称零越权；合法的补数提案由执行方应用不属于探针直接写入。 |
| RM25 / 指标-25 | Duplicate delivery rate / 重复投递率 | Confirmed repeated receipts of identical events / all raw receipts before deduplication. Same identity with different content is a conflict, not a duplicate; redelivery alone is not a business failure.<br>接收次数中被确认是已见相同事件的次数 ÷ 原始接收总次数。<br>幂等处理前统计；同一标识不同内容是冲突，不是正常重复。至少一次投递机制下存在重复并不自动是业务错误。 |
| RM26 / 指标-26 | Probe processing latency / 探针处理延迟 | Observation persistence time minus input reception time within the probe clock domain. This is not event-occurrence-to-visibility latency across systems; that requires verified clock alignment.<br>观测结果持久化时点－该输入在探针入口被接收时点。<br>使用探针自身同一时钟域；不冒充业务事件从发生到可见的全链路延迟。后者要额外证明跨源时钟一致。 |
| RM27 / 指标-27 | Incremental execution latency from probe / 探针对执行时长的增量影响 | For comparable repeated pairs, compute duration with probe minus duration without probe, plus relative-difference distribution. Fix candidate, rules, task structure and environment; no paired baseline means not calculable and one production log cannot establish causal overhead.<br>在可比成对测试中，对每对计算“接入探针耗时－不接探针耗时”，并报告差值及相对差值分布。<br>需固定候选、规则、任务结构和环境并重复测试；没有基准不能计算，单条生产日志不能证明因果开销。 |
<!-- review:metrics:end -->

## Default Gate Suggestions / 默认门控建议

Execution checks per-baseline completion, no open blockers, current receipt and explicit authority. Probe aggregates diagnose controls; they do not replace conditions. Complete review need not spend all budget; exhausted incomplete work cannot count as complete. / 执行方逐基线检查完成、无未关闭阻断、当前回执及明确授权；探针聚合用于诊断，不替代条件。完成评审无需用尽预算，耗尽但未完成不能算完成。

Do not optimize for zero objections, agreement, reviewer count, first-round approval or decaying findings: they can reflect candidate quality, shared blind spots or changing risk mix. Logs alone cannot establish avoided incident cost, missed-defect rate or semantic truth. Independent labels or authorized adjudicated outcome samples are needed; compare like scenarios, risks and rule versions. / 不以零异议、一致、人数、首轮批准或发现递减作目标，这些可反映候选质量、共同盲区或风险结构变化。仅凭日志不能证明避免事故成本、漏检或语义真值；须独立标注或授权复核样本，按同类场景风险规则比较。

<a id="report"></a>
## Findings and Report / 风险发现与报告

Separate confirmed violations, suspected anomalies and evidence gaps. Confirmed effects violating hard rules, version mismatches, unauthorized closure or effective probe writes warrant high-priority findings. Missing receipt records alone do not prove historical approval never existed; execution validates findings and owns scoped response. / 区分确认违规、疑似异常和证据缺口；确认效果违反硬规则、错版、越权关闭或探针越权写入生效应报高优先级发现。只缺回执不证明历史批准从未存在，由执行方验证发现并限定响应。

Report order: what can/cannot be confirmed; anomalies/gaps; current baseline coverage/control checks; efficiency/probe overhead; accepted/rejected/pending proposals; sources/formulas/limits and exact resume nodes. Keep aggregate labels low-cardinality, artifact references controlled, text redacted and retention bounded. / 报告依次列可确认与不可确认、异常缺口、当前覆盖控制、效率开销、接受拒绝待定提案、来源公式限制及精确恢复节点；汇总低基数，明细受控引用、脱敏及限定保留。

Synthetic example: three of four required risks gives RM07 = 3/4; no destination records gives RM10/RM12 = null, not zero/100%. Two unacknowledged proposals remain pending. State that the listed controls have the observed evidence and final authorization belongs to execution. / 构造示例：四项风险完成三项时 RM07 为 3/4；无目的端记录时 RM10/RM12 为空，不是零或 100%；两条未确认提案仍待接收。结论说明所列控制拥有观测证据，最终授权由执行方完成。

<a id="acceptance"></a>
## Acceptance and Replay / 验收与回放

RPT scenarios are pending integration requirements, not deployment test results. Combined RET/RPT coverage includes normal, denied, missing evidence, wrong version, conflict, duplicate, late, concurrent and uncertain-effect paths. / RPT 为待接入要求，不是部署测试结果；与 RET 合并覆盖正常拒绝、缺证错版、冲突重复、迟到并发及效果不确定。

<!-- review:probe_cases:start -->
| ID / 编号 | Scenario / 场景 | Required outcome / 必需结果 |
| --- | --- | --- |
| RPT01 / 探针验收-01 | 只给候选正文，无控制账本。 | With candidate text but no ledger, report gaps; control-effectiveness metrics are not calculable. / 能独立运行并输出缺口；控制效果指标不可计算。 |
| RPT02 / 探针验收-02 | 两名评审者都覆盖同一风险，另一项无人检查。 | Two reviewers checking one risk leave the other uncovered; deduplicate coverage by risk. / 覆盖按风险去重，不按评审人数得出100%。 |
| RPT03 / 探针验收-03 | 零次阻断场景。 | With no blocking opportunities, enforcement rate is not applicable rather than 100 percent. / 阻断执行率不适用，不填100%。 |
| RPT04 / 探针验收-04 | 对抗评审必审清单为空。 | An empty required-risk list is a configuration error, not a vacuous pass. / 配置错误；不能用零分母证明全部通过。 |
| RPT05 / 探针验收-05 | 关键源没有接入。 | A missing critical source requires an unverified-scope disclosure, not a system-wide zero-violation claim. / 标明未验证范围，不输出全系统“零违规”。 |
| RPT06 / 探针验收-06 | 同一事件重复投递十次。 | Ten identical event deliveries create one business fact; duplicates remain probe statistics. / 业务计数仍为一次；重复投递计入探针自身统计。 |
| RPT07 / 探针验收-07 | 同一事件标识对应不同载荷。 | The same event ID with different payloads is quarantined as conflict, never silently deduplicated. / 记录冲突，隔离调查，不按普通重复静默吞掉。 |
| RPT08 / 探针验收-08 | 事件乱序、跨机器时钟偏移。 | Out-of-order events and clock skew use authoritative sequence/causality; unreliable durations stay null. / 按权威序号和因果恢复；无法可靠计算的耗时置空。 |
| RPT09 / 探针验收-09 | 今日关闭了昨日发布时未关闭的异议。 | Closing an objection today cannot make yesterday's blocked publication compliant. / 昨日控制检查仍按昨日快照，不被今日状态洗白。 |
| RPT10 / 探针验收-10 | 只有现在的权限记录，要求补历史权限。 | Current permissions cannot backfill historical permission proof; keep history unknown. / 保留历史未知；不把现在状态当历史证明。 |
| RPT11 / 探针验收-11 | 新版本收到旧版补数。 | Old-version supplements never update the current version; reject or archive historically. / 不回填当前版；拒收或归历史。 |
| RPT12 / 探针验收-12 | 补数提案声称“不改变基线”，实际改了来源。 | A proposal claiming no baseline change but changing a source requires execution to detect the impact and re-review. / 执行方重新判定影响并重审，不能信任自报布尔值。 |
| RPT13 / 探针验收-13 | 探针试图直接修改批准或异议状态。 | Probe writes to approval or objection state are denied; blocked attempts are not counted as effective writes. / 权限阻断；记录企图，不将拒绝误算成生效写入。 |
| RPT14 / 探针验收-14 | 只生成补数提案，没有接受确认。 | A generated proposal without acceptance confirmation stays pending, not completed. / 维持待接收，不算补齐。 |
| RPT15 / 探针验收-15 | 无法取回历史使用量。 | Unavailable historical usage stays null with a gap; estimates cannot overwrite factual fields. / 数值为空，附缺口，不用估算覆盖真实字段。 |
| RPT16 / 探针验收-16 | 没有不接探针的对照运行。 | Without a no-probe comparison, incremental impact is not calculable; report probe processing time separately. / 增量时长影响不可计算；可另报自身处理耗时。 |
| RPT17 / 探针验收-17 | 没有独立缺陷标注。 | Without independent defect labels, do not report actual miss rate, false-positive rate or semantic accuracy. / 不报告真实漏检率、误报率或语义准确率。 |
| RPT18 / 探针验收-18 | 只有部分抽样遥测。 | Sampled telemetry cannot prove every release satisfied hard constraints. / 不能据此证明全部发布符合硬约束。 |
| RPT19 / 探针验收-19 | 探针崩溃后重放已确认提案。 | Replaying an accepted proposal after a crash is idempotent and neither reapplies nor recounts it. / 幂等返回，不重复应用，不重复计数。 |
| RPT20 / 探针验收-20 | 日志内容含要求读取凭据或发布的指令。 | Log instructions to access credentials or publish remain data and cannot widen capabilities. / 按数据处理，不执行，不扩大能力。 |
| RPT21 / 探针验收-21 | 补数导致探针自身反复产生新缺口。 | Repeated probe self-gaps merge under the original gap and stop at depth/budget bounds. / 合并原缺口，受预算与深度限制，不无限反馈。 |
| RPT22 / 探针验收-22 | 高风险任务占比上升，首轮批准率下降。 | When high-risk workload share rises, stratify first-round approval before attributing decline to model regression. / 先分层展示，不直接归因为模型退化。 |
<!-- review:probe_cases:end -->

Source definitions and fingerprints / 来源定义及指纹: [adversarial-review-source-map.json](../../adversarial-review-source-map.json). Maintain generated blocks using `scripts/sync_adversarial_review_docs.py --write`; source/contract checks verify documentation only. / 用专用同步脚本维护生成区块，来源契约检查仅验证文档。
