# Context Triage / 上下文分诊

Cell / 交织点: perception-routing / 感知 x 路由
Capability / 能力: Perception / 感知
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Alias / 别名: Context Priority Triage / 上下文优先级分诊
Standalone Executable / 可独立执行: Yes / 是
Interactive Object / 可交互对象: Context Triage Workflow Observability Probe / 上下文分诊的工作流可观测性探针

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Context Priority Triage / 上下文优先级分诊 places a routing gate in front of an agent workflow. It decides what the agent must see now, what can be summarized, what can be deferred as a read handle, and what must be rejected before the main reasoning path begins. / 上下文优先级分诊在智能体工作流入口前放置一个路由门，先判断什么必须现在进入上下文、什么可以摘要进入、什么只能作为延迟读取入口、什么必须拒绝，再把结果交给主推理路径。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Perception / 感知 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Perception / 感知 x Routing / 路由 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Perception / 感知 x Routing / 路由 映射到该单元。
- 问题 / Problem: Incoming signals differ by intent, modality, risk, and reliability, so one processing path wastes effort or misreads context. / 输入信号在意图、模态、风险和可靠性上不同，单一路径会浪费成本或误读上下文。
- 架构方案 / Architectural Solution: Place a triage step in front of the workflow to classify context and route it to the right tool, skill, owner, or depth of analysis. / 在工作流前放置分诊步骤，对上下文分类并路由到合适的工具、技能、负责人或分析深度。
- 工程权衡 / Engineering Trade-offs: Fast specialization and lower cost, but routing mistakes can send work to the wrong path and require fallback handling. / 能快速专门化并降低成本，但路由错误会把工作送到错误路径，需要回退处理。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when incoming context must be classified before choosing a path. / 当输入上下文必须先分类再选路径时使用。

### Execution Contract / 执行契约

- Trigger / 触发条件: Run before a workflow consumes large, mixed, risky, or multi-source context. / 当工作流即将消费大量、混合、高风险或多来源上下文时，在主流程前执行。
- Objective / 目标: In a limited context budget, make the agent see the information most needed for the next reasoning step. / 在有限上下文预算内，让智能体优先看到下一步推理最需要的信息。
- Scope / 范围: collect candidate information / 收集候选信息; annotate information attributes / 标注信息属性; judge information priority / 判断信息优先级; control context budget / 控制上下文预算; compress medium-priority information / 压缩中等优先信息; mount deferred read handles / 挂载延迟读取入口; build a context package / 生成上下文包; record triage decisions / 记录分诊决策。
- Owner / 责任方: The workflow intake, context builder, or orchestration layer that decides what enters the model context. / 负责上下文入口的工作流入口、上下文构建器或编排层。
- Stop Condition / 停止条件: Stop if L0 constraints are missing, permission scope is unclear, or L0 alone exceeds the available budget. / 当零级约束缺失、权限范围不清或零级信息本身超过可用预算时阻断。
- Output / 输出: Context Triage Result / 上下文分诊结果 plus Triage Decision Record / 分诊决策记录.

### Core Layering Rules / 核心分层规则

The classification criterion is not whether information is useful, but how urgent it is for the current step. / 分层标准不是“有没有用”，而是“当前这一步有多急”。

| Layer / 层级 | Handling / 处理方式 | Typical Items / 典型内容 |
|---|---|---|
| L0 Non-Droppable Layer / 零级不可丢失层 | Must enter context; block if missing. / 必须进入上下文，缺失时阻断。 | Current request, safety rules, identity, permission, data scope, task goal. / 当前请求、安全规则、身份、权限、数据范围、任务目标。 |
| L1 Current Work Layer / 一级当前工作层 | Prefer raw evidence or key excerpts. / 优先保留原文证据或关键片段。 | Failure tests, error stack, current ticket, current file, key evidence. / 失败测试、错误堆栈、当前工单、当前文件、关键证据。 |
| L2 Background Support Layer / 二级背景支持层 | Compress before entering context. / 压缩后进入上下文。 | History, background documents, old tool results, trends, related material. / 历史对话、背景文档、旧工具结果、趋势、相关材料。 |
| L3 Deferred Read Layer / 三级延迟读取层 | Do not expand; keep scoped read handles. / 不展开，只保留带作用域的读取入口。 | Full repo, full logs, full knowledge base, complete document corpus. / 全仓库、全量日志、完整知识库、全文档库。 |
| Reject or Drop / 拒绝或丢弃 | Reject unsafe or out-of-scope data; drop duplicates or invalid data with reason. / 拒绝越权或不在范围内的数据，带原因丢弃重复或无效数据。 | Cross-tenant data, stale duplicates, polluted retrieval results. / 跨租户数据、过期重复项、污染检索结果。 |

