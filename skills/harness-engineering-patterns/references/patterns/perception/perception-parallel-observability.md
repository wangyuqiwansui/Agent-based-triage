# Multi-Modal Fusion / 多模态融合 Observability Metrics / 可观测性指标

Cell / 交织点: perception-parallel / 感知 x 并行  
Capability / 能力: Perception / 感知  
Mode / 模式: Parallel / 并行  
Pattern ID / 模式标识: PATTERN_0021
Probe ID / 探针标识: PROBE_MMF_0001  
Matrix Coordinate / 矩阵坐标: COG_PERCEPTION__TOP_PARALLEL  
Status / 状态: Draft, executable observability probe / 草稿，可执行可观测性探针  
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the observability metrics source for Multi-Modal Fusion. / 将本文档作为多模态融合的可观测性指标来源。

Design Pattern File / 设计模式文件: [perception-parallel.md](perception-parallel.md)

## Observability Goal / 可观测性目标

Observe, diagnose, and improve whether Multi-Modal Fusion turns heterogeneous inputs into the right evidence shape with traceable sources, controlled cost, stable latency, safe degradation, and reusable state. / 观察、诊断并改进多模态融合是否把异构输入转换为合适的证据形态，并同时保持来源可追踪、成本可控、延迟稳定、降级安全和状态可复用。

The probe should make the fusion workflow replayable and governable. It should not only say that an output is weak; it should identify which modality, route, branch, evidence link, budget, cache, or fallback created the weakness. / 探针应让融合工作流可回放、可治理。它不只指出产出薄弱，还要定位是哪个模态、路由、分支、证据链接、预算、缓存或降级策略造成了问题。

## Run Modes / 运行模式

| Mode / 模式 | Use / 用途 | Input / 输入 | Output / 输出 |
| --- | --- | --- | --- |
| Standalone probe / 独立运行 | Audit an existing multimodal Agent, historical logs, launch test, or route strategy. / 审查已有多模态 Agent、历史日志、上线压测或路由策略。 | workflow samples, traces, outputs, errors, feedback / 工作流样本、记录、输出、错误、反馈 | health report, bottlenecks, risk flags, route recommendations / 健康报告、瓶颈、风险标记、路由建议 |
| Interactive probe / 交互运行 | Run inside the execution flow and feed decisions back while the task is running. / 嵌入执行流程，在任务运行中回填决策。 | live inventory, route decisions, branch metrics, evidence index / 实时输入清单、路由决策、分支指标、证据索引 | route overrides, threshold updates, quality gates, review items / 路由覆盖、阈值更新、质量门禁、复核项 |

```yaml
probe_report:
  workflow_health_score: int
  bottlenecks: []
  risk_flags: []
  metric_report: []
  route_recommendations: []
  execution_flow_patch: []
```

## Probe Flow / 探针流程

| Stage / 阶段 | Purpose / 目的 | Output / 输出 |
| --- | --- | --- |
| 1. Capture / 采集 | Capture workflow binding, inventory, modality annotation, shape decision, trace, blocks, evidence, output, feedback, and errors. / 采集绑定、清单、模态标注、形态决策、融合记录、内容块、证据、输出、反馈和错误。 | `capture_targets` |
| 2. Normalize / 标准化 | Convert different scenario events into comparable probe events. / 将不同场景事件转为可比较的探针事件。 | `normalized_probe_event` |
| 3. Measure / 计量 | Calculate coverage, route, cost, latency, filter, evidence, consistency, cache, and governance metrics. / 计算覆盖、路由、成本、延迟、过滤、证据、一致性、缓存和治理指标。 | `metric_report` |
| 4. Diagnose / 诊断 | Turn metric anomalies into actionable cause statements. / 将指标异常转为可执行原因判断。 | `diagnosis` |
| 5. Backfill / 回填 | Patch execution stages with route, filter, threshold, cache, and quality-gate changes. / 将路由、过滤、阈值、缓存和质量门禁变更回填执行阶段。 | `execution_flow_patch` |
| 6. Persist / 沉淀 | Save verified thresholds, failure modes, cache candidates, and human-review rules. / 沉淀已验证阈值、失败模式、缓存候选和人工复核规则。 | `probe_memory` |

```yaml
normalized_probe_event:
  workflow_id: string
  scenario_id: string
  stage: string
  item_id: string
  source_type: string
  selected_route: string
  method: string
  tokens_in_estimate: int
  tokens_out_estimate: int
  processing_ms: int
  status: success | degraded | failed | skipped
  source_ref_present: true | false
  confidence: high | medium | low
  error_type: optional[string]
```

