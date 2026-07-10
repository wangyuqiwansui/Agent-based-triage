import contextlib
import importlib.util
import json
import pathlib
import shutil
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "harness-engineering-patterns"
REGISTRY = SKILL_DIR / "references" / "registry.json"
VALIDATOR = SKILL_DIR / "scripts" / "validate_harness_skill.py"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_harness_skill",
        VALIDATOR,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def copied_skill():
    with tempfile.TemporaryDirectory() as temporary_directory:
        target = pathlib.Path(temporary_directory) / SKILL_DIR.name
        shutil.copytree(SKILL_DIR, target)
        yield target


def read_registry(skill_dir):
    path = skill_dir / "references" / "registry.json"
    return json.loads(path.read_text(encoding="utf-8"))


def write_registry(skill_dir, registry):
    path = skill_dir / "references" / "registry.json"
    path.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class HarnessSkillRegistryTest(unittest.TestCase):
    def load_registry(self):
        return json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registry_covers_axes_cells_and_provenance(self):
        registry = self.load_registry()

        self.assertEqual(registry["schema_version"], "1.0.0")
        self.assertEqual(len(registry["capabilities"]), 7)
        self.assertEqual(len(registry["topologies"]), 6)
        self.assertEqual(len(registry["cells"]), 42)
        self.assertEqual(
            sum(cell["status"] == "named" for cell in registry["cells"]),
            30,
        )
        self.assertEqual(
            sum(
                cell["status"] == "extension_candidate"
                for cell in registry["cells"]
            ),
            12,
        )
        self.assertEqual(registry["upstream_sources"][0]["version"], "v2")

        for cell in registry["cells"]:
            self.assertRegex(cell["id"], r"^CELL_[A-Z]+_[A-Z]+$")
            self.assertIn(
                cell["maturity"],
                {"seed", "draft", "validated", "operational"},
            )
            self.assertTrue((SKILL_DIR / cell["design_path"]).is_file())
            self.assertTrue(
                (SKILL_DIR / cell["observability_path"]).is_file()
            )
            if cell["status"] == "named":
                self.assertRegex(cell["pattern_ref"], r"^PATTERN_\d{4}$")
                self.assertIn(
                    cell["source_kind"],
                    {"paper_v2", "local_extension"},
                )
            else:
                self.assertIsNone(cell["pattern_ref"])

    def test_real_skill_has_no_registry_structure_errors(self):
        validator = load_validator()
        report = validator.validate_skill(SKILL_DIR)
        structural_codes = {
            "registry_shape",
            "duplicate_capability_id",
            "duplicate_topology_id",
            "duplicate_pattern_id",
            "duplicate_cell_id",
            "missing_design_file",
            "missing_observability_file",
            "missing_provenance",
        }

        self.assertFalse(
            [
                error
                for error in report.errors
                if error.split(":", 1)[0] in structural_codes
            ]
        )

    def test_duplicate_pattern_id_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            registry["patterns"][1]["id"] = registry["patterns"][0]["id"]
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("duplicate_pattern_id" in error for error in report.errors)
        )

    def test_missing_design_file_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            target = skill_dir / registry["cells"][0]["design_path"]
            target.unlink()

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("missing_design_file" in error for error in report.errors)
        )

    def test_wrong_cell_status_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            registry["cells"][0]["status"] = "unknown"
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("registry_shape" in error for error in report.errors))

    def test_missing_named_cell_provenance_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            registry["cells"][0]["source_kind"] = ""
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("missing_provenance" in error for error in report.errors)
        )

    def test_missing_required_design_field_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            target = skill_dir / registry["cells"][0]["design_path"]
            content = target.read_text(encoding="utf-8")
            target.write_text(
                content.replace("状态 / Status", "状态"),
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("missing_design_field" in error for error in report.errors)
        )

    def test_broken_relative_markdown_link_fails(self):
        with copied_skill() as skill_dir:
            skill_path = skill_dir / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8")
                + "\n[Broken / 断链](references/not-present.md)\n",
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("broken_link" in error for error in report.errors))

    def test_default_bundled_trace_write_instruction_fails(self):
        with copied_skill() as skill_dir:
            skill_path = skill_dir / "SKILL.md"
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8")
                + "\nAlways append to references/patterns/<capability-key>/trace.md.\n",
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("bundled_trace_write" in error for error in report.errors)
        )

    def test_skill_has_bounded_output_and_project_local_trace_contracts(self):
        validator = load_validator()
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("When Not To Use / 不适用场景", skill)
        self.assertIn("Output Profiles / 输出档位", skill)
        self.assertIn("quick / 快速", skill)
        self.assertIn("standard / 标准", skill)
        self.assertIn("full / 完整", skill)
        self.assertIn("preliminary / 初步", skill)
        self.assertIn("references/trace-schema.md", skill)
        self.assertIn(".harness-analysis/<analysis_id>/trace.yaml", skill)
        self.assertIsNone(validator.BUNDLED_TRACE_WRITE.search(skill))

    def test_eir_schema_covers_every_declared_collection(self):
        eir = (SKILL_DIR / "references" / "eir-schema.md").read_text(
            encoding="utf-8"
        )
        required_headings = [
            "## Control Flow / 控制流",
            "## State Flow / 状态流",
            "## Tool Flow / 工具流",
            "## Permission Flow / 权限流",
            "## Pattern Record / 模式记录",
            "## Skill Recommendation / Skill 建议",
            "## Evaluation Reference / 评价引用",
            "## Governance Item / 治理项",
        ]

        for heading in required_headings:
            self.assertIn(heading, eir)
        for prefix in (
            "ANALYSIS_",
            "MAP_",
            "EVAL_",
            "GOV_",
            "FAIL_",
            "PROBE_",
        ):
            self.assertIn(prefix, eir)

    def test_evaluation_output_has_seven_operational_dimensions(self):
        evaluation = (
            SKILL_DIR / "references" / "evaluation-governance.md"
        ).read_text(encoding="utf-8")
        for key in (
            "coverage",
            "mapping_accuracy",
            "evidence",
            "reuse",
            "skill_readiness",
            "governance",
            "evaluability",
        ):
            self.assertRegex(evaluation, rf"(?m)^  {key}:$")
        for field in (
            "rubric:",
            "direction:",
            "evidence_sources:",
            "observation_window:",
            "score:",
            "confidence:",
            "notes:",
        ):
            self.assertGreaterEqual(evaluation.count(f"    {field}"), 7)

    def test_every_design_file_has_the_full_pattern_template(self):
        validator = load_validator()
        registry = read_registry(SKILL_DIR)

        for cell in registry["cells"]:
            content = (SKILL_DIR / cell["design_path"]).read_text(
                encoding="utf-8"
            )
            for field in validator.DESIGN_FIELDS:
                self.assertIn(field, content, f"{cell['cell_key']}: {field}")

    def test_source_aliases_and_harness_spelling_are_explicit(self):
        memory_loop = (
            SKILL_DIR / "references" / "patterns" / "memory" / "memory-loop.md"
        ).read_text(encoding="utf-8")
        catalog = (SKILL_DIR / "references" / "pattern-catalog.md").read_text(
            encoding="utf-8"
        )
        matrix = (SKILL_DIR / "references" / "matrix-index.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Failure Journal / 失败日志", memory_loop)
        self.assertIn("Failure Diary / 失败日记", memory_loop)
        for content in (catalog, matrix):
            self.assertIn("28 upstream named patterns / 上游 28 个命名模式", content)
            self.assertIn("two local promotions / 2 个本地晋升模式", content)

        for path in SKILL_DIR.rglob("*.md"):
            self.assertNotIn(
                "Hanerss",
                path.read_text(encoding="utf-8"),
                str(path),
            )

    def test_trace_schema_is_bilingual_and_project_scoped(self):
        trace_schema = SKILL_DIR / "references" / "trace-schema.md"
        content = trace_schema.read_text(encoding="utf-8")

        self.assertIn("Runtime Trace Contract / 运行 Trace 契约", content)
        self.assertIn(".harness-analysis/<analysis_id>/trace.yaml", content)
        for field in (
            "analysis_id",
            "project_scope",
            "tenant_scope",
            "sensitivity",
            "source_revision",
            "evidence_refs",
            "validity",
            "retention",
            "expires_at",
            "owner",
        ):
            self.assertIn(field, content)

    def test_design_trace_hooks_are_project_local(self):
        registry = read_registry(SKILL_DIR)

        for cell in registry["cells"]:
            content = (SKILL_DIR / cell["design_path"]).read_text(
                encoding="utf-8"
            )
            self.assertNotIn(
                "add an entry to [trace.md](trace.md)",
                content,
                cell["cell_key"],
            )
            self.assertIn(
                ".harness-analysis/<analysis_id>/trace.yaml",
                content,
                cell["cell_key"],
            )

    def test_references_over_500_lines_have_quick_navigation(self):
        for path in SKILL_DIR.joinpath("references").rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            if len(content.splitlines()) > 500:
                self.assertIn(
                    "## Quick Navigation / 快速导航",
                    content,
                    str(path),
                )

    def test_real_skill_passes_full_validation(self):
        report = load_validator().validate_skill(SKILL_DIR)
        self.assertEqual(report.errors, [])


if __name__ == "__main__":
    unittest.main()
