# Pattern Composition and Selection / 组合设计与模式选型执行流程

Name / 名称: Evidence-Based Pattern Composition / 基于证据的模式组合。Version / 版本: `0.1.0`. Status / 状态: `draft`, `specification_only`.

Description / 描述: Select the smallest sufficient program, model boundary and topology from observed task difficulties, then validate the composition against a frozen baseline. / 从已观察的任务困难出发，选择最小充分程序、模型边界及拓扑，再对冻结基线验证组合。

## Quick Navigation / 快速导航

- [Workflow / 流程](#workflow)
- [Difficulty diagnosis / 困难诊断](#difficulties)
- [Composition / 组合规则](#composition)
- [Artifacts and validation / 工件与验证](#artifacts)
- [Acceptance cases / 验收用例](#cases)
- [Selection card / 选型卡](pattern-selection-card.md), [Independent probes / 独立探针](pattern-selection-observability-probes.md), [Shared contract / 共享契约](pattern-selection-contract.md), [Source map / 来源映射](pattern-selection-source-map.json)

## Usage and Boundaries / 适用场景与边界

Use for new workflows, existing engineering-node diagnosis, decisions about additional model calls or roles, and composition across matrix cells. Ordinary deterministic solutions may be the final answer. Data defects first require data repair; absent business authority cannot be repaired by adding a model. / 用于新流程、现有工程节点诊断、是否增加模型调用或角色的决策，以及跨矩阵单元组合。普通确定性方案可以就是最终答案；数据缺陷应先修数据，业务权限缺失不能靠增加模型解决。

This extends the existing Trace Insert → ASSESS → ROUTE → SELECT → Plan entrypoint. Source IDs `PATTERN_SELECTION_0001` and `SKILL_SELECTION_0001` are provenance aliases for this cross-cutting procedure, not newly promoted matrix patterns or installed Skills. All new business acceptance cases remain `not_executed`. / 本流程扩展现有 Trace 插入、评估、判拓扑、查矩阵与规划入口。来源 ID 仅是本跨单元规程的出处别名，不代表新增矩阵模式或已安装技能；新增业务验收用例均为未执行。

Run independently with manual evidence records or with optional probes. The workflow owns business decisions; the probe owns observation and append-only enrichment. Missing optional telemetry does not invalidate independent business evidence; missing mandatory business checks still blocks the dependent action. / 可以手工记录证据独立运行，也可接可选探针。流程承担业务决定，探针负责观察及追加补全。可选遥测缺失不否定独立业务证据；必要业务检查缺失仍阻断依赖动作。

<a id="workflow"></a>
## Workflow / 执行流程

Freeze task version, rule version, evaluation set and acceptance thresholds before comparison. Each stage records owner, evidence, result and transition reason. Evidence-poor inputs can produce a preliminary design with verification tasks; they cannot produce an approved selection. / 比较前冻结任务版本、规则版本、评估集和验收阈值。每阶段记录责任人、证据、结果与迁移原因。证据不足可以形成带验证任务的初步设计，不能形成已批准选型。

| Stage / 阶段 | Work and completion condition / 工作及完成条件 |
| --- | --- |
| S0 | Initialize / 初始化运行: assign `selection_run_id`, input/rule versions, object, owner, risk and probe mode; retain initial inputs. / 分配运行标识、输入及规则版本、对象、责任人、风险与探针模式，保留初始输入。 |
| S1 | Contract / 定义正确性、禁止动作和安全出口: define deliverable, authoritative verification, prohibited effects and correct execution, acceptance, refusal, waiting and degradation. `SEL-G1` requires all applicable fields. / 定义交付物、权威验证、禁止效果及正确执行、受理、拒绝、等待、降级；任务契约门要求适用字段齐全。 |
| S2 | Baseline / 运行现有办法或最小方案: actually exercise representative normal and boundary cases; record per-case outcomes, failures, latency, cost and manual load. `SEL-G2`: sufficient baseline → S8, without adding models or patterns. / 实跑正常与边界案例，记录逐例结果、失败、时延、成本及人工负担；基线足够则直达 S8，不增加模型或模式。 |
| S3 | Diagnose / 定位具体困难: attach evidence and affected steps to D1–D12; distinguish missing data, stale data, conflicts, reasoning, rules, execution and misreporting. / 困难须绑定证据与受影响步骤，区分缺失、过期、冲突、推理、规则、执行及误报。 |
| S4 | Assign responsibility / 划定模型、程序与人工的边界: each fact has a source, each decision an owner, each action an authority; document why each model call is needed. / 每个事实有来源、决定有责任人、动作有授权主体；逐次说明模型调用必要性。 |
| S5 | Choose topology / 选择最小拓扑结构: choose one primary topology and scoped auxiliaries only for evidenced needs; record dependencies and prohibited combinations. / 选一个主拓扑，仅按已证实需要添加有范围的辅助拓扑，记录依赖及禁止组合。 |
| S6 | Choose controls / 选择工程模式与治理控制: select existing stable pattern IDs, record rejected candidates and required authority, prechecks, idempotency, limits, postchecks and recovery. / 选择现有稳定模式 ID，记录未选候选及权限、前检、幂等、限额、后检和恢复要求。 |
| S7 | Specify workflow / 形成可执行工作流: bind every step to inputs, executor, decision owner, versions, dependencies, outputs, failure exits and observation points. / 每步绑定输入、执行者、决定责任人、版本、依赖、输出、失败出口和观察点。 |
| S8 | Validate / 用同一任务集比较验证: compare baseline and candidate on the same frozen cases and conditions; `SEL-G3` requires correctness, safety, cost, latency and traceability. / 在相同冻结案例与条件上比较基线和候选，验证门同时要求正确性、安全性、成本、时延与可追溯性。 |
| S9 | Publish / 发布选型卡与运行约束: version the card, decision, effective configuration, accepted evidence and unverified items; activation follows the applicable authority process. / 版本化选型卡、决定、实际配置、采纳证据及未验证项，启用遵循适用授权流程。 |
| S10 | Re-select / 运行变化与重新选型: mark affected conclusions stale on material change, retain valid portions and return affected scope to S1. / 实质变化后标记受影响结论过期，保留仍有效部分并让受影响范围回 S1。 |

State progression / 状态推进: `initialized → contracting → baseline_testing → diagnosing → selecting → designing → validating → completed`. A sufficient baseline skips diagnosis/design and goes directly to validation. `review_required`, `suspended`, `rejected`, `reselect_required` and `archived` retain explicit reasons. `active` describes approved use of a configuration, not business completion; finishing a selection run never grants tool authority. / 基线足够可跳过诊断设计直达验证。待评审、暂停、拒绝、待重选与归档保留原因；启用仅描述配置获准使用，不代表业务完成，选型结束不授予工具权限。

<a id="difficulties"></a>
## Difficulty Diagnosis / 困难诊断

| ID | Difficulty / 困难 | First remedy / 首选补救 |
| --- | --- | --- |
| D1 | Ambiguous input / 输入表达模糊 | Model extracts intent and candidate objects; program verifies ownership. / 模型提取意图与候选对象，程序核验归属。 |
| D2 | Missing facts / 关键事实缺失 | Query authority, detect, request evidence or hand off; never infer absence from missing records. / 查询权威源、检测、补证或交接，不从未查到推断不存在。 |
| D3 | Conflicting facts / 事实相互冲突 | Preserve both sources, arbitrate versions, suspend dependent risky action. / 保留双方来源、仲裁版本、暂停依赖的风险动作。 |
| D4 | Complex rule applicability / 规则适用复杂 | Decision table or rules first; model interpretation is a candidate. / 先用决策表或规则，模型解释仅为候选。 |
| D5 | Multi-fact explanation / 回复需要结合多处事实 | Supply verified material to a justified explanation call; template remains an option. / 把已核验材料交给有必要的解释调用，模板仍是选项。 |
| D6 | Variable task steps / 每项任务步骤不同 | Candidate plan plus durable dependency and progress control. / 候选计划加持久依赖和进度控制。 |
| D7 | Feedback determines next step / 下一步依赖新结果 | Bounded investigation or tool-choice loop. / 有界调查或工具选择循环。 |
| D8 | Independent work / 多项工作互不依赖 | Program parallelism or fan-out/gather with explicit merge rules. / 程序并行或带明确汇合规则的扇出聚合。 |
| D9 | Independent responsibilities / 不同角色需独立负责 | Delegation or handoff only with owned artifacts and acceptance. / 仅在工件及验收责任清楚时委派或交接。 |
| D10 | Risky action / 高风险动作需要责任判断 | Authority, approval if required, limits and verified outcome. / 权限、适用审批、限额及结果核验。 |
| D11 | Missing traceability / 输出正确但不可追溯 | Decision and evidence ledger, optional observation probes. / 决策及证据账本、可选观察探针。 |
| D12 | Excess cost or latency / 成本或时延不可接受 | Route, cache with freshness, degrade or remove unnecessary calls. / 路由、保鲜缓存、降级或去除无用调用。 |

Repeated assessment of unchanged material does not create new facts. An independent critique can still have justified value; record its purpose and measured benefit instead of declaring all repeated calls redundant. / 对相同材料反复评估不能产生新事实；独立批评仍可能有价值，应记录目的和已测收益，不能把所有重复调用一律判为冗余。

<a id="composition"></a>
## Composition Rules / 组合规则

When the validated selection requires multiple patterns, pass the versioned S7 specification and S9 card to [Pattern Combination Execution / 模式组合执行](pattern-combination-execution-flow.md), `PATTERN_0053`. Selection determines what is justified; that execution contract governs connection semantics, scheduling, local retry/replanning, shared budgets and end-to-end acceptance. A draft or selected plan is never action authority. / 已验证选型确需多个模式时，将版本化 S7 说明及 S9 卡片交给模式组合执行。选型回答哪些结构有依据，组合执行契约管理连接语义、调度、局部重试重规划、共享预算与端到端验收；草稿或所选计划均不是行动权限。

| Topology / 拓扑 | Use and required control / 适用与必要控制 |
| --- | --- |
| `TOP_CHAIN` / 链式 | Fixed order; versioned step contracts and failure exits. / 固定先后，步骤契约、版本传递与失败出口。 |
| `TOP_ROUTING` / 路由 | Fact/rule-dependent exits; explicit unknown and safe default routes. / 事实规则分支，显式未知与安全默认出口。 |
| `TOP_PARALLEL` / 并行 | Independent branches; shared resource inventory, required branch manifest, timeout, conflict and join rules. / 独立分支，列明共享资源、必选分支、超时、冲突和汇合规则。 |
| `TOP_ORCHESTRATION` / 编排 | Variable plans or controller-managed dependencies; versioned plan, mandatory checks and recovery. / 可变计划或控制器管理依赖，计划版本、强制检查与恢复。 |
| `TOP_LOOP` / 循环 | New results change next steps; stop condition, iteration/time/cost budgets and progress evidence. / 新结果改变下一步，停止条件、次数时间成本预算及进展证据。 |
| `TOP_HIERARCHY` / 层级 | Separate responsibility and layered acceptance; delegation boundaries and parent composition gate. / 独立责任与分层验收，委派边界与父级组合门。 |

Every auxiliary records its `scope`, `reason`, inputs/outputs, entry/exit conditions, owner, dependencies and failure route. A dependent step waits for all required branches; partial aggregation may proceed only under a predeclared safe policy. Local approval or local correctness never implies parent approval or end-to-end correctness. / 每个辅助拓扑记录范围、理由、输入输出、进出条件、负责人、依赖及失败出口。依赖步骤等待全部必选分支；部分汇合仅可遵循预先声明的安全策略。局部批准或正确不代表父级批准或端到端正确。

Reuse stable identities from [registry](registry.json): `PATTERN_0035` prompt chaining, `PATTERN_0037` plan-and-execute with `PATTERN_0029` progress tracking, `PATTERN_0038` guardrail sandwich, `PATTERN_0034` hypothesis testing, `PATTERN_0043` handoff, `PATTERN_0044` gather, `PATTERN_0045` review, `PATTERN_0046` delegation, `PATTERN_0047` approval, `PATTERN_0048` progressive commitment, `PATTERN_0050` blast radius and `PATTERN_0052` probes. / 复用注册表中提示链、计划并执行及进度追踪、护栏夹层、假设测试、交接、汇聚、评审、委派、审批、渐进承诺、爆炸半径与探针的稳定身份。

Multiple APIs alone do not justify multiple Agents. High risk adds governance obligations, not an automatic topology change. A plan proposes work; the execution host still checks current object, fact freshness, scope, authority, applicable approval and limits before each effect. Durable idempotency and post-action verification are required for retryable effects; unknown effects require reconciliation before retry. / 多接口本身不构成多 Agent 的理由。高风险增加治理义务，不自动改变拓扑。计划只提出工作；每次效果前仍由执行宿主核验当前对象、事实新鲜度、范围、权限、适用审批与限额。可重试效果需持久幂等和执行后验证；未知效果须先核对再重试。

<a id="artifacts"></a>
## Artifacts and Validation / 工件与验证

Produce five linked artifacts: selection card, workflow specification, control checklist, comparison report and observation manifest. Use project-local `.harness-analysis/<analysis_id>/` for actual run evidence, not bundled historical Trace files. / 形成五类关联工件：选型卡、工作流说明、控制清单、比较报告和观测清单。实际运行证据保存在项目本地分析目录，不写入内置历史 Trace。

```yaml
# Selection card shape / 选型卡结构（示意，非已执行证据）
selection_run_id: SEL-example
task_id: refund-example
task_version: "1"
rule_version: "1"
status: draft
evidence_status: preliminary
task_contract:
  goal: "Create an eligible refund instruction / 为符合条件的退款创建指令"
  accepted_outcomes: [executed, accepted, refused, waiting, degraded]
  prohibited_effects: [pay_with_unknown_invoice]
  verification_source: "Authoritative business record / 权威业务记录"
baseline: {id: BASE-example, evaluation_set_version: "1", evidence_refs: []}
difficulties: [] # D1–D12 plus evidence / 困难及证据
responsibilities: [] # executor, authority, verifier / 执行者、权限、核验者
primary_topology: TOP_CHAIN
secondary_topologies: [] # topology, scope, reason, controls / 拓扑、范围、理由、控制
selected_patterns: [] # Empty is valid when baseline suffices / 基线足够可为空
rejected_patterns: [] # candidate and evidence-based reason / 候选及有据理由
steps: [] # See step contract below / 见下方步骤契约
controls: []
validation: {status: not_executed, decision: pending_evidence, evidence_refs: []}
unverified_items: [baseline_and_candidate_comparison]
observability: {mode: manual, required_events: [], retention_policy_ref: null}
```

Each step requires `step_id`, purpose, cognition/topology/pattern refs, executor, decision owner, dependency IDs, required inputs and accepted evidence states, preconditions, operation/tool/effect type, output types, postconditions, failure routes, events and recovery point. Plans also require `plan_id`, version, previous version, completed/pending/blocked steps and change reason. Replanning preserves completed facts and effects; omitted mandatory checks remain mandatory. / 每步包含标识、目的、认知拓扑模式引用、执行者、决定责任人、依赖、必要输入及可接受事实状态、前置条件、操作工具效果类型、输出类型、后置条件、失败出口、事件及恢复点。计划额外记录身份、当前及前版、完成待办阻塞步骤和变更原因；重规划保留已完成事实与效果，遗漏的强制检查仍必须执行。

Compare per-case expected and actual results, prohibited effects, routing, new error types, model necessity, pre/postcheck coverage, mean/tail latency, cost, manual load and recovery. Use the same task/input/rule versions and controlled tool fixtures for baseline/candidate comparison; do not repeat live risky effects merely to compare alternatives. A sufficient baseline may be reaffirmed without inventing a candidate. / 逐例比较预期和实际结果、禁止效果、路由、新增错误、模型必要性、前后检查覆盖、平均及尾部时延、成本、人工负担和恢复。基线候选使用相同任务输入规则版本及受控工具数据，不为对比而重复真实风险效果；基线足够时可直接确认，不虚构候选。

Source S8 allows an explicitly set high-risk error threshold; the maintained interpretation keeps contractual prohibited effects at zero and requires risk-owner thresholds for other admissible risks, set before testing. No post-hoc threshold relaxation. Missing truth or audit labels remains an unverified item, never a passing score. / 原文 S8 允许明确的高风险误执行阈值；维护口径要求契约禁止效果为零，其他可接受风险由责任人在测试前设阈值，不得事后放宽。缺真值或审计标注保留为未验证项，不得填通过分数。

S10 watches input form, read-to-write authority, risk, roles/systems, sources/rules/tools, call count, plan mutability, error distribution and budget changes. Record affected claims, configuration version and revalidation scope; do not reuse stale approval for changed objects or actions. / S10 关注输入形式、读变写权限、风险、角色系统、来源规则工具、调用次数、计划可变性、错误分布及预算变化。记录受影响主张、配置版本和复验范围，不把旧批准用于新对象或动作。

## Worked Composition / 组合示例

A 347-unit refund uses a primary chain and local routing. A vague order request may need D1 extraction followed by ownership verification; an unknown invoice is D2 and routes to a named human verification task, with no payment instruction. Verify that the human ticket exists before saying it was accepted. Once an authoritative invoice fact arrives, recheck permission and any applicable approval, create and independently verify the instruction; report its actual state without claiming receipt of funds. / 347 元退款采用主链式加局部路由。模糊订单请求可用 D1 提取后核验归属；发票未知属于 D2，转明确责任人的人工核实单，不创建付款指令。核验人工单存在后才能说已受理。权威发票事实到达后重查权限及适用审批，创建并独立核验付款指令，只报告实际状态，不声称到账。

Readonly policy Q&A needs sources, freshness and grounded claims, while investigation may need bounded loops, and cross-department work may need explicit responsibility handoffs. Apply only the controls relevant to each scope. / 只读制度问答需要来源、新鲜度和有据主张；调查可能需要有界循环；跨部门工作可能需要明确责任交接。按各范围启用适用控制。

<a id="cases"></a>
## Acceptance Cases / 验收用例

The following source cases are requirements, all `not_executed`; passing documentation validation does not execute them. / 以下来源用例均为待执行要求；文档校验通过不代表用例已运行。

| ID | Source case / 来源用例 | Expected behavior / 预期行为 | Status / 状态 |
| --- | --- | --- | --- |
| SEL-CASE-01 | 规范输入且条件满足，程序直接完成。 | Structured eligible input completes through the program. | not_executed / 未执行 |
| SEL-CASE-02 | 模糊输入，模型提出候选对象，程序核对后继续。 | Ambiguous input produces a candidate, then program verification. | not_executed / 未执行 |
| SEL-CASE-03 | 关键事实未知，系统转人工且不产生风险副作用。 | Critical unknown routes to a human with no risky effect. | not_executed / 未执行 |
| SEL-CASE-04 | 关键事实冲突，系统暂停并暴露冲突。 | Conflicting facts suspend the dependent action and expose the conflict. | not_executed / 未执行 |
| SEL-CASE-05 | 权限不足，系统拒绝。 | Insufficient permission is refused. | not_executed / 未执行 |
| SEL-CASE-06 | 工具调用超时，重试不产生重复副作用。 | Timeout retries create no duplicate effects. | not_executed / 未执行 |
| SEL-CASE-07 | 工具返回成功但业务状态未变化，后置验证发现异常。 | Technical success with unchanged business state is detected by postchecks. | not_executed / 未执行 |
| SEL-CASE-08 | 模型生成了材料外事实，输出校验将其拦截。 | Unsupported model facts are rejected before use. | not_executed / 未执行 |
| SEL-CASE-09 | 计划遗漏强制步骤，程序仍阻止后续动作。 | Missing mandatory plan steps do not bypass program guards. | not_executed / 未执行 |
| SEL-CASE-10 | 模板足够的简单问题，不发生不必要的模型调用。 | A sufficient template avoids unnecessary model calls. | not_executed / 未执行 |
