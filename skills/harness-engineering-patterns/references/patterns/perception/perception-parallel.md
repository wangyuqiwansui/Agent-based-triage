# Multi-Modal Fusion / 多模态融合

Cell / 交织点: perception-parallel / 感知 x 并行  
Capability / 能力: Perception / 感知  
Mode / 模式: Parallel / 并行  
Pattern ID / 模式标识: PATTERN_0021
Matrix Coordinate / 矩阵坐标: COG_PERCEPTION__TOP_PARALLEL  
Status / 状态: Draft, executable pattern / 草稿，可执行模式  
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this matrix intersection. / 将本文档作为该交织点的设计模式来源。

Observability Metrics File / 可观测性指标文件: [perception-parallel-observability.md](perception-parallel-observability.md)

## Design Pattern / 设计模式

Multi-Modal Fusion is a data-shape design workflow. It decides what the Agent should see, in which form, at which cost, and with which source trail before downstream reasoning starts. / 多模态融合是一种数据形态设计流程。它在下游推理开始前决定 Agent 应该看见什么、以什么形态看见、花费多少成本，以及如何保留来源链路。

Do not treat this pattern as "send every file to a multimodal model." Treat it as a controlled intake, routing, alignment, and evidence-packaging process. / 不要把本模式理解成“把所有文件都发给多模态模型”。应将其视为受控的输入接收、路由、对齐和证据打包流程。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Perception / 感知 x Parallel / 并行.
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Perception / 感知 x Parallel / 并行 to Multi-Modal Fusion / 多模态融合.
- 问题 / Problem: Heterogeneous inputs such as PDF, image, table, log, SQL, audio, and video lose value when everything is stuffed into context or blindly converted to text. / PDF、图片、表格、日志、SQL、音频、视频等异构材料如果全部塞入上下文或盲目转文本，会丢失结构、来源和证据价值。
- 架构方案 / Architectural Solution: Run modality-specific branches in parallel, normalize outputs into evidence blocks, align metadata, and merge them into a fused context package. / 并行运行按模态分发的处理分支，将结果标准化为证据块，对齐元数据，并合并为融合上下文包。
- 工程权衡 / Engineering Trade-offs: Parallel intake improves coverage but can increase merge conflicts, duplicate work, latency, token cost, and source-tracking burden. / 并行接入提升覆盖率，但会增加合并冲突、重复处理、时延、token 成本和来源追踪负担。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when multiple signal types should be gathered, filtered, structured, referenced, and fused before reasoning. / 当多类信号需要在推理前被采集、过滤、结构化、引用并融合时使用。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选，已补充执行流程 / Named candidate with executable workflow.
- 模式清单 / Patterns: Multi-Modal Fusion / 多模态融合.
- 诊断用途 / Diagnostic Use: Use when multiple signal types should be gathered and fused. / 当多类信号需要采集并融合时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 输入预处理、上下文感知、文档分析、日志诊断、事实核查、报告生成 / Intake preprocessing, context sensing, document analysis, log diagnosis, fact checking, report generation.
- 当前症状 / Current Symptoms: Heterogeneous sources are blindly converted to text or loaded wholesale, losing structure, source identity, confidence, or budget control. / 异构来源被盲目转文本或整体加载，导致结构、来源身份、置信度或预算控制丢失。
- 适配信号 / Fit Signals: Multiple independent signal sources can be observed in parallel and merged. / 多个独立信号源可以并行观察后汇总。
- 调整方向 / Adjustment Direction: Route each modality through a suitable extractor, normalize results into evidence blocks, align metadata, and fuse only task-relevant evidence. / 将每种模态路由到合适的抽取器，把结果标准化为证据块，对齐元数据，并只融合与任务相关的证据。
- 修改方式 / How To Modify: Register sources, classify modality and role, process independent branches, preserve page or event references, align scope and time, merge with conflict rules, and verify precise claims against structured evidence. / 登记来源、分类模态与角色、处理独立分支、保留页码或事件引用、对齐范围与时间、按冲突规则合并，并用结构化证据核验精确判断。
- 输入 / Inputs: Task contract, source registry, modality metadata, extraction capabilities, context budget, permission scope, and evidence requirements. / 任务契约、来源注册表、模态元数据、抽取能力、上下文预算、权限范围和证据要求。
- 输出 / Outputs: Fused context package, evidence blocks, source map, conflicts, degraded branches, confidence labels, and project-local Trace proposal. / 融合上下文包、证据块、来源图、冲突、降级分支、置信标签和项目本地 Trace 建议。
- 风险与治理 / Risks & Governance: Require source references for precise numbers, avoid whole-PDF or raw-log stuffing, preserve original evidence when extraction is uncertain, and mark low-confidence or degraded branches for review. / 精确数字必须有来源引用，避免整份 PDF 或原始长日志塞入上下文；抽取不确定时保留原始证据，并将低置信或降级分支标记为待复核。

