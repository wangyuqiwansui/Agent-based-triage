# Example Compilation / 编译示例

Use this file as an end-to-end worked reference for the compiler path: input -> EIR -> matrix mapping -> pattern selection -> adjustment -> evaluation -> trace. It contains four compressed article cases and one full repository case. / 当需要参照完整编译路径（输入 -> EIR -> 矩阵映射 -> 模式选型 -> 调整 -> 评估 -> 追踪）时使用本文档。它包含四个压缩论文案例和一个完整仓库案例。

Sources / 来源: the four cross-domain case studies in arXiv:2605.13850 (financial lending, legal due diligence, network operations, healthcare triage), and the Novel Studio project-10 story_macro gate records (2026-07-03) in `patterns/governance/trace.md` and `patterns/reasoning/trace.md`. / arXiv:2605.13850 的四个跨领域案例研究（金融信贷、法务尽调、网络运维、医疗分诊），以及 `patterns/governance/trace.md` 与 `patterns/reasoning/trace.md` 中的 Novel Studio project-10 story_macro 门禁记录（2026-07-03）。

## How To Use / 使用方式

- Read the article cases to see how the same pipeline re-parameterizes across environments per the Environmental Constraint Laws / 环境约束定律 in `diagnosis-method.md`. / 阅读论文案例，观察同一管线如何按 `diagnosis-method.md` 中的环境约束定律跨环境重新参数化。
- Read the repository case to see every pipeline step executed against real trace evidence, including a failure and its repair. / 阅读仓库案例，观察每个管线步骤在真实 Trace 证据上的执行，包括一次失败及其修复。
- Never copy thresholds, budgets, or criteria from any case here (Law 5); re-derive them from local evidence. / 不要照抄任何案例的阈值、预算或判据（定律 5）；必须由本地证据重推。

## Article Cases / 论文案例

### Environment Comparison / 环境对照

| Dimension / 维度 | Financial Lending / 金融信贷 | Legal Due Diligence / 法务尽调 | Network Operations / 网络运维 | Healthcare Triage / 医疗分诊 |
| --- | --- | --- | --- | --- |
| Time budget / 时间预算 | ~4 hours / 约 4 小时 | ~8 hours / 约 8 小时 | 5-minute SLA / 5 分钟 SLA | ~60 seconds / 约 60 秒 |
| Volume / 处理量 | One application at a time / 单笔申请 | ~500 contracts per deal / 单案约 500 份合同 | Continuous alert stream / 持续告警流 | One patient at a time / 单个患者 |
| Dominant topology / 主导拓扑 | Orchestration / 编排 | Hierarchy / 层级 | Routing / 路由 | Chain / 链式 |
| Pattern count / 模式数量 | 7 | 8 | 9 | 7 |
| Binding constraint / 绑定约束 | Full audit trail / 完整审计链 | Cross-client data isolation / 跨客户数据隔离 | Blast radius: auto-execute only P3/P4 alerts / 爆炸半径：仅 P3/P4 告警自动执行 | Failure-cost asymmetry: under-triage is fatal / 失败成本不对称：低估分诊致命 |

### Selection Readout / 选型解读

An illustrative readout of how each law binds each environment. The article's case narratives are authoritative; use this table only as a reading aid. / 以下是各定律如何约束各环境的解读示意。论文案例叙述为准，本表仅作阅读辅助。

| Selection step / 选型步骤 | Financial Lending / 金融信贷 | Legal Due Diligence / 法务尽调 | Network Operations / 网络运维 | Healthcare Triage / 医疗分诊 |
| --- | --- | --- | --- | --- |
| ROUTE by Law 1 (time) / 按定律 1（时间）判拓扑 | Hours allow controller-managed multi-check orchestration. / 小时级预算允许控制器管理的多检查编排。 | Hours plus volume justify layered decomposition. / 小时级预算加处理量支撑分层拆解。 | 5-minute SLA forbids deep topology; route to the shortest fitting path. / 5 分钟 SLA 不容深拓扑；路由到最短适配路径。 | 60 seconds force a minimal linear chain. / 60 秒只容最小线性链。 |
| Governance by Law 2 (authority) / 按定律 2（权限）选治理 | Decision is advisory; a gate plus full audit trail carries accountability. / 决策为建议型；门禁加完整审计链承担问责。 | Isolation dominates: contain what each subteam may read. / 隔离优先：限制每个子团队可读范围。 | Low-risk alerts auto-execute inside blast-radius limits; higher severities route to humans. / 低风险告警在爆炸半径内自动执行；更高严重度路由给人。 | Recommendation only; the critic and gate carry the safety burden. / 仅输出建议；批评器与门禁承担安全责任。 |
| Reflection by Law 3 (failure cost) / 按定律 3（失败成本）调反思 | Critique the decision memo before it enters the audit record. / 决策备忘进入审计记录前先批评。 | Sample-review contract findings across subteams. / 跨子团队抽检合同发现。 | No in-loop critic fits the SLA; rely on post-incident replay. / SLA 内放不下环内批评器；依赖事后回放。 | Critic biased to upgrade acuity because under-triage is the fatal direction. / 批评器偏向提升急重度，因为低估分诊是致命方向。 |
| Collaboration by Law 4 (volume) / 按定律 4（处理量）定协作 | Single item: no collaboration row needed. / 单项：无需协作行。 | ~500 items: Fan-Out/Gather plus Hierarchical Delegation. / 约 500 项：扇出汇聚叠加层级委派。 | Continuous stream: routing plus auto-scaling. / 持续流：路由加自动伸缩。 | Single patient: no collaboration row needed. / 单个患者：无需协作行。 |

