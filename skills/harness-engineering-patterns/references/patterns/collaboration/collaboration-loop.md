# Adversarial Review / 对抗评审

Cell / 交织点: collaboration-loop / 协作 x 循环
Capability / 能力: Collaboration / 协作
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Adversarial Review pits an independent attacker against the artifact in repeated rounds — the attacker probes for exploitable findings, the author repairs, and the loop converges when the attacker finds no new findings within budget or the round bound forces escalation. / 对抗评审让独立攻击者对产物发起多轮攻击——攻击者探查可利用的发现、作者修复，当攻击者在预算内找不到新发现时收敛，或轮次上限触顶强制升级。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Collaboration / 协作 x Loop / 循环 (Loop / 循环).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; the article intro mentions the related adversarial-verification idea; source table maps Collaboration / 协作 x Loop / 循环 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；论文引言提及相关对抗验证思想；来源表将 Collaboration / 协作 x Loop / 循环 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: Friendly review shares the author's blind spots: a critic aligned with the same improvement direction confirms the design instead of breaking it, so exploitable flaws — edge cases, abuse paths, unstated assumptions — survive review and surface in production where repair is most expensive. / 友好评审共享作者的盲区：与作者同一改进方向的评审者是在确认设计而不是攻破设计，可被利用的缺陷——边界情况、滥用路径、未言明假设——因此穿过评审、在修复最昂贵的生产环境浮现。
- 架构方案 / Architectural Solution: Run review as bounded adversarial rounds: an attacker with an independent brief and isolated context probes a declared attack surface and files findings with severity and reproduction steps; the author repairs; the loop converges when a full attack round yields no new findings within budget, and hitting the round bound escalates the surviving findings instead of looping on. / 把评审跑成有界对抗轮次：持独立任务书、上下文隔离的攻击者在声明的攻击面上探查，提交带严重度与复现步骤的发现；作者修复；当完整攻击轮在预算内产出零新发现时收敛，触及轮次上限则带存活发现升级而非继续循环。
- 工程权衡 / Engineering Trade-offs: This differs from Generator-Critic (reflection-chain) — one or two critique passes sharing the improvement direction — by paying for an independent adversary perspective, multiple rounds, and a "no new findings" convergence proof; the price is attacker setup and round latency, worth it for high-stakes artifacts and wasted on drafts a single critique pass would fix. / 与生成者-评审者（reflection-chain）的一两轮同向评审不同，这里花钱买的是独立对抗视角、多轮攻防与"零新发现"收敛证明；代价是攻击者搭建成本与轮次时延，对高风险产物值得，对一轮评审就能修好的草稿则是浪费。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when collaborative critique repeats until conflict or risk is resolved. / 当协作式批评需要重复到冲突或风险解决时使用。

### Adversarial Round Contract / 对抗轮次契约

```yaml
attacker_brief: independent_break_mandate    # 独立任务书：找到能攻破产物的证据 / independent mandate: find what breaks the artifact
attack_surface: declared_scope               # 声明的攻击面与禁区 / declared in-scope surface and off-limits zones
context_isolation: no_author_rationale       # 攻击者不读作者辩护理由 / attacker never reads the author's rationale
finding:
  severity: blocker_major_minor              # 严重度分级 / severity classes
  reproduction: steps_or_evidence            # 复现步骤或证据，无复现不立案 / reproduction steps or evidence; no repro, no finding
repair: author_fix_per_finding               # 作者逐项修复并声明处置 / author repairs and declares disposition per finding
convergence_rule: zero_new_findings_in_round # 一整轮零新发现即收敛 / a full round with zero new findings converges
max_rounds: hard_bound_then_escalate         # 轮次硬上限，超限带存活发现升级 / hard bound; exceeding escalates surviving findings
round_log: per_GOV_0002                      # 每轮攻防按 GOV_0002 入账 / every round recorded per GOV_0002
```

Loop rules / 循环规则:

- The attacker's context is isolated from the author's: it sees the artifact and attack surface, never the author's rationale — otherwise it inherits the same blind spots it exists to break. / 攻击者上下文与作者隔离：只见产物与攻击面，不见作者辩护——否则会继承它本该攻破的盲区。
- Findings without reproduction steps do not count toward convergence or escalation; severity disputes resolve toward the more severe class. / 无复现步骤的发现不计入收敛或升级；严重度争议就高不就低。
- Convergence requires a full attack round, not attacker fatigue: budget per round is fixed up front so "no new findings" means the surface was probed, not that time ran out. / 收敛以完整攻击轮为准而非攻击者疲劳：每轮预算事先固定，"零新发现"意味着攻击面被探查过，而不是时间耗尽。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Adversarial Review / 对抗评审.
- 诊断用途 / Diagnostic Use: Use when collaborative critique repeats until conflict or risk is resolved. / 当协作式批评需要重复到冲突或风险解决时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 验证测试、事故修复 / Verification, incident repair.
- 当前症状 / Current Symptoms: Reviews consistently approve artifacts that later fail in production on edge cases or abuse paths; critics restate the author's framing instead of attacking it; high-stakes releases pass review in one pass with zero findings — a sign of confirmation, not verification. / 评审一致通过的产物随后在生产环境因边界情况或滥用路径失败；评审者复述作者框架而非攻击它；高风险发布一轮零发现即过审——这是确认而非验证的信号。
- 适配信号 / Fit Signals: 协作需要反复反馈、修改、确认直到达成条件 / Collaboration repeats feedback, revision, and confirmation until criteria are met.
- 调整方向 / Adjustment Direction: Replace friendly critique with bounded adversarial rounds: isolated attacker brief, reproducible findings, repair, and zero-new-findings convergence. / 用有界对抗轮次取代友好评审：隔离的攻击者任务书、可复现发现、修复、零新发现收敛。
- 修改方式 / How To Modify: 1) Reserve the pattern for high-stakes artifacts; drafts go to Generator-Critic (reflection-chain). 2) Write the attacker brief and declare the attack surface. 3) Isolate attacker context from author rationale. 4) Fix per-round budget, finding format (severity plus reproduction), and max rounds. 5) Record every round per `GOV_0002` and escalate surviving findings at the bound. / 1）本模式留给高风险产物，草稿走生成者-评审者（reflection-chain）；2）撰写攻击者任务书并声明攻击面；3）隔离攻击者上下文与作者辩护；4）固定每轮预算、发现格式（严重度加复现）与最大轮次；5）每轮按 `GOV_0002` 入账，触顶带存活发现升级。
- 输入 / Inputs: High-stakes artifact, attacker brief with declared attack surface, per-round budget, finding format, round bound, isolated attacker context. / 高风险产物、带声明攻击面的攻击者任务书、每轮预算、发现格式、轮次上限、隔离的攻击者上下文。
- 输出 / Outputs: Finding ledger (severity, reproduction, disposition), repaired artifact, convergence certificate (final round with zero new findings) or escalation package with surviving findings. / 发现台账（严重度、复现、处置）、修复后的产物、收敛证书（末轮零新发现）或带存活发现的升级包。
- 风险与治理 / Risks & Governance: Endless attack-repair cycling is `FAIL_0007` — the round bound forces escalation with surviving findings instead of looping; attacker-author context bleed is `FAIL_0008` — isolation keeps the adversary perspective independent; findings on out-of-surface zones route to approval per `GOV_0001` rather than silent expansion; every round's findings, repairs, and verdicts are recorded per `GOV_0002` so the convergence claim is auditable. / 攻防无止境循环是 `FAIL_0007`——轮次上限强制带存活发现升级而非继续循环；攻击者与作者上下文互渗是 `FAIL_0008`——隔离保证对抗视角独立；攻击面之外的发现按 `GOV_0001` 走审批而非默默扩面；每轮发现、修复与裁定按 `GOV_0002` 入账，收敛声明可被审计。

Observability Metrics File / 可观测性指标文件: [collaboration-loop-observability.md](collaboration-loop-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
