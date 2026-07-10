from __future__ import annotations

import argparse
import json
import pathlib
import re
from collections import Counter


DESIGN_FIELDS = (
    "状态 / Status",
    "模式清单 / Patterns",
    "诊断用途 / Diagnostic Use",
    "适用工作流节点 / Applicable Workflow Nodes",
    "当前症状 / Current Symptoms",
    "适配信号 / Fit Signals",
    "调整方向 / Adjustment Direction",
    "修改方式 / How To Modify",
    "输入 / Inputs",
    "输出 / Outputs",
    "风险与治理 / Risks & Governance",
)

OBSERVABILITY_FIELDS = (
    "质量指标 / Quality Metrics",
    "时延指标 / Latency Metrics",
    "成本指标 / Cost Metrics",
    "风险指标 / Risk Metrics",
    "Trace 指标 / Trace Metrics",
)

EIR_HEADINGS = (
    "## Control Flow / 控制流",
    "## State Flow / 状态流",
    "## Tool Flow / 工具流",
    "## Permission Flow / 权限流",
    "## Pattern Record / 模式记录",
    "## Skill Recommendation / Skill 建议",
    "## Evaluation Reference / 评价引用",
    "## Governance Item / 治理项",
)

EVALUATION_KEYS = (
    "coverage",
    "mapping_accuracy",
    "evidence",
    "reuse",
    "skill_readiness",
    "governance",
    "evaluability",
)

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\((?P<target>[^)]+)\)")
BUNDLED_TRACE_TARGET = (
    r"(?:`?references/patterns/<capability-key>/trace\.md`?|"
    r"\[trace\.md\]\(trace\.md\))"
)
BUNDLED_TRACE_WRITE = re.compile(
    r"(?is)\b(?:add\s+an\s+entry|append|write|update|record)\b.{0,80}"
    r"\b(?:to|into|in)\s+" + BUNDLED_TRACE_TARGET
)
BUNDLED_TRACE_PATH_FIRST_WRITE = re.compile(
    r"(?is)" + BUNDLED_TRACE_TARGET
    + r".{0,60}(?:\bto\s+(?:append|write|update|record)\b|记录(?:使用)?结果|写入结果|追加记录)"
)


class ValidationReport:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, code: str, message_en: str, message_zh: str) -> None:
        self.errors.append(f"{code}: {message_en} / {message_zh}")

    def warning(self, code: str, message_en: str, message_zh: str) -> None:
        self.warnings.append(f"{code}: {message_en} / {message_zh}")


def load_registry(skill_dir: pathlib.Path) -> dict[str, object]:
    path = skill_dir / "references" / "registry.json"
    return json.loads(path.read_text(encoding="utf-8"))


def duplicate_values(records: list[dict[str, object]], field: str) -> list[str]:
    values = [str(record.get(field, "")) for record in records]
    return sorted(value for value, count in Counter(values).items() if count > 1)


def has_bundled_trace_write(content: str) -> bool:
    return bool(
        BUNDLED_TRACE_WRITE.search(content)
        or BUNDLED_TRACE_PATH_FIRST_WRITE.search(content)
    )


