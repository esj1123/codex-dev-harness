from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

sys.dont_write_bytecode = True

try:
    from scripts import generate_checksums
except ModuleNotFoundError:  # Direct script execution places scripts/ on sys.path.
    import generate_checksums  # type: ignore[no-redef]


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1"
CANDIDATE_ID = "local_release_evidence_preflight_dry_run"
MAX_INPUT_BYTES = 1024 * 1024
MAX_OUTPUT_BYTES = 8 * 1024
MAX_GIT_OUTPUT_BYTES = 64 * 1024
GIT_TIMEOUT_SECONDS = 10

POLICY_PATHS = (
    "docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md",
    "docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md",
    "docs/RELEASE_BUNDLE_POLICY.md",
    "docs/RELEASE_MANIFEST_POLICY.md",
    "docs/SBOM_PROVENANCE_PLAN.md",
)
RELEASE_ARTIFACT_PATHS = (
    "artifacts/release-manifest.json",
    "artifacts/checksums.sha256",
    "artifacts/sbom.spdx.json",
    "artifacts/sbom.cdx.json",
    "artifacts/provenance.intoto.jsonl",
)
CHECKSUM_INPUT_PATHS = (
    "artifacts/eval-report.json",
    "artifacts/provenance.intoto.jsonl",
    "artifacts/release-manifest.json",
    "artifacts/sbom.cdx.json",
    "artifacts/sbom.spdx.json",
)
READ_ONLY_INPUT_PATHS = POLICY_PATHS + RELEASE_ARTIFACT_PATHS + ("artifacts/eval-report.json",)
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SAFE_REF_PATTERN = re.compile(r"^[A-Za-z0-9._/-]{1,128}$")


class GitInspectionError(RuntimeError):
    pass


class EvidenceValidationError(ValueError):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def base_result(*, dry_run: bool) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "candidate_id": CANDIDATE_ID,
        "dry_run": dry_run,
        "status": "NOT RUN",
        "readiness": "NOT RUN",
        "reason_codes": [],
        "repository_state": {
            "branch": None,
            "head_commit": None,
            "upstream_ref": None,
            "pushed_commit": None,
            "pushed_commit_basis": "local_tracking_ref",
            "tracked_changes": 0,
            "untracked_files": 0,
        },
        "evidence_state": {
            "source_basis_commit": None,
            "artifact_containing_commit": None,
            "artifact_paths": list(RELEASE_ARTIFACT_PATHS),
            "checksum_input_paths": list(CHECKSUM_INPUT_PATHS),
            "checksum_entry_count": 0,
            "checksum_status": "NOT RUN",
            "license_status": "NOT RUN",
        },
        "external_state": {
            "tag_target": None,
            "release_target": {"status": "NOT RUN", "reason_code": "NETWORK_NOT_AUTHORIZED"},
            "uploaded_artifact": {"status": "NOT RUN", "reason_code": "UPLOAD_NOT_AUTHORIZED"},
            "downstream_release": {"status": "NOT RUN", "reason_code": "DOWNSTREAM_NOT_AUTHORIZED"},
        },
        "performed_actions": [],
    }


