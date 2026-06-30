# Context Priority Triage Probe / 上下文优先级分诊探针 Observability Metrics / 可观测性指标

Cell / 交织点: perception-routing / 感知 x 路由
Capability / 能力: Perception / 感知
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Standalone Executable / 可独立执行: Yes / 是

Use this file as the observability metrics and probe protocol source for Context Priority Triage / 上下文优先级分诊. / 将本文档作为上下文优先级分诊的可观测性指标与探针协议来源。
Design Pattern File / 设计模式文件: [perception-routing.md](perception-routing.md)

## Probe Role / 探针定位

The probe is not the triage executor. It observes, evaluates, attributes failures, and feeds structured signals back to the next triage or compression run. / 探针不是分诊执行器，而是观察、评估、失败归因，并把结构化信号回填给下一轮分诊或压缩。

It answers ten engineering questions / 它回答十个工程问题:

- Was candidate information complete? / 候选信息是否完整？
- Did L0 constraints enter context? / 零级约束是否进入上下文？
- Was current evidence preserved? / 当前证据是否稳定保留？
- Did summaries preserve conclusion, evidence, and source index? / 摘要是否保留结论、证据和来源索引？
- Were deferred read handles safe, usable, and useful? / 延迟读取入口是否安全、可用、有效？
- Did dropped information later prove useful? / 被丢弃信息是否后来证明有价值？
- Was the context high-signal and low-noise? / 上下文是否高信号、低噪声？
- Did triage failure affect the final result? / 分诊失败是否影响最终结果？
- Did the policy drift from business reality? / 策略是否随业务变化发生漂移？
- What should be fed back to triage and compression? / 哪些观测结果应回填给分诊和压缩？

## Operating Modes / 运行模式

| Mode / 模式 | Intervention / 干预方式 | Use When / 适用场景 |
|---|---|---|
| Sidecar Probe / 旁路探针 | Observe only; do not change the workflow. / 只观察，不改变工作流。 | Existing workflows need a baseline or context problem diagnosis. / 现有工作流需要建立基线或定位上下文问题。 |
| Shadow Evaluator / 影子评估器 | Run on historical or sampled traffic and compare strategies. / 对历史或采样流量运行，并对比策略。 | New triage or compression policy needs validation before rollout. / 新分诊或压缩策略上线前需要验证。 |
| Inline Guard / 内联守卫 | Block high-risk issues at critical workflow points. / 在关键节点阻断高风险问题。 | Enterprise, multi-tenant, permission-sensitive, or audited workflows. / 企业级、多租户、权限敏感或强审计流程。 |
| Compression Strategy Assistant / 压缩策略辅助器 | Provide compression keep/drop/strength signals. / 提供压缩保留、丢弃和强度信号。 | L2 summaries, long documents, logs, code context, research material, or tool results need safe compression. / 二级摘要、长文档、日志、代码上下文、研究材料或工具结果需要安全压缩。 |

## Probe Input Contract / 探针输入契约

Collect events when available; accept partial input for sidecar diagnosis. / 优先采集事件流；旁路诊断允许部分输入。

