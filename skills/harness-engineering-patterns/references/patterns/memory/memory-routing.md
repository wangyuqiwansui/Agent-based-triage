# Hierarchical Retrieval / 层级检索

Cell / 交织点: memory-routing / 记忆 x 路由
Capability / 能力: Memory / 记忆
Mode / 模式: Routing / 路由
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Hierarchical Retrieval routes each query by intent across tiered memory stores — hot working state, warm project knowledge, cold archive — querying the cheapest sufficient tier first, falling through on miss, and promoting entries that prove themselves by access frequency. / 层级检索按查询意图在分层记忆存储间路由——热层工作状态、温层项目知识、冷层归档——先查最便宜的足够层、未命中再下探，并按访问频率晋升被反复证明有用的条目。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Memory / 记忆 x Routing / 路由 (Routing / 路由).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Memory / 记忆 x Routing / 路由 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Memory / 记忆 x Routing / 路由 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: One flat memory store makes every query pay the same price: session state, project decisions, and years of archive compete in a single index, so lookups that should be instant scan everything, broad recalls drag stale archive material into context, and the store that answers "what did we decide last week" is the same slow, noisy one that answers "what happened two years ago". / 单一扁平记忆库让每个查询付同一价钱：会话状态、项目决策与多年归档挤在一个索引里，本该瞬时的查找要全库扫描、宽泛召回把过期归档拖进上下文，回答"上周我们决定了什么"和回答"两年前发生了什么"用的是同一个又慢又吵的库。
- 架构方案 / Architectural Solution: Tier the stores and route by query intent: hot (current session and task working state, always cheapest), warm (project knowledge — decision records, historical cases, norms), cold (archive and external corpora); classify each query to its likely tier, query the cheapest sufficient tier first, fall through on explicit miss, promote entries upward by access frequency and demote by staleness, and record routing decisions and hits per `GOV_0002`. / 给存储分层并按查询意图路由：热层（当前会话与任务工作状态，永远最便宜）、温层（项目知识——决策记录、历史案例、规范）、冷层（归档与外部语料）；每个查询先分类到可能层、先查最便宜的足够层、显式未命中再下探，条目按访问频率上升晋升、按陈旧度降级，路由决策与命中按 `GOV_0002` 入账。
- 工程权衡 / Engineering Trade-offs: This differs from the RAG Pipeline (memory-chain) — that is within-store chain processing (retrieve, rerank, inject) while this is cross-store tier routing that decides which store to enter at all; tiering makes common lookups fast and cheap, but misclassified queries either short-circuit on a shallow tier and miss the real answer below, or dive cold unnecessarily and pay archive latency — and tier boundaries plus promotion thresholds need local re-derivation per Law 5. / 与 RAG 管道（memory-chain）不同——那是库内链式处理（检索、重排、注入），这是跨库分层路由、决定进哪个库；分层让常见查找又快又便宜，但查询误分类要么在浅层短路、错过下层真答案，要么无谓下潜冷层、白付归档时延——层边界与晋升阈值需按定律 5 本地重推。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when the workflow must route retrieval through levels of memory. / 当工作流必须按记忆层级路由检索时使用。

### Retrieval Tier Table / 检索层级表

| Tier / 层 | Stored Content / 存储内容 | Index Method / 索引方式 | Query Timing / 查询时机 | Relative Cost / 相对成本 | Promotion / Demotion / 晋升与降级 |
| --- | --- | --- | --- | --- | --- |
| Hot / 热层 | Current session and task working state. / 当前会话与任务工作状态。 | In-context or key-value, exact keys. / 上下文内或键值、精确键。 | First for any query — always. / 任何查询永远先查。 | Near zero. / 近乎为零。 | Evict to warm on task closure. / 任务关闭降入温层。 |
| Warm / 温层 | Project knowledge: decision records, historical cases, norms. / 项目知识：决策记录、历史案例、规范。 | Structured plus semantic index. / 结构化加语义索引。 | On hot miss for project-scoped intents. / 项目域意图热层未命中时。 | Moderate. / 中等。 | Promote by access frequency; demote stale entries cold. / 按访问频率晋升；陈旧条目降入冷层。 |
| Cold / 冷层 | Full history archive, external corpora. / 全量历史归档、外部语料。 | Bulk search, offline indexes. / 批量搜索、离线索引。 | On warm miss or explicit deep-history intent. / 温层未命中或显式深历史意图。 | High latency and volume. / 高时延高体量。 | Promote proven answers to warm with provenance. / 被证明有用的答案携出处晋升温层。 |

