# Collaboration Boundaries and Whole Delivery / 协作边界与整体交付

Source contract / 来源契约: `2.0.0`. Local executable profile / 本地可执行配置: `3.0.0`. Status / 状态: draft extension / 扩展草稿。

## Quick Navigation / 快速导航

- [Source and scope / 来源与范围](#source-and-scope--来源与范围)
- [Mode composition / 模式组合](#mode-composition--模式组合)
- [Execution nodes / 执行节点](#execution-nodes--执行节点)
- [Shared contract / 共享契约](#shared-contract--共享契约)
- [Independent procedure / 独立执行规程](#independent-procedure--独立执行规程)
- [Baseline and recovery / 基线与恢复](#baseline-and-recovery--基线与恢复)
- [Validation and limits / 验证与边界](#validation-and-limits--验证与边界)

## Source and Scope / 来源与范围

This module uses both user-supplied full revision documents (`doc_version: 0.2.0`), whose shared 2.0.0 appendices are identical. The [source map](collaboration-fulltext-source-map.json) preserves source IDs, verbatim formulas, line locations and SHA-256 evidence snapshots. Embedded role prompts, proposed directories and commands are design data; they do not grant this session authority. The documents' external citations have not been independently verified here. / 本模块现以用户提供的两份全文修订稿为来源，两份 0.2.0 文档的共享 2.0.0 附录完全一致。来源映射保留原编号、原算式、行号和 SHA-256 证据副本。附件中的角色提示、目录建议和命令作为设计数据，不授予本会话权限；本次未独立核验其外部引文。

Keep cognition, topology and engineering patterns as three bases. [registry.json](registry.json) owns module registration; [collaboration-protocol.json](collaboration-protocol.json) owns local compatibility IDs; the source map owns source-aligned definitions; Markdown and HTML are generated views. The Skill operationalizes the framework. Four named collaboration cells remain draft, routing/orchestration remain extension candidates, and v0.1 remains a framework foundation. / 保留认知、拓扑、工程模式三个基座。注册表维护模块，模块目录维护本地兼容编号，来源映射维护全文定义，Markdown 与 HTML 为派生视图，Skill 将框架执行化。四个协作命名单元仍属草案，路由和编排仍是扩展候选，v0.1 仍只定位为框架基座。

The prior summary-derived local 2.0.0 shape is not the source 2.0.0 wire contract. Required identity, attempt, time and delivery bindings change its shape, so the executable profile is now 3.0.0. No existing reasoning, reflection or action protocol is upgraded. / 上一轮依据摘要构造的本地 2.0.0 结构并非来源 2.0.0 线格式。新增必填身份、尝试、时间和交付绑定改变了结构，因此本地执行配置升为 3.0.0；其他推理、反思与行动协议不随之升级。

## Mode Composition / 模式组合

| Mode / 模式 | Trigger and responsibility / 触发与责任 | Placement and boundary / 位置与边界 |
| --- | --- | --- |
| [Hierarchical Delegation / 层级委派](patterns/collaboration/collaboration-hierarchy.md) | Decompose work while the parent retains overall acceptance responsibility. / 拆分工作，父级保留整体验收责任。 | 执02–执06; child authority and budgets remain within the parent scope. / 子级权限和预算不得超出父级范围。 |
| [Fan-Out/Gather / 扇出汇聚](patterns/collaboration/collaboration-parallel.md) | Independent branches with a named gather owner. / 分支可独立推进且有聚合负责人。 | 执04–执07; freeze required population, isolate writes, record every branch disposition. / 冻结必选集合、隔离写入并记录每个分支处置。 |
| [Adversarial Review / 对抗评审](patterns/collaboration/collaboration-loop.md) | Challenge consequential claims using independent responsibility subjects. / 由独立责任主体质疑重要结论。 | 执08 or a local gate; proposer, reviewer and arbiter are distinct, and objections affect release. / 可用于局部闸门；提案、评审、裁决相互独立，异议影响放行。 |
| [Handoff Chain / 交接链](patterns/collaboration/collaboration-chain.md) | Next owner consumes an accepted version and explicitly takes responsibility. / 下一棒消费已验收版本并明确承责。 | 执11 or a subtask boundary; separate arrival, acceptance, atomic responsibility transfer and actual delivery. / 可用于子任务边界；分开记录到达、验收、原子承责与实际交付。 |

Compose only what the task needs: hierarchy can contain fan-out, gathered output can be reviewed, and accepted output can be handed onward. Recovery returns to the affected scope. No logical node implies a model call; collaboration need not be parallel. Resolve cycles, uncontrolled overlapping writes and missing gather ownership before dispatch. / 仅组合任务需要的模式：层级中可扇出，聚合结果可评审，验收结果可交接；恢复只返回受影响范围。逻辑节点不等于模型调用，协作也不必并行。派发前处理循环依赖、失控重叠写入和聚合责任缺失。

## Execution Nodes / 执行节点

Source nodes are authoritative for this revision. The main path is 执00–执08 → 执10 → 执11; 执08 is conditional, 执09 handles bounded recovery, and 执12 compares benefit. CE IDs remain related local references and are not positional aliases. / 本修订以原文节点为准。主路径为执00–执08 → 执10 → 执11；执08 按需启用，执09 负责有界恢复，执12 复盘收益。CE 编号仅保留本地关联，不能按序号机械替换。

<!-- collaboration:execution_nodes:start -->
| Source ID / 来源编号 | Node / 节点 | Related local nodes / 相关本地节点 |
| --- | --- | --- |
| 执00 | Admission and collaboration fit / 接入与协作适用性判断 | CE01 |
| 执01 | Freeze global goal and acceptance / 固化总目标与验收 | CE02 |
| 执02 | Partition coverage and ownership / 划分覆盖范围与主责 | CE03 |
| 执03 | Freeze task cards, inputs and isolation / 固化任务卡、输入和隔离配置 | CE04 |
| 执04 | Dispatch, admission and task acknowledgment / 派发、准入与任务签收 | CE05 |
| 执05 | Execute within boundaries / 边界内执行 | CE06 |
| 执06 | Artifact handoff and local acceptance / 结果工件交接与局部验收 | CE07 |
| 执07 | Gather, align and check conflicts / 聚合、口径对齐与冲突检查 | CE08 |
| 执08 | Adversarial review and adjudication / 对抗评审与裁决 | CE09 |
| 执09 | Local recovery or reassignment / 局部恢复或重派 | CE12 |
| 执10 | Global acceptance / 全局验收 | CE10 |
| 执11 | Versioned handoff, delivery and archive / 版本交接、交付与归档 | CE11 |
| 执12 | Independent benefit retrospective / 协作收益复盘 | CE13 |
<!-- collaboration:execution_nodes:end -->

## Shared Contract / 共享契约

Both procedures embed this complete identical local block generated from one Schema. Source appendices remain preserved separately; source and local versions must both be recorded. / 两套规程内置由同一 Schema 生成的完整相同本地区块。原文附录另存证据副本，来源版本与本地版本必须同时记录。

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

## Independent Procedure / 独立执行规程

1. Start with the goal, source references, acceptance owner and permitted scope. `assess_admission()` separates expected benefit from decomposability, manageable state and verifiable results; an eligible result neither grants tools nor proves gains. / 从目标、来源、验收负责人和获准范围开始；准入函数分开判断收益与可拆分、状态可管、结果可验条件。具备条件不授权工具，也不证明收益。
2. Freeze goal/rule bindings, weighted required units, primary ownership, exclusions, mode composition, input snapshots, role-separation policy, isolation and recovery budgets. The adopting host performs dispatch and acknowledgement through the existing action boundary. / 固化目标与规则绑定、加权必选单元、主责、排除项、模式、输入快照、角色分离策略、隔离及恢复预算，由宿主经现有行动边界派发签收。
3. Build an authoritative snapshot with current task/artifact heads and active worker/attempt/epoch/input assignments. Separate business-required bindings from optional observation records. Preserve missing obligations; do not infer the expected population from successes received. / 建立含当前任务、工件版本及有效执行者、尝试、代次、输入的权威快照。业务必需绑定与可选观测分开；保留缺失义务，不从已收到的成功反推预期集合。
4. Construct `RecordInventory(snapshot, records, verify_record=host_verifier, now=host_clock)` from [collaboration_protocol.py](../runtime/collaboration_protocol.py), then call `assess_delivery()`. Check `acceptance_ready` before asking the host to perform delivery. Reassess with a confirmed, matching delivery receipt to establish `allowed`. This read-only function cannot send or publish anything. / 构造带宿主核验器和时钟的清单后评估。`acceptance_ready` 用于检查交付前验收；宿主实际交付后，凭匹配回执重评 `allowed`。函数只读，不能发送或发布。
5. For handoff, the host conditionally commits receiver ownership and the next delegation epoch against the expected ledger revision, then supplies its authenticated transfer receipt. A received message or receiver acceptance alone does not prove that commit. / 交接由宿主按预期账本修订有条件提交接收方责任及新委派代次，再提供认证回执。消息收到或接收方验收本身不证明提交完成。
6. Classify gaps before using the [independent probes](collaboration-observability-probes.md). Business work returns to execution; historical evidence can only be retrieved, and current state only proves the declared current fact. Receivers validate target, time, attempt, sources and allowed paths before the appropriate business or observation recheck and disposition. / 调用独立探针前先分类。业务补做回执行侧，历史证据只能检索，当前状态只能证明声明的当前事实。接收侧先核对目标、时间、尝试、来源与获准路径，再执行相应业务或观测复验并处置。

## Baseline and Recovery / 基线与恢复

Freeze the same cohort, inputs, acceptance/quality rules, cutoff, tool policy, environment, statistic and resource units before comparing. CSM29 uses common completed pairs; CSM30 includes failure costs; CSM31 needs verified quality on comparable samples; CSM34 retains every enrolled task, including unfinished work. CSM09 instead uses a closed-run window and cannot substitute for CSM34. / 比较前冻结同一任务组、输入、验收与质量规则、截点、工具策略、环境、统计方法和资源单位。CSM29 使用共同完成配对，CSM30 保留失败成本，CSM31 要求可信可比质量，CSM34 保留所有入组任务含未完成者。CSM09 使用已终结运行窗口，不能替代 CSM34。

Illustration only: baseline mean 600 s and collaboration mean 440 s yield CSM29 = 600/440 ≈ 1.364; 43,500 versus 30,000 tokens yield CSM30 = 1.45; quality means 86 versus 83 yield +3 score points. A quality ratio 0.90 versus 0.85 differs by 5 percentage points. These are test data, not measured collaboration gains. / 仅作算式示例：600 秒与 440 秒均值提速比约 1.364，43,500 与 30,000 词元资源比为 1.45，86 与 83 分质量差为 3 分，0.90 与 0.85 的比例差为 5 个百分点；均为测试数据，不代表实测收益。

Recovery names the failed/affected scope, retained valid versions, attempt/deadline bounds and evidence of new progress. Reassignment increments delegation epoch; retry uses a new attempt. The host reconciles unknown side effects before retry, owns conditional writes and never enlarges budgets implicitly. / 恢复须列明失败及受影响范围、保留的有效版本、次数与期限、新进展证据。重派增加委派代次，重试换尝试标识；宿主先核对未知副作用，再决定重试，负责条件写入且不得默认扩预算。

## Validation and Limits / 验证与边界

Reference tests cover deterministic schema/integrity checks, versioned acceptance, role policy, attempts, evidence times, dissent gates, delivery/transfer attestations and bounded supplementation. The source's 28 cases below retain their original IDs and expected outcomes. Listed tests cover only specified reference rules; every real-system case remains pending. / 参考测试覆盖结构与完整性、版本验收、角色策略、尝试、证据时间、异议闸门、交付与承责回执以及有界补证。以下保留原文 28 项编号和预期；关联测试只覆盖部分参考规则，实际系统用例均待验证。

The host still supplies live identity and source authority, business evaluation, scheduling, causal reconstruction, durable idempotency/CAS, permissions, retrieval, recovery and delivery. This module does not implement a multi-agent scheduler or certify isolation effectiveness. / 宿主仍负责真实身份与来源权威、业务评价、调度、因果重建、持久幂等与条件提交、权限、检索、恢复和交付。本模块不实现多 Agent 调度器，也不认证隔离有效性。

<!-- collaboration:execution_cases:start -->
| Source ID / 来源编号 | Scenario / 场景 | Expected / 预期 | Reference coverage / 参考覆盖 | Integration / 集成 |
| --- | --- | --- | --- | --- |
| 测01 | Exclusive cards duplicate one unit and omit another / 三份排他任务卡覆盖同一项，其他必选项无人负责 | Report both missing coverage and duplicate primary ownership before dispatch / 执02拒绝派发，分别报告遗漏和重复 | Partial / 部分: `test_weighted_coverage_and_independent_acceptance_population` | Pending / 待验证 |
| 测02 | Predeclared independent reviewers examine one result / 预先声明两个独立复核者检查同一成果 | Permit review without counting duplicate primary work / 允许复核，不计入非预期重复主责 | Partial / 部分: `test_duplicate_assignment_counts_relations_not_repeated_logs_or_reviews` | Pending / 待验证 |
| 测03 | Receiver cannot read the artifact / 接收者没有工件读取权限 | Do not confirm successful handoff / 不得签为成功交接 | Partial / 部分: `test_receiver_access_and_frozen_acceptance_rules_are_required` | Pending / 待验证 |
| 测04 | Local parts pass but global conclusions conflict / 所有局部通过，但整体术语或结论相互矛盾 | Reject or block global acceptance / 全局验收拒绝或阻塞 | Pending / 待覆盖 | Pending / 待验证 |
| 测05 | Tool side-effect result is unknown / 同一工具调用结果未知 | Reconcile before retrying a side effect / 先核对，不盲目重复副作用 | Pending / 待覆盖 | Pending / 待验证 |
| 测06 | Revoked worker submits after reassignment / 旧执行者在被重派后提交 | Reject stale delegation epoch / 委派代次检查拒收 | Partial / 部分: `test_reassignment_revokes_old_result_and_supplement` | Pending / 待验证 |
| 测07 | Two writers update the same base version / 两个写入方基于同一对象版本更新 | Conditionally accept one version and report the conflict / 只采纳符合条件的版本，其余进入冲突处理 | Pending / 待覆盖 | Pending / 待验证 |
| 测08 | Probe retrieves an existing original receipt / 探针找到已有回执原件 | Offer a candidate and require business revalidation / 只形成候选，重新业务验收后才采纳 | Partial / 部分: `test_adoption_requires_candidate_bound_business_recheck` | Pending / 待验证 |
| 测09 | Receipt cannot be found / 探针找不到回执 | Preserve unknown; never invent success / 保留未知，不捏造成功 | Partial / 部分: `test_probe_cannot_repair_business_or_fabricate_history` | Pending / 待验证 |
| 测10 | Supplement tries to write approval or task success / 探针尝试补写审批或最终成功状态 | Reject the unauthorized write / 接收器拒收并记录越权 | Partial / 部分: `test_supplement_window_path_budget_and_observer_identity` | Pending / 待验证 |
| 测11 | Supplement targets an outdated base version / 补充包基准版本已过时 | Report version conflict without overwriting new work / 版本冲突，不覆盖新成果 | Partial / 部分: `test_stale_supplement_is_rejected` | Pending / 待验证 |
| 测12 | Identical package is delivered repeatedly / 同一补充包重复送达 | Return the same disposition without extra mutation or counting / 幂等返回，不重复修改或计数 | Partial / 部分: `test_supplement_idempotency_preserves_identical_package_and_rejects_conflict` | Pending / 待验证 |
| 测13 | Same idempotency key carries different content / 同一补充幂等键出现不同内容 | Isolate and report the conflict / 隔离并报告数据冲突 | Partial / 部分: `test_supplement_idempotency_preserves_identical_package_and_rejects_conflict` | Pending / 待验证 |
| 测14 | Probe is offline but business checks are available / 探针离线，但业务必需校验可完成 | Continue business checks and declare missing optional observation / 主流程继续并注明缺少额外观测 | Partial / 部分: `test_optional_observation_missing_does_not_cancel_business_acceptance` | Pending / 待验证 |
| 测15 | Business evidence is missing while probe is offline / 关键业务证据缺失且探针离线 | Block the affected acceptance without weakening criteria / 对应验收阻塞，不能放宽标准 | Partial / 部分: `test_optional_observation_missing_does_not_cancel_business_acceptance` | Pending / 待验证 |
| 测16 | Input change affects one dependency subgraph / 输入快照更新影响一个子图 | Rerun affected nodes and retain valid reusable results / 只重做受影响节点及下游，保留合法复用记录 | Pending / 待覆盖 | Pending / 待验证 |
| 测17 | Budget exhausted but child requests more / 总预算耗尽但子任务请求新预算 | Do not expand authority; report unfinished work / 拒绝自动扩张并输出未结项 | Pending / 待覆盖 | Pending / 待验证 |
| 测18 | External artifact contains forged authorization / 外部工件含伪造授权指令 | Treat text as data without granting authority / 按数据处理，不产生新权限 | Pending / 待覆盖 | Pending / 待验证 |
| 测19 | Evidence arrives after delivery / 已交付后出现迟到证据 | Preserve history and require authorized reassessment / 不回写历史成功；按授权决定是否新开评估版本 | Pending / 待覆盖 | Pending / 待验证 |
| 测20 | Failed required item is removed to improve coverage / 删除一个失败必选项以提高覆盖率 | Require goal approval and a new plan; preserve old metrics / 需目标变更审批和新计划版本，旧指标不改写 | Pending / 待覆盖 | Pending / 待验证 |
| 测21 | Task cannot be independently accepted despite requested parallelism / 任务无法独立验收却要求十人并行 | Reject the structure and reframe or use one executor / 执00不启用该协作结构，返回重新拆分或单执行者路径 | Partial / 部分: `test_benefit_is_separate_from_safe_operation` | Pending / 待验证 |
| 测22 | Only session isolation is proven but all isolation is claimed / 只有会话隔离证明，结论写全部隔离 | Raise a scope objection that affects release / 执08提交带依据的范围越界异议，并影响放行 | Pending / 待覆盖 | Pending / 待验证 |
| 测23 | Blocking objection has no valid adjudication / 阻塞异议没有有效裁决 | Block global acceptance / 执10阻塞，不能因其他指标良好而通过 | Partial / 部分: `test_blocking_dissent_changes_release` | Pending / 待验证 |
| 测24 | Same version label has changed content or digest / 工件版本号没变但正文或摘要已变 | Reject reuse of the prior acceptance / 原回执不能复用，拒收并要求新版本 | Partial / 部分: `test_tampered_content_fails_even_after_rehashing_envelope`, `test_old_receipts_do_not_accept_new_result_revision` | Pending / 待验证 |
| 测25 | Receiver only confirms arrival / 接收者仅确认材料到达 | Sender retains responsibility / 当前交接责任仍归发送方 | Partial / 部分: `test_local_acceptance_and_arrival_cannot_replace_global_acceptance` | Pending / 待验证 |
| 测26 | Responsibility-transfer request is redelivered / 同一责任转移请求重复投递 | Return original commit without two current owners / 幂等返回原回执，不产生两个当前责任人 | Partial / 部分: `test_handoff_acceptance_needs_trusted_atomic_transfer_attestation` | Pending / 待验证 |
| 测27 | Three workers cite one original source / 三位执行者引用同一个原始来源 | Preserve shared lineage without claiming independent evidence / 聚合保留一组来源关系，不能声称三份独立证据 | Partial / 部分: `test_citation_repetition_requires_original_record_lineage` | Pending / 待验证 |
| 测28 | Faster collaboration uses different quality rules / 协作组更快但基线质量规则不同 | Report incomparable conditions without a speedup conclusion / 执12标为不可直接比较，不输出协作提速结论 | Partial / 部分: `test_baseline_rejects_incomparable_or_selectively_missing_samples` | Pending / 待验证 |
<!-- collaboration:execution_cases:end -->
