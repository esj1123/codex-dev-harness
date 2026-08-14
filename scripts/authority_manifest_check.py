"""Validate the repository authority manifest without modifying the repository."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

try:
    from scripts.repo_path_policy import (
        safe_repo_path as shared_safe_repo_path,
        safe_repo_prefix as shared_safe_repo_prefix,
    )
except ImportError:  # pragma: no cover - direct script execution
    from repo_path_policy import (
        safe_repo_path as shared_safe_repo_path,
        safe_repo_prefix as shared_safe_repo_prefix,
    )

try:
    from scripts.gates.docs_gate import BASELINE_REQUIRED_DOCS as REQUIRED_DOCS
except ImportError:  # pragma: no cover - direct script execution
    from gates.docs_gate import BASELINE_REQUIRED_DOCS as REQUIRED_DOCS


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "2"
VALIDATOR_ID = "authority_manifest_check"
MANIFEST_ID = "authority_manifest"
MANIFEST_PATH = "docs/AUTHORITY_MANIFEST.json"
MAX_MANIFEST_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 16 * 1024
MAX_PATH_BYTES = 512
CLASSIFICATION_KEYS = ("current_authority", "durable_policy", "historical_evidence")
EXPECTED_KEYS = {
    "schema_version",
    "manifest_id",
    "current_state",
    "conditional_read_order",
    "default_read_order",
    *CLASSIFICATION_KEYS,
    "integration_only_exact",
    "integration_only_prefixes",
    "namespace_authority",
    "operational_inputs",
    "unlisted_document_policy",
}
ALLOWED_CURRENT_STATES = {
    "PRE_LARGE_INTEGRATION_SELF_PILOT",
    "READY_FOR_GREENFIELD_INITIALIZATION",
    "READY_FOR_PARALLEL_APPLICATION_DEVELOPMENT",
    "AGENT_QUALITY_BASELINE_NOT_ESTABLISHED",
    "READY_FOR_PROFILE_CALIBRATION",
    "CORE_HARNESS_READY",
}
EXPECTED_DEFAULT_READ_ORDER = [
    "AGENTS.md",
    MANIFEST_PATH,
    "PRODUCT.md",
    "MVP.md",
    "STATUS.md",
    "docs/SAFETY_POLICY.md",
]
EXPECTED_CONDITIONAL_READ_ORDER = {
    "capability_selection": ["docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md"],
    "handoff": ["docs/AI_HANDOFF.md"],
    "verification": ["docs/VERIFICATION.md", "docs/CI_POLICY.md"],
}
EXPECTED_INTEGRATION_ONLY_EXACT = {
    "AGENTS.md",
    "README.md",
    "STATUS.md",
    "ACCEPTANCE_TRACE.md",
    MANIFEST_PATH,
    "docs/AI_HANDOFF.md",
    "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
    "docs/VERIFICATION_IMPACT_MAP.json",
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
EXPECTED_OPERATIONAL_INPUTS = [
    "docs/APPROVED_CORPUS_SOURCE_SET.v2.json",
    "docs/DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md",
    "docs/JSON_EVIDENCE_POLICY.md",
    "docs/VERIFICATION_IMPACT_MAP.json",
    "evals/agentic/agent-role-profiles.json",
    "evals/agentic/suites/agentic-regression-v2.json",
]
EXPECTED_NAMESPACE_AUTHORITY = {
    "agent_run_evidence_schema": "docs/AGENT_QUALITY_STABILITY_POLICY.md",
    "release_provenance_schema": "docs/SBOM_PROVENANCE_PLAN.md",
    "verification_tier": "docs/VERIFICATION.md",
    "work_package_schema": "docs/CHANGE_CONTROL.md",
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
            "conditional_read_order_count": 0,
            "integration_only_exact_count": 0,
            "integration_only_prefix_count": 0,
            "namespace_authority_count": 0,
            "operational_input_count": 0,
        },
        "performed_actions": [],
    }


def safe_repo_path(value: Any) -> bool:
    return shared_safe_repo_path(value, max_bytes=MAX_PATH_BYTES)


def safe_repo_prefix(value: Any) -> bool:
    return shared_safe_repo_prefix(value, max_bytes=MAX_PATH_BYTES)


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
    if (
        payload["unlisted_document_policy"]
        != "non_authoritative_reference_only_except_declared_operational_inputs"
    ):
        issues.add("UNLISTED_DOCUMENT_POLICY_INVALID")
    if payload["current_state"] not in ALLOWED_CURRENT_STATES:
        issues.add("CURRENT_STATE_INVALID")
    else:
        result["current_state"] = payload["current_state"]

    list_keys = (
        *CLASSIFICATION_KEYS,
        "default_read_order",
        "integration_only_exact",
        "integration_only_prefixes",
        "operational_inputs",
    )
    invalid_lists = [key for key in list_keys if not unique_string_list(payload[key])]
    if invalid_lists:
        result["reason_codes"] = sorted(f"{key.upper()}_INVALID" for key in invalid_lists)
        return result

    classifications = {key: list(payload[key]) for key in CLASSIFICATION_KEYS}
    conditional_read_order = payload["conditional_read_order"]
    if (
        not isinstance(conditional_read_order, dict)
        or set(conditional_read_order) != set(EXPECTED_CONDITIONAL_READ_ORDER)
        or any(
            not unique_string_list(value)
            for value in conditional_read_order.values()
        )
    ):
        result["reason_codes"] = ["CONDITIONAL_READ_ORDER_INVALID"]
        return result
    summary = result["manifest_summary"]
    for key in CLASSIFICATION_KEYS:
        summary[f"{key}_count"] = len(classifications[key])
    summary["default_read_order_count"] = len(payload["default_read_order"])
    summary["conditional_read_order_count"] = sum(
        len(paths) for paths in conditional_read_order.values()
    )
    summary["integration_only_exact_count"] = len(payload["integration_only_exact"])
    summary["integration_only_prefix_count"] = len(payload["integration_only_prefixes"])
    summary["operational_input_count"] = len(payload["operational_inputs"])

    namespace_authority = payload["namespace_authority"]
    if not isinstance(namespace_authority, dict):
        issues.add("NAMESPACE_AUTHORITY_SET_INVALID")
        namespace_owner_paths: list[str] = []
    else:
        summary["namespace_authority_count"] = len(namespace_authority)
        if namespace_authority != EXPECTED_NAMESPACE_AUTHORITY:
            issues.add("NAMESPACE_AUTHORITY_SET_INVALID")
        namespace_owner_paths = [
            value for value in namespace_authority.values() if isinstance(value, str)
        ]
        if len(namespace_owner_paths) != len(namespace_authority) or any(
            not safe_repo_path(path) for path in namespace_owner_paths
        ):
            issues.add("NAMESPACE_AUTHORITY_PATH_UNSAFE")

    declared_paths = [path for key in CLASSIFICATION_KEYS for path in classifications[key]]
    if any(not safe_repo_path(path) for path in declared_paths):
        issues.add("CLASSIFICATION_PATH_UNSAFE")
    if len(declared_paths) != len(set(declared_paths)):
        issues.add("CLASSIFICATION_DUPLICATE")
    if any(path not in declared_paths for path in namespace_owner_paths):
        issues.add("NAMESPACE_AUTHORITY_OUTSIDE_AUTHORITY")

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
    if conditional_read_order != EXPECTED_CONDITIONAL_READ_ORDER:
        issues.add("CONDITIONAL_READ_ORDER_INVALID")
    conditional_paths = [
        path for paths in conditional_read_order.values() for path in paths
    ]
    if (
        any(not safe_repo_path(path) for path in conditional_paths)
        or not set(conditional_paths).issubset(set(declared_paths))
    ):
        issues.add("CONDITIONAL_READ_ORDER_OUTSIDE_AUTHORITY")

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

    operational_inputs = payload["operational_inputs"]
    if operational_inputs != EXPECTED_OPERATIONAL_INPUTS:
        issues.add("OPERATIONAL_INPUT_SET_INVALID")
    if any(not safe_repo_path(path) for path in operational_inputs):
        issues.add("OPERATIONAL_INPUT_PATH_UNSAFE")
    if set(operational_inputs).intersection(declared_paths):
        issues.add("OPERATIONAL_INPUT_CLASSIFICATION_OVERLAP")
    if any(
        not (repo_root / PurePosixPath(path)).is_file()
        or (repo_root / PurePosixPath(path)).is_symlink()
        for path in operational_inputs
        if safe_repo_path(path)
    ):
        issues.add("OPERATIONAL_INPUT_MISSING_OR_NOT_REGULAR")

    if any(
        not (repo_root / PurePosixPath(path)).is_file()
        or (repo_root / PurePosixPath(path)).is_symlink()
        for path in set(declared_paths)
        if safe_repo_path(path)
    ):
        issues.add("DECLARED_FILE_MISSING_OR_NOT_REGULAR")

    status_path = repo_root / "STATUS.md"
    try:
        status_text = status_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        issues.add("STATUS_CURRENT_STATE_UNREADABLE")
    else:
        match = re.search(
            r"(?ms)^## Current State\s*$\s*^`([A-Z][A-Z0-9_]*)`\s*$",
            status_text,
        )
        if match is None:
            issues.add("STATUS_CURRENT_STATE_MISSING")
        elif match.group(1) != payload["current_state"]:
            issues.add("STATUS_CURRENT_STATE_MISMATCH")

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
