# Node Gap Checklist / 节点不足与弥补检查清单

## Quick Navigation / 快速导航

Use only the responsibility sections that match the inventoried nodes: 1–4 for intake and planning, 5–7 for execution and delivery, 8–10 for operation and reuse, 11–12 for handoff and governance. Review applicable cross-node checks for the actual edges. Use [the audit playbook](workflow-audit-playbook.md) for coverage, dispositions, priorities and closure. / 仅按清单内节点读取相应职责章节：1–4 为进入与规划，5–7 为执行与交付，8–10 为运行与复用，11–12 为交接与治理。对实际连线检查适用跨节点条目。覆盖、结论、优先级及闭环以审计流程为准。

## Purpose And Use / 目的与使用

Use this checklist after reconstructing the actual workflow with [workflow-nodes.md](workflow-nodes.md), alongside [diagnosis-method.md](diagnosis-method.md). It helps turn an observed failure or a specific uncertainty into a small, verifiable improvement. It is a question bank, not a maturity score or a required architecture. / 使用 [workflow-nodes.md](workflow-nodes.md) 还原实际工作流后，结合 [diagnosis-method.md](diagnosis-method.md) 使用本清单，将已观察的失败或具体不确定性转成小而可验证的改进。本清单是问题库，不是成熟度评分表，也不是必须实现的架构。

- The 12 responsibility types below are prompts. One real node may cover several types; one type may occur in several nodes. Do not require 12 nodes, split by filename, or infer a missing responsibility from a missing directory. Follow actual inputs, decisions, ownership, outputs and state transitions. / 以下 12 类职责仅作提示；一个真实节点可以承担多类职责，同类职责也可出现在多个节点。不得强制凑齐 12 个节点，不得按文件名切节点，不得因缺少某目录就推断职责缺失。沿实际输入、决策、归属、输出和状态迁移识别节点。
- Apply relevant questions to every identified node and to each real handoff. Mark an item `not_applicable` with a reason when its prerequisite does not exist; for example, a read-only workflow does not need a rollback mechanism for writes it never performs. / 对每个已识别节点及实际交接应用相关问题；前提不存在时以理由标记“不适用”，例如纯只读工作流无需为从未执行的写入补回滚机制。
- Separate documented intent, implemented behavior, test coverage and observed runtime behavior. A design document does not prove enforcement; an implementation does not prove the deployed version uses it; a passing test proves only its exercised conditions. Record revision, environment and time where relevant. / 分开记录文档意图、实现行为、测试覆盖与运行表现。设计文档不能证明约束已生效，实现存在不能证明部署版本正在使用它，测试通过只证明其实际覆盖条件。按需记录版本、环境与时间。
- Missing evidence is not a confirmed defect. Use `unknown / 待核实` when a path or observation is unavailable; identify the smallest read, sample or controlled check that would resolve it. A `confirmed_gap / 已确认不足` requires an applicable obligation and evidence of its violation or demonstrable absence on the relevant path. / 缺证不等于确认缺陷。路径或观察不可得时使用 `unknown / 待核实`，注明可消除不确定性的最小读取、样本或受控检查。`confirmed_gap / 已确认不足` 必须同时具备适用的职责要求及相关路径违反要求或可证明确实缺失的证据。
- Check counterevidence before recommending change: another node, service, procedure or owner may already supply the control. Resolve disagreements between documents, code, tests and runs explicitly; do not silently select the source that makes a finding look stronger. / 提出改动前检查反证：其他节点、服务、流程或负责人可能已经承担控制职责。明确处理文档、代码、测试与运行证据的冲突，不得只挑能强化问题的来源。
- Keep a satisfactory node as `adequate / 已足够` with its evidence and limits. Do not invent a problem for every table cell, require every failure mode, or turn every uncertainty into a new component. / 对已满足要求的节点记录 `adequate / 已足够`、依据及覆盖限制。不得为了填满表格每格而造问题，不得要求每类失败模式都存在，也不得把每个不确定性转成一个新组件。
- Prefer clarifying an existing contract, fixing one transition or adding one observation over introducing orchestration, agents, reflection loops or permanent approval gates. Consider a pattern only when the simple repair cannot meet a demonstrated need, then follow the selection workflow. / 优先澄清现有契约、修复一处迁移或增加一个观察点；不要直接增加编排、Agent、反思循环或常驻审批门禁。只有简单修复无法满足已证实需求时才考虑模式，并遵循选型流程。
- Acceptance examples below are proposed checks, not evidence that they ran or universal pass thresholds. Adapt their input, expected outcome, limits and observation window to the project's contract; label checks `not_run`, `passed`, `failed`, `blocked` or `not_applicable` with their actual scope. Use existing evidence before adding tests or instrumentation. / 下方验收示例是待选检查，不是已经执行的证据，也不是通用达标阈值。按项目契约调整输入、预期结果、边界及观察窗口，并按实际范围标记“未运行、通过、失败、受阻、不适用”。新增测试或埋点前先使用既有证据。