Core law / 核心法则:

- Text carries logic. / 文本承载逻辑。
- Tables carry structure and numbers. / 表格承载结构和数字。
- Images and charts carry spatial relations and visual evidence. / 图片和图表承载空间关系与视觉证据。
- Logs carry process and time. / 日志承载过程与时间。
- SQL results carry factual slices. / SQL 结果承载事实切片。
- Audio should be transcribed first unless tone or speaker order is material. / 音频通常先转写，除非语气或发言顺序本身重要。
- PDF should be split into outline, key pages, tables, key figures, and page-linked text. / PDF 应拆成目录、关键页、表格、关键图和带页码的文本。
- Precise numbers require structured source references. / 精确数字必须有结构化来源引用。
- Every fusion decision must leave a trace. / 所有融合决策必须留下记录。

## When To Use / 适用场景

Use this pattern when the workflow receives heterogeneous input and the main Agent must reason from combined evidence. / 当工作流接收异构输入，且主控 Agent 需要基于合并证据推理时使用本模式。

Strong fit / 强适配:

| Scenario / 场景 | Typical Inputs / 典型输入 | Goal / 目标 |
| --- | --- | --- |
| Financial research / 金融研报 | PDF, charts, tables, footnotes / PDF、图表、表格、脚注 | Summaries, number checks, sales points / 摘要、数字核查、销售要点 |
| Ops diagnosis / 运维诊断 | Logs, traces, monitoring screenshots, SQL / 日志、调用链、监控截图、SQL | Fault localization and cause analysis / 故障定位与归因 |
| Contract review / 合同审阅 | PDF, scans, clause tables, attachments / PDF、扫描件、条款表、附件 | Clause extraction and risk review / 条款抽取与风险审查 |
| Customer support / 客服工单 | User text, screenshots, audio, status snapshots / 用户描述、截图、录音、状态快照 | Problem reconstruction and handling path / 问题还原与处理路径 |
| Code review / 代码评审 | Diff, architecture diagram, API docs, test logs / 代码差异、架构图、接口文档、测试日志 | Risk review and fix suggestions / 风险审查与修改建议 |
| Knowledge analysis / 知识库分析 | Docs, tables, flowcharts, permission data / 文档、表格、流程图、权限数据 | Retrieval, QA, summaries, process explanation / 检索、问答、摘要、流程解释 |

Weak fit / 弱适配:

- Plain short text Q&A. / 短纯文本问答。
- Small structured JSON that already fits context. / 已结构化且规模较小的 JSON。
- Simple translation or code completion without attachments. / 无附件的简单翻译或代码补全。

If screenshots, PDFs, logs, tables, audio, video, or SQL results appear later, re-enter this pattern. / 如果后续出现截图、PDF、日志、表格、音频、视频或 SQL 结果，应重新进入本模式。

## Input Contract / 输入契约

The workflow receives a list of traceable input items, not one loose prompt. / 工作流接收一组可追踪输入项，而不是一个松散提示。

```yaml
input_contract:
  request_id: string
  scenario_id: string
  task_goal: string
  items:
    - item_id: string
      source_id: string
      source_type: text | image | table | log | pdf | audio | video | sql_result | screenshot | web_page | mixed
      payload_ref: string
      business_hint: string
      source_location:
        page: optional[int]
        section: optional[string]
        chart_id: optional[string]
        table_id: optional[string]
        timestamp: optional[string]
        file_path: optional[string]
        url: optional[string]
      expected_use:
        - summarize
        - fact_check
        - diagnose
        - compare
        - extract
        - calculate
        - generate
      constraints:
        keep_as_original: optional[bool]
        require_reference: optional[bool]
        privacy_level: optional[string]
        max_tokens: optional[int]
        max_processing_ms: optional[int]
```

## Output Contract / 输出契约

The output is a fused context package for downstream work, not the final user answer. / 输出是供下游任务消费的融合上下文包，不是最终用户答案。

