# Skill Package / 技能包

Cell / 交织点: reflection-routing / 反思 x 路由
Capability / 能力: Reflection / 反思
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Skill Package routes each evaluation conclusion to its handling path — rework, escalation, handoff, or release — through a verdict-keyed routing table, and packages solutions that repeatedly prove themselves into reusable Skills so the same class of finding lands on a verified routine instead of an improvised fix. / 技能包通过以裁定为键的路由表，把每个评估结论路由到对应处理路径——返工、升级、交接或发布——并将反复验证有效的解法封装为可复用技能，让同类发现落到已验证例程上而不是临场即兴修复。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reflection / 反思 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Reflection / 反思 x Routing / 路由 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Reflection / 反思 x Routing / 路由 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: When every evaluation conclusion falls into one undifferentiated fix-it queue, mechanical rework blocks release-ready work, findings that need escalation get silently absorbed, and recurring problems are re-solved from scratch because nothing turns a proven fix into a reusable routine. / 当所有评估结论都落入同一条无差别修补队列时，机械返工挡住可发布的工作、需要升级的发现被悄悄消化、重复问题一次次从零重解——因为没有机制把已验证的修复变成可复用例程。
- 架构方案 / Architectural Solution: Maintain a verdict-keyed routing table: each evaluation result class maps to a route — rework (self-heal or generator-critic), escalation per `GOV_0001`, handoff, or release — with trigger and owner; when the same problem class is solved by the same solution enough consecutive times, route it to a skill proposal that packages the solution as a reusable Skill (references/pattern-skill-packaging.md). / 维护以裁定为键的路由表：每类评估结果映射到路径——返工（自愈或生成者-评审者）、按 `GOV_0001` 升级、交接或发布——并带触发条件与负责人；当同类问题被同一解法连续解决足够次数，路由到技能提议，将解法封装为可复用技能（references/pattern-skill-packaging.md）。
- 工程权衡 / Engineering Trade-offs: Routing plus packaging converts repeated repairs into one-time skill investments, but a misclassified verdict sends work down the wrong path, and premature packaging freezes an unproven solution — packaging evidence must clear the scoring anchor, since structural completeness alone caps at 89. / 路由加封装把重复修复转化为一次性技能投资，但裁定误分类会把工作送错路径，过早封装则固化未经验证的解法——封装证据必须过评分锚点，仅结构完整最高只有 89 分。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when reflection routes work to packaged evaluators, repair skills, or review routines. / 当反思需要路由到封装评估器、修复技能或评审例程时使用。

### Reflection Routing Table / 反思路由表

| Evaluation Result / 评估结果 | Route Target / 路由目标 | Trigger / 触发条件 | Owner / 负责人 |
| --- | --- | --- | --- |
| Verifier-decidable defect / 验证器可裁定的缺陷 | Self-Heal Loop (reflection-loop) / 自愈循环 | Deterministic failure signature present. / 存在确定性失败特征。 | Agent / 智能体 |
| Judgment-quality gap / 判断型质量差距 | Generator-Critic rework (reflection-chain) / 生成者-评审者返工 | Critique below the acceptance bar. / 评审低于采纳线。 | Author and critic / 作者与评审者 |
| Out-of-mandate or high-risk finding / 超授权或高风险发现 | Escalation per `GOV_0001` / 按 `GOV_0001` 升级 | Permission or blast radius exceeds mandate. / 权限或影响面超出授权。 | Human approver / 人工审批者 |
| Passed, owned elsewhere / 通过但归属他方 | Handoff (collaboration-chain) / 交接（collaboration-chain） | Acceptance check ready. / 验收检查就绪。 | Receiving owner / 接收方负责人 |
| Passed all gates / 全部门控通过 | Release path / 发布路径 | Required checks all green. / 所需检查全绿。 | Release owner / 发布负责人 |
| Same problem, same solution, N consecutive times / 同类问题同一解法连续 N 次 | Skill proposal (references/pattern-skill-packaging.md) / 技能封装提议 | Recurrence threshold hit with evidence. / 带证据达到复现阈值。 | Skill maintainer / 技能维护者 |

