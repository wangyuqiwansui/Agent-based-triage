# Failure Modes / 失败模式

Use this file when naming risks, checking mitigations, or designing observability for a workflow, matrix cell, pattern, or Harness source component. / 当需要为工作流、矩阵单元、模式或 Harness 源码组件命名风险、检查缓解方式或设计可观测性时使用本文档。

## Failure Mode Library / 失败模式库

| Failure ID / 失败 ID | Failure Mode / 失败模式 | Common Coordinate / 常见坐标 | Symptom / 表现 | Mitigation / 缓解方式 |
| --- | --- | --- | --- | --- |
| `FAIL_0001` | Context Pollution / 上下文污染 | `COG_PERCEPTION__TOP_CHAIN` | Irrelevant information enters the prompt. / 无关信息进入 prompt。 | Context budget and relevance filtering. / 上下文预算与相关性过滤。 |
| `FAIL_0002` | Retrieval Miss / 检索遗漏 | `COG_PERCEPTION__TOP_ROUTING` | Key files or evidence are not retrieved. / 关键文件或证据未被检索。 | Multi-source retrieval and recall evaluation. / 多源检索与召回评估。 |
| `FAIL_0003` | Wrong Tool Selection / 工具误选 | `COG_ACTION__TOP_ROUTING` | The workflow calls the wrong tool. / 工作流调用了错误工具。 | Tool schema, router evaluation, and intent checks. / 工具 schema、路由评估与意图检查。 |
| `FAIL_0004` | Parameter Hallucination / 参数幻觉 | `COG_ACTION__TOP_ROUTING` | Tool parameters are invalid, missing, or dangerous. / 工具参数不存在、缺失或危险。 | Schema validation and pre-execution checks. / schema 校验与执行前检查。 |
| `FAIL_0005` | Permission Bypass / 权限绕过 | `COG_GOVERNANCE__TOP_ROUTING` | High-risk action proceeds without approval. / 高风险动作未审批就继续。 | Policy gate and explicit approval. / 策略门禁与显式审批。 |
| `FAIL_0006` | State Loss / 状态丢失 | `COG_MEMORY__TOP_CHAIN` | Long-running work cannot resume. / 长任务无法恢复。 | Event log, snapshot, and resumable progress records. / 事件日志、快照与可恢复进度记录。 |
| `FAIL_0007` | Runaway Loop / 循环失控 | `COG_REFLECTION__TOP_LOOP` | Retry or repair never exits. / 重试或修复无法退出。 | Max iteration, stop condition, and escalation. / 最大迭代、停止条件与升级处理。 |
| `FAIL_0008` | Unclear Subagent Boundary / 子 Agent 边界不清 | `COG_COLLABORATION__TOP_HIERARCHY` | Context leaks or responsibilities blur. / 上下文泄漏或职责混乱。 | Task contract and context scope. / 任务契约与上下文范围。 |
| `FAIL_0009` | Sandbox Escape / 沙箱逃逸 | `COG_GOVERNANCE__TOP_ORCHESTRATION` | Execution crosses intended boundaries. / 执行越过预期边界。 | Sandbox policy and capability limits. / 沙箱策略与能力限制。 |
| `FAIL_0010` | Non-Replayable Audit / 审计不可复现 | `COG_MEMORY__TOP_CHAIN` | The process cannot be replayed. / 过程无法回放。 | Append-only event log and evidence references. / 追加式事件日志与证据引用。 |
| `FAIL_0011` | Approval Fatigue / 审批疲劳 | `COG_GOVERNANCE__TOP_ROUTING` | Too many low-risk actions route to human gates; reviewers rubber-stamp and the gate stops catching real risk. / 过多低风险动作进入人工门禁；审批者机械放行，门禁不再拦截真实风险。 | Tune Deny/Allow/Gate thresholds by reversibility x impact; watch per-reviewer fire rate and time-to-approve. / 按可逆性 x 影响调整拒绝/放行/门禁阈值；监控单审批者触发频率与审批耗时。 |
| `FAIL_0012` | Context Starvation / 上下文饥饿 | `COG_PERCEPTION__TOP_ROUTING` | Over-aggressive filtering drops evidence the task needs; downstream steps reason from an incomplete picture. / 过度过滤丢弃任务所需证据；下游步骤基于不完整画面推理。 | Track filter rejection rate and downstream rework; keep a retrieval escape hatch to re-admit dropped context. / 追踪过滤拒绝率与下游返工；保留检索逃生通道以重新引入被丢弃的上下文。 |
| `FAIL_0013` | Aggregation Bottleneck / 聚合瓶颈 | `COG_COLLABORATION__TOP_PARALLEL` | Parallel workers finish but synthesis flattens, contradicts, or drops their findings; fan-out cost buys no quality. / 并行工作者完成后，综合环节压平、矛盾或丢失其发现；扇出成本换不来质量。 | Name a synthesis owner with output contracts and conflict rules; measure synthesis fidelity against worker outputs. / 指定综合负责人并定义输出契约与冲突规则；用综合保真度对照工作者产出度量。 |

## Use In Recommendations / 在建议中使用

For each recommended pattern adjustment, name at least one likely failure mode, explain why it matters, and attach a mitigation or observability probe. / 对每条模式调整建议，至少命名一个可能失败模式，说明其影响，并附上缓解方式或可观测性探针。
