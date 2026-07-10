# Harness Engineering Patterns Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `harness-engineering-patterns` registry-backed, deterministically validated, provenance-aware, trace-safe, and contract-complete without breaking its existing 42-cell Markdown layout.

**Architecture:** Add a standard-library JSON registry as the structural source of truth and a read-only validator inside the Skill. Keep Markdown as the detailed human-readable view, verify it against the registry, and migrate the existing HTML generator to registry-backed axes and cells. Repair Skill guidance and schemas with focused contract tests before each edit.

**Tech Stack:** Python 3 standard library (`json`, `pathlib`, `unittest`, `tempfile`, `shutil`), Markdown, JSON, PowerShell test commands.

## Global Constraints

- Preserve bilingual Chinese and English metadata and core Skill instructions.
- Keep all new Skill resources under `skills/harness-engineering-patterns`.
- Preserve all existing public Markdown paths and `PATTERN_0001` through `PATTERN_0022`.
- Do not edit `skills/harness-engineering-patterns/references/patterns/memory/trace.md`.
- Do not edit or delete `tests/__pycache__`.
- Use Python with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1` during tests.
- Do not add third-party dependencies, push, or create a pull request.
- Use RED-GREEN-REFACTOR for every behavior or Skill contract change.

---

### Task 1: Registry Contract And Authoritative Data

**Files:**
- Create: `tests/test_harness_skill_registry.py`
- Create: `skills/harness-engineering-patterns/references/registry.json`

**Interfaces:**
- Consumes: existing axes, matrix index, pattern catalog, pattern seed table, and pattern file paths.
- Produces: JSON object with `schema_version`, `skill`, `upstream_sources`, `capabilities`, `topologies`, `patterns`, `cells`, `allowed_values`, and `existing_id_floor`.

- [ ] **Step 1: Write the failing registry shape test**

```python
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
        self.assertEqual(sum(cell["status"] == "named" for cell in registry["cells"]), 30)
        self.assertEqual(sum(cell["status"] == "extension_candidate" for cell in registry["cells"]), 12)
        self.assertEqual(registry["upstream_sources"][0]["version"], "v2")
        for cell in registry["cells"]:
            self.assertRegex(cell["id"], r"^CELL_[A-Z]+_[A-Z]+$")
            self.assertIn(cell["maturity"], {"seed", "draft", "validated", "operational"})
            self.assertTrue((SKILL_DIR / cell["design_path"]).is_file())
            self.assertTrue((SKILL_DIR / cell["observability_path"]).is_file())
            if cell["status"] == "named":
                self.assertRegex(cell["pattern_ref"], r"^PATTERN_\d{4}$")
                self.assertIn(cell["source_kind"], {"paper_v2", "local_extension"})
            else:
                self.assertIsNone(cell["pattern_ref"])
```

- [ ] **Step 2: Run the registry test and verify RED**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python -m unittest tests.test_harness_skill_registry.HarnessSkillRegistryTest.test_registry_covers_axes_cells_and_provenance -v
```

Expected: ERROR with `FileNotFoundError` for `references/registry.json`.

- [ ] **Step 3: Add the complete registry**

Use these stable IDs:

```text
COG_PERCEPTION, COG_MEMORY, COG_REASONING, COG_ACTION,
COG_REFLECTION, COG_COLLABORATION, COG_GOVERNANCE

TOP_CHAIN, TOP_ROUTING, TOP_PARALLEL, TOP_ORCHESTRATION,
TOP_LOOP, TOP_HIERARCHY
```

Preserve `PATTERN_0001` through `PATTERN_0022`. Reuse `PATTERN_0021` for Multi-Modal Fusion and `PATTERN_0022` for Layered Retention. Assign matrix patterns as follows:

```text
PATTERN_0023 Semantic Compaction
PATTERN_0024 Context Triage
PATTERN_0025 Progressive Disclosure
PATTERN_0026 Progressive Discovery
PATTERN_0027 RAG Pipeline
PATTERN_0028 Hierarchical Retrieval
PATTERN_0029 Progress Tracking
PATTERN_0030 Failure Journal (local alias: Failure Diary)
PATTERN_0031 Chain-of-Thought
PATTERN_0032 Complexity-Based Routing
PATTERN_0033 Parallel Exploration
PATTERN_0034 Iterative Hypothesis Testing
PATTERN_0035 Prompt Chaining
PATTERN_0036 Tool Dispatch
PATTERN_0037 Plan-and-Execute
PATTERN_0038 Guardrail Sandwich
PATTERN_0039 Generator-Critic
PATTERN_0040 Skill Package
PATTERN_0041 Self-Heal Loop
PATTERN_0042 Experience Replay
PATTERN_0043 Handoff Chain
PATTERN_0044 Fan-Out/Gather
PATTERN_0045 Adversarial Review
PATTERN_0046 Hierarchical Delegation
PATTERN_0047 Approval Gate
PATTERN_0048 Progressive Commitment
PATTERN_0049 Observability Harness
PATTERN_0050 Blast Radius Control
```