```yaml
output_contract:
  fused_context:
    content_blocks:
      - block_id: string
        block_type: text | image | markdown_table | json | csv | mermaid | transcript | summary | pointer
        content_ref: string
        source_refs:
          - source_id: string
            item_id: string
            page: optional[int]
            chart_id: optional[string]
            table_id: optional[string]
            timestamp: optional[string]
        confidence: high | medium | low
        token_estimate: int
        usage_hint:
          - summary
          - evidence
          - calculation
          - diagnosis
          - background
  evidence_index:
    numbers:
      - claim_id: string
        number: string
        source_ref: string
    charts:
      - chart_id: string
        source_ref: string
    tables:
      - table_id: string
        source_ref: string
  fusion_trace:
    - event_id: string
      item_id: string
      source_type: string
      route: string
      method: string
      tokens_in_estimate: int
      tokens_out_estimate: int
      processing_ms: int
      status: success | degraded | failed | skipped
      reason: string
  quality_flags:
    - flag_id: string
      severity: info | warning | critical
      message: string
      related_item_id: optional[string]
      suggested_action: string
  downstream_requirements:
    reference_required: bool
    calculation_should_use_structured_data: bool
    human_review_required: bool
```

## Execution Flow / 执行流程

| Stage / 阶段 | Purpose / 目的 | Required Output / 必要输出 |
| --- | --- | --- |
| 0. Bind task / 任务绑定 | Confirm the pattern is needed and assign workflow coordinates. / 确认需要本模式并绑定工作流坐标。 | `workflow_binding` |
| 1. Register sources / 来源登记 | Convert loose attachments into traceable input assets. / 将零散附件转为可追踪输入资产。 | `input_inventory` |
| 2. Annotate modality and role / 模态与业务角色标注 | Identify both file type and business use. / 同时识别文件类型和业务用途。 | `modality_annotation` |
| 3. Decide data shape / 数据形态判断 | Choose original, text, table, summary, pointer, or discard. / 选择原形、文本、表格、摘要、指针或丢弃。 | `shape_decision` |
| 4. Process by modality / 按模态处理 | Run independent branches with modality-specific rules. / 按模态规则并行处理。 | modality blocks / 模态块 |
| 5. Align metadata / 元数据对齐 | Link pages, figures, tables, timestamps, claims, and source refs. / 对齐页码、图表、时间戳、结论和来源。 | `alignment_metadata` |
| 6. Build fused package / 生成融合包 | Merge blocks, evidence index, flags, and trace. / 合并内容块、证据索引、风险标记和记录。 | `fused_context_package` |
| 7. Consume downstream / 下游消费 | Let summary, diagnosis, review, or calculation tasks use the package. / 让摘要、诊断、审阅或计算任务消费融合包。 | task-specific result / 任务结果 |
| 8. Verify evidence / 证据校验 | Check source coverage, number traceability, and conflicts. / 检查来源覆盖、数字可追溯和证据冲突。 | `evidence_checked_claims` |
| 9. Cache and persist state / 缓存与状态沉淀 | Reuse fingerprints, extracts, summaries, and verified claims. / 复用指纹、抽取结果、摘要和已验证结论。 | `state_artifacts` |
| 10. Degrade safely / 异常降级 | Skip or downgrade failing branches without blocking the whole workflow. / 对失败分支跳过或降级，避免阻断整体流程。 | `degradation_result` |

## Routing Rules / 路由规则