def validate_registry_shape(
    registry: dict[str, object],
    skill_dir: pathlib.Path,
    report: ValidationReport,
) -> None:
    required = {
        "schema_version",
        "skill",
        "upstream_sources",
        "allowed_values",
        "governance_rules",
        "failure_mode_refs",
        "capabilities",
        "topologies",
        "patterns",
        "cells",
    }
    missing = sorted(required - set(registry))
    if missing:
        report.error(
            "registry_shape",
            f"missing top-level keys {missing}",
            f"缺少顶层键 {missing}",
        )
        return

    capabilities = registry.get("capabilities", [])
    topologies = registry.get("topologies", [])
    patterns = registry.get("patterns", [])
    cells = registry.get("cells", [])
    governance_rules = registry.get("governance_rules", [])
    failure_mode_refs = registry.get("failure_mode_refs", [])
    collections = (
        capabilities,
        topologies,
        patterns,
        cells,
        governance_rules,
        failure_mode_refs,
    )
    if not all(isinstance(items, list) for items in collections):
        report.error(
            "registry_shape",
            "registry record collections must be arrays",
            "注册表记录集合必须是数组",
        )
        return

    expected_counts = (
        ("capabilities", capabilities, 7),
        ("topologies", topologies, 6),
        ("cells", cells, 42),
    )
    for label, records, expected in expected_counts:
        if len(records) != expected:
            report.error(
                "registry_shape",
                f"{label} expected {expected}, observed {len(records)}",
                f"{label} 应为 {expected}，实际为 {len(records)}",
            )

    for label, records, code in (
        ("capability", capabilities, "duplicate_capability_id"),
        ("topology", topologies, "duplicate_topology_id"),
        ("pattern", patterns, "duplicate_pattern_id"),
        ("cell", cells, "duplicate_cell_id"),
        ("governance rule", governance_rules, "registry_shape"),
        ("failure mode", failure_mode_refs, "registry_shape"),
    ):
        for duplicate in duplicate_values(records, "id"):
            report.error(
                code,
                f"duplicate {label} id {duplicate}",
                f"重复的 {label} ID {duplicate}",
            )

    if len(governance_rules) < 3:
        report.error(
            "registry_shape",
            "at least three explicit governance rules are required",
            "至少需要三条明确治理规则",
        )

    for field in ("coordinate", "cell_key", "design_path", "observability_path"):
        for duplicate in duplicate_values(cells, field):
            report.error(
                "registry_shape",
                f"duplicate cell {field} {duplicate}",
                f"重复的单元字段 {field}: {duplicate}",
            )

    allowed_values = registry.get("allowed_values", {})
    allowed_status = set(allowed_values.get("cell_status", []))
    allowed_maturity = set(allowed_values.get("maturity", []))
    allowed_source_kind = set(allowed_values.get("source_kind", []))
    pattern_ids = {pattern.get("id") for pattern in patterns}
    capability_by_id = {item.get("id"): item for item in capabilities}
    topology_by_id = {item.get("id"): item for item in topologies}
    expected_pairs = {
        (capability_id, topology_id)
        for capability_id in capability_by_id
        for topology_id in topology_by_id
    }
    observed_pairs: Counter[tuple[object, object]] = Counter()

    for cell in cells:
        cell_id = str(cell.get("id", "<missing>"))
        status = cell.get("status")
        maturity = cell.get("maturity")
        source_kind = cell.get("source_kind")
        if (
            status not in allowed_status
            or maturity not in allowed_maturity
            or source_kind not in allowed_source_kind
        ):
            report.error(
                "registry_shape",
                f"{cell_id} has invalid status, maturity, or source kind",
                f"{cell_id} 的状态、成熟度或来源类型无效",
            )

        capability_ref = cell.get("capability_ref")
        topology_ref = cell.get("topology_ref")
        capability = capability_by_id.get(capability_ref)
        topology = topology_by_id.get(topology_ref)
        if capability is None or topology is None:
            report.error(
                "registry_shape",
                f"{cell_id} references unknown capability or topology",
                f"{cell_id} 引用了未知能力或拓扑",
            )
        else:
            observed_pairs[(capability_ref, topology_ref)] += 1
            capability_key = str(capability.get("key"))
            topology_key = str(topology.get("key"))
            expected_fields = {
                "id": f"CELL_{capability_key.upper()}_{topology_key.upper()}",
                "coordinate": f"{capability_ref}__{topology_ref}",
                "cell_key": f"{capability_key}-{topology_key}",
                "design_path": (
                    f"references/patterns/{capability_key}/"
                    f"{capability_key}-{topology_key}.md"
                ),
                "observability_path": (
                    f"references/patterns/{capability_key}/"
                    f"{capability_key}-{topology_key}-observability.md"
                ),
            }
            for field, expected in expected_fields.items():
                if cell.get(field) != expected:
                    report.error(
                        "registry_shape",
                        f"{cell_id} {field} expected {expected}",
                        f"{cell_id} 的 {field} 应为 {expected}",
                    )

        for numeric_field in ("local_evidence_count", "domain_count"):
            value = cell.get(numeric_field)
            if type(value) is not int or value < 0:
                report.error(
                    "registry_shape",
                    f"{cell_id} {numeric_field} must be a non-negative integer",
                    f"{cell_id} 的 {numeric_field} 必须是非负整数",
                )
        if maturity in {"validated", "operational"} and cell.get("local_evidence_count", 0) < 2:
            report.error(
                "registry_shape",
                f"{cell_id} maturity {maturity} requires at least two evidence cases",
                f"{cell_id} 的成熟度 {maturity} 至少需要两个证据案例",
            )

        design_path = skill_dir / str(cell.get("design_path", ""))
        observability_path = skill_dir / str(cell.get("observability_path", ""))
        if not design_path.is_file():
            report.error(
                "missing_design_file",
                f"{cell_id} design file not found: {design_path}",
                f"{cell_id} 的设计文件不存在：{design_path}",
            )
        if not observability_path.is_file():
            report.error(
                "missing_observability_file",
                f"{cell_id} observability file not found: {observability_path}",
                f"{cell_id} 的可观测性文件不存在：{observability_path}",
            )

        if status == "named":
            if source_kind not in {"paper_v2", "local_extension"}:
                report.error(
                    "registry_shape",
                    f"{cell_id} named cell has invalid source kind {source_kind}",
                    f"{cell_id} 命名单元的来源类型 {source_kind} 无效",
                )
            if not source_kind or not cell.get("source_name_en") and source_kind == "paper_v2":
                report.error(
                    "missing_provenance",
                    f"{cell_id} is missing named-pattern provenance",
                    f"{cell_id} 缺少命名模式来源",
                )
            if cell.get("pattern_ref") not in pattern_ids:
                report.error(
                    "registry_shape",
                    f"{cell_id} references an unknown pattern id {cell.get('pattern_ref')}",
                    f"{cell_id} 引用了未知模式 ID {cell.get('pattern_ref')}",
                )
        else:
            if source_kind != "paper_blank" or maturity != "seed":
                report.error(
                    "registry_shape",
                    f"{cell_id} extension candidate must be a paper_blank seed",
                    f"{cell_id} 扩展候选必须是 paper_blank 种子",
                )
            if cell.get("pattern_ref") is not None:
                report.error(
                    "registry_shape",
                    f"{cell_id} extension candidate must not have a pattern id",
                    f"{cell_id} 扩展候选不得拥有模式 ID",
                )

    missing_pairs = expected_pairs - set(observed_pairs)
    duplicate_pairs = sorted(pair for pair, count in observed_pairs.items() if count > 1)
    if missing_pairs or duplicate_pairs:
        report.error(
            "registry_shape",
            f"7x6 coverage has missing pairs {sorted(missing_pairs)} or duplicates {duplicate_pairs}",
            f"7x6 覆盖存在缺失坐标 {sorted(missing_pairs)} 或重复坐标 {duplicate_pairs}",
        )

    upstream_sources = registry.get("upstream_sources", [])
    if len(upstream_sources) != 1 or not isinstance(upstream_sources[0], dict):
        report.error(
            "registry_shape",
            "exactly one pinned upstream source is required",
            "必须且只能有一个固定上游来源",
        )
    else:
        upstream = upstream_sources[0]
        named_count = upstream.get("named_pattern_count")
        blank_count = upstream.get("blank_cell_count")
        source_counts = Counter(cell.get("source_kind") for cell in cells)
        valid_counts = type(named_count) is int and type(blank_count) is int
        if (
            upstream.get("version") != "v2"
            or not valid_counts
            or named_count != 28
            or blank_count != 14
            or source_counts["paper_v2"] != named_count
            or source_counts["local_extension"] != 2
            or source_counts["paper_blank"] + source_counts["local_extension"] != blank_count
        ):
            report.error(
                "registry_shape",
                "provenance counts must remain 28 named, 14 blank, 2 promoted, and 12 candidates",
                "来源统计必须保持 28 个命名、14 个空白、2 个晋升和 12 个候选",
            )

    known_coordinates = {str(cell.get("coordinate")) for cell in cells}
    for rule in governance_rules:
        reference = skill_dir / str(rule.get("reference", ""))
        if (
            not re.fullmatch(r"GOV_RULE_\d{4}", str(rule.get("id", "")))
            or not rule.get("name_en")
            or not rule.get("name_zh")
            or not reference.is_file()
        ):
            report.error(
                "registry_shape",
                f"invalid governance rule {rule.get('id')}",
                f"治理规则 {rule.get('id')} 无效",
            )

    failure_file = skill_dir / "references" / "failure-modes.md"
    failure_text = failure_file.read_text(encoding="utf-8") if failure_file.is_file() else ""
    declared_failures = {str(item.get("id")) for item in failure_mode_refs}
    documented_failures = set(re.findall(r"FAIL_\d{4}", failure_text))
    if declared_failures != documented_failures:
        report.error(
            "registry_shape",
            "failure-mode references do not match failure-modes.md",
            "失败模式引用与 failure-modes.md 不一致",
        )
    for item in failure_mode_refs:
        reference = skill_dir / str(item.get("reference", ""))
        if item.get("coordinate") not in known_coordinates or not reference.is_file():
            report.error(
                "registry_shape",
                f"invalid failure-mode reference {item.get('id')}",
                f"失败模式引用 {item.get('id')} 无效",
            )


