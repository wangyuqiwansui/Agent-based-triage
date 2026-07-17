"""Behavior tests for the reasoning reference kernel / 推理参考内核行为测试。"""

import json
import pathlib
import sys
import tempfile
import threading
import unittest
from unittest import mock
from datetime import datetime, timezone

from jsonschema import Draft202012Validator, FormatChecker


ROOT = pathlib.Path(__file__).resolve().parents[1]
TESTS_DIR = ROOT / "tests"
RUNTIME_DIR = ROOT / "skills" / "harness-engineering-patterns" / "runtime"
EVENT_SCHEMA = (
    ROOT
    / "skills"
    / "harness-engineering-patterns"
    / "schemas"
    / "reasoning-event.schema.json"
)
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(1, str(TESTS_DIR))

from reasoning_runtime import (  # noqa: E402
    BudgetExceededError,
    BudgetLedger,
    BudgetLimits,
    DuplicateEventConflictError,
    EventSchemaViolationError,
    EventStore,
    EventStorePersistenceError,
    IllegalTransitionError,
    JsonlEventStore,
    NoProgressLimitError,
    PrivateReasoningCaptureError,
    ReasoningEngine,
    ReasoningRuntimeError,
    RiskLevel,
    ValidationGateError,
    ValidationStatus,
    ValidatorSpec,
    WorkflowState,
    candidate_binding_for,
    content_fingerprint,
)
from reasoning_artifacts import artifact_fingerprint  # noqa: E402
from test_reasoning_runtime_schemas import sealed_contract  # noqa: E402


def probe_health_payload(*, health="healthy"):
    observed_zero = {"state": "observed_zero", "value": 0}
    return {
        "probe_binding": {
            "id": "probe-runtime-test",
            "version": "1.0.0",
            "hash": "sha256:" + "a" * 64,
        },
        "health": health,
        "window": {
            "started_at": "2026-07-15T00:00:00Z",
            "ended_at": "2026-07-15T00:01:00Z",
        },
        "reconstruction_status": "complete",
        "unreconstructable_reasons": [],
        "received_events": {"state": "observed", "value": 1},
        "expected_events": {"state": "observed", "value": 1},
        "missing_events": dict(observed_zero),
        "duplicate_events": dict(observed_zero),
        "out_of_order_events": dict(observed_zero),
        "parse_failures": dict(observed_zero),
        "calculation_failures": dict(observed_zero),
        "alerts_due": dict(observed_zero),
        "alerts_delivered": dict(observed_zero),
        "alert_delivery_failures": dict(observed_zero),
        "event_loss_rate": dict(observed_zero),
        "policy_action": "continue",
    }


