# Evaluation And Governance / 评估与治理

Use this file before finalizing quality, evidence, governance, risk, or verification sections for a workflow or Harness analysis. / 在最终确定工作流或 Harness 分析的质量、证据、治理、风险或验证章节前使用本文档。

## Quality Evaluation / 质量评估

Score qualitatively when exact metrics are unavailable. / 没有精确指标时使用定性评分。

| Dimension / 维度 | Question / 问题 | Metric / 指标 |
| --- | --- | --- |
| Coverage / 覆盖度 | Does the analysis cover main loop, context, tools, state, and governance? / 是否覆盖主循环、上下文、工具、状态和治理？ | `coverage_score` |
| Accuracy / 准确度 | Are cognition and topology mappings reasonable? / 认知与拓扑映射是否合理？ | `mapping_accuracy` |
| Evidence / 证据性 | Do claims have source, test, doc, config, log, or trace support? / 判断是否有源码、测试、文档、配置、日志或 Trace 支撑？ | `evidence_ratio` |
| Reuse / 可复用性 | Can the pattern work across workflows? / 模式能否跨流程复用？ | `reuse_score` |
| Skill Readiness / Skill 化程度 | Can it become an executable or reusable Skill? / 是否能转成可执行或可复用 Skill？ | `skill_readiness` |
| Governance / 治理完整度 | Are permission, sandbox, audit, and rollback clear? / 权限、沙箱、审计和回滚是否明确？ | `governance_score` |
| Evaluability / 可评估性 | Are tests, probes, or evaluation cases defined? / 是否定义测试、探针或评估用例？ | `evaluation_score` |

## Scoring Anchors / 评分锚点

Score each dimension 0-100 using these bands. Anchors make scores comparable across analyses and reviewers; without them a score is an opinion. / 每个维度按 0-100 打分并使用以下分段。锚点让分数在不同分析和评审者之间可比；没有锚点的分数只是观点。

| Band / 分段 | Label / 标签 | Criteria / 判据 |
| --- | --- | --- |
| 90-100 | Verified / 已验证 | Claim holds with direct evidence (source, tests, runtime records) and has been checked against at least one counterexample or failure path. / 判断有直接证据（源码、测试、运行记录）支撑，且至少对照过一个反例或失败路径。 |
| 70-89 | Grounded / 有依据 | Claim has direct evidence but no counterexample check; gaps are named. / 判断有直接证据但未做反例检查；缺口已被点名。 |
| 50-69 | Plausible / 貌似合理 | Claim rests on descriptive evidence (docs, README, config) only. / 判断仅依赖描述性证据（文档、README、配置）。 |
| 25-49 | Asserted / 仅断言 | Claim is stated without evidence references; treat as hypothesis. / 判断未引用证据；视为假说。 |
| 0-24 | Unknown / 未知 | The dimension was not analyzed. / 该维度未被分析。 |

Anchor rules / 锚点规则:

- A structural pass alone caps the score at 89: full marks require a semantic or behavioral check on top of structure (repository evidence: a structurally perfect `score=100` gate output was later superseded for semantic contamination — see `example-compilation.md`). / 仅结构通过最高 89 分：满分要求在结构之上叠加语义或行为检查（仓库实证：结构满分 `score=100` 的门禁产物后来因语义污染被废弃——见 `example-compilation.md`）。
- Do not average across bands to hide a weak dimension; report the lowest-scoring dimension alongside the aggregate. / 不要用跨维度平均掩盖薄弱维度；聚合分旁必须报告最低分维度。
- Re-derive band thresholds locally when a domain has stricter norms (Law 5 in `diagnosis-method.md`). / 当领域有更严格规范时，按本地证据重推分段阈值（见 `diagnosis-method.md` 定律 5）。

## Evidence Priority / 证据优先级

Prefer direct evidence over descriptive evidence. / 优先直接证据，而不是描述性证据。

```text
source code > tests > official docs > config > runtime logs > README
源码 > 测试 > 官方文档 > 配置 > 运行日志 > README
```

Unsupported claims should be marked as assumptions, hypotheses, or verification tasks. / 无证据判断应标记为假设、假说或验证任务。

## Governance Checklist / 治理检查清单

Ask these questions for any Agent Harness or workflow. / 对任何 Agent Harness 或工作流都检查以下问题。

- What can the Agent see? / Agent 能看什么？
- What can the Agent remember? / Agent 能记什么？
- Which tools can the Agent call? / Agent 能调用什么工具？
- Which external state can the Agent modify? / Agent 能修改什么外部状态？
- Which actions require human confirmation? / 哪些动作需要人类确认？
- Which actions must run in a sandbox? / 哪些动作必须进入沙箱？
- Which results must be recorded? / 哪些结果必须入账？
- Can failures roll back or recover? / 失败后能否回滚或恢复？
- Can the process be audited or replayed? / 过程能否审计或回放？
- Are permissions scoped by identity, channel, environment, or task type? / 权限是否按身份、channel、环境或任务类型区分？

## Governance Rules / 治理规则

