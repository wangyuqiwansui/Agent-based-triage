# Parallel Exploration / 并行探索

Cell / 交织点: reasoning-parallel / 推理 x 并行
Capability / 能力: Reasoning / 推理
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

Runtime Protocols / 运行协议: [Reasoning Execution Flow / 推理执行流程](../../reasoning-execution-flow.md); [Reasoning Parallel Factory / 推理并行工厂](../../reasoning-parallel-factory.md); [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md).

## Design Pattern / 设计模式

Parallel Exploration runs several independent reasoning branches on the same question at once — rival hypotheses, designs, or root causes — then compares them in an explicit synthesis step that must see every branch's evidence. / 并行探索让多条独立推理分支同时处理同一问题——竞争的假设、方案或根因——再由一个显式综合步骤比较它们，且综合步骤必须看到每条分支的证据。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reasoning / 推理 x Parallel / 并行 (Parallel / 并行).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; 矩阵列名模式 / Matrix-listed pattern; source table maps Reasoning / 推理 x Parallel / 并行 in arXiv:2605.13850. The article describes tree- and graph-style search exploring multiple reasoning branches simultaneously and names it the most expensive reasoning topology. / 代表性定义 / Representative definition；矩阵列名模式 / Matrix-listed pattern；来源表将 Reasoning / 推理 x Parallel / 并行 映射到该单元。论文描述树/图式搜索同时探索多条推理分支，并称其为最贵的推理拓扑。
- 问题 / Problem: A single reasoning path commits early to one framing; when the problem has several plausible framings, the committed path can be confidently wrong. / 单一推理路径过早承诺一种问题表述；当问题存在多种貌似合理的表述时，被承诺的路径可能自信地一路错下去。
- 架构方案 / Architectural Solution: Spawn independent branches in isolated contexts, give each a budget and an early-pruning rule, then merge through an explicit synthesis that compares branch conclusions on evidence rather than on confident tone. / 在隔离上下文中生成独立分支，为每条分支设预算与早期剪枝规则，再通过显式综合步骤基于证据而非语气自信度比较分支结论。
- 工程权衡 / Engineering Trade-offs: Widest coverage of alternatives but the most expensive reasoning topology — n branches cost roughly n× tokens; branches must be genuinely independent or the spend buys no diversity, and a weak synthesis step wastes all upstream branch diversity (the same logic as aggregation bottleneck `FAIL_0013`). / 覆盖替代方案最广，但也是最贵的推理拓扑——n 条分支约花 n 倍 token；分支必须真正独立，否则白付成本；综合步骤薄弱会浪费全部上游分支多样性（与聚合瓶颈 `FAIL_0013` 同逻辑）。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when independent hypotheses or solution paths should be explored together. / 当多个独立假设或方案路径应同时探索时使用。

### Branch And Synthesis Rules / 分支与综合规则

- Branch independence / 分支独立性: branches share inputs only and must not see each other's intermediate reasoning. / 分支只共享输入，不得看到彼此的中间推理。
- Branch budget and pruning / 分支预算与剪枝: give each branch a token or step budget; prune only when hard constraints fail, required evidence is unavailable, a common criterion is not met, or the branch cannot be validated within the remaining budget. Model self-confidence alone is not a pruning gate. / 每条分支设置 token 或步骤预算；仅当违反硬约束、必需证据不可得、不满足统一标准，或剩余预算内无法验证时剪枝。模型自信度不能单独作为剪枝闸门。
- Synthesis owner / 综合责任方: a single owner sees every branch's conclusion plus its evidence — not summaries of summaries — and decides on evidence. / 单一责任方看到每条分支的结论及其证据——不是摘要的摘要——并基于证据作出决定。
- Minority preservation / 少数派保留: losing and refuted branches are preserved with sources and elimination reasons, never silently dropped. / 落选与被证伪分支连同来源和排除原因保留，绝不静默丢弃。
- Sizing / 规模: 2-4 branches for design or root-cause comparison; beyond that, aggregate cost usually exceeds marginal coverage gain — re-derive the threshold locally per Law 5. / 方案或根因比较用 2-4 条分支；再多通常成本超过边际覆盖收益——按定律 5 本地重推阈值。

