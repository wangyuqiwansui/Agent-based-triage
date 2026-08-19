# Experience Replay / 经验回放 Observability Metrics / 可观测性指标

Pattern ID / 模式 ID: `PATTERN_0042`
Registration Version / 注册版本: `1.0.0`
Cell / 交织点: reflection-hierarchy / 反思 x 层级
Capability / 能力: Reflection / 反思
Mode / 模式: Hierarchy / 层级
Design Pattern File / 设计模式文件: [reflection-hierarchy.md](reflection-hierarchy.md)

Use this file as the observability contract for the registered Experience Replay pattern. / 将本文档作为已注册经验回放模式的可观测性契约。

Shared Reflection Contract / 共享反思契约: [Governed Reflection Execution Flow / 受治理反思执行流程](../../reflection-execution-flow.md)

## Quick Navigation / 快速导航

- [Probe Binding / 探针绑定](#probe-binding--探针绑定)
- [Observation Funnel / 观测漏斗](#observation-funnel--观测漏斗)
- [Metric Definitions / 指标定义](#metric-definitions--指标定义)
- [Gates And Alerts / 门控与告警](#gates-and-alerts--门控与告警)
- [Acceptance / 验收](#acceptance--验收)

## Probe Binding / 探针绑定

Use [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md) as the shared deployable source. Resolve the actual execution mode with `resolve_required_probes(..., supporting_topologies=("hierarchy",), condition_states=...)`, and resolve the admitted reflection profile with `resolve_reflection_required_probes(attribution_claimed=..., learning_promotion=...)`. / 使用共享工作流可观测性探针作为可部署事实源。通过 `resolve_required_probes(..., supporting_topologies=("hierarchy",), condition_states=...)` 解析实际执行模式，并通过 `resolve_reflection_required_probes(attribution_claimed=..., learning_promotion=...)` 解析已准入反思档案。

At minimum, bind / 至少绑定：

- `PROBE_0013` when an external outcome exists or is expected. / 存在或预期存在外部结果时绑定结果回接探针。
- `PROBE_0014` and `PROBE_0015` for privacy, governance, and probe self-health. / 使用隐私治理与探针自健康探针。
- `PROBE_0016` through `PROBE_0021` for admitted reflection, baseline, revalidation, anti-gaming, recovery, and closure. / 使用反思准入、基线、复验、反投机、恢复与闭环探针。
- `PROBE_0022` only when a causal attribution is claimed. / 仅在声称因果归因时启用混杂因素与归因探针。
- `PROBE_0023` when an experience is retained persistently or nominated as a checklist, rule, hard guard, knowledge item, or Skill. / 当经验被持久保留或提名为检查清单、规则、硬守卫、知识条目或 Skill 时启用学习晋升探针。

The shared probe resolver does not yet provide a dedicated `experience_replay=True` deployable profile. Until a replay-specific probe pack and receipt Schema are versioned, the stage fields below are design-level requirements and the cell remains `draft`. / 共享探针解析器目前尚未提供专用的 `experience_replay=True` 可部署档案。在回放专用探针包与凭据 Schema 完成版本化前，下述阶段字段属于设计层要求，本单元保持 `draft`。

## Observation Funnel / 观测漏斗

```text
eligible source trajectories / 可用来源轨迹
  -> distilled candidates / 已蒸馏候选
  -> recalled candidates / 已召回候选
  -> filtered candidates / 已过滤候选
  -> injected experiences / 已注入经验
  -> adopted experiences / 已采用经验
  -> linked local outcomes / 已关联局部结果
  -> linked external outcomes / 已关联外部结果
  -> per-experience credit / 逐条信用
  -> lifecycle decision / 生命周期决定
```

Every stage records an explicit set, source version, event time, run and task bindings, producer or observer, completeness state, and exclusion reason. Empty is a measured value; missing, unknown, not applicable, redacted, stale, conflicting, and unmatched are distinct states. / 每个阶段都记录显式集合、来源版本、事件时间、运行与任务绑定、生产者或观察者、完整性状态及排除原因。空集合是已测值；缺失、未知、不适用、已脱敏、过期、冲突和无法关联是不同状态。

## Evidence Strength / 证据强度

| State / 状态 | Minimum evidence / 最低证据 | Probe treatment / 探针处理 |
| --- | --- | --- |
| Recalled / 已召回 | Retrieval event binding the experience and target run. / 绑定经验与目标运行的检索事件。 | Count in recall denominator only. / 只进入召回分母。 |
| Injected / 已注入 | Filter decision plus bounded-context placement. / 过滤决定及有界上下文位置。 | Count in adoption denominator. / 进入采用率分母。 |
| Adopted / 已采用 | Version-bound plan or node change, or concrete action/check evidence. / 绑定版本的计划或节点改变，或具体行动/检查证据。 | Self-report alone remains weak and is excluded. / 仅有自述仍属弱证据并排除。 |
| Beneficial / 已产生收益 | Comparable local or external outcome linked to the adopted experience. / 与已采用经验关联的可比局部或外部结果。 | May support gain; causal credit still requires attribution evidence. / 可支持收益；因果信用仍需归因证据。 |
| Promoted / 已晋升 | Complete source round, bounded task distribution, outcome evidence, owner, authority, version, rollback, and expiry. / 完整来源轮次、有界任务分布、结果证据、责任人、权限、版本、回滚与到期。 | Require `PROBE_0023`; nomination is not publication. / 必须启用 `PROBE_0023`；提名不等于发布。 |

## Metric Definitions / 指标定义

All ratios declare an exact window, task distribution, pattern registration version, experience-bundle version, source completeness rule, and exclusions. Do not mix experience versions or task classes silently. / 所有比率都必须声明精确时间窗、任务分布、模式注册版本、经验包版本、来源完整性规则与排除项；不得静默混合不同经验版本或任务类型。

| Metric / 指标 | Formula / 公式 | Decision use / 决策用途 |
| --- | --- | --- |
| `experience_recall_precision` / 经验召回精确率 | Post-task confirmed relevant recalled experiences / all recalled experiences. / 任务后确认相关的召回经验数 ÷ 全部召回经验数。 | Detect relevance hallucination and noisy retrieval. / 发现相关性幻觉与噪声检索。 |
| `experience_injection_rate` / 经验注入率 | Experiences passing all filters and entering context / recalled candidates. / 通过全部过滤并进入上下文的经验数 ÷ 召回候选数。 | Diagnose candidate quality and filter strictness. / 诊断候选质量与过滤严格度。 |
| `experience_adoption_rate` / 经验采用率 | Injected experiences with medium or strong adoption evidence / injected experiences. / 具有中等或强采用证据的已注入经验数 ÷ 已注入经验数。 | Determine whether recall changes behavior. / 判断召回是否改变行为。 |
| `experience_outcome_linkage_coverage` / 经验结果关联覆盖率 | Adopted experiences with a matched local or external outcome / adopted experiences whose outcome window closed. / 具有已匹配局部或外部结果的已采用经验数 ÷ 结果窗口已关闭的已采用经验数。 | Expose missing result return. / 暴露结果回接缺口。 |
| `experience_credit_assignment_coverage` / 经验信用分配覆盖率 | Outcome-updated experiences with per-experience evidence and contribution state / experiences receiving an outcome update. / 具有逐条证据与贡献状态的结果更新经验数 ÷ 收到结果更新的经验数。 | Prevent blanket credit. / 防止统一记功。 |
| `experience_replay_gain` / 经验回放增益 | Outcome metric with adopted experience minus a comparable no-experience or prior-version baseline. / 采用经验后的结果指标减去可比的无经验或旧版本基线。 | Estimate actual improvement. / 估计真实改善。 |
| `repeat_failure_avoidance_rate` / 重复失败避免率 | Comparable repeated-failure opportunities avoided with supported adoption / all comparable repeated-failure opportunities with an available experience. / 有可用经验的可比重复失败机会中，具有受支持采用并避免失败的次数 ÷ 全部机会数。 | Measure whether lessons prevent recurrence. / 衡量经验是否避免复发。 |
| `stale_experience_use_rate` / 过期经验使用率 | Adopted experiences already stale or invalid at adoption time / adopted experiences. / 采用时已经过期或失效的经验数 ÷ 已采用经验数。 | Detect old-state contamination. / 发现旧状态污染。 |
| `replay_provenance_completeness` / 回放来源完整率 | Lifecycle-updated experiences traceable through candidate, injection, adoption, outcome, and credit bindings to `L0` / all lifecycle-updated experiences. / 可经候选、注入、采用、结果与信用绑定回查至 `L0` 的生命周期更新经验数 ÷ 全部生命周期更新经验数。 | Audit replay conclusions. / 审计回放结论。 |
| `replay_receipt_closure_rate` / 回放凭据闭环率 | Started replay receipts ending in explicit no-op, rejected, pending-outcome, retained, down-ranked, invalidated, archived, or nominated terminal / all started replay receipts whose close deadline passed. / 在关闭期限内进入显式无操作、拒绝、等待结果、保留、降权、失效、归档或提名终态的凭据数 ÷ 关闭期限已过的全部启动凭据数。 | Detect abandoned replays. / 发现悬空回放。 |

`experience_replay_gain` is unreportable when the comparison is not comparable. A missing baseline is not zero gain, and a task-level success is not per-experience credit. / 比较不可比时不得报告 `experience_replay_gain`。基线缺失不等于零收益，任务级成功也不等于逐条经验信用。

## Observability Metrics / 可观测性指标

- 质量指标 / Quality Metrics: `experience_recall_precision`, `experience_adoption_rate`, `experience_replay_gain`, `repeat_failure_avoidance_rate`, and sampled conclusion accuracy. / 经验召回精确率、经验采用率、经验回放增益、重复失败避免率及结论抽样准确率。
- 时延指标 / Latency Metrics: trajectory-to-candidate latency, recall-to-injection latency, adoption-to-outcome latency, outcome-to-credit latency, and stale-experience discovery delay. / 轨迹到候选、召回到注入、采用到结果、结果到信用的时延，以及过期经验发现时延。
- 成本指标 / Cost Metrics: replay review effort, retrieval and filtering cost, context tokens occupied by injected experience, outcome-collection cost, and cost per supported retained lesson. / 回放评审投入、检索与过滤成本、注入经验占用的上下文 token、结果采集成本及每条受支持保留经验的成本。
- 风险指标 / Risk Metrics: `stale_experience_use_rate`, record-gap rate, cross-tenant experience exposure, unfiltered lesson volume, self-report-only adoption rate, blanket-credit rate, unreviewed promotion count, and probe-unhealthy windows. / 过期经验使用率、记录缺口率、跨租户经验暴露、未过滤经验体量、仅自述采用率、统一记功率、未经评审的晋升数及探针不健康窗口。
- Trace 指标 / Trace Metrics: `replay_provenance_completeness`, `experience_outcome_linkage_coverage`, `experience_credit_assignment_coverage`, `replay_receipt_closure_rate`, explicit-filter-reason coverage, and unmatched-outcome backlog. / 回放来源完整率、经验结果关联覆盖率、经验信用分配覆盖率、回放凭据闭环率、显式过滤原因覆盖率及未匹配结果积压。

## Gates And Alerts / 门控与告警

Aggregate metrics remain diagnostic until an accountable owner approves thresholds, minimum samples, task-distribution boundaries, drift handling, and promotion evidence. / 在责任人批准阈值、最小样本、任务分布边界、漂移处理与晋升证据前，聚合指标保持诊断用途。

Direct integrity violations may fail closed per run / 以下直接完整性违规可按单次运行默认阻断：

- An adopted experience was never injected or lacks plan/action evidence. / 已采用经验从未注入，或缺少计划/行动证据。
- An experience overrides current authoritative truth, permission, policy, tenant, or risk boundaries. / 经验覆盖当前权威真值、权限、策略、租户或风险边界。
- A positive credit assignment lacks an outcome binding or exceeds the attribution evidence level. / 正向信用缺少结果绑定，或超过归因证据等级。
- A binding rule or capability promotion lacks owner, authority, version, rollback, expiry, or source-round evidence. / 约束性规则或能力晋升缺少责任人、权限、版本、回滚、到期或来源轮证据。
- A replay conclusion is built on undisclosed record gaps or an unhealthy observation window. / 回放结论建立在未披露的记录缺口或不健康观测窗口上。

Alert when recall is high but adoption stays low, adoption is high but outcome linkage stays low, positive credit rises without comparable gain, stale-experience use rises, repeat failures do not decline, or receipts remain open beyond their declared window. / 当召回高但采用持续低、采用高但结果关联持续低、正向信用上升却没有可比收益、过期经验使用率上升、重复失败不下降，或凭据超过声明窗口仍未关闭时告警。

## Observation Patch Boundary / 观察补丁边界

The probe may automatically add a uniquely derivable correlation key, field provenance, completeness state, or deterministic lifecycle label. It may not automatically invent adoption, overwrite a business outcome, change credit, revive stale experience, authorize injection, or promote an asset. / 探针可以自动补充唯一可确定的关联键、字段来源、完整性状态或确定性生命周期标签；不得自动编造采用、覆盖业务结果、改变信用、恢复过期经验、授权注入或晋升资产。

Every non-deterministic proposal carries source events, rule version, confidence, scope, expiry, and an accept/reject/revoke history. / 每个非确定性提案都必须携带来源事件、规则版本、置信度、适用范围、到期条件及接受/拒绝/撤销历史。

## Acceptance / 验收

Experience Replay observability is acceptable only when / 经验回放可观测性仅在以下条件全部满足时可验收：

- Every stage of the replay funnel is distinguishable and bound to one run, task type, pattern registration version, and experience-bundle version. / 回放漏斗的每个阶段都可区分，并绑定一个运行、任务类型、模式注册版本与经验包版本。
- Stage sets and denominators are complete or explicitly degraded; missing never becomes zero. / 阶段集合与分母完整或显式降级；缺失不得变成零。
- Adoption evidence is stronger than self-report, and outcome evidence is independently linked. / 采用证据强于自述，结果证据独立关联。
- Credit is allocated per experience and causal language does not exceed attribution evidence. / 信用逐条分配，因果表述不超过归因证据。
- Probe health, privacy, retention, tenant isolation, and unmatched outcomes remain visible. / 探针健康、隐私、保留、租户隔离及未匹配结果保持可见。
- Every observation patch is additive, provenance-bound, and auditable. / 每个观察补丁都是追加式、带来源且可审计。
- A missing replay-specific deployable profile is reported as a maturity gap, not presented as implemented coverage. / 缺少回放专用可部署档案时，将其报告为成熟度缺口，不得伪称已实现覆盖。
