# Runtime Trace Contract / 运行 Trace 契约

Use this contract for analysis-time and runtime observations produced by this Skill. Store runtime state with the analyzed project, not inside the Skill package. / 使用本契约记录本 Skill 在分析期和运行期产生的观察数据。运行状态应随被分析项目存储，不写入 Skill 包内部。

## Default Location / 默认位置

```text
.harness-analysis/<analysis_id>/trace.yaml
```

If the destination is unavailable, return the Trace payload in the response and name the intended path. Do not redirect runtime data into `references/patterns/*/trace.md`. / 如果目标不可用，在响应中返回 Trace 载荷并说明预期路径；不要把运行数据重定向到 `references/patterns/*/trace.md`。

## Runtime Record / 运行记录

```yaml
trace_id: TRACE_0001
analysis_id: ANALYSIS_20260710_0001
event_time: "2026-07-10T00:00:00Z"
status: draft | active | superseded | deprecated | verified

scope:
  project_scope: "project identifier or repository"
  tenant_scope: "tenant or none"
  environment_scope: "local | test | staging | production"
  task_scope: "bounded workflow slice"

sensitivity: public | internal | confidential | restricted
source_revision: "repository commit, artifact version, or document revision"

subject:
  subject_type: business_node | source_component | pattern | skill | workflow
  subject_ref: NODE_0001
  cell_refs: [CELL_ACTION_ROUTING]
  pattern_refs: [PATTERN_0036]

observation:
  trigger: "what started this record"
  before: "evidence-backed state before adjustment"
  adjustment: "what changed or was recommended"
  outcome: "observed result or pending observation"
  validity: proposed | observed | verified | superseded | rejected

evidence_refs: [EVIDENCE_0001]
verification_tasks: []
follow_up: []
owner: "responsible person or Agent"

retention:
  policy: session | project | audit | legal_hold
  expires_at: null
  deletion_or_archive_rule: "archive when superseded"
```

## Required Boundaries / 必需边界

- `analysis_id` separates independent analyses. / `analysis_id` 隔离独立分析。
- `project_scope`, `tenant_scope`, and `environment_scope` prevent cross-scope reuse. / `project_scope`、`tenant_scope` 和 `environment_scope` 防止跨范围复用。
- `sensitivity` controls whether content may enter reports, prompts, or shared stores. / `sensitivity` 控制内容能否进入报告、提示或共享存储。
- `source_revision` freezes the evidence version used by the observation. / `source_revision` 固定观察所使用的证据版本。
- `evidence_refs` must resolve through the EIR or declare an external reference. / `evidence_refs` 必须通过 EIR 解析，或声明外部引用。
- `validity` distinguishes proposals, observations, verified outcomes, superseded records, and rejected claims. / `validity` 区分建议、观察、已验证结果、已废弃记录和被拒判断。
- `retention` and `expires_at` prevent runtime evidence from becoming indefinite memory by default. / `retention` 与 `expires_at` 防止运行证据默认变成无限期记忆。
- `owner` names who closes verification and follow-up work. / `owner` 明确由谁关闭验证与后续工作。

## Curated Skill History / Skill 精选历史

Bundled capability Trace files are curated pattern-level evidence snapshots. They may retain generalized lessons and reviewed evidence pointers, but they are not the latest project state. / Skill 内置能力 Trace 文件是模式级精选证据快照，可以保留泛化经验和经过复核的证据指针，但不代表项目最新状态。

Update curated history only when the user explicitly requests a Skill evidence update. Before writing, verify scope, sensitivity, source revision, validity, and whether the lesson generalizes beyond one project. / 只有用户明确要求更新 Skill 证据时才修改精选历史。写入前核验范围、敏感级别、来源版本、有效状态，以及经验是否能超越单一项目泛化。

## Minimum Trace Proposal / 最小 Trace 建议

When a full file is unnecessary, return: / 不需要完整文件时，返回：

- Intended path / 预期路径
- `analysis_id`
- Scope and sensitivity / 范围与敏感级别
- Subject and coordinate / 对象与坐标
- Before, adjustment, and outcome / 使用前、调整和结果
- Evidence references and source revision / 证据引用与来源版本
- Validity, owner, retention, and follow-up / 有效状态、负责人、留存和后续
