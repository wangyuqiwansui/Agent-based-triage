# Experience Replay / 经验回放 Observability Metrics / 可观测性指标

Cell / 交织点: reflection-hierarchy / 反思 x 层级
Capability / 能力: Reflection / 反思
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reflection-hierarchy.md](reflection-hierarchy.md)

Shared Probe Contract / 共享探针契约: use [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md), especially `PROBE_0016` through `PROBE_0023`, with the round observation pack defined by the governed [Reflection Execution Flow / 反思执行流程](../../reflection-execution-flow.md). / 使用共享工作流可观测性探针，重点使用 `PROBE_0016` 至 `PROBE_0023`，并采用受治理反思执行流程定义的轮次观察包。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Experience Replay / 经验回放 improves the workflow after selection or application. / 使用以下指标观察 Experience Replay / 经验回放 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `lesson_adoption_rate` (distilled rules and checklists actually applied in later runs), `repeat_incident_rate` (same failure class recurring after its lesson shipped — the pattern's core success measure, falling is good), and `replay_conclusion_accuracy` (sampled audit of replay conclusions against raw records). / `lesson_adoption_rate`（提炼的规则与清单在后续运行中被实际应用的比例）、`repeat_incident_rate`（教训发布后同类失败的复发率——本模式核心成效指标，下降为好）、`replay_conclusion_accuracy`（回放结论对照原始记录的抽样审计准确率）。
- 时延指标 / Latency Metrics: `replay_turnaround` per tier (trigger to lesson artifact), lesson-to-adoption lag (artifact shipped to first application), and review latency for version-level rule changes. / 各层 `replay_turnaround`（触发到教训产物的耗时）、教训采纳滞后（产物发布到首次应用）、版本级规则变更的评审时延。
- 成本指标 / Cost Metrics: review effort per tier per cycle, `replay_roi` (repeat-incident cost avoided versus replay effort spent), and context tokens consumed by injected lessons per run. / 每层每周期的复盘投入、`replay_roi`（避免的复发事故成本对比回放投入）、每次运行中注入教训消耗的上下文 token。
- 风险指标 / Risk Metrics: `record_gap_rate` (replays run over incomplete records, watch `FAIL_0010`), `lesson_dump_size` (unfiltered lesson volume entering context, watch `FAIL_0001`), `tier_skip_count` (replays consuming raw records two levels down), and unreviewed version-level rule changes (violates `GOV_0001`). / `record_gap_rate`（在不完整记录上运行的回放比例，对应 `FAIL_0010`）、`lesson_dump_size`（未过滤进入上下文的教训体量，对应 `FAIL_0001`）、`tier_skip_count`（越两级消费原始记录的回放数）、未经评审的版本级规则变更数（违反 `GOV_0001`）。
- Trace 指标 / Trace Metrics: `replay_provenance_completeness` (each lesson traceable to its source records, per `GOV_0002`), gap-disclosure coverage in replay reports, and lesson-artifact closure rate (proposed rules either adopted or explicitly rejected). / `replay_provenance_completeness`（每条教训可追溯到源记录的完整率，按 `GOV_0002`）、回放报告中缺口披露的覆盖率、教训产物闭环率（提议规则要么采纳要么显式否决）。

### Default Gate Suggestions / 默认门控建议

- Alert when `repeat_incident_rate` fails to fall after lessons ship or `record_gap_rate` climbs — the former means replay produces artifacts nobody applies, the latter means conclusions are being drawn from unreliable records (`FAIL_0010`). / 教训发布后 `repeat_incident_rate` 不降或 `record_gap_rate` 上升即告警——前者说明回放产物无人应用，后者说明结论正建立在不可靠记录上（`FAIL_0010`）。
- Block a replay conclusion from becoming a binding rule when its source records have undisclosed gaps or the version-level change skipped `GOV_0001` review; return it as a provisional observation instead. / 源记录存在未披露缺口或版本级变更跳过 `GOV_0001` 评审时，阻断回放结论成为约束性规则；将其退回为临时观察。
