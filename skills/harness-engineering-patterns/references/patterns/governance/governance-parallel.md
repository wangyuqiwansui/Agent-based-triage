# Progressive Commitment / 渐进承诺

Cell / 交织点: governance-parallel / 治理 x 并行
Capability / 能力: Governance / 治理
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Progressive Commitment separates a single task's commitment ladder from cross-task capability authority. Each task stage merges all independent required checks; wider authority additionally requires a locked, verified evidence batch, scoped approval and a newly issued credential. Incidents freeze affected authority and fence further dispatch. / 渐进承诺分开单次任务承诺阶梯与跨任务能力权限。各任务阶段汇合全部独立必要检查；权限扩大还须锁定核验证据批次、范围审批及新凭证签发。事故冻结相关权限并围栏阻断后续派发。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Parallel / 并行 (Parallel / 并行).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Governance / 治理 x Parallel / 并行 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Governance / 治理 x Parallel / 并行 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: All-or-nothing commitment forces one gate to bear the entire blast radius: work jumps from proposal straight to full production on a single serial review, independent concerns (policy, security, compliance, quality, budget) queue behind each other adding latency, and when the one gate misjudges there is no intermediate level to stop at or roll back to. / 全有或全无的承诺让一道门背负全部爆炸半径：工作凭一次串行评审从提案直跳全量生产，独立关切（策略、安全、合规、质量、预算）互相排队徒增时延，而那道门一旦误判，既没有可停留的中间层也没有可回退的落点。
- 架构方案 / Architectural Solution: Define a commitment ladder with bounded side-effect scope per level — dry-run, sandbox apply (per `GOV_0003`), limited production, full production; at each level run that level's required checks as independent parallel branches and merge them into one explicit commitment decision (no silent dropping of failed checks); promotion happens only when all required checks pass and is approved per `GOV_0001`, failure blocks further promotion; scope can be reduced under policy, while external rollback requires separate verified compensation, and every verdict and promotion is recorded per `GOV_0002`. / 定义每层副作用范围受限的承诺阶梯——干跑、沙箱执行（按 `GOV_0003`）、受限生产、全量生产；每层将该层所需检查作为独立并行分支运行，并汇成一个显式承诺决定（失败检查绝不静默丢弃）；只有全部所需检查通过才晋级并按 `GOV_0001` 审批，失败阻断继续晋级；可按策略缩减范围，外部回滚另需经核验的独立补偿，每次裁定与晋级按 `GOV_0002` 入账。
- 工程权衡 / Engineering Trade-offs: Parallel checks cut gate latency versus serial review and the ladder converts one big irreversible bet into several small reversible ones, but each level adds promotion overhead and environment maintenance — trivial reversible changes do not need four levels, and check independence must be real or the parallel verdicts are one opinion wearing five hats. / 并行检查相比串行评审削减门控时延，阶梯把一次不可逆的大赌注换成多次可回退的小赌注，但每层都增加晋级开销与环境维护成本——琐碎可逆变更不需要四层，且检查独立性必须真实，否则并行裁定只是一个意见戴五顶帽子。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when commitments should be staged and checked in parallel with execution evidence. / 当承诺需要分阶段并与执行证据并行检查时使用。

### Commitment Ladder / 承诺阶梯

These four rows are **task stages**, not the five cross-task authority levels. Passing a stage stays within the current credential; authority promotion follows the dedicated evidence-and-issuance contract below. / 以下四行是**任务阶段**，不是跨任务的五级权限。阶段通过仍受当前凭证约束；权限晋级遵循下方专用证据与签发契约。

