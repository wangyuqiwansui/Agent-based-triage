# Complexity-Based Routing / 复杂度路由

Cell / 交织点: reasoning-routing / 推理 x 路由
Capability / 能力: Reasoning / 推理
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

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
| System 1 / 直觉档 | ~500 tokens | Lookup, classification, template answers, repeat questions. / 查表、分类、模板回答、重复问题。 | Answer emitted with confidence above threshold. / 置信度高于阈值即输出。 |
| System 2 / 深思档 | ~8K tokens | Multi-step reasoning, cross-file synthesis, non-trivial debugging. / 多步推理、跨文件综合、非平凡调试。 | Reasoning chain closes all subgoals. / 推理链关闭全部子目标。 |
| Extended Deliberation / 扩展深思档 | ~64K tokens | Architecture decisions, incident root cause, adversarial cases. / 架构决策、事故根因、对抗性案例。 | Requires explicit review or evaluation gate. / 需要显式评审或评估闸门。 |

Routing rules / 路由规则:

- Classify before reasoning starts; never let the default path be the deepest tier. / 在推理开始前分类；不得默认走最深档位。
- Route on observable complexity signals: input length, entity count, dependency depth, ambiguity flags, historical failure on similar requests. / 依据可观测复杂度信号路由：输入长度、实体数量、依赖深度、歧义标记、同类请求历史失败率。
- Escalate one tier when confidence is below threshold, verification fails, or the same request bounces back; record every escalation. / 当置信度低于阈值、验证失败或同一请求被退回时升一档，并记录每次升级。
- De-escalation is allowed only between requests, never inside one request. / 只允许在请求之间降档，不允许在单个请求内部降档。
- Misroute review: sample routed-low cases and audit whether they should have escalated. / 误路由审查：抽样低档案例，审计其是否本应升级。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Complexity-Based Routing / 复杂度路由.
- 诊断用途 / Diagnostic Use: Use when problem complexity should determine the reasoning path. / 当问题复杂度应决定推理路径时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 需求进入、事故修复 / Intake, incident repair.
- 当前症状 / Current Symptoms: All requests take one reasoning path; cost grows linearly with volume; hard cases fail silently on the cheap path. / 所有请求走同一推理路径；成本随请求量线性增长；难案例在便宜路径上静默失败。
- 适配信号 / Fit Signals: 需要通过判断把问题送往不同策略或专家路径 / Judgement routes the problem to different strategies or specialist paths.
- 调整方向 / Adjustment Direction: Insert a complexity classifier at intake; define at least two reasoning tiers with budget anchors; add an escalation rule tied to confidence and verification results. / 在入口插入复杂度分类器；定义至少两个带预算锚点的推理档位；增加与置信度和验证结果绑定的升级规则。
- 修改方式 / How To Modify: 1) Name the tiers and their token or model budgets. 2) Write the routing signal list and thresholds. 3) Wire verification failure and low confidence to escalation. 4) Log route decisions for misroute audit. / 1）命名档位及其 token 或模型预算；2）写出路由信号清单与阈值；3）将验证失败与低置信接入升级；4）记录路由决策供误路由审计。
- 输入 / Inputs: Request text, complexity signals, historical route outcomes, tier budget policy. / 请求文本、复杂度信号、历史路由结果、档位预算策略。
- 输出 / Outputs: Route decision record (chosen tier, signals, confidence), reasoning result, escalation events. / 路由决策记录（所选档位、信号、置信度）、推理结果、升级事件。
- 风险与治理 / Risks & Governance: Misroute cost asymmetry — under-routing hard tasks is usually costlier than over-routing simple ones, so bias escalation toward the expensive direction for high-impact requests; related failure modes `FAIL_0003` (wrong path selection) and `FAIL_0007` (escalation loop without exit); keep route decisions in the event log per `GOV_0002`. / 误路由成本不对称——难任务被低估通常比简单任务被高估更贵，高影响请求应偏向升级方向；相关失败模式 `FAIL_0003`（路径误选）与 `FAIL_0007`（升级循环无退出）；路由决策按 `GOV_0002` 记录到事件日志。

Observability Metrics File / 可观测性指标文件: [reasoning-routing-observability.md](reasoning-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
