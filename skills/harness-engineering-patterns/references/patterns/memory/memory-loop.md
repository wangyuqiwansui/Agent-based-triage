# Failure Diary / 失败日记

Cell / 交织点: memory-loop / 记忆 x 循环
Capability / 能力: Memory / 记忆
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850), extended with user-provided failure diary workflow. / 来源：arXiv:2605.13850，并结合用户提供的失败日记执行流程扩展。

Use this file as the design pattern source for this matrix intersection. / 将本文档作为该交织点的设计模式来源。

Observability Metrics File / 可观测性指标文件: [memory-loop-observability.md](memory-loop-observability.md)

## Design Pattern / 设计模式

Use Failure Diary when failures must be recorded, reviewed, indexed, and recalled across future attempts so the next similar workflow changes behavior before repeating the same mistake. / 当失败必须被记录、审查、索引，并在未来相似任务中召回，从而让下一次流程提前改变行为时，使用失败日记。

This pattern is not a normal error log. It turns a failure into a reviewed experience guardrail: capture the event, preserve evidence, extract a concrete lesson, control review state, recall the lesson at the right boundary, re-check current facts, and update or archive the lesson after observing the result. / 本模式不是普通错误日志。它把失败转化为经过审查的经验护栏：捕获事件、保留证据、提取具体教训、控制审查状态、在正确边界召回、重新核验当前事实，并在观察结果后更新或归档经验。

## Article Grounding / 论文依据

- Article coordinate / 论文坐标: Memory x Loop / 记忆 x 循环.
- Article basis / 论文依据: the matrix maps memory feedback loops to failure reuse across attempts. / 矩阵将记忆反馈循环映射到跨尝试复用失败经验。
- Core fit signal / 核心适配信号: outcomes are written back to memory and affect the next iteration. / 结果持续反写记忆，并影响下一轮工作。
- Engineering extension / 工程扩展: add evidence, review, recall, current-fact re-check, governance, and lifecycle controls. / 工程扩展：加入证据、审查、召回、当前事实再核验、治理和生命周期控制。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Failure Diary / 失败日记.
- 论文坐标 / Article Coordinate: Memory / 记忆 x Loop / 循环.
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; extended as a user-provided executable workflow. / 矩阵列名模式；并扩展为用户提供的可执行工作流。
- 问题 / Problem: A workflow repeats the same failure because prior failures are logged but not converted into reviewed, recallable action constraints. / 工作流重复同类失败，因为过去失败只被记录，没有转化为经过审查、可召回的行动约束。
- 架构方案 / Architectural Solution: Build a loop that captures failure candidates, assembles evidence, distills lessons, runs review states, indexes enabled cards, recalls before future risky actions, and updates outcomes. / 构建循环：捕获失败候选、组装证据、蒸馏教训、运行审查状态、索引已启用卡片、在未来高风险动作前召回，并根据结果更新。
- 工程权衡 / Engineering Trade-offs: Failure memory reduces repeated mistakes, but needs evidence quality, recall limits, current-fact re-checks, and governance to avoid noise or memory poisoning. / 失败记忆能减少重复错误，但需要证据质量、召回数量控制、当前事实再核验和治理，避免噪声或记忆投毒。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when failures must be recorded, reviewed, indexed, and recalled across future attempts. / 当失败必须被记录、审查、索引，并在未来相似任务中召回时使用。
- 适用工作流节点 / Applicable Workflow Nodes: failure capture, validation gate, review, indexing, planning, pre-action guardrail, task-end observation. / 失败捕获、验证闸门、审查、索引、规划、动作前护栏、任务结束观测。
- 风险与治理 / Risks & Governance: Unreviewed recall, stale lessons, cross-scope leakage, over-broad recall, and memory poisoning require state-machine, source, scope, and retention controls. / 未审查召回、过期经验、跨范围泄漏、召回过宽和记忆投毒需要状态机、来源、范围和留存控制。

## When To Use / 适用场景

Use this pattern for long-running, high-recurrence, or high-loss workflows such as development fixes, operations releases, data analysis, finance approval, contract review, customer support, HR processes, office automation, multi-tool orchestration, and knowledge retrieval. / 适用于长程、高复发或高损失流程，例如研发修复、运维发布、数据分析、财务审批、合同审阅、客服、人事流程、办公自动化、多工具编排和知识检索。

Prefer this pattern when failures involve tools, validation gates, semantic drift, stale context, wrong mechanical state, permission boundaries, tenant or environment leakage, approval bypass, production writes, customer impact, or irreversible side effects. / 当失败涉及工具、验证闸门、语义偏离、过期上下文、机械状态错误、权限边界、租户或环境泄漏、审批绕过、生产写入、客户影响或不可逆副作用时，优先使用本模式。

