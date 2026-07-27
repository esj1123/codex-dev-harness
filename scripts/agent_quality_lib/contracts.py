"""Manual validation for bounded agent-quality trial envelopes."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

from scripts.repo_path_policy import safe_repo_path as shared_safe_repo_path


MAX_JSON_BYTES = 64 * 1024
MAX_IDENTIFIER_BYTES = 160
MAX_EVIDENCE_REF_BYTES = 260
MAX_LIST_ITEMS = 20

RUN_KEYS = {
    "schema_version",
    "run_id",
    "task_id",
    "trial_id",
    "suite_id",
    "task_class",
    "criticality",
    "fingerprint",
    "execution",
    "grading",
    "metrics",
    "evidence_refs",
    "performed_actions",
}
FINGERPRINT_BASE_KEYS = {
    "harness_commit",
    "target_base_commit",
    "contract_basis_sha",
    "work_package_plan_digest",
    "agent_adapter_id",
    "agent_adapter_version",
    "model_id",
    "reasoning_profile",
    "task_contract_hash",
    "tool_policy_hash",
    "skill_set_hash",
    "approved_corpus_digest",
    "dependency_lock_hash",
    "environment_profile_id",
    "verification_suite_id",
    "grader_version",
}
FINGERPRINT_DERIVED_KEYS = {
    "configuration_id",
    "run_fingerprint_id",
    "comparability",
    "unknown_fields",
}
FINGERPRINT_KEYS = FINGERPRINT_BASE_KEYS | FINGERPRINT_DERIVED_KEYS
EXECUTION_KEYS = {"status", "reason_codes"}
BOUND_EXECUTION_KEYS = EXECUTION_KEYS | {
    "verification_contract_hash",
    "interpreter_id",
    "required_command_ids",
    "completed_command_ids",
}
GRADING_KEYS = {
    "functional_correctness",
    "contract_adherence",
    "scope_adherence",
    "semantic_consistency",
    "architectural_consistency",
    "safety_compliance",
    "reproducibility",
    "blocker_count",
}
BOUND_GRADING_KEYS = GRADING_KEYS | {"invariant_results"}
INVARIANT_RESULT_KEYS = {
    "invariant_id",
    "grader_id",
    "status",
    "result_hash",
}
METRIC_KEYS = {
    "critical_failure_count",
    "scope_violation_count",
    "safety_violation_count",
    "postflight_block_count",
    "contract_reopen_count",
    "semantic_blocker_count",
    "integration_fix_file_count",
    "integration_fix_line_count",
    "holdout_passed_count",
    "holdout_failed_count",
}

STATUSES = {"PASS", "FAIL", "BLOCKED", "NOT RUN", "ENVIRONMENT BLOCKED"}
CRITICALITIES = {"normal", "critical"}
REASONING_PROFILES = {"low", "medium", "high", "xhigh", "max", "ultra", "UNKNOWN"}
PERFORMED_ACTIONS = {"local_write", "execute", "stage", "commit", "review"}
UNKNOWN_ALLOWED_FIELDS = {
    "agent_adapter_version",
    "model_id",
    "reasoning_profile",
    "approved_corpus_digest",
    "dependency_lock_hash",
}

SAFE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
REASON_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
GIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40,64}$")
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
WINDOWS_DRIVE_PATTERN = re.compile(r"^[A-Za-z]:")
FORBIDDEN_TEXT_PATTERN = re.compile(
    r"(?:^|[^a-z0-9])"
    r"(?:raw|prompt|transcript|stdout|stderr|secret|secrets|token|tokens|"
    r"password|passwd|credential|credentials|api[_-]?key|command[_-]?log)"
    r"(?:$|[^a-z0-9])",
    re.IGNORECASE,
)


class AgentQualityValidationError(ValueError):
    """Raised when a public helper cannot return a valid safe value."""

    def __init__(self, issues: Iterable[str]):
        self.issues = tuple(sorted(set(issues)))
        super().__init__(", ".join(self.issues))


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic compact ASCII JSON bytes."""

    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    """Hash the canonical JSON representation of a value."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AgentQualityValidationError(("JSON_DUPLICATE_KEY",))
        result[key] = value
    return result


def _reject_non_json_constant(value: str) -> None:
    raise AgentQualityValidationError(("JSON_INPUT_MALFORMED",))


def load_json_file(path: str | Path) -> Any:
    """Load one regular UTF-8 JSON file no larger than 64 KiB."""

    source = Path(path)
    try:
        if source.is_symlink() or not source.is_file():
            raise AgentQualityValidationError(("JSON_INPUT_NOT_REGULAR_FILE",))
        if source.stat().st_size > MAX_JSON_BYTES:
            raise AgentQualityValidationError(("JSON_INPUT_TOO_LARGE",))
        raw = source.read_bytes()
    except AgentQualityValidationError:
        raise
    except OSError as exc:
        raise AgentQualityValidationError(("JSON_INPUT_UNAVAILABLE",)) from exc

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AgentQualityValidationError(("JSON_INPUT_UTF8_INVALID",)) from exc
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_json_constant,
        )
    except AgentQualityValidationError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        raise AgentQualityValidationError(("JSON_INPUT_MALFORMED",)) from exc


def _safe_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value.encode("utf-8")) <= MAX_IDENTIFIER_BYTES
        and SAFE_IDENTIFIER_PATTERN.fullmatch(value) is not None
        and not _unsafe_text(value)
    )


def _safe_reason_code(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value.encode("utf-8")) <= 80
        and REASON_CODE_PATTERN.fullmatch(value) is not None
        and not _unsafe_text(value)
    )


def _unsafe_text(value: str) -> bool:
    return (
        "\\" in value
        or "://" in value
        or WINDOWS_DRIVE_PATTERN.match(value) is not None
        or "\x00" in value
        or "\r" in value
        or "\n" in value
        or FORBIDDEN_TEXT_PATTERN.search(value) is not None
    )


def safe_repo_path(value: Any) -> bool:
    """Return whether a value is a Windows-safe repository-relative path."""

    return (
        isinstance(value, str)
        and not _unsafe_text(value)
        and shared_safe_repo_path(value, max_bytes=MAX_EVIDENCE_REF_BYTES)
    )


def _exact_keys(value: Any, expected: set[str], issue: str, issues: list[str]) -> bool:
    if not isinstance(value, dict) or set(value) != expected:
        issues.append(issue)
        return False
    return True


def _safe_unique_list(
    value: Any,
    *,
    limit: int,
    validator: Any,
) -> bool:
    if not isinstance(value, list) or len(value) > limit:
        return False
    if not all(isinstance(item, str) for item in value):
        return False
    return len(value) == len(set(value)) and all(validator(item) for item in value)


def _non_negative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def fingerprint_base_issues(fingerprint: Any, *, allow_derived_omission: bool) -> list[str]:
    """Validate fingerprint source fields used by the normalizer."""

    if not isinstance(fingerprint, dict):
        return ["FINGERPRINT_NOT_OBJECT"]
    accepted = (
        {frozenset(FINGERPRINT_BASE_KEYS), frozenset(FINGERPRINT_KEYS)}
        if allow_derived_omission
        else {frozenset(FINGERPRINT_KEYS)}
    )
    if frozenset(fingerprint) not in accepted:
        return ["FINGERPRINT_KEY_SET_INVALID"]

    issues: list[str] = []
    for key in ("harness_commit", "target_base_commit", "contract_basis_sha"):
        value = fingerprint[key]
        if not isinstance(value, str) or GIT_SHA_PATTERN.fullmatch(value) is None:
            issues.append(f"{key.upper()}_INVALID")
    for key in (
        "work_package_plan_digest",
        "task_contract_hash",
        "tool_policy_hash",
        "skill_set_hash",
    ):
        value = fingerprint[key]
        if not isinstance(value, str) or HASH_PATTERN.fullmatch(value) is None:
            issues.append(f"{key.upper()}_INVALID")
    for key in ("approved_corpus_digest", "dependency_lock_hash"):
        value = fingerprint[key]
        if value != "UNKNOWN" and (
            not isinstance(value, str) or HASH_PATTERN.fullmatch(value) is None
        ):
            issues.append(f"{key.upper()}_INVALID")
    for key in (
        "agent_adapter_id",
        "environment_profile_id",
        "verification_suite_id",
        "grader_version",
    ):
        if not _safe_identifier(fingerprint[key]):
            issues.append(f"{key.upper()}_INVALID")
    for key in ("agent_adapter_version", "model_id"):
        if fingerprint[key] != "UNKNOWN" and not _safe_identifier(fingerprint[key]):
            issues.append(f"{key.upper()}_INVALID")
    if fingerprint["reasoning_profile"] not in REASONING_PROFILES:
        issues.append("REASONING_PROFILE_INVALID")
    return sorted(set(issues))


def _validate_fingerprint(fingerprint: Any, issues: list[str]) -> None:
    base_issues = fingerprint_base_issues(fingerprint, allow_derived_omission=False)
    issues.extend(base_issues)
    if base_issues:
        return

    from .fingerprint import normalize_fingerprint

    derived_validity = {
        "configuration_id": (
            isinstance(fingerprint["configuration_id"], str)
            and HASH_PATTERN.fullmatch(fingerprint["configuration_id"]) is not None
        ),
        "run_fingerprint_id": (
            isinstance(fingerprint["run_fingerprint_id"], str)
            and HASH_PATTERN.fullmatch(fingerprint["run_fingerprint_id"]) is not None
        ),
        "comparability": fingerprint["comparability"] in {"FULL", "PARTIAL"},
        "unknown_fields": _safe_unique_list(
            fingerprint["unknown_fields"],
            limit=MAX_LIST_ITEMS,
            validator=lambda item: item in FINGERPRINT_BASE_KEYS,
        ),
    }
    for key, valid in derived_validity.items():
        if not valid:
            issues.append(f"{key.upper()}_INVALID")

    try:
        expected = normalize_fingerprint(fingerprint)
    except AgentQualityValidationError as exc:
        issues.extend(exc.issues)
        return
    for key in FINGERPRINT_DERIVED_KEYS:
        if derived_validity[key] and fingerprint[key] != expected[key]:
            issues.append(f"{key.upper()}_MISMATCH")


def _validate_execution(value: Any, issues: list[str]) -> None:
    if not isinstance(value, dict) or set(value) not in {
        frozenset(EXECUTION_KEYS),
        frozenset(BOUND_EXECUTION_KEYS),
    }:
        issues.append("EXECUTION_KEY_SET_INVALID")
        return
    if value["status"] not in STATUSES:
        issues.append("EXECUTION_STATUS_INVALID")
    if not _safe_unique_list(
        value["reason_codes"], limit=MAX_LIST_ITEMS, validator=_safe_reason_code
    ):
        issues.append("EXECUTION_REASON_CODES_INVALID")
    if set(value) == BOUND_EXECUTION_KEYS:
        if (
            not isinstance(value["verification_contract_hash"], str)
            or HASH_PATTERN.fullmatch(value["verification_contract_hash"]) is None
        ):
            issues.append("VERIFICATION_CONTRACT_HASH_INVALID")
        if not _safe_identifier(value["interpreter_id"]):
            issues.append("VERIFICATION_INTERPRETER_ID_INVALID")
        for key in ("required_command_ids", "completed_command_ids"):
            if not _safe_unique_list(
                value[key],
                limit=MAX_LIST_ITEMS,
                validator=_safe_identifier,
            ):
                issues.append(f"{key.upper()}_INVALID")
        if (
            value["status"] == "PASS"
            and set(value["required_command_ids"])
            != set(value["completed_command_ids"])
        ):
            issues.append("VERIFICATION_COMMANDS_INCOMPLETE")


def _validate_grading(value: Any, issues: list[str]) -> None:
    if not isinstance(value, dict) or set(value) not in {
        frozenset(GRADING_KEYS),
        frozenset(BOUND_GRADING_KEYS),
    }:
        issues.append("GRADING_KEY_SET_INVALID")
        return
    for key in GRADING_KEYS - {"blocker_count"}:
        if value[key] not in STATUSES:
            issues.append(f"GRADING_{key.upper()}_INVALID")
    if not _non_negative_integer(value["blocker_count"]):
        issues.append("GRADING_BLOCKER_COUNT_INVALID")
    if set(value) == BOUND_GRADING_KEYS:
        results = value["invariant_results"]
        if not isinstance(results, list) or not results or len(results) > MAX_LIST_ITEMS:
            issues.append("INVARIANT_RESULTS_INVALID")
            return
        invariant_ids: list[str] = []
        for result in results:
            if not isinstance(result, dict) or set(result) != INVARIANT_RESULT_KEYS:
                issues.append("INVARIANT_RESULT_KEY_SET_INVALID")
                continue
            if not _safe_identifier(result["invariant_id"]):
                issues.append("INVARIANT_ID_INVALID")
            else:
                invariant_ids.append(result["invariant_id"])
            if not _safe_identifier(result["grader_id"]):
                issues.append("INVARIANT_GRADER_ID_INVALID")
            if result["status"] not in {"PASS", "FAIL", "NOT RUN"}:
                issues.append("INVARIANT_STATUS_INVALID")
            if (
                not isinstance(result["result_hash"], str)
                or HASH_PATTERN.fullmatch(result["result_hash"]) is None
            ):
                issues.append("INVARIANT_RESULT_HASH_INVALID")
        if len(invariant_ids) != len(set(invariant_ids)):
            issues.append("INVARIANT_ID_DUPLICATE")
        if invariant_ids != sorted(invariant_ids):
            issues.append("INVARIANT_RESULT_ORDER_INVALID")


def _validate_metrics(value: Any, issues: list[str]) -> None:
    if not _exact_keys(value, METRIC_KEYS, "METRICS_KEY_SET_INVALID", issues):
        return
    for key in METRIC_KEYS:
        if not _non_negative_integer(value[key]):
            issues.append(f"METRICS_{key.upper()}_INVALID")


def _run_issues(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["RUN_NOT_OBJECT"]
    if set(payload) != RUN_KEYS:
        return ["RUN_KEY_SET_INVALID"]

    issues: list[str] = []
    if payload["schema_version"] != "1":
        issues.append("SCHEMA_VERSION_INVALID")
    for key in ("run_id", "task_id", "trial_id", "suite_id", "task_class"):
        if not _safe_identifier(payload[key]):
            issues.append(f"{key.upper()}_INVALID")
    if payload["criticality"] not in CRITICALITIES:
        issues.append("CRITICALITY_INVALID")

    _validate_fingerprint(payload["fingerprint"], issues)
    _validate_execution(payload["execution"], issues)
    _validate_grading(payload["grading"], issues)
    _validate_metrics(payload["metrics"], issues)

    if not _safe_unique_list(
        payload["evidence_refs"], limit=MAX_LIST_ITEMS, validator=safe_repo_path
    ):
        issues.append("EVIDENCE_REFS_INVALID")
    if not _safe_unique_list(
        payload["performed_actions"], limit=5, validator=PERFORMED_ACTIONS.__contains__
    ):
        issues.append("PERFORMED_ACTIONS_INVALID")
    return sorted(set(issues))


def validate_run(payload: Any) -> dict[str, Any]:
    """Return an independent validated run or raise deterministic issues."""

    issues = _run_issues(payload)
    if issues:
        raise AgentQualityValidationError(issues)
    return deepcopy(payload)
