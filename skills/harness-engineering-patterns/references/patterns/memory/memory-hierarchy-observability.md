# Layered Retention / 分层保留 Observability Metrics / 可观测性指标

Cell / 交织点: memory-hierarchy / 记忆 x 层级
Capability / 能力: Memory / 记忆
Mode / 模式: Hierarchy / 层级
Source / 来源: User-extension pattern grounded in Hanerss workflow practice; arXiv:2605.13850 leaves this matrix cell unnamed. / 用户扩展模式，基于 Hanerss 工作流实践；arXiv:2605.13850 未命名该交织点。
Alias / 别名: Layered Retention Probe / 分层保留的工作流可观测性探针
Standalone Executable / 可独立执行: Yes / 是
Primary Axes / 主轴: Perception / 感知; Governance / 治理
Secondary Axes / 辅轴: Memory / 记忆; Reflection / 反思
Primary Topology / 主拓扑: Routing / 路由
Secondary Topologies / 辅拓扑: Loop / 循环; Orchestration / 编排; Hierarchy / 层级

Use this file as the observability metrics and probe protocol source for Layered Retention / 分层保留. / 将本文档作为分层保留的可观测性指标与探针协议来源。
Design Pattern File / 设计模式文件: [memory-hierarchy.md](memory-hierarchy.md)

## Document Goal / 文档目标

This document defines a general workflow observability probe system for observing, completing, and correcting key data in the Layered Retention / 分层保留 execution flow. It is not only a metric list; it is a set of probes that can connect to workflow nodes. Each probe must answer what to observe, where to get data, how to identify abnormal states, what to feed back to the execution flow, when to block, and when to request human review. / 本文档定义一套通用的工作流可观测性探针系统，用于观察、补全和校正分层保留执行流程中的关键数据。它不是单纯的指标清单，而是一组可以接入工作流节点的探针。每个探针都要回答：观察什么、从哪里取数、如何判断异常、向执行流程补回什么数据、何时阻断、何时人审。

This probe system can run independently or interactively with the Layered Retention execution flow. In standalone mode, it analyzes historical logs, conversation traces, memory write records, and context assembly records, then outputs risk reports and completion advice. In interactive mode, it receives runtime events at key execution nodes and returns completion packages to correct layering, evidence, context, write routing, and governance actions. / 本探针系统可以独立运行，也可以与分层保留执行流程交互运行。独立运行时，它分析历史日志、对话轨迹、记忆写入记录和上下文装配记录，输出风险报告和补全建议。交互运行时，它在执行流程关键节点实时接收事件，并返回补全包，用于修正分层、证据、上下文、写入路由和治理动作。

## Position In Hanerss / 在 Hanerss 框架中的位置

| Foundation / 基座 | Alignment / 归属 |
|---|---|
| Cognitive foundation / 认知基座 | Perception, Memory, Reflection, Governance / 感知、记忆、反思、治理 |
| Topology foundation / 拓扑基座 | Routing, Loop, Orchestration, Hierarchy / 路由、循环、编排、层级 |
| Engineering pattern foundation / 工程模式基座 | Observability completion pattern for Layered Retention / 分层保留的可观测性补全模式 |
| Skill layer / 技能层 | Can be packaged as Workflow Observability Probe / 可包装为“工作流可观测性探针技能” |

Probe roles / 探针定位:

| Role / 定位 | Description / 说明 |
|---|---|
| Observer / 观察器 | Collect execution-node, memory-layer, evidence, context, and write events. / 采集执行节点、记忆层、证据、上下文和写入事件。 |
| Completer / 补全器 | Fill missing execution data such as evidence, risk, and layer corrections. / 为执行流程补充缺失数据，例如证据、风险、层级修正。 |
| Gatekeeper / 守门器 | Block policy override, cross-tenant contamination, and evidence-free promotion. / 对策略覆盖、跨租户污染、无证据升层等问题进行阻断。 |
| Retrospector / 复盘器 | Analyze failures, expiry, noise, and incorrect writes offline. / 对失败、过期、噪声、误写进行离线分析。 |
| Tuner / 调参器 | Adjust thresholds, sampling frequency, and alert levels by scenario. / 根据不同场景调整阈值、采样频率和告警等级。 |

## Probe Role / 探针定位

Probe does not own memory writes / 探针不直接拥有记忆写入. It observes the layered retention flow, fills missing evidence, checks whether write routing is safe, and reports whether context assembly and lifecycle handling are healthy. / 探针不直接写入记忆、不覆盖策略、不代替人审；它观察分层保留流程，补全缺失证据，检查写入路由是否安全，并报告上下文装配和生命周期处理是否健康。

The probe answers / 探针回答:

- Which workflow node produced the signal? / 信号发生在流程哪个节点？
- Which memory layer is affected? / 影响哪一层记忆？
- Does the execution flow need missing data filled? / 是否需要补全执行数据？
- Does the write route need correction? / 是否需要修正写入路由？
- Does the action or write need blocking or human review? / 是否需要阻断或人审？
- Should the signal become retrospective material? / 是否形成后续复盘材料？
- Is every retention candidate assigned to a layer? / 每条保留候选是否都有层级？
- Does every durable write have source, scope, lifecycle, and evidence? / 每个长期写入是否具备来源、作用域、生命周期和证据？
- Did any lower-layer item attempt to override a higher-layer rule? / 是否有低层信息试图覆盖高层规则？
- Was context assembled from necessary summaries and references instead of full history? / 上下文是否由必要摘要和引用装配，而不是全量历史？

## Probe Principles / 探针运行原则

### Probe Is Not Only A Result Metric / 探针不是结果指标

Ordinary metrics describe what happened. Workflow observability probes must also explain where it happened, what memory layer it affected, whether execution data needs completion, whether write routing should change, whether blocking or human review is required, and whether the issue becomes retrospective material. / 普通指标只说明“发生了什么”。工作流可观测性探针还必须说明它发生在哪个流程节点、影响哪一层记忆、是否需要补全执行数据、是否需要修正写入路由、是否需要阻断或人审，以及是否形成后续复盘材料。

### Probe Must Be Feedback-Capable / 探针必须可回填

Each probe output should be usable by the execution flow whenever possible. / 每个探针的输出都应尽量能被执行流程使用。

```yaml
Probe Output / 探针输出:
  judgment / 判断结果: normal | abnormal | risk | blocked | human_review
  affected_node / 影响节点: required / 必填
  affected_layer / 影响层级: optional / 可选
  completion_fields / 补全字段: optional / 可选
  evidence_refs / 证据引用: []
  recommended_actions / 建议动作: []
  feed_back_to_execution_flow / 是否回填执行流程: yes | no
```

### Probe Must Support Multiple Scenarios / 探针必须支持多场景

The same probe should use different thresholds in different scenarios. / 同一个探针在不同场景下阈值不同。

| Scenario / 场景 | Probe Strategy / 探针策略 |
|---|---|
| Personal assistant / 个人助理 | Flexible by default; prevent temporary preferences from being written to durable user memory. / 偏向灵活，重点防止临时偏好误写长期层。 |
| Coding assistant / 编程助手 | Verify project rules, test results, and debugging state. / 重点验证项目规则、测试结果、调试状态。 |
| Enterprise knowledge assistant / 企业知识助手 | Monitor permissions, tenant isolation, and expired policies. / 重点监控权限、租户隔离、过期政策。 |
| Course coach / 课程教练 | Observe mastery evidence and session-state contamination. / 重点观察掌握度证据和会话状态污染。 |
| Support assistant / 客服助手 | Observe policy consistency, ticket state, and user-data isolation. / 重点观察政策一致性、工单状态、用户数据隔离。 |
| Approval assistant / 审批助手 | Observe approval gates, audit completeness, and real-time writeback of critical state. / 重点观察审批门禁、审计完整性、关键状态实时写回。 |

## Relationship With Execution Flow / 与执行流程的关系

Sidecar observation mode / 旁路观测模式:

```text
Existing workflow / 现有工作流
  -> Copy layered-retention events / 复制分层保留事件
  -> Probe checks layer, evidence, conflict, budget, and lifecycle / 探针检查层级、证据、冲突、预算和生命周期
  -> Observability report / 可观测性报告
  -> Retention improvement advice / 保留策略改进建议
```

Interactive guard mode / 交互守卫模式:

```text
Before writeback / 写回前
  -> Probe evaluates write candidates / 探针评估写入候选
  -> Flow routes write, blocks, or requests review / 流程执行写入路由、阻断或人审
  -> Probe checks post-write trace / 探针检查写后轨迹
  -> Repair, demote, or audit / 修复、降权或审计
```

Replay evaluation mode / 回放评估模式:

```text
Historical runs / 历史运行
  -> Reconstruct candidates, layer decisions, context packages, and write decisions / 重建候选、分层决策、上下文包和写入决策
  -> Score correctness and safety / 评分正确性与安全性
  -> Produce rule updates / 生成规则更新建议
```

## Operating Modes / 运行模式

| Mode / 模式 | Use / 用途 | Output / 输出 |
|---|---|---|
| Sidecar Probe / 旁路探针 | Observe an existing workflow without blocking it. / 旁路观察现有流程，不阻塞主流程。 | Observation Report / 观测报告. |
| Inline Guard / 内联守卫 | Check write candidates before durable memory changes. / 在长期记忆变更前检查写入候选。 | Block, allow, demote, or human-review decision / 阻断、允许、降权或人审决策。 |
| Shadow Evaluator / 影子评估器 | Evaluate old runs against newer retention rules. / 用新规则评估历史运行。 | Replay score and rule-change advice / 回放评分与规则调整建议。 |
| Lifecycle Monitor / 生命周期监控器 | Watch expiry, stale memory, conflicts, and review queues. / 监控过期、陈旧记忆、冲突和复核队列。 | Lifecycle alert and cleanup advice / 生命周期告警与清理建议。 |

## Probe Input Contract / 探针输入契约

Required input / 必需输入:

