# Semantic Compaction / 语义压缩

Cell / 交织点: perception-chain / 感知 x 链式
Capability / 能力: Perception / 感知
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Alias / 别名: Semantic Compression Execution / 语义压缩的执行流程
Standalone Executable / 可独立执行: Yes / 是
Primary Axis / 主轴: Perception / 感知
Secondary Axes / 辅轴: Memory / 记忆; Governance / 治理
Primary Topology / 主拓扑: Chain / 链式
Secondary Topologies / 辅拓扑: Loop / 循环; Orchestration / 编排

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Semantic Compaction / 语义压缩 is not ordinary summarization. It is a working-memory maintenance flow for long-running agent work. It must reduce context occupancy / 减少上下文占用, preserve key semantics / 保留关键语义, and protect traceable evidence / 保护可回溯证据 while keeping the next reasoning step executable. / 语义压缩不是普通摘要，而是长任务中的工作记忆维护流程：在保证下一步仍可执行的前提下，减少上下文占用、保留关键语义、保护可回溯证据。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Perception / 感知 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Perception / 感知 x Chain / 链式 in arXiv:2605.13850. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Perception / 感知 x Chain / 链式映射到该单元。
- 问题 / Problem: Raw signals, tool results, logs, documents, and conversation history can exceed the context budget while still containing evidence needed for later reasoning. / 原始信号、工具结果、日志、文档和对话历史会超出上下文预算，但其中仍包含后续推理需要的证据。
- 架构方案 / Architectural Solution: Run an ordered compaction chain that classifies information, protects evidence, selects a compression level, updates a working memory anchor, attaches source handles, and passes a quality gate. / 执行有序压缩链：分类信息、保护证据、选择压缩级别、更新工作记忆锚点、挂接原文句柄，并通过质量门禁。
- 工程权衡 / Engineering Trade-offs: Sequential compaction is auditable and stable, but it needs looped quality repair and orchestrated probe/storage/handoff support when risk or drift rises. / 链式压缩易审计且稳定，但当风险或漂移升高时，需要循环质量修复，并与探针、存储和交接流程编排协同。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when raw signals must be compacted before they enter or remain in working context. / 当原始信号进入或保留在工作上下文前必须压缩时使用。

### Execution Contract / 执行契约

- Trigger / 触发条件: Run when context grows, tool results become verbose, repeated attempts appear, evidence risks rise, or a handoff may be needed. / 当上下文膨胀、工具结果变长、重复尝试出现、证据风险升高或可能需要交接时执行。
- Objective / 目标: Keep the task executable after compression by preserving user goal, completed actions, current judgments, excluded paths, next steps, key evidence, and source handles. / 压缩后仍保持任务可执行，保留用户目标、已完成动作、当前判断、已排除路径、下一步、关键证据和原文句柄。
- Scope / 范围: classify information fragments, identify evidence items, choose a compression level, update the working memory anchor, attach source handles, run a quality gate, and record a compression event. / 分类信息片段、识别证据项、选择压缩级别、更新工作记忆锚点、挂接原文句柄、运行质量门禁、记录压缩事件。
- Stop Condition / 停止条件: Stop or lower compression strength if protected evidence lacks body or handle, the working memory anchor is incomplete, or high-risk material would be compressed without traceability. / 当受保护证据缺少正文或句柄、工作记忆锚点不完整，或高风险材料会在无可回溯性的情况下被压缩时停止或降低压缩强度。
- Output / 输出: compressed context, updated working memory anchor, preserved evidence list, source handle list, Compression Event / 压缩事件, Quality Gate Result / 质量门禁结果, and next-step recommendation. / 输出压缩后上下文、更新后的工作记忆锚点、保留证据清单、原文句柄清单、压缩事件、质量门禁结果和下一步建议。

### Mounting Guidance / 框架挂载建议

