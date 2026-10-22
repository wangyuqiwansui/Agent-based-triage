# Workflow Audit and Remediation / 工作流审计与弥补闭环

Use for an entire project's workflows, a bounded process or one engineering node. Deliver an evidence-backed account of what works, what fails, what is unknown and how to close each meaningful gap. / 用于整个项目的工作流、限定流程或单个工程节点，给出有证据的有效机制、失败之处、未知项及实质缺口的闭合方式。

## Quick Navigation / 快速导航

- Scope and source inventory / 范围与来源：sections 1–2 / 第 1–2 节。
- Node and transition review / 节点与转移审查：sections 3–4 and [checklist](node-gap-checklist.md) / 第 3–4 节及检查表。
- Remedies, priorities and acceptance / 弥补、排序与验收：sections 5–7 / 第 5–7 节。
- Delivery / 交付：section 8 and [report template](../assets/workflow-audit-report-template.md) / 第 8 节及报告模板。

## 1. Bound the Question / 界定问题

Capture project/root or supplied material, workflow objective, trigger, intended terminal outcome, actors, environment, constraints, requested depth and source revision. If Git is available, record HEAD and relevant dirty files; a commit alone does not describe an edited working tree. For supplied documents, record title/version/sections. / 记录项目或材料、流程目标、触发、预期终态、参与者、环境、约束、请求深度及来源版本。有 Git 时记录 HEAD 和相关未提交文件；单个提交号不能描述已编辑的工作区。文档记录标题、版本和章节。

Infer scope from the request and repository before asking questions. Ask only when a missing objective, boundary or success criterion would materially change the conclusion; continue independent inspection and label assumptions. Default to analysis and recommendations unless implementation is also requested or already authorized. / 先从请求和仓库推断范围；仅当目标、边界或成功标准缺失会实质影响结论时询问，同时继续独立检查并标注假设。除非请求包含实施或已获实施授权，否则默认输出分析与建议。

“Every node” means all discovered in-scope responsibilities and transitions, not all files. Multiple independent workflows need distinct inventories and explicit shared nodes. If coverage is too broad for the available context, maintain the full inventory, review by batches and disclose remaining work; do not silently sample. / “每个节点”指已发现且在范围内的全部职责和转移，不指每个文件。多个独立工作流分别建清单，共享节点显式关联。上下文不足时保留完整清单、分批审查并披露剩余工作，不暗中抽样。

## 2. Build an Evidence Ledger / 建立证据台账

Inspect entrypoints, orchestration, configuration, schemas, tests and available run evidence. Use documentation to locate behavior; inspect the actual implementation or authoritative workflow record before claiming behavior is enforced. Read only the relevant module references. / 查看入口、编排、配置、Schema、测试及可用运行证据。用文档定位行为；声称行为已强制执行之前，核对实际实现或权威流程记录。按需读取模块参考。

Record each evidence item as `EVIDENCE_*` with source path and line/section/event, revision, kind, time/environment where relevant, what it supports and its limitations. Reconcile contradictory evidence; report the conflict until the authoritative source is established. / 每项证据使用 `EVIDENCE_*` 编号，记录路径及行号、章节或事件，版本、类型、相关时间环境、支持内容与局限。核对冲突证据；确定权威来源前保留冲突。

| Evidence kind / 证据类型 | Supports / 能支持 | Does not alone establish / 单独不能证明 |
| --- | --- | --- |
| Requirement or design / 需求或设计 | Intended responsibilities and acceptance / 预期职责和验收 | Implementation or actual enforcement / 已实现或实际强制执行 |
| Code, schema or config / 代码、Schema 或配置 | Static behavior and configured boundary / 静态行为及配置边界 | Deployment, live usage or business outcome / 已部署、实际使用或业务结果 |
| Test source / 测试源码 | A described case and asserted expectation / 已描述的场景及断言 | A passing run / 已执行通过 |
| Executed test / 已执行测试 | Outcome for the recorded version and environment / 对应版本环境下的结果 | Uncovered paths or production reliability / 未覆盖路径或生产可靠性 |
| Trace or operation record / Trace 或操作记录 | Observed behavior within its scope / 范围内的已观察行为 | Unobserved populations or lasting improvement / 未观察群体或持续改进 |

