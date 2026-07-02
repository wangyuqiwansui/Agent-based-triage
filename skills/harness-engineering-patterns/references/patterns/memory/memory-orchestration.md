# Progress Tracking / 进度追踪

Cell / 交织点: memory-orchestration / 记忆 x 编排  
Capability / 能力: Memory / 记忆  
Mode / 模式: Orchestration / 编排  
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850), adapted as an engineering workflow pattern / 来源于 arXiv:2605.13850，并调整为工程工作流模式

Use this file as the design pattern source for long-running task progress tracking. / 将本文档作为长程任务进度追踪的设计模式来源。

Observability Metrics File / 可观测性指标文件: [memory-orchestration-observability.md](memory-orchestration-observability.md)

## Design Pattern / 设计模式

Progress Tracking is a memory-orchestration pattern for tasks that cannot be safely completed from a plain checklist. It freezes the goal, splits work into milestones, maintains separate narrative, scheduling, and mechanical state, records append-only progress events, uses acceptance gates, asks probes to fill gaps, and emits recovery packages after each cycle. / 进度追踪是一种记忆 x 编排模式，适用于不能仅靠普通待办清单安全完成的任务。它先冻结目标，再拆分里程碑，分别维护叙事态、调度态和机械态，追加式记录进度事件，使用验收闸门，在缺口出现时请求探针补数，并在每轮循环后生成恢复包。

The core rule is: if any required confirmation is missing, do not continue by default. Enter blocked, pending review, rework, or observation, or issue a probe request. / 核心规则是：如果任一必要确认项无法确认，不得默认继续。必须进入阻塞、待复核、需返工或观察中状态，或发出探针请求。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Memory / 记忆 x Orchestration / 编排.
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; the source matrix maps Memory / 记忆 x Orchestration / 编排 to Progress Tracking / 进度追踪.
- 问题 / Problem: Long-running work loses reliable task memory when goals, milestones, evidence, mechanical truth, blockers, and handoff state are mixed into ordinary conversation. / 当目标、里程碑、证据、机械真值、阻塞项和交接状态混在普通对话中时，长程任务会丢失可靠任务记忆。
- 架构方案 / Architectural Solution: Use an orchestration controller to maintain goal contracts, milestone gates, narrative state, scheduling state, mechanical state, append-only events, probe requests, and recovery packages. / 使用编排控制器维护目标契约、里程碑闸门、叙事态、调度态、机械态、只追加事件、探针请求和恢复包。
- 工程权衡 / Engineering Trade-offs: Progress tracking improves resumability and auditability, but adds state-maintenance overhead and requires strict gate discipline. / 进度追踪提升可恢复性和可审计性，但会增加状态维护成本，并要求严格执行闸门纪律。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when long-running work needs a recoverable control structure for goals, milestones, evidence, mechanical truth, gates, probes, and handoff state. / 当长程任务需要用可恢复的控制结构管理目标、里程碑、证据、机械真值、闸门、探针和交接状态时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Progress Tracking / 进度追踪.
- 诊断用途 / Diagnostic Use: Coordinate task memory across milestones, tools, state planes, acceptance gates, probes, and recovery packages. / 跨里程碑、工具、状态平面、验收闸门、探针和恢复包协调任务记忆。
- 适用工作流节点 / Applicable Workflow Nodes: long-running execution, engineering delivery, data migration, approval flow, incident repair, research synthesis, release operation, and handoff-heavy work. / 长程执行、工程交付、数据迁移、审批流、事故修复、资料研究、运营发布和重交接工作。
- 当前症状 / Current Symptoms: The task keeps moving in text but cannot prove goal coverage, current milestone, evidence health, true parameters, or safe next action. / 任务在文本上持续推进，但无法证明目标覆盖、当前里程碑、证据健康、真实参数或安全下一步。
- 适配信号 / Fit Signals: multiple steps, recoverable state, critical values, evidence requirements, acceptance gates, probe interactions, or cross-session handoff. / 存在多步骤、可恢复状态、关键值、证据要求、验收闸门、探针交互或跨会话交接。
- 调整方向 / Adjustment Direction: Separate narrative, scheduling, and mechanical state; make the ledger append-only; gate milestones; and generate recovery packages every cycle. / 分离叙事态、调度态和机械态；账本只追加；里程碑过闸；每轮生成恢复包。
- 修改方式 / How To Modify: Replace free-form status updates with the execution workflow in this file and observe it with [memory-orchestration-observability.md](memory-orchestration-observability.md). / 用本文档中的执行流程替代自由状态更新，并用 [memory-orchestration-observability.md](memory-orchestration-observability.md) 观测。
- 输入 / Inputs: original goal, constraints, available materials, tools, object scope, risk boundaries, known evidence, and current blockers. / 原始目标、约束、已有材料、工具、对象范围、风险边界、已知证据和当前阻塞项。
- 输出 / Outputs: goal contract, milestone list, state planes, progress events, probe requests/results, acceptance records, recovery package, and archive package. / 目标契约、里程碑清单、状态平面、进度事件、探针请求/结果、验收记录、恢复包和归档包。
- 风险与治理 / Risks & Governance: Unknown gate answers must block default continuation; high-risk actions require review; mechanical truth must have source records. / 闸门答案未知时必须阻止默认继续；高风险动作需要复核；机械真值必须有来源记录。

