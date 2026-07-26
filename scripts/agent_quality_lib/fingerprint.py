"""Deterministic agent-quality fingerprint normalization."""

from __future__ import annotations

from typing import Any

from .contracts import (
    AgentQualityValidationError,
    FINGERPRINT_BASE_KEYS,
    UNKNOWN_ALLOWED_FIELDS,
    fingerprint_base_issues,
    sha256_json,
)


CONFIGURATION_FIELDS = (
    "agent_adapter_id",
    "agent_adapter_version",
    "model_id",
    "reasoning_profile",
    "task_contract_hash",
    "tool_policy_hash",
    "skill_set_hash",
    "dependency_lock_hash",
    "environment_profile_id",
    "verification_suite_id",
    "grader_version",
)


def normalize_fingerprint(fingerprint: Any) -> dict[str, Any]:
    """Derive comparison metadata and stable IDs without mutating the input."""

    issues = fingerprint_base_issues(fingerprint, allow_derived_omission=True)
    if issues:
        raise AgentQualityValidationError(issues)

    base = {key: fingerprint[key] for key in sorted(FINGERPRINT_BASE_KEYS)}
    unknown_fields = sorted(
        key for key in UNKNOWN_ALLOWED_FIELDS if base[key] == "UNKNOWN"
    )
    configuration = {key: base[key] for key in CONFIGURATION_FIELDS}
    normalized = {
        **base,
        "comparability": "PARTIAL" if unknown_fields else "FULL",
        "configuration_id": sha256_json(configuration),
        "unknown_fields": unknown_fields,
    }
    normalized["run_fingerprint_id"] = sha256_json(normalized)
    return normalized