| Input / 输入 | Default Route / 默认路由 | Preserve Original When / 何时保留原形 | Structure When / 何时结构化 | Main Risk / 主要风险 |
| --- | --- | --- | --- | --- |
| Text / 文本 | Clean, segment, summarize / 清洗、切分、摘要 | Source wording matters. / 原文措辞重要。 | Claims, clauses, or arguments must be indexed. / 需要索引观点、条款或论证。 | Losing source location / 丢失来源位置 |
| Image or screenshot / 图片或截图 | Keep key image plus description / 保留关键图并生成说明 | Spatial layout or visual anomaly matters. / 空间布局或视觉异常重要。 | Nodes, labels, or UI states can be extracted. / 节点、标签或界面状态可抽取。 | Visual relation loss / 视觉关系丢失 |
| Table / 表格 | Convert to Markdown, CSV, or JSON / 转 Markdown、CSV 或 JSON | Multi-level headers or merged cells matter. / 多层表头或合并单元格重要。 | Calculations or comparisons are needed. / 需要计算或对比。 | Column shift, number OCR errors / 列错位、数字识别错 |
| Chart / 图表 | Keep image plus extracted trend/data / 保留图像并抽取趋势或数据 | Axes, color, and layout carry meaning. / 坐标、颜色、布局有意义。 | YoY, ratio, or exact values are needed. / 需要同比、占比或精确值。 | Visual readout treated as exact / 把视觉读数当精确值 |
| Log / 日志 | Filter by time, service, request id, error code, then summarize / 按时间、服务、请求标识、错误码过滤后摘要 | Small critical windows need raw evidence. / 小型关键窗口需要原始证据。 | Timeline, error clusters, or trace paths are needed. / 需要时间线、错误聚类或链路。 | Over-filtering or under-filtering / 过滤过狠或过松 |
| PDF / PDF | Split outline, key pages, tables, figures, text / 拆目录、关键页、表格、图和文本 | Complex layout or signatures matter. / 复杂版式或签章重要。 | Clauses, numbers, tables, or citations are needed. / 需要条款、数字、表格或引用。 | Whole-document context bloat / 整份塞入导致膨胀 |
| Audio / 音频 | Transcribe with timestamps / 带时间戳转写 | Tone, pause, speaker order matters. / 语气、停顿、发言顺序重要。 | Content and action items are needed. / 需要内容和行动项。 | Transcription uncertainty / 转写低置信 |
| Video / 视频 | Extract audio, transcript, key frames, timeline / 抽音频、转写、关键帧和时间线 | Motion or UI sequence matters. / 动作或界面变化顺序重要。 | Events can be timestamped. / 事件可按时间戳结构化。 | Too many frames, high cost / 抽帧过多、成本过高 |
| SQL result / SQL 结果 | Sample, aggregate, sort, or truncate; preserve schema / 采样、聚合、排序或截断，并保留 schema | Visualization or raw rows are evidence. / 可视化或原始行是证据。 | Any calculation or audit is needed. / 需要计算或审计。 | Large result inserted directly / 大结果集直接进入上下文 |

## Stage Details / 阶段细则

### 0. Bind Task / 任务绑定

Generate `workflow_id`, confirm `PATTERN_0021`, set `COG_PERCEPTION__TOP_PARALLEL`, and decide whether the observability probe is enabled. / 生成 `workflow_id`，确认 `PATTERN_0021`，设置 `COG_PERCEPTION__TOP_PARALLEL`，并判断是否启用可观测性探针。

```yaml
workflow_binding:
  workflow_id: string
  enabled_pattern: PATTERN_0021
  cognition_ref: COG_PERCEPTION
  topology_ref: TOP_PARALLEL
  scenario_type: research | ops | contract | customer_service | code_review | knowledge_base | other
  probe_enabled: true | false
```

### 1. Register Sources / 来源登记

Assign `item_id` and `source_id`, record original location, mark business hints, detect duplicates, and flag sensitive inputs. / 分配 `item_id` 与 `source_id`，记录原始位置，标注业务提示，识别重复材料，并标记敏感输入。

### 2. Annotate Modality And Role / 模态与角色标注

Classify every item by both source type and business role: primary evidence, context, diagnostic signal, calculation source, decoration, or duplicate. / 按来源类型和业务角色同时分类：主证据、背景、诊断信号、计算来源、装饰或重复。

### 3. Decide Data Shape / 数据形态判断

Choose a route from `keep_original`, `markdown`, `csv`, `json`, `mermaid`, `transcript`, `filtered_summary`, `key_pages`, `pointer_only`, or `discard`. / 从 `keep_original`、`markdown`、`csv`、`json`、`mermaid`、`transcript`、`filtered_summary`、`key_pages`、`pointer_only` 或 `discard` 中选择路由。

Use this decision rule / 使用以下判断规则:

- If value is in layout, arrows, position, or visual marks, keep visual evidence. / 如果价值在布局、箭头、位置或视觉标注中，保留视觉证据。
- If value is in rows, columns, fields, numbers, or formulas, structure it. / 如果价值在行列、字段、数字或公式中，结构化处理。
- If value is in body text, clauses, explanations, or opinions, build a text skeleton with source refs. / 如果价值在正文、条款、解释或观点中，生成带来源的文本骨架。
- If value is in time, sequence, or error context, filter and summarize with replay pointers. / 如果价值在时间、顺序或错误上下文中，过滤摘要并保留回放指针。
- If value is low or decorative, discard it or keep only a pointer. / 如果价值低或只是装饰，丢弃或只保留指针。