## Positioning / 定位

Use Progress Tracking when execution depends on persistent task memory: what the goal is, where the task currently is, which evidence has been verified, which true parameters are bound, which risks are blocked, and how a new executor can resume without reading the full history. / 当执行依赖持久任务记忆时使用进度追踪：目标是什么、任务当前在哪里、哪些证据已验证、哪些关键真值已绑定、哪些风险已阻断，以及新的接手者如何不翻完整历史也能继续。

It is not a todo list or a casual log. It is an executable control structure for recoverable, auditable, multi-step work. / 它不是待办清单，也不是随手日志，而是一套可恢复、可审计、多步骤工作的执行控制结构。

### Use For / 适用场景

- Long-running workflows crossing multiple tools, files, roles, approvals, or sessions. / 跨多个工具、文件、角色、审批或会话的长程工作流。
- Tasks with explicit deliverables, milestones, acceptance criteria, or audit requirements. / 有明确交付物、里程碑、验收标准或审计要求的任务。
- Work that reads or writes important state: files, money, IDs, accounts, versions, dates, ranges, approvals, environments, or customer data. / 会读写关键状态的任务：文件、金额、编号、账号、版本、日期、范围、审批、环境或客户数据。
- Tasks that may be interrupted, delegated, resumed, reviewed, or repaired. / 可能中断、委派、续跑、复核或修复的任务。
- Tasks where "done" must mean "the success criteria are proven", not merely "some actions were performed". / 需要证明“成功标准已达成”，而不是只证明“已经做过一些动作”的任务。

### Do Not Use For / 不适用场景

- One-shot Q&A with no state to preserve. / 无需保留状态的一次性问答。
- Simple rewriting or formatting with no milestone or evidence requirement. / 无里程碑或证据要求的简单改写或格式调整。
- Open-ended chat without an executable goal. / 没有可执行目标的开放式闲聊。
- Work where no decision, state, or recovery record should be retained. / 不需要保留决策、状态或恢复记录的工作。

## Design Principles / 设计原则

1. Freeze the goal before expanding execution. / 先冻结目标，再展开执行。  
   The original request, success criteria, non-goals, constraints, and risk boundaries form the contract for all later execution, observation, recovery, and acceptance. / 原始请求、成功标准、非目标、约束和风险边界构成后续执行、观测、恢复和验收的共同契约。

2. Separate state planes. / 分离状态平面。  
   Narrative state explains why and where the work is; scheduling state determines what can run next; mechanical state stores true parameters and evidence-backed values. / 叙事态解释为什么做、做到哪里；调度态决定下一步能做什么；机械态保存真实参数和有证据支持的值。

3. Append the ledger; do not overwrite history. / 账本只追加，不覆盖历史。  
   Corrections are new events. Old events stay available for audit and diagnosis. / 纠偏通过新增事件完成，旧事件保留用于审计和诊断。

4. Gate every milestone. / 每个里程碑都必须过闸。  
   A milestone cannot complete because it feels complete; each acceptance condition must be checked. / 里程碑不能因为“看起来完成”而完成；必须逐条检查验收条件。

