# Pattern Combination Observability Probes / 模式组合可观测性探针

For evidence-based architecture selection and baseline comparison, use the separate [selection probes](pattern-selection-observability-probes.md) and [selection exchange contract](pattern-selection-contract.md). Keep `pattern-selection/0.1.0` metrics distinct from this composition profile; correlate explicit run/object/version bindings rather than aliasing event or metric IDs. / 架构选型与基线比较使用独立的选型探针及选型交互契约。选型指标与本组合配置保持独立，通过明确运行对象版本关联，不把事件或指标 ID 互作别名。

Name / 名称: Pattern Combination Probe Profile / 模式组合探针配置. Description / 说明: independently reconstruct task, state, evidence, decision, action, authority, responsibility and outcome / 独立重建任务、状态、证据、决策、动作、权限、责任与结果八条观察线。

Version / 版本: `0.1.0`; status / 状态: draft / 草案; implementation / 实现: `specification_only`. Parent pattern / 所属模式: `PATTERN_0052`; source alias / 来源别名: `PATTERN_OBSERVABILITY_PROBE_0001`; composition / 组合: `PATTERN_0053`.

## Quick Navigation / 快速导航

[Modes / 模式](#modes) · [Catalog / 目录](#catalog) · [Metrics / 指标](#metrics) · [Placement / 布置](#placement) · [Report / 报告](#report) · [Contract / 契约](pattern-combination-contract.md) · [Execution / 执行](pattern-combination-execution-flow.md) · [Sources / 来源](pattern-combination-source-map.json).

<a id="modes"></a>
## Usage and Modes / 用途与运行模式

Use only relevant probes for the task; this document defines rules and data requirements, not deployed collectors or calculators. Source probe IDs live in `pattern_combination/0.1.0`; existing shared runtime probes and their `0.8.0` protocol retain their own semantics. / 按任务选择必要探针；本文件定义规则和数据要求，不代表采集器计算器已经部署。来源探针使用专属名称空间，既有共享运行探针及其 `0.8.0` 协议保留原有语义。

| Mode / 模式 | Behavior / 行为 |
| --- | --- |
| Offline / 独立离线 | Correlate completed/interrupted run logs, snapshots and artifacts; report gaps; request data only if an authorized original source remains available. / 关联结束中断运行日志快照工件并报缺口，原来源仍可授权访问才请求补数。 |
| Online read-only / 独立在线 | Consume events or query permitted sources to build an independent read view; never write business state. / 消费事件或查询允许来源建立独立视图，不写业务状态。 |
| Interactive / 交互增强 | Exchange standardized events, bounded enrichment requests/responses, findings and disposition receipts. / 交换标准事件、有界补全请求响应、发现及处理回执。 |
| Governance-linked / 治理联动 | Explicit configuration may submit a control request; independently authorized governance decides and applies it. / 明确配置下可提交控制请求，具独立授权的治理入口决定并执行。 |

Workflow: ingest → normalize and authenticate → correlate → reconstruct topology/state → establish expected populations → run enabled probes → request permitted missing originals → revise findings → report and verify disposition. Observation repair never automatically repairs a business defect. / 流程为采集、规范认证、关联、重建拓扑状态、建立预期总体、运行已启用探针、请求允许的缺失原记录、修订发现、报告与核验处理；修补观测不自动修复业务缺陷。

<a id="catalog"></a>
## Probe Catalog / 探针目录

The source map retains complete dependencies, formulas, anomaly conditions and outputs for every probe, beyond these operational summaries. Every finding includes source evidence, confidence, affected scope, owner and a proposed return point. / 来源映射保留各探针的完整依赖、公式、异常条件与输出，以下为操作摘要；每项发现带来源证据、置信、影响范围、责任和建议返回点。

| ID | Name / 名称 | Dependencies / 依赖 | Trigger and output / 触发与输出 |
| --- | --- | --- | --- |
| PROBE_TASK_001 | Task boundary and delivery / 任务边界与交付完整性探针 | Task contract, boundary revisions, required output, acceptance and completion events. / 任务契约、边界修订、必需输出、验收完成事件。 | Omitted deliverable, unapproved scope change or premature completion → list missing work/criteria and request completion review. / 漏交付、未经批准范围变化或提前完成 → 列缺项验收并请求复核。 |
| PROBE_TOPOLOGY_001 | Topology and aggregation / 链路、分支与聚合完整性探针 | Plan, parent/child inventory, branch lifecycle and aggregation inputs. / 计划父子清单、分支生命周期与聚合输入。 | Unfinished/missing branch, orphan result, unexplained cancellation, duplicate or version conflict → identify branch and recovery owner. / 分支未完缺失、孤立结果、取消无理由、重复版本冲突 → 定位分支与恢复责任。 |
| PROBE_STATE_001 | State and recovery / 状态一致性与可恢复性探针 | Transitions, state/plan versions, external receipts and checkpoints. / 迁移、状态计划版本、外部回执与检查点。 | Completed task with live nodes, effect/state mismatch, stale recovery or replay risk → identify trusted source and request reconciliation. / 完成任务仍有运行节点、效果状态不符、陈旧恢复或重放风险 → 明确信源并请求核对。 |
| PROBE_DEPENDENCY_001 | Dependency readiness / 依赖满足与非法跨步探针 | Graph, ready/start events, preconditions, authority and budgets. / 任务图、就绪开始事件、前置权限与预算。 | Missing backup, dependency or authority at dispatch → record illegal start, missing prerequisite and safe return point. / 派发时缺备份依赖权限 → 记录非法启动、缺前置及安全返回点。 |
| PROBE_EVIDENCE_001 | Evidence traceability / 证据覆盖与原文回溯探针 | Claims, evidence references, original locator, source version/time, invalidation/conflict. / 命题证据引用、原定位版本时间及失效冲突。 | Summary-only, inaccessible or invalid evidence, low-confidence action premise → list unverifiable claims and originals to retrieve. / 只有摘要、来源不可达失效或动作前提低置信 → 列不可核验命题与待取原文。 |
| PROBE_COMPRESSION_001 | Compression fidelity / 压缩损失与例外保留探针 | Original and summary, entities/dates/values/negations/exceptions, downstream artifacts and reviews. / 原文摘要、实体日期数值否定例外、下游工件评审。 | Lost exception/date/scope, overwritten regional distinction or overstated certainty → identify affected claims and request recompression/original review. / 丢例外日期范围、抹平地域差异或过度确定 → 定位受影响结论并请求重压缩回原文。 |
| PROBE_HYPOTHESIS_001 | Hypothesis update / 假设验证与调查转向探针 | Candidate causes, chosen check, expected discriminating result, actual observation and next route. / 候选原因、检查、预期区分结果、实际观察及后续路由。 | Refuted cause still drives repairs, aimless tests or premature broad fix → return to investigation or planning with evidence. / 被否原因仍驱动修补、无目的检查或过早广改 → 据证返回调查规划。 |
| PROBE_LOOP_001 | Retry and budget / 循环、重试与预算探针 | Loop/attempt IDs, objectives, input/output digests, changes, new evidence and hierarchical budgets. / 循环尝试号、目标、输入输出摘要、差异新证及分层预算。 | Repeated unchanged work, no gain, nested overspend, approval wait retried or guard bypass → request stop/reroute/takeover. / 无差异重复、无增益、嵌套超支、审批等待重试或绕闸 → 请求停止换路接管。 |
| PROBE_ACTION_001 | Preconditions and outcome / 动作前置条件与结果核验探针 | Action target/input, pre-check, tool receipt, actual effects, post-query and compensation. / 动作对象输入、前查、工具回执、实际效果、后查补偿。 | No live pre-check/query, false success, unaccounted partial effects or missing recovery → identify objects for verification/compensation. / 缺实时前后查、假成功、部分效果未记或无恢复 → 定位待核验补偿对象。 |
| PROBE_GOVERNANCE_001 | Approval and scope / 审批、权限与爆炸半径探针 | Approval/action identity, target/version, scope, limits/time, actual affected inventory and permission check. / 审批动作号、对象版本范围、限额时间、实际影响清单及权限检查。 | Stale/mismatched approval, excessive targets or tool permission without business scope → list exact mismatches and request governance review. / 审批过期失配、超对象或接口权限无业务范围 → 列精确失配并请求治理复核。 |
| PROBE_REVIEW_001 | Review closure / 评审覆盖与问题闭环探针 | Review version/criteria, originals, issues, revision, closure and release. / 评审版本标准、原文、问题修订关闭与放行。 | Unreviewed mandatory object, stale review, unsupported closure or open severe issue at release → request revalidation. / 必需对象未审、旧评审、关闭无依据或严重问题未关即放行 → 请求复验。 |
| PROBE_HANDOFF_001 | Handoff responsibility / 交接责任与版本完整性探针 | Handoff package/version, receiver, completed/pending work, evidence, checkpoint, receipt and transfer. / 交接包版本、接收者、已完未完、证据检查点、接收与转移。 | Wrong artifact version, missing evidence/return point, unaccepted handoff or ownerless work → request return or corrected transfer. / 工件版本错误、缺证据返回点、未接收或责任悬空 → 请求退回或纠正转移。 |
| PROBE_ACCEPTANCE_001 | Truthful completion / 终态验收与完成真实性探针 | Five-gate records, business query, unresolved issues and completion claim. / 五门记录、业务查询、未解决问题与完成声明。 | Any mandatory gate pending/failed or unaccounted unauthorized/partial effects → report premature completion and accountable return node. / 必需门待定失败或越权部分效果未处理 → 报提前完成及责任返回节点。 |
| PROBE_EFFICIENCY_001 | End-to-end value / 成本、时延与人工接管价值探针 | Latency, model/tool/human cost, errors/rework/takeover, matched with/without-component runs and final quality. / 时延、模型工具人工成本、错误返工接管、组件有无的匹配对照及最终质量。 | Added latency/cost without quality or risk benefit → propose keep, tune, risk-based use, trial or removal. / 增加时延成本而无质量风险收益 → 建议保留调整按风险启用对照或撤销。 |

<a id="metrics"></a>
## Metric Definitions / 指标定义

`PCM-01`–`PCM-54` are local source locators, not executable metric registrations. The bilingual formula table below preserves the original formulas. Freeze population, time window, contract/version, units and sampling before computing. Unknown inputs produce `unknown`; complete empty populations produce `not_applicable`, neither zero nor a passing rate. Coverage and passing rates are different. Qualitative judgments need a versioned rubric and independently reviewable inputs. / `PCM` 为本地来源定位编号，不是可执行指标注册；下表中英公式保留原式。计算前冻结总体、时间窗、契约版本、单位与采样。输入未知则未知，已知空总体则不适用，都不能当零或通过率。覆盖率不等于通过率；定性判断须有版本量规及可独立复核输入。

| ID | Definition / 定义 | Source formula / 原始公式 |
| --- | --- | --- |
| PCM-01 | Delivery coverage = satisfied mandatory deliverables / all mandatory deliverables | 交付覆盖率 = 已满足的必需交付项数量 ÷ 必需交付项总数 |
| PCM-02 | Acceptance coverage = mandatory criteria with an explicit determination / all mandatory criteria | 验收覆盖率 = 已有明确结论的强制验收项数量 ÷ 强制验收项总数 |
| PCM-03 | Unexplained gaps = missing mandatory items without a reason | 未说明缺口数 = 缺失且未给出原因的必需项数量 |
| PCM-04 | Branch recovery = required started branches with aggregatable results / all required started branches | 分支回收率 = 已形成可聚合结果的必需分支数量 ÷ 已启动的必需分支数量 |
| PCM-05 | Orphan nodes = nodes without valid parent, entry or exit | 孤立节点数 = 无有效父节点、无入口或无出口的节点数量 |
| PCM-06 | Aggregation gaps = required branches absent from the aggregation manifest | 聚合缺口数 = 聚合清单中缺少的必需分支数量 |
| PCM-07 | Duplicate branch ratio = semantically redundant branches without added value / all branches | 重复分支率 = 语义上重复且未产生新增价值的分支数量 ÷ 总分支数量 |
| PCM-08 | State consistency = consistent state reads / all state reads | 状态一致率 = 一致的状态读取次数 ÷ 总状态读取次数 |
| PCM-09 | Version conflicts = writes whose read version is stale | 版本冲突数 = 写入时发现读取版本已过期的次数 |
| PCM-10 | Recoverable node ratio = long-running nodes with valid checkpoints / all long-running nodes | 可恢复节点率 = 具有有效恢复点的长时节点数量 ÷ 长时节点总数 |
| PCM-11 | Duplicate effect risks = nodes that may repeat an external effect after recovery | 重复执行风险数 = 恢复后可能再次产生相同外部效果的节点数量 |
| PCM-12 | Dependency violations = starts with an unsatisfied mandatory dependency | 依赖违规次数 = 未满足必需依赖却启动节点的次数 |
| PCM-13 | False-ready ratio = ready nodes actually lacking conditions / all ready nodes | 就绪误判率 = 被标记就绪但实际缺少条件的节点数量 ÷ 就绪节点数量 |
| PCM-14 | Skipped steps = downstream actions started after skipping required nodes | 跨步次数 = 跳过必需节点直接执行后续动作的次数 |
| PCM-15 | Evidence coverage = key claims with valid supporting evidence / all key claims | 证据覆盖率 = 有有效证据支持的关键结论数量 ÷ 关键结论总数 |
| PCM-16 | Original traceability = key claims locatable in original material / all key claims | 原文回溯率 = 可定位到原始片段的关键结论数量 ÷ 关键结论总数 |
| PCM-17 | Invalid evidence ratio = invalid evidence references / all evidence references | 失效证据占比 = 已失效证据引用数量 ÷ 总证据引用数量 |
| PCM-18 | Single-source dependence = high-risk claims supported by one source / all high-risk claims | 单源依赖率 = 仅由单一来源支持的高风险结论数量 ÷ 高风险结论数量 |
| PCM-19 | Exception retention = key exceptions retained in summary / key exceptions in original | 例外保留率 = 摘要中保留的关键例外数量 ÷ 原文关键例外总数 |
| PCM-20 | Qualification retention = scope, date and conditions retained in summary / corresponding original items | 限定条件保留率 = 摘要中保留的适用范围、日期和条件数量 ÷ 原文对应数量 |
| PCM-21 | Key fact differences = original-summary differences in objects, values, dates, negation and conditions | 关键事实差异数 = 原文与摘要在对象、数值、日期、否定和条件上的差异数量 |
| PCM-22 | Discriminating check ratio = checks distinguishing at least two explanations / all checks | 有效检查率 = 能区分至少两个候选解释的检查数量 ÷ 总检查数量 |
| PCM-23 | Timely hypothesis update = updates at the next step after refuting evidence / refuting observations | 假设更新及时率 = 否定证据后在下一步更新假设的次数 ÷ 否定证据次数 |
| PCM-24 | Irrelevant check ratio = checks unrelated to current candidate causes / all checks | 无关检查率 = 与当前候选原因无明显关系的检查数量 ÷ 总检查数量 |
| PCM-25 | Budget consumption = consumed budget / available budget | 预算消耗率 = 已消耗预算 ÷ 可用预算 |
| PCM-26 | Repeated attempt ratio = attempts with near-identical inputs, parameters and actions / all attempts | 重复尝试率 = 输入、参数和动作近似相同的尝试数量 ÷ 总尝试数量 |
| PCM-27 | Stagnant rounds = consecutive rounds without new evidence, state change or effective difference | 信息增益停滞轮数 = 连续没有新增证据、状态变化或有效差异的轮数 |
| PCM-28 | Retry benefit = retries resolving a local problem / all retries | 重试收益率 = 成功解决局部问题的重试数量 ÷ 总重试数量 |
| PCM-29 | Nested amplification = actual total attempts / outer declared maximum attempts | 嵌套放大倍数 = 实际总尝试数量 ÷ 外层声明的最大尝试数量 |
| PCM-30 | Pre-check coverage = completed required pre-checks / all required pre-checks | 前置检查覆盖率 = 已完成的必需前置检查数量 ÷ 必需前置检查总数 |
| PCM-31 | Post-verification ratio = real actions with independent outcome verification / all real actions | 后置核验率 = 已进行独立结果核验的真实动作数量 ÷ 真实动作总数 |
| PCM-32 | Technical-success business-failure count = actions with successful tool receipts but failed business acceptance | 接口成功但业务失败数 = 工具返回成功但业务验收失败的动作数量 |
| PCM-33 | Compensation coverage = high-risk actions with explicit compensation paths / all high-risk actions | 可补偿覆盖率 = 具有明确补偿路径的高风险动作数量 ÷ 高风险动作数量 |
| PCM-34 | Approval match = actions exactly matching approved objects, versions and scope / actions requiring approval | 审批匹配率 = 与审批对象、版本和范围完全匹配的动作数量 ÷ 需审批动作数量 |
| PCM-35 | Unauthorized actions = real actions lacking valid approval or authority | 未授权动作数 = 没有有效审批或权限的真实动作数量 |
| PCM-36 | Actual impact ratio = affected object count / approved object-count limit | 实际影响比 = 实际影响对象数量 ÷ 批准对象上限 |
| PCM-37 | Out-of-scope count = affected objects outside approved scope | 范围越界数 = 实际影响但未被批准的对象数量 |
| PCM-38 | Expired approval use = actions using expired approval | 过期审批使用数 = 使用已过期审批的动作数量 |
| PCM-39 | Review coverage = reviewed mandatory objects / all mandatory review objects | 评审覆盖率 = 已被评审的强制对象数量 ÷ 强制评审对象总数 |
| PCM-40 | Issue closure = verified closed issues / all review issues | 问题闭环率 = 已验证关闭的问题数量 ÷ 评审问题总数 |
| PCM-41 | Stale review reuse = old review conclusions used after artifact change | 旧版评审沿用数 = 工件变化后仍使用旧评审结论的次数 |
| PCM-42 | Evidence independence = reviews able to retrieve originals independently / all reviews | 证据独立率 = 能独立回取原始证据的评审数量 ÷ 评审总数 |
| PCM-43 | Handoff completeness = populated mandatory handoff fields / all mandatory fields | 交接完整率 = 已填写的必需交接字段数量 ÷ 必需字段总数 |
| PCM-44 | Handoff receipt ratio = explicitly accepted handoffs / all handoffs | 接收确认率 = 已明确接收的交接数量 ÷ 交接总数 |
| PCM-45 | Wrong-version handoffs = receiver version differs from delivered version | 错误版本交接数 = 接收者使用的版本与交接版本不一致的次数 |
| PCM-46 | Ownerless items = items without an explicit owner after handoff | 责任悬空数 = 交接后没有明确责任人的事项数量 |
| PCM-47 | Mandatory acceptance pass = passed mandatory criteria / all mandatory criteria | 强制验收通过率 = 已通过的强制验收项数量 ÷ 强制验收项总数 |
| PCM-48 | Completion truthfulness = whether completion claim agrees with actual acceptance | 完成声明真实性 = 完成声明与实际验收结果是否一致 |
| PCM-49 | Unresolved high-risk issues = high-risk issues still open at completion | 未解决高风险问题数 = 完成时仍未关闭的高风险问题数量 |
| PCM-50 | Cost per success = total cost / tasks passing acceptance | 单位成功成本 = 总成本 ÷ 通过验收的任务数量 |
| PCM-51 | Rework ratio = tasks entering revision or redo / all tasks | 返工率 = 进入修订或重做的任务数量 ÷ 总任务数量 |
| PCM-52 | Human takeover ratio = tasks requiring human takeover / all tasks | 人工接管率 = 需要人工接管的任务数量 ÷ 总任务数量 |
| PCM-53 | Early takeover benefit = later costs and risks avoided by early stop | 早期接管收益 = 早期停止避免的后续成本和风险 |
| PCM-54 | Component net benefit = quality or risk improvement minus latency, cost and maintenance | 组件净收益 = 组件带来的质量或风险改善减去时延、费用和维护成本 |

## Calculation and Control Constraints / 计算与控制约束

Never infer completion from a high average score, collector health or all workers returning. Count all required branches from the task/plan, including those never started; report both the source started-branch ratio and required-inventory gaps. Reconcile original exceptions before scoring compression. Preserve invalidated evidence and affected claims for re-review. / 不从高均分、采集器健康或执行者全返回推断完成。按任务计划统计所有必需分支，含未启动项，同时报告原式的启动分支回收率和必需清单缺口。压缩评分前核对原例外；保留失效证据及受影响结论供复审。

Deduplicate events before counting actions. Distinguish a retry from waiting, an intent from actual effect, receipt success from business success, and observed state from authority. For costs compare common units; for early takeover/net benefit require a matched counterfactual and uncertainty rather than an invented saved amount. / 动作计数前事件去重；分开重试与等待、意图与效果、回执成功与业务成功、观测状态与权威状态。成本用共同单位；早接管与净收益需要匹配反事实及不确定性，不能编造节省金额。

Thresholds vary by scene, risk and task size. An example of three no-gain iterations is not a universal threshold. Default severity means information → report, warning → authorized notification, high → review/pause request, critical → governance block request. Final control stays at the separately authorized gateway. / 阈值随场景风险规模配置，连续三轮无增益仅为示例而非通用阈值。默认信息报表、警告经授权通知、高风险请求复核暂停、严重请求治理阻断；最终控制由独立授权入口承担。

<a id="placement"></a>
## Topology Placement and Profiles / 拓扑布置与场景组合

| Topology / 拓扑 | Observe before and after / 前后观测位置 |
| --- | --- |
| Chain / 链式 | Output contract, consumed version, evidence propagation and acceptance. / 输出契约、消费版本、证据传递与验收。 |
| Routing / 路由 | Candidates, source facts, chosen path, excluded alternatives and reroute. / 候选、依据事实、所选未选路径及换路。 |
| Parallel / 并行 | Frozen inventory, launch, per-branch terminal, conflicts and aggregate receipt. / 冻结清单、启动、逐分支终态、冲突与聚合回执。 |
| Orchestration / 编排 | Plan changes, dependency readiness, dispatch, wait and resume. / 计划变化、依赖就绪、派发等待与恢复。 |
| Loop / 循环 | Round inputs/changes/evidence, parent/local balances and exit. / 每轮输入差异证据、父局部余额及退出。 |
| Hierarchy / 层级 | Delegated scope, parent requirement coverage, child evidence and ownership return. / 委派范围、父要求覆盖、子证据及责任回收。 |

Recommended starting profiles, extensible for actual requirements / 建议起始组合，按实际要求扩展:

- Research: TASK, TOPOLOGY, EVIDENCE, COMPRESSION, REVIEW, ACCEPTANCE, EFFICIENCY. / 资料研究：任务、拓扑、证据、压缩、评审、验收、效率。
- Troubleshooting: HYPOTHESIS, LOOP, STATE, DEPENDENCY, ACTION, REVIEW, ACCEPTANCE. / 故障排查：假设、循环、状态、依赖、动作、评审、验收。
- Business operation: TASK, DEPENDENCY, ACTION, GOVERNANCE, STATE, HANDOFF, ACCEPTANCE. / 业务办理：任务、依赖、动作、治理、状态、交接、验收。
- Short fixed work: TASK, ACTION when an action exists, necessary GOVERNANCE checks and ACCEPTANCE. Keep observation cost proportional to the task. / 简单固定任务：任务、存在动作时的动作、必要治理检查及验收；观测成本应与任务相称。

## Configuration Example / 配置示例

```yaml
# Explicitly illustrative, requires host adapters / 仅示例，需要宿主适配
profile: pattern_combination/0.1.0
mode: offline
enabled_probes: [PROBE_TASK_001, PROBE_EVIDENCE_001, PROBE_ACCEPTANCE_001]
enrichment:
  enabled: false
  allowed_sources: []
  max_requests_per_run: 0
  unavailable_policy: unknown
control:
  default: report_only
  governance_entry: null
privacy:
  redact_secrets: true
  collect_private_reasoning: false
```

<a id="report"></a>
## Report, Storage and Verification / 报告、存储与验证

The report includes run scope/time/mode, completeness/confidence, causal timeline, task/topology view, evidence map, action/authority view, findings/gaps with owners and due dates, and per-gate outcome. Show what was sampled, unavailable, inferred or corrected. Retain old reports when late events change a conclusion; reopen affected findings with a reason. / 报告包含范围时间模式、完整性置信、因果时间线、任务拓扑视图、证据地图、动作权限视图、带责任期限的异常缺口及逐门结果。展示采样、不可得、推断和纠错；迟到事件改变结论时保留旧报告，附原因重开异常。

Record adapter/normalization/correlation failures, dropped events and calculation errors as observation failures. Source sequence, causal ancestry and state version constrain order; clocks and receipt order alone cannot prove a causal violation. Reconstructed state remains a read-only projection. / 将适配规范关联失败、事件丢失及计算错误记录为观测失败；来源序号、因果祖先及状态版本约束顺序，仅时钟接收顺序不能证明因果违规。重建状态始终是只读投影。

The [contract](pattern-combination-contract.md) specifies enrichment, controls, sampling, privacy and acceptance refinements. The [source map](pattern-combination-source-map.json) retains all 12 probe cases and 8 execution cases with original expected outcomes. They require a host implementation before business validation; current repository validation checks source/formula integrity and discoverability only. / 共享契约定义补全控制采样隐私及验收细化；来源映射保留全部探针与执行用例的原预期，需要宿主实现后才能业务验证，当前仓库校验只检查来源公式完整性及可发现性。

## Source Acceptance Cases / 来源验收用例

Status / 状态: `not_executed`. These are source scenarios, not passed runtime tests. / 以下为来源场景，不是已通过的运行测试。

| ID | Source case / 来源用例 | Input and expected result / 输入与预期 |
| --- | --- | --- |
| PCQ-01 | 用例一：缺失分支 | Two of three branches complete before aggregation → topology identifies missing recovery and task probe requests completion review. / 三个调查分支只完成两个，聚合器准备生成最终报告。 预期：拓扑探针发现分支回收率不足；任务探针阻止完成声明或要求明确缺失原因。 |
| PCQ-02 | 用例二：摘要遗漏例外 | Exception absent from summary/report → compression identifies difference, evidence links original, review issue reopens. / 原文包含例外条款，摘要和报告均未保留。 预期：压缩探针发现关键差异；证据探针给出原文引用；评审探针重新打开相关问题。 |
| PCQ-03 | 用例三：非法跨步 | Import starts before backup completes → dependency reports skipped step, action requests pause, governance decides blocking. / 备份节点未完成，导入节点已经启动。 预期：依赖探针报告跨步；动作探针要求暂停；治理入口决定是否阻断。 |
| PCQ-04 | 用例四：假设未转向 | Logs refute timeout but retries keep changing timeout → hypothesis flags ignored evidence and loop flags low gain. / 日志否定超时原因，但后续仍连续修改超时参数。 预期：假设探针标记否定证据未生效；循环探针识别低信息增益重试。 |
| PCQ-05 | 用例五：嵌套循环失控 | Three outer rounds nest five inner repairs → loop evaluates actual shared task balance and requests blocking at hard limit. / 外层三轮，内层五轮，总尝试数不断增长。 预期：循环探针按任务级预算计算真实剩余额度，并在达到硬上限时发出阻断请求。 |
| PCQ-06 | 用例六：审批失配 | Approval binds v3 but execution uses v4 → governance identifies mismatch and requests reapproval. / 审批绑定配置第三版，执行使用第四版。 预期：治理探针发现版本不匹配，要求重新审批。 |
| PCQ-07 | 用例七：范围越界 | One department approved, two written → governance lists unauthorized objects; action requests impact query/compensation. / 批准一个部门，实际写入两个部门。 预期：治理探针列出越界对象；动作探针请求查询实际影响并准备补偿。 |
| PCQ-08 | 用例八：技术成功、业务失败 | Interface succeeds while query shows old configuration → action reports business failure; acceptance reports premature completion. / 接口返回成功，但目标系统查询仍显示旧配置。 预期：动作探针报告业务核验失败；验收探针拒绝完成。 |
| PCQ-09 | 用例九：错误版本交接 | Receiver uses older artifact → handoff identifies mismatch and affected downstream conclusions. / 接收者使用旧版工件继续核对。 预期：交接探针发现版本不一致并标记后续结论受影响。 |
| PCQ-10 | 用例十：无标准事件的旧系统 | Legacy system has only text logs → adapter uses labeled temporary IDs with low/medium confidence; report limits on automatic controls. / 系统只提供文本日志。 预期：适配器生成临时标识，所有关联标注低或中置信；报告说明无法自动阻断的限制。 |
| PCQ-11 | 用例十一：数据不可获得 | Original was deleted when requested → return unavailable, invent no citation and keep related claim unverified. / 探针请求原文位置，但原始材料已删除。 预期：补全响应为“不可获得”，不生成虚假引用；相关结论保持未验证状态。 |
| PCQ-12 | 用例十二：评审层不值得保留 | Review delays low-risk tasks without improving errors → efficiency recommends risk-based or sampled review or removing the layer. / 大量低风险任务增加评审后时延显著上升，但错误率没有改善。 预期：成本探针建议改为按风险启用、抽样评审或撤销该层。 |
