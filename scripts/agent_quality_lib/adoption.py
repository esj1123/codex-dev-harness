from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
import re
from typing import Any

from scripts.agent_quality_lib.aggregation import validate_aggregate_record
from scripts.agent_quality_lib.contracts import safe_repo_path, sha256_json


_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40,64}$")
_BLOCKER_FIELDS = (
    "critical_failure_count",
    "scope_violation_count",
    "safety_violation_count",
    "contract_reopen_count",
    "semantic_blocker_count",
)
_REGRESSION_MAX_FIELDS = (
    "postflight_block_count",
    "integration_fix_file_count",
    "integration_fix_line_count",
    "holdout_failed_count",
)
_RATE_FIELDS = (
    "strict_pass_3_task_rate",
    "strict_pass_5_critical_rate",
)
_METRIC_FIELDS = (
    *_RATE_FIELDS,
    *_BLOCKER_FIELDS,
    *_REGRESSION_MAX_FIELDS,
    "holdout_passed_count",
)
_BASELINE_KEYS = {
    "schema_version",
    "baseline_id",
    "status",
    "decision",
    "suite_id",
    "suite_manifest_hash",
    "configuration_id",
    "source_basis",
    "task_count",
    "run_count",
    "metrics",
    "run_evidence_manifest",
    "run_manifest_hash",
    "evidence_refs",
    "approval_ref",
    "created_at",
    "release_artifact",
    "performed_actions",
}
_HASH = re.compile(r"^[0-9a-f]{64}$")
def _metrics(record: Mapping[str, Any]) -> Mapping[str, int | float]:
    metrics = record.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("record metrics must be an object")
    missing = [field for field in _METRIC_FIELDS if field not in metrics]
    if missing:
        raise ValueError(f"record metrics missing fields: {','.join(missing)}")
    if set(metrics) != set(_METRIC_FIELDS):
        raise ValueError("record metrics contain unexpected fields")
    for field in _RATE_FIELDS:
        value = metrics[field]
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not 0.0 <= value <= 1.0
        ):
            raise ValueError(f"record metric is invalid: {field}")
    for field in set(_METRIC_FIELDS) - set(_RATE_FIELDS):
        value = metrics[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"record metric is invalid: {field}")
    return metrics


def _valid_created_at(value: str) -> bool:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return False
    return parsed.tzinfo is not None


def _validate_source_basis(source_basis: Mapping[str, Any]) -> dict[str, str]:
    if set(source_basis) != {"harness_commit", "target_commit"}:
        raise ValueError("source_basis must contain exact commit keys")
    normalized: dict[str, str] = {}
    for field in ("harness_commit", "target_commit"):
        value = source_basis[field]
        if not isinstance(value, str) or not _GIT_SHA.fullmatch(value):
            raise ValueError(f"invalid source basis field: {field}")
        normalized[field] = value
    return normalized


def _baseline_ready(
    aggregate: Mapping[str, Any], suite: Mapping[str, Any]
) -> bool:
    try:
        aggregate = validate_aggregate_record(aggregate, suite=suite)
    except ValueError:
        return False
    metrics = _metrics(aggregate)
    return (
        aggregate.get("status") == "PASS"
        and aggregate.get("comparability") == "FULL"
        and all(metrics[field] == 1.0 for field in _RATE_FIELDS)
        and all(metrics[field] == 0 for field in _BLOCKER_FIELDS)
        and metrics["postflight_block_count"] == 0
        and metrics["holdout_passed_count"] == aggregate["run_count"]
        and metrics["holdout_failed_count"] == 0
    )


