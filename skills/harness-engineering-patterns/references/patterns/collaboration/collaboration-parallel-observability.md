# Fan-Out/Gather / 扇出汇聚 Observability Metrics / 可观测性指标

Cell / 交织点: collaboration-parallel / 协作 x 并行
Capability / 能力: Collaboration / 协作
Mode / 模式: Parallel / 并行
Pattern / 模式标识: `PATTERN_0044`; specification / 专用规格: `0.1.0`; status / 状态: draft / 草案。
Source / 来源: User-supplied workflow observability draft / 用户提供的工作流可观测性草案。
Design Pattern File / 设计模式文件: [collaboration-parallel.md](collaboration-parallel.md)

Description / 描述: Independently audit plans, attempts, cards, reports and receipts; compute only supported metrics and recover existing facts under bounded authority. / 独立审计计划、尝试、证据卡、报告和回执；仅计算有依据的指标，并在有界权限内恢复已有事实。

Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。

## Quick Navigation / 快速导航

- [Modes and inputs / 模式与输入](#modes-and-inputs--模式与输入)
- [Probe workflow / 探针流程](#probe-procedure--探针流程)
- [Metric semantics / 指标语义](#metric-semantics--指标语义)
- [Metric catalog / 指标目录](#source-metric-catalog--来源指标目录)
- [Gaps and closure / 缺口与闭环](#gaps-and-closure--缺口与闭环)
- [Supplement contract / 补数契约](#shared-interaction-contract--共享交互契约)
- [Regression cases / 回归用例](#acceptance-cases--验收用例)

## Shared Probe Integration / 共享探针接入

The [source map](../../collaboration-gather-source-map.json) binds the two user-supplied drafts and namespaces source `M01–M17` as `GM01–GM17`. These are specification-only definitions pending dedicated adapters and runtime calculations. No GM calculation is exposed by the current shared runtime. Keep them separate from [shared collaboration probes](../../collaboration-observability-probes.md) and their executable/unsupported CSM subsets. / 来源映射绑定两份用户草案，将原 `M01–M17` 加命名空间为 `GM01–GM17`；这些定义仅为规格，专用适配器与计算仍待实现，当前共享运行时未提供 GM 计算。它们与共享 CSM 指标及其已实现／未支持子集分开维护。

| Related metric / 相关指标 | Distinction / 区别 |
| --- | --- |
| CSM08, CSM12, CSM24 / 共享指标 | Use the shared catalog's original cohorts and definitions, not automatic GM aliases. / 使用共享目录原队列与定义，不自动作为 GM 别名。 |
| CSM32 convergence share / 收口占比 | Time from the last required used branch being ready to whole acceptance, divided by run-to-acceptance time. GM11 instead measures seconds from each round's N04 start to report commit. / 最后一个必要且被采纳分支就绪至整体验收的时长占运行至验收时长的比例；GM11 则计算每轮 N04 开始至报告提交的耗时。 |
| CSM33 unintended duplicate-work cost / 意外重复成本 | Confirmed unnecessary duplicate-work cost / total business cost in scope; excludes planned independent review. GM08 counts verified same-source redundant cards, not wasted work or cost. / 已确认不必要重复工作费用占同范围业务费用，排除计划内独立评审；GM08 统计经核验同源冗余卡，不代表工作浪费或费用。 |

The probe may audit an external workflow without starting the paired execution. It cannot dispatch workers, retry business actions, modify authoritative business state, create missing claims, change R, lower thresholds, grant authority or infer successful delivery. An audit can succeed while the business failed; business completion can coexist with insufficient observation. / 探针可独立审计外部工作流，无需启动配套执行；不可派发、重试业务、改权威状态、创造缺失主张、改 R、降阈值、授予权限或推断成功交接。业务失败时审计可完成，业务完成时观测仍可不足。

## Modes and Inputs / 模式与输入

| Mode / 模式 | Allowed activity / 允许活动 | Output / 输出 |
| --- | --- | --- |
| Offline audit / 离线审计 | Read only imported frozen inputs by default; no external collection authority is implied. / 默认只读导入冻结输入，不隐含外部采集授权。 | Audit, metric states, gaps and unsubmitted suggestions. / 审计、指标状态、缺口及未提交建议。 |
| Online side observation / 在线旁路 | Adapt the event stream and readonly artifacts; version snapshots with watermarks and pending events. / 适配事件流与只读工件，按水位及待到事件生成版本快照。 | Provisional and final snapshots, diagnostics. / 暂定及最终快照、诊断。 |
| Authorized active recovery / 授权主动补采 | Read allowed logs, snapshots and metadata within explicit resources, paths, time and cumulative budgets. / 在明确资源、路径、时间与累计预算内读获准日志、快照和元数据。 | Provenance-bound patches/proposals and adoption/recheck tracking. / 来源绑定补丁／建议及采纳重验跟踪。 |

Minimum input may be one log or report; no input yields a structured insufficient-input report. Missing plan means planned coverage is not computable. Missing original cards/reference conflicts means conflict retention is not computable. No receiver means suggestions can remain unsubmitted without preventing audit completion. / 最小输入可为一份日志或报告，完全无输入时输出结构化输入不足报告。无计划不可算覆盖，无原卡／参考冲突不可算冲突保留；无接收端时建议可未提交，审计仍可结束。

Freeze target workflow/run/plan and probe identity, required/optional obligations, exact artifact revisions/hashes, current authoritative admissions, attempts/tool events and outcomes, original cards/lineage, normalization/conflict/seam rules, report/handoff evidence, adapter/metric versions, watermark/cutoff and optional comparable baselines. Missing fields stay unknown; never reconstruct the expected population from successful returns. / 冻结目标工作流／运行／计划和探针身份、必选／可选责任、精确工件版本摘要、当前权威准入、尝试／工具事件及终态、原卡／血缘、归一化／冲突／接缝规则、报告／交接、适配／指标版本、水位／截止与可选对照；缺字段保持未知，不从成功返回反推全集。

External adapters map planned population, logical shard, attempt, immutable artifact, source location, typed conflict/qualification and actual handoff. A general chain without shard semantics marks dedicated shard/multi-source/incremental-worker metrics not applicable while retaining general event, provenance, failure, latency and recovery observations. / 外部适配器映射预期全集、逻辑分片、尝试、不可变工件、来源定位、类型化冲突限定及实际交接；无分片语义的普通链式流程将专用指标标为不适用，保留通用事件、来源、失败、时延及补数观测。

### ProbeReport / 探针报告

Output immutable report identity/version/hash; target run/plan; mode, adapter and rule versions; input artifact manifest/digests, filters, watermark/cutoff; completed/partial/insufficient/aborted probe status; separate observation quality; metric records; findings with affected nodes, evidence, severity and necessity; gaps; patches and receipts; bounded proposals; submitted/adopted/revalidated/closed gap counts; probe calls/wall-time/tokens/cost or unknown reasons; and a fact/calculation/source ledger. / 输出不可变报告身份版本摘要、目标运行计划、模式与适配规则版本、输入清单摘要及过滤／水位／截止、探针完成／部分／不足／中止状态、独立观测质量、逐指标记录、有据发现与影响／严重性／必要性、缺口、补丁回执、有界建议、分阶段闭环计数、自身开销或未知原因，以及事实／计算／来源账本。

Each metric binds `metric_id, metric_version, run_id, plan_revision, snapshot_id, value, numerator, denominator, unit, status, scope, as_of, provisional, evidence_refs, limitations`. Vector/count/time metrics declare components or units rather than inventing a ratio denominator. / 每项指标绑定身份、版本、快照、数值、分子分母、单位、状态、范围、截止、暂定标记、证据及限制；向量／计数／耗时明确分量或单位，不伪造比例分母。

## Probe Procedure / 探针流程

GP nodes correspond to source P nodes; GPT IDs below are acceptance cases, not workflow nodes. / GP 对应原 P 流程节点；下方 GPT 为验收用例，不是流程节点。

<!-- gather:probe_nodes:start -->
| ID / 编号 | Node / 节点 | Required behavior / 必需行为 |
| --- | --- | --- |
| GP00 / P00 | 确定观测模式、目标与权限 | Choose audit mode, target and permissions. |
| GP01 / P01 | 读取并适配输入，冻结审计快照 | Adapt inputs and freeze an audit snapshot without inventing populations. |
| GP02 / P02 | 核对身份、版本、事件水位与时钟 | Verify identities, versions, producer watermarks and clock trust. |
| GP03 / P03 | 检查数据质量与所需字段 | Check required fields, data quality and source evidence. |
| GP04 / P04 | 生成缺口台账并判断能否恢复 | Classify gaps, necessity, affected scope and recoverability. |
| GP05 / P05 | 在授权范围内补采或确定性复算 | Recover existing facts or derive deterministically within authority and cumulative budgets. |
| GP06 / P06 | 按可比组核验来源、冲突与接缝记录 | Verify lineage, conflicts and seam records by comparable groups. |
| GP07 / P07 | 计算指标，保留分子分母和不可计算原因 | Calculate supported metrics with exact denominators, provenance and unknown reasons. |
| GP08 / P08 | 形成诊断、补丁与限定范围的动作建议 | Propose diagnoses, source-bound patches and bounded actions. |
| GP09 / P09 | 接收采纳与重验回执，更新缺口闭环状态 | Verify adoption, dependency rechecks and explicit closure receipts. |
| GP10 / P10 | 输出、封存报告及自身采集账本 | Seal inputs, report, metric versions, unresolved gaps and collection overhead. |
<!-- gather:probe_nodes:end -->

Deduplicate message IDs before checking per-producer sequence continuity. Record missing sequences and authoritative expected manifests; cross-machine wall clocks cannot establish total order. Distinguish nonexistent data, unrecorded data, denied access and failed reads. Late events revise a new snapshot of their original run/window. / 先按消息去重，再查同生产者序号连续性；记录缺号及权威预期清单，跨机墙钟不能确定全序。区分未发生、未记录、无读取权和读取失败；迟到事件生成原运行窗口的新快照。

## Metric Semantics / 指标语义

| Status / 状态 | Representation / 表示 |
| --- | --- |
| Available / 可用 | Required inputs/rules complete; numeric result, exact cohort and provenance. / 必需输入规则完整，输出数值、精确队列与来源。 |
| Partially available / 部分可用 | Overall value normally null; separately labeled subset value, verified/unknown counts and subset denominator. / 整体通常为空，另列有标签的子集值、已核验／未知数量和子集分母。 |
| Not computable / 不可计算 | `value: null` with missing plan, record, reference set, version or clock reason. / 空值并说明缺少计划、记录、参考集、版本或可信时钟。 |
| Not applicable / 不适用 | `value: null` with a scenario-based reason or no evaluable event. / 空值并说明场景不适用或无可评价事件。 |

Zero is a measured result, not unknown. Zero denominator never becomes 0%, 100% or infinity; distinguish inapplicability from invalid configuration. An allegedly fan-out plan with R empty is invalid. Preserve logical shards, attempts, calls, artifact versions, cards, source families, gaps and runs as distinct counting units. / 零是实测结果而非未知，零分母不填零、百分之百或无穷；区分不适用与配置错误，宣称扇出却 R 为空属于无效输入。逻辑分片、尝试、调用、工件版本、卡片、来源族、缺口与运行分别计数。

Aggregate only comparable definitions/scopes using summed numerators and denominators; use leaf set unions for hierarchical populations and select one explicit report revision per run. Nine qualified leaves plus one failed leaf yield 9/10, not an average of two group percentages. Include running and censored attempts and sample sizes. / 仅汇总同定义同范围的分子分母；分层使用叶子集合并集，每次运行选定一个明确报告版本。九片合格加一片失败为 9/10，不平均两组百分比；披露运行中、截尾尝试和样本数。

Durations need monotonic time in one trusted domain or documented offset correction/error bounds. Untrusted cross-machine differences are unknown; negative durations cannot be clamped to zero. Online incomplete snapshots are provisional. / 耗时要求同可信域单调时间或有记录的偏移校正／误差界；不可信跨机时差保留未知，不把负时长截为零；在线不完整快照标暂定。

### Four Core Measures / 四项核心观测

- **GM01 / M01 Qualified required-shard coverage / 必选分片覆盖率:** R is frozen required logical shards, Q contains only shards whose entire required object/proposition/dimension obligations satisfy local identity, format, comparison and source rules. Report |Q|/|R|, R−Q, optional coverage and obligation detail. Global seam failure does not erase local Q; conflicts remain separately visible. / R 为冻结必选逻辑分片，Q 仅含全部必要义务满足局部规则者；输出比率、缺片、可选覆盖与责任明细，接缝失败不删除局部 Q，冲突另列。
- **GM02 / M02 Independent-evidence ratio / 独立证据率:** Per comparable proposition group, N is effective card count and I is verified upstream source-family count; output I/N with lineage evidence and verification scope. This operational ratio is neither statistical independence nor truth probability. Any unverified lineage makes the overall value null; publish a clearly scoped subset if possible. Three cards from one announcement give 1/3 even from different workers or URLs. / 每个可比命题组以有效卡数 N、已核验上游来源族 I 计算，披露血缘范围；不代表统计独立或正确概率。血缘未知时整体为空，可另列子集；三卡同公告为 1/3。
- **GM03 / M03 Conflict retention / 冲突保留率:** K comes from human labels, fixture labels or independent recomputation of frozen original cards. H is the subset whose identity, both sides, qualifications and sources survive both report and a verifiably generated/sent handoff. Output |H|/|K| with missing conflict IDs. A dispute label alone does not qualify. Resolved conflicts retain original evidence and adjudication. No reference set or no handoff means not computable; K empty is not applicable. A self-detected conflict denominator is only a labeled self-check proxy, not this full metric. / K 来自人工、样例标签或冻结原卡独立复算；H 要求身份、双方、限定和来源同时保留在报告及有生成发送证据的交接中。仅“存在争议”不足，已解决冲突保留原证据与裁决；无参考集或交接不可计算，K 空不适用；自检分母仅作标注代理。
- **GM04 / M04 Added-worker increment / 新增执行者增量:** Freeze the same task population, comparison/source/quality policies and window before comparing coverage, source-family, cost and wall-time deltas; retain token/call/retry/gather overhead. No comparable baseline means no increment estimate. A single run or leave-one-worker-out recomputation may show observed unique contributions, not causal scheduling/cost/latency benefits. No universal utility score or post-hoc weights; unknown costs stay unknown, and nonpositive cost deltas do not justify mechanical per-currency ratios. / 先冻结同一任务全集、可比／来源／质量政策与窗口，再比较覆盖、来源族、费用及墙钟差并保留开销；无可比基线不估增益，单次运行或移除结果复算仅说明独有贡献，不证明因果收益；不设通用总分或事后权重，未知费用保留未知，非正费用增量不机械算每元收益。

Global source-family counts are descriptive and cannot replace within-proposition evidence. Summed per-group family counts may reuse one source across groups and must not be labeled globally unique. GM11 round closeout is report commit minus that round's N04 start, separate from pre-gather waiting, shared CSM32 timing and end-to-end wall time. / 全局来源族数仅为描述，不能替代同命题证据；组内计数相加可能跨组重复，不称全局唯一。GM11 为每轮报告提交减该轮 N04 开始，与聚合前等待、共享 CSM32 计时及端到端墙钟分开。

## Source Metric Catalog / 来源指标目录

All definitions below are design-only; each source locator remains in the map. Implement only the selected scenario profile and version changed definitions instead of silently replacing denominators. / 下列均为设计定义，映射保留来源定位；仅实现所选场景配置，定义变化须升级版本，不静默替换分母。

<!-- gather:metrics:start -->
| ID / 编号 | Metric / 指标 | Definition and boundary / 定义与边界 | Original formula and limits / 原口径与限制 |
| --- | --- | --- | --- |
| GM01 / M01 | Required-shard coverage / 必选分片覆盖率 | Qualified required logical shards / frozen required shards. Include every required obligation; no plan means not computable. | 必选分片覆盖率 = &#124;Q&#124; / &#124;R&#124;<br>缺失分片集合 = R − Q |
| GM02 / M02 | Independent-evidence ratio / 独立证据率 | Verified upstream source families / effective cards in one comparable group. Unknown lineage makes the overall value null; this is not truth probability. | 独立证据率 = I / N |
| GM03 / M03 | Conflict retention / 冲突保留率 | Independent reference conflicts fully preserved in report and evidenced handoff / reference conflicts. No reference or handoff means not computable; empty reference is not applicable. | 冲突保留率 = &#124;H&#124; / &#124;K&#124; |
| GM04 / M04 | Added-worker increments / 新增执行者的增量收益 | Changes in coverage, verified source families, cost and wall time under the same frozen task and policies. No comparable baseline means no increment or causal claim; keep other overhead. | 覆盖增量 = 新配置覆盖率 − 基线覆盖率<br>来源增量 = 新配置已核验来源族数 − 基线已核验来源族数<br>费用增量 = 新配置总费用 − 基线总费用<br>时长变化 = 新配置墙钟时长 − 基线墙钟时长 |
| GM05 / M05 | Absence disclosure / 缺席披露率 | Correctly disclosed missing required shards / independently reconciled missing required shards. No missing shards is not applicable; no plan is not computable. | 最终报告中正确列出的缺失必选分片数 ÷ 独立核对得到的实际缺失必选分片数；需要冻结 R、有效 Q 和报告；无缺片时不适用，缺计划时不可计算 |
| GM06 / M06 | Comparison-field completeness / 可比口径完整率 | Cards meeting required comparison fields / cards under review. Completeness is not truth; incomplete inventory permits subset reporting only. | 必要对象、时间、单位、分母等字段满足场景契约的卡数 ÷ 当前待验卡数；字段不适用必须有规则；完整不等于内容正确；卡清单不完整时只报子集 |
| GM07 / M07 | Source-chain completeness / 来源链完整率 | Cards with required claim-card-source-version/snapshot chain / cards requiring checks. Reachability does not prove source independence. | 必须的主张—卡—来源—版本／快照定位均可回溯的卡数 ÷ 应检查卡数；必须来源链清单由场景定义；来源血缘独立性是另一个检查，不因地址可访问就通过 |
| GM08 / M08 | Same-source redundancy / 同源重复率 | Verified redundant cards / effective cards in one comparable group. Unknown lineage makes overall value null; keep all originals and mappings. | 同一可比组内，因已核验同源关系被标记为冗余的卡数 ÷ 有效卡数；未核验血缘时整体值为空；保留代表卡与原卡映射，不实际删除原件 |
| GM09 / M09 | Final shard timeout rate / 分片最终超时率 | Required logical shards finally timed out / frozen required shards. A failed timeout attempt followed by success is not a final shard timeout; online values are provisional. | 最终以超时收口的必选逻辑分片数 ÷ 冻结必选分片数；需权威终态与截止政策；在线仍运行时标暂定；曾超时后成功不计最终超时 |
| GM10 / M10 | Artifact rejection rate / 工件拒收率 | Distinct submitted versions rejected / distinct submitted versions entering admission. Deduplicate deliveries and disclose pending checks or unknown outcomes. | 在选定快照被明确拒收的唯一提交工件版本数 ÷ 进入准入检查的唯一提交工件版本数；先按工件版本去重；待检查版本另列，终态未知时整体不完整 |
| GM11 / M11 | Aggregation-round closeout time / 收口耗时 | Report commit time minus that round's N04 start; exclude waiting before aggregation and keep rounds and end-to-end time separate. Untrusted clocks mean not computable. | 单轮聚合报告提交时刻 − 该轮 N04 聚合开始时刻；不含开始聚合前等待分片的时间；补数多轮分别计时，另报端到端总时长；时钟不可信时不可计算 |
| GM12 / M12 | Seam-check coverage / 接缝检查覆盖 | Required seam rules with known pass/fail / frozen required rules. Show pass/fail/unknown counts; checked failure is not passing; empty applicable set is not applicable. | 已有确定结果的必需接缝规则数 ÷ 冻结必需规则数，并另列通过、失败、未知数；失败规则属于已检查，但绝不等于通过；无适用规则时不适用并说明 |
| GM13 / M13 | First-attempt artifact qualification / 首次工件合格率 | Required shards qualified on first attempt / required shards with first attempt started. Disclose unstarted shards and provisional unfinished first attempts. | 首次尝试即产出满足局部契约工件的必选分片数 ÷ 已启动首次尝试的必选分片数；在线首次尝试未结束时结果暂定；未启动分片另列，不能隐藏调度缺口 |
| GM14 / M14 | Retry amplification / 重试放大率 | Business attempts / distinct started logical shards. No retries gives one; exclude probe reads; no starts is not applicable. | 业务执行尝试总数 ÷ 已启动的唯一逻辑分片数；无重试且每片启动一次时为 1；探针读取不计业务尝试；无启动时不适用 |
| GM15 / M15 | Supplement closure / 补数闭环率 | Due recoverable gaps with source verification, adoption, recheck and closure evidence / all due recoverable gaps. Count gap IDs; separate future and unrecoverable gaps. | 已通过来源核验、被采纳、完成重验且关闭的可恢复缺口数 ÷ 已到处理截止点的可恢复缺口数；按缺口标识去重，不按补丁条数；新发现未到期缺口另列；不可恢复业务证据缺口单列 |
| GM16 / M16 | Critical event completeness / 关键事件记录完整率 | Verified critical instances / authoritative expected instances from a frozen plan, state or producer manifest. Received events cannot define their own denominator. | 已核验的关键事件实例数 ÷ 应有关键事件实例数；分母来自冻结计划、权威状态或生产者清单，不以已收到事件反推；缺少可信清单时不可计算 |
| GM17 / M17 | Probe overhead / 探针观测开销 | Actual reads, wall time, tokens and costs separately. Probe and business accounting share the global cap; unknown costs stay null; no baseline means no causal business-delay claim. | 探针实际读取次数、墙钟时长、令牌、费用分别报告；与业务分账且共享总授权上限；费用未知不填零；无对照不声称探针增加了多少业务延迟 |
<!-- gather:metrics:end -->

## Gaps and Closure / 缺口与闭环

| Gap / 缺口 | Allowed resolution and boundary / 允许恢复与边界 |
| --- | --- |
| Existing metadata or history / 已有元数据或历史 | Read bound immutable snapshots or authoritative logs; keep occurrence and collection times distinct. / 读取绑定不可变快照或权威日志，发生与采集时间分开。 |
| Deterministic derivation / 确定性推导 | Preserve inputs, formula, rule version and source evidence. / 保留输入、公式、规则版本和来源。 |
| Missing business evidence / 缺业务证据 | Propose bounded execution collection; never fabricate a claim. / 建议限定执行补证，不生成伪造主张。 |
| Unknown lineage / 血缘未知 | Verify allowed upstream relationships or retain unknown. / 核验获准上游关系，否则保持未知。 |
| Missing historical snapshot / 历史快照缺失 | Mark unrecoverable; current content cannot backfill history. / 标不可恢复，不用当前内容倒填历史。 |
| Incomplete events or clocks / 事件或时钟不完整 | Request replay/authoritative manifest or degrade affected metrics. / 请求重放／权威清单或降级相关指标。 |
| Authorization/budget exhausted / 权限或预算不足 | Stop reads, retain partial results and gaps; no lowered gate. / 停止读取，保留部分结果和缺口，不降低闸门。 |

A gap record binds gap/run/plan, exact target/field, cause, necessity, impacted business nodes/metrics, allowed sources, method, deadline, budget, status and evidence. Supplement submitted, adopted, revalidated and closed are separate facts. GM15 counts only due recoverable gap IDs whose source validation, adoption, dependency recheck and closure are evidenced; overdue open gaps stay in the denominator, future gaps and unrecoverable evidence are listed separately. / 缺口记录绑定身份计划、目标字段、原因、必要性、影响节点指标、允许来源、方法、截止预算、状态及证据；提交、采纳、重验、关闭分别记录。GM15 仅统计处理截止已到、来源核验／采纳／依赖重验／关闭都有据的可恢复缺口，逾期未闭环留在分母，未到期与不可恢复证据另列。

More complete observation may expose a new conflict or common source and reduce business admission; it does not imply improved business quality. Probe failures report their own partial state and cost without changing business success. / 观测更完整可能揭示新冲突或同源，进而使业务不再准入，不等于业务质量提高；探针故障报告自身部分状态与开销，不改业务成功状态。

## Shared Interaction Contract / 共享交互契约

Canonical maintained source / 规范维护源: [collaboration-gather-contract.md](../../collaboration-gather-contract.md).

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

## Observability Metrics / 可观测性指标

- 质量指标 / Quality Metrics: GM01 coverage, GM02 independence, GM03 retained conflicts, GM05–GM08 data integrity and GM12/GM13 checks. / 覆盖、独立性、冲突保留、数据完整性及检查。
- 时延指标 / Latency Metrics: GM09 final logical-shard timeouts and GM11 aggregation-round latency; wall-clock comparison needs a comparable baseline. / 逻辑分片最终超时、逐轮收口时延，墙钟比较须可比基线。
- 成本指标 / Cost Metrics: GM04 comparable deltas, GM14 retry amplification and GM17 actual probe costs. / 可比增量、重试放大和探针实际开销。
- 风险指标 / Risk Metrics: Unresolved necessary conflicts, missing provenance, failed/unknown seams and unauthorized/stale patches. Probe findings go to the execution owner. / 必要未决冲突、缺来源、接缝失败或未知、越权或过期补丁；发现交执行负责人。
- Trace 指标 / Trace Metrics: GM07 source chains, GM15 verified closure and GM16 authoritative event completeness. / 来源链、有据闭环与权威事件完整性。

Diagnose low diversity through sources and execution records; it alone proves neither isolation failure nor unnecessary parallelism. Do not set universal worker-count, cost or independence thresholds. Owned scenario policy determines business gates; optional observation loss alone is not a business veto. / 低多样性须结合来源与执行记录诊断，不能单独证明隔离失败或并行无用；不设通用人数、费用或独立性阈值。业务闸门由有责任人的场景政策决定，可选观测缺失本身不否决业务。

### Scenario Profiles and Fixed Examples / 场景配置与固定样例

Research prioritizes coverage, lineage, comparison and retained conflict; document batches prioritize omission, duplicates and timeouts; reconciliation prioritizes units, denominators, source chains and total seams; code scans bind repository/rule versions and cross-module checks; operations prioritize event/clock quality. Disable inapplicable metrics explicitly. / 研究优先覆盖、血缘、口径及冲突；文档批次优先遗漏、重复和超时；对账优先单位、分母、来源链及总量接缝；扫描绑定仓库／规则版本及跨模块检查；运维优先事件／时钟质量；不适用指标显式关闭。

Fixed expectations / 固定预期: source-version repair may change 2/3 to 3/3 only after execution rechecks; three same-source comparable cards give GM02=1/3 and GM08=2/3; one of two independently labeled conflicts fully delivered gives GM03=1/2; adding coverage can still add zero source families. All are fixture expectations, not production measurements. / 来源版本补数仅在执行重验后可将覆盖从 2/3 变为 3/3；三张同源可比卡独立率 1/3、重复率 2/3；两个独立标注冲突完整交接一个则保留率 1/2；覆盖增加仍可能来源增量为零。以上为样例预期，不是生产测量。

## Acceptance Cases / 验收用例

All 20 cases remain pending host integration, including offline operation without an execution receiver. Documentation tests check faithful mapping and synchronization, not business outcomes. / 以下 20 项均待宿主集成，包括无执行接收端的独立审计；文档测试只核验映射与同步，不验证业务结果。

<!-- gather:probe_cases:start -->
| ID / 编号 | Scenario / 场景 | Required outcome / 必需结果 |
| --- | --- | --- |
| GPT01 / P01 | 已知三片，两片合格 | Two of three qualified shards gives 2/3 coverage and a missing shard. / M01 为 2/3；缺席清单能定位第三片 |
| GPT02 / P02 | 只有成功结果，没有计划 | No plan means no coverage denominator even with successful results. / 覆盖不可计算；不把结果数量当作计划全集 |
| GPT03 / P03 | 同一分片重试并重复投递事件 | Deduplicate shard coverage and messages; count actual attempts for retries. / 覆盖不重复计数；重试放大率使用尝试数 |
| GPT04 / P04 | 同命题三卡同一上游来源 | Three same-source cards give independence 1/3 and redundancy 2/3; keep originals. / M02 为 1/3，M08 为 2/3，原始卡仍在 |
| GPT05 / P05 | 三卡不同网址但血缘未核验 | Different URLs with unknown lineage give overall null independence. / M02 整体为空，列出未知来源，不自动计为三份独立证据 |
| GPT06 / P06 | 会话隔离、工作区共享、工具受限 | Different isolation dimensions are neither votes nor comparable conflicts. / 不误标为同维度冲突，不做多数表决 |
| GPT07 / P07 | 两个参考冲突只完整交接一个 | One of two reference conflicts fully delivered gives 1/2 retention; locate the lost conflict. / M03 为 1/2，并能定位丢失的冲突 |
| GPT08 / P08 | 无参考冲突、无可靠参考集或无交接记录 | Empty reference, missing reliable reference and missing handoff get appropriate null states. / 分别标不适用或不可计算；不伪造百分之百 |
| GPT09 / P09 | 事件时间来自不可信跨机时钟 | Untrusted cross-machine clocks cannot provide definite corrected latency. / 不输出未经校正的确定时延，记录时钟限制 |
| GPT10 / P10 | 读取当前网页尝试补历史版本 | Reject current-page historical backfill and record the unrecoverable/snapshot gap. / 拒绝历史倒填，生成不可恢复或需历史快照的缺口 |
| GPT11 / P11 | 补丁已发送但没有采纳或重验回执 | Sent patches without adoption and recheck receipts are not closed. / 不计补数闭环，不声称业务状态已改善 |
| GPT12 / P12 | 补丁试图改 `accepted` 或原始主张 | Reject and audit changes to accepted or raw claims. / 拒绝并留下审计记录 |
| GPT13 / P13 | 旧版本补丁到达已修订工件 | Reject or reevaluate a superseded-base patch. / 拒绝或重新评估，不能无条件套用 |
| GPT14 / P14 | 没有执行流程接收端 | Audit independently without an execution receiver or new business run. / 独立生成报告与建议，仍可完成审计，不触发业务运行 |
| GPT15 / P15 | 探针预算耗尽或来源无权限 | Stop active reads on budget or authority limits; report partial evidence. / 停止主动采集，输出部分结果与明确限制 |
| GPT16 / P16 | 新增执行者但没有可比基线 | No comparable baseline means no causal gains, only evidenced contribution. / 不输出因果收益；仅可报告可核验贡献 |
| GPT17 / P17 | 一组九片合格、一组一片失败 | Nine qualified leaves and one failed leaf gives 9/10, not group average. / 叶子覆盖为 9/10，不把两组平均为 1/2 |
| GPT18 / P18 | 单执行者链式流程没有分片语义 | No shard semantics means dedicated metrics not applicable; keep general probes. / 专用指标标不适用，通用事件与补数观测照常 |
| GPT19 / P19 | 观测事件再次进入被观测事件流 | Isolate observation namespaces to prevent recursive probes and inflated business calls. / 命名空间隔离，避免递归触发和虚增业务调用 |
| GPT20 / P20 | 聚合器与探针采用不同指标／规则版本 | Reject unexplained comparisons across incompatible metric/rule versions. / 拒绝无说明的直接比较，输出版本不兼容提示 |
<!-- gather:probe_cases:end -->

## Maintenance / 维护

Use `scripts/sync_collaboration_gather_docs.py --write` after changing the maintained source map or shared contract, then run the skill validator and tests. Preserve raw snapshots, original metric IDs, unimplemented status and old report versions. / 修改来源映射或共享契约后运行专用同步脚本，再运行技能校验和测试；保留原始快照、来源指标编号、未实现状态与旧报告版本。
