# RAG Pipeline / RAG 管线

Cell / 交织点: memory-chain / 记忆 x 链式
Capability / 能力: Memory / 记忆
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

RAG Pipeline / RAG 管线 is a memory-chain pattern for tasks where retrieval, evidence validation, grounded reasoning, and output construction must happen in a dependable order. / RAG 管线是一种记忆 x 链式模式，适用于检索、证据校验、基于证据推理和输出构造必须按可靠顺序发生的任务。

The core rule is: retrieved is not automatically usable. Candidate evidence must pass source, version, scope, permission, and citation checks before it can support a conclusion or action plan. / 核心规则是：召回不等于可用。候选证据必须通过来源、版本、范围、权限和引用检查后，才能支撑结论或动作计划。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Memory / 记忆 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Memory / 记忆 x Chain / 链式 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Memory / 记忆 x Chain / 链式 映射到该单元。
- 问题 / Problem: Model-internal knowledge is stale, incomplete, or unverifiable for the current task. / 模型内部知识对当前任务而言过期、不完整或无法验证。
- 架构方案 / Architectural Solution: Retrieve external sources, rank or filter them, ground the answer or plan in retrieved evidence, and pass the grounded context forward. / 检索外部来源，排序或过滤，再基于检索证据生成回答或计划并传递扎根上下文。
- 工程权衡 / Engineering Trade-offs: Improves freshness and provenance, but retrieval quality, latency, and source trust become part of system quality. / 提升新鲜度和来源可追溯性，但检索质量、延迟和来源可信度也成为系统质量的一部分。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when retrieval, grounding, and answer construction form a sequence. / 当检索、扎根和回答构成顺序管线时使用。

## Usage / 使用方式

Use this pattern for: / 适用于：

- Knowledge QA over policies, manuals, contracts, procedures, tickets, or document collections. / 基于制度、手册、合同、流程、工单或文档集合的知识问答。
- Business analysis where causes, impacts, or recommendations must be evidence-backed. / 原因、影响或建议必须由证据支撑的业务分析。
- Action planning where explanation depends on retrieved evidence, but action parameters require deterministic state. / 解释依赖检索证据、但动作参数需要确定性状态的动作计划。
- Audit or troubleshooting of bad recall, stale evidence, broken citations, conflicting sources, or ungrounded answers. / 对召回错误、证据过期、引用断裂、来源冲突或未扎根回答的审计与排障。

Do not use this pattern as the whole solution when the dominant problem is classification, parallel evidence gathering, iterative memory repair, or governance gating. Use memory-routing, memory-parallel, memory-loop, or governance cells when those concerns dominate. / 当主导问题是分类路由、并行证据采集、迭代记忆修复或治理门控时，不要把本模式当作完整方案；应使用 memory-routing、memory-parallel、memory-loop 或治理相关单元。

## Core Boundaries / 核心边界

| Plane / 平面 | Source rule / 来源规则 | Never do / 禁止事项 |
|---|---|---|
| User intent / 用户意图 | Preserve the original request and output need. / 保留原始请求和输出需求。 | Do not silently change the question. / 不要静默改写问题目标。 |
| Retrieval constraints / 检索约束 | Carry role, time, version, product, tenant, region, and source scope into every query or filter. / 将角色、时间、版本、产品、租户、地区和来源范围带入每个查询或过滤条件。 | Do not broaden retrieval by dropping hard constraints. / 不要通过丢弃硬约束来扩大召回。 |
| Mechanical state / 机械状态 | Read IDs, amounts, statuses, accounts, and action parameters from deterministic systems, tool results, session state, or explicit human confirmation. / 编号、金额、状态、账户和动作参数必须来自业务系统、工具返回、会话状态或明确人工确认。 | Do not infer action parameters from semantically similar evidence. / 不要从语义相似证据中推断动作参数。 |
| Business evidence / 业务证据 | Use source, version, effective time, scope, permission, and citation location. / 使用来源、版本、生效时间、适用范围、权限和引用位置。 | Do not cite source-free summaries as authoritative evidence. / 不要把无来源摘要当作权威证据。 |
| Reasoning assumptions / 推理假设 | Mark assumptions explicitly and keep them out of factual claims. / 显式标注假设，不把假设写成事实。 | Do not hide uncertainty behind confident wording. / 不要用肯定语气掩盖不确定性。 |
| Action authority / 动作权限 | Bind action authority to permission, approval, risk, and rollback gates. / 将动作权限绑定到权限、审批、风险和回滚门控。 | Do not execute merely because the answer is known. / 不要因为能回答就直接执行。 |