class StateMachineTest(unittest.TestCase):
    def test_authoritative_state_and_validation_enums_are_stable(self):
        self.assertEqual(
            {state.value for state in WorkflowState},
            {
                "received",
                "normalized",
                "governance_precheck",
                "routed",
                "contract_established",
                "executing",
                "waiting_for_evidence",
                "mode_switched",
                "candidate_ready",
                "validating",
                "repairable_failure",
                "completed",
                "rejected",
                "failed",
                "escalated",
                "cancelled",
                "timed_out",
            },
        )
        self.assertEqual(
            {status.value for status in ValidationStatus},
            {
                "not_run",
                "passed",
                "conditionally_passed",
                "repairable_failure",
                "nonrepairable_failure",
                "human_required",
                "timed_out",
            },
        )

    def test_illegal_transition_is_rejected_without_an_event(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-illegal", auto_start=False)
        before = len(engine.events.events(run_id))

        with self.assertRaises(IllegalTransitionError):
            engine.transition(run_id, WorkflowState.COMPLETED, reason="skip gates")

        self.assertEqual(engine.snapshot(run_id).state, WorkflowState.RECEIVED)
        self.assertEqual(len(engine.events.events(run_id)), before)

    def test_transition_command_is_idempotent(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-transition", auto_start=False)

        first = engine.transition(
            run_id,
            WorkflowState.NORMALIZED,
            reason="normalized input",
            idempotency_key="transition-command-1",
        )
        event_count = len(engine.events.events(run_id))
        second = engine.transition(
            run_id,
            WorkflowState.NORMALIZED,
            reason="normalized input",
            idempotency_key="transition-command-1",
        )

        self.assertEqual(first.state, second.state)
        self.assertEqual(len(engine.events.events(run_id)), event_count)

    def test_cancel_and_timeout_are_explicit_terminal_states(self):
        cancelled = ReasoningEngine()
        cancel_id = cancelled.create_run(task_id="task-cancel")
        self.assertEqual(
            cancelled.cancel(cancel_id, reason="input invalidated").state,
            WorkflowState.CANCELLED,
        )

        timed_out = ReasoningEngine()
        timeout_id = timed_out.create_run(task_id="task-timeout")
        self.assertEqual(
            timed_out.timeout(timeout_id, reason="deadline reached").state,
            WorkflowState.TIMED_OUT,
        )

    def test_terminal_event_stream_is_sealed_after_run_ended(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-terminal-seal")
        engine.cancel(run_id, reason="user cancelled")

        with self.assertRaises(ReasoningRuntimeError):
            engine.events.append(
                run_id=run_id,
                event_type="probe_health_reported",
                state=WorkflowState.CANCELLED,
                payload=probe_health_payload(),
            )

    def test_terminal_transition_and_receipt_roll_back_as_one_event_transaction(self):
        class FailingTerminalStore(EventStore):
            def append(self, **kwargs):
                if kwargs.get("event_type") == "run_ended":
                    raise RuntimeError("injected terminal receipt failure")
                return super().append(**kwargs)

        store = FailingTerminalStore()
        engine = ReasoningEngine(store)
        run_id = engine.create_run(task_id="task-terminal-transaction")
        before = len(store.events(run_id))

        with self.assertRaises(RuntimeError):
            engine.cancel(run_id, reason="user cancelled")

        self.assertEqual(engine.snapshot(run_id).state, WorkflowState.EXECUTING)
        self.assertEqual(len(store.events(run_id)), before)
        self.assertNotIn(
            "run_ended", {event.event_type for event in store.events(run_id)}
        )

    def test_failed_state_event_append_does_not_mutate_live_state(self):
        class FailingTransitionStore(EventStore):
            def append(self, **kwargs):
                if kwargs.get("event_type") == "state_transitioned":
                    raise RuntimeError("injected state persistence failure")
                return super().append(**kwargs)

        store = FailingTransitionStore()
        engine = ReasoningEngine(store)
        run_id = engine.create_run(
            task_id="task-state-event-transaction",
            auto_start=False,
        )
        before = len(store.events(run_id))

        with self.assertRaises(RuntimeError):
            engine.transition(run_id, WorkflowState.NORMALIZED, reason="normalized")

        self.assertEqual(engine.snapshot(run_id).state, WorkflowState.RECEIVED)
        self.assertEqual(len(store.events(run_id)), before)


class EventStoreTest(unittest.TestCase):
    def test_exact_duplicate_event_is_idempotent_and_conflict_is_rejected(self):
        store = EventStore()
        first = store.append(
            run_id="run-1",
            event_type="probe_health_reported",
            state=WorkflowState.RECEIVED,
            payload=probe_health_payload(),
            event_id="event-1",
            idempotency_key="logical-1",
        )
        duplicate = store.append(
            run_id="run-1",
            event_type="probe_health_reported",
            state=WorkflowState.RECEIVED,
            payload=probe_health_payload(),
            event_id="event-1",
            idempotency_key="logical-1",
        )

        self.assertIs(first, duplicate)
        self.assertEqual(first.as_dict()["occurred_at"], duplicate.as_dict()["occurred_at"])
        self.assertEqual(first.sequence, 1)
        self.assertEqual(len(store.events("run-1")), 1)
        with self.assertRaises(DuplicateEventConflictError):
            store.append(
                run_id="run-1",
                event_type="probe_health_reported",
                state=WorkflowState.RECEIVED,
                payload=probe_health_payload(health="degraded"),
                idempotency_key="logical-1",
            )

    def test_payload_is_detached_and_private_reasoning_is_rejected(self):
        store = EventStore()
        event = store.append(
            run_id="run-2",
            event_type="probe_health_reported",
            state=WorkflowState.RECEIVED,
            payload=probe_health_payload(),
        )
        detached = event.payload
        detached["probe_binding"]["id"] = "mutated"
        self.assertEqual(event.payload["probe_binding"]["id"], "probe-runtime-test")

        with self.assertRaises(PrivateReasoningCaptureError):
            store.append(
                run_id="run-2",
                event_type="probe_health_reported",
                state=WorkflowState.RECEIVED,
                payload={"chain_of_thought": "must not persist"},
            )

    def test_schema_invalid_event_is_rejected_before_append(self):
        store = EventStore()
        with self.assertRaises(EventSchemaViolationError):
            store.append(
                run_id="run-invalid-event",
                event_type="probe_health_reported",
                state=WorkflowState.RECEIVED,
                payload={"health": "healthy"},
            )
        self.assertEqual(store.events("run-invalid-event"), ())

    def test_replay_rejects_a_terminal_receipt_without_a_run_lifecycle(self):
        store = EventStore()
        store.append(
            run_id="run-orphan-terminal",
            event_type="run_ended",
            state=WorkflowState.CANCELLED,
            payload={
                "terminal_state": "cancelled",
                "reason_code": "user_cancelled",
            },
        )

        with self.assertRaises(ReasoningRuntimeError):
            ReasoningEngine(event_store=store).replay("run-orphan-terminal")

    def test_human_work_event_can_carry_the_required_contract_binding(self):
        binding = {
            "id": "contract-human-1",
            "version": "1.0.0",
            "hash": "sha256:" + "a" * 64,
        }
        event = EventStore().append(
            run_id="run-human-1",
            task_id="task-human-1",
            workflow_id="workflow-human-1",
            event_type="human_work_updated",
            state=WorkflowState.EXECUTING,
            human_work_id="human-work-1",
            contract_binding=binding,
            payload={
                "phase": "expired",
                "work_type": "review",
                "authority_scope": ["release"],
                "expired_at": "2030-01-01T00:00:00Z",
                "expiration_reason_code": "service_level_expired",
                "fallback_action": "fail_closed",
            },
        )

        self.assertEqual(event.as_dict()["contract_binding"], binding)

    def test_jsonl_store_reopens_replays_and_preserves_idempotency(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "reasoning-events.jsonl"
            store = JsonlEventStore(path)
            first = store.append(
                run_id="run-durable-1",
                event_type="probe_health_reported",
                state=WorkflowState.RECEIVED,
                payload=probe_health_payload(),
                event_id="event-durable-1",
                idempotency_key="durable-logical-1",
            )

            reopened = JsonlEventStore(path)
            restored = reopened.events("run-durable-1")[0]
            duplicate = reopened.append(
                run_id="run-durable-1",
                event_type="probe_health_reported",
                state=WorkflowState.RECEIVED,
                payload=probe_health_payload(),
                event_id="event-durable-1",
                idempotency_key="durable-logical-1",
            )

            self.assertEqual(restored.as_dict(), first.as_dict())
            self.assertIs(duplicate, restored)
            self.assertEqual(len(reopened.replay("run-durable-1")), 1)

    def test_jsonl_transaction_commits_once_and_rolls_back_failed_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "reasoning-events.jsonl"
            store = JsonlEventStore(path)
            with store.transaction("run-durable-transaction"):
                for index in (1, 2):
                    store.append(
                        run_id="run-durable-transaction",
                        event_type="probe_health_reported",
                        state=WorkflowState.RECEIVED,
                        payload=probe_health_payload(),
                        event_id=f"event-durable-transaction-{index}",
                        idempotency_key=f"durable-transaction-{index}",
                    )
            committed_text = path.read_text(encoding="utf-8")
            self.assertEqual(
                len(JsonlEventStore(path).events("run-durable-transaction")),
                2,
            )

            with self.assertRaises(RuntimeError):
                with store.transaction("run-durable-transaction"):
                    store.append(
                        run_id="run-durable-transaction",
                        event_type="probe_health_reported",
                        state=WorkflowState.RECEIVED,
                        payload=probe_health_payload(),
                        event_id="event-durable-transaction-3",
                        idempotency_key="durable-transaction-3",
                    )
                    raise RuntimeError("abort durable group")

            self.assertEqual(path.read_text(encoding="utf-8"), committed_text)
            self.assertEqual(len(store.events("run-durable-transaction")), 2)

    def test_jsonl_store_supports_engine_replay_after_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "reasoning-engine-events.jsonl"
            engine = ReasoningEngine(JsonlEventStore(path))
            run_id = engine.create_run(
                task_id="task-durable-replay",
                run_id="run-durable-replay",
                auto_start=False,
            )

            replayed = ReasoningEngine(JsonlEventStore(path)).replay(run_id)

            self.assertEqual(replayed.state, WorkflowState.RECEIVED)
            self.assertEqual(replayed.event_count, 1)
            self.assertEqual(replayed.last_sequence, 1)

    def test_jsonl_commit_failure_rolls_back_memory_and_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "reasoning-events.jsonl"
            store = JsonlEventStore(path)
            store.append(
                run_id="run-durable-failure",
                event_type="probe_health_reported",
                state=WorkflowState.RECEIVED,
                payload=probe_health_payload(),
                event_id="event-durable-before-failure",
            )
            committed_text = path.read_text(encoding="utf-8")

            with mock.patch.object(
                store,
                "_persist_snapshot",
                side_effect=EventStorePersistenceError("injected commit failure"),
            ):
                with self.assertRaises(EventStorePersistenceError):
                    store.append(
                        run_id="run-durable-failure",
                        event_type="probe_health_reported",
                        state=WorkflowState.RECEIVED,
                        payload=probe_health_payload(health="degraded"),
                        event_id="event-durable-after-failure",
                    )

            self.assertEqual(len(store.events("run-durable-failure")), 1)
            self.assertEqual(path.read_text(encoding="utf-8"), committed_text)
            self.assertEqual(
                len(JsonlEventStore(path).events("run-durable-failure")),
                1,
            )

    def test_jsonl_store_rejects_a_tampered_storage_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "reasoning-events.jsonl"
            JsonlEventStore(path).append(
                run_id="run-durable-tamper",
                event_type="probe_health_reported",
                state=WorkflowState.RECEIVED,
                payload=probe_health_payload(),
                event_id="event-durable-tamper",
            )
            record = json.loads(path.read_text(encoding="utf-8"))
            record["envelope"]["payload"]["data"]["health"] = "degraded"
            path.write_text(
                json.dumps(record, ensure_ascii=False, separators=(",", ":"))
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(EventStorePersistenceError):
                JsonlEventStore(path)


class BudgetLedgerTest(unittest.TestCase):
    def test_budget_and_event_write_roll_back_together(self):
        class FailingEventStore(EventStore):
            fail_type = None

            def append(self, **kwargs):
                if kwargs.get("event_type") == self.fail_type:
                    raise RuntimeError("injected event persistence failure")
                return super().append(**kwargs)

        store = FailingEventStore()
        engine = ReasoningEngine(store)
        run_id = engine.create_run(
            task_id="task-budget-event-transaction",
            budget_limits={"tokens": 10},
        )

        store.fail_type = "budget_consumed"
        with self.assertRaises(RuntimeError):
            engine.consume_budget(
                run_id,
                {"tokens": 2},
                idempotency_key="consume-fails-to-persist",
            )
        self.assertEqual(engine.snapshot(run_id).budget.used["tokens"], 0)

        store.fail_type = "budget_reserved"
        with self.assertRaises(RuntimeError):
            engine.reserve_budget(
                run_id,
                {"tokens": 3},
                reservation_id="reservation-fails-to-persist",
            )
        self.assertEqual(engine.snapshot(run_id).budget.reserved["tokens"], 0)

        store.fail_type = None
        reservation_id = engine.reserve_budget(
            run_id,
            {"tokens": 4},
            reservation_id="reservation-release-rollback",
        )
        store.fail_type = "budget_released"
        with self.assertRaises(RuntimeError):
            engine.release_budget(run_id, reservation_id)
        self.assertEqual(engine.snapshot(run_id).budget.reserved["tokens"], 4)

    def test_step_reservation_and_start_commit_or_roll_back_as_one_group(self):
        class FailingStartStore(EventStore):
            fail_start = True

            def append(self, **kwargs):
                if self.fail_start and kwargs.get("event_type") == "step_started":
                    raise RuntimeError("injected step-start persistence failure")
                return super().append(**kwargs)

        store = FailingStartStore()
        engine = ReasoningEngine(store)
        run_id = engine.create_run(
            task_id="task-reserve-start-transaction",
            budget_limits={"tokens": 10},
        )
        command = {
            "step_id": "step-reserve-start",
            "claim": "reservation precedes dispatch",
            "evidence_refs": [],
            "action": "inspect public state",
            "reservation_amounts": {"tokens": 4},
            "reservation_id": "reservation-step-reserve-start",
        }

        with self.assertRaises(RuntimeError):
            engine.start_step_with_budget_reservation(run_id, **command)

        snapshot = engine.snapshot(run_id)
        self.assertEqual(snapshot.budget.reserved["tokens"], 0)
        self.assertEqual(snapshot.open_step_count, 0)
        self.assertFalse(
            {"budget_reserved", "step_started"}
            & {event.event_type for event in store.events(run_id)}
        )

        store.fail_start = False
        record = engine.start_step_with_budget_reservation(run_id, **command)
        self.assertEqual(record.step_id, "step-reserve-start")
        self.assertEqual(engine.snapshot(run_id).budget.reserved["tokens"], 4)
        lifecycle = [
            event.event_type
            for event in store.events(run_id)
            if event.event_type in {"budget_reserved", "step_started"}
        ]
        self.assertEqual(lifecycle, ["budget_reserved", "step_started"])

    def test_step_budget_and_close_roll_back_when_budget_event_append_fails(self):
        class FailingStepBudgetStore(EventStore):
            def append(self, **kwargs):
                if kwargs.get("event_type") == "budget_consumed":
                    raise RuntimeError("injected step-budget persistence failure")
                return super().append(**kwargs)

        store = FailingStepBudgetStore()
        engine = ReasoningEngine(store)
        run_id = engine.create_run(
            task_id="task-step-budget-transaction",
            budget_limits={"tokens": 10},
        )

        with self.assertRaises(RuntimeError):
            engine.record_step(
                run_id,
                step_id="step-budget-failure",
                claim="budget is persisted atomically",
                evidence_refs=[],
                action="consume the declared budget",
                observation="event append failed",
                local_decision="retry safely",
                resource_use={"tokens": 2},
                progress=True,
            )

        snapshot = engine.snapshot(run_id)
        self.assertEqual(snapshot.budget.used["tokens"], 0)
        self.assertEqual(snapshot.step_count, 0)
        self.assertEqual(snapshot.open_step_count, 1)
        self.assertNotIn(
            "step_closed", {event.event_type for event in store.events(run_id)}
        )

    def test_normative_schema_budget_names_are_accepted(self):
        limits = BudgetLimits.from_value(
            {
                "max_reasoning_tokens": 100,
                "max_latency_ms": 500,
                "max_model_calls": 2,
                "max_tool_calls": 3,
                "max_parallel_paths": 2,
                "max_iterations": 4,
                "max_retries": 1,
                "max_total_cost_units": None,
            }
        )

        self.assertEqual(limits.tokens, 100)
        self.assertEqual(limits.latency_ms, 500)
        self.assertEqual(limits.retries, 1)
        self.assertIsNone(limits.cost_units)

    def test_atomic_overrun_leaves_all_dimensions_unchanged(self):
        ledger = BudgetLedger(
            BudgetLimits(
                tokens=10,
                latency_ms=10,
                model_calls=1,
                tool_calls=1,
                paths=1,
                iterations=1,
                retries=1,
                cost_units=2,
            )
        )
        ledger.consume({"tokens": 4, "tool_calls": 1})

        with self.assertRaises(BudgetExceededError):
            ledger.consume({"tokens": 2, "model_calls": 1, "tool_calls": 1})

        self.assertEqual(ledger.snapshot().used["tokens"], 4)
        self.assertEqual(ledger.snapshot().used["model_calls"], 0)
        self.assertEqual(ledger.snapshot().used["tool_calls"], 1)

    def test_null_limit_is_unconfigured_not_unlimited(self):
        ledger = BudgetLedger({"cost_units": None})

        with self.assertRaises(BudgetExceededError):
            ledger.consume({"cost_units": 0.1})

        self.assertEqual(ledger.snapshot().used["cost_units"], 0)

    def test_reservations_are_thread_safe_and_fail_closed(self):
        ledger = BudgetLedger({"tokens": 10})
        outcomes = []
        barrier = threading.Barrier(3)

        def reserve(identifier):
            barrier.wait()
            try:
                ledger.reserve({"tokens": 6}, identifier)
                outcomes.append("reserved")
            except BudgetExceededError:
                outcomes.append("blocked")

        threads = [threading.Thread(target=reserve, args=(f"r-{index}",)) for index in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait()
        for thread in threads:
            thread.join()

        self.assertCountEqual(outcomes, ["reserved", "blocked"])
        self.assertEqual(ledger.snapshot().reserved["tokens"], 6)

    def test_engine_reservation_commit_and_release_emit_events(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-engine-reservation",
            budget_limits={"tokens": 10, "tool_calls": 2},
        )

        reservation_id = engine.reserve_budget(
            run_id,
            {"tokens": 6, "tool_calls": 1},
            reservation_id="reservation-test-1",
            idempotency_key="reserve-command-1",
        )
        duplicate_id = engine.reserve_budget(
            run_id,
            {"tokens": 6, "tool_calls": 1},
            reservation_id="reservation-test-1",
            idempotency_key="reserve-command-1",
        )
        committed = engine.consume_budget(
            run_id,
            {"tokens": 4, "tool_calls": 1},
            reservation_id=reservation_id,
            idempotency_key="consume-reservation-1",
        )
        release_id = engine.reserve_budget(
            run_id,
            {"tokens": 2},
            reservation_id="reservation-test-2",
        )
        released = engine.release_budget(run_id, release_id)

        self.assertEqual(duplicate_id, reservation_id)
        self.assertEqual(committed.used["tokens"], 4)
        self.assertEqual(released.reserved["tokens"], 0)
        event_types = [event.event_type for event in engine.events.events(run_id)]
        self.assertIn("budget_reserved", event_types)
        self.assertIn("budget_consumed", event_types)
        self.assertIn("budget_released", event_types)

    def test_positive_consumption_requires_an_idempotency_key(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-budget-key-required")

        with self.assertRaises(ValueError):
            engine.consume_budget(run_id, {"tokens": 1})

        self.assertEqual(engine.snapshot(run_id).budget.used["tokens"], 0)

    def test_default_reservation_key_makes_same_reservation_retry_idempotent(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-reservation-default-key")

        first = engine.reserve_budget(
            run_id,
            {"tokens": 2},
            reservation_id="reservation-default-key",
        )
        second = engine.reserve_budget(
            run_id,
            {"tokens": 2},
            reservation_id="reservation-default-key",
        )

        self.assertEqual(first, second)
        self.assertEqual(engine.snapshot(run_id).budget.reserved["tokens"], 2)

    def test_zero_actual_commit_releases_a_reservation_idempotently(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-zero-reservation-commit")
        reservation_id = engine.reserve_budget(
            run_id,
            {"tokens": 2},
            reservation_id="reservation-zero-actual",
        )

        first = engine.consume_budget(
            run_id,
            {"tokens": 0},
            reservation_id=reservation_id,
            idempotency_key="consume-zero-actual",
        )
        second = engine.consume_budget(
            run_id,
            {"tokens": 0},
            reservation_id=reservation_id,
            idempotency_key="consume-zero-actual",
        )

        self.assertEqual(first.reservation_count, 0)
        self.assertEqual(second.reservation_count, 0)


class ValidationAndEngineTest(unittest.TestCase):
    @staticmethod
    def direct_release_rule():
        return {
            "rule_id": "DIRECT_RELEASE_TEST",
            "rule_version": "1.0.0",
            "allowed_risk_levels": ["low"],
            "predicate": {
                "field_path": "/candidate/verified",
                "operator": "eq",
                "expected": True,
            },
            "criteria_version": "1.0.0",
            "required_evidence": {
                "min_independent_sources": 1,
                "required_evidence_types": ["policy"],
                "max_source_age_seconds": 3600,
                "min_integrity_score": 1.0,
                "min_claim_coverage_ratio": 1.0,
                "max_unresolved_critical_claims": 0,
                "unknown_source_policy": "reject",
            },
            "validator_exemption_basis": {
                "basis": "deterministic_rule",
                "policy_binding": {
                    "id": "POLICY_DIRECT_TEST",
                    "version": "1.0.0",
                    "hash": "sha256:" + "a" * 64,
                },
            },
        }

    @staticmethod
    def direct_release_evidence():
        return [
            {
                "evidence_id": "evidence-direct-policy",
                "evidence_type": "policy",
                "source_id": "policy-direct-test",
                "captured_at": datetime.now(timezone.utc).isoformat().replace(
                    "+00:00", "Z"
                ),
                "integrity_score": 1.0,
                "claim_coverage_ratio": 1.0,
                "unresolved_critical_claims": 0,
            }
        ]

    def test_low_risk_completion_still_requires_validator_without_direct_rule(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-low-no-gate")
        engine.set_candidate(run_id, {"verified": True}, evidence=["rule-v1"])

        with self.assertRaises(ValidationGateError):
            engine.finalize(run_id)

    def test_contract_cannot_drift_from_authoritative_budget_or_validators(self):
        engine = ReasoningEngine()
        with self.assertRaises(ValueError):
            engine.create_run(
                task_id="task-contract-budget-drift",
                budget_limits={"tokens": 10},
                contract={"budget": {"tokens": 999}},
            )

        with self.assertRaises(ValueError):
            engine.create_run(
                task_id="task-contract-validator-drift",
                validators=[ValidatorSpec("required-validator")],
                contract={"validators": []},
            )

        with self.assertRaises(ValueError):
            engine.create_run(
                task_id="task-contract-stop-drift",
                max_no_progress_steps=2,
                contract={"max_no_progress_steps": 99},
            )

    def test_valid_low_risk_direct_release_rule_can_replace_validator(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-low-direct-rule",
            contract={"direct_release_rule": self.direct_release_rule()},
        )
        engine.set_candidate(
            run_id,
            {"verified": True},
            evidence=self.direct_release_evidence(),
        )

        result = engine.finalize(run_id)

        self.assertEqual(result.state, WorkflowState.COMPLETED)

    def test_direct_release_rule_must_match_the_bound_candidate(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-low-direct-rule-fail",
            contract={"direct_release_rule": self.direct_release_rule()},
        )
        engine.set_candidate(
            run_id,
            {"verified": False},
            evidence=self.direct_release_evidence(),
        )

        with self.assertRaises(ValidationGateError):
            engine.finalize(run_id)

    def test_direct_release_rule_cannot_exempt_high_risk(self):
        engine = ReasoningEngine()

        with self.assertRaises(ValueError):
            engine.create_run(
                task_id="task-high-direct-rule",
                risk_level="high",
                contract={"direct_release_rule": self.direct_release_rule()},
            )

    def test_direct_release_rule_is_validated_against_the_normative_definition(self):
        malformed_rules = []
        missing_evidence_thresholds = self.direct_release_rule()
        missing_evidence_thresholds["required_evidence"] = {}
        malformed_rules.append(missing_evidence_thresholds)
        incomplete_policy_binding = self.direct_release_rule()
        incomplete_policy_binding["validator_exemption_basis"]["policy_binding"] = {}
        malformed_rules.append(incomplete_policy_binding)

        for index, rule in enumerate(malformed_rules):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):
                    ReasoningEngine().create_run(
                        task_id=f"task-malformed-direct-rule-{index}",
                        contract={"direct_release_rule": rule},
                    )

    def test_direct_release_rejects_invalid_regex_predicates_at_contract_time(self):
        rule = self.direct_release_rule()
        rule["predicate"] = {
            "field_path": "/candidate/value",
            "operator": "matches",
            "expected": "[",
        }

        with self.assertRaises(ValueError):
            ReasoningEngine().create_run(
                task_id="task-invalid-direct-regex",
                contract={"direct_release_rule": rule},
            )

    def test_evidence_freshness_uses_an_auditable_injected_clock(self):
        evaluated_at_epoch = 1_893_456_000.0  # 2030-01-01T00:00:00Z
        evidence = self.direct_release_evidence()
        evidence[0]["captured_at"] = "2030-01-01T00:00:10Z"
        engine = ReasoningEngine(
            clock=lambda: evaluated_at_epoch,
            max_future_evidence_skew_seconds=5,
        )
        run_id = engine.create_run(
            task_id="task-future-direct-evidence",
            contract={"direct_release_rule": self.direct_release_rule()},
        )
        engine.set_candidate(run_id, {"verified": True}, evidence=evidence)

        with self.assertRaises(ValidationGateError):
            engine.finalize(run_id)

        snapshot = engine.snapshot(run_id)
        replayed = engine.replay(run_id)
        gate_event = [
            event
            for event in engine.events.events(run_id)
            if event.event_type == "governance_decided"
            and event.payload.get("reason_code") == "release_gate_blocked"
        ][-1]
        self.assertIn("future", " ".join(engine.completion_failures(run_id)))
        self.assertEqual(gate_event.timestamp, evaluated_at_epoch)
        self.assertEqual(snapshot.release_gate_evaluated_at, "2030-01-01T00:00:00.000Z")
        self.assertEqual(replayed.release_gate_evaluated_at, snapshot.release_gate_evaluated_at)

    def test_finalize_accepts_an_explicit_evaluation_time(self):
        evidence = self.direct_release_evidence()
        evidence[0]["captured_at"] = "2030-01-01T00:00:00Z"
        engine = ReasoningEngine(clock=lambda: 1_893_466_000.0)
        run_id = engine.create_run(
            task_id="task-explicit-direct-evaluation",
            contract={"direct_release_rule": self.direct_release_rule()},
        )
        engine.set_candidate(run_id, {"verified": True}, evidence=evidence)

        result = engine.finalize(
            run_id,
            evaluated_at="2030-01-01T00:00:00Z",
        )

        self.assertEqual(result.state, WorkflowState.COMPLETED)
        self.assertEqual(result.release_gate_evaluated_at, "2030-01-01T00:00:00.000Z")

    def test_direct_release_fails_closed_on_unstructured_or_incomplete_evidence(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-low-direct-evidence-fail",
            contract={"direct_release_rule": self.direct_release_rule()},
        )
        engine.set_candidate(run_id, {"verified": True}, evidence=["rule-v1"])

        with self.assertRaises(ValidationGateError):
            engine.finalize(run_id)

    def test_completion_rejects_open_steps(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-open-step-gate",
            contract={"direct_release_rule": self.direct_release_rule()},
        )
        engine.start_step(
            run_id,
            step_id="step-still-open",
            claim="candidate has a verified flag",
            evidence_refs=["policy-direct-test"],
            action="inspect candidate",
        )
        engine.set_candidate(
            run_id,
            {"verified": True},
            evidence=self.direct_release_evidence(),
        )

        with self.assertRaises(ValidationGateError):
            engine.finalize(run_id)

    def test_completion_rejects_active_budget_reservations(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-active-reservation-gate",
            contract={"direct_release_rule": self.direct_release_rule()},
        )
        engine.reserve_budget(
            run_id,
            {"tokens": 1},
            reservation_id="reservation-active-at-release",
        )
        engine.set_candidate(
            run_id,
            {"verified": True},
            evidence=self.direct_release_evidence(),
        )

        with self.assertRaises(ValidationGateError):
            engine.finalize(run_id)

    def test_high_risk_without_mandatory_validator_cannot_complete(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-high", risk_level=RiskLevel.HIGH)
        engine.set_candidate(run_id, {"decision": "approve"}, evidence=["evidence-1"])

        with self.assertRaises(ValidationGateError):
            engine.finalize(run_id)

        self.assertNotEqual(engine.snapshot(run_id).state, WorkflowState.COMPLETED)

    def test_passing_human_validation_requires_actor_and_authority_bindings(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-human-audit",
            validators=[ValidatorSpec("human-review", kind="human")],
        )
        engine.set_candidate(run_id, {"approved": True}, evidence=["attestation"])

        with self.assertRaises(ValidationGateError):
            engine.record_validation(
                run_id,
                validator_id="human-review",
                status=ValidationStatus.PASSED,
            )
        self.assertEqual(engine.snapshot(run_id).state, WorkflowState.CANDIDATE_READY)
        self.assertEqual(engine.snapshot(run_id).validation_count, 0)

        def observed(identifier):
            return {
                "state": "observed",
                "value": {
                    "id": identifier,
                    "version": "1.0.0",
                    "hash": "sha256:" + "a" * 64,
                },
            }

        engine.record_validation(
            run_id,
            validator_id="human-review",
            status=ValidationStatus.PASSED,
            actor_binding=observed("reviewer-1"),
            authority_binding=observed("approval-authority-1"),
        )
        self.assertEqual(engine.finalize(run_id).state, WorkflowState.COMPLETED)

    def test_candidate_mutation_invalidates_a_previous_validation(self):
        validator = ValidatorSpec("rules", version="2026.7.0", required=True)
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-mutate", validators=[validator])
        engine.set_candidate(run_id, {"answer": 1}, evidence=["source-v1"])
        engine.record_validation(
            run_id,
            validator_id="rules",
            status=ValidationStatus.PASSED,
        )
        engine.set_candidate(run_id, {"answer": 2}, evidence=["source-v1"])

        with self.assertRaises(ValidationGateError):
            engine.finalize(run_id)
        self.assertIn("stale", " ".join(engine.completion_failures(run_id)))

    def test_nonrepairable_validation_closes_the_run_and_cannot_be_overwritten(self):
        validator = ValidatorSpec("terminal-validator", required=True)
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-nonrepairable-validation",
            validators=[validator],
        )
        engine.set_candidate(run_id, {"value": 1}, evidence=["evidence-1"])

        engine.record_validation(
            run_id,
            validator_id="terminal-validator",
            status="nonrepairable_failure",
            idempotency_key="terminal-validation-failure",
        )

        self.assertEqual(engine.snapshot(run_id).state, WorkflowState.FAILED)
        with self.assertRaises(ReasoningRuntimeError):
            engine.record_validation(
                run_id,
                validator_id="terminal-validator",
                status="passed",
                idempotency_key="invalid-overwrite-pass",
            )

    def test_repairable_validation_requires_explicit_reexecution(self):
        validator = ValidatorSpec("repair-validator", required=True)
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-repairable-validation",
            validators=[validator],
        )
        engine.set_candidate(run_id, {"revision": 1}, evidence=["evidence-1"])
        engine.record_validation(
            run_id,
            validator_id="repair-validator",
            status="repairable_failure",
        )
        self.assertEqual(
            engine.snapshot(run_id).state,
            WorkflowState.REPAIRABLE_FAILURE,
        )

        engine.transition(
            run_id,
            WorkflowState.EXECUTING,
            reason="repair authorized",
        )
        engine.set_candidate(run_id, {"revision": 2}, evidence=["evidence-2"])
        engine.record_validation(
            run_id,
            validator_id="repair-validator",
            status="passed",
        )
        self.assertEqual(engine.finalize(run_id).state, WorkflowState.COMPLETED)

    def test_conditional_validation_requires_reexecution_and_new_bindings(self):
        validator = ValidatorSpec("conditional-validator", required=True)
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-conditional-validation",
            validators=[validator],
        )
        engine.set_candidate(run_id, {"revision": 1}, evidence=["evidence-1"])
        engine.record_validation(
            run_id,
            validator_id="conditional-validator",
            status="conditionally_passed",
            details={
                "conditional_obligations": [
                    {
                        "obligation_id": "obligation-revise",
                        "due_state": "completed",
                    }
                ]
            },
        )
        self.assertEqual(
            engine.snapshot(run_id).state,
            WorkflowState.REPAIRABLE_FAILURE,
        )
        with self.assertRaises(ReasoningRuntimeError):
            engine.record_validation(
                run_id,
                validator_id="conditional-validator",
                status="passed",
            )

        engine.transition(
            run_id,
            WorkflowState.EXECUTING,
            reason="conditional obligation repair authorized",
        )
        engine.set_candidate(run_id, {"revision": 1}, evidence=["evidence-1"])
        with self.assertRaises(ValidationGateError):
            engine.record_validation(
                run_id,
                validator_id="conditional-validator",
                status="passed",
            )

        engine.set_candidate(run_id, {"revision": 2}, evidence=["evidence-2"])
        engine.record_validation(
            run_id,
            validator_id="conditional-validator",
            status="passed",
        )
        self.assertEqual(engine.finalize(run_id).state, WorkflowState.COMPLETED)

    def test_human_required_and_validation_timeout_drive_terminal_state(self):
        cases = (
            ("human_required", WorkflowState.ESCALATED),
            ("timed_out", WorkflowState.TIMED_OUT),
        )
        for status, expected_state in cases:
            with self.subTest(status=status):
                engine = ReasoningEngine()
                run_id = engine.create_run(
                    task_id=f"task-validation-{status}",
                    validators=[ValidatorSpec("boundary-validator")],
                )
                engine.set_candidate(run_id, {"value": 1}, evidence=["evidence"])
                engine.record_validation(
                    run_id,
                    validator_id="boundary-validator",
                    status=status,
                )
                self.assertEqual(engine.snapshot(run_id).state, expected_state)
    def test_candidate_and_validation_commands_are_idempotent(self):
        validator = ValidatorSpec("rules", required=True)
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-idempotent", validators=[validator])
        first_hash = engine.set_candidate(
            run_id,
            {"answer": 1},
            evidence=["source-v1"],
            idempotency_key="candidate-command-1",
        )
        second_hash = engine.set_candidate(
            run_id,
            {"answer": 1},
            evidence=["source-v1"],
            idempotency_key="candidate-command-1",
        )
        first_validation = engine.record_validation(
            run_id,
            validator_id="rules",
            status="passed",
            details={"check": "ok"},
            idempotency_key="validation-command-1",
        )
        second_validation = engine.record_validation(
            run_id,
            validator_id="rules",
            status="passed",
            details={"check": "ok"},
            idempotency_key="validation-command-1",
        )

        self.assertEqual(first_hash, second_hash)
        self.assertIs(first_validation, second_validation)
        self.assertEqual(engine.snapshot(run_id).validation_count, 1)

    def test_candidate_and_evidence_records_commit_or_roll_back_together(self):
        class FailingEvidenceStore(EventStore):
            def __init__(self):
                super().__init__(validate_schema=False)
                self.fail_evidence = True

            def append(self, **kwargs):
                if (
                    self.fail_evidence
                    and kwargs.get("event_type") == "evidence_recorded"
                ):
                    raise RuntimeError("injected candidate evidence failure")
                return super().append(**kwargs)

        store = FailingEvidenceStore()
        engine = ReasoningEngine(store)
        run_id = engine.create_run(task_id="task-candidate-evidence-atomic")
        candidate = {"answer": "externally supported / 外部证据支持"}
        contract_binding = engine.events.events(run_id)[0].as_dict()[
            "contract_binding"
        ]
        evidence = {
            "evidence_id": "candidate-evidence-atomic",
            "evidence_version": "1.0.1",
            "evidence_hash": content_fingerprint({"source": "test"}),
            "contract_binding": contract_binding,
            "candidate_binding": {
                "state": "observed",
                "value": candidate_binding_for(candidate),
            },
        }
        evidence["record_hash"] = content_fingerprint(evidence)

        with self.assertRaisesRegex(RuntimeError, "injected candidate evidence"):
            engine.set_candidate_with_evidence_records(
                run_id,
                candidate,
                evidence_records=[evidence],
                idempotency_key="candidate-evidence-atomic",
            )

        failed_snapshot = engine.snapshot(run_id)
        self.assertEqual(failed_snapshot.state, WorkflowState.EXECUTING)
        self.assertIsNone(failed_snapshot.candidate_hash)
        self.assertIsNone(failed_snapshot.evidence_hash)
        self.assertFalse(
            {
                "candidate_created",
                "evidence_recorded",
            }
            & {event.event_type for event in engine.events.events(run_id)}
        )

        store.fail_evidence = False
        candidate_hash = engine.set_candidate_with_evidence_records(
            run_id,
            candidate,
            evidence_records=[evidence],
            idempotency_key="candidate-evidence-atomic",
        )
        committed = engine.snapshot(run_id)
        self.assertEqual(committed.state, WorkflowState.CANDIDATE_READY)
        self.assertEqual(committed.candidate_hash, candidate_hash)
        committed_events = [
            event
            for event in engine.events.events(run_id)
            if event.event_type in {"candidate_created", "evidence_recorded"}
        ]
        self.assertEqual(
            [event.event_type for event in committed_events],
            ["candidate_created", "evidence_recorded"],
        )

    def test_budget_overrun_fails_closed_and_closes_run(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-budget",
            budget_limits={"tokens": 5},
        )

        with self.assertRaises(BudgetExceededError):
            engine.consume_budget(
                run_id,
                {"tokens": 6},
                idempotency_key="consume-overrun-test",
            )

        self.assertEqual(engine.snapshot(run_id).state, WorkflowState.FAILED)
        self.assertEqual(engine.snapshot(run_id).budget.used["tokens"], 0)

    def test_started_but_unclosed_step_remains_observable(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-open-step")

        first = engine.start_step(
            run_id,
            step_id="step-open-1",
            claim="source must be available",
            evidence_refs=[],
            action="request the source",
        )
        duplicate = engine.start_step(
            run_id,
            step_id="step-open-1",
            claim="source must be available",
            evidence_refs=[],
            action="request the source",
        )

        self.assertIs(first, duplicate)
        self.assertEqual(engine.snapshot(run_id).open_step_count, 1)
        self.assertEqual(engine.replay(run_id).open_step_count, 1)
        self.assertIn(
            "step_started",
            [event.event_type for event in engine.events.events(run_id)],
        )

        engine.record_step(
            run_id,
            step_id="step-open-1",
            claim="source must be available",
            evidence_refs=[],
            action="request the source",
            observation="source received",
            local_decision="continue with verified source",
            progress=True,
        )
        self.assertEqual(engine.snapshot(run_id).open_step_count, 0)
        self.assertEqual(engine.replay(run_id).open_step_count, 0)

    def test_no_progress_limit_stops_and_escalates_high_risk_run(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-no-progress",
            risk_level="high",
            validators=[ValidatorSpec("human", kind="human")],
            max_no_progress_steps=2,
        )
        common = {
            "evidence_refs": ["probe-1"],
            "action": "run safe probe",
            "observation": "no new evidence",
            "local_decision": "continue once",
            "progress": False,
        }
        engine.record_step(run_id, step_id="step-1", claim="cause A", **common)

        with self.assertRaises(NoProgressLimitError):
            engine.record_step(run_id, step_id="step-2", claim="cause A remains", **common)

        self.assertEqual(engine.snapshot(run_id).state, WorkflowState.ESCALATED)

    def test_normal_validated_completion_and_replay_have_same_terminal_state(self):
        validator = ValidatorSpec("test-suite", version="1.0.0", kind="test", required=True)
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-success", validators=[validator])
        engine.record_step(
            run_id,
            step_id="step-1",
            claim="output satisfies schema",
            evidence_refs=["test-report-1"],
            action="execute deterministic tests",
            observation={"passed": 8, "failed": 0},
            local_decision="candidate is ready for validation",
            resource_use={"tool_calls": 1, "latency_ms": 10},
            progress=True,
        )
        step_closed = next(
            event
            for event in engine.events.events(run_id)
            if event.event_type == "step_closed"
        )
        self.assertEqual(
            step_closed.as_dict()["resources"]["tool_calls"],
            {"value_state": "observed", "value": 1},
        )
        engine.set_candidate(
            run_id,
            {"answer": "verified"},
            evidence=[{"id": "test-report-1", "digest": "abc"}],
        )
        engine.validate(
            run_id,
            validator_id="test-suite",
            status="passed",
            details={"report": "test-report-1"},
        )

        completed = engine.finalize(run_id)
        replayed = engine.replay(run_id)

        self.assertEqual(completed.state, WorkflowState.COMPLETED)
        self.assertEqual(replayed.state, completed.state)
        self.assertEqual(replayed.candidate_hash, completed.candidate_hash)
        self.assertEqual(replayed.validation_count, 1)
        self.assertEqual(replayed.last_sequence, len(engine.events.events(run_id)))


class NormativeContractExecutionTest(unittest.TestCase):
    def test_contract_bootstrap_emits_protocol_events_and_preserves_route_binding(self):
        contract = sealed_contract()
        engine = ReasoningEngine()

        run_id = engine.create_run_from_contract(contract)

        protocol_events = {
            event.event_type: event.as_dict()
            for event in engine.events.events(run_id)
            if event.event_type
            in {
                "task_received",
                "task_normalized",
                "route_selected",
                "contract_established",
            }
        }
        self.assertEqual(
            set(protocol_events),
            {
                "task_received",
                "task_normalized",
                "route_selected",
                "contract_established",
            },
        )
        self.assertEqual(
            protocol_events["route_selected"]["payload"]["data"][
                "signal_fingerprint"
            ],
            contract["routing_decision"]["signal_fingerprint"],
        )
        self.assertEqual(
            protocol_events["contract_established"]["contract_binding"]["hash"],
            contract["contract_hash"],
        )

    def test_normative_no_progress_uses_exact_information_gain_and_action(self):
        contract = sealed_contract()
        engine = ReasoningEngine()
        run_id = engine.create_run_from_contract(contract)
        common = {
            "evidence_refs": [],
            "action": "measure external information gain",
            "observation": "gain remained below threshold",
            "local_decision": "continue until the declared limit",
            "progress": False,
            "information_gain": 0.005,
        }

        engine.record_step(run_id, step_id="norm-step-1", claim="hypothesis A", **common)
        with self.assertRaises(NoProgressLimitError):
            engine.record_step(run_id, step_id="norm-step-2", claim="hypothesis A", **common)

        self.assertEqual(engine.snapshot(run_id).state, WorkflowState.ESCALATED)
        limit_event = next(
            event
            for event in engine.events.events(run_id)
            if event.event_type == "no_progress_limit_reached"
        )
        self.assertEqual(limit_event.payload["minimum_information_gain"], 0.01)
        self.assertEqual(
            limit_event.payload["observed_information_gain"],
            {"state": "observed", "value": 0.005},
        )
        self.assertEqual(limit_event.payload["on_trigger"], "escalate")

    def test_normative_no_progress_refuses_an_unmeasured_progress_flag(self):
        engine = ReasoningEngine()
        run_id = engine.create_run_from_contract(sealed_contract())

        with self.assertRaisesRegex(ValueError, "information_gain"):
            engine.record_step(
                run_id,
                step_id="norm-step-unmeasured",
                claim="hypothesis A",
                evidence_refs=[],
                action="measure information gain",
                observation="not measured",
                local_decision="cannot classify progress",
                progress=False,
            )

        self.assertEqual(engine.snapshot(run_id).open_step_count, 0)

    def test_budget_reject_action_is_not_compressed_to_fail_or_escalate(self):
        contract = sealed_contract()
        contract["budget"]["max_reasoning_tokens"] = 1
        contract["budget"]["on_exhaustion"] = "reject"
        contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")
        engine = ReasoningEngine()
        run_id = engine.create_run_from_contract(contract)

        with self.assertRaises(BudgetExceededError):
            engine.consume_budget(
                run_id,
                {"tokens": 2},
                idempotency_key="normative-budget-reject",
            )

        self.assertEqual(engine.snapshot(run_id).state, WorkflowState.REJECTED)
        exhausted = next(
            event
            for event in engine.events.events(run_id)
            if event.event_type == "budget_exhausted"
        )
        self.assertEqual(exhausted.payload["on_exhaustion"], "reject")

    def test_unsupported_normative_stop_or_degrade_policy_fails_explicitly(self):
        unsupported_stop = sealed_contract()
        unsupported_stop["stop_conditions"].append(
            {
                "condition_id": "stop-fatal-runtime",
                "type": "fatal_error",
                "on_trigger": "fail",
            }
        )
        unsupported_stop["contract_hash"] = artifact_fingerprint(
            unsupported_stop, "contract_hash"
        )
        with self.assertRaisesRegex(ValueError, "fatal_error"):
            ReasoningEngine().create_run_from_contract(unsupported_stop)

        degrade = sealed_contract()
        degrade["budget"]["on_exhaustion"] = "degrade"
        degrade["contract_hash"] = artifact_fingerprint(degrade, "contract_hash")
        with self.assertRaisesRegex(ValueError, "degrade"):
            ReasoningEngine().create_run_from_contract(degrade)

    def test_multiple_no_progress_rules_are_not_silently_minimized(self):
        contract = sealed_contract()
        contract["stop_conditions"].append(
            {
                "condition_id": "stop-no-progress-secondary",
                "type": "no_progress",
                "consecutive_steps": 4,
                "min_information_gain": 0.2,
                "on_trigger": "fail",
            }
        )
        contract["contract_hash"] = artifact_fingerprint(contract, "contract_hash")

        with self.assertRaisesRegex(ValueError, "composition rule"):
            ReasoningEngine().create_run_from_contract(contract)

    def test_replay_uses_the_live_aggregate_evidence_set_hash(self):
        engine = ReasoningEngine()
        run_id = engine.create_run(task_id="task-evidence-set-replay")
        evidence = [
            {
                "evidence_id": "evidence-set-a",
                "evidence_version": "1.0.0",
                "evidence_hash": "sha256:" + "a" * 64,
            },
            {
                "evidence_id": "evidence-set-b",
                "evidence_version": "1.0.0",
                "evidence_hash": "sha256:" + "b" * 64,
            },
        ]
        engine.set_candidate(run_id, {"answer": 1}, evidence=evidence)

        expected = content_fingerprint(evidence)
        self.assertEqual(engine.snapshot(run_id).evidence_hash, expected)
        self.assertEqual(engine.replay(run_id).evidence_hash, expected)


class SchemaCompatibilityTest(unittest.TestCase):
    def test_every_runtime_event_conforms_to_the_normative_event_schema(self):
        schema = json.loads(EVENT_SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        validator_spec = ValidatorSpec("schema-validator", required=True)
        engine = ReasoningEngine()
        run_id = engine.create_run(
            task_id="task-schema-events",
            execution_mode="chain",
            validators=[validator_spec],
        )
        engine.record_step(
            run_id,
            step_id="step-schema-1",
            claim="candidate has a deterministic schema",
            evidence_refs=["schema-check-1"],
            action="validate event structure",
            observation={"schema_errors": 0},
            local_decision="candidate may enter its release gate",
            resource_use={"tool_calls": 1, "latency_ms": 2},
            progress=True,
        )
        engine.set_candidate(
            run_id,
            {"answer": "schema-valid"},
            evidence=["schema-check-1"],
        )
        engine.validate(
            run_id,
            validator_id="schema-validator",
            status="passed",
        )
        engine.finalize(run_id)

        budget_engine = ReasoningEngine()
        budget_run = budget_engine.create_run(
            task_id="task-schema-budget",
            budget_limits={"tokens": 1},
        )
        with self.assertRaises(BudgetExceededError):
            budget_engine.consume_budget(
                budget_run,
                {"tokens": 2},
                idempotency_key="consume-schema-overrun",
            )

        progress_engine = ReasoningEngine()
        progress_run = progress_engine.create_run(
            task_id="task-schema-progress",
            max_no_progress_steps=1,
        )
        with self.assertRaises(NoProgressLimitError):
            progress_engine.record_step(
                progress_run,
                step_id="step-schema-no-progress",
                claim="evidence remains unavailable",
                evidence_refs=[],
                action="check evidence boundary",
                observation="no new evidence",
                local_decision="stop at the configured threshold",
                progress=False,
            )

        direct_support_engine = ReasoningEngine()
        direct_support_run = direct_support_engine.create_run(
            task_id="task-schema-direct-support",
            execution_mode="direct",
            supporting_topologies=["orchestration"],
            auto_start=False,
        )

        all_events = (
            engine.events.events(run_id)
            + budget_engine.events.events(budget_run)
            + progress_engine.events.events(progress_run)
            + direct_support_engine.events.events(direct_support_run)
        )
        for event in all_events:
            errors = sorted(
                validator.iter_errors(event.as_dict()),
                key=lambda error: list(error.path),
            )
            self.assertEqual(
                errors,
                [],
                f"event {event.sequence} ({event.event_type}) failed schema: "
                + " | ".join(error.message for error in errors),
            )


if __name__ == "__main__":
    unittest.main()