def run_git(repo_root: Path, args: list[str], *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as exc:
        raise GitInspectionError("GIT_UNAVAILABLE") from exc
    if len(completed.stdout.encode("utf-8")) > MAX_GIT_OUTPUT_BYTES:
        raise GitInspectionError("GIT_OUTPUT_LIMIT_EXCEEDED")
    if completed.returncode != 0 and not allow_failure:
        raise GitInspectionError("GIT_COMMAND_FAILED")
    return completed


def safe_ref(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.strip()
    return candidate if SAFE_REF_PATTERN.fullmatch(candidate) else None


def safe_sha(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    candidate = value.strip().lower()
    return candidate if SHA_PATTERN.fullmatch(candidate) else None


def status_snapshot(repo_root: Path) -> tuple[str, int, int]:
    output = run_git(repo_root, ["status", "--porcelain=v1", "--untracked-files=normal"]).stdout
    lines = tuple(line for line in output.splitlines() if line)
    untracked = sum(1 for line in lines if line.startswith("??"))
    return output, len(lines) - untracked, untracked


def repo_input_path(repo_root: Path, relative_path: str) -> Path:
    resolved_root = repo_root.resolve()
    resolved = (resolved_root / relative_path).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise EvidenceValidationError("UNSAFE_INPUT_PATH") from exc
    return resolved


def read_text_input(repo_root: Path, relative_path: str) -> str:
    path = repo_input_path(repo_root, relative_path)
    if not path.is_file():
        raise FileNotFoundError(relative_path)
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise EvidenceValidationError("INPUT_SIZE_LIMIT_EXCEEDED")
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceValidationError("INVALID_UTF8_INPUT") from exc


def read_json_object(repo_root: Path, relative_path: str) -> dict[str, Any]:
    try:
        value = json.loads(read_text_input(repo_root, relative_path))
    except json.JSONDecodeError as exc:
        raise EvidenceValidationError("MALFORMED_RELEASE_EVIDENCE") from exc
    if not isinstance(value, dict):
        raise EvidenceValidationError("MALFORMED_RELEASE_EVIDENCE")
    return value


def read_provenance(repo_root: Path) -> dict[str, Any]:
    lines = [line for line in read_text_input(repo_root, "artifacts/provenance.intoto.jsonl").splitlines() if line]
    if len(lines) != 1:
        raise EvidenceValidationError("MALFORMED_RELEASE_EVIDENCE")
    try:
        value = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise EvidenceValidationError("MALFORMED_RELEASE_EVIDENCE") from exc
    if not isinstance(value, dict):
        raise EvidenceValidationError("MALFORMED_RELEASE_EVIDENCE")
    return value


def artifact_commits(repo_root: Path) -> dict[str, str]:
    commits: dict[str, str] = {}
    for relative_path in RELEASE_ARTIFACT_PATHS:
        output = run_git(repo_root, ["log", "-1", "--format=%H", "--", relative_path]).stdout.strip()
        commit = safe_sha(output)
        if commit is None:
            raise EvidenceValidationError("ARTIFACT_COMMIT_MISSING")
        commits[relative_path] = commit
    return commits


def is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    completed = run_git(repo_root, ["merge-base", "--is-ancestor", ancestor, descendant], allow_failure=True)
    return completed.returncode == 0


def find_spdx_package(spdx: dict[str, Any], repository: str) -> dict[str, Any] | None:
    packages = spdx.get("packages")
    if not isinstance(packages, list):
        return None
    for package in packages:
        if isinstance(package, dict) and package.get("name") == repository:
            return package
    return None


def validate_evidence(repo_root: Path, result: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    fail_reasons: list[str] = []
    blocked_reasons: list[str] = []
    note_reasons: list[str] = []

    try:
        for relative_path in READ_ONLY_INPUT_PATHS:
            read_text_input(repo_root, relative_path)
    except FileNotFoundError:
        blocked_reasons.append("MISSING_RELEASE_EVIDENCE")
        return fail_reasons, blocked_reasons, note_reasons
    except EvidenceValidationError as exc:
        fail_reasons.append(exc.reason_code)
        return fail_reasons, blocked_reasons, note_reasons

    try:
        manifest = read_json_object(repo_root, "artifacts/release-manifest.json")
        spdx = read_json_object(repo_root, "artifacts/sbom.spdx.json")
        cyclonedx = read_json_object(repo_root, "artifacts/sbom.cdx.json")
        provenance = read_provenance(repo_root)
    except EvidenceValidationError as exc:
        fail_reasons.append(exc.reason_code)
        return fail_reasons, blocked_reasons, note_reasons

    source_basis = safe_sha(manifest.get("git_commit"))
    repository = manifest.get("repository")
    manifest_files = manifest.get("files")
    included_roots = manifest.get("included_roots")
    if source_basis is None or not isinstance(repository, str):
        fail_reasons.append("MALFORMED_RELEASE_EVIDENCE")
        return fail_reasons, blocked_reasons, note_reasons

    result["evidence_state"]["source_basis_commit"] = source_basis
    file_paths = {
        entry.get("path")
        for entry in manifest_files
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    } if isinstance(manifest_files, list) else set()
    roots = set(included_roots) if isinstance(included_roots, list) else set()
    if not {"LICENSE", "SECURITY.md"}.issubset(file_paths) or not {"LICENSE", "SECURITY.md"}.issubset(roots):
        fail_reasons.append("LICENSE_METADATA_MISMATCH")

    spdx_package = find_spdx_package(spdx, repository)
    cdx_component = cyclonedx.get("metadata", {}).get("component") if isinstance(cyclonedx.get("metadata"), dict) else None
    provenance_repo = provenance.get("predicate", {}).get("repo") if isinstance(provenance.get("predicate"), dict) else None
    provenance_basis = safe_sha(provenance_repo.get("git_commit")) if isinstance(provenance_repo, dict) else None
    spdx_basis = safe_sha(spdx_package.get("versionInfo")) if isinstance(spdx_package, dict) else None
    cdx_basis = safe_sha(cdx_component.get("version")) if isinstance(cdx_component, dict) else None
    if {source_basis, provenance_basis, spdx_basis, cdx_basis} != {source_basis}:
        fail_reasons.append("SOURCE_BASIS_MISMATCH")

    spdx_mit = bool(
        isinstance(spdx_package, dict)
        and spdx_package.get("licenseDeclared") == "MIT"
        and spdx_package.get("licenseConcluded") == "MIT"
        and spdx_package.get("copyrightText") == "Copyright (c) 2026 esj1123"
    )
    cdx_licenses = cdx_component.get("licenses") if isinstance(cdx_component, dict) else None
    cdx_mit = bool(
        isinstance(cdx_licenses, list)
        and any(
            isinstance(item, dict)
            and isinstance(item.get("license"), dict)
            and item["license"].get("id") == "MIT"
            for item in cdx_licenses
        )
    )
    if spdx_mit and cdx_mit:
        result["evidence_state"]["license_status"] = "PASS"
    else:
        result["evidence_state"]["license_status"] = "FAIL"
        fail_reasons.append("LICENSE_METADATA_MISMATCH")

    checksum_path = repo_input_path(repo_root, "artifacts/checksums.sha256")
    manifest_path = repo_input_path(repo_root, "artifacts/release-manifest.json")
    try:
        entries = generate_checksums.parse_checksum_lines(
            checksum_path.read_text(encoding="utf-8").splitlines(),
            "artifacts/checksums.sha256",
        )
        if set(entries) != set(CHECKSUM_INPUT_PATHS):
            raise EvidenceValidationError("CHECKSUM_ENTRY_SET_MISMATCH")
        checksum_passed, _ = generate_checksums.verify_checksums(
            repo_root,
            manifest_path,
            checksum_path,
            allow_missing=False,
        )
    except (FileNotFoundError, UnicodeDecodeError, ValueError) as exc:
        reason = exc.reason_code if isinstance(exc, EvidenceValidationError) else "MALFORMED_RELEASE_EVIDENCE"
        fail_reasons.append(reason)
        checksum_passed = False
        entries = {}
    result["evidence_state"]["checksum_entry_count"] = len(entries)
    result["evidence_state"]["checksum_status"] = "PASS" if checksum_passed else "FAIL"
    if not checksum_passed:
        fail_reasons.append("CHECKSUM_MISMATCH")

    try:
        commits = artifact_commits(repo_root)
    except EvidenceValidationError as exc:
        blocked_reasons.append(exc.reason_code)
        return fail_reasons, blocked_reasons, note_reasons
    unique_commits = set(commits.values())
    if len(unique_commits) != 1:
        fail_reasons.append("ARTIFACT_COMMIT_MISMATCH")
        return fail_reasons, blocked_reasons, note_reasons

    artifact_commit = next(iter(unique_commits))
    result["evidence_state"]["artifact_containing_commit"] = artifact_commit
    head_commit = result["repository_state"]["head_commit"]
    if not is_ancestor(repo_root, source_basis, artifact_commit):
        fail_reasons.append("SOURCE_BASIS_NOT_ANCESTOR")
    if not isinstance(head_commit, str) or not is_ancestor(repo_root, artifact_commit, head_commit):
        blocked_reasons.append("ARTIFACT_COMMIT_NOT_ANCESTOR")
    elif artifact_commit != head_commit:
        note_reasons.append("EVIDENCE_REFRESH_RECOMMENDED")

    return fail_reasons, blocked_reasons, note_reasons


def inspect_preflight(repo_root: Path) -> dict[str, Any]:
    result = base_result(dry_run=True)
    repo_root = repo_root.resolve()
    before_raw: str | None = None

    try:
        if not repo_root.is_dir():
            raise GitInspectionError("NOT_GIT_REPOSITORY")
        top_level = run_git(repo_root, ["rev-parse", "--show-toplevel"]).stdout.strip()
        try:
            if Path(top_level).resolve() != repo_root:
                raise GitInspectionError("NOT_GIT_REPOSITORY")
        except (OSError, RuntimeError) as exc:
            raise GitInspectionError("NOT_GIT_REPOSITORY") from exc

        before_raw, tracked_changes, untracked_files = status_snapshot(repo_root)
        branch = safe_ref(run_git(repo_root, ["branch", "--show-current"]).stdout)
        head_commit = safe_sha(run_git(repo_root, ["rev-parse", "HEAD"]).stdout)
        if branch is None or head_commit is None:
            raise GitInspectionError("GIT_STATE_INVALID")

        upstream_result = run_git(
            repo_root,
            ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
            allow_failure=True,
        )
        upstream_ref = safe_ref(upstream_result.stdout) if upstream_result.returncode == 0 else None
        upstream_commit = None
        if upstream_ref is not None:
            upstream_commit = safe_sha(run_git(repo_root, ["rev-parse", "@{upstream}"]).stdout)
        tag_lines = [line.strip() for line in run_git(repo_root, ["tag", "--points-at", "HEAD"]).stdout.splitlines() if line.strip()]
        tag_target = safe_ref(sorted(tag_lines)[0]) if tag_lines else None

        result["repository_state"].update(
            {
                "branch": branch,
                "head_commit": head_commit,
                "upstream_ref": upstream_ref,
                "pushed_commit": upstream_commit,
                "tracked_changes": tracked_changes,
                "untracked_files": untracked_files,
            }
        )
        result["external_state"]["tag_target"] = tag_target

        blocked_reasons: list[str] = []
        if tracked_changes:
            blocked_reasons.append("DIRTY_WORKTREE")
        if untracked_files:
            blocked_reasons.append("UNTRACKED_FILES_PRESENT")
        if upstream_ref is None or upstream_commit is None:
            blocked_reasons.append("UPSTREAM_MISSING")
        else:
            upstream_branch = upstream_ref.rsplit("/", 1)[-1]
            if upstream_branch != branch or upstream_commit != head_commit:
                blocked_reasons.append("HEAD_UPSTREAM_MISMATCH")

        fail_reasons, evidence_blocked, note_reasons = validate_evidence(repo_root, result)
        blocked_reasons.extend(evidence_blocked)

        after_raw, _, _ = status_snapshot(repo_root)
        if before_raw != after_raw:
            fail_reasons.append("CLEANUP_VERIFICATION_FAILED")

        if fail_reasons:
            result["status"] = "FAIL"
            result["readiness"] = "BLOCKED"
            result["reason_codes"] = sorted(set(fail_reasons + blocked_reasons + note_reasons))
        elif blocked_reasons:
            result["status"] = "BLOCKED"
            result["readiness"] = "BLOCKED"
            result["reason_codes"] = sorted(set(blocked_reasons + note_reasons))
        elif note_reasons:
            result["status"] = "PASS WITH NOTES"
            result["readiness"] = "READY"
            result["reason_codes"] = sorted(set(note_reasons))
        else:
            result["status"] = "PASS"
            result["readiness"] = "READY"
            result["reason_codes"] = []
    except GitInspectionError as exc:
        result["status"] = "ENVIRONMENT BLOCKED"
        result["readiness"] = "BLOCKED"
        result["reason_codes"] = [str(exc)]

    return result


def json_bytes(result: dict[str, Any]) -> bytes:
    encoded = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(encoded) > MAX_OUTPUT_BYTES:
        raise ValueError("bounded JSON output exceeded")
    return encoded


def text_summary(result: dict[str, Any]) -> str:
    reasons = ",".join(result["reason_codes"]) or "NONE"
    head = result["repository_state"]["head_commit"] or "UNKNOWN"
    return (
        f"{result['status']} {CANDIDATE_ID} readiness={result['readiness']} "
        f"head={head} reasons={reasons}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local release evidence preflight in read-only dry-run mode.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect")
    parser.add_argument("--dry-run", action="store_true", help="Required read-only execution mode")
    parser.add_argument("--json", action="store_true", help="Emit bounded deterministic JSON stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.dry_run:
        result = inspect_preflight(Path(args.repo_root))
    else:
        result = base_result(dry_run=False)
        result["reason_codes"] = ["DRY_RUN_REQUIRED"]

    if args.json:
        try:
            sys.stdout.buffer.write(json_bytes(result))
        except ValueError:
            fallback = base_result(dry_run=bool(args.dry_run))
            fallback["status"] = "FAIL"
            fallback["readiness"] = "BLOCKED"
            fallback["reason_codes"] = ["OUTPUT_LIMIT_EXCEEDED"]
            sys.stdout.buffer.write(json_bytes(fallback))
            return 1
    else:
        print(text_summary(result))

    if result["status"] in {"PASS", "PASS WITH NOTES"}:
        return 0
    if result["status"] == "NOT RUN":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
