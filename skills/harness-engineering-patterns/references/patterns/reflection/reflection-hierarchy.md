# Experience Replay / 经验回放

Cell / 交织点: reflection-hierarchy / 反思 x 层级
Capability / 能力: Reflection / 反思
Mode / 模式: Hierarchy / 层级
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Experience Replay reviews past execution records in tiers — action-level replay after each run, task-level replay at milestones, version-level replay at release or incident boundaries — and distills each tier's lessons into rules, checklists, or memory entries that constrain the next round of work. / 经验回放分层回看过往执行记录——每次运行后做动作级回放、里程碑处做任务级回放、发布或事故边界做版本级回放——并把每层教训提炼为规则、检查清单或记忆条目，约束下一轮工作。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reflection / 反思 x Hierarchy / 层级 (Hierarchy / 层级).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Reflection / 反思 x Hierarchy / 层级 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Reflection / 反思 x Hierarchy / 层级 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: Execution records pile up but are never replayed at the right granularity: single-run mistakes repeat because no action-level review happens, systemic patterns stay invisible because nobody aggregates across tasks, and version-scale lessons evaporate at release boundaries — the same incidents recur with fresh surprise. / 执行记录不断堆积却从未在合适粒度上被回放：没有动作级复盘导致单次错误重犯、没人跨任务聚合导致系统性模式不可见、版本尺度的教训在发布边界蒸发——同样的事故一再复发且每次都"意外"。
- 架构方案 / Architectural Solution: Run replay in stacked tiers, each with its own trigger, input records, and output artifact: action-level replay after each run distills per-step corrections, task-level replay at milestones aggregates action lessons into checklists, version-level replay at release or incident boundaries distills rules and policy changes; lessons flow into rules, checklists, and memory entries (the Failure Diary in memory-loop stores them; this pattern is the reflection-side tiered consumer that produces and re-reads them). / 分层叠放回放，每层有各自触发时机、输入记录与产物：每次运行后的动作级回放提炼逐步修正、里程碑处的任务级回放把动作教训聚合为检查清单、发布或事故边界的版本级回放提炼规则与策略变更；教训流入规则、检查清单与记忆条目（memory-loop 的失败日记负责存储，本模式是反思侧的分层生产者与消费者）。
- 工程权衡 / Engineering Trade-offs: Tiered replay catches patterns invisible at any single level, but each tier costs review effort and depends on complete audit records — replay over gappy logs produces confident but wrong lessons, and dumping every lesson back into context unfiltered pollutes future runs. / 分层回放能捕捉任何单层都看不见的模式，但每层都要花复盘投入，且依赖完整审计记录——在有缺口的日志上回放会得出自信却错误的教训，而把所有教训不加过滤地回灌上下文又会污染后续运行。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when reflection needs replay across levels of past attempts or lessons. / 当反思需要跨多层历史尝试或经验回放时使用。

### Replay Tier Model / 回放层级模型

| Tier / 层级 | Trigger Timing / 触发时机 | Input Records / 输入记录 | Output Artifacts / 产物 |
| --- | --- | --- | --- |
| Action-level / 动作级 | After each run or repair. / 每次运行或修复后。 | Step ledger, verifier verdicts, fix attempts. / 步骤账本、验证器裁定、修复尝试。 | Per-step corrections, failure-diary entries. / 逐步修正、失败日记条目。 |
| Task-level / 任务级 | At milestones or task closure. / 里程碑或任务关闭时。 | Action-level lessons, handoff records, rework counts. / 动作级教训、交接记录、返工次数。 | Checklists, task-template updates. / 检查清单、任务模板更新。 |
| Version-level / 版本级 | At release or incident boundaries. / 发布或事故边界。 | Task-level aggregates, incident timelines, gate outcomes. / 任务级聚合、事故时间线、门控结果。 | Rules, policy changes, threshold re-derivations. / 规则、策略变更、阈值重推。 |

