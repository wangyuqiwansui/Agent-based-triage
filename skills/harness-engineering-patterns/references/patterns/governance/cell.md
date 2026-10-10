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

## Module Engineering Entry / 模块工程入口

Use the [execution flow / 执行流程](../../governance-execution-flow.md#execution-steps) for proposal freezing, policy provenance, approval, atomic reservation, final dispatch checks, reconciliation, and revocation; use the [probe workflow / 探针流程](../../governance-observability-probes.md) for read-only reconstruction, measurement, and evidence gaps. Their [shared contract / 共享契约](../../governance-contract.md) defines `GOV_BOUNDARY_OBS`. / 提案冻结、策略来历、审批、原子预留、最终派发检查、对账和撤销读取执行流程；只读重建、指标计算和证据缺口读取探针流程；二者以共享契约定义 `GOV_BOUNDARY_OBS`。

These maintained documents adapt the supplied lesson-36 engineering proposals. They remain `specification_only`: there is no dedicated production runtime for this contract, and existing plan/action/collaboration runtimes do not become compatible merely because fields or checks look similar. A local Trace is workflow evidence, not an approval, a credential, or proof of business success. / 维护文档改编自用户第 36 讲工程提案，状态为 `specification_only`：该契约没有专用生产运行时，既有规划、行动或协作运行时不因字段或检查相似就自动兼容。本地 Trace 是工作流证据，不是批准、权限凭证或业务成功证明。

| Existing identity / 现有身份 | Source correspondence and attachment / 来源对应与挂载 |
| --- | --- |
| `PATTERN_0047` — Approval Gate / 审批门禁 | Lesson label G1; bind proposal, current rules, receipt, and independent approval where required. / 讲义标签 G1；绑定提案、当前规则、回执与必要的独立批准。 |
| `PATTERN_0048` — Progressive Commitment / 渐进承诺 | Lesson label G3; independently merge required checks, keep shared budgets, and approve scoped promotion. / 讲义标签 G3；独立汇合必要检查、保留共享预算并批准限定范围的晋级。 |
| `PATTERN_0049` — Observability Harness / 可观测性框架 | Lesson cross-cutting label X1; reconstruct evidence and feed observations without taking control authority. / 讲义横切标签 X1；重建证据、反馈观测，不取得控制权。 |
| `PATTERN_0050` — Blast Radius Control / 爆炸半径控制 | Lesson label G2; intersect parent/child capabilities, aggregate limits, and propagate revocation. / 讲义标签 G2；取父子权限交集、聚合限额并传播撤销。 |
| `CELL_GOVERNANCE_CHAIN`, `CELL_GOVERNANCE_LOOP` | Existing unnamed extension candidates with `pattern_ref: null`; use sequential checks and bounded recovery as attachments, without naming new official patterns. / 既有未命名扩展候选，`pattern_ref: null`；挂载顺序检查与有界恢复，不新增官方模式。 |

G1/G2/G3/X1 are lesson-source labels, not registry IDs. The supplied `PATTERN_GOVERNANCE_0036` / `SKILL_GOVERNANCE_0036` proposals are source-local identifiers for a combined workflow; they do not replace existing pattern identities or add a seventh governance cell. See [source map / 来源映射](../../governance-source-map.json). / G1/G2/G3/X1 是讲义来源标签，不是注册表 ID；源资料的 `PATTERN_GOVERNANCE_0036` / `SKILL_GOVERNANCE_0036` 是组合流程的局部建议标识，不替换既有模式身份，也不新增第七个治理单元。来源关系见映射文件。

### Independent Execution and Optional Observation / 独立执行与可选观测

- Execution keeps local identity, current policy, budget/idempotency, final checks, and minimum durable audit; a disconnected optional probe does not by itself block every action. Missing mandatory controls or evidence blocks affected work according to configured policy. / 执行侧保留本地身份、当前策略、预算与幂等、最终检查及最小持久审计；可选探针断开本身不阻断全部动作，必要控制或证据缺失时按配置策略阻断受影响工作。
- Permission, dispatch, verified success, verified failure, partial completion, and unknown results stay distinct. Timeouts keep unknown reservations until authoritative reconciliation; stop or revocation does not prove that in-flight effects were recalled. / 许可、派发、核实成功、核实失败、部分完成与未知结果保持区分；超时保留未知占用直至权威对账，停止或撤销不证明在途效果已撤回。
- Probe patches append only `observation_enrichment`, preserve original facts, and need validated sources, target versions, and per-field acceptance receipts. Recovered evidence re-enters execution checks; probes cannot manufacture approvals or rewrite business outcomes. / 探针补丁仅追加 `observation_enrichment`，保留原始事实，并要求核验来源、目标版本及逐字段采纳回执；补回证据须重新进入执行检查，探针不能生成批准或改写业务结果。
- Use [execution acceptance cases / 执行验收用例](../../governance-execution-flow.md#acceptance) and [probe acceptance cases / 探针验收用例](../../governance-observability-probes.md#acceptance) as unexecuted expectations until concrete evidence proves a run. The [metric catalog / 指标目录](../../governance-observability-probes.md#metric-catalog) separates unknown denominators from empty applicable populations. / 执行与探针验收用例在取得具体运行证据前均是未执行的预期；指标目录区分未知分母与已知无适用样本。

## Observability engineering entry / 可观测性工程入口

For `PATTERN_0049`, use the dedicated [execution stages](../../observability-execution-flow.md#execution-steps), [business-outcome probes](../../observability-probes.md) and [completion contract](../../observability-contract.md). Preserve raw status, confirm outcomes at the designated authority, keep public claims evidence-bound and separate run closure from task resolution. Source aliases do not replace the shared probe pattern or promote maturity. / 可观测性框架使用专用执行阶段、业务结果探针及补全契约；保留原始状态，由约定权威源确认结果，对外承诺绑定证据，分开运行关闭与任务解决。来源别名不替换共享探针模式，也不晋升成熟度。

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

For cumulative external effects and delegated quotas, read [Blast Radius Control execution](../../blast-radius-execution-flow.md), [probes](../../blast-radius-observability-probes.md), and [shared contract](../../blast-radius-contract.md). These extend `PATTERN_0050` with conserved reservations, gateway permits, unknown-result holds and bounded observation; all 32 integration cases remain unexecuted. / 对累计外部效果及委派额度，读取爆炸半径控制专用执行、探针和共享契约；在现有模式上补充守恒预留、网关许可、未知占用及受限观测，32 个集成场景均保持未执行。

For capability autonomy and evidence-based promotion, use [Progressive Commitment execution](../../progressive-commitment-execution-flow.md), [probes](../../progressive-commitment-observability-probes.md) and [shared contract](../../progressive-commitment-contract.md). Keep task stages separate from authority levels, require fresh evidence and scoped approval at issuance, and enforce revocation at gateways; the probe has no authority-write access. / 对能力自主及证据晋级，读取渐进承诺专用执行探针与共享契约；分开任务阶段和权限等级，签发时要求新鲜证据及范围批准，执行点落实吊销，探针无权限写权。