Every cell uses `CELL_<CAPABILITY>_<TOPOLOGY>`, `COG_*__TOP_*`, existing design and observability paths, bilingual local names and diagnostic use, `draft` maturity for named patterns, and `seed` maturity for extension candidates. Record paper v2 as 28 upstream named patterns and 14 upstream blank cells; mark Progressive Discovery and Layered Retention as `local_extension`.

- [ ] **Step 4: Run the registry test and verify GREEN**

Run the Step 2 command. Expected: `OK`, 1 test.

- [ ] **Step 5: Run the existing suite**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python -m unittest tests.test_generate_skill_visualization tests.test_harness_skill_registry -v
```

Expected: 17 tests, 0 failures.

- [ ] **Step 6: Commit Task 1**

```powershell
git add -- tests/test_harness_skill_registry.py skills/harness-engineering-patterns/references/registry.json
git commit -m "feat(harness): 添加权威模式注册表"
```

---

### Task 2: Read-Only Registry Validator

**Files:**
- Modify: `tests/test_harness_skill_registry.py`
- Create: `skills/harness-engineering-patterns/scripts/validate_harness_skill.py`

**Interfaces:**
- Consumes: `pathlib.Path` to a Skill directory.
- Produces: `ValidationReport(errors: list[str], warnings: list[str])`, `validate_skill(skill_dir)`, and CLI exit 0/1.

- [ ] **Step 1: Write failing validator tests**

Add tests that import the validator with `importlib.util`, verify the real Skill has no registry-structure errors, and copy the Skill to a temporary directory for negative cases. Required assertions:

```python
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
        [error for error in report.errors if error.split(":", 1)[0] in structural_codes]
    )

def test_duplicate_pattern_id_fails(self):
    with copied_skill() as skill_dir:
        registry = read_registry(skill_dir)
        registry["patterns"][1]["id"] = registry["patterns"][0]["id"]
        write_registry(skill_dir, registry)
        report = load_validator().validate_skill(skill_dir)
        self.assertTrue(any("duplicate_pattern_id" in error for error in report.errors))

def test_missing_design_file_fails(self):
    with copied_skill() as skill_dir:
        target = skill_dir / read_registry(skill_dir)["cells"][0]["design_path"]
        target.unlink()
        report = load_validator().validate_skill(skill_dir)
        self.assertTrue(any("missing_design_file" in error for error in report.errors))
```

Also cover wrong status, missing provenance, missing required design field, broken relative link, and a default-write instruction targeting `references/patterns/<capability>/trace.md` in `SKILL.md`.

- [ ] **Step 2: Run validator tests and verify RED**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python -m unittest tests.test_harness_skill_registry -v
```

Expected: ERROR because `scripts/validate_harness_skill.py` does not exist.

- [ ] **Step 3: Implement the minimal validator**

Implement:

```python
@dataclasses.dataclass
class ValidationReport:
    errors: list[str] = dataclasses.field(default_factory=list)
    warnings: list[str] = dataclasses.field(default_factory=list)


def load_registry(skill_dir: pathlib.Path) -> dict[str, object]:
    return json.loads((skill_dir / "references" / "registry.json").read_text(encoding="utf-8"))


def validate_skill(skill_dir: pathlib.Path) -> ValidationReport:
    # Run registry shape, ID, path-pair, Markdown contract, link,
    # provenance, EIR/evaluation, trace-boundary, and navigation checks.
    return report


def main(argv: list[str] | None = None) -> int:
    # Print bilingual ERROR/WARNING lines and return 1 only for errors.
```

Use stable error codes in every message: `registry_shape`, `duplicate_*_id`, `missing_*_file`, `matrix_drift`, `catalog_drift`, `missing_provenance`, `missing_design_field`, `missing_observability_field`, `broken_link`, `eir_contract`, `evaluation_contract`, and `bundled_trace_write`.

