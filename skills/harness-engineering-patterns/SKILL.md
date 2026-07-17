---
name: harness-engineering-patterns
description: Use when a request explicitly needs Agent Harness architecture analysis, cognition x topology mapping, workflow or engineering node diagnosis, a governed reasoning execution flow, workflow observability probes, pattern governance, evidence-backed EIR, or Skillization decisions. / 当请求明确需要 Agent Harness 架构分析、认知 x 拓扑映射、工作流或工程节点诊断、受治理的推理执行流程、工作流可观测性探针、模式治理、有证据的 EIR 或 Skill 化决策时使用。
---

# Harness Engineering Patterns / Harness 工程模式

## Overview / 概览

Compile a Workflow / Harness Source / 工作流程 / Harness 源码 into an Engineering Intermediate Representation / 工程中间表示, map it onto cognition x topology coordinates, and produce Evidence + Evaluation + Governance / 证据 + 评估 + 治理 decisions that can be verified and maintained. / 将工作流程或 Harness 源码编译为工程中间表示，映射到认知 x 拓扑坐标，并产出可验证、可维护的证据、评估与治理决策。

Treat `references/registry.json` as the authoritative structural source. Treat the matrix, catalog, cell guides, design files, observability files, and HTML as maintained views or detailed guidance. / 将 `references/registry.json` 视为权威结构数据源；将矩阵、目录、纵轴导论、设计文件、可观测性文件和 HTML 视为维护视图或详细指导。

## When To Use / 适用场景

- Analyze an Agent Harness repository, runtime, tool system, memory system, sandbox, permission layer, subagent system, or event log. / 分析 Agent Harness 仓库、runtime、工具系统、记忆系统、沙箱、权限层、子 Agent 系统或事件日志。
- Diagnose a workflow or engineering node whose capability, topology, feedback, memory, ownership, or governance is unclear. / 诊断能力、拓扑、反馈、记忆、归属或治理不清的工作流或工程节点。
- Produce an EIR, matrix mapping, pattern card, evidence table, governance gap, evaluation, or Skillization decision. / 生成 EIR、矩阵映射、模式卡、证据表、治理缺口、评价或 Skill 化决策。
- Evaluate whether repeated workflow evidence justifies promoting an extension candidate into a named pattern. / 评价反复工作流证据是否足以把扩展候选晋升为命名模式。

## When Not To Use / 不适用场景

- Ordinary code review that does not need Harness architecture mapping. / 不需要 Harness 架构映射的普通代码评审。
- Isolated bug diagnosis where the task is to find one root cause, not classify a workflow. / 只需定位单一根因、不需要工作流分类的单点缺陷诊断。
- General product or UX workflow critique that does not need the cognition x topology matrix. / 不需要认知 x 拓扑矩阵的通用产品或 UX 流程评审。
- Simple implementation, rewriting, formatting, or factual questions with no reusable pattern decision. / 不涉及可复用模式决策的简单实现、改写、格式调整或事实问答。

Use the focused domain Skill instead when another Skill directly covers the task. / 当其他领域 Skill 能直接覆盖任务时，使用更聚焦的领域 Skill。

## Compiler Spine / 编译主线

