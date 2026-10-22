# Workflow Audit Report / 工作流审计报告

Template instructions: replace field descriptions with observed facts or explicit unknowns. Scale the prose, not requested coverage. Delete instructions from the delivered report. Use the user's language for the report unless bilingual output is requested; this reusable template is bilingual. / 模板说明：以观察事实或明确未知替换字段说明。可缩减文字，不缩减用户要求的覆盖。交付时删除说明。报告使用用户语言，除非另要求双语；本可复用模板保持双语。

## Scope and Conclusion / 范围与结论

- Analysis ID, project/root, workflow(s), source revision and relevant dirty files or document version / 分析编号、项目路径、工作流、来源版本及相关未提交文件或文档版本。
- Objective, trigger, success/failure terminals, environment and constraints / 目标、触发、成功失败终态、环境及约束。
- Requested scope, excluded areas with reasons, assumptions and unresolved business criteria / 请求范围、排除项及理由、假设和待明确业务标准。
- Overall assessment, highest-impact confirmed findings, effective mechanisms to retain, and limits on confidence / 总体判断、影响最大的已确认发现、应保留机制及置信边界。
- Review status: complete or partial; reviewed nodes / in-scope nodes; reviewed edges / in-scope edges; partially reviewed and unreviewed IDs / 审查状态：完整或部分；已审节点数/范围内节点数、已审连线数/范围内连线数，部分及未审编号。
- Evidence limits: investigated-but-unknown nodes/edges and inaccessible sources, kept separate from unreviewed entries / 证据局限：已调查但未知的节点连线及不可访问来源，与未审项分开。

## Actual Workflow / 实际工作流

Describe ordering, branches, joins, feedback, failure exits and manual handoffs. Add a diagram if useful. Preserve stable IDs shared by all tables. / 描述顺序、分支、汇合、反馈、异常出口及人工交接；按需绘图，各表共用稳定编号。

### Node Inventory and Coverage / 节点清单与覆盖

One row per in-scope responsibility, including adequate and unknown nodes. A node can link multiple findings; summarize mixed checks instead of forcing one verdict. / 每项范围内职责一行，包含已足够及未知节点。节点可关联多项发现；不同检查结论并存时概要说明，不强行归一。

| Node ID and responsibility / 节点编号与职责 | Owner, trigger / 责任、触发 | Inputs → outputs, consumers / 输入→输出、接收者 | Current control and exits / 当前控制及出口 | Review state / 审查状态 | Check dispositions and evidence / 检查结论及证据 | Findings / 发现编号 |
| --- | --- | --- | --- | --- | --- | --- |

Review state: `reviewed`, `partial`, `unreviewed`, `out_of_scope`. Check disposition: `confirmed_gap`, `suspected_gap`, `adequate`, `unknown`, `not_applicable`. State the reason for exclusions. / 审查状态：已审、部分、未审、范围外；检查结论：已确认不足、疑似不足、已足够、未知、不适用。排除须说明理由。

### Transition Inventory / 转移清单

| Edge ID, source → target / 连线编号、来源→目标 | Condition and artifact/version / 条件及制品版本 | Responsibility transfer and acceptance / 责任转移与验收 | Failure, timeout, recovery / 失败、超时、恢复 | Review state and disposition / 审查状态与结论 | Evidence and findings / 证据及发现 |
| --- | --- | --- | --- | --- | --- |

## Finding Cards / 发现卡

Repeat for material findings; a compact table can replace cards for small scopes if it preserves these fields. Shared root causes reference all affected subjects and one action; adequate nodes need no invented issue. / 为实质发现重复此卡；小范围可用保留相同字段的紧凑表格。共同根因关联全部受影响对象及一个行动项，已足够节点无需硬造问题。

