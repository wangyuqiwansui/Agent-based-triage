# Pattern Selection Observability Probes / 模式选型工作流可观测性探针

Name / 名称: Pattern Selection Probe Profile / 模式选型探针配置。Version / 版本: `0.1.0`. Status / 状态: `draft`, `specification_only`.

Description / 描述: Observe evidence, decisions, topology, authorization, effects and public outcomes for pattern composition without taking over business decisions. / 观察模式组合的证据、决定、拓扑、授权、效果与公开结果，不接管业务决定。

## Quick Navigation / 快速导航

- [Modes and lifecycle / 模式与生命周期](#modes)
- [Probe catalog / 探针目录](#probes)
- [Metric semantics / 指标口径](#semantics)
- [Metric catalog / 指标目录](#metrics)
- [Anomalies / 异常目录](#anomalies)
- [Events / 事件目录](#events)
- [Acceptance cases / 验收用例](#cases)
- [Execution / 执行流程](pattern-selection-execution-flow.md), [Shared contract / 共享契约](pattern-selection-contract.md), [Source map / 来源映射](pattern-selection-source-map.json), [Existing probe suite / 既有探针套件](workflow-observability-probes.md)

## Usage and Constraints / 适用场景与约束

For a composed workflow, also use [composition probes](pattern-combination-observability-probes.md) to inspect connection boundaries and parent acceptance. Selection metrics compare the chosen architecture against its baseline; composition probes inspect its execution. Keep their profile versions and metric identities distinct while linking the same workflow run through an explicit adapter. / 对组合工作流，同时使用组合探针检查连接边界与父级验收。选型指标比较架构与基线，组合探针检查实际执行；通过显式适配关联同次运行，同时保持配置版本与指标身份独立。

Use with selection or adapt existing workflows independently. `PRB-*`, `MTR-*`, `ANO-*` belong to profile `pattern-selection/0.1.0`, a source-backed specification attached to `PATTERN_0052`; none of these new calculations or collectors is implemented here. Existing runtime metric families remain separate. / 可与选型交互，也可独立适配已有工作流。本页编号属于模式选型专用配置，是挂载既有探针的有来源规格；此处未实现这些新指标计算或采集器，既有运行指标族保持独立。

Observe task → fact/source → decision → route/approval/plan → tool/effect → actual business state → public claim. Record concise, inspectable reasons and references, never private chain-of-thought. Unknown telemetry is not proof of non-occurrence. / 观察任务、事实来源、决定、路由审批计划、工具效果、实际业务状态到公开表述的链路。记录简要可检查依据与引用，不采集私密思维过程；遥测未知不证明事件未发生。

<a id="modes"></a>
## Modes and Lifecycle / 模式与生命周期

| Mode / 模式 | Behavior / 行为 |
| --- | --- |
| Standalone sidecar / 独立旁路 | Map available events, retain unmapped records and report partial coverage; advisory only. / 映射已有事件，保留未分类记录并报告部分覆盖，仅作建议。 |
| Interactive enrichment / 交互补全 | Consume stage context, emit supplements and signals at namespaced checkpoints; workflow owns gate enforcement. / 接收阶段上下文，在带命名空间的门返回补丁及信号，流程负责执行门控。 |
| Offline replay / 离线复盘 | Rebuild versioned analysis from historical observations; never alter historical business state. / 从历史观察重建版本化分析，不改变当时业务状态。 |

Lifecycle / 生命周期: `P0` register / 注册 → `P1` receive context / 接收上下文 → `P2` map stages / 映射阶段 → `P3` collect public events / 采集公开事件 → `P4` link causes and versions / 关联因果版本 → `P5` check completeness/consistency / 检查完整一致性 → `P6` compute supported metrics / 计算有依据指标 → `P7` detect anomalies / 检测异常 → `P8` propose supplements / 提出补丁 → `P9` return configured gate signals / 返回预配门信号 → `P10` summarize/archive / 摘要归档. Sidecar/replay do not enforce P9. / 旁路与复盘不执行 P9 门控。

Outputs / 输出: run trace, evidence ledger, decision ledger, action/effect ledger, plan history, metric snapshots, anomaly report and append-only supplements. / 运行轨迹、证据账本、决策账本、动作效果账本、计划历史、指标快照、异常报告及追加补丁。

<a id="probes"></a>
## Probe Catalog / 探针目录

Each row defines trigger, evidence and gap checks, and the selection fields it can supplement. / 每行定义触发点、证据和缺口检查，以及可补全的选型字段。

| ID | Probe / 探针 | Trigger and checks / 触发与检查 | Supplement target / 补全目标 |
| --- | --- | --- | --- |
| PRB-00 | Run context / 运行上下文探针 | Run start: unique IDs, versions, object, owner and risk. / 运行开始：唯一身份、版本、对象、责任及风险。 | S0 |
| PRB-01 | Task contract / 任务契约探针 | Contract recorded: completion, safe exits, prohibited effects, verification source. / 契约记录：完成、安全出口、禁止效果及核验源。 | S1 |
| PRB-02 | Baseline / 基线探针 | Baseline start/end: actual cases, errors, cost, latency and comparable candidate set. / 基线起止：实际案例、错误、成本、时延与候选可比任务集。 | S2, S8 |
| PRB-03 | Facts and sources / 事实与来源探针 | Fact/evidence events: source, state, object/version, expiry, conflicts and dependent decisions. / 事实证据事件：来源、状态、对象版本、过期、冲突及依赖决定。 | S1, S3, S4 |
| PRB-04 | Model necessity / 模型调用必要性探针 | Model requested/responded/skipped: purpose, material version, alternatives, output type, validation, cost. / 模型请求响应跳过：目的、材料版本、替代方案、输出类型、验证及成本。 | S4, S8 |
| PRB-05 | Decision and routing / 判断与路由探针 | Decision/route: owner, fact/rule refs, selected/default/unknown exit; distinguish advice and approval. / 决策路由：责任、事实规则、已选默认未知出口，区分建议与批准。 | S3, S5, S6 |
| PRB-06 | Topology execution / 拓扑执行探针 | Step/branch/loop/delegation events: dependencies, boundaries, budgets and merge obligations. / 步骤分支循环委派事件：依赖、边界、预算及汇合义务。 | S5, S7 |
| PRB-07 | Plan and progress / 计划与进度探针 | Plan changes/completion: predecessor, mandatory steps, retained completed effects and recovery. / 计划变更完成：前版、强制步骤、保留已完成效果及恢复。 | S7 |
| PRB-08 | Approval and handoff / 审批与交接探针 | Approval/handoff: exact object/action/version/scope/expiry; recipient, outstanding facts and artifacts. / 审批交接：精确对象动作版本范围有效期、接收者、待核事实与工件。 | S6, S7 |
| PRB-09 | Pre-action guards / 执行前护栏探针 | Guard/limit before dispatch: current authority, facts, approval, limits, durable idempotency and expected effects. / 派发前护栏限额：当前权限、事实、审批、限额、持久幂等及预期效果。 | S6, S7 |
| PRB-10 | Tools and effects / 工具调用与副作用探针 | Tool/effect events: pair calls/returns, object and versions, retries, expected/actual/unplanned effects. / 工具效果事件：配对调用返回、对象版本、重试、预期实际及计划外效果。 | S7, S8 |
| PRB-11 | Post-action verification / 执行后验证探针 | Effect/outcome verification: independent business query, discrepancies, recovery and completed compensation. / 效果结果核验：独立业务查询、差异、恢复及已完成补偿。 | S6, S7 |
| PRB-12 | Grounded response / 回复依据探针 | Draft/ground/send: claim-source binding, current business status and safe-exit explanation. / 草稿有据发送：主张来源绑定、当前业务状态与安全退出说明。 | S1, S7 |
| PRB-13 | Outcome and safe completion / 结果与安全完成探针 | Run close/outcome: actual outcome, forbidden effects, correct safe exits, verified state and accurate reply. / 结束结果：实际结果、禁止效果、正确安全出口、核验状态及准确回复。 | S8, S9 |
| PRB-14 | Retry, loop and recovery / 重试、循环与恢复探针 | Retry/loop/resume: reason, new evidence, budgets, recovery version and previously completed effects. / 重试循环恢复：原因、新证据、预算、恢复版本及已完成效果。 | S6, S7 |
| PRB-15 | Change and re-selection / 变更与重新选型探针 | Material input/authority/role/rule/tool/plan/error/budget changes: stale selection and affected scope. / 实质输入权限角色规则工具计划错误预算变化：过期选型及影响范围。 | S10 |

## Deployment Profiles / 部署配置

Always inventory required observations from the task/step manifest before processing received events. Start with run, step, tool and outcome events; add facts, decisions, plans, approvals and claims as required. / 处理已接收事件前，先由任务步骤清单确定必需观察总体。从运行、步骤、工具及结果事件起步，再按需增加事实、决定、计划、审批及主张。

| Scope / 范围 | Required observations / 必需观察 |
| --- | --- |
| Readonly Q&A / 只读问答 | PRB-00/01/03/04/12/13; source/version/freshness and claim grounding. Approval/effect probes may be inapplicable. / 来源版本新鲜度及主张依据；审批效果探针可不适用。 |
| Transaction or permission / 交易或权限 | Add PRB-05/08/09/10/11/14; full critical authority, guard, effect and postcheck records. / 增加路由审批护栏效果后检恢复，关键记录全量。 |
| Investigation / 调查 | Add PRB-06/14; hypothesis versions, new evidence, exclusions, conflicts and stopping. / 增加拓扑恢复，假设版本、新证据、排除、冲突及停止。 |
| Dynamic plan / 动态计划 | Add PRB-06/07/14; dependencies, plan changes, mandatory checks, durable completed effects. / 增加拓扑计划恢复，依赖、计划变更、强制检查和持久已完成效果。 |
| Multiple responsibilities / 多方责任 | Add PRB-06/08; versioned delegation, artifact review, conflicts and parent acceptance. / 增加拓扑交接，版本化委派、工件评审、冲突和父级验收。 |
| Code change/release / 代码修改发布 | Reproduction, code/test versions, scope and test evidence; add action gates and post-release checks when releasing. / 复现、代码测试版本、范围和测试证据；发布时加行动门与发布后核验。 |

For topology, chain observes ordering and versions; routing observes conditions/defaults/unknowns; parallel observes required branches/shared resources/joins; orchestration observes dependencies and plan revisions; loops observe new information/budgets/stops; hierarchy observes responsibility/artifacts/parent acceptance. / 拓扑方面，链式观察顺序版本；路由观察条件默认未知；并行观察必选分支共享资源汇合；编排观察依赖计划版本；循环观察新信息预算停止；层级观察责任工件父验收。

Do not sample critical approvals, permissions, guards, irreversible effects, tool/postcheck failures, compensation, severe anomalies, plan changes, handoffs or final states. Low-risk repeated queries/debug details may be sampled with declared rates. Monitor ingestion, link precision/recall, duplicate/conflicting IDs, alert accuracy, patch conflict rate, lag, cost, access and retention. / 不采样关键审批权限护栏、不可逆效果、工具后检失败、补偿、严重异常、计划变更、交接及终态。低风险重复查询调试可按声明比例采样。监控摄取、关联准确与召回、重复冲突 ID、告警准确性、补丁冲突、延迟、成本、访问和保留。

<a id="semantics"></a>
## Metric Semantics / 指标口径

Every snapshot identifies profile/version, metric ID, task/config/evaluation-set versions, window, unit, numerator, denominator, population source, evidence, sample size, coverage and computability. Allowed states are `computed`, `insufficient_data`, `needs_ground_truth`, `needs_audit`, `not_applicable`; noncomputed values are null. Empty applicable populations are not automatically 100%; distinguish a confirmed inapplicable population from unknown inventory. / 每个快照记录配置版本、指标 ID、任务配置评估集版本、窗口、单位、分子分母、总体来源、证据、样本量、覆盖和可计算状态。允许已计算、数据不足、需真值、需审计、不适用；非已计算值为空。适用总体为空不自动填满分，确认不适用与清单未知须区分。

Source formulas and type labels below are preserved for provenance; these maintained qualifications apply before claiming computation: / 下方保留来源公式与类型，宣称可计算前须应用这些维护限定：

- Denominators come from independent task/step/tool manifests where possible, not only successful received events. Event-type coverage MTR-002 must be paired with per-required-event-instance coverage; one observed approval cannot cover ten required approvals. / 尽可能从独立任务步骤工具清单确定分母，不只统计已接收成功事件。事件类型覆盖须配逐个必要实例覆盖，一条审批不能覆盖十项应审批动作。
- MTR-105/106 detect unsupported upgrades, excluding separately evidenced legitimate verification; preserve the original declared/inferred revision. / 误升级指标排除有独立证据的合法核验，但仍保留原声明推断版本。
- MTR-209/303/413/414 require authoritative expected routes/outcomes to claim safe or correct behavior. A source label of “direct” does not manufacture business truth. / 降级、安全路由、恢复、补偿是否正确需要权威预期路由结果，来源标注“直接”不能产生业务真值。
- MTR-203 is an unchanged-material indicator, not proof of redundancy; MTR-201/202 need comparison/audit and a purpose-bound necessity rubric. / 无新材料指标不证明冗余，必要或冗余需对照审计及目的绑定的判据。
- MTR-501 checks each case's expected outcome; MTR-502 includes correct execution, acceptance, refusal, waiting and degradation with no forbidden effects. Report unknown/unlabeled cases separately; never count arbitrary refusal as success. / 正确完成按逐例预期判断；安全完成包含无禁止效果的正确执行受理拒绝等待降级，单报未知未标注案例，不把任意拒绝算成功。
- MTR-408 is conditional on verified actions and must accompany MTR-407 plus unknown/unverified action counts. Zero observed forbidden effects is not proof of zero actual effects under incomplete coverage. / 副作用一致率以已核验动作为条件，须同时给后检覆盖及未知未核验数；覆盖不完整时观测为零不证明实际为零。
- MTR-507 has no numeric formula in the source: use a declared audit rubric and report its sample. MTR-602 separates time to human acceptance from time to resolution; expose still-open/censored waits. / 用户疑问命中率原文无数值公式，须声明审计量表和样本。人工等待分别记录接受耗时及解决耗时，披露尚未结束的等待。
- Audit samples are not population truth. Compare cohorts by risk, task, versions and data completeness; never mix event retries into independent run counts. Hashes and field presence alone do not prove semantic validity. / 审计样本不等于总体真值。按风险任务版本和完整性分组比较，不把重试事件算独立运行；摘要及字段存在不证明语义正确。

<a id="metrics"></a>
## Metric Catalog / 指标目录

Source definitions retain their exact Chinese formulas; the English column summarizes their meaning. All definitions are specification-only. / 保留来源中文公式原文，英文列说明其含义；全部定义仅为规格。

| ID | Metric / 指标 | Source formula / 来源公式 | Source type / 来源类型 | Source meaning / 来源解释 | English definition / 英文释义 |
| --- | --- | --- | --- | --- | --- |
| MTR-001 | 任务契约完整率 | 已填写必填契约项 ÷ 必填契约项总数 | 直接 | 是否明确目标、完成、安全出口和禁止动作 | Contract completeness: completed required fields / required fields. |
| MTR-002 | 关键事件覆盖率 | 已采集关键事件类型 ÷ 应采集关键事件类型 | 直接 | 运行链是否有明显断点 | Event-type coverage: collected critical types / expected critical types. |
| MTR-003 | 证据覆盖率 | 有来源的关键事实数 ÷ 关键事实总数 | 直接 | 判断是否建立在可追溯材料上 | Evidence coverage: sourced critical facts / critical facts. |
| MTR-004 | 权威来源覆盖率 | 权威来源支持的关键事实数 ÷ 关键事实总数 | 直接 | 高风险判断的数据可靠度 | Authority coverage: authority-backed critical facts / critical facts. |
| MTR-005 | 决策依据完整率 | 同时具备事实、规则、主体和版本的关键决定数 ÷ 关键决定总数 | 直接 | 决策能否复盘 | Decision basis: decisions with facts, rules, owner and version / critical decisions. |
| MTR-006 | 工具调用配对率 | 同时有调用和返回事件的工具调用数 ÷ 工具调用总数 | 直接 | 是否存在孤立调用 | Call pairing: calls with request and response / all calls. |
| MTR-007 | 前后状态关联率 | 同时记录动作前状态与动作后状态的风险动作数 ÷ 风险动作总数 | 直接 | 是否能判断副作用 | State linkage: risky actions with pre/post states / risky actions. |
| MTR-008 | 回复事实可追溯率 | 可关联到事实来源的关键回复断言数 ÷ 关键断言总数 | 审计 | 回复是否有据可查 | Claim traceability: sourced key claims / audited key claims. |
| MTR-009 | 交接契约完整率 | 同时有状态、责任、证据、待办和版本的交接数 ÷ 交接总数 | 直接 | 下一棒能否接住正确状态 | Handoff completeness: handoffs with state, owner, evidence, todo and version / handoffs. |
| MTR-010 | 计划版本完整率 | 可关联前版、变更原因和步骤状态的计划变更数 ÷ 计划变更总数 | 直接 | 动态计划是否可恢复 | Plan history completeness: changes linked to predecessor, reason and step state / changes. |
| MTR-101 | 事实状态标注率 | 已标注状态的关键事实数 ÷ 关键事实总数 | 直接 | 是否区分验证、声明、推断和未知 | Fact-state labeling: labeled critical facts / critical facts. |
| MTR-102 | 未知事实显式率 | 被显式标为未知的关键未知数 ÷ 审计发现的关键未知总数 | 审计 | 系统是否隐藏未知 | Explicit unknowns: explicitly unknown critical facts / audited unknown critical facts. |
| MTR-103 | 冲突暴露率 | 已产生冲突事件的事实冲突数 ÷ 审计发现的冲突总数 | 审计 | 数据矛盾是否被发现 | Conflict exposure: signaled conflicts / audited conflicts. |
| MTR-104 | 过期事实使用数 | 被后续决定或动作引用的过期事实数量 | 直接 | 越低越好 | Stale-fact use: expired facts referenced by decisions or actions. |
| MTR-105 | 用户声明误升级数 | 用户声明被标记为已验证的次数 | 直接 | 应为零 | Declaration mis-upgrades: declarations treated as verified without separate verification. |
| MTR-106 | 模型推断误升级数 | 模型推断被标记为权威事实的次数 | 直接 | 应为零 | Inference mis-upgrades: inferences treated as authoritative without verification. |
| MTR-107 | 对象一致率 | 事实、审批、动作和结果指向同一对象的运行数 ÷ 可检查运行数 | 直接 | 防止错单、错人、错版本 | Object consistency: runs whose facts, approval, action and result share the object / checkable runs. |
| MTR-108 | 数据新鲜度合格率 | 在有效期内的关键事实数 ÷ 需要新鲜度检查的事实数 | 直接 | 规则和状态是否仍有效 | Freshness: valid critical facts / facts requiring freshness checks. |
| MTR-201 | 模型必要调用率 | 有明确判断需求且无更简单可靠替代的模型调用数 ÷ 模型调用总数 | 对照 | 越高说明模型边界越清晰 | Model necessity: justified calls lacking a simpler reliable alternative / model calls. |
| MTR-202 | 冗余模型调用率 | 未获得新材料、未改变可验证结论且无必要输出价值的调用数 ÷ 模型调用总数 | 审计 | 越低越好 | Redundancy: calls with no new material, verified conclusion change or necessary output value / calls. |
| MTR-203 | 无新材料复审率 | 输入材料版本未变化的重复评审调用数 ÷ 评审调用总数 | 直接 | 识别“多一次模型等于多一份事实”的误区 | Unchanged review input: repeated reviews on unchanged material versions / reviews. |
| MTR-204 | 模型输出验证率 | 在使用前经过程序、规则、工具或人工验证的关键模型输出数 ÷ 关键模型输出总数 | 直接 | 高风险输出应接近百分之百 | Output validation: critical model outputs validated before use / critical model outputs. |
| MTR-205 | 模型越权建议数 | 建议中包含超出授权范围动作的次数 | 审计 | 应被后续控制拦截 | Out-of-scope proposals: proposed actions outside current authority. |
| MTR-206 | 模型事实幻写数 | 输出中出现材料和权威来源均不支持的事实数 | 审计 | 越低越好 | Unsupported model facts: output facts unsupported by material and authoritative sources. |
| MTR-207 | 单任务模型调用数 | 模型调用总数 ÷ 工作流运行数 | 直接 | 用于版本和场景比较 | Calls per task: model calls / workflow runs. |
| MTR-208 | 单任务模型成本 | 模型成本总和 ÷ 工作流运行数 | 直接 | 与质量改进一起评估 | Model cost per task: total model cost / workflow runs. |
| MTR-209 | 模型降级成功率 | 模型不可用时安全完成的运行数 ÷ 触发降级的运行数 | 直接 | 衡量系统韧性 | Safe degradation: safely completed fallback runs / fallback runs; requires outcome truth. |
| MTR-301 | 固定链跳步数 | 未满足依赖却开始后续步骤的次数 | 直接 | 应为零 | Skipped dependencies: later steps started before dependencies were met. |
| MTR-302 | 路由可解释率 | 有条件、事实和规则引用的路由数 ÷ 路由总数 | 直接 | 路由是否可复盘 | Route explainability: routes with conditions, facts and rules / routes. |
| MTR-303 | 未知事实安全路由率 | 关键事实未知时进入安全出口的运行数 ÷ 关键事实未知运行数 | 直接 | 应较高 | Unknown-safe routing: runs with critical unknowns taking the expected safe exit / critical-unknown runs. |
| MTR-304 | 并行有效率 | 实际可并行且无隐藏依赖的并行分支数 ÷ 并行分支总数 | 对照 | 判断并行是否合理 | Effective parallelism: independent branches without hidden dependencies / parallel branches. |
| MTR-305 | 隐藏依赖异常数 | 并行运行后发现前后依赖或共享冲突的次数 | 直接 | 越低越好 | Hidden dependencies: detected ordering or shared-state conflicts in parallel execution. |
| MTR-306 | 计划依赖违规数 | 依赖未完成却执行步骤的次数 | 直接 | 应为零 | Plan dependency violations: steps executed before dependencies completed. |
| MTR-307 | 已完成状态保留率 | 计划变更后仍正确保留的已完成步骤数 ÷ 变更前已完成步骤数 | 直接 | 应为百分之百 | Completed-state preservation: retained completed steps / previously completed steps. |
| MTR-308 | 无效重规划率 | 未发生新事实或约束变化却重写计划的次数 ÷ 重规划总数 | 审计 | 越低越好 | Invalid replanning: plan changes without changed facts or constraints / plan changes. |
| MTR-309 | 循环预算遵守率 | 未超次数、时间和成本预算的循环数 ÷ 循环总数 | 直接 | 防止无限探索 | Loop budget compliance: loops within iteration, time and cost caps / loops. |
| MTR-310 | 无新信息循环率 | 迭代未引入新事实、检测或结论变化的次数 ÷ 总迭代数 | 直接 | 越低越好 | No-information iterations: iterations without new facts, tests or changed conclusions / iterations. |
| MTR-311 | 委派契约完整率 | 输入、输出、责任和验收齐全的委派数 ÷ 委派总数 | 直接 | 层级结构的基本质量 | Delegation completeness: delegations with input, output, owner and acceptance / delegations. |
| MTR-312 | 聚合冲突处置率 | 被显式处理的子结果冲突数 ÷ 发现的冲突总数 | 直接 | 聚合不应直接覆盖异议 | Merge conflict handling: explicitly handled conflicts / detected child-result conflicts. |
| MTR-401 | 前置检查覆盖率 | 已完成全部必需前置检查的风险动作数 ÷ 风险动作总数 | 直接 | 风险动作的基本门槛 | Precheck coverage: risky actions with all required prechecks / risky actions. |
| MTR-402 | 权限检查覆盖率 | 有当前身份权限校验的风险动作数 ÷ 风险动作总数 | 直接 | 防止越权 | Permission coverage: risky actions with current identity authorization checks / risky actions. |
| MTR-403 | 审批绑定完整率 | 审批对象、动作、版本、范围和有效期齐全的审批数 ÷ 审批总数 | 直接 | 防止一次点头无限扩张 | Approval binding: approvals with object, action, version, scope and expiry / approvals. |
| MTR-404 | 过期审批使用数 | 动作使用已过期批准的次数 | 直接 | 应为零 | Expired approval use: actions relying on expired approvals. |
| MTR-405 | 幂等保护覆盖率 | 具备幂等键或等价保护的可重试副作用动作数 ÷ 可重试副作用动作总数 | 直接 | 防止重复执行 | Idempotency coverage: protected retryable effects / retryable effects. |
| MTR-406 | 范围限制覆盖率 | 有对象、金额、次数、时间或地域限制的高风险动作数 ÷ 高风险动作总数 | 直接 | 控制最大损失 | Scope limits: high-risk actions with explicit limits / high-risk actions. |
| MTR-407 | 后置验证覆盖率 | 执行后查询实际业务状态的风险动作数 ÷ 风险动作总数 | 直接 | 防止只信工具返回 | Postcheck coverage: risky actions with actual-state verification / risky actions. |
| MTR-408 | 业务副作用一致率 | 实际副作用与预期一致的动作数 ÷ 已验证动作数 | 直接 | 检查执行是否真正正确 | Effect consistency: actions matching expected effects / verified actions. |
| MTR-409 | 重复副作用数 | 同一幂等语义下重复产生副作用的次数 | 直接 | 应为零 | Duplicate effects: repeated effects under the same semantic idempotency scope. |
| MTR-410 | 计划外副作用数 | 未在计划或授权范围内的副作用次数 | 直接 | 应为零 | Unplanned effects: effects outside plan or authorized scope. |
| MTR-411 | 高风险误执行数 | 条件、权限或事实不满足仍执行的次数 | 对照 | 核心安全指标 | High-risk misexecution: actions performed with unmet conditions, authority or facts. |
| MTR-412 | 禁止副作用发生数 | 命中任务契约禁止动作的次数 | 直接 | 应为零 | Forbidden effects: effects prohibited by the task contract. |
| MTR-413 | 恢复成功率 | 中断后从正确恢复点完成或安全退出的运行数 ÷ 触发恢复的运行数 | 直接 | 衡量韧性 | Recovery success: correct completion or safe exit from the right checkpoint / recovery runs. |
| MTR-414 | 补偿闭环率 | 补偿动作完成且业务状态验证正确的次数 ÷ 启动补偿的次数 | 直接 | 回滚不应只记录开始 | Compensation closure: completed and state-verified compensation / started compensation. |
| MTR-501 | 正确完成率 | 符合预期结果类型的运行数 ÷ 有真值运行数 | 对照 | 包括执行和正确安全退出 | Correct completion: runs matching expected outcome type / truth-labeled runs. |
| MTR-502 | 安全完成率 | 正确执行、受理、拒绝、等待和降级的运行数 ÷ 有真值运行数 | 对照 | 比单纯办成率更完整 | Safe completion: correct execution, acceptance, refusal, waiting or degradation / truth-labeled runs. |
| MTR-503 | 结果验证率 | 最终业务状态经过权威查询或责任人确认的运行数 ÷ 完成运行数 | 直接 | 防止状态误报 | Outcome verification: completed runs with authoritative query or responsible confirmation / completed runs. |
| MTR-504 | 状态表述一致率 | 对用户表述与实际业务状态一致的运行数 ÷ 已发送回复运行数 | 审计 | 防止把批准说成到账 | Message-state consistency: accurate business-state replies / sent replies, under audit. |
| MTR-505 | 安全退出说明完整率 | 说明原因、待办和下一责任方的安全退出回复数 ÷ 安全退出运行数 | 审计 | 人工路由必须可执行 | Safe-exit explanation: replies with reason, next work and next owner / safe-exit runs, under audit. |
| MTR-506 | 无依据断言数 | 回复中缺少证据支持的关键断言数 | 审计 | 越低越好 | Unsupported assertions: key reply claims without evidence. |
| MTR-507 | 用户疑问命中率 | 回复是否针对用户实际疑问，而非只报告流程状态 | 审计 | 适合解释型回复 | Question relevance: audited fit to the actual question; a rubric is required, not supplied numerically. |
| MTR-601 | 端到端时延 | 运行结束时间减开始时间 | 直接 | 应同时看平均值和高分位 | End-to-end latency: end time minus start time; report mean and tails. |
| MTR-602 | 人工等待时长 | 进入人工路由到被接受或完成的时间 | 直接 | 发现责任悬空 | Human wait: human-route entry to acceptance or resolution; report these separately. |
| MTR-603 | 单任务总成本 | 模型、工具、人工和外部服务成本之和 | 直接 | 与质量和风险一起比较 | Total task cost: model, tool, human and external service cost. |
| MTR-604 | 不必要工具调用率 | 对结果无贡献且可被缓存或省略的调用数 ÷ 工具调用总数 | 审计 | 优化成本和时延 | Unnecessary tools: omit-able or cacheable calls without outcome contribution / calls, under audit. |
| MTR-605 | 缓存命中有效率 | 命中缓存且数据仍新鲜的次数 ÷ 缓存命中次数 | 直接 | 不能以过期换速度 | Valid cache hits: fresh cache hits / cache hits. |
| MTR-606 | 重新选型触发及时率 | 实质变化后在阈值内触发重选型的次数 ÷ 实质变化次数 | 对照 | 防止结构过期 | Timely reselection: material changes triggering reselection within threshold / material changes. |
| MTR-607 | 版本漂移运行数 | 任务、规则、提示、计划或工具版本无法对应的运行数 | 直接 | 越低越好 | Version drift: runs with unresolvable task, rule, prompt, plan or tool versions. |
| MTR-608 | 过期选型继续运行时长 | 应重选型时刻到实际停用或重选型的时间 | 对照 | 衡量演化响应速度 | Stale-selection exposure: time from required reselection to withdrawal or reselection. |

<a id="anomalies"></a>
## Anomaly Catalog / 异常目录

Source severities and suggested responses below are observations for the host policy. A probe cannot revoke approval, edit a business record, delete data or compensate an effect itself. Missing telemetry raises a gap; a proven violation requires bound evidence. / 下方来源级别与建议供宿主策略使用。探针不能自行撤销审批、修改业务、删除数据或补偿效果。缺遥测报告缺口，有据违规须绑定证据。

| ID | Anomaly / 异常 | Source trigger / 来源触发条件 | Severity / 级别 | Source response / 来源建议 | English interpretation / 英文解释 |
| --- | --- | --- | --- | --- | --- |
| ANO-001 | 对象不一致 | 任务、事实、审批、动作或结果对象不同 | 严重 | 阻塞动作并人工复核 | Object mismatch: block the affected action and review. |
| ANO-002 | 未知事实驱动高风险动作 | 关键事实为未知仍进入执行 | 严重 | 阻塞并进入安全出口 | Unknown critical fact used for risky action: take a safe exit. |
| ANO-003 | 冲突事实未处置 | 冲突存在但继续执行 | 严重 | 暂停并仲裁数据 | Unresolved fact conflict: pause and arbitrate. |
| ANO-004 | 过期事实被使用 | 关键事实超有效期仍支持判断 | 高 | 重新查询或审批 | Expired fact use: refresh evidence or applicable approval. |
| ANO-005 | 模型推断误作事实 | 推断被标记为已验证 | 严重 | 撤销升级并复核下游动作 | Inference presented as verified: append a correction and revalidate downstream decisions. |
| ANO-006 | 缺事实却重复模型评审 | 输入材料未变且问题本质为事实缺失 | 中 | 停止复审，转数据或人工核实 | Missing facts repeatedly reviewed by a model: obtain data or responsible verification. |
| ANO-007 | 模型无新材料重复调用 | 相同输入版本重复调用且无明确价值 | 提醒 | 优化调用或缓存 | Unchanged-input call without clear value: investigate redundancy. |
| ANO-008 | 模型越权闭环 | 模型提出、批准并触发动作 | 严重 | 拆分责任并阻塞动作 | Model proposes, approves and executes: separate responsibility and stop unauthorized effects. |
| ANO-009 | 路由无安全默认出口 | 未知条件无明确出口 | 高 | 增加人工、等待或拒绝路由 | No safe default route: add refusal, waiting or human review. |
| ANO-010 | 计划依赖违规 | 前置步骤未完成却执行后续步骤 | 严重 | 暂停、回滚或补偿 | Unmet plan dependency: pause and evaluate authorized recovery. |
| ANO-011 | 已完成状态丢失 | 计划变更后完成步骤被重置 | 高 | 恢复历史状态并复核重复执行 | Completed state lost after replanning: reconstruct history and check duplicates. |
| ANO-012 | 循环无停止条件 | 循环缺少次数、时间或预算上限 | 高 | 设置上限或暂停 | Unbounded loop: impose declared limits or suspend. |
| ANO-013 | 并行隐藏依赖 | 并行分支共享状态或存在先后依赖 | 高 | 串行化或增加同步点 | Hidden parallel dependency: serialize or synchronize the dependent work. |
| ANO-014 | 委派无验收契约 | 子任务无明确输出或接收人 | 中 | 补充交接契约 | Delegation lacks acceptance: complete ownership and artifact contract. |
| ANO-015 | 审批范围不匹配 | 批准对象、版本、金额或动作与执行不一致 | 严重 | 阻塞并重新审批 | Approval scope mismatch: stop and return to authority workflow. |
| ANO-016 | 过期审批被使用 | 批准已过有效期 | 严重 | 阻塞并重新审批 | Expired approval: stop and refresh through authority workflow. |
| ANO-017 | 缺少前置检查 | 风险动作前未完成必要检查 | 严重 | 阻塞动作 | Missing required precheck: block the dependent action. |
| ANO-018 | 缺少幂等保护 | 可重试副作用动作无幂等控制 | 高 | 禁止自动重试 | Missing durable idempotency: disallow automatic retry of the effect. |
| ANO-019 | 工具成功但业务状态不一致 | 接口成功，后置状态未变化或错误 | 严重 | 暂停后续步骤并恢复 | Tool success but business mismatch: pause dependent steps and reconcile. |
| ANO-020 | 重复副作用 | 同一语义动作被重复执行 | 严重 | 停止重试并补偿 | Duplicate effect: stop retries and request authorized compensation. |
| ANO-021 | 计划外副作用 | 实际副作用不在授权或计划范围 | 严重 | 隔离、回滚、升级处理 | Unplanned effect: contain and escalate through authorized controls. |
| ANO-022 | 人工路由不可执行 | 没写明待核实事项、责任人或证据 | 中 | 补全交接单 | Unusable human handoff: specify outstanding facts, owner and evidence. |
| ANO-023 | 回复状态夸大 | 受理、批准或提交被写成最终完成 | 高 | 更正回复并复核影响 | Reply overstates state: correct through the authorized communication workflow. |
| ANO-024 | 回复无事实依据 | 关键断言无法关联证据 | 高 | 阻止发送或降级模板 | Ungrounded reply claim: withhold or use a grounded fallback. |
| ANO-025 | 探针链路断裂 | 关键调用或步骤无法关联 | 中 | 标记数据不完整，不做过度结论 | Broken event linkage: mark incomplete coverage, avoid unsupported conclusions. |
| ANO-026 | 探针推断被当作权威事实 | 补丁未经确认进入高风险判断 | 严重 | 撤销并复核 | Probe inference treated as authority: correct evidence and review dependent decisions. |
| ANO-027 | 版本漂移 | 任务、规则、工具或提示版本不一致 | 高 | 暂停或重跑验证 | Version drift: pause affected scope or revalidate. |
| ANO-028 | 选型过期 | 能力或风险变化后仍使用旧选型 | 高 | 触发重新选型 | Stale selection: trigger reselection for the changed scope. |
| ANO-029 | 观测到敏感数据过量 | 采集超出最小必要范围 | 高 | 脱敏、删除并调整采集策略 | Excess sensitive collection: request authorized minimization and policy repair. |
| ANO-030 | 保留期违规 | 数据超过保留期仍可访问 | 高 | 归档或删除并审计 | Retention violation: route to authorized retention handling and audit. |

<a id="events"></a>
## Event Catalog / 事件目录

Use the envelope, namespaces and alias rules in the [shared contract](pattern-selection-contract.md). This is the source event vocabulary, not an implemented emitter or runtime allowlist. / 使用共享契约的包络、命名空间和别名规则。以下是来源事件词汇，不是已实现的发射器或运行时允许列表。

```text
selection.run.started
selection.contract.recorded
selection.baseline.started
selection.baseline.completed
selection.difficulty.diagnosed
selection.boundary.decided
selection.topology.selected
selection.patterns.selected
selection.workflow.published
selection.validation.started
selection.validation.completed
selection.decision.published
selection.reselection.triggered
selection.run.completed
workflow.run.started
workflow.phase.started
workflow.step.started
workflow.step.completed
workflow.step.failed
workflow.run.suspended
workflow.run.resumed
workflow.run.completed
workflow.run.failed
workflow.fact.observed
workflow.fact.verified
workflow.fact.declared
workflow.fact.inferred
workflow.fact.marked_unknown
workflow.fact.conflict_detected
workflow.fact.expired
workflow.evidence.attached
workflow.model.requested
workflow.model.responded
workflow.model.output_rejected
workflow.model.output_accepted
workflow.model.call_skipped
workflow.decision.proposed
workflow.decision.evaluated
workflow.decision.approved
workflow.decision.rejected
workflow.route.selected
workflow.route.fallback
workflow.plan.created
workflow.plan.validated
workflow.plan.changed
workflow.plan.rejected
workflow.step.blocked_by_dependency
workflow.loop.iteration_started
workflow.loop.iteration_completed
workflow.loop.stopped
workflow.loop.budget_exceeded
workflow.approval.requested
workflow.approval.granted
workflow.approval.denied
workflow.approval.expired
workflow.guard.checked
workflow.guard.failed
workflow.limit.checked
workflow.limit.exceeded
workflow.tool.called
workflow.tool.returned
workflow.tool.failed
workflow.tool.retried
workflow.side_effect.expected
workflow.side_effect.observed
workflow.side_effect.verified
workflow.side_effect.mismatch
workflow.rollback.started
workflow.rollback.completed
workflow.compensation.created
workflow.delegation.created
workflow.delegation.accepted
workflow.artifact.submitted
workflow.artifact.reviewed
workflow.handoff.created
workflow.handoff.accepted
workflow.handoff.rejected
workflow.aggregation.started
workflow.aggregation.completed
workflow.conflict.escalated
workflow.response.drafted
workflow.response.grounded
workflow.response.sent
workflow.outcome.verified
workflow.outcome.reported
probe.coverage.updated
probe.data_gap.detected
probe.anomaly.detected
probe.metric.snapshot
probe.supplement.proposed
probe.supplement.accepted
probe.supplement.rejected
probe.run.summary
workflow.response.generated
```

<a id="cases"></a>
## Acceptance Cases / 验收用例

All cases are `not_executed`. Exercise missing/duplicate/late events, authoritative truth and adapter failures in the adopting system before making operational claims. / 全部用例未执行；采用系统应覆盖缺失重复迟到事件、权威真值及适配故障后再作运行声明。

| ID | Source case / 来源用例 | Expected behavior / 预期行为 | Status / 状态 |
| --- | --- | --- | --- |
| OBS-CASE-01 | 完整固定链，所有步骤正确关联。 | Complete chain events associate correctly. | not_executed / 未执行 |
| OBS-CASE-02 | 工具调用有开始无返回，触发链路缺口。 | Call without return exposes an unresolved linkage gap. | not_executed / 未执行 |
| OBS-CASE-03 | 发票未知却创建付款指令，触发严重异常。 | Unknown invoice with payment instruction raises a severe violation. | not_executed / 未执行 |
| OBS-CASE-04 | 模型在相同材料上重复评审，触发冗余调用提示。 | Unchanged-material repeated review signals possible redundancy under the necessity rubric. | not_executed / 未执行 |
| OBS-CASE-05 | 第二次模型调用获得新业务事实，不应误报为冗余。 | A second call with new business facts is not mislabeled redundant. | not_executed / 未执行 |
| OBS-CASE-06 | 计划变更保留已完成步骤，指标正确。 | Replanning that preserves completed steps yields correct preservation metrics. | not_executed / 未执行 |
| OBS-CASE-07 | 计划变更丢失已完成状态，触发异常。 | Replanning that loses completed states raises an anomaly. | not_executed / 未执行 |
| OBS-CASE-08 | 重试使用相同幂等键且无重复副作用，判定正常。 | Idempotent retry with verified absence of duplicates remains normal. | not_executed / 未执行 |
| OBS-CASE-09 | 工具返回成功但业务状态未变化，触发后置不一致。 | Technical success with unchanged business state raises postcheck mismatch. | not_executed / 未执行 |
| OBS-CASE-10 | 回复把“已批准”写成“已到账”，触发状态夸大。 | Approval reported as received funds raises state overstatement. | not_executed / 未执行 |
| OBS-CASE-11 | 探针无法关联事件时，标记数据不足，不虚构结论。 | Unlinkable events remain insufficient data without invented conclusions. | not_executed / 未执行 |
| OBS-CASE-12 | 推断补丁未经确认，不得满足高风险前置条件。 | Unconfirmed inferred patches cannot satisfy risky preconditions. | not_executed / 未执行 |
| OBS-CASE-13 | 敏感载荷超量采集，触发隐私异常。 | Excess sensitive collection raises a privacy anomaly. | not_executed / 未执行 |
| OBS-CASE-14 | 规则版本变化后仍使用旧选型，触发重新选型提示。 | Old selection after rule change triggers reselection advice. | not_executed / 未执行 |

Additional boundary requirements / 额外边界要求: identical G2 names must not collide; generated responses must not become sent; inference-only links cannot auto-upgrade; stale-base or duplicate-ID-different-payload supplements cannot be accepted; zero denominators remain explicit; optional probe failure cannot bypass required guards or block unrelated work; missing payment telemetry cannot prove no payment occurred. / 同名 G2 不冲突，生成不变为已发，推断关联不自动升级，陈旧基准或同 ID 异载荷补丁不接受，零分母显式，可选探针故障不绕过必要闸门或阻断无关工作，缺付款遥测不证明未付款。