5. Use probes for missing truth. / 用探针补齐缺失真值。  
   The execution flow identifies gaps and requests data. It must not invent probe results. / 执行流程负责发现缺口并请求数据，不得伪造探针结果。

6. Recovery must not depend on the full conversation. / 恢复不能依赖完整对话。  
   Each cycle should leave a recovery package that contains the goal contract, current milestone, current working set, recent ledger, blockers, mechanical-state index, latest observation, next action, and forbidden actions. / 每轮循环都应留下恢复包，包含目标契约、当前里程碑、当前工作集、最近账本、阻塞项、机械态索引、最新观测、下一步动作和禁止动作。

## Roles / 角色

| Role / 角色 | Responsibility / 职责 |
| --- | --- |
| Task initiator / 任务发起者 | Provide the original goal, boundaries, priority, and final acceptance. / 提供原始目标、边界、优先级和最终验收意见。 |
| Orchestrator / 流程编排者 | Maintain the goal contract, milestones, schedule, blockers, and recovery package. / 维护目标契约、里程碑、调度、阻塞项和恢复包。 |
| Executor / 执行者 | Execute the current action and return results, evidence, outputs, and exceptions. / 执行当前动作，并返回结果、证据、产物和异常。 |
| Tool or system / 工具或系统 | Provide deterministic operations, queries, file changes, state writes, and external evidence. / 提供确定性操作、查询、文件变更、状态写入和外部证据。 |
| Reviewer / 审核者 | Review high-risk actions, abnormal results, milestone gates, and final delivery. / 复核高风险动作、异常结果、里程碑闸门和最终交付。 |
| Observability probe / 可观测性探针 | Independently observe progress, fill data gaps, detect drift, score evidence, and report conflicts. / 独立观察进度、补全数据缺口、发现漂移、评估证据并报告冲突。 |

## Core State Objects / 核心状态对象

### Goal Contract / 目标契约

Freeze the task anchor before execution. / 执行前冻结任务锚点。

```text
Goal contract / 目标契约:
  Task name / 任务名称:
  Original goal / 原始目标:
  Success criteria / 成功标准:
    -
  Non-goals / 非目标:
    -
  Constraints / 约束条件:
    -
  High-risk actions / 高风险动作:
    -
  Acceptance method / 验收方式:
  Change rule / 变更规则: append a goal-change event only / 只能追加目标变更事件
  Current version / 当前版本:
```

### Milestone List / 里程碑清单

Break the far goal into near, testable targets. / 将远目标拆成可验收的近目标。

```text
Milestone / 里程碑:
  Name / 名称:
  Status / 当前状态: not started | running | observing | blocked | pending review | rework | complete
                    未开始 | 执行中 | 观察中 | 阻塞 | 待复核 | 需返工 | 已完成
  Entry conditions / 进入条件:
    -
  Acceptance conditions / 验收条件:
    -
  Main outputs / 主要产物:
    -
  Dependent state / 依赖状态:
    -
  Risk points / 风险点:
    -
  Open questions / 开放问题:
    -
```

### Scheduling State / 调度态

Use this to decide what can run next. / 用于决定下一步能做什么。

```text
Scheduling state / 调度态:
  Pending items / 待执行事项:
    -
  Ready items / 已就绪事项:
    -
  Blocked items / 阻塞事项:
    -
  Completed items / 已完成事项:
    -
  Rework items / 返工事项:
    -
  Current milestone / 当前里程碑:
  Next action / 下一步动作:
```

### Narrative State / 叙事态

Use this to preserve meaning and continuity. / 用于保存任务意义和连续性。

```text
Narrative state / 叙事态:
  Goal anchor / 目标锚: reference the goal contract / 引用目标契约
  Progress ledger / 进度账: append-only progress events / 只追加进度事件
  Current working set / 当前工作集: minimum context needed for this cycle / 本轮最小必要上下文
  Latest judgment / 最新判断:
  Reason for next action / 下一步理由:
```

### Mechanical State / 机械态

Use this for critical truth. Do not copy critical values from casual summaries. / 用于保存关键真值。不得从自然语言摘要中复制关键值。

