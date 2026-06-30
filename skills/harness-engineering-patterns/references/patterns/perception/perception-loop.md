# Progressive Discovery / 渐进式发现

Cell / 交织点: perception-loop / 感知 x 循环
Capability / 能力: Perception / 感知
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850); user-supplied workflow draft / 用户提供的工作流草稿
Alias / 别名: Progressive Discovery Execution / 渐进发现的执行流程; Bounded Evidence Discovery / 有边界证据发现
Standalone Executable / 可独立执行: Yes / 是
Primary Axis / 主轴: Perception / 感知
Secondary Axes / 辅轴: Reasoning / 推理; Memory / 记忆; Governance / 治理
Primary Topology / 主拓扑: Loop / 循环
Secondary Topologies / 辅拓扑: Orchestration / 编排; Chain / 链式; Routing / 路由

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Progressive Discovery / 渐进式发现 is an evidence-seeking workflow for large or unfamiliar information spaces. It applies when relevant evidence exists somewhere in a repository, log set, document corpus, ticket history, contract set, paper collection, or mixed data space, but the executor does not know where it is and must not load everything into context at once. / 渐进式发现用于大型或陌生信息空间中的证据定位：相关证据存在于代码库、日志、文档库、工单、合同、论文或混合数据空间中，但执行者不知道具体位置，也不能一次性把全部内容放入上下文。

The operating principle is: do not load the whole information space at once / 不一次性加载整个信息空间; expand only when evidence justifies expansion / 只有证据支持扩展时才扩展. / 操作原则是：不全量读取，只在证据支持时扩展探索范围。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Perception / 感知 x Loop / 循环 (Loop / 循环).
- 论文依据 / Article Basis: 用户扩展模式 / User-extension pattern; arXiv:2605.13850 leaves this intersection as an 空白单元 / Empty cell, and this skill fills it only because repeated workflow evidence shows that perception needs bounded iterative discovery. / 用户扩展模式 / User-extension pattern；arXiv:2605.13850 将该交织点留为空白单元，本技能基于反复出现的工作流证据补入“有边界的循环式感知发现”。
- 问题 / Problem: The task-relevant evidence is hidden in a large information space, first-pass search results are only candidates, and loading all candidates pollutes context or exceeds budget. / 任务相关证据隐藏在大型信息空间中，第一次搜索结果只是候选，全部加载会污染上下文或超出预算。
- 架构方案 / Architectural Solution: Run a bounded loop of clarify -> trim -> broad scan -> focus -> deep dive -> verify -> stop or restart with sharper clues. / 执行有边界循环：澄清 -> 裁剪 -> 广扫 -> 聚焦 -> 深挖 -> 验证 -> 停止或带着更准线索重启。
- 工程权衡 / Engineering Trade-offs: The loop improves recall, evidence quality, and context hygiene, but it requires explicit budgets, stop rules, and trace records to avoid endless search. / 循环提升召回、证据质量和上下文卫生，但必须有预算、停止规则和追踪记录，否则会变成无尽搜索。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when a workflow must gradually locate high-signal evidence in an unknown information space. / 当工作流必须在未知信息空间中逐步定位高信号证据时使用。

### Execution Contract / 执行契约

- Trigger / 触发条件: Run when the task asks for evidence, root cause, risk, link understanding, or local context, and the relevant location is unknown. / 当任务需要证据、根因、风险、链路理解或局部上下文，但相关位置未知时执行。
- Objective / 目标: Find enough trustworthy evidence within a bounded budget, while preserving the exploration path, confidence, unresolved gaps, and next actions. / 在有限预算内找到足够可信证据，同时保留探索路径、置信度、缺口和后续动作。
- Scope / 范围: clarify the task, trim the search space, scan cheaply, rank candidates, inspect high-value regions, verify hypotheses, and output an evidence chain. / 澄清任务、裁剪搜索空间、低成本广扫、排序候选、检查高价值区域、验证假设，并输出证据链。
- Stop Rule / 停止规则: Stop when evidence supports the conclusion, new signal declines, the loop or budget limit is reached, permission or data is missing, or the task goal is satisfied. / 当证据足以支撑结论、新信号下降、达到轮次或预算上限、缺少权限或数据、任务目标已满足时停止。
- Escalation Rule / 升级规则: Escalate when the conclusion remains low confidence, required data is inaccessible, the risk is high, or the next expansion would exceed the approved boundary. / 当结论仍低置信、关键数据不可访问、风险高，或下一步扩展会越过批准边界时升级。
- Output / 输出: Progressive Discovery Result / 渐进发现结果 with conclusion, evidence chain, exploration path, confidence, unresolved issues, next actions, and trace-ready events. / 输出包含结论、证据链、探索路径、置信度、未解决问题、后续动作和可写入 Trace 的事件。

