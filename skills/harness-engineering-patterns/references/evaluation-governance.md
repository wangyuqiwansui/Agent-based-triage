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

Use this shape when a user needs a scored result. / 当用户需要评分结果时使用此结构。

```yaml
evaluation_id: EVAL_0001
target_type: pattern | skill | workflow | harness_source
target_ref: TODO
status: draft

criteria:
  coverage:
    score: null
    notes: TODO
  evidence:
    score: null
    notes: TODO
  mapping_accuracy:
    score: null
    notes: TODO
  governance:
    score: null
    notes: TODO
  skill_readiness:
    score: null
    notes: TODO

open_verification_tasks: []
```
