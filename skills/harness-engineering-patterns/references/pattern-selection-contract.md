# Pattern Selection and Probe Contract / 模式选型与探针共享契约

Name / 名称: Pattern Selection Exchange / 模式选型交互。Version / 版本: `0.1.0`. Description / 描述: A specification-only reconciliation of the two supplied draft documents. / 对两份来源草案统一口径的设计规格。Source contract / 来源契约: `OBSERVABILITY_SUPPLEMENT_V1`; maintained profile / 维护配置: `pattern-selection/0.1.0`.

## Usage and Workflow / 适用场景与流程

Read with [execution](pattern-selection-execution-flow.md) and [probes](pattern-selection-observability-probes.md). The [source map](pattern-selection-source-map.json) retains immutable source bytes, hashes and section locations. Workflow emits versioned public evidence → probe associates and proposes enrichment → receiver validates bindings → append acceptance or rejection → workflow independently revalidates any affected decision. / 配合执行流程与探针阅读。来源映射保留原始字节、摘要和章节位置。流程发送版本化公开证据，探针关联并提出补全，接收方校验绑定后追加接受或拒绝记录，流程独立复验受影响决定。

This profile does not implement a collector, evaluator, business guard, transaction manager or new runtime Schema. Existing reasoning, tool-dispatch and collaboration schemas remain normative for their runtimes; source event names cannot simply be passed to them without a validated adapter. / 本配置尚未实现采集器、评估器、业务闸门、事务管理器或新的运行时 Schema。现有推理、工具调度与协作 Schema 仍约束各自运行时，来源事件名未经已验证适配不能直接传入。

## Identity and Compatibility / 身份与兼容

| Source issue / 来源差异 | Maintained interpretation / 维护口径 |
| --- | --- |
| `PATTERN_SELECTION_0001`, `SKILL_SELECTION_0001` | Aliases of this procedure; no matrix-cell promotion or new Skill installation. / 本规程出处别名，不晋升矩阵单元或安装新技能。 |
| `PATTERN_OBSERVABILITY_0001`, `SKILL_OBSERVABILITY_0001` | Provenance aliases for a selection-specific profile of existing `PATTERN_0052`. Keep its existing `0.8.0` reference and other metric families intact. / 作为既有探针的选型专用配置出处，保留既有版本及其他指标族。 |
| Execution G1/G2/G3 vs probe G0–G8 / 执行门与探针门同名异义 | Require `checkpoint_namespace` (`selection` or `probe`) and `checkpoint_id`; use `SEL-G*` and `OBS-G*` in prose. Bare G2/G3 is ambiguous and rejected by an adopting adapter. / 接口须带命名空间和门编号，文档用前缀区分，适配器拒绝裸同名门。 |
| `workflow.response.generated` vs `workflow.response.drafted` | Normalize generated → drafted only; retain original name. Neither implies grounding, sending or delivery. / 仅将生成归一为草稿，保留原名，不代表有据、已发或送达。 |
| Eight execution fact states vs nine probe states / 执行八态与探针九态 | Use the union below; human judgment is not automatically authoritative verification. / 使用下方并集，人工判断不自动等于权威验证。 |
| General `MTR-*`, `PRB-*`, `ANO-*` names / 通用指标探针异常编号 | Qualify every identity with `profile` and version; never merge with other metric families by suffix or label. / 全部身份携带配置和版本，不按后缀或名称合并其他指标族。 |

## Checkpoint Map / 安全门映射

