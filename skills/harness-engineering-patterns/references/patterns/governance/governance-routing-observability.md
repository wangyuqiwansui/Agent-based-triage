# Approval Gate / 审批门禁 Observability Metrics / 可观测性指标

Cell / 交织点: governance-routing / 治理 x 路由
Capability / 能力: Governance / 治理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-routing.md](governance-routing.md)

## Dedicated approval probes / 审批门专用探针

Read [the dedicated probe catalog / 专用探针目录](../../approval-gate-observability-probes.md), [execution stages / 执行阶段](../../approval-gate-execution-flow.md) and [binding/supplement contract / 绑定补全契约](../../approval-gate-contract.md). Source contract `1.0.0` supplies 28 probe checks, `AGM01–AGM50` metric definitions, quality L0–L4 and 28 unexecuted probe acceptance requirements. These definitions complement the module metrics below; they are not deployed calculators or aliases for `MET_GOV_*`. / 来源契约提供 28 项探针检查、50 项指标、L0–L4 质量等级及 28 项未执行探针验收要求；与下列模块指标互补，不表示已部署计算器，也不是治理指标别名。

Correlate proposal/policy/receipt/checkpoint/execution/effect; verify exact bindings, current roles/quorum, drift, atomic use and destination effects. Source absence remains a gap until authoritative evidence proves a violation. Supplement only the observation layer with authenticated provenance and explicit adoption; never modify signed receipts or infer missing approval. / 关联提案策略回执检查点执行效果，核验精确绑定、当前角色会签、漂移、原子使用及目的端效果；来源缺失保持缺口，直到权威证据证实违规。补全只追加观测层，须认证来源与明确采纳，不修改签名回执，不推断缺失批准。

## Probe Contract and Scope / 探针契约与范围

