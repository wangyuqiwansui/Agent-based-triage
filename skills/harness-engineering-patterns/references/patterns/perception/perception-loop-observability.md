# Progressive Discovery / 渐进式发现 Observability Metrics / 可观测性指标

Cell / 交织点: perception-loop / 感知 x 循环
Capability / 能力: Perception / 感知
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850); user-supplied workflow draft / 用户提供的工作流草稿
Design Pattern File / 设计模式文件: [perception-loop.md](perception-loop.md)
Alias / 别名: Progressive Discovery Probe / 渐进发现的工作流可观测性探针
Standalone Executable / 可独立执行: Yes / 是

Use this file as the observability metrics and probe protocol source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标与探针协议来源。

## Quick Navigation / 快速导航

- [Probe Role / 探针定位](#probe-role--探针定位)
- [Probe Input Contract / 探针输入契约](#probe-input-contract--探针输入契约)
- [Observation Objects / 观测对象](#observation-objects--观测对象)
- [Observability Metrics / 可观测性指标](#observability-metrics--可观测性指标)
- [Diagnostic Rules / 诊断规则](#diagnostic-rules--诊断规则)
- [Probe Report Template / 探针报告模板](#probe-report-template--探针报告模板)
- [Minimum Standalone Run / 独立运行最小流程](#minimum-standalone-run--独立运行最小流程)
- [Interaction Data Interface / 交互数据接口](#interaction-data-interface--与执行流程交互的数据接口)

## Probe Role / 探针定位

Progressive Discovery Probe / 渐进发现的工作流可观测性探针 observes, records, diagnoses, and improves the discovery workflow. It answers whether a discovery run is healthy, where cost was wasted, where focus drifted, what evidence is missing, and how the next loop should improve. / 渐进发现的工作流可观测性探针负责观测、记录、诊断和改进发现流程，回答本次寻找是否健康、哪里浪费成本、哪里选错方向、哪些证据缺失、下一轮如何改进。

Probe does not search / 探针不负责寻找信息. Probe does not directly provide the final business answer / 探针不直接给最终业务答案. It observes the workflow and returns metrics, diagnoses, and feedback. / 探针不替代执行流程，不直接给业务结论，只返回指标、诊断和回填建议。

## Relationship with Execution Flow / 与执行流程的关系

The execution flow answers "how to find information"; the probe answers "whether the finding process is healthy." / 执行流程回答“如何找到信息”，探针回答“寻找过程是否健康”。

| Direction / 方向 | Data / 数据 | Purpose / 目的 |
|---|---|---|
| Execution -> Probe / 执行流程到探针 | task profile, stage events, candidates, selected objects, evidence, costs, final result. / 任务画像、阶段事件、候选、选中对象、证据、成本、最终结果。 | Build the observation record. / 建立观测记录。 |
| Probe -> Execution / 探针到执行流程 | keyword suggestions, search boundary suggestions, ranking suggestions, rollback, stop, or escalation advice. / 关键词建议、搜索范围建议、排序建议、回退、停止或升级建议。 | Improve the current or next discovery loop. / 改进当前或下一轮发现。 |

## Operating Modes / 运行模式

| Mode / 模式 | Use When / 适用场景 | Output / 输出 |
|---|---|---|
| Sidecar Observation Mode / 旁路观测模式 | Evaluate existing or historical discovery work without changing execution. / 不改变执行结果，只评估现有或历史发现过程。 | health report, failure statistics, optimization advice. / 健康报告、失败统计、优化建议。 |
| Online Assistance Mode / 联机辅助模式 | Runtime cost is high, candidates are noisy, or stop and rollback decisions need support. / 运行成本高、候选噪声大，或需要辅助判断停止与回退。 | next-step advice, risk hints, rollback or stop recommendation. / 下一步建议、风险提示、回退或停止建议。 |
| Replay Evaluation Mode / 回放评测模式 | Compare keyword, ranking, boundary, or budget strategies on historical tasks. / 用历史任务比较关键词、排序、范围或预算策略。 | strategy comparison, success rate, cost comparison, miss analysis. / 策略对比、成功率、成本对比、漏选分析。 |

## Probe Input Contract / 探针输入契约

Minimum input / 最小输入:

```yaml
task_id / 任务编号: ""
task_description / 任务描述: ""
information_space_type / 信息空间类型: ""
stage_events / 阶段事件: []
final_result / 最终结果: {}
```

Recommended input / 推荐输入:

```yaml
task_profile / 任务画像:
  task_type / 任务类型: ""
  information_space / 信息空间: ""
  initial_keywords / 初始关键词: []
  search_boundary / 搜索范围: []
  output_requirement / 输出要求: ""
  constraints / 约束条件: {}
stage_event / 阶段事件:
  round / 所属轮次: 1
  stage / 所属阶段: clarify | trim | broad_scan | focus | deep_dive | verify | output
  clues_used / 使用线索: []
  operation_type / 操作类型: ""
  input_count / 输入数量: 0
  output_count / 输出数量: 0
  selected_count / 选中数量: 0
  selection_reason / 选中原因: ""
  exclusion_reason / 排除原因: ""
  cost / 成本: ""
  elapsed / 耗时: ""
  next_stage / 下一阶段: ""
  transition_reason / 阶段切换理由: ""
candidate / 候选对象:
  candidate_id / 候选编号: ""
  source_location / 来源位置: ""
  matched_snippet / 命中片段: ""
  match_reason / 命中原因: ""
  initial_relevance / 初始相关度: high | medium | low
  selected / 是否被选中: false
  exclusion_reason / 排除原因: ""
evidence_item / 证据项:
  evidence_id / 证据编号: ""
  source_location / 来源位置: ""
  related_hypothesis / 支撑的假设: ""
  verified / 是否被验证: false
  included_in_final_answer / 是否进入最终答案: false
final_result / 最终结果:
  conclusion / 结论: ""
  confidence / 置信度: high | medium | low
  stop_reason / 停止原因: ""
  success / 是否成功: false
```

## Probe Output Contract / 探针输出契约

Probe output must include numbers and interpretation. / 探针输出不仅要有数字，还要有解释。

```yaml
Probe Report / 探针报告:
  overall_judgment / 总体判断: healthy | warning | danger
  key_metrics / 关键指标: []
  stage_diagnostics / 阶段诊断: []
  failure_modes / 失败模式: []
  data_gaps / 数据缺口: []
  tuning_suggestions / 调优建议: []
  continue_discovery_recommended / 是否建议继续探索: false
  human_intervention_recommended / 是否建议人工介入: false
  writeback_data / 可回填给执行流程的数据: {}
Metric Snapshot / 指标快照:
  metric_name / 指标名称: ""
  value / 当前值: ""
  reference / 参考状态: ""
  judgment / 判断: healthy | warning | danger
Failure Diagnosis / 失败诊断:
  symptom / 现象: ""
  likely_cause / 可能原因: ""
  probe_advice / 探针建议: ""
  writeback / 回填给执行流程: {}
Feedback Advice / 回填建议:
  target / 回填目标: keyword | boundary | ranking | transition | evidence_gap | stop_rule
  advice / 建议内容: ""
  reason / 建议原因: ""
```

## Observation Objects / 观测对象

- Task Profile / 任务画像
- Search Space / 搜索空间
- Stage Event / 阶段事件
- Discovery Candidate / 发现候选
- Selected Object / 选中对象
- Tool Call / 工具调用
- Cost and Latency / 成本与耗时
- Stage Transition / 阶段切换
- Evidence Chain / 证据链
- Verification Result / 验证结果
- Stop Reason / 停止原因
- Human Feedback / 人工反馈

## Stage Observation / 阶段观测

Every stage must answer: did it do the right thing, did it produce useful data, and should it move to the next stage? / 每个阶段都要回答：是否做了该做的事、是否产生足够有用的数据、是否应该进入下一阶段。

| Stage / 阶段 | Observation Points / 观测点 | Common Probe Advice / 常见探针建议 |
|---|---|---|
| Clarify / 任务澄清 | goal clarity, information space, initial clues, output requirement, max rounds, budget, stop condition. / 目标、信息空间、初始线索、输出要求、最大轮次、预算、停止条件。 | complete task profile, suggest keywords, suggest first boundary, suggest stop rules. / 补全任务画像、建议关键词、第一轮范围和停止条件。 |
| Trim / 搜索空间裁剪 | whether trimming happened first, rationale quality, key-area coverage, mistaken exclusions. / 是否先裁剪、依据质量、关键区域覆盖、误排风险。 | expand or narrow boundary, add backup space, record trimming reason. / 扩大或收窄范围、加入备用范围、记录裁剪理由。 |
| Broad Scan / 广扫 | keyword specificity, candidate count, noise ratio, cluster concentration, hit reason recording, no full reading. / 关键词具体性、候选数量、噪声率、聚集度、命中原因、避免全量读取。 | narrow keywords, add synonyms, switch dimensions, cluster candidates, truncate low-value candidates. / 收窄关键词、扩展同义词、切换维度、聚类候选、截断低价值候选。 |
| Focus / 聚焦 | candidate ranking, selection reason, high-value region priority, miss risk, focus count. / 候选排序、入选原因、高价值区域优先、漏选风险、聚焦数量。 | adjust weights, increase core path and recent data weight, reduce duplicate and example weight. / 调整权重，提高核心路径与近期数据权重，降低重复和示例权重。 |
| Deep Dive / 深挖 | strongest-line tracking, depth boundary, no-signal steps, unrelated dependency drift, evidence chain. / 是否沿最强线索、追踪边界、无新信号、无关依赖漂移、证据链。 | stop current path, return to focus, limit depth, switch line, mark manual confirmation point. / 停止当前路径、回到聚焦、限制深度、切换主线、标记人工确认点。 |
| Verify / 验证 | counterexamples, boundary conditions, timeline, upstream/downstream consistency, correlation versus causality, confidence. / 反例、边界条件、时间线、上下游一致性、相关与因果、置信度。 | add counterexample checks, lower confidence, list alternatives, return to deep dive. / 补反例检查、降低置信度、列替代解释、返回深挖。 |
| Output / 输出 | conclusion, evidence chain, exploration path, unresolved issues, confidence, stop reason, next actions. / 结论、证据链、探索路径、未解决问题、置信度、停止原因、后续动作。 | complete output structure, add sources, add unresolved questions, adjust conclusion strength. / 补全输出结构、补来源、补未确认问题、调整结论强度。 |

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Progressive Discovery / 渐进式发现 improves a workflow after selection or application. / 使用以下指标观察 Progressive Discovery / 渐进式发现 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: Track evidence precision, selected candidate precision, evidence chain completeness, conclusion support, and user or reviewer acceptance. / 跟踪证据精度、选中候选精确率、证据链完整度、结论支撑度和用户或评审采纳情况。
- 时延指标 / Latency Metrics: Track time from task framing to first useful candidate, first verified evidence, final conclusion, and Probe Report / 探针报告. / 跟踪从任务定位到首个有效候选、首个已验证证据、最终结论和探针报告的耗时。
- 成本指标 / Cost Metrics: Track loop count, scan count, focus reads, deep-dive paths, tool calls, token or compute spend, and repeated search avoided. / 跟踪循环次数、扫描次数、精读数量、深挖主线、工具调用、Token 或计算成本，以及避免的重复搜索。
- 风险指标 / Risk Metrics: Track search-boundary violations, unsupported conclusions, missed stop rules, permission errors, stale sources, and sensitive information exposure. / 跟踪搜索边界违规、无证据结论、停止规则遗漏、权限错误、过期来源和敏感信息暴露。
- Trace 指标 / Trace Metrics: Track Trace Completeness / 轨迹完整度, Stage Transition Explainability / 阶段切换可解释率, Stop Reason Record Rate / 停止原因记录率, and follow-up closure. / 跟踪轨迹完整度、阶段切换可解释率、停止原因记录率和后续动作关闭情况。

## Metric System / 指标体系

### Efficiency Metrics / 效率指标

| Metric / 指标 | Meaning / 含义 | Warning / 预警 |
|---|---|---|
| Rounds To Signal / 成功所需轮数 | Average loops needed to find useful signal. / 找到有效信号平均需要几轮。 | Rising rounds show keyword, boundary, or ranking issues. / 轮数升高说明关键词、范围或排序可能有问题。 |
| Broad Scan To Focus Budget Ratio / 广扫与聚焦预算比 | Broad scan cost divided by focus cost. / 广扫成本除以聚焦成本。 | Too high means noisy broad scan; too low means insufficient scan. / 过高说明广扫噪声大，过低说明候选不足。 |
| Evidence Cost Per Item / 单次有效证据成本 | Cost required to obtain one useful evidence item. / 每条有效证据所需成本。 | High cost suggests ranking or deep-dive drift. / 成本高说明排序或深挖可能漂移。 |

### Search Quality Metrics / 搜索质量指标

| Metric / 指标 | Meaning / 含义 | Warning / 预警 |
|---|---|---|
| Zero Signal Rate / 零信号率 | Share of runs that produce no useful clue. / 一轮或多轮后没有有效线索的比例。 | May indicate wrong keyword, permission, stale index, or unavailable data. / 可能是关键词、权限、索引或数据源问题。 |
| Candidate Relevance Rate / 候选相关率 | Relevant candidates divided by all broad scan candidates. / 相关候选占广扫候选比例。 | Low rate means search is too broad or untrimmed. / 比例低说明搜索过宽或未裁剪。 |
| Candidate Coverage Rate / 候选覆盖率 | Whether broad scan covered the later-confirmed key area. / 广扫是否覆盖事后确认的关键区域。 | Low coverage means first boundary or keyword missed key areas. / 覆盖低说明第一轮范围或关键词遗漏。 |

### Focus Quality Metrics / 聚焦质量指标

| Metric / 指标 | Meaning / 含义 | Warning / 预警 |
|---|---|---|
| Selected Candidate Precision / 选中精确率 | Valuable selected candidates divided by selected candidates. / 真正有价值的选中候选占比。 | Low precision means ranking or region judgment is weak. / 精确率低说明排序或区域判断不足。 |
| High-Value Candidate Miss Rate / 高价值候选漏选率 | Important candidates missed during focus. / 重要候选未进入聚焦的比例。 | High miss rate means weights or domain features are incomplete. / 漏选率高说明权重或领域特征不足。 |
| Information Region Quality / 信息区域质量 | Whether the focused region can explain the task and supply verifiable evidence. / 聚焦区域是否能解释任务并提供可验证证据。 | Low quality means return to ranking or clustering. / 质量低应返回排序或聚类。 |

### Deep Dive Quality Metrics / 深挖质量指标

| Metric / 指标 | Meaning / 含义 | Warning / 预警 |
|---|---|---|
| Marginal Evidence Gain / 边际新增价值 | New useful evidence per deep-dive step. / 每一步深挖带来的新增有效证据。 | Falling or zero gain means stop, rollback, or switch line. / 持续下降或为零应停止、回退或换线。 |
| Invalid Trace Ratio / 无效追踪比例 | Share of deep-dive steps entering unrelated paths. / 深挖进入无关路径的比例。 | High ratio means missing boundary or weak stop rule. / 比例高说明边界或停止规则不足。 |
| Evidence Chain Completeness / 证据链完整度 | Whether evidence links phenomenon -> clue -> evidence -> conclusion -> verification. / 证据是否连接现象、线索、关键证据、结论和验证。 | Broken chain means mark gaps and search missing nodes. / 断裂则标记缺口并补查。 |

### Verification Quality Metrics / 验证质量指标

| Metric / 指标 | Meaning / 含义 | Warning / 预警 |
|---|---|---|
| Counterexample Check Rate / 反例检查率 | Whether final conclusions checked counterexamples or alternatives. / 最终结论是否检查反例或替代解释。 | Low rate causes premature conclusions. / 低检查率容易导致过早结论。 |
| Evidence Precision / 证据精确率 | Final evidence that truly supports the conclusion. / 最终证据中真正支撑结论的比例。 | Important tasks should target above 80%. / 重要任务建议高于 80%。 |
| Confidence Calibration / 置信度校准度 | Whether confidence matches evidence strength. / 置信度是否与证据强度匹配。 | Overconfidence or unexplained uncertainty needs repair. / 过度自信或不说明不确定性都需修复。 |

### Traceability Metrics / 可观测性指标

| Metric / 指标 | Meaning / 含义 | Required Record / 必需记录 |
|---|---|---|
| Trace Completeness / 轨迹完整度 | Whether key events are recorded. / 关键事件是否被记录。 | stage, keyword, input/output count, selected count, cost, elapsed, next stage, stop reason. / 阶段、关键词、输入输出数量、选中数量、成本、耗时、下一阶段、停止原因。 |
| Stage Transition Explainability / 阶段切换可解释率 | Whether stage changes have reasons. / 阶段切换是否有理由。 | broad scan -> focus, focus -> deep dive, deep dive -> verify. / 广扫到聚焦、聚焦到深挖、深挖到验证。 |
| Stop Reason Record Rate / 停止原因记录率 | Whether every stop explains why. / 每次停止是否说明原因。 | enough evidence, no new signal, budget reached, max rounds, permission missing, human intervention. / 证据足够、无新信号、达到预算、最大轮次、缺权限、人工介入。 |

### Governance Metrics / 治理指标

| Metric / 指标 | Meaning / 含义 | Governance Rule / 治理规则 |
|---|---|---|
| Permission Exception Rate / 权限异常率 | Discovery gaps caused by permission failure. / 因权限失败导致信息缺失的比例。 | Escalate instead of guessing. / 升级，不猜测。 |
| Stale Source Rate / 过期来源率 | Evidence based on outdated material, index, config, or document. / 使用过期材料、索引、配置或文档作为证据的比例。 | Mark freshness and verify before conclusion. / 标记新鲜度并验证。 |
| Sensitive Information Exposure Risk / 敏感信息暴露风险 | Whether probe records unnecessary sensitive raw content. / 探针是否记录不必要敏感原文。 | do not save unnecessary raw material; save reference, summary, structure, or metric first. / 不保存不必要原文，优先保存引用、摘要、结构化字段或指标。 |

## Health State / 健康状态判断

Healthy / 健康:

- Most tasks find useful signal in 1 to 2 loops. / 大多数任务 1 到 2 轮找到有效信号。
- Candidate count is moderate and selected candidates are relevant. / 候选数量适中，选中候选相关。
- Deep-dive paths are short and productive. / 深挖路径短且有效。
- Evidence chain is complete and verification includes counterexamples. / 证据链完整，验证包含反例检查。
- Output includes conclusion, evidence, confidence, stop reason, and next actions. / 输出包含结论、证据、置信度、停止原因和后续动作。

Warning / 预警:

- Rounds To Signal / 成功所需轮数 rises.
- Candidate counts swing widely. / 候选数量波动很大。
- Zero Signal Rate / 零信号率 rises.
- Focus often selects wrong objects. / 聚焦经常选错对象。
- Output often misses evidence chain or stop reason. / 输出经常缺证据链或停止原因。

Danger / 危险:

- Most tasks find no useful signal. / 多数任务找不到有效线索。
- Tool or permission failures are frequent. / 工具或权限失败频繁。
- Evidence chain is not traceable. / 证据链不可追溯。
- Costs keep rising without stronger evidence. / 成本持续上升但证据没有变强。
- Sensitive information is over-recorded. / 敏感信息被过度记录。

## Diagnostic Rules / 诊断规则

| Symptom / 现象 | Likely Cause / 可能原因 | Probe Advice / 探针建议 | Writeback / 回填给执行流程 |
|---|---|---|---|
| Too many candidates / 候选过多 | keywords too broad, search space not trimmed. / 关键词太宽、搜索空间未裁剪。 | narrow keywords, add path or time limits. / 收窄关键词，增加路径或时间限制。 | new keywords, new boundary. / 新关键词、新裁剪范围。 |
| Too few candidates / 候选过少 | keywords too narrow, insufficient initial clues. / 关键词太窄、初始线索不足。 | add synonyms, move to broader scope. / 扩展同义词，上移到更宽范围。 | expanded keywords, backup boundary. / 扩展关键词、备用范围。 |
| Zero signal rises / 零信号率升高 | tool, permission, index, or data source failure. / 工具、权限、索引或数据源异常。 | check tool and data freshness. / 检查工具和数据新鲜度。 | pause deep dive, switch source. / 暂停深挖，切换数据源。 |
| Wrong focus / 聚焦错误 | ranking weights are weak. / 排序权重不合理。 | adjust core path, recent data, production source weights. / 调整核心路径、近期数据、生产材料权重。 | new ranking weights. / 新排序权重。 |
| Runaway deep dive / 深挖失控 | missing tracking boundary. / 缺少追踪边界。 | limit depth and branch count. / 限制深度和分支数量。 | max tracking depth. / 最大追踪深度。 |
| Broken evidence chain / 证据链断裂 | missing intermediate evidence. / 中间证据缺失。 | mark missing nodes. / 标记缺失节点。 | supplemental search target. / 补充搜索目标。 |
| Premature conclusion / 结论过早 | no verification stage. / 没有验证阶段。 | require counterexample check. / 强制反例检查。 | return to Verify / 验证. |
| High cost / 成本过高 | too many loops or candidates. / 循环过多或候选过多。 | lower max rounds or candidate cap. / 降低最大轮次或候选上限。 | new budget strategy. / 新预算策略。 |
| Not reviewable / 输出不可复盘 | missing trace events. / 轨迹记录缺失。 | require stage event template. / 强制阶段事件模板。 | mandatory record schema. / 强制记录模板。 |

## Feedback Writeback Rules / 反馈回填规则

Keyword Suggestions / 关键词建议:

```yaml
Keyword Suggestions / 关键词建议:
  original_keywords / 原始关键词: []
  issue / 问题: too_broad | too_narrow | missing_domain_terms | missing_upstream_terms | missing_downstream_terms
  new_keywords / 新关键词: []
  excluded_keywords / 排除关键词: []
```

Search Boundary Suggestions / 搜索范围建议:

```yaml
Search Boundary Suggestions / 搜索范围建议:
  current_boundary / 当前范围: []
  risk / 风险: too_large | too_small | key_area_may_be_excluded
  suggested_boundary / 建议范围: []
  backup_boundary / 备用范围: []
```

Ranking Suggestions / 排序建议:

```yaml
Ranking Suggestions / 排序建议:
  current_ranking_issue / 当前排序问题: ""
  increase_weight / 应提高权重:
    - core_path / 核心路径
    - recent_data / 近期数据
    - main_chain_node / 主链路节点
    - production_material / 生产材料
    - high_trust_source / 高可信来源
  decrease_weight / 应降低权重:
    - example_content / 示例内容
    - duplicate_content / 重复内容
    - low_trust_source / 低可信来源
    - stale_material / 过期材料
```

Stage Transition Suggestions / 阶段切换建议:

```yaml
Stage Transition Suggestions / 阶段切换建议:
  current_stage / 当前阶段: ""
  current_state / 当前状态: healthy | warning | danger
  recommended_action / 建议动作: continue_current | next_stage | previous_stage | adjust_keywords | adjust_boundary | rerank | fill_evidence | stop | human_intervention
  reason / 理由: ""
```

Evidence Gap Suggestions / 证据缺口建议:

```yaml
Evidence Gap Suggestions / 证据缺口建议:
  current_conclusion / 当前结论: ""
  existing_evidence / 已有证据: []
  missing_evidence / 缺失证据: []
  needs_verification / 需要验证: []
  suggested_search_locations / 建议补查位置: []
```

Stop Suggestions / 停止建议:

```yaml
Stop Suggestions / 停止建议:
  stop_recommended / 是否建议停止: false
  stop_reason / 停止原因: enough_evidence | no_new_signal | budget_reached | max_rounds | human_intervention_needed
  confidence / 置信度: high | medium | low
  next_actions / 后续动作: []
```

## Scenario Adaptation / 场景适配层

| Scenario / 场景 | Priority Metrics / 重点指标 | Diagnostic Focus / 重点诊断 |
|---|---|---|
| Codebase / 代码库 | candidate file relevance, core path hit rate, production file priority, test file false selection, call chain completeness, recent commit hit rate, config coverage. / 候选文件相关率、核心路径命中率、生产文件优先率、测试文件误选率、调用链完整度、最近提交命中率、配置覆盖率。 | whether semantic search missed real call chain or drifted into third-party code. / 是否漏掉真实调用链或追入第三方代码。 |
| Incident logs / 事故日志 | time window coverage, abnormal log hit rate, request chain completeness, service association, deployment event association, Zero Signal Rate / 零信号率. / 时间窗覆盖、异常日志命中、请求链路完整、服务关联、部署事件关联、零信号率。 | whether concurrency was mistaken for cause or config changes were ignored. / 是否把并发现象误判为因果或忽略配置变更。 |
| Contract review / 合同审阅 | high-risk clause hit rate, clause reference completeness, definition coverage, party identification, exception miss rate. / 高风险条款命中、条款引用完整、定义覆盖、责任主体识别、例外漏检。 | whether definitions, exceptions, or clause conflicts were ignored. / 是否忽略定义、例外或条款冲突。 |
| Paper research / 论文资料 | method evidence coverage, experiment setup coverage, dataset recognition, metric recognition, limitation coverage, citation chain completeness. / 方法证据覆盖、实验设置覆盖、数据集识别、指标识别、局限性覆盖、引用链完整。 | whether author claims were treated as verified facts. / 是否把作者主张当作已验证事实。 |
| Support tickets / 工单支持 | similar ticket hit rate, same-customer history coverage, version match rate, resolution feedback availability, repeated issue recognition. / 相似工单命中、同客户历史覆盖、版本匹配、解决反馈可用、重复问题识别。 | whether old fixes were applied without checking version and customer fit. / 是否未检查版本和客户适配就套用旧方案。 |
| Business chain / 业务链路 | main chain coverage, upstream/downstream consistency, state transition completeness, interface hit rate, dataflow evidence completeness. / 主链路覆盖、上下游一致性、状态转换完整、接口命中、数据流证据完整。 | whether single-system evidence missed async links or downstream validation. / 是否只看单系统而漏异步链路或下游验证。 |

## Probe Report Template / 探针报告模板

```markdown
# Progressive Discovery Probe Report / 渐进发现工作流可观测性探针报告

## 1. Overall Judgment / 总体判断

healthy | warning | danger / 健康 | 预警 | 危险

## 2. Task Information / 任务信息

- Task Type / 任务类型:
- Information Space / 信息空间:
- Loop Count / 执行轮数:
- Final State / 最终状态:
- Stop Reason / 停止原因:

## 3. Core Metrics / 核心指标

| Metric / 指标 | Value / 当前值 | Reference / 参考状态 | Judgment / 判断 |
|---|---:|---|---|
| Rounds To Signal / 成功所需轮数 |  |  |  |
| Broad Scan To Focus Budget Ratio / 广扫与聚焦预算比 |  |  |  |
| Zero Signal Rate / 零信号率 |  |  |  |
| Candidate Relevance Rate / 候选相关率 |  |  |  |
| Selected Candidate Precision / 选中精确率 |  |  |  |
| Evidence Chain Completeness / 证据链完整度 |  |  |  |
| Trace Completeness / 轨迹完整度 |  |  |  |

## 4. Stage Diagnosis / 阶段诊断

List issues and advice for clarify, trim, broad scan, focus, deep dive, verify, and output. / 列出任务澄清、裁剪、广扫、聚焦、深挖、验证、输出阶段的问题和建议。

## 5. Failure Modes / 失败模式

List matched failure modes. / 列出命中的失败模式。

## 6. Data Gaps / 数据缺口

List missing data from the execution flow. / 列出执行流程缺失的数据。

## 7. Writeback Advice / 回填建议

Keywords, search boundary, ranking weights, stage transition, evidence gap, stop condition. / 关键词、搜索范围、排序权重、阶段切换、证据缺口、停止条件。

## 8. Continue Discovery / 是否建议继续探索

yes | no / 是 | 否

## 9. Human Intervention / 是否建议人工介入

yes | no / 是 | 否

## 10. Next Actions / 后续动作

Recommended next steps. / 推荐下一步。
```

## Minimum Standalone Run / 独立运行最小流程

Minimum capability / 最小能力:

- Receive Discovery Event / 接收探索事件
- Record candidate count and selected count / 记录候选数量和选中数量
- Record transition reason / 记录阶段切换原因
- Record cost and latency / 记录成本与耗时
- Record evidence chain / 记录证据链
- Calculate core metrics / 计算核心指标
- Detect common failure modes / 识别常见失败模式
- Output Probe Report / 输出探针报告

Minimum tables / 最小数据表:

```yaml
task_table / 任务表:
  task_id / 任务编号: ""
  task_type / 任务类型: ""
  information_space / 信息空间: ""
  start_time / 开始时间: ""
  end_time / 结束时间: ""
  final_state / 最终状态: ""
stage_event_table / 阶段事件表:
  task_id / 任务编号: ""
  round / 轮次: 1
  stage / 阶段: ""
  input_count / 输入数量: 0
  output_count / 输出数量: 0
  selected_count / 选中数量: 0
  cost / 成本: ""
  elapsed / 耗时: ""
  next_stage / 下一阶段: ""
  transition_reason / 切换原因: ""
candidate_table / 候选表:
  task_id / 任务编号: ""
  candidate_id / 候选编号: ""
  source_location / 来源位置: ""
  match_reason / 命中原因: ""
  selected / 是否选中: false
  exclusion_reason / 排除原因: ""
evidence_table / 证据表:
  task_id / 任务编号: ""
  evidence_id / 证据编号: ""
  source_location / 来源位置: ""
  related_hypothesis / 支撑假设: ""
  verified / 是否验证: false
  included_in_final_answer / 是否进入最终答案: false
metric_table / 指标表:
  task_id / 任务编号: ""
  metric_name / 指标名称: ""
  metric_value / 指标值: ""
  judgment / 判断: ""
```

## Governance Requirements / 治理要求

- Do not save unnecessary raw material / do not save unnecessary raw material. Save references, summaries, structured fields, metrics, and judgments first. / 不保存不必要原文，优先保存引用位置、摘要、结构化字段、指标和判断。
- Preserve reviewability / 保留可复盘性: record why the flow searched, selected, excluded, transitioned, and stopped. / 记录为什么搜索、为什么选中、为什么排除、为什么切换、为什么停止。
- Separate observation from intervention / 区分观测和干预: sidecar mode must not change execution; online assistance may advise, but adoption must be recorded. / 旁路模式不改变执行；联机辅助可建议，但必须记录是否采纳。
- Metrics do not replace judgment / metrics do not replace judgment. Interpret metrics by scenario, task risk, and available evidence. / 指标不能替代判断，必须结合场景、任务风险和可用证据解释。
- Respect permission and privacy boundaries. / 遵守权限和隐私边界。

## Anti-Patterns / 反模式

| Anti-Pattern / 反模式 | Problem / 问题 |
|---|---|
| Only inspect final answer / 只看最终答案 | Cannot know where exploration failed. / 无法知道探索过程哪里失败。 |
| Record tool calls but not stage reasons / 只记录工具调用，不记录阶段理由 | Decisions cannot be reviewed. / 无法复盘决策。 |
| Treat probe as executor / 把探针当执行器 | Responsibilities become confused. / 职责混乱。 |
| Save all raw content / 保存所有原始内容 | Raises privacy, cost, and context risk. / 增加隐私、成本和上下文风险。 |
| Use one threshold for every scene / 所有场景用同一阈值 | Metrics become misleading. / 指标失真。 |
| No human feedback loop / 没有人工反馈闭环 | Candidate and evidence quality cannot be calibrated. / 无法校准候选和证据质量。 |
| No stop reason / 没有停止原因 | Cannot distinguish success stop from failure stop. / 无法区分成功停止和失败停止。 |
| Probe output too long / 探针输出过长 | Creates new context pollution. / 造成新的上下文污染。 |

## Interaction Data Interface / 与执行流程交互的数据接口

Execution flow sends to probe / 执行流程发送给探针:

```yaml
stage_event / 阶段事件:
  task_id / 任务编号: ""
  current_round / 当前轮次: 1
  current_stage / 当前阶段: ""
  current_operation / 当前操作: ""
  clues_used / 使用线索: []
  search_boundary / 搜索范围: []
  input_count / 输入数量: 0
  output_count / 输出数量: 0
  selected_count / 选中数量: 0
  selection_reason / 选中原因: ""
  exclusion_reason / 排除原因: ""
  cost / 成本: ""
  elapsed / 耗时: ""
  current_hypothesis / 当前假设: ""
  next_stage / 下一阶段: ""
  transition_reason / 阶段切换理由: ""
```

Probe returns to execution flow / 探针返回给执行流程:

```yaml
probe_advice / 探针建议:
  current_state / 当前状态: healthy | warning | danger
  recommended_action / 建议动作:
    - continue_current_stage / 继续当前阶段
    - enter_next_stage / 进入下一阶段
    - return_previous_stage / 返回上一阶段
    - adjust_keywords / 调整关键词
    - adjust_search_boundary / 调整搜索范围
    - adjust_candidate_ranking / 调整候选排序
    - supplement_evidence / 补充证据
    - stop_discovery / 停止探索
    - human_intervention / 人工介入
  reason / 建议原因: ""
  writeback_data / 回填数据:
    keywords / 关键词: []
    search_boundary / 搜索范围: []
    ranking_weights / 排序权重: {}
    evidence_gaps / 证据缺口: []
    stop_condition / 停止条件: ""
```

## Minimum Checklist / 最小检查清单

- Task Profile / 任务画像 is recorded. / 已记录任务画像。
- Every stage event is recorded. / 已记录每个阶段事件。
- Candidate counts are recorded. / 已记录候选数量。
- Selection and exclusion reasons are recorded. / 已记录选中原因和排除原因。
- Stage transition reasons are recorded. / 已记录阶段切换原因。
- Cost and latency are recorded. / 已记录成本和耗时。
- Evidence chain is recorded. / 已记录证据链。
- Verification result is recorded. / 已记录验证结果。
- Stop reason is recorded. / 已记录停止原因。
- Core metrics are calculated. / 已计算核心指标。
- Failure diagnosis is output. / 已输出失败诊断。
- Feedback Advice / 回填建议 is provided. / 已给出回填建议。