Do not use it for one-off network jitter, harmless formatting cleanup, events with no recurrence value, or unverified claims that cannot be isolated from recall. / 不适用于一次性网络抖动、无影响格式修正、没有复发价值的事件，或无法核验且不能隔离召回的说法。

## Core Objects / 核心对象

### Failure Candidate / 失败候选事件

```text
Failure candidate / 失败候选：
  Event ID / 事件编号：
  Workflow instance / 工作流编号：
  Task family / 任务族：
  Node / 节点名称：
  Failure boundary / 失败边界：hard / gate / semantic / safety
                                硬失败 / 闸门失败 / 语义失败 / 安全失败
  Failure category / 失败分类：
  Risk level / 风险等级：low / medium / high / critical
                            低 / 中 / 高 / 严重
  Trigger source / 触发来源：
  Evidence reference / 证据引用：
  Status / 状态：draft / pending review / enabled / archived
                 草稿 / 待审查 / 已启用 / 已归档
```

### Failure Diary Entry / 失败日记条目

```text
Failure diary entry / 失败日记条目：
  Failure ID / 失败编号：
  Task family / 任务族：
  Failure boundary / 失败边界：
  Failure category / 失败分类：
  Risk level / 风险等级：
  Status / 状态：
  Symptom / 表面现象：
  Root cause / 根因分析：
  Current remediation / 本次补救：
  Next lesson / 下次教训：
  Forbidden actions / 禁止动作：
  Evidence package / 证据包：
  Recall conditions / 召回条件：
  Retention policy / 留存策略：
  Review record / 审查信息：
```

### Recall Danger Card / 召回危险卡

```text
Recall danger card / 召回危险卡：
  Lesson ID / 经验编号：
  Why relevant / 适用原因：
  Risk warning / 风险提醒：
  Forbidden action / 禁止动作：
  Required check / 必做校验：
  Evidence reference / 证据引用：
  Trust status / 可信状态：
  Current re-check / 当前事实再核验：
```

## Execution Workflow / 执行流程

1. Register context: record task goal, task family, node, workflow instance, tenant, project, environment, permission scope, and trace channel. / 任务接入：记录任务目标、任务族、节点、工作流编号、租户、项目、环境、权限范围和追踪通道。
2. Capture failure candidates from tool failures, gates, semantic drift, safety boundary touches, human feedback, abnormal metrics, rollbacks, and reconciliation mismatches. / 从工具失败、闸门、语义偏离、安全边界、人工反馈、指标异常、回滚和对账差异中捕获失败候选。
3. Decide the failure boundary as hard failure, gate failure, semantic failure, or safety failure. / 将失败边界判定为硬失败、闸门失败、语义失败或安全失败。
4. Classify and grade risk using stable categories such as tool failure, retrieval failure, planning failure, goal drift, context contamination, mechanical-state mismatch, boundary leakage, human-review bypass, policy violation, or unknown root cause. / 使用工具失败、检索失败、规划失败、目标漂移、上下文污染、机械状态错配、边界泄漏、人审绕过、策略违规或根因未知等稳定分类，并进行风险分级。
5. Assemble evidence with four layers: workspace evidence, narrative evidence, mechanical-state evidence, and raw observation evidence. / 组装四层证据：工作区证据、叙事证据、机械状态证据和原始观测证据。
6. Extract symptom, root cause, remediation, next lesson, and forbidden action. Root cause must point to a mechanism and become a recall condition or validation rule. / 提取表面现象、根因、本次补救、下次教训和禁止动作。根因必须指向具体机制，并能转化为召回条件或验证规则。
7. Distill a short danger card instead of injecting a long incident report into future work. / 蒸馏短危险卡，而不是把完整事故报告塞入未来上下文。
8. Run the review state machine: draft -> pending review -> enabled -> archived. / 运行审查状态机：草稿 -> 待审查 -> 已启用 -> 已归档。
9. Store and index only enabled lessons by task family, node, tool, mechanical parameter, category, risk, tenant/project scope, status, and version. / 仅将已启用经验按任务族、节点、工具、机械参数、分类、风险、租户/项目范围、状态和版本入库索引。
10. Recall proactively at task start, planning time, and before high-risk actions. / 在任务启动、任务规划和高风险动作前主动召回。
11. Inject recalled cards near the constrained action and re-check current facts, parameter source, permission, tenant, and environment. / 在被约束动作附近注入召回卡，并重新核验当前事实、参数来源、权限、租户和环境。
12. Observe whether recall changed the plan, parameters, validation, human review, rollback rate, or repeated-failure outcome. / 观察召回是否改变计划、参数、校验、人审、回滚率或重复失败结果。
13. Update, archive, or escalate lessons based on repeat failures, false reminders, missed recalls, invalidated root causes, resolved mechanisms, or poisoning signals. / 根据重复失败、误提醒、漏召回、根因被推翻、机制已修复或污染信号，更新、归档或升级经验。