1. Read `references/compiler-workflow.md` and classify the input as `workflow`, `harness_source`, or `mixed`. / 读取 `references/compiler-workflow.md`，将输入分类为 `workflow`、`harness_source` 或 `mixed`。
2. Read `references/eir-schema.md` and maintain evidence-backed nodes, components, flows, mappings, patterns, evaluations, and governance items. / 读取 `references/eir-schema.md`，维护有证据的节点、组件、流、映射、模式、评价和治理项。
3. For workflow or engineering-node diagnosis, use Trace Insert / Trace 插入 before Pattern Selection Card / 模式选型卡. / 对工作流或工程节点诊断，先执行 Trace 插入，再运行模式选型卡。
4. For a reasoning runtime, read `references/reasoning-execution-flow.md` before the selected reasoning cell; use the contracts under `schemas/` as normative, `runtime/reasoning_router.py` as the deterministic route reference, `runtime/reasoning_runtime.py` as the executable semantics and event-conformance kernel, and `runtime/reasoning_artifacts.py` as the producer-side hash, Schema, cross-binding, and evidence-gate guard; establish identities, input and reasoning contracts, budgets, validators, switches, stop conditions, release-bound public claims, authoritative gate time, and terminal output without collecting private chain-of-thought. When the selected cell is `reasoning-chain`, also read `references/reasoning-chain-factory.md`; compile the explicit blueprint and sealed contract through `runtime/reasoning_chain_factory.py` using the blueprint, plan, and checkpoint-validation Schemas; retain the original blueprint and contract for deterministic session reconstruction, and never bypass `ChainPlanSession` for step or candidate execution. Supply versioned, self-hashed evidence records rather than bare references, reserve the exact compiled allocation before step dispatch, and settle actual use against that reservation at close. / 对推理运行时，先读取 `references/reasoning-execution-flow.md`，再读取已选推理单元；以 `schemas/` 下的契约为规范，以 `runtime/reasoning_router.py` 为确定性路由参考，以 `runtime/reasoning_runtime.py` 为可执行语义与事件一致性内核，以 `runtime/reasoning_artifacts.py` 为生产端哈希、Schema、跨绑定与证据门闸门；建立标识、输入与推理契约、预算、验证器、换路、停止条件、放行绑定的公开声明、权威闸门时间和终态输出，且不采集私密思维过程。所选单元为 `reasoning-chain` 时，还要读取 `references/reasoning-chain-factory.md`；使用蓝图、计划与检查点验证 Schema，通过 `runtime/reasoning_chain_factory.py` 编译显式蓝图和密封契约；保留原始蓝图与契约以便确定性重建会话，且步骤与候选执行均不得绕过 `ChainPlanSession`。应提供带版本和自哈希的证据记录而非裸引用，在步骤分派前预留编译出的精确预算，并在关闭时针对该预留结算实际用量。
   The compatibility entrypoint is `runtime/reasoning_chain_factory.py`; static compilation and validation live in `runtime/reasoning_chain_compiler.py`, while guarded execution lives in `runtime/reasoning_chain_session.py`. For durable local events, construct `JsonlEventStore`; keep the sealed plan and contract beside its stream, and use a transactional database adapter for high-volume or multi-writer production. A tool step must bind one exact versioned read-only tool and authorization policy, reserve exactly one call, and pass the same concrete `authorization_binding` through `dispatch_readonly_tool()` and `observe_readonly_tool()`; configure a trusted `tool_authorizer`, fail closed unless it returns exact `true`, and never persist raw tool input/output. After the final checkpoint passes, call `set_candidate(candidate, evidence_records=[...])` with higher-version candidate-bound evidence revisions whose `predecessor_evidence_binding` exactly covers the ordered final-claim step evidence. / 兼容入口为 `runtime/reasoning_chain_factory.py`；静态编译与校验位于 `runtime/reasoning_chain_compiler.py`，受守卫执行位于 `runtime/reasoning_chain_session.py`。本地事件需要持久化时构造 `JsonlEventStore`，把封存计划与契约同事件流并置保存；高吞吐或多写者生产环境使用事务数据库适配器。工具步骤必须绑定一个确切版本的只读工具与授权策略、精确预留一次调用，并向 `dispatch_readonly_tool()` 与 `observe_readonly_tool()` 传入同一个具体 `authorization_binding`；配置可信 `tool_authorizer`，只有精确返回 `true` 才放行，且不得持久化原始工具输入输出。末个检查点通过后，调用 `set_candidate(candidate, evidence_records=[...])`，传入更高版本且绑定候选的证据修订，其 `predecessor_evidence_binding` 必须精确覆盖有序的最终命题步骤证据。
