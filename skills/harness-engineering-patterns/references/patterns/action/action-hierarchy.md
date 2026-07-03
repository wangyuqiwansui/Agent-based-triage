# Guardrail Sandwich / 护栏夹层

Cell / 交织点: action-hierarchy / 行动 x 层级
Capability / 能力: Action / 行动
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Guardrail Sandwich wraps every consequential action between a pre-check layer (permission, parameters, impact rehearsal), a controlled execution layer (sandbox, least privilege), and a post-verify layer (result check, side-effect audit, rollback plan), with guardrails placed at each level of the phase-task-subtask hierarchy. / 护栏夹层把每个有后果的动作夹在前置检查层（权限、参数、影响面预演）、受控执行层（沙箱、最小权限）与后置验证层（结果校验、副作用审计、回滚预案）之间，护栏沿阶段-任务-子任务层级逐层布置。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Action / 行动 x Hierarchy / 层级 (Hierarchy / 层级).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; Environmental Constraint Law 2 names it for irreversible-action authority; source table maps Action / 行动 x Hierarchy / 层级 in arXiv:2605.13850. / 矩阵列名模式 / Matrix-listed pattern；环境约束定律 2 为不可逆动作点名；来源表将 Action / 行动 x Hierarchy / 层级 映射到该单元。
- 问题 / Problem: Irreversible actions executed with only a single flat check — or none — leave no chance to catch a bad parameter before damage, no containment during execution, and no verification that side effects matched intent afterward. / 不可逆动作若只有一道扁平检查甚至没有检查，就没有机会在造成损害前拦截坏参数、执行中没有隔离、事后也无法验证副作用是否符合意图。
- 架构方案 / Architectural Solution: Sandwich each consequential action between three ordered layers — pre-check (permission, parameter, impact rehearsal such as dry-run or diff preview), controlled execution (sandbox, least privilege), post-verify (result check, side-effect audit, ready rollback plan) — and place guardrails at phase, task, subtask, and action levels so an escaped fault meets the next layer's check. / 将每个有后果的动作夹在三段有序层之间——前置检查（权限、参数、干跑或差异预览式影响面预演）、受控执行（沙箱、最小权限）、后置验证（结果校验、副作用审计、就绪的回滚预案）——护栏沿阶段、任务、子任务、动作层级布置，逃过一层的故障会撞上下一层检查。
- 工程权衡 / Engineering Trade-offs: Layered guardrails convert irreversible failures into pre-execution blocks or post-execution rollbacks, but each layer adds latency and maintenance; over-sandwiching trivial reversible actions wastes throughput — reversibility × impact decides which actions deserve the full sandwich (Law 2), and thresholds are re-derived locally (Law 5). / 分层护栏把不可逆失败转化为执行前阻断或执行后回滚，但每层都增加时延与维护成本；对琐碎可逆动作过度夹层浪费吞吐——由"可逆性 × 影响面"决定哪些动作值得完整夹层（定律 2），阈值按定律 5 本地重推。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when action execution must be constrained by layered pre/post guardrails. / 当行动执行必须受分层前后置护栏约束时使用。

### Sandwich Layer Model / 夹层模型

| Layer / 层 | Checks / 检查内容 | On Failure / 失败时动作 |
| --- | --- | --- |
| Pre-check / 前置检查 | Permission and scope match, parameter schema, impact rehearsal (dry-run, diff preview, affected-resource list). / 权限与范围匹配、参数 schema、影响面预演（干跑、差异预览、受影响资源清单）。 | Block before execution; escalate ambiguous scope to approval per `GOV_0001`. / 执行前阻断；范围模糊按 `GOV_0001` 升级审批。 |
| Controlled execution / 受控执行 | Runs inside sandbox or controlled runtime with least privilege per `GOV_0003`; resource and time limits armed. / 按 `GOV_0003` 在沙箱或受控 runtime 内以最小权限运行；资源与时间限制就位。 | Kill and contain; never widen privileges mid-run. / 终止并隔离；绝不在运行中扩权。 |
| Post-verify / 后置验证 | Result matches intent, side-effect audit against the rehearsed impact list, rollback plan ready and tested. / 结果符合意图、副作用对照预演影响清单审计、回滚预案就绪且经过验证。 | Roll back or compensate; record the gap between rehearsed and actual impact. / 回滚或补偿；记录预演与实际影响的差距。 |