## Probe Timing / 探针时机

| Timing / 时机 | Probe Focus / 探针关注点 | Feeds Back To / 回填位置 |
| --- | --- | --- |
| Before run / 运行前 | Input inventory, modality distribution, duplicate detection, sensitive material, estimated token/cost/latency, recommended routes. / 输入清单、模态分布、重复判断、敏感材料、预计 token/成本/时延、推荐路由。 | Stages 0-3 / 阶段 0-3 |
| During run / 运行中 | Actual token share, branch latency, extraction failures, PDF key-page looseness, image retention rate, log compression ratio, reference gaps. / 实际 token 占比、分支耗时、抽取失败、PDF 关键页宽松度、图片保留率、日志压缩比、引用缺口。 | Stages 4-6, 10 / 阶段 4-6、10 |
| After run / 运行后 | Evidence coverage, cross-modal consistency, unsupported claims, cache hit rate, degradation causes, route override suggestions. / 证据覆盖、跨模态一致性、无来源结论、缓存命中、降级原因、路由覆盖建议。 | Stages 8-9 / 阶段 8-9 |

## Observability Metrics / 可观测性指标

Use these metrics to observe whether Multi-Modal Fusion / 多模态融合 improves the workflow after selection or application. / 使用以下指标观察 Multi-Modal Fusion / 多模态融合 在选型或应用后是否改善工作流。

- 质量指标 / Quality Metrics: Track source coverage, route correctness, extraction success, evidence consistency, and final claim support. / 跟踪来源覆盖、路由正确性、抽取成功、证据一致性和最终结论支撑度。
- 时延指标 / Latency Metrics: Track time from input registration to fused context readiness, including slow branches, lazy-load failures, and degradation time. / 跟踪从输入登记到融合上下文就绪的耗时，包括慢分支、延迟加载失败和降级耗时。
- 成本指标 / Cost Metrics: Track token share, tool calls, compute spend, repeated work, and cache savings by modality. / 按模态跟踪 token 占比、工具调用、计算成本、重复处理和缓存节省。
- 风险指标 / Risk Metrics: Track unsupported claims, sensitive material handling, degraded primary evidence, budget overruns, and human review triggers. / 跟踪无来源结论、敏感材料处理、主证据降级、预算超限和人工复核触发。
- Trace 指标 / Trace Metrics: Track route decisions, fusion events, probe backfill, outcome comparison, and closed follow-up actions. / 跟踪路由决策、融合事件、探针回填、结果对比和后续动作关闭情况。

## Metric Groups / 指标分组

| Group / 指标组 | Problem / 解决问题 | Main Use / 主要用途 |
| --- | --- | --- |
| Input coverage / 输入覆盖 | Whether all inputs were seen and registered. / 是否看全并登记输入。 | Complete source registration. / 补全输入登记。 |
| Shape routing / 形态路由 | Whether each modality used the right processing path. / 每种模态是否走对处理路径。 | Correct keep, convert, filter, discard decisions. / 修正保留、转换、过滤、丢弃决策。 |
| Token and cost / token 与成本 | Whether context or processing cost is bloated. / 上下文或处理成本是否膨胀。 | Control budget and context size. / 控制预算和上下文大小。 |
| Latency and stability / 延迟与稳定性 | Whether branches are slow, failed, or unstable. / 分支是否变慢、失败或不稳定。 | Locate slow branches and crash points. / 找出慢分支和崩溃点。 |
| Compression and filtering / 压缩与过滤 | Whether large artifacts are filtered too loosely or aggressively. / 大型材料过滤是否过松或过狠。 | Tune logs and large document handling. / 优化日志和大文档处理。 |
| Evidence and references / 证据与引用 | Whether outputs are traceable. / 输出是否可追溯。 | Support fact checks and human review. / 支撑事实核查和人工复核。 |
| Cross-modal consistency / 跨模态一致性 | Whether text, tables, charts, logs, and SQL conflict. / 图、表、文、日志、SQL 是否冲突。 | Reduce misreadings and hallucinations. / 降低误读与幻觉。 |
| Cache and reuse / 缓存与复用 | Whether repeated artifacts are reprocessed. / 是否重复处理相同材料。 | Lower cost and latency. / 降低成本和延迟。 |
| Governance and risk / 治理与风险 | Whether the workflow is compliant and controlled. / 工作流是否合规可控。 | Support launch, audit, and escalation. / 支撑上线、审计和升级处理。 |