## Review State Machine / 审查状态机

```text
draft / 草稿
  -> pending review / 待审查
  -> enabled / 已启用
  -> archived / 已归档
```

Special transitions: / 特殊流转：

- Draft to archived when there is no recurrence value. / 无复发价值时，草稿可直接归档。
- Pending review to draft when evidence is insufficient. / 证据不足时，待审查退回草稿。
- Enabled to pending review when the same failure repeats after recall. / 已启用经验召回后仍重复失败时，退回待审查。
- Enabled to archived when the mechanism has fully eliminated the issue. / 机制已彻底消除问题时，已启用经验可归档。

## Recall Rules / 召回规则

| Rule / 规则 | Action / 动作 |
|---|---|
| Same task family + same tool + same mechanical parameter + high risk / 同任务族 + 同工具 + 同机械参数 + 高风险 | Recall before the action with highest priority. / 动作前最高优先级召回。 |
| Same task family + same failure category / 同任务族 + 同失败分类 | Recall during planning. / 规划时召回。 |
| Same node + same risk level / 同节点 + 同风险等级 | Recall as medium priority. / 中优先级召回。 |
| Semantic similarity without structured keys / 仅语义相似但结构键不一致 | Low priority; require current-fact re-check. / 低优先级，并强制当前事实再核验。 |

Default limits: task start up to 3 lessons, planning up to 5 lessons, high-risk action up to 3 danger cards. / 默认数量：任务启动最多 3 条，规划最多 5 条，高风险动作前最多 3 张危险卡。

## Governance / 治理约束

- Automatically generated entries start as draft. / 自动生成条目必须从草稿开始。
- High-risk entries require human review before activation. / 高风险条目启用前必须人工审查。
- Ordinary conversation cannot directly write to the enabled recall library. / 普通对话不得直接写入已启用召回库。
- Recall only enabled lessons by default. / 默认只召回已启用经验。
- Recalled lessons must show source, status, and scope. / 召回经验必须显示来源、状态和范围。
- Lessons must not override current business rules, verified current facts, or permission gates. / 经验不得覆盖当前业务规则、已验证当前事实或权限门控。
- Cross-tenant, cross-project, cross-environment, and source-free memories must stay isolated. / 跨租户、跨项目、跨环境和无来源记忆必须隔离。

## Minimal Record Template / 最小记录模板

```text
Failure ID / 失败编号：
Task family / 任务族：
Failure boundary / 失败边界：
Failure category / 失败分类：
Risk level / 风险等级：
Status / 状态：
Symptom / 表面现象：
Root cause / 根因分析：
Current remediation / 本次补救：
Next lesson / 下次教训：
Forbidden actions / 禁止动作：
Evidence reference / 证据引用：
Recall conditions / 召回条件：
Reviewer / 审查人：
Review time / 审查时间：
Retention policy / 留存策略：
```

## Failure Modes / 失败模式

| Failure mode / 失败模式 | Signal / 表现 | Correction / 修正方向 |
|---|---|---|
| Error-only diary / 只记错误不写教训 | Future behavior does not change. / 下次行为没有改变。 | Distill a danger card. / 蒸馏危险卡。 |
| Vague root cause / 根因过泛 | Causes say "careless" or "unstable." / 根因写成“粗心”或“不稳定”。 | Point to a mechanism. / 指向具体机制。 |
| Weak evidence / 证据不足 | Review cannot reproduce facts. / 审查无法还原事实。 | Require four evidence layers. / 强制四层证据。 |
| Missing recall condition / 缺召回条件 | Diary becomes passive documentation. / 日记变成被动文档库。 | Add structured recall keys. / 增加结构化召回键。 |
| Recall too late / 召回太晚 | Side effect already happened. / 副作用已经发生。 | Add pre-action recall. / 增加动作前召回。 |
| False reminders / 误提醒过多 | Irrelevant cards distract work. / 无关卡片干扰任务。 | Narrow recall conditions. / 缩窄召回条件。 |
| Missed recall / 漏召回过多 | Same failure repeats. / 同类失败重复。 | Add indexes or entry points. / 增加索引或召回入口。 |
| Unreviewed recall / 未审查即召回 | Bad memory affects actions. / 错误记忆影响动作。 | Enforce state machine. / 强化状态机。 |
| Memory poisoning / 记忆投毒 | Untrusted lesson persists. / 不可信经验长期存在。 | Track source, isolate, and review. / 追踪来源、隔离并审查。 |

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
