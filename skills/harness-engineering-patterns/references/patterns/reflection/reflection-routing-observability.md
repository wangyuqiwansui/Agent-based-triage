# Governed Skill Package Observability / 受治理技能包可观测性

Cell / 交织点: `reflection-routing` / 反思 × 路由

Pattern / 模式: [Governed Skill Package Engineering / 受治理技能包工程](reflection-routing.md)

Contract / 契约: `1.0.0`

Design Pattern File / 设计模式文件: [reflection-routing.md](reflection-routing.md)

Observe the public facts that prove nomination, packaging, independent validation, credentialing, release, real reuse, freshness withdrawal, and retirement. Never collect private chain-of-thought, infer success from package existence, or let a probe mutate qualification, credentials, aliases, permissions, or policy. / 观测能够证明提名、打包、独立验证、凭证、发布、真实复用、新鲜度撤权与退役的公开事实。绝不采集私密思维链，不从技能包存在推断成功，也不允许探针修改资格、凭证、别名、权限或策略。

## Probe Profile / 探针档案

Call `resolve_reflection_required_probes(skill_package=True)`. This activates shared reflection probes `PROBE_0016` through `PROBE_0021`, learning-nomination probe `PROBE_0023`, and Skill Package probes `PROBE_0028` through `PROBE_0033`; add `PROBE_0022` only when causal attribution is claimed. / 调用 `resolve_reflection_required_probes(skill_package=True)`。它会激活共享反思探针 `PROBE_0016`–`PROBE_0021`、学习提名探针 `PROBE_0023` 与技能包探针 `PROBE_0028`–`PROBE_0033`；仅在声称因果归因时加入 `PROBE_0022`。

| Probe / 探针 | Boundary / 边界 | Evidence / 证据 | Default disposition / 默认处置 |
| --- | --- | --- | --- |
| `PROBE_0028` | Candidate and distillation / 候选与蒸馏 | Distinct run/outcome/environment bindings, contribution states, accepted reflection assurance, stable steps, parameters, assumptions, boundary evidence. / 不同运行、结果、环境绑定，贡献状态，已接受反思保证，稳定步骤、参数、假设与边界证据。 | Block nomination or `TRIAL` registration. / 阻断提名或 `TRIAL` 注册。 |
| `PROBE_0029` | Package and supply chain / 技能包与供应链 | Bilingual discovery, parameter origin, exact tool/permission/dependency inventory, resource trust, rollback, provenance. / 双语发现信息、参数来源、精确工具、权限、依赖清单、资源信任、回滚与来源。 | Block `TRIAL` registration. / 阻断 `TRIAL` 注册。 |
| `PROBE_0030` | Evaluation, credential, qualification / 评估、凭证与资格 | Exact suite, environment, five dimensions, counterexamples, failure paths, regression/gaming state, issuer and credential bindings. / 精确套件、环境、五维、反例、失败路径、回归与投机状态、签发者和凭证绑定。 | Fail closed before `VERIFIED`. / `VERIFIED` 前默认阻断。 |
| `PROBE_0031` | Qualification and atomic release / 资格与原子发布 | Qualification/release transitions, exact manifest/credential, stage evidence, CAS revisions and receipt. / 资格与发布转换、精确清单与凭证、阶段证据、CAS 修订与回执。 | Fail closed before traffic mutation. / 流量变更前默认阻断。 |
| `PROBE_0032` | Real reuse and outcome / 真实复用与结果 | Router decision, run, exact manifest/credential, alias window, external outcome, attribution state. / 路由决定、运行、精确清单与凭证、别名窗口、外部结果与归因状态。 | Record and recompute; hard-alert exact-version violations. / 记录并重算；精确版本违规硬告警。 |
| `PROBE_0033` | Freshness, withdrawal, re-verification, retirement / 新鲜度、撤权、复验与退役 | Ordered suspension, demotion, re-verification, superseding credential, revocation, retirement, archive, hash chain. / 有序暂停、降级、复验、替代凭证、撤销、退役、归档与哈希链。 | Fail closed on stale authority or illegal order. / 陈旧权限或非法顺序时默认阻断。 |

## Required Observable Fields / 必选可观测字段

Every event must preserve `schema_version`, event ID, lifecycle ID, sequence, RFC 3339 event time, idempotency key, previous-event hash, contract binding, optional exact manifest and credential bindings, actor binding, qualification before/after, release before/after, payload provenance, emitted time, received time, and privacy class. / 每个事件必须保留 Schema 版本、事件 ID、生命周期 ID、序号、RFC 3339 事件时间、幂等键、前事件哈希、契约绑定、可选精确清单与凭证绑定、主体绑定、资格前后态、发布前后态、载荷来源、发出时间、接收时间与隐私类别。