### Problem Framing / 问题定位

Use this pattern only after confirming the problem is a discovery problem rather than a direct reading problem. / 先确认这是发现问题，而不是直接阅读问题。

| Question / 问题 | Use Progressive Discovery When / 使用条件 | Prefer Another Pattern When / 改用其他模式 |
|---|---|---|
| Location known? / 位置是否已知 | The relevant location is unknown or only partially known. / 相关位置未知或只知道一部分。 | The user gave the exact file, paragraph, record, or dataset. / 用户已经给出精确文件、段落、记录或数据集。 |
| Context size safe? / 上下文是否安全 | Full loading would exceed budget or introduce noise. / 全量加载会超预算或引入噪声。 | All relevant material is already in context. / 相关材料已经在上下文中。 |
| Evidence needed? / 是否需要证据 | The answer must cite sources, paths, logs, records, clauses, or examples. / 答案需要引用来源、路径、日志、记录、条款或样例。 | The task is open-ended ideation, translation, or style rewrite. / 任务是开放创意、翻译或风格改写。 |
| Search enough? / 搜索是否足够 | Search results are noisy candidates that need ranking and verification. / 搜索结果是有噪声候选，需要排序和验证。 | One stable lookup directly answers the task. / 一次稳定查询即可回答。 |

### Search Space Trimming / 搜索空间裁剪

Trim before scanning. Trimming limits the first discovery round; it does not permanently discard information. / 先裁剪再广扫。裁剪只限定第一轮探索范围，不永久丢弃信息。

| Information Space / 信息空间 | First Trimming Boundary / 第一轮裁剪边界 |
|---|---|
| Codebase / 代码库 | directories, modules, languages, error strings, recent changes, tests. / 目录、模块、语言、错误字符串、近期变更、测试。 |
| Logs / 日志库 | alert time window, service, instance, request id, error code, deployment event. / 告警时间窗、服务、实例、请求 ID、错误码、部署事件。 |
| Documents / 文档库 | titles, sections, summaries, metadata, known entities, recent versions. / 标题、章节、摘要、元数据、已知实体、近期版本。 |
| Contracts / 合同库 | liability, fee, breach, termination, data, security, exception clauses. / 责任、费用、违约、终止、数据、安全、例外条款。 |
| Papers / 论文库 | research question, method, experiment, dataset, metric, conclusion, citation chain. / 研究问题、方法、实验、数据集、指标、结论、引用链。 |
| Tickets / 工单库 | customer, product, version, error description, time range, similar cases. / 客户、产品、版本、错误描述、时间范围、相似案例。 |
| Business chain / 业务链路 | entry system, downstream service, state flow, data flow, permission flow, failure point. / 入口系统、下游服务、状态流、数据流、权限流、失败点。 |

### Input Contract / 输入契约

Minimum inputs / 最小输入:

```yaml
task_description / 任务描述: ""
information_space / 信息空间: ""
output_requirement / 输出要求: conclusion | evidence_chain | candidate_list | root_cause_hypothesis | handoff_note
```

Recommended inputs / 推荐输入:

```yaml
target_type / 目标类型: locate_issue | find_evidence | understand_link | identify_risk | synthesize_material
initial_clues / 初始线索:
  keywords / 关键词: []
  errors / 错误信息: []
  time_points / 时间点: []
  modules_or_entities / 模块或实体: []
constraints / 约束条件:
  time_budget / 时间预算: ""
  context_budget / 上下文预算: ""
  permission_boundary / 权限边界: ""
  privacy_rules / 隐私要求: []
  allowed_tools / 允许工具: []
loop_limits / 循环限制:
  max_rounds / 最大轮次: 3
  max_deep_dive_paths / 最大深挖主线: 2
  max_dependency_depth / 最大追踪深度: 2
```

