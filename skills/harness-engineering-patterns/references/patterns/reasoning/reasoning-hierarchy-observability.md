# Extension Candidate / 扩展候选 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-hierarchy / 推理 x 层级
Capability / 能力: Reasoning / 推理
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-hierarchy.md](reasoning-hierarchy.md)
Shared Probe Suite / 共享探针套件: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe parent-child reasoning support without treating the evidence as promotion of the extension candidate. / 使用以下指标观察父子推理支撑作用，但不得将这些证据直接视为扩展候选晋升。

- 质量指标 / Quality Metrics: parent-child correlation success, handoff completeness, goal/constraint fidelity, evidence-traceability preservation, conflict rate, duplicate-work rate, and parent validation pass rate. / 父子关联成功率、交接完整率、目标/约束保真率、证据可追踪保留率、冲突率、重复工作率和父级验证通过率。
- 时延指标 / Latency Metrics: child queue and execution latency, handoff wait, parent synthesis latency, escalation wait, and end-to-end critical-path latency. / 子任务排队与执行时延、交接等待、父级综合时延、升级等待和端到端关键路径时延。
- 成本指标 / Cost Metrics: child budget utilization, budget conservation error, duplicate-work cost, parent synthesis cost, and cost per validated parent result. / 子预算利用率、预算守恒误差、重复工作成本、父级综合成本和单位父级验证成功成本。
- 风险指标 / Risk Metrics: missing parent event, authority widening, hard-constraint dilution, evidence loss, child overrun, orphaned task, and unowned final validation. / 父事件缺失、权限扩大、硬约束弱化、证据丢失、子任务越界、孤儿任务和最终验证无人负责。
- Trace 指标 / Trace Metrics: task/run/step/parent identity propagation, snapshot-version propagation, child stop reasons, authority and budget records, evidence handoff, conflict preservation, and parent synthesis linkage. / 任务/运行/步骤/父事件标识传播、快照版本传播、子任务停止原因、权限与预算记录、证据交接、冲突保留和父级综合关联。

### Required Probe Coverage / 必需探针覆盖

Enable identity and parent linkage (`PROBE_0001`), contract completeness (`PROBE_0002`), budget (`PROBE_0004`), step closure (`PROBE_0005`), evidence (`PROBE_0006`), tool and action (`PROBE_0007`) when delegated actions exist, drift (`PROBE_0010`), validation (`PROBE_0011`), stop/escalation (`PROBE_0012`), outcome (`PROBE_0013`) when available, privacy/governance (`PROBE_0014`), and self-health (`PROBE_0015`). / 启用身份与父子关联、契约完整性、预算、步骤闭环、证据、工具与动作（存在委派动作时）、漂移、验证、停止升级、结果回接（可用时）、隐私治理和自健康探针。

Require `parent_event_id` propagation, inherited snapshot versions, least authority, explicit child budget, evidence-bearing handoff, child stop reason, and parent-owned final validation. Block audit-grade completion when the parent chain is irrecoverable or hard constraints diverge without an approved revision. / 强制传播 `parent_event_id`、继承快照版本、最小权限、显式子预算、带证据交接、子任务停止原因和父级最终验证责任。父子链不可恢复或硬约束未经批准发生分歧时，阻断审计级完成。