```text
Mechanical state / 机械态:
  State key / 状态键:
  Scope / 适用范围:
  Value reference / 值引用:
  Source tool or system / 来源工具或系统:
  Producing step / 产生步骤:
  Trust level / 信任级别:
  Last read location / 最近读取位置:
  Last write location / 最近写入位置:
```

Examples: employee IDs, invoice IDs, account numbers, payment amounts, data ranges, file paths, branch names, version numbers, approval IDs, environment names, tenant IDs, and external evidence references. / 示例：员工编号、发票编号、账号、付款金额、数据范围、文件路径、分支名、版本号、审批单号、环境名、租户 ID 和外部证据引用。

### Progress Event / 进度事件

Use this as the smallest ledger unit. / 作为账本最小单位。

```text
Progress event / 进度事件:
  Event ID / 事件编号:
  Timestamp / 时间:
  Current milestone / 当前里程碑:
  What happened / 发生事项:
  Action executed / 执行动作:
  Decision / 决策:
  Reason / 原因:
  Evidence references / 证据引用:
    -
  State read / 读取状态:
    -
  State written / 写入状态:
    -
  Impact scope / 影响范围:
  Next action / 下一步动作:
  Needs probe data / 是否需要探针补数: yes | no / 是 | 否
  Needs human review / 是否需要人工复核: yes | no / 是 | 否
```

### Recovery Package / 恢复包

Use this for interruption, handoff, and audit. / 用于中断续跑、交接和审计。

```text
Recovery package / 恢复包:
  Goal contract / 目标契约:
  Current milestone / 当前里程碑:
  Current working set / 当前工作集:
  Recent progress events / 最近进度事件:
    -
  Open blockers / 开放阻塞项:
    -
  Mechanical-state index / 机械态索引:
    -
  Latest probe conclusion / 最近探针结论:
  Next action / 下一步动作:
  Forbidden actions / 禁止动作:
    -
```

## State Machine / 状态机

| State / 状态 | Meaning / 含义 | Allowed Actions / 允许动作 |
| --- | --- | --- |
| Not started / 未开始 | Goal and milestones are not frozen. / 目标与里程碑尚未冻结。 | Freeze goal, split milestones. / 固化目标、拆分里程碑。 |
| Running / 执行中 | Current milestone is being executed. / 当前里程碑正在推进。 | Execute actions, write ledger, run gates, request probes. / 执行动作、写账本、运行闸门、请求探针。 |
| Observing / 观察中 | A probe is filling data or diagnosing abnormal state. / 探针正在补数或诊断异常状态。 | Pause risky progress, receive results, backfill state. / 暂停高风险推进、接收结果、回填状态。 |
| Blocked / 阻塞 | A required input, permission, approval, data source, or mechanical truth is missing. / 缺少必要输入、权限、审批、数据源或机械真值。 | Request data, ask human, wait for external result. / 请求补数、请求人工、等待外部结果。 |
| Pending review / 待复核 | A high-risk action or milestone output needs review. / 高风险动作或里程碑产物需要复核。 | Review, approve, reject, return to rework. / 复核、通过、驳回、进入返工。 |
| Rework / 需返工 | Acceptance failed or a probe found a critical anomaly. / 验收失败或探针发现关键异常。 | Return to the relevant milestone and append correction event. / 回到对应里程碑并追加纠偏事件。 |
| Complete / 已完成 | All milestones passed and final delivery is confirmed. / 所有里程碑通过且最终交付已确认。 | Archive, review, reuse. / 归档、复盘、复用。 |
| Archived / 已归档 | Task is closed and state is read-only. / 任务关闭且状态只读。 | Query, audit, retrospective. / 查询、审计、复盘。 |

## Execution Workflow / 执行流程

```text
Receive task / 接收任务
  ->
Freeze goal contract / 固化目标契约
  ->
Split milestones / 拆分里程碑
  ->
Initialize narrative, scheduling, and mechanical state / 初始化叙事态、调度态和机械态
  ->
Generate current working set / 生成当前工作集
  ->
Select next action / 选择下一步动作
  ->
Run pre-execution confirmation gate / 运行执行前确认闸门
  ->
Bind mechanical truth / 绑定机械真值
  ->
Execute action / 执行动作
  ->
Write state, outputs, and evidence / 写入状态、产物和证据
  ->
Append progress event / 追加进度事件
  ->
Run milestone acceptance gate / 运行里程碑验收闸门
  ->
Issue probe request when needed / 必要时发出探针请求
  ->
Backfill probe results / 回填探针结果
  ->
Advance, block, review, rework, or complete / 推进、阻塞、复核、返工或完成
  ->
Generate recovery package / 生成恢复包
  ->
Archive final package / 归档最终包
```

