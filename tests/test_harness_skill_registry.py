import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "harness-engineering-patterns"
REGISTRY = SKILL_DIR / "references" / "registry.json"


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


if __name__ == "__main__":
    unittest.main()