| Namespaced checkpoint / 带命名空间的门 | Location and meaning / 位置与含义 |
| --- | --- |
| SEL-G1 | After S1: complete task contract. / S1 后：任务契约完整。 |
| SEL-G2 | After S2: baseline sufficiency; sufficient goes to S8. / S2 后：基线是否足够，足够直达 S8。 |
| SEL-G3 | After S8: comparison acceptance. / S8 后：比较验证验收。 |
| OBS-G0 | After S0: identity, versions, risk, owner. / S0 后：标识、版本、风险、责任。 |
| OBS-G1 | After S1: completion, safe exits, prohibitions. / S1 后：完成、安全出口、禁止事项。 |
| OBS-G2 | After S3: evidence-backed diagnosis. / S3 后：诊断证据。 |
| OBS-G3 | After S4: model necessity and boundary. / S4 后：模型必要性与边界。 |
| OBS-G4 | After S5/S6: topology and control completeness. / S5、S6 后：拓扑与控制完整性。 |
| OBS-G5 | Each risky workflow action before dispatch. / 业务流程每次风险动作派发前。 |
| OBS-G6 | Each risky action after effect verification. / 每次风险动作效果核验后。 |
| OBS-G7 | Before each public reply. / 每次对外回复前。 |
| OBS-G8 | At run close: verified outcome, metrics, unresolved anomalies. / 运行结束：核验结果、指标、未闭环异常。 |

The first five probe checkpoints inspect selection; the last four inspect execution of the designed workflow. They are not all one-time design-stage gates. / 前五个探针门检查选型，后四个检查所设计工作流的实际执行，不全是一次性的设计阶段门。

## Evidence States / 事实状态

`verified` / 已验证, `observed` / 已观测, `declared` / 用户声明, `human_judgment` / 人工判断, `inferred` / 模型推断, `unknown` / 未知, `conflict` / 冲突, `expired` / 过期, `not_applicable` / 不适用.

Record value/reference, source identity, object/version, observed and verified times, validity and verifier scope. A later verification appends a new evidence revision tied to an authoritative source; it does not relabel the original declaration. Unknown/conflict/expired or inference alone cannot satisfy a risky action prerequisite. Even verified facts require current action authority and applicable business checks. / 记录值或引用、来源身份、对象版本、观察及核验时间、有效期和核验者范围。后续核验须追加绑定权威源的新证据版本，不改写原声明。未知、冲突、过期或单纯推断不能满足风险前置条件；已验证事实仍需当前行动权限及适用业务检查。

## Event Envelope / 事件包络

Events require `schema_version`, `profile`, immutable `event_id`, event type, occurred/ingested times, actor, object, context and payload summary. Correlate `selection_run_id` with any number of distinct `workflow_run_id` values; never reuse a workflow run ID for all baseline/candidate cases. Selection-only events need no fabricated business run ID. / 事件须带版本、配置、不可变事件 ID、类型、发生及摄取时间、主体、对象、上下文与载荷摘要。一轮选型可关联多个独立工作流运行，不把全部基线候选案例复用为一个运行 ID。纯选型事件无需虚构业务运行 ID。

Link trace/span/parent IDs, task/rule/plan/artifact versions, step, fact/source references and tool-call/approval/effect/handoff IDs as applicable. Separate `technical_status`, `business_status`, expected effect, verified effect and response state. Missing fields mean incomplete coverage, not a negative fact. / 按需关联链路跨度及父节点、任务规则计划工件版本、步骤、事实来源及工具审批效果交接 ID。分开技术状态、业务状态、预期效果、已核验效果和回复状态。字段缺失表示覆盖不完整，不表示否定事实。

Deduplicate identical event IDs and hashes; conflicting payloads for an ID are integrity anomalies. Preserve event and ingestion times, causal references and late arrivals; arrival order alone is not execution order. A returned error may pair with a call without implying success; absent return by itself means unresolved telemetry/outcome. / 同 ID 同摘要去重，同 ID 异载荷为完整性异常。保留发生和摄取时间、因果引用及迟到事件，不以到达顺序充当执行顺序。错误返回可与调用配对但不代表成功；缺少返回本身表示遥测或结果未解决。

## Exchange and Supplements / 交互与补全

