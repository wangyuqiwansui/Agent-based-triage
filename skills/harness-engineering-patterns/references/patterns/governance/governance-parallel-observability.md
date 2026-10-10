# Progressive Commitment / 渐进承诺 Observability Metrics / 可观测性指标

Cell / 交织点: governance-parallel / 治理 x 并行
Capability / 能力: Governance / 治理
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-parallel.md](governance-parallel.md)

## Probe Contract and Scope / 探针契约与范围

This card selects metrics for the topology; the [module metric catalog / 模块指标目录](../../governance-observability-probes.md#metric-catalog) owns their full definitions. Read the [shared contract / 共享契约](../../governance-contract.md) for event identities, source quality, and patch acceptance. / 本卡选择拓扑所需指标，完整定义以模块指标目录为准；事件身份、来源质量及补丁采纳遵循共享契约。

This is a specification-only attachment for `CELL_GOVERNANCE_PARALLEL; PATTERN_0048`, not an installed probe or proof that the existing runtime speaks `GOV_BOUNDARY_OBS`. Keep permission, dispatch, and verified business outcome separate; a Trace or passed structural check supplies no business authorization. / 这是该现有单元的规范级挂载，不是已部署探针，也不证明既有运行时已实现 `GOV_BOUNDARY_OBS`。分开记录许可、派发及核实业务结果；Trace 或结构检查通过不授予业务权限。

| Metric selection / 指标选择 | Topology-specific interpretation / 拓扑口径 | Required independent evidence / 必要独立证据 |
| --- | --- | --- |
| 指07–08 | Peak confirmed consumption + pending reservation + unknown occupancy, and verified admissions exceeding the then-current cap. / 已确认消耗＋待执行预留＋未知占用峰值，以及超过当时上限的已核实准入次数。 | Authoritative shared parent/subject ledger; same unit and window, mutually exclusive buckets. / 权威共享父级或主体账本；单位和窗口相同，三类占用互斥。 |
| 指16 | Promotions with scoped outcomes, observation window, anomaly review and valid approval ÷ all promotions. / 具备场景结果、观察窗、异常审查及有效批准的晋升数 ÷ 全部晋升数。 | Authorization inventory joined to every required branch verdict and promotion evidence. / 授权清单关联全部必要分支裁定及晋级证据。 |
| 指18 | Business audit completeness also requires the versioned merge decision and all applicable checks. / 业务审计链完整性还须包含版本化汇合决定及全部适用检查。 | Dispatch/results and explicit required-check roster, including failures and timeouts. / 派发与结果，以及含失败和超时的显式必要检查清单。 |
| 指32 | Measure authorized, verified first-attempt business completion separately from check-pass and promotion rates. / 将获合法授权且核实的首次业务完成率与检查通过率、晋级率分开。 | Independently valid due requests, proposal versions, attempts and business verification. / 独立有效的到期需求、提案版本、尝试及业务核验。 |

### Measurement and Control Boundary / 统计与控制边界

- Report population, numerator, denominator, time window, units, source references, quality state, and unresolved items. Missing reliable denominators or review truth means `unknown`; a known empty applicable population means `not_applicable`, never 100%. / 报告总体、分子、分母、窗口、单位、来源引用、质量状态及未决项；可靠分母或复核真值缺失记为 `unknown`，已知无适用样本记为 `not_applicable`，不能记为 100%。
- Deduplicate by tenant and immutable event identity; isolate same-ID/different-content conflicts. Do not remove failed, unknown, or overdue items merely to improve ratios; retain pending ages alongside completed latency distributions. / 按租户及不可变事件身份去重，同标识异内容须隔离冲突；不得为提高比例删除失败、未知或到期未决项，完成时延之外还须保留待处理年龄。
- A probe may read authorized sources, append verified observations, and propose controls. Only an authorized execution service can approve, dispatch, settle, stop, or compensate; an `observation_enrichment` patch never mutates those truths. / 探针可读取获准来源、追加核验观测及提出控制建议；只有有权执行服务能批准、派发、结算、停止或补偿，`observation_enrichment` 补丁不能修改这些真值。
- An optional probe outage does not automatically block the workflow. Execution maintains its local controls and minimum audit; missing mandatory evidence or controls is handled by the configured policy for the affected action. / 可选探针故障不自动阻断工作流；执行侧维持本地控制和最小审计，必要证据或控制缺失时按配置策略处理受影响动作。

Acceptance / 验收: 执验09–10、15、24. See the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These references define expected cases; report an actual run only with its inputs and evidence. / 这些引用定义预期用例；只有具备实际输入和证据才能报告用例已执行。

## Dedicated Progressive Commitment Probes / 渐进承诺专用探针

Use the [13-node probe pipeline](../../progressive-commitment-observability-probes.md#probe-steps), [20 specialized checks](../../progressive-commitment-observability-probes.md#specialized-probes), [114 source metric definitions](../../progressive-commitment-observability-probes.md#metric-catalog), [measurement clarifications](../../progressive-commitment-observability-probes.md#interpretation) and [shared contract](../../progressive-commitment-contract.md). They extend this existing card without changing its identity, source provenance or maturity. / 读取 13 节点探针、20 项专项检查、114 项来源指标、统计澄清及共享契约；扩展现有卡片，不改变身份、原始来源或成熟度。

Audit both task-stage progression and cross-run authority. Credential coverage requires an independent inventory of actual effects; stable batch hashes also require fresh failure watermarks; revocation propagation requires the full gateway roster and pending ages. Distinguish post-fence dispatch from pre-fence effects settling later, and conditional business success from terminal-result coverage. / 同时审计任务阶段和跨运行权限；凭证覆盖须独立实际效果清单，稳定批次摘要还须最新失败水位，吊销传播须完整执行点清单及待处理年龄。区分围栏后派发与围栏前效果迟后结算，分开条件业务成功率和终态覆盖率。

Source alias `PROBE_GOVERNANCE_0003` is not a new runtime probe registration. The [31 source probe acceptance cases](../../progressive-commitment-observability-probes.md#acceptance) remain unexecuted until an adopting implementation supplies fixture and result evidence. The metrics below retain topology diagnostics; do not silently alias them to a source metric with a different denominator or outcome definition. / 来源探针别名不新增运行时注册；31 项来源探针验收须待采用方提供样例与结果证据。下方指标保留拓扑诊断，不能静默映射为分母或结果定义不同的来源指标。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Progressive Commitment / 渐进承诺 improves the workflow after selection or application. / 使用以下指标观察 Progressive Commitment / 渐进承诺 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `check_independence` (sampled audit that parallel checks used separate evidence and owners), `promotion_regret_rate` (promotions later rolled back or causing incidents), and `ladder_catch_locality` (failures caught at dry-run or sandbox rather than production levels — higher is the ladder working). / `check_independence`（并行检查使用独立证据与独立负责人的抽样审计）、`promotion_regret_rate`（事后被回退或引发事故的晋级比例）、`ladder_catch_locality`（失败在干跑或沙箱层而非生产层被拦截的比例——越高说明阶梯在起作用）。
- 时延指标 / Latency Metrics: `per_level_gate_latency` (parallel check wall-time versus the serial-review baseline), `ladder_climb_time` (dry-run to full production), and soak-window duration per level. / `per_level_gate_latency`（并行检查墙钟时间对比串行评审基线）、`ladder_climb_time`（干跑到全量生产的总时长）、每层浸泡窗口时长。
- 成本指标 / Cost Metrics: parallel check compute per level, environment maintenance cost (sandbox, canary), and full-blast incident cost avoided by low-level catches. / 每层并行检查计算成本、环境维护成本（沙箱、金丝雀）、低层拦截所避免的全量事故成本。
- 风险指标 / Risk Metrics: `level_skip_count` (entries without the prior level's merged pass, `FAIL_0005`), `silent_check_drop_count` (failed or timed-out checks absent from the commitment decision, `FAIL_0013`), `unapproved_promotion_count` (promotions without `GOV_0001` approval), and untested-rollback share per level. / `level_skip_count`（未持上一层合并通过即进入的次数，`FAIL_0005`）、`silent_check_drop_count`（承诺决定中缺席的失败或超时检查数，`FAIL_0013`）、`unapproved_promotion_count`（未经 `GOV_0001` 审批的晋级数）、每层回退预案未经演练的占比。
- Trace 指标 / Trace Metrics: `commitment_decision_completeness` (every required check's verdict present in each promotion record, per `GOV_0002`), climb-chain traceability (production state traceable through all levels), and rollback event closure rate. / `commitment_decision_completeness`（每次晋级记录含全部所需检查裁定的完整率，按 `GOV_0002`）、攀升链可追溯性（生产状态可回溯全部层级）、回退事件闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert on any `level_skip_count` or `silent_check_drop_count` above zero — a skip means the ladder is not the only path to production (`FAIL_0005`), a silent drop means the merge is lying about what passed (`FAIL_0013`). / `level_skip_count` 或 `silent_check_drop_count` 一旦大于零即告警——跳层说明阶梯不是通往生产的唯一路径（`FAIL_0005`），静默丢弃说明合并在谎报通过情况（`FAIL_0013`）。
- Block promotion when any required check failed, timed out, or has not reported, when the soak window is unfinished, or when the next level's rollback action is untested; remain at the authorized scope, repair or hand off, or perform separately authorized compensation; permission downgrade alone is not business rollback. / 任一所需检查失败、超时或未上报，浸泡窗口未走完，或下一层回退动作未经演练时阻断晋级；可留在已授权范围修复或移交，或执行另行授权的补偿；权限降级本身不是业务回滚。