| Rule ID / 规则 ID | Rule / 规则 | Applies To / 适用坐标 |
| --- | --- | --- |
| `GOV_0001` | High-risk actions need approval or policy checks. / 高风险动作需要审批或策略检查。 | `COG_ACTION__TOP_ROUTING`, `COG_GOVERNANCE__TOP_ROUTING` |
| `GOV_0002` | Tool results must be written to state, event log, or conversation history. / 工具执行结果必须记录到 state、event log 或 conversation history。 | `COG_ACTION__TOP_CHAIN`, `COG_MEMORY__TOP_CHAIN` |
| `GOV_0003` | Code execution, shell commands, file writes, and network calls should run inside controlled runtime or sandbox boundaries. / 代码执行、命令运行、文件写入和网络调用应在受控 runtime 或 sandbox 边界内运行。 | `COG_GOVERNANCE__TOP_ORCHESTRATION` |

## Evaluation Output / 评估输出

For runtime action governance, use the [execution flow](governance-execution-flow.md), [independent probes](governance-observability-probes.md) and [shared exchange contract](governance-contract.md). These extend the existing governance patterns with specifications, without changing their IDs or declaring deployment. Separate permission, budget reservation, dispatch and verified business outcome; source-backed observation repair never grants action authority. / 运行时行动治理使用执行流程、独立探针与共享交互契约；这些规格完善已有治理模式，不改变编号，也不宣称已部署。分别记录许可、预算预留、派发和已核验业务结果；有来源的观测修复不授予行动权。