### 1. Receive Task / 接收任务

Collect the initiator's original intent, expected deliverables, time range, object scope, known constraints, risk boundaries, available materials, and callable tools. / 收集任务发起者的原始意图、期望产物、时间范围、对象范围、已知约束、风险边界、已有材料和可调用工具。

Output / 输出: original task statement / 原始任务说明。

### 2. Freeze Goal Contract / 固化目标契约

Rewrite the original request into an executable contract. Include success criteria and non-goals. Non-goals prevent local details from pulling the executor outside the task. / 将原始请求改写为可执行契约。必须包含成功标准和非目标。非目标用于防止执行者被局部细节吸出任务范围。

Output / 输出: goal contract / 目标契约。

### 3. Split Milestones / 拆分里程碑

Create milestones with entry conditions, acceptance conditions, main outputs, dependencies, risks, and open questions. / 创建带进入条件、验收条件、主要产物、依赖、风险和开放问题的里程碑。

Output / 输出: milestone list / 里程碑清单。

### 4. Initialize State Planes / 初始化状态平面

Initialize scheduling state, narrative state, and mechanical state. / 初始化调度态、叙事态和机械态。

Output / 输出: initial task state / 初始任务状态。

### 5. Generate Current Working Set / 生成当前工作集

Crop the minimum context needed for the current cycle from the goal contract, current milestone, recent ledger, blockers, mechanical-state index, and evidence. The working set must include the goal anchor; do not use only recent summaries. / 从目标契约、当前里程碑、最近账本、阻塞项、机械态索引和证据中裁剪本轮最小必要上下文。当前工作集必须带目标锚，不能只带最近摘要。

Output / 输出: current working set / 当前工作集。

### 6. Select Next Action / 选择下一步动作

Choose the next action from ready items. The action must serve the goal, advance the current milestone, satisfy prerequisites, and respect high-risk boundaries. / 从已就绪事项中选择下一步动作。该动作必须服务目标、推进当前里程碑、满足前置条件并尊重高风险边界。

Output / 输出: selected next action / 已选下一步动作。

### 7. Run Pre-Execution Confirmation Gate / 运行执行前确认闸门

Before executing any meaningful action, check all gate questions: / 执行任何关键动作前，检查所有闸门问题：

```text
1. Does this serve the goal contract? / 是否服务目标契约？
2. Does this advance the current milestone? / 是否推进当前里程碑？
3. Are prerequisites satisfied? / 前置条件是否满足？
4. Does this touch a high-risk boundary? / 是否触碰高风险边界？
5. Are critical truths bound from mechanical state? / 关键真值是否已从机械态绑定？
6. Is the evidence source reliable enough? / 证据来源是否足够可靠？
7. Can acceptance be judged after this action? / 执行后是否可以判断验收？
```

Hard gate / 硬闸门:

```text
If any item cannot be confirmed, do not continue by default.
Enter blocked, pending review, rework, or observing, or issue a probe request.

如果任一项无法确认，不得默认继续。
必须进入阻塞、待复核、需返工或观察中状态，或发出探针请求。
```

### 8. Bind Mechanical Truth / 绑定机械真值

If the action needs IDs, amounts, accounts, file paths, versions, approval numbers, object ranges, data windows, tenants, or environments, read them from mechanical state. / 如果动作需要编号、金额、账号、文件路径、版本、审批单号、对象范围、数据窗口、租户或环境，必须从机械态读取。

Output / 输出: bound execution parameters / 已绑定执行参数。

### 9. Execute Action / 执行动作

Execute the current action only. It may be query, analysis, write, modification, generation, submission, notification, review, or wait. Do not silently expand the goal. / 只执行当前动作。动作可以是查询、分析、写入、修改、生成、提交、通知、复核或等待。不得静默扩展目标。

