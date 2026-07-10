# Progressive Commitment / 渐进承诺

Cell / 交织点: governance-parallel / 治理 x 并行
Capability / 能力: Governance / 治理
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Progressive Commitment climbs a commitment ladder — dry-run, sandbox apply, limited production, full production — where each promotion requires all of that level's independent parallel checks (policy, security, compliance, quality, budget) to pass and merge into one explicit commitment decision. / 渐进承诺沿承诺阶梯攀升——干跑、沙箱执行、受限生产、全量生产——每次晋级都要求该层全部独立并行检查（策略、安全、合规、质量、预算）通过并汇成一个显式承诺决定。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Parallel / 并行 (Parallel / 并行).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Governance / 治理 x Parallel / 并行 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Governance / 治理 x Parallel / 并行 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: All-or-nothing commitment forces one gate to bear the entire blast radius: work jumps from proposal straight to full production on a single serial review, independent concerns (policy, security, compliance, quality, budget) queue behind each other adding latency, and when the one gate misjudges there is no intermediate level to stop at or roll back to. / 全有或全无的承诺让一道门背负全部爆炸半径：工作凭一次串行评审从提案直跳全量生产，独立关切（策略、安全、合规、质量、预算）互相排队徒增时延，而那道门一旦误判，既没有可停留的中间层也没有可回退的落点。
- 架构方案 / Architectural Solution: Define a commitment ladder with bounded side-effect scope per level — dry-run, sandbox apply (per `GOV_0003`), limited production, full production; at each level run that level's required checks as independent parallel branches and merge them into one explicit commitment decision (no silent dropping of failed checks); promotion happens only when all required checks pass and is approved per `GOV_0001`, failure stops at the current level and can roll back one level, and every verdict and promotion is recorded per `GOV_0002`. / 定义每层副作用范围受限的承诺阶梯——干跑、沙箱执行（按 `GOV_0003`）、受限生产、全量生产；每层将该层所需检查作为独立并行分支运行，并汇成一个显式承诺决定（失败检查绝不静默丢弃）；只有全部所需检查通过才晋级并按 `GOV_0001` 审批，失败停在当前层并可回退一层，每次裁定与晋级按 `GOV_0002` 入账。
- 工程权衡 / Engineering Trade-offs: Parallel checks cut gate latency versus serial review and the ladder converts one big irreversible bet into several small reversible ones, but each level adds promotion overhead and environment maintenance — trivial reversible changes do not need four levels, and check independence must be real or the parallel verdicts are one opinion wearing five hats. / 并行检查相比串行评审削减门控时延，阶梯把一次不可逆的大赌注换成多次可回退的小赌注，但每层都增加晋级开销与环境维护成本——琐碎可逆变更不需要四层，且检查独立性必须真实，否则并行裁定只是一个意见戴五顶帽子。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when commitments should be staged and checked in parallel with execution evidence. / 当承诺需要分阶段并与执行证据并行检查时使用。

### Commitment Ladder / 承诺阶梯

| Level / 层级 | Allowed Side-Effect Scope / 允许副作用范围 | Required Parallel Checks / 所需并行检查 | Promotion Criteria / 晋级标准 | Rollback Action / 回退动作 |
| --- | --- | --- | --- | --- |
| Dry-run / 干跑 | None — plan and diff only. / 无——仅计划与差异。 | Policy, schema, budget estimate. / 策略、schema、预算估计。 | All checks pass; diff reviewed. / 检查全过、差异经评审。 | Discard the plan. / 丢弃计划。 |
| Sandbox apply / 沙箱执行 | Isolated environment per `GOV_0003`. / 按 `GOV_0003` 的隔离环境。 | Security, quality, behavior-vs-diff match. / 安全、质量、行为与差异吻合。 | All checks pass; approval per `GOV_0001`. / 检查全过、按 `GOV_0001` 审批。 | Reset the sandbox. / 重置沙箱。 |
| Limited production / 受限生产 | Bounded slice (canary, subset, cap). / 受限切片（金丝雀、子集、上限）。 | Compliance, live metrics vs sandbox baseline, incident watch. / 合规、线上指标对照沙箱基线、事故监视。 | All checks pass over the soak window. / 浸泡窗口内检查全过。 | Revert the slice; incidents feed back. / 回滚切片；事故回灌检查。 |
| Full production / 全量生产 | Full blast radius. / 全量影响面。 | All prior levels green plus final approval per `GOV_0001`. / 前序各层全绿加按 `GOV_0001` 终审。 | Terminal level. / 终态层。 | Tested full rollback plan. / 经过验证的全量回滚预案。 |

Ladder rules / 阶梯规则:

- No level skipping: entering a level without the previous level's merged pass verdict is a permission bypass (`FAIL_0005`); the ladder is the only path to full production for covered change classes. / 不可跳层：未持有上一层合并通过裁定即进入下一层属权限绕过（`FAIL_0005`）；对覆盖的变更类，阶梯是通往全量生产的唯一路径。
- The merge is explicit: every check's verdict appears in the commitment decision, failed or timed-out checks block promotion — a checklist that only shows passes is an aggregation failure (`FAIL_0013`). / 合并必须显式：每个检查的裁定都出现在承诺决定中，失败或超时的检查阻断晋级——只展示通过项的清单就是聚合失败（`FAIL_0013`）。
- Complementary cells / 互补格: the Approval Gate (governance-routing) gates single actions by risk; this ladder governs how far a change's commitment may climb over time; Blast Radius Control (governance-hierarchy) bounds where effects land in space. / 审批门禁（governance-routing）按风险管单个动作；本阶梯管一项变更的承诺随时间能爬多高；爆炸半径控制（governance-hierarchy）管副作用在空间上落到哪里。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Progressive Commitment / 渐进承诺.
- 诊断用途 / Diagnostic Use: Use when commitments should be staged and checked in parallel with execution evidence. / 当承诺需要分阶段并与执行证据并行检查时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 验证测试、治理审查 / Verification, governance review.
- 当前症状 / Current Symptoms: Changes jump from proposal to full production on one serial review; governance checks queue behind each other and gate latency dominates delivery; a misjudged release has no intermediate level to stop at, so every incident is a full-blast incident. / 变更凭一次串行评审从提案直跳全量生产；治理检查互相排队、门控时延主导交付；误判的发布没有可停留的中间层，每次事故都是全量事故。
- 适配信号 / Fit Signals: 多个独立治理检查可以并行执行后汇总 / Multiple independent governance checks can run in parallel and merge.
- 调整方向 / Adjustment Direction: Replace the single all-or-nothing gate with a commitment ladder whose levels each run independent parallel checks merged into explicit promotion decisions. / 用承诺阶梯取代全有或全无的单一门控，每层独立并行检查、显式合并成晋级决定。
- 修改方式 / How To Modify: 1) Classify change types by reversibility × impact and decide which climb the full ladder (trivial reversible classes may start higher). 2) Define each level's side-effect scope, required checks, and soak window. 3) Make checks genuinely independent (separate evidence, separate owners). 4) Wire the explicit merge: all verdicts visible, any failure blocks, promotions approved per `GOV_0001`. 5) Define and test each level's rollback action; record everything per `GOV_0002`. / 1）按可逆性 × 影响面给变更分类，决定哪些爬完整阶梯（琐碎可逆类可从较高层起步）；2）定义每层副作用范围、所需检查与浸泡窗口；3）保证检查真正独立（独立证据、独立负责人）；4）接显式合并：全部裁定可见、任一失败即阻断、晋级按 `GOV_0001` 审批；5）定义并演练每层回退动作；全程按 `GOV_0002` 入账。
- 输入 / Inputs: Change request with reversibility and impact class, ladder definition (levels, scopes, checks), independent check owners and evidence sources, sandbox and canary environments, rollback recipes. / 带可逆性与影响等级的变更请求、阶梯定义（层级、范围、检查）、独立检查负责人与证据源、沙箱与金丝雀环境、回滚配方。
- 输出 / Outputs: Per-level merged commitment decisions with all check verdicts, promotion and approval events, soak-window evidence, rollback events with outcomes. / 每层带全部检查裁定的合并承诺决定、晋级与审批事件、浸泡窗口证据、带结果的回退事件。
- 风险与治理 / Risks & Governance: Level skipping is `FAIL_0005` — make the ladder the only path to production for covered classes and alert on out-of-ladder entries; the merge point is a `FAIL_0013` aggregation bottleneck — failed and timed-out checks must block visibly, never drop silently; promotions are approved per `GOV_0001`, low levels stay inside sandbox boundaries per `GOV_0003`, and all verdicts and promotions are recorded per `GOV_0002` so any production state traces back through its full climb. / 跳层是 `FAIL_0005`——让阶梯成为覆盖类通往生产的唯一路径，阶梯外进入即告警；合并点是 `FAIL_0013` 聚合瓶颈——失败与超时检查必须可见地阻断，绝不静默丢弃；晋级按 `GOV_0001` 审批，低层按 `GOV_0003` 留在沙箱边界内，全部裁定与晋级按 `GOV_0002` 入账，任何生产状态都能回溯其完整攀升过程。

Observability Metrics File / 可观测性指标文件: [governance-parallel-observability.md](governance-parallel-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
