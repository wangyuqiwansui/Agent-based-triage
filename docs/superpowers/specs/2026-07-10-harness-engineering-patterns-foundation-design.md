# Harness Engineering Patterns Foundation Design / Harness 工程模式基础改造设计

**Status / 状态:** Approved approach / 已批准方案 A（兼容优先）
**Date / 日期:** 2026-07-10
**Scope / 范围:** `skills/harness-engineering-patterns`, its visualization generator, and focused repository tests. / `skills/harness-engineering-patterns`、对应可视化生成器及聚焦的仓库测试。

## Goal / 目标

Turn the existing Markdown-heavy Skill into a compatibility-preserving, machine-checkable engineering knowledge package without rewriting the 42-cell corpus in one pass. / 在不一次性重写 42 个交织点内容的前提下，把当前以 Markdown 为主的 Skill 改造成兼容现有结构、可机器校验的工程知识包。

The first implementation must establish one registry, deterministic validation, explicit provenance and maturity, project-local runtime traces, complete EIR and evaluation contracts, and bounded output profiles. / 首轮实现必须建立单一注册表、确定性校验、明确的来源与成熟度、项目本地运行 Trace、完整 EIR 与评价契约，以及有边界的输出档位。

## Non-Goals / 非目标

- Do not rewrite or shorten all 84 pattern and observability files in this phase. / 本阶段不重写或压缩全部 84 个模式与可观测性文件。
- Do not delete or relocate existing trace history. / 不删除或迁移既有 Trace 历史。
- Do not modify the current user change in `references/patterns/memory/trace.md`. / 不修改 `references/patterns/memory/trace.md` 中现有用户改动。
- Do not modify or remove the untracked `tests/__pycache__` artifact. / 不修改或删除未跟踪的 `tests/__pycache__` 产物。
- Do not add a third-party runtime dependency. / 不增加第三方运行时依赖。
- Do not push changes or open a pull request. / 不推送改动，也不创建拉取请求。

## Existing Constraints / 现有约束

- Skill metadata and core instructions remain bilingual in Chinese and English. / Skill 元数据和核心说明继续保持中英双语。
- Newly created Skill resources stay under `skills/harness-engineering-patterns`. / 新建 Skill 资源保留在 `skills/harness-engineering-patterns` 下。
- The current 7 x 6 matrix, 42 design files, 42 observability files, seven cell guides, and seven trace files remain addressable at their existing paths. / 当前 7 x 6 矩阵、42 个设计文件、42 个可观测性文件、7 个纵轴导论和 7 个 Trace 文件继续使用现有路径。
- Existing `PATTERN_0001` through `PATTERN_0022` identifiers are never renumbered or reused. / 现有 `PATTERN_0001` 至 `PATTERN_0022` 不重编号、不复用。
- The implementation follows test-first RED-GREEN-REFACTOR. / 实施遵循测试先行的 RED-GREEN-REFACTOR。

## Chosen Approach / 选定方案

Use a compatibility-first registry with validation, not full document generation. / 使用兼容优先的注册表加校验方案，不在本阶段全面生成文档。

`references/registry.json` becomes the authoritative structural source. Existing Markdown remains the human-readable view and detailed pattern content. A validator checks that every maintained view agrees with the registry. The visualization generator reads structural data from the registry while continuing to read long-form diagnostic content from Markdown where needed. / `references/registry.json` 成为权威结构数据源；现有 Markdown 继续承担人类可读视图和模式详情。校验器检查所有维护视图是否与注册表一致。可视化生成器从注册表读取结构数据，并在需要时继续从 Markdown 读取长篇诊断内容。

This approach avoids a high-risk bulk rewrite while removing silent drift between axes, matrix cells, pattern names, paths, source provenance, and maturity. / 该方案避免高风险的大规模重写，同时消除轴、矩阵单元、模式名称、路径、来源和成熟度之间的静默漂移。

## Architecture / 架构

### 1. Authoritative Registry / 权威注册表

