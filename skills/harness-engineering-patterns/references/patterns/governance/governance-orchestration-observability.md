# Observability Harness / 可观测性框架 Observability Metrics / 可观测性指标

Cell / 交织点: governance-orchestration / 治理 x 编排
Capability / 能力: Governance / 治理
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-orchestration.md](governance-orchestration.md)

## Dedicated business-outcome probes / 专用业务结果探针

Read [the dedicated probe catalog](../../observability-probes.md#probe-catalog), [OBM01–OBM50 definitions](../../observability-probes.md#metric-catalog), [27 unexecuted acceptance cases](../../observability-probes.md#acceptance) and [shared contract](../../observability-contract.md). The source-specific supplement observes identity, raw status, authoritative results, public commitments, asynchronous recovery and evidence completion across all six topologies. / 阅读专用探针、50 项指标、27 个未执行验收场景及共享契约；本来源扩展跨六类拓扑观测身份、原始状态、权威结果、对外承诺、异步恢复及证据补全。

OBM is a specification namespace, separate from the module's 指18–36 selection below and the shared `PATTERN_0052` runtime diagnostics. A passed asset check does not measure these business metrics. Missing denominators remain unknown, empty populations remain not-applicable, and probe outages are evaluated against mandatory local controls. / OBM 是规格编号，与下方治理模块指标选择及共享运行时诊断分开；资产检查通过不代表实测这些业务指标。缺分母记未知，空总体记不适用，探针故障按必要本地控制依赖处理。

## Probe Contract and Scope / 探针契约与范围

This card selects metrics for the topology; the [module metric catalog / 模块指标目录](../../governance-observability-probes.md#metric-catalog) owns their full definitions. Read the [shared contract / 共享契约](../../governance-contract.md) for event identities, source quality, and patch acceptance. / 本卡选择拓扑所需指标，完整定义以模块指标目录为准；事件身份、来源质量及补丁采纳遵循共享契约。

This is a specification-only attachment for `CELL_GOVERNANCE_ORCHESTRATION; PATTERN_0049`, not an installed probe or proof that the existing runtime speaks `GOV_BOUNDARY_OBS`. Keep permission, dispatch, and verified business outcome separate; a Trace or passed structural check supplies no business authorization. / 这是该现有单元的规范级挂载，不是已部署探针，也不证明既有运行时已实现 `GOV_BOUNDARY_OBS`。分开记录许可、派发及核实业务结果；Trace 或结构检查通过不授予业务权限。

| Metric selection / 指标选择 | Topology-specific interpretation / 拓扑口径 | Required independent evidence / 必要独立证据 |
| --- | --- | --- |
| 指18–25 | Audit, event/source/field coverage, conflicts, ambiguous links, evidence validity, and ingestion delay. / 审计、事件与来源及字段覆盖、冲突、关联歧义、证据有效性与采集延迟。 | Independent producer/business inventories and immutable raw references; timestamps preserve clock quality. / 独立生产者或业务清单及不可变原始引用；时间戳保留时钟质量。 |
| 指26–29 | Qualified gap closure, closure latency, patch adoption, and rejected attempts to write outside the whitelist. / 合格缺口关闭、关闭耗时、补丁采纳及非白名单写入尝试。 | Gap deadlines, original evidence, target revisions, per-field receiver acknowledgements. / 缺口期限、原证据、目标版本及接收方逐字段回执。 |
| 指30 | Reviewed correct alerts ÷ independently reviewed alerts; this cannot establish recall or prove every unreviewed alert. / 经独立复核正确告警数 ÷ 已复核告警数；不能由此得出召回率或证实未复核告警。 | Independent review outcomes and explicit sampling method. / 独立复核结论与明确抽样方法。 |
| 指35–36 | Probe overhead needs a matched baseline; feedback coverage uses all requests whose response deadline has elapsed. / 探针附加开销需要匹配基线；反馈覆盖率以全部已到反馈期限请求为总体。 | Controlled enabled/disabled measurements; request and acknowledgement inventories. / 受控启停对照测量；请求及处理回执清单。 |

### Measurement and Control Boundary / 统计与控制边界

- Report population, numerator, denominator, time window, units, source references, quality state, and unresolved items. Missing reliable denominators or review truth means `unknown`; a known empty applicable population means `not_applicable`, never 100%. / 报告总体、分子、分母、窗口、单位、来源引用、质量状态及未决项；可靠分母或复核真值缺失记为 `unknown`，已知无适用样本记为 `not_applicable`，不能记为 100%。
- Deduplicate by tenant and immutable event identity; isolate same-ID/different-content conflicts. Do not remove failed, unknown, or overdue items merely to improve ratios; retain pending ages alongside completed latency distributions. / 按租户及不可变事件身份去重，同标识异内容须隔离冲突；不得为提高比例删除失败、未知或到期未决项，完成时延之外还须保留待处理年龄。
- A probe may read authorized sources, append verified observations, and propose controls. Only an authorized execution service can approve, dispatch, settle, stop, or compensate; an `observation_enrichment` patch never mutates those truths. / 探针可读取获准来源、追加核验观测及提出控制建议；只有有权执行服务能批准、派发、结算、停止或补偿，`observation_enrichment` 补丁不能修改这些真值。
- An optional probe outage does not automatically block the workflow. Execution maintains its local controls and minimum audit; missing mandatory evidence or controls is handled by the configured policy for the affected action. / 可选探针故障不自动阻断工作流；执行侧维持本地控制和最小审计，必要证据或控制缺失时按配置策略处理受影响动作。

Acceptance / 验收: 执验17–21、探验03–08、12–21、26–28. See the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These references define expected cases; report an actual run only with its inputs and evidence. / 这些引用定义预期用例；只有具备实际输入和证据才能报告用例已执行。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Observability Harness / 可观测性框架 improves the workflow after selection or application. / 使用以下指标观察 Observability Harness / 可观测性框架 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `replay_answerability` (sampled audit questions — who did what when, on what evidence — answered fully from the harness), `evidence_join_rate` (events joinable to trace and actor), and `gate_evidence_freshness` (age of evidence consumed by gate verdicts). / `replay_answerability`（抽样审计问题——谁何时凭何证据做了什么——可完全由支架回答的比例）、`evidence_join_rate`（可关联到 trace 与行为者的事件比例）、`gate_evidence_freshness`（门控裁定所耗证据的新鲜度）。
- 时延指标 / Latency Metrics: `capture_overhead` (per-action logging cost relative to action time), `alert_routing_latency` (breach to owner notification), and `replay_reconstruction_time` (audit question to evidenced answer, versus the manual-archaeology baseline). / `capture_overhead`（单动作日志成本相对动作耗时）、`alert_routing_latency`（突破到负责人收到通知的时延）、`replay_reconstruction_time`（审计提问到带证据回答的耗时，对比人工考古基线）。
- 成本指标 / Cost Metrics: storage and retention spend per risk class, `capture_scope_efficiency` (full-capture share of trivial reversible actions — over-collection signal), and postmortem or regulatory-response effort avoided. / 每风险等级的存储与保留开销、`capture_scope_efficiency`（琐碎可逆动作被全量采集的占比——采集过度信号）、避免的复盘或监管响应投入。
- 风险指标 / Risk Metrics: `capture_gap_count` (actions, decisions, or approvals with no event record — each is live `FAIL_0010`), `harness_blind_window` (time affected gates admitted actions while mandatory evidence or local controls were unavailable), `alert_flood_rate` (alerts per owner per day, watch `FAIL_0011` fatigue), and unauthorized evidence access (violates least privilege within `GOV_0003`). / `capture_gap_count`（无事件记录的动作、决策或审批数——每个都是现行 `FAIL_0010`）、`harness_blind_window`（必要证据或本地控制不可用时，受影响门控仍准入动作的时长）、`alert_flood_rate`（每负责人每日告警量，对应 `FAIL_0011` 疲劳）、越权访问证据事件（违反 `GOV_0003` 内最小权限）。
- Trace 指标 / Trace Metrics: `correlation_scheme_conformance` (events carrying actor, action, timestamp, trace id — the `GOV_0002` implementation measure), gate-verdict evidence annotation coverage, and alert-to-resolution closure rate. / `correlation_scheme_conformance`（事件携带行为者、动作、时间戳、trace id 的合规率——`GOV_0002` 的实现度量）、门控裁定的证据标注覆盖率、告警到解决的闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert on `capture_gap_count` above zero for irreversible or approval-gated action classes and on any `harness_blind_window` — gaps in those classes are live `FAIL_0010`, and a blind window means an affected gate admitted work without mandatory evidence, not merely that an optional probe was offline. / 不可逆或需审批动作类的 `capture_gap_count` 大于零即告警，任何 `harness_blind_window` 同样告警——这些类别的缺口就是现行 `FAIL_0010`，盲窗意味着受影响门控在缺少必要证据时准入动作，不是指可选探针单纯离线。
- Recommend blocking affected dispatches or promotions when mandatory evidence cannot be validated from any approved source; the authorized execution service applies the configured policy. An optional stream outage with adequate local evidence does not require a global stop. / 无法从任何获准来源核验必要证据时，建议阻断受影响派发或晋级，由有权执行服务按配置策略处理；本地证据完备时，可选流中断无需全局停止。
