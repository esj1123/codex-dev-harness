"""Validate repository work packages and detect unsafe parallel overlap."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, Iterable

try:
    from scripts.repo_path_policy import safe_repo_path as shared_safe_repo_path
except ImportError:  # pragma: no cover - direct script execution
    from repo_path_policy import safe_repo_path as shared_safe_repo_path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "2"
CHECKER_ID = "work_package_conflict_check"
MAX_INPUT_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 16 * 1024
MAX_PACKAGES = 32
MAX_PATH_ITEMS = 128
MAX_STRING_BYTES = 512
LANES = ("contract", "feature", "integration")
VERIFICATION_TIERS = ("V0", "V1", "V2", "V3")
SIDE_EFFECT_CLASSES = (
    "repository_access",
    "network_read",
    "local_write",
    "execute",
    "stage",
    "commit",
    "push",
    "pull_request",
    "merge",
    "workflow_dispatch",
    "artifact_upload",
    "tag",
    "release",
    "publish",
    "deploy",
    "live_action",
)
REMOTE_SIDE_EFFECTS = {
    "network_read",
    "push",
    "pull_request",
    "merge",
    "workflow_dispatch",
    "artifact_upload",
    "tag",
    "release",
    "publish",
    "deploy",
    "live_action",
}
EXPECTED_KEYS = {
    "schema_version",
    "task_id",
    "base_sha",
    "contract_basis_sha",
    "contract_frozen_paths",
    "lane",
    "depends_on",
    "read_set",
    "write_set",
    "generated_outputs",
    "verification_tier",
    "declared_side_effects",
    "approval_ref",
}
INTEGRATION_ONLY_EXACT = {
    "AGENTS.md",
    "README.md",
    "STATUS.md",
    "ACCEPTANCE_TRACE.md",
    "docs/AUTHORITY_MANIFEST.json",
    "docs/AI_HANDOFF.md",
    "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
    "scripts/agent_quality.py",
    "scripts/quality_gate.py",
    "docs/APPROVED_CORPUS_SOURCE_SET.v2.json",
}
INTEGRATION_ONLY_PREFIXES = (
    "artifacts/",
    ".github/workflows/",
    "scripts/gates/",
    "scripts/agent_quality_lib/",
    "evals/agentic/",
    "evals/golden/",
)
SAFE_ID_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def base_result() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "checker_id": CHECKER_ID,
        "status": "FAIL",
        "authorization_status": "NOT_AUTHENTICATED",
        "parallelizable": False,
        "plan_digest": None,
        "reason_codes": [],
        "package_summary": {
            "package_count": 0,
            "task_ids": [],
            "dependency_count": 0,
            "conflict_count": 0,
        },
        "conflicts": [],
        "performed_actions": [],
    }


def safe_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value.encode("utf-8")) <= 64
        and SAFE_ID_PATTERN.fullmatch(value) is not None
    )


def safe_reference(value: Any) -> bool:
    return value is None or safe_identifier(value)


def safe_repo_path(value: Any) -> bool:
    return shared_safe_repo_path(value, max_bytes=MAX_STRING_BYTES)


def canonical_repo_path(value: str) -> tuple[str, ...]:
    return tuple(part.lower() for part in PurePosixPath(value).parts)


def path_covers(owner: str, candidate: str) -> bool:
    owner_parts = canonical_repo_path(owner)
    candidate_parts = canonical_repo_path(candidate)
    return len(owner_parts) <= len(candidate_parts) and candidate_parts[: len(owner_parts)] == owner_parts


def paths_overlap(left: str, right: str) -> bool:
    return path_covers(left, right) or path_covers(right, left)


def path_is_covered(candidate: str, owners: Iterable[str]) -> bool:
    return any(path_covers(owner, candidate) for owner in owners)


def path_sets_overlap(left: Iterable[str], right: Iterable[str]) -> bool:
    return any(paths_overlap(left_path, right_path) for left_path in left for right_path in right)


def unique_string_list(value: Any, *, item_limit: int = MAX_PATH_ITEMS) -> bool:
    return (
        isinstance(value, list)
        and len(value) <= item_limit
        and all(isinstance(item, str) for item in value)
        and len(value) == len(set(value))
    )


def integration_only(path: str) -> bool:
    canonical = "/".join(canonical_repo_path(path))
    exact = {"/".join(canonical_repo_path(item)) for item in INTEGRATION_ONLY_EXACT}
    prefixes = tuple("/".join(canonical_repo_path(item.rstrip("/"))) for item in INTEGRATION_ONLY_PREFIXES)
    return canonical in exact or any(canonical == prefix or canonical.startswith(f"{prefix}/") for prefix in prefixes)


def package_issues(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["PACKAGE_NOT_OBJECT"]
    issues: list[str] = []
    if set(payload) != EXPECTED_KEYS:
        issues.append("PACKAGE_KEY_SET_INVALID")
        return issues
    if payload["schema_version"] != SCHEMA_VERSION:
        issues.append("SCHEMA_VERSION_INVALID")
    if not safe_identifier(payload["task_id"]):
        issues.append("TASK_ID_INVALID")
    if not isinstance(payload["base_sha"], str) or SHA_PATTERN.fullmatch(payload["base_sha"]) is None:
        issues.append("BASE_SHA_INVALID")
    if (
        not isinstance(payload["contract_basis_sha"], str)
        or SHA_PATTERN.fullmatch(payload["contract_basis_sha"]) is None
    ):
        issues.append("CONTRACT_BASIS_SHA_INVALID")
    if payload["lane"] not in LANES:
        issues.append("LANE_INVALID")
    if payload["verification_tier"] not in VERIFICATION_TIERS:
        issues.append("VERIFICATION_TIER_INVALID")
    if not safe_reference(payload["approval_ref"]):
        issues.append("APPROVAL_REF_INVALID")

    for key in (
        "depends_on",
        "read_set",
        "write_set",
        "generated_outputs",
        "contract_frozen_paths",
        "declared_side_effects",
    ):
        if not unique_string_list(payload[key]):
            issues.append(f"{key.upper()}_INVALID")

    if issues:
        return sorted(set(issues))

    if any(not safe_identifier(item) for item in payload["depends_on"]):
        issues.append("DEPENDENCY_ID_INVALID")
    if payload["task_id"] in payload["depends_on"]:
        issues.append("SELF_DEPENDENCY")
    for key in ("read_set", "write_set", "generated_outputs", "contract_frozen_paths"):
        if any(not safe_repo_path(item) for item in payload[key]):
            issues.append(f"{key.upper()}_PATH_INVALID")
        canonical = [canonical_repo_path(item) for item in payload[key]]
        if len(canonical) != len(set(canonical)):
            issues.append(f"{key.upper()}_CANONICAL_DUPLICATE")
    if payload["contract_basis_sha"] != payload["base_sha"]:
        issues.append("CONTRACT_BASIS_MISMATCH")
    if payload["lane"] == "feature" and not payload["contract_frozen_paths"]:
        issues.append("CONTRACT_FROZEN_PATHS_REQUIRED")
    if any(
        not path_is_covered(frozen, payload["read_set"])
        for frozen in payload["contract_frozen_paths"]
    ):
        issues.append("CONTRACT_FROZEN_PATH_NOT_READ")
    if any(
        not path_is_covered(generated, payload["write_set"])
        for generated in payload["generated_outputs"]
    ):
        issues.append("GENERATED_OUTPUT_OUTSIDE_WRITE_SET")
    if path_sets_overlap(payload["contract_frozen_paths"], payload["write_set"]):
        issues.append("CONTRACT_CHANGE_REQUIRED")
    if any(item not in SIDE_EFFECT_CLASSES for item in payload["declared_side_effects"]):
        issues.append("SIDE_EFFECT_CLASS_INVALID")

    lane = payload["lane"]
    tier = payload["verification_tier"]
    if lane == "feature" and tier != "V1":
        issues.append("FEATURE_VERIFICATION_TIER_INVALID")
    if lane == "contract" and tier not in ("V0", "V1"):
        issues.append("CONTRACT_VERIFICATION_TIER_INVALID")
    if lane == "integration" and tier not in ("V2", "V3"):
        issues.append("INTEGRATION_VERIFICATION_TIER_INVALID")
    if lane != "integration" and REMOTE_SIDE_EFFECTS.intersection(payload["declared_side_effects"]):
        issues.append("REMOTE_SIDE_EFFECT_REQUIRES_INTEGRATION")
    if lane != "integration" and any(integration_only(path) for path in payload["write_set"]):
        issues.append("INTEGRATION_ONLY_PATH")
    return sorted(set(issues))


def dependency_reaches(start: str, target: str, dependencies: dict[str, set[str]]) -> bool:
    pending = list(dependencies.get(start, set()))
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current == target:
            return True
        if current not in visited:
            visited.add(current)
            pending.extend(dependencies.get(current, set()))
    return False


def dependency_cycle(task_ids: Iterable[str], dependencies: dict[str, set[str]]) -> bool:
    return any(dependency_reaches(task_id, task_id, dependencies) for task_id in task_ids)


def plan_digest(payloads: list[dict[str, Any]]) -> str:
    ordered = sorted(payloads, key=lambda payload: str(payload["task_id"]))
    canonical = json.dumps(ordered, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def inspect_payloads(payloads: list[Any]) -> dict[str, Any]:
    result = base_result()
    if not payloads or len(payloads) > MAX_PACKAGES:
        result["reason_codes"] = ["PACKAGE_COUNT_INVALID"]
        return result

    all_issues = sorted({issue for payload in payloads for issue in package_issues(payload)})
    if all_issues:
        result["reason_codes"] = all_issues
        return result

    packages = [payload for payload in payloads if isinstance(payload, dict)]
    result["plan_digest"] = plan_digest(packages)
    task_ids = [str(package["task_id"]) for package in packages]
    result["package_summary"]["package_count"] = len(packages)
    result["package_summary"]["task_ids"] = sorted(task_ids)

    if len(task_ids) != len(set(task_ids)):
        result["status"] = "BLOCKED"
        result["reason_codes"] = ["DUPLICATE_TASK_ID"]
        return result
    if len({str(package["base_sha"]) for package in packages}) != 1:
        result["status"] = "BLOCKED"
        result["reason_codes"] = ["BASE_SHA_MISMATCH"]
        return result
    frozen_sets = {
        tuple(sorted(canonical_repo_path(path) for path in package["contract_frozen_paths"]))
        for package in packages
    }
    if len(frozen_sets) != 1:
        result["status"] = "BLOCKED"
        result["reason_codes"] = ["CONTRACT_FROZEN_PATHS_MISMATCH"]
        return result

    known_ids = set(task_ids)
    dependencies = {
        str(package["task_id"]): set(str(item) for item in package["depends_on"])
        for package in packages
    }
    result["package_summary"]["dependency_count"] = sum(len(items) for items in dependencies.values())
    if any(not items.issubset(known_ids) for items in dependencies.values()):
        result["status"] = "BLOCKED"
        result["reason_codes"] = ["UNKNOWN_DEPENDENCY"]
        return result
    if dependency_cycle(task_ids, dependencies):
        result["status"] = "BLOCKED"
        result["reason_codes"] = ["DEPENDENCY_CYCLE"]
        return result

    conflicts: list[dict[str, str]] = []
    reason_codes: set[str] = set()
    serialization_required = any(dependencies.values())
    for index, left in enumerate(packages):
        left_id = str(left["task_id"])
        left_reads = set(str(item) for item in left["read_set"])
        left_writes = set(str(item) for item in left["write_set"])
        for right in packages[index + 1 :]:
            right_id = str(right["task_id"])
            right_reads = set(str(item) for item in right["read_set"])
            right_writes = set(str(item) for item in right["write_set"])
            if path_sets_overlap(left_writes, right_writes):
                conflicts.append({"left_task_id": left_id, "right_task_id": right_id, "kind": "write_write"})
                reason_codes.add("WRITE_SET_CONFLICT")
                continue
            if path_sets_overlap(left_writes, right_reads) or path_sets_overlap(right_writes, left_reads):
                declared = dependency_reaches(left_id, right_id, dependencies) or dependency_reaches(
                    right_id, left_id, dependencies
                )
                if declared:
                    serialization_required = True
                else:
                    conflicts.append({"left_task_id": left_id, "right_task_id": right_id, "kind": "write_read"})
                    reason_codes.add("UNDECLARED_DEPENDENCY")

    result["conflicts"] = sorted(
        conflicts,
        key=lambda item: (item["left_task_id"], item["right_task_id"], item["kind"]),
    )
    result["package_summary"]["conflict_count"] = len(conflicts)
    if conflicts:
        result["status"] = "BLOCKED"
        result["reason_codes"] = sorted(reason_codes)
    elif serialization_required:
        result["status"] = "PASS WITH NOTES"
        result["parallelizable"] = False
        result["reason_codes"] = ["SERIALIZATION_REQUIRED"]
    else:
        result["status"] = "PASS"
        result["parallelizable"] = True
        result["reason_codes"] = []
    return result


def load_package(raw_path: str, *, repo_root: Path) -> Any:
    if not safe_repo_path(raw_path) or not raw_path.endswith(".json"):
        raise ValueError("PACKAGE_PATH_INVALID")
    root = repo_root.resolve()
    candidate = root.joinpath(*PurePosixPath(raw_path).parts)
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise FileNotFoundError("PACKAGE_MISSING") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("PACKAGE_PATH_OUTSIDE_REPOSITORY") from exc
    info = resolved.stat()
    if not stat.S_ISREG(info.st_mode) or candidate.is_symlink():
        raise ValueError("PACKAGE_NOT_REGULAR_FILE")
    if info.st_size > MAX_INPUT_BYTES:
        raise ValueError("PACKAGE_TOO_LARGE")
    try:
        return json.loads(resolved.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("PACKAGE_NOT_UTF8") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("PACKAGE_JSON_INVALID") from exc


def inspect_packages(package_paths: list[str], *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    payloads: list[Any] = []
    for raw_path in package_paths:
        try:
            payloads.append(load_package(raw_path, repo_root=repo_root))
        except FileNotFoundError:
            result = base_result()
            result["status"] = "BLOCKED"
            result["reason_codes"] = ["PACKAGE_MISSING"]
            return result
        except (OSError, ValueError) as exc:
            result = base_result()
            code = str(exc)
            result["reason_codes"] = [code if code.isupper() else "PACKAGE_READ_FAILED"]
            return result
    return inspect_payloads(payloads)


def json_bytes(result: dict[str, Any]) -> bytes:
    payload = (json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    if len(payload) > MAX_OUTPUT_BYTES:
        raise ValueError("OUTPUT_TOO_LARGE")
    return payload


def text_summary(result: dict[str, Any]) -> str:
    summary = result["package_summary"]
    reasons = ",".join(result["reason_codes"]) or "NONE"
    return (
        f"status={result['status']} parallelizable={str(result['parallelizable']).lower()} "
        f"packages={summary['package_count']} dependencies={summary['dependency_count']} "
        f"conflicts={summary['conflict_count']} reasons={reasons}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check whether repository work packages may run in parallel.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--package", action="append", required=True, help="Repo-relative work-package JSON path")
    parser.add_argument("--json", action="store_true", help="Emit bounded deterministic JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = inspect_packages(args.package, repo_root=Path(args.repo_root))
    if args.json:
        sys.stdout.buffer.write(json_bytes(result))
    else:
        print(text_summary(result))
    return 0 if result["status"] in ("PASS", "PASS WITH NOTES") else 1


if __name__ == "__main__":
    raise SystemExit(main())
