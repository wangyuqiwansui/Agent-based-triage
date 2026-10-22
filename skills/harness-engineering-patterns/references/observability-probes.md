# Observability Harness Probes / 可观测性框架探针

Name / 名称: Business Outcome Observation Probes / 业务结果观测探针

Version / 版本: `0.1.0`; status / 状态: `draft`; implementation / 实现: `specification_only`

Pattern / 模式: `PATTERN_0049`; source alias / 来源别名: `PATTERN_OBSERVABILITY_0002`

Produce trustworthy, correlated facts before deriving metrics. / 先产生可信且可关联的事实，再派生指标。

## Quick Navigation / 快速导航

- [Probe catalog / 探针目录](#probe-catalog)
- [Metric definitions / 指标定义](#metric-catalog)
- [Acceptance matrix / 验收矩阵](#acceptance)
- [Completion contract / 补全契约](observability-contract.md#completion-protocol)

## Usage and workflow / 用法与流程

Read the [execution flow](observability-execution-flow.md) and [shared contract](observability-contract.md). Independently reconstruct legacy evidence, interact with current execution, or combine lightweight real-time checks with offline analysis. Process-local hooks, middleware, sidecars, collectors, bus consumers and batch jobs share semantics, not necessarily deployment. / 阅读执行流程及共享契约；可独立重建遗留证据、与当前执行交互，或实时轻量检查加离线分析；进程钩子、中间件、旁车、采集器、总线消费者及批处理共享语义，不要求同一部署。

Workflow: freeze scenario/version and expected inventories → authorize source reads → ingest/redact/deduplicate → establish scoped identities and causal links → validate required events, controls, versions and state fidelity → request and validate bounded completion → derive qualified metrics → route alerts and seal an evidence report. All business transitions stay with execution. / 流程：冻结场景版本及预期清单→授权读取→采集脱敏去重→建立范围标识及因果链→校验必要事件、控制、版本与状态保真→请求并验证有界补全→派生合格指标→路由告警并封存证据报告。业务迁移始终由执行方负责。

Every configured probe declares ID/name/version, purpose/scope, trigger, required/optional inputs, source priority, collection mode, validation rules, facts/metrics, missing/conflict policies, severity, enforcement owner, privacy/access/retention and responsible owner. A blocking flag describes an execution policy, not new permission for the probe. / 每个探针配置含编号名称版本、目的范围、触发、必需可选输入、来源优先级、采集方式、规则、事实指标、缺失冲突策略、严重度、执行门负责人、隐私访问留存及责任人；阻断标记表示执行策略，不给探针新增权限。

The ten layers are identity, context/version, proposal/decision, governance, tool/state fidelity, async/recovery, business result, public commitment, feedback/evolution and record governance. The following 45 IDs preserve source identity; the [source map](observability-source-map.json) records exact lines and hashes. They are not replacements for the shared `PATTERN_0052` probe catalog. / 十层为身份、上下文版本、提案决策、治理、工具状态保真、异步恢复、业务结果、对外承诺、反馈演进与记录治理。以下 45 个编号保留来源身份，映射记录精确行号和哈希；不替换共享探针目录。

<a id="probe-catalog"></a>
## Probe catalog / 探针目录

| ID | Source requirement / 来源要求 | Trigger, validation and response / 触发、校验及响应 |
| --- | --- | --- |
| PROBE_RUN_001 | 运行身份连续性；运行开始、跨服务、运行关闭；`task_id`、`run_id`、`trace_id` 是否连续；请求补传；无法关联则标记孤儿事件 | Run identity continuity: at start, boundaries and close, validate task/run/trace links; request missing context or quarantine orphans. |
| PROBE_CTX_001 | 输入工件版本；上下文固定、交接、执行前；实际工件版本是否符合任务要求；版本冲突时暂停 | Input artifact versions: at context freeze, handoff and preflight, compare exact versions; pause on conflict. |
| PROBE_CTX_002 | 模型与提示版本；模型调用；是否记录真实使用版本；缺失时影响重放评分 | Model/prompt versions: on each model call, capture actual versions; missing versions limit replay. |
| PROBE_CTX_003 | 工具可见性快照；规划与工具选择前；当时可用、被过滤和不可见工具；缺失时无法判断“没选”还是“看不见” | Tool visibility: before planning/selection, snapshot available and filtered tools/reasons; distinguish not chosen from unavailable. |
| PROBE_CTX_004 | 规则与权限快照；控制校验前；是否保存生效规则和权限；高风险缺失时阻断 | Policy/permission snapshots: before control checks, retain effective rules and authority; required high-risk gaps block dispatch. |
| PROBE_PLAN_001 | 提案版本绑定；提案形成、批准、执行前；批准和执行是否指向同一版提案；不一致时阻断 | Proposal binding: at proposal, approval and preflight, compare exact versions; mismatch blocks dispatch. |
| PROBE_PLAN_002 | 路由决策；路由发生；候选路径、选择理由、规则版本；记录缺口，必要时转人工 | Routing decisions: on routing, retain candidates, reasons and rule version; request missing evidence or human review. |
| PROBE_PLAN_003 | 并行分支登记；分支创建与聚合；分支是否完整登记、是否有遗漏；聚合前补全或标记部分结果 | Parallel inventory: register all expected branches before launch and validate at gather; preserve absent/partial branches. |
| PROBE_PLAN_004 | 循环终止条件；每次迭代；次数、成本、变化和终止原因；超限时暂停 | Loop termination: each iteration records count, cost, progress and stop reason; exceeded limits pause work. |
| PROBE_PLAN_005 | 层级委派边界；委派和回收；子任务边界、验收和责任主体；边界不明时拒绝委派 | Delegation boundaries: on delegation/return, check scope, acceptance and owner; unclear responsibility prevents dispatch. |
| PROBE_GOV_001 | 批准证据匹配；控制校验、外部动作前；批准主体、对象、范围、版本、有效期；高风险缺失或不匹配时阻断 | Approval match: before effects, verify approver, object, scope, version and expiry; required missing/mismatched evidence blocks. |
| PROBE_GOV_002 | 额度预留与消费；预留、执行、释放；预留、消费、释放是否闭环；超额时阻断；悬挂时告警 | Budget lifecycle: check reservation, consumption and release; overrun blocks and stranded reservations alert. |
| PROBE_GOV_003 | 实际执行身份；工具调用前；计划身份与实际身份是否一致；不一致时阻断或转人工 | Actual identity: before tools, compare planned and actual actor; mismatch blocks or escalates. |
| PROBE_GOV_004 | 权限边界；工具调用前；当前权限是否覆盖对象、动作和环境；越权时阻断 | Permission boundary: before tools, check object/action/environment scope; deny unauthorized execution. |
| PROBE_GOV_005 | 自治等级适配；高风险任务开始；智能体当前自治等级是否足够；不足时降级或人工批准 | Autonomy suitability: at high-risk intake, compare permitted autonomy with task risk; downgrade or seek authorized approval. |
| PROBE_GOV_006 | 控制绕过检测；运行关闭；应出现的批准、额度、权限记录是否存在；严重告警并启动审计 | Control bypass: at close, compare required controls with actual actions; raise critical audit findings on confirmed bypass. |
| PROBE_TOOL_001 | 工具请求响应完整性；工具调用；请求、响应、版本、耗时和回执是否齐全；请求原始引用或标记不可重放 | Tool request/response: on calls, capture references, versions, duration and receipts; request originals or mark replay unavailable. |
| PROBE_TOOL_002 | 业务状态保真；响应转换后；原始状态与下游状态是否一致；状态丢失时严重告警 | State fidelity: after mapping, compare raw and downstream semantics; alert on lost or promoted state without evidence. |
| PROBE_TOOL_003 | 幂等与重复副作用；重试、超时、回调；幂等键是否复用，是否重复办理；发现风险时暂停重试 | Idempotency: on retry, timeout or callback, verify key reuse and effect uniqueness; pause unsafe retries. |
| PROBE_TOOL_004 | 参数与批准一致性；工具调用前后；实际参数是否超出批准范围；超范围时阻断 | Parameter match: around calls, compare actual parameters with approved scope; block excess scope. |
| PROBE_TOOL_005 | 工具结构漂移；响应解析；新字段、未知状态、结构变化；进入隔离解析并告警 | Schema drift: when parsing, isolate new/unknown fields and statuses; alert rather than assume success. |
| PROBE_TOOL_006 | 回退与替代工具；回退发生；是否记录回退原因和差异风险；需要重新控制校验时触发 | Fallback tools: on fallback, record reason and changed risk; rerun controls where required. |
| PROBE_ASYNC_001 | 业务申请号稳定性；异步受理；是否保存稳定外部申请号；缺失时禁止盲目重试 | Stable application ID: on asynchronous acceptance, persist external identity; missing identity prohibits blind retry. |
| PROBE_ASYNC_002 | 回调关联；回调到达；回调是否接回正确任务和提案；无法关联则进入隔离队列 | Callback correlation: on arrival, authenticate and join exact task/proposal; quarantine ambiguous callbacks. |
| PROBE_ASYNC_003 | 超时查询；等待超时；是否查询权威系统而非直接重试；违规时阻断重试 | Timeout query: on waiting deadline, query original authority before retry; block blind resubmission. |
| PROBE_ASYNC_004 | 跨运行恢复；新运行接手；新旧运行、未决事项和状态是否接续；生成补全请求 | Cross-run recovery: on resumption, link old/new runs, pending obligations and state; request missing evidence. |
| PROBE_ASYNC_005 | 交接工件验收；交接发生；工件版本、回执和待办是否完整；验收失败时停在交接点 | Handoff acceptance: verify artifact version, receipt and pending duties; stop at failed handoff. |
| PROBE_RESULT_001 | 权威结果确认；运行关闭前；是否从指定业务系统确认最终结果；高风险任务不得关闭为成功 | Authoritative result: before success closure, verify designated business evidence; no authority means no success claim. |
| PROBE_RESULT_002 | 期望与实际差异；结果确认后；每个验收项是否满足；生成差异明细 | Expected/actual delta: after confirmation, compare every acceptance item; report differences. |
| PROBE_RESULT_003 | 接口成功但任务未完成；工具结束、结果确认；技术成功与业务结果是否分离；生成专用异常 | Technical/business mismatch: after tools and confirmation, distinguish technical success from task completion; emit a dedicated anomaly. |
| PROBE_RESULT_004 | 结果未知保护；超时、冲突；未知状态是否阻止重复副作用；未保护时严重告警 | Unknown-result protection: on timeout/conflict, preserve pending effects and prevent duplicate writes; missing protection is critical. |
| PROBE_COMMIT_001 | 对外承诺一致性；答复发送前；表达是否超过当前业务状态；不一致时阻断答复 | Public commitment: before reply, compare material claims with current proven state; block unsupported claims. |
| PROBE_COMMIT_002 | 工件采用与验收；交付后；产物是否被使用、接受或创建后续任务；记录业务采用事实 | Artifact adoption: after delivery, record actual use, acceptance or follow-up task; distinguish adoption from correctness. |
| PROBE_FB_001 | 用户反馈关联；投诉、评分、人工纠正；反馈是否关联到具体运行和阶段；无法关联则进入人工匹配 | Feedback linkage: on complaint/rating/correction, join exact run/stage; ambiguous links require review. |
| PROBE_FB_002 | 失败样本入集；根因确认后；输入、预期、版本和模拟响应是否齐全；不完整时不可进入回归集 | Failure dataset: after confirmed cause, require input, expected output, versions and recorded/mock responses before regression admission. |
| PROBE_EVAL_001 | 回归重放；版本变更前；新版是否在历史样本上通过；未通过时阻止发布建议 | Regression replay: before version release, run isolated historical cases; failed required cases block a release recommendation. |
| PROBE_EVOLVE_001 | 规则调整因果；规则或权限变更；调整是否有事故、评测或业务依据；无依据变更告警 | Rule-change causality: on policy/permission changes, link incident, evaluation or business basis; alert on unsupported changes. |
| PROBE_EVOLVE_002 | 调整后效果；新规则生效后；指标是否改善，是否产生副作用；触发回滚评审 | Post-change effect: after a new policy, compare qualified outcomes and side effects; recommend rollback review when warranted. |
| PROBE_REC_001 | 必需事件完整性；阶段结束、运行关闭；场景要求的事件是否齐全；生成缺口清单 | Required-event inventory: at stage/run close, compare with scenario obligations; report all gaps. |
| PROBE_REC_002 | 顺序与因果一致性；事件到达；时间、序号、父子和业务关系是否冲突；保留冲突，不强行排序 | Order/causality: on ingestion, check time, sequence, parents and business links; preserve conflicts rather than invent order. |
| PROBE_REC_003 | 防篡改与更正链；写入、读取、导出；校验值、更正引用是否有效；发现异常立即审计 | Integrity/corrections: at write/read/export, verify content checks and correction references; audit integrity failures. |
| PROBE_REC_004 | 敏感信息泄露；写入前后；密码、令牌、证件号是否进入记录；阻断写入并隔离 | Sensitive-field leak: before/after persistence, detect secrets and identifiers; block unsafe writes and isolate evidence. |
| PROBE_REC_005 | 访问权限；查询与导出；访问者是否只看到必要内容；拒绝访问并记录 | Access control: at query/export, enforce least privilege; deny and audit excess access. |
| PROBE_REC_006 | 保留期限；周期任务；是否按类型保留或删除；生成合规任务 | Retention: on scheduled checks, enforce record-class retention/deletion with authorized owners. |
| PROBE_REC_007 | 采集器健康；持续；丢失、延迟、积压和存储失败；触发降级或暂停策略 | Collector health: continuously measure loss, delay, backlog and storage errors; apply dependency-aware degradation or pause. |

<a id="metric-catalog"></a>
## Metric definitions / 指标定义

OBM01–OBM42 correspond to source section 13; OBM43–OBM50 correspond to probe-quality measures in section 21.2. OBM is a local documentation namespace; all 50 definitions are `specification_only`, have no dedicated calculator here, and are not automatically gating. / 前 42 项对应原文第 13 节，后 8 项对应第 21.2 节探针质量指标。OBM 是本地文档编号；50 项均为规格，当前没有专用计算器，不能自动作为门槛。

Apply these rules to every row / 每行统一遵循：

- Declare owner, definition version, scenario/risk/tool/workflow version buckets, population source, unique grain, numerator/denominator or distribution samples, unit, window/cohort, cutoff/watermark, coverage and evidence. Default to a task-entry cohort `[start,end)` observed at an explicit cutoff; use declared run/event/action/artifact populations when the row requires them. Do not mix retries/runs with tasks. / 声明负责人、口径版本、场景风险工具工作流分桶、总体来源、唯一粒度、分子分母或分布样本、单位、窗口队列、截止水位、覆盖与证据；默认使用进入任务的左闭右开队列，在明确截止时观测；运行事件动作工件指标声明各自总体，不能混淆重试运行和任务。
- Ratios are fractions (display as percent); duplicate-effect count per task can exceed one and is an intensity, not probability. Time is milliseconds; tokens are tokens; money has one stated currency; bytes, compute and network remain separate. Report completed distributions plus pending age/censored counts, not only averages. / 比值为比例（可显示百分比）；每任务重复副作用数可能超过一，属于强度而非概率。时间用毫秒，令牌按个，金额声明单一币种；字节、计算、网络分开。完成耗时之外报告未决年龄及截尾数，不能只报均值。
- Missing denominators/authority/labels → `unknown`; known empty applicable population → `not_applicable`; incomplete coverage → `partial`; too few reviewed samples → `insufficient_sample`; fully qualified data → `available`. Missing is never zero or success. Show coverage alongside observed ratios; do not silently exclude unavailable or overdue items. / 分母权威真值缺失记未知；已知适用总体为空记不适用；覆盖不全记部分；复核样本不足记样本不足；合格数据记可用。缺失不等于零或成功，观测比值必须带覆盖率，不暗删不可得或到期项。
- Use independently expected event/branch/action inventories for completeness and loss, an authority-owned task ledger for result populations, access audit for security, reviewed labels for correctness, and matched enabled/disabled workloads for overhead. Collector records alone cannot prove that unobserved events never happened. / 完整率丢失率用独立预期事件分支动作清单，结果总体用权威任务账，安全用访问审计，正确性用复核标签，开销用匹配启停工作负载；采集器单方记录不能证明未观测事件未发生。
- Exclude only documented, rule-validated not-applicable obligations and report their counts. Deduplicate exact event identities, quarantine contradictory duplicates, retain late data in new metric revisions and never mutate historical windows silently. Thresholds need an owner, minimum samples, evaluation evidence and sustained window; per-instance unauthorized effects or unsupported success claims escalate without waiting for an average. / 仅排除有规则验证的不适用责任并报告数量；同事件去重，矛盾重复隔离，迟到数据进入新指标版本，不静默改写历史。门槛须有负责人、最小样本、评测证据及持续窗口；逐实例越权副作用或无据成功声明立即升级，不等待均值。

| ID | Source name and formula / 来源名称及公式 | Maintained definition / 维护口径 |
| --- | --- | --- |
| OBM01 | 真实完成率；已确认成功任务数 ÷ 已关闭任务数 | Confirmed completion: confirmed-success tasks / closed-disposition tasks; publish waiting/unknown cohort counts separately. |
| OBM02 | 结果未知率；结果未知任务数 ÷ 已进入执行任务数 | Unknown outcomes: unknown-result tasks / tasks that entered execution. |
| OBM03 | 部分完成率；部分完成任务数 ÷ 已关闭任务数 | Partial completion: partially completed tasks / closed-disposition tasks. |
| OBM04 | 接口成功但任务未完成率；技术成功且业务未成功任务数 ÷ 技术成功任务数 | Technical/business mismatch: technically successful tasks without confirmed business success / technically successful tasks; split waiting, unknown and failure. |
| OBM05 | 过度承诺率；对外表达高于业务状态的任务数 ÷ 已答复任务数 | Overcommitment: replied tasks whose claims exceed proven state / replied tasks, with assessed coverage. |
| OBM06 | 补偿率；发生补偿的任务数 ÷ 已产生副作用任务数 | Compensation: tasks requiring compensation / tasks with external effects; distinguish requested from confirmed compensation. |
| OBM07 | 业务采用率；被采纳工件数 ÷ 已交付工件数 | Adoption: adopted artifacts / delivered artifacts; use acceptance/use evidence, not creation logs. |
| OBM08 | 必需事件完整率；已取得必需事件数 ÷ 应有事件数 | Required-event completeness: received required obligations / independently expected required obligations, each once. |
| OBM09 | 因果链完整率；已建立有效因果关系数 ÷ 应有因果关系数 | Causal completeness: valid evidenced causal edges / expected causal edges. |
| OBM10 | 追踪上下文连续率；成功传递追踪标识的跨边界次数 ÷ 总跨边界次数 | Trace propagation: boundaries with correctly propagated context / independently inventoried crossed boundaries. |
| OBM11 | 业务申请号覆盖率；有稳定业务申请号的异步任务数 ÷ 异步任务数 | Application-ID coverage: asynchronous tasks with a stable external ID / asynchronous accepted tasks. |
| OBM12 | 版本快照覆盖率；版本字段齐全运行数 ÷ 总运行数 | Version coverage: runs with all applicable version snapshots / runs. |
| OBM13 | 工具状态保真率；原始状态与下游状态一致次数 ÷ 可比较次数 | State fidelity: comparable transformations preserving semantics / comparable transformations; report missing comparisons separately. |
| OBM14 | 对外答复可追溯率；可关联到业务状态和证据的答复数 ÷ 总答复数 | Reply traceability: replies linked to exact business state and evidence / replies. |
| OBM15 | 批准证据匹配率；批准范围与执行完全匹配次数 ÷ 需批准执行次数 | Approval match: executions with fully valid scope/version-bound approval / executions requiring approval. |
| OBM16 | 额度闭环率；完成预留、消费或释放闭环的额度项 ÷ 总额度项 | Budget closure: reservations with verified consumption or release reconciliation / reservation items; include pending ages. |
| OBM17 | 权限快照覆盖率；有有效权限快照的受控执行数 ÷ 受控执行总数 | Permission coverage: controlled executions with valid permission snapshots / controlled executions. |
| OBM18 | 控制绕过率；缺少必需控制但发生执行的次数 ÷ 受控执行总数 | Control bypass: executions confirmed to lack mandatory controls / controlled executions; unavailable evidence remains unresolved. |
| OBM19 | 自治等级越界率；实际风险超过自治等级的执行数 ÷ 总执行数 | Autonomy overreach: executions exceeding current autonomy / executions. |
| OBM20 | 规则调整可追溯率；有依据、决定者和生效版本的调整数 ÷ 总调整数 | Rule-change traceability: changes with basis, owner and effective version / rule changes. |
| OBM21 | 重试率；重试尝试数 ÷ 总尝试数 | Retry share: retry attempts / all attempts; retain logical-action linkage. |
| OBM22 | 重复副作用率；重复业务动作数 ÷ 有副作用任务数 | Duplicate-effect intensity: extra confirmed effects / tasks with effects; publish affected-task share separately. |
| OBM23 | 回调关联成功率；正确接回原任务的回调数 ÷ 总回调数 | Callback association: callbacks correctly linked to original tasks / callbacks under the declared delivery-deduplication policy. |
| OBM24 | 恢复成功率；正确接续并完成的恢复任务数 ÷ 恢复任务数 | Recovery completion: recovery tasks correctly resumed and completed / recovery tasks; retain unresolved population. |
| OBM25 | 平均定位时间；从投诉或告警到确定问题阶段的平均时长 | Mean diagnosis time: average elapsed time from complaint/alert to evidenced fault-stage identification; also publish unresolved ages. |
| OBM26 | 一次定位率；无需跨团队反复查询即可定位的事件数 ÷ 调查事件数 | First-pass localization: investigations localized without repeated cross-team queries / investigations, with reviewed outcomes. |
| OBM27 | 人工纠正率；被人工修改结果的任务数 ÷ 已评审任务数 | Human correction: tasks whose result was modified by a human / reviewed tasks; identify review selection. |
| OBM28 | 回归通过率；通过样本数 ÷ 回归样本总数 | Regression pass: passing cases / all scheduled regression cases; skipped and unrun cases remain visible. |
| OBM29 | 失败复现率；能在隔离环境复现的失败数 ÷ 选定失败数 | Failure reproduction: failures reproduced in isolation / failures selected for reproduction. |
| OBM30 | 根因确认率；已确认根因事件数 ÷ 已调查事件数 | Cause confirmation: investigations with independently confirmed cause / investigated incidents. |
| OBM31 | 反馈关联率；能关联到具体运行的反馈数 ÷ 总反馈数 | Feedback linkage: feedback items linked to a specific run / feedback items. |
| OBM32 | 成功任务单位令牌成本；总令牌消耗 ÷ 已确认成功任务数 | Tokens per success: all cohort token consumption, including failed attempts / confirmed-success tasks; token/task. |
| OBM33 | 成功任务单位计算成本；总计算成本 ÷ 已确认成功任务数 | Compute cost per success: all cohort compute cost, including failed attempts / confirmed-success tasks; declared currency/task. |
| OBM34 | 成功任务端到端耗时；从运行开始到业务结果确认的耗时分布 | Success latency: distribution from task start to authoritative business confirmation; milliseconds, with cross-run policy declared. |
| OBM35 | 失败任务耗时；失败或未知任务的耗时分布 | Failure/unknown latency: distributions until confirmed failure or measurement cutoff for unknown tasks; report censoring separately. |
| OBM36 | 探针延迟开销；启用探针后新增的端到端耗时 | Probe latency overhead: paired end-to-end latency with probes minus without probes on matched workloads; milliseconds. |
| OBM37 | 探针存储成本；单位任务观测数据量与保留成本 | Probe storage cost: bytes and retention cost per task over a declared retention horizon; separate units. |
| OBM38 | 敏感字段拦截率；写入前被正确识别并处理的敏感字段数 ÷ 检出的敏感字段数 | Sensitive-field interception: correctly handled detected sensitive fields before persistence / detected sensitive fields; not leak recall. |
| OBM39 | 未授权访问率；被拒绝或确认违规的访问数 ÷ 总访问数 | Unauthorized access: denied attempts and confirmed violations / access attempts, reported as separate series. |
| OBM40 | 采集丢失率；预期事件数与实际接收事件数的差额 ÷ 预期事件数 | Collection loss: independently expected events absent after the lateness cutoff / expected events; exclude exact duplicate deliveries. |
| OBM41 | 采集延迟；采集时间减业务事件时间的分布 | Ingestion lag: ingest time minus event time distribution, only for comparable clocks; milliseconds. |
| OBM42 | 更正链完整率；有原记录引用的更正数 ÷ 总更正数 | Correction linkage: corrections with valid original-record references / corrections. |
| OBM43 | 缺口发现率；已知缺口中被探针发现的比例 | Gap detection: independently known true gaps detected / all known true gaps in a labeled evaluation population. |
| OBM44 | 误报率；实际完整却被判断为缺失或冲突的比例 | False-positive rate: truly complete labeled items wrongly flagged missing/conflicting / truly complete labeled items. |
| OBM45 | 补全成功率；发出补全请求后成功关闭的缺口比例 | Completion success: requests whose original required fields were validated closed / issued completion requests; split pending/overdue and rejected. |
| OBM46 | 关联准确率；事件被关联到正确任务、运行和业务对象的比例 | Correlation accuracy: independently verified correct joins / independently reviewed joins, with sampling and coverage disclosed. |
| OBM47 | 调查缩短时间；启用探针前后平均定位时间差 | Diagnosis time reduction: matched pre-probe mean diagnosis time minus post-probe mean; include unresolved ages and selection controls. |
| OBM48 | 重放可用率；选定运行中能形成有效重放包的比例 | Replay usability: selected runs with validated isolated replay bundles / selected runs. |
| OBM49 | 探针开销；延迟、计算、存储和网络开销 | Probe overhead: paired added latency, compute, bytes stored and network traffic; retain a vector, never add unlike units. |
| OBM50 | 隐私事件数；探针导致的敏感数据暴露或越权访问事件 | Privacy incidents: distinct confirmed probe-caused exposure or unauthorized-access incidents in the window; retain severity and unresolved allegations. |

### Interpretation safeguards / 解释约束

OBM01 uses task resolution in the declared cohort, not closed-run count; publish waiting/unknown populations and ages so closure policy cannot inflate success. OBM04 includes legitimate waiting/unknown separately from confirmed failure; it is a mismatch diagnostic, not a failure or blame rate. OBM13 permits a state upgrade only with new authority evidence under a versioned mapping. OBM15 validates current exact action bindings, not just approval existence. / OBM01 完成率使用队列内任务处置，不以关闭运行计数，并展示等待未知总体年龄，防止靠关闭策略美化成功率。OBM04 接口业务差异率拆分合法等待未知与确认失败，不作为失败或归责率。OBM13 状态保真允许有新权威证据及版本化映射的升级。OBM15 批准匹配验证当前精确动作绑定，不能只看有无审批。

OBM22 counts extra confirmed business effects, not repeated callback deliveries; OBM23 separately evaluates callback association under its declared deduplication policy. OBM32–33 include failed/retried effort in the same cohort, with no division if there are no confirmed successes. OBM38 measures handling among detected sensitive fields, not recall; detecting missed secrets requires independent labels. OBM39 reports denied attempts and confirmed violations separately because successful defenses are not breaches. OBM40 requires an independent expected inventory and a lateness policy. OBM41 requires comparable clocks. OBM44 is false-positive rate over reviewed truly complete items; false-discovery share among alerts is a separate statistic. / OBM22 统计额外已确认业务副作用，不统计重复回调投递；OBM23 按明示去重策略另行评价回调关联。单位成功成本包含同队列失败重试消耗，无成功样本时不做除法。敏感字段拦截率只评价已检出字段，不是召回率；漏检须独立真值。越权访问拆分被拒尝试与确认违规，成功防御不是泄露。丢失率须有独立预期清单和迟到策略，延迟须可比时钟。误报率以复核后真正完整项为分母；告警中的错误占比属于另一指标。

No metric trend proves causation; adoption does not prove correctness; incomparable versions or censored windows cannot support an improvement claim. These clarifications are maintained engineering decisions; the original source formula text remains preserved for review. / 指标趋势不证明因果，采用不证明正确，不可比版本或截尾窗口不支持改善结论；这些细化属于维护版工程决定，原公式文本保留供核对。

<a id="acceptance"></a>
## Acceptance matrix / 验收矩阵

All cases are `not_executed`. Source-derived OBT cases and locally added OBX boundary cases define required fixtures, expected behavior and observable evidence; asset tests below do not run these business scenarios. / 全部用例状态为未执行。来源 OBT 与新增 OBX 边界用例定义输入、预期及可观察证据；资产测试不等于执行这些业务场景。

| ID | Source scenario / 来源场景 | Expected behavior and evidence / 预期行为及证据 |
| --- | --- | --- |
| OBT01 | 正常完成 | Normal completion: exact authority receipt permits success; linked reply and evidence bundle agree. / 正常完成：精确权威回执允许成功，关联答复与证据包一致。 |
| OBT02 | 等待审核 | Pending review: HTTP success stays waiting; no completed claim; pending identity and query obligation persist. / 等待审核：接口成功仍保留等待，不称完成，持久化未决号及查询责任。 |
| OBT03 | 明确拒绝 | Explicit rejection: preserve authority rejection and safe public reason; no success claim. / 明确拒绝：保留权威拒绝与可公开原因，不称成功。 |
| OBT04 | 工具超时但业务成功 | Timeout but business succeeded: query original identity, find receipt, confirm once; no second effect. / 工具超时但业务成功：查询原标识，找到回执并确认，不产生第二次副作用。 |
| OBT05 | 工具超时且业务未生效 | Timeout and verified no effect: authority proves absence for the exact request; only then revalidate current controls for a retry. / 工具超时且未生效：权威证明精确请求未生效，之后重验当前控制再决定重试。 |
| OBT06 | 重复回调 | Duplicate callback: authenticated exact duplicate is idempotent; same-ID differing content is quarantined. / 重复回调：可信同内容幂等，同号异内容隔离。 |
| OBT07 | 工件版本错误 | Wrong artifact: preflight/handoff rejects incorrect version and retains expected/actual digests. / 工件错版：预检交接拒绝错误版本，保留预期实际摘要。 |
| OBT08 | 批准票错版 | Wrong approval version: reject dispatch and record mismatched proposal/approval binding. / 批准票错版：拒绝派发并记录错配绑定。 |
| OBT09 | 额度不足 | Insufficient budget: atomic reservation fails; no effect occurs; record denial. / 额度不足：原子预留失败，不产生效果并记录拒绝。 |
| OBT10 | 权限不足 | Insufficient permission: current actor scope check denies dispatch with evidence. / 权限不足：当前主体范围校验拒绝派发并留证。 |
| OBT11 | 记录器故障 | Recorder failure: missing mandatory durable audit blocks protected dispatch; preserve a separate health incident and recovery evidence. / 记录器故障：必要持久审计缺失阻断受保护派发，保留独立健康事故及恢复证据。 |
| OBT12 | 敏感字段误写 | Sensitive field written: pre-write redaction/denial; if detected after write, isolate and apply authorized removal/access audit. / 敏感字段误写：写前脱敏拒绝，写后发现则隔离并落实获准清除及访问审计。 |
| OBT13 | 对外答复过度承诺 | Overcommitted reply: evidence comparison blocks or corrects the draft before publication; retain the verdict. / 对外过度承诺：发布前依证据阻断或修正草稿，保留裁定。 |
| OBT14 | 跨运行恢复 | Cross-run recovery: same task/application, new run, old-run link, accepted handoff and pending query ownership survive restart. / 跨运行恢复：任务申请号不变，新运行关联旧运行，交接验收与未决查询责任跨重启保留。 |
| OBT15 | 重放隔离 | Replay isolation: recorded/mock adapters only; attempted production payment/coupon/delete/release access is denied with test evidence. / 重放隔离：只使用录制模拟适配器，访问真实付款发券删除发布接口的尝试被拒并有测试证据。 |

| ID | Local boundary scenario / 本地边界场景 | Expected behavior and evidence / 预期行为及证据 |
| --- | --- | --- |
| OBX01 | Cross-tenant same business ID / 跨租户同业务号 | Reject join, retain isolated events and access denial. / 拒绝关联，保留隔离事件及访问拒绝。 |
| OBX02 | Same event ID, different payload / 同事件号不同载荷 | Conflict quarantine, neither silent overwrite nor metric double count. / 隔离冲突，不覆盖也不双计。 |
| OBX03 | Late/old callback after newer success / 成功后迟到旧回调 | Authenticate and retain history; no state regression; report revision records decision. / 认证后保留历史，不降级状态；报告修订记录决定。 |
| OBX04 | Optional probe down, local controls complete / 探针离线但本地控制完整 | Policy-governed execution and durable backfill, distinct from missing mandatory audit. / 按策略执行并持久补传，与必要审计缺失区分。 |
| OBX05 | Forged/stale/out-of-scope gap response / 伪造陈旧越范围补数 | Reject with per-field receipt; old target and open gap unchanged; authenticated exact retry idempotent. / 逐字段拒绝回执，原目标与缺口保持，可信相同重试幂等。 |
| OBX06 | Patch attempts approval/status/budget write / 补丁试图写批准状态预算 | Whitelist rejection and audit; no business mutation. / 白名单拒绝并审计，无业务改动。 |
| OBX07 | Crash after intent commit or after external effect / 意图持久化或外部生效后崩溃 | Recover durable intent, query same request/application, preserve unknown reservation and prevent duplicate dispatch. / 恢复意图，查询同请求申请，保留未知占用并防止重复派发。 |
| OBX08 | Out-of-order/skewed clocks / 乱序与时钟偏差 | Preserve causal partial order and clock quality; unreliable latency is unknown. / 保留因果偏序和时钟质量，不可靠延迟记未知。 |
| OBX09 | Missing, empty and sampled populations / 缺失空集及采样总体 | Unknown vs not-applicable vs partial remain distinct; independent denominator and coverage retained. / 区分未知不适用部分，保留独立分母与覆盖。 |
| OBX10 | Waiting run closed then process restarted / 等待运行关闭后重启 | Durable owner/deadline/query survives; new run links task and old run; no lost unresolved obligation. / 责任期限查询可恢复，新运行关联任务及旧运行，不丢未决责任。 |
| OBX11 | Cancellation or compensation without receipt / 无回执取消或补偿 | Keep requested/unknown effect state; refuse cancelled/compensated final claim. / 保留已请求或未知效果，拒绝已取消已补偿终态。 |
| OBX12 | Source expires or approved payload deletion / 来源过期或获准删除载荷 | Keep permitted tombstone/provenance and explicit gap, no recovery by copying deleted secrets. / 保留允许的墓碑来源及明确缺口，不复制应删秘密补全。 |

## Report, alerts and replay / 报告、告警与重放

Per-run report: scope/profile/schema versions; required/completed probes and independent coverage; observed/inferred/missing/conflict/not-applicable facts; technical/acceptance/business states; commitment consistency including unknown; approval/budget/permission evidence status; gap request/response/adoption ledger; alerts/owners/delivery receipts; evidence index and replay readiness with limitations. A global confidence score never suppresses a critical gap. / 单次报告含范围配置结构版本、应有完成探针及独立覆盖、五类事实状态、技术受理业务状态、含未知的承诺一致性、批准预算权限证据状态、补数收发采纳账、告警负责人送达回执、证据索引及重放可用性限制；总置信分不得遮蔽关键缺口。

Investigate a complaint through feedback → exact reply version → contemporaneous business state → raw tool response → proposal/control bindings → actual actor → authority receipt. Start with the business outcome, then workflow, then local components. Record the broken edge and whether evidence was never generated, not collected, unlinked, semantically wrong or unavailable at the authority. / 投诉沿反馈→精确答复版本→当时业务状态→工具原始响应→提案控制绑定→实际主体→权威回执调查；先查业务结果，再查流程，最后查组件。记录断点及未生成、未采集、未关联、含义错误或权威缺失的原因。

Information records facts; reminders request completion; warnings limit closure or seek review; critical/blocking findings propose affected-stage pause or denial to the authorized execution gate. Deduplicate scoped alerts, retain severity and repeats, require an owner and delivery acknowledgment, and escalate overdue unhandled alerts. Do not infer alert delivery from enqueue success. / 信息级记事实，提醒级请求补全，警告级限制关闭或请求复核，严重阻断级向授权执行门建议暂停拒绝相关阶段；按范围去重，保留严重度次数，明确负责人及送达回执，未处理到期告警升级；入队成功不等于送达。

Replay bundles contain sanitized request/expected outcome, historical input/proposal/control/context versions, recorded tool responses, authority receipts, original reply and a prohibited-effect list. Choose read-only reconstruction, adapter/decision/workflow replay or batch regression; preserve new-version output separately. Enforce the isolation boundary in the contract. / 重放包含脱敏请求预期、历史输入提案控制上下文版本、录制工具响应、权威回执、原答复及禁止副作用清单；按需只读重建、适配决策工作流重放或批量回归，新版输出分存，并落实契约隔离边界。

## Constraints and maintenance / 约束与维护

Never fabricate a missing result, approval or source; never let a probe repair business truth. Version joins, mappings, profiles and metrics; preserve append-only corrections and unresolved conflicts. Execute `scripts/validate_observability_docs.py` and the full Skill validator after edits; regenerate the repository HTML. Those checks establish source/navigation integrity only. / 不得编造缺失结果、批准或来源，探针不得修写业务真值。关联、映射、配置及指标均版本化，保留追加更正和未决冲突。修改后运行专用及完整技能校验器并生成仓库 HTML；这些检查只证明来源导航完整性。
