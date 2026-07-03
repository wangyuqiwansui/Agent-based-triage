# Parallel Exploration / 并行探索 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-parallel / 推理 x 并行
Capability / 能力: Reasoning / 推理
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-parallel.md](reasoning-parallel.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Parallel Exploration / 并行探索 improves the workflow after selection or application. / 使用以下指标观察 Parallel Exploration / 并行探索 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `synthesis_fidelity` (sampled audit of whether the synthesis decision reflects branch evidence), `branch_diversity` (distinct conclusions divided by branch count), and `minority_preservation_rate` (losing findings preserved with sources). / `synthesis_fidelity`（抽样审计综合决定是否反映分支证据）、`branch_diversity`（不同结论数除以分支数）、`minority_preservation_rate`（带来源保留的落选发现比例）。
- 时延指标 / Latency Metrics: `slowest_branch_latency` (the gather step waits for the slowest branch), synthesis-step latency, and end-to-end latency versus single-path baseline. / `slowest_branch_latency`（汇聚步骤等待最慢分支的时间）、综合步骤时延、端到端时延对比单路径基线。
- 成本指标 / Cost Metrics: `branch_token_multiplier` (actual spend versus single-path baseline, expected ~n×), pruning savings (tokens saved by early-pruned branches), and cost per adopted alternative. / `branch_token_multiplier`（实际花费对比单路径基线，预期约 n 倍）、剪枝节省（提前剪枝分支省下的 token）、每个被采纳替代方案的成本。
- 风险指标 / Risk Metrics: `branch_convergence_rate` (branches reaching identical conclusions — high values suggest context leakage and n× cost for zero diversity), `silent_drop_count` (branch findings absent from the synthesis with no elimination reason, the `FAIL_0013` logic), and unpruned hopeless-branch spend. / `branch_convergence_rate`（分支得出相同结论的比例——过高提示上下文泄漏、n 倍成本零多样性）、`silent_drop_count`（综合中缺席且无排除原因的分支发现数，即 `FAIL_0013` 逻辑）、未被剪枝的无望分支花费。
- Trace 指标 / Trace Metrics: `branch_record_completeness` (per-branch conclusion plus evidence recorded, per `GOV_0002`), elimination-reason coverage for pruned and losing branches, and synthesis rationale record rate. / `branch_record_completeness`（逐分支结论与证据的记录完整率，按 `GOV_0002`）、剪枝与落选分支的排除原因覆盖率、综合理由记录率。

### Default Gate Suggestions / 默认门控建议

- Alert when `branch_convergence_rate` is high or `branch_diversity` approaches 1/n — isolation is likely broken and the n× spend is buying no perspective diversity. / 当 `branch_convergence_rate` 偏高或 `branch_diversity` 接近 1/n 时告警——隔离很可能已被破坏，n 倍花费买不到视角多样性。
- Block synthesis sign-off until the synthesis owner has accessed every branch's evidence and every dropped finding carries an elimination reason. / 综合责任方未查阅全部分支证据、或存在无排除原因的被丢弃发现时，阻断综合签署。
