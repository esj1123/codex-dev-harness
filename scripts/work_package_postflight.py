"""Validate a completed work-package lane against its declared surface."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

try:
    from scripts import work_package_conflict_check as preflight
except ImportError:  # pragma: no cover - direct script execution
    import work_package_conflict_check as preflight


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = preflight.SCHEMA_VERSION
CHECKER_ID = "work_package_postflight"
MAX_OUTPUT_BYTES = 16 * 1024
GIT_TIMEOUT_SECONDS = 10
VERIFICATION_STATUSES = ("PASS", "FAIL", "NOT_RUN", "ENVIRONMENT_BLOCKED")


class GitObservationError(RuntimeError):
    """Raised when the repository cannot be observed safely."""


def base_result() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "checker_id": CHECKER_ID,
        "status": "FAIL",
        "authorization_status": "NOT_AUTHENTICATED",
        "reason_codes": [],
        "task_id": None,
        "lane": None,
        "base_sha": None,
        "contract_basis_sha": None,
        "head_sha": None,
        "plan_digest": None,
        "declared_surface": {
            "write_set_count": 0,
            "generated_output_count": 0,
            "contract_frozen_path_count": 0,
        },
        "actual_surface": {
            "changed_paths": [],
            "untracked_paths": [],
            "commit_count": 0,
            "rename_count": 0,
            "delete_count": 0,
        },
        "verification": {
            "tier": None,
            "status": "NOT_RUN",
        },
        "central_authority_changed": False,
        "performed_actions": [],
    }


def run_git(repo_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as exc:
        raise GitObservationError("GIT_OBSERVATION_FAILED") from exc
    if check and completed.returncode != 0:
        raise GitObservationError("GIT_OBSERVATION_FAILED")
    return completed


def load_payloads(package_paths: list[str], repo_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for package_path in package_paths:
        try:
            payload = preflight.load_package(package_path, repo_root=repo_root)
        except FileNotFoundError:
            result = base_result()
            result["status"] = "BLOCKED"
            result["reason_codes"] = ["PACKAGE_MISSING"]
            return [], result
        except (OSError, ValueError) as exc:
            result = base_result()
            code = str(exc)
            result["reason_codes"] = [code if code.isupper() else "PACKAGE_READ_FAILED"]
            return [], result
        if isinstance(payload, dict):
            payloads.append(payload)
        else:
            result = base_result()
            result["reason_codes"] = ["PACKAGE_NOT_OBJECT"]
            return [], result

    preflight_result = preflight.inspect_payloads(payloads)
    if preflight_result["status"] not in ("PASS", "PASS WITH NOTES"):
        result = base_result()
        result["status"] = preflight_result["status"]
        result["reason_codes"] = list(preflight_result["reason_codes"])
        result["plan_digest"] = preflight_result["plan_digest"]
        return [], result
    return payloads, preflight_result


def parse_name_status(raw: str) -> tuple[list[str], int, int]:
    paths: set[str] = set()
    rename_count = 0
    delete_count = 0
    for line in raw.splitlines():
        fields = line.split("\t")
        if len(fields) < 2:
            raise ValueError("GIT_DIFF_OUTPUT_INVALID")
        status = fields[0]
        if status.startswith(("R", "C")):
            if len(fields) != 3:
                raise ValueError("GIT_DIFF_OUTPUT_INVALID")
            rename_count += 1
            candidates = fields[1:]
        else:
            if len(fields) != 2:
                raise ValueError("GIT_DIFF_OUTPUT_INVALID")
            candidates = fields[1:]
        if status.startswith("D"):
            delete_count += 1
        for candidate in candidates:
            if not preflight.safe_repo_path(candidate):
                raise ValueError("GIT_DIFF_PATH_INVALID")
            paths.add(candidate)
    return sorted(paths), rename_count, delete_count


def observe_repository(repo_root: Path, base_sha: str) -> dict[str, Any]:
    root = repo_root.resolve()
    top_level = Path(run_git(root, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    if top_level != root:
        raise GitObservationError("REPOSITORY_ROOT_MISMATCH")

    head_sha = run_git(root, "rev-parse", "HEAD").stdout.strip()
    if preflight.SHA_PATTERN.fullmatch(head_sha) is None:
        raise GitObservationError("HEAD_SHA_INVALID")
    ancestor = run_git(root, "merge-base", "--is-ancestor", base_sha, head_sha, check=False)
    if ancestor.returncode != 0:
        raise GitObservationError("BASE_NOT_ANCESTOR")

    diff = run_git(root, "diff", "--name-status", "--find-renames", f"{base_sha}..{head_sha}")
    changed_paths, rename_count, delete_count = parse_name_status(diff.stdout)
    untracked_output = run_git(root, "ls-files", "--others", "--exclude-standard").stdout
    untracked_paths = sorted(path for path in untracked_output.splitlines() if path)
    if any(not preflight.safe_repo_path(path) for path in untracked_paths):
        raise ValueError("UNTRACKED_PATH_INVALID")

    tracked_status = run_git(root, "status", "--porcelain", "--untracked-files=no").stdout
    diff_check = run_git(root, "diff", "--check", f"{base_sha}..{head_sha}", check=False)
    commit_count_raw = run_git(root, "rev-list", "--count", f"{base_sha}..{head_sha}").stdout.strip()
    try:
        commit_count = int(commit_count_raw)
    except ValueError as exc:
        raise GitObservationError("COMMIT_COUNT_INVALID") from exc

    return {
        "head_sha": head_sha,
        "changed_paths": changed_paths,
        "untracked_paths": untracked_paths,
        "rename_count": rename_count,
        "delete_count": delete_count,
        "commit_count": commit_count,
        "tracked_dirty": bool(tracked_status.strip()),
        "diff_check_failed": diff_check.returncode != 0 or bool(diff_check.stdout.strip()),
    }


def inspect_postflight(
    package_paths: list[str],
    *,
    task_id: str,
    verification_status: str,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    result = base_result()
    result["verification"]["status"] = verification_status
    if verification_status not in VERIFICATION_STATUSES:
        result["reason_codes"] = ["VERIFICATION_STATUS_INVALID"]
        return result

    payloads, preflight_result = load_payloads(package_paths, repo_root)
    if not payloads:
        preflight_result["verification"]["status"] = verification_status
        return preflight_result

    matching = [payload for payload in payloads if payload["task_id"] == task_id]
    if len(matching) != 1:
        result["status"] = "BLOCKED"
        result["reason_codes"] = ["TASK_ID_NOT_FOUND"]
        result["plan_digest"] = preflight_result["plan_digest"]
        return result

    package = matching[0]
    result.update(
        {
            "task_id": task_id,
            "lane": package["lane"],
            "base_sha": package["base_sha"],
            "contract_basis_sha": package["contract_basis_sha"],
            "plan_digest": preflight_result["plan_digest"],
        }
    )
    result["declared_surface"] = {
        "write_set_count": len(package["write_set"]),
        "generated_output_count": len(package["generated_outputs"]),
        "contract_frozen_path_count": len(package["contract_frozen_paths"]),
    }
    result["verification"] = {
        "tier": package["verification_tier"],
        "status": verification_status,
    }

    try:
        observed = observe_repository(repo_root, str(package["base_sha"]))
    except GitObservationError as exc:
        code = str(exc)
        result["status"] = (
            "BLOCKED"
            if code in ("BASE_NOT_ANCESTOR", "REPOSITORY_ROOT_MISMATCH")
            else "ENVIRONMENT BLOCKED"
        )
        result["reason_codes"] = [code]
        return result
    except ValueError as exc:
        result["reason_codes"] = [str(exc)]
        return result

    result["head_sha"] = observed["head_sha"]
    result["actual_surface"] = {
        "changed_paths": observed["changed_paths"],
        "untracked_paths": observed["untracked_paths"],
        "commit_count": observed["commit_count"],
        "rename_count": observed["rename_count"],
        "delete_count": observed["delete_count"],
    }
    central_changed = any(preflight.integration_only(path) for path in observed["changed_paths"])
    result["central_authority_changed"] = central_changed

    reasons: set[str] = set()
    changed = observed["changed_paths"]
    untracked = observed["untracked_paths"]
    if any(not preflight.path_is_covered(path, package["write_set"]) for path in changed):
        reasons.add("WRITE_SET_EXCEEDED")
    if any(not preflight.path_is_covered(path, package["generated_outputs"]) for path in untracked):
        reasons.add("GENERATED_OUTPUT_SET_EXCEEDED")
    if preflight.path_sets_overlap(
        [*changed, *untracked],
        package["contract_frozen_paths"],
    ):
        reasons.add("CONTRACT_CHANGE_REQUIRED")
    if observed["tracked_dirty"]:
        reasons.add("TRACKED_WORKTREE_DIRTY")
    if observed["rename_count"]:
        reasons.add("RENAME_NOT_ALLOWED")
    if observed["delete_count"]:
        reasons.add("DELETE_NOT_ALLOWED")
    if observed["diff_check_failed"]:
        reasons.add("DIFF_CHECK_FAILED")
    if package["lane"] in ("feature", "contract") and observed["commit_count"] != 1:
        reasons.add("LANE_COMMIT_COUNT_INVALID")
    if package["lane"] == "integration" and observed["commit_count"] < 1:
        reasons.add("LANE_COMMIT_COUNT_INVALID")
    if package["lane"] != "integration" and central_changed:
        reasons.add("INTEGRATION_ONLY_PATH")

    if verification_status == "FAIL":
        reasons.add("VERIFICATION_FAILED")
        result["status"] = "FAIL"
    elif verification_status == "ENVIRONMENT_BLOCKED":
        reasons.add("VERIFICATION_ENVIRONMENT_BLOCKED")
        result["status"] = "ENVIRONMENT BLOCKED"
    elif verification_status == "NOT_RUN":
        reasons.add("VERIFICATION_NOT_RUN")
        result["status"] = "BLOCKED"
    elif reasons:
        result["status"] = "BLOCKED"
    else:
        result["status"] = "PASS"
    result["reason_codes"] = sorted(reasons)
    return result


def json_bytes(result: dict[str, Any]) -> bytes:
    payload = (json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    if len(payload) > MAX_OUTPUT_BYTES:
        raise ValueError("OUTPUT_TOO_LARGE")
    return payload


def text_summary(result: dict[str, Any]) -> str:
    reasons = ",".join(result["reason_codes"]) or "NONE"
    actual = result["actual_surface"]
    return (
        f"status={result['status']} task={result['task_id'] or 'NONE'} "
        f"changed={len(actual['changed_paths'])} untracked={len(actual['untracked_paths'])} "
        f"commits={actual['commit_count']} reasons={reasons}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a completed work-package lane.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--package", action="append", required=True, help="Repo-relative work-package JSON path")
    parser.add_argument("--task-id", required=True, help="Task ID to validate")
    parser.add_argument("--verification-status", required=True, choices=VERIFICATION_STATUSES)
    parser.add_argument("--json", action="store_true", help="Emit bounded deterministic JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = inspect_postflight(
        args.package,
        task_id=args.task_id,
        verification_status=args.verification_status,
        repo_root=Path(args.repo_root),
    )
    if args.json:
        sys.stdout.buffer.write(json_bytes(result))
    else:
        print(text_summary(result))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