| Role / 角色 | Axis or Topology / 轴或拓扑 | Why / 理由 |
|---|---|---|
| Primary capability / 主能力 | Perception / 感知 | Compression decides what the agent can still see. / 压缩决定智能体后续仍能看见什么。 |
| Supporting capability / 辅助能力 | Memory / 记忆 | The working memory anchor preserves task state across rounds. / 工作记忆锚点承载跨轮任务状态。 |
| Supporting capability / 辅助能力 | Governance / 治理 | Compression events, evidence handles, privacy, and handoff need auditability. / 压缩事件、证据句柄、隐私和交接需要可审计。 |
| Primary topology / 主拓扑 | Chain / 链式 | Compaction proceeds through classify, protect, compress, anchor, gate, output. / 压缩按分类、保护、压缩、锚定、门禁、输出逐步推进。 |
| Supporting topology / 辅助拓扑 | Loop / 循环 | Failed quality gates trigger repair and lower compression strength. / 质量门禁失败会触发修复和降低压缩强度。 |
| Supporting topology / 辅助拓扑 | Orchestration / 编排 | Probe, policy, storage, handles, and handoff cooperate in production systems. / 生产系统中探针、策略、存储、句柄和交接需要协同。 |

### Scenario Adaptation / 场景适配层

Keep business differences in a scene adapter instead of hard-coding them into the main flow. / 将业务差异放入场景适配层，不写死在主流程中。

```yaml
scene_adapter / 场景适配:
  scene_type / 场景类型: ""
  risk_level / 任务风险等级: low | medium | high
  context_budget / 上下文预算: ""
  compressible_information_types / 可压缩信息类型: []
  protected_information_types / 必须保护的信息类型: []
  evidence_retention_strength / 证据保留强度: ""
  source_handle_policy / 原文句柄策略: ""
  privacy_masking_policy / 隐私与脱敏要求: ""
  handoff_required / 交接要求: false
  quality_gate_thresholds / 质量门禁阈值: {}
  evaluation_goals / 评估目标: []
```

Scene examples / 场景示例:

| Scene / 场景 | Must Protect / 必须保护 | Prefer Compressing / 优先压缩 | Quality Focus / 质量重点 |
|---|---|---|---|
| Long-document research / 长文档研究 | Research goal, conclusions, evidence sources, citation locations, open questions. / 研究目标、结论、证据来源、引用位置、未解决问题。 | Repeated background and already-synthesized intermediate material. / 重复背景和已归纳中间材料。 | No conclusion drift; evidence remains traceable. / 结论不漂移，证据可回溯。 |
| Debugging / 错误排查 | Error type, key numbers, paths, failing tests, failed attempts, raw log handles. / 错误类型、关键数字、路径、失败测试、已失败方案、原始日志句柄。 | Repeated logs, irrelevant normal output, unrelated environment details. / 重复日志、无关正常输出、无关环境信息。 | Error evidence is not lost; failed attempts are not repeated. / 错误证据不丢，不重复失败方案。 |
| Content production / 内容生产 | Style preference, topic boundary, accepted version, forbidden expressions. / 风格偏好、主题边界、已确认版本、禁用表达。 | Old drafts, outdated alternatives, repeated feedback. / 旧草稿、过期备选、重复反馈。 | Style continuity and clear version evolution. / 风格一致，版本演进清晰。 |

### Input Contract / 输入契约

Required inputs / 必需输入:

```yaml
current_session_history / 当前会话历史: []
current_task_goal / 当前任务目标: ""
current_context_usage / 当前上下文占用: ""
working_memory_anchor / 当前工作记忆锚点: {}
recent_tool_results_or_external_material / 最近工具结果或外部资料返回: []
existing_compression_records / 已有压缩记录: []
scene_adapter / 场景适配配置: {}
```

Optional inputs / 可选输入:

```yaml
observability_probe_report / 可观测性探针报告: {}
compression_advice / 压缩建议: []
error_evidence_list / 错误证据清单: []
repeated_attempt_list / 重复尝试清单: []
information_hotspot_distribution / 信息热点分布: {}
source_material_handles / 原始材料句柄: []
human_handoff_requirement / 人工交接要求: ""
risk_level / 风险等级: ""
user_preferences / 用户偏好: []
compliance_constraints / 合规约束: []
```

### Output Contract / 输出契约

Minimum outputs / 最小输出:

