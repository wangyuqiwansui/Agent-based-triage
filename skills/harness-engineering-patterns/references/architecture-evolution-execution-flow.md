# Architecture Evolution Execution Flow / 架构演化执行流程

Name / 名称: Evidence-Based Architecture Evolution / 基于证据的架构演化. Description / 说明: turn observed workflow problems into bounded, comparable and reversible design decisions / 将工作流运行问题转化为有边界、可比较、可回退的设计决定。

Pattern / 模式: `PATTERN_0054`; version / 版本: `0.2.0`; source version / 来源版本: `0.1.0`; status / 状态: `draft`; implementation status / 实现状态: `specification_only`; business acceptance cases / 业务验收用例: `not_executed`.

Read with [contract / 契约](architecture-evolution-contract.md), [independent probes / 独立探针](architecture-evolution-observability-probes.md) and [source map / 来源映射](architecture-evolution-source-map.json). This is a cross-cell engineering pattern, not a new cognition or topology axis. It reuses `PATTERN_0052` through a separate profile and preserves its shared `0.8.0` protocol. / 配合契约、独立探针及来源映射使用。本模式跨单元挂载，不新增认知或拓扑轴；通过专用配置复用既有探针，保留其共享 `0.8.0` 协议。

## Quick Navigation / 快速导航