def parse_matrix_records(
    matrix: str,
    capabilities: list[dict[str, object]],
    topologies: list[dict[str, object]],
) -> dict[tuple[object, object], tuple[str, str]]:
    capability_labels = {
        f"{item.get('name_en')} / {item.get('name_zh')}": item.get("id")
        for item in capabilities
    }
    records: dict[tuple[object, object], tuple[str, str]] = {}
    for line in matrix.splitlines():
        if not line.startswith("|"):
            continue
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) != len(topologies) + 1:
            continue
        capability_id = capability_labels.get(columns[0])
        if capability_id is None:
            continue
        for topology, raw_cell in zip(topologies, columns[1:]):
            match = re.fullmatch(r"\[(?P<label>.+)\]\((?P<path>[^)]+)\)", raw_cell)
            if match:
                records[(capability_id, topology.get("id"))] = (
                    match.group("label"),
                    match.group("path"),
                )
    return records


def parse_catalog_records(catalog: str) -> tuple[dict[str, tuple[str, str]], set[str]]:
    named: dict[str, tuple[str, str]] = {}
    extensions: set[str] = set()
    for line in catalog.splitlines():
        if line.startswith("|"):
            columns = [column.strip() for column in line.strip().strip("|").split("|")]
            if len(columns) == 3:
                cell_key = columns[0].split(" / ", 1)[0]
                if re.fullmatch(r"[a-z]+-[a-z]+", cell_key):
                    named[cell_key] = (columns[1], columns[2])
        match = re.match(r"^- (?P<cell_key>[a-z]+-[a-z]+) / ", line)
        if match:
            extensions.add(match.group("cell_key"))
    return named, extensions