### Shared Execution Contract / 共享执行契约

Use `PATTERN_0051` to assign `candidate_path_id`, a material-difference statement, per-path evidence, validation state, elimination reason, and resource budget. Apply one comparison and veto contract to all candidates. The selected path still requires its mandatory final validator. / 使用 `PATTERN_0051` 为每条候选分配 `candidate_path_id`、实质差异说明、逐路径证据、验证状态、淘汰原因和资源预算。所有候选使用同一比较与否决契约；选中路径仍必须通过必选最终验证器。

Preserve conflicting and minority evidence. A synthesis may return conditional alternatives or escalate a material tie; it must not convert voting or confident tone into truth. / 保留冲突与少数派证据。综合可以返回条件化备选或升级重大并列，但不得把投票或自信语气转化为事实。

### Executable Engineering Contract / 可执行工程契约

Compile the author-owned blueprint and sealed parallel reasoning contract through `runtime/reasoning_parallel_factory.py`; treat [`reasoning-parallel-blueprint.schema.json`](../../../schemas/reasoning-parallel-blueprint.schema.json) and [`reasoning-parallel-plan.schema.json`](../../../schemas/reasoning-parallel-plan.schema.json) as normative. Open new execution only through `ReasoningParallelFactory.start_session()` and restore an event-backed run only through `resume_session()`, so plan identity, input isolation, atomic wave budgets, probe bindings, join policy, and comparison criteria remain reproducible. Coordinate external workers through [`reasoning_parallel_scheduler.py`](../../../runtime/reasoning_parallel_scheduler.py) plus the transactional [`reasoning_parallel_outbox.py`](../../../runtime/reasoning_parallel_outbox.py); every reacquisition advances a fencing token and stale results fail closed. Use [`reasoning_event_sqlite_store.py`](../../../runtime/reasoning_event_sqlite_store.py) for single-node multi-writer serialization, or the Psycopg 3 [`reasoning_event_postgres_store.py`](../../../runtime/reasoning_event_postgres_store.py) and [`reasoning_parallel_postgres_outbox.py`](../../../runtime/reasoning_parallel_postgres_outbox.py) references for horizontal writers. Project metrics only through [`reasoning_parallel_projection.py`](../../../runtime/reasoning_parallel_projection.py). / 通过 `runtime/reasoning_parallel_factory.py` 编译负责人维护的蓝图与已封存并行推理契约；以 [`reasoning-parallel-blueprint.schema.json`](../../../schemas/reasoning-parallel-blueprint.schema.json) 和 [`reasoning-parallel-plan.schema.json`](../../../schemas/reasoning-parallel-plan.schema.json) 为规范。新执行只通过 `ReasoningParallelFactory.start_session()` 打开，事件支持的运行只通过 `resume_session()` 恢复，使计划标识、输入隔离、原子波次预算、探针绑定、汇合策略和比较判据可复现。外部工作者通过 [`reasoning_parallel_scheduler.py`](../../../runtime/reasoning_parallel_scheduler.py) 与事务型 [`reasoning_parallel_outbox.py`](../../../runtime/reasoning_parallel_outbox.py) 协调；每次重新获取都推进栅栏令牌，陈旧结果默认阻断。单节点多写者串行化使用 [`reasoning_event_sqlite_store.py`](../../../runtime/reasoning_event_sqlite_store.py)；水平写者使用基于 Psycopg 3 的 [`reasoning_event_postgres_store.py`](../../../runtime/reasoning_event_postgres_store.py) 与 [`reasoning_parallel_postgres_outbox.py`](../../../runtime/reasoning_parallel_postgres_outbox.py) 参考实现。指标只能通过 [`reasoning_parallel_projection.py`](../../../runtime/reasoning_parallel_projection.py) 投影。

Use this lifecycle / 使用以下生命周期:

