# Chain-of-Thought / 思维链 Observability Metrics / 可观测性指标

Cell / 交织点: reasoning-chain / 推理 x 链式
Capability / 能力: Reasoning / 推理
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)
Use this file as the observability metrics source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的可观测性指标来源。
Design Pattern File / 设计模式文件: [reasoning-chain.md](reasoning-chain.md)
Factory Implementation / 工厂实现: [Reasoning Chain Factory / 推理链工厂](../../reasoning-chain-factory.md)
Shared Probe Suite / 共享探针套件: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)
Metric Registry / 指标注册表: [`metric_registry.json`](../../../runtime/metric_registry.json)

## Observability Metrics / 可观测性指标

Use these metrics to observe whether an Externally Verifiable Reasoning Chain / 外部可核验推理链 improves the workflow after selection or application. Preserve Chain-of-Thought / 思维链 only as the upstream source alias; never treat private reasoning text as runtime data. / 使用以下指标观察外部可核验推理链在选型或应用后是否改善工作流。Chain-of-Thought / 思维链仅作为上游来源别名保留，绝不能把私密推理文本当作运行数据。

- 质量指标 / Quality Metrics: `step_check_pass_rate` (intermediate conclusions passing their checkpoint), `chain_acceptance_rate` (final conclusions accepted downstream), and `error_localization_rate` (share of wrong conclusions traceable to a specific step). / `step_check_pass_rate`（中间结论通过检查点的比例）、`chain_acceptance_rate`（最终结论被下游采纳的比例）、`error_localization_rate`（错误结论可定位到具体步骤的比例）。
- 时延指标 / Latency Metrics: `per_step_latency`, `chain_total_latency` versus a single-shot baseline, and `checkpoint_overhead` (time spent checking versus reasoning). / `per_step_latency`（单步时延）、`chain_total_latency`（链式总时延，对比一次性推理基线）、`checkpoint_overhead`（检查耗时占推理耗时比）。
- 成本指标 / Cost Metrics: `tokens_per_step`, total chain tokens versus single-shot baseline, and rework tokens avoided by catching errors at checkpoints. / `tokens_per_step`（单步 token）、链式总 token 对比一次性基线、检查点拦截错误而避免的返工 token。
- 风险指标 / Risk Metrics: `error_propagation_depth` (steps an undetected error traveled before being caught), `forced_single_path_rate` (chains that should have escalated to reasoning-parallel or reasoning-loop but did not), and `unrecorded_step_count` (intermediate conclusions lost between steps, watch `FAIL_0006`). / `error_propagation_depth`（未被发现的错误在被捕获前传播的步数）、`forced_single_path_rate`（本应升级到 reasoning-parallel 或 reasoning-loop 却硬撑链式的比例）、`unrecorded_step_count`（步骤间丢失的中间结论数，对应 `FAIL_0006`）。
- Trace 指标 / Trace Metrics: `step_record_completeness` (input, claim, grounding, link recorded per step, per `GOV_0002`), checkpoint result coverage, and escalation event coverage. / `step_record_completeness`（每步输入、主张、依据、衔接的记录完整率，按 `GOV_0002`）、检查点结果覆盖率、升级事件覆盖率。

### Required Probe Coverage / 必需探针覆盖

Enable task identity (`PROBE_0001`), contract completeness (`PROBE_0002`), route decision (`PROBE_0003`) for forced-single-path analysis, budget and resources (`PROBE_0004`), step closure (`PROBE_0005`), evidence chain (`PROBE_0006`), tool and action (`PROBE_0007`) when actions occur, drift (`PROBE_0010`), validation (`PROBE_0011`), stop and escalation (`PROBE_0012`), outcome (`PROBE_0013`) for downstream acceptance or correctness, privacy and governance (`PROBE_0014`), and probe self-health (`PROBE_0015`). / 启用任务身份、契约完整性、路由决策（用于分析硬撑单路径）、预算与资源、步骤闭环、证据链、工具与动作（存在动作时）、漂移、验证、停止升级、结果回接（用于下游采纳或正确性）、隐私治理和探针自健康探针。