```yaml
Layered Retention Trace / 分层保留轨迹:
  request_id / 请求编号: required / 必填
  scenario_type / 场景类型: required / 必填
  layer_model / 层级模型: []
  retention_candidates / 保留候选: []
  layer_decisions / 分层决策: []
  conflict_checks / 冲突检查: []
  context_assembly_record / 上下文装配记录: {}
  write_decisions / 写入决策: []
  lifecycle_actions / 生命周期动作: []
  final_result_ref / 最终结果引用: ""
  occurred_at / 发生时间: required / 必填
```

Optional input / 可选输入:

```yaml
Optional Probe Context / 可选探针上下文:
  policy_boundary_package / 策略边界包: {}
  project_rules / 项目规则: []
  user_profile_summary / 用户画像摘要: {}
  task_state_history / 任务状态历史: []
  source_handle_map / 来源句柄映射: {}
  evidence_records / 证据记录: []
  permission_context / 权限上下文: {}
  context_budget / 上下文预算: {}
  prior_probe_reports / 历史探针报告: []
```

## Data Model / 探针数据模型

### Probe Definition / 探针定义

```yaml
Probe Definition / 探针定义:
  probe_id / 探针编号: required / 必填
  probe_name / 探针名称: required / 必填
  target_nodes / 目标节点: []
  observation_objects / 观察对象: []
  input_events / 输入事件: []
  output_fields / 输出字段: []
  judgment_rules / 判断规则: required / 必填
  severity / 异常等级: hint | suggestion | risk | block | human_review
  feedback_method / 回填方式: none | complete_field | correct_decision | block_action | trigger_human_review
  applicable_scenarios / 适用场景: []
  default_thresholds / 默认阈值: optional / 可选
  related_coordinates / 关联坐标: []
```

### Flow Event / 流程事件

```yaml
Flow Event / 流程事件:
  request_id / 请求编号: required / 必填
  event_id / 事件编号: required / 必填
  node_id / 节点编号: required / 必填
  node_name / 节点名称: required / 必填
  event_type / 事件类型: required / 必填
  scenario_type / 场景类型: required / 必填
  affected_layer / 影响层级: optional / 可选
  input_summary / 输入摘要: optional / 可选
  output_summary / 输出摘要: optional / 可选
  used_memory_refs / 使用记忆引用: []
  write_candidates / 写入候选: []
  evidence_refs / 证据引用: []
  risk_marks / 风险标记: []
  budget_data / 预算数据: {}
  time / 时间: required / 必填
```

### Probe Result / 探针结果

```yaml
Probe Result / 探针结果:
  probe_id / 探针编号: required / 必填
  request_id / 请求编号: required / 必填
  target_node / 目标节点: required / 必填
  result_level / 结果等级: normal | hint | suggestion | risk | block | human_review
  findings / 发现问题: optional / 可选
  matched_rules / 命中规则: []
  completion_fields / 补全字段: {}
  evidence_refs / 证据引用: []
  recommended_actions / 建议动作: []
  should_feedback / 是否回填: yes | no
  generated_at / 生成时间: required / 必填
```

### Workflow Completion Package / 工作流补全包

```yaml
Workflow Completion Package / 工作流补全包:
  request_id / 请求编号: required / 必填
  source_probe / 来源探针: required / 必填
  target_node / 目标节点: required / 必填
  completion_type / 补全类型: layer_correction | evidence_completion | context_completion | write_correction | risk_block | human_review_request | lifecycle_correction
  advice_level / 建议等级: hint | suggestion | risk | block | human_review
  completion_content / 补全内容:
    suggested_layer / 建议层级: optional / 可选
    suggested_evidence / 建议证据: []
    suggested_memory_removals / 建议移除记忆: []
    suggested_memory_additions / 建议补充记忆: []
    suggested_write_route / 建议写入路由: optional / 可选
    suggested_expiry_action / 建议过期动作: optional / 可选
    suggested_audit_action / 建议审计动作: optional / 可选
  reason / 原因: required / 必填
  evidence_refs / 证据引用: []
```

## Event Stream / 事件流

Track the following event types / 追踪以下事件类型:

| Event Type / 事件类型 | Required Fields / 必需字段 | Purpose / 用途 |
|---|---|---|
| request_normalized / 请求归一完成 | request_id, scenario_type, current_goal / 请求编号、场景类型、当前目标 | Anchor the run. / 锚定本次执行。 |
| policy_loaded / 策略加载完成 | policy_refs, forbidden_actions, approval_required_actions / 策略引用、禁止动作、审批动作 | Check higher-layer boundary. / 检查高层边界。 |
| context_recovered / 上下文恢复完成 | loaded_layers, missing_context, source_refs / 已加载层级、缺失上下文、来源引用 | Evaluate context hit and gaps. / 评估上下文命中和缺口。 |
| candidate_collected / 候选采集完成 | candidate_id, source, trust, verified / 候选编号、来源、可信度、验证状态 | Prepare layer classification. / 准备分层判定。 |
| layer_decided / 分层判定完成 | candidate_id, assigned_layer, reason / 候选编号、判定层级、原因 | Score classification accuracy. / 评分分层准确性。 |
| conflict_checked / 冲突检查完成 | conflict_type, handling, blocked / 冲突类型、处理方式、是否阻断 | Detect coverage violations. / 发现覆盖违规。 |
| context_assembled / 上下文装配完成 | resident, deferred, excluded, budget_usage / 常驻、延迟读取、排除、预算使用 | Check budget and relevance. / 检查预算和相关性。 |
| tool_result_verified / 工具结果验证完成 | tool_name, input_ref, output_ref, reproducibility / 工具名称、输入引用、输出引用、可复现性 | Decide whether tool evidence can support writes. / 判断工具证据是否可支持写入。 |
| checkpoint_written / 检查点写回完成 | task_state_ref, freshness, missing_state / 任务状态引用、新鲜度、缺失状态 | Detect long-running state loss risk. / 发现长程任务状态丢失风险。 |
| write_routed / 写入路由完成 | route, evidence_refs, rejection_reason / 路由、证据引用、拒绝原因 | Validate write safety. / 验证写入安全。 |
| lifecycle_handled / 生命周期处理完成 | action, trigger, review_time / 动作、触发条件、复核时间 | Check cleanup and review. / 检查清理和复核。 |
| result_emitted / 结果输出完成 | final_response_ref, next_steps / 结果引用、下一步 | Close trace. / 闭合轨迹。 |

## Probe Output Contract / 探针输出契约

Minimum output / 最小输出:

```yaml
Layered Retention Probe Report / 分层保留探针报告:
  report_id / 报告编号: ""
  request_id / 请求编号: ""
  health_state / 健康状态: healthy | warning | unsafe | blocked
  main_findings / 主要发现: []
  missing_evidence / 缺失证据: []
  layer_corrections / 层级修正: []
  conflict_alerts / 冲突告警: []
  context_budget_findings / 上下文预算发现: []
  write_routing_findings / 写入路由发现: []
  lifecycle_findings / 生命周期发现: []
  recommended_actions / 建议动作: []
  audit_refs / 审计引用: []
```

Inline guard output / 内联守卫输出:

```yaml
Retention Guard Decision / 保留守卫决策:
  candidate_id / 候选编号: ""
  decision / 决策: allow | block | demote | require_human_review | request_evidence
  target_layer / 目标层级: ""
  reason / 原因: ""
  required_repairs / 必需修复: []
  evidence_refs / 证据引用: []
  review_required_by / 人审要求: ""
```

## Observation Objects / 观测对象

Retention Candidate / 保留候选:

```yaml
Retention Candidate / 保留候选:
  candidate_id / 候选编号: ""
  source / 来源: ""
  scope / 作用域: ""
  lifecycle / 生命周期: ""
  authority / 权威来源: ""
  evidence_refs / 证据引用: []
  initial_layer / 初始层级: ""
  assigned_layer / 判定层级: ""
  write_route / 写入路由: ""
```

Context Package / 上下文包:

```yaml
Context Package / 上下文包:
  resident_content / 常驻内容: []
  summarized_content / 摘要内容: []
  deferred_read_refs / 延迟读取引用: []
  excluded_content / 排除内容: []
  budget_limit / 预算上限: ""
  budget_used / 已用预算: ""
  missing_required_context / 缺失必要上下文: []
```

Lifecycle Action / 生命周期动作:

```yaml
Lifecycle Action / 生命周期动作:
  memory_id / 记忆编号: ""
  action / 动作: promote | demote | archive | delete | review
  trigger / 触发条件: ""
  evidence_refs / 证据引用: []
  before_state / 变更前状态: {}
  after_state / 变更后状态: {}
  audit_ref / 审计引用: ""
```

## Probe Catalog / 探针总览