## Metric Catalog / 指标目录

| ID | Metric / 指标 | Calculation / 计算方式 | Healthy / 健康范围 | Feed Stage / 回填阶段 | Action / 动作 |
| --- | --- | --- | --- | --- | --- |
| MMF_INPUT_001 | Modality inventory coverage / 模态清单覆盖率 | registered input items / actual input items / 已登记输入项 / 实际输入项 | >= 0.98 | Stage 1 / 阶段 1 | Fill missing inputs; block unregistered materials from main context. / 补齐缺失输入；禁止未登记材料直接进入主上下文。 |
| MMF_INPUT_002 | Source ID coverage / 来源标识覆盖率 | items with both `source_id` and `item_id` / total items / 同时具备 `source_id` 与 `item_id` 的输入项 / 输入项总数 | >= 0.99 | Stages 1, 5, 8 / 阶段 1、5、8 | Build references before fact checks. / 事实核查前补建引用。 |
| MMF_INPUT_003 | Business hint coverage / 业务提示覆盖率 | items with `business_hint` / total items / `business_hint` 非空输入项 / 输入项总数 | >= 0.90 | Stage 2 / 阶段 2 | Generate initial hints; send low-confidence items to review. / 生成初始业务提示；低置信项人工确认。 |
| MMF_INPUT_004 | Duplicate input ratio / 重复输入比例 | duplicate candidates / total items / 疑似重复输入项 / 输入项总数 | < 0.10 | Stage 9 / 阶段 9 | Create fingerprints, cache, and pointer refs. / 建立内容指纹、缓存和指针引用。 |
| MMF_ROUTE_001 | Route decision completeness / 路由决策完整率 | items with `selected_route` / total items / 已生成路由输入项 / 输入项总数 | >= 0.98 | Stage 3 / 阶段 3 | Force explicit route decisions; avoid "all text" or "all image". / 强制路由，不允许默认全部转文本或全部保留为图。 |
| MMF_ROUTE_002 | Original-preservation reason coverage / 强制保留原形说明率 | `keep_original` items with reason / `keep_original` items / 有保留理由项 / 原形保留项 | >= 0.95 | Stages 3-4 / 阶段 3-4 | Re-route unjustified originals. / 重判无理由原形保留项。 |
| MMF_ROUTE_003 | Table structuring success rate / 表格结构化成功率 | structured tables / table inputs / 成功结构化表格 / 表格输入 | >= 0.90 | Stage 4 / 阶段 4 | Keep original plus structured attempt for complex tables. / 复杂表格保留原图并尝试结构化。 |
| MMF_ROUTE_004 | Key chart retention hit rate / 关键图表保留命中率 | retained key charts / expected key charts / 已保留关键图表 / 应保留关键图表 | >= 0.95 | Stage 4 / 阶段 4 | Tune key-chart rules and business keywords. / 调整关键图识别规则和业务关键词。 |
| MMF_ROUTE_005 | Decorative image discard rate / 装饰图丢弃率 | discarded decorative images / decorative images / 已丢弃装饰图 / 识别为装饰图 | >= 0.95 | Stage 4 / 阶段 4 | Add logo, footer, size, position, and repetition filters. / 增加 logo、页脚、尺寸、位置和重复度规则。 |
| MMF_COST_001 | Token share by modality / 按模态 token 占比 | modality tokens / total tokens / 某模态 token / 全部 token | scenario baseline / 场景基线 | Stages 4, 6 / 阶段 4、6 | Re-route or compress bloated modalities. / 对异常膨胀模态重新路由或压缩。 |
| MMF_COST_002 | Image token anomaly rate / 图片 token 异常率 | image tokens / total tokens / 图片 token / 全部 token | <= 0.30 | Stage 4 / 阶段 4 | Structure table screenshots; discard decorative or duplicate images. / 表格截图结构化；丢弃装饰图和重复图。 |
| MMF_COST_003 | Log token anomaly rate / 日志 token 异常率 | log tokens / total tokens / 日志 token / 全部 token | <= 0.15 | Stage 4 / 阶段 4 | Tighten by time, service, error code, request id. / 按时间、服务、错误码、请求标识收紧过滤。 |
| MMF_COST_004 | PDF token anomaly rate / PDF token 异常率 | PDF-related tokens / total tokens / PDF 相关 token / 全部 token | scenario configured / 按场景配置 | Stage 4 / 阶段 4 | Use outline, key pages, section summaries, tables, and figures. / 改用目录、关键页、章节摘要、表格和关键图。 |
| MMF_COST_005 | Single fusion task cost / 单任务融合成本 | model in/out + tools + storage/cache / 模型输入输出 + 工具 + 存储缓存成本 | scenario configured / 按场景配置 | Stage 9 / 阶段 9 | Cache frequent artifacts; use pointers and summaries. / 高频材料启用缓存、指针和摘要。 |
| MMF_LATENCY_001 | Total fusion latency / 融合处理总耗时 | fusion end - fusion start / 融合结束时间 - 开始时间 | < 5s; warning 5-30s; critical > 30s / 小于 5 秒；5-30 秒警告；超过 30 秒严重 | Stages 4, 10 / 阶段 4、10 | Locate slow PDF, image, audio, video, or log branches. / 定位慢分支。 |
| MMF_LATENCY_002 | Branch latency share / 分支处理耗时占比 | branch processing ms / total processing ms / 分支耗时 / 总耗时 | scenario configured / 按场景配置 | Stage 4 / 阶段 4 | Use async, cache, sampling, thumbnails, or degradation. / 启用异步、缓存、采样、缩略图或降级。 |
| MMF_LATENCY_003 | Lazy-load failure rate / 延迟加载失败率 | lazy-load failures / attempts / 延迟加载失败次数 / 尝试次数 | < 0.01 | Stage 10 / 阶段 10 | Move dependencies into lazy loaders and add capability probes. / 将依赖延迟加载并加入能力探测。 |
| MMF_LATENCY_004 | Branch failure rate / 分支失败率 | failed events / total events by modality / 某模态失败事件 / 总事件 | < 0.02 | Stage 10 / 阶段 10 | Configure fallback and review for failed branches. / 为失败分支配置降级和复核。 |
| MMF_FILTER_001 | Log prefilter compression ratio / 日志预过滤压缩比 | filtered size / original size / 过滤后大小 / 原始大小 | 0.01 - 0.05 | Stage 4 / 阶段 4 | Too loose: add filters; too aggressive: expand window. / 过松增加过滤；过狠扩大窗口。 |
| MMF_FILTER_002 | Log signal retention rate / 日志信号保留率 | retained key signals / expected key signals / 已保留关键信号 / 应保留关键信号 | >= 0.90 | Stage 4 / 阶段 4 | Replay raw logs and tune rules. / 回放原始日志并修正规则。 |
| MMF_FILTER_003 | PDF key-page selection rate / PDF 关键页选择率 | selected key pages / total pages / 已选关键页 / 总页数 | document-type baseline / 按文档类型配置 | Stage 4 / 阶段 4 | Tune by TOC, titles, business keywords, figures, and tables. / 结合目录、标题、业务关键词、图表规则调整。 |
| MMF_FILTER_004 | Information density / 信息密度 | task-relevant facts / output tokens / 任务相关信息点 / 输出 token | scenario baseline / 场景基线 | Stage 6 / 阶段 6 | Recompress low-density blocks or keep pointer-only. / 低密度块重新压缩或只保留指针。 |
| MMF_EVIDENCE_001 | Numeric reference coverage / 数字结论引用覆盖率 | numeric claims with source / numeric claims / 带来源数字结论 / 数字结论总数 | >= 0.95 | Stage 8 / 阶段 8 | Mark missing refs low confidence; require evidence or review. / 缺引用项标低置信并要求补证据或复核。 |
| MMF_EVIDENCE_002 | Evidence link validity / 证据链接有效率 | locatable refs / refs / 可定位引用 / 引用总数 | >= 0.98 | Stages 5, 8 / 阶段 5、8 | Repair broken refs before final fact checks. / 最终事实核查前修复失效引用。 |
| MMF_EVIDENCE_003 | Unsupported conclusion rate / 无来源结论率 | unsupported conclusions / all conclusions / 无来源结论 / 全部结论 | < 0.05 | Stage 8 / 阶段 8 | Force basis fields; downgrade unsupported claims to hypotheses. / 强制依据字段；无依据结论降级为假设。 |
| MMF_EVIDENCE_004 | Low-confidence evidence ratio / 低置信证据比例 | low-confidence evidence / total evidence / 低置信证据 / 证据总数 | < 0.10 | Stages 8, 10 / 阶段 8、10 | Run second pass, preserve original, or request review. / 二次识别、保留原件或人工复核。 |
| MMF_CONSISTENCY_001 | Chart-text number consistency / 图文数字一致率 | consistent chart-text numbers / comparable numbers / 图文数字一致项 / 可比对数字项 | >= 0.95 | Stage 8 / 阶段 8 | Output conflict list; do not auto-pick a winner. / 输出冲突清单，不自动选择结论。 |
| MMF_CONSISTENCY_002 | Table-text consistency / 表文一致率 | consistent table-text items / comparable items / 表文一致项 / 可比对项 | >= 0.95 | Stage 8 / 阶段 8 | Use structured tables for calculation; text as explanation. / 结构化表格用于计算，正文用于解释。 |
| MMF_CONSISTENCY_003 | Log-SQL consistency / 日志与 SQL 一致率 | consistent events / alignable events / 一致事件 / 可对齐事件 | >= 0.90 | Stage 8 / 阶段 8 | Add trace id, request id, time window, and SQL conditions. / 补充 trace、请求标识、时间窗和 SQL 条件。 |
| MMF_CONSISTENCY_004 | Audio-text consistency / 音频转写与文本记录一致率 | consistent spans / comparable spans / 一致片段 / 可比对片段 | >= 0.90 | Stage 8 / 阶段 8 | Mark inconsistent spans for review and keep timestamps. / 不一致片段人工复核并保留时间戳。 |
| MMF_CACHE_001 | Cache hit rate / 缓存命中率 | cache hits / cache lookups / 缓存命中 / 缓存查询 | scenario configured / 按场景配置 | Stage 9 / 阶段 9 | Fingerprint repeated PDFs, contracts, reports, charts, and tables. / 对重复材料建立指纹缓存。 |
| MMF_CACHE_002 | Duplicate processing cost share / 重复处理成本占比 | duplicate processing cost / total cost / 重复处理成本 / 总成本 | < 0.10 | Stage 9 / 阶段 9 | Use fingerprints, prompt cache, batching, and pointer refs. / 使用指纹、提示缓存、批处理和指针引用。 |
| MMF_CACHE_003 | Persisted-state effectiveness / 状态沉淀有效率 | reused state items / reusable state items / 被复用状态项 / 可沉淀状态项 | scenario configured / 按场景配置 | Stage 9 / 阶段 9 | Persist frequent outlines, key tables, verified numbers, and bad routes. / 沉淀高频骨架、关键表格、已核查数字和失败路由。 |
| MMF_GOV_001 | Budget overrun rate / 预算超限率 | budget exceeded events / total events / 超限事件 / 总事件 | < 0.02 | Stage 10 / 阶段 10 | Add hard stops; use pointers, summaries, and cache. / 设置硬停止，使用指针、摘要和缓存。 |
| MMF_GOV_002 | Human review trigger rate / 人工复核触发率 | triggered reviews / should-review cases / 已触发复核 / 应复核项 | >= 0.95 | Stages 8, 10 / 阶段 8、10 | Force review for missing evidence, conflict, low confidence, or high risk. / 缺证据、冲突、低置信、高风险强制复核。 |
| MMF_GOV_003 | Sensitive information exposure rate / 敏感信息暴露率 | unmasked sensitive items / sensitive items / 未脱敏敏感项 / 敏感项总数 | 0 | Stages 1, 6, 8 / 阶段 1、6、8 | Mask before main context; keep pointers or summaries. / 进入主上下文前脱敏，只保留指针或摘要。 |
| MMF_GOV_004 | Subtask runaway rate / 子任务失控率 | recursion or timeout events / subtask events / 递归或超时事件 / 子任务事件 | < 0.01 | Stage 10 / 阶段 10 | Set token, time, and recursion budgets; stop at limit. / 设置 token、时间和递归预算，超限停止。 |

