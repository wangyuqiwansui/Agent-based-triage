# Adversarial Review / 对抗评审

Cell / 交织点: collaboration-loop / 协作 x 循环

Capability / 能力: Collaboration / 协作

Mode / 模式: Loop / 循环

Identity / 稳定标识: `PATTERN_0045`, `CELL_COLLABORATION_LOOP`

Source / 来源: Existing paper coordinate / 既有论文坐标: arXiv:2605.13850; dedicated engineering inputs / 专用工程输入: 《对抗评审_执行流程.md》与《对抗评审_工作流可观测性探针.md》, version / 版本 `0.1.0`.

## Quick Navigation / 快速导航

- [Design and boundaries / 模式与边界](#design)
- [Roles and evidence / 角色与证据](#roles)
- [Objects and lifecycle / 对象与生命周期](#objects)
- [Execution nodes / 执行节点](#execution)
- [Approval and release gates / 批准与发布闸](#gates)
- [Shared exchange contract / 共享交互契约](#exchange)
- [Acceptance and implementation / 验收与实现](#acceptance)

<a id="design"></a>
## Design Pattern / 设计模式

Make independent, evidence-backed objections constrain approval and release of an exact artifact version. The loop is propose → independently review → revise → fully re-review → deterministically adjudicate; a valid version receipt precedes any separately authorized release. A quiet round, exhausted budget, high score or majority agreement is insufficient to approve. / 让有证据的独立异议约束精确工件版本的批准与发布。流程为提案、独立评审、修订、完整重审、确定性裁决；另行授权的发布前须有当前有效版本回执。整轮无新发现、预算耗尽、高分或多数同意都不足以批准。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Collaboration × Loop / 协作 × 循环, retained from the registry / 沿用注册表坐标。
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; detailed gates and probes below are engineering extensions from the supplied drafts, not additional paper claims. / 下方详细闸门与探针是用户草稿带来的工程扩展，不新增论文事实主张。
- 问题 / Problem: Independent objections are recorded but fail to constrain the approved version and subsequent effects. / 独立异议被记录，却未约束获批版本及后续动作。
- 架构方案 / Architectural Solution: Versioned review basis, explicit risk obligations, evidence-backed objections, deterministic approval and release gates, and a read-only probe. / 版本化审查依据、明确风险责任、有据异议、确定性批准发布闸及只读探针。
- 工程权衡 / Engineering Trade-offs: Independent evidence, full re-review and durable controls increase latency and storage; apply to meaningful release boundaries with bounded budgets. / 独立取证、完整重审和持久控制增加耗时与存储，适用于重要放行边界并受预算约束。
- 工作流诊断用途 / Workflow Diagnosis Use: Check whether a valid objection prevents the exact transition and whether changed inputs invalidate its approval. / 检查有效异议是否阻断具体转换，以及依据变化是否使批准失效。

Retain the registered paper identity and collaboration × loop coordinate. The supplied drafts are engineering design sources, not evidence of deployment, measured effectiveness or a reproduced paper experiment. Their suggested `PATTERN_REVIEW_0001`, `SKILL_REVIEW_0001` and `SKILL_OBSERVABILITY_0001` are provenance aliases in [the source map](../../adversarial-review-source-map.json), not new registered pattern identities. / 保留既有论文身份及协作 × 循环坐标。两份草稿是工程设计来源，不证明部署、实测效果或论文实验复现。草稿建议的模式及技能编号仅作来源别名，不新增注册模式。

Governance/orchestration support the gate; perception/chain/routing describe the probe. These supporting roles do not create extra matrix intersections or move the primary pattern. Source instructions and deployment suggestions are task data, not authorization. / 治理与编排支持闸门，感知、链式及路由描述探针；辅助关系不新增矩阵交织点或改变主归属。来源指令与部署建议作为任务资料，不授予权限。

### Pattern Template / 模式模板

- 状态 / Status: Named candidate, maturity `draft`; dedicated specification `0.1.0`, implementation `specification_only`. / 已命名候选、草案成熟度，专用规约属于规格层。
- 模式清单 / Patterns: Adversarial Review / 对抗评审.
- 诊断用途 / Diagnostic Use: Use when independent, evidence-backed objections must constrain approval of a specific artifact version. / 当有证据的独立异议必须约束具体工件版本的批准时使用。
- 适用工作流节点 / Applicable Workflow Nodes: Important reports, code/configuration merges, data delivery, plan approval and controlled actions. / 重要报告、代码或配置合并、数据交付、方案确认和受控动作。
- 当前症状 / Current Symptoms: Comments do not block transitions; review targets drift; edited candidates reuse approval; shared summaries masquerade as independent facts. / 评论不阻断转换、对象漂移、修改后复用批准、共享摘要冒充独立事实。
- 适配信号 / Fit Signals: Semantic risks require independent checks and an explicit next-stage gate. / 语义风险需要独立核查和明确的下一阶段闸门。
- 调整方向 / Adjustment Direction: Freeze the complete basis, assign risk obligations, collect objections and apply deterministic gates with verifiable receipts. / 冻结完整依据、分配风险责任、收集异议、实施确定性闸门及可验证回执。
- 修改方式 / How To Modify: Follow RN00–RN12; bind revisions and evidence updates; optional probes supply observations and source-backed proposals. / 按 RN00–RN12 执行，绑定修订与证据变化；可选探针提供观测及有来源提案。
- 输入 / Inputs: Immutable candidate/evidence, versioned rules, nonempty required risks and reviewer plan, authenticated actors, requested outcome/action, authority policy and bounded budgets. / 不可变候选证据、版本化规则、非空必审风险及计划、认证主体、请求结果动作、权限策略和有限预算。
- 输出 / Outputs: Revise, await evidence, escalate, terminate or approve; issue a current receipt when justified, and a separately confirmed release result only if requested and authorized; preserve ledgers and recovery points. / 修改、待补证、升级、终止或批准；满足条件签发当前回执，请求且授权时另记确认发布结果，保留账本及恢复点。
- 风险与治理 / Risks & Governance: `FAIL_0007` bounds repeated repair; `FAIL_0008` motivates context/source separation; `GOV_0001` bounds actions; `GOV_0002` preserves versions, objections and decisions. / 限制反复修订、隔离上下文与来源、约束动作范围、保存版本异议裁决。

Ordinary polishing may use Generator-Critic (`reflection-chain`); its inner revision loop can help repair a candidate here, but its score or receipt cannot replace the outer independent gate. Neither pattern is defined by fixed pass counts, mandatory different models or agreement. / 普通润色可用生成评审；其内层循环也可辅助修复，但分数或回执不能替代外层独立闸门。不以固定轮数、强制不同模型或一致程度定义模式。

## Shared Module Contract / 共享模块契约

The [shared collaboration procedure](../../collaboration-execution-flow.md) integrates review at `CE09`, source contract `2.0.0`, executable profile `3.0.0`. Its reference checks exact result versions, designated role separation, review acceptance and unresolved/upheld blocking objections. It does not implement all RN nodes, required-risk inventories, two-stage binding, a dedicated receipt service or external reconciliation below. / 通用协作规程在 CE09 接入评审，来源契约 `2.0.0`、执行配置 `3.0.0`；参考实现检查精确结果版本、指定角色分离、评审准入及未决或被维持的阻断。它未实现下方全部节点、风险清单、两层绑定、专用回执服务及外部核对。

When using the shared executable profile, retain its stricter executor/reviewer/arbiter separation and explicitly map this dedicated contract. Do not rename the profile or feed illustrative YAML directly to its Schema. / 使用共享可执行配置时，保留执行者、评审者、裁决者相互分离的约束，显式映射专用契约；不重命名配置或把演示 YAML 直接交给其 Schema。

<a id="roles"></a>
## Roles and Independence / 角色与独立性

| Role / 角色 | Responsibility and boundary / 责任与边界 |
| --- | --- |
| Proposer / 提案者 | Creates candidate, evidence claims and action request; cannot approve itself or directly use protected release. / 形成候选、依据及动作请求，不得自批或直接受保护发布。 |
| Reviewer / 评审者 | Reads assigned material, independently obtains evidence, files objections and verifies repairs; cannot edit candidate or issue approval. / 读取分配材料、独立取证、提异议并复核，不改候选或签批准。 |
| Reviser / 修订者 | May also be proposer; responds per objection and creates a new version; cannot close its own repair. / 可由提案者兼任，逐项回应并建新版本，不自行关闭修复。 |
| Arbiter / 裁决者 | Applies current policy and evidence; trusted deterministic control checks all conditions; semantic decisions never waive hard blockers. / 按当前策略及证据裁决，可信确定性控制检查全部条件，语义判断不豁免硬阻断。 |
| Authorized human / 授权人工 | Resolves scoped disputes/actions within policy; cannot approve with an upheld, open hard blocker. / 在策略范围内裁决争议或授权动作，不得带成立且未关闭的硬阻断批准。 |
| Probe / 探针 | Reads, correlates, measures and proposes supplements/findings; cannot directly close, approve, revoke or release. / 读取关联计量、提出补数及发现，不直接关闭、批准、撤销或发布。 |

Verify five independence dimensions with runtime evidence: authenticated reviewer/assignment; actual input/access manifests; inherited/excluded conclusions and blind-review policy; original snapshots and upstream source families; actual tool/server permissions and self-release paths. / 用运行时证据核验五项独立性：认证评审及授权、实际输入访问清单、继承与排除结论及盲审策略、原始快照与上游来源族、真实工具服务端权限及自放行通路。

One actor may cover multiple risks, but each required risk needs valid completion evidence. Same/different models alone prove neither dependence nor independence; two summaries of one upstream source remain one fact family. Necessary evidence access follows the versioned policy; blind review is not an unconditional ban on context. / 同一主体可覆盖多项风险，每项须有有效完成证据；模型同异不证明独立性，同上游的两个摘要仍属一条事实链。必要取证按版本化策略执行，盲审不等于无条件禁止上下文。

<a id="objects"></a>
## Objects and Lifecycle / 对象与生命周期

| Object / 对象 | Minimum binding / 最小绑定 |
| --- | --- |
| Candidate / 候选 | ID, version, parent, exact content location/digest, proposer, creation time and scenario. Every body edit creates a version. / 标识、版本、父版本、正文位置摘要、提案者、时间与场景；任何正文修改都建新版本。 |
| Evidence / 证据 | Immutable snapshot/version, digest, original locator, supported claim, data time, validity and trust level; a mutable URL is insufficient. / 不可变快照版本、摘要、原始定位、支持结论、时间、有效期及可信级别；可变地址不足。 |
| Baseline / 基线 | Candidate + evidence + rules + nonempty risks + complete reviewer plan + action boundary. Assignments precede final hashing. / 候选、证据、规则、非空风险、完整评审计划及动作边界；分工先于最终哈希。 |
| Review result / 评审结果 | Reviewer/task, baseline/round, checked risks, sources, findings, unknowns, completion and objection references. “No problem” is not completion proof. / 评审任务、基线轮次、已查风险、来源、发现、未知、完成及异议引用；“没问题”不是完成证明。 |
| Objection / 异议 | Stable ID, version/baseline/round, actor, risk, rule, location, failure condition, evidence, severity, separate confidence, requested fix, owner and disposition. / 稳定标识、版本基线轮次、主体风险规则定位、失败条件、证据、严重性、独立确信度、修复要求、责任及处置。 |
| Policy/checkpoint / 策略检查点 | Versioned gates, escalation, authority, receipt expiry and revision/retry/cost bounds; checkpoint stores node, attempts, baseline, task inventory, open issues, ledger cursor, budget, receipt and intent. / 版本化闸门升级权限、回执时效及修订重试成本界限；检查点保存节点尝试、基线任务、未决项、账本游标、预算回执意图。 |

```text
draft / 草稿 → reviewing / 评审中
  → revise / 修改 → new version and baseline / 新版本新基线 → reviewing
  → awaiting_evidence / 待补证 → verified supplement / 验证补充 → resume or re-review
  → escalated / 升级 → scoped decision / 有范围裁决 → re-review or terminated / 终止
  → approved / 批准 → pre-release recheck / 发布前复核 → intent / 发布意图
      → confirmed / 外部确认 | failed / 明确失败 | unknown / 结果不确定
  material change / 依据变化 → approval_invalidated / 当前批准失效 → re-review
```

Objections remain open through pending evidence, dispute or repair-awaiting-verification. Closure needs the original objection, target successor version, authorized independent verifier, rule, evidence and reason; disproven objections need an authorized evidence-backed dismissal. Repair in version 2 does not make version 1 historically correct. / 异议在待补证、争议及修复待复核期间保持未关闭；关闭须含原异议、目标后继版本、授权独立复核者、规则证据和理由；不成立也须授权举证撤回。第二版修复不改变第一版历史事实。

A semantic objection can cite evidence without executable reproduction. Insufficient proof of a serious concern becomes a critical pending question, not silence; severity disputes await authorized adjudication. New baselines recheck all required risks, reusing immutable sources when valid but never previous passing conclusions. / 语义异议可引用证据而不要求可执行复现；重大疑点缺证时成为关键待核实项，不被删除；严重性争议须授权裁决。新基线重审全部风险，可重用仍有效的不可变来源，不继承旧通过结论。

<a id="execution"></a>
## Execution Workflow / 执行流程

Distinguish review-only, receipt-only and actual release. Missing critical inputs return gaps and recovery actions. Budgets are configured bounds, not completion proofs; unused budget is not a failure and exhaustion of incomplete work is not success. / 区分仅评审、仅回执和实际发布；关键输入不足返回缺口和恢复动作。预算是配置边界，不证明完成；未用尽不是失败，耗尽但未完成不是成功。

<!-- review:execution_nodes:start -->
| ID / 编号 | Node / 节点 | Action, output and recovery / 动作、产出与恢复 |
| --- | --- | --- |
| RN00 / 节点-00 | Admission / 受理 | Check task, risk, requested outcome and authority; issue a bounded run contract or disclose missing configuration and reject unauthorized requests.<br>读取任务、风险等级、目标动作和权限；确认本模式适用。<br>产出 / Output: 任务契约、执行边界、运行标识。<br>恢复 / Recovery: 关键配置缺失则列缺口；越权请求直接拒绝。 |
| RN01 / 节点-01 | Freeze inputs / 冻结材料 | Freeze candidate, evidence, rules and action boundary into immutable versions and a provisional baseline; unavailable immutable sources require evidence recovery.<br>固化候选及证据清单，读取规则和动作边界，建立基线草案。<br>产出 / Output: 不可变工件版本、基线草案。<br>恢复 / Recovery: 来源可变且无法锁定则待补证；不得用当前摘要猜测历史。 |
| RN02 / 节点-02 | Assign responsibilities / 分配责任 | Assign every required risk, verify independence and freeze the complete plan before hashing the dispatchable baseline; pause on coverage or self-approval paths.<br>为每一必审风险指定主体与证据要求，检查独立性；冻结完整计划并计算最终基线摘要。<br>产出 / Output: 评审计划、独立性检查结果、封存的审查基线。<br>恢复 / Recovery: 覆盖缺口或自批自放通路未排除则暂停。 |
| RN03 / 节点-03 | Deterministic prechecks / 前置规则检查 | Validate types, bounds, authority, evidence freshness and completeness in code; failures block and cannot be overridden by a model.<br>程序核对类型、范围、权限、证据时效、输入完整性。<br>产出 / Output: 规则检查记录、确定性阻断项。<br>恢复 / Recovery: 失败直接阻断；模型评审不得覆盖结果。 |
| RN04 / 节点-04 | Dispatch review / 发起评审 | Send the same baseline, scoped risks and read-only inputs to assigned reviewers; record actual access; retries are bounded and reviewer replacement rebuilds the plan/baseline.<br>按同一基线分发任务、规则和只读材料；记录实际访问清单。<br>产出 / Output: 每个评审任务的受理记录。<br>恢复 / Recovery: 暂时失败可有限重试；替换评审者需更新计划并重建基线。 |
| RN05 / 节点-05 | Collect results / 执行与收集 | Review semantics, original evidence and risk boundaries; validate result bindings and sources; quarantine wrong versions and keep unsupported assertions pending verification.<br>核对语义、原始证据与风险边界，输出结构化结果；校验结果绑定和来源。<br>产出 / Output: 有效结果、异议、缺口与任务完成状态。<br>恢复 / Recovery: 错版结果隔离；缺少证据的断言进入待核实，不计完成。 |
| RN06 / 节点-06 | Coordinate supplements / 补数协调 | Classify gaps, retrieve evidence directly or request the probe, and validate replies; degrade only noncritical telemetry and escalate expired critical gaps.<br>分类缺口；自身读取或向探针发起带作用域请求，验证回传。<br>产出 / Output: 已验证补充、拒收原因或仍待补证。<br>恢复 / Recovery: 非关键观测缺失可降级；关键缺口超时进入升级，不视为通过。 |
| RN07 / 节点-07 | Seal and adjudicate / 封口裁决 | Require all mandatory tasks and critical requests to terminate, seal the review package, then revise, escalate or approve by deterministic conditions; material late facts reopen review.<br>确认全部必需结果完成、无未决关键请求，冻结评审包；按条件作裁决。<br>产出 / Output: 要求修改、升级或批准裁决。<br>恢复 / Recovery: 新发现到达且影响依据则撤销封口，重开评审。 |
| RN08 / 节点-08 | Revise and re-review / 修订重审 | Respond to each objection, create a new candidate version and review every required risk under a new baseline; exhaustion escalates or terminates without automatic approval.<br>修订者逐项回应并形成新版本；新版本重新建立基线、分配审查。<br>产出 / Output: 新版本及修复说明。<br>恢复 / Recovery: 达到预算仍不满足条件则升级或终止，禁止以轮数换批准。 |
| RN09 / 节点-09 | Issue receipt / 签发回执 | Validate the approved decision; bind baseline, final package, scope and expiry in a verifiable receipt; issuance failure leaves no usable credential and retries bind the same decision.<br>回执服务校验有效批准裁决，并绑定基线、最终评审包、动作范围及有效期。<br>产出 / Output: 可验证回执、批准事件。<br>恢复 / Recovery: 签发失败不产生可用批准凭证；幂等重试同一裁决。 |
| RN10 / 节点-10 | Recheck before release / 发布前复核 | Reload candidate, evidence, rules, revocation, authority and control revision; changed digests, expiry, new blockers or changed authority reject intent creation.<br>重新读取候选、证据、规则、撤销状态、授权与最新控制序号。<br>产出 / Output: 允许建立发布意图或拒绝原因。<br>恢复 / Recovery: 摘要变更、过期、新阻断、权限变化均拒绝；必要时重新评审。 |
| RN11 / 节点-11 | Controlled release / 受控发布 | Conditionally persist the intent and stable operation ID, dispatch through the controlled adapter, then reconcile external state; unknown effects cannot be blindly retried.<br>原子登记发布意图，按同一操作标识调用受控适配器并核对外部状态。<br>产出 / Output: 已确认成功、明确失败或结果不确定。<br>恢复 / Recovery: 结果不确定先查询核对，不能盲目重试副作用。 |
| RN12 / 节点-12 | Archive and feedback / 归档反馈 | Persist artifacts, evidence, objections, reviews, receipts and external results with recovery points; missing mandatory control persistence prevents a completion claim.<br>归档工件、证据、异议、评审、回执及发布结果；交付可恢复点和观测事件。<br>产出 / Output: 可追溯结果包、后续监控或人工任务。<br>恢复 / Recovery: 关键控制记录无法持久化时，不宣称本轮完成。 |
<!-- review:execution_nodes:end -->

Return run, current artifact/version/baseline/round, state, completed stage, open blockers, uncovered risks, critical gaps, pending disputes, receipt/external result references, next allowed action, resume node, ledger and observation degradation. Intent registration or timeout is never actual publication. / 返回运行、当前工件版本基线轮次、状态完成阶段、阻断缺口争议、回执及外部结果引用、下一动作恢复节点、账本与观测降级；意图登记或超时不等于实际发布。

<a id="gates"></a>
## Approval and Release Gates / 批准与发布闸

Design pseudocode only; all terms bind the current baseline and unknown never means true. / 以下仅为设计伪代码，所有条件绑定当前基线，未知不为真。

```text
approve = critical_inputs_and_sources_valid
      AND all_results_match_current_baseline_and_round
      AND nonempty_required_risk_inventory_and_plan
      AND every_required_risk_has_valid_completion
      AND identities_and_independence_satisfy_policy
      AND required_tasks_terminal_and_review_package_sealed
      AND open_blockers == 0
      AND no_unresolved_critical_disputes_or_supplement_requests
      AND deterministic_checks_pass
      AND target_action_and_authority_scope_are_explicit
```

批准条件须全部满足：关键输入来源有效、结果匹配基线轮次、风险计划非空、每项风险完成、主体独立性合规、任务终态且封口、无未关闭阻断、无关键未决或补证、程序检查通过、动作权限明确。 / Every conjunction is mandatory; aggregate scores cannot cancel a failed condition.

Receipt fields: authenticated issuer, tenant/run/artifact/version, baseline digest, final review-package digest, round, decision, control revision, rule version, allowed action/digest, target environment, authority, issuance/expiry, verification and revocation evidence. Authenticate via protected server record, MAC or signature; self-reported hashes do not prove issuance. / 回执含认证签发者、租户运行工件版本、基线及最终评审包摘要、轮次裁决控制修订、规则、动作摘要、环境权限、签发到期和验证撤销证据；使用受保护服务端记录、消息认证码或签名认证，自报哈希不证明签发。

Release entrypoints reload authoritative state: receipt identity/current availability, exact body/version, evidence freshness, current rules/risks, sealed package/new blockers, live authority, exact action/destination and control revision. Any mismatch rejects. A one-shot receipt binds one operation; retries reuse that identity, never authorize a second action. / 发布入口重读权威状态，核验回执身份可用性、正文版本、证据时效、当前规则风险、封口新阻断、实时权限、精确动作目标及控制修订；不符即拒绝。单次回执只绑定一个操作，重试复用标识，不授权第二次动作。

Validate the current control revision and durably register intent/operation ID in one conditional local commit. The dispatcher rechecks authority/revocation immediately before sending the same external idempotency key. Reconcile unknown effects before retry. Use destination preconditions when available; a local transaction cannot promise cross-system atomicity or exactly-once effects, and the dispatch-to-effect race remains an adapter limitation. / 在同一本地条件提交中核对控制修订并持久登记意图操作标识；派发器在使用同一外部幂等键发送前重验权限撤销；未知效果先核对后重试。目的端支持前置条件时使用；本地事务不保证跨系统原子或严格一次，派发到生效之间的竞态须由适配器说明。

Late material facts reopen sealed review and invalidate current receipt use. After publication, preserve the historical effect and create a separately authorized incident, withdrawal or compensation. Recovery reads authoritative state before trusting cached checkpoints; mandatory control-ledger failure prevents its dependent transition. / 重要迟到事实重开评审，使回执当前不可用；已发布则保留历史效果，另建授权处置、撤回或补偿。恢复先核验权威状态再信缓存；关键账本失败阻止相关状态转换。

<a id="exchange"></a>
## Shared Exchange Contract / 共享交互契约

Embedded for independent execution. Maintain [the shared source](../../adversarial-review-contract.md), then synchronize both peers. / 内嵌以支持独立执行；维护共享来源后同步两份规约。

<!-- review:contract:start -->
Description / 描述: Exchange control observations, scoped evidence requests and proposals while execution retains adjudication and release authority. / 交换控制观测、有范围的取证请求与提案，裁决和放行权限始终属于执行方。

Version / 版本: `0.1.0`; status / 状态: draft specification / 草案规格。

Usage / 适用场景: Standalone execution, independent offline observation, optional online observation or checkpoint evidence recovery. Neither peer requires the other to be running. / 独立执行、独立离线观测、可选在线旁路或检查点补证；双方均不要求对方必须在线。

Implementation boundary / 实现边界: This dedicated contract is specification-only. It is distinct from collaboration source contract `2.0.0`, executable profile `3.0.0`, CE09 and CSM25–CSM26. No dedicated service, authorization, durable proposal receiver, receipt signer or RM calculator is supplied by this document. An adapter must explicitly map fields and demonstrate its own validation and failure paths. / 本专用契约仅为规格，与协作来源契约、可执行配置、CE09 和 CSM25–CSM26 分开；本文不提供专用服务、鉴权、持久补数接收端、回执签发器或 RM 计算器。适配器须显式映射字段并验证校验与失败路径。

### Identity and bindings / 身份与绑定

| Fields / 字段 | Required semantics / 必需语义 |
| --- | --- |
| `contract_version`, `tenant_id`, `run_id` | Require compatible `0.1.0` semantics and authenticated tenant scope. A transport retry retains its run; a new business request starts another run. / 校验兼容版本与经认证租户；传输重试保留运行标识，重新发起业务任务另建运行。 |
| `artifact_id`, `artifact_version`, `baseline_digest`, `review_round` | Bind the immutable candidate and the exact review basis; new evidence or rules start a new baseline and round even without a body edit. / 绑定不可变候选与精确审查依据；正文未变但证据或规则改变仍须新基线、新轮次。 |
| `node_id`, `task_id`, `attempt` | Distinguish logical work from its bounded retries. Do not count attempts as independent tasks or risk coverage. / 区分逻辑任务及有限重试，不把尝试数当任务数或风险覆盖。 |
| `event_id`, `ledger_sequence`, `related_event_ids` | Unique event identity, authoritative order within a run and causal references. Exact redelivery is deduplicated; same ID with different content is quarantined as conflict. / 事件唯一键、运行内权威顺序与因果引用；同内容重投去重，同标识异内容隔离为冲突。 |
| `occurred_at`, `collected_at`, `unknown_time_reason` | Occurrence and collection are separate. Unknown historical occurrence is null with a reason, never copied from collection time. / 发生与采集时间分开；历史发生时间未知时为空并注明原因，不用采集时间冒充。 |
| `actor_id`, `source_type`, `source_refs`, `data_classification` | Trusted ingress verifies actor, authority, source and sequence; payload assertions cannot authenticate themselves. Unverified exports remain unverified. / 可信接入验证主体、权限、来源和序号；载荷自述无法自证身份，未验证导出保持未验证。 |
| `observation_revision`, `control_revision`, `report_revision` | Independent concurrency domains for side observations, release control and reports; none equals the artifact version. / 分别控制旁路观测、放行控制与报告的并发版本，不等同工件版本。 |

Baseline digest / 基线摘要 = canonical binding of candidate content, versioned evidence manifest, rules, required risks, reviewer plan and action boundary. Final review-package digest / 最终评审包摘要 = sealed results, objection disposition evidence and closure record. The receipt binds both digests plus adjudication, control revision and authority. Do not include future review results in the baseline hash. / 基线规范绑定正文、版本化证据清单、规则、必审风险、评审计划和动作边界；最终评审包绑定封存结果、异议处置证据和封口记录；回执绑定两者及裁决、控制修订与授权。基线哈希不得包含未来才产生的评审结果。

Fix encoding, field ordering, numeric/time formats and digest algorithm/version; preserve exact candidate text, including whitespace and punctuation. A digest detects binding changes; it proves neither source truth nor issuer identity. / 固定编码、字段排序、数值和时间格式、摘要算法及版本；保留正文原貌，包括空白和标点。摘要证明绑定变化，不证明来源真实或签发身份。

### Exchange workflow / 交换流程

| Message / 消息 | Minimum content and handling / 最小内容与处理 |
| --- | --- |
| Control event / 控制事件 | Full identity envelope, event type, authority-backed payload and immutable source references. Observation cannot rewrite the underlying control fact. / 完整身份信封、事件类型、有权威依据的载荷和不可变来源引用；观测不得改写底层控制事实。 |
| Supplement request / 补数请求 | `request_id`, `gap_id`, exact run/artifact/baseline/round, `field_path`, `expected_observation_revision`, evidence grade, allowed sources/operations, authorization reference, deadline, attempt budget and resume node. / 请求与缺口标识、精确对象绑定、字段路径、预期观测修订、证据等级、来源及操作白名单、授权引用、截止、尝试预算和恢复节点。 |
| Supplement proposal / 补数提案 | `proposal_id`, request and gap bindings, proposed value, evidence grade, source references/digest, collection/expiry times and claimed baseline impact. Submission alone changes no business fact. / 提案标识、请求与缺口绑定、提议值、证据等级、来源引用及摘要、采集与过期时间、声明的基线影响；提交本身不改变业务事实。 |
| Acceptance result / 接受结果 | Request/proposal identity, one disposition below, reason, old/new observation and control revisions, exact resulting baseline and resume node. Persist and replay the result with the application decision. / 请求与提案标识、下列一种处置、原因、新旧观测和控制修订、结果基线与恢复节点；接受决定及其结果须持久保存、可重放。 |
| Risk finding / 风险发现 | Affected scope, evidence, uncertainty and suspected violated rule; execution validates the finding and owns any pause, objection or new adjudication. / 受影响范围、证据、不确定性及疑似违反规则；执行方核验并负责暂停、异议或重新裁决。 |

Receiver order / 接收顺序: contract → authenticated identity/permission → tenant → correlated object → active request → current baseline/round → source authenticity → evidence freshness → field allowlist → expected observation revision. Any failure records a rejection with no partial update. / 依次校验契约、身份权限、租户、关联对象、请求有效性、当前基线轮次、来源真实性、证据时效、字段白名单、预期观测修订；任一失败只记拒收，不部分更新。

Use `(tenant_id, request_id, proposal_id)` as the durable idempotency key. Same key and same content returns the original result, including after restart; divergent content conflicts. A distinct stale proposal is rejected or filed under its historical version and never applied to the current head. / 以租户、请求、提案组成持久幂等键；同键同内容即使重启后也返回原结果，异内容冲突；新的陈旧提案拒收或归历史，不应用于当前版本。

| Disposition / 接受结果 | Execution-owned transition / 执行方状态转换 |
| --- | --- |
| `accepted_observation` / 已接受为观测补充 | Append source-backed telemetry and conditionally increment observation revision; resume the original check if its decision basis is unchanged. / 追加有来源遥测，条件更新观测修订；判断依据未变时恢复原检查。 |
| `accepted_re_review` / 已接受并触发重新评审 | Register new evidence/configuration, create a new baseline, invalidate current use of the old receipt and complete every required risk again. / 登记新证据或配置，建新基线，使旧回执当前不可用，再完成全部必审项。 |
| `pending_human_verification` / 待人工核实 | Preserve the proposal as unconfirmed; affected release conditions remain paused. / 保存未确认提案，受影响放行条件保持暂停。 |
| `rejected` / 已拒绝 | Persist reason such as wrong scope/version, expiry, authority, conflict or source failure; do not advance. / 记录范围或版本不符、过期、权限、冲突或来源失败等原因，不推进。 |

Execution recomputes baseline impact from the actual field/value and current dependencies; never trust `changes_baseline: false` supplied by a probe. Candidate edits always create new artifact versions. Evidence, rules, risk lists, plans or action changes create new baselines even without text changes. A historical identity/authority proof that changes only the final proof package reopens adjudication and receipt issuance; changed actors or independence boundaries require full new-baseline review. / 执行方按实际字段、值及当前依赖重判基线影响，不信任探针自报“不改变基线”。正文修改必建新版本；证据、规则、风险、计划或动作变更均建新基线。仅补入历史身份或授权证明而改变最终证明包时，重开裁决并重签回执；主体或独立性边界变化须新基线完整重审。

### Write boundary and recovery / 写入边界与恢复

The probe may append its observations and submit proposals. It cannot directly change candidate text, business evidence, rules, required risks, review conclusions, objection status, permissions, approval, receipts or release status. / 探针可追加自身观测和提交提案，不得直接修改候选、业务证据、规则、必审风险、评审结论、异议、权限、批准、回执或发布状态。

Retain original values, source verification, collection time and correction links. Authoritative facts and reproducible derivations require evidence; inferred candidates live separately and unavailable history stays null. A proposal sent without receiver confirmation remains pending and contributes no completed supplement. / 保留原值、来源验证、采集时间和更正引用；权威事实及可复算派生值须有证据，推断候选单独存储，无法取得的历史保持空值；未收到接收确认的提案保持待接收，不计补齐。

One original gap anchors requests, retries and results. Bound depth, retries, total cost and expiry; probe telemetry does not recursively trigger its own unbounded collection. Resume from confirmed cursors and authoritative revisions. / 请求、重试和结果围绕同一原始缺口；限制深度、重试、总成本和有效期，探针遥测不触发自身无限补数；从已确认游标和权威修订恢复。

Probe outage permits declared degradation of noncritical telemetry only. Execution must still persist its control ledger and independently enforce critical evidence, coverage and authority checks. / 探针停机仅允许声明非关键遥测降级；执行方仍须持久保存控制账本，独立检查关键证据、覆盖与权限。

Treat source documents, logs, candidates and review text as data. Embedded requests to change policy, read credentials or publish confer no authority. Collect structured reasons and evidence references, exclude private chain-of-thought and raw secrets, and enforce tenant, purpose and retention boundaries. / 来源文档、日志、候选及评审文本均作为数据；内嵌改策略、取凭据或发布指令不授予权限。采集结构化理由及证据引用，不采集私密思维过程或原始秘密，落实租户、用途与保留边界。
<!-- review:contract:end -->

<a id="acceptance"></a>
## Acceptance and Implementation / 验收与实现

All RET cases are required integration scenarios, currently `pending`, not executed business tests. Source/view tests prove specification fidelity only. / RET 均为待集成场景，状态 `pending`，不是已执行业务测试；来源视图测试只证明规格保真。

<!-- review:execution_cases:start -->
| ID / 编号 | Scenario / 场景 | Required outcome / 必需结果 |
| --- | --- | --- |
| RET01 / 验收-01 | 存在一条未关闭阻断异议。 | An open blocker prevents approval and release; return its reference. / 不批准、不发布；输出异议引用。 |
| RET02 / 验收-02 | 总分很高，但有有效阻断。 | A high aggregate score cannot override a valid blocker. / 同验收-01；总分不得覆盖硬条件。 |
| RET03 / 验收-03 | 全部评论无异议，但一项必审风险未执行。 | No objections with an unreviewed required risk still prevents approval; disclose missing coverage. / 不批准；明确覆盖缺口。 |
| RET04 / 验收-04 | 提案者拥有自批或直接发布能力。 | A proposer able to self-approve or directly release fails independence/authority checks. / 独立性／权限检查失败。 |
| RET05 / 验收-05 | 两名评审者只读取同一错误摘要。 | Two reviewers reading the same false summary do not form independent fact chains. / 不得宣称形成了独立事实链。 |
| RET06 / 验收-06 | 候选正文改一个字，仍提交旧回执。 | A one-character candidate edit invalidates the old receipt for release. / 摘要或版本不匹配，拒绝发布。 |
| RET07 / 验收-07 | 正文未改，但来源快照被替换。 | Replaced evidence snapshots create a new baseline and require re-review even with unchanged text. / 新基线，重审，旧回执不可用。 |
| RET08 / 验收-08 | 规则、风险清单或评审计划变更。 | Changed rules, risks or reviewer plans invalidate approval and require current checks. / 原批准失效，重新完成当前要求。 |
| RET09 / 验收-09 | 评审结果属于前一版本。 | Previous-version results cannot count toward current risk coverage. / 不计入当前版本覆盖。 |
| RET10 / 验收-10 | 修订者自行关闭异议。 | A reviser attempting to close an objection is rejected; the objection stays open. / 权限拒绝，异议仍未关闭。 |
| RET11 / 验收-11 | 探针提案来源不明或只含推测。 | Unknown-source or inferred probe proposals cannot become authoritative facts or approval evidence. / 不进入权威事实或批准条件。 |
| RET12 / 验收-12 | 同一补数提案重复投递。 | Exact repeated supplement proposals apply once and return the original acceptance result. / 只应用一次，返回原接受结果。 |
| RET13 / 验收-13 | 补数提案错租户、错版、过期或修订号冲突。 | Wrong tenant/version, expired or stale-revision proposals are rejected without partial updates. / 拒收并记录原因，无部分写入。 |
| RET14 / 验收-14 | 探针停机但业务证据齐全。 | With sufficient business evidence, a probe outage permits execution with declared observation degradation. / 业务可继续；明确观测降级。 |
| RET15 / 验收-15 | 探针停机且关键证据不足。 | With critical evidence missing, a probe outage requires evidence recovery or escalation, never automatic passage. / 待补证或升级，不能自动通过。 |
| RET16 / 验收-16 | 回执校验与提交之间发生撤销。 | Revocation between receipt checking and commit fails the conditional submission and prevents valid dispatch. / 条件提交失败；不生成有效派发。 |
| RET17 / 验收-17 | 外部调用超时，但动作可能已生效。 | A timed-out external call with possible effect remains unknown until reconciliation before any retry decision. / 结果不确定，先核对再决定重试。 |
| RET18 / 验收-18 | 超过修订或成本预算仍有阻断。 | Budget exhaustion with blockers escalates or safely terminates without approval. / 升级或安全终止，不自动批准。 |
| RET19 / 验收-19 | 关键控制账本写入失败。 | Control-ledger persistence failure prevents the dependent protected transition. / 阻止相应受保护状态转移。 |
| RET20 / 验收-20 | 恶意来源要求忽略评审、索取发布凭据。 | Malicious source instructions seeking bypass or credentials remain data without authority. / 作为数据隔离处理，不提升权限。 |
| RET21 / 验收-21 | 发布后才发现新阻断。 | New blockers found after publication create incident handling while preserving the real release history. / 新建事件处置；保留真实发布历史。 |
| RET22 / 验收-22 | 仅请求评审或回执，没有发布授权。 | A review-only or receipt-only request produces that result without external publication. / 返回评审结果或回执，不发生外部发布。 |
<!-- review:execution_cases:end -->

Constructed example: version 1 claims “complete isolation”; evidence distinguishes session, workspace and tool boundaries, so valid blockers prevent approval even at full coverage. Version 2 qualifies the claim, completes all reviews and receives its own receipt. Restoring the absolute title creates version 3, which cannot use version 2's receipt. This is an acceptance scenario, not a product measurement. / 构造示例：第一版宣称“完全隔离”，证据区分会话、工作区和工具边界，覆盖完整仍因阻断不能批准；第二版补限定、全部重审并取得专属回执；第三版改回绝对化标题，不能用第二版回执。此为验收场景，不是产品实测。

Implement immutable versions/evidence, risk obligations, authenticated roles, objection dispositions, deterministic gates and control persistence first; then receipt verification, conditional intents and destination reconciliation; finally optional collection/RM metrics. Validate RET/RPT failure paths before claiming runtime completion. / 先实现不可变版本证据、风险责任、认证角色、异议处置、确定性闸门及控制持久化，再实现回执验证、条件意图、目的端核对，最后可选采集及 RM 指标；验证 RET/RPT 失败路径后才声明运行时完成。

Maintenance / 维护: `python skills/harness-engineering-patterns/scripts/sync_adversarial_review_docs.py --write`, then the skill validator and relevant tests. Keep original identity and draft maturity; [the source map](../../adversarial-review-source-map.json) retains original definitions and fingerprints. / 修改后运行专用同步、技能校验与相关测试；保留原身份及草案成熟度，来源映射保存原定义与指纹。

Observability Metrics File / 可观测性指标文件: [collaboration-loop-observability.md](collaboration-loop-observability.md)

## Trace Hook / 追踪钩子

Use `references/trace-schema.md` to record project evidence at `.harness-analysis/<analysis_id>/trace.yaml`. Distinguish proposed specifications, verified documentation and verified deployment outcomes; bundled historical traces are not runtime state. / 按 Trace 契约在项目本地记录证据，区分设计规格、已验证文档及已验证部署效果；内置历史 Trace 不作运行状态。
