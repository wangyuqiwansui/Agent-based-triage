# Extension Candidate / 扩展候选

Cell / 交织点: governance-loop / 治理 x 循环
Capability / 能力: Governance / 治理
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Use this section to define the design pattern, its source grounding, and its workflow adjustment template. / 本节定义设计模式、来源依据和工作流调整模板。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Governance / 治理 x Loop / 循环 (Loop / 循环).
- 论文依据 / Article Basis: 空白单元 / Empty cell; arXiv:2605.13850 leaves this intersection unnamed. / 空白单元 / Empty cell；arXiv:2605.13850 未命名该交织点。
- 问题 / Problem: The article leaves this intersection unnamed; use it only if workflow evidence shows that Governance / 治理 needs Loop / 循环. / 论文未命名该交织点；仅当工作流证据表明 Governance / 治理 需要 Loop / 循环 时使用。
- 架构方案 / Architectural Solution: Keep this as an extension candidate and define a concrete pattern only after repeated workflow evidence appears. / 将其保留为扩展候选，仅在反复出现工作流证据后再定义具体模式。
- 工程权衡 / Engineering Trade-offs: This avoids inventing taxonomy, but leaves a deliberate gap until practice justifies the pattern. / 这避免凭空发明分类，但在实践证明前会保留有意空白。
- 工作流诊断用途 / Workflow Diagnosis Use: Extension candidate / 扩展候选.

### Pattern Template / 模式模板

- 状态 / Status: 扩展候选 / Extension candidate.
- 模式清单 / Patterns: 待发现 / To be discovered.
- 诊断用途 / Diagnostic Use: Extension candidate / 扩展候选.
- 适用工作流节点 / Applicable Workflow Nodes: 运行监控、治理审查 / Monitoring, governance review.
- 当前症状 / Current Symptoms: Timeouts cause duplicate writes, task renaming resets limits, or retries continue without a terminal owner. / 超时导致重复写入、任务改名重置限额，或重试没有最终责任人。
- 适配信号 / Fit Signals: 治理根据结果持续复查、修正和再确认 / Governance repeatedly reviews, corrects, and reconfirms based on outcomes.
- 调整方向 / Adjustment Direction: Keep stable business identity and cumulative limits across attempts, reconciling unknown outcomes before any controlled retry. / 跨尝试保留稳定业务身份与累计约束，先对账未知结果再受控重试。
- 修改方式 / How To Modify: Add durable checkpoints, result queries, bounded retries, current authorization checks, and explicit unresolved or human-handoff exits. / 增加持久检查点、结果查询、有界重试、当前授权检查及明确的未解决或人工移交出口。
- 输入 / Inputs: Original proposal and business identity, attempt history, reservations, current policy and credentials, query and idempotency guarantees. / 原提案与业务身份、尝试历史、占用、当前策略及凭证、查询与幂等保障。
- 输出 / Outputs: Reconciliation result, item-level settlement, controlled next action, retry budget remaining, unresolved owner and deadline. / 对账结果、分项结算、受控下一动作、剩余重试预算、未决责任人与期限。
- 风险与治理 / Risks & Governance: Preserve unknown occupancy; do not infer failure from silence, reset limits on retry, or label local restoration as external rollback. / 保留未知占用；不把静默推断为失败，不因重试重置限额，不将本地恢复标为外部回滚。

### Module Attachment / 模块工程挂载

Identity / 身份: `CELL_GOVERNANCE_LOOP; pattern_ref: null`. Existing names and maturity stay unchanged. / 保持现有名称与成熟度不变。

Attach bounded reconciliation and revalidation to feedback-driven workflows without promoting this unnamed matrix cell into a new official pattern. / 为反馈驱动流程挂载有界对账与再核验，不将该未命名单元升格为新的官方模式。

Read the maintained [execution flow / 执行流程](../../governance-execution-flow.md#execution-steps) (执09–16、探09–12) and [shared contract / 共享契约](../../governance-contract.md). These are specification-only engineering extensions from the supplied lesson-36 documents; this card does not provide a dedicated production runtime or make an existing runtime implement `GOV_BOUNDARY_OBS`. / 阅读维护版执行流程与共享契约。这些内容是用户第 36 讲资料的规范级工程扩展；本卡不提供专用生产运行时，也不表示既有运行时已实现 `GOV_BOUNDARY_OBS`。

| Attachment point / 落点 | Required behavior and evidence / 必要行为与证据 |
| --- | --- |
| Retry identity / 重试身份 | Keep one business_operation_id and idempotency_key for the same business intent; create new attempt IDs while preserving cumulative consumption and any unknown reservations. / 同一业务意图保留 business_operation_id 与 idempotency_key；新建尝试 ID，同时保留累计消耗及未知占用。 |
| Unknown outcome / 结果未知 | Query the original request first. Timeouts and temporarily absent records do not prove failure; retries require current authority and the adapter's proven idempotency guarantee. / 先查询原请求；超时和暂时查无记录不证明失败，重试须有当前权限与适配器经核验的幂等保障。 |
| Exit and recovery / 退出与恢复 | Set retry/query budgets, deadlines, owners, and checkpoints. Reconcile partial batches per item; expired idempotency guarantees or unresolved outcomes go to the configured owner. / 设置重试与查询预算、截止时间、责任人及检查点；部分批次分项对账，幂等保障过期或仍未决时移交配置的责任人。 |

Boundary / 边界: A new task ID does not renew budget or authorization. Observation patches cannot replay business writes. Stop prevents new dispatches but does not recall in-flight effects; compensation needs its own controlled action and result verification. / 更换任务 ID 不重置预算或授权；观测补丁不能重放业务写入。停止只禁止新派发，不撤回在途副作用；补偿需要独立受控动作及结果核验。

Acceptance references / 验收引用: 执验10、12–16、20–23、探验09–11、18、26、28; use the [execution acceptance matrix / 执行验收矩阵](../../governance-execution-flow.md#acceptance) and [probe acceptance matrix / 探针验收矩阵](../../governance-observability-probes.md#acceptance). These are expected checks, not claims that production tests passed. / 这些是待验证的预期，不代表生产测试已通过。

Metric references / 指标引用: 指09–12、17、26–28、33、36; definitions, denominators, and unavailable states live in the [metric catalog / 指标目录](../../governance-observability-probes.md#metric-catalog). Permission and verified business success are separate results. / 口径、分母及不可用状态由指标目录统一定义；合规许可与已核实业务成功分开记录。

Observability Metrics File / 可观测性指标文件: [governance-loop-observability.md](governance-loop-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
