# Progressive Commitment Probes / 渐进承诺工作流可观测性探针

Version / 版本: `0.1.0`; status / 状态: `draft`; implementation / 实现: `specification_only`; source alias / 来源别名: `PROBE_GOVERNANCE_0003`.

## Quick Navigation / 快速导航

- [Probe pipeline / 探针流程](#probe-steps)
- [Specialized checks / 专项探针](#specialized-probes)
- [Engineering clarifications / 工程口径澄清](#interpretation)
- [114 metric definitions / 114 项指标](#metric-catalog)
- [Acceptance scenarios / 验收场景](#acceptance)
- [Shared contract / 共享契约](progressive-commitment-contract.md)

## Usage, Scope and Authority / 用法、范围与权责

Audit `PATTERN_0048; CELL_GOVERNANCE_PARALLEL` using the [shared contract](progressive-commitment-contract.md) and [execution specification](progressive-commitment-execution-flow.md). Independently reconstruct task stages, scoped authority, evidence batches, promotions, incidents and gateway enforcement from authoritative sources. Read the [source map](progressive-commitment-source-map.json) for immutable snapshots and each original definition. This is a maintained specification, not a deployed probe or executable metric registry. / 按共享契约和执行规格审计现有渐进承诺模式；依据权威来源独立重建任务阶段、范围权限、证据批次、晋级、事故及执行点控制。来源映射保留不可变快照及每项原始定义。本文件是维护规范，不代表探针已部署或运行时指标已注册。

Offline mode reads authorized exports and emits findings/reports only. Interactive mode subscribes, queries sources and submits observation gaps, verified enrichment and recommendations; only the authorized controller performs governance changes. Optional probe outage does not remove local mandatory checks. / 离线模式读取获准导出并只输出发现报告；交互模式订阅查询来源，提交缺口、核验补全及建议，由有权控制器实施治理变更。可选探针故障不能取消本地必要检查。

Required inventories include capability/policy versions, credential issuance/revocation, **all independent effect and gateway admission records**, approvals, business outcomes, outcome cohorts, windows, incidents, gateway roster and human corrections. Sampling only credential-check events cannot prove check coverage or absence of bypasses. / 所需清单包含能力策略版本、凭证签发吊销、**独立的全部效果与网关准入记录**、审批业务终态、证据组窗口、事故执行点清单及人工纠正。只采样凭证检查事件无法证明检查覆盖或没有绕过。

<a id="probe-steps"></a>
## Probe Pipeline / 探针流程

| ID | Node / 节点 | Behavior and output / 行为与输出 |
| --- | --- | --- |
| P01 | Load policy and versions / 加载注册表、策略与版本 | Freeze interpretation, source authority, required steps/checks and metric definitions; missing policy permits inventory only. / 固定解释、来源权威、必需步骤检查及指标定义，策略缺失只盘点。 |
| P02 | Ingest events and artifacts / 接收事件、快照和工件 | Retain raw bytes/references, occurred/recorded times and authenticated source; replay ingestion idempotently. / 保留原文引用、发生记录时间及认证来源，幂等接收重放。 |
| P03 | Normalize with provenance / 标准化与保留原始引用 | Map types/states/versions without deleting unknown raw values; link every normalized field to its source. / 映射类型状态版本而不删除未知原值，每字段关联来源。 |
| P04 | Resolve identity and deduplicate / 身份解析、去重与链路关联 | Tenant/source/event identity, outcome cohorts and explicit references; isolate conflicts and mark fallback joins reconstructed. / 使用租户来源事件身份、结果组及显式引用，隔离冲突，备用关联标重建。 |
| P05 | Check completeness and trust / 数据完整性和可信度检查 | Compare against independent expected populations; verify source/digest/causal sequence and expose gaps before ratios. / 对照独立预期总体核验来源摘要因果序列，先暴露缺口再算比例。 |
| P06 | Rebuild task clock / 重建单次任务钟表 | Compare stages, entry gates and actual effects against the approved risk profile, not a universal fixed ladder. / 按获批风险配置核对阶段进入闸与实际效果，不套统一固定阶梯。 |
| P07 | Rebuild authority clock / 重建跨任务权限钟表 | Reconstruct per-capability grants, exact scopes, approvals, baselines, predecessor/successor and freeze states. / 重建各能力授权范围、审批基线、新旧凭证及冻结状态。 |
| P08 | Inspect execution boundary / 检查凭证与执行点边界 | Join independent actual dispatch/effect inventory to fresh credential, epoch, approval and all mandatory gate receipts. / 将独立派发效果清单关联最新凭证代次审批及全部必要闸回执。 |
| P09 | Inspect evidence and promotion / 检查证据窗口与晋级批次 | Check uniqueness, coverage, verifier independence, versions, locked digest and fresh failure watermarks at issuance. / 检查唯一覆盖、独立验证、版本、锁定摘要及签发时最新失败水位。 |
| P10 | Inspect incidents and recovery / 检查事故、降级与恢复 | Distinguish freeze, revocation, propagation, post-fence dispatch and late settlement; check new recovery baseline. / 分开发现冻结吊销传播、围栏后派发及迟后结算，核对新恢复基线。 |
| P11 | Compute metrics and trends / 计算指标和趋势 | Persist populations, operands, units, window, dimensions, definition version, quality and source refs; carry pending ages. / 保存总体算子单位窗口维度、定义版本质量来源，并保留待处理年龄。 |
| P12 | Produce gaps and recommendations / 生成缺口、补全包、发现和建议 | Mark inference and conflicting sources, obtain authoritative enrichment, assign severity/owner and propose scoped governance. / 标记推断冲突、获取权威补全、指定严重度负责人并提出范围治理建议。 |
| P13 | Deliver reports and receipts / 输出报告、告警和交互回执 | Link each conclusion to evidence; track accepted/rejected/deferred response and unresolved gaps without changing authority. / 每项结论下钻证据，跟踪采纳拒绝延期与未决缺口，不改权限。 |

<a id="specialized-probes"></a>
## Specialized Checks / 专项探针

| ID | Check / 探针 | Required verification / 必需核验 |
| --- | --- | --- |
| SP-01 | 主体与版本探针 / Subject and version | 运行上下文、凭证、策略 → 主体、模型、Agent、策略和工具版本是否一致 → 版本错配发现 / Match subject, agent, model, policy and tool versions against trusted context and credential. |
| SP-02 | 能力与范围探针 / Capability and scope | 动作请求、能力注册表、凭证 → 是否用错能力，是否超出环境、租户、工具和数据范围 → 范围越界发现 / Compare canonical request and registered capability against environment, tenant, tool and data limits. |
| SP-03 | 凭证有效性探针 / Credential validity | 凭证、吊销列表、动作时间 → 是否过期、吊销、被替代或签名无效 → 无效凭证发现 / Verify signature and authoritative active status, expiry, revocation and replacement at dispatch. |
| SP-04 | 单次任务阶梯探针 / Task ladder | 步骤事件、执行计划 → 是否跳步，是否先高风险后低风险 → 阶梯违规发现 / Reconstruct planned entries and actual effects; detect unauthorized skips or high-risk-first actions. |
| SP-05 | 组合闸探针 / Combined gate | 审批、预算、限额、幂等回执 → 真实执行前是否全部通过 → 闸门缺失或不一致 / Require matching approval, budget, containment and idempotency receipts before every real effect. |
| SP-06 | 影子隔离探针 / Shadow isolation | 工具调用、输出位置、写入日志 → 影子运行是否产生真实写入 → 隔离违规发现 / Compare tool destinations with independent production-write inventory; any shadow production effect is a violation. |
| SP-07 | 证据唯一性探针 / Evidence uniqueness | 运行结果、证据引用、摘要 → 同一结果是否重复计数 → 重复证据集合 / Find reused outcomes, trials and evidence references without merging distinct legitimate identical-content trials. |
| SP-08 | 证据新鲜度探针 / Evidence freshness | 证据时间、基线、策略 → 是否过期、早于当前签发或事故后基线 → 过期证据发现 / Compare occurrence, baseline, expiry and policy; reject stale or pre-incident scored evidence. |
| SP-09 | 证据覆盖探针 / Evidence coverage | 任务切片、风险矩阵、目标权限 → 是否覆盖目标金额、异常、并发、重试和例外 → 覆盖缺口矩阵 / Compare required target slices and risk cases with verified outcomes, including concurrency, retry and limits. |
| SP-10 | 验证者信任探针 / Verifier trust | 验证记录、验证者注册表 → 是否由受信且独立的验证者核验 → 无效验证发现 / Check registered independent verifier identity, authority, source authenticity and verification time. |
| SP-11 | 晋级批次完整性探针 / Promotion batch integrity | 晋级申请、证据窗口、摘要 → 审批前后证据是否同一批 → 批次变化发现 / Match locked request, window and approval digest and inspect fresh failures through issuance. |
| SP-12 | 审批权探针 / Approval authority | 审批记录、审批权限 → 审批者是否有权批准目标范围 → 审批权不匹配发现 / Verify the approver's live target-scope authority and approval expiry before issuance. |
| SP-13 | 凭证签发一致性探针 / Credential issuance consistency | 批准决定、新凭证 → 最终凭证是否超出批准范围 → 超签发发现 / Compare new grant to approved scope and predecessor replacement transaction. |
| SP-14 | 永久人工确认探针 / Permanent human rules | 动作规则、执行事件 → 必须人工确认的动作是否被自动执行 → 人工责任绕过发现 / Join applicable human rules and authenticated exact-action approval to actual execution. |
| SP-15 | 业务终态探针 / Business terminal | 工具结果、业务事实源 → 调用成功是否真正对应业务成功 → 机械成功误判发现 / Compare tool status with authoritative business results; preserve pending, partial and conflict states. |
| SP-16 | 事故降级探针 / Incident downgrade | 事故、冻结、吊销、执行日志 → 是否快速收权，旧凭证是否继续成功 → 收权时延和泄漏 / Measure freeze/revocation/propagation and inspect post-fence dispatch, not merely late settlement. |
| SP-17 | 恢复基线探针 / Recovery baseline | 事故前后证据、恢复申请 → 是否违规复用事故前成绩 → 恢复证据污染发现 / Detect scored pre-incident evidence and recovery outside the approved safe progression. |
| SP-18 | 数据缺口探针 / Observation gaps | 期望事件模型、实际数据 → 哪些字段、事件和来源缺失 → 数据缺口单 / Compare required records and independent source inventories; create owned field/event gaps. |
| SP-19 | 探针越权探针 / Probe overreach | 权限状态变更日志、探针身份 → 探针是否直接改写权限或业务事实 → 控制面越权发现 / Audit permission/business stores for unauthorized writes by probe identities. |
| SP-20 | 父子委派探针 / Parent-child delegation | 父凭证、子凭证、委派记录 → 子 Agent 是否获得父级没有的权限 → 委派越界发现 / Verify child scope, expiry, epoch and shared quota against the currently valid parent grant. |

## Measurement Contract / 统计契约

Each metric snapshot includes `metric_id`, `definition_version`, `population_ref`, `numerator`, `denominator` (or explicit non-ratio reason), `start/end_event_refs` for latency, unit, filters, dimensions, event-time interval, ingestion cutoff/watermark, sample count, pending count/age, source/evidence refs, generated time and quality state. Dimensions include subject, subject/model/policy/tool version, capability, level, environment, tenant, slice and risk. / 每指标快照包含标识定义版本、总体引用、分子分母或非比例说明、时延起止事件、单位过滤维度、事件时间区间、摄取截止水位、样本量、待处理数年龄、来源证据、生成时间及质量。维度含主体模型策略工具版本、能力等级环境租户切片风险。

Quality states are `verified / reconstructed / pending / inferred / conflict / missing`. A trusted exact-key join can establish a relationship but cannot upgrade an unverified underlying fact. Missing denominators or unresolved truth yield `unknown`; a known empty applicable population yields `not_applicable`, never 0% or 100%. Valid observed counts are lower bounds when inventory is incomplete. / 质量状态为已核验、重建、待核验、推断、冲突、缺失。受信精确键关联可建立关系，不能把未核验底层事实升级。分母缺失或真值未决为 `unknown`；已知无适用总体为 `not_applicable`，不可记成 0% 或 100%。清单不完整时已观测计数只是下界。

Deduplicate exact deliveries by tenant/source/event ID, retain conflicts separately, and deduplicate outcome cohorts for evidence sufficiency. DQ delivery metrics explicitly use raw deliveries where defined. Do not remove failures, unknown results, unreviewed findings or overdue open work to improve apparent performance. Latencies report completed distributions **and** open ages/completion coverage; negative or clock-incomparable durations are invalid, not clamped to zero. / 精确投递按租户来源事件标识去重，冲突另存；证据充分性按结果组去重。数据质量投递指标按定义使用原始投递总体。不得为改善表现删除失败未知、未复核发现或到期未决；时延报告完成分布**及**未完成年龄和完成覆盖率，负值或时钟不可比不能强行归零。

Threshold classes are invariants, capability-specific policies and cohort trends. Verified direct violations may trigger an independently authorized incident policy; ratios or high confidence do not grant authority. Missing observation is a gap rather than proof of a violation or safety. A configured exception must name owner, scope, reason, compensation and expiry without redefining the metric or silently waiving mandatory authority. / 阈值分不变量、能力策略与同组趋势。已核实直接违规可触发独立授权事故策略，比例及高置信度不能授权。缺观测属于缺口，不能单独证明违规或安全。配置例外需负责人范围理由补偿到期，不重定义指标或静默免除必要权限。

<a id="interpretation"></a>
## Engineering Clarifications / 工程口径澄清

The catalog below preserves source IDs and source formulas; these named clarifications define how to implement them safely. Report both source and maintained definition versions when they differ. / 下表目录保留来源标识及原始公式；以下明确修订规定实现口径，存在差异时同时报告来源与维护定义版本。

| Metrics / 指标 | Required interpretation / 必需解释 |
| --- | --- |
| PM-DQ-01–03, PM-AUTH-01–09, PM-RUN-06–07 | Denominators originate from independent run/admission/effect inventories, not only emitted successful-check logs. Count every required action/check, including failed and missing. Prove authorization-before-dispatch with causal receipts/revisions; clock uncertainty yields unknown ordering. / 分母来自独立运行准入效果清单，不限成功校验日志；包含所有必需动作检查及失败缺失，以因果回执修订证明授权先于派发，时钟不确定则顺序未知。 |
| PM-DQ-06–07 | Duplicates use excess exact deliveries divided by raw received deliveries; same-ID conflicts are separate. Out-of-order measures causal delivery disorder, while a true causal contradiction is separately flagged; timestamp inversion alone is not a permission bypass. / 重复率为精确额外投递除原始投递，同标识冲突另计；乱序衡量因果投递乱序，真实因果矛盾另报，时间倒置本身不等于越权。 |
| PM-EV-01, PM-EV-05–07, PM-EV-11, PM-EV-14 | Count unique qualified trial cohorts per capability/window. Required-set intersection determines coverage, capped at 100%; extra sources/slices never compensate for a missing required type. One multi-capability run does not become globally invalid or multiply one capability's sample size. / 每能力窗口按合格试验组计唯一；覆盖取必需集合交集，最多 100%，额外来源切片不能替代缺少类型。多能力运行不因此全局失效，也不能放大单能力样本量。 |
| PM-EV-03–04, PM-EV-08, PM-PR-12 | Match explicit target evidence policy. Approved sandbox/shadow transfer may cover specified prerequisite tests, never real-production success. Inspect tool/capability versions in addition to source-listed model/subject/policy. / 匹配明确目标证据策略，获批沙箱影子迁移仅覆盖指定前置测试，不能算真实生产成功；除原文模型主体策略外还检查工具能力版本。 |
| PM-EV-13, PM-PR-04, PM-PR-07 | Stable digest is necessary, not sufficient: check source watermarks, relevant late failures, baseline and authority revision through issuance, including the approved-but-not-yet-issued interval. / 摘要稳定必要但不充分；检查签发前来源水位、相关迟到失败、基线权限修订，包括已批准待签发阶段。 |
| PM-PR-01, PM-INC-09 | Report ordinary adjacent transitions and explicitly policy-approved exceptions separately; preserve an overall authorized-path compliance rate. Unapproved jumps always violate; approved shorter task profiles do not count as authority jumps. / 普通相邻迁移与策略明确批准例外分开，并保留总获准路径合规率；未批准跳级必违规，获批短任务配置不属于权限跳级。 |
| PM-PR-09 | Use replacement issuances as denominator; exclude correctly classified bootstrap grants with no predecessor. The predecessor must be unusable at the successor's authoritative commit, not merely eventually marked. / 分母为替换签发，排除正确标记且无前驱的初始授权；新凭证权威提交时旧凭证即不可用，不能只最终标记。 |
| PM-OUT-01–03, PM-OUT-11–14 | PM-OUT-01 is conditional success among authoritative terminal outcomes; always show terminal coverage, unknown/pending counts and exposure. Example: 80 passes, 10 fails, 10 unknown = 88.9% terminal success with 90% terminal coverage, not 88.9% overall effectiveness. Unknown business truth among tool successes remains unresolved for PM-OUT-02. Compare matched capability/version/risk/scope cohorts and follow-up durations; changed task mix is not causal proof of promotion harm. / PM-OUT-01 只是在权威终态中计算的条件成功率，必须同时报告终态覆盖、未知待决及暴露。例如 80 成功、10 失败、10 未知，终态成功率 88.9%、终态覆盖 90%，不能称整体有效率 88.9%。工具成功但业务未知在 PM-OUT-02 保持未决。比较需匹配能力版本风险范围及随访时长，任务分布变化不能证明晋级导致风险。 |
| PM-RUN-14, PM-OUT-04–07, PM-INC-05 | Only independently verified compensation/rollback counts as completed; list not-stoppable and unresolved effects separately. Report loss per comparable unit/currency and severity; do not sum people, currency, rows and downtime into one untyped scalar. / 仅独立核验的补偿回滚计完成，不可停止及未决效果另列。损失按可比单位币种严重度分别报告，不把人数金额行数停机时长无单位相加。 |
| PM-INC-03–04 | Freeze gateway membership at revocation, retain missing acknowledgments and pending age. Report post-fence **dispatch** violations separately from pre-fence effects that settle later. Incomplete propagation cannot produce a completed maximum latency. / 吊销时固定执行点清单，保留缺失确认及待处理年龄；围栏后**派发**违规与围栏前效果迟后结算分开。传播未完成不能给出已完成最大时延。 |
| PM-INC-10 | Treat the source count ratio as a repeat-incident diagnostic that may exceed 100%, not a probability. Also report a cohort recurrence fraction: closed incidents with a same-root-cause recurrence within a fixed follow-up horizon divided by eligible closed incidents with that full horizon. / 原始数量比是可超 100% 的重复事故诊断比，不是概率；另报告固定随访窗内同根因复发的已关闭事故数，除已完成该随访的合格关闭事故数。 |
| PM-OUT-09–10, PM-OBS-09–10 | Correct human routing and false alerts need independently adjudicated truth and review coverage. False-negative truth requires an independent confirmed-problem inventory, not only the probe's own findings. / 转人工正确性和误报需独立裁定真值及复核覆盖；漏报需独立已确认问题清单，不能只用探针自身发现。 |
| PM-HUM-08, PM-OBS-02–04 | Exact valid approval reuse avoids repeated nuisance, but any material action/scope/authority change requires revalidation. Gap/completion cohorts retain deferred/rejected/open counts and ages. / 有效同动作批准可复用减少打扰，动作范围权限实质变化须重验；缺口补全总体保留延期拒绝未决及年龄。 |

<a id="metric-catalog"></a>
## Metric Catalog / 指标目录

The 114 source definitions follow in their original groups and order. Source recommendations are configurable targets, not measurements or implemented gates. Every row inherits the measurement contract and applicable clarification above. / 以下保留 114 项来源定义的原始分组及顺序。原文建议是可配置目标，不是实测值或已实现闸门；每行继承统计契约及适用口径澄清。


### Data quality / 数据质量

| ID | Name / 名称 | Source formula and English rendering / 来源口径及英文释义 |
| --- | --- | --- |
| PM-DQ-01 | 必需事件完整率 / Required event completeness | 已出现的必需事件数 ÷ 应出现的必需事件数 / Observed required events / expected required events. |
| PM-DQ-02 | 必需字段完整率 / Required field completeness | 非空必需字段数 ÷ 应填必需字段数 / Nonempty required fields / expected required fields. |
| PM-DQ-03 | 链路关联成功率 / Trace association | 成功关联到完整链路的事件数 ÷ 需关联事件数 / Events linked to complete traces / events needing association. |
| PM-DQ-04 | 证据引用可解析率 / Resolvable evidence | 可解析证据引用数 ÷ 全部证据引用数 / Resolvable evidence references / all evidence references. |
| PM-DQ-05 | 权威来源覆盖率 / Authoritative source coverage | 来自权威来源的关键事实数 ÷ 关键事实总数 / Authoritative key facts / all key facts. |
| PM-DQ-06 | 事件重复率 / Duplicate delivery rate | 被判定重复的事件数 ÷ 全部事件数 / Duplicate event deliveries / all event deliveries. |
| PM-DQ-07 | 乱序事件率 / Out-of-order event rate | 不符合因果顺序的事件数 ÷ 可排序事件数 / Events outside causal order / orderable events. |
| PM-DQ-08 | 记录延迟 / Recording delay | recorded_at 减 occurred_at / Recorded time minus occurrence time. |
| PM-DQ-09 | 内容摘要一致率 / Digest consistency | 多来源内容摘要一致的记录数 ÷ 可比记录数 / Matching multi-source digests / comparable records. |
| PM-DQ-10 | 时钟偏差 / Clock deviation | 同一动作多来源时间的最大差值 / Maximum source-time difference for the same action. |
| PM-DQ-11 | 未知来源记录率 / Unknown source rate | 来源系统未知的记录数 ÷ 全部记录数 / Unknown-source records / all records. |
| PM-DQ-12 | 推断事实占比 / Inferred fact share | 推断记录数 ÷ 派生记录总数 / Inferred records / derived records. |

### Task clock / 单次任务钟表

| ID | Name / 名称 | Source formula and English rendering / 来源口径及英文释义 |
| --- | --- | --- |
| PM-RUN-01 | 阶梯步骤覆盖率 / Task stage coverage | 已完成要求步骤数 ÷ 计划要求步骤数 / Completed required stages / planned required stages. |
| PM-RUN-02 | 未授权跳步次数 / Unauthorized stage skips | 未满足进入条件却进入后续步骤的次数 / Entries without fulfilled prerequisites. |
| PM-RUN-03 | 可撤销优先合规率 / Reversible-first compliance | 首个外部效果为可撤销动作的适用运行数 ÷ 适用运行总数 / Applicable runs whose first effect is reversible / applicable runs. |
| PM-RUN-04 | 演练覆盖率 / Rehearsal coverage | 高风险真实执行前完成演练的运行数 ÷ 高风险真实执行运行数 / Rehearsed high-risk real runs / high-risk real runs. |
| PM-RUN-05 | 影子隔离违规数 / Shadow isolation violations | 影子级产生真实写入的次数 / Real writes produced at shadow level. |
| PM-RUN-06 | 组合闸回执完整率 / Combined gate receipt completeness | 真实执行前具备全部要求回执的运行数 ÷ 真实执行运行数 / Real runs with all prior gate receipts / real runs. |
| PM-RUN-07 | 外部效果先于授权次数 / Effects preceding authorization | 动作时间早于最终凭证校验或组合闸通过的次数 / Actions occurring before final credential/gate approval. |
| PM-RUN-08 | 幂等键覆盖率 / Idempotency key coverage | 带有效幂等键的可重试写操作数 ÷ 可重试写操作总数 / Retryable writes with valid keys / retryable writes. |
| PM-RUN-09 | 重复外部效果次数 / Duplicate external effects | 同一业务意图产生多次不可接受外部效果的次数 / Unacceptable repeated effects for the same business intent. |
| PM-RUN-10 | 受限范围使用率 / Limited scope utilization | 实际使用量 ÷ 凭证允许量 / Actual usage / credential allowance. |
| PM-RUN-11 | 超限请求拦截率 / Over-limit interception | 被成功阻断的超限请求数 ÷ 全部超限请求数 / Blocked over-limit requests / all over-limit requests. |
| PM-RUN-12 | 阶梯退回率 / Stage fallback rate | 因检查失败退回低风险步骤的运行数 ÷ 适用运行数 / Applicable runs returning to lower-risk stages after failed checks / applicable runs. |
| PM-RUN-13 | 组合闸等待时长 / Combined gate wait | 真实执行请求到全部回执齐备的时间 / Time from real-execution request to all required receipts. |
| PM-RUN-14 | 部分成功补偿率 / Partial-success compensation | 已完成补偿的部分成功运行数 ÷ 需要补偿的部分成功运行数 / Verified compensated partial runs / partial runs requiring compensation. |

### Credentials and execution / 凭证与执行点

| ID | Name / 名称 | Source formula and English rendering / 来源口径及英文释义 |
| --- | --- | --- |
| PM-AUTH-01 | 真实执行凭证检查覆盖率 / Effect credential check coverage | 执行点完成凭证检查的真实动作数 ÷ 真实动作总数 / Real actions checked at execution boundary / all real actions. |
| PM-AUTH-02 | 无凭证执行次数 / Credential-free executions | 没有凭证却产生外部效果的次数 / Effects produced without a credential. |
| PM-AUTH-03 | 无效凭证拦截率 / Invalid credential interception | 被阻断的无效凭证请求数 ÷ 无效凭证请求总数 / Blocked invalid-credential requests / invalid-credential requests. |
| PM-AUTH-04 | 吊销凭证拒绝率 / Revoked credential refusal | 被拒绝的吊销凭证请求数 ÷ 吊销凭证请求总数 / Refused revoked-credential requests / revoked-credential requests. |
| PM-AUTH-05 | 过期凭证拒绝率 / Expired credential refusal | 被拒绝的过期凭证请求数 ÷ 过期凭证请求总数 / Refused expired-credential requests / expired-credential requests. |
| PM-AUTH-06 | 被替代凭证拒绝率 / Superseded credential refusal | 被拒绝的旧版凭证请求数 ÷ 旧版凭证请求总数 / Refused superseded-credential requests / superseded-credential requests. |
| PM-AUTH-07 | 范围错配拦截率 / Scope mismatch interception | 被阻断的能力、环境、租户或工具错配请求数 ÷ 全部错配请求数 / Blocked capability/environment/tenant/tool mismatches / all mismatches. |
| PM-AUTH-08 | 未授权外部效果次数 / Unauthorized external effects | 未满足权限却成功产生外部效果的次数 / Effects successfully produced without sufficient authority. |
| PM-AUTH-09 | 跨租户越权次数 / Cross-tenant violations | 主体在未授权租户产生外部效果的次数 / Effects in unauthorized tenants. |
| PM-AUTH-10 | 跨能力证据借用次数 / Cross-capability evidence borrowing | 使用其他能力成绩支持当前能力晋级的次数 / Other-capability results used to support promotion. |
| PM-AUTH-11 | 永久人工确认绕过尝试数 / Human-rule bypass attempts | 自动流程尝试执行永久人工确认动作的次数 / Automated attempts at human-required actions. |
| PM-AUTH-12 | 永久人工确认绕过成功数 / Successful human-rule bypasses | 上述动作实际自动完成的次数 / Human-required actions actually completed automatically. |
| PM-AUTH-13 | 审批门关联完整率 / Approval receipt coverage | 需审批动作中可解析审批回执的动作数 ÷ 需审批动作总数 / Approval-required actions with resolvable approval / approval-required actions. |
| PM-AUTH-14 | 爆炸半径回执完整率 / Containment receipt coverage | 需限额动作中可解析限额回执的动作数 ÷ 需限额动作总数 / Limit-required actions with resolvable containment receipts / limit-required actions. |
| PM-AUTH-15 | 父子委派越界次数 / Delegation scope violations | 子权限超出父权限的次数 / Child grants exceeding parent authority. |

### Evidence windows / 证据窗口

| ID | Name / 名称 | Source formula and English rendering / 来源口径及英文释义 |
| --- | --- | --- |
| PM-EV-01 | 证据唯一率 / Evidence uniqueness | 唯一运行和唯一引用的证据数 ÷ 纳入窗口证据数 / Evidence with unique runs and references / evidence in window. |
| PM-EV-02 | 证据新鲜率 / Evidence freshness | 未超过有效期的证据数 ÷ 纳入窗口证据数 / Unexpired evidence / evidence in window. |
| PM-EV-03 | 版本匹配率 / Version match | 与当前主体、模型和策略版本一致的证据数 ÷ 纳入窗口证据数 / Evidence matching current subject/model/policy / evidence in window. |
| PM-EV-04 | 环境匹配率 / Environment match | 与目标环境一致或被策略允许迁移的证据数 ÷ 纳入窗口证据数 / Target-matched or approved-transfer evidence / evidence in window. |
| PM-EV-05 | 任务切片覆盖率 / Task slice coverage | 已覆盖必需任务切片数 ÷ 必需任务切片总数 / Covered required slices / required slices. |
| PM-EV-06 | 风险场景覆盖率 / Risk scenario coverage | 已覆盖必需风险场景数 ÷ 必需风险场景总数 / Covered required risk scenarios / required risk scenarios. |
| PM-EV-07 | 受信验证覆盖率 / Trusted verification coverage | 经受信验证者核验的证据数 ÷ 纳入窗口证据数 / Trusted-verified evidence / evidence in window. |
| PM-EV-08 | 权威业务终态覆盖率 / Authoritative terminal coverage | 有权威业务终态的真实执行证据数 ÷ 真实执行证据数 / Real-effect evidence with authoritative terminal / real-effect evidence. |
| PM-EV-09 | 阻断性失败未关闭数 / Open blocking failures | 窗口内未关闭 blocker 记录数 / Unclosed blocker records in window. |
| PM-EV-10 | 证据拒绝率 / Evidence rejection | 因重复、过期、失配或未核验被拒绝的证据数 ÷ 提交证据数 / Duplicate/stale/mismatched/unverified rejections / submitted evidence. |
| PM-EV-11 | 单一切片集中度 / Largest slice concentration | 最大单一切片证据数 ÷ 窗口证据总数 / Evidence in largest single slice / window evidence. |
| PM-EV-12 | 事故前证据复用数 / Pre-incident evidence reuse | 事故后恢复申请中使用事故前证据的条数 / Pre-incident evidence reused for recovery. |
| PM-EV-13 | 证据窗口稳定率 / Review window stability | 评审期间摘要未变化的申请数 ÷ 进入评审的申请数 / Applications whose reviewed digest stays stable / reviewed applications. |
| PM-EV-14 | 证据来源多样性 / Evidence source diversity | 已覆盖独立来源类型数 ÷ 策略要求来源类型数 / Covered independent source types / required source types. |
| PM-EV-15 | 证据补全依赖率 / Enrichment dependency | 依赖探针补全后才完整的证据数 ÷ 窗口证据数 / Evidence complete only after probe enrichment / window evidence. |

### Promotion and issuance / 晋级与签发

| ID | Name / 名称 | Source formula and English rendering / 来源口径及英文释义 |
| --- | --- | --- |
| PM-PR-01 | 相邻晋级合规率 / Adjacent promotion compliance | 相邻等级晋级数 ÷ 全部晋级数 / Adjacent-level promotions / all promotions. |
| PM-PR-02 | 晋级申请证据锁定率 / Promotion batch lock coverage | 带证据批次摘要的申请数 ÷ 晋级申请总数 / Requests with a locked evidence digest / all promotion requests. |
| PM-PR-03 | 审批权匹配率 / Approver scope match | 审批者权限覆盖目标范围的批准数 ÷ 批准总数 / Approvals whose approver covers target scope / approvals. |
| PM-PR-04 | 批准后摘要一致率 / Post-approval digest match | 批准时摘要与签发时摘要一致的凭证数 ÷ 新签发凭证数 / Issued credentials with matching approval/issuance digest / new credentials. |
| PM-PR-05 | 凭证与批准范围一致率 / Issued scope containment | 新凭证范围不超过批准范围的凭证数 ÷ 新签发凭证数 / Credentials within approved scope / new credentials. |
| PM-PR-06 | 晋级决策时长 / Promotion decision time | 申请进入评审到批准、拒绝或失效的时间 / Review entry to approval, refusal or invalidation. |
| PM-PR-07 | 等待期失败失效率 / Failure invalidation coverage | 等待评审期间新增失败后正确失效的申请数 ÷ 应失效申请数 / Correctly invalidated applications after new review-period failures / applications needing invalidation. |
| PM-PR-08 | 新凭证签发时长 / Credential issuance time | 批准到新凭证生效的时间 / Approval to new credential activation. |
| PM-PR-09 | 旧凭证替代完整率 / Predecessor replacement coverage | 新凭证生效后旧凭证被标记替代的次数 ÷ 新凭证数 / Successor activations with predecessor superseded / new credentials. |
| PM-PR-10 | 晋级后强化观测覆盖率 / Enhanced post-promotion observation | 晋级后观察期内被强化观测的主体能力数 ÷ 晋级主体能力数 / Promoted subject-capabilities observed during watch / promoted subject-capabilities. |
| PM-PR-11 | 晋级撤回率 / Promotion reversal rate | 晋级后在观察期内降回原等级的次数 ÷ 晋级次数 / Promotions downgraded during watch / promotions. |
| PM-PR-12 | 目标范围验证覆盖率 / Target scope verification | 晋级前已验证目标金额、对象、租户和工具范围的申请数 ÷ 晋级申请数 / Requests with target amount/object/tenant/tool verified / promotion requests. |

### Business outcomes / 业务结果

| ID | Name / 名称 | Source formula and English rendering / 来源口径及英文释义 |
| --- | --- | --- |
| PM-OUT-01 | 业务成功率 / Conditional business success | 满足业务验收条件的运行数 ÷ 已有权威终态的运行数 / Business-accepted runs / runs with authoritative terminals. |
| PM-OUT-02 | 机械成功误判率 / Mechanical success misclassification | 工具成功但业务失败的运行数 ÷ 工具报告成功的运行数 / Tool-success but business-failed runs / tool-success runs. |
| PM-OUT-03 | 人工纠正率 / Human correction rate | 被人工修改或改判的运行数 ÷ 已完成运行数 / Human-corrected or rejudged runs / completed runs. |
| PM-OUT-04 | 回滚率 / Rollback rate | 发生回滚的真实执行数 ÷ 真实执行数 / Real executions with rollback / real executions. |
| PM-OUT-05 | 补偿率 / Compensation completion | 需要补偿且完成补偿的运行数 ÷ 需要补偿的运行数 / Required and verified completed compensation / required compensation. |
| PM-OUT-06 | 事故率 / Incident rate | 事故运行数 ÷ 真实执行运行数 / Incident runs / real-execution runs. |
| PM-OUT-07 | 严重度加权损失 / Severity-weighted loss | 各事故影响量乘严重度权重之和 / Sum of comparable incident impact times severity weight. |
| PM-OUT-08 | 影子与真实结果差异率 / Shadow versus real disagreement | 影子输出与权威结果不一致项数 ÷ 可比较项数 / Disagreeing items / comparable items. |
| PM-OUT-09 | 例外转人工准确率 / Required human routing accuracy | 应转人工且成功转人工的任务数 ÷ 应转人工任务数 / Correctly routed human-required tasks / human-required tasks. |
| PM-OUT-10 | 错误转人工率 / Unnecessary human routing | 无需转人工却被转人工的任务数 ÷ 可自主任务数 / Unnecessarily human-routed tasks / autonomous-eligible tasks. |
| PM-OUT-11 | 晋级后成功率变化 / Post-promotion success change | 晋级后业务成功率减晋级前基线 / Post-promotion success minus comparable baseline. |
| PM-OUT-12 | 晋级后事故率变化 / Post-promotion incident change | 晋级后事故率减晋级前基线 / Post-promotion incident rate minus comparable baseline. |
| PM-OUT-13 | 晋级后人工纠正率变化 / Post-promotion correction change | 晋级后纠正率减晋级前基线 / Post-promotion correction rate minus comparable baseline. |
| PM-OUT-14 | 范围扩大边际风险 / Expansion marginal risk | 新增范围内事故或纠正数 ÷ 新增范围任务数 / New-scope tasks with incidents or corrections / new-scope tasks. |

### Incident and recovery / 事故与恢复

| ID | Name / 名称 | Source formula and English rendering / 来源口径及英文释义 |
| --- | --- | --- |
| PM-INC-01 | 事故发现到冻结时长 / Detection-to-freeze time | 冻结时间减事故发现时间 / Freeze time minus incident detection time. |
| PM-INC-02 | 冻结到吊销时长 / Freeze-to-revocation time | 凭证吊销时间减冻结时间 / Revocation time minus freeze time. |
| PM-INC-03 | 吊销传播时长 / Revocation propagation time | 最后一个执行点确认吊销时间减吊销时间 / Last required gateway acknowledgment minus revocation time. |
| PM-INC-04 | 吊销后成功执行数 / Post-revocation successful execution | 吊销生效后旧凭证仍成功的动作数 / Old-credential actions successful after effective revocation. |
| PM-INC-05 | 在途动作停止率 / In-flight containment | 已停止、回滚或补偿的在途动作数 ÷ 事故时在途动作总数 / Stopped, rolled-back or compensated in-flight actions / in-flight actions at incident. |
| PM-INC-06 | 影响范围确定时长 / Impact discovery time | 完成影响对象清单时间减事故确认时间 / Complete affected-object inventory minus confirmation time. |
| PM-INC-07 | 新基线建立时长 / New baseline setup time | 新证据基线时间减事故确认时间 / New baseline time minus incident confirmation. |
| PM-INC-08 | 事故前证据违规复用数 / Improper pre-incident scoring | 恢复晋级中被计分的事故前证据数 / Pre-incident evidence counted toward recovery. |
| PM-INC-09 | 恢复逐级合规率 / Staged recovery compliance | 按策略逐级恢复的恢复流程数 ÷ 全部恢复流程数 / Policy-compliant staged recovery flows / all recovery flows. |
| PM-INC-10 | 重复事故率 / Repeat incident ratio | 同类根因再次发生的事故数 ÷ 已关闭同类事故数 / Repeated same-root-cause incidents / closed same-type incidents. |
| PM-INC-11 | 精准收权率 / Scoped revocation precision | 仅冻结相关能力和范围的适用事故数 ÷ 可精准收权事故数 / Appropriately narrowly frozen incidents / incidents eligible for narrow freeze. |
| PM-INC-12 | 事故治理记录完整率 / Incident record completeness | 具备发现、确认、冻结、吊销、影响和恢复记录的事故数 ÷ 事故总数 / Incidents with discovery, confirmation, freeze, revocation, impact and recovery records / incidents. |

### Human responsibility / 人工责任

| ID | Name / 名称 | Source formula and English rendering / 来源口径及英文释义 |
| --- | --- | --- |
| PM-HUM-01 | 永久人工确认规则覆盖率 / Human-required rule coverage | 已登记永久人工确认规则的高风险能力数 ÷ 应登记能力数 / High-risk capabilities with required human rules / capabilities needing rules. |
| PM-HUM-02 | 人工确认请求完整率 / Human review request completeness | 带对象、差异、影响和证据的人工请求数 ÷ 人工请求总数 / Requests with objects, diff, impact and evidence / human review requests. |
| PM-HUM-03 | 审批理由完整率 / Decision reason completeness | 有明确批准或拒绝理由的审批数 ÷ 审批总数 / Reasoned approval or refusal decisions / all decisions. |
| PM-HUM-04 | 无权审批尝试数 / Unauthorized approval attempts | 审批者无权覆盖目标范围的尝试次数 / Attempts whose approver lacks target-scope authority. |
| PM-HUM-05 | 例外积压时长 / Exception queue time | 例外进入人工队列到处理完成的时间 / Manual-queue entry to completed disposition. |
| PM-HUM-06 | 人工改判证据回流率 / Correction evidence feedback | 人工改判被记录进证据窗口的次数 ÷ 人工改判总数 / Human corrections entered in evidence windows / human corrections. |
| PM-HUM-07 | 人工责任绕过成功数 / Human responsibility bypasses | 本应由人决定却自动完成的次数 / Human-owned decisions completed automatically. |
| PM-HUM-08 | 人工确认重复打扰率 / Repeated human confirmation | 同一事实和同一权限下重复请求相同确认的次数 ÷ 人工确认请求数 / Repeated identical confirmations under unchanged facts/authority / human requests. |

### Probe interaction / 探针交互

| ID | Name / 名称 | Source formula and English rendering / 来源口径及英文释义 |
| --- | --- | --- |
| PM-OBS-01 | 数据缺口发生率 / Observation gap incidence | 发现数据缺口的运行数 ÷ 运行总数 / Runs with observation gaps / all runs. |
| PM-OBS-02 | 数据缺口关闭率 / Observation gap closure | 已关闭缺口数 ÷ 已创建缺口数 / Closed gaps / created gaps. |
| PM-OBS-03 | 缺口关闭时长 / Gap closure time | 缺口关闭时间减创建时间 / Closure time minus creation time. |
| PM-OBS-04 | 补全包接纳率 / Enrichment acceptance | 被执行流程接纳的补全包数 ÷ 提交补全包数 / Accepted completion packages / submitted packages. |
| PM-OBS-05 | 已核验补全占比 / Verified enrichment share | 已核验补全字段数 ÷ 全部补全字段数 / Verified enriched fields / all enriched fields. |
| PM-OBS-06 | 推断误用次数 / Inference misuse | 推断事实被用于正式晋级或授权的次数 / Inferred facts used for formal promotion or authorization. |
| PM-OBS-07 | 探针直接改权次数 / Probe authority mutations | 探针身份直接修改权限状态的次数 / Direct permission-state mutations by probe identity. |
| PM-OBS-08 | 建议转正式治理率 / Recommendation governance conversion | 被转为正式评审、事故或策略变更的高优先级建议数 ÷ 高优先级建议数 / High-priority recommendations entering formal governance / high-priority recommendations. |
| PM-OBS-09 | 发现误报率 / Finding false-positive rate | 经核查为误报的发现数 ÷ 已核查发现数 / Adjudicated false positives / reviewed findings. |
| PM-OBS-10 | 发现漏报率 / Finding false-negative rate | 事后确认但探针未发现的问题数 ÷ 已确认问题总数 / Independently confirmed missed problems / confirmed problems. |
| PM-OBS-11 | 报告可下钻率 / Report drill-down coverage | 可从结论定位到原始证据的结论数 ÷ 报告结论总数 / Conclusions traceable to raw evidence / report conclusions. |
| PM-OBS-12 | 探针运行成功率 / Probe run success | 成功完成预期探针节点的运行数 ÷ 探针运行总数 / Runs completing expected probe nodes / probe runs. |

## Findings, Enrichment and Operations / 发现、补全与运行

Use the shared contract's gap/completion/finding/recommendation/receipt objects. Prefer authoritative business outcomes for success, the issuer/revocation ledger for authority, and gateway facts for actual enforcement; authority-source conflicts stay visible and exclude affected evidence from promotion. Reconstructed links and inferred facts never overwrite source truth. A later legitimate receipt may resolve an observation gap but cannot retroactively authorize an effect. / 使用共享契约的缺口补全发现建议回执对象。成功优先权威业务终态，权限优先签发吊销账本，实际控制优先网关事实；权威冲突持续可见并排除相关晋级证据。重建推断不能覆盖真值；迟到合法回执可补观测缺口，但不能追溯授权效果。

Critical findings require confirmed unauthorized effects, shadow production writes, cross-tenant effects, post-fence dispatch, human-rule bypass, changed-batch issuance, over-issued scope, unauthorized approval, probe mutation or child-scope escalation. Suspected boundary failures are high-priority investigations; missing data is reported with uncertainty. Group alerts by tenant/capability/incident and rule, preserve severity and all evidence, and use open/acknowledged/resolved/false-positive lifecycle with an owner and closure proof. / 确认的未授权效果、影子生产写、跨租户、围栏后派发、人工规则绕过、变批签发、超范围签发、无权批准、探针改权或子级越权产生严重发现。疑似边界失效进入高优调查，缺数据报告不确定性。按租户能力事故规则合并告警、保留严重度及全部证据，以打开确认关闭误报生命周期追踪负责人和关闭依据。

Probe depth progresses from existence → consistency → governance reconstruction → trends. Claim full auditability only with reconstruction of why authority was valid and how changes reached every execution boundary; passing existence checks is insufficient. Reports show source scope/unavailable systems, quality, both clocks, authority map, evidence coverage, promotion/incident timelines, metric operands, unresolved gaps and recommendations with drill-down. / 探针深度从存在性、一致性、治理重建到趋势；只有能重建权限成立原因及变更如何到达各执行边界，才可声称完整可审计性，仅存在性通过不足。报告包含来源范围缺失系统、质量、两只钟表、权限地图、证据覆盖、晋级事故时间线、指标算子、未决缺口及可下钻建议。

Version probe/rule/metric/source adapters; monitor ingestion lag and backlog; replay with preserved event identity after outages; isolate raw records from derived views; minimize sensitive payloads and honor versioned retention/incident holds. Rule execution failure means `not_run`, never “no problems.” Probe identities have no write access to authority or business stores. / 对探针规则指标来源适配器版本化；监测摄取滞后积压，故障后保留事件身份重放；分离原文与派生视图，最小化敏感载荷并遵守保留与事故保全。规则失败为未运行，不能报告无问题；探针身份没有权限业务库写权。

<a id="acceptance"></a>
## Acceptance Scenarios / 验收场景

These 31 source-derived cases are unexecuted expectations. The documentation validator checks source identity and coverage only; an actual probe needs independent fixtures, expected findings/metrics and runtime results. / 以下 31 项来源用例为未执行预期。文档校验器只检查来源身份及覆盖，真实探针须独立样例、预期发现指标及运行结果。

| ID | Source scenario and expected behavior / 来源场景与预期行为 |
| --- | --- |
| PCQ-01 | 缺少 `run_id` 的事件应被保留并生成缺口，而不是丢弃。 / Keep events missing run identity and create a gap instead of dropping them. |
| PCQ-02 | 相同 `event_id` 重复到达不得重复计数。 / Exact duplicate event delivery must not double-count. |
| PCQ-03 | 相同证据摘要使用不同标识时，应进入疑似重复集合。 / Different IDs with identical evidence content enter a suspected-duplicate set. |
| PCQ-04 | 多来源时间冲突时，应保留原始时间并标记时钟问题。 / Keep source timestamps and flag clock conflicts. |
| PCQ-05 | 分母未知时，不得输出伪精确百分比。 / Unknown denominator must not produce a precise percentage. |
| PCQ-06 | 真实执行先于凭证校验时，必须产生严重发现。 / Proven execution before credential validation creates a critical finding. |
| PCQ-07 | 影子级出现生产写入时，必须产生严重发现。 / Shadow production writes create a critical finding. |
| PCQ-08 | 跳过要求的演练或小范围步骤时，必须记录跳步。 / Missing required rehearsal or limited stage creates a skip finding. |
| PCQ-09 | 超限请求被正确阻断时，应计入超限拦截率。 / Correctly blocked over-limit requests enter the interception numerator. |
| PCQ-10 | 工具成功但业务失败时，应计入机械成功误判率。 / Tool success with business failure enters mechanical-success misclassification. |
| PCQ-11 | 相同 `run_id` 不得重复计入。 / Do not count one run repeatedly toward a capability evidence window. |
| PCQ-12 | 相同 `evidence_ref` 不得重复计入。 / Do not count the same evidence reference repeatedly. |
| PCQ-13 | 旧版本证据进入新版本窗口时，应标记版本失配。 / Old-version evidence in a new window produces a mismatch finding. |
| PCQ-14 | 单一简单切片占比过高时，应生成覆盖不足发现。 / Excess single-slice concentration produces a coverage finding. |
| PCQ-15 | 未经受信验证的证据不得被标记为合格晋级证据。 / Untrusted or unverified evidence cannot be marked qualified for promotion. |
| PCQ-16 | 评审期间新增失败时，探针应判断旧申请失效。 / A relevant new failure during review invalidates the old request. |
| PCQ-17 | 审批者权限不足时，应产生审批权不匹配发现。 / Insufficient approver authority produces a scope mismatch finding. |
| PCQ-18 | 新凭证范围超过批准范围时，应产生超签发发现。 / Credential scope exceeding approval produces an over-issuance finding. |
| PCQ-19 | 批准后证据摘要变化时，应产生批次不一致发现。 / Changed evidence digest after approval produces a batch mismatch finding. |
| PCQ-20 | 新凭证生效后旧凭证仍有效时，应产生双凭证窗口发现。 / A usable predecessor after successor activation produces a dual-grant finding. |
| PCQ-21 | 跨级晋升没有策略依据时，应产生晋级路径违规发现。 / Unapproved cross-level promotion produces a path violation finding. |
| PCQ-22 | 严重事故后没有冻结事件，应产生高优先级发现。 / Missing freeze after a severe incident creates a high-priority finding. |
| PCQ-23 | 吊销后旧凭证成功执行，应产生严重发现。 / Post-fence dispatch with an old credential produces a critical finding; exclude pre-fence late settlements. |
| PCQ-24 | 事故前证据被用于恢复晋级，应产生恢复证据污染发现。 / Pre-incident evidence counted for restoration produces contamination findings. |
| PCQ-25 | 直接从观察级恢复到自主级，应产生恢复路径违规发现。 / Direct observe-to-autonomous recovery violates the normal recovery path; review any explicit policy exception. |
| PCQ-26 | 事故只影响单一能力却无理由全局停机，应标记为可能过度收权，供治理评估。 / Unjustified global freeze for a narrowly scoped incident is flagged for governance review. |
| PCQ-27 | 探针写入权限状态应被检测并阻断。 / Control-plane access denies probe writes; independent audit detects attempts or actual bypasses. |
| PCQ-28 | 推断事实进入正式晋级证据应被检测。 / Inferred facts used in formal promotion are detected. |
| PCQ-29 | 补全包来源摘要不一致时，执行流程应拒绝，探针记录拒绝原因。 / The execution service rejects mismatched source digests and the probe retains the reason. |
| PCQ-30 | 探针不可用时，执行流程仍能执行正式权限控制。 / Probe outage leaves formal local authority controls operating. |
| PCQ-31 | 执行流程恢复后，探针可以补采并重建中断时间线。 / After execution recovery, replay missing data and reconstruct the interrupted timeline. |

Additional fixtures must cover unknown denominators, duplicate delivery versus cohort reuse, identical content from distinct trials, delayed failure after approval, missing gateway acknowledgment, clock skew, pre-freeze dispatch settling after freeze, and an enrichment attempt to mutate authority. / 补充样例必须覆盖未知分母、重复投递与证据组复用、不同试验相同内容、批准后迟到失败、执行点缺确认、时钟漂移、冻结前派发冻结后结算及补全越权修改。
