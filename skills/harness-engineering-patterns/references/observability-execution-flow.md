# Observability Execution Flow / 可观测性执行流程

Name / 名称: Business Outcome Observability / 业务结果可观测性

Version / 版本: `0.1.0`; status / 状态: `draft`; implementation / 实现: `specification_only`

Pattern / 模式: `PATTERN_0049`; source alias / 来源别名: `PATTERN_OBSERVABILITY_0001`

Make every important transition attributable to inputs, control evidence and a confirmed result. / 让每个关键迁移都能追溯到输入、控制证据和已确认结果。

## Quick Navigation / 快速导航

- [Execution stages / 执行阶段](#execution-steps)
- [Topology mounts / 拓扑挂载](#topology)
- [State and confirmation / 状态与确认](observability-contract.md#status-contract)
- [Acceptance matrix / 验收矩阵](observability-probes.md#acceptance)

## Usage, inputs and outputs / 用法、输入与输出

Use for governed tools, asynchronous effects, delivery and complaint reconstruction; follow the [shared contract](observability-contract.md) and [independent probes](observability-probes.md). The [source map](observability-source-map.json) binds the original 13 stages to OBE01–OBE13; these are maintained bilingual specifications, not executed tasks. / 适用于受治理工具、异步副作用、交付和投诉重建；遵循共享契约及独立探针。来源映射将原文 13 阶段映射到 OBE01–OBE13；这是双语维护规格，不代表任务已执行。

Required inputs: scoped task/run identity; objective and item-level expected result; authority and confirmation deadline; actor/risk/reversibility; input versions; policy, permission and visible-tool snapshots; workflow/model/prompt/tool/schema versions. Conditional controls: immutable proposal/version/digest, approval, budget reservation, idempotency and parent/handoff bindings. The external application ID is required once issued, not invented before the service returns it. / 必需输入为带范围的任务运行标识、目标及逐项预期、权威来源和确认期限、主体风险可逆性、输入版本、规则权限及可见工具快照、工作流模型提示工具结构版本；条件控制含不可变提案版本摘要、批准、预算预留、幂等及父子交接绑定。外部申请号在服务生成后必需，不能在响应前虚构。

Output `execution_result`: task/run, final disposition, separate technical/acceptance/business statuses, confirmation source/time/receipt, commitment check (`consistent`, `inconsistent`, `unknown`), item differences, evidence/replay bundle references, unresolved gaps/anomalies and next action/owner/deadline. Task resolution remains independent of run closure. / 输出执行结果应包含任务运行号、处置状态、分离的技术受理业务状态、确认来源时间回执、承诺检查结果、逐项差异、证据重放包、未解缺口异常及下一动作负责人期限；任务解决与运行关闭独立。

<a id="execution-steps"></a>
## Workflow and gates / 流程与闸门

| ID | Stage / 阶段 | Action and durable output / 动作及持久产物 | Gate or failure path / 闸门或失败路径 |
| --- | --- | --- | --- |
| OBE01 | Baseline / 建立任务基线（阶段 0） | Freeze objective, acceptance items, authority, deadline, risk, reversible scope and task/run IDs. / 固定目标、验收项、权威方、期限、风险、可逆范围及任务运行号。 | No verifiable expected outcome or high-risk authority → remain in intake. / 预期不可核验或高风险缺确认方则留在入口。 |
| OBE02 | Context / 固定运行上下文（阶段 1） | Snapshot input digests, models/prompts/tools, filtered tools/reasons, policy/identity and data handling. / 快照输入摘要、模型提示工具、过滤原因、规则身份与数据处理。 | Wrong artifact, unidentified actor or failed redaction → pause. / 工件错版、身份不明或脱敏失败则暂停。 |
| OBE03 | Proposal / 形成提案与执行计划（阶段 2） | Bind proposal version/digest to concrete parameters, effects, alternatives, dependencies and topology/stop conditions. / 将提案版本摘要绑定实际参数、副作用、替代项、依赖及拓扑停止条件。 | Material parameter change requires new proposal and control checks. / 参数实质变化须新提案并重检控制。 |
| OBE04 | Controls / 执行治理控制（阶段 3） | Verify approval object/scope/expiry, current identity/permissions/autonomy; atomically reserve shared budget and record decisions. / 核验批准对象范围有效期、当前身份权限自治范围，原子预留共享预算并记决定。 | Missing/invalid control, insufficient reservation or unavailable required audit → reject/defer affected action. / 控制缺失失效、预留不足或必要审计不可用则拒绝延后受影响动作。 |
| OBE05 | Preflight / 执行前校验（阶段 4） | Recheck exact request, object/environment/version, current authorization, durable idempotency, pending intent, callback/query and recorder health. / 重检精确请求、对象环境版本、实时授权、持久幂等、未决意图、回调查询及记录器健康。 | Persist intent before dispatch; unknown prior effect forbids blind retry. / 派发前持久化意图；先前效果未知时禁止盲目重试。 |
| OBE06 | Dispatch / 调用工具或服务（阶段 5） | Record start/end, actual actor, request/raw response references, raw technical/business codes, external ID, attempt and timing. / 记录起止、实际主体、请求原始响应引用、技术业务代码、外部号、尝试与时间。 | Timeout is unknown; keep reservation and reconcile. Do not collapse raw state to success=true. / 超时记未知，保留占用并对账；不得把原始状态压成布尔成功。 |
| OBE07 | Interpretation / 解释技术结果与业务状态（阶段 6） | Versioned mapping preserves technical, acceptance and business axes; record anomalies and allowed public expressions. / 版本化映射保留三层状态，记录异常及允许公开表述。 | Unknown enum quarantines parsing; a stronger claim needs stronger verified evidence. / 未知枚举隔离解析；更强结论须更强核验证据。 |
| OBE08 | Async/recovery / 等待、回调与跨运行接续（阶段 7） | Persist application/intent ID, deadline, query owner and handoff versions; authenticate/dedupe callbacks; new run links old run. / 持久化申请意图号、期限、查询负责人及交接版本，认证去重回调，新运行关联旧运行。 | Missing callback triggers bounded authority query; missing external ID uses the recorded request key or manual reconciliation. / 缺回调触发有界权威查询；缺外部号使用原请求键或人工对账。 |
| OBE09 | Confirmation / 确认最终业务结果（阶段 8） | Authority checks exact object/version and every acceptance item; record source/time/receipt and batch differences. / 权威方核验精确对象版本与每项验收条件，记录来源时间回执及批量差异。 | Unavailable/conflicting authority cannot become success; preserve unknown/partial and next obligation. / 权威不可用或冲突不得记成功，保留未知部分状态及后续责任。 |
| OBE10 | Delivery / 生成对外答复或交付物（阶段 9） | Bind reply/artifact digest and version to the evidence/status used; redact and check each material claim before publishing. / 答复工件摘要版本绑定所用证据状态，发布前脱敏并逐项校验关键承诺。 | Pending permits “submitted”, not “completed”; inconsistency blocks/revises the reply. / 待处理只允许称已提交，不称完成；不一致时拦截或改写答复。 |
| OBE11 | Closure / 关闭运行并形成证据包（阶段 10） | Seal timeline, causal links, required-control receipts, final disposition, gaps and safe replay references. / 封存时间线、因果链、必要控制回执、处置状态、缺口及安全重放引用。 | Persist unresolved reconciliation across shutdown; run closed is not task resolved. / 关机前持久化未解决对账责任；运行关闭不等于任务解决。 |
| OBE12 | Regression / 评测、修复与回归验证（阶段 11） | Diagnose tool/state/policy/business/expression failures; replay frozen responses and adjacent success/reject/pending/unknown cases under new versions. / 定位工具状态策略业务表达故障，在新版本下重放冻结响应及相邻成功拒绝等待未知样本。 | Isolate real effects; actual regression evidence and release approval precede rollout. / 隔离真实副作用，取得实际回归证据及发布批准后上线。 |
| OBE13 | Governance feedback / 反馈到治理调整（阶段 12） | Owner records incident/evaluation basis, old/new values, affected scope, effective version/time and rollback criterion. / 负责人记录事故评测依据、新旧值、范围、生效版本时间及回滚条件。 | Metrics advise; only authorized governance changes future controls. Preserve historical interpretation. / 指标只提供建议，授权治理方改变未来控制，保留历史解释。 |

## State transitions and example / 状态迁移与示例

`created → context_frozen → proposed → controls_checked → reserved → preflight → executing → technical_ended → waiting/unknown/result_verification → confirmed_success/confirmed_failure/partial`. Rejection, pre-effect cancellation and confirmed compensation have separate evidence paths. Every transition appends an event; unknown returns through reconciliation, never directly to a new write. / 从创建经上下文、提案、控制、预留和预检进入执行；技术结束后可能等待、未知或核验结果。拒绝、效果前取消及已确认补偿有各自证据路径；状态迁移追加事件，未知经对账处理，不能直接触发新写操作。

Coupon example / 发券示例: `HTTP 200 + pending_review` means technical success and accepted/pending, with business outcome still waiting. Reply: “申请已提交，等待审核 / Submitted; awaiting review.” A later authenticated coupon-instance receipt for the same user/application permits “已发放 / Issued.” A timeout followed by an issued instance is a reconciled success, not a second issuance. / 后续只有同一用户申请的可信券实例回执才允许宣称发放；超时后查得券实例属于对账成功，不触发第二次发券。

## Independent and interactive operation / 独立与交互运行

Independent mode persists ten minimum event types: run start, context frozen, proposal, controls checked, tool start, tool end, status interpreted, result confirmed/unknown, reply generated, run closed. Record conditional steps explicitly as not-applicable with profile reasons. Approval/control/receipt events are never replaced by debug sampling. / 独立模式持久化十类最小事件：运行开始、上下文固定、提案、控制检查、工具开始结束、状态解释、结果确认或未知、答复生成及运行关闭；条件步骤不适用须明确场景理由；控制回执不能被调试采样替代。

Interactive mode emits stage, wait, callback and rule-change events as applicable. It receives record acknowledgments, gaps, conflicts, redaction alerts, confirmation requests, pause/degrade advice and bundle-ready notices. Apply the [completion protocol](observability-contract.md#completion-protocol) to every response. Neither probe acknowledgment nor bundle-ready means the task succeeded. / 交互模式按需追加阶段、等待、回调及规则变更事件，接收记录确认、缺口冲突、隐私告警、结果查询、暂停降级建议及证据包通知；响应均遵循补全协议。探针收件确认或证据包就绪均不证明任务成功。

<a id="topology"></a>
## Topology mounts / 拓扑挂载

| Shape / 拓扑 | Required evidence / 必要证据 |
| --- | --- |
| Chain / 链式 | Exact predecessor output version, stage continuity and state preservation. / 精确前序输出版本、阶段连续性和状态保真。 |
| Routing / 路由 | Candidate/chosen/filtered paths, reasons and rule version; distinguish routing from execution failure. / 候选选中及过滤路径、理由规则版本，区分路由与执行故障。 |
| Parallel / 并行 | Predeclared branch inventory, independent spans, timeout/cancel dispositions, adopted/omitted outputs and partial failures. / 事先登记分支、独立操作号、超时取消状态、采用舍弃输出与部分失败。 |
| Orchestration / 编排 | Planned/actual dependency graphs, scheduling, skipped/reordered nodes and gate evidence. / 计划实际依赖图、调度、跳过重排节点及闸门证据。 |
| Loop / 循环 | Iteration/input-difference records, time/cost bounds, no-progress detection and explicit stop reason. / 迭代输入差异、时间成本上限、无进展检测及明确停止原因。 |
| Hierarchy / 层级 | Parent/child boundaries and acceptance, exact handoff artifact/receipt and unresolved responsibility; child success does not prove parent success. / 父子边界验收、精确交接工件回执及未解责任；子成功不证明父成功。 |

## Scenario configuration / 场景配置

Freeze `profile_id/version`, risk, expected-result schema, authoritative source, max-wait/query limits, reversibility, required controls/events/probes, affected-action blocking policy, retention/access and sampling. Profile changes are revisions, not a way to delete failed obligations. / 固定场景标识版本、风险、预期结构、权威源、等待查询上限、可逆性、必需控制事件探针、受影响动作阻断策略、留存访问及采样；配置变更应生成修订，不能借此删除失败责任。

| Scenario / 场景 | Confirmation and critical bindings / 确认与关键绑定 |
| --- | --- |
| Coupon / 补偿券 | User/application/approval/coupon instance; pending-review differs from issued. / 用户申请批准券实例，待审不同于发放。 |
| Payment / 付款 | Payee, amount/currency, approved list version, budget, bank receipt and internal ledger; reconcile before retry. / 收款人金额币种、批准清单版本、预算、银行回执及内部账；重试前对账。 |
| Release / 软件发布 | Commit/build/environment/approval/batch plus deployed instance and required health checks; job creation is insufficient. / 代码构建环境批准批次、部署实例及必要健康检查；创建任务不足以确认成功。 |
| Report / 分析报告 | Data snapshot, source lineage, artifact version and agreed review acceptance; track adoption separately from correctness. / 数据快照、来源血缘、工件版本及约定评审验收；采用与正确性分别记录。 |

## Constraints and verification / 约束与验证

Progress tracking answers where to resume; handoff chains answer what was accepted and who owns it; this harness answers what happened, why and whether outcomes were confirmed. Share stable IDs without treating these records as interchangeable. / 进度追踪回答从哪里续跑，交接链回答验收了什么及谁负责，可观测性回答发生了什么、为何发生及结果是否确认；可共享标识，记录不能互相替代。

Use [the acceptance matrix](observability-probes.md#acceptance) to verify normal and failure paths. Until adapters and recorded scenario runs exist, all behavior above is an engineering specification. / 用验收矩阵检验正常及失败路径；在适配器及有证据的场景运行形成前，上述行为均为工程规格。
