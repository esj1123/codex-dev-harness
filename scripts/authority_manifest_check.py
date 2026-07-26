"""Validate the repository authority manifest without modifying the repository."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

try:
    from scripts.gates.docs_gate import BASELINE_REQUIRED_DOCS as REQUIRED_DOCS
except ImportError:  # pragma: no cover - direct script execution
    from gates.docs_gate import BASELINE_REQUIRED_DOCS as REQUIRED_DOCS


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1"
VALIDATOR_ID = "authority_manifest_check"
MANIFEST_ID = "authority_manifest"
MANIFEST_PATH = "docs/AUTHORITY_MANIFEST.json"
MAX_MANIFEST_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 16 * 1024
CLASSIFICATION_KEYS = ("current_authority", "durable_policy", "historical_evidence")
EXPECTED_KEYS = {
    "schema_version",
    "manifest_id",
    "current_state",
    "default_read_order",
    *CLASSIFICATION_KEYS,
    "integration_only_exact",
    "integration_only_prefixes",
}
ALLOWED_CURRENT_STATES = {
    "PRE_LARGE_INTEGRATION_SELF_PILOT",
    "READY_FOR_GREENFIELD_INITIALIZATION",
    "READY_FOR_PARALLEL_APPLICATION_DEVELOPMENT",
}
EXPECTED_DEFAULT_READ_ORDER = [
    "AGENTS.md",
    MANIFEST_PATH,
    "PRODUCT.md",
    "MVP.md",
    "STATUS.md",
    "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
    "docs/SAFETY_POLICY.md",
    "docs/VERIFICATION.md",
    "docs/AI_HANDOFF.md",
]
EXPECTED_INTEGRATION_ONLY_EXACT = {
    "AGENTS.md",
    "README.md",
    "STATUS.md",
    "ACCEPTANCE_TRACE.md",
    MANIFEST_PATH,
    "docs/AI_HANDOFF.md",
    "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
    "scripts/agent_quality.py",
    "scripts/quality_gate.py",
    "docs/APPROVED_CORPUS_SOURCE_SET.v2.json",
}
EXPECTED_INTEGRATION_ONLY_PREFIXES = {
    "artifacts/",
    ".github/workflows/",
    "scripts/gates/",
    "evals/golden/",
    "evals/agentic/",
    "scripts/agent_quality_lib/",
}


def base_result() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "status": "FAIL",
        "reason_codes": [],
        "current_state": None,
        "manifest_summary": {
            "required_doc_count": len(REQUIRED_DOCS),
            "classified_required_doc_count": 0,
            "current_authority_count": 0,
            "durable_policy_count": 0,
            "historical_evidence_count": 0,
            "default_read_order_count": 0,
            "integration_only_exact_count": 0,
            "integration_only_prefix_count": 0,
        },
        "performed_actions": [],
    }


def safe_repo_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or not value.isascii():
        return False
    if "\\" in value or "://" in value or value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        return False
    candidate = PurePosixPath(value)
    return (
        not candidate.is_absolute()
        and all(part not in ("", ".", "..") for part in candidate.parts)
        and candidate.as_posix() == value
        and not value.endswith("/")
    )


def safe_repo_prefix(value: Any) -> bool:
    return isinstance(value, str) and value.endswith("/") and safe_repo_path(value[:-1])


def unique_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) for item in value)
        and len(value) == len(set(value))
    )


def validate_manifest(payload: Any, *, repo_root: Path) -> dict[str, Any]:
    result = base_result()
    if not isinstance(payload, dict):
        result["reason_codes"] = ["MANIFEST_NOT_OBJECT"]
        return result
    if set(payload) != EXPECTED_KEYS:
        result["reason_codes"] = ["MANIFEST_KEY_SET_INVALID"]
        return result

    issues: set[str] = set()
    if payload["schema_version"] != SCHEMA_VERSION:
        issues.add("SCHEMA_VERSION_INVALID")
    if payload["manifest_id"] != MANIFEST_ID:
        issues.add("MANIFEST_ID_INVALID")
    if payload["current_state"] not in ALLOWED_CURRENT_STATES:
        issues.add("CURRENT_STATE_INVALID")
    else:
        result["current_state"] = payload["current_state"]

    list_keys = (
        *CLASSIFICATION_KEYS,
        "default_read_order",
        "integration_only_exact",
        "integration_only_prefixes",
    )
    invalid_lists = [key for key in list_keys if not unique_string_list(payload[key])]
    if invalid_lists:
        result["reason_codes"] = sorted(f"{key.upper()}_INVALID" for key in invalid_lists)
        return result

    classifications = {key: list(payload[key]) for key in CLASSIFICATION_KEYS}
    summary = result["manifest_summary"]
    for key in CLASSIFICATION_KEYS:
        summary[f"{key}_count"] = len(classifications[key])
    summary["default_read_order_count"] = len(payload["default_read_order"])
    summary["integration_only_exact_count"] = len(payload["integration_only_exact"])
    summary["integration_only_prefix_count"] = len(payload["integration_only_prefixes"])

    declared_paths = [path for key in CLASSIFICATION_KEYS for path in classifications[key]]
    if any(not safe_repo_path(path) for path in declared_paths):
        issues.add("CLASSIFICATION_PATH_UNSAFE")
    if len(declared_paths) != len(set(declared_paths)):
        issues.add("CLASSIFICATION_DUPLICATE")

    required_docs = set(REQUIRED_DOCS)
    classified_required_docs = set(declared_paths) - {MANIFEST_PATH}
    summary["classified_required_doc_count"] = len(classified_required_docs.intersection(required_docs))
    if required_docs - classified_required_docs:
        issues.add("REQUIRED_DOC_CLASSIFICATION_MISSING")
    if classified_required_docs - required_docs:
        issues.add("UNKNOWN_CLASSIFIED_PATH")
    if classifications["current_authority"].count(MANIFEST_PATH) != 1:
        issues.add("MANIFEST_NOT_CURRENT_AUTHORITY")
    if MANIFEST_PATH in classifications["durable_policy"] or MANIFEST_PATH in classifications["historical_evidence"]:
        issues.add("MANIFEST_CLASSIFICATION_INVALID")

    read_order = payload["default_read_order"]
    if read_order != EXPECTED_DEFAULT_READ_ORDER:
        issues.add("DEFAULT_READ_ORDER_INVALID")
    if not set(read_order).issubset(set(classifications["current_authority"])):
        issues.add("DEFAULT_READ_ORDER_OUTSIDE_CURRENT_AUTHORITY")
    if "ACCEPTANCE_TRACE.md" in read_order or "docs/PROFILE_MATRIX.md" in read_order:
        issues.add("HISTORICAL_OR_MATRIX_IN_DEFAULT_READ_ORDER")

    integration_exact = payload["integration_only_exact"]
    integration_prefixes = payload["integration_only_prefixes"]
    if any(not safe_repo_path(path) for path in integration_exact):
        issues.add("INTEGRATION_EXACT_PATH_UNSAFE")
    if any(not safe_repo_prefix(prefix) for prefix in integration_prefixes):
        issues.add("INTEGRATION_PREFIX_UNSAFE")
    if set(integration_exact) != EXPECTED_INTEGRATION_ONLY_EXACT:
        issues.add("INTEGRATION_EXACT_SET_INVALID")
    if set(integration_prefixes) != EXPECTED_INTEGRATION_ONLY_PREFIXES:
        issues.add("INTEGRATION_PREFIX_SET_INVALID")

    if any(
        not (repo_root / PurePosixPath(path)).is_file()
        or (repo_root / PurePosixPath(path)).is_symlink()
        for path in set(declared_paths)
        if safe_repo_path(path)
    ):
        issues.add("DECLARED_FILE_MISSING_OR_NOT_REGULAR")

    result["reason_codes"] = sorted(issues)
    if not issues:
        result["status"] = "PASS"
    return result


def inspect_manifest(*, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    manifest_path = repo_root / PurePosixPath(MANIFEST_PATH)
    try:
        if manifest_path.is_symlink() or not manifest_path.is_file():
            result = base_result()
            result["reason_codes"] = ["MANIFEST_MISSING_OR_NOT_REGULAR"]
            return result
        if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
            result = base_result()
            result["reason_codes"] = ["MANIFEST_TOO_LARGE"]
            return result
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        result = base_result()
        result["status"] = "ENVIRONMENT BLOCKED"
        result["reason_codes"] = ["MANIFEST_READ_FAILED"]
        return result
    except json.JSONDecodeError:
        result = base_result()
        result["reason_codes"] = ["MANIFEST_JSON_INVALID"]
        return result
    return validate_manifest(payload, repo_root=repo_root)


def json_bytes(result: dict[str, Any]) -> bytes:
    payload = (json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    if len(payload) > MAX_OUTPUT_BYTES:
        raise ValueError("OUTPUT_TOO_LARGE")
    return payload


def text_summary(result: dict[str, Any]) -> str:
    summary = result["manifest_summary"]
    reasons = ",".join(result["reason_codes"]) or "NONE"
    return (
        f"status={result['status']} current_state={result['current_state'] or 'UNKNOWN'} "
        f"required_docs={summary['classified_required_doc_count']}/{summary['required_doc_count']} "
        f"reasons={reasons}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the repository authority manifest.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--json", action="store_true", help="Emit bounded deterministic JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = inspect_manifest(repo_root=Path(args.repo_root))
    if args.json:
        sys.stdout.buffer.write(json_bytes(result))
    else:
        print(text_summary(result))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