def validate_markdown_views(
    registry: dict[str, object],
    skill_dir: pathlib.Path,
    report: ValidationReport,
) -> None:
    matrix = (skill_dir / "references" / "matrix-index.md").read_text(encoding="utf-8")
    catalog = (skill_dir / "references" / "pattern-catalog.md").read_text(encoding="utf-8")
    capabilities = registry.get("capabilities", [])
    topologies = registry.get("topologies", [])
    capability_by_id = {item.get("id"): item for item in capabilities}
    topology_by_id = {item.get("id"): item for item in topologies}
    matrix_records = parse_matrix_records(matrix, capabilities, topologies)
    catalog_named, catalog_extensions = parse_catalog_records(catalog)

    for cell in registry.get("cells", []):
        cell_key = str(cell.get("cell_key", ""))
        capability = capability_by_id.get(cell.get("capability_ref"), {})
        topology = topology_by_id.get(cell.get("topology_ref"), {})
        expected_label = f"{cell.get('local_name_en')} / {cell.get('local_name_zh')}"
        expected_path = str(cell.get("design_path", "")).removeprefix("references/")
        matrix_record = matrix_records.get(
            (cell.get("capability_ref"), cell.get("topology_ref"))
        )
        if matrix_record != (expected_label, expected_path):
            report.error(
                "matrix_drift",
                f"{cell_key} does not match matrix-index.md",
                f"{cell_key} 与 matrix-index.md 不一致",
            )

        if cell.get("status") == "named":
            catalog_record = catalog_named.get(cell_key)
            catalog_matches = bool(
                catalog_record
                and catalog_record[0].startswith(expected_label)
                and str(cell.get("diagnostic_use_en")) in catalog_record[1]
                and str(cell.get("diagnostic_use_zh")) in catalog_record[1]
            )
        else:
            catalog_matches = cell_key in catalog_extensions and cell_key not in catalog_named
        if not catalog_matches:
            report.error(
                "catalog_drift",
                f"{cell_key} does not match pattern-catalog.md",
                f"{cell_key} 与 pattern-catalog.md 不一致",
            )

        design_path = skill_dir / str(cell.get("design_path", ""))
        if design_path.is_file():
            content = design_path.read_text(encoding="utf-8")
            for field in DESIGN_FIELDS:
                if field not in content:
                    report.error(
                        "missing_design_field",
                        f"{cell_key} missing {field}",
                        f"{cell_key} 缺少 {field}",
                    )
            expected_header = f"# {expected_label}"
            expected_cell = (
                f"Cell / 交织点: {cell_key} / {capability.get('name_zh')} x "
                f"{topology.get('name_zh')}"
            )
            expected_capability = (
                f"Capability / 能力: {capability.get('name_en')} / "
                f"{capability.get('name_zh')}"
            )
            expected_mode = (
                f"Mode / 模式: {topology.get('name_en')} / {topology.get('name_zh')}"
            )
            status_match = re.search(r"(?m)^- 状态 / Status:\s*(.*)$", content)
            expected_status = (
                "Named candidate"
                if cell.get("status") == "named"
                else "Extension candidate"
            )
            header_matches = (
                content.startswith(expected_header + "\n")
                and expected_cell in content
                and expected_capability in content
                and expected_mode in content
                and status_match is not None
                and expected_status in status_match.group(1)
            )
            aliases = list(cell.get("aliases_en", [])) + list(cell.get("aliases_zh", []))
            if not header_matches or any(alias not in content for alias in aliases):
                report.error(
                    "catalog_drift",
                    f"{cell_key} design header or aliases drift from registry",
                    f"{cell_key} 的设计文件头或别名与注册表不一致",
                )

        observability_path = skill_dir / str(cell.get("observability_path", ""))
        if observability_path.is_file():
            content = observability_path.read_text(encoding="utf-8")
            for field in OBSERVABILITY_FIELDS:
                if field not in content:
                    report.error(
                        "missing_observability_field",
                        f"{cell_key} missing {field}",
                        f"{cell_key} 缺少 {field}",
                    )

    for capability in capabilities:
        guide_path = skill_dir / str(capability.get("guide_path", ""))
        expected_title = (
            f"# {capability.get('name_en')} Cells Introduction / "
            f"{capability.get('name_zh')}交织点导论"
        )
        if not guide_path.is_file() or not guide_path.read_text(
            encoding="utf-8"
        ).startswith(expected_title + "\n"):
            report.error(
                "catalog_drift",
                f"{capability.get('id')} guide does not match registry",
                f"{capability.get('id')} 的导论与注册表不一致",
            )


