# Memory Trace / 记忆追踪

## Trace / 追踪

Use this file to record what happened after a memory pattern was applied to a workflow. / 使用本文档记录记忆模式应用到工作流之后发生了什么。

Boundary note / 边界说明: entries carry pattern-level lessons; application-specific identifiers inside them (such as Novel Studio stage-output ids) are evidence pointers frozen at write time, not current application state. During Trace Insert, reuse the lesson, but verify any concrete id or status against the application's own data before acting on it. / 记录承载模式层经验；其中的应用专属标识（如 Novel Studio 阶段产物编号）是写入时刻冻结的证据指针，不代表应用当前状态。Trace 插入时可复用经验，但任何具体编号或状态在采用前必须与应用自身数据核对。

## Usage Log / 使用日志

Add new entries below this template. / 在此模板下方追加新记录。

### Entry Template / 记录模板

- Date / 日期:
- Workflow / 工作流:
- Cell / 交织点:
- Pattern Used / 使用模式:
- Before / 使用前:
- Adjustment / 调整:
- Outcome / 结果:
- Evidence / 证据:
- Follow-up / 后续:
- Owner / 负责人:

## Entries / 记录

### 2026-07-02 / 2026-07-02

- Date / 日期: 2026-07-02
- Workflow / 工作流: Add Retrieval-Augmented execution flow and observability probes to the Memory x Chain cell. / 将检索增强执行流程与可观测性探针写入记忆 x 链式交织点。
- Cell / 交织点: memory-chain / 记忆 x 链式
- Pattern Used / 使用模式: RAG Pipeline / RAG 管线
- Before / 使用前: The cell contained a compact RAG placeholder and generic observability bullets. / 该单元仅包含简短 RAG 占位内容和通用可观测性要点。
- Adjustment / 调整: Expanded the design file into a bilingual evidence-grounded RAG execution flow covering task normalization, boundary splitting, constraint completion, source selection, retrieval planning, candidate recording, evidence usability validation, evidence package construction, grounded reasoning, output gates, action-plan safeguards, trace records, output contract, and failure modes. Expanded the observability file into probe records, supplement packages, observation positions, core metrics, probe catalog, default gate rules, scenario probe sets, and report templates. / 将设计文件扩展为中英双语证据型 RAG 执行流程，覆盖任务标准化、边界拆分、约束补齐、来源选择、检索规划、候选记录、证据可用性校验、证据包构建、扎根推理、输出门控、动作计划防护、追踪记录、输出契约和失败模式。同步将可观测性文件扩展为探针记录、补数包、观测位置、核心指标、探针目录、默认门控规则、场景化探针组合和报告模板。
- Outcome / 结果: The Memory x Chain cell now carries the corresponding engineering-pattern location for retrieval-augmented workflows and can be used as an executable RAG pipeline protocol, not just a generic pattern label. / 记忆 x 链式单元现在承载检索增强工作流的对应工程模式位置，可作为可执行 RAG 管线协议使用，而不仅是通用模式标签。
- Evidence / 证据: User requests for "检索增强 的 执行流程", "检索增强 的 可观测性指标", and "写入 harness-engineering-patterns 下对应的位置"; updated memory-chain.md and memory-chain-observability.md. / 用户要求“检索增强 的 执行流程”、“检索增强 的 可观测性指标”和“写入 harness-engineering-patterns 下对应的位置”；已更新 memory-chain.md 与 memory-chain-observability.md。
- Follow-up / 后续: Validate repository tests and regenerate visualization only if the HTML artifact needs refresh. / 验证仓库测试；仅当 HTML 产物需要刷新时再重新生成可视化。
- Owner / 负责人: Codex

### 2026-07-02 / 2026-07-02

