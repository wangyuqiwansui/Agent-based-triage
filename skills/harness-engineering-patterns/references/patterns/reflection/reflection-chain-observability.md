# Generator-Critic / 生成器-批评器 Observability Metrics / 可观测性指标

Cell / 交织点: reflection-chain / 反思 x 链式
Capability / 能力: Reflection / 反思
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reflection-chain.md](reflection-chain.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Generator-Critic / 生成器-批评器 improves the workflow after selection or application. / 使用以下指标观察 Generator-Critic / 生成器-批评器 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `critique_catch_rate` (defects found by critic versus defects found downstream), `revision_improvement` (acceptance of revised output versus first draft), and per-criterion finding distribution (criteria that never fire are dead weight). / `critique_catch_rate`（批评器发现缺陷对比下游发现缺陷）、`revision_improvement`（修订稿相对初稿的采纳率提升）、逐判据发现分布（从不命中的判据是死重）。
- 时延指标 / Latency Metrics: critique pass latency, end-to-end generate→critique→revise time versus generate-only baseline, and escalation delay to reflection-loop or human review. / 批评轮时延、"生成→批评→修订"端到端时间对比纯生成基线、升级到 reflection-loop 或人工评审的延迟。
- 成本指标 / Cost Metrics: critique overhead ratio (critic plus revision tokens over generator tokens), cost per caught defect, and cross-model or tool invocation spend by feedback variant. / 批评开销比（批评加修订 token 除以生成 token）、单缺陷捕获成本、按反馈变体统计的跨模型或工具调用花销。
- 风险指标 / Risk Metrics: critic approval rate (near 100% signals rubber-stamping; near 0% signals mis-calibrated criteria), share of correctness-critical outputs reviewed only by self-critique, and unresolved-finding leak rate into delivery. / 批评通过率（接近 100% 提示橡皮图章，接近 0% 提示判据失准）、仅经自评的正确性关键产出占比、未解决发现泄漏进交付的比例。
- Trace 指标 / Trace Metrics: critique report completeness (every finding mapped to a criterion and a resolution), pass-count distribution (should concentrate at 1–2 per the article), and escalation record coverage. / 批评报告完整率（每个发现对应判据与处置）、轮次分布（按论文应集中在 1–2 轮）、升级记录覆盖率。

### Default Gate Suggestions / 默认门控建议

- Alert when critic approval rate stays above ~95% across a sampling window — the critic is likely not discriminating. / 批评通过率在采样窗口内持续高于约 95% 时告警——批评器很可能失去区分度。
- Block delivery of correctness-critical output that received only self-critique when tool-grounded feedback was available. / 当工具接地反馈可用时，阻止仅经自评的正确性关键产出直接交付。
- Alert when pass count exceeds 2 — the work belongs in Self-Heal Loop (reflection-loop), not a longer chain. / 轮次超过 2 时告警——该工作应转入自愈循环（reflection-loop）而非加长链。
