# Tool Dispatch / 工具分派

Cell / 交织点: action-routing / 行动 x 路由
Capability / 能力: Action / 行动
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Execution reference / 执行参考: [Governed Tool Dispatch Execution / 受治理工具调度执行](../../tool-dispatch-execution.md)
Contract version / 契约版本: `1.0.0`

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Tool Dispatch compiles each pending action into a sealed intent, exposes only the least-privilege capability frontier, selects one deterministic candidate, and then performs fourteen ordered admission checks before real execution. Selection is not authorization. Side-effecting calls also require a durable idempotency lease, and every outcome is classified by result certainty. / 工具分派把每个待执行动作编译为封存意图，只暴露最小权限能力前沿，确定性选择一个候选，然后在真实执行前完成十四项有序准入检查。选中不等于授权。具有副作用的调用还必须取得持久幂等租约，并按结果确定性分类每个执行结果。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Action / 行动 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Action / 行动 x Routing / 路由 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Action / 行动 x Routing / 路由 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: When every action goes through one generic execution path, capability mismatches send work to the wrong tool, hallucinated parameters reach real systems, and high-risk actions run with the same friction as trivial ones. / 当所有动作走同一条通用执行路径时，能力错配把工作送进错误工具、幻觉参数直达真实系统、高风险动作与琐碎动作以同样的摩擦执行。
- 架构方案 / Architectural Solution: Maintain a versioned capability catalog; hard-filter it into the current frontier before semantic matching; bind the selected candidate, actor, authorization, approval, state evidence, idempotency identity, and permit expiry into one dispatch envelope; execute only an `allow` envelope with live authorization and, for writes, a durable lease. / 维护版本化能力目录；语义匹配前先硬过滤为当前能力前沿；把所选候选、执行人、授权、审批、状态证据、幂等身份与许可有效期封存在一个调度信封中；只有 `allow` 信封通过实时授权，并且写动作取得持久租约后才执行。
- 工程权衡 / Engineering Trade-offs: The stronger boundary adds catalog maintenance, evidence freshness checks, a durable store, and reconciliation work for unknown outcomes. It buys least-privilege discovery, deterministic replay, safe write retries, and auditable execution. / 更强边界增加了能力目录维护、证据新鲜度检查、持久存储以及结果未知时的核验工作；换来最小权限发现、确定性重放、安全写重试和可审计执行。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when the workflow chooses a tool based on request type or state. / 当工作流根据请求类型或状态选择工具时使用。

### Dispatch Table Model / 分派表模型

| Field / 字段 | Content / 内容 | Guarded Failure / 防护的失败 |
| --- | --- | --- |
| action_type / 动作类型 | Classified intent of the pending action. / 待执行动作的分类意图。 | Wrong-path dispatch. / 错误路径分派。 |
| target tool / 目标工具 | Tool or skill whose declared capability matches the action. / 声明能力与动作匹配的工具或技能。 | `FAIL_0003` wrong tool selection. / `FAIL_0003` 工具选择错误。 |
| parameter schema / 参数 schema | Validation rules the call parameters must pass before dispatch. / 分派前调用参数必须通过的校验规则。 | `FAIL_0004` parameter hallucination. / `FAIL_0004` 参数幻觉。 |
| permission requirement / 权限要求 | Identity and scope needed to invoke the target. / 调用目标所需的身份与范围。 | `FAIL_0005` permission bypass. / `FAIL_0005` 权限绕过。 |
| side-effect class / 副作用等级 | read-only, reversible write, irreversible, external. / 只读、可逆写、不可逆、外部副作用。 | Underestimated blast radius. / 影响面被低估。 |
| approval hook / 审批挂钩 | Whether the action routes through the Approval Gate (governance-routing) first, per `GOV_0001`. / 是否先经审批门禁（governance-routing），按 `GOV_0001`。 | Unreviewed high-risk execution. / 高风险动作未审即行。 |

### Executable Admission Contract / 可执行准入契约

The normative order is fixed: `registration → frontier → parameters → identity_scope → workflow_stage → dependencies → state_evidence → budget_quota → idempotency → concurrency → approval → risk_environment → compensation → observability`. Every check emits `passed`, `failed`, or `waiting`; failed checks reject, waiting checks wait, and only a clean set allows execution. / 规范顺序固定为：`registration → frontier → parameters → identity_scope → workflow_stage → dependencies → state_evidence → budget_quota → idempotency → concurrency → approval → risk_environment → compensation → observability`。每项检查输出 `passed`、`failed` 或 `waiting`；失败项导致拒绝，等待项导致等待，全部通过才允许执行。

The runtime contract is split into three sealed artifacts: [`tool-dispatch-envelope.schema.json`](../../../schemas/tool-dispatch-envelope.schema.json), [`tool-execution-event.schema.json`](../../../schemas/tool-execution-event.schema.json), and [`tool-execution-result.schema.json`](../../../schemas/tool-execution-result.schema.json). [`tool_dispatch.py`](../../../runtime/tool_dispatch.py) is the coordinator and execution boundary; [`tool_dispatch_sqlite_store.py`](../../../runtime/tool_dispatch_sqlite_store.py) is the local durable lease/event reference; [`tool_dispatch_projection.py`](../../../runtime/tool_dispatch_projection.py) rebuilds complete inventories and integrity anomalies. / 运行契约分为三个封存制品：调度信封、执行事件与执行结果。`tool_dispatch.py` 是协调器与真实执行边界；`tool_dispatch_sqlite_store.py` 是本地持久租约/事件参考；`tool_dispatch_projection.py` 重建完整清单与完整性异常。