Keep four times distinct: occurrence, emission, receipt, and outcome observation. Keep missing, unknown, not applicable, observed zero, computed, and insufficient sample as distinct metric states. / 保持发生、发出、接收与结果观察四种时间相互分离。保持缺失、未知、不适用、观测零值、已计算与样本不足为不同指标状态。

## Registered Metrics / 已注册指标

The following ten metrics are implemented in `runtime/reasoning_metrics.py` and defined in `runtime/metric_registry.json`. They remain diagnostic until the adopting owner approves a threshold, window, minimum sample, exclusions, and rollback policy. / 以下十项指标已在 `runtime/reasoning_metrics.py` 实现，并在 `runtime/metric_registry.json` 定义。在采用负责人批准阈值、窗口、最小样本、排除项与回滚策略前，它们保持诊断性。

| Metric / 指标 | Formula / 公式 | Direction / 方向 | Required probes / 必选探针 |
| --- | --- | --- | --- |
| `skill_candidate_recurrence_evidence_rate` | candidates meeting recurrence policy / nominated candidates / 满足复现策略候选数 ÷ 提名数 | Higher / 越高越好 | `0028`, `0013` |
| `skill_package_contract_completeness_rate` | complete contracts / registered `TRIAL` packages / 完整契约数 ÷ `TRIAL` 包数 | Higher / 越高越好 | `0029` |
| `skill_package_five_dimension_verification_rate` | five-dimension passes / completed evaluations / 五维通过数 ÷ 完成评估数 | Higher / 越高越好 | `0030`, `0011` |
| `trial_to_verified_rate` | promoted versions / evaluated `TRIAL` versions / 晋升版本数 ÷ 已评估 `TRIAL` 版本数 | Higher / 越高越好 | `0030`, `0031` |
| `credential_exact_binding_rate` | exact credentials / issued credentials / 精确凭证数 ÷ 已签发凭证数 | Higher / 越高越好 | `0030` |
| `alias_switch_integrity_rate` | valid CAS switches / production switch attempts / 有效 CAS 切换数 ÷ 生产切换尝试数 | Higher / 越高越好 | `0031` |
| `skill_reuse_success_rate` | successful real reuses / determined real reuses / 成功真实复用数 ÷ 结果已确定复用数 | Higher / 越高越好 | `0032`, `0013` |
| `version_window_integrity_rate` | reuses in exact valid window / real reuses / 精确有效窗口内复用数 ÷ 真实复用数 | Higher / 越高越好 | `0032` |
| `reverification_prewithdrawal_compliance_rate` | re-verifications with prior withdrawal / re-verifications started / 已先撤权复验数 ÷ 已开始复验数 | Higher / 越高越好 | `0033` |
| `stale_credential_use_rate` | stale/inactive credential reuses / real reuses / 过时或非活跃凭证复用数 ÷ 真实复用数 | Lower / 越低越好 | `0031`, `0033` |

Do not manufacture a denominator. A real-reuse denominator excludes shadow, synthetic, dry-run, unmatched-router, pending-outcome, and unknown-outcome records as specified by each metric. Publish numerator, denominator, exclusions, window, watermark, completeness, and probe health together. / 不得伪造分母。真实复用分母按各指标定义排除影子、合成、演练、无匹配路由、待定结果和未知结果记录。发布指标时必须同时发布分子、分母、排除项、窗口、水位线、完整度和探针健康。

## Observability Metrics / 可观测性指标

