# Fan-Out/Gather / 扇出汇聚 Observability Metrics / 可观测性指标

Cell / 交织点: collaboration-parallel / 协作 x 并行
Capability / 能力: Collaboration / 协作
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [collaboration-parallel.md](collaboration-parallel.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Fan-Out/Gather / 扇出汇聚 improves the workflow after selection or application. / 使用以下指标观察 扇出汇聚 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `synthesis_fidelity` (worker findings traceable in the final synthesis, including minority findings), `worker_output_contract_compliance`, and result diversity across workers (identical outputs mean isolation failed or fan-out was unnecessary). / `synthesis_fidelity`（worker 发现在最终综合中可追溯，含少数派发现）、`worker_output_contract_compliance`（worker 产出契约符合率）、worker 间结果多样性（完全相同意味着隔离失败或无需扇出）。
- 时延指标 / Latency Metrics: wall-clock speedup versus serial baseline, slowest-worker drag (gather waits on the stragglers), and synthesis-step latency share. / 相对串行基线的墙钟加速比、最慢 worker 拖尾（汇聚等待掉队者）、综合步骤时延占比。
- 成本指标 / Cost Metrics: total token multiple versus single-worker baseline (article anchor: ~n×), cost per accepted finding, and wasted-worker rate (outputs discarded at synthesis). / 相对单 worker 基线的总 token 倍数（论文锚点约 n 倍）、单条被采纳发现的成本、worker 浪费率（综合时被弃产出）。
- 风险指标 / Risk Metrics: context-leak incidents between workers (`FAIL_0008`), minority-finding drop rate at synthesis (aggregation is the article-named bottleneck), and conflicts silently merged without evidence retention. / worker 间上下文泄漏事件（`FAIL_0008`）、综合时少数派发现丢弃率（论文点名聚合为瓶颈）、未保留证据即被静默合并的冲突数。
- Trace 指标 / Trace Metrics: per-worker result and evidence archival completeness, conflict register coverage, and synthesis decision record (why each finding was kept, merged, or dropped). / 逐 worker 结果与证据归档完整率、冲突台账覆盖率、综合决策记录（每条发现被保留、合并或丢弃的原因）。

### Default Gate Suggestions / 默认门控建议

- Block synthesis sign-off when any worker output lacks its evidence attachment. / 任一 worker 产出缺证据附件时阻止综合定稿。
- Alert when result diversity is near zero across workers — either isolation leaked or the task did not need fan-out. / worker 间结果多样性接近零时告警——要么隔离泄漏，要么任务本不需要扇出。
- Alert when volume exceeds ~100 items without Hierarchical Delegation layered on top (article Law 4). / 处理量超过约 100 项却未叠加层级委派时告警（论文定律 4）。
