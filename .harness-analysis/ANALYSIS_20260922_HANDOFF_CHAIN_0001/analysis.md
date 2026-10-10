# Handoff Chain Engineering Update / 交接链工程模式完善

The requested change improves the existing `PATTERN_0043` design asset at `COG_COLLABORATION__TOP_CHAIN`. The two supplied documents are design evidence; their embedded execution prompts, placeholders and external examples do not authorize running a business workflow. / 本次完善现有交接链工程模式，两份附件作为设计依据；其中的执行提示、占位编号与外部示例不构成本次业务执行授权。

## Findings and changes / 缺口与改进

| Previous gap / 原有缺口 | Maintained design / 完善内容 |
| --- | --- |
| A context package and receiver acceptance were treated as enough to transfer responsibility. / 上下文包与接收意见被视为足以转移责任。 | Separate candidate, acceptance and durable commit; atomically persist the next manifest, receipt, owner and notification with conditional version/epoch checks. / 区分候选、验收与持久提交，以版本和代次条件检查原子保存下一版清单、回执、责任人与通知。 |
| State, attempts, transport redelivery and external intent were not distinguished. / 状态、执行尝试、传输重发与外部意图未充分区分。 | Freeze scope and immutable versions; retain distinct stage, attempt, handoff, operation and event identities. / 固定作用域及不可变版本，区分阶段、尝试、交接包、业务操作与事件身份。 |
| Content correctness and factual bindings lacked executable acceptance requirements. / 内容正确性与事实绑定缺乏具体验收要求。 | Require eight gates, independently recomputed content digests, version-bound evidence and semantic coverage of titles, body, attachments and payloads. / 定义八道闸门，独立重算内容摘要，并以版本化证据核验标题、正文、附件和载荷。 |
| Rejection and retry did not address external effects or concurrent head changes. / 拒收与重试未覆盖外部效果及并发头版本变化。 | Preserve the current head on rejected attempts; reconcile unknown operations by their original intent; define bounded local recovery and separately authorized compensation. / 拒收不回退当前头版本；按原业务意图查证未知效果，定义有界局部恢复与独立授权补偿。 |
| Probe metrics lacked expected populations, unknown states and trustworthy adoption rules. / 探针缺少应有对象集合、未知状态与可信采纳规则。 | Preserve all 30 source definitions, observation cutoffs, independent denominators and coverage; bind read-only patches to exact versions and durable adoption receipts. / 保留全部 30 项来源定义、观察截止点、独立分母与覆盖率，将只读补丁绑定精确版本及持久采纳回执。 |
| Pattern prose had no complete source inventory or drift checks. / 模式正文缺少完整来源清单与漂移校验。 | Preserve source snapshots and hashes; validate complete inventories and shared transport templates before updating bounded document sections. / 保留来源快照和摘要，先核对完整清单及共享传输模板，再更新有界文档区块。 |

Original assets are preserved under [before](before/collaboration-chain.md); supplied sources are preserved as [execution](sources/execution.md) and [probe](sources/probe.md). / 修改前资产及附件快照均保留，可追溯原有行为和规格来源。

## Assets and scope / 资产与范围

- [Execution design / 执行模式](../../skills/harness-engineering-patterns/references/patterns/collaboration/collaboration-chain.md): 9 nodes, 12 invariants, 8 acceptance gates, 12 recovery reasons, 6 variants and 12 pending acceptance scenarios. / 9 个节点、12 条不变量、8 道闸门、12 类恢复原因、6 个变体和 12 个待验收场景。
- [Independent probes / 独立探针](../../skills/harness-engineering-patterns/references/patterns/collaboration/collaboration-chain-observability.md): 8 nodes, 12 checks, 30 metric definitions and 17 pending validation scenarios. / 8 个节点、12 项检查、30 项指标定义和 17 个待验证场景。
- [Shared contract / 共享契约](../../skills/harness-engineering-patterns/references/handoff-chain-contract.md): source interface `1.0`; scope, version, content, permission and observation adoption semantics. / 来源接口 `1.0`，规范作用域、版本、内容、权限与观测采纳。
- [Source map / 来源映射](../../skills/harness-engineering-patterns/references/handoff-chain-source-map.json) and [synchronizer / 同步校验器](../../skills/harness-engineering-patterns/scripts/sync_handoff_chain_docs.py): source fidelity, bilingual summaries, stable IDs and preflighted maintenance. / 来源保真、双语说明、稳定编号与写入前预检。

The 42-cell taxonomy, `PATTERN_0043`, `draft` maturity and zero local business-evidence counts remain unchanged. Source placeholder `PATTERN_XXXX` is provenance only. Document version `0.1.0`, dedicated protocol `1.0`, shared collaboration source `2.0.0` and executable profile `3.0.0` are distinct. / 保留 42 单元分类、既有模式编号、草案成熟度和零项本地业务证据；来源占位符仅作出处，文档版本、专用接口、共享来源协议与本地执行配置分别管理。

## Verification boundary / 验证边界

This update supplies specifications and executable document-maintenance checks. It does not implement a production handoff transaction service, authorization gateway, external reconciliation adapter or HCM metric calculator. Business scenarios remain pending; passing maintenance tests cannot promote them or establish production reliability. / 本次交付规格及可执行的文档维护校验，不实现生产交接事务服务、授权网关、外部查证适配器或 HCM 指标计算器；业务场景保持待验收，文档测试通过不能替代业务验证或证明生产可靠性。

Actual checks and their results are recorded in [verification.json](verification.json); the scoped project observation is in [trace.yaml](trace.yaml). / 实际检查结果及范围化项目观察分别记录在验证文件与 Trace 中。

Validation completed: 48 dedicated maintenance tests passed; full regression passed 897 tests and 243 subtests, with 3 real PostgreSQL tests skipped because `HARNESS_POSTGRES_DSN` was not configured. Skill validation reported zero errors and 18 navigation warnings outside the handoff assets. Source/contract validation, generated HTML consistency, Skill metadata validation and whitespace checks passed. / 验证完成：48 项专项维护测试通过；全量回归 897 项及 243 个子测试通过，3 项真实 PostgreSQL 测试因未配置数据库跳过。技能校验零错误，18 条导航提示来自交接链资产以外。来源契约、HTML 一致性、技能元信息及空白检查均通过。

Concurrent governance work in the shared workspace was preserved; the full regression result describes that combined working-tree snapshot, while this change owns only the handoff assets and their integration points. / 保留共享工作区的并行治理修改；全量回归结果针对当时共享工作区快照，本次仅负责交接链资产及其接入点。
