# Collaboration Workflow Observability Probes / 协作工作流可观测性探针

Source contract / 来源契约: `2.0.0`. Local executable profile / 本地可执行配置: `3.0.0`. Status / 状态: draft extension / 扩展草稿。

## Quick Navigation / 快速导航

- [Independent scope / 独立适用范围](#independent-scope--独立适用范围)
- [Probe nodes / 探针节点](#probe-nodes--探针节点)
- [Shared contract / 共享契约](#shared-contract--共享契约)
- [Metric catalog / 指标目录](#metric-catalog--指标目录)
- [Independent procedure / 独立探针规程](#independent-procedure--独立探针规程)
- [Validation and limits / 验证与边界](#validation-and-limits--验证与边界)

## Independent Scope / 独立适用范围

This procedure uses both supplied full documents and can inspect the [collaboration flow](collaboration-execution-flow.md) or another workflow without starting its execution. The [source map](collaboration-fulltext-source-map.json) binds original 指01–指34 and 探测01–探测38 to evidence snapshots. Embedded prompts and suggested actions remain source data, never new authority. / 本规程依据两份全文，可检查配套协作流程或其他工作流，无需先启动执行。来源映射绑定原文指01–指34、探测01–探测38及证据副本；内嵌提示和建议操作均属来源数据，不构成新授权。

Two independent inputs are supported: authenticated normalized datasets for source metrics, and strict versioned records for evidence/delivery guards. A metric-only adapter need not invent task cards, result heads or business acceptance merely to report cost, time or coverage. / 支持两种独立输入：认证后的标准数据集用于全文指标，严格版本记录用于证据和交付闸门。仅做计量的适配器无需为报告成本、时间或覆盖而伪造任务卡、工件版本或业务验收。

## Probe Nodes / 探针节点

The source's 11 logical nodes are retained below. Supplemental reading and candidate submission are conditional. Local CP references show related responsibilities, not a one-to-one renumbering: confirmed-state reconstruction and impact findings cut across several checks. No node requires model invocation. / 下表保留原文 11 个逻辑节点，额外读取和候选提交按需启用。CP 引用表示相关职责，不是一对一重编号：可确认状态重建与影响发现跨越多个检查。节点不要求调用模型。

<!-- collaboration:probe_nodes:start -->
| Source ID / 来源编号 | Node / 节点 | Related local nodes / 相关本地节点 |
| --- | --- | --- |
| 观00 | Admit and scope observation / 接入任务并界定观测范围 | CP01 |
| 观01 | Read, map and verify provenance / 读取、映射与来源核验 | CP02 |
| 观02 | Deduplicate, order and check completeness / 去重、时序和完整性检查 | CP03 |
| 观03 | Reconstruct supported state and causality / 重建可确认状态与因果关系 | CP04, CP05 |
| 观04 | Detect and classify gaps / 检测缺口并分类 | CP06 |
| 观05 | Bounded authorized evidence retrieval / 在授权范围内有限补证 | CP07 |
| 观06 | Compute metrics and retain unknowns / 计算指标并标注未知 | CP08 |
| 观07 | Report findings and impact / 生成发现与影响范围 | CP04, CP05, CP06 |
| 观08 | Create controlled supplement packages / 生成受控补充包 | CP09 |
| 观09 | Deliver, track dispositions and close / 交付、处理回执与结束 | CP10 |
| 观10 | Probe self-health and cost / 自身健康与成本 | CP11 |
<!-- collaboration:probe_nodes:end -->

## Shared Contract / 共享契约

This complete local projection is generated from the same Schema as the execution procedure. Source 2.0.0 and executable profile 3.0.0 are recorded separately. / 本完整本地投影与执行规程由同一 Schema 生成，来源 2.0.0 与执行配置 3.0.0 分开记录。

<!-- collaboration:contract:start -->
Source contract / 来源契约: `2.0.0`; local executable profile / 本地可执行配置: `3.0.0`. Normative local shape / 本地规范结构: [collaboration-record.schema.json](../schemas/collaboration-record.schema.json).

Intent follows messages; truth follows references; results follow artifacts; responsibility follows acceptance. Both supplied documents embed the same source contract. The schema below is a stricter local projection, not a verbatim or wire-compatible implementation. / 意图随消息、真值随引用、结果随工件、责任随验收。两份附件内置相同的来源契约。以下 Schema 是更严格的本地投影，不是逐字复制或线格式兼容实现。

Every listed field is required unless its type explicitly permits null; nested objects reject undeclared fields except public content and declared maps. Empty lists mean none, not unknown. / 下列字段均必填，只有类型明确允许时可为 null；嵌套对象拒绝未声明字段，公开 content 与声明的映射除外。空列表表示没有，不表示未知。

| Record / 记录 | Field / 字段 | Type and constraints / 类型与约束 |
| --- | --- | --- |
| Envelope / 信封 | `protocol_version` | "3.0.0" |
| Envelope / 信封 | `kind` | "task_card" / "result_artifact" / "acceptance_receipt" / "objection" / "adjudication" / "evidence" / "gap" / "supplement_candidate" / "supplement_receipt" / "snapshot" / "delivery_receipt" / "responsibility_transfer" / "observation_repair_receipt" |
| Envelope / 信封 | `id` | string; minLength=1; pattern=\S |
| Envelope / 信封 | `revision` | integer; minimum=1 |
| Envelope / 信封 | `run_id` | string; minLength=1; pattern=\S |
| Envelope / 信封 | `scope` | string; minLength=1; pattern=\S |
| Envelope / 信封 | `actor` | string; minLength=1; pattern=\S |
| Envelope / 信封 | `payload` | object |
| Envelope / 信封 | `record_hash` | string; pattern=^sha256:[a-f0-9]{64}$ |
| Envelope / 信封 | `source_contract_version` | "2.0.0" |
| Envelope / 信封 | `tenant_id` | string; minLength=1; pattern=\S |
| Envelope / 信封 | `request_id` | string; minLength=1; pattern=\S |
| Envelope / 信封 | `plan_revision` | integer; minimum=1 |
| Exact revision binding / 精确修订绑定 (`binding`) | `id` | string; minLength=1; pattern=\S |
| Exact revision binding / 精确修订绑定 (`binding`) | `revision` | integer; minimum=1 |
| Exact revision binding / 精确修订绑定 (`binding`) | `hash` | string; pattern=^sha256:[a-f0-9]{64}$ |
| Task card / 任务卡 (`task_card`) | `goal` | string; minLength=1; pattern=\S |
| Task card / 任务卡 (`task_card`) | `criteria` | array<object>; minItems=1; uniqueItems=True |
| Task card / 任务卡 (`task_card`) | `criteria[].id` | string; minLength=1; pattern=\S |
| Task card / 任务卡 (`task_card`) | `criteria[].required` | boolean |
| Task card / 任务卡 (`task_card`) | `criteria[].description` | string; minLength=1; pattern=\S |
| Task card / 任务卡 (`task_card`) | `owner` | string; minLength=1; pattern=\S |
| Task card / 任务卡 (`task_card`) | `acceptor` | string; minLength=1; pattern=\S |
| Task card / 任务卡 (`task_card`) | `reviewer` | string; minLength=1; pattern=\S or null |
| Task card / 任务卡 (`task_card`) | `arbiter` | string; minLength=1; pattern=\S or null |
| Task card / 任务卡 (`task_card`) | `handoff_to` | string; minLength=1; pattern=\S or null |
| Task card / 任务卡 (`task_card`) | `modes` | array<"hierarchical_delegation" / "fan_out_gather" / "adversarial_review" / "handoff_chain">; minItems=1; uniqueItems=True |
| Task card / 任务卡 (`task_card`) | `input_bindings` | array<binding>; minItems=0; uniqueItems=True |
| Task card / 任务卡 (`task_card`) | `allowed_scope` | array<string; minLength=1; pattern=\S>; minItems=1; uniqueItems=True |
| Task card / 任务卡 (`task_card`) | `forbidden_scope` | array<string; minLength=1; pattern=\S>; minItems=0; uniqueItems=True |
| Task card / 任务卡 (`task_card`) | `isolation` | object |
| Task card / 任务卡 (`task_card`) | `isolation.namespace` | string; minLength=1; pattern=\S |
| Task card / 任务卡 (`task_card`) | `isolation.write_resources` | array<string; minLength=1; pattern=\S>; minItems=0; uniqueItems=True |
| Task card / 任务卡 (`task_card`) | `isolation.merge_owner` | string; minLength=1; pattern=\S |
| Task card / 任务卡 (`task_card`) | `budget` | object |
| Task card / 任务卡 (`task_card`) | `budget.max_attempts` | integer; minimum=1 |
| Task card / 任务卡 (`task_card`) | `budget.timeout_seconds` | integer; minimum=1 |
| Task card / 任务卡 (`task_card`) | `tool_policy` | binding |
| Task card / 任务卡 (`task_card`) | `goal_binding` | binding |
| Task card / 任务卡 (`task_card`) | `rule_binding` | binding |
| Task card / 任务卡 (`task_card`) | `separation_required` | boolean |
| Task card / 任务卡 (`task_card`) | `coverage_units` | array<string; minLength=1; pattern=\S>; minItems=1; uniqueItems=True |
| Task card / 任务卡 (`task_card`) | `deadline_at` | string; format=date-time |
| Task card / 任务卡 (`task_card`) | `delivery_scope` | string; minLength=1; pattern=\S |
| Task card / 任务卡 (`task_card`) | `final_receiver` | string; minLength=1; pattern=\S |
| Result artifact / 结果工件 (`result_artifact`) | `task` | binding |
| Result artifact / 结果工件 (`result_artifact`) | `outcome` | "complete" / "partial" / "failed" / "unknown" |
| Result artifact / 结果工件 (`result_artifact`) | `content` | object |
| Result artifact / 结果工件 (`result_artifact`) | `content_digest` | string; pattern=^sha256:[a-f0-9]{64}$ |
| Result artifact / 结果工件 (`result_artifact`) | `evidence` | array<binding>; minItems=0; uniqueItems=True |
| Result artifact / 结果工件 (`result_artifact`) | `attempt_id` | string; minLength=1; pattern=\S |
| Result artifact / 结果工件 (`result_artifact`) | `delegation_epoch` | integer; minimum=1 |
| Result artifact / 结果工件 (`result_artifact`) | `input_snapshot` | binding |
| Result artifact / 结果工件 (`result_artifact`) | `submitted_at` | string; format=date-time |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `task` | binding |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `target` | binding |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `stage` | "arrival" / "local" / "global" / "review" / "handoff" |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `verdict` | "received" / "accepted" / "rejected" / "unknown" |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `criteria_results` | object<key, "passed" / "failed" / "unknown"> |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `evidence` | array<binding>; minItems=0; uniqueItems=True |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `next_owner` | string; minLength=1; pattern=\S or null |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `supplement` | binding or null |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `rule_binding` | binding |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `accepted_at` | string; format=date-time |
| Acceptance receipt / 验收回执 (`acceptance_receipt`) | `access_verified` | boolean |
| Objection / 异议单 (`objection`) | `task` | binding |
| Objection / 异议单 (`objection`) | `target` | binding |
| Objection / 异议单 (`objection`) | `severity` | "blocking" / "advisory" |
| Objection / 异议单 (`objection`) | `finding` | string; minLength=1; pattern=\S |
| Objection / 异议单 (`objection`) | `evidence` | array<binding>; minItems=1; uniqueItems=True |
| Objection / 异议单 (`objection`) | `raised_at` | string; format=date-time |
| Adjudication / 裁决回执 (`adjudication`) | `objection` | binding |
| Adjudication / 裁决回执 (`adjudication`) | `target` | binding |
| Adjudication / 裁决回执 (`adjudication`) | `decision` | "uphold" / "dismiss" |
| Adjudication / 裁决回执 (`adjudication`) | `rationale` | string; minLength=1; pattern=\S |
| Adjudication / 裁决回执 (`adjudication`) | `evidence` | array<binding>; minItems=1; uniqueItems=True |
| Adjudication / 裁决回执 (`adjudication`) | `decided_at` | string; format=date-time |
| Source evidence / 来源证据 (`evidence`) | `target` | binding |
| Source evidence / 来源证据 (`evidence`) | `source_id` | string; minLength=1; pattern=\S |
| Source evidence / 来源证据 (`evidence`) | `claim_id` | string; minLength=1; pattern=\S |
| Source evidence / 来源证据 (`evidence`) | `evidence_type` | "execution_record" / "approval" / "adjudication" / "current_state" |
| Source evidence / 来源证据 (`evidence`) | `source_ref` | string; minLength=1; pattern=\S |
| Source evidence / 来源证据 (`evidence`) | `observed_at` | string; format=date-time |
| Source evidence / 来源证据 (`evidence`) | `attempt_id` | string; minLength=1; pattern=\S |
| Source evidence / 来源证据 (`evidence`) | `input_snapshot` | binding |
| Source evidence / 来源证据 (`evidence`) | `fact_time` | string; format=date-time |
| Source evidence / 来源证据 (`evidence`) | `read_time` | string; format=date-time |
| Source evidence / 来源证据 (`evidence`) | `record_grade` | "original" / "derived" / "candidate" / "unknown" |
| Gap request / 缺口单 (`gap`) | `target` | binding |
| Gap request / 缺口单 (`gap`) | `gap_type` | "observation_record" / "business_evidence" / "business_incomplete" / "authorization" / "unclassified" |
| Gap request / 缺口单 (`gap`) | `required_claims` | array<string; pattern=^.+:(execution_record&#124;approval&#124;adjudication&#124;current_state)$>; minItems=1; uniqueItems=True |
| Gap request / 缺口单 (`gap`) | `allowed_sources` | array<string; minLength=1; pattern=\S>; minItems=1; uniqueItems=True |
| Gap request / 缺口单 (`gap`) | `reason` | string; minLength=1; pattern=\S |
| Gap request / 缺口单 (`gap`) | `attempt_id` | string; minLength=1; pattern=\S |
| Gap request / 缺口单 (`gap`) | `input_snapshot` | binding |
| Gap request / 缺口单 (`gap`) | `active_read_authorized` | boolean |
| Gap request / 缺口单 (`gap`) | `authorization_binding` | binding |
| Gap request / 缺口单 (`gap`) | `allowed_paths` | array<string; pattern=^/(observation_supplements&#124;verification_candidates&#124;evidence_candidates)/[^~]+$>; minItems=1; uniqueItems=True |
| Gap request / 缺口单 (`gap`) | `deadline_at` | string; format=date-time |
| Gap request / 缺口单 (`gap`) | `max_reads` | integer; minimum=0 |
| Gap request / 缺口单 (`gap`) | `max_rounds` | integer; minimum=0 |
| Gap request / 缺口单 (`gap`) | `receiver` | string; minLength=1; pattern=\S |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `gap` | binding |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `target` | binding |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `acquisition` | "offline" / "archive_read" / "current_state" |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `evidence` | array<binding>; minItems=1; uniqueItems=True |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `observation_run_id` | string; minLength=1; pattern=\S |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `idempotency_key` | string; minLength=1; pattern=\S |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `candidate_path` | string; minLength=1; pattern=\S |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `generated_at` | string; format=date-time |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `expires_at` | string; format=date-time |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `reads_used` | integer; minimum=0 |
| Supplement candidate / 补充候选 (`supplement_candidate`) | `rounds_used` | integer; minimum=1 |
| Supplement disposition / 补充处理回执 (`supplement_receipt`) | `candidate` | binding |
| Supplement disposition / 补充处理回执 (`supplement_receipt`) | `target` | binding |
| Supplement disposition / 补充处理回执 (`supplement_receipt`) | `decision` | "pending" / "adopted" / "rejected" / "expired" / "version_conflict" / "human_required" |
| Supplement disposition / 补充处理回执 (`supplement_receipt`) | `reason` | string; minLength=1; pattern=\S |
| Supplement disposition / 补充处理回执 (`supplement_receipt`) | `recheck` | binding or null |
| Supplement disposition / 补充处理回执 (`supplement_receipt`) | `disposed_at` | string; format=date-time |
| Supplement disposition / 补充处理回执 (`supplement_receipt`) | `business_state_changed` | false |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `source_id` | string; minLength=1; pattern=\S |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `completeness` | "complete" / "partial" / "unknown" |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `expected_tasks` | array<binding>; minItems=0; uniqueItems=True |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `result_heads` | object<key, binding> |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `record_bindings` | array<binding>; minItems=0; uniqueItems=True |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `observed_at` | string; format=date-time |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `active_assignments` | object<key, object> |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `gap_usage` | object<key, object> |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `business_completeness` | "complete" / "partial" / "unknown" |
| Authoritative adapted snapshot / 权威适配快照 (`snapshot`) | `business_required_bindings` | array<binding>; uniqueItems=True |
| Actual delivery receipt / 实际交付回执 (`delivery_receipt`) | `task` | binding |
| Actual delivery receipt / 实际交付回执 (`delivery_receipt`) | `target` | binding |
| Actual delivery receipt / 实际交付回执 (`delivery_receipt`) | `global_acceptance` | binding |
| Actual delivery receipt / 实际交付回执 (`delivery_receipt`) | `delivery_scope` | string; minLength=1; pattern=\S |
| Actual delivery receipt / 实际交付回执 (`delivery_receipt`) | `delivered_to` | string; minLength=1; pattern=\S |
| Actual delivery receipt / 实际交付回执 (`delivery_receipt`) | `delivered_at` | string; format=date-time |
| Actual delivery receipt / 实际交付回执 (`delivery_receipt`) | `outcome` | "confirmed" / "failed" / "unknown" |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `task` | binding |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `target` | binding |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `handoff_acceptance` | binding |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `from_owner` | string; minLength=1; pattern=\S |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `to_owner` | string; minLength=1; pattern=\S |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `responsibility_scope` | string; minLength=1; pattern=\S |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `previous_epoch` | integer; minimum=1 |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `next_epoch` | integer; minimum=1 |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `expected_ledger_revision` | integer; minimum=0 |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `committed_ledger_revision` | integer; minimum=1 |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `commit_ref` | string; minLength=1; pattern=\S |
| Atomic responsibility transfer attestation / 原子责任转移证明 (`responsibility_transfer`) | `committed_at` | string; format=date-time |
| Observation view repair receipt / 观测视图修复回执 (`observation_repair_receipt`) | `candidate` | binding |
| Observation view repair receipt / 观测视图修复回执 (`observation_repair_receipt`) | `target` | binding |
| Observation view repair receipt / 观测视图修复回执 (`observation_repair_receipt`) | `view_ref` | string; minLength=1; pattern=\S |
| Observation view repair receipt / 观测视图修复回执 (`observation_repair_receipt`) | `repaired_at` | string; format=date-time |

`record_hash` hashes UTF-8 canonical JSON with sorted keys, compact separators and finite numbers, excluding only itself. `content_digest` separately hashes public `content`. Bindings compare id, revision and digest within one tenant, request, run, scope and plan revision. Active attempts also bind worker, delegation epoch and input snapshot. / `record_hash` 对按键排序、紧凑分隔且仅含有限数的 UTF-8 规范 JSON 计算哈希，仅排除自身；`content_digest` 独立哈希公开内容。绑定须核对标识、修订、摘要及租户、请求、运行、范围、计划版本；有效尝试还须绑定执行者、委派代次与输入快照。

A host verifier must authenticate record actors, source provenance and the current authoritative inventory. An always-true verifier is suitable only for a controlled test fixture. Hashes and self-declared roles cannot establish authority. / 宿主核验器必须验证记录参与者身份、来源与当前权威清单；恒真的核验器仅适用于受控测试夹具。哈希和自报角色不能建立权限。

Use one stable receipt ID per task, result and stage; a higher revision supersedes the same receipt ID. Conflicting active receipts or adjudications block release. The snapshot fixes current task and result heads and must list the complete applicable evidence and objection inventory. / 每个任务、工件与验收阶段使用一个稳定回执 ID；同 ID 的更高修订取代旧修订。冲突的当前回执或裁决阻断放行。快照固定当前任务与工件版本，并必须列出适用证据与异议的完整清单。

Arrival, local acceptance, global acceptance, actual delivery and responsibility transfer are distinct facts. `acceptance_ready` indicates configured acceptance gates pass; `allowed` additionally requires the matching actual delivery receipt. Handoff checks an authenticated atomic transfer attestation; the host performs and persists the conditional owner/epoch update. / 材料到达、局部验收、全局验收、实际交付和责任转移分别记录。`acceptance_ready` 表示已配置验收闸门通过；`allowed` 还要求匹配的实际交付凭据。交接核验经认证的原子转移回执，宿主负责执行并持久化有条件的负责人和代次更新。

Gap routing / 缺口路由: `business_incomplete` returns to execution; `business_evidence` adoption needs a candidate-consuming business recheck; `observation_record` adoption needs an observation repair receipt; `authorization` requires the authority workflow; `unclassified` cannot be auto-repaired. / 业务未完成回执行侧；业务证据采纳须消费候选的业务复验；观测记录采纳须观测修复回执；权限缺口交授权流程；未分类缺口不能自动修复。探针不改变业务成功状态。

Supplement intake verifies current target, attempt, input, source, field allowlist, authorization, explicit host time and bounded cumulative reads/rounds. `gap_usage` is the host-attested usage immediately before this package. Historical adoption is checked at its recorded disposition time; expiry later does not erase valid history. The host owns idempotent persistence and concurrency control. / 补证接入核验当前目标、尝试、输入、来源、字段白名单、授权、显式宿主时间及累计读取和轮次预算。`gap_usage` 是宿主证明的本包接入前用量。历史采纳按其处置时刻检查，后续过期不抹掉有效历史；幂等持久化和并发控制由宿主负责。

Role separation follows declared policy; low-risk owner/acceptor sharing is permitted only when separation is not required. Adversarial proposer, reviewer and arbiter remain distinct responsibility subjects, without requiring different model vendors. Business obligations are separate from optional telemetry. Missing optional observation cannot invalidate independently supported business checks. / 角色分离服从声明策略，低风险主责和验收仅在不要求分离时可兼任；对抗提案、评审、裁决仍为独立责任主体，不强制不同模型厂商。业务义务与可选观测分开；缺少额外观测不能取消独立具备依据的业务校验。

Migration must map source fields explicitly and obtain missing authoritative bindings. Changing a version label or synthesizing identity, attempt, digest, approval or success fields is not migration. Local 2.0.0 records are rejected by profile 3.0.0. / 迁移必须显式映射来源字段并补齐权威绑定；改版本号或伪造身份、尝试、摘要、审批、成功字段不构成迁移。本地旧 2.0.0 记录不能直接通过 3.0.0 配置。
<!-- collaboration:contract:end -->

## Metric Catalog / 指标目录

CSM01–CSM34 preserve the exact meanings of source 指01–指34. Twenty metrics have reference calculations in [collaboration_observability.py](../runtime/collaboration_observability.py); fourteen return `not_computable / measurement_adapter_required`. The [adapter contract](collaboration-observation-adapter.md) specifies required populations, fields and host attestations. / CSM01–CSM34 保留原文指01–指34的含义；20 项有参考计算，其余 14 项明确返回待适配且不可计算。适配契约规定预期集合、字段和宿主证明要求。

The earlier CM01–CM34 definitions remain deprecated local diagnostics in the module catalog. `inspect_workflow()` retains their meanings for compatibility; CM IDs must never be presented as source 指 IDs, and its six calculations do not add to the source implementation count. / 旧 CM01–CM34 在模块目录中保留为弃用本地诊断，旧接口保留原意供兼容；不能把 CM 编号当作原文指标，其六项计算不计入全文实现数量。

Use four states: `computable` for supported values; `not_applicable` for a known empty denominator or disabled mode; `not_computable` for missing, conflicting or incomparable prerequisites; `partial_observation` for supported lower bounds or unfinished age. Unknown is not zero. Missing inputs invalidate only dependent metrics. / 使用四态：有充分依据为可计算；已知空分母或模式未启用为不适用；缺少、冲突或不可比前提为不可计算；可确认下界或未结束年龄为部分观测。未知不等于零，缺输入只影响依赖指标。

All outputs retain source ID, rule version, scope/cutoff, unit, numerator/denominator where relevant, sample count, deduplication rule, source references and incompleteness reason. Dataset completeness is a host-attested fact, not inferred from logs received. Keep configuration proof separate from execution proof, source repetition separate from wasted work, and whole-cohort completion separate from the closed-run rate. / 输出保留来源编号、规则版本、范围与截点、单位、适用的分子分母、样本数、去重规则、来源及缺失原因。完整性由宿主证明，不能从收到的日志反推。配置证明与执行证明、同源引用与浪费成本、全入组完成差与关闭队列完成率分别处理。

<!-- collaboration:metrics:start -->
| ID / 来源 | Metric / 指标 | Formula / 口径 | Unit / 单位 | Support / 支持 | Source boundary / 原文边界 |
| --- | --- | --- | --- | --- | --- |
| CSM01 / 指01 | Goal allocation coverage / 目标分配覆盖率 | Assigned required-unit weights / all required-unit weights / 已有有效主责分配的必选单元权重和 ÷ 全部必选单元权重和 | ratio | Reference / 参考计算 | 只看是否分到人，不证明完成；重复分配不能提高覆盖 |
| CSM02 / 指02 | Unexpected duplicate allocation / 非预期重复分配率 | Sum of extra primary assignments on exclusive units / all exclusive primary assignment relations / 每个排他单元“有效主责任务卡数减一、最低为零”的总和 ÷ 排他单元主责分配总数 | ratio | Reference / 参考计算 | 预先声明的独立复核不计入；语义相似但未确认的不算确定重复 |
| CSM03 / 指03 | Intent contract transmission completeness / 意图契约传递完整率 | Matching received intent contracts / acknowledged task cards / 接收时目标版本、范围、排除项、输入和输出约定均匹配的任务卡数 ÷ 已签收任务卡数 | ratio | Adapter required / 待适配 | 证明契约传递完整，不证明执行者真正理解全部语义 |
| CSM04 / 指04 | Responsibility chain completeness / 责任链完整率 | Linked terminal responsibility paths / terminated task cards / 主责分配、执行签收、结果接收及最终处置均有有效关联的已终结任务卡数 ÷ 全部已终结任务卡数 | ratio | Adapter required / 待适配 | 失败但责任清楚也可完整；完整不等于结果通过 |
| CSM05 / 指05 | Fact version compliance / 事实版本合规率 | Compliant fact uses / independently expected fact uses / 满足任务卡声明版本或兼容规则的事实使用记录数 ÷ 应核验的事实使用记录数 | ratio | Adapter required / 待适配 | 版本合规不等于事实正确；未披露事实使用范围时不能声称全量合规 |
| CSM06 / 指06 | Artifact evidence completeness / 成果证据完整率 | Submitted units with business-verified required evidence / submitted units / 必需证据槽位均经业务核验的已提交单元数 ÷ 全部已提交单元数 | ratio | Adapter required / 待适配 | 证据存在和来源可定位不等于其支持结论，必须使用业务核验结果 |
| CSM07 / 指07 | Local first-acceptance pass rate / 局部首次验收通过率 | Task cards passed on their first disposition / task cards with a first disposition / 首次验收处置即通过的任务卡数 ÷ 已完成首次验收处置的任务卡数 | ratio | Reference / 参考计算 | 仍待验收者单列；只衡量进入首次验收的对象，不是端到端成功率 |
| CSM08 / 指08 | Accepted result coverage / 结果覆盖率 | Business-accepted required-unit weights / all required-unit weights / 已通过业务核验的必选单元权重和 ÷ 全部必选单元权重和 | ratio | Reference / 参考计算 | 同一单元只计一次；覆盖全部也不能代替跨部分整体验收 |
| CSM09 / 指09 | Closed-run whole completion rate / 整体完成率 | Fully accepted and actually delivered completed runs / all closed runs in the window / 终态为已完成且具备全局通过记录及目标要求的交付凭据的运行数 ÷ 统计窗口内全部已终结运行数 | ratio | Reference / 参考计算 | 分母含失败、拒绝、终止和部分交付；仍在执行或阻塞的运行单列 |
| CSM10 / 指10 | On-time handoff acceptance / 按时交接签收率 | Correct handoffs accepted before deadline / handoffs due by cutoff / 在规定期限内被正确接收者签收的交接数 ÷ 截至观察截点已到签收期限的应签收交接数 | ratio | Adapter required / 待适配 | 尚未到期者不进分母；业务取消须在到期前获准并单列 |
| CSM11 / 指11 | Handoff waiting duration / 交接等待时长 | Accepted time minus sent time with comparable clocks / 同一交接的有效签收时刻减可信发送时刻 | seconds | Adapter required / 待适配 | 未签收者报告当前等待年龄，不冒充已完成时长；跨源时钟不明则不报精确值 |
| CSM12 / 指12 | Unresolved conflicts / 未解决冲突数 | Unique confirmed unresolved conflict records at cutoff / 截至观察截点仍未获得有效处理决定的唯一冲突单数 | count | Reference / 参考计算 | 语义疑似冲突单列；没有完整登记范围时只报已发现数量 |
| CSM13 / 指13 | Business retry amplification / 重试放大倍数 | Distinct started business attempts / distinct task cards with a started attempt / 已开始的全部业务尝试数 ÷ 至少开始一次的唯一任务卡数 | multiple | Reference / 参考计算 | 单位为倍，不是百分比；探针读取重试不计入；全部失败的任务卡也计入 |
| CSM14 / 指14 | Due evidence-gap completion / 到期缺口补全率 | Evidence gaps validly adopted and closed before deadline / evidence gaps due by cutoff / 在截止时间前获有效采纳且关闭的证据缺口数 ÷ 截至观察截点已到期的证据缺口数 | ratio | Adapter required / 待适配 | 观测记录缺口和业务证据缺口分组；无法补全、拒读、超时都保留在对应分母 |
| CSM15 / 指15 | Disposed supplement adoption / 补充包采纳率 | Adopted supplements / disposed supplements; pending excluded and reported / 处置为已采纳的唯一补充包数 ÷ 已完成处置的唯一补充包数 | ratio | Adapter required / 待适配 | 过期、拒收、版本冲突都计入已处置；待回执单列；高采纳率不自动代表质量好 |
| CSM16 / 指16 | Evidence completion duration / 证据补全时长 | Valid adoption time minus gap registration time / 缺口登记到有效采纳回执产生的时间间隔 | seconds | Adapter required / 待适配 | 未关闭缺口单列年龄；不以生成候选的时间当补全结束 |
| CSM17 / 指17 | Correct stale-candidate rejection / 陈旧候选正确拒收率 | Correctly rejected stale candidates / all stale candidates at disposition / 处置时已过期或基准版本不匹配且被拒收的候选数 ÷ 处置时所有已过期或基准版本不匹配候选数 | ratio | Adapter required / 待适配 | 用于验证防护；没有陈旧候选时为不适用，不是百分之百 |
| CSM18 / 指18 | Required record collection completeness / 必需记录采集完整率 | Received unique required records / independently expected required records / 截点前已收到的唯一必需记录数 ÷ 独立清单要求的必需记录数 | ratio | Reference / 参考计算 | 不能以收到的记录反推预期记录；采样日志不能证明全量关键事件完整 |
| CSM19 / 指19 | Probe cost share / 探针开销占比 | Probe cost / (business cost + probe cost) in one declared unit / 同一范围内探针成本 ÷ 业务执行成本与探针成本之和 | ratio | Reference / 参考计算 | 金额、词元、读取次数分别计算，不能混加；不能把并行耗时简单相加称墙钟时间 |
| CSM20 / 指20 | Confirmed unauthorized supplement requests / 越权补写确认数 | Confirmed unauthorized logical write requests; blocked and effective separate / 已由可信接收器或审计规则证实的越权补写尝试数 | count | Adapter required / 待适配 | 按逻辑请求去重；已阻止和已生效分开；观测不全时不能把未发现称为不存在 |
| CSM21 / 指21 | Collection latency / 采集延迟 | Collected time minus occurred time under comparable clocks / 可比条件下采集时间减发生时间 | seconds | Adapter required / 待适配 | 时钟不可比时改用单接收端队列滞留等可测代理值，并改名说明 |
| CSM22 / 指22 | Probe run completion / 探针任务完成率 | Probe runs delivering promised output within bounds / ended probe runs / 在限定预算和期限内完成承诺输出的观测任务数 ÷ 已结束的观测任务数 | ratio | Adapter required / 待适配 | 必须同时报告部分输出、失败和未结束任务；探针完成不代表业务完成 |
| CSM23 / 指23 | Isolation verification coverage / 隔离核验覆盖率 | Verified required isolation obligations / required isolation obligations; group config and execution / 已有合格核验依据的隔离义务数 ÷ 当前计划要求核验的隔离义务总数 | ratio | Reference / 参考计算 | 只衡量被要求的检查是否得到证明；配置已声明不等于边界有效，更不等于绝对安全 |
| CSM24 / 指24 | Same-origin citation repetition / 同源引用重复占比 | Verified citation entries minus normalized original evidence records, divided by verified entries / 已核验引用条目数减规范化原始证据记录数，所得差值 ÷ 已核验引用条目数 | ratio | Reference / 参考计算 | 衡量同一证据被多次引用，不自动代表浪费；复核可有意重复，不能按域名或模型数量判定独立性 |
| CSM25 / 指25 | Open blocking objections / 阻塞异议未结数 | Unique blocking objections without valid resolution at cutoff / 截点前仍未获得有效解除决定的唯一阻塞异议数 | count | Reference / 参考计算 | 来源不全时只能报已确认下界；普通讨论不自动当作阻塞异议 |
| CSM26 / 指26 | Historical release past blocking objections / 越过阻塞异议放行确认数 | Unique artifact revisions released while blocking objections were still open / 放行时仍有有效阻塞异议却已被放行的唯一整体工件版本数 | count | Reference / 参考计算 | 事后补裁决不能抹掉此前越界；依赖历史状态，不按当前已解决状态回推当时安全 |
| CSM27 / 指27 | Handoff version and digest match / 交接版本摘要匹配率 | Disposed handoffs matching both accepted version and digest / disposed handoffs / 与所引用的有效验收回执同时匹配工件版本和摘要的已处置交接数 ÷ 全部已处置的唯一交接数 | ratio | Reference / 参考计算 | 仅检查对象一致性，不替代授权、可读性、下一棒责任或业务正确性 |
| CSM28 / 指28 | End-to-end wall-clock duration / 端到端墙钟时长 | Declared endpoint minus declared start in one trusted clock domain / 约定结束时刻减约定开始时刻；验收结束和交付结束分别统计 | seconds | Reference / 参考计算 | 排队、协调、评审和恢复是否计入必须预先固定；未结束报告年龄，不能把并行分支耗时相加 |
| CSM29 / 指29 | Comparable delivery speedup / 可比交付提速比 | Baseline duration statistic / collaboration statistic for common completed pairs / 双方均按同一规则完整验收的配对任务中，基线时长统计量 ÷ 协作时长同类统计量 | multiple | Reference / 参考计算 | 大于1才表示该样本条件下更快；失败、超时及未结束样本单列，不能推广为总体必然提速 |
| CSM30 / 指30 | Total resource consumption ratio / 总资源消耗比 | All collaboration resource use / all baseline resource use in the same frozen cohort and unit / 同一冻结任务组中协作方案全部资源消耗 ÷ 基线方案全部同类资源消耗 | multiple | Reference / 参考计算 | 词元、金额、读取次数、人工时间分别算，不能混加；失败耗费不可删除 |
| CSM31 / 指31 | Comparable quality difference / 可比质量差值 | Collaboration quality statistic minus baseline statistic on identical covered samples / 在相同评价规则和样本覆盖下，协作质量统计量减基线质量同类统计量 | score_points_or_percentage_points | Reference / 参考计算 | 评分差用分，比例差用百分点；模型自评不等于独立质量证明；无可信评价则不可计算 |
| CSM32 / 指32 | Post-parallel convergence share / 并行结束后收口时长占比 | Last required used branch ready to global acceptance duration / total run-to-acceptance duration / 最后一个必要且用于最终工件的分支工件就绪至整体验收结束的时长 ÷ 运行开始至整体验收结束的时长 | ratio | Reference / 参考计算 | 只测并行后的收口尾段，可能含排队、评审与等待；不是聚合器纯计算时间，也不是全部协调开销 |
| CSM33 / 指33 | Confirmed unintended duplicate-work cost / 已确认意外重复工作成本占比 | Confirmed unnecessary duplicate-work cost / all business work cost in the scope / 已由责任方确认不必要的重复尝试或可分离工作片段成本 ÷ 同范围全部业务工作成本 | ratio | Adapter required / 待适配 | 排除计划内独立评审和交叉验证；不把同源引用、同模型或内容相似直接算作浪费 |
| CSM34 / 指34 | Enrolled-cohort completion-rate difference / 同质样本整体完成率差 | Difference in completion proportions of all pre-enrolled tasks, multiplied by 100 percentage points / 两组在同一预定评估截止点的整体完成比例之差，乘100后以百分点表达 | percentage_points | Reference / 参考计算 | 每组分母为预先入组任务数，未完成和超时不从分母删除；不是指09的关闭队列口径 |
<!-- collaboration:metrics:end -->

Illustrations only: required weights 1 and 3 with only the first assigned/accepted give CSM01/08 = 25%; five started business attempts across three tasks give CSM13 = 5/3; nine received required records out of ten independent obligations give CSM18 = 90%; probe cost 5 plus business cost 100 gives CSM19 = 5/105. Last required used branch ready at 300 s and global acceptance at 420 s gives CSM32 = 120/420. / 仅作示例：必选权重 1 与 3，仅前者分配或通过，覆盖率为 25%；三任务五次业务尝试为 5/3 倍；独立要求十条记录收到九条为 90%；探针成本 5、业务成本 100 占比为 5/105；最后必需且被采纳分支在 300 秒就绪、420 秒全局验收，收口占比为 120/420。

## Independent Procedure / 独立探针规程

1. Obtain the workflow owner's permitted data and scoped observation request. Freeze tenant, run, plan revision, window and cutoff; keep original source schema, identity, version and location in adapter evidence. Missing facts must remain missing. / 获取工作流负责方提供的获准数据与观测范围，冻结租户、运行、计划版本、窗口和截点；在适配证据中保留原结构、身份、版本和定位。缺事实保持缺失。
2. Map only datasets needed by enabled metrics using the [adapter contract](collaboration-observation-adapter.md). The host authenticates scope, provenance, complete populations, causal decisions, clock comparability and costs. Same-record redelivery collapses; conflicting contents invalidate dependent measurements. / 仅映射启用指标所需数据。宿主认证范围、来源、完整集合、因果处置、时钟可比性和成本。同记录重投折叠，内容冲突使依赖计量不可用。
3. Call `calculate_source_metrics(observation, verify_observation=host_verifier, enabled_metrics=[...])`. This pure calculation requires no execution engine or network access, produces no business state change and is not an acceptance gate. / 直接调用纯计算函数，无需执行引擎或网络，不改变业务状态，也不构成验收闸门。
4. For strict record checks construct `RecordInventory(..., now=host_clock)`. Missing business evidence blocks the corresponding gate; missing optional probe records does not erase other valid checks. Do not interpret an unavailable probe as a clean bill of health. / 严格记录检查使用带显式宿主时钟的清单。业务证据缺失阻塞对应闸门；可选探针记录缺失不抹掉其他有效校验。探针不可用不代表无问题。
5. Classify a gap before acquiring more evidence. Offline review reads only supplied records. Extra archive/current-state acquisition needs explicit authority, allowed sources and paths, independent observation-run identity, a deadline and cumulative read/round budget. `validate_supplement()` checks the already acquired package; the host performs authorized reads. / 额外取证前先分类。离线检查仅用已有材料；额外归档或当前状态采集须有明确授权、来源和路径白名单、独立观测运行、期限和累计读取轮次预算。校验器只检查已取得的包，宿主执行获准读取。
6. Route business-incomplete gaps to execution and authorization gaps to the authority workflow. Business-evidence adoption needs a matching candidate-consuming business recheck; observation-record adoption needs an observation repair receipt. `validate_supplement_receipt()` checks receiver, target and disposition time. Pending, rejected, expired and conflicting states never imply gap success. / 业务未完成回执行，权限缺口回授权流程；业务证据采纳须匹配并消费候选的业务复验，观测记录采纳须观测修复回执。回执校验核对接收者、目标、处置时间。待定、拒收、过期、冲突均不代表补全成功。
7. Report the supported findings, unresolved evidence, candidate dispositions and probe health independently. Do not start business tests, create approvals/adjudications, enlarge authority, modify success status or rewrite historical release violations. / 独立报告有依据的发现、未决证据、候选处置与探针健康；不启动业务测试，不生成审批裁决，不扩权，不修改成功状态，不回写历史放行违规。

## Validation and Limits / 验证与边界

The 38 original scenarios below remain integration-pending. Listed local tests exercise only deterministic portions using authenticated synthetic fixtures and normalized datasets. Fourteen source metrics still require further adapters/calculators; all real data adapters require host integration, source authentication and operational validation. / 以下 38 项原文场景仍待集成验证。所列本地测试仅用经夹具认证的合成记录和标准数据验证确定性部分；14 项来源指标仍需补充适配与计算，所有真实数据适配器均需宿主集成、来源认证和运行验证。

<!-- collaboration:probe_cases:start -->
| Source ID / 来源编号 | Scenario / 场景 | Expected / 预期 | Reference coverage / 参考覆盖 | Integration / 集成 |
| --- | --- | --- | --- | --- |
| 探测01 | Same event is delivered three times / 同一事件投递三次 | Count once and retain redelivery diagnostics / 只计一次，保留重投统计 | Partial / 部分: `test_duplicate_assignment_counts_relations_not_repeated_logs_or_reviews` | Pending / 待验证 |
| 探测02 | Same event identity has conflicting contents / 同一事件标识出现不同内容 | Isolate conflict without arrival-order overwrite / 隔离冲突，不以后到覆盖先到 | Partial / 部分: `test_bad_inputs_only_degrade_dependent_metrics` | Pending / 待验证 |
| 探测03 | Retry has a new attempt identity / 重试使用新尝试标识 | Count a business attempt, not a redelivery / 计入真实业务尝试，不误判为重投 | Partial / 部分: `test_retry_amplification_excludes_probe_attempts_and_deduplicates` | Pending / 待验证 |
| 探测04 | Frozen coverage population is missing / 缺少冻结覆盖清单 | CSM01 and CSM08 are not computable / 指01、指08不可计算 | Partial / 部分: `test_bad_inputs_only_degrade_dependent_metrics` | Pending / 待验证 |
| 探测05 | Independent review is predeclared / 预先声明独立复核 | Exclude it from duplicate primary ownership / 不计入非预期重复主责 | Partial / 部分: `test_duplicate_assignment_counts_relations_not_repeated_logs_or_reviews` | Pending / 待验证 |
| 探测06 | First format disposition fails and next passes / 首次格式验收失败，第二次通过 | Keep first-acceptance outcome unchanged / 首次通过率不被第二次结果改写 | Partial / 部分: `test_first_rejected_disposition_is_not_replaced_by_later_pass` | Pending / 待验证 |
| 探测07 | Global result is partially delivered / 全局部分交付 | Exclude it from whole-completion numerator / 不计入整体完成率分子 | Partial / 部分: `test_closed_run_completion_keeps_failures_and_separates_open_runs` | Pending / 待验证 |
| 探测08 | Source clocks are not comparable / 跨源时间不同步 | Do not report exact cross-source duration / 不输出精确跨源耗时 | Partial / 部分: `test_incomplete_or_incomparable_timing_never_becomes_finished_duration` | Pending / 待验证 |
| 探测09 | Events arrive out of order with causal references / 事件乱序且有因果引用 | Use causality and versions rather than arrival order / 按因果和版本关联，不按到达顺序改终态 | Pending / 待覆盖 | Pending / 待验证 |
| 探测10 | Event is missing but authoritative snapshot exists / 缺事件但有权威快照 | Confirm supported state and retain the event gap / 状态可按快照确认，事件链仍标缺失 | Pending / 待覆盖 | Pending / 待验证 |
| 探测11 | Independent expected-record population is absent / 没有独立预期记录清单 | Do not compute self-confirming completeness / 不计算自证式采集完整率 | Partial / 部分: `test_independent_obligations_and_producer_cutoff_are_required` | Pending / 待验证 |
| 探测12 | Historical lookup returns only current state / 读取历史缺口时只返回当前实时状态 | Do not use current observation as historical evidence / 不把当前状态当作历史证据 | Partial / 部分: `test_probe_cannot_repair_business_or_fabricate_history` | Pending / 待验证 |
| 探测13 | Successful receipt belongs to another attempt / 找到其他尝试的成功回执 | Do not attach it to this attempt / 不补给本次尝试 | Partial / 部分: `test_other_attempt_success_evidence_cannot_repair_current_attempt` | Pending / 待验证 |
| 探测14 | Source has no receipt / 来源没有回执 | Return unavailable evidence without running business tests / 返回无法补全，不启动业务测试冒充补证 | Pending / 待覆盖 | Pending / 待验证 |
| 探测15 | Active acquisition is not authorized / 主动取证未授权 | Do not read extra sources / 不访问额外来源，输出权限边界 | Partial / 部分: `test_offline_inspection_does_not_grant_active_read_permission` | Pending / 待验证 |
| 探测16 | Supplement is sent but not adopted / 补充已发送但未被采纳 | Do not count the gap as completed / 缺口不算补全成功 | Partial / 部分: `test_adoption_requires_candidate_bound_business_recheck` | Pending / 待验证 |
| 探测17 | Candidate expires or object changes / 候选过期或对象已更新 | Reject intake or report version conflict / 接收端拒收或报告版本冲突 | Partial / 部分: `test_supplement_window_path_budget_and_observer_identity` | Pending / 待验证 |
| 探测18 | Supplement writes approval or success / 补充请求写审批结果或成功状态 | Reject and report the authority violation / 拒绝并输出越权发现 | Partial / 部分: `test_supplement_window_path_budget_and_observer_identity` | Pending / 待验证 |
| 探测19 | Different tenants share a task ID / 租户不同但任务编号相同 | Never associate, merge or disclose across tenants / 不关联、不合并、不泄露工件 | Partial / 部分: `test_shared_ids_do_not_cross_tenant_request_or_plan_boundaries` | Pending / 待验证 |
| 探测20 | Probe generates its own retries / 探针产生自身重试事件 | Exclude them from business retry amplification / 不计入业务重试放大倍数 | Partial / 部分: `test_retry_amplification_excludes_probe_attempts_and_deduplicates` | Pending / 待验证 |
| 探测21 | Gap repeats without new evidence / 无限重复缺口或无新增证据 | Stop at the bounded recovery limit / 达到终止条件，返回无法补全 | Partial / 部分: `test_supplement_budget_includes_prior_rounds` | Pending / 待验证 |
| 探测22 | All ratio populations are empty / 所有比例分母为零 | Report not applicable instead of perfect scores / 分别输出不适用，不伪造满分 | Partial / 部分: `test_empty_population_unknown_data_and_disabled_mode_are_distinct` | Pending / 待验证 |
| 探测23 | Unfinished task remains blocked / 未结束任务持续阻塞 | Report in-flight and overdue state separately / 单列在途与超期，不用已关闭成功样本掩盖 | Partial / 部分: `test_closed_run_completion_keeps_failures_and_separates_open_runs` | Pending / 待验证 |
| 探测24 | External workflow snapshot is supplied independently / 探针独立输入外部工作流快照 | Compute supported observations without execution startup / 不启动配套执行流程，完成可支持的观测输出 | Partial / 部分: `test_measurements_are_read_only_and_keep_source_rule_provenance` | Pending / 待验证 |
| 探测25 | Probe is unavailable / 探针完全不可用 | Retain business checks; no alert is not proof of no problem / 主执行保留必要校验，不能以无告警认定无问题 | Partial / 部分: `test_optional_observation_missing_does_not_cancel_business_acceptance` | Pending / 待验证 |
| 探测26 | Same version has a different digest / 相同版本号对应不同工件摘要 | CSM27 detects mismatch; do not reuse acceptance / 指27检查不匹配，不复用旧验收 | Partial / 部分: `test_handoff_rejection_stays_in_denominator_and_pending_separate` | Pending / 待验证 |
| 探测27 | Isolation configuration exists without execution proof / 隔离配置存在但无执行验证记录 | Report configuration coverage separately / 只认可配置检查，不声称实际隔离已经验证 | Partial / 部分: `test_isolation_configuration_and_execution_remain_distinct` | Pending / 待验证 |
| 探测28 | Citations resolve to the same original passage / 多份引用经追踪来自同一原始段落 | Normalize lineage without independent-evidence claims / 合并来源记录，不当作独立证据 | Partial / 部分: `test_citation_repetition_requires_original_record_lineage` | Pending / 待验证 |
| 探测29 | Artifact is released with an unresolved blocking objection / 阻塞异议未裁决却整体放行 | Record a historical CSM26 violation / 根据放行时状态产生指26确认事件 | Partial / 部分: `test_late_adjudication_cannot_erase_historical_release_violation` | Pending / 待验证 |
| 探测30 | Objection is dismissed only after release / 放行后才出现解除异议的决定 | Preserve the earlier release violation / 不抹掉此前越过阻塞异议的历史事件 | Partial / 部分: `test_late_adjudication_cannot_erase_historical_release_violation` | Pending / 待验证 |
| 探测31 | Baseline and collaboration differ in task or rules / 基线与协作采用不同任务或验收规则 | Refuse comparable speedup and quality claims / 不计算可比提速与质量提升，说明混杂差异 | Partial / 部分: `test_baseline_rejects_incomparable_or_selectively_missing_samples` | Pending / 待验证 |
| 探测32 | Three parallel branches each take ten seconds / 三个并行分支各耗时十秒 | Do not call their summed time wall-clock duration / 不把分支和三十秒当作运行墙钟时长 | Partial / 部分: `test_wall_clock_and_post_parallel_convergence_follow_distinct_endpoints` | Pending / 待验证 |
| 探测33 | Failed samples and costs are omitted / 协作只保留成功样本，丢掉失败成本 | Require full cohort and cost ledgers before overall comparison / 拒绝整体收益结论，要求完整队列和成本账本 | Partial / 部分: `test_unverified_quality_and_incomplete_costs_do_not_invalidate_completion`, `test_baseline_rejects_incomparable_or_selectively_missing_samples` | Pending / 待验证 |
| 探测34 | An enrolled task has not started or finished / 一项预先入组任务未开始或未结束 | Retain it in the CSM34 denominator and report its state / 指34分母保留该项，单列状态，不靠关闭队列筛选 | Partial / 部分: `test_enrolled_completion_does_not_drop_failure_or_unfinished_runs` | Pending / 待验证 |
| 探测35 | Current configuration is used to prove historical isolation / 当前配置用于证明过去的隔离效果 | Keep current observation time; do not invent history / 保留当前观测时间，不将其当历史证据 | Partial / 部分: `test_probe_cannot_repair_business_or_fabricate_history` | Pending / 待验证 |
| 探测36 | Old protocol only changes its version label / 旧协议缺摘要却仅修改契约版本号 | Reject migration with absent required evidence fields / 迁移校验失败；未知字段不能伪造补齐 | Partial / 部分: `test_old_contract_cannot_migrate_by_changing_version_label_only` | Pending / 待验证 |
| 探测37 | Citation repetition is converted directly into wasted cost / 同源重复被直接换算成浪费成本 | Require separable work and confirmed duplicate-cost evidence / 不计算指33，要求可分离片段与确认依据 | Partial / 部分: `test_empty_population_unknown_data_and_disabled_mode_are_distinct` | Pending / 待验证 |
| 探测38 | Adversarial review is not enabled / 对抗评审未启用 | Report review checks as not applicable / 专项检查不适用，不虚构评审通过或阻塞异议为零 | Partial / 部分: `test_empty_population_unknown_data_and_disabled_mode_are_distinct` | Pending / 待验证 |
<!-- collaboration:probe_cases:end -->
