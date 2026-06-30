# Workflow Nodes / 工作流业务节点

Use this file to split the current workflow into analyzable business nodes before mapping axes. / 使用本文档先将当前工作流拆成可分析的业务节点，再进行轴映射。

## Initial Node Set / 初始节点集

| Key | 中文 | English | Typical Capability / 常见能力 | Typical Mode / 常见模式 |
| --- | --- | --- | --- | --- |
| intake | 需求进入 | Intake | 感知 / Perception | 路由 / Routing |
| context-sensing | 上下文感知 | Context Sensing | 感知 / Perception | 链式 / Chain |
| decomposition | 问题拆解 | Decomposition | 推理 / Reasoning | 层级 / Hierarchy |
| design | 方案设计 | Design | 推理 / Reasoning | 编排 / Orchestration |
| implementation | 执行实现 | Implementation | 行动 / Action | 链式 / Chain |
| verification | 验证测试 | Verification | 反思 / Reflection | 循环 / Loop |
| delivery | 发布交付 | Delivery | 行动 / Action | 编排 / Orchestration |
| monitoring | 运行监控 | Monitoring | 感知 / Perception | 循环 / Loop |
| incident-repair | 事故修复 | Incident Repair | 推理 / Reasoning | 编排 / Orchestration |
| knowledge-memory | 知识沉淀 | Knowledge Memory | 记忆 / Memory | 链式 / Chain |
| collaboration-handoff | 协作交接 | Collaboration Handoff | 协作 / Collaboration | 路由 / Routing |
| governance-review | 治理审查 | Governance Review | 治理 / Governance | 层级 / Hierarchy |

## Node Breakdown Rules / 节点拆解规则

- Split by business responsibility, not by file or tool. / 按业务职责拆分，不按文件或工具拆分。
- Keep a node if it has a distinct input, output, owner, decision, or risk. / 若节点有独立输入、输出、负责人、决策或风险，则保留。
- Merge steps that are only mechanical details of the same responsibility. / 若步骤只是同一职责的机械细节，则合并。
- Mark missing nodes explicitly when the current workflow skips necessary feedback, memory, verification, or governance. / 当当前工作流跳过必要反馈、记忆、验证或治理时，明确标记缺失节点。

## Node Output Shape / 节点输出格式

Use this shape when reporting a diagnosis: / 诊断报告中使用此格式：

| Node / 节点 | Current Behavior / 当前行为 | Capability / 能力 | Mode / 模式 | Problem / 问题 | Change / 修改 |
| --- | --- | --- | --- | --- | --- |

## Node Evidence For Trace Insert / Trace 插入的节点证据

Before running Pattern Selection Card / 模式选型卡, collect enough node evidence to make ASSESS, ROUTE, and SELECT grounded in the current workflow. / 运行 Pattern Selection Card / 模式选型卡 前，先采集足够节点证据，确保 ASSESS、ROUTE、SELECT 基于当前工作流。

Minimum evidence / 最小证据：

- Engineering Node / 工程节点: name, responsibility, owner, and boundary. / 名称、职责、负责人和边界。
- Trigger / 触发: what starts the node. / 什么触发节点。
- Inputs and outputs / 输入与输出: required artifacts and produced decisions, changes, handoffs, or traces. / 所需产物，以及产出的决策、修改、交接或追踪。
- Current behavior / 当前行为: how the node runs today. / 节点当前如何运行。
- Failure signal / 失败信号: the symptom that motivates adjustment. / 促使调整的症状。
- Risk / 风险: quality, permission, data, production, compliance, cost, or safety impact. / 质量、权限、数据、生产、合规、成本或安全影响。
- Trace Evidence / Trace 证据: existing outcomes from `references/patterns/<capability-key>/trace.md`, if available. / 如果可用，读取 `references/patterns/<capability-key>/trace.md` 中的既有结果。
