# Governed Tool Dispatch Execution / 受治理工具调度执行

Pattern ID / 模式 ID: `PATTERN_0036`

Version / 版本: `1.0.0`

Status / 状态: Review / 评审中

Primary coordinate / 主坐标: `COG_ACTION__TOP_ROUTING`

This reference turns Tool Dispatch from a descriptive routing table into an executable action boundary. It covers capability discovery, the current capability frontier, deterministic candidate selection, fourteen ordered admission checks, durable idempotency leasing, real execution, result certainty, standard events, and observability projection. / 本参考将工具分派从描述性路由表升级为可执行行动边界，覆盖能力发现、当前能力前沿、确定性候选选择、十四项有序准入检查、持久幂等租约、真实执行、结果确定性、标准事件与可观测投影。

The source workflow draft described a cross-cutting general executor under a temporary `PATTERN_0001` identity. This repository preserves its stable registry IDs and absorbs the action-routing responsibilities into `PATTERN_0036`; goal completion, replanning, compensation orchestration, and workflow termination remain outside this cell. / 来源工作流草案以临时 `PATTERN_0001` 标识描述跨单元通用执行器。本仓库保留既有稳定注册表 ID，并将其中行动路由职责吸收到 `PATTERN_0036`；目标完成、重新规划、补偿编排和工作流终止仍位于本单元之外。

## Quick Navigation / 快速导航