- Compressed Context / 压缩后上下文
- Updated Working Memory Anchor / 更新后的工作记忆锚点
- Preserved Evidence List / 保留证据清单
- Source Handle List / 原文句柄清单
- Compression Event / 压缩事件记录
- Quality Gate Result / 质量门禁结果
- Next-Step Recommendation / 下一步建议

High-risk or long-running outputs / 高风险或长任务输出:

- Handoff Summary / 交接摘要
- Excluded Path List / 已排除方案清单
- Evidence Trace Index / 证据回溯索引
- Compression Risk Notes / 压缩风险说明
- Human Confirmation Questions / 需要人工确认的问题

### Core Objects / 核心对象

Information Fragment / 信息片段:

```yaml
Information Fragment / 信息片段:
  source / 来源: user_input | agent_reply | tool_result | external_material | error_log | test_result | human_note
  content / 内容: ""
  token_usage / 占用: 0
  created_at / 时间: ""
  importance / 重要性: high | medium | low
  is_error / 是否错误: false
  needs_raw_source / 是否需要原文: false
  source_handle / 原文句柄: ""
```

Evidence Item / 证据项:

```yaml
Evidence Item / 证据项:
  type / 类型: error | key_number | path | failing_test | user_constraint | decision_basis | excluded_path | citation
  content / 内容: ""
  severity / 严重性: high | medium | low
  must_keep / 是否必须保留: true
  fingerprint / 指纹: ""
  source_handle / 原文句柄: ""
```

Working Memory Anchor / 工作记忆锚点:

```yaml
Working Memory Anchor / 工作记忆锚点:
  user_goal / 用户目标: ""
  completed_actions / 已完成动作: []
  current_judgments / 已形成判断: []
  excluded_paths / 已排除方案: []
  next_plan / 下一步计划: []
  evidence_references / 证据引用: []
  open_questions / 未决问题: []
```

Compression Event / 压缩事件:

```yaml
Compression Event / 压缩事件:
  event_id / 事件编号: ""
  session_id / 会话编号: ""
  trigger_reason / 触发原因: ""
  compression_level / 压缩级别: ""
  before_tokens / 压缩前占用: 0
  after_tokens / 压缩后占用: 0
  preserved_evidence_count / 保留证据数量: 0
  created_handle_count / 创建句柄数量: 0
  updated_anchor_fields / 更新的工作记忆字段: []
  dropped_or_masked_categories / 丢弃或遮蔽的信息类别: []
  quality_gate_result / 质量门禁结果: ""
  occurred_at / 发生时间: ""
```

### Compression Levels / 压缩级别

| Level / 级别 | Use When / 适用条件 | Actions / 动作 | Do Not Lose / 不得丢失 |
|---|---|---|---|
| L0 Mark Only / 第零级：不压缩，只标注 | Task just started, usage is low, raw details still matter, or risk is high but evidence is not organized. / 任务刚开始、占用较低、原始细节仍重要，或风险高但证据尚未整理。 | Label information types, identify potential evidence, create initial anchor, attach handles to large material. / 标注信息类型、识别潜在证据、建立初始锚点、为大块内容挂句柄。 | Nothing is removed. / 不删除内容。 |
| L1 Clean Verbose Returns / 第一级：清理冗长返回 | Tool results grow, repeated output appears, normal logs or intermediate results dominate. / 工具结果变长、重复输出增多、正常日志或中间结果占用过大。 | Mask old non-key returns, merge duplicates, delete invalid whitespace, replace long output with summary plus handle. / 遮蔽旧的非关键返回、合并重复、删除无效空白、长输出替换为摘要加句柄。 | Error type, key number, path, line or paragraph location, failing test, user constraint, failed path. / 错误类型、关键数字、路径、行号或段落位置、失败测试、用户约束、已失败方案。 |
| L2 Merge into Working Memory Anchor / 第二级：合并进工作记忆锚点 | Conversation is long, old history affects reasoning, multiple decisions exist, or L1 is not enough. / 会话较长、旧历史影响推理、多轮决策形成，或一级不够。 | Extract user goal, completed actions, current judgments, excluded paths, next plan, and evidence references into the anchor. / 抽取用户目标、已完成动作、已形成判断、已排除方案、下一步计划和证据引用进入锚点。 | Do not repeatedly summarize the summary. Keep incremental anchor updates. / Do not repeatedly summarize the summary；保持增量更新。 |
| L3 Extreme Compression and Handoff Signal / 第三级：极限压缩与交接信号 | Context keeps expanding, compression has triggered repeatedly, semantic drift rises, or handoff/new session is needed. / 上下文持续膨胀、多次触发压缩、语义漂移升高，或需要交接、新会话。 | Keep minimum executable anchor, preserve all evidence indexes, export handoff summary, mark high-risk open questions. / 保留最小可执行锚点、保留全部证据索引、导出交接摘要、标记高风险未决问题。 | L3 is an exit or handoff signal, not ordinary extra compression. / 第三级是退场或交接信号，不是普通再压一次。 |

