# Failure Diary / 失败日记 Observability Metrics / 可观测性指标

Cell / 交织点: memory-loop / 记忆 x 循环
Capability / 能力: Memory / 记忆
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850), extended with user-provided failure diary observability probes. / 来源：arXiv:2605.13850，并结合用户提供的失败日记可观测性探针扩展。

Use this file as the observability metrics source for this matrix intersection. / 将本文档作为该交织点的可观测性指标来源。

Design Pattern File / 设计模式文件: [memory-loop.md](memory-loop.md)

## Observability Goal / 观测目标

Observe whether failure lessons are correctly captured, reviewed, recalled, and used to reduce repeated failures. The probes do not replace the execution flow; they supply data, quality checks, risk signals, and workflow corrections. / 观测失败经验是否被正确捕获、正确审查、正确召回，并最终减少同类失败。探针不替代执行流程，而是提供数据、质量检查、风险信号和流程修正建议。

Core question: did the system see the right failure, turn it into a useful lesson, recall it at the right time, and change future behavior? / 核心问题：系统是否看见了正确失败，把它转成有用经验，在正确时机召回，并改变未来行为？

## Operating Modes / 运行模式

- Sidecar observation: read traces, logs, gate results, recall records, and human feedback without changing the workflow. / 旁路观测：读取轨迹、日志、闸门结果、召回记录和人工反馈，但不改变工作流。
- Embedded assist: run inside the failure diary flow to supplement fields, check evidence completeness, score recall risk, prioritize review, and block unsafe paths. / 内嵌辅助：嵌入失败日记流程，补齐字段、检查证据完整性、评估召回风险、排序审查优先级并阻断不安全路径。
- Replay evaluation: replay historical traces to test whether recall rules would have found lessons before past failures. / 回放评测：回放历史轨迹，测试召回规则能否在过去失败前找到经验。

## Probe Installation Points / 探针安装点

| Position / 位置 | Observe / 观测内容 | Question / 核心问题 |
|---|---|---|
| Task start / 任务启动 | task family, goal, scope, permission / 任务族、目标、范围、权限 | Can historical failures match this task? / 是否能匹配历史失败？ |
| Plan generation / 计划生成 | steps, dependencies, validation, risk / 步骤、依赖、验收、风险 | Did the plan miss a known pitfall? / 是否遗漏已知坑？ |
| Context assembly / 上下文装配 | injected context and old memories / 注入上下文和旧记忆 | Is stale context polluting judgment? / 是否有旧信息污染判断？ |
| Before tool call / 工具调用前 | tool, parameters, source, scope / 工具、参数、来源、范围 | Is a danger card needed before action? / 动作前是否需要危险卡？ |
| After tool call / 工具返回后 | result, error, state change / 返回、错误、状态变化 | Did this create a failure candidate? / 是否产生失败候选？ |
| Validation gate / 验证闸门 | rule, pass/fail, block reason / 规则、通过情况、阻断原因 | Should gate failure become a draft? / 闸门失败是否应转草稿？ |
| Candidate generation / 候选生成 | boundary, category, risk / 边界、分类、风险 | Is this worth preserving? / 是否值得沉淀？ |
| Review transition / 审查流转 | draft, pending, enabled, archived / 草稿、待审查、已启用、已归档 | Did unreviewed memory enter recall? / 未审查经验是否进入召回？ |
| Recall injection / 召回注入 | recalled card, match reason, position / 召回卡、匹配原因、注入位置 | Was recall relevant and timely? / 召回是否相关且及时？ |
| Task end / 任务结束 | result, rollback, feedback, repeat failure / 结果、回滚、反馈、重复失败 | Did the loop improve behavior? / 是否形成改进闭环？ |

## Data Contract / 数据契约

Collect enough trace to calculate metrics and diagnose causes. / 采集足以计算指标并诊断原因的轨迹。

```text
Task data / 任务级数据：
  Workflow ID / 工作流编号：
  Task family / 任务族：
  Goal / 任务目标：
  Business scope / 业务范围：
  Permission scope / 权限范围：
  Risk level / 风险等级：
  Start and end time / 开始与结束时间：
  Final status / 最终状态：

Node data / 节点级数据：
  Node ID / 节点编号：
  Node type / 节点类型：
  Input and output / 输入与输出：
  State change / 状态变化：
  Failure candidate / 失败候选：
  Gate result / 闸门结果：
  Human feedback / 人工反馈：

Tool data / 工具级数据：
  Tool name and type / 工具名称与类别：
  Parameter source / 参数来源：
  Mechanical parameters / 机械参数：
  Scope / 作用范围：
  Result / 返回结果：
  Side effect / 副作用：
  Pre-action recall / 前置召回：
  Pre-action verification / 前置校验：

Diary data / 失败日记级数据：
  Failure ID / 失败编号：
  Boundary, category, risk / 边界、分类、风险：
  Status / 状态：
  Evidence completeness / 证据完整性：
  Root-cause quality / 根因质量：
  Recall conditions / 召回条件：
  Recall count and result / 召回次数与结果：
  Repeated failure / 重复失败：
```

