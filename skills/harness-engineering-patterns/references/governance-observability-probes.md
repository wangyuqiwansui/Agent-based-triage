# Governance Observability Probes / 治理工作流可观测性探针

Name / 名称: Independent Governance Evidence and Enrichment / 独立治理证据与观测补全。Definition version / 定义版本: `1.0.0`; status / 状态: design specification / 设计规范。

Description / 描述: Independently collect, authenticate, associate, reconstruct, diagnose, measure, and enrich existing governance evidence, while preserving unknowns and the execution system's authority. / 独立采集、核验、关联、重建、诊断、统计并补全既有治理证据，保留未知状态与执行系统的裁决权。

This maintained guide adapts [the supplied probe document](sources/governance/36_治理模块_工作流可观测性探针.source.txt), including its twelve steps, thirty-six metric definitions, and twenty-eight acceptance designs. Follow [GOV_BOUNDARY_OBS 1.0.0](governance-contract.md) when exchanging data with [execution](governance-execution-flow.md). These documents specify required behavior; they do not supply a running collector, metric calculator, authenticator, message receiver, or business controller. Acceptance designs below have not been executed against a production integration. / 本维护版承接用户探针资料的十二步骤、三十六项指标与二十八项验收设计；与执行侧交换数据遵循共享协议。这些文件规定应有行为，未提供运行中的采集器、指标计算器、认证器、消息接收器或业务控制器；下述设计用例未对生产集成执行。

Source-local `PATTERN_OBSERVABILITY_0036`, `SKILL_OBSERVABILITY_0036`, and `NODE_OBSERVABILITY_0036` remain provenance aliases. They do not create new registered patterns, skills, or nodes, nor replace existing stable IDs. Source claims about lectures or external frameworks remain attributed source claims. / 来源局部标识仅作溯源别名，不新注册模式、技能或节点，也不替换既有稳定标识。有关讲义及外部框架的说法保留为来源陈述。

## Quick Navigation / 快速导航