def validate_baseline_record(
    record: Mapping[str, Any], suite: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Validate one complete tracked baseline artifact."""

    if not isinstance(record, Mapping) or set(record) != _BASELINE_KEYS:
        raise ValueError("baseline key set is invalid")
    if record.get("schema_version") != "1":
        raise ValueError("baseline schema_version is invalid")
    if record.get("status") != "PASS WITH NOTES":
        raise ValueError("baseline status is invalid")
    if record.get("decision") != "PROVISIONAL_BASELINE_ACCEPTED":
        raise ValueError("baseline decision is invalid")
    for field in ("suite_id", "approval_ref"):
        if not isinstance(record.get(field), str) or not _SAFE_IDENTIFIER.fullmatch(
            record[field]
        ):
            raise ValueError(f"baseline {field} is invalid")
    for field in ("suite_manifest_hash", "configuration_id", "run_manifest_hash"):
        if not isinstance(record.get(field), str) or not _HASH.fullmatch(record[field]):
            raise ValueError(f"baseline {field} is invalid")
    source_basis = record.get("source_basis")
    if not isinstance(source_basis, Mapping):
        raise ValueError("baseline source_basis is invalid")
    _validate_source_basis(source_basis)
    for field in ("task_count", "run_count"):
        value = record.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"baseline {field} is invalid")
    metrics = _metrics(record)
    if (
        any(metrics[field] != 1.0 for field in _RATE_FIELDS)
        or any(metrics[field] != 0 for field in _BLOCKER_FIELDS)
        or metrics["postflight_block_count"] != 0
        or metrics["holdout_failed_count"] != 0
        or metrics["holdout_passed_count"] != record["run_count"]
    ):
        raise ValueError("baseline metrics are not adoption-eligible")
    refs = record.get("evidence_refs")
    if (
        not isinstance(refs, list)
        or len(refs) > 20
        or len(refs) != len(set(refs))
        or any(not safe_repo_path(ref) for ref in refs)
    ):
        raise ValueError("baseline evidence_refs are invalid")
    if not isinstance(record.get("created_at"), str) or not _valid_created_at(
        record["created_at"]
    ):
        raise ValueError("baseline created_at is invalid")
    if record.get("release_artifact") is not False:
        raise ValueError("baseline release_artifact must be false")
    if record.get("performed_actions") != ["local_write"]:
        raise ValueError("baseline performed_actions are invalid")
    validate_aggregate_record(
        {
            "schema_version": record["schema_version"],
            "status": "PASS",
            "reason_codes": [],
            "suite_id": record["suite_id"],
            "suite_manifest_hash": record["suite_manifest_hash"],
            "configuration_id": record["configuration_id"],
            "comparability": "FULL",
            "source_basis": record["source_basis"],
            "task_count": record["task_count"],
            "run_count": record["run_count"],
            "metrics": record["metrics"],
            "run_evidence_manifest": record["run_evidence_manifest"],
            "run_manifest_hash": record["run_manifest_hash"],
            "performed_actions": [],
        },
        suite=suite,
    )
    expected_id = "agent-quality-" + sha256_json(
        {
            "configuration_id": record["configuration_id"],
            "created_at": record["created_at"],
            "run_manifest_hash": record["run_manifest_hash"],
            "suite_id": record["suite_id"],
            "suite_manifest_hash": record["suite_manifest_hash"],
        }
    )[:24]
    if record.get("baseline_id") != expected_id:
        raise ValueError("baseline_id does not match baseline content")
    return dict(record)


def build_baseline(
    aggregate: Mapping[str, Any],
    *,
    suite: Mapping[str, Any],
    approval_ref: str,
    created_at: str,
    evidence_refs: Sequence[str] = (),
) -> dict[str, Any]:
    """Build a schema-shaped baseline record without writing it to disk."""

    if not isinstance(aggregate, Mapping) or not _baseline_ready(aggregate, suite):
        raise ValueError("aggregate is not eligible for baseline adoption")
    if not isinstance(approval_ref, str) or not _SAFE_IDENTIFIER.fullmatch(
        approval_ref
    ):
        raise ValueError("approval_ref is not a safe identifier")
    if not isinstance(created_at, str) or not _valid_created_at(created_at):
        raise ValueError("created_at must be a timezone-aware ISO timestamp")
    if (
        not isinstance(evidence_refs, Sequence)
        or isinstance(evidence_refs, (str, bytes, bytearray))
        or len(evidence_refs) > 20
    ):
        raise ValueError("evidence_refs must be a bounded sequence")
    safe_refs: list[str] = []
    for ref in evidence_refs:
        if (
            not isinstance(ref, str)
            or not safe_repo_path(ref)
        ):
            raise ValueError("evidence_refs must be safe repo-relative paths")
        safe_refs.append(ref)

    normalized_source = _validate_source_basis(aggregate["source_basis"])
    baseline_id = "agent-quality-" + sha256_json(
        {
            "configuration_id": aggregate["configuration_id"],
            "created_at": created_at,
            "run_manifest_hash": aggregate["run_manifest_hash"],
            "suite_id": aggregate["suite_id"],
            "suite_manifest_hash": aggregate["suite_manifest_hash"],
        }
    )[:24]
    baseline = {
        "schema_version": "1",
        "baseline_id": baseline_id,
        "status": "PASS WITH NOTES",
        "decision": "PROVISIONAL_BASELINE_ACCEPTED",
        "suite_id": aggregate["suite_id"],
        "suite_manifest_hash": aggregate["suite_manifest_hash"],
        "configuration_id": aggregate["configuration_id"],
        "source_basis": normalized_source,
        "task_count": aggregate["task_count"],
        "run_count": aggregate["run_count"],
        "metrics": dict(_metrics(aggregate)),
        "run_evidence_manifest": [
            dict(entry) for entry in aggregate["run_evidence_manifest"]
        ],
        "run_manifest_hash": aggregate["run_manifest_hash"],
        "evidence_refs": safe_refs,
        "approval_ref": approval_ref,
        "created_at": created_at,
        "release_artifact": False,
        "performed_actions": ["local_write"],
    }
    return validate_baseline_record(baseline, suite=suite)


def _has_operational_measurements(candidate: Mapping[str, Any]) -> bool:
    if any(field in candidate for field in ("duration_seconds", "cost_units")):
        return True
    operational = candidate.get("operational_metrics")
    return isinstance(operational, Mapping) and any(
        field in operational for field in ("duration_seconds", "cost_units")
    )


def compare_baseline(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    suite: Mapping[str, Any],
) -> dict[str, Any]:
    """Compare quality only; supplied duration or cost requires owner review."""

    if not isinstance(baseline, Mapping) or not isinstance(candidate, Mapping):
        raise ValueError("baseline and candidate must be objects")
    baseline = validate_baseline_record(baseline, suite=suite)
    candidate = validate_aggregate_record(
        candidate, suite=suite, allow_operational=True
    )
    baseline_metrics = _metrics(baseline)
    candidate_metrics = _metrics(candidate)

    suite_manifest_mismatch = baseline["suite_manifest_hash"] != candidate[
        "suite_manifest_hash"
    ]
    structural_mismatches = [
        f"{field.upper()}_MISMATCH"
        for field in ("suite_id", "task_count", "run_count")
        if baseline.get(field) != candidate.get(field)
    ]
    comparability_reasons = []
    if suite_manifest_mismatch:
        comparability_reasons.append("SUITE_MANIFEST_MISMATCH")
    comparability_reasons.extend(structural_mismatches)
    if candidate["comparability"] != "FULL":
        comparability_reasons.append("CONFIGURATION_COMPARABILITY_NOT_FULL")

    owner_decision_required = _has_operational_measurements(candidate)
    if owner_decision_required:
        comparability_reasons.append("OWNER_DECISION_REQUIRED")
    if comparability_reasons:
        return {
            "schema_version": "1",
            "status": "HOLD",
            "decision": "HOLD",
            "reason_codes": comparability_reasons,
            "baseline_configuration_id": baseline.get("configuration_id"),
            "candidate_configuration_id": candidate.get("configuration_id"),
            "regression_metric_ids": [],
            "owner_decision_required": owner_decision_required,
            "performed_actions": [],
        }

    reasons: list[str] = []
    regressions: list[str] = []

    for field in _BLOCKER_FIELDS:
        if candidate_metrics[field] != 0:
            reasons.append(f"{field.upper()}_PRESENT")
            regressions.append(field)

    for field in _RATE_FIELDS:
        if candidate_metrics[field] < baseline_metrics[field]:
            reasons.append(f"{field.upper()}_REGRESSED")
            regressions.append(field)

    for field in _REGRESSION_MAX_FIELDS:
        if candidate_metrics[field] > baseline_metrics[field]:
            reasons.append(f"{field.upper()}_REGRESSED")
            regressions.append(field)

    if (
        candidate_metrics["holdout_passed_count"]
        < baseline_metrics["holdout_passed_count"]
    ):
        reasons.append("HOLDOUT_PASSED_COUNT_REGRESSED")
        regressions.append("holdout_passed_count")

    if regressions:
        decision = "REJECT"
        status = "REJECT"
    else:
        decision = "ADOPT"
        status = "PASS"

    return {
        "schema_version": "1",
        "status": status,
        "decision": decision,
        "reason_codes": reasons,
        "baseline_configuration_id": baseline.get("configuration_id"),
        "candidate_configuration_id": candidate.get("configuration_id"),
        "regression_metric_ids": sorted(set(regressions)),
        "owner_decision_required": owner_decision_required,
        "performed_actions": [],
    }
