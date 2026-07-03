# Adversarial Review / 对抗评审 Observability Metrics / 可观测性指标

Cell / 交织点: collaboration-loop / 协作 x 循环
Capability / 能力: Collaboration / 协作
Mode / 模式: Loop / 循环
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [collaboration-loop.md](collaboration-loop.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Adversarial Review / 对抗评审 improves the workflow after selection or application. / 使用以下指标观察 Adversarial Review / 对抗评审 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `finding_yield_per_round` (new reproducible findings per attack round — should decay toward zero as the loop converges), `post_release_escape_rate` (defects surfacing in production after a convergence certificate — the pattern's core success measure), and `finding_reproduction_rate` (filed findings that actually reproduce). / `finding_yield_per_round`（每攻击轮的新可复现发现数——收敛时应衰减到零）、`post_release_escape_rate`（收敛证书发出后仍在生产逃逸的缺陷率——本模式核心成效指标）、`finding_reproduction_rate`（立案发现可实际复现的比例）。
- 时延指标 / Latency Metrics: `round_turnaround` (attack plus repair per round), `rounds_to_convergence`, and end-to-end review latency versus the single-pass critique baseline. / `round_turnaround`（每轮攻击加修复耗时）、`rounds_to_convergence`（到收敛的轮数）、端到端评审时延对比单轮评审基线。
- 成本指标 / Cost Metrics: attacker setup and per-round budget spend, repair effort per finding by severity, and production incident cost avoided by pre-release catches. / 攻击者搭建与每轮预算开销、按严重度分的每发现修复投入、发布前拦截所避免的生产事故成本。
- 风险指标 / Risk Metrics: `max_round_hit_rate` (loops escalating at the bound, watch `FAIL_0007`), `context_bleed_incidents` (attacker exposed to author rationale, watch `FAIL_0008`), `fatigue_convergence_count` (rounds ending on exhausted budget claimed as zero findings), and out-of-surface findings handled without `GOV_0001` approval. / `max_round_hit_rate`（触顶升级的循环比例，对应 `FAIL_0007`）、`context_bleed_incidents`（攻击者接触到作者辩护的事件，对应 `FAIL_0008`）、`fatigue_convergence_count`（预算耗尽却宣称零发现的轮次数）、未经 `GOV_0001` 审批即处理的攻击面外发现。
- Trace 指标 / Trace Metrics: `round_log_completeness` (findings, repairs, dispositions recorded per round, per `GOV_0002`), convergence-certificate auditability (final round replayable), and surviving-finding escalation closure rate. / `round_log_completeness`（每轮发现、修复、处置的记录完整率，按 `GOV_0002`）、收敛证书可审计性（末轮可回放）、存活发现升级的闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert when `post_release_escape_rate` rises after convergence certificates or `finding_yield_per_round` fails to decay — the former means convergence is being declared hollow, the latter means repairs are spawning as many flaws as they fix. / 收敛证书发出后 `post_release_escape_rate` 上升或 `finding_yield_per_round` 不衰减即告警——前者说明收敛宣告名不副实，后者说明修复制造的缺陷与其消除的一样多。
- Block the convergence certificate when the final round ran under budget, findings lack reproduction steps, or blocker-severity findings remain open; the only legal exits are another full round or escalation with the surviving findings. / 末轮预算未跑满、发现缺复现步骤或阻断级发现仍未关闭时，禁发收敛证书；唯一合法出口是再跑一整轮或带存活发现升级。