## Input Contract / 输入契约

Collect or mark these fields before retrieval. / 检索前收集或标记以下字段。

```text
Workflow instance / 流程实例：
  Instance ID / 实例编号：
  Task request / 任务请求：
  Task type / 任务类型：answer / analysis / action plan / audit / ingestion / troubleshooting
                         问答 / 分析 / 动作计划 / 审计 / 入库 / 排障
  Current role and permission scope / 当前角色与权限范围：
  Business object / 业务对象：
  Time and version constraints / 时间与版本约束：
  Risk level / 风险等级：low / medium / high / critical
                           低 / 中 / 高 / 极高

Retrieval request / 检索请求：
  Semantic question / 语义问题：
  Required sources / 必须检索来源：
  Excluded sources / 禁止使用来源：
  Metadata filters / 元数据过滤条件：
  Required citation fields / 必须引用字段：source / version / scope / location / effective time
                                      来源 / 版本 / 范围 / 位置 / 生效时间

Mechanical state / 机械状态：
  Fields needed / 所需字段：
  Deterministic source / 确定性来源：
  Read time / 读取时间：
  Verification status / 校验状态：

Output requirement / 输出要求：
  Output type / 输出类型：answer / decision / action plan / audit report
                          答案 / 决策 / 动作计划 / 审计报告
  Citation requirement / 引用要求：
  Human confirmation / 人工确认：required / not required / conditional
                               需要 / 不需要 / 条件触发
```

## Execution Flow / 执行流程

### 0. Register Context / 场景登记

Create a workflow instance, bind role and permission scope, record business object, time range, risk level, and whether the task may produce an action. Block sensitive requests when actor, scope, or legal task boundary is unclear. / 创建流程实例，绑定角色和权限范围，记录业务对象、时间范围、风险等级，并判断任务是否可能产生执行动作。敏感请求中的操作者、范围或合法边界不清时应阻断。

### 1. Normalize The Task / 任务标准化

Rewrite the raw request into a structured task without changing intent. Extract target question, business object, output type, time range, explicit constraints, implicit constraints, and unknowns. / 在不改变意图的前提下，将原始请求改写为结构化任务。提取目标问题、业务对象、输出类型、时间范围、显式约束、隐含约束和不确定项。

### 2. Route The Task / 任务路由

Choose the route: answer, analysis, action plan, audit, ingestion, or troubleshooting. Action plans must activate mechanical-state and governance checks even when the explanation uses retrieved evidence. / 选择问答、分析、动作计划、审计、入库或排障路径。动作计划即使解释依赖检索证据，也必须启用机械状态和治理校验。

### 3. Split Boundaries / 边界拆分

Create separate lists for mechanical state, business evidence, retrieval assumptions, action intent, and output constraints. Treat every unknown as a gap, not as model-fillable context. / 分别列出机械状态、业务证据、检索假设、动作意图和输出约束。每个未知项都视为缺口，而不是可由模型自行补全的上下文。

### 4. Complete Constraints / 约束补齐

Resolve role, tenant or organization, product, process, region, business object, effective date, version standard, source scope, and permission range. If multiple versions may apply and the effective date is missing, ask, apply version policy, or block high-risk output. / 补齐角色、租户或组织、产品、流程、地区、业务对象、生效日期、版本口径、来源范围和权限范围。若可能存在多个版本且生效日期缺失，应询问、应用版本策略，或阻断高风险输出。

### 5. Select Sources / 来源选择

Choose sources by information type. Deterministic systems are required for IDs, amounts, statuses, accounts, and action parameters. Published knowledge sources are required for rules, policies, and explanatory evidence. / 按信息类型选择来源。编号、金额、状态、账户和动作参数必须来自确定性系统。规则、制度和解释性证据必须来自已发布知识源。

### 6. Plan Retrieval / 检索规划

Build a retrieval plan before calling search tools. Include semantic query, exact keywords, metadata filters, source priority, date or version filters, required citation fields, and fallback searches. Decompose multi-part questions into subqueries while preserving hard constraints on every subquery. / 调用检索工具前制定检索计划。包含语义查询、精确关键词、元数据过滤、来源优先级、日期或版本过滤、必需引用字段和兜底检索。将多问题拆为子查询时，每个子查询都必须保留硬约束。

### 7. Retrieve And Record Candidates / 召回并记录候选

Run the retrieval plan and record query text, filters, source, time, returned documents, ranking scores if available, and retrieval failures. Keep candidate evidence separate from usable evidence. / 执行检索计划，并记录查询文本、过滤条件、来源、时间、返回文档、可用排序分数和检索失败。候选证据必须与可用证据分开保存。