## Diagnosis Rules / 诊断规则

- If `image_tokens / total_tokens > 0.50`, flag severe image-token bloat; inspect table screenshots, decorative images, duplicates, and low-value visuals. / 如果 `image_tokens / total_tokens > 0.50`，标记图片 token 严重异常；检查表格截图、装饰图、重复图和低价值图。
- If `log_tokens / total_tokens > 0.40`, flag log prefilter failure; rerun filters by time window, service, error code, and request id. / 如果 `log_tokens / total_tokens > 0.40`，标记日志预过滤失败；按时间窗、服务、错误码和请求标识重跑过滤。
- If `log_prefilter_compression_ratio > 0.10`, filtering is too loose; if `< 0.005`, filtering is too aggressive and may lose root-cause context. / 如果日志预过滤压缩比大于 0.10，说明过滤过松；小于 0.005，说明过滤过狠，可能丢失根因上下文。
- If PDF-related tokens exceed budget, switch to outline, key pages, section summaries, key charts, and tables. / 如果 PDF 相关 token 超预算，改用目录、关键页、章节摘要、关键图和表格。
- If key-page selection is low and output lacks evidence, expand rules with business keywords, figure/table numbers, and section titles. / 如果关键页选择过低且输出缺证据，用业务关键词、图号、表号和章节标题扩展规则。
- If numeric reference coverage is below 0.95, block automated delivery for fact-check tasks and require source repair or human review. / 如果数字引用覆盖率低于 0.95，事实核查任务不进入自动交付，要求补来源或人工复核。
- If chart-text or table-text consistency is below 0.95, output conflicts explicitly; use structured data for calculation and visuals for trend understanding. / 如果图文或表文一致率低于 0.95，显式输出冲突；计算优先用结构化数据，图像用于趋势理解。
- If `fusion_processing_p99_ms > 30000`, flag severe latency risk and locate PDF extraction, OCR, audio transcription, video frame extraction, or log subtasks. / 如果 `fusion_processing_p99_ms > 30000`，标记严重延迟风险，并定位 PDF 抽取、OCR、音频转写、视频抽帧或日志子任务。
- If lazy-load failure rate exceeds 0.05, move audio, vision, PDF, or video dependencies behind capability probes and graceful degradation. / 如果延迟加载失败率超过 0.05，将音频、视觉、PDF 或视频依赖放到能力探测和优雅降级之后。
- If subtasks repeatedly time out or recurse, require explicit token, time, and recursion budgets with hard stops. / 如果子任务频繁超时或递归，要求声明 token、时间和递归预算，并设置硬停止。

