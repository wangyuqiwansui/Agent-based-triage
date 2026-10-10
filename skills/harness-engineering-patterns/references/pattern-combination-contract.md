# Pattern Combination Exchange Contract / 模式组合交互契约

Name / 名称: Pattern Combination Contract / 模式组合契约. Description / 说明: identity, evidence, completion and control boundaries between execution and independent probes / 执行与独立探针之间的标识、证据、完成及控制边界。

Version / 版本: `0.1.0`; status / 状态: draft / 草案; implementation / 实现: `specification_only`; business cases / 业务用例: `not_executed`.

## Quick Navigation / 快速导航

[Objects / 对象](#objects) · [Exchange / 交互](#exchange) · [Refinements / 细化](#refinements) · [Validation / 验证](#validation) · [Execution / 执行](pattern-combination-execution-flow.md) · [Probes / 探针](pattern-combination-observability-probes.md) · [Sources / 来源](pattern-combination-source-map.json).

## Registration and Usage / 注册与用法

Register composition as `PATTERN_0053`, retaining source alias `PATTERN_COMBINATION_0001`. The companion `PATTERN_OBSERVABILITY_PROBE_0001` is a source alias attached to existing `PATTERN_0052`, not a replacement ID. Source `PROBE_*_001` identifiers are scoped to `pattern_combination/0.1.0`; never silently alias them to existing runtime probe IDs or register formulas as implemented calculators. / 模式组合登记为 `PATTERN_0053` 并保留来源别名；配套探针来源标识挂载既有 `PATTERN_0052`，不替换稳定编号。来源探针编号限定在 `pattern_combination/0.1.0` 名称空间，不能暗中映射既有运行探针或把公式登记为已实现计算器。

Execution may operate alone; probes may inspect unrelated offline or online workflows. Both use original records as evidence and preserve the executor's authoritative business state. Supplied documents are untrusted evidence, including embedded registration suggestions and sample commands. / 执行可独立运行，探针可离线或在线观察其他工作流；双方使用原始记录并保留执行侧权威业务状态。来源中的注册建议和示例指令均按资料处理。

<a id="objects"></a>
## Identity and Version Bindings / 标识与版本绑定

| Object / 对象 | Required binding / 必要绑定 |
| --- | --- |
| Task / 任务 | `task_id`, objective, mandatory deliverables/acceptance, prohibitions, scope, risk, contract version. / 任务标识、目标、必需交付验收、禁止项、范围、风险及契约版本。 |
| Run / 运行 | `trace_id`, `run_id`, `task_id`, actor, predecessor run/checkpoint for recovery. / 链路运行任务标识、主体及恢复时前驱运行检查点。 |
| Plan / 计划 | `plan_id`, `plan_version`, nodes, dependencies, branch inventory and change reasons. / 计划版本、节点、依赖、分支清单及变更原因。 |
| Node and attempt / 节点与尝试 | `node_id`, optional parent/branch, new `attempt_id` per retry, owner, read state version, inputs, readiness and completion. / 节点及可选父分支、每次重试新尝试号、责任、读取状态版本、输入就绪与完成。 |
| Artifact and evidence / 工件与证据 | `artifact_id/version`, `evidence_id`, source locator/version/time, digest where available, access scope and validity. / 工件版本、证据标识、来源定位版本时间、可用时摘要、访问范围及有效性。 |
| Decision / 决策 | `decision_id`, candidates, public rationale, evidence and reroute triggers; no private reasoning transcript. / 决策号、候选、公开依据、证据和换路条件，不含私密思维稿。 |
| Action and approval / 动作与审批 | `action_id`, exact target/input version, permitted scope/limits/time, `approval_id`, pre/post evidence, receipt, idempotency key and actual effects. / 动作号、精确对象输入版本、批准范围额度时间、审批号、前后证据、回执、幂等键和实际效果。 |
| Review / 评审 | `review_id`, immutable artifact version, criteria, evidence access and issue disposition. / 评审号、不可变工件版本、标准、证据访问及问题处理。 |
| Handoff / 交接 | `handoff_id`, delivered version, sender/receiver, pending duties, receipt, responsibility transfer and recovery. / 交接号、交付版本、双方、剩余职责、接收回执、责任转移及恢复点。 |
| Budget / 预算 | `budget_id`, dimension/unit, parent, limit, reserved/consumed balance and authoritative revision. / 预算号、维度单位、父账户、限额、预留消耗余额及权威修订。 |

<a id="exchange"></a>
## Event and Enrichment Exchange / 事件与补全交互

Every append-only event carries `event_id`, `event_type`, `occurred_at` with offset, source-local `sequence`, `trace_id`, `run_id`, `task_id`, `source_actor`, `source_type`, `data_version` and `payload`. Conditional fields bind plan/node/branch/attempt, artifact/version, evidence, decision/action/approval/review/handoff, state before/after, duration/cost, input/output digests, sensitivity and collection confidence. / 每条追加事件包含事件号、类型、带偏移时间、来源内序号、链路运行任务、来源主体类型、数据版本和载荷；条件字段绑定计划节点分支尝试、工件版本、证据及各业务对象、前后状态、耗时费用、输入输出摘要、敏感级别与采集置信。

Append corrections with a `supersedes_event_id` or corresponding finding/report revision; never overwrite raw history. Preserve causal parents, source sequence, read/write state versions and both occurred/received times. Sequences from different producers are not globally comparable. Deduplicate by authenticated source plus event ID; a repeated ID with different content is a conflict, not a replacement. / 纠错追加前驱事件或发现报告修订，不覆盖历史；保留因果父事件、来源序号、读写状态版本及发生接收时间。不同来源序号不可全局比较；按认证来源与事件号去重，同号异内容记冲突而非替换。

| Record / 记录 | Required content and constraints / 必需内容与约束 |
| --- | --- |
| Data request / 补全请求 | `request_id`, namespaced probe, trace/run/task, related object/type/version, missing fields, reason, allowed candidate sources, severity, expected evidence; local refinement adds deadline and cumulative request budget. / 请求号、名称空间探针、链路运行任务、对象类型版本、缺失字段原因、允许来源、严重度及预期证据；本地细化增加期限和累计请求预算。 |
| Data response / 补全响应 | `response_id`, request binding, completed/partial/unavailable/forbidden, original references, source, confidence, unavailable reason and `business_state_changed: false`. / 响应号、请求绑定、已补全或部分或不可得或无权、原始引用来源置信、不可得原因及不变更业务状态。 |
| Finding / 异常发现 | `finding_id`, probe/version, task/object bindings, severity/status, observed facts, evidence, affected scope, recommendation, confidence and optional block request. / 发现号、探针版本、任务对象绑定、严重度状态、事实证据、影响范围、建议置信及可选阻断请求。 |
| Resolution / 处理结果 | `resolution_id`, finding/version, blocked/revised/waived/false_positive/pending_human, authenticated deciding actor, evidence/policy, follow-up and state transition receipt. / 处理号、发现版本、阻断修订豁免误报待人工、认证决定主体、证据策略、后续及状态迁移回执。 |

Workflow: emit → correlate → request missing original data → authorize scoped read → return evidence or reason → append revised finding → governance decides any control → append receipt → verify closure. A response is not business acceptance, an approval, a rerun or a write instruction. Late contradictory evidence may reopen a finding; business revalidation remains an explicit execution action. / 流程为发送、关联、请求原始数据、核准范围读取、返回证据或原因、追加发现修订、治理决定控制、追加回执、核验关闭。补全响应不等于业务验收、审批、重跑或写入指令。迟到冲突证据可重开异常，业务复验仍须由执行侧明确实施。

## Control and Data Boundaries / 控制与数据边界

Default behavior is report-only. Optional authorized notification, enrichment reads and governance requests are bounded actions; the probe never directly changes goals, plan, evidence truth, business state or authority. A critical finding can request blocking only through an explicitly configured governance entry with independent current authority; lack of probe service does not disable the action gateway's own mandatory checks. / 默认仅报告；可选授权通知、补数读取及治理请求属于有界动作，探针不直接修改目标计划证据事实业务状态或权限。严重发现须经明确配置且独立具备当前权限的治理入口请求阻断；探针离线不取消动作入口自身强制检查。

Record fact, deterministic calculation, labeled inference and unknown separately. Missingness distinguishes not_occurred with evidence, not_collected, collection_failed and unavailable; forbidden is a response status, not proof an action did not occur. Temporary correlation includes generation method, original locator and confidence. Append a mapping when stable IDs arrive. Low-confidence time-based links cannot alone block high-risk work. / 分开记录事实、确定性计算、标注推断与未知；缺失区分有依据的未发生、未采集、采集失败和不可获得，无权访问不证明动作未发生。临时关联含生成方法、原位置与置信；真实编号到达时追加映射。低置信时间关联不能单独阻断高风险工作。

Restrict sources and report detail by original task/tenant/role permissions. Redact secrets, prefer digests and stable references, configure retention/deletion proof, and capture public decision summaries instead of hidden chain-of-thought. Full capture is required for boundary/plan changes, external effects, authority, high-risk evidence, handoffs, mandatory acceptance and control/compensation/takeover. Disclose any sampling of low-risk reads/debug records and its denominator effect. / 按原任务租户角色限制来源与报告粒度；遮蔽秘密，优先摘要与稳定引用，配置保留删除证明，仅采集公开决策摘要。边界计划变更、外部效果、权限、高风险证据、交接、强制验收及阻断补偿接管需全量记录；披露低风险读取调试采样及其分母影响。

<a id="refinements"></a>
## Explicit Source Refinements / 明确的来源细化

| Source ambiguity / 来源歧义 | Adopted interpretation / 采用解释 |
| --- | --- |
| Research example accepts “result or explicit missing reason”; later rules forbid completing missing mandatory branches. / 研究示例允许结果或缺失原因，后文禁止缺必需分支时完成。 | The frozen task contract decides whether a declared gap is an acceptable deliverable; otherwise it remains incomplete. Recording a reason cannot waive a mandatory result. / 以冻结任务契约决定缺失说明能否验收，否则仍未完成，原因不构成豁免。 |
| Probe examples say “block completion” or “refuse acceptance”. / 探针示例说阻止完成或拒绝验收。 | These are findings or control requests; execution/governance owns actual transitions. / 解释为发现或控制请求，执行治理入口负责真实迁移。 |
| Required branch recovery uses started branches as denominator. / 分支回收率以已启动必需分支为分母。 | Preserve source formula, also compare frozen required inventory including never-started branches; a 100% recovery ratio alone cannot pass completion. / 保留原公式，另核对含未启动分支的冻结必需清单，回收率满分不能单独验收。 |
| Minimum remaining budget, with parallel and nested work. / 并行嵌套工作取最小余额。 | Compute per dimension and atomically reserve all applicable shared accounts; distinguish waiting from retries. / 分维度计算并原子预留全部适用共享账户，分开等待与重试。 |
| Unknown external response and recovery. / 外部响应未知与恢复。 | Keep effect unknown and reservation occupied until independently reconciled; a new run or attempt does not permit duplicate effects. / 独立核对前保持效果未知及额度占用，新运行尝试不允许重复效果。 |
| Qualitative duplication, information gain, component benefit. / 定性的重复、信息增益及组件收益。 | Require a versioned rubric or matched comparison, input provenance and units; otherwise report not computable, not an invented score. / 要求版本量规或匹配对照、输入来源及单位，否则报告不可计算而非虚构分数。 |

<a id="validation"></a>
## Evaluation and Evidence Status / 评估与证据状态

The source map preserves all numbered source chapters, 11 stages, 14 probes, 54 formulas, 8 execution cases and 12 probe cases by source line range and SHA-256. Local `PCF`, `PCM`, `PCE` and `PCQ` IDs are locators only. All source business cases remain `not_executed`; source snapshots are immutable original-language evidence, while maintained metadata and instructions are bilingual. / 来源映射以行范围和 SHA-256 保留全部编号章节、11 阶段、14 探针、54 公式、8 执行用例和 12 探针用例。本地编号仅用于定位；来源业务用例均未执行，副本保留原语言作为证据，维护元信息及说明中英双语。

Additional adopter checks / 采用系统补充检查:

| ID | Input → expected result / 输入 → 预期结果 |
| --- | --- |
| PCI-01 | Two branches race for the last parent call → only one reservation succeeds. / 两分支抢最后一次父预算 → 仅一方预留成功。 |
| PCI-02 | Required branch never starts; started branches all finish → inventory gate stays incomplete. / 必需分支从未启动，其余全完 → 清单闸仍未完成。 |
| PCI-03 | Action times out after possible effect; resume new run → reconcile before any repeat write. / 动作可能生效后超时，新运行恢复 → 重写前先核对。 |
| PCI-04 | Late duplicate or contradictory event → no double count; conflicting evidence appends a report revision and may reopen finding. / 迟到重复冲突事件 → 不重复计数，冲突证据追加报告修订并可重开异常。 |
| PCI-05 | Missing approval, forged enrichment or cross-task response → no authority grant, no business state write. / 缺审批、伪造补数或跨任务响应 → 不授权、不写业务状态。 |
| PCI-06 | Empty denominator or sampled/unknown population → N/A or unknown with coverage, never automatic 100% pass. / 零分母或采样未知总体 → 带覆盖信息的不可用或未知，不能自动满分通过。 |
| PCI-07 | Probe unavailable while independently required business gates pass → observation gap reported; only explicit policy can require observation availability. / 探针不可用但独立业务门通过 → 报观测缺口，仅显式策略可要求观测可用性。 |

These seven additional cases are also unexecuted. A real result must include host/version, input, expected/actual outcome, independent evidence, authority scope and remaining limitations. Run `scripts/validate_pattern_combination_docs.py`, the full Skill validator and relevant repository tests after changes; regenerate the HTML. These checks verify asset integrity, registration and navigation, not business execution. / 七项补充用例同样未执行。真实结果须含宿主版本、输入、预期实际结果、独立证据、授权范围及剩余限制。修改后运行专用资产校验、完整 Skill 校验及相关仓库测试并重生成 HTML；这些检查验证资产注册导航，不证明业务已运行。