### Trigger Strategy / 触发策略

Trigger when any signal crosses the scene threshold. / 任一信号超过场景阈值时触发。

- Context usage exceeds threshold. / 上下文占用超过阈值。
- Turns are too many. / 轮次过多。
- Tool results or external materials are too large. / 工具结果或外部资料过大。
- Error or failure records become dense. / 错误或失败记录密集。
- The agent repeats queries, attempts, or questions. / 智能体开始重复查询、重复尝试或重复提问。
- User corrections increase. / 用户纠正次数增多。
- Working memory anchor misses key fields. / 工作记忆锚点缺失关键字段。
- Probe recommends compression or handoff. / 探针建议压缩或交接。

Threshold guidance / 阈值建议:

- Low-risk content generation can compress later. / 低风险内容生成可以晚压。
- Ordinary long tasks use medium thresholds. / 普通长任务使用中等阈值。
- Debugging compresses earlier but preserves evidence strongly. / 错误排查较早压缩，但强保护证据。
- High-risk tasks compress earlier and more conservatively. / 高风险任务更早触发并保守压缩。
- Handoff-oriented tasks prepare handoff summaries early. / 需要交接的任务优先准备交接摘要。

### Execution Procedure / 执行流程

1. Read scene adapter / 读取场景适配配置: confirm scene, risk, evidence requirements, thresholds, and handoff requirements. / 确认场景、风险、证据要求、阈值和交接要求。
2. Collect current context / 收集当前上下文: collect conversation history, tool results, external material, errors, tests, intermediate decisions, current anchor, and prior compression events. / 收集对话历史、工具结果、外部资料、错误、测试、中间决策、当前锚点和历史压缩事件。
3. Classify information fragments / 分类信息片段: user goal, constraints, agent actions, external returns, error evidence, intermediate judgments, failed paths, next plan, background noise, and traceable raw material. / 分类用户目标、约束、动作、外部返回、错误证据、中间判断、失败方案、下一步、背景噪声和可回溯原文。
4. Identify key evidence / 识别关键证据: protect error type, failure reason, key number, path, line or paragraph location, failing test, user request, decision basis, excluded path, and source citation. / 保护错误类型、失败原因、关键数字、路径、行号或段落位置、失败测试、用户要求、决策依据、排除方案和来源引用。
5. Select compression level / 判断压缩级别: use context usage, expansion source, error density, repeated attempts, risk level, anchor completeness, handoff need, and probe advice. / 根据上下文占用、膨胀来源、错误密度、重复尝试、风险等级、锚点完整度、交接要求和探针建议判断级别。
6. Execute level-specific compaction / 执行分级压缩: apply L0, L1, L2, or L3 actions. / 执行第零级、第一级、第二级或第三级动作。
7. Update working memory anchor / 更新工作记忆锚点: ensure it answers what the user wants, what was done, what was judged, what was excluded, what comes next, and where evidence lives. / 确保锚点回答用户要什么、做过什么、判断了什么、排除了什么、下一步是什么、证据在哪里。
8. Attach source handles / 挂接原文句柄: attach handles for long logs, documents, full tool returns, full test output, raw user material, large intermediate material, and masked old returns. / 为长日志、长文档、完整工具返回、完整测试输出、原始用户资料、大块中间材料和被遮蔽旧返回挂句柄。
9. Run quality gate / 运行质量门禁: check protected evidence, anchor completeness, handle usability, and next-step clarity. / 检查受保护证据、锚点完整度、句柄可用性和下一步清晰度。
10. Output or repair / 输出或修复: if the gate passes, emit outputs and continue; otherwise repair evidence, handles, anchor, compression strength, or handoff. / 门禁通过则输出并继续；不通过则修复证据、句柄、锚点、压缩强度或交接。