## Probe Backfill Map / 探针回填表

| Probe Data / 探针数据 | Backfill Field / 回填字段 | Use / 用途 |
| --- | --- | --- |
| Modality inventory / 模态清单 | `input_inventory`, `modality_annotation` | Complete input registration and type recognition. / 补全输入登记和类型识别。 |
| Route confidence / 路由置信度 | `shape_decision.needs_probe_validation` | Correct keep, convert, filter, discard decisions. / 修正保留、转换、过滤、丢弃决策。 |
| Token share / token 占比 | `fusion_trace.tokens_in_estimate`, `token_estimate` | Detect context bloat. / 识别上下文膨胀。 |
| Processing time / 处理耗时 | `fusion_trace.processing_ms`, `degradation_result.failed_stage` | Locate slow branches and degradation points. / 定位慢分支和降级点。 |
| Log compression ratio / 日志压缩比 | log branch filter settings / 日志分支过滤设置 | Tune time windows and error filters. / 调整时间窗和错误过滤。 |
| Reference coverage / 引用覆盖率 | `evidence_index`, `quality_flags` | Judge fact-check reliability. / 判断事实核查可靠性。 |
| Cross-modal consistency / 跨模态一致性 | `quality_flags`, `evidence_checked_claims` | Surface conflicts between text, tables, charts, SQL, and logs. / 暴露图、文、表、SQL、日志冲突。 |
| Cache hit rate / 缓存命中率 | `state_artifacts` | Decide whether reusable state is needed. / 判断是否需要复用状态。 |
| Budget overrun / 预算超限 | `downstream_requirements`, `degradation_result` | Add hard stops and review gates. / 增加硬停止和复核门禁。 |

