# Extension Candidate / 扩展候选 Observability Metrics / 可观测性指标

Cell / 交织点: governance-chain / 治理 x 链式
Capability / 能力: Governance / 治理
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-chain.md](governance-chain.md)

## Probe Contract and Scope / 探针契约与范围

This card selects metrics for the topology; the [module metric catalog / 模块指标目录](../../governance-observability-probes.md#metric-catalog) owns their full definitions. Read the [shared contract / 共享契约](../../governance-contract.md) for event identities, source quality, and patch acceptance. / 本卡选择拓扑所需指标，完整定义以模块指标目录为准；事件身份、来源质量及补丁采纳遵循共享契约。

This is a specification-only attachment for `CELL_GOVERNANCE_CHAIN; pattern_ref: null`, not an installed probe or proof that the existing runtime speaks `GOV_BOUNDARY_OBS`. Keep permission, dispatch, and verified business outcome separate; a Trace or passed structural check supplies no business authorization. / 这是该现有单元的规范级挂载，不是已部署探针，也不证明既有运行时已实现 `GOV_BOUNDARY_OBS`。分开记录许可、派发及核实业务结果；Trace 或结构检查通过不授予业务权限。

| Metric selection / 指标选择 | Topology-specific interpretation / 拓扑口径 | Required independent evidence / 必要独立证据 |
| --- | --- | --- |
| 指01 | Allowed receipts with complete matching proposal/policy binding ÷ all allowed receipts in the authoritative decision inventory. / 完整匹配提案与策略绑定的允许回执数 ÷ 权威裁决清单中的允许回执总数。 | Decision inventory and immutable proposal/policy history. / 裁决清单及不可变提案、策略历史。 |
| 指04–05 | Final-check completeness over actual dispatches; rejection rate only over verified stale or mismatched attempts. / 对实际派发统计最终检查完整率，仅对核实失效或不匹配尝试统计拦截率。 | Dispatch inventory, actual payloads, receipt checks and controlled fault truth. / 派发清单、实际载荷、回执检查与受控故障真值。 |
| 指18 | Full applicable responsibility chain ÷ authoritative operations known to have produced effects; unknown outcomes remain separate. / 责任链完整的实际效果操作数 ÷ 权威清单中的已知效果操作数；未知结果单列。 | Business results joined to request, proposal, policy, approval and dispatch. / 将业务结果关联到请求、提案、策略、批准与派发。 |
| 指32 | First-version, first-attempt authorized and verified success by deadline over independently valid requests already due. / 在独立有效且已到期需求中，首版首次尝试获合法授权且按期核实成功的比例。 | Independent demand inventory and deadline-aware outcome records. / 独立有效需求清单与包含期限的结果记录。 |

### Measurement and Control Boundary / 统计与控制边界

- Report population, numerator, denominator, time window, units, source references, quality state, and unresolved items. Missing reliable denominators or review truth means `unknown`; a known empty applicable population means `not_applicable`, never 100%. / 报告总体、分子、分母、窗口、单位、来源引用、质量状态及未决项；可靠分母或复核真值缺失记为 `unknown`，已知无适用样本记为 `not_applicable`，不能记为 100%。
- Deduplicate by tenant and immutable event identity; isolate same-ID/different-content conflicts. Do not remove failed, unknown, or overdue items merely to improve ratios; retain pending ages alongside completed latency distributions. / 按租户及不可变事件身份去重，同标识异内容须隔离冲突；不得为提高比例删除失败、未知或到期未决项，完成时延之外还须保留待处理年龄。
- A probe may read authorized sources, append verified observations, and propose controls. Only an authorized execution service can approve, dispatch, settle, stop, or compensate; an `observation_enrichment` patch never mutates those truths. / 探针可读取获准来源、追加核验观测及提出控制建议；只有有权执行服务能批准、派发、结算、停止或补偿，`observation_enrichment` 补丁不能修改这些真值。
- An optional probe outage does not automatically block the workflow. Execution maintains its local controls and minimum audit; missing mandatory evidence or controls is handled by the configured policy for the affected action. / 可选探针故障不自动阻断工作流；执行侧维持本地控制和最小审计，必要证据或控制缺失时按配置策略处理受影响动作。

Acceptance / 验收: 执验01、03–05、16–18、25–26. See the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These references define expected cases; report an actual run only with its inputs and evidence. / 这些引用定义预期用例；只有具备实际输入和证据才能报告用例已执行。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Extension Candidate / 扩展候选 improves the workflow after selection or application. / 使用以下指标观察 Extension Candidate / 扩展候选 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: Track output acceptance, defect or rework rate, and whether the fit signal is satisfied. / 跟踪产出采纳率、缺陷或返工率，以及适配信号是否满足。
- 时延指标 / Latency Metrics: Track time from node trigger to usable output, including waiting, routing, iteration, and handoff time. / 跟踪从节点触发到可用输出的耗时，包括等待、路由、迭代和交接时间。
- 成本指标 / Cost Metrics: Track tool calls, token or compute spend, human review effort, and repeated work avoided. / 跟踪工具调用、Token 或计算成本、人工评审投入，以及避免的重复工作。
- 风险指标 / Risk Metrics: Track policy violations, permission escalations, unsafe actions, missed checks, and blast-radius changes. / 跟踪策略违规、权限升级、不安全动作、遗漏检查和影响范围变化。
- Trace 指标 / Trace Metrics: Track trace completeness, evidence freshness, outcome comparison, and whether follow-up actions are closed. / 跟踪 Trace 完整性、证据新鲜度、结果对比和后续动作是否关闭。