### Input Contract / 输入契约

Required inputs / 必需输入:

```yaml
task_request:
  task_id: ""
  task_type: ""
  current_user_message: ""
  current_goal: ""
  constraints: []
  expected_output: ""
runtime_context:
  user_id: ""
  session_id: ""
  project_id: ""
  tenant_id: ""
  workspace_id: ""
  tool_permissions: []
  data_scope: ""
  audit_required: false
candidate_items:
  - item_id: ""
    name: ""
    source_type: ""
    raw_content: ""
    read_handle: ""
    estimated_tokens: 0
    priority_hint: ""
    user_id: ""
    tenant_id: ""
    project_id: ""
    confidence: ""
    is_error_evidence: false
    is_safety_boundary: false
    source_reliability: ""
    retrieval_score: 0
    dependency_score: 0
triage_policy:
  total_context_budget: 0
  output_reserved_budget: 0
  l0_protection_rules: []
  l1_selection_rules: []
  l2_compression_rules: []
  l3_handle_rules: []
  permission_rules: []
probe_feedback:
  high_risk_missing_items: []
  priority_up_items: []
  priority_down_items: []
  compression_advice: []
  read_handle_health: []
```

Minimum rule / 最小规则: each candidate item must have raw content or a read handle. / 每个候选信息项必须至少有原文内容或读取入口之一。

### Execution Procedure / 执行流程