For each relevant finding, retain the node and boundary, required behavior, current evidence, observed deviation, consequence, minimal remedy, owner and acceptance check. Use the failure IDs in [failure-modes.md](failure-modes.md) only when they match the evidence; the library is not exhaustive. / 每个相关发现保留节点及边界、应有行为、当前证据、实际偏差、后果、最小弥补措施、负责人和验收方式。仅在证据吻合时引用 [failure-modes.md](failure-modes.md) 的失败 ID；该库并不穷尽所有问题。

## 1. Intake / 需求进入 (`intake`)

- **Verify / 核验：** What event admits a request, who supplies its goal, and which output makes it complete? Are required inputs, duplicate requests and changes of scope handled consistently? Clarify only ambiguity that changes correctness, authority or consequential behavior. / 什么事件接收请求，谁提供目标，以何种输出判定完成？必要输入、重复请求与范围变更是否有一致处理？仅澄清会改变正确性、权限或重要行为的歧义。
- **Failure signals / 失败信号：** Work begins without a required identifier; different consumers interpret the same request differently; the same submission creates duplicate work; work is reported complete although the requested artifact is absent. / 缺少必需标识仍启动工作；同一请求被不同接收方理解为不同任务；同次提交重复创建任务；所需产物未生成却报告完成。
- **Minimal remedy / 最小弥补：** Add the missing field or decision rule at the existing intake boundary, record the accepted scope and completion condition, and reuse an existing request identity where duplicates matter. Avoid forcing a questionnaire onto requests whose intent is already clear. / 在现有入口补缺失字段或判定规则，记录已接受范围及完成条件；重复有影响时复用既有请求标识。意图已清晰的请求无需强制填写问卷。
- **Acceptance example / 验收示例：** Replay one valid and one incomplete sample. The valid request produces the agreed task and output contract; the incomplete request identifies the exact missing prerequisite before dependent work. A duplicate sample has the project-defined result without unintended additional work. / 回放一个有效样本和一个不完整样本：有效请求形成约定任务及输出契约；不完整请求在依赖工作启动前指出具体缺失前提；重复样本产生项目约定结果且不引发意外重复工作。

## 2. Context Sensing / 上下文感知 (`context-sensing`)

- **Verify / 核验：** Which sources support the next decision, how are current versions selected, and how are conflicting or unavailable sources represented? Can filtering remove evidence needed by a downstream step? Are external content and instructions kept distinguishable? / 下一决策依赖哪些来源，如何选择当前版本，如何表达冲突或不可用来源？过滤是否会移除下游所需证据？外部内容与执行指令能否区分？
- **Failure signals / 失败信号：** Decisions cite stale settings, miss an available governing file, mix environments, or present an empty retrieval as proof that no record exists. Irrelevant content crowds out the decisive evidence. / 决策引用过期配置、漏掉可读取的约束文件、混淆环境，或把空检索结果当成记录不存在的证明；无关内容挤掉关键证据。
- **Minimal remedy / 最小弥补：** Attach source location, version or observation time to decisive inputs; add the specific missing retrieval or freshness check; preserve an explicit unknown or conflict for downstream consumers. Limit collection to the decision's needs. / 给关键输入附来源、版本或观察时间；补充具体遗漏的检索或时效检查；向下游保留明确未知项或冲突。采集范围以决策所需为限。
- **Acceptance example / 验收示例：** For a sample with old and current configuration, the decision uses the intended version and points to it. For an unavailable required source, the output exposes the missing evidence and follows the defined fallback rather than fabricating a value. / 在同时存在旧、新配置的样本中，决策使用目标版本并可定位来源；必需来源不可用时，输出暴露缺证并走约定后备路径，不编造取值。