```yaml
execution_flow_patch:
  - target_stage: "Stage 3: Data-shape decision / 阶段 3：数据形态价值判断"
    patch_type: route_adjustment
    content: "Prefer table structuring for ordinary table screenshots. / 普通表格截图优先转结构化表格。"
  - target_stage: "Stage 4: Log processing / 阶段 4：日志处理"
    patch_type: filter_rule_adjustment
    content: "Expand the log window and add error-code filters. / 扩大日志窗口并加入错误码过滤。"
  - target_stage: "Stage 8: Evidence verification / 阶段 8：证据校验"
    patch_type: quality_gate
    content: "If numeric reference coverage is below 95%, require human review. / 数字引用覆盖率低于 95% 时要求人工复核。"
```

## Minimum Probe Record / 最小探针记录

```yaml
fusion_probe_event:
  workflow_id: string
  scenario_id: string
  stage: bind | register | annotate | decide_shape | process | align | package | verify | cache | degrade
  item_id: optional[string]
  source_type: optional[string]
  route: optional[string]
  method: optional[string]
  tokens_in_estimate: optional[int]
  tokens_out_estimate: optional[int]
  processing_ms: optional[int]
  source_ref_present: optional[bool]
  reference_coverage: optional[float]
  route_confidence: optional[high | medium | low]
  status: success | warning | degraded | failed | skipped
  finding: string
  recommended_backfill: string
```