- **Identity / 身份:** `FINDING_*`, title, affected `NODE_*` / `EDGE_*`, disposition, confidence with rationale. / 发现编号、标题、受影响节点连线、结论、置信程度及依据。
- **Expected vs actual / 预期与实际:** requirement source, current behavior, exact mismatch, trigger and downstream impact. / 要求来源、当前行为、具体偏差、触发及下游影响。
- **Evidence / 证据:** `EVIDENCE_*`, supporting observations, counterevidence, missing data and whether the claim is static or observed. / 证据编号、支持观察、反证、缺失数据，以及静态判断或运行观察。
- **Cause / 原因:** proven mechanism or labeled hypothesis; avoid restating the symptom as the cause. / 已证机制或标明的假设，避免以症状充当原因。
- **Remedy / 弥补:** immediate containment if needed, smallest durable correction, exact change location/process artifact, retained controls and rejected heavier alternatives when relevant. / 必要止损、最小长期修复、具体修改位置或流程制品、保留控制，及适用时未采纳复杂方案的原因。
- **Priority / 优先级:** P0–P3 or project standard, supporting impact/exposure/reversibility, dependencies and whether this prioritizes investigation or correction. / 项目标准或 P0–P3，影响暴露可逆性依据、依赖，以及调查或修复优先级。
- **Delivery / 实施:** `ACTION_*`, owner role or unassigned, effort with assumptions, risks/tradeoffs, rollout and recovery if applicable. / 行动编号、责任角色或待分配、带假设工作量、风险取舍及适用的实施恢复。
- **Acceptance / 验收:** `CHECK_*`, input/condition, expected state/output, authoritative observation, environment, responsible role, pass/fail rule and verification status. / 验收编号、输入条件、预期状态输出、权威观察、环境、责任角色、通过失败规则及验证状态。

## Improvement Backlog / 改进清单

| Action / 行动 | Findings and subjects / 发现及对象 | Concrete deliverable / 具体交付物 | Priority and rationale / 优先级及理由 | Prerequisites / 前置依赖 | Owner role / 责任角色 | Effort and assumptions / 工作量及假设 | Acceptance / 验收 | Delivery state / 实施状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Order by actual risk and dependencies. Separate containment, evidence collection and permanent correction. Delivery state may be proposed, accepted plan, implemented, verified in a named environment, or operationally observed; do not imply all stages occurred. / 按实际风险及依赖排序，分开止损、补证和永久修复。实施状态可为建议、已接受方案、已实现、指定环境已验证、已运行观察；不要暗示所有阶段都已发生。

## Acceptance and Observation / 验收与观察

| Check / 检查 | Finding/action / 发现/行动 | Scenario and baseline / 场景与基线 | Expected result and source of truth / 预期结果及权威来源 | Procedure, environment, version / 流程、环境、版本 | Actual result and evidence / 实际结果及证据 | Status and owner / 状态及责任 |
| --- | --- | --- | --- | --- | --- | --- |

Status: `not_run`, `passed`, `failed`, `blocked`, `not_applicable`. Where relevant, include normal, failure and recovery cases; record the selected cases' limits. For metrics, state definition, sample window, denominator, baseline, target rationale and guardrails. An unmeasured value is unknown. / 状态：未运行、通过、失败、受阻、不适用。按需包含正常、失败及恢复场景，注明所选场景局限。指标说明定义、窗口、分母、基线、目标依据及护栏；未测值为未知。

## Evidence and Open Questions / 证据与待核实项

| Evidence / 证据 | Source path and line/section/event / 来源路径及行章节事件 | Revision, time, environment / 版本、时间、环境 | Kind / 类型 | Supports and limits / 支持内容及局限 |
| --- | --- | --- | --- | --- |

| Question / 待核实项 | Affected subjects / 影响对象 | Missing or conflicting evidence / 缺失或冲突证据 | Collection task and source / 采集任务及来源 | Owner role / 责任角色 | Completion criterion / 完成标准 |
| --- | --- | --- | --- | --- | --- |

## EIR and Trace Links / EIR 与 Trace 关联

Retain the relevant business nodes, source components, control/state/tool/permission flows and evidence references using `references/eir-schema.md`. Include matrix mappings and patterns only when useful; zero added patterns is valid. Findings/coverage/backlog are report-local companions, not runtime schema changes. / 按 EIR 指南保留相关业务节点、源码组件、控制状态工具权限流及证据引用；按需纳入矩阵模式，允许不新增模式。发现、覆盖、改进清单为报告内配套记录，不改运行时 Schema。

Use `references/trace-schema.md` for a Trace proposal: intended project-local path, analysis ID, scope, sensitivity, subject, source revision, before/adjustment/outcome, evidence, validity, owner, retention and follow-up. Mark proposed remedies as proposed and future checks as pending. / 按 Trace 契约提出追踪建议：项目本地预期路径、分析编号、范围、敏感性、对象、来源版本、修改前及调整结果、证据、有效状态、责任、留存和后续。建议仍标为建议，未来检查仍待完成。
