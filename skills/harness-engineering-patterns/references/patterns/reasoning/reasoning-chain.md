# Chain-of-Thought / 思维链

Cell / 交织点: reasoning-chain / 推理 x 链式
Capability / 能力: Reasoning / 推理
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

Runtime Protocols / 运行协议: [Reasoning Execution Flow / 推理执行流程](../../reasoning-execution-flow.md); [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md).

Factory Implementation / 工厂实现: [Reasoning Chain Factory / 推理链工厂](../../reasoning-chain-factory.md).

## Design Pattern / 设计模式

Externally Verifiable Reasoning Chain is the runtime name; Chain-of-Thought / 思维链 is retained only as the upstream source alias. The runtime records an ordered sequence of externally checkable subclaims and decision checkpoints. Each checked result may become the next premise, making the workflow auditable without exposing private chain-of-thought. / 外部可核验推理链是运行时名称；Chain-of-Thought / 思维链仅作为上游来源别名保留。运行时记录有序的外部可核验子命题与决策检查点。每个经检查的结果可以成为下一步前提，使工作流可审计而不暴露私密思维过程。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reasoning / 推理 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; 矩阵列名模式 / Matrix-listed pattern; source table maps Reasoning / 推理 x Chain / 链式 in arXiv:2605.13850. The article grounds the cell in Wei et al.'s step-by-step decomposition and names it the fastest, cheapest reasoning topology. / 代表性定义 / Representative definition；矩阵列名模式 / Matrix-listed pattern；来源表将 Reasoning / 推理 x Chain / 链式 映射到该单元。论文以 Wei et al. 的逐步分解为依据，并称其为最快、最便宜的推理拓扑。
- 问题 / Problem: Jumping directly from question to answer hides intermediate assumptions, so a wrong conclusion cannot be localized to the step that produced it and cannot be audited. / 从问题直接跳到答案会隐藏中间假设，错误结论无法定位到产生它的那一步，也无法审计。
- 架构方案 / Architectural Solution: Decompose reasoning into ordered steps with named intermediate conclusions; each step consumes the previous step's checked output, and a failed checkpoint stops the chain instead of passing the error forward. / 将推理分解为带命名中间结论的有序步骤；每步消费上一步经校验的输出，检查点失败即停链，而不是把错误向前传递。
- 工程权衡 / Engineering Trade-offs: Fastest and cheapest reasoning topology and easy to audit, but it commits to a single path, may miss alternatives, and early-step errors propagate down the chain; the article also notes its standalone value may fade as reasoning models internalize step-by-step thinking, so pair it with budget-aware Complexity-Based Routing (reasoning-routing). / 最快、最便宜且易审计的推理拓扑，但承诺单一路径、可能错过替代方案、早期步骤错误会沿链传播；论文并指出随着推理模型内化逐步推理，显式思维链的独立价值可能衰减，应与预算感知的复杂度路由（reasoning-routing）配合。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when reasoning should proceed through ordered intermediate conclusions. / 当推理需要经过有序中间结论时使用。

### Chain Step Discipline / 链式步骤纪律

| Element / 要素 | Rule / 规则 |
| --- | --- |
| Step statement / 步骤陈述 | Every step states its input, claim, grounding, and link to the next step. / 每一步陈述输入、主张、依据以及与下一步的衔接。 |
| Checkpoint / 检查点 | An intermediate conclusion must pass a check (evidence present, consistent with constraints) before it becomes the next premise. / 中间结论必须通过检查（证据在场、与约束一致）才能成为下一前提。 |
| Branch exit / 分支出口 | When a step needs to compare rival options, escalate to Parallel Exploration (reasoning-parallel) instead of forcing one path. / 当某步需要比较竞争选项时，升级到并行探索（reasoning-parallel），而不是强行单路径。 |
| Feedback exit / 反馈出口 | When a conclusion can only be trusted after external verification, escalate to Iterative Hypothesis Testing (reasoning-loop). / 当结论只有经过外部验证才可信时，升级到迭代假设测试（reasoning-loop）。 |
| Cost position / 成本位置 | Chain is the fastest and cheapest reasoning topology; tier selection among chain, loop, and parallel belongs to Complexity-Based Routing (reasoning-routing). / 链式是最快最便宜的推理拓扑；链式、循环、并行之间的档位选择交给复杂度路由（reasoning-routing）。 |