## Observability Metrics / 可观测性指标

Use the five generic metric families for matrix consistency, then use the failure-diary-specific catalog below for operational diagnosis. / 为保持矩阵一致性先使用五类通用指标，再使用下方失败日记专用指标目录做运行诊断。

- 质量指标 / Quality Metrics: Track capture correctness, evidence completeness, root-cause actionability, recall relevance, and repeated-failure decline. / 跟踪捕获正确性、证据完整性、根因可行动性、召回相关性和重复失败下降。
- 时延指标 / Latency Metrics: Track failure-to-draft time, review cycle time, failure-to-enable time, recall latency, and update timeliness. / 跟踪失败到草稿、审查周期、失败到启用、召回时延和更新及时性。
- 成本指标 / Cost Metrics: Track review effort, card context share, recall volume, repeated work avoided, and per-lesson preservation cost. / 跟踪审查投入、卡片上下文占用、召回数量、避免的重复工作和单条失败沉淀成本。
- 风险指标 / Risk Metrics: Track unreviewed recall attempts, scope leakage, stale lessons, history-current conflict, and suspected memory poisoning. / 跟踪未审查召回、范围泄漏、过期经验、历史与当前冲突和疑似记忆投毒。
- Trace 指标 / Trace Metrics: Track trace completeness, evidence reference validity, mechanical-state source clarity, recall audit records, and remediation closure. / 跟踪轨迹完整性、证据引用有效性、机械状态来源清晰度、召回审计记录和补救闭环。

## Metric System / 指标体系

### Failure Capture / 失败捕获

| Metric / 指标 | Formula / 定义 | Use / 用途 |
|---|---|---|
| Candidate capture rate / 失败候选捕获率 | captured failure candidates / actual failure events / 被捕获候选数 / 实际失败事件数 | Detect invisible failures. / 判断失败是否被看见。 |
| Invalid candidate ratio / 无效候选比例 | candidates judged not worth preserving / all candidates / 无需沉淀候选数 / 候选总数 | Detect over-broad capture. / 判断捕获是否过宽。 |
| Silent failure discovery rate / 静默失败发现率 | semantic or safety failures without explicit errors / all failures / 无显性报错但被发现的语义或安全失败数 / 全部失败数 | Detect "successful but wrong" work. / 发现“表面成功但目标错误”。 |
| Gate-to-draft rate / 闸门失败转草稿率 | gate failures converted to diary drafts / all gate failures / 转草稿闸门失败数 / 闸门失败总数 | Check whether gates feed lessons. / 判断闸门是否接入沉淀流程。 |

### Evidence Completeness / 证据完整性

| Metric / 指标 | Formula / 定义 | Use / 用途 |
|---|---|---|
| Four-layer evidence completeness / 四层证据完整率 | entries with workspace, narrative, mechanical-state, and raw-observation evidence / all entries / 具备四层证据的日记数 / 日记总数 | Ensure review and auditability. / 保证可复盘、可审计。 |
| Evidence reference validity / 证据引用有效率 | resolvable evidence references / all evidence references / 可回查引用数 / 全部引用数 | Prevent broken evidence chains. / 防止引用断裂。 |
| Mechanical state source clarity / 机械状态来源清晰度 | key parameters with source, scope, and consumer node / all key parameters / 标明来源、范围、消费节点的关键参数数 / 关键参数总数 | Track IDs, amounts, accounts, batches, and objects. / 追踪编号、金额、账号、批次和对象。 |
| Raw observation retention / 原始观测保留率 | entries with tool output, gate report, error stack, or human review record / all entries / 带原始观测的日记数 / 日记总数 | Keep facts, not only conclusions. / 防止只留结论不留事实。 |

### Root Cause And Remediation / 根因与补救

| Metric / 指标 | Formula / 定义 | Use / 用途 |
|---|---|---|
| Actionable root-cause rate / 根因可行动率 | reviewed entries whose root cause points to a mechanism, rule, tool, state, or process change / reviewed entries / 根因可指向机制、规则、工具、状态或流程修改的日记数 / 已审查日记数 | Judge whether lessons can improve the system. / 判断根因是否能指导改进。 |
| Invalid root-cause ratio / 无效根因比例 | reviewed entries using vague causes / reviewed entries / 使用泛化根因的日记数 / 已审查日记数 | Detect non-engineering explanations. / 发现不可操作解释。 |
| Remediation closure rate / 补救闭环率 | completed remediation actions / required remediation actions / 已完成补救动作数 / 需要补救动作数 | Ensure fixes happen. / 保证失败被真正修复。 |
| Forbidden-action clarity / 禁止动作明确率 | enabled entries with explicit forbidden actions / enabled entries / 明确禁止动作的已启用日记数 / 已启用日记数 | Turn lessons into constraints. / 把经验转成行动约束。 |
| Regression-test conversion rate / 回归测试转化率 | high-risk failures converted to tests / high-risk failures / 转成测试用例的高风险失败数 / 高风险失败总数 | Move memory into engineering defenses. / 把记忆护栏变成工程防线。 |

