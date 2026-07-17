# Parallel Exploration / 并行探索 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-parallel / 推理 x 并行
Capability / 能力: Reasoning / 推理
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-parallel.md](reasoning-parallel.md)
Shared Probe Suite / 共享探针套件: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)
Metric Registry / 指标注册表: [`metric_registry.json`](../../../runtime/metric_registry.json)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Parallel Exploration / 并行探索 improves the workflow after selection or application. / 使用以下指标观察 Parallel Exploration / 并行探索 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `synthesis_fidelity` (sampled audit of whether the synthesis decision reflects branch evidence), `branch_diversity` (distinct conclusions divided by branch count), and `minority_preservation_rate` (losing findings preserved with sources). / `synthesis_fidelity`（抽样审计综合决定是否反映分支证据）、`branch_diversity`（不同结论数除以分支数）、`minority_preservation_rate`（带来源保留的落选发现比例）。
- 时延指标 / Latency Metrics: `slowest_branch_latency` (the gather step waits for the slowest branch), synthesis-step latency, and end-to-end latency versus single-path baseline. / `slowest_branch_latency`（汇聚步骤等待最慢分支的时间）、综合步骤时延、端到端时延对比单路径基线。
- 成本指标 / Cost Metrics: `branch_token_multiplier` (actual spend versus single-path baseline, expected ~n×), pruning savings (tokens saved by early-pruned branches), and cost per adopted alternative. / `branch_token_multiplier`（实际花费对比单路径基线，预期约 n 倍）、剪枝节省（提前剪枝分支省下的 token）、每个被采纳替代方案的成本。
- 风险指标 / Risk Metrics: `branch_convergence_rate` (branches reaching identical conclusions — high values suggest context leakage and n× cost for zero diversity), `silent_drop_count` (branch findings absent from the synthesis with no elimination reason, the `FAIL_0013` logic), and unpruned hopeless-branch spend. / `branch_convergence_rate`（分支得出相同结论的比例——过高提示上下文泄漏、n 倍成本零多样性）、`silent_drop_count`（综合中缺席且无排除原因的分支发现数，即 `FAIL_0013` 逻辑）、未被剪枝的无望分支花费。
- Trace 指标 / Trace Metrics: `branch_record_completeness` (per-branch conclusion plus evidence recorded, per `GOV_0002`), elimination-reason coverage for pruned and losing branches, and synthesis rationale record rate. / `branch_record_completeness`（逐分支结论与证据的记录完整率，按 `GOV_0002`）、剪枝与落选分支的排除原因覆盖率、综合理由记录率。

### Required Probe Coverage / 必需探针覆盖

Enable task identity and parent linkage (`PROBE_0001`), contract completeness (`PROBE_0002`), route decision and switch reasons (`PROBE_0003`), budget and resources (`PROBE_0004`), step closure (`PROBE_0005`), evidence chain (`PROBE_0006`), tool and action (`PROBE_0007`) when branches act, parallel path (`PROBE_0008`), drift (`PROBE_0010`), validation (`PROBE_0011`), stop and escalation (`PROBE_0012`), outcome (`PROBE_0013`) for adoption or correctness claims, privacy and governance (`PROBE_0014`), and probe self-health (`PROBE_0015`). / 启用任务身份与父子关联、契约完整性、路由决定与换路原因、预算与资源、步骤闭环、证据链、工具与动作（分支执行动作时）、并行路径、漂移、验证、停止升级、结果回接（用于采纳或正确性判断）、隐私治理和探针自健康探针。

Define material difference over hypotheses, evidence, rule or model version, or plan—not wording. Calculate `material_candidate_difference`, winner-validation rate, path convergence, and invalid-parallel cost under one versioned comparison contract. Preserve losing paths, conflicting evidence, and elimination reasons. / 实质差异应定义在假设、证据、规则或模型版本、计划上，而不是措辞上。用同一版本化比较契约计算候选实质差异率、胜出路径验证率、路径收敛率和无效并行成本。保留落选路径、冲突证据和淘汰原因。

Bucket metrics by scene, risk, candidate count, isolation method, comparison-contract version, validator, model, tool, and outcome availability. A missing candidate result is not a failed or losing candidate. / 指标按场景、风险、候选数量、隔离方式、比较契约版本、验证器、模型、工具和后验可用性分桶。候选结果缺失不等于失败或落选。

### Default Gate Suggestions / 默认门控建议

- Alert when gate-eligible `material_candidate_difference` falls below its owned, bucketed threshold while `max_budget_utilization` rises; planned branch-convergence diagnostics cannot drive a gate until implemented. / 当可用于门控的 `material_candidate_difference` 低于有负责人且按桶配置的阈值，同时 `max_budget_utilization` 上升时告警；规划中的分支收敛诊断在实现前不得驱动门控。
- Block synthesis sign-off until the synthesis owner has accessed every branch's evidence and every dropped finding carries an elimination reason. / 综合责任方未查阅全部分支证据、或存在无排除原因的被丢弃发现时，阻断综合签署。
