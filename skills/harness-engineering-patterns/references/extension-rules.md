# Extension Rules / 扩展规则

Use this file when the current axes or matrix cannot accurately express the workflow. / 当当前轴或交织表无法准确表达工作流时，使用本文档。

## When To Extend / 何时扩展

Extend the framework when: / 以下情况需要扩展框架：

- A workflow node repeatedly does not fit any existing capability. / 某类工作流节点反复无法适配现有能力轴。
- A workflow node repeatedly does not fit any existing orchestration mode. / 某类工作流节点反复无法适配现有编排模式。
- A new business pattern needs a distinct intersection with its own symptoms and modification rules. / 新业务模式需要独立交织点及其症状和修改规则。
- Forcing the node into an existing axis would hide the real workflow problem. / 强行归类会掩盖真实工作流问题。

Do not extend when a clearer definition or boundary can solve the ambiguity. / 如果通过更清晰定义或边界即可解决歧义，不要扩展。

Before extending, inspect `pattern-catalog.md` for named patterns and extension candidates. / 扩展前先检查 `pattern-catalog.md` 中的命名模式和扩展候选。

## Adding A Vertical Capability / 新增纵轴能力

1. Add the capability to `axes.md` with key, bilingual names, fit signals, and boundary. / 在 `axes.md` 中加入 key、中英文名、适配信号和边界。
2. Add a new row to `matrix-index.md`. / 在 `matrix-index.md` 增加新行。
3. Create `references/patterns/<capability-key>/cell.md` as the vertical introduction and navigation file. / 创建 `references/patterns/<capability-key>/cell.md` 作为纵轴导论和导航文件。
4. Create `references/patterns/<capability-key>/trace.md` as the post-use trace log. / 创建 `references/patterns/<capability-key>/trace.md` 作为模式使用后的追踪日志。
5. Create one design pattern file under `references/patterns/<capability-key>/<capability-key>-<mode-key>.md` for every horizontal mode. / 为每个横轴模式在 `references/patterns/<capability-key>/<capability-key>-<mode-key>.md` 创建一个设计模式文件。
6. Create one observability metrics file under `references/patterns/<capability-key>/<capability-key>-<mode-key>-observability.md` for every horizontal mode. / 为每个横轴模式在 `references/patterns/<capability-key>/<capability-key>-<mode-key>-observability.md` 创建一个可观测性指标文件。
7. Link every new matrix cell to its dedicated design pattern file, link every design pattern file to its observability metrics file, and link every new pattern file from the vertical introduction. / 将每个新增矩阵单元链接到对应独立设计模式文件，将每个设计模式文件链接到对应可观测性指标文件，并从纵轴导论链接每个新模式文件。
8. State migration impact if existing cells should move. / 如已有交织点需要迁移，说明迁移影响。

## Adding A Horizontal Mode / 新增横轴模式

1. Add the mode to `axes.md` with key, bilingual names, fit signals, and boundary. / 在 `axes.md` 中加入 key、中英文名、适配信号和边界。
2. Add a new column to `matrix-index.md`. / 在 `matrix-index.md` 增加新列。
3. Create one new design pattern file under `references/patterns/<capability-key>/<capability-key>-<mode-key>.md` for every vertical capability. / 为每个纵轴能力在 `references/patterns/<capability-key>/<capability-key>-<mode-key>.md` 创建一个新设计模式文件。
4. Create one new observability metrics file under `references/patterns/<capability-key>/<capability-key>-<mode-key>-observability.md` for every vertical capability. / 为每个纵轴能力在 `references/patterns/<capability-key>/<capability-key>-<mode-key>-observability.md` 创建一个新可观测性指标文件。
5. Update every vertical introduction at `references/patterns/<capability-key>/cell.md` with a navigation link to the new mode cell. / 更新 `references/patterns/<capability-key>/cell.md` 中每个纵轴导论，加入指向新增模式单元的导航链接。
6. Update any diagnosis examples that mention mode selection. / 更新涉及模式选择的诊断示例。

## Adding Or Updating A Cell / 新增或更新交织点

Keep two files per intersection: one design pattern file and one observability metrics file. / 每个交织点保持两个文件：一个设计模式文件，一个可观测性指标文件。

Use this `Design Pattern / 设计模式` template: / 使用以下 `Design Pattern / 设计模式` 模板：

- `状态 / Status`
- `模式清单 / Patterns`
- `诊断用途 / Diagnostic Use`
- `适用工作流节点 / Applicable Workflow Nodes`
- `当前症状 / Current Symptoms`
- `适配信号 / Fit Signals`
- `调整方向 / Adjustment Direction`
- `修改方式 / How To Modify`
- `输入 / Inputs`
- `输出 / Outputs`
- `风险与治理 / Risks & Governance`

Use this `Observability Metrics / 可观测性指标` template: / 使用以下 `Observability Metrics / 可观测性指标` 模板：

- `质量指标 / Quality Metrics`
- `时延指标 / Latency Metrics`
- `成本指标 / Cost Metrics`
- `风险指标 / Risk Metrics`
- `Trace 指标 / Trace Metrics`

## Adding Or Updating A Vertical Introduction / 新增或更新纵轴导论

Keep one introductory file per vertical capability at `references/patterns/<capability-key>/cell.md`. These files are navigation and framing pages, not pattern detail pages. / 在 `references/patterns/<capability-key>/cell.md` 为每个纵轴能力保留一个导论文件。这些文件是导航和框架页，不是模式详情页。

Use this template: / 使用此模板：

- `Role / 定位`
- `When To Read / 何时读取`
- `Navigation / 导航`
- `Extension Note / 扩展说明`

## Adding Or Updating Trace / 新增或更新追踪

Keep one trace file per vertical capability at `references/patterns/<capability-key>/trace.md`. Use Trace before selection as inserted node evidence, and after application as outcome evidence. / 在 `references/patterns/<capability-key>/trace.md` 为每个纵轴能力保留一个追踪文件。选型前将 Trace 作为插入式节点证据，应用后将 Trace 作为结果证据。

Use this template: / 使用此模板：

- `Date / 日期`
- `Workflow / 工作流`
- `Cell / 交织点`
- `Pattern Used / 使用模式`
- `Before / 使用前`
- `Adjustment / 调整`
- `Outcome / 结果`
- `Evidence / 证据`
- `Follow-up / 后续`
- `Owner / 负责人`

When updating Trace for pre-selection evidence, include the engineering node, observed symptom, available evidence, and missing data. / 当为选型前证据更新 Trace 时，包含工程节点、已观察症状、可用证据和缺失数据。

## Extension Output / 扩展建议输出

When recommending an extension, include: / 推荐扩展时包含：

- Proposed new key and bilingual name / 建议新增 key 与中英文名
- Why existing axes are insufficient / 为什么现有轴不足
- Files to update / 需要更新的文件
- New or changed matrix cells / 新增或变更的交织点
- Backward compatibility impact / 兼容性影响
- Evidence from the current workflow showing that an existing axis or pattern is insufficient / 证明现有轴或模式不足的当前工作流证据