| Probe ID / 探针编号 | Probe Name / 探针名称 | Main Goal / 主要目标 | Feedback Target / 回填对象 |
|---|---|---|---|
| Probe 001 / 探针_001 | Scenario Completeness Probe / 场景完整性探针 | Check whether scenario, goal, permission, and constraints are complete. / 检查场景、目标、权限、约束是否齐全。 | Request normalization node / 请求归一节点 |
| Probe 002 / 探针_002 | Policy Boundary Probe / 策略边界探针 | Check whether policy boundaries are loaded. / 检查是否加载策略边界。 | Policy loading node / 策略加载节点 |
| Probe 003 / 探针_003 | Layer Decision Probe / 层级判定探针 | Check whether memories are assigned to correct layers. / 检查记忆是否放入正确层级。 | Layer classification node / 分层判定节点 |
| Probe 004 / 探针_004 | Scope Isolation Probe / 作用域隔离探针 | Check whether user, tenant, or project data is mixed. / 检查用户、租户、项目是否串用。 | Conflict check node / 冲突检查节点 |
| Probe 005 / 探针_005 | Evidence Sufficiency Probe / 证据充分性探针 | Check whether durable writes have evidence. / 检查长期写入是否有证据。 | Write routing node / 写入路由节点 |
| Probe 006 / 探针_006 | Draft Leakage Probe / 草稿泄漏探针 | Check whether draft content enters durable layers incorrectly. / 检查草稿内容是否误入长期层。 | Write routing node / 写入路由节点 |
| Probe 007 / 探针_007 | Override Violation Probe / 覆盖违规探针 | Check whether lower layers override higher-layer facts. / 检查低层是否覆盖高层事实。 | Conflict check node / 冲突检查节点 |
| Probe 008 / 探针_008 | Context Hit Probe / 上下文命中探针 | Check whether required memory enters context. / 检查该进入上下文的记忆是否进入。 | Context assembly node / 上下文装配节点 |
| Probe 009 / 探针_009 | Context Noise Probe / 上下文噪声探针 | Check whether irrelevant, expired, or repeated information enters context. / 检查无关、过期、重复信息是否进入上下文。 | Context assembly node / 上下文装配节点 |
| Probe 010 / 探针_010 | Context Budget Probe / 上下文预算探针 | Check whether lower layers crowd out higher-priority context. / 检查各层预算是否挤占。 | Context assembly node / 上下文装配节点 |
| Probe 011 / 探针_011 | Tool Result Validation Probe / 工具结果验证探针 | Check whether tool results are reproducible and traceable. / 检查工具结果是否可复现、可追溯。 | Action execution node / 执行动作节点 |
| Probe 012 / 探针_012 | Checkpoint Freshness Probe / 检查点新鲜度探针 | Check whether task state is written back in time. / 检查任务状态是否及时写回。 | State-change node / 状态变化节点 |
| Probe 013 / 探针_013 | Promotion Gate Probe / 升层门禁探针 | Check whether short-term memory meets durable promotion rules. / 检查短期记忆升长期层是否满足条件。 | Promotion node / 升层节点 |
| Probe 014 / 探针_014 | Expiry And Demotion Probe / 过期与降权探针 | Check whether old memory should be demoted, archived, or deleted. / 检查旧记忆是否需要降权、归档或删除。 | Lifecycle node / 生命周期节点 |
| Probe 015 / 探针_015 | Failure Retrospective Probe / 失败复盘探针 | Check whether failures become reusable lessons. / 检查失败是否转化为可复用经验。 | Reflection node / 反思节点 |
| Probe 016 / 探针_016 | Output Traceability Probe / 输出可追溯探针 | Check whether final output traces to used memory and evidence. / 检查最终结果是否能追溯到使用的记忆和证据。 | Output node / 输出节点 |
| Probe 017 / 探针_017 | Human Review Gate Probe / 人审门禁探针 | Check whether high-risk writes or actions enter human review. / 检查高风险写入或动作是否进入人审。 | Governance node / 治理节点 |
| Probe 018 / 探针_018 | Structured Discipline Probe / 结构化纪律探针 | Check whether durable memory has version, source, confidence, and expiry. / 检查长期层是否有版本、来源、置信度、有效期。 | Write routing node / 写入路由节点 |

## Probe Details / 探针详情

### Probe 001: Scenario Completeness Probe / 探针_001：场景完整性探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Request normalization node / 请求归一节点 |
| Observation objects / 观察对象 | Scenario type, current goal, user input, permission context, project context. / 场景类型、当前目标、用户输入、权限上下文、项目上下文。 |
| Judgment rule / 判断规则 | Mark risk when scenario type, goal, permission, or critical constraints are missing. / 缺少场景类型、目标、权限或关键约束时标记为风险。 |
| Feedback / 回填内容 | Missing fields, default scenario config, clarification questions. / 缺失字段清单、默认场景配置、待澄清问题。 |
| Severity / 异常等级 | suggestion or risk / 建议或风险 |

Example output / 输出示例:

```yaml
Probe Result / 探针结果:
  probe_id / 探针编号: Probe 001 / 探针_001
  result_level / 结果等级: suggestion / 建议
  finding / 发现问题: permission context is missing / 缺少权限上下文
  completion_fields / 补全字段:
    missing_fields / 待补字段:
      - user_role / 用户角色
      - allowed_actions / 可执行动作
  recommended_actions / 建议动作:
    - run in low-risk mode / 按低风险模式执行
    - forbid high-risk actions / 禁止高风险动作
```

### Probe 002: Policy Boundary Probe / 探针_002：策略边界探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Policy loading node, conflict check node. / 策略加载节点、冲突检查节点。 |
| Observation objects / 观察对象 | Policy load result, forbidden actions, approval-required actions. / 策略层加载结果、禁止动作、必须审批动作。 |
| Judgment rule / 判断规则 | Trigger when policy layer is empty or high-risk actions have no approval requirement. / 策略层为空或高风险动作没有审批要求时触发。 |
| Feedback / 回填内容 | Policy gap, conservative execution mode, blocking advice. / 策略缺口、保守执行模式、阻断建议。 |
| Severity / 异常等级 | risk, block, or human review / 风险、阻断或人审 |

### Probe 003: Layer Decision Probe / 探针_003：层级判定探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Layer classification node / 分层判定节点 |
| Observation objects / 观察对象 | Scope, lifecycle, source, evidence, and budget of each memory candidate. / 每条记忆候选的作用域、生命周期、来源、证据、预算。 |
| Judgment rule / 判断规则 | Trigger when layer and scope mismatch, or durable write lacks evidence. / 层级与作用域不一致，或长期层写入缺少证据时触发。 |
| Feedback / 回填内容 | Suggested layer, demotion suggestion, evidence requirement. / 建议层级、降级建议、补充证据要求。 |
| Severity / 异常等级 | suggestion or block / 建议或阻断 |

Layer correction examples / 判定示例:

| Finding / 发现 | Feedback Advice / 回填建议 |
|---|---|
| Current-turn user emotion is written to user layer. / 当前轮用户情绪被写入用户层。 | Demote to task layer and set short expiry. / 降为任务层，设置短期有效期。 |
| Single tool result is written to project layer. / 单次工具结果被写入项目层。 | Demote to draft or task layer until reproducible evidence exists. / 降为草稿层或任务层，等待复现证据。 |
| Organization rule is written as project preference. / 组织规则被写成项目偏好。 | Promote to policy candidate and require human review. / 升为策略层候选，进入人审。 |

### Probe 004: Scope Isolation Probe / 探针_004：作用域隔离探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Context recovery, conflict check, write routing. / 上下文恢复节点、冲突检查节点、写入路由节点。 |
| Observation objects / 观察对象 | User id, tenant id, project id, memory references, write target. / 用户编号、租户编号、项目编号、记忆引用、写入目标。 |
| Judgment rule / 判断规则 | Trigger when unauthorized memory references cross users, tenants, or projects. / 不同用户、租户、项目之间出现未授权记忆引用时触发。 |
| Feedback / 回填内容 | Polluted references, memory to remove, audit event. / 污染引用、需移除记忆、审计事件。 |
| Severity / 异常等级 | block / 阻断 |

### Probe 005: Evidence Sufficiency Probe / 探针_005：证据充分性探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Write routing node, promotion node. / 写入路由节点、升层节点。 |
| Observation objects / 观察对象 | Write candidates, evidence refs, source, confidence. / 写入候选、证据引用、来源、置信度。 |
| Judgment rule / 判断规则 | Trigger when durable writes lack evidence, rely only on model inference, or evidence scope mismatches target layer. / 写入长期层但没有证据、只有模型推断、证据范围不匹配时触发。 |
| Feedback / 回填内容 | Evidence gap, verification tasks, reject-write advice. / 证据缺口、待验证项、拒绝写入建议。 |
| Severity / 异常等级 | suggestion, block, or human review / 建议、阻断或人审 |

Minimum evidence requirements / 最低证据要求:

| Target layer / 目标层 | Minimum evidence / 最低证据要求 |
|---|---|
| Policy / 策略层 | Management process, human review, config change record. / 管理流程、人审、配置变更记录。 |
| Project / 项目层 | Repository file, review record, maintainer confirmation, reproducible tool result. / 仓库文件、评审记录、项目维护者确认、可复现工具结果。 |
| User / 用户层 | Explicit user confirmation, repeated stable behavior, task outcome evidence. / 用户明确确认、多次稳定行为、任务结果证据。 |
| Task / 任务层 | Current execution trace, tool result, user input. / 当前执行轨迹、工具结果、用户输入。 |
| Draft / 草稿层 | Evidence optional, but source and time are required. / 可无证据，但必须有来源和时间。 |

### Probe 006: Draft Leakage Probe / 探针_006：草稿泄漏探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Write routing node, promotion node. / 写入路由节点、升层节点。 |
| Observation objects / 观察对象 | Draft-layer content, durable-layer write record, evidence chain. / 草稿层内容、长期层写入记录、证据链。 |
| Judgment rule / 判断规则 | Trigger when unverified guesses, temporary variables, or half-finished tool output write directly to durable layers. / 未验证猜测、临时变量、工具半成品直接写长期层时触发。 |
| Feedback / 回填内容 | Block write, demote to draft layer, create verification task. / 写入阻断、降回草稿层、待验证任务。 |
| Severity / 异常等级 | block / 阻断 |

### Probe 007: Override Violation Probe / 探针_007：覆盖违规探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Conflict check node, write routing node. / 冲突检查节点、写入路由节点。 |
| Observation objects / 观察对象 | Higher-layer rules, lower-layer candidates, override action. / 高层规则、低层候选、覆盖动作。 |
| Judgment rule / 判断规则 | Trigger when user preference overrides policy, task state overrides project layer, or draft judgment overrides user layer. / 用户偏好覆盖策略层、任务状态覆盖项目层、草稿判断覆盖用户层时触发。 |
| Feedback / 回填内容 | Override block, conflict reason, higher-layer rule reference. / 覆盖阻断、冲突原因、高层规则引用。 |
| Severity / 异常等级 | block or human review / 阻断或人审 |

