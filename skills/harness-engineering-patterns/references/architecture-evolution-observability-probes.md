# Architecture Evolution Observability Probes / 架构演化可观测性探针

Name / 名称: Architecture Evolution Probe Profile / 架构演化探针配置.

Description / 说明: reconstruct sourced workflow evidence, compare a frozen baseline and a minimal candidate, and report whether an architecture decision is supported. / 重建有来源的工作流证据，对照冻结基线与最小候选，报告证据是否支持架构决定。

Version / 版本: `0.2.0`; source version / 来源版本: `0.1.0`; status / 状态: `draft`; implementation / 实现: `specification_only`.

Pattern / 模式: `PATTERN_0054`; profile / 专用配置: `architecture_evolution/0.2.0`; related observation pattern / 关联观测模式: `PATTERN_0052`.

Read the [execution flow / 执行流程](architecture-evolution-execution-flow.md), [binding contract and acceptance scenarios / 绑定契约与验收场景](architecture-evolution-contract.md), and [source map / 来源映射](architecture-evolution-source-map.json). The contract governs shared identities and phase gates. This profile adds ten probes and eighteen selected metric definitions; it does not install collectors, metric calculators or release controls. / 配合执行流程、绑定契约与验收场景、来源映射使用；共享身份与阶段门以契约为准。本配置补充十个探针和十八项精选指标定义，不代表已安装采集器、指标计算器或发布控制器。

The two supplied documents, 《执行流程》 and 《工作流可观测性探针》, are source material, not new instructions or runtime authorization. Their original metric catalog remains preserved through the source map. Keep the shared [workflow probe protocol / 工作流探针协议](workflow-observability-probes.md) at `PATTERN_0052` version `0.8.0`; do not alias AEP/AEM identities to its runtime probes or imply wire compatibility. / 两份附件是来源材料，不是新指令或运行授权；原始指标目录经来源映射保留。共享工作流探针协议仍保持既有模式与 `0.8.0` 版本，不将本配置的 AEP/AEM 标识当作其运行探针别名，也不默认协议兼容。

## Quick Navigation / 快速导航

