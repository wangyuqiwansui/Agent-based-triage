# Pattern Catalog / 模式目录

Source: arXiv:2605.13850 v2, adapted for workflow diagnosis rather than general agent taxonomy. / 来源：arXiv:2605.13850 v2，已从通用 Agent 分类调整为工作流诊断用途。

Provenance summary / 来源摘要: 28 upstream named patterns / 上游 28 个命名模式, 14 upstream blank cells / 上游 14 个空白单元, two local promotions / 2 个本地晋升模式 (`Progressive Discovery`, `Layered Retention`), and 12 remaining extension candidates / 剩余 12 个扩展候选。 The authoritative identity, source name, local alias, status, and maturity are stored in `registry.json`. / 权威身份、来源名称、本地别名、状态和成熟度存储在 `registry.json`。

Use this catalog as a compact index after locating a matrix cell. Detailed source content lives in one grouped folder per vertical capability under `references/patterns/<capability-key>/`. Empty cells are intentional gaps: propose an extension only when the current workflow repeatedly needs that intersection. / 定位交织点后，将本目录作为紧凑索引使用。详细来源内容按每个纵轴能力分组存放在 `references/patterns/<capability-key>/` 下。空白单元是有意保留的缺口：仅当当前工作流反复需要该交织点时，才建议扩展。

Each detailed pattern has two Markdown files: `<cell-key>.md` for `Design Pattern / 设计模式` and `<cell-key>-observability.md` for `Observability Metrics / 可观测性指标`. / 每个详细模式都有两个 Markdown 文件：`<cell-key>.md` 存放 `Design Pattern / 设计模式`，`<cell-key>-observability.md` 存放 `Observability Metrics / 可观测性指标`。

## Pattern Map / 模式映射

| Cell / 交织点 | Pattern / 模式 | Diagnostic Use / 诊断用途 |
| --- | --- | --- |
| perception-chain / 感知 x 链式 | Semantic Compaction / 语义压缩 | Use when raw signals must be compacted before they enter working context. / 当原始信号进入工作上下文前必须压缩时使用。 |
| perception-routing / 感知 x 路由 | Context Triage / 上下文分诊 | Use when incoming context must be classified before choosing a path. / 当输入上下文必须先分类再选路径时使用。 |
| perception-parallel / 感知 x 并行 | Multi-Modal Fusion / 多模态融合 | Use when multiple signal types should be gathered and fused. / 当多类信号需要采集并融合时使用。 |
| perception-orchestration / 感知 x 编排 | Progressive Disclosure / 渐进披露 | Use when context should be revealed by a controller as the workflow needs it. / 当上下文应由控制器按工作流需要逐步披露时使用。 |
| perception-loop / 感知 x 循环 | Progressive Discovery / 渐进式发现 | Use when a workflow must gradually locate high-signal evidence in an unknown information space. / 当工作流必须在未知信息空间中逐步定位高信号证据时使用。 |
| memory-chain / 记忆 x 链式 | RAG Pipeline / RAG 管线 | Use when retrieval, grounding, and answer construction form a sequence. / 当检索、扎根和回答构成顺序管线时使用。 |
| memory-routing / 记忆 x 路由 | Hierarchical Retrieval / 层级检索 | Use when the workflow must route retrieval through levels of memory. / 当工作流必须按记忆层级路由检索时使用。 |
| memory-orchestration / 记忆 x 编排 | Progress Tracking / 进度追踪 | Use when long-running work needs a recoverable control structure for goals, milestones, evidence, mechanical truth, gates, probes, and handoff state. / 当长程任务需要用可恢复的控制结构管理目标、里程碑、证据、机械真值、闸门、探针和交接状态时使用。 |
| memory-loop / 记忆 x 循环 | Failure Diary / 失败日记（source name: Failure Journal / 来源名称：失败日志） | Use when failures must be recorded, reviewed, indexed, and recalled across future attempts. / 当失败必须被记录、审查、索引，并在未来相似任务中召回时使用。 |
| memory-hierarchy / 记忆 x 层级 | Layered Retention / 分层保留 | Use when information must be retained by scope, lifecycle, authority, evidence, and context budget across multiple memory levels. / 当信息必须按照作用域、生命周期、权威来源、证据和上下文预算跨多层记忆保留时使用。 |
| reasoning-chain / 推理 x 链式 | Chain-of-Thought / 思维链 | Use when reasoning should proceed through ordered intermediate conclusions. / 当推理需要经过有序中间结论时使用。 |
| reasoning-routing / 推理 x 路由 | Complexity-Based Routing / 复杂度路由 | Use when problem complexity should determine the reasoning path. / 当问题复杂度应决定推理路径时使用。 |
| reasoning-parallel / 推理 x 并行 | Parallel Exploration / 并行探索 | Use when independent hypotheses or solution paths should be explored together. / 当多个独立假设或方案路径应同时探索时使用。 |
| reasoning-loop / 推理 x 循环 | Iterative Hypothesis Testing / 迭代假设测试 | Use when reasoning must revise hypotheses after evidence or tests. / 当推理必须根据证据或测试修正假设时使用。 |
| action-chain / 行动 x 链式 | Prompt Chaining / 提示链 | Use when action is represented as a deterministic sequence of prompts or tool steps. / 当行动由确定性的提示或工具步骤序列表示时使用。 |
| action-routing / 行动 x 路由 | Tool Dispatch / 工具分派 | Use when the workflow chooses a tool based on request type or state. / 当工作流根据请求类型或状态选择工具时使用。 |
| action-orchestration / 行动 x 编排 | Plan-and-Execute / 计划并执行 | Use when actions need explicit planning, execution, and coordination. / 当行动需要明确计划、执行和协调时使用。 |
| action-hierarchy / 行动 x 层级 | Guardrail Sandwich / 护栏夹层 | Use when action execution must be constrained by layered pre/post guardrails. / 当行动执行必须受分层前后置护栏约束时使用。 |
| reflection-chain / 反思 x 链式 | Generator-Critic / 生成器-批评器 | Use when output should pass through a sequential critique step. / 当产出需要经过顺序批评步骤时使用。 |
| reflection-routing / 反思 x 路由 | Skill Package / 技能包 | Use when reflection routes work to packaged evaluators, repair skills, or review routines. / 当反思需要路由到封装评估器、修复技能或评审例程时使用。 |
| reflection-loop / 反思 x 循环 | Self-Heal Loop / 自愈循环 | Use when verification failure should drive repair until an external check passes. / 当验证失败应驱动修复直到外部检查通过时使用。 |
| reflection-hierarchy / 反思 x 层级 | Experience Replay / 经验回放 | Use when reflection needs replay across levels of past attempts or lessons. / 当反思需要跨多层历史尝试或经验回放时使用。 |
| collaboration-chain / 协作 x 链式 | Handoff Chain / 交接链 | Use when work passes through ordered actors or roles. / 当工作按顺序经过多个参与者或角色时使用。 |
| collaboration-parallel / 协作 x 并行 | Fan-Out/Gather / 扇出汇聚 | Use when several contributors can work independently before synthesis. / 当多个贡献者可独立工作后再综合时使用。 |
| collaboration-loop / 协作 x 循环 | Adversarial Review / 对抗评审 | Use when collaborative critique repeats until conflict or risk is resolved. / 当协作式批评需要重复到冲突或风险解决时使用。 |
| collaboration-hierarchy / 协作 x 层级 | Hierarchical Delegation / 层级委派 | Use when work should be delegated from high-level goals to subteams or subagents. / 当工作应从高层目标委派到子团队或子 Agent 时使用。 |
| governance-routing / 治理 x 路由 | Approval Gate / 审批门禁 | Use when risk or permission determines whether work can continue. / 当风险或权限决定工作能否继续时使用。 |
| governance-parallel / 治理 x 并行 | Progressive Commitment / 渐进承诺 | Use when commitments should be staged and checked in parallel with execution evidence. / 当承诺需要分阶段并与执行证据并行检查时使用。 |
| governance-orchestration / 治理 x 编排 | Observability Harness / 可观测性框架 | Use when governance requires coordinated evidence, traces, metrics, and review. / 当治理需要协调证据、追踪、指标和评审时使用。 |
| governance-hierarchy / 治理 x 层级 | Blast Radius Control / 爆炸半径控制 | Use when permissions, rollout, or impact must be limited by level. / 当权限、发布或影响范围必须按层级限制时使用。 |