## 3. Decomposition / 问题拆解 (`decomposition`)

- **Verify / 核验：** Does each task produce an outcome needed by the goal? Are dependencies, shared resources and ownership represented? Are tasks treated as independent only when their required inputs and writes permit it? / 每项任务是否产出目标所需结果？依赖、共享资源和归属是否明确？只有输入和写入允许独立执行时，才把任务视为相互独立了吗？
- **Failure signals / 失败信号：** Two workers modify the same artifact without coordination; a task starts before its prerequisite; essential integration is unassigned; subtasks finish while the overall outcome remains incomplete. / 两个工作者无协调修改同一产物；前置条件未就绪就启动任务；必要集成无人负责；子任务全部完成而整体结果仍不完整。
- **Minimal remedy / 最小弥补：** Add the missing dependency or integration owner; merge inseparable work; make each delegated task's input, output and completion condition explicit. Do not add hierarchy solely because there are many files. / 补缺失依赖或集成负责人；合并不可分离的工作；写明委派任务的输入、输出和完成条件。不得仅因文件多就增加层级。
- **Acceptance example / 验收示例：** Walk the task graph for one representative goal. Every required outcome has a producer, every consumer has available prerequisites, and an intentionally delayed prerequisite prevents only dependent work from proceeding. / 对一个代表性目标走查任务图：每个必需结果都有生产者，每个消费者都有可用前提；故意延迟一个前提时，只阻止依赖它的工作继续。

## 4. Design / 方案设计 (`design`)

- **Verify / 核验：** Is correctness defined before choosing structure? Can the existing path or a small change satisfy the requirement? Does the proposed behavior fit actual limits, interfaces, authority and failure costs? Which assumption would invalidate it? / 是否先定义正确性再选择结构？现有路径或小改动能否满足要求？方案是否适配真实限制、接口、权限和失败代价？哪项假设不成立会使方案失效？
- **Failure signals / 失败信号：** A named pattern is selected without a bottleneck; a design depends on unavailable capabilities; incompatible interfaces remain unspecified; cost or recovery requirements contradict the selected path. / 未发现瓶颈就选定命名模式；设计依赖不可用能力；接口不兼容却未说明；成本或恢复要求与选定路径矛盾。
- **Minimal remedy / 最小弥补：** State the behavior contract and decisive tradeoff; compare the current path with the smallest alternative; verify the one uncertain interface or assumption that determines feasibility. / 写明行为契约和决定性取舍；比较当前路径与最小替代方案；核实决定可行性的关键接口或假设。
- **Acceptance example / 验收示例：** A concrete input, boundary case and failure case can be traced to outputs and responsible components. The chosen approach meets the stated limits, and any unverified dependency remains a named condition rather than a claim of readiness. / 一个具体输入、一个边界案例和一个失败案例均可追到输出及负责组件；所选方案满足已定限制，尚未验证的依赖保留为具名条件，不宣称已就绪。

## 5. Implementation / 执行实现 (`implementation`)

