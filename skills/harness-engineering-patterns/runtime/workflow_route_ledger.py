"""Crash-safe append-only workflow route ledger / 崩溃安全的追加式工作流路由账本。

The ledger is deliberately single-writer per process. Every durable JSONL line
contains a complete committed envelope, so replay never has to join a partially
written event with a later snapshot. / 账本明确采用进程内单写者模型；每一条持久化
JSONL 记录都包含完整的已提交信封，因此重放无需把半条事件与后续快照拼接。
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
from threading import RLock
from typing import Any, Mapping, Sequence

try:  # Package import / 包导入
    from .reasoning_artifacts import (
        ArtifactValidationError,
        artifact_fingerprint,
        build_artifact,
        validate_workflow_route_envelope,
        validate_workflow_route_revision,
    )
except ImportError:  # Direct test/module import / 测试与直接模块导入
    from reasoning_artifacts import (
        ArtifactValidationError,
        artifact_fingerprint,
        build_artifact,
        validate_workflow_route_envelope,
        validate_workflow_route_revision,
    )


REVISION_SCHEMA_VERSION = "1.0.0"
_BUDGET_FIELDS = (
    "reasoning_tokens",
    "latency_ms",
    "model_calls",
    "tool_calls",
    "parallel_paths",
    "iterations",
    "retries",
    "total_cost_units",
)


class WorkflowRouteLedgerError(ValueError):
    """A route history is unsafe, conflicting, or corrupt / 路由历史不安全、冲突或损坏。"""


def _detached(value: Any) -> Any:
    return deepcopy(value)


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _record_hash(record: Mapping[str, Any]) -> str:
    content = dict(record)
    content.pop("record_hash", None)
    return artifact_fingerprint(content)


def _binding(envelope: Mapping[str, Any]) -> dict[str, str]:
    return {
        "id": envelope["decision_id"],
        "version": envelope["schema_version"],
        "hash": envelope["route_envelope_hash"],
    }


def _route_state(envelope: Mapping[str, Any]) -> dict[str, Any]:
    reasoning = envelope["reasoning_decision"]
    return {
        "workflow_signal_fingerprint": envelope["workflow_signal_fingerprint"],
        "reasoning_signal_fingerprint": reasoning["signal_fingerprint"],
        "execution_lane": envelope["execution_lane"],
        "action_allowed": envelope["action_allowed"],
        "reasoning_disposition": reasoning["disposition"],
        "configuration": _detached(reasoning["configuration"]),
    }


def _operational_signature(envelope: Mapping[str, Any]) -> str:
    state = _route_state(envelope)
    state.pop("workflow_signal_fingerprint")
    state.pop("reasoning_signal_fingerprint")
    return artifact_fingerprint(state)


def _envelope_intent(envelope: Mapping[str, Any]) -> dict[str, Any]:
    content = _detached(dict(envelope))
    content.pop("route_envelope_hash", None)
    content.pop("decision_revision", None)
    return content


def _zero_budget_impact() -> dict[str, int | float]:
    return {field: 0.0 if field == "total_cost_units" else 0 for field in _BUDGET_FIELDS}


class WorkflowRouteLedger:
    """Own monotonic route revisions, idempotency, replay, and hysteresis.

    / 统一负责单调路由修订、幂等、重放与迟滞约束。
    """

    def __init__(self, path: str | Path | None = None, *, max_switches: int = 8) -> None:
        if max_switches < 1:
            raise ValueError("max_switches must be positive / max_switches 必须为正整数")
        self.path = None if path is None else Path(path)
        self.max_switches = max_switches
        self._lock = RLock()
        self._records: list[dict[str, Any]] = []
        self._idempotency: dict[str, dict[str, Any]] = {}
        if self.path is not None and self.path.exists() and self.path.stat().st_size:
            self.replay()

    @property
    def head(self) -> dict[str, Any] | None:
        with self._lock:
            if not self._records:
                return None
            return _detached(self._records[-1]["envelope"])

    @property
    def revision_events(self) -> tuple[dict[str, Any], ...]:
        with self._lock:
            return tuple(
                _detached(record["revision_event"])
                for record in self._records
                if record["record_type"] == "route_revision_commit"
            )

    @property
    def committed_records(self) -> tuple[dict[str, Any], ...]:
        """Return detached canonical records for adapters and migration.

        / 返回供适配器与迁移使用的脱离式规范记录。
        """

        with self._lock:
            return tuple(_detached(record) for record in self._records)

    @classmethod
    def from_records(
        cls,
        records: Sequence[Mapping[str, Any]],
        *,
        max_switches: int = 8,
    ) -> "WorkflowRouteLedger":
        """Validate and hydrate a ledger from an ordered committed chain.

        / 从有序已提交记录链校验并恢复账本。
        """

        ledger = cls(max_switches=max_switches)
        with ledger._lock:
            for record in records:
                ledger._validate_record(record)
                ledger._commit(record)
        return ledger

    @property
    def switch_count(self) -> int:
        return sum(
            1
            for event in self.revision_events
            if event["direction"] != "gate_only"
        )

    def register_initial(
        self,
        envelope: Mapping[str, Any],
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Commit the immutable revision-one envelope / 提交不可变的第一版路由信封。"""

        with self._lock:
            sealed = _detached(dict(envelope))
            validate_workflow_route_envelope(sealed)
            request_fingerprint = artifact_fingerprint(
                {"operation": "register_initial", "envelope": sealed}
            )
            existing = self._idempotent_result(idempotency_key, request_fingerprint)
            if existing is not None:
                return existing
            if self._records:
                raise WorkflowRouteLedgerError(
                    "initial route already exists / 初始路由已经存在"
                )
            if sealed["decision_revision"] != 1:
                raise WorkflowRouteLedgerError(
                    "initial route revision must be one / 初始路由修订号必须为一"
                )
            record = {
                "record_type": "initial_route",
                "record_sequence": 1,
                "idempotency_key": idempotency_key,
                "request_fingerprint": request_fingerprint,
                "envelope": sealed,
            }
            record["record_hash"] = _record_hash(record)
            self._validate_record(record)
            self._persist(record)
            self._commit(record)
            return _detached(sealed)

    def append_revision(
        self,
        candidate_envelope: Mapping[str, Any],
        *,
        idempotency_key: str,
        trigger_class: str,
        direction: str,
        trigger_reason_code: str,
        trigger_evidence_bindings: Sequence[Mapping[str, Any]],
        actor_binding: Mapping[str, Any],
        authority_binding: Mapping[str, Any],
        hysteresis_evidence_bindings: Sequence[Mapping[str, Any]] = (),
        budget_impact: Mapping[str, Any] | None = None,
        unfinished_step_ids: Sequence[str] = (),
        switch_event_binding: Mapping[str, Any] | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        """Atomically append one validated route or gate revision.

        / 原子追加一个经验证的路由或门禁修订。
        """

        with self._lock:
            if not self._records:
                raise WorkflowRouteLedgerError(
                    "initial route is required / 必须先登记初始路由"
                )
            raw_candidate = _detached(dict(candidate_envelope))
            validate_workflow_route_envelope(raw_candidate)
            effective_created_at = created_at or raw_candidate["created_at"]
            effective_budget = _zero_budget_impact()
            if budget_impact is not None:
                effective_budget.update(dict(budget_impact))
            effective_switch = (
                {"state": "not_applicable"}
                if switch_event_binding is None
                else _detached(dict(switch_event_binding))
            )
            request_material = {
                "operation": "append_revision",
                "candidate": _envelope_intent(raw_candidate),
                "trigger_class": trigger_class,
                "direction": direction,
                "trigger_reason_code": trigger_reason_code,
                "trigger_evidence_bindings": list(trigger_evidence_bindings),
                "hysteresis_evidence_bindings": list(hysteresis_evidence_bindings),
                "actor_binding": actor_binding,
                "authority_binding": authority_binding,
                "budget_impact": effective_budget,
                "unfinished_step_ids": list(unfinished_step_ids),
                "switch_event_binding": effective_switch,
                "created_at": effective_created_at,
            }
            request_fingerprint = artifact_fingerprint(request_material)
            existing = self._idempotent_result(idempotency_key, request_fingerprint)
            if existing is not None:
                return existing

            previous = self._records[-1]["envelope"]
            candidate = _detached(raw_candidate)
            candidate.pop("route_envelope_hash", None)
            candidate["decision_revision"] = previous["decision_revision"] + 1
            candidate["created_at"] = effective_created_at
            candidate = build_artifact("workflow_route_envelope", candidate)

            event_content = {
                "schema_version": REVISION_SCHEMA_VERSION,
                "idempotency_key": idempotency_key,
                "workflow_id": candidate["workflow_id"],
                "task_id": candidate["task_id"],
                "run_id": candidate["run_id"],
                "scene_id": candidate["scene_id"],
                "task_atom_id": candidate["task_atom"]["task_atom_id"],
                "from_decision_id": previous["decision_id"],
                "to_decision_id": candidate["decision_id"],
                "from_revision": previous["decision_revision"],
                "to_revision": candidate["decision_revision"],
                "previous_envelope_binding": _binding(previous),
                "current_envelope_binding": _binding(candidate),
                "trigger_class": trigger_class,
                "direction": direction,
                "trigger_reason_code": trigger_reason_code,
                "trigger_evidence_bindings": _detached(list(trigger_evidence_bindings)),
                "hysteresis_evidence_bindings": _detached(list(hysteresis_evidence_bindings)),
                "actor_binding": _detached(dict(actor_binding)),
                "authority_binding": _detached(dict(authority_binding)),
                "budget_impact": effective_budget,
                "unfinished_step_ids": list(unfinished_step_ids),
                "from_route": _route_state(previous),
                "to_route": _route_state(candidate),
                "switch_event_binding": effective_switch,
                "created_at": effective_created_at,
            }
            event_content["revision_event_id"] = "WORKFLOW_ROUTE_REVISION_" + artifact_fingerprint(
                event_content
            ).removeprefix("sha256:")[:24]
            revision_event = build_artifact("workflow_route_revision", event_content)
            record = {
                "record_type": "route_revision_commit",
                "record_sequence": len(self._records) + 1,
                "idempotency_key": idempotency_key,
                "request_fingerprint": request_fingerprint,
                "envelope": candidate,
                "revision_event": revision_event,
            }
            record["record_hash"] = _record_hash(record)
            self._validate_record(record)
            self._persist(record)
            self._commit(record)
            return _detached(candidate)

    def bind_run_graph(
        self,
        run_graph_binding: Mapping[str, Any],
        *,
        idempotency_key: str,
        actor_binding: Mapping[str, Any],
        authority_binding: Mapping[str, Any],
        created_at: str,
    ) -> dict[str, Any]:
        """Bind a run graph without silently changing the route / 绑定运行图且不静默换路。"""

        with self._lock:
            current = self.head
            if current is None:
                raise WorkflowRouteLedgerError(
                    "initial route is required / 必须先登记初始路由"
                )
            candidate = _detached(current)
            candidate.pop("route_envelope_hash", None)
            candidate["run_graph_binding"] = {
                "state": "observed",
                "value": _detached(dict(run_graph_binding)),
            }
            candidate["created_at"] = created_at
            candidate = build_artifact("workflow_route_envelope", candidate)
            return self.append_revision(
                candidate,
                idempotency_key=idempotency_key,
                trigger_class="external_state_change",
                direction="gate_only",
                trigger_reason_code="RUN_GRAPH_BOUND",
                trigger_evidence_bindings=[run_graph_binding],
                actor_binding=actor_binding,
                authority_binding=authority_binding,
                created_at=created_at,
            )

    def replay(self) -> dict[str, Any] | None:
        """Fail closed while reconstructing the committed head / 默认阻断地重建已提交头部。"""

        with self._lock:
            if self.path is None or not self.path.exists():
                return None
            payload = self.path.read_bytes()
            if payload and not payload.endswith(b"\n"):
                raise WorkflowRouteLedgerError(
                    "ledger ends with a partial record / 账本尾部存在半条记录"
                )
            self._records = []
            self._idempotency = {}
            for line_number, line in enumerate(payload.splitlines(), start=1):
                if not line.strip():
                    raise WorkflowRouteLedgerError(
                        f"blank ledger record at line {line_number} / 第 {line_number} 行为空记录"
                    )
                try:
                    record = json.loads(line.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise WorkflowRouteLedgerError(
                        f"invalid ledger record at line {line_number} / 第 {line_number} 行记录无效"
                    ) from exc
                self._validate_record(record)
                self._commit(record)
            return self.head

    def _idempotent_result(
        self,
        idempotency_key: str,
        request_fingerprint: str,
    ) -> dict[str, Any] | None:
        existing = self._idempotency.get(idempotency_key)
        if existing is None:
            return None
        if existing["request_fingerprint"] != request_fingerprint:
            raise WorkflowRouteLedgerError(
                "idempotency key was reused for different content / 幂等键被用于不同内容"
            )
        return _detached(existing["envelope"])

    def _validate_record(self, record: Mapping[str, Any]) -> None:
        expected_common = {
            "record_type",
            "record_sequence",
            "idempotency_key",
            "request_fingerprint",
            "envelope",
            "record_hash",
        }
        expected = set(expected_common)
        if record.get("record_type") == "route_revision_commit":
            expected.add("revision_event")
        if set(record) != expected:
            raise WorkflowRouteLedgerError(
                "ledger record fields are not canonical / 账本记录字段不符合规范"
            )
        if record["record_hash"] != _record_hash(record):
            raise WorkflowRouteLedgerError(
                "ledger record hash mismatch / 账本记录哈希不匹配"
            )
        if record["record_sequence"] != len(self._records) + 1:
            raise WorkflowRouteLedgerError(
                "ledger record sequence is not monotonic / 账本记录序号不单调"
            )
        if record["idempotency_key"] in self._idempotency:
            raise WorkflowRouteLedgerError(
                "duplicate persisted idempotency key / 持久化账本存在重复幂等键"
            )
        validate_workflow_route_envelope(record["envelope"])

        if record["record_type"] == "initial_route":
            expected_request_fingerprint = artifact_fingerprint(
                {"operation": "register_initial", "envelope": record["envelope"]}
            )
            if record["request_fingerprint"] != expected_request_fingerprint:
                raise WorkflowRouteLedgerError(
                    "initial request fingerprint mismatch / 初始请求指纹不匹配"
                )
            if self._records or record["envelope"]["decision_revision"] != 1:
                raise WorkflowRouteLedgerError(
                    "invalid initial route record / 初始路由记录无效"
                )
            return
        if record["record_type"] != "route_revision_commit" or not self._records:
            raise WorkflowRouteLedgerError(
                "revision record has no committed parent / 修订记录没有已提交父记录"
            )

        event = record["revision_event"]
        candidate = record["envelope"]
        previous = self._records[-1]["envelope"]
        validate_workflow_route_revision(event)
        if event["idempotency_key"] != record["idempotency_key"]:
            raise WorkflowRouteLedgerError(
                "revision and ledger idempotency keys differ / 修订事件与账本幂等键不一致"
            )
        expected_request_fingerprint = artifact_fingerprint(
            {
                "operation": "append_revision",
                "candidate": _envelope_intent(candidate),
                "trigger_class": event["trigger_class"],
                "direction": event["direction"],
                "trigger_reason_code": event["trigger_reason_code"],
                "trigger_evidence_bindings": event["trigger_evidence_bindings"],
                "hysteresis_evidence_bindings": event[
                    "hysteresis_evidence_bindings"
                ],
                "actor_binding": event["actor_binding"],
                "authority_binding": event["authority_binding"],
                "budget_impact": event["budget_impact"],
                "unfinished_step_ids": event["unfinished_step_ids"],
                "switch_event_binding": event["switch_event_binding"],
                "created_at": event["created_at"],
            }
        )
        if record["request_fingerprint"] != expected_request_fingerprint:
            raise WorkflowRouteLedgerError(
                "revision request fingerprint mismatch / 修订请求指纹不匹配"
            )
        scope_fields = ("workflow_id", "task_id", "run_id", "scene_id")
        if any(candidate[field] != previous[field] for field in scope_fields):
            raise WorkflowRouteLedgerError(
                "route revision changed workflow identity / 路由修订改变了工作流身份"
            )
        if any(event[field] != candidate[field] for field in scope_fields):
            raise WorkflowRouteLedgerError(
                "revision event scope differs from envelope / 修订事件作用域与信封不一致"
            )
        if event["task_atom_id"] != candidate["task_atom"]["task_atom_id"]:
            raise WorkflowRouteLedgerError(
                "revision event task atom differs from envelope / "
                "修订事件任务原子与信封不一致"
            )
        if (
            event["from_decision_id"] != previous["decision_id"]
            or event["to_decision_id"] != candidate["decision_id"]
        ):
            raise WorkflowRouteLedgerError(
                "revision decision identities do not match the envelope chain / "
                "修订决定标识与信封链不一致"
            )
        if candidate["task_atom"] != previous["task_atom"]:
            raise WorkflowRouteLedgerError(
                "route revision changed the task atom / 路由修订改变了任务原子"
            )
        if event["previous_envelope_binding"] != _binding(previous):
            raise WorkflowRouteLedgerError(
                "revision does not bind the committed parent / 修订未绑定已提交父记录"
            )
        if event["current_envelope_binding"] != _binding(candidate):
            raise WorkflowRouteLedgerError(
                "revision does not bind the candidate envelope / 修订未绑定候选信封"
            )
        if event["from_revision"] != previous["decision_revision"] or event[
            "to_revision"
        ] != candidate["decision_revision"]:
            raise WorkflowRouteLedgerError(
                "revision numbers do not match envelope chain / 修订号与信封链不一致"
            )
        if event["from_route"] != _route_state(previous) or event["to_route"] != _route_state(
            candidate
        ):
            raise WorkflowRouteLedgerError(
                "revision route states do not match envelopes / 修订路由状态与信封不一致"
            )
        self._validate_transition(previous, candidate, event)

    def _validate_transition(
        self,
        previous: Mapping[str, Any],
        candidate: Mapping[str, Any],
        event: Mapping[str, Any],
    ) -> None:
        route_changed = _operational_signature(previous) != _operational_signature(candidate)
        same_frozen_inputs = (
            previous["workflow_signal_fingerprint"]
            == candidate["workflow_signal_fingerprint"]
            and previous["reasoning_decision"]["signal_fingerprint"]
            == candidate["reasoning_decision"]["signal_fingerprint"]
        )
        if route_changed and same_frozen_inputs:
            raise WorkflowRouteLedgerError(
                "same frozen inputs produced a different route / 同一冻结输入产生了不同路由"
            )
        if not route_changed and event["direction"] != "gate_only":
            raise WorkflowRouteLedgerError(
                "route switch did not change operational route / 路由切换未改变实际路由"
            )
        if event["direction"] == "gate_only":
            if route_changed:
                raise WorkflowRouteLedgerError(
                    "gate-only revision changed the operational route / 纯门禁修订改变了实际路由"
                )
            if _envelope_intent(previous) == _envelope_intent(candidate):
                raise WorkflowRouteLedgerError(
                    "gate-only revision changed no bound state / 纯门禁修订未改变任何绑定状态"
                )

        if route_changed and self.switch_count >= self.max_switches:
            raise WorkflowRouteLedgerError(
                "route switch budget exhausted / 路由切换预算已耗尽"
            )
        if event["direction"] == "deescalation":
            if not event["hysteresis_evidence_bindings"]:
                raise WorkflowRouteLedgerError(
                    "deescalation lacks hysteresis evidence / 降级缺少迟滞证据"
                )
            if any(item["severity"] == "critical" for item in candidate["blockers"]):
                raise WorkflowRouteLedgerError(
                    "deescalation retained critical blockers / 降级后仍有关键阻断项"
                )
            if any(
                signal["value"]["state"] in {"missing", "unknown"}
                for signal in candidate["workflow_signals"]
            ):
                raise WorkflowRouteLedgerError(
                    "deescalation retained unresolved route signals / 降级后仍有未解决路由信号"
                )

        candidate_signature = _operational_signature(candidate)
        historical_signatures = {
            _operational_signature(record["envelope"])
            for record in self._records[:-1]
        }
        if route_changed and candidate_signature in historical_signatures:
            if not event["hysteresis_evidence_bindings"]:
                raise WorkflowRouteLedgerError(
                    "route oscillation requires hysteresis evidence / 路由往返振荡必须具有迟滞证据"
                )
            if candidate["workflow_signal_fingerprint"] == previous[
                "workflow_signal_fingerprint"
            ]:
                raise WorkflowRouteLedgerError(
                    "route oscillation requires changed workflow evidence / 路由往返必须具有变化后的工作流证据"
                )

    def _persist(self, record: Mapping[str, Any]) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("ab") as stream:
            stream.write(_canonical_bytes(record))
            stream.flush()
            os.fsync(stream.fileno())

    def _commit(self, record: Mapping[str, Any]) -> None:
        committed = _detached(dict(record))
        self._records.append(committed)
        self._idempotency[committed["idempotency_key"]] = committed


__all__ = [
    "WorkflowRouteLedger",
    "WorkflowRouteLedgerError",
]