Create `skills/harness-engineering-patterns/references/registry.json` using only JSON features supported by Python's standard library. / 创建 `skills/harness-engineering-patterns/references/registry.json`，仅使用 Python 标准库可处理的 JSON。

The registry contains: / 注册表包含：

- `schema_version` and Skill identity. / `schema_version` 与 Skill 身份。
- Pinned upstream source metadata for arXiv:2605.13850 v2. / 固定到 arXiv:2605.13850 v2 的上游来源元数据。
- Seven capabilities with `COG_*` IDs and bilingual names. / 7 个带 `COG_*` ID 和双语名称的能力。
- Six topologies with `TOP_*` IDs and bilingual names. / 6 个带 `TOP_*` ID 和双语名称的拓扑。
- Forty-two cells with stable `CELL_*` IDs, coordinate IDs, paths, status, provenance, maturity, and diagnostic use. / 42 个带稳定 `CELL_*` ID、坐标、路径、状态、来源、成熟度和诊断用途的单元。
- Pattern records, including the existing 22 seed IDs and matrix-pattern identity. / 模式记录，包括现有 22 个种子 ID 和矩阵模式身份。
- Governance rules, failure-mode references, and allowed enum values needed by validation. / 校验所需的治理规则、失败模式引用和枚举值。

Pattern identity rules: / 模式身份规则：

1. Preserve all existing `PATTERN_0001` through `PATTERN_0022` records unchanged. / 原样保留现有 `PATTERN_0001` 至 `PATTERN_0022`。
2. Reuse an existing ID only when the matrix pattern is the same named engineering concept, not merely a related concept at the same coordinate. / 仅当矩阵模式与既有记录是同一个命名工程概念时复用 ID，不能因为坐标相同或概念相关而复用。
3. Assign new non-colliding IDs after `PATTERN_0022` for named matrix patterns without an existing exact identity. / 对没有既有精确身份的命名矩阵模式，从 `PATTERN_0022` 之后分配不冲突的新 ID。
4. Extension candidates have a stable cell ID but no `pattern_id` until promotion. / 扩展候选拥有稳定 cell ID，但晋升前不分配 `pattern_id`。
5. Each named cell records `source_kind`, `source_name_en`, `local_name_en`, aliases, evidence count, domain count, and maturity. / 每个命名单元记录 `source_kind`、`source_name_en`、`local_name_en`、别名、证据数、领域数和成熟度。

### 2. Deterministic Validator / 确定性校验器

Create `skills/harness-engineering-patterns/scripts/validate_harness_skill.py`. / 创建 `skills/harness-engineering-patterns/scripts/validate_harness_skill.py`。

The validator is read-only and returns exit code 0 only when required contracts pass. Diagnostics are concise and bilingual. / 校验器只读；仅当必需契约全部通过时返回退出码 0。诊断信息保持简洁、双语。

Required checks: / 必需检查：

- JSON schema shape and required keys. / JSON 结构及必填键。
- Unique stable IDs and non-reuse of existing IDs. / 稳定 ID 唯一且既有 ID 未复用。
- Exactly 7 capabilities, 6 topologies, and 42 cells. / 恰好 7 个能力、6 个拓扑和 42 个单元。
- Every design and observability path exists and forms a pair. / 每个设计与可观测性路径存在并成对。
- Matrix index, catalog, cell guides, and pattern headers agree with registry names and statuses. / 矩阵索引、目录、纵轴导论及模式文件头与注册表名称和状态一致。
- Named cells have provenance and maturity; extension candidates have no invented pattern ID. / 命名单元有来源与成熟度；扩展候选没有虚构模式 ID。
- Required design and observability contract fields are present. / 必需设计与可观测性契约字段存在。
- Relative Markdown links resolve. / 相对 Markdown 链接可解析。
- EIR and evaluation contracts contain all declared sections and dimensions. / EIR 与评价契约包含全部已声明章节和维度。
- Static Skill guidance does not instruct default writes into bundled trace history. / 静态 Skill 说明不得指示默认写入 Skill 内置 Trace 历史。