```text
route parallel / 路由到并行
  -> compile candidate space + common comparison contract / 编译候选空间与统一比较契约
  -> atomically reserve the complete branch wave / 原子预留完整分支波次
  -> atomically acquire fenced lease + enqueue immutable dispatch / 原子获取带栅栏租约并入队不可变分派
  -> claim with expiring delivery token + heartbeat lease / 使用可过期交付令牌领取并心跳续约租约
  -> run isolated branches / 运行隔离分支
  -> expire ownership -> reacquire open paths, or close paths at the global deadline / 所有权过期 -> 重新领取开放路径，或在全局截止时关闭路径
  -> close every branch with completed | pruned | failed | timed_out | cancelled
  -> enforce all-completed or quorum join / 执行全部完成或法定数汇合
  -> synthesize over the complete branch manifest / 基于完整分支清单综合
  -> project branch inventory + metric inputs / 投影分支清单与指标输入
  -> selected: bind final evidence -> validate -> release gate -> sealed result / 选中：绑定最终证据 -> 验证 -> 放行门 -> 封存结果
  -> tie or incomparable: escalate, wait, or return conditional alternatives / 并列或不可比：升级、等待或返回条件化备选
```

The candidate manifest is the source of truth. A planned branch without a terminal is `missing`, not failed; a failed or pruned branch remains in the manifest with its reason. `quorum` relaxes the number of completed candidates but never permits silent branch disappearance. / 候选清单是事实源。计划分支没有终态时属于 `missing`，不等于失败；失败或剪枝分支仍连同原因保留在清单中。`quorum` 只放宽完成候选数量，绝不允许分支静默消失。

Apply the same versioned criteria and vetoes to every completed candidate. Record criterion outcomes separately from candidate prose. The synthesis owner must explicitly attest access to every planned path, preserve minority findings, and give exactly one elimination reason for every non-selected path. / 对每个完成候选应用相同版本的判据与否决规则；判据结果与候选表述分开记录。综合责任方必须显式确认已访问每条计划路径，保留少数派发现，并为每条未选路径给出且仅给出一个淘汰原因。

Keep reasoning and action authorization separate. The reference factory accepts public branch results and evidence but does not execute tools or side effects inside branches. If a branch requires environment interaction to produce evidence, route that work through an authorized action/iterative lifecycle and return its immutable evidence record; do not treat `execution_mode: parallel` as action permission. / 分离推理与行动授权。参考工厂接收公开分支结果与证据，但不在分支内执行工具或副作用。分支需要环境交互补证时，应通过有授权的行动/迭代生命周期执行并返回不可变证据记录；不得把 `execution_mode: parallel` 当作行动权限。

### Join And Failure Rules / 汇合与失败规则

