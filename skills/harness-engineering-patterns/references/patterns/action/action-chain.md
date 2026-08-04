# Prompt Chaining / 提示链

Cell / 交织点: action-chain / 行动 x 链式
Capability / 能力: Action / 行动
Mode / 模式: Chain / 链式
Pattern ID / 模式 ID: `PATTERN_0035`
Cell ID / 单元 ID: `CELL_ACTION_CHAIN`
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Engineering Extension Basis / 工程扩展依据: “提示链 Workflow 执行流程” and “提示链 Workflow 可观测性探针” (user-provided design drafts, 2026-08-04, external descriptive evidence rather than runtime proof). / 《提示链 Workflow 执行流程》与《提示链 Workflow 可观测性探针》（用户提供的设计草案，2026-08-04，属于外部描述性证据，不等同于运行证明）。

Use this file as the design pattern source for this 7x6 matrix intersection. Keep `references/registry.json` authoritative for pattern identity, lifecycle, provenance, and maturity. / 将本文档作为该 7x6 交织点的设计模式来源；模式身份、生命周期、来源和成熟度以 `references/registry.json` 为权威。

## Quick Navigation / 快速导航

- [Design Pattern / 设计模式](#design-pattern--设计模式)
- [System Boundary / 系统边界](#system-boundary--系统边界)
- [Hard Invariants / 硬不变量](#hard-invariants--硬不变量)
- [Execution Lifecycle / 执行生命周期](#execution-lifecycle--执行生命周期)
- [Step And Handoff Contract / 步骤与交接契约](#step-and-handoff-contract--步骤与交接契约)
- [Artifact Contract / 工件契约](#artifact-contract--工件契约)
- [Four-Layer Gate / 四层闸门](#four-layer-gate--四层闸门)
- [Safety Boundary / 安全边界](#safety-boundary--安全边界)
- [Failure Recovery / 失败恢复](#failure-recovery--失败恢复)
- [Pattern Template / 模式模板](#pattern-template--模式模板)
- [Acceptance / 验收](#acceptance--验收)

## Design Pattern / 设计模式

Prompt Chaining decomposes a deterministic multi-step action into single-responsibility steps. Each step emits a typed, versioned, traceable artifact; an explicit contract and gate validate that artifact before it can be registered or consumed by the next step. The design objective is not to increase prompt count, but to create verifiable handoff boundaries that stop defective artifacts from propagating. / 提示链把确定性的多步行动拆成单一职责步骤。每一步产出带类型、版本和来源链的可追踪工件；该工件只有通过显式契约与闸门校验后，才能注册或被下一步消费。设计目标不是增加 Prompt 数量，而是建立可验证的交接边界，阻止错误工件继续传播。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Action / 行动 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; the source matrix names Prompt Chaining at Action x Chain in arXiv:2605.13850; the lifecycle, artifact, gate, safety, recovery, and probe contracts below are engineering extensions. / 来源矩阵在 arXiv:2605.13850 的“行动 x 链式”单元命名了提示链；下述生命周期、工件、闸门、安全、恢复和探针契约属于工程扩展。
- 问题 / Problem: A monolithic prompt hides intermediate defects, relies on implicit conversational state, discovers failures late, and often forces a full rerun. / 巨型提示会隐藏中间缺陷、依赖隐式会话状态、延迟暴露错误，并经常迫使整链重跑。
- 架构方案 / Architectural Solution: Split work at natural validation boundaries; bind every step to named inputs, a typed output artifact, evidence requirements, a four-layer gate, and a declared recovery policy. / 在自然验证边界拆分工作；把每一步绑定到命名输入、类型化输出工件、证据要求、四层闸门和预先声明的恢复策略。
- 工程权衡 / Engineering Trade-offs: Smaller steps are easier to test, replay, and diagnose, but introduce serialization, validation latency, artifact storage, and contract-version overhead. A chain is intentionally weak when dynamic branching, parallel search, feedback-driven iteration, or replanning dominates. / 更小的步骤更易测试、重放和诊断，但会引入串行化、验证时延、工件存储与契约版本成本。当动态分支、并行搜索、反馈迭代或重规划占主导时，链式模式天然较弱。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when action is represented as a deterministic sequence of prompts or tool steps and each handoff can be validated before continuation. / 当行动由确定性的提示或工具步骤序列表示，且每次交接都能在继续前验证时使用。

### Fit And Non-Fit / 适配与不适配

Choose Prompt Chaining when step order is stable, every step has one bounded responsibility, intermediate outputs can be materialized as artifacts, and a failed handoff should stop the next step. / 当步骤顺序稳定、每步只有一个有界职责、中间结果能够工件化，且交接失败应阻断下一步时，选择提示链。

Do not force the workflow into this cell when / 出现以下情况时不要强行使用本单元：

- The next step depends on dynamic classification or tool ownership; use [Tool Dispatch / 工具分派](action-routing.md). / 下一步取决于动态分类或工具归属；使用工具分派。
- Independent paths should execute concurrently; evaluate [Action Parallel / 行动并行](action-parallel.md). / 独立路径应并发执行；评估行动并行。
- Failure changes the remaining plan or dependency graph; use [Plan-and-Execute / 计划并执行](action-orchestration.md). / 失败会改变剩余计划或依赖图；使用计划并执行。
- Feedback must change the next attempt repeatedly; evaluate [Action Loop / 行动循环](action-loop.md). / 反馈必须反复改变下一次尝试；评估行动循环。

## System Boundary / 系统边界

Prompt Chaining owns ordering, handoff contracts, artifact lineage, gate decisions, and legal recovery transitions. It does not itself own tool authorization, sandbox enforcement, durable side-effect idempotency, or human approval. / 提示链负责顺序、交接契约、工件谱系、闸门决定与合法恢复转换；它本身不负责工具授权、沙箱执行、持久副作用幂等或人工审批。

| Component / 组件 | Responsibility / 职责 | Must Not Imply / 不得暗示 |
| --- | --- | --- |
| Chain coordinator / 链协调器 | Select the next declared step, bind validated inputs, enforce state transitions, and stop at terminal state. / 选择下一声明步骤、绑定已验证输入、执行状态转换并在终态停止。 | Sequence is authorization. / 顺序即授权。 |
| Step executor / 步骤执行器 | Perform one declared task and emit one or more contract-bound artifacts. / 执行一个声明任务并产出一个或多个契约绑定工件。 | Free access to conversation memory or undeclared tools. / 可自由读取会话记忆或未声明工具。 |
| Artifact registry / 工件注册表 | Preserve immutable identity, version, digest, lineage, validation state, and lifecycle. / 保存不可变身份、版本、摘要、谱系、验证状态和生命周期。 | Registration proves business truth. / 注册即证明业务事实。 |
| Gate evaluator / 闸门评估器 | Apply format, structure, semantic, and factual checks and return an explicit decision. / 执行格式、结构、语义和事实检查并返回显式决定。 | A model assertion counts as independent validation. / 模型断言等同独立验证。 |
| Tool Dispatch and governance / 工具分派与治理 | Admit, authorize, sandbox, execute, and classify concrete tool actions. / 对具体工具动作执行准入、授权、沙箱、执行与结果分类。 | Chain inclusion grants permission. / 进入链即获得权限。 |
| Workflow Probe / 工作流探针 | Observe execution quality and propose versioned optimization. / 观察执行质量并提出版本化优化建议。 | Observation silently mutates control flow. / 观察可静默修改控制流。 |

## Hard Invariants / 硬不变量

1. Give every step one explicit responsibility, stable `step_id`, declared input contract, output contract, constraints, evidence requirements, and recovery policy. / 每步只有一个显式职责，并具备稳定 `step_id`、输入契约、输出契约、约束、证据要求和恢复策略。
2. Pass state through named artifact references; never depend on “whatever remains in context.” / 通过命名工件引用传递状态；绝不依赖“上下文里还剩什么”。
3. Start a step only after every required input artifact is registered and its producing gate returned `pass`. / 只有全部必需输入工件已注册且生产闸门返回 `pass` 后，步骤才能启动。
4. Never register, release, or forward an artifact whose required gate failed or is unknown. / 必需闸门失败或状态未知的工件不得注册、放行或转交。
5. Keep artifact identity, content digest, source lineage, schema version, producing step, and attempt immutable after registration; issue a successor artifact for corrections. / 工件注册后，其身份、内容摘要、来源谱系、Schema 版本、生产步骤和尝试不可变；修正时生成后继工件。
6. Treat sequence as control flow, not permission. Send tool actions through the applicable dispatch, policy, approval, sandbox, idempotency, and result-certainty controls. / 把顺序视为控制流而非权限；工具动作必须经过适用的分派、策略、审批、沙箱、幂等和结果确定性控制。
7. Require every recovery attempt to introduce declared information gain and remain within a positive attempt budget; otherwise escalate or terminate. / 每次恢复尝试必须引入声明的信息增益并受正数尝试预算约束；否则升级或终止。
8. Preserve `failed`, `rejected`, `unknown`, `escalated`, `cancelled`, and missing as distinct states; never coerce them into success or zero. / 保持失败、拒绝、未知、升级、取消和缺失状态相互独立；不得强制转换为成功或数值零。
9. Record public decisions, evidence references, digests, and lifecycle facts; do not collect private chain-of-thought or unnecessary raw sensitive payloads. / 记录公开决定、证据引用、摘要和生命周期事实；不得采集私密思维过程或不必要的原始敏感载荷。
10. Enter `completed` only after the final artifact passes its final output contract and all required protected actions have confirmed terminal outcomes. / 只有最终工件通过最终输出契约，且全部必需受保护动作均获得已确认终态后，才能进入 `completed`。

## Execution Lifecycle / 执行生命周期

```text
initialize
  -> load explicit context
  -> make step ready
  -> execute step
  -> emit candidate artifact
  -> evaluate gate
       -> pass: register artifact -> next declared step
       -> reject: execute bounded recovery policy
       -> unknown: verify or escalate; never guess
  -> evaluate final contract
  -> completed | failed | escalated | cancelled
```

The coordinator persists the last valid transition before starting the next step. A restart reconstructs the chain from registered artifacts, gate decisions, and the step ledger; it does not regenerate already accepted work solely from conversation history. / 协调器在启动下一步前持久化最后一个合法转换。重启时通过已注册工件、闸门决定与步骤台账重建链路；不得仅凭会话历史重新生成已接受工作。

Legal step states / 合法步骤状态：

```text
PENDING -> READY -> RUNNING -> GATING -> PASSED
                              -> REJECTED -> RECOVERING -> READY
                                          -> ESCALATED | FAILED
PENDING | READY -> CANCELLED
```

`PASSED`, `FAILED`, `ESCALATED`, and `CANCELLED` are terminal for one step attempt. A new attempt receives a new `attempt_id`; it never overwrites the prior attempt. / `PASSED`、`FAILED`、`ESCALATED` 和 `CANCELLED` 是单次步骤尝试的终态。新尝试使用新的 `attempt_id`，不得覆盖上一尝试。

## Step And Handoff Contract / 步骤与交接契约

Seal the chain definition before execution. Treat the following YAML as a design-level contract shape; it is not yet a bundled normative JSON Schema or runtime implementation. / 在执行前封存链定义。以下 YAML 是设计层契约形状；当前尚不是内置的规范 JSON Schema 或运行时实现。

```yaml
prompt_chain_contract:
  schema_version: "1.0.0"
  chain_id: "CHAIN_..."
  chain_version: "1.0.0"
  goal: "bounded action goal / 有界行动目标"
  initial_input_contract: "typed initial input / 类型化初始输入"
  final_output_contract: "typed accepted result / 类型化可验收结果"
  steps:
    - step_id: "STEP_..."
      role: "single responsibility / 单一职责"
      task: "one bounded operation / 一个有界操作"
      input_contract:
        artifact_types: []
        schema_versions: []
        required_fields: []
      output_contract:
        artifact_type: "..."
        schema_version: "1.0.0"
        required_fields: []
        quality_criteria: []
      constraints: []
      evidence_requirements: []
      gate_contract:
        format_validators: []
        structure_validators: []
        semantic_validators: []
        factual_validators: []
      action_contract:
        tool_ref: null
        authorization_policy_ref: null
        approval_policy_ref: null
        side_effect_class: "none | read_only | reversible_write | irreversible | external"
      recovery_policy:
        max_attempts: 2
        allowed_actions: [revise_and_retry, rollback, compensate, escalate, fail]
        information_gain_required: true
  state_passing: explicit_artifact_refs
  registration_policy: gate_pass_required
  terminal_states: [completed, failed, escalated, cancelled]
```

Every handoff defines three contracts / 每次交接定义三类契约：

- Input Contract / 输入契约: what the consumer may read, including artifact type, accepted schema versions, required fields, trust class, and lineage. / 消费者可读取什么，包括工件类型、可接受 Schema 版本、必需字段、信任等级与谱系。
- Output Contract / 输出契约: what the producer must deliver, including structure, quality criteria, evidence, and lifecycle state. / 生产者必须交付什么，包括结构、质量判据、证据与生命周期状态。
- Constraint Contract / 约束契约: which invariants, permissions, budgets, privacy rules, and stop conditions apply. / 适用哪些不变量、权限、预算、隐私规则与停止条件。

## Artifact Contract / 工件契约

An artifact is a verifiable, traceable, replayable data object rather than unstructured conversational text. / 工件是可验证、可追踪、可重放的数据对象，而不是无结构会话文本。

```yaml
workflow_artifact:
  artifact_id: "ARTIFACT_..."
  artifact_type: "..."
  schema_version: "1.0.0"
  chain_id: "CHAIN_..."
  run_id: "RUN_..."
  created_by:
    step_id: "STEP_..."
    attempt_id: "ATTEMPT_..."
  created_at: "RFC3339 timestamp"
  source_refs: []
  parent_artifact_ids: []
  content_digest: "sha256:..."
  trust_class: "untrusted | derived | verified"
  sensitivity_class: "public | internal | confidential | restricted"
  lifecycle_state: "candidate | validated | registered | rejected | superseded"
  payload: {}
```

Artifact rules / 工件规则：

- Validate the complete serialized artifact, not a different in-memory draft, and bind the gate decision to its digest. / 校验完整序列化工件而非另一份内存草稿，并把闸门决定绑定到其摘要。
- Register only `validated` artifacts, then make registration append-only; corrections create a new version with predecessor lineage. / 仅注册 `validated` 工件，注册记录保持追加式；修正通过带前驱谱系的新版本完成。
- Keep payload retention separate from trace retention. Prefer digests and resolvable references when raw data is sensitive or large. / 将载荷留存与 Trace 留存分离；原始数据敏感或过大时优先保存摘要与可解析引用。
- Reject incompatible schema versions before semantic use; never silently coerce an unknown version. / 在语义使用前拒绝不兼容 Schema 版本；不得静默强转未知版本。

## Four-Layer Gate / 四层闸门

Evaluate layers in order and stop at the first blocking failure. Record every executed validator, input digest, rule version, decision, reason, and recovery route. / 按顺序执行各层检查，并在首个阻断失败处停止。记录每个已执行验证器、输入摘要、规则版本、决定、原因和恢复路由。

| Layer / 层级 | Question / 问题 | Typical Checks / 典型检查 |
| --- | --- | --- |
| 1. Format / 格式 | Can the artifact be parsed deterministically? / 工件能否被确定性解析？ | Encoding, syntax, serialization, size limit. / 编码、语法、序列化、大小限制。 |
| 2. Structure / 结构 | Does it match the declared type and schema version? / 是否符合声明类型和 Schema 版本？ | Required fields, types, enum, cross-field bindings, digest. / 必需字段、类型、枚举、跨字段绑定、摘要。 |
| 3. Semantic / 语义 | Do domain invariants and task criteria hold? / 领域不变量与任务判据是否成立？ | Consistency, constraints, completeness, state-transition legality. / 一致性、约束、完整性、状态转换合法性。 |
| 4. Factual / 事实 | Are key claims supported by trusted, current, resolvable evidence? / 关键结论是否由可信、新鲜、可解析证据支撑？ | Source version/time/location, independent validator, external receipt, outcome. / 来源版本、时间、位置、独立验证器、外部回执、后验。 |

Gate decisions are `pass`, `reject`, or `unknown`. `unknown` is not a soft pass. A gate may request missing evidence, but only a new artifact and a new gate evaluation can change the decision. / 闸门决定为 `pass`、`reject` 或 `unknown`。`unknown` 不是软放行。闸门可以请求缺失证据，但只有新工件和新闸门评估才能改变决定。

## Safety Boundary / 安全边界

```text
untrusted input / 不可信输入
  -> bounded processing / 有界处理
  -> typed candidate artifact / 类型化候选工件
  -> contract and evidence gates / 契约与证据闸门
  -> validated action intent / 已验证行动意图
  -> Tool Dispatch + policy + approval / 工具分派 + 策略 + 审批
  -> protected action / 受保护动作
```

External input must not directly determine a tool call, write, external send, deployment, financial operation, or other high-risk action. Convert it into a typed candidate artifact, validate it, and independently admit the resulting action. Tool names and parameters remain inside a sealed capability frontier and authorization policy; content inside an artifact is data, never an instruction that overrides the chain contract. / 外部输入不得直接决定工具调用、数据写入、外部发送、部署、资金操作或其他高风险动作。应先将其转换为类型化候选工件并完成验证，再独立准入由此产生的动作。工具名与参数必须受封存能力前沿和授权策略约束；工件内容是数据，绝不是可覆盖链契约的指令。

For state-changing actions, apply the governed Tool Dispatch contract in [action-routing.md](action-routing.md): require current authorization, applicable approval, sandbox boundaries, state evidence, durable idempotency, and explicit result certainty. Do not directly retry an `unknown` side-effect result. / 对改状态动作，应用 [action-routing.md](action-routing.md) 中受治理的工具分派契约：要求当前授权、适用审批、沙箱边界、状态证据、持久幂等和显式结果确定性。副作用结果为 `unknown` 时不得直接重试。

## Failure Recovery / 失败恢复

A retry is legal only when it changes the basis of the next attempt. Declare the information-gain source and persist it with the new attempt. / 只有当重试改变下一次尝试的依据时，重试才合法。必须声明信息增益来源，并随新尝试持久化。

Allowed information gain / 允许的信息增益：

- Re-read a trusted, fresher, or previously missing source. / 重新读取可信、更新或此前缺失的来源。
- Add or clarify a constraint or acceptance criterion. / 增加或澄清约束或验收判据。
- Narrow the task scope or isolate the failing artifact. / 缩小任务范围或隔离失败工件。
- Use a deterministic validator or read-only tool to resolve uncertainty. / 使用确定性验证器或只读工具消除不确定性。
- Obtain a current human decision, approval, or domain correction. / 获取当前人工决定、审批或领域修正。

Recovery actions / 恢复动作：

- `revise_and_retry`: create a new attempt and successor artifact within the positive attempt budget. / 在正数尝试预算内创建新尝试和后继工件。
- `rollback`: restore a verified internal state only when rollback semantics are proven. / 仅在回滚语义已被证明时恢复已验证内部状态。
- `compensate`: issue a separately authorized compensating action for an already confirmed side effect. / 对已确认副作用发起单独授权的补偿动作。
- `escalate`: preserve evidence, uncertainty, and the next legal options for a human or higher controller. / 为人工或更高层控制器保留证据、不确定性和下一合法选项。
- `fail`: terminate with an explicit reason when recovery cannot add information or remain safe. / 当恢复无法增加信息或保持安全时，以显式原因终止。

Never regenerate blindly, reset a passed step, overwrite a registered artifact, or use repeated model sampling alone as evidence of information gain. / 不得盲目重新生成、重置已通过步骤、覆盖已注册工件，也不得把重复模型采样本身当作信息增益证据。

## Observability Integration / 可观测性集成

Instrument step, artifact, gate, recovery, action, terminal, and probe-health boundaries using [action-chain-observability.md](action-chain-observability.md) and the shared [Workflow Observability Probes](../../workflow-observability-probes.md). Keep the observer independent from the workflow; inline intervention is allowed only through named, deterministic, versioned gates. / 使用 [action-chain-observability.md](action-chain-observability.md) 与共享[工作流可观测性探针](../../workflow-observability-probes.md)埋设步骤、工件、闸门、恢复、行动、终态和探针健康边界。观察器与工作流保持独立；只有命名、确定性、版本化的闸门才能内联干预。

Observability Metrics File / 可观测性指标文件: [action-chain-observability.md](action-chain-observability.md)

## Anti-Patterns / 反模式

- Serial prompts with no typed intermediate artifacts. / 只有串联 Prompt，没有类型化中间工件。
- Natural-language handoffs that rely on implicit conversation context. / 依赖隐式会话上下文的自然语言交接。
- A single “looks good” model check standing in for format, schema, semantics, and evidence validation. / 用一次“看起来不错”的模型检查替代格式、Schema、语义和证据验证。
- A failed gate whose output still enters the next step. / 闸门失败后工件仍进入下一步。
- Repeated regeneration with no new evidence, constraint, scope, deterministic check, or human input. / 在没有新证据、新约束、范围变化、确定性检查或人工输入时反复重新生成。
- Untrusted artifact text directly selecting tools or authorizing high-risk actions. / 不可信工件文本直接选择工具或授权高风险动作。
- Treating logs as complete observability while artifact lineage, expected events, and probe health are missing. / 在缺少工件谱系、预期事件和探针健康时，把日志当成完整可观测性。

## Pattern Template / 模式模板

- 状态 / Status: Named candidate / 已命名候选.
- 模式清单 / Patterns: Prompt Chaining / 提示链.
- 诊断用途 / Diagnostic Use: Use when action is represented as a deterministic sequence of prompts or tool steps whose handoffs can be contract-gated. / 当行动由确定性的提示或工具步骤序列表示，且交接可由契约门控时使用。
- 适用工作流节点 / Applicable Workflow Nodes: Deterministic transformation, extraction, validation, staged generation, implementation, and delivery steps. / 确定性转换、抽取、校验、分阶段生成、实现和交付步骤。
- 当前症状 / Current Symptoms: Monolithic prompts hide intermediate failure; late defects force full reruns; state is implicit; outputs lack type, version, lineage, and gate evidence; unsafe content can reach actions. / 巨型提示隐藏中间失败；晚期缺陷迫使整链重跑；状态依赖隐式上下文；输出缺少类型、版本、谱系和闸门证据；不安全内容可能直达行动。
- 适配信号 / Fit Signals: The order is stable, responsibilities are separable, intermediate results can be materialized, and each continuation has a deterministic acceptance boundary. / 顺序稳定、职责可拆分、中间结果可工件化，且每次继续都有确定性验收边界。
- 调整方向 / Adjustment Direction: Replace implicit prompt-to-prompt continuation with explicit step, artifact, contract, gate, registration, recovery, and trace boundaries. / 用显式步骤、工件、契约、闸门、注册、恢复和 Trace 边界替代隐式 Prompt 延续。
- 修改方式 / How To Modify: 1) Cut at natural validation points. 2) Seal the chain and final contract. 3) Give each step one responsibility and named artifact inputs. 4) Define typed output artifacts and four-layer gates. 5) Register only passed artifacts. 6) Route protected actions through dispatch and governance. 7) Require information-gaining bounded recovery. 8) Instrument the complete lifecycle. / 1）在自然验证点切分；2）封存链与最终契约；3）为每步指定单一职责和命名工件输入；4）定义类型化输出工件与四层闸门；5）仅注册通过的工件；6）让受保护动作经过分派与治理；7）要求有信息增益的有界恢复；8）埋设完整生命周期探针。
- 输入 / Inputs: Bounded goal, initial typed input, sealed chain contract, artifact schemas, validators, evidence policy, tool and permission policies, budgets, and stop conditions. / 有界目标、初始类型化输入、封存链契约、工件 Schema、验证器、证据策略、工具与权限策略、预算和停止条件。
- 输出 / Outputs: Accepted final artifact, immutable artifact lineage, step and gate ledger, action receipts, recovery records, terminal reason, and observability report. / 已验收最终工件、不可变工件谱系、步骤与闸门台账、动作回执、恢复记录、终态原因和可观测性报告。
- 风险与治理 / Risks & Governance: Error propagation, schema drift, false pass/rejection, state loss (`FAIL_0006`), runaway recovery (`FAIL_0007`), permission bypass (`FAIL_0005`), non-replayable audit (`FAIL_0010`), unsafe execution (`GOV_0003`), and missing result persistence (`GOV_0002`). Mitigate with explicit artifacts, versioned gates, bounded information-gaining recovery, governed Tool Dispatch, append-only lifecycle records, redaction, and probe self-health. / 风险包括错误传播、Schema 漂移、误放行/误拒绝、状态丢失（`FAIL_0006`）、恢复失控（`FAIL_0007`）、权限绕过（`FAIL_0005`）、审计不可复现（`FAIL_0010`）、不安全执行（`GOV_0003`）和结果未入账（`GOV_0002`）。通过显式工件、版本化闸门、有信息增益的有界恢复、受治理工具分派、追加式生命周期记录、脱敏和探针自健康进行缓解。

## Acceptance / 验收

- Every step has one responsibility and a sealed contract with stable identity and version. / 每步只有一个职责，并具备带稳定身份和版本的封存契约。
- Every consumed artifact was produced, validated, and registered under a resolvable schema and digest-bound lineage. / 每个被消费工件都在可解析 Schema 下完成生产、校验和注册，并具备摘要绑定谱系。
- Every handoff executed all applicable format, structure, semantic, and factual validators before continuation. / 每次交接在继续前执行全部适用的格式、结构、语义和事实验证器。
- Invalid or unknown artifacts cannot silently enter a later step or protected action. / 无效或未知工件不能静默进入后续步骤或受保护动作。
- Every retry has a new attempt identity, positive remaining budget, and recorded information gain. / 每次重试都有新尝试身份、剩余正数预算和已记录信息增益。
- Tool sequencing, authorization, approval, idempotency, sandboxing, and result certainty remain separate controls. / 工具顺序、授权、审批、幂等、沙箱和结果确定性保持为独立控制。
- Restart and audit can reconstruct the last valid state without private chain-of-thought or unnecessary raw sensitive data. / 重启与审计能够在不采集私密思维过程或不必要原始敏感数据的情况下重建最后合法状态。
- Final completion binds the exact accepted artifact, final gate decision, terminal reason, and all required protected-action outcomes. / 最终完成绑定确切已验收工件、最终闸门决定、终态原因和全部必需受保护动作结果。

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. Do not write normal runtime evidence into the bundled curated `trace.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议；不要把普通运行证据写入内置精选 `trace.md`。
