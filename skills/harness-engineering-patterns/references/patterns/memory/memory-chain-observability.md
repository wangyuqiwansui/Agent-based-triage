# RAG Pipeline / RAG 管线 Observability Metrics / 可观测性指标

Cell / 交织点: memory-chain / 记忆 x 链式
Capability / 能力: Memory / 记忆
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [memory-chain.md](memory-chain.md)

## Observability Metrics / 可观测性指标

### Probe Positioning / 探针定位

RAG Pipeline observability treats metrics as workflow probes, not as isolated dashboard values. / RAG 管线可观测性将指标视为工作流探针，而不是孤立看板数值。

```text
Metric / 指标：what is the value now? / 现在是多少？
Probe / 探针：where to observe, what to collect, how to judge, what to fill, and what to do next.
             在哪里看、采集什么、如何判断、补什么数、下一步怎么做。
```

A probe should return a decision that the workflow can consume: continue, retry, human review, block, or degraded output. / 探针应返回可被工作流消费的结论：继续、重试、转人工、阻断或降级输出。

### Standard Metric Groups / 标准指标分组

- 质量指标 / Quality Metrics: Track usable evidence rate, evidence contract completeness, grounded claim coverage, citation traceability, evidence adoption, and user correction or rework. / 跟踪可用证据率、证据契约完整率、接地结论覆盖率、引用可追率、证据采纳率，以及用户修正或返工情况。
- 时延指标 / Latency Metrics: Track retrieval latency p95, ranking latency, evidence validation time, output gate time, and total time from request to grounded answer. / 跟踪检索延迟 P95、排序延迟、证据校验耗时、输出门控耗时，以及从请求到扎根答案的总耗时。
- 成本指标 / Cost Metrics: Track tool calls, retrieval calls, rerank calls, context tokens, human review effort, and repeated retrieval avoided by better metadata. / 跟踪工具调用、检索调用、重排调用、上下文 token、人审投入，以及因元数据改善而避免的重复检索。
- 风险指标 / Risk Metrics: Track stale evidence, scope mismatch, permission miss, broken citation, state contamination, unresolved conflict, unsupported high-risk claims, and gate blocks. / 跟踪过期证据、范围错配、权限缺失、引用断裂、状态污染、未解决冲突、无依据高风险结论和门控阻断。
- Trace 指标 / Trace Metrics: Track query/filter trace completeness, candidate evidence trace, used and excluded evidence trace, gate records, failure attribution, and closed improvement tasks. / 跟踪查询与过滤追踪完整性、候选证据追踪、已用与排除证据追踪、门控记录、失败归因和已关闭改进任务。

## Probe Record Schema / 探针记录格式

```text
Probe record / 探针记录：
  Probe record ID / 探针记录编号：
  Workflow instance ID / 流程实例编号：
  Scenario / 场景名称：
  Step / 步骤名称：
  Collected at / 采集时间：
  Observation object / 采集对象：input / query / retrieval / ranking / evidence / context / reasoning / action / output / trace
                                输入 / 查询 / 检索 / 排序 / 证据 / 上下文 / 推理 / 动作 / 输出 / 追踪
  Observed values / 观测值：
  Rule / 判定规则：
  Result / 判定结果：pass / note / warning / block / missing / human review
                    通过 / 提示 / 警告 / 阻断 / 缺失 / 需人工
  Severity / 严重级别：low / medium / high / critical
                      低 / 中 / 高 / 极高
  Confidence note / 置信说明：
  Supplementable fields / 可补字段：
  Remaining gaps / 剩余缺口：
  Suggested action / 建议动作：continue / retry / human review / block / degraded output
                              继续 / 重试 / 转人工 / 阻断 / 降级输出
  Owner / 责任方：
  Trace link / 追踪链接：
```

## Supplement Package / 观测补数包

When a probe feeds a running RAG pipeline, return this package. / 当探针服务于运行中的 RAG 管线时，返回以下补数包。

