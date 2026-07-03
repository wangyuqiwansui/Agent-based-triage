# Harness Source Analysis / Harness 源码分析

Use this file when analyzing an Agent Harness source repository, runtime, tool system, memory system, sandbox, permission layer, subagent system, or event log. / 当分析 Agent Harness 源码仓库、runtime、工具系统、记忆系统、沙箱、权限层、子 Agent 系统或事件日志时使用本文档。

## Goal / 目标

Compile source code into a Harness engineering map with main loop, core components, cognition classification, topology mapping, noise filtering, patterns, evidence, and governance gaps. / 将源码编译为 Harness 工程地图，包括主循环、核心组件、认知归类、拓扑映射、噪声过滤、模式、证据和治理缺口。

## Detect / 找主循环

Locate the loop that connects user input, session state, context construction, model calls, response parsing, tool or subagent dispatch, runtime execution, observation construction, event logging, and next turn state. / 定位连接用户输入、会话状态、上下文构造、模型调用、响应解析、工具或子 Agent 分发、runtime 执行、观察构造、事件记录和下一轮状态的循环。

Typical shape / 典型形态:

```text
User Input
  -> Session
  -> Context Builder
  -> LLM Call
  -> Response Parser
  -> Tool / Agent Dispatcher
  -> Runtime / Sandbox
  -> Observation Builder
  -> Event Log / State Store
  -> Next Turn
```

Search hints / 搜索线索:

```bash
rg "tool_call|function_call|tool_use|ToolCall|Action|Observation" .
rg "while|loop|step|run|turn|conversation|session" .
rg "messages|context|history|state|event" .
rg "permission|approval|policy|sandbox|runtime|executor" .
```

Language-specific hints / 语言线索:

- Python: `async def run`, `while True`, `yield`, `stream`, `agent.step`, `tool_calls`, `BaseAgent`, `AgentState`. / Python：关注这些入口和状态对象。
- TypeScript or JavaScript: `async function`, `for await`, `session`, `message`, `toolCall`, `dispatch`, `execute`, `Provider`, `Permission`. / TypeScript 或 JavaScript：关注这些入口和调度对象。
- Rust: `async fn`, `loop {`, `match`, `enum`, `trait`, `tool`, `exec`, `sandbox`, `policy`, `Session`, `Event`. / Rust：关注这些控制流和协议对象。

## Classify / 组件归类

Classify components by what engineering resource they change, not by filename alone. / 按组件改变的工程资源归类，而不是只看文件名。

| Component / 组件 | Primary Cognition / 主认知 | Common Names / 常见命名 |
| --- | --- | --- |
| Context Builder / 上下文构造器 | Perception / 感知 | context, prompt, message, repo_map, lsp |
| Memory Store / 记忆存储 | Memory / 记忆 | memory, history, event_store, state, snapshot |
| Planner or Router / 规划器或路由器 | Reasoning / 推理 | planner, router, task, reasoning, controller |
| Tool Dispatcher / 工具分发器 | Action / 行动 | tools, actions, executor, runtime, command |
| Evaluator or Retry / 评估器或重试器 | Reflection / 反思 | eval, retry, fix, critic, reflect, test_loop |
| Subagent or Handoff / 子 Agent 或交接 | Collaboration / 协作 | subagent, delegate, handoff, worker, team |
| Permission or Sandbox / 权限或沙箱 | Governance / 治理 | permission, policy, approval, sandbox, audit |

## Filter / 噪声过滤

First-round reading should focus on files that change Agent decisions, context, state, action, permissions, feedback, audit, or handoff. / 第一轮阅读应聚焦会改变 Agent 决策、上下文、状态、行动、权限、反馈、审计或交接的文件。

Read first / 第一轮优先读取:

