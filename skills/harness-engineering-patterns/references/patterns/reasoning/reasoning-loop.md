# Iterative Hypothesis Testing / 迭代假设测试

Cell / 交织点: reasoning-loop / 推理 x 循环
Capability / 能力: Reasoning / 推理
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Iterative Hypothesis Testing alternates hypothesis generation with evidence gathering: the agent probes the environment, observes results, updates hypothesis confidence, and repeats until a hypothesis is confirmed, refuted, or the budget is exhausted. / 迭代假设测试让假设生成与证据收集交替进行：智能体探测环境、观察结果、更新假设置信度，如此往复，直到假设被确认、被证伪或预算耗尽。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reasoning / 推理 x Loop / 循环 (Loop / 循环).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; 矩阵列名模式 / Matrix-listed pattern; source table maps Reasoning / 推理 x Loop / 循环 in arXiv:2605.13850. The article describes probe-observe-adjust cycles through environment interaction, and its lending case uses the pattern to probe financial-statement anomalies. / 代表性定义 / Representative definition；矩阵列名模式 / Matrix-listed pattern；来源表将 Reasoning / 推理 x Loop / 循环 映射到该单元。论文描述通过环境交互进行探测-观察-调整循环，其 lending 案例用该模式探查财务报表异常。
- 问题 / Problem: One-shot reasoning cannot resolve questions whose answer depends on evidence that only appears after interacting with the environment. / 一次性推理无法解决那些答案依赖于与环境交互后才出现的证据的问题。
- 架构方案 / Architectural Solution: Maintain a hypothesis register with prior confidence and a discriminating experiment per hypothesis; run the cheapest discriminating probe first, update confidence from observations with recorded reasons, and loop until an exit condition fires. / 维护假设台账，每个假设带先验置信与判别性实验；优先执行最便宜的判别性探测，根据观察带原因更新置信度，循环直到退出条件触发。
- 工程权衡 / Engineering Trade-offs: The slowest reasoning topology — every iteration pays probe latency and tokens — but the only one that grounds conclusions in fresh environment evidence; without hard exit conditions it degenerates into runaway retries (`FAIL_0007`). / 最慢的推理拓扑——每轮迭代都付出探测时延和 token——但也是唯一让结论落在新鲜环境证据上的拓扑；没有硬退出条件就会退化为失控重试（`FAIL_0007`）。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when reasoning must revise hypotheses after evidence or tests. / 当推理必须根据证据或测试修正假设时使用。

### Hypothesis Loop Contract / 假设循环契约

```yaml
hypothesis_loop:
  hypothesis_register:
    - hypothesis: ""            # falsifiable statement / 可证伪陈述
      prior_confidence: ""      # low | medium | high / 低 | 中 | 高
      discriminating_probe: ""  # cheapest experiment separating it from rivals / 能将它与竞争假设区分开的最便宜实验
  probe_rules:
    order: cheapest_discriminating_first          # 最便宜且最有判别力的探测优先
    evidence_update: record_observation_then_adjust_confidence_with_reason  # 先记录观察，再带原因升降置信度
  exit_conditions:
    confirmed: one hypothesis passes its probe and rivals are refuted / 一个假设通过探测且竞争假设被证伪
    refuted_all: hypothesis space exhausted, escalate with evidence trail / 假设空间耗尽，携证据链升级
    budget_exhausted: iteration or token budget hit, report best surviving hypothesis / 迭代或 token 预算触顶，报告最优存活假设
  max_iterations: 0             # hard cap against FAIL_0007 / 防 FAIL_0007 的硬上限
  loop_log: probe, observation, confidence delta per iteration / 每轮记录探测、观察、置信度变化
```

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Iterative Hypothesis Testing / 迭代假设测试.
- 诊断用途 / Diagnostic Use: Use when reasoning must revise hypotheses after evidence or tests. / 当推理必须根据证据或测试修正假设时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 验证测试、事故修复 / Verification, incident repair.
- 当前症状 / Current Symptoms: Root-cause analysis fixates on the first plausible explanation without testing it; the same failed fix is retried with no new evidence; long debugging sessions leave no record of which hypotheses were eliminated and why. / 根因分析固守第一个貌似合理的解释而不测试；同一失败修复在没有新证据下被反复重试；漫长排障后没有任何"哪些假设被排除、为何被排除"的记录。
- 适配信号 / Fit Signals: 推理需要根据验证结果持续修正 / Reasoning must revise itself based on verification results.
- 调整方向 / Adjustment Direction: Make hypotheses explicit and falsifiable, and let the cheapest discriminating probe — not intuition — decide which survives. / 显式化、可证伪化假设，让最便宜的判别性探测而非直觉决定哪个假设存活。
- 修改方式 / How To Modify: 1) Write 2-4 rival hypotheses with prior confidence into the register. 2) Design the cheapest discriminating probe for each. 3) Loop probe, observe, update confidence, logging each iteration. 4) Set max_iterations and the three exit conditions before starting. 5) On exhaustion, escalate with the evidence trail instead of guessing. / 1）把 2-4 个竞争假设连同先验置信写入台账；2）为每个假设设计最便宜的判别性探测；3）循环"探测、观察、更新置信度"并逐轮记录；4）开始前设定 max_iterations 与三类退出条件；5）耗尽时携证据链升级而不是猜测。
- 输入 / Inputs: Failure or question statement, hypothesis register, probe toolset with permissions, iteration and token budget. / 失败或问题陈述、假设台账、带权限的探测工具集、迭代与 token 预算。
- 输出 / Outputs: Confirmed or best-surviving hypothesis with confidence, per-iteration loop log, eliminated hypotheses with refuting evidence, escalation package on exhaustion. / 带置信度的已确认或最优存活假设、逐轮循环日志、带证伪证据的被排除假设、耗尽时的升级包。
- 风险与治理 / Risks & Governance: Runaway retries without new evidence (`FAIL_0007`) — enforce max_iterations and require each iteration to add evidence rather than repeat the last probe; unlogged iterations make the conclusion unauditable — write the loop log per `GOV_0002`; probes that mutate the environment must run inside sandbox boundaries per `GOV_0003`. / 无新证据的失控重试（`FAIL_0007`）——强制 max_iterations 并要求每轮新增证据而非重复上一次探测；不记录迭代会让结论不可审计——循环日志按 `GOV_0002` 入账；会改变环境的探测必须按 `GOV_0003` 在沙箱边界内运行。

Observability Metrics File / 可观测性指标文件: [reasoning-loop-observability.md](reasoning-loop-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