```text
Observation supplement package / 观测补数包：
  Workflow instance ID / 流程实例编号：
  Related step / 对应步骤：
  Source probe / 来源探针：
  Filled fields / 补齐字段：
    - Field / 字段名：
      Value / 字段值：
      Source / 字段来源：
      Collected at / 采集时间：
      Confidence note / 置信说明：
  Risk judgment / 风险判断：
  Block reason / 阻断原因：
  Remaining gaps / 剩余缺口：
  Suggested action / 建议动作：
  Human required / 是否需要人工：yes / no
  Continue allowed / 是否允许继续：yes / no / conditional
  Trace record / 追踪记录：
```

## Observation Map / 观测位置图谱

| Workflow position / 流程位置 | Observation object / 采集对象 | Main probes / 主要探针 |
|---|---|---|
| Task intake / 任务进入 | task, role, scope, time / 任务、角色、范围、时间 | Input completeness, permission scope, time/version constraint / 输入完整性、权限范围、时间版本约束 |
| Query planning / 检索规划 | semantic query, filters, source plan / 语义查询、过滤条件、来源计划 | Query constraint retention, source routing / 查询约束保留、来源路由 |
| Retrieval / 证据召回 | candidates, scores, filters, misses / 候选、分数、过滤、未命中 | Recall sufficiency, filter adherence, diversity / 召回充分性、过滤遵守、多样性 |
| Ranking / 证据排序 | ranked list, reranked list, used evidence / 排序列表、重排列表、已用证据 | Ranking quality, top-k usable hit / 排序质量、Top-K 可用命中 |
| Context packing / 上下文组装 | chunks, surrounding context, token budget / 切块、前后文、上下文预算 | Context completeness, context efficiency / 上下文完整性、上下文效率 |
| Evidence validation / 证据校验 | source, version, scope, citation / 来源、版本、范围、引用 | Evidence contract, version validity, scope applicability / 证据契约、版本有效性、范围适用性 |
| Reasoning / 推理 | claims, evidence links, assumptions / 结论、证据链接、假设 | Evidence coverage, reasoning adoption, conflict handling / 证据覆盖、推理采纳、冲突处理 |
| Output gate / 输出门控 | answer, citations, gaps, risk / 答案、引用、缺口、风险 | Citation integrity, groundedness, answer completeness / 引用完整性、接地性、答案完整性 |
| Action gate / 动作门控 | state, action parameters, permissions / 状态、动作参数、权限 | Mechanical state source, state contamination, human confirmation / 机械状态来源、状态污染、人工确认 |
| Trace and review / 留痕复盘 | logs, tool calls, probe records / 日志、工具调用、探针记录 | Trace completeness, failure attribution, improvement loop / 追踪完整性、失败归因、闭环改进 |

## Core Metrics / 核心指标口径

Use metrics to locate risk, then use probes to decide next action. / 用指标定位风险，再用探针决定下一步动作。

