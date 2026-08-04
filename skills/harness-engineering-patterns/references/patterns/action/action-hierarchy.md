# Guardrail Sandwich / 护栏夹层

Pattern ID / 模式 ID: `PATTERN_0038`

Version / 版本: `0.2.0`

Status / 状态: Draft / 草案

Cell / 交织点: action-hierarchy / 行动 x 层级
Capability / 能力: Action / 行动
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Related executable protocol / 关联可执行协议: [`PATTERN_0036` Tool Dispatch / 工具分派](../../tool-dispatch-execution.md)

Related observability protocol / 关联可观测协议: [`PATTERN_0052` Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)


Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Quick Navigation / 快速导航

- [Design And Boundary / 设计与边界](#design-pattern--设计模式)
- [Threat Model And Invariants / 威胁模型与不变量](#threat-model-and-safety-invariants--威胁模型与安全不变量)
- [Sandwich Layer Model / 夹层模型](#sandwich-layer-model--夹层模型)
- [Executable Composition / 可执行组合](#executable-composition--可执行组合)
- [Action Binding And Mutation / 动作绑定与参数变更](#action-binding-and-mutation-rules--动作绑定与参数变更规则)
- [Orthogonal State Facts / 正交状态事实](#orthogonal-state-facts--正交状态事实)
- [Unknown, Partial, And Compensation / 未知、部分成功与补偿](#unknown-partial-and-compensation-protocol--未知部分成功与补偿协议)
- [Audit And Observability / 审计与可观测性](#audit-and-observability-boundary--审计与可观测性边界)
- [MCP Adapter Boundary / MCP 适配边界](#mcp-adapter-boundary--mcp-适配边界)
- [Verification And Acceptance / 验证与验收](#verification-and-acceptance--验证与验收)
- [Trace Hook / 追踪钩子](#trace-hook--追踪钩子)

## Design Pattern / 设计模式

Guardrail Sandwich wraps every consequential action between a pre-check layer (permission, parameters, impact rehearsal), a controlled execution layer (sandbox, least privilege), and a post-verify layer (result check, side-effect audit, rollback plan), with guardrails placed at each level of the phase-task-subtask hierarchy. / 护栏夹层把每个有后果的动作夹在前置检查层（权限、参数、影响面预演）、受控执行层（沙箱、最小权限）与后置验证层（结果校验、副作用审计、回滚预案）之间，护栏沿阶段-任务-子任务层级逐层布置。

The pattern is a temporal and hierarchical safety wrapper, not a replacement for tool routing, workflow planning, business completion, or policy ownership. Use Tool Dispatch for capability-frontier construction and execution admission; use Plan-and-Execute for plan recovery, compensation orchestration, and final completion; use Workflow Observability Probes for evidence-backed observation and configured protected-transition gates. / 本模式是时间线与层级上的安全包装，不替代工具路由、工作流规划、业务完成判断或策略归属。能力前沿与执行准入使用 Tool Dispatch；计划恢复、补偿编排与最终完成使用 Plan-and-Execute；基于证据的观测和已配置受保护转换门禁使用 Workflow Observability Probes。

## Boundary And Non-Goals / 边界与非目标

| Component / 组件 | Owns / 负责 | Does not own / 不负责 |
| --- | --- | --- |
| Planner or model / 规划器或模型 | Propose an intent and bounded plan. / 提出行动意图与有界计划。 | Execution authority, credentials, or final effect truth. / 执行权限、凭据或最终效果事实。 |
| Guardrail Sandwich / 护栏夹层 | Layer placement, exact-action binding, containment, post-execution separation, and recovery handoff. / 护栏分层、精确动作绑定、执行隔离、事后事实分离与恢复交接。 | Semantic tool selection or goal completion. / 语义工具选择或目标完成判断。 |
| Tool Dispatch / 工具分派 | Capability frontier, candidate binding, fourteen admission checks, permit, durable write lease, execution, and result certainty. / 能力前沿、候选绑定、十四项准入、许可、写动作持久租约、执行和结果确定性。 | Workflow replanning, compensation orchestration, or output publication policy. / 工作流重规划、补偿编排或输出发布策略。 |
| Policy and approval services / 策略与审批服务 | Deterministic decisions, scoped approval, authority, expiry, and exemptions. / 确定性裁定、限定审批、权限、有效期与豁免。 | Tool execution or silent parameter repair. / 工具执行或静默修补参数。 |
| Probe suite / 探针套件 | Capture externally verifiable facts, detect gaps, compute supported metrics, and enforce configured named transition gates. / 采集外部可核验事实、发现缺口、计算有数据支持的指标并执行已配置具名转换门禁。 | Business truth or self-authorized policy change. / 业务真值或自行授权的策略变更。 |

## Threat Model And Safety Invariants / 威胁模型与安全不变量

Treat model proposals, retrieved content, tool descriptions, tool annotations, tool output, remote acknowledgements, and cross-boundary clocks as potentially wrong or adversarial. MCP requires clients to treat tool annotations as untrusted unless they come from trusted servers; annotations are hints, not local authorization. / 将模型提议、检索内容、工具描述、工具 annotations、工具输出、远程确认以及跨信任边界的时钟都视为可能错误或带攻击性。MCP 要求：除非来自可信服务器，否则客户端必须把工具 annotations 视为不可信；annotations 是提示，不是本地授权依据。

Enforce these invariants / 强制以下不变量：

1. Selection is not authorization; a planner, selector, alternate adapter, or model cannot bypass the policy enforcement point. / 选中不等于授权；规划器、选择器、替代适配器或模型不得绕过策略执行点。
2. Approval and permit bind one canonical action: actor, tool version, operation, targets, parameter hash, resource-version hash, risk, policy, source-to-sink lineage, and expiry. Any material change invalidates them. / 审批与许可绑定一个规范动作：主体、工具版本、操作、目标、参数摘要、资源版本摘要、风险、策略、source-to-sink 血缘和有效期；任何实质变化都会使其失效。
3. The executor rechecks live authority and permit validity immediately before the external call and never widens privilege or rewrites semantics. / 执行器在外部调用前立即复核实时权限与许可有效性，且绝不扩权或改写语义。
4. High-risk intent and admission facts are durably recorded before the side-effect boundary. A configured audit-persistence failure fails closed. / 高风险行动在跨越副作用边界前持久记录意图与准入事实；若策略配置为审计持久化必需，写入失败时默认阻断。
5. Once a request may have crossed the side-effect boundary, timeout, disconnect, parser failure, or tool error cannot prove `confirmed_absent`. / 请求一旦可能跨越副作用边界，超时、断连、解析失败或工具报错都不能证明 `confirmed_absent`。
6. Output release never rewrites external-effect truth. `effect=confirmed` and `output=blocked` may coexist and must not be reported as a blocked action. / 输出放行不得改写外部效果事实；`effect=confirmed` 与 `output=blocked` 可以同时成立，且不得被描述为动作已阻断。
7. An `unknown` or `partial` effect is reconciled before retry or compensation unless a separately verified operation is safe whether the original action was duplicated or absent. / 效果为 `unknown` 或 `partial` 时，必须先核验再重试或补偿；除非另行证明某操作在原动作重复与未发生两种情况下都安全。
8. Compensation is a new governed action with new action and attempt identities, a link to the original action, independent authorization, idempotency, result verification, and residual-risk evidence. / 补偿是新的受治理动作，具有新的 action/attempt 身份并关联原动作，还需独立授权、幂等、结果核验和残余风险证据。
9. Raw parameters, credentials, raw tool output, and private chain-of-thought do not enter normal events, metrics, or Trace. Persist hashes, versioned bindings, reason codes, receipts, and controlled evidence references. / 原始参数、凭据、原始工具输出和私密思维过程不得进入普通事件、指标或 Trace；只持久化摘要、版本化绑定、理由码、回执和受控证据引用。
10. Observability may propose a policy change but cannot deploy it directly. Promotion requires data-quality review, replay or adversarial evaluation, authorized approval, staged rollout, monitoring, and rollback. / 可观测数据可以提出策略变更，但不能直接部署；晋升必须经过数据质量检查、回放或对抗评估、有权限审批、分阶段发布、监控和回滚。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Action / 行动 x Hierarchy / 层级 (Hierarchy / 层级).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; Environmental Constraint Law 2 names it for irreversible-action authority; source table maps Action / 行动 x Hierarchy / 层级 in arXiv:2605.13850. / 矩阵列名模式 / Matrix-listed pattern；环境约束定律 2 为不可逆动作点名；来源表将 Action / 行动 x Hierarchy / 层级 映射到该单元。
- 问题 / Problem: Irreversible actions executed with only a single flat check — or none — leave no chance to catch a bad parameter before damage, no containment during execution, and no verification that side effects matched intent afterward. / 不可逆动作若只有一道扁平检查甚至没有检查，就没有机会在造成损害前拦截坏参数、执行中没有隔离、事后也无法验证副作用是否符合意图。
- 架构方案 / Architectural Solution: Sandwich each consequential action between three ordered layers — pre-check (permission, parameter, impact rehearsal such as dry-run or diff preview), controlled execution (sandbox, least privilege), post-verify (result check, side-effect audit, ready rollback plan) — and place guardrails at phase, task, subtask, and action levels so an escaped fault meets the next layer's check. / 将每个有后果的动作夹在三段有序层之间——前置检查（权限、参数、干跑或差异预览式影响面预演）、受控执行（沙箱、最小权限）、后置验证（结果校验、副作用审计、就绪的回滚预案）——护栏沿阶段、任务、子任务、动作层级布置，逃过一层的故障会撞上下一层检查。
- 工程权衡 / Engineering Trade-offs: Layered guardrails convert irreversible failures into pre-execution blocks or post-execution rollbacks, but each layer adds latency and maintenance; over-sandwiching trivial reversible actions wastes throughput — reversibility × impact decides which actions deserve the full sandwich (Law 2), and thresholds are re-derived locally (Law 5). / 分层护栏把不可逆失败转化为执行前阻断或执行后回滚，但每层都增加时延与维护成本；对琐碎可逆动作过度夹层浪费吞吐——由"可逆性 × 影响面"决定哪些动作值得完整夹层（定律 2），阈值按定律 5 本地重推。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when action execution must be constrained by layered pre/post guardrails. / 当行动执行必须受分层前后置护栏约束时使用。

### Sandwich Layer Model / 夹层模型

| Layer / 层 | Checks / 检查内容 | On Failure / 失败时动作 |
| --- | --- | --- |
| Pre-check / 前置检查 | Permission and scope match, parameter schema, impact rehearsal (dry-run, diff preview, affected-resource list). / 权限与范围匹配、参数 schema、影响面预演（干跑、差异预览、受影响资源清单）。 | Block before execution; escalate ambiguous scope to approval per `GOV_0001`. / 执行前阻断；范围模糊按 `GOV_0001` 升级审批。 |
| Controlled execution / 受控执行 | Runs inside sandbox or controlled runtime with least privilege per `GOV_0003`; resource and time limits armed. / 按 `GOV_0003` 在沙箱或受控 runtime 内以最小权限运行；资源与时间限制就位。 | Kill and contain; never widen privileges mid-run. / 终止并隔离；绝不在运行中扩权。 |
| Post-verify / 后置验证 | Result matches intent, side-effect audit against the rehearsed impact list, rollback plan ready and tested. / 结果符合意图、副作用对照预演影响清单审计、回滚预案就绪且经过验证。 | Roll back or compensate; record the gap between rehearsed and actual impact. / 回滚或补偿；记录预演与实际影响的差距。 |

Placement rules / 布置规则:

- Guardrails stack by hierarchy: phase-level gates bound what tasks may do, task-level gates bound subtasks, action-level sandwiches wrap individual irreversible calls — a fault escaping one level meets the next. / 护栏按层级叠放：阶段级门约束任务、任务级门约束子任务、动作级夹层包裹单个不可逆调用——逃过一层的故障会撞上下一层。
- Complementary cells / 互补格: Blast Radius Control (governance-hierarchy) bounds *where* effects may land in space; the sandwich bounds *when* checks fire around a single action's timeline. / 爆炸半径控制（governance-hierarchy）管副作用在空间上能落到哪里；夹层管单个动作时间线上检查何时触发。
- Only irreversible or high-impact actions get the full three layers; reversible-low-impact actions may skip the rehearsal to avoid check fatigue. / 只有不可逆或高影响动作才配齐三层；可逆低影响动作可跳过预演以避免检查疲劳。


## Executable Composition / 可执行组合

```text
Action intent / 行动意图
  -> Canonical action + lineage / 规范动作与血缘
  -> Tool Dispatch frontier + candidate / 工具分派前沿与候选
  -> PRE: fourteen admission checks + rehearsal/source-sink obligations
  -> Bound approval + short-lived permit / 内容绑定审批与短时许可
  -> Durable intent/admission facts / 持久化意图与准入事实
  -> EXEC: live authority + write lease + controlled executor
  -> Side-effect boundary / 副作用边界
  -> Raw-result quarantine / 原始结果隔离
  -> POST: output validation + effect verification
  -> Release | Reconcile | Compensate | Human review
  -> Durable terminal facts / 持久终态事实
```

Use the existing Tool Dispatch artifacts as the normative executable subset / 使用现有 Tool Dispatch 制品作为规范的可执行子集：

- [`tool-dispatch-envelope.schema.json`](../../../schemas/tool-dispatch-envelope.schema.json) seals frontier lineage, the selected tool, fourteen ordered checks, exact action hashes, decision, execution contract, and permit. / 封存前沿血缘、所选工具、十四项有序检查、精确动作摘要、裁定、执行契约和许可。
- [`tool-execution-event.schema.json`](../../../schemas/tool-execution-event.schema.json) records ordered, correlatable dispatch lifecycle facts. / 记录有序且可关联的调度生命周期事实。
- [`tool-execution-result.schema.json`](../../../schemas/tool-execution-result.schema.json) separates execution classification from side-effect certainty. / 分离执行分类与副作用确定性。
- [`tool_dispatch.py`](../../../runtime/tool_dispatch.py) is the execution boundary; the durable store is a local reference; the projection reconstructs complete inventories and integrity anomalies. / `tool_dispatch.py` 是执行边界；持久存储是本地参考；投影器重建完整清单与完整性异常。

These artifacts do not yet make the entire Guardrail Sandwich executable. A production adopter must add versioned contracts for rehearsal and source lineage, result quarantine and output release, reconciliation, compensation orchestration, and their failure-path tests. / 这些制品尚不足以让完整护栏夹层可执行。生产采用者还必须为预演与来源血缘、结果隔离与输出放行、核验、补偿编排及其失败路径测试增加版本化契约。

## Action Binding And Mutation Rules / 动作绑定与参数变更规则

- Build a canonical action from deterministic workflow state. Free-form model text cannot define authority, approvals, resource versions, idempotency, or compensation availability. / 从确定性工作流状态构造规范动作；自由文本模型输出不得定义权限、审批、资源版本、幂等或补偿可用性。
- Preserve one stable business-idempotency identity across retries. Each physical retry receives a new `action_id` and `attempt_id`, links `parent_action_id` to the prior action, and repeats admission with current state. / 跨重试保留一个稳定业务幂等身份；每次物理重试使用新的 `action_id` 与 `attempt_id`，通过 `parent_action_id` 关联前一动作，并基于当前状态重新准入。
- A guard may reject, wait, or return a proposed diff. It must not silently repair semantic parameters. Any accepted material diff creates a new canonical action and invalidates prior approval and permit. / 护栏可以拒绝、等待或返回建议差异，但不得静默修补语义参数；任何被接受的实质差异都会生成新的规范动作，并使原审批与许可失效。
- Source trust and data classification propagate through summarize, translate, format, retrieve, or model-transform steps. Only an authorized, recorded declassification decision may lower them. / 来源可信度与数据等级随摘要、翻译、格式化、检索或模型转换传播；只有经授权并入账的降级裁定可以降低等级。
- Before an external send, upload, publish, payment, deletion, deployment, or other high-risk sink, evaluate the complete lineage, destination, audience, release scope, and data classification. / 在外部发送、上传、发布、支付、删除、部署或其他高风险 sink 前，必须检查完整血缘、目标、接收主体、发布范围和数据等级。

OpenAI describes this control problem as source-sink analysis: untrusted external content becomes dangerous when it can influence a sensitive transmission or tool action. Constrain the sink even when input classification is imperfect. / OpenAI 将该控制问题描述为 source-sink 分析：当不可信外部内容能够影响敏感传输或工具动作时，风险才完成闭环；即使输入分类不完美，系统仍必须约束 sink。

## Orthogonal State Facts / 正交状态事实

Do not collapse action outcome into `blocked_pre`, `blocked_post`, or one generic `completed` state. Preserve at least these independent facts / 不要把行动结果压成 `blocked_pre`、`blocked_post` 或一个笼统 `completed` 状态；至少保留以下正交事实：

| Axis / 维度 | Normative or proposed values / 规范或拟议值 | Meaning / 含义 |
| --- | --- | --- |
| Admission / 准入 | `allow`, `reject`, `wait` | Whether execution may start now. / 当前是否可以开始执行。 |
| Execution classification / 执行分类 | `success`, `reused_success`, `rejected`, `explicit_failure`, `unknown`, `partial_success`, `waiting` | What is known about executor completion. / 对执行器完成情况的认知。 |
| Side-effect state / 副作用状态 | `none`, `confirmed`, `confirmed_absent`, `unknown`, `partial` | What is known about external effects. / 对外部效果的认知。 |
| Output release / 输出放行 | `not_evaluated`, `quarantined`, `redacted`, `released`, `blocked` *(design-level / 设计层)* | Whether returned content may leave quarantine. / 返回内容能否离开隔离区。 |
| Verification / 核验 | `not_required`, `pending`, `running`, `confirmed`, `inconclusive`, `exhausted` *(design-level / 设计层)* | Whether effect reconciliation is complete. / 效果核验是否完成。 |
| Compensation / 补偿 | `not_required`, `planned`, `required`, `running`, `succeeded`, `failed`, `manual_required` *(outer workflow / 外层工作流)* | Recovery debt and closure. / 恢复债务及其闭环。 |

State invariants / 状态不变量：

- `output_release=blocked` does not change `side_effect_state=confirmed`. / 输出被阻断不改变已确认副作用。
- An executor exception for a write is `unknown`, not `explicit_failure`, unless absence of side effect is independently confirmed. / 写执行器异常属于 `unknown`，除非独立确认未发生副作用，否则不得记为 `explicit_failure`。
- `partial` and `unknown` suspend dependent high-risk steps and direct retry. / `partial` 与 `unknown` 会暂停依赖的高风险步骤和直接重试。
- A successful compensation changes recovery state but never erases the original confirmed effect. / 补偿成功只改变恢复状态，不抹除原始已确认效果。

## Unknown, Partial, And Compensation Protocol / 未知、部分成功与补偿协议

1. Freeze dependent high-risk transitions and preserve the stable business-idempotency binding. / 暂停依赖的高风险转换，并保留稳定业务幂等绑定。
2. Reconcile through an external request identifier, business receipt, idempotency query, authoritative read-back, or audit record. / 使用外部请求标识、业务回执、幂等查询、权威回读或审计记录核验。
3. Respect eventual-consistency windows; one missing read is an observation, not proof of absence. / 尊重最终一致性窗口；一次未查到只是观察，不是未发生的证明。
4. Resolve to confirmed, confirmed absent, partial, or inconclusive. Bound attempts and escalate inconclusive cases to an accountable human owner. / 收敛到已确认、已确认未发生、部分成功或无法判定；限制核验次数，并将无法判定交给明确的人类负责人。
5. Retry only after confirmed absence or when the external system enforces the same stable idempotency identity. / 仅在确认未发生，或外部系统执行同一稳定幂等身份时重试。
6. Start compensation as a new guarded action and verify both compensation effects and residual risk. / 把补偿作为新的受护栏动作启动，并核验补偿效果与残余风险。

## Audit And Observability Boundary / 审计与可观测性边界

Use shared identities but separate reliability and access classes / 使用共享关联标识，但分离可靠性与访问等级：

- Audit facts / 审计事实: policy decision, authorization, approval, permit, execution intent, external-effect evidence, override, compensation, and policy change. These are append-only, non-sampled, integrity-checked records. / 策略裁定、授权、审批、许可、执行意图、外部效果证据、人工覆盖、补偿和策略变更；采用追加写、不采样并校验完整性。
- Telemetry / 遥测: latency spans, resource usage, and bounded debug context. These may be redacted, sampled, and degraded according to policy. / 时延 Span、资源消耗和有界调试上下文；可以按策略脱敏、采样和降级。
- Controlled evidence / 受控证据: exceptional raw payload references only when retention, encryption, access, and deletion rules explicitly allow them. / 仅在留存、加密、访问与删除规则明确允许时保存例外原始载荷引用。

The probe suite is not the sole source of execution truth. Reconcile gateway events with durable permits or leases, credential-broker records, network-egress evidence, and external receipts to detect bypasses and orphan effects. / 探针套件不能成为唯一执行事实来源；应将网关事件与持久许可或租约、凭据代理记录、网络出口证据和外部回执对账，以发现旁路调用与孤立副作用。

## MCP Adapter Boundary / MCP 适配边界

The repository does not currently contain an MCP adapter. When one is added, snapshot and bind the trusted server principal, negotiated protocol version, tool name, input/output Schemas, description, annotations, execution metadata, and a normalized contract digest. Recheck on session establishment, tool-list change, and before high-risk calls. Unknown or security-relevant drift fails closed; annotations never widen local capability or authorization. / 仓库当前没有 MCP 适配器。未来增加时，应快照并绑定可信服务主体、协商协议版本、工具名、输入/输出 Schema、描述、annotations、execution 元数据和规范化契约摘要；在会话建立、工具列表变化及高风险调用前复核。未知或安全相关漂移默认阻断；annotations 绝不能扩大本地能力或授权。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Guardrail Sandwich / 护栏夹层.
- 诊断用途 / Diagnostic Use: Use when action execution must be constrained by layered pre/post guardrails. / 当行动执行必须受分层前后置护栏约束时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 执行实现、发布交付 / Implementation, delivery.
- 当前症状 / Current Symptoms: Irreversible actions (deletes, deploys, external writes) execute with no dry-run or rollback plan; incidents reveal side effects nobody predicted; checks exist but all at one flat level, so a single miss reaches production. / 不可逆动作（删除、部署、外部写入）在没有干跑或回滚预案的情况下执行；事故暴露出无人预测到的副作用；检查虽有但全在同一扁平层，漏过一次就直达生产。
- 适配信号 / Fit Signals: 行动需要按阶段、任务、子任务或权限层级执行 / Actions execute by phase, task, subtask, or permission level.
- 调整方向 / Adjustment Direction: Wrap irreversible actions in the three-layer sandwich and stack guardrails down the phase-task-subtask hierarchy. / 用三层夹层包裹不可逆动作，并沿阶段-任务-子任务层级叠放护栏。
- 修改方式 / How To Modify: 1) Classify actions by reversibility × impact and pick the ones deserving the full sandwich (Law 2). 2) Define pre-checks including an impact rehearsal (dry-run or diff preview). 3) Confine execution to sandbox with least privilege. 4) Define post-verify checks and a tested rollback plan per action class. 5) Stack level gates so phase bounds task and task bounds subtask. / 1）按可逆性 × 影响面给动作分级，选出值得完整夹层的动作（定律 2）；2）定义含影响面预演（干跑或差异预览）的前置检查；3）执行限定在最小权限沙箱内；4）为每类动作定义后置验证与经过验证的回滚预案；5）叠放层级门：阶段约束任务、任务约束子任务。
- 输入 / Inputs: Action request with reversibility and impact class, permission scope, rehearsal capability (dry-run, diff), sandbox environment, rollback recipes. / 带可逆性与影响等级的动作请求、权限范围、预演能力（干跑、差异）、沙箱环境、回滚配方。
- 输出 / Outputs: Pre-check verdicts with rehearsal artifacts, contained execution record, post-verify report (result check, side-effect audit), rollback events with outcomes. / 带预演产物的前置检查裁定、受控执行记录、后置验证报告（结果校验、副作用审计）、带结果的回滚事件。
- 风险与治理 / Risks & Governance: Permission bypass `FAIL_0005` when an action skips its pre-check level — make the sandwich the only execution path for irreversible classes; sandbox escape `FAIL_0009` — execution layer enforces `GOV_0003` boundaries and never widens privileges mid-run; ambiguous-scope actions escalate to approval per `GOV_0001`; all three layers' verdicts are recorded per `GOV_0002` so the post-incident audit can replay which layer failed. / 动作绕过前置检查层即权限绕过 `FAIL_0005`——让夹层成为不可逆动作类的唯一执行路径；沙箱逃逸 `FAIL_0009`——执行层强制 `GOV_0003` 边界且绝不在运行中扩权；范围模糊动作按 `GOV_0001` 升级审批；三层裁定全部按 `GOV_0002` 入账，事后审计可回放是哪一层失守。

Observability Metrics File / 可观测性指标文件: [action-hierarchy-observability.md](action-hierarchy-observability.md)

## Verification And Acceptance / 验证与验收

Minimum design acceptance / 最小设计验收：

- Every high-risk path identifies the exact pre-guard, side-effect boundary, post-guard, owner, and failure disposition. / 每条高风险路径都明确前置护栏、副作用边界、后置护栏、负责人和失败处置。
- Protected actions cannot reach credentials, network egress, or the real adapter outside the guarded executor. / 受保护动作不能绕过受控执行器取得凭据、网络出口或真实适配器。
- Approval and permit drift tests cover parameters, targets, tool version, resource version, policy, lineage, and expiry. / 审批与许可漂移测试覆盖参数、目标、工具版本、资源版本、策略、血缘和有效期。
- Timeout, crash, stale lease, duplicate delivery, partial batch, false success, malicious tool output, reconciliation exhaustion, compensation failure, and probe outage have explicit failure-path tests. / 超时、崩溃、陈旧租约、重复投递、批量部分成功、伪成功、恶意工具输出、核验耗尽、补偿失败和探针故障都有明确失败路径测试。
- Effect truth, output release, verification, and compensation remain independently replayable. / 效果事实、输出放行、核验和补偿可以独立回放。
- No design-only metric or field is described as registered, implemented, or gate-eligible. / 不把设计层指标或字段描述成已注册、已实现或可门控。

Current executable subset verification / 当前可执行子集验证：

```text
python -m pytest tests/test_tool_dispatch.py tests/test_tool_dispatch_sqlite_store.py tests/test_tool_dispatch_projection.py -q
python skills/harness-engineering-patterns/scripts/validate_harness_skill.py skills/harness-engineering-patterns
python -m pytest -q
```

## Evidence Sources / 证据来源

- [A Two-Dimensional Framework for AI Agent Design Patterns](https://arxiv.org/abs/2605.13850) — pattern identity and coordinate. / 模式身份与坐标。
- [MCP Tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) — tool Schema and the untrusted-annotation boundary. / 工具 Schema 与 annotations 不可信边界。
- [Designing AI agents to resist prompt injection](https://openai.com/index/designing-agents-to-resist-prompt-injection/) — source-sink analysis and constraining sensitive actions. / source-sink 分析与敏感动作约束。
- Repository Tool Dispatch Schemas, runtime, stores, projection, and tests linked above. / 上文链接的仓库 Tool Dispatch Schema、运行时、存储、投影与测试。

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