### Probe 008: Context Hit Probe / 探针_008：上下文命中探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Context assembly node / 上下文装配节点 |
| Observation objects / 观察对象 | Current goal, loaded memory, excluded memory, final answer. / 当前目标、装入上下文的记忆、被排除记忆、最终回答。 |
| Judgment rule / 判断规则 | Trigger when critical policy, project rules, user summary, or task state is missing. / 关键策略、项目规则、用户摘要、任务状态遗漏时触发。 |
| Feedback / 回填内容 | Suggested memory additions, missing reason, reassembly advice. / 建议补入记忆、缺失原因、再次装配建议。 |
| Severity / 异常等级 | suggestion or risk / 建议或风险 |

Context hit guidance / 命中计算建议:

```yaml
Context Hit Judgment / 命中判断:
  must_hit / 必须命中:
    - policy_boundary / 策略边界
    - current_task_goal / 当前任务目标
    - current_turn_user_input / 当前轮用户输入
  conditional_hit / 条件命中:
    - project_rules / 项目规则
    - user_preference / 用户偏好
    - recent_task_state / 最近任务状态
    - related_failure_experience / 相关失败经验
  optional_miss / 可不命中:
    - expired_history / 过期历史
    - irrelevant_durable_profile / 与当前任务无关的长期画像
    - unverified_draft / 未验证草稿
```

### Probe 009: Context Noise Probe / 探针_009：上下文噪声探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Context assembly node / 上下文装配节点 |
| Observation objects / 观察对象 | Loaded context, relevance, expiry, duplication. / 装入上下文的信息、相关性、有效期、重复度。 |
| Judgment rule / 判断规则 | Trigger when irrelevant history, expired rules, duplicate memory, or low-trust drafts occupy context. / 无关历史、过期规则、重复记忆、低可信草稿占用上下文时触发。 |
| Feedback / 回填内容 | Removal advice, compression advice, deferred-read advice. / 建议移除内容、压缩建议、按需读取建议。 |
| Severity / 异常等级 | hint or suggestion / 提示或建议 |

### Probe 010: Context Budget Probe / 探针_010：上下文预算探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Context assembly node / 上下文装配节点 |
| Observation objects / 观察对象 | Budget usage by layer, actual loaded content, displaced content. / 各层预算使用、实际装入内容、被挤出内容。 |
| Judgment rule / 判断规则 | Trigger when lower-layer content displaces higher-layer boundaries or budget exceeds threshold. / 低层内容挤出高层边界，或预算使用超过阈值时触发。 |
| Feedback / 回填内容 | Budget reallocation, summarization, reference-only conversion. / 预算重分配建议、摘要化建议、引用化建议。 |
| Severity / 异常等级 | suggestion or risk / 建议或风险 |

Default budget priority / 默认预算优先级:

| Priority / 优先级 | Content / 内容 |
|---|---|
| First / 第一优先 | Policy boundary, current goal, current-turn key input. / 策略边界、当前目标、当前轮关键输入。 |
| Second / 第二优先 | Hard project rules, recent task state. / 项目硬规则、任务最近状态。 |
| Third / 第三优先 | User summary, related historical experience. / 用户摘要、相关历史经验。 |
| Fourth / 第四优先 | Detailed tool results, long-document fragments. / 工具详细结果、长文档片段。 |
| Fifth / 第五优先 | Low-trust draft, irrelevant history, duplicate memory. / 低可信草稿、无关历史、重复记忆。 |

### Probe 011: Tool Result Validation Probe / 探针_011：工具结果验证探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Action execution node, write routing node. / 执行动作节点、写入路由节点。 |
| Observation objects / 观察对象 | Tool name, input, output, execution status, reproducibility. / 工具名称、输入、输出、执行状态、可复现性。 |
| Judgment rule / 判断规则 | Trigger when tool fails, result is not reproducible, or input reference is missing. / 工具失败、结果不可复现、结果缺少输入引用时触发。 |
| Feedback / 回填内容 | Tool evidence state, task-layer write eligibility, promotion eligibility. / 工具证据状态、是否可写任务层、是否可升层。 |
| Severity / 异常等级 | suggestion or risk / 建议或风险 |

### Probe 012: Checkpoint Freshness Probe / 探针_012：检查点新鲜度探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | State-change node, lifecycle node. / 状态变化节点、生命周期节点。 |
| Observation objects / 观察对象 | Task state writeback time, critical state changes, latest checkpoint. / 任务状态写回时间、关键状态变化、最近检查点。 |
| Judgment rule / 判断规则 | Trigger when critical long-running task state is not written back in time. / 长程任务关键状态未及时写回时触发。 |
| Feedback / 回填内容 | Immediate writeback advice, state gap, recovery risk. / 立即写回建议、状态缺口、恢复风险。 |
| Severity / 异常等级 | risk / 风险 |

### Probe 013: Promotion Gate Probe / 探针_013：升层门禁探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Promotion node / 升层节点 |
| Observation objects / 观察对象 | Candidate source, evidence, occurrence count, target layer. / 候选来源、候选证据、历史出现次数、目标层级。 |
| Judgment rule / 判断规则 | Trigger when promotion conditions, evidence alignment, or confidence are insufficient. / 升层条件不足、证据不匹配、置信度不足时触发。 |
| Feedback / 回填内容 | Block promotion, keep candidate, require evidence. / 阻断升层、保留候选、要求补证据。 |
| Severity / 异常等级 | block or human review / 阻断或人审 |

Default promotion gates / 默认升层门槛:

| Promotion direction / 升层方向 | Default gate / 默认门槛 |
|---|---|
| Draft to task / 草稿层到任务层 | Tool validation, user-input confirmation, task trace support. / 工具结果验证、用户输入确认、任务轨迹支持。 |
| Task to user / 任务层到用户层 | Stable repetition, user confirmation, exercise or business-result support. / 多次稳定出现、用户确认、练习或业务结果支持。 |
| Task to project / 任务层到项目层 | Project file, review record, maintainer confirmation. / 项目文件、评审记录、维护者确认。 |
| Any layer to policy / 任意层到策略层 | Management process and human review. / 管理流程和人审。 |

### Probe 014: Expiry And Demotion Probe / 探针_014：过期与降权探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Lifecycle node, context assembly node. / 生命周期节点、上下文装配节点。 |
| Observation objects / 观察对象 | Memory expiry, last used time, version, conflict record. / 记忆有效期、最后使用时间、版本、冲突记录。 |
| Judgment rule / 判断规则 | Trigger when memory is expired, long unused, conflicts with new evidence, or version-lagged. / 过期、长期未使用、与新证据冲突、版本落后时触发。 |
| Feedback / 回填内容 | Demote, archive, delete, or review advice. / 降权、归档、删除、复核建议。 |
| Severity / 异常等级 | hint, suggestion, or risk / 提示、建议或风险 |

### Probe 015: Failure Retrospective Probe / 探针_015：失败复盘探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Reflection node, lifecycle node. / 反思节点、生命周期节点。 |
| Observation objects / 观察对象 | Failure record, excluded paths, error cause, repair result. / 失败记录、被排除方案、错误原因、修复结果。 |
| Judgment rule / 判断规则 | Trigger when a failure has no attribution, reusable lesson, or evidence. / 有失败但没有归因、没有可复用经验、没有证据时触发。 |
| Feedback / 回填内容 | Failure retrospective task, lesson candidate, evidence requirement. / 失败复盘任务、经验候选、证据要求。 |
| Severity / 异常等级 | suggestion / 建议 |

### Probe 016: Output Traceability Probe / 探针_016：输出可追溯探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Output node / 输出节点 |
| Observation objects / 观察对象 | Final response, used memory, evidence refs, write decisions. / 最终响应、使用记忆、证据引用、写入决策。 |
| Judgment rule / 判断规则 | Trigger when final output cannot trace to used memory or evidence. / 最终结果无法追溯到使用的记忆或证据时触发。 |
| Feedback / 回填内容 | Add references, uncertainty notes, and rejected-write reasons. / 补充引用、补充不确定性说明、补充被拒绝写入原因。 |
| Severity / 异常等级 | suggestion or risk / 建议或风险 |

### Probe 017: Human Review Gate Probe / 探针_017：人审门禁探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Governance node, write routing node, action execution node. / 治理节点、写入路由节点、执行动作节点。 |
| Observation objects / 观察对象 | High-risk action, high-authority-layer write, sensitive information, approval state. / 高风险动作、高权威层写入、敏感信息、审批状态。 |
| Judgment rule / 判断规则 | Trigger when an approval-required action does not enter human review. / 需要审批但未进入人审时触发。 |
| Feedback / 回填内容 | Human review request, blocked action, audit record. / 人审请求、阻断动作、审计记录。 |
| Severity / 异常等级 | human review or block / 人审或阻断 |

### Probe 018: Structured Discipline Probe / 探针_018：结构化纪律探针

| Field / 字段 | Content / 内容 |
|---|---|
| Target node / 目标节点 | Write routing node, promotion node. / 写入路由节点、升层节点。 |
| Observation objects / 观察对象 | Durable write fields, source, evidence, confidence, expiry, version. / 长期层写入字段、来源、证据、置信度、有效期、版本。 |
| Judgment rule / 判断规则 | Trigger when durable-layer writes are free text and lack structured fields. / 长期层写入为自由文本且缺少结构字段时触发。 |
| Feedback / 回填内容 | Structured field advice, reject-write advice, migration advice. / 结构化字段建议、拒绝写入建议、迁移建议。 |
| Severity / 异常等级 | suggestion or block / 建议或阻断 |

## Probe-To-Execution Interaction Table / 探针与执行流程交互表