```yaml
probe_input / 探针输入:
  task_request / 任务请求:
    task_id / 任务标识: ""
    task_type / 任务类型: ""
    current_user_message / 当前用户消息: ""
    current_goal / 当前目标: ""
  scene_profile / 场景画像:
    scene_type / 场景类型: ""
    multi_turn / 是否多轮: false
    requires_citation / 是否需要引用: false
    has_permission_boundary / 是否有权限边界: false
    compression_allowed / 是否允许压缩: true
    deferred_read_allowed / 是否允许延迟读取: true
  runtime_context / 运行时上下文:
    user_id / 用户标识: ""
    tenant_id / 租户标识: ""
    project_id / 项目标识: ""
    session_id / 会话标识: ""
    data_scope / 数据范围: ""
    tool_permissions / 工具权限: []
  candidate_items / 候选信息清单:
    - item_id / 信息标识: ""
      name / 信息名称: ""
      source_type / 来源类型: ""
      estimated_tokens / 估算长度: 0
      priority_hint / 优先级提示: ""
      read_handle / 读取入口: ""
      scope / 所属范围: ""
      is_error_evidence / 是否错误信息: false
      is_safety_boundary / 是否安全边界: false
  context_package / 上下文包:
    direct_items / 直接进入的信息: []
    compressed_items / 压缩进入的信息: []
    deferred_read_handles / 延迟读取入口: []
    dropped_items / 被丢弃信息: []
    rejected_items / 被拒绝信息: []
    risks / 风险提示: []
  triage_decisions / 分诊决策:
    record_id / 记录标识: ""
    policy_version / 策略版本: ""
    total_budget / 总预算: 0
    used_budget / 已用预算: 0
    candidate_count / 候选信息总量: 0
    item_decisions / 每个信息项的处理决定: []
  compression_events / 压缩事件:
    - source_item / 原始材料: ""
      summary / 摘要结果: ""
      retained_evidence / 保留证据: []
      source_index / 来源索引: []
      compression_strength / 压缩强度: ""
  read_handle_events / 读取入口事件:
    - exposed_handle / 暴露入口: ""
      read_attempted / 是否尝试读取: false
      read_success / 是否读取成功: false
      latency_ms / 读取延迟: 0
      result_used / 读取结果是否被使用: false
  task_result / 任务结果:
    success / 是否成功: false
    rework_required / 是否返工: false
    human_takeover / 是否人工接管: false
    context_failure / 是否因上下文问题失败: false
```

## Event Stream / 事件流

Prefer event-based collection over final-result-only inspection. / 优先按事件流采集，而不是只看最终结果。

Required event names / 推荐事件名:

- Candidate Collected / 候选信息已收集
- Metadata Normalized / 元数据已规范化
- Scope Checked / 范围已检查
- Priority Assigned / 信息已分级
- Context Inserted / 信息已进入上下文
- Context Compressed / 信息已压缩
- Read Deferred / 信息已延迟读取
- Item Dropped / 信息已丢弃
- Item Rejected / 信息已拒绝
- Context Package Built / 上下文包已生成
- Read Handle Exposed / 读取入口已暴露
- Read Handle Used / 读取入口已使用
- Compression Completed / 压缩已完成
- Model Completed / 模型已完成
- Result Scored / 结果已评分
- Human Feedback Received / 人工已反馈

## Probe Output Contract / 探针输出契约

The probe produces structured feedback, not plain logs. / 探针产出结构化反馈，而不是普通日志。

```yaml
Observation Report / 观测报告:
  report_id / 报告标识: ""
  task_id / 任务标识: ""
  policy_version / 策略版本: ""
  scene_type / 场景类型: ""
  overall_score / 总体评分: ""
  budget_pressure / 预算压力: ""
  critical_layer_completeness / 关键层完整性: ""
  context_quality / 上下文质量: ""
  compression_quality / 压缩质量: ""
  read_handle_health / 读取入口健康度: ""
  candidate_set_quality / 候选集质量: ""
  outcome_attribution / 结果归因: ""
  cost_benefit / 成本收益: ""
  governance_risk / 治理风险: ""
  policy_drift / 策略漂移: ""
  main_issues / 主要问题: []
  recommendations / 修正建议: []
Strategy Feedback / 策略反馈:
  priority_up_types / 建议提升优先级的信息类型: []
  priority_down_types / 建议降低优先级的信息类型: []
  fixed_protection_items / 建议固定保护的信息: []
  reduce_read_handles / 建议减少暴露的读取入口: []
  strengthen_recall_sources / 建议加强召回的来源: []
  tighten_permission_rules / 建议收紧的权限规则: []
  budget_ratio_adjustments / 建议调整的预算比例: []
  rollback_policy_versions / 建议回滚的策略版本: []
Compression Advice / 压缩建议:
  item_id / 信息标识: ""
  source_type / 来源类型: ""
  recommended_strength / 建议压缩强度: ""
  must_keep_conclusions / 必须保留的结论: []
  must_keep_evidence / 必须保留的证据: []
  must_keep_source_index / 必须保留的来源索引: []
  forbidden_loss_fields / 禁止丢失的字段: []
  preserve_conflict_statement / 是否需要保留冲突说明: false
  action / 建议动作: enter_raw | compress | defer_read | reject
Risk Alert / 风险告警:
  alert_id / 告警标识: ""
  severity / 告警等级: ""
  alert_type / 告警类型: ""
  trigger / 触发条件: ""
  blast_radius / 影响范围: ""
  recommended_action / 建议动作: ""
```

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Context Priority Triage / 上下文优先级分诊 improves context selection, routing, budget control, compression, read-handle safety, and traceability. / 使用以下指标观察上下文优先级分诊是否改善上下文选择、路由、预算控制、压缩、读取入口安全和可追溯性。

