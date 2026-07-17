import importlib.util
import inspect
import json
import pathlib
import re
import sys
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
MODULE_PATH = RUNTIME_DIR / "reasoning_metrics.py"
REGISTRY_PATH = RUNTIME_DIR / "metric_registry.json"
PROBE_REGISTRY_PATH = RUNTIME_DIR / "probe_registry.json"
WORKFLOW_PROBES_PATH = (
    ROOT
    / "skills"
    / "harness-engineering-patterns"
    / "references"
    / "workflow-observability-probes.md"
)
REASONING_OBSERVABILITY_DIR = (
    ROOT
    / "skills"
    / "harness-engineering-patterns"
    / "references"
    / "patterns"
    / "reasoning"
)


def documented_formula_ids():
    content = WORKFLOW_PROBES_PATH.read_text(encoding="utf-8")
    formulas = content[
        content.index("### Core formulas / 核心公式") : content.index(
            "### Hard alerts / 硬告警"
        )
    ]
    blocks = re.findall(r"```text\s*(.*?)```", formulas, flags=re.DOTALL)
    raw_ids = set(
        re.findall(
            r"(?m)^([a-z][a-z0-9_]*(?:_<dimension>|\[dimension\])?)\s*=",
            "\n".join(blocks),
        )
    )
    aliases = {
        "budget_utilization_<dimension>": "budget_utilization_vector",
        "budget_utilization_vector[dimension]": "budget_utilization_vector",
    }
    return {aliases.get(metric_id, metric_id) for metric_id in raw_ids}, len(blocks)


def documented_formulas():
    content = WORKFLOW_PROBES_PATH.read_text(encoding="utf-8")
    formulas = content[
        content.index("### Core formulas / 核心公式") : content.index(
            "### Hard alerts / 硬告警"
        )
    ]
    records = {}
    for block in re.findall(r"```text\s*(.*?)```", formulas, flags=re.DOTALL):
        for line in block.splitlines():
            if "=" not in line:
                continue
            metric_id, formula = (part.strip() for part in line.split("=", 1))
            records[metric_id] = formula
    return records


