# Plan-and-Execute / 计划并执行

Cell / 交织点: action-orchestration / 行动 x 编排

Pattern ID / 模式 ID: `PATTERN_0037`

Version / 版本: `1.1.0`

Capability / 能力: Action / 行动

Mode / 模式: Orchestration / 编排

Status / 状态: Active engineering pattern / 有效工程模式

Source / 来源: arXiv:2605.13850; expanded with the user-provided Agent Workflow Execution Framework and Workflow Observability Probe Framework. / arXiv:2605.13850；并结合用户提供的《Agent 工作流执行框架》和《工作流可观测性探针框架》扩展。

Use this file as the normative design source for the action-orchestration cell. Use [`goal-contract.schema.json`](../../../schemas/goal-contract.schema.json), [`workflow-plan.schema.json`](../../../schemas/workflow-plan.schema.json), [`workflow-plan-patch.schema.json`](../../../schemas/workflow-plan-patch.schema.json), [`workflow-checkpoint.schema.json`](../../../schemas/workflow-checkpoint.schema.json), and [`workflow-execution-result.schema.json`](../../../schemas/workflow-execution-result.schema.json) as machine-readable artifact contracts. Use [`plan_execution.py`](../../../runtime/plan_execution.py) as the deterministic reference kernel, [`plan_execution_sqlite_store.py`](../../../runtime/plan_execution_sqlite_store.py) for transactional local persistence, [`plan_tool_dispatch.py`](../../../runtime/plan_tool_dispatch.py) for persist-before-dispatch coordination, [`plan_execution_events.py`](../../../runtime/plan_execution_events.py) for the dual-contract observability adapter, and [`plan_execution_completion.py`](../../../runtime/plan_execution_completion.py) for the terminal completion gate. / 将本文档作为“行动 x 编排”单元的规范设计来源。机器可读制品契约以目标契约、工作流计划、计划补丁、检查点和工作流执行结果 Schema 为准；确定性执行语义以 `plan_execution.py` 参考内核为准，事务型本地持久化使用 `plan_execution_sqlite_store.py`，分派前持久化协调使用 `plan_tool_dispatch.py`，双契约可观测性适配使用 `plan_execution_events.py`，终态完成闸门使用 `plan_execution_completion.py`。

## Quick Navigation / 快速导航

