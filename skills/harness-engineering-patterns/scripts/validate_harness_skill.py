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
BUNDLED_TRACE_WRITE = re.compile(
    r"(?is)\b(?:append|write|update|record)\b.{0,180}"
    r"references/patterns/<capability-key>/trace\.md"
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
    if not all(isinstance(items, list) for items in (capabilities, topologies, patterns, cells)):
        report.error(
            "registry_shape",
            "capabilities, topologies, patterns, and cells must be arrays",
            "capabilities、topologies、patterns 和 cells 必须是数组",
        )
        return

    expected_counts = (("capabilities", capabilities, 7), ("topologies", topologies, 6), ("cells", cells, 42))
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
    ):
        for duplicate in duplicate_values(records, "id"):
            report.error(
                code,
                f"duplicate {label} id {duplicate}",
                f"重复的 {label} ID {duplicate}",
            )

    allowed_values = registry.get("allowed_values", {})
    allowed_status = set(allowed_values.get("cell_status", []))
    allowed_maturity = set(allowed_values.get("maturity", []))
    pattern_ids = {pattern.get("id") for pattern in patterns}

    for cell in cells:
        cell_id = str(cell.get("id", "<missing>"))
        status = cell.get("status")
        maturity = cell.get("maturity")
        if status not in allowed_status or maturity not in allowed_maturity:
            report.error(
                "registry_shape",
                f"{cell_id} has invalid status or maturity",
                f"{cell_id} 的状态或成熟度无效",
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
            if not cell.get("source_kind") or not cell.get("source_name_en") and cell.get("source_kind") == "paper_v2":
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
        elif cell.get("pattern_ref") is not None:
            report.error(
                "registry_shape",
                f"{cell_id} extension candidate must not have a pattern id",
                f"{cell_id} 扩展候选不得拥有模式 ID",
            )


def validate_markdown_views(
    registry: dict[str, object],
    skill_dir: pathlib.Path,
    report: ValidationReport,
) -> None:
    matrix = (skill_dir / "references" / "matrix-index.md").read_text(encoding="utf-8")
    catalog = (skill_dir / "references" / "pattern-catalog.md").read_text(encoding="utf-8")

    for cell in registry.get("cells", []):
        design_relative = str(cell.get("design_path", "")).removeprefix("references/")
        local_name_en = str(cell.get("local_name_en", ""))
        cell_key = str(cell.get("cell_key", ""))
        if f"]({design_relative})" not in matrix or local_name_en not in matrix:
            report.error(
                "matrix_drift",
                f"{cell_key} does not match matrix-index.md",
                f"{cell_key} 与 matrix-index.md 不一致",
            )
        if cell_key not in catalog:
            report.error(
                "catalog_drift",
                f"{cell_key} is missing from pattern-catalog.md",
                f"pattern-catalog.md 缺少 {cell_key}",
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

    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if BUNDLED_TRACE_WRITE.search(skill_text):
        report.error(
            "bundled_trace_write",
            "normal-use guidance writes to bundled trace history",
            "普通使用说明会写入 Skill 内置 Trace 历史",
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