| Metric / 指标 | Formula / 计算方式 | Primary use / 主要用途 |
|---|---|---|
| Input completeness / 输入完整率 | filled required intake fields ÷ required intake fields / 已填必填输入字段数 ÷ 必填输入字段总数 | Decide if workflow can start. / 判断能否进入流程。 |
| Query constraint retention / 查询约束保留率 | subqueries retaining hard constraints ÷ all subqueries / 保留硬约束的子查询数 ÷ 子查询总数 | Detect query rewrite drift. / 发现查询改写漂移。 |
| Recall hit rate / 召回命中率 | retrieval requests with at least one candidate ÷ retrieval requests / 至少有候选的检索请求数 ÷ 检索请求总数 | Detect missing source or index failure. / 发现来源缺失或索引失败。 |
| Usable evidence rate / 可用证据率 | validated usable evidence ÷ candidate evidence / 已校验可用证据数 ÷ 候选证据数 | Distinguish relevance from usability. / 区分相关与可用。 |
| Top-k usable hit rate / Top-K 可用命中率 | requests with usable evidence in top-k ÷ requests / Top-K 中有可用证据的请求数 ÷ 请求总数 | Check ranking and reranking quality. / 检查排序与重排质量。 |
| Filter adherence rate / 过滤遵守率 | candidates satisfying hard filters ÷ candidates / 满足硬过滤候选数 ÷ 候选总数 | Detect scope or permission leakage. / 发现范围或权限泄漏。 |
| Evidence contract completeness / 证据契约完整率 | used evidence with source, version, scope, citation ÷ used evidence / 具备来源、版本、范围、引用的已用证据数 ÷ 已用证据总数 | Validate evidence package quality. / 校验证据包质量。 |
| Version validity rate / 版本有效率 | evidence valid for task time ÷ used evidence / 对任务时间有效的证据数 ÷ 已用证据总数 | Detect stale or unpublished evidence. / 发现过期或未发布证据。 |
| Citation traceability / 引用可追率 | claims with resolvable citations ÷ cited claims / 可追溯引用结论数 ÷ 有引用结论总数 | Check auditability. / 检查可审计性。 |
| Grounded claim coverage / 接地结论覆盖率 | material claims supported by evidence ÷ material claims / 有证据支撑的关键结论数 ÷ 关键结论总数 | Detect hallucination or unsupported claims. / 发现幻觉或无依据结论。 |
| Evidence adoption rate / 证据采纳率 | evidence used in final reasoning ÷ validated evidence / 被最终推理采纳的证据数 ÷ 已校验证据数 | Detect ignored evidence or context overload. / 发现证据被忽略或上下文过载。 |
| Conflict evidence rate / 冲突证据率 | unresolved conflict groups ÷ usable evidence groups / 未解决冲突组数 ÷ 可用证据组数 | Detect knowledge governance risk. / 发现知识治理风险。 |
| Mechanical state source coverage / 状态来源覆盖率 | deterministic state fields ÷ required state fields / 有确定性来源的状态字段数 ÷ 必需状态字段数 | Validate action parameters. / 校验动作参数。 |
| State contamination rate / 状态污染率 | contaminated action parameters ÷ action parameters / 被污染动作参数数 ÷ 动作参数总数 | Block unsafe execution. / 阻断不安全执行。 |
| Gate pass, warning, block rates / 门控通过、警告、阻断率 | gate outcomes ÷ entered gates / 各类门控结果数 ÷ 进入门控流程数 | Monitor safety boundary. / 监控安全边界。 |
| Human review trigger rate / 人审触发率 | human-review flows ÷ total flows / 触发人审流程数 ÷ 总流程数 | Tune automation boundary. / 调整自动化边界。 |
| Trace completeness / 追踪完整率 | workflows with complete trace ÷ total workflows / 追踪完整流程数 ÷ 总流程数 | Ensure audit and debugging. / 保证审计与排障。 |
| Failure attribution rate / 失败可归因率 | attributable failures ÷ total failures / 可归因失败数 ÷ 失败总数 | Measure diagnosability. / 衡量可诊断性。 |
| Retrieval latency p95 / 检索延迟 P95 | 95th percentile retrieval latency / 检索延迟第 95 百分位 | Monitor user experience and timeout risk. / 监控体验和超时风险。 |
| Context efficiency / 上下文效率 | used evidence tokens ÷ context tokens / 已采纳证据 token 数 ÷ 上下文 token 数 | Detect context bloat. / 发现上下文膨胀。 |

## Probe Catalog / 探针目录

### Input And Scope Probes / 输入与范围探针

| Probe / 探针 | Applies to / 适用步骤 | Collect / 采集字段 | Rule / 判定规则 | Default action / 默认动作 |
|---|---|---|---|---|
| Input completeness / 输入完整性探针 | intake, task normalization / 进入、任务标准化 | task goal, object, role, time, output need, risk clues / 任务目标、对象、角色、时间、输出要求、风险线索 | Missing low-risk fields warn; missing sensitive role, permission, or object blocks. / 低风险字段缺失则警告；敏感角色、权限或对象缺失则阻断。 | Fill supplementable fields, ask human, or block. / 补齐可补字段、转人工或阻断。 |
| Permission scope / 权限范围探针 | intake, source selection, evidence validation, gates / 进入、来源选择、证据校验、门控 | actor, role, tenant, data class, source permission, action scope / 操作者、角色、租户、数据级别、证据权限、动作范围 | Any hard permission miss blocks; unknown permission is missing. / 任一硬权限不满足则阻断；权限未知视为缺失。 | Block unauthorized read or action. / 阻断越权读取或动作。 |
| Time and version constraint / 时间版本约束探针 | task normalization, retrieval planning, evidence validation / 任务标准化、检索规划、证据校验 | task date, effective date, retired date, index version, document version / 任务日期、生效日期、废止日期、索引版本、文档版本 | Evidence must cover task time; multiple versions require a version rule. / 证据必须覆盖任务时间；多版本并存时必须有版本口径。 | Supplement time, re-retrieve current version, or downgrade. / 补齐时间、重取当前版本或降级。 |

