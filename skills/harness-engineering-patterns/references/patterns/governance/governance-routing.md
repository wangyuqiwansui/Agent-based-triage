# Approval Gate / 审批门禁

Cell / 交织点: governance-routing / 治理 x 路由
Capability / 能力: Governance / 治理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Approval Gate prepares a reviewable proposal, routes it under current policy, binds limited approval to its exact content, and revalidates before consuming permission and reconciling external effects. Mandatory denial precedes all routes; missing evidence returns to preparation. / 审批门禁先形成可审提案，按当前策略路由，将有限批准绑定精确内容，在消费许可前重新验证并核对外部效果；强制拒绝优先于所有路线，缺证返回准备。

Read the dedicated [execution flow / 执行流程](../../approval-gate-execution-flow.md), [independent probes / 独立探针](../../approval-gate-observability-probes.md), [binding and supplement contract / 绑定与补全契约](../../approval-gate-contract.md) and [source map / 来源映射](../../approval-gate-source-map.json). They preserve 20 execution stages, 28 probes, 50 metric definitions and 55 unexecuted acceptance requirements from the supplied approval documents. This is a `specification_only` extension of `PATTERN_0047`, not a deployed service or a new pattern. / 专用规约保留用户审批资料的 20 个执行阶段、28 项探针、50 项指标定义及 55 项未执行验收要求；这是原模式的规格扩展，并非已部署服务或新模式。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Governance / 治理 x Routing / 路由 in arXiv:2605.13850. The article cites Claude Code's tiered permission system as a production example. / 代表性定义 / Representative definition；来源表将 Governance / 治理 x Routing / 路由 映射到该单元。论文引用 Claude Code 分级权限系统作为生产实例。
- 问题 / Problem: Autonomous work sometimes crosses risk, permission, or policy boundaries where continuation requires explicit approval. / 自主工作有时会跨越风险、权限或策略边界，继续推进需要明确审批。
- 架构方案 / Architectural Solution: Route decisions through three ordered stages: 1) Deny rules reject forbidden actions immediately; 2) Allow rules pass known-safe actions without friction; 3) everything else goes to a human or policy gate. Classify actions by reversibility × impact to decide which stage applies. / 通过三段有序路由决策：1）拒绝规则立即拦截禁止动作；2）放行规则让已知安全动作无摩擦通过；3）其余全部进入人工或策略门。按"可逆性 × 影响面"给动作分类，决定其落入哪一段。
- 工程权衡 / Engineering Trade-offs: Improves safety and accountability, but introduces bottlenecks and requires calibrated thresholds. The article names approval fatigue as the central failure: gates that fire too often train humans to click through, which silently destroys the control. / 提升安全和问责，但引入瓶颈并需要校准阈值。论文点名"审批疲劳"为核心失败：门禁触发过频会训练人类无脑放行，静默摧毁控制力。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when risk or permission determines whether work can continue. / 当风险或权限决定工作能否继续时使用。

### Gate Routing Model / 门禁路由模型

| Stage / 段 | Decision / 决策 | Examples / 示例 |
| --- | --- | --- |
| 1. Deny rules / 拒绝规则 | Hard block, no escalation. / 硬阻断，不升级。 | Cross-tenant reads, credential exfiltration, destructive ops outside scope. / 跨租户读取、凭据外泄、越界破坏性操作。 |
| 2. Allow rules / 放行规则 | Only complete, explicitly preauthorized proposals qualify; issue a bounded machine receipt and revalidate. / 仅完整且明确预授权提案可用，签发有限机器回执并重检。 | Read-only queries in scope, idempotent formatting, sandboxed tests. / 范围内只读查询、幂等格式化、沙箱内测试。 |
| 3. Gate / 人工或策略门 | Review complete proposals or escalate authority; evidence gaps return to preparation before human review. / 对完整提案人审或升级权限；缺证在人审前返回准备。 | Irreversible writes, external side effects, boundary-ambiguous actions. / 不可逆写入、外部副作用、边界模糊动作。 |

Action classification / 动作分类: place each action on reversibility × impact; mandatory denies always win; otherwise irreversible-high-impact hits stage 3 and preauthorized reversible-low-impact may reach stage 2 so the gate stays rare and meaningful. / 将动作放入"可逆性 × 影响面"坐标；强制拒绝始终优先；其他不可逆高影响动作进入第三段，预授权可逆低影响动作可进入第二段，让人工门保持稀少而有意义。

### Gate Sufficiency Rule / 门禁充分性规则

