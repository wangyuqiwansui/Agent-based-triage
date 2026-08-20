# Governed Reflection Execution Flow / 受治理反思执行流程

Version / 版本: `1.0.0`

Status / 状态: Reference Runtime Contract / 参考运行时契约

This reference turns reflection from an unconstrained “think again” prompt into an auditable control loop. It governs whether reflection may start, what may change, how before-and-after results remain comparable, who authorizes a change, which independent checks must run, and how the loop stops. / 本参考把无约束的“再想一次”提示转化为可审计控制闭环，治理反思能否启动、允许改变什么、前后结果如何保持可比、由谁授权改变、必须运行哪些独立检查以及循环怎样停止。

It is a cross-cutting protocol for the existing Reflection cells—Generator-Critic, Skill Package, Self-Heal Loop, and Experience Replay. It does not create a fourth base, rename a matrix cell, or replace those pattern identities. / 它是现有反思单元——生成者-评审者、技能包、自愈循环和经验回放——的跨切协议；不新增第四基座、不重命名矩阵单元，也不替代这些模式身份。

## Quick Navigation / 快速导航

- [Normative Artifacts / 规范制品](#normative-artifacts--规范制品)
- [Admission And Routing / 准入与路由](#admission-and-routing--准入与路由)
- [State Machine / 状态机](#state-machine--状态机)
- [Baseline Change Result / 基线改变结果](#baseline-change-result--基线改变结果)
- [Independent Revalidation And Anti-Gaming / 独立复验与反投机](#independent-revalidation-and-anti-gaming--独立复验与反投机)
- [Events And Observation Pack / 事件与观察包](#events-and-observation-pack--事件与观察包)
- [Stopping Recovery And Learning / 停止恢复与学习](#stopping-recovery-and-learning--停止恢复与学习)
- [Acceptance / 验收](#acceptance--验收)

## Normative Artifacts / 规范制品

Use these files as the executable source of truth / 以下文件是可执行事实源：

- [`reflection-contract.schema.json`](../schemas/reflection-contract.schema.json): admission decision, reviewed subject, frozen baseline, signal independence, allowed change targets, validator policy, budget, rollback, and handoff. / 准入决定、被审对象、冻结基线、信号独立性、允许改变对象、验证器策略、预算、回滚与交接。
- [`reflection-event.schema.json`](../schemas/reflection-event.schema.json): immutable lifecycle events with stable identity, sequence, state transition, contract binding, subject version, idempotency key, and public payload. / 带稳定标识、顺序、状态转换、契约绑定、对象版本、幂等键与公开载荷的不可变生命周期事件。
- [`reflection-round-observation.schema.json`](../schemas/reflection-round-observation.schema.json): the comparable baseline-change-result record for one round, including new signal, deviation, validation, regression, attribution, outcome, and event bindings. / 单轮可比“基线—改变—结果”记录，包含新信号、偏差、复验、回归、归因、结果与事件绑定。
- [`reflection_runtime.py`](../runtime/reflection_runtime.py): deterministic state coordinator and semantic guards. / 确定性状态协调器与语义闸门。
- [`workflow-observability-probes.md`](workflow-observability-probes.md): probe, metric, and hard-alert semantics. / 探针、指标与硬告警语义。

For route `generator_critic`, additionally read [`reflection-chain.md`](patterns/reflection/reflection-chain.md). Use the six [`generator-critic-*.schema.json`](../schemas/generator-critic-contract.schema.json) artifacts and [`generator_critic.py`](../runtime/generator_critic.py) to bind immutable artifact revisions, evidence-bucketed reviews, deterministic policy decisions, explicit re-review, receipts, and release-version verification. Construct `GeneratorCriticSession` with `build_shared_reflection_guard(contract, events_provider, observations_provider)`, and pass `reflection_subject_binding_for_artifact(artifact)` to `ReflectionSession.record_change_applied()`. The adapter validates this contract's complete public event stream and round observation, checks the exact mapped artifact, and derives a versioned assurance binding for each protected Generator-Critic boundary. The dedicated contract binds this shared reflection contract and does not replace shared admission, change authorization, independent revalidation, rollback, attribution, or learning governance. / 路由为 `generator_critic` 时，还要读取 [`reflection-chain.md`](patterns/reflection/reflection-chain.md)。使用六个生成评审 Schema 及 [`generator_critic.py`](../runtime/generator_critic.py) 绑定不可变工件修订、证据分桶评审、确定性策略裁决、显式复审、回执及发布版本校验。使用 `build_shared_reflection_guard(contract, events_provider, observations_provider)` 构造 `GeneratorCriticSession`，并把 `reflection_subject_binding_for_artifact(artifact)` 传给 `ReflectionSession.record_change_applied()`。适配器校验本契约的完整公开事件流与轮次观察、核对精确映射工件，并为每个生成评审受保护边界派生版本化保证绑定。专用契约绑定本共享反思契约，不替代共享准入、改变授权、独立复验、回滚、归因或学习治理。

The runtime records externally verifiable claims and evidence bindings only. Never request, store, infer, or expose private chain-of-thought or 私密思维过程. / 运行时只记录外部可核验的声明与证据绑定；不得请求、保存、推断或暴露私密思维过程。

## Admission And Routing / 准入与路由

Reflection is conditional, not a mandatory tail step. An automatic reflection instance is admitted only when its contract binds all of the following / 反思是条件节点，不是固定尾节点。自动反思只有在契约绑定以下全部内容时才准入：

1. Trigger and reviewed version / 触发原因与被审版本。
2. Frozen baseline, criteria, validators, regression scope, and environment state when relevant / 冻结基线、判定标准、验证器、回归范围及适用的环境状态。
3. A qualified new result signal, or a bounded authorized evidence-acquisition plan / 有效的新结果信号，或有界且已授权的取证计划。
4. Explicit allowed and forbidden change targets plus exact authorizer binding / 明确的允许与禁止改变对象，以及精确授权器绑定。
5. Independent revalidation and comparison policy / 独立复验与比较策略。
6. Round, no-progress, rollback, handoff, and terminal-outcome policy / 轮次、无进展、回滚、交接与终态策略。

The admission result is one of `admitted`, `needs_evidence`, `not_applicable`, `blocked`, or `human_required`. Route it deterministically / 准入结果只能是上述五种状态，并按以下规则确定性路由：

| Eligibility / 准入状态 | Legal route / 合法路由 | Meaning / 含义 |
| --- | --- | --- |
| `admitted` | `generator_critic`, `self_heal`, `experience_replay`, `skill_lifecycle` | A governed feedback loop may change its declared object. / 可由受治理反馈闭环改变声明对象。 |
| `needs_evidence` | `evidence_collection` | Acquire a named missing signal; do not pretend to improve yet. / 获取指定缺失信号，不得伪称改善。 |
| `not_applicable` | `release` | Required checks already pass and no qualified deviation remains. / 必需检查已通过且没有有效偏差。 |
| `blocked` | `human_triage` | Policy, permission, or recoverability prevents automatic work. / 策略、权限或可恢复性阻止自动处理。 |
| `human_required` | `human_triage` | The decision requires accountable human judgment. / 决策需要可问责的人工判断。 |

An unknown route never defaults to self-heal. Fail closed and use human triage. / 未知路由不得默认进入自愈；应默认阻断并转人工分诊。

## State Machine / 状态机

The authoritative admitted path is / 已准入路径的权威状态机如下：

```text
candidate
  -> admitted
  -> baseline_frozen
  -> round_active
  -> change_proposed
  -> change_authorized
  -> change_applied
  -> revalidating
  -> round_closed | accepted | rolled_back | handed_off | rejected | aborted
```

An evidence-only round may move from `round_active` to `round_closed`, `handed_off`, `rejected`, or `aborted` without a change, but it may continue only after measurable information progress. / 纯取证轮可从 `round_active` 进入 `round_closed`、`handed_off`、`rejected` 或 `aborted` 而不发生改变，但只有出现可测信息进展时才能继续。

Proposal, authorization, application, and release are separate authorities. A proposed change has no permission to act; a successfully applied change has no permission to declare success; a validator pass has no permission to promote a Skill. / 提议、授权、应用和放行属于不同权限。改变提案不具备行动权限；成功应用的改变不具备声明成功的权限；验证器通过也不具备晋升 Skill 的权限。

Use `ReflectionSession` to enforce transitions. The reference runtime coordinates externally performed work; it never performs the repair or side effect itself. / 使用 `ReflectionSession` 强制状态转换。参考运行时只协调外部完成的工作，绝不自行执行修复或副作用。

## Baseline Change Result / 基线改变结果

Every improvement claim binds three separately versioned parts / 每个改善声明必须分别绑定三个版本化部分：

| Part / 部分 | Required contents / 必需内容 |
| --- | --- |
| Baseline / 基线 | Exact subject version, criteria, validator versions, regression scope, environment or fixture, predeclared metric ID and measured value, measurement evidence, and freeze time. / 精确对象版本、标准、验证器版本、回归范围、环境或夹具、预声明指标 ID 与测量值、测量证据及冻结时间。 |
| Change / 改变 | Target, proposal version, authorization, applied new subject version, and any validator-change approval. / 改变对象、提案版本、授权、应用后的新对象版本及任何验证器改变审批。 |
| Result / 结果 | Candidate, criteria, and environment bindings; mandatory and regression verdicts; metric ID; the contract-owned baseline value and measured result value; recomputable delta and threshold verdict; unique independent-signal bindings and recomputed count; comparison state; evidence; and terminal outcome. / 候选、标准与环境绑定；必选与回归裁定；指标 ID；契约拥有的基线值与已测结果值；可重算增量与阈值裁定；唯一独立信号绑定及重算数量；可比状态；证据与终态结果。 |

Signal counts are never trusted as caller-supplied facts. The runtime derives the count from the unique evidence bindings of the one qualified signal set for that round, and the same binding cannot be consumed again by a later round. / 信号数量绝不作为调用方自报事实直接信任；运行时从本轮唯一有效信号集合的唯一证据绑定重算数量，同一绑定不得被后续轮次再次消费。

`observed_unattributed` means the result improved but causality is not established. `verified_improvement` means the result is comparable, independently revalidated, above its contract threshold, and regression-free; it still does not imply a specific causal attribution unless the attribution evidence independently supports that claim. / `observed_unattributed` 表示结果改善但因果关系未建立。`verified_improvement` 表示结果可比、经过独立复验、达到契约阈值且无回归；除非归因证据另行支持，它仍不自动表示改善由某个具体改变导致。

Record deviation and attribution separately. A deviation is an observed gap. An attribution hypothesis states both a predicted observable and a falsifier, discloses confounders, and remains a hypothesis until controlled evidence justifies the next state. Attribution states advance one evidence level at a time—hypothesis, correlation, controlled replay, intervention—and every promotion binds a matching `evidence_kind`; ordinary evidence cannot be relabeled as an intervention. / 偏差与归因必须分开记录。偏差是观测到的差距；归因假设必须同时给出可预测观察与反证条件、披露混杂因素，并在受控证据足够前保持为假设。归因状态按“假设、相关、受控回放、干预”逐级晋升，每次晋升都绑定匹配的 `evidence_kind`；普通证据不得重标为干预证据。

## Independent Revalidation And Anti-Gaming / 独立复验与反投机

Acceptance requires all of the following / 接受改变必须同时满足：

- The exact changed subject version was checked. / 检查了精确的改变后对象版本。
- Every mandatory and regression validator bound by the contract ran. / 契约绑定的全部必选与回归验证器均已运行。
- The required number of independent signals exists. / 达到所需独立信号数。
- The before-and-after comparison is `comparable` or independently rebased under an approved policy. / 前后比较为 `comparable`，或已按批准策略独立重建基线。
- Target-relevant result progress meets the predeclared threshold. / 目标相关结果进展达到预声明阈值。
- Previous passes, hard constraints, and high-risk invariants have no blocking regression. / 原有通过项、硬约束和高风险不变量没有阻断级回归。
- No validator gaming is present. / 不存在验证器投机。

Validator gaming includes deleting a failing test, skipping a mandatory check, narrowing a denominator, changing a scoring prompt, replacing a validator inside the loop without independent approval, or reporting a pass from a different candidate version. / 验证器投机包括删除失败用例、跳过必选检查、缩小分母、改变评分提示、未经独立审批在循环内替换验证器，或使用不同候选版本的通过结果。

A contract may forbid validator changes. If it allows them, the general change authorizer and validator-change authorizer must be distinct at contract-seal time. The replacement comparison must bind the before-subject, criteria, environment, validator and regression sets, metric ID and measured baseline value, external reconstruction evidence, and the exact validator-change approval; its binding hash is recomputed before acceptance. Such a result is `independently_rebased`, never silently treated as the original unchanged comparison. / 契约可以禁止修改验证器。若允许，封存契约时一般改变授权器与验证器改变授权器就必须不同。替代比较必须绑定改变前对象、标准、环境、验证器与回归集合、指标 ID 与已测基线值、外部重建证据及精确的验证器改变审批，并在接受前重算其绑定哈希；此类结果标记为 `independently_rebased`，不得静默冒充原口径比较。

Any blocking regression or validator gaming prevents both `continue` and `accepted`. The legal handling is rollback, explicit rejection, governed handoff, or abort. / 任何阻断级回归或验证器投机都会阻止 `continue` 与 `accepted`；合法处理只能是回滚、明确拒绝、受治理交接或中止。

## Events And Observation Pack / 事件与观察包

Once reflection starts, emit a contiguous event sequence as applicable / 反思启动后按路径发出连续事件序列：

```text
reflection_started
reflection_eligibility_evaluated
reflection_routed
reflection_baseline_frozen
reflection_round_started
reflection_signal_recorded              # evidence-plan rounds only / 仅取证计划轮
deviation_detected
attribution_evidence_recorded           # one event per evidence-level promotion / 每级归因晋升一个事件
change_proposed
change_authorized | change_rejected
change_applied
revalidation_started
revalidation_finished
rollback_started                     # failed changed version only / 仅失败的改变后版本
rollback_applied
rollback_verified
reflection_round_finished
learning_promotion_evaluated            # separately governed / 独立治理
reflection_stopped
```

Conditional events are not fabricated. A non-admitted candidate has no baseline or round events; an evidence-only round has no change or revalidation events. Every emitted event is Schema-valid, self-hashed, sequence-bound, contract-bound, and idempotently identifiable. / 不得伪造条件事件。未准入候选没有基线或轮次事件；纯取证轮没有改变或复验事件。每个已发事件都必须通过 Schema、具备自哈希、顺序绑定、契约绑定与幂等标识。

At round close, persist one observation pack binding all events for that round. Contract-level validation requires the complete event stream and replays it: subject evolution, signal consumption, attribution promotions, proposal-authorize-apply, revalidation, learning, and stop records must match the pack exactly. Recomputing only an observation hash cannot legitimize a rewritten history. / 轮次关闭时持久化一个绑定本轮全部事件的观察包。契约级校验必须提供并重放完整事件流：对象演进、信号消费、归因晋升、提议—授权—应用、复验、学习与停止记录都必须与观察包精确一致；仅重算观察包哈希不能使被改写的历史合法化。

## Stopping Recovery And Learning / 停止恢复与学习

`continue` is legal only when the round produced result progress or information progress and every applicable budget remains. More text, another same-source self-review, a semantically equivalent patch, a noisy score fluctuation, or more evidence records with no decision impact is not progress. / 只有轮次产生结果进展或信息进展且所有适用预算仍有余额时，`continue` 才合法。更多文字、再次同源自评、语义等价补丁、噪声范围内分数波动，或对决策无影响的更多证据记录，都不算进展。

Enforce three separate bounds / 强制三类独立上限：

- total rounds / 总轮次；
- consecutive rounds without result progress / 连续无结果进展轮次；
- information-only rounds / 仅信息进展轮次。

Every terminal outcome carries a stop reason. `rolled_back` is not a label: it is legal only after an applied changed version emits `rollback_started`, consumes the exact contract `rollback_binding`, emits `rollback_applied` with application evidence, restores the round's before-subject, and emits `rollback_verified` with the mandatory validator set and verification evidence. The observation ends at the restored subject and separately retains the failed changed version. Unknown side effects or an uncertain environment terminal are handed off for reconciliation; they are never called success. / 每个终态结果都必须携带停止原因。`rolled_back` 不是一个文本标签：只有已应用的改变后版本发出 `rollback_started`、消费契约中的精确 `rollback_binding`、以应用证据发出 `rollback_applied`、恢复本轮改变前对象，并以必选验证器集合及验证证据发出 `rollback_verified` 后才合法。观察包以恢复对象结束，同时单独保留失败的改变后版本。副作用未知或环境终态不确定时应交接对账，绝不得称为成功。

A successful round may create only a learning candidate. When learning governance is enabled, an accepted round must record an explicit candidate, promoted, or rejected decision. Promotion into persistent memory, a checklist, rule, policy, or Skill additionally requires the contract-bound owner, exact promotion authorizer, minimum unique evidence set, and a separate `learning_promotion_evaluated` event. The evidence record should cover task distribution, sample size, comparable baseline, success and risk metrics, recurrence or replay, version, rollback, and expiry. A new Skill version does not inherit old validation automatically. / 成功轮次最多产生学习候选。启用学习治理时，已接受轮必须明确记录候选、已晋升或已拒绝决定。晋升为持久记忆、检查清单、规则、策略或 Skill 还必须具备契约绑定的责任人、精确晋升授权器、最小唯一证据集合，并单独发出 `learning_promotion_evaluated` 事件；证据记录应覆盖任务分布、样本量、可比基线、成功与风险指标、复发或回放、版本、回滚和有效期。新 Skill 版本不得自动继承旧版本验证结果。

## Acceptance / 验收

A reflection implementation is acceptable only when / 反思实现仅在以下条件全部满足时可验收：

- Non-admitted cases close explicitly without manufactured rounds. / 未准入情况明确关闭且不伪造轮次。
- Admitted cases freeze the baseline before any proposal. / 已准入情况在任何提案前冻结基线。
- Change proposal, authorization, application, and release remain distinct. / 改变提议、授权、应用与放行保持分离。
- Every accepted change is version-bound, independently revalidated, comparable, and regression-free. / 每个已接受改变都绑定版本、经过独立复验、可比且无回归。
- Validator gaming fails closed. / 验证器投机默认阻断。
- Continuation requires measurable progress and respects all budgets. / 继续循环要求可测进展并遵守全部预算。
- Every terminal path has a reason, recovery or handoff path, and closed event chain. / 每条终态路径都有原因、恢复或交接路径以及闭合事件链。
- Attribution strength never exceeds its evidence, and learning promotion remains a separate governed lifecycle. / 归因强度不超过证据等级，学习晋升保持为独立受治理生命周期。