- Date / 日期: 2026-07-02
- Workflow / 工作流: Improve the Progress Tracking execution flow in the Memory x Orchestration cell. / 完善记忆 x 编排交织点中的进度追踪执行流程。
- Cell / 交织点: memory-orchestration / 记忆 x 编排
- Pattern Used / 使用模式: Progress Tracking / 进度追踪
- Before / 使用前: The cell contained a compact placeholder template and generic observability checklist. / 该单元仅包含简短占位模板和通用可观测性清单。
- Adjustment / 调整: Replaced the design file with a bilingual full execution flow covering goal contracts, milestone gates, narrative state, scheduling state, mechanical state, progress events, probe protocol, recovery packages, exception handling, completion conditions, and failure modes. Expanded the observability file into probes, metrics, alert rules, health levels, and observation reports. / 将设计文件替换为中英双语完整执行流程，覆盖目标契约、里程碑闸门、叙事态、调度态、机械态、进度事件、探针协议、恢复包、异常处理、完成条件和失败模式。同步扩展可观测性文件，加入探针、指标、告警规则、健康等级和观测报告。
- Outcome / 结果: The Progress Tracking cell can now be used as an executable engineering-mode process for long-running tasks, including the hard rule that unknown confirmations must stop default continuation. / 进度追踪单元现在可作为长程任务的工程模式执行流程使用，并包含“确认项未知时不得默认继续”的硬规则。
- Evidence / 证据: User request to write Progress Tracking into the corresponding harness-engineering-patterns location and updated memory-orchestration files. / 用户要求将进度追踪写入 harness-engineering-patterns 对应位置，以及已更新的 memory-orchestration 文件。
- Follow-up / 后续: Run validation and regenerate visualization only if the user wants the HTML artifact refreshed. / 运行校验；仅当用户需要刷新 HTML 产物时再重新生成可视化。
- Owner / 负责人: Codex

### 2026-07-02 / 2026-07-02

- Date / 日期: 2026-07-02
- Workflow / 工作流: Add Failure Diary execution flow and observability metrics to the Memory x Loop cell. / 将失败日记执行流程与可观测性指标写入记忆 x 循环交织点。
- Cell / 交织点: memory-loop / 记忆 x 循环
- Pattern Used / 使用模式: Failure Diary / 失败日记
- Before / 使用前: The cell only contained a generic failure-record placeholder and generic observability bullets. / 该单元只有通用失败记录占位内容和通用可观测性要点。
- Adjustment / 调整: Replaced the placeholder with a bilingual failure diary execution workflow, review state machine, recall rules, governance constraints, probe installation points, metric catalog, output templates, and matrix/catalog labels. / 替换为中英双语失败日记执行流程、审查状态机、召回规则、治理约束、探针安装点、指标目录、输出模板，并同步矩阵与目录标签。
- Outcome / 结果: The Memory x Loop cell now has the corresponding engineering-pattern location for the user-provided failure diary workflow and observability probe documents. / 记忆 x 循环单元现在承载了用户提供的失败日记执行流程和可观测性探针对应的工程模式位置。
- Evidence / 证据: User-provided documents "失败日记执行流程" and "失败日记工作流可观测性探针"; updated memory-loop.md and memory-loop-observability.md. / 用户提供的《失败日记执行流程》和《失败日记工作流可观测性探针》；已更新 memory-loop.md 与 memory-loop-observability.md。
- Follow-up / 后续: Validate repository tests and regenerate visualization only when the HTML artifact needs refresh. / 验证仓库测试；仅当 HTML 产物需要刷新时再重新生成可视化。
- Owner / 负责人: Codex

### 2026-07-02 / 2026-07-02

- Date / 日期: 2026-07-02
- Workflow / 工作流: Add Layered Retention execution flow to the Memory x Hierarchy cell. / 将分层保留执行流程写入记忆 x 层级交织点。
- Cell / 交织点: memory-hierarchy / 记忆 x 层级
- Pattern Used / 使用模式: Layered Retention / 分层保留
- Before / 使用前: The cell was an extension candidate with no concrete execution process. / 该单元为扩展候选，尚无具体执行流程。
- Adjustment / 调整: Replaced the placeholder with a bilingual standalone execution flow, probe protocol, catalog entries, matrix label, and memory-row guide updates. / 替换占位内容，写入中英双语可独立执行流程、探针协议、目录条目、矩阵标签和记忆行导论更新。
- Outcome / 结果: The pattern now defines layer models, input and output contracts, twelve execution nodes, write routing, lifecycle handling, probe interaction, failure modes, and minimum configuration. / 该模式现在定义层级模型、输入输出契约、十二个执行节点、写入路由、生命周期处理、探针交互、失败模式和最小配置。
- Evidence / 证据: User-provided document "流程_分层保留_0001" and updated files in this memory pattern folder. / 用户提供的《流程_分层保留_0001》及本记忆模式目录下的更新文件。
- Follow-up / 后续: Validate tests and regenerate visualization only if the user wants the HTML artifact refreshed. / 验证测试；仅当用户需要刷新 HTML 产物时再重新生成可视化。
- Owner / 负责人: Codex

### 2026-07-02 / 2026-07-02