- [Boundary / 边界](#boundary--边界)
- [Normative Artifacts / 规范制品](#normative-artifacts--规范制品)
- [Execution Spine / 执行主线](#execution-spine--执行主线)
- [Capability Frontier / 能力前沿](#capability-frontier--能力前沿)
- [Admission / 执行准入](#admission--执行准入)
- [Durable Idempotency / 持久幂等](#durable-idempotency--持久幂等)
- [Execution And Result Certainty / 执行与结果确定性](#execution-and-result-certainty--执行与结果确定性)
- [Events And Projection / 事件与投影](#events-and-projection--事件与投影)
- [Reference API / 参考接口](#reference-api--参考接口)
- [Deployment Boundaries / 部署边界](#deployment-boundaries--部署边界)
- [Acceptance / 验收](#acceptance--验收)

## Boundary / 边界

Keep these responsibilities separate / 保持以下职责分离：

| Component / 组件 | Owns / 负责 | Must not claim / 不得声称 |
| --- | --- | --- |
| Workflow shell / 工作流外壳 | North-star goal, completion criteria, plan versions, recovery, compensation, and termination. / 北极星目标、完成判据、计划版本、恢复、补偿和终止。 | A selected or successful tool means the goal is complete. / 工具被选中或执行成功即代表目标完成。 |
| Capability catalog / 能力目录 | Registered versions, action types, schemas, scopes, side effects, executor, sandbox, and disposition paths. / 注册版本、动作类型、Schema、范围、副作用、执行器、沙箱和处置路径。 | Metadata alone enforces runtime behavior. / 元数据本身已经形成运行时保证。 |
| Frontier builder / 前沿生成器 | Hard-filter the catalog by tenant, identity, stage, side-effect ceiling, and resource scope before semantic selection. / 在语义选择前按租户、身份、阶段、副作用上限和资源范围硬过滤目录。 | Hidden or unauthorized capabilities were safely ignored by the selector. / 选择器会安全忽略已暴露的无权能力。 |
| Candidate selector / 候选选择器 | Choose the best semantic match only inside the sealed frontier. / 只在封存能力前沿中选择最佳语义匹配。 | Semantic selection authorizes execution. / 语义选择已经授权执行。 |
| Admission coordinator / 准入协调器 | Evaluate every execution attempt with the current mechanical and governance state. / 使用当前机械状态与治理状态评估每次执行尝试。 | A prior admission remains valid after parameters, resource versions, approval, or authority changes. / 参数、资源版本、审批或权限变化后旧准入仍有效。 |
| Policy enforcement point / 策略执行点 | Require a sealed allow decision and live authority immediately before entering the real executor. / 真实执行器前要求封存放行决定与实时权限。 | A planner, model, or alternate entry point may bypass the gate. / 计划器、模型或其他入口可以绕过门禁。 |
| Durable action store / 持久行动存储 | Own idempotency identities, execution leases, immutable successful results, result-unknown state, and ordered events. / 管理幂等身份、执行租约、不可变成功结果、结果未知状态和有序事件。 | In-memory counters provide business idempotency. / 内存计数可以提供业务幂等。 |
| Observability projection / 可观测投影 | Reconstruct dispatch facts, calculate registered inputs, and report evidence-backed anomalies. / 重建调度事实、计算已注册输入并报告有证据异常。 | Missing evidence means zero, failure, or no side effect. / 证据缺失等于零、失败或未发生副作用。 |

The dispatcher returns a structured result and a next-action handoff. The outer workflow decides whether to reconcile, wait, retry an explicit failure, replan, compensate, or request human review. / 调度器返回结构化结果与下一动作交接；外层工作流决定核验、等待、对明确失败重试、改计划、补偿或转人工。

## Normative Artifacts / 规范制品

Use these contracts and implementations together / 组合使用以下契约与实现：

- [`tool-dispatch-envelope.schema.json`](../schemas/tool-dispatch-envelope.schema.json): sealed catalog/frontier lineage, candidates, fourteen admission checks, decision, and permit; contains `parameter_hash`, never raw parameters. / 封存目录/前沿血缘、候选、十四项准入检查、决定与许可；只含参数摘要，不含原始参数。
- [`tool-execution-event.schema.json`](../schemas/tool-execution-event.schema.json): strict event identity, per-run sequence, stage, decision, dispatch/frontier/tool/permit/idempotency/lease/result bindings, and result certainty. / 严格事件身份、单运行序号、阶段、决定以及调度/前沿/工具/许可/幂等/租约/结果绑定与结果确定性。
- [`tool-execution-result.schema.json`](../schemas/tool-execution-result.schema.json): sealed rejection, waiting, explicit failure, unknown, partial success, success, or reused success. / 封存拒绝、等待、明确失败、结果未知、部分成功、成功或复用成功。
- [`tool_dispatch.py`](../runtime/tool_dispatch.py): deterministic catalog, frontier, selection, admission, execution boundary, and result normalization. / 确定性目录、前沿、选择、准入、执行边界与结果规范化。
- [`tool_dispatch_sqlite_store.py`](../runtime/tool_dispatch_sqlite_store.py): single-node multi-writer WAL reference for durable leases, immutable-success reuse, and ordered events. / 用于持久租约、成功结果不可变复用和有序事件的单节点多写者 WAL 参考实现。
- [`tool_dispatch_projection.py`](../runtime/tool_dispatch_projection.py): complete-inventory reconstruction, anomaly detection, and registered metric inputs. / 完整清单重建、异常检测和已注册指标输入。
- [`reasoning_artifacts.py`](../runtime/reasoning_artifacts.py): producer-side Schema, hash, cross-binding, and result-certainty guards. / 生产端 Schema、哈希、跨绑定与结果确定性闸门。

Treat the JSON Schemas and executable semantic validators as normative. Markdown examples explain the contract but do not override it. / 以 JSON Schema 与可执行语义校验器为规范；Markdown 示例用于解释，不覆盖契约。

## Execution Spine / 执行主线

```text
Action intent / 行动意图
  ↓
Registered capability catalog / 已注册能力目录
  ↓  hard tenant, identity, stage, side-effect, resource filters
Current capability frontier / 当前能力前沿
  ↓  semantic action-type match and deterministic priority
Selected candidate / 所选候选
  ↓
Fourteen admission checks / 十四项准入检查
  ├── reject / 拒绝 → no executor, structured reason, outer goal judgment
  ├── wait / 等待 → no executor, preserve pending condition
  └── allow / 放行 → sealed time-bounded permit
                         ↓
              live authority recheck / 实时权限复核
                         ↓
              durable idempotency lease / 持久幂等租约
                         ↓
                 real executor / 真实执行器
                         ↓
          result and side-effect certainty / 结果与副作用确定性
                         ↓
        event ledger + workflow handoff / 事件账本与工作流交接
```

Do not persist raw parameters or raw output in the dispatch envelope, action ledger, events, metrics, or traces. Pass raw parameters only across the in-process execution boundary; persist a stable hash and resolvable output or receipt bindings. / 不得在调度信封、行动账本、事件、指标或 Trace 中持久化原始参数或原始输出。原始参数只跨进程内执行边界传递；持久化稳定摘要及可解析输出或回执绑定。

## Capability Frontier / 能力前沿

Build the frontier before semantic matching in this order / 在语义匹配前按以下顺序构建前沿：

1. Remove disabled registrations. / 移除已停用注册项。
2. Enforce tenant scope. / 执行租户范围。
3. Enforce actor scopes. / 执行主体权限范围。
4. Enforce the current workflow stage. / 执行当前工作流阶段。
5. Enforce the action contract's maximum side-effect class. / 执行行动契约最大副作用等级。
6. Enforce target-resource scope. / 执行目标资源范围。
7. Apply the versioned frontier-size limit. / 应用版本化前沿规模上限。
8. Match the action type and rank deterministically. / 匹配动作类型并确定性排序。

The sealed frontier records retained tool bindings and aggregate exclusion counts. It does not expose rejected unauthorized tool identities back to the semantic selector. A tool can be selected only when its binding exists in the retained frontier. / 封存前沿记录保留工具绑定与聚合排除计数，不把被拒绝的无权工具身份暴露回语义选择器；只有绑定存在于保留前沿中的工具才能被选中。

No semantic candidate means rejection to a safe path. Never fabricate a tool name, silently broaden the frontier, or dispatch to a generic write executor. / 没有语义候选时拒绝并进入安全路径；不得虚构工具名、静默扩大前沿或分派到通用写执行器。

## Admission / 执行准入

Run every check for every execution attempt and preserve the fixed order / 每次执行尝试均执行并按固定顺序保留：

| Order / 顺序 | Check / 检查 | Pass basis / 通过依据 | Failure disposition / 未通过处置 |
| --- | --- | --- | --- |
| 1 | `registration` / 注册 | Exact registered tool version exists. / 精确注册工具版本存在。 | Reject. / 拒绝。 |
| 2 | `frontier` / 前沿 | Selected binding is retained in the current sealed frontier. / 所选绑定位于当前封存前沿。 | Reject. / 拒绝。 |
| 3 | `parameters` / 参数 | Raw in-memory parameters pass the selected tool's Draft 2020-12 Schema. / 内存原始参数通过所选工具 Draft 2020-12 Schema。 | Reject with paths, never silently repair. / 携带路径拒绝，不静默修补。 |
| 4 | `identity_scope` / 身份范围 | Scopes match, authority binding is observed, and live verifier returns exact `true`. / 范围匹配、授权绑定已观测且实时验证器精确返回 `true`。 | Reject closed. / 默认阻断。 |
| 5 | `workflow_stage` / 工作流阶段 | Current runtime state is executable. / 当前运行状态允许执行。 | Reject. / 拒绝。 |
| 6 | `dependencies` / 依赖 | All prerequisite nodes are satisfied. / 所有前置节点已满足。 | Wait. / 等待。 |
| 7 | `state_evidence` / 状态证据 | Writes bind exactly the target resources and their current versions. / 写动作精确绑定目标资源及其当前版本。 | Wait to reread on version conflict; reject scope mismatch. / 版本冲突等待重读；范围不符拒绝。 |
| 8 | `budget_quota` / 预算配额 | Current attempt has available budget and quota. / 当前尝试具备预算与配额。 | Reject current attempt. / 拒绝当前尝试。 |
| 9 | `idempotency` / 幂等 | Writes have a stable business key and durable store availability. / 写动作具备稳定业务键与持久存储。 | Reject missing key; wait unavailable store. / 缺键拒绝；存储不可用等待。 |
| 10 | `concurrency` / 并发 | No unresolved target-resource conflict. / 无未解决目标资源冲突。 | Wait. / 等待。 |
| 11 | `approval` / 审批 | Required approval is current and binds parameter hash plus resource-version hash. / 必需审批有效并绑定参数摘要与资源版本摘要。 | Reject denial/drift; wait pending/expired/version change. / 拒绝否决或参数漂移；等待审批、过期或版本变化。 |
| 12 | `risk_environment` / 风险环境 | Declared side effect matches the tool and writes have a controlled runtime binding. / 声明副作用与工具一致，写动作具备受控运行时绑定。 | Reject. / 拒绝。 |
| 13 | `compensation` / 补偿 | Reversible writes have a compensation binding; higher-risk actions have compensation or a manual disposition path. / 可逆写具备补偿绑定；更高风险动作具备补偿或人工处置路径。 | Reject. / 拒绝。 |
| 14 | `observability` / 可观测性 | Hard-gated writes have critical probe readiness. / 硬门控写动作的关键探针已就绪。 | Wait in hard-gate mode; record warning in soft-gate mode. / 硬门控等待；软门控记录告警。 |

Only `allow`, `reject`, and `wait` are valid decisions. Rejected or waiting actions do not enter the executor, acquire a success slot, or consume a completed business action. / 准入结果只允许放行、拒绝与等待；被拒绝或等待的动作不得进入执行器、占用成功名额或消耗已完成业务动作。

Selection and admission remain separate even when the same deterministic component calculates both. The sealed envelope makes the boundary auditable. / 即使由同一确定性组件计算，选择与准入仍保持分离；封存信封使边界可审计。

## Durable Idempotency / 持久幂等

Use one stable business idempotency identity across retries. Bind it to a logical business-action hash that excludes attempt and action-instance IDs while retaining the workflow, goal, action type, parameter hash, target resources, side-effect class, and risk. / 跨重试使用同一稳定业务幂等身份；将其绑定到逻辑业务行动摘要，该摘要排除尝试与行动实例 ID，但保留工作流、目标、动作类型、参数摘要、目标资源、副作用类别和风险。

The reference store applies these rules / 参考存储执行以下规则：

| Stored state / 已存状态 | Acquisition result / 取得结果 | Required next step / 后续要求 |
| --- | --- | --- |
| Missing / 不存在 | Acquire a unique lease and increment revision. / 取得唯一租约并增加修订。 | Execute with the same key. / 携带同一键执行。 |
| `executing` and unexpired / 执行中且未过期 | `busy` / 忙碌 | Wait or query status. / 等待或查询状态。 |
| `executing` and expired / 执行中且已过期 | Persist `unknown`; do not reassign. / 持久化为结果未知；不重新分配。 | Reconcile actual side effect. / 核验真实副作用。 |
| `succeeded` / 已成功 | Return immutable prior result. / 返回不可变原结果。 | Do not call executor. / 不调用执行器。 |
| `unknown` or `partial` / 未知或部分成功 | `verify_unknown` / 核验未知 | Reconcile or compensate; do not retry. / 核验或补偿；不重试。 |
| `explicit_failure` / 明确失败 | Require an authorized new attempt. / 要求已授权的新尝试。 | Revalidate state, approval, and authority before a new lease. / 新租约前重新验证状态、审批与权限。 |
| Same key, different logical action / 同键不同逻辑行动 | Conflict. / 冲突。 | Fail closed and investigate key design. / 默认阻断并检查键设计。 |

Lease tokens are secret execution capabilities. Persist only their hash and a safe lease binding; never place the raw token in events, reports, traces, or health output. / 租约令牌是秘密执行能力；只持久化其摘要与安全租约绑定，绝不把原始令牌放入事件、报告、Trace 或健康输出。

## Execution And Result Certainty / 执行与结果确定性

Recheck live authority and permit expiry immediately before the executor. For writes, require a durable store even if the earlier admission context reported one available. This second enforcement protects against configuration drift and alternate entry points. / 进入执行器前立即复核实时权限与许可过期时间；写动作即使早先准入上下文声明持久存储可用，也必须再次要求真实持久存储，以防配置漂移与旁路入口。

Normalize executor output to one certainty class / 将执行器输出规范为以下确定性类别：

| Classification / 分类 | Meaning / 含义 | Retry rule / 重试规则 |
| --- | --- | --- |
| `success` / 成功 | Executor completed and required side effect or external receipt is confirmed. / 执行器完成且必需副作用或外部回执已确认。 | Reuse immutable result for the same key. / 同键复用不可变结果。 |
| `reused_success` / 复用成功 | Durable store returned the prior success; executor was not called. / 持久存储返回原成功；未调用执行器。 | None. / 无。 |
| `rejected` / 被拒绝 | A gate blocked before execution. / 执行前门禁阻断。 | Replan or correct contract. / 改计划或修正契约。 |
| `explicit_failure` / 明确失败 | Executor ran and absence of write side effect is confirmed. / 执行器运行且已确认未产生写副作用。 | Retry only when policy authorizes a fresh attempt. / 仅策略授权新尝试时重试。 |
| `unknown` / 结果未知 | Request may have reached the target or side effect may exist, but proof is insufficient. / 请求可能已到达目标或副作用可能存在，但证据不足。 | Reconcile first; direct retry is forbidden. / 先核验；禁止直接重试。 |
| `partial_success` / 部分成功 | Only part of a batch or multi-effect action is confirmed. / 批量或多副作用动作只有部分已确认。 | Compensate or transfer to human review. / 补偿或转人工。 |
| `waiting` / 等待 | A condition remains pending without a terminal execution result. / 条件仍待满足，暂无终态执行结果。 | Wait or query. / 等待或查询。 |

An executor exception for a write becomes `unknown`, not explicit failure. A claimed write success without confirmed side-effect evidence becomes `unknown`. An irreversible external success without an external receipt becomes `unknown`. / 写执行器异常必须归为结果未知而非明确失败；写动作声称成功但缺少已确认副作用证据时转为结果未知；不可逆外部动作成功但缺少外部回执时也转为结果未知。

Result success remains local to the executor. The outer workflow still evaluates original completion criteria, forbidden actions, side-effect count, unresolved unknowns, evidence completeness, and compensation debt. / 结果成功只描述执行器局部；外层工作流仍需判断原始完成判据、禁止事项、副作用次数、未解决未知结果、证据完整性与补偿债务。

## Events And Projection / 事件与投影

Persist these lifecycle facts with stable action, attempt, plan, correlation, dispatch, frontier, tool, permit, idempotency, lease, and result bindings / 使用稳定行动、尝试、计划、关联、调度、前沿、工具、许可、幂等、租约与结果绑定持久化以下生命周期事实：

1. `capability_frontier_built`
2. `candidate_selection_completed`
3. `execution_admission_completed`
4. `execution_lease_acquired` when applicable / 适用时
5. `tool_execution_started` only after allow and lease / 仅在放行和租约后
6. exactly one result event / 唯一结果事件
7. `side_effect_confirmed` when evidence exists / 存在证据时

The event store assigns a contiguous per-run sequence and makes `run_id + event_key` idempotent. Reusing an event key with different content fails closed. / 事件存储分配单运行连续序号，并使 `run_id + event_key` 幂等；同一事件键复用于不同内容时默认阻断。

Call `project_tool_dispatch_run(envelopes, results, events)` only with complete bounded inventories. Preserve its projection hash and anomalies. The projection detects orphan events, sequence gaps, incomplete records, execution without allow, frontier escape, write execution without a lease, and duplicate confirmed side effects. / 仅使用完整有界清单调用 `project_tool_dispatch_run(envelopes, results, events)`；保留投影摘要与异常。投影检测孤立事件、序号缺口、记录不完整、未经放行执行、能力前沿逃逸、写执行无租约及重复已确认副作用。

`probe_dependency_matrix.json` describes the outer reasoning runtime mode; it intentionally does not introduce a second `action-routing` execution mode. Resolve probes with the actual outer mode (`direct`, `chain`, `parallel`, or another registered supporting topology) and set the complete condition state for `tool_or_side_effect_action` to `true` so conditional `PROBE_0007` is required. For parallel or delegated actions, use the equivalent registered condition (`branch_action` or `delegated_action`). Missing or `unknown` condition state fails closed. / `probe_dependency_matrix.json` 描述外层推理运行模式，刻意不再引入第二个 `action-routing` 执行模式。应使用真实外层模式（`direct`、`chain`、`parallel` 或其他已注册支撑拓扑）解析探针，并把 `tool_or_side_effect_action` 的完整条件状态设为 `true`，从而要求条件探针 `PROBE_0007`；并行或委派动作使用对应已注册条件（`branch_action` 或 `delegated_action`）。条件状态缺失或为 `unknown` 时默认阻断。

Feed the returned counters to the shared metric registry / 将返回计数输入共享指标注册表：

- `dispatch_admission_coverage`
- `side_effect_lease_coverage`
- `state_evidence_coverage`
- `approval_binding_coverage`
- `frontier_escape_rate`
- `dispatch_record_completeness`
- `result_unknown_rate`
- `duplicate_side_effect_rate`

These ratios remain diagnostic until an accountable owner approves thresholds, minimum samples, drift controls, and promotion evidence. Direct integrity anomalies may still trigger deterministic emergency handling without waiting for a statistical threshold. / 在责任人批准阈值、最小样本、漂移控制与晋升证据前，这些比率保持诊断用途；直接完整性异常仍可在不等待统计阈值的情况下触发确定性紧急处置。

## Reference API / 参考接口

```python
coordinator = ToolDispatchCoordinator(
    capabilities,
    authority_verifier=verify_live_authority,
)
store = SqliteToolDispatchStore("tool-dispatch.sqlite")
runtime = ToolDispatchRuntime(coordinator, store=store)

run = runtime.execute(request, executor)

envelope = run.envelope      # sealed selection + admission / 封存选择与准入
result = run.result          # sealed certainty result / 封存确定性结果
events = run.events          # externally verifiable facts / 外部可核验事实
```

Construct `ToolCapability`, `ActionIntent`, and `DispatchContext` from deterministic workflow state. Do not derive permissions, resource versions, approvals, idempotency identities, or compensation availability from free-form model text. / 从确定性工作流状态构造 `ToolCapability`、`ActionIntent` 与 `DispatchContext`；不得从自由文本模型输出推导权限、资源版本、审批、幂等身份或补偿可用性。

For delayed execution, reconstruct current state and prepare a new envelope rather than reusing an expired permit. For retry, create a new attempt and action identity with the prior action as parent while preserving the stable business idempotency key. / 延迟执行时应重建当前状态并准备新信封，不复用已过期许可；重试时创建新的尝试与行动身份，以原行动为父，同时保留稳定业务幂等键。

## Deployment Boundaries / 部署边界

`SqliteToolDispatchStore` is a local single-node reference. It uses WAL, `BEGIN IMMEDIATE`, uniqueness constraints, secret-token hashing, immutable-success reuse, and bounded health output. It is appropriate for local integration, tests, and a single host with multiple writers. / `SqliteToolDispatchStore` 是本地单节点参考实现，使用 WAL、`BEGIN IMMEDIATE`、唯一约束、秘密令牌哈希、成功结果不可变复用和有界健康输出，适用于本地集成、测试及单主机多写者。

Horizontal or remote writers require a network database adapter with equivalent / 水平或远程写者需要具备以下等价语义的网络数据库适配器：

- transaction serialization or compare-and-set ownership / 事务串行化或比较交换所有权；
- unique idempotency identity and immutable successful result / 唯一幂等身份与不可变成功结果；
- lease fencing and expiry-to-unknown behavior / 租约栅栏与过期转未知行为；
- atomic ordered event append / 原子有序事件追加；
- schema migration and unknown-version rejection / Schema 迁移与未知版本拒绝；
- credentials, TLS, least privilege, retention, backup/restore, failover, and disaster-recovery drills / 凭据、TLS、最小权限、保留、备份恢复、故障切换与灾备演练。

Do not claim end-to-end exactly-once execution. The reference prevents duplicate entry through its own boundary; external systems must also consume the same stable idempotency identity or provide a queryable business receipt. / 不得声称端到端严格一次执行；本参考只能防止自身边界重复进入，外部系统也必须消费同一稳定幂等身份或提供可查询业务回执。

Store health proves mechanics only. It does not prove correct capability metadata, trustworthy live authorization, correct business state, external side-effect truth, or goal completion. / 存储健康只证明机械能力，不证明能力元数据正确、实时授权可信、业务状态正确、外部副作用真实或目标完成。

## Acceptance / 验收

Minimum behavioral acceptance / 最小行为验收：

- Unauthorized capabilities are removed before semantic selection and are not named in the frontier. / 无权能力在语义选择前被移除，且不在前沿中点名。
- Unknown action types reject safely without guessing a tool. / 未知动作类型安全拒绝，不猜测工具。
- Parameter Schema failure and live-authorization failure block execution. / 参数 Schema 失败与实时授权失败阻断执行。
- Every envelope contains exactly fourteen ordered admission checks. / 每个信封恰含十四项有序准入检查。
- A selected tool cannot execute outside the sealed frontier. / 所选工具不能在封存能力前沿之外执行。
- Writes require exact target-resource version evidence, a stable idempotency key, a durable store, a controlled runtime binding, and a compensation or manual disposition path. / 写动作要求精确目标资源版本证据、稳定幂等键、持久存储、受控运行时绑定以及补偿或人工处置路径。
- Approval-required writes bind approval to the current parameter and resource-version hashes. / 需要审批的写动作将审批绑定当前参数与资源版本摘要。
- The executor is never called for reject, wait, busy, prior success, or unresolved unknown result. / 拒绝、等待、忙碌、已有成功或未解决未知结果时不调用执行器。
- The same business key produces at most one executor success through the reference boundary and reuses the immutable result. / 同一业务键通过参考边界至多产生一次执行器成功，并复用不可变结果。
- Write timeout or process uncertainty becomes result-unknown and cannot be directly retried. / 写超时或进程不确定性转为结果未知且不可直接重试。
- Raw parameters, raw outputs, idempotency keys, and lease tokens do not enter persisted artifacts. / 原始参数、原始输出、幂等键与租约令牌不进入持久化制品。
- Events are hash-valid, correlatable, idempotent by key, and contiguous per run. / 事件哈希有效、可关联、按键幂等且单运行连续。
- Projection-derived metric inputs and direct anomalies are reproducible from complete inventories. / 投影指标输入与直接异常可从完整清单复现。

Verification commands / 验证命令：

```text
python -m pytest tests/test_tool_dispatch.py tests/test_tool_dispatch_sqlite_store.py tests/test_tool_dispatch_projection.py -q
python skills/harness-engineering-patterns/scripts/validate_harness_skill.py skills/harness-engineering-patterns
python -m pytest -q
```
