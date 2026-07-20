import contextlib
import importlib.util
import json
import pathlib
import re
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

    def test_duplicate_registry_coordinate_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            registry["cells"][1]["coordinate"] = registry["cells"][0]["coordinate"]
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("registry_shape" in error for error in report.errors))

    def test_unknown_axis_reference_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            registry["cells"][0]["capability_ref"] = "COG_UNKNOWN"
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("registry_shape" in error for error in report.errors))

    def test_invalid_source_kind_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            registry["cells"][0]["source_kind"] = "invented_source"
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("registry_shape" in error for error in report.errors))

    def test_upstream_provenance_count_drift_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            registry["upstream_sources"][0]["named_pattern_count"] = 27
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("registry_shape" in error for error in report.errors))

    def test_maturity_requirements_are_explicit(self):
        requirements = self.load_registry()["maturity_requirements"]

        self.assertEqual(requirements["validated"]["minimum_independent_cases"], 2)
        self.assertTrue(requirements["validated"]["failure_path_check_required"])
        self.assertTrue(requirements["operational"]["recurring_monitoring_required"])
        self.assertTrue(requirements["operational"]["owned_thresholds_required"])

    def test_validated_maturity_requires_failure_path_check(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            cell = registry["cells"][0]
            cell["maturity"] = "validated"
            cell["local_evidence_count"] = 2
            cell["independent_case_count"] = 2
            cell["failure_path_checked"] = False
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("registry_shape" in error for error in report.errors))

    def test_operational_maturity_requires_monitoring_owner(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            cell = registry["cells"][0]
            cell["maturity"] = "operational"
            cell["local_evidence_count"] = 2
            cell["independent_case_count"] = 2
            cell["failure_path_checked"] = True
            cell["recurring_monitoring"] = False
            cell["threshold_owner"] = ""
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("registry_shape" in error for error in report.errors))

    def test_registry_declares_governance_and_failure_references(self):
        registry = self.load_registry()

        self.assertGreaterEqual(len(registry["governance_rules"]), 3)
        self.assertEqual(
            {item["id"] for item in registry["failure_mode_refs"]},
            {f"FAIL_{number:04d}" for number in range(1, 17)},
        )

    def test_runtime_protocols_preserve_existing_ids_and_use_new_ids(self):
        registry = self.load_registry()
        patterns = {pattern["id"]: pattern for pattern in registry["patterns"]}

        self.assertEqual(patterns["PATTERN_0001"]["name_en"], "Main Loop Progression")
        self.assertEqual(patterns["PATTERN_0002"]["name_en"], "Context Assembly")
        self.assertEqual(
            patterns["PATTERN_0051"]["reference"],
            "references/reasoning-execution-flow.md",
        )
        self.assertEqual(patterns["PATTERN_0051"]["source_draft_id"], "PATTERN_0001")
        self.assertEqual(patterns["PATTERN_0051"]["source_version"], "0.2.0")
        self.assertIn(
            "COG_REASONING__TOP_ORCHESTRATION",
            patterns["PATTERN_0051"]["matrix_coordinates"],
        )
        self.assertEqual(
            patterns["PATTERN_0052"]["reference"],
            "references/workflow-observability-probes.md",
        )
        self.assertEqual(patterns["PATTERN_0052"]["source_draft_id"], "PATTERN_0002")
        self.assertEqual(patterns["PATTERN_0052"]["source_version"], "0.4.0")
        self.assertIn(
            "COG_GOVERNANCE__TOP_ORCHESTRATION",
            patterns["PATTERN_0052"]["matrix_coordinates"],
        )

    def test_runtime_protocols_are_bilingual_and_complete(self):
        validator = load_validator()
        execution = (
            SKILL_DIR / "references" / "reasoning-execution-flow.md"
        ).read_text(encoding="utf-8")
        probes = (
            SKILL_DIR / "references" / "workflow-observability-probes.md"
        ).read_text(encoding="utf-8")

        for marker in validator.EXECUTION_CONTRACT_MARKERS:
            self.assertIn(marker, execution)
        for marker in validator.OBSERVABILITY_CONTRACT_MARKERS:
            self.assertIn(marker, probes)
        self.assertEqual(
            set(validator.REQUIRED_PROBES),
            set(re.findall(r"PROBE_\d{4}", probes)),
        )
        for relative in validator.RUNTIME_SCHEMA_FILES:
            self.assertTrue((SKILL_DIR / relative).is_file(), relative)
        for relative in validator.RUNTIME_IMPLEMENTATION_FILES:
            self.assertTrue((SKILL_DIR / relative).is_file(), relative)

    def test_every_reasoning_cell_links_shared_runtime_protocols(self):
        registry = self.load_registry()

        for cell in registry["cells"]:
            if cell["capability_ref"] != "COG_REASONING":
                continue
            design = (SKILL_DIR / cell["design_path"]).read_text(encoding="utf-8")
            observability = (SKILL_DIR / cell["observability_path"]).read_text(
                encoding="utf-8"
            )
            self.assertIn("../../reasoning-execution-flow.md", design)
            self.assertIn("../../workflow-observability-probes.md", design)
            self.assertIn("../../workflow-observability-probes.md", observability)

    def test_missing_stable_probe_fails_runtime_validation(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "references" / "workflow-observability-probes.md"
            content = target.read_text(encoding="utf-8")
            target.write_text(
                content.replace("`PROBE_0008`", "`MISSING_PROBE`"),
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("observability_probe_catalog" in error for error in report.errors)
        )

    def test_budget_table_column_drift_fails_runtime_validation(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "references" / "reasoning-execution-flow.md"
            content = target.read_text(encoding="utf-8")
            target.write_text(
                content.replace(
                    "| standard / 标准 | 8,000 | 12 s | 4 | 8 | 3 | 6 |",
                    "| standard / 标准 | 8,000 | 12 s | 4 | 8 | 3 |",
                ),
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("reasoning_budget_table" in error for error in report.errors))

    def test_budget_table_rejects_every_nonpositive_numeric_dimension(self):
        validator = load_validator()
        execution = (
            SKILL_DIR / "references" / "reasoning-execution-flow.md"
        ).read_text(encoding="utf-8")
        rows = validator.markdown_table_rows(execution, "| Profile / 档位")
        light_row = rows[2]
        original = "| " + " | ".join(light_row) + " |"
        invalid_values = {
            1: "0",
            2: "0 s",
            3: "0",
            4: "0",
            5: "0",
            6: "0",
        }

        for column, invalid_value in invalid_values.items():
            with self.subTest(column=column):
                mutated_row = list(light_row)
                mutated_row[column] = invalid_value
                mutated = "| " + " | ".join(mutated_row) + " |"
                report = validator.ValidationReport()
                validator.validate_budget_profile_table(
                    execution.replace(original, mutated, 1), report
                )
                self.assertTrue(
                    any("reasoning_budget_table" in error for error in report.errors)
                )

    def test_schema_enum_drift_fails_runtime_validation(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "schemas" / "reasoning-event.schema.json"
            schema = json.loads(target.read_text(encoding="utf-8"))
            schema["$defs"]["WorkflowState"]["enum"].remove("cancelled")
            target.write_text(
                json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("reasoning_schema_enums" in error for error in report.errors))

    def test_invalid_draft_202012_schema_fails_runtime_validation(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "schemas" / "reasoning-result.schema.json"
            schema = json.loads(target.read_text(encoding="utf-8"))
            schema["type"] = 7
            target.write_text(
                json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_reasoning_schemas(skill_dir, report)

        self.assertTrue(any("reasoning_schema" in error for error in report.errors))

    def test_result_validation_enum_drift_fails_runtime_validation(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "schemas" / "reasoning-result.schema.json"
            schema = json.loads(target.read_text(encoding="utf-8"))
            schema["$defs"]["ValidationOutcome"]["enum"].remove("timed_out")
            target.write_text(
                json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_reasoning_schemas(skill_dir, report)

        self.assertTrue(any("reasoning_schema_enums" in error for error in report.errors))

    def test_missing_mode_probe_dependency_fails_runtime_validation(self):
        with copied_skill() as skill_dir:
            target = (
                skill_dir
                / "references"
                / "patterns"
                / "reasoning"
                / "reasoning-routing-observability.md"
            )
            content = target.read_text(encoding="utf-8")
            target.write_text(
                content.replace("PROBE_0005", "MISSING_STEP_PROBE"),
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("reasoning_probe_dependencies" in error for error in report.errors)
        )

    def test_dependency_matrix_rejects_baseline_overlap_and_nonbilingual_condition(self):
        mutations = {
            "missing_baseline": lambda entry: entry.update(
                required_probes=["PROBE_0001", "PROBE_0014", "PROBE_0015"]
            ),
            "required_conditional_overlap": lambda entry: entry[
                "conditional_probes"
            ].update({"PROBE_0001": "always / 始终"}),
            "nonbilingual_condition": lambda entry: entry[
                "conditional_probes"
            ].update({"PROBE_0013": "outcome only"}),
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name), copied_skill() as skill_dir:
                target = skill_dir / "runtime" / "probe_dependency_matrix.json"
                matrix = json.loads(target.read_text(encoding="utf-8"))
                chain = next(
                    entry for entry in matrix["entries"] if entry["mode"] == "chain"
                )
                mutation(chain)
                target.write_text(
                    json.dumps(matrix, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                validator = load_validator()
                report = validator.ValidationReport()
                validator.validate_probe_dependency_matrix(skill_dir, report)
                self.assertTrue(
                    any(
                        "reasoning_probe_dependencies" in error
                        for error in report.errors
                    )
                )

    def test_dependency_matrix_malformed_probe_array_reports_instead_of_crashing(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "probe_dependency_matrix.json"
            matrix = json.loads(target.read_text(encoding="utf-8"))
            matrix["entries"][0]["required_probes"] = [
                {"id": "PROBE_0001"}
            ]
            target.write_text(
                json.dumps(matrix, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_probe_dependency_matrix(skill_dir, report)

        self.assertTrue(
            any("reasoning_probe_dependencies" in error for error in report.errors)
        )

    def test_probe_registry_rejects_missing_versioned_deployable_definition(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "probe_registry.json"
            registry = json.loads(target.read_text(encoding="utf-8"))
            registry["probes"][0].pop("version")
            target.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_probe_registry(skill_dir, report)

        self.assertTrue(
            any("reasoning_probe_registry" in error for error in report.errors)
        )

    def test_probe_catalog_id_in_prose_cannot_replace_first_column_record(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "references" / "workflow-observability-probes.md"
            content = target.read_text(encoding="utf-8")
            content = content.replace(
                "| `PROBE_0008` Parallel Path / 并行路径 |",
                "| `MISSING_PROBE` Parallel Path / 并行路径 |",
                1,
            )
            content = content.replace(
                "Every applicable probe must declare",
                "A prose cross-reference mentions PROBE_0008. / 正文交叉引用 PROBE_0008。\n\n"
                "Every applicable probe must declare",
                1,
            )
            target.write_text(content, encoding="utf-8")

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("observability_probe_catalog" in error for error in report.errors)
        )

    def test_stale_metric_formula_fails_runtime_validation(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "references" / "workflow-observability-probes.md"
            content = target.read_text(encoding="utf-8")
            target.write_text(
                content.replace("route_stability_rate =", "first_route_hit_rate ="),
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("reasoning_metric_semantics" in error for error in report.errors)
        )

    def test_metric_registry_rejects_invalid_metadata_and_metric_semantics(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "metric_registry.json"
            registry = json.loads(target.read_text(encoding="utf-8"))
            registry["schema_version"] = "999.0.0"
            metric = next(
                record
                for record in registry["metrics"]
                if record["metric_id"] == "false_release_rate"
            )
            metric["formula"] = ""
            metric["minimum_sample"] = 0
            metric["required_probes"] = []
            target.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_metric_registry(skill_dir, report)

        self.assertTrue(
            any("reasoning_metric_registry" in error for error in report.errors)
        )

    def test_metric_registry_malformed_probe_array_reports_instead_of_crashing(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "metric_registry.json"
            registry = json.loads(target.read_text(encoding="utf-8"))
            registry["metrics"][0]["required_probes"] = [
                {"id": "PROBE_0001"}
            ]
            target.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_metric_registry(skill_dir, report)

        self.assertTrue(
            any("reasoning_metric_registry" in error for error in report.errors)
        )

    def test_metric_registry_rejects_invalid_inputs_and_mvp_coverage(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "metric_registry.json"
            registry = json.loads(target.read_text(encoding="utf-8"))
            registry["metrics"][0]["inputs"] = ["invalid-input"]
            registry["coverage"]["implemented"] = ["not_a_registered_metric"]
            target.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_metric_registry(skill_dir, report)

        matching_errors = [
            error
            for error in report.errors
            if "reasoning_metric_registry" in error
        ]
        self.assertGreaterEqual(len(matching_errors), 2)

    def test_outcome_metric_requires_outcome_probe(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "metric_registry.json"
            registry = json.loads(target.read_text(encoding="utf-8"))
            metric = next(
                record
                for record in registry["metrics"]
                if record["metric_id"] == "outcome_route_accuracy"
            )
            metric["required_probes"].remove("PROBE_0013")
            target.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_metric_registry(skill_dir, report)

        self.assertTrue(
            any("must require PROBE_0013" in error for error in report.errors)
        )

    def test_missing_reference_runtime_fails_runtime_validation(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "reasoning_runtime.py"
            target.unlink()

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("reasoning_runtime_implementation" in error for error in report.errors)
        )

    def test_runtime_import_smoke_rejects_import_failure(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "reasoning_runtime.py"
            target.write_text(
                target.read_text(encoding="utf-8")
                + "\nraise RuntimeError('import smoke sentinel')\n",
                encoding="utf-8",
            )
            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_runtime_imports(skill_dir, report)

        self.assertTrue(
            any("reasoning_runtime_import" in error for error in report.errors)
        )

    def test_runtime_import_smoke_requires_public_exports(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "__init__.py"
            target.write_text(
                '"""Empty smoke-test package / 空冒烟测试包。"""\n\n__all__ = []\n',
                encoding="utf-8",
            )
            validator = load_validator()
            report = validator.ValidationReport()
            validator.validate_runtime_imports(skill_dir, report)

        self.assertTrue(
            any("lacks required exports" in error for error in report.errors)
        )

    def test_runtime_enum_drift_from_schema_fails(self):
        with copied_skill() as skill_dir:
            target = skill_dir / "runtime" / "reasoning_router.py"
            content = target.read_text(encoding="utf-8")
            target.write_text(
                content.replace('CHAIN = "chain"', 'CHAIN = "chain_v2"', 1),
                encoding="utf-8",
            )
            validator = load_validator()
            report = validator.ValidationReport()
            schemas = validator.validate_reasoning_schemas(skill_dir, report)
            modules = validator.validate_runtime_imports(skill_dir, report)
            validator.validate_runtime_schema_enums(modules, schemas, report)

        self.assertTrue(
            any("reasoning_runtime_schema_enums" in error for error in report.errors)
        )

    def test_missing_governance_references_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            registry.pop("governance_rules", None)
            write_registry(skill_dir, registry)

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("registry_shape" in error for error in report.errors))

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

    def test_path_first_bundled_trace_write_instruction_fails(self):
        with copied_skill() as skill_dir:
            matrix = skill_dir / "references" / "matrix-index.md"
            matrix.write_text(
                matrix.read_text(encoding="utf-8")
                + "\nUse `references/patterns/<capability-key>/trace.md` "
                "to record outcomes. / 使用该内置路径记录结果。\n",
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(
            any("bundled_trace_write" in error for error in report.errors)
        )

    def test_matrix_labels_are_compared_per_cell(self):
        with copied_skill() as skill_dir:
            matrix = skill_dir / "references" / "matrix-index.md"
            content = matrix.read_text(encoding="utf-8")
            first = "[Semantic Compaction / 语义压缩](patterns/perception/perception-chain.md)"
            second = "[Context Triage / 上下文分诊](patterns/perception/perception-routing.md)"
            content = content.replace(first, "__FIRST__").replace(
                second,
                f"[Semantic Compaction / 语义压缩](patterns/perception/perception-routing.md)",
            ).replace(
                "__FIRST__",
                "[Context Triage / 上下文分诊](patterns/perception/perception-chain.md)",
            )
            matrix.write_text(content, encoding="utf-8")

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("matrix_drift" in error for error in report.errors))

    def test_stale_design_header_fails(self):
        with copied_skill() as skill_dir:
            registry = read_registry(skill_dir)
            target = skill_dir / registry["cells"][0]["design_path"]
            content = target.read_text(encoding="utf-8")
            target.write_text(
                content.replace(
                    "# Semantic Compaction / 语义压缩",
                    "# Stale Pattern / 过期模式",
                    1,
                ),
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("catalog_drift" in error for error in report.errors))

    def test_stale_guide_row_fails(self):
        with copied_skill() as skill_dir:
            guide = skill_dir / "references" / "patterns" / "perception" / "cell.md"
            content = guide.read_text(encoding="utf-8")
            guide.write_text(
                content.replace(
                    "[Semantic Compaction / 语义压缩](perception-chain.md)",
                    "[Context Triage / 上下文分诊](perception-chain.md)",
                    1,
                ),
                encoding="utf-8",
            )

            report = load_validator().validate_skill(skill_dir)

        self.assertTrue(any("catalog_drift" in error for error in report.errors))

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
