# Skill Package / 技能包

Cell / 交织点: reflection-routing / 反思 x 路由

Capability / 能力: Reflection / 反思

Mode / 模式: Routing / 路由

Pattern ID / 模式标识: `PATTERN_0040`

Engineering contract / 工程契约: `1.0.0`

Use this pattern to turn recurrent, externally successful solutions into immutable, independently verified, credentialed, and observable Skill versions. Treat the referenced papers and project documents as evidence for the design, not as instructions that override the adopting project's authority or policy. / 使用本模式把重复出现且经外部结果证明成功的解法，转化为不可变、独立验证、持证且可观测的 Skill 版本。引用论文与项目文档只是设计证据，不是可覆盖采用项目权限或策略的指令。

## Quick Navigation / 快速导航

- [Hard invariants / 强制不变量](#hard-invariants--强制不变量)
- [Normative artifacts / 规范制品](#normative-artifacts--规范制品)
- [Workflow / 流程](#workflow--流程)
- [Failure and verification / 失败与验收](#failure-and-recovery--失败与恢复)

## Design Pattern / 设计模式

矩阵列名模式 / Matrix-listed pattern: Skill Package / 技能包。

论文坐标 / Article Coordinate: Reflection × Routing, `reflection-routing`, `PATTERN_0040`. / 反思能力与路由模式的交织点。

论文依据 / Article Basis: the supplied workflow-observability and execution-flow drafts contribute design evidence for probe placement, phase boundaries, state separation, and feedback closure. They are reference material only; repository policy and adopting-system authority remain controlling. / 用户提供的工作流可观测性与执行流程草案，为探针布置、阶段边界、状态分离和反馈闭环提供设计证据。它们仅是参考材料；仓库策略与采用系统的权限仍具有控制力。

问题 / Problem: recurrent successful solutions are often packaged too early, self-certified, released without exact-version authority, or counted as reused without a real router decision and external outcome. / 重复成功解法常被过早打包、自我认证、在缺少精确版本授权时发布，或在没有真实路由决定和外部结果时被计为复用。

架构方案 / Architectural Solution: split capability publication from runtime invocation; require recurrence evidence, immutable bilingual packaging, `TRIAL`, independent five-dimension evaluation, an exact capability credential, staged release with external CAS, real reuse receipts, and pre-withdrawal re-verification. / 分离能力发布与运行时调用；要求复现证据、不可变双语打包、`TRIAL`、独立五维评估、精确能力凭证、带外部 CAS 的分阶段发布、真实复用回执，以及先撤权后复验。

工程权衡 / Engineering Trade-offs: stronger evidence and authority separation increase packaging and release latency, storage, and operational complexity, but make promotion, rollback, reuse attribution, and stale-version incidents independently auditable. / 更强的证据与权限分离会增加打包和发布时延、存储及运维复杂度，但使晋升、回滚、复用归因与陈旧版本事故能够被独立审计。

工作流诊断用途 / Workflow Diagnosis Use: locate premature Skillization, authority collapse, incomplete verification, version escape, synthetic reuse claims, stale credentials, and illegal re-verification order. / 定位过早技能化、权限合并、验证不完整、版本逃逸、合成复用声明、陈旧凭证与非法复验顺序。

Observability Metrics File / 可观测性指标文件: [reflection-routing-observability.md](reflection-routing-observability.md)

## When To Use / 适用场景

Use this pattern when all of the following are true. / 仅在以下条件同时成立时使用：

- The same problem class and materially same solution recur in distinct runs. / 同一问题类别与实质相同的解法在不同运行中复现。
- Each source run has an external outcome and attributable solution contribution. / 每个来源运行都有外部结果与可归属的解法贡献。
- A stable routine can be separated from instance-specific constants and hidden assumptions. / 可以把稳定例程与实例特定常量、隐含假设分离。
- The adopter can provide distinct verification, credential, publication, and lifecycle authorities. / 采用方能提供相互分离的验证、凭证、发布与生命周期权限主体。

Do not use it for a one-off workaround, a solution without an external outcome, a task-specific secret, or a change whose risk cannot be bounded and independently tested. / 不要把它用于一次性补丁、缺少外部结果的解法、任务特定秘密，或无法限定风险并独立测试的变更。

## Hard Invariants / 强制不变量

1. Success may nominate a candidate; it never grants qualification or production traffic. / 成功只能提名候选，绝不能直接授予资格或生产流量。
2. Every source enters as `TRIAL`, including a human-authored package. / 所有来源都必须先进入 `TRIAL`，包括人工编写的技能包。
3. Asset qualification (`UNREGISTERED | TRIAL | VERIFIED | RETIRED`) is separate from traffic exposure (`unpublished | shadow | limited | production | suspended | retired | archived`) and credential status (`issued | suspended | expired | revoked`). / 资产资格、流量暴露态与凭证态是三组正交事实，不得混为一个“已发布”布尔值。
4. Verification covers exactly five dimensions: result, activation, flow, incremental value, and freshness. Partial pass is not `VERIFIED`. / 验证必须精确覆盖结果、激活、流程、增量价值和新鲜度五维；部分通过不是 `VERIFIED`。
5. A credential binds the exact contract, Skill ID, semantic version, manifest digest, evaluation, policy, tool contracts, runner/environment, and permission scope. / 凭证必须精确绑定契约、Skill ID、语义版本、清单摘要、评估、策略、工具契约、运行器或环境与权限范围。
6. Production requires `shadow → limited → production` and an external compare-and-swap alias receipt. / 生产必须经过 `shadow → limited → production`，并提供外部比较并交换别名回执。
7. A production reuse counts only when the router selected the exact manifest with the active credential and a real run later produced an external outcome. / 生产复用只在路由器选中精确清单与活跃凭证，且真实运行后续产生外部结果时计入。
8. Re-verification withdraws traffic and qualification before evaluation starts; a new credential must supersede the previous credential. / 复验开始前必须先撤回流量与资格；新凭证必须显式替代上一凭证。
9. Observability records facts and raises evidence-backed signals; it does not mutate qualification, aliases, permissions, or policy. / 可观测层只记录事实并产生有证据信号，不修改资格、别名、权限或策略。
10. A reference implementation in this repository is not evidence that a deployed Skill is production-qualified. / 本仓库中存在参考实现，不等于某个已部署 Skill 已获生产资格。

## Two Independent Pipelines / 两条独立管道

```text
Capability publication / 能力发布
accepted reflection candidate
  -> recurrence proof -> distillation -> immutable package -> TRIAL
  -> independent five-dimension evaluation -> credential -> VERIFIED
  -> shadow -> limited -> atomic alias switch -> production

Runtime invocation / 运行时调用
task -> route decision -> exact alias/manifest/credential check
  -> governed execution -> external outcome -> reuse receipt
```

The publication pipeline decides whether a version may be routed. The invocation pipeline decides whether one concrete task may use that already-qualified version. Passing either pipeline cannot substitute for the other. / 发布管道决定某版本是否可被路由；调用管道决定某个具体任务是否可使用该已合格版本。任一管道通过都不能替代另一条。

## Authority Model / 权限模型

| Role / 角色 | May do / 可做 | Must not do / 禁止 |
| --- | --- | --- |
| Nominator / 提名者 | Bind recurrent source evidence to a candidate. / 将复现来源证据绑定为候选。 | Grant `VERIFIED`. / 授予 `VERIFIED`。 |
| Packager / 打包者 | Distill, parameterize, inventory dependencies, register `TRIAL`. / 蒸馏、参数化、盘点依赖并注册 `TRIAL`。 | Validate its own package. / 自验自签。 |
| Independent verifier / 独立验证者 | Execute sealed suites and issue evaluation evidence. / 执行封存套件并产生评估证据。 | Change the package, criteria, or denominator while judging it. / 在裁定时修改包、判据或分母。 |
| Credential issuer / 凭证签发者 | Issue an exact, time-bounded capability credential. / 签发精确且有时间界的能力凭证。 | Publish or rewrite evidence. / 发布或改写证据。 |
| Publisher / 发布者 | Advance traffic stages and perform external CAS. / 推进流量阶段并执行外部 CAS。 | Select a different manifest than the credential binds. / 选择与凭证不同的清单。 |
| Lifecycle owner / 生命周期负责人 | Promote after credential, record reuse, suspend, demote, retire, archive. / 持证后晋升、记录复用、暂停、降级、退役和归档。 | Invent verification or route around a failed gate. / 伪造验证或绕过失败闸门。 |

The verifier must differ from nominator and packager; the credential issuer and publisher are also separate authorities. An adopting project may impose stricter separation. / 验证者必须与提名者、打包者不同；凭证签发者与发布者也是独立权限主体。采用项目可施加更严格的分权。

## Normative Artifacts / 规范制品

Treat these Schemas and the runtime as the executable reference subset. / 将以下 Schema 与运行时视为可执行参考子集：

| Artifact / 制品 | Purpose / 用途 |
| --- | --- |
| [`skill-package-contract.schema.json`](../../../schemas/skill-package-contract.schema.json) | Seal recurrence, roles, package, verification, release, reuse, and governance policy. / 封存复现、角色、包、验证、发布、复用与治理策略。 |
| [`skill-package-candidate.schema.json`](../../../schemas/skill-package-candidate.schema.json) | Bind distinct successful runs and reflection nomination. / 绑定不同成功运行与反思提名。 |
| [`skill-package-manifest.schema.json`](../../../schemas/skill-package-manifest.schema.json) | Describe one immutable bilingual `TRIAL` package and supply chain. / 描述一个不可变双语 `TRIAL` 包与供应链。 |
| [`skill-package-evaluation.schema.json`](../../../schemas/skill-package-evaluation.schema.json) | Record independently reproducible five-dimension results. / 记录可独立复算的五维结果。 |
| [`capability-credential.schema.json`](../../../schemas/capability-credential.schema.json) | Bind exact qualification and replacement lineage. / 绑定精确资格与替换谱系。 |
| [`skill-package-alias-receipt.schema.json`](../../../schemas/skill-package-alias-receipt.schema.json) | Prove atomic route-alias publication. / 证明原子路由别名发布。 |
| [`skill-package-reuse-receipt.schema.json`](../../../schemas/skill-package-reuse-receipt.schema.json) | Bind real invocation, exact version, external outcome, and attribution state. / 绑定真实调用、精确版本、外部结果与归因状态。 |
| [`skill-package-event.schema.json`](../../../schemas/skill-package-event.schema.json) | Preserve the immutable state and authority chain. / 保留不可变状态与权限链。 |

Use [`runtime/skill_package.py`](../../../runtime/skill_package.py) for semantic validation and deterministic lifecycle coordination. It deliberately leaves durable storage, external evaluation execution, credential signing, alias mutation, and task execution to adopting systems. / 使用 `runtime/skill_package.py` 完成语义校验与确定性生命周期协调。持久化存储、外部评估执行、凭证签名、别名变更与任务执行故意留给采用系统。

## Workflow / 流程

| Phase / 阶段 | Required action / 必选动作 | Exit evidence / 退出证据 |
| --- | --- | --- |
| P00 Collect / 收集 | Capture distinct run, environment, external outcome, and contribution bindings. / 采集不同运行、环境、外部结果和贡献绑定。 | Immutable source inventory. / 不可变来源清单。 |
| P01 Nominate / 提名 | Require an accepted terminal shared-reflection observation whose learning decision is `candidate`, never `promoted`. / 要求已接受且终止的共享反思观察，其学习决定必须是 `candidate`，不得是 `promoted`。 | Candidate plus reflection assurance. / 候选与反思保证。 |
| P02 Distill / 蒸馏 | Separate stable steps, parameters, constants, hidden assumptions, and bounds. / 分离稳定步骤、参数、常量、隐含假设与边界。 | Distillation and boundary evidence. / 蒸馏与边界证据。 |
| P03 Package / 打包 | Build a bilingual immutable manifest with input/output, workflow, permissions, recovery, verification, provenance, resources, and dependencies. / 构建包含输入输出、流程、权限、恢复、验证、来源、资源与依赖的双语不可变清单。 | Manifest digest. / 清单摘要。 |
| P04 Register / 注册 | Register the exact manifest as `TRIAL`. / 将精确清单注册为 `TRIAL`。 | `UNREGISTERED → TRIAL` event. / 资格转换事件。 |
| P05 Verify / 验证 | A distinct verifier runs sealed cases, failure paths, counterexamples, regression checks, and gaming detection for all five dimensions. / 独立验证者针对全部五维执行封存用例、失败路径、反例、回归检查和投机检测。 | Passed or failed evaluation, never a silent partial pass. / 通过或失败评估，不存在静默部分通过。 |
| P06 Credential / 持证 | An independent issuer signs or otherwise externally attests the exact passed version. / 独立签发者对精确通过版本签名或作外部证明。 | Issued credential. / 已签发凭证。 |
| P07 Qualify / 授资格 | Lifecycle owner promotes only after credential validation. / 生命周期负责人仅在凭证校验后晋升。 | `TRIAL → VERIFIED` event. / 资格晋升事件。 |
| P08 Release / 发布 | Publisher advances shadow, limited, then performs exact-version CAS for production. / 发布者推进影子、有限流量，再对精确版本执行生产 CAS。 | Stage evidence and alias receipt. / 阶段证据与别名回执。 |
| P09 Reuse / 复用 | Record only real router-selected production runs; join external outcomes without rewriting earlier facts. / 仅记录路由器真实选中的生产运行；追加外部结果而不改写早期事实。 | Reuse receipt and outcome binding. / 复用回执与结果绑定。 |
| P10 Re-verify / 复验 | On freshness, dependency, environment, incident, or policy triggers, suspend credential, demote to `TRIAL`, then evaluate. / 遇到新鲜度、依赖、环境、事故或策略触发时，先暂停凭证、降为 `TRIAL`，再评估。 | Ordered suspension, demotion, re-verification events. / 有序的暂停、降级与复验事件。 |
| P11 Retire / 退役 | Revoke credentials, remove traffic, retain immutable history, then archive. / 撤销凭证、移除流量、保留不可变历史，再归档。 | `RETIRED` and archive events. / `RETIRED` 与归档事件。 |

## Failure And Recovery / 失败与恢复

- Insufficient recurrence: reject the nomination; gather new independent runs rather than duplicating evidence. / 复现不足：拒绝提名；收集新的独立运行，不得复制证据。
- Incomplete package or untrusted write dependency: remain before `TRIAL` or return to packaging with a recorded gap list. / 包不完整或不可信写依赖：停在 `TRIAL` 之前，或带缺口清单返回打包。
- Failed or incomplete dimension: remain `TRIAL`; create a new immutable manifest for content changes and re-run the full evaluation. / 维度失败或不完整：保持 `TRIAL`；内容变更时创建新的不可变清单并重跑完整评估。
- Credential, manifest, environment, permission, or tool-contract mismatch: fail closed before qualification or publication. / 凭证、清单、环境、权限或工具契约不匹配：在授资格或发布前默认阻断。
- CAS failure: leave the previous alias unchanged and record the failed external attempt; do not synthesize a success event. / CAS 失败：保持旧别名不变并记录外部失败尝试；不得伪造成功事件。
- Missing or late outcome: retain `pending` or `unknown`; do not count success and do not coerce it to zero. / 结果缺失或延迟：保留 `pending` 或 `unknown`；不计为成功，也不强制改为零。
- Freshness trigger: pre-withdraw before testing; reuse with the old or inactive credential is a hard incident. / 新鲜度触发：测试前先撤权；使用旧凭证或非活跃凭证复用是硬事故。

## Verification / 验收

Minimum acceptance tests for an adopting implementation: / 采用实现的最低验收测试：

- Reject duplicate runs, distinct-run shortfalls, authority collapse, and a reflection decision that already claims promotion. / 拒绝重复运行、不同运行不足、权限合并，以及已声称晋升的反思决定。
- Reject missing core sections, origin-free parameters, mismatched tool inventories, and untrusted write resources. / 拒绝缺失核心章节、无来源参数、不一致工具清单和不可信写资源。
- Reject a pass missing any one dimension, failure path, counterexample, regression guard, or exact evidence binding. / 缺任一维度、失败路径、反例、回归保护或精确证据绑定时拒绝通过。
- Reject credential mismatch, stage skipping, stale alias revision, old-version reuse, reuse outside the credential window, and re-verification without prior withdrawal. / 拒绝凭证不匹配、跳过阶段、陈旧别名修订、旧版本复用、凭证窗口外复用与未先撤权的复验。
- Replay the immutable event stream and verify contiguous sequence, previous hash, authority, qualification, and release-state continuity. / 重放不可变事件流，校验连续序号、前置哈希、权限、资格和发布态连续性。

## Pattern Template / 模式模板

- 状态 / Status: Named candidate; reference implementation complete; operational qualification remains project-local. / 已命名候选；参考实现已完成；运行资格仍由项目本地决定。
- 模式清单 / Patterns: Governed Skill Package Engineering / 受治理技能包工程。
- 诊断用途 / Diagnostic Use: Diagnose premature Skillization, self-certification, version escape, stale reuse, and unverifiable production claims. / 诊断过早 Skill 化、自签自验、版本逃逸、陈旧复用与无法验证的生产声明。
- 适用工作流节点 / Applicable Workflow Nodes: Reflection closure, learning nomination, package registration, verification, release, runtime routing, outcome return, and retirement. / 反思闭环、学习提名、包注册、验证、发布、运行时路由、结果回接与退役。
- 当前症状 / Current Symptoms: Repeated fixes remain ad hoc, or a structurally complete package is treated as proven and routed to production without exact qualification evidence. / 重复修复始终即兴，或结构完整的包被误当作已证明能力，在缺少精确资格证据时就路由到生产。
- 适配信号 / Fit Signals: Recurrent problem/solution signature, external success, separable stable procedure, bounded permissions, and available independent authorities. / 问题与解法签名复现、外部成功、稳定过程可分离、权限可限定、且独立权限主体可用。
- 调整方向 / Adjustment Direction: Replace direct packaging-to-production with evidence nomination, `TRIAL`, independent validation, exact credentials, staged CAS release, real reuse receipts, and pre-withdrawal re-verification. / 用证据提名、`TRIAL`、独立验证、精确凭证、分阶段 CAS 发布、真实复用回执与先撤权复验，替代从打包直达生产。
- 修改方式 / How To Modify: Seal the lifecycle contract; wire the shared reflection guard; emit and validate all eight artifacts; connect durable storage and external authorities; deploy probes; run positive, negative, replay, and drift tests; then calibrate thresholds from project evidence. / 封存生命周期契约；接入共享反思闸；发出并校验全部八类制品；连接持久存储与外部权限主体；部署探针；执行正向、反向、重放与漂移测试；再用项目证据校准阈值。
- 输入 / Inputs: Shared reflection artifacts, recurrent run/outcome evidence, role bindings, policies, immutable package contents, evaluation suites, external receipts, and outcome events. / 共享反思制品、复现运行与结果证据、角色绑定、策略、不可变包内容、评估套件、外部回执与结果事件。
- 输出 / Outputs: Candidate, manifest, evaluation, credential, alias/reuse receipts, immutable lifecycle events, probe events, metrics, alerts, and a project-local Trace proposal. / 候选、清单、评估、凭证、别名与复用回执、不可变生命周期事件、探针事件、指标、告警与项目本地 Trace 建议。
- 风险与治理 / Risks & Governance: Main risks are premature promotion, authority collapse, validator gaming, dependency or permission drift, version escape, false reuse attribution, stale credential use, and observability mutating control facts. Each is fail-closed at its named boundary; aggregate rates stay diagnostic until an owner approves thresholds and promotion evidence. / 主要风险包括过早晋升、权限合并、验证器投机、依赖或权限漂移、版本逃逸、虚假复用归因、过时凭证使用，以及可观测层修改控制事实。每项都在命名边界默认阻断；聚合比率在负责人批准阈值与晋升证据前保持诊断性。

Observability / 可观测: [reflection-routing-observability.md](reflection-routing-observability.md)

Shared reflection contract / 共享反思契约: [reflection-execution-flow.md](../../reflection-execution-flow.md)

Shared probes / 共享探针: [workflow-observability-probes.md](../../workflow-observability-probes.md)

## Trace Hook / 追踪钩子

After recommending or applying this pattern, create a project-local proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. Record exact artifact bindings, lifecycle events, unresolved gaps, adopting authorities, and verification evidence; never claim operational `VERIFIED` from repository structure alone. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 创建项目本地建议。记录精确制品绑定、生命周期事件、未解决缺口、采用权限主体与验证证据；不得仅凭仓库结构声称运行态 `VERIFIED`。
