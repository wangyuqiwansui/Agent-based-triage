# Handoff Chain / 交接链

Cell / 交织点: collaboration-chain / 协作 x 链式
Capability / 能力: Collaboration / 协作
Mode / 模式: Chain / 链式
Source / 来源: arXiv:2605.13850 (https://arxiv.org/html/2605.13850)

Use this file as the design pattern source for this 7x6 matrix intersection. / 将本文档作为该 7x6 交织点的设计模式来源。

## Design Pattern / 设计模式

Handoff Chain transfers work through ordered roles with an explicit context package at each boundary — artifact, done criteria, open risks, acceptance check — and responsibility moves only after the receiver runs the acceptance check and accepts. / 交接链让工作按有序角色传递，每个边界附显式上下文包——产物、完成标准、未决风险、验收检查——责任只在接收方运行验收检查并接受后才转移。

### Article Grounding / 论文依据

- 论文坐标 / Article Coordinate: Collaboration / 协作 x Chain / 链式 (Sequential / 顺序).
- 论文依据 / Article Basis: 矩阵列名模式 / Matrix-listed pattern; source table maps Collaboration / 协作 x Chain / 链式 in arXiv:2605.13850; design content is an engineering extension. / 矩阵列名模式 / Matrix-listed pattern；来源表将 Collaboration / 协作 x Chain / 链式 映射到该单元；设计内容为工程扩展。
- 问题 / Problem: When work passes between roles with only the artifact and no context, the receiver reconstructs intent from scratch, open risks silently drop at each boundary, and when a defect surfaces nobody can say which side of which handoff owned it — handoff points are exactly where state gets lost. / 当工作在角色间只传产物不传上下文时，接收方要从零重建意图、未决风险在每个边界悄悄丢失，缺陷浮出水面时没人说得清哪次交接的哪一侧该负责——交接点正是状态丢失的高发处。
- 架构方案 / Architectural Solution: Define each handoff as a contract: the sender assembles a context package (artifact, done criteria, open risks, acceptance check) and the receiver runs the acceptance check before accepting; responsibility transfers only on acceptance, rejected handoffs return with reasons, and every handoff event is recorded per `GOV_0002`. / 把每次交接定义为契约：交出方组装上下文包（产物、完成标准、未决风险、验收检查），接收方先运行验收检查再接受；责任只在接受后转移，被拒交接带原因退回，每次交接事件按 `GOV_0002` 入账。
- 工程权衡 / Engineering Trade-offs: Explicit context packages and acceptance checks add per-boundary overhead, but they convert silent state loss into visible rejections; the sequential shape stays easy to audit yet weak when branching or feedback dominates — route those flows to routing or loop cells instead. / 显式上下文包与验收检查增加每个边界的开销，但把无声的状态丢失变成可见的拒收；顺序结构保持易审计，却在分支或反馈占主导时乏力——那类流程应改走路由或循环单元。
- 工作流诊断用途 / Workflow Diagnosis Use: Use when work passes through ordered actors or roles. / 当工作按顺序经过多个参与者或角色时使用。

### Handoff Contract / 交接契约

```yaml
handoff:
  from_owner: sending_role                  # 交出方角色 / role releasing the work
  to_owner: receiving_role                  # 接收方角色 / role taking the work
  artifact: deliverable_reference           # 交付物引用，非复述 / reference to the deliverable, not a retelling
  context_package:
    done_criteria: what_finished_means      # 交出方眼中"完成"的定义 / sender's definition of done
    open_risks: known_unresolved_items      # 已知未决风险与假设 / known risks and assumptions still open
    decisions: choices_and_rejected_paths   # 关键取舍与被否路径 / key choices and rejected alternatives
  acceptance_check: receiver_runnable       # 接收方可独立运行的验收检查 / check the receiver can run alone
  on_accept: responsibility_transfers       # 接受即责任转移并入账 / acceptance transfers ownership, recorded
  on_reject: return_with_reason             # 拒收带原因退回交出方 / rejection returns with reasons
```

Chain rules / 链式规则:

- No package, no handoff: an artifact arriving without done criteria and open risks is rejected by default — the receiver never guesses missing context. / 无包不交接：缺完成标准与未决风险的产物默认拒收——接收方绝不猜测缺失的上下文。
- Responsibility is singular at all times: until acceptance the sender owns the work, after acceptance the receiver does; there is no shared-limbo interval. / 责任始终唯一：接受前归交出方，接受后归接收方；不存在共担的悬空区间。
- Every handoff, acceptance verdict, and rejection reason is recorded per `GOV_0002`; repeated rejections at one boundary escalate per `GOV_0001` instead of ping-ponging. / 每次交接、验收裁定与拒收原因按 `GOV_0002` 入账；同一边界反复拒收按 `GOV_0001` 升级而非来回弹。

### Pattern Template / 模式模板

- 状态 / Status: 已命名候选 / Named candidate.
- 模式清单 / Patterns: Handoff Chain / 交接链.
- 诊断用途 / Diagnostic Use: Use when work passes through ordered actors or roles. / 当工作按顺序经过多个参与者或角色时使用。
- 适用工作流节点 / Applicable Workflow Nodes: 协作交接、发布交付 / Collaboration handoff, delivery.
- 当前症状 / Current Symptoms: Receivers repeatedly ask "what was the intent here" after taking over work; risks known upstream resurface downstream as surprises; defects surface after several handoffs and ownership is unassignable; work bounces between two roles with no acceptance criteria. / 接收方接手后反复追问"当时意图是什么"；上游已知的风险在下游以意外形式复发；缺陷经过几次交接后浮现却无法定责；工作在两个角色间来回弹而没有验收标准。
- 适配信号 / Fit Signals: 协作按明确顺序交接，前一角色完成后后一角色接手 / Collaboration hands off in order from one role to the next.
- 调整方向 / Adjustment Direction: Contract every handoff boundary: context package from the sender, runnable acceptance check by the receiver, responsibility transfer only on acceptance. / 契约化每个交接边界：交出方给上下文包、接收方跑验收检查、只在接受后转移责任。
- 修改方式 / How To Modify: 1) Map the role sequence and each boundary's deliverable. 2) Define the context package fields (done criteria, open risks, decisions) per boundary. 3) Give each receiver an independently runnable acceptance check. 4) Wire the reject path (return with reason) and the escalation bound for repeated rejections. 5) Record all handoff events per `GOV_0002`. / 1）梳理角色顺序与每个边界的交付物；2）为每个边界定义上下文包字段（完成标准、未决风险、取舍）；3）给每个接收方一个可独立运行的验收检查；4）接好拒收路径（带原因退回）与反复拒收的升级上限；5）全部交接事件按 `GOV_0002` 入账。
- 输入 / Inputs: Ordered role sequence, per-boundary deliverable definitions, context package template, acceptance checks, escalation policy. / 有序角色序列、每边界交付物定义、上下文包模板、验收检查、升级策略。
- 输出 / Outputs: Accepted handoffs with recorded verdicts, rejection events with reasons, a responsibility ledger showing exactly one owner at any moment, boundary-level rework statistics. / 带裁定记录的已接受交接、带原因的拒收事件、任一时刻恰有一个负责人的责任账本、边界级返工统计。
- 风险与治理 / Risks & Governance: Handoff points are `FAIL_0006` state-loss hotspots — the context package makes implicit state explicit and the default-reject rule stops artifacts traveling without it; unclear ownership between agents is `FAIL_0008` — the singular-responsibility rule leaves no shared-limbo interval; repeated boundary rejections escalate per `GOV_0001`; all handoff events are recorded per `GOV_0002` so post-hoc audits can pin which boundary lost what. / 交接点是 `FAIL_0006` 状态丢失热点——上下文包把隐式状态显式化，默认拒收规则阻止裸产物流转；智能体间归属不清是 `FAIL_0008`——责任唯一规则消灭共担悬空区间；边界反复拒收按 `GOV_0001` 升级；全部交接事件按 `GOV_0002` 入账，事后审计可定位哪个边界丢了什么。

Observability Metrics File / 可观测性指标文件: [collaboration-chain-observability.md](collaboration-chain-observability.md)

## Trace Hook / 追踪钩子

After this pattern is recommended or applied, produce a project-local Trace proposal at `.harness-analysis/<analysis_id>/trace.yaml` using `references/trace-schema.md`. / 推荐或应用本模式后，使用 `references/trace-schema.md` 在 `.harness-analysis/<analysis_id>/trace.yaml` 生成项目本地 Trace 建议。