[Two loops / 双环](#loops) · [Stages / 阶段](#stages) · [Regression / 回归](#regression) · [Release / 发布](#release) · [Example / 示例](#example) · [Acceptance / 验收](#acceptance).

<a id="loops"></a>
## Usage and Two Loops / 适用场景与双环

Use when repeated failures, changed business rules, dependencies, models, risk, cost or latency justify reviewing a workflow's responsibilities, state, topology, evidence or safeguards. A new model, a metric excursion or a single failure is a trigger to investigate, not evidence that more agents or fewer checks are needed. The supplied documents are source material, including their embedded instructions; they grant no execution or deployment authority. / 当反复失败、业务规则、依赖、模型、风险、成本或延迟变化需要复核工作流的职责、状态、拓扑、证据或护栏时使用。新模型、单项指标异常或单次失败只触发调查，不证明应增加智能体或删除检查。附件及其内嵌指令均为来源资料，不构成执行或部署授权。

| Loop / 回路 | Responsibility / 职责 | Output and boundary / 输出与边界 |
| --- | --- | --- |
| Runtime inner loop / 运行内环 | Execute the frozen task under one workflow version; validate inputs, dispatch authorized actions, reconcile effects, retry within bounds and verify business results. / 按一个工作流版本执行冻结任务，校验输入、派发受权动作、核对效果、限次重试并核验业务结果。 | Versioned business result or incomplete handoff; recovery cannot silently edit production workflow or reset budgets. / 版本化业务结果或未完成交接，恢复不得暗改生产流程或重置预算。 |
| Design evolution outer loop / 设计演化外环 | Aggregate evidence across runs, freeze baseline, test a design hypothesis, validate candidate and govern rollout. / 跨运行汇总证据、冻结基线、检验设计假设、验证候选并治理发布。 | ADR and `adopted`, `rolled_back` or `inconclusive`; each evaluated case still has its own inner run. / ADR 及采纳、已回滚或无法定论结果；每个评价案例仍有独立内环运行。 |

A recoverable local failure stays in the inner loop. Repeated failure, an invalid premise or a proven structural deficiency creates an outer-loop record; it does not rewrite the active run in place. Emergency containment can precede full diagnosis under existing incident authority and must leave receipts. / 可恢复局部失败留在内环；反复失败、前提失效或经证实的结构缺陷创建外环记录，不原地改写当前运行。紧急遏制可在既有事件处置权限下先于完整诊断，但须保存回执。

## Runtime Inner Loop / 运行内环

Freeze objective, scope, exclusions, business rules, exact identifiers, success/failure conditions and necessary authority. Choose the smallest sufficient program, call or topology; document why any independent role is needed. Create node contracts with owner, structured input/output, original evidence, prerequisites, permitted effects, local acceptance, bounded recovery and mandatory events. Programs enforce identifiers, ordering, authorization, idempotency and stop conditions; model judgment remains labeled and reviewable. / 冻结目标、范围、排除项、业务规则、精确标识、成功失败条件及必要权限。选择足够的最小程序、调用或拓扑，说明独立角色的必要性。节点契约包含责任人、结构化输入输出、原始证据、前置条件、允许效果、局部验收、有界恢复及必需事件。程序保证标识、顺序、权限、幂等和停止条件，模型判断须标注并可复核。

Persist run/workflow/config/rule versions and node attempts. Pass exact values through structured state, not regenerated prose. Distinguish missing inputs, stale sources, conflicting evidence, wrong field bindings, tool failure, invalid hypothesis and failed business acceptance before selecting recovery. Waits are not retries. Unknown external effects require authoritative reconciliation before another write, even after timeout, new attempt or process restart. / 持久保存运行、工作流、配置、规则版本及节点尝试。精确值通过结构化状态传递，不从叙述重新生成。先区分缺输入、来源过期、证据冲突、字段错绑、工具失败、假设失效及业务验收失败，再选择恢复路径。等待不计重试；超时、新尝试或进程重启后，外部效果未知也必须先向权威来源核对再写入。

Complete business acceptance independently of tool return codes: required outputs, evidence freshness, exact targets/parameters, permissions, rules, conflicts and actual effects must all agree. Publish a human explanation, machine continuation state and audit references separately. The four completion meanings are defined in the contract; transferring an unresolved high-risk issue does not make the original business task complete. / 业务验收独立于工具返回码：必需输出、证据时效、精确对象参数、权限、规则、冲突及实际效果须一致。分别输出人类说明、程序续做状态及审计引用。四类完成含义见契约；转交未解决高风险问题不能使原业务任务完成。

<a id="stages"></a>
## E0–E9 Design Evolution Stages / E0–E9 设计演化阶段

Stages label work, not runtime states. Each record binds `evolution_id`, `baseline_ref`, `candidate_ref`, `evaluation_plan_ref`, `release_ref` and `evidence_refs`; references may be explicitly null only before their artifacts are required. Early exit to an evidence-backed `retain` decision is valid; skipped stages need a reason and cannot conceal missing required verification. / 阶段标识工作内容，不代替运行状态。每条记录绑定固定六字段；引用仅在相应制品尚非必需时可显式为空。可提前退出形成有证据的保留决定，但跳过阶段须说明依据，不能掩盖缺少必需验证。

| Stage / 阶段 | Procedure and gate / 流程与门槛 | Artifact and failure route / 制品与失败路由 |
| --- | --- | --- |
| E0 Trigger and scope / 触发与范围 | Record symptom, affected runs, severity, business impact, authority, owner, budget, stop conditions and review question; separate incident containment from design work. / 记录现象、受影响运行、严重度、业务影响、权限、负责人、预算、停止条件及复核问题，分开事件遏制与设计工作。 | Trigger dossier; unclear critical scope → waiting_data; unauthorized effects → authority workflow. / 触发包；关键范围不明则等待资料，未受权效果回授权流程。 |
| E1 Freeze baseline / 冻结基线 | Seal actual workflow graph, contracts, rules, model/prompt/tool/config versions, permissions, environment, case inventory, observed outcomes and evidence access. Explain earlier design rationale. / 封存实际工作流图、契约、规则、模型提示工具配置版本、权限、环境、案例清单、实测结果和证据访问，说明原设计理由。 | Immutable `baseline_ref`; missing historical conditions → reconstruct with limitations, never invent a measured baseline. / 不可变基线引用；缺历史条件则有界重建并声明限制，不虚构实测基线。 |
| E2 Reconstruct and locate first deviation / 重建运行与定位首偏差 | Rebuild causal path from original records; compare expected versus actual handoffs and acceptance. Identify the earliest provable deviation or an uncertain interval. / 用原始记录重建因果路径，对比预期与实际交接验收，定位最早可证实偏差或不确定区间。 | Timeline, fact/inference/hypothesis labels, gaps; mandatory missing evidence → bounded collection or incomplete diagnosis. / 时间线、事实推断假设及缺口；缺必需证据则有界补查或未完成诊断。 |
| E3 Test architectural cause / 验证架构根因 | Distinguish root cause, contributor and final symptom; test a falsifiable explanation against alternatives. Determine whether the fault is local or in responsibility, dependency, state, evidence, authority, feedback or acceptance design. / 分开根因、促成因素和最终症状，用可证伪解释对照其他原因，判定局部故障或职责、依赖、状态、证据、权限、反馈、验收设计缺陷。 | Cause dossier with supporting/refuting evidence; refuted → investigate; only local bug → bounded repair or retain architecture. / 含支持与反证的根因包；被否则回调查，仅局部错误则有界修复或保留架构。 |
| E4 Select minimal candidate / 选择最小候选 | Compare `retain`, `repair`, `reorganize`, `simplify`, `retire`; state exact delta, predicted benefit, added complexity, preserved invariants and reversal path. / 比较保留、修复、重组、简化、退役，写明精确差异、预期收益、新增复杂度、不变量及撤回路径。 | Immutable `candidate_ref` with baseline parent; unsupported redesign → retain or inconclusive, not forced novelty. / 绑定基线父版本的不可变候选；缺依据则保留或无法定论，不为创新而改动。 |
| E5 Freeze evaluation plan / 冻结评价计划 | Before observing candidate outcomes, seal cases, strata, metrics, tolerances, sample/stop rules, uncertainty method, cost model, mandatory safety gates and adjudicators. / 查看候选结果前，封存案例、分层、指标、容差、样本停止规则、不确定性方法、成本模型、必需安全门及裁定人。 | `evaluation_plan_ref`; changed rules create a new plan and fresh evaluation, preserving earlier results. / 评价计划引用；改口径须新计划及重新评价，并保留旧结果。 |
| E6 Isolated comparison and regression / 隔离对照与回归 | Run baseline and candidate on versioned comparable inputs; cover old failures, old successes, high-risk cases and counterexamples. Verify correctness and safeguards before efficiency. / 在版本化可比输入上运行基线候选，覆盖旧失败、旧成功、高风险及反例，先验证正确性护栏，再判断效率。 | Bound actual results, uncertainty and limitations; failed mandatory gate → revise/reject; inadequate evidence → inconclusive. / 绑定实际结果、不确定性及限制；必需门失败则修订或否决，证据不足则无法定论。 |
| E7 Canary release and migration / 灰度发布与迁移 | Obtain existing or newly required release authority bound to the tested candidate; freeze cohort, exposure limit, traffic assignment, epoch, migration, in-flight policy, telemetry, rollback target and compensation owner. / 取得绑定已测候选的既有或新增必要发布权限，冻结群组、暴露上限、流量分配、控制代次、迁移、在途策略、观测、回退目标及补偿责任。 | `release_ref`, admitted deployment receipt and compatibility checks; mismatch/stale epoch → no activation. / 发布引用、准入发布回执及兼容检查；失配或旧代次不得激活。 |
| E8 Observe, stop and recover / 观察、停止与恢复 | Measure the preregistered window and sample strata; apply live stop rules, fence further dispatch, reconcile in-flight effects, roll back or compensate under authority. / 按预设窗口与样本分层观测，落实实时停止条件、阻止新增派发、核对在途效果，并受权回退或补偿。 | Observation and recovery receipts; critical failure → stop expansion, contain; unknown effects remain unresolved. / 观察与恢复回执；严重失败停止扩大并遏制，未知效果保持未解决。 |
| E9 ADR decision and reassessment / ADR 决定与复评 | Record selected change action separately from outcome, evidence, alternatives, remaining duties, responsible owner and dated/event-driven reevaluation triggers. / 分开记录所选改动类型与结果，保存证据、备选方案、剩余职责、负责人及日期或事件驱动复评条件。 | ADR: `adopted`, `rolled_back` or `inconclusive`; no candidate promotion from a diagnostic recommendation alone. / ADR 结果为采纳、已回滚或无法定论；诊断建议不得直接晋升候选。 |

<a id="regression"></a>
## Minimum Change and Regression / 最小改动与回归

`retain` keeps a justified design; `repair` corrects an omitted or wrong constraint; `reorganize` changes ownership/state/handoffs; `simplify` removes a proven redundant layer; `retire` withdraws a mechanism with replacement or decommission obligations. These describe intended design changes, not test or release success. Prefer restoring a structured state binding over adding reviewers to a parameter error. Added agents require independent responsibility, permission or demonstrated parallel benefit. / 保留维持有依据的设计；修复补足错误或缺失约束；重组调整责任、状态及交接；简化删除经证实冗余层；退役撤除机制并处理替代或下线义务。这些是设计改动类型，不是测试发布结果。参数错绑优先恢复结构化状态绑定；增加智能体须有独立职责、权限或实证并行收益。

The evaluation plan includes all four case families; any inapplicable family needs an evidence-backed rationale. Freeze representative and deliberately difficult cases, avoid leaking held-out cases into tuning, and retain exclusions with reasons. An old failure is resolved only when the business condition passes or the scope has legitimately changed under a new contract; deleting its assertion does not resolve it. / 评价计划包含四类案例，不适用须有证据理由。冻结代表性及故意困难案例，避免把留出集泄漏给调优，保存排除理由。旧失败须业务条件通过，或在新契约下合法变更范围；删除断言不算解决。

| Case family / 案例族 | Required question / 必答问题 |
| --- | --- |
| Old failures / 旧失败 | Does the candidate remove the earliest established defect and restore the expected business outcome? / 候选是否消除已定位的早期缺陷并恢复预期业务结果？ |
| Old successes / 旧成功 | Do previously valid paths still pass the same business acceptance within frozen non-inferiority limits? / 原有效路径是否仍通过相同业务验收并满足冻结的不劣化界限？ |
| High risk / 高风险 | Are authority, exact targets, idempotency, sensitive data, irreversible effects and severe errors protected separately? / 权限、精确对象、幂等、敏感数据、不可逆效果及严重错误是否单独受检？ |
| Counterexamples / 反例 | Does the proposal fail where its hypothesis should fail; can removed controls still catch the important fault by another validated path? / 候选能否识别应否定其假设的情况；删除控制后，其他经验证路径能否仍发现重要故障？ |

Compare matched inputs, rules, authority, environment and evaluation criteria. For stochastic systems predeclare repeated trials, seeds when supported, aggregation and uncertainty. Report per-stratum counts, effect sizes, uncertainty, missingness, excluded cases, latency distribution, measured cost and human effort; incomparable confounders restrict claims. No fixed sample size or confidence threshold is universal. Zero severe errors in a small sample proves neither zero risk nor a safe removal of safeguards. / 对照匹配输入、规则、权限、环境及评价口径。随机系统预先定义重复试验、支持时的种子、汇总方式及不确定性。分层报告数量、效果差异、不确定性、缺失、排除案例、延迟分布、实测成本及人工投入；不可比混杂因素限制结论。不存在通用固定样本量或置信阈值，小样本零严重错误不能证明零风险或可安全删除护栏。

<a id="release"></a>
## Release, Stop and Recovery / 发布、停止与恢复

Before activation, the adopting host must atomically verify the current control epoch, expected baseline, candidate digest, release scope, authority and relevant state revision. Advance the epoch on control transfer or rollback so old workers cannot commit new transitions. Pin each run to its admitted workflow/rule/schema versions. Choose and test exactly one documented in-flight policy per class: drain old runs, explicit migration with checkpoint conversion, or cancellation followed by effect reconciliation and authorized compensation. Mixed-version compatibility and authoritative idempotency records must survive deployment. / 激活前，采用宿主须原子核验当前控制代次、预期基线、候选摘要、发布范围、权限及相关状态修订。控制转移或回退时递增代次，阻止旧工作者提交新迁移。每个运行固定准入时的工作流规则和结构版本。每类在途运行明确选择并测试：旧运行排空、带检查点转换的显式迁移，或取消后核对效果并受权补偿。混合版本兼容及权威幂等记录必须跨部署保留。

At release admission, reread actual tool, model, rule, configuration and permission versions and compare them with the frozen evaluation dependency snapshot, even if the candidate digest is unchanged. Any relevant mismatch makes the affected gate `pending` with reason `stale_dependency` and prohibits activation. Create new bindings and repeat affected evaluation, or perform a scoped, evidence-backed compatibility revalidation; retain prior validation as history. Unknown/unpinnable versions cannot be silently assumed compatible. / 发布准入须重读实际工具、模型、规则、配置及权限版本，与冻结评价依赖快照核对，即使候选摘要未变也必须检查。任一相关不符使对应门变为待定，原因为 `stale_dependency`，禁止激活。建立新绑定并重做受影响评价，或进行有范围、有证据的兼容复验；旧验证作为历史保留。未知或无法固定版本不能被默认为兼容。

Schema/data migration requires forward/backward compatibility evidence or a tested cutover and restore plan. Do not promise code rollback can reverse an irreversible data migration. A stop closes new admissions but does not prove in-flight calls stopped. An external result marked `unknown` stays unresolved until authoritative query, callback or operator evidence reconciles it; keep the logical action and any occupied exposure reservation. Never resend solely because a timeout elapsed. / 结构数据迁移须有前后兼容证据，或经测切换恢复计划。不可承诺代码回退能撤销不可逆数据迁移。停止新准入不证明在途调用已停止。外部结果为未知时，须由权威查询、回调或操作人员证据核对后才能解除；保留逻辑动作及占用的暴露额度，不能只因超时而重发。

Freeze stop rules before release: failed mandatory gate, material severe regression, authority/version mismatch, exceeded exposure/budget, or unavailable evidence required to judge safe continuation. Optional telemetry loss is reported with its effect on confidence; it does not automatically block independently verified work. If missing telemetry prevents the preregistered release judgment, stop expansion and record an inconclusive observation result. / 发布前冻结停止规则：必需门失败、重大严重回归、权限版本失配、暴露预算超限，或缺少判断安全续行所必需的证据。可选遥测缺失需报告对置信的影响，不自动阻断已有独立业务依据的工作；若缺失导致无法做出预设发布判断，则停止扩大并记录观察无法定论。

Rollback confirms the previous design is effective; compensation separately addresses business effects already produced. Track each effect as `none_verified`, `applied`, `partial`, `unknown` or `compensated`, with evidence. Compensation itself may fail or require fresh authority. `rolled_back` does not imply affected business tasks succeeded or every obligation is closed. / 回滚核实旧设计重新生效，补偿单独处理已产生的业务效果。每项效果按已证实无效果、已生效、部分、未知或已补偿记录并附证据。补偿自身可能失败或需新授权；已回滚不表示受影响业务任务成功或所有义务已关闭。

<a id="example"></a>
## Worked Example / 完整示例

Illustrative only; no measurements or releases have been performed. / 以下仅为示例，未执行测量或发布。

A refund workflow's lookup returns account `A17`, while its prose handoff causes the payment node to submit `A71`. E1 freezes workflow v3, the rule and provider versions plus request/response evidence. E2 identifies the structured-to-prose handoff as the earliest proved divergence; “the model was distracted” remains an unsupported hypothesis. E3 checks mappings and replays in an isolated fake provider; the architectural hypothesis is that exact identifiers cross an unvalidated generative boundary. / 退款工作流查询返回账户 `A17`，叙述交接却使支付节点提交 `A71`。E1 冻结工作流 v3、规则供应方版本及请求响应证据。E2 定位结构化到叙述的交接为最早已证实偏差；“模型分心”仍为无依据假设。E3 检查映射并用隔离伪供应方重放，架构假设为精确标识跨过未经验证的生成边界。

E4 selects `repair`: pass an immutable account reference and validate target equality before dispatch. E5 freezes wrong-ID failures, valid refunds, duplicate/timeout high-risk cases and a counterexample with a deliberately stale account version. E6 must show correct targets, unchanged successful behavior, no duplicate effects and explicit rejection of stale versions; any missing result leaves validation pending. / E4 选择修复：传递不可变账户引用并在派发前验证对象相等。E5 冻结错号失败、有效退款、重复超时高风险及故意使用过期账户版本的反例。E6 须证明对象正确、旧成功路径不退化、无重复效果且明确拒绝过期版本；缺任何必需结果，验证都保持待定。

E7 plans an authorized, bounded cohort and drains old runs; replay uses no real refunds. If an E8 request times out after potential payment, freeze its logical action and reconcile with the provider before retry. A release rollback restores routing but does not refund the refund or erase its receipt. E9 can select `repair/adopted` only after required comparison and observation pass; use `repair/rolled_back` after confirmed rollback, or `repair/inconclusive` when evidence cannot establish benefit. / E7 规划已授权有界群组并排空旧运行，重放不产生真实退款。E8 若请求可能付款后超时，冻结其逻辑动作并先向供应方核对。发布回滚恢复路由，不会撤销已付退款或抹掉回执。E9 仅在必需对照观察通过后记为修复／已采纳；确认回退后记为修复／已回滚；无法证明收益时为修复／无法定论。

<a id="acceptance"></a>
## Acceptance Scenarios / 验收场景

All 14 cases below are specifications with expected outcomes, `not_executed`. An adopter must attach actual input/host/version, observed result, evidence and evaluator before claiming a pass. Asset/link validation is not a business execution result. / 以下 14 项均为带预期结果的规格，状态为未执行。采用方须附实际输入、宿主版本、观察结果、证据及评价者，才能声称通过。资产链接检查不等于业务执行结果。

| ID | Given / 输入 | Expected / 预期结果 |
| --- | --- | --- |
| AET-01 | A single transient read failure recovers within the frozen contract. / 单次临时读取失败在冻结契约内恢复。 | Inner-loop recovery; no silent design mutation or budget reset. / 内环恢复，不暗改设计或重置预算。 |
| AET-02 | Final output is wrong; handoff evidence proves an earlier identifier change. / 最终输出错误，交接证据证明更早的标识改变。 | E2 names the handoff and evidence; unsupported psychological explanations stay hypotheses. / E2 绑定交接及证据，心理解释仅为假设。 |
| AET-03 | Candidate improves old failures but breaks an old success beyond tolerance. / 候选改好旧失败，却使旧成功超容差退化。 | Validation fails; aggregate improvement cannot permit adoption. / 验证失败，总体改善不能放行采纳。 |
| AET-04 | One severe unauthorized effect appears among many successful cases. / 大量成功中出现一项严重未授权效果。 | Mandatory safety gate fails; halt expansion and invoke authorized containment. / 必需安全门失败，停止扩大并受权遏制。 |
| AET-05 | A removed review catches no observed errors, but no counterexample tests its replacement. / 拟删评审未发现错误，却无反例验证替代检查。 | Simplification remains unvalidated; no inferred zero marginal value. / 简化保持未验证，不推断零增益。 |
| AET-06 | Candidate uses newer rules and easier inputs than baseline. / 候选规则更新且输入更简单。 | Mark confounding; rerun matched strata or restrict claims and return inconclusive. / 标记混杂，重跑匹配分层或限制结论并无法定论。 |
| AET-07 | Optional latency telemetry is missing; all independent required business evidence is present. / 可选延迟遥测缺失，独立必需业务证据齐备。 | Business may complete; metric remains unknown with a declared gap. / 业务可完成，指标保留未知及缺口。 |
| AET-08 | A high-risk unresolved effect has been handed to an operator. / 未解决高风险效果已转人工。 | Handoff may complete; original business completion remains false. / 交接可完成，原业务完成仍为否。 |
| AET-09 | Probe recommends production activation without deployment authority. / 探针建议激活生产但无部署权限。 | Advice is recorded; no activation or authority mutation. / 记录建议，不激活也不改变权限。 |
| AET-10 | Payment times out, then a new run retries under a new workflow version. / 付款超时，新工作流版本的新运行想重试。 | Preserve logical action/idempotency; reconcile unknown effect before any repeat write. / 保留逻辑动作幂等，未知效果先核对再重写。 |
| AET-11 | Rollback advances epoch while an old worker submits a result. / 回滚递增代次时旧工作者提交结果。 | Reject stale state commit; retain receipt as evidence and reconcile any actual effect. / 拒绝旧代次状态提交，保留回执并核对真实效果。 |
| AET-12 | Candidate includes incompatible schema migration with old requests in flight. / 候选含不兼容结构迁移且旧请求在途。 | Block activation until a tested drain/migration/cancellation and recovery policy exists. / 测试排空迁移取消及恢复策略前不得激活。 |
| AET-13 | Code returns to baseline but an external write remains unconfirmed or uncompensated. / 代码恢复基线，外部写仍未知或待必要补偿。 | `rolled_back` only for confirmed design reversion; release completion stays false and owner persists. / 仅确认设计回退可记已回滚，发布完成为否且责任持续。 |
| AET-14 | Baseline/criteria change after evaluation, or an external tool upgrades while candidate digest stays unchanged. / 评价后基线口径改变，或候选摘要不变但外部工具升级。 | Reject stale bindings; affected gate becomes pending (`stale_dependency` for dependency drift), no activation until new bound evaluation or scoped compatibility revalidation; preserve old results. / 拒绝旧绑定，对应门转待定，依赖漂移原因为 `stale_dependency`；完成新绑定评价或范围化兼容复验前不激活，保留旧结果。 |

## Completion and Reuse / 完成与复用

An evolution record can close with an honest inconclusive decision and assigned outstanding duties. That is not successful validation, release or business completion. An adopted ADR must retain baseline/candidate/plan/release references, evidence, exact delta, rejected alternatives, uncertainty, owners, removal criteria and reassessment triggers. Changed traffic, rules, model/tool versions, severe failures or expired evidence can reopen the design question with a new evolution ID linked to the prior ADR. / 演化记录可在如实无法定论并明确剩余责任后关闭，但不等于验证、发布或业务成功。采纳 ADR 须保存基线候选计划发布引用、证据、精确差异、未选方案、不确定性、责任人、移除条件及复评触发。流量、规则、模型工具版本变化、严重失败或证据过期可用新演化编号关联旧 ADR 并重开设计问题。
