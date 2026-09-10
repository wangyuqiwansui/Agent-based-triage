# Hierarchical Delegation Interaction Contract / 层级委派交互契约

Name / 名称: Hierarchy execution–probe exchange / 层级执行与探针交换。
Description / 描述: A design-level field mapping of the shared source contract `0.1.0`, embedded in both mode documents. It is not the shared module's `3.0.0` runtime Schema. / 来源共享契约 `0.1.0` 的设计层字段映射，内置于两份模式文档；不是通用模块 `3.0.0` 运行时 Schema。

## Quick Navigation / 快速导航

- [Ownership / 对象归属](#ownership-and-usage--对象归属与用法)
- [Messages / 消息](#message-envelope--消息信封)
- [Events / 事件](#minimum-event-envelope--最小事件信封)
- [Adoption / 采纳](#adoption-workflow-and-constraints--采纳流程与约束)
- [Termination / 终止](#timeout-and-closed-loop-termination--超时与闭环终止)

## Ownership and Usage / 对象归属与用法

| Authority / 权威维护方 | Objects / 对象 | Other party / 另一方 |
| --- | --- | --- |
| Execution and authorized writers / 执行及授权写入组件 | Goal, responsibilities, plan, business state, formal artifacts and gate verdicts. / 目标、责任、计划、业务状态、正式工件与闸门裁决。 | Probe reads only. / 探针只读。 |
| Runtime and resource services / 运行时与资源服务 | Identity, live grants, reservations/settlement and cancellation/recovery credentials. / 身份、实时授权、预留／结算及取消／恢复凭据。 | Both read within granted scope. / 双方按授权读取。 |
| Probe / 探针 | Observation extensions, metrics, evidence gaps and supplementation proposals. / 观测扩展、指标、证据缺口与补全提案。 | Execution validates before use/adoption. / 执行先校验再引用或采纳。 |
| Execution / 执行流程 | Adoption receipts, new object versions and revalidation results. / 采纳回执、新对象版本与重验结果。 | Probe reconciles before closing gaps. / 探针核对后再关闭缺口。 |

Business write ownership never lets a model bypass runtime controls. Observation authority never grants business verdict authority. / 业务写入权不允许模型绕过运行时控制，观测权也不授予业务裁决权。

## Message Envelope / 消息信封

English keys below map to the source's Chinese fields; null means unknown/not relevant with an explicit reason in the report, not permission to guess. Event/message-specific applicability determines required fields. / 以下英文键映射来源中文字段；空值代表未知或不相关，报告中须有理由，不允许猜填；必填性按消息／事件类型确定。

```yaml
protocol_version: "0.1.0"  # 契约版本：通信协议
message_id: required       # 消息编号：唯一，重投复用
message_type: observation_request  # 消息类型
sender: execution          # 发送方
run_id: required           # 运行编号
parent_goal_id: required   # 父目标编号
goal_version: null        # 目标版本
plan_version: null        # 计划版本
baseline_snapshot_id: null # 基线快照编号
baseline_state_revision: null # 基线状态修订号
responsibility_id: null   # 责任编号
task_id: null             # 任务编号
task_contract_version: null # 契约版本号：业务任务契约
attempt_id: null          # 尝试编号
correlation_request_id: null # 关联请求编号
created_at: required      # 产生时间：带时区
deadline_at: required     # 截止时间：带时区
payload: {}               # 数据体：见下表
```

Protocol version and task-contract version are different fields. Goal/plan versions describe business scope; state revision describes progress under that scope. Sender strings and hashes do not authenticate anyone; the host must verify credentials and current write authority. / 通信协议版本与任务契约版本不同；目标／计划版本描述业务口径，状态修订描述同一口径的进度。发送方字符串与哈希不能认证身份，须由宿主核验凭据及当前写入权。

| Type / 类型 | Direction / 方向 | Minimum payload / 最小数据体 |
| --- | --- | --- |
| `observation_request` / 观测请求 | Execution → probe / 执行→探针 | Scope, requested fields, rule version, read-grant reference, budget, blocking flag and business basis. / 范围、需补字段、规则版本、读取授权引用、预算、是否阻断及业务依据。 |
| `observation_snapshot` / 观测快照 | Execution → probe / 执行→探针 | Goal/responsibility snapshots, artifact manifest, gate records, event range and completeness declaration. / 目标／责任快照、工件清单、闸门记录、事件区间与完整性声明。 |
| `observation_report` / 观测报告 | Probe → execution / 探针→执行 | Metric values and definitions, evidence, unknowns, gaps, recommendations and report version. / 指标值与口径、证据、未知、缺口、建议与报告版本。 |
| `supplement_proposal` / 补全提案 | Probe → execution / 探针→执行 | Patch ID, target object/version, field path, baseline-value digest, proposed value, evidence, expiry and affected scope. / 补丁编号、目标对象／版本、字段路径、基线值指纹、建议值、证据、有效期与影响范围。 |
| `adoption_receipt` / 采纳回执 | Execution → probe / 执行→探针 | Patch ID, per-field disposition/reason, actual new object version, affected gates and revalidation references. / 补丁编号、逐字段状态／原因、实际新对象版本、受影响闸门与重验引用。 |

No message directly authorizes business mutation. Only execution's authorized adoption may change a business object. Dispositions are `adopted / 已采纳`, `partially_adopted / 部分采纳`, `rejected / 已拒绝`, `expired / 已过期`, `superseded / 已被替代`. Partial adoption records each field separately. Required revalidation still pending must be stated and cannot close a critical gap. / 消息本身不授权业务变更；只有执行侧授权采纳后才可改变业务对象。采纳状态限定为上述五种，部分采纳须逐字段记录。必需重验未完成时须明示，不得关闭关键缺口。

## Minimum Event Envelope / 最小事件信封

```yaml
event_id: required          # 事件编号
event_type: artifact_gate_decided # 事件类型
run_id: required            # 运行编号
parent_goal_id: required    # 父目标编号
goal_version: null         # 目标版本
plan_version: null         # 计划版本
responsibility_id: null    # 责任编号
task_id: null              # 任务编号
task_contract_version: null # 契约版本号
attempt_id: null           # 尝试编号
executor_instance_id: null # 执行者实例编号
producer_id: required      # 生产者编号
producer_sequence: null    # 生产者序号
occurred_at: null          # 发生时间
received_at: required      # 接收时间
object_ref: null           # 对象引用
object_version: null       # 对象版本
object_digest: null        # 对象指纹：运行时计算
causal_event_id: null      # 因果事件编号
source_category: runtime_record # 来源类别
payload_ref: required      # 负载引用
```

Deduplicate events by `(run_id, event_id)`; isolate divergent payloads under the same ID. Deduplicate messages by unique message ID, preserving the original ID on retry. Repeated delivery is not a new attempt. Producer sequence orders only that producer, never global time; events without child tasks need no invented task/attempt IDs. / 事件按运行编号＋事件编号去重，同编号异载荷隔离；消息按唯一编号去重，重投保留原编号。重复投递不是新尝试。生产者序号只表示本生产者顺序，不是全局时间；无子任务事件不造任务／尝试编号。

## Adoption Workflow and Constraints / 采纳流程与约束

Authenticate sender and authority → deduplicate → check goal/plan versions → check target digest and expiry → enforce field allowlist → verify evidence → classify impact → create a new record/artifact version → rerun affected gates → issue receipt. / 认证发送方与权限→去重→核验目标／计划版本→核验对象指纹与有效期→执行字段白名单→复核证据→判断影响→生成新记录／工件版本→重跑受影响闸门→返回回执。

Unrelated state changes need not invalidate a whole report, but every proposal dependency must remain valid. Changes to goals, task contracts, evidence objects or gate rules require rebasing and recomputation. / 无关状态变化不必废弃整个报告，但须核验提案每项依赖；目标、任务契约、证据对象或闸门规则变更须重建基线并重算。

| Impact / 影响 | Lawful handling / 合法处理 |
| --- | --- |
| Observation timing, associations or derived statistics / 观测时间、关联、派生统计 | Write provenance-bearing observation extensions and retain original events; no business recheck unless used as acceptance evidence. / 写带来源观测扩展并保留原事件；未成为验收依据时无需业务重验。 |
| Formal artifact sources, input mapping or acceptance data / 正式工件来源、输入映射、验收数据 | Authorized writer creates a new artifact version; rerun artifact gate and affected composition gate. / 授权组件生成新工件版本，重跑工件闸及受影响组合闸。 |
| Responsibility, acceptance criteria, authority or budgets / 责任、验收条件、权限、预算 | Submit to original governance workflow for approval and versioning; probe cannot apply. / 交原治理流程批准并版本化，探针不能实施。 |
| Unperformed business responsibility / 业务责任未完成 | Return a business gap/local reassignment recommendation to execution; never manufacture completion. / 返回业务缺口／局部重派建议，不能伪造完成。 |

Probes cannot rewrite parent completion, official verdicts, settled costs, raw event timestamps, business facts or authorization scope. Record fact-valid time, source version, read time and supplementation time separately; newly acquired evidence cannot prove historical possession. / 探针不能改写父目标完成、正式裁决、已结算费用、原始事件时间、业务事实或授权范围。分别记录事实适用时间、来源版本、读取时间与补全时间；新取得证据不能证明历史上已持有。

## Timeout and Closed-Loop Termination / 超时与闭环终止

Noncritical observation timeouts do not block execution; missing required business evidence remains pending or escalates, even with a probe offline. Execution may use its own lawful evidence channels. / 非关键观测超时不阻断执行；必需业务证据缺失时保持待补充或升级，即使探针离线也一样；执行侧可使用自身合法取证渠道。

Deduplicate a gap by `(run_id, goal_version, plan_version, object_id, field_path, rule_version)`, with at most one request in flight. Bound retries, sources, reads, elapsed time and cumulative use; report generation, metric refresh and log repair do not trigger another identical observation. Only new business events, arriving evidence or an explicit recheck can begin a new round. / 缺口按运行、目标版本、计划版本、对象、字段路径、规则版本去重，最多一个请求在途；限制重试、来源、读取、耗时与累计消耗。报告、指标刷新、日志补写不触发同类观测；只有新业务事件、证据到达或明确复核才能开启新轮次。

Sending, adopting and resolving are separate states. Close critical gaps only after evidence is restored and necessary revalidation passes. Exhausted budget, rejection, termination, goal upgrade or unrecoverable evidence ends the round with an explicit reason and unresolved gaps retained. Cancel obsolete requests on goal cancellation/upgrade; do not pretend unconfirmed external reads have stopped, and never write their stale results into a new business version. / 发送、采纳、解决分别记录。证据补齐且必需重验通过后才可关闭关键缺口；预算耗尽、拒绝、终止、目标升级或不可恢复证据，以明确原因结束本轮并保留未解决项。目标取消／升级时取消旧请求，未确认的外部读取不能假装已停止，陈旧结果不得写入新业务版本。
