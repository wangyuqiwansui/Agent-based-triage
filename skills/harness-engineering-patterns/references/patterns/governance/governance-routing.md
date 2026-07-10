# Approval Gate / 审批门禁

Cell / 交织点: governance-routing / 治理 x 路由
Capability / 能力: Governance / 治理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Approval Gate routes every consequential action through a three-stage policy decision — deny rules, allow rules, then a human gate — so risk, not convenience, decides whether work continues. / 审批门禁将每个有后果的动作路由经过三段策略决策——拒绝规则、放行规则、人工门——由风险而非便利决定工作能否继续。

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
| 2. Allow rules / 放行规则 | Auto-pass, still logged. / 自动通过，仍记录。 | Read-only queries in scope, idempotent formatting, sandboxed tests. / 范围内只读查询、幂等格式化、沙箱内测试。 |
| 3. Gate / 人工或策略门 | Approve, block, escalate, or request evidence. / 批准、阻断、升级或索取证据。 | Irreversible writes, external side effects, boundary-ambiguous actions. / 不可逆写入、外部副作用、边界模糊动作。 |

Action classification / 动作分类: place each action on reversibility × impact; irreversible-high-impact always hits stage 3, reversible-low-impact should reach stage 2 so the gate stays rare and meaningful. / 将动作放入"可逆性 × 影响面"坐标；不可逆高影响必进第三段，可逆低影响应进第二段，让人工门保持稀少而有意义。

### Gate Sufficiency Rule / 门禁充分性规则

Applied evidence from this repository (governance trace, 2026-07-03): a structural gate passed an output with score 100 while the content was semantically contaminated by cross-project terms; the output later had to be superseded. Rule: a gate must check both structure (required fields, counts, thresholds) and semantics (content consistency with the project's own evidence); structural pass alone is not approval. Pair every structural gate metric with a semantic consistency companion check before routing downstream. / 本仓库实际应用证据（治理 trace，2026-07-03）：结构门以 100 分放行了一个被跨作品术语语义污染的产物，事后不得不作废。规则：门禁必须同时检查结构（必填字段、计数、阈值）与语义（内容与项目自身证据的一致性）；仅结构通过不等于批准。任何结构门指标在向下游路由前都应配套语义一致性检查。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Approval Gate / 审批门禁.
- 诊断用途 / Diagnostic Use: Use when risk or permission determines whether work can continue. / 当风险或权限决定工作能否继续时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 需求进入、治理审查 / Intake, governance review.
- 当前症状 / Current Symptoms: High-risk actions proceed unreviewed, or every trivial action demands confirmation and reviewers rubber-stamp; gates check field presence but pass semantically wrong content. / 高风险动作未审即行，或琐碎动作全要确认导致评审无脑放行；门禁只查字段存在却放行语义错误内容。
- 适配信号 / Fit Signals: 风险、权限或合规等级决定路径 / Risk, permission, or compliance level determines the path.
- 调整方向 / Adjustment Direction: Introduce the three-stage deny/allow/gate routing; classify actions by reversibility × impact; pair structural gate metrics with semantic consistency checks; tune allow rules until human gates are rare. / 引入拒绝/放行/门三段路由；按可逆性 × 影响面分类动作；结构门指标配套语义一致性检查；调整放行规则直到人工门足够稀少。
- 修改方式 / How To Modify: 1) Write deny and allow rule lists with owners. 2) Map action types onto the reversibility × impact grid. 3) Add a semantic consistency companion to each structural gate. 4) Track gate frequency and prune noisy triggers to fight approval fatigue. / 1）写出带负责人的拒绝与放行规则清单；2）将动作类型映射到可逆性 × 影响面网格；3）为每个结构门配语义一致性检查；4）跟踪门禁触发频率并裁剪噪声触发以对抗审批疲劳。
- 输入 / Inputs: Action request with type and scope, policy rule sets, reversibility/impact classification, project evidence for semantic checks. / 带类型与范围的动作请求、策略规则集、可逆性/影响分类、用于语义检查的项目证据。
- 输出 / Outputs: Gate decision record (stage, rule hit, decision, approver), blocked-action report with reasons, escalation events. / 门禁决策记录（段、命中规则、决定、审批人）、带原因的阻断报告、升级事件。
- 风险与治理 / Risks & Governance: Approval fatigue `FAIL_0011` (article-named) — measure gate frequency and keep stage-3 rare; permission bypass `FAIL_0005` when actions are misclassified into allow rules; structural-only gates passing contaminated content (repository-evidenced); all decisions logged per `GOV_0001` and `GOV_0002`. / 审批疲劳 `FAIL_0011`（论文点名）——度量门禁频率并保持第三段稀少；动作被误分类进放行规则时的权限绕过 `FAIL_0005`；仅结构门放行污染内容（本仓库实证）；所有决策按 `GOV_0001` 与 `GOV_0002` 记录。

Observability Metrics File / 可观测性指标文件: [governance-routing-observability.md](governance-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
