# Blast Radius Control / 爆炸半径控制

Cell / 交织点: governance-hierarchy / 治理 x 层级
Capability / 能力: Governance / 治理
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Blast Radius Control wraps agent execution in nested containment layers so that any single failure is bounded by the innermost layer it can escape, never by good luck. / 爆炸半径控制用嵌套遏制层包裹 Agent 执行，让任何单点失败的影响被"它能逃出的最内层"限定，而不是靠运气。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Hierarchy / 层级 (Hierarchy / 层级).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Governance / 治理 x Hierarchy / 层级 in arXiv:2605.13850. The article cites the Codex CLI sandbox as a production example. / 代表性定义 / Representative definition；来源表将 Governance / 治理 x Hierarchy / 层级 映射到该单元。论文引用 Codex CLI 沙箱作为生产实例。
- 问题 / Problem: Agent actions can have outsized impact if permissions, rollout scope, or affected systems are not bounded. / 如果权限、发布范围或受影响系统没有边界，Agent 行动可能产生过大影响。
- 架构方案 / Architectural Solution: Nest containment layers from inside out — process sandbox → filesystem isolation → network restrictions → API rate limits → budget caps. Each layer bounds a different escape direction; an action must be explicitly granted passage through each layer it needs. Escalate scope only after evidence supports it. / 由内向外嵌套遏制层——进程沙箱 → 文件系统隔离 → 网络限制 → API 限速 → 预算上限。每层限定一个不同的逃逸方向；动作需要穿过哪层就必须显式获得那层的通行授权。只有证据支持时才扩大范围。
- 工程权衡 / Engineering Trade-offs: Contains risk and improves reversibility, but slows rollout and constrains capability. The article names the central challenge as minimum viable containment: layers tight enough to bound damage but loose enough that the agent can still do useful work. / 控制风险并提升可回滚性，但放慢发布并限制能力。论文点名核心难题为"最小可行遏制"：层要紧到能限损，又要松到 Agent 还能干活。

- 工作流诊断用途 / Workflow Diagnosis Use: Use when external effects need shared cumulative limits, conserved child reservations, bound permits and unknown-result reconciliation. / 当外部效果需要共享累计限额、守恒子预留、绑定许可及未知结果对账时使用。

### Containment Layer Model / 遏制层模型

| Layer (inner → outer) / 层（内→外） | Bounds / 限定 | Typical Control / 典型控制 |
| --- | --- | --- |
| 1. Process sandbox / 进程沙箱 | Code and command execution. / 代码与命令执行。 | Isolated runtime, no host escape. / 隔离运行时，不可逃逸宿主。 |
| 2. Filesystem isolation / 文件系统隔离 | What can be read or written. / 可读写范围。 | Workspace-scoped paths, read-only mounts. / 工作区路径限定、只读挂载。 |
| 3. Network restrictions / 网络限制 | Which endpoints are reachable. / 可达端点。 | Allowlists, no arbitrary egress. / 白名单、禁止任意出网。 |
| 4. API rate limits / API 限速 | How fast external effects accumulate. / 外部影响累积速度。 | Per-tool and per-endpoint quotas. / 按工具与端点配额。 |
| 5. Budget caps / 预算上限 | Total spend and total work. / 总花费与总工作量。 | Token, cost, and wall-clock ceilings. / token、成本与墙钟上限。 |

Layer rules / 层规则:

- Deny by default at every layer; passage is granted per task, not per agent. / 每层默认拒绝；通行按任务授予，不按 Agent 授予。
- Widening any layer requires evidence from a successful run at the narrower setting (staged rollout). / 放宽任何一层都需要更窄设置下成功运行的证据（分阶段放量）。
- A breach of layer n must still be contained by layer n+1 — design layers assuming the inner ones fail. / 第 n 层被突破仍须被第 n+1 层遏制——设计时假设内层会失败。
- Pair with Approval Gate (governance-routing): the gate decides whether an action runs; blast radius decides how much it can damage when it runs. / 与审批门禁（governance-routing）配套：门禁决定动作是否执行，爆炸半径决定执行时最多能损坏多少。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Blast Radius Control / 爆炸半径控制.
- 诊断用途 / Diagnostic Use: Use when external effects need shared cumulative limits, conserved child reservations, bound permits and unknown-result reconciliation. / 当外部效果需要共享累计限额、守恒子预留、绑定许可及未知结果对账时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 治理审查、方案设计 / Governance review, design.
- 当前症状 / Current Symptoms: The agent runs with ambient host permissions; one wrong command can touch production; scope grants are permanent and per-agent instead of per-task; no budget ceiling stops a runaway session. / Agent 携带宿主环境权限运行；一条错误命令即可触及生产；范围授权是永久且按 Agent 的，而非按任务；无预算上限阻止失控会话。
- 适配信号 / Fit Signals: 治理按风险、权限、组织或系统层级执行 / Governance executes by risk, permission, organization, or system level.
- 调整方向 / Adjustment Direction: Keep nested isolation and task-scoped grants; intersect business boundaries into conserved root/child envelopes, meter all entry points through one ledger/gateway, and require evidence before settlement, return or widening. / 保留嵌套隔离及任务授权，将业务边界交集转成守恒根子信封，全部入口经过同一账本网关计量，结算返还放宽均须证据。
- 修改方式 / How To Modify: Inventory effects and bypass entries; select scenario dimensions; implement atomic reservation/admission with durable idempotency; fence dispatch on stop; reconcile unknowns; test containment and failure paths in the linked acceptance matrix. / 盘点效果及旁路入口，选择场景维度，实现原子预留准入及持久幂等，停止时围栏派发，对账未知，并按所链接验收矩阵验证遏制与失败路径。
- 输入 / Inputs: Versioned proposal/approval, authenticated identity, hard/task/capability/context boundaries, scenario dimensions, staged rollout, reconciliation and stop policy. / 版本化提案审批、认证身份、硬任务能力上下文边界、场景维度、阶段推进、对账及停止策略。
- 输出 / Outputs: Scope snapshot, conserved envelopes, reservations and permits, request/receipt links, refusal and unknown records, reconciled balances, stop/resume decisions and closure reports. / 范围快照、守恒信封预留许可、请求回执关联、拒绝未知记录、已对账余额、停止恢复决策及关闭报告。
- 风险与治理 / Risks & Governance: Sandbox escape `FAIL_0009` when layers trust each other; over-containment starving the task (minimum-viable-containment challenge, article-named) pushes users to disable layers entirely — the worst outcome; permanent ambient grants recreate `FAIL_0005`; containment execution follows `GOV_0003`, passage decisions log per `GOV_0002`. / 层间互信导致沙箱逃逸 `FAIL_0009`；过度遏制饿死任务（论文点名的最小可行遏制难题）会促使用户整体关闭防线——最坏结果；永久环境授权重演 `FAIL_0005`；遏制执行遵循 `GOV_0003`，通行决策按 `GOV_0002` 记录。

### Effect Envelope Execution / 效果信封执行

