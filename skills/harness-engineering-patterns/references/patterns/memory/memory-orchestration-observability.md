# Progress Tracking / 进度追踪 Observability Metrics / 可观测性指标

Cell / 交织点: memory-orchestration / 记忆 x 编排  
Capability / 能力: Memory / 记忆  
Mode / 模式: Orchestration / 编排  
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850), adapted as an engineering workflow pattern / 来源于 arXiv:2605.13850，并调整为工程工作流模式  
Design Pattern File / 设计模式文件: [memory-orchestration.md](memory-orchestration.md)

Use this file to observe whether Progress Tracking is actually controlling a long-running workflow, rather than merely producing status text. / 使用本文档观察进度追踪是否真的在控制长程工作流，而不只是生成状态文字。

## Observability Metrics / 可观测性指标

Use these metric groups to measure the effect of Progress Tracking after it is selected or applied. / 选择或应用进度追踪后，使用以下指标组衡量效果。

- 质量指标 / Quality Metrics: Track goal coverage, milestone acceptance pass rate, evidence-backed conclusions, recovery-package usability, and rework rate. / 跟踪目标覆盖率、里程碑验收通过率、有证据支撑的结论、恢复包可用性和返工率。
- 时延指标 / Latency Metrics: Track time from task intake to goal freeze, milestone cycle time, blocker resolution time, probe turnaround time, and handoff resume time. / 跟踪从任务接入到目标冻结的耗时、里程碑周期、阻塞解决时间、探针周转时间和交接续跑时间。
- 成本指标 / Cost Metrics: Track state-maintenance overhead, tool calls, human review effort, repeated context reconstruction avoided, and duplicated work avoided. / 跟踪状态维护成本、工具调用、人工复核投入、避免的重复上下文重建和避免的重复工作。
- 风险指标 / Risk Metrics: Track unknown-gate continuation, unbound mechanical truth, evidence-free completion, high-risk actions without review, and state conflicts. / 跟踪未知闸门继续、未绑定机械真值、无证据完成、未复核高风险动作和状态冲突。
- Trace 指标 / Trace Metrics: Track ledger completeness, probe backfill completion, correction events, acceptance records, and whether follow-up actions close. / 跟踪账本完整性、探针回填完成度、纠偏事件、验收记录和后续动作是否关闭。

## Observation Goal / 观测目标

The observability side must answer seven questions: / 可观测性侧必须回答七个问题：

```text
1. Is the goal contract stable and current? / 目标契约是否稳定且为当前版本？
2. Is the current milestone known and moving? / 当前里程碑是否明确且正在推进？
3. Are critical truths stored in mechanical state with sources? / 关键真值是否带来源写入机械态？
4. Is the progress ledger append-only and evidence-backed? / 进度账本是否只追加且有证据支撑？
5. Are gates stopping unsafe continuation? / 闸门是否阻止了不安全继续？
6. Are probe results backfilled into execution state? / 探针结果是否回填到执行状态？
7. Can another executor resume from the recovery package? / 新接手者是否能通过恢复包续跑？
```

If any answer is unknown, the health level cannot be normal. / 如果任一答案未知，健康等级不能是正常。

## Health Levels / 健康等级

| Level / 等级 | Meaning / 含义 | Required Action / 必要动作 |
| --- | --- | --- |
| Normal / 正常 | Goal, state, evidence, gates, probes, and recovery are coherent. / 目标、状态、证据、闸门、探针和恢复一致。 | Continue and monitor. / 继续并观察。 |
| Observe / 观察 | Minor gap or drift exists, but no critical action is exposed. / 存在轻微缺口或漂移，但未暴露关键动作。 | Request probe or tighten working set. / 请求探针或收紧工作集。 |
| Correct / 回正 | State conflict, weak evidence, stalled milestone, or missing mechanical truth affects next action. / 状态冲突、证据薄弱、里程碑停滞或机械真值缺失影响下一步。 | Backfill, correct state, or return to a milestone. / 回填、纠偏或回到里程碑。 |
| Pause / 暂停 | High-risk action, unknown acceptance, missing recovery, or repeated failure makes continuation unsafe. / 高风险动作、验收未知、恢复缺失或重复失败使继续不安全。 | Block, review, or rework before continuing. / 继续前阻塞、复核或返工。 |

## Core Metrics / 核心指标