### 4. Process By Modality / 按模态处理

Run branches independently when possible, then return normalized content blocks. / 尽量并行运行各分支，再返回标准化内容块。

- Text branch: clean, segment by heading or semantic block, preserve key sentences and source positions. / 文本分支：清洗，按标题或语义块切分，保留关键句和来源位置。
- Image branch: detect decorative images, keep key visuals, extract chart data when needed, cache duplicate images. / 图片分支：识别装饰图，保留关键视觉证据，必要时抽取图表数据，缓存重复图片。
- Table branch: detect headers, merged cells, cross-page tables, and extract key numbers with source refs. / 表格分支：识别表头、合并单元格、跨页表，并为关键数字保留来源。
- Log branch: filter by time window, service, request id, and error code; preserve abnormal windows and filter rules. / 日志分支：按时间窗、服务、请求标识和错误码过滤，保留异常窗口和过滤规则。
- PDF branch: extract outline, sections, key pages, tables, figures, and page-figure-table links. / PDF 分支：抽取目录、章节、关键页、表格、图，并建立页码、图号、表号关联。
- Audio branch: lazy-load audio tooling, transcribe, mark speakers, timestamps, and low-confidence spans. / 音频分支：延迟加载音频工具，转写并标记说话人、时间戳和低置信片段。
- Video branch: extract transcript and key frames, then align them on a timeline. / 视频分支：抽取转写和关键帧，并按时间线对齐。
- SQL branch: preserve query, schema, timestamp, result version, and sampled or aggregated rows. / SQL 分支：保留查询语句、schema、时间、结果版本，以及采样或聚合后的行。

### 5. Align Metadata / 元数据对齐

Build relationships across modalities so the Agent sees connected evidence, not isolated blocks. / 建立跨模态关系，让 Agent 看到关联证据，而不是孤立材料。

```yaml
alignment_metadata:
  source_id: string
  item_id: string
  page: optional[int]
  section: optional[string]
  chart_id: optional[string]
  table_id: optional[string]
  timestamp: optional[string]
  related_blocks:
    - block_id
  evidence_role: claim | number | trend | cause | symptom | constraint | background
  confidence: high | medium | low
```

Alignment rules / 对齐规则:

- Link body text, figures, and tables on the same page. / 对齐同页正文、图和表。
- Link chart titles, chart numbers, footnotes, images, and extracted data. / 对齐图标题、图号、脚注、图像和抽取数据。
- Link table titles, table numbers, fields, and exact numbers. / 对齐表标题、表号、字段和精确数字。
- Link logs, traces, SQL results, and monitoring screenshots by time and request id. / 按时间和请求标识对齐日志、trace、SQL 和监控截图。
- Link audio transcripts and video key frames by timestamp. / 按时间戳对齐音频转写和视频关键帧。

### 6. Build Fused Package / 生成融合包

Merge content blocks, evidence index, trace events, quality flags, and downstream requirements. / 合并内容块、证据索引、融合记录、质量标记和下游要求。

### 7. Consume Downstream / 下游消费

Use the same fused package for summaries, fact checks, calculations, diagnosis, risk review, and recommendations. / 使用同一个融合包支持摘要、事实核查、计算、诊断、风险审查和建议生成。

Downstream rules / 下游规则:

- Summary tasks may use text skeletons, key visual descriptions, and structured tables. / 摘要任务可使用文本骨架、关键图说明和结构化表格。
- Fact checks must use evidence blocks with source references. / 事实核查必须使用带来源引用的证据块。
- Calculations must use structured data, not visual estimates alone. / 计算必须使用结构化数据，不能只依赖视觉估读。
- Diagnosis must use timelines, logs, traces, SQL results, and monitoring evidence. / 诊断必须使用时间线、日志、trace、SQL 结果和监控证据。
- Generation tasks must separate factual evidence from background material. / 生成任务必须区分事实证据和背景材料。

### 8. Verify Evidence / 证据校验

Every numeric conclusion must trace to a page, figure, table, SQL result, or log span. If evidence conflicts, output the conflict instead of forcing a merge. / 每个数字结论必须能追溯到页码、图号、表号、SQL 结果或日志片段。若证据冲突，应输出冲突说明，而不是强行合并。

