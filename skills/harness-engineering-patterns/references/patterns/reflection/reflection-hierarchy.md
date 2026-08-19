# Experience Replay / 经验回放

Pattern ID / 模式 ID: `PATTERN_0042`
Registration Version / 注册版本: `1.0.0`
Cell / 交织点: reflection-hierarchy / 反思 x 层级
Capability / 能力: Reflection / 反思
Mode / 模式: Hierarchy / 层级
Alias / 别名: Reflection Experience Replay / 反思经验回放
Status / 状态: Active registry identity, draft engineering maturity / 注册身份已启用，工程成熟度为草稿
Source / 来源: arXiv:2605.13850 v2 matrix identity plus repository engineering specifications / arXiv:2605.13850 v2 矩阵身份与仓库工程规范

Use this file as the canonical design-pattern definition for `PATTERN_0042`. / 将本文档作为 `PATTERN_0042` 的规范设计模式定义。

Engineering specifications / 工程规范：

- [General Execution Flow v0.2 / 通用执行流程 v0.2](../../../../../docs/reflection/hanerss_通用执行流程_v0_2.md) defines the execution control plane. / 定义执行控制面。
- [Workflow Observability Probes v0.2 / 工作流可观测性探针 v0.2](../../../../../docs/reflection/hanerss_工作流可观测性探针_v0_2.md) defines the observation and evidence-completion plane. / 定义观测与证据补全面。
- [Governed Reflection Execution Flow / 受治理反思执行流程](../../reflection-execution-flow.md) owns shared admission, authorization, comparable revalidation, recovery, learning governance, and stopping. / 负责共享准入、授权、可比复验、恢复、学习治理与停止。

## Quick Navigation / 快速导航

