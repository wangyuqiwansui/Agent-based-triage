# Governance Cells Introduction / 治理交织点导论

## Role / 定位

Use the governance row when workflow quality depends on permissions, policy, approvals, evidence, compliance, or risk containment. / 当工作流质量依赖权限、策略、审批、证据、合规或风险控制时，使用治理行。

Control, safety, and oversight mechanisms: enforce constraints, manage risk, preserve auditability, and govern autonomy. / 控制、安全与监督机制：执行约束、管理风险、保留可审计性并治理自主性。

## 论文对齐 / Article Alignment

- Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850).
- Cognitive function / 认知功能: Governance / 治理.
- Article framing / 论文框架: The article treats this row as one cognitive function in a 7 x 6 matrix, crossed with six execution topologies. / 论文将本行作为 7 x 6 矩阵中的一个认知功能，并与六种执行拓扑交叉。
- Boundary / 边界: Governance is not ordinary preference; it changes what is allowed, observable, reversible, or accountable. / 治理不是普通偏好；它改变什么被允许、可观察、可回滚或可问责。

## When To Read / 何时读取

Read this introduction before choosing a specific governance intersection. / 在选择具体 governance 交织点前，先阅读本导论。

- Use / 使用: Use it when unsafe actions need gating, rollout impact must be limited, evidence is missing, or autonomy needs boundaries. / 当不安全行动需要门禁、发布影响必须受限、证据缺失或自主性需要边界时使用。
- Do not use it as the source of detailed pattern fields; open the linked pattern file for the chosen intersection. / 不要将本页作为详细模式字段来源；选择交织点后打开对应模式文件。

## 矩阵摘要 / Matrix Summary

This row currently has 4 named pattern candidates and 2 extension candidates. / 本行当前包含 4 个已命名候选模式和 2 个扩展候选。

| Mode / 模式 | Status / 状态 | Pattern Cell / 模式单元 |
| --- | --- | --- |
| Chain / 链式 | Extension / 扩展 | [Extension Candidate / 扩展候选](governance-chain.md) |
| Routing / 路由 | Named / 已命名 | [Approval Gate / 审批门禁](governance-routing.md) |
| Parallel / 并行 | Named / 已命名 | [Progressive Commitment / 渐进承诺](governance-parallel.md) |
| Orchestration / 编排 | Named / 已命名 | [Observability Harness / 可观测性框架](governance-orchestration.md) |
| Loop / 循环 | Extension / 扩展 | [Extension Candidate / 扩展候选](governance-loop.md) |
| Hierarchy / 层级 | Named / 已命名 | [Blast Radius Control / 爆炸半径控制](governance-hierarchy.md) |

## 选择法则 / Selection Laws

- Choose Chain when the work is a dependable sequence. / 当工作是可靠顺序流程时选择链式。
- Choose Routing when the first decision is classification or ownership. / 当第一步决策是分类或归属时选择路由。
- Choose Parallel when independent evidence or contributors can be gathered safely. / 当独立证据或贡献者可以安全汇聚时选择并行。
- Choose Orchestration when a controller must manage state, tools, dependencies, or handoffs. / 当控制器必须管理状态、工具、依赖或交接时选择编排。
- Choose Loop when feedback must change the next attempt. / 当反馈必须改变下一次尝试时选择循环。
- Choose Hierarchy when work must be delegated or constrained across levels. / 当工作必须跨层级委派或约束时选择层级。

## Trace / 追踪

After applying a design pattern, produce a project-local runtime Trace at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 应用设计模式后，依据 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地运行时 Trace。

## Navigation / 导航

| Mode / 模式 | Pattern Cell / 模式单元 |
| --- | --- |
| Chain / 链式 | [Extension Candidate / 扩展候选](governance-chain.md) |
| Routing / 路由 | [Approval Gate / 审批门禁](governance-routing.md) |
| Parallel / 并行 | [Progressive Commitment / 渐进承诺](governance-parallel.md) |
| Orchestration / 编排 | [Observability Harness / 可观测性框架](governance-orchestration.md) |
| Loop / 循环 | [Extension Candidate / 扩展候选](governance-loop.md) |
| Hierarchy / 层级 | [Blast Radius Control / 爆炸半径控制](governance-hierarchy.md) |

## Extension Note / 扩展说明

Extend this row only when a workflow needs a new approval, observability, compliance, or containment behavior. / 仅当工作流需要新的审批、可观测、合规或约束行为时扩展本行。
