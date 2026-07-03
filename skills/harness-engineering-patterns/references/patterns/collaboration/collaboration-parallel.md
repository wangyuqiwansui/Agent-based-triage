# Fan-Out/Gather / 扇出汇聚

Cell / 交织点: collaboration-parallel / 协作 x 并行
Capability / 能力: Collaboration / 协作
Mode / 模式: Parallel / 并行
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Fan-Out/Gather has a coordinator split work into independent subtasks, dispatch them to n isolated workers concurrently, then aggregate the results into one synthesis. / 扇出汇聚由协调者将工作切分为独立子任务，并发分发给 n 个相互隔离的 worker，再将结果聚合为一个综合产出。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Collaboration / 协作 x Parallel / 并行 (Parallel / 并行).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Collaboration / 协作 x Parallel / 并行 in arXiv:2605.13850. The article cites multi-agent-debate results as evidence that independent parallel perspectives improve answer quality. / 代表性定义 / Representative definition；来源表将 Collaboration / 协作 x Parallel / 并行 映射到该单元。论文引用多智能体辩论结果作为"独立并行视角提升答案质量"的证据。
- 问题 / Problem: One actor cannot cover all perspectives or independent subtasks quickly enough. / 单一参与者无法足够快地覆盖所有视角或独立子任务。
- 架构方案 / Architectural Solution: Fan out independent work to multiple agents or contributors working in isolated contexts, then gather results into a synthesis step. Workers must not share intermediate state — isolation is what buys perspective diversity. / 将独立工作扇出给多个在隔离上下文中工作的 Agent 或贡献者，再将结果汇聚到综合步骤。worker 之间不得共享中间状态——隔离正是视角多样性的来源。
- 工程权衡 / Engineering Trade-offs: Improves speed and diversity, but costs roughly n× tokens, and the article identifies aggregation as the quality bottleneck: a weak synthesis step wastes all upstream diversity. / 提升速度和多样性，但成本约为 n 倍 token，且论文指出聚合是质量瓶颈：综合步骤薄弱会浪费全部上游多样性。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when several contributors can work independently before synthesis. / 当多个贡献者可独立工作后再综合时使用。

### Fan-Out Contract / 扇出契约

```yaml
fan_out:
  coordinator: ""              # owns split and synthesis / 负责切分与综合
  workers:
    - worker_id: ""
      subtask: ""              # self-contained brief; workers cannot see each other / 自包含任务书；worker 互不可见
      context_scope: ""        # exactly what this worker may read / 该 worker 可读范围
      output_contract: ""      # required result shape for aggregation / 聚合所需结果结构
  gather:
    synthesis_owner: ""        # single accountable aggregator / 单一聚合责任方
    conflict_rule: ""          # keep-both-with-evidence | vote | escalate / 带证据保留双方、投票或升级
    dedup_rule: ""
  sizing_rule: ""              # article Law 4: 1 item no fan-out; 10-50 fan-out; 100-500 add hierarchy / 论文定律 4：1 项不扇出；10-50 扇出；100-500 加层级
```

Gather rules / 汇聚规则:

- The synthesis owner must see every worker output plus its evidence, not summaries of summaries. / 综合责任方必须看到每个 worker 产出及其证据，而不是摘要的摘要。
- Conflicting worker results are preserved with sources, not silently averaged. / 冲突的 worker 结果连同来源保留，不得静默取平均。
- Scale by volume (article Law 4): a single item needs no fan-out; 10–50 items fit Fan-Out/Gather; 100–500 items add Hierarchical Delegation on top (collaboration-hierarchy); continuous streams need routing plus auto-scaling instead. / 按处理量伸缩（论文定律 4）：单项无需扇出；10–50 项适用扇出汇聚；100–500 项需叠加层级委派（collaboration-hierarchy）；持续流则改用路由加自动伸缩。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Fan-Out/Gather / 扇出汇聚.
- 诊断用途 / Diagnostic Use: Use when several contributors can work independently before synthesis. / 当多个贡献者可独立工作后再综合时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 方案设计、执行实现 / Design, implementation.
- 当前症状 / Current Symptoms: Independent subtasks run serially and dominate latency; a single reviewer covers all perspectives; parallel workers exist but leak context to each other or produce unmergeable formats. / 独立子任务串行执行主导时延；单一评审覆盖所有视角；已有并行 worker 但相互泄漏上下文或产出无法合并的格式。
- 适配信号 / Fit Signals: 多个参与者可独立工作并在约定点合并 / Multiple participants can work independently and merge at agreed points.
- 调整方向 / Adjustment Direction: Write self-contained worker briefs with context scopes and output contracts; assign a single synthesis owner; size n by volume per Law 4. / 编写带上下文范围与输出契约的自包含 worker 任务书；指定单一综合责任方；按定律 4 依处理量确定 n。
- 修改方式 / How To Modify: 1) Split work only along genuinely independent boundaries. 2) Fill the fan-out contract above. 3) Give the gather step first-class effort — it is the quality bottleneck. 4) Add hierarchy only when volume exceeds ~100 items. / 1）仅沿真正独立的边界切分；2）填写上方扇出契约；3）将汇聚步骤当作一等工作——它是质量瓶颈；4）仅当处理量超过约 100 项时加层级。
- 输入 / Inputs: Decomposable task, worker pool or subagent capacity, output contracts, token budget for n workers. / 可分解任务、worker 池或子 Agent 容量、输出契约、n 个 worker 的 token 预算。
- 输出 / Outputs: Per-worker results with evidence, synthesis artifact, conflict register. / 逐 worker 带证据结果、综合产物、冲突台账。
- 风险与治理 / Risks & Governance: Aggregation bottleneck `FAIL_0013` (named by the article) — synthesis silently dropping minority findings; context leakage between workers destroying independence (`FAIL_0008` unclear subagent boundary); n× cost without quality gain when subtasks were not actually independent; record per-worker outputs per `GOV_0002`. / 聚合瓶颈 `FAIL_0013`（论文点名）——综合静默丢弃少数派发现；worker 间上下文泄漏破坏独立性（`FAIL_0008` 子 Agent 边界不清）；子任务并非真正独立时付出 n 倍成本而无质量收益；逐 worker 产出按 `GOV_0002` 记录。

Observability Metrics File / 可观测性指标文件: [collaboration-parallel-observability.md](collaboration-parallel-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, add an entry to [trace.md](trace.md) in this capability folder. / 推荐或应用本模式后，在该能力文件夹的 [trace.md](trace.md) 中追加记录。