Applied evidence from this repository (governance trace, 2026-07-03): a structural gate passed an output with score 100 while the content was semantically contaminated by cross-project terms; the output later had to be superseded. Rule: a gate must check both structure (required fields, counts, thresholds) and semantics (content consistency with the project's own evidence); structural pass alone is not approval. Pair every structural gate metric with a semantic consistency companion check before routing downstream. / 本仓库实际应用证据（治理 trace，2026-07-03）：结构门以 100 分放行了一个被跨作品术语语义污染的产物，事后不得不作废。规则：门禁必须同时检查结构（必填字段、计数、阈值）与语义（内容与项目自身证据的一致性）；仅结构通过不等于批准。任何结构门指标在向下游路由前都应配套语义一致性检查。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Approval Gate / 审批门禁.
- 诊断用途 / Diagnostic Use: Use when reviewable proposals need scoped approval, durable waiting, revalidation and accountable effect reconciliation. / 当可审提案需要受限审批、持久等待、执行前重检及可追责的效果核对时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 需求进入、治理审查 / Intake, governance review.
- 当前症状 / Current Symptoms: High-risk actions proceed unreviewed, or every trivial action demands confirmation and reviewers rubber-stamp; gates check field presence but pass semantically wrong content. / 高风险动作未审即行，或琐碎动作全要确认导致评审无脑放行；门禁只查字段存在却放行语义错误内容。
- 适配信号 / Fit Signals: 风险、权限或合规等级决定路径 / Risk, permission, or compliance level determines the path.
- 调整方向 / Adjustment Direction: Introduce the three-stage deny/allow/gate routing; classify actions by reversibility × impact; pair structural gate metrics with semantic consistency checks; calibrate authorized allow rules using reviewed evidence without dropping necessary approvals. / 引入拒绝/放行/门三段路由；按可逆性 × 影响面分类动作；结构门指标配套语义一致性检查；依据复核证据校准经授权的放行规则，同时保留必要审批。
- 修改方式 / How To Modify: Freeze proposal and policy, require complete evidence, route by explicit authority, verify role/quorum/separation, persist waiting, issue scoped receipts, revalidate and atomically consume with durable idempotency, reconcile effects, and observe through independent probes. Use the dedicated acceptance matrix before claiming an implementation. / 冻结提案策略，要求证据完整，按明确权限路由，核验角色会签职责，持久化等待，签发有限回执，重检后原子消费并持久幂等，核对效果并由独立探针观测；声明实现前验证专用验收矩阵。
- 输入 / Inputs: Action request with type and scope, policy rule sets, reversibility/impact classification, project evidence for semantic checks. / 带类型与范围的动作请求、策略规则集、可逆性/影响分类、用于语义检查的项目证据。
- 输出 / Outputs: Bound proposal/policy/decision/receipt, durable checkpoint, execution/effect records, structured denial/escalation reasons, supplements and adoption receipts, and a final run state distinct from business success. / 绑定提案策略决定回执、持久检查点、执行效果记录、结构化拒绝升级原因、补全及采纳回执，以及与业务成功分开的最终运行状态。
- 风险与治理 / Risks & Governance: Approval fatigue `FAIL_0011` (article-named) — measure gate frequency and keep stage-3 rare; permission bypass `FAIL_0005` when actions are misclassified into allow rules; structural-only gates passing contaminated content (repository-evidenced); all decisions logged per `GOV_0001` and `GOV_0002`. / 审批疲劳 `FAIL_0011`（论文点名）——度量门禁频率并保持第三段稀少；动作被误分类进放行规则时的权限绕过 `FAIL_0005`；仅结构门放行污染内容（本仓库实证）；所有决策按 `GOV_0001` 与 `GOV_0002` 记录。

### Module Attachment / 模块工程挂载

Identity / 身份: `CELL_GOVERNANCE_ROUTING; PATTERN_0047`. Existing names and maturity stay unchanged. / 保持现有名称与成熟度不变。

Route a frozen action to allow, deny, human review, or read-only rehearsal using current applicable rules; rule changes are a separate authorized workflow. / 根据当前适用规则，将冻结动作路由到允许、拒绝、人工复核或只读演练；规则变更是独立授权流程。

Read the maintained [execution flow / 执行流程](../../governance-execution-flow.md#execution-steps) (执04–07、执09) and [shared contract / 共享契约](../../governance-contract.md). These are specification-only engineering extensions from the supplied lesson-36 documents; this card does not provide a dedicated production runtime or make an existing runtime implement `GOV_BOUNDARY_OBS`. / 阅读维护版执行流程与共享契约。这些内容是用户第 36 讲资料的规范级工程扩展；本卡不提供专用生产运行时，也不表示既有运行时已实现 `GOV_BOUNDARY_OBS`。

| Attachment point / 落点 | Required behavior and evidence / 必要行为与证据 |
| --- | --- |
| Decision inputs / 裁决输入 | Use the immutable proposal, current policy set, trusted identity and delegated scope, and impact evidence; a model's risk label is not authority. / 使用不可变提案、当前策略集合、可信身份与委托范围、影响证据；模型风险标签不是授权。 |
| Decision record / 裁决记录 | Keep proposal, policy, receipt, and human approval as distinct objects. Allow and deny receipts bind policy ID, version, full digest, decision context, reason, and expiry. / 分开保存提案、策略、回执与人工批准；允许和拒绝回执均绑定策略 ID、版本、完整摘要、裁决上下文、原因及有效期。 |
| Revalidation / 再核验 | Changed amount, recipient, artifact, policy, credential, or resource precondition requires the appropriate fresh decision and final payload check. / 金额、接收方、工件、策略、凭证或资源前置条件变化时，重新进行适用裁决及最终载荷检查。 |

Boundary / 边界: An automatic-approval threshold controls routing; it is not a hard budget or account balance. Human approval cannot override mandatory denies or create budget. Verify policy-change proposer/approver separation and scope; never raise a threshold merely to let the current request pass. / 自动审批阈值控制路由，不是硬预算或账户余额；人工批准不能覆盖强制拒绝或创造预算。核验策略变更提出者与批准者的职责分离及权限，不为放行当前请求擅自升限。

Acceptance references / 验收引用: 执验01–08、26; use the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These are expected checks, not claims that production tests passed. / 这些是待验证的预期，不代表生产测试已通过。

Metric references / 指标引用: 指01–05、13–15、31; definitions, denominators, and unavailable states live in the [metric catalog / 指标目录](../../governance-observability-probes.md#metric-catalog). Permission and verified business success are separate results. / 口径、分母及不可用状态由指标目录统一定义；合规许可与已核实业务成功分开记录。

Observability Metrics File / 可观测性指标文件: [governance-routing-observability.md](governance-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