```yaml
# Proposed request shape / 请求结构规格
contract: OBSERVABILITY_SUPPLEMENT_V1
profile: pattern-selection/0.1.0
request_id: REQ-example
selection_run_id: SEL-example
workflow_run_id: null
checkpoint_namespace: selection
checkpoint_id: G1
target_revision: "1"
target_hash: "hash-of-frozen-target"
expected_fields: [completion_conditions, safe_exits, prohibited_effects]
events: []
blocking_policy: advisory
deadline_at: "host-supplied-deadline"
```

Response echoes request/run/checkpoint and exact target revision/hash, then reports coverage, missing fields, anomaly refs, supplements, metric snapshots and `continue | warn | review | suspend | block`. These are signals interpreted by the workflow's preconfigured policy, not grants of business authority. Late or stale responses are retained as observations and cannot pass a newer gate. / 响应回显请求运行检查点和精确目标版本摘要，返回覆盖、缺字段、异常、补丁、指标和继续、告警、复核、暂停、阻断信号。信号由流程预设策略解释，不授予业务权限；迟到或陈旧响应保留为观察，不能放行新版本门。

Each supplement binds `supplement_id`, request and run IDs, phase/step, allowlisted `field_path`, base revision/hash, value type, evidence refs, collection method, evidence state, probe identity and proposed application policy. `overwrite_allowed` is always false. Record a separate acceptance/rejection receipt with receiver, time, resulting revision and reason. / 每条补丁绑定自身、请求和运行 ID、阶段步骤、允许字段路径、基准版本摘要、值类型、证据、采集方式、事实状态、探针身份及建议应用策略；禁止覆盖。接收或拒绝通过独立回执记录接收者、时间、结果版本和原因。

Only authenticated direct observations and exact associations may auto-append to observation fields. Inferred associations remain inferred even when packaged as a link. Conflicting values coexist with a conflict record; stale-base patches require rebasing and review. Idempotent repeats reuse the receipt; changed content under the same supplement ID is rejected. Business-evidence use requires source verification and downstream decision revalidation, separate from accepting the observation. / 仅经认证的直接观察与精确关联可自动追加到观测字段；推断关联即使包装为链接也仍是推断。矛盾值并存并建冲突记录；陈旧基准须重定基准和评审。相同补丁幂等复用回执，同 ID 改内容则拒绝。观测接收与用于业务证据分开，后者需核验来源及复验下游决定。

## Constraints and Failure Behavior / 约束与故障行为

- No patch may change goals, rules, authority, approvals, plans, executed effects or business state. Corrections append evidence and route action requests to the independent authorized workflow. / 补丁不得改变目标、规则、权限、审批、计划、已发生效果或业务状态；更正追加证据，动作请求交独立授权流程。
- Sidecar and offline modes remain advisory. Interactive blocks require a preconfigured business gate, exact scope and host enforcement. Probe outage never waives a mandatory business check; an optional probe gap need not block unrelated work. / 旁路和离线保持建议；交互阻断须预配业务门、精确范围和宿主执行。探针故障不免除必要业务检查，可选缺口无需阻断无关工作。
- Extra reads require existing authority and bounded time, scope and cumulative cost. Probe recommendations do not grant access or authorize notifications, deletions or compensations. / 额外读取须有既有权限及时间、范围、累计成本边界；探针建议不授予访问、通知、删除或补偿权限。
- Collect public evidence and concise decision reasons, never private chain-of-thought, secrets or unnecessary personal data. Prefer hashes/references, access control and declared retention. Append-only history is bounded by authorized retention/deletion policies, with auditable tombstones where permitted. / 采集公开证据和简要决策依据，不收集私密思维过程、密钥或无关个人信息。优先摘要引用、权限与保留策略；追加历史仍受授权保留删除策略约束，允许时记录可审计删除标记。
- A hash establishes byte integrity, not authority, truth or actual effect. No errors, no observed payment, or all workers returning cannot prove business success or absence of prohibited effects without sufficient independent coverage. / 摘要仅证明字节完整性，不证明权威、事实或实际效果。没有报错、未观测到付款或全员返回，均不能在独立覆盖不足时证明业务成功或禁止效果不存在。
