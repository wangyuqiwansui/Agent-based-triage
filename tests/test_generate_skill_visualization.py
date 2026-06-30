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
        self.assertEqual(data["summary"]["named_patterns"], 29)
        self.assertEqual(data["summary"]["extension_candidates"], 13)
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


if __name__ == "__main__":
    unittest.main()
