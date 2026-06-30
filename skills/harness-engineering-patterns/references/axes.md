# Axes / 轴定义

Use this file to map a workflow node onto capability and orchestration axes, or to decide whether the axes need extension. / 使用本文档将工作流节点映射到能力轴与编排轴，或判断是否需要扩展轴。

Source alignment: the initial axes follow the two-dimensional taxonomy in arXiv:2605.13850, adapted for workflow diagnosis. / 来源对齐：初始轴参考 arXiv:2605.13850 的二维分类，并调整为工作流诊断用途。

## Vertical Axis: Capabilities / 纵轴：能力

| Key | 中文 | English | Core Question / 核心问题 | Fit Signals / 适配信号 | Boundary / 边界 |
| --- | --- | --- | --- | --- | --- |
| perception | 感知 | Perception | What must be sensed before work can proceed? / 工作推进前必须感知什么？ | The workflow must observe, collect, parse, inspect, or normalize signals. / 工作流需要观察、采集、解析、检查或标准化信号。 | Not the same as judging or deciding. / 不等同于判断或决策。 |
| memory | 记忆 | Memory | What prior context must be retained or retrieved? / 哪些既有上下文必须保留或检索？ | The workflow depends on stored context, decisions, history, summaries, or reusable knowledge. / 工作流依赖已存上下文、决策、历史、摘要或可复用知识。 | Not the same as temporary context gathering. / 不等同于临时上下文采集。 |
| reasoning | 推理 | Reasoning | What must be inferred, decomposed, compared, or chosen? / 什么需要推断、拆解、比较或选择？ | The workflow decomposes, compares, diagnoses, plans, or chooses. / 工作流需要拆解、比较、诊断、规划或选择。 | Not the same as executing the chosen step. / 不等同于执行已选步骤。 |
| action | 行动 | Action | What state-changing operation must happen? / 哪些会改变状态的操作必须发生？ | The workflow changes code, data, systems, documents, tickets, or operational state. / 工作流会改变代码、数据、系统、文档、工单或运行状态。 | Not the same as preparing an action plan. / 不等同于准备行动方案。 |
| reflection | 反思 | Reflection | How does the workflow evaluate and improve itself? / 工作流如何评估并改进自身？ | The workflow checks outcomes, learns from results, evaluates quality, or revises assumptions. / 工作流检查结果、从结果学习、评估质量或修正假设。 | Not the same as one-time validation without learning. / 不等同于无学习的一次性验证。 |
| collaboration | 协作 | Collaboration | Which actors must coordinate or hand off? / 哪些参与者必须协同或交接？ | The workflow coordinates humans, agents, roles, reviewers, owners, or handoffs. / 工作流协调人、Agent、角色、评审者、负责人或交接。 | Not every message is collaboration; look for dependency between actors. / 不是所有消息都是协作，需存在参与者依赖。 |
| governance | 治理 | Governance | What control, safety, audit, or policy constraint must hold? / 哪些控制、安全、审计或策略约束必须成立？ | The workflow enforces policy, permission, auditability, safety, quality, or compliance. / 工作流执行策略、权限、审计、安全、质量或合规要求。 | Not the same as ordinary preference or style. / 不等同于普通偏好或风格。 |

## Horizontal Axis: Orchestration Modes / 横轴：编排模式

| Key | 中文 | English | Article Alias / 文章别名 | Fit Signals / 适配信号 | Boundary / 边界 |
| --- | --- | --- | --- | --- | --- |
| chain | 链式 | Chain | Sequential / 顺序 | Steps are ordered and each output feeds the next. / 步骤有顺序，前一步输出进入后一步。 | Weak when feedback or branching dominates. / 当反馈或分支占主导时不适合。 |
| routing | 路由 | Routing | Conditional branching / 条件分支 | Work is classified and sent to a tool, role, skill, path, or owner. / 工作被分类并分派到工具、角色、技能、路径或负责人。 | Not the same as a normal next step. / 不等同于普通下一步。 |
| parallel | 并行 | Parallel | Fan-out / 扇出 | Independent streams can run concurrently before merge or comparison. / 独立工作流可并发运行，再合并或比较。 | Requires independence or controlled merge. / 需要独立性或可控合并。 |
| orchestration | 编排 | Orchestration | Controller-mediated / 控制器协调 | A controller coordinates tools, agents, state, dependencies, and handoffs. / 控制器协调工具、Agent、状态、依赖和交接。 | Heavier than simple sequencing. / 比简单顺序流程更重。 |
| loop | 循环 | Loop | Iterative / 迭代 | The workflow repeats observe-act-check until an exit condition is met. / 工作流重复观察、行动、检查直到满足退出条件。 | Requires explicit iteration and stop condition. / 需要明确迭代和停止条件。 |
| hierarchy | 层级 | Hierarchy | Recursive or layered / 递归或分层 | Work is decomposed across levels such as strategy, plan, task, subtask, review. / 工作按战略、计划、任务、子任务、评审等层级拆解。 | Not the same as a long flat checklist. / 不等同于很长的平铺清单。 |

## Selection Heuristics / 选择启发

- Start with the capability question, then choose the smallest topology that fits. / 先回答能力问题，再选择足够表达问题的最小拓扑。
- Use routing when heterogeneity is high, parallelism when independence is high, orchestration when coordination burden is high, loop when feedback is required, and hierarchy when decomposition depth is high. / 异质性高用路由，独立性高用并行，协调负担高用编排，需要反馈用循环，拆解深度高用层级。
- Treat governance as a cross-cutting capability; if risk changes the path, map the primary cell to governance even if another capability performs the work. / 将治理视为横切能力；如果风险会改变路径，即使执行由其他能力完成，也优先映射到治理单元。

## Extension Record / 扩展记录格式

When adding an axis item, include: / 新增轴项时包含：

- Stable key / 稳定 key
- Chinese and English names / 中英文名
- Definition / 定义
- Fit signals / 适配信号
- Boundary against existing axes / 与现有轴项的边界
- Affected matrix cells / 受影响的交织点
