# Approval Gate Independent Probes / 审批门独立可观测性探针

Name / 名称: Approval Gate Workflow Observability / 审批门工作流可观测性。
Description / 描述: Reconstruct approval chains, diagnose gaps/drift/bypass and propose verifiable supplements without acquiring action authority. / 重建审批链路、诊断缺口漂移绕过并提出可验证补全，不取得行动权。

Identity / 身份: `PATTERN_0047` · local specification / 本地规格 `0.1.0` · source contract / 来源契约 `1.0.0` · `draft` · `specification_only`.

## Quick Navigation / 快速导航

- [Probe catalog / 探针目录](#probes)
- [Metric contract / 指标契约](#metric-contract)
- [Fifty metrics / 五十项指标](#metrics)
- [Gaps and alerts / 缺口与告警](#gaps)
- [Acceptance / 验收](#acceptance)

## Usage, modes and authority / 用法、模式与权限

Read with [execution](approval-gate-execution-flow.md), the [shared contract](approval-gate-contract.md) and [source map](approval-gate-source-map.json). These probes and `AGM01–AGM50` are specifications, not installed detectors or registered runtime calculators. Keep module `MET_GOV_*`, existing runtime metric names and these local IDs distinct; translations do not establish executable aliases. / 同时阅读执行、共享契约与来源映射。本探针及 50 项指标是规格，不是已安装检测器或注册运行计算器；与治理模块及既有运行指标分开，译名不构成可执行别名。

| Mode / 模式 | Inputs and permitted result / 输入与允许结果 |
|---|---|
| Offline / 独立离线 | Historical events, policy/approval snapshots, execution and external ledgers → replay, gaps, metrics and findings. No production mutation. / 历史事件、策略审批快照、执行及外部账本生成回放、缺口、指标发现，不修改生产。 |
| Realtime sidecar / 旁路实时 | Subscribe and correlate asynchronously; default is nonblocking. / 订阅并异步关联，默认不阻断主流程。 |
| Interactive supplement / 交互补全 | A bounded request produces sourced field candidates and an explicit adoption receipt. / 有界请求产生有来源字段候选及明确采纳回执。 |
| Control advice / 控制建议 | Recommend pause, revalidation, receipt invalidation, investigation or rule review to an authorized owner. No direct control. / 向有权方建议暂停、重检、回执失效、调查或规则复核，不直接控制。 |
| Synchronous precheck / 闸前同步检查 | Explicitly configured completeness/binding/event checks before human review or execution; never business judgment or approval. / 显式配置人审或执行前的完整性、绑定及事件检查，不代替业务判断或批准。 |

The probe cannot approve/deny, issue receipts, change decisions or proposal scope, modify source records or directly invoke effectful tools. A missing approval record is an evidence gap; only authoritative negative evidence can establish that no valid approval existed. Fatigue signals are diagnostic, not automatic invalidation or permission to remove gates. / 探针不能批准拒绝、签发回执、改变决定或提案范围、修改源记录或直接调用副作用工具。审批记录缺失是证据缺口，只有权威否定证据才能证明不存在有效批准。疲劳信号用于诊断，不自动使批准失效，也不授权删除门禁。

## Workflow and quality / 流程与质量

Ingest → authenticate/deduplicate → correlate tenant/run/proposal/policy/receipt/execution/effect → evaluate applicable checks → produce gaps and evidence-backed findings → query bounded sources → submit supplements → track adoption/closure. Preserve event occurrence and collection time, source revisions, causal order, late arrivals and conflicting identities. / 采集、认证去重、关联租户运行提案策略回执执行效果、执行适用检查、产生缺口与证据化发现、有界查询、提交补全、跟踪采纳收口；保留事件发生与采集时间、来源版本、因果、迟到及身份冲突。

| Quality / 质量 | Meaning and limit / 含义与限制 |
|---|---|
| L0 | Missing or uncorrelatable data; report gaps only. / 缺失或无法关联，只报告缺口。 |
| L1 | Correlatable but incomplete; label basic counts and rough trends. / 可关联但不完整，基础计数与粗趋势须标注。 |
| L2 | Required fields present with identifiable sources; routine diagnosis. / 必要字段齐全且来源可识别，可作常规诊断。 |
| L3 | Source, digest, version and freshness verified; binding/drift analysis and verified supplements. / 来源摘要版本时效已验证，支持绑定漂移分析与核验补全。 |
| L4 | Events, snapshots and destination effects replayable; audit and policy simulation. / 事件快照与目的端效果可重放，支持审计及策略仿真。 |

Quality is assessed per field/check/window, not assigned by the best event in a run. A high quality label never creates authority. Preserve `unknown` for missing required evidence and `not_applicable` for a known empty eligible population; neither becomes a zero failure rate or 100% success. / 质量按字段、检查及窗口评估，不取运行中最好事件等级；高质量不能创造权限。必要证据不足为未知，已知无适用总体为不适用，均不能记为零失败率或百分百成功。

<a id="probes"></a>
## Probe catalog / 探针目录

`AGP01–AGP28` preserve source §11. Distinct-ID historical evidence is required for quorum and bypass checks; the probe's own successful checks are not an independent execution inventory. / 对应来源第 11 节；会签及绕过检查需身份可区分的历史证据，探针自己的成功检查日志不是独立执行清单。

<!-- approval:probe_checks:start -->
| ID | Source / 来源 | Definition / 定义 |
|---|---|---|
| AGP01 | ## 11.1 标识关联探针 | Correlate trace/run/proposal/request/receipt/execution/effect identities and causality; detect orphans, duplicates and cross-run associations. / 关联链路运行提案请求回执执行效果与因果，发现孤立对象、重复标识和跨运行误关联。 |
| AGP02 | ## 11.2 提案完整性探针 | Check actor/action/tool/version/environment, versioned targets, quantity/value, differences, evidence, preconditions, impact, reversibility and proposal digest. / 检查主体动作工具版本环境、对象版本、数量金额、差异证据、业务前提、影响可逆性及提案摘要。 |
| AGP03 | ## 11.3 对象确定性探针 | Require stable targets, deterministic batch manifests and query plus result snapshots; detect ambiguous names or missing versions. / 要求稳定对象、确定批量清单、查询与结果快照，发现名称歧义及缺失版本。 |
| AGP04 | ## 11.4 差异突出探针 | Check that the card highlights account/amount/target/artifact/permission/recipient/data/policy changes, measuring high-risk omissions. / 检查审批卡突出账户金额对象工件权限收件人数据及策略变化，度量高风险差异遗漏。 |
| AGP05 | ## 11.5 证据充分性探针 | Check required evidence, trusted sources, expiry, target-version binding, conflicts, verifier and independent checks for high-risk changes. / 核验必要证据、可信来源、期限、对象版本绑定、冲突、核验者及高风险独立核验。 |
| AGP06 | ## 11.6 可审条件探针 | Check clear targets, complete evidence, visible impact/differences/reversibility and determined policy before human review. / 进入人审前检查对象明确、证据完整、影响差异可逆性可见及策略确定。 |
| AGP07 | ## 11.7 策略匹配探针 | Verify contemporaneous policy/version/digest, rule precedence, role/count/expiry/use limits and explicit conflict handling. / 验证当时适用策略版本摘要、拒绝优先、角色人数期限次数及显式冲突处理。 |
| AGP08 | ## 11.8 路由正确性探针 | Independently compare risk/policy inputs and observed routes; detect wrongful automation, human review of prohibited or incomplete proposals and needless escalation. / 独立比较风险策略输入与实际路由，发现错放行、禁止或缺证提案进入人审及不必要升级。 |
| AGP09 | ## 11.9 审批卡信息质量探针 | Check card summary, target/scope, material changes, verified evidence, impact/reversal, limits, roles, validity/usage and conditions. / 核验审批卡摘要、对象范围、关键变化、证据、影响可逆性、限制角色、期限次数及条件。 |
| AGP10 | ## 11.10 审批者资格探针 | Verify identity, current role/authority, substitution/delegation, authorization tier and conflicts; detect decisions after suspension or revocation. / 核验身份、当前角色权限、代班委托、层级及利益冲突，发现停职或撤权后审批。 |
| AGP11 | ## 11.11 职责分离探针 | Detect prohibited proposer/executor self-approval, policy-beneficiary conflicts, reused identities across roles and non-independent review. / 检查禁止的发起者执行者自批、策略受益冲突、多角色复用身份及不独立复核。 |
| AGP12 | ## 11.12 会签完整性探针 | Check every role and count, still-valid decisions, vetoes, compatible conditions and duplicate-decision counting. / 检查全部角色人数、决定有效性、否决、条件相容及重复决定计数。 |
| AGP13 | ## 11.13 决定范围探针 | Verify decisions remain limited to the specific action, objects, environment, tool/version, validity and usage; detect expanded vague session consent. / 核验决定仅适用于当前动作对象环境工具版本期限次数，发现含糊会话许可被扩大。 |
| AGP14 | ## 11.14 回执绑定探针 | Check receipt proposal/policy digests, decision set, scope, expiry/use limit and authentic signature or source; missing bindings are high-risk gaps. / 检查回执提案策略摘要、决定集合、范围、期限次数及真实签名来源；缺少绑定形成高风险缺口。 |
| AGP15 | ## 11.15 等待持久化探针 | Verify durable run state, proposal/policy digests, decisions/missing roles, expiry, resume node, preconditions and state version during waiting. / 核验等待期间持久运行状态、提案策略摘要、决定和缺失角色、期限恢复点、前提及状态版本。 |
| AGP16 | ## 11.16 恢复点探针 | Verify trusted checkpoint, current proposal/policy, revalidation entry, run/state version and protection against replaying pre-interruption effects. / 核验可信检查点、当前提案策略、重检入口、运行状态版本及中断前动作的防重复措施。 |
| AGP17 | ## 11.17 提案漂移探针 | Compare approved versus current objects/count/value/parameters/tool/environment/versions/reversibility/visibility; report each semantic change. / 比较批准与当前对象数量金额参数工具环境版本可逆性可见性，报告全部语义变化。 |
| AGP18 | ## 11.18 策略漂移探针 | Compare approved/current policy digests, effective time, revocation and emergency rules; identify use of obsolete authorization. / 比较批准与当前策略摘要、生效时间、撤销及紧急规则，发现旧授权继续使用。 |
| AGP19 | ## 11.19 有效期和使用次数探针 | Check request/decision/receipt expiry, usage, atomic single-use consumption and revocation; distinguish blocked attempts from repeated effects. / 检查请求决定回执时效、使用次数、原子单次消费及撤销，区分被阻断尝试与已重复效果。 |
| AGP20 | ## 11.20 业务前置条件新鲜度探针 | Verify fresh balance/inventory/person/account/contract/artifact/ticket/query/window conditions on resume and detect changes during waiting. / 恢复时核验余额库存人员账户合同工件工单查询结果及执行窗口新鲜度，发现等待期间变化。 |
| AGP21 | ## 11.21 幂等执行探针 | Check proposal-bound durable idempotency, external-status lookup before retry, per-object partial recovery and callback replay protection. / 核验绑定提案的持久幂等键、重试前外部查询、部分成功逐对象恢复及回调重放保护。 |
| AGP22 | ## 11.22 实际效果一致性探针 | Compare requested effect, approved scope and actual effect; detect overrun, omissions, wrong objects, duplicates, partial success and local/destination disagreement. / 比较请求效果、批准范围和实际效果，发现超额遗漏错对象重复部分成功及本地目的端不一致。 |
| AGP23 | ## 11.23 审批绕过探针 | Investigate no-receipt execution, direct-tool paths, forged approval text, composed low-risk effects, self-relaxed policy, cross-environment or cross-run reuse. / 调查无回执执行、直调工具、伪造已批文本、低风险组合产生高风险效果、自改策略、跨环境或跨运行复用。 |
| AGP24 | ## 11.24 补偿与收口探针 | Check failure compensation/escalation, compensation scope versus actual effects, its own governance, eventual closure and explicit residual obligations. / 检查失败补偿升级、补偿范围与实际效果、补偿自身治理、最终关闭及明确未决责任。 |
| AGP25 | ## 11.25 策略变更治理探针 | Check separately proposed rule changes, old/new diff, expanded automatic exposure, historical simulation, independent approval, rollback and observation period. / 检查规则变更独立提案、前后差异、扩大的自动权限、历史模拟、独立批准、回滚与观察期。 |
| AGP26 | ## 11.26 审批疲劳探针 | Observe reviewer volume, decision speed/streaks, repeated cards, zero returns/rejections, access interactions and unusual time patterns; fatigue is advisory only. / 观察审批负荷、速度及连续同意、重复卡片、零退回拒绝、访问交互及异常时段；疲劳仅为诊断提示。 |
| AGP27 | ## 11.27 自动放行适配探针 | Assess automatic rules for stability, failures, compensation cost, bypass, calculable scope, quality and current policy; propose independently reviewed improvements. / 评估自动规则稳定性、失败补偿成本、绕过、范围可计算性、数据质量及当前策略，提出需独立复核的改进建议。 |
| AGP28 | ## 11.28 数据最小化探针 | Minimize sensitive card/event/probe data, verify classification/access/retention and ensure supplementary queries never widen authorized access. / 最小化审批卡事件探针敏感数据，验证分级访问留存，确保补全查询不扩大授权访问范围。 |
<!-- approval:probe_checks:end -->

<a id="metric-contract"></a>
## Metric contract / 指标契约

Every metric result includes ID/definition version, window and watermark, action/scenario, tenant/environment, policy version, risk, unit, sample count, population source, numerator/denominator or distribution observations, exclusions, quality, missing/unknown counts, late-data revision and supplemented-field proportion. No computation implementation is supplied. / 每项指标结果需有编号定义版本、窗口水位、动作场景、租户环境、策略版本、风险、单位样本量、总体来源、分子分母或分布观测、排除项、质量、缺失未知数、迟到修订及补全占比；本次未提供计算实现。

| Family / 分组 | Grain, denominator and limits / 粒度、分母与限制 |
|---|---|
| AGM01–06 Routing / 路由 | One first routing decision per frozen proposal version in the cohort. “Routable” includes attempts returned for missing evidence, or supplementation disappears from the denominator. Include escalation/waits separately and never imply the five listed routes sum to 100% when external waits exist. Independently recompute applicable policy for inconsistency. / 队列中每份冻结提案版本取首次路由；可路由总体包含因缺证退回的尝试，否则补证被排除。升级等待另记，有外部等待时不声称五类之和为 100%；以独立适用策略重算不一致。 |
| AGM07–13 Efficiency / 效率 | Request-created cohorts; durations in seconds from creation to first valid decision or full valid quorum. Completed percentiles identify their population; report pending/expired ages and censored counts separately. Publish the chosen quantile/method and minimum sample rule. / 按请求创建队列，秒数为创建到首次有效决定或完整有效会签；完成时延分位明确总体，另报未决过期年龄及截尾数，声明分位算法与最小样本。 |
| AGM14–21 Quality / 质量 | Do not mix request, decision, card and high-risk-difference grains. Attempts for self-approval/quorum interception require authenticated attempt inventories, including blocked and successful attempts. Deny truth is established independently. / 不混合请求、决定、卡片及高风险差异粒度。自批会签拦截须有认证尝试清单，包含阻断和成功尝试；独立建立拒绝真值。 |
| AGM22–28 Binding / 绑定 | Cohort receipts by issuance; record request vs receipt expiry separately. For drift, snapshot the pending-execution receipt population at cohort entry so invalidated receipts are not removed retroactively. Replays use attempt identities, not event counts. / 回执按签发队列，请求过期与回执过期分开；漂移分母取进入队列时待执行回执快照，不能事后删除失效回执；重放按尝试身份计数。 |
| AGM29–36 Execution / 执行 | Destination/admission inventories, including unknown and failed effects, define controlled executions. API success is not reconciled success. “No valid receipt” requires historical authority evidence; otherwise report unknown coverage separately. Compensation denominator includes every required compensation, including pending/failed cases. / 以目的端和准入清单定义执行总体，包含未知失败效果；接口成功不等于核对成功。无有效回执须有历史权限证据，否则另报未知覆盖；补偿分母包括全部需补偿项及待决失败项。 |
| AGM37–44 Data / 数据 | Expected event/field inventories come from versioned applicable contracts, not received-event totals. Count each expected event slot once. Adopt/reject per field; pending and expired supplements stay visible, partial acceptance splits field outcomes. / 预期事件字段由版本化适用契约确定，不能以收到总量自证完整；每个预期槽计一次。采纳拒绝逐字段计，待决过期保持可见，部分采纳拆字段结果。 |
| AGM45–50 Fatigue / 疲劳 | Per authenticated approver and policy/risk strata. Configure reading threshold, similarity method and sample/window rules before measuring. Fast clicks and zero rejection are signals requiring review, not proof of misconduct or safe automation. / 按认证审批者及策略风险分层；测量前配置阅读阈值、相似度方法、样本窗口规则。极速与零拒绝只是需复核信号，不证明违规或自动放行安全。 |

Do not mix policy versions or incomplete/full windows without explicit stratification. Show verified subsets and whole-population coverage together. Late events revise a versioned window after the allowed-lateness watermark; never silently rewrite a previously published value. Sample scarcity yields insufficient evidence, not a decisive conclusion. / 不经分层不能混合策略版本或完整与残缺窗口；同时显示已验证子集及全量覆盖。迟到事件按容许迟到水位修订带版本窗口，不静默改历史值；小样本只能表示证据不足。

<a id="metrics"></a>
## Metric catalog / 指标目录

The source has no metric IDs; AGM IDs are local stable definitions in source order. Formulas below retain source intent; the contract above fixes population ambiguities. / 来源未给指标编号，AGM 为按原顺序分配的本地稳定定义；下列公式保留来源意图，上述契约明确总体歧义。

<!-- approval:metrics:start -->
| ID | Source / 来源 | Definition / 定义 |
|---|---|---|
| AGM01 | 自动放行率 | Automatic allowance rate / 自动放行率<br>Automatically allowed proposals / all routable proposals / 自动放行提案数 ÷ 可路由提案总数 |
| AGM02 | 人工审批率 | Human review rate / 人工审批率<br>Proposals entering human review / all routable proposals / 进入人审提案数 ÷ 可路由提案总数 |
| AGM03 | 补证率 | Evidence return rate / 补证率<br>Proposals returned for evidence / all routable proposals / 返回补证提案数 ÷ 可路由提案总数 |
| AGM04 | 硬拒绝率 | Hard denial rate / 硬拒绝率<br>Hard-denied proposals / all routable proposals / 硬拒绝提案数 ÷ 可路由提案总数 |
| AGM05 | 升级率 | Escalation rate / 升级率<br>Escalated proposals / all routable proposals / 升级提案数 ÷ 可路由提案总数 |
| AGM06 | 路由不一致率 | Routing inconsistency rate / 路由不一致率<br>Routes inconsistent with independently evaluated policy / all routable proposals / 实际路线与策略计算不一致数 ÷ 可路由提案总数 |
| AGM07 | 首次响应时间 | First response time / 首次响应时间<br>First valid approver decision time minus request creation time (seconds) / 第一位审批者决定时间减请求创建时间 |
| AGM08 | 完整会签时间 | Full quorum time / 完整会签时间<br>Time when all required roles are satisfied minus request creation time (seconds) / 满足全部角色时间减请求创建时间 |
| AGM09 | 等待时间中位数 | Median waiting time / 等待时间中位数<br>Median human-request waiting duration; disclose observed and censored populations / 全部人工审批等待时间的中位数 |
| AGM10 | 等待时间高分位 | High-percentile waiting time / 等待时间高分位<br>Configured high quantile of human-request waiting duration; disclose quantile and method / 全部人工审批等待时间的高分位值 |
| AGM11 | 超时率 | Timeout rate / 超时率<br>Expired approval requests / all human approval requests / 过期审批请求数 ÷ 人工审批请求总数 |
| AGM12 | 升级后完成率 | Completion after escalation / 升级后完成率<br>Completed escalated requests / all escalated requests / 升级后完成的请求数 ÷ 升级请求总数 |
| AGM13 | 补材料次数 | Material supplementation count / 补材料次数<br>Total material-supplement rounds / approval requests in the cohort / 单个审批请求平均补充材料次数 |
| AGM14 | 退回率 | Return rate / 退回率<br>Human requests asking for more material or returning the proposal / all human approval requests / 请求补充或退回提案数 ÷ 人工审批请求总数 |
| AGM15 | 拒绝率 | Rejection rate / 拒绝率<br>Rejected human approval requests / all human approval requests / 审批拒绝数 ÷ 人工审批请求总数 |
| AGM16 | 附条件批准率 | Conditional approval rate / 附条件批准率<br>Conditionally allowed decisions / all allowed decisions / 附条件允许数 ÷ 允许决定总数 |
| AGM17 | 无效审批决定率 | Invalid decision rate / 无效审批决定率<br>Decisions invalid for identity, role or time / all decisions / 身份、角色或时效无效决定数 ÷ 决定总数 |
| AGM18 | 自批拦截率 | Self-approval interception rate / 自批拦截率<br>Self-approval attempts blocked by separation / all self-approval attempts / 被职责分离阻止的自批数 ÷ 自批尝试总数 |
| AGM19 | 会签不完整拦截率 | Incomplete-quorum interception rate / 会签不完整拦截率<br>Execution attempts blocked for missing roles or counts / all incomplete-quorum attempts / 未满足角色或人数而被阻止的执行数 ÷ 不完整会签尝试数 |
| AGM20 | 决策材料完整率 | Decision-material completeness / 决策材料完整率<br>Complete approval cards / all approval cards / 完整审批卡数 ÷ 审批卡总数 |
| AGM21 | 关键差异展示率 | Material-difference display coverage / 关键差异展示率<br>Displayed high-risk changes / all required high-risk changes / 已展示高风险变化数 ÷ 应展示高风险变化数 |
| AGM22 | 提案摘要覆盖率 | Proposal-digest coverage / 提案摘要覆盖率<br>Receipts binding a proposal digest / all receipts / 绑定提案摘要的回执数 ÷ 回执总数 |
| AGM23 | 策略摘要覆盖率 | Policy-digest coverage / 策略摘要覆盖率<br>Receipts binding a policy digest / all receipts / 绑定策略摘要的回执数 ÷ 回执总数 |
| AGM24 | 回执过期率 | Unused receipt expiry rate / 回执过期率<br>Receipts expiring unused / all receipts / 未使用即过期回执数 ÷ 回执总数 |
| AGM25 | 回执重放拦截率 | Receipt replay interception / 回执重放拦截率<br>Blocked duplicate-consumption attempts / all duplicate-consumption attempts / 被拦截重复消费数 ÷ 重复消费尝试数 |
| AGM26 | 提案漂移失效率 | Proposal-drift invalidation rate / 提案漂移失效率<br>Receipts invalidated by proposal changes / pending-execution receipts at cohort entry / 因提案变化失效回执数 ÷ 待执行回执总数 |
| AGM27 | 策略漂移失效率 | Policy-drift invalidation rate / 策略漂移失效率<br>Receipts invalidated by policy changes / pending-execution receipts at cohort entry / 因策略变化失效回执数 ÷ 待执行回执总数 |
| AGM28 | 前置条件变化率 | Precondition-change rate / 前置条件变化率<br>Resumes discovering changed business conditions / all resumes / 恢复时发现业务条件变化数 ÷ 恢复次数 |
| AGM29 | 执行前重检覆盖率 | Pre-execution revalidation coverage / 执行前重检覆盖率<br>High-risk executions with completed revalidation / all high-risk executions / 完成重检的高风险执行数 ÷ 高风险执行总数 |
| AGM30 | 有效回执覆盖率 | Valid receipt coverage / 有效回执覆盖率<br>Controlled executions with verified valid receipts / all controlled executions / 具备有效回执的受控执行数 ÷ 受控执行总数 |
| AGM31 | 幂等键覆盖率 | Idempotency-key coverage / 幂等键覆盖率<br>External writes with a bound idempotency key / all external writes / 具备幂等键的外部写操作数 ÷ 外部写操作总数 |
| AGM32 | 实际效果一致率 | Actual-effect consistency / 实际效果一致率<br>Completed executions whose actual effects match approved scope / all completed executions / 实际效果与批准范围一致数 ÷ 完成执行总数 |
| AGM33 | 部分成功率 | Partial-success rate / 部分成功率<br>Partially successful executions / all executions / 部分成功执行数 ÷ 执行总数 |
| AGM34 | 补偿成功率 | Compensation success rate / 补偿成功率<br>Successful compensations / all required compensations / 成功补偿数 ÷ 需要补偿数 |
| AGM35 | 审批绕过率 | Approval bypass rate / 审批绕过率<br>Executions proven to lack valid approval / all controlled executions / 无有效审批执行数 ÷ 受控执行总数 |
| AGM36 | 未授权副作用率 | Unauthorized side-effect rate / 未授权副作用率<br>Executions with effects outside approved scope / all executions / 出现批准范围外效果的执行数 ÷ 执行总数 |
| AGM37 | 事件完整率 | Event completeness / 事件完整率<br>Received applicable required event slots / all expected required event slots / 已收到必需事件数 ÷ 应收到必需事件数 |
| AGM38 | 标识关联率 | Identifier correlation / 标识关联率<br>Completely correlated chains / all runs / 可完整关联链路数 ÷ 运行总数 |
| AGM39 | 来源可验证率 | Source verifiability / 来源可验证率<br>Key data items with verifiable sources / all key data items / 来源可验证数据项数 ÷ 关键数据项总数 |
| AGM40 | 新鲜度合格率 | Freshness compliance / 新鲜度合格率<br>Freshness-compliant items / all freshness-constrained items / 时效合格数据项数 ÷ 有时效要求数据项总数 |
| AGM41 | 可重放率 | Replayability / 可重放率<br>Fully replayable chains / all runs / 可完整重放链路数 ÷ 运行总数 |
| AGM42 | 数据冲突率 | Data conflict rate / 数据冲突率<br>Conflicting key data items / all key data items / 存在冲突的数据项数 ÷ 关键数据项总数 |
| AGM43 | 补全成功率 | Supplement acceptance rate / 补全成功率<br>Accepted supplement fields / all submitted supplement fields / 被采纳补全字段数 ÷ 提交补全字段数 |
| AGM44 | 补全拒绝率 | Supplement rejection rate / 补全拒绝率<br>Rejected supplement fields / all submitted supplement fields / 被拒绝补全字段数 ÷ 提交补全字段数 |
| AGM45 | 单人小时审批量 | Hourly reviewer volume / 单人小时审批量<br>Decisions completed by one authenticated approver per hour / 单个审批者一小时内完成的决定数 |
| AGM46 | 极速批准率 | Very-fast approval rate / 极速批准率<br>Allowed decisions below configured reading time / all allowed decisions / 低于配置阅读时间的允许决定数 ÷ 允许决定总数 |
| AGM47 | 连续同意长度 | Longest approval streak / 连续同意长度<br>Maximum consecutive allowed decisions per authenticated approver / 单个审批者连续允许决定的最大数量 |
| AGM48 | 重复审批卡比例 | Repeated-card share / 重复审批卡比例<br>Highly similar approval cards / all approval cards / 高相似度审批卡数 ÷ 审批卡总数 |
| AGM49 | 长期零拒绝规则数 | Long-term zero-rejection rules / 长期零拒绝规则数<br>Rules with zero rejections in the observation window and sufficient samples / 在观察期内无拒绝且样本足够的规则数 |
| AGM50 | 高风险快速批准率 | High-risk very-fast approval rate / 高风险快速批准率<br>High-risk allowed decisions below configured decision time / all high-risk allowed decisions / 高风险且决策时长过短的允许数 ÷ 高风险允许数 |
<!-- approval:metrics:end -->

<a id="gaps"></a>
## Gaps, supplements and alerts / 缺口、补全与告警

Classify gaps as identity/correlation, version, digest, time, role identity, evidence, state/checkpoint, effect, causality or semantics/units. Prioritize missing authority, prechecks, scope, separation and unknown effects above display gaps. Track `open → sourcing → candidate_ready → submitted → accepted | partially_accepted | rejected | expired | closed_unresolved`; a sourced candidate does not close a gap until its recipient verifies adoption. / 缺口分为标识关联、版本、摘要、时间、角色身份、证据、状态检查点、效果、因果、语义单位；授权重检范围职责与未知效果优先于展示缺口。按所列状态跟踪，有候选不等于缺口关闭，须接收方验证采纳。

Follow the [supplement exchange](approval-gate-contract.md#supplement-exchange--补全交互): append only, per-field provenance/type/freshness/conflicts, version-bound target, explicit adoption receipt, no forged approval, and a new proposal for semantic changes. Optional collection failure retains the gap and lowers quality; it never weakens execution controls. / 遵循补全协议：仅追加、逐字段来源类别时效冲突、版本绑定目标、明确采纳回执、不伪造批准、语义变化生成新提案；可选采集失败保留缺口并降低质量，不能放松执行控制。

| Severity / 级别 | Evidence and recommendation / 证据与建议 |
|---|---|
| Critical / 严重 | Confirmed unauthorized execution, drift executed, duplicate effects, hard-deny bypass, forged/revoked identities or cross-environment approval. Recommend stopping new dispatch and incident review; probe cannot stop it itself. / 已证实无权执行、漂移仍执行、重复效果、绕过硬拒绝、伪造撤权身份或跨环境批准；建议停后续派发及事件处理，探针不自行停机。 |
| High / 高 | Missing receipt bindings, missing revalidation, changed preconditions, incomplete quorum, duty conflict, broken checkpoint or unreconciled effects. Distinguish a missing record from a confirmed violation. / 缺回执绑定或重检、前提变化、会签不全、职责冲突、坏检查点或效果未核对；区分记录缺失与已证实违规。 |
| Medium / 中 | Card omissions, excessive wait/material requests, route disagreement before execution, metric gaps or supplement conflicts. / 卡片遗漏、等待补证过多、执行前路由不一致、统计缺口或补全冲突。 |
| Low / 低 | Noncritical lateness, display gaps, redundant review candidates or retention improvements. / 非关键迟到、展示缺失、冗余人审候选或保留期改进。 |

Isolate a failing rule, deduplicate repeated findings and keep closure reason/evidence and rule version. Alert delivery success is not control adoption. Source outage, conflicting IDs, partial windows and observer lag remain explicit. Sensitive data queries/exports themselves need applicable authorization; minimize account/person/secret plaintext, enforce access and per-artifact retention, and aggregate reviewer signals to avoid unnecessary individual exposure. / 隔离单规则失败、发现去重，保存关闭原因证据及规则版本；告警送达不等于控制采纳。源故障、标识冲突、残缺窗口及观测延迟保持显式。敏感查询导出自身遵循适用授权，最小化账户个人密钥明文，按资产控制访问留存，并聚合审批者信号以减少不必要个人暴露。

<a id="acceptance"></a>
## Views, examples and acceptance / 视图、示例与验收

Produce a single-run timeline, approval queue, policy outcomes, reviewer workload and data-quality view. Return `probe_run_id`, mode/window, event/trace counts, quality/missingness, findings/gaps by status, metric/report references and completion time. Per trace show bindings, revalidation, execution/effects, supplements/adoption and final quality. These are output requirements, not a built dashboard. / 输出单运行时间线、审批队列、策略效果、审批负荷和数据质量视图；返回探针运行模式窗口、事件链路计数、质量缺失、发现缺口状态、指标报告引用及完成时间。逐链路展示绑定重检执行效果补全采纳和最终质量；这是输出要求，不是已建仪表盘。

For the source payroll example (798 → 800 people, +CNY 38,444.00), report both manifest and amount drift and that the old receipt does not authorize the new proposal. The probe may reconstruct the two new identities and the deterministic delta with authorized evidence; it cannot add them to an approved manifest or create new approval. / 来源工资示例需报告人员集合与金额双重漂移，旧回执不授权新提案；探针可凭获准证据重建新增两人及差额，不能将其加入已批清单或生成批准。

All `AGPT` cases below are `not_executed` integration requirements. The minimum source set includes correlation, proposal/evidence/policy checks, identity/separation/quorum, receipt binding, durable waits/resume, proposal/policy drift, expiry/usage, idempotency/effects/bypass, gap supplements and waiting/expiry measurements; do not claim full coverage when these are absent. / 下列均为未执行集成要求；最小集合包括关联、提案证据策略、身份职责会签、回执绑定、持久等待恢复、提案策略漂移、时效次数、幂等效果绕过、缺口补全及等待过期度量；缺项不能声称完整覆盖。

<!-- approval:probe_cases:start -->
| ID | Source / 来源 | Definition / 定义 |
|---|---|---|
| AGPT01 | 能从历史事件重建一条完整审批链路； | Reconstruct a complete approval chain from historical events. / 能从历史事件重建一条完整审批链路；<br>`not_executed` / 未执行 |
| AGPT02 | 能识别缺失事件和孤立对象； | Identify missing events and orphan objects. / 能识别缺失事件和孤立对象；<br>`not_executed` / 未执行 |
| AGPT03 | 能计算主要路由、等待、漂移和执行指标； | Compute principal route, waiting, drift and execution measures from valid inputs. / 能计算主要路由、等待、漂移和执行指标；<br>`not_executed` / 未执行 |
| AGPT04 | 能发现提案摘要与回执摘要不一致； | Detect mismatch between proposal and receipt-bound digests. / 能发现提案摘要与回执摘要不一致；<br>`not_executed` / 未执行 |
| AGPT05 | 能发现无有效回执执行； | Detect execution without a valid receipt when historical evidence establishes it. / 能发现无有效回执执行；<br>`not_executed` / 未执行 |
| AGPT06 | 能输出数据质量等级； | Report data quality levels. / 能输出数据质量等级；<br>`not_executed` / 未执行 |
| AGPT07 | 能生成补全包但不修改源记录。 | Generate supplements without modifying original records. / 能生成补全包但不修改源记录。<br>`not_executed` / 未执行 |
| AGPT08 | 能接收执行流程的补全请求； | Accept bounded supplement requests from execution. / 能接收执行流程的补全请求；<br>`not_executed` / 未执行 |
| AGPT09 | 能按允许来源查询数据； | Query only allowed sources. / 能按允许来源查询数据；<br>`not_executed` / 未执行 |
| AGPT10 | 能返回来源、时效、置信度和冲突； | Return source, freshness, confidence and conflicts. / 能返回来源、时效、置信度和冲突；<br>`not_executed` / 未执行 |
| AGPT11 | 执行流程能返回采纳结果； | Receive explicit adoption outcomes from execution. / 执行流程能返回采纳结果；<br>`not_executed` / 未执行 |
| AGPT12 | 语义变化会触发新提案，而不是静默覆盖； | Semantic changes require new proposals instead of silent overwrite. / 语义变化会触发新提案，而不是静默覆盖；<br>`not_executed` / 未执行 |
| AGPT13 | 探针故障不会扩大执行权限； | Probe failure never expands execution authority. / 探针故障不会扩大执行权限；<br>`not_executed` / 未执行 |
| AGPT14 | 控制建议不会被误当作批准决定。 | Control recommendations never become approval decisions. / 控制建议不会被误当作批准决定。<br>`not_executed` / 未执行 |
| AGPT15 | 指标公式有明确分子和分母； | Define explicit numerator and denominator for ratio metrics. / 指标公式有明确分子和分母；<br>`not_executed` / 未执行 |
| AGPT16 | 时间窗口和策略版本可追溯； | Trace window and policy version. / 时间窗口和策略版本可追溯；<br>`not_executed` / 未执行 |
| AGPT17 | 重复事件不造成重复计数； | Duplicate events do not double count. / 重复事件不造成重复计数；<br>`not_executed` / 未执行 |
| AGPT18 | 延迟事件可以回补； | Allow late events to revise versioned windows. / 延迟事件可以回补；<br>`not_executed` / 未执行 |
| AGPT19 | 不完整窗口被标记； | Label incomplete windows. / 不完整窗口被标记；<br>`not_executed` / 未执行 |
| AGPT20 | 补全数据占比可见； | Expose the proportion of supplemented data. / 补全数据占比可见；<br>`not_executed` / 未执行 |
| AGPT21 | 样本不足时不输出过度结论。 | Avoid definitive conclusions from insufficient samples. / 样本不足时不输出过度结论。<br>`not_executed` / 未执行 |
| AGPT22 | 探针服务账户无审批权； | Probe service identity has no approval authority. / 探针服务账户无审批权；<br>`not_executed` / 未执行 |
| AGPT23 | 探针无高风险执行工具权限； | Probe has no high-risk execution-tool authority. / 探针无高风险执行工具权限；<br>`not_executed` / 未执行 |
| AGPT24 | 敏感数据最小化； | Minimize sensitive information. / 敏感数据最小化；<br>`not_executed` / 未执行 |
| AGPT25 | 补全查询范围受限； | Restrict supplementary query scope. / 补全查询范围受限；<br>`not_executed` / 未执行 |
| AGPT26 | 原始记录不可覆盖； | Original records remain immutable. / 原始记录不可覆盖；<br>`not_executed` / 未执行 |
| AGPT27 | 补全包可验证且可撤回； | Supplements are verifiable and can be withdrawn through an audit record. / 补全包可验证且可撤回；<br>`not_executed` / 未执行 |
| AGPT28 | 探针规则变更有版本和审计。 | Probe rule changes have versions and audit history. / 探针规则变更有版本和审计。<br>`not_executed` / 未执行 |
<!-- approval:probe_cases:end -->

## Source coverage / 来源覆盖

Display headings normalize framework spelling to Harness; the source map and snapshots preserve original titles and bytes. / 展示标题统一使用 Harness 的规范拼写；来源映射及副本保留原始标题与字节。

<!-- approval:probe_sections:start -->
| ID | Source / 来源 | Definition / 定义 |
|---|---|---|
| AGPS01 | # 1. 文档目的 | Purpose / 文档目的 |
| AGPS02 | # 2. Harness 框架映射 | Framework mapping / Harness 框架映射 |
| AGPS03 | # 3. 核心定位 | Collect, correlate, diagnose and supplement / 核心定位 |
| AGPS04 | # 4. 运行模式 | Operating modes / 运行模式 |
| AGPS05 | # 5. 权限边界 | Authority boundaries / 权限边界 |
| AGPS06 | # 6. 与执行流程共享的稳定标识 | Shared stable identifiers / 与执行流程共享的稳定标识 |
| AGPS07 | # 7. 标准采集事件 | Event catalog / 标准采集事件 |
| AGPS08 | # 8. 标准事件契约 | Standard event contract / 标准事件契约 |
| AGPS09 | # 9. 探针对象模型 | Probe object model / 探针对象模型 |
| AGPS10 | # 10. 数据质量等级 | Data quality levels / 数据质量等级 |
| AGPS11 | # 11. 核心探针集合 | Twenty-eight core probes / 核心探针集合 |
| AGPS12 | # 12. 核心指标 | Fifty metric definitions / 核心指标 |
| AGPS13 | # 13. 指标计算要求 | Metric calculation requirements / 指标计算要求 |
| AGPS14 | # 14. 告警分级 | Alert severity / 告警分级 |
| AGPS15 | # 15. 数据缺口处理 | Data gaps / 数据缺口处理 |
| AGPS16 | # 16. 补全协议 | Supplement protocol / 补全协议 |
| AGPS17 | # 17. 漂移检测 | Drift detection / 漂移检测 |
| AGPS18 | # 18. 审批疲劳诊断 | Approval fatigue diagnosis / 审批疲劳诊断 |
| AGPS19 | # 19. 场景探针配置 | Scenario probe profiles / 场景探针配置 |
| AGPS20 | # 20. 输出视图 | Output views / 输出视图 |
| AGPS21 | # 21. 反馈协议 | Feedback protocol / 反馈协议 |
| AGPS22 | # 22. 补全交互流程 | Supplement interaction / 补全交互流程 |
| AGPS23 | # 23. 规则示例 | Rule examples / 规则示例 |
| AGPS24 | # 24. 数据保留与隐私 | Retention and privacy / 数据保留与隐私 |
| AGPS25 | # 25. 失败处理 | Failure handling / 失败处理 |
| AGPS26 | # 26. 反模式 | Anti-patterns / 反模式 |
| AGPS27 | # 27. 最小探针集合 | Minimum probe set / 最小探针集合 |
| AGPS28 | # 28. 验收标准 | Acceptance requirements / 验收标准 |
| AGPS29 | # 29. 示例：识别工资清单漂移 | Payroll drift example / 示例：识别工资清单漂移 |
| AGPS30 | # 30. 配置模板 | Configuration example / 配置模板 |
| AGPS31 | # 31. 输出契约 | Probe run output / 输出契约 |
| AGPS32 | # 32. 与执行流程的最终关系 | Relationship to execution / 与执行流程的最终关系 |
| AGPS33 | # 33. 总结 | Summary / 总结 |
<!-- approval:probe_sections:end -->