- Main loop / 主循环
- Context assembly / 上下文装配
- Model call and response parsing / 模型调用与响应解析
- Tool registry and dispatcher / 工具注册表与分发器
- Tool result writeback / 工具结果回填
- State, memory, event log, or snapshot / 状态、记忆、事件日志或快照
- Permission, approval, policy, sandbox, runtime / 权限、审批、策略、沙箱、runtime
- Failure retry and evaluation loops / 失败重试与评估循环
- Subagent dispatch and handoff contracts / 子 Agent 分发与交接契约
- Tests that expose design boundaries / 暴露设计边界的测试

Defer unless needed / 除非必要先跳过:

- UI layout / UI 布局
- CLI flag details / CLI 参数细节
- Error copy / 错误文案
- Thin provider SDK wrappers / provider SDK 薄封装
- Type aliases without behavior / 无行为的类型别名
- Serialization boilerplate / 序列化样板
- Platform compatibility branches / 平台兼容分支
- Fixture data / 测试 fixture 数据
- Telemetry adapters / telemetry 适配
- Installer or documentation site config / 安装脚本或文档站点配置

Noise test / 噪声判断: Would this file change what the Agent can see, remember, decide, do, retry, audit, or govern? If no, mark support or boilerplate. / 这个文件是否会改变 Agent 可见、可记、可判断、可行动、可重试、可审计或可治理的内容？如果不会，标为 support 或 boilerplate。

## Map / 落矩阵

Map each retained component to one primary cognition and one primary topology, then add secondary references only when they change the diagnosis. / 将每个保留组件映射到一个主认知和一个主拓扑；只有当副认知或副拓扑会改变诊断时才补充。

| Source Area / 源码区域 | Cognition / 认知 | Topology / 拓扑 | Coordinate / 坐标 | Candidate Pattern / 候选模式 |
| --- | --- | --- | --- | --- |
| context_builder.py | Perception / 感知 | Chain / 链式 | `COG_PERCEPTION__TOP_CHAIN` | Context Assembly / 上下文装配 |
| repo_map.py | Perception / 感知 | Routing / 路由 | `COG_PERCEPTION__TOP_ROUTING` | Repository Map Sensing / 仓库地图感知 |
| tool_dispatcher.ts | Action / 行动 | Routing / 路由 | `COG_ACTION__TOP_ROUTING` | Tool Dispatch / 工具分派 |
| sandbox_manager.rs | Governance / 治理 | Orchestration / 编排 | `COG_GOVERNANCE__TOP_ORCHESTRATION` | Sandbox Isolation / 沙箱隔离 |
| event_store.py | Memory / 记忆 | Chain / 链式 | `COG_MEMORY__TOP_CHAIN` | Event Ledger / 事件账本 |
| retry_loop.py | Reflection / 反思 | Loop / 循环 | `COG_REFLECTION__TOP_LOOP` | Failure Repair Loop / 失败修复循环 |
| subagent_router.ts | Collaboration / 协作 | Hierarchy / 层级 | `COG_COLLABORATION__TOP_HIERARCHY` | Subagent Delegation / 子 Agent 委派 |

## Verify / 证据验证

Evidence priority / 证据优先级:

```text
source code > tests > official docs > config > runtime logs > README
源码 > 测试 > 官方文档 > 配置 > 运行日志 > README
```

Use README as supporting evidence only. / README 仅作为辅助证据。

Evidence table / 证据表:

| claim_id | Claim / 架构判断 | Evidence Type / 证据类型 | Path / 路径 | Line or Symbol / 行号或符号 | Confidence / 可信度 | Notes / 说明 |
| --- | --- | --- | --- | --- | --- | --- |

## Harness Report Shape / Harness 报告结构

Include these sections when rendering the analysis. / 输出分析时包含以下章节。

- Scope and input references / 分析范围与输入引用
- Main loop Detect / 主循环 Detect
- Component Classify / 组件 Classify
- Noise Filter / 噪声 Filter
- Matrix Map / 矩阵 Map
- Engineering Patterns / 工程模式
- Skillization Recommendations / Skill 化建议
- Evidence Verify / 证据 Verify
- Governance Gaps / 治理缺口
- Evaluation Readiness / 评估就绪度
