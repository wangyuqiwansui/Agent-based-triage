# Tool Dispatch / 工具分派

Cell / 交织点: action-routing / 行动 x 路由
Capability / 能力: Action / 行动
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Tool Dispatch classifies each pending action by type, permission level, and side-effect scope, then routes it to the right tool, skill, or owner through a maintained dispatch table — with schema-validated parameters and approval hooks for high-risk actions. / 工具分派按类型、权限等级和副作用范围对每个待执行动作分类，再通过维护的分派表将其路由到正确的工具、技能或负责人——参数经 schema 校验，高风险动作挂接审批。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Action / 行动 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Action / 行动 x Routing / 路由 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Action / 行动 x Routing / 路由 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: When every action goes through one generic execution path, capability mismatches send work to the wrong tool, hallucinated parameters reach real systems, and high-risk actions run with the same friction as trivial ones. / 当所有动作走同一条通用执行路径时，能力错配把工作送进错误工具、幻觉参数直达真实系统、高风险动作与琐碎动作以同样的摩擦执行。
- 架构方案 / Architectural Solution: Maintain a dispatch table keyed by action type: match tool capability before dispatch, validate parameters against the tool's schema, attach the permission requirement and side-effect class, and route approval-required actions through the Approval Gate (governance-routing) before execution inside sandbox boundaries. / 维护以动作类型为键的分派表：分派前先匹配工具能力、按工具 schema 校验参数、附上权限要求与副作用等级，需审批的动作先经审批门禁（governance-routing）再在沙箱边界内执行。
- 工程权衡 / Engineering Trade-offs: Correct dispatch buys specialization and least-privilege execution, but the table must be maintained as tools evolve, and a misclassified action either wastes a round trip or — worse — reaches a tool with broader side effects than intended. / 正确分派换来专门化与最小权限执行，但分派表必须随工具演进而维护；动作被误分类轻则浪费一次往返，重则进入副作用比预期更大的工具。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when the workflow chooses a tool based on request type or state. / 当工作流根据请求类型或状态选择工具时使用。

### Dispatch Table Model / 分派表模型

| Field / 字段 | Content / 内容 | Guarded Failure / 防护的失败 |
| --- | --- | --- |
| action_type / 动作类型 | Classified intent of the pending action. / 待执行动作的分类意图。 | Wrong-path dispatch. / 错误路径分派。 |
| target tool / 目标工具 | Tool or skill whose declared capability matches the action. / 声明能力与动作匹配的工具或技能。 | `FAIL_0003` wrong tool selection. / `FAIL_0003` 工具选择错误。 |
| parameter schema / 参数 schema | Validation rules the call parameters must pass before dispatch. / 分派前调用参数必须通过的校验规则。 | `FAIL_0004` parameter hallucination. / `FAIL_0004` 参数幻觉。 |
| permission requirement / 权限要求 | Identity and scope needed to invoke the target. / 调用目标所需的身份与范围。 | `FAIL_0005` permission bypass. / `FAIL_0005` 权限绕过。 |
| side-effect class / 副作用等级 | read-only, reversible write, irreversible, external. / 只读、可逆写、不可逆、外部副作用。 | Underestimated blast radius. / 影响面被低估。 |
| approval hook / 审批挂钩 | Whether the action routes through the Approval Gate (governance-routing) first, per `GOV_0001`. / 是否先经审批门禁（governance-routing），按 `GOV_0001`。 | Unreviewed high-risk execution. / 高风险动作未审即行。 |

Dispatch rules / 分派规则:

- No table entry, no dispatch: unknown action types go to a default safe path (human or read-only analysis), never to a guessed tool. / 无表项不分派：未知动作类型进默认安全路径（人工或只读分析），绝不猜测工具。
- Schema validation failures return to the caller with the diff; the dispatcher never repairs parameters silently. / schema 校验失败带差异退回调用方；分派器绝不静默修补参数。
- Execution runs inside controlled runtime or sandbox boundaries per `GOV_0003`, and every dispatch decision plus result is recorded per `GOV_0002`. / 执行按 `GOV_0003` 在受控 runtime 或沙箱边界内进行，每次分派决策与结果按 `GOV_0002` 入账。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Tool Dispatch / 工具分派.
- 诊断用途 / Diagnostic Use: Use when the workflow chooses a tool based on request type or state. / 当工作流根据请求类型或状态选择工具时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 执行实现、协作交接 / Implementation, collaboration handoff.
- 当前症状 / Current Symptoms: Actions frequently hit the wrong tool and bounce back; hallucinated or malformed parameters reach real systems; high-risk and trivial actions share one undifferentiated execution path with no approval distinction. / 动作频繁打到错误工具并被弹回；幻觉或畸形参数直达真实系统；高风险与琐碎动作共用一条无差别执行路径、没有审批区分。
- 适配信号 / Fit Signals: 不同动作需要分派给不同工具、权限或负责人 / Different actions must be routed to different tools, permissions, or owners.
- 调整方向 / Adjustment Direction: Put a capability-and-permission-aware dispatch table in front of execution, with schema validation and approval hooks as dispatch preconditions. / 在执行前放置能力与权限感知的分派表，以 schema 校验和审批挂钩作为分派前置条件。
- 修改方式 / How To Modify: 1) Inventory action types and the tools that can serve them. 2) Fill the dispatch table (target, schema, permission, side-effect class, approval hook). 3) Wire schema validation before dispatch and a default safe path for unknown types. 4) Route approval-required rows through the Approval Gate (governance-routing). 5) Record every dispatch decision and result. / 1）盘点动作类型及可承接工具；2）填写分派表（目标、schema、权限、副作用等级、审批挂钩）；3）在分派前接入 schema 校验，并为未知类型设默认安全路径；4）需审批的表项路由经审批门禁（governance-routing）；5）记录每次分派决策与结果。
- 输入 / Inputs: Pending action with type and parameters, dispatch table, tool capability declarations and schemas, caller identity and permission scope. / 带类型与参数的待执行动作、分派表、工具能力声明与 schema、调用方身份与权限范围。
- 输出 / Outputs: Dispatch decision record (action, target, rule hit), validated tool invocation, execution result written back to state, rejection or approval-escalation events. / 分派决策记录（动作、目标、命中规则）、经校验的工具调用、写回状态的执行结果、拒绝或审批升级事件。
- 风险与治理 / Risks & Governance: Wrong tool selection `FAIL_0003` — require capability match before dispatch and audit bounce-backs; parameter hallucination `FAIL_0004` — schema-validate every call and return diffs instead of silently repairing; permission bypass `FAIL_0005` when side-effect class is underestimated — classify conservatively and route doubtful actions to the approval hook per `GOV_0001`; execution stays inside sandbox boundaries per `GOV_0003` and all results are recorded per `GOV_0002`. / 工具选择错误 `FAIL_0003`——分派前强制能力匹配并审计弹回；参数幻觉 `FAIL_0004`——每次调用做 schema 校验，返回差异而非静默修补；副作用等级被低估导致权限绕过 `FAIL_0005`——保守分级，存疑动作按 `GOV_0001` 走审批挂钩；执行按 `GOV_0003` 留在沙箱边界内，全部结果按 `GOV_0002` 入账。

Observability Metrics File / 可观测性指标文件: [action-routing-observability.md](action-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