- 质量指标 / Quality Metrics:
  - Priority Accuracy / 优先级准确率: Share of sampled candidate items whose L0-L3, reject, or drop decision is accepted by downstream review or probe feedback. / 抽样候选项中，零级到三级、拒绝或丢弃决策被下游评审或探针反馈认可的比例。
  - Evidence Preservation Rate / 证据保留率: Share of L1 and L2 outputs that preserve required conclusion, evidence, and source index. / 一级和二级输出中保留必要结论、证据和来源索引的比例。
  - Critical Layer Completeness / 关键层完整性: Whether L0 constraints, current evidence, error evidence, and runtime boundaries are present. / 零级约束、当前证据、错误证据和运行时边界是否完整。
  - High Signal Ratio / 高信号比例: Useful context items divided by all context items. / 有效上下文项占全部上下文项的比例。
- 时延指标 / Latency Metrics:
  - Context Package Ready Latency / 上下文包可用时延: Time from triage trigger to a usable context package. / 从触发分诊到生成可用上下文包的耗时。
  - Permission Check Latency / 权限检查时延: Time spent checking user, tenant, project, tool, and data-scope boundaries. / 检查用户、租户、项目、工具和数据范围边界的耗时。
  - Compression Queue Latency / 压缩队列时延: Time from L2 assignment to compressed summary availability. / 从分配为二级到压缩摘要可用的耗时。
  - Deferred Read Retrieval Latency / 延迟读取回取时延: Time from L3 handle selection to successful retrieval when later used. / 三级读取入口被使用后，从选择入口到成功读取的耗时。
- 成本指标 / Cost Metrics:
  - Budget Protection Rate / 预算保护率: Share of runs where output budget and L0 budget are preserved without emergency truncation. / 输出预算和零级预算未被紧急截断的运行比例。
  - Context Token Reduction / 上下文 Token 降幅: Tokens avoided by compressing L2 and deferring L3 instead of loading all raw content. / 通过压缩二级和延迟三级而非加载全部原文节省的 Token。
  - Cost Benefit / 成本收益: Compare added triage latency and compression cost against reduced rework and lower context spend. / 比较新增分诊时延、压缩成本与减少返工和上下文成本之间的收益。
  - Manual Retriage Count / 人工重分诊次数: Number of manual corrections required after automated triage. / 自动分诊后需要人工修正的次数。
- 风险指标 / Risk Metrics:
  - High-Risk Capture Rate / 高风险捕获率: Share of safety, permission, identity, and data-scope constraints correctly classified as L0 or rejected. / 安全、权限、身份和数据范围约束被正确归为零级或拒绝的比例。
  - Unsafe Inclusion Count / 不安全纳入次数: Count of out-of-scope or unauthorized items that entered the context package. / 越权或不在范围内的信息进入上下文包的次数。
  - Missing L0 Count / 零级缺失次数: Count of runs where required L0 information was absent or removed. / 必需零级信息缺失或被移除的运行次数。
  - Read Handle Health Rate / 读取入口健康率: Share of L3 handles that include scope, permission, stable location, and can be resolved later. / 包含作用域、权限、稳定位置且后续可解析的三级读取入口比例。