### 8. Validate Evidence Usability / 校验证据可用性

Do not use a retrieved item until it passes trusted source, correct version, effective time, applicable scope, permission, traceable citation, and no unresolved conflict with stronger evidence. / 召回项在通过来源可信、版本正确、生效时间覆盖、适用范围匹配、权限允许、引用可追和不存在未解决的更强证据冲突前，不得使用。

When evidence conflicts, prefer explicit policy precedence, responsible owner, newer effective version, narrower applicable scope, or human confirmation. If conflict remains, report it instead of smoothing it over. / 当证据冲突时，优先使用明确制度优先级、责任方、更新有效版本、更窄适用范围或人工确认。若冲突仍未解决，应报告冲突，不要强行调和。

### 9. Build Evidence Package / 构建证据包

Select only validated evidence. For each item, record source, title or record ID, version, scope, effective time, citation location, retrieved snippet, why it is used, and limits. Exclude unused candidates with reasons when they look relevant but fail a gate. / 仅选择已校验证据。每条证据记录来源、标题或记录编号、版本、范围、生效时间、引用位置、召回片段、使用原因和限制。对看似相关但未通过门控的候选，记录未使用原因。

### 10. Reason From Evidence / 基于证据推理

Answer or analyze only from the evidence package and verified mechanical state. Bind each material claim to evidence, mark assumptions, state unknowns, and distinguish conclusion, evidence, state, and recommendation. / 只基于证据包和已验证机械状态回答或分析。每个关键事实主张都要绑定证据，标注假设，说明未知项，并区分结论、证据、状态和建议。

### 11. Run Output Gate / 执行输出门控

Before responding or executing, check that the answer covers the actual question, every key claim has usable evidence or an explicit assumption label, citations are traceable, scope and limits are stated, action parameters come only from deterministic state, and permission, risk, human confirmation, and rollback requirements are satisfied for actions. / 输出或执行前检查：答案覆盖真实问题；每个关键主张都有可用证据或显式假设标记；引用可追；范围和限制已说明；动作参数仅来自确定性状态；执行动作满足权限、风险、人工确认和回滚要求。

Gate decisions: pass, warning pass, retry, human review, or block. / 门控结论：通过、警告通过、重试、转人工或阻断。

### 12. Output Or Action Plan / 输出或动作计划

For answers and analysis, include conclusion, evidence citations, applicable scope, limits, conflicts, and remaining gaps. For action plans, include action name, object, parameters, parameter sources, preconditions, risk level, confirmation requirement, rollback or reversal path, and post-execution checks. / 对问答和分析，包含结论、证据引用、适用范围、限制、冲突和剩余缺口。对动作计划，包含动作名称、对象、参数、参数来源、前置条件、风险等级、确认要求、回滚或撤销路径和执行后核验。

### 13. Trace And Improve / 留痕与改进

Record workflow instance, normalized task, retrieval plan, queries and filters, candidate evidence, used evidence, excluded evidence, mechanical state sources, gate decisions, final output, and failure reasons. Convert repeated gaps into source-quality fixes, indexing fixes, metadata fixes, evaluation cases, or workflow guardrails. / 记录流程实例、标准化任务、检索计划、查询与过滤、候选证据、已用证据、排除证据、机械状态来源、门控结论、最终输出和失败原因。将重复缺口转化为来源质量修复、索引修复、元数据修复、评估用例或流程护栏。

## Output Contract / 输出契约

```text
RAG result / RAG 结果：
  Final status / 最终状态：complete / partial / blocked / human review / failed
                            完成 / 部分完成 / 阻断 / 转人工 / 失败
  Main answer or plan / 主答案或计划：
  Confidence note / 置信说明：
  Applicable scope / 适用范围：
  Limits and exclusions / 限制与不适用范围：

Evidence package / 证据包：
  Used evidence / 已使用证据：
    - Evidence ID / 证据编号：
      Source / 来源：
      Version / 版本：
      Scope / 适用范围：
      Effective time / 生效时间：
      Citation location / 引用位置：
      Why used / 使用原因：
  Excluded evidence / 未使用证据：
    - Evidence ID / 证据编号：
      Reason excluded / 未使用原因：

Mechanical state binding / 机械状态绑定：
  - Field / 字段：
    Value / 值：
    Source / 来源：
    Read time / 读取时间：
    Verification / 校验状态：

Gates / 门控记录：
  Evidence usability / 证据可用性：pass / warning / failed
  Citation coverage / 引用覆盖：pass / warning / failed
  Permission / 权限校验：pass / failed / not applicable
  Risk / 风险校验：pass / human review / blocked
  Human confirmation / 人工确认：confirmed / missing / not required

Gaps / 缺口清单：
  - Gap / 缺口：
    Impact / 影响：
    Suggested handling / 建议处理：

Trace / 追踪记录：
  Queries and filters / 查询与过滤：
  Tool calls / 工具调用：
  Retrieval failures / 检索失败：
  Review entry / 复盘入口：
```