- [Registration Contract / 注册契约](#registration-contract--注册契约)
- [Core Replay Flow / 核心回放流程](#core-replay-flow--核心回放流程)
- [Two Orthogonal Hierarchies / 两组正交层级](#two-orthogonal-hierarchies--两组正交层级)
- [Replay Receipt / 回放凭据](#replay-receipt--回放凭据)
- [Adoption And Credit Evidence / 采用与信用证据](#adoption-and-credit-evidence--采用与信用证据)
- [Acceptance / 验收](#acceptance--验收)

## Registration Contract / 注册契约

Experience Replay is a registered Reflection x Hierarchy pattern. Its primary coordinate remains `COG_REFLECTION__TOP_HIERARCHY`; memory, loop, orchestration, and governance are supporting dependencies and do not rename the cell. / 经验回放是已注册的“反思 x 层级”模式。其主坐标保持为 `COG_REFLECTION__TOP_HIERARCHY`；记忆、循环、编排和治理只是支撑依赖，不改变该单元身份。

| Registration field / 注册字段 | Value / 值 |
| --- | --- |
| Stable identity / 稳定身份 | `PATTERN_0042` |
| Primary cognition / 主认知 | `COG_REFLECTION` |
| Supporting cognition / 支撑认知 | `COG_MEMORY`, `COG_GOVERNANCE` |
| Primary topology / 主拓扑 | `TOP_HIERARCHY` |
| Supporting topology / 支撑拓扑 | `TOP_LOOP`, `TOP_ORCHESTRATION` |
| Canonical cell / 规范单元 | `CELL_REFLECTION_HIERARCHY` |
| Registry lifecycle / 注册生命周期 | `active` |
| Engineering maturity / 工程成熟度 | `draft` |

`active` means the identity is stable and selectable. `draft` means the engineering definition exists but dedicated replay-receipt Schema, replay-specific runtime semantics, and two independent behavioral cases have not yet established validated maturity. / `active` 表示身份稳定且可用于选型；`draft` 表示已有工程定义，但专用回放凭据 Schema、回放专用运行语义及两个独立行为案例尚未建立“已验证”成熟度。

## Design Pattern / 设计模式

Experience Replay turns prior execution into a governed, testable influence on later work. It records trajectories, distills experience candidates, recalls and filters them for a later run, proves whether an experience changed a plan or action, binds that adoption to local and external outcomes, assigns credit per experience, and then retains, down-ranks, archives, or promotes the experience. / 经验回放把历史执行转化为对后续工作的受治理、可检验影响：记录轨迹、蒸馏经验候选、在后续运行中召回并过滤、证明某条经验是否改变计划或行动、将采用行为绑定到局部与外部结果、逐条分配信用，最后对经验进行保留、降权、归档或晋升。

The pattern does not treat stored history as current mechanical truth. Experience may tell the workflow what to verify; authoritative systems, deterministic checks, tool results, and accountable human decisions determine what is true now. / 本模式不把历史记录当作当前机械真值。经验可以提示工作流应该核验什么；权威系统、确定性检查、工具结果及可问责人工决定负责判定当前事实。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reflection / 反思 x Hierarchy / 层级。
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern；arXiv:2605.13850 v2 names Experience Replay at this coordinate, while the executable and observable details in this file are repository engineering extensions. / arXiv:2605.13850 v2 在该坐标命名 Experience Replay，本文的执行与观测细节属于仓库工程扩展。
- 问题 / Problem: Historical lessons exist but cannot be shown to alter later work or improve outcomes. / 历史经验存在，却无法证明其改变了后续工作或改善了结果。
- 架构方案 / Architectural Solution: Connect layered trajectories, filtered recall, adoption evidence, external outcomes, per-experience credit, and governed lifecycle decisions through one replay receipt. / 通过一份回放凭据连接分层轨迹、过滤召回、采用证据、外部结果、逐条信用与受治理生命周期决定。
- 工程权衡 / Engineering Trade-offs: Strong provenance and outcome linkage improve trust but add storage, delayed-result handling, comparison, and governance cost. / 强来源链路与结果关联提高可信度，但增加存储、延迟结果处理、比较与治理成本。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when cross-run lessons must be recalled, filtered, evidenced as adopted, linked to external outcomes, and lifecycle-managed without replacing current truth. / 当跨运行经验必须被召回、过滤、以证据证明已采用、绑定外部结果并管理生命周期，且不得替代当前真值时使用。

### Problem And Context / 问题与上下文

Use this pattern when similar work recurs across runs but ordinary logging or postmortems do not reliably change later behavior. Common symptoms are repeated failures despite available lessons, high recall with no action change, successful tasks that grant blanket credit to every injected lesson, stale experience overriding current state, and lessons promoted to rules or Skills after one anecdotal success. / 当相似工作跨运行重复出现，而普通日志或复盘不能可靠改变后续行为时使用本模式。常见症状包括：已有经验却重复失败、召回很多但行动不变、任务成功后给所有注入经验统一记功、过期经验覆盖当前状态，以及一次偶然成功后就把教训晋升为规则或 Skill。

Do not use this pattern for simple historical event playback whose goal is only debugging; that is Trace Replay Debugging. Do not use it for an in-run repair loop whose main goal is restoring the current subject; that is Self-Heal Loop. Experience Replay requires cross-run influence plus adoption and outcome evidence. / 如果只是为调试而重放历史事件，应使用 Trace Replay Debugging；如果主要目标是在本轮恢复当前对象，应使用 Self-Heal Loop。经验回放必须具备跨运行影响、采用证据和结果证据。

### Core Replay Flow / 核心回放流程

```text
source trajectory / 来源轨迹
  -> experience candidate / 经验候选
  -> layered storage with provenance / 带来源的分层存储
  -> later-run recall / 后续运行召回
  -> relevance, version, authority, freshness, conflict, and risk filtering
     / 相关性、版本、权限、时效、冲突与风险过滤
  -> context injection / 上下文注入
  -> plan or action adoption evidence / 计划或行动采用证据
  -> local result and external outcome / 局部结果与外部结果
  -> per-experience credit assignment / 逐条经验信用分配
  -> retain, down-rank, invalidate, archive, or promote
     / 保留、降权、失效、归档或晋升
```

Four facts must remain separate / 必须分开记录四类事实：

1. Recalled / 已召回: the experience was a candidate for this run. / 该经验成为本轮候选。
2. Injected / 已注入: the experience passed filtering and entered bounded context. / 该经验通过过滤并进入有界上下文。
3. Adopted / 已采用: a plan, node, field read, tool call, check, or constraint changed in a way bound to the experience. / 与该经验绑定的计划、节点、字段读取、工具调用、检查或约束发生改变。
4. Beneficial / 已产生收益: comparable local or external results support a positive contribution. / 可比的局部或外部结果支持其正向贡献。

Recall is not injection, injection is not adoption, adoption is not benefit, and task-level success does not prove that every co-present experience helped. / 召回不等于注入，注入不等于采用，采用不等于收益；任务级成功也不能证明所有同场经验都产生了帮助。

### Two Orthogonal Hierarchies / 两组正交层级

The pattern uses two different hierarchies that must not be collapsed into one label. / 本模式同时使用两组不同层级，不能混成同一标签。

Evidence abstraction / 证据抽象层级：

| Level / 层级 | Contents / 内容 | Default use / 默认用途 |
| --- | --- | --- |
| `L0` | Raw steps, events, artifacts, verifier results, and external receipts. / 原始步骤、事件、工件、验证结果与外部回执。 | Audit, reconstruction, and falsification. / 审计、重建与反证。 |
| `L1` | One episode's distilled lesson with source, scope, version, and uncertainty. / 单次任务蒸馏出的带来源、范围、版本与不确定性的教训。 | Primary recall object. / 主要召回对象。 |
| `L2` | A recurring rule candidate aggregated from multiple comparable `L1` lessons. / 从多个可比 `L1` 教训聚合出的稳定规律候选。 | Governed checklist, rule, knowledge, or Skill nomination. / 受治理的清单、规则、知识或 Skill 提名。 |

Operational replay scope / 运行回放层级：

| Scope / 范围 | Trigger / 触发 | Inputs / 输入 | Outputs / 输出 |
| --- | --- | --- | --- |
| Action-level / 动作级 | Run, repair, or failure closure. / 运行、修复或失败关闭。 | Step ledger, failure signature, verifier result. / 步骤账本、失败签名、验证结果。 | Per-step correction and `L1` candidate. / 逐步修正与 `L1` 候选。 |
| Task-level / 任务级 | Milestone or task closure. / 里程碑或任务关闭。 | Action lessons, handoffs, rework, cost, outcomes. / 动作教训、交接、返工、成本与结果。 | Checklist or task-template proposal. / 检查清单或任务模板提案。 |
| Version-level / 版本级 | Release, incident, or policy-cycle boundary. / 发布、事故或策略周期边界。 | Comparable task aggregates, incident timeline, gate outcomes. / 可比任务聚合、事故时间线与门控结果。 | Rule, threshold, policy, or capability proposal. / 规则、阈值、策略或能力提案。 |

Upper-level replay consumes validated lower-level artifacts and preserves links back to `L0`; it does not hide gaps by replacing raw evidence with summaries. / 上层回放消费已验证的下层产物，并保留回查 `L0` 的链路；不得以摘要替代原始证据来掩盖缺口。

### Execution And Observation Planes / 执行面与观测面

| Plane / 平面 | Responsibility / 职责 | Forbidden shortcut / 禁止捷径 |
| --- | --- | --- |
| Execution control plane / 执行控制面 | Create run identity, freeze the current contract, load current truth, recall and filter candidates, execute nodes, obtain outcomes, and write lifecycle decisions. / 创建运行身份、冻结当前契约、加载当前真值、召回与过滤候选、执行节点、取得结果并写入生命周期决定。 | Treating an experience as permission or current truth. / 把经验当作权限或当前真值。 |
| Observation and evidence plane / 观测与证据面 | Correlate run, experience, injection, adoption, action, outcome, and credit records; identify gaps; produce evidence-bound observation patches. / 关联运行、经验、注入、采用、行动、结果与信用记录；识别缺口；生成带证据的观察补丁。 | Editing business truth or inferring adoption from self-report alone. / 修改业务真值，或只凭自述推断采用。 |

Observation may complete deterministic references and quality labels, but it cannot silently alter an experience decision, route, permission, business result, or credit assignment. / 观测层可以补全确定性引用与质量标签，但不能静默改变经验决定、路由、权限、业务结果或信用分配。

### Replay Receipt / 回放凭据

Every participating run should produce one version-bound receipt. This is a design-level contract until a dedicated normative Schema is introduced. / 每次参与回放的运行都应产生一份绑定版本的凭据；在专用规范 Schema 引入前，它属于设计层契约。

```yaml
receipt_id: REPLAY_RECEIPT_0001
pattern_ref: PATTERN_0042
registration_version: 1.0.0
run_ref: RUN_0001
task_type_ref: TASK_TYPE_0001
experience_bundle_version: 0.2.0
candidate_experience_refs: []
filtered_experience_refs: []
injected_experience_refs: []
adopted_experience_refs: []
adoption_evidence_refs: []
local_outcome_refs: []
external_outcome_ref: null
credit_assignments:
  - experience_ref: EXPERIENCE_0001
    contribution_state: supported|unsupported|unattributed|unknown
    evidence_refs: []
lifecycle_decisions:
  - experience_ref: EXPERIENCE_0001
    decision: retain|down_rank|invalidate|archive|nominate
    authority_ref: null
    evidence_refs: []
record_completeness: complete|partial|unknown
unresolved_gaps: []
```

Empty sets are explicit facts. Missing sets are data-quality gaps. An experience may appear in a later set only if it appeared in every required prior set, and every adoption, outcome, credit, and lifecycle transition must bind its own evidence. / 空集合是显式事实，缺失集合是数据质量缺口。经验只有出现在所有必需前序集合中，才能进入后续集合；每次采用、结果、信用与生命周期转换都必须绑定自己的证据。

### Adoption And Credit Evidence / 采用与信用证据

| Evidence level / 证据等级 | Example / 示例 | Allowed conclusion / 允许结论 |
| --- | --- | --- |
| Weak / 弱 | The model or executor says it used the lesson. / 模型或执行器声明参考了经验。 | Lead only; do not mark adopted. / 仅作线索，不标记已采用。 |
| Medium / 中 | A version-bound plan, node graph, checklist, or constraint changed consistently with the lesson. / 绑定版本的计划、节点图、检查清单或约束按经验发生改变。 | May support adoption when lineage is explicit. / 血缘明确时可支持采用。 |
| Strong / 强 | A concrete tool call, authoritative field read, guard, or validation action changed and binds the lesson. / 具体工具调用、权威字段读取、守卫或验证动作发生改变并绑定经验。 | Reliable adoption evidence. / 可靠采用证据。 |
| Very strong / 很强 | Comparable replay or controlled evidence shows a local and external outcome improvement. / 可比回放或受控证据表明局部与外部结果改善。 | May support per-experience credit. / 可支持逐条经验信用分配。 |

When multiple experiences are injected, assign `supported`, `unsupported`, `unattributed`, or `unknown` separately. Never distribute one task outcome evenly across the set. Causal wording requires the attribution policy and evidence levels in the shared reflection contract. / 同时注入多条经验时，必须逐条分配 `supported`、`unsupported`、`unattributed` 或 `unknown`；不得把一个任务结果平均分给整个集合。因果表述必须满足共享反思契约中的归因策略与证据等级。

### Lifecycle And Capability Conversion / 生命周期与能力转化

| Observed state / 观测状态 | Legal next decision / 合法后续决定 |
| --- | --- |
| Relevant but not adopted / 相关但未采用 | Retain as a candidate, inspect routing or context placement, or down-rank. / 保留候选、检查路由或上下文位置，或降权。 |
| Adopted with unknown outcome / 已采用但结果未知 | Keep pending; do not grant positive credit. / 保持待定，不给予正向信用。 |
| Repeatedly ineffective or stale / 反复无效或过期 | Down-rank, invalidate, or archive with version and reason. / 带版本与原因降权、失效或归档。 |
| Repeatedly beneficial in a bounded distribution / 在有界任务分布中反复有效 | Nominate a checklist, rule, knowledge item, hard guard, or Skill. / 提名检查清单、规则、知识条目、硬守卫或 Skill。 |

Nomination is not publication. Every promoted asset follows its own evaluation, authority, release, rollback, expiry, and version lifecycle; a new version does not inherit old evidence automatically. / 提名不等于发布。每类晋升资产都必须走自己的评估、权限、发布、回滚、到期与版本生命周期；新版本不得自动继承旧证据。

### Stopping And Failure Handling / 停止与失败处理

- No qualified candidate / 无合格候选: close the replay as an explicit no-op. / 以显式无操作关闭回放。
- Incomplete or conflicting records / 记录缺失或冲突: return a provisional observation, request named evidence, or hand off; do not manufacture a lesson. / 返回临时观察、请求指定证据或交接，不得编造经验。
- Stale or unauthorized experience / 经验过期或越权: reject injection and record the reason. / 拒绝注入并记录原因。
- Adoption without outcome / 已采用但无结果: keep credit unknown and await the outcome window. / 信用保持未知并等待结果窗口。
- No measurable replay gain / 无可测回放收益: stop repeated self-justification, down-rank or redesign the experience, and preserve the baseline. / 停止重复自证，降权或重新设计经验，并保留基线。
- Risk increase or truth conflict / 风险上升或与真值冲突: current authoritative truth wins; stop, recover, or hand off under governance. / 当前权威真值优先；按治理要求停止、恢复或交接。

The replay process itself is bounded by explicit attempt, time, cost, context, and outcome-window limits. / 回放过程本身必须受明确的尝试次数、时间、成本、上下文及结果窗口限制。

### Pattern Template / 模式模板

- 状态 / Status: Named candidate / 已命名候选；stable registry identity, draft engineering maturity / 注册身份稳定，工程成熟度为草稿。
- 模式清单 / Patterns: Experience Replay / 经验回放；alias: Reflection Experience Replay / 反思经验回放。
- 诊断用途 / Diagnostic Use: Use when cross-run lessons must be recalled, filtered, evidenced as adopted, linked to external outcomes, and lifecycle-managed without replacing current truth. / 当跨运行经验必须被召回、过滤、以证据证明已采用、绑定外部结果并管理生命周期，且不得替代当前真值时使用。
- 适用工作流节点 / Applicable Workflow Nodes: Post-run review, milestone review, incident review, experience retrieval, memory writeback, outcome return, credit assignment, rule or Skill nomination. / 运行后复盘、里程碑复盘、事故复盘、经验检索、记忆回写、结果回接、信用分配、规则或 Skill 提名。
- 当前症状 / Current Symptoms: Lessons are stored but not adopted, repeated failures continue, all recalled lessons receive blanket credit, stale history overrides current state, or one success is promoted into a permanent capability. / 经验被存储却未采用、重复失败持续发生、所有召回经验被统一记功、过期历史覆盖当前状态，或一次成功就被晋升为永久能力。
- 适配信号 / Fit Signals: Similar task classes recur across runs; complete or recoverable trajectories exist; later actions and external outcomes can be linked; and the workflow needs learning beyond the current run. / 相似任务类型跨运行重复出现；存在完整或可恢复轨迹；后续动作与外部结果可关联；工作流需要超出本轮的学习。
- 调整方向 / Adjustment Direction: Separate trajectory, candidate, recall, injection, adoption, outcome, credit, and lifecycle states; preserve two orthogonal hierarchies; make current truth authoritative. / 分离轨迹、候选、召回、注入、采用、结果、信用和生命周期状态；保留两组正交层级；以当前真值为权威。
- 修改方式 / How To Modify: Register the stable pattern ID; bind the shared reflection contract; add replay receipts; filter experience before context injection; capture plan/action evidence; bind outcomes; allocate credit per experience; govern retention and promotion; instrument the observability funnel. / 注册稳定模式 ID；绑定共享反思契约；增加回放凭据；经验进入上下文前过滤；采集计划或行动证据；绑定结果；逐条分配信用；治理保留与晋升；为观测漏斗埋点。
- 输入 / Inputs: Versioned trajectories, evidence and artifact references, task type, current authoritative state, candidate experiences, policy and permission bindings, comparison baseline, outcome source, and replay budget. / 版本化轨迹、证据与工件引用、任务类型、当前权威状态、经验候选、策略与权限绑定、比较基线、结果来源及回放预算。
- 输出 / Outputs: Replay receipt, filtered and adopted experience sets, action evidence, local and external outcome bindings, per-experience credit, lifecycle decisions, unresolved gaps, and capability nominations. / 回放凭据、过滤后与已采用经验集合、行动证据、局部与外部结果绑定、逐条信用、生命周期决定、未解决缺口及能力提名。
- 风险与治理 / Risks & Governance: `FAIL_0010` Non-Replayable Audit / 审计不可复现 limits every conclusion; `FAIL_0001` Context Pollution / 上下文污染 arises from unfiltered lesson dumps; `FAIL_0007` Runaway Loop / 循环失控 applies when replay repeatedly self-justifies without outcome progress. Mitigate with provenance, current-truth checks, filtering, bounded context, explicit no-op closure, independent outcomes, per-experience credit, and separate promotion authority. / `FAIL_0010` 审计不可复现限制所有结论；未过滤经验倾倒会触发 `FAIL_0001` 上下文污染；没有结果进展却反复自证会触发 `FAIL_0007` 循环失控。通过来源追溯、当前真值核验、过滤、有界上下文、显式无操作关闭、独立结果、逐条信用和独立晋升权限缓解。

Observability Metrics File / 可观测性指标文件: [reflection-hierarchy-observability.md](reflection-hierarchy-observability.md)

## Acceptance / 验收

A registered implementation is acceptable only when / 已注册实现仅在以下条件全部满足时可验收：

- The run binds `PATTERN_0042`, registration version, task type, experience-bundle version, and current contract version. / 运行绑定 `PATTERN_0042`、注册版本、任务类型、经验包版本及当前契约版本。
- Candidate, filtered, injected, adopted, outcome, credit, and lifecycle sets are explicit and provenance-linked. / 候选、过滤、注入、采用、结果、信用与生命周期集合显式存在且带来源链路。
- Adoption is supported by plan or action evidence, never self-report alone. / 采用由计划或行动证据支持，不得只凭自述。
- Benefit and credit claims bind comparable local or external outcomes and stay within their evidence level. / 收益与信用声明绑定可比的局部或外部结果，且不超过证据等级。
- Current authoritative truth, permission, policy, and tenant boundaries override recalled experience. / 当前权威真值、权限、策略与租户边界优先于召回经验。
- Missing, conflicting, stale, redacted, and unmatched states remain explicit rather than being coerced into success or failure. / 缺失、冲突、过期、已脱敏及无法关联状态保持显式，不被强制解释为成功或失败。
- Promotion remains a separately authorized lifecycle and every terminal replay has a reason. / 晋升保持为独立授权生命周期，每个回放终态都有原因。
- No private chain-of-thought is requested or stored. / 不请求或存储私密思维过程。

## Related Patterns / 关联模式

- [Failure Diary / 失败日记](../memory/memory-loop.md): stores and recalls failure lessons. / 存储并召回失败教训。
- [Layered Retention / 分层保留](../memory/memory-hierarchy.md): governs scope, expiry, authority, and context budget. / 治理范围、到期、权威来源与上下文预算。
- [Self-Heal Loop / 自愈循环](reflection-loop.md): repairs the current subject inside a bounded loop. / 在有界循环中修复当前对象。
- [Skill Package / 技能包](reflection-routing.md): governs capability nomination, verification, publication, reuse, and withdrawal. / 治理能力提名、验证、发布、复用与撤销。
- [Observability Harness / 可观测性框架](../governance/governance-orchestration.md): coordinates audit and evidence controls. / 协调审计与证据控制。
- [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md): supplies shared deployable probes and metric semantics. / 提供共享可部署探针与指标语义。

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. Do not write ordinary runtime data into bundled history. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议；不得把普通运行数据写入内置历史。
