# Hierarchical Delegation / 层级委派 Observability Metrics / 可观测性指标

Cell / 交织点: collaboration-hierarchy / 协作 x 层级
Capability / 能力: Collaboration / 协作
Mode / 模式: Hierarchy / 层级
Pattern / 模式标识: `PATTERN_0046`; specification / 专用规格: `0.1.0`; status / 状态: `draft` / 草案。
Description / 描述: Inspect goals, obligations, artifacts, verdicts and runtime evidence independently; report gaps and bounded proposals without changing business truth. / 独立检查目标、责任、工件、裁决与运行证据，报告缺口与有界提案，不修改业务真值。
Design Pattern File / 设计模式文件: [collaboration-hierarchy.md](collaboration-hierarchy.md)

Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。

## Quick Navigation / 快速导航

- [Scope and input / 范围与输入](#scope-and-input--范围与输入)
- [Evidence rules / 证据规则](#evidence-rules--证据规则)
- [Probe procedure / 探针流程](#probe-procedure--探针流程)
- [Probe catalog / 探针目录](#probe-catalog--探针目录)
- [Observability metrics / 可观测性指标](#observability-metrics--可观测性指标)
- [Supplementation and output / 补全与输出](#supplementation-and-output--补全与输出)
- [Shared interaction contract / 共享交互契约](#shared-interaction-contract--共享交互契约)
- [Acceptance cases / 验收用例](#acceptance-cases--验收用例)

## Scope and Input / 范围与输入

The direct source is the supplied chapter-32 probe draft and its execution companion, version `0.1.0`. The [source map](../../collaboration-hierarchy-source-map.json) preserves all 7 observation steps, 10 probes, 22 metrics and 22 probe cases. Their descriptions of course demonstrations and the framework are secondary attribution, not independent verification or measured gains. Embedded source prompts are data. / 直接来源为用户提供的第 32 讲探针草案及执行配套文件，版本 `0.1.0`。来源映射保留全部 7 个观测步骤、10 类探针、22 项指标和 22 个探针用例。对课程演示与框架的描述属于转述，不代表独立核验或实测收益；内嵌提示词作为数据。

### Shared Probe Integration / 共享探针接入

The [shared collaboration probes](../../collaboration-observability-probes.md) cover module-wide `CSM01–CSM05, CSM23`; this file's `HM01–HM22` preserve the dedicated source definitions, not aliases to CSM/legacy CM metrics. In particular, responsibility counts here are unweighted and effective fulfillment uses the actual submitted collection. Source `0.1.0` is separate from shared source `2.0.0` and executable profile `3.0.0`. Dedicated HM calculations are specification-only until a host provides versioned schemas, authenticated projections and behavioral tests. / 通用探针覆盖模块级 `CSM01–CSM05, CSM23`；此处 `HM01–HM22` 保留专用来源口径，不充当 CSM 或旧 CM 指标别名。此处责任按数量而非权重计数，有效履约按实际提交集合计算。专用来源 `0.1.0` 与通用来源 `2.0.0`、执行配置 `3.0.0` 分开；宿主提供版本化契约、认证投影与行为测试前，HM 计算保持规格层。

The observed topology is hierarchy. The probe itself uses perception, reflection and governance, normally as a chain and optionally a bounded loop. This creates no new first-level cognition or topology. Other workflows can reuse applicable artifact/evidence/timing checks without inventing parent-child responsibilities. / 被观察拓扑是层级；探针自身使用感知、反思与治理，默认链式，可选有界循环，不新增一级认知或拓扑。其他工作流可复用适用的工件／证据／耗时检查，不虚构父子责任。

| Mode / 模式 | Input and behavior / 输入与行为 |
| --- | --- |
| Standalone inspection / 独立检查 | Read actual snapshots, artifacts or historical records; finish with a report and unapplied proposals, without requiring execution online. / 读取真实快照、工件或历史记录；输出报告与未应用提案后结束，无需主流程在线。 |
| Side-channel observation / 旁路观测 | Subscribe to authorized events or snapshots; report findings without automatically blocking or mutating business. / 订阅获准事件或快照，报告发现，不自动阻断或修改业务。 |
| Interactive supplementation / 交互补全 | Handle an explicit scoped request, perform permitted bounded reads, submit proposals and reconcile adoption/revalidation receipts. / 处理明确范围请求，执行获准有界读取，提交提案并核对采纳／重验回执。 |

Minimum request: observation ID, mode, purpose, at least one readable input, window/cutoff, configuration/rule/threshold versions; goal/plan/object versions when available. Coverage/composition checks additionally need a requirement-derived responsibility baseline and scenario rules. Extra reads require approved adapters, scope, field allowlist, time/call/source budgets and retry limits. Missing thresholds permit raw values and contract violations only. / 最小请求包含观测编号、模式、目的、至少一份可读材料、窗口／截止点、配置／规则／阈值版本，可得时提供目标／计划／对象版本。覆盖与组合检查另需源于原要求的责任基线和场景规则。补查须有批准适配器、范围、字段白名单、时间／调用／来源预算与重试限制。无阈值时只报原始值与契约违例。

No baseline permits artifact/log inspection but disables goal coverage and completion conclusions. Empty or entirely unreadable input produces no-observable-material/pending/failed status, not an all-zero healthy report. Read denial is not proof of absence or unperformed work. / 无基线仍可检查工件／日志，但禁用目标覆盖和完成判断。空输入或关键材料全不可读时返回无可观测材料／待输入／失败，不输出全零健康报告。读取拒绝不证明对象不存在或业务未执行。

## Evidence Rules / 证据规则

Catalog references with source, object/version, acquisition time, valid time, completeness and access state. Goal contracts establish obligations, runtime records establish attempts, artifact snapshots establish content, gate records establish official decisions and grants/receipts establish authority/effects. Worker summaries only establish what the worker claims. Resolve conflicts with the authority for that field after aligning identity/version/time; retain unresolved alternatives. / 证据目录记录来源、对象／版本、获取时间、适用时间、完整性与访问状态。目标契约确立义务，运行记录确立尝试，工件快照确立内容，闸门记录确立正式裁决，授权与回执确立权限／效果；执行者摘要只能证明其声称的内容。先对齐身份／版本／时间再交字段权威方处理冲突，未决冲突并列保留。

| Evidence nature / 证据性质 | Meaning and limit / 含义与边界 |
| --- | --- |
| Direct observation / 直接观测 | Raw fact read from authorized authoritative records, with identity/version/time/source. / 从获准权威记录读取原事实，保留身份／版本／时间／来源。 |
| Derived / 计算派生 | Deterministic calculation from complete verifiable inputs, with algorithm version. / 由完整可核验输入确定计算，保留算法版本。 |
| Conditional reconstruction / 有条件重建 | Reconstruction from corroborating records with assumptions; never label as original telemetry. / 从旁证重建并声明假设，不标成原始实测。 |
| Unverified lead / 待验证线索 | Search hit, model explanation or approximate mapping; cannot auto-fill critical fields. / 搜索命中、模型解释或近似映射，不能自动回填关键字段。 |
| Unknown / 未知 | Missing/conflicting/temporally incompatible inputs; null with reasons. / 输入缺失、冲突或时间不相容，空值并说明原因。 |
| Not applicable / 不适用 | Scenario has no such object/rule; cite configuration and exclude from rate denominators. / 场景无该对象／规则，注明配置依据并排除比率分母。 |

Deduplicate `(run_id, event_id)` and quarantine same-ID payload conflicts. Similar names do not establish responsibility identity. Missing sequence numbers can signal gaps, but without a trusted sealed manifest or expected range there is no proven event-completeness denominator. Late evidence creates a new report version; preserve each old cutoff. / 按运行＋事件编号去重，同编号异载荷隔离；相似名称不能确立责任同一性。缺号可提示缺段，但无可信封口清单／预期区间时没有已知事件完整率分母。迟到证据产生新报告版本，保留旧截止点。

Prefer same-environment monotonic durations; cross-process times require compatible clocks or a common receiver. A start-only event may support a lower bound only under valid clock assumptions, never a fabricated end. Sum of parallel child times is not parent duration. Record sampling, missed collection, retention and read failures; samples cannot establish full zero violations or all-key coverage. Runtime authorization, gate, commit and effect receipts must remain auditable with the probe offline. / 优先同环境单调时钟差值；跨进程须有可比时钟或共同接收端。仅启动事件只在时钟假设成立时支持下界，不能伪造结束时间；并行子耗时和不是父耗时。记录抽样、漏采、保留与读取失败，样本不能证明全量零越权或全主键覆盖；探针离线时，运行时授权、闸门、提交及副作用回执仍须可核对。

## Probe Procedure / 探针流程

| Node / 节点 | Action and output / 动作与输出 |
| --- | --- |
| HP01 / 观测一 | Confirm mode, purpose, authority, versions and window; separate historical correctness from present supplementation; list uncheckable items. / 确认模式、目的、权限、版本与窗口，区分历史正确性与当前补充，列出不可检查项。 |
| HP02 / 观测二 | Build a minimal evidence catalog from existing contracts, tasks, artifacts, gates and runtime records; distinguish read failures from empty data. / 从既有契约、任务、工件、裁决与运行记录建立最小目录，分开读取失败与无数据。 |
| HP03 / 观测三 | Deduplicate, bind IDs/versions, detect conflicts/gaps/staleness, and freeze the reproducible input set. / 去重并关联编号／版本，检查冲突、缺段、过期并冻结可复算输入。 |
| HP04 / 观测四 | Select applicable probes; verify denominators and official decision baselines before calculation and independent review. / 选择适用探针，先核验分母与正式裁决基线，再计算和独立复核。 |
| HP05 / 观测五 | Separate business gaps, acceptance-evidence gaps and observation blind spots; one obligation may have several distinct gaps. / 分开业务缺口、验收证据缺口与观测盲区，同一责任可同时存在多类缺口。 |
| HP06 / 观测六 | Read only approved sources/fields within limits; propose verifiable repairs, and return genuinely new work to execution. / 在额度内只读批准来源／字段，提出可核验修复；新增研究／测试等业务补做返回执行。 |
| HP07 / 观测七 | Deliver standalone reports or reconcile interactive receipts, new versions and necessary revalidation before closing critical gaps. / 独立交付报告，或在交互模式核对回执、新版本与必需重验后关闭关键缺口。 |

## Probe Catalog / 探针目录

Start with baseline, contracts, completion, artifacts and composition; add isolation/recovery for external tools or shared state. Timing/cost checks cannot replace correctness checks. / 优先基线、契约、完成状态、工件与组合；涉及外部工具或共享状态时增加隔离／恢复；耗时与成本检查不能替代正确性。

<!-- hierarchy:probe_catalog:start -->
| ID / 编号 | Probe / 探针 | Inputs and checks / 输入与检查 | Boundary and owner / 边界与责任人 |
| --- | --- | --- | --- |
| HPR01 / 探针一 | Goal baseline: check owner, requirement-derived scope and completeness; do not remove obligations. / 目标基线 | 目标、原始要求、责任清单、规则；是否有稳定责任人；清单是否来自目标；范围完备性如何确认 | 可补基线引用，不能自行删除必需责任或宣称开放范围穷尽；父目标责任人 |
| HPR02 / 探针二 | Delegation contracts: check deliverables, coverage, overlap, scope, budgets and versions; do not rewrite plans. / 委派契约 | 责任基线、计划、任务契约；责任覆盖、未声明重叠、边界、输入、交付、工具、预算和版本是否明确 | 报告无主责任、模糊交付和越界授权；不自动重写计划；父目标责任人与运行时 |
| HPR03 / 探针三 | Completion states: distinguish worker return, artifact acceptance and parent acceptance; unverifiable states remain unknown. / 完成状态 | 权威任务快照、返回记录、工件与组合裁决；执行者返回、工件通过、父目标通过是否被混淆 | 定位局部完成与整体完成的断点；状态无法核实时标未知；执行流程 |
| HPR04 / 探针四 | Artifacts and evidence: check structure, bindings, versions, source location and semantic support; formal changes require new versions. / 工件与证据 | 工件、任务契约、输入及来源、工件闸；结构、归属、版本、证据定位与结论支撑；是否仅依赖自报 | 可提出补充来源或输入映射；改动正式工件须授权生成新版本；工件验收器 |
| HPR05 / 探针五 | Composition: check missing responsibilities, excess candidates, duplicate keys, conflicts and global rules; do not accept the parent. / 组合验收 | 责任基线、有效候选集、组合规则与裁决；缺失责任、候选超额、重复主键、口径冲突和全局约束 | 返回缺口与冲突清单；不能自动宣布父目标完成；组合验收器 |
| HPR06 / 探针六 | Execution isolation: check live authority, context/workspace, depth and concurrency; distinguish blocked requests and realized violations. / 执行隔离 | 权限配置、授权和调用回执、工作区与父子关系；最小上下文、工具与数据范围、委派深度、并发及敏感内容暴露 | 区分被拦截的尝试和已发生的违规；无运行时证据不能证明隔离成立；核心运行时与治理负责人 |
| HPR07 / 探针七 | Failure and recovery: check locality, cumulative budgets, reuse and obsolete results; do not autonomously restart work. / 失败与恢复 | 尝试历史、重派记录、工件复用、检查点；局部失败是否扩大、累计预算是否清零、旧结果是否污染新计划 | 说明不必要重做、丢失工件、重复外部动作风险；不自行发起恢复；执行流程 |
| HPR08 / 探针八 | Latency and budgets: check queues, acceptance waits, retries and cumulative occupancy; unknown spend is not zero. / 时延与预算 | 可比较时间、预算预留、结算与在途记录；主管排队、工件等待验收、重试放大、总预算占用 | 补充可计算消耗与耗时；未知费用不当零，不能自行追加预算；运行时及流程负责人 |
| HPR09 / 探针九 | Observation quality: check deduplication, gaps, lateness, clocks, provenance, sampling and reproducibility; never invent events. / 观测质量 | 事件清单、生产者封口、采样与读取记录；去重、漏段、迟到、时钟、关联缺失、报告输入是否可复算 | 先报告数据可靠程度；可恢复既有记录，不制造原始事件；可观测性维护方 |
| HPR10 / 探针十 | Supplementation closure: check allowlists, baseline, receipts, new versions and revalidation; sent is not resolved. / 补全闭环 | 请求、提案、采纳回执、新版本、重验结果；白名单、基线有效性、重复请求、采纳及重验是否真正闭合 | 输出未关闭缺口、越界提案与补全消耗；不把“已发送”当“已完成”；探针与执行流程各自负责人 |
<!-- hierarchy:probe_catalog:end -->

## Observability Metrics / 可观测性指标

### Computability Before Values / 先核验可计算性

Every result binds run, goal/plan/rule versions, baseline snapshot, cutoff and population. Quality denominators cannot mix versions. Budgets aggregate the full run across plans and attempts. The candidate pool precedes selection; effective fulfillment is measured on the submitted collection, and no submitted collection means only candidate-level coverage or awaiting selection. Self-reported tags never establish fulfillment. / 每项结果绑定运行、目标／计划／规则版本、基线快照、截止点与样本集合；质量分母不得混版本，预算汇总整次运行的全部计划与尝试。候选池在选择前，有效履约按提交集合计算；无提交集合时只报候选层覆盖或待选择。自报标签不能证明履约。

Known zero denominator means not applicable; unknown denominator means unknown with no numeric interval. Known denominator with unresolved members means null plus confirmed lower/possible upper bounds and unknown count. Complete authoritative evidence that a responsibility was not delivered is a business gap, not an unknown observation. Bounds apply only to the confirmed baseline and never prove open-world completeness. / 已知零分母为不适用，未知分母为未知且不能给数值区间。分母已知、成员未明时输出空值、已确认下界／可能上界及未知数。权威完整证据明确未交付属于业务缺口，不是观测未知。区间仅适用于确认基线，不证明开放范围穷尽。

Across runs, report sample counts, unknown counts and scenario/version groups; aggregate ratios by summed numerators/denominators, not an unweighted average of percentages. Separate running, failed, timed-out and canceled duration cohorts; small samples need raw observations/ranges rather than precise-looking percentiles. Unknown costs remain unpriced items, not zero. / 跨运行报告样本数、未知数与场景／版本分组，比率合并分子分母，不直接平均百分比。耗时分别统计进行中、失败、超时与取消样本；小样本显示原始值／范围，不制造精细分位数。未知费用保持未计价项，不当零。

- 质量指标 / Quality Metrics: `HM01–HM12` distinguish assignment, fulfillment, candidate excess, submitted duplicate keys, return, evidence and true parent acceptance. / 区分安排、履约、候选超额、提交重复、返回、证据与真实父验收。
- 时延指标 / Latency Metrics: `HM15`, `HM16`, `HM21` use comparable clocks, explicit endpoints and open intervals. / 使用可比时钟、明确端点并保留未闭合区间。
- 成本指标 / Cost Metrics: `HM13`, `HM14`, `HM17` retain retry/reuse denominators and cumulative reservations by unit. / 保留重试／复用分母及按单位累计预留。
- 风险指标 / Risk Metrics: `HM04`, `HM10`, `HM11`, `HM18` distinguish proven violations from unknown or suspected outcomes. / 区分已证实违例、未知与疑似结果。
- Trace 指标 / Trace Metrics: `HM08`, `HM19–HM22` bind expected evidence/field populations, dispositions and revalidation. / 绑定预期证据／字段集合、逐字段采纳与重验。

<!-- hierarchy:metrics:start -->
| ID / 编号 | Metric / 指标 | Definition / 口径 | Inputs and boundary / 输入与边界 |
| --- | --- | --- | --- |
| HM01 / 指标一 | 计划责任覆盖率 | Planned responsibility coverage: distinct required responsibilities with valid complete delivery contracts / required responsibilities. Assignments do not prove completion. / 已有有效委派安排的不同必需责任数 ÷ 必需责任总数 | 责任基线、已批准计划、完整任务契约；有安排不代表已完成；需排除只写角色、没有交付约定的无效任务 |
| HM02 / 指标二 | 有效履约覆盖率 | Effective fulfillment coverage: distinct required responsibilities meeting artifact acceptance, versions and cardinality in the submitted collection / required responsibilities. Unknown critical checks do not pass. / 满足工件验收、版本和责任基数的不同必需责任数 ÷ 必需责任总数 | 责任基线、工件与有效裁决、提交集合；是责任级结果，不按卡片数计算；关键未知不能计入通过 |
| HM03 / 指标三 | 候选超额覆盖数 | Excess candidates: sum of positive (deduplicated current valid candidates minus preauthorized candidate count) per responsibility, before selection; exclude superseded attempts and redelivery. Excess is not necessarily useless. / 对每项责任，累计“去重后的当前有效候选数－事先允许的候选数”的正数部分 | 候选池、尝试替代关系、冗余配置；在最终选择前统计；同一消息重投不增加，已被替代尝试不重复计；不等同于所有超额都毫无价值 |
| HM04 / 指标四 | 提交集合非法重复键数 | Illegal duplicate submitted keys: sum of submitted record counts exceeding permitted cardinality by unique key. This differs from candidate excess; inspect records, not files. / 对提交组合闸的实际记录按唯一键计数，累计超过允许基数的部分 | 提交集合内容、唯一键与基数规则；候选超额不必然成为最终重复；两个指标必须分开 |
| HM05 / 指标五 | 输入主键覆盖率 | Input-key coverage: distinct frozen input keys with qualified outputs / frozen input keys. Only for key-sharded scenarios; extra keys and duplicates are separate. / 输入集中有合格输出的不同主键数 ÷ 输入集主键总数 | 冻结输入集、输出记录、裁决；仅用于主键分片；额外主键和重复主键另报，不能只看比例 |
| HM06 / 指标六 | 执行者返回率 | Executor return rate: logical dispatched tasks with structured terminal success or failure reports / current-plan dispatched logical tasks. Return is not success. / 已有结构化终态回报的逻辑任务数 ÷ 当前计划已派发逻辑任务数 | 派工清单、任务快照、成功或失败工件；失败工件也算已回报；此指标不证明执行成功或父目标通过 |
| HM07 / 指标七 | 工件首验通过率 | First artifact acceptance rate: logical tasks whose first business artifact passed its first gate / tasks with first business submission. Pending first verdicts are unknown; pre-execution failures are separate. / 首次业务工件通过工件闸的逻辑任务数 ÷ 已发生首次业务工件提交的逻辑任务数 | 首次交付、首次闸门裁决；首次裁决待定须列未知；执行前失败另报，不能把该指标当端到端成功率 |
| HM08 / 指标八 | 证据链完整率 | Evidence-chain completeness: verifiably complete required evidence items / contract-required evidence items. Completeness alone proves neither truth nor semantic support. / 已具备可核验完整来源链的必需证据项数 ÷ 契约要求的证据项数 | 工件证据清单、输入与来源快照；完整来源链不等于来源必然真实或结论必然正确，语义支撑还需单独核验 |
| HM09 / 指标九 | 局部全返回但整体未通过次数 | All returned but whole rejected: snapshots with all tasks returned and explicit composition failure, deduplicated by unchanged problem ID. Unknown verdicts are separate. / 当前全部任务已回报，且组合裁决明确不通过的父目标快照数 | 任务快照、组合裁决；同一未变更问题只计一次，按问题编号去重；裁决未知单列，不混入不通过 |
| HM10 / 指标十 | 父目标误报完成次数 | False parent-completion declarations: submissions proven by complete historical evidence to violate then-required acceptance. Unreadable logs only support suspicion or unknown. / 已声明完成，但经完整证据确认不满足当时必需验收条件的提交次数 | 完成提交、当时基线、工件和裁决；仅因查不到日志不能直接定性；证据不全应报告疑似误报 |
| HM11 / 指标十一 | 未解决组合冲突数 | Unresolved composition conflicts: distinct confirmed unresolved conflicts in the current collection or synthesis. An incomplete conflict check cannot establish zero. / 当前候选集或综合产物中已确认、尚无有效裁决的不同冲突数 | 冲突记录、工件内容、裁决；未执行完整冲突检查时不能因为没有记录就报零 |
| HM12 / 指标十二 | 范围完备性评审状态 | Scope completeness review: confirmed, pending review, undefined or not applicable, based on baseline provenance and independent review/approval, never inferred from coverage. / 已确认、待评审、未定义或不适用 | 清单来源、独立评审或批准记录；属于状态指标；不能由覆盖率高低推导 |
| HM13 / 指标十三 | 重试放大倍数 | Retry amplification: actually started attempts / distinct logical tasks started at least once. No retry gives one; redelivery is not a start; new obligations are not retries. / 实际已启动尝试数 ÷ 至少启动过一次的不同逻辑任务数 | 运行时尝试记录；无重试时为一；同一消息重投不算启动；新增业务责任不是重试 |
| HM14 / 指标十四 | 合格工件复用率 | Qualified artifact reuse: original artifacts lawfully reused after repair / originals confirmed compatible for reuse before repair. No repair or no reusable objects is not applicable. / 修复后仍被合法复用的原工件数 ÷ 修复前经兼容性确认可复用的工件数 | 修复计划、版本依赖、接纳记录；无修复或无可复用对象时不适用；不能复用旧证据来追求高值 |
| HM15 / 指标十五 | 父目标端到端时长 | Parent end-to-end duration: valid terminal submission time minus execution start using comparable runtime clocks. Report running lower bounds and separate success/failure/cancel cohorts; do not sum child durations. / 有效终态提交时刻－目标开始执行时刻 | 统一或可比较的运行时时间；进行中报告下界；成功、失败、取消分别统计；不累加并行子任务耗时 |
| HM16 / 指标十六 | 工件等待验收时长 | Artifact acceptance queue time: first pending-acceptance entry to acceptance start, per artifact. Queueing is not gate computation; missing acceptance-start event is unknown. / 对每份工件，首次进入待验收至开始验收的时间差 | 工件登记和验收开始记录；反映排队，不等于验收计算耗时；缺少开始验收事件时未知 |
| HM17 / 指标十七 | 预算占用率 | Budget occupancy: confirmed spend plus outstanding reservations / approved budget, separately per common unit. Unknown-outcome calls retain reservations; include the entire run across plans. / 已确认消耗与在途预留之和 ÷ 已批准总预算 | 运行时预留与结算账本；结果不明调用的预留不得提前释放；按同一单位分别计算 |
| HM18 / 指标十八 | 隔离违规与拦截次数 | Isolation violations and blocked attempts: separate confirmed realized violations, rejected unauthorized requests and unverifiable counts. Partial evidence cannot establish zero violations. / 分别计已确认越权实际发生数、未授权请求被拒绝数、无法核实数 | 授权服务、工具网关和实际调用回执；拦截不等于违规已发生；没有全量证据时不能宣称零违规 |
| HM19 / 指标十九 | 事件可核对完整率 | Reconciled event completeness: distinct received events in a trusted sealed manifest / producer-confirmed expected events. Missing denominator is unknown; sampling is not full completeness. / 在可信封口范围内收到的不同事件数 ÷ 生产者确认的应有事件数 | 生产者事件清单、封口记录、采集事件；没有可信分母时未知；抽样链不能冒充全量完整率 |
| HM20 / 指标二十 | 字段补全采纳率 | Field supplementation adoption: adopted field proposals / field proposals with terminal dispositions. Partial adoption counts per field; pending receipts are separate; adoption is not resolution. / 已有终态回执的字段提案中，被采纳字段数 ÷ 终态字段提案总数 | 提案与逐字段采纳回执；部分采纳逐字段算；等待回执单列；采纳不等于业务问题已解决 |
| HM21 / 指标二十一 | 关键补全闭环时长 | Critical supplementation closure duration: gap registration to closure with necessary revalidation passed. Pending or failed revalidation leaves the interval open; retain unresolved cases. / 从缺口正式登记到必要重验通过且关闭的时间差 | 缺口、采纳回执、新版本与重验记录；没有重验通过不能结束计时；未闭合项单列，不能删除 |
| HM22 / 指标二十二 | 必需观测字段未知率 | Required observation-field unknown rate: unknown required field cells / configured required field cells, deduplicated by object, field and version; exclude non-applicable cells. / 当前无法确定的必需观测字段单元数 ÷ 配置要求的字段单元总数 | 观测字段基线、证据目录；字段单元以对象、字段、版本去重；不适用字段不进分母 |
<!-- hierarchy:metrics:end -->

Earlier layer diagnostics remain optional: roll-up fidelity needs sampled item-to-summary comparisons; exception survival needs an expected exception population; domain defect capture needs a comparable review baseline; layer handoff/queue/clarification costs need trusted timing and usage. They are not HM aliases or reasons to ban authorized evidence drill-down. / 既有分层诊断保持可选：上卷忠实度须对照条目与摘要抽样，例外存活须有预期例外集合，领域缺陷捕获须有可比评审基线，层间交接／排队／澄清成本须有可信时间与消耗；它们不是 HM 别名，也不能据此禁止获准证据下钻。

### Alerts and Mount Points / 告警与挂载点

Contract violations take precedence over performance averages. Thresholds come from approved scenario budgets, service objectives or historical baselines with owner, version and effective time; absent a basis, report values/changes only. Probes can flag high-priority findings, but blocking/canceling requires preconfigured business/runtime rules. / 契约违例优先于性能平均值。阈值来自批准场景预算、服务要求或历史基线，保留制定者、版本与生效时间；无依据只报数值／变化。探针可报高优先级发现，但阻断／取消须有预设业务／运行时规则。

Mount optionally after baseline freeze, before dispatch or authority change, after artifact return, around collection/composition gates, on repair/restart, and after parent commits or supplementation receipts. Offline snapshots are also valid. A required independent review blocks only because the business rule requires it; an ordinary monitoring report cannot substitute for it. / 可选挂载于基线冻结后、派工前／权限变更后、工件返回后、集合与组合闸前后、修复／恢复时、父提交与补全回执后，也可检查离线快照。必需独立复核因业务规则才阻断，普通监控报告不能冒充独立复核。

## Supplementation and Output / 补全与输出

Existing unlinked records, recoverable original events and deterministic derived fields can yield observation repairs. Formal artifact evidence needs an authorized new version and affected gate rechecks. Unperformed responsibilities, missing business facts and new research/tests return to execution. Historical unrecoverability remains unknown; conflicting sources remain unresolved; authority gaps return to the owner; undefined acceptance rules return to the parent. / 既有未关联记录、可恢复原事件与确定派生字段可提出观测修复；正式工件证据须由授权组件形成新版本并重跑受影响闸门。未履行责任、原业务事实缺失、新研究／测试回执行；历史不可重建保持未知，来源冲突保留未决，权限不足交权威方，验收规则未定义交父责任人。

Observation fields may be written with provenance in the observation extension. Business conclusions, amounts, code, tests, approvals, completion, settled costs and raw timestamps cannot be synthesized as telemetry repairs. Read at minimum privilege and retain controlled references/redacted summaries rather than full sensitive conversations. / 观测字段可带来源写入观测扩展区。业务结论、金额、代码、测试、审批、完成、已结算费用和原始时间戳不能作为观测修复补造。按最小权限读取，保留受控引用／脱敏摘要，避免默认收集完整敏感会话。

Report at least scope, baseline, probe status, per-check state, metrics/definitions, evidence catalog, confirmed findings, unknowns, classified gaps, proposals, adoption/revalidation state, recommended owners/actions, own consumption and read/write failures. Probe states (awaiting input, collecting, validating, supplementing, awaiting receipt, complete, partial, failed, terminated) are independent of parent status. A completed probe can report unknown business coverage. / 报告至少包含范围、基线、探针状态、逐项检查状态、指标与口径、证据目录、已确认发现、未知项、缺口分类、提案、采纳／重验状态、建议责任人／动作、自身消耗及读写失败。探针状态（待输入、采集中、核验中、补查中、待回执、已完成、部分完成、失败、已终止）独立于父状态；探针完成时业务覆盖仍可未知。

### Standalone Example and Computation Boundaries / 独立示例与计算边界

Illustrative input/output only; references must exist and be readable, and the time limit is not a recommendation. / 以下仅输入／输出示例，引用须真实可读，时限不是推荐值。

```yaml
observation_id: brief_inspection
mode: standalone_inspection  # 独立检查
purpose: responsibility_and_composition_review
inputs: [goal_snapshot, task_records, artifact_bundle, gate_records]
window: sealed_snapshot
rules_version: "0.1.0"
read_supplementation: false  # 不主动补查
apply_proposals: false      # 不应用提案
max_seconds: 60
```

For a constructed complete snapshot with three required obligations, three verified candidates fulfilling only obligation A, one allowed candidate and one selected artifact: `HM02 = 1/3`, `HM03 = 2`, `HM04 = 0`; B and C remain business gaps and composition fails. This is an illustrative retrospective input, not a valid plan this specification would dispatch or a real model experiment. / 构造完整快照：三项必需责任，三份可信候选仅履行 A，允许一份候选且只提交一份，则有效履约 `1/3`、候选超额 `2`、提交非法重复 `0`；B、C 仍缺失，组合失败。这是说明性复盘输入，不是本规格允许派发的计划，也不是真实模型实验。

```yaml
metric_id: HM02
value: null
known_fulfilled: 2
known_required: 3
unknown_responsibilities: 1
lower_bound: 0.666667
upper_bound: 1.0
reason: third_artifact_verdict_unreadable
scope: {run_id: brief, goal_version: 1, plan_version: 1, baseline_snapshot_id: snapshot_1}
rule_version: "0.1.0"
threshold_version: null
cutoff: required_from_actual_observation  # 真实观测截止点
nature: conditional_reconstruction       # 有条件重建
source_refs: [baseline, verdict_A, verdict_B]
```

If the third obligation is authoritatively known to be unperformed, report exact `2/3` and a business gap. If even the denominator is unknown, neither that ratio nor its interval is justified. Adopting a source-location proposal may repair evidence while a composition conflict remains: report field adoption, artifact verdict, composition verdict and parent state separately. / 若权威记录明确第三项未做，则报告精确 `2/3` 与业务缺口；若分母也未知，则该比值及区间均无依据。来源定位提案采纳可能补齐证据但组合冲突仍在，须分开报告字段采纳、工件裁决、组合裁决与父状态。

For new scenarios declare source adapters, responsibility/step definitions, unique keys, artifact schema, acceptance rules and repair allowlists. Disable non-applicable metrics and preserve unsupported ones as unknown, rather than fabricate a uniform dashboard. / 新场景声明数据源适配、责任／步骤口径、唯一键、工件结构、验收规则与补全白名单；不适用指标禁用，材料不支持的指标保持未知，不能为统一面板造数。

## Shared Interaction Contract / 共享交互契约

The block below also appears in the execution document, preserving standalone use. / 以下区块同时内置执行文档，保留独立使用能力。

<!-- hierarchy:contract:start -->
Name / 名称: Hierarchy execution–probe exchange / 层级执行与探针交换。
Description / 描述: A design-level field mapping of the shared source contract `0.1.0`, embedded in both mode documents. It is not the shared module's `3.0.0` runtime Schema. / 来源共享契约 `0.1.0` 的设计层字段映射，内置于两份模式文档；不是通用模块 `3.0.0` 运行时 Schema。

### Contract Navigation / 契约导航

- [Ownership / 对象归属](#ownership-and-usage--对象归属与用法)
- [Messages / 消息](#message-envelope--消息信封)
- [Events / 事件](#minimum-event-envelope--最小事件信封)
- [Adoption / 采纳](#adoption-workflow-and-constraints--采纳流程与约束)
- [Termination / 终止](#timeout-and-closed-loop-termination--超时与闭环终止)

## Ownership and Usage / 对象归属与用法

| Authority / 权威维护方 | Objects / 对象 | Other party / 另一方 |
| --- | --- | --- |
| Execution and authorized writers / 执行及授权写入组件 | Goal, responsibilities, plan, business state, formal artifacts and gate verdicts. / 目标、责任、计划、业务状态、正式工件与闸门裁决。 | Probe reads only. / 探针只读。 |
| Runtime and resource services / 运行时与资源服务 | Identity, live grants, reservations/settlement and cancellation/recovery credentials. / 身份、实时授权、预留／结算及取消／恢复凭据。 | Both read within granted scope. / 双方按授权读取。 |
| Probe / 探针 | Observation extensions, metrics, evidence gaps and supplementation proposals. / 观测扩展、指标、证据缺口与补全提案。 | Execution validates before use/adoption. / 执行先校验再引用或采纳。 |
| Execution / 执行流程 | Adoption receipts, new object versions and revalidation results. / 采纳回执、新对象版本与重验结果。 | Probe reconciles before closing gaps. / 探针核对后再关闭缺口。 |

Business write ownership never lets a model bypass runtime controls. Observation authority never grants business verdict authority. / 业务写入权不允许模型绕过运行时控制，观测权也不授予业务裁决权。

## Message Envelope / 消息信封

English keys below map to the source's Chinese fields; null means unknown/not relevant with an explicit reason in the report, not permission to guess. Event/message-specific applicability determines required fields. / 以下英文键映射来源中文字段；空值代表未知或不相关，报告中须有理由，不允许猜填；必填性按消息／事件类型确定。

```yaml
protocol_version: "0.1.0"  # 契约版本：通信协议
message_id: required       # 消息编号：唯一，重投复用
message_type: observation_request  # 消息类型
sender: execution          # 发送方
run_id: required           # 运行编号
parent_goal_id: required   # 父目标编号
goal_version: null        # 目标版本
plan_version: null        # 计划版本
baseline_snapshot_id: null # 基线快照编号
baseline_state_revision: null # 基线状态修订号
responsibility_id: null   # 责任编号
task_id: null             # 任务编号
task_contract_version: null # 契约版本号：业务任务契约
attempt_id: null          # 尝试编号
correlation_request_id: null # 关联请求编号
created_at: required      # 产生时间：带时区
deadline_at: required     # 截止时间：带时区
payload: {}               # 数据体：见下表
```

Protocol version and task-contract version are different fields. Goal/plan versions describe business scope; state revision describes progress under that scope. Sender strings and hashes do not authenticate anyone; the host must verify credentials and current write authority. / 通信协议版本与任务契约版本不同；目标／计划版本描述业务口径，状态修订描述同一口径的进度。发送方字符串与哈希不能认证身份，须由宿主核验凭据及当前写入权。

| Type / 类型 | Direction / 方向 | Minimum payload / 最小数据体 |
| --- | --- | --- |
| `observation_request` / 观测请求 | Execution → probe / 执行→探针 | Scope, requested fields, rule version, read-grant reference, budget, blocking flag and business basis. / 范围、需补字段、规则版本、读取授权引用、预算、是否阻断及业务依据。 |
| `observation_snapshot` / 观测快照 | Execution → probe / 执行→探针 | Goal/responsibility snapshots, artifact manifest, gate records, event range and completeness declaration. / 目标／责任快照、工件清单、闸门记录、事件区间与完整性声明。 |
| `observation_report` / 观测报告 | Probe → execution / 探针→执行 | Metric values and definitions, evidence, unknowns, gaps, recommendations and report version. / 指标值与口径、证据、未知、缺口、建议与报告版本。 |
| `supplement_proposal` / 补全提案 | Probe → execution / 探针→执行 | Patch ID, target object/version, field path, baseline-value digest, proposed value, evidence, expiry and affected scope. / 补丁编号、目标对象／版本、字段路径、基线值指纹、建议值、证据、有效期与影响范围。 |
| `adoption_receipt` / 采纳回执 | Execution → probe / 执行→探针 | Patch ID, per-field disposition/reason, actual new object version, affected gates and revalidation references. / 补丁编号、逐字段状态／原因、实际新对象版本、受影响闸门与重验引用。 |

No message directly authorizes business mutation. Only execution's authorized adoption may change a business object. Dispositions are `adopted / 已采纳`, `partially_adopted / 部分采纳`, `rejected / 已拒绝`, `expired / 已过期`, `superseded / 已被替代`. Partial adoption records each field separately. Required revalidation still pending must be stated and cannot close a critical gap. / 消息本身不授权业务变更；只有执行侧授权采纳后才可改变业务对象。采纳状态限定为上述五种，部分采纳须逐字段记录。必需重验未完成时须明示，不得关闭关键缺口。

## Minimum Event Envelope / 最小事件信封

```yaml
event_id: required          # 事件编号
event_type: artifact_gate_decided # 事件类型
run_id: required            # 运行编号
parent_goal_id: required    # 父目标编号
goal_version: null         # 目标版本
plan_version: null         # 计划版本
responsibility_id: null    # 责任编号
task_id: null              # 任务编号
task_contract_version: null # 契约版本号
attempt_id: null           # 尝试编号
executor_instance_id: null # 执行者实例编号
producer_id: required      # 生产者编号
producer_sequence: null    # 生产者序号
occurred_at: null          # 发生时间
received_at: required      # 接收时间
object_ref: null           # 对象引用
object_version: null       # 对象版本
object_digest: null        # 对象指纹：运行时计算
causal_event_id: null      # 因果事件编号
source_category: runtime_record # 来源类别
payload_ref: required      # 负载引用
```

Deduplicate events by `(run_id, event_id)`; isolate divergent payloads under the same ID. Deduplicate messages by unique message ID, preserving the original ID on retry. Repeated delivery is not a new attempt. Producer sequence orders only that producer, never global time; events without child tasks need no invented task/attempt IDs. / 事件按运行编号＋事件编号去重，同编号异载荷隔离；消息按唯一编号去重，重投保留原编号。重复投递不是新尝试。生产者序号只表示本生产者顺序，不是全局时间；无子任务事件不造任务／尝试编号。

## Adoption Workflow and Constraints / 采纳流程与约束

Authenticate sender and authority → deduplicate → check goal/plan versions → check target digest and expiry → enforce field allowlist → verify evidence → classify impact → create a new record/artifact version → rerun affected gates → issue receipt. / 认证发送方与权限→去重→核验目标／计划版本→核验对象指纹与有效期→执行字段白名单→复核证据→判断影响→生成新记录／工件版本→重跑受影响闸门→返回回执。

Unrelated state changes need not invalidate a whole report, but every proposal dependency must remain valid. Changes to goals, task contracts, evidence objects or gate rules require rebasing and recomputation. / 无关状态变化不必废弃整个报告，但须核验提案每项依赖；目标、任务契约、证据对象或闸门规则变更须重建基线并重算。

| Impact / 影响 | Lawful handling / 合法处理 |
| --- | --- |
| Observation timing, associations or derived statistics / 观测时间、关联、派生统计 | Write provenance-bearing observation extensions and retain original events; no business recheck unless used as acceptance evidence. / 写带来源观测扩展并保留原事件；未成为验收依据时无需业务重验。 |
| Formal artifact sources, input mapping or acceptance data / 正式工件来源、输入映射、验收数据 | Authorized writer creates a new artifact version; rerun artifact gate and affected composition gate. / 授权组件生成新工件版本，重跑工件闸及受影响组合闸。 |
| Responsibility, acceptance criteria, authority or budgets / 责任、验收条件、权限、预算 | Submit to original governance workflow for approval and versioning; probe cannot apply. / 交原治理流程批准并版本化，探针不能实施。 |
| Unperformed business responsibility / 业务责任未完成 | Return a business gap/local reassignment recommendation to execution; never manufacture completion. / 返回业务缺口／局部重派建议，不能伪造完成。 |

Probes cannot rewrite parent completion, official verdicts, settled costs, raw event timestamps, business facts or authorization scope. Record fact-valid time, source version, read time and supplementation time separately; newly acquired evidence cannot prove historical possession. / 探针不能改写父目标完成、正式裁决、已结算费用、原始事件时间、业务事实或授权范围。分别记录事实适用时间、来源版本、读取时间与补全时间；新取得证据不能证明历史上已持有。

## Timeout and Closed-Loop Termination / 超时与闭环终止

Noncritical observation timeouts do not block execution; missing required business evidence remains pending or escalates, even with a probe offline. Execution may use its own lawful evidence channels. / 非关键观测超时不阻断执行；必需业务证据缺失时保持待补充或升级，即使探针离线也一样；执行侧可使用自身合法取证渠道。

Deduplicate a gap by `(run_id, goal_version, plan_version, object_id, field_path, rule_version)`, with at most one request in flight. Bound retries, sources, reads, elapsed time and cumulative use; report generation, metric refresh and log repair do not trigger another identical observation. Only new business events, arriving evidence or an explicit recheck can begin a new round. / 缺口按运行、目标版本、计划版本、对象、字段路径、规则版本去重，最多一个请求在途；限制重试、来源、读取、耗时与累计消耗。报告、指标刷新、日志补写不触发同类观测；只有新业务事件、证据到达或明确复核才能开启新轮次。

Sending, adopting and resolving are separate states. Close critical gaps only after evidence is restored and necessary revalidation passes. Exhausted budget, rejection, termination, goal upgrade or unrecoverable evidence ends the round with an explicit reason and unresolved gaps retained. Cancel obsolete requests on goal cancellation/upgrade; do not pretend unconfirmed external reads have stopped, and never write their stale results into a new business version. / 发送、采纳、解决分别记录。证据补齐且必需重验通过后才可关闭关键缺口；预算耗尽、拒绝、终止、目标升级或不可恢复证据，以明确原因结束本轮并保留未解决项。目标取消／升级时取消旧请求，未确认的外部读取不能假装已停止，陈旧结果不得写入新业务版本。
<!-- hierarchy:contract:end -->

## Acceptance Cases / 验收用例

These are expected outcomes from the supplied probe specification; host integration remains pending. / 以下为来源探针规格的预期结果，宿主集成待实现。

<!-- hierarchy:probe_cases:start -->
| ID / 编号 | Scenario and expected behavior / 场景与预期行为 | Source scenario / 来源场景 | Required outcome / 必需结果 |
| --- | --- | --- | --- |
| HPT01 / 探针验收一 | Offline complete snapshot: produce an independent report and unapplied proposals without calling execution. | 无主流程在线，仅有完整离线快照 | 能输出独立报告和未应用提案，不要求调用执行流程 |
| HPT02 / 探针验收二 | Artifacts without responsibility baseline: count artifacts; responsibility coverage remains unknown. | 只有三张工件，没有责任基线 | 可统计工件数；责任覆盖率未知 |
| HPT03 / 探针验收三 | Only one of three obligations fulfills trusted acceptance and selection: report one-third and two business gaps. | 三项责任，可信核验与选择后仅一项履约 | 有效履约覆盖为三分之一；缺少两项业务责任 |
| HPT04 / 探针验收四 | Three valid candidates allowing one, with one selected: candidate excess is two; submitted duplication is zero. | 三份当前候选同属一责任，允许一份；最终只选一份 | 候选超额为二，提交集合重复为零，不混淆两者 |
| HPT05 / 探针验收五 | Two required independent reviews are present: no excess; still verify independence and conflicts. | 约定每项责任需两份独立复核，确有两份 | 不记为超额；仍核验独立性与冲突处理 |
| HPT06 / 探针验收六 | Two passes and one unreadable verdict: coverage unknown, lower bound two-thirds, upper bound one, with reasons. | 三项责任，两项已确认通过，一项裁决不可读 | 覆盖值未知；可报告下界三分之二、上界一和未知原因 |
| HPT07 / 探针验收七 | One event redelivered three times: count once; no extra attempts or candidates. | 同一事件重投三次 | 只记一次，不增加尝试和候选数量 |
| HPT08 / 探针验收八 | One event ID has divergent payloads: quarantine conflict, never choose arbitrarily. | 同一事件编号出现不同内容 | 隔离并报告冲突，不任意择一 |
| HPT09 / 探针验收九 | Correct tag but unsupported conclusion: no tag-based fulfillment; report semantic failure. | 工件责任标签正确，但来源不支撑结论 | 不以标签计有效履约；报告语义核验问题 |
| HPT10 / 探针验收十 | Only start event and incomparable clocks: no invented end or exact duration. | 只有开始事件且时钟不可比较 | 不伪造结束时间或精确耗时 |
| HPT11 / 探针验收十一 | Sampled logs without trusted total: event completeness unknown; no claim of full zero violations. | 日志经过抽样，没有可信总事件数 | 事件完整率未知，不能报告全量零违规 |
| HPT12 / 探针验收十二 | Trusted executor receipt restores missing end: record reconstruction provenance without overwriting original events. | 缺少结束事件，但可信实例回执可恢复 | 标明历史恢复来源，不覆盖原始事件 |
| HPT13 / 探针验收十三 | Business data without trusted source: return work/input gaps; never invent official values. | 原始业务数据没有任何可信来源 | 返回业务补做或输入缺口，不自行生成正式值 |
| HPT14 / 探针验收十四 | Material appeared after the task: label current supplementation, not historical possession. | 新资料仅在原任务之后出现 | 标记当前补充证据，不能证明原任务当时已获证 |
| HPT15 / 探针验收十五 | Proposal targets obsolete goal: do not apply; expire or rebuild it. | 补全提案目标版本已过期 | 不应用，返回过期或重新生成提案 |
| HPT16 / 探针验收十六 | Proposal changes parent completion: reject field and preserve diagnostic and refusal reasons. | 提案要求改父目标完成状态 | 拒绝越权字段，保留诊断和拒绝原因 |
| HPT17 / 探针验收十七 | Adopted proposal but required composition revalidation failed: field adoption counts, critical gap stays open. | 提案已采纳，关键组合重验未通过 | 字段采纳可计入，关键缺口不能关闭 |
| HPT18 / 探针验收十八 | All returned and composition failed: return rate may equal one while parent remains unaccepted. | 所有执行者已回报，组合闸不通过 | 返回率可以为一，但父目标仍未通过 |
| HPT19 / 探针验收十九 | Completion exists but logs unreadable: suspected misreport or unknown, not confirmed violation. | 正式完成状态存在，验收日志不可读 | 报疑似误报或未知；不武断确认违规 |
| HPT20 / 探针验收二十 | Repeated refresh/report triggers: deduplicate, bound usage and prevent self-triggering loops. | 同一缺口被多次刷新或报告触发 | 去重且受预算约束，不形成自激循环 |
| HPT21 / 探针验收二十一 | Probe offline with lawful runtime validation: optional observation does not block; critical evidence follows business rules. | 探针离线，运行时仍有合法验收能力 | 非关键观测不阻塞；关键证据仍依业务规则处理 |
| HPT22 / 探针验收二十二 | Denominator comes from another plan: reject mixed-version calculation and reconstruct grouped baselines. | 把其他计划版本的责任集用于当前统计 | 拒绝混算，按版本分组重建分母 |
<!-- hierarchy:probe_cases:end -->

## Trace Hook / 追踪钩子

Record a project-local report/Trace at `.harness-analysis/<analysis_id>/`, retaining baseline, cutoff, provenance and unresolved gaps. Distinguish documentation checks, constructed examples and observed business outcomes. / 在项目本地保存报告／Trace，保留基线、截止点、来源与未决缺口，区分文档校验、构造示例与观测业务结果。
