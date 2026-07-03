# Plan-and-Execute / 计划并执行 Observability Metrics / 可观测性指标

Cell / 交织点: action-orchestration / 行动 x 编排
Capability / 能力: Action / 行动
Mode / 模式: Orchestration / 编排
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [action-orchestration.md](action-orchestration.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Plan-and-Execute / 计划并执行 improves the workflow after selection or application. / 使用以下指标观察 Plan-and-Execute / 计划并执行 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `plan_completion_rate` (subtasks meeting done criteria without rework), `decomposition_fitness` (share of subtasks that needed neither splitting nor merging during execution), and goal acceptance after final synthesis. / `plan_completion_rate`（无返工满足完成判据的子任务比例）、`decomposition_fitness`（执行中既不需再拆也不需合并的子任务占比）、最终合成后的目标采纳率。
- 时延指标 / Latency Metrics: planning latency (goal to plan artifact), critical-path execution time versus sum of subtask times (parallelism gain), and replan turnaround. / 规划时延（目标到计划产物）、关键路径执行时间对比子任务时间总和（并行收益）、重规划周转时间。
- 成本指标 / Cost Metrics: coordination overhead ratio (planner plus coordinator tokens over executor tokens), wasted work from discarded plans, and compensation-action spend. / 协调开销比（规划器加协调器 token 除以执行器 token）、被废弃计划造成的浪费、补偿动作花销。
- 风险指标 / Risk Metrics: subtasks completed on self-report without observable criteria, state-changing subtasks lacking compensation, replan count hitting stop conditions, and high-risk subtasks bypassing the approval gate. / 仅凭自述、无可观测判据即判完成的子任务数；缺补偿的改状态子任务数；触达停止条件的重规划次数；绕过审批门禁的高风险子任务数。
- Trace 指标 / Trace Metrics: plan artifact versioning (every replan preserved), per-subtask execution record completeness, and compensation log coverage for failed branches. / 计划产物版本化（每次重规划留存）、逐子任务执行记录完整率、失败分支的补偿日志覆盖率。

### Default Gate Suggestions / 默认门控建议

- Block completion marking when `done_criteria` is empty for a state-changing subtask. / 改状态子任务 `done_criteria` 为空时阻止标记完成。
- Alert when replan count reaches the stop condition — the plan model no longer matches reality (`FAIL_0006` risk if progress records are also missing). / 重规划次数触达停止条件时告警——计划模型已与现实脱节（若进度记录同时缺失则有 `FAIL_0006` 风险）。