Output / 输出: result, evidence, artifact, exception / 结果、证据、产物、异常。

### 10. Write State / 写入状态

Write newly confirmed truths into mechanical state, outputs and judgments into narrative state, and completion state into scheduling state. / 将新确认的真值写入机械态，将产物和判断写入叙事态，将完成度写入调度态。

Output / 输出: state changes / 状态变更。

### 11. Append Progress Event / 追加进度事件

Append a progress event that explains what happened, why, based on what evidence, which state was read or written, what changed, and what comes next. / 追加进度事件，说明发生了什么、为什么这样做、依据什么证据、读写了哪些状态、改变了什么、下一步是什么。

Output / 输出: new ledger entry / 新增账本条目。

### 12. Run Acceptance Gate / 运行验收闸门

When a milestone claims completion, check every acceptance condition. Pass only when all conditions are satisfied. If not, enter rework and append an acceptance-failure event. / 当里程碑声称完成时，逐条检查验收条件。只有全部满足才通过；否则进入需返工，并追加验收失败事件。

Output / 输出: acceptance conclusion / 验收结论。

### 13. Issue Probe Request / 发出探针请求

Issue a probe request when goal relevance, progress, evidence, mechanical state, consistency, acceptance, context load, or recovery integrity cannot be judged. / 当目标相关性、进度、证据、机械态、一致性、验收、上下文负载或恢复完整性无法判断时，发出探针请求。

Output / 输出: probe request / 探针请求单。

### 14. Backfill Probe Result / 回填探针结果

Write probe results into the intended locations: working set, mechanical-state index, progress ledger, blocker list, acceptance record, recovery package, or next action. / 将探针结果写入目标位置：当前工作集、机械态索引、进度账本、阻塞清单、验收记录、恢复包或下一步动作。

Output / 输出: backfilled task state / 回填后的任务状态。

### 15. Generate Recovery Package / 生成恢复包

At the end of each cycle, generate or update the recovery package so another executor can continue without reading the full history. / 每轮循环结束时生成或更新恢复包，使接手者无需读取完整历史即可继续。

Output / 输出: recovery package / 恢复包。

### 16. Complete and Archive / 完成与归档

After all milestones pass and final delivery is confirmed, archive the goal contract, milestone list, progress ledger, mechanical-state index, probe records, acceptance records, recovery package, and retrospective. / 所有里程碑通过且最终交付确认后，归档目标契约、里程碑清单、进度账本、机械态索引、探针记录、验收记录、恢复包和复盘结论。

Output / 输出: archive package / 归档包。

## Probe Interaction Protocol / 探针交互协议

### Probe Request / 探针请求单

```text
Probe request / 探针请求单:
  Request ID / 请求编号:
  Trigger step / 触发步骤:
  Current milestone / 当前里程碑:
  Reason / 请求原因:
    goal unclear | progress stalled | evidence insufficient | state conflict |
    mechanical state missing | acceptance unknown | risk increased | recovery incomplete
    目标不清 | 进度停滞 | 证据不足 | 状态冲突 |
    机械态缺失 | 验收未知 | 风险升高 | 恢复不完整
  Data needed / 需要补全的数据:
    -
  Existing evidence / 已有证据:
    -
  Expected backfill target / 期望回填位置:
    goal contract | current working set | mechanical state | ledger |
    blockers | acceptance record | recovery package | next action
    目标契约 | 当前工作集 | 机械态 | 进度账本 |
    阻塞清单 | 验收记录 | 恢复包 | 下一步动作
  Expected handling level / 期望处理级别:
    continue | observe | correct | pause
    继续 | 观察 | 回正 | 暂停
```

### Probe Result / 探针结果单

```text
Probe result / 探针结果单:
  Request ID / 请求编号:
  Probe name / 探针名称:
  Observation conclusion / 观测结论:
  Health level / 健康等级:
    normal | observe | correct | pause
    正常 | 观察 | 回正 | 暂停
  Completed data / 补全数据:
    -
  Abnormal signals / 异常信号:
    -
  Evidence references / 证据引用:
    -
  Suggested backfill target / 建议回填位置:
  Suggested next action / 建议下一步动作:
  Needs human review / 是否需要人工复核: yes | no / 是 | 否
```

