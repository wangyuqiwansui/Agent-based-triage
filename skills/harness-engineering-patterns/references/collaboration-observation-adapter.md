# Collaboration Observation Adapter / 协作观测适配契约

Name / 名称: Source-aligned collaboration measurements / 对齐全文的协作计量。
Description / 描述: Read-only normalized input for 20 reference metrics; authentic sources remain the host's responsibility. / 为 20 项参考指标提供只读标准输入，真实来源仍由宿主负责。

## Usage / 适用场景

Use [calculate_source_metrics](../runtime/collaboration_observability.py) for an external workflow or the collaboration module. No execution engine, task dispatch or strict collaboration-record conversion is required. Map only supported facts; unavailable data must not be replaced with fabricated success records. / 可检查外部工作流或协作模块，无需执行引擎、任务派发或严格协作记录转换。仅映射有依据的事实，不以伪造成功记录补缺。

The source contract is 2.0.0; this local input profile is 3.0.0. Source 指NN maps to CSMNN; legacy CMNN has different definitions. [The source map](collaboration-fulltext-source-map.json) owns formulas and implementation status. / 来源契约为 2.0.0，本地输入配置为 3.0.0。来源指 NN 对应 CSMNN，旧 CMNN 定义不同；来源映射维护算式与实现状态。

## Workflow / 流程

1. Freeze observation identity, tenant, run, plan revision, time window and enabled modes before collecting data. / 采集前冻结观测身份、租户、运行、计划版本、时间窗口和启用模式。
2. Obtain independent expected populations and authorized source records. Normalize stable IDs, exact version/digest bindings, causal disposition order and declared resource units. / 获取独立预期集合和获准记录，规范稳定编号、精确版本摘要绑定、因果处置顺序及资源单位。
3. Have the host authenticate the entire frozen observation. Its verifier must return the boolean `True`, and must not trust self-declared completeness or actor strings. The callback receives a defensive copy. / 由宿主认证完整冻结观测，核验器必须返回布尔 `True`，不得信任自报完整性或参与者字符串；回调收到防御性副本。
4. Compute selected CSM metrics, retain provenance and missing-data states, and deliver only observation output. / 计算所选 CSM 指标，保留来源与缺失状态，只交付观测输出。

## Envelope and Datasets / 信封与数据集

Required envelope fields / 必填信封字段:

```json
{
  "local_profile_version": "3.0.0",
  "source_contract_version": "2.0.0",
  "observation_id": "observation-1",
  "tenant_id": "tenant-1",
  "run_id": "run-1",
  "plan_revision": 1,
  "window_start": "2026-09-09T03:00:00Z",
  "cutoff": "2026-09-09T03:10:00Z",
  "modes": [],
  "datasets": {
    "coverage": {
      "complete": true,
      "source_refs": ["fixture://frozen-plan-and-acceptance"],
      "rows": [
        {"id": "unit-1", "weight": 1, "required": true, "exclusive": true, "accepted": true},
        {"id": "unit-2", "weight": 3, "required": true, "exclusive": true, "accepted": false}
      ]
    }
  }
}
```

This synthetic example supports CSM08 = 0.25. CSM01 cannot be computed without `assignments`; missing that dataset does not invalidate CSM08. No verifier is supplied in this example because source authority must come from the adopting host. / 本合成示例支持 CSM08 = 0.25；缺少 `assignments` 时 CSM01 不可计算，但不影响 CSM08。示例不提供核验器，来源权威必须由宿主建立。

Every dataset requires `complete`, a nonempty `source_refs` list and `rows`. Every row has a nonempty stable `id`. Identical redelivery collapses; the same ID with different content invalidates dependent metrics. A complete empty dataset means the population is known to be empty; an absent/incomplete dataset means missing knowledge. The host must attest that rows belong to the declared scope and cutoff. / 每个数据集须有完整性标记、非空来源列表和行列表，每行有稳定非空 ID。相同重投折叠，同 ID 异内容使依赖指标不可用。完整空集表示已知集合为空，缺失或不完整数据集表示知识不足。宿主须证明数据属于声明范围及截点。

