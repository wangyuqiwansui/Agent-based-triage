# Extension Candidate / 扩展候选

Cell / 交织点: reasoning-orchestration / 推理 x 编排
Capability / 能力: Reasoning / 推理
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

Runtime Protocols / 运行协议: [Reasoning Execution Flow / 推理执行流程](../../reasoning-execution-flow.md); [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md).

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reasoning / 推理 x Orchestration / 编排 (Orchestration / 编排).
- 论文依据 / Article Basis: 空白单元 / Empty cell; arXiv:2605.13850 leaves this intersection unnamed. / 空白单元 / Empty cell；arXiv:2605.13850 未命名该交织点。
- 问题 / Problem: The article leaves this intersection unnamed; use it only if workflow evidence shows that Reasoning / 推理 needs Orchestration / 编排. / 论文未命名该交织点；仅当工作流证据表明 Reasoning / 推理 需要 Orchestration / 编排 时使用。
- 架构方案 / Architectural Solution: Keep this as an extension candidate and define a concrete pattern only after repeated workflow evidence appears. / 将其保留为扩展候选，仅在反复出现工作流证据后再定义具体模式。
- 工程权衡 / Engineering Trade-offs: This avoids inventing taxonomy, but leaves a deliberate gap until practice justifies the pattern. / 这避免凭空发明分类，但在实践证明前会保留有意空白。
- 工作流诊断用途 / Workflow Diagnosis Use: Extension candidate / 扩展候选.

### Shared Protocol Role, Not Promotion / 共享协议角色，不构成晋升

`PATTERN_0051` needs controller-mediated coordination when one run manages routing, contracts, budgets, validators, tools, mode switches, terminal transitions, and `PATTERN_0052` feedback. This is valid evidence that orchestration supports the runtime, but one draft protocol is not repeated independent evidence for promoting this empty matrix cell into a named pattern. / 当单次运行需要管理路由、契约、预算、验证器、工具、模式切换、终态转换和 `PATTERN_0052` 反馈时，`PATTERN_0051` 需要控制器协调。这说明编排能够支撑运行时，但单份草案协议不构成将此空白矩阵单元晋升为命名模式所需的反复独立证据。

### Pattern Template / 模式模板

- 状态 / Status: 扩展候选 / Extension candidate.
- 模式清单 / Patterns: 待发现 / To be discovered.
- 诊断用途 / Diagnostic Use: Extension candidate / 扩展候选.
- 适用工作流节点 / Applicable Workflow Nodes: 方案设计、事故修复 / Design, incident repair.
- 当前症状 / Current Symptoms: Route, budget, validator, tool, and terminal-state decisions are scattered across components; switches lose unfinished work or identity context; probe feedback has no single control owner. / 路由、预算、验证器、工具和终态决策分散在多个组件；换路时丢失未完成工作或标识上下文；探针反馈没有单一控制责任方。
- 适配信号 / Fit Signals: 推理需要协调多种证据、工具、角色和决策点 / Reasoning coordinates evidence, tools, roles, and decision points.
- 调整方向 / Adjustment Direction: Keep the cell as an extension candidate while using an explicit controller for cross-mode runtime state and probe feedback. Collect independent workflow evidence before naming a distinct reasoning-orchestration pattern. / 保持本单元为扩展候选，同时使用显式控制器管理跨模式运行状态与探针反馈；命名独立推理编排模式前收集独立工作流证据。
- 修改方式 / How To Modify: 1) Define one state-machine owner. 2) Centralize identity, contract version, budget counters, validators, switch records, and terminal gates. 3) Accept versioned probe feedback with advisory versus blocking authority. 4) Persist only externally verifiable decision events. 5) Record independent cases and failure-path checks for any later promotion proposal. / 1）定义单一状态机责任方；2）集中管理标识、契约版本、预算计数、验证器、换路记录和终态闸门；3）接收带版本且区分建议/阻断权限的探针反馈；4）只持久化外部可核验决策事件；5）为后续晋升提案记录独立案例和失败路径检查。
- 输入 / Inputs: Normalized task, reasoning contract, current state, tool and validator availability, budget counters, workflow events, and probe feedback. / 标准化任务、推理契约、当前状态、工具与验证器可用性、预算计数、工作流事件和探针反馈。
- 输出 / Outputs: Next authorized transition, mode and switch record, dispatched work, validation gate result, terminal state, and correlated event stream. / 下一授权状态转换、模式与换路记录、已分派工作、验证闸门结果、终态和已关联事件流。
- 风险与治理 / Risks & Governance: A controller can become a single point of failure or silently change business semantics. Keep governance and validator precedence explicit, version transitions, require idempotency, observe controller and probe health, and do not treat advice as business truth. / 控制器可能成为单点故障或静默改变业务语义。应明确治理与验证器优先级、版本化状态转换、要求幂等、监控控制器与探针健康，并禁止将建议视为业务事实。

Observability Metrics File / 可观测性指标文件: [reasoning-orchestration-observability.md](reasoning-orchestration-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