| Metric Group / 指标组 | What To Measure / 观测内容 | Healthy Signal / 健康信号 |
| --- | --- | --- |
| Goal integrity / 目标完整性 | Goal contract exists, version is current, success criteria and non-goals are explicit. / 目标契约存在、版本当前、成功标准和非目标明确。 | No execution before goal freeze. / 目标冻结前不执行。 |
| Milestone progress / 里程碑推进 | Current milestone, ready items, blockers, rework items, and acceptance state. / 当前里程碑、就绪项、阻塞项、返工项和验收状态。 | Each milestone has entry and acceptance conditions. / 每个里程碑都有进入和验收条件。 |
| Mechanical truth / 机械真值 | Critical values, sources, trust level, last read/write position. / 关键值、来源、信任等级、最近读写位置。 | Critical actions read truth from mechanical state. / 关键动作从机械态读取真值。 |
| Evidence health / 证据健康 | Evidence references, freshness, reliability, conflict status. / 证据引用、新鲜度、可靠性、冲突状态。 | Key conclusions cite evidence. / 关键结论有证据引用。 |
| Gate behavior / 闸门行为 | Pre-execution checks, acceptance checks, blocked continuations, review escalation. / 执行前检查、验收检查、阻断继续、升级复核。 | Unknown confirmations stop progress. / 未知确认项会阻止推进。 |
| Probe loop / 探针闭环 | Probe requests, results, backfill target, backfill completion. / 探针请求、结果、回填目标、回填完成情况。 | Probe results change task state. / 探针结果会改变任务状态。 |
| Recovery quality / 恢复质量 | Recovery package completeness, next action clarity, forbidden actions, current working set. / 恢复包完整性、下一步清晰度、禁止动作、当前工作集。 | Handoff can resume without full history. / 接手者无需完整历史即可续跑。 |

## Probe Catalog / 探针目录

Use these probes independently or as a coordinated observation pass. / 可独立使用以下探针，也可组合成一次观测。

### 1. Goal Contract Probe / 目标契约探针

- Checks / 检查: original goal, success criteria, non-goals, constraints, high-risk actions, version. / 原始目标、成功标准、非目标、约束、高风险动作、版本。
- Warning / 警告: execution started while goal contract is missing or outdated. / 目标契约缺失或过期时已开始执行。
- Backfill / 回填: goal contract, recovery package, progress ledger. / 目标契约、恢复包、进度账本。

### 2. Milestone Progress Probe / 里程碑推进探针

- Checks / 检查: current milestone, status, entry conditions, acceptance conditions, blockers, ready items. / 当前里程碑、状态、进入条件、验收条件、阻塞项、就绪项。
- Warning / 警告: progress events accumulate but no milestone state changes. / 进度事件增加但里程碑状态不变。
- Backfill / 回填: scheduling state, blocker list, next action. / 调度态、阻塞清单、下一步动作。

### 3. Mechanical State Probe / 机械态探针

- Checks / 检查: required IDs, amounts, accounts, paths, versions, dates, ranges, approvals, environments, tenants. / 必要编号、金额、账号、路径、版本、日期、范围、审批、环境、租户。
- Warning / 警告: critical values appear only in narrative text, not mechanical state. / 关键值只出现在叙事文本中，未进入机械态。
- Backfill / 回填: mechanical-state index and forbidden actions. / 机械态索引和禁止动作。

### 4. Evidence Health Probe / 证据健康探针

- Checks / 检查: evidence source, freshness, conflict, sufficiency, acceptance relevance. / 证据来源、新鲜度、冲突、充分性、验收相关性。
- Warning / 警告: key conclusion has no evidence reference or cites stale evidence. / 关键结论无证据引用或引用过期证据。
- Backfill / 回填: evidence references, ledger, acceptance record. / 证据引用、账本、验收记录。

### 5. Gate Compliance Probe / 闸门遵从探针

- Checks / 检查: pre-execution confirmation gate and milestone acceptance gate. / 执行前确认闸门和里程碑验收闸门。
- Warning / 警告: the workflow continued after an unknown confirmation, missing prerequisite, or high-risk boundary touch. / 在确认项未知、前置条件缺失或触碰高风险边界后仍继续。
- Backfill / 回填: pending review, blocked state, rework state, progress event. / 待复核、阻塞态、返工态、进度事件。

### 6. Probe Backfill Probe / 探针回填探针

- Checks / 检查: probe request, probe result, target location, state update, resulting next action. / 探针请求、探针结果、目标位置、状态更新、后续动作。
- Warning / 警告: probe returns a result but execution state is unchanged. / 探针返回结果但执行状态没有变化。
- Backfill / 回填: working set, mechanical state, ledger, blockers, next action. / 当前工作集、机械态、账本、阻塞项、下一步动作。

### 7. Recovery Integrity Probe / 恢复完整性探针

