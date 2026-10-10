# Extension Candidate / 扩展候选 Observability Metrics / 可观测性指标

Cell / 交织点: governance-loop / 治理 x 循环
Capability / 能力: Governance / 治理
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-loop.md](governance-loop.md)

## Probe Contract and Scope / 探针契约与范围

This card selects metrics for the topology; the [module metric catalog / 模块指标目录](../../governance-observability-probes.md#metric-catalog) owns their full definitions. Read the [shared contract / 共享契约](../../governance-contract.md) for event identities, source quality, and patch acceptance. / 本卡选择拓扑所需指标，完整定义以模块指标目录为准；事件身份、来源质量及补丁采纳遵循共享契约。

This is a specification-only attachment for `CELL_GOVERNANCE_LOOP; pattern_ref: null`, not an installed probe or proof that the existing runtime speaks `GOV_BOUNDARY_OBS`. Keep permission, dispatch, and verified business outcome separate; a Trace or passed structural check supplies no business authorization. / 这是该现有单元的规范级挂载，不是已部署探针，也不证明既有运行时已实现 `GOV_BOUNDARY_OBS`。分开记录许可、派发及核实业务结果；Trace 或结构检查通过不授予业务权限。

| Metric selection / 指标选择 | Topology-specific interpretation / 拓扑口径 | Required independent evidence / 必要独立证据 |
| --- | --- | --- |
| 指09–12 | Duplicate effects, unknown occupancy/age, and timely reconciliation closure; unresolved is never silently rewritten as failure. / 重复效果、未知占用与年龄、按期对账关闭；未解决不得静默改为失败。 | Original request/business result inventory, idempotency history and authoritative settlement ledger. / 原请求与业务结果清单、幂等历史及权威结算账本。 |
| 指17 | Longest revocation-to-confirmation delay across relevant dispatch entries, plus unconfirmed entry count. / 权威撤销到相关派发入口确认的最长延迟，并报未确认入口数。 | Fence versions and entry acknowledgements; this does not prove in-flight effects were recalled. / 围栏版本与入口确认；不证明在途副作用已经撤回。 |
| 指26–28、36 | Close gaps only after qualified receiver acknowledgement; sent patches and unacknowledged feedback remain pending. / 合格接收回执后才能关闭缺口；已发送补丁和未确认反馈仍待处理。 | Versioned requests, query budget/deadline, per-field adoption and original acceptance condition. / 版本化请求、查询预算与期限、逐字段采纳及原验收条件。 |
| 指33 | Actual call attempts ÷ logical operations invoked at least once; separate reads, writes, and legitimately new business actions. / 实际调用尝试数 ÷ 至少调用一次的逻辑操作数；读取、写入与合法新业务动作分开统计。 | Stable business/operation identity and attempt records across workers and runs. / 跨执行者和运行保持的业务、操作身份及尝试记录。 |

### Measurement and Control Boundary / 统计与控制边界

- Report population, numerator, denominator, time window, units, source references, quality state, and unresolved items. Missing reliable denominators or review truth means `unknown`; a known empty applicable population means `not_applicable`, never 100%. / 报告总体、分子、分母、窗口、单位、来源引用、质量状态及未决项；可靠分母或复核真值缺失记为 `unknown`，已知无适用样本记为 `not_applicable`，不能记为 100%。
- Deduplicate by tenant and immutable event identity; isolate same-ID/different-content conflicts. Do not remove failed, unknown, or overdue items merely to improve ratios; retain pending ages alongside completed latency distributions. / 按租户及不可变事件身份去重，同标识异内容须隔离冲突；不得为提高比例删除失败、未知或到期未决项，完成时延之外还须保留待处理年龄。
- A probe may read authorized sources, append verified observations, and propose controls. Only an authorized execution service can approve, dispatch, settle, stop, or compensate; an `observation_enrichment` patch never mutates those truths. / 探针可读取获准来源、追加核验观测及提出控制建议；只有有权执行服务能批准、派发、结算、停止或补偿，`observation_enrichment` 补丁不能修改这些真值。
- An optional probe outage does not automatically block the workflow. Execution maintains its local controls and minimum audit; missing mandatory evidence or controls is handled by the configured policy for the affected action. / 可选探针故障不自动阻断工作流；执行侧维持本地控制和最小审计，必要证据或控制缺失时按配置策略处理受影响动作。

Acceptance / 验收: 执验10、12–16、20–23、探验09–11、18、26、28. See the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These references define expected cases; report an actual run only with its inputs and evidence. / 这些引用定义预期用例；只有具备实际输入和证据才能报告用例已执行。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Extension Candidate / 扩展候选 improves the workflow after selection or application. / 使用以下指标观察 Extension Candidate / 扩展候选 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: Track output acceptance, defect or rework rate, and whether the fit signal is satisfied. / 跟踪产出采纳率、缺陷或返工率，以及适配信号是否满足。
- 时延指标 / Latency Metrics: Track time from node trigger to usable output, including waiting, routing, iteration, and handoff time. / 跟踪从节点触发到可用输出的耗时，包括等待、路由、迭代和交接时间。
- 成本指标 / Cost Metrics: Track tool calls, token or compute spend, human review effort, and repeated work avoided. / 跟踪工具调用、Token 或计算成本、人工评审投入，以及避免的重复工作。
- 风险指标 / Risk Metrics: Track policy violations, permission escalations, unsafe actions, missed checks, and blast-radius changes. / 跟踪策略违规、权限升级、不安全动作、遗漏检查和影响范围变化。
- Trace 指标 / Trace Metrics: Track trace completeness, evidence freshness, outcome comparison, and whether follow-up actions are closed. / 跟踪 Trace 完整性、证据新鲜度、结果对比和后续动作是否关闭。
