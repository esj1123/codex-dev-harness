"""Build a read-only advisory verification plan from a Git path diff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = "docs/VERIFICATION_IMPACT_MAP.json"
SCHEMA_VERSION = "1"
PLANNER_ID = "verification_plan"
MAX_MAP_BYTES = 64 * 1024
MAX_GIT_OUTPUT_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 16 * 1024
MAX_CHANGED_PATHS = 512
GIT_TIMEOUT_SECONDS = 10
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SAFE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
TIERS = ("V0", "V1", "V2")
TIER_RANK = {tier: index for index, tier in enumerate(TIERS)}
RULE_KEYS = {
    "rule_id",
    "match_kind",
    "patterns",
    "minimum_tier",
    "command_ids",
    "digest_check_required",
    "checksum_check_required",
    "render_check_required",
    "integration_owner_required",
}


class GitObservationError(RuntimeError):
    """Raised when Git cannot be observed safely."""


class MapValidationError(ValueError):
    """Raised when the tracked impact map is malformed."""


def base_result() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "planner_id": PLANNER_ID,
        "status": "FAIL",
        "minimum_tier": None,
        "changed_paths": [],
        "matched_rule_ids": [],
        "required_command_ids": [],
        "not_required_command_ids": [],
        "digest_check_required": False,
        "checksum_check_required": False,
        "render_check_required": False,
        "integration_owner_required": False,
        "reason_codes": [],
        "performed_actions": [],
    }


def safe_repo_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or not value.isascii():
        return False
    if len(value.encode("utf-8")) > 512:
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


def safe_prefix(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.endswith("/")
        and safe_repo_path(value[:-1])
    )


def run_git(
    repo_root: Path,
    *args: str,
    allow_failure: bool = False,
) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as exc:
        raise GitObservationError("GIT_UNAVAILABLE") from exc
    if len(completed.stdout.encode("utf-8")) > MAX_GIT_OUTPUT_BYTES:
        raise GitObservationError("GIT_OUTPUT_LIMIT_EXCEEDED")
    if completed.returncode != 0 and not allow_failure:
        raise GitObservationError("GIT_COMMAND_FAILED")
    return completed


def validate_repository(repo_root: Path) -> Path:
    root = repo_root.resolve()
    top_level = run_git(root, "rev-parse", "--show-toplevel").stdout.strip()
    try:
        observed_root = Path(top_level).resolve()
    except OSError as exc:
        raise GitObservationError("REPOSITORY_ROOT_INVALID") from exc
    if observed_root != root:
        raise GitObservationError("REPOSITORY_ROOT_MISMATCH")
    return root


def resolve_commit(repo_root: Path, value: str, *, label: str) -> tuple[str | None, str | None]:
    if SHA_PATTERN.fullmatch(value) is None:
        return None, f"{label}_SHA_INVALID"
    completed = run_git(
        repo_root,
        "rev-parse",
        "--verify",
        f"{value}^{{commit}}",
        allow_failure=True,
    )
    if completed.returncode != 0:
        return None, f"{label}_REF_NOT_FOUND"
    resolved = completed.stdout.strip()
    if SHA_PATTERN.fullmatch(resolved) is None:
        raise GitObservationError("GIT_REF_OUTPUT_INVALID")
    return resolved, None


def observe_changed_paths(repo_root: Path, base_sha: str, head_sha: str) -> tuple[list[str], str | None]:
    ancestor = run_git(
        repo_root,
        "merge-base",
        "--is-ancestor",
        base_sha,
        head_sha,
        allow_failure=True,
    )
    if ancestor.returncode == 1:
        return [], "BASE_NOT_ANCESTOR"
    if ancestor.returncode != 0:
        raise GitObservationError("GIT_ANCESTRY_CHECK_FAILED")

    diff = run_git(repo_root, "diff", "--name-only", f"{base_sha}..{head_sha}")
    paths = sorted(set(line for line in diff.stdout.splitlines() if line))
    if len(paths) > MAX_CHANGED_PATHS:
        raise GitObservationError("CHANGED_PATH_LIMIT_EXCEEDED")
    if any(not safe_repo_path(path) for path in paths):
        raise MapValidationError("GIT_DIFF_PATH_INVALID")
    return paths, None


def read_json_object(path: Path, *, max_bytes: int, error_code: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise MapValidationError(error_code) from exc
    if len(raw) > max_bytes:
        raise MapValidationError(f"{error_code}_TOO_LARGE")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MapValidationError(error_code) from exc
    if not isinstance(value, dict):
        raise MapValidationError(error_code)
    return value


def validate_map(payload: dict[str, Any]) -> dict[str, Any]:
    if set(payload) != {
        "schema_version",
        "planner_id",
        "command_ids",
        "tier_command_ids",
        "rules",
    }:
        raise MapValidationError("IMPACT_MAP_KEY_SET_INVALID")
    if payload["schema_version"] != SCHEMA_VERSION or payload["planner_id"] != PLANNER_ID:
        raise MapValidationError("IMPACT_MAP_IDENTITY_INVALID")

    command_ids = payload["command_ids"]
    if (
        not isinstance(command_ids, list)
        or len(command_ids) != len(set(command_ids))
        or not command_ids
        or any(not isinstance(item, str) or SAFE_ID_PATTERN.fullmatch(item) is None for item in command_ids)
    ):
        raise MapValidationError("COMMAND_ID_SET_INVALID")
    command_set = set(command_ids)

    tier_commands = payload["tier_command_ids"]
    if not isinstance(tier_commands, dict) or set(tier_commands) != set(TIERS):
        raise MapValidationError("TIER_COMMAND_SET_INVALID")
    for tier in TIERS:
        items = tier_commands[tier]
        if (
            not isinstance(items, list)
            or len(items) != len(set(items))
            or not set(items).issubset(command_set)
        ):
            raise MapValidationError("TIER_COMMAND_SET_INVALID")

    rules = payload["rules"]
    if not isinstance(rules, list) or not rules or len(rules) > 64:
        raise MapValidationError("RULE_SET_INVALID")
    rule_ids: set[str] = set()
    for rule in rules:
        if not isinstance(rule, dict) or set(rule) != RULE_KEYS:
            raise MapValidationError("RULE_KEY_SET_INVALID")
        rule_id = rule["rule_id"]
        if (
            not isinstance(rule_id, str)
            or SAFE_ID_PATTERN.fullmatch(rule_id) is None
            or rule_id in rule_ids
        ):
            raise MapValidationError("RULE_ID_INVALID")
        rule_ids.add(rule_id)
        if rule["match_kind"] not in ("exact", "prefix", "corpus_sources"):
            raise MapValidationError("RULE_MATCH_KIND_INVALID")
        patterns = rule["patterns"]
        if (
            not isinstance(patterns, list)
            or not patterns
            or len(patterns) > 128
            or len(patterns) != len(set(patterns))
        ):
            raise MapValidationError("RULE_PATTERN_SET_INVALID")
        path_validator = safe_prefix if rule["match_kind"] == "prefix" else safe_repo_path
        if any(not path_validator(pattern) for pattern in patterns):
            raise MapValidationError("RULE_PATTERN_INVALID")
        if rule["match_kind"] == "corpus_sources" and len(patterns) != 1:
            raise MapValidationError("CORPUS_SOURCE_RULE_INVALID")
        if rule["minimum_tier"] not in TIERS:
            raise MapValidationError("RULE_TIER_INVALID")
        if (
            not isinstance(rule["command_ids"], list)
            or len(rule["command_ids"]) != len(set(rule["command_ids"]))
            or not set(rule["command_ids"]).issubset(command_set)
        ):
            raise MapValidationError("RULE_COMMAND_SET_INVALID")
        for key in (
            "digest_check_required",
            "checksum_check_required",
            "render_check_required",
            "integration_owner_required",
        ):
            if not isinstance(rule[key], bool):
                raise MapValidationError("RULE_FLAG_INVALID")
    return payload


def load_impact_map(repo_root: Path) -> dict[str, Any]:
    return validate_map(
        read_json_object(
            repo_root / MAP_PATH,
            max_bytes=MAX_MAP_BYTES,
            error_code="IMPACT_MAP_INVALID",
        )
    )


def corpus_source_paths(repo_root: Path, relative_path: str) -> set[str]:
    payload = read_json_object(
        repo_root / relative_path,
        max_bytes=MAX_MAP_BYTES,
        error_code="CORPUS_DIGEST_INVALID",
    )
    sources = payload.get("sources")
    if not isinstance(sources, list) or len(sources) > 128:
        raise MapValidationError("CORPUS_SOURCE_SET_INVALID")
    paths: set[str] = set()
    for source in sources:
        if not isinstance(source, dict) or not safe_repo_path(source.get("source_path")):
            raise MapValidationError("CORPUS_SOURCE_SET_INVALID")
        paths.add(source["source_path"])
    if len(paths) != len(sources):
        raise MapValidationError("CORPUS_SOURCE_SET_INVALID")
    return paths


def matching_paths(
    changed_paths: list[str],
    rule: dict[str, Any],
    *,
    repo_root: Path,
) -> set[str]:
    kind = rule["match_kind"]
    patterns = rule["patterns"]
    if kind == "exact":
        return set(changed_paths).intersection(patterns)
    if kind == "prefix":
        return {
            path
            for path in changed_paths
            if any(path.startswith(prefix) for prefix in patterns)
        }
    approved_sources = corpus_source_paths(repo_root, patterns[0])
    return set(changed_paths).intersection(approved_sources)


def build_plan(repo_root: Path, changed_paths: list[str], impact_map: dict[str, Any]) -> dict[str, Any]:
    result = base_result()
    result["status"] = "PASS"
    result["changed_paths"] = changed_paths
    minimum_tier = "V0"
    matched_rule_ids: set[str] = set()
    matched_paths: set[str] = set()
    additional_commands: set[str] = set()

    for rule in impact_map["rules"]:
        matches = matching_paths(changed_paths, rule, repo_root=repo_root)
        if not matches:
            continue
        matched_paths.update(matches)
        matched_rule_ids.add(rule["rule_id"])
        if TIER_RANK[rule["minimum_tier"]] > TIER_RANK[minimum_tier]:
            minimum_tier = rule["minimum_tier"]
        additional_commands.update(rule["command_ids"])
        for key in (
            "digest_check_required",
            "checksum_check_required",
            "render_check_required",
            "integration_owner_required",
        ):
            result[key] = result[key] or rule[key]

    unknown_paths = sorted(set(changed_paths) - matched_paths)
    if unknown_paths:
        minimum_tier = "V2"
        result["reason_codes"] = ["UNKNOWN_PATH_ESCALATED"]

    required_commands = set(impact_map["tier_command_ids"][minimum_tier])
    required_commands.update(additional_commands)
    if result["digest_check_required"]:
        required_commands.add("corpus_digest_check")
    if result["checksum_check_required"]:
        required_commands.add("checksum_verify")
    if result["render_check_required"]:
        required_commands.add("render_dry_runs")

    result["minimum_tier"] = minimum_tier
    result["matched_rule_ids"] = sorted(matched_rule_ids)
    result["required_command_ids"] = sorted(required_commands)
    result["not_required_command_ids"] = sorted(
        set(impact_map["command_ids"]) - required_commands
    )
    return result


def inspect_plan(
    *,
    repo_root: Path = REPO_ROOT,
    base_sha: str,
    head_sha: str | None = None,
) -> dict[str, Any]:
    result = base_result()
    if SHA_PATTERN.fullmatch(base_sha) is None:
        result["reason_codes"] = ["BASE_SHA_INVALID"]
        return result
    if head_sha is not None and SHA_PATTERN.fullmatch(head_sha) is None:
        result["reason_codes"] = ["HEAD_SHA_INVALID"]
        return result

    try:
        root = validate_repository(repo_root)
        observed_head = head_sha or run_git(root, "rev-parse", "HEAD").stdout.strip()
        if SHA_PATTERN.fullmatch(observed_head) is None:
            raise GitObservationError("HEAD_SHA_INVALID")

        resolved_base, base_issue = resolve_commit(root, base_sha, label="BASE")
        resolved_head, head_issue = resolve_commit(root, observed_head, label="HEAD")
        if base_issue or head_issue:
            result["status"] = "BLOCKED"
            result["reason_codes"] = [issue for issue in (base_issue, head_issue) if issue]
            return result
        assert resolved_base is not None and resolved_head is not None

        changed_paths, ancestry_issue = observe_changed_paths(root, resolved_base, resolved_head)
        if ancestry_issue:
            result["status"] = "BLOCKED"
            result["reason_codes"] = [ancestry_issue]
            return result
        impact_map = load_impact_map(root)
        return build_plan(root, changed_paths, impact_map)
    except GitObservationError as exc:
        result["status"] = "ENVIRONMENT BLOCKED"
        result["reason_codes"] = [str(exc)]
        return result
    except MapValidationError as exc:
        result["reason_codes"] = [str(exc)]
        return result


def json_bytes(result: dict[str, Any]) -> bytes:
    payload = (
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")
    if len(payload) > MAX_OUTPUT_BYTES:
        raise ValueError("OUTPUT_TOO_LARGE")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an advisory verification plan without executing checks."
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--base-sha", required=True, help="40-hex base commit")
    parser.add_argument("--head-sha", help="40-hex head commit; defaults to HEAD")
    parser.add_argument("--json", action="store_true", required=True, help="Emit deterministic JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = inspect_plan(
        repo_root=Path(args.repo_root),
        base_sha=args.base_sha,
        head_sha=args.head_sha,
    )
    try:
        sys.stdout.buffer.write(json_bytes(result))
    except ValueError:
        fallback = base_result()
        fallback["reason_codes"] = ["OUTPUT_TOO_LARGE"]
        sys.stdout.buffer.write(json_bytes(fallback))
        return 1
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