Bindings below denote authenticated identity + revision + digest, plus location for citation lineage. The calculator compares normalized bindings; the adapter must establish their truth and cannot use display labels as evidence. / 下列绑定指经认证的标识、修订、摘要，引用血缘还含定位。计算器只比较规范绑定；真实性由适配器建立，显示标签不能充当证据。

| Dataset / 数据集 | Used by / 指标 | Required row fields beyond `id` / 除 ID 外所需字段 | Semantics / 语义 |
| --- | --- | --- | --- |
| `coverage` | CSM01, 02, 08 | `weight`, `required`, `exclusive`, `accepted` as used by the chosen metric / 按所选指标使用 | Frozen required units; positive weights; accepted means current-version business verification. / 冻结必选单元，权重为正；通过表示当前版本已业务核验。 |
| `assignments` | CSM01, 02 | `unit_id`, `task_id`, `role`, `active` | Valid primary relations; predeclared review uses role `review` and does not inflate primary coverage. / 有效主责关系；预声明复核用 review，不抬高主责覆盖。 |
| `local_dispositions` | CSM07 | `task_id`, `disposition_order`, `decision` | Authoritative integer causal order; passed, returned, rejected, needs_evidence, pending. First completed disposition is immutable for this metric. / 权威整数因果序；首次已处置结果不被后续通过覆盖。 |
| `closed_runs` | CSM09 | `state`, `closed_at`, `global_accepted`, `delivered` for completed state / 完成状态须有两项证明 | Closed window includes all failure/partial terminal states. `closed_at: null` is open, reported separately. / 已终结窗口保留失败和部分终态；空关闭时间表示在途，单列。 |
| `attempts` | CSM13 | `task_id`, `domain`, `started` | `id` identifies the logical attempt; business attempts include failures; probe attempts excluded. / ID 标识逻辑尝试，业务失败也计入，探针尝试排除。 |
| `record_obligations`, `received_records` | CSM18 | stable expected/received `id` / 稳定预期和接收 ID | Obligations independent of received logs; `watermark_closed: true` on obligations proves the producer cutoff is closed. / 义务独立于接收日志，义务集须证明生产者截点已关闭。 |
| `costs` | CSM19 | `domain`, `unit`, `value` | Full business/probe cost ledger, one unit per call, nonnegative finite values. / 完整业务与探针成本，每次同一单位，数值有限非负。 |
| `isolation` | CSM23 | `required`, `check_type`, `verified` | `configuration` and `execution` checks stay separate; declaration alone is not execution proof. / 配置和执行核验分组，声明不等于执行证明。 |
| `citations` | CSM24 | `origin_binding` | One row per verified citation entry; normalize original record/version/location, not domain or model identity. / 每条已核验引用一行，按原始记录、版本、定位归一，不按域名或模型。 |
| `conflicts` | CSM12 | `confirmed`, `raised_at`, `resolved_at` | Complete ledger yields exact unresolved count; partial ledger yields a confirmed lower bound only. / 完整账本给精确未结数，部分账本只给已确认下界。 |
| `objections` | CSM25, 26 | conflict fields plus `blocking`, `artifact_binding` / 冲突字段加阻塞与工件绑定 | Valid version-bound adjudication defines `resolved_at`; preserve historical resolution time. / 有效版本裁决决定解除时刻，保留历史时间。 |
| `releases` | CSM26 | `artifact_binding`, `released_at` | Count unique artifact revisions that were blocked at release time; later resolution cannot erase violations. / 按放行时状态统计唯一工件版本，后续解除不抹掉违规。 |
| `handoffs` | CSM27 | `disposition`, `artifact_binding`, `acceptance_binding` | accepted/rejected/expired/version_conflict are disposed; pending reported separately. Match both revision and digest. / 已处置含拒收、过期、冲突；待定单列，同时匹配版本摘要。 |
| `timing` | CSM28, 32 | `started_at`, `accepted_at`; CSM28 `endpoint`, optional `delivered_at`; CSM32 `branches` / 按指标提供终点或分支 | Exactly one run. Endpoint global_acceptance/delivery is predeclared. Each branch has id, required, used_in_final, ready_at. / 每次一个运行，预声明验收或交付终点；分支含 ID、必需、最终采纳和就绪时间。 |
| `cohort` | CSM29–31, 34 | `input_binding`, `criteria_binding` | Frozen pre-enrolled task IDs for both arms; never derive from successful runs. / 两组共同冻结入组集合，不从成功运行推导。 |
| `comparison_runs` | CSM29–31, 34 | `task_id`, `arm`, cohort bindings, `state`, `global_accepted`, `delivered` for completed runs / 完成者须有证明 | Exactly one baseline and collaboration summary per enrolled task, retaining all attempt costs and final state. / 每项各一条基线和协作汇总，保留所有尝试成本与最终状态。 |

