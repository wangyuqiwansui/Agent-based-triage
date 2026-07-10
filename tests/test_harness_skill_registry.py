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


if __name__ == "__main__":
    unittest.main()