An absent search result means “not found in the inspected paths”, not “does not exist”. To confirm a missing responsibility, cite both why it is required and the inspected control path showing its omission. Missing runtime access becomes a verification task; do not manufacture logs or execute a side-effecting workflow just to fill evidence. / 搜索无结果只能说明“所查路径未发现”，不能说明“不存在”。确认职责缺失须同时引用必要性依据及展示遗漏的控制路径。缺少运行访问时生成验证任务，不虚构日志，也不为补证擅自执行有副作用的流程。

Judge maturity against the requested deliverable. A specification can satisfy a design task while leaving implementation pending; a reference runtime or validated static visualization does not prove a deployed workflow. For this Skill's own repository, inspect the registry, module contracts, runtime and executed tests separately rather than treating the entire pattern library as an installed application. / 按所需交付物判断成熟度：规格可满足设计任务，同时保留实现待完成；参考运行时或校验通过的静态可视化不证明流程已部署。分析本 Skill 自身仓库时分别核对注册表、模块契约、运行时及已执行测试，不把整个模式库当作已安装应用。

## 3. Reconstruct Nodes and Edges / 重建节点与连线

Use [workflow-nodes.md](workflow-nodes.md) as discovery prompts. Assign stable analysis-local `NODE_*` IDs by responsibility; use `EDGE_*` for transitions. Preserve project-specific stages and names. Draw a small flow diagram when it clarifies branches; a diagram is optional, the inventory is not. / 以节点指南辅助发现，按职责分配分析内稳定的节点及连线编号，保留项目特有阶段和名称。分支较复杂时可画简图；图可选，清单不可省略。

For every node record: responsibility and owner role, trigger/preconditions, inputs and their source/version, decision/control, outputs and consumer, success/failure exit, relevant state and side effects, linked evidence. Owner unknown is explicit, not an invented person. / 每个节点记录职责及责任角色、触发与前置条件、输入及来源版本、决策与控制、输出及接收者、成功失败出口、相关状态及副作用和证据。负责人未知时明确标注，不编造姓名。

For every edge record: source/target, activation condition, artifact and version, producer/consumer responsibility, acceptance acknowledgement, failure/timeout route and evidence. Check branches, joins, retries, cancellation, manual handoffs and orphan outputs when applicable. / 每条连线记录来源目标、触发条件、制品及版本、交出接收责任、验收确认、失败超时去向和证据；按需核查分支、汇合、重试、取消、人工交接和无人接收的输出。

Track review state separately from findings: `reviewed`, `partial`, `unreviewed`, `out_of_scope`. A fully investigated evidence absence can be reviewed and still have an `unknown` disposition. A partially inspected node cannot be called adequate. / 审查状态与问题结论分开，使用已审、部分、未审、范围外。已充分调查但证据仍缺失可为已审且未知；部分检查的节点不能判为已足够。

Report node coverage and edge coverage separately with actual denominators. Exclude justified out-of-scope entries, keep unknowns visible and count only completed reviews in the numerator. Never describe complete inventory coverage as verified business success. / 节点及连线覆盖分别给出真实分母；排除有理由的范围外项，保留未知项，只将已完成审查纳入分子。清单审查覆盖完整不代表业务成功已验证。

State the inventory's source and discovery limit. If inaccessible entrypoints or unknown routing prevent establishing the in-scope inventory, report discovery as incomplete even if every currently known node was reviewed; do not infer a complete project audit from that fraction. For an empty applicable population use not applicable, not 100%. / 说明清单来源及发现边界。入口不可访问或路由未知导致无法确定范围内清单时，即使已知节点全部审过也应报告发现尚不完整，不从该比例推导项目全审。适用总体为空时标不适用，不写 100%。

## 4. Diagnose Nodes and Seams / 诊断节点与交接

Apply [node-gap-checklist.md](node-gap-checklist.md) to applicable responsibilities. Inspect contracts, data/context, decision quality, ownership, authorization, failure recovery, state consistency, observability, capacity and acceptance only where relevant. For a single-node review, include its immediate upstream/downstream seam without expanding to unrelated workflows. / 按适用职责使用节点不足检查表，检查契约、数据上下文、决策、责任、权限、失败恢复、状态一致性、可观测性、容量及验收；单节点审查包含紧邻上下游交接，不扩大到无关流程。

Use these dispositions for individual checks/findings; a node may contain multiple checks with different dispositions. / 对具体检查或发现使用下列结论；一个节点的不同检查可以有不同结论。