Time datasets require host-attested `comparable_clock: true`. Timestamps include a timezone. Rows used as historic facts retain original times; absence of an endpoint reports current age, not completed duration. CSM32 always ends at global acceptance and uses only required branches used in the final artifact. / 时间数据集须由宿主证明时钟可比，时间戳带时区。历史事实保留原时刻；缺结束点报告年龄，不冒充完成耗时。CSM32 固定以全局验收为终点，仅用必要且最终采纳分支。

Comparison envelope `comparison` declares `statistic: mean|median`, `duration_endpoint: global_acceptance|delivery`, `resource_unit` and `quality_unit: score_points|ratio`. CSM29 requires the declared endpoint, positive `duration_seconds` and comparable clocks; CSM30 requires `resource_value`, matching `resource_unit` and `costs_complete: true` for every run; CSM31 requires `quality_score`, matching `quality_unit` and `quality_verified: true` for every run. Quality ratios lie in [0,1]; their differences use percentage points. Unavailable quality/cost does not invalidate independently supported CSM34. / 比较信封声明均值或中位数、验收或交付结束点、资源单位和质量单位。提速要求预声明终点、正时长及可比时钟；资源比要求所有运行完整同单位成本；质量差要求所有运行可信同单位评分。质量比例限 [0,1]，差值用百分点。缺质量或成本不影响独立有据的 CSM34。

## Constraints and Output / 约束与输出

Supported run states are completed, partial, failed, timed_out, not_started, running, blocked, rejected and terminated. Only completed plus verified global acceptance and required actual delivery counts as whole completion. The host must map lifecycle semantics honestly and retain unfinished tasks in the comparison cohort. / 支持完成、部分、失败、超时、未开始、运行、阻塞、拒绝、终止；仅完成且有全局验收和目标要求的实际交付证明才计整体完成。宿主须准确映射生命周期，并在比较队列保留未完成任务。

Each metric has `value`, four-state `state`, `unit`, numerator/denominator where applicable, `sample_count`, `reason`, `source_id`, `rule_version`, `evidence_refs`, dataset dependencies, completeness, scope and deduplication rule. Partial counts expose `confirmed_lower_bound`; open durations expose `age_seconds`, with `value: null`. Disabled review/parallel modes are not applicable; unsupported formulas are not computable. / 每项输出值、四态、单位、适用分子分母、样本数、原因、来源编号、规则版本、证据、依赖数据集、完整性、范围和去重规则。部分计数给已确认下界，未结束时长给年龄，值保留 null；模式未启用为不适用，未实现算式为不可计算。

Do not turn CSM24 source repetition into CSM33 wasted cost, infer independence from model count, sum parallel branch time as wall time, fabricate missing baseline scores, or treat a computed metric as business acceptance. Live adapters, clock synchronization and durable authority are outside this reference calculator. / 不把同源引用折算为浪费成本，不按模型数量断言独立性，不把并行时长相加冒充墙钟时间，不伪造基线评分，不将指标计算当业务验收。真实适配器、时钟同步和持久权威在参考计算器之外。