- **Verify / 核验：** Does the actual execution path enforce input, authority and state preconditions? Which calls change external state, and how is their outcome established? Are partial changes visible to consumers before completion? / 实际执行路径是否落实输入、权限及状态前提？哪些调用改变外部状态，如何确认其结果？未完成的部分修改是否会被消费者当成完整结果读取？
- **Failure signals / 失败信号：** Invalid parameters reach a side-effecting tool; a direct path bypasses a guard; success is recorded before a required write finishes; rerunning repeats an already committed effect. / 无效参数进入有副作用工具；直连路径绕过守卫；必需写入结束前已记录成功；重跑重复执行已提交副作用。
- **Minimal remedy / 最小弥补：** Fix the affected execution boundary, validate the relevant inputs and preconditions, and record results at the point where they become authoritative. Add idempotency or compensation only for the demonstrated side-effect risk; see the retry check below. / 修复受影响执行边界，校验相关输入及前提，在结果具有权威性的时点记录结果。仅针对已证实的副作用风险补幂等或补偿，参见下方重试检查。
- **Acceptance example / 验收示例：** A valid sample reaches the expected state; an invalid or out-of-scope sample produces no prohibited effect. Interrupting the affected boundary yields the documented partial or terminal state, and recovery does not silently repeat a completed effect. / 有效样本到达预期状态；无效或超范围样本不产生禁止效果；在受影响边界中断后，产生约定部分状态或终态，恢复时不会悄然重复已完成副作用。

## 6. Verification / 验证测试 (`verification`)

- **Verify / 核验：** Which requirement does each check prove, against which version and environment? Are expected outcomes independent of the behavior under test? Are relevant negative cases covered, and are skipped checks distinguishable from passes? / 每项检查证明哪条要求，针对哪个版本与环境？预期结果是否独立于待测行为？相关反例是否覆盖，跳过检查能否与通过区分？
- **Failure signals / 失败信号：** Tests repeat implementation logic without checking its result; fixtures exclude the known failure; a missing dependency silently skips the only integration check; an older build's result is used to approve a newer build. / 测试复述实现逻辑而不检查结果；样本排除了已知失败；依赖缺失悄然跳过唯一集成检查；以旧版本通过结果批准新版本。
- **Minimal remedy / 最小弥补：** Repair the decisive assertion or sample and bind results to the candidate version. Reuse existing checks; add a focused failure case when needed instead of imposing a large new suite on every change. / 修复决定性断言或样本，将结果绑定候选版本。复用已有检查；必要时补一个聚焦失败用例，不对每次改动强加大型新套件。
- **Acceptance example / 验收示例：** The selected check distinguishes the original failure from the proposed correction under the same condition. A missing environment reports `not_run` with its coverage limit, and the report claims no validation beyond what actually executed. / 所选检查在相同条件下能区分原始失败与修正结果；环境缺失时报告“未执行”及覆盖限制，报告不声称超出实际执行范围的验证。

## 7. Delivery / 发布交付 (`delivery`)

- **Verify / 核验：** Is the delivered artifact the version that was verified? Who receives it, and what establishes usable delivery? If delivery changes a live system, are compatibility, migration and recovery responsibilities defined where needed? / 交付产物是否为已验证版本？谁接收它，如何证明可用交付？若交付改变线上系统，是否按需明确兼容性、迁移和恢复责任？
- **Failure signals / 失败信号：** A build succeeds but the user cannot access the artifact; a different revision is deployed; migration runs without a compatible reader; delivery fails midway but status remains successful. / 构建成功但用户无法访问产物；部署了不同版本；迁移执行后读端不兼容；交付中途失败而状态仍为成功。
- **Minimal remedy / 最小弥补：** Bind the handoff to an immutable version or artifact identity, check receipt and essential usability, and document the applicable recovery action. A local document delivery may need only a verified path and readable contents. / 将交付绑定不可变版本或产物标识，检查接收及基本可用性，并记录适用恢复动作。本地文档交付可能只需确认路径有效和内容可读。
- **Acceptance example / 验收示例：** The recipient opens or retrieves the intended artifact, its identity matches validation evidence, and the agreed smoke check passes. Where a deployment recovery procedure applies, its evidence refers to the deployed version and stated recovery conditions. / 接收者能打开或获取目标产物，标识与验证证据一致，约定冒烟检查通过；适用部署恢复流程时，其证据关联实际部署版本及规定恢复条件。

## 8. Monitoring / 运行监控 (`monitoring`)