### 9. Cache And Persist State / 缓存与状态沉淀

Cache fingerprints, PDF outlines, table extracts, chart extracts, log windows, SQL versions, verified claims, bad routes, and route overrides. / 缓存内容指纹、PDF 目录、表格抽取、图表抽取、日志窗口、SQL 版本、已验证结论、失败路由和路由覆盖项。

```yaml
state_artifacts:
  document_fingerprint: string
  reusable_toc: string
  reusable_table_extracts: []
  reusable_chart_extracts: []
  verified_claims: []
  known_bad_routes: []
  recommended_route_overrides: []
```

### 10. Degrade Safely / 异常降级

Do not let one failing modality block the whole workflow. Return degraded status, keep raw pointers, and require human review when confidence is low. / 不要让单个模态失败阻断整个工作流。返回降级状态，保留原始指针，并在低置信时要求人工复核。

| Failure / 异常 | Symptom / 表现 | Fallback / 降级策略 |
| --- | --- | --- |
| PDF extraction failure / PDF 抽取失败 | Text unreadable or page order broken / 正文不可读或页码错乱 | Keep key page screenshots and mark human review. / 保留关键页截图并标记人工复核。 |
| Image cost too high / 图片成本过高 | Too many images enter context / 图片过多进入上下文 | Crop, thumbnail, or keep only key visuals. / 裁剪、缩略或只保留关键图。 |
| Table structure loss / 表格结构丢失 | Headers or columns shift / 表头或列错位 | Keep original image plus partial schema. / 保留原图和部分 schema。 |
| Log under-filtering / 日志过滤过松 | Irrelevant logs flood context / 无关日志淹没上下文 | Tighten by error code, service, and time window. / 按错误码、服务和时间窗收紧。 |
| Log over-filtering / 日志过滤过狠 | Root-cause context missing / 根因上下文丢失 | Expand window and replay from raw logs. / 扩大窗口并从原始日志回放。 |
| Audio tooling failure / 音频工具失败 | Dependency missing or transcription fails / 依赖缺失或转写失败 | Skip audio branch, preserve pointer, continue. / 跳过音频分支，保留指针并继续。 |
| Unsupported conclusion / 无证据结论 | Number or claim lacks source / 数字或判断无来源 | Mark low confidence and request evidence. / 标记低置信并要求补证据。 |
| Cross-modal conflict / 跨模态冲突 | Text, table, and chart disagree / 图、表、文不一致 | Output conflict list, do not average. / 输出冲突清单，不自动取平均。 |

```yaml
degradation_result:
  status: degraded
  failed_stage: string
  affected_items:
    - item_id
  fallback_used: string
  human_review_required: true | false
  suggested_probe: string
```

## Minimum Checklist / 最小执行清单

- Is there any non-text input? / 是否存在非纯文本输入？
- Does every input have `source_id` and `item_id`? / 每个输入是否都有 `source_id` 和 `item_id`？
- Is every item annotated with business meaning? / 每个材料是否已标注业务含义？
- Has each item received a data-shape decision? / 每个材料是否已有数据形态判断？
- Is the workflow avoiding whole-PDF context stuffing? / 是否避免整份 PDF 暴力进入上下文？
- Is the workflow avoiding raw long-log stuffing? / 是否避免长日志直接进入主上下文？
- Are normal tables structured? / 普通表格是否已结构化？
- Are spatially important images preserved? / 承载空间关系的关键图是否已保留？
- Are decorative or duplicate materials discarded or pointer-only? / 装饰或重复材料是否已丢弃或只保留指针？
- Do numeric conclusions have source references? / 数字结论是否有来源引用？
- Does `fusion_trace` record routes, methods, status, cost, and reason? / `fusion_trace` 是否记录路由、方法、状态、成本和原因？
- Are token, latency, recursion, and cost budgets set? / 是否设置 token、时延、递归和成本预算？
- Is there a degradation strategy? / 是否有降级策略？
- Are probe results feeding route and threshold updates? / 探针结果是否回填路由和阈值？
- Are reusable artifacts cached? / 可复用产物是否已缓存？

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。

Trace entry should include task type, input modalities, selected routes, degraded branches, evidence coverage, cache decisions, and outcome. / 追踪记录应包含任务类型、输入模态、已选路由、降级分支、证据覆盖率、缓存决策和结果。