| Condition / 条件 | Required control / 必需控制 |
| --- | --- |
| One or more planned branches still have no terminal. / 仍有计划分支没有终态。 | Block synthesis and keep the paths missing. / 阻断综合并保留路径缺失状态。 |
| Completed candidates are below quorum. / 完成候选少于法定数。 | Apply the declared deadline policy: wait, fail, or escalate. / 执行声明的截止策略：等待、失败或升级。 |
| Candidate outputs are identical. / 候选输出相同。 | Record false diversity; regenerate distinct framings or fall back to chain. / 记录伪多样；重新生成不同表述或降为链式。 |
| Required criterion or veto result is absent. / 缺少必需判据或否决结果。 | Reject that branch closure; never infer a pass. / 拒绝该分支关闭；不得推断通过。 |
| Material tie remains after common criteria. / 统一判据后仍实质并列。 | Execute the versioned tie policy; never choose by vote or tone. / 执行版本化并列策略；不得按投票或语气选择。 |
| Winning candidate content differs from its branch binding. / 胜出候选内容与分支绑定不同。 | Reject as plan drift. / 按计划漂移拒绝。 |
| A lease expires or a stale worker heartbeats/submits. / 租约过期或陈旧工作者发送心跳/提交。 | Record ownership expiry, keep the logical path and reservation open for a new lease, and reject the stale holder; close only under the global deadline policy. / 记录所有权过期，保留逻辑路径及预算预留供新租约接管，并拒绝陈旧持有者；只有全局截止策略才关闭路径。 |
| A dispatcher crashes after claiming work. / 分派器领取工作后崩溃。 | Let the delivery claim expire, reclaim with a new token, and reject the old acknowledgement; keep consumer side effects idempotent because delivery is at least once. / 让交付领取过期，使用新令牌重新领取并拒绝旧确认；交付为至少一次，因此消费者副作用必须幂等。 |
| A worker result carries an older fencing token. / 工作者结果携带旧栅栏令牌。 | Reject it even if the lease ID or payload otherwise looks valid; never let a superseded worker close the branch. / 即使租约标识或负载看似有效也拒绝；绝不允许已被取代的工作者关闭分支。 |
| Mandatory final validation or evidence coverage is incomplete. / 必选最终验证或证据覆盖不完整。 | Keep the run non-completed and return the explicit repair gate; never emit a success result. / 保持运行未完成并返回显式修复闸门；不得输出成功结果。 |

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Parallel Exploration / 并行探索.
- 诊断用途 / Diagnostic Use: Use when independent hypotheses or solution paths should be explored together. / 当多个独立假设或方案路径应同时探索时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 方案设计、事故修复 / Design, incident repair.
- 当前症状 / Current Symptoms: The first proposed design gets implemented without rivals ever being drafted; incident reviews reveal an alternative root cause nobody explored; parallel drafts exist but share context and converge to the same answer. / 第一个提出的方案未经对比就被实现；事故复盘揭示存在无人探索过的替代根因；虽有并行草案但共享上下文并收敛到同一答案。
- 适配信号 / Fit Signals: 多个假设、方案或根因可以独立推理后比较 / Multiple hypotheses, designs, or causes can be reasoned about independently and compared.
- 调整方向 / Adjustment Direction: Fork genuinely independent branches with budgets, and treat the synthesis comparison as first-class work. / 派生真正独立、带预算的分支，并把综合比较当作一等工作。
- 修改方式 / How To Modify: 1) Frame 2-4 rival framings or hypotheses worth exploring. 2) Spawn isolated branches with per-branch budget and pruning rule. 3) Run branches to conclusion or pruning. 4) Synthesize: a single owner compares all branch evidence and writes the decision, preserving minority findings. 5) Record eliminated branches with reasons. / 1）确定 2-4 个值得探索的竞争表述或假设；2）生成带预算与剪枝规则的隔离分支；3）分支运行至结论或被剪枝；4）综合：单一责任方比较全部分支证据并写出决定、保留少数派发现；5）带原因记录被排除分支。
- 输入 / Inputs: Question with rival framings, branch count and per-branch budget, isolation mechanism (separate contexts or subagents), synthesis criteria. / 带竞争表述的问题、分支数与每分支预算、隔离机制（独立上下文或子 Agent）、综合判据。
- 输出 / Outputs: Per-branch conclusions with evidence, synthesis decision with comparison rationale, eliminated-branch register, minority findings with sources. / 逐分支带证据结论、带比较理由的综合决定、被排除分支台账、带来源的少数派发现。
- 风险与治理 / Risks & Governance: Weak synthesis silently dropping minority findings (`FAIL_0013` logic) — require the synthesis owner to see raw branch evidence; context leakage between branches destroys independence and pays n× cost for zero diversity — enforce isolation; per-branch conclusions and the synthesis decision are recorded per `GOV_0002`. External dispatch is at least once, so use transactional outbox records, fencing tokens, dead-letter ownership, and consumer-side durable idempotency; never present transport retries as end-to-end exactly once. / 综合薄弱静默丢弃少数派发现（`FAIL_0013` 同逻辑）——要求综合责任方看到分支原始证据；分支间上下文泄漏破坏独立性、n 倍成本零多样性——强制隔离；逐分支结论与综合决定按 `GOV_0002` 入账。外部分派为至少一次，因此使用事务型发件箱记录、栅栏令牌、死信责任归属与消费者侧持久幂等；不得把传输重试表述为端到端严格一次。

Observability Metrics File / 可观测性指标文件: [reasoning-parallel-observability.md](reasoning-parallel-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