### Output Contract / 输出契约

Progressive Discovery Result / 渐进发现结果:

```yaml
conclusion / 结论: ""
evidence_chain / 证据链:
  - evidence_id / 证据编号: ""
    source_location / 来源位置: ""
    evidence_content / 证据内容: ""
    proves_or_disproves / 证明作用: ""
exploration_path / 探索路径:
  broad_scan / 广扫: []
  focus / 聚焦: []
  deep_dive / 深挖: []
  verification / 验证: []
confidence / 置信度: high | medium | low
unresolved_issues / 未解决问题: []
next_actions / 后续动作: []
stop_reason / 停止原因: ""
trace_events / Trace 事件: []
```

### Core Objects / 核心对象

Task Profile / 任务画像:

```yaml
Task Profile / 任务画像:
  task_id / 任务编号: ""
  task_type / 任务类型: ""
  information_space / 信息空间: ""
  initial_clues / 初始线索: []
  search_boundary / 搜索范围: []
  constraints / 约束条件: {}
  output_requirement / 输出要求: ""
  max_rounds / 最大轮次: 3
  per_round_budget / 单轮预算: ""
```

Discovery Candidate / 发现候选:

```yaml
Discovery Candidate / 发现候选:
  candidate_id / 候选编号: ""
  candidate_type / 候选类型: file | log | record | clause | paper_section | ticket | service | table
  source_location / 来源位置: ""
  matched_snippet / 命中片段: ""
  match_reason / 命中原因: ""
  region / 所属区域: ""
  initial_relevance / 初始相关度: high | medium | low
  estimated_cost / 成本估计: ""
  selected_for_focus / 是否进入聚焦: false
  exclusion_reason / 排除原因: ""
```

Discovery Event / 探索事件:

```yaml
Discovery Event / 探索事件:
  event_id / 事件编号: ""
  round / 所属轮次: 1
  stage / 所属阶段: clarify | trim | broad_scan | focus | deep_dive | verify
  clues_used / 使用线索: []
  operation_type / 操作类型: ""
  input_count / 输入数量: 0
  output_count / 输出数量: 0
  selected_count / 选中数量: 0
  decision_reason / 决策原因: ""
  cost / 成本: ""
  elapsed / 耗时: ""
  next_stage / 下一阶段: ""
```

Evidence Item / 证据项:

```yaml
Evidence Item / 证据项:
  evidence_id / 证据编号: ""
  source_location / 来源位置: ""
  content / 证据内容: ""
  related_hypothesis / 关联假设: ""
  proof_role / 证明作用: support | refute | narrow | contextualize
  confidence / 可信度: high | medium | low
  verified / 是否已验证: false
  counterexample_status / 反例状态: unchecked | none_found | found
```

Discovery Session / 探索会话:

```yaml
Discovery Session / 探索会话:
  session_id / 会话编号: ""
  task_profile / 任务画像: {}
  discovery_events / 探索事件: []
  candidates / 候选对象: []
  evidence_chain / 证据链: []
  current_hypotheses / 当前假设: []
  final_conclusion / 最终结论: ""
  confidence / 置信度: high | medium | low
  stop_reason / 停止原因: ""
```

### Discovery Stages / 发现阶段