### Retrieval Probes / 检索探针

| Probe / 探针 | Applies to / 适用步骤 | Collect / 采集字段 | Rule / 判定规则 | Default action / 默认动作 |
|---|---|---|---|---|
| Query constraint retention / 查询约束保留探针 | query planning, query rewrite / 检索规划、查询改写 | original request, subqueries, hard filters, rewritten queries / 原始请求、子查询、硬过滤、改写查询 | All hard constraints must appear in every relevant subquery or metadata filter. / 所有硬约束必须出现在相关子查询或元数据过滤中。 | Rewrite query with constraints restored. / 恢复约束后重写查询。 |
| Source routing / 来源路由探针 | source selection / 来源选择 | evidence need, source priority, source health, excluded sources / 证据需求、来源优先级、来源健康、禁用来源 | Authoritative source required for policy or action explanations; summaries are secondary only. / 制度或动作解释必须查权威来源；摘要只能作为次级来源。 | Switch to authoritative source or flag gap. / 切换权威来源或标记缺口。 |
| Recall sufficiency / 召回充分性探针 | retrieval / 证据召回 | query, filters, candidate count, miss reason, source coverage / 查询、过滤、候选数量、未命中原因、来源覆盖 | No candidate or only out-of-scope candidates means missing; low diversity warns. / 无候选或仅有范围外候选视为缺失；多样性低则警告。 | Retry with alternate query, source, or non-critical filter relaxation. / 使用替代查询、来源或放宽非关键过滤重试。 |
| Filter adherence / 过滤遵守探针 | retrieval, ranking / 召回、排序 | candidates, metadata, permissions, hard filters / 候选、元数据、权限、硬过滤 | Candidate violating tenant, role, time, product, or permission must be excluded. / 违反租户、角色、时间、产品或权限的候选必须排除。 | Remove violating candidates and inspect index or filter bug. / 移除违规候选并检查索引或过滤问题。 |
| Ranking quality / 排序质量探针 | ranking, evidence selection / 排序、证据选择 | ranked list, reranked list, used evidence, relevance labels if available / 排序列表、重排列表、已用证据、可用相关标签 | Usable evidence retrieved but not surfaced in top-k warns; wrong evidence high in rank triggers rerank. / 可用证据被召回但未进 Top-K 则警告；错误证据靠前则触发重排。 | Rerank, add metadata boosts, or human review. / 重排、增加元数据权重或转人工。 |

### Evidence And Context Probes / 证据与上下文探针

| Probe / 探针 | Applies to / 适用步骤 | Collect / 采集字段 | Rule / 判定规则 | Default action / 默认动作 |
|---|---|---|---|---|
| Evidence contract / 证据契约探针 | evidence validation, reasoning, output / 证据校验、推理、输出 | source, version, scope, citation, effective time, permission / 来源、版本、范围、引用、生效时间、权限 | Used evidence must include source, version, scope, and citation; missing key fields warn or block by risk. / 已用证据必须包含来源、版本、范围和引用；关键字段缺失按风险警告或阻断。 | Supplement metadata, filter evidence, or re-retrieve. / 补元数据、过滤证据或重新检索。 |
| Version validity / 版本有效性探针 | retrieval, evidence validation, output / 检索、证据校验、输出 | document version, index version, effective date, retired date, publish status / 文档版本、索引版本、生效日期、废止日期、发布状态 | Stale, retired, unpublished, or wrong-index evidence cannot support current conclusions. / 过期、废止、未发布或索引版本错误的证据不能支撑当前结论。 | Exclude and fetch valid version. / 排除并获取有效版本。 |
| Scope applicability / 范围适用性探针 | evidence validation, reasoning / 证据校验、推理 | tenant, region, product, role, process stage, business object / 租户、地区、产品、角色、流程阶段、业务对象 | Evidence outside current scope is unusable; missing scope warns or requires human review. / 超出当前范围的证据不可用；范围缺失则警告或转人工。 | Keep only applicable evidence. / 只保留适用证据。 |
| Context completeness / 上下文完整性探针 | context packing, reasoning / 上下文组装、推理 | chunk text, title, section, neighboring chunks, table headers, document path / 片段、标题、章节、前后片段、表头、文档路径 | Critical claims must not rely on isolated fragments that lose object, condition, or exception context. / 关键结论不得依赖丢失对象、条件或例外的孤立片段。 | Fetch surrounding context or switch chunk. / 补取前后文或更换片段。 |
| Citation integrity / 引用完整性探针 | output, audit / 输出、审计 | citation location, page, section, clause, original file, evidence ID / 引用位置、页码、章节、条款、原文件、证据编号 | Citation must resolve to original source or original record; broken citation cannot support serious claims. / 引用必须回到原始来源或记录；断裂引用不能支撑严肃结论。 | Repair citation, replace evidence, or downgrade output. / 修复引用、替换证据或降级输出。 |

