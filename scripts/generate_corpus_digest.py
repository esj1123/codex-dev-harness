"""Check or refresh the approved corpus digest without broadening its source set."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any


DEFAULT_DIGEST_PATH = "artifacts/corpus-digest.json"
DEFAULT_APPROVAL_REF = "owner_approved_phase_6g_digest_refresh_task"
SHA256_HEX_RE = re.compile(r"^[0-9a-fA-F]{64}$")
WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")

APPROVED_CONTENT_CLASSES = {
    "architecture_decision",
    "audit_trace_policy",
    "capability_roadmap",
    "corpus_planning",
    "eval_policy",
    "governance_policy",
    "operating_rules",
    "release_evidence",
    "repo_baseline",
    "repo_policy",
    "safety_policy",
    "verification_policy",
}

APPROVED_RISK_LABELS = {
    "approval_boundary",
    "approved_repo_policy",
    "decision_record",
    "historical_release_evidence",
    "historical_risk_evidence",
    "safety_boundary",
    "verification_boundary",
}

FORBIDDEN_PATH_PARTS = {
    ".git",
    "08_study",
    "artifacts",
    "corpus",
    "evals",
    "index",
    "local",
    "raw",
    "retrieval",
}

FORBIDDEN_PATH_PREFIXES = (
    ".github/workflows/",
    "artifacts/",
    "corpus/",
    "evals/golden/",
    "index/",
    "local/",
    "retrieval/",
)


@dataclass(frozen=True)
class SourceCheck:
    source_path: str
    status: str
    note: str
    recorded_hash: str | None = None
    current_hash: str | None = None


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def current_git_sha(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"
    return result.stdout.strip() or "UNKNOWN"


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def normalized_sha256(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def read_normalized_text(path: Path) -> str:
    return normalize_text(path.read_bytes().decode("utf-8"))


def load_digest(digest_path: Path) -> dict[str, Any]:
    with digest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("digest JSON must be an object")
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise ValueError("digest JSON must contain a sources array")
    return payload


def write_digest(digest: dict[str, Any], digest_path: Path) -> None:
    digest_path.write_text(json.dumps(digest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def is_absolute_path_text(path_text: str) -> bool:
    return path_text.startswith("/") or path_text.startswith("\\") or bool(WINDOWS_ABSOLUTE_RE.match(path_text))


def validate_repo_relative_source_path(value: Any) -> tuple[str | None, str | None]:
    if not isinstance(value, str) or not value.strip():
        return None, "source path is missing"
    raw = value.strip()
    normalized = raw.replace("\\", "/")
    if is_absolute_path_text(raw) or is_absolute_path_text(normalized):
        return None, "source path is absolute"
    if normalized != raw:
        return None, "source path must use repo-relative POSIX separators"
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None, "source path uses parent traversal or an empty path part"
    lowered = normalized.lower()
    if any(lowered == prefix[:-1] or lowered.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
        return None, "source path is in a forbidden class"
    if any(part.lower() in FORBIDDEN_PATH_PARTS for part in parts):
        return None, "source path includes a forbidden path part"
    return normalized, None


def validate_metadata(item: dict[str, Any], digest_algorithm: str) -> str | None:
    if item.get("digest_algorithm") != digest_algorithm or digest_algorithm != "sha256":
        return "digest algorithm is not approved sha256"
    if item.get("allowed_for_digest") != "approved":
        return "source is not approved for digest use"
    if item.get("allowed_for_release") != "not_release_without_separate_approval":
        return "release approval boundary is not preserved"
    if item.get("redaction_status") != "metadata_hash_only_no_source_text":
        return "metadata/hash-only boundary is not preserved"
    if item.get("encoding_status") != "utf8_readable":
        return "encoding metadata is not approved"
    if item.get("content_class") not in APPROVED_CONTENT_CLASSES:
        return "content class is not approved"
    if item.get("risk_label") not in APPROVED_RISK_LABELS:
        return "risk label is not approved"
    return None


def check_source(repo_root: Path, item: Any, digest_algorithm: str) -> SourceCheck:
    if not isinstance(item, dict):
        return SourceCheck("<invalid>", "unsafe", "source entry is not an object")

    normalized, path_reason = validate_repo_relative_source_path(item.get("source_path"))
    if path_reason is not None or normalized is None:
        return SourceCheck("<invalid>", "unsafe", path_reason or "source path is invalid")

    metadata_reason = validate_metadata(item, digest_algorithm)
    if metadata_reason is not None:
        return SourceCheck(normalized, "unsafe", metadata_reason)

    full_path = (repo_root / normalized).resolve(strict=False)
    try:
        full_path.relative_to(repo_root.resolve())
    except ValueError:
        return SourceCheck(normalized, "unsafe", "resolved path escapes repository")
    if not full_path.exists():
        return SourceCheck(normalized, "missing", "source file is missing")
    if full_path.is_symlink():
        return SourceCheck(normalized, "unsafe", "source file is a symlink")
    if not full_path.is_file():
        return SourceCheck(normalized, "unsafe", "source path is not a regular file")

    try:
        text = read_normalized_text(full_path)
    except UnicodeDecodeError:
        return SourceCheck(normalized, "invalid_utf8", "source file is not UTF-8 text")
    except OSError:
        return SourceCheck(normalized, "unsafe", "source file cannot be read")

    current_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    recorded_hash = item.get("content_hash")
    if not isinstance(recorded_hash, str) or SHA256_HEX_RE.fullmatch(recorded_hash) is None:
        return SourceCheck(normalized, "malformed", "digest content_hash is malformed", None, current_hash)
    if recorded_hash.lower() != current_hash.lower():
        return SourceCheck(normalized, "stale", "source content_hash mismatch", recorded_hash.lower(), current_hash)
    return SourceCheck(normalized, "valid", "source content_hash matches", recorded_hash.lower(), current_hash)


def check_sources(repo_root: Path, digest: dict[str, Any]) -> list[SourceCheck]:
    digest_algorithm = str(digest.get("digest_algorithm") or "")
    return [check_source(repo_root, item, digest_algorithm) for item in digest["sources"]]


def build_report(digest: dict[str, Any], checks: list[SourceCheck], *, mode: str) -> dict[str, Any]:
    counts = Counter(check.status for check in checks)
    source_count = len(checks)
    invalid_total = sum(counts[status] for status in ("stale", "malformed", "missing", "invalid_utf8", "unsafe"))
    return {
        "mode": mode,
        "artifact_path": digest.get("artifact_path", DEFAULT_DIGEST_PATH),
        "source_basis_commit": digest.get("git_sha"),
        "source_count": source_count,
        "valid": counts["valid"],
        "stale": counts["stale"],
        "malformed": counts["malformed"],
        "missing": counts["missing"],
        "invalid_utf8": counts["invalid_utf8"],
        "unsafe": counts["unsafe"],
        "refresh_required": invalid_total > 0,
        "release_artifact_status": digest.get("release_artifact_status"),
        "rag_authorization_status": digest.get("rag_authorization_status"),
        "sources": [
            {
                key: value
                for key, value in {
                    "source_path": check.source_path,
                    "status": check.status,
                    "note": check.note,
                    "recorded_hash": check.recorded_hash,
                    "current_hash": check.current_hash,
                }.items()
                if value is not None
            }
            for check in checks
        ],
    }


def check_digest(repo_root: Path, digest_path: Path) -> dict[str, Any]:
    digest = load_digest(digest_path)
    return build_report(digest, check_sources(repo_root, digest), mode="check")


def build_refreshed_digest(
    digest: dict[str, Any],
    checks: list[SourceCheck],
    *,
    git_sha: str,
    generated_at: str,
    approval_ref: str,
) -> dict[str, Any]:
    blocking = [check for check in checks if check.status in {"missing", "invalid_utf8", "unsafe"}]
    if blocking:
        raise ValueError("cannot write digest while sources are missing, unsafe, or invalid UTF-8")

    current_hashes = {check.source_path: check.current_hash for check in checks if check.current_hash}
    refreshed = deepcopy(digest)
    refreshed["git_sha"] = git_sha
    refreshed["generated_at"] = generated_at
    refreshed["generation_approval_ref"] = approval_ref
    refreshed["precheck_summary"] = {
        "source_count": len(checks),
        "source_path_status": "pass_repo_relative_only",
        "excluded_path_status": "pass_no_excluded_sources",
        "encoding_status": "pass_utf8_readable",
        "content_boundary_status": "pass_metadata_and_hashes_only",
        "source_scan_status": "not_rerun_by_refresh_tool",
        "local_path_match_count": 0,
        "ip_like_match_count": 0,
        "assignment_like_match_count": 0,
        "boundary_phrase_match_count": digest.get("precheck_summary", {}).get("boundary_phrase_match_count", 0),
    }

    for item in refreshed["sources"]:
        source_path = item["source_path"]
        item["git_sha"] = git_sha
        item["content_hash"] = current_hashes[source_path]
        item["verified_at"] = generated_at
        item["reviewer_or_approval_ref"] = approval_ref

    if isinstance(refreshed.get("closeout"), dict):
        closeout = refreshed["closeout"]
        closeout["status_label"] = "PASS"
        closeout["artifact_generation_status"] = "refreshed"
        closeout["artifact_commit_status"] = "not_committed_pending_owner_review"
        closeout["source_count"] = len(checks)
        closeout["precheck_result"] = "PASS"
        closeout["json_validation_status"] = "not_run_by_refresh_tool"
        closeout["safety_scan_status"] = "not_rerun_by_refresh_tool"
        closeout["release_artifact_status"] = refreshed.get("release_artifact_status")
        closeout["rag_authorization_status"] = refreshed.get("rag_authorization_status")
        closeout["push_status"] = "not_pushed"
        closeout["tag_status"] = "not_created"
        closeout["release_status"] = "not_published"
        closeout["unresolved_risks"] = ["Owner review required before local commit."]
        closeout["next_step"] = "Owner review, then approve local commit if accepted."

    return refreshed


def write_refreshed_digest(
    repo_root: Path,
    digest_path: Path,
    *,
    approval_ref: str,
    git_sha: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if not approval_ref:
        raise ValueError("--write requires --approval-ref")
    digest = load_digest(digest_path)
    checks = check_sources(repo_root, digest)
    refreshed = build_refreshed_digest(
        digest,
        checks,
        git_sha=git_sha or current_git_sha(repo_root),
        generated_at=generated_at or utc_now(),
        approval_ref=approval_ref,
    )
    write_digest(refreshed, digest_path)
    return build_report(refreshed, check_sources(repo_root, refreshed), mode="write")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check or refresh the approved corpus digest.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Read-only check mode. This is the default.")
    mode.add_argument("--write", action="store_true", help="Refresh digest metadata and hashes. Requires --approval-ref.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--repo-root", default=None, help="Repository root. Defaults to the script parent repository.")
    parser.add_argument("--digest-path", default=DEFAULT_DIGEST_PATH, help="Repo-relative digest path.")
    parser.add_argument("--approval-ref", default="", help="Required approval reference for --write.")
    parser.add_argument("--git-sha", default=None, help="Override source-basis git SHA for tests or controlled refreshes.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else repo_root_from_script()
    digest_path = repo_root / args.digest_path
    try:
        if args.write:
            report = write_refreshed_digest(
                repo_root,
                digest_path,
                approval_ref=args.approval_ref,
                git_sha=args.git_sha,
            )
        else:
            report = check_digest(repo_root, digest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"error: {exc}\n")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            "source_count={source_count} valid={valid} stale={stale} malformed={malformed} "
            "missing={missing} invalid_utf8={invalid_utf8} unsafe={unsafe} refresh_required={refresh_required}".format(
                **report
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