def load_metrics_module():
    spec = importlib.util.spec_from_file_location(
        "harness_reasoning_metrics",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


metrics = load_metrics_module()


class MetricStateTest(unittest.TestCase):
    def test_states_are_explicit_and_distinct(self):
        self.assertEqual(
            {state.value for state in metrics.MetricState},
            {
                "observed_zero",
                "missing",
                "unknown",
                "not_applicable",
                "insufficient_sample",
                "computed",
            },
        )

    def test_missing_is_not_observed_zero(self):
        observed_zero = metrics.safe_ratio("example", 0, 10)
        missing = metrics.safe_ratio("example", None, 10)
        unknown = metrics.safe_ratio(
            "example",
            None,
            10,
            unavailable_state=metrics.MetricState.UNKNOWN,
        )

        self.assertEqual(observed_zero.state, metrics.MetricState.OBSERVED_ZERO)
        self.assertEqual(observed_zero.value, 0.0)
        self.assertEqual(missing.state, metrics.MetricState.MISSING)
        self.assertIsNone(missing.value)
        self.assertEqual(unknown.state, metrics.MetricState.UNKNOWN)
        self.assertIsNone(unknown.value)

    def test_zero_denominator_is_not_applicable(self):
        result = metrics.safe_ratio("example", 0, 0)

        self.assertEqual(result.state, metrics.MetricState.NOT_APPLICABLE)
        self.assertIsNone(result.value)
        self.assertEqual(result.reason, "zero_denominator")

    def test_small_sample_is_reported_without_value(self):
        result = metrics.safe_ratio("example", 2, 4, min_sample=5)

        self.assertEqual(result.state, metrics.MetricState.INSUFFICIENT_SAMPLE)
        self.assertIsNone(result.value)
        self.assertEqual(result.details["minimum_sample"], 5.0)

    def test_nonzero_ratio_is_computed(self):
        result = metrics.safe_ratio("example", 2, 4)

        self.assertEqual(result.state, metrics.MetricState.COMPUTED)
        self.assertEqual(result.value, 0.5)

    def test_public_bounded_and_unbounded_helpers(self):
        bounded = metrics.bounded_ratio("bounded", 1, 2)
        unbounded = metrics.unbounded_ratio("unbounded", 3, 2)

        self.assertEqual(bounded.value, 0.5)
        self.assertEqual(unbounded.value, 1.5)
        with self.assertRaises(ValueError):
            metrics.bounded_ratio("bounded", 3, 2)

    def test_metric_result_enforces_state_value_invariants(self):
        with self.assertRaises(ValueError):
            metrics.MetricResult(
                metric_id="invalid",
                state=metrics.MetricState.COMPUTED,
                value=0,
            )
        with self.assertRaises(ValueError):
            metrics.MetricResult(
                metric_id="invalid",
                state=metrics.MetricState.OBSERVED_ZERO,
                value=1,
            )
        with self.assertRaises(ValueError):
            metrics.MetricResult(
                metric_id="invalid",
                state=metrics.MetricState.MISSING,
                value=0,
                reason="missing",
            )
        with self.assertRaises(ValueError):
            metrics.MetricResult(
                metric_id="invalid",
                state=metrics.MetricState.UNKNOWN,
            )

    def test_safe_ratio_validates_present_numbers_before_early_return(self):
        with self.assertRaises(ValueError):
            metrics.safe_ratio("invalid", -1, None)
        with self.assertRaises(ValueError):
            metrics.safe_ratio(
                "invalid",
                -1,
                10,
                unavailable_state=metrics.MetricState.UNKNOWN,
            )
        with self.assertRaises(ValueError):
            metrics.safe_ratio("invalid", None, 10, sample_size=-1)


class CorrectedReasoningMetricTest(unittest.TestCase):
    def test_step_closure_uses_due_started_steps_as_denominator(self):
        closure = metrics.eligible_step_closure_rate(7, 10)
        record_completeness = metrics.closed_step_record_completeness(7, 7)

        self.assertEqual(closure.value, 0.7)
        self.assertEqual(record_completeness.value, 1.0)
        self.assertEqual(closure.denominator, 10.0)
        self.assertEqual(record_completeness.denominator, 7.0)

    def test_route_stability_is_separate_from_outcome_accuracy(self):
        stability = metrics.route_stability_rate(9, 10)
        accuracy = metrics.outcome_route_accuracy(5, 10)

        self.assertEqual(stability.metric_id, "route_stability_rate")
        self.assertEqual(accuracy.metric_id, "outcome_route_accuracy")
        self.assertEqual(stability.value, 0.9)
        self.assertEqual(accuracy.value, 0.5)

    def test_route_accuracy_without_outcomes_is_missing(self):
        result = metrics.outcome_route_accuracy(None, None)

        self.assertEqual(result.state, metrics.MetricState.MISSING)
        self.assertIsNone(result.value)

    def test_hypothesis_efficiency_keeps_denominator_units_separate(self):
        per_iteration = metrics.hypothesis_elimination_per_iteration(6, 3)
        per_cost = metrics.hypothesis_elimination_per_cost_unit(6, 12)

        self.assertEqual(per_iteration.value, 2.0)
        self.assertEqual(per_cost.value, 0.5)
        self.assertEqual(per_iteration.denominator, 3.0)
        self.assertEqual(per_cost.denominator, 12.0)

    def test_budget_utilization_is_multidimensional_and_has_maximum(self):
        actual = {"reasoning_tokens": 800, "tool_calls": 0, "latency_ms": 50}
        limits = {"reasoning_tokens": 1000, "tool_calls": 10, "latency_ms": 100}

        vector = metrics.budget_utilization_vector(actual, limits)
        maximum = metrics.max_budget_utilization(actual, limits)

        self.assertEqual(vector.state, metrics.MetricState.COMPUTED)
        self.assertEqual(
            vector.value,
            {"latency_ms": 0.5, "reasoning_tokens": 0.8, "tool_calls": 0.0},
        )
        self.assertEqual(maximum.value, 0.8)
        self.assertEqual(maximum.metric_id, "max_budget_utilization")
        self.assertEqual(maximum.details["maximum_dimension"], "reasoning_tokens")

    def test_all_zero_budget_use_is_observed_zero(self):
        actual = {"model_calls": 0, "tool_calls": 0}
        limits = {"model_calls": 4, "tool_calls": 8}

        vector = metrics.budget_utilization_vector(actual, limits)
        maximum = metrics.budget_utilization_max(actual, limits)

        self.assertEqual(vector.state, metrics.MetricState.OBSERVED_ZERO)
        self.assertEqual(maximum.state, metrics.MetricState.OBSERVED_ZERO)
        self.assertEqual(maximum.value, 0.0)

    def test_missing_budget_dimension_prevents_false_maximum(self):
        actual = {"reasoning_tokens": 800}
        limits = {"reasoning_tokens": 1000, "tool_calls": 10}

        vector = metrics.budget_utilization_vector(actual, limits)
        maximum = metrics.budget_utilization_max(actual, limits)

        self.assertEqual(vector.state, metrics.MetricState.MISSING)
        self.assertEqual(
            vector.details["dimension_states"]["tool_calls"],
            "missing",
        )
        self.assertEqual(maximum.state, metrics.MetricState.MISSING)
        self.assertIsNone(maximum.value)

    def test_null_budget_limit_is_unconfigured_not_missing(self):
        actual = {"reasoning_tokens": 5, "tool_calls": 7}
        limits = {"reasoning_tokens": 10, "tool_calls": None}

        vector = metrics.budget_utilization_vector(actual, limits)
        maximum = metrics.max_budget_utilization(actual, limits)

        self.assertEqual(vector.state, metrics.MetricState.COMPUTED)
        self.assertEqual(vector.value, {"reasoning_tokens": 0.5})
        self.assertEqual(
            vector.details["dimension_states"]["tool_calls"],
            "not_applicable",
        )
        self.assertIn("tool_calls", vector.details["unconfigured_actual_dimensions"])
        self.assertEqual(maximum.value, 0.5)

    def test_all_null_budget_limits_are_not_applicable(self):
        vector = metrics.budget_utilization_vector(
            {"model_calls": 0},
            {"model_calls": None},
        )

        self.assertEqual(vector.state, metrics.MetricState.NOT_APPLICABLE)
        self.assertIsNone(vector.value)

    def test_zero_or_negative_budget_limit_is_invalid(self):
        with self.assertRaises(ValueError):
            metrics.budget_utilization_vector({"tool_calls": 0}, {"tool_calls": 0})
        with self.assertRaises(ValueError):
            metrics.budget_utilization_vector({"tool_calls": 0}, {"tool_calls": -1})

    def test_event_chain_denominator_is_expected_run_inventory(self):
        result = metrics.event_chain_completeness(8, 10)

        self.assertEqual(result.value, 0.8)
        self.assertEqual(result.denominator, 10.0)

    def test_validation_false_release_and_probe_health_rates(self):
        validation = metrics.validation_coverage(18, 20)
        false_release = metrics.false_release_rate(1, 20)
        event_loss = metrics.event_loss_rate(2, 100)
        duplicate = metrics.duplicate_event_rate(3, 100)
        parse_failure = metrics.parse_failure_rate(4, 100)

        self.assertEqual(validation.value, 0.9)
        self.assertEqual(false_release.value, 0.05)
        self.assertEqual(event_loss.value, 0.02)
        self.assertEqual(duplicate.value, 0.03)
        self.assertEqual(parse_failure.value, 0.04)

    def test_rate_numerator_cannot_exceed_denominator(self):
        with self.assertRaises(ValueError):
            metrics.event_loss_rate(11, 10)

    def test_added_bounded_metrics_use_deterministic_ratios(self):
        cases = [
            (metrics.validation_pass_rate, 8, 10, 0.8),
            (metrics.reasoning_drift_rate, 1, 10, 0.1),
            (metrics.contract_completeness, 9, 10, 0.9),
            (metrics.evidence_traceability, 7, 10, 0.7),
            (metrics.stop_reason_completeness, 10, 10, 1.0),
            (metrics.probe_completion_rate, 6, 10, 0.6),
            (metrics.evidence_coverage, 8, 10, 0.8),
            (metrics.unsupported_conclusion_rate, 2, 10, 0.2),
            (metrics.unverified_premise_propagation, 1, 10, 0.1),
            (metrics.material_candidate_difference, 3, 4, 0.75),
            (metrics.path_convergence_rate, 7, 10, 0.7),
            (metrics.no_progress_loop_rate, 2, 10, 0.2),
            (metrics.budget_overrun_rate, 1, 10, 0.1),
            (metrics.tool_success_rate, 9, 10, 0.9),
            (metrics.probe_coverage, 5, 5, 1.0),
            (metrics.alert_delivery_rate, 8, 10, 0.8),
            (metrics.plan_compile_success_rate, 9, 10, 0.9),
            (metrics.plan_drift_rate, 1, 10, 0.1),
            (metrics.checkpoint_validation_binding_rate, 8, 10, 0.8),
            (metrics.budget_pre_reservation_coverage, 10, 10, 1.0),
            (metrics.evidence_resolution_rate, 7, 10, 0.7),
            (metrics.candidate_evidence_lineage_integrity_rate, 9, 10, 0.9),
            (metrics.readonly_tool_lifecycle_completion_rate, 8, 10, 0.8),
        ]

        for function, numerator, denominator, expected in cases:
            with self.subTest(metric=function.__name__):
                self.assertEqual(function(numerator, denominator).value, expected)

    def test_added_unbounded_metrics_and_retry_invariant(self):
        cost = metrics.cost_per_validated_success(25, 5)
        amplification = metrics.retry_amplification(15, 10)

        self.assertEqual(cost.value, 5.0)
        self.assertEqual(amplification.value, 1.5)
        with self.assertRaises(ValueError):
            metrics.retry_amplification(9, 10)

    def test_calculate_metric_uses_canonical_keyword_inputs(self):
        result = metrics.calculate_metric(
            "reasoning_drift_rate",
            {
                "long_runs_with_unapproved_goal_constraint_or_fact_drift": 1,
                "long_runs_with_comparable_snapshots": 10,
            },
        )

        self.assertEqual(result.value, 0.1)
        with self.assertRaises(ValueError):
            metrics.calculate_metric(
                "reasoning_drift_rate",
                {
                    "long_runs_with_unapproved_drift": 1,
                    "long_runs_with_comparable_snapshots": 10,
                },
            )

    def test_calculate_metric_enforces_registry_minimum_sample(self):
        definition = metrics.METRIC_DEFINITIONS["validation_pass_rate"]
        with mock.patch.dict(definition, {"minimum_sample": 5}):
            result = metrics.calculate_metric(
                "validation_pass_rate",
                {
                    "runs_passing_all_mandatory_validators": 2,
                    "runs_with_valid_validation_results": 2,
                },
            )

        self.assertEqual(result.state, metrics.MetricState.INSUFFICIENT_SAMPLE)
        self.assertEqual(result.reason, "sample_below_minimum")
        self.assertEqual(result.details["minimum_sample"], 5.0)

    def test_calculate_metric_rejects_invalid_registry_minimum_sample(self):
        definition = metrics.METRIC_DEFINITIONS["validation_pass_rate"]
        with mock.patch.dict(definition, {"minimum_sample": 0}):
            with self.assertRaises(RuntimeError):
                metrics.calculate_metric(
                    "validation_pass_rate",
                    {
                        "runs_passing_all_mandatory_validators": 1,
                        "runs_with_valid_validation_results": 2,
                    },
                )

    def test_calculate_metric_dispatches_every_mvp_metric(self):
        for metric_id, definition in metrics.METRIC_DEFINITIONS.items():
            with self.subTest(metric_id=metric_id):
                if metric_id in {
                    "budget_utilization_vector",
                    "max_budget_utilization",
                }:
                    inputs = {
                        "actual_use": {"tool_calls": 1},
                        "configured_limits": {"tool_calls": 2},
                    }
                elif metric_id == "retry_amplification":
                    inputs = {
                        definition["inputs"][0]: 2,
                        definition["inputs"][1]: 1,
                    }
                else:
                    inputs = {
                        definition["inputs"][0]: 1,
                        definition["inputs"][1]: 2,
                    }
                self.assertEqual(
                    metrics.calculate_metric(metric_id, inputs).metric_id,
                    metric_id,
                )


class MetricEnvelopeTest(unittest.TestCase):
    def envelope_for(
        self,
        result,
        *,
        observed_probes=None,
        probe_health=None,
        expected_manifest_version=None,
        calculation_inputs=None,
        watermark="2026-07-15T01:00:00Z",
        allowed_lateness_seconds=0,
        window_finalized=True,
    ):
        definition = metrics.METRIC_DEFINITIONS[result.metric_id]
        required = set(metrics.UNIVERSAL_REQUIRED_PROBES) | set(
            definition["required_probes"]
        )
        if calculation_inputs is None:
            calculation_inputs = {
                definition["inputs"][0]: result.numerator,
                definition["inputs"][1]: result.denominator,
            }
        return metrics.MetricEnvelope(
            result=result,
            registry_version=metrics.METRIC_REGISTRY["schema_version"],
            metric_version=definition["version"],
            calculation_inputs=calculation_inputs,
            window_start="2026-07-15T00:00:00Z",
            window_end="2026-07-15T01:00:00Z",
            time_basis="occurred_at",
            watermark=watermark,
            allowed_lateness_seconds=allowed_lateness_seconds,
            window_revision=1,
            window_finalized=window_finalized,
            buckets={
                "scene_id": "reasoning",
                "risk_level": "medium",
                "execution_mode": "chain",
            },
            exclusion_counts={name: 0 for name in definition["exclusions"]},
            completeness=1.0,
            source_mix={"raw_observation": 10},
            observed_probes=tuple(sorted(required))
            if observed_probes is None
            else observed_probes,
            probe_health=probe_health or metrics.ProbeHealthState.HEALTHY,
            expected_manifest_version=expected_manifest_version,
        )

    def test_publish_guard_accepts_complete_healthy_envelope(self):
        result = metrics.validation_pass_rate(9, 10)
        published = metrics.publish_metric(self.envelope_for(result))

        self.assertEqual(published["metric_id"], "validation_pass_rate")
        self.assertEqual(published["metric_state"], "computed")
        self.assertEqual(published["probe_health"], "healthy")
        self.assertEqual(
            published["calculation_inputs"],
            {
                "runs_passing_all_mandatory_validators": 9,
                "runs_with_valid_validation_results": 10,
            },
        )
        self.assertRegex(published["calculation_inputs_hash"], r"^sha256:[0-9a-f]{64}$")

    def test_publish_guard_rejects_missing_probe_and_unhealthy_collection(self):
        result = metrics.validation_pass_rate(9, 10)
        envelope = self.envelope_for(
            result,
            observed_probes=("PROBE_0002", "PROBE_0011"),
            probe_health=metrics.ProbeHealthState.DEGRADED,
        )

        failures = metrics.metric_publication_failures(envelope)
        self.assertTrue(any(item.startswith("missing_required_probes:") for item in failures))
        self.assertIn("probe_health_not_healthy", failures)
        with self.assertRaises(metrics.MetricPublicationError):
            metrics.publish_metric(envelope)

    def test_publish_guard_recomputes_and_rejects_forged_result(self):
        forged = metrics.MetricResult(
            metric_id="validation_pass_rate",
            state=metrics.MetricState.COMPUTED,
            value=2.0,
            numerator=1,
            denominator=2,
            sample_size=2,
        )
        envelope = self.envelope_for(forged)

        failures = metrics.metric_publication_failures(envelope)
        self.assertIn("calculation_mismatch:value", failures)
        with self.assertRaises(metrics.MetricPublicationError):
            metrics.publish_metric(envelope)

    def test_publish_guard_requires_registry_buckets_and_exact_exclusions(self):
        result = metrics.validation_pass_rate(9, 10)
        valid = self.envelope_for(result)
        envelope = metrics.MetricEnvelope(
            **{
                **valid.__dict__,
                "buckets": {"scene_id": "reasoning"},
                "exclusion_counts": {"invented_exclusion": 0},
            }
        )

        failures = metrics.metric_publication_failures(envelope)
        self.assertTrue(
            any(item.startswith("missing_required_buckets:") for item in failures)
        )
        self.assertTrue(
            any(item.startswith("missing_declared_exclusions:") for item in failures)
        )
        self.assertEqual(
            [
                item
                for item in failures
                if item.startswith("unknown_exclusion_counts:")
            ],
            ["unknown_exclusion_counts:invented_exclusion"],
        )

    def test_budget_metric_persists_inputs_and_is_recomputable(self):
        inputs = {
            "actual_use": {"tool_calls": 3, "model_calls": 1},
            "configured_limits": {"tool_calls": 6, "model_calls": 4},
        }
        result = metrics.calculate_metric("max_budget_utilization", inputs)
        published = metrics.publish_metric(
            self.envelope_for(result, calculation_inputs=inputs)
        )

        self.assertEqual(published["calculation_inputs"], inputs)
        self.assertEqual(published["value"], 0.5)

    def test_metric_window_requires_rfc3339_order_and_final_watermark(self):
        result = metrics.validation_pass_rate(9, 10)
        with self.assertRaises(ValueError):
            metrics.MetricEnvelope(
                **{
                    **self.envelope_for(result).__dict__,
                    "window_start": "2026-07-15 00:00:00",
                }
            )
        with self.assertRaises(ValueError):
            metrics.MetricEnvelope(
                **{
                    **self.envelope_for(result).__dict__,
                    "window_start": "2026-07-15T02:00:00Z",
                }
            )

        envelope = self.envelope_for(
            result,
            watermark="2026-07-15T01:00:30Z",
            allowed_lateness_seconds=60,
            window_finalized=False,
        )
        failures = metrics.metric_publication_failures(envelope)
        self.assertIn("watermark_before_finalization_threshold", failures)
        self.assertIn("window_not_finalized", failures)

    def test_inventory_metrics_require_manifest_binding(self):
        result = metrics.event_chain_completeness(8, 10)
        without_manifest = self.envelope_for(result)
        with_manifest = self.envelope_for(
            result,
            expected_manifest_version="expected-runs-v1",
        )

        self.assertIn(
            "expected_manifest_version_required",
            metrics.metric_publication_failures(without_manifest),
        )
        self.assertEqual(metrics.metric_publication_failures(with_manifest), ())

    def test_unavailable_metric_is_diagnostic_not_publishable(self):
        result = metrics.validation_pass_rate(None, 10)
        envelope = self.envelope_for(result)

        self.assertIn(
            "metric_value_unavailable",
            metrics.metric_publication_failures(envelope),
        )
        self.assertEqual(envelope.as_dict()["metric_state"], "missing")
        with self.assertRaises(metrics.MetricPublicationError):
            metrics.publish_metric(envelope)


class ProbeDependencyResolutionTest(unittest.TestCase):
    def test_direct_mode_requires_explicit_tri_state_conditions(self):
        with self.assertRaises(ValueError):
            metrics.resolve_required_probes("direct")

        base = metrics.resolve_required_probes(
            "direct",
            condition_states={
                "tool_or_side_effect_action": "false",
                "correctness_or_release_metric": "false",
            },
        )
        self.assertNotIn("PROBE_0007", base.required_probes)
        self.assertNotIn("PROBE_0013", base.required_probes)

        resolved = metrics.resolve_required_probes(
            "direct",
            condition_states={
                "tool_or_side_effect_action": "true",
                "correctness_or_release_metric": "true",
            },
        )
        self.assertIn("PROBE_0007", resolved.required_probes)
        self.assertIn("PROBE_0013", resolved.required_probes)
        self.assertEqual(
            resolved.as_dict()["activated_conditionals"],
            [
                {
                    "probe_id": "PROBE_0007",
                    "condition_id": "tool_or_side_effect_action",
                },
                {
                    "probe_id": "PROBE_0013",
                    "condition_id": "correctness_or_release_metric",
                },
            ],
        )
        self.assertEqual(
            resolved.as_dict()["condition_states"],
            {
                "correctness_or_release_metric": "true",
                "tool_or_side_effect_action": "true",
            },
        )
        self.assertTrue(resolved.as_dict()["required_probe_bindings"])
        self.assertEqual(
            {
                binding["probe_id"]: binding["version"]
                for binding in resolved.as_dict()["required_probe_bindings"]
            },
            {
                probe_id: metrics.PROBE_DEFINITIONS[probe_id]["version"]
                for probe_id in resolved.required_probes
            },
        )

    def test_supporting_topology_requirements_are_merged(self):
        resolved = metrics.resolve_required_probes(
            "parallel",
            supporting_topologies=("orchestration",),
            condition_states={
                "branch_action": "true",
                "winner_adoption_or_correctness_metric": "false",
                "parallel_branch_exists": "true",
                "iteration_exists": "false",
                "outcome_metric": "true",
            },
        )
        self.assertTrue(
            {
                "PROBE_0007",
                "PROBE_0008",
                "PROBE_0013",
                "PROBE_0015",
            }
            <= set(resolved.required_probes)
        )

    def test_unknown_or_inapplicable_configuration_fails_closed(self):
        with self.assertRaises(ValueError):
            metrics.resolve_required_probes("unknown")
        with self.assertRaises(ValueError):
            metrics.resolve_required_probes(
                "direct", supporting_topologies=("loop",)
            )
        with self.assertRaises(ValueError):
            metrics.resolve_required_probes(
                "direct",
                condition_states={
                    "tool_or_side_effect_action": "false",
                    "correctness_or_release_metric": "false",
                    "branch_action": "true",
                },
            )
        with self.assertRaises(ValueError):
            metrics.resolve_required_probes(
                "direct",
                condition_states={
                    "tool_or_side_effect_action": "unknown",
                    "correctness_or_release_metric": "false",
                },
            )
        with self.assertRaises(ValueError):
            metrics.resolve_required_probes(
                "direct",
                condition_states={"tool_or_side_effect_action": "false"},
            )
        with self.assertRaises(ValueError):
            metrics.resolve_required_probes(
                "chain", supporting_topologies=("orchestration", "orchestration")
            )


class MetricRegistryTest(unittest.TestCase):
    def test_probe_registry_is_versioned_and_closes_all_dependencies(self):
        registry = json.loads(PROBE_REGISTRY_PATH.read_text(encoding="utf-8"))
        records = {record["probe_id"]: record for record in registry["probes"]}
        self.assertEqual(registry["schema_version"], "1.0.0")
        self.assertEqual(set(records), {f"PROBE_{index:04d}" for index in range(1, 16)})
        required_fields = {
            "version",
            "name_en",
            "name_zh",
            "owner",
            "trigger_event_types",
            "required_capture_fields",
            "output_event_type",
            "disposition",
        }
        for probe_id, record in records.items():
            with self.subTest(probe_id=probe_id):
                self.assertTrue(required_fields <= set(record))
                self.assertRegex(record["version"], r"^\d+\.\d+\.\d+$")
                self.assertTrue(record["trigger_event_types"])
                self.assertTrue(record["required_capture_fields"])

        referenced = set(metrics.UNIVERSAL_REQUIRED_PROBES)
        for definition in metrics.METRIC_DEFINITIONS.values():
            referenced.update(definition["required_probes"])
        for entry in metrics.PROBE_DEPENDENCY_MATRIX["entries"]:
            referenced.update(entry["required_probes"])
            referenced.update(entry["conditional_probes"])
        self.assertTrue(referenced <= set(records))

    def test_registry_is_bilingual_and_complete(self):
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        expected_ids, formula_block_count = documented_formula_ids()
        records = {record["metric_id"]: record for record in registry["metrics"]}

        self.assertEqual(formula_block_count, 3)
        self.assertEqual(registry["schema_version"], "1.0.0")
        self.assertTrue(registry["name_en"])
        self.assertTrue(registry["name_zh"])
        self.assertEqual(set(records), expected_ids)

        required_fields = {
            "metric_id",
            "document_formula_id",
            "version",
            "formula",
            "inputs",
            "formula_zh",
            "unit",
            "unit_zh",
            "direction",
            "direction_zh",
            "required_probes",
            "denominator",
            "denominator_zh",
            "exclusions",
            "exclusions_zh",
            "minimum_sample",
            "owner",
            "owner_en",
            "owner_zh",
        }
        for record in records.values():
            self.assertTrue(required_fields <= set(record))
            self.assertTrue(record["name_en"])
            self.assertTrue(record["name_zh"])
            self.assertTrue(record["description_en"])
            self.assertTrue(record["description_zh"])
            self.assertGreaterEqual(record["minimum_sample"], 1)
            self.assertTrue(record["inputs"])
            self.assertEqual(len(record["inputs"]), len(set(record["inputs"])))
            self.assertNotRegex(record["formula"], r"[a-z]-[a-z]")
            self.assertTrue(
                all(re.fullmatch(r"[a-z][a-z0-9_]*", name) for name in record["inputs"])
            )
            self.assertEqual(len(record["exclusions"]), len(record["exclusions_zh"]))
            self.assertIn(
                record["direction"],
                {
                    "higher_is_better",
                    "lower_is_better",
                    "closer_to_one_is_better",
                },
            )

    def test_registry_matches_document_formulas_and_public_functions(self):
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        documented_ids, block_count = documented_formula_ids()
        formulas = documented_formulas()
        registry_ids = {record["metric_id"] for record in registry["metrics"]}
        registry_document_ids = {
            record["document_formula_id"] for record in registry["metrics"]
        }

        self.assertEqual(block_count, 3)
        self.assertEqual(registry_ids, documented_ids)
        self.assertEqual(registry_document_ids, documented_ids)
        self.assertEqual(set(formulas), registry_ids)
        for record in registry["metrics"]:
            metric_id = record["metric_id"]
            with self.subTest(metric_id=metric_id):
                self.assertTrue(hasattr(metrics, metric_id))
                self.assertIn(metric_id, metrics.__all__)
                self.assertEqual(record["formula"], formulas[metric_id])
                function = getattr(metrics, metric_id)
                required_parameters = [
                    name
                    for name, parameter in inspect.signature(function).parameters.items()
                    if parameter.default is inspect.Parameter.empty
                    and parameter.kind
                    in {
                        inspect.Parameter.POSITIONAL_ONLY,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    }
                ]
                self.assertEqual(record["inputs"], required_parameters)

    def test_mvp_coverage_declaration_is_closed(self):
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        metric_ids = {record["metric_id"] for record in registry["metrics"]}
        coverage = registry["coverage"]

        self.assertEqual(coverage["profile"], "mvp_core")
        self.assertEqual(set(coverage["implemented"]), metric_ids)
        self.assertTrue(set(coverage["gate_eligible"]) <= metric_ids)
        self.assertFalse(set(coverage["planned"]) & metric_ids)
        self.assertEqual(
            set(registry["universal_required_probes"]),
            {"PROBE_0001", "PROBE_0014", "PROBE_0015"},
        )
        self.assertEqual(
            registry["required_bucket_dimensions"],
            ["scene_id", "risk_level", "execution_mode"],
        )
        self.assertNotIn("outcome_route_accuracy", coverage["gate_eligible"])
        self.assertNotIn("path_convergence_rate", coverage["gate_eligible"])
        self.assertTrue(
            {
                "plan_compile_success_rate",
                "plan_drift_rate",
                "checkpoint_validation_binding_rate",
                "budget_pre_reservation_coverage",
                "evidence_resolution_rate",
                "candidate_evidence_lineage_integrity_rate",
                "readonly_tool_lifecycle_completion_rate",
            }
            <= set(coverage["implemented"])
        )
        self.assertFalse(
            {
                "plan_compile_success_rate",
                "plan_drift_rate",
                "checkpoint_validation_binding_rate",
                "budget_pre_reservation_coverage",
                "evidence_resolution_rate",
                "candidate_evidence_lineage_integrity_rate",
                "readonly_tool_lifecycle_completion_rate",
            }
            & set(coverage["gate_eligible"])
        )

    def test_default_alert_gates_use_only_gate_eligible_metrics(self):
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        gate_eligible = set(registry["coverage"]["gate_eligible"])
        observed_gate_metrics = set()

        for path in REASONING_OBSERVABILITY_DIR.glob("*observability.md"):
            content = path.read_text(encoding="utf-8")
            if "### Default Gate Suggestions" not in content:
                continue
            gate_section = content.split("### Default Gate Suggestions", 1)[1]
            for line in gate_section.splitlines():
                if not line.startswith("- Alert"):
                    continue
                observed_gate_metrics.update(re.findall(r"`([a-z][a-z0-9_]*)`", line))

        self.assertTrue(observed_gate_metrics)
        self.assertTrue(observed_gate_metrics <= gate_eligible)

    def test_registry_marks_stability_as_non_accuracy_and_requires_outcome_probe(self):
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        records = {record["metric_id"]: record for record in registry["metrics"]}

        self.assertIn("not route accuracy", records["route_stability_rate"]["description_en"])
        self.assertIn(
            "PROBE_0013",
            records["outcome_route_accuracy"]["required_probes"],
        )
        self.assertEqual(
            records["event_chain_completeness"]["denominator"],
            "expected_runs",
        )
        self.assertEqual(
            records["hypothesis_elimination_per_iteration"]["denominator"],
            "completed_iterations",
        )
        self.assertEqual(
            records["hypothesis_elimination_per_cost_unit"]["denominator"],
            "observed_cost_units",
        )


if __name__ == "__main__":
    unittest.main()
