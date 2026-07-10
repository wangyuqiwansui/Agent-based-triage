import importlib.util
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_skill_visualization.py"
SKILL_DIR = ROOT / "skills" / "harness-engineering-patterns"
SELECTION_CARD = SKILL_DIR / "references" / "pattern-selection-card.md"
PATTERN_DIR = SKILL_DIR / "references" / "patterns"
CAPABILITY_KEYS = {
    "perception",
    "memory",
    "reasoning",
    "action",
    "reflection",
    "collaboration",
    "governance",
}
REPRESENTATIVE_PATTERN_KEYS = {
    "perception-routing",
    "memory-chain",
    "reasoning-routing",
    "action-orchestration",
    "reflection-chain",
    "collaboration-parallel",
    "governance-routing",
    "governance-hierarchy",
}
COMPILER_REFERENCE_FILES = {
    "references/compiler-workflow.md": [
        "Engineering Analysis Compiler / 工程分析编译器",
        "Registry As Source Data / 注册表作为源数据",
        "Control Plane First / 先抓控制面",
    ],
    "references/eir-schema.md": [
        "Engineering Intermediate Representation / 工程中间表示",
        "Business Node / 业务节点",
        "Evidence Item / 证据项",
    ],
    "references/harness-source-analysis.md": [
        "Harness Source Analysis / Harness 源码分析",
        "Detect / 找主循环",
        "Classify / 组件归类",
        "Filter / 噪声过滤",
        "Map / 落矩阵",
        "Verify / 证据验证",
    ],
    "references/pattern-skill-packaging.md": [
        "Pattern And Skill Packaging / 模式与 Skill 化",
        "Pattern Extraction / 模式抽取",
        "Skillization / Skill 化",
    ],
    "references/evaluation-governance.md": [
        "Evaluation And Governance / 评估与治理",
        "Quality Evaluation / 质量评估",
        "Governance Checklist / 治理检查清单",
    ],
    "references/failure-modes.md": [
        "Failure Modes / 失败模式",
        "FAIL_0001",
        "FAIL_0010",
    ],
}


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_skill_visualization", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillVisualizationGeneratorTest(unittest.TestCase):
    def test_loads_axes_matrix_and_pattern_counts(self):
        generator = load_generator()

        data = generator.load_skill_data(SKILL_DIR)

        self.assertEqual(len(data["vertical_axes"]), 7)
        self.assertEqual(len(data["horizontal_axes"]), 6)
        self.assertEqual(len(data["matrix"]), 42)
        self.assertEqual(data["summary"]["named_patterns"], 30)
        self.assertEqual(data["summary"]["extension_candidates"], 12)
        self.assertEqual(data["matrix"][0]["id"], "CELL_PERCEPTION_CHAIN")
        self.assertEqual(data["matrix"][0]["pattern_ref"], "PATTERN_0023")
        self.assertEqual(data["matrix"][0]["source_kind"], "paper_v2")
        self.assertEqual(data["matrix"][0]["maturity"], "draft")
        self.assertIn(
            SKILL_DIR / "references" / "registry.json",
            generator.source_files(SKILL_DIR),
        )
        self.assertIn("perception-chain", data["patterns"])
        self.assertEqual(data["patterns"]["perception-chain"]["pattern"], "Semantic Compaction / 语义压缩")
        self.assertEqual(data["patterns"]["perception-chain"]["status"], "named")
        self.assertEqual(
            data["patterns"]["perception-chain"]["source"],
            "references/patterns/perception/perception-chain.md",
        )
        self.assertEqual(
            data["observability"]["perception-chain"]["source"],
            "references/patterns/perception/perception-chain-observability.md",
        )
        self.assertEqual(len(data["cell_guides"]), 7)
        self.assertEqual(
            data["cell_guides"]["perception"]["source"],
            "references/patterns/perception/cell.md",
        )
        self.assertEqual(len(data["traces"]), 7)
        self.assertEqual(
            data["traces"]["perception"]["source"],
            "references/patterns/perception/trace.md",
        )
        self.assertEqual(
            data["selection_card"]["source"],
            "references/pattern-selection-card.md",
        )

    def test_every_matrix_cell_has_a_dedicated_pattern_file(self):
        generator = load_generator()
        data = generator.load_skill_data(SKILL_DIR)
        matrix_keys = {cell["cell_key"] for cell in data["matrix"]}
        pattern_files = sorted(
            path
            for path in PATTERN_DIR.glob("*/*.md")
            if path.name not in {"cell.md", "trace.md"} and not path.stem.endswith("-observability")
        )
        observability_files = sorted(PATTERN_DIR.glob("*/*-observability.md"))
        pattern_keys = {path.stem for path in pattern_files}
        observability_keys = {path.stem.removesuffix("-observability") for path in observability_files}

        self.assertEqual(len(pattern_files), 42)
        self.assertEqual(len(observability_files), 42)
        self.assertEqual(pattern_keys, matrix_keys)
        self.assertEqual(observability_keys, matrix_keys)
        self.assertFalse(list(PATTERN_DIR.glob("*.md")))
        self.assertFalse((SKILL_DIR / "references" / "cells").exists())

        for cell in data["matrix"]:
            expected_href = (
                "skills/harness-engineering-patterns/references/"
                f"patterns/{cell['capability_key']}/{cell['cell_key']}.md"
            )
            expected_observability_href = (
                "skills/harness-engineering-patterns/references/"
                f"patterns/{cell['capability_key']}/{cell['cell_key']}-observability.md"
            )
            self.assertEqual(cell["href"], expected_href)
            self.assertEqual(cell["observability_href"], expected_observability_href)
            pattern_path = PATTERN_DIR / cell["capability_key"] / f"{cell['cell_key']}.md"
            observability_path = PATTERN_DIR / cell["capability_key"] / f"{cell['cell_key']}-observability.md"
            content = pattern_path.read_text(encoding="utf-8")
            observability = observability_path.read_text(encoding="utf-8")
            self.assertIn(f"# {cell['pattern']}", content)
            self.assertRegex(content, re.compile(r"状态 / Status"))
            self.assertIn("## Design Pattern / 设计模式", content)
            self.assertIn("Observability Metrics File / 可观测性指标文件", content)
            self.assertNotIn("## Observability Metrics / 可观测性指标", content)
            self.assertIn("## Observability Metrics / 可观测性指标", observability)
            self.assertIn("Design Pattern File / 设计模式文件", observability)
            self.assertIn("质量指标 / Quality Metrics", observability)
            self.assertIn("时延指标 / Latency Metrics", observability)
            self.assertIn("成本指标 / Cost Metrics", observability)
            self.assertIn("风险指标 / Risk Metrics", observability)
            self.assertIn("Trace 指标 / Trace Metrics", observability)
            self.assertRegex(content, re.compile(r"论文坐标 / Article Coordinate"))
            self.assertRegex(content, re.compile(r"论文依据 / Article Basis"))
            self.assertRegex(content, re.compile(r"问题 / Problem"))
            self.assertRegex(content, re.compile(r"架构方案 / Architectural Solution"))
            self.assertRegex(content, re.compile(r"工程权衡 / Engineering Trade-offs"))
            self.assertRegex(content, re.compile(r"工作流诊断用途 / Workflow Diagnosis Use"))
            self.assertRegex(content, re.compile(r"模式清单 / Patterns"))
            self.assertRegex(content, re.compile(r"适用工作流节点 / Applicable Workflow Nodes"))
            self.assertRegex(content, re.compile(r"风险与治理 / Risks & Governance"))
            if cell["cell_key"] in REPRESENTATIVE_PATTERN_KEYS:
                self.assertIn("代表性定义 / Representative definition", content)
            elif cell["status"] == "named":
                self.assertTrue(
                    "矩阵列名模式 / Matrix-listed pattern" in content
                    or "用户扩展模式 / User-extension pattern" in content
                    or "本地扩展模式 / Local-extension pattern" in content
                )
            else:
                self.assertIn("空白单元 / Empty cell", content)

    def test_context_priority_triage_pattern_is_executable(self):
        pattern = (
            PATTERN_DIR / "perception" / "perception-routing.md"
        ).read_text(encoding="utf-8")
        observability = (
            PATTERN_DIR / "perception" / "perception-routing-observability.md"
        ).read_text(encoding="utf-8")

        required_sections = [
            "### Execution Contract / 执行契约",
            "### Core Layering Rules / 核心分层规则",
            "### Input Contract / 输入契约",
            "### Execution Procedure / 执行流程",
            "### Priority Triage Rules / 优先级分诊规则",
            "### Context Budget Assembly / 上下文预算装配",
            "### Output Schema / 输出结构",
            "### Observability Probe Interaction / 可观测性探针交互",
            "### Failure Handling / 失败处理",
            "### Done Criteria / 完成标准",
        ]
        for section in required_sections:
            self.assertIn(section, pattern)

        required_phrases = [
            "Context Priority Triage / 上下文优先级分诊",
            "Standalone Executable / 可独立执行: Yes / 是",
            "collect candidate information / 收集候选信息",
            "annotate information attributes / 标注信息属性",
            "judge information priority / 判断信息优先级",
            "control context budget / 控制上下文预算",
            "compress medium-priority information / 压缩中等优先信息",
            "mount deferred read handles / 挂载延迟读取入口",
            "build a context package / 生成上下文包",
            "record triage decisions / 记录分诊决策",
            "L0 Non-Droppable Layer / 零级不可丢失层",
            "L1 Current Work Layer / 一级当前工作层",
            "L2 Background Support Layer / 二级背景支持层",
            "L3 Deferred Read Layer / 三级延迟读取层",
            "Context Triage Result / 上下文分诊结果",
            "Triage Decision Record / 分诊决策记录",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, pattern)

        required_metrics = [
            "Priority Accuracy / 优先级准确率",
            "Budget Protection Rate / 预算保护率",
            "Context Package Ready Latency / 上下文包可用时延",
            "Read Handle Health Rate / 读取入口健康率",
            "Trace Decision Coverage / Trace 决策覆盖率",
        ]
        for metric in required_metrics:
            self.assertIn(metric, observability)

    def test_context_priority_triage_observability_is_a_probe_protocol(self):
        observability = (
            PATTERN_DIR / "perception" / "perception-routing-observability.md"
        ).read_text(encoding="utf-8")

        required_sections = [
            "## Probe Role / 探针定位",
            "## Operating Modes / 运行模式",
            "## Probe Input Contract / 探针输入契约",
            "## Event Stream / 事件流",
            "## Probe Output Contract / 探针输出契约",
            "## Metric System / 核心指标体系",
            "## Compression Strategy Assistant / 压缩策略辅助器",
            "## Probe Execution Procedure / 探针执行流程",
            "## Alert Rules / 告警规则",
            "## Feedback Writeback Rules / 反馈回填规则",
            "## Minimum Standalone Run / 独立运行最小流程",
            "## Output Templates / 输出模板",
        ]
        for section in required_sections:
            self.assertIn(section, observability)

        required_phrases = [
            "Sidecar Probe / 旁路探针",
            "Shadow Evaluator / 影子评估器",
            "Inline Guard / 内联守卫",
            "Compression Strategy Assistant / 压缩策略辅助器",
            "Observation Report / 观测报告",
            "Strategy Feedback / 策略反馈",
            "Compression Advice / 压缩建议",
            "Risk Alert / 风险告警",
            "Budget Usage Rate / 预算使用率",
            "Critical Layer Completeness / 关键层完整性",
            "High Signal Ratio / 高信号比例",
            "Priority Calibration / 优先级校准",
            "Compression Quality / 压缩质量",
            "Read Handle Health / 读取入口健康度",
            "Candidate Set Quality / 候选集质量",
            "Outcome Attribution / 结果归因",
            "Cost Benefit / 成本收益",
            "Governance Safety / 治理安全",
            "Immediate Writeback / 即时回填",
            "Next-Run Writeback / 下一轮回填",
            "Batch Writeback / 批量回填",
            "do not directly override L0 or permission rules",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, observability)

    def test_layered_retention_pattern_is_executable(self):
        pattern = (
            PATTERN_DIR / "memory" / "memory-hierarchy.md"
        ).read_text(encoding="utf-8")
        observability = (
            PATTERN_DIR / "memory" / "memory-hierarchy-observability.md"
        ).read_text(encoding="utf-8")
        matrix = (SKILL_DIR / "references" / "matrix-index.md").read_text(encoding="utf-8")
        catalog = (SKILL_DIR / "references" / "pattern-catalog.md").read_text(encoding="utf-8")
        cell = (PATTERN_DIR / "memory" / "cell.md").read_text(encoding="utf-8")

        self.assertIn(
            "[Layered Retention / 分层保留](patterns/memory/memory-hierarchy.md)",
            matrix,
        )
        self.assertIn("memory-hierarchy / 记忆 x 层级 | Layered Retention / 分层保留", catalog)
        self.assertIn("[Layered Retention / 分层保留](memory-hierarchy.md)", cell)

        required_sections = [
            "### Execution Contract / 执行契约",
            "### Input Contract / 输入契约",
            "### Output Contract / 输出契约",
            "### Core Objects / 核心对象",
            "### Execution Procedure Overview / 执行流程总览",
            "### Node 1: Request Intake And Scenario Normalization / 节点一：接收请求与场景归一",
            "### Node 5: Information Layer Classification / 节点五：信息分层判定",
            "### Node 10: Write Routing / 节点十：写入路由",
            "### Node 11: Promotion, Demotion, Discard, Human Review / 节点十一：升层、降权、丢弃、人审",
            "### Operating Modes / 两种运行模式",
            "### Probe Interaction / 探针交互",
            "### Failure Modes / 失败模式与处理",
            "### Minimum Configuration Checklist / 最小可执行清单",
        ]
        for section in required_sections:
            self.assertIn(section, pattern)

        required_phrases = [
            "Layered Retention / 分层保留",
            "Standalone Executable / 可独立执行: Yes / 是",
            "Primary Axis / 主轴: Memory / 记忆",
            "Primary Topology / 主拓扑: Hierarchy / 层级",
            "Local-extension pattern",
            "COG_MEMORY__TOP_HIERARCHY",
            "Policy / 策略层",
            "Project / 项目层",
            "User / 用户层",
            "Task / 任务层",
            "Draft / 草稿层",
            "Retention Candidate / 保留候选",
            "Layer Decision / 分层决策",
            "Write Decision / 写入决策",
            "lower layers may temporarily shape how higher-level information is used",
            "Every durable write has source, evidence, scope, lifecycle, and route",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, pattern + observability)

    def test_layered_retention_observability_is_a_probe_protocol(self):
        observability = (
            PATTERN_DIR / "memory" / "memory-hierarchy-observability.md"
        ).read_text(encoding="utf-8")

        required_sections = [
            "## Document Goal / 文档目标",
            "## Position In Harness / 在 Harness 框架中的位置",
            "## Probe Role / 探针定位",
            "## Relationship With Execution Flow / 与执行流程的关系",
            "## Operating Modes / 运行模式",
            "## Probe Input Contract / 探针输入契约",
            "## Data Model / 探针数据模型",
            "## Event Stream / 事件流",
            "## Probe Output Contract / 探针输出契约",
            "## Observation Objects / 观测对象",
            "## Probe Catalog / 探针总览",
            "## Probe Details / 探针详情",
            "### Probe 001: Scenario Completeness Probe / 探针_001：场景完整性探针",
            "### Probe 018: Structured Discipline Probe / 探针_018：结构化纪律探针",
            "## Probe-To-Execution Interaction Table / 探针与执行流程交互表",
            "## Standalone Mode / 独立运行模式",
            "## Interactive Mode / 交互运行模式",
            "## Observability Metrics / 可观测性指标",
            "## Metric System / 指标体系",
            "## Health State / 健康状态判断",
            "## Diagnostic Rules / 诊断规则",
            "## Feedback Writeback Rules / 反馈回填规则",
            "## Scenario Thresholds / 场景化阈值建议",
            "## Aggregated Views / 聚合视图",
            "## Alert Rules / 告警规则",
            "## How Probe Results Complete Execution Data / 探针结果如何补全执行流程数据",
            "## Minimum Probe Set / 最小可执行探针集",
            "## Minimum Standalone Run / 独立运行最小流程",
            "## Probe Configuration Template / 探针配置模板",
            "## Output Templates / 输出模板",
            "## Interaction Data Interface / 与执行流程交互的数据接口",
            "## Failure Coverage / 失败模式与探针覆盖",
            "## Skill Packaging Draft / 可包装技能草案",
            "## Engineering Node Registration / 推荐工程节点注册项",
            "## Version Extension Suggestions / 版本扩展建议",
            "## Failure Modes / 常见失败模式",
            "## Design Principles / 设计原则总结",
        ]
        for section in required_sections:
            self.assertIn(section, observability)

        required_phrases = [
            "Layered Retention Probe / 分层保留的工作流可观测性探针",
            "Probe does not own memory writes / 探针不直接拥有记忆写入",
            "Sidecar Probe / 旁路探针",
            "Inline Guard / 内联守卫",
            "Shadow Evaluator / 影子评估器",
            "Lifecycle Monitor / 生命周期监控器",
            "Probe Definition / 探针定义",
            "Workflow Completion Package / 工作流补全包",
            "Scenario Completeness Probe / 场景完整性探针",
            "Policy Boundary Probe / 策略边界探针",
            "Layer Decision Probe / 层级判定探针",
            "Scope Isolation Probe / 作用域隔离探针",
            "Evidence Sufficiency Probe / 证据充分性探针",
            "Draft Leakage Probe / 草稿泄漏探针",
            "Override Violation Probe / 覆盖违规探针",
            "Context Hit Probe / 上下文命中探针",
            "Context Noise Probe / 上下文噪声探针",
            "Context Budget Probe / 上下文预算探针",
            "Tool Result Validation Probe / 工具结果验证探针",
            "Checkpoint Freshness Probe / 检查点新鲜度探针",
            "Promotion Gate Probe / 升层门禁探针",
            "Expiry And Demotion Probe / 过期与降权探针",
            "Failure Retrospective Probe / 失败复盘探针",
            "Output Traceability Probe / 输出可追溯探针",
            "Human Review Gate Probe / 人审门禁探针",
            "Structured Discipline Probe / 结构化纪律探针",
            "Layer Assignment Coverage / 层级判定覆盖率",
            "Durable Write Evidence Coverage / 长期写入证据覆盖率",
            "Low-to-High Override Attempt Count / 低层覆盖高层尝试数",
            "Cross-Tenant Contamination Count / 跨租户污染数",
            "Draft Leakage Count / 草稿泄漏次数",
            "Context Hit Rate / 关键记忆命中率",
            "Context Noise Ratio / 上下文噪声占比",
            "Write Decision Trace Coverage / 写入决策追踪覆盖率",
            "Completion Package Adoption Rate / 补全包采纳率",
            "Retention Guard Decision / 保留守卫决策",
            "Offline Probe Report / 离线探针报告",
            "Workflow Health / 流程健康",
            "Memory Health / 记忆健康",
            "Context Health / 上下文健康",
            "Minimum Probe Set / 最小可执行探针集",
            "Probe Configuration / 探针配置",
            "NODE_OBSERVABILITY_EVENT_CAPTURE",
            "Do not directly override policy or permission rules from probe feedback",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, observability)

    def test_semantic_compaction_pattern_is_executable(self):
        pattern = (
            PATTERN_DIR / "perception" / "perception-chain.md"
        ).read_text(encoding="utf-8")

        required_sections = [
            "### Execution Contract / 执行契约",
            "### Mounting Guidance / 框架挂载建议",
            "### Scenario Adaptation / 场景适配层",
            "### Input Contract / 输入契约",
            "### Output Contract / 输出契约",
            "### Core Objects / 核心对象",
            "### Compression Levels / 压缩级别",
            "### Trigger Strategy / 触发策略",
            "### Execution Procedure / 执行流程",
            "### Information Handling Strategy / 信息处理策略",
            "### Quality Gate / 质量门禁",
            "### Handoff Summary / 交接摘要",
            "### Minimum Standalone Run / 独立运行最小流程",
            "### Probe Interaction / 探针交互",
            "### Evaluation / 评估方式",
            "### Failure Modes / 常见失败模式",
            "### Done Criteria / 完成标准",
        ]
        for section in required_sections:
            self.assertIn(section, pattern)

        required_phrases = [
            "Semantic Compression Execution / 语义压缩的执行流程",
            "Standalone Executable / 可独立执行: Yes / 是",
            "Primary Axis / 主轴: Perception / 感知",
            "Secondary Axes / 辅轴: Memory / 记忆; Governance / 治理",
            "Primary Topology / 主拓扑: Chain / 链式",
            "Secondary Topologies / 辅拓扑: Loop / 循环; Orchestration / 编排",
            "reduce context occupancy / 减少上下文占用",
            "preserve key semantics / 保留关键语义",
            "protect traceable evidence / 保护可回溯证据",
            "Information Fragment / 信息片段",
            "Evidence Item / 证据项",
            "Working Memory Anchor / 工作记忆锚点",
            "Compression Event / 压缩事件",
            "L0 Mark Only / 第零级：不压缩，只标注",
            "L1 Clean Verbose Returns / 第一级：清理冗长返回",
            "L2 Merge into Working Memory Anchor / 第二级：合并进工作记忆锚点",
            "L3 Extreme Compression and Handoff Signal / 第三级：极限压缩与交接信号",
            "Quality Gate Result / 质量门禁结果",
            "Handoff Summary / 交接摘要",
            "Do not repeatedly summarize the summary",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, pattern)

    def test_progressive_discovery_pattern_is_executable(self):
        pattern = (
            PATTERN_DIR / "perception" / "perception-loop.md"
        ).read_text(encoding="utf-8")
        matrix = (SKILL_DIR / "references" / "matrix-index.md").read_text(encoding="utf-8")
        catalog = (SKILL_DIR / "references" / "pattern-catalog.md").read_text(encoding="utf-8")
        cell = (PATTERN_DIR / "perception" / "cell.md").read_text(encoding="utf-8")

        self.assertIn(
            "[Progressive Discovery / 渐进式发现](patterns/perception/perception-loop.md)",
            matrix,
        )
        self.assertIn("perception-loop / 感知 x 循环 | Progressive Discovery / 渐进式发现", catalog)
        self.assertIn("[Progressive Discovery / 渐进式发现](perception-loop.md)", cell)

        required_sections = [
            "### Execution Contract / 执行契约",
            "### Problem Framing / 问题定位",
            "### Search Space Trimming / 搜索空间裁剪",
            "### Input Contract / 输入契约",
            "### Output Contract / 输出契约",
            "### Core Objects / 核心对象",
            "### Discovery Stages / 发现阶段",
            "### Execution Procedure / 执行流程",
            "### Loop Rules / 循环规则",
            "### Stop and Escalation Rules / 停止与升级规则",
            "### Quality Gate / 质量门禁",
            "### Scenario Adaptation / 场景适配层",
            "### Probe Interaction / 探针交互",
            "### Failure Modes / 常见失败模式",
            "### Done Criteria / 完成标准",
        ]
        for section in required_sections:
            self.assertIn(section, pattern)

        required_phrases = [
            "Progressive Discovery / 渐进式发现",
            "Standalone Executable / 可独立执行: Yes / 是",
            "Primary Axis / 主轴: Perception / 感知",
            "Primary Topology / 主拓扑: Loop / 循环",
            "Secondary Topologies / 辅拓扑: Orchestration / 编排; Chain / 链式; Routing / 路由",
            "do not load the whole information space at once / 不一次性加载整个信息空间",
            "expand only when evidence justifies expansion / 只有证据支持扩展时才扩展",
            "Task Profile / 任务画像",
            "Discovery Candidate / 发现候选",
            "Discovery Event / 探索事件",
            "Evidence Item / 证据项",
            "Discovery Session / 探索会话",
            "Broad Scan / 广扫",
            "Focus / 聚焦",
            "Deep Dive / 深挖",
            "Verify / 验证",
            "Stop Rule / 停止规则",
            "Escalation Rule / 升级规则",
            "Quality Gate Result / 质量门禁结果",
            "Progressive Discovery Result / 渐进发现结果",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, pattern)

    def test_progressive_discovery_observability_is_a_probe_protocol(self):
        observability = (
            PATTERN_DIR / "perception" / "perception-loop-observability.md"
        ).read_text(encoding="utf-8")

        required_sections = [
            "## Probe Role / 探针定位",
            "## Relationship with Execution Flow / 与执行流程的关系",
            "## Operating Modes / 运行模式",
            "## Probe Input Contract / 探针输入契约",
            "## Probe Output Contract / 探针输出契约",
            "## Observation Objects / 观测对象",
            "## Stage Observation / 阶段观测",
            "## Observability Metrics / 可观测性指标",
            "## Metric System / 指标体系",
            "## Health State / 健康状态判断",
            "## Diagnostic Rules / 诊断规则",
            "## Feedback Writeback Rules / 反馈回填规则",
            "## Scenario Adaptation / 场景适配层",
            "## Probe Report Template / 探针报告模板",
            "## Minimum Standalone Run / 独立运行最小流程",
            "## Governance Requirements / 治理要求",
            "## Anti-Patterns / 反模式",
            "## Interaction Data Interface / 与执行流程交互的数据接口",
            "## Minimum Checklist / 最小检查清单",
        ]
        for section in required_sections:
            self.assertIn(section, observability)

        required_phrases = [
            "Progressive Discovery Probe / 渐进发现的工作流可观测性探针",
            "Standalone Executable / 可独立执行: Yes / 是",
            "Probe does not search / 探针不负责寻找信息",
            "Probe does not directly provide the final business answer / 探针不直接给最终业务答案",
            "Sidecar Observation Mode / 旁路观测模式",
            "Online Assistance Mode / 联机辅助模式",
            "Replay Evaluation Mode / 回放评测模式",
            "Probe Report / 探针报告",
            "Metric Snapshot / 指标快照",
            "Failure Diagnosis / 失败诊断",
            "Feedback Advice / 回填建议",
            "Efficiency Metrics / 效率指标",
            "Search Quality Metrics / 搜索质量指标",
            "Focus Quality Metrics / 聚焦质量指标",
            "Deep Dive Quality Metrics / 深挖质量指标",
            "Verification Quality Metrics / 验证质量指标",
            "Traceability Metrics / 可观测性指标",
            "Governance Metrics / 治理指标",
            "Rounds To Signal / 成功所需轮数",
            "Broad Scan To Focus Budget Ratio / 广扫与聚焦预算比",
            "Zero Signal Rate / 零信号率",
            "Candidate Relevance Rate / 候选相关率",
            "Selected Candidate Precision / 选中精确率",
            "High-Value Candidate Miss Rate / 高价值候选漏选率",
            "Marginal Evidence Gain / 边际新增价值",
            "Evidence Chain Completeness / 证据链完整度",
            "Counterexample Check Rate / 反例检查率",
            "Trace Completeness / 轨迹完整度",
            "Stage Transition Explainability / 阶段切换可解释率",
            "Stop Reason Record Rate / 停止原因记录率",
            "Permission Exception Rate / 权限异常率",
            "Sensitive Information Exposure Risk / 敏感信息暴露风险",
            "Keyword Suggestions / 关键词建议",
            "Search Boundary Suggestions / 搜索范围建议",
            "Ranking Suggestions / 排序建议",
            "Stage Transition Suggestions / 阶段切换建议",
            "Evidence Gap Suggestions / 证据缺口建议",
            "Stop Suggestions / 停止建议",
            "do not save unnecessary raw material",
            "metrics do not replace judgment",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, observability)

    def test_semantic_compaction_observability_is_a_probe_protocol(self):
        observability = (
            PATTERN_DIR / "perception" / "perception-chain-observability.md"
        ).read_text(encoding="utf-8")

        required_sections = [
            "## Probe Role / 探针定位",
            "## Mounting Guidance / 框架挂载建议",
            "## Relationship with Execution Flow / 与执行流程的关系",
            "## Scenario Adaptation / 场景适配层",
            "## Probe Input Contract / 探针输入契约",
            "## Probe Output Contract / 探针输出契约",
            "## Core Objects / 核心对象",
            "## Probe Execution Procedure / 探针执行流程",
            "## Observability Metrics / 可观测性指标",
            "## Metric System / 指标体系",
            "## Compression Advice Control Block / 压缩建议控制块",
            "## Quality Gate / 质量门禁",
            "## Sidecar Report Format / 旁路报告格式",
            "## Alert Rules / 告警规则",
            "## Minimum Standalone Run / 独立运行最小版本",
            "## Interaction Data Interface / 与执行流程交互的数据接口",
            "## Evaluation / 评估方式",
            "## Failure Modes / 常见失败模式",
            "## Design Principles / 设计原则总结",
        ]
        for section in required_sections:
            self.assertIn(section, observability)

        required_phrases = [
            "Semantic Compression Probe / 语义压缩的工作流可观测性探针",
            "Standalone Executable / 可独立执行: Yes / 是",
            "Probe does not compress / 探针不压缩",
            "Primary Axes / 主轴: Governance / 治理; Reflection / 反思",
            "Secondary Axes / 辅轴: Perception / 感知; Memory / 记忆",
            "Primary Topology / 主拓扑: Parallel / 并行",
            "Secondary Topologies / 辅拓扑: Chain / 链式; Loop / 循环; Orchestration / 编排",
            "Workflow Event / 工作流事件",
            "Evidence Item / 证据项",
            "Metric Snapshot / 指标快照",
            "Compression Advice / 压缩建议",
            "Quality Gate Result / 质量门禁结果",
            "Runtime Health Metrics / 运行健康指标",
            "Compression Effect Metrics / 压缩效果指标",
            "Evidence Protection Metrics / 证据保护指标",
            "Working Memory Metrics / 工作记忆指标",
            "Behavior Degradation Metrics / 行为退化指标",
            "Governance Audit Metrics / 治理审计指标",
            "Control Block / 控制块",
            "Full metrics go to monitoring and audit",
            "Critical Error Loss Count / 关键错误丢失数",
            "Source Handle Traceability Rate / 原文句柄可回溯率",
            "Working Memory Completeness / 工作记忆完整度",
            "Repeated Failed Action Rate After Compression / 压缩后重复失败动作率",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, observability)

    def test_patterns_are_grouped_by_vertical_cell_with_intro_trace_and_patterns(self):
        generator = load_generator()
        data = generator.load_skill_data(SKILL_DIR)
        cell_dirs = sorted(path for path in PATTERN_DIR.iterdir() if path.is_dir())
        axis_keys = {axis["key"] for axis in data["vertical_axes"]}

        self.assertEqual(len(cell_dirs), 7)
        self.assertEqual({path.name for path in cell_dirs}, CAPABILITY_KEYS)
        self.assertEqual(axis_keys, CAPABILITY_KEYS)

        for axis in data["vertical_axes"]:
            cell_dir = PATTERN_DIR / axis["key"]
            guide_path = cell_dir / "cell.md"
            trace_path = cell_dir / "trace.md"
            design_pattern_files = sorted(
                path for path in cell_dir.glob(f"{axis['key']}-*.md") if not path.stem.endswith("-observability")
            )
            observability_files = sorted(cell_dir.glob(f"{axis['key']}-*-observability.md"))

            content = guide_path.read_text(encoding="utf-8")
            linked_patterns = re.findall(r"\]\(\.\./patterns/([a-z]+-[a-z]+)\.md\)", content)
            if not linked_patterns:
                linked_patterns = re.findall(r"\]\(([a-z]+-[a-z]+)\.md\)", content)

            self.assertIn("导论", content)
            self.assertIn("Introduction", content)
            self.assertIn("Role / 定位", content)
            self.assertIn("论文对齐 / Article Alignment", content)
            self.assertIn("矩阵摘要 / Matrix Summary", content)
            self.assertIn("选择法则 / Selection Laws", content)
            self.assertIn("Navigation / 导航", content)
            self.assertEqual(len(set(linked_patterns)), 6)
            self.assertTrue(all(key.startswith(f"{axis['key']}-") for key in set(linked_patterns)))
            self.assertNotIn("当前症状 / Current Symptoms", content)

            trace_content = trace_path.read_text(encoding="utf-8")
            self.assertIn("Trace / 追踪", trace_content)
            self.assertIn("Usage Log / 使用日志", trace_content)
            self.assertIn("Pattern Used / 使用模式", trace_content)
            self.assertIn("Outcome / 结果", trace_content)
            self.assertIn("Evidence / 证据", trace_content)
            self.assertEqual(len(design_pattern_files), 6)
            self.assertEqual(len(observability_files), 6)

    def test_renders_self_contained_html_visualization(self):
        generator = load_generator()
        data = generator.load_skill_data(SKILL_DIR)

        html = generator.render_html(data)

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn("Harness Engineering Patterns", html)
        self.assertIn("Semantic Compaction / 语义压缩", html)
        self.assertIn("Blast Radius Control / 爆炸半径控制", html)
        self.assertIn("references/patterns/perception/cell.md", html)
        self.assertIn("references/patterns/perception/trace.md", html)
        self.assertIn("references/patterns/perception/perception-chain.md", html)
        self.assertIn("references/patterns/perception/perception-chain-observability.md", html)
        self.assertIn("Pattern Selection Card / 模式选型卡", html)
        self.assertIn("references/pattern-selection-card.md", html)
        self.assertIn("Trace Insert / Trace 插入", html)
        self.assertIn("Design Pattern / 设计模式", html)
        self.assertIn("Observability Metrics / 可观测性指标", html)
        self.assertIn("Provenance / 来源", html)
        self.assertIn("Maturity / 成熟度", html)
        self.assertIn("data-source-hash=", html)
        self.assertNotIn("{{", html)

    def test_pattern_selection_card_requires_trace_before_selection(self):
        card = SELECTION_CARD.read_text(encoding="utf-8")
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        diagnosis = (SKILL_DIR / "references" / "diagnosis-method.md").read_text(encoding="utf-8")

        for content in (card, skill, diagnosis):
            self.assertIn("Trace Insert / Trace 插入", content)
            self.assertIn("Pattern Selection Card / 模式选型卡", content)

        required_phrases = [
            "ASSESS / 评估",
            "ROUTE / 判拓扑",
            "SELECT / 查矩阵",
            "低协作 + 短任务",
            "中等复杂 + 多步骤",
            "多专家 + 宽任务",
            "高风险动作",
            "Governance Routing / Chain / Hierarchy",
            "Engineering Node / 工程节点",
            "Node Evidence / 节点证据",
            "Trace Evidence / Trace 证据",
            "Selected Patterns / 已选模式",
            "Plan / 规划",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, card)

        trace_position = card.index("Trace Insert / Trace 插入")
        selection_position = card.index("Pattern Selection Card / 模式选型卡")
        self.assertLess(trace_position, selection_position)

    def test_engineering_node_analysis_automatically_runs_selection_flow(self):
        card = SELECTION_CARD.read_text(encoding="utf-8")
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        diagnosis = (SKILL_DIR / "references" / "diagnosis-method.md").read_text(encoding="utf-8")

        for content in (card, skill, diagnosis):
            self.assertIn("Automatic Engineering Node Analysis / 工程节点自动分析", content)
            self.assertIn("automatically run Trace Insert / 自动运行 Trace 插入", content)
            self.assertIn("Pattern Selection Card / 模式选型卡", content)

        self.assertRegex(skill, re.compile(r"description: .*engineering node", re.I))
        self.assertIn("Do not skip directly to matrix selection", card)

    def test_compiler_references_are_linked_and_bilingual(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        for relative_path, required_phrases in COMPILER_REFERENCE_FILES.items():
            self.assertIn(relative_path, skill)
            content = (SKILL_DIR / relative_path).read_text(encoding="utf-8")
            for phrase in required_phrases:
                self.assertIn(phrase, content)

        self.assertIn("Workflow / Harness Source / 工作流程 / Harness 源码", skill)
        self.assertIn("Engineering Intermediate Representation / 工程中间表示", skill)
        self.assertIn("Evidence + Evaluation + Governance / 证据 + 评估 + 治理", skill)

    def test_pattern_ids_are_unique_and_consistent(self):
        packaging = (SKILL_DIR / "references" / "pattern-skill-packaging.md").read_text(encoding="utf-8")
        seed_rows = re.findall(r"^\| `(PATTERN_\d{4})` \| ([^/|]+?) /", packaging, re.MULTILINE)
        seed_ids = [pattern_id for pattern_id, _ in seed_rows]
        self.assertEqual(len(seed_ids), len(set(seed_ids)), "duplicate PATTERN_* id in seed table")
        id_to_name = {pattern_id: name.strip() for pattern_id, name in seed_rows}

        binding_re = re.compile(r"(PATTERN_\d{4}) / ([^/\n]+?) /")
        skill_id_re = re.compile(r"skill_id[^:\n]*:\s*(SKILL_[A-Z0-9_]+)")
        skill_id_sources = {}
        for path in SKILL_DIR.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            for pattern_id, name in binding_re.findall(content):
                self.assertIn(
                    pattern_id,
                    id_to_name,
                    f"{path}: {pattern_id} is not registered in pattern-skill-packaging.md",
                )
                self.assertEqual(
                    id_to_name[pattern_id],
                    name.strip(),
                    f"{path}: {pattern_id} bound to '{name.strip()}' but registered as '{id_to_name[pattern_id]}'",
                )
            for skill_id in skill_id_re.findall(content):
                previous = skill_id_sources.setdefault(skill_id, path)
                self.assertEqual(
                    previous,
                    path,
                    f"duplicate skill_id {skill_id} in {previous} and {path}",
                )


if __name__ == "__main__":
    unittest.main()