### Information Handling Strategy / 信息处理策略

| Information Type / 信息类型 | Recommended Handling / 推荐处理 | Notes / 说明 |
|---|---|---|
| User goal / 用户目标 | Keep or write into anchor. / 保留或写入锚点。 | Must not become vague. / 不能被模糊化。 |
| User constraints / 用户约束 | Keep or structure. / 保留或结构化。 | Especially prohibitions and preferences. / 尤其是禁止项和偏好。 |
| Background / 普通背景 | Compress. / 可压缩。 | Preserve conclusion. / 保留结论即可。 |
| Verbose tool return / 冗长工具返回 | Mask with summary and handle. / 摘要加句柄遮蔽。 | Keep action record and errors. / 保留动作记录和错误。 |
| Error information / 错误信息 | Strongly protect. / 强保护。 | Keep type, key number, path, and handle. / 保留类型、关键数字、位置和句柄。 |
| Failing test / 测试失败 | Strongly protect. / 强保护。 | Keep test name, assertion, failure reason, and location. / 保留测试名、断言、失败原因和位置。 |
| Key number / 关键数字 | Strongly protect. / 强保护。 | Do not round or generalize. / 不得四舍五入或泛化。 |
| Path or location / 位置路径 | Strongly protect. / 强保护。 | File, document, line, or paragraph location. / 文件、文档、行号或段落位置。 |
| Completed action / 已完成动作 | Moderately preserve. / 中度保留。 | Compress into an action sequence. / 可压缩为动作序列。 |
| Current judgment / 已形成判断 | Preserve. / 保留。 | Later reasoning depends on it. / 后续推理依赖它。 |
| Failed path / 已失败方案 | Strongly protect. / 强保护。 | Prevent repeated attempts. / 防止重复试错。 |
| Next plan / 下一步计划 | Preserve. / 保留。 | Maintains continuity. / 保证任务连续性。 |
| Large raw material / 原始大材料 | Handleize. / 句柄化。 | Summary enters context; raw source stays retrievable. / 摘要进入上下文，原文可回溯。 |

### Quality Gate / 质量门禁

Must-pass rules / 必过规则:

- Missing key error count is zero. / 关键错误丢失数为零。
- Every must-keep evidence item has body or source handle. / 必须保留证据均有正文或原文句柄。
- Working memory anchor core fields are complete. / 工作记忆锚点核心字段完整。
- Failed paths are not deleted. / 已失败方案没有被删除。
- Next plan is explicit. / 下一步计划明确。
- Compression event is recorded. / 压缩事件已记录。

Conditional rules / 条件规则:

- If error information exists, preserve error type, key number, location, and source handle. / 如果存在错误信息，必须保留错误类型、关键数字、位置和原文句柄。
- If failed attempts exist, update excluded paths. / 如果存在失败尝试，必须更新已排除方案。
- If L3 is selected, generate Handoff Summary / 交接摘要. / 如果进入第三级，必须生成交接摘要。
- If risk is high, forbid aggressive compression without handles. / 如果风险高，禁止无句柄的激进压缩。
- If private material exists, mask it before report or summary output. / 如果涉及隐私资料，先脱敏再进入报告或摘要。

Repair actions / 修复动作:

- Restore key evidence. / 补回关键证据。
- Add source handles. / 补充原文句柄。
- Repair working memory anchor. / 修复工作记忆锚点。
- Lower compression level. / 降低压缩级别。
- Regenerate compressed summary. / 重新生成压缩摘要。
- Generate handoff summary. / 生成交接摘要。
- Request human confirmation. / 请求人工确认。

### Handoff Summary / 交接摘要

