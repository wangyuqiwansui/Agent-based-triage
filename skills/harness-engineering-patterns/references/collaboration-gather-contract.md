# Fan-Out/Gather Supplement Contract / 扇出聚合补数契约

Description / 描述: Exchange observations, gaps, evidence-backed metadata and receipts without transferring business authority to a probe. / 交换观测、缺口、有据元数据与回执，不向探针转移业务权限。

Version / 版本: `0.1.0`; source protocol / 来源协议: `扇出聚合补数协议/0.1.0`; status / 状态: draft specification / 草案规格。

Usage / 适用场景: Standalone execution, optional online observation, or an independent audit of an adapted workflow. Both peers may finish independently. / 独立执行、可选在线观测或适配外部工作流的独立审计；双方可以独立完成。

This is a documentation contract. It does not extend `collaboration-record.schema.json` or implement dispatch, storage, authorization, collection or metrics. The shared source contract `2.0.0`, executable profile `3.0.0` and this dedicated `0.1.0` protocol are distinct; migration requires explicit field, identity and evidence mappings. / 本节是文档契约，不扩展现有 Schema，也不实现调度、存储、授权、采集或指标。通用来源契约 `2.0.0`、可执行配置 `3.0.0` 与本专用 `0.1.0` 协议分别维护；迁移须显式映射字段、身份与证据。

### Envelope / 消息信封

| Fields / 字段 | Meaning and validation / 含义与校验 |
| --- | --- |
| `schema_version`, `message_type`, `message_id` | Version `0.1.0`, one of the five message types below, globally unique message identity. Reject incompatible versions before processing. / 版本为 `0.1.0`，类型取下方五类之一，消息标识全局唯一；先拒绝不兼容版本。 |
| `run_id`, `plan_revision`, `probe_run_id` | Bind the business run and frozen plan. A probe uses its own run identity in addition to the target run. / 绑定业务运行与冻结计划；探针另有自身运行身份。 |
| `producer_id`, `producer_sequence` | Authenticate the producer; sequence numbers increase within that producer instance only. Cross-producer timestamps are not global order. / 认证生产者；序号仅在同一生产者实例内单调增长，跨生产者时间戳不代表全局顺序。 |
| `node_id`, `shard_id`, `attempt_id` | Bind applicable execution scope. Run-level events may use null; do not invent a shard. / 绑定适用执行范围；运行级事件可为空，不伪造分片。 |
| `artifact_ref`, `artifact_revision`, `artifact_hash` | Exact immutable artifact binding whenever an artifact is involved. A mutable latest reference is insufficient. / 涉及工件时绑定精确不可变版本；可变的最新引用不足。 |
| `occurred_at`, `observed_at` | Distinguish occurrence from collection. Unknown historical occurrence remains null with a reason. / 区分发生与采集时间；历史发生时间未知时保留空值及原因。 |
| `causation_id`, `correlation_id` | Direct cause and the complete supplement chain; an initial message may lack a direct cause. / 直接原因与完整补数链；首条消息可无直接原因。 |
| `data_origin` | Original record, source read, deterministic derivation or historical replay; model guesses are ineligible. / 原始记录、来源读取、确定性推导或历史重放；模型猜测不可采纳。 |
| `payload`, `evidence_refs` | Typed payload and controlled references to supporting snapshots, logs or artifacts. References and hashes alone do not prove authority or truth. / 类型化载荷及受控快照、日志或工件引用；引用和摘要本身不证明权限或真实性。 |

### Five Message Types / 五类消息