5. For workflow instrumentation, observability gaps, metrics, alerts, or runtime feedback, read `references/workflow-observability-probes.md`; use `runtime/probe_dependency_matrix.json`, `runtime/metric_registry.json`, and `runtime/reasoning_metrics.py`; call `resolve_required_probes` for the selected runtime configuration, then preserve field-level provenance plus missing, unknown, not-applicable, observed-zero, and computed states. For strict-chain diagnostics, compute registered `candidate_evidence_lineage_integrity_rate` and `readonly_tool_lifecycle_completion_rate` only from complete candidate and dispatch inventories; keep them non-gating until owned thresholds and promotion evidence are approved. / 对工作流埋点、可观测性缺口、指标、告警或运行反馈，读取 `references/workflow-observability-probes.md`；使用 `runtime/probe_dependency_matrix.json`、`runtime/metric_registry.json` 和 `runtime/reasoning_metrics.py`；针对已选运行配置调用 `resolve_required_probes`，并保留字段级来源以及缺失、未知、不适用、观测零值和已计算状态。严格链诊断仅在候选与分派清单完整时计算已注册的 `candidate_evidence_lineage_integrity_rate` 与 `readonly_tool_lifecycle_completion_rate`；在负责人阈值和晋升证据获批前保持非门控。
6. For Harness source, read `references/harness-source-analysis.md` and run Detect / Classify / Filter / Map / Verify. / 对 Harness 源码，读取 `references/harness-source-analysis.md`，执行找主循环、归类、过滤、映射和验证。
7. For pattern or Skill packaging, read `references/pattern-skill-packaging.md`. / 对模式或 Skill 封装，读取 `references/pattern-skill-packaging.md`。
8. For quality, evidence, risk, and governance, read `references/evaluation-governance.md` and `references/failure-modes.md`. / 对质量、证据、风险和治理，读取 `references/evaluation-governance.md` 与 `references/failure-modes.md`。
9. For controlled extension, read `references/extension-rules.md`; for an end-to-end example, read `references/example-compilation.md`. / 对受控扩展读取 `references/extension-rules.md`；需要端到端示例时读取 `references/example-compilation.md`。

## Automatic Engineering Node Analysis / 工程节点自动分析

When the request is to analyze an engineering node, automatically run Trace Insert / 自动运行 Trace 插入 before any matrix decision. / 当请求是分析工程节点时，在任何矩阵决策前自动运行 Trace 插入。

Collect the node responsibility, owner, boundary, trigger, inputs, outputs, current behavior, failure signals, risk, and available evidence. Then run ASSESS / 评估, ROUTE / 判拓扑, and SELECT / 查矩阵 using `references/pattern-selection-card.md`. / 采集节点职责、负责人、边界、触发、输入、输出、当前行为、失败信号、风险和可用证据；然后使用 `references/pattern-selection-card.md` 执行评估、判拓扑和查矩阵。

If evidence is incomplete, return a preliminary / 初步 result with gaps and verification tasks. Block only final pattern promotion or high-confidence selection; do not suppress useful preliminary analysis. / 如果证据不完整，输出带缺口和验证任务的初步结果；只阻断最终模式晋升或高置信选型，不压制有用的初步分析。

## Workflow And Node Diagnosis / 工作流与节点诊断

1. Read `references/workflow-nodes.md` and split by business responsibility, input, output, owner, decision, and risk. / 读取 `references/workflow-nodes.md`，按业务职责、输入、输出、负责人、决策和风险拆分节点。
2. Read `references/axes.md`, then select the smallest capability and topology that preserve required dependencies. / 读取 `references/axes.md`，选择能保留必要依赖的最小能力与拓扑。
3. Read `references/matrix-index.md`, the relevant `references/patterns/<capability-key>/cell.md`, the selected design file, and its observability file. / 读取 `references/matrix-index.md`、相关纵轴导论、已选设计文件及其可观测性文件。
4. Read `references/pattern-catalog.md` for named candidates and `references/diagnosis-method.md` for concrete workflow modification. / 使用 `references/pattern-catalog.md` 查命名候选，使用 `references/diagnosis-method.md` 形成具体工作流修改。
5. Cite evidence for every architecture judgment and name at least one failure mode, mitigation, verification method, and observation point. / 每个架构判断都引用证据，并至少命名一个失败模式、缓解方式、验证方法和观察点。

## Harness Source Compilation / Harness 源码编译

