# Blast Radius Control / 爆炸半径控制 Observability Metrics / 可观测性指标

Cell / 交织点: governance-hierarchy / 治理 x 层级
Capability / 能力: Governance / 治理
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-hierarchy.md](governance-hierarchy.md)

## Probe Contract and Scope / 探针契约与范围

This card selects metrics for the topology; the [module metric catalog / 模块指标目录](../../governance-observability-probes.md#metric-catalog) owns their full definitions. Read the [shared contract / 共享契约](../../governance-contract.md) for event identities, source quality, and patch acceptance. / 本卡选择拓扑所需指标，完整定义以模块指标目录为准；事件身份、来源质量及补丁采纳遵循共享契约。

This is a specification-only attachment for `CELL_GOVERNANCE_HIERARCHY; PATTERN_0050`, not an installed probe or proof that the existing runtime speaks `GOV_BOUNDARY_OBS`. Keep permission, dispatch, and verified business outcome separate; a Trace or passed structural check supplies no business authorization. / 这是该现有单元的规范级挂载，不是已部署探针，也不证明既有运行时已实现 `GOV_BOUNDARY_OBS`。分开记录许可、派发及核实业务结果；Trace 或结构检查通过不授予业务权限。

| Metric selection / 指标选择 | Topology-specific interpretation / 拓扑口径 | Required independent evidence / 必要独立证据 |
| --- | --- | --- |
| 指06 | Verified effects exceeding the then-effective subject, object or action grant; absence of result evidence cannot become zero violations. / 已核实效果超出当时主体、对象或动作授权；结果证据缺失不能报告零违规。 | Authoritative business effects and historical parent/child credentials, actual payload and scope. / 权威业务效果、历史父子凭证、实际载荷及范围。 |
| 指07–08 | Aggregate exposure and over-cap admission across the entire applicable parent/subject tree. / 对适用父级或主体整树汇总累计暴露与超限准入。 | Shared authoritative ledger with trusted account dimensions; never sum unlike units. / 带可信账户维度的共享权威账本；不同单位不得相加。 |
| 指16–17 | Scoped promotion evidence and revocation propagation across all relevant dispatch entries. / 场景匹配的晋升证据及所有相关派发入口的撤销传播。 | Grant inventory, independent approval, outcome windows, fence versions and acknowledgements. / 授权清单、独立批准、结果观察窗、围栏版本及确认。 |
| 指18 | Responsibility chain includes delegation and handoff acknowledgement but still binds each child's specific action. / 责任链包含委托及交接确认，且仍须绑定每个子执行者的具体动作。 | Parent plan, child credential, proposal and result records; responsibility does not imply permission. / 父计划、子凭证、提案及结果记录；责任不等于权限。 |

### Measurement and Control Boundary / 统计与控制边界

- Report population, numerator, denominator, time window, units, source references, quality state, and unresolved items. Missing reliable denominators or review truth means `unknown`; a known empty applicable population means `not_applicable`, never 100%. / 报告总体、分子、分母、窗口、单位、来源引用、质量状态及未决项；可靠分母或复核真值缺失记为 `unknown`，已知无适用样本记为 `not_applicable`，不能记为 100%。
- Deduplicate by tenant and immutable event identity; isolate same-ID/different-content conflicts. Do not remove failed, unknown, or overdue items merely to improve ratios; retain pending ages alongside completed latency distributions. / 按租户及不可变事件身份去重，同标识异内容须隔离冲突；不得为提高比例删除失败、未知或到期未决项，完成时延之外还须保留待处理年龄。
- A probe may read authorized sources, append verified observations, and propose controls. Only an authorized execution service can approve, dispatch, settle, stop, or compensate; an `observation_enrichment` patch never mutates those truths. / 探针可读取获准来源、追加核验观测及提出控制建议；只有有权执行服务能批准、派发、结算、停止或补偿，`observation_enrichment` 补丁不能修改这些真值。
- An optional probe outage does not automatically block the workflow. Execution maintains its local controls and minimum audit; missing mandatory evidence or controls is handled by the configured policy for the affected action. / 可选探针故障不自动阻断工作流；执行侧维持本地控制和最小审计，必要证据或控制缺失时按配置策略处理受影响动作。

Acceptance / 验收: 执验09–11、22–24. See the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These references define expected cases; report an actual run only with its inputs and evidence. / 这些引用定义预期用例；只有具备实际输入和证据才能报告用例已执行。

## Dedicated Effect Probes / 专用效果探针

Use the [blast-radius probe workflow](../../blast-radius-observability-probes.md#probe-workflow), [component inventory](../../blast-radius-observability-probes.md#components), [39 metric definitions](../../blast-radius-observability-probes.md#metric-catalog) and [shared interaction contract](../../blast-radius-contract.md). This specializes the module metrics above and retains their scope; it does not install a production observer. / 使用爆炸半径专用探针流程、组件清单、39 项指标定义及共享交互契约；这细化前述模块指标且保留其范围，不表示安装了生产观察器。

Prioritize child conservation, independent permit coverage, idempotency conflicts, occupied unknowns, post-stop new dispatch and source silence. Keep actual committed effects, attempted rejected units, unavailable reserved capacity and unresolved outcomes separate. Root reports count descendant effects once; same-intent duplicates differ from repeated event delivery; stopped-before-send differs from a delayed receipt. Missing independent effect inventories means coverage is unknown. / 优先观察子级守恒、独立许可覆盖、幂等冲突、未知占用、停止后新派发及来源静默。分开实际提交效果、被拒尝试量、不可用预留容量及未决结果。根报告后代只计一次，同意图重复与事件重复分开，停止前发送与迟到回执分开；缺少独立效果总体时覆盖率为未知。

Probe output follows target/base-revision/expiry checks and explicit execution responses. Observation patches never release balances or manufacture approval/success. Only pre-registered deterministic control rules can invoke automatic blocking through the authorized execution service. / 探针输出须经目标、基线修订、有效期校验及执行侧明确响应；观测补丁不释放余额、不制造审批成功，只有预注册确定性控制规则可经有权执行服务自动阻断。

Acceptance / 验收: [BRQ01–BRQ16](../../blast-radius-observability-probes.md#acceptance), all `not_executed` integration requirements. / 全部为未执行的集成要求。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Blast Radius Control / 爆炸半径控制 improves the workflow after selection or application. / 使用以下指标观察 爆炸半径控制 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: task completion rate inside containment versus with layers relaxed (measures minimum-viable-containment fit), and share of tasks completing without any layer-widening request. / 遏制内任务完成率对比放宽层后的完成率（度量最小可行遏制的贴合度）、无需任何放宽请求即完成的任务占比。
- 时延指标 / Latency Metrics: containment setup time per task, layer-passage grant turnaround, and staged-rollout duration from narrowest to production scope. / 每任务遏制配置时间、层通行授权周转时间、从最窄范围到生产范围的分阶段放量时长。
- 成本指标 / Cost Metrics: containment infrastructure overhead, budget-cap utilization distribution (interpret alongside legitimate demand and risk, not as an automatic reason to widen limits), and damage cost avoided in contained incidents. / 遏制基础设施开销、预算上限利用率分布（结合合法需求与风险解释，不作为自动放宽限额的理由）、被遏制事件避免的损失成本。
- 风险指标 / Risk Metrics: layer-breach and near-miss count by layer (`FAIL_0009` sandbox escape when layer 1 fails into layer 2), denied-action distribution per layer (a silent layer may be bypassed, not safe), ambient or permanent grants outstanding (`FAIL_0005` recreation), and layer-disable events — users switching containment off is the worst signal. / 分层突破与险情计数（第 1 层失守进入第 2 层即 `FAIL_0009` 沙箱逃逸）、各层拒绝动作分布（长期无声的层可能已被绕过而非安全）、存量环境或永久授权（重演 `FAIL_0005`）、层被关闭事件——用户整体关闭遏制是最坏信号。
- Trace 指标 / Trace Metrics: per-task containment profile archival, passage-grant evidence completeness, breach report replayability, and widening decisions carrying staged evidence. / 按任务遏制配置归档率、通行授权证据完整率、突破报告可回放性、放宽决策附带分阶段证据的比例。

### Default Gate Suggestions / 默认门控建议

- The authorization service blocks widening without scoped success evidence, an appropriate observation window, anomaly review, and valid independent approval; the probe cannot grant scope. / 缺少场景成功证据、适当观察窗、异常审查或有效独立批准时，由授权服务阻止放宽；探针不能授予范围。
- Alert on any breach where layer n+1 did not log a containment event for a layer-n escape — the nesting assumption failed. / 第 n 层逃逸而第 n+1 层未记录遏制事件时告警——嵌套假设已失效。
- Alert when per-task widening requests exceed a configured threshold and inspect task needs, misconfiguration, or misuse before deciding whether any boundary should change. / 每任务放宽请求超过配置阈值时告警，先核查任务需求、配置错误或滥用，再决定是否调整边界。