| Stage / 阶段 | Allowed Side-Effect Scope / 允许副作用范围 | Required Parallel Checks / 所需并行检查 | Advancement Criteria / 推进条件 | Rollback Action / 回退动作 |
| --- | --- | --- | --- | --- |
| Dry-run / 干跑 | None — plan and diff only. / 无——仅计划与差异。 | Policy, schema, budget estimate. / 策略、schema、预算估计。 | All checks pass; diff reviewed. / 检查全过、差异经评审。 | Discard the plan. / 丢弃计划。 |
| Sandbox apply / 沙箱执行 | Isolated environment per `GOV_0003`. / 按 `GOV_0003` 的隔离环境。 | Security, quality, behavior-vs-diff match. / 安全、质量、行为与差异吻合。 | All checks pass; approval per `GOV_0001`. / 检查全过、按 `GOV_0001` 审批。 | Reset the sandbox. / 重置沙箱。 |
| Limited production / 受限生产 | Bounded slice (canary, subset, cap). / 受限切片（金丝雀、子集、上限）。 | Compliance, live metrics vs sandbox baseline, incident watch. / 合规、线上指标对照沙箱基线、事故监视。 | All checks pass over the soak window. / 浸泡窗口内检查全过。 | Revert the slice; incidents feed back. / 回滚切片；事故回灌检查。 |
| Full production / 全量生产 | Full approved scope, bounded by current credentials and shared hard limits. / 完整已批准范围，仍受当前凭证及共享硬上限约束。 | All configured prior stages green, live combined gates and applicable final approval per `GOV_0001`. / 配置内前序阶段通过、即时组合闸及适用终审。 | Task terminal; no automatic authority promotion. / 任务终态，不自动晋升长期权限。 | Separately authorized and verified rollback/compensation. / 另行授权并核验回滚或补偿。 |

Ladder rules / 阶梯规则:

- No level skipping: entering a level without the previous level's merged pass verdict is a permission bypass (`FAIL_0005`); the ladder is the only path to full production for covered change classes. / 不可跳层：未持有上一层合并通过裁定即进入下一层属权限绕过（`FAIL_0005`）；对覆盖的变更类，阶梯是通往全量生产的唯一路径。
- The merge is explicit: every check's verdict appears in the commitment decision, failed or timed-out required checks block promotion — a checklist that only shows passes is an aggregation failure (`FAIL_0013`). / 合并必须显式：每个检查的裁定都出现在承诺决定中，失败或超时的必要检查阻断晋级——只展示通过项的清单就是聚合失败（`FAIL_0013`）。
- Complementary cells / 互补格: the Approval Gate (governance-routing) gates single actions by risk; this ladder governs how far a change's commitment may climb over time; Blast Radius Control (governance-hierarchy) bounds where effects land in space. / 审批门禁（governance-routing）按风险管单个动作；本阶梯管一项变更的承诺随时间能爬多高；爆炸半径控制（governance-hierarchy）管副作用在空间上落到哪里。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Progressive Commitment / 渐进承诺.
- 诊断用途 / Diagnostic Use: Use when commitments should be staged and checked in parallel with execution evidence. / 当承诺需要分阶段并与执行证据并行检查时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 验证测试、治理审查 / Verification, governance review.
- 当前症状 / Current Symptoms: Changes jump from proposal to full production on one serial review; governance checks queue behind each other and gate latency dominates delivery; a misjudged release has no intermediate level to stop at, so every incident is a full-blast incident. / 变更凭一次串行评审从提案直跳全量生产；治理检查互相排队、门控时延主导交付；误判的发布没有可停留的中间层，每次事故都是全量事故。
- 适配信号 / Fit Signals: 多个独立治理检查可以并行执行后汇总 / Multiple independent governance checks can run in parallel and merge.
- 调整方向 / Adjustment Direction: Replace the single all-or-nothing gate with a commitment ladder whose levels each run independent parallel checks merged into explicit promotion decisions. / 用承诺阶梯取代全有或全无的单一门控，每层独立并行检查、显式合并成晋级决定。
- 修改方式 / How To Modify: 1) Classify change types by reversibility × impact and decide which climb the full ladder (trivial reversible classes may use a preapproved shorter profile). 2) Define each level's side-effect scope, required checks, and soak window. 3) Make checks genuinely independent (separate evidence, separate owners). 4) Wire the explicit merge: all verdicts visible, any required-check failure blocks promotion, promotions approved per `GOV_0001`. 5) Define and test each level's rollback action; record everything per `GOV_0002`. / 1）按可逆性 × 影响面给变更分类，决定哪些爬完整阶梯（琐碎可逆类可使用预先批准的短阶梯配置）；2）定义每层副作用范围、所需检查与浸泡窗口；3）保证检查真正独立（独立证据、独立负责人）；4）接显式合并：全部裁定可见、任一必要检查失败即阻断晋级、晋级按 `GOV_0001` 审批；5）定义并演练每层回退动作；全程按 `GOV_0002` 入账。
- 输入 / Inputs: Change request with reversibility and impact class, ladder definition (levels, scopes, checks), independent check owners and evidence sources, sandbox and canary environments, rollback recipes. / 带可逆性与影响等级的变更请求、阶梯定义（层级、范围、检查）、独立检查负责人与证据源、沙箱与金丝雀环境、回滚配方。
- 输出 / Outputs: Per-level merged commitment decisions with all check verdicts, promotion and approval events, soak-window evidence, rollback events with outcomes. / 每层带全部检查裁定的合并承诺决定、晋级与审批事件、浸泡窗口证据、带结果的回退事件。
- 风险与治理 / Risks & Governance: Level skipping is `FAIL_0005` — make the ladder the only path to production for covered classes and alert on out-of-ladder entries; the merge point is a `FAIL_0013` aggregation bottleneck — failed and timed-out checks must block visibly, never drop silently; promotions are approved per `GOV_0001`, low levels stay inside sandbox boundaries per `GOV_0003`, and all verdicts and promotions are recorded per `GOV_0002` so any production state traces back through its full climb. / 跳层是 `FAIL_0005`——让阶梯成为覆盖类通往生产的唯一路径，阶梯外进入即告警；合并点是 `FAIL_0013` 聚合瓶颈——失败与超时检查必须可见地阻断，绝不静默丢弃；晋级按 `GOV_0001` 审批，低层按 `GOV_0003` 留在沙箱边界内，全部裁定与晋级按 `GOV_0002` 入账，任何生产状态都能回溯其完整攀升过程。