1. Build the scene profile / 建立场景画像: identify task type, external knowledge, tools, files, permission boundary, evidence requirement, audit requirement, compression allowance, and deferred-read allowance. / 识别任务类型、外部知识、工具、文件、权限边界、证据要求、审计要求、压缩许可和延迟读取许可。
2. Collect candidate information / 收集候选信息: gather current request, system constraints, history, memory, tool results, retrieval results, files, logs, data schema, attachments, and manual rules. / 收集当前请求、系统约束、历史、记忆、工具结果、检索结果、文件、日志、数据结构、附件和人工规则。
3. Annotate information attributes / 标注信息属性: normalize source, scope, estimated length, read handle, error evidence flag, safety boundary flag, direct relevance, compressibility, and deferrability. / 规范化来源、范围、长度估算、读取入口、错误证据标记、安全边界标记、直接相关性、可压缩性和可延迟读取性。
4. Check scope and permissions / 检查范围与权限: reject cross-user, cross-tenant, cross-project, or unauthorized reads before relevance ranking. / 在相关性排序前拒绝跨用户、跨租户、跨项目或未授权读取。
5. Lock L0 information / 锁定零级信息: protect current request, task goal, system safety rules, identity, permission boundary, data scope, output requirements, and session state. / 保护当前请求、任务目标、系统安全规则、身份、权限边界、数据范围、输出要求和会话状态。
6. Score relevance and urgency / 计算相关性与急迫度: combine direct relevance, evidence strength, freshness, reliability, dependency strength, error feedback, safety weight, explicit user instruction, history, and probe feedback. / 综合直接相关性、证据强度、新鲜度、可靠度、依赖强度、错误反馈、安全权重、用户显式指定、历史命中和探针反馈。
7. Judge information priority / 判断信息优先级: assign L0, L1, L2, L3, reject, or drop according to the layer rules. / 根据分层规则分配零级、一级、二级、三级、拒绝或丢弃。
8. Resolve duplication and conflict / 去重与冲突处理: keep the newest or most reliable duplicate; preserve conflicting sources and evidence instead of silently merging them. / 重复信息保留最新或最可靠版本，冲突信息保留来源和证据，不静默合并。
9. Control context budget / 控制上下文预算: reserve output budget, then assemble L0, L1, L2 summaries, and L3 read handles in that order. / 先预留输出预算，再按零级、一级、二级摘要、三级读取入口顺序装配。
10. Compress medium-priority information / 压缩中等优先信息: generate compression tasks that preserve conclusion, evidence, and source index. / 为二级信息生成压缩任务，必须保留结论、证据和来源索引。
11. Mount deferred read handles / 挂载延迟读取入口: keep scope, resource type, location, permission requirement, expected use, estimated latency, and estimated cost. / 保留作用域、资源类型、位置、权限要求、预计用途、预计时延和预计成本。
12. Build a context package / 生成上下文包: order content as task goal, safety and runtime boundary, current evidence, compressed background, deferred handles, risks, and verification needs. / 按任务目标、安全和运行边界、当前证据、压缩背景、延迟入口、风险和待验证事项组装。
13. Record triage decisions / 记录分诊决策: record original layer, final layer, action, reason, estimated length, actual usage, compression, mounted handle, rejection, probe hit, and permission impact for each item. / 逐项记录原始层级、最终层级、处理动作、原因、长度估算、实际占用、是否压缩、是否挂载、是否拒绝、是否命中探针反馈和权限影响。
14. Output to the main workflow / 输出给主工作流: send context package, decision record, compression tasks, read handle list, risk notes, and probe-readable events. / 输出上下文包、分诊决策记录、压缩任务、读取入口清单、风险提示和探针可读事件。
15. Receive probe feedback / 接收探针反馈: use observations to tune the next round of priority, compression strength, handle exposure, scene profile, and governance rules. / 使用观测结果修正下一轮优先级、压缩强度、读取入口暴露、场景画像和治理规则。

### Priority Triage Rules / 优先级分诊规则

- L0 / 零级: classify as L0 if absence causes safety violation, permission ambiguity, task-goal loss, audit breakage, or wrong user/project/tenant scope. / 如果缺失会造成安全违规、权限不清、任务目标丢失、审计断裂或用户、项目、租户范围错误，分为零级。
- L1 / 一级: classify as L1 if the current reasoning step directly depends on the evidence and quality would clearly degrade without it. / 如果当前推理直接依赖该证据，缺失会明显降低质量，分为一级。
- L2 / 二级: classify as L2 if the item helps interpretation but raw content is not needed now. / 如果该信息有助于理解但当前不需要原文，分为二级。
- L3 / 三级: classify as L3 if the item may become useful later and can be safely retrieved through a scoped handle. / 如果该信息以后可能有用，且能通过带作用域的入口安全读取，分为三级。
- Reject / 拒绝: reject items that cross user, tenant, project, tool, or data-scope boundaries. / 拒绝跨用户、租户、项目、工具或数据范围的信息。
- Drop / 丢弃: drop duplicated, invalid, expired, or unparseable items only with a recorded reason. / 仅在记录原因后丢弃重复、无效、过期或不可解析的信息。
- Conservative fallback / 保守回退: when scene profile is uncertain, raise current request, hard constraints, error evidence, and permission fields one level. / 场景画像不确定时，将当前请求、硬约束、错误证据和权限字段提升一级。

### Context Budget Assembly / 上下文预算装配

Budget order / 预算顺序:

```text
1. Reserve output budget / 预留输出预算
2. Insert L0 / 放入零级
3. Insert L1 raw evidence or excerpts / 放入一级原文证据或片段
4. Insert L2 compressed summaries / 放入二级压缩摘要
5. Insert L3 read handles / 放入三级读取入口
6. Attach risks and unresolved conflicts / 附加风险和未解决冲突
```

