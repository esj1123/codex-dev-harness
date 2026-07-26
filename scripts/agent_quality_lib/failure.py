"""Validate safe failure cases and the failure-to-eval lifecycle."""

from __future__ import annotations

from datetime import date
import re
from typing import Any

from scripts.agent_quality_lib.contracts import safe_repo_path

SCHEMA_VERSION = "1"
VALIDATOR_ID = "agent_quality_failure"
LIFECYCLE = (
    "OBSERVED",
    "QUARANTINED",
    "SANITIZED",
    "REPRODUCED",
    "HUMAN_REVIEWED",
    "GRADER_VALIDATED",
    "REGRESSION",
    "DEPRECATED",
)
FAILURE_KEYS = {
    "schema_version",
    "failure_id",
    "task_class",
    "state",
    "safe_symptom_summary",
    "minimal_synthetic_fixture_ref",
    "minimal_synthetic_fixture_hash",
    "expected_invariant_id",
    "grader_id",
    "first_observed_date",
    "last_reproduced_date",
    "affected_configuration_hashes",
    "review_refs",
}
IDENTITY_FIELDS = (
    "schema_version",
    "failure_id",
    "task_class",
    "minimal_synthetic_fixture_ref",
    "minimal_synthetic_fixture_hash",
    "expected_invariant_id",
    "grader_id",
    "first_observed_date",
    "affected_configuration_hashes",
)
SAFE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
WINDOWS_ABSOLUTE_PATTERN = re.compile(r"(?:^|[\s\"'])[A-Za-z]:[\\/]")
POSIX_ABSOLUTE_PATTERN = re.compile(r"(?:^|[\s\"'])/[A-Za-z0-9_.-]+(?:/|$)")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SECRET_VALUE_PATTERN = re.compile(
    r"(?i)\b(?:api[_ -]?key|credential|password|secret|token)\b\s*[:=]\s*\S+"
)
RAW_VALUE_PATTERN = re.compile(
    r"(?i)\b(?:command_log|private_data|prompt_text|raw_input|raw_output|"
    r"raw_payload|transcript)\b\s*[:=]"
)


def _safe_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and 1 <= len(value) <= 160
        and len(value.encode("utf-8")) <= 160
        and SAFE_IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _safe_repo_ref(value: Any, *, fixture: bool = False) -> bool:
    if not safe_repo_path(value):
        return False
    return not fixture or value.startswith("evals/agentic/fixtures/")


def _valid_date(value: Any, *, nullable: bool = False) -> bool:
    if value is None:
        return nullable
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _safe_summary(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 500:
        return False
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        return False
    if "\\" in value or "://" in value:
        return False
    return not any(
        pattern.search(value)
        for pattern in (
            WINDOWS_ABSOLUTE_PATTERN,
            POSIX_ABSOLUTE_PATTERN,
            IP_PATTERN,
            SECRET_VALUE_PATTERN,
            RAW_VALUE_PATTERN,
        )
    )


def failure_case_issues(payload: Any) -> list[str]:
    """Return deterministic validation issues for one failure case."""

    if not isinstance(payload, dict):
        return ["FAILURE_CASE_NOT_OBJECT"]
    if set(payload) != FAILURE_KEYS:
        return ["FAILURE_CASE_KEY_SET_INVALID"]

    issues: set[str] = set()
    if payload["schema_version"] != SCHEMA_VERSION:
        issues.add("SCHEMA_VERSION_INVALID")
    for field in ("failure_id", "task_class", "expected_invariant_id", "grader_id"):
        if not _safe_identifier(payload[field]):
            issues.add(f"{field.upper()}_INVALID")
    if payload["state"] not in LIFECYCLE:
        issues.add("STATE_INVALID")
    if not _safe_summary(payload["safe_symptom_summary"]):
        issues.add("SAFE_SYMPTOM_SUMMARY_INVALID")
    if not _safe_repo_ref(payload["minimal_synthetic_fixture_ref"], fixture=True):
        issues.add("MINIMAL_SYNTHETIC_FIXTURE_REF_INVALID")
    if (
        not isinstance(payload["minimal_synthetic_fixture_hash"], str)
        or HASH_PATTERN.fullmatch(payload["minimal_synthetic_fixture_hash"]) is None
    ):
        issues.add("MINIMAL_SYNTHETIC_FIXTURE_HASH_INVALID")
    if not _valid_date(payload["first_observed_date"]):
        issues.add("FIRST_OBSERVED_DATE_INVALID")
    if not _valid_date(payload["last_reproduced_date"], nullable=True):
        issues.add("LAST_REPRODUCED_DATE_INVALID")
    if (
        _valid_date(payload["first_observed_date"])
        and _valid_date(payload["last_reproduced_date"], nullable=True)
        and payload["last_reproduced_date"] is not None
        and payload["last_reproduced_date"] < payload["first_observed_date"]
    ):
        issues.add("REPRODUCTION_DATE_ORDER_INVALID")

    hashes = payload["affected_configuration_hashes"]
    if (
        not isinstance(hashes, list)
        or not hashes
        or len(hashes) > 10
        or len(hashes) != len(set(item for item in hashes if isinstance(item, str)))
        or any(
            not isinstance(item, str) or HASH_PATTERN.fullmatch(item) is None
            for item in hashes
        )
    ):
        issues.add("AFFECTED_CONFIGURATION_HASHES_INVALID")

    refs = payload["review_refs"]
    if (
        not isinstance(refs, list)
        or len(refs) > 10
        or any(not _safe_repo_ref(item) for item in refs)
        or len(refs) != len(set(item for item in refs if isinstance(item, str)))
    ):
        issues.add("REVIEW_REFS_INVALID")

    if payload["state"] in LIFECYCLE:
        state_index = LIFECYCLE.index(payload["state"])
        review_count = len(refs) if isinstance(refs, list) else 0
        reproduced_index = LIFECYCLE.index("REPRODUCED")
        human_reviewed_index = LIFECYCLE.index("HUMAN_REVIEWED")
        grader_validated_index = LIFECYCLE.index("GRADER_VALIDATED")
        if state_index < reproduced_index and payload["last_reproduced_date"] is not None:
            issues.add("FUTURE_REPRODUCTION_EVIDENCE_FORBIDDEN")
        if state_index >= reproduced_index and payload["last_reproduced_date"] is None:
            issues.add("REPRODUCED_STATE_EVIDENCE_MISSING")
        if state_index < human_reviewed_index and review_count:
            issues.add("FUTURE_REVIEW_EVIDENCE_FORBIDDEN")
        if state_index == human_reviewed_index and review_count != 1:
            issues.add("HUMAN_REVIEW_EVIDENCE_MISSING")
        if state_index >= grader_validated_index and review_count < 2:
            issues.add("GRADER_VALIDATION_EVIDENCE_MISSING")
    return sorted(issues)


def validate_failure_case(payload: Any) -> dict[str, Any]:
    """Validate a failure case without persisting or echoing its values."""

    issues = failure_case_issues(payload)
    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "status": "PASS" if not issues else "FAIL",
        "reason_codes": issues,
        "validation_summary": {
            "issue_count": len(issues),
            "state": payload.get("state") if isinstance(payload, dict) and payload.get("state") in LIFECYCLE else None,
        },
        "performed_actions": [],
    }