Law 5 reading / 定律 5 解读: lending and triage both use Generator-Critic / 生成器-批评器, but with different criteria (audit completeness vs. acuity safety) — the pattern is a structural template, and every environment re-parameterizes it. / 金融信贷与医疗分诊都使用生成器-批评器，但判据不同（审计完整性对急重度安全）——模式是结构模板，每个环境都要重新参数化。

## Repository Case: Novel Studio story_macro Gate / 仓库案例：Novel Studio story_macro 门禁

A full pipeline walkthrough on real evidence: gating a regenerated full-story bible before downstream volume work. / 基于真实证据的完整管线演练：在下游分卷工作前，对重新生成的全本故事圣经执行门禁。

### Step 1: Classify Input / 第一步：输入分类

Input type is mixed / 混合输入: a pipeline workflow (`run_novel_pipeline.py --stage story_macro`), runtime outputs (stage outputs 1447, 1801, 1803, 1804), and existing trace entries. / 输入类型为混合输入：管线工作流（`run_novel_pipeline.py --stage story_macro`）、运行产物（阶段产物 1447、1801、1803、1804）和既有追踪记录。

### Step 2: EIR Slice / 第二步：EIR 切片

Example-local node IDs; not registry entries. / 示例内节点编号，非注册表条目。

| Node / 节点 | Responsibility / 职责 | Capability / 能力 | Topology / 拓扑 | Cell / 交织点 |
| --- | --- | --- | --- | --- |
| N1 story_macro regeneration / 故事圣经再生成 | Decompose premise into reader contract, mainline, arcs, event chain, foreshadowing, volume blueprint. / 将前提拆解为读者契约、主线、成长弧、事件链、伏笔和分卷蓝图。 | Reasoning / 推理 | Hierarchy / 层级 | reasoning-hierarchy（扩展候选 / extension candidate） |
| N2 macro quality gate / 宏观质量门禁 | Decide whether the bible may enter `volume_strategy`. / 决定圣经能否进入 `volume_strategy`。 | Governance / 治理 | Routing / 路由 | governance-routing（Approval Gate / 审批门禁） |
| N3 downstream handoff / 下游交接 | Keep volume work a separate skill invocation, never auto-triggered. / 保持分卷工作为独立技能调用，绝不自动触发。 | Governance / 治理 | Routing / 路由 | governance-routing |

### Step 3: Trace Insert / 第三步：Trace 插入

Node evidence for N2 at first run / 首轮运行时 N2 的节点证据:

- Trigger / 触发: bible regenerated; a go/no-go decision is required. / 圣经已再生成，需要通过/阻断决策。
- Inputs / 输入: `full_story_bible` payload plus gate policy. / `full_story_bible` 载荷加门禁策略。
- Outputs / 输出: gate status, score, route decision `can_enter_volume_strategy`. / 门禁状态、分数、路由决策 `can_enter_volume_strategy`。
- Current behavior / 当前行为: structural metrics only (counts, completeness). / 仅结构指标（计数、完整性）。
- Risk / 风险: contaminated planning data propagating into all downstream volumes. / 污染规划数据向所有下游分卷传播。
- Trace evidence / Trace 证据: none at first run — marked as initial planning. / 首轮无既有 Trace——标记为初次规划。

### Step 4: ASSESS, ROUTE, SELECT / 第四步：评估、判拓扑、查矩阵

- N2: governance + routing -> governance-routing -> named pattern Approval Gate / 审批门禁. / N2：治理 + 路由 -> governance-routing -> 命名模式审批门禁。
- N1: reasoning + hierarchy -> reasoning-hierarchy is an extension candidate; it was applied as the hypothesis "Narrative Decomposition Ladder / 叙事分解层级" and logged as evidence, not added to the catalog — naming requires repeated workflow evidence per `extension-rules.md`. / N1：推理 + 层级 -> reasoning-hierarchy 为扩展候选；按假设"叙事分解层级"应用并记录为证据，未加入目录——依 `extension-rules.md`，命名需要反复的工作流证据。