| Disposition / 结论 | Required basis / 所需依据 | Next action / 下一步 |
| --- | --- | --- |
| `confirmed_gap` / 已确认不足 | Requirement plus demonstrated mismatch from code, records or a reproducible case / 要求与由代码、记录或可复现场景展示的偏差 | Remedy and verify / 弥补并复验 |
| `suspected_gap` / 疑似不足 | Plausible mechanism with partial evidence; identify the uncertainty / 部分证据支持可能机制，明确不确定性 | Discriminating check before adoption / 先作能区分假设的核验 |
| `adequate` / 已足够 | Applicable requirement is met in the inspected scope, with evidence and limits / 有证据显示在所查范围满足要求，并说明边界 | Retain; monitor only if justified / 保留，按需观察 |
| `unknown` / 未知 | Missing, inaccessible, stale or conflicting evidence prevents judgment / 缺失、不可访问、过期或冲突证据妨碍判断 | Name source, collector role and completion criterion / 明确来源、采集角色及完成标准 |
| `not_applicable` / 不适用 | Responsibility/control is unnecessary in this scoped workflow, with a reason / 有理由说明范围内无需该职责或控制 | Exclude this check, not the whole node / 排除此检查，不排除整个节点 |

Explain the causal chain: triggering condition → observed deviation → failed obligation → downstream effect. Distinguish symptom from root-cause hypothesis and list contrary evidence. Link shared causes to all affected nodes/edges and one remediation item; keep independent causes separate. / 说明因果链：触发条件 → 已观察偏差 → 未履行义务 → 下游影响。区分症状与根因假设，列出反证。共享根因关联多个节点或连线和同一整改项，独立根因分开。

For proven local logic errors, runtime observations are not mandatory if the static control path is conclusive; state that the proof is static. For operational frequency, latency or reliability claims, require measured observations. / 对局部逻辑错误，静态控制路径已充分证明时无需强求运行日志，但须标为静态证明；发生频率、延迟及可靠性结论须有实测依据。

## 5. Select the Smallest Effective Remedy / 选择最小有效弥补

Use [diagnosis-method.md](diagnosis-method.md) and the [selection card](pattern-selection-card.md) after evidence capture. Compare retaining the baseline, clarifying a contract/owner, adding a deterministic check, and adding a pattern only when it addresses the established failure mechanism. A sufficient baseline legitimately has `selected_patterns: []`. / 采证后使用诊断方法及选型卡；比较保留基线、澄清契约责任、增加确定性检查以及确能处理失败机制时才增加模式。充分基线可以不新增模式。

For each actionable finding, specify: / 每个可行动发现说明：

- Immediate containment if needed, durable correction and any evidence collection still required; these are distinct tasks. / 必要的临时止损、长期修复以及仍需补充的证据，三者分别说明。
- The exact responsibility or interface to change and the intended before/after behavior; cite files/symbols if known, otherwise name the process artifact. / 具体修改的职责或接口及前后行为；位置已知时引用文件符号，否则指明流程制品。
- Retained controls, dependencies, owner role, effort estimate with assumptions, tradeoffs and affected consumers. / 保留控制、依赖、责任角色、带假设的工作量估计、取舍及受影响接收者。
- Verification case and expected observable result; include a relevant negative/failure case when it protects the reported gap. / 验证场景及可观察预期结果；能保护该缺口时包含相关负向或失败场景。
- Rollout/recovery for stateful or externally visible changes; for a document correction, state that reverting the edit is sufficient if true. / 涉及状态或外部可见行为时说明实施与恢复；纯文档更正可如实注明回退编辑即可。

Map capabilities/topologies only when they help explain the remedy; mark uncertain mappings preliminary. Read the selected pattern's design and observability pair before recommending it. Do not change registry identities or install a runtime just to complete an audit. / 仅在有助于解释弥补方式时映射能力拓扑，不确定映射标为初步。建议模式前读取其设计与观测配对文档，不为完成审计改注册表身份或安装运行时。

## 6. Prioritize Without Invented Precision / 有依据地排优先级

Use project severity definitions when available. Otherwise use this explicitly declared review convention; priority is not a measured score. / 优先使用项目严重性定义；没有时使用并声明以下审查约定，优先级不是实测分数。

| Priority / 优先级 | Basis / 依据 |
| --- | --- |
| P0 | Active or imminently triggered severe harm, unauthorized irreversible effects or data loss requiring containment / 正在发生或即将触发的严重损害、未授权不可逆效果或数据丢失，需先止损 |
| P1 | Blocks the core outcome or a required control/recovery path; material exposure is evidenced / 阻断核心目标或必需控制恢复路径，且重大暴露有依据 |
| P2 | Confirmed local reliability, handoff or efficiency gap with a usable workaround / 已确认的局部可靠性、交接或效率不足，有可行绕行 |
| P3 | Optional improvement with limited present impact / 当前影响有限的可选优化 |