The probe must not directly replace the execution flow. The execution flow must not fabricate probe data. / 探针不能直接替代执行流程推进任务；执行流程也不能伪造探针数据。

## Independent and Interactive Modes / 独立与交互模式

### Independent Mode / 独立执行模式

When no observability probe is available, the orchestrator must manually check goal relevance, milestone progress, evidence completeness, state consistency, mechanical truth, and high-risk actions before each milestone completes. Unknown data must become blocked or pending review, never silently accepted. / 没有可观测性探针时，编排者必须在每个里程碑完成前人工检查目标相关性、里程碑推进度、证据完整性、状态一致性、机械真值和高风险动作。无法判断的数据必须进入阻塞或待复核，不得静默通过。

Required objects / 必需对象:

- Goal contract / 目标契约
- Milestone list / 里程碑清单
- Append-only progress ledger / 只追加进度账本
- Mechanical-state index / 机械态索引
- Acceptance records / 验收记录
- Recovery package / 恢复包

### Interactive Probe Mode / 交互探针模式

In interactive mode, the execution flow advances the task and probes supply missing observations. / 交互模式下，执行流程推进任务，探针负责补充缺失观测。

```text
Execution flow finds a gap / 执行流程发现缺口
  ->
Generate probe request / 生成探针请求单
  ->
Probe collects and diagnoses / 探针采集与诊断
  ->
Return probe result / 返回探针结果单
  ->
Execution flow backfills state / 执行流程回填状态
  ->
Continue, correct, rework, block, or pause / 继续、回正、返工、阻塞或暂停
```

## Scenario Adaptation Template / 场景适配模板

```text
Scenario name / 场景名称:
Task type / 任务类型:
  query | analysis | modification | approval | migration | release | generation | review | mixed
  查询 | 分析 | 修改 | 审批 | 迁移 | 发布 | 生成 | 复核 | 综合
Main objects / 主要对象:
Critical truths / 关键真值:
  -
Main risks / 主要风险:
  -
Mandatory milestones / 必须验收的里程碑:
  -
Forbidden actions / 禁止动作:
  -
Callable tools / 可调用工具:
  -
Human review nodes / 人工复核节点:
  -
Probe priority / 探针优先级:
  -
Final deliverable / 最终交付物:
  -
```

## Scenario Map / 场景映射

| Scenario / 场景 | Critical Truth / 关键真值 | Common Risk / 常见风险 | Core Acceptance / 核心验收 |
| --- | --- | --- | --- |
| HR payroll / 人事薪资 | Employee scope, batch, amount, rule version, approval state / 员工范围、批次、金额、规则版本、审批状态 | Wrong object, abnormal amount, unauthorized submission / 对象串错、金额异常、越权提交 | Headcount consistent, amount explainable, anomalies listed, payment blocked before review / 人数一致、金额可解释、异常已列出、付款前已阻断。 |
| Expense approval / 报销审批 | Claims, budget, invoices, approval chain, payment state / 单据、预算、发票、审批链、支付状态 | Duplicate claim, unauthorized approval, missing evidence / 重复报销、越权审批、证据缺失 | Documents complete, budget available, approval chain correct, payment reviewed first / 单据完整、预算可用、审批链正确、支付前已复核。 |
| Contract review / 合同审阅 | Contract version, party, clause, amount, term / 合同版本、主体、条款、金额、期限 | Wrong version, omitted clause, unmarked risk / 版本误用、条款遗漏、风险未标注 | Version consistent, risk list complete, suggestions traceable / 版本一致、风险清单完整、修改建议可追溯。 |
| Code refactor / 代码重构 | Files, branch, test scope, dependency, release target / 文件、分支、测试范围、依赖、发布目标 | Local fix drifts from refactor goal, insufficient tests / 局部修错偏离重构目标、测试不足 | Core behavior unchanged, tests pass, change scope explainable / 核心行为不变、测试通过、变更范围可解释。 |
| Data migration / 数据迁移 | Source, target table, mapping rules, validation sample / 数据源、目标表、映射规则、校验样本 | Field mismatch, duplicate write, data loss / 字段错配、重复写入、丢数据 | Row counts align, samples pass, rollback path clear / 行数对齐、抽样通过、回滚路径明确。 |
| Research / 资料研究 | Question, sources, evidence, conclusion, citations / 问题、来源、证据、结论、引用 | Evidence weak, conclusion overreaches, source conflict / 证据不足、结论过度、来源冲突 | Evidence checkable, boundaries stated, conflicts explained / 证据可查、结论有边界、冲突已说明。 |
| Operations release / 运营发布 | Material, channel, schedule, approval, rollback plan / 物料、渠道、时间、审批、回滚方案 | Wrong channel, wrong time, missing approval / 错渠道、错时间、未审批 | Material consistent, release window correct, rollback available / 物料一致、发布窗口正确、回滚方案可用。 |