| Stage / 阶段 | Goal / 目标 | Actions / 动作 | Exit / 出口 |
|---|---|---|---|
| Clarify / 任务澄清 | Turn a vague request into an executable discovery task. / 将模糊请求转成可执行发现任务。 | identify task type, target object, initial clues, boundaries, budget, stop rules. / 识别任务类型、目标对象、初始线索、边界、预算和停止规则。 | Task Profile / 任务画像 is complete. / 任务画像完整。 |
| Trim / 搜索空间裁剪 | Define the first exploration boundary. / 定义第一轮探索边界。 | choose relevant spaces, time windows, modules, sections, entities, tools. / 选择相关空间、时间窗、模块、章节、实体和工具。 | Boundary is narrow enough to scan cheaply. / 边界足以低成本广扫。 |
| Broad Scan / 广扫 | Gather low-cost clues without deep reading. / 用低成本方式收集线索。 | keyword search, path scan, title scan, metadata search, time-window search, symbol search, summary retrieval. / 关键词、路径、标题、元数据、时间窗、符号和摘要检索。 | Candidate count is reasonable or a strong hit appears. / 候选数量合理或出现强命中。 |
| Focus / 聚焦 | Select high-value regions for inspection. / 选择高价值区域精读。 | rank, deduplicate, cluster, group, inspect a few candidates, form hypotheses. / 排序、去重、聚类、分组、少量精读、形成假设。 | A strong clue or hypothesis needs deeper evidence. / 出现强线索或需深证据的假设。 |
| Deep Dive / 深挖 | Follow the strongest line to support or refute a hypothesis. / 沿最强主线支撑或推翻假设。 | inspect callers, dependencies, configs, tests, timelines, clauses, related records, citation details. / 检查调用方、依赖、配置、测试、时间线、条款、相关记录和引用细节。 | Evidence chain is near complete or the path stops producing signal. / 证据链接近完整或路径不再产出信号。 |
| Verify / 验证 | Avoid mistaking correlation for cause. / 避免把相关性误作因果。 | check counterexamples, boundary conditions, timeline, upstream/downstream consistency, stale data, reproducibility, missing permissions. / 检查反例、边界条件、时间线、上下游一致性、过期数据、可复现性和权限缺口。 | Conclusion is accepted, repaired, restarted, or escalated. / 结论被采纳、修复、重启或升级。 |

### Execution Procedure / 执行流程

1. Build Task Profile / 建立任务画像: classify the task, target type, information space, output requirement, risks, boundaries, and loop limits. / 分类任务、目标类型、信息空间、输出要求、风险、边界和循环限制。
2. Trim first search space / 裁剪第一轮搜索空间: choose the smallest useful region based on clues, metadata, time, ownership, or known entities. / 根据线索、元数据、时间、归属或已知实体选择最小可用区域。
3. Broad Scan / 广扫: use cheap scans only; collect titles, paths, hit lines, timestamps, object names, summaries, and short snippets. / 只做低成本扫描，收集标题、路径、命中行、时间戳、对象名、摘要和短片段。
4. Build Discovery Candidates / 建立发现候选: assign candidate id, source, match reason, region, relevance, cost, and exclusion state. / 标注候选编号、来源、命中原因、区域、相关度、成本和排除状态。
5. Focus / 聚焦: rank and cluster candidates, then read only the strongest regions needed to create or reject first hypotheses. / 对候选排序和聚类，只精读足以形成或排除初步假设的最强区域。
6. Deep Dive / 深挖: follow at most 1 to 2 main lines, default no more than 2 dependency hops, and stop any path that does not produce new evidence. / 最多追踪 1 到 2 条主线，默认不超过 2 跳依赖，无新证据的路径立即停止。
7. Verify / 验证: check counterexamples, time order, upstream/downstream consistency, configuration, permission, environment, and reproducibility. / 检查反例、时间顺序、上下游一致性、配置、权限、环境和可复现性。
8. Decide next loop / 判断下一轮: stop, repair evidence, restart Broad Scan / 广扫 with sharper clues, or escalate. / 停止、修复证据、带更准线索重新广扫或升级。
9. Emit result / 输出结果: produce Progressive Discovery Result / 渐进发现结果 and write trace-ready Discovery Events / 探索事件. / 输出渐进发现结果，并准备可写入 Trace 的探索事件。

### Loop Rules / 循环规则