- 质量指标 / Quality Metrics: Use the ten registered lifecycle ratios above plus sampled routing accuracy and downstream defect escape. Never combine `pending`, `unknown`, or insufficient sample with failure. / 使用上述十项已注册生命周期比率，并补充抽样路由准确率与下游缺陷逃逸。不得把 `pending`、`unknown` 或样本不足与失败合并。
- 时延指标 / Latency Metrics: Measure candidate-to-`TRIAL`, `TRIAL`-to-evaluation, evaluation-to-credential, credential-to-each-release-stage, route-to-start, start-to-outcome, outcome lag, withdrawal latency, and retirement latency. These are project-local until registered. / 测量候选到 `TRIAL`、`TRIAL` 到评估、评估到凭证、凭证到各发布阶段、路由到启动、启动到结果、结果滞后、撤权时延与退役时延。它们在注册前为项目本地指标。
- 成本指标 / Cost Metrics: Measure packaging, independent evaluation, staged release, observability, maintenance, re-verification, and avoided repeated-solution cost by exact Skill version. Keep token, money, tool, and human-review units separate. / 按精确 Skill 版本测量打包、独立评估、分阶段发布、可观测、维护、复验与避免重复求解的成本。令牌、货币、工具与人工评审单位分开。
- 风险指标 / Risk Metrics: Track premature qualification, authority collapse, partial-pass promotion, validator gaming, exact-binding mismatch, stage skip, CAS conflict, stale credential use, version-window contamination, reuse attribution overclaim, withdrawal-order violation, and probe-health failure. / 跟踪过早授资格、权限合并、部分通过晋升、验证器投机、精确绑定不匹配、跳阶段、CAS 冲突、过时凭证使用、版本窗口污染、复用归因越级、撤权顺序违规与探针健康失败。
- Trace 指标 / Trace Metrics: Measure event-chain completeness, exact artifact-binding coverage, actor-authority coverage, source-to-candidate lineage, candidate-to-manifest lineage, evaluation-to-credential lineage, credential-to-alias lineage, alias-to-reuse lineage, and reuse-to-outcome linkage. / 测量事件链完整度、精确制品绑定覆盖、主体权限覆盖、来源到候选、候选到清单、评估到凭证、凭证到别名、别名到复用，以及复用到结果的链接完整度。

## Hard Alerts And Gates / 硬告警与闸门

Fail closed per instance, regardless of aggregate trend, when any of these occurs: / 以下任一情况发生时，无论聚合趋势如何，都要按实例默认阻断：

- `VERIFIED` without a complete passed evaluation and active exact credential. / 在没有完整通过评估与活跃精确凭证时进入 `VERIFIED`。
- Verifier, issuer, publisher, or lifecycle actor violates the sealed authority binding. / 验证者、签发者、发布者或生命周期主体违反封存权限绑定。
- Evaluation, credential, alias, or reuse references a different manifest/version/digest, environment, tool contract, or permission scope. / 评估、凭证、别名或复用引用不同清单、版本、摘要、环境、工具契约或权限范围。
- Production stage is skipped or the external CAS receipt is absent, stale, failed, or revision-inconsistent. / 跳过生产阶段，或外部 CAS 回执缺失、陈旧、失败或修订不一致。
- A reuse is synthetic, not router-selected, outside the exact version window, or uses a suspended, expired, revoked, or superseded credential. / 复用为合成运行、非路由器选中、位于精确版本窗口外，或使用暂停、过期、撤销或已被替代的凭证。
- Re-verification begins before `credential_suspended` and `demoted_trial` occur in that order. / 复验在 `credential_suspended` 和 `demoted_trial` 未按该顺序发生前开始。
- Event sequence, previous hash, qualification continuity, release continuity, or required probe health fails. / 事件序号、前置哈希、资格连续性、发布连续性或必选探针健康失败。

Aggregate metrics may open an investigation or a project-approved gate, but a dashboard must never auto-edit the package, expand permission, issue a credential, switch an alias, or suppress an incident. / 聚合指标可以启动调查或项目已批准闸门，但仪表板绝不得自动编辑技能包、扩大权限、签发凭证、切换别名或压制事故。

## Feedback And Versioning / 反馈与版本

Join downstream outcomes by immutable bindings and append a new event; never rewrite an earlier nomination, evaluation, release, or reuse event. Version probe definitions, metric definitions, schemas, and policy independently. A definition change starts a new comparable window or explicitly rebases it; do not silently merge incompatible windows. / 使用不可变绑定回接下游结果并追加新事件；不得改写早期提名、评估、发布或复用事件。探针定义、指标定义、Schema 与策略独立版本化。定义变更时开启新的可比窗口或显式重建基线；不得静默合并不兼容窗口。

Shared definitions / 共享定义: [Workflow Observability Probes / 工作流可观测性探针](../../workflow-observability-probes.md)

Shared reflection execution / 共享反思执行: [Reflection Execution Flow / 反思执行流程](../../reflection-execution-flow.md)

Executable registries / 可执行注册表: [`probe_registry.json`](../../../runtime/probe_registry.json), [`probe_dependency_matrix.json`](../../../runtime/probe_dependency_matrix.json), [`metric_registry.json`](../../../runtime/metric_registry.json)

Runtime / 运行时: [`skill_package.py`](../../../runtime/skill_package.py), [`reasoning_metrics.py`](../../../runtime/reasoning_metrics.py)