| Type / 类型 | Minimum payload and receiver action / 最小载荷与接收动作 |
| --- | --- |
| `observation_event` | Event name, object version, fact references and producer authority scope. Append observation; never directly update authoritative business state. / 事件名称、对象版本、事实引用与生产者权限域；追加观测，不直接改业务权威状态。 |
| `gap_request` | `gap_id`, category, target artifact/field, required semantics, time range, necessity, allowed sources, deadline and budget. Determine recoverability before reading. / 缺口标识、类别、目标工件与字段、所需语义、时间范围、必要性、允许来源、截止与预算；先判能否恢复再读取。 |
| `data_patch` | `patch_id`, `gap_id`, exact target/base hash, field path, recovered value, source, collection time and validation evidence. Validate before appending a derived revision. / 补丁与缺口标识、精确目标及基准摘要、字段路径、补充值、来源、采集时间与校验证据；通过后追加派生修订。 |
| `action_proposal` | `action_id`, gap, bounded action/shards, required authority, estimated resources and reason. Execution decides authorization and scheduling. / 动作标识、缺口、限定动作与分片、所需权限、预计资源和原因；执行侧决定授权与调度。 |
| `apply_receipt` | Patch/proposal identity, disposition, rejection reason, new artifact binding, revalidation nodes/results/evidence and gap state. Preserve submitted, adopted, revalidated and closed separately. / 补丁或建议标识、采纳状态、拒绝原因、新工件绑定、重验节点／结果／证据和缺口状态；分开记录提交、采纳、重验与关闭。 |

Source receipt dispositions / 来源采纳状态: `已采纳` (adopted), `已拒绝` (rejected), `重复消息` (duplicate), `待处理` (pending). Gap states / 缺口状态: `已发现` → `待采集` → `已补采` → `已提交` → `已采纳` → `已重验` → `已关闭`, with `不可恢复` or `已拒绝` as explicit dispositions. Transitions require evidence; a failed recheck leaves an adopted gap open. / 状态推进须有证据，重验失败的已采纳缺口仍保持未闭环。

### Allowed Data and Protected State / 允许数据与受保护状态

Recover only facts that already exist: attempt history in authoritative logs, source versions in immutable snapshots, verified source lineage, and derived conversions with exact inputs and rule versions. A current page cannot establish its historical content. / 仅恢复已经存在的事实：权威日志中的尝试历史、不可变快照中的来源版本、经核验血缘，以及有确切输入和规则版本的派生换算；当前页面不能证明历史内容。

Write supplements only to allowed derived metadata or observation records. Never overwrite raw cards, original `value` or `claim`, `verdict`, `accepted`, seam pass status, authority, budgets, expected shards or acceptance thresholds. Conflicting old and recovered values require a discrepancy record and review. New claims require execution to acquire a new evidence card; changed scope requires an authorized new plan revision. / 补数只写入允许的派生元数据或观测记录；禁止覆盖原卡、原始值和主张、业务表述、结构准入、接缝通过状态、权限、预算、预期分片或验收阈值。旧值与补采值矛盾时记录差异并复核；新主张由执行侧获取新卡，范围变更须授权并生成新计划版本。

Gap necessity comes from frozen scenario policy: business-mandatory data, metric-required observation data, or optional diagnosis. Missing business evidence blocks its gate; optional telemetry loss does not invalidate independently supported business checks. / 缺口必要性来自冻结场景政策，分为业务强制、指标计算必要和可选诊断；缺业务证据阻断相应闸门，可选观测缺失不取消独立有据的业务检查。

### Adoption and Revalidation Workflow / 采纳与重验流程

1. Detect a gap and recover within authorized sources, time and cumulative budgets; otherwise retain null and a reason or propose new evidence collection. / 发现缺口，在授权来源、时间与累计预算内恢复；否则保留空值和原因，或建议重新采证。
2. Execution authenticates sender/source/authority and checks run, plan, active attempt where applicable, exact base hash, field allowlist and derivation. Stale bases are rejected or explicitly reevaluated. / 执行侧认证发送者、来源与权限，核对运行、计划、适用的有效尝试、精确基准摘要、字段白名单与推导；过期基准拒绝或显式重新评估。
3. Append a derived version and durable adoption receipt. Use host conditional commit and a recoverable event-publication boundary; do not overwrite the original. / 追加派生版本及持久采纳回执，使用宿主条件提交与可恢复的事件发布边界，不覆盖原件。
4. Revalidate from the earliest affected node through its dependencies; recompute final qualified shards and create a new report revision. Mark a gap closed only after supported revalidation and explicit closure. / 从最早受影响节点重验依赖下游，重算最终合格分片并生成新报告；有据重验与显式关闭后才计闭环。

