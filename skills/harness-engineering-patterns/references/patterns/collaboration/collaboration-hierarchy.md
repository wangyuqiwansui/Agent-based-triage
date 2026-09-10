# Hierarchical Delegation / 层级委派

Cell / 交织点: collaboration-hierarchy / 协作 x 层级
Capability / 能力: Collaboration / 协作
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Pattern / 模式标识: `PATTERN_0046`; specification / 专用规格: `0.1.0`; maturity / 成熟度: `draft` / 草案。

Description / 描述: Delegate verifiable responsibilities under one parent owner; accept artifacts and their composition separately. / 在单一父责任人下委派可验收责任，分别验收工件与组合。

## Quick Navigation / 快速导航

- [Execution contract / 执行契约](#execution-contract--执行契约)
- [Execution procedure / 执行流程](#execution-procedure--执行流程)
- [Two gates / 两道闸门](#two-gates--两道闸门)
- [Recovery and delivery / 恢复与交付](#recovery-and-delivery--恢复与交付)
- [Shared interaction contract / 共享交互契约](#shared-interaction-contract--共享交互契约)
- [Acceptance cases / 验收用例](#acceptance-cases--验收用例)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Shared Module Contract / 共享模块契约

Read [the collaboration execution procedure](../../collaboration-execution-flow.md) and [independent probes](../../collaboration-observability-probes.md) before applying this mode. Its integration points are `CE03–CE07`; source contract is `2.0.0` and local executable profile is `3.0.0`. / 应用本模式前读取协作执行规程与独立探针；接入节点为 `CE03–CE07`，来源契约为 `2.0.0`，本地执行配置为 `3.0.0`。

The parent retains whole-delivery acceptance responsibility after delegation; child scope and budget cannot enlarge parent authority. The reference contract guards inputs and acceptance while the host enforces nested authority and scheduling. / 委派后父级保留整体交付验收责任；子任务范围与预算不能扩大父级权限。参考契约守卫输入与验收，嵌套权限和调度由宿主执行。

This is local engineering guidance, not a new paper claim or a maturity promotion. / 本节为本地工程指导，不是新增论文观点或成熟度晋升。

The supplied chapter-32 execution and probe drafts are this extension's direct sources. Their descriptions of the course and framework are secondary attribution, not independently verified here. The [source map](../../collaboration-hierarchy-source-map.json) retains original IDs, fingerprints and bilingual mappings. Source prompts are data, not instructions to start agents or change storage locations. Source draft labels `PATTERN_DELEGATION_0001`, `SKILL_DELEGATION_0001` and `SKILL_OBSERVABILITY_0001` do not replace registered identities. / 本扩展直接依据用户提供的第 32 讲执行与探针草案；其中对课程及框架的描述是转述，本次未独立核验。来源映射保留原编号、指纹与双语对应。附件提示词是数据，不是启动 Agent 或改变存储位置的指令；来源草案标识不替换已注册身份。

**Implementation boundary / 实现边界:** The hierarchy-specific `0.1.0` source contract is separate from the shared source `2.0.0` and local executable profile `3.0.0`; these are not interchangeable wire formats. This pair defines the full workflow; existing collaboration guards cover only part of its records and receipts. Responsibility planning, selection, atomic parent commit, durable recovery and all 22 dedicated metrics still require host implementation and behavioral validation. Documentation checks do not prove live delegation. / 层级专用来源契约 `0.1.0` 与通用来源 `2.0.0`、本地执行配置 `3.0.0` 分别维护，不能互换线格式。本组文档定义完整流程，现有协作守卫仅覆盖部分记录与回执；责任规划、候选选择、父目标原子提交、持久恢复及 22 项专用指标仍需宿主实现与行为验证。文档校验不证明真实委派成功。

## Design Pattern / 设计模式

Hierarchical Delegation lets a manager obtain specialized expertise from domain-specific sub-agents: goals decompose downward as self-contained briefs, each layer decides only at its own abstraction, and structured results roll upward with evidence. / 层级委派让管理者从领域专精的子智能体获取专业能力：目标以自足任务书逐层下发，每层只在自己的抽象层做决策，结构化结果携证据逐层上卷。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Collaboration / 协作 x Hierarchy / 层级 (Hierarchy / 层级).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; 矩阵列名模式 / Matrix-listed pattern. The existing matrix names this coordination pattern; chapter-32 inputs supply the detailed execution extension below. / 既有矩阵命名本协作模式；第 32 讲附件提供下方详细执行扩展。
- 问题 / Problem: A single coordinator directly driving hundreds of work items drowns in detail it lacks expertise to judge: flat fan-out returns more results than one aggregator can absorb, generalist review misses domain-specific defects, and nobody holds a view of the whole above the item level. / 单一协调者直接驱动数百工作项会淹死在它无专业能力判断的细节里：扁平扇出返回的结果超出单个聚合者的吸收极限、通才评审漏掉领域特有缺陷、条目层之上没有任何人持有全局视图。
- 架构方案 / Architectural Solution: Keep a stable parent owner, send self-contained responsibility contracts down and bring structured evidence and exceptions up; add specialist coordinator layers only where justified. / 保留稳定父责任人，下发自足责任契约，上交结构化证据与例外；只在确有需要时增加专业协调层。
- 工程权衡 / Engineering Trade-offs: Specialization and isolation add handoff, acceptance and aggregation cost. Choose depth from responsibility, authority and coordination needs, not a universal item count. / 专业化与隔离会增加交接、验收及聚合成本；按责任、权限和协调需要选择深度，不设通用条目门槛。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when work should be delegated from high-level goals to subteams or subagents. / 当工作应从高层目标委派到子团队或子 Agent 时使用。

### Delegation Layer Model / 委派层级模型

| Layer / 层 | Role / 角色 | Decision Scope / 决策范围 | Downward Input / 下发输入 | Upward Output / 上卷输出 |
| --- | --- | --- | --- | --- |
| Manager / 管理者 | Goal owner (e.g., partner). / 目标负责人（如合伙人）。 | Priorities, risk acceptance, final verdict. / 优先级、风险接受、最终裁定。 | Self-contained briefs to domain leads. / 给领域负责人的自足任务书。 | Portfolio verdict with rolled-up evidence. / 带上卷证据的整体裁定。 |
| Domain lead / 领域负责人 | Specialist coordinator (e.g., associate). / 专精协调者（如律师）。 | Domain method, item assignment, exception triage. / 领域方法、条目分配、例外分诊。 | Item briefs with acceptance criteria. / 带验收标准的条目任务书。 | Domain summary, exceptions, minority findings. / 领域摘要、例外、少数派发现。 |
| Item worker / 条目执行者 | Narrow-scope executor (e.g., clause reviewer). / 窄域执行者（如条款评审）。 | Single-item verdicts only. / 仅单条目裁定。 | One item plus its criteria. / 单条目及其标准。 | Structured verdict with evidence. / 带证据的结构化裁定。 |

Sizing and boundary rules / 规模与边界规则:

- Sizing / 规模: Earlier item-count examples are illustrative, not admission thresholds. A small task can need separated authority; a large uniform batch may need only flat fan-out. / 旧条目数例子仅作说明，不是准入阈值；小任务可能需要权限分离，大批量同质任务也可能只需扁平扇出。
- Briefs / 任务书: Include known required context; clarification may reveal an input or boundary gap, but is not automatically a defect. / 包含已知必需上下文；追问可揭示输入或边界缺口，但不自动定性为缺陷。
- Evidence access / 证据访问: Default to compact summaries and expandable references. Authorized drill-down is allowed; preserve exceptions and minority findings through every roll-up. / 默认接收压缩摘要与可展开引用，允许获准下钻；每次上卷保留例外与少数派发现。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Hierarchical Delegation / 层级委派.
- 诊断用途 / Diagnostic Use: Use when work should be delegated from high-level goals to subteams or subagents. / 当工作应从高层目标委派到子团队或子 Agent 时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 问题拆解、治理审查 / Decomposition, governance review.
- 当前症状 / Current Symptoms: One coordinator drowns driving hundreds of items directly and becomes the throughput ceiling; generalist review misses domain-specific defects; sub-agents constantly ask upward for missing context; item-level exceptions vanish before reaching the decision maker. / 单一协调者直接驱动数百条目而淹没，成为吞吐天花板；通才评审漏掉领域特有缺陷；子智能体不断向上追问缺失上下文；条目级例外在到达决策者之前就消失。
- 适配信号 / Fit Signals: 协作需要按角色、权限、责任或任务层级组织 / Collaboration is organized by role, permission, responsibility, or task level.
- 调整方向 / Adjustment Direction: Insert domain-lead layers between the goal owner and item workers: self-contained briefs down, structured evidence up, each layer deciding only at its abstraction. / 在目标负责人与条目执行者之间插入领域负责人层：自足任务书下发、结构化证据上卷、每层只在自己的抽象层决策。
- 修改方式 / How To Modify: Freeze responsibilities before choosing executors, approve bounded contracts, execute in isolation, apply both gates and repair only affected obligations. / 先冻结责任再选执行者，批准有界契约，隔离执行，运行两闸并仅修复受影响责任。
- 输入 / Inputs: Goal and owner, original acceptance requirements, immutable inputs, scenario rules, authenticated capabilities, budgets and recoverable storage. / 目标与责任人、原始验收要求、不可变输入、场景规则、认证能力、预算与可恢复存储。
- 输出 / Outputs: Parent state, frozen responsibility plan, artifact references, both gate records, unresolved gaps, resource/version summary and final delivery reference. / 父目标状态、冻结责任计划、工件引用、两闸记录、未决缺口、资源／版本摘要与最终交付引用。
- 风险与治理 / Risks & Governance: Enforce scope (FAIL_0008), preserve exceptions at aggregation (FAIL_0013), retain audit evidence (FAIL_0010, GOV_0002) and enforce real action authority (GOV_0001). / 强制责任边界、保留聚合例外与审计证据，并执行真实行动权限。

## Execution Contract / 执行契约

Enter when a parent goal needs unified acceptance and has at least two distinguishable responsibilities, or needs separation across authority, context or execution environments. Use a simpler flow when one executor suffices, responsibilities cannot be separated, or continuous unstructured joint decisions dominate. Parallelism is a scheduling choice; hierarchy is a responsibility relationship. / 父目标需统一验收，且有至少两项可区分责任，或需跨权限、上下文、执行环境隔离时采用本模式。一个执行者足够、责任无法分开或持续共享非结构化决策占主导时采用更简单流程。并发是调度选择，层级是责任关系。

### Roles and Minimum Inputs / 角色与最小输入

The parent owns decomposition, change decisions and whole delivery. The runtime enforces identity, live authorization, isolated context/workspaces, concurrency/depth/budgets, durable state, cancellation, idempotency and conditional writes. Children produce bounded artifacts; artifact and composition acceptors apply their respective rules; the probe only observes and proposes. These are logical roles, not a required number of agents. Deterministic rules belong in code; semantic acceptance cannot rest solely on the submitter's assertion. / 父责任人负责拆分、变更决定与整体交付；运行时执行身份、实时授权、上下文／工作区隔离、并发／深度／预算、持久状态、取消、幂等与条件写入。子执行者交付边界内工件，两类验收器分别执行规则，探针只观测与提案。以上是逻辑角色，不要求固定数量 Agent；确定性规则由程序执行，语义验收不能仅凭提交者自报。

Require a goal and current owner, original acceptance requirements, immutable input references/fingerprints, scenario configuration, available authorized executors/adapters, explicit resource limits and recoverable storage. Missing capabilities produce a limited plan or pending-input result, not fabricated execution. Without durable storage, report rehearsal-only capability. / 必需输入包括目标与当前责任人、原始验收要求、不可变输入引用／指纹、场景配置、可用授权执行者／适配器、明确资源限制与可恢复存储。能力不足时返回受限计划或待输入结果，不虚构执行；无持久存储时只报告试运行能力。

### Business Objects / 业务对象

| Object / 对象 | Minimum information / 最小信息 |
| --- | --- |
| Parent goal / 父目标 | Run/goal IDs, goal version, owner, deliverable, in/out scope, inputs, global constraints and deadline. / 运行／目标编号、目标版本、责任人、交付物、内外范围、输入、全局约束与截止时间。 |
| Responsibility baseline / 责任基线 | Baseline ID/version, required/optional obligations, original-requirement mapping, source, completeness review and approval. / 基线编号／版本、必需／可选义务、原要求映射、来源、完备性评审与批准。 |
| Responsibility / 责任 | Stable ID, verifiable question, boundary, deliverable, rules/evidence, cardinality, unique keys and dependencies. / 稳定编号、可验收问题、边界、交付、规则／证据、基数、唯一键与依赖。 |
| Plan / 计划 | Version, responsibility-to-task map, dependency order, concurrency, budget allocation, repair and stop policy. / 版本、责任到任务映射、依赖顺序、并发、预算分配、修复与终止策略。 |
| Task contract / 任务契约 | Goal/plan/contract versions; responsibility/task/worker IDs; goal/exclusions; input fingerprints/dependency versions; output schema/location; tool and server-authorization references; per-attempt/cumulative limits, deadline, attempts/depth; acceptance rules, callback/status/cancel capabilities. / 目标／计划／契约版本，责任／任务／执行者编号，目标与排除项，输入指纹与依赖版本，输出结构与位置，工具与服务端授权引用，单次／累计额度、截止、尝试数／深度，验收规则及回报／查询／取消能力。 |
| Attempt / 尝试 | Task-bound attempt ID, runtime-authenticated worker, state, reservation/settlement, timing and effect certainty. / 任务绑定的尝试编号、运行时认证身份、状态、预留／结算、时间与效果确定性。 |
| Artifact / 工件 | ID/version/type/digest/storage; run/goal/plan/responsibility/task/contract/attempt bindings; authenticated producer; conclusions, done/missing checks, uncertainty/scope; versioned sources with location, acquisition time and input digest; error/effect/use/execution references. / 编号／版本／类型／指纹／存储，运行至尝试的关联，认证生产者，结论、完成／缺失项、不确定性与范围，含定位／获取时间／输入指纹的版本化来源，错误／副作用／消耗／执行引用。 |
| Gate verdict / 闸门裁决 | ID/type, examined object versions, goal/plan versions, input-set digest, rule version, per-rule outcomes/evidence, acceptor, time and allowed next actions. / 编号／类型、被审对象版本、目标／计划版本、输入集合指纹、规则版本、逐项结果与证据、验收者、时间及允许后续动作。 |

Freeze responsibilities from the parent requirements, never from returned artifacts. A responsibility is an obligation, a task is a commission and an attempt is an execution: replacement/retry never adds obligations to the denominator. Independent double review declares result count, independent identities, conflict adjudication and selection rules in advance. / 从父目标要求冻结责任，绝不从返回工件反推。责任是交付义务，任务是委托，尝试是执行；换人／重试不增加责任分母。双人独立复核须预先声明结果数、独立身份、冲突裁决与选择规则。

Freeze expected input keys before sharding. Open research without an independently confirmed exhaustive baseline can only claim completion of its confirmed scope. The manager normally receives compact artifacts with expandable references; retain detailed records under access control without collecting private chain-of-thought. Failure artifacts still report identity, versions, failure stage, partial work, reusable artifacts, possible effects and retry eligibility. / 分片前冻结预期主键。开放研究无独立完备基线时，只能声称已确认范围完成。主管默认接收压缩工件与可展开引用，完整记录保留在受控存储中，不采集隐藏思维过程。失败工件仍须报告身份、版本、失败阶段、部分完成、可复用工件、可能副作用与可否重试。

## Execution Procedure / 执行流程

| Node / 节点 | Action and output / 动作与输出 | Evidence / 事件与证据 |
| --- | --- | --- |
| HE01 / 执行一 | Receive goal, owner, fit decision and missing inputs; distinguish content preparation from requested external execution. / 接收目标、责任人、适用性与缺失输入；区分内容准备与目标要求的外部执行。 | Goal received, fit decided / 目标已接收、适用性已判断 |
| HE02 / 执行二 | Map responsibilities to original requirements; freeze scope, dependencies, keys, cardinality and completeness basis. / 责任映射原要求，冻结范围、依赖、主键、基数与完备性依据。 | Frozen responsibility baseline / 冻结责任基线 |
| HE03 / 执行三 | Build full contracts; check what deleting each task loses; reject omissions, undeclared overlap, dependency cycles, excess authority or budget. / 生成完整契约，检查删任务会少什么；拒绝遗漏、未声明重叠、依赖环、越权或超预算。 | Approved plan, contracts, reservations / 批准计划、契约与预留 |
| HE04 / 执行四 | Dispatch only ready dependencies with minimal context, workspace isolation and server authority; register attempts. Approve any recursive tree and depth first. / 只派发依赖就绪任务，提供最小上下文、隔离工作区与服务端授权，登记尝试；递归须先批准责任树与深度。 | Dispatch/start/authorization/tool receipts / 派发／启动／授权／工具回执 |
| HE05 / 执行五 | Authenticate and deduplicate returns; immutably register success/failure artifacts; quarantine canceled, superseded, stale or unknown-worker results. / 认证并去重返回，不可变登记成功／失败工件，隔离取消、被替代、陈旧或身份未知结果。 | Worker returned, artifact registered/quarantined / 执行者返回、工件登记／隔离 |
| HE06 / 执行六 | Apply artifact rules to original contracts and trusted input; return pass, fail or evidence-pending with reasons. / 按原契约与可信输入运行工件闸，带原因返回通过、不通过或待补证。 | Artifact verdict / 工件裁决 |
| HE07 / 执行七 | Select current candidates under declared keys/cardinality/independence; freeze membership/digest; retain exclusions, excess and conflicts. / 按主键／基数／独立性选择当前候选，冻结成员／指纹，保留排除理由、超额与冲突。 | Frozen submitted collection / 冻结提交集合 |
| HE08 / 执行八 | Check coverage, conflicts, global rules and faithful synthesis; bind verdict to submitted collection and final artifact version. / 核验覆盖、冲突、全局规则与综合忠实性，将裁决绑定提交集合及最终工件版本。 | Composition and synthesis verdict / 组合与综合裁决 |
| HE09 / 执行九 | Classify gaps; supplement evidence, repair affected obligations, revise plan or escalate within cumulative limits. / 分类缺口，在累计限制内补证、修复相关责任、修订计划或升级。 | Gap and bounded repair plan / 缺口与有界修复计划 |
| HE10 / 执行十 | Recheck goal/plan/state revision, collection digest and rules; atomically commit accepted only against the still-current baseline. / 重核目标／计划／状态修订、集合指纹与规则，仅对仍有效基线原子提交已验收。 | Accepted result or stale-baseline rejection / 验收结果或基线失效拒绝 |
| HE11 / 执行十一 | Archive status, plan, artifacts, verdicts and gaps; execute requested delivery with its own authority and durable idempotency. / 归档状态、计划、工件、裁决与缺口；按相应权限与持久幂等完成目标要求的交付。 | Delivery package and actual receipt / 交付包与真实回执 |

The candidate pool precedes selection; the submitted collection is exactly what reaches the composition gate. Deduplication cannot repair missing obligations or erase already duplicated work. / 候选池在选择之前，提交集合是实际送入组合闸的集合；去重不能补齐缺失责任，也不能抹掉既有重复劳动。

## Two Gates / 两道闸门

| Gate / 闸门 | Required checks / 必需检查 |
| --- | --- |
| Artifact / 工件 | Structure/types; authenticated ownership/attempt; goal/contract/input/dependency versions; source location and actual support; local checks and scenario constraints; authorization and external-effect certainty. / 结构类型、认证归属／尝试、目标／契约／输入／依赖版本、来源定位及真实支撑、局部检查与场景约束、权限与外部效果确定性。 |
| Composition / 组合 | Every required obligation at declared cardinality; exact expected keys where applicable; compatible scope/time/units/interfaces; adjudicated conflicts; global totals/budget/integration/approval constraints; faithful synthesis and current commit baseline. / 必需责任满足基数、适用时核对全部预期主键、范围／时间／单位／接口相容、冲突已裁决、全局总量／预算／集成／审批约束成立、综合忠实与提交基线有效。 |

Per-rule outcomes are `pass / 通过`, `fail / 不通过`, `unknown / 未知`, `not_applicable / 不适用`. Non-applicability needs a scenario basis or authorized exemption. Required checks must all pass; averages cannot offset failure or unknown critical evidence. A waiver first creates an authorized rule/goal version, then revalidation. / 逐项结果分为四态，不适用须有场景依据或授权豁免。必需检查全部通过，均分不能抵消失败或关键未知。豁免应先产生授权规则／目标版本，再重验。

A matching responsibility label, parseable object or accessible link is insufficient semantic evidence. Unreadable sources, unavailable authorization proofs and unexecuted required rules produce unknown, not automatic success or automatic factual falsity. / 标签匹配、对象可解析或链接可打开均不足以证明语义正确。来源不可读、权限依据不可得、必需规则未执行时标未知，不自动通过，也不直接认定事实错误。

## Recovery and Delivery / 恢复与交付

### Independent States and Versions / 独立状态与版本

| Object / 对象 | States / 状态 |
| --- | --- |
| Parent / 父目标 | Modeling, ready, executing, accepting, repairing, awaiting evidence/approval, accepted, failed, terminated. / 待建模、待派工、执行中、验收中、修复中、待补充／审批、已验收、失败、已终止。 |
| Attempt / 尝试 | Pending, running, returned, failed, timed out, cancel requested, canceled, outcome unknown. / 待启动、执行中、已返回、失败、超时、取消请求中、已取消、结果待核对。 |
| Artifact / 工件 | Pending acceptance, accepted, awaiting evidence, rejected, quarantined, superseded. / 待验收、已通过、待补证、未通过、已隔离、已被替代。 |

Return does not imply artifact acceptance, and artifact acceptance does not imply parent acceptance. Cancel requested does not prove the external executor stopped. / 返回不代表工件通过，工件通过不代表父目标通过；请求取消不证明外部执行已停止。

Scope/required-rule changes create a new goal baseline; worker/schedule/mapping changes create a new plan; retries create new attempts; artifact/acceptance-evidence changes create new artifact versions and affected gate verdicts. Pure observation repair creates observation records only. Cross-version reuse requires explicit compatibility proof, current dependency checks and reacceptance. / 范围／必需规则变更产生新目标基线，执行者／调度／映射变更产生新计划，重试产生新尝试，工件／验收证据变更产生新工件及受影响裁决；纯观测修复只产生观测记录。跨版本复用须有明确兼容证明、当前依赖核验与重新接纳。

### Failure Routing and Cumulative Limits / 失败路由与累计限制

Recoverable associations/events go to observation repair; missing acceptance evidence requires lawful supplementation and revalidation; unperformed or incorrect work returns to local execution; global conflict needs an accountable adjudication; permission gaps return to the authority workflow. A timeout with possible external effects requires receipt/idempotency reconciliation before retry. / 可恢复关联／事件进入观测修复，缺验收证据须合法补证并重验，未做或错误工作回局部执行，全局冲突交有责任人的裁决，权限不足回授权流程；外部超时且可能已生效时，重试前必须核对回执与幂等。

Confirmed spend plus outstanding reservations cannot exceed the approved parent limit; unresolved calls keep their reservations. Maximum attempts includes the first attempt. Preserve parent and responsibility cumulative use across retries and plan upgrades, including coordinator, acceptance and supplementation. Units remain separate: calls, tokens, currency and time cannot be added together. At deadline/limit, stop new work, request cancellation and archive partial results and unresolved outcomes. / 已确认消耗加在途预留不得超过父级批准额度，结果不明调用保留预留。最大尝试数包含首次；跨重试与计划升级保留父级和责任累计消耗，包括主管、验收与补全。调用、词元、货币、时间不能混加。达到截止／额度后停止新增工作、请求取消并归档部分产物与未明结果。

Adapters expose submit, status, artifact fetch and cancellation, or explicitly report unsupported capabilities. Replacement rechecks identity, callback authentication, authority, isolation, accounting, duplicate delivery, storage and effect/cancel semantics. Recover from durable goal/plan/attempt/gate state, reconcile in-flight work first and retain valid artifacts. A replacement owner needs a recorded handoff and a single valid writer. Shared writes require isolated workspaces, versioned merging and global checks. / 适配器提供提交、查询、取工件与取消，缺失能力须明示。替换执行者时重核身份、回调认证、授权、隔离、计量、重投、存储与效果／取消语义。恢复读取持久目标／计划／尝试／裁决，先核对在途并保留有效工件；替换主管须记录交接并保持单一有效写入者。共享写入须有隔离工作区、版本化合并与全局检查。

### Scenario Configuration / 场景配置

Research uses confirmed topics and supported conclusions; batches use frozen input keys; code uses scoped changes plus local/integration tests; incident review uses comparable clocks and separate hypotheses; sensitive processing uses authoritative grants and actual receipts. Exactly once per input key differs from two independent reviews per obligation. / 研究按确认主题与证据结论，批次按冻结主键，代码按范围变更与局部／集成测试，事故复盘按可比时钟并区分假设，敏感处理按权威授权与真实回执。每主键恰好一次不同于每责任两份独立复核。

Minimal start example, with illustrative limits only / 最小启动示例，额度仅示例：

```yaml
mode: standalone_execution  # 独立执行
goal: {id: brief, version: 1, owner: coordinator, input_refs: [authorized_snapshot]}
required_responsibilities: [organization_topology, state_management, cross_boundary_handoff]
cardinality: {accepted_per_responsibility: 1, allowed_candidates: 1}
artifact_required_fields: [responsibility_id, conclusion, source_ref, source_location, input_digest]
limits: {unit: calls, parent_total: 30, per_responsibility_total: 8, coordinator_and_acceptance: 6, max_attempts: 2, max_concurrency: 3, max_depth: 1, deadline_seconds: 300}
authority: {tools: authorized_read_adapters, external_publish: false}
probe: {enabled: false}
```

Expand into actual versioned contracts, references, validators and host permissions before dispatch. The probe is optional; both gates and critical runtime records remain mandatory. Final delivery includes state, baseline, plan, artifact/gate references, work/evidence gaps, reuse eligibility, resource/version summary, deliverable reference and next-action authority. Accepted content does not imply publication. An external action included in the goal must itself be a required obligation with an accepted real receipt before parent completion. / 派工前扩成真实版本化契约、引用、验收器与宿主权限。探针可选，两闸与关键运行记录仍必需。最终包包含状态、基线、计划、工件／裁决引用、工作／证据缺口、可复用性、资源／版本摘要、交付引用与后续权限。内容通过不代表已发布；目标包含的外部动作须纳入必需责任并验收真实回执后，父目标才能完成。

## Shared Interaction Contract / 共享交互契约

This generated block is identical in the execution and probe files so either can be read independently. / 以下生成区块在执行与探针文件中相同，使两份规格均可独立阅读。

<!-- hierarchy:contract:start -->
Name / 名称: Hierarchy execution–probe exchange / 层级执行与探针交换。
Description / 描述: A design-level field mapping of the shared source contract `0.1.0`, embedded in both mode documents. It is not the shared module's `3.0.0` runtime Schema. / 来源共享契约 `0.1.0` 的设计层字段映射，内置于两份模式文档；不是通用模块 `3.0.0` 运行时 Schema。

### Contract Navigation / 契约导航

- [Ownership / 对象归属](#ownership-and-usage--对象归属与用法)
- [Messages / 消息](#message-envelope--消息信封)
- [Events / 事件](#minimum-event-envelope--最小事件信封)
- [Adoption / 采纳](#adoption-workflow-and-constraints--采纳流程与约束)
- [Termination / 终止](#timeout-and-closed-loop-termination--超时与闭环终止)

## Ownership and Usage / 对象归属与用法

| Authority / 权威维护方 | Objects / 对象 | Other party / 另一方 |
| --- | --- | --- |
| Execution and authorized writers / 执行及授权写入组件 | Goal, responsibilities, plan, business state, formal artifacts and gate verdicts. / 目标、责任、计划、业务状态、正式工件与闸门裁决。 | Probe reads only. / 探针只读。 |
| Runtime and resource services / 运行时与资源服务 | Identity, live grants, reservations/settlement and cancellation/recovery credentials. / 身份、实时授权、预留／结算及取消／恢复凭据。 | Both read within granted scope. / 双方按授权读取。 |
| Probe / 探针 | Observation extensions, metrics, evidence gaps and supplementation proposals. / 观测扩展、指标、证据缺口与补全提案。 | Execution validates before use/adoption. / 执行先校验再引用或采纳。 |
| Execution / 执行流程 | Adoption receipts, new object versions and revalidation results. / 采纳回执、新对象版本与重验结果。 | Probe reconciles before closing gaps. / 探针核对后再关闭缺口。 |

Business write ownership never lets a model bypass runtime controls. Observation authority never grants business verdict authority. / 业务写入权不允许模型绕过运行时控制，观测权也不授予业务裁决权。

## Message Envelope / 消息信封

English keys below map to the source's Chinese fields; null means unknown/not relevant with an explicit reason in the report, not permission to guess. Event/message-specific applicability determines required fields. / 以下英文键映射来源中文字段；空值代表未知或不相关，报告中须有理由，不允许猜填；必填性按消息／事件类型确定。

```yaml
protocol_version: "0.1.0"  # 契约版本：通信协议
message_id: required       # 消息编号：唯一，重投复用
message_type: observation_request  # 消息类型
sender: execution          # 发送方
run_id: required           # 运行编号
parent_goal_id: required   # 父目标编号
goal_version: null        # 目标版本
plan_version: null        # 计划版本
baseline_snapshot_id: null # 基线快照编号
baseline_state_revision: null # 基线状态修订号
responsibility_id: null   # 责任编号
task_id: null             # 任务编号
task_contract_version: null # 契约版本号：业务任务契约
attempt_id: null          # 尝试编号
correlation_request_id: null # 关联请求编号
created_at: required      # 产生时间：带时区
deadline_at: required     # 截止时间：带时区
payload: {}               # 数据体：见下表
```

Protocol version and task-contract version are different fields. Goal/plan versions describe business scope; state revision describes progress under that scope. Sender strings and hashes do not authenticate anyone; the host must verify credentials and current write authority. / 通信协议版本与任务契约版本不同；目标／计划版本描述业务口径，状态修订描述同一口径的进度。发送方字符串与哈希不能认证身份，须由宿主核验凭据及当前写入权。

| Type / 类型 | Direction / 方向 | Minimum payload / 最小数据体 |
| --- | --- | --- |
| `observation_request` / 观测请求 | Execution → probe / 执行→探针 | Scope, requested fields, rule version, read-grant reference, budget, blocking flag and business basis. / 范围、需补字段、规则版本、读取授权引用、预算、是否阻断及业务依据。 |
| `observation_snapshot` / 观测快照 | Execution → probe / 执行→探针 | Goal/responsibility snapshots, artifact manifest, gate records, event range and completeness declaration. / 目标／责任快照、工件清单、闸门记录、事件区间与完整性声明。 |
| `observation_report` / 观测报告 | Probe → execution / 探针→执行 | Metric values and definitions, evidence, unknowns, gaps, recommendations and report version. / 指标值与口径、证据、未知、缺口、建议与报告版本。 |
| `supplement_proposal` / 补全提案 | Probe → execution / 探针→执行 | Patch ID, target object/version, field path, baseline-value digest, proposed value, evidence, expiry and affected scope. / 补丁编号、目标对象／版本、字段路径、基线值指纹、建议值、证据、有效期与影响范围。 |
| `adoption_receipt` / 采纳回执 | Execution → probe / 执行→探针 | Patch ID, per-field disposition/reason, actual new object version, affected gates and revalidation references. / 补丁编号、逐字段状态／原因、实际新对象版本、受影响闸门与重验引用。 |

No message directly authorizes business mutation. Only execution's authorized adoption may change a business object. Dispositions are `adopted / 已采纳`, `partially_adopted / 部分采纳`, `rejected / 已拒绝`, `expired / 已过期`, `superseded / 已被替代`. Partial adoption records each field separately. Required revalidation still pending must be stated and cannot close a critical gap. / 消息本身不授权业务变更；只有执行侧授权采纳后才可改变业务对象。采纳状态限定为上述五种，部分采纳须逐字段记录。必需重验未完成时须明示，不得关闭关键缺口。

## Minimum Event Envelope / 最小事件信封

```yaml
event_id: required          # 事件编号
event_type: artifact_gate_decided # 事件类型
run_id: required            # 运行编号
parent_goal_id: required    # 父目标编号
goal_version: null         # 目标版本
plan_version: null         # 计划版本
responsibility_id: null    # 责任编号
task_id: null              # 任务编号
task_contract_version: null # 契约版本号
attempt_id: null           # 尝试编号
executor_instance_id: null # 执行者实例编号
producer_id: required      # 生产者编号
producer_sequence: null    # 生产者序号
occurred_at: null          # 发生时间
received_at: required      # 接收时间
object_ref: null           # 对象引用
object_version: null       # 对象版本
object_digest: null        # 对象指纹：运行时计算
causal_event_id: null      # 因果事件编号
source_category: runtime_record # 来源类别
payload_ref: required      # 负载引用
```

Deduplicate events by `(run_id, event_id)`; isolate divergent payloads under the same ID. Deduplicate messages by unique message ID, preserving the original ID on retry. Repeated delivery is not a new attempt. Producer sequence orders only that producer, never global time; events without child tasks need no invented task/attempt IDs. / 事件按运行编号＋事件编号去重，同编号异载荷隔离；消息按唯一编号去重，重投保留原编号。重复投递不是新尝试。生产者序号只表示本生产者顺序，不是全局时间；无子任务事件不造任务／尝试编号。

## Adoption Workflow and Constraints / 采纳流程与约束

Authenticate sender and authority → deduplicate → check goal/plan versions → check target digest and expiry → enforce field allowlist → verify evidence → classify impact → create a new record/artifact version → rerun affected gates → issue receipt. / 认证发送方与权限→去重→核验目标／计划版本→核验对象指纹与有效期→执行字段白名单→复核证据→判断影响→生成新记录／工件版本→重跑受影响闸门→返回回执。

Unrelated state changes need not invalidate a whole report, but every proposal dependency must remain valid. Changes to goals, task contracts, evidence objects or gate rules require rebasing and recomputation. / 无关状态变化不必废弃整个报告，但须核验提案每项依赖；目标、任务契约、证据对象或闸门规则变更须重建基线并重算。

| Impact / 影响 | Lawful handling / 合法处理 |
| --- | --- |
| Observation timing, associations or derived statistics / 观测时间、关联、派生统计 | Write provenance-bearing observation extensions and retain original events; no business recheck unless used as acceptance evidence. / 写带来源观测扩展并保留原事件；未成为验收依据时无需业务重验。 |
| Formal artifact sources, input mapping or acceptance data / 正式工件来源、输入映射、验收数据 | Authorized writer creates a new artifact version; rerun artifact gate and affected composition gate. / 授权组件生成新工件版本，重跑工件闸及受影响组合闸。 |
| Responsibility, acceptance criteria, authority or budgets / 责任、验收条件、权限、预算 | Submit to original governance workflow for approval and versioning; probe cannot apply. / 交原治理流程批准并版本化，探针不能实施。 |
| Unperformed business responsibility / 业务责任未完成 | Return a business gap/local reassignment recommendation to execution; never manufacture completion. / 返回业务缺口／局部重派建议，不能伪造完成。 |

Probes cannot rewrite parent completion, official verdicts, settled costs, raw event timestamps, business facts or authorization scope. Record fact-valid time, source version, read time and supplementation time separately; newly acquired evidence cannot prove historical possession. / 探针不能改写父目标完成、正式裁决、已结算费用、原始事件时间、业务事实或授权范围。分别记录事实适用时间、来源版本、读取时间与补全时间；新取得证据不能证明历史上已持有。

## Timeout and Closed-Loop Termination / 超时与闭环终止

Noncritical observation timeouts do not block execution; missing required business evidence remains pending or escalates, even with a probe offline. Execution may use its own lawful evidence channels. / 非关键观测超时不阻断执行；必需业务证据缺失时保持待补充或升级，即使探针离线也一样；执行侧可使用自身合法取证渠道。

Deduplicate a gap by `(run_id, goal_version, plan_version, object_id, field_path, rule_version)`, with at most one request in flight. Bound retries, sources, reads, elapsed time and cumulative use; report generation, metric refresh and log repair do not trigger another identical observation. Only new business events, arriving evidence or an explicit recheck can begin a new round. / 缺口按运行、目标版本、计划版本、对象、字段路径、规则版本去重，最多一个请求在途；限制重试、来源、读取、耗时与累计消耗。报告、指标刷新、日志补写不触发同类观测；只有新业务事件、证据到达或明确复核才能开启新轮次。

Sending, adopting and resolving are separate states. Close critical gaps only after evidence is restored and necessary revalidation passes. Exhausted budget, rejection, termination, goal upgrade or unrecoverable evidence ends the round with an explicit reason and unresolved gaps retained. Cancel obsolete requests on goal cancellation/upgrade; do not pretend unconfirmed external reads have stopped, and never write their stale results into a new business version. / 发送、采纳、解决分别记录。证据补齐且必需重验通过后才可关闭关键缺口；预算耗尽、拒绝、终止、目标升级或不可恢复证据，以明确原因结束本轮并保留未解决项。目标取消／升级时取消旧请求，未确认的外部读取不能假装已停止，陈旧结果不得写入新业务版本。
<!-- hierarchy:contract:end -->

## Acceptance Cases / 验收用例

These are source-required outcomes; host integration remains pending. Documentation verification is not business execution evidence. / 以下为来源要求的预期结果，宿主集成待实现；文档校验不是业务执行证据。

<!-- hierarchy:execution_cases:start -->
| ID / 编号 | Scenario and expected behavior / 场景与预期行为 | Source scenario / 来源场景 | Required outcome / 必需结果 |
| --- | --- | --- | --- |
| HET01 / 执行验收一 | Three acceptable artifacts cover one obligation: reject composition; retain two missing obligations and excess candidates. | 三张合格工件实际都对应同一必需责任 | 不能通过组合闸；保留另外两项责任缺口及重复候选记录 |
| HET02 / 执行验收二 | Three distinct obligations each have valid artifacts and all rules pass: allow parent acceptance submission. | 三项不同必需责任各有一份有效工件，全部约束通过 | 允许提交父目标已验收 |
| HET03 / 执行验收三 | Labels are complete but a source does not support its conclusion: artifact fails or is unknown and does not count as fulfilled. | 三项责任名齐全，但一项来源无法支撑结论 | 对应工件不通过或未知，不能被计为已履约 |
| HET04 / 执行验收四 | Old-goal artifact: quarantine or explicitly prove compatibility and revalidate for current acceptance. | 工件属于旧目标版本 | 隔离，或经明确兼容性证明及重验后生成当前接纳记录 |
| HET05 / 执行验收五 | Repeated message: register once without increasing candidates or consumption counts. | 同一消息重复投递 | 只登记一次，不增加候选数或消耗计数 |
| HET06 / 执行验收六 | Replace executor after failure: preserve the responsibility denominator and cumulative budget. | 同一责任失败后换人重试 | 不增加父目标责任数量，累计预算不清零 |
| HET07 / 执行验收七 | One timeout with other passed obligations: repair only that obligation and retain valid artifacts. | 某项超时，其他项已通过 | 只修复该项；其他工件在版本仍有效时保留 |
| HET08 / 执行验收八 | All calls returned but composition is unknown: parent cannot be accepted. | 所有子调用都已返回，但组合闸未知 | 父目标不能已验收 |
| HET09 / 执行验收九 | Two independent reviewers are required: apply declared cardinality; lawful review is not duplication. | 任务要求双人独立复核 | 按已声明基数验收，不把合法复核误判为重复 |
| HET10 / 执行验收十 | Probe supplements a source field: create a new artifact version and rerun both affected gates. | 探针补充来源字段 | 新工件版本，重跑两道受影响闸门 |
| HET11 / 执行验收十一 | Proposal changes permissions/completion: reject with reason; explanations cannot replace authorization. | 探针提案试图修改权限或完成状态 | 拒绝写入，留下原因，不以模型解释替代权限检查 |
| HET12 / 执行验收十二 | Goal upgraded after composition passed: old submission fails baseline comparison and cannot overwrite new state. | 组合闸通过后目标升级，旧裁决尝试提交 | 比较基线失败，不能覆盖新状态 |
| HET13 / 执行验收十三 | External timeout may have written: keep outcome unknown and reconcile before retry. | 外部执行超时，可能已经写入 | 保持结果待核对，未确认前禁止盲目重试 |
| HET14 / 执行验收十四 | Probe down but local evidence complete: normal acceptance continues with observation gaps disclosed. | 探针停机但本地验收证据齐全 | 不影响正常验收；标记可观测性缺口 |
| HET15 / 执行验收十五 | Parent restarts: recover durable state without repeating confirmed external effects. | 父责任人重启后恢复 | 从持久化状态继续，不重复已确认的外部动作 |
| HET16 / 执行验收十六 | Enumerated topics finish but completeness unconfirmed: report confirmed-scope completion only. | 所有已枚举研究主题完成，但清单完备性未获确认 | 仅报告已确认范围完成，不声称开放问题已穷尽 |
<!-- hierarchy:execution_cases:end -->

Observability Metrics File / 可观测性指标文件: [collaboration-hierarchy-observability.md](collaboration-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