| Execution Node / 执行节点 | Probes / 应接入探针 | Feedback Fields / 回填字段 |
|---|---|---|
| Request normalization / 请求归一 | Probe 001 / 探针_001 | Missing scenario, missing permission, default risk mode. / 缺失场景、缺失权限、默认风险模式。 |
| Policy loading / 策略加载 | Probe 002, Probe 017 / 探针_002、探针_017 | Policy gap, approval requirement, blocking advice. / 策略缺口、审批要求、阻断建议。 |
| Context recovery / 上下文恢复 | Probe 004, Probe 008, Probe 014 / 探针_004、探针_008、探针_014 | Missing context, polluted references, expired memory. / 缺失上下文、污染引用、过期记忆。 |
| Current-turn collection / 当前轮采集 | Probe 011 / 探针_011 | Tool result trust, input and output references. / 工具结果可信度、输入输出引用。 |
| Layer classification / 分层判定 | Probe 003, Probe 005 / 探针_003、探针_005 | Suggested layer, evidence gap. / 建议层级、证据缺口。 |
| Conflict check / 冲突检查 | Probe 004, Probe 007 / 探针_004、探针_007 | Override violation, cross-scope pollution, blocked action. / 覆盖违规、跨域污染、阻断动作。 |
| Context assembly / 上下文装配 | Probe 008, Probe 009, Probe 010 / 探针_008、探针_009、探针_010 | Add memory, remove noise, reallocate budget. / 补入记忆、移除噪声、预算重分配。 |
| Action execution / 执行动作 | Probe 011, Probe 017 / 探针_011、探针_017 | Tool-result trust, high-risk gate. / 工具结果可信度、高风险门禁。 |
| State change / 状态变化 | Probe 012 / 探针_012 | Checkpoint writeback advice, state gap. / 检查点写回建议、状态缺口。 |
| Write routing / 写入路由 | Probe 005, Probe 006, Probe 018 / 探针_005、探针_006、探针_018 | Reject durable write, structure completion. / 拒绝长期写入、结构化补全。 |
| Lifecycle handling / 生命周期处理 | Probe 013, Probe 014, Probe 015 / 探针_013、探针_014、探针_015 | Promotion block, demotion, retrospective task. / 升层阻断、降权、复盘任务。 |
| Result output / 输出结果 | Probe 016 / 探针_016 | Traceability completion, evidence completion. / 可追溯补充、证据补充。 |

## Standalone Mode / 独立运行模式

Standalone mode does not require real-time access to the execution flow. The probe system reads historical data and outputs a report. / 独立运行时，探针系统不需要实时接入执行流程。它可以读取历史数据并输出报告。

Input / 输入:

```yaml
Offline Probe Input / 离线探针输入:
  execution_logs / 执行日志: []
  conversation_traces / 对话轨迹: []
  memory_write_records / 记忆写入记录: []
  context_assembly_records / 上下文装配记录: []
  tool_call_records / 工具调用记录: []
  approval_records / 审批记录: []
  user_feedback / 用户反馈: []
```

Output / 输出:

```yaml
Offline Probe Report / 离线探针报告:
  overall_level / 总体等级: normal | hint | risk | severe
  issue_list / 问题清单:
    - issue_id / 问题编号: required / 必填
      issue_type / 问题类型: required / 必填
      affected_layer / 影响层级: optional / 可选
      affected_node / 影响节点: optional / 可选
      evidence_refs / 证据引用: []
      suggested_fix / 建议修复: []
  feedback_completion_packages / 可回填补全包: []
  human_review_items / 需人审事项: []
  memories_to_clean / 需清理记忆: []
  flow_events_to_complete / 需补充流程事件: []
```

Standalone scenarios / 独立运行适用场景:

| Scenario / 场景 | Use / 用法 |
|---|---|
| Pre-launch evaluation / 上线前评估 | Use historical samples to check layer rules and write routing. / 用历史样本检查分层规则和写入路由。 |
| Incident retrospective / 事故复盘 | Find incorrect memory, override violations, and stale-policy reuse. / 找出错误记忆、越权覆盖、过期规则复用。 |
| Periodic inspection / 周期巡检 | Clean noise, duplicates, stale items, and evidence-free content in durable layers. / 清理长期层噪声、重复、过期、无证据内容。 |
| Quality evaluation / 质量评估 | Measure context hit, draft leakage, evidence coverage, and related issues. / 统计上下文命中、草稿泄漏、证据覆盖等情况。 |

## Interactive Mode / 交互运行模式

Interactive flow / 交互流程:

```text
Execution node starts / 执行节点开始
  -> Execution flow sends node event / 执行流程发送节点事件
  -> Probe system selects relevant probes / 探针系统选择相关探针
  -> Probe system emits probe result / 探针系统产出探针结果
  -> If completion exists, return workflow completion package / 若存在补全内容，返回工作流补全包
  -> Execution flow adopts, records, blocks, or requests review by level / 执行流程根据等级采纳、记录、阻断或人审
  -> Execution node continues or stops / 执行节点继续或中止
```

Interaction level handling / 交互等级处理:

| Probe Level / 探针等级 | Execution Flow Action / 执行流程动作 |
|---|---|
| normal / 正常 | Continue execution. / 继续执行。 |
| hint / 提示 | Record hint without changing path. / 记录提示，不改变路径。 |
| suggestion / 建议 | Auto-adopt or add as candidate. / 可自动采纳，或加入候选。 |
| risk / 风险 | Degrade execution and increase evidence requirements. / 降级执行，增加证据要求。 |
| block / 阻断 | Stop corresponding action or write. / 停止对应动作或写入。 |
| human_review / 人审 | Pause automatic execution and request human confirmation. / 暂停自动执行，转入人工确认。 |

Feedback example / 回填示例:

```yaml
Workflow Completion Package / 工作流补全包:
  request_id / 请求编号: example_0001 / 示例_0001
  source_probe / 来源探针: Probe 006 / 探针_006
  target_node / 目标节点: write_routing_node / 写入路由节点
  completion_type / 补全类型: write_correction / 写入修正
  advice_level / 建议等级: block / 阻断
  completion_content / 补全内容:
    suggested_write_route / 建议写入路由: from user layer to task-layer candidate / 从用户层降为任务层候选
    suggested_evidence / 建议证据:
      - require user reconfirmation / 需要用户再次确认
      - require stable occurrence across multiple sessions / 需要多次会话稳定出现
  reason / 原因: current preference appears only once and cannot be written to durable user layer / 当前偏好只出现一次，不能写入长期用户层
  evidence_refs / 证据引用:
    - current_session_record / 当前会话记录
```

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Layered Retention / 分层保留 protects durable memory, routes writes correctly, keeps context lean, prevents unsafe coverage, and creates usable feedback packages. / 使用以下指标观察分层保留是否保护长期记忆、正确路由写入、保持上下文精简、防止不安全覆盖，并生成可用回填包。

- 质量指标 / Quality Metrics:
  - Layer Assignment Coverage / 层级判定覆盖率: Share of retention candidates with explicit layer decisions. / 具备明确层级判定的保留候选比例。
  - Layer Assignment Accuracy / 层级判定准确率: Share of reviewed decisions that match scope, lifecycle, authority, evidence, and budget. / 经复核后符合作用域、生命周期、权威、证据和预算的判定比例。
  - Durable Write Evidence Coverage / 长期写入证据覆盖率: Share of durable writes with source, evidence, scope, and lifecycle. / 长期写入中具备来源、证据、作用域和生命周期的比例。
  - Context Hit Rate / 关键记忆命中率: Share of required policy, project, user, and task memory that enters context when needed. / 需要进入上下文的策略、项目、用户、任务记忆实际命中的比例。
  - Context Noise Ratio / 上下文噪声占比: Share of resident context that is irrelevant, expired, duplicated, or low trust. / 常驻上下文中无关、过期、重复或低可信内容的比例。
  - Output Traceability Rate / 输出可追溯率: Share of final outputs that can trace to used memory, evidence, and write decisions. / 最终输出能追溯到使用记忆、证据和写入决策的比例。
- 时延指标 / Latency Metrics:
  - Layer Decision Latency / 分层判定时延: Time from candidate collection to layer decision. / 从候选采集到层级判定的耗时。
  - Probe Completion Latency / 探针补全时延: Time from node event to probe result or completion package. / 从节点事件到探针结果或补全包的耗时。
  - Write Routing Latency / 写入路由时延: Time from state-change candidate to write decision. / 从状态变化候选到写入决策的耗时。
  - Human Review Queue Time / 人审排队时间: Time spent waiting for required review. / 必需人审等待时间。
  - Deferred Read Retrieval Latency / 延迟读取回溯时延: Time needed to retrieve referenced long content. / 读取延迟引用长内容所需时间。
- 成本指标 / Cost Metrics:
  - Context Budget Usage Rate / 上下文预算使用率: Used context divided by available budget. / 已用上下文占可用预算比例。
  - Avoided History Load Cost / 避免全量历史加载成本: Estimated context saved by summaries and references. / 通过摘要和引用节省的上下文成本。
  - Probe Processing Cost / 探针处理成本: Tool, compute, or token cost of probe analysis. / 探针分析消耗的工具、计算或 Token 成本。
  - Review Effort / 复核投入: Human or automated review effort per durable write. / 每次长期写入的人审或自动复核投入。
  - Cleanup Cost / 清理成本: Cost to demote, archive, delete, or migrate stale memory. / 降权、归档、删除或迁移陈旧记忆的成本。
- 风险指标 / Risk Metrics:
  - Low-to-High Override Attempt Count / 低层覆盖高层尝试数: Count of blocked lower-layer override attempts. / 被阻断的低层覆盖高层尝试数量。
  - Cross-Tenant Contamination Count / 跨租户污染数: Count of detected tenant-boundary violations. / 发现的租户边界违规数量。
  - Draft Leakage Count / 草稿泄漏次数: Count of unverified draft items attempting durable writes. / 未验证草稿尝试长期写入的次数。
  - Evidence-Free Promotion Count / 无证据升层数: Count of promotion attempts without sufficient evidence. / 缺少充分证据的升层尝试数量。
  - Stale Memory Recall Rate / 过期记忆召回率: Share of recalled memory that is expired or stale. / 被召回记忆中过期或陈旧的比例。
  - Human Review Miss Count / 人审漏检数: Count of high-risk actions or writes that bypassed required review. / 高风险动作或写入绕过必要人审的数量。