### Reasoning And Output Probes / 推理与输出探针

| Probe / 探针 | Applies to / 适用步骤 | Collect / 采集字段 | Rule / 判定规则 | Default action / 默认动作 |
|---|---|---|---|---|
| Evidence coverage / 证据覆盖探针 | reasoning, output gate / 推理、输出门控 | material claims, used evidence, state bindings, assumptions / 关键结论、已用证据、状态绑定、假设 | High-risk claims need usable evidence and required state; unsupported claims must be marked as assumptions. / 高风险结论需要可用证据和必要状态；无支撑结论必须标为假设。 | Add evidence, downgrade to assumption, or human review. / 补证据、降级为假设或转人工。 |
| Reasoning adoption / 推理采纳探针 | reasoning, output, audit / 推理、输出、审计 | validated evidence, final claims, citations, reasoning notes / 已校验证据、最终结论、引用、推理记录 | Conclusion that contradicts or ignores stronger evidence warns or blocks by risk. / 结论违背或忽略更强证据时，按风险警告或阻断。 | Re-reason from evidence or escalate. / 重新基于证据推理或升级处理。 |
| Conflict evidence / 冲突证据探针 | evidence validation, reasoning, output / 证据校验、推理、输出 | conflicting evidence, version, owner, priority, scope / 冲突证据、版本、责任方、优先级、范围 | Same-scope effective conflicts cannot be hidden; different-scope conflicts require boundary explanation. / 同范围有效冲突不得隐藏；不同范围冲突必须说明边界。 | Resolve by precedence or ask human. / 按优先级解决或转人工。 |
| Answer completeness / 答案完整性探针 | output / 输出 | user question, answer sections, gaps, caveats, citations / 用户问题、答案段落、缺口、限制、引用 | Answer must address the actual question and disclose limits, gaps, and conflicts. / 答案必须覆盖真实问题，并披露限制、缺口和冲突。 | Revise output or produce partial answer. / 修改输出或产出部分答案。 |

### Action And Governance Probes / 动作与治理探针

| Probe / 探针 | Applies to / 适用步骤 | Collect / 采集字段 | Rule / 判定规则 | Default action / 默认动作 |
|---|---|---|---|---|
| Mechanical state source / 机械状态来源探针 | action planning, action gate / 动作计划、动作门控 | IDs, amounts, accounts, statuses, source system, read time / 编号、金额、账户、状态、来源系统、读取时间 | Action parameters must come from deterministic state, not retrieved text or model inference. / 动作参数必须来自确定性状态，不能来自检索文本或模型推断。 | Fetch state or block action. / 读取状态或阻断动作。 |
| State contamination / 状态污染探针 | reasoning, action gate / 推理、动作门控 | action parameters, parameter source, evidence text, model draft / 动作参数、参数来源、证据文本、模型草稿 | Any critical parameter derived from evidence text or inference blocks execution. / 任一关键参数来自证据文本或推断则阻断执行。 | Re-bind deterministic state. / 重新绑定确定性状态。 |
| Risk and human confirmation / 风险与人审探针 | routing, output gate, action gate / 路由、输出门控、动作门控 | risk level, action type, impact, reversibility, confirmation record / 风险等级、动作类型、影响、可逆性、确认记录 | High-risk, irreversible, external, financial, permission, or deletion actions require confirmation. / 高风险、不可逆、外部可见、财务、权限或删除动作需要确认。 | Generate human review package. / 生成人工复核包。 |
| Rollback readiness / 回滚准备探针 | action planning, action gate, post-action trace / 动作计划、动作门控、执行后追踪 | prior state, backup, rollback steps, owner, deadline / 前置状态、备份、回滚步骤、责任方、时限 | High-risk publishing or write actions need rollback or compensating action. / 高风险发布或写动作需要回滚或补救动作。 | Block, confirm manually, or record compensating plan. / 阻断、人工确认或记录补救方案。 |

