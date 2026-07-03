# Handoff Chain / 交接链 Observability Metrics / 可观测性指标

Cell / 交织点: collaboration-chain / 协作 x 链式
Capability / 能力: Collaboration / 协作
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [collaboration-chain.md](collaboration-chain.md)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Handoff Chain / 交接链 improves the workflow after selection or application. / 使用以下指标观察 Handoff Chain / 交接链 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: `handoff_acceptance_rate` (handoffs accepted on first presentation), `context_package_completeness` (packages carrying done criteria, open risks, and decisions), and `downstream_surprise_rate` (defects traced to risks known upstream but absent from the package). / `handoff_acceptance_rate`（首次提交即被接受的交接比例）、`context_package_completeness`（携带完成标准、未决风险与取舍的包完整率）、`downstream_surprise_rate`（追溯为上游已知却未入包的风险所致缺陷比例）。
- 时延指标 / Latency Metrics: `handoff_dwell_time` (sender-ready to receiver-accepted), acceptance-check execution time per boundary, and `reject_return_cycle` (rejection to re-presentation). / `handoff_dwell_time`（交出方就绪到接收方接受的停留时间）、每边界验收检查执行耗时、`reject_return_cycle`（拒收到再次提交的周期）。
- 成本指标 / Cost Metrics: package assembly effort per boundary, `context_reconstruction_cost` avoided (receiver time saved by not re-deriving intent), and rework cost from boundary ping-pong. / 每边界的包组装投入、避免的 `context_reconstruction_cost`（接收方免于重建意图节省的时间）、边界来回弹产生的返工成本。
- 风险指标 / Risk Metrics: `naked_handoff_count` (artifacts transferred without a package, watch `FAIL_0006`), `orphaned_work_incidents` (intervals with no single owner, watch `FAIL_0008`), `repeat_rejection_count` per boundary (escalation trigger per `GOV_0001`), and dropped-risk incidents (open risks lost between boundaries). / `naked_handoff_count`（无包转移的产物数，对应 `FAIL_0006`）、`orphaned_work_incidents`（无唯一负责人的悬空区间数，对应 `FAIL_0008`）、每边界 `repeat_rejection_count`（按 `GOV_0001` 触发升级）、风险掉落事件（未决风险在边界间丢失）。
- Trace 指标 / Trace Metrics: `handoff_ledger_completeness` (package, verdict, rejection reason recorded per boundary, per `GOV_0002`), responsibility-ledger continuity (exactly one owner at every timestamp), and rejection-reason closure rate. / `handoff_ledger_completeness`（每边界的包、裁定、拒收原因记录完整率，按 `GOV_0002`）、责任账本连续性（任一时刻恰有一个负责人）、拒收原因闭环率。

### Default Gate Suggestions / 默认门控建议

- Alert on any `naked_handoff_count` above zero and when `downstream_surprise_rate` climbs — the former means the default-reject rule is being bypassed, the latter means packages are structurally present but semantically hollow. / `naked_handoff_count` 一旦大于零即告警，`downstream_surprise_rate` 上升同样告警——前者说明默认拒收规则被绕过，后者说明包结构俱在而语义空心。
- Block responsibility transfer when the acceptance check has not run or the context package lacks done criteria or open risks; repeated rejections at one boundary escalate per `GOV_0001` instead of another return cycle. / 验收检查未运行或上下文包缺完成标准、未决风险时阻断责任转移；同一边界反复拒收按 `GOV_0001` 升级而非再来一轮退回。
