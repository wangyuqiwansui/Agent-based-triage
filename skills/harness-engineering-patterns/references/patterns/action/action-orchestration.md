# Plan-and-Execute / 计划并执行

Cell / 交织点: action-orchestration / 行动 x 编排
Capability / 能力: Action / 行动
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Plan-and-Execute separates a planner that builds a subtask graph from executors that carry the subtasks out under coordination. / 计划并执行将"构建子任务图的规划器"与"在协调下执行子任务的执行器"分离。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Action / 行动 x Orchestration / 编排 (Orchestration / 编排).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Action / 行动 x Orchestration / 编排 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Action / 行动 x Orchestration / 编排 映射到该单元。
- 问题 / Problem: Direct execution can be brittle when tasks require multiple dependent actions and changing state. / 当任务需要多个相互依赖的行动和变化状态时，直接执行会很脆弱。
- 架构方案 / Architectural Solution: The planner decomposes the goal into a subtask DAG with dependencies; executors run subtasks in dependency order; a coordinator observes results, marks completion, and replans when execution diverges. The article frames this as the Saga pattern adapted to agents: each executed step may need a compensating action if a later step fails. / 规划器将目标分解为带依赖的子任务 DAG；执行器按依赖顺序执行；协调器观察结果、标记完成，并在执行偏离时重新规划。论文将其类比为适配到 Agent 的 Saga 模式：每个已执行步骤在后续步骤失败时可能需要补偿动作。
- 工程权衡 / Engineering Trade-offs: Improves transparency and control, but plans go stale as state changes; over-decomposition adds planning latency and coordination overhead, under-decomposition hides dependencies and blocks parallelism. / 提升透明度和控制力，但计划会随状态变化过期；过度分解增加规划时延和协调开销，分解不足则隐藏依赖并阻碍并行。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when actions need explicit planning, execution, and coordination. / 当行动需要明确计划、执行和协调时使用。

### Plan Contract / 计划契约

Each plan should carry / 每份计划应包含:

```yaml
plan:
  goal: ""
  subtasks:
    - subtask_id: ""
      description: ""
      depends_on: []
      executor: ""            # tool, skill, or subagent / 工具、技能或子 Agent
      done_criteria: ""       # observable completion signal / 可观测完成信号
      compensation: ""        # rollback or repair action if later steps fail / 后续失败时的回滚或修复动作
      risk_level: low | medium | high
  replan_triggers: []          # state divergence, failed done_criteria, new constraints / 状态偏离、完成判据失败、新约束
  stop_conditions: []          # max replans, budget, human-escalation rules / 最大重规划次数、预算、人工升级规则
```

Coordination rules / 协调规则:

- Execute only subtasks whose dependencies are complete; run independent subtasks in parallel when executors allow. / 只执行依赖已完成的子任务；执行器允许时并行运行相互独立的子任务。
- Mark completion only on observable `done_criteria`, never on executor self-report alone. / 只依据可观测 `done_criteria` 标记完成，不能仅凭执行器自述。
- On divergence, replan the remaining graph instead of patching one step; bound replans with `stop_conditions`. / 偏离时对剩余子图重新规划而非修补单步；用 `stop_conditions` 约束重规划次数。
- High-risk subtasks route through the approval gate before execution (see [governance-routing](../governance/governance-routing.md)). / 高风险子任务执行前经审批门禁路由（见 [governance-routing](../governance/governance-routing.md)）。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Plan-and-Execute / 计划并执行.
- 诊断用途 / Diagnostic Use: Use when actions need explicit planning, execution, and coordination. / 当行动需要明确计划、执行和协调时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 发布交付、事故修复 / Delivery, incident repair.
- 当前症状 / Current Symptoms: Multi-step actions run ad hoc without dependency tracking; failures midway leave state half-changed with no compensation path; nobody can tell which steps remain. / 多步行动临时串联、无依赖跟踪；中途失败让状态半改无补偿路径；无人能说清剩余步骤。
- 适配信号 / Fit Signals: 行动涉及多个工具、系统状态、依赖和回滚路径 / Actions involve tools, system state, dependencies, and rollback paths.
- 调整方向 / Adjustment Direction: Introduce an explicit plan artifact with subtask DAG, done criteria, and compensation actions; separate planner and executor roles; add replan triggers and stop conditions. / 引入显式计划产物（子任务 DAG、完成判据、补偿动作）；分离规划与执行角色；增加重规划触发器和停止条件。
- 修改方式 / How To Modify: 1) Write the plan contract above into the workflow. 2) Gate completion on observable criteria. 3) Define compensation per state-changing subtask. 4) Bound replanning and wire high-risk subtasks to the approval gate. / 1）将上方计划契约写入工作流；2）以可观测判据判定完成；3）为每个改状态子任务定义补偿；4）约束重规划并将高风险子任务接入审批门禁。
- 输入 / Inputs: Goal statement, available executors and tools, current system state, risk policy. / 目标陈述、可用执行器与工具、当前系统状态、风险策略。
- 输出 / Outputs: Plan artifact, per-subtask execution records, replan events, compensation log. / 计划产物、逐子任务执行记录、重规划事件、补偿日志。
- 风险与治理 / Risks & Governance: Stale plans acting on changed state (`FAIL_0006` state loss if progress is not recorded); orchestration without compensation turns partial failure into unrecoverable state; record all subtask results per `GOV_0002` and route high-risk actions per `GOV_0001`. / 过期计划作用于已变化状态（进度未记录时对应 `FAIL_0006` 状态丢失）；无补偿的编排会让部分失败变成不可恢复状态；子任务结果按 `GOV_0002` 全量记录，高风险动作按 `GOV_0001` 路由审批。

Observability Metrics File / 可观测性指标文件: [action-orchestration-observability.md](action-orchestration-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