This card selects metrics for the topology; the [module metric catalog / 模块指标目录](../../governance-observability-probes.md#metric-catalog) owns their full definitions. Read the [shared contract / 共享契约](../../governance-contract.md) for event identities, source quality, and patch acceptance. / 本卡选择拓扑所需指标，完整定义以模块指标目录为准；事件身份、来源质量及补丁采纳遵循共享契约。

This is a specification-only attachment for `CELL_GOVERNANCE_ROUTING; PATTERN_0047`, not an installed probe or proof that the existing runtime speaks `GOV_BOUNDARY_OBS`. Keep permission, dispatch, and verified business outcome separate; a Trace or passed structural check supplies no business authorization. / 这是该现有单元的规范级挂载，不是已部署探针，也不证明既有运行时已实现 `GOV_BOUNDARY_OBS`。分开记录许可、派发及核实业务结果；Trace 或结构检查通过不授予业务权限。

| Metric selection / 指标选择 | Topology-specific interpretation / 拓扑口径 | Required independent evidence / 必要独立证据 |
| --- | --- | --- |
| 指01–03 | Policy binding/provenance coverage and confirmed separation-of-duties violations; missing identity evidence is a gap, not proven misconduct. / 策略绑定与来历覆盖率、已证实职责分离违规数；身份资料缺失是缺口，不是已证实违规。 | Decision and policy inventories, protected approvals, identity and authority history. / 裁决与策略清单、受保护批准、身份及授权历史。 |
| 指04–05 | Final-check coverage and known-invalid receipt interception expose approval-to-payload drift. / 最终检查覆盖率和已知失效回执拦截率揭示批准与载荷漂移。 | Actual dispatches and validated stale/mismatch attempts, not only successful check logs. / 实际派发与已核验失效、不匹配尝试，不能只看成功检查日志。 |
| 指13–15 | Approval latency, reminders per 100 logical actions, and independently reviewed unnecessary approvals. / 审批等待、每百逻辑动作提醒次数及经独立复核的冗余审批。 | Approval lifecycle, all interactions, action inventory and review sampling truth. / 审批生命周期、全部交互、动作清单与复核抽样真值。 |
| 指31 | First route agrees with independently established route ÷ actions with route truth; the final branch is not its own answer key. / 首次路由符合独立真值的动作数 ÷ 有路由真值的动作数；最终分支不能自证正确。 | Historical rules plus independent review or fixed-case truth. / 历史规则与独立复核或固定用例真值。 |

### Measurement and Control Boundary / 统计与控制边界

- Report population, numerator, denominator, time window, units, source references, quality state, and unresolved items. Missing reliable denominators or review truth means `unknown`; a known empty applicable population means `not_applicable`, never 100%. / 报告总体、分子、分母、窗口、单位、来源引用、质量状态及未决项；可靠分母或复核真值缺失记为 `unknown`，已知无适用样本记为 `not_applicable`，不能记为 100%。
- Deduplicate by tenant and immutable event identity; isolate same-ID/different-content conflicts. Do not remove failed, unknown, or overdue items merely to improve ratios; retain pending ages alongside completed latency distributions. / 按租户及不可变事件身份去重，同标识异内容须隔离冲突；不得为提高比例删除失败、未知或到期未决项，完成时延之外还须保留待处理年龄。
- A probe may read authorized sources, append verified observations, and propose controls. Only an authorized execution service can approve, dispatch, settle, stop, or compensate; an `observation_enrichment` patch never mutates those truths. / 探针可读取获准来源、追加核验观测及提出控制建议；只有有权执行服务能批准、派发、结算、停止或补偿，`observation_enrichment` 补丁不能修改这些真值。
- An optional probe outage does not automatically block the workflow. Execution maintains its local controls and minimum audit; missing mandatory evidence or controls is handled by the configured policy for the affected action. / 可选探针故障不自动阻断工作流；执行侧维持本地控制和最小审计，必要证据或控制缺失时按配置策略处理受影响动作。

Acceptance / 验收: 执验01–08、26. See the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These references define expected cases; report an actual run only with its inputs and evidence. / 这些引用定义预期用例；只有具备实际输入和证据才能报告用例已执行。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Approval Gate / 审批门禁 improves the workflow after selection or application. / 使用以下指标观察 审批门禁 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `gate_precision` (blocked actions that were genuinely unsafe) and `gate_recall` (unsafe actions that were caught), stage distribution (deny/allow/gate hit ratios), and semantic-companion coverage (structural gates that also ran a semantic consistency check). / `gate_precision`（被阻断动作中确属不安全的比例）与 `gate_recall`（不安全动作被捕获的比例）、三段命中分布（拒绝/放行/门比率）、语义配套覆盖率（同时执行语义一致性检查的结构门占比）。
- 时延指标 / Latency Metrics: rule-stage decision latency against the configured service target, human-gate waiting time, and share of workflow wall-clock spent blocked at gates. / 规则段决策时延与配置服务目标的差距、人工门等待时间、工作流墙钟中被门禁阻塞的占比。
- 成本指标 / Cost Metrics: human review effort per gated action, evidence-preparation cost for gate requests, and rework avoided by pre-execution blocking. / 每个受门动作的人工评审投入、门禁请求的证据准备成本、执行前阻断避免的返工。
- 风险指标 / Risk Metrics: approval-fatigue signals — stage-3 fire rate per reviewer per day and time-to-approve trending toward zero (a signal for independent review, not proof of rubber-stamping); `FAIL_0005` permission-bypass incidents (actions misrouted into allow rules); structural-pass-semantic-fail escapes (repository-evidenced failure class, 2026-07-03). / 审批疲劳信号——每评审人每日第三段触发次数、审批耗时趋近于零（需要独立复核的信号，不直接证明无脑放行）；`FAIL_0005` 权限绕过事件（动作被误路由进放行规则）；结构通过但语义失败的漏网数（本仓库 2026-07-03 实证失败类）。
- Trace 指标 / Trace Metrics: gate decision record completeness (stage, rule hit, decision, approver identity), blocked-action reason coverage, and superseded-output audit chain (bad approvals must stay replayable, not deleted). / 门禁决策记录完整率（段、命中规则、决定、审批人身份）、阻断原因覆盖率、废弃产物审计链（错误批准必须可回放，不得删除）。

### Default Gate Suggestions / 默认门控建议

- Alert when stage-3 volume exceeds the configured reviewer capacity; review redundant triggers and authorized low-risk rules, preserving all required approvals. / 第三段数量超过配置的评审容量时告警；复核冗余触发及获准的低风险规则，保留全部必要审批。
- Treat unusually short approval time as a review signal using the action's complexity and reviewer context; do not infer invalid approval from timing alone. / 结合动作复杂度及评审背景复核异常短的审批耗时，不仅凭时间断定批准无效。
- A configured mandatory semantic companion that fails or is missing blocks the affected downstream action through the authorized gate; the probe only reports the evidence and recommendation. / 配置为必要的语义配套失败或缺失时，由有权门控阻断受影响的后续动作；探针仅报告证据与建议。
