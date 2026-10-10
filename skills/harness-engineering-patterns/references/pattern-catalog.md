# Pattern Catalog / 模式目录

Source: arXiv:2605.13850 v2, adapted for workflow diagnosis rather than general agent taxonomy. / 来源：arXiv:2605.13850 v2，已从通用 Agent 分类调整为工作流诊断用途。

Provenance summary / 来源摘要: 28 upstream named patterns / 上游 28 个命名模式, 14 upstream blank cells / 上游 14 个空白单元, two local promotions / 2 个本地晋升模式 (`Progressive Discovery`, `Layered Retention`), and 12 remaining extension candidates / 剩余 12 个扩展候选。 The authoritative identity, source name, local alias, status, and maturity are stored in `registry.json`. / 权威身份、来源名称、本地别名、状态和成熟度存储在 `registry.json`。

Use this catalog as a compact index after locating a matrix cell. Detailed source content lives in one grouped folder per vertical capability under `references/patterns/<capability-key>/`. Empty cells are intentional gaps: propose an extension only when the current workflow repeatedly needs that intersection. / 定位交织点后，将本目录作为紧凑索引使用。详细来源内容按每个纵轴能力分组存放在 `references/patterns/<capability-key>/` 下。空白单元是有意保留的缺口：仅当当前工作流反复需要该交织点时，才建议扩展。

Each detailed pattern has two Markdown files: `<cell-key>.md` for `Design Pattern / 设计模式` and `<cell-key>-observability.md` for `Observability Metrics / 可观测性指标`. / 每个详细模式都有两个 Markdown 文件：`<cell-key>.md` 存放 `Design Pattern / 设计模式`，`<cell-key>-observability.md` 存放 `Observability Metrics / 可观测性指标`。

## Cross-Cutting Runtime Protocols / 跨单元运行协议

Composition entrypoint / 组合入口: [selection card](pattern-selection-card.md), [execution](pattern-selection-execution-flow.md), [probes](pattern-selection-observability-probes.md), [exchange contract](pattern-selection-contract.md). This source-backed selection procedure is specification-only and preserves existing pattern IDs and matrix maturity; choose no additional pattern when the baseline suffices. / 有来源的选型规程仅为规格，保留现有模式身份和矩阵成熟度；基线足够时不新增模式。

These local draft patterns coordinate several matrix cells without changing cell identity or promoting an extension candidate. The registry assigns stable local IDs and preserves supplied draft IDs as provenance; the original reasoning and probe drafts had collided with existing IDs. / 以下本地草案模式协调多个矩阵单元，但不改变单元身份，也不自动晋升扩展候选。注册表分配稳定本地 ID 并保留来源草案标识；最初推理与探针草案曾与既有 ID 冲突。

| Pattern ID / 模式 ID | Pattern / 模式 | Use / 用途 | Reference / 参考 |
| --- | --- | --- | --- |
| `PATTERN_0051` | Reasoning Execution Flow / 推理执行流程 | Route work into direct, chain, parallel, or iterative execution under machine-readable identity, budget, validation, switching, stopping, replay, and audit contracts, with a deterministic router and executable reference kernel. / 在机器可读的标识、预算、验证、换路、停止、回放和审计契约下，将工作路由到直接、链式、并行或迭代执行，并提供确定性路由器与可执行参考内核。 | [reasoning-execution-flow.md](reasoning-execution-flow.md) |
| `PATTERN_0052` | Workflow Observability Probes / 工作流可观测性探针 | Deploy stable probes with a versioned event schema, mode-probe dependency matrix, field-level provenance, reproducible metric registry, and fail-closed protected transitions. / 使用版本化事件 Schema、模式—探针依赖矩阵、字段级来源、可复现指标注册表和默认阻断的受保护转换部署稳定探针。 | [workflow-observability-probes.md](workflow-observability-probes.md) |
| `PATTERN_0053` | Pattern Combination Execution Flow / 模式组合执行流程 | Compose existing patterns through versioned connections, dependencies, shared budgets, recovery and five acceptance gates; independent probes remain report-only by default. Specification only. / 通过版本化连接、依赖、共享预算、恢复及五道验收门组合既有模式，独立探针默认仅报告；当前仅为规范。 | [Execution / 执行](pattern-combination-execution-flow.md) · [Probes / 探针](pattern-combination-observability-probes.md) · [Contract / 契约](pattern-combination-contract.md) |