Compute `eligible_step_closure_rate` over all started steps whose close deadline elapsed, including hanging steps. Separately compute `closed_step_record_completeness` over closed steps that distinguish claim, action, observation, and decision. Track evidence support and field-level provenance per externally checkable subclaim. Do not capture hidden reasoning text or use answer length as a proxy for chain depth. / `eligible_step_closure_rate` 的分母包含所有已到关闭期限的启动步骤，包括悬挂步骤；对已关闭步骤另算能否区分命题、动作、观察和决定的 `closed_step_record_completeness`。逐个外部可核验子命题记录证据支持和字段级来源。不得采集隐藏推理文本，也不得用答案长度代替链深度。

Version metric definitions and bucket by scene, risk, chain length, evidence grade, validator, model, tool, and outcome availability. Preserve missing checkpoints as missing rather than treating them as passes. / 指标口径版本化，并按场景、风险、链长、证据等级、验证器、模型、工具和后验可用性分桶。缺失检查点保留为缺失，不得计为通过。

### Factory Observability / 工厂可观测性

Bind every step, action, local decision, and checkpoint validation to the sealed plan and contract. Compare planned versus actual sequence, predecessor claim, exact action envelope and tool flag, checkpoint/validator/criteria bindings, observation hash, resolved `(evidence_id, evidence_version, record_hash)` bindings, evidence sufficiency, actor/authority bindings, pre-dispatch reservation and close-time settlement, resolved probe plan, and terminal candidate timing, plan binding, and final-claim coverage. Any mismatch is plan drift and blocks dependent work or completion. / 每个步骤、动作、局部决定和检查点验证都必须绑定密封计划与契约。比较计划与实际的顺序、前驱命题、精确动作信封与工具标志、检查点/验证器/标准绑定、观察哈希、已解析的 `(evidence_id, evidence_version, record_hash)` 绑定、证据充分性、分派前预算预留与关闭时结算、执行者/授权绑定、已解析探针计划，以及终态候选的时机、计划绑定与最终命题覆盖；任何不一致都属于计划漂移，并阻断依赖工作或完成态。

The registry now implements `plan_compile_success_rate`, `plan_drift_rate`, `checkpoint_validation_binding_rate`, `budget_pre_reservation_coverage`, `evidence_resolution_rate`, `candidate_evidence_lineage_integrity_rate`, and `readonly_tool_lifecycle_completion_rate` as publication-grade factory diagnostics with explicit denominators, owners, and required probes. They remain outside `gate_eligible` until owned thresholds and promotion evidence are approved. Capability-preflight and rejected-authorization reasons remain categorical diagnostics. Deterministic compiler rejection, invalid-validation successor blocking, budget reservation failure, unresolved evidence, early or unbound candidate blocking, and unverified tool authorization are runtime guards rather than statistical metric gates. / 注册表现已实现 `plan_compile_success_rate`、`plan_drift_rate`、`checkpoint_validation_binding_rate`、`budget_pre_reservation_coverage`、`evidence_resolution_rate`、`candidate_evidence_lineage_integrity_rate` 与 `readonly_tool_lifecycle_completion_rate`，作为具备明确分母、负责人和必需探针的可发布工厂诊断指标；在负责人阈值和晋升证据获批前，它们仍不进入 `gate_eligible`。能力预检与被拒授权原因仍是分类诊断。确定性编译拒绝、无效验证后的后继阻断、预算预留失败、证据无法解析、候选过早或未绑定，以及工具授权未验证属于运行时守卫，而非统计指标门控。

### Default Gate Suggestions / 默认门控建议

- Alert when gate-eligible `closed_step_record_completeness` falls below its owned, bucketed threshold or `unverified_premise_propagation` is observed above zero. Implemented factory diagnostics remain non-gating until separately promoted. / 当可用于门控的 `closed_step_record_completeness` 低于有负责人且按桶配置的阈值，或观测到 `unverified_premise_propagation` 大于零时告警。已实现的工厂诊断指标在单独晋升前仍不可用于门控。
- Block the next step when the current intermediate conclusion fails its checkpoint; require a fix or an escalation to reasoning-loop or reasoning-parallel, never a silent pass-through. / 当前中间结论未通过检查点时阻断下一步；要求修复或升级到 reasoning-loop / reasoning-parallel，禁止静默放行。
