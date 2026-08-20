# Generator-Critic / 生成器-批评器 Observability Metrics / 可观测性指标

Cell / 交织点: reflection-chain / 反思 x 链式

Capability / 能力: Reflection / 反思

Mode / 模式: Chain / 链式

Observability revision / 可观测性修订: `1.1.0`

Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850) and the Harness exact-version generation-review probe profile / Harness 精确版本生成评审探针档案

Use this file as the observability source for the Generator-Critic intersection. / 将本文档作为生成器-批评器交织点的可观测性来源。

Design Pattern File / 设计模式文件: [reflection-chain.md](reflection-chain.md)

Shared Reflection Runtime / 共享反思运行时: [Governed Reflection Execution Flow / 受治理反思执行流程](../../reflection-execution-flow.md)

Shared Probe Contract / 共享探针契约: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md), with `PROBE_0016` through `PROBE_0021` plus the Generator-Critic specialization `PROBE_0024` through `PROBE_0027`. / 使用共享工作流可观测性探针中的 `PROBE_0016` 至 `PROBE_0021`，并增加生成评审专用的 `PROBE_0024` 至 `PROBE_0027`。

## Quick Navigation / 快速导航

- [Observation Boundary / 观测边界](#observation-boundary--观测边界)
- [Required Events / 必需事件](#required-events--必需事件)
- [Probe Profile / 探针档案](#probe-profile--探针档案)
- [Registered Metrics / 已注册指标](#registered-metrics--已注册指标)
- [Operational Metrics / 运行指标](#operational-metrics--运行指标)
- [Metric State And Denominators / 指标状态与分母](#metric-state-and-denominators--指标状态与分母)
- [Alerts And Gates / 告警与门禁](#alerts-and-gates--告警与门禁)
- [Rubber-stamp Diagnosis / 橡皮图章诊断](#rubber-stamp-diagnosis--橡皮图章诊断)
- [Replay Checks / 回放检查](#replay-checks--回放检查)
- [Acceptance / 验收](#acceptance--验收)

## Observation Boundary / 观测边界

Observe public, externally auditable records only: contract hashes, actor bindings, artifact identity and lineage, criterion/check results, evidence snapshots, supported findings, retained opinions, score evidence, policy rules, decisions, receipts, release checks, timing, cost, and later outcomes. Never collect raw hidden prompts, private chain-of-thought, or 私密思维过程. / 只观测公开、可外部审计记录：契约哈希、角色绑定、工件身份与谱系、判据/检查结果、证据快照、有据问题、保留意见、评分证据、策略规则、裁决、回执、发布检查、时延、成本及后续结果。不得采集原始隐藏提示、私密思维过程。

The probe is read-only by default. It may report a protected-transition failure to the policy or release gate, but it does not mutate the artifact, convert an opinion into evidence, issue a receipt, or approve release. / 探针默认只读；它可以向策略闸或发布闸报告受保护转换失败，但不得修改工件、把意见转换为证据、签发回执或批准发布。

Use [`probe_registry.json`](../../../runtime/probe_registry.json) as the deployable probe source, [`probe_dependency_matrix.json`](../../../runtime/probe_dependency_matrix.json) as the profile dependency source, and [`metric_registry.json`](../../../runtime/metric_registry.json) as the metric definition source. Call `resolve_reflection_required_probes(generator_critic=True)` before collection. / 使用探针注册表作为可部署探针源、探针依赖矩阵作为档案依赖源、指标注册表作为指标定义源；采集前调用 `resolve_reflection_required_probes(generator_critic=True)`。

## Required Events / 必需事件

| Event / 事件 | Required public capture / 必需公开采集 | Integrity meaning / 完整性含义 |
| --- | --- | --- |
| `artifact_revision_created` | session, contract, artifact ID, revision, digest, record hash, parent binding, producer, shared-reflection assurance, created time, invalidated receipt bindings when superseding. / 会话、契约、工件标识、修订号、摘要、记录哈希、父版本、生产者、共享反思保证、创建时间；替代修订还含失效回执绑定。 | A new version exists, starts unreviewed, and crossed the shared admission or change-authorization boundary. / 新版本存在、从未评审开始且已跨越共享准入或改变授权边界。 |
| `artifact_review_started` | exact artifact binding, review ID, pass number, critic and configuration bindings. / 精确工件绑定、评审标识、批次号、评审器与配置绑定。 | Review did not silently target a stale or different version. / 评审未静默指向陈旧或不同版本。 |
| `artifact_review_recorded` | review binding, all criterion results, evidence snapshots, supported findings, opinions, score, risk coverage, review time. / 评审绑定、全部判据结果、证据快照、有据问题、意见、评分、风险覆盖及评审时间。 | Critique is complete, evidence-bucketed, and still has no release authority. / 评审完整、已证据分桶且仍无发布权限。 |
| `review_decision_recorded` | decision binding, review/artifact bindings, policy gate, decision, triggered rules, gating issues, retained opinions. / 裁决绑定、评审/工件绑定、策略闸、裁决、触发规则、门控问题与保留意见。 | Policy decision is separate and replayable. / 策略裁决分离且可回放。 |
| `review_receipt_issued` | receipt binding, accepted decision, exact artifact, critic/policy/release actors, evidence set, shared-reflection revalidation assurance, issue/expiry times. / 回执绑定、接受裁决、精确工件、评审/策略/发布主体、证据集合、共享反思复验保证及签发/过期时间。 | Receipt belongs to one accepted and independently revalidated version only. / 回执只属于一个已接受且独立复验的版本。 |
| `artifact_release_verified` | current artifact, current receipt, current policy, release-time shared assurance, release time, evidence freshness verdict. / 当前工件、当前回执、当前策略、发布时共享保证、发布时间及证据新鲜度裁定。 | Released version equals the reviewed, revalidated, and receipted version. / 发布版本等于已评审、已复验且已签回执版本。 |
| `generator_critic_stopped` | final state, stop reason, current artifact and last decision/receipt references when present. / 最终状态、停止原因、当前工件及存在时的末次裁决/回执引用。 | Unreleased or escalated work closes explicitly. / 未发布或已升级工作明确闭合。 |

Events must have contiguous positive sequence numbers, unique event IDs and idempotency keys, state continuity, exact contract binding, exact artifact binding, and a valid self-excluding event hash. Missing is not zero, and an absent conditional event must not be fabricated. / 事件必须具有连续正序号、唯一事件标识与幂等键、状态连续性、精确契约绑定、精确工件绑定及有效排除自身字段的事件哈希。缺失不等于零，不得伪造不存在的条件事件。

## Probe Profile / 探针档案

Use the shared governed-reflection core plus the Generator-Critic-specific probes / 使用共享受治理反思核心探针及生成评审专用探针：

| Probe / 探针 | Scope / 范围 | Protected finding / 受保护发现 |
| --- | --- | --- |
| `PROBE_0016` | Reflection admission and `generator_critic` route. / 反思准入与生成评审路由。 | Block automatic review when trigger, baseline, change boundary, or route is invalid. / 触发、基线、改变边界或路由非法时阻断自动评审。 |
| `PROBE_0017` | Frozen baseline and comparable result. / 冻结基线与可比结果。 | Block improvement claims without a stable or independently rebased baseline. / 缺少稳定或独立重建基线时阻断改善声明。 |
| `PROBE_0018` | Independent exact-version revalidation. / 独立精确版本复验。 | Block shared reflection acceptance without mandatory validators. / 缺少必选验证器时阻断共享反思接受。 |
| `PROBE_0019` | Validator and criteria gaming. / 验证器与判据投机。 | Fail closed when checks are weakened, skipped, replaced, or narrowed without approval. / 检查未经批准被削弱、跳过、替换或缩小范围时默认阻断。 |
| `PROBE_0020` | Regression and recovery. / 回归与恢复。 | Blocking regression prevents acceptance or continuation. / 阻断回归阻止接受或继续。 |
| `PROBE_0021` | Reflection and round closure. / 反思与轮次闭环。 | Detect hanging work, budget escape, and missing stop reason. / 发现悬空工作、预算逃逸及停止原因缺失。 |
| `PROBE_0024` | Artifact version and parent lineage. / 工件版本与父版本谱系。 | Block stale review, noncontiguous revision, unchanged digest, or inherited review status. / 阻断陈旧评审、不连续修订、摘要未变或继承评审状态。 |
| `PROBE_0025` | Criteria, evidence buckets, score basis, and risk coverage. / 判据、证据分桶、评分依据及风险覆盖。 | Block missing criteria, untrusted gating evidence, unsupported automatic gates, or uncovered material risk. / 阻断判据缺失、不可信门控证据、无据自动门控或重大风险未覆盖。 |
| `PROBE_0026` | Critic, policy, receipt, and release authority separation. / 评审、策略、回执与发布权限分离。 | Block critic-owned release, missing receipt, mismatched decision, or collapsed authority. / 阻断评审器自有发布、回执缺失、裁决不匹配或权限坍缩。 |
| `PROBE_0027` | Explicit re-review, pass budget, and version escape. / 显式复审、批次预算及版本逃逸。 | Block old receipt reuse, unre-reviewed revision release, pass count above two, or digest mismatch. / 阻断旧回执复用、未复审修订发布、批次超过两次或摘要不匹配。 |

Activate `PROBE_0022` only for causal attribution claims and `PROBE_0023` only for learning promotion. A Generator-Critic receipt is not evidence that a Skill should be promoted. / 只有声明因果归因时启用 `PROBE_0022`，只有学习晋升时启用 `PROBE_0023`；生成评审回执不等于 Skill 应晋升的证据。

## Registered Metrics / 已注册指标

The following metrics are implemented in the machine-readable registry. They remain diagnostic until an accountable owner approves thresholds, minimum samples, drift handling, and promotion evidence; per-instance integrity violations may still block immediately. / 以下指标已在机器可读注册表实现。在责任人批准阈值、最小样本、漂移处理及晋升证据前，它们保持诊断用途；单实例完整性违规仍可立即阻断。

| Metric / 指标 | Formula / 公式 | Interpretation / 解释 |
| --- | --- | --- |
| `generator_critic_review_version_match_rate` | `exact_version_review_records / review_records` | Whether review binds the artifact actually inspected. / 评审是否绑定实际受检工件。 |
| `generator_critic_revision_rereview_compliance_rate` | `rereviewed_revised_artifacts / revised_artifacts_entering_release` | Whether each revised release candidate obtained a new review, decision, and receipt. / 每个修订发布候选是否取得新评审、裁决与回执。 |
| `generator_critic_receipt_coverage_rate` | `accepted_versions_with_valid_receipt / accepted_versions_entering_release` | Whether accepted release candidates carry exact valid receipts. / 接受发布候选是否具有精确有效回执。 |
| `generator_critic_version_escape_rate` | `released_version_escapes / released_reviewed_artifacts` | Whether a different revision or digest escaped release. / 是否有不同修订或摘要逃逸发布。 |
| `generator_critic_evidenced_finding_rate` | `evidenced_findings / reported_findings_and_opinions` | Share of reported critique eligible for evidence-gated policy use. / 报告评审中可用于证据门控策略的比例。 |
| `generator_critic_opinion_retention_rate` | `retained_non_gating_opinions / unsupported_opinions` | Whether non-gating opinions remain visible through decision. / 非门控意见是否保留到裁决。 |
| `generator_critic_risk_evidence_coverage_rate` | `risk_items_with_check_and_evidence / declared_material_risk_items` | Whether every material risk has both a check and trusted evidence. / 每项重大风险是否同时具有检查与可信证据。 |
| `generator_critic_rubber_stamp_escape_rate` | `accepted_artifacts_with_downstream_covered_defect / accepted_artifacts_with_outcome_evidence` | Outcome-backed critic false-release signal for defects inside sealed criteria. / 由后验支撑、针对封存判据内缺陷的评审错误放行信号。 |
| `generator_critic_pass_budget_compliance_rate` | `sessions_within_critique_pass_budget / generator_critic_sessions` | Whether the chain stops or escalates within one to two review passes. / 链是否在一至两次评审内停止或升级。 |

Do not compute a denominator from only successful or complete records. For example, the re-review denominator includes every revised artifact that reached the release boundary, including those blocked for missing review. The version-escape denominator includes confirmed releases only; unknown external release terminal remains unknown and is separately reconciled. / 不得只用成功或完整记录构造分母。例如，复审分母包含所有到达发布边界的修订工件，包括因缺少评审而被阻断者；版本逃逸分母只包含已确认发布，外部发布终态未知应保持未知并单独对账。

## Operational Metrics / 运行指标

In addition to the registered integrity metrics, observe / 除已注册完整性指标外，还应观测：

- 质量指标 / Quality Metrics: `critique_catch_rate` (defects found by critic before release versus defects within sealed criteria found before and after release), revision acceptance improvement over the first draft, per-criterion pass/fail/unknown distribution, and downstream defect severity. / `critique_catch_rate`（发布前评审捕获缺陷对封存判据内发布前后全部缺陷）、修订稿相对初稿的接受改善、逐判据通过/失败/未知分布及下游缺陷严重度。
- 时延指标 / Latency Metrics: generation latency, review latency, policy-decision latency, revision latency, re-review latency, receipt latency, end-to-end generate-to-release time, and escalation delay. / 生成、评审、策略裁决、修订、复审、回执时延，生成到发布端到端时延及升级延迟。
- 成本指标 / Cost Metrics: critic plus revision overhead ratio, cost per evidenced finding, cost per prevented downstream defect, model/tool spend by feedback variant, and human-review load. / 评审加修订开销比、单个有据问题成本、单个避免下游缺陷成本、按反馈变体统计的模型/工具花费及人工评审负载。
- 风险指标 / Risk Metrics: self-critique-only share for correctness-critical artifacts, stale-evidence attempt rate, criterion coverage gaps, authority-collapse attempts, old-receipt replay attempts, and unknown release terminals. / 正确性关键工件仅自评比例、过期证据尝试率、判据覆盖缺口、权限坍缩尝试、旧回执重放尝试及未知发布终态。
- Trace 指标 / Trace Metrics: contract-binding coverage, artifact-lineage completeness, review/decision/receipt binding completeness, event-chain completeness, invalidated-receipt coverage, explicit escalation coverage, and replay anomaly count. / 契约绑定覆盖、工件谱系完整、评审/裁决/回执绑定完整、事件链完整、失效回执覆盖、显式升级覆盖及回放异常数量。

Metrics such as `revision_improvement` or `critique_catch_rate` require trustworthy downstream labels and are not published as zero when outcome linkage is missing. / `revision_improvement` 或 `critique_catch_rate` 等指标需要可信下游标签；结果关联缺失时不得发布为零。

## Metric State And Denominators / 指标状态与分母

Every metric sample must distinguish / 每个指标样本必须区分：

- `computed`: numerator and denominator are complete and eligible. / 分子分母完整且合格；
- `observed_zero`: a complete eligible denominator exists and numerator is truly zero. / 存在完整合格分母且分子确为零；
- `missing`: required events or records were not captured. / 必需事件或记录未采集；
- `unknown`: records exist but truth cannot be determined, such as an external release terminal. / 记录存在但真值无法确定，例如外部发布终态；
- `not_applicable`: the scenario does not require the metric under a named policy. / 场景按命名策略不适用该指标；
- `insufficient_sample`: denominator is valid but below the registered minimum or owner threshold. / 分母有效但低于注册最小样本或责任人阈值。

Preserve field-level provenance for every numerator and denominator input. Direct capture, producer resend, system query, and reproducible deterministic derivation may support audit calculation; statistical inference may support diagnosis only. / 为每个分子与分母输入保留字段级来源。直接采集、生产者补发、系统查询及可复现确定性推导可支撑审计计算；统计推断只能支撑诊断。

## Alerts And Gates / 告警与门禁

Raise a per-instance critical alert and fail the protected transition when / 出现以下情况时产生单实例严重告警并阻断受保护转换：

1. review starts for a non-current revision, digest, or record hash; / 评审针对非当前修订、摘要或记录哈希启动；
2. a new revision is marked reviewed, inherits a decision/receipt, lacks a parent, or repeats the parent digest; / 新修订被标记已评审、继承裁决/回执、缺少父版本或重复父摘要；
3. a sealed criterion is missing or a missing/unknown check is represented as pass; / 封存判据缺失，或缺失/未知检查被表示为通过；
4. a gating issue lacks a sealed criterion, exact check, fresh trusted evidence, or risk reference; / 门控问题缺少封存判据、精确检查、新鲜可信证据或风险引用；
5. an unsupported opinion or unevidenced score changes the decision; / 无据意见或无据评分改变裁决；
6. critic, policy gate, and release gate authority collapses; / 评审器、策略闸与发布闸权限坍缩；
7. automatic revision uses an issue not adopted by policy; / 自动修订使用未被策略采纳的问题；
8. critique pass count exceeds two or work continues after the sealed budget; / 评审批次超过两次或封存预算后继续工作；
9. receipt does not bind the current exact accepted artifact, decision, policy, and evidence set; / 回执未绑定当前精确接受工件、裁决、策略及证据集合；
10. receipt or required evidence is expired at release; / 发布时回执或必需证据已过期；
11. released revision or digest differs from the receipt; / 发布修订或摘要与回执不一致；
12. a protected boundary lacks a valid shared-reflection assurance, or the real publisher can bypass `verify_release()`. / 受保护边界缺少有效共享反思保证，或真实发布器可以绕过 `verify_release()`。
12. private reasoning is captured or a nonexistent business fact is synthesized to satisfy a probe. / 采集私密推理或为满足探针虚构不存在的业务事实。

Aggregate alerts should supplement, not replace, instance gates / 聚合告警只能补充，不能替代实例门禁：

- Alert when acceptance stays above approximately 95% across a representative window and downstream defect evidence exists; do not call a small or easy sample rubber-stamping by approval rate alone. / 代表性窗口内接受率持续高于约 95% 且存在下游缺陷证据时告警；不得仅凭小样本或简单样本的高通过率判定橡皮图章。
- Alert when a sealed criterion never fires and has no verified pass evidence across a meaningful window; it may be dead weight or incorrectly instrumented. / 封存判据在有效窗口内从不触发且没有可验证通过证据时告警；它可能是死重或埋点错误。
- Block correctness-critical output reviewed only by self-critique when an authoritative tool-grounded check was available. / 权威工具接地检查可用时，阻断仅经自评的正确性关键产出。
- Alert when pass budget compliance falls below the owner threshold; route those cases to `reflection-loop` or human review. / 批次预算合规率低于责任人阈值时告警，并路由到 `reflection-loop` 或人工复核。

## Rubber-stamp Diagnosis / 橡皮图章诊断

High approval alone is not proof of rubber-stamping. Diagnose with a joint signal / 高通过率本身不证明橡皮图章，应使用联合信号诊断：

```text
representative sample
+ complete criterion coverage
+ downstream outcome linkage
+ acceptance concentration
+ near-zero evidenced findings
+ criteria that never discriminate
+ covered downstream defects after acceptance
= rubber-stamp suspicion
```

Compare by scenario, risk, artifact type, feedback variant, critic version, and criterion set. A formatting critic on already normalized templates may correctly approve nearly all cases; a correctness critic that approves nearly all cases while downstream factual defects recur is suspicious. / 按场景、风险、工件类型、反馈变体、评审器版本及判据集合比较。面对已规范化模板的格式评审器可能合理地几乎全部通过；正确性评审器几乎全部通过但下游事实缺陷反复出现则值得怀疑。

Use later authoritative evidence to populate `generator_critic_rubber_stamp_escape_rate`. Do not backfill a defect that was outside the sealed criteria as a critic failure; record it as a criteria-gap or policy-revision candidate. / 使用后续权威证据填充 `generator_critic_rubber_stamp_escape_rate`。不得把封存判据之外的缺陷回填为评审失败；应记录为判据缺口或策略修订候选。

## Replay Checks / 回放检查

An audit replay should / 审计回放应：

1. validate every Schema and self-hash; / 校验全部 Schema 与自哈希；
2. verify contiguous events, state continuity, unique IDs, and idempotency keys; / 校验连续事件、状态连续、唯一标识及幂等键；
3. reconstruct the artifact parent chain and prove every digest transition is real; / 重建工件父版本链并证明每次摘要变化真实；
4. prove each review targeted the then-current exact artifact; / 证明每份评审针对当时当前精确工件；
5. re-evaluate evidence freshness and trusted-source eligibility at review time; / 按评审时间重新评价证据新鲜度与可信来源资格；
6. prove criteria results cover the sealed set exactly once; / 证明判据结果恰好覆盖封存集合一次；
7. prove every gating issue is supported and every unsupported opinion is retained; / 证明每个门控问题有据且每个无据意见被保留；
8. recompute the policy decision from the contract and review; / 从契约与评审重算策略裁决；
9. prove every revised or superseding artifact returned to unreviewed and obtained explicit re-review before release; / 证明每个修订或替代工件返回未评审并在发布前显式复审；
10. prove the receipt binds the current accepted artifact and was fresh under the current policy at release; / 证明回执绑定当前接受工件，且发布时在当前策略下仍新鲜；
11. preserve unknown external terminal states rather than infer success; / 保持外部终态未知，不推断成功；
12. emit anomalies without rewriting history. / 在不改写历史的情况下输出异常。

The in-memory reference session can validate its event stream but is not a crash-safe audit store. Production replay requires immutable durable records and a defined retention, migration, backup, restore, and tamper-evidence policy. / 内存参考会话可校验自身事件流，但不是崩溃安全审计存储。生产回放需要不可变持久记录，以及明确的保留、迁移、备份、恢复与防篡改策略。

## Observability Metrics / 可观测性指标

- 质量指标 / Quality Metrics: Exact-version match, re-review compliance, receipt coverage, evidenced finding rate, risk-evidence coverage, critic catch rate, revision improvement, and outcome-backed rubber-stamp escape. / 精确版本匹配、复审合规、回执覆盖、有据问题、风险证据覆盖、评审捕获、修订改善及后验支撑的橡皮图章逃逸。
- 时延指标 / Latency Metrics: Generation, review, decision, revision, re-review, receipt, release, and escalation latency. / 生成、评审、裁决、修订、复审、回执、发布及升级时延。
- 成本指标 / Cost Metrics: Review overhead, cost per evidenced finding, cost per prevented defect, per-variant model/tool spend, and human review effort. / 评审开销、单个有据问题成本、单个避免缺陷成本、逐变体模型/工具花费及人工评审投入。
- 风险指标 / Risk Metrics: Version escape, stale evidence, unsupported gating, authority collapse, self-critique-only critical review, old-receipt replay, and unknown release terminal. / 版本逃逸、证据过期、无据门控、权限坍缩、关键任务仅自评、旧回执重放及发布终态未知。
- Trace 指标 / Trace Metrics: Contract, shared-reflection assurance, artifact lineage, review, decision, receipt, invalidation, release, stop, and event-chain binding completeness. / 契约、共享反思保证、工件谱系、评审、裁决、回执、失效、发布、停止及事件链绑定完整度。

## Acceptance / 验收

- [ ] `resolve_reflection_required_probes(generator_critic=True)` returns the shared core plus `PROBE_0024` through `PROBE_0027`. / 探针解析返回共享核心及 `PROBE_0024` 至 `PROBE_0027`。
- [ ] All required events are captured with exact artifact and contract bindings. / 全部必需事件均采集精确工件与契约绑定。
- [ ] Artifact lineage and invalidated receipts can be replayed without reading mutable business state. / 无需读取可变业务状态即可回放工件谱系与失效回执。
- [ ] Supported findings, unsupported opinions, score evidence, and risk coverage remain separate. / 有据问题、无据意见、评分证据及风险覆盖保持分离。
- [ ] Policy decisions are reproducible from registered records. / 策略裁决可从注册记录复现。
- [ ] Revised artifacts appear in re-review denominators even when blocked before acceptance. / 修订工件即使接受前被阻断也进入复审分母。
- [ ] Missing, unknown, not applicable, observed zero, computed, and insufficient sample remain distinct. / 缺失、未知、不适用、观测零、已计算及样本不足保持区分。
- [ ] Instance integrity failures block immediately; aggregate metrics do not weaken them. / 实例完整性失败立即阻断，聚合指标不得削弱它们。
- [ ] Rubber-stamp claims use representative samples and downstream outcome evidence. / 橡皮图章判断使用代表性样本与下游结果证据。
- [ ] No private reasoning or fabricated completion data is collected. / 不采集私密推理或虚构补全数据。
- [ ] Production audit claims name the durable store and recovery boundary. / 生产审计声明明确持久存储与恢复边界。
