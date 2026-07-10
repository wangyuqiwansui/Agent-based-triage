# Layered Retention / 分层保留

Cell / 交织点: memory-hierarchy / 记忆 x 层级
Capability / 能力: Memory / 记忆
Mode / 模式: Hierarchy / 层级
Source / 来源: Local extension grounded in Harness workflow practice; arXiv:2605.13850 v2 leaves this matrix cell unnamed. / 本地扩展模式，基于 Harness 工作流实践；arXiv:2605.13850 v2 未命名该交织点。
Alias / 别名: Layered Retention Execution Flow / 分层保留执行流程
Standalone Executable / 可独立执行: Yes / 是
Primary Axis / 主轴: Memory / 记忆
Secondary Axes / 辅轴: Governance / 治理; Reflection / 反思; Action / 行动
Primary Topology / 主拓扑: Hierarchy / 层级
Secondary Topologies / 辅拓扑: Routing / 路由; Loop / 循环; Orchestration / 编排

Use this file as the design pattern source for the Memory / 记忆 x Hierarchy / 层级 intersection. / 将本文档作为 Memory / 记忆 x Hierarchy / 层级交织点的设计模式来源。

## Quick Navigation / 快速导航

- [Article Grounding / 论文依据](#article-grounding--论文依据)
- [Default Memory Layer Model / 默认记忆层模型](#default-memory-layer-model--默认记忆层模型)
- [Input And Output Contracts / 输入与输出契约](#input-contract--输入契约)
- [Core Objects / 核心对象](#core-objects--核心对象)
- [Execution Procedure Overview / 执行流程总览](#execution-procedure-overview--执行流程总览)
- [Operating Modes / 两种运行模式](#operating-modes--两种运行模式)
- [Probe Interaction / 探针交互](#probe-interaction--探针交互)
- [Failure Modes / 失败模式与处理](#failure-modes--失败模式与处理)
- [Pattern Template / 模式模板](#pattern-template--模式模板)

## Design Pattern / 设计模式

Layered Retention / 分层保留 is a long-running agent memory governance flow. It decides how information should be read, used, written, promoted, demoted, discarded, reviewed, and audited across different memory layers. It is not a single business workflow; it is a reusable engineering pattern that can be mounted onto assistants, coding agents, course coaches, enterprise knowledge assistants, support agents, approval agents, operations agents, and research agents. / 分层保留是一套长程智能体记忆治理流程，用于判断信息应该如何读取、使用、写入、升层、降权、丢弃、复核和审计。它不是某一个业务流程，而是可挂载到个人助理、编程助手、课程教练、企业知识助手、客服助手、审批助手、运维助手和研究助手等场景的工程模式。

The pattern can run alone or interact with a workflow observability probe. In standalone mode, the flow performs minimum verification and write-routing decisions by itself. In interactive mode, the probe fills evidence, boundaries, exceptions, quality signals, and context-hit data before writeback or promotion. / 本模式可以独立执行，也可以与工作流可观测性探针交互运行。独立执行时，流程自身完成最小校验和写入路由；交互运行时，探针补全证据、边界、异常、质量信号和上下文命中数据，再参与写入或升层决策。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Memory / 记忆 x Hierarchy / 层级.
- 论文依据 / Article Basis: 本地扩展模式 / Local-extension pattern; the source matrix leaves this cell unnamed, and a concrete Harness workflow supplies draft evidence for a hierarchy-based memory pattern. / 本地扩展模式；来源矩阵未命名该单元，一个具体 Harness 工作流为基于层级的记忆模式提供了草案证据。
- 问题 / Problem: Long-running agents can confuse temporary signals with durable knowledge, let low-level context override higher-level rules, overfill working context with history, or write unverified guesses into long-term memory. / 长程智能体容易把临时信号当作长期知识，让低层上下文覆盖高层规则，将历史全量塞入工作上下文，或把未验证猜测写入长期记忆。
- 架构方案 / Architectural Solution: Establish explicit memory layers, classify every retention candidate, enforce coverage and conflict rules, assemble only necessary context, route writes by evidence strength, and manage lifecycle through promotion, demotion, archive, deletion, and human review. / 建立显式记忆层，对每条待保留信息做分层判定，执行覆盖与冲突规则，只装配必要上下文，按证据强度路由写入，并通过升层、降权、归档、删除和人审管理生命周期。
- 工程权衡 / Engineering Trade-offs: Layering protects durable knowledge and auditability, but it adds routing, evidence, lifecycle, and probe overhead; use the full flow for long-running, high-risk, or reusable work, and use the minimum checklist for lightweight work. / 分层能保护长期知识和审计能力，但会增加路由、证据、生命周期和探针成本；长程、高风险或可复用工作使用完整流程，轻量任务使用最小清单。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when information must be retained by scope, lifecycle, authority, evidence, and context budget across multiple memory levels. / 当信息必须按照作用域、生命周期、权威来源、证据和上下文预算跨多层记忆保留时使用。

### Document Goal / 文档目标

Define a general execution process for deciding how an agent should retain information during long-running work. / 定义一套通用执行流程，用于让智能体在长程任务中判断信息应当如何保留。

The process governs seven actions / 本流程治理七类动作:

| Action / 动作 | Purpose / 目的 |
|---|---|
| Read / 读取 | Load only the necessary layer summaries or source references. / 只加载必要层级摘要或来源引用。 |
| Use / 使用 | Apply retained information without violating layer authority. / 在不违反层级权威的前提下使用保留信息。 |
| Write / 写入 | Persist verified task state or evidence to the right layer. / 将已验证的任务状态或证据写入正确层级。 |
| Promote / 升层 | Move short-term information into a durable layer only with sufficient evidence. / 只有证据充分时才把短期信息升入长期层。 |
| Demote / 降权 | Lower confidence or visibility when information ages or conflicts with newer evidence. / 当信息过期或与新证据冲突时降低置信度或可见性。 |
| Discard / 丢弃 | Remove temporary, noisy, sensitive, or low-value material when retention is unjustified. / 在无保留价值时清理临时、噪声、敏感或低价值材料。 |
| Audit / 审计 | Preserve decisions, evidence, and blocked actions for replay and governance. / 保留决策、证据和阻断动作，支持复盘与治理。 |

### Position In Harness / 在 Harness 框架中的位置

| Foundation / 基座 | Alignment / 归属 |
|---|---|
| Cognitive foundation / 认知基座 | Memory, Governance, Reflection, Action / 记忆、治理、反思、行动 |
| Topology foundation / 拓扑基座 | Hierarchy, Routing, Loop, Orchestration / 层级、路由、循环、编排 |
| Engineering pattern foundation / 工程模式基座 | Layered Retention / 分层保留 |
| Skill layer / 技能层 | Can be packaged as Layered Memory Governance / 可包装为“分层记忆治理” |

Primary and secondary coordinates / 主坐标与副坐标:

| Type / 类型 | Coordinate / 坐标 | Use / 用途 |
|---|---|---|
| Primary / 主坐标 | COG_MEMORY__TOP_HIERARCHY | Build memory layers by scope, lifecycle, and trust. / 按作用域、生命周期和可信度建立记忆层级。 |
| Secondary / 副坐标 | COG_MEMORY__TOP_ROUTING | Route writes, promotions, and discards. / 决定写入、升层和丢弃路径。 |
| Secondary / 副坐标 | COG_MEMORY__TOP_LOOP | Support expiry, review, demotion, and version updates. / 支持过期、复核、降权和版本更新。 |
| Secondary / 副坐标 | COG_GOVERNANCE__TOP_HIERARCHY | Prevent low-level information from overriding higher-level constraints. / 防止低层信息覆盖高层边界。 |
| Secondary / 副坐标 | COG_REFLECTION__TOP_LOOP | Turn failures, excluded paths, and retrospectives into reusable lessons. / 将失败、排除方案和复盘结果沉淀为经验。 |
| Secondary / 副坐标 | COG_ACTION__TOP_ORCHESTRATION | Coordinate storage, tools, audit, human review, and context assembly. / 编排存储、工具、审计、人审和上下文装配。 |

### Execution Principles / 执行原则

Every retention candidate must answer five questions before it is written or promoted. / 所有待保留信息在写入或升层前都必须回答五个问题。

| Question / 问题 | Explanation / 说明 |
|---|---|
| Scope / 作用域是什么 | Organization, team, project, tenant, user, task, session, or current turn. / 属于组织、团队、项目、租户、用户、任务、会话还是当前轮次。 |
| Lifecycle / 生命周期多长 | Current turn, session, task cycle, project cycle, or long-term validity. / 是当前一轮、一次会话、一个任务周期、一个项目周期还是长期有效。 |
| Authority / 权威来源是谁 | Human confirmation, system rule, tool result, external evidence, history, or model inference. / 来自人类确认、系统规则、工具结果、外部证据、历史记录还是模型推断。 |
| Evidence / 证据是否充分 | Test result, approval, log, file, ticket, conversation trace, or other proof. / 是否有测试结果、审批记录、日志、文件、工单、对话轨迹等证据。 |
| Context budget / 上下文预算如何 | Resident context, summarized context, deferred read, or reference-only retention. / 是常驻上下文、摘要进入、按需读取还是仅保留引用。 |

Coverage rules / 覆盖原则:

| Layer / 层级 | May Influence / 可影响 | Must Not Override / 不可覆盖 |
|---|---|---|
| Policy / 策略层 | All lower-level flows. / 所有低层流程。 | User preferences, session state, draft judgments. / 用户偏好、会话状态、草稿判断。 |
| Project / 项目层 | Default rules, domain conventions, tool usage. / 默认规则、领域规范、工具调用方式。 | Single tool result or temporary debug config. / 单次工具结果或临时调试配置。 |
| User / 用户层 | Tone, durable preferences, personalization. / 表达方式、长期偏好、个性化策略。 | Policy layer and hard project rules. / 策略层和项目硬规则。 |
| Task / 任务层 | Current priority, goal, progress, excluded paths. / 当前优先级、当前目标、当前进度、已排除方案。 | Durable user profile and project rules. / 用户长期画像和项目规范。 |
| Draft / 草稿层 | Current-turn reasoning and candidate options. / 当前轮判断和候选方案。 | Any durable layer without validation. / 未经验证不得覆盖任何长期层。 |

Core constraint / 核心约束: lower layers may temporarily shape how higher-level information is used, but they cannot automatically rewrite higher-level facts. / 低层信息可以临时影响高层信息的使用方式，但不能自动改写高层事实。

Promotion rules / 升层原则:

| Promotion Condition / 升层条件 | Example / 示例 |
|---|---|
| Explicit human confirmation / 人类明确确认 | The user says future answers should be concise Chinese. / 用户确认“以后都用中文简洁回答”。 |
| Repeated stable occurrence / 多次稳定出现 | The same preference appears across multiple sessions. / 同一偏好在多次会话中重复出现。 |
| Tool or system validation / 工具或系统验证 | Tests pass, permission check succeeds, ticket status is confirmed. / 测试通过、权限校验通过、工单状态确认。 |
| Traceable evidence / 有可追溯证据 | Conversation id, log id, file path, approval id. / 对话编号、日志编号、文件路径、审批编号。 |
| Completed retrospective / 完成复盘 | A failure cause is attributed and becomes reusable experience. / 失败原因经过归因并形成可复用经验。 |

### Default Memory Layer Model / 默认记忆层模型

| Layer / 层级 | Content / 内容 | Default Storage / 默认存储 | Default Read / 默认读取 | Default Write / 默认写入 |
|---|---|---|---|---|
| Policy / 策略层 | Organization rules, safety boundaries, compliance red lines, approval requirements. / 组织规则、安全边界、合规红线、审批要求。 | Config center, read-only files, admin console. / 配置中心、只读文件、管理后台。 | Load key summary at startup. / 启动时加载关键摘要。 | Agent cannot write directly; it can only propose changes. / 智能体不可直接写入，只能提出变更建议。 |
| Project / 项目层 | Project conventions, domain model, business process, test commands, directory rules. / 项目规范、领域模型、业务流程、测试命令、目录约定。 | Repository files, knowledge base, project config. / 仓库文件、知识库、项目配置。 | Load core conventions; read long content on demand. / 加载核心约定，长内容按需读取。 | Usually requires review, file evidence, or system evidence. / 通常需要评审、文件证据或系统证据。 |
| User / 用户层 | User preferences, tenant config, durable profile, long-term mastery. / 用户偏好、租户配置、长期画像、长期掌握度。 | User profile store, tenant config store, structured database. / 用户画像库、租户配置库、结构化数据库。 | Load summary at task entry; read fields as needed. / 进入任务时加载摘要，必要时按字段读取。 | Requires confirmation, repeated evidence, or strong validation. / 需要确认、多次证据或强验证。 |
| Task / 任务层 | Current goal, progress, milestones, excluded paths, current state. / 当前目标、进度、里程碑、已排除方案、当前状态。 | Checkpoint store or task state store. / 检查点存储或任务状态库。 | Restore recent state; avoid full-history loading. / 恢复最近状态，不加载完整历史。 | Agent may write with timestamp and source. / 智能体可写入，但必须带时间和来源。 |
| Draft / 草稿层 | Current input, temporary tool result, intermediate judgment, candidate plan. / 当前轮输入、工具临时结果、中间判断、候选计划。 | Runtime state or short-term cache. / 运行时状态或短期缓存。 | Current turn only, then cleanup. / 当前轮进入上下文，用后清理。 | Free to write, but not durable by default. / 可自由写入，但默认不可长期保留。 |

Scenario layer templates / 场景可裁剪层级:

| Scenario / 场景 | Recommended Layers / 推荐层级 |
|---|---|
| Personal assistant / 个人助理 | User, Task, Draft / 用户层、任务层、草稿层 |
| Coding assistant / 编程助手 | Project, User, Task, Draft / 项目层、用户层、任务层、草稿层 |
| Enterprise knowledge assistant / 企业知识助手 | Policy, Project, Tenant, Task, Draft / 策略层、项目层、租户层、任务层、草稿层 |
| Course coach / 课程教练 | Course, User, Session, Draft / 课程层、用户层、会话层、草稿层 |
| Support assistant / 客服助手 | Policy, Tenant, User, Ticket, Draft / 策略层、租户层、用户层、工单层、草稿层 |
| Approval assistant / 审批助手 | Policy, Project, Task, Audit, Draft / 策略层、项目层、任务层、审计层、草稿层 |
| Research assistant / 研究助手 | Project, Topic, Task, Evidence, Draft / 项目层、主题层、任务层、证据层、草稿层 |

### Execution Contract / 执行契约

- Trigger / 触发条件: Run when a task may retain information beyond the current turn, when context must be selected from history, when writeback is possible, or when temporary evidence may affect durable memory. / 当任务可能跨当前轮保留信息、需要从历史中装配上下文、可能写回状态，或临时证据可能影响长期记忆时执行。
- Objective / 目标: Produce a user-facing result and a governed retention decision package. / 产出用户可见结果和受治理的保留决策包。
- Scope / 范围: normalize request, load boundaries, recover context, collect current materials, classify layers, check conflict, assemble context, execute task action, generate state changes, route writes, manage lifecycle, and emit observability events. / 覆盖请求归一、加载边界、恢复上下文、采集材料、信息分层、冲突检查、上下文装配、执行动作、生成状态变化、写入路由、生命周期处理和可观测事件输出。
- Stop Condition / 停止条件: Stop or route to human review when policy boundaries are missing for high-risk action, cross-tenant contamination appears, write evidence is insufficient for durable memory, or a lower layer attempts to override a higher layer. / 当高风险动作缺少策略边界、出现跨租户污染、长期写入证据不足，或低层试图覆盖高层时停止或转人审。
- Output / 输出: final response, used-memory list, write decisions, context assembly record, risk and governance record, observability event package, and next-step recommendations. / 输出最终响应、使用的记忆、写入决策、上下文装配记录、风险治理记录、可观测事件包和下一步建议。

### Input Contract / 输入契约

Minimum input / 最小输入:

```yaml
Execution Request / 执行请求:
  request_id / 请求编号: required / 必填
  scenario_type / 场景类型: required / 必填
  current_goal / 当前目标: required / 必填
  user_input / 用户输入: required / 必填
  current_time / 当前时间: required / 必填
  permission_context / 权限上下文: optional / 可选
  project_context / 项目上下文: optional / 可选
  user_context / 用户上下文: optional / 可选
  task_state / 任务状态: optional / 可选
  current_turn_tool_results / 当前轮工具结果: optional / 可选
  known_constraints / 已知约束: optional / 可选
  available_context_budget / 可用上下文预算: optional / 可选
```

Complete input / 完整输入:

```yaml
Execution Request / 执行请求:
  request_id / 请求编号: example_0001
  scenario_type / 场景类型: coding_assistant / 编程助手
  current_goal / 当前目标: fix a failing unit test / 修复一个单元测试失败问题
  user_input / 用户输入: description, code snippet, error text / 描述、代码片段、报错信息
  current_time / 当前时间: concrete timestamp / 具体时间
  identity_and_permission / 身份与权限:
    user_id / 用户编号: optional / 可选
    tenant_id / 租户编号: optional / 可选
    role / 角色: optional / 可选
    allowed_actions / 可执行动作: []
  policy_constraints / 策略约束:
    rule_refs / 规则引用: []
    forbidden_actions / 禁止动作: []
    approval_required_actions / 必须审批动作: []
  project_context / 项目上下文:
    project_id / 项目编号: optional / 可选
    file_refs / 文件引用: []
    test_commands / 测试命令: []
    domain_rules / 领域规则: []
  user_context / 用户上下文:
    preference_summary / 偏好摘要: optional / 可选
    durable_profile_ref / 长期画像引用: optional / 可选
    confirmed_history_items / 历史确认项: []
  task_state / 任务状态:
    current_stage / 当前阶段: optional / 可选
    completed_items / 已完成事项: []
    excluded_paths / 已排除方案: []
    next_step_candidates / 下一步候选: []
  current_turn_material / 当前轮材料:
    tool_results / 工具结果: []
    temporary_judgments / 临时判断: []
    candidate_plans / 候选方案: []
  observability_input / 可观测输入:
    probe_result_refs / 探针结果引用: []
    anomaly_alerts / 异常告警: []
    data_completion_suggestions / 数据补全建议: []
```

### Output Contract / 输出契约

```yaml
Execution Result / 执行结果:
  request_id / 请求编号: required / 必填
  final_response / 最终响应: required / 必填
  used_memory / 使用的记忆:
    policy_layer / 策略层: []
    project_layer / 项目层: []
    user_layer / 用户层: []
    task_layer / 任务层: []
    draft_layer / 草稿层: []
  write_decisions / 写入决策:
    written / 已写入: []
    promotion_candidates / 候选升层: []
    rejected / 已拒绝: []
    human_review_required / 待人审: []
    expiry_pending / 待过期: []
  context_assembly_record / 上下文装配记录:
    resident_content / 常驻内容: []
    on_demand_content / 按需读取内容: []
    excluded_content / 被排除内容: []
    budget_usage / 预算使用情况: {}
  risk_and_governance / 风险与治理:
    triggered_rules / 触发规则: []
    blocked_actions / 阻断动作: []
    degraded_actions / 降级动作: []
  observability_events / 可观测事件:
    event_refs / 事件引用: []
    probe_completion_requests / 探针补全请求: []
  next_steps / 下一步:
    recommended_actions / 推荐动作: []
    evidence_needed / 需补充证据: []
```

### Core Objects / 核心对象

Retention Candidate / 保留候选:

```yaml
Retention Candidate / 保留候选:
  candidate_id / 候选编号: ""
  content_summary / 内容摘要: ""
  source / 来源: user | system | tool | file | log | ticket | model_inference | historical_memory
  scope / 作用域: policy | project | tenant | user | task | session | turn
  lifecycle / 生命周期: turn | session | task | project | durable
  authority / 权威来源: human_confirmed | system_rule | tool_verified | external_evidence | historical | inferred
  evidence_refs / 证据引用: []
  confidence / 置信度: low | medium | high
  default_layer / 默认层级: policy | project | user | task | draft
  write_intent / 写入意图: none | draft | task | user | project | policy_change_proposal
  context_mode / 上下文模式: resident | summary | deferred_read | reference_only
  expiry_rule / 过期规则: ""
```

Layer Decision / 分层决策:

```yaml
Layer Decision / 分层决策:
  candidate_id / 候选编号: ""
  assigned_layer / 判定层级: ""
  reason / 判定原因: ""
  coverage_risk / 覆盖风险: ""
  conflict_status / 冲突状态: none | conflict | blocked | needs_review
  promotion_allowed / 是否允许升层: false
  promotion_requirements / 升层要求: []
```

Write Decision / 写入决策:

```yaml
Write Decision / 写入决策:
  candidate_id / 候选编号: ""
  route / 路由: discard | draft | task | user | project | policy_change_proposal | human_review
  write_payload / 写入内容: {}
  evidence_refs / 证据引用: []
  expiry_or_review_at / 过期或复核时间: ""
  rejection_reason / 拒绝原因: ""
  audit_ref / 审计引用: ""
```

### Execution Procedure Overview / 执行流程总览

```text
Start / 开始
  -> Node 1: receive request and normalize scenario / 节点一：接收请求与场景归一
  -> Node 2: load policy boundaries / 节点二：加载策略边界
  -> Node 3: recover project, user, and task context / 节点三：恢复项目、用户、任务上下文
  -> Node 4: collect current-turn material / 节点四：采集当前轮材料
  -> Node 5: classify information into layers / 节点五：信息分层判定
  -> Node 6: check conflict and coverage / 节点六：冲突与覆盖检查
  -> Node 7: assemble context / 节点七：上下文装配
  -> Node 8: execute task actions / 节点八：执行任务动作
  -> Node 9: generate result and state changes / 节点九：生成结果与状态变化
  -> Node 10: route writes / 节点十：写入路由
  -> Node 11: promote, demote, discard, or review / 节点十一：升层、降权、丢弃、人审
  -> Node 12: output result package and events / 节点十二：输出结果包与可观测事件
End / 结束
```

### Node 1: Request Intake And Scenario Normalization / 节点一：接收请求与场景归一

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Convert diverse scenario requests into executable input. / 将不同场景请求统一成可执行输入。 |
| Input / 输入 | User input, task goal, scenario type, permission data. / 用户输入、任务目标、场景类型、权限信息。 |
| Actions / 动作 | Identify scenario, confirm goal, create request id, initialize execution record. / 识别场景、确认目标、建立请求编号、初始化执行记录。 |
| Output / 输出 | Normalized execution request. / 归一后的执行请求。 |
| Failure handling / 失败处理 | If the goal is unclear, create a task-layer clarification state and do not write durable memory. / 如果目标不清，建立任务层待澄清状态，不写长期层。 |

Execution rules / 执行规则:

1. Do not treat a temporary user expression as a durable preference. / 不把用户临时表达直接当作长期偏好。
2. Do not treat the current task goal as a project rule. / 不把当前任务目标直接当作项目规范。
3. Do not treat a tool result as fact before validation. / 不把工具结果直接当作事实，除非后续节点验证。
4. Generate a unique request id for this run. / 必须为本次执行生成唯一请求编号。

### Node 2: Load Policy Boundaries / 节点二：加载策略边界

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Load non-overridable rules before any lower-layer context is used. / 先加载不可被覆盖的规则。 |
| Input / 输入 | Policy references, permission context, scenario type. / 策略层引用、权限上下文、场景类型。 |
| Actions / 动作 | Read organization rules, safety boundaries, approval requirements, forbidden actions. / 读取组织规则、安全边界、审批要求、禁止动作。 |
| Output / 输出 | Policy boundary package. / 策略边界包。 |
| Failure handling / 失败处理 | If policy cannot be read, enter conservative mode and allow only low-risk actions. / 策略不可读取时进入保守模式，只允许低风险动作。 |

Policy boundary package example / 策略边界包示例:

```yaml
Policy Boundary Package / 策略边界包:
  forbidden_actions / 禁止动作:
    - unauthorized production data write / 未授权写入生产数据
    - sensitive information sent to unauthorized services / 将敏感信息发送到未授权服务
  approval_required_actions / 必须审批动作:
    - permission change / 权限变更
    - billing change / 账单变更
    - bulk deletion / 批量删除
  allowed_actions / 允许动作:
    - read public project documents / 读取公开项目文档
    - generate a plan / 生成计划
    - generate a draft for confirmation / 生成待确认草案
```

### Node 3: Recover Project, User, And Task Context / 节点三：恢复项目、用户、任务上下文

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Load only context necessary for the current task. / 只取当前任务必要的上下文。 |
| Input / 输入 | Project id, user id, task id, historical state references. / 项目编号、用户编号、任务编号、历史状态引用。 |
| Actions / 动作 | Load core project rules, user summary, and recent task state. / 加载核心项目规则、用户摘要、最近任务状态。 |
| Output / 输出 | Context candidate package. / 上下文候选包。 |
| Failure handling / 失败处理 | Start from minimum context and record missing-state gaps. / 恢复失败时从最小上下文启动，并记录状态缺口。 |

Read order / 读取顺序:

1. Policy summary / 策略层摘要。
2. Project core conventions / 项目层核心约定。
3. User summary / 用户层摘要。
4. Recent task state / 任务层最近状态。
5. Current draft material / 当前轮草稿材料。

Do not load all historical conversations into context. Keep long history as on-demand references. / 不要把全部历史对话塞入上下文；长历史只能作为按需读取引用。

### Node 4: Collect Current-Turn Material / 节点四：采集当前轮材料

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Collect current input, tool results, and temporary judgments. / 收集当前轮输入、工具结果和临时判断。 |
| Input / 输入 | User input, file fragments, tool returns, model judgments. / 用户输入、文件片段、工具返回、当前模型判断。 |
| Actions / 动作 | Mark source, time, trust level, and verification status. / 标记来源、时间、可信度、是否已验证。 |
| Output / 输出 | Current-turn material package. / 当前轮材料包。 |
| Failure handling / 失败处理 | If a source cannot be verified, mark it as low-trust draft. / 无法验证来源时标记为低可信草稿。 |

Current-turn material package example / 当前轮材料包示例:

```yaml
Current Turn Material Package / 当前轮材料包:
  user_input / 用户输入:
    content_ref / 内容引用: current_message / 当前消息
    source / 来源: user / 用户
    initial_trust / 初始可信度: medium / 中
  tool_results / 工具结果:
    - tool_name / 工具名称: test_runner / 测试执行器
      result_summary / 结果摘要: one test failed / 一个测试失败
      verified / 是否验证: true / 是
  temporary_judgments / 临时判断:
    - content / 内容: config path may be wrong / 可能是配置路径错误
      source / 来源: agent_inference / 智能体推断
      verified / 是否验证: false / 否
      default_layer / 默认层级: draft / 草稿层
```

### Node 5: Information Layer Classification / 节点五：信息分层判定

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Decide the temporary layer for every information item. / 决定每条信息暂存在哪一层。 |
| Input / 输入 | Current-turn material package, context candidate package, policy boundary package. / 当前轮材料包、上下文候选包、策略边界包。 |
| Actions / 动作 | Classify by scope, lifecycle, source, evidence, and budget. / 根据作用域、生命周期、来源、证据、预算分层。 |
| Output / 输出 | Layer decision record. / 分层判定记录。 |
| Failure handling / 失败处理 | If classification is unclear, default to draft layer and block durable write. / 无法判定时默认进入草稿层，不进入长期层。 |

Classification table / 判定表:

| Information Type / 信息类型 | Default Layer / 默认层级 | Promotable / 是否可升层 | Promotion Condition / 升层条件 |
|---|---|---|---|
| Organization red line / 组织红线 | Policy / 策略层 | No / 否 | Only management workflow can change it. / 只能由管理流程变更。 |
| Project test command / 项目测试命令 | Project / 项目层 | Yes / 是 | Repository file or maintainer confirmation. / 仓库文件或项目维护者确认。 |
| User expression preference / 用户表达偏好 | Task or user candidate / 任务层或用户层候选 | Yes / 是 | Explicit confirmation or repeated stable occurrence. / 用户明确确认或多次稳定出现。 |
| Current task goal / 当前任务目标 | Task / 任务层 | No durable promotion / 不升长期层 | Archive or summarize after task completion. / 任务结束后归档或摘要。 |
| Temporary tool result / 工具临时结果 | Draft or task / 草稿层或任务层 | Yes / 是 | Reproducible tool result or validation. / 工具结果可复现或通过验证。 |
| Model guess / 模型猜测 | Draft / 草稿层 | Yes / 是 | Validation, retrospective, or human confirmation. / 经过验证、复盘或人类确认。 |
| Excluded path / 被排除方案 | Task or failure record / 任务层或失败记录 | Yes / 是 | Test evidence or retrospective conclusion. / 有测试证据或复盘结论。 |

### Node 6: Conflict And Coverage Check / 节点六：冲突与覆盖检查

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Prevent lower-layer information from polluting higher-layer facts. / 防止低层信息污染高层事实。 |
| Input / 输入 | Layer decision record, policy boundary package, existing memory. / 分层判定记录、策略边界包、已存在记忆。 |
| Actions / 动作 | Check overwrite, conflict, cross-tenant contamination, expiry, and permission gaps. / 检查覆盖、冲突、跨租户、过期、权限不足。 |
| Output / 输出 | Conflict handling record. / 冲突处理记录。 |
| Failure handling / 失败处理 | If conflict cannot be resolved, block write and keep only draft state. / 冲突无法解决时阻断写入，仅保留草稿。 |

Conflict rules / 冲突处理规则:

| Conflict Type / 冲突类型 | Handling / 处理方式 |
|---|---|
| User preference conflicts with policy / 用户偏好冲突策略层 | Policy wins; keep preference only for current request if allowed. / 策略层胜出，用户偏好只作为当前请求偏好。 |
| Tool result conflicts with project layer / 当前工具结果冲突项目层 | Put into draft first; wait for reproduction or project evidence. / 先进入草稿层，等待复现或项目证据。 |
| Current state conflicts with durable user profile / 当前状态冲突用户长期画像 | Current state affects only this task. / 当前状态只影响本次任务。 |
| Cross-tenant data appears / 租户数据交叉 | Block immediately and record governance event. / 立即阻断并记录治理事件。 |
| Expired memory is recalled / 过期记忆被召回 | Demote or remove, then create review event. / 降权或剔除，生成复核事件。 |

### Node 7: Context Assembly / 节点七：上下文装配

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Load the information actually needed for the current reasoning step. / 将本次推理真正需要的信息装入上下文。 |
| Input / 输入 | Layer decisions, context candidate package, budget constraints. / 分层判定记录、上下文候选包、预算约束。 |
| Actions / 动作 | Assemble by layer authority, relevance, confidence, and budget. / 按层级、相关性、可信度和预算装配。 |
| Output / 输出 | Context assembly record. / 上下文装配记录。 |
| Failure handling / 失败处理 | If budget is insufficient, keep policy, hard project rules, task goal, and current material first. / 预算不足时优先保留策略、项目硬规则、任务目标和当前轮材料。 |

Assembly priority / 装配优先级:

1. Mandatory policy boundaries / 必须遵守的策略边界。
2. Project rules required for the task / 当前任务不可缺少的项目规则。
3. Necessary user or tenant summary / 当前用户或租户必要摘要。
4. Recent task state / 最近任务状态。
5. Current input and tool results / 当前轮输入和工具结果。
6. Deferred-read references for large memories / 大体量记忆的按需读取引用。
7. Exclude low-confidence, expired, repeated, or irrelevant information by default. / 低置信、过期、重复、与任务无关的信息默认排除。

### Node 8: Execute Task Actions / 节点八：执行任务动作

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Complete the current task inside the assembled context. / 在装配后的上下文中完成当前任务。 |
| Input / 输入 | Context assembly record, tool list, user goal. / 上下文装配记录、工具清单、用户目标。 |
| Actions / 动作 | Reason, call tools, generate plans, or perform allowed actions. / 推理、调用工具、生成计划、执行允许动作。 |
| Output / 输出 | Task execution record. / 任务执行记录。 |
| Failure handling / 失败处理 | If tools fail, record failure cause without rewriting durable memory. / 工具失败时记录失败原因，不直接改写长期记忆。 |

Action risk levels / 执行动作分级:

| Level / 等级 | Description / 说明 | Confirmation / 是否需要确认 |
|---|---|---|
| Low risk / 低风险 | Explanation, draft, suggestion, read-only query. / 生成解释、草案、建议、只读查询。 | Usually no. / 通常不需要。 |
| Medium risk / 中风险 | Modify non-critical config, write task state, generate commit suggestion. / 修改非关键配置、写入任务状态、生成提交建议。 | Scenario dependent. / 视场景而定。 |
| High risk / 高风险 | Permission, billing, production data, bulk deletion, external sensitive sharing. / 权限、账单、生产数据、批量删除、外发敏感信息。 | Approval required. / 必须确认或审批。 |

### Node 9: Generate Result And State Changes / 节点九：生成结果与状态变化

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Produce a user-visible result and internal state-change candidates. / 形成对用户可见结果和内部状态变化。 |
| Input / 输入 | Task execution record, context assembly record. / 任务执行记录、上下文装配记录。 |
| Actions / 动作 | Output answer, completed items, and next actions. / 输出回答、列出已完成事项、生成后续动作。 |
| Output / 输出 | Result draft and state-change candidates. / 执行结果草案、状态变化候选。 |
| Failure handling / 失败处理 | If uncertain, mark uncertainty and avoid durable write. / 结果不确定时标明不确定性，状态不写长期层。 |

State-change candidate example / 状态变化候选示例:

```yaml
State Change Candidates / 状态变化候选:
  task_layer / 任务层:
    - field / 字段: completed_items / 已完成事项
      new_value / 新值: located failing test cause in config path / 已定位失败测试来自配置路径
      evidence / 证据: test log ref / 测试日志引用
  user_layer_candidate / 用户层候选:
    - field / 字段: preference.answer_style / 偏好.回答风格
      new_value / 新值: prefers conclusion first / 喜欢先给结论
      evidence / 证据: one expression in current session / 当前会话一次表达
      handling / 处理: insufficient evidence; do not promote / 证据不足，暂不升层
  project_layer_candidate / 项目层候选:
    - field / 字段: test_command / 测试命令
      new_value / 新值: use module-specific command / 使用指定命令运行模块测试
      evidence / 证据: repository doc ref / 仓库文档引用
      handling / 处理: pending project evidence review / 待项目证据复核
```

### Node 10: Write Routing / 节点十：写入路由

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Decide what to write, where to write it, and whether review is needed. / 决定哪些信息写入、写到哪里、是否待审。 |
| Input / 输入 | State-change candidates, conflict handling record, evidence record. / 状态变化候选、冲突处理记录、证据记录。 |
| Actions / 动作 | Route to draft, task, user, project, policy-change proposal, review, or discard. / 路由到草稿层、任务层、用户层、项目层、策略层变更建议、人审或丢弃。 |
| Output / 输出 | Write decision record. / 写入决策记录。 |
| Failure handling / 失败处理 | Reject durable writes when evidence is insufficient; keep candidate if useful. / 证据不足时拒绝长期写入，可保留候选。 |

Write routing rules / 写入路由规则:

| Candidate / 候选内容 | Default Route / 默认路由 |
|---|---|
| Unverified inference / 未验证推断 | Draft layer; discard or review at task end. / 草稿层，任务结束后丢弃或复核。 |
| Verified tool result / 已验证工具结果 | Task layer, can enter progress record. / 任务层，可进入进度记录。 |
| Current task progress / 当前任务进展 | Task layer with time, source, and evidence. / 任务层，带时间、来源、证据。 |
| Repeatedly confirmed user preference / 多次确认的用户偏好 | User layer with evidence and scope. / 用户层，带证据和有效范围。 |
| Repository or maintainer-confirmed project rule / 仓库或维护者确认的项目规则 | Project layer with file or review reference. / 项目层，带文件或评审引用。 |
| Safety boundary change / 安全边界变更 | Policy-change proposal; human review required. / 策略层变更建议，必须人审。 |
| Failure retrospective conclusion / 失败复盘结论 | Failure record or reusable lesson with evidence. / 失败记录或经验记录，带复盘证据。 |

### Node 11: Promotion, Demotion, Discard, Human Review / 节点十一：升层、降权、丢弃、人审

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Manage memory lifecycle. / 处理记忆生命周期。 |
| Input / 输入 | Write decision record, existing memory, expiry policy. / 写入决策记录、已有记忆、有效期策略。 |
| Actions / 动作 | Promote, demote, archive, delete, or request review. / 升层、降权、归档、删除、待审。 |
| Output / 输出 | Memory change record. / 记忆变更记录。 |
| Failure handling / 失败处理 | If lifecycle is unclear, set a review time. / 生命周期不明确时设置复核时间。 |

Lifecycle handling / 生命周期处理:

| Action / 动作 | Trigger / 触发条件 |
|---|---|
| Promote / 升层 | Evidence is sufficient, repeated, explicitly confirmed, or validated. / 证据充分、重复出现、明确确认、验证通过。 |
| Demote / 降权 | Long unused, conflicts with new evidence, or confidence drops. / 长时间未使用、与新证据冲突、置信度下降。 |
| Archive / 归档 | Project ends, task completes, or version expires but traceability is needed. / 项目结束、任务完成、版本过期但仍需追溯。 |
| Delete / 删除 | Temporary draft, expired sensitive material, or no retention value. / 临时草稿、敏感材料到期、无保留价值。 |
| Human review / 待审 | Policy, permission, billing, production, or sensitive information is involved. / 涉及策略、权限、账单、生产、敏感信息。 |

### Node 12: Output Result Package And Events / 节点十二：输出结果包与可观测事件

| Item / 项目 | Content / 内容 |
|---|---|
| Goal / 目标 | Return the result to the user and expose observable workflow data. / 向用户输出结果，同时向探针系统暴露可观测数据。 |
| Input / 输入 | Execution result, memory change record, context assembly record. / 执行结果、记忆变更记录、上下文装配记录。 |
| Actions / 动作 | Generate result package, event package, and probe completion requests. / 生成结果包、事件包、探针补全请求。 |
| Output / 输出 | Final execution result. / 最终执行结果。 |
| Failure handling / 失败处理 | If event write fails, keep a local minimum log. / 事件写入失败时保留本地最小日志。 |

Observable event package example / 可观测事件包示例:

```yaml
Observable Event Package / 可观测事件包:
  request_id / 请求编号: example_0001
  events / 事件列表:
    - event_id / 事件编号: event_001
      node / 节点: information_layer_classification / 信息分层判定
      type / 类型: layer_decision / 层级判定
      summary / 内容摘要: user preference kept as task-layer candidate / 用户偏好被暂存为任务层候选
      evidence_ref / 证据引用: current_session / 当前会话
    - event_id / 事件编号: event_002
      node / 节点: write_routing / 写入路由
      type / 类型: durable_write_rejected / 拒绝长期写入
      reason / 原因: insufficient evidence / 证据不足
      suggested_probe / 建议探针: promotion_evidence_sufficiency_probe / 升层证据充分性探针
```

### Operating Modes / 两种运行模式

Standalone mode / 独立执行模式:

| Check / 检查项 | Minimum Requirement / 最小要求 |
|---|---|
| Layer decision / 层级判定 | Every retention candidate has a layer. / 每条待保留信息必须有层级。 |
| Source marking / 来源标记 | Every memory item has a source. / 每条记忆必须有来源。 |
| Evidence marking / 证据标记 | Durable writes require evidence. / 长期层写入必须有证据。 |
| Expiry policy / 过期策略 | Draft and task layers need cleanup or review conditions. / 草稿层和任务层必须有清理或复核条件。 |
| Coverage constraint / 覆盖约束 | Lower layers cannot rewrite higher-level facts. / 低层不能改写高层事实。 |
| Output record / 输出记录 | Write decisions and rejection reasons must be emitted. / 必须输出写入决策和被拒绝原因。 |

Interactive mode / 交互运行模式:

```text
Execution flow emits events / 执行流程产出事件
  -> Probe checks events, context, write decisions, and exceptions / 探针检查事件、上下文、写入决策、异常
  -> Probe emits completion package / 探针生成补全包
  -> Execution flow absorbs completion package / 执行流程吸收补全包
  -> Classification, assembly, routing, or risk handling is corrected / 修正分层、上下文装配、写入路由或风险处理
```

### Probe Interaction / 探针交互

Events sent to probe / 发送给探针的事件:

```yaml
Flow Event / 流程事件:
  request_id / 请求编号: required / 必填
  node_id / 节点编号: required / 必填
  node_name / 节点名称: required / 必填
  event_type / 事件类型: required / 必填
  input_summary / 输入摘要: optional / 可选
  output_summary / 输出摘要: optional / 可选
  used_memory_refs / 使用记忆引用: []
  write_candidates / 写入候选: []
  evidence_refs / 证据引用: []
  risk_marks / 风险标记: []
  budget_data / 预算数据: {}
  time / 时间: required / 必填
```

Probe completion package / 接收探针的补全包:

```yaml
Probe Completion Package / 探针补全包:
  request_id / 请求编号: required / 必填
  target_node / 目标节点: required / 必填
  completion_type / 补全类型: required / 必填
  advice_level / 建议等级: hint | suggestion | block | human_review
  completion_fields / 补全字段:
    layer_correction / 层级修正: optional / 可选
    evidence_completion / 证据补充: optional / 可选
    risk_completion / 风险补充: optional / 可选
    context_completion / 上下文补充: optional / 可选
    write_correction / 写入修正: optional / 可选
  reason / 原因: required / 必填
  evidence_refs / 证据引用: []
  recommended_actions / 建议动作: []
```

Completion handling rules / 补全包处理规则:

| Advice Level / 建议等级 | Flow Handling / 执行流程处理 |
|---|---|
| Hint / 提示 | Record only; do not change flow. / 记录即可，不改变流程。 |
| Suggestion / 建议 | Auto-adopt or keep as candidate. / 可自动采纳，也可记录为候选。 |
| Block / 阻断 | Stop the corresponding write or action. / 必须停止对应写入或动作。 |
| Human review / 人审 | Enter pending confirmation; do not auto-run high-risk action. / 进入待确认状态，不能自动执行高风险动作。 |

### Scenario Adaptation / 场景适配指南

| Scenario / 场景 | Layer Config / 层级配置 | Write Strategy / 写入策略 | Main Risk / 重点风险 | Recommended Probe / 推荐探针 |
|---|---|---|---|---|
| Personal assistant / 个人助理 | User, Task, Draft / 用户层、任务层、草稿层 | Explicit preferences can promote quickly but must be reversible. / 用户明确偏好可较快升层，但仍需可撤销。 | Temporary emotion written as durable preference. / 临时情绪被误写为长期偏好。 | Preference stability probe / 用户偏好稳定性探针。 |
| Coding assistant / 编程助手 | Project, User, Task, Draft / 项目层、用户层、任务层、草稿层 | Project rules require repository, test, or review evidence. / 项目规则必须有仓库文件、测试结果或评审证据。 | Temporary debug config pollutes project rules. / 临时调试配置污染项目规则。 | Project rule evidence probe, tool result validation probe. / 项目规则证据探针、工具结果验证探针。 |
| Enterprise knowledge assistant / 企业知识助手 | Policy, Project, Tenant, Task, Draft / 策略层、项目层、租户层、任务层、草稿层 | Strict tenant isolation; policy changes only through management flow. / 租户信息严格隔离，策略层只允许管理流程变更。 | Cross-tenant pollution, stale policy, permission overreach. / 跨租户污染、旧政策复用、权限越界。 | Tenant isolation probe, policy coverage probe. / 租户隔离探针、策略覆盖探针。 |
| Course coach / 课程教练 | Course, User, Session, Draft / 课程层、用户层、会话层、草稿层 | Durable student profile needs exercise, quiz, or repeated performance evidence. / 学生长期画像需要练习、测验或多次表现证据。 | One struggle written as durable lack of ability. / 一次卡顿被误写为长期能力不足。 | Mastery evidence probe. / 掌握度证据探针。 |
| Support assistant / 客服助手 | Policy, Tenant, User, Ticket, Draft / 策略层、租户层、用户层、工单层、草稿层 | Prices, discounts, permissions, compensation need system or approval evidence. / 价格、折扣、权限、赔付必须引用业务系统或审批。 | Single-user discount pollutes global rule. / 单个用户优惠污染全局规则。 | Tenant boundary probe, ticket-state probe. / 租户边界探针、工单状态探针。 |
| Approval or high-risk assistant / 审批与高风险操作助手 | Policy, Project, Task, Audit, Draft / 策略层、项目层、任务层、审计层、草稿层 | Critical states write immediately; ordinary states can batch-write. / 关键状态实时写回，一般状态批量写回。 | Unapproved execution, missing audit, lost state. / 未审批执行、审计缺失、状态丢失。 | Approval gate probe, audit completeness probe. / 审批门禁探针、审计完整性探针。 |

### Failure Modes / 失败模式与处理

| Failure Mode / 失败模式 | Symptom / 表现 | Handling / 处理 |
|---|---|---|
| Full history loaded into context / 全量历史塞入上下文 | Old information distracts the answer. / 回答被旧信息干扰。 | Use resident summaries and on-demand references. / 改为摘要常驻、引用按需读取。 |
| Draft flows directly into durable memory / 草稿直通长期层 | Temporary guess becomes durable fact. / 临时猜测变成长期事实。 | Block durable write and require evidence. / 阻断长期写入，要求证据。 |
| Promotion without evidence / 无证据升层 | User profile or project rule is wrongly changed. / 用户画像或项目规则被误改。 | Roll back or demote to candidate. / 回滚或降为候选。 |
| Policy overridden by lower layer / 策略被低层覆盖 | User asks to bypass safety boundary. / 用户要求突破安全边界。 | Policy wins and governance event is recorded. / 策略层胜出，记录治理事件。 |
| Cross-tenant contamination / 跨租户污染 | One tenant's data affects another tenant. / 一个租户信息影响另一个租户。 | Block, alert, audit, and clean polluted memory. / 阻断、告警、审计、清理污染记忆。 |
| Stale memory stays forever / 旧记忆永久有效 | Expired rule is still used. / 已过期规则仍被引用。 | Demote, review, archive, or delete. / 降权、复核、归档或删除。 |
| Free-text durable accumulation / 自由文本长期堆积 | Retrieval is unstable and updates are hard. / 检索不稳定、更新困难。 | Structure, version, and evidence durable memory. / 长期层结构化、版本化、证据化。 |
| Crash loses state / 中途崩溃丢状态 | Long-running task cannot resume. / 长程任务无法恢复。 | Write critical task state checkpoints. / 关键状态实时检查点。 |

### Minimum Configuration Checklist / 最小可执行清单

```yaml
Minimum Configuration / 最小配置:
  layer_list / 层级清单: required / 必填
  write_permission_per_layer / 每层写入权限: required / 必填
  read_strategy_per_layer / 每层读取策略: required / 必填
  cleanup_rule_per_layer / 每层清理规则: required / 必填
  promotion_conditions / 升层条件: required / 必填
  coverage_rules / 覆盖规则: required / 必填
  evidence_fields / 证据字段: required / 必填
  output_record_format / 输出记录格式: required / 必填
  high_risk_blocking_rules / 高风险阻断规则: optional_but_recommended / 可选但推荐
  probe_interaction_interface / 探针交互接口: optional_but_recommended / 可选但推荐
```

### Engineering Node Registration / 推荐工程节点注册项

```yaml
Business Nodes / 业务节点:
  - node_id / 节点编号: NODE_MEMORY_REQUEST_NORMALIZE
    node_name / 节点名称: request_normalization / 请求归一
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_MEMORY, COG_GOVERNANCE]
    related_topology / 相关拓扑: [TOP_CHAIN]
  - node_id / 节点编号: NODE_MEMORY_LAYER_CLASSIFY
    node_name / 节点名称: memory_layer_classification / 记忆分层判定
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_MEMORY]
    related_topology / 相关拓扑: [TOP_HIERARCHY, TOP_ROUTING]
  - node_id / 节点编号: NODE_CONTEXT_ASSEMBLY
    node_name / 节点名称: context_assembly / 上下文装配
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_MEMORY, COG_REASONING]
    related_topology / 相关拓扑: [TOP_ORCHESTRATION]
  - node_id / 节点编号: NODE_MEMORY_WRITE_ROUTE
    node_name / 节点名称: memory_write_routing / 记忆写入路由
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_MEMORY, COG_GOVERNANCE]
    related_topology / 相关拓扑: [TOP_ROUTING]
  - node_id / 节点编号: NODE_MEMORY_PROMOTION
    node_name / 节点名称: memory_promotion / 记忆升层
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_MEMORY, COG_REFLECTION]
    related_topology / 相关拓扑: [TOP_LOOP, TOP_HIERARCHY]
  - node_id / 节点编号: NODE_MEMORY_DECAY
    node_name / 节点名称: memory_demotion_and_expiry / 记忆降权与过期
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_MEMORY, COG_GOVERNANCE]
    related_topology / 相关拓扑: [TOP_LOOP]
```

### Skill Packaging Draft / 可包装技能草案

```yaml
Skill Draft / 技能草案:
  skill_id / 技能编号: SKILL_LAYERED_MEMORY_GOVERNANCE
  skill_name / 技能名称: Layered Memory Governance / 分层记忆治理
  version / 版本: 0.1.0
  status / 状态: draft / 草稿
  related_patterns / 关联模式:
    - Layered Retention / 分层保留
  related_cognition / 关联认知:
    - COG_MEMORY
    - COG_GOVERNANCE
    - COG_REFLECTION
  related_topology / 关联拓扑:
    - TOP_HIERARCHY
    - TOP_ROUTING
    - TOP_LOOP
    - TOP_ORCHESTRATION
  related_business_nodes / 关联业务节点:
    - NODE_MEMORY_LAYER_CLASSIFY
    - NODE_CONTEXT_ASSEMBLY
    - NODE_MEMORY_WRITE_ROUTE
    - NODE_MEMORY_PROMOTION
    - NODE_MEMORY_DECAY
```

### Version Extension Suggestions / 版本扩展建议

Future versions can add / 后续版本可以继续补充:

1. Default layer templates for more scenarios. / 不同场景的默认层级模板。
2. Structured field standards for each memory type. / 每类记忆的结构化字段标准。
3. Evidence scoring rules for promotion. / 记忆升层的证据评分规则。
4. Real-time protocol with workflow observability probes. / 与工作流可观测性探针的实时交互协议。
5. Rollback, archive, audit, and migration processes. / 记忆回滚、归档、审计和迁移流程。
6. Write-permission matrix based on business risk. / 基于业务风险的写入权限矩阵。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Layered Retention / 分层保留; Layered Retention Execution Flow / 分层保留执行流程.
- 诊断用途 / Diagnostic Use: Use when information must be retained by scope, lifecycle, authority, evidence, and context budget across multiple memory levels. / 当信息必须按照作用域、生命周期、权威来源、证据和上下文预算跨多层记忆保留时使用。
- 适用工作流节点 / Applicable Workflow Nodes: request intake, context recovery, memory classification, context assembly, write routing, promotion, demotion, audit, human review / 请求进入、上下文恢复、记忆分层、上下文装配、写入路由、升层、降权、审计、人审。
- 当前症状 / Current Symptoms: Temporary guesses become durable facts, low-level context overrides policy or project rules, history fills the context window, repeated failures are forgotten, or writeback has no evidence. / 临时猜测变成长期事实、低层上下文覆盖策略或项目规则、历史填满上下文、重复失败被遗忘，或写回缺少证据。
- 适配信号 / Fit Signals: Knowledge must be stored by organization, project, tenant, user, task, session, or turn, and each layer has different authority and lifecycle. / 知识必须按组织、项目、租户、用户、任务、会话或轮次存放，且每层具备不同权威和生命周期。
- 调整方向 / Adjustment Direction: Insert a layered retention flow before durable writeback and before large-history context assembly. / 在长期写回和大历史上下文装配前插入分层保留流程。
- 修改方式 / How To Modify: Add memory layers, read/write permissions, classification rules, coverage rules, promotion gates, context assembly priority, lifecycle rules, and optional probe interaction. / 增加记忆层、读写权限、分层规则、覆盖规则、升层门禁、上下文装配优先级、生命周期规则和可选探针交互。
- 输入 / Inputs: execution request, policy constraints, project context, user context, task state, current-turn material, tool results, evidence references, context budget, optional probe reports. / 执行请求、策略约束、项目上下文、用户上下文、任务状态、当前轮材料、工具结果、证据引用、上下文预算、可选探针报告。
- 输出 / Outputs: final response, used-memory list, write decisions, context assembly record, risk and governance record, observability events, next-step recommendations. / 最终响应、使用的记忆、写入决策、上下文装配记录、风险治理记录、可观测事件、下一步建议。
- 风险与治理 / Risks & Governance: Durable memory writes require source, evidence, scope, lifecycle, conflict checks, expiry or review rules, and human review for policy, permission, production, billing, or sensitive information. / 长期记忆写入必须具备来源、证据、作用域、生命周期、冲突检查、过期或复核规则；涉及策略、权限、生产、账单或敏感信息时必须人审。

Observability Metrics File / 可观测性指标文件: [memory-hierarchy-observability.md](memory-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. Record the scenario, layer model, write-routing changes, promotion gates, context assembly effect, blocked writes, evidence coverage, and observed outcome. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。记录场景、层级模型、写入路由变化、升层门禁、上下文装配效果、阻断写入、证据覆盖和观察结果。
