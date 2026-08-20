# Generator-Critic / 生成器-批评器

Cell / 交织点: reflection-chain / 反思 x 链式

Capability / 能力: Reflection / 反思

Mode / 模式: Chain / 链式

Design revision / 设计修订: `1.1.0`

Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850) and the Harness exact-version generation-review profile / Harness 精确版本生成评审档案

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

Runtime Contract / 运行时契约: apply this cell through [Governed Reflection Execution Flow / 受治理反思执行流程](../../reflection-execution-flow.md), then use the Generator-Critic Schemas and `GeneratorCriticSession` below for exact-version review, evidence bucketing, policy decision, revision, receipt, and release verification. Build the mandatory guard with `build_shared_reflection_guard` and map applied artifacts with `reflection_subject_binding_for_artifact`; the adapter replays the complete shared contract, event stream, and round observation before deriving an auditable assurance binding. Missing, exceptional, invalid, stale, or artifact-mismatched assurance fails closed. The shared reflection protocol owns admission, frozen baseline, change authorization, independent revalidation, regression protection, attribution, learning, and bounded stopping; this cell owns the short generation-review chain. / 先通过共享受治理反思执行流程应用本单元，再使用下述生成评审 Schema 与 `GeneratorCriticSession` 管理精确版本评审、证据分桶、策略裁决、修订、回执及发布校验。使用 `build_shared_reflection_guard` 构建必选闸，并以 `reflection_subject_binding_for_artifact` 映射已应用工件；适配器在派生可审计保证绑定前重放完整共享契约、事件流及轮次观察。保证缺失、异常、无效、陈旧或工件不匹配时默认阻断。共享反思协议负责准入、冻结基线、改变授权、独立复验、回归保护、归因、学习与有界停止；本单元负责短链生成评审。

## Quick Navigation / 快速导航