- Maximum rounds / 最大轮次: default 2 to 3; raise only with explicit budget or high-value evidence. / 默认 2 到 3 轮；只有明确预算或高价值证据时才提高。
- Per-round change requirement / 单轮变化要求: each loop must improve keywords, narrow scope, cluster candidates, clarify hypotheses, strengthen evidence, or reduce counterexamples. / 每轮必须让关键词更准、范围更窄、候选更集中、假设更清楚、证据更强或反例更少。
- No-signal rule / 无信号规则: stop or escalate after 1 to 2 consecutive loops without new signal. / 连续 1 到 2 轮无新信号后停止或升级。
- Context hygiene / 上下文卫生: candidates are not context; only high-value snippets, summaries, and evidence handles enter working context. / 候选不等于上下文；只有高价值片段、摘要和证据句柄进入工作上下文。
- Boundary rule / 边界规则: do not inspect unrelated external dependencies, stale examples, private data, or large files unless they directly test the current hypothesis. / 除非直接验证当前假设，否则不检查无关外部依赖、过期示例、隐私数据或大文件。

### Stop and Escalation Rules / 停止与升级规则

Stop Rule / 停止规则:

- Evidence chain supports the conclusion. / 证据链足以支撑结论。
- A credible root cause or explanation is found. / 已找到可信根因或解释。
- Further exploration has low marginal value. / 继续探索的边际价值很低。
- Max rounds, time, context, or tool budget is reached. / 达到最大轮次、时间、上下文或工具预算。
- The goal is satisfied by a candidate list or handoff note rather than final proof. / 目标只需要候选清单或交接说明，不需要最终证明。

Escalation Rule / 升级规则:

- Required data or permission is missing. / 缺少必要数据或权限。
- The risk is high and evidence remains incomplete. / 风险高且证据仍不完整。
- Strong candidates conflict and cannot be resolved inside budget. / 强候选互相冲突且预算内无法解决。
- Verification finds a serious counterexample. / 验证发现严重反例。
- Next step would require production action, private data, or external owner approval. / 下一步需要生产动作、隐私数据或外部负责人批准。

### Quality Gate / 质量门禁

Quality Gate Result / 质量门禁结果:

```yaml
quality_gate_result / 质量门禁结果:
  status / 状态: pass | repair | restart | escalate
  evidence_chain_complete / 证据链完整: true
  counterexamples_checked / 反例已检查: true
  source_locations_present / 来源位置完整: true
  context_budget_respected / 上下文预算已遵守: true
  stop_reason_recorded / 停止原因已记录: true
  trace_events_ready / Trace 事件已就绪: true
  repair_actions / 修复动作: []
```

Must-pass checks / 必过检查:

- The conclusion is backed by source locations, not just memory. / 结论有来源位置支撑，而不只是凭记忆。
- Candidate ranking explains why selected regions were read and why others were deferred. / 候选排序说明为什么读取某些区域、延迟其他区域。
- Deep dive stayed inside the declared path and depth limit. / 深挖没有越过声明的主线和深度限制。
- Verification checked at least one counterexample, alternative explanation, or boundary condition when available. / 有条件时至少检查一个反例、替代解释或边界条件。
- Stop or escalation reason is explicit. / 停止或升级原因明确。

### Scenario Adaptation / 场景适配层

| Scenario / 场景 | Discovery Emphasis / 发现重点 | Verification Focus / 验证重点 |
|---|---|---|
| Codebase issue location / 陌生代码库问题定位 | error strings, function names, call paths, config, tests, recent commits. / 错误字符串、函数名、调用路径、配置、测试、近期提交。 | failing test, repro path, permissions, cache, concurrency, boundary condition. / 失败测试、复现路径、权限、缓存、并发、边界条件。 |
| Incident log root cause / 事故日志根因排查 | time window, service, instance, request chain, error codes, deployment event. / 时间窗、服务、实例、请求链路、错误码、部署事件。 | timeline, upstream/downstream consistency, resource metrics, config changes. / 时间线、上下游一致性、资源指标、配置变更。 |
| Contract risk identification / 合同风险识别 | liability, fee, breach, termination, data, security, exceptions, definitions. / 责任、费用、违约、终止、数据、安全、例外、定义。 | clause conflict, exception scope, defined terms, enforceability risk. / 条款冲突、例外范围、定义术语、可执行风险。 |
| Paper evidence search / 论文资料证据查找 | research question, method, dataset, metric, experiment, result, limitations. / 研究问题、方法、数据集、指标、实验、结果、局限性。 | whether claims are supported by method and experiment. / 结论是否被方法和实验支持。 |
| Ticket context tracking / 客户工单上下文追踪 | customer, product, version, error, history, similar cases, resolution feedback. / 客户、产品、版本、错误、历史、相似案例、解决反馈。 | applicability to current customer and version. / 是否适用于当前客户和版本。 |
| Cross-system business chain / 跨系统业务链路分析 | entry system, service interfaces, tables, events, state transitions, failure branch. / 入口系统、服务接口、表、事件、状态转换、失败分支。 | data consistency and state consistency across systems. / 跨系统数据一致性和状态一致性。 |

