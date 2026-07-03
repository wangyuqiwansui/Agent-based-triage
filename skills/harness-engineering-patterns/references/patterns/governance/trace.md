# Governance Trace / 治理追踪

## Trace / 追踪

Use this file to record what happened after a governance pattern was applied to a workflow. / 使用本文档记录治理模式应用到工作流之后发生了什么。

Boundary note / 边界说明: entries carry pattern-level lessons; application-specific identifiers inside them (such as Novel Studio stage-output ids) are evidence pointers frozen at write time, not current application state. During Trace Insert, reuse the lesson, but verify any concrete id or status against the application's own data before acting on it. / 记录承载模式层经验；其中的应用专属标识（如 Novel Studio 阶段产物编号）是写入时刻冻结的证据指针，不代表应用当前状态。Trace 插入时可复用经验，但任何具体编号或状态在采用前必须与应用自身数据核对。

## Usage Log / 使用日志

Add new entries below this template. / 在此模板下方追加新记录。

### Entry Template / 记录模板

- Date / 日期:
- Workflow / 工作流:
- Cell / 交织点:
- Pattern Used / 使用模式:
- Before / 使用前:
- Adjustment / 调整:
- Outcome / 结果:
- Evidence / 证据:
- Follow-up / 后续:
- Owner / 负责人:

## Entries / 记录

### 2026-07-03 / 2026-07-03

- Date / 日期: 2026-07-03
- Workflow / 工作流: Gate Novel Studio project-10 full-story bible before later volume work. / 对 Novel Studio project-10 全本故事圣经执行后续分卷前的质量门禁。
- Cell / 交织点: governance-routing / 治理 x 路由
- Pattern Used / 使用模式: Approval Gate / 审批门禁
- Before / 使用前: The workflow needed evidence that the regenerated story bible could safely enter later `volume_strategy`, without automatically running the downstream stage. / 工作流需要证明新生成的故事圣经可以安全进入后续 `volume_strategy`，但不得自动执行下游阶段。
- Adjustment / 调整: Used `macro_quality_gate` as the route decision: passed allows later volume work, blocked would stop and report blockers. / 使用 `macro_quality_gate` 作为路由决策：passed 才允许后续分卷，blocked 则停止并报告阻断项。
- Outcome / 结果: Output id 1801 produced `macro_quality_gate.status=passed`, `score=100`, and `can_enter_volume_strategy=true`; no blocking issues were reported. / 产物 1801 得到 `macro_quality_gate.status=passed`、`score=100`、`can_enter_volume_strategy=true`，没有阻断项。
- Evidence / 证据: Stage output 1801 data contains `macro_quality_gate`, its metrics, and `harness_patterns` including `governance-routing / Approval Gate`. / 阶段产物 1801 的 data 包含 `macro_quality_gate`、指标，以及包含 `governance-routing / Approval Gate` 的 `harness_patterns`。
- Follow-up / 后续: Keep the Skill boundary explicit: downstream volume work should be invoked through `$novel-volume-cards`, not by this story-bible run. / 继续保持 Skill 边界明确：后续分卷应通过 `$novel-volume-cards` 单独调用，而不是由本次故事圣经重跑自动触发。
- Owner / 负责人: Codex

### 2026-07-03 Correction / 2026-07-03 更正

- Date / 日期: 2026-07-03
- Workflow / 工作流: Correct project-10 macro gate evidence after semantic mismatch was found. / 发现语义错配后，更正 project-10 宏观门证据。
- Cell / 交织点: governance-routing / 治理 x 路由
- Pattern Used / 使用模式: Approval Gate plus semantic consistency guard / 审批门禁加语义一致性保护
- Before / 使用前: Output 1801 passed structural `macro_quality_gate`, but the gate did not detect alien-story terms. / 产物 1801 通过结构性 `macro_quality_gate`，但该门禁没有发现异作品术语。
- Adjustment / 调整: Output 1801 was marked `superseded`; `latest_stage_output` was changed to skip unusable statuses such as `superseded`. / 已将 1801 标记为 `superseded`；`latest_stage_output` 已改为跳过 `superseded` 等不可用状态。
- Outcome / 结果: The active macro evidence for project-10 is output 1447, not 1801. / project-10 当前生效宏观证据是产物 1447，不是 1801。
- Evidence / 证据: Regression tests verify superseded outputs are skipped and unbound sci-fi terms are blocked from story_macro outputs. / 回归测试验证已废弃产物会被跳过，且未绑定科幻词不会进入 story_macro 输出。
- Follow-up / 后续: Treat structural gates as insufficient without a project-semantic consistency check. / 没有项目语义一致性检查时，不应仅凭结构门通过判定产物可用。
- Owner / 负责人: Codex

### 2026-07-03 Repair / 2026-07-03 修复

- Date / 日期: 2026-07-03
- Workflow / 工作流: Repair Novel Studio project-10 planning gates after cross-project contamination. / 修复跨作品污染后的 Novel Studio project-10 规划门禁。
- Cell / 交织点: governance-routing / 治理 x 路由
- Pattern Used / 使用模式: Approval Gate with semantic consistency gate / 审批门禁加语义一致性门
- Before / 使用前: Structural gates could pass outputs containing unbound alien-story terms. / 结构门可能放行包含未绑定异作品术语的产物。
- Adjustment / 调整: Added `semantic_consistency_gate` to `macro_quality_gate` and `volume_density_gate`, blocking unbound project-specific terms before downstream routing. / 在 `macro_quality_gate` 与 `volume_density_gate` 中加入 `semantic_consistency_gate`，在下游路由前阻断未绑定项目专有词。
- Outcome / 结果: Repaired project-10 outputs 1803 and 1804 both passed semantic gates and structural gates. / 修复后的 project-10 产物 1803 与 1804 同时通过语义门和结构门。
- Evidence / 证据: Output 1803 has `macro_quality_gate.semantic_consistency_gate.status=passed`; output 1804 has `volume_density_gate.semantic_consistency_gate.status=passed`; forbidden-term scan returned no hits. / 产物 1803 的 `macro_quality_gate.semantic_consistency_gate.status=passed`；产物 1804 的 `volume_density_gate.semantic_consistency_gate.status=passed`；禁用词扫描无命中。
- Follow-up / 后续: Keep semantic consistency as a required companion to structural gate metrics for future planning stages. / 后续规划阶段必须将语义一致性作为结构指标的配套门禁。
- Owner / 负责人: Codex