- Trace 指标 / Trace Metrics:
  - Trace Decision Coverage / Trace 决策覆盖率: Share of candidate items with recorded original layer, final layer, action, reason, and source. / 记录原始层级、最终层级、动作、原因和来源的候选项比例。
  - Probe Feedback Closure Rate / 探针反馈闭环率: Share of probe feedback items reviewed and applied, rejected, or deferred with reason. / 探针反馈被评审并应用、拒绝或带原因延迟的比例。
  - Reclassification Reason Capture / 重分类原因记录率: Share of priority or route changes with an explicit reason. / 优先级或路由变更中记录明确原因的比例。
  - Outcome Linkage Rate / 结果关联率: Share of triage records linked to the final workflow outcome. / 分诊记录关联最终工作流结果的比例。

## Metric System / 核心指标体系

| Family / 类别 | Core Metrics / 核心指标 | Use / 用途 |
|---|---|---|
| Triage Pressure / 分诊压力 | Budget Usage Rate / 预算使用率; high-percentile dropped count; high-percentile deferred-read count; high-percentile compressed count; candidate growth rate. / 预算使用率、丢弃数量高位值、延迟读取数量高位值、压缩数量高位值、候选信息膨胀率。 | Detect whether information volume is crushing the workflow. / 判断信息量是否压垮工作流。 |
| Critical Layer Completeness / 关键层完整性 | Highest-priority loss count; current evidence loss count; missing error evidence; missing failure feedback; missing current request; missing runtime boundary. / 最高优先信息丢失次数、当前证据丢失次数、错误信息缺失次数、失败反馈缺失次数、当前请求缺失次数、运行时边界缺失次数。 | Confirm that key constraints and current evidence are stable. / 判断关键约束和当前证据是否稳定保留。 |
| Context Quality / 上下文质量 | High Signal Ratio / 高信号比例; evidence coverage; noise ratio; duplicate ratio; unmarked conflict count; key-content position risk. / 高信号比例、证据覆盖率、噪声比例、重复比例、冲突未标注次数、关键内容位置风险。 | Judge whether context content is useful and usable. / 判断进入上下文的信息是否真的有用。 |
| Priority Calibration / 优先级校准 | Needed-but-not-promoted ratio; frequently-used deferred item ratio; raw reread-after-compression ratio; manual priority correction ratio; frequent rank oscillation ratio. / 实际需要但未提升比例、延迟后频繁使用比例、压缩后频繁回读原文比例、人工修正优先级比例、多轮频繁升降级比例。 | Check whether the triage logic understands importance. / 判断分诊器是否稳定理解什么重要。 |
| Compression Quality / 压缩质量 | Compression ratio; evidence retention rate; source-index retention rate; summary conflict rate; summary reread rate; compression failure rate. / 压缩率、证据保留率、来源索引保留率、摘要冲突率、摘要回读率、压缩失败率。 | Verify whether L2 summaries remain trustworthy. / 判断二级摘要是否可信。 |
| Read Handle Health / 读取入口健康度 | Read success rate; invalid handle ratio; scoped handle ratio; cross-scope block count; high-percentile read latency; read-result contribution rate; exposed-unused handle ratio. / 读取成功率、失效入口比例、有作用域入口比例、跨范围读取阻断次数、读取延迟高位值、读取结果贡献率、暴露但未使用入口比例。 | Measure whether deferred-read is safe, available, and useful. / 判断延迟读取机制是否安全、可用、有效。 |
| Candidate Set Quality / 候选集质量 | Key material recall; complete miss ratio; reranking lift; source diversity; invalid candidate ratio; stale candidate ratio. / 关键材料召回率、关键材料完全漏召比例、重排序收益、来源多样性、无效候选比例、过期候选比例。 | Judge upstream collection quality. / 判断上游收集的信息质量。 |
| Outcome Attribution / 结果归因 | Task success rate; first-pass resolution rate; context-caused failure ratio; missing-context failure ratio; noisy-context failure ratio; rework rounds caused by context; human handoff ratio caused by context. / 任务成功率、首轮解决率、上下文导致失败比例、缺关键上下文导致失败比例、噪声上下文导致失败比例、上下文不足返工轮数、上下文问题转人工比例。 | Connect triage decisions to task outcomes. / 把分诊决策关联到任务结果。 |
| Cost Benefit / 成本收益 | Cost per successful task; invalid information occupancy; information saved by triage; compression cost share; deferred-read cost share; triage-added latency; rework reduction from triage. / 单次成功任务成本、无效信息占用比例、分诊节省信息量、压缩成本占比、延迟读取成本占比、分诊新增延迟、分诊带来的返工减少量。 | Decide whether budget savings create real value. / 判断节省预算是否换来更好结果。 |
| Governance Safety / 治理安全 | Missing runtime fields; missing high-priority safety rules; unscoped read handles; cross-user read attempts; cross-tenant read attempts; cross-project read attempts; permission reject ratio; context-injection blocks; missing audit records. / 运行时字段缺失次数、最高优先安全规则缺失次数、无作用域读取入口次数、跨用户读取尝试次数、跨租户读取尝试次数、跨项目读取尝试次数、权限拒绝比例、上下文注入拦截次数、审计记录缺失次数。 | Confirm the context entry satisfies governance. / 判断上下文入口是否满足治理要求。 |