## Adversarial Review Specification / 对抗评审专用规格

`PATTERN_0045` remains collaboration × loop with draft maturity. [Execution](patterns/collaboration/collaboration-loop.md) now defines 13 nodes, independent risk coverage, two-stage binding and approval/release controls; [the independent probe](patterns/collaboration/collaboration-loop-observability.md) defines 12 nodes and 27 metrics. [Contract 0.1.0](adversarial-review-contract.md) and [source mappings](adversarial-review-source-map.json) retain the supplied drafts and 44 pending integration cases. These dedicated specifications do not extend shared executable profile 3.0.0 or claim deployed receipt/metric services. / 保留既有协作 × 循环身份与草案成熟度；执行规约含 13 节点、独立风险覆盖、两层绑定和批准发布控制，独立探针含 12 节点及 27 指标；专用契约与来源映射保留两份草稿及 44 个待集成用例，不扩展共享执行配置或宣称回执指标服务已部署。

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
| action-routing / 行动 x 路由 | Tool Dispatch / 工具分派 | Use when a workflow must select and safely execute a tool under capability, authorization, idempotency, side-effect, and observability constraints. / 当工作流必须在能力、授权、幂等、副作用与可观测性约束下选择并安全执行工具时使用。 |
| action-orchestration / 行动 x 编排 | Plan-and-Execute / 计划并执行 | Use when actions need explicit planning, execution, and coordination. / 当行动需要明确计划、执行和协调时使用。 |
| action-hierarchy / 行动 x 层级 | Guardrail Sandwich / 护栏夹层 | Use when action execution must be constrained by layered pre/post guardrails. / 当行动执行必须受分层前后置护栏约束时使用。 |
| reflection-chain / 反思 x 链式 | Generator-Critic / 生成器-批评器 | Use when output should pass through a sequential critique step. / 当产出需要经过顺序批评步骤时使用。 |
| reflection-routing / 反思 x 路由 | Skill Package / 技能包 | Use when reflection routes work to packaged evaluators, repair skills, or review routines. / 当反思需要路由到封装评估器、修复技能或评审例程时使用。 |
| reflection-loop / 反思 x 循环 | Self-Heal Loop / 自愈循环 | Use when verification failure should drive repair until an external check passes. / 当验证失败应驱动修复直到外部检查通过时使用。 |
| reflection-hierarchy / 反思 x 层级 | Experience Replay / 经验回放 | Use when cross-run lessons must be recalled, filtered, evidenced as adopted, linked to external outcomes, and lifecycle-managed without replacing current truth. / 当跨运行经验必须被召回、过滤、以证据证明已采用、绑定外部结果并管理生命周期，且不得替代当前真值时使用。 |
| collaboration-chain / 协作 x 链式 | Handoff Chain / 交接链 | Use when ordered roles must transfer committed state, responsibility and evidence with verifiable acceptance and bounded recovery. / 当有序角色须通过可验证验收与有界恢复，一并交接正式状态、责任和证据时使用。 |
| collaboration-parallel / 协作 x 并行 | Fan-Out/Gather / 扇出汇聚 | Use when several contributors can work independently before synthesis. / 当多个贡献者可独立工作后再综合时使用。 |
| collaboration-loop / 协作 x 循环 | Adversarial Review / 对抗评审 | Use when independent, evidence-backed objections must constrain approval of a specific artifact version. / 当有证据的独立异议必须约束具体工件版本的批准时使用。 |
| collaboration-hierarchy / 协作 x 层级 | Hierarchical Delegation / 层级委派 | Use when work should be delegated from high-level goals to subteams or subagents. / 当工作应从高层目标委派到子团队或子 Agent 时使用。 |
| governance-routing / 治理 x 路由 | Approval Gate / 审批门禁 | Use when reviewable proposals need scoped approval, durable waiting, revalidation and accountable effect reconciliation. / 当可审提案需要受限审批、持久等待、执行前重检及可追责的效果核对时使用。 |
| governance-parallel / 治理 x 并行 | Progressive Commitment / 渐进承诺 | Use when scoped capability authority must grow through verified evidence, independent checks and approved promotion, with fast revocation. / 当范围明确的能力权限需要通过核验证据、独立检查和获批晋级逐步扩大，并能快速收权时使用。 |
| governance-orchestration / 治理 x 编排 | Observability Harness / 可观测性框架 | Use when workflows must prove business outcomes, preserve raw state, reconcile asynchronous effects and bind public claims to auditable evidence. / 当工作流需要证明业务结果、保留原始状态、对账异步副作用，并把对外承诺绑定到可审计证据时使用。 |
| governance-hierarchy / 治理 x 层级 | Blast Radius Control / 爆炸半径控制 | Use when external effects need shared cumulative limits, conserved child reservations, bound permits and unknown-result reconciliation. / 当外部效果需要共享累计限额、守恒子预留、绑定许可及未知结果对账时使用。 |