- Date / 日期: 2026-07-02
- Workflow / 工作流: Optimize Layered Retention observability metrics and probe protocol. / 优化分层保留的可观测性指标与探针协议。
- Cell / 交织点: memory-hierarchy / 记忆 x 层级
- Pattern Used / 使用模式: Layered Retention / 分层保留
- Before / 使用前: The observability file contained a compact probe protocol and core metric groups. / 可观测性文件包含概括版探针协议与核心指标组。
- Adjustment / 调整: Expanded the file from the user-provided probe document into a bilingual probe system with data models, 18 probes, offline and interactive modes, thresholds, aggregate health views, alert rules, feedback packages, report templates, and engineering node registration. / 根据用户提供的探针文档扩展为中英双语探针系统，包含数据模型、18 个探针、离线与交互模式、阈值、聚合健康视图、告警规则、回填包、报告模板和工程节点注册项。
- Outcome / 结果: The observability side now matches the Layered Retention execution flow and can be used as an executable probe protocol, not just a metric checklist. / 可观测性侧现在与分层保留执行流程匹配，可作为可执行探针协议使用，而不仅是指标清单。
- Evidence / 证据: User-provided document "探针_分层保留_0001" and updated memory-hierarchy-observability.md. / 用户提供的《探针_分层保留_0001》及更新后的 memory-hierarchy-observability.md。
- Follow-up / 后续: Validate tests and regenerate visualization only if the user wants the HTML artifact refreshed. / 验证测试；仅当用户需要刷新 HTML 产物时再重新生成可视化。
- Owner / 负责人: Codex

### 2026-07-03 / 2026-07-03

- Date / 日期: 2026-07-03
- Workflow / 工作流: Track the rerun of Novel Studio project-10 story_macro full-story bible. / 追踪 Novel Studio project-10 的 story_macro 全本故事圣经重跑。
- Cell / 交织点: memory-orchestration / 记忆 x 编排
- Pattern Used / 使用模式: Progress Tracking / 进度追踪
- Before / 使用前: The latest known story_macro output was id 1447, and the rerun needed a recoverable record of target, command, result id, gate status, and follow-up boundary. / 重跑前已知最新 story_macro 产物为 1447，本次需要可恢复记录目标、命令、结果编号、门禁状态和后续边界。
- Adjustment / 调整: Captured before-state, executed the single-stage command, inspected output 1801, and wrote reasoning/governance/memory trace entries as the append-only ledger. / 记录重跑前状态，执行单阶段命令，检查产物 1801，并将推理、治理、记忆 trace 作为只追加账本写入。
- Outcome / 结果: New story_macro output id 1801 is ready; `macro_quality_gate` passed with score 100 and the rerun did not invoke volume, chapter, or body stages. / 新 story_macro 产物 1801 已就绪；`macro_quality_gate` 以 100 分通过，本次未调用分卷、拆章或正文阶段。
- Evidence / 证据: Command result returned `latest_output_id=1801`; inspection reported `markdown_has_bible=True`, `event_chain_count=12`, `volume_blueprint_count=6`, and `can_enter_volume_strategy=True`. / 命令结果返回 `latest_output_id=1801`；检查结果显示 `markdown_has_bible=True`、`event_chain_count=12`、`volume_blueprint_count=6`、`can_enter_volume_strategy=True`。
- Follow-up / 后续: If the user wants to continue, invoke `$novel-volume-cards project-10` as an independent stage and carry output 1801 as upstream evidence. / 如果用户要继续，应独立调用 `$novel-volume-cards project-10`，并将产物 1801 作为上游证据。
- Owner / 负责人: Codex

### 2026-07-03 Correction / 2026-07-03 更正

- Date / 日期: 2026-07-03
- Workflow / 工作流: Correct the project-10 rerun ledger after bad outputs 1801 and 1802 were identified. / 识别错误产物 1801 与 1802 后，更正 project-10 重跑账本。
- Cell / 交织点: memory-orchestration / 记忆 x 编排
- Pattern Used / 使用模式: Progress Tracking correction event / 进度追踪纠偏事件
- Before / 使用前: The ledger treated 1801 and downstream 1802 as the latest usable outputs. / 账本曾将 1801 及其下游 1802 当作最新可用产物。
- Adjustment / 调整: Marked outputs 1801 and 1802 as `superseded`, changed latest-output retrieval to skip unusable statuses, and added regression tests for both semantic contamination and superseded filtering. / 已将 1801 与 1802 标记为 `superseded`，修改最新产物读取以跳过不可用状态，并新增语义污染与 superseded 过滤回归测试。
- Outcome / 结果: Active project-10 outputs are now `story_macro_latest_id=1447` and `volume_strategy_latest_id=1595`; the bad rerun is retained only as audit history. / project-10 当前生效产物为 `story_macro_latest_id=1447` 与 `volume_strategy_latest_id=1595`；错误重跑仅作为审计历史保留。
- Evidence / 证据: Database readback returned 1447/1595 after correction; `tests/test_novel_planning_density.py tests/test_novel_independent_skills.py` passed 10 tests. / 更正后数据库读回 1447/1595；`tests/test_novel_planning_density.py tests/test_novel_independent_skills.py` 共 10 项测试通过。
- Follow-up / 后续: Future reruns should require a semantic consistency check before a structural gate can advance downstream planning. / 后续重跑必须在结构门放行前执行语义一致性检查。
- Owner / 负责人: Codex

