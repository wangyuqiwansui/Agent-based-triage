# Extension Candidate / 扩展候选 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-orchestration / 推理 x 编排
Capability / 能力: Reasoning / 推理
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-orchestration.md](reasoning-orchestration.md)
Shared Probe Suite / 共享探针套件: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe the supporting controller role without treating the evidence as promotion of the extension candidate. / 使用以下指标观察控制器支撑作用，但不得将这些证据直接视为扩展候选晋升。

- 质量指标 / Quality Metrics: state-transition validity, mandatory-validator coverage, event-chain completeness, switch-record completeness, terminal-state consistency, and controller recovery success. / 状态转换有效率、必选验证覆盖率、事件链完整率、换路记录完整率、终态一致率和控制器恢复成功率。
- 时延指标 / Latency Metrics: per-stage and end-to-end latency, controller decision overhead, probe-feedback handling latency, queue wait, and protected-transition delay. / 分阶段与端到端时延、控制器决策开销、探针反馈处理延迟、队列等待和受保护转换延迟。
- 成本指标 / Cost Metrics: per-step and per-mode model/tool cost, retry amplification, invalid dispatch cost, controller overhead, and cost per validated success. / 分步骤与分模式模型/工具成本、重试放大、无效分派成本、控制器开销和单位验证成功成本。
- 风险指标 / Risk Metrics: invalid transition, duplicated dispatch, budget continuation after exhaustion, ignored blocking signal, missing terminal reason, and controller/probe outage release. / 非法转换、重复分派、预算耗尽后继续、忽略阻断信号、终态原因缺失和控制器/探针故障放行。
- Trace 指标 / Trace Metrics: task-run-step-parent correlation, contract and event version coverage, route and switch reason coverage, validator linkage, stop/escalation context, and data-source completeness. / 任务-运行-步骤-父事件关联、契约与事件版本覆盖、路由与换路原因覆盖、验证器关联、停止/升级上下文和来源完整性。

### Required Probe Coverage / 必需探针覆盖

Enable identity, contract, routing, budget, step, evidence, tool, drift, validation, stop/escalation, privacy/governance, and self-health probes: `PROBE_0001`, `PROBE_0002`, `PROBE_0003`, `PROBE_0004`, `PROBE_0005`, `PROBE_0006`, `PROBE_0007`, `PROBE_0010`, `PROBE_0011`, `PROBE_0012`, `PROBE_0014`, and `PROBE_0015`. Add branch, iteration, or outcome probes when those states exist. / 启用身份、契约、路由、预算、步骤、证据、工具、漂移、验证、停止升级、隐私治理和自健康探针；存在并行、迭代或结果回接状态时增加对应探针。

Block high-risk completion when a mandatory validator is missing or failed, an irreversible action lacks authorization, a hard constraint drifted without approval, the event chain is irrecoverable, or the terminal reason is missing. Probe advice cannot silently change business semantics. / 高风险完成在以下情况阻断：必选验证器缺失或失败、不可逆动作无授权、硬约束未经批准漂移、事件链不可恢复、终态原因缺失。探针建议不得静默改变业务语义。
