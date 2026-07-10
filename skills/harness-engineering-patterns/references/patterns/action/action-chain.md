# Prompt Chaining / 提示链

Cell / 交织点: action-chain / 行动 x 链式
Capability / 能力: Action / 行动
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Prompt Chaining decomposes an action sequence into ordered prompt or tool steps, where each step's output is validated against an explicit contract before it becomes the next step's input, so errors are caught at the handoff instead of amplifying down the chain. / 提示链将行动序列分解为有序的提示或工具步骤，每步输出先按显式契约校验，再成为下一步输入，使错误在交接处被拦截而不是沿链放大。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Action / 行动 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Action / 行动 x Chain / 链式 in arXiv:2605.13850; the authors even considered merging it with Chain-of-Thought; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Action / 行动 x Chain / 链式 映射到该单元；作者甚至考虑过将其与思维链合并；设计内容为工程扩展。
- 问题 / Problem: A multi-step action run as one monolithic prompt hides intermediate failures: a defect produced early is only discovered at the final output, and the whole run must be redone. / 多步行动如果作为单个巨型提示执行，会隐藏中间失败：早期产生的缺陷直到最终输出才被发现，整次运行必须重做。
- 架构方案 / Architectural Solution: Split the action into ordered steps with an explicit handoff contract per step — validated input, output contract, and a declared on-failure action (retry, rollback, or escalate) — and pass state between steps explicitly rather than through implicit conversation memory. / 将行动拆分为带显式交接契约的有序步骤——校验后的输入、输出契约、声明的失败动作（重试、回滚或升级）——步骤间状态显式传递，而不是依赖隐式会话记忆。
- 工程权衡 / Engineering Trade-offs: Per-step validation localizes errors and keeps each prompt small and testable, but adds handoff overhead, and the chain remains weak when branching or feedback dominates; the central risk is error propagation — an unvalidated early defect amplifies through every later step. / 逐步校验能就地定位错误并让每个提示小而可测，但增加交接开销，且分支或反馈占主导时链式仍然薄弱；核心风险是错误传播——未经校验的早期缺陷会在后续每一步被放大。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when action is represented as a deterministic sequence of prompts or tool steps. / 当行动由确定性的提示或工具步骤序列表示时使用。

### Step Handoff Contract / 步骤交接契约

```yaml
prompt_chain:
  steps:
    - step_id: ""
      input_from: ""            # previous step output or initial input; state passed explicitly / 上一步输出或初始输入；状态显式传递
      validation: ""            # check on input before running (schema, invariants) / 运行前对输入的检查（schema、不变量）
      output_contract: ""       # required shape and quality of this step's output / 本步输出的必需结构与质量
      on_failure: retry | rollback | escalate   # declared before the run / 运行前声明
  state_passing: explicit       # no implicit reliance on conversation memory (FAIL_0006) / 不隐式依赖会话记忆（防 FAIL_0006）
  step_ledger: record input, output, validation result per step (GOV_0002) / 逐步记录输入、输出、校验结果（GOV_0002）
```

Chain rules / 链式规则:

- A step may start only after the previous step's output passed its contract; a failed contract triggers the declared on-failure action, never a silent pass-through. / 只有上一步输出通过契约后本步才能开始；契约失败触发声明的失败动作，绝不静默放行。
- Retries are bounded per step; exhausting retries escalates rather than looping (`FAIL_0007`). / 每步重试有上限；重试耗尽即升级而不是继续循环（防 `FAIL_0007`）。
- When later steps need branching on intermediate results, hand routing to Tool Dispatch (action-routing); when the sequence needs replanning, escalate to Plan-and-Execute (action-orchestration). / 当后续步骤需要根据中间结果分支时，路由交给工具分派（action-routing）；当序列需要重规划时，升级到计划执行（action-orchestration）。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Prompt Chaining / 提示链.
- 诊断用途 / Diagnostic Use: Use when action is represented as a deterministic sequence of prompts or tool steps. / 当行动由确定性的提示或工具步骤序列表示时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 执行实现、发布交付 / Implementation, delivery.
- 当前症状 / Current Symptoms: One monolithic prompt performs a multi-step action and fails opaquely; defects surface only at final output and force full reruns; steps implicitly depend on conversation memory and break when context is trimmed. / 单个巨型提示执行多步行动且失败原因不透明；缺陷只在最终输出暴露并迫使整次重跑；步骤隐式依赖会话记忆，上下文被裁剪即断裂。
- 适配信号 / Fit Signals: 行动步骤必须按顺序执行，前置结果决定后续动作 / Actions must run in sequence and prior results determine later actions.
- 调整方向 / Adjustment Direction: Split the action into contract-bounded steps with explicit state passing and declared failure actions. / 将行动拆成契约约束的步骤，状态显式传递，失败动作事先声明。
- 修改方式 / How To Modify: 1) Cut the action at natural validation points into ordered steps. 2) Write the handoff contract (input_from, validation, output_contract, on_failure) per step. 3) Make state passing explicit — each step receives named inputs, not "whatever is in context". 4) Bound retries per step and wire escalation. 5) Record the step ledger. / 1）在自然校验点将行动切成有序步骤；2）为每步写交接契约（input_from、validation、output_contract、on_failure）；3）状态显式传递——每步接收命名输入，而非"上下文里有什么用什么"；4）限定每步重试并接通升级；5）记录步骤台账。
- 输入 / Inputs: Action goal, step decomposition with contracts, initial input, per-step retry budget. / 行动目标、带契约的步骤分解、初始输入、每步重试预算。
- 输出 / Outputs: Final artifact, per-step ledger (input, output, validation result), failure events with the on-failure action taken. / 最终产物、逐步台账（输入、输出、校验结果）、带所执行失败动作的失败事件。
- 风险与治理 / Risks & Governance: Error propagation — an unvalidated early defect amplifies down the chain, so contracts must gate every handoff; implicit state between steps is lost when context shifts (`FAIL_0006`) — pass state explicitly and persist the ledger per `GOV_0002`; unbounded per-step retries become runaway loops (`FAIL_0007`) — bound and escalate; steps that execute code or write files stay inside sandbox boundaries per `GOV_0003`. / 错误传播——未经校验的早期缺陷沿链放大，契约必须把守每次交接；步骤间隐式状态在上下文变动时丢失（`FAIL_0006`）——显式传递状态并按 `GOV_0002` 持久化台账；每步重试不设限会变成失控循环（`FAIL_0007`）——限定并升级；执行代码或写文件的步骤按 `GOV_0003` 留在沙箱边界内。

Observability Metrics File / 可观测性指标文件: [action-chain-observability.md](action-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