## Cross-Domain Tiers / 跨域分级

The article validates the catalog on four domains (financial lending, legal due diligence, network operations, healthcare triage) and tiers patterns by how often they recur. Use tiers to order selection: check foundational patterns first, treat conditional patterns as environment-triggered. / 论文在四个领域（金融信贷、法务尽调、网络运维、医疗分诊）验证目录，并按复现频率给模式分级。选型时先查基础模式，条件模式按环境触发。

| Tier / 级别 | Patterns / 模式 | Meaning / 含义 |
| --- | --- | --- |
| Foundational / 基础（3+ 领域复现） | Context Triage / 上下文分诊, RAG Pipeline / RAG 管线, Complexity-Based Routing / 复杂度路由, Generator-Critic / 生成器-批评器 | Appear in most agent workflows regardless of domain; absence needs justification. / 与领域无关地出现在多数 Agent 工作流中；缺席需要说明理由。 |
| Conditional / 条件 | Blast Radius Control / 爆炸半径控制, Fan-Out/Gather / 扇出汇聚 | Triggered by environment: action authority triggers blast radius, volume triggers fan-out (see Environmental Constraint Laws / 环境约束定律 in `diagnosis-method.md`). / 由环境触发：行动权限触发爆炸半径，处理量触发扇出（见 `diagnosis-method.md` 环境约束定律）。 |

## Empty Or Exploratory Cells / 空白或探索单元

The paper leaves 14 intersections structurally redundant or not yet observed in practice. This Skill locally promotes perception-loop and memory-hierarchy, leaving these 12 as extension candidates: / 论文将 14 个交织点保留为空白或未观察单元。本 Skill 在本地晋升 perception-loop 与 memory-hierarchy，剩余以下 12 个扩展候选：

- perception-hierarchy / 感知 x 层级
- memory-parallel / 记忆 x 并行
- reasoning-orchestration / 推理 x 编排
- reasoning-hierarchy / 推理 x 层级
- action-parallel / 行动 x 并行
- action-loop / 行动 x 循环
- reflection-parallel / 反思 x 并行 (article hypothesis: Parallel Reflection, multiple simultaneous critics / 论文假设：并行反思，多个批评器同时评审)
- reflection-orchestration / 反思 x 编排 (article hypothesis: Reflection Orchestrate, a meta-critic dispatching domain evaluators / 论文假设：反思编排，元批评器分派领域评估器)
- collaboration-routing / 协作 x 路由
- collaboration-orchestration / 协作 x 编排
- governance-chain / 治理 x 链式
- governance-loop / 治理 x 循环