- [Scope, inputs, and quality / 边界、输入与质量](#scope)
- [Twelve probe steps / 十二探针步骤](#probe-steps)
- [State and report / 状态与报告](#report)
- [Counting rules / 统计规则](#counting)
- [Thirty-six metrics / 三十六项指标](#metric-catalog)
- [Twenty-eight acceptance designs / 二十八项验收设计](#acceptance)
- [Failure, privacy, and shutdown / 失败、隐私与停止](#constraints)

<a id="scope"></a>
## Scope, inputs, and quality / 边界、输入与质量

Use for offline audit, authorized read-only observation, missing evidence retrieval, version drift, cumulative exposure, and incident analysis. It attaches across chain, routing, parallel, orchestration, loop, and hierarchy topologies; maintain causal predecessors, real branches, parent/child obligations, logical action versus retry, and explicit handoff acceptance. / 用于离线审计、获授权的只读观测、缺证检索、版本漂移、累计暴露与异常复盘。可横切链式、路由、并行、编排、循环与层级拓扑，须维护因果前驱、真实分支、父子责任、逻辑动作与重试区别以及明确交接接收。

Do not use observation to invent approvals, retrospectively change audit time, guess payment success, acquire business write access, or promote authority from unrelated past success. Tool-returned text and source documents remain data; embedded instructions cannot alter tool permissions. / 不用观测来补造批准、回改审计时间、猜测付款成功、取得业务写权或依据无关历史成功扩权；工具返回与来源文档仍是数据，内嵌指令不能改变工具权限。

| Input / 输入 | Need and boundary / 必需性与边界 |
|---|---|
| Evidence and analysis scope / 材料与分析范围 | Required: tenant, target objects/runs, timezone-bearing window, scenario, and definition version. With no material, output an input gap, not metric values. / 必需：租户、对象或运行、带时区窗口、场景、定义版本；无材料时仅输出输入缺口，不输出指标数值。 |
| Original field mapping / 原始字段映射 | Required for nonstandard input; retain originals and versioned conversion rules. / 非标准输入必需；保留原文与版本化转换规则。 |
| Node/event contract / 节点事件契约 | Required for coverage: determines applicable fields and expected events at each actual state. / 计算覆盖率必需；决定真实状态下适用字段与应有事件。 |
| Immutable snapshots / 不可变快照 | Proposal, artifact, contract, historical policy, approval, credential, and ledger records as required by the question. Current policy cannot establish historical policy. / 按问题取得提案、工件、契约、历史策略、审批、凭证和账本；不能用现行策略证明历史策略。 |
| Business-result authority / 业务结果权威来源 | Required to establish side effects, final outcomes, or duplicates; tool success or request acceptance is insufficient. / 判断副作用、终态及重复效果必需；工具成功或请求接收不充分。 |
| Independent operation inventory / 独立操作清单 | Required for whole-population coverage: authoritative business operations, persisted dispatch intents, approval requests, producer inventory/sequence, or controlled test inventory. Received complete logs alone are not a denominator. / 判断总体覆盖率必需：权威业务操作、持久派发意图、审批请求、生产者清单或序号、受控测试清单；仅收到的完整日志不能作分母。 |
| Read adapters and feedback channel / 读取适配器与反馈通道 | Optional and explicitly authorized by source/tenant; no adapter means offline candidate output, not claimed online adoption. / 可选且按来源与租户明确授权；无适配器则输出离线候选，不声称线上采纳。 |

Different facts have different authorities: approval systems establish approval records, authorization services establish permission, business systems establish effects, and authoritative ledgers establish exposure. Keep conflicts between credible sources unresolved until adjudicated; never select whichever result favors execution. / 不同事实的权威来源不同：审批系统证明审批记录，授权服务证明权限，业务系统证明效果，权威账本证明暴露。可信来源冲突须保留待裁定，不能选择最有利于执行的结果。

| Quality / 质量状态 | Meaning / 含义 |
|---|---|
| `verified` / 已核验 | Source, target, and content checked for the stated observation; the execution gate still independently checks applicability and authorization. / 已核验本次观测的来源、对象与内容；执行入口仍独立核验适用性与授权。 |
| `pending_verification` / 待核验 | A lead exists but authenticity or applicability is unresolved; cannot authorize. / 存在线索但真实性或适用性未确认，不能授权。 |
| `missing` / 缺失 | The node contract requires evidence that has not been obtained; retain it in known required populations. / 节点契约要求但未取得的证据，须保留在已知必需总体中。 |
| `conflict` / 冲突 | Incompatible facts or versions; do not choose automatically. / 事实或版本不兼容，不自动选择。 |
| `expired` / 已过期 | Too old or bound to a superseded target; may explain history, cannot authorize now. / 超过时效或绑定旧对象，可解释历史但不能支持当前授权。 |
| `not_applicable` / 不适用 | Not required in this actual branch/stage, with recorded contract-based justification. Missing values alone never justify exemption. / 实际分支或阶段不要求，须记录契约依据；不能因值缺失就豁免。 |

Separately classify values as source facts, deterministic derivations with versioned formulas/inputs, or model hypotheses. A source fact is not inherently verified; hypotheses remain diagnostic leads and never enter authoritative amounts, approvals, or business outcomes. / 另行区分来源事实、带版本公式与输入的确定性推导、模型假设；来源事实不天然已核验，假设仅作线索，不进入权威金额、审批或业务终态。

Default configuration: no business/policy writes, no sampling of critical decisions/approvals/dispatch/reservations/results, network queries disabled unless authorized, explicit performance sampling, bounded query/retry budgets and deadline, source-specific late-arrival tolerance, and target-specific patch expiry. Missing budgets or validity configuration does not mean unlimited queries or permanent validity. / 默认禁止业务与策略写入；关键裁决、审批、派发、预留及结果不得采样；联网查询须获授权，性能采样须声明；明确查询与重试预算、期限、来源迟到容忍窗与目标补丁有效期。配置缺失不表示无限查询或永久有效。

<a id="probe-steps"></a>
## Twelve probe steps / 十二探针步骤

| Step / 步骤 | Required behavior and evidence / 必需行为与证据 |
|---|---|
| 探01 — Scope and contracts / 目标与数据契约 | Fix question, tenant, target, window, pattern/skill versions, node contract, metrics, and units. Establish whether authoritative results and independent denominators exist; declare unavailable conclusions before analysis. Payment, export, and deployment need different impact units. / 固定问题、租户、对象、窗口、模式与技能版本、节点契约、指标及单位；先确认权威结果与独立分母，提前声明不能得出的结论。付款、导出与发布不得强行共用金额口径。 |
| 探02 — Capture originals / 采集与保存原始引用 | Collect events, artifacts, policies, approvals, reservations, and outcomes with source/version/digest, occurrence and retrieval times, access scope, and retention. Never sample critical audit events; record performance sampling. Preserve embedded instructions only as data. / 采集事件、工件、策略、审批、预留及结果，保存来源、版本、摘要、发生与获取时间、访问范围及保留策略。关键审计不采样，性能采样留规则；内嵌指令仅作为数据。 |
| 探03 — Normalize and authenticate / 规范化、去重与真实性 | Retain originals and a separate normalized view. Deduplicate tenant plus event ID: identical content once; divergent content quarantined as conflict. Verify source permissions, protocol, digests, and fields; retain sequence gaps, parser failures, and unverifiable material instead of silently dropping them. / 保留原件并另建标准视图。按租户与事件标识去重：同内容一次，异内容隔离冲突。核验来源权限、协议、摘要与字段；保留序号缺口、解析失败及不可核验材料，不静默丢弃。 |
| 探04 — Strict association / 严格关联 | Link tenant/run/action, proposal/policy digests, business idempotency identity, and external request ID. Retries have distinct attempts under one action; preserve parent/child and shared account references. Similar name, amount, or time is only a candidate. Reject cross-tenant links; aggregate cross-run exposure only through an authorized subject/account without merging run evidence. / 用租户、运行、动作、提案与策略摘要、业务幂等身份、外部请求标识关联；重试不同尝试但同动作，保留父子及共享账户。名字、金额与时间相近仅为候选；拒绝跨租户，跨运行只经授权主体与账户汇总且不混写证据。 |
| 探05 — Causality and accountability / 状态与责任链 | Rebuild by causal references, source sequence, and versions, with time only supporting. Retain disorder, late events, clock skew, orphan receipts, missing predecessors, and contradictory terminals. Minimum chain: request → contract → proposal/artifact → policy → decision/required approval → budget/authority → final check → dispatch → business result → verification/handoff. Rejected actions require no payment result; unsubmitted actions need no invented request ID; pending reconciliation remains unknown. Report stage completeness separately from business closure. / 按因果引用、来源序号和版本重建，时间辅助；保留乱序、迟到、时钟偏差、孤立回执、缺失前驱与终态矛盾。最低链：请求→契约→提案与工件→策略→裁决及必要审批→额度与权限→最终检查→派发→业务结果→核验及交接。拒绝分支不要求付款结果，未提交不造请求标识，对账待定保留未知；阶段完整与业务闭环分报。 |
| 探06 — Governance and aggregate risk / 治理异常与组合风险 | Check policy binding/provenance, independent authorized approval, actual payload, shared exposure, unknown-result retries, and scenario-specific promotion evidence. Separate approved policy changes, unauthorized relaxation, unknown provenance, and same-version divergent content. A higher limit alone is not a violation. If cross-run ledger data is unavailable, global exposure is unknown. / 检查策略绑定与来历、独立有权审批、实际载荷、共享暴露、未知结果重试及场景匹配晋升证据。区分合法调整、未批准放宽、来源未知与同版本异内容；升限本身不是违规。无跨运行账本时全局暴露未知。 |
| 探07 — Classify the gap / 缺口分类 | Missing evidence: retrieve existing original references. Fact not performed: request a new governed business step. Conflict: preserve and seek adjudication. Stale evidence: require new evidence/redecision. Access denied: hand to authorized owner. Ambiguous linkage: keep candidate unbound. Never fabricate approvals, alter timestamps, bypass access, or guess ownership. / 证据缺失：检索既有原记录；事实未发生：请求受治理的新业务步骤；来源冲突：保留并请求裁定；时效失效：新证据或重新裁决；权限不足：交授权负责人；关联不明：保留未绑定候选。禁止造批准、改时间、绕权或猜归属。 |
| 探08 — Metrics with quality / 指标与质量 | Use the catalog and fixed evidence snapshot. Emit numerator/denominator, value/unit, window, grouping, definition version, sources, quality, and unknown/pending counts. Unavailable denominator, key source, or control baseline gives null plus reason. Late evidence creates a new calculation revision; negative or untrusted durations remain clock anomalies. / 使用指标字典与固定证据快照；输出分子、分母、值及单位、窗口、分组、口径版本、来源、质量和未知与未决数量。分母、关键来源或对照基线缺失则空值加原因。迟到重算新增版本；负值与不可信耗时保留时钟异常。 |
| 探09 — Bounded read-only retrieval / 受控只读补证 | Query permitted historical approvals, policies, artifacts, outcomes, and ledger references within budget/deadline; revalidate identity, version, applicability, and age. Never pay, issue, publish, delete, change rules, or expand privilege to test success. If an unknown outcome becomes authoritative, submit its reference; execution independently updates status/ledger after rechecking. / 在来源白名单、预算与期限内查询历史审批、策略、工件、结果及账本，再核身份、版本、适用性及时效。禁止用付款、发券、发布、删除、改规则或扩权验证结果。未知终态查明后仅提交权威引用，由执行侧复核并更新状态与账本。 |
| 探10 — Patches and recommendations / 补丁与控制建议 | Bind exact target revision, proposal/policy/artifact digests and evidence, and write only whitelisted observation enrichment. Send control recommendations separately with scope, evidence, risk, expiry, and required authority. Without controller receipt, report “recommended”, never “stopped”. / 精确绑定目标版本、提案、策略及工件摘要与证据，仅写观测补全白名单。控制建议另发，含范围、证据、风险、有效期和所需授权；无控制执行回执只能报告建议，不能称已停止。 |
| 探11 — Verify feedback / 核验反馈与关闭 | Match per-field receipt to patch ID/digest, exact target, and observation revision. Keep rejection reasons and partially unresolved items. Conflicts require new snapshot/reanalysis; never freshen old evidence timestamps. Close only when receiver-verified evidence meets original acceptance; sent/read/partially accepted/acknowledged is insufficient. / 逐字段回执核对补丁标识与摘要、精确目标及观测版本；保留拒绝原因和未采纳项。冲突须新快照重分析，不刷新旧证据时间。接收方核验且满足原条件才关闭；发送、已读、部分采纳或知悉均不充分。 |
| 探12 — Report and next window / 报告与下一窗口 | Separate verified facts, deterministic explanations, hypotheses, and recommendations. Assign owner, permitted next action, deadline, and closure criterion to each gap. Offline audits yield reports/candidates; online probes retain cursor, deduplication identities, source sequence, and pending requests. Stop automatic retrieval at budget/retry limit while preserving unresolved work. / 分开已核验事实、确定性解释、假设与建议；缺口逐项配负责人、允许下一步、期限与关闭条件。离线产报告及候选；在线保留游标、去重身份、来源序号及未闭环请求。预算或重试达限停止自动补证且保留未解决事项。 |

<a id="report"></a>
## State, report, and durable layers / 状态、报告与持久层

Probe states progress from awaiting input → collecting → validating → associating → analyzing, then report-ready, waiting evidence, waiting human, or waiting late data. Evidence retrieval ends as candidate found, inaccessible source, denied access, or confirmed unperformed fact. A verified candidate is submitted or retained for future integration; adoption ends as accepted, partial, rejected, conflict, expired, or pending human. Reanalysis determines actual gap closure. Completion with unresolved items, completion, and stopped are separate terminal outcomes. / 探针依次经历待输入、采集、校验、关联与分析，再到可报告、待补证、待人工或待迟到数据。查询结果区分找到候选、来源不可达、权限不足与确认事实未发生；核验后提交或待接入，采纳分为完整、部分、拒绝、冲突、过期或待人工，再分析决定缺口是否关闭。结束但有未解决项、完成与停止分别记录。

Probe state, evidence quality, business state, and definition lifecycle state remain separate. Probe completion means only that this analysis ended; receipt timeout remains unresolved. / 探针状态、证据质量、业务状态及定义生命周期分别保存；探针完成只说明本次分析结束，回执超时仍未闭环。

Every report includes run ID; tenant/runs/window/timezone/scenario; source inventory; reconstructed trace; verified facts; deterministic derivations; hypotheses; metric results; gaps; candidate/applied observation patches; recommendations; receipts; unresolved risk; conclusion and stop reason. “No verified violation found” must include coverage and missing evidence, never become “all compliant”. “Enriched” must identify fields, provenance, verifier, and adoption status. / 每份报告包含运行标识，租户、目标运行、窗口、时区与场景，来源清单、轨迹、已核验事实、确定性推导、假设、指标、缺口、候选或已采纳观测补丁、建议、回执、未解决风险、结论与停止原因。“未发现已证实违规”须同时说明覆盖与缺证，不能变成“全部合规”；“已补全”须说明字段、来源、核验者与采纳状态。

Preserve six separately versioned layers: originals, normalized events, association graph, observation enrichment, metric snapshots, and gap/feedback history. Everything traces back to originals; none of the derived layers overwrites source facts. Preserve restricted references or redaction instead of replicating salaries, accounts, personal data, or secrets into metric systems. / 保留六个独立版本层：原始证据、标准事件、关联图、观测补全、指标快照、缺口与反馈历史；均回溯原件，派生层不覆盖来源事实。敏感工资、账户、个人资料及密钥使用受控引用或脱敏，不复制到指标系统。

<a id="counting"></a>
## Counting and result semantics / 统计口径与结果语义

1. Separate units: logical business operation by `business_operation_id` or verified equivalent; proposal by content version; decision by receipt; call by attempt. Five retries remain one logical operation. Count only once per tenant-scoped identity; quarantine divergent identity content instead of silently deduplicating away evidence. / 分离单位：逻辑业务操作用业务身份去重，提案按内容版本，裁决按回执，调用按尝试；五次重试仍是一个逻辑操作。租户内身份只计一次，异内容身份冲突隔离保留。
2. Derive denominators from independent authoritative inventories, not complete observations. Known required members with missing evidence stay in the denominator and out of the complete numerator. Unknown population means unknown metric; observed-sample results must explicitly restrict their scope. / 分母来自独立权威清单，不来自完整观测样本；已知必需成员缺证仍留分母且不得入完整分子。总体未知则总体指标未知；已见样本结果须明确限制范围。
3. Group at least by scenario, risk, action type, subject/resource domain, policy version, skill version, and business-time window. Exposure groups additionally bind account, dimension, and unit/currency. Preserve sample mix across comparisons; relaxed rules can improve pass rate without improving execution quality. / 至少按场景、风险、动作类型、主体或资源域、策略版本、技能版本与业务时间窗分组；暴露还绑定账户、维度及单位或币种。比较保留样本构成，规则放宽导致通过率提升不代表执行质量提升。
4. Use occurrence time for business windows and ingestion time for collection latency. Keep not-yet-due, overdue unresolved, and resolved populations visible. Late arrivals append calculation revisions with reasons and recomputation time, preserving prior snapshots. / 业务窗口按发生时间，采集延迟按接收时间；未到期、逾期未决及已解决分别保留。迟到重算新增计算版本、原因与时间，不覆盖旧快照。
5. `unknown` / 未知 is a metric result status: a required population, result authority, historical version, truth label, clock, or baseline is unavailable. Set `value: null` and explain what is missing. `not_applicable` / 不适用 means a complete, trusted population has no applicable members, or the contract excludes the metric for this scenario; record the basis. A zero denominator never produces 100%; an unknown denominator never means zero. / 指标未知表示必需总体、权威结果、历史版本、真值、时钟或基线不可得，值设空并说明缺失；不适用表示完整可信总体无适用成员，或契约明确排除此场景，并记录依据。零分母不能产出100%，未知分母不能当零。
6. Counts and totals require known scoped populations and sources before reporting zero; absence of received events is not proof of zero violations. Distributions require trusted comparable clocks; negative durations are anomalies, never clamped to zero. Preserve valid-sample counts and excluded/unresolved counts. / 计数与总量只有在限定总体及来源已知时才能报告零；没收到事件不证明零违规。分布要求可信可比时钟；负耗时记异常，不截为零，保留有效、排除与未决样本数。
7. Report original record completeness and post hoc reconstructability separately. A later-discovered authentic prior approval can improve reconstruction, but never erase the original missing field; an approval created after execution cannot repair prior authorization. / 原始记录完整性与事后可还原程度分开报告。事后找到真实事前批准可提高可还原程度，但不消除原缺字段；事后才形成的批准不能补成事前授权。

Each metric result carries `metric_id`, bilingual name, `definition_version`, evidence snapshot/calculation revision, window/timezone, population definition/reference, group dimensions, numerator/denominator for ratios, value/unit, sample count, quality and result status, missing/pending/not-yet-due counts, source references, formula/derivation, and computation time. Counts, sums, and distributions explicitly declare their aggregation and applicable sample population instead of inventing a ratio denominator. `quality_state` describes evidence; `result_status` distinguishes measured / 已测得, unknown / 未知, and not_applicable / 不适用. / 每项结果携带稳定指标标识、双语名、口径版本、证据快照与计算版本、窗口及时区、总体定义与引用、分组、比例的分子分母、值与单位、样本数、质量与结果状态、缺失和未决与未到期数、来源、公式或派生规则、计算时间。计数、总和与分布明确聚合方法及适用样本，不伪造比例分母；证据质量与测得、未知、不适用的结果状态分开。

<a id="metric-catalog"></a>
## Metric catalog / 指标字典

Stable IDs are `MET_GOV_01` through `MET_GOV_36`; source row labels below preserve provenance. Definition version is `1.0.0`; change the version when formula or applicability changes. These are specifications, not computed production values or an executable metric registry. / 稳定标识从 `MET_GOV_01` 到 `MET_GOV_36`，下表原始编号用于溯源；口径版本为 `1.0.0`，公式或适用范围变化须升版。这里是规范，不是已计算生产结果或可执行指标注册表。

### Governance and business effects / 治理与业务效果

| ID and name / 编号与名称 | Formula or aggregation / 公式或聚合口径 | Authority and limits / 来源与边界 |
|---|---|---|
| 指01 `MET_GOV_01` Policy binding coverage / 放行策略绑定覆盖率 | Allow receipts with complete matching proposal and policy IDs, versions, digests ÷ all allow receipts in authoritative inventory. / 提案与策略标识、版本、摘要完整匹配的允许回执数 ÷ 权威清单允许回执总数。 | Decision inventory, proposal and policy stores; complete binding does not prove reasonable or authorized rules. / 裁决清单、提案与策略库；绑定完整不证明规则合理或变更有权。 |
| 指02 `MET_GOV_02` Policy provenance completeness / 策略来历完整率 | Effective versions with original content, change reason, proposer/approver identities, authority, and activation record ÷ effective versions requiring review. / 具备原内容、原因、提出与批准身份、授权及生效记录的版本数 ÷ 应核验生效版本数。 | Policy/approval stores; initial versions also need lawful issuance. / 策略与审批库；初始版本也须合法发布依据。 |
| 指03 `MET_GOV_03` Confirmed separation violations / 职责分离违规数 | Count deduplicated effective policy changes or approvals proven to violate independent identity or approval authority requirements. / 按原记录去重，计已证实不满足身份独立或审批权限却生效的策略变更或批准。 | Identity, authorization, approval, activation; missing evidence separately reported, not treated as proved violations. / 身份、授权、审批与生效记录；缺证单列，不混作已证实违规。 |
| 指04 `MET_GOV_04` Final check completeness / 最终执行检查完整率 | Dispatched actions with every applicable pre-dispatch check evidenced ÷ actions in authoritative dispatch inventory. / 派发前全部适用检查有证据的动作数 ÷ 权威派发清单动作数。 | Durable dispatch intent, gate checks, payload, external requests; not only actions with observed check logs. / 持久派发意图、检查、载荷与外部请求；不只统计有检查日志的动作。 |
| 指05 `MET_GOV_05` Invalid receipt interception / 失效回执拦截率 | Blocked final-check attempts with verified invalid/mismatched receipts ÷ all verified attempts of that class. / 失效或不匹配回执被拦截次数 ÷ 此类已核验最终检查尝试总数。 | Gate records and fault-injection truth; exclude normal attempts and separately report unknown outcomes. / 入口记录及注入真值；正常尝试不入分母，未知结果单列。 |
| 指06 `MET_GOV_06` Unauthorized side effects / 实际越权副作用数 | Count logical operations with authoritative effect evidence outside the then-valid principal, object, or action authority. / 计权威效果证据证实超出当时主体、对象或动作授权的逻辑操作。 | Business result, actual payload, historical authorization/policy; unavailable result authority cannot yield zero. / 业务结果、实际载荷、历史授权与策略；缺结果来源不能报告零起。 |
| 指07 `MET_GOV_07` Peak cumulative exposure / 累计暴露峰值 | Maximum of confirmed consumption + pending reserved + unknown occupied within one account/unit/window; also exposure ÷ applicable limit. / 同账户、单位、窗口内已确认消耗＋待执行预留＋未知占用的最大值，另报相对上限比例。 | Authoritative ledger; buckets mutually exclusive, currencies never summed, grandfathered exposure after limit reduction annotated. / 权威账本；三类互斥，不跨币种相加，降额导致存量超额另注。 |
| 指08 `MET_GOV_08` Excess admission events / 额度超用事件数 | Count verified new admissions/reservations exceeding a then-applicable limit in any governed dimension. / 计新准入或新增预留使适用维度超出当时上限的已核验次数。 | Atomic ledger transitions and historical limits; later lowered limits do not retroactively establish violation. / 原子账本迁移与历史限额；事后降额不反证过去违规。 |
| 指09 `MET_GOV_09` Duplicate side effect rate / 重复副作用率 | Logical operations with more effects than legally expected ÷ verifiable logical operations in authoritative result inventory. / 实际效果超过合法预期次数的逻辑操作数 ÷ 权威结果清单可核验逻辑操作数。 | Reconciliation and idempotency records; also report excess-effect total and unknown operation count; not proof about unverifiable members. / 对账与幂等记录；另报超额效果次数及未知操作数，不据此证明不可核验成员。 |
| 指10 `MET_GOV_10` Unknown occupied exposure / 结果未知占用量 | Sum occupancy still in unknown status, plus unknown action count, separately per amount/count or other unit. / 按金额、条数等单位分别求当前未知占用总和，另报未知动作数。 | Authoritative ledger/reconciliation; observation cannot release occupancy. / 权威账本与对账；观测不得释放占用。 |
| 指11 `MET_GOV_11` Unknown outcome age / 未知结果年龄 | Outstanding cases: time from first unknown transition to report time; median, p95, oldest. / 未决案例首次进入未知至报告时刻的时长分布：中位数、p95与最老年龄。 | State history and clock; no applicable cases → not applicable, untrusted time → unknown. / 状态历史与时钟；无适用样本为不适用，时间不可信为未知。 |
| 指12 `MET_GOV_12` Timely reconciliation closure / 对账按期闭环率 | Due unknown-result cases with authoritative terminal and ledger settlement by deadline ÷ all due cases. / 期限内取得权威终态并完成账本处置的到期案例数 ÷ 全部到期未知结果案例数。 | Reconciliation/results/settlement; keep not-yet-due and still-unknown counts visible. / 对账、结果与结算；未到期及仍未知另列。 |
| 指13 `MET_GOV_13` Approval wait time / 人工审批等待时长 | Processed requests: duration from awaiting approval to approved, rejected, or terminal timeout; report distribution. / 已处理请求进入待审批至批准、拒绝或超时终结的时长分布。 | Approval request and terminal events; report ages of open requests separately. / 审批请求与终结事件；开放请求年龄另报。 |
| 指14 `MET_GOV_14` Interruptions per 100 actions / 每百动作人工打断次数 | Actual human reminders/interactions ÷ logical actions entering governance × 100. / 实际人工提醒或交互次数 ÷ 进入治理流程逻辑动作数 ×100。 | Human interaction log and action intake inventory; repeated reminders count repeatedly; missing interaction logs cannot be estimated. / 人工交互日志与动作立案清单；重复催办重复计，无日志不估算。 |
| 指15 `MET_GOV_15` Reviewed redundant approvals / 经复核冗余审批率 | Independently reviewed requests unnecessarily routed to approval under then-current rules ÷ all independently reviewed approval requests. / 独立复核认定按当时规则无需人工却要求审批数 ÷ 独立复核审批请求数。 | Independent review with sampling method or controlled truth; no truth means unknown. / 带抽样方法的独立复核或受控真值；无真值则未知。 |
| 指16 `MET_GOV_16` Promotion evidence adequacy / 权限晋升证据合格率 | Promotions with relevant scenario outcomes, observation window, anomaly review, and valid approval ÷ all promotions. / 同时具备适用场景结果、观察窗、异常审查与有效批准的晋升数 ÷ 晋升总数。 | Authorization, verified outcomes, approvals; success in low-risk scenarios does not cover other scenarios. / 授权、核验结果与审批；低风险成功不能覆盖其他场景。 |
| 指17 `MET_GOV_17` Revocation confirmation latency / 撤销传播确认延迟 | Longest interval from authoritative revocation activation to all relevant dispatch gates acknowledging the new fencing version; also unconfirmed gate count. / 权威撤销生效至所有相关派发入口确认新围栏版本的最长时间，另报未确认入口数。 | Revocation and gate acknowledgements; incomplete acknowledgement leaves overall delay unresolved, never zero; submitted effects are not undone. / 撤销与入口确认；确认不全则整体延迟未决，不能记零；不表示撤回已提交效果。 |
| 指18 `MET_GOV_18` Business audit chain completeness / 业务审计链完整率 | Known effect-producing operations with every applicable accountability link ÷ such operations in authoritative business-result inventory. / 已知有副作用且全部适用责任链齐全的操作数 ÷ 权威业务结果清单此类操作数。 | Request/proposal/policy/approval/dispatch/results; unknown effects separately counted, never build denominator from complete chains. / 请求、提案、策略、审批、派发与结果；未知效果单列，不用完整链自造分母。 |

### Evidence quality and enrichment / 证据质量与补全

| ID and name / 编号与名称 | Formula or aggregation / 公式或聚合口径 | Authority and limits / 来源与边界 |
|---|---|---|
| 指19 `MET_GOV_19` Critical event capture coverage / 关键事件采集覆盖率 | Retrieved critical events passing baseline validation ÷ expected events from reliable producer inventory or controlled event contract. / 已取得且通过基础校验关键事件数 ÷ 可靠生产者清单或受控事件契约确认应有事件数。 | Producer inventory, sequence, node state; receiver logs alone usually leave global denominator unknown. / 生产者清单、序号与节点状态；仅接收日志通常无法确定总体分母。 |
| 指20 `MET_GOV_20` Divergent identity conflicts / 同标识异内容冲突数 | Count tenant/event IDs with multiple distinct payloads; not count of transport copies. / 计同租户事件标识对应多个不同载荷的标识数，不计传输副本数。 | Original events/digests; ordinary retransmission is not conflict; deduplication must not erase divergence. / 原事件与摘要；普通重传不是冲突，去重不得隐藏异内容。 |
| 指21 `MET_GOV_21` Provenance completeness / 来源链完整率 | Fact entries with original source, version, exact association, verification path ÷ fact entries requiring provenance. / 有原始来源、版本、精确关联及核验路径的事实条目数 ÷ 应带来源事实条目数。 | Fact inventory and evidence references; hypotheses do not become verified facts. / 事实清单与证据引用；假设不成为已核验事实。 |
| 指22 `MET_GOV_22` Required field completeness / 关键字段完整率 | Obtained field items satisfying current node contract ÷ field items required by applicable states. / 满足当前节点契约的已取得字段项数 ÷ 适用状态应有字段项数。 | Versioned field contracts; non-applicability needs evidence, not a missing value. / 版本化字段契约；不适用须依据，不得因缺值豁免。 |
| 指23 `MET_GOV_23` Association ambiguity / 关联歧义率 | Events requiring linkage but lacking one unique target proposal/action ÷ all events requiring linkage. / 需关联却无法唯一绑定目标提案或动作的事件数 ÷ 需关联事件总数。 | Association graph/event contract; erroneous cross-tenant linkage is separately severe. / 关联图与事件契约；跨租户误关联另列严重问题。 |
| 指24 `MET_GOV_24` Evidence validity / 证据有效率 | Required evidence meeting target, content version, freshness, authenticated source ÷ all evidence items required for current decision. / 满足对象、内容版本、时效与来源核验的证据项数 ÷ 当前判定必需证据项数。 | Evidence and exact current snapshot; historically valid does not mean currently valid. / 证据与精确当前快照；历史有效不代表当前有效。 |
| 指25 `MET_GOV_25` Ingestion latency / 事件采集延迟 | Ingestion time minus trustworthy occurrence time; p95 and maximum over valid samples. / 接收时间减可信发生时间，在有效样本上报p95与最大值。 | Source/collector clocks; negative or unknown-clock values remain separate anomalies, never zero. / 来源与采集时钟；负值或时钟不明单列异常，不能记零。 |
| 指26 `MET_GOV_26` Qualified evidence enrichment / 合格证据补全率 | Due retrievable-evidence gaps closed after receiver verification against original condition ÷ all due gaps of that class. / 经接收方核验且满足原条件关闭的到期可补证缺口数 ÷ 此类全部到期缺口数。 | Gap/evidence/adoption records; unperformed facts excluded from this denominator but separately reported; unreachable sources stay in known denominator. / 缺口、证据与采纳记录；事实未发生类不入此分母但须单报，已知来源不可达项仍留分母。 |
| 指27 `MET_GOV_27` Evidence enrichment duration / 证据补全耗时 | Qualified closed gaps: creation to verified closure duration distribution. / 合格关闭缺口从创建至核验关闭的时长分布。 | Gap/closure history; separately report unresolved ages to avoid only showing fast completions. / 缺口与关闭历史；未决年龄另报，避免只展示快完成样本。 |
| 指28 `MET_GOV_28` Patch adoption / 补丁采纳率 | Fully accepted patches ÷ patches with explicit completed disposition; partially accepted fields additionally reported as a field ratio. / 完全采纳补丁数 ÷ 已获明确处理结果的补丁数；部分采纳另报字段比例。 | Patch/per-field receipts; pending or pending-human without disposition remain pending, not discarded; adoption is not factual correctness. / 补丁与逐字段回执；待处理或尚无结论的待人工另列，不能丢弃；采纳不等于事实正确。 |
| 指29 `MET_GOV_29` Unauthorized patch attempts / 越权补丁尝试数 | Count patches attempting non-whitelisted fields, cross-tenant objects, or forged original records. / 计尝试改非白名单字段、跨租户对象或伪造原件的补丁数。 | Receiver validation records; a rejected attempt is not an actual business effect. / 接收器校验记录；被拒尝试不等于已造成业务影响。 |
| 指30 `MET_GOV_30` Reviewed alert precision / 经复核告警准确率 | Independently reviewed alerts confirmed correct ÷ independently reviewed alerts. / 独立复核确认正确的告警数 ÷ 独立复核告警总数。 | Review verdict and sampling method; cannot infer missed-alert rate, no truth means unknown. / 复核结论与抽样方法；不能推断漏报率，无真值则未知。 |

### Workflow and probe operation / 工作流与探针运行

| ID and name / 编号与名称 | Formula or aggregation / 公式或聚合口径 | Authority and limits / 来源与边界 |
|---|---|---|
| 指31 `MET_GOV_31` First route accuracy / 首次路由命中率 | Initial automatic/human/deny/degrade route matching independent expected branch ÷ actions with routing truth. / 首次自动、人工、拒绝或降级分支符合独立真值的动作数 ÷ 有路由真值动作数。 | Historical policy, routing, test/review truth; final observed branch is not its own truth label. / 历史策略、路由及测试或复核真值；最终执行分支不能当自身真值。 |
| 指32 `MET_GOV_32` First pass success / 首轮通过率 | Independently valid due demands whose first proposal/attempt obtained valid authority and verified on-time success without rework ÷ all independently valid due demands. / 独立确认有效且到期需求中，首版首次尝试即有效授权、按期核实成功且无返工的动作数 ÷ 此类全部到期动作数。 | Valid-demand inventory, proposal/decision/attempt/verification; due unresolved counts as not passed, not-yet-due separate, absent valid-demand inventory → unknown. / 有效需求清单、提案、裁决、尝试与核验；到期未决算未通过，未到期单列，无有效需求清单则未知。 |
| 指33 `MET_GOV_33` Retry amplification / 重试放大率 | Actual attempts for a logical tool-operation class ÷ operations of that class called at least once. / 同类逻辑工具操作实际尝试总数 ÷ 至少调用一次的该类逻辑操作数。 | Call records/operation IDs; single call baseline is 1; separate reads, writes, and business redo. / 调用记录与操作身份；正常单次为1，读、写及业务重做分计。 |
| 指34 `MET_GOV_34` Human intervention / 人工介入率 | Tasks with any human approval or manual exception handling ÷ accepted tasks in same period. / 发生人工审批或人工异常处置的任务数 ÷ 同期受理任务数。 | Task/approval/exception records; each task once, distinct from interruption count. / 任务、审批与处置记录；每任务只计一次，区别于打断次数。 |
| 指35 `MET_GOV_35` Probe overhead / 探针附加开销率 | (Matched execution duration with probe − duration without probe) ÷ duration without probe; also report probe resources. / 匹配条件下启用与未启用探针执行耗时差 ÷ 未启用探针耗时，另报探针资源。 | Controlled comparison or explainable baseline; no baseline → unknown ratio and own cost only; zero baseline cannot yield a ratio. / 受控对照或可解释基线；无基线则比例未知，仅报自身成本，零基线也不能求比例。 |
| 指36 `MET_GOV_36` Feedback receipt coverage / 反馈回执覆盖率 | Due feedback requests with valid itemized handling receipts ÷ all feedback requests whose deadlines have passed. / 具备有效逐项处理回执的到期反馈请求数 ÷ 全部到期反馈请求数。 | Requests and receiver receipts; communication disposition does not establish risk elimination. / 请求与接收方回执；沟通有结论不等于风险消除。 |

No universal pass thresholds are defined. A safety violation is not offset by high average success; efficiency metrics cannot justify skipped approval, recoding unknown as failure, or shrinking a denominator. / 不定义脱离场景的统一合格阈值。安全违规不被高平均成功率抵消；效率指标不能证明可跳过审批、把未知改失败或缩小分母。

Constructed arithmetic checks only: five authoritative allow receipts, four bound, one missing → `MET_GOV_01 = 4/5 = 80%`; duplicate transport of a complete event leaves that unchanged. Four due retrievable gaps, two verified closed, one patch merely sent, one source unreachable → `MET_GOV_26 = 2/4 = 50%`. These numbers are not runtime measurements. / 仅构造公式例：权威五次放行四次绑定、一次缺失，绑定覆盖率80%；完整事件重复传输不改结果。四个到期可补证缺口，两个核验关闭、一个仅发补丁、一个来源不可达，合格补全率50%。这些不是运行测量值。

<a id="acceptance"></a>
## Acceptance designs / 验收设计

All cases below are **design cases, not executed runtime tests**. An integration must preserve input fixture, expected behavior, actual outcome, and supporting evidence before marking any case passed. Document coverage checks do not verify authentication, atomicity, dispatch behavior, metric computation, or production safety. / 下列均为**设计用例，未执行运行时测试**。集成须留存输入夹具、期望、实际与证据后才可标通过；文档覆盖检查不验证认证、原子性、派发、指标计算或生产安全。

| Case / 用例 | Input or fault / 输入或故障 | Expected outcome / 预期结果 |
|---|---|---|
| 探验01 | Allow receipt missing policy binding. / 放行回执缺策略绑定。 | Exclude from complete numerator, retain known denominator, open gap. / 不计完整分子，保留已知分母并开缺口。 |
| 探验02 | Current policy only, no historical snapshot. / 只有当前策略，无历史快照。 | Historical policy unknown; no retroactive approval inference. / 历史策略未知，不反推旧批准。 |
| 探验03 | Same event delivered three times. / 同事件三次传入。 | Count once; preserve delivery retry metadata. / 只计一次，保留传输重试信息。 |
| 探验04 | Same event ID, divergent payload. / 同标识异载荷。 | Quarantine conflict; never latest-wins. / 隔离冲突，不以最新覆盖掩盖。 |
| 探验05 | Result arrives before submission event. / 结果先于提交事件到达。 | Mark lateness/missing predecessor and recompute after capture; no invented submission. / 标迟到或缺前驱，补齐重算，不造提交。 |
| 探验06 | Source clock yields negative duration. / 来源时钟导致负耗时。 | Clock anomaly excluded from normal percentiles, retained in quality report. / 时钟异常不入正常百分位，质量报告保留。 |
| 探验07 | Same user name/amount, different proposals. / 同名用户同金额不同提案。 | Approval cannot transfer; unresolved association. / 不复用批准，保留关联不明。 |
| 探验08 | Cross-tenant patch. / 跨租户补丁。 | Reject with no target observation mutation. / 拒绝且不得写入目标观测层。 |
| 探验09 | Business API only acknowledges request. / 业务仅返回请求已接收。 | Submitted/accepted request is not verified success. / 请求接收不标业务成功。 |
| 探验10 | Timed-out call later confirmed successful. / 超时后查明已成功。 | Reference original request's authoritative result; do not retry the business effect. / 提交原请求权威结果引用，不业务重试。 |
| 探验11 | No authoritative outcome query. / 无业务结果查询能力。 | Preserve unknown; duplicate rate cannot be declared zero. / 保留未知，重复率不得称零。 |
| 探验12 | Genuine prior approval omitted by collection. / 原批准存在但漏采。 | Add original reference with discovery time and original gap preserved. / 补原引用，保留发现时间与原缺口。 |
| 探验13 | Approval created after action. / 批准发生在操作之后。 | Preserve temporal violation evidence; no backdated approval. / 保留时序违规证据，不补成事前批准。 |
| 探验14 | Asked to invent missing approval. / 要求模型生成缺失批准。 | Report unperformed fact and request new governed work. / 报事实未发生并请求受治理补做。 |
| 探验15 | Patch writes success or ledger amount. / 补丁改付款成功或额度。 | Reject non-whitelisted mutation. / 拒绝非白名单写入。 |
| 探验16 | Target proposal changed before old patch arrival. / 提案变化后旧补丁到达。 | Return conflict; do not overwrite new target. / 返回冲突，不覆盖新版本。 |
| 探验17 | Fresh patch wraps expired evidence. / 新补丁携带过期证据。 | Evidence remains expired. / 证据仍过期。 |
| 探验18 | Patch sent, receipt absent. / 已发补丁无回执。 | Pending/unresolved; no gap closure. / 仍待处理，不关缺口。 |
| 探验19 | Receiver adopts selected fields only. / 仅采纳部分字段。 | Partial adoption; retain each unresolved gap. / 部分采纳，逐项保留未解决缺口。 |
| 探验20 | Reliable denominator unavailable. / 可靠分母缺失。 | Metric unknown, with observed sample scope. / 指标未知并报已见样本范围。 |
| 探验21 | Trusted population has no applicable members. / 可信总体无适用样本。 | Not applicable, never 100%. / 不适用，不输出100%。 |
| 探验22 | Five authoritative allow receipts, one unbound. / 权威五次放行一次缺绑定。 | Binding coverage is 4/5 = 80%; missing member stays in denominator. / 绑定覆盖率4÷5＝80%，缺失项不删分母。 |
| 探验23 | Parallel branches individually within limit, aggregate over. / 并行单项未超限但合计超限。 | Detect on authoritative shared account/parent or business subject; no per-run false reassurance. / 按权威共享账户、父级或主体识别，不因单运行未超限称安全。 |
| 探验24 | Authorized policy limit increase. / 合法策略升限。 | Preserve change and approval; increase alone is not violation. / 记录变更与审批，不仅因升限判违规。 |
| 探验25 | No independent review truth. / 无独立复核真值。 | Redundant approval, alert precision, and route accuracy unknown. / 冗余审批率、告警准确率及路由命中率未知。 |
| 探验26 | Probe re-ingests its own output. / 再采集探针自身输出。 | Request causation and deduplication prevent infinite enrichment. / 请求因果关联与去重避免无限补全。 |
| 探验27 | Offline audit without execution peer. / 离线运行无执行侧。 | Report and candidate patches only; no claimed adoption or stop. / 输出报告与候选，不称已采纳或已停止。 |
| 探验28 | Exhausted query budget or denied access. / 查询预算耗尽或无权读取。 | Stop automatic retrieval, assign unresolved items and owner. / 停止自动查询，明确未解决项与负责人。 |

<a id="constraints"></a>
## Failure, privacy, and stopping / 失败、隐私与停止

| Failure or severity / 失败或等级 | Required handling / 必需处理 |
|---|---|
| Confirmed unauthorized effects, excess admission, duplicates, or tampered critical records / 已证实越权效果、超额度准入、重复效果或关键记录篡改 | Urgent: preserve in-flight inventory and recommend scoped stopping to an authorized controller with human handling; only its receipt proves control execution. / 紧急：保留在途清单，向授权控制方建议局部停止并人工处置；仅其回执证明控制已执行。 |
| Missing high-risk prerequisites, growing unknowns, policy conflicts, unverifiable revocation / 高风险前提缺证、未知积压、策略冲突或撤销不可核验 | High: request verification or governed pause; missing evidence is not itself a confirmed violation. / 高：请求核验或受治理暂停；缺证本身不是已证实违规。 |
| Late collection, ambiguous links, rejected patches, deteriorating quality / 采集迟到、关联歧义、补丁拒绝或质量下降 | Medium: bounded evidence retrieval and adapter/mapping repair. / 中：限期补证并修复适配器或映射。 |
| Performance or noncritical field deficiencies / 性能或非关键字段不足 | Low: improve without weakening safety boundaries. / 低：优化但不放松安全边界。 |
| Probe unavailable or no critical capture guarantee / 探针不可用或关键采集无保障 | Publish probe health, save cursor and pending work, report coverage unknown; execution retains local controls and blocks necessary high-risk dispatch per configured policy if mandatory audit cannot persist. / 输出健康、保存游标及未决项、报告覆盖未知；执行保持本地控制，必需审计无法持久化时按配置策略阻断相应高风险派发。 |
| Missing source, denied access, deadline or retry/query budget exhausted / 无证可补、权限不足、期限或重试及查询预算耗尽 | Stop that automated path, preserve unresolved terminal and accountable next steps; no access bypass or endless feedback loop. / 停止该自动路径，保留未解决终态与负责人的下一步，不绕权或无限反馈。 |

Severity labels above are design semantics; configure business-specific amounts, expiry, waiting limits, and thresholds. Keep safety measures separate from efficiency objectives, retain historical source versions, and never let an attractive aggregate score hide unresolved or excluded populations. / 上述等级为设计语义，金额、有效期、等待时限及阈值须业务配置。安全与效率目标分开，保留历史来源版本，不让好看的总体分数隐藏未决或排除样本。