- **Verify / 核验：** Can an owner distinguish healthy progress, stalled work, terminal failure and missing telemetry? Does a signal cover the important outcome rather than merely tool activity? Are thresholds tied to the workflow's expected rate and deadline? / 负责人能否区分正常推进、停滞、终态失败与遥测缺失？信号是否覆盖重要结果而不仅是工具活动？阈值是否关联流程预期速率与截止时间？
- **Failure signals / 失败信号：** Requests are accepted but no output arrives while dashboards remain green; a quiet workload triggers repeated false alerts; an alert has no owner; logs reveal failure only after users report it. / 请求接收后无输出而面板仍显示正常；低负载反复触发误报；告警无人负责；用户反馈后才从日志发现失败。
- **Minimal remedy / 最小弥补：** Use the existing event or status source to track the missing outcome, attach an actionable owner and condition, and distinguish absence of work from absence of evidence. Add only the telemetry needed to resolve the observed blind spot. / 使用现有事件或状态来源追踪缺失结果，附上可行动的负责人及触发条件，区分没有工作和没有证据。仅增加消除已观察盲点所需的遥测。
- **Acceptance example / 验收示例：** A controlled stalled sample becomes visible within the agreed window with enough context to identify the affected run and next action. A normal idle interval stays quiet, and disabled telemetry is shown as unknown rather than healthy. / 一个受控停滞样本在约定窗口内被识别，并提供受影响运行及下一动作所需上下文；正常空闲期不误报，遥测关闭显示未知而非健康。

## 9. Incident Repair / 事故修复 (`incident-repair`)

- **Verify / 核验：** Are symptom containment, cause investigation and restoration distinguished? Is the current state known before retry or repair? Who may apply the fix, and what evidence establishes that service and affected data are restored? / 是否区分症状遏制、根因调查与恢复？重试或修复前是否知道当前状态？谁有权执行修复，何种证据证明服务及受影响数据已经恢复？
- **Failure signals / 失败信号：** A restart hides the symptom but loses unfinished work; repair changes evidence before it is captured; the same fix repeats without diagnosis; recovery creates duplicate effects or leaves corrupted records. / 重启掩盖症状却丢失未完成工作；修复前未留存必要证据；同一修复反复执行而未查明原因；恢复产生重复效果或遗留损坏记录。
- **Minimal remedy / 最小弥补：** Capture the relevant state, apply the smallest authorized containment or repair, and give it an explicit stop condition and post-repair check. Preserve unresolved cause uncertainty instead of presenting a workaround as root-cause resolution. / 保留相关状态，执行最小且已授权的遏制或修复，明确停止条件及修后检查。保留未解决的根因不确定性，不把临时绕过说成根因修复。
- **Acceptance example / 验收示例：** Reproduce the affected condition safely or inspect a representative recorded incident. Restoration meets the service criterion, unfinished obligations are accounted for, and recurrence detection or a remaining investigation item is assigned. / 安全复现受影响条件或检查代表性事故记录：恢复满足服务判据，未完责任均有处置，对复发检测或仍需调查的事项明确归属。

## 10. Knowledge Memory / 知识沉淀 (`knowledge-memory`)

- **Verify / 核验：** Which recurring decision would benefit from reuse? Can the next run retrieve the relevant decision, evidence, scope and validity conditions? How are superseded records distinguished, and is retained data necessary and permitted? / 哪类反复决策值得复用？下一次运行能否检索到相关决策、证据、适用范围与有效条件？如何区分已过期记录，保留数据是否必要且获准？
- **Failure signals / 失败信号：** The same constraint is repeatedly rediscovered; a prior workaround is reused outside its scope; contradictory records have no authority rule; old secrets or unnecessary raw inputs persist in memory. / 同一约束被反复重新发现；旧临时方案被跨范围复用；冲突记录无权威选择规则；记忆中长期保存旧秘密或不必要原始输入。
- **Minimal remedy / 最小弥补：** Add one searchable decision record with source, applicability and replacement information, or repair retrieval to an existing record. Prefer the existing knowledge store; do not add a vector database merely to preserve a small decision log. / 补一条可检索且包含来源、适用条件和替代关系的决策记录，或修复对既有记录的检索。优先现有知识存储，不为保存少量决策日志就增加向量数据库。
- **Acceptance example / 验收示例：** A fresh run facing the same condition retrieves and correctly applies the record. A changed-condition sample rejects or revalidates it, and the retained content excludes unnecessary sensitive data. / 新运行遇到相同条件时能检索并正确使用记录；条件变化的样本会拒绝套用或重新验证；保留内容不含不必要的敏感数据。