### Shared Execution Contract / 共享执行契约

Use `PATTERN_0051` to create one closable record per step with `claim_to_verify`, evidence references, action, external observation, local decision, decision state, data-source type, and resource use. A checkpoint failure blocks dependent steps until repair, rollback, switch, or escalation. / 使用 `PATTERN_0051` 为每一步创建可关闭记录，包含待验证命题、证据引用、动作、外部观察、局部决定、决定状态、来源类型和资源消耗。检查点失败时阻断依赖步骤，直至修复、回滚、换路或升级。

Never request or persist hidden reasoning text. Auditability comes from claims, evidence, actions, observations, decisions, validator results, and stop reasons. / 不得请求或持久化隐藏推理文本；可审计性来自命题、证据、动作、观察、决定、验证结果和停止原因。

### Factory Compilation / 工厂编译

Only compile a chain after the router has selected `execution_mode: chain`. Submit an explicit, versioned blueprint plus the sealed reasoning contract to `ReasoningChainFactory`; validate them with [`reasoning-chain-blueprint.schema.json`](../../../schemas/reasoning-chain-blueprint.schema.json) and [`reasoning-chain-plan.schema.json`](../../../schemas/reasoning-chain-plan.schema.json), then execute the sealed plan through `ChainPlanSession`. Before run creation, the compiler verifies runtime support for every normative stop and budget action and recompiles the source blueprint/contract to prevent rehashed-plan drift. Each step starts only after its versioned evidence records resolve and its full allocation is atomically reserved. A tool step binds one exact versioned read-only tool plus one authorization policy; its dispatch is accepted only when the injected live authorizer verifies the concrete grant, after which one fingerprint-only dispatch/observation pair is required before close. Each close uses a [`reasoning-chain-checkpoint-validation.schema.json`](../../../schemas/reasoning-chain-checkpoint-validation.schema.json) artifact bound to the plan, step, criteria, observation, evidence records, actor, and authority; actual use is then settled against the reservation exactly once. After all checkpoints pass, candidate creation atomically persists higher-version candidate-bound evidence revisions whose predecessor bindings exactly cover final-claim step evidence. Use `JsonlEventStore` when local restart-safe event replay is required, while persisting the sealed plan and contract separately. / 仅在路由器已选中 `execution_mode: chain` 后编译推理链。将显式、版本化蓝图与已密封推理契约交给 `ReasoningChainFactory`，使用 [`reasoning-chain-blueprint.schema.json`](../../../schemas/reasoning-chain-blueprint.schema.json) 和 [`reasoning-chain-plan.schema.json`](../../../schemas/reasoning-chain-plan.schema.json) 校验，再通过 `ChainPlanSession` 执行密封计划。创建运行前，编译器会核验运行时能否执行每个规范停止条件与预算动作，并重新编译源蓝图/契约以防止重算哈希后的计划漂移。每个步骤只有在版本化证据记录完成解析、完整分配预算完成原子预留后才能启动。工具步骤绑定一个确切版本的只读工具与一个授权策略；只有注入的实时授权器验证具体授权后才接受分派，且关闭前必须完成一组仅含指纹的分派—观测事件。每次关闭步骤都使用符合 [`reasoning-chain-checkpoint-validation.schema.json`](../../../schemas/reasoning-chain-checkpoint-validation.schema.json) 的制品，绑定计划、步骤、标准、观察、证据记录、执行者与授权，并把实际用量针对该预留精确结算一次。全部检查点通过后，候选创建会原子持久化更高版本且绑定候选的证据修订，其前驱绑定精确覆盖最终命题步骤证据。需要本地重启安全的事件重放时使用 `JsonlEventStore`，并另行持久化封存计划与契约。