def validate_relative_links(skill_dir: pathlib.Path, report: ValidationReport) -> None:
    for path in sorted(skill_dir.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(content):
            target = match.group("target").strip().strip("<>")
            if re.match(r"^(?:https?://|mailto:|#)", target):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = path.parent / target
            if not resolved.exists():
                line = content.count("\n", 0, match.start()) + 1
                relative = path.relative_to(skill_dir).as_posix()
                report.error(
                    "broken_link",
                    f"{relative}:{line} -> {target}",
                    f"{relative}:{line} 指向不存在的 {target}",
                )


def validate_analysis_contracts(skill_dir: pathlib.Path, report: ValidationReport) -> None:
    eir_path = skill_dir / "references" / "eir-schema.md"
    eir = eir_path.read_text(encoding="utf-8")
    for heading in EIR_HEADINGS:
        if heading not in eir:
            report.error(
                "eir_contract",
                f"missing heading {heading}",
                f"缺少标题 {heading}",
            )

    evaluation_path = skill_dir / "references" / "evaluation-governance.md"
    evaluation = evaluation_path.read_text(encoding="utf-8")
    for key in EVALUATION_KEYS:
        if not re.search(rf"(?m)^\s{{2}}{re.escape(key)}:\s*$", evaluation):
            report.error(
                "evaluation_contract",
                f"evaluation output missing {key}",
                f"评价输出缺少 {key}",
            )

    for path in sorted(skill_dir.rglob("*.md")):
        if path.name == "trace.md":
            continue
        content = path.read_text(encoding="utf-8")
        if has_bundled_trace_write(content):
            relative = path.relative_to(skill_dir).as_posix()
            report.error(
                "bundled_trace_write",
                f"{relative} writes normal-use Trace to bundled history",
                f"{relative} 将普通运行 Trace 写入 Skill 内置历史",
            )


def validate_navigation(skill_dir: pathlib.Path, report: ValidationReport) -> None:
    references = skill_dir / "references"
    for path in sorted(references.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        line_count = len(content.splitlines())
        has_navigation = "## Quick Navigation / 快速导航" in content
        relative = path.relative_to(skill_dir).as_posix()
        if line_count > 500 and not has_navigation:
            report.error(
                "missing_navigation",
                f"{relative} has {line_count} lines and no quick navigation",
                f"{relative} 有 {line_count} 行但缺少快速导航",
            )
        elif line_count > 100 and not has_navigation:
            report.warning(
                "missing_navigation",
                f"{relative} has {line_count} lines and no quick navigation",
                f"{relative} 有 {line_count} 行但缺少快速导航",
            )


def validate_skill(skill_dir: pathlib.Path) -> ValidationReport:
    skill_dir = pathlib.Path(skill_dir).resolve()
    report = ValidationReport()
    try:
        registry = load_registry(skill_dir)
    except (OSError, json.JSONDecodeError) as error:
        report.error(
            "registry_shape",
            f"cannot load registry: {error}",
            f"无法加载注册表：{error}",
        )
        return report

    validate_registry_shape(registry, skill_dir, report)
    validate_markdown_views(registry, skill_dir, report)
    validate_relative_links(skill_dir, report)
    validate_analysis_contracts(skill_dir, report)
    validate_navigation(skill_dir, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Harness Engineering Patterns / 校验 Harness 工程模式 Skill"
    )
    parser.add_argument(
        "skill_dir",
        nargs="?",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args(argv)
    report = validate_skill(args.skill_dir)

    for error in report.errors:
        print(f"ERROR / 错误: {error}")
    for warning in report.warnings:
        print(f"WARNING / 警告: {warning}")
    if report.errors:
        print(
            f"Validation failed / 校验失败: {len(report.errors)} error(s), "
            f"{len(report.warnings)} warning(s)"
        )
        return 1
    print(
        f"Validation passed / 校验通过: 0 errors, "
        f"{len(report.warnings)} warning(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
