# Self-Heal Loop / 自愈循环

Cell / 交织点: reflection-loop / 反思 x 循环
Capability / 能力: Reflection / 反思
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Self-Heal Loop auto-iterates repair for objectively verifiable failures: run the external verifier, parse the failure signature, apply a targeted fix, and re-run the verifier — exiting only when the verifier passes or the attempt budget forces escalation to a human. / 自愈循环对可客观验证的失败自动迭代修复：运行外部验证器、解析失败特征、实施定向修复、再次运行验证器——只有验证器通过才退出，或尝试预算耗尽而升级人工。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reflection / 反思 x Loop / 循环 (Loop / 循环).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; 矩阵列名模式 / Matrix-listed pattern; the article grounds self-healing loops that repair objectively verifiable failures until an external verifier passes; source table maps Reflection / 反思 x Loop / 循环 in arXiv:2605.13850. / 代表性定义 / Representative definition；矩阵列名模式 / Matrix-listed pattern；论文以"修复可客观验证的失败直到外部验证器通过"落定自愈循环；来源表将 Reflection / 反思 x Loop / 循环 映射到该单元。
- 问题 / Problem: Verification failures that always round-trip through a human waste the cheapest repair window — most test, schema, and runtime failures carry enough signal for mechanical repair — while unbounded self-repair thrashes, burns budget, and can quietly break items that already passed. / 验证失败每次都绕经人工，浪费了最便宜的修复窗口——大多数测试、schema 与运行时失败携带的信号足以支撑机械修复——而无界的自我修复又会空转震荡、烧掉预算，还可能悄悄破坏已通过的项目。
- 架构方案 / Architectural Solution: Loop verify-diagnose-fix against an external deterministic verifier (test suite, schema validator, runtime check): parse the failure signature, apply the smallest targeted fix, re-run the verifier; exit only on verifier pass, enforce a max-attempt budget with human escalation carrying full attempt history, and arm a regression guard so fixes never break previously passing items. / 围绕外部确定性验证器（测试套件、schema 校验器、运行时检查）循环"验证-诊断-修复"：解析失败特征、实施最小定向修复、重跑验证器；只有验证器通过才退出，强制最大尝试预算、超限带全部尝试历史升级人工，并布置回归护栏保证修复不破坏已通过项。
- 工程权衡 / Engineering Trade-offs: The deterministic verifier-pass exit separates it from Generator-Critic (reflection-chain), which converges on subjective critique in one or two passes; self-heal buys autonomous repair but only for verifier-decidable failures — applying it to judgment-quality issues loops indefinitely, and every retry costs a full verify-fix round. / 确定性"验证器通过"退出条件把它与一两轮主观评审即收敛的生成者-评审者（reflection-chain）区分开；自愈换来自主修复，但只适用于验证器可裁定的失败——套在判断型质量问题上会无限循环，且每次重试都要花一整轮验证-修复成本。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when verification failure should drive repair until an external check passes. / 当验证失败应驱动修复直到外部检查通过时使用。

### Verifier Loop Contract / 验证器循环契约

```yaml
verifier: external_deterministic_check       # 测试套件、schema 校验器、运行时检查 / test suite, schema validator, runtime check
exit_condition: verifier_pass                # 唯一退出条件：验证器判定通过，绝非自评 / sole exit: verifier verdict, never self-assessment
failure_signature: case_error_location       # 解析失败用例、错误类别、位置 / parsed failing case, error class, location
fix_attempt:
  scope: smallest_change_for_signature       # 针对失败特征的最小修改 / smallest change addressing the signature
  forbidden: weaken_verifier                 # 禁止删测试、放宽 schema / never delete tests or loosen schemas
max_attempts: per_failure_class_bound        # 每类失败的硬上限，超限即 FAIL_0007 / hard bound per class; exceeding is FAIL_0007
escalation: human_with_attempt_history       # 升级人工并附全部尝试历史 / escalate with the full attempt history
regression_guard: passing_items_stay_green   # 已通过项必须保持绿灯 / previously passing items must stay green
loop_log: every_round_per_GOV_0002           # 每轮按 GOV_0002 入账 / every round recorded per GOV_0002
```