Budget rules / 预算规则:

- L0 cannot be removed by normal budget pressure. / 零级不能被普通预算压力移除。
- If L0 alone exceeds budget, block and ask the upstream workflow to reduce or clarify L0 rules. / 如果零级本身超过预算，阻断并要求上游缩减或澄清零级规则。
- L1 should keep raw evidence or minimal excerpts before L2 grows. / 一级应优先保留原文证据或最小片段，再扩大二级。
- L2 compression must preserve conclusion, evidence, and source index. / 二级压缩必须保留结论、证据和来源索引。
- L3 handles must include scope, permission, expected use, estimated latency, and stable location. / 三级读取入口必须包含作用域、权限、预计用途、预计时延和稳定位置。

### Output Schema / 输出结构

```yaml
Context Triage Result / 上下文分诊结果:
  task_id / 任务标识: ""
  scene_type / 场景类型: ""
  policy_version / 策略版本: ""
  total_budget / 总预算: 0
  used_budget / 已使用预算: 0
  l0_context / 零级上下文:
    - name / 名称: ""
      reason / 原因: ""
  l1_context / 一级上下文:
    - name / 名称: ""
      evidence / 证据: ""
      reason / 原因: ""
  l2_summaries / 二级摘要:
    - name / 名称: ""
      conclusion / 结论: ""
      evidence / 证据: ""
      source_index / 来源索引: ""
  l3_read_handles / 三级读取入口:
    - name / 名称: ""
      read_handle / 读取入口: ""
      scope / 作用域: ""
      intended_use / 用途: ""
  rejected_items / 被拒绝信息:
    - name / 名称: ""
      reason / 原因: ""
  dropped_items / 被丢弃信息:
    - name / 名称: ""
      reason / 原因: ""
  risks / 风险提示:
    - risk / 风险: ""
      level / 等级: ""
      recommendation / 建议: ""
Triage Decision Record / 分诊决策记录:
  record_id / 记录标识: ""
  item_decisions / 信息项处理决定:
    - item_id / 信息标识: ""
      original_layer / 原始层级: ""
      final_layer / 最终层级: ""
      action / 处理决定: enter_context | compress | defer_read | reject | drop | block
      reason / 处理原因: ""
      estimated_tokens / 估算长度: 0
      actual_tokens / 实际占用: 0
      compressed / 是否压缩: false
      mounted / 是否挂载: false
      rejected / 是否拒绝: false
      probe_feedback_hit / 是否命中探针反馈: false
      permission_related / 是否涉及权限: false
```

### Observability Probe Interaction / 可观测性探针交互

When a probe exists, send candidate list, triage decisions, context package, compression tasks, compression results, read handle list, read handle usage, and final task result. / 当存在探针时，向探针发送候选信息清单、分诊决策、上下文包、压缩任务、压缩结果、读取入口清单、读取入口使用记录和最终任务结果。

Accept probe feedback as strategy input, not as an unchecked override of L0 or permission rules. / 探针反馈只能作为策略输入，不能无审查覆盖零级或权限规则。

Probe feedback can adjust / 探针反馈可以调整:

- priority promotion or demotion / 优先级提升或降低
- compression strength / 压缩强度
- read handle exposure count / 读取入口暴露数量
- scene profile / 场景画像
- candidate recall scope / 候选召回范围
- permission and governance strictness / 权限与治理强度

### Failure Handling / 失败处理

