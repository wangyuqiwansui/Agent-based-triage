"""Source-aligned, read-only collaboration measurements / 对齐全文的只读协作计量。

Adapters provide authenticated, scoped datasets with independent populations.
Missing inputs affect only dependent metrics. This module never runs business
work, issues approvals, repairs source records or treats metric values as gates.
/ 适配器提供经过认证、范围明确且有独立预期集合的数据集。缺输入只影响依赖指标；
本模块不执行业务、不审批、不修复源记录，也不把指标值作为业务闸门。
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import math
import re
from statistics import mean, median
from typing import Any, Callable, Mapping, Sequence

try:
    from .collaboration_protocol import CollaborationContractError, digest, _time
except ImportError:
    from collaboration_protocol import CollaborationContractError, digest, _time


SOURCE_METRIC_IDS = tuple(f"CSM{i:02d}" for i in range(1, 35))
IMPLEMENTED_METRICS = tuple(f"CSM{i:02d}" for i in (1, 2, 7, 8, 9, 12, 13, 18, 19, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34))
DEFAULT_SOURCE_METRICS = ("CSM01", "CSM02", "CSM07", "CSM08", "CSM09", "CSM13", "CSM18")
METRIC_UNITS = {key: "ratio" for key in SOURCE_METRIC_IDS}
METRIC_UNITS.update({f"CSM{i:02d}": "count" for i in (12, 20, 25, 26)})
METRIC_UNITS.update({f"CSM{i:02d}": "seconds" for i in (11, 16, 21, 28)})
METRIC_UNITS.update({f"CSM{i:02d}": "multiple" for i in (13, 29, 30)})
METRIC_UNITS.update(CSM31="score_points_or_percentage_points", CSM34="percentage_points")


class MeasurementUnavailable(ValueError):
    """A local measurement cannot be supported / 某项局部计量依据不足。"""


def _number(value: Any, *, positive: bool = False) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise MeasurementUnavailable("invalid_number")
    return value


def _boolean(value: Any) -> bool:
    if type(value) is not bool:
        raise MeasurementUnavailable("unknown_fact")
    return value


def _binding(value: Any, *, location: bool = False) -> dict[str, Any]:
    """Require an explicit version and digest, not an adapter label / 要求显式版本摘要，不接受适配标签。"""
    if (not isinstance(value, dict) or not isinstance(value.get("id"), str) or not value["id"].strip()
            or type(value.get("revision")) is not int or value["revision"] < 1
            or not isinstance(value.get("hash"), str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", value["hash"])):
        raise MeasurementUnavailable("missing_version_digest_binding")
    result = {key: value[key] for key in ("id", "revision", "hash")}
    if location:
        if not isinstance(value.get("location"), str) or not value["location"].strip():
            raise MeasurementUnavailable("missing_source_location")
        result["location"] = value["location"]
    return result


class _Observation:
    def __init__(self, source: Mapping[str, Any], verify: Callable[[Mapping[str, Any]], bool]):
        self.source = deepcopy(dict(source))
        for key in ("local_profile_version", "source_contract_version", "observation_id", "tenant_id", "run_id", "plan_revision", "cutoff", "window_start", "modes", "datasets"):
            if key not in self.source:
                raise CollaborationContractError("missing_observation_field:" + key)
        if self.source["local_profile_version"] != "3.0.0" or self.source["source_contract_version"] != "2.0.0":
            raise CollaborationContractError("unsupported_observation_profile")
        if type(self.source["plan_revision"]) is not int or self.source["plan_revision"] < 1:
            raise CollaborationContractError("invalid_observation_plan")
        if any(not isinstance(self.source[key], str) or not self.source[key].strip()
               for key in ("observation_id", "tenant_id", "run_id")):
            raise CollaborationContractError("invalid_observation_identity")
        if not isinstance(self.source["datasets"], dict) or not isinstance(self.source["modes"], list):
            raise CollaborationContractError("invalid_observation_collections")
        modes = self.source["modes"]
        if (any(not isinstance(mode, str) or mode not in {"hierarchical_delegation", "fan_out_gather", "adversarial_review", "handoff_chain"}
                for mode in modes) or len(set(modes)) != len(modes)):
            raise CollaborationContractError("invalid_observation_modes")
        self.cutoff = _time(self.source["cutoff"])
        self.start = _time(self.source["window_start"])
        if self.start > self.cutoff:
            raise CollaborationContractError("invalid_observation_window")
        try:
            trusted = verify(deepcopy(self.source)) is True
        except Exception:
            trusted = False
        if not trusted:
            raise CollaborationContractError("untrusted_observation")
        self.used_sources: set[str] = set()
        self.used_datasets: set[str] = set()

    def rows(self, name: str, *, exact: bool = True) -> list[dict[str, Any]]:
        dataset = self.source["datasets"].get(name)
        self.used_datasets.add(name)
        if not isinstance(dataset, dict) or not dataset.get("source_refs"):
            raise MeasurementUnavailable("missing_dataset:" + name)
        if not isinstance(dataset.get("rows"), list) or not isinstance(dataset["source_refs"], list):
            raise MeasurementUnavailable("invalid_dataset:" + name)
        if any(not isinstance(ref, str) or not ref for ref in dataset["source_refs"]):
            raise MeasurementUnavailable("invalid_provenance:" + name)
        self.used_sources.update(dataset["source_refs"])
        if exact and dataset.get("complete") is not True:
            raise MeasurementUnavailable("incomplete_dataset:" + name)
        by_id = {}
        for row in dataset["rows"]:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
                raise MeasurementUnavailable("missing_record_id:" + name)
            if row["id"] in by_id and digest(by_id[row["id"]]) != digest(row):
                raise MeasurementUnavailable("conflicting_record:" + name)
            by_id[row["id"]] = row
        return list(by_id.values())

    def complete(self, name: str) -> bool:
        return self.source["datasets"].get(name, {}).get("complete") is True

    def clock(self, name: str) -> None:
        if self.source["datasets"][name].get("comparable_clock") is not True:
            raise MeasurementUnavailable("incomparable_clock:" + name)


def _result(value=None, *, state="computable", unit="ratio", numerator=None, denominator=None,
            sample_count=0, reason=None, **extra) -> dict[str, Any]:
    return dict(value=value, state=state, unit=unit, numerator=numerator, denominator=denominator,
                sample_count=sample_count, reason=reason, **extra)


def _ratio(numerator, denominator, *, unit="ratio", sample_count=0, **extra):
    numerator, denominator = _number(numerator), _number(denominator)
    if denominator == 0:
        return _result(state="not_applicable", unit=unit, numerator=numerator, denominator=0,
                       sample_count=sample_count, reason="empty_population", **extra)
    return _result(numerator / denominator, unit=unit, numerator=numerator, denominator=denominator,
                   sample_count=sample_count, **extra)


def _weighted_coverage(obs: _Observation, *, accepted: bool):
    units = obs.rows("coverage")
    assignments = [] if accepted else obs.rows("assignments")
    assigned = set()
    unit_ids = {item["id"] for item in units}
    for row in assignments:
        if row["unit_id"] not in unit_ids:
            raise MeasurementUnavailable("unknown_coverage_unit")
        if _boolean(row["active"]) and row["role"] == "primary":
            assigned.add(row["unit_id"])
    numerator = denominator = 0
    population = 0
    for unit in units:
        weight = _number(unit["weight"], positive=True)
        if _boolean(unit["required"]):
            population += 1
            denominator += weight
            if (_boolean(unit["accepted"]) if accepted else unit["id"] in assigned):
                numerator += weight
    return _ratio(numerator, denominator, sample_count=population)


def _duplicate_assignments(obs: _Observation):
    units = obs.rows("coverage")
    assignments = obs.rows("assignments")
    exclusive = {item["id"] for item in units if _boolean(item["exclusive"])}
    known_units = {item["id"] for item in units}
    relations = set()
    for row in assignments:
        if row["unit_id"] not in known_units:
            raise MeasurementUnavailable("unknown_coverage_unit")
        if _boolean(row["active"]) and row["role"] == "primary" and row["unit_id"] in exclusive:
            relations.add((row["unit_id"], row["task_id"]))
    extra = sum(max(sum(unit == key for unit, _ in relations) - 1, 0) for key in exclusive)
    return _ratio(extra, len(relations), sample_count=len(relations))


def _first_acceptance(obs: _Observation):
    rows = obs.rows("local_dispositions")
    earliest = {}
    for row in rows:
        ordinal = _number(row["disposition_order"])
        if type(ordinal) is not int or row["decision"] not in {"passed", "returned", "rejected", "needs_evidence", "pending"}:
            raise MeasurementUnavailable("invalid_disposition")
        if row["decision"] == "pending":
            continue
        previous = earliest.get(row["task_id"])
        if previous is not None and previous["disposition_order"] == ordinal and previous != row:
            raise MeasurementUnavailable("conflicting_first_disposition")
        if previous is None or ordinal < previous["disposition_order"]:
            earliest[row["task_id"]] = row
    return _ratio(sum(row["decision"] == "passed" for row in earliest.values()), len(earliest),
                  sample_count=len(earliest), pending_count=sum(row["decision"] == "pending" for row in rows))


def _completed(row):
    states = {"completed", "partial", "failed", "timed_out", "not_started", "running", "blocked", "rejected", "terminated"}
    if row["state"] not in states:
        raise MeasurementUnavailable("unknown_run_state")
    return row["state"] == "completed" and _boolean(row["global_accepted"]) and _boolean(row["delivered"])


def _closed_completion(obs: _Observation):
    rows = obs.rows("closed_runs")
    obs.clock("closed_runs")
    closed = []
    open_count = 0
    for row in rows:
        _completed(row)
        if row["closed_at"] is None:
            open_count += 1
        elif obs.start <= _time(row["closed_at"]) <= obs.cutoff:
            closed.append(row)
    return _ratio(sum(_completed(row) for row in closed), len(closed), sample_count=len(closed),
                  open_count=open_count, window_start=obs.source["window_start"], window_end=obs.source["cutoff"])


def _unresolved(obs: _Observation, name: str):
    rows = obs.rows(name, exact=False)
    obs.clock(name)
    count = 0
    for row in rows:
        if name == "objections":
            _binding(row["artifact_binding"])
            if not _boolean(row["blocking"]):
                continue
        if not _boolean(row["confirmed"]):
            continue
        if _time(row["raised_at"]) <= obs.cutoff and (row["resolved_at"] is None or _time(row["resolved_at"]) > obs.cutoff):
            count += 1
    if not obs.complete(name):
        return _result(state="partial_observation", unit="count", sample_count=len(rows),
                       confirmed_lower_bound=count, reason="incomplete_register")
    return _result(count, unit="count", sample_count=len(rows))


def _attempts(obs: _Observation):
    rows = obs.rows("attempts")
    if any(row["domain"] not in {"business", "probe"} for row in rows):
        raise MeasurementUnavailable("unknown_attempt_domain")
    business = [row for row in rows if row["domain"] == "business" and _boolean(row["started"])]
    return _ratio(len(business), len({row["task_id"] for row in business}), unit="multiple", sample_count=len(business))


def _collection(obs: _Observation):
    expected, received = obs.rows("record_obligations"), obs.rows("received_records")
    if obs.source["datasets"]["record_obligations"].get("watermark_closed") is not True:
        raise MeasurementUnavailable("producer_watermark_not_closed")
    expected_ids = {row["id"] for row in expected}
    return _ratio(len(expected_ids & {row["id"] for row in received}), len(expected_ids), sample_count=len(expected_ids))


def _probe_cost(obs: _Observation):
    rows = obs.rows("costs")
    units = {row["unit"] for row in rows}
    if len(units) > 1:
        raise MeasurementUnavailable("mixed_cost_units")
    if any(row["domain"] not in {"business", "probe"} for row in rows):
        raise MeasurementUnavailable("unknown_cost_domain")
    total = sum(_number(row["value"]) for row in rows)
    probe = sum(_number(row["value"]) for row in rows if row["domain"] == "probe")
    return _ratio(probe, total, sample_count=len(rows), cost_unit=next(iter(units), None))


def _isolation(obs: _Observation):
    rows = obs.rows("isolation")
    groups = {}
    required = [row for row in rows if _boolean(row["required"])]
    for kind in ("configuration", "execution"):
        group = [row for row in required if row["check_type"] == kind]
        groups[kind] = _ratio(sum(_boolean(row["verified"]) for row in group), len(group), sample_count=len(group))
    if any(row["check_type"] not in groups for row in rows):
        raise MeasurementUnavailable("unknown_isolation_check_type")
    return _ratio(sum(_boolean(row["verified"]) for row in required), len(required), sample_count=len(required), groups=groups)


def _citations(obs: _Observation):
    rows = obs.rows("citations")
    if any(row["origin_binding"] is None for row in rows):
        raise MeasurementUnavailable("unresolved_source_lineage")
    # Adapter evidence identifies original record + version + location; domains
    # or model identities cannot stand in for this. / 原记录、版本与定位来自适配证据，域名或模型身份不能替代。
    origins = {digest(_binding(row["origin_binding"], location=True)) for row in rows}
    return _ratio(len(rows) - len(origins), len(rows), sample_count=len(rows))


def _historical_release(obs: _Observation):
    objections, releases = obs.rows("objections"), obs.rows("releases")
    obs.clock("objections")
    obs.clock("releases")
    violated = set()
    for release in releases:
        at = _time(release["released_at"])
        if at > obs.cutoff:
            continue
        if any(_binding(row["artifact_binding"]) == _binding(release["artifact_binding"])
               and _boolean(row["blocking"]) and _boolean(row["confirmed"])
               and _time(row["raised_at"]) <= at
               and (row["resolved_at"] is None or _time(row["resolved_at"]) > at) for row in objections):
            violated.add(digest(_binding(release["artifact_binding"])))
    return _result(len(violated), unit="count", sample_count=len(releases))


def _handoff_matches(obs: _Observation):
    rows = obs.rows("handoffs")
    if any(row["disposition"] not in {"accepted", "rejected", "expired", "version_conflict", "pending"} for row in rows):
        raise MeasurementUnavailable("unknown_handoff_disposition")
    disposed = [row for row in rows if row["disposition"] != "pending"]
    if any(row["artifact_binding"] is None or row["acceptance_binding"] is None for row in disposed):
        raise MeasurementUnavailable("unreadable_handoff_version")
    return _ratio(sum(_binding(row["artifact_binding"]) == _binding(row["acceptance_binding"]) for row in disposed),
                  len(disposed), sample_count=len(disposed), pending_count=len(rows) - len(disposed))


def _timing(obs: _Observation, *, convergence: bool = False):
    rows = obs.rows("timing")
    obs.clock("timing")
    if not rows:
        return _result(state="not_applicable", unit="ratio" if convergence else "seconds", reason="empty_population")
    if len(rows) != 1:
        raise MeasurementUnavailable("one_run_timing_required")
    row = rows[0]
    start = _time(row["started_at"])
    endpoint = "global_acceptance" if convergence else row["endpoint"]
    if endpoint not in {"global_acceptance", "delivery"}:
        raise MeasurementUnavailable("unknown_timing_endpoint")
    end_value = row["accepted_at"] if endpoint == "global_acceptance" else row["delivered_at"]
    if end_value is None:
        if start > obs.cutoff:
            raise MeasurementUnavailable("invalid_time_order")
        return _result(state="partial_observation", unit="ratio" if convergence else "seconds",
                       age_seconds=(obs.cutoff - start).total_seconds(), reason="run_open", endpoint=endpoint)
    end = _time(end_value)
    if not start <= end <= obs.cutoff:
        raise MeasurementUnavailable("invalid_time_order")
    duration = (end - start).total_seconds()
    if not convergence:
        return _result(duration, unit="seconds", sample_count=1, endpoint=endpoint)
    branches = [branch for branch in row["branches"] if _boolean(branch["required"]) and _boolean(branch["used_in_final"])]
    if not branches:
        return _result(state="not_applicable", reason="no_parallel_branches")
    ready_times = [_time(branch["ready_at"]) for branch in branches]
    if not all(start <= ready <= end for ready in ready_times):
        raise MeasurementUnavailable("invalid_convergence_order")
    ready = max(ready_times)
    return _ratio((end - ready).total_seconds(), duration, sample_count=len(branches))


def _baseline(obs: _Observation, metric: str):
    cohort = obs.rows("cohort")
    runs = obs.rows("comparison_runs")
    settings = obs.source.get("comparison", {})
    if settings.get("statistic") not in {"mean", "median"}:
        raise MeasurementUnavailable("missing_predeclared_statistic")
    statistic = mean if settings["statistic"] == "mean" else median
    expected = {row["id"]: row for row in cohort}
    pairs = {identifier: {} for identifier in expected}
    for row in runs:
        if row["task_id"] not in pairs or row["arm"] not in {"baseline", "collaboration"}:
            raise MeasurementUnavailable("unexpected_comparison_run")
        pair = pairs[row["task_id"]]
        if row["arm"] in pair:
            raise MeasurementUnavailable("duplicate_comparison_arm")
        if any(_binding(row[field]) != _binding(expected[row["task_id"]][field]) for field in ("input_binding", "criteria_binding")):
            raise MeasurementUnavailable("incomparable_cohort")
        _completed(row)
        pair[row["arm"]] = row
    if any(set(pair) != {"baseline", "collaboration"} for pair in pairs.values()):
        raise MeasurementUnavailable("missing_enrolled_run")
    if not pairs:
        return _result(state="not_applicable", reason="empty_population")
    arms = {arm: [pair[arm] for pair in pairs.values()] for arm in ("baseline", "collaboration")}
    states = {arm: {state: sum(row["state"] == state for row in rows) for state in sorted({row["state"] for row in rows})}
              for arm, rows in arms.items()}
    if metric == "CSM34":
        base_count, collab_count = (sum(_completed(row) for row in arms[arm]) for arm in ("baseline", "collaboration"))
        return _result(100 * (collab_count - base_count) / len(pairs), unit="percentage_points", sample_count=len(pairs),
                       baseline_completed=base_count, collaboration_completed=collab_count, enrolled_per_arm=len(pairs), states=states)
    if metric == "CSM29":
        if settings.get("duration_endpoint") not in {"global_acceptance", "delivery"}:
            raise MeasurementUnavailable("missing_predeclared_duration_endpoint")
        common = [pair for pair in pairs.values() if all(_completed(row) for row in pair.values())]
        if not common:
            return _result(state="not_applicable", unit="multiple", reason="no_common_completed_pairs", states=states)
        obs.clock("comparison_runs")
        values = {arm: statistic(_number(pair[arm]["duration_seconds"], positive=True) for pair in common) for arm in arms}
        return _ratio(values["baseline"], values["collaboration"], unit="multiple", sample_count=len(common),
                      common_pair_share=len(common) / len(pairs), states=states, endpoint=settings["duration_endpoint"])
    if metric == "CSM30":
        units = {row["resource_unit"] for row in runs}
        if len(units) != 1 or next(iter(units)) != settings.get("resource_unit"):
            raise MeasurementUnavailable("mixed_resource_units")
        if any(row["costs_complete"] is not True for row in runs):
            raise MeasurementUnavailable("incomplete_cost_ledger")
        total = {arm: sum(_number(row["resource_value"]) for row in rows) for arm, rows in arms.items()}
        return _ratio(total["collaboration"], total["baseline"], unit="multiple", sample_count=len(pairs), resource_unit=next(iter(units)), states=states)
    if any(row["quality_verified"] is not True or row["quality_unit"] != settings.get("quality_unit") for row in runs):
        raise MeasurementUnavailable("unverified_or_incomparable_quality")
    if settings.get("quality_unit") not in {"score_points", "ratio"}:
        raise MeasurementUnavailable("unknown_quality_unit")
    if settings["quality_unit"] == "ratio" and any(_number(row["quality_score"]) > 1 for row in runs):
        raise MeasurementUnavailable("invalid_quality_ratio")
    scores = {arm: statistic(_number(row["quality_score"]) for row in rows) for arm, rows in arms.items()}
    multiplier = 100 if settings["quality_unit"] == "ratio" else 1
    return _result(multiplier * (scores["collaboration"] - scores["baseline"]),
                   unit="percentage_points" if multiplier == 100 else "score_points", sample_count=len(pairs), states=states)


def calculate_source_metrics(observation: Mapping[str, Any], *, verify_observation: Callable[[Mapping[str, Any]], bool],
                             enabled_metrics: Sequence[str] = DEFAULT_SOURCE_METRICS) -> dict[str, Any]:
    """Calculate source-numbered metrics without starting execution / 无需启动执行，计算全文编号指标。"""
    if len(set(enabled_metrics)) != len(enabled_metrics) or any(key not in SOURCE_METRIC_IDS for key in enabled_metrics):
        raise CollaborationContractError("unknown_source_metric")
    obs = _Observation(observation, verify_observation)
    calculators = {
        "CSM01": lambda: _weighted_coverage(obs, accepted=False), "CSM02": lambda: _duplicate_assignments(obs),
        "CSM07": lambda: _first_acceptance(obs), "CSM08": lambda: _weighted_coverage(obs, accepted=True),
        "CSM09": lambda: _closed_completion(obs), "CSM12": lambda: _unresolved(obs, "conflicts"),
        "CSM13": lambda: _attempts(obs), "CSM18": lambda: _collection(obs), "CSM19": lambda: _probe_cost(obs),
        "CSM23": lambda: _isolation(obs), "CSM24": lambda: _citations(obs),
        "CSM25": lambda: _unresolved(obs, "objections"), "CSM26": lambda: _historical_release(obs),
        "CSM27": lambda: _handoff_matches(obs), "CSM28": lambda: _timing(obs),
        "CSM29": lambda: _baseline(obs, "CSM29"), "CSM30": lambda: _baseline(obs, "CSM30"),
        "CSM31": lambda: _baseline(obs, "CSM31"), "CSM32": lambda: _timing(obs, convergence=True),
        "CSM34": lambda: _baseline(obs, "CSM34"),
    }
    metrics = {}
    for key in enabled_metrics:
        obs.used_sources.clear()
        obs.used_datasets.clear()
        unavailable = dict(unit=METRIC_UNITS[key], sample_count=None)
        try:
            if key in {"CSM25", "CSM26"} and "adversarial_review" not in obs.source["modes"]:
                result = _result(state="not_applicable", reason="review_not_enabled", **unavailable)
            elif key == "CSM32" and "fan_out_gather" not in obs.source["modes"]:
                result = _result(state="not_applicable", reason="parallel_not_enabled", **unavailable)
            elif key not in calculators:
                result = _result(state="not_computable", reason="measurement_adapter_required", **unavailable)
            else:
                result = calculators[key]()
        except (MeasurementUnavailable, CollaborationContractError, KeyError, TypeError, ValueError) as error:
            result = _result(state="not_computable", reason=str(error), **unavailable)
        result.update(metric_id=key, source_id="指" + key[-2:], rule_version="1",
                      evidence_refs=sorted(obs.used_sources), datasets=sorted(obs.used_datasets),
                      completeness=("unknown" if not obs.used_datasets else "complete"
                                    if all(obs.complete(name) for name in obs.used_datasets) else "incomplete"),
                      scope={key: deepcopy(obs.source[key]) for key in ("tenant_id", "run_id", "plan_revision", "cutoff", "window_start")},
                      deduplication="stable record identity within the frozen scope / 冻结范围内按稳定记录标识去重")
        metrics[key] = result
    return {"observation_id": obs.source["observation_id"], "observation_hash": digest(obs.source),
            "source_contract_version": "2.0.0", "local_profile_version": "3.0.0", "metrics": metrics,
            "business_state_changed": False}