Treat missing navigation in files over 500 lines as an error and in files from 101 through 500 lines as a warning.

- [ ] **Step 4: Run validator tests and verify GREEN**

Run the Step 2 command. Expected: all validator tests pass. The real Skill may still report document-contract and navigation errors that are intentionally repaired in Tasks 4 and 5.

- [ ] **Step 5: Run the validator CLI**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python skills/harness-engineering-patterns/scripts/validate_harness_skill.py skills/harness-engineering-patterns
```

Expected at this stage: non-zero with errors for known document-contract gaps. Record the exact errors; Task 4 and Task 5 remove them.

- [ ] **Step 6: Commit Task 2**

```powershell
git add -- tests/test_harness_skill_registry.py skills/harness-engineering-patterns/scripts/validate_harness_skill.py
git commit -m "test(harness): 添加注册表一致性校验"
```

---

### Task 3: Registry-Backed Visualization

**Files:**
- Modify: `tests/test_generate_skill_visualization.py`
- Modify: `scripts/generate_skill_visualization.py`
- Modify: `harness-engineering-patterns.html`

**Interfaces:**
- Consumes: `references/registry.json` plus existing Markdown details.
- Produces: the existing `load_skill_data()` shape with added `provenance`, `maturity`, and registry-backed source hash.

- [ ] **Step 1: Write failing visualization assertions**

Extend `test_loads_axes_matrix_and_pattern_counts`:

```python
self.assertEqual(data["matrix"][0]["id"], "CELL_PERCEPTION_CHAIN")
self.assertEqual(data["matrix"][0]["pattern_ref"], "PATTERN_0023")
self.assertEqual(data["matrix"][0]["source_kind"], "paper_v2")
self.assertEqual(data["matrix"][0]["maturity"], "draft")
self.assertIn(SKILL_DIR / "references" / "registry.json", generator.source_files(SKILL_DIR))
```

Extend HTML assertions to require `Provenance / 来源` and `Maturity / 成熟度`.

- [ ] **Step 2: Run focused visualization tests and verify RED**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python -m unittest tests.test_generate_skill_visualization.SkillVisualizationGeneratorTest.test_loads_axes_matrix_and_pattern_counts tests.test_generate_skill_visualization.SkillVisualizationGeneratorTest.test_renders_self_contained_html_visualization -v
```

Expected: FAIL because registry fields are absent.

- [ ] **Step 3: Implement registry loading**

Add `import json` and:

```python
def load_registry(skill_dir: pathlib.Path) -> dict[str, Any]:
    return json.loads(read_text(skill_dir / "references" / "registry.json"))


def registry_axes(registry: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    return registry["capabilities"], registry["topologies"]


def registry_matrix(registry: dict[str, Any]) -> list[dict[str, str]]:
    return [normalize_registry_cell(cell) for cell in registry["cells"]]
```

Make `load_skill_data()` use these functions for structural data. Keep pattern, observability, cell-guide, trace, and selection-card Markdown parsing for human-readable details and consistency tests. Add `registry.json` to `source_files()`.

Render source-kind and maturity labels in every matrix cell without changing existing file links.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the Step 2 command. Expected: 2 tests pass.