## 11. Collaboration Handoff / 协作交接 (`collaboration-handoff`)

- **Verify / 核验：** Who owns an obligation before and after transfer, and what constitutes acceptance? Does the recipient receive the exact input version, required result and limits? Who resolves conflicting results, missing workers and late replies? / 交接前后分别由谁负责，何种行为代表接受？接收方是否获得确切输入版本、所需结果及限制？冲突结果、工作者缺席和迟到回复由谁处理？
- **Failure signals / 失败信号：** Both actors assume the other owns the next step; a result arrives without its assumptions or evidence; aggregation drops a dissenting result; a late worker overwrites a newer decision. / 双方都以为对方负责下一步；结果缺少假设或证据；汇总丢弃异议结果；迟到工作者覆盖更新决策。
- **Minimal remedy / 最小弥补：** Make the existing handoff message carry task identity, input version, output requirement, receiver and acknowledgment. Define one conflict or timeout rule where the observed failure needs it; parallel delegation is not required. / 在现有交接消息中携带任务标识、输入版本、输出要求、接收方及确认信息；针对已观察失败补一条冲突或超时规则，无需因此采用并行委派。
- **Acceptance example / 验收示例：** A recipient can complete a sample handoff without guessing its version or owner. A missing acknowledgment remains visible to the sender; a conflicting or late result is resolved or rejected under the stated rule, with its evidence retained. / 接收方无需猜测版本或负责人就能完成样本交接；未确认事项对发送方持续可见；冲突或迟到结果按已定规则解决或拒绝，且保留其证据。

## 12. Governance Review / 治理审查 (`governance-review`)

- **Verify / 核验：** Which actions need constraints or approval under the actual policy and user authorization? Is the check on every relevant execution path and bound to the specific action, scope and current conditions? Does a changed action invalidate only the authorization that no longer applies? / 按实际策略和用户授权，哪些动作需要约束或审批？检查是否覆盖每条相关执行路径，并绑定具体动作、范围与当前条件？动作变化时，是否仅使不再适用的授权失效？
- **Failure signals / 失败信号：** A route label is treated as permission; an approved artifact is changed before execution without the required recheck; a bypass executes an unauthorized action; repeated approval requests stall already authorized low-risk work. / 把路由标签当作权限；获批产物执行前改变但未按要求复验；旁路执行未授权动作；重复索要审批阻塞已获授权的低风险工作。
- **Minimal remedy / 最小弥补：** Enforce the applicable boundary at the action, carry existing authorization forward while it remains valid, and record the decision basis. Add a human gate only where the governing policy or consequential uncertainty requires it. / 在行动处落实适用边界，既有授权有效时继续沿用，并记录决策依据。仅在治理策略或有重要后果的不确定性要求时增加人工门禁。
- **Acceptance example / 验收示例：** An authorized in-scope action proceeds under its existing authorization; an out-of-scope or materially altered action takes the required deny or review path. The evidence identifies the action and policy actually evaluated. / 已授权且在范围内的动作沿用既有授权继续；超范围或实质改变的动作进入要求的拒绝或复审路径；证据可定位实际被评估的动作与策略。

## Cross-Node Checks / 跨节点检查

Check real edges and shared obligations even when individual nodes look sufficient. Report one underlying finding with all affected nodes instead of multiplying the same issue across rows. / 即使单个节点看似充分，也应检查真实连边及共享责任；同一根因记录一项发现并列出影响节点，不要在多行重复放大问题数量。

### Handoff And End-To-End Completion / 交接与端到端完成