| Recovered information / 补充内容 | Revalidation dependency / 重验依赖 |
| --- | --- |
| Source location or version / 来源定位或版本 | `N03` local admission → `N04–N09`; recompute final Q. / 从局部准入重验至报告，重算最终 Q。 |
| Entity mapping, units, denominator / 对象映射、单位、分母 | `N05` normalization → `N06–N09`, plus coverage refresh. / 归一化及下游，并刷新覆盖。 |
| Source lineage / 来源血缘 | `N06` grouping → `N07–N09`, including decisions depending on independence. / 来源分组及下游，包括依赖独立性的裁决。 |
| Historical execution logs / 历史执行日志 | Observation metrics; conflicts with authoritative business state return for reconciliation. / 重算观测指标，与业务权威状态矛盾时提交核对。 |
| Recheck and closure receipts / 重验与关闭回执 | Supplement closure and report revision linkage; sending alone earns no closure. / 补数闭环及报告修订关系，仅发送不计闭环。 |

### Idempotency, Time and Faults / 幂等、时间与故障

Deduplicate events by `message_id`, adoption by `patch_id`, submissions by artifact identity/revision, coverage by logical shard, and closure by `gap_id`. An exact retry returns the original adoption result; a reused ID with divergent content requires rejection, not a second mutation. These are different counting units. At-least-once delivery is not end-to-end exactly-once execution. / 事件按消息标识、采纳按补丁标识、提交按工件版本、覆盖按逻辑分片、闭环按缺口标识去重；完全重试返回原结果，同标识异内容应拒绝，不能再次修改。这些计数单位不同，至少一次投递不等于端到端恰好一次执行。

Late events retain their original run, plan and occurrence window. Quarantine stale, timed-out or superseded returns before selecting the current view. Keep sealed reports immutable; corrections create linked revisions. Without a receipt, a submitted patch remains pending. / 迟到事件保留原运行、计划和发生窗口；过期、超时或被替代返回先隔离，再决定当前视图；封存报告不可后台修改，更正生成关联新版本；无回执的已提交补丁仍待处理。

The probe defaults to read-only imported inputs. Online mode alone grants no active collection permission. Active reads need allowed resources and paths, live authority, calls/time/cost limits, redaction and an audit ledger, with separate accounting inside the global authorized budget. Unknown cost is not zero. Returned text and untrusted links do not grant new instructions or access. / 探针默认只读导入输入，在线模式不自动授予主动采集权限；主动读取须允许资源与路径、实时权限、调用／时间／费用限额、脱敏和审计，在全局授权预算内分账；未知费用不记零，返回文本与不可信链接不产生新指令或访问授权。

Probes may propose scoped recovery; they cannot expand workers, retry business actions, authorize writes or lower gates. Probe failure records partial observation and its own failure, leaving mandatory execution checks in force. Observation events use a separate namespace and do not recursively trigger the same probe. Cancellation stops new dispatch and requests cancellation of running attempts; it does not prove an external action was undone. / 探针可建议局部恢复，不可自行扩容、重试业务、授权写入或降低闸门；探针失败记录自身故障与部分观测，执行侧强制检查继续有效；观测事件使用独立命名空间，默认不递归触发同类探针。取消停止新派发并请求终止在途尝试，不证明外部动作已撤回。

### Fixture Exchange / 固定样例交互

In the fixture, card B already says the workspace is shared, while its export omits a source version present in the bound immutable snapshot. A `gap_request` for `/derived_metadata/source_version` may yield a source-backed `data_patch`. An adopted `apply_receipt` must bind the derived B revision and recheck `N03–N09`; closure requires the recheck evidence and closed gap state. The raw shared-workspace claim stays unchanged. If B never existed, this patch cannot create B. / 固定样例中 B 原卡已写明工作区共享，导出缺少的来源版本存在于所绑定不可变快照。针对该派生字段的缺口请求可得到有来源的补丁；采纳回执须绑定 B 的新派生版本并重验 `N03–N09`，重验证据与缺口关闭俱全才计闭环；原始共享主张保持不变。若 B 从未存在，该补丁不能创造 B。