### Step 5: First Run Outcome / 第五步：首轮结果

Output 1801 passed the structural gate: `macro_quality_gate.status=passed`, `score=100`, `can_enter_volume_strategy=true`; recorded as a success entry in `patterns/governance/trace.md`. / 产物 1801 通过结构门：`macro_quality_gate.status=passed`、`score=100`、`can_enter_volume_strategy=true`；作为成功记录写入 `patterns/governance/trace.md`。

### Step 6: Failure Discovery / 第六步：失败发现

A later semantic check found unbound cross-project terms (such as `熵岸`, `熵潮`) inside the passed output. Structural pass did not mean semantic validity. Problem type: weak-governance / 治理薄弱; the escape class is a structural-pass-semantic-fail gate escape (see the Gate Sufficiency Rule / 门禁充分性规则 in `patterns/governance/governance-routing.md`). Output 1801 was marked `superseded`; active evidence reverted to output 1447. / 后续语义检查在已通过产物中发现未绑定跨作品术语（如 `熵岸`、`熵潮`）。结构通过不等于语义有效。问题类型：治理薄弱；逃逸类别为"结构通过-语义失败"的门禁逃逸（见 `patterns/governance/governance-routing.md` 的门禁充分性规则）。产物 1801 被标记 `superseded`；生效证据回退到产物 1447。

### Step 7: Adjustment / 第七步：调整

- Added a `semantic_consistency_gate` companion to `macro_quality_gate` and `volume_density_gate`, blocking unbound project-specific terms before downstream routing. / 在 `macro_quality_gate` 与 `volume_density_gate` 中加入 `semantic_consistency_gate` 配套门，在下游路由前阻断未绑定项目专有词。
- Made fallback planning defaults project-aware, validated against project title, premise, constraints, and bound resources. / 将兜底规划默认值改为项目感知，并与项目标题、前提、约束和绑定资源比对校验。
- Changed `latest_stage_output` to skip unusable statuses such as `superseded` — a memory-governance fix so stale evidence cannot be recalled as current. / 修改 `latest_stage_output` 跳过 `superseded` 等不可用状态——记忆治理修复，防止过期证据被当作当前证据召回。

### Step 8: Verification / 第八步：验证

Outputs 1803 (macro) and 1804 (volume density) passed both structural and semantic gates; regression tests assert superseded outputs are skipped and unbound terms are blocked. / 产物 1803（宏观）与 1804（分卷密度）同时通过结构门和语义门；回归测试断言已废弃产物被跳过、未绑定术语被阻断。

### Step 9: Trace Update / 第九步：追踪更新

Three entries each (initial, correction, repair) were appended to `patterns/governance/trace.md` and `patterns/reasoning/trace.md`. The correction entry is first-class content: it records the reversal, not only the success. / `patterns/governance/trace.md` 与 `patterns/reasoning/trace.md` 各追加三条记录（初始、更正、修复）。更正记录是一等内容：它记录了推翻，而不只是成功。

### Law Readings For This Case / 本案例定律解读

- Law 2 / 定律 2: the gate was chosen from what the pipeline may do (route a bible into all downstream volumes), not from what it usually does. / 门禁依据管线被允许做什么（将圣经路由进所有下游分卷）选择，而非它通常做什么。
- Law 3 / 定律 3: a contaminated bible propagating downstream costs far more than a blocked rerun, so the repaired gate biases toward blocking on the expensive direction. / 污染圣经向下游传播的代价远高于一次被阻断的重跑，因此修复后的门禁偏向在昂贵方向阻断。
- Law 5 / 定律 5: `score=100` was meaningless without a semantic dimension — gate criteria had to be re-derived from local project evidence. / 缺少语义维度时 `score=100` 毫无意义——门禁判据必须由本地项目证据重推。

## Takeaways / 要点

- Pair every structural gate with a semantic consistency companion; track structural-pass-semantic-fail escapes in `patterns/governance/governance-routing-observability.md`. / 每个结构门都要配语义一致性检查；在 `patterns/governance/governance-routing-observability.md` 中追踪"结构通过-语义失败"逃逸。
- Extension candidates accumulate trace evidence instead of premature names; the reasoning-hierarchy hypothesis stays a candidate until it recurs. / 扩展候选靠 Trace 证据积累而非提前命名；reasoning-hierarchy 假设在反复出现前保持候选状态。
- Superseding bad evidence is part of memory governance: recall paths must skip unusable statuses. / 废弃错误证据是记忆治理的一部分：召回路径必须跳过不可用状态。
- The pipeline is re-runnable because every step left artifacts: EIR nodes, gate records, trace entries, and regression tests. / 管线可重跑，因为每一步都留下产物：EIR 节点、门禁记录、追踪条目和回归测试。