Routing rules / 路由规则:

- No verdict class, no route: unclassified evaluation results go to human triage, never to a guessed path. / 无裁定类不路由：未分类评估结果进人工分诊，绝不猜路径。
- Skillize only on evidence: a packaging proposal carries the recurrence trace and must clear the scoring anchor — structural completeness alone caps at 89. / 只凭证据技能化：封装提议须携带复现追踪并过评分锚点——仅结构完整最高 89 分。
- Every routing decision and its downstream outcome is recorded per `GOV_0002`. / 每次路由决策及其下游结果按 `GOV_0002` 入账。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Skill Package / 技能包.
- 诊断用途 / Diagnostic Use: Use when reflection routes work to packaged evaluators, repair skills, or review routines. / 当反思需要路由到封装评估器、修复技能或评审例程时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 验证测试、治理审查 / Verification, governance review.
- 当前症状 / Current Symptoms: All evaluation findings queue for the same generic fix regardless of severity or ownership; escalation-worthy findings get silently patched; the same class of problem is re-solved from scratch every sprint with no packaging into a reusable routine. / 所有评估发现不分严重度与归属排进同一条通用修补队列；本应升级的发现被悄悄修掉；同类问题每个迭代都从零重解，从未封装成可复用例程。
- 适配信号 / Fit Signals: 评估结果决定返工、升级、交接或发布路径 / Evaluation decides rework, escalation, handoff, or release path.
- 调整方向 / Adjustment Direction: Put a verdict-keyed routing table after evaluation, with a skillize route that packages recurrently proven solutions as reusable Skills. / 在评估之后放置以裁定为键的路由表，并设技能化路径，把反复验证的解法封装为可复用技能。
- 修改方式 / How To Modify: 1) Enumerate evaluation verdict classes and their handling paths (rework, escalate, handoff, release). 2) Fill the routing table with trigger and owner per class, defaulting unknowns to human triage. 3) Set the recurrence threshold (same problem, same solution, N consecutive times) for skill proposals. 4) Require packaging evidence to clear the scoring anchor before a Skill ships. 5) Record routing decisions and outcomes per `GOV_0002`. / 1）枚举评估裁定类及处理路径（返工、升级、交接、发布）；2）为每类填路由表（触发条件、负责人），未知类默认人工分诊；3）为技能提议设复现阈值（同类问题同一解法连续 N 次）；4）技能发布前封装证据须过评分锚点；5）路由决策与结果按 `GOV_0002` 入账。
- 输入 / Inputs: Evaluation verdict with class and evidence, routing table, recurrence history per problem class, skill packaging criteria and scoring anchors. / 带类别与证据的评估裁定、路由表、每类问题的复现历史、技能封装标准与评分锚点。
- 输出 / Outputs: Routing decision record (verdict, route, rule hit), dispatched rework or escalation or handoff or release events, skill proposals with recurrence traces, packaged Skills. / 路由决策记录（裁定、路径、命中规则）、派发的返工/升级/交接/发布事件、带复现追踪的技能提议、封装完成的技能。
- 风险与治理 / Risks & Governance: Misrouted verdicts send release-ready work to rework or absorb escalation-worthy findings — audit routing decisions by sampling and keep the human-triage default for unknown classes; premature skillization freezes unproven fixes — enforce the recurrence threshold and scoring anchor (structural-only caps at 89); high-risk routes go through approval per `GOV_0001`; every decision is recorded per `GOV_0002` so routing quality itself can be evaluated. / 裁定误路由会把可发布工作送去返工或消化掉本应升级的发现——抽样审计路由决策，未知类保持人工分诊默认；过早技能化固化未经验证的修复——强制复现阈值与评分锚点（仅结构完整最高 89 分）；高风险路径按 `GOV_0001` 走审批；每次决策按 `GOV_0002` 入账，路由质量本身可被评估。

Observability Metrics File / 可观测性指标文件: [reflection-routing-observability.md](reflection-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