- [Design Pattern / 设计模式](#design-pattern--设计模式)
- [Hard Invariants / 硬不变量](#hard-invariants--硬不变量)
- [Normative Artifacts / 规范制品](#normative-artifacts--规范制品)
- [Roles And Authority / 角色与权限](#roles-and-authority--角色与权限)
- [Contract Compilation / 契约编译](#contract-compilation--契约编译)
- [State Machine / 状态机](#state-machine--状态机)
- [Execution Workflow / 执行流程](#execution-workflow--执行流程)
- [Evidence Gate / 证据闸](#evidence-gate--证据闸)
- [Policy Decision / 策略裁决](#policy-decision--策略裁决)
- [Revision And Explicit Re-review / 修订与显式复审](#revision-and-explicit-re-review--修订与显式复审)
- [Receipt And Release / 回执与发布](#receipt-and-release--回执与发布)
- [Feedback Variant Selection / 反馈变体选择](#feedback-variant-selection--反馈变体选择)
- [Composition With Governed Reflection / 与受治理反思组合](#composition-with-governed-reflection--与受治理反思组合)
- [Failure And Recovery / 失败与恢复](#failure-and-recovery--失败与恢复)
- [Pattern Template / 模式模板](#pattern-template--模式模板)
- [Acceptance / 验收](#acceptance--验收)

## Design Pattern / 设计模式

Generator-Critic runs `generate → review → policy decision → optional revision → explicit re-review` as a short, bounded chain. A generator creates one immutable artifact revision; a distinct critic evaluates that exact revision against criteria sealed before generation; a policy gate converts supported findings into a decision; a reviser may create one new unreviewed revision; and a release gate accepts only a receipt that binds the exact released digest. / 生成器-批评器以短且有界的链运行“生成 → 评审 → 策略裁决 → 可选修订 → 显式复审”。生成器创建一个不可变工件修订；独立评审器按生成前封存的判据检查该精确修订；策略闸把有据问题转换为裁决；修订器可创建一个新的未评审修订；发布闸只接受绑定实际发布摘要的精确回执。

This is a Chain pattern because the expected production path converges in one or two critique passes. Open-ended repair, repeated tool use, or convergence search belongs to Self-Heal Loop at `reflection-loop`; multi-critic comparison belongs to a separately justified parallel extension rather than being hidden inside this cell. / 本模式属于链式，因为生产路径预期在一至两次评审中收敛。开放式修复、重复工具调用或收敛搜索属于 `reflection-loop` 的自愈循环；多评审器比较只有在独立论证后才能使用并行扩展，不得隐藏在本单元中。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reflection / 反思 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; 矩阵列名模式 / Matrix-listed pattern; the article places Generator-Critic at Reflection / 反思 x Chain / 链式. / 论文将生成器-批评器落在反思 x 链式交织点。
- 问题 / Problem: A single generator can produce plausible output that is unchecked, stale, weakly evidenced, or reviewed against the wrong version. / 单一生成器可能产出看似合理但未经检查、证据过期、支撑不足或评错版本的结果。
- 架构方案 / Architectural Solution: Separate generation, critique, policy decision, revision, and release; bind every stage to immutable versions and evidence. / 分离生成、评审、策略裁决、修订与发布，并把每个阶段绑定到不可变版本和证据。
- 工程权衡 / Engineering Trade-offs: The pattern increases quality and auditability but adds latency, cost, and critic blind spots. Tool-grounded or cross-model review is preferred for correctness-critical output. / 本模式提高质量与可审计性，但增加时延、成本及评审盲点；正确性关键产出优先使用工具接地或跨模型评审。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when one immutable output should pass through a short sequential review and at most one normal revision before release. / 当一个不可变输出应在发布前经过短链顺序评审及正常最多一次修订时使用。

## Hard Invariants / 硬不变量

1. Seal critique criteria, risk coverage, actor bindings, decision policy, pass budget, and release policy before generation. / 在生成前封存评审判据、风险覆盖、角色绑定、裁决策略、批次预算及发布策略。
2. Identify every artifact by `artifact_id + revision + artifact_digest + artifact_record_hash`; a filename or task ID is not a version binding. / 每个工件以“工件标识 + 修订号 + 内容摘要 + 工件记录哈希”识别；文件名或任务号不能替代版本绑定。
3. Store revisions append-only with a parent binding; never overwrite historical content or its decision. / 以追加方式保存修订并绑定父版本；不得覆盖历史内容或其裁决。
4. Mark every new or superseding revision `unreviewed`; no review, decision, or receipt is inherited. / 每个新修订或替代修订都标记为 `unreviewed`；不得继承评审、裁决或回执。
5. Let the critic report findings only. The critic cannot decide release, modify the artifact, authorize revision, or issue a receipt. / 评审器只能报告发现；不得决定发布、修改工件、授权修订或签发回执。
6. Separate supported findings from unsupported opinions. Preserve both; only supported findings may enter automatic policy decision. / 分离有据问题与无据意见并同时保留；只有有据问题可进入自动策略裁决。
7. Require each supported finding to bind a sealed criterion, exact check ID, fresh auditable evidence, and applicable risk references. / 每个有据问题必须绑定封存判据、精确检查标识、新鲜可审计证据及适用风险引用。
8. Treat statistical inference and diagnostic-only evidence as alert input, never as automatic release authority. / 统计推断与仅诊断证据只能用于告警，不得成为自动发布依据。
9. Derive policy decisions deterministically from the sealed policy; never accept a critic-supplied “pass” as the state transition. / 从封存策略确定性派生裁决；不得把评审器自报“通过”直接作为状态转换。
10. Allow automatic revision to consume only issue IDs adopted by the policy decision. / 自动修订只能消费策略裁决采纳的问题标识。
11. Cap the chain at one or two review passes. On unresolved blocking issues at the cap, escalate or reject according to the sealed policy. / 链式评审限制为一至两次；到达上限仍有阻断问题时，按封存策略升级或拒绝。
12. Release only when the receipt, decision, review, artifact revision, digest, policy, and evidence freshness all match. / 只有回执、裁决、评审、工件修订、摘要、策略及证据新鲜度全部匹配时才允许发布。
13. Record public claims, checks, evidence bindings, and decisions only; never collect private chain-of-thought or 私密思维过程. / 只记录公开声明、检查、证据绑定与裁决；不得采集私密思维过程。

## Normative Artifacts / 规范制品

Treat these files as the executable source of truth / 将以下文件视为可执行事实源：

- [`generator-critic-contract.schema.json`](../../../schemas/generator-critic-contract.schema.json): artifact policy, role separation, predeclared criteria, feedback variant, decision rules, pass budget, and release policy. / 工件策略、角色分权、预声明判据、反馈变体、裁决规则、批次预算及发布策略。
- [`generator-critic-artifact.schema.json`](../../../schemas/generator-critic-artifact.schema.json): immutable revision, content digest, parent binding, producer, and forced `unreviewed` state. / 不可变修订、内容摘要、父版本绑定、生产者及强制未评审状态。
- [`generator-critic-review.schema.json`](../../../schemas/generator-critic-review.schema.json): exact-version criteria results, evidence snapshots, supported findings, unsupported opinions, score evidence, and risk coverage. / 精确版本判据结果、证据快照、有据问题、无据意见、评分依据及风险覆盖。
- [`generator-critic-decision.schema.json`](../../../schemas/generator-critic-decision.schema.json): policy-owned decision, triggered rules, gating issue references, and retained opinion references. / 策略所有的裁决、触发规则、门控问题引用及保留意见引用。
- [`generator-critic-receipt.schema.json`](../../../schemas/generator-critic-receipt.schema.json): accepted exact version, review, decision, actors, evidence snapshots, and expiry. / 已接受精确版本、评审、裁决、角色、证据快照及过期时间。
- [`generator-critic-event.schema.json`](../../../schemas/generator-critic-event.schema.json): contiguous lifecycle events for artifact, review, decision, revision, receipt, release, and stop. / 工件、评审、裁决、修订、回执、发布与停止的连续生命周期事件。
- [`generator_critic.py`](../../../runtime/generator_critic.py): producer-side hashing, semantic guards, `build_shared_reflection_guard`, exact artifact-to-subject mapping, deterministic decisions, revision lineage, receipt issuance, release verification, and event replay checks. / 生产端哈希、语义闸门、共享反思闸构造器、精确工件到对象映射、确定性裁决、修订谱系、回执签发、发布校验及事件回放检查。
- [`reflection_runtime.py`](../../../runtime/reflection_runtime.py): shared reflection admission, baseline, change authorization, independent revalidation, rollback, attribution, and learning lifecycle. / 共享反思准入、基线、改变授权、独立复验、回滚、归因及学习生命周期。

JSON Schema validates local shape. `generator_critic.py` additionally validates cross-record binding, actor separation, trusted evidence subsets, exact criterion coverage, deterministic decisions, contiguous lineage, shared-reflection assurance bindings, receipt freshness, and release-version equality. Use the supplied guard builder rather than fabricating a binding callback; it calls the shared validators over the complete contract, event stream, and observation and checks accepted revalidation against the exact mapped artifact. A Schema pass alone is not proof that the workflow is safe. / JSON Schema 校验局部结构；`generator_critic.py` 还校验跨记录绑定、角色分权、可信证据子集、完整判据覆盖、确定性裁决、连续谱系、共享反思保证绑定、回执新鲜度及发布版本相等性。应使用随附闸构造器，不得伪造绑定回调；它对完整共享契约、事件流与观察包调用共享校验器，并以精确映射工件核对已接受复验。仅通过 Schema 不等于工作流安全。

## Roles And Authority / 角色与权限

| Role / 角色 | May / 可以 | Must not / 禁止 |
| --- | --- | --- |
| Generator / 生成器 | Produce the initial content and content reference. / 产出初始内容与内容引用。 | Review itself as an independent actor, decide, or release. / 以独立主体名义评审自身、裁决或发布。 |
| Critic / 评审器 | Evaluate the exact revision against sealed criteria; produce both evidence-backed findings and retained opinions. / 按封存判据检查精确修订；产出有据问题与保留意见。 | Mutate content, authorize revision, convert opinions into gates, or issue release. / 修改内容、授权修订、把意见转成门控或签发发布。 |
| Policy gate / 策略闸 | Apply sealed deterministic rules to one review. / 对单份评审应用封存确定性规则。 | Rewrite the review or artifact. / 改写评审或工件。 |
| Reviser / 修订器 | Create a new revision from policy-adopted issues. / 基于策略采纳问题创建新修订。 | Reuse the old decision or receipt. / 复用旧裁决或回执。 |
| Release gate / 发布闸 | Issue and verify the exact-version receipt after acceptance. / 在接受后签发并校验精确版本回执。 | Release a different digest, stale evidence, or changed policy. / 发布不同摘要、过期证据或策略已变化的版本。 |
| Probe / 探针 | Observe, reconstruct, alert, and request missing data. / 观测、重建、告警并请求缺失数据。 | Invent facts or directly mutate business state. / 虚构事实或直接修改业务状态。 |

The critic, policy gate, and release gate must use distinct versioned bindings. For `cross_model`, `tool_grounded`, or `human_review`, the generator and critic must also be distinct. `self_critique` may share a model identity only when it binds a separate critic configuration and remains limited to low-risk style, format, or completeness checks. / 评审器、策略闸与发布闸必须使用不同版本化绑定。`cross_model`、`tool_grounded` 或 `human_review` 还要求生成器与评审器分离。`self_critique` 仅可在绑定独立评审配置且任务限于低风险风格、格式或完整性检查时共享模型身份。

## Contract Compilation / 契约编译

Before content generation / 内容生成前：

1. Bind the shared governed-reflection contract and run identity. / 绑定共享受治理反思契约与运行身份。
2. Declare one stable artifact ID, artifact type, initial revision, append-only rule, and revision budget. / 声明稳定工件标识、工件类型、初始修订号、追加写规则及修订预算。
3. Bind generator, critic, critic configuration, reviser, policy gate, and release gate. / 绑定生成器、评审器、评审配置、修订器、策略闸及发布闸。
4. Declare every criterion with a stable criterion ID, check ID, default severity, evidence requirement, risk references, and optional validator binding. / 为每项判据声明稳定判据标识、检查标识、默认严重级别、证据要求、风险引用及可选验证器绑定。
5. Select feedback variant and one-to-two-pass budget. / 选择反馈变体及一至两次评审批次预算。
6. Seal deterministic actions for blocking findings, warnings, unknown checks, evidenced low scores, and budget exhaustion. / 封存阻断问题、警告、未知检查、有据低分及预算耗尽的确定性动作。
7. Seal receipt, exact-digest, current-policy, evidence-freshness, and expiry rules. / 封存回执、精确摘要、当前策略、证据新鲜度及过期规则。
8. Call `build_generator_critic_contract()` and persist the returned `contract_hash`; do not execute from a caller-rehashed contract that failed semantic validation. / 调用 `build_generator_critic_contract()` 并持久化返回的 `contract_hash`；不得从调用方重算但未通过语义校验的契约执行。

Criteria that do not exist before generation are post-hoc preferences, not sealed review criteria. They may be preserved as opinions or require an authorized contract revision; they cannot silently block the current artifact. / 生成前不存在的判据属于事后偏好，不是封存评审判据；可作为意见保留或要求经授权修订契约，但不得静默阻断当前工件。

## State Machine / 状态机

```text
initialized
  -> artifact_unreviewed
  -> reviewing
  -> reviewed
  -> accepted
       -> receipt issued (state remains accepted)
       -> released
       -> artifact_unreviewed       # superseding content invalidates old acceptance
  -> needs_revision
       -> artifact_unreviewed       # new revision, old decision remains historical
  -> waiting_evidence
       -> reviewing                 # explicit same-version re-review
  -> human_required | rejected

any nonterminal unreleased state
  -> stopped
```

`reviewed` is never a release state. `accepted` without a receipt is never a release state. `receipt issued` does not mutate the artifact. A superseding content change moves back to `artifact_unreviewed` and records every invalidated receipt binding. / `reviewed` 绝不是发布状态；缺少回执的 `accepted` 也不是发布状态；签发回执不会修改工件。任何替代内容变更都会回到 `artifact_unreviewed`，并记录全部失效回执绑定。

## Execution Workflow / 执行流程

### 1. Create The Initial Artifact / 创建初始工件

Call `create_initial_artifact(content=..., content_ref=..., producer_binding=..., created_at=...)`. The runtime calculates `artifact_digest` from canonical content, creates an immutable record, forces `review_status: unreviewed`, and emits `artifact_revision_created`. The runtime stores the digest and reference, not private reasoning. / 调用 `create_initial_artifact(...)`。运行时从规范内容计算 `artifact_digest`，创建不可变记录，强制 `review_status: unreviewed`，并发送 `artifact_revision_created`；运行时保存摘要与引用，不保存私密推理。

### 2. Start Exact-Version Review / 开始精确版本评审

Call `start_review()` with the full current `artifact_binding`. A stale revision, changed digest, old record hash, duplicate review ID, illegal state, or exhausted pass budget fails closed before critique is accepted. / 使用完整当前 `artifact_binding` 调用 `start_review()`；陈旧修订、摘要变化、旧记录哈希、重复评审标识、非法状态或批次预算耗尽都会在接收评审前默认阻断。

### 3. Record The Critic Report / 记录评审报告

Call `record_review()` with / 调用 `record_review()` 并提供：

- one result for every sealed criterion; / 每个封存判据恰好一条结果；
- evidence snapshots with source kind, authority, acquisition time, and expiry; / 带来源类型、权威等级、获取时间与过期时间的证据快照；
- supported findings with criterion, check, evidence, summary, severity, location, and risk references; / 带判据、检查、证据、摘要、严重级别、定位和风险引用的有据问题；
- unsupported opinions with explicit reason and `preserved_non_gating: true`; / 带明确原因及 `preserved_non_gating: true` 的无据意见；
- optional score plus separate score evidence and rationale; / 可选评分及独立评分证据与依据；
- the complete material-risk set checked by this review. / 本评审检查的完整重大风险集合。

The method emits `artifact_review_recorded` and moves only to `reviewed`. It has no parameter for a critic-owned pass/fail verdict. / 该方法发送 `artifact_review_recorded`，状态只进入 `reviewed`；它不接受评审器自有的通过/失败裁决参数。

### 4. Derive The Policy Decision / 派生策略裁决

Call `decide()`. The runtime recomputes the result from the sealed policy and emits `review_decision_recorded`. The caller cannot supply or override the decision. / 调用 `decide()`；运行时依据封存策略重算结果并发送 `review_decision_recorded`，调用方不能提供或覆盖裁决。

### 5. Revise Or Enter Shared Revalidation / 修订或进入共享复验

- On `needs_revision`, first use the exact decision binding as the shared change proposal and obtain shared authorization; then call `create_revision()` with only policy-adopted issue IDs. The output is a new contiguous, digest-changed, parent-bound, unreviewed artifact that must be explicitly re-reviewed. / 裁决为 `needs_revision` 时，先以精确裁决绑定作为共享改变提案并取得共享授权；再仅使用策略采纳问题标识调用 `create_revision()`。输出是连续递增、摘要已变化、绑定父版本且未评审的新工件，必须显式复审。
- On `wait_for_evidence`, collect a named missing snapshot, then explicitly call `start_review()` for the same exact version. / 裁决为 `wait_for_evidence` 时，采集命名缺失快照，再对同一精确版本显式调用 `start_review()`。
- On `accepted`, make sure the exact accepted artifact is covered by a shared change proposal and authorization, record it with `reflection_subject_binding_for_artifact()`, run mandatory and regression revalidation, and close an accepted shared round observation. Do not issue the receipt before this step passes. / 裁决为 `accepted` 时，确保精确接受工件已被共享改变提案与授权覆盖，使用 `reflection_subject_binding_for_artifact()` 记录该对象，运行必选与回归复验，并闭合已接受共享轮次观察。在此步骤通过前不得签发回执。
- On `human_required` or `rejected`, stop automatic work and preserve the full history. / 裁决为 `human_required` 或 `rejected` 时，停止自动工作并保留完整历史。

### 6. Issue The Exact Receipt / 签发精确回执

After shared independent revalidation and round closure pass for the exact accepted artifact, obtain the live release-gate binding and call `issue_receipt()`. The runtime replays shared history through `build_shared_reflection_guard`, binds its assurance into the receipt, and refuses receipt creation if acceptance, artifact mapping, validators, or closure do not match. / 只有精确接受工件的共享独立复验与轮次闭环通过后，才取得实时发布闸绑定并调用 `issue_receipt()`。运行时通过 `build_shared_reflection_guard` 重放共享历史，把保证绑定写入回执；接受状态、工件映射、验证器或闭环不匹配时拒绝创建回执。

### 7. Verify Release / 校验发布

Call `verify_release()` with the current exact artifact binding, the session-issued current receipt, the current governance-policy binding, and release time. The gate checks receipt integrity, artifact equality, policy equality, receipt expiry, every required evidence expiry, and a fresh shared-reflection assurance before emitting `artifact_release_verified`. Wire the actual external publish side effect behind this call; otherwise an operator can bypass the reference coordinator. / 使用当前精确工件绑定、会话签发的当前回执、当前治理策略绑定及发布时间调用 `verify_release()`；门禁在发送 `artifact_release_verified` 前校验回执完整性、工件相等性、策略相等性、回执过期时间、全部必需证据过期时间及新鲜共享反思保证。实际外部发布副作用必须置于此调用之后，否则操作方可绕过参考协调器。

## Evidence Gate / 证据闸

### Supported Finding / 有据问题

```yaml
issue_id: issue-accuracy-1
severity: blocking
description: "Claim conflicts with the authoritative result. / 论断与权威结果冲突。"
location: section-2
criterion_id: criterion-accuracy
check_id: check-accuracy
evidence_bindings: [EVIDENCE_BINDING]
evidence_summary: "Expected A, observed B. / 预期 A，实际 B。"
risk_refs: [risk-factual-error]
```

A supported finding is eligible for policy gating only when its evidence binding resolves to a fresh snapshot whose source is direct capture, producer resend, system query, or reproducible deterministic derivation, and whose authority is not `diagnostic_only`. / 有据问题只有在其证据绑定可解析为新鲜快照，且来源属于直接采集、生产者补发、系统查询或可复现确定性推导，权威等级不为 `diagnostic_only` 时，才可参与策略门控。

### Unsupported Opinion / 无据意见

```yaml
opinion_id: opinion-tone-1
description: "The tone feels flat. / 语气似乎平淡。"
proposed_severity: warning
criterion_id: criterion-style
reason: unverifiable
evidence_bindings: []
preserved_non_gating: true
```

Unsupported opinions remain visible for human review, later evidence acquisition, critic calibration, and audit. They cannot silently enter `gating_issue_refs`, drive an automatic revision, or lower the release state. / 无据意见继续对人工复核、后续取证、评审器校准及审计可见；不得静默进入 `gating_issue_refs`、驱动自动修订或降低发布状态。

### Score Evidence / 评分依据

A score may be recorded without evidence for diagnostic comparison, but it becomes non-gating. A below-threshold score triggers policy only when `score.evidence_bindings` resolves to trusted fresh snapshots. A rationale is always required when a numeric score exists. / 评分可在无证据时用于诊断比较，但不参与门控；低于阈值的评分只有在 `score.evidence_bindings` 可解析为可信新鲜快照时才触发策略；任何数值评分都必须有依据说明。

### Risk Coverage / 风险覆盖

Evidence truth and risk coverage are different. A valid screenshot of a title does not cover factual correctness; a successful format check does not cover unsafe advice. The review must cover every material risk declared by the sealed criteria, or fail as incomplete rather than report a cosmetic pass. / 证据真实与风险覆盖不是一回事。真实标题截图不能覆盖事实正确性，格式检查通过也不能覆盖不安全建议；评审必须覆盖封存判据声明的全部重大风险，否则应以不完整失败，而不是给出表面通过。

## Policy Decision / 策略裁决

The default deterministic order is / 默认确定性顺序如下：

| Condition / 条件 | Decision / 裁决 | Rule / 规则 |
| --- | --- | --- |
| One or more supported findings use a configured blocking severity. / 存在配置为阻断严重度的有据问题。 | `needs_revision`; at pass budget, `human_required` or `reject`. / 需要修订；到达批次上限时转人工或拒绝。 | `POLICY_SUPPORTED_BLOCKING`, optional `POLICY_REVIEW_BUDGET_EXHAUSTED` |
| No blocking finding, but a sealed criterion is `unknown`. / 无阻断问题但封存判据为未知。 | `wait_for_evidence` or `human_required`. / 等待证据或转人工。 | `POLICY_UNKNOWN_CRITERION` |
| Supported warning exists. / 存在有据警告。 | Sealed `warning_action`. / 封存的警告动作。 | `POLICY_SUPPORTED_WARNING` |
| Evidenced score is below minimum. / 有据评分低于阈值。 | Sealed score action. / 封存的低分动作。 | `POLICY_EVIDENCED_SCORE_BELOW_MINIMUM` |
| Unevidenced score is below minimum. / 无据评分低于阈值。 | No state change from the score. / 评分不改变状态。 | `POLICY_UNEVIDENCED_SCORE_NON_GATING` |
| No gating finding, unknown, or evidenced low score. / 无门控问题、未知或有据低分。 | `accept`. / 接受。 | `POLICY_NO_GATING_FINDING` |

Policy evaluation retains every unsupported opinion reference in the decision. This proves that the item was considered but did not gain automatic authority. / 策略裁决保留全部无据意见引用，以证明意见已被考虑但未获得自动权限。

## Revision And Explicit Re-review / 修订与显式复审

The decision for revision `n` belongs only to revision `n`. When `create_revision()` produces revision `n+1` / 修订 `n` 的裁决只属于修订 `n`。当 `create_revision()` 产出修订 `n+1` 时：

1. calculate a new content digest; / 计算新的内容摘要；
2. bind the full parent artifact identity; / 绑定完整父工件身份；
3. preserve the old review and decision unchanged; / 保持旧评审与裁决不变；
4. set `review_status: unreviewed`; / 设置 `review_status: unreviewed`；
5. require a new review ID, review artifact, policy decision, and receipt; / 要求新的评审标识、评审制品、策略裁决及回执；
6. count the new review against the one-to-two-pass chain budget. / 将新评审计入一至两次链式预算。

`create_superseding_revision()` covers an accepted artifact edited before release. Supply the exact shared `change_proposal_binding`; the guard requires the current unconsumed authorization for that proposal. The method records invalidated receipt bindings and returns the session to `artifact_unreviewed`; this prevents “small post-review edits” from escaping review. / `create_superseding_revision()` 处理接受后、发布前被编辑的工件。必须提供精确共享 `change_proposal_binding`，闸要求该提案具有当前未消费授权。该方法记录失效回执绑定并把会话返回 `artifact_unreviewed`，防止“评审后小改动”逃逸评审。

If a task needs more than two passes, repeated tool-driven repair, or dynamic hypothesis search, close this chain and route to Self-Heal Loop or accountable human review. Do not increase the pass cap in place. / 若任务需要超过两次评审、重复工具驱动修复或动态假设搜索，应关闭本链并路由到自愈循环或可问责人工复核；不得原地提高批次上限。

## Receipt And Release / 回执与发布

A valid receipt binds / 有效回执必须绑定：

- Generator-Critic contract ID, version, and hash; / 生成评审契约标识、版本与哈希；
- exact review ID and review hash; / 精确评审标识与评审哈希；
- exact policy decision ID and decision hash; / 精确策略裁决标识与裁决哈希；
- artifact ID, revision, content digest, and record hash; / 工件标识、修订号、内容摘要及记录哈希；
- critic, policy gate, and release gate; / 评审器、策略闸及发布闸；
- all evidence snapshot bindings; / 全部证据快照绑定；
- the shared-reflection assurance proving independent revalidation and round closure; / 证明独立复验与轮次闭环的共享反思保证；
- issue and expiry times. / 签发与过期时间。

Release fails closed when the artifact changed after receipt issuance, a different receipt is supplied, the governance policy changed, the receipt expired, required evidence expired, or the decision was not `accept`. A successful model or tool response never substitutes for the receipt. / 工件在回执签发后变化、传入不同回执、治理策略变化、回执过期、必需证据过期或裁决不是 `accept` 时，发布默认阻断。模型或工具调用成功绝不能替代回执。

## Feedback Variant Selection / 反馈变体选择

| Variant / 变体 | Cost / 成本 | Reliability / 可靠性 | Use When / 适用 |
| --- | --- | --- | --- |
| Self-critique / 自评 | Lowest / 最低 | Weakest; shares generator blind spots. / 最弱；共享生成器盲点。 | Low-risk style, formatting, and completeness checks with a separate critic configuration. / 使用独立评审配置的低风险风格、格式与完整性检查。 |
| Cross-model / 跨模型 | Medium / 中 | Better independent priors, but still judgement-based. / 先验更独立，但仍依赖判断。 | Review has explicit criteria but no executable oracle. / 评审有明确判据但无可执行判定器。 |
| Tool-grounded / 工具接地 | Varies / 视工具 | Strongest when the tool is authoritative and version-bound. / 工具权威且绑定版本时最强。 | Code, data, calculations, schemas, citations, or policies are mechanically checkable. / 代码、数据、计算、Schema、引用或策略可机械验证。 |
| Human review / 人工评审 | Highest / 最高 | Accountable judgement; capacity-constrained. / 可问责判断但受容量限制。 | High-risk ambiguity, policy conflict, or non-automatable acceptance. / 高风险歧义、策略冲突或无法自动验收。 |

Correctness-critical output must not use self-critique alone when an authoritative tool-grounded check is available. Failure-cost-asymmetric domains should bias severity and escalation toward the expensive failure direction, while retaining the explicit policy and evidence for audit. / 正确性关键产出在权威工具检查可用时不得只用自评。失败成本不对称领域应让严重度和升级方向偏向昂贵失败一侧，同时保留明确策略与证据供审计。

## Composition With Governed Reflection / 与受治理反思组合

Use both runtimes with one-way evidence bindings / 通过单向证据绑定组合两个运行时：

1. `ReflectionSession` admits route `generator_critic`, freezes the baseline, and owns the declared change boundary. / `ReflectionSession` 准入 `generator_critic` 路由、冻结基线并拥有声明的改变边界。
2. The Generator-Critic contract binds the sealed reflection contract hash. / 生成评审契约绑定封存反思契约哈希。
3. `GeneratorCriticSession` owns artifact versions, review evidence buckets, policy decision, receipt, and release-version verification. / `GeneratorCriticSession` 拥有工件版本、评审证据分桶、策略裁决、回执及发布版本校验。
4. A `needs_revision` decision becomes evidence for a separately authorized change proposal; it is not itself change authorization. / `needs_revision` 裁决成为独立授权改变提案的证据，但本身不是改变授权。
5. The accepted exact artifact and Generator-Critic decision binding feed the shared change-applied event, independent revalidation, and round observation. / 已接受精确工件及生成评审裁决绑定进入共享改变应用事件、独立复验与轮次观察。
6. `build_shared_reflection_guard` validates those shared public records; `reflection_subject_binding_for_artifact` makes the applied/revalidated subject exact; the resulting assurance feeds receipt issuance and release verification. / `build_shared_reflection_guard` 校验这些共享公开记录；`reflection_subject_binding_for_artifact` 保证已应用/已复验对象精确；产生的保证进入回执签发与发布校验。
7. The shared reflection acceptance does not bypass the Generator-Critic receipt, and the Generator-Critic receipt does not prove broad causal improvement or authorize learning promotion. / 共享反思接受不得绕过生成评审回执；生成评审回执也不证明广义因果改善，不能授权学习晋升。

This composition prevents two common collapses: treating critique as change permission, and treating one accepted revision as proof that a persistent Skill or policy improved. / 该组合防止两类常见权限坍缩：把评审当作改变权限，以及把单个接受修订当作持久 Skill 或策略已改善的证明。

## Failure And Recovery / 失败与恢复

| Failure / 失败 | Runtime response / 运行时处理 | Recovery / 恢复 |
| --- | --- | --- |
| Stale artifact binding / 陈旧工件绑定 | Reject review start. / 拒绝开始评审。 | Reload current revision and explicitly restart review. / 重载当前修订并显式重启评审。 |
| Missing criterion result / 缺失判据结果 | Reject review artifact. / 拒绝评审制品。 | Complete the sealed criterion set; do not mark missing as pass. / 补齐封存判据集合，不得把缺失记为通过。 |
| Stale or diagnostic-only evidence / 过期或仅诊断证据 | Keep it out of supported gating evidence. / 不允许进入有据门控证据。 | Acquire a fresh allowed snapshot or route to human review. / 获取新鲜允许来源快照或转人工。 |
| Unsupported blocking opinion / 无据阻断意见 | Preserve as non-gating. / 保留为非门控意见。 | Add evidence and a valid check in a later explicit review. / 在后续显式评审中补证据与有效检查。 |
| Low score without evidence / 无据低分 | Record but do not gate. / 记录但不门控。 | Attach trusted score evidence or use criterion-level findings. / 绑定可信评分证据或改用判据级问题。 |
| Revision repeats the same digest / 修订摘要未变化 | Reject revision. / 拒绝修订。 | Produce a real content change or stop for no progress. / 产生真实内容变化或按无进展停止。 |
| Pass budget exhausted / 批次预算耗尽 | Apply sealed `human_required` or `reject`. / 应用封存的转人工或拒绝动作。 | Start a new governed Self-Heal Loop only with a new contract and budget. / 仅在新契约与预算下启动受治理自愈循环。 |
| Receipt or policy mismatch / 回执或策略不匹配 | Block release. / 阻断发布。 | Re-review under the current policy and issue a new receipt. / 按当前策略复审并签发新回执。 |
| Missing or invalid shared-reflection assurance / 共享反思保证缺失或无效 | Fail the initial-artifact, revision, receipt, or release boundary closed. / 在初始工件、修订、回执或发布边界默认阻断。 | Validate the complete shared contract/event/observation history and return its versioned assurance binding. / 校验完整共享契约、事件流与观察包历史并返回其版本化保证绑定。 |
| Release or side-effect terminal unknown / 发布或副作用终态未知 | Do not retry blindly or claim success. / 不盲目重试或宣称成功。 | Reconcile external state through governed action/tool-dispatch controls. / 通过受治理行动/工具调度对账外部状态。 |

The reference runtime is in-memory and coordinates public records. Production durability requires an append-only transactional store that commits artifact, event, decision, and receipt records atomically or exposes a recoverable boundary with stale-head rejection and idempotency. Do not claim crash safety from the in-memory session. / 参考运行时以内存方式协调公开记录。生产持久化需要追加式事务存储，原子提交工件、事件、裁决与回执，或暴露具备陈旧头拒绝与幂等性的可恢复边界；不得从内存会话声称崩溃安全。

## Pattern Template / 模式模板

- 状态 / Status: 已命名候选，专用契约与参考运行时已实现，生产持久化待部署方实现 / Named candidate with dedicated contracts and a reference runtime; production durability remains deployment-owned.
- 模式清单 / Patterns: Generator-Critic / 生成器-批评器.
- 诊断用途 / Diagnostic Use: Use when one immutable output version should pass through a short sequential review and optional explicit revision before release. / 当一个不可变输出版本应在发布前经过短链顺序评审及可选显式修订时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 内容生成、报告、代码补丁、结构化数据、知识沉淀、发布前验收 / Content generation, reports, code patches, structured data, knowledge memory, pre-release acceptance.
- 当前症状 / Current Symptoms: Generator confidence directly releases output; review has no predeclared criteria; findings lack evidence; critic decides release; revisions inherit an old pass; post-review edits escape; critique loops run open-ended. / 生成器自信直接放行；评审无预声明判据；问题无证据；评审器直接决定发布；修订继承旧通过；评审后编辑逃逸；评审循环无界运行。
- 适配信号 / Fit Signals: One artifact version, sequential dependency, explicit acceptance criteria, at most one normal revision, and a need for audit-grade version binding. / 单一工件版本、顺序依赖、明确验收判据、正常最多一次修订，以及审计级版本绑定需求。
- 调整方向 / Adjustment Direction: Insert exact-version artifact, critic, policy decision, revision, receipt, and release gates; select feedback by verifiability; keep the chain at one to two passes. / 插入精确版本工件、评审器、策略裁决、修订、回执及发布闸；按可验证性选择反馈；链限制为一至两次。
- 修改方式 / How To Modify: 1) Seal contract and criteria. 2) Create an immutable unreviewed artifact. 3) Review that exact binding. 4) Bucket supported findings and opinions. 5) Derive the policy decision. 6) Create a parent-bound unreviewed revision only from adopted issues. 7) Re-review explicitly. 8) Release only with a matching fresh receipt. / 1）封存契约与判据；2）创建不可变未评审工件；3）评审精确绑定；4）分桶有据问题与意见；5）派生策略裁决；6）仅基于采纳问题创建绑定父版本的未评审修订；7）显式复审；8）仅凭匹配且新鲜的回执发布。
- 输入 / Inputs: Shared reflection contract binding, artifact content/reference, criteria and risks, actor bindings, evidence snapshots, feedback variant, decision policy, revision/pass budgets, and release policy. / 共享反思契约绑定、工件内容/引用、判据与风险、角色绑定、证据快照、反馈变体、裁决策略、修订/批次预算及发布策略。
- 输出 / Outputs: Immutable artifact lineage, exact review records, supported and unsupported buckets, deterministic policy decisions, explicit re-review history, accepted-version receipt, release-verification event, and stop or escalation reason. / 不可变工件谱系、精确评审记录、有据与无据分桶、确定性策略裁决、显式复审历史、接受版本回执、发布校验事件及停止或升级原因。
- 风险与治理 / Risks & Governance: Shared critic blind spots, rubber-stamping, criteria gaming, stale evidence, incomplete risk coverage, version escape, receipt replay, open-ended critique, and false production durability claims; mitigate with role separation, tool grounding, frozen criteria, evidence freshness, exact digest binding, bounded passes, probe replay, and deployment-owned transactional persistence. / 共享评审盲点、橡皮图章、判据投机、证据过期、风险覆盖不足、版本逃逸、回执重放、无界评审及虚假生产持久化声明；通过角色分权、工具接地、冻结判据、证据新鲜度、精确摘要绑定、有界批次、探针回放及部署方事务持久化缓解。

Observability Metrics File / 可观测性指标文件: [reflection-chain-observability.md](reflection-chain-observability.md)

## Acceptance / 验收

- [ ] Criteria and material risks exist before generation. / 生成前已有判据与重大风险。
- [ ] Contract roles are version-bound and critic, policy gate, and release gate are distinct. / 契约角色已版本绑定，且评审器、策略闸、发布闸相互分离。
- [ ] Every artifact revision is immutable, digest-bound, parent-linked when revised, and initially unreviewed. / 每个工件修订不可变、绑定摘要、修订时链接父版本且初始未评审。
- [ ] Review starts only for the current exact artifact binding. / 评审只针对当前精确工件绑定启动。
- [ ] Every sealed criterion has one explicit result; missing and unknown are not pass. / 每个封存判据均有明确结果；缺失和未知不等于通过。
- [ ] Every gating issue has fresh trusted evidence; unsupported opinions are retained and non-gating. / 每个门控问题有新鲜可信证据；无据意见被保留且不门控。
- [ ] Policy decision is recomputed from the sealed contract and cannot be supplied by the critic. / 策略裁决从封存契约重算，评审器无法自报。
- [ ] Automatic revision uses only adopted issue IDs and creates a new unreviewed version. / 自动修订只使用采纳问题标识并创建新的未评审版本。
- [ ] A revised or superseding version obtains a new review, decision, and receipt. / 修订或替代版本取得新的评审、裁决及回执。
- [ ] Pass budget never exceeds two; unresolved work explicitly escalates or rejects. / 评审批次不超过两次；未解决工作明确升级或拒绝。
- [ ] Release checks exact artifact, receipt, policy, and evidence freshness. / 发布校验精确工件、回执、策略及证据新鲜度。
- [ ] Every protected boundary records a valid `shared_reflection_guard` assurance binding, and the real publish side effect cannot bypass `verify_release()`. / 每个受保护边界记录有效共享反思闸保证绑定，真实发布副作用无法绕过 `verify_release()`。
- [ ] Event stream is contiguous, self-hashed, replayable, and contains no private reasoning. / 事件流连续、自哈希、可回放且不含私密推理。
- [ ] Production durability claims are backed by a real transactional persistence implementation. / 生产持久化声明由真实事务持久化实现支撑。

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. Record the selected feedback variant, contract hash, artifact revision/digest lineage, review and decision bindings, receipt binding, required probes, release check, failure path, and unresolved deployment boundary. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议；记录所选反馈变体、契约哈希、工件修订/摘要谱系、评审与裁决绑定、回执绑定、必需探针、发布检查、失败路径及未解决部署边界。
