# Progressive Commitment / 渐进承诺 Observability Metrics / 可观测性指标

Cell / 交织点: governance-parallel / 治理 x 并行
Capability / 能力: Governance / 治理
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-parallel.md](governance-parallel.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Progressive Commitment / 渐进承诺 improves the workflow after selection or application. / 使用以下指标观察 Progressive Commitment / 渐进承诺 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `check_independence` (sampled audit that parallel checks used separate evidence and owners), `promotion_regret_rate` (promotions later rolled back or causing incidents), and `ladder_catch_locality` (failures caught at dry-run or sandbox rather than production levels — higher is the ladder working). / `check_independence`（并行检查使用独立证据与独立负责人的抽样审计）、`promotion_regret_rate`（事后被回退或引发事故的晋级比例）、`ladder_catch_locality`（失败在干跑或沙箱层而非生产层被拦截的比例——越高说明阶梯在起作用）。
- 时延指标 / Latency Metrics: `per_level_gate_latency` (parallel check wall-time versus the serial-review baseline), `ladder_climb_time` (dry-run to full production), and soak-window duration per level. / `per_level_gate_latency`（并行检查墙钟时间对比串行评审基线）、`ladder_climb_time`（干跑到全量生产的总时长）、每层浸泡窗口时长。
- 成本指标 / Cost Metrics: parallel check compute per level, environment maintenance cost (sandbox, canary), and full-blast incident cost avoided by low-level catches. / 每层并行检查计算成本、环境维护成本（沙箱、金丝雀）、低层拦截所避免的全量事故成本。
- 风险指标 / Risk Metrics: `level_skip_count` (entries without the prior level's merged pass, `FAIL_0005`), `silent_check_drop_count` (failed or timed-out checks absent from the commitment decision, `FAIL_0013`), `unapproved_promotion_count` (promotions without `GOV_0001` approval), and untested-rollback share per level. / `level_skip_count`（未持上一层合并通过即进入的次数，`FAIL_0005`）、`silent_check_drop_count`（承诺决定中缺席的失败或超时检查数，`FAIL_0013`）、`unapproved_promotion_count`（未经 `GOV_0001` 审批的晋级数）、每层回退预案未经演练的占比。
- Trace 指标 / Trace Metrics: `commitment_decision_completeness` (every required check's verdict present in each promotion record, per `GOV_0002`), climb-chain traceability (production state traceable through all levels), and rollback event closure rate. / `commitment_decision_completeness`（每次晋级记录含全部所需检查裁定的完整率，按 `GOV_0002`）、攀升链可追溯性（生产状态可回溯全部层级）、回退事件闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert on any `level_skip_count` or `silent_check_drop_count` above zero — a skip means the ladder is not the only path to production (`FAIL_0005`), a silent drop means the merge is lying about what passed (`FAIL_0013`). / `level_skip_count` 或 `silent_check_drop_count` 一旦大于零即告警——跳层说明阶梯不是通往生产的唯一路径（`FAIL_0005`），静默丢弃说明合并在谎报通过情况（`FAIL_0013`）。
- Block promotion when any required check failed, timed out, or has not reported, when the soak window is unfinished, or when the next level's rollback action is untested; the only legal continuations are fixing at the current level or rolling back one level. / 任一所需检查失败、超时或未上报，浸泡窗口未走完，或下一层回退动作未经演练时阻断晋级；唯一合法的继续方式是在当前层修复或回退一层。
