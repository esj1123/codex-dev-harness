"""Validate safe failure cases and the failure-to-eval lifecycle."""

from __future__ import annotations

from datetime import date
from pathlib import PurePosixPath
import re
from typing import Any


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
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > 260:
        return False
    if not value.isascii() or "\\" in value or "://" in value or value.startswith("/"):
        return False
    if re.match(r"^[A-Za-z]:", value):
        return False
    candidate = PurePosixPath(value)
    if (
        candidate.is_absolute()
        or candidate.as_posix() != value
        or any(part in ("", ".", "..") for part in candidate.parts)
        or value.endswith("/")
    ):
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
        if (
            state_index >= LIFECYCLE.index("REPRODUCED")
            and payload["last_reproduced_date"] is None
        ):
            issues.add("REPRODUCED_STATE_EVIDENCE_MISSING")
        if state_index >= LIFECYCLE.index("HUMAN_REVIEWED") and review_count < 1:
            issues.add("HUMAN_REVIEW_EVIDENCE_MISSING")
        if state_index >= LIFECYCLE.index("GRADER_VALIDATED") and review_count < 2:
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


def validate_failure_transition(payload: Any, next_state: Any) -> dict[str, Any]:
    """Validate a case and then its proposed transition without mutation."""

    validation = validate_failure_case(payload)
    if validation["status"] != "PASS":
        return validation
    return validate_transition(payload["state"], next_state)