Long reference navigation is a warning in this phase except for files over 500 lines, where a navigation section is required. / 本阶段长参考文件导航通常作为警告；超过 500 行的文件必须包含导航章节。

### 3. Visualization Compatibility / 可视化兼容

Update `scripts/generate_skill_visualization.py` so axes, topology, cell status, names, provenance, and paths come from the registry. Detailed snippets may still be read from Markdown. / 更新 `scripts/generate_skill_visualization.py`，使轴、拓扑、单元状态、名称、来源和路径来自注册表；详细片段仍可从 Markdown 读取。

The generated HTML keeps existing links and matrix counts. It adds provenance and maturity without changing the public file layout. The registry participates in the source hash. / 生成的 HTML 保持现有链接和矩阵数量，新增来源与成熟度展示，不改变公共文件布局；注册表纳入源哈希。

### 4. Provenance And Maturity / 来源与成熟度

Pin the upstream framework to arXiv:2605.13850 v2 and state: 28 upstream named patterns, 14 upstream blank cells, two locally promoted patterns, and 12 remaining extension candidates. / 将上游框架固定为 arXiv:2605.13850 v2，并明确：上游 28 个命名模式、14 个空白单元、本地晋升 2 个模式、剩余 12 个扩展候选。

Use these maturity values: / 使用以下成熟度：

- `seed`: named or hypothesized, not behaviorally validated. / 已命名或提出假设，尚未行为验证。
- `draft`: executable contract exists, validation evidence is incomplete. / 已有可执行契约，但验证证据不完整。
- `validated`: exercised on at least two independent cases with evidence and a failure-path check. / 至少在两个独立案例中使用，有证据并检查过失败路径。
- `operational`: validated and monitored in recurring use with owned thresholds. / 已验证，并在持续使用中由明确负责人监控阈值。

`Failure Journal` remains the upstream English name; `Failure Diary` remains a local alias. `Progressive Discovery` and `Layered Retention` are marked as local extensions, not upstream cells. / `Failure Journal` 保留为上游英文名，`Failure Diary` 保留为本地别名；`Progressive Discovery` 和 `Layered Retention` 标记为本地扩展，而不是上游原生单元。

### 5. Trace Boundary / Trace 边界

Create `references/trace-schema.md` as the bilingual runtime Trace contract. / 创建 `references/trace-schema.md` 作为双语运行 Trace 契约。

Default runtime location: / 默认运行位置：

```text
.harness-analysis/<analysis_id>/trace.yaml
```

Runtime traces include analysis ID, project and tenant scope, sensitivity, source revision, evidence references, event time, validity state, owner, retention, and expiry. / 运行 Trace 包含分析 ID、项目与租户范围、敏感级别、来源版本、证据引用、事件时间、有效状态、负责人、保留策略和到期时间。

Bundled `references/patterns/*/trace.md` files become historical curated snapshots. Normal Skill use proposes a project-local trace record and does not modify bundled history. Updating curated history requires an explicit user request and evidence review. / Skill 内置 `references/patterns/*/trace.md` 变为历史精选快照。普通使用只生成项目本地 Trace 建议，不修改内置历史；更新精选历史必须有用户明确要求并经过证据复核。

Existing trace content remains in place during this phase. / 本阶段既有 Trace 内容原地保留。

### 6. EIR And Evaluation Contracts / EIR 与评价契约

Extend `eir-schema.md` with bilingual schemas for control flow, state flow, tool flow, permission flow, pattern, Skill recommendation, evaluation reference, and governance item. / 扩展 `eir-schema.md`，加入控制流、状态流、工具流、权限流、模式、Skill 建议、评价引用和治理项的双语 Schema。

Define all ID prefixes and shared lifecycle states. Every reference must either resolve inside the analysis or be marked external. / 定义全部 ID 前缀和共享生命周期状态；每个引用必须在分析内解析，或明确标记为外部引用。