## Exception Handling / 异常处理

| Exception / 异常 | Handling / 处理方式 |
| --- | --- |
| Goal change / 目标变更 | Pause current progress, append a goal-change event, update goal contract version. / 暂停当前推进，追加目标变更事件，更新目标契约版本。 |
| Evidence insufficient / 证据不足 | Issue an evidence-health probe; do not report completion before evidence is filled. / 发出证据健康探针；证据补齐前不得汇报完成。 |
| State conflict / 状态冲突 | Issue a state-consistency probe; prefer the trusted source and append correction event. / 发出状态一致性探针；以可信来源为准并追加纠偏事件。 |
| Mechanical state missing / 机械态缺失 | Issue mechanical-parameter provenance probe; do not execute critical action before source confirmation. / 发出机械参数溯源探针；来源确认前不得执行关键动作。 |
| Milestone stalled / 里程碑停滞 | Issue milestone-progress probe; narrow the current sub-goal if needed. / 发出里程碑推进探针；必要时缩小当前子目标。 |
| High-risk action / 高风险动作 | Set state to pending review; do not continue before approval. / 状态置为待复核；人工通过前不得继续。 |
| Acceptance failure / 验收失败 | Set state to rework; return to the relevant milestone. / 状态置为需返工；回到对应里程碑。 |
| Repeated failure / 重复失败 | Pause, diagnose, and append an error-pressure event. / 暂停推进，进入诊断，并追加错误压力事件。 |
| Context overload / 上下文过载 | Rebuild the current working set with only goal anchor and necessary materials. / 重建当前工作集，只保留目标锚和必要材料。 |
| Recovery incomplete / 恢复包不完整 | Issue recovery-integrity probe and resume only after completion. / 发出恢复完整性探针，补齐后再继续。 |

## Completion Conditions / 完成条件

Mark the task complete only when all conditions are true: / 只有同时满足以下条件，才能标记任务完成：

- Every success criterion in the goal contract is covered. / 目标契约中的成功标准全部覆盖。
- Every milestone has passed its acceptance gate. / 所有里程碑均通过验收闸门。
- High-risk actions are blocked or reviewed and approved. / 高风险动作已被阻断或通过复核。
- Critical mechanical state has source and read records. / 关键机械态都有来源和读取记录。
- Critical conclusions have evidence references. / 关键结论都有证据引用。
- Open blockers are empty or explicitly moved out of scope. / 开放阻塞项为空，或已明确移出任务范围。
- The recovery package and archive package are generated. / 恢复包与归档包已生成。
- The final deliverable is confirmed by the initiator or designated reviewer. / 最终交付物已被任务发起者或指定审核者确认。

## Failure Modes / 失败模式

- Maintaining only a todo list, with no goal contract. / 只维护待办清单，没有目标契约。
- Recording only what was done, not why, with what evidence, or which state changed. / 只记录做过什么，不记录为什么做、依据是什么、状态变了什么。
- Mixing IDs, amounts, accounts, paths, or object scopes into casual summaries. / 把编号、金额、账号、路径或对象范围混入自然语言摘要。
- Omitting non-goals, causing scope drift. / 缺少非目标，导致范围漂移。
- Skipping acceptance gates, making the task look complete without meeting the goal. / 跳过验收闸门，导致看似完成但未达成目标。
- Receiving probe results but failing to backfill them. / 接收探针结果但没有回填。
- Resuming by guessing from full history instead of using a recovery package. / 中断后从完整历史中猜状态，而不是从恢复包继续。
- Continuing when a required confirmation is unknown. / 在必要确认项未知时继续推进。

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