Generate Handoff Summary / 交接摘要 when the task is too long, risk rises, L3 is selected, or ownership changes. / 当任务过长、风险升高、进入第三级或责任主体变化时生成交接摘要。

Required fields / 必需字段:

- Task Goal / 任务目标
- Current State / 当前状态
- Completed Actions / 已完成动作
- Current Judgments / 已形成判断
- Key Evidence / 关键证据
- Excluded Paths / 已排除方案
- Next Plan / 下一步计划
- Open Questions / 未决问题
- Risk Notes / 风险提示
- Source Handles / 原文句柄

The handoff goal is to let the next executor understand why the task reached this state without reading the full history. / 交接摘要的目标是让下一个执行者无需阅读全文，也能知道任务为什么走到这里。

### Minimum Standalone Run / 独立运行最小流程

Minimum executable capabilities / 最小可执行能力:

- Information classification / 信息分类
- Evidence identification / 证据识别
- Working Memory Anchor / 工作记忆锚点
- Three active compression levels / 三级压缩
- Source handles / 原文句柄
- Quality gate / 质量门禁
- Compression event record / 压缩事件记录

Minimum flow / 最小流程:

```text
Collect context / 收集上下文
  -> Identify evidence / 识别证据
  -> Select compression level / 判断压缩级别
  -> Clean or merge / 清理或合并
  -> Update working memory anchor / 更新工作记忆锚点
  -> Check quality gate / 检查质量门禁
  -> Output compression result / 输出压缩结果
```

### Probe Interaction / 探针交互

Semantic compaction can run alone, but a probe can provide stronger runtime signals. / 语义压缩可以独立运行，但探针能提供更强的运行时信号。

Probe may provide / 探针可提供:

- Context usage ratio / 上下文占用率
- Turn statistics / 轮次统计
- Information hotspot sources / 信息热点来源
- Error evidence detection / 错误证据检测结果
- Key number detection / 关键数字检测结果
- Path and location detection / 位置路径检测结果
- Repeated attempt detection / 重复尝试检测结果
- Working memory completeness / 工作记忆完整度
- Missing excluded paths / 已排除方案缺失情况
- Source handle coverage / 原文句柄覆盖率
- Recommended compression level / 建议压缩级别
- Masking rules / 建议遮蔽规则
- Keep rules / 建议保留规则
- Repair actions / 建议修复动作
- Handoff need / 是否需要交接

Use probe signals to adjust thresholds, choose compression level, decide evidence protection, mask returns, repair anchors, trigger handoff, and reduce semantic drift. / 使用探针信号调整阈值、选择压缩级别、决定证据保护、遮蔽返回、修复锚点、触发交接，并降低语义漂移。

### Evaluation / 评估方式

General metrics / 通用指标:

- Post-compaction task success rate / 压缩后任务成功率
- Key evidence retention rate / 关键证据保留率
- Lost error evidence count / 错误证据丢失数
- Key number retention rate / 关键数字保留率
- Working memory completeness / 工作记忆完整度
- Repeated failed action rate / 重复失败动作率
- Source handle traceability rate / 原文句柄可回溯率
- User correction rate after compaction / 压缩后用户纠正率
- Handoff summary completeness / 交接摘要完整度
- Semantic drift risk / 语义漂移风险

Scenario weighting / 场景权重:

- Debugging: emphasize error evidence retention and repeated failed action rate. / 错误排查：提高错误证据保留率和重复失败动作率权重。
- Research: emphasize source traceability and conclusion stability. / 资料研究：提高来源回溯率和结论稳定性权重。
- Content production: emphasize style consistency and user preference retention. / 内容生产：提高风格一致性和用户偏好保留权重。
- Workflow approval: emphasize decision basis and state continuity. / 流程审批：提高决策依据和状态连续性权重。
- Support ticket: emphasize handoff summary and time-risk signals. / 客服工单：提高交接摘要和时效风险权重。

### Failure Modes / 常见失败模式