### 2026-07-03 Repair / 2026-07-03 修复

- Date / 日期: 2026-07-03
- Workflow / 工作流: Track repaired project-10 planning outputs after semantic gate implementation. / 追踪语义门实现后的 project-10 修复规划产物。
- Cell / 交织点: memory-orchestration / 记忆 x 编排
- Pattern Used / 使用模式: Progress Tracking with invalidation and replacement / 带失效与替换的进度追踪
- Before / 使用前: Bad outputs 1801 and 1802 were invalidated, leaving older clean outputs 1447 and 1595 active. / 错误产物 1801 与 1802 已失效，较旧的干净产物 1447 与 1595 处于生效状态。
- Adjustment / 调整: After code repair, reran only the independent `story_macro` and `volume_strategy` stages for project-10. / 代码修复后，仅独立重跑 project-10 的 `story_macro` 与 `volume_strategy` 阶段。
- Outcome / 结果: Active repaired outputs are now `story_macro_latest_id=1803` and `volume_strategy_latest_id=1804`. / 当前生效修复产物为 `story_macro_latest_id=1803` 与 `volume_strategy_latest_id=1804`。
- Evidence / 证据: Database inspection reported both outputs `ready`, both semantic gates `passed`, and forbidden-term scans returned `[]`. / 数据库检查显示两个产物均为 `ready`，两个语义门均为 `passed`，禁用词扫描返回 `[]`。
- Follow-up / 后续: Keep 1801 and 1802 as superseded audit history; use 1803 and 1804 for further independent planning stages. / 保留 1801 与 1802 作为已废弃审计历史；后续独立规划阶段使用 1803 与 1804。
- Owner / 负责人: Codex

### 2026-07-07 / 2026-07-07

- Date / 日期: 2026-07-07
- Workflow / 工作流: Apply Progress Tracking and Failure Diary to OpenClaw Novel Studio current-session body flow. / 将进度追踪与失败日记应用到 OpenClaw Novel Studio 当前会话正文流程。
- Cell / 交织点: memory-orchestration + memory-loop / 记忆 x 编排 + 记忆 x 循环
- Pattern Used / 使用模式: Progress Tracking + Failure Diary / 进度追踪 + 失败日记
- Before / 使用前: `body_flow_trace` recorded only the state order and recovery package; quality repair emitted a temporary stagnation candidate that was not a governed, recallable diary card. / 使用前：`body_flow_trace` 只记录状态顺序和恢复包；质量修复只输出临时停滞候选，尚不是受治理、可召回的失败日记卡。
- Adjustment / 调整: Added goal contracts, milestone acceptance records, mechanical state, progress events, ledger observability, draft failure diary entries for no-change or stagnation, and enabled-entry recall into later preflight forbidden-inference cards. / 调整：加入目标契约、里程碑验收记录、机械状态、进度事件、账本可观测指标、no-change 或停滞时的草稿失败日记，以及已启用条目到后续预检禁止推断卡的召回。
- Outcome / 结果: The body flow is now more recoverable and can reuse reviewed failure lessons before repeating deterministic repair mistakes. / 结果：正文流程更可恢复，并能在重复确定性修复错误前复用已审查的失败经验。
- Evidence / 证据: Updated `src/novel/current_session_body.py`, `src/novel/body_preprocessor.py`, `src/novel/quality_repair_hook.py`, and related tests; `python -m pytest tests -q` passed 242 tests. / 已更新 `src/novel/current_session_body.py`、`src/novel/body_preprocessor.py`、`src/novel/quality_repair_hook.py` 及相关测试；`python -m pytest tests -q` 通过 242 项测试。
- Follow-up / 后续: Observe false-reminder rate and repeat-failure rate before promoting draft failure diary entries automatically. / 后续观察误召回率与重复失败率，再决定是否自动提升草稿失败日记条目。
- Owner / 负责人: Codex