def validate_transition(current_state: Any, next_state: Any) -> dict[str, Any]:
    """Validate one adjacent lifecycle transition without changing a case."""

    if current_state not in LIFECYCLE or next_state not in LIFECYCLE:
        status = "FAIL"
        reasons = ["STATE_INVALID"]
    else:
        current_index = LIFECYCLE.index(current_state)
        expected = (
            LIFECYCLE[current_index + 1]
            if current_index + 1 < len(LIFECYCLE)
            else None
        )
        status = "PASS" if next_state == expected else "BLOCKED"
        reasons = [] if status == "PASS" else ["LIFECYCLE_TRANSITION_INVALID"]
    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "status": status,
        "reason_codes": reasons,
        "transition_summary": {
            "current_state": current_state if current_state in LIFECYCLE else None,
            "next_state": next_state if next_state in LIFECYCLE else None,
        },
        "performed_actions": [],
    }


def validate_failure_transition(payload: Any, next_payload: Any) -> dict[str, Any]:
    """Validate two complete cases and one evidence-preserving transition."""

    current_issues = failure_case_issues(payload)
    next_issues = failure_case_issues(next_payload)
    if current_issues or next_issues:
        reasons = []
        if current_issues:
            reasons.append("CURRENT_FAILURE_CASE_INVALID")
        if next_issues:
            reasons.append("NEXT_FAILURE_CASE_INVALID")
        return {
            "schema_version": SCHEMA_VERSION,
            "validator_id": VALIDATOR_ID,
            "status": "FAIL",
            "reason_codes": reasons,
            "transition_summary": {
                "current_state": payload.get("state") if isinstance(payload, dict) else None,
                "next_state": next_payload.get("state") if isinstance(next_payload, dict) else None,
            },
            "performed_actions": [],
        }

    transition = validate_transition(payload["state"], next_payload["state"])
    if transition["status"] != "PASS":
        return transition

    reasons: list[str] = []
    if any(payload[field] != next_payload[field] for field in IDENTITY_FIELDS):
        reasons.append("FAILURE_IDENTITY_CHANGED")
    current_date = payload["last_reproduced_date"]
    next_date = next_payload["last_reproduced_date"]
    if current_date is not None and next_date is not None and next_date < current_date:
        reasons.append("REPRODUCTION_EVIDENCE_NOT_MONOTONIC")
    current_refs = payload["review_refs"]
    next_refs = next_payload["review_refs"]
    if next_refs[: len(current_refs)] != current_refs:
        reasons.append("REVIEW_EVIDENCE_NOT_MONOTONIC")
    if reasons:
        return {
            **transition,
            "status": "BLOCKED",
            "reason_codes": reasons,
        }
    return transition