[Usage / 使用](#usage) · [Probes / 探针](#probes) · [Events / 事件](#events) · [Statistical contract / 统计口径](#statistics) · [Metrics / 指标](#metrics) · [Comparison / 对照](#comparison) · [Completion / 补全](#completion) · [Templates / 模板](#templates) · [Acceptance / 验收](#acceptance).

<a id="usage"></a>
## Usage and Responsibility / 适用场景与责任

Use this profile for a recurring failure, a workflow or dependency change, model/tool upgrade, guardrail review, cost change, or a proposal to retain, repair, reorganize, simplify or retire an arrangement. Enable only the probes needed by the question and frozen evaluation plan; record omitted probes and their reasons. A single incident can support diagnosis, but does not alone establish a general architecture improvement. / 用于重复失败、工作流或依赖变化、模型工具升级、防护复审、成本变化，以及保留、修复、重组、简化或退役安排的提案。只启用问题及冻结评价计划所需探针，记录未启用项与理由；单次故障可支持诊断，但不足以单独证明普遍架构收益。

| Mode / 模式 | Inputs and behavior / 输入与行为 | Output boundary / 输出边界 |
| --- | --- | --- |
| Standalone offline / 独立离线 | Read supplied logs, contracts, snapshots and authoritative receipts; reconstruct a completed, interrupted or unresolved run. / 读取提供的日志、契约、快照与权威回执，重建完成、中断或未决运行。 | Return a sourced diagnostic package and unresolved gaps. Inaccessible evidence remains unavailable. / 返回有来源诊断包及未决缺口，不可访问证据保持不可取得。 |
| Standalone online / 独立在线 | Read events or explicitly permitted authoritative sources within the configured budget. / 在配置预算内读取事件或明确允许的权威来源。 | Append observations to the observation store; do not change workflow or business state. / 仅向观测存储追加观察，不修改工作流或业务状态。 |
| Execution collaboration / 与执行流程协作 | Accept a bound request at E0–E9, inspect evidence, and return findings, metrics and proposed next steps. / 在 E0–E9 接收绑定请求、检查证据并返回发现、指标与下一步建议。 | Execution/governance independently decides whether to continue, investigate, pause, release or roll back. / 执行治理方独立决定继续、补查、暂停、发布或回滚。 |

Probes own collection, provenance, gaps and recommendations. They cannot approve a release, grant access, alter a baseline, rewrite an acceptance result, change production, dispatch retries or perform compensation. `permissions.read_only: true` restricts an already authorized read; it does not create permission. A configured execution gate may consume a probe result under its own policy and authority. / 探针负责采集、来源、缺口和建议，不能批准发布、赋权、改基线、改写验收结果、修改生产、派发重试或执行补偿。只读标志约束已有授权的读取，不自行授予权限；配置好的执行门可在自身策略与权限下使用探针结果。

<a id="probes"></a>
## Ten Probes / 十个探针

Every finding binds the evolution, exact target revision, run/attempt where applicable, source references, affected scenario/risk, fact/inference/hypothesis classification, owner and proposed return point. Anomaly thresholds come from the versioned evaluation plan; this document supplies no universal passing threshold. / 每项发现绑定演化、精确目标修订、适用的运行尝试、来源引用、受影响场景风险、事实推断假设分类、责任人与建议返回点。异常阈值取自版本化评价计划，本文件不提供通用通过阈值。

| ID | Name and placement / 名称与接入位置 | Evidence and checks / 证据与检查 | Output / 输出 |
| --- | --- | --- | --- |
| AEP01 | Scope and baseline / 范围与基线；E0–E1 | Trigger, objective, exclusions, scenario/risk manifest, baseline artifact versions, input cohort and original design rationale. Detect a moving baseline or scope without provenance. / 触发、目标、排除项、场景风险清单、基线制品版本、输入总体与原设计理由；发现漂移基线或无来源范围。 | Missing bindings and freeze defects; recommend return to E0/E1. / 缺失绑定及冻结缺陷，建议回 E0/E1。 |
| AEP02 | Evidence and freshness / 证据与时效；E1–E3 | Authoritative originals, rule versions, timestamps, expiry, required acceptance evidence and conflicts. Distinguish an inaccessible source from a source that confirms absence. / 权威原件、规则版本、时间、过期、必要验收证据与冲突；区分来源不可访问与来源确认不存在。 | Evidence inventory and gaps; AEM04–AEM06; unsupported conclusions remain unknown. / 证据清单、缺口及相关指标，无依据结论保持未知。 |
| AEP03 | Causal reconstruction / 因果重建；E2 | Run, attempt, span, producer epoch/sequence, lifecycle events and explicit parent/consumption links. Detect duplicates, gaps, impossible transitions and late conflicts. / 运行、尝试、跨度、生产者代次序号、生命周期与显式父级消费关系；检查重复、缺段、不可能迁移及迟到冲突。 | Partial-order timeline, missing intervals and earliest provable deviation; never fill an absent event with a guessed success. / 偏序时间线、缺失区间与最早可证实偏差，不猜测补成成功事件。 |
| AEP04 | Handoff and exact values / 交接与精确值；E2–E4 | Producer output and actual consumer input, schemas, target IDs, digests, permissions and versioned field maps. Compare structured state, not just matching summaries. / 上游输出与实际下游输入、结构、对象号、摘要、权限与字段映射版本；比对结构化状态，不只比较摘要。 | First mismatched field/object/version and impacted consumers; AEM07. / 首个失配字段对象版本及受影响消费者。 |
| AEP05 | Recovery and bounded progress / 恢复与有界进展；E2–E4/E8 | Retry lineage, loop budgets, input differences, new evidence, checkpoints, effect receipts and takeover records. Differentiate local retry, investigation, replanning and approval wait. / 重试谱系、循环预算、输入变化、新证据、检查点、副作用回执与接管记录；区分局部重试、调查、重规划及审批等待。 | Unproductive loops, duplicate-effect risks and unresolved recovery obligations; AEM08–AEM11. / 无效循环、重复效果风险与未决恢复责任。 |
| AEP06 | Hypothesis and minimal candidate / 假设与最小候选；E3–E4 | Earliest deviation, competing explanations, discriminating checks, original design rationale, candidate diff and unchanged invariants. Check whether a data/rule/tool defect is mislabeled as architecture failure. / 首偏差、竞争解释、区分性检查、原设计理由、候选差异与保持的不变量；核查是否把数据规则工具缺陷误归为架构问题。 | Supported/refuted/unverified hypotheses, confounders and smaller alternatives; no speculative root cause promoted to fact. / 有支持、被否、未验证的假设、混杂因素与更小替代项，不将推测根因升格为事实。 |
| AEP07 | Comparable evaluation and regression / 可比评价与回归；E5–E6 | Frozen cases, assignment/pairing, reference results, validators, environments, seeds where meaningful, sample sizes and exclusions. Include old failures, old successes, counterexamples, boundary and high-risk cases. / 冻结用例、分组配对、参考结果、验收器、环境、适用的种子、样本量与排除项；覆盖旧失败、旧成功、反例、边界及高风险。 | Coverage, paired differences, uncertainty and invalid comparisons; AEM01–AEM03/AEM15–AEM18. / 覆盖、成对差异、不确定性及无效对照。 |
| AEP08 | Acceptance and true completion / 验收与真实完成；E6–E8 | Business rule results, designated authority, exact object/version, mandatory evidence, final effects and unresolved severe issues. Technical success cannot replace business acceptance. / 业务规则结果、指定权威、精确对象版本、必要证据、最终效果与严重未决项；技术成功不能替代业务验收。 | Acceptance coverage paired with success, critical errors by severity, unresolved effects and false completion findings; AEM01–AEM05/AEM10. / 与成功率配套的验收覆盖、分严重度关键错误、未决效果与假完成发现。 |
| AEP09 | Release and post-release change / 发布与发布后变化；E7–E8 | Release cohort, release/rollback artifacts, exposure, live control epoch, migration and compatibility, outcome-maturation window and incident receipts. Observe stop requests and their acknowledged effect separately. / 发布总体、发布回滚制品、暴露量、实时控制代次、迁移兼容、结果成熟窗口与事故回执；分开观测停止请求及已确认效果。 | Version/risk-specific deterioration, rollback/compensation gaps and stale controls; recommend authorized review, never self-apply a change. / 分版本风险退化、回滚补偿缺口与陈旧控制；建议授权复核，不自行变更。 |
| AEP10 | Decision value and reassessment / 决定价值与复评；E9 | Comparable quality, residual risk, latency, complete cost coverage, human effort, guard contributions, ADR rationale/owner and reassessment trigger/date. / 可比质量、残余风险、延迟、完整成本覆盖、人工量、防护贡献、ADR 理由责任人与复评触发日期。 | Evidence supporting retain/repair/reorganize/simplify/retire, limits and open obligations; AEM11–AEM18. / 支持保留修复重组简化退役的证据、限制及未决责任。 |

<a id="events"></a>
## Event Model and Reconstruction / 事件模型与重建

An event is an immutable observation, not proof of a successful transition merely because its name says “success”. Retain the original record and versioned interpretation separately. References use `{id, version, digest}` where the contract requires artifact bindings; a digest verifies content identity, not authenticity or truth. / 事件是不可变观察，名称含“成功”不构成成功迁移证明；分别保存原记录及版本化解释。契约要求的制品绑定采用 `{id, version, digest}`；摘要校验内容身份，不证明来源真实性或业务真实性。

| Field group / 字段组 | Required content and semantics / 必需内容与语义 |
| --- | --- |
| Event identity / 事件身份 | `event_id`, `event_schema_version`, `profile`, `event_type`, `payload_digest`; exact duplicate IDs/content deduplicate, same ID/different content creates a conflict. / 事件号、结构版本、配置、类型与载荷摘要；同号同内容去重，同号异内容记冲突。 |
| Evolution binding / 演化绑定 | `evolution_id`, `baseline_ref`, `candidate_ref`, `evaluation_plan_ref`, `release_ref`, `target_ref`, `expected_control_epoch`; pre-creation null references need a reason and cannot satisfy a later gate requiring the artifact. / 演化、基线、候选、评价、发布、目标及预期控制代次；产生前空引用须说明理由，不能满足后来必须具备该制品的门。 |
| Execution correlation / 执行关联 | `tenant_id`, `environment`, applicable `workflow_id`, `workflow_version`, `scenario_id`, `scenario_version`, `run_id`, `node_id`, `logical_operation_id`, `attempt_id`, `attempt_number`, `span_id`, `parent_span_id`, typed `links`. Pure outer evolution events retain their evolution identity and mark inapplicable business run/node fields null with reasons; never invent them. Retries use new attempts, linked to the original logical operation. / 租户环境及适用的工作流场景版本、运行节点、逻辑操作、尝试号及次数、跨度父跨度与类型化关系；纯外环演化事件保留演化身份，不适用的业务运行节点字段为空并注明理由，不得虚构；重试创建新尝试并关联原逻辑操作。 |
| Producer order / 生产者顺序 | `producer_id`, `producer_epoch`, `sequence_no`; sequence orders only one producer/epoch stream unless a separately proven serialized allocator exists. `producer_epoch` is a restart generation, distinct from the execution control epoch. / 生产者、重启代次、序号；序号默认仅在单个生产者代次流内有序，除非另有可证明串行分配器；重启代次不同于执行控制代次。 |
| Time / 时间 | `occurred_at`, `observed_at`, timezone/precision, clock source, skew bound when known; optional same-clock monotonic duration. Occurrence time and collector receipt time serve different purposes. / 发生与观测时间、时区精度、时钟来源、已知偏差界及可选同钟单调耗时；发生时间与采集接收时间不可混用。 |
| Versions / 版本 | Model, prompt, tool, rule, data snapshot, configuration, node contract and validator versions; record explicit unknowns and raw version labels. / 模型、提示词、工具、规则、数据快照、配置、节点契约与验收器版本；保留明确未知及原始版本标签。 |
| Sourced payload / 有来源载荷 | `input_refs`, `output_refs`, `tool_receipt_refs`, `evidence_refs`, source record locator/version/digest, observed source identity, `source_kind`, access scope, retention/expiry, redaction policy. Keep controlled references and safe summaries, not secrets or private chain-of-thought. / 输入输出、工具回执、证据及来源记录位置版本摘要、来源身份类型、访问范围、留存过期与脱敏策略；存受控引用安全摘要，不存密钥或私密思维过程。 |
| Separate states / 独立状态 | Raw technical status/error, mapped technical status, business acceptance, effect confirmation and observation quality; mapping rule/version and evidence for each. / 原始技术状态错误、映射技术态、业务验收、效果确认与观测质量，各自保存映射规则版本及证据。 |
| Measured resources / 实测资源 | Duration, cost components, units/currency/rate version and coverage; label measured, estimated, partial or unknown. / 耗时、成本构成、单位币种费率版本与覆盖，标明实测、估算、部分或未知。 |

Reconstruct by authenticated identity and explicit `parent_of`, `consumed_by`, `triggered_by`, `retries`, `confirmed_by`, `supersedes` and `corrects` links. First apply known local ordering, then causal links; concurrent events remain unordered. Clock sorting is only a display aid. A trace match or nearby timestamp alone cannot prove causal or approval relationships. / 根据可信身份及显式父级、消费、触发、重试、确认、替代、更正关系重建；先保留已知局部顺序，再组合因果边，并发事件保持无序。时钟排序只用于展示；追踪号相同或时间接近不证明因果或审批关系。

Detect missing sequence ranges, unmatched starts/ends, unlinked attempts, stale epochs and incompatible versions. Retain duplicate counts without double-counting outcomes. Quarantine conflicting identities; heuristic joins carry their rule, confidence and alternatives and remain inferred until corroborated. If several earliest deviations are incomparable, report the earliest provable frontier and uncertainty interval rather than inventing one global first event. / 检查序号缺段、未配对起止、孤立尝试、旧代次与不兼容版本；保留重复数但不重复计算结果。冲突身份隔离；启发式关联保留规则置信与候选，在佐证前保持推断。多个最早偏差无法比较时，报告最早可证实偏差集合与不确定区间，不虚构全局唯一首事件。

Late evidence appends a new report revision with a correction link, affected metric IDs and revised cutoff. It does not silently overwrite sealed findings, execution state or historical acceptance. A missing side-effect receipt means the effect is unknown, not absent. / 迟到证据通过带更正关系、受影响指标号与新截止时间的新报告修订追加，不静默覆盖已封存发现、执行态或历史验收；缺少副作用回执表示效果未知，不表示未发生。

<a id="statistics"></a>
## Statistical Contract / 统计口径契约

Freeze the statistical unit, eligible population, inclusion/exclusion rules, versions, scenario/risk strata, calendar interval `[start, end)`, observation cutoff, outcome-maturation rule, sampling design, thresholds and comparison method before evaluating the candidate. A run, node, attempt, call, handoff and evaluation case are different units; never interchange their denominators. / 评价候选前冻结统计单位、应纳入总体、纳入排除规则、版本、场景风险分层、日历区间 `[start, end)`、观测截止、结果成熟规则、采样设计、阈值与对照方法。运行、节点、尝试、调用、交接和评价用例是不同单位，分母不可互换。

Define the following scoped populations; each report supplies the concrete manifest and cutoff used. / 定义下列范围内总体，每份报告都给出使用的具体清单及截止时间。

- `S`: started runs in the frozen intake cohort whose planned outcome-maturation deadline has passed by the cutoff; include failed, cancelled, unresolved and unaccepted runs according to the predeclared eligibility rule. Report not-yet-mature runs separately. A slow failure must not disappear because its completion event is absent. / `S` 为冻结进入总体中，预设结果成熟期限在截止前已到的启动运行；按事先资格规则保留失败、取消、未决及未验收项，另报未成熟运行。不能因缺完成事件而删掉慢失败。
- `A`: runs in `S` with an authoritative, definitive pass/fail business acceptance under the frozen rubric; `P` is the passing subset. Pending, unknown or conflicting results are outside `A` but remain in `S`. / `A` 为 `S` 中依冻结量规获得权威明确通过或失败验收的运行，`P` 为通过子集；待定、未知或冲突不进入 `A`，但保留在 `S`。
- `N`, `L`, `H`, `R`: independent manifests of executed logical nodes, loop-bearing runs, required handoffs, and required event instances. `R` comes from the frozen workflow and actual permitted branches, not merely received logs; justified skips are explicit events. / `N`、`L`、`H`、`R` 分别为独立建立的已执行逻辑节点、有循环运行、必需交接与必需事件实例清单。`R` 来自冻结工作流及实际获准分支，不只来自已收到日志；合理跳过也须显式记录。
- `C`: planned evaluation cases with mandatory baseline/candidate arms and repetitions; `C_p` contains cases with both comparable, mature, valid results. Old-success `C_s` and old-failure `C_f` labels are fixed before candidate evaluation, using authoritative baseline evidence. / `C` 为计划评价用例及必需基线候选臂和重复次数；`C_p` 含两侧均可比、成熟且有效的用例。旧成功 `C_s` 与旧失败 `C_f` 标签须据权威基线证据在候选评价前固定。

Every metric result records definition/version, unit, numerator, denominator or distribution sample count, population manifest, time/maturity window, stratum, evidence references, missing/unknown/conflict counts, coverage, sample size and uncertainty/limitations. A known empty denominator yields `not_applicable` with `value: null`; an unavailable denominator or required input yields `unknown`, also null. Zero is a measured count; a nonzero denominator with zero successes can yield a real 0%. / 每项指标记录定义版本、单位、分子分母或分布样本数、总体清单、时间成熟窗口、分层、证据引用、缺失未知冲突数、覆盖、样本量及不确定性限制。已知空分母为不适用且值为空，分母或必要输入不可得为未知且值为空；零是实测计数，非零分母下成功数为零可以产生真实的 0%。

Distinguish a documented absent event (`missing`), an unresolved truth (`unknown`), a confirmed zero and a rule-backed `not_applicable`. Do not mark a ratio known merely because the available subset is complete. When a verified subset is reported, label the conditional subset explicitly and also report full-population coverage. Mandatory controls, critical errors and acceptance evidence must not be sampled away. / 区分有明确缺口的未采集、真值未明的未知、已确认零及有规则依据的不适用；不能仅因可取得子集完整，就称总体比率已知。报告已核实子集时明确其条件范围并同时报告总体覆盖；不可通过采样省略强制控制、关键错误和验收证据。

<a id="metrics"></a>
## Selected Metrics / 精选指标

`AEM01`–`AEM18` are versioned specification locators, not executable registrations. “Source” below refers to the supplied probe document's section; “extended” identifies an explicit refinement or new comparison definition. Other source metrics, including freshness, timeout, rollback and field completeness, may be added by a versioned scenario plan without changing these definitions. / AEM 编号是版本化规格定位符，不是可执行注册。“来源”指附件探针对应章节，“扩展”明确区分细化或新增对照口径；场景计划可版本化增选新鲜度、超时、回滚及字段完整等来源指标，不得改写以下定义。

| ID | Name and unit / 名称与单位 | Numerator / 分子 | Denominator and interpretation / 分母与解释 | Provenance / 来源 |
| --- | --- | --- | --- | --- |
| AEM01 | Business success / 业务成功率；run / 运行 | `count(P)` / 通过验收运行数 | `count(A)`; always publish with AEM02 and `count(S)`, by risk/version. Success among reviewed survivors is not population success. / 已明确验收运行数；必须同时报验收覆盖及成熟总体，按风险版本分层；被验收幸存子集成功不代表总体成功。 | §5.1; matured cohort refinement / 成熟总体细化 |
| AEM02 | Acceptance coverage / 验收覆盖率；run / 运行 | `count(A)` / 获明确验收运行数 | `count(S)`; missing/pending/conflicting acceptance stays in denominator. A high AEM01 with low coverage cannot establish improvement. / 成熟应验收运行数；缺失待定冲突保留分母，低覆盖高成功不能证明改善。 | Extended from §5.1/§6 / 据业务指标与诊断规则扩展 |
| AEM03 | Critical business error / 关键业务错误率；run / 运行 | Accepted runs with at least one confirmed critical error, once per run and separately by severity/class / 存在已确认关键错误的验收运行数，单运行只计一次并另按严重度类别列示 | `count(A)`; publish AEM02, confirmed counts outside `A`, and unresolved suspected errors. An aggregate improvement never offsets a failing high-risk slice. / 明确验收数；同时报验收覆盖、验收外已确认错误及未决疑似项，总体改善不能抵消高风险分层失败。 | §5.1 |
| AEM04 | Result traceability / 结果可追溯率；completed run / 已完成运行 | Completed runs whose every required key conclusion resolves to a valid original / 全部必需关键结论均可定位有效原件的完成运行数 | All recorded completed runs in the cohort, including unverifiable ones; report completion coverage against `S` separately. / 总体内所有记录为完成的运行，含不可核验项；另报相对 `S` 的完成覆盖。 | §5.1 |
| AEM05 | Acceptance evidence completeness / 验收证据完整率；run / 运行 | Runs in `S` with all required fresh, verifiable acceptance evidence / `S` 中必要验收证据齐全新鲜可核验的运行数 | `count(S)`; evidence completeness is not a passing verdict. / 成熟应验收运行数；证据齐全不等于验收通过。 | §5.1 |
| AEM06 | Required-event coverage / 必需事件覆盖率；event instance / 事件实例 | Unique valid received instances matching the frozen required-event manifest / 匹配必需事件清单的唯一有效已接收实例数 | `count(R)`; report duplicate, late, conflicted and unmatched counts separately. If the expected manifest is unknown, coverage is unknown. / 应有事件实例数；另报重复迟到冲突未关联数，应有清单未知时覆盖未知。 | §5.3 observation coverage / 观测覆盖 |
| AEM07 | Handoff consistency / 交接一致率；handoff / 交接 | Checked handoffs with exact required field/object/version consistency / 必需字段对象版本完全一致的已检查交接数 | Checked handoffs with both original sides; also publish checked `÷ count(H)` and list uncheckable critical handoffs. / 双方原件齐备的已检查交接数，同时报已检查占必需交接覆盖并列不可查关键交接。 | §5.3 |
| AEM08 | Node retry / 节点重试率；logical node / 逻辑节点 | Logical nodes in `N` with at least one later attempt / `N` 中至少有一次后续尝试的逻辑节点数 | `count(N)`; retries do not create new logical-node denominator entries. Publish attempt counts and uncovered nodes separately. / 已执行逻辑节点数，重试不扩大逻辑节点分母；另报尝试数与未覆盖节点。 | §5.2 |
| AEM09 | No-progress loop / 无进展循环率；loop-bearing run / 有循环运行 | Runs in `L` reaching the frozen loop limit without new verifiable evidence or effective state change / 达预设循环上限而无新可核验证据或有效状态变化的运行数 | `count(L)`; publish open/censored loops and missing-round coverage; use a versioned progress rubric. / 有循环运行数；另报未闭合删失循环和轮次缺失覆盖，进展使用版本量规。 | §5.2 |
| AEM10 | Unexpected external effect / 非预期外部副作用率；run / 运行 | Executed runs with a confirmed unexpected external effect / 有已确认非预期外部效果的执行运行数 | Executed runs in the declared cohort; separately publish effect-confirmation coverage, unknown-effect runs and severity. No receipt is not proof of no effect. / 声明总体中的执行运行数；另报效果确认覆盖、效果未知运行和严重度，无回执不是无效果。 | §5.1 |
| AEM11 | Human takeover / 人工接手率；run / 运行 | Started runs requiring human operational takeover / 需要人工接管执行的启动运行数 | All started runs in the declared mature cohort; classify planned review separately from unplanned takeover and report missing handoff records. / 声明成熟总体中的启动运行数；计划评审与非计划接管分开并报告交接记录缺失。 | §5.2 |
| AEM12 | End-to-end latency / 端到端延迟；duration / 时长 | Distribution of authoritative terminal time minus start time, once per run / 每运行一次，权威终态时刻减开始时刻的分布 | Report `n`, median/p95 where supportable, known starts, observed terminals and right-censored runs at cutoff; not a ratio. Cross-clock uncertainty stays explicit. / 报样本数、可支持的中位数及 p95、已知开始终态及截止右删失运行，不是比率；跨钟不确定保持明确。 | §5.4 |
| AEM13 | Cost per run / 单任务成本；currency/run / 货币每运行 | Sum of model, tool, compute and human costs for all attempts of a run / 运行全部尝试的模型工具计算人工成本之和 | One logical run; show distribution and per-component coverage across the cohort. Partial coverage permits only a labeled observed subtotal. / 单个逻辑运行；给总体分布及逐构成覆盖，覆盖不足只能给标记清楚的已观测小计。 | §5.4 |
| AEM14 | Cost per accepted success / 每次成功成本；currency/success / 货币每成功 | Complete total execution cost of the same cohort, including failures, retries and human work / 同一总体的完整执行成本，含失败重试及人工 | `count(P)`; requires complete cost accounting and definitive acceptance for every eligible mature run, `count(A) = count(S)`. If either coverage is incomplete, value is unknown; separately report observed cost subtotal and acceptance coverage. / 通过数；要求成本全覆盖且每个成熟应验收运行均有明确验收，即 `count(A) = count(S)`。任一覆盖不全则值未知，另报观测成本小计与验收覆盖。 | §5.4 |
| AEM15 | Paired evaluation coverage / 成对评价覆盖率；case / 用例 | `count(C_p)` / 两侧可比成熟有效的用例数 | `count(C)`; separately report missing arm, invalid pairing, environment drift and required repetition coverage. / 计划用例数；另报缺失对照臂、无效配对、环境漂移与必需重复覆盖。 | Extended from §7 / 据对照验证扩展 |
| AEM16 | Old-success preservation / 旧成功保留率；case / 用例 | Cases in `C_s` with a candidate pass under the unchanged required rubric / `C_s` 中候选在未改变的必要量规下通过的用例数 | All planned `count(C_s)`; any unknown/missing outcome makes the primary value unknown/null. Report `verified_pass ÷ planned_count` only as a labeled lower bound, with confirmed failures and pending counts; never drop gaps. / 全部计划旧成功用例数；任何未知缺失结果使主值未知为空。另将已核实通过数除计划数明确标为下界，并报确认失败待定数，不删除缺口。 | Extended from §7 and execution §3 step 10 / 据对照及演化步骤扩展 |
| AEM17 | Old-failure repair / 旧失败修复率；case / 用例 | Cases in `C_f` whose candidate passes with verified resolution of the frozen failure condition / `C_f` 中候选通过且已核验解决冻结失败条件的用例数 | All planned `count(C_f)`; unknown/missing outcomes make the primary value unknown/null; a verified-pass/planned-count fraction is only a labeled lower bound. Run the paired baseline, report pending counts and AEM15; a changed passing test alone is not a repair. / 全部计划旧失败用例数；未知缺失使主值未知为空，已核实通过除计划数仅作明确下界。运行配对基线，报待定数与对照覆盖；仅通过改后测试不是修复。 | Extended from §7 and execution §3 step 10 / 据对照及演化步骤扩展 |
| AEM18 | Guard incremental detection / 防护边际检出增益；confirmed issue by severity / 分严重度确认问题 | Confirmed issues additionally caught by the with-guard arm versus the comparable without-guard arm; retain missed issues as well / 有防护臂相对可比无防护臂额外捕获的已确认问题，同时保留漏检问题 | Paired mature case count and exposure are reported; publish counts by severity and optional per-case difference, not an unqualified universal percentage. / 报成对成熟用例数及暴露量，分严重度给计数和可选逐例差异，不给无条件普遍百分比。 | §5.4 review gain plus §7 extension / 评审增益与对照扩展 |

<a id="comparison"></a>
## Comparison, Censoring and Interpretation / 对照、删失与解释

Business success always travels with acceptance coverage, evidence completeness, critical-error severity and sample size. If acceptance covers 10 of 100 eligible mature runs and all ten pass, report `AEM01 = 10/10` and `AEM02 = 10/100`, with ninety unresolved outcomes; never report “100% workflow success”. The numbers here illustrate arithmetic only, not measured project results. / 业务成功率必须同时报告验收覆盖、证据完整、关键错误严重度及样本量。100 个成熟应验收运行只验收 10 个且全部通过，应报成功 `10/10`、覆盖 `10/100` 和 90 个结果未决，不能称“工作流成功率 100%”。此处数字仅演示口径，不是项目实测结果。

Report baseline and candidate by scenario, risk, input difficulty/distribution, workflow/model/tool/rule version, environment, exposure and human involvement. Keep cancelled, failed, unknown and missing runs visible. Freeze comparator selection and minimum meaningful change before examining candidate results; report repeated looks and protocol changes. Pair on the same cases where possible, use an appropriate uncertainty method, and state when samples cannot support tail or rare-event estimates. / 基线候选按场景、风险、输入难度分布、工作流模型工具规则版本、环境、暴露量及人工参与分层报告，保留取消失败未知缺失运行可见。看候选结果前冻结对照选择与最小有意义变化，记录反复查看及协议改动；尽可能同例配对，使用合适不确定性方法，并说明样本何时不足以估计尾部或罕见事件。

Do not average away high-risk deterioration with many low-risk successes. Release safety constraints are separate hard conditions in the evaluation plan, not weights that a lower cost can cancel. Zero observed severe events with a small exposure does not prove zero severe-event risk. / 不用大量低风险成功平均稀释高风险退化。发布安全条件是评价计划中独立硬约束，不是可被低成本抵消的权重；小暴露下严重事件观测为零不证明风险为零。

For latency, a terminal-only sample is a conditional distribution. Keep unfinished/timeout runs as right-censored at the observation cutoff or classified failures according to the frozen plan. Do not treat a timeout threshold as a real completion duration, invent a p95 from too few values, replace uncertain negative clock differences with zero, or compare one arm's mature tail with another arm's early sample. Survival analysis requires its assumptions and censoring mechanism to be stated; otherwise report observed duration and censor counts separately. / 延迟仅用终态样本时是条件分布。按冻结计划把未完成超时运行保留为截止时右删失或明确分类失败；不把超时阈值当真实完成耗时，不用不足样本伪造 p95，不将时钟不明的负值归零，不比较一侧成熟尾部与另一侧早期样本。采用生存分析须声明假设及删失机制，否则分别报告观测时长和删失数。

For cost, declare currency, rate date/version, human-time pricing, shared-cost allocation and included components. Estimates remain estimates. If one provider or human-work component is missing, do not present the observed subtotal as total cost or precise savings; compare matching covered components only, with explicit exclusions. / 成本声明币种、费率日期版本、人工定价、共享分摊及包含构成；估算保持估算。若缺一家供应方或人工构成，不把已观测小计称为总成本或精确节省；仅对照相同覆盖构成并明确排除项。

An observed before/after improvement, a matched comparison or review gain does not itself establish causation. Retain changed inputs, external service drift, reviewer learning and concurrent policy changes as confounders. A causal claim needs the justified experiment/identification design and its assumptions. Simplification or guard retirement also needs evidence that mandatory downstream checks still detect important failures; model upgrades alone do not supply that evidence. / 前后改善、匹配对照或评审增益本身不证明因果；保留输入变化、外部服务漂移、评审者学习及同时策略变更等混杂因素。因果声明需有论证过的实验或识别设计及假设。简化或退役防护还须证明下游必要检查仍能检出重要失败；模型升级本身不提供该证据。

<a id="completion"></a>
## Bounded Evidence Completion and Replay / 有界补全与重放

1. Inventory originals before querying. For each gap record the missing field, source expected, exact artifact/run binding, reason (`not_generated`, `not_received`, `not_collected`, `collection_failed`, `unlinked`, `expired`, `forbidden`, `unavailable`, `conflict`, `unknown` or rule-backed `not_applicable`), impact and owner. Preserve source-specific reasons through a versioned mapping. / 先盘点原件再补查；逐缺口记录字段、预期来源、精确制品运行绑定、原因、影响及责任人；原因区分未生成、未接收、未采集、采集失败、未关联、过期、禁止访问、不可获得、冲突、未知及有规则依据的不适用，并通过版本映射保留来源具体原因。
2. Freeze a shared request budget: maximum queries including retries/pages, elapsed duration, scanned records/bytes, concurrency, monetary cost and replay attempts. Enforce the remaining budget across child probes; do not restart it on retries. Stop on exhaustion, expired authority, unchanged repeated evidence or an unavailable source. / 冻结共享请求预算，包含计入重试分页的查询次数、耗时、扫描记录字节、并发、金额和重放次数；子探针共享剩余预算，重试不重置。耗尽、授权过期、重复无新证据或来源不可得时停止。
3. Prefer retained logs → source/version checks → upstream/downstream originals → authorized read-only authoritative queries. Every query records purpose, scope, real source locator, outcome and actual resource use. Access denial does not justify widening access or copying data to an unapproved store. / 优先留存日志、来源版本核验、上下游原件，再作获准权威只读查询；每次记录目的范围、真实来源位置、结果及实际资源消耗。访问被拒不授权扩大权限或复制到未批准存储。
4. Accept an enrichment only after verifying responder/source identity, artifact binding, freshness and access scope. Append the original reference, verification result and correction linkage to `observation_enrichment`; never synthesize absent originals, approval or business acceptance. / 核验应答来源身份、制品绑定、时效范围后采纳补全，只追加原始引用、核验结果和更正关系，不生成不存在的原件、审批或业务验收。
5. Replay is a separately authorized non-production evaluation request, not a read-only query. Use captured/mock tool responses, isolated identity/storage, approved fixture data, bounded compute and no production credentials; deny network and external side effects unless explicitly permitted in the test contract. A “read-only” API that triggers work is not safe merely because of its name. / 重放是单独授权的非生产评价请求，不是只读查询。使用录制模拟响应、隔离身份存储、获准测试数据、有界算力且无生产凭据；默认拒绝网络与外部副作用，除非测试契约明确允许。名为只读却触发工作的接口不能仅凭名称视为安全。
6. Preserve original `run_id` in replay provenance but create a new test run/attempt identity; never reuse a live idempotency key to repeat an effect. Report historical reconstruction and candidate behavior as separate products. A sandbox result does not confirm a past or live business effect. / 重放来源保留原运行号，但新建测试运行尝试身份，不复用线上幂等键重复副作用。历史重建与候选行为分别报告；沙箱结果不确认过去或线上业务效果。

<a id="templates"></a>
## Request and Return Templates / 请求与返回模板

The YAML below is the canonical field shape for this profile, as a design template rather than a recorded run or executable authorization. Replace placeholders with authentic source-bound values. References are `{id, version, digest}` or explicitly null before creation; stage gates in the contract require the relevant non-null bindings. Null budget placeholders require concrete finite limits before dispatch and never mean unlimited. Do not fabricate a baseline, candidate, evaluation or release reference to make a template appear complete. / 以下 YAML 是本配置的规范字段形状，属于设计模板，不是运行记录或可执行授权。占位值须替换为真实有来源值；引用为三元绑定，产生前可显式为空，阶段门要求对应绑定非空。预算空占位必须在派发前补成有限实值，绝不表示无限；不能为使模板完整而编造引用。

```yaml
probe_request:
  profile: architecture_evolution/0.2.0
  request_id: null                 # Required real ID / 必需真实编号
  evolution_id: null
  baseline_ref: null               # {id, version, digest} when frozen / 冻结后必需
  candidate_ref: null
  evaluation_plan_ref: null
  release_ref: null
  null_binding_reasons: {}         # Per-ref lifecycle reason / 逐引用生命周期理由
  target_ref: null
  expected_control_epoch: null     # Bind live controls where applicable / 适用时绑定实时控制
  stage: null                     # E0 ... E9 / 执行阶段
  run_ids: []
  scope:
    scenario_ids: []
    node_ids: []
    time_range: {start: null, end: null}
    observation_cutoff: null
    maturity_rule_ref: null
    population_manifest_ref: null
  probe_ids: []                    # Select AEP01 ... AEP10 / 按需选择
  question: null
  evidence_refs: []                # Real originals and source locators / 真实原件与来源定位
  required_evidence: []
  deadline_at: null                # Optional response deadline / 可选响应截止
  permissions:
    authorization_ref: null
    read_only: true
    allowed_sources: []
    allowed_fields: []
    production_mutation: false
    replay_allowed: false
    replay_contract_ref: null
  budget:
    cumulative_budget_ref: null    # Optional shared budget binding / 可选共享预算绑定
    max_queries: null
    max_duration_seconds: null
    max_records: null
    max_bytes: null
    max_concurrency: null
    max_cost: null
    currency: null
    max_replays: 0
```

```yaml
probe_result:
  profile: architecture_evolution/0.2.0
  request_id: null
  report_id: null
  report_revision: null
  supersedes_report_ref: null
  evolution_id: null
  baseline_ref: null
  candidate_ref: null
  evaluation_plan_ref: null
  release_ref: null
  target_ref: null
  null_binding_reasons: {}         # Echo request lifecycle reasons / 回显请求生命周期理由
  expected_control_epoch: null
  observed_control_epoch: null
  status: unavailable             # complete | partial | unavailable: collection only / 仅采集完成度
  status_reason: null
  business_state_changed: false
  evidence_refs: []
  missing_evidence: []             # field, expected source, reason, owner / 字段来源原因责任人
  observation_enrichment: []       # Append-only original refs / 仅追加原件引用
  timeline_refs: []
  source_checks: []                # Identity, version, time, redaction / 身份版本时间脱敏核验
  first_deviation:
    candidate_event_ids: []
    node_ids: []
    evidence_refs: []
    causal_order_status: unknown
    uncertainty_interval: null
    confidence: unknown
  hypotheses: []                  # Description, support, contradiction, status / 说明支持反证状态
  metrics: []                     # AEM ID, definition, n/d, units, coverage, cutoff, refs / 指标完整口径
  findings: []                    # Fact/inference/hypothesis, risk, owner / 事实推断假设及风险责任
  recommended_next_step:
    action: null
    return_stage: null
    rationale_refs: []
    authorization_granted: false
  execution_disposition:
    status: not_observed          # Independent execution receipt / 独立执行回执
    evidence_ref: null
  budget_used: {}                 # Actual use and remaining shared budget / 实耗及共享余额
  limitations: []
```

`complete` means the requested observation scope has all required valid evidence and required calculations/gaps have been resolved; it does not mean business success, release approval or runtime implementation. A fully observed failed workflow can yield a complete probe report. `partial` means useful evidence exists but required coverage or verification remains unresolved, including forbidden or unavailable sources. `unavailable` means no usable evidence can satisfy the requested scope. Preserve the reason and any limited inventory; never use unavailable as a passing result. / `complete` 仅表示所请求观测范围具备全部必要有效证据，且必要计算及缺口已解决，不表示业务成功、发布获批或运行时实现；观察完整的失败流程也可得到采集完成报告。`partial` 表示已有有用证据但必要覆盖核验仍未解决，含禁止访问或不可取得来源。`unavailable` 表示没有可用证据满足请求范围；保留原因及有限盘点，不能当作通过。

A result must echo the exact request bindings. Reject or quarantine mismatched/stale responses; do not attach them to the latest candidate by name alone. New evidence, candidate changes or control epochs require linked new requests/report revisions. Proposed actions and the observed execution disposition are separate fields; only an authentic execution receipt can populate the latter. / 返回须复现请求精确绑定；失配陈旧响应拒收或隔离，不能只按名称挂到最新候选。新证据、候选变化或控制代次变化需要关联的新请求报告修订；建议动作与已观测执行处置分字段，后者只能由真实执行回执填写。

<a id="acceptance"></a>
## Diagnostic Package and Acceptance / 诊断包与验收

Deliver scope and bindings; source inventory and gaps; causal timeline and uncertainty; first provable deviation; facts versus hypotheses; comparable metric tables with denominator/coverage/maturity; high-risk findings; bounded validation proposals; recommended next step; and unresolved obligations with owner and deadline. Record an observation cutoff and report version so a reviewer can reproduce the interpretation. / 交付范围绑定、来源清单缺口、因果时间线与不确定性、首个可证实偏差、事实与假设、带分母覆盖成熟窗口的可比指标、高风险发现、有界验证建议、下一步及含责任期限的未决义务；记录观测截止与报告版本以便复查重现。

Validate the contract's `AET-01`–`AET-14` scenarios before claiming an adopting runtime conforms. In particular inspect duplicate/late/missing events, survivor-biased acceptance, empty versus unknown denominators, version drift, high-risk regression, incomplete cost, censored latency, failed enrichment authority and replay side effects. Documentation checks only validate asset structure; all such runtime and business cases require separately recorded inputs, expected/actual results and evidence. / 宣称接入运行时符合规范前，应验证契约的验收场景；重点覆盖重复迟到缺失事件、幸存者验收偏差、空分母与未知分母、版本漂移、高风险回归、不全成本、删失延迟、补全授权失败与重放副作用。文档检查仅验证资产结构；运行及业务场景均需另行记录输入、预期实际结果及证据。

The useful outcome is a supported, bounded design decision with visible uncertainty, not more logs or a falsely complete metric dashboard. / 有效产出是证据支持、范围明确、保留不确定性的设计决定，而不是更多日志或看似完整却失真的指标面板。