- [Design Pattern / 设计模式](#design-pattern--设计模式)
- [Hard Invariants / 硬不变量](#hard-invariants--硬不变量)
- [Goal Contract / 目标契约](#goal-contract--目标契约)
- [Mechanical State Machine / 机械状态机](#mechanical-state-machine--机械状态机)
- [Checkpoint And Idempotency / 检查点与幂等](#checkpoint-and-idempotency--检查点与幂等)
- [Transactional Dispatch Boundary / 事务型分派边界](#transactional-dispatch-boundary--事务型分派边界)
- [Local Replanning / 局部重规划](#local-replanning--局部重规划)
- [Completion Gate / 完成闸门](#completion-gate--完成闸门)
- [Reference Kernel / 参考内核](#reference-kernel--参考内核)
- [Acceptance / 验收](#acceptance--验收)

## Design Pattern / 设计模式

Plan-and-Execute externalizes the goal, compiles a dependency graph, validates it before dispatch, executes only ready steps, records mechanical truth separately from the plan, and recovers through a local versioned patch. It is not a longer todo list and not permission to act. / 计划并执行将目标外部化，编译依赖图，分派前校验，只执行就绪步骤，将机械执行真值与计划分离，并通过局部版本化补丁恢复。它不是更长的待办列表，也不代表获得行动权限。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Action / 行动 x Orchestration / 编排.
- 论文依据 / Article Basis: 代表性定义 / Representative definition; the source table maps Plan-and-Execute to this cell and describes a planner, an executor set, dependency-aware coordination, and Saga-like compensation. / 来源表将“计划并执行”映射到本单元，并描述规划器、执行器集合、依赖感知协调和类似 Saga 的补偿。
- 问题 / Problem: Direct execution becomes brittle when actions have dependencies, changing external state, partial failure, or irreversible effects. / 当行动具有依赖、变化的外部状态、部分失败或不可逆副作用时，直接执行会变得脆弱。
- 架构方案 / Architectural Solution: Externalize a goal contract, compile and validate an immutable Plan DAG, schedule only ready steps, admit every action separately, persist checkpoints and idempotency records, and recover through a local plan patch. / 外部化目标契约，编译并校验不可变计划 DAG，只调度就绪步骤，单独准入每个动作，持久化检查点与幂等记录，并通过局部计划补丁恢复。
- 工程权衡 / Engineering Trade-offs: The pattern improves control, recovery, and auditability but adds planning latency, state persistence, reconciliation, and coordination overhead; over-decomposition increases overhead while under-decomposition hides risk and dependencies. / 本模式提升控制、恢复和可审计性，但增加规划时延、状态持久化、核验和协调开销；过度拆解增加开销，拆解不足则隐藏风险与依赖。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when actions need explicit planning, dependency-aware execution, durable state, and bounded recovery. / 当行动需要显式规划、依赖感知执行、持久状态和有界恢复时使用。
- 工程扩展 / Engineering Expansion: Add protected `DONE`, explicit `UNKNOWN → VERIFYING`, versioned local patches, and an independent observability plane. / 增加受保护的 `DONE`、显式 `UNKNOWN → VERIFYING`、版本化局部补丁和独立观测面。

## System Boundary / 系统边界

```text
Goal input / 目标输入
  -> Goal contract / 目标契约
  -> Planner / 规划器
  -> Plan DAG / 计划 DAG
  -> Plan validator / 计划校验器
  -> Scheduler / 调度器
  -> Tool-dispatch admission / 工具分派准入
  -> Executor / 执行器
  -> Checkpoint + idempotency ledger / 检查点 + 幂等账
  -> Completion evidence or recovery / 完成证据或恢复

Execution events / 执行事件
  -> Observability probes / 可观测性探针
  -> Metrics, alerts, and authorized feedback / 指标、告警与有权限反馈
```

Keep these separations explicit / 明确保持以下分离：

- Planner proposes a graph; it does not perform business actions. / 规划器提出计划图，不执行业务动作。
- Plan Validator protects invariants; it does not optimize task content. / 计划校验器保护不变量，不优化任务内容。
- Scheduler selects ready work; selection is not authorization. / 调度器选择就绪工作；选中不等于授权。
- Executor performs one admitted step; it does not redefine the goal. / 执行器执行一个已准入步骤，不重新定义目标。
- Checkpoint records where the workflow believes it is; the idempotency ledger records whether a business action happened. / 检查点记录流程认为自己走到哪里；幂等账记录业务动作是否发生。
- Probe observes execution facts; it does not manufacture business truth or replace the executor. / 探针观察执行事实，不制造业务真相，也不替代执行器。

## Hard Invariants / 硬不变量

1. Bind every plan revision to exactly one versioned goal contract. / 每个计划修订只绑定一个版本化目标契约。
2. Execute a step only when every declared dependency is `DONE`. / 仅当全部声明依赖均为 `DONE` 时执行步骤。
3. Mark `DONE` only from declared completion criteria and observable evidence. / 只有满足声明的完成判据并取得可观测证据时才标记 `DONE`。
4. Never mutate, reset, delete, or replay a `DONE` business fact through replanning. / 重规划不得修改、重置、删除或重放 `DONE` 业务事实。
5. Patch only the failed step and its affected downstream subgraph; preserve unrelated steps and existing dependencies. / 只修补失败步骤及受影响下游子图；保留无关步骤和已有依赖。
6. Treat an interrupted or ambiguous state-changing action as `UNKNOWN`; verify external state before any retry. / 中断或结果不确定的改状态动作进入 `UNKNOWN`；任何重试前先核验外部状态。
7. Require a durable idempotency identity before every state-changing action. / 每个改状态动作执行前必须具备持久幂等身份。
8. Require current authorization and approval at dispatch time; plan inclusion never grants authority. / 分派时必须具备当前授权与审批；步骤进入计划不等于获得权限。
9. Preserve immutable plan, patch, checkpoint, action-result, and external-receipt evidence. / 保留不可变的计划、补丁、检查点、动作结果与外部回执证据。
10. Fail closed when a protected high-risk transition lacks current evidence, authorization, or probe health. / 受保护高风险转换缺少当前证据、授权或探针健康时默认阻断。
11. Persist-before-dispatch: commit the step state, idempotency snapshot, contiguous events, and a bounded outbox binding before entering a tool side-effect boundary. / 分派前持久化：进入工具副作用边界前，共同提交步骤状态、幂等快照、连续事件和有界 Outbox 绑定。
12. Never equate all steps being `DONE` with workflow completion; seal a result only after the completion gate rechecks goal evidence, validators, approvals, receipts, and probe health. / 绝不把全部步骤 `DONE` 等同于工作流完成；只有完成闸门重新检查目标证据、验证器、审批、回执和探针健康后才能封存结果。

## Roles / 角色

| Role / 角色 | Owns / 负责 | Must not / 禁止 |
| --- | --- | --- |
| Goal owner / 目标负责人 | Objective, scope, constraints, success criteria, completion evidence, permission boundary. / 目标、范围、约束、成功标准、完成证据、权限边界。 | Allow a local failure message to silently redefine the goal. / 允许局部失败信息静默改写目标。 |
| Planner / 规划器 | Initial DAG and candidate recovery patch. / 初始 DAG 与候选恢复补丁。 | Execute tools or overwrite confirmed business facts. / 执行工具或覆盖已确认业务事实。 |
| Plan Validator / 计划校验器 | Schema, DAG, handler, dependency, effect, idempotency, approval, and patch-boundary checks. / Schema、DAG、处理器、依赖、副作用、幂等、审批和补丁边界校验。 | Approve an invalid plan because execution has already started. / 因执行已开始而放行无效计划。 |
| Scheduler / 调度器 | Deterministic ready-set calculation and bounded concurrency. / 确定性就绪集计算与有界并发。 | Run a blocked, unknown, verifying, or dependency-incomplete step. / 运行阻塞、未知、核验中或依赖未完成步骤。 |
| Executor / 执行器 | One admitted handler call and returned public result. / 一次已准入处理器调用及其公开结果。 | Replan the goal or mark itself complete without evidence. / 重规划目标或无证据自报完成。 |
| State and recovery store / 状态与恢复存储 | Step truth, checkpoints, immutable events, receipts, idempotency records. / 步骤真值、检查点、不可变事件、回执、幂等记录。 | Collapse missing or unknown into failed, success, or zero. / 将缺失或未知折叠为失败、成功或零。 |
| Probe suite / 探针套件 | Correlation, quality signals, alerts, and configured gates. / 关联、质量信号、告警和已配置门控。 | Infer private chain-of-thought or invent outcome linkage. / 推断私密思维过程或编造结果关联。 |

## Goal Contract / 目标契约

Do not run a long or state-changing workflow from a prompt alone. Compile and seal the goal contract before planning. / 长任务或改状态工作流不得只依赖 Prompt；规划前先编译并封存目标契约。

Required content / 必需内容：

- Objective and explicit in-scope/out-of-scope boundaries. / 目标及明确的范围内、范围外边界。
- Versioned business, technical, safety, compliance, budget, time, and permission constraints. / 版本化业务、技术、安全、合规、预算、时间和权限约束。
- Observable success criteria and required evidence. / 可观测成功标准及所需证据。
- Completion evidence for the whole workflow. / 整体工作流完成证据。
- Recovery policy: preserve `DONE`, patch only affected subgraph, verify `UNKNOWN` before retry. / 恢复策略：保护 `DONE`，只修补受影响子图，`UNKNOWN` 重试前核验。
- Permission boundary and actions that require approval. / 权限边界及需要审批的动作。

Changing the goal creates a new goal-contract version and triggers impact analysis. It is not a plan patch. / 变更目标必须创建新的目标契约版本并触发影响分析；它不是计划补丁。

## Plan Graph Contract / 计划图契约

A compiled plan is an immutable DAG revision. Mutable status lives in checkpoint step records, not inside the plan artifact. / 已编译计划是不可变 DAG 修订；可变状态存放在检查点步骤记录中，不写回计划制品。

Every step declares / 每个步骤声明：

- Stable `step_id`, description, and exact versioned handler. / 稳定 `step_id`、描述和确切版本化处理器。
- Dependencies, named inputs, and named outputs. / 依赖、命名输入和命名输出。
- One or more observable completion criteria and evidence types. / 一个或多个可观测完成判据及证据类型。
- Whether a checkpoint is required after completion. / 完成后是否必须生成检查点。
- Effect class: `read_only`, `reversible_write`, or `irreversible_external`. / 副作用类型：只读、可逆写或不可逆外部动作。
- Durable idempotency key for every write; compensation for reversible writes; current approval binding for irreversible actions. / 每个写动作的持久幂等键；可逆写的补偿；不可逆动作的当前审批绑定。

Reject duplicate IDs, missing dependencies, cycles, unversioned handlers, empty completion criteria, writes without idempotency, reversible writes without compensation, and irreversible actions without approval binding. / 拒绝重复 ID、缺失依赖、依赖环、未版本化处理器、空完成判据、无幂等写动作、无补偿可逆写以及无审批绑定的不可逆动作。

## Mechanical State Machine / 机械状态机

```text
TODO -> DOING -> DONE
          |        ^
          v        |
        FAILED     |

TODO -> BLOCKED

DOING -> UNKNOWN -> VERIFYING -> DONE
                              -> FAILED
```

Transition rules / 转换规则：

- `TODO → DOING`: all dependencies are `DONE`, retry budget remains, and dispatch admission passes. / 全部依赖均 `DONE`、仍有重试预算且分派准入通过。
- `DOING → DONE`: completion evidence exists; state-changing action also has a confirmed successful idempotency record. / 存在完成证据；改状态动作还必须具有已确认成功的幂等记录。
- `DOING → FAILED`: execution or validation produced a confirmed failure. / 执行或验证产生已确认失败。
- `TODO → BLOCKED`: an upstream failure or unresolved governance condition prevents readiness. / 上游失败或未解决治理条件阻止就绪。
- `DOING → UNKNOWN`: the system cannot confirm whether an external side effect happened. / 系统无法确认外部副作用是否发生。
- `UNKNOWN → VERIFYING`: start reconciliation against the provider or business system. / 开始与提供方或业务系统核对。
- `VERIFYING → DONE | FAILED`: close only with external evidence. / 仅凭外部证据关闭为成功或失败。

There is no `UNKNOWN → DOING` shortcut and no `DONE → TODO` transition. / 不存在 `UNKNOWN → DOING` 捷径，也不存在 `DONE → TODO` 转换。

## Planning And Validation Workflow / 规划与校验流程

1. Normalize the user goal and freeze the goal contract. / 标准化用户目标并冻结目标契约。
2. Inventory handlers, current system state, authority, risk, and external dependencies. / 盘点处理器、当前系统状态、权限、风险和外部依赖。
3. Decompose by business responsibility and observable outputs, not by arbitrary token-sized fragments. / 按业务职责和可观测输出拆解，不按任意 token 大小切碎。
4. Build the DAG and identify the critical path plus safely parallel ready sets. / 构建 DAG，并识别关键路径和可安全并行的就绪集。
5. Bind completion criteria, checkpoint policy, side-effect class, idempotency, compensation, and approval to every step. / 为每个步骤绑定完成判据、检查点策略、副作用类型、幂等、补偿和审批。
6. Run Schema and semantic validation before any dispatch. / 任何分派前执行 Schema 与语义校验。
7. Seal the plan hash and persist the goal, plan, and initial checkpoint together. / 封存计划哈希，并共同持久化目标、计划和初始检查点。

## Scheduling And Execution / 调度与执行

At each scheduling cycle / 每个调度周期：

1. Reload authoritative plan, checkpoint, idempotency ledger, approvals, and external-state evidence. / 重载权威计划、检查点、幂等账、审批和外部状态证据。
2. Calculate the deterministic ready set. / 计算确定性就绪集。
3. Recheck deadline, budget, authority, approval, state evidence, concurrency, and probe health. / 重新检查期限、预算、权限、审批、状态证据、并发和探针健康。
4. Route tool actions through [Tool Dispatch / 工具分派](action-routing.md); plan selection must not bypass its capability frontier or admission checks. / 工具动作必须经过工具分派；进入计划不得绕过能力前沿或准入检查。
5. Persist-before-dispatch: atomically commit the current checkpoint, new internal events, idempotency snapshot, and bounded outbox binding before invoking the handler. / 分派前持久化：调用处理器前，原子提交当前检查点、新内部事件、幂等快照和有界 Outbox 绑定。
6. Let Tool Dispatch own the durable side-effect lease and authoritative execution result; do not duplicate or weaken its certainty classification. / 由工具分派拥有持久副作用租约和权威执行结果；不得重复实现或弱化其确定性分类。
7. Atomically record the mapped plan result and outbox acknowledgement after execution. / 执行后原子记录映射后的计划结果与 Outbox 确认。
8. Persist a checkpoint at required boundaries before releasing downstream work. / 在要求的边界持久化检查点后，再放行下游工作。

Parallel execution is allowed only for steps in the same ready set whose handlers, state scopes, rate limits, idempotency domains, and approval scopes do not conflict. / 只有同一就绪集中处理器、状态范围、限流、幂等域和审批范围互不冲突的步骤才可并行。

## Checkpoint And Idempotency / 检查点与幂等

Checkpoint answers “where can the workflow resume?” It contains the bound goal and plan revision, all step states, attempts, output digests, evidence references, errors, external receipts, replan count, and idempotency records. / 检查点回答“工作流可以从哪里恢复？”，包含绑定的目标与计划修订、全部步骤状态、尝试次数、输出摘要、证据引用、错误、外部回执、重规划次数和幂等记录。

Idempotency answers “did this business action happen?” A record binds `idempotency_key`, `step_id`, `request_digest`, status, provider reference, and result digest. / 幂等回答“这个业务动作是否发生？”，记录绑定幂等键、步骤、请求摘要、状态、提供方引用和结果摘要。

On process recovery / 进程恢复时：

- Interrupted read-only `DOING` may return to `TODO`. / 中断的只读 `DOING` 可回到 `TODO`。
- Interrupted write `DOING` becomes `UNKNOWN`; never silently redispatch it. / 中断的写 `DOING` 进入 `UNKNOWN`；绝不静默重分派。
- A confirmed successful idempotency record is immutable and reusable. / 已确认成功的幂等记录不可变且可复用。
- The reference checkpoint is portable, but production must persist checkpoint, event, claim, and dispatch transactionally. / 参考检查点可移植，但生产必须以事务方式持久化检查点、事件、领取和分派。

## Transactional Dispatch Boundary / 事务型分派边界

Use `SqlitePlanExecutionStore.initialize_run()` to commit the goal, first plan revision, initial checkpoint, and initial event suffix. Every later writer must present the exact `expected_head_hash`; stale writers fail closed. `commit_session()` advances the plan head only when the internal event suffix is contiguous and writes the checkpoint, embedded idempotency snapshot, events, and outbox changes in one `BEGIN IMMEDIATE` transaction. / 使用 `SqlitePlanExecutionStore.initialize_run()` 共同提交目标、首个计划修订、初始检查点和初始事件后缀。此后每个写入者都必须提供确切 `expected_head_hash`；陈旧写入默认阻断。只有内部事件后缀连续时，`commit_session()` 才会在一个 `BEGIN IMMEDIATE` 事务中推进计划头并写入检查点、其中的幂等快照、事件和 Outbox 变更。

`PlanToolDispatchCoordinator.dispatch_step()` implements persist-before-dispatch, then calls the existing governed `ToolDispatchRuntime`, then commits the result. The plan database and Tool Dispatch database are a recoverable two-phase boundary, not one distributed transaction and not end-to-end exactly once. If the process dies after the tool boundary but before the second plan commit, the pending outbox item remains visible and `restore_session()` changes an interrupted write to `UNKNOWN`; reconcile the provider state before retry. / `PlanToolDispatchCoordinator.dispatch_step()` 实现分派前持久化，随后调用既有受治理 `ToolDispatchRuntime`，最后提交结果。计划数据库与工具分派数据库构成可恢复的两阶段边界，而不是一个分布式事务，也不是端到端严格一次。若进程在工具边界之后、第二次计划提交之前退出，待处理 Outbox 项仍然可见，`restore_session()` 会把中断写动作转为 `UNKNOWN`；重试前必须先核对提供方状态。

Outbox rows contain only an action-intent binding and hashes, never raw parameters, secrets, or private reasoning. Delivery and reconciliation are at-least-once; business writes remain protected by Tool Dispatch durable idempotency. / Outbox 行只包含行动意图绑定与哈希，绝不包含原始参数、密钥或私密推理。交付与对账语义为至少一次；业务写动作仍由工具分派持久幂等保护。

## Local Replanning / 局部重规划

Use this recovery sequence / 使用以下恢复序列：

```text
Confirmed FAILED step / 已确认 FAILED 步骤
  -> derive failed-and-affected descendants / 推导失败节点及受影响下游
  -> compile Plan Patch / 编译计划补丁
  -> validate blast radius and protected facts / 校验影响范围与受保护事实
  -> seal next plan revision / 封存下一计划修订
  -> reset only patched non-DONE records / 仅重置补丁内非 DONE 记录
  -> continue from new ready set / 从新就绪集继续
```

A valid patch / 合法补丁：

The exact recovery boundary is the failed step and affected subgraph / 精确恢复边界是失败节点及受影响子图。

- Binds the current plan ID, revision, and hash. / 绑定当前计划 ID、修订和哈希。
- Names one or more `FAILED` roots and the exact derived downstream impact set. / 指定一个或多个 `FAILED` 根节点及精确推导的下游影响集。
- Replaces every affected existing step so omission cannot delete work silently. / 替换每个受影响的已有步骤，避免通过遗漏静默删除工作。
- Does not touch `DONE`, `DOING`, `UNKNOWN`, `VERIFYING`, or unrelated steps. / 不触碰 `DONE`、`DOING`、`UNKNOWN`、`VERIFYING` 或无关步骤。
- Does not remove an existing dependency or change an existing write idempotency identity. / 不移除已有依赖，也不改变已有写动作幂等身份。
- Adds only steps connected to the affected subgraph. / 只新增与受影响子图相连的步骤。
- Increments the plan revision exactly once and remains within `max_replans`. / 计划修订严格递增一次，且不超过 `max_replans`。

Do not automatically compensate a successful action. Compensation is a new governed action, not time travel; execute it only when the goal contract, current state, authorization, and safety condition require it. / 不要自动补偿成功动作。补偿是新的受治理动作，不是时间倒流；只有目标契约、当前状态、权限和安全条件要求时才执行。

## Observability Integration / 可观测性集成

Read [Plan-and-Execute Observability Metrics / 计划并执行可观测性指标](action-orchestration-observability.md) and [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md). Emit stable task, run, plan, patch, step, attempt, action, idempotency, checkpoint, evidence, approval, and provider identities. / 读取本模式可观测性指标与工作流探针协议；发出稳定的任务、运行、计划、补丁、步骤、尝试、动作、幂等、检查点、证据、审批和提供方标识。

Use sidecar mode for initial observation, advisory mode for plan-quality and recovery guidance, and inline gates for protected transitions such as irreversible dispatch, `DONE`, retry after ambiguity, and final workflow completion. / 初始观测使用旁路模式，计划质量与恢复建议使用建议模式，不可逆分派、进入 `DONE`、不确定结果后的重试和最终完成等受保护转换使用内联门控。

`PlanExecutionEventAdapter` emits plan lifecycle, step closure, recovery, and completion through the shared `reasoning-event` contract. State-changing tool events remain in the normative `tool-execution-event` stream because shared reasoning tool events are read-only by design. Consumers must correlate both validated streams; they must not rewrite a write action as a read-only reasoning tool event. / `PlanExecutionEventAdapter` 通过共享 `reasoning-event` 契约发送计划生命周期、步骤闭环、恢复与完成事件。改状态工具事件保留在规范 `tool-execution-event` 流中，因为共享推理工具事件按设计只读。消费方必须关联两条已校验事件流；不得把写动作改写成只读推理工具事件。

## Completion Gate / 完成闸门

`finalize_workflow_execution()` is the only reference path that seals [`workflow-execution-result.schema.json`](../../../schemas/workflow-execution-result.schema.json). It fails closed unless every step is `DONE`, every write has a confirmed immutable ledger result and provider reference, every goal success criterion and whole-goal evidence type is covered, every supplied mandatory validator passed with evidence, required approval bindings are still exact and valid, and required probe health is healthy with zero blocking findings. / `finalize_workflow_execution()` 是封存工作流执行结果 Schema 的唯一参考路径。除非全部步骤均为 `DONE`、每个写动作都有已确认不可变账本结果及提供方引用、每项目标成功标准和整体目标证据类型均被覆盖、每个必选验证器都携带证据通过、必需审批绑定仍然精确有效、必需探针健康且无阻断发现，否则默认阻断。

`PlanExecutionSession.is_complete()` reports only mechanical completion and must never publish a terminal answer by itself. Persist the sealed final artifact with `save_terminal_result()` under the current checkpoint head, then emit `run_ended` through the event adapter. / `PlanExecutionSession.is_complete()` 只报告机械完成，绝不得单独发布终态答案。应在当前检查点头下通过 `save_terminal_result()` 持久化封存终态制品，再通过事件适配器发送 `run_ended`。

## Reference Kernel / 参考内核

[`plan_execution.py`](../../../runtime/plan_execution.py) provides / 提供：

- Goal, plan, patch, and checkpoint sealing plus semantic validation. / 目标、计划、补丁和检查点封存及语义校验。
- Deterministic ready-step calculation and guarded state transitions. / 确定性就绪步骤计算与受保护状态转换。
- Write-action claims that reuse success, block in-progress duplication, and route unknown results to verification. / 写动作领取：复用成功、阻止进行中重复、将未知结果路由到核验。
- Local plan-patch compilation with exact affected-subgraph enforcement. / 精确执行受影响子图边界的局部计划补丁编译。
- Portable checkpoint creation and safe restore semantics. / 可移植检查点创建与安全恢复语义。

The kernel intentionally does not call tools. The supplied coordinator composes it with governed Tool Dispatch without moving authorization or side-effect truth into the plan kernel. / 内核有意不直接调用工具。提供的协调器会把它与受治理工具分派组合，但不会把授权或副作用真值移入计划内核。

Additional executable components / 其他可执行组件：

- [`plan_execution_sqlite_store.py`](../../../runtime/plan_execution_sqlite_store.py): WAL transactions, optimistic head checks, contiguous internal events, checkpoint/idempotency snapshots, bounded outbox, terminal-result immutability, and health checks. / WAL 事务、乐观头校验、连续内部事件、检查点/幂等快照、有界 Outbox、终态结果不可变性和健康检查。
- [`plan_tool_dispatch.py`](../../../runtime/plan_tool_dispatch.py): exact goal/plan/step/effect/handler binding plus persist-before-dispatch two-phase coordination. / 精确目标、计划、步骤、副作用、处理器绑定及分派前持久化两阶段协调。
- [`plan_execution_events.py`](../../../runtime/plan_execution_events.py): validated dual-stream reasoning and tool observability. / 已校验的推理与工具双流可观测性。
- [`plan_execution_completion.py`](../../../runtime/plan_execution_completion.py): final completion gate and sealed workflow result. / 最终完成闸门与封存工作流结果。

## Acceptance / 验收

- The goal contract is sealed before planning and every plan binds its exact version. / 规划前已封存目标契约，每份计划绑定其确切版本。
- The plan is a valid DAG with unique IDs, exact handlers, observable completion criteria, and bounded recovery. / 计划是合法 DAG，具有唯一 ID、确切处理器、可观测完成判据和有界恢复。
- The scheduler never starts a dependency-incomplete or non-`TODO` step. / 调度器绝不启动依赖未完成或非 `TODO` 步骤。
- Every `DONE` step has completion evidence; every successful write has one confirmed idempotency record. / 每个 `DONE` 步骤都有完成证据；每个成功写动作都有一条已确认幂等记录。
- Crash recovery never silently replays an interrupted write. / 崩溃恢复绝不静默重放中断写动作。
- Replanning changes only the failed-and-affected subgraph and cannot overwrite completed facts. / 重规划只改变失败及受影响子图，不能覆盖已完成事实。
- High-risk dispatch and final completion recheck current authorization, approval, evidence, and probe health. / 高风险分派与最终完成重新检查当前授权、审批、证据和探针健康。
- A crash between Tool Dispatch and the second plan commit leaves an open reconciliation item and never silently retries the write. / 工具分派与第二次计划提交之间崩溃会留下开放对账项，绝不静默重试写动作。
- A terminal result is immutable, head-bound, and impossible to seal from mechanical `DONE` alone. / 终态结果不可变、绑定当前头，且不可能仅凭机械 `DONE` 封存。
- Events and metrics distinguish missing, unknown, observed zero, failed, and not applicable. / 事件与指标区分缺失、未知、观测零值、失败和不适用。

### Pattern Template / 模式模板

- 状态 / Status: Named candidate with machine-readable contracts and a reference kernel / 已命名候选，具备机器可读契约与参考内核。
- 模式清单 / Patterns: Plan-and-Execute / 计划并执行.
- 诊断用途 / Diagnostic Use: Use when actions need explicit planning, dependency-aware execution, durable state, and bounded recovery. / 当行动需要显式规划、依赖感知执行、持久状态和有界恢复时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 发布交付、企业流程、事故修复、数据变更、长任务、多系统协调 / Delivery, enterprise workflow, incident repair, data mutation, long-running tasks, multi-system coordination.
- 当前症状 / Current Symptoms: Ad hoc multi-step actions, hidden dependencies, stale plans, replayed writes, global restarts, ambiguous completion, or unrecoverable partial state. / 多步行动临时串联、依赖隐藏、计划过期、写动作重放、全量重启、完成含糊或部分状态不可恢复。
- 适配信号 / Fit Signals: Multiple handlers, explicit dependencies, changing external state, checkpoints, approval boundaries, side effects, or recovery needs. / 多处理器、显式依赖、变化外部状态、检查点、审批边界、副作用或恢复需求。
- 调整方向 / Adjustment Direction: Externalize the goal, compile and validate a plan DAG, separate immutable plan from mechanical state, protect `DONE`, and recover with a local patch. / 外部化目标，编译并校验计划 DAG，分离不可变计划与机械状态，保护 `DONE`，通过局部补丁恢复。
- 修改方式 / How To Modify: Adopt the five Schemas and reference runtime modules; integrate governed tool dispatch, transactional persistence, the dual-stream event adapter, completion gate, and probes; validate with failure, crash, unknown-result, stale-head, stale-patch, and duplicate-dispatch tests. / 采用五个 Schema 与参考运行时模块；接入受治理工具分派、事务持久化、双流事件适配器、完成闸门和探针；用失败、崩溃、未知结果、陈旧头、陈旧补丁和重复分派测试验证。
- 输入 / Inputs: Versioned goal contract, handler inventory, current state, risk and permission policy, completion evidence definitions. / 版本化目标契约、处理器清单、当前状态、风险与权限策略、完成证据定义。
- 输出 / Outputs: Sealed plan revisions, step records, action receipts, checkpoints, idempotency records, plan patches, execution events, and final completion evidence. / 封存计划修订、步骤记录、动作回执、检查点、幂等记录、计划补丁、执行事件和最终完成证据。
- 风险与治理 / Risks & Governance: Stale state, unsafe replay, plan drift, excessive patch blast radius, compensation misuse, approval expiry, and probe outage; mitigate with live admission, idempotency, local patches, immutable evidence, and fail-closed protected transitions. / 状态过期、不安全重放、计划漂移、补丁影响范围过大、补偿误用、审批过期和探针故障；通过实时准入、幂等、局部补丁、不可变证据和默认阻断的受保护转换缓解。

Observability Metrics File / 可观测性指标文件: [action-orchestration-observability.md](action-orchestration-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. Record the goal and plan bindings, patch blast radius, protected `DONE` facts, unknown-result reconciliation, checkpoint identity, idempotency evidence, and acceptance result. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议；记录目标与计划绑定、补丁影响范围、受保护 `DONE` 事实、未知结果核验、检查点身份、幂等证据和验收结果。