### Probe Interaction / 探针交互

This design pattern can run independently. A workflow observability probe may sit beside it to record events and recommend tuning, but the probe does not replace the discovery loop. / 本设计模式可以独立执行。工作流可观测性探针可以旁路记录事件并给出调优建议，但不替代发现循环。

Execution flow -> probe / 执行流程到探针:

- Discovery Event / 探索事件
- Discovery Candidate / 发现候选
- Evidence Item / 证据项
- stage decision / 阶段决策
- cost and latency / 成本与耗时
- stop, restart, or escalation reason / 停止、重启或升级原因

Probe -> execution flow / 探针到执行流程:

- keyword suggestions / 关键词建议
- search-boundary suggestions / 搜索范围建议
- candidate ranking suggestions / 候选排序建议
- budget risk / 预算风险
- stop or rollback recommendation / 停止或回退建议
- missing evidence hints / 缺失证据提示

### Evaluation / 评估方式

- Evidence precision / 证据精度: selected evidence supports or refutes the final conclusion. / 被选证据能支撑或推翻最终结论。
- Candidate noise ratio / 候选噪声率: broad scan candidates do not overwhelm focus. / 广扫候选不会压垮聚焦阶段。
- Discovery efficiency / 发现效率: useful evidence per search, tool call, or time unit. / 每次搜索、工具调用或单位时间带来的有效证据。
- Context pollution rate / 上下文污染率: irrelevant content entering working context. / 无关内容进入工作上下文的比例。
- Verification coverage / 验证覆盖率: counterexamples, timelines, and boundary conditions checked. / 反例、时间线和边界条件检查覆盖率。
- Trace completeness / Trace 完整度: events, candidates, evidence, decisions, and stop reasons are recorded. / 事件、候选、证据、决策和停止原因均被记录。

### Failure Modes / 常见失败模式

| Failure Mode / 失败模式 | Symptom / 表现 | Handling / 处理 |
|---|---|---|
| Search too broad / 搜索过宽 | Too many candidates and high noise. / 候选过多且噪声很高。 | Re-trim scope and use more specific clues. / 重新裁剪范围，使用更具体线索。 |
| Search too narrow / 搜索过窄 | Too few candidates or no useful signal. / 候选太少或无有效信号。 | Add synonyms, upstream/downstream terms, or adjacent regions. / 增加同义词、上下游词或相邻区域。 |
| Wrong focus / 聚焦错误 | Detailed reading targets low-value material. / 精读落在低价值材料。 | Re-rank by entity, time, core path, and multi-clue agreement. / 按实体、时间、核心路径和多线索一致性重新排序。 |
| Deep dive runaway / 深挖失控 | The path drifts into unrelated dependencies. / 路径漂到无关依赖。 | Enforce max path count, max depth, and current-hypothesis relevance. / 强制主线数量、深度和当前假设相关性。 |
| Evidence gap / 证据不足 | There is a guess but no source-backed proof. / 有猜测但无来源证据。 | Return to Broad Scan / 广扫 or escalate for missing data. / 回到广扫或为缺失数据升级。 |
| Premature conclusion / 结论过早 | The first plausible hit becomes final answer. / 第一个貌似合理的命中被当成最终答案。 | Require Verify / 验证 before stop. / 停止前必须验证。 |
| Context pollution / 上下文污染 | Noisy material crowds out key evidence. / 噪声材料挤占关键证据。 | Keep summaries, source handles, and selected evidence only. / 只保留摘要、来源句柄和已选证据。 |
| Endless loop / 循环过多 | Cost rises without better evidence. / 成本上升但证据没有变强。 | Apply no-signal rule, stop, or escalate. / 执行无信号规则，停止或升级。 |

### Done Criteria / 完成标准