Routing rules / 路由规则:

- Fall-through requires an explicit miss verdict, not a weak partial match — a shallow answer that "sort of fits" is how the real answer below gets short-circuited. / 下探以显式未命中裁定为前提，而非勉强的部分匹配——"差不多沾边"的浅层答案正是下层真答案被短路的方式。
- Cross-tier recall injects selectively: results carry tier and provenance, and cold material enters context only after relevance filtering — never as a bulk dump. / 跨层召回选择性注入：结果携层级与出处，冷层材料经相关性过滤才入上下文——绝不整体倾倒。
- Boundary with the RAG Pipeline (memory-chain): once this pattern picks the store, the within-store retrieve-rerank-inject chain belongs to that cell. / 与 RAG 管道（memory-chain）的边界：本模式选定库之后，库内检索-重排-注入链归那个单元。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Hierarchical Retrieval / 层级检索.
- 诊断用途 / Diagnostic Use: Use when the workflow must route retrieval through levels of memory. / 当工作流必须按记忆层级路由检索时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 需求进入、协作交接 / Intake, collaboration handoff.
- 当前症状 / Current Symptoms: Simple working-state lookups pay full archive-search latency; recalls drag stale years-old material into context alongside last week's decision; the team re-derives decisions that exist in records because retrieval from the flat store is too noisy to trust. / 简单的工作状态查找付出全量归档搜索的时延；召回把多年前的过期材料和上周决策一起拖进上下文；因扁平库检索噪音太大不可信，团队重推已有记录的决策。
- 适配信号 / Fit Signals: 需要按历史案例、项目知识或决策记录选择路径 / History, project knowledge, or decisions choose the path.
- 调整方向 / Adjustment Direction: Tier stores into hot-warm-cold, classify queries by intent, query cheapest-sufficient first with explicit-miss fall-through, and promote by access frequency. / 存储分为热-温-冷三层，按意图分类查询、先查最便宜足够层、显式未命中下探、按访问频率晋升。
- 修改方式 / How To Modify: 1) Partition existing memory into hot (session/task state), warm (decision records, cases, norms), cold (archive, external corpora). 2) Define query-intent classes and their entry tiers. 3) Wire explicit-miss fall-through and tier-tagged, provenance-carrying results. 4) Set promotion (access frequency) and demotion (staleness) rules; re-derive thresholds per Law 5. 5) Record routing decisions and hits per `GOV_0002`. / 1）把现有记忆划分为热（会话/任务状态）、温（决策记录、案例、规范）、冷（归档、外部语料）；2）定义查询意图类及其入口层；3）接显式未命中下探与带层级、出处标注的结果；4）设晋升（访问频率）与降级（陈旧度）规则，阈值按定律 5 重推；5）路由决策与命中按 `GOV_0002` 入账。
- 输入 / Inputs: Query with intent class, tier definitions and indexes, promotion and demotion thresholds, provenance metadata per entry, relevance filter for cold recalls. / 带意图类的查询、层定义与索引、晋升降级阈值、每条目出处元数据、冷层召回的相关性过滤器。
- 输出 / Outputs: Routed retrieval results tagged with tier and provenance, miss and fall-through events, promotion and demotion events, routing decision log. / 带层级与出处标注的路由检索结果、未命中与下探事件、晋升降级事件、路由决策日志。
- 风险与治理 / Risks & Governance: Wrong-tier routing and premature short-circuit are `FAIL_0002` retrieval misses — audit answered-at-tier against where the true answer lived, and require explicit miss verdicts before fall-through stops; unfiltered cross-tier recall is `FAIL_0001` context pollution — cold material passes relevance filtering and carries provenance before injection; promotion without provenance lets unvetted archive content masquerade as current knowledge — promotions carry source and date; routing decisions and hits are recorded per `GOV_0002` so tier boundaries can be re-derived from evidence per Law 5. / 错层路由与过早短路是 `FAIL_0002` 检索未中——审计"在哪层作答"对照真答案所在层，且停止下探前必须有显式未命中裁定；跨层召回不过滤是 `FAIL_0001` 上下文污染——冷层材料经相关性过滤、携出处才注入；无出处晋升让未经审视的归档内容冒充现行知识——晋升必须带来源与日期；路由决策与命中按 `GOV_0002` 入账，层边界可按定律 5 凭证据重推。

Observability Metrics File / 可观测性指标文件: [memory-routing-observability.md](memory-routing-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
