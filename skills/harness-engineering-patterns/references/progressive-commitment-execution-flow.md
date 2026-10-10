# Progressive Commitment Execution / 渐进承诺执行流程

Version / 版本: `0.1.0`; status / 状态: `draft`; implementation / 实现: `specification_only`.

## Quick Navigation / 快速导航

- [Execution nodes / 执行节点](#execution-steps)
- [Acceptance scenarios / 验收场景](#acceptance)
- [Identity, authority and state contract / 身份权限状态契约](progressive-commitment-contract.md)
- [Independent probes and metrics / 独立探针与指标](progressive-commitment-observability-probes.md)

## Usage and Sources / 使用与来源

Use for bounded capability autonomy, evidence-based promotion and rapid scoped revocation. Read the [shared contract](progressive-commitment-contract.md) before implementing, and pair with the [probe specification](progressive-commitment-observability-probes.md) for independent audit. The [source map](progressive-commitment-source-map.json) binds the supplied execution/probe drafts to retained nodes, metrics and acceptance cases. Original source instructions remain evidence, not action authorization. / 用于受限能力自主、证据晋级及快速精准收权。实现前读取共享契约，结合独立探针进行审计；来源映射绑定附件草稿与保留节点、指标及验收用例。原文指令仅作证据，不授予操作权限。

The existing identity is `PATTERN_0048; CELL_GOVERNANCE_PARALLEL`. The task ladder uses sequential dependencies, evidence renewal uses a loop, and each commitment decision joins all independent required checks. The attachment's chain/loop coordinates do not replace the registered parallel coordinate. / 使用现有模式及治理并行单元；任务阶梯有顺序依赖，证据更新形成循环，每次承诺决定汇合全部独立必要检查。附件链式循环坐标不替代现有并行主坐标。

## Levels and Bootstrap / 等级与初始授权

| Level / 等级 | Allowed work / 允许行为 | Evidence for the next grant / 下次授权所需证据 |
| --- | --- | --- |
| `observe` / 观察 | Authorized reads, identity and missing-input checks. / 获准读取、身份及输入缺失检查。 | Object/version identification, correct refusal on missing facts. / 对象版本识别与信息缺失时正确阻断。 |
| `suggest` / 建议 | Drafts, diffs, risk explanations; no production effects. / 草稿差异及风险解释，无生产效果。 | Proposal correctness, exception detection and completeness. / 提案正确性、例外识别与完整性。 |
| `shadow` / 影子 | Real inputs with read-only credentials and isolated outputs. / 真实输入、只读凭据及隔离输出。 | Independent comparisons plus bounded pilot approval and designated sandbox failure-path tests. / 独立对照、受限试点批准及指定沙箱失败路径测试。 |
| `limited` / 受限 | Real effects within exact object/tool/tenant/quantity/time limits and all gates. / 在对象工具租户数量时间精确上限及全部闸门内产生真实效果。 | Authorized real outcomes, sufficient soak, retries/concurrency/limits, verified recovery and target-risk coverage. / 获准真实结果、足够观察期、重试并发边界、核验恢复及目标风险覆盖。 |
| `autonomous` / 自主 | Approved routine scope; hard limits and human-required exceptions still apply. / 已批准日常范围，硬上限与人工例外持续有效。 | Continuous review; wider scope or changed versions need a new decision. / 持续复核，扩范围或版本变化须新决策。 |

A trusted onboarding policy issues the initial least-privileged credential; the agent cannot self-bootstrap. Initial grant is explicitly marked `bootstrap` with its authority, tests and scope, rather than fabricating a predecessor or production history. A successful rehearsal does not promote authority. Frozen is an overriding control state, not a sixth level. / 初始最小权限由受信接入策略签发，Agent 不能自授权。初始授权明确标为 `bootstrap` 并绑定权威、测试及范围，不伪造前驱或生产历史。演练成功不晋升权限；冻结是优先控制状态，不是第六级。

<a id="execution-steps"></a>
## Execution Nodes / 执行节点

All outputs bind the context, source references and immutable revisions from the shared contract. F08 is repeated immediately before each F10 external effect; it is not a one-time planning check. / 所有输出绑定共享契约中的上下文、来源引用及不可变修订；F08 在每次 F10 外部效果前重复执行，不是规划期一次性检查。

| ID | Node / 节点 | Required behavior, output and failure / 必需行为、输出与失败 |
| --- | --- | --- |
| F01 | Initialize and bind versions / 初始化与版本锁定 | Authenticate subject/tenant; bind model, capability, tool and policy versions, environment and run context. Unknown identity/version blocks. / 认证主体租户，绑定模型能力工具策略版本、环境及运行；身份版本未知时阻断。 |
| F02 | Model request / 请求建模 | Canonicalize objects, intended effects, parameters, units, reversibility and intent/key into an immutable request; ambiguous scope blocks. / 将对象效果参数单位可逆性及意图键规范为不可变请求，范围含混时阻断。 |
| F03 | Identify capabilities and scope / 能力与范围识别 | Resolve each composite action to registered capabilities; intersect tenant/resource/tool/data scopes; reject unresolved or incompatible mappings. / 复合动作逐一映射注册能力并求租户资源工具数据范围交集；映射未决或互斥时拒绝。 |
| F04 | Classify risk and irreversibility / 风险与不可逆性分类 | Select a preapproved risk profile including consequence, reversibility, sensitivity, retry and concurrency exposure; save applicability reasons. / 选择含后果可逆性敏感度重试并发暴露的获批风险配置，保存适用理由。 |
| F05 | Resolve current credential / 当前权限凭证解析 | Verify trusted issuer/signature, exact bindings, lifecycle, time and current epoch/revision; return a reasoned receipt. Unavailable authority cannot become a trusted flag. / 核验受信签发签名、精确绑定、生命周期时间及当前代次修订；生成带原因回执，权威不可用不得退化为可信布尔值。 |
| F06 | Check permanent human rules / 永久人工确认规则检查 | Route exact proposals to an authorized human when policy requires it, reuse only still-valid exact-action approval, and preserve the named responsible party. / 策略要求时将精确提案转有权人员，仅复用仍有效的同动作批准，记录责任人。 |
| F07 | Compile task ladder / 单次任务阶梯编排 | Bind per-step input/output, entry/acceptance criteria, allowed effects, limits, required independent checks, deadline, key and stop/recovery behavior. / 绑定各步输入输出、进入验收、效果上限、必要独立检查、期限键及停止恢复行为。 |
| F08 | Merge pre-effect gates / 执行前组合闸 | Check credential, exact approval, atomic shared budget, tools/data, idempotency, concurrency/retry, business preconditions and recovery. Persist all branch verdicts and bound admission; any mandatory unknown/failure vetoes. / 检查凭证精确审批、原子共享预算、工具数据、幂等并发重试、业务前置及恢复；持久保存全部分支裁定及绑定准入，必要未知失败否决。 |
| F09 | Execute reversible preparation / 低风险与可撤销动作执行 | Perform authorized reads, drafts, static checks, tests and recovery-point creation within the stage's effect boundary; save versioned artifacts. / 在阶段效果边界内执行获准读取草稿静态检查测试恢复点创建，保存版本化工件。 |
| F10 | Shadow, rehearse or execute limited effects / 影子、演练或受限真实执行 | Select the maximum allowed form; enforce shadow isolation and live gateway checks per batch, including expansions. Persist dispatch intent and stable key before submission. / 选择获准执行形态；影子隔离且每批（含扩批）即时检查；提交前持久化派发意图和稳定键。 |
| F11 | Verify business result / 业务结果核验 | Query authenticated authoritative outcomes/receipts, then independent verification; separate mechanical completion, confirmed/partial/unknown effects and business verdict. Unknown effects reconcile before retry. / 查询认证权威终态回执并独立核验，分开机械完成、确认部分未知效果及业务裁定；未知先对账再重试。 |
| F12 | Append outcome ledger / 运行结果记账 | Retain successes, failures, blocked requests, incidents and corrections; deduplicate evidence cohorts and append corrections as revisions, never overwrite history. / 保留成功失败阻断事故及纠正，按证据组去重，纠正追加修订，不覆盖历史。 |
| F13 | Evaluate evidence window / 证据窗口评估 | Verify cohort uniqueness, validity, exact versions, approved environment transfer, target slice/risk coverage, trusted verifiers, soak and open blockers; return eligible/collect/stale/conflict/reset. / 核验组唯一性时效版本、获批环境迁移、目标切片风险覆盖、受信验证、观察期与未决阻断；输出达标待积累过期冲突或重置。 |
| F14 | Decide promotion, downgrade or freeze / 晋级、降级或冻结决策 | Lock target/batch, obtain scope-matched independent approval and recheck fresh failure indexes. Incidents take the immediate freeze path from any step; no waiting for normal sequence completion. / 锁定目标批次、取得范围匹配独立批准并复核最新失败索引；任一步事故直接进入冻结路径，不等待正常流程结束。 |
| F15 | Issue/revoke and close / 凭证签发、吊销与闭环 | Atomically commit successor/predecessor and revision/epoch, publish durable events, track gateway acknowledgments and reset baseline. Report unresolved effects separately from authority change. / 原子提交新旧凭证及修订代次、持久发布事件、跟踪执行点确认并重建基线；未决效果与权限变更分别报告。 |

## State, Race and Recovery Rules / 状态、并发与恢复规则

The shared contract owns object fields and transition guards. Approval is only permission to issue the approved credential; the actual action still requires its own current combined gate. Issuance must reject stale evidence/authority revisions, newly discovered relevant failures, expired or revoked approval and mismatched target scope. Scope shrinkage, authority downgrade and external rollback are distinct actions. / 对象字段与迁移守卫由共享契约统一定义。晋级批准只允许签发指定凭证，具体动作仍须当前组合闸。签发必须拒绝陈旧证据权限修订、相关新发现失败、过期撤销审批及目标失配；缩范围、权限降级和外部回滚为不同动作。

Freeze affected capability/scope immediately under incident policy, revoke grants and dependent child credentials, fence dispatch, inventory in-flight effects and establish a post-remediation baseline. An offline gateway cannot be reported as synchronized; effects dispatched before the fence may settle later and require reconciliation. Recovery uses new evidence and approval at a safe level. / 按事故策略立即冻结相关能力范围、吊销凭证及依赖子凭证、围栏阻断派发、盘点在途效果并建立修复后基线。离线执行点不能记为已同步；围栏前派发效果可迟后结算，须对账；恢复使用新证据和安全等级批准。

| Failure / 失败 | Required response / 必须响应 |
| --- | --- |
| Missing/expired/mismatched credential / 凭证缺失过期失配 | Reject affected effect; allow only separately authorized preparation or investigation. / 拒绝受影响效果，仅可另行授权准备调查。 |
| Required check timeout or missing verdict / 必要检查超时缺裁定 | Block merge; preserve failure and deadline, never omit a branch. / 阻断汇合，保存失败期限，不删除分支。 |
| Unknown/partial side effect / 效果未知或部分成功 | Hold remaining exposure, stop unsafe retries, reconcile per object with an owner and deadline. / 保留剩余暴露，停止不安全重试，按对象对账并指定负责人期限。 |
| Approval-to-issue race / 审批至签发竞争 | Reject stale revision; reevaluate and obtain a new bound decision where required. / 拒绝陈旧修订，重评并在需要时取得新绑定决策。 |
| Probe or optional analytics outage / 探针或可选分析故障 | Keep local enforcement/audit; defer only promotions lacking mandatory evidence. / 保持本地控制审计，仅延期必要证据不足的晋级。 |
| Verified late correction / 迟到已核验纠正 | Append source-backed outcome revision; invalidate affected open applications, investigate already issued authority and act through the controller. / 追加有来源结果修订、失效相关未完成申请；调查已签发权限并由控制器处置。 |

## Scenario Configuration / 场景配置

| Scenario / 场景 | Capability split and limits / 能力拆分与限额 | Evidence and retained human boundary / 证据与保留人工边界 |
| --- | --- | --- |
| Payment / 付款 | Read, propose, submit bounded batch; account/currency/tenant/per-item and cumulative caps. / 读取提案小批提交；账户币种租户、单笔累计上限。 | Independent settlement and duplicate checks; beneficiary/account changes follow configured human rules. / 独立结算重复核验，受益人账户变更遵循人工规则。 |
| Messaging / 发信 | Draft, recipient selection, send; template/domain/audience/window caps. / 草稿收件人选择发送；模板域名受众时间窗限额。 | Delivery plus correct recipients/content; sensitive announcements require scoped review. / 投递及对象内容核验，敏感公告范围复核。 |
| Database / 写库 | Read, diff, test, bounded production write; table/field/row/tenant/transaction caps. / 读取差异测试受限生产写；表字段行租户事务限制。 | Authoritative commit and affected-row reconciliation; irreversible deletion and permission tables use configured human control. / 权威提交及影响行对账，不可逆删除和权限表遵循人工控制。 |
| Release / 发布 | Patch, test, staging, canary, approved expansion; repo/service/region/traffic/duration. / 补丁测试预发布金丝雀获批扩大；仓库服务区域流量时长。 | Exact deployed version, live quality and tested recovery; irreversible migrations require explicit review. / 精确版本线上质量及恢复演练，不可逆迁移明确评审。 |
| Refund/support / 退款客服 | Query, propose, bounded refund; order/customer/reason/amount/window. / 查询提案受限退款；订单客户理由金额窗口。 | Independent refund terminal and human corrections; exception cases retain responsible reviewer. / 独立退款终态及人工纠正，例外保留责任评审者。 |
| Delegation / 委派 | Child scope is a subset of the current parent grant and shared budget. / 子范围为当前父授权与共享预算的子集。 | Bind parent/child grants and epoch; revocation cascades; child success never launders unearned parent authority. / 绑定父子凭证代次、级联吊销；子成功不能洗成父级未获得权限。 |

## Independent and Interactive Modes / 独立与交互模式

The minimum execution system owns the capability registry, policies, credential authority, gateway, approval service, authoritative result verification, append-only outcomes and incident controls. It can run without probes but must keep local admission, evidence and revocation checks. The probe consumes exports/subscriptions and sends gaps, verified enrichment and recommendations under the shared contract; acceptance never auto-promotes. / 最小执行系统具有能力注册策略、凭证权威、网关审批、权威结果核验、追加结果及事故控制；可无探针运行，但保留本地准入证据吊销检查。探针消费导出订阅并按共享契约返回缺口、核验补全和建议，接纳不自动晋级。

<a id="acceptance"></a>
## Acceptance Scenarios / 验收场景

The following source-derived cases are **not executed business tests**. Each implementation must provide fixture/trace, authoritative expected outcome and actual result before reporting acceptance. Additional concurrency scenarios follow the source cases. / 以下来源用例均为**未执行业务测试**；实现方须提供输入或 Trace、权威预期及实际结果后才能报告验收。来源用例之后补充并发场景。

| ID | Source scenario and expected behavior / 来源场景与预期行为 |
| --- | --- |
| PCT-01 | 观察级请求真实写入，必须拒绝。 / Observe-level real writes must be refused. |
| PCT-02 | 建议级可以生成提案，但不能触发外部效果。 / Suggest-level proposals must not produce external effects. |
| PCT-03 | 影子级使用真实输入时，输出必须进入隔离位置。 / Shadow outputs from real inputs must remain isolated. |
| PCT-04 | 受限级在人数、金额或对象数上限内允许通过授权检查。 / Limited-level requests within authorized caps may pass authority checks. |
| PCT-05 | 受限级超过任一上限必须拒绝。 / Any exceeded applicable cap must refuse admission. |
| PCT-06 | 自主级命中永久人工确认清单时必须转人工。 / Autonomous-level human-required exceptions must route to human review. |
| PCT-07 | 相同 `run_id` 不得重复计数。 / The same run cannot be counted repeatedly toward one capability window; use the cohort clarification for composite runs. |
| PCT-08 | 相同 `evidence_ref` 不得重复计数。 / The same evidence reference cannot be counted repeatedly. |
| PCT-09 | 事故前证据不得直接用于事故后恢复。 / Pre-incident evidence cannot directly qualify post-incident recovery. |
| PCT-10 | 旧模型、旧策略或旧环境证据不得自动继承。 / Old model, policy or environment evidence is not inherited automatically. |
| PCT-11 | 单一任务切片不足以满足多样性要求。 / One task slice cannot satisfy a required diverse set. |
| PCT-12 | 待核验和推断事实不得作为晋级成功证据。 / Unverified or inferred facts cannot qualify as promotion successes. |
| PCT-13 | 只能从相邻等级申请晋级，除非策略明确允许跨级。 / Only adjacent promotion is allowed unless explicitly authorized by policy. |
| PCT-14 | 证据窗口锁定后新增失败，旧申请必须失效。 / A new relevant failure after batch lock invalidates the old request. |
| PCT-15 | 无权审批者批准时，凭证签发必须拒绝。 / Approval by an unauthorized reviewer cannot issue a credential. |
| PCT-16 | 审批范围小于申请范围时，只能签发审批范围。 / A narrower approval permits only that approved scope, with sealed binding and coverage recheck. |
| PCT-17 | 策略版本变化后，旧晋级申请必须重新评估。 / A policy version change requires reevaluation of old requests. |
| PCT-18 | 严重事故触发后，相关能力应立即冻结。 / A severe incident immediately freezes affected capability authority. |
| PCT-19 | 吊销通知到达后，旧凭证请求必须被执行点拒绝。 / Gateways refuse revoked credentials; authoritative fencing and propagation are tested separately. |
| PCT-20 | 降级应优先影响相关能力和范围，不应无理由全局停机。 / Downgrade targets relevant scope; wider shutdown requires supporting evidence. |
| PCT-21 | 恢复必须从新基线重新积累证据。 / Recovery collects new evidence after a new baseline. |
| PCT-22 | 审批通过但权限范围不足，必须拒绝。 / Approval with insufficient credential scope must refuse admission. |
| PCT-23 | 权限足够但预算不足，必须拒绝。 / Sufficient authority with insufficient budget must refuse admission. |
| PCT-24 | 权限和预算都足够但永久人工确认命中，必须转人工。 / Sufficient authority/budget never bypass human-required rules. |
| PCT-25 | 所有闸通过后，“允许”只代表可以进入执行，不代表业务已经成功。 / Passing every gate only permits execution; it does not prove business success. |
| PCT-26 | 探针提供已核验业务终态，可被执行流程附加到运行结果。 / Independently verified authoritative terminal enrichment may append to the outcome observation. |
| PCT-27 | 探针提供推断结果，不得触发晋级。 / Inferred completion cannot trigger promotion. |
| PCT-28 | 探针建议降级，不得直接改写权限状态。 / Probe downgrade recommendations cannot directly mutate authority. |
| PCT-29 | 补全包摘要不一致时必须拒绝接纳。 / Completion package digest mismatch must be rejected. |

| ID | Additional implementation scenario / 补充实现场景 | Expected evidence / 预期证据 |
| --- | --- | --- |
| PCX-01 | Relevant failure arrives after approval but before issuance. / 批准后签发前到达相关失败。 | Stale revision rejected, no new active credential; revised request required. / 拒绝陈旧修订，无新有效凭证，须修订申请。 |
| PCX-02 | Two issuers concurrently promote the same predecessor. / 两签发者同时晋升同一前驱。 | One committed successor; exact retry returns it, divergent second request conflicts. / 一个提交后继，精确重试返回原凭证，分歧请求冲突。 |
| PCX-03 | Freeze races with gateway dispatch; another gateway is offline. / 冻结与派发竞争且另有执行点离线。 | Serialized fence, no later dispatch; incomplete propagation explicitly remains pending. / 串行围栏后无新派发，传播不完整明确待处理。 |
| PCX-04 | Response lost after external submission; run restarted. / 提交后响应丢失且运行重启。 | Same intent/key, retained unknown exposure, independent query before retry. / 保留意图键及未知暴露，重试前独立查询。 |
| PCX-05 | Shadow subject seeks first production grant. / 影子主体申请首个生产授权。 | Approved bounded pilot, designated preproduction evidence; no unauthorized production prerequisite. / 获批受限试点与指定上线前证据，不要求越权生产前置。 |
| PCX-06 | One multi-capability run produces child/retry evidence. / 多能力运行产生子级重试证据。 | Per-capability outcomes preserved; same trial counts once per window. / 保留各能力结果，同试验每窗口只计一次。 |
| PCX-07 | Same level, wider amount/tool scope requested. / 同等级申请更大金额工具范围。 | Full target-risk evidence/approval path, no silent credential edit. / 完整目标风险证据审批路径，不静默修改凭证。 |
| PCX-08 | Verified enrichment tries to backdate authorization or alter business truth. / 核验补全试图倒填授权或改业务真值。 | Field allowlist rejects mutation; observed evidence and rejection retained. / 字段白名单拒绝变更，保存观察证据及拒绝。 |

## Delivery and Readiness / 交付与就绪

Every implementation returns bound context/request/plan, individual and merged gate receipts, dispatch/result verification, immutable outcomes, evidence windows, authority decisions, credential lifecycle and unresolved incidents/gaps. Start with isolated fixture replay, then shadow observation, then a separately authorized pilot. Production readiness additionally needs real signatures, transactional authority and budget stores, gateway coverage, durable delivery, freshness/partition policy, failure injection, tenant isolation and operational ownership. This repository update supplies the specification and asset integrity checks only. / 实现须交付绑定上下文请求计划、独立汇合闸回执、派发结果核验、不可变结果、证据窗口、权限决策凭证生命周期及未决事故缺口。先隔离样例回放，再影子观测，再另行授权试点。生产就绪还需真实签名、事务权限预算存储、网关覆盖、持久投递、新鲜度分区策略、故障注入、租户隔离及运行责任；本次仓库更新仅提供规范和资产完整性检查。
