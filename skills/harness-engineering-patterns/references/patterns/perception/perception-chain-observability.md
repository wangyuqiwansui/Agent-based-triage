# Semantic Compaction / 语义压缩 Observability Metrics / 可观测性指标

Cell / 交织点: perception-chain / 感知 x 链式
Capability / 能力: Perception / 感知
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Alias / 别名: Semantic Compression Probe / 语义压缩的工作流可观测性探针
Standalone Executable / 可独立执行: Yes / 是
Primary Axes / 主轴: Governance / 治理; Reflection / 反思
Secondary Axes / 辅轴: Perception / 感知; Memory / 记忆
Primary Topology / 主拓扑: Parallel / 并行
Secondary Topologies / 辅拓扑: Chain / 链式; Loop / 循环; Orchestration / 编排

Use this file as the observability metrics and probe protocol source for Semantic Compaction / 语义压缩. / 将本文档作为语义压缩的可观测性指标与探针协议来源。
Design Pattern File / 设计模式文件: [perception-chain.md](perception-chain.md)

## Quick Navigation / 快速导航

- [Probe Role / 探针定位](#probe-role--探针定位)
- [Probe Input Contract / 探针输入契约](#probe-input-contract--探针输入契约)
- [Core Objects / 核心对象](#core-objects--核心对象)
- [Probe Execution Procedure / 探针执行流程](#probe-execution-procedure--探针执行流程)
- [Observability Metrics / 可观测性指标](#observability-metrics--可观测性指标)
- [Quality Gate / 质量门禁](#quality-gate--质量门禁)
- [Minimum Standalone Run / 独立运行最小版本](#minimum-standalone-run--独立运行最小版本)
- [Interaction Data Interface / 交互数据接口](#interaction-data-interface--与执行流程交互的数据接口)

## Probe Role / 探针定位

Probe does not compress / 探针不压缩. It observes the workflow, fills missing runtime data, produces compression advice, and checks quality after compression. / 探针不直接压缩、不删除历史、不改写上下文；它观察工作流、补全运行数据、生成压缩建议，并在压缩后执行质量检查。

The probe answers / 探针回答:

- Does the current workflow need compression? / 当前工作流是否需要压缩？
- Where does context growth come from? / 上下文膨胀来自哪里？
- Which items are key evidence? / 哪些信息是关键证据？
- Which errors or failed attempts must not be lost? / 哪些错误或失败记录不能丢？
- What is missing from the working memory anchor? / 工作记忆锚点缺少什么？
- Are repeated attempts or repeated tool calls appearing? / 是否存在重复尝试或重复调用？
- Which compression level should be selected? / 应该选择哪一级压缩？
- Did the result pass the quality gate after compression? / 压缩后是否通过质量门禁？
- Is handoff or a new session needed? / 是否需要交接或开启新会话？

## Mounting Guidance / 框架挂载建议

| Role / 角色 | Axis or Topology / 轴或拓扑 | Reason / 理由 |
|---|---|---|
| Primary capability / 主能力 | Governance / 治理 | The probe owns metrics, audit, alerting, quality gates, and replay evidence. / 探针负责指标、审计、告警、质量门禁和回放证据。 |
| Primary capability / 主能力 | Reflection / 反思 | The probe evaluates whether behavior degrades after compression. / 探针判断压缩后工作流是否退化。 |
| Supporting capability / 辅助能力 | Perception / 感知 | The probe decides what should remain visible or protected. / 探针判断哪些信息应被看见和保留。 |
| Supporting capability / 辅助能力 | Memory / 记忆 | The probe evaluates working memory anchor completeness. / 探针评估工作记忆锚点是否完整。 |
| Primary topology / 主拓扑 | Parallel / 并行 | The probe can observe beside the main workflow without blocking it. / 探针可旁路观察主工作流，不阻塞原流程。 |
| Supporting topology / 辅助拓扑 | Chain / 链式 | Probe work proceeds through collection, normalization, evidence extraction, metrics, advice, and gate. / 探针内部按采集、标准化、抽证据、算指标、出建议和门禁推进。 |
| Supporting topology / 辅助拓扑 | Loop / 循环 | Quality failures create repair loops. / 质量失败会触发修复循环。 |
| Supporting topology / 辅助拓扑 | Orchestration / 编排 | Production use coordinates execution flow, policy, storage, handles, and handoff. / 生产环境需要协调执行流程、策略层、存储层、句柄和交接。 |

## Relationship with Execution Flow / 与执行流程的关系

Independent sidecar mode / 独立旁路模式:

```text
Existing workflow / 现有工作流
  -> Copy execution trace / 复制执行轨迹
  -> Probe analysis / 探针分析
  -> Observability report / 可观测性报告
  -> Compression strategy advice / 压缩策略建议
```

Interactive mode / 交互模式:

```text
Before compression: probe emits metrics and advice / 压缩前：探针生成指标和建议
  -> Semantic compaction executes / 语义压缩流程执行
  -> After compression: probe runs quality gate / 压缩后：探针执行质量门禁
  -> Pass, repair, or handoff / 通过、修复或交接
```

In interactive mode, full reports stay in monitoring and audit systems while the execution flow receives only a short control block. / 交互运行时，完整报告进入监控和审计系统，执行流程只接收短控制块。

## Scenario Adaptation / 场景适配层

Keep the probe generic; put scene-specific thresholds and evidence types in the adapter. / 保持探针通用性，把场景阈值和证据类型放入适配层。

```yaml
scene_adapter / 场景适配:
  scene_name / 场景名称: ""
  risk_level / 风险等级: low | medium | high
  main_sources / 主要信息来源: []
  key_evidence_types / 关键证据类型: []
  compressible_information_types / 可压缩信息类型: []
  non_droppable_information_types / 不可丢失信息类型: []
  metric_thresholds / 指标阈值: {}
  alert_levels / 告警等级: {}
  privacy_masking_rules / 隐私与脱敏要求: []
  handoff_required / 交接要求: false
  evaluation_focus / 评估重点: []
```

Scene examples / 场景示例:

| Scene / 场景 | Main Evidence / 主要证据 | Focus Metrics / 重点指标 | Compression Advice / 压缩建议 |
|---|---|---|---|
| Long-document research / 长文档研究 | Source locations, conclusions, research goal, open questions. / 来源位置、关键结论、研究目标、未解决问题。 | Source traceability, conclusion drift risk, working memory completeness. / 来源回溯率、结论漂移风险、工作记忆完整度。 | Compress repeated background; preserve source handles. / 重复背景优先压缩，来源句柄必须保留。 |
| Debugging / 错误排查 | Error type, key numbers, paths, failing tests, failed paths. / 错误类型、关键数字、位置路径、失败测试、已失败方案。 | Error evidence retention, key number retention, repeated failed action rate. / 错误证据保留率、关键数字保留率、重复失败动作率。 | Mask normal redundant output; strongly protect error evidence. / 正常冗余输出可遮蔽，错误证据强保护。 |
| Content production / 内容生产 | Style preference, accepted version, forbidden expression, revision direction. / 风格偏好、已确认版本、禁止表达、修改方向。 | Preference retention, version continuity, user correction rate. / 用户偏好保留率、版本连续性、用户纠正率。 | Summarize old drafts; preserve explicit prohibitions. / 旧草稿可摘要，明确禁止项必须保留。 |

## Probe Input Contract / 探针输入契约

Required input / 必需输入:

```yaml
workflow_trace / 工作流执行轨迹: []
session_id / 当前会话编号: ""
event_sequence / 事件序列: []
current_context_usage / 当前上下文占用: ""
working_memory_anchor / 当前工作记忆锚点: {}
scene_adapter / 场景适配配置: {}
```

Optional input / 可选输入:

```yaml
historical_compression_events / 历史压缩事件: []
tool_return_records / 工具返回记录: []
external_material_returns / 外部资料返回: []
error_records / 错误记录: []
test_results / 测试结果: []
user_correction_records / 用户纠正记录: []
human_handoff_records / 人工交接记录: []
source_handle_map / 原文句柄映射: {}
business_risk_level / 业务风险等级: ""
privacy_masking_rules / 隐私与脱敏规则: []
```

## Probe Output Contract / 探针输出契约

Minimum output / 最小输出:

```yaml
metric_snapshot / 指标快照: {}
observability_report / 可观测性报告: {}
key_evidence_list / 关键证据清单: []
working_memory_gaps / 工作记忆缺口: []
compression_advice / 压缩建议: {}
quality_gate_result / 质量门禁结果: {}
alert_events / 告警事件: []
audit_references / 审计引用: []
```

Control block for interactive execution / 交互运行控制块:

```yaml
control_block / 控制块:
  recommended_compression_level / 建议压缩级别: ""
  trigger_reason / 触发原因: ""
  must_keep_items / 必须保留项: []
  maskable_items / 可遮蔽项: []
  working_memory_repairs / 工作记忆修复项: []
  source_handle_requirements / 原文句柄要求: []
  handoff_needed / 是否需要交接: false
  risk_level / 风险等级: ""
```

## Core Objects / 核心对象

Workflow Event / 工作流事件:

```yaml
Workflow Event / 工作流事件:
  event_id / 事件编号: ""
  session_id / 会话编号: ""
  step_id / 步骤编号: ""
  event_type / 事件类型: user_input | agent_reply | tool_call | tool_return | error | decision | memory_update | compression | handoff
  source_role / 来源角色: ""
  content_ref / 内容引用: ""
  content_fingerprint / 内容指纹: ""
  token_size / 占用大小: 0
  tool_name / 工具名称: ""
  action_name / 动作名称: ""
  status / 状态: ""
  tags / 标签: []
  timestamp / 时间: ""
  extra / 附加信息: {}
```

Evidence Item / 证据项:

```yaml
Evidence Item / 证据项:
  evidence_id / 证据编号: ""
  source_event / 来源事件: ""
  evidence_type / 证据类型: error | key_number | path | failing_test | user_constraint | decision_basis | excluded_path | citation | next_plan
  content / 证据内容: ""
  severity / 严重性: high | medium | low
  must_keep / 是否必须保留: true
  fingerprint / 证据指纹: ""
  source_handle / 原文句柄: ""
```

Metric Snapshot / 指标快照:

```yaml
Metric Snapshot / 指标快照:
  snapshot_id / 快照编号: ""
  session_id / 会话编号: ""
  step_id / 步骤编号: ""
  runtime_health / 运行健康指标: {}
  compression_effect / 压缩效果指标: {}
  evidence_protection / 证据保护指标: {}
  working_memory / 工作记忆指标: {}
  behavior_degradation / 行为退化指标: {}
  cost / 成本指标: {}
  governance_audit / 治理审计指标: {}
  risk_level / 风险等级: ""
  generated_at / 生成时间: ""
```

Compression Advice / 压缩建议:

```yaml
Compression Advice / 压缩建议:
  advice_id / 建议编号: ""
  based_on_snapshot / 基于哪个指标快照: ""
  recommended_compression_level / 建议压缩级别: ""
  trigger_reason / 触发原因: ""
  must_keep_items / 必须保留项: []
  maskable_items / 可遮蔽项: []
  working_memory_repairs / 工作记忆修复项: []
  source_handle_requirements / 原文句柄要求: []
  handoff_needed / 是否需要交接: false
  risk_level / 风险等级: ""
  confidence / 置信度: ""
  rationale / 理由: ""
```

Quality Gate Result / 质量门禁结果:

```yaml
Quality Gate Result / 质量门禁结果:
  gate_id / 门禁编号: ""
  related_compression_event / 关联压缩事件: ""
  passed / 是否通过: false
  failed_rules / 失败规则: []
  repair_actions / 修复动作: []
  risk_level / 风险等级: ""
  generated_at / 生成时间: ""
```

## Probe Execution Procedure / 探针执行流程

1. Read scene adapter / 读取场景适配配置: confirm risk, evidence types, compression thresholds, alert rules, and handoff requirements. / 确认风险、证据类型、压缩阈值、告警规则和交接要求。
2. Collect workflow events / 采集工作流事件: gather user input, agent replies, tool calls, tool returns, errors, decisions, memory updates, compression events, and handoffs. / 采集用户输入、智能体回复、工具调用、工具返回、错误、决策、记忆更新、压缩事件和交接。
3. Normalize events / 标准化事件: fill event id, session id, step id, content reference, fingerprint, token size, time, and tags. / 补齐事件编号、会话编号、步骤编号、内容引用、指纹、占用、时间和标签。
4. Classify events / 分类事件类型: action, return, error, evidence, decision, working memory, compression, handoff, and noise. / 分为动作、返回、错误、证据、决策、工作记忆、压缩、交接和噪声。
5. Extract key evidence / 抽取关键证据: error type, key number, path, failing test, user constraint, decision basis, failed path, citation, and next plan. / 抽取错误类型、关键数字、位置路径、失败测试、用户强约束、决策依据、已失败方案、来源引用和下一步计划。
6. Calculate metrics / 计算指标: runtime health, evidence protection, working memory, behavior degradation, cost, and governance. / 计算运行健康、证据保护、工作记忆、行为退化、成本和治理指标。
7. Assess risk / 评估风险: decide whether compression is needed, evidence is under-protected, memory is incomplete, repeated attempts appear, handoff is needed, or aggressive compression is forbidden. / 判断是否需要压缩、证据保护是否不足、记忆是否缺字段、是否重复试错、是否需要交接、是否禁止激进压缩。
8. Generate compression advice / 生成压缩建议: name the level, must-keep items, maskable items, memory repairs, handle requirements, and handoff need. / 明确压缩级别、必须保留项、可遮蔽项、记忆修复项、句柄要求和交接需要。
9. Run quality gate after compression / 压缩后执行质量门禁: verify evidence, working memory, failed paths, source handles, repeated-attempt risk, repair need, and handoff need. / 检查证据、工作记忆、已失败方案、原文句柄、重复尝试风险、修复需要和交接需要。
10. Record audit data / 记录审计数据: metric snapshots, evidence fingerprints, memory changes, advice, gate result, alerts, and handle mappings. / 记录指标快照、证据指纹、工作记忆变化、压缩建议、门禁结果、告警和句柄映射。

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Semantic Compaction / 语义压缩 protects evidence, preserves working memory, reduces context pressure, and avoids behavior degradation. / 使用以下指标观察语义压缩是否保护证据、保留工作记忆、降低上下文压力，并避免行为退化。

- 质量指标 / Quality Metrics:
  - Evidence Retention Rate / 证据保留率: Share of required evidence preserved after compression. / 压缩后必需证据被保留的比例。
  - Error Evidence Retention Rate / 错误证据保留率: Share of error evidence preserved with type, key number, path, and handle. / 错误证据保留错误类型、关键数字、位置和句柄的比例。
  - Working Memory Completeness / 工作记忆完整度: Coverage of user goal, actions, judgments, excluded paths, next plan, evidence references, and open questions. / 用户目标、动作、判断、排除方案、下一步、证据引用和未决问题的覆盖度。
  - Handoff Summary Completeness / 交接摘要完整度: Completeness of handoff summary when L3 or handoff is triggered. / 进入第三级或触发交接时，交接摘要的完整度。
- 时延指标 / Latency Metrics:
  - Probe Processing Latency / 探针处理耗时: Time spent collecting events, extracting evidence, calculating metrics, and producing advice. / 采集事件、抽取证据、计算指标和生成建议的耗时。
  - Compression Gate Latency / 压缩门禁耗时: Time from compression output to quality gate result. / 从压缩输出到质量门禁结果的耗时。
  - Source Handle Retrieval Latency / 原文句柄回溯时延: Time needed to retrieve source material from handles. / 通过原文句柄回溯材料的耗时。
- 成本指标 / Cost Metrics:
  - Probe Token Footprint / 探针自身占用: Tokens or context budget consumed by probe output. / 探针输出占用的 Token 或上下文预算。
  - Compression Savings / 压缩节省量: Context units saved by semantic compaction. / 语义压缩节省的上下文占用。
  - Compression Benefit Ratio / 压缩收益比: Saved context and reduced rework compared with probe and compression cost. / 节省上下文和减少返工相对于探针与压缩成本的收益。
  - Trace Storage Cost / Trace 存储成本: Storage cost of snapshots, evidence fingerprints, and handle mappings. / 指标快照、证据指纹和句柄映射的存储成本。
- 风险指标 / Risk Metrics:
  - Critical Error Loss Count / 关键错误丢失数: Count of required critical errors missing after compression. / 压缩后缺失的关键错误数量。
  - Source Handle Traceability Rate / 原文句柄可回溯率: Share of protected items whose handles can retrieve the source material. / 受保护项目中可通过句柄回溯原文的比例。
  - Repeated Failed Action Rate After Compression / 压缩后重复失败动作率: Share of failed actions repeated after compression. / 压缩后重复已失败动作的比例。
  - Semantic Drift Risk / 语义漂移风险: Risk that compressed memory changes goal, judgment, evidence, or next plan. / 压缩记忆改变目标、判断、证据或下一步计划的风险。
- Trace 指标 / Trace Metrics:
  - Compression Event Record Coverage / 压缩事件记录覆盖率: Share of compression runs with complete event records. / 压缩运行中具备完整事件记录的比例。
  - Evidence Fingerprint Coverage / 证据指纹记录覆盖率: Share of evidence items with stable fingerprints. / 具备稳定指纹的证据项比例。
  - Working Memory Change Coverage / 工作记忆变化记录覆盖率: Share of anchor changes captured in trace. / 工作记忆锚点变更被 Trace 捕获的比例。
  - Audit Reference Coverage / 审计引用覆盖率: Share of reports and advice linked to source events, snapshots, and handles. / 报告和建议关联来源事件、指标快照和句柄的比例。

## Metric System / 指标体系

| Family / 类别 | Core Metrics / 核心指标 | Purpose / 用途 |
|---|---|---|
| Runtime Health Metrics / 运行健康指标 | Context usage rate / 上下文占用率; session turn count / 会话轮次数; tool-return occupancy ratio / 工具返回占用比例; external-material occupancy ratio / 外部资料占用比例; compression trigger count / 压缩触发次数; L1/L2/L3 trigger rate / 第一级、第二级、第三级压缩触发率; repeated L3 trigger rate / 第三级重复触发率. | Locate context growth and detect late, frequent, or handoff-level compression. / 定位上下文膨胀来源，并判断是否压得太晚、太频繁或需要交接。 |
| Compression Effect Metrics / 压缩效果指标 | Compression ratio / 压缩比; average compression ratio / 平均压缩比; over-compression rate / 过度压缩率; under-compression rate / 压缩不足率; saved occupancy / 节省占用量; compression latency / 压缩耗时; Compression Benefit Ratio / 压缩收益比. | Judge whether compression is useful, too strong, too weak, or too expensive. / 判断压缩是否有用、过强、过弱或成本过高。 |
| Evidence Protection Metrics / 证据保护指标 | Evidence retention rate / 证据保留率; error evidence retention rate / 错误证据保留率; Critical Error Loss Count / 关键错误丢失数; key number retention rate / 关键数字保留率; path retention rate / 位置路径保留率; source handle coverage / 原文句柄覆盖率; Source Handle Traceability Rate / 原文句柄可回溯率; evidence fingerprint coverage / 证据指纹覆盖率. | This is the most important metric group; it protects reasoning and auditability. / 这是最重要的指标组，用于保护推理与审计能力。 |
| Working Memory Metrics / 工作记忆指标 | Working Memory Completeness / 工作记忆完整度; memory staleness / 工作记忆陈旧度; memory update frequency / 工作记忆更新频率; memory conflict count / 工作记忆冲突数; excluded path missing rate / 已排除方案缺失率; next plan executability / 下一步计划可执行度; evidence reference coverage / 证据引用覆盖率. | Check whether the anchor still carries task state. / 检查锚点是否仍承载任务状态。 |
| Behavior Degradation Metrics / 行为退化指标 | Post-compression task success rate / 压缩后任务成功率; repeated action rate / 压缩后重复动作率; Repeated Failed Action Rate After Compression / 压缩后重复失败动作率; tool retry rate after compression / 压缩后工具重试率; user correction rate after compression / 压缩后用户纠正率; judgment reversal count / 判断反转次数; goal drift count / 目标偏移次数; semantic drift risk / 语义漂移风险. | Detect whether the agent forgot important state after compression. / 判断智能体是否在压缩后忘记关键状态。 |
| Cost Metrics / 成本指标 | Probe processing latency / 探针处理耗时; probe token footprint / 探针自身占用; saved occupancy / 压缩节省量; compression benefit ratio / 压缩收益比; storage occupancy / 存储占用; retrieval cost / 回溯成本. | Decide whether the probe and compression flow are worth running. / 判断探针和压缩流程本身是否值得运行。 |
| Governance Audit Metrics / 治理审计指标 | Compression event record coverage / 压缩事件记录覆盖率; working memory change coverage / 工作记忆变化记录覆盖率; evidence fingerprint coverage / 证据指纹记录覆盖率; untraceable summary rate / 不可追溯摘要率; dropped content category count / 丢弃内容类别数; policy violation count / 策略违规数; handoff summary completeness / 交接摘要完整度. | Support replay, audit, review, and governance. / 支持复盘、审计、回放和治理。 |

## Compression Advice Control Block / 压缩建议控制块

Full metrics go to monitoring and audit; short Control Block / 控制块 goes to the semantic compaction flow. / 完整指标进入监控和审计系统，短控制块进入语义压缩流程。

```yaml
Compression Control Block / 压缩控制块:
  recommended_compression_level / 建议压缩级别: "L2 / 第二级"
  trigger_reason / 触发原因: "High context usage and large tool returns / 上下文占用较高，工具返回占用过大"
  evidence_risk / 证据风险: high
  working_memory_risk / 工作记忆风险: medium
  must_keep / 必须保留:
    - error_type / 错误类型
    - key_numbers / 关键数字
    - paths / 位置路径
    - failing_tests / 失败测试
    - current_judgments / 已形成判断
    - excluded_paths / 已排除方案
    - next_plan / 下一步计划
  maskable / 可以遮蔽:
    - old_non_key_returns / 旧的非关键返回
    - repeated_output / 重复输出
    - large_raw_material / 大块原始资料
    - confirmed_irrelevant_background / 已确认无关的背景信息
  must_attach_handles / 必须挂句柄:
    - raw_error_record / 原始错误记录
    - long_logs / 长日志
    - full_material_returns / 完整资料返回
    - full_test_results / 完整测试结果
  working_memory_repairs / 工作记忆修复:
    - add_excluded_paths / 补充已排除方案
    - update_next_plan / 更新下一步计划
    - add_evidence_references / 补充证据引用
  quality_gate / 质量门禁:
    - critical_error_loss_count_is_zero / 关键错误丢失数为零
    - working_memory_completeness_reaches_threshold / 工作记忆完整度达到阈值
    - source_handle_coverage_reaches_threshold / 原文句柄覆盖率达到阈值
```

## Quality Gate / 质量门禁

Hard rules / 硬性规则:

- Critical Error Loss Count / 关键错误丢失数 must be zero. / 关键错误丢失数必须为零。
- Must-keep evidence must have body or source handle. / 必须保留证据必须有正文或句柄。
- Working Memory Completeness / 工作记忆完整度 must reach the scene threshold. / 工作记忆完整度不得低于场景阈值。
- If failed attempts exist, excluded paths must not be empty. / 存在失败尝试时，已排除方案不能为空。
- L3 compression must produce Handoff Summary / 交接摘要. / 第三级压缩必须生成交接摘要。
- High-risk scenes forbid aggressive compression without handles. / 高风险场景禁止无句柄激进压缩。

Conditional rules / 条件规则:

- If error evidence exists, preserve error type, key number, path, and handle. / 如果错误证据存在，必须保留错误类型、关键数字、位置路径和原文句柄。
- If tool returns dominate usage, recommend masking old non-key returns. / 如果工具返回占用过高，建议遮蔽旧的非关键返回。
- If next plan is missing, repair working memory before compression. / 如果工作记忆缺失下一步计划，先修复再压缩。
- If repeated failed action rate rises, force excluded-path repair. / 如果重复失败动作率升高，强制补充已排除方案。
- If handoff is required, output Handoff Summary / 交接摘要. / 如果存在交接要求，必须输出交接摘要。

Failure actions / 失败后的动作:

- Evidence repair / 证据修复
- Working memory repair / 工作记忆修复
- Lower compression level / 降低压缩级别
- Restore raw excerpt / 恢复原文片段
- Add source handle / 补充原文句柄
- Generate handoff summary / 生成交接摘要
- Human confirmation / 转人工确认
- Start new session / 开启新会话

## Sidecar Report Format / 旁路报告格式

When running beside an existing workflow, output a report instead of a control block. / 旁路运行时输出报告，而不是控制块。

```yaml
Sidecar Observability Report / 旁路可观测性报告:
  report_id / 报告编号: ""
  session_id / 会话编号: ""
  workflow_name / 工作流名称: ""
  overall_risk_level / 总体风险等级: ""
  main_findings / 主要发现: []
  context_hotspots / 上下文热点: []
  evidence_risk / 证据风险: ""
  working_memory_gaps / 工作记忆缺口: []
  repeated_attempt_risk / 重复尝试风险: ""
  handoff_risk / 交接风险: ""
  recommended_compression_strategy / 建议压缩策略: ""
  metric_snapshot_ref / 指标快照引用: ""
  audit_ref / 审计引用: ""
```

Example conclusion / 示例结论:

```text
The workflow has clear context growth from tool returns and repeated material.
Key evidence is partly identified, but source-handle coverage is weak.
The working memory anchor lacks excluded paths, creating repeated-attempt risk after compression.
Recommended action: run L1 cleanup now, repair the anchor before L2, attach handles to all key evidence, and generate handoff if L3 triggers again.
```

## Alert Rules / 告警规则

Highest priority alerts / 最高优先级告警:

- Critical Error Loss Count / 关键错误丢失数 > 0.
- Source handle cannot retrieve original material. / 原文句柄不可回溯。
- High-risk scene lacks Handoff Summary / 高风险场景缺少交接摘要。
- Repeated Failed Action Rate After Compression / 压缩后重复失败动作率 rises sharply.

High priority alerts / 高优先级告警:

- Repeated L3 trigger rate is too high. / 第三级重复触发率过高。
- Working Memory Completeness / 工作记忆完整度 is below threshold.
- Excluded path missing rate is too high. / 已排除方案缺失率过高。
- Over-compression rate is too high. / 过度压缩率过高。

Trend alerts / 趋势观察告警:

- Under-compression rate keeps rising. / 压缩不足率持续升高。
- Probe processing cost is too high. / 探针处理成本过高。
- Old return reopen rate is too high. / 旧返回重新打开率过高。
- User correction rate rises. / 用户纠正率上升。

## Minimum Standalone Run / 独立运行最小版本

Minimum capabilities / 最小能力:

- Event collection / 事件采集
- Event classification / 事件分类
- Evidence extraction / 证据抽取
- Metric calculation / 指标计算
- Compression advice / 压缩建议
- Quality gate / 质量门禁
- Report output / 报告输出

Minimum metrics / 最小指标:

- Context Usage Rate / 上下文占用率
- Tool Return Occupancy Ratio / 工具返回占用比例
- Compression Ratio / 压缩比
- Error Evidence Retention Rate / 错误证据保留率
- Critical Error Loss Count / 关键错误丢失数
- Source Handle Coverage / 原文句柄覆盖率
- Working Memory Completeness / 工作记忆完整度
- Excluded Path Missing Rate / 已排除方案缺失率
- Repeated Failed Action Rate After Compression / 压缩后重复失败动作率
- L3 Trigger Rate / 第三级触发率

Minimum gate / 最小门禁:

- Critical Error Loss Count / 关键错误丢失数 is zero.
- Source Handle Coverage / 原文句柄覆盖率 reaches threshold.
- Working Memory Completeness / 工作记忆完整度 reaches threshold.
- If failed attempts exist, excluded paths are not empty. / 存在失败尝试时已排除方案不能为空。

## Interaction Data Interface / 与执行流程交互的数据接口

Probe sends to semantic compaction / 探针向语义压缩执行流程补全:

- Context Usage Rate / 上下文占用率
- Information Hotspot Distribution / 信息热点分布
- Recommended Compression Level / 建议压缩级别
- Error Evidence List / 错误证据清单
- Key Number List / 关键数字清单
- Path and Location List / 位置路径清单
- Failed Attempt List / 失败尝试清单
- Excluded Path Gap / 已排除方案缺口
- Working Memory Completeness / 工作记忆完整度
- Must-Keep Items / 必须保留项
- Maskable Items / 可以遮蔽项
- Must-Attach-Handle Items / 必须挂句柄项
- Quality Gate Rules / 质量门禁规则
- Handoff Advice / 交接建议

Semantic compaction returns to probe / 语义压缩执行流程向探针回传:

- Actual Compression Level / 实际压缩级别
- Before and After Context Usage / 压缩前后占用
- Updated Working Memory Anchor / 更新后的工作记忆锚点
- Preserved Evidence List / 保留证据清单
- Masked Content Categories / 遮蔽内容类别
- Source Handle List / 原文句柄清单
- Compression Event Record / 压缩事件记录
- Quality Gate Input / 质量门禁输入

Closed loop / 闭环:

```text
Probe fills data / 探针补数
  -> Execution flow compresses / 执行流程压缩
  -> Probe checks / 探针检查
  -> Execution flow repairs / 执行流程修复
  -> Continue observing / 继续观察
```

## Evaluation / 评估方式

Offline evaluation / 离线评估:

- Historical session replay / 历史会话回放
- Key evidence recall test / 关键证据召回测试
- Working memory completeness test / 工作记忆完整度测试
- Repeated failed action test / 重复失败动作测试
- Handoff summary quality test / 交接摘要质量测试
- Semantic drift test / 语义漂移测试

Online evaluation / 在线评估:

- Post-compression task success rate / 压缩后任务成功率
- User correction rate after compression / 压缩后用户纠正率
- Repeated Failed Action Rate After Compression / 压缩后重复失败动作率
- Source Handle Traceability Rate / 原文句柄可回溯率
- Human handoff acceptance rate / 人工交接接受率
- High-risk alert hit rate / 高风险告警命中率

Scenario weighting / 场景权重:

- Debugging: weight error evidence and repeated failed action higher. / 错误排查：错误证据和重复失败动作权重更高。
- Research: weight source traceability and conclusion stability higher. / 资料研究：来源回溯和结论稳定性权重更高。
- Content production: weight preference retention and version continuity higher. / 内容生产：偏好保留和版本连续性权重更高。
- Workflow approval: weight decision basis and state continuity higher. / 流程审批：决策依据和状态连续性权重更高。
- Support ticket: weight handoff summary and time-risk signals higher. / 客服工单：交接摘要和时效风险权重更高。

## Failure Modes / 常见失败模式

- Monitoring only context length and not evidence retention. / 只监控上下文长度，不监控证据保留。
- Putting the full metric report into the compression prompt and creating noise. / 把完整指标报告塞进压缩提示，反而制造噪声。
- Using one threshold set without scene adaptation. / 没有场景适配层，所有任务使用同一阈值。
- Reporting problems without executable compression advice. / 只输出报告，不输出可执行压缩建议。
- Observing before compression but skipping post-compression quality gate. / 只在压缩前观测，不在压缩后检查。
- Ignoring working memory anchor gaps. / 忽略工作记忆锚点缺口。
- Ignoring excluded failed paths. / 忽略已失败方案。
- Missing source handles and losing traceability. / 没有原文句柄，无法回溯。
- Continuing execution after quality gate failure. / 质量门禁失败后仍继续执行。
- Too many alerts without severity levels. / 告警过多但没有分级。

## Design Principles / 设计原则总结

- Probe does not compress; it observes, fills data, advises, and checks. / 探针不压缩，只观测、补数、建议和检查。
- Scene differences belong in the adapter, not the probe core. / 场景差异进入适配层，不写死在探针主流程。
- Full reports are for governance; short control blocks are for compression. / 完整报告用于治理，短控制块用于压缩。
- Evidence, working memory, and behavior degradation matter more than length alone. / 证据、工作记忆和行为退化比单纯长度更重要。
- Give advice before compression and run gates after compression. / 压缩前给建议，压缩后做门禁。
- Every key evidence item should trace to a source. / 每个关键证据都应能追溯到来源。
- L3 compression should trigger handoff judgment. / 第三级压缩应触发交接判断。
- The probe and execution flow can run independently or as a closed loop. / 探针和执行流程可以独立运行，也可以闭环运行。