## Compression Strategy Assistant / 压缩策略辅助器

When the probe assists semantic compression, it provides strategy signals and never replaces the compressor. / 当探针辅助语义压缩时，它只提供策略信号，不替代压缩器。

Before compression / 压缩前:

- Decide whether the item is suitable for compression. / 判断材料是否适合压缩。
- Recommend compression strength. / 建议压缩强度。
- List must-keep conclusions, evidence, source indexes, timestamps, fields, and conflict statements. / 列出必须保留的结论、证据、来源索引、时间点、字段和冲突说明。
- Recommend direct-entry or deferred-read when compression is risky. / 压缩有风险时建议直接进入上下文或改为延迟读取。

During compression / 压缩中:

- Check that conclusions, evidence, indexes, conflicts, timeline order, field meaning, source scope, and permission boundaries are not lost. / 检查结论、证据、索引、冲突、时间线顺序、字段含义、来源范围和权限边界没有丢失。

After compression / 压缩后:

- Evaluate whether the summary is usable for the current task. / 评估摘要是否可用于当前任务。
- Request added evidence, source index, raw excerpt, downgrade to read handle, or promotion to current work layer. / 要求补充证据、来源索引、原文片段，或降级为读取入口、提升为当前工作层。
- Flag hallucination, over-generalization, or erased conflict. / 标记幻化、过度概括或冲突被抹平。

Scene-specific keep rules / 场景化必须保留:

| Scene / 场景 | Must Keep / 必须保留 |
|---|---|
| Conversation history / 历史对话 | User goal, confirmed facts, unfinished items, excluded paths. / 用户目标、已确认事实、未完成事项、被排除路径。 |
| Log diagnosis / 日志诊断 | Anomaly timeline, error samples, impact scope, metric spikes. / 异常时间线、错误样本、影响范围、指标突变点。 |
| Long-document QA / 长文档问答 | Section conclusions, evidence spans, citation locations, applicability. / 章节结论、证据段、引用位置、适用范围。 |
| Code analysis / 代码分析 | Relevant functions, call relations, error evidence, modification risk. / 相关函数、调用关系、错误证据、修改风险。 |
| Data analysis / 数据分析 | Metric definition, field meaning, query scope, sample conclusion. / 指标口径、字段含义、查询范围、样本结论。 |
| Research synthesis / 研究整理 | Claims, experimental evidence, limitations, source. / 观点、实验依据、限制条件、出处。 |
| Enterprise workflow / 企业流程 | Permission boundary, approval state, responsible owner, audit clue. / 权限边界、审批状态、责任主体、审计线索。 |