- Trace 指标 / Trace Metrics:
  - Write Decision Trace Coverage / 写入决策追踪覆盖率: Share of write decisions with reason and evidence references. / 具备原因和证据引用的写入决策比例。
  - Lifecycle Action Trace Coverage / 生命周期动作追踪覆盖率: Share of lifecycle actions with trigger and audit reference. / 具备触发条件和审计引用的生命周期动作比例。
  - Conflict Handling Trace Coverage / 冲突处理追踪覆盖率: Share of conflicts with recorded handling result. / 有处理结果记录的冲突比例。
  - Probe Feedback Closure Rate / 探针反馈闭环率: Share of probe recommendations resolved or explicitly rejected. / 探针建议被解决或明确拒绝的比例。
  - Completion Package Adoption Rate / 补全包采纳率: Share of useful probe completion packages adopted by the flow. / 被流程采纳的有效补全包比例。

## Metric System / 指标体系

| Family / 类别 | Core Metrics / 核心指标 | Purpose / 用途 |
|---|---|---|
| Classification Quality / 分层质量 | Layer Assignment Coverage / 层级判定覆盖率; Layer Assignment Accuracy / 层级判定准确率; Unknown Layer Rate / 未知层级率. | Check whether every candidate is classified correctly. / 检查每个候选是否被正确分层。 |
| Evidence And Write Safety / 证据与写入安全 | Durable Write Evidence Coverage / 长期写入证据覆盖率; Evidence-Free Promotion Count / 无证据升层数; Draft Leakage Count / 草稿泄漏次数; Write Rejection Correctness / 写入拒绝正确率. | Protect long-term memory from unverified content. / 防止未验证内容进入长期记忆。 |
| Coverage Governance / 覆盖治理 | Low-to-High Override Attempt Count / 低层覆盖高层尝试数; Policy Conflict Block Rate / 策略冲突阻断率; Cross-Tenant Contamination Count / 跨租户污染数; Human Review Miss Count / 人审漏检数. | Prevent lower-layer pollution and permission boundary failures. / 防止低层污染和权限边界失败。 |
| Context Assembly / 上下文装配 | Context Budget Usage Rate / 上下文预算使用率; Context Hit Rate / 关键记忆命中率; Context Noise Ratio / 上下文噪声占比; Deferred Read Health / 延迟读取健康度. | Keep working context lean and executable. / 保持工作上下文精简且可执行。 |
| Lifecycle Health / 生命周期健康 | Stale Memory Recall Rate / 过期记忆召回率; Review Overdue Count / 超期复核数; Demotion And Cleanup Rate / 降权清理率; Duplicate Memory Count / 重复记忆数量. | Keep retained memory fresh and governed. / 保持保留记忆新鲜且受治理。 |
| Trace And Audit / 追踪与审计 | Write Decision Trace Coverage / 写入决策追踪覆盖率; Lifecycle Action Trace Coverage / 生命周期动作追踪覆盖率; Probe Feedback Closure Rate / 探针反馈闭环率; Output Traceability Rate / 输出可追溯率. | Support replay, audit, and rule improvement. / 支持回放、审计和规则改进。 |

## Health State / 健康状态判断

| State / 状态 | Conditions / 条件 | Required Action / 必需动作 |
|---|---|---|
| healthy / 健康 | Required candidates classified, durable writes have evidence, no unresolved override risk. / 必需候选已分层、长期写入有证据、无未解决覆盖风险。 | Continue and record trace. / 继续并记录轨迹。 |
| warning / 警告 | Some candidates lack evidence, context budget is high, or stale memory appears. / 部分候选缺证据、上下文预算偏高或出现陈旧记忆。 | Repair evidence, demote, summarize, or attach deferred reads. / 修复证据、降权、摘要或挂延迟读取。 |
| unsafe / 不安全 | Durable write lacks evidence, lower-layer override is attempted, or tenant boundary is unclear. / 长期写入缺证据、低层尝试覆盖高层或租户边界不清。 | Block write and request repair or review. / 阻断写入并请求修复或人审。 |
| blocked / 已阻断 | Policy, permission, production, billing, sensitive data, or cross-tenant conflict requires stop. / 策略、权限、生产、账单、敏感数据或跨租户冲突要求停止。 | Stop action and emit governance event. / 停止动作并发出治理事件。 |

## Diagnostic Rules / 诊断规则

- If scenario, goal, permission, or key constraints are missing, switch to low-risk mode and request completion. / 场景、目标、权限或关键约束缺失时，切换低风险模式并请求补全。
- If policy boundary is missing for a high-risk action, block the action and request policy context. / 高风险动作缺少策略边界时阻断动作并请求策略上下文。
- If a durable write has no evidence, mark unsafe and request evidence. / 长期写入无证据时标记不安全并请求证据。
- If a draft item writes directly to user, project, or policy layer, block and demote. / 草稿项直接写入用户、项目或策略层时阻断并降权。
- If a user preference conflicts with policy, policy wins and preference stays scoped to the current task if allowed. / 用户偏好冲突策略时策略胜出，偏好如允许则仅限当前任务。
- If a tool result conflicts with project rules, keep it in draft until reproduced or confirmed. / 工具结果冲突项目规则时，先保留在草稿层，等待复现或确认。
- If stale memory is recalled, lower confidence and create a review event. / 过期记忆被召回时降低置信度并创建复核事件。
- If full history is loaded while a summary and references exist, flag context assembly waste. / 已有摘要和引用却加载全量历史时，标记上下文装配浪费。
- If final output cannot trace to used memory or evidence, request traceability completion. / 最终输出无法追溯到使用记忆或证据时，请求可追溯补全。

## Feedback Writeback Rules / 反馈回填规则

Immediate writeback / 即时回填:

- Blocked override attempts. / 被阻断的覆盖尝试。
- Cross-tenant contamination alerts. / 跨租户污染告警。
- Human review requirements. / 人审要求。
- Missing evidence for a requested durable write. / 长期写入所需证据缺口。
- Checkpoint freshness risk. / 检查点新鲜度风险。

Next-run writeback / 下一轮回填:

- Updated classification thresholds. / 更新后的分层阈值。
- Better context assembly priorities. / 更好的上下文装配优先级。
- Demotion or expiry candidates. / 降权或过期候选。
- Probe recommendation closure status. / 探针建议闭环状态。

Batch writeback / 批量回填:

- Lifecycle cleanup results. / 生命周期清理结果。
- Replay evaluation summaries. / 回放评估摘要。
- Rule calibration and metric baselines. / 规则校准和指标基线。

Do not directly override policy or permission rules from probe feedback. / 不得用探针反馈直接覆盖策略或权限规则。

## Scenario Thresholds / 场景化阈值建议

### Personal Assistant / 个人助理

| Probe / 探针 | Threshold Advice / 阈值建议 |
|---|---|
| User preference promotion / 用户偏好升层 | At least one explicit confirmation, or three stable occurrences. / 至少一次明确确认，或三次稳定出现。 |
| Draft leakage / 草稿泄漏 | Block whenever draft enters durable layer. / 只要进入长期层即阻断。 |
| Expired preference / 过期偏好 | Review when unused for long or user expression changes. / 长期未使用或用户表达变化时复核。 |

### Coding Assistant / 编程助手

| Probe / 探针 | Threshold Advice / 阈值建议 |
|---|---|
| Project rule write / 项目规则写入 | Require file, test, review, or maintainer confirmation. / 必须有文件、测试、评审或维护者确认。 |
| Tool result validation / 工具结果验证 | Failure result must preserve input, command, and output summary. / 失败结果必须保留输入、命令、输出摘要。 |
| Debug config write / 调试配置写入 | Default route is task layer or draft layer only. / 默认只能进任务层或草稿层。 |

### Enterprise Knowledge Assistant / 企业知识助手

| Probe / 探针 | Threshold Advice / 阈值建议 |
|---|---|
| Cross-tenant isolation / 跨租户隔离 | Block immediately once matched. / 一旦命中立即阻断。 |
| Policy override / 策略覆盖 | Block and audit immediately once matched. / 一旦命中立即阻断并审计。 |
| Expired policy reuse / 过期政策复用 | Mark risk and require review. / 标记风险，要求复核。 |

### Course Coach / 课程教练

| Probe / 探针 | Threshold Advice / 阈值建议 |
|---|---|
| Mastery promotion / 掌握度升层 | Require exercise, quiz, repeated correct explanation, or user confirmation. / 需要练习、测验、连续正确解释或用户确认。 |
| Emotional state write / 情绪状态写入 | Default route is session layer, not user layer. / 默认只进会话层，不进用户层。 |
| Learning weakness record / 学习弱点记录 | Require repeated evidence or explicit assignment result. / 需要多次证据或明确作业结果。 |

### Support Assistant / 客服助手

| Probe / 探针 | Threshold Advice / 阈值建议 |
|---|---|
| Discount rule write / 折扣规则写入 | Must come from business system or approval. / 必须来自业务系统或审批。 |
| Ticket state / 工单状态 | Must reference ticket-system state. / 必须引用工单系统状态。 |
| Complaint attribution / 用户投诉归因 | Default route is task layer; promote after retrospective. / 默认写任务层，复盘后再沉淀经验。 |

### Approval Assistant / 审批助手

| Probe / 探针 | Threshold Advice / 阈值建议 |
|---|---|
| High-risk action / 高风险动作 | Human review is required. / 必须人审。 |
| Critical state writeback / 关键状态写回 | Write back in real time; do not wait for task end. / 实时写回，不等待任务结束。 |
| Audit completeness / 审计完整性 | Block when audit fields are missing. / 缺失审计字段即阻断。 |

## Aggregated Views / 聚合视图

### Workflow Health View / 流程健康视图

```yaml
Workflow Health / 流程健康:
  total_requests / 请求总数: number / 数值
  normal_completion / 正常完成: number / 数值
  blocked / 被阻断: number / 数值
  human_review / 进入人审: number / 数值
  degraded / 发生降级: number / 数值
  state_recovery_failed / 状态恢复失败: number / 数值
```

### Memory Health View / 记忆健康视图