Use an independent authoritative inventory for metric denominators. Unknown denominators remain unknown; known empty applicable populations are not applicable, never 100%. Report original evidence completeness separately from retrospective reconstruction, and retain pending or unknown results in their defined populations. See the [36 metric definitions](governance-observability-probes.md#metric-catalog). / 指标分母来自独立权威清单；未知分母仍为未知，已知无适用样本标为不适用，不能记为 100%。原始证据完整性与事后还原程度分报，待处理或未知结果按指标口径保留在总体中；详见 36 项指标定义。

Use this seven-dimension shape when a user needs a scored result. Every dimension declares how it is judged, which direction is better, which evidence is used, and which observation window the score covers. / 当用户需要评分结果时使用以下七维结构。每个维度都声明判断方式、优劣方向、证据来源和评分覆盖的观察窗口。

```yaml
evaluation_id: EVAL_0001
target_type: pattern | skill | workflow | harness_source
target_ref: ANALYSIS_20260710_0001
status: draft

criteria:
  coverage:
    rubric: "required control-plane areas covered / 必需控制面区域覆盖率"
    direction: higher_is_better
    evidence_sources: []
    observation_window: current_analysis
    score: null
    confidence: null
    notes: ""
  mapping_accuracy:
    rubric: "mappings supported by boundaries and counterexamples / 映射有边界与反例支撑"
    direction: higher_is_better
    evidence_sources: []
    observation_window: current_analysis
    score: null
    confidence: null
    notes: ""
  evidence:
    rubric: "claims with fresh resolvable evidence / 具备新鲜可解析证据的判断比例"
    direction: higher_is_better
    evidence_sources: []
    observation_window: current_analysis
    score: null
    confidence: null
    notes: ""
  reuse:
    rubric: "independent workflows supported without copying local parameters / 不复制本地参数时可支持的独立工作流"
    direction: higher_is_better
    evidence_sources: []
    observation_window: observed_cases
    score: null
    confidence: null
    notes: ""
  skill_readiness:
    rubric: "bounded input, output, tools, failure handling, tests, and risk / 输入输出工具失败处理测试与风险边界完整度"
    direction: higher_is_better
    evidence_sources: []
    observation_window: current_pattern_version
    score: null
    confidence: null
    notes: ""
  governance:
    rubric: "permission, sandbox, audit, rollback, retention, and ownership coverage / 权限沙箱审计回滚留存与归属覆盖度"
    direction: higher_is_better
    evidence_sources: []
    observation_window: current_analysis
    score: null
    confidence: null
    notes: ""
  evaluability:
    rubric: "executable tests, probes, thresholds, and failure-path checks / 可执行测试探针阈值与失败路径检查完整度"
    direction: higher_is_better
    evidence_sources: []
    observation_window: current_pattern_version
    score: null
    confidence: null
    notes: ""

lowest_dimension: null
aggregate_score: null
aggregate_method: "report mean and lowest dimension separately / 分别报告均值与最低维度"
open_verification_tasks: []
```

Metric metadata rules / 指标元数据规则：

- `rubric` may be a formula when measurable or a bounded scoring rule when qualitative. / 可量化时 `rubric` 使用公式；定性时使用有边界的评分规则。
- `direction` is `higher_is_better`, `lower_is_better`, or `target_range`. / `direction` 使用 `higher_is_better`、`lower_is_better` 或 `target_range`。
- `evidence_sources` contains resolvable EIR evidence IDs or external references. / `evidence_sources` 包含可解析的 EIR 证据 ID 或外部引用。
- `observation_window` prevents scores from silently mixing versions or time periods. / `observation_window` 防止评分静默混合不同版本或时间区间。
- `confidence` is `high`, `medium`, or `low` and does not substitute for a score. / `confidence` 使用 `high`、`medium` 或 `low`，不能替代分数。

## Observability evidence boundary / 可观测性证据边界

The [Observability Harness supplement](observability-contract.md) is `specification_only`. Its [source map](observability-source-map.json) preserves 13 stages, 45 probes, 50 metric definitions and 15 source acceptance scenarios; [12 additional boundary scenarios](observability-probes.md#acceptance) cover completion, recovery and measurement integrity. All 27 scenarios remain `not_executed` until an adopting host records input, expected/actual result and independently verifiable evidence. Asset/hash/link checks neither execute these scenarios nor promote pattern maturity. / 可观测性扩展仅为规格；来源映射保留 13 阶段、45 探针、50 指标及 15 来源验收场景，另补 12 个补全恢复统计边界场景。27 个场景在接入宿主提供输入、预期实际结果及独立证据前均为未执行；资产哈希链接检查不执行场景，也不晋升模式成熟度。

Require authority-confirmed outcomes, scoped authenticated correlation, reviewed labels for diagnostic accuracy, independent expected-event populations, qualified denominators and isolated replay. A healthy collector, completed run, high coverage score, accepted observation patch or generated artifact does not by itself prove a successful business outcome. / 要求权威确认结果、范围认证关联、诊断准确性的复核标签、独立预期事件总体、合格分母及隔离重放；采集健康、运行结束、高覆盖分、补丁采纳或工件生成本身均不证明业务成功。

## Pattern Combination Evidence Boundary / 模式组合证据边界

The [composition contract](pattern-combination-contract.md) and [source map](pattern-combination-source-map.json) retain 11 stages, 14 probes, 54 formulas and 20 source cases, with seven additional host-integration scenarios. All business scenarios remain unexecuted. Evaluate never-started mandatory branches, shared-budget races, unknown external effects, late/duplicate/conflicting events, cross-task enrichment, empty or sampled populations and optional probe failure. Document validation is not evidence of a working scheduler, calculator or business acceptance. / 组合契约与来源映射保留 11 阶段、14 探针、54 公式及 20 来源场景，另含七项宿主接入场景，业务场景均未执行。应评估未启动必需分支、共享预算竞争、未知效果、迟到重复冲突事件、跨任务补数、空或采样总体及可选探针故障；文档校验不证明调度器、计算器或业务验收已实现。

## Architecture Evolution Evidence Boundary / 架构演化证据边界

The [evolution contract](architecture-evolution-contract.md) requires a frozen baseline/candidate pair, evaluation population, rules, thresholds and evidence window. Incomparable inputs, missing required evidence or immature outcomes yield an inconclusive evaluation; a high observed success rate cannot replace acceptance coverage or critical-error checks. An updated candidate invalidates earlier version-bound validation and release authority. / 演化契约要求冻结基线候选对、评价总体、规则、阈值与证据窗口。输入不可比、缺必需证据或结果未成熟时，验证结论为证据不足；高观测成功率不能替代验收覆盖及关键错误检查。候选更新使先前版本绑定的验证与发布权限失效。

The [source-backed specification](architecture-evolution-source-map.json) and AET scenarios are `specification_only` / `not_executed`. Local asset, provenance and navigation checks do not establish a working deployment gate, successful rollback or business acceptance. / 有来源的规格及 AET 场景分别标为仅规格与未执行；本地资产、来源和导航检查不证明发布门已实现、回滚成功或业务验收通过。

## Progressive Commitment Evidence Boundary / 渐进承诺证据边界

The [progressive commitment contract](progressive-commitment-contract.md) is specification-only. Its [source map](progressive-commitment-source-map.json) binds 15 execution nodes, 13 probe nodes, 20 specialized probes, 114 metric definitions and 60 source cases; 8 additional execution cases target concurrency and authority boundaries. None is a passed business test until an adopting implementation supplies input, expected/actual outcome and independent evidence. Source/hash/navigation validation does not promote pattern maturity or prove enforcement. / 渐进承诺契约仅为规范；来源映射绑定 15 执行节点、13 探针节点、20 专项探针、114 指标及 60 来源场景，另有 8 项并发权限边界场景。在采用实现提供输入、预期实际结果及独立证据前，均不能称为业务测试通过。来源哈希导航校验不晋升模式成熟度，也不证明控制已生效。

Evaluate distinct task progression, evidence cohort uniqueness/diversity/freshness, authority revision and failure-watermark races, atomic predecessor replacement, gateway revocation coverage, unknown effects and post-incident recovery. Report conditional success with terminal coverage; do not confuse a stable digest, a high aggregate score, a verified observation patch or a Skill routing qualification with an action grant. / 评估独立任务推进、证据组唯一多样新鲜度、权限修订与失败水位竞争、原子新旧替代、执行点吊销覆盖、未知效果及事故后恢复。条件成功率同时报告终态覆盖；稳定摘要、高汇总分、核验补全及 Skill 路由资格均不能当作行动授权。