## Probe Execution Procedure / 探针执行流程

1. Read task and scene profile. / 读取任务和场景画像。
2. Read candidate items and triage records. / 读取候选信息和分诊记录。
3. Check critical layer completeness. / 检查关键层完整性。
4. Check triage pressure and budget pressure. / 检查分诊压力和预算压力。
5. Check context quality. / 检查上下文质量。
6. Check compression quality. / 检查压缩质量。
7. Check read handle health. / 检查读取入口健康度。
8. Check candidate set quality. / 检查候选集质量。
9. Link final task result. / 关联最终任务结果。
10. Attribute failures. / 执行失败归因。
11. Generate Observation Report / 观测报告.
12. Generate Strategy Feedback / 策略反馈.
13. Generate Compression Advice / 压缩建议.
14. Trigger Risk Alert / 风险告警 when needed. / 必要时触发风险告警。
15. Feed signals back to the main triage workflow. / 把反馈回填给主分诊流程。

## Alert Rules / 告警规则

| Alert / 告警 | Severity / 等级 | Action / 动作 |
|---|---|---|
| Highest-priority information dropped / 最高优先信息被丢弃 | Critical / 严重 | Block current flow or switch to conservative policy. / 阻断当前流程或切换保守策略。 |
| Runtime identity missing / 运行时身份缺失 | Critical / 严重 | Block and require runtime context repair. / 阻断并要求修复运行时上下文。 |
| Permission scope missing / 权限范围缺失 | Critical / 严重 | Block or safe-mode the workflow. / 阻断或进入安全模式。 |
| Cross-user, cross-tenant, or cross-project read attempt / 跨用户、跨租户或跨项目读取尝试 | Critical / 严重 | Reject read and record audit event. / 拒绝读取并记录审计事件。 |
| Error feedback dropped / 错误反馈被丢弃 | High / 高 | Promote error evidence and rerun triage. / 提升错误证据并重新分诊。 |
| Compression summary missing source index / 压缩摘要无来源索引 | High / 高 | Lower compression strength or keep raw excerpt. / 降低压缩强度或保留原文片段。 |
| Read handle invalid or unscoped / 读取入口失效或缺少作用域 | High / 高 | Remove handle and request repair. / 移除入口并请求修复。 |
| Budget pressure high-percentile anomaly / 预算压力高位值异常 | Medium / 中 | Rebalance L1/L2/L3 budget ratios. / 调整一级、二级、三级预算比例。 |
| Exposed-unused handles too many / 暴露但未使用入口过多 | Medium / 中 | Reduce read-handle exposure count. / 减少读取入口暴露数量。 |

## Feedback Writeback Rules / 反馈回填规则

Probe output should do not directly override L0 or permission rules. / 探针输出不应直接覆盖零级或权限规则。

- Immediate Writeback / 即时回填: Use for dropped L0, missing permission, unauthorized read handle, or dropped error feedback. Block or switch to conservative policy. / 用于零级被丢、权限缺失、读取入口越权或错误反馈被丢；处理方式是阻断或切换保守策略。
- Next-Run Writeback / 下一轮回填: Use for ordinary priority, compression, read-handle, and recall adjustments. Feed the result into the next triage run. / 用于普通优先级、压缩、读取入口和召回调整；作为下一轮分诊输入。
- Batch Writeback / 批量回填: Use for scene policy, budget ratio, candidate recall, compression template, and read-handle rule changes. Update policy versions after review. / 用于场景策略、预算比例、候选召回、压缩模板和读取入口规则调整；评审后更新策略版本。

## Minimum Standalone Run / 独立运行最小流程

Minimum input / 最小输入:

```yaml
current_task / 当前任务: ""
actual_context / 实际上下文: []
available_but_excluded_material / 可用但未进入的材料: []
final_result / 最终结果: ""
human_or_auto_score / 人工评分或自动评分: ""
```