Placement rules / 布置规则:

- Guardrails stack by hierarchy: phase-level gates bound what tasks may do, task-level gates bound subtasks, action-level sandwiches wrap individual irreversible calls — a fault escaping one level meets the next. / 护栏按层级叠放：阶段级门约束任务、任务级门约束子任务、动作级夹层包裹单个不可逆调用——逃过一层的故障会撞上下一层。
- Complementary cells / 互补格: Blast Radius Control (governance-hierarchy) bounds *where* effects may land in space; the sandwich bounds *when* checks fire around a single action's timeline. / 爆炸半径控制（governance-hierarchy）管副作用在空间上能落到哪里；夹层管单个动作时间线上检查何时触发。
- Only irreversible or high-impact actions get the full three layers; reversible-low-impact actions may skip the rehearsal to avoid check fatigue. / 只有不可逆或高影响动作才配齐三层；可逆低影响动作可跳过预演以避免检查疲劳。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Guardrail Sandwich / 护栏夹层.
- 诊断用途 / Diagnostic Use: Use when action execution must be constrained by layered pre/post guardrails. / 当行动执行必须受分层前后置护栏约束时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 执行实现、发布交付 / Implementation, delivery.
- 当前症状 / Current Symptoms: Irreversible actions (deletes, deploys, external writes) execute with no dry-run or rollback plan; incidents reveal side effects nobody predicted; checks exist but all at one flat level, so a single miss reaches production. / 不可逆动作（删除、部署、外部写入）在没有干跑或回滚预案的情况下执行；事故暴露出无人预测到的副作用；检查虽有但全在同一扁平层，漏过一次就直达生产。
- 适配信号 / Fit Signals: 行动需要按阶段、任务、子任务或权限层级执行 / Actions execute by phase, task, subtask, or permission level.
- 调整方向 / Adjustment Direction: Wrap irreversible actions in the three-layer sandwich and stack guardrails down the phase-task-subtask hierarchy. / 用三层夹层包裹不可逆动作，并沿阶段-任务-子任务层级叠放护栏。
- 修改方式 / How To Modify: 1) Classify actions by reversibility × impact and pick the ones deserving the full sandwich (Law 2). 2) Define pre-checks including an impact rehearsal (dry-run or diff preview). 3) Confine execution to sandbox with least privilege. 4) Define post-verify checks and a tested rollback plan per action class. 5) Stack level gates so phase bounds task and task bounds subtask. / 1）按可逆性 × 影响面给动作分级，选出值得完整夹层的动作（定律 2）；2）定义含影响面预演（干跑或差异预览）的前置检查；3）执行限定在最小权限沙箱内；4）为每类动作定义后置验证与经过验证的回滚预案；5）叠放层级门：阶段约束任务、任务约束子任务。
- 输入 / Inputs: Action request with reversibility and impact class, permission scope, rehearsal capability (dry-run, diff), sandbox environment, rollback recipes. / 带可逆性与影响等级的动作请求、权限范围、预演能力（干跑、差异）、沙箱环境、回滚配方。
- 输出 / Outputs: Pre-check verdicts with rehearsal artifacts, contained execution record, post-verify report (result check, side-effect audit), rollback events with outcomes. / 带预演产物的前置检查裁定、受控执行记录、后置验证报告（结果校验、副作用审计）、带结果的回滚事件。
- 风险与治理 / Risks & Governance: Permission bypass `FAIL_0005` when an action skips its pre-check level — make the sandwich the only execution path for irreversible classes; sandbox escape `FAIL_0009` — execution layer enforces `GOV_0003` boundaries and never widens privileges mid-run; ambiguous-scope actions escalate to approval per `GOV_0001`; all three layers' verdicts are recorded per `GOV_0002` so the post-incident audit can replay which layer failed. / 动作绕过前置检查层即权限绕过 `FAIL_0005`——让夹层成为不可逆动作类的唯一执行路径；沙箱逃逸 `FAIL_0009`——执行层强制 `GOV_0003` 边界且绝不在运行中扩权；范围模糊动作按 `GOV_0001` 升级审批；三层裁定全部按 `GOV_0002` 入账，事后审计可回放是哪一层失守。

Observability Metrics File / 可观测性指标文件: [action-hierarchy-observability.md](action-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