Align `evaluation-governance.md` so the output schema contains all seven dimensions: coverage, mapping accuracy, evidence, reuse, Skill readiness, governance, and evaluability. Each metric records formula or rubric, direction, evidence source, observation window, score, confidence, and notes. / 对齐 `evaluation-governance.md`，使输出 Schema 包含覆盖度、映射准确度、证据性、复用性、Skill 就绪度、治理完整度和可评估性七个维度。每个指标记录公式或评分规则、方向、证据来源、观察窗口、分数、置信度和说明。

### 7. Trigger And Output Profiles / 触发与输出档位

Tighten `SKILL.md` metadata around explicit Harness architecture compilation, cognition-topology mapping, EIR generation, and pattern governance. Add non-use cases for ordinary code review, isolated bug diagnosis, general product workflow critique, and requests that do not need the matrix. / 收紧 `SKILL.md` 触发范围，聚焦 Harness 架构编译、认知-拓扑映射、EIR 生成和模式治理；增加普通代码评审、单点缺陷诊断、通用产品流程评审以及不需要矩阵的请求等不适用场景。

Add three output profiles: / 增加三个输出档位：

- `quick`: coordinate, evidence, problem, adjustment, verification. / 坐标、证据、问题、调整和验证。
- `standard`: EIR slice, selection, risks, observability, and trace proposal. / EIR 切片、选型、风险、可观测性和 Trace 建议。
- `full`: complete compiler output, scoring, governance, and extension analysis. / 完整编译产出、评分、治理和扩展分析。

Incomplete evidence produces a preliminary result with explicit gaps; only final pattern promotion is blocked. / 证据不完整时输出带明确缺口的初步结果；只有最终模式晋升被阻断。

### 8. Contract Repair And Navigation / 契约修复与导航

Normalize the required Pattern Template fields in `memory-loop.md` and `perception-parallel.md` without removing their richer content. / 在不删除丰富内容的前提下，规范 `memory-loop.md` 与 `perception-parallel.md` 的必需 Pattern Template 字段。

Correct `Hanerss` to `Harness` in affected Skill content and tests. / 将相关 Skill 内容和测试中的 `Hanerss` 更正为 `Harness`。

Add compact bilingual navigation sections to the five reference files over 500 lines. Other files over 100 lines remain validator warnings for a later content-splitting phase. / 为 5 个超过 500 行的参考文件增加紧凑双语导航；其他超过 100 行的文件在本阶段保留为校验警告，后续再拆分内容。

## Data Flow / 数据流

```text
registry.json
  -> validate_harness_skill.py
      -> structural and semantic contract verdicts
  -> generate_skill_visualization.py
      -> harness-engineering-patterns.html

Markdown pattern corpus
  -> validator consistency checks against registry
  -> detailed runtime guidance

User workflow or Harness source
  -> EIR
  -> matrix selection
  -> output profile
  -> project-local .harness-analysis/<analysis_id>/trace.yaml
```

## Error Handling / 错误处理

- Missing or invalid registry: fail validation and visualization generation with the exact path and field. / 注册表缺失或无效时，校验与可视化生成失败，并报告精确路径和字段。
- Duplicate or reused stable ID: fail validation; never auto-renumber. / 稳定 ID 重复或复用时校验失败，绝不自动重编号。
- Registry-to-Markdown drift: fail required structural checks and print the expected and observed values. / 注册表与 Markdown 漂移时，必需结构检查失败，并输出期望值和实际值。
- Missing runtime evidence: emit preliminary output and verification tasks; do not invent confidence or promote a pattern. / 缺少运行证据时输出初步结果与验证任务，不虚构置信度、不晋升模式。
- Trace destination unavailable: return a trace payload in the response and report the intended path; do not fall back to bundled trace files. / Trace 目标不可写时，在响应中返回 Trace 载荷并报告预期路径，不回退写入 Skill 内置 Trace。

## Testing Strategy / 测试策略

Use the existing standard-library `unittest` setup. Add focused contract tests rather than expanding the visualization test into a general validator test suite. / 继续使用现有标准库 `unittest`；新增聚焦的契约测试，不把可视化测试扩张成通用校验器测试集。