Dispatch rules / 分派规则:

- No catalog entry, no dispatch: unknown action types are explicitly rejected or returned for replanning, never sent to a guessed tool. / 无目录表项不分派：未知动作类型被明确拒绝或返回重规划，绝不猜测工具。
- Build the capability frontier before semantic selection; tools outside tenant, scope, stage, side-effect, or resource boundaries must not be shown to the selector. / 语义选择前先构建能力前沿；租户、权限、阶段、副作用或资源边界之外的工具不得暴露给选择器。
- Candidate selection is advisory; only the complete admission result plus a current, content-bound permit authorizes execution. / 候选选择只是建议；只有完整准入结果和当前、内容绑定的许可才能授权执行。
- Schema validation failures return to the caller with the diff; the dispatcher never repairs parameters silently. / schema 校验失败带差异退回调用方；分派器绝不静默修补参数。
- Every write requires a durable idempotency lease. An expired or uncertain lease becomes `unknown` and must be reconciled; it must never be directly retried. / 每个写动作必须取得持久幂等租约。过期或不确定租约进入 `unknown` 并必须先核验；绝不得直接重试。
- Distinguish `rejected`, `waiting`, `explicit_failure`, `unknown`, `partial_success`, `success`, and `reused_success`; a write is successful only when its side effect is confirmed. / 区分拒绝、等待、明确失败、结果未知、部分成功、成功和复用成功；写动作只有副作用已确认时才算成功。
- Execution runs inside controlled runtime or sandbox boundaries per `GOV_0003`, and every dispatch decision plus result is recorded per `GOV_0002`. / 执行按 `GOV_0003` 在受控 runtime 或沙箱边界内进行，每次分派决策与结果按 `GOV_0002` 入账。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选，具备可执行参考实现 / Named candidate with an executable reference implementation.
- 模式清单 / Patterns: Tool Dispatch / 工具分派.
- 诊断用途 / Diagnostic Use: Use when the workflow chooses a tool based on request type or state. / 当工作流根据请求类型或状态选择工具时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 执行实现、协作交接 / Implementation, collaboration handoff.
- 当前症状 / Current Symptoms: Actions frequently hit the wrong tool and bounce back; hallucinated or malformed parameters reach real systems; high-risk and trivial actions share one undifferentiated execution path with no approval distinction. / 动作频繁打到错误工具并被弹回；幻觉或畸形参数直达真实系统；高风险与琐碎动作共用一条无差别执行路径、没有审批区分。
- 适配信号 / Fit Signals: 不同动作需要分派给不同工具、权限或负责人 / Different actions must be routed to different tools, permissions, or owners.
- 调整方向 / Adjustment Direction: Put a sealed capability-frontier and admission compiler in front of the executor, then protect writes with durable idempotency and result reconciliation. / 在执行器前放置封存的能力前沿与准入编译器，再用持久幂等和结果核验保护写动作。
- 修改方式 / How To Modify: 1) Inventory and version tool capabilities. 2) Hard-filter the least-privilege frontier. 3) Deterministically select one candidate without granting authority. 4) Run all fourteen admission checks and seal a short-lived permit. 5) Acquire a durable write lease, execute once, and persist the result. 6) Project complete event inventories and reconcile unknown outcomes before retry. / 1）盘点并版本化工具能力；2）硬过滤最小权限能力前沿；3）确定性选择一个候选但不授予权限；4）执行十四项准入检查并封存短时许可；5）写动作取得持久租约、仅执行一次并持久化结果；6）投影完整事件清单，结果未知时先核验再重试。
- 输入 / Inputs: Pending action with type and parameters, dispatch table, tool capability declarations and schemas, caller identity and permission scope. / 带类型与参数的待执行动作、分派表、工具能力声明与 schema、调用方身份与权限范围。
- 输出 / Outputs: Sealed dispatch envelope, ordered admission evidence, bounded permit, durable lease record for writes, standard lifecycle events, classified result, and deterministic observability projection. / 封存调度信封、有序准入证据、受限许可、写动作持久租约记录、标准生命周期事件、分类结果和确定性可观测投影。
- 风险与治理 / Risks & Governance: Wrong tool selection `FAIL_0003` — constrain selection to the frontier and verify the selected binding; parameter hallucination `FAIL_0004` — schema-validate without silent repair; permission bypass `FAIL_0005` — recheck live authority at execution; duplicate side effects — require durable leases and immutable successful-result reuse; unknown outcomes — reconcile before retry; high-risk writes — bind approval to parameters and current resource versions per `GOV_0001`; execute inside `GOV_0003` boundaries and account for all records under `GOV_0002`. / 工具选择错误 `FAIL_0003`——把选择限制在能力前沿并校验所选绑定；参数幻觉 `FAIL_0004`——按 schema 校验且不静默修补；权限绕过 `FAIL_0005`——执行时重新检查实时授权；重复副作用——要求持久租约并复用不可变成功结果；结果未知——重试前先核验；高风险写——按 `GOV_0001` 将审批绑定到参数与当前资源版本；执行留在 `GOV_0003` 边界内，全部记录按 `GOV_0002` 入账。

Observability Metrics File / 可观测性指标文件: [action-routing-observability.md](action-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
