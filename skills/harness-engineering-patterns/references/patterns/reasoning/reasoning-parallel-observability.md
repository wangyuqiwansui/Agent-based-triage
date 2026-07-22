# Parallel Exploration / 并行探索 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-parallel / 推理 x 并行
Capability / 能力: Reasoning / 推理
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-parallel.md](reasoning-parallel.md)
Executable Factory / 可执行工厂: [Reasoning Parallel Factory / 推理并行工厂](../../reasoning-parallel-factory.md)
Event Projector / 事件投影器: [`reasoning_parallel_projection.py`](../../../runtime/reasoning_parallel_projection.py)
Lease Scheduler / 租约调度器: [`reasoning_parallel_scheduler.py`](../../../runtime/reasoning_parallel_scheduler.py)
Transactional Outbox / 事务型发件箱: [`reasoning_parallel_outbox.py`](../../../runtime/reasoning_parallel_outbox.py)
PostgreSQL Outbox / PostgreSQL 发件箱: [`reasoning_parallel_postgres_outbox.py`](../../../runtime/reasoning_parallel_postgres_outbox.py)
Shared Probe Suite / 共享探针套件: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)
Metric Registry / 指标注册表: [`metric_registry.json`](../../../runtime/metric_registry.json)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Parallel Exploration / 并行探索 improves the workflow after selection or application. / 使用以下指标观察 Parallel Exploration / 并行探索 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: implemented diagnostic `branch_diversity` (distinct immutable candidate bindings divided by completed candidate paths); planned `synthesis_fidelity` and `minority_preservation_rate` remain design candidates only. / 已实现诊断指标 `branch_diversity`（不同不可变候选绑定数除以完成候选路径数）；规划中的 `synthesis_fidelity` 与 `minority_preservation_rate` 仍只可作为设计候选。
- 时延指标 / Latency Metrics: `slowest_branch_latency` (the gather step waits for the slowest branch), synthesis-step latency, lease-expiry-to-reacquisition handoff latency, dispatch-created-to-first-claim latency, and claim-to-ack latency. / `slowest_branch_latency`（汇聚步骤等待最慢分支的时间）、综合步骤时延、租约过期至重新获取的接管时延、分派创建至首次领取时延，以及领取至确认时延。
- 成本指标 / Cost Metrics: `branch_token_multiplier` (actual spend versus single-path baseline, expected ~n×), pruning savings, cost per adopted alternative, and outbox `delivery_attempt_count` segmented by dispatch terminal status. / `branch_token_multiplier`（实际花费对比单路径基线，预期约 n 倍）、剪枝节省、每个被采纳替代方案的成本，以及按分派终态分段的发件箱 `delivery_attempt_count`。
- 风险指标 / Risk Metrics: implemented diagnostic `candidate_completion_rate` distinguishes planned paths with explicit terminal records from missing results; `branch_diversity` exposes identical candidate bindings and false diversity. Monitor superseded-result rejection, stale delivery-token rejection, delivery retry amplification, claimed-row expiry, and `dead_lettered` count as operational signals. Planned `branch_convergence_rate`, `silent_drop_count`, and unpruned hopeless-branch spend remain design candidates only. / 已实现诊断指标 `candidate_completion_rate` 区分具有显式终态记录的计划路径与缺失结果；`branch_diversity` 暴露相同候选绑定和伪多样。把已取代结果拒绝、陈旧交付令牌拒绝、交付重试放大、领取记录过期和 `dead_lettered` 数量作为运行信号监控。规划中的 `branch_convergence_rate`、`silent_drop_count` 与未剪枝无望分支消耗仍只可作为设计候选。
- Trace 指标 / Trace Metrics: implemented diagnostic `branch_record_completeness` measures explicit terminal records containing status, path binding, budget, evidence or elimination reason, and common assessment. Correlate `dispatch_id`, `lease_id`, path-local `fencing_token`, `delivery_token`, `delivery_attempt_count`, worker, owner, timestamps, and terminal status without storing credentials or private reasoning. Elimination-reason coverage and synthesis-rationale audit remain mandatory records even where no standalone formula exists. / 已实现诊断指标 `branch_record_completeness` 衡量显式终态记录是否含状态、路径绑定、预算、证据或淘汰原因及统一评估。关联 `dispatch_id`、`lease_id`、路径局部 `fencing_token`、`delivery_token`、`delivery_attempt_count`、工作者、所有者、时间戳与终态，但不得存储凭据或私密推理。即使尚无独立公式，淘汰原因覆盖与综合理由审计仍是必需记录。

### Required Probe Coverage / 必需探针覆盖