### Module Attachment / 模块工程挂载

Identity / 身份: `CELL_GOVERNANCE_PARALLEL; PATTERN_0048`. Existing names and maturity stay unchanged. / 保持现有名称与成熟度不变。

At each configured commitment level, gather independent checks against the same proposal and policy snapshot; all required verdicts must be accounted for before promotion. / 每个配置的承诺层级均针对相同提案与策略快照汇聚独立检查；晋级前必须交代全部必要裁定。

Read the maintained [execution flow / 执行流程](../../governance-execution-flow.md#execution-steps) (执02、06–08、11、14–15) and [shared contract / 共享契约](../../governance-contract.md). These are specification-only engineering extensions from the supplied lesson-36 documents; this card does not provide a dedicated production runtime or make an existing runtime implement `GOV_BOUNDARY_OBS`. / 阅读维护版执行流程与共享契约。这些内容是用户第 36 讲资料的规范级工程扩展；本卡不提供专用生产运行时，也不表示既有运行时已实现 `GOV_BOUNDARY_OBS`。

| Attachment point / 落点 | Required behavior and evidence / 必要行为与证据 |
| --- | --- |
| Fork / 分支拆分 | Give each branch an identity, required/optional classification, evidence contract, deadline, and shared parent budget reference. / 为各分支指定标识、必要或可选分类、证据契约、截止时间及共享父预算引用。 |
| Merge / 汇合 | Preserve failed, missing, and timed-out required checks; never majority-vote them away. Bind the promotion decision to the proposal version and every required result. / 保留失败、缺失及超时的必要检查，不能用多数票消除；晋级决定绑定提案版本及全部必要结果。 |
| Budget and promotion / 预算与晋级 | All effectful branches share authoritative aggregate accounts with atomic reservation. Promotion needs scenario-specific results, an observation window, anomaly review, and applicable independent approval. / 所有产生副作用的分支共享权威聚合账户并原子预留；晋级需要场景特定结果、观察窗、异常审查及适用的独立批准。 |

Boundary / 边界: Passing parallel checks grants neither a new credential nor a full parent budget per branch. A preconfigured shorter ladder is a different approved change class, not an ad hoc skip. Separate permission downgrade from external compensation: reducing a level cannot erase effects already produced. / 并行检查通过不自动签发凭证，也不为每个分支复制完整父预算。预配置短阶梯属于另一获准变更类，不是临时跳层。权限降级与外部补偿分开，降低层级不能抹去已有副作用。

Acceptance references / 验收引用: 执验09–10、15、24; use the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These are expected checks, not claims that production tests passed. / 这些是待验证的预期，不代表生产测试已通过。

Metric references / 指标引用: 指07–08、16、18、32; definitions, denominators, and unavailable states live in the [metric catalog / 指标目录](../../governance-observability-probes.md#metric-catalog). Permission and verified business success are separate results. / 口径、分母及不可用状态由指标目录统一定义；合规许可与已核实业务成功分开记录。

### Capability Authority Engineering / 能力权限工程化

Use the dedicated [15 execution nodes](../../progressive-commitment-execution-flow.md#execution-steps), [independent probes](../../progressive-commitment-observability-probes.md) and [shared contract](../../progressive-commitment-contract.md). Retain `PATTERN_0048`, `CELL_GOVERNANCE_PARALLEL` and draft maturity. Source aliases `PATTERN_GOVERNANCE_0003` and `PROBE_GOVERNANCE_0003`, including their chain/loop coordinates, are reconciled in the [source map](../../progressive-commitment-source-map.json); sequential transitions and feedback do not replace required parallel checks or register another pattern. / 读取专用 15 节点执行、独立探针及共享契约，保留现有编号、治理并行坐标与草稿成熟度。来源映射解释附件编号及链式循环坐标；顺序迁移和反馈不替代必要并行检查，也不新建模式。

| Concern / 关注点 | Engineering rule / 工程规则 |
| --- | --- |
| Two clocks / 两只钟表 | Task rehearsal/canary advances only that task; `observe → suggest → shadow → limited → autonomous` requires scoped grants between runs. Freeze overrides any level. / 任务演练金丝雀只推进本任务；观察至自主的跨运行晋级须范围授权，冻结优先于任何等级。 |
| Specific authority / 具体权限 | Bind subject/model/capability/tool/policy versions, tenant/environment, resources, data, limits, validity and human exceptions; check at every actual dispatch. / 绑定主体模型能力工具策略版本、租户环境资源数据额度有效期及人工例外，每次实际派发复查。 |
| Evidence and issuance / 证据与签发 | Unique trial cohorts, trusted business verification, required slice/risk coverage, immutable batch and fresh failure watermarks; atomically issue successor and replace predecessor under current revision/epoch. / 独立试验组、受信业务核验、必要切片风险覆盖、不可变批次及最新失败水位；按当前修订代次原子签新替旧。 |
| Incident control / 事故控制 | Fence new affected dispatch, track gateway acknowledgments and in-flight unknowns; recovery uses a new baseline and approval. Downgrade cannot undo external effects. / 围栏阻断新派发、跟踪执行点确认及在途未知；恢复使用新基线批准，降级不能撤销既有外部效果。 |
| Observation / 观测 | Probe findings and verified enrichment remain observations; no direct authority mutation, inferred success or retroactive authorization. / 探针发现及核验补全仍属观察，不直接改权、不推断成功、不追溯授权。 |

This is specification-only: 29 source execution cases plus 8 added race/boundary cases are unexecuted expectations. Existing Skill routing credentials are not these action-authority credentials. / 本扩展仅为规范：29 个来源执行用例及 8 个补充并发边界场景均为未执行预期；已有 Skill 路由凭证不等于这里的行动权限凭证。

Observability Metrics File / 可观测性指标文件: [governance-parallel-observability.md](governance-parallel-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