### Trace And Improvement Probes / 留痕与改进探针

| Probe / 探针 | Applies to / 适用步骤 | Collect / 采集字段 | Rule / 判定规则 | Default action / 默认动作 |
|---|---|---|---|---|
| Trace completeness / 追踪完整性探针 | trace, audit, troubleshooting / 留痕、审计、排障 | instance, steps, queries, candidates, used evidence, gates, output / 实例、步骤、查询、候选、已用证据、门控、输出 | Missing critical trace warns; high-risk incomplete trace blocks launch or requires incident review. / 缺关键追踪则警告；高风险追踪不完整则阻断上线或进入事故复盘。 | Backfill trace or mark audit risk. / 补记追踪或标记审计风险。 |
| Failure attribution / 失败归因探针 | troubleshooting, review / 排障、复盘 | missing fields, source health, index state, retrieval trace, ranking, evidence package, output, feedback / 缺失字段、来源健康、索引状态、检索追踪、排序、证据包、输出、反馈 | Attribute failure to intake, permission, source, indexing, chunking, retrieval, ranking, context, evidence, reasoning, citation, output, tool, or gate. / 将失败归因到输入、权限、来源、索引、切块、召回、排序、上下文、证据、推理、引用、输出、工具或门控。 | Generate fix task and regression case. / 生成修复任务和回归用例。 |
| Closed-loop improvement / 闭环改进探针 | review, periodic health check / 复盘、周期巡检 | repeated gaps, human corrections, user feedback, regression failures / 重复缺口、人工修正、用户反馈、回归失败 | Repeated issues must become knowledge fixes, metadata fixes, retrieval tuning, eval cases, or workflow guardrails. / 重复问题必须沉淀为知识修复、元数据修复、检索调优、评估用例或流程护栏。 | Add improvement task with owner and acceptance criteria. / 增加带责任方和验收口径的改进任务。 |

## Default Gate Rules / 默认门控规则

Block by default when: / 默认阻断：

- Sensitive task lacks permission scope. / 敏感任务缺少权限范围。
- High-risk answer uses evidence without source, version, scope, or traceable citation. / 高风险答案使用缺少来源、版本、范围或可追引用的证据。
- Evidence is stale, unpublished, retired, or outside scope. / 证据过期、未发布、已废止或超范围。
- Final conclusion contradicts stronger usable evidence. / 最终结论与更强可用证据冲突。
- Any action parameter lacks deterministic state source. / 任一动作参数缺少确定性状态来源。
- Required human confirmation is missing. / 必要人工确认缺失。

Warn or downgrade when: / 警告或降级：

- Evidence is relevant but missing non-critical metadata. / 证据相关但缺少非关键元数据。
- Retrieval found candidates but no authoritative source. / 检索到候选但缺权威来源。
- Context is enough for a narrow answer but not for broad generalization. / 上下文足以回答窄问题，但不足以泛化。
- Citations are traceable but not granular enough for audit preference. / 引用可追，但粒度不够理想。
- Latency or context usage is high but correctness is not at risk. / 延迟或上下文使用偏高，但正确性未受影响。

## Scenario Probe Sets / 场景化探针组合