- Task Profile / 任务画像 includes task type, information space, first boundary, output requirement, budget, and stop rules. / 任务画像包含任务类型、信息空间、第一轮边界、输出要求、预算和停止规则。
- Broad Scan / 广扫 produced a candidate list with source locations and match reasons. / 广扫产出带来源位置和命中原因的候选列表。
- Focus / 聚焦 selected high-value regions and documented why other candidates were deferred or excluded. / 聚焦选择了高价值区域，并记录其他候选为何延迟或排除。
- Deep Dive / 深挖 stayed within declared path and depth boundaries. / 深挖保持在声明主线和深度边界内。
- Verify / 验证 checked counterexamples, alternatives, timeline, or boundary conditions where available. / 有条件时验证反例、替代解释、时间线或边界条件。
- Progressive Discovery Result / 渐进发现结果 includes conclusion, evidence chain, exploration path, confidence, unresolved issues, next actions, and stop reason. / 渐进发现结果包含结论、证据链、探索路径、置信度、未解决问题、后续动作和停止原因。
- Quality Gate Result / 质量门禁结果 is pass, repaired, restarted, or escalated. / 质量门禁结果为通过、已修复、已重启或已升级。
- Trace entry can be written with events, candidates, evidence, decisions, costs, and outcome. / 可写入包含事件、候选、证据、决策、成本和结果的 Trace。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Progressive Discovery / 渐进式发现; Progressive Discovery Execution / 渐进发现的执行流程.
- 诊断用途 / Diagnostic Use: Use when a workflow must gradually locate high-signal evidence in an unknown information space. / 当工作流必须在未知信息空间中逐步定位高信号证据时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 上下文感知、问题拆解、方案设计、验证测试、运行监控、事故修复、知识沉淀、协作交接 / Context sensing, decomposition, design, verification, monitoring, incident repair, knowledge memory, collaboration handoff.
- 当前症状 / Current Symptoms: The relevant location is unknown, initial search is noisy, full context loading is unsafe, or evidence must be found with budget limits. / 相关位置未知、初始搜索噪声大、全量加载不安全，或必须在预算内寻找证据。
- 适配信号 / Fit Signals: The workflow needs iterative sensing, candidate filtering, focused reading, evidence verification, and explicit stop or escalation decisions. / 工作流需要循环感知、候选过滤、聚焦阅读、证据验证，以及明确停止或升级决策。
- 调整方向 / Adjustment Direction: Insert a bounded discovery loop before reasoning, implementation, repair, or handoff consumes uncertain context. / 在推理、实现、修复或交接消耗不确定上下文前，插入有边界发现循环。
- 修改方式 / How To Modify: Add task profile, search trimming, broad scan, candidate ranking, focused deep dive, verification, loop limits, quality gate, and trace events. / 增加任务画像、搜索裁剪、广扫、候选排序、聚焦深挖、验证、循环限制、质量门禁和 Trace 事件。
- 输入 / Inputs: task description, information space, output requirement, initial clues, constraints, budgets, loop limits, and optional probe signals. / 任务描述、信息空间、输出要求、初始线索、约束、预算、循环限制和可选探针信号。
- 输出 / Outputs: Progressive Discovery Result / 渐进发现结果, evidence chain, exploration path, confidence, unresolved issues, next actions, quality gate result, and trace-ready events. / 渐进发现结果、证据链、探索路径、置信度、未解决问题、后续动作、质量门禁结果和可写入 Trace 的事件。
- 风险与治理 / Risks & Governance: Bound search scope, protect private data, preserve source handles, record decisions, enforce stop rules, and escalate high-risk or low-confidence conclusions. / 约束搜索范围、保护隐私数据、保留来源句柄、记录决策、执行停止规则，并升级高风险或低置信结论。

Observability Metrics File / 可观测性指标文件: [perception-loop-observability.md](perception-loop-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. Record task type, information space, loop count, search boundary, candidate counts, selected regions, evidence items, verification result, stop or escalation reason, cost, confidence, and outcome. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。记录任务类型、信息空间、循环次数、搜索边界、候选数量、入选区域、证据项、验证结果、停止或升级原因、成本、置信度和结果。
