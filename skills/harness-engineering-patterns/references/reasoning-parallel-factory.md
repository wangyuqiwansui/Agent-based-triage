# Reasoning Parallel Factory / 推理并行工厂

Factory ID / 工厂标识: `reasoning-parallel-factory`

Version / 版本: `1.0.0`

Status / 状态: Reference implementation / 参考实现

The factory turns an author-owned Parallel Exploration blueprint plus a sealed reasoning contract into an immutable, replayable branch-and-synthesis plan. It implements `COG_REASONING__TOP_PARALLEL`; it does not grant action permission and does not collect private chain-of-thought. / 本工厂把负责人维护的并行探索蓝图与已封存推理契约编译为不可变、可回放的分支—综合计划。它实现 `COG_REASONING__TOP_PARALLEL`，不授予行动权限，也不采集私密思维链。

## Quick Navigation / 快速导航

- [Use And Boundaries / 适用与边界](#use-and-boundaries--适用与边界)
- [Normative Artifacts / 规范制品](#normative-artifacts--规范制品)
- [Compile Workflow / 编译流程](#compile-workflow--编译流程)
- [Guarded Session / 受守卫会话](#guarded-session--受守卫会话)
- [Leases And Deadlines / 租约与截止时间](#leases-and-deadlines--租约与截止时间)
- [Durable Dispatch And Network Storage / 持久分派与网络存储](#durable-dispatch-and-network-storage--持久分派与网络存储)
- [Recovery And Projection / 恢复与投影](#recovery-and-projection--恢复与投影)
- [Synthesis Contract / 综合契约](#synthesis-contract--综合契约)
- [Observability / 可观测性](#observability--可观测性)
- [Acceptance / 验收](#acceptance--验收)

## Use And Boundaries / 适用与边界

Use the factory when two or more materially different hypotheses, designs, policies, or root causes can be explored independently under one common comparison contract. Prefer chain when there is one dominant dependency path; prefer iterative when evidence appears only after environment interaction. / 当两个或更多具有实质差异的假设、方案、政策或根因可以在同一比较契约下独立探索时使用本工厂。只有一条主导依赖路径时优先链式；证据只能通过环境交互出现时优先迭代。

The v1 reference session supports read-only reasoning branches whose external executors return public candidate and evidence records. It intentionally does not execute branch tool calls or side effects. Tool-enabled branches must use a separately authorized action lifecycle with `PROBE_0007`; do not hide tool work inside a reasoning branch result. / v1 参考会话支持只读推理分支，由外部执行器返回公开候选与证据记录。它有意不执行分支工具调用或副作用。启用工具的分支必须使用独立授权的行动生命周期并启用 `PROBE_0007`；不得把工具工作隐藏在推理分支结果中。

## Normative Artifacts / 规范制品

- Blueprint Schema / 蓝图 Schema: [`reasoning-parallel-blueprint.schema.json`](../schemas/reasoning-parallel-blueprint.schema.json)
- Immutable Plan Schema / 不可变计划 Schema: [`reasoning-parallel-plan.schema.json`](../schemas/reasoning-parallel-plan.schema.json)
- Runtime / 运行时: [`reasoning_parallel_factory.py`](../runtime/reasoning_parallel_factory.py)
- Event projector / 事件投影器: [`reasoning_parallel_projection.py`](../runtime/reasoning_parallel_projection.py)
- Lease and deadline scheduler / 租约与截止调度器: [`reasoning_parallel_scheduler.py`](../runtime/reasoning_parallel_scheduler.py)
- Transactional worker outbox / 事务型工作者发件箱: [`reasoning_parallel_outbox.py`](../runtime/reasoning_parallel_outbox.py)
- Single-node multi-writer event store / 单节点多写者事件库: [`reasoning_event_sqlite_store.py`](../runtime/reasoning_event_sqlite_store.py)
- Network multi-writer event store / 网络多写者事件库: [`reasoning_event_postgres_store.py`](../runtime/reasoning_event_postgres_store.py)
- PostgreSQL worker outbox / PostgreSQL 工作者发件箱: [`reasoning_parallel_postgres_outbox.py`](../runtime/reasoning_parallel_postgres_outbox.py)
- Shared contract and events / 共享契约与事件: [`reasoning-contract.schema.json`](../schemas/reasoning-contract.schema.json), [`reasoning-event.schema.json`](../schemas/reasoning-event.schema.json)
- Probe resolution / 探针解析: [`probe_dependency_matrix.json`](../runtime/probe_dependency_matrix.json)

The blueprint owns candidate space, isolation, material-difference dimensions, common criteria and vetoes, join policy, branch budgets, synthesis budget, and final claims. The plan binds those declarations to one contract, stable runtime IDs, exact budgets, versioned probes, and a content hash. / 蓝图负责候选空间、隔离、实质差异维度、统一判据与否决规则、汇合策略、分支预算、综合预算和最终命题。计划把这些声明绑定到一个契约、稳定运行标识、精确预算、版本化探针和内容哈希。

## Compile Workflow / 编译流程

1. Validate bilingual metadata, candidate count, stable path IDs, and JSON shape. / 校验双语元数据、候选数量、稳定路径标识和 JSON 结构。
2. Reject identical hypotheses, undeclared difference dimensions, insufficient material differences, duplicate criteria or veto IDs, and branch-specific comparison rules. / 拒绝相同假设、未声明差异维度、实质差异不足、重复判据或否决标识，以及分支私有比较规则。
3. Require `execution_mode: parallel`, `primary_topology: parallel`, `reserve_before_launch`, and a shared-input binding equal to the contract normalized input. / 强制 `execution_mode: parallel`、`primary_topology: parallel`、`reserve_before_launch`，且共享输入绑定必须等于契约标准化输入。
4. Require exactly one parallel-path unit per branch and zero for synthesis; reject total allocation above any contract dimension. / 每分支必须精确分配一个并行路径单位，综合为零；任何总分配超过契约维度都拒绝。
5. Resolve `PROBE_0008` and all universal, mode, and supporting-topology probes before producing the plan. / 产出计划前解析 `PROBE_0008` 以及全部通用、模式和支撑拓扑探针。
6. Derive deterministic branch step IDs, synthesis step ID, comparison-rule binding, plan ID, and `plan_hash`. / 确定性派生分支步骤标识、综合步骤标识、比较规则绑定、计划标识与 `plan_hash`。

Compilation fails closed. A changed blueprint, contract, budget, input binding, criterion, veto, or isolation policy produces a different plan; a supplied plan that cannot be reproduced is rejected. / 编译默认阻断。蓝图、契约、预算、输入绑定、判据、否决或隔离策略发生变化都会生成不同计划；无法复现的外部计划会被拒绝。

## Guarded Session / 受守卫会话

Open new governed execution only through `ReasoningParallelFactory.start_session()` and restore durable execution only through `resume_session()`. Both entrypoints check run identity, contract hash, mode, topology, plan reproduction, and event history. / 新建受治理执行只能通过 `ReasoningParallelFactory.start_session()`，恢复持久化执行只能通过 `resume_session()`。两个入口都校验运行标识、契约哈希、模式、拓扑、计划复现和事件历史。

### 1. Launch the branch wave / 启动分支波次

Call `launch_wave()`. It submits every named branch reservation as one atomic batch before the first branch `step_started` event. The ledger and all reservation events commit together or roll back together; runtime contention can never leave a partial branch wave. Exact retries return the original reservation identities and do not recreate a member already consumed by a completed branch. / 调用 `launch_wave()`。它会在首个分支 `step_started` 事件前，把全部具名分支预留作为一个原子批次提交。账本与全部预留事件共同提交或共同回滚；运行时竞争不会留下部分分支波次。完全相同的重试返回原预留标识，也不会重建已被完成分支消费的成员。

Each branch receives only the sealed shared input, its own hypothesis and namespace, the common comparison-rule binding, its budget, and `branch_private_until_closed`. It never receives another branch's intermediate output. / 每个分支只接收已封存共享输入、自身假设与命名空间、统一比较规则绑定、自身预算和 `branch_private_until_closed`；绝不接收其他分支的中间输出。

### 2. Close every branch / 关闭每个分支

The in-process controller calls `close_branch()` exactly once per `candidate_path_id`. An external worker must instead call scheduler `close_leased_branch()` so only the current unexpired holder can publish. Allowed terminals are `completed`, `pruned`, `failed`, `timed_out`, and `cancelled`. / 进程内控制器对每个 `candidate_path_id` 只调用一次 `close_branch()`。外部工作者必须改用调度器的 `close_leased_branch()`，确保只有当前未过期持有者可以发布。允许终态为 `completed`、`pruned`、`failed`、`timed_out` 和 `cancelled`。

A completed branch must provide a candidate, all required evidence types, every common criterion exactly once, and every common veto exactly once. A non-completed branch must provide no candidate and one explicit elimination reason. Actual use must fit the branch allocation. / 完成分支必须提供候选、全部必需证据类型、逐项且仅一次报告所有统一判据与统一否决规则。未完成分支不得提供候选，且必须提供一个显式淘汰原因。实际用量必须落在分支分配内。

The runtime emits path-bound `step_started`, `step_closed`, and `candidate_created` events. Source evidence is immutable and precedes candidate selection; the branch candidate does not replace the run-level final candidate. / 运行时发出绑定路径的 `step_started`、`step_closed` 与 `candidate_created` 事件。来源证据不可变且先于候选选择；分支候选不会替换运行级最终候选。

### 3. Join and synthesize / 汇合与综合

Call `synthesize()` only after every planned branch has an explicit terminal. `all_completed` requires all candidates; `quorum` permits failed or pruned branches but still requires their terminal records and the configured minimum completed count. / 只有全部计划分支具有显式终态后才能调用 `synthesize()`。`all_completed` 要求全部候选完成；`quorum` 允许失败或剪枝分支，但仍要求这些分支的终态记录并满足配置的最小完成数。

The synthesis owner must declare that every planned path was reviewed. Every non-selected path—including missing, failed, pruned, timed-out, tied, and identical-output paths—requires one elimination reason. / 综合责任方必须声明已审阅每条计划路径。每条未选路径——包括缺失、失败、剪枝、超时、并列及相同输出路径——都必须有一个淘汰原因。

## Leases And Deadlines / 租约与截止时间

Use `ParallelPathScheduler` when branches are dispatched to external workers. Call `acquire()` only after `launch_wave()`, then `renew()` as a heartbeat, `release()` when the holder gives up the path, or `close_leased_branch()` to atomically release and publish a public terminal result. Every `parallel_path_updated` event binds the immutable plan, path and step envelope, worker binding, lease identity, monotonic revision, path-local fencing token / 栅栏令牌, acquisition time, expiry, and scheduler deadline. Each reacquisition increments the token; renew, release, and result submission require the current token. A request from another, expired, or superseded worker fails closed. / 分支由外部工作者执行时使用 `ParallelPathScheduler`。只能在 `launch_wave()` 后调用 `acquire()`，随后用 `renew()` 作为心跳，在持有者放弃路径时调用 `release()`，或调用 `close_leased_branch()` 原子释放并发布公开终态结果。每条 `parallel_path_updated` 事件都绑定不可变计划、路径与步骤信封、工作者绑定、租约标识、单调修订、路径局部栅栏令牌、获取时间、过期时间和调度截止时间。每次重新获取都会递增令牌；续约、释放与结果提交必须携带当前令牌。其他、过期或已被取代的工作者请求默认阻断。

Call `sweep_due()` before reassignment and at the global deadline. A lease TTL expiry records `expired`, revokes worker ownership, preserves the logical branch and its existing wave reservation, and returns `reassign_expired_paths`; a new lease ID may then acquire that open path. It does not manufacture a `timed_out` branch result. A plan deadline records `deadline_reached` for every still-open path, closes those paths as `timed_out`, and applies the compiled `on_deadline` policy. `proceed_with_quorum` permits synthesis only when the configured minimum completed count remains satisfied; otherwise it fails closed. `escalate` and `fail` transition to their explicit terminal states. A deadline event permits an `all_completed` plan to use the declared quorum override, but never removes the synthesis requirement for at least two comparable completed candidates. / 重新分配前及全局截止时间到达时调用 `sweep_due()`。租约 TTL 到期会记录 `expired`、撤销工作者所有权、保留逻辑分支及其现有波次预算预留，并返回 `reassign_expired_paths`；随后可以用新租约标识获取该开放路径。它不会伪造 `timed_out` 分支结果。计划截止会为每条仍开放路径记录 `deadline_reached`，把这些路径关闭为 `timed_out`，再执行已编译的 `on_deadline` 策略。只有仍满足配置的最小完成数时，`proceed_with_quorum` 才允许综合，否则默认失败关闭；`escalate` 与 `fail` 进入各自显式终态。截止事件可允许 `all_completed` 计划采用已声明的法定完成数覆盖，但绝不取消综合至少需要两个可比较完成候选的要求。

Lease decisions must run inside the event-store transaction. With `SqliteEventStore`, competing processes or engine instances serialize through `BEGIN IMMEDIATE`; the losing writer observes the committed lease and cannot acquire the same path. SQLite is only the single-node reference, not distributed consensus. / 租约决定必须位于事件库事务内。使用 `SqliteEventStore` 时，竞争进程或引擎实例通过 `BEGIN IMMEDIATE` 串行化；落败写者会看到已提交租约，不能获取同一路径。SQLite 只是单节点参考，不是分布式共识。

## Durable Dispatch And Network Storage / 持久分派与网络存储

Construct `ParallelDispatchCoordinator` with the scheduler and a matching outbox. `acquire_and_enqueue()` records the lease event and immutable dispatch in the same database transaction; `close_leased_branch()` records outbox completion, verifies the fencing token, releases ownership, and closes the branch in one commit. A crash before commit leaves neither half; an exact retry returns the committed acquisition or completion, while changed content under the same identity conflicts. / 使用调度器与匹配发件箱构造 `ParallelDispatchCoordinator`。`acquire_and_enqueue()` 在同一数据库事务中记录租约事件与不可变分派；`close_leased_branch()` 在一次提交中记录发件箱完成、校验栅栏令牌、释放所有权并关闭分支。提交前崩溃不会留下任一半成品；完全相同的重试返回已提交的获取或完成结果，而同一标识下内容变化会冲突。

`SqliteParallelDispatchOutbox` is the single-node reference. Consumers claim pending rows with an expiring delivery token; a dispatcher crash makes the row reclaimable, and an old token cannot acknowledge the replacement claim. This is at-least-once / 至少一次 delivery, not end-to-end exactly-once execution. A side-effecting consumer must persist a business idempotency key or inbox in the same transaction as its effect; the dispatch ID and fencing token are suitable inputs but do not replace that consumer-side commit. Dead-lettered work requires an owned review and replay policy. / `SqliteParallelDispatchOutbox` 是单节点参考。消费者使用可过期交付令牌领取待处理记录；分派器崩溃后记录可重新领取，旧令牌不能确认替代领取。这是至少一次交付，不是端到端严格一次执行。产生副作用的消费者必须把业务幂等键或 inbox 与其副作用放在同一事务中持久化；分派标识与栅栏令牌可作为输入，但不能替代消费者侧提交。死信工作需要有负责人维护的审查与重放策略。

For horizontal writers, `PostgresEventStore` takes a transaction-scoped per-run advisory lock, reloads the authoritative event stream, and relies on unique constraints for event sequence, event identity, run-scoped idempotency, and immutable result identity. `PostgresParallelDispatchOutbox` shares that transaction for enqueue and completion; competing consumers use `FOR UPDATE SKIP LOCKED`. The reference opens direct Psycopg 3 connections and does not own production pooling or credential policy. / 水平写者使用 `PostgresEventStore`：它取得按运行划分的事务级 advisory lock，重载权威事件流，并通过唯一约束保护事件序列、事件标识、运行域幂等及不可变结果标识。`PostgresParallelDispatchOutbox` 在入队与完成时共享该事务；竞争消费者使用 `FOR UPDATE SKIP LOCKED`。参考实现直接打开 Psycopg 3 连接，不负责生产连接池或凭据策略。

Run the network integration suite with an isolated database DSN: `HARNESS_POSTGRES_DSN=postgresql://... python -m pytest -q tests/test_reasoning_postgres_runtime.py`. The fixture creates and drops only a generated `harness_test_*` schema. Without the variable, real-server tests report `skipped`; static imports or SQLite tests are not substitutes. Production acceptance additionally requires TLS, least-privilege roles, connection pooling, migration rehearsal, backup/restore, retention, monitoring, capacity limits, and failover tests. / 使用隔离数据库 DSN 运行网络集成套件：`HARNESS_POSTGRES_DSN=postgresql://... python -m pytest -q tests/test_reasoning_postgres_runtime.py`。夹具只创建并删除生成的 `harness_test_*` Schema。未设置变量时，真实服务器测试报告为 `skipped`；静态导入或 SQLite 测试不能替代。生产验收还要求 TLS、最小权限角色、连接池、迁移演练、备份恢复、保留策略、监控、容量限制与故障转移测试。

## Recovery And Projection / 恢复与投影

Persist the sealed blueprint, contract, and plan beside a `JsonlEventStore` stream. The store writes an immutable terminal result to a self-hashed sibling `.results.json` sidecar. After process loss, construct a fresh engine over the reopened store and call `ReasoningParallelFactory.resume_session()`. The engine validates the entire ordered stream, restores the original attempt identity, state, active reservations, consumed budget, open and closed steps, evidence records, candidate bindings, validator outcomes, and any sealed terminal result, then rechecks plan history without emitting establishment events. Event termination and result persistence are a recoverable two-phase boundary: a crash before the sidecar commit leaves a terminal stream from which the result can be rebuilt; a committed result is immutable and exact-idempotent. / 将封存蓝图、契约和计划与 `JsonlEventStore` 事件流并置持久化。存储把不可变终态结果写入自哈希的同级 `.results.json` 伴随文件。进程丢失后，在重新打开的存储上构造新引擎并调用 `ReasoningParallelFactory.resume_session()`。引擎校验完整有序事件流，恢复原尝试标识、状态、活动预留、已消费预算、开放与闭合步骤、证据记录、候选绑定、验证结果及已有封存终态结果，再重新校验计划历史，且不重复发送建链事件。事件终止与结果持久化构成可恢复的两阶段边界：伴随文件提交前崩溃会留下可重建结果的终态事件流；已提交结果不可变且完全幂等。

Use [`SqliteEventStore`](../runtime/reasoning_event_sqlite_store.py) instead of JSONL for single-node multi-writer events and terminal results. Each outer transaction reloads and validates all authoritative event rows before appending; database constraints keep run sequence, event identity, run-scoped idempotency, one result per run, and result identity unique. A supplied causal parent that is no longer the stream head is rejected; reopen or resume the engine before retrying. Schema v2 migrates a v1 event database by adding `terminal_results` without rewriting events. `health_check()` reports schema version, WAL mode, integrity, event count, run count, and result count. / 单节点多写者事件及终态结果应使用 `SqliteEventStore`，而不是 JSONL。每个最外层事务在追加前重载并校验全部权威事件记录；数据库约束保证运行序列、事件标识、运行域幂等键、每运行一个结果及结果标识唯一。调用方提供的因果父事件若已不是流头则被拒绝，重试前必须重新打开或恢复引擎。Schema v2 通过增加 `terminal_results` 迁移 v1 事件库，不重写事件。`health_check()` 报告 Schema 版本、WAL 模式、完整性、事件数、运行数及结果数。

Events deliberately retain final candidate bindings rather than raw candidate content. Resupply `candidate_artifact` only when a resumed validator or result builder needs that public artifact; its hash must equal the recorded run-level candidate binding. Contract, plan, context, attempt, or candidate drift fails closed. / 事件有意保留最终候选绑定而不保留候选原文。只有恢复后的验证器或结果生成器需要该公开制品时才重供 `candidate_artifact`，且其哈希必须等于已记录的运行级候选绑定。契约、计划、上下文、尝试或候选发生漂移时默认阻断。

Call `project_parallel_run(plan, events)` from [`reasoning_parallel_projection.py`](../runtime/reasoning_parallel_projection.py) to produce a deterministic, hash-bound branch inventory. Structural drift raises `ParallelProjectionError`; missing starts, terminals, records, comparison, or synthesis remain explicit anomalies. The projection is the authoritative source for `candidate_completion_rate`, `branch_diversity`, and `branch_record_completeness` inputs—never rebuild those denominators from successful branches alone. / 调用事件投影器中的 `project_parallel_run(plan, events)` 生成确定且哈希绑定的分支清单。结构漂移抛出 `ParallelProjectionError`；缺少启动、终态、记录、比较或综合时保留为显式异常。该投影是 `candidate_completion_rate`、`branch_diversity` 与 `branch_record_completeness` 输入的权威来源；不得只基于成功分支重建分母。

## Synthesis Contract / 综合契约

For `selected`, the supplied winning candidate must hash to the exact branch candidate binding. The runtime records the complete branch manifest and minority findings, emits `candidate_compared`, and only then promotes the selected content as the run candidate. Final evidence revisions must explicitly bind that selected candidate and the final public claims. / 对 `selected`，提交的胜出候选必须哈希匹配确切分支候选绑定。运行时记录完整分支清单与少数派发现，发出 `candidate_compared`，然后才把选中内容晋升为运行候选。最终证据修订必须显式绑定选中候选及最终公开命题。

For `tie`, `incomparable`, or `more_evidence_required`, no winner may be attached. The versioned tie policy controls the next action: escalate a material tie, wait for more evidence, or return conditional alternatives without claiming truth. / 对 `tie`、`incomparable` 或 `more_evidence_required`，不得绑定胜出者。版本化并列策略控制下一动作：升级实质并列、等待更多证据，或返回条件化备选而不宣称真值。

Voting, model confidence, fluent prose, or branch count cannot override common vetoes, mandatory validators, evidence sufficiency, governance, or action authorization. / 投票、模型自信度、流畅表述或分支数量不能覆盖统一否决、必选验证器、证据充分性、治理或行动授权。

After a `selected` synthesis, call `finalize_selected_candidate()`. Supply public outcomes from contract-declared external validators plus the exact release claims, final decision, output, and field provenance. The method records validators in contract order, stops on a repairable outcome, seals an explicit failed/escalated/timed-out result for terminal validation outcomes, or calls the authoritative release gate and `build_result()` after all mandatory validators pass. A missing or stale validator returns `repair_release_gate` without claiming completion. Exact retries return the same validation records and immutable result; changed content under the same idempotency identity is rejected. / `selected` 综合后调用 `finalize_selected_candidate()`。传入契约声明的外部验证器公开结果，以及完全一致的放行声明、最终决定、输出和字段来源。该方法按契约顺序记录验证器；遇到可修复结果时停止；遇到终态验证结果时封存显式失败、升级或超时结果；全部必选验证器通过后调用权威放行门与 `build_result()`。验证器缺失或陈旧时返回 `repair_release_gate`，不宣称完成。完全相同的重试返回原验证记录和不可变结果；同一幂等身份下内容变化会被拒绝。

## Observability / 可观测性

The plan always resolves `PROBE_0008` Parallel Path. Its minimum capture is `candidate_path_id`, branch lifecycle, candidate binding, comparison-rule binding, selection, and the complete planned-path inventory. Identity, contract, budget, step closure, evidence, drift, validation, stop/escalation, privacy, and self-health probes remain mandatory. / 计划始终解析 `PROBE_0008` 并行路径探针。其最小采集为 `candidate_path_id`、分支生命周期、候选绑定、比较规则绑定、选择结果和完整计划路径清单。身份、契约、预算、步骤闭环、证据、漂移、验证、停止/升级、隐私和自健康探针仍为必需。

Treat identical candidate bindings from different paths as false diversity evidence, not a schema error. Treat a planned path without a terminal as missing, not failed. Never publish implemented candidate-completion, branch-diversity, branch-record-completeness, or convergence metrics without the required complete inventory and finalized time window. Synthesis-fidelity and minority-preservation metrics remain planned and unreported. / 不同路径产生相同候选绑定时，将其作为伪多样证据，而不是 Schema 错误。计划路径没有终态时标记为缺失，不标记为失败。缺少所需完整清单和已封窗时间窗口时，不得发布已实现的候选完成率、分支多样性、分支记录完整率或收敛指标。综合保真度和少数结论保留率仍在规划中，不得发布。

## Acceptance / 验收

- Blueprint and plan pass Draft 2020-12 Schema plus semantic validation. / 蓝图与计划通过 Draft 2020-12 Schema 和语义校验。
- Plan reproduces byte-for-byte from its blueprint and sealed contract. / 计划可由蓝图与封存契约逐字节复现。
- All branch budgets are reserved before any branch starts. / 所有分支预算在任一分支启动前完成预留。
- A failed batch reservation leaves no branch reservation or reservation event. / 批次预留失败时不留下任何分支预留或预留事件。
- Branch intermediate context is isolated; shared input is immutable and contract-bound. / 分支中间上下文隔离；共享输入不可变且绑定契约。
- Every path has one explicit terminal; completed paths have evidence and common assessments. / 每条路径有一个显式终态；完成路径具有证据与统一评估。
- Synthesis reviews the full path inventory and records one reason for every non-selected path. / 综合审阅完整路径清单，并为每条未选路径记录一个原因。
- Winner content, candidate event, final evidence revisions, validators, and final claims share exact bindings. / 胜出内容、候选事件、最终证据修订、验证器与最终命题具有精确绑定。
- Material ties escalate or wait according to the versioned policy; they never silently become truth. / 实质并列按版本化策略升级或等待，绝不静默变成真值。
- Events are replayable, path-correlated, budget-closed, and free of private chain-of-thought. / 事件可回放、可按路径关联、预算闭合，且不含私密思维链。
- Lease acquisition is single-holder, revisions are contiguous, stale workers cannot renew or submit, and TTL expiry preserves the open branch for a new lease. / 租约获取为单持有者，修订连续，陈旧工作者不能续约或提交，TTL 到期会保留开放分支供新租约接管。
- Every path reacquisition increases its fencing token, and a superseded token cannot acknowledge delivery or publish a branch result. / 每次路径重新获取都递增栅栏令牌，已被取代的令牌不能确认交付或发布分支结果。
- Lease acquisition plus outbox enqueue, and result acceptance plus outbox completion, each commit or roll back atomically. / 租约获取与发件箱入队、结果接受与发件箱完成分别共同提交或共同回滚。
- Expired delivery claims are reclaimable with a new delivery token; side-effecting consumers document and test their own durable idempotency boundary. / 过期交付领取可使用新交付令牌重新领取；产生副作用的消费者记录并测试其自有持久幂等边界。
- Deadline sweeps close every open path and apply the compiled quorum, escalation, or failure policy exactly. / 截止扫描关闭每条开放路径，并精确执行已编译的法定完成数、升级或失败策略。
- A reopened durable store restores the same state, budget, open-step inventory, and idempotency history without new lifecycle events. / 重新打开持久化存储后恢复相同状态、预算、开放步骤清单与幂等历史，且不新增生命周期事件。
- A reopened durable store restores the exact sealed terminal result; tampering, a duplicate with changed content, or a result/event terminal-state mismatch fails closed. / 重新打开持久化存储后恢复完全相同的封存终态结果；篡改、同运行不同内容的重复结果或结果与事件终态不匹配时默认阻断。
- SQLite v1 migrates to v2 without rewriting events, and JSONL result commit failure leaves neither an in-memory result nor a partial sidecar. / SQLite v1 不重写事件即可迁移到 v2；JSONL 结果提交失败不会留下内存结果或部分伴随文件。
- Multi-writer SQLite commits retain contiguous run sequences, cross-instance idempotency, rollback atomicity, and stale-parent rejection. / 多写者 SQLite 提交保持连续运行序列、跨实例幂等、回滚原子性和陈旧父事件拒绝。
- With `HARNESS_POSTGRES_DSN`, real PostgreSQL tests cover cross-instance event serialization, immutable terminal results, transactional outbox rollback, `SKIP LOCKED` claims, and stale-token rejection; without it, those cases are explicitly skipped. / 配置 `HARNESS_POSTGRES_DSN` 后，真实 PostgreSQL 测试覆盖跨实例事件串行化、不可变终态结果、事务发件箱回滚、`SKIP LOCKED` 领取与陈旧令牌拒绝；未配置时这些用例被明确跳过。
- The deterministic projection owns complete metric inventories and exposes missing paths as anomalies, not failures or zeros. / 确定性投影负责完整指标清单，并把缺失路径暴露为异常，而不是失败或零值。
- An exact retry of a completed branch close or synthesis returns the prior result without adding events; changed content under the same identity fails as a conflict. / 对已完成分支关闭或综合的完全相同重试返回既有结果且不新增事件；同一标识下内容变化时以冲突失败。
- Selected synthesis closes through mandatory validation, the evidence gate, and one schema-valid immutable terminal result. / 选中综合必须经过必选验证、证据门并闭合为一个符合 Schema 的不可变终态结果。