- Knowledge QA / 知识问答: input completeness, time/version constraint, source routing, recall sufficiency, evidence contract, version validity, scope applicability, context completeness, citation integrity, evidence coverage, reasoning adoption, trace completeness. / 输入完整性、时间版本约束、来源路由、召回充分性、证据契约、版本有效性、范围适用性、上下文完整性、引用完整性、证据覆盖、推理采纳、追踪完整性。
- Business analysis / 业务分析: source routing, recall sufficiency, ranking quality, evidence contract, conflict evidence, evidence coverage, reasoning adoption, answer completeness, failure attribution. / 来源路由、召回充分性、排序质量、证据契约、冲突证据、证据覆盖、推理采纳、答案完整性、失败归因。
- Action planning / 动作计划: permission scope, mechanical state source, state contamination, evidence contract, risk and human confirmation, rollback readiness, output gate, trace completeness. / 权限范围、机械状态来源、状态污染、证据契约、风险与人审、回滚准备、输出门控、追踪完整性。
- Document ingestion / 文档入库: input completeness, source routing, evidence contract, version validity, scope applicability, context completeness, retrieval regression, trace completeness, closed-loop improvement. / 输入完整性、来源路由、证据契约、版本有效性、范围适用性、上下文完整性、检索回归、追踪完整性、闭环改进。
- Audit and troubleshooting / 审计与排障: trace completeness, evidence contract, version validity, citation integrity, reasoning adoption, state contamination, failure attribution, closed-loop improvement. / 追踪完整性、证据契约、版本有效性、引用完整性、推理采纳、状态污染、失败归因、闭环改进。

## Observability Report Template / 观测报告模板

```text
Observability report / 观测报告：
  Report ID / 报告编号：
  Scenario / 场景名称：
  Time range / 时间范围：
  Covered workflows / 覆盖流程数：
  Enabled probes / 启用探针：

Overall conclusion / 总体结论：
  Passed flows / 通过流程数：
  Warning flows / 警告流程数：
  Blocked flows / 阻断流程数：
  Human-review flows / 转人工流程数：
  Failed flows / 失败流程数：

Metric summary / 指标摘要：
  Input completeness / 输入完整率：
  Recall hit rate / 召回命中率：
  Usable evidence rate / 可用证据率：
  Evidence contract completeness / 证据契约完整率：
  Citation traceability / 引用可追率：
  Grounded claim coverage / 接地结论覆盖率：
  Gate block rate / 门控阻断率：
  Trace completeness / 追踪完整率：
  Failure attribution rate / 失败可归因率：

Major risks / 主要风险：
  - Risk / 风险：
    Scope / 影响范围：
    Severity / 严重级别：
    Evidence / 证据：
    Suggested action / 建议动作：

Data gaps / 数据缺口：
  - Gap / 缺口字段：
    Step / 发生步骤：
    Impact / 影响：
    Supplement suggestion / 补数建议：

Failure attribution / 失败归因：
  Intake / 输入：
  Permission / 权限：
  Source / 来源：
  Indexing or chunking / 索引或切块：
  Retrieval / 召回：
  Ranking / 排序：
  Context / 上下文：
  Evidence / 证据：
  Reasoning / 推理：
  Citation / 引用：
  Output / 输出：
  Tool / 工具：
  Gate / 门控：

Improvement tasks / 改进任务：
  - Task / 任务名称：
    Owner / 责任方：
    Priority / 优先级：
    Acceptance criteria / 验收方式：
```

## Constraints / 约束

- Keep metrics tied to concrete probes and workflow positions. / 指标必须绑定具体探针和流程位置。
- Do not use aggregate metrics to override safety gates. / 不得用汇总指标绕过安全门控。
- Do not fabricate missing evidence, missing state, citations, permissions, or trace records. / 不得伪造缺失证据、状态、引用、权限或追踪记录。
- Do not treat relevant retrieval as usable evidence until source, version, scope, permission, and citation checks pass. / 相关召回在通过来源、版本、范围、权限和引用检查前，不得视为可用证据。
- Do not let probes directly execute production actions. / 探针不得直接执行生产动作。
- Version probes with the workflow; update probes when sources, indexes, chunking, permissions, tools, or gate rules change. / 探针应随流程版本化；当来源、索引、切块、权限、工具或门控规则变化时同步更新。