```yaml
Memory Health / 记忆健康:
  memory_count_by_layer / 各层记忆数量: {}
  evidence_free_durable_memory_count / 无证据长期记忆数量: number / 数值
  expired_memory_count / 过期记忆数量: number / 数值
  duplicate_memory_count / 重复记忆数量: number / 数值
  draft_leakage_count / 草稿泄漏次数: number / 数值
  low_to_high_override_count / 低层覆盖高层次数: number / 数值
  cross_scope_contamination_count / 跨域污染次数: number / 数值
```

### Context Health View / 上下文健康视图

```yaml
Context Health / 上下文健康:
  key_memory_hit_rate / 关键记忆命中率: number / 数值
  noise_ratio / 噪声占比: number / 数值
  expired_memory_loaded_count / 过期记忆进入次数: number / 数值
  high_layer_memory_displaced_count / 高层记忆被挤出次数: number / 数值
  budget_overrun_count / 预算超限次数: number / 数值
  deferred_read_hit_count / 按需读取命中次数: number / 数值
```

## Alert Rules / 告警规则

Highest priority alerts / 最高优先级告警:

- Cross-Tenant Contamination Count / 跨租户污染数 > 0.
- Durable write targets policy, project, or user layer without evidence. / 长期写入目标为策略、项目或用户层但无证据。
- Lower-layer item attempts to override policy. / 低层信息试图覆盖策略层。
- High-risk action continues without required approval. / 高风险动作缺少必要审批仍继续。

Recommended alert rules / 推荐告警规则:

| Alert / 告警 | Trigger / 触发条件 | Level / 等级 | Suggested Handling / 建议处理 |
|---|---|---|---|
| Policy override alert / 策略覆盖告警 | Lower-layer content attempts to override policy layer. / 低层内容试图覆盖策略层。 | severe / 严重 | Block and audit. / 阻断并审计。 |
| Draft leakage alert / 草稿泄漏告警 | Unverified draft writes to durable layer. / 未验证草稿写入长期层。 | severe / 严重 | Roll back write and require evidence. / 回滚写入并要求证据。 |
| Cross-scope contamination alert / 跨域污染告警 | User, tenant, or project memory is mixed. / 不同用户、租户、项目记忆串用。 | severe / 严重 | Block, isolate, and clean. / 阻断、隔离、清理。 |
| Evidence-free promotion alert / 无证据升层告警 | Durable-layer write lacks evidence. / 长期层写入缺少证据。 | high / 高 | Demote to candidate or request review. / 降为候选或人审。 |
| Context noise alert / 上下文噪声告警 | Irrelevant history uses too much budget. / 无关历史占用预算过高。 | medium / 中 | Compress, remove, or convert to references. / 压缩、移除或引用化。 |
| Expired memory alert / 过期记忆告警 | Expired rule is still used. / 过期规则仍被使用。 | high / 高 | Demote, review, or delete. / 降权、复核或删除。 |
| Checkpoint lag alert / 检查点滞后告警 | Long-running critical state is not written back. / 长程任务关键状态未写回。 | high / 高 | Write back immediately. / 立即写回。 |
| Structure missing alert / 结构化缺失告警 | Durable layer lacks source, evidence, or expiry. / 长期层缺少来源、证据、有效期。 | medium / 中 | Complete structure or reject write. / 补全结构或拒写。 |

Trend alerts / 趋势观察告警:

- Evidence-Free Promotion Count / 无证据升层数 is increasing.
- Full-history loading recurs across tasks. / 全量历史加载跨任务重复出现。
- Write rejection reasons repeat without rule improvement. / 写入拒绝原因重复但规则未改进。
- Probe Feedback Closure Rate / 探针反馈闭环率 falls below threshold.

## How Probe Results Complete Execution Data / 探针结果如何补全执行流程数据

### Complete Layer Data / 补全层级数据

```yaml
Completion Type / 补全类型: layer_correction / 层级修正
Completion Content / 补全内容:
  original_layer / 原层级: user_layer / 用户层
  suggested_layer / 建议层级: task_layer / 任务层
  reason / 原因: current information only reflects this task state and does not represent durable preference / 当前信息只反映本次任务状态，不代表长期偏好
```

### Complete Evidence Data / 补全证据数据

```yaml
Completion Type / 补全类型: evidence_completion / 证据补充
Completion Content / 补全内容:
  missing_evidence / 缺失证据:
    - user_confirmation / 用户确认
    - tool_result_ref / 工具结果引用
    - test_log / 测试日志
  recommended_actions / 建议动作:
    - do_not_promote_yet / 暂不升层
    - keep_as_task_layer_candidate / 保留为任务层候选
```

### Complete Context Data / 补全上下文数据

```yaml
Completion Type / 补全类型: context_completion / 上下文补充
Completion Content / 补全内容:
  suggested_memory_additions / 建议补入记忆:
    - policy_layer_safety_boundary_summary / 策略层安全边界摘要
    - project_layer_current_test_command / 项目层当前测试命令
  suggested_memory_removals / 建议移除记忆:
    - expired_task_summary / 过期任务摘要
    - irrelevant_user_preference / 无关用户偏好
```

### Complete Risk Data / 补全风险数据

```yaml
Completion Type / 补全类型: risk_block / 风险阻断
Advice Level / 建议等级: block / 阻断
Completion Content / 补全内容:
  blocked_actions / 阻断动作:
    - stop_user_layer_write / 停止写入用户层
    - stop_external_tool_call / 停止调用外发工具
  audit_fields / 审计字段:
    - request_id / 请求编号
    - user_id / 用户编号
    - matched_policy / 命中策略
```

### Complete Lifecycle Data / 补全生命周期数据

```yaml
Completion Type / 补全类型: lifecycle_correction / 生命周期修正
Completion Content / 补全内容:
  suggested_action / 建议动作: demote / 降权
  target_memory / 目标记忆: project_layer.test_command.old_version / 项目层.测试命令.旧版本
  reason / 原因: conflicts with new project document / 与新项目文档冲突
  follow_up / 后续动作: enter review queue / 进入复核队列
```

## Minimum Probe Set / 最小可执行探针集

| Priority / 优先级 | Probe / 探针 | Reason / 原因 |
|---|---|---|
| Required / 必须 | Policy Boundary Probe / 策略边界探针 | Prevent permission overreach and safety-boundary override. / 防止越权和安全边界被覆盖。 |
| Required / 必须 | Layer Decision Probe / 层级判定探针 | Prevent memory layer confusion. / 防止记忆混层。 |
| Required / 必须 | Evidence Sufficiency Probe / 证据充分性探针 | Prevent evidence-free durable writes. / 防止无证据长期写入。 |
| Required / 必须 | Draft Leakage Probe / 草稿泄漏探针 | Prevent half-finished material from entering durable layers. / 防止半成品进入长期层。 |
| Recommended / 推荐 | Context Hit Probe / 上下文命中探针 | Ensure required memory enters context. / 保证该用的记忆进入上下文。 |
| Recommended / 推荐 | Expiry And Demotion Probe / 过期与降权探针 | Prevent stale memory from polluting new judgments. / 防止旧记忆污染新判断。 |

## Minimum Standalone Run / 独立运行最小流程

Minimum capabilities / 最小能力:

- Event capture / 事件采集
- Candidate collection / 候选采集
- Layer assignment coverage check / 层级判定覆盖检查
- Durable-write evidence check / 长期写入证据检查
- Draft leakage check / 草稿泄漏检查
- Conflict and override check / 冲突与覆盖检查
- Context hit, noise, and budget check / 上下文命中、噪声和预算检查
- Write decision trace check / 写入决策追踪检查
- Lifecycle action check / 生命周期动作检查
- Probe report generation / 探针报告生成

Minimum flow / 最小流程:

```text
Collect retention candidates / 采集保留候选
  -> Check layer assignment / 检查层级判定
  -> Check evidence and source / 检查证据和来源
  -> Check draft leakage / 检查草稿泄漏
  -> Check conflict and coverage / 检查冲突和覆盖
  -> Check context assembly / 检查上下文装配
  -> Check write route / 检查写入路由
  -> Check lifecycle actions / 检查生命周期动作
  -> Emit report or guard decision / 输出报告或守卫决策
```

Minimum gate / 最小门禁:

- Every durable write has source, evidence, scope, lifecycle, and route. / 每个长期写入都有来源、证据、作用域、生命周期和路由。
- No lower-layer item writes over a higher-layer fact. / 没有低层信息覆盖高层事实。
- High-risk writes are blocked or reviewed. / 高风险写入被阻断或人审。
- Context package keeps required policy, project rules, task goal, and current material. / 上下文包保留必要策略、项目规则、任务目标和当前轮材料。
- Write decision reason is recorded. / 写入决策原因已记录。

## Probe Configuration Template / 探针配置模板

```yaml
Probe Configuration / 探针配置:
  scenario_type / 场景类型: enterprise_knowledge_assistant / 企业知识助手
  enabled_probes / 启用探针:
    - Probe 001 / 探针_001
    - Probe 002 / 探针_002
    - Probe 003 / 探针_003
    - Probe 004 / 探针_004
    - Probe 005 / 探针_005
    - Probe 006 / 探针_006
    - Probe 007 / 探针_007
    - Probe 008 / 探针_008
    - Probe 010 / 探针_010
    - Probe 014 / 探针_014
    - Probe 017 / 探针_017
  thresholds / 阈值:
    durable_layer_minimum_evidence_count / 长期层最低证据数: 1
    user_preference_minimum_occurrences_for_promotion / 用户偏好升层最少出现次数: 3
    context_noise_ratio_limit / 上下文噪声占比上限: 0.25
    checkpoint_max_lag_turns / 检查点最大滞后轮次: 2
  blocking_rules / 阻断规则:
    - policy_override / 策略覆盖
    - cross_tenant_contamination / 跨租户污染
    - draft_write_to_durable_layer / 草稿写入长期层
    - high_risk_action_without_approval / 高风险动作未审批
  feedback_strategy / 回填策略:
    hint / 提示: record / 记录
    suggestion / 建议: auto_adopt / 自动采纳
    risk / 风险: degrade_execution / 降级执行
    block / 阻断: stop_action / 停止动作
    human_review / 人审: request_human_confirmation / 转人工确认
```

