# Reasoning Execution Flow / 推理执行流程

Pattern ID / 模式 ID: `PATTERN_0051`

Version / 版本: `0.2.0`

Status / 状态: Draft / 草案
Related pattern / 关联模式: `PATTERN_0052` Workflow Observability Probes / 工作流可观测性探针

This reference defines a shortest-sufficient, verifiable, stoppable, and auditable execution protocol for agent reasoning. It is a cross-cutting runtime protocol, not a replacement for any single cognition x topology cell. / 本参考定义一套最短充分、可验证、可停止、可审计的智能体推理执行协议。它是跨交织点的运行协议，不替代任一认知 x 拓扑单元。

Compatibility note / 兼容说明: the source draft used `PATTERN_0001`, which is already the stable registry ID for Main Loop Progression / 主循环推进模式. Preserve that historical ID and register this protocol as `PATTERN_0051`; do not rewrite existing Trace or registry records. / 来源草案使用了 `PATTERN_0001`，但该稳定 ID 已分配给主循环推进模式。应保留历史 ID，并将本协议登记为 `PATTERN_0051`；不得改写既有 Trace 或注册表记录。

## Quick Navigation / 快速导航

- [Scope And Invariants / 范围与不变量](#scope-and-invariants--范围与不变量)
- [Cognition And Topology Mounts / 认知与拓扑挂载](#cognition-and-topology-mounts--认知与拓扑挂载)
- [Identity And Input Contract / 标识与输入契约](#identity-and-input-contract--标识与输入契约)
- [Machine-Readable Contracts / 机器可读契约](#machine-readable-contracts--机器可读契约)
- [Reasoning Contract / 推理契约](#reasoning-contract--推理契约)
- [State Machine And Main Flow / 状态机与主流程](#state-machine-and-main-flow--状态机与主流程)
- [Routing And Execution Modes / 路由与执行模式](#routing-and-execution-modes--路由与执行模式)
- [Validation, Switching, And Stopping / 验证、换路与停止](#validation-switching-and-stopping--验证换路与停止)
- [Standalone And Interactive Operation / 独立与交互运行](#standalone-and-interactive-operation--独立与交互运行)
- [Output And Acceptance / 输出与验收](#output-and-acceptance--输出与验收)

## Scope And Invariants / 范围与不变量

Use the protocol for fact and rule queries, evidence comparison, risk decisions, root-cause investigation, code repair, multi-tool or multi-agent work, and workflows requiring review or audit. Prefer a deterministic program when inputs, rules, and outputs are fully fixed, or when policy reserves the final decision for a human. / 将本协议用于事实与规则查询、证据比较、风险判断、根因调查、代码修复、多工具或多智能体工作，以及需要复核或审计的流程。输入、规则和输出完全确定，或策略规定必须由人工最终决定时，优先使用确定性程序。

Enforce these invariants / 强制以下不变量:

1. Route before deep reasoning; never default every task to the heaviest path. / 先路由再深推理；不得让所有任务默认进入最重路径。
2. Separate evidence (what was observed) from decisions (what was concluded or chosen). / 分离证据（观察到什么）与决定（据此得出或选择什么）。
3. Prefer deterministic checks, tests, external data, execution results, or authorized human review over model self-confidence. / 确定性检查、测试、外部数据、执行结果或有权限的人工复核优先于模型自信度。
4. Treat token, latency, model-call, tool-call, branch, iteration, retry, and cost limits as a contract. / 将令牌、延迟、模型调用、工具调用、分支、迭代、重试和成本上限视为契约。
5. Record externally verifiable decision events only. Never request, store, or expose private chain-of-thought. / 只记录外部可核验的决策事件；不得要求、保存或暴露私密思维过程。
6. Define evidence sufficiency, stop, and escalation conditions before execution. / 执行前定义证据充分、停止与升级条件。
7. Version goals, hard constraints, and verified facts; revise them only with reason, evidence, impact, and approver. / 对目标、硬约束和已验证事实做版本管理；只有记录原因、证据、影响与批准者后才能修订。
8. A candidate conclusion is never a completed result until all mandatory validators, evidence-sufficiency checks over the release-bound public claims, and terminal-state checks pass. / 候选结论只有在针对放行绑定的公开声明通过全部必选验证器、证据充分性检查和终态检查后，才能成为完成结果。

## Cognition And Topology Mounts / 认知与拓扑挂载

Reasoning is the primary cognition. Perception supplies observations, memory retains snapshots and events, action executes authorized probes or tools, reflection validates and repairs, and governance controls permission, risk, privacy, audit, and escalation. / 推理是主要认知；感知提供观察，记忆保留快照与事件，行动执行有权限的探测或工具，反思负责验证与修复，治理控制权限、风险、隐私、审计和升级。

| Runtime responsibility / 运行职责 | Matrix mount / 矩阵挂载 |
| --- | --- |
| Select direct, chain, parallel, or iterative execution. / 选择直接、链式、并行或迭代执行。 | `COG_REASONING__TOP_ROUTING` |
| Execute ordered verifiable subclaims. / 执行有序可验证子命题。 | `COG_REASONING__TOP_CHAIN` |
| Compare materially different candidate paths. / 比较实质不同的候选路径。 | `COG_REASONING__TOP_PARALLEL` |
| Coordinate contract, state, tools, validators, events, and feedback; supporting role only while the cell remains an extension candidate. / 协调契约、状态、工具、验证器、事件和反馈；单元仍为扩展候选时只作支撑角色。 | `COG_REASONING__TOP_ORCHESTRATION` |
| Revise hypotheses from new observations until an explicit exit. / 根据新观察修订假设直至显式退出。 | `COG_REASONING__TOP_LOOP` |
| Propagate authority, risk limits, approval, and parent-child accountability. / 传播权限、风险上限、审批和父子问责。 | `COG_GOVERNANCE__TOP_HIERARCHY` |

The protocol may use hierarchy for multi-agent decomposition, but the source draft does not by itself promote `COG_REASONING__TOP_HIERARCHY`; keep that cell as an extension candidate until repeated independent evidence satisfies promotion rules. / 协议可以在多智能体拆解中使用层级，但来源草案本身不会晋升 `COG_REASONING__TOP_HIERARCHY`；在反复独立证据满足晋升规则前，该单元保持扩展候选。

## Identity And Input Contract / 标识与输入契约

### Stable identities / 稳定标识

| Identity / 标识 | Rule / 规则 |
| --- | --- |
| `task_id` / 任务标识 | Stable across retries and reruns of the same business request. / 同一业务请求的重试与重跑保持稳定。 |
| `run_id` / 运行标识 | New for every execution or rerun. / 每次执行或重跑新建。 |
| `step_id` / 步骤标识 | New for every closable work unit. / 每个可关闭工作单元新建。 |
| `event_id` / 事件标识 | Unique for every emitted event. / 每条事件唯一。 |
| `parent_event_id` / 父事件标识 | Required for cross-system calls, parallel branches, and child tasks. / 跨系统调用、并行分支和子任务必填。 |
| `candidate_path_id` / 候选路径标识 | Required for every parallel candidate. / 每条并行候选必填。 |
| `evidence_id` / 证据标识 | Identifies evidence plus version, time, and source. / 标识证据及其版本、时间和来源。 |
| `verification_id` / 验证标识 | Identifies one validation action and result. / 标识一次验证动作及结果。 |
| `attempt_id` / 尝试标识 | New for every attempt of one logical step or action. / 同一逻辑步骤或动作的每次尝试新建。 |
| `idempotency_key` / 幂等键 | Stable for retries of one logical side effect; duplicate keys must not repeat the effect. / 同一逻辑副作用的重试保持稳定；重复键不得重复执行副作用。 |
| `causation_id` / 因果标识 | Identifies the command or event that caused the current event. / 标识导致当前事件的命令或事件。 |
| `transition_id` / 转换标识 | Identifies one guarded state transition. / 标识一次受门控的状态转换。 |
| `tool_call_id` / 工具调用标识 | Links request, response, retry, receipt, and compensation for one logical call. / 关联一次逻辑调用的请求、响应、重试、回执和补偿。 |
| `human_work_id` / 人工工作标识 | Links escalation, approval, expiry, resumption, and outcome. / 关联升级、审批、过期、恢复和结果。 |

Every event carries non-null `workflow_id`, `task_id`, and `run_id`. The contract and final result carry the same identity chain plus `scene_id`. The `step_id` field is present but may be `null` for run-level events; it becomes non-null for step and action events. Parallel, multi-agent, and cross-system child events require a non-null `parent_event_id`. / 每条事件都携带非空 `workflow_id`、`task_id` 与 `run_id`；契约和最终结果携带相同标识链以及 `scene_id`。`step_id` 字段始终存在，但运行级事件可为 `null`；步骤与动作事件必须为非空。并行、多智能体和跨系统子事件要求非空 `parent_event_id`。

### Normalized input / 标准化输入

```yaml
schema_version: 1.0.0
normalized_input_id: INPUT_EXAMPLE
normalized_input_version: 1.0.0
normalized_input_hash: sha256:0000000000000000000000000000000000000000000000000000000000000000
workflow_id: WORKFLOW_EXAMPLE
request_id: REQUEST_EXAMPLE
received_at: "2026-07-15T09:00:00Z"
request:
  content_state: {state: observed, value: "validate the candidate / 验证候选结果"}
  language: zh-CN
  channel: api
task:
  task_type: verification
  objectives:
    - objective_id: OBJECTIVE_VALIDATED_RESULT
      description: "produce an evidence-backed result / 生成有证据支撑的结果"
      priority: required
  constraints: []
  expected_output: {format: json, must_include_evidence: true, locale: zh-CN}
risk:
  level: medium
  dimensions: [operational]
  reversibility: reversible
  requires_human_review: false
reasoning_context:
  known_facts: {state: observed, items: []}
  assumptions: {state: observed, items: []}
  claims_to_verify:
    state: observed
    items:
      - claim_id: CLAIM_VALID
        statement: {state: observed, value: "candidate passes deterministic validation / 候选通过确定性验证"}
        criticality: critical
        required_evidence_types: [test]
  preferences: {state: observed, items: []}
  evidence_requirement:
    state: observed
    value:
      required_evidence_types: [test]
      min_independent_sources: 1
      max_source_age_seconds: 3600
      min_integrity_score: 0.95
      unknown_source_policy: reject
  deadline: {state: unknown}
permission_context:
  actor:
    state: observed
    value: {actor_id: AGENT_EXAMPLE, actor_type: agent, actor_version: 1.0.0}
  grant:
    state: observed
    value:
      id: GRANT_EXAMPLE
      version: 1.0.0
      hash: sha256:1111111111111111111111111111111111111111111111111111111111111111
  allowed_actions: {state: observed, items: [read, validate]}
  resource_scope: {state: observed, items: [workspace:reasoning]}
  expires_at: {state: unknown}
available_capabilities:
  - capability_id: VALIDATOR_EXAMPLE
    kind: validator
    availability: available
    version: 1.0.0
field_provenance:
  - field_path: /request/content_state
    source_type: user
    source_ref: REQUEST_EXAMPLE
    observed_at: "2026-07-15T09:00:00Z"
    integrity_hash: sha256:2222222222222222222222222222222222222222222222222222222222222222
    value_state: observed
```

Before routing, turn vague goals into verifiable targets, separate facts from assumptions and preferences, mark missing critical facts, verify permissions and reversibility, assign mandatory validators for high-risk work, and create versioned snapshots of goals, constraints, and verified facts. / 路由前，将模糊目标改写为可验证目标，分离事实、假设与偏好，标记关键事实缺失，确认权限和可逆性，为高风险工作指定必选验证器，并建立目标、约束与已验证事实的版本快照。

## Machine-Readable Contracts / 机器可读契约

The normative Draft 2020-12 schemas are [Normalized Input](../schemas/normalized-input.schema.json), [Reasoning Contract](../schemas/reasoning-contract.schema.json), [Reasoning Event](../schemas/reasoning-event.schema.json), and [Reasoning Result](../schemas/reasoning-result.schema.json). Markdown examples are explanatory views; schemas and conformance tests own field types, enums, conditional requirements, null semantics, and compatibility. / 规范性的 Draft 2020-12 Schema 为[标准化输入](../schemas/normalized-input.schema.json)、[推理契约](../schemas/reasoning-contract.schema.json)、[推理事件](../schemas/reasoning-event.schema.json)和[推理结果](../schemas/reasoning-result.schema.json)。Markdown 示例是解释视图；字段类型、枚举、条件必填、空值语义和兼容性以 Schema 与一致性测试为准。

Use schema major version `1` for this protocol generation. Unknown fields are rejected unless a versioned extension namespace explicitly permits them. Producers may add backward-compatible optional fields within a minor version; removing fields, changing meaning, tightening required fields, or changing enums requires a new major version and migration tests. / 本代协议使用 Schema 主版本 `1`。除非版本化扩展命名空间明确允许，否则拒绝未知字段。同一小版本内可增加向后兼容的可选字段；删除字段、改变语义、收紧必填或修改枚举必须升级主版本并提供迁移测试。

Every `sha256:` digest is computed from UTF-8 canonical JSON with lexicographically sorted object keys, no insignificant whitespace, finite JSON numbers only, and the artifact's own hash field omitted. Array order remains significant unless the field definition explicitly declares set semantics. The producer must reject a supplied digest that does not match the recomputed value. / 每个 `sha256:` 摘要均基于 UTF-8 规范 JSON 计算：对象键按字典序排列、去除无意义空白、仅允许有限 JSON 数值，并排除制品自身的哈希字段。除非字段定义明确声明集合语义，否则数组顺序具有意义。生产者必须拒绝与重算值不一致的外部摘要。

The repeated zero-to-five digests in the Markdown snippets are format-only placeholders and are not executable sample values. Producers must use [`reasoning_artifacts.py`](../runtime/reasoning_artifacts.py) to seal and validate normalized input, contract, and result artifacts, or implement byte-for-byte equivalent canonicalization, hash, Schema, and semantic checks. / Markdown 片段中重复的零至五摘要只用于展示格式，不是可执行样例值。生产者必须使用 [`reasoning_artifacts.py`](../runtime/reasoning_artifacts.py) 封存并校验标准化输入、契约和结果制品，或实现逐字节等价的规范化、哈希、Schema 与语义检查。

An evidence object binds `evidence_id`, retrievable source or URI, source version, content digest, valid and retrieval times, scope, freshness, integrity, privacy/redaction, transformation history, and its `supports`, `refutes`, or `neutral` relation to a named claim. Claim-to-evidence and evidence-to-claim bindings are reciprocal; only a bound `supports` relation counts toward supported-claim coverage. A validation result binds the content fingerprints of the exact normative validator and pass criteria, candidate fingerprint, contract version, ordered evidence fingerprints, independence class, start/end time, timeout/retry, result, obligations, actor, and authority. A passing human validation requires observed actor and authority bindings. A changed bound input invalidates the old result rather than mutating it. / 证据对象绑定证据标识、可取回来源或 URI、来源版本、内容摘要、有效与获取时间、范围、新鲜度、完整性、隐私/脱敏、转换历史，以及它与命名主张之间的支持、反驳或中立关系。声明到证据与证据到声明的绑定必须双向闭合；只有已绑定的 `supports` 关系计入已支持声明覆盖率。验证结果绑定完整规范验证器与通过准则的内容指纹、候选指纹、契约版本、有序证据指纹、独立性类别、起止时间、超时/重试、结果、义务、执行者和权限。人工验证通过必须记录可观测的执行人与权限绑定。任何绑定输入变化都会使旧结果失效，而不是修改旧结果。

## Reasoning Contract / 推理契约

Create and version this contract before formal execution. Any change must record actor, reason, evidence, impact, and new version. / 正式执行前创建并版本化此契约。任何变更必须记录变更者、原因、证据、影响和新版本。

```yaml
schema_version: 1.0.0
contract_id: CONTRACT_XXXX
contract_version: 1.0.0
contract_hash: sha256:0000000000000000000000000000000000000000000000000000000000000000
workflow_id: WORKFLOW_XXXX
task_id: TASK_XXXX
run_id: RUN_XXXX
scene_id: SCENE_XXXX
normalized_input_binding:
  id: INPUT_XXXX
  version: 1.0.0
  hash: sha256:1111111111111111111111111111111111111111111111111111111111111111
created_at: "2026-07-15T09:00:00Z"
routing_decision:
  decision_id: ROUTE_EXAMPLE
  policy_binding:
    id: ROUTING_POLICY_EXAMPLE
    version: 1.0.0
    hash: sha256:2222222222222222222222222222222222222222222222222222222222222222
  disposition: execute
  signals:
    - signal: complexity
      value: {state: observed, value: high}
    - signal: external_verifiability
      value: {state: observed, value: available}
  reasons:
    - reason_code: multi_step_dependency
      source_binding: {state: not_applicable}
    - reason_code: external_validation_required
      source_binding: {state: not_applicable}
  selected_configuration:
    execution_mode: chain
    reasoning_depth: deliberative
    primary_topology: chain
    supporting_topologies: [orchestration]
  signal_fingerprint: sha256:5555555555555555555555555555555555555555555555555555555555555555
  missing_signals: []
  abstained: false
snapshot_versions: {goal: 1, constraints: 1, verified_facts: 1}
execution_mode: chain
reasoning_depth: deliberative
primary_topology: chain
supporting_topologies: [orchestration]
budget:
  max_reasoning_tokens: 8000
  max_latency_ms: 12000
  max_model_calls: 4
  max_tool_calls: 8
  max_parallel_paths: 3
  max_iterations: 6
  max_retries: 2
  max_total_cost_units: null
  cost_unit: compute_credit
  enforcement: hard
  parallel_reservation_policy: reserve_before_launch
  on_exhaustion: escalate
validators:
  - validator_id: VALIDATOR_XXXX
    validator_version: 1.0.0
    validator_type: deterministic
    required: true
    applicability:
      aggregation: all
      predicates: []
    pass_criteria:
      aggregation: all
      checks:
        - check_id: CHECK_XXXX
          predicate:
            field_path: /candidate/verified
            operator: eq
            expected: true
          severity: fatal
          weight: 1.0
    timeout_ms: 3000
    on_error: fail_closed
evidence_sufficiency:
  min_independent_sources: 1
  required_evidence_types: [test]
  max_source_age_seconds: 3600
  min_integrity_score: 0.95
  min_claim_coverage_ratio: 1.0
  max_unresolved_critical_claims: 0
  unknown_source_policy: reject
stop_conditions:
  - condition_id: STOP_VALIDATED
    type: validated_success
    on_trigger: complete
  - condition_id: STOP_NO_PROGRESS
    type: no_progress
    consecutive_steps: 2
    min_information_gain: 0.01
    on_trigger: escalate
escalation_conditions:
  - condition_id: ESCALATE_EVIDENCE
    trigger: insufficient_evidence
    severity: error
    action: request_evidence
allowed_mode_switches:
  - switch_id: SWITCH_PARALLEL
    from:
      execution_mode: chain
      reasoning_depth: deliberative
      primary_topology: chain
      supporting_topologies: [orchestration]
    to:
      execution_mode: parallel
      reasoning_depth: deliberative
      primary_topology: parallel
      supporting_topologies: [orchestration]
    trigger: conflicting_evidence
    max_switches: 1
    preserve_budget: true
    requires_validation: true
governance:
  risk_level: medium
  validator_failure_policy: fail_closed
  probe_failure_policy: degrade_and_alert
  human_review_required: false
```

`direct_release_rule` is optional and valid only for low-risk, reversible work under a deterministic versioned policy. It is not model confidence and cannot exempt high or critical risk, irreversible actions, missing permissions, unknown rule versions, or conflicting evidence. When absent, direct mode still uses the mandatory validator gate. / `direct_release_rule` 为可选项，只适用于确定性版本化策略下的低风险、可逆工作。它不等于模型置信度，也不能豁免高风险或极高风险、不可逆动作、权限缺失、规则版本未知或证据冲突。未配置时，直接模式仍必须经过必选验证闸门。

Default budget profiles are starting points, not universal thresholds. Scene configuration owns overrides. / 默认预算档位只是起点，不是通用阈值；场景配置负责覆盖。

| Profile / 档位 | Reasoning tokens / 推理令牌 | Latency / 延迟 | Model calls / 模型调用 | Tool calls / 工具调用 | Paths / 路径 | Iterations / 轮次 | Typical use / 常见用途 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| light / 轻量 | 2,000 | 3 s | 1 | 2 | 1 | 1 | Lookup and stable rules / 查询与稳定规则 |
| standard / 标准 | 8,000 | 12 s | 4 | 8 | 3 | 6 | Evidence checks and ordinary investigation / 证据核对与一般调查 |
| deep / 深入 | 24,000 | 60 s | 12 | 24 | 5 | 12 | High-value research and complex diagnosis / 高价值研究与复杂诊断 |
| controlled-high-risk / 受控高风险 | 12,000 | 30 s | 6 | 12 | 3 | 8 | Approval or irreversible action with independent release gate / 带独立放行闸门的审批或不可逆动作 |

All configured numeric limits are positive; zero or a negative value is invalid. `null` means that a dimension is explicitly unconfigured, not unlimited and not zero, and must retain its value state; positive consumption against an unconfigured dimension fails closed until an authorized contract revision configures it. Retries and resumed attempts consume the same run budget. Parallel and child work reserve budget atomically before dispatch; unused reservations may be released, while observed spend is never refunded. The sum of active child reservations plus parent spend cannot exceed the parent limit. Charge latency with a monotonic clock and record approved human-wait suspension separately. Each cost unit has a scene-owned unit and version. / 所有已配置数值上限必须为正数，零或负数非法。`null` 表示该维度明确未配置，不表示无限或零，并且必须保留其值状态；在未配置维度上发生正消费时默认阻断，直至通过有权限的契约修订配置该维度。重试与恢复尝试消耗同一运行预算。并行与子任务在分派前原子预留预算；未使用预留可释放，但已观测消耗不得退款。活动子任务预留与父任务已消耗之和不得超过父级上限。延迟使用单调时钟计量，并单独记录经批准的人工等待暂停。每个成本单位都由场景定义单位和版本。

## State Machine And Main Flow / 状态机与主流程

```text
received / 已接收
  -> normalized / 已标准化
  -> governance_precheck / 治理预检
       -> rejected / 已拒绝
       -> escalated / 已升级
       -> routed / 已路由
  routed -> contract_established / 契约已建立
  -> executing / 执行中
       -> waiting_for_evidence -> executing / 等待证据后恢复执行
       -> waiting_for_evidence -> timed_out | escalated | cancelled / 等待超时、升级或取消
       -> mode_switched -> executing / 换路后继续执行
       -> candidate_ready / 候选已形成
       -> failed | escalated | cancelled | timed_out / 失败、升级、取消或超时
  candidate_ready -> validating / 验证中
       -> completed / 已完成
       -> repairable_failure -> executing / 可修复失败后继续执行
       -> failed | escalated | cancelled | timed_out / 失败、升级、取消或超时
```

Every terminal state must contain a reason. Use `completed` only after validation or an explicitly configured low-risk direct condition and after the final public claim set passes the contractual evidence-sufficiency gate. Persist the authoritative gate evaluation time and reject validations after that time or a result `created_at` before it. Use `escalated` at an authority boundary; use `rejected` for governance denial; use `failed` when the authorized budget cannot finish and no escalation path exists; use `cancelled` only for explicit cancellation or invalidated input. / 每个终态都必须包含原因。只有验证通过或明确配置的低风险直接条件满足，并且最终公开声明集合通过契约证据充分性门后，才能使用 `completed`。必须持久化权威放行门评估时间，并拒绝晚于该时间的验证或早于该时间的结果 `created_at`。到达责任边界时使用 `escalated`；治理不允许时使用 `rejected`；授权预算内无法完成且没有升级通道时使用 `failed`；仅在外部明确取消或输入失效时使用 `cancelled`。

`workflow_state` is business execution state. `event_processing_status` is only whether an event was `accepted`, detected as `duplicate`, or `rejected`; never use it as the workflow result. Every transition records `transition_id`, previous and next state, guard results, actor, reason, contract version, sequence, attempt, causation, and idempotency key. Illegal transitions are rejected without mutating state. State mutation and event append must be atomic or use a transactional outbox. / `workflow_state` 表示业务执行状态；`event_processing_status` 只表示事件被接受、识别为重复或被拒绝，绝不能替代工作流结果。每次转换记录转换标识、前后状态、门控结果、执行者、原因、契约版本、序号、尝试、因果关系和幂等键。非法转换必须在不修改状态的情况下拒绝。状态修改与事件追加必须原子完成，或使用事务 outbox。

The reference transition table and replay behavior are executable in [`reasoning_runtime.py`](../runtime/reasoning_runtime.py). Crash recovery replays accepted events in sequence; duplicate idempotency keys return the original event; late tool results are recorded but cannot mutate a terminal run without an explicit new run or authorized compensation command. / 参考转换表与回放行为在 [`reasoning_runtime.py`](../runtime/reasoning_runtime.py) 中可执行。崩溃恢复按序回放已接受事件；重复幂等键返回原事件；迟到工具结果可以记录，但不得修改已终止运行，除非显式创建新运行或执行有权限的补偿命令。

Cancellation stops new dispatch, propagates to active child work, and marks in-flight side effects for result reconciliation or authorized compensation. A child cannot widen parent authority, budget, retention, or hard constraints; parent synthesis owns conflict preservation and final validation. / 取消会阻止新分派、传播到活动子任务，并将执行中的副作用标记为待结果核对或有权限补偿。子任务不得扩大父级权限、预算、留存或硬约束；父级综合负责保留冲突并承担最终验证责任。

Execute the control flow in this order / 按以下顺序执行控制流:

1. Receive and normalize: generate identities; extract goal, scope, facts, claims, constraints, risk, and output shape; create snapshots. / 接收并标准化：生成标识，抽取目标、范围、事实、主张、约束、风险和输出结构，建立快照。
2. Governance precheck: verify access, sensitive data, irreversibility, required approval, prohibited actions, redaction, and review policy. Before every side effect, revalidate that an unexpired grant is bound to the exact tool and version, parameter fingerprint, resource scope, action, contract version, and attempt; record dry-run or compensation receipts when required. / 治理预检：检查访问权限、敏感数据、不可逆性、必需审批、禁止动作、脱敏和复核策略。每次副作用前重新校验未过期授权是否绑定到确切的工具及版本、参数指纹、资源范围、动作、契约版本和尝试；需要时记录试运行或补偿回执。
3. Assess evidence: classify it as complete-consistent, mostly complete, conflicting, insufficient, unavailable, or untrusted. / 评估证据：分类为完整一致、基本完整、冲突、不足、不可取得或不可信。
4. Route by observable complexity and hard gates. / 根据可观测复杂度与硬门槛路由。
5. Establish the reasoning contract. / 建立推理契约。
6. Execute one closable step at a time; record claim, evidence, action, observation, local decision, and resource use. / 每次执行一个可关闭步骤，记录命题、证据、动作、观察、局部决定和资源消耗。
7. Validate the candidate with mandatory validators; freeze the externally auditable claim set used for release. / 使用必选验证器验证候选结论，并冻结用于放行的外部可审计声明集合。
8. Recompute evidence sufficiency at the authoritative gate time, then apply stop, switch, repair, reject, or escalation rules. / 在权威放行门时间重算证据充分性，再应用停止、换路、修复、拒绝或升级规则。
9. Emit a final result whose claims exactly match the release-bound set and that separates facts, inferences, decisions, unresolved items, limitations, and next actions. / 输出声明与放行绑定集合完全一致的最终结果，并分离事实、推断、决定、未解决项、限制与后续动作。

## Routing And Execution Modes / 路由与执行模式

Represent routing on separate axes. `reasoning_depth` is `direct` or `deliberative`; `execution_mode` is the runtime strategy `direct`, `chain`, `parallel`, or `iterative`; `primary_topology` is `null`, `chain`, `parallel`, or `loop`; `supporting_topologies` may contain `orchestration` and `hierarchy`. Preserve a `mode_stack` for composites such as route -> parallel -> per-branch iterative -> chain synthesis. Never force orchestration or hierarchy into the single current-mode field. / 分轴表示路由。`reasoning_depth` 为直接或深思；`execution_mode` 为直接、链式、并行或迭代运行策略；`primary_topology` 为无、链式、并行或循环；`supporting_topologies` 可包含编排和层级。组合流程应保留 `mode_stack`，例如“路由 -> 并行 -> 分支内迭代 -> 链式综合”。不得把编排或层级强塞进单一当前模式字段。

Canonical execution-mode set / 规范执行模式集合: `direct | chain | parallel | iterative`.

### Routing signals and hard gates / 路由信号与硬门槛

Use intent complexity, evidence state, mechanism uncertainty, action risk, and environment observability. / 使用意图复杂度、证据状态、机制不确定性、动作风险和环境可观测性五类信号。

Every scene owns a versioned `route_policy_id`, signal schema, precedence, thresholds, abstention behavior, and under-route versus over-route cost. Apply governance denial and irreversible-action gates first; then prefer iterative when evidence requires interaction, parallel when material rivals exist, chain for one dominant dependency path, and direct only for complete evidence, stable rules, and low risk. Missing required signals cause abstention or a safer configured route, never an invented low-risk value. / 每个场景负责版本化的路由策略标识、信号 Schema、优先级、阈值、弃权行为和欠路由/过路由成本。先执行治理拒绝和不可逆动作门槛；随后，需交互补证时优先迭代，存在实质竞争解释时优先并行，只有一条主导依赖路径时使用链式，仅在证据完整、规则稳定且低风险时直接处理。必需信号缺失时应弃权或走已配置的更安全路由，绝不能编造低风险值。

[`reasoning_router.py`](../runtime/reasoning_router.py) is the deterministic reference policy. It intentionally has no confidence input: low-confidence adapters may mark a signal missing or mechanism uncertainty high, but no confidence value can release work. / [`reasoning_router.py`](../runtime/reasoning_router.py) 是确定性参考策略。其接口刻意不包含置信度：低置信适配器可以把信号标为缺失或把机制不确定性标为高，但任何置信度值都不能直接放行任务。

| Condition / 条件 | Route / 路由 |
| --- | --- |
| No permission, prohibited action, or governance denial / 无权限、动作被禁止或治理不允许 | Reject / 拒绝 |
| High, critical, or irreversible action without strong validation / 高风险、极高风险或不可逆动作缺少强验证 | Human escalation / 人工升级 |
| Stable rule, complete evidence, low risk / 规则稳定、证据完整、风险低 | Direct / 直接处理 |
| One dominant dependency path with checkable subclaims / 一条主导依赖路径且子命题可核验 | Chain / 链式分解 |
| Several plausible explanations, versions, policies, or plans / 多个解释、版本、口径或计划均可能成立 | Parallel / 并行探索 |
| New evidence appears only after action or probing / 只有行动或探测后才能获得新证据 | Iterative / 迭代验证 |

### Mode contracts / 模式契约

| Mode / 模式 | Entry / 进入条件 | Required work / 必需动作 | Required artifact / 必需产物 | Exit / 退出条件 |
| --- | --- | --- | --- | --- |
| direct / 直接处理 | Single clear goal, complete evidence, stable rule, low risk. / 单一明确目标、证据完整、规则稳定、风险低。 | Confirm source or rule version; run one query, calculation, or match; perform a minimal consistency check. / 确认来源或规则版本；执行一次查询、计算或匹配；做最小一致性检查。 | Evidence or rule refs, decision, validation state, stop reason. / 证据或规则引用、决定、验证状态、停止原因。 | Escalate on conflict, unknown version, high-risk effect, or need for more evidence. / 证据冲突、版本不明、高风险影响或需继续补证时升级。 |
| chain / 链式分解 | One dominant path with ordered, verifiable subclaims. / 存在带顺序依赖、可验证子命题的主导路径。 | Split into non-overlapping sufficient subproblems; define evidence and local pass criteria; checkpoint each external conclusion; roll back dependents when a premise fails. / 拆为互不重叠且合起来充分的子问题；定义证据与局部标准；检查每个外部结论；前提失败时回滚依赖步骤。 | Ordered step records and final validator result; never private reasoning text. / 有序步骤记录和最终验证结果；不得包含私密推理文本。 | Switch to parallel for unresolved rivals; iterative when action is needed for evidence; stop or escalate when depth grows without validation value. / 竞争解释无法排除时转并行；需行动补证时转迭代；深度增长但验证收益低时停止或升级。 |
| parallel / 并行探索 | Multiple materially different candidates can be compared under common criteria. / 多个实质不同候选可用统一标准比较。 | Define candidate space and difference rule; collect evidence independently; apply common scores and vetoes; preserve losing paths and elimination reasons; validate the winner. / 定义候选空间和差异规则；独立收集证据；应用统一评分与否决；保留落选路径及原因；验证胜出者。 | Candidate IDs, hypotheses, evidence, validation, elimination reason, selected path, selection basis. / 候选 ID、假设、证据、验证、淘汰原因、选中路径和选择依据。 | Switch to iterative when all candidates depend on unknown facts; regenerate or fall back to chain when diversity is false; escalate material ties. / 所有候选依赖未知事实时转迭代；伪多样时重新生成或降为链式；重大并列时升级。 |
| iterative / 迭代验证 | The unknown can be reduced only through environment interaction. / 只有与环境交互才能缩小未知。 | Maintain hypotheses; choose the safest high-information-gain action; observe; update, eliminate, or add hypotheses; check snapshots, budget, and stop rules every round. / 维护假设集；选择风险可接受且信息增益高的动作；观察；更新、淘汰或新增假设；每轮检查快照、预算和停止规则。 | Round number, key unknown, action and expected discrimination, observation, hypothesis delta, progress state, cost. / 轮次、关键未知、动作与预期判别力、观察、假设变化、进展状态和成本。 | Stop when evidence is sufficient, no progress persists, next action exceeds risk or permission, budget is exhausted, or human/external evidence is required. / 证据充分、持续无进展、下一动作风险或权限越界、预算耗尽或需人工/外部证据时停止。 |

Direct processing is an optimized runtime path, not a seventh matrix topology. Orchestration coordinates modes and state; hierarchy propagates contracts and authority across parent-child work. Neither supporting role promotes an extension cell without repeated independent evidence. / 直接处理是优化的运行路径，不是第七种矩阵拓扑。编排负责协调模式与状态，层级负责在父子工作间传播契约和权限。这些支撑作用不会在缺少反复独立证据时自动晋升扩展单元。

## Validation, Switching, And Stopping / 验证、换路与停止

### Validator precedence / 验证器优先级

Prefer deterministic rules, calculations, tests, and real execution results; then traceable external data; then independent-model review; use original-model self-evaluation only as an auxiliary signal. Human approval can be the highest governance gate but must retain actor, time, basis, and authority. / 优先使用确定性规则、计算、测试和真实执行结果，其次是可追踪外部数据，再其次是独立模型评审；原模型自评只能作为辅助信号。人工审批可作为最高治理门槛，但必须保留人员、时间、依据与权限。

Record validation as `not_run`, `passed`, `conditionally_passed`, `repairable_failure`, `nonrepairable_failure`, `human_required`, or `timed_out`. Bind every result to the exact contract-declared validator and criteria fingerprints plus candidate, contract, and evidence fingerprints; recompute each nested validation hash. Any bound input change invalidates the result. `completed` requires one contract-matching gate for every mandatory validator and every such result to be `passed`; `conditionally_passed` records an unresolved obligation and must repair, fail, or escalate unless a separate versioned low-risk release rule explicitly permits it. Missing, timed-out, unavailable, undeclared, or authority-less human validation is fail-closed. / 验证结果记录为未运行、通过、有条件通过、可修复失败、不可修复失败、需要人工或超时。每个结果必须绑定契约中完整声明的验证器与准则指纹，以及候选、契约和证据指纹，并重算每条嵌套验证哈希；任何绑定输入变化都会使结果失效。进入 `completed` 要求每个必选验证器都存在一个与契约匹配的闸门，且相应结果均为 `passed`；`conditionally_passed` 必须记录未完成义务，并进入修复、失败或升级，除非独立的版本化低风险放行规则明确允许。必选验证缺失、超时、不可用、未声明，或人工验证缺少权限时默认阻断。

### Mode-switch record / 模式切换记录

Every switch records old mode, new mode, triggering evidence, budget impact, unfinished steps, and event identity. Mode switching is a control action, not automatically a failure. A heavy mode may return to direct or deterministic execution after critical uncertainty is resolved, but only through an explicit recorded switch. / 每次换路记录原模式、新模式、触发证据、预算影响、未完成步骤和事件标识。换路是控制动作，不应自动视为失败。关键不确定性解决后，重模式可以返回直接或确定性执行，但必须显式记录切换。

### Human escalation and resumption / 人工升级与恢复

An escalation package contains `human_work_id`, recipient capability or queue, service objective, expiry, resume token, task/run/contract identities, immutable input/candidate/evidence fingerprints, authority requested, unfinished work, and the allowed approval or rejection payload. `escalated` terminates the current run. Approval starts a new linked run that refreshes permissions, snapshots, budgets, and validators; changed inputs or expired authority require a new approval. No recipient or expired work item follows the scene-owned fail-closed fallback. / 升级包包含人工工作标识、接收能力或队列、服务目标、过期时间、恢复令牌、任务/运行/契约标识、不可变的输入/候选/证据指纹、所请求权限、未完成工作，以及允许的批准或拒绝载荷。`escalated` 会终止当前运行。批准后启动一个新的关联运行，并重新确认权限、快照、预算和验证器；输入变化或权限过期必须重新审批。无人接收或人工工作项过期时，执行场景定义的默认阻断回退。

### Strong stop conditions / 强停止条件

Stop or transition when any configured strong condition fires / 任一已配置强条件触发时停止或转换:

- Mandatory validators pass and evidence sufficiency is met. / 必选验证器通过且证据充分。
- A configured low-risk direct condition yields a determinate answer. / 已配置的低风险直接条件得到确定答案。
- Budget is exhausted and the exact contract `on_exhaustion` action is applied: `stop`, `escalate`, or `reject`; `degrade` is valid only with an executable degradation plan and otherwise the contract is rejected before execution. / 预算耗尽时执行契约中确切的 `on_exhaustion` 动作：`stop`、`escalate` 或 `reject`；`degrade` 只有在存在可执行降级方案时才有效，否则契约在执行前即被拒绝。
- The `no_progress` stop condition's positive `consecutive_steps` limit is reached after each closed step reports a measured `information_gain`; a step counts as progress only when its gain meets `min_information_gain`, and the exact `on_trigger` action is applied. Multiple active rules are not silently compressed into one threshold. / 每个闭合步骤报告可度量的 `information_gain` 后，达到 `no_progress` 的正整数 `consecutive_steps` 上限即触发停止；只有信息增益达到 `min_information_gain` 才算进展，并执行确切的 `on_trigger` 动作。多个生效规则不得被静默压缩成一个阈值。
- Critical evidence is unavailable, goals or constraints conflict, authority is insufficient, a human decision is mandatory, or the task is cancelled. / 关键证据不可得、目标或约束冲突、权限不足、必须人工决定或任务被取消。

Never stop only because the model reports high confidence or the explanation is long. / 不得仅因模型自信度高或解释很长而停止。

## Standalone And Interactive Operation / 独立与交互运行

Standalone operation requires a normalizer, router, needed mode executors, atomic budget controller, validator gate, append-only event store, replayable state machine, and terminal-output builder. The deterministic route reference is [`reasoning_router.py`](../runtime/reasoning_router.py), the execution kernel is [`reasoning_runtime.py`](../runtime/reasoning_runtime.py), and producer-side Schema, hash, cross-binding, and evidence-gate checks are [`reasoning_artifacts.py`](../runtime/reasoning_artifacts.py). Use `EventStore` only for ephemeral runs; use `JsonlEventStore` for modest local restart-safe event replay, and replace it with a transactional database adapter for high-volume or multi-writer production while preserving atomic commit, idempotency, and replay semantics. Start governed execution through `ReasoningEngine.create_run_from_contract()` so the normative contract remains the sole authority for identity, route, budget, validators, stop limits, governance, and binding hash; the lower-level `create_run()` remains a compact kernel/test adapter. Record at least identities, initial route and reason, budget limits, reservations and use, per-step evidence/action/observation/decision, validator bindings and results, switches, escalation reason, and stop reason. / 独立运行需要标准化器、路由器、所需模式执行器、原子预算控制器、验证闸门、追加式事件存储、可回放状态机和终态输出生成器。确定性路由参考见 [`reasoning_router.py`](../runtime/reasoning_router.py)，执行内核见 [`reasoning_runtime.py`](../runtime/reasoning_runtime.py)，生产端 Schema、哈希、跨绑定与证据门校验见 [`reasoning_artifacts.py`](../runtime/reasoning_artifacts.py)。`EventStore` 只用于临时运行；轻量本地且需要重启安全重放时使用 `JsonlEventStore`，高吞吐或多写者生产环境则替换为事务数据库适配器，同时保持原子提交、幂等与重放语义。受治理执行必须通过 `ReasoningEngine.create_run_from_contract()` 启动，使规范契约成为标识、路由、预算、验证器、停止上限、治理与绑定哈希的唯一权威；底层 `create_run()` 仅保留为紧凑内核/测试适配器。至少记录标识、初始路由及原因、预算上限、预留与消耗、逐步证据/动作/观察/决定、验证绑定及结果、换路、升级原因和停止原因。

For `execution_mode: chain`, compile an explicit blueprint and the sealed contract with the [Reasoning Chain Factory / 推理链工厂](reasoning-chain-factory.md), then execute steps only through its plan session so order, predecessor claims, checkpoints, budgets, probes, and plan hashes remain enforceable and replayable. Plan-bound tool steps use the fingerprint-only read-only dispatch/observation lifecycle, and final candidate creation requires immutable higher-version evidence revisions linked to the exact final-claim step records. / 对 `execution_mode: chain`，使用[推理链工厂](reasoning-chain-factory.md)编译显式蓝图与密封契约，随后只通过其计划会话执行步骤，使顺序、前驱命题、检查点、预算、探针和计划哈希保持可强制、可回放。与计划绑定的工具步骤使用仅指纹的只读分派—观测生命周期；最终候选创建要求不可变的更高版本证据修订，并链接到确切最终命题步骤记录。

Interactive operation uses [Workflow Observability Probes / 工作流可观测性探针](workflow-observability-probes.md). Emit `task_received`, `task_normalized`, `route_selected`, `contract_established`, guarded `state_transitioned`, `step_started`, `action_dispatched`, `action_observed`, `step_closed`, applicable evidence/candidate/iteration events, `mode_switched`, `validation_started`, `validation_completed`, `feedback_updated`, and `run_ended`. Before collection, resolve versioned probes with complete `true | false | unknown` condition states; missing or unknown applicability fails closed. Before metric publication, retain calculation inputs and recompute the result under the registry-owned minimum sample and finalized watermark window. Handle probe feedback as data completion, continue, switch, stop, escalate, or block according to severity and authority. / 交互运行使用[工作流可观测性探针](workflow-observability-probes.md)。发送任务接收、任务标准化、路由选择、契约建立、受门控状态转换、步骤开始、动作分派、动作观察、步骤关闭、适用的证据/候选/迭代事件、模式切换、验证开始、验证完成、反馈更新和运行结束事件。采集前以完整的 `true | false | unknown` 条件状态解析版本化探针；条件缺失或未知时默认阻断。指标发布前保留计算输入，并在注册表拥有的最小样本与已封窗 watermark 下重算结果；按严重级别与权限将探针反馈处理为补数、继续、换路、停止、升级或阻断。

Control precedence is governance hard gates, mandatory validator results, contractual budget and stop conditions, authorized inline probe blocks, probe advice, and model self-evaluation. Probes do not make business decisions. / 控制优先级依次为治理硬门槛、必选验证器结果、契约预算与停止条件、有授权的内联探针阻断、探针建议和模型自评。探针不替代业务决策。

## Output And Acceptance / 输出与验收

### Closable step record / 可关闭步骤记录

```yaml
step_id: STEP_EXAMPLE
step_version: 1.0.0
step_hash: sha256:3333333333333333333333333333333333333333333333333333333333333333
contract_binding:
  id: CONTRACT_EXAMPLE
  version: 1.0.0
  hash: sha256:4444444444444444444444444444444444444444444444444444444444444444
sequence_number: 1
attempt_number: 1
status: completed
summary: "execute an externally verifiable check / 执行外部可核验检查"
claim: "candidate must satisfy the deterministic validator / 候选必须满足确定性验证器"
evidence_refs: []
action: "run deterministic test / 执行确定性测试"
observation: {passed: 8, failed: 0}
local_decision: "auditable decision / 可审计决定"
resource_use:
  reasoning_tokens: {state: observed_zero, value: 0}
  latency_ms: {state: observed, value: 12}
  model_calls: {state: observed_zero, value: 0}
  tool_calls: {state: observed, value: 1}
  parallel_paths: {state: observed_zero, value: 0}
  iterations: {state: observed_zero, value: 0}
  retries: {state: observed_zero, value: 0}
  total_cost_units: {state: observed_zero, value: 0}
progress: true
no_progress_streak: 0
input_evidence_bindings: []
output_evidence_bindings: []
validation_bindings: []
started_at: "2026-07-15T09:00:01Z"
ended_at: "2026-07-15T09:00:02Z"
```

This is the `payload.data` shape for `step_closed`; the enclosing event supplies task/run identity, state, causation, idempotency, provenance, and privacy fields. A terminal result additionally binds each included step to the final candidate and adds a reproducible `record_hash` over the complete closed-step record. `step_hash` remains the stable start identity. Evidence follows the same two-digest rule: `evidence_hash` identifies external source content, while `record_hash` seals the complete evidence metadata envelope. If a scene records model self-confidence, keep it in separate advisory telemetry and never substitute it for validator results. / 这是 `step_closed` 的 `payload.data` 结构；外层事件提供任务/运行标识、状态、因果、幂等、来源和隐私字段。终态结果还会把纳入的每个步骤绑定到最终候选，并增加覆盖完整闭合步骤记录的可重算 `record_hash`；`step_hash` 保持为稳定的步骤起始身份。证据采用相同的双摘要规则：`evidence_hash` 标识外部来源内容，`record_hash` 封存完整证据元数据。若场景记录模型自评置信度，应放在独立建议性遥测中，绝不能替代验证结果。

### Final result / 最终结果

Return the machine-readable [Reasoning Result](../schemas/reasoning-result.schema.json): result, workflow, task, run, and scene identities; structured terminal reason; risk; contract and candidate bindings; initial/final execution configurations and switches; budget accounting; release-gate basis and authoritative evaluation time; evidence; externally verifiable steps; validation results; typed facts/inferences/decisions/recommendations; final decision; unresolved items; next actions; limitations; user-visible output; provenance; and creation time. The append-only event stream retains the same identity chain for replay. A user-facing answer may be shorter, but the audit record retains the complete result envelope. / 返回机器可读的[推理结果](../schemas/reasoning-result.schema.json)：结果、工作流、任务、运行与场景标识，结构化终态原因，风险，契约与候选绑定，初始/最终执行配置及切换，预算核算，放行依据与权威评估时间，证据，外部可核验步骤，验证结果，已分类的事实/推断/决定/建议，最终决定，未解决事项，后续动作，限制，用户可见输出，来源和创建时间。仅追加事件流保留相同标识链以供重放。面向用户的答案可以更短，但审计记录必须保留完整结果信封。

For a run created by the normative-contract adapter, call `ReasoningEngine.finalize(..., claims=public_claims)` so the exact auditable claim set participates in the evidence gate. `ReasoningEngine.build_result()` derives identities, terminal state, contract/candidate bindings, execution configuration, budget accounting, steps, validations, evidence, release-gate records, and gate time from runtime state; it rejects a different claim set or a backdated creation time, closes the mode-switch chain and per-dimension budget accounting, recomputes nested evidence/step record hashes and inline output `content_hash`, then seals the top-level result hash and runs Schema plus cross-binding/evidence-gate semantic validation. One run has one immutable sealed result: an identical retry returns it, while conflicting result content is rejected. The caller supplies the same domain claims, final decision, user-visible output, unresolved items, next actions, limitations, and field provenance. / 对由规范契约适配器创建的运行，调用 `ReasoningEngine.finalize(..., claims=public_claims)`，使确切的可审计声明集合参与证据门。`ReasoningEngine.build_result()` 从运行状态派生标识、终态、契约/候选绑定、执行配置、预算核算、步骤、验证、证据、放行门记录与闸门时间；它拒绝不同的声明集合或回填的创建时间，闭合模式切换链和逐维预算核算，重算证据/步骤记录摘要及内联输出 `content_hash`，再封存顶层结果哈希并执行 Schema、跨绑定与证据门语义校验。每个运行只有一个不可变封存结果：相同重试返回原结果，冲突内容会被拒绝。调用方提供相同的领域声明、最终决定、用户可见输出、未解决事项、后续动作、限制和字段来源。

Acceptance checklist / 验收清单:

- Goal is verifiable; facts, assumptions, preferences, and constraints are separate. / 目标可验证；事实、假设、偏好和约束已分离。
- Risk, reversibility, evidence requirement, permissions, budget, validators, and stop rules are explicit. / 风险、可逆性、证据要求、权限、预算、验证器和停止规则明确。
- Every closed step contains claim, evidence, action, observation, decision, source type, resource use, and a reproducible full-record hash; inline output content is independently hashed. / 每个已关闭步骤包含命题、证据、动作、观察、决定、来源类型、资源消耗及可重算的完整记录哈希；内联输出内容另行独立计算摘要。
- Parallel paths are materially different; iterative rounds show information gain or stop. / 并行路径有实质差异；迭代轮次产生信息增益，否则停止。
- Goal, constraint, and verified-fact revisions are explicit and versioned. / 目标、约束和已验证事实的修订显式且有版本。
- Mandatory validators ran; output status matches validation; stop reason exists. / 必选验证器已运行；输出状态与验证一致；停止原因存在。
- Illegal transitions, duplicate side effects, stale validation, budget overruns, no-progress loops, crash replay, cancellation, and timeout have behavioral tests. / 非法转换、重复副作用、过期验证、预算越界、无进展循环、崩溃回放、取消与超时均有行为测试。
- No private chain-of-thought or fabricated evidence, approval, or validation result is captured. / 未采集私密思维过程，未伪造证据、审批或验证结果。