- [ ] **Step 5: Regenerate the HTML and run the full visualization suite**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python scripts/generate_skill_visualization.py
python -m unittest tests.test_generate_skill_visualization -v
```

Expected: generator exits 0; 16 tests pass.

- [ ] **Step 6: Commit Task 3**

```powershell
git add -- tests/test_generate_skill_visualization.py scripts/generate_skill_visualization.py harness-engineering-patterns.html
git commit -m "feat(harness): 由注册表驱动模式可视化"
```

---

### Task 4: Skill, Trace, EIR, Evaluation, And Pattern Contract Repair

**Files:**
- Modify: `tests/test_harness_skill_registry.py`
- Modify: `skills/harness-engineering-patterns/SKILL.md`
- Modify: `skills/harness-engineering-patterns/agents/openai.yaml`
- Modify: `skills/harness-engineering-patterns/references/compiler-workflow.md`
- Modify: `skills/harness-engineering-patterns/references/eir-schema.md`
- Modify: `skills/harness-engineering-patterns/references/evaluation-governance.md`
- Modify: `skills/harness-engineering-patterns/references/pattern-catalog.md`
- Modify: `skills/harness-engineering-patterns/references/matrix-index.md`
- Create: `skills/harness-engineering-patterns/references/trace-schema.md`
- Modify: `skills/harness-engineering-patterns/references/patterns/memory/memory-loop.md`
- Modify: `skills/harness-engineering-patterns/references/patterns/perception/perception-parallel.md`
- Modify: `skills/harness-engineering-patterns/references/patterns/memory/memory-hierarchy.md`
- Modify: `skills/harness-engineering-patterns/references/patterns/memory/memory-hierarchy-observability.md`

**Interfaces:**
- Consumes: registry and design specification.
- Produces: bounded Skill trigger, three output profiles, project-local Trace contract, complete EIR collections, seven evaluation dimensions, exact Pattern Template fields, corrected source terminology.

- [ ] **Step 1: Write failing static contract tests**

Require:

```python
self.assertIn("When Not To Use / 不适用场景", skill)
self.assertIn("Output Profiles / 输出档位", skill)
self.assertIn("quick / 快速", skill)
self.assertIn("standard / 标准", skill)
self.assertIn("full / 完整", skill)
self.assertIn("preliminary / 初步", skill)
self.assertIn("references/trace-schema.md", skill)
self.assertIn(".harness-analysis/<analysis_id>/trace.yaml", skill)
self.assertNotRegex(skill, r"append.*references/patterns/<capability-key>/trace\.md")
```

Require EIR headings for Control Flow, State Flow, Tool Flow, Permission Flow, Pattern Record, Skill Recommendation, Evaluation Reference, and Governance Item. Require evaluation YAML keys `coverage`, `mapping_accuracy`, `evidence`, `reuse`, `skill_readiness`, `governance`, and `evaluability`, each with rubric/formula, direction, evidence sources, observation window, score, confidence, and notes.

Require every design file to contain all 11 exact Pattern Template labels. Require `Failure Journal / 失败日志` plus `Failure Diary / 失败日记` as alias text. Reject `Hanerss` in Skill files.

- [ ] **Step 2: Run contract tests and verify RED**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python -m unittest tests.test_harness_skill_registry -v
```

Expected: FAIL on missing output profiles, trace schema, EIR sections, evaluation keys, template fields, or spelling.

- [ ] **Step 3: Apply minimal bilingual contract changes**

Update the frontmatter description to triggering conditions only. Add non-use cases and profile selection to `SKILL.md`. Replace normal-use bundled Trace writes with a project-local trace proposal and explicit curated-history authorization rule. Synchronize `agents/openai.yaml` with the revised trigger and default prompt.

Replace the conceptual-registry storage note in `compiler-workflow.md` with `registry.json` ownership and Markdown-view validation rules.

Add the eight missing EIR object schemas and shared ID/status rules. Align evaluation output to all seven dimensions and operational metric metadata.

In catalog and matrix documentation, state paper-v2 provenance: 28 upstream named, 14 upstream blank, two local promotions, 12 remaining candidates. Use `Failure Journal` as source name and `Failure Diary` as local alias.

Create the runtime Trace schema with scope, sensitivity, revision, evidence, validity, retention, expiry, owner, and fallback-to-response behavior. Do not edit any existing `trace.md` file.

Add the exact missing Pattern Template labels to `memory-loop.md` and `perception-parallel.md`. Correct all `Hanerss` occurrences in the two layered-retention files and affected tests.

- [ ] **Step 4: Run contract tests and verify GREEN**

Run the Step 2 command. Expected: all registry and contract tests pass.

- [ ] **Step 5: Run validator CLI and inspect remaining errors**

Run the Task 2 CLI command. Expected: only navigation errors for references over 500 lines; warnings for 101-500 line files are allowed.

- [ ] **Step 6: Commit Task 4**

```powershell
git add -- tests/test_harness_skill_registry.py skills/harness-engineering-patterns/SKILL.md skills/harness-engineering-patterns/agents/openai.yaml skills/harness-engineering-patterns/references/compiler-workflow.md skills/harness-engineering-patterns/references/eir-schema.md skills/harness-engineering-patterns/references/evaluation-governance.md skills/harness-engineering-patterns/references/pattern-catalog.md skills/harness-engineering-patterns/references/matrix-index.md skills/harness-engineering-patterns/references/trace-schema.md skills/harness-engineering-patterns/references/patterns/memory/memory-loop.md skills/harness-engineering-patterns/references/patterns/perception/perception-parallel.md skills/harness-engineering-patterns/references/patterns/memory/memory-hierarchy.md skills/harness-engineering-patterns/references/patterns/memory/memory-hierarchy-observability.md
git commit -m "docs(harness): 完善来源追踪与分析契约"
```

