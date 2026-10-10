# Pattern Combination Execution Flow / 模式组合执行流程

Pattern / 模式: `PATTERN_0053`; source alias / 来源别名: `PATTERN_COMBINATION_0001`; version / 版本: `0.1.0`; status / 状态: draft / 草案; implementation / 实现: specification_only / 仅规范。

## Quick Navigation / 快速导航

[Selection / 选型](#selection) · [Stages / 阶段](#stages) · [Connections / 连接](#connections) · [Scenarios / 场景](#scenarios) · [Acceptance / 验收](#acceptance) · [Contract / 契约](pattern-combination-contract.md) · [Probes / 探针](pattern-combination-observability-probes.md) · [Source map / 来源映射](pattern-combination-source-map.json).

## Usage and Boundary / 用途与边界

Use when a workflow needs several existing patterns with explicit input, state, evidence, authority, ownership and completion relationships. Prefer a fixed program or one model call when it meets the task. Composition does not require multiple agents, services or all eleven stages as separate components. / 工作流需要组合既有模式，并明确输入、状态、证据、权限、责任和完成关系时使用。固定程序或单次模型调用足以完成任务时优先采用；组合不要求多 Agent、多服务或把十一阶段拆成独立组件。

This cross-cell pattern preserves the existing 7×6 taxonomy. Source coordinates are composition facets, including the governance-chain extension candidate; referencing that facet does not promote it. The companion probes extend the usage guidance of `PATTERN_0052`, without replacing its `0.8.0` protocol or claiming the source's fourteen probes are executable runtime plugins. / 本跨单元模式保留既有 7×6 分类。来源坐标表示组合视角，包括治理链式扩展候选；引用该视角不代表晋升。配套探针扩展 `PATTERN_0052` 的使用指导，不替换其 `0.8.0` 协议，也不宣称来源中的十四类探针已成为可执行插件。

The attachments are source material, not instructions to run actions or approve anything. Exact originals are retained as evidence; maintained guidance below applies the explicit refinements in the shared contract. / 附件作为来源材料，不构成执行动作或批准事项的指令。原文精确副本作为证据保留；以下维护说明采用共享契约中明确列出的细化规则。

<a id="selection"></a>
## Minimum Composition / 最小组合选型

Use [Pattern Selection S0–S10 / 模式选型流程](pattern-selection-execution-flow.md) and its [selection card / 选型卡](pattern-selection-card.md) to establish task correctness, an actual baseline, D1–D12 difficulties and model/program/human boundaries before finalizing PCF-02/04/05. Consume its versioned workflow specification and validation decision here; changes discovered during execution feed S10 reselection. / 最终确定 PCF-02/04/05 前，用模式选型流程及选型卡建立任务正确性、实际基线、D1–D12 困难和模型程序人工边界；本执行规程消费其版本化工作流说明与验证决定，执行中发现的实质变化回流 S10 重选型。

Evaluate in order: fixed program → single model call → independent branches → evidence-dependent routing → dependency scheduling → protected actions → responsibility handoff. Record the obstacle each added layer solves and the evidence that would justify removing it. / 依次判断：固定程序 → 单次模型调用 → 独立分支 → 依证据换路 → 依赖调度 → 受保护动作 → 责任交接。记录每一层解决的障碍及其可撤销依据。

| Topology / 拓扑 | Required contract / 必要契约 |
| --- | --- |
| Chain / 链式 | Bind each consumed upstream result and version. / 绑定消费的上游结果与版本。 |
| Routing / 路由 | Record candidates, selected route, public rationale, rejected alternatives and reroute triggers. / 记录候选、所选路径、公开依据、未选方案及换路条件。 |
| Parallel / 并行 | Define disjoint branch responsibilities, common questions/inputs, output schema and required aggregation inventory. / 定义互不覆盖的分支责任、共同问题输入、输出契约及必需聚合清单。 |
| Orchestration / 编排 | Check dependencies and live readiness in the scheduler; persist versions and recovery points. / 由调度器检查依赖和实时就绪条件，持久保存版本与恢复点。 |
| Loop / 循环 | Specify information gain, changed attempt, local/global budgets and exit conditions. / 定义信息增益、尝试差异、局部总预算和退出条件。 |
| Hierarchy / 层级 | Freeze parent coverage, child scope, owner and result-return obligations before delegation. / 委派前冻结父目标覆盖、子范围、负责人和回收义务。 |

<a id="stages"></a>
## Execution Stages / 执行阶段

The `PCF` labels below are local locators for the source's §9.1–9.11, not source-owned IDs. Each stage carries its source heading and full-section fingerprint in the source map. / 下列 `PCF` 是来源 §9.1–9.11 的本地定位编号，并非原文编号；映射保留章节标题及全文指纹。

| ID | Source stage / 来源阶段 | Procedure and exit / 执行与退出 | Failure route / 失败路由 |
| --- | --- | --- | --- |
| PCF-01 | 阶段一：建立任务边界 | Freeze objective, mandatory deliverables, acceptance, prohibitions, scope, risk, identities and state version. / 冻结目标、必需交付、验收、禁止项、范围、风险、标识和状态版本。 | Critical ambiguity → waiting_data. / 关键歧义进入等待资料。 |
| PCF-02 | 阶段二：判断是否需要模式组合 | Select the smallest sufficient program/model/pattern set; record layer benefit and removal criteria. / 选择足够的最小程序、模型或模式集合，记录增益和撤销条件。 | Unjustified layer → remove or trial separately. / 无明确价值的层移除或单独对照。 |
| PCF-03 | 阶段三：绘制任务地形 | Map task, state, authority and evidence lines; mark branches, dependencies, exploration, deterministic actions, acceptance and rollback. / 绘制任务、状态、权限、证据四条线，标注分支、依赖、探索、确定动作、验收和回退。 | Missing ownership or dependency → clarify before dispatch. / 缺责任或依赖先补齐再派发。 |
| PCF-04 | 阶段四：选择拓扑 | Select a primary topology and only necessary nested topologies using the contracts above. / 按上述契约选择主拓扑及必要嵌套。 | Unsafe shared write or missing aggregate contract → redesign. / 共享写入无保护或缺聚合契约则重设计。 |
| PCF-05 | 阶段五：选择工程模式并定义组合关系 | Bind every connection to an object, version, completeness requirement, failure route and authority consequence. / 每条连接绑定对象、版本、完整性要求、失败路由及权限影响。 | Incompatible outputs/versions → return upstream. / 输出版本不兼容则返回上游。 |
| PCF-06 | 阶段六：建立计划与节点契约 | Version the graph; assign owner, input references, readiness, executor type, output, completion, error class, budget and next routes. / 版本化任务图，指定负责人、输入引用、就绪、执行方式、输出、完成、错误类、预算及后续路径。 | Unverifiable node such as “process data” → rewrite acceptance. / “处理数据”等不可验收节点先重写条件。 |
| PCF-07 | 阶段七：调度和执行 | Reload authoritative state; check dependencies, current authority and shared budgets; create attempt, execute, persist raw receipts, verify locally and conditionally commit state. / 重读权威状态，检查依赖、实时权限与共享预算，创建尝试、执行、保存原回执、局部核验并条件提交状态。 | No ready node → distinguish wait, plan defect, conflict and terminal; never busy-loop. / 无就绪节点时区分等待、计划缺陷、冲突与终态，禁止空转。 |
| PCF-08 | 阶段八：处理循环、修订和重新规划 | Retry only a local implementation error with changed input/check, unchanged valid premise, authority and remaining budgets; refuted hypotheses return to investigation; changed graph creates a new plan. / 仅在前提权限有效、预算剩余且修改或检查有差异时重试局部实现错误；假设被否回调查，任务图变化新建计划。 | No progress, exhausted budget, conflict or increased risk → safe stop/handoff. / 无进展、预算耗尽、冲突或风险升高则安全停止或交接。 |
| PCF-09 | 阶段九：治理真实动作 | Bind action, target, input version, prerequisite, allowed/forbidden scope, approval, post-query and compensation. Keep approval, blast-radius limit and pre/post guards distinct. / 绑定动作、对象、输入版本、前置条件、允许禁止范围、审批、后查与补偿，分开审批门、爆炸半径及前后护栏。 | Mismatch/expired authority → wait or reapprove; unknown effects → reconcile before retry. / 失配或过期则等待或重审批，效果未知先对账再重试。 |
| PCF-10 | 阶段十：聚合与验收 | Reconcile required branches, common versions, duplicates/conflicts and evidence; evaluate all five gates below. / 核对必需分支、共同版本、重复冲突与证据，评估下述五道门。 | Missing mandatory result or failed gate → incomplete with recovery owner. / 必需结果缺失或闸门失败则保持未完成并指定恢复责任。 |
| PCF-11 | 阶段十一：交接、归档和复用 | When role, authority, responsibility or context changes, deliver version-bound artifacts, evidence, completed/pending work and recovery point; obtain acceptance and explicit responsibility transfer. Archive reusable evidence. / 角色权限责任或上下文变化时交付版本化工件、证据、已完未完事项与恢复点，取得接收及明确责任转移，归档可复用证据。 | Unaccepted handoff → retain current owner; ordinary function calls need no agent handoff. / 交接未接收则保留原责任，普通函数调用无需 Agent 交接。 |

<a id="connections"></a>
## Composition Connections / 组合连接

| Relation / 关系 | Contract check / 契约检查 |
| --- | --- |
| Feed-forward / 前后供料 | Downstream receives required meaning and original evidence, beyond valid syntax. / 下游得到所需语义与原始证据，不能只检查格式。 |
| Nesting / 内部嵌套 | Child loops and branches consume the same parent goals, completion constraints and cumulative budgets. / 子循环分支受父目标、完成约束与累计预算限制。 |
| Execution constraint / 执行约束 | Approval, scope and pre/post checks refer to the same immutable action/input version. / 审批、范围、前后检查绑定同一不可变动作输入版本。 |
| Shared capability / 共享能力 | One authoritative state, version-checked writes, isolated branch artifacts, explicit aggregation. / 单一权威状态、版本写检查、分支工件隔离及显式聚合。 |
| Responsibility transfer / 责任交接 | Deliverable version, receiving owner, evidence and restart position agree. / 交付版本、接收负责人、证据及续做位置一致。 |
| Feedback / 反馈回路 | Classify the failure before choosing local retry, investigation or replanning. / 先分类失败，再选择局部重试、调查或重规划。 |

```yaml
# Structural template, not an executable plan / 结构模板，不是可执行计划
edge_id: EDGE_A_B
upstream_node_id: NODE_A
downstream_node_id: NODE_B
relation: feed_forward
objects: [{artifact_id: ARTIFACT_A, artifact_version: 2}]
required_fields: [evidence_refs, result]
failure_route: NODE_A
authority_change_requires_review: true
```

## State, Recovery and Budgets / 状态、恢复与预算

Task states: pending_analysis → running → pending_acceptance → completed. Running may enter waiting_data, waiting_approval, replan_required, local_failure, human_takeover or terminated. Waits resume only after the missing condition is satisfied; local failure resumes only with a valid recovery path and budget. / 任务状态为待分析 → 运行 → 待验收 → 完成；运行可转等待资料、等待审批、需重规划、局部失败、人工接管或终止。等待须条件补齐才能恢复；局部失败须有恢复路径和预算。

Recovery preserves `task_id` and creates a new `run_id`; retry preserves `node_id` and creates a new `attempt_id`. Store plan/version, read state version, evidence, approval status, committed effects and checkpoint together. Do not reset an effected action to “not executed”; query its actual outcome, record compensation separately and retain unknown effects. / 恢复保留任务标识并新建运行标识，重试保留节点标识并新建尝试标识；共同保存计划版本、读取状态版本、证据、审批、已提交效果和检查点。产生效果的动作不可重置未执行，应查询实际结果、单独记录补偿并保留未知效果。

For each comparable budget dimension, admissible remaining use is the minimum of task, branch, node and loop balances, additionally bounded by tool and external-impact limits. Concurrent branches need atomic reservations on the shared parent account; nested allowances do not multiply. Time, calls, money and impact are separate units, not one scalar minimum. / 每个可比较预算维度取任务、分支、节点和循环余额最小值，再受工具与外部影响上限限制。并发分支须在共享父账户原子预留；嵌套额度不相乘。时间、调用、费用及影响分别计量，不能混成一个标量最小值。

| Failure / 失败 | Required destination / 必需去向 |
| --- | --- |
| Missing material / 材料缺失 | Perception; request a permitted source or declare unavailable. / 感知节点，合法补取或声明不可获得。 |
| Evidence conflict / 证据冲突 | Evidence reconciliation; compare version, time, scope and effective conditions. / 证据核对，比较版本时间范围与生效条件。 |
| Compression loss / 压缩丢失 | Original evidence and compression node; invalidate affected claims. / 回取原文重压缩，标记受影响结论失效。 |
| Refuted hypothesis / 假设被否 | Investigation; update competing explanations. / 回调查并更新候选解释。 |
| Local implementation error / 局部实现错误 | Bounded changed attempt at the same node. / 当前节点限次差异重试。 |
| Invalid plan / 计划失效 | New plan version, dependency and authority review. / 新计划版本，复核依赖与权限。 |
| Waiting approval / 等待审批 | Persist and wait; consumes no failure retry. / 保存并等待，不消耗失败重试次数。 |
| Approval mismatch / 审批失配 | Governance entry; no automatic inheritance. / 回治理入口，不自动继承授权。 |
| Partial success / 部分成功 | Query actual affected objects; authorized compensation or continuation. / 查询实际影响对象，受权补偿或续做。 |
| State conflict / 状态冲突 | Freeze writes, reload authority and reconcile. / 冻结写入，重读权威并核对。 |
| Budget exhaustion / 预算耗尽 | Safe checkpoint with failure package and owner. / 在安全点交付异常包与责任。 |
| Acceptance failure / 验收失败 | Relevant gate's node: revision, compensation or replanning. / 对应验收节点，修订补偿或重规划。 |

<a id="scenarios"></a>
## Scenario Adapters / 场景适配器

| Scenario / 场景 | Minimum useful flow / 最小适用流程 | Required evidence / 必要证据 |
| --- | --- | --- |
| Research / 资料研究 | Triage → independent retrieval → exception-preserving compression → gather → generate/review → acceptance. / 分诊 → 独立检索 → 保留例外的压缩 → 汇聚 → 生成评审 → 验收。 | Source location, version, scope/date and exceptions per claim; reviewer can retrieve originals independently. Add hierarchy or adversarial review only for an actual need. / 每项结论保留原文位置版本范围日期例外，评审可独立回取；确有需要才加层级或对抗评审。 |
| Troubleshooting / 故障排查 | Symptoms → hypotheses → discriminating check → update → plan → fix/test → review → governed action → regression. / 症状 → 假设 → 区分性检查 → 更新 → 计划 → 修复测试 → 评审 → 受治理动作 → 回归。 | Check names hypotheses it distinguishes; disproved premise returns to investigation, unchanged failure stops; preserve affected scope and recovery point. / 检查说明区分哪些假设，前提被否回调查，无变化失败停止，保留受影响范围及恢复点。 |
| Business operation / 业务办理 | Clarify target/version → dependency plan → concrete approval → live pre-check → write → independent query → compensate/continue → acceptance. / 明确对象版本 → 依赖计划 → 具体审批 → 实时前查 → 写入 → 独立查询 → 补偿续做 → 验收。 | Action-specific authority, exact affected objects and actual business result; retries cannot widen permission. / 具体动作授权、精确影响对象和真实业务结果，重试不得扩大权限。 |
| Short fixed work / 简单固定任务 | Program or one call with references and acceptance. / 程序或单次调用，保留引用并验收。 | Preserve required inputs/results; do not add delegation, loops or review without demonstrated benefit. / 保留必要输入结果，无明确收益不增加委派循环或评审。 |

## Existing Pattern Entry Points / 既有模式接入点

These are candidates selected by the actual obstacle, not a mandatory component list. Read each selected design and its paired observability document before host integration. / 以下按实际障碍选择，并非强制组件清单；接入宿主前读取所选设计及其配套观测文档。

| Need / 需求 | Existing patterns / 既有模式 | Composition constraint / 组合约束 |
| --- | --- | --- |
| Independent research / 独立资料方向 | [Fan-Out/Gather / 扇出汇聚](patterns/collaboration/collaboration-parallel.md), [RAG / 检索增强](patterns/memory/memory-chain.md), [Progressive Discovery / 渐进发现](patterns/perception/perception-loop.md), [Generator-Critic / 生成评审](patterns/reflection/reflection-chain.md) | Separate branch artifacts and preserve original evidence through [Semantic Compaction / 语义压缩](patterns/perception/perception-chain.md). / 分支工件隔离，压缩仍保留原证据。 |
| Evidence changes the next check / 新证据改变下一步 | [Hypothesis Testing / 假设验证](patterns/reasoning/reasoning-loop.md), [Progress Tracking / 进度追踪](patterns/memory/memory-orchestration.md) | Reroute on refutation; do not pre-fix every investigation step. / 否定后换路，不预先固定所有调查步骤。 |
| Known fix with dependencies / 原因明确且修改有依赖 | [Plan-and-Execute / 规划执行](patterns/action/action-orchestration.md), [Tool Dispatch / 工具调度](patterns/action/action-routing.md), [Self-Heal / 局部自愈](patterns/reflection/reflection-loop.md) | Scheduler checks dependencies; local repair does not widen scope or multiply budget. / 调度器检查依赖，局部修复不扩范围或倍增预算。 |
| Distinct roles or permissions / 不同角色权限 | [Hierarchical Delegation / 层级委派](patterns/collaboration/collaboration-hierarchy.md), [Handoff Chain / 交接链](patterns/collaboration/collaboration-chain.md), [Adversarial Review / 对抗评审](patterns/collaboration/collaboration-loop.md) | Isolate responsibility and context; use independent review only when differing evidence/roles add value. / 隔离责任上下文，证据角色差异有价值时才加独立评审。 |
| Long-running recovery / 长任务恢复 | [Progress Tracking / 进度追踪](patterns/memory/memory-orchestration.md), [Failure Diary / 失败日志](patterns/memory/memory-loop.md) | Persist versioned state and effects beyond chat history. / 聊天外持久保存版本化状态和效果。 |
| Protected external effects / 受保护外部效果 | [Approval Gate / 审批门](patterns/governance/governance-routing.md), [Blast Radius / 爆炸半径](patterns/governance/governance-hierarchy.md), [Guardrail Sandwich / 前后护栏](patterns/action/action-hierarchy.md), [Progressive Commitment / 渐进承诺](patterns/governance/governance-parallel.md) | Bind exact action version and actual limits; neither confidence nor review substitutes for authority. / 绑定精确动作版本及实际限额，自信和评审均不替代权限。 |

<a id="acceptance"></a>
## Five Acceptance Gates / 五道验收门

1. Task: every required deliverable and branch has its contractual outcome. / 任务：所有必需交付和分支均有契约要求的结果。
2. Evidence: key claims return to valid originals, preserving exceptions and qualifications. / 证据：关键结论可回溯有效原文，并保留例外限定。
3. State: task, plan, nodes and actual external effects agree and can be recovered. / 状态：任务计划节点与实际外部效果一致并可恢复。
4. Authority: actual actions match approved target, version, scope, limits and validity. / 权限：实际动作符合批准对象版本范围限额及有效期。
5. Result: independent tests, queries or authorized confirmations demonstrate the business outcome. / 结果：独立测试查询或授权确认证明业务结果。

Report passed, failed, pending or explicitly authorized waiver for each criterion, with versioned evidence and owner. Missing mandatory work stays incomplete even when its reason is documented; only a task contract that explicitly permits a declared gap can accept that gap. Observation gaps alone do not overturn independently verified business outcomes. / 各项记录通过、失败、待定或显式授权豁免，并带版本证据和负责人。说明原因不等于完成必需工作；只有任务契约显式允许缺失说明时才可据此验收。纯观测缺口不单独推翻已独立核验的业务结果。

Final package: business deliverable, evidence ledger, state/plan snapshot, action receipts, public decision summaries, unresolved issues and per-gate acceptance. Handoffs additionally name receiver, remaining duties, recovery and return point. / 最终包包含业务交付、证据账本、状态计划快照、动作回执、公开决策摘要、未解决问题及逐门验收；交接另含接收者、剩余职责、恢复与返回位置。

## Host Integration and Constraints / 宿主接入与约束

Existing reasoning, workflow routing, plan/execute, action, collaboration and governance modules cover parts of this flow; no general composition scheduler or these 54 metric calculators is added here. Adopters implement the task parser, dependency scheduler, authoritative version store, evidence ledger, action gateway, governance/acceptance checks and recovery routes; event adapters remain optional. / 既有推理、工作流路由、计划执行、行动、协作及治理模块覆盖部分流程；本次未新增通用组合调度器或这 54 项指标计算器。采用系统需实现任务解析、依赖调度、权威版本存储、证据账本、动作入口、治理验收检查及恢复路由；事件适配器可选。

Use the [shared contract](pattern-combination-contract.md) for wire fields, source conflicts, open integration cases and validation boundaries. Never claim that document validation executes the source business cases or grants action authority. / 使用共享契约确定传输字段、来源冲突、待接入用例和验证边界；文档校验不执行来源业务用例，也不授予行动权限。

## Source Acceptance Cases / 来源验收用例

Status / 状态: `not_executed`. These are source scenarios, not passed runtime tests. / 以下为来源场景，不是已通过的运行测试。

| ID | Source case / 来源用例 | Input and expected result / 输入与预期 |
| --- | --- | --- |
| PCE-01 | 用例一：短任务不过度设计 | Three short files fit one call → use a simple chain, no fan-out/delegation; retain originals. / 输入只有三份短文件，单次模型调用即可完整比较。 预期：选择简单链式处理，不启动多分支和层级委派；仍保留关键原文引用。 |
| PCE-02 | 用例二：并行研究缺少一个分支 | Only two of three regional results arrive → mark the missing required branch; do not complete. / 三个地区只返回两个地区的结果。 预期：聚合器标记缺失分支，不能把任务标记为完成。 |
| PCE-03 | 用例三：摘要遗漏例外 | A custom-goods exception is lost in summary → reviewer retrieves original and triggers revision. / 原文包含“定制商品除外”，摘要漏掉该信息。 预期：评审能够通过原文回取路径发现问题并触发修订。 |
| PCE-04 | 用例四：故障排查假设被推翻 | Timeout hypothesis is contradicted by a fast response with missing fields → investigate schema/caller instead of increasing timeout. / 原先怀疑超时，日志显示请求快速返回但字段缺失。 预期：路由转向响应格式和调用方，不继续修改超时参数。 |
| PCE-05 | 用例五：修复循环失控 | Outer three rounds nest five repairs → task budget caps total attempts; do not assume fifteen attempts. / 外层调查三轮，内层修复五轮。 预期：总尝试数受任务级预算限制，不自动扩张为十五次。 |
| PCE-06 | 用例六：审批范围不一致 | Approval covers one department but plan adds another → stop mismatched write and request new approval. / 审批只允许修改一个部门，执行计划新增了第二个部门。 预期：原审批失效，写入被停止并要求重新审批。 |
| PCE-07 | 用例七：接口返回成功但业务未生效 | Import receipt succeeds but query still shows old configuration → partial success or failed acceptance, not completed. / 导入接口返回成功，查询目标对象发现仍是旧配置。 预期：任务进入验收失败或部分成功，不得宣告完成。 |
| PCE-08 | 用例八：中断后恢复 | Interrupted during approval wait → reload same plan, approval and completed effects; do not repeat backup/import. / 任务在等待审批时中断。 预期：恢复后读取同一计划版本、审批状态和已完成动作，不重复执行备份或导入。 |