For every assignment explain affected scope, impact, exposure/frequency if known, reversibility and dependency. Do not turn a severe hypothetical into a confirmed P0. Unknowns and suspected gaps may receive an investigation priority with rationale, but remain unconfirmed. / 每项排序说明影响范围、影响、已知暴露频率、可逆性和依赖，不把严重假设写成已确认 P0。未知和疑似项可设置有理由的调查优先级，但仍未确认。

Order the backlog by urgent containment, prerequisite evidence/contracts, necessary fixes, then optimizations; adapt to actual dependencies. Avoid invented deadlines or named owners. If useful, estimate effort as small/medium/large with the change boundary and uncertainty, not unsupported hours or ROI. / 按紧急止损、前置证据契约、必要修复和优化安排清单，并服从实际依赖。不编造期限或负责人；需要时以小中大估算工作量并说明边界与不确定性，不编造工时或收益。

## 7. Define and Close Acceptance / 定义并闭合验收

An acceptance check names inputs/conditions, expected output or state, authoritative observation, environment, responsible role and pass/fail rule. “Improve robustness” is not a check. For performance, compare the same case population/configuration and record baseline, candidate, sample window, denominator and guardrails; unknown targets remain proposed until justified. / 验收须注明输入条件、预期输出状态、权威观察、环境、责任角色及通过失败规则。“提升稳健性”不是验收。性能对比使用相同样本口径配置，记录基线候选、窗口、分母及护栏；未知目标在有依据前标为建议值。

Distinguish `not_run`, `passed`, `failed`, `blocked` and `not_applicable`. Record command/procedure, version, actual result and limitations. Skipped tests or a validated document are not passed business acceptance. A test passing before the remedy does not demonstrate the remedy improved anything. / 区分未运行、通过、失败、受阻及不适用；记录命令流程、版本、实际结果及局限。跳过测试或文档通过校验不等于业务验收通过；修复前已通过的测试不能证明改进收益。

Track delivery stages separately: proposed → accepted plan → implemented → verified in a named environment → operationally observed, as applicable. Only claim a gap closed after its stated acceptance passes; leave longer-term effectiveness pending when observations are unavailable. Do not deploy or schedule monitoring merely to fill these states. / 按适用性分别跟踪建议、已接受方案、已实现、指定环境已验证及已运行观察。只有对应验收通过才声称缺口已关闭；缺长期观察时保留效果待验证。不为填满状态而擅自部署或创建定时监控。

## 8. Deliver and Check Completeness / 交付并检查完整性

Use [the report template](../assets/workflow-audit-report-template.md), scaled to scope. The report should answer: every node/edge reviewed? evidence for each judgment? what to retain? what to change first? who does what? how is closure demonstrated? / 按范围缩放使用报告模板，回答：节点连线是否全审、每项判断的证据、保留什么、先改什么、由谁做什么、如何证明闭合。

Keep an [EIR](eir-schema.md) slice in the report; findings, coverage and backlog are analysis-local companion records, not new normative runtime schema fields. Link IDs bidirectionally so an issue, remedy and acceptance case resolve to the same subject. / 在报告保留 EIR 切片；发现、覆盖和改进清单是分析内配套记录，不是新增规范运行时字段。编号双向关联，确保问题、补救和验收解析到同一对象。

Return the report in the requested medium. When a file is requested or warranted, use the analyzed project's `.harness-analysis/<analysis_id>/workflow-audit.md`; use [trace-schema.md](trace-schema.md) for an accompanying Trace proposal. Respect an explicit destination. Do not place project evidence in the reusable Skill or overwrite another analysis. / 按要求的媒介交付；请求或确有必要落盘时使用被分析项目的上述路径，按 Trace 契约附上追踪建议。遵循用户指定目的地，不把项目证据写入可复用 Skill，也不覆盖其他分析。

Before delivery, resolve references, reconcile coverage counts, retain adequate/unknown nodes, merge duplicate root causes, and check that proposed work is not described as completed. For substantial audits, an independent reviewer can check evidence and omitted seams against the same scope; reconcile disagreements rather than averaging them. / 交付前解析引用、核对覆盖统计、保留已足够及未知节点、合并重复根因，检查是否把建议写成完成。较大审计可由独立审查者按同范围检查证据和遗漏交接，分歧应核对而非取平均。