Before commit, verify the staged path list does not include `references/patterns/memory/trace.md`.

---

### Task 5: Navigation For The Five Largest References

**Files:**
- Modify: `skills/harness-engineering-patterns/references/patterns/memory/memory-hierarchy-observability.md`
- Modify: `skills/harness-engineering-patterns/references/patterns/memory/memory-hierarchy.md`
- Modify: `skills/harness-engineering-patterns/references/patterns/memory/memory-orchestration.md`
- Modify: `skills/harness-engineering-patterns/references/patterns/perception/perception-loop-observability.md`
- Modify: `skills/harness-engineering-patterns/references/patterns/perception/perception-chain-observability.md`

**Interfaces:**
- Consumes: existing level-two headings.
- Produces: `## Quick Navigation / 快速导航` near the top of every reference over 500 lines, with links to its major sections.

- [ ] **Step 1: Write the failing navigation test**

```python
def test_references_over_500_lines_have_quick_navigation(self):
    for path in SKILL_DIR.joinpath("references").rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        if len(content.splitlines()) > 500:
            self.assertIn("## Quick Navigation / 快速导航", content, str(path))

def test_real_skill_passes_full_validation(self):
    report = load_validator().validate_skill(SKILL_DIR)
    self.assertEqual(report.errors, [])
```

- [ ] **Step 2: Run the navigation test and verify RED**

Run the focused test. Expected: FAIL listing the five files.

- [ ] **Step 3: Add compact navigation sections**

For each file, add links to its existing major headings only. Do not rewrite body content, rename anchors, or change examples.

- [ ] **Step 4: Run the navigation test and validator; verify GREEN**

Expected: test passes and validator exits 0 with warnings only for 101-500 line references.

- [ ] **Step 5: Commit Task 5**

```powershell
git add -- tests/test_harness_skill_registry.py skills/harness-engineering-patterns/references/patterns/memory/memory-hierarchy-observability.md skills/harness-engineering-patterns/references/patterns/memory/memory-hierarchy.md skills/harness-engineering-patterns/references/patterns/memory/memory-orchestration.md skills/harness-engineering-patterns/references/patterns/perception/perception-loop-observability.md skills/harness-engineering-patterns/references/patterns/perception/perception-chain-observability.md
git commit -m "docs(harness): 为大型模式文档增加导航"
```

---

### Task 6: Full Verification And Delivery

**Files:**
- Modify only if verification exposes a tested defect in the files above.

**Interfaces:**
- Consumes: completed implementation.
- Produces: clean verification evidence and a scoped delivery summary.

- [ ] **Step 1: Run all repository tests**

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python -m unittest discover -s tests -v
```

Expected: all tests pass, 0 failures and 0 errors.

- [ ] **Step 2: Run Skill validators**

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python skills/harness-engineering-patterns/scripts/validate_harness_skill.py skills/harness-engineering-patterns
python 'C:\Users\wangs\.codex\skills\.system\skill-creator\scripts\quick_validate.py' skills/harness-engineering-patterns
```

Expected: custom validator exit 0; standard validator prints `Skill is valid!`.

- [ ] **Step 3: Regenerate and verify HTML determinism**

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'; python scripts/generate_skill_visualization.py
git diff --check
```

Expected: generator exits 0 and `git diff --check` reports no whitespace errors.

- [ ] **Step 4: Verify protected working-tree state**

```powershell
git status --short
git diff -- skills/harness-engineering-patterns/references/patterns/memory/trace.md
```

Expected: the pre-existing memory trace diff is unchanged from the baseline; the untracked cache remains untouched; no implementation file is left unintentionally unstaged or uncommitted.

- [ ] **Step 5: Review final commit range**

```powershell
git log --oneline 84f226f..HEAD
git diff --stat 84f226f..HEAD
```

Expected: only the approved registry, validator, visualization, Skill contract, navigation, test, and generated HTML changes.

- [ ] **Step 6: Use `superpowers:verification-before-completion`, then `superpowers:finishing-a-development-branch`**

Report exact test counts, validator results, commits, preserved user changes, and any remaining warnings. Do not push without a separate explicit request.