- Treating semantic compaction as ordinary summarization. / 把语义压缩当成普通摘要。
- Compressing length without protecting evidence. / 只压缩长度，不保护证据。
- Turning errors into vague conclusions. / 把错误信息压成模糊结论。
- Losing key numbers and locations. / 丢失关键数字和位置路径。
- Forgetting failed paths. / 忘记已经失败的方案。
- Repeatedly summarizing the summary. / 反复生成摘要的摘要。
- Losing source handles and traceability. / 没有原文句柄，无法回溯。
- Skipping the quality gate after compression. / 压缩后不做质量门禁。
- Treating L3 as normal compression instead of handoff. / 第三级压缩后仍不交接。
- Using one threshold set for every scene. / 不同场景使用同一套阈值。

### Done Criteria / 完成标准

- Context occupancy is reduced or kept below the scene threshold. / 上下文占用已降低或保持在场景阈值内。
- Key semantics needed for the next reasoning step are preserved. / 下一步推理所需关键语义已保留。
- Every protected evidence item has body, handle, or trace index. / 每个受保护证据都有正文、句柄或回溯索引。
- Working memory anchor answers goal, actions, judgments, excluded paths, next plan, evidence, and open questions. / 工作记忆锚点能回答目标、动作、判断、排除路径、下一步、证据和未决问题。
- Compression level and trigger reason are recorded. / 压缩级别和触发原因已记录。
- Quality Gate Result / 质量门禁结果 is pass, repaired, or explicitly handed off. / 质量门禁结果为通过、已修复或明确交接。
- L3 runs include Handoff Summary / 交接摘要. / 第三级执行包含交接摘要。
- Trace entry can be written with evidence and outcome. / 可写入包含证据和结果的 Trace。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Semantic Compaction / 语义压缩; Semantic Compression Execution / 语义压缩的执行流程.
- 诊断用途 / Diagnostic Use: Use when raw signals must be compacted before they enter working context. / 当原始信号进入工作上下文前必须压缩时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 上下文感知、知识沉淀、运行监控、协作交接、治理审查 / Context sensing, knowledge memory, monitoring, collaboration handoff, governance review.
- 当前症状 / Current Symptoms: Context grows, history becomes noisy, tools return too much data, failed attempts repeat, or handoff risk rises. / 上下文膨胀、历史变噪、工具返回过长、失败尝试重复或交接风险升高。
- 适配信号 / Fit Signals: Signals must be collected, parsed, protected, compacted, anchored, and gated in sequence. / 信号需要按顺序采集、解析、保护、压缩、锚定并通过门禁。
- 调整方向 / Adjustment Direction: Insert a semantic compaction chain before context overflow, semantic drift, or handoff failure appears. / 在上下文溢出、语义漂移或交接失败前插入语义压缩链。
- 修改方式 / How To Modify: Add scene adapter, compression levels, evidence protection, working memory anchor, source handles, quality gate, compression events, and optional probe interaction. / 增加场景适配、压缩级别、证据保护、工作记忆锚点、原文句柄、质量门禁、压缩事件和可选探针交互。
- 输入 / Inputs: current session history, task goal, context usage, working memory anchor, recent tool or external material, compression records, scene adapter, optional probe report. / 当前会话历史、任务目标、上下文占用、工作记忆锚点、最近工具或外部材料、压缩记录、场景适配、可选探针报告。
- 输出 / Outputs: compressed context, updated working memory anchor, preserved evidence list, source handle list, compression event, quality gate result, next-step recommendation, optional handoff summary. / 压缩后上下文、更新后的工作记忆锚点、保留证据清单、原文句柄清单、压缩事件、质量门禁结果、下一步建议、可选交接摘要。
- 风险与治理 / Risks & Governance: Evidence, key numbers, locations, failed paths, source handles, privacy masking, quality gate, and audit trace must be protected. / 必须保护证据、关键数字、位置、失败方案、原文句柄、隐私脱敏、质量门禁和审计追踪。

Observability Metrics File / 可观测性指标文件: [perception-chain-observability.md](perception-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. Record trigger reason, compression level, before/after context usage, preserved evidence count, handle count, updated anchor fields, quality gate result, repair actions, handoff status, and outcome. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。记录触发原因、压缩级别、压缩前后占用、保留证据数量、句柄数量、更新的锚点字段、质量门禁结果、修复动作、交接状态和结果。
