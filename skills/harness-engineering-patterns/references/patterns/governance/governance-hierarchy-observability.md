# Blast Radius Control / 爆炸半径控制 Observability Metrics / 可观测性指标

Cell / 交织点: governance-hierarchy / 治理 x 层级
Capability / 能力: Governance / 治理
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [governance-hierarchy.md](governance-hierarchy.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Blast Radius Control / 爆炸半径控制 improves the workflow after selection or application. / 使用以下指标观察 爆炸半径控制 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: task completion rate inside containment versus with layers relaxed (measures minimum-viable-containment fit), and share of tasks completing without any layer-widening request. / 遏制内任务完成率对比放宽层后的完成率（度量最小可行遏制的贴合度）、无需任何放宽请求即完成的任务占比。
- 时延指标 / Latency Metrics: containment setup time per task, layer-passage grant turnaround, and staged-rollout duration from narrowest to production scope. / 每任务遏制配置时间、层通行授权周转时间、从最窄范围到生产范围的分阶段放量时长。
- 成本指标 / Cost Metrics: containment infrastructure overhead, budget-cap utilization distribution (caps never approached are too loose; caps constantly hit are too tight), and damage cost avoided in contained incidents. / 遏制基础设施开销、预算上限利用率分布（从未接近的上限过松，频繁触顶的上限过紧）、被遏制事件避免的损失成本。
- 风险指标 / Risk Metrics: layer-breach and near-miss count by layer (`FAIL_0009` sandbox escape when layer 1 fails into layer 2), denied-action distribution per layer (a silent layer may be bypassed, not safe), ambient or permanent grants outstanding (`FAIL_0005` recreation), and layer-disable events — users switching containment off is the worst signal. / 分层突破与险情计数（第 1 层失守进入第 2 层即 `FAIL_0009` 沙箱逃逸）、各层拒绝动作分布（长期无声的层可能已被绕过而非安全）、存量环境或永久授权（重演 `FAIL_0005`）、层被关闭事件——用户整体关闭遏制是最坏信号。
- Trace 指标 / Trace Metrics: per-task containment profile archival, passage-grant evidence completeness, breach report replayability, and widening decisions carrying staged evidence. / 按任务遏制配置归档率、通行授权证据完整率、突破报告可回放性、放宽决策附带分阶段证据的比例。

### Default Gate Suggestions / 默认门控建议

- Block layer widening when no successful-run evidence exists at the current narrower setting. / 当前更窄设置下无成功运行证据时，阻止放宽该层。
- Alert on any breach where layer n+1 did not log a containment event for a layer-n escape — the nesting assumption failed. / 第 n 层逃逸而第 n+1 层未记录遏制事件时告警——嵌套假设已失效。
- Alert when per-task widening requests exceed a threshold — containment is below minimum viable and users will route around it. / 每任务放宽请求超过阈值时告警——遏制已低于最小可行水平，用户将绕开它。