## Failure Modes / 失败模式

| Failure / 失败模式 | Signal / 识别信号 | Handling / 处理方式 |
|---|---|---|
| No evidence / 证据缺失 | Search returns no usable source. / 检索未返回可用来源。 | Retry with constrained alternatives, then report gap or ask human. / 使用保留约束的替代检索重试，然后报告缺口或转人工。 |
| Stale evidence / 证据过期 | Effective date or version does not cover the task. / 生效日期或版本不覆盖任务。 | Exclude, retrieve current version, or block high-risk answer. / 排除、检索当前版本，或阻断高风险答案。 |
| Scope mismatch / 范围错配 | Evidence applies to another tenant, product, region, or role. / 证据适用于其他租户、产品、地区或角色。 | Exclude and record why. / 排除并记录原因。 |
| Citation break / 引用断裂 | Citation cannot return to source text or original record. / 引用无法回到原文或原始记录。 | Do not use as authoritative evidence. / 不作为权威证据使用。 |
| Conflict / 证据冲突 | Two usable sources disagree. / 两个可用来源口径不一致。 | Resolve by precedence or report conflict. / 按优先级解决或报告冲突。 |
| State contamination / 状态污染 | Action parameter came from retrieved text or model inference. / 动作参数来自检索文本或模型推断。 | Block action and re-bind deterministic state. / 阻断动作并重新绑定确定性状态。 |
| Ungrounded answer / 未采纳证据 | Conclusion is not supported by used evidence. / 结论未被已用证据支撑。 | Re-reason from evidence or downgrade to gap statement. / 重新基于证据推理或降级为缺口说明。 |
| Over-broad retrieval / 检索过宽 | Results look relevant but ignore constraints. / 结果看似相关但忽略约束。 | Reapply filters and keep constraints on subqueries. / 重新应用过滤，并在子查询中保留约束。 |

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: RAG Pipeline / RAG 管线.
- 诊断用途 / Diagnostic Use: Use when retrieval, grounding, evidence validation, and answer construction form a sequence. / 当检索、扎根、证据校验和回答构成顺序管线时使用。
- 适用工作流节点 / Applicable Workflow Nodes: Knowledge QA, policy lookup, document-grounded analysis, evidence-backed action planning, RAG troubleshooting. / 知识问答、制度查询、文档扎根分析、证据型动作计划、RAG 排障。
- 当前症状 / Current Symptoms: stale knowledge, unverifiable answer, missing citation, low source trust, evidence conflict, or action parameter contamination. / 知识过期、答案不可验证、引用缺失、来源可信度低、证据冲突或动作参数污染。
- 适配信号 / Fit Signals: A previous retrieval result must directly feed the next grounding, reasoning, or output step. / 上一步检索结果必须直接进入下一步扎根、推理或输出。
- 调整方向 / Adjustment Direction: Add explicit retrieval planning, evidence usability gates, evidence package construction, output gates, and trace records. / 增加明确检索规划、证据可用性门控、证据包构建、输出门控和追踪记录。
- 修改方式 / How To Modify: Separate mechanical state from business evidence, keep hard constraints on every query, validate evidence before reasoning, and block high-risk unsupported output. / 分离机械状态与业务证据，在每次查询中保留硬约束，推理前校验证据，并阻断高风险无依据输出。
- 输入 / Inputs: task request, role and permission, time and version constraints, retrieval request, source scope, state needs, output requirement. / 任务请求、角色与权限、时间与版本约束、检索请求、来源范围、状态需求、输出要求。
- 输出 / Outputs: grounded answer or action plan, evidence package, state binding, gate record, gap list, trace record. / 扎根答案或动作计划、证据包、状态绑定、门控记录、缺口清单、追踪记录。
- 风险与治理 / Risks & Governance: stale evidence, scope mismatch, citation break, state contamination, hidden conflict, over-broad retrieval, and ungrounded conclusions. / 过期证据、范围错配、引用断裂、状态污染、隐藏冲突、检索过宽和未扎根结论。

Observability Metrics File / 可观测性指标文件: [memory-chain-observability.md](memory-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