## Scenario Probe Templates / 场景化探针模板

| Scenario / 场景 | Must Collect / 必采项 | Key Metrics / 关键指标 | Quality Gate / 质量门禁 |
| --- | --- | --- | --- |
| Financial research / 金融研报 | PDF pages, outline, key pages, charts, tables, discarded decorations, numeric claims / PDF 页数、目录、关键页、图表、表格、装饰图丢弃、数字结论 | PDF token anomaly, key chart retention, table structuring, numeric reference coverage, chart-text consistency / PDF token 异常率、关键图保留、表格结构化、数字引用覆盖、图文一致 | Numeric reference coverage below 95% blocks automated delivery. / 数字引用覆盖率低于 95% 不自动交付。 |
| Ops diagnosis / 运维诊断 | Raw log size, filtered size, rules, time window, error code, service, request id, SQL, trace / 原始日志大小、过滤后大小、规则、时间窗、错误码、服务、请求标识、SQL、trace | Log compression, log signal retention, log token anomaly, log-SQL consistency, branch latency / 日志压缩、信号保留、token 异常、日志-SQL 一致、分支耗时 | Compression > 0.10 is too loose; < 0.005 is too aggressive. / 压缩比大于 0.10 过松，小于 0.005 过狠。 |
| Contract review / 合同审阅 | Pages, clause outline, clause page refs, scan confidence, attachments, seal pages, risk refs / 页数、条款目录、条款页码、扫描置信、附件、签章页、风险引用 | Source ID coverage, evidence link validity, low-confidence evidence, review trigger rate / 来源覆盖、证据链接有效、低置信证据、复核触发率 | Clauses without page refs cannot be final conclusions. / 无页码条款不得作为确定结论。 |
| Customer support / 客服工单 | User text, screenshot count, audio transcript quality, system snapshot, similar cases, recommendation sources / 用户描述、截图数量、录音转写质量、系统快照、相似工单、建议来源 | Modality coverage, business hint coverage, evidence link validity, audio-text consistency, unsupported conclusion rate / 模态覆盖、业务提示、证据链接、音文一致、无来源结论 | Root-cause judgment without screenshot or system-state evidence is a hypothesis. / 无截图或系统状态证据的根因判断标记为假设。 |
| Code review / 代码评审 | Diff, related files, architecture diagram, test logs, API docs, CI result / 差异、相关文件、架构图、测试日志、接口文档、CI 结果 | Log/table structuring, log signal retention, evidence link validity, unsupported conclusion rate / 日志或表格结构化、日志信号保留、证据链接有效、无来源结论 | Risk advice must cite files, logs, or tests. / 风险建议必须引用文件、日志或测试结果。 |

## Minimum Dashboard / 最小仪表盘

- Daily task count and scenario distribution. / 每日任务数量与场景分布。
- Input modality count distribution. / 输入模态数量分布。
- Token share by modality. / 按模态 token 占比。
- Fusion latency p50 / p90 / p99. / 融合处理耗时 p50 / p90 / p99。
- Slowest modality branches. / 各模态分支耗时排行。
- Log prefilter compression distribution. / 日志预过滤压缩比分布。
- PDF key-page selection rate. / PDF 关键页选择率。
- Image-token anomaly task list. / 图片 token 异常任务列表。
- Numeric reference coverage. / 数字结论引用覆盖率。
- Evidence link validity. / 证据链接有效率。
- Cross-modal conflict list. / 跨模态一致性冲突列表。
- Cache hit rate. / 缓存命中率。
- Degraded and failed events. / 降级与失败事件。
- Human review trigger rate. / 人工复核触发率。
- Budget overrun rate. / 预算超限率。

## Report Template / 报告模板