1. Detect the main loop and control plane before peripheral implementation details. / 先定位主循环和控制面，再读边缘实现细节。
2. Classify retained components into perception, memory, reasoning, action, reflection, collaboration, and governance. / 将保留组件归类到感知、记忆、推理、行动、反思、协作和治理。
3. Keep files that change context, state, tools, permissions, execution, retry, audit, or handoff; defer boilerplate until needed. / 保留会改变上下文、状态、工具、权限、执行、重试、审计或交接的文件；样板内容按需延后。
4. Map each component to one primary coordinate, add secondary coordinates only when they change the diagnosis, and attach evidence before extracting patterns. / 将每个组件映射到一个主坐标；只有副坐标会改变诊断时才补充，并在抽取模式前挂载证据。

## Output Profiles / 输出档位

Choose the smallest profile that satisfies the request. / 选择能满足请求的最小档位。

### quick / 快速

Return coordinate, evidence, diagnosed problem, practical adjustment, risk, and verification. / 输出坐标、证据、诊断问题、可执行调整、风险和验证方式。

### standard / 标准

Return an EIR slice, node or component map, ASSESS / ROUTE / SELECT result, selected patterns, observability metrics, risks, governance, verification, and a project-local Trace proposal. / 输出 EIR 切片、节点或组件图、评估/判拓扑/查矩阵结果、已选模式、可观测性指标、风险、治理、验证和项目本地 Trace 建议。

### full / 完整

Return the complete compiler output: scope, main flow, EIR, noise filter, matrix mapping, pattern and Skillization candidates, evidence verification, evaluation scores, governance gaps, failure modes, extension analysis, and implementation plan. / 输出完整编译结果：范围、主流程、EIR、噪声过滤、矩阵映射、模式与 Skill 化候选、证据验证、评价分数、治理缺口、失败模式、扩展分析和实施规划。

## Runtime Trace / 运行 Trace

Read `references/trace-schema.md`. Normal use produces a Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml`. / 读取 `references/trace-schema.md`。普通使用在 `.harness-analysis/<analysis_id>/trace.yaml` 生成 Trace 建议。

Bundled `references/patterns/*/trace.md` files are curated historical snapshots, not runtime state. Modify curated history only when the user explicitly requests a Skill evidence update and the evidence has been reviewed. / Skill 内置 `references/patterns/*/trace.md` 是精选历史快照，不是运行状态。只有用户明确要求更新 Skill 证据且证据经过复核时，才能修改精选历史。

If the project-local destination is unavailable, return the Trace payload in the response with the intended path; never redirect runtime data into bundled history. / 如果项目本地目标不可用，在响应中返回 Trace 载荷和预期路径；绝不把运行数据重定向到内置历史。

## Constraints / 约束

- Keep all Skill metadata and core instructions bilingual in Chinese and English. / 所有 Skill 元数据和核心说明保持中英双语。
- Keep newly created Skill resources under `.\skills`. / 新建 Skill 资源统一放在 `.\skills` 下。
- Keep stable IDs and registry records after introduction; deprecate instead of reusing. / 稳定 ID 与注册表记录引入后保持不变；使用废弃标记，不复用。
- Treat `registry.json` as source data and Markdown matrices as maintained views. / 将 `registry.json` 视为源数据，将 Markdown 矩阵视为维护视图。
- Cite source, test, official documentation, config, log, Trace, runtime record, or protocol evidence for every architecture judgment. / 每个架构判断都引用源码、测试、官方文档、配置、日志、Trace、运行记录或协议证据。
- Treat README evidence as supporting evidence, not the strongest proof. / README 只作为辅助证据，不作为最强证明。
- Prefer controlled extension over forcing a workflow into an inaccurate cell. / 优先受控扩展，不强行把工作流塞入不准确的单元。
- Do not invent patterns to fill empty cells. Promote a candidate only with repeated evidence, failure-path checks, and explicit provenance. / 不为填满空白单元而虚构模式；只有存在反复证据、失败路径检查和明确来源时才晋升候选。
- After changing reasoning contracts, runtime behavior, probes, or metrics, run the schema, runtime, metric, registry, and full test suites; a structural marker pass alone is not runtime verification. / 修改推理契约、运行时行为、探针或指标后，必须运行 Schema、运行时、指标、注册表及全量测试；仅结构标记通过不代表运行时已验证。
