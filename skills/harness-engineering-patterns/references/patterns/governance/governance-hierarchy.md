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

- 工作流诊断用途 / Workflow Diagnosis Use: Use when permissions, rollout, or impact must be limited by level. / 当权限、发布或影响范围必须按层级限制时使用。

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
- 诊断用途 / Diagnostic Use: Use when permissions, rollout, or impact must be limited by level. / 当权限、发布或影响范围必须按层级限制时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 治理审查、方案设计 / Governance review, design.
- 当前症状 / Current Symptoms: The agent runs with ambient host permissions; one wrong command can touch production; scope grants are permanent and per-agent instead of per-task; no budget ceiling stops a runaway session. / Agent 携带宿主环境权限运行；一条错误命令即可触及生产；范围授权是永久且按 Agent 的，而非按任务；无预算上限阻止失控会话。
- 适配信号 / Fit Signals: 治理按风险、权限、组织或系统层级执行 / Governance executes by risk, permission, organization, or system level.
- 调整方向 / Adjustment Direction: Introduce the five nested layers with deny-by-default; make grants task-scoped; require staged evidence before widening; wire budget caps as the outermost stop. / 引入默认拒绝的五层嵌套；授权按任务限定；放宽前要求分阶段证据；预算上限作为最外层停止器。
- 修改方式 / How To Modify: 1) Inventory escape directions (exec, file, network, external API, spend). 2) Set the narrowest workable bound per layer — minimum viable containment. 3) Define the evidence needed to widen each layer. 4) Test that layer n+1 catches a simulated layer-n breach. / 1）盘点逃逸方向（执行、文件、网络、外部 API、花费）；2）为每层设置最窄可用边界——最小可行遏制；3）定义放宽每层所需证据；4）测试第 n+1 层能接住模拟的第 n 层突破。
- 输入 / Inputs: Task risk classification, workspace boundary definition, endpoint allowlists, quota and budget policies. / 任务风险分类、工作区边界定义、端点白名单、配额与预算策略。
- 输出 / Outputs: Per-task containment profile, layer-passage grants with evidence, breach and near-miss reports, widening decisions with staged evidence. / 按任务遏制配置、带证据的层通行授权、突破与险情报告、附分阶段证据的放宽决策。
- 风险与治理 / Risks & Governance: Sandbox escape `FAIL_0009` when layers trust each other; over-containment starving the task (minimum-viable-containment challenge, article-named) pushes users to disable layers entirely — the worst outcome; permanent ambient grants recreate `FAIL_0005`; containment execution follows `GOV_0003`, passage decisions log per `GOV_0002`. / 层间互信导致沙箱逃逸 `FAIL_0009`；过度遏制饿死任务（论文点名的最小可行遏制难题）会促使用户整体关闭防线——最坏结果；永久环境授权重演 `FAIL_0005`；遏制执行遵循 `GOV_0003`，通行决策按 `GOV_0002` 记录。

Observability Metrics File / 可观测性指标文件: [governance-hierarchy-observability.md](governance-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