Test groups: / 测试组：

1. Registry schema, counts, stable IDs, provenance, maturity, and exact 42-cell coverage. / 注册表结构、数量、稳定 ID、来源、成熟度和 42 单元完整覆盖。
2. Registry-to-Markdown consistency and paired paths. / 注册表与 Markdown 一致性及文件配对。
3. Validator failure cases using temporary copied fixtures: duplicate ID, missing file, wrong status, missing provenance, missing required field, bundled trace write instruction. / 使用临时复制夹具验证失败场景：重复 ID、文件缺失、状态错误、来源缺失、必填字段缺失、内置 Trace 写入指令。
4. Visualization compatibility: 7, 6, 42, 30, 12; stable links; provenance and maturity rendering. / 可视化兼容：7、6、42、30、12；稳定链接；来源和成熟度渲染。
5. EIR and seven-dimension evaluation contract checks. / EIR 和七维评价契约检查。
6. Trigger, non-use, output-profile, preliminary-result, and project-local Trace guidance checks. / 触发、不适用场景、输出档位、初步结果和项目本地 Trace 说明检查。
7. Existing executable-pattern tests remain green. / 既有可执行模式测试继续通过。

Each behavior change starts with a failing test, then minimal implementation, then refactoring. / 每项行为变化先写失败测试，再完成最小实现，最后重构。

## Success Criteria / 成功标准

- Standard Skill validation passes in UTF-8 mode. / 标准 Skill 校验在 UTF-8 模式下通过。
- Repository unit tests pass with zero failures. / 仓库单元测试零失败。
- The new validator exits 0 on the real Skill and non-zero on every negative fixture. / 新校验器对真实 Skill 返回 0，对每个负向夹具返回非 0。
- The visualization regenerates successfully and preserves matrix counts and links. / 可视化可成功再生成，并保持矩阵数量和链接。
- Registry IDs are unique, existing IDs are preserved, and every named cell has provenance plus maturity. / 注册表 ID 唯一、既有 ID 保留、每个命名单元都有来源与成熟度。
- No normal-use instruction writes to bundled trace history. / 普通使用说明不再写入 Skill 内置 Trace 历史。
- EIR covers every declared collection and evaluation output contains all seven dimensions. / EIR 覆盖全部已声明集合，评价输出包含全部七个维度。
- Required template fields are present in all 42 design files. / 42 个设计文件都具备必需模板字段。
- The five references over 500 lines have navigation sections. / 5 个超过 500 行的参考文件具备导航章节。
- The existing `memory/trace.md` modification and untracked cache artifact remain untouched. / 现有 `memory/trace.md` 改动和未跟踪缓存产物保持不变。

## Rollout / 推进顺序

1. Add failing registry and validator tests. / 增加失败的注册表与校验器测试。
2. Add the registry and minimal validator. / 增加注册表和最小校验器。
3. Move visualization structure loading to the registry. / 将可视化结构读取迁移到注册表。
4. Repair provenance, Trace, EIR, evaluation, trigger, output, and template contracts. / 修复来源、Trace、EIR、评价、触发、输出和模板契约。
5. Add navigation to the five largest references. / 为五个最大参考文件增加导航。
6. Regenerate HTML and run complete verification. / 重新生成 HTML 并运行完整验证。

## Compatibility And Migration / 兼容与迁移

All existing public Markdown paths remain stable. Existing trace records remain readable. The HTML artifact remains at the repository root. Consumers that only read Markdown continue to work; registry-aware consumers gain deterministic structure and validation. / 所有现有公共 Markdown 路径保持稳定；既有 Trace 记录继续可读；HTML 产物仍位于仓库根目录。只读取 Markdown 的消费者继续工作，理解注册表的消费者获得确定性结构和校验能力。

No automatic migration writes runtime trace data. Future extraction of historical traces into a separate evidence store requires a dedicated user-approved task. / 本阶段不会自动迁移或写入运行 Trace；未来若要把历史 Trace 抽取到独立证据库，必须另行获得用户批准。