Loop rules / 循环规则:

- The exit condition is the verifier's verdict, never the agent's self-assessment; failures without a deterministic verifier route to Generator-Critic (reflection-chain) instead. / 退出条件是验证器的裁定而非智能体自评；没有确定性验证器的失败改走生成者-评审者（reflection-chain）。
- Repairing by weakening the check is forbidden — the verifier definition is owned outside the loop and changes to it follow the normal review path. / 禁止靠削弱检查来修复——验证器定义归循环之外所有，其变更走正常评审路径。
- Repairs run inside sandbox boundaries per `GOV_0003`; only verifier-passing changes promote outward. / 修复按 `GOV_0003` 在沙箱边界内进行；只有验证器通过的变更才向外晋级。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Self-Heal Loop / 自愈循环.
- 诊断用途 / Diagnostic Use: Use when verification failure should drive repair until an external check passes. / 当验证失败应驱动修复直到外部检查通过时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 验证测试、事故修复 / Verification, incident repair.
- 当前症状 / Current Symptoms: Test or validation failures always round-trip through a human even when the fix is mechanical; repair attempts thrash with no attempt bound; a fix lands but breaks other passing checks and nobody notices until later. / 测试或校验失败即使修复是机械性的也总要绕经人工；修复尝试没有次数上限而空转震荡；修复落地却破坏了其他已通过检查，直到很晚才被发现。
- 适配信号 / Fit Signals: 反思结果不断驱动下一轮修正直到达标 / Reflection repeatedly drives correction until criteria are met.
- 调整方向 / Adjustment Direction: Wrap objectively verifiable failures in a bounded verifier loop: deterministic pass exit, attempt budget, escalation with history, regression guard. / 用有界验证器循环包裹可客观验证的失败：确定性通过退出、尝试预算、带历史升级、回归护栏。
- 修改方式 / How To Modify: 1) Identify failure classes with a deterministic external verifier; route the rest to Generator-Critic (reflection-chain). 2) Define the failure-signature parser and smallest-fix policy. 3) Set max attempts per class and the escalation package (attempt history included). 4) Arm the regression guard over previously passing items. 5) Record every round per `GOV_0002`. / 1）识别拥有确定性外部验证器的失败类，其余走生成者-评审者（reflection-chain）；2）定义失败特征解析与最小修复策略；3）为每类设最大尝试次数与升级包（附尝试历史）；4）对已通过项布置回归护栏；5）每轮按 `GOV_0002` 入账。
- 输入 / Inputs: Failing verifier report with failure signature, repairable artifact, verifier command and pass criteria, attempt budget, sandbox environment. / 带失败特征的验证器失败报告、可修复产物、验证器命令与通过标准、尝试预算、沙箱环境。
- 输出 / Outputs: Verifier-passing artifact, per-round loop log (signature, fix, verdict), escalation package when the budget is exhausted, regression-guard verdicts. / 通过验证器的产物、每轮循环日志（特征、修复、裁定）、预算耗尽时的升级包、回归护栏裁定。
- 风险与治理 / Risks & Governance: Runaway repair `FAIL_0007` — enforce the max-attempt bound and escalate with history instead of looping on; verifier weakening disguised as repair — forbid loop-side edits to the verifier; repairs stay inside sandbox boundaries per `GOV_0003`; every round's signature, fix, and verdict is recorded per `GOV_0002` so the escalated human replays the loop instead of restarting it. / 修复失控 `FAIL_0007`——强制最大尝试上限，超限带历史升级而非继续循环；以削弱验证器伪装修复——禁止循环侧修改验证器；修复按 `GOV_0003` 留在沙箱边界内；每轮特征、修复与裁定按 `GOV_0002` 入账，升级后的人工可回放循环而非从头再来。

Observability Metrics File / 可观测性指标文件: [reflection-loop-observability.md](reflection-loop-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