For cumulative business consequences, extend the containment layers with the dedicated [execution flow](../../blast-radius-execution-flow.md#execution-steps), [shared contract](../../blast-radius-contract.md), [18 probe components and 39 metrics](../../blast-radius-observability-probes.md#components), and [source mapping](../../blast-radius-source-map.json). This is a source-backed specification for existing `PATTERN_0050`, not a deployed ledger or a new pattern. / 对累计业务后果，在遏制层之外接入专用执行流程、共享契约、18 个探针组件及 39 项指标与来源映射。这是现有模式的来源支持规范，不是已部署账本或新模式。

The execution chain is approved versioned proposal → intersected scope → root envelope → atomic child reservation → bound one-effect permit → gateway dispatch → success/nonexecution/unknown settlement → reconciliation → evidence-based return. All entry points and workers consume the same authoritative aggregate accounts; unused issued permits already occupy capacity. Parent child-allocation liabilities include descendant use and must not be counted twice. / 执行链为获批版本提案、范围交集、根信封、原子子预留、单效果绑定许可、网关派发、成功未执行未知结算、对账及证据返还。全部入口及 Worker 消费相同权威聚合账户；未用已签发许可已经占容量，父级子预留负债包含后代用量，不得重复计算。

Retries and recovery keep the original logical intent, key and cumulative quota; timeout never proves failure. Stop fences block new admission and dispatch while retaining late receipts. Manual holds preserve unknown balances and responsibility; administrative closure is not quota return. Probes cannot grant scope or mutate settlement. / 重试恢复保留原逻辑意图、键及累计额度；超时不证明失败。停止围栏阻止新准入派发且保留迟到回执；人工冻结保留未知余额责任，行政关闭不等于返还额度；探针不得授予范围或改结算。

Acceptance / 验收: [BRT01–BRT16](../../blast-radius-execution-flow.md#acceptance) and [BRQ01–BRQ16](../../blast-radius-observability-probes.md#acceptance) specify unexecuted failure-path scenarios; source-fidelity tests do not verify real external containment. / 这些为尚未执行的失败路径场景，来源保真测试不验证真实外部遏制。

### Module Attachment / 模块工程挂载

Identity / 身份: `CELL_GOVERNANCE_HIERARCHY; PATTERN_0050`. Existing names and maturity stay unchanged. / 保持现有名称与成熟度不变。

Constrain delegated work at every parent/child boundary and every effectful entry point, with aggregate limits shared across the delegation tree. / 在每个父子委托边界及外部影响入口约束工作，并让整棵委托树共享聚合限额。

Read the maintained [execution flow / 执行流程](../../governance-execution-flow.md#execution-steps) (执02、06、08–09、14–16) and [shared contract / 共享契约](../../governance-contract.md). These are specification-only engineering extensions from the supplied lesson-36 documents; this card does not provide a dedicated production runtime or make an existing runtime implement `GOV_BOUNDARY_OBS`. / 阅读维护版执行流程与共享契约。这些内容是用户第 36 讲资料的规范级工程扩展；本卡不提供专用生产运行时，也不表示既有运行时已实现 `GOV_BOUNDARY_OBS`。

| Attachment point / 落点 | Required behavior and evidence / 必要行为与证据 |
| --- | --- |
| Delegation / 委托 | The child's effective capability is the intersection of parent delegation, child credential, current policy, and resource scope; verify expiry and revocation. / 子执行者有效能力取父委托、子凭证、当前策略与资源范围的交集，核验有效期和撤销状态。 |
| Aggregate containment / 聚合约束 | Key accounts by trusted tenant, business subject, resource domain, time window, and parent plan as applicable; children cannot select new account keys by renaming tasks. / 按适用的可信租户、业务主体、资源域、时间窗及父计划确定账户；子任务不能改名后自行选择新账户键。 |
| Revocation and handoff / 撤销与交接 | Record credential and fence versions at each dispatch entry point, acknowledgements of revocation, and in-flight work. Handoffs transfer responsibility with receipt, not ambient authority. / 在各派发入口记录凭证与围栏版本、撤销确认及在途工作；交接以回执移交责任，不移交环境中的全部权限。 |

Boundary / 边界: A parent's general approval does not approve a changed child payload. Successful low-risk work cannot justify unrelated high-risk authority. Widening requires scoped evidence and a valid independent grant; stopping or revoking does not prove an external rollback. / 父级泛化同意不批准变更后的子载荷；低风险成功不支持无关的高风险权限。放宽须有范围匹配的证据及有效独立授权，停止或撤销不证明外部已回滚。

Acceptance references / 验收引用: 执验09–11、22–24; use the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These are expected checks, not claims that production tests passed. / 这些是待验证的预期，不代表生产测试已通过。

Metric references / 指标引用: 指06–08、16–18; definitions, denominators, and unavailable states live in the [metric catalog / 指标目录](../../governance-observability-probes.md#metric-catalog). Permission and verified business success are separate results. / 口径、分母及不可用状态由指标目录统一定义；合规许可与已核实业务成功分开记录。

Observability Metrics File / 可观测性指标文件: [governance-hierarchy-observability.md](governance-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
