# Generator-Critic / 生成器-批评器

Cell / 交织点: reflection-chain / 反思 x 链式
Capability / 能力: Reflection / 反思
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

Runtime Contract / 运行时契约: apply this cell through [Governed Reflection Execution Flow / 受治理反思执行流程](../../reflection-execution-flow.md) and its normative Schemas and `ReflectionSession`; the cell defines the change strategy, while the shared protocol owns admission, authorization, comparable revalidation, regression protection, and stopping. / 通过共享反思执行流程及其规范 Schema 与 `ReflectionSession` 应用本单元；本单元定义改变策略，共享协议负责准入、授权、可比复验、回归保护与停止。

## Design Pattern / 设计模式

Generator-Critic runs generate → critique → revise as a short chain: a generator produces output, a distinct critic evaluates it against explicit criteria, and one revision pass applies the critique. / 生成器-批评器以"生成 → 批评 → 修订"短链运行：生成器产出结果，独立批评器按显式判据评估，一次修订应用批评意见。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Reflection / 反思 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 代表性定义 / Representative definition; source table maps Reflection / 反思 x Chain / 链式 in arXiv:2605.13850. The v2 article deliberately moved this pattern from Loop to Chain because production runs converge in 1–2 critique passes; open-ended repair belongs to Self-Heal Loop at reflection-loop. / 代表性定义 / Representative definition；来源表将 Reflection / 反思 x Chain / 链式 映射到该单元。论文 v2 有意将本模式从循环移到链式，因为生产环境通常 1–2 轮批评即收敛；开放式修复属于 reflection-loop 的自愈循环。
- 问题 / Problem: A single generator may produce plausible but unchecked output. / 单一生成器可能产生看似合理但未被检查的输出。
- 架构方案 / Architectural Solution: Use a generator to produce output and a separate critic step to evaluate, identify issues, and request repair when needed. The article defines three feedback variants: self-critique (same model, different prompt role), cross-model critique (a different model reviews), and tool-grounded critique (tests, linters, or verifiers supply the feedback). / 使用生成器产出结果，再用独立批评步骤评估、识别问题并按需请求修复。论文定义三种反馈变体：自评（同模型不同提示角色）、跨模型批评（另一模型评审）、工具接地批评（测试、静态检查或验证器提供反馈）。
- 工程权衡 / Engineering Trade-offs: Improves quality and catches errors, but adds cost and can inherit critic blind spots. The article cites evidence (Huang et al., CRITIC, Self-Refine) that pure self-correction without external feedback is unreliable — prefer tool-grounded or cross-model critique for correctness-critical output. / 提升质量并捕获错误，但增加成本，也可能继承批评器盲点。论文引用证据（Huang 等、CRITIC、Self-Refine）表明缺乏外部反馈的纯自纠错不可靠——正确性关键产出应优先工具接地或跨模型批评。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when output should pass through a sequential critique step. / 当产出需要经过顺序批评步骤时使用。

### Feedback Variant Selection / 反馈变体选择

| Variant / 变体 | Cost / 成本 | Reliability / 可靠性 | Use When / 适用 |
| --- | --- | --- | --- |
| Self-critique / 自评 | Lowest / 最低 | Weakest — shares generator blind spots / 最弱——与生成器共享盲点 | Style, formatting, completeness checks. / 风格、格式、完整性检查。 |
| Cross-model / 跨模型 | Medium / 中 | Better — independent priors / 较好——先验独立 | Judgement-heavy review without executable checks. / 无可执行检查的判断型评审。 |
| Tool-grounded / 工具接地 | Varies / 视工具 | Strongest — external ground truth / 最强——外部基准 | Code, data, claims verifiable by tests or retrieval. / 可被测试或检索验证的代码、数据、论断。 |

Chain rules / 链式规则:

- Critic criteria must be explicit and written before generation; a critic without criteria degenerates into a second generator. / 批评判据必须在生成前显式写出；无判据的批评器会退化为第二个生成器。
- Cap the chain at 1–2 critique passes; if issues persist, escalate to Self-Heal Loop (reflection-loop) or human review instead of extending the chain. / 链长上限 1–2 轮批评；问题仍存在时升级到自愈循环（reflection-loop）或人工评审，而不是加长链。
- For failure-cost-asymmetric domains, bias the critic toward the expensive failure direction (the article's healthcare case biases toward acuity upgrades because under-triage is fatal). / 失败成本不对称领域应让批评器偏向昂贵失败方向（论文医疗案例偏向提升急重度，因为低估分诊致命）。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Generator-Critic / 生成器-批评器.
- 诊断用途 / Diagnostic Use: Use when output should pass through a sequential critique step. / 当产出需要经过顺序批评步骤时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 验证测试、知识沉淀 / Verification, knowledge memory.
- 当前症状 / Current Symptoms: Output ships on generator confidence alone; review exists but has no written criteria; critique cycles run open-ended without convergence. / 产出仅凭生成器自信直接交付；有评审但无成文判据；批评循环开放运行不收敛。
- 适配信号 / Fit Signals: 评估结果按顺序进入下一步改进 / Evaluation results feed the next improvement step in order.
- 调整方向 / Adjustment Direction: Insert a critic step with written criteria after generation; choose the feedback variant by verifiability; cap passes at 1–2 and define the escalation path. / 生成后插入带成文判据的批评步骤；按可验证性选择反馈变体；轮次限制 1–2 并定义升级路径。
- 修改方式 / How To Modify: 1) Write critique criteria as a checklist or rubric. 2) Pick self / cross-model / tool-grounded per the table. 3) Wire critic findings into one revision pass. 4) Route unresolved findings to reflection-loop or human review. / 1）将批评判据写成清单或量表；2）按上表选择自评、跨模型或工具接地；3）批评发现接入一次修订；4）未解决项路由到 reflection-loop 或人工评审。
- 输入 / Inputs: Generator output, critique criteria, verification tools or reviewer model, failure-cost policy. / 生成器产出、批评判据、验证工具或评审模型、失败成本策略。
- 输出 / Outputs: Critique report (findings mapped to criteria), revised output, escalation decision. / 批评报告（发现对应判据）、修订产出、升级决策。
- 风险与治理 / Risks & Governance: Critic blind spots shared with the generator (mitigate with tool-grounded feedback); rubber-stamp critique that always passes (`FAIL_0007` inverse — watch approval rate near 100%); unbounded critique chains belong to reflection-loop, not here; record critique reports per `GOV_0002`. / 批评器与生成器共享盲点（用工具接地反馈缓解）；橡皮图章式批评恒通过（`FAIL_0007` 的反面——关注接近 100% 的通过率）；无界批评链属于 reflection-loop 而非本单元；批评报告按 `GOV_0002` 记录。

Observability Metrics File / 可观测性指标文件: [reflection-chain-observability.md](reflection-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
