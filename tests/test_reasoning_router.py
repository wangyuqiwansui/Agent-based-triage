import importlib.util
import json
import pathlib
import sys
import unittest

from jsonschema import Draft202012Validator


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "skills"
    / "harness-engineering-patterns"
    / "runtime"
    / "reasoning_router.py"
)
CONTRACT_SCHEMA_PATH = MODULE_PATH.parents[1] / "schemas" / "reasoning-contract.schema.json"
EVENT_SCHEMA_PATH = MODULE_PATH.parents[1] / "schemas" / "reasoning-event.schema.json"


def load_router_module():
    spec = importlib.util.spec_from_file_location("harness_reasoning_router", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


router = load_router_module()
CONTRACT_SCHEMA = json.loads(CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
EVENT_SCHEMA = json.loads(EVENT_SCHEMA_PATH.read_text(encoding="utf-8"))


def definition_validator(schema, definition_name):
    return Draft202012Validator(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$ref": f"#/$defs/{definition_name}",
            "$defs": schema["$defs"],
        }
    )


def signals(**overrides):
    values = {
        "task_id": "TASK_0001",
        "scene_id": "SCENE_TEST",
        "intent_complexity": router.IntentComplexity.LOW,
        "evidence_state": router.EvidenceState.COMPLETE_CONSISTENT,
        "mechanism_uncertainty": router.MechanismUncertainty.LOW,
        "risk_level": router.RiskLevel.LOW,
        "environment_interaction_required": False,
        "material_rivals_present": False,
        "dominant_dependency_path": False,
        "permission_granted": True,
        "strong_validation_available": True,
    }
    values.update(overrides)
    return router.RoutingSignals(**values)


class ReasoningRoutingPolicyTest(unittest.TestCase):
    def setUp(self):
        self.policy = router.RoutingPolicy()

    def test_low_risk_complete_evidence_routes_direct_without_topology(self):
        decision = self.policy.route(signals())

        self.assertEqual(decision.disposition, router.RouteDisposition.EXECUTE)
        self.assertEqual(decision.reasoning_depth, router.ReasoningDepth.DIRECT)
        self.assertEqual(decision.execution_mode, router.ExecutionMode.DIRECT)
        self.assertIsNone(decision.primary_topology)

    def test_prohibited_action_is_rejected_before_other_signals(self):
        decision = self.policy.route(
            signals(prohibited_action=True, environment_interaction_required=True)
        )

        self.assertEqual(decision.disposition, router.RouteDisposition.REJECT)
        self.assertEqual(decision.reason_codes, ("policy_constraint",))

    def test_denied_permission_is_rejected(self):
        decision = self.policy.route(signals(permission_granted=False))

        self.assertEqual(decision.disposition, router.RouteDisposition.REJECT)
        self.assertEqual(decision.reason_codes, ("policy_constraint",))

    def test_missing_required_signal_abstains_and_escalates(self):
        decision = self.policy.route(signals(evidence_state=None))

        self.assertEqual(decision.disposition, router.RouteDisposition.ESCALATE)
        self.assertTrue(decision.abstained)
        self.assertEqual(decision.missing_signals, ("evidence_state",))

    def test_irreversible_action_without_strong_validation_escalates(self):
        decision = self.policy.route(
            signals(irreversible_action=True, strong_validation_available=False)
        )

        self.assertEqual(decision.disposition, router.RouteDisposition.ESCALATE)
        self.assertIn("hierarchy", decision.supporting_topologies)

    def test_high_risk_without_strong_validation_escalates(self):
        decision = self.policy.route(
            signals(
                risk_level=router.RiskLevel.HIGH,
                strong_validation_available=False,
            )
        )

        self.assertEqual(decision.disposition, router.RouteDisposition.ESCALATE)
        self.assertEqual(decision.reason_codes, ("external_validation_required",))

    def test_environment_interaction_precedes_parallel_rivals(self):
        decision = self.policy.route(
            signals(
                environment_interaction_required=True,
                material_rivals_present=True,
            )
        )

        self.assertEqual(decision.execution_mode, router.ExecutionMode.ITERATIVE)
        self.assertEqual(decision.primary_topology, router.PrimaryTopology.LOOP)

    def test_conflicting_evidence_routes_parallel(self):
        decision = self.policy.route(
            signals(evidence_state=router.EvidenceState.CONFLICTING)
        )

        self.assertEqual(decision.execution_mode, router.ExecutionMode.PARALLEL)
        self.assertEqual(decision.primary_topology, router.PrimaryTopology.PARALLEL)

    def test_dominant_dependency_path_routes_chain(self):
        decision = self.policy.route(signals(dominant_dependency_path=True))

        self.assertEqual(decision.execution_mode, router.ExecutionMode.CHAIN)
        self.assertEqual(decision.primary_topology, router.PrimaryTopology.CHAIN)

    def test_medium_risk_cannot_use_direct_release_path(self):
        decision = self.policy.route(signals(risk_level=router.RiskLevel.MEDIUM))

        self.assertEqual(decision.execution_mode, router.ExecutionMode.CHAIN)

    def test_unavailable_evidence_escalates(self):
        decision = self.policy.route(
            signals(evidence_state=router.EvidenceState.UNAVAILABLE)
        )

        self.assertEqual(decision.disposition, router.RouteDisposition.ESCALATE)
        self.assertTrue(decision.abstained)

    def test_signal_fingerprint_is_stable_and_sensitive(self):
        first = self.policy.route(signals()).signal_fingerprint
        second = self.policy.route(signals()).signal_fingerprint
        changed = self.policy.route(
            signals(intent_complexity=router.IntentComplexity.HIGH)
        ).signal_fingerprint

        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)
        self.assertRegex(first, r"^sha256:[a-f0-9]{64}$")

    def test_route_policy_version_is_semantic(self):
        self.assertEqual(self.policy.route_policy_version, "1.0.0")
        with self.assertRaises(ValueError):
            router.RoutingPolicy(route_policy_version="1")

    def test_route_policy_id_satisfies_the_contract_identifier(self):
        for invalid_id in ("bad policy", "_bad-prefix", "a" * 161):
            with self.subTest(invalid_id=invalid_id[:20]):
                with self.assertRaises(ValueError):
                    router.RoutingPolicy(route_policy_id=invalid_id)
        with self.assertRaises(TypeError):
            router.RoutingPolicy(route_policy_id=123)

    def test_confidence_is_not_a_routing_input(self):
        self.assertNotIn("confidence", router.RoutingSignals.__dataclass_fields__)

    def test_signal_types_are_strict_and_cannot_silently_misroute(self):
        with self.assertRaises(TypeError):
            signals(risk_level="high")
        with self.assertRaises(TypeError):
            signals(permission_granted=1)

    def test_route_decision_is_json_serializable(self):
        decision = self.policy.route(signals())

        encoded = json.dumps(decision.as_dict(), sort_keys=True)

        self.assertIn('"execution_mode": "direct"', encoded)
        self.assertIn('"route_policy_version": "1.0.0"', encoded)

    def test_execute_route_serializes_to_contract_and_event_schemas(self):
        route_signals = signals()
        decision = self.policy.route(route_signals)

        contract_value = decision.to_contract_routing_decision(route_signals)
        event_value = decision.to_route_event_payload(route_signals)

        self.assertTrue(
            definition_validator(CONTRACT_SCHEMA, "RoutingDecision").is_valid(
                contract_value
            )
        )
        self.assertTrue(
            definition_validator(EVENT_SCHEMA, "RouteSelectedPayload").is_valid(
                event_value
            )
        )

    def test_abstained_route_has_schema_valid_event_but_no_contract(self):
        route_signals = signals(evidence_state=None)
        decision = self.policy.route(route_signals)

        event_value = decision.to_route_event_payload(route_signals)
        self.assertTrue(
            definition_validator(EVENT_SCHEMA, "RouteSelectedPayload").is_valid(
                event_value
            )
        )
        with self.assertRaises(ValueError):
            decision.to_contract_routing_decision(route_signals)

    def test_schema_serializers_reject_signals_from_another_decision(self):
        original = signals()
        changed = signals(intent_complexity=router.IntentComplexity.HIGH)
        decision = self.policy.route(original)

        with self.assertRaises(ValueError):
            decision.to_route_event_payload(changed)
        with self.assertRaises(ValueError):
            decision.to_contract_routing_decision(changed)


if __name__ == "__main__":
    unittest.main()
