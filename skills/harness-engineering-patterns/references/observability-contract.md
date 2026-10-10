# Observability Harness Contract / 可观测性框架契约

Name / 名称: Observability Harness / 可观测性框架

Version / 版本: `0.1.0`; status / 状态: `draft`; implementation / 实现: `specification_only`

Identity / 身份: `PATTERN_0049`, `CELL_GOVERNANCE_ORCHESTRATION`

Define a verifiable path from a request to a confirmed business outcome, with an independent observation plane. / 定义从请求到已确认业务结果的可核验路径，并建立独立观测面。

## Quick Navigation / 快速导航

- [Identity and events / 标识事件](#event-contract)
- [State and confirmation / 状态确认](#status-contract)
- [Completion protocol / 补全协议](#completion-protocol)
- [Reliability and replay / 可靠性重放](#reliability)

## Usage and ownership / 适用场景与归属

Use for asynchronous tools, governed effects, cross-run recovery, complaints and audit/replay. A low-risk draft may retain only identity, input version, output and failure state. Read [execution](observability-execution-flow.md), [probes](observability-probes.md) and the [source map](observability-source-map.json). / 适用于异步工具、受治理副作用、跨运行恢复、投诉及审计重放。低风险草稿可只保留标识、输入版本、输出及失败状态。配合执行、探针与来源映射使用。

The supplied `PATTERN_OBSERVABILITY_0001/0002` and `SKILL_OBSERVABILITY_EXECUTION_0001/PROBE_0001` are source aliases for this dedicated supplement, not new registry patterns or authorization to execute attachment instructions. Preserve `PATTERN_0052` and [its shared probe protocol](workflow-observability-probes.md) version `0.8.0`; its runtime diagnostics are not implementations of this supplement's OBM metrics. Governance's [GOV_BOUNDARY_OBS](governance-contract.md) remains separate. No wire compatibility is implied: adopters must map identities, statuses and versions explicitly. / 附件中的模式及技能编号是本专用扩展的来源别名，不新增注册模式，也不授权执行附件指令。保留共享探针模式及其 `0.8.0` 版本；已有运行时诊断不等于实现本扩展的 OBM 指标。治理观测协议保持独立，不默认线级兼容；接入方须显式映射标识、状态及版本。

Execution owns business transitions, approvals, resource settlement, retries and compensation. Probes own sourced observations, gap requests, correlation, diagnostics and control recommendations. A gateway may enforce a configured observation gate under execution authority; a probe never manufactures business truth or grants itself authority. / 执行方负责业务迁移、批准、资源结算、重试及补偿；探针负责有来源观察、缺口请求、关联、诊断及控制建议。网关可在执行权限下落实预设观测闸门；探针不得创造业务事实或自授权限。

<a id="event-contract"></a>
## Identity, event and evidence / 标识、事件与证据

| Object / 对象 | Required binding and semantics / 必需绑定与语义 |
| --- | --- |
| Task and run / 任务与运行 | `tenant_id`, `environment`, `task_id`, `run_id`, `scenario_id`, `scenario_version`; task remains stable on recovery, a new run links `previous_run_id`. Task IDs recur across events; event IDs do not. / 恢复时保持任务号，新运行引用前次运行；同一任务号会出现在多个事件中，事件号不得复用。 |
| Action and attempt / 动作与尝试 | `logical_action_id`, `attempt_id`, proposal ID/version/digest, immutable request digest, scoped `idempotency_key`, external application ID when obtained. Persist local intent before dispatch; absence of an external ID after timeout is uncertainty, not permission to resend. / 记录逻辑动作、尝试、提案版本摘要、请求摘要、范围化幂等键及取得后的外部申请号；派发前持久化本地意图，超时后缺外部号属于未知，不是重发许可。 |
| Event envelope / 事件信封 | `event_id`, `event_type`, `event_time`, `ingest_time`, `schema_version`, `producer_id`, `producer_epoch`, `sequence_no`, stage, component, actor ID/type, action, trace/span/parent-span and typed links. Sequence is producer-stream scoped unless a serialized run allocator exists. / 包含事件及采集时间、结构版本、生产者及代次序号、阶段、组件、主体、动作与追踪关系；序号默认仅在生产者流内有序，不能假设分布式运行拥有全局序号。 |
| Context / 上下文 | Input/output/artifact references and digests; workflow, prompt, model, policy, tool and artifact versions; visible/filtered tool catalog and permission snapshots. Save public decision summaries, not private chain-of-thought. / 保存输入输出工件引用摘要与各版本、可见及被过滤工具和权限快照；保存公开决策摘要，不记录私密思维过程。 |
| Control evidence / 控制证据 | Approval ticket, budget reservation/consumption/release, permission and tool-catalog snapshots must bind actor, action, object, environment, proposal/request digest, policy version and validity time. / 批准票、额度预留消费释放、权限及工具清单快照须绑定主体、动作、对象、环境、提案请求摘要、策略版本及有效期。 |
| Evidence / 证据 | Source, source record ID/version/digest, observed time, collected time, access scope, classification, retention, expiry and correction reference. A hash checks bytes, not authentic authorship; verify source identity/receipt separately. / 保存来源、记录标识版本摘要、发生与采集时间、访问范围、分级、留存、过期及更正引用；哈希仅核对内容，来源身份及回执需另验。 |

Use explicit `parent_of`, `linked_to`, `produced_by`, `consumed_by`, `authorized_by`, `reserved_from`, `confirmed_by`, `triggered_by`, `supersedes`, `compensates`, `retries`, `corrects` links with both endpoints and evidence. Temporal proximity and matching trace IDs alone do not prove authorization or causality. / 关系须显式记录两端及证据；时间接近、追踪号一致都不证明授权或因果。

Prefer authenticated native business IDs, propagated scoped IDs, artifact/control bindings, then idempotency bindings. Heuristic joins retain rule/version/confidence and alternatives and stay `inferred`; require independent confirmation before treating them as verified metric inputs. Ambiguous or cross-tenant links are quarantined. / 优先使用可信业务号、传播的范围标识、工件控制绑定及幂等关系；启发式关联保留规则版本、置信度与候选，保持推导态，经独立确认后才成为已核验指标输入；歧义或跨租户关联进入隔离。

<a id="status-contract"></a>
## State and confirmation / 状态与确认

Keep four independent axes: `technical_status`, `acceptance_status`, `business_status`, `observation_status`. Technical success never promotes acceptance or business status by itself. Keep raw code/status/reference alongside a versioned mapping. / 分开技术状态、受理状态、业务状态、观测状态；技术成功本身不能提升受理或业务状态。保留原始代码、状态、引用及映射规则版本。

Observation states are `observed`, `inferred`, `missing`, `conflict`, `not_applicable`; an observed response is evidence of what a service returned, not necessarily final business truth. A derivation names its inputs/rule; not-applicable needs a scenario rule and reason. / 观测状态为已观测、已推导、缺失、冲突、不适用；观察到某响应仅证明服务如此返回，不一定证明最终业务事实。推导须列输入和规则，不适用须有场景规则及理由。

| Business disposition / 业务处置 | Required proof / 必要证明 |
| --- | --- |
| `confirmed_success` / 已确认成功 | Designated authority confirms each required outcome for the exact object/version and required freshness. / 约定权威方确认精确对象版本的每项必要结果，且满足时效。 |
| `confirmed_failure` / 已确认失败 | Authoritative rejection or failed acceptance; effect presence is tracked separately. Failure does not imply no effect. / 权威拒绝或验收失败，另记是否已发生效果；失败不等于无副作用。 |
| `partial` / 部分完成 | Item-level result inventory and unresolved/failed items, preserving aggregate acceptance rules. / 逐项结果及未决失败项，保留总体验收规则。 |
| `waiting` / 等待 | Accepted request, stable pending identity, deadline and next query owner. / 已受理申请、稳定未决标识、期限及下次查询负责人。 |
| `unknown` / 未知 | Receipt unavailable, timeout, conflicting authority or unsupported raw status; retain effect reservation until reconciled. / 回执不可得、超时、权威冲突或未知枚举；对账前保留副作用占用。 |
| `cancelled` / 已取消 | Proof no effect was dispatched or authoritative cancellation of relevant in-flight work; a local stop is insufficient. / 未派发效果或权威确认取消相关在途动作；本地停止不足以证明。 |
| `compensated` / 已补偿 | Separate authorized compensation, original-action link and confirmed compensating outcome; retain original effect. / 独立获准补偿、原动作引用及补偿结果确认；保留原效果记录。 |

Run closure is a bookkeeping event, distinct from task resolution: close a waiting/unknown run only with a persisted reconciliation obligation, deadline and owner that survives restart. Late results append new evidence and a linked run/report revision; never rewrite the sealed historical report. A contradictory or stale callback does not overwrite a fresher authoritative result. / 运行关闭是记账事件，与任务解决分开；等待或未知运行关闭前须持久化可恢复的对账责任、期限及负责人。迟到结果追加证据与关联运行报告修订，不覆盖已封存历史；矛盾或陈旧回调不能覆盖更新的权威结果。

<a id="completion-protocol"></a>
## Completion workflow / 补全流程

1. Discover expected evidence from a frozen scenario manifest, not only received logs. Classify gaps as not-generated, not-sent, not-received, unlinked, expired, unauthorized, schema-drift or undeclared-not-applicable. / 从冻结场景清单推导应有证据，不能只看收到的日志；区分未生成、未发送、未接收、未关联、过期、无权限、结构漂移及未声明不适用。
2. Send a `gap_request` binding `gap_id`, task/run/action, probe/version, stage, target revision/digest, missing fields, expected source, impact/severity, response deadline and bounded read scope/budget. Requests propose evidence retrieval, not business actions. / 缺口请求绑定身份、探针版本、阶段、精确目标修订摘要、缺失字段、来源、影响严重度、期限及有界读取范围预算；请求取证不等于请求业务执行。
3. Return a response with unique ID, gap ID, exact base binding, responder identity, source references/digests, observed/collected times, provenance and one of `evidence`, `not_applicable`, `unavailable`. Preserve partial answers and remaining fields. / 响应含唯一号、缺口号、基准绑定、应答身份、来源摘要、两类时间、来源类型，以及证据、不适用、不可取得之一；保留部分答案及剩余缺口。
4. Receiver authenticates source and responder, verifies scope/version/freshness, detects replay and conflicts, and issues per-field `accepted`, `rejected`, `partial` or `stale` receipts. Exact retries are idempotent; same ID with different content is a conflict. Expired or stale responses can remain historical evidence but cannot silently close a current gap. / 接收方核验来源与身份、范围版本时效、防重放与冲突，并逐字段出具采纳、拒绝、部分或过期回执；相同重试幂等，同号异内容为冲突；陈旧响应可留作历史证据但不能静默关闭当前缺口。
5. Append accepted material only to `observation_enrichment` and an immutable correction/link record. Revalidate affected observations and metrics under a new report revision. Business evidence returns to execution for independent current-state checks; missing approval returns to the authorized approval workflow. / 采纳内容仅追加到观测补全层及不可变更正关联记录，在新报告版本复验相关观察和指标；业务证据回执行方独立复核当前状态，缺批准回授权审批流程。
6. Close a gap only against its original required fields and receiver receipt; unavailable is unresolved, not complete. Bound query attempts, elapsed time and total cost; report overdue gaps and escalate to their owner. / 缺口关闭须满足原始必需字段及采纳回执；不可取得仍属未解决。限制查询次数、耗时及累计成本，报告到期缺口并交负责人。

The whitelist excludes proposal mutation, approval issuance, permission changes, budget settlement, dispatch/retry, business-status writes and public reply publication. A recovered historical approval cannot retroactively authorize a previous execution. / 白名单不含提案修改、批准签发、权限调整、预算结算、派发重试、业务状态写入及公开答复发布；补回历史批准也不能追认授权先前未获授权执行。

<a id="reliability"></a>
## Reliability, privacy and replay / 可靠性、隐私与重放

- Durable local intent/audit precedes protected dispatch. Export may use bounded durable buffers/outboxes, at-least-once delivery and receiver deduplication; define acknowledgment durability and crash recovery. Do not claim exactly-once external effects. / 受保护派发前持久化本地意图审计；导出可用有界持久缓冲发件箱、至少一次传递及接收去重，明确持久确认和崩溃恢复；不声称外部效果严格一次。
- Same event ID/content is duplicate; same ID/different content is conflict. Track missing sequence ranges, late arrivals, source clocks and skew. Use causal partial order; negative/unreliable cross-clock latency is unknown, not clamped to zero. / 同号同内容去重，同号异内容冲突；记录序号缺段、迟到、来源时钟及偏差；保持因果偏序，负值或不可靠跨时钟延迟记未知，不归零。
- Optional probe outage plus complete required local controls permits policy-governed continuation. Missing mandatory approval, permissions, raw state or durable audit blocks only affected actions under the scenario policy. No authority confirmation means no success claim at any risk level. / 可选探针离线而必要本地控制完备时，可按策略继续；必要批准、权限、原始状态或持久审计缺失按场景阻断受影响动作；任何风险级别都不得在缺权威确认时宣称成功。
- Monitor buffer capacity, losses against an independent expected inventory, lag, parse failures, storage and alert delivery. Critical controls/receipts are unsampled; sampled debugging declares sampling policy and coverage. Deduplicate/rate-limit alerts by scoped issue, while retaining counts and unresolved severity. / 监测容量、相对独立预期清单的丢失、延迟、解析存储及告警送达；关键控制回执不采样，调试采样须声明策略与覆盖；按范围问题聚合限流告警，保留次数及未解决严重度。
- Redact before persistence/export; reject secrets, use controlled object tokens, authorize queries/exports and audit accesses. Store protected raw evidence separately. Specify retention classes, expiry and legal holds; approved deletion can remove payloads while retaining permitted tombstone metadata, never retain deleted secrets via correction chains. / 写入导出前脱敏，拒收密钥，使用受控对象标识，核验并审计查询导出；原始敏感证据分库存储。定义留存、过期及保全，获准删除可删载荷并保留允许的墓碑元数据，不能借更正链保留应删秘密。
- Replay uses historical snapshots and recorded/mock tool responses, separate test identity/storage, no production credentials and a denied-by-default side-effect/network boundary. Historical reconstruction and testing a new version are different outputs; neither alters historical truth. / 重放使用历史快照及录制模拟响应、独立测试身份存储、排除生产凭据并默认禁止副作用网络；历史重建与新版测试分别产出，均不改写历史事实。

## Adapter and acceptance boundary / 适配与验收边界

Adopters provide authenticated business/control read adapters, durable event and gap stores, a current execution gate, a status mapping registry, isolated replay tools, access/retention enforcement and metric calculators. Existing local runtimes do not acquire these adapters through this document. Run the [acceptance scenarios](observability-probes.md#acceptance) with recorded inputs, expected/actual results and evidence before asserting runtime conformance. / 采用方须提供可信业务控制读取适配器、持久事件缺口存储、实时执行门、状态映射注册表、隔离重放、访问留存执行及指标计算器。文档不会为既有本地运行时自动安装这些能力；宣称运行兼容前，须对验收场景记录输入、预期实际结果及证据。