The factory is the implementation mechanism for this existing matrix cell, not a new topology. It does not invent hidden decomposition, execute side effects, silently retry, or switch modes by itself. Rival paths exit to parallel; evidence-producing interaction exits to iterative; every exit must already be allowed by the contract. / 工厂是现有矩阵单元的实现机制，不是新拓扑。它不会凭空生成隐藏拆解、执行副作用、静默重试或自行换路。竞争路径退出到并行，需交互产证据时退出到迭代；每个出口都必须已获契约许可。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Externally Verifiable Reasoning Chain / 外部可核验推理链（upstream alias / 上游别名: Chain-of-Thought / 思维链）.
- 诊断用途 / Diagnostic Use: Use when reasoning should proceed through ordered intermediate conclusions. / 当推理需要经过有序中间结论时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 问题拆解、方案设计 / Decomposition, design.
- 当前症状 / Current Symptoms: Answers jump to conclusions with no traceable steps; wrong conclusions cannot be localized to a specific step; review effectively re-derives the whole problem instead of auditing steps. / 答案直接跳到结论、没有可追溯步骤；错误结论无法定位到具体步骤；评审等于重新推导整个问题而不是审计步骤。
- 适配信号 / Fit Signals: 推理步骤存在明确前后依赖 / Reasoning steps have clear ordered dependencies.
- 调整方向 / Adjustment Direction: Make intermediate conclusions explicit and checkable, and define escalation exits to the parallel and loop topologies. / 显式化并可校验中间结论，并定义向并行与循环拓扑升级的出口。
- 修改方式 / How To Modify: 1) Split the reasoning task into ordered steps with named intermediate conclusions. 2) Declare evidence requirements, checked claims, and a versioned checkpoint for each step. 3) Allocate the sealed contract budget and define allowlisted parallel or iterative exits. 4) Compile and seal the plan, then execute only through the session guard. 5) Record the external step chain so reviews audit claims and checkpoints, not private derivation. / 1）把推理任务拆成带命名中间结论的有序步骤；2）为每步声明证据要求、受检命题和版本化检查点；3）分配密封契约预算并定义许可的并行或迭代出口；4）编译并密封计划，且只通过会话守卫执行；5）记录外部步骤链，让评审审计命题和检查点，而非私密推导。
- 输入 / Inputs: Task statement, constraints, known evidence, explicit chain blueprint, sealed reasoning contract, and step budget. / 任务陈述、约束、已知证据、显式推理链蓝图、已密封推理契约和步骤预算。
- 输出 / Outputs: Immutable chain plan and probe plan, ordered external step records with checkable subclaims, live-verified authorization and read-only tool fingerprints when applicable, bound checkpoint-validation artifacts, candidate evidence revisions with predecessor lineage, plan-bound final candidate, mode-switch events, and stop reason; no private chain-of-thought. / 不可变推理链计划与探针计划、带可核验子命题的有序外部步骤记录、适用时实时验证的授权与只读工具指纹、已绑定的检查点验证制品、带前驱血缘的候选证据修订、与计划绑定的最终候选、换路事件和停止原因；不包含私密思维过程。
- 风险与治理 / Risks & Governance: Early-step errors propagate down the chain — checkpoint every intermediate conclusion before it becomes a premise; unrecorded intermediate conclusions lose reasoning state between steps (`FAIL_0006`) — persist the step chain per `GOV_0002`; single-path commitment misses alternatives — use the escalation exits instead of forcing the chain. / 早期步骤错误沿链传播——每个中间结论成为前提之前先过检查点；中间结论不入账会在步骤间丢失推理状态（`FAIL_0006`）——步骤链按 `GOV_0002` 持久化；单路径承诺会错过替代方案——使用升级出口而不是硬撑链式。

Observability Metrics File / 可观测性指标文件: [reasoning-chain-observability.md](reasoning-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