Replay rules / 回放规则:

- Each tier consumes the tier below it, never raw records two levels down — action lessons feed task replay, task aggregates feed version replay. / 每层只消费下一层产物，绝不越两级读原始记录——动作教训喂任务回放，任务聚合喂版本回放。
- Lessons enter future context filtered and tiered, not as a bulk dump; storage lives in the Failure Diary (memory-loop) while this pattern owns when each tier reads and writes it. / 教训经过滤、分层进入后续上下文，而非整体倾倒；存储在失败日记（memory-loop），本模式负责各层何时读写。
- Replay quality is bounded by record completeness — audit gaps before trusting replayed conclusions. / 回放质量受记录完整性约束——先审计缺口再相信回放结论。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Experience Replay / 经验回放.
- 诊断用途 / Diagnostic Use: Use when reflection needs replay across levels of past attempts or lessons. / 当反思需要跨多层历史尝试或经验回放时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 治理审查、知识沉淀 / Governance review, knowledge memory.
- 当前症状 / Current Symptoms: The same mistakes recur across runs with no distilled lessons; postmortems happen only after major incidents and their conclusions never constrain daily work; execution logs exist but nobody reviews them at task or version granularity. / 同样的错误跨运行重复出现而没有提炼教训；只有重大事故后才复盘且结论从不约束日常工作；执行日志虽在，却无人按任务或版本粒度回看。
- 适配信号 / Fit Signals: 评估需要按任务、模块、版本或风险层级进行 / Evaluation happens by task, module, version, or risk level.
- 调整方向 / Adjustment Direction: Stack action, task, and version replay tiers, each distilling the tier below into rules, checklists, or memory entries. / 叠放动作、任务、版本三层回放，每层把下层提炼为规则、检查清单或记忆条目。
- 修改方式 / How To Modify: 1) Verify audit-record completeness per `GOV_0002` — replay is only as good as its inputs. 2) Define each tier's trigger, input records, and output artifact. 3) Wire action lessons into the Failure Diary (memory-loop) and task or version artifacts into checklists and rules. 4) Filter what re-enters future context by relevance tier. 5) Review replay conclusions before they become binding constraints. / 1）按 `GOV_0002` 核验审计记录完整性——回放质量以输入为上限；2）定义每层触发时机、输入记录与产物；3）动作教训接入失败日记（memory-loop），任务与版本产物接入检查清单与规则；4）按相关层级过滤回灌后续上下文的内容；5）回放结论成为约束前先经评审。
- 输入 / Inputs: Complete execution records (step ledgers, verdicts, incident timelines), tier definitions with triggers, Failure Diary storage, checklist and rule repositories. / 完整执行记录（步骤账本、裁定、事故时间线）、带触发时机的层级定义、失败日记存储、检查清单与规则库。
- 输出 / Outputs: Tiered lesson artifacts (corrections, checklists, rules), Failure Diary entries, replay reports with record-gap disclosures, threshold re-derivation proposals. / 分层教训产物（修正、清单、规则）、失败日记条目、附记录缺口披露的回放报告、阈值重推提议。
- 风险与治理 / Risks & Governance: Non-replayable audit `FAIL_0010` is the prerequisite risk — verify record completeness per `GOV_0002` before every replay and disclose gaps in conclusions; unfiltered lesson backfill pollutes future context `FAIL_0001` — inject lessons tiered and filtered, never as a bulk dump; version-level rule changes are policy-grade and go through review per `GOV_0001` before they bind. / 审计不可回放 `FAIL_0010` 是前置风险——每次回放前按 `GOV_0002` 核验记录完整性并在结论中披露缺口；教训不加过滤回灌会污染后续上下文 `FAIL_0001`——分层过滤注入，绝不整体倾倒；版本级规则变更属策略级，生效前按 `GOV_0001` 评审。

Observability Metrics File / 可观测性指标文件: [reflection-hierarchy-observability.md](reflection-hierarchy-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
