# Complexity-Based Routing / 复杂度路由

Cell / 交织点: reasoning-routing / 推理 x 路由
Capability / 能力: Reasoning / 推理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

Runtime Protocols / 运行协议: [Reasoning Execution Flow / 推理执行流程](../../reasoning-execution-flow.md); [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md).

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
- 风险与治理 / Risks & Governance: Misroute cost asymmetry — under-routing hard tasks is usually costlier than over-routing simple ones, so bias escalation toward the expensive direction for high-impact requests; related failure modes `FAIL_0003` (wrong path selection) and `FAIL_0007` (escalation loop without exit); keep route decisions in the event log per `GOV_0002`. / 误路由成本不对称——难任务被低估通常比简单任务被高估更贵，高影响请求应偏向升级方向；相关失败模式 `FAIL_0003`（路径误选）与 `FAIL_0007`（升级循环无退出）；路由决策按 `GOV_0002` 记录到事件日志。

Observability Metrics File / 可观测性指标文件: [reasoning-routing-observability.md](reasoning-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
