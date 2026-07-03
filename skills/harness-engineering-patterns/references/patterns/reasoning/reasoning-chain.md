# Chain-of-Thought / 思维链

Cell / 交织点: reasoning-chain / 推理 x 链式
Capability / 能力: Reasoning / 推理
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Chain-of-Thought decomposes a reasoning task into an ordered sequence of explicit intermediate conclusions, where each step's checked conclusion becomes the premise of the next, making the path from question to answer auditable step by step. / 思维链将推理任务分解为带显式中间结论的有序序列，每一步经校验的结论成为下一步的前提，使从问题到答案的路径可以逐步审计。

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

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Chain-of-Thought / 思维链.
- 诊断用途 / Diagnostic Use: Use when reasoning should proceed through ordered intermediate conclusions. / 当推理需要经过有序中间结论时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 问题拆解、方案设计 / Decomposition, design.
- 当前症状 / Current Symptoms: Answers jump to conclusions with no traceable steps; wrong conclusions cannot be localized to a specific step; review effectively re-derives the whole problem instead of auditing steps. / 答案直接跳到结论、没有可追溯步骤；错误结论无法定位到具体步骤；评审等于重新推导整个问题而不是审计步骤。
- 适配信号 / Fit Signals: 推理步骤存在明确前后依赖 / Reasoning steps have clear ordered dependencies.
- 调整方向 / Adjustment Direction: Make intermediate conclusions explicit and checkable, and define escalation exits to the parallel and loop topologies. / 显式化并可校验中间结论，并定义向并行与循环拓扑升级的出口。
- 修改方式 / How To Modify: 1) Split the reasoning task into ordered steps with named intermediate conclusions. 2) Add a checkpoint rule for each conclusion (evidence present, consistent with constraints). 3) Define branch and feedback escalation exits per the step discipline. 4) Record the step chain so reviews audit steps, not the whole derivation. / 1）把推理任务拆成带命名中间结论的有序步骤；2）为每个结论加检查点规则（证据在场、与约束一致）；3）按步骤纪律定义分支与反馈升级出口；4）记录步骤链，让评审只审步骤而非重推全程。
- 输入 / Inputs: Task statement, constraints, known evidence, step budget. / 任务陈述、约束、已知证据、步骤预算。
- 输出 / Outputs: Ordered step chain with intermediate conclusions, checkpoint results, final conclusion with per-step grounding, escalation events. / 带中间结论的有序步骤链、检查点结果、逐步依据支撑的最终结论、升级事件。
- 风险与治理 / Risks & Governance: Early-step errors propagate down the chain — checkpoint every intermediate conclusion before it becomes a premise; unrecorded intermediate conclusions lose reasoning state between steps (`FAIL_0006`) — persist the step chain per `GOV_0002`; single-path commitment misses alternatives — use the escalation exits instead of forcing the chain. / 早期步骤错误沿链传播——每个中间结论成为前提之前先过检查点；中间结论不入账会在步骤间丢失推理状态（`FAIL_0006`）——步骤链按 `GOV_0002` 持久化；单路径承诺会错过替代方案——使用升级出口而不是硬撑链式。

Observability Metrics File / 可观测性指标文件: [reasoning-chain-observability.md](reasoning-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