- Checks / 检查: goal contract, current milestone, working set, recent events, blockers, mechanical-state index, latest observation, next action, forbidden actions. / 目标契约、当前里程碑、当前工作集、最近事件、阻塞项、机械态索引、最新观测、下一步动作、禁止动作。
- Warning / 警告: recovery package cannot support handoff without full history. / 恢复包无法支持不翻完整历史的交接。
- Backfill / 回填: recovery package and archive package. / 恢复包和归档包。

### 8. Scope Drift Probe / 范围漂移探针

- Checks / 检查: current action against goal contract, non-goals, and milestone scope. / 用目标契约、非目标和里程碑范围检查当前动作。
- Warning / 警告: local detail is pulling execution into a non-goal. / 局部细节把执行拉入非目标。
- Backfill / 回填: next action, blocked item, goal-change event if the user approves a scope change. / 下一步动作、阻塞项；如用户批准范围变化，则追加目标变更事件。

### 9. Stagnation Probe / 停滞探针

- Checks / 检查: repeated events, repeated failures, unchanged blockers, unchanged acceptance state. / 重复事件、重复失败、阻塞项不变、验收状态不变。
- Warning / 警告: work is busy but not moving a milestone. / 工作很忙但没有推进里程碑。
- Backfill / 回填: narrower sub-goal, rework item, diagnostic event. / 更小子目标、返工项、诊断事件。

## Alert Rules / 告警规则

| Alert / 告警 | Trigger / 触发条件 | Health / 健康等级 |
| --- | --- | --- |
| Goalless execution / 无目标执行 | Any action runs before goal contract exists. / 目标契约存在前执行任何动作。 | Pause / 暂停 |
| Unbound critical truth / 未绑定关键真值 | Critical action depends on a value not found in mechanical state. / 关键动作依赖未进入机械态的值。 | Pause / 暂停 |
| Unknown gate continuation / 未知闸门继续 | Any pre-execution gate item is unknown and execution continues. / 任一执行前闸门项未知但继续执行。 | Pause / 暂停 |
| Evidence-free completion / 无证据完成 | Milestone or task marked complete without evidence references. / 里程碑或任务无证据引用即标记完成。 | Correct / 回正 |
| Probe orphan / 探针孤儿 | Probe result exists but no state was backfilled. / 探针结果存在但未回填状态。 | Correct / 回正 |
| Recovery gap / 恢复缺口 | Recovery package lacks current milestone, blockers, mechanical index, or next action. / 恢复包缺少当前里程碑、阻塞项、机械态索引或下一步。 | Correct / 回正 |
| Repeated failure / 重复失败 | Same failure pattern repeats without diagnostic event or changed next action. / 同类失败重复出现但无诊断事件或下一步变化。 | Pause / 暂停 |

## Observation Report Template / 观测报告模板

```text
Progress tracking observation / 进度追踪观测:
  Workflow / 工作流:
  Current milestone / 当前里程碑:
  Health level / 健康等级:
  Goal contract status / 目标契约状态:
  Mechanical-state status / 机械态状态:
  Evidence status / 证据状态:
  Gate status / 闸门状态:
  Probe status / 探针状态:
  Recovery status / 恢复状态:
  Abnormal signals / 异常信号:
    -
  Required backfill / 必须回填:
    -
  Recommended next action / 建议下一步:
  Forbidden until resolved / 解决前禁止:
    -
```

## Acceptance Metrics / 验收指标

Progress Tracking is working only when these are true: / 只有满足以下条件，进度追踪才算有效：

- The task cannot advance from an unknown or unsafe gate. / 任务不能从未知或不安全闸门继续推进。
- Every critical state value has a mechanical-state source. / 每个关键状态值都有机械态来源。
- Every milestone completion has evidence and acceptance records. / 每个里程碑完成都有证据和验收记录。
- Probe results cause visible state changes or explicit rejection reasons. / 探针结果会产生可见状态变化，或有明确拒绝回填理由。
- The recovery package is sufficient for handoff. / 恢复包足以支持交接。
- The final completion claim covers every success criterion. / 最终完成声明覆盖所有成功标准。

## Common Observation Failures / 常见观测失败

- Treating a status summary as a progress ledger. / 把状态摘要当成进度账本。
- Counting actions performed instead of acceptance conditions passed. / 统计已执行动作，而不是已通过的验收条件。
- Watching only narrative state while mechanical state is stale. / 只观察叙事态，机械态已经陈旧。
- Emitting probe recommendations without checking whether they were backfilled. / 只输出探针建议，不检查是否回填。
- Reporting "normal" when a gate answer is unknown. / 闸门答案未知时仍报告“正常”。
- Keeping recovery packages that require reading the full conversation. / 恢复包仍要求接手者阅读完整对话。