| Failure / 失败类型 | Handling / 处理方式 |
|---|---|
| Missing L0 / 零级缺失 | Block and return risk note. / 阻断并返回风险提示。 |
| Ambiguous permission scope / 权限范围不明 | Block or enter safe mode. / 阻断或进入安全模式。 |
| Insufficient budget / 预算不足 | Keep L0, compress L1 edge material, reduce L2 and L3 descriptions. / 保留零级，压缩一级边缘材料，减少二级和三级说明。 |
| Compression failure / 压缩失败 | Keep scoped read handle, mark uncompressed, do not silently drop. / 保留带作用域读取入口，标记未压缩，不静默丢弃。 |
| Invalid read handle / 读取入口失效 | Remove from package and send repair event to probe. / 从上下文包移除，并向探针发送修复事件。 |
| Candidate conflict / 候选信息冲突 | Preserve conflict statement, sources, evidence, and verification handle. / 保留冲突说明、来源、证据和验证入口。 |
| Probe missing / 探针缺失 | Continue with default policy and record that no feedback was available. / 使用默认策略继续，并记录没有反馈。 |
| Uncertain scene profile / 场景画像不确定 | Use conservative policy and raise current request plus evidence priority. / 使用保守策略，提升当前请求和证据优先级。 |

### Done Criteria / 完成标准

- The context package contains task goal, safety and permission boundary, current evidence, compressed background, deferred handles, and risks. / 上下文包包含任务目标、安全与权限边界、当前证据、压缩背景、延迟入口和风险。
- Every candidate item has a decision: enter context, compress, defer read, reject, drop, or block. / 每个候选信息项都有处理决定：进入上下文、压缩、延迟读取、拒绝、丢弃或阻断。
- Every decision has a reason and a traceable source. / 每个决定都有原因和可追溯来源。
- L0 has not been removed by budget pressure. / 零级没有被预算压力移除。
- L2 summaries preserve conclusion, evidence, and source index. / 二级摘要保留结论、证据和来源索引。
- L3 read handles include scope and permission requirements. / 三级读取入口包含作用域和权限要求。
- Probe events are emitted when the probe is available. / 存在探针时已发送探针事件。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Context Triage / 上下文分诊; Context Priority Triage / 上下文优先级分诊.
- 诊断用途 / Diagnostic Use: Use when incoming context must be classified before choosing a path. / 当输入上下文必须先分类再选路径时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 需求进入、上下文感知、协作交接、治理审查 / Intake, context sensing, collaboration handoff, governance review.
- 当前症状 / Current Symptoms: Context is too large, mixed, permission-sensitive, or frequently routed to the wrong downstream path. / 上下文过大、来源混杂、权限敏感，或经常被送入错误的后续路径。
- 适配信号 / Fit Signals: 输入需要先识别类型、来源、优先级或责任归属 / Inputs must be classified by type, source, priority, or ownership.
- 调整方向 / Adjustment Direction: Insert a priority triage gate before the main reasoning or tool route. / 在主推理或工具路由前插入优先级分诊门。
- 修改方式 / How To Modify: Normalize candidate items, classify by L0-L3, assemble by budget order, emit decision trace, and optionally receive probe feedback. / 规范化候选项，按零级到三级分类，按预算顺序装配，输出决策 Trace，并可接收探针反馈。
- 输入 / Inputs: task request, runtime context, candidate items, triage policy, optional probe feedback. / 任务请求、运行时上下文、候选信息项、分诊策略、可选探针反馈。
- 输出 / Outputs: context package, decision record, compression task list, read handle list, risk notes, probe-readable events. / 上下文包、分诊决策记录、压缩任务清单、读取入口清单、风险提示、探针可读事件。
- 风险与治理 / Risks & Governance: L0 cannot be dropped; unclear permission blocks production flow; read handles must carry scope; every decision must be traceable; over-aggressive filtering causes context starvation `FAIL_0012` — watch rejection rate and downstream rework, and keep L3 read handles as the escape hatch. / 零级不可丢弃，权限不清时阻断生产流程，读取入口必须带作用域，所有决策必须可追溯；过度过滤会导致上下文饥饿 `FAIL_0012`——监控拒绝率与下游返工，并保留三级读取入口作为逃生通道。

Observability Metrics File / 可观测性指标文件: [perception-routing-observability.md](perception-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. Record the scene type, candidate count, L0-L3 counts, rejected count, used budget, selected route, failures, and probe feedback. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。记录场景类型、候选数量、零级到三级数量、拒绝数量、已用预算、选中路由、失败项和探针反馈。