## Cross-Domain Tiers / 跨域分级

The article validates the catalog on four domains (financial lending, legal due diligence, network operations, healthcare triage) and tiers patterns by how often they recur. Use tiers to order selection: check foundational patterns first, treat conditional patterns as environment-triggered. / 论文在四个领域（金融信贷、法务尽调、网络运维、医疗分诊）验证目录，并按复现频率给模式分级。选型时先查基础模式，条件模式按环境触发。

| Tier / 级别 | Patterns / 模式 | Meaning / 含义 |
| --- | --- | --- |
| Foundational / 基础（3+ 领域复现） | Context Triage / 上下文分诊, RAG Pipeline / RAG 管线, Complexity-Based Routing / 复杂度路由, Generator-Critic / 生成器-批评器 | Appear in most agent workflows regardless of domain; absence needs justification. / 与领域无关地出现在多数 Agent 工作流中；缺席需要说明理由。 |
| Conditional / 条件 | Blast Radius Control / 爆炸半径控制, Fan-Out/Gather / 扇出汇聚 | Triggered by environment: action authority motivates blast-radius control; independent obligations and measured throughput needs motivate fan-out (see Environmental Constraint Laws / 环境约束定律 in `diagnosis-method.md`). / 由环境触发：行动权限要求控制爆炸半径，独立责任及实测吞吐需求支持扇出（见 `diagnosis-method.md` 环境约束定律）。 |

## Empty Or Exploratory Cells / 空白或探索单元

For governance, combine the existing approval, progressive commitment, observability and blast-radius patterns using the [module execution flow](governance-execution-flow.md), [36 probe metrics](governance-observability-probes.md#metric-catalog) and [shared contract](governance-contract.md). The supplied composite and probe IDs are source aliases; governance-chain and governance-loop remain extension candidates. / 治理任务通过模块执行流程、36 项探针指标和共享契约，组合已有审批、渐进承诺、可观测与爆炸半径模式；附件中的组合及探针编号仅为来源别名，治理链式和循环仍是扩展候选。

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

For `PATTERN_0050`, use the dedicated [Blast Radius Control execution](blast-radius-execution-flow.md), [probes and metrics](blast-radius-observability-probes.md), and [shared contract](blast-radius-contract.md) for conserved envelopes, permits, unknown reconciliation and live stops. Source aliases do not add a new pattern or change maturity. / 对爆炸半径控制，使用专用执行、探针指标及共享契约，覆盖信封守恒、许可、未知对账及实时停止；来源别名不新增模式或改变成熟度。

## Observability Harness supplement / 可观测性框架扩展

For `PATTERN_0049`, use [13 execution stages](observability-execution-flow.md#execution-steps), [45 dedicated probes and 50 OBM definitions](observability-probes.md), and [the shared contract](observability-contract.md). Confirm business outcomes independently of interface success, reconcile unknown effects, validate public claims and bind evidence completion to source/version/receiver receipts. Source aliases do not add patterns; shared `PATTERN_0052` remains unchanged. / 可观测性框架使用专用执行、探针指标及共享契约；业务结果独立于接口成功确认，未知效果先对账，对外承诺核验，证据补全绑定来源版本及接收回执。来源别名不新增模式，共享探针模式保持不变。

Progressive Commitment / 渐进承诺 uses the dedicated [execution](progressive-commitment-execution-flow.md), [114-metric probe catalog](progressive-commitment-observability-probes.md#metric-catalog) and [authority contract](progressive-commitment-contract.md) for separate task/authority clocks, evidence-bound issuance and rapid scoped revocation. This remains a draft specification on `PATTERN_0048`. / 渐进承诺通过专用执行、114 项指标探针及权限契约，分开任务与权限钟表，绑定证据签发并快速精准收权；仍是现有模式上的草案规范。