Enable task identity and parent linkage (`PROBE_0001`), contract completeness (`PROBE_0002`), route decision and switch reasons (`PROBE_0003`), budget and resources (`PROBE_0004`), step closure (`PROBE_0005`), evidence chain (`PROBE_0006`), tool and action (`PROBE_0007`) only when a future tool-enabled branch is separately authorized, parallel path (`PROBE_0008`), drift (`PROBE_0010`), validation (`PROBE_0011`), stop and escalation (`PROBE_0012`), outcome (`PROBE_0013`) for adoption or correctness claims, privacy and governance (`PROBE_0014`), and probe self-health (`PROBE_0015`). `PROBE_0008` must capture the immutable planned-path inventory, path terminal, candidate binding, common comparison-rule binding, criteria and veto results, selection, elimination reason, and each `parallel_path_updated` lease or deadline phase with worker, revision, fencing token, expiry, and plan binding. Outbox health contributes bounded status counts and total delivery attempts; rejection counters belong in the service telemetry path because rejected stale requests do not mutate the event stream. / 启用任务身份与父子关联、契约完整性、路由决定与换路原因、预算与资源、步骤闭环、证据链；仅当未来工具化分支获得独立行动授权时启用工具与动作探针；同时启用并行路径、漂移、验证、停止升级、结果回接（用于采纳或正确性判断）、隐私治理和探针自健康探针。`PROBE_0008` 必须采集不可变计划路径清单、路径终态、候选绑定、统一比较规则绑定、准则与否决结果、选择、淘汰原因，以及每条 `parallel_path_updated` 租约或截止阶段的工作者、修订、栅栏令牌、过期时间与计划绑定。发件箱健康检查提供有限的状态计数与总交付尝试数；拒绝计数属于服务遥测路径，因为被拒绝的陈旧请求不会修改事件流。

Define declared material difference over hypotheses, evidence, rule or model version, or plan—not wording. Under one versioned comparison contract, call `project_parallel_run(plan, events)` and compute implemented `candidate_completion_rate`, `branch_diversity`, and `branch_record_completeness` from its metric inputs; compute `material_candidate_difference` and `path_convergence_rate` only from their complete registered inventories. Retain the projection hash and anomalies with every published window. Preserve losing paths, conflicting evidence, minority findings, and elimination reasons. Do not publish planned metrics as observed values. / 声明的实质差异应定义在假设、证据、规则或模型版本、计划上，而不是措辞上。在同一版本化比较契约下，调用 `project_parallel_run(plan, events)`，并根据其指标输入计算已实现的 `candidate_completion_rate`、`branch_diversity` 与 `branch_record_completeness`；`material_candidate_difference` 和 `path_convergence_rate` 只能基于各自完整注册清单计算。每个发布窗口都要保留投影哈希与异常。保留落选路径、冲突证据、少数结论和淘汰原因；不得把规划中指标发布为观测值。

Treat lease `expired` as an ownership transition, not a branch terminal. Measure expiry-to-reacquisition handoff latency separately from branch completion, and alert on stale-holder renew/release/submission attempts. A branch becomes `timed_out` only when the global deadline closes it under the compiled policy. / 将租约 `expired` 视为所有权转换，而不是分支终态。租约过期到重新领取的接管时延应与分支完成时延分开度量，并对陈旧持有者的续约、释放或提交尝试告警。只有全局截止按已编译策略关闭分支时，该分支才变为 `timed_out`。

Alert on sustained delivery retry amplification, nonzero dead-letter growth, claimed rows older than their claim TTL, or stale-token rejection bursts. Keep these signals diagnostic until their inventory, window, owner, threshold, and minimum sample are registered; do not convert one crash-recovery retry into a workflow failure. / 对持续的交付重试放大、非零死信增长、超过领取 TTL 的已领取记录或陈旧令牌拒绝突增告警。在清单、窗口、负责人、阈值与最小样本注册前，这些信号只作诊断；不得把一次崩溃恢复重试转换为工作流失败。

Bucket metrics by scene, risk, candidate count, isolation method, comparison-contract version, validator, model, tool, and outcome availability. A missing candidate result is not a failed or losing candidate. / 指标按场景、风险、候选数量、隔离方式、比较契约版本、验证器、模型、工具和后验可用性分桶。候选结果缺失不等于失败或落选。

### Default Gate Suggestions / 默认门控建议

- Alert when gate-eligible `material_candidate_difference` falls below its owned, bucketed threshold while `max_budget_utilization` rises. / 当可用于门控的 `material_candidate_difference` 低于有负责人且按桶配置的阈值，同时 `max_budget_utilization` 上升时告警。
- Keep `candidate_completion_rate`, `branch_diversity`, `branch_record_completeness`, and `path_convergence_rate` diagnostic until accountable owners approve thresholds, minimum samples, drift controls, and promotion evidence. / `candidate_completion_rate`、`branch_diversity`、`branch_record_completeness` 和 `path_convergence_rate` 在责任人批准阈值、最小样本、漂移控制与晋升证据前只作诊断。
- Block synthesis sign-off until the synthesis owner has accessed every branch's evidence and every dropped finding carries an elimination reason. / 综合责任方未查阅全部分支证据、或存在无排除原因的被丢弃发现时，阻断综合签署。