## Output Templates / 输出模板

Observation report / 观测报告:

```yaml
Observation Report / 观测报告:
  report_id / 报告编号: ""
  request_id / 请求编号: ""
  health_state / 健康状态: ""
  summary / 摘要: ""
  findings / 发现:
    - type / 类型: ""
      severity / 严重级别: ""
      node / 节点: ""
      evidence_refs / 证据引用: []
      recommendation / 建议: ""
  metric_snapshot_ref / 指标快照引用: ""
  audit_refs / 审计引用: []
```

Retention guard decision / 保留守卫决策:

```yaml
Retention Guard Decision / 保留守卫决策:
  decision_id / 决策编号: ""
  candidate_id / 候选编号: ""
  decision / 决策: block
  reason / 原因: durable write lacks evidence / 长期写入缺少证据
  required_action / 必需动作: provide evidence or keep in draft layer / 补充证据或保留在草稿层
  review_required / 是否需要人审: false
```

Full probe report / 探针输出报告:

```yaml
Probe Report / 探针报告:
  report_id / 报告编号: report_0001 / 报告_0001
  time_range / 时间范围: current_request_or_period / 本次请求或指定周期
  scenario_type / 场景类型: required / 必填
  overall_conclusion / 总体结论: normal | needs_attention | high_risk | severe
  key_findings / 关键发现:
    - type / 类型: draft_leakage / 草稿泄漏
      level / 等级: severe / 严重
      affected_node / 影响节点: write_routing_node / 写入路由节点
      affected_layer / 影响层级: user_layer / 用户层
      evidence_refs / 证据引用: []
      recommended_action / 建议动作: rollback_write / 回滚写入
  flow_completion_packages / 流程补全包:
    - request_id / 请求编号: example_0001 / 示例_0001
      target_node / 目标节点: write_routing_node / 写入路由节点
      completion_type / 补全类型: write_correction / 写入修正
      advice_level / 建议等级: block / 阻断
  durable_governance_advice / 长期治理建议:
    - clean_expired_memory / 清理过期记忆
    - complete_evidence_fields / 补充证据字段
    - adjust_context_budget / 调整上下文预算
    - add_human_review_gate / 增加人审门禁
```

## Interaction Data Interface / 与执行流程交互的数据接口

Probe sends to execution flow / 探针向执行流程补全:

- Layer correction / 层级修正
- Evidence completion / 证据补充
- Context completion / 上下文补充
- Write route correction / 写入路由修正
- Conflict alert / 冲突告警
- Context budget finding / 上下文预算发现
- Lifecycle cleanup recommendation / 生命周期清理建议
- Human review requirement / 人审要求

Execution flow returns to probe / 执行流程向探针回传:

- Final layer decisions / 最终分层决策
- Accepted and rejected write decisions / 已接受和已拒绝的写入决策
- Context package / 上下文包
- Lifecycle actions / 生命周期动作
- Blocked actions / 被阻断动作
- Human review outcome / 人审结果
- Final result reference / 最终结果引用

Closed loop / 闭环:

```text
Probe checks / 探针检查
  -> Flow repairs or routes / 流程修复或路由
  -> Probe verifies trace / 探针验证轨迹
  -> Flow writes only safe state / 流程只写入安全状态
  -> Lifecycle monitor continues / 生命周期监控继续
```

## Failure Coverage / 失败模式与探针覆盖

| Failure Mode / 失败模式 | Covering Probes / 覆盖探针 |
|---|---|
| Full history loaded into context / 所有历史塞入上下文 | Context Noise Probe, Context Budget Probe / 上下文噪声探针、上下文预算探针 |
| Temporary judgment written to durable layer / 临时判断写入长期层 | Draft Leakage Probe, Evidence Sufficiency Probe / 草稿泄漏探针、证据充分性探针 |
| User preference overrides policy / 用户偏好覆盖策略 | Override Violation Probe, Policy Boundary Probe / 覆盖违规探针、策略边界探针 |
| Temporary project config pollutes project rules / 项目临时配置污染规范 | Layer Decision Probe, Evidence Sufficiency Probe / 层级判定探针、证据充分性探针 |
| Cross-tenant contamination / 跨租户污染 | Scope Isolation Probe / 作用域隔离探针 |
| Old memory remains active / 旧记忆继续生效 | Expiry And Demotion Probe / 过期与降权探针 |
| Long-running task loses state after interruption / 长程任务中断丢状态 | Checkpoint Freshness Probe / 检查点新鲜度探针 |
| Durable layer accumulates free text / 长期层自由文本堆积 | Structured Discipline Probe / 结构化纪律探针 |
| Final answer is not traceable / 最终答案不可追溯 | Output Traceability Probe / 输出可追溯探针 |

## Failure Modes / 常见失败模式

- Tracking write count but not evidence coverage. / 只跟踪写入数量，不跟踪证据覆盖。
- Measuring context length without checking layer priority. / 只看上下文长度，不检查层级优先级。
- Letting probe suggestions mutate policy directly. / 让探针建议直接修改策略。
- Treating every user statement as durable preference. / 把每个用户表达都当成长期偏好。
- Ignoring stale memory recall. / 忽略过期记忆召回。
- Blocking writes without recording rejection reasons. / 阻断写入但不记录拒绝原因。
- Running lifecycle cleanup without audit references. / 生命周期清理没有审计引用。
- Reporting metrics without feedback packages. / 只输出指标，不输出可回填补全包。
- Using one threshold set for all scenarios. / 所有场景使用同一套阈值。

## Skill Packaging Draft / 可包装技能草案

```yaml
Skill Draft / 技能草案:
  skill_id / 技能编号: SKILL_WORKFLOW_OBSERVABILITY_PROBE
  skill_name / 技能名称: Workflow Observability Probe / 工作流可观测性探针
  version / 版本: 0.1.0
  status / 状态: draft / 草稿
  related_patterns / 关联模式:
    - PATTERN_0022 / Layered Retention / 分层保留
  related_cognition / 关联认知:
    - COG_PERCEPTION
    - COG_MEMORY
    - COG_REFLECTION
    - COG_GOVERNANCE
  related_topology / 关联拓扑:
    - TOP_ROUTING
    - TOP_LOOP
    - TOP_ORCHESTRATION
    - TOP_HIERARCHY
  related_business_nodes / 关联业务节点:
    - NODE_OBSERVABILITY_EVENT_CAPTURE
    - NODE_OBSERVABILITY_PROBE_RUN
    - NODE_OBSERVABILITY_WORKFLOW_FEEDBACK
    - NODE_OBSERVABILITY_ALERT
    - NODE_OBSERVABILITY_REPORT
```

## Engineering Node Registration / 推荐工程节点注册项

```yaml
Business Nodes / 业务节点:
  - node_id / 节点编号: NODE_OBSERVABILITY_EVENT_CAPTURE
    node_name / 节点名称: observability_event_capture / 可观测事件采集
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_PERCEPTION, COG_GOVERNANCE]
    related_topology / 相关拓扑: [TOP_ROUTING]

  - node_id / 节点编号: NODE_OBSERVABILITY_PROBE_RUN
    node_name / 节点名称: probe_execution / 探针执行
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_REFLECTION, COG_GOVERNANCE]
    related_topology / 相关拓扑: [TOP_LOOP]

  - node_id / 节点编号: NODE_OBSERVABILITY_WORKFLOW_FEEDBACK
    node_name / 节点名称: workflow_completion_feedback / 工作流补全回填
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_MEMORY, COG_ACTION]
    related_topology / 相关拓扑: [TOP_ORCHESTRATION]

  - node_id / 节点编号: NODE_OBSERVABILITY_ALERT
    node_name / 节点名称: risk_alert_and_blocking / 风险告警与阻断
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_GOVERNANCE]
    related_topology / 相关拓扑: [TOP_ROUTING]

  - node_id / 节点编号: NODE_OBSERVABILITY_REPORT
    node_name / 节点名称: probe_report_generation / 探针报告生成
    status / 状态: draft / 草稿
    related_cognition / 相关认知: [COG_REFLECTION]
    related_topology / 相关拓扑: [TOP_CHAIN]
```

## Version Extension Suggestions / 版本扩展建议

Future versions can add / 后续版本可以继续补充:

1. Precise scoring formulas for each probe. / 每类探针的精确评分公式。
2. Default threshold packages for different scenarios. / 不同场景的默认阈值包。
3. Real-time communication protocol between probe results and the execution flow. / 探针结果与执行流程的实时通信协议。
4. Alert-level handling processes. / 探针告警的分级处置流程。
5. Dashboard templates for memory health, context health, and governance health. / 记忆健康、上下文健康、治理健康的仪表盘模板。
6. Closed-loop mechanism for probe results to improve layer rules. / 探针结果反向优化分层规则的闭环机制。

## Design Principles / 设计原则总结

- Probe observes, completes, guards, reviews, and tunes; it does not directly own durable memory. / 探针负责观察、补全、守门、复盘和调参，不直接拥有长期记忆。
- Every durable write needs source, evidence, scope, lifecycle, and route. / 每个长期写入都需要来源、证据、作用域、生命周期和路由。
- Lower layers can influence execution, but cannot rewrite higher-layer facts. / 低层可以影响执行，但不能改写高层事实。
- Probe outputs should feed back into the execution flow whenever possible. / 探针输出应尽量可回填执行流程。
- Context assembly is part of retention governance. / 上下文装配是保留治理的一部分。
- Lifecycle health matters as much as write safety. / 生命周期健康与写入安全同等重要。
- Human review is required for policy, permission, production, billing, or sensitive information. / 涉及策略、权限、生产、账单或敏感信息时必须人审。
- Metrics do not replace judgment; they create auditable evidence for correction. / 指标不替代判断，而是为修正提供可审计证据。