- **Verify / 核验：** Does each producer's output satisfy the consumer's actual input contract, including version, completeness and failure meaning? Who owns work while it is queued, rejected or awaiting acceptance? / 每个生产者输出是否满足消费者实际输入契约，包括版本、完整性和失败含义？排队、拒绝和等待接收期间由谁负责？
- **Failure signal / 失败信号：** An upstream success becomes unusable downstream; no owner holds an in-flight obligation; all nodes say complete while the final user outcome is absent. / 上游成功产物到下游无法使用；流转中责任无人持有；所有节点均称完成但用户最终结果缺失。
- **Minimal remedy / 最小弥补：** Correct the boundary field or status meaning, name the transfer owner and define a final outcome check at the existing endpoint. / 修正边界字段或状态语义，明确交接责任人，在现有终点定义最终结果检查。
- **Acceptance example / 验收示例：** Follow one normal and one rejected handoff from trigger to terminal result. Every required output is consumed or explicitly disposed of, and the final status agrees with the user-visible outcome. / 从触发到终态跟踪一次正常交接和一次拒收交接；每项必要输出均被消费或明确处置，最终状态与用户可见结果一致。

### Shared State And Concurrent Writers / 共享状态与并发写入

- **Verify / 核验：** Which record is authoritative, who may write it, and what protects a state transition from stale or concurrent updates? Do cache, task status, artifact identity and external state agree at the boundaries that matter? / 哪条记录具有权威性，谁可写入，如何避免状态迁移被陈旧或并发更新破坏？关键边界上的缓存、任务状态、产物标识和外部状态是否一致？
- **Failure signal / 失败信号：** A later writer loses a completed result, two actors claim exclusive ownership, status says success before the artifact exists, or recovery reloads an incompatible snapshot. / 后写入者丢失已完成结果；两个参与者同时占有独占责任；产物尚不存在而状态已成功；恢复加载了不兼容快照。
- **Minimal remedy / 最小弥补：** Establish the authoritative record and fix the affected atomic boundary or revision check. Serialize only competing updates when sufficient; add distributed coordination only if real multi-writer requirements demand it. / 确立权威记录，修复受影响原子边界或版本检查；足够时仅串行化竞争更新，只有真实多写者要求才增加分布式协调。
- **Acceptance example / 验收示例：** Two updates based on the same revision cannot silently overwrite each other's accepted result. A restart restores a consistent status/artifact pair or exposes a recoverable incomplete state with its owner. / 基于同一版本的两次更新不能悄然覆盖已接受结果；重启恢复一致的状态与产物，或暴露带负责人的可恢复未完成状态。

### Exceptional Exits, Cancellation And Partial Results / 异常出口、取消与部分结果

- **Verify / 核验：** What happens on input rejection, dependency failure, cancellation and deadline expiry? Which outputs are valid partial results, which obligations remain, and who closes resources or escalates the unresolved work? / 输入拒绝、依赖失败、取消和截止到期后如何处理？哪些输出是有效部分结果，哪些责任未完，谁关闭资源或接管未解决工作？
- **Failure signal / 失败信号：** An exception leaves a task indefinitely running; cancelled workers still publish; partial output is labeled complete; resource cleanup destroys evidence needed for recovery. / 异常让任务永久运行；取消后工作者仍发布结果；部分输出被标成完整；清理资源销毁了恢复所需证据。
- **Minimal remedy / 最小弥补：** Add the missing terminal or recoverable state, record remaining obligations, and prevent late continuation past the relevant boundary. Preserve the small amount of state needed for diagnosis and recovery. / 补缺失终态或可恢复状态，记录剩余责任，阻止越过相关边界的迟到继续执行，并保留诊断和恢复所需最小状态。
- **Acceptance example / 验收示例：** Interrupt a sample at the actual vulnerable boundary. Its state becomes the documented failure, cancellation or partial result; dependent work does not interpret it as success, and outstanding resources and obligations have a known disposition. / 在实际脆弱边界中断样本：状态变为约定失败、取消或部分结果，下游不把它理解为成功，未结资源与责任均有明确处置。