### Recall Quality / 召回质量

| Metric / 指标 | Formula / 定义 | Use / 用途 |
|---|---|---|
| Recall hit rate / 召回命中率 | relevant lessons recalled / expected recalls / 成功召回相关经验次数 / 应召回次数 | Check whether recall finds the right lesson. / 判断是否能找到正确经验。 |
| Recall effectiveness / 召回有效率 | recalls that changed plan, parameters, validation, or human-review path / total recalls / 改变计划、参数、校验或人审路径的召回数 / 召回总数 | Check whether recall changes behavior. / 判断召回是否改变行为。 |
| Missed recall rate / 漏召回率 | repeat failures where an applicable diary existed but was not recalled / repeat failures / 有经验但未召回的重复失败次数 / 重复失败总次数 | Detect missing indexes or late recall points. / 发现索引或召回入口不足。 |
| False reminder rate / 误提醒率 | irrelevant recalled lessons / total recalls / 无关召回经验数 / 召回总数 | Control context noise. / 控制上下文噪声。 |
| Structured recall share / 结构化召回占比 | recalls hit by task family, tool, mechanical parameter, or category / total recalls / 通过结构化键命中的召回数 / 召回总数 | Reduce reliance on semantic similarity only. / 降低对纯语义相似的依赖。 |
| High-risk pre-action recall coverage / 高风险动作前召回覆盖率 | high-risk tool calls with pre-action recall / all high-risk tool calls / 完成前置召回的高风险工具调用数 / 高风险工具调用总数 | Ensure side-effect gates have memory. / 保证副作用入口有经验护栏。 |
| Post-recall re-check rate / 召回后再核验率 | recalls followed by current-fact verification / total recalls / 召回后核验当前事实次数 / 召回总数 | Prevent blind trust in history. / 防止盲信历史经验。 |

### Closed-Loop Effectiveness / 闭环效果

| Metric / 指标 | Formula / 定义 | Use / 用途 |
|---|---|---|
| Repeated failure rate / 重复失败率 | recorded failure patterns repeated / same-family task executions / 已记录失败模式再次发生次数 / 同类任务总数 | Primary success metric. / 核心成效指标。 |
| Same-failure decline rate / 同类失败下降率 | previous-period failures minus current-period failures / previous-period failures / 上周期同类失败次数减当前周期次数 / 上周期次数 | Measure long-term benefit. / 衡量长期收益。 |
| Post-recall repeated failure rate / 召回后重复失败率 | same failures after relevant recall / relevant recalls / 召回后仍发生同类失败次数 / 相关召回次数 | Detect weak lessons, wrong root causes, or late recall. / 发现经验不具体、根因错误或召回太晚。 |
| Lesson update timeliness / 经验更新及时率 | repeated failures updated within SLA / repeated failures requiring update / 规定时间内更新经验次数 / 需更新重复失败次数 | Ensure continuous correction. / 保证经验持续校正。 |
| Failure-to-enable cycle time / 失败到启用周期 | average time from failure event to enabled lesson / 从失败发生到经验启用的平均时长 | Measure learning speed. / 衡量经验沉淀速度。 |

### Governance Safety / 治理安全

| Metric / 指标 | Formula / 定义 | Use / 用途 |
|---|---|---|
| Unreviewed recall block rate / 未审查召回拦截率 | blocked unenabled recall attempts / all unenabled recall attempts / 被拦截的未启用召回次数 / 未启用召回尝试次数 | Validate the review state machine. / 校验状态机有效性。 |
| Source completeness / 来源完整率 | entries with source, generated time, review info, and scope / all entries / 带来源、生成时间、审查信息和范围的日记数 / 日记总数 | Prevent source-free memory. / 防止无来源记忆。 |
| Scope isolation hit rate / 范围隔离命中率 | recalls correctly limited by tenant, project, environment, or organization / all recalls / 被正确限制在范围内的召回数 / 召回总数 | Prevent cross-scope contamination. / 防止跨范围污染。 |
| Suspected memory poisoning rate / 记忆污染疑似率 | entries flagged for abnormal source, lesson, or recall behavior / all entries / 来源、教训或召回异常的日记数 / 日记总数 | Detect unsafe long-term memory. / 发现不安全长期记忆。 |
| Historical conflict rate / 历史经验冲突率 | recalls conflicting with current facts or rules / total recalls / 与当前事实或规则冲突的召回次数 / 召回总数 | Detect stale or over-general lessons. / 发现过期或过度概括经验。 |