Minimum output / 最小输出:

- Whether key material is missing. / 关键材料是否缺失。
- Whether context noise is too high. / 上下文噪声是否过高。
- Whether any material should be compressed. / 是否存在应压缩材料。
- Whether any material should become a deferred read handle. / 是否存在应延迟读取材料。
- Whether governance risk exists. / 是否存在治理风险。
- Next-run triage suggestions. / 下一轮分诊建议。

## Output Templates / 输出模板

Observation report template / 观测报告模板:

```yaml
Context Triage Observation Report / 上下文分诊观测报告:
  report_id / 报告标识: ""
  task_id / 任务标识: ""
  scene_type / 场景类型: ""
  policy_version / 策略版本: ""
  overall_judgment / 总体判断: ""
  triage_pressure / 分诊压力:
    budget_usage_rate / 预算使用率: ""
    dropped_count / 丢弃数量: ""
    deferred_read_count / 延迟读取数量: ""
    risk_judgment / 风险判断: ""
  critical_layer_completeness / 关键层完整性:
    highest_priority_complete / 最高优先信息是否完整: ""
    current_evidence_complete / 当前证据是否完整: ""
    error_feedback_complete / 错误反馈是否完整: ""
    runtime_boundary_complete / 运行时边界是否完整: ""
  context_quality / 上下文质量:
    high_signal_ratio / 高信号比例: ""
    evidence_coverage / 证据覆盖率: ""
    noise_issue / 噪声问题: ""
    conflict_issue / 冲突问题: ""
  compression_quality / 压缩质量:
    evidence_retention / 证据保留情况: ""
    source_index_retention / 来源索引保留情况: ""
    raw_reread_needed / 是否需要回读原文: ""
    compression_risk / 压缩风险: ""
  read_handle_health / 读取入口健康度:
    read_success / 读取成功情况: ""
    scope_status / 作用域情况: ""
    contribution / 使用贡献: ""
    invalid_handles / 失效入口: []
  outcome_attribution / 结果归因:
    context_caused_failure / 是否因上下文导致失败: ""
    failure_reason / 失败原因: ""
    rework_status / 返工情况: ""
  suggestions / 建议:
    priority / 优先级建议: []
    compression / 压缩建议: []
    read_handle / 读取入口建议: []
    governance / 治理建议: []
```

Compression advice template / 压缩建议模板:

```yaml
Compression Advice / 压缩建议:
  item_id / 信息标识: ""
  source_type / 来源类型: ""
  suitable_for_compression / 是否适合压缩: ""
  recommended_strength / 建议压缩强度: ""
  must_keep_conclusions / 必须保留的结论: []
  must_keep_evidence / 必须保留的证据: []
  must_keep_source_index / 必须保留的来源索引: []
  forbidden_loss / 禁止丢失: []
  risk_notes / 风险提示: []
  recommended_actions / 建议动作:
    - enter_raw / 直接进入上下文
    - compress / 压缩后进入上下文
    - defer_read / 只保留读取入口
    - reject / 拒绝进入
```

Strategy feedback template / 策略反馈模板:

```yaml
Strategy Feedback / 策略反馈:
  feedback_id / 反馈标识: ""
  source_report / 来源报告: ""
  feedback_level / 反馈等级: ""
  applicable_scene / 适用场景: ""
  priority_up / 建议提升:
    - information_type / 信息类型: ""
      reason / 原因: ""
  priority_down / 建议降低:
    - information_type / 信息类型: ""
      reason / 原因: ""
  compression_adjustment / 建议压缩调整:
    - information_type / 信息类型: ""
      adjustment / 调整方式: ""
      reason / 原因: ""
  read_handle_adjustment / 建议读取入口调整:
    - handle_type / 入口类型: ""
      adjustment / 调整方式: ""
      reason / 原因: ""
  governance_adjustment / 建议治理调整:
    - rule / 规则: ""
      action / 动作: ""
      reason / 原因: ""
```