```markdown
# Multi-Modal Fusion Probe Report / 多模态融合探针报告

## 1. Overall Health / 总体健康度
- Health level / 健康等级:
- Main bottleneck / 主要瓶颈:
- Main risk / 主要风险:
- Recommended next action / 建议优先处理项:

## 2. Input Coverage / 输入覆盖情况
- Total inputs / 输入总数:
- Source ID coverage / 来源标识覆盖率:
- Business hint coverage / 业务提示覆盖率:
- Duplicate input ratio / 重复输入比例:
- Missing items / 缺失项:

## 3. Shape Routing / 形态路由情况
- Kept original / 保留原形:
- Structured / 转结构化:
- Filtered summary / 过滤摘要:
- Discarded / 丢弃:
- Route anomalies / 路由异常项:

## 4. Cost And Latency / 成本与延迟
- Total token estimate / 总 token 估算:
- Token share by modality / 按模态 token 占比:
- Fusion p99 / 融合处理 p99:
- Slow branches / 高耗时分支:
- Cache hit rate / 缓存命中率:

## 5. Evidence And Quality / 证据与质量
- Numeric reference coverage / 数字结论引用覆盖率:
- Evidence link validity / 证据链接有效率:
- Cross-modal conflicts / 跨模态冲突项:
- Low-confidence evidence ratio / 低置信证据比例:

## 6. Failure Modes / 失败模式
- Failure types / 失败类型:
- Impact / 影响范围:
- Likely cause / 可能原因:
- Suggested fix / 建议修正:

## 7. Backfill Suggestions / 回填执行流程建议
| Target Stage / 目标阶段 | Patch Type / 修正类型 | Suggestion / 建议内容 |
| --- | --- | --- |
| Stage 3 / 阶段 3 | Route / 路由修正 |  |
| Stage 4 / 阶段 4 | Branch / 分支处理修正 |  |
| Stage 8 / 阶段 8 | Evidence / 证据校验修正 |  |
| Stage 9 / 阶段 9 | Cache / 缓存复用修正 |  |
| Stage 10 / 阶段 10 | Degrade / 降级策略修正 |  |
```

## Operational Alerts / 运行告警

- Alert when a precise number has no source reference. / 精确数字无来源引用时告警。
- Alert when raw logs or whole PDFs dominate context budget. / 原始日志或整份 PDF 占据主要上下文预算时告警。
- Alert when a primary evidence branch is degraded. / 主证据分支降级时告警。
- Alert when chart, table, text, SQL, audio, or log evidence conflicts. / 图、表、文、SQL、音频或日志证据冲突时告警。
- Alert when repeated artifacts miss cache. / 重复产物未命中缓存时告警。
- Alert when low-confidence extraction feeds downstream final claims. / 低置信抽取进入最终结论时告警。
- Alert when sensitive information enters the fused context without masking. / 敏感信息未经脱敏进入融合上下文时告警。
- Alert when subtask recursion, timeout, or repeated calls exceed budget. / 子任务递归、超时或重复调用超预算时告警。

## Minimum Checklist / 最小执行清单

- Have all input items been captured? / 是否采集了所有输入项？
- Does every input have `source_id` and `item_id`? / 是否每个输入都有 `source_id` 和 `item_id`？
- Were business hints recorded or inferred? / 是否记录或推断了业务提示？
- Was every route decision recorded? / 是否记录了每个输入的路由决策？
- Were token output and processing time recorded per branch? / 是否记录了每个分支的 token 输出和耗时？
- Can the probe detect image token anomalies? / 是否能发现图片 token 异常？
- Can the probe detect log filtering anomalies? / 是否能发现日志过滤异常？
- Can the probe detect PDF over-selection or under-selection? / 是否能发现 PDF 抽取过松或过狠？
- Can the probe detect table structuring failures? / 是否能发现表格结构化失败？
- Can the probe detect numeric claims without source refs? / 是否能发现数字结论缺来源？
- Can the probe detect cross-modal numeric conflicts? / 是否能发现跨模态数字冲突？
- Can the probe detect repeated processing and cache misses? / 是否能发现重复处理和缓存缺失？
- Can the probe detect budget overruns? / 是否能发现预算超限？
- Can diagnostics be backfilled into the execution flow? / 是否能把诊断结果回填执行流程？

## Trace Hook / 追踪钩子

After observing a run, produce a project-local runtime Trace at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. Include modality distribution, route decisions, major metrics, degraded branches, evidence gaps, cache decisions, and recommended route overrides. / 观察一次运行后，依据 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地运行时 Trace，包含模态分布、路由决策、主要指标、降级分支、证据缺口、缓存决策和建议的路由覆盖项。
