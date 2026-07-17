# Reasoning Chain Factory / 推理链工厂

Version / 版本: `1.4.0`

Status / 状态: Reference implementation / 参考实现

Parent cell / 所属交织点: [Chain-of-Thought / 思维链](patterns/reasoning/reasoning-chain.md)

Shared protocols / 共享协议: [Reasoning Execution Flow / 推理执行流程](reasoning-execution-flow.md); [Workflow Observability Probes / 工作流可观测性探针](workflow-observability-probes.md)

The factory is an implementation mechanism for `COG_REASONING__TOP_CHAIN`, not a new matrix pattern. It compiles an explicit blueprint and one sealed reasoning contract into an immutable, externally verifiable chain plan, then guards ordered execution through the shared runtime. / 本工厂是 `COG_REASONING__TOP_CHAIN` 的实现机制，不是新的矩阵模式。它把显式蓝图与单个已封存推理契约编译为不可变、外部可核验的链计划，再通过共享运行时守卫有序执行。

## Quick Navigation / 快速导航

- [Design Basis / 设计依据](#design-basis--设计依据)
- [Boundary / 边界](#boundary--边界)
- [Factory Contract / 工厂契约](#factory-contract--工厂契约)
- [Compile Invariants / 编译不变量](#compile-invariants--编译不变量)
- [Execution Workflow / 执行流程](#execution-workflow--执行流程)
- [Guarded APIs / 受守卫-api](#guarded-apis--受守卫-api)
- [Blueprint Example / 蓝图示例](#blueprint-example--蓝图示例)
- [Failure And Exit Matrix / 失败与出口矩阵](#failure-and-exit-matrix--失败与出口矩阵)
- [Observability / 可观测性](#observability--可观测性)
- [Constraints And Acceptance / 约束与验收](#constraints-and-acceptance--约束与验收)

## Design Basis / 设计依据

- `Execution Flow Framework v0.1 / 执行流程框架 v0.1` contributes definition-versus-run separation, explicit dependency and state rules, versioned contracts, controlled side effects, budget and stop governance, and failure-as-state handling. / `执行流程框架 v0.1` 提供定义与运行实例分离、显式依赖与状态规则、版本化契约、受控副作用、预算与停止治理，以及“失败即状态”的原则。
- `Workflow Observability Probe Framework v0.1 / 工作流可观测性探针框架 v0.1` contributes independent probes, stable identities, field-level provenance, explicit data gaps, raw-versus-derived separation, completion protection, and denominator-aware metrics. / `工作流可观测性探针框架 v0.1` 提供独立探针、稳定标识、字段级来源、显式数据缺口、原始与派生数据分离、完成态保护和分母明确的指标原则。

The factory specializes those cross-cutting rules for the existing reasoning-chain cell; it does not duplicate either shared protocol. / 工厂把这些跨单元规则专门化到现有推理链单元，不重复定义两个共享协议。

## Boundary / 边界

Use the factory only after routing selects `execution_mode=chain` and `primary_topology=chain`. The factory does not classify tasks, choose a heavier mode, execute domain tools, make business decisions, or release results. Those responsibilities remain with routing, adapters, validators, governance gates, and `ReasoningEngine`. / 仅在路由已选择 `execution_mode=chain` 与 `primary_topology=chain` 后使用工厂。工厂不负责任务分类、选择更重模式、执行领域工具、作出业务决定或放行结果；这些职责仍属于路由器、适配器、验证器、治理闸门与 `ReasoningEngine`。

The persisted plan contains public claims to verify, evidence types, read-only actions, checkpoint criteria, budgets, gap policies, and exits. It must never contain private chain-of-thought, hidden reasoning, an internal monologue, or a scratchpad. / 持久化计划只包含待核验公开命题、证据类型、只读动作、检查点标准、预算、缺口策略与出口；不得包含私密思维链、隐藏推理、内部独白或草稿区。

## Factory Contract / 工厂契约

| Layer / 层 | Normative artifact / 规范制品 | Responsibility / 职责 |
| --- | --- | --- |
| Input / 输入 | [Reasoning Chain Blueprint Schema / 推理链蓝图 Schema](../schemas/reasoning-chain-blueprint.schema.json) | Author-owned reusable step intent, claim dependencies, evidence, checkpoint, gap, and budget declarations. / 负责人维护的可复用步骤意图、命题依赖、证据、检查点、缺口和预算声明。 |
| Authority / 权威 | [Reasoning Contract Schema / 推理契约 Schema](../schemas/reasoning-contract.schema.json) | Run identity, selected mode, global budget, stop conditions, allowed switches, validators, and governance. / 运行标识、选定模式、全局预算、停止条件、允许换路、验证器和治理。 |
| Output / 输出 | [Reasoning Chain Plan Schema / 推理链计划 Schema](../schemas/reasoning-chain-plan.schema.json) | Immutable factory, blueprint, contract, step, checkpoint, budget, and probe bindings. / 不可变的工厂、蓝图、契约、步骤、检查点、预算和探针绑定。 |
| Local validation / 局部验证 | [Checkpoint Validation Schema / 检查点验证 Schema](../schemas/reasoning-chain-checkpoint-validation.schema.json) | Self-hashed result bound to the exact plan, step, checkpoint, validator, criteria, observation, versioned evidence records, actor, and authority. / 自带哈希的结果，精确绑定计划、步骤、检查点、验证器、标准、观察、版本化证据记录、执行者与授权。 |
| Compatibility / 兼容入口 | [`reasoning_chain_factory.py`](../runtime/reasoning_chain_factory.py) | Stable public imports for the split implementation. / 为拆分后的实现提供稳定公共导入。 |
| Compiler / 编译器 | [`reasoning_chain_compiler.py`](../runtime/reasoning_chain_compiler.py) | Deterministic compilation plus blueprint, contract, plan, budget, checkpoint, and probe validation. / 确定性编译，以及蓝图、契约、计划、预算、检查点与探针校验。 |
| Session / 会话 | [`reasoning_chain_session.py`](../runtime/reasoning_chain_session.py) | Prefix-order guard, evidence lineage, read-only tool lifecycle, checkpoint gate, and candidate binding. / 前缀顺序守卫、证据血缘、只读工具生命周期、检查点门控与候选绑定。 |
| Kernel / 内核 | [`reasoning_runtime.py`](../runtime/reasoning_runtime.py) | State, append-only events, budget ledger, validation, switching, stopping, replay, and final result. / 状态、仅追加事件、预算账本、验证、换路、停止、重放和最终结果。 |
| Durable event adapter / 持久化事件适配器 | `JsonlEventStore` in [`reasoning_runtime.py`](../runtime/reasoning_runtime.py) | Self-hashed JSONL snapshots, atomic replace, restart replay, idempotency restoration, and memory/disk rollback on commit failure. / 自哈希 JSONL 快照、原子替换、重启重放、幂等恢复，以及提交失败时的内存与磁盘回滚。 |

The same blueprint and sealed contract compile to the same plan. The plan hash excludes only its own `plan_hash`; checkpoint and validation hashes exclude only their own hash fields. Starting or reconstructing a session recompiles the original blueprint and contract and requires byte-equivalent plan content, so recomputing a modified plan hash cannot authorize blueprint drift. `validate_chain_plan(plan)` performs self-consistency checks; authoritative validation must supply both `contract=` and `blueprint=` together, never only one authority source. / 同一蓝图与已封存契约必须编译出相同计划。计划摘要只排除自身 `plan_hash`，检查点与验证摘要只排除各自哈希字段。启动或重建会话时会重新编译原始蓝图与契约，并要求计划内容逐字节等价，因此重算被修改计划的哈希不能授权蓝图漂移。`validate_chain_plan(plan)` 执行自一致性校验；权威校验必须同时传入 `contract=` 与 `blueprint=`，不得只提供一个权威来源。

## Compile Invariants / 编译不变量

Reject before run creation unless every invariant holds / 任一不变量不满足时必须在创建运行前拒绝：

1. The contract and its routing decision both select chain execution. / 契约及其路由决定都选择链式执行。
2. Step numbers are contiguous; step keys, output claims, checkpoint IDs, and compiled step IDs are unique. / 步骤序号连续，步骤键、输出命题、检查点 ID 与编译后步骤 ID 均唯一。
3. The first step has no chain-internal premise; every later step depends only on its immediate predecessor and binds that predecessor's checked output claim. / 首步不含链内前提；后续每步只依赖直接前驱，并绑定前驱经检查的输出命题。
4. Every consumed chain claim was produced earlier; the last step's claim is included in `final_claim_ids`. / 每个被消费的链内命题都已在前序生成；末步命题必须进入 `final_claim_ids`。
5. Every critical step declares evidence types and a versioned checkpoint with explicit pass criteria and failure exit. / 每个关键步骤声明证据类型及带版本的检查点，检查点包含明确通过标准和失败出口。
6. Step budget vectors sum within every configured contract limit. A positive allocation against an unconfigured limit is rejected. / 逐步预算向量之和不得超过任一已配置契约上限；未配置上限却进行正数分配时拒绝。
7. Strict-chain steps allocate zero parallel paths, iterations, and retries. Rival paths or feedback repair use an allowlisted switch instead of hiding another topology inside the chain. / 严格链步骤的并行路径、迭代和重试分配必须为零；竞争路径或反馈修复通过契约允许的换路完成，不得把其他拓扑藏进链式步骤。
8. A `switch_parallel` or `switch_iterative` exit is valid only when the sealed contract contains the matching allowed mode switch. / `switch_parallel` 或 `switch_iterative` 出口只有在封存契约包含匹配的允许换路规则时才有效。
9. Reasoning steps are read-only: `side_effect=false`. State-changing work belongs to Action / 行动 or a governed orchestration boundary. / 推理步骤只读，必须为 `side_effect=false`；修改状态的工作属于行动能力或受治理编排边界。
10. A tool step declares one exact `(id, version, hash)` `tool_binding`, one exact `authorization_policy_binding`, and exactly one tool-call allocation. Non-tool steps cannot declare either binding or a tool-call budget. / 工具步骤声明一个确切的 `(id, version, hash)` `tool_binding`、一个确切的 `authorization_policy_binding`，并且只分配一次工具调用；非工具步骤不得声明这两类绑定或工具调用预算。
11. Conditional probe applicability is resolved before execution and embedded with versioned required-probe bindings. / 执行前解析条件探针适用性，并把带版本的必需探针绑定写入计划。
12. Every normative stop condition and budget-exhaustion action must be executable by the current runtime. Unsupported conditions, ambiguous duplicate `no_progress` rules, and undeclared degradation fail during compilation rather than after run creation. / 每个规范停止条件与预算耗尽动作都必须可由当前运行时执行；不支持的条件、含义不明的重复 `no_progress` 规则及未声明的降级会在编译期失败，而不是创建运行后才失败。
13. The compiled plan must be an exact projection of its bound blueprint and contract, including claims, actions, tool identities, checkpoints, budgets, controls, and final claims. / 编译计划必须是其绑定蓝图与契约的精确投影，包括命题、动作、工具身份、检查点、预算、控制项与最终命题。

## Execution Workflow / 执行流程

```text
route to chain / 路由到链式
  -> seal reasoning contract / 封存推理契约
  -> validate blueprint / 校验蓝图
  -> preflight runtime capabilities / 预检运行时能力
  -> compile and seal plan / 编译并封存计划
  -> resolve required probes / 解析必需探针
  -> create contract-bound run / 创建契约绑定运行
  -> record and resolve versioned evidence / 记录并解析版本化证据
  -> reserve the complete step allocation / 预留完整步骤预算
  -> start only the next eligible step / 仅启动下一可执行步骤
  -> for a tool step, live-verify its grant against the bound policy / 工具步骤按绑定策略实时验证授权
  -> dispatch and observe the exact read-only tool by fingerprint / 按指纹分派并观测确切只读工具
  -> observe and emit a bound validation artifact / 观察并生成绑定验证制品
       -> passed: unlock successor / 通过：解锁后继
       -> insufficient evidence: apply data-gap policy / 证据不足：执行缺口策略
       -> failed: apply declared failure exit / 失败：执行已声明失败出口
       -> human required: escalate / 需要人工：升级
  -> atomically consume actual use and release unused reservation / 原子消费实际用量并释放未用预留
  -> revise final-claim step evidence to the exact candidate / 把最终命题步骤证据修订为精确绑定候选
  -> atomically bind candidate, evidence revisions, plan, and final claims / 原子绑定候选、证据修订、计划与最终命题
  -> run mandatory final validators and evidence gate / 执行必选终态验证与证据门
```

Call `compile(blueprint, contract)`, then `start_session(engine, plan, contract, blueprint)`. Start with `start_step(step_key, evidence_records=[...])`, never bare evidence strings: each self-hashed record is validated against the Evidence definition, contract and candidate state, persisted once, and rebound as `(id, version, record_hash)`. The session atomically commits the exact compiled reservation and `step_started`; either both persist in order or both roll back, while reservation exhaustion closes before dispatch. A tool step must pass a concrete `authorization_binding` to `dispatch_readonly_tool()` and `observe_readonly_tool()`. Before accepting the dispatch, the injected `tool_authorizer` receives only that detached binding plus bounded public context—plan, step, tool, bound policy, input hash, risk, and `side_effect=false`; missing authorizer, exception, revocation, or any result other than exact `true` fails closed without an action event. Accepted events bind the exact plan, step, tool, policy, verified grant, input hash, output hash, and outcome without persisting raw tool data. Close with `checkpoint_validation=...`; a passed result must bind the exact observation and evidence records, satisfy type, freshness, integrity, source-independence, and claim-coverage policy, and carry concrete actor and authority bindings. Independent-source count uses source type plus source reference, so multiple versions of one source do not inflate it. Close atomically consumes actual use against the reservation and releases the remainder. After all steps pass, `set_candidate(candidate, evidence_records=[...])` requires a higher-version candidate-bound revision for every ordered final-claim step record; each revision names its exact predecessor record, preserves source content, and appends the declared lineage operation. Candidate creation and evidence persistence commit or roll back together. Replay recomputes evidence, authorization, tool, candidate-lineage, and budget lifecycle bindings and rejects direct generic-runtime bypasses. / 先调用 `compile(blueprint, contract)`，再调用 `start_session(engine, plan, contract, blueprint)`。使用 `start_step(step_key, evidence_records=[...])` 启动，不得传裸证据字符串：每条自带哈希的记录都要通过 Evidence 定义、契约和候选状态校验，只持久化一次，并重新绑定为 `(id, version, record_hash)`。会话会把编译出的精确预算预留与 `step_started` 原子提交：二者按顺序同时持久化或同时回滚；预留额度不足则在分派前关闭。工具步骤必须向 `dispatch_readonly_tool()` 与 `observe_readonly_tool()` 传入具体 `authorization_binding`。接受分派前，注入的 `tool_authorizer` 只能收到脱离内部状态的授权绑定与有界公开上下文，包括计划、步骤、工具、绑定策略、输入哈希、风险和 `side_effect=false`；授权器缺失、异常、授权撤销或返回值不是精确 `true` 时，默认阻断且不写入动作事件。已接受事件绑定确切计划、步骤、工具、策略、已验证授权、输入哈希、输出哈希与结果，但不持久化原始工具数据。关闭时传入 `checkpoint_validation=...`；通过结果必须绑定确切观察与证据记录，满足类型、新鲜度、完整性、独立来源和命题覆盖策略，并包含具体执行者与授权绑定。独立来源按来源类型与来源引用计数，同一来源的多个版本不会抬高来源数。关闭操作针对该预留原子消费实际用量并释放余量。全部步骤通过后，`set_candidate(candidate, evidence_records=[...])` 要求针对每条有序最终命题步骤记录提供更高版本且绑定候选的修订；每条修订必须指明确切前驱记录、保持来源内容不变并追加已声明的血缘操作。候选创建与证据持久化同时提交或同时回滚。重放会重算证据、授权、工具、候选血缘与预算生命周期绑定，并拒绝直接绕过会话调用通用运行时。

## Guarded APIs / 受守卫 API

The adapter is an authorization and audit boundary, not a domain-tool executor. Configure `ReasoningEngine(tool_authorizer=...)` with a trusted verifier that authenticates the grant binding against the plan-bound policy and public dispatch context. The controller performs the actual authorized read outside the factory, then reports only deterministic fingerprints and a public outcome. A passed tool step must use the observed output itself as the checkpoint observation and report `tool_calls=1`. / 适配器是授权与审计边界，不是领域工具执行器。通过 `ReasoningEngine(tool_authorizer=...)` 配置可信验证器，针对计划绑定策略与公开分派上下文认证授权绑定。控制器在工厂之外执行已经授权的实际只读操作，再只上报确定性指纹和公开结果。通过的工具步骤必须把已观测输出本身作为检查点观察，并报告 `tool_calls=1`。

```python
session.start_step(step_key, evidence_records=[step_evidence])
tool_call_id = session.dispatch_readonly_tool(
    step_key,
    tool_input={"query": "public-record-42"},
    authorization_binding=verified_grant_binding,
)
# The controller executes the authorized read-only tool here.
# 控制器在此执行已授权的只读工具。
session.observe_readonly_tool(
    step_key,
    tool_input={"query": "public-record-42"},
    authorization_binding=verified_grant_binding,
    outcome="succeeded",
    output=public_tool_output,
)
session.close_step(
    step_key,
    observation=public_tool_output,
    checkpoint_validation=bound_checkpoint_validation,
    resource_use={**observed_usage, "tool_calls": 1},
)
```

Candidate evidence is a new immutable revision, not an in-place mutation and not a second copy with no ancestry. Its `evidence_id` and source-content fields stay unchanged; `evidence_version` increases; `predecessor_evidence_binding` points to the exact step record `(id, version, record_hash)`; `candidate_binding` becomes observed; and `transformation_history` appends exactly one `candidate_binding_revision` entry carrying that predecessor binding. Recompute `record_hash`, then pass all revisions in predecessor order. / 候选证据是新的不可变修订，不是原地修改，也不是没有祖先关系的第二份副本。其 `evidence_id` 与来源内容字段保持不变；`evidence_version` 提升；`predecessor_evidence_binding` 指向确切步骤记录 `(id, version, record_hash)`；`candidate_binding` 变为已观测；`transformation_history` 精确追加一条携带该前驱绑定的 `candidate_binding_revision`。重新计算 `record_hash` 后，按前驱顺序传入全部修订。

```python
candidate_hash = session.set_candidate(
    public_candidate,
    evidence_records=candidate_bound_revisions,
)
```

An exact retry may reuse the same idempotency key. Any missing revision, reordered predecessor, version rollback, candidate mismatch, source-content change, raw tool payload, tool substitution, duplicate tool phase, failed tool outcome presented as passed, or post-close action fails closed. / 完全相同的重试可以复用同一幂等键。任何缺失修订、前驱乱序、版本回退、候选错绑、来源内容变化、原始工具载荷、工具替换、重复工具阶段、把失败工具结果冒充通过，或步骤关闭后再发动作，都会失败关闭。

## Blueprint Example / 蓝图示例

The blueprint is a public execution specification, not a request for model rationale. / 蓝图是公开执行规范，不是索取模型推理过程的请求。

For a tool step, set `uses_tool: true`, add both `tool_binding: {id, version, hash}` and `authorization_policy_binding: {id, version, hash}`, keep `side_effect: false`, and allocate exactly `tool_calls: 1`. Omit both bindings and allocate zero tool calls for every non-tool step. / 对工具步骤，设置 `uses_tool: true`，同时增加 `tool_binding: {id, version, hash}` 与 `authorization_policy_binding: {id, version, hash}`，保持 `side_effect: false`，并精确分配 `tool_calls: 1`；所有非工具步骤都省略这两类绑定且工具调用分配为零。

```yaml
schema_version: 1.0.0
blueprint_id: VERIFY_THEN_SYNTHESIZE
blueprint_version: 1.0.0
name_en: Verify then synthesize
name_zh: 先验证后综合
description_en: Verify the critical premise before producing the final claim.
description_zh: 先验证关键前提，再形成最终命题。
max_steps: 2
requires_outcome: true
steps:
  - step_key: verify-premise
    name_en: Verify premise
    name_zh: 验证前提
    sequence_number: 1
    depends_on: []
    input_claim_ids: []
    output_claim_id: CLAIM_PREMISE_VALID
    criticality: critical
    claim_to_verify: The required premise is supported by current test evidence. / 必需前提由当前测试证据支持。
    action: {kind: inspect, instruction: Inspect the named test evidence. / 检查指定测试证据。, uses_tool: false, side_effect: false}
    required_evidence_types: [test]
    checkpoint:
      checkpoint_id: CHECK_PREMISE
      checkpoint_version: 1.0.0
      validator_type: test
      pass_criteria: {all_required_tests_pass: true}
      on_failure: escalate
    data_gap_policy: request_probe
    budget_allocation: {reasoning_tokens: 500, latency_ms: 1000, model_calls: 1, tool_calls: 0, parallel_paths: 0, iterations: 0, retries: 0, total_cost_units: 0.2}
  - step_key: synthesize-result
    name_en: Synthesize result
    name_zh: 综合结果
    sequence_number: 2
    depends_on: [verify-premise]
    input_claim_ids: [CLAIM_PREMISE_VALID]
    output_claim_id: CLAIM_FINAL
    criticality: critical
    claim_to_verify: The final claim follows from the verified premise. / 最终命题由已验证前提推出。
    action: {kind: synthesize, instruction: Use only checked public claims. / 仅使用已检查公开命题。, uses_tool: false, side_effect: false}
    required_evidence_types: [test]
    checkpoint:
      checkpoint_id: CHECK_SYNTHESIS
      checkpoint_version: 1.0.0
      validator_type: deterministic
      pass_criteria: {all_inputs_verified: true}
      on_failure: terminate
    data_gap_policy: terminate
    budget_allocation: {reasoning_tokens: 500, latency_ms: 1000, model_calls: 1, tool_calls: 0, parallel_paths: 0, iterations: 0, retries: 0, total_cost_units: 0.2}
final_claim_ids: [CLAIM_FINAL]
```

## Failure And Exit Matrix / 失败与出口矩阵

| Observation / 观察 | Session result / 会话结果 | Required controller action / 控制器必需动作 |
| --- | --- | --- |
| Checkpoint validation passed with all required evidence types, exact evidence/observation bindings, and accountable actor/authority. / 检查点验证通过，证据类型完整，证据与观察精确绑定，执行者与授权可追责。 | `premise_state=verified`; successor unlocks. / 前提标记已验证，解锁后继。 | Continue or bind the plan-bound candidate after the final step. / 继续，末步后绑定与计划关联的候选。 |
| Required evidence is absent, stale, conflicting, or unavailable. / 必需证据缺失、过期、冲突或不可得。 | `status=insufficient_evidence`; successor remains locked. / 状态为证据不足，后继保持锁定。 | Apply the step's `data_gap_policy`: wait, request probe, switch source, escalate, or terminate. / 执行步骤缺口策略。 |
| Local checkpoint fails. / 局部检查点失败。 | `premise_state=blocked`; successor and candidate binding are blocked. / 前提被阻断，后继与候选绑定均阻断。 | Apply the compiled `on_failure` exit. / 执行已编译失败出口。 |
| Competing material explanations appear. / 出现实质竞争解释。 | Chain cannot branch. / 链不得分支。 | Use an allowlisted switch to parallel. / 使用允许规则换到并行。 |
| New evidence requires environment interaction. / 新证据必须通过环境交互取得。 | Chain cannot hide an iteration. / 链不得隐藏迭代。 | Use an allowlisted switch to iterative. / 使用允许规则换到迭代。 |
| Human authority is required. / 需要人工权限。 | `status=human_required`; no successor. / 状态为需要人工，不允许后继。 | Escalate with the shared human-work package. / 使用共享人工工作包升级。 |
| A tool dispatch lacks a live authorizer, uses an unverified/revoked grant, substitutes the plan-bound tool or policy, lacks its one dispatch-observation pair, changes input between phases, reports failure as passed, or does not bind the close observation to the output hash. / 工具分派缺少实时授权器、使用未验证或已撤销授权、替换计划绑定工具或策略、缺少唯一分派—观测对、阶段间更改输入、把失败结果报告为通过，或关闭观察未绑定输出哈希。 | Command-time `ToolAuthorizationError` or `ChainPlanStateError`; replay-time `ChainPlanDriftError`. / 命令期授权错误或状态错误；重放期计划漂移错误。 | Do not execute, close, or unlock the successor; preserve hashes and diagnose the authority, adapter, and controller boundaries. / 不执行、不关闭、不解锁后继；保留哈希并诊断授权源、适配器与控制器边界。 |
| Candidate evidence lacks an exact predecessor, changes source content, rolls back its version, binds another candidate, or incompletely covers final-claim step evidence. / 候选证据缺少确切前驱、更改来源内容、版本回退、绑定其他候选，或未完整覆盖最终命题步骤证据。 | Candidate creation is rejected or the atomic candidate/evidence transaction rolls back. / 拒绝创建候选，或原子候选—证据事务整体回滚。 | Produce corrected immutable evidence revisions; never patch accepted evidence in place. / 生成正确的不可变证据修订，绝不原地修改已接受证据。 |
| Runtime step is absent, out of order, or differs from its bound claim, action, validation artifact, evidence, decision, or allocation; or a candidate is early or unbound. / 运行步骤缺失、乱序，或与绑定的命题、动作、验证制品、证据、决定、分配不一致；或候选过早、未绑定。 | `ChainPlanDriftError`. / 抛出计划漂移错误。 | Stop dispatch, preserve events, diagnose bypass, then start a new authorized run if needed. / 停止分派、保留事件、诊断绕过，必要时新建授权运行。 |

## Observability / 可观测性

The compiled plan resolves the authoritative dependency matrix and embeds required probe versions. For a chain, retain task identity, contract completeness, route, budget, step closure, evidence, drift, validation, stop/escalation, privacy/governance, and probe self-health coverage; tool and outcome coverage are activated or inherited when applicable. / 编译计划解析权威依赖矩阵并嵌入必需探针版本。链式运行保留任务身份、契约完整性、路由、预算、步骤闭环、证据、漂移、验证、停止升级、隐私治理与探针自健康覆盖；适用时激活或继承工具与结果回接覆盖。

Use the shared implemented metrics plus the factory diagnostics `plan_compile_success_rate`, `plan_drift_rate`, `checkpoint_validation_binding_rate`, `budget_pre_reservation_coverage`, `evidence_resolution_rate`, `candidate_evidence_lineage_integrity_rate`, and `readonly_tool_lifecycle_completion_rate`. Bucket by blueprint version, plan version, scene, risk, chain length, checkpoint type, evidence grade, authorization policy, and outcome availability. / 使用共享已实现指标，以及工厂诊断指标 `plan_compile_success_rate`、`plan_drift_rate`、`checkpoint_validation_binding_rate`、`budget_pre_reservation_coverage`、`evidence_resolution_rate`、`candidate_evidence_lineage_integrity_rate` 与 `readonly_tool_lifecycle_completion_rate`；并按蓝图版本、计划版本、场景、风险、链长、检查点类型、证据等级、授权策略和后验可用性分桶。

The seven factory metrics are registered and publishable with a complete metric envelope, but deliberately remain outside `gate_eligible` until owned thresholds and promotion evidence are approved. Compiler, capability-preflight, and rejected-authorization reasons remain categorical diagnostics, not ratios. None of these diagnostics may drive release or a protected transition. / 七项工厂指标已注册，具备完整指标信封时可发布，但在负责人阈值与晋升证据获批前仍刻意不进入 `gate_eligible`。编译器、能力预检和被拒授权原因仍是分类诊断，而不是比率。这些诊断均不得驱动放行或受保护转换。

Retain categorical counts for candidate-lineage rejection, authorization rejection, tool/policy substitution, failed-tool-as-passed, and atomic candidate/evidence rollback. The two registered ratios cover accepted candidate-lineage integrity and dispatch-to-observation lifecycle completion; rejection reasons and rollback causes remain diagnostic event views until separately registered. / 保留候选血缘拒绝、授权拒绝、工具或策略替换、把工具失败冒充通过，以及候选—证据原子回滚的分类计数。两项已注册比率覆盖已接受候选的血缘完整性与分派到观测的生命周期完成度；拒绝原因和回滚原因在另行注册前仍属于诊断事件视图。

## Constraints And Acceptance / 约束与验收

Current reference limits / 当前参考限制：

- No hidden automatic decomposition: another component may propose a blueprint, but the persisted proposal must pass Schema and semantic validation. / 不做隐藏式自动拆解；其他组件可以提出蓝图，但持久化提案必须通过 Schema 与语义校验。
- No in-chain retry or repair loop: retry allocation is zero; repair uses an explicit iterative switch or a new linked run. / 链内不做重试或修复循环；重试分配为零，修复使用显式迭代换路或新关联运行。
- Data-gap outcomes such as `wait`, `request_probe`, and `switch_source` are controller instructions, not silent step reopening. The reference session blocks the current prefix; resumption requires an authorized linked run or an allowlisted iterative switch. / `wait`、`request_probe`、`switch_source` 等数据缺口结果是控制器指令，不会静默重开步骤。参考会话会阻断当前前缀；恢复需要经授权的新关联运行或许可的迭代换路。
- No side effects: a read-only query is allowed only with an exact plan-bound tool and authorization policy, a live-verified grant, one-call budget, `PROBE_0007`, and the dispatch/observation lifecycle. The adapter persists bindings and hashes rather than raw input/output; external writes belong outside this reasoning factory. / 不产生副作用；只读查询只有在工具与授权策略精确绑定、授权实时验证通过、预算恰为一次调用、启用 `PROBE_0007` 且完成分派—观测生命周期时才允许。适配器只持久化绑定与哈希而非原始输入输出；外部写入不属于本推理工厂。
- `JsonlEventStore` durably persists the event stream, not the sealed plan or contract. Store those authority artifacts beside the stream. The adapter rewrites an atomic snapshot and is intended for modest local workloads; use a transactional database adapter for high-volume or multi-writer production. / `JsonlEventStore` 持久化事件流，但不持久化封存计划或契约；必须把这些权威制品与事件流并置保存。该适配器通过原子快照重写实现，适合轻量本地负载；高吞吐或多写者生产环境应使用事务数据库适配器。
- Self-hashes detect accidental corruption but are not hostile-tamper-proof because an attacker with write access can recompute them. `tool_authorizer` adds live verification, but its trust is only as strong as the injected verifier and authority source. Production storage should add authenticated signatures or a trusted digest ledger plus append-only retention. / 自哈希可检测意外损坏，但拥有写权限的攻击者可重新计算哈希，因此不能抵御恶意篡改。`tool_authorizer` 增加实时校验，但可信度取决于注入验证器与授权源；生产存储还应增加认证签名或可信摘要账本及仅追加留存。
- The reference guard resolves every step binding to an immutable versioned evidence record and enforces evidence type, provenance, freshness, integrity, independent-source count, claim coverage, observation binding, and concrete actor/authority for a passed checkpoint. Production adapters must additionally authenticate source access and retain the referenced source material. / 参考守卫把每个步骤绑定解析到不可变的版本化证据记录，并对通过检查点强制证据类型、来源、新鲜度、完整性、独立来源数量、命题覆盖、观察绑定及具体执行者/授权；生产适配器还必须认证来源访问并留存被引用的源材料。

Acceptance checklist / 验收清单：

- Blueprint, plan, and checkpoint-validation artifacts pass their Draft 2020-12 Schemas and semantic validators. / 蓝图、计划与检查点验证制品通过 Draft 2020-12 Schema 和语义校验器。
- Recompiling the same blueprint and contract returns byte-equivalent plan content. / 同一蓝图与契约重复编译得到逐字节等价计划。
- Runtime capability preflight rejects every normative condition the executor cannot enforce. / 运行时能力预检拒绝执行器无法落实的任何规范条件。
- Budget allocation fits the sealed contract in every dimension, is reserved before dispatch, and is reconciled exactly once against actual use before step closure. / 每一预算维度都不超过封存契约，并在分派前完成预留、在步骤关闭前按实际用量精确结算一次。
- Every successor consumes only an explicitly verified predecessor claim. / 每个后继只消费显式验证通过的前驱命题。
- Failed, insufficient, or human-required checkpoints cannot unlock a successor or candidate. / 失败、证据不足或需人工的检查点不能解锁后继或候选。
- Passed checkpoint validations bind the exact plan, step, criteria, observation, versioned evidence records, actor, and authority, and meet contract-owned evidence sufficiency. / 通过的检查点验证精确绑定计划、步骤、标准、观察、版本化证据记录、执行者与授权，并满足契约拥有的证据充分性规则。
- Every tool step binds one exact versioned read-only tool and authorization policy, accepts only a live-verified concrete grant, emits one ordered dispatch-observation pair with stable authorization bindings, binds a passed close observation to the successful output hash, and reports exactly one tool call. / 每个工具步骤绑定一个确切版本的只读工具与授权策略，只接受实时验证通过的具体授权，生成一组授权绑定稳定的有序分派—观测事件，把通过时的关闭观察绑定到成功输出哈希，并精确报告一次工具调用。
- Reopening `JsonlEventStore` restores exact event envelopes, per-run sequence, idempotency indexes, and replay; failed durable commits leave both memory and the prior disk snapshot unchanged. / 重新打开 `JsonlEventStore` 后可恢复确切事件信封、逐运行序列、幂等索引与重放；持久提交失败时，内存与旧磁盘快照均保持不变。
- Every candidate event binds the exact plan and final-claim set plus an ordered, complete set of higher-version candidate evidence revisions whose predecessor record bindings and source content replay exactly. / 每个候选事件除绑定确切计划与最终命题集合外，还绑定一组有序、完整的更高版本候选证据修订；其前驱记录绑定与来源内容可被精确重放。
- Required probe bindings are complete and reproducible. / 必需探针绑定完整且可复算。
- Tampered plan, checkpoint, contract, or probe bindings are rejected. / 被篡改的计划、检查点、契约或探针绑定会被拒绝。
- No private reasoning field or state-changing action enters the blueprint, plan, step, candidate, or event stream. / 蓝图、计划、步骤、候选与事件流均不含私密推理字段或状态修改动作。