### Retries When Side-Effect Outcomes Are Unknown / 副作用结果未知时的重试

- **Verify / 核验：** Can a timeout occur after an external write commits? Does recovery distinguish `not performed`, `performed` and `unknown`? Is a stable operation identity preserved, and can authoritative status be queried before another attempt? / 超时是否可能发生在外部写入已提交之后？恢复是否区分“未执行、已执行、未知”？是否保留稳定操作标识，再尝试前能否查询权威状态？
- **Failure signal / 失败信号：** Timeout is treated as proof of failure; retries create duplicate orders, messages or artifacts; a fresh key defeats existing deduplication; retry limits reset after every restart. / 将超时当成失败证明；重试产生重复订单、消息或产物；换新键绕过既有去重；每次重启都清零重试上限。
- **Minimal remedy / 最小弥补：** Preserve operation identity, reconcile against the authoritative external state, and use the destination's durable deduplication when supported. If effects remain unknown and no safe retry exists, keep the operation unresolved and route to the existing recovery owner. Bound attempts and elapsed time. / 保留操作标识，与权威外部状态对账，目标支持时使用其持久去重；效果仍未知且无安全重试方式时，保持未决并交给既有恢复负责人。限制尝试次数和总耗时。
- **Acceptance example / 验收示例：** Simulate or inspect a write that commits but loses its response. Recovery identifies the committed effect or explicitly retains uncertainty; it does not blindly create another effect. Repeated failure reaches the defined stop condition, including across restart. / 模拟或检查“写入已提交但响应丢失”的案例：恢复识别已提交效果或明确保留不确定性，不盲目产生第二次效果；反复失败达到已定停止条件，重启后也不失效。

### Resource Limits And Backpressure / 资源约束与背压

- **Verify / 核验：** Which deadline, cost, concurrency, queue, rate, storage or human-review limit actually constrains the workflow? Are checks made before expensive work and do they include retries, aggregation and cleanup? What does the caller see when capacity is unavailable? / 实际约束流程的是哪项截止时间、成本、并发、队列、速率、存储或人工审核容量？昂贵工作前是否检查，预算是否包含重试、汇总和清理？容量不可用时调用方看到什么？
- **Failure signal / 失败信号：** Parallelism overloads a shared service; queues grow without a response policy; retries consume the budget needed for final validation; cost rises without a quality gain; users wait indefinitely for unavailable reviewers. / 并行压垮共享服务；队列增长但无应对策略；重试耗尽最终验证预算；成本增加而质量无提升；用户无限等待不可用审核者。
- **Minimal remedy / 最小弥补：** Bound the actual bottleneck, account for the remaining required work, and use the existing queue, rejection or deferral path. Reduce optional work before weakening required correctness or authorization checks. Derive limits from workload evidence or explicit constraints. / 限制真实瓶颈，计入剩余必需工作，使用既有排队、拒绝或延期路径。先削减可选工作，不削弱必需正确性或权限检查。依据负载证据或显式约束确定限制。
- **Acceptance example / 验收示例：** At the agreed capacity boundary, admitted work stays within its limits and excess work receives the documented response. Reserved validation or cleanup can still finish; measured latency and cost are compared with the baseline under equivalent conditions. / 在约定容量边界上，准入工作不越限，超额工作得到约定响应；预留验证或清理仍能完成；在等价条件下比较实测延迟、成本与基线。

## Completion Check / 检查完成条件

The checklist is complete for a workflow slice when every real node and relevant boundary has an evidence-backed status, material unknowns have explicit verification actions, and each recommended remedy changes a named behavior with a checkable outcome. It is acceptable to conclude that the current path is sufficient or that a particular conclusion remains unknown. Do not claim the workflow is proven reliable merely because all checklist headings were visited. / 对一个工作流切片，只有每个真实节点和相关边界均有基于证据的状态、重要未知项均有明确补证动作、每条建议都改变具名行为且具备可检查结果，才算完成本清单。可以得出现有路径已经足够或某结论仍待核实；不能因遍历了所有标题就宣称流程可靠性已被证明。
