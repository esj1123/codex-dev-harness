from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
import re
from typing import Any

from scripts.agent_quality_lib.contracts import sha256_json


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


def _metrics(record: Mapping[str, Any]) -> Mapping[str, int | float]:
    metrics = record.get("metrics")
    if not isinstance(metrics, Mapping):
        raise ValueError("record metrics must be an object")
    missing = [field for field in _METRIC_FIELDS if field not in metrics]
    if missing:
        raise ValueError(f"record metrics missing fields: {','.join(missing)}")
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


def _baseline_ready(aggregate: Mapping[str, Any]) -> bool:
    metrics = _metrics(aggregate)
    return (
        aggregate.get("status") == "PASS"
        and aggregate.get("comparability") == "FULL"
        and all(metrics[field] == 1.0 for field in _RATE_FIELDS)
        and all(metrics[field] == 0 for field in _BLOCKER_FIELDS)
        and metrics["postflight_block_count"] == 0
        and metrics["holdout_passed_count"] > 0
        and metrics["holdout_failed_count"] == 0
    )


def build_baseline(
    aggregate: Mapping[str, Any],
    *,
    source_basis: Mapping[str, Any],
    approval_ref: str,
    created_at: str,
    evidence_refs: Sequence[str] = (),
) -> dict[str, Any]:
    """Build a schema-shaped baseline record without writing it to disk."""

    if not isinstance(aggregate, Mapping) or not _baseline_ready(aggregate):
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
            or len(ref) > 260
            or not re.fullmatch(r"[A-Za-z0-9._/-]+", ref)
            or ref.startswith("/")
            or ".." in ref.split("/")
        ):
            raise ValueError("evidence_refs must be safe repo-relative paths")
        safe_refs.append(ref)

    normalized_source = _validate_source_basis(source_basis)
    baseline_id = "agent-quality-" + sha256_json(
        {
            "configuration_id": aggregate["configuration_id"],
            "created_at": created_at,
            "run_manifest_hash": aggregate["run_manifest_hash"],
            "suite_id": aggregate["suite_id"],
        }
    )[:24]
    return {
        "schema_version": "1",
        "baseline_id": baseline_id,
        "status": "PASS WITH NOTES",
        "decision": "PROVISIONAL_BASELINE_ACCEPTED",
        "suite_id": aggregate["suite_id"],
        "configuration_id": aggregate["configuration_id"],
        "source_basis": normalized_source,
        "task_count": aggregate["task_count"],
        "run_count": aggregate["run_count"],
        "metrics": dict(_metrics(aggregate)),
        "run_manifest_hash": aggregate["run_manifest_hash"],
        "evidence_refs": safe_refs,
        "approval_ref": approval_ref,
        "created_at": created_at,
        "release_artifact": False,
        "performed_actions": ["local_write"],
    }


def _has_operational_measurements(candidate: Mapping[str, Any]) -> bool:
    if any(field in candidate for field in ("duration_seconds", "cost_units")):
        return True
    operational = candidate.get("operational_metrics")
    return isinstance(operational, Mapping) and any(
        field in operational for field in ("duration_seconds", "cost_units")
    )


def compare_baseline(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any]
) -> dict[str, Any]:
    """Compare quality only; supplied duration or cost requires owner review."""

    if not isinstance(baseline, Mapping) or not isinstance(candidate, Mapping):
        raise ValueError("baseline and candidate must be objects")
    baseline_metrics = _metrics(baseline)
    candidate_metrics = _metrics(candidate)

    reasons: list[str] = []
    regressions: list[str] = []
    reject = False

    for field in ("suite_id", "task_count", "run_count"):
        if baseline.get(field) != candidate.get(field):
            reasons.append(f"{field.upper()}_MISMATCH")
            reject = True

    if candidate.get("comparability", "FULL") != "FULL":
        reasons.append("CONFIGURATION_COMPARABILITY_NOT_FULL")

    for field in _BLOCKER_FIELDS:
        if candidate_metrics[field] != 0:
            reasons.append(f"{field.upper()}_PRESENT")
            regressions.append(field)
            reject = True

    for field in _RATE_FIELDS:
        if candidate_metrics[field] < baseline_metrics[field]:
            reasons.append(f"{field.upper()}_REGRESSED")
            regressions.append(field)
            reject = True

    for field in _REGRESSION_MAX_FIELDS:
        if candidate_metrics[field] > baseline_metrics[field]:
            reasons.append(f"{field.upper()}_REGRESSED")
            regressions.append(field)
            reject = True

    if (
        candidate_metrics["holdout_passed_count"]
        < baseline_metrics["holdout_passed_count"]
    ):
        reasons.append("HOLDOUT_PASSED_COUNT_REGRESSED")
        regressions.append("holdout_passed_count")
        reject = True

    owner_decision_required = _has_operational_measurements(candidate)
    if owner_decision_required:
        reasons.append("OWNER_DECISION_REQUIRED")

    if reject:
        decision = "REJECT"
        status = "REJECT"
    elif "CONFIGURATION_COMPARABILITY_NOT_FULL" in reasons:
        decision = "HOLD"
        status = "HOLD"
    elif owner_decision_required:
        decision = "HOLD"
        status = "HOLD"
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