### Cost And Load / 成本与负载

| Metric / 指标 | Formula / 定义 | Use / 用途 |
|---|---|---|
| Average recalled cards / 平均召回条数 | recalled cards per recall event / 每次召回注入的经验卡数量 | Control noise. / 控制噪声。 |
| Lesson-card context share / 经验卡上下文占用 | lesson-card tokens / total context tokens / 经验卡 token 数 / 总上下文 token 数 | Protect task context. / 保护任务核心上下文。 |
| Review backlog / 审查积压量 | pending-review diary count / 待审查失败日记数量 | Measure governance load. / 衡量治理负担。 |
| Per-lesson preservation cost / 单条失败沉淀成本 | labor, time, compute, and storage from candidate to enabled lesson / 从候选到启用所需人力、时间、计算和存储成本 | Assess scalability. / 评估规模化能力。 |

## Minimal Probe Set / 最小探针集

Start with: candidate capture rate, four-layer evidence completeness, actionable root-cause rate, review pass rate, recall effectiveness, missed recall rate, false reminder rate, and repeated failure rate. / 最小落地先采集：失败候选捕获率、四层证据完整率、根因可行动率、审查通过率、召回有效率、漏召回率、误提醒率和重复失败率。

## Probe-To-Workflow Corrections / 探针反向修正流程

| Probe signal / 探针信号 | Workflow correction / 执行流程修正 |
|---|---|
| Low capture rate or low silent-failure discovery / 捕获率低或静默失败发现率低 | Add capture entry points, semantic acceptance checks, human feedback loops, and end-of-task reconciliation. / 增加捕获入口、语义验收、人工反馈回流和任务结束对账。 |
| Low four-layer evidence completeness / 四层证据完整率低 | Require workspace, narrative, mechanical-state, and raw-observation evidence before review. / 审查前强制补齐工作区、叙事、机械状态和原始观测证据。 |
| Low actionable root-cause rate / 根因可行动率低 | Add root-cause review templates, reject vague causes, bind causes to mechanisms, and assign remediation owners. / 增加根因审查模板，拒绝泛化根因，要求根因绑定机制并指定补救负责人。 |
| High missed recall or low structured recall share / 漏召回率高或结构化召回占比低 | Add task-family, tool, mechanical-parameter, and category indexes; move recall before high-risk actions. / 增加任务族、工具、机械参数和分类索引，并把召回前移到高风险动作前。 |
| High false reminder rate or high context share / 误提醒率高或上下文占用高 | Limit recall count, prioritize high risk, downgrade low risk, archive stale lessons, and narrow recall conditions. / 限制召回数量，优先高风险，低风险降权，归档旧经验，并缩窄召回条件。 |
| Unreviewed recall attempts or poisoning signals / 未审查召回或污染信号 | Block unenabled recall, isolate source-free lessons, enforce scope boundaries, and send abnormal lessons to review. / 阻断未启用召回，隔离无来源经验，强制范围边界，并将异常经验送审。 |

## Output Templates / 输出模板

### Single-Task Observation / 单次任务观测

```text
Task ID / 任务编号：
Task family / 任务族：
Risk level / 风险等级：
Failure lessons recalled / 是否召回失败经验：
Recall position / 召回位置：
Recalled card count / 召回条数：
Changed plan / 是否改变计划：
Changed parameters / 是否改变参数：
Added validation / 是否增加校验：
Escalated to human / 是否升级人审：
Failure occurred / 是否发生失败：
Failure boundary / 失败边界：
Failure category / 失败分类：
Diary draft created / 是否生成失败日记草稿：
Evidence completeness / 证据完整性：
Root-cause quality / 根因质量：
Missing data / 需要补全的数据：
Workflow correction / 执行流程修正建议：
```

### Periodic Summary / 周期汇总

```text
Period / 统计周期：
Total tasks / 任务总数：
Failure candidates / 失败候选数：
Diary drafts / 失败日记草稿数：
Pending review / 待审查数：
Enabled lessons / 已启用数：
Archived lessons / 已归档数：
Repeated failure rate / 重复失败率：
Recall effectiveness / 召回有效率：
Missed recall rate / 漏召回率：
False reminder rate / 误提醒率：
Four-layer evidence completeness / 四层证据完整率：
Actionable root-cause rate / 根因可行动率：
Unreviewed recall block rate / 未审查召回拦截率：
Scope isolation hit rate / 范围隔离命中率：
Highest-risk task family / 最高风险任务族：
Highest-risk tool / 最高风险工具：
Highest-risk mechanical parameter / 最高风险机械参数：
Process gaps / 流程缺口：
Recommendations / 修正建议：
```
