# Complexity-Based Routing / 复杂度路由

Pattern ID / 模式 ID: `PATTERN_0032`

Design revision / 设计修订: `0.4.0`

Status / 状态: Active / 活跃

Cell / 交织点: reasoning-routing / 推理 x 路由
Capability / 能力: Reasoning / 推理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

Runtime Protocols / 运行协议: [Reasoning Execution Flow / 推理执行流程](../../reasoning-execution-flow.md); [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md).

## Quick Navigation / 快速导航

- [Design Pattern / 设计模式](#design-pattern--设计模式)
- [Position And Boundary / 定位与边界](#position-and-boundary--定位与边界)
- [Design Invariants / 设计不变量](#design-invariants--设计不变量)
- [Two-Level Routing Architecture / 两级路由架构](#two-level-routing-architecture--两级路由架构)
- [Task-Atom And Signal Contract / 任务原子与信号契约](#task-atom-and-signal-contract--任务原子与信号契约)
- [Deterministic Policy / 确定性策略](#deterministic-policy--确定性策略)
- [Decision Contract / 决策契约](#decision-contract--决策契约)
- [Lifecycle And Switching / 生命周期与换路](#lifecycle-and-switching--生命周期与换路)
- [Run-Graph Compilation / 运行图编译](#run-graph-compilation--运行图编译)
- [Failure Handling / 失败处理](#failure-handling--失败处理)
- [Implementation Boundary / 实现边界](#implementation-boundary--实现边界)
- [Acceptance / 验收](#acceptance--验收)

## Design Pattern / 设计模式

Complexity-Based Routing places a classifier in front of reasoning so each request receives the cheapest reasoning depth that can still solve it. / 复杂度路由在推理前放置一个分类器，让每个请求获得能解决它的最便宜推理深度。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reasoning / 推理 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Reasoning / 推理 x Routing / 路由 in arXiv:2605.13850. / 代表性定义 / Representative definition；来源表将 Reasoning / 推理 x Routing / 路由 映射到该单元。
- 问题 / Problem: Tasks vary widely in difficulty, so treating every request with the same reasoning depth wastes cost or under-solves hard cases. / 任务难度差异很大，对所有请求使用同样推理深度会浪费成本或低估困难案例。
- 架构方案 / Architectural Solution: Classify complexity first, then route simple cases to lightweight reasoning and hard cases to deeper planning, search, or review. / 先判断复杂度，再将简单案例路由到轻量推理，将困难案例路由到更深规划、搜索或评审。
- 工程权衡 / Engineering Trade-offs: Balances cost and capability, but misclassification can under-resource hard tasks or over-process simple ones; the article quantifies misrouting cost at roughly $18,850 per day at 100K queries. / 平衡成本与能力，但误分类会让难任务资源不足或让简单任务过度处理；论文将误路由成本量化为约每天 $18,850（10 万请求规模）。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when problem complexity should determine the reasoning path. / 当问题复杂度应决定推理路径时使用。

### Reasoning Tier Model / 推理档位模型

The article grounds the tiers in dual-process theory (Kahneman) and cites RouteLLM reaching about 85% cost reduction with quality retained. / 论文以双过程理论（Kahneman）为依据划分档位，并引用 RouteLLM 在保持质量下降本约 85%。

| Tier / 档位 | Budget Anchor / 预算锚点 | Fit / 适用 | Exit / 退出 |
| --- | --- | --- | --- |
| System 1 / 直觉档 | ~500 tokens | Lookup, classification, template answers, repeat questions. / 查表、分类、模板回答、重复问题。 | A versioned deterministic rule or configured low-risk direct-release check passes; confidence alone never releases. / 版本化确定性规则或已配置低风险直接放行检查通过；不得仅凭置信度放行。 |
| System 2 / 深思档 | ~8K tokens | Multi-step reasoning, cross-file synthesis, non-trivial debugging. / 多步推理、跨文件综合、非平凡调试。 | Reasoning chain closes all subgoals. / 推理链关闭全部子目标。 |
| Extended Deliberation / 扩展深思档 | ~64K tokens | Architecture decisions, incident root cause, adversarial cases. / 架构决策、事故根因、对抗性案例。 | Requires explicit review or evaluation gate. / 需要显式评审或评估闸门。 |

Routing rules / 路由规则:

- Treat the article token figures as comparative source anchors, not runtime limits. The versioned reasoning contract and scene-owned budget profile are authoritative for execution. / 将论文中的 token 数视为来源比较锚点，而不是运行上限；执行时以版本化推理契约和场景预算档位为准。
- Classify before reasoning starts; never let the default path be the deepest tier. / 在推理开始前分类；不得默认走最深档位。
- Route on observable complexity signals: input length, entity count, dependency depth, ambiguity flags, historical failure on similar requests. / 依据可观测复杂度信号路由：输入长度、实体数量、依赖深度、歧义标记、同类请求历史失败率。
- Apply governance hard gates before scoring complexity. Include evidence state, mechanism uncertainty, action risk, and whether new information requires environment interaction. / 在复杂度评分前先执行治理硬门槛；信号还应包含证据状态、机制不确定性、动作风险，以及是否必须与环境交互才能获得新信息。
- The router consumes typed observable uncertainty, evidence, permission, reversibility, and risk signals—not model self-confidence. An upstream adapter may translate a low-confidence report into an explicit `unknown` or high-uncertainty signal for escalation; it must discard high confidence as a release signal. Escalate when verification fails, required signals are unknown, or the same request bounces back, and record every escalation. / 路由器消费类型化的可观测不确定性、证据、权限、可逆性和风险信号，而不是模型自报置信度。上游适配器可以把低置信报告转换为显式 `unknown` 或高不确定性信号用于升级，但必须丢弃将高置信作为放行信号的做法。验证失败、必需信号未知或同一请求被退回时应升级，并记录每次升级。
- De-escalate within a run only after critical uncertainty is resolved and the remaining work is deterministic or low-risk; record the old mode, new mode, triggering evidence, budget impact, and unfinished work. / 只有关键不确定性已解决且剩余工作为确定性或低风险时，才允许在单次运行内降档；记录原模式、新模式、触发证据、预算影响和未完成工作。
- Misroute review: sample routed-low cases and audit whether they should have escalated. / 误路由审查：抽样低档案例，审计其是否本应升级。

### Shared Execution Contract / 共享执行契约

Use `PATTERN_0051` to normalize the task, establish task/run/step identities, create the versioned reasoning contract, choose `direct`, `chain`, `parallel`, or `iterative`, and require validators and stop reasons before completion. The routing cell owns the choice and switch record; it does not own downstream business truth. / 使用 `PATTERN_0051` 标准化任务，建立任务/运行/步骤标识，创建版本化推理契约，选择直接、链式、并行或迭代模式，并在完成前强制验证器和停止原因。路由单元负责选择与换路记录，不负责下游业务事实。

Do not infer a designed route from observed topology. When no explicit router event exists, label the result `observed_mode` and leave `route_reason` missing. / 不得根据观测拓扑反推设计路由；没有显式路由事件时，将结果标记为 `observed_mode`，并保留 `route_reason` 为缺失。

## Engineering Design / 工程设计

### Position And Boundary / 定位与边界

Complexity-Based Routing classifies each independently closable task atom and selects the least expensive reasoning configuration that can still satisfy evidence, validation, risk, and governance requirements. Cost never overrides a hard gate. / 复杂度路由对每个可独立闭环的任务原子进行分类，并选择仍能满足证据、验证、风险和治理要求的最低成本推理配置。成本绝不能覆盖硬门槛。

Routing, reasoning, action, and observation remain separate responsibilities. / 路由、推理、行动与观测保持职责分离。

| Responsibility / 职责 | Owns / 负责 | Must not own / 不得负责 |
| --- | --- | --- |
| Workflow route coordinator / 流程路由协调器 | Task-atom scope, execution lane, mechanical readiness, action boundary, human gate, and blockers. / 任务原子范围、执行车道、机械状态、行动边界、人工闸门和阻塞项。 | Private reasoning or business truth. / 私密推理或业务事实。 |
| Reasoning subrouter / 推理子路由器 | `reasoning_depth`, `execution_mode`, primary/supporting topologies, typed reasons, and abstention. / 推理深度、执行模式、主/支撑拓扑、类型化原因和弃权。 | Write permission, approval, target-object confirmation, or final business action. / 写权限、审批、目标对象确认或最终业务动作。 |
| Mode executor / 模式执行器 | Execute the selected direct, chain, parallel, or iterative contract. / 执行所选直接、链式、并行或迭代契约。 | Silently change route, authority, or budget. / 静默修改路由、权限或预算。 |
| Governance and action / 治理与行动 | Policy, permission, risk, idempotency, confirmation, compensation, and protected transitions. / 策略、权限、风险、幂等、确认、补偿和受保护转换。 | Treat a reasoning decision as action authorization. / 把推理决定当作行动授权。 |
| Probe suite / 探针套件 | Observe, complete traceable fields, alert, advise, or enforce an explicitly authorized observation gate. / 观测、可追踪补全、告警、建议或执行显式授权的观测闸门。 | Replace the router, approve high-risk action, or invent missing facts. / 替代路由器、批准高风险动作或编造缺失事实。 |

[`reasoning_router.py`](../../../runtime/reasoning_router.py) is the deterministic reasoning subrouter, not a general workflow authorization engine. `disposition: execute` permits establishment of a reasoning contract only after upstream workflow and governance gates pass; it never authorizes a side effect. / [`reasoning_router.py`](../../../runtime/reasoning_router.py) 是确定性推理子路由器，不是通用流程授权引擎。`disposition: execute` 只表示上游流程与治理门通过后可以建立推理契约，绝不授权副作用。

### Design Invariants / 设计不变量

1. Route one task atom at a time. Split judgment, write action, and reporting when their permissions or stop conditions differ. / 每次只路由一个任务原子；当判断、写动作和报告的权限或停止条件不同时先拆分。
2. Apply governance denial, permission, irreversibility, evidence, and mechanical-state gates before cost or complexity optimization. / 在成本或复杂度优化前执行治理拒绝、权限、不可逆性、证据和机械状态门槛。
3. Evidence shortage is a collection, clarification, waiting, or escalation problem—not a reason to spend more reasoning tokens. / 证据不足属于补证、澄清、等待或升级问题，不是增加推理 token 的理由。
4. Use externally observable typed signals with explicit `observed | missing | unknown | not_applicable` states and field-level provenance. / 使用外部可观测类型化信号，并显式区分已观测、缺失、未知和不适用状态及字段级来源。
5. Model confidence is advisory telemetry only. High confidence never releases work; low confidence may only become a missing/unknown or high-uncertainty signal through a versioned adapter. / 模型置信度仅为建议性遥测。高置信不得放行；低置信只能通过版本化适配器转换为缺失、未知或高不确定性信号。
6. Every decision binds policy identity/version/hash, signal fingerprint, reason codes, selected configuration, budget profile, blockers, and abstention. / 每个决定绑定策略标识/版本/哈希、信号指纹、原因码、所选配置、预算档位、阻塞项和弃权状态。
7. Missing required signals fail closed into abstention or a configured safer route; they never inherit a low-risk default. / 必需信号缺失时默认阻断为弃权或进入已配置的更安全路径，绝不继承低风险默认值。
8. Every switch creates a new route revision and event; execution cannot mutate the original decision in place. / 每次换路创建新的路由修订和事件；执行不得原地修改原始决定。
9. Completion depends on contractual validators and release-bound evidence, not route selection, explanation length, or model confidence. / 完成取决于契约验证器与放行绑定证据，而非路由选择、解释长度或模型置信度。
10. Record externally verifiable summaries and fingerprints only; never capture private chain-of-thought. / 只记录外部可核验摘要与指纹，不采集私密思维过程。

### Two-Level Routing Architecture / 两级路由架构

```text
request / 请求
  -> normalize and freeze versions / 标准化并冻结版本
  -> split task atoms and dependencies / 拆分任务原子与依赖
  -> workflow route / 流程路由
       execution lane + mechanical state + action risk + human gate
       执行车道 + 机械状态 + 动作风险 + 人工闸门
  -> reasoning subroute / 推理子路由
       depth + execution mode + topology + reason codes
       深度 + 执行模式 + 拓扑 + 原因码
  -> bind scene-owned budget and validators / 绑定场景预算与验证器
  -> compile immutable run graph / 编译不可变运行图
  -> execute, observe, validate, and switch if authorized / 执行、观测、验证并在授权时换路
  -> aggregate atom results and close / 聚合原子结果并关闭
```

The workflow route selects one execution lane: `direct_answer`, `read_only_analysis`, `structured_judgment`, `planned_execution`, or `clarification_human_review`. It also carries task intent, action-risk class, mechanical readiness, human-gate placement, blockers, and whether action is allowed. The lane defines a business boundary, not a thinking shape. / 流程路由选择 `direct_answer`、`read_only_analysis`、`structured_judgment`、`planned_execution` 或 `clarification_human_review` 之一，并携带任务意图、动作风险类别、机械状态、人工闸门位置、阻塞项和是否允许行动。车道定义业务边界，不定义思考形状。

The reasoning subroute uses separate axes. / 推理子路由使用相互分离的轴。

| Axis / 轴 | Values / 取值 | Meaning / 含义 |
| --- | --- | --- |
| `reasoning_depth` | `direct | deliberative` | Governed reasoning depth, separate from topology. / 受治理推理深度，与拓扑分离。 |
| `execution_mode` | `direct | chain | parallel | iterative` | Runtime reasoning strategy. / 运行时推理策略。 |
| `primary_topology` | `null | chain | parallel | loop` | Dominant matrix topology; direct has no extra topology. / 主导矩阵拓扑；直接处理没有额外拓扑。 |
| `supporting_topologies` | `orchestration`, optionally `hierarchy` | Coordination and authority propagation, never forced into the primary mode. / 协调与权限传播，不强塞进主模式。 |

Composite work keeps a `mode_stack`, for example route -> parallel candidates -> per-candidate iterative evidence collection -> chain synthesis. Every frame has its own scope, budget allocation, entry/exit rule, and parent identity. / 组合工作保留 `mode_stack`，例如“路由 -> 并行候选 -> 候选内迭代补证 -> 链式综合”。每一帧都有自己的范围、预算分配、进入/退出规则和父标识。

### Task-Atom And Signal Contract / 任务原子与信号契约

Before routing, each atom has a stable `task_atom_id`, one primary intent, declared input/output, dependency edges, risk owner, and frozen policy snapshot. An atom mixing read-only judgment with a write action must be split. / 路由前，每个原子具有稳定 `task_atom_id`、一个主要意图、声明的输入/输出、依赖边、风险负责人和冻结的策略快照。混合只读判断与写动作的原子必须拆分。

| Signal family / 信号族 | Examples / 示例 | Missing behavior / 缺失处理 |
| --- | --- | --- |
| Task intent / 任务意图 | Query, read-only analysis, judgment, draft, business action. / 查询、只读分析、判断、草稿、业务动作。 | Unknown -> clarification or human review. / 未知 -> 澄清或人工审核。 |
| Evidence state / 证据状态 | Complete-consistent, mostly complete, conflicting, insufficient, unavailable, untrusted. / 完整一致、基本完整、冲突、不足、不可得、不可信。 | Critical insufficiency -> complement evidence, wait, or escalate. / 关键证据不足 -> 补证、等待或升级。 |
| Mechanical state / 机械状态 | Object identity, tenant, version, batch, permission, idempotency readiness. / 对象标识、租户、版本、批次、权限、幂等就绪。 | Unknown for a write atom -> block action. / 写原子未知 -> 阻断行动。 |
| Action risk / 动作风险 | Read-only, draft, reversible write, sensitive write, irreversible external action. / 只读、草稿、可回滚写入、敏感写入、不可逆外部动作。 | Unknown -> fail closed. / 未知 -> 默认阻断。 |
| Observable complexity / 可观测复杂度 | Goal/entity count, dependency depth, ambiguity, audited historical failure. / 目标/实体数、依赖深度、歧义、经审计历史失败。 | Missing required feature -> abstain; no score imputation. / 必需特征缺失 -> 弃权，不填充评分。 |
| Reasoning structure / 推理结构 | Environment interaction, material rivals, dominant dependency path. / 环境交互、实质竞争解释、主导依赖路径。 | Unknown -> safer configured route or escalation. / 未知 -> 更安全配置路径或升级。 |
| Governance / 治理 | Permission, prohibited action, reversibility, strong validation, accountable owner. / 权限、禁止动作、可逆性、强验证、责任人。 | Missing critical gate -> reject or escalate. / 关键门槛缺失 -> 拒绝或升级。 |

Every signal binds source/version, valid/capture time, method, and integrity or content hash. A versioned adapter may derive current Reasoning Contract Schema signals from richer Harness workflow fields, but it must retain original values and provenance in the workflow route envelope. / 每个信号绑定来源/版本、有效/采集时间、方法及完整性或内容哈希。版本化适配器可以从更丰富的 Harness 流程字段派生当前推理契约 Schema 信号，但必须在流程路由信封中保留原值与来源。

The supplied Harness v0.1 specifications include route confidence and completion confidence. In this project those values are observational metadata only. They may support calibration research after trustworthy outcomes exist, but are excluded from release, permission, evidence-sufficiency, and direct-route predicates. / 输入的 Harness v0.1 规范包含路由置信度与补全置信度。在本项目中，这些值只属于观测元数据；只有存在可信后验后才能用于校准研究，并且不得进入放行、权限、证据充分性或直接路径谓词。

### Deterministic Policy / 确定性策略

Each scene owns a versioned policy with an ordered rule manifest. First-match semantics are deterministic. A change that alters precedence or outcome requires a new semantic version and regression fixtures. / 每个场景拥有带顺序规则清单的版本化策略。首个命中规则决定结果；改变优先级或结果的变更必须升级语义版本并提供回归样例。

| Priority / 优先级 | Condition / 条件 | Disposition or mode / 处置或模式 | Reason / 原因 |
| --- | --- | --- | --- |
| P0 | Invalid identity, missing policy version, or unresolvable policy binding. / 标识无效、策略版本缺失或策略绑定不可解析。 | Reject or escalate by scene. / 按场景拒绝或升级。 | `policy_constraint` |
| P1 | Prohibited action or permission denied. / 动作被禁止或权限拒绝。 | `reject` | `policy_constraint` |
| P2 | Any required typed signal is missing or unknown. / 任一必需类型化信号缺失或未知。 | `escalate`, `abstained: true` | `missing_route_signal` |
| P3 | High/critical or irreversible action lacks strong validation, approval, or accountable owner. / 高/极高风险或不可逆动作缺少强验证、审批或责任人。 | `escalate` | `external_validation_required` or `human_judgment_required` |
| P4 | Critical evidence is insufficient, unavailable, or untrusted. / 关键证据不足、不可得或不可信。 | Complement evidence, wait, or `escalate`; never deepen reasoning as a substitute. / 补证、等待或升级；不得以加深推理替代。 | `insufficient_evidence` |
| P5 | New evidence can appear only after authorized environment interaction. / 只有授权环境交互后才能获得新证据。 | `iterative` + `loop` | `feedback_required` |
| P6 | Material rivals exist or evidence conflicts. / 存在实质竞争解释或证据冲突。 | `parallel` + `parallel` | `independent_hypotheses` |
| P7 | Complete consistent evidence, stable deterministic rule, low risk, one-step goal. / 证据完整一致、规则稳定确定、低风险、单步目标。 | `direct`, no primary topology | `direct_low_risk_release` |
| P8 | One dominant ordered dependency path exists. / 存在一条主导有序依赖路径。 | `chain` + `chain` | `multi_step_dependency` |
| P9 | No safe route can be proven. / 无法证明任何路径安全。 | Scene-owned fail-closed fallback, normally `escalate`. / 场景拥有的默认阻断回退，通常为升级。 | `missing_route_signal` |

[`reasoning_router.py`](../../../runtime/reasoning_router.py) implements the reasoning subset. Version `1.1.0` treats `insufficient`, `unavailable`, and `untrusted` evidence as non-executable escalation states. / [`reasoning_router.py`](../../../runtime/reasoning_router.py) 实现以上优先级的推理子集。版本 `1.1.0` 将证据不足、不可得和不可信都作为不可执行升级状态。

### Tier And Budget Binding / 档位与预算绑定

| Profile / 档位 | Typical fit / 典型适用 | Runtime rule / 运行规则 |
| --- | --- | --- |
| `direct` / 直接档 | Lookup, stable classification, deterministic calculation. / 查表、稳定分类、确定性计算。 | One bounded operation plus minimal validation; no implicit topology. / 一次受限操作加最小验证；无隐式拓扑。 |
| `standard_deliberative` / 标准深思档 | Multi-step synthesis, debugging, one dominant dependency path. / 多步综合、调试、单一主依赖路径。 | Scene-owned chain/parallel/iterative budget and mandatory validators. / 场景拥有的链式/并行/迭代预算与必选验证器。 |
| `extended_deliberative` / 扩展深思档 | Architecture, incident root cause, adversarial or high-impact analysis. / 架构、事故根因、对抗或高影响分析。 | Explicit review/evaluation gate; never the default. / 显式评审/评价闸门；不得作为默认。 |

Budget is a vector over reasoning tokens, latency, model calls, tool calls, branches, iterations, retries, and cost units. Never sum heterogeneous dimensions. Reserve branch or step allocations before dispatch and settle actual use at close. / 预算是推理 token、时延、模型调用、工具调用、分支、迭代、重试和成本单位组成的向量，禁止累加异构维度。分支或步骤分派前预留预算，关闭时结算实际消耗。

### Decision Contract / 决策契约

The design uses two bound records sharing task atom, policy snapshot, signal fingerprint, and decision identity. / 本设计使用两个相互绑定的记录，二者共享任务原子、策略快照、信号指纹和决定标识。

1. `workflow_route_envelope` is the implemented Harness-level composite decision defined by [`workflow-route-envelope.schema.json`](../../../schemas/workflow-route-envelope.schema.json), produced by [`workflow_router.py`](../../../runtime/workflow_router.py), and validated by [`reasoning_artifacts.py`](../../../runtime/reasoning_artifacts.py). It remains separate from the strict Reasoning Contract Schema. / `workflow_route_envelope` 是已实现的 Harness 层复合决定，由工作流路由信封 Schema 定义、工作流协调器生成并由推理制品闸门校验；它仍与严格推理契约 Schema 分离。
2. `routing_decision` is the current normative reasoning subset in [`reasoning-contract.schema.json`](../../../schemas/reasoning-contract.schema.json), produced by `RouteDecision.to_contract_routing_decision()`. / `routing_decision` 是当前推理契约 Schema 中的规范推理子集，由 `RouteDecision.to_contract_routing_decision()` 产生。

The excerpt below shows the field grouping; the Schema is authoritative and producers emit all required task-atom, 15-signal, provenance, blocker, and binding fields. / 下列节选展示字段分组；Schema 为权威来源，生产者必须输出全部任务原子、15 项信号、来源、阻断项与绑定字段。

```yaml
schema_version: 1.0.0
decision_id: WORKFLOW_ROUTE_0123456789abcdef01234567
decision_revision: 1
route_envelope_hash: "sha256:..."
workflow_id: WORKFLOW_0001
task_id: TASK_0001
run_id: RUN_0001
scene_id: SCENE_PRODUCTION
task_atom:
  task_atom_id: ATOM_0002
  task_atom_version: 1.0.0
  primary_intent: structured_judgment
  input_binding: {id: ATOM_INPUT, version: 1.0.0, hash: "sha256:..."}
  output_contract_binding: {id: ATOM_OUTPUT, version: 1.0.0, hash: "sha256:..."}
  dependency_atom_ids: []
  risk_owner_binding: {state: observed, value: {id: RISK_OWNER, version: 1.0.0, hash: "sha256:..."}}
  includes_read_only_judgment: true
  includes_write_action: false
workflow_policy_binding: {id: WORKFLOW_ROUTE_DEFAULT, version: 1.0.0, hash: "sha256:..."}
adapter_binding: {id: WORKFLOW_TO_REASONING_SIGNAL_ADAPTER, version: 1.0.0, hash: "sha256:..."}
reasoning_policy_binding: {id: REASONING_ROUTE_DEFAULT, version: 1.1.0, hash: "sha256:..."}
workflow_signals: ["exactly 15 typed value-state records with field provenance / 恰好 15 条带字段来源的类型化状态记录"]
workflow_signal_fingerprint: "sha256:..."
execution_lane: structured_judgment
action_allowed: false
human_gate: null
blockers: []
reasoning_decision: {decision_binding: {id: REASONING_DECISION_0123456789abcdef01234567, version: 1.1.0, hash: "sha256:..."}, disposition: execute, configuration: {execution_mode: direct, reasoning_depth: direct, primary_topology: null, supporting_topologies: []}, reason_codes: [direct_low_risk_release], missing_signals: [], signal_fingerprint: "sha256:...", escalation_handoff: null}
budget_profile_binding: {id: BUDGET_STANDARD, version: 1.0.0, hash: "sha256:..."}
validator_profile_binding: {id: VALIDATOR_STANDARD, version: 1.0.0, hash: "sha256:..."}
run_graph_binding: {state: not_applicable}
abstained: false
route_confidence_telemetry: {state: not_applicable}
created_at: "2026-07-17T00:00:00Z"
```

The strict reasoning record contains decision ID, policy binding, `execute` disposition, typed signals, typed reasons, selected configuration, signal fingerprint, missing signals, and abstention. Reject and escalate decisions are emitted as `route_selected` events and terminal state; only `execute` establishes a Reasoning Contract. / 严格推理记录包含决定 ID、策略绑定、`execute` 处置、类型化信号、类型化原因、所选配置、信号指纹、缺失信号和弃权状态。拒绝与升级决定通过 `route_selected` 事件及终态记录；只有 `execute` 建立推理契约。

All hashes use the shared canonical JSON rules. The same logical decision retried with the same policy and signal fingerprint returns the same decision ID; a different result is a conflict, not an update. / 所有哈希使用共享规范 JSON 规则。同一策略与信号指纹下的同一逻辑决定重试时返回相同决定 ID；不同结果属于冲突而非更新。

### Lifecycle And Switching / 生命周期与换路

```text
unassessed / 未评估
  -> evaluating / 评估中
       -> rejected / 已拒绝
       -> abstained / 已弃权
       -> selected / 已选择
  selected -> contract_bound / 已绑定契约
  contract_bound -> active / 执行中
  active -> switch_proposed / 已提出换路
       -> switch_rejected -> active / 换路被拒后继续
       -> switched -> active / 换路成功后继续
  active -> completed | failed | timed_out | cancelled | escalated
```

A switch may be proposed when mandatory validation shows structural insufficiency; new evidence creates or resolves material rivals; environment interaction becomes necessary or finishes; an authorized goal, constraint, fact, permission, risk, object version, or tool-availability revision occurs; or a budget, no-progress, timeout, or probe-feedback boundary fires. / 出现以下情况时可以提出换路：必选验证表明结构不足；新证据产生或消除实质竞争解释；环境交互变为必需或已经完成；目标、约束、事实、权限、风险、对象版本或工具可用性经授权修订；预算、无进展、超时或探针反馈边界触发。

Every committed revision conforms to [`workflow-route-revision.schema.json`](../../../schemas/workflow-route-revision.schema.json) and binds the previous/current envelope hashes, monotonic revisions, trigger class and evidence, direction, hysteresis evidence, budget impact, unfinished work, actor/authority, and time. A reasoning topology change may additionally bind its strict `mode_switched` event; a `gate_only` revision binds run-graph or gate state without pretending the reasoning route changed. / 每个已提交修订都符合工作流路由修订 Schema，并绑定前后信封哈希、单调修订号、触发类别与证据、方向、迟滞证据、预算影响、未完成工作、执行者/权限及时间。推理拓扑变化还可绑定严格的换路事件；`gate_only` 修订用于绑定运行图或门禁状态，不伪装成推理换路。

Anti-oscillation rules / 防振荡规则：

1. The same policy version and signal fingerprint cannot produce a different route. / 同一策略版本与信号指纹不得产生不同路由。
2. Do not repeat a rejected switch without new evidence, a changed policy, or changed authoritative state. / 没有新证据、策略变化或权威状态变化时，不得重复被拒换路。
3. Configure a positive maximum switch count and no-progress condition; reaching either applies the contract's exact stop, escalate, or reject action. / 配置正整数最大换路次数与无进展条件；达到任一上限时执行契约中精确的停止、升级或拒绝动作。
4. De-escalation requires resolved critical uncertainty, a remaining deterministic or low-risk scope, validator compatibility, and recorded budget settlement. / 降档要求关键不确定性已解决、剩余范围确定或低风险、验证器兼容且预算已记录结算。
5. Human escalation terminates the current run. Approval starts a linked run with refreshed permissions, snapshots, policy, budget, and validators. / 人工升级终止当前运行；批准后启动关联新运行，并刷新权限、快照、策略、预算和验证器。

### Run-Graph Compilation / 运行图编译

After routing, compile an immutable initial run graph. A route selects structure; it does not directly dispatch work. / 路由后编译不可变初始运行图。路由只选择结构，不直接分派工作。

| Selected mode / 所选模式 | Compile requirement / 编译要求 |
| --- | --- |
| `direct` | One bounded node, source/rule binding, minimal validator, explicit stop reason; no fake `direct` topology. / 一个受限节点、来源/规则绑定、最小验证器、显式停止原因；不伪造 `direct` 拓扑。 |
| `chain` | Compile ordered claims, dependencies, checkpoints, and reservations with the [Reasoning Chain Factory / 推理链工厂](../../reasoning-chain-factory.md). / 使用推理链工厂编译有序命题、依赖、检查点和预算预留。 |
| `parallel` | Compile materially different candidate IDs, isolated state, common criteria, join rule, vetoes, and synthesis owner. / 编译实质不同的候选 ID、隔离状态、统一标准、汇合规则、否决项和综合负责人。 |
| `iterative` | Compile hypothesis state, authorized observation action, expected information gain, per-round budget, progress measure, and stop rule. / 编译假设状态、授权观测动作、预期信息增益、单轮预算、进展度量和停止规则。 |

The graph compiler preserves task-atom dependency edges and workflow-lane controls. A reasoning node may produce judgment for a later action atom, but cannot merge with that action or bypass its mechanical-state and human gates. Runtime graph modification creates a new graph version with reason, impact, and authorization; completed side effects are reconciled rather than replayed. / 图编译器保留任务原子依赖边与流程车道控制。推理节点可以为后续行动原子产出判断，但不能与该行动合并或绕过其机械状态与人工闸门。运行中改图必须创建带原因、影响和授权的新图版本；已完成副作用应核对而非重放。

### Failure Handling / 失败处理

| Failure / 失败 | Symptom / 表现 | Required response / 必需响应 | Probe / 探针 |
| --- | --- | --- | --- |
| `FAIL_0014` Reasoning Under-Route / 推理欠路由 | A cheap path cannot satisfy required evidence or validators, or releases a false result. / 轻路径无法满足证据或验证器，或错误放行。 | Stop release; upgrade only if evidence is sufficient, otherwise complement evidence or escalate. / 阻止放行；仅在证据充分时升级推理，否则补证或升级责任边界。 | `PROBE_0003`, `PROBE_0011`, `PROBE_0013` |
| `FAIL_0015` Reasoning Over-Route / 推理过路由 | Expensive mode adds no validated quality or risk reduction. / 重路径未增加经验证的质量或风险降低。 | Counterfactual audit; tune scene policy only after enough outcome-backed samples. / 反事实审计；仅在足够后验样本后调优场景策略。 | `PROBE_0003`, `PROBE_0004`, `PROBE_0013` |
| `FAIL_0016` Route Oscillation / 路由振荡 | Repeated upgrades/de-escalations with the same evidence or state. / 在相同证据或状态下反复升降档。 | Enforce fingerprint determinism, switch cap, hysteresis, and terminal escalation. / 强制指纹确定性、换路上限、滞回和终态升级。 | `PROBE_0003`, `PROBE_0012` |
| `FAIL_0007` Runaway Loop / 循环失控 | Iterative collection or repair never exits. / 迭代补证或修复无法退出。 | Enforce information-gain/no-progress and budget stops. / 强制信息增益/无进展与预算停止。 | `PROBE_0009`, `PROBE_0012` |
| `FAIL_0005` Permission Bypass / 权限绕过 | A reasoning route is mistaken for action authorization. / 推理路由被误当作行动授权。 | Split the action atom and re-run permission, mechanical-state, approval, idempotency, and compensation gates. / 拆分行动原子并重新执行权限、机械状态、审批、幂等和补偿门。 | `PROBE_0007`, `PROBE_0014` |

Tool misselection remains `FAIL_0003` at `COG_ACTION__TOP_ROUTING`; it is not the generic identifier for a wrong reasoning path. / 工具误选仍使用行动 x 路由坐标下的 `FAIL_0003`；它不是推理路径误选的通用标识。

### Observability And Governance / 可观测性与治理

Emit at least `task_normalized`, `route_selected`, `contract_established` for executable decisions, `mode_switched`, `validation_completed`, `feedback_updated` when advice is handled, `outcome_recorded` when trustworthy outcomes arrive, and `run_ended`. Route events preserve initial/final decisions, revisions, signal states/provenance, policy binding, blockers, reasons, abstention, configuration, budget impact, and whether a switch came from route insufficiency or external-state change. / 至少发送任务已标准化、路由已选择；可执行决定还发送契约已建立；换路发送模式已切换；验证后发送验证完成；处理建议后发送反馈已更新；可信后验到达时发送结果已回接；最终发送运行已结束。路由事件保留首次/最终决定、修订、信号状态/来源、策略绑定、阻塞项、原因、弃权、配置、预算影响，以及换路由路由不足还是外部状态变化引起。

Keep route events append-only and redact request content, tool input/output, secrets, personal data, and private reasoning. Retain fingerprints, typed summaries, evidence references, actor/authority, and policy versions under scene retention policy. / 路由事件仅追加保存，并脱敏请求内容、工具输入输出、秘密、个人数据和私密推理；按场景留存策略保留指纹、类型化摘要、证据引用、执行者/权限和策略版本。

### Implementation Boundary / 实现边界

Implemented reference runtime / 已实现参考运行时：

- Typed reasoning and workflow signals use strict enum/bool states, field-level provenance, stable fingerprints, versioned workflow/reasoning policy bindings, and a versioned lossless adapter. / 推理与工作流信号使用严格枚举/布尔状态、字段级来源、稳定指纹、版本化流程/推理策略绑定及版本化无损适配器。
- [`workflow_router.py`](../../../runtime/workflow_router.py) produces the strict [workflow route envelope](../../../schemas/workflow-route-envelope.schema.json), separates execution lane from reasoning topology, retains explicit escalation handoff, and never derives `action_allowed` from reasoning alone. / 工作流协调器生成严格路由信封，分离执行车道与推理拓扑，保留显式升级交接，且绝不只凭推理得出行动授权。
- [`workflow_route_ledger.py`](../../../runtime/workflow_route_ledger.py) commits initial routes and [route revisions](../../../schemas/workflow-route-revision.schema.json) as crash-safe append-only JSONL with record/envelope/event hashes, monotonic revisions, idempotency conflict detection, a total positive switch cap, evidence-backed de-escalation, A→B→A hysteresis, deterministic replay, and `gate_only` run-graph binding. / 路由账本将初始路由与修订以崩溃安全追加式 JSONL 提交，包含记录/信封/事件哈希、单调修订、幂等冲突检测、正整数总换路上限、有证据降级、A→B→A 迟滞、确定性重放及 `gate_only` 运行图绑定。
- [`workflow_route_sqlite_ledger.py`](../../../runtime/workflow_route_sqlite_ledger.py) is the local transactional multi-writer reference: schema-versioned SQLite WAL, `BEGIN IMMEDIATE` writer serialization, full-chain validation inside every commit, compare-and-set head advancement, stream-scoped idempotency, atomic JSONL migration, fail-closed replay, and bounded health checks. It reuses the same route-transition semantics and stores no raw request, tool input/output, or private reasoning. / SQLite 路由账本是本地事务型多写者参考实现：采用带版本 Schema 的 SQLite WAL、`BEGIN IMMEDIATE` 写者串行化、每次提交内完整链校验、比较并交换式头部推进、流级幂等、JSONL 原子迁移、默认阻断重放与有限健康检查；它复用同一路由转换语义，且不存储原始请求、工具输入输出或私密推理。
- [`reasoning_artifacts.py`](../../../runtime/reasoning_artifacts.py) is the producer and consumer semantic guard for both route artifacts; [`runtime/__init__.py`](../../../runtime/__init__.py) exposes the supported workflow routing API. / 推理制品模块是两类路由制品的生产端与消费端语义闸门；运行时包入口公开受支持的工作流路由 API。
- `outcome_linkage_coverage`, `underroute_rate`, `overroute_rate`, `route_abstention_rate`, `route_oscillation_rate`, and `forced_route_with_missing_signal_rate` are registered diagnostic metrics with explicit denominators and missing states; none is gate eligible by default. / 六项路由覆盖、欠/过路由、弃权、振荡与缺失信号强制路由指标均已注册为带显式分母和缺失态的诊断指标，默认均不可门控。

Remaining production integration targets / 剩余生产集成目标：

- Replace the single-node SQLite reference with a deployment-owned network database adapter when horizontal scale, remote writers, failover, backup, or service-level objectives require it; preserve schema versioning, atomic append-and-head commit, idempotency, replay, migration, health, and fail-closed behavior. / 当水平扩展、远程写者、故障切换、备份或服务目标需要时，以部署方负责的网络数据库适配器替换单节点 SQLite 参考实现；必须保持 Schema 版本、追加记录与头部推进原子提交、幂等、重放、迁移、健康检查和默认阻断语义。
- Integrate each downstream run-graph compiler and side-effect reconciler with the sealed `run_graph_binding`; completed side effects must never be replayed blindly. / 将各下游运行图编译器与副作用核对器接入封存的运行图绑定；已完成副作用不得盲目重放。
- Deploy the trustworthy outcome linker and independently governed counterfactual-audit label producer; approve owned coverage thresholds before correctness metrics or policy auto-tuning can gate execution. / 部署可信后验关联器与独立治理的反事实审计标签生产器；在正确性指标或策略自动调优参与门控前，审批负责人覆盖阈值。

Do not promote a remaining integration target until its producer, consumer, replay or recovery, migration, behavior, and operational tests pass. / 在剩余集成目标的生产者、消费者、重放或恢复、迁移、行为及运维测试通过前，不得晋升为已实现生产能力。

### Acceptance / 验收

- Composite requests are split into independently routable task atoms with explicit dependencies. / 复合请求拆为带显式依赖、可独立路由的任务原子。
- Workflow lane and reasoning shape are separate, mutually bound decisions; reasoning execute never authorizes action. / 流程车道与推理形状相互分离又相互绑定；推理执行绝不授权行动。
- Policy, signal schema, precedence, fallback, cost asymmetry, budgets, validators, and stop conditions are versioned. / 策略、信号 Schema、优先级、兜底、成本不对称、预算、验证器和停止条件均有版本。
- Missing or unknown critical signals abstain; insufficient evidence cannot fall through to deeper reasoning. / 关键必需信号缺失或未知时弃权；证据不足不能落入更深推理。
- Selected mode compiles to an immutable run graph; switches are explicit revisions with evidence, authority, budget impact, unfinished work, hysteresis, and a finite cap. / 所选模式编译为不可变运行图；换路是带证据、权限、预算影响、未完成工作、滞回和有限上限的显式修订。
- Duplicate decisions are idempotent; policy/input changes create new decisions; crash replay reproduces the same route. / 重复决定保持幂等；策略/输入变化创建新决定；崩溃回放得到相同路由。
- Write atoms recheck object identity/version, permission, approval, idempotency, confirmation, and compensation immediately before action. / 写原子在行动前即时重检对象标识/版本、权限、审批、幂等、确认和补偿。
- Outcome-backed route accuracy is separate from operational stability; under/over-route and confidence calibration stay diagnostic until coverage and owned thresholds are approved. / 后验支撑的路由准确率与运行稳定率分离；欠/过路由及置信度校准在覆盖率和负责人阈值获批前仅作诊断。
- No private chain-of-thought, fabricated evidence, inferred approval, or unsupported route reason is stored. / 不保存私密思维过程、伪造证据、推断审批或无依据路由原因。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Complexity-Based Routing / 复杂度路由.
- 诊断用途 / Diagnostic Use: Use when problem complexity should determine the reasoning path. / 当问题复杂度应决定推理路径时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 需求进入、事故修复 / Intake, incident repair.
- 当前症状 / Current Symptoms: All requests take one reasoning path; cost grows linearly with volume; hard cases fail silently on the cheap path. / 所有请求走同一推理路径；成本随请求量线性增长；难案例在便宜路径上静默失败。
- 适配信号 / Fit Signals: 需要通过判断把问题送往不同策略或专家路径 / Judgement routes the problem to different strategies or specialist paths.
- 调整方向 / Adjustment Direction: Insert a deterministic policy at intake; define at least two reasoning tiers with budget anchors; add deterministic release rules and escalation rules tied to missing or unknown typed signals and verification failure. / 在入口插入确定性策略；定义至少两个带预算锚点的推理档位；增加确定性放行规则，以及与类型化信号缺失、未知和验证失败绑定的升级规则。
- 修改方式 / How To Modify: 1) Name the tiers and their token or model budgets. 2) Write the typed routing-signal list, precedence, abstention behavior, and versioned policy. 3) Wire missing or unknown signals and verification failure to escalation; never expose model confidence as a release input. 4) Log decision reason codes, policy version, signal fingerprint, and route switches for counterfactual misroute audit. / 1）命名档位及其 token 或模型预算；2）写出类型化路由信号、优先级、弃权行为与版本化策略；3）将信号缺失或未知及验证失败接入升级，禁止将模型置信度暴露为放行输入；4）记录决定原因码、策略版本、信号指纹与换路，用于反事实误路由审计。
- 输入 / Inputs: Request text, complexity signals, historical route outcomes, tier budget policy. / 请求文本、复杂度信号、历史路由结果、档位预算策略。
- 输出 / Outputs: Route decision record (chosen mode, topology, typed signals, policy version, reason codes, signal fingerprint, abstention), reasoning result, and escalation events. / 路由决策记录（所选模式、拓扑、类型化信号、策略版本、原因码、信号指纹、弃权状态）、推理结果与升级事件。
- 风险与治理 / Risks & Governance: Misroute cost asymmetry — under-routing hard tasks is usually costlier than over-routing simple ones, so bias escalation toward the expensive direction for high-impact requests; related failure modes `FAIL_0014` (under-route), `FAIL_0015` (over-route), `FAIL_0016` (route oscillation), and `FAIL_0007` (runaway loop); keep route decisions in the event log per `GOV_0002`. / 误路由成本不对称——难任务被低估通常比简单任务被高估更贵，高影响请求应偏向升级方向；相关失败模式 `FAIL_0014`（欠路由）、`FAIL_0015`（过路由）、`FAIL_0016`（路由振荡）与 `FAIL_0007`（循环失控）；路由决策按 `GOV_0002` 记录到事件日志。

Observability Metrics File / 可观测性指标文件: [reasoning-routing-observability.md](reasoning-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
