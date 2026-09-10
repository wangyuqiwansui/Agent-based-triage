# 对抗评审工程模式完善记录 / Adversarial Review Engineering Update

已将现有 `PATTERN_0045`（协作 × 循环）完善为以独立证据、必审风险和具体版本放行为中心的工程规约。两份输入文档的共享协议一致，已保留原始字节快照，并逐条登记 13 个执行节点、12 个探针节点、27 项指标和 44 个验收场景。

The existing pattern now specifies independent evidence, required-risk coverage and exact-version approval/release. Original source snapshots and complete mappings are retained. This is a specification and maintenance-tool update; it does not deploy a review or release service.

## 主要修正 / Main Corrections

| 原有问题 / Before | 已完善行为 / Updated requirement |
| --- | --- |
| 整轮零新发现被写作收敛证明。 / A quiet round served as convergence proof. | 同时检查当前基线覆盖、独立性、封口、阻断、关键缺口、程序校验及权限；零新发现不单独放行。 / Require all current-baseline gate conditions. |
| 无复现步骤的发现不计入升级，可能排除重要语义疑点。 / Missing reproduction excluded findings from escalation. | 有据语义异议可成立；关键疑点缺证时保持待补证或待裁决。 / Evidence-backed semantic findings and critical unknowns remain actionable. |
| 评审上下文一律禁止作者理由，以形式代替独立性验证。 / Blanket context isolation substituted for independence evidence. | 认证主体、实际访问、结论继承、来源族和真实权限五项核验；按策略声明盲审。 / Verify identity, access, context lineage, source families and authority. |
| 仅有攻击修复轮次，未完整定义审查基线和最终评审包。 / Rounds lacked complete binding semantics. | 两层摘要分别绑定输入基线与最终证明包，回执再绑定裁决、控制修订及动作权限。 / Bind baseline and final package separately in the receipt. |
| 新版修复容易被解释为旧版问题已经不存在。 / Successor repair could erase historical problems. | 保留旧异议及后继版本解决关联；新基线全部必审项重审。 / Preserve historical facts and fully re-review new baselines. |
| 探针将“末轮预算未跑满”列为阻断条件。 / Unspent budget blocked convergence. | 预算是上限；实际责任完成才是完成条件，耗尽但未完成也不通过。 / Completion follows obligations, not budget consumption. |
| 指标缺少明确总体、历史快照和未知边界。 / Metrics lacked population and uncertainty rules. | RM01–RM27 保留来源口径；区分可算、部分可算、不可算及不适用，控制结论另记。 / Preserve populations, historical snapshots and distinct calculability states. |
| 补数、裁决和放行缺少专用接收契约。 / Supplement handling lacked a dedicated receiver contract. | 校验租户、对象、基线、时效、白名单和修订；持久幂等接收，明确观测补充、重审、待人工和拒收。 / Validate scoped proposals and persist idempotent dispositions. |
| 发布意图、真实效果与失败恢复未充分区分。 / Intent and actual effect were insufficiently separated. | 条件提交意图、派发前复核、外部结果核对；未知效果不盲重试，已发生效果不靠撤销回执抹除。 / Reconcile effects and preserve history. |

改动前证据保存在 [原模式](before/collaboration-loop.md) 与 [原探针](before/collaboration-loop-observability.md)。两份输入快照见 [执行草稿](sources/execution.md) 与 [探针草稿](sources/probe.md)。来源文档中的路径、注册建议及执行指令只作为分析资料，没有当作本次用户授权执行。

## 可使用的资产 / Maintained Assets

- [执行模式](../../skills/harness-engineering-patterns/references/patterns/collaboration/collaboration-loop.md)：角色、对象、状态转换、RN00–RN12、批准发布闸及 RET01–RET22。
- [独立探针](../../skills/harness-engineering-patterns/references/patterns/collaboration/collaboration-loop-observability.md)：RP00–RP11、RM01–RM27、数据质量、历史快照、报告和 RPT01–RPT22。
- [共享交互契约](../../skills/harness-engineering-patterns/references/adversarial-review-contract.md)：版本 `0.1.0`，同时内嵌到执行与探针两份规约。
- [来源映射](../../skills/harness-engineering-patterns/references/adversarial-review-source-map.json)：文件及逐行 SHA-256、完整清单、中英说明和待集成状态。
- [维护脚本](../../skills/harness-engineering-patterns/scripts/sync_adversarial_review_docs.py)：校验来源与完整映射后更新生成区块，保留手写内容；写入前预检两份文档。

技能入口、模式目录、协作导论、注册表和矩阵 HTML 已同步。保留稳定编号 `PATTERN_0045`、42 个矩阵单元及 `draft` 成熟度；草稿建议的编号仅作出处别名。已有未提交内容继续保留，没有执行提交、推送或部署。

## 实现状态 / Implementation Status

| 层次 / Layer | 当前状态 / Status |
| --- | --- |
| 现有通用协作参考内核 / Shared collaboration reference | 已有精确结果版本、角色分离、评审准入及阻断异议校验。 / Existing checks cover current result versions, designated roles, review acceptance and blockers. |
| 本次专用控制规约 / Dedicated review specification | 已完成可维护规格，版本 `0.1.0`；与共享来源 `2.0.0`、执行配置 `3.0.0` 分开。 / Complete maintained specification, separate from the shared profile. |
| 专用回执、风险清单控制、持久补数接收、发布核对 / Dedicated execution services | 尚未实现或部署；RET01–RET22 保持 `pending`。 / Not implemented/deployed; integration cases remain pending. |
| 专用探针采集及 RM 计算器 / Dedicated collection and metric calculators | 尚未实现或部署；RPT01–RPT22 保持 `pending`；不输出虚构测量值。 / Pending implementation and integration; no fabricated measurements. |

通用内核的相关现状可在 [collaboration_protocol.py](../../skills/harness-engineering-patterns/runtime/collaboration_protocol.py) 中核对。专用规格不更改现有可执行协议含义，也不把 CSM25–CSM26 当作全部 RM 指标的实现。

后续运行时接入可依次实现：不可变版本与证据、必审责任及异议账本；批准与回执验证；条件发布意图及外部核对；最后接入可选探针和 RM 投影。每阶段以对应 RET/RPT 场景验收，不能用文档测试代替业务验证。

## 验证 / Verification

- 新增维护测试：18 项通过，覆盖来源遗漏、原定义漂移、协议不一致、双端预检、保留手写内容、幂等同步及不虚报实现状态。 / All 18 maintenance tests passed.
- 全量回归：828 项通过、243 个子测试通过、3 项跳过。跳过项均为未配置 `HARNESS_POSTGRES_DSN` 的真实 PostgreSQL 集成测试。 / Full regression: 828 passed, 243 subtests passed, 3 PostgreSQL tests skipped because no DSN was configured.
- 技能完整校验：0 错误、18 条既有导航提示，与修改前一致；`quick_validate.py` 通过。 / Skill validation: zero errors and the same 18 pre-existing navigation warnings; quick validation passed.
- 矩阵 HTML 与当前来源重新生成结果完全一致，文档导航链接有效，`git diff --check` 通过。 / Generated HTML, navigation and whitespace checks passed.
- 上述验证不等于 RET/RPT 的业务集成验收，也不证明专用运行时已经部署。 / These checks do not constitute business integration acceptance or deployment evidence.

机器记录见 [verification.json](verification.json)，项目 Trace 见 [trace.yaml](trace.yaml)。
