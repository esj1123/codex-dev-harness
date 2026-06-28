"""Synthetic not-run writer skeleton for Hermes git-push preflight evidence.

The Phase 9S writer accepts selected synthetic fields only and writes a bounded
temporary NOT_RUN JSON record. It never captures live preflight stdout, writes
receipt/trace/audit files, calls Git, executes MCP tools, or persists durable
evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Mapping


SCHEMA_VERSION = "hermes_git_push_preflight_writer.not_run.v0"
WRITER_CLASS = "not_run_record_only"
STATUS_NOT_RUN = "NOT_RUN"
SIDE_EFFECT_CLASS = "git_push"

ALLOWED_FIELDS = {
    "schema_version",
    "writer_class",
    "status",
    "reason_code",
    "side_effect_class",
    "decision",
    "performed_actions",
    "evidence_refs",
    "safe_summary",
    "checked_commit",
    "local_verify_run_id",
    "local_verify_job_id",
    "created_at",
}

FIXED_VALUES = {
    "schema_version": SCHEMA_VERSION,
    "writer_class": WRITER_CLASS,
    "status": STATUS_NOT_RUN,
    "side_effect_class": SIDE_EFFECT_CLASS,
    "performed_actions": [],
}

REQUIRED_SELECTED_FIELDS = {
    "reason_code",
    "decision",
    "evidence_refs",
    "safe_summary",
    "checked_commit",
    "local_verify_run_id",
    "local_verify_job_id",
    "created_at",
}

FORBIDDEN_KEYS = {
    "raw_stdout",
    "stdout",
    "stderr",
    "raw_stderr",
    "shell_transcript",
    "command_log",
    "raw_command_log",
    "approval_text",
    "approval_conversation",
    "prompt",
    "prompt_transcript",
    "tool_call_body",
    "tool_call_request",
    "tool_call_response",
    "token",
    "account_value",
    "local_absolute_path",
    "ip",
    "port",
    "endpoint",
    "live_config",
    "device_value",
    "private_data",
    "raw_08_study",
    "rsid_raw_evidence",
    "downstream_raw_evidence",
    "receipt_path",
    "trace_path",
    "audit_log_path",
    "artifact_path",
}

ALLOWED_DECISIONS = {"STOP", "not checked", "not applicable"}
ALLOWED_REASON_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
UTC_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^\d{1,20}$")
WINDOWS_ABSOLUTE_RE = re.compile(r"[A-Za-z]:[\\/][^\s]*")
POSIX_ABSOLUTE_RE = re.compile(r"(^|\s)/(?:Users|home|etc|var|tmp|mnt|opt|root)\b[^\s]*")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SECRET_ASSIGNMENT_RE = re.compile(r"(?i)\b(secret|token|password|credential|api[_-]?key)\s*[:=]\s*\S+")
FORBIDDEN_TEXT_RE = re.compile(
    r"(?i)\b("
    r"raw prompt|prompt transcript|private data|raw command log|shell transcript|"
    r"tool-call body|tool call body|unredacted tool|secret|credential|password|api key|"
    r"live config|device value|account value|broker value|equipment value|endpoint|"
    r"08[_ -]?study|rsid raw|downstream raw|private raw|generated downstream"
    r")\b"
)
SAFE_SUMMARY_MAX_LENGTH = 240
MAX_EVIDENCE_REFS = 20


class WriterValidationError(ValueError):
    """Validation failure for the synthetic not-run writer skeleton."""


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def _fail(message: str) -> None:
    raise WriterValidationError(f"FAIL: {message}")


def _sanitize_text(value: str) -> str:
    return " ".join(value.strip().split())


def _validate_safe_text(value: Any, *, field_name: str, max_length: int = SAFE_SUMMARY_MAX_LENGTH) -> str:
    if not isinstance(value, str):
        _fail(f"{field_name} must be a string")
    if "\n" in value or "\r" in value:
        _fail(f"{field_name} must not contain multiline raw content")
    sanitized = _sanitize_text(value)
    if not sanitized:
        _fail(f"{field_name} must not be empty")
    if len(sanitized) > max_length:
        _fail(f"{field_name} exceeds bounded length")
    if WINDOWS_ABSOLUTE_RE.search(sanitized) or POSIX_ABSOLUTE_RE.search(sanitized):
        _fail(f"{field_name} must not contain a local absolute path")
    if IPV4_RE.search(sanitized):
        _fail(f"{field_name} must not contain an IP-like value")
    if SECRET_ASSIGNMENT_RE.search(sanitized) or FORBIDDEN_TEXT_RE.search(sanitized):
        _fail(f"{field_name} contains forbidden raw, private, live, secret, or transcript material")
    return sanitized


def _validate_repo_relative_path(path_text: Any) -> str:
    path = _validate_safe_text(path_text, field_name="evidence_refs item", max_length=200)
    if "\\" in path:
        _fail("evidence_refs item must use POSIX separators")
    if path.startswith("/") or path.startswith("\\") or WINDOWS_ABSOLUTE_RE.match(path):
        _fail("evidence_refs item must be repo-relative")
    parts = PurePosixPath(path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        _fail("evidence_refs item must not use dot or parent traversal")
    lowered = {part.lower() for part in parts}
    if lowered & {"08_study", "local", "logs", "private", "raw", "secrets", "credentials"}:
        _fail("evidence_refs item must not point at private/raw/local evidence")
    return path


def _validate_evidence_refs(value: Any) -> list[str]:
    if not isinstance(value, list):
        _fail("evidence_refs must be a list")
    if len(value) > MAX_EVIDENCE_REFS:
        _fail("evidence_refs exceeds bounded item count")
    return [_validate_repo_relative_path(item) for item in value]


def _validate_commit(value: Any) -> str:
    text = _validate_safe_text(value, field_name="checked_commit", max_length=80)
    if text in {"not checked", "not applicable"}:
        return text
    if not COMMIT_RE.fullmatch(text):
        _fail("checked_commit must be a 40-character lowercase commit id or not checked")
    return text


def _validate_run_or_job_id(value: Any, *, field_name: str) -> str:
    text = _validate_safe_text(value, field_name=field_name, max_length=80)
    if text in {"not checked", "not applicable"}:
        return text
    if not ID_RE.fullmatch(text):
        _fail(f"{field_name} must be a decimal identifier or not checked")
    return text


def _validate_created_at(value: Any) -> str:
    text = _validate_safe_text(value, field_name="created_at", max_length=40)
    if not UTC_TIMESTAMP_RE.fullmatch(text):
        _fail("created_at must be an explicit UTC timestamp like 2026-06-28T01:23:45Z")
    return text


def _validate_no_forbidden_keys(payload: Mapping[str, Any]) -> None:
    keys = set(payload)
    forbidden = sorted(keys & FORBIDDEN_KEYS)
    if forbidden:
        _fail(f"forbidden selected-field keys present: {', '.join(forbidden)}")
    unknown = sorted(keys - ALLOWED_FIELDS)
    if unknown:
        _fail(f"unknown selected-field keys present: {', '.join(unknown)}")


def build_not_run_record(selected_fields: Mapping[str, Any]) -> dict[str, Any]:
    """Validate synthetic selected fields and return a bounded NOT_RUN record."""

    _validate_no_forbidden_keys(selected_fields)

    missing = sorted(field for field in REQUIRED_SELECTED_FIELDS if field not in selected_fields)
    if missing:
        _fail(f"missing required selected fields: {', '.join(missing)}")

    for field, expected in FIXED_VALUES.items():
        if field in selected_fields and selected_fields[field] != expected:
            _fail(f"{field} must be {expected!r}")

    decision = _validate_safe_text(selected_fields["decision"], field_name="decision", max_length=40)
    if decision not in ALLOWED_DECISIONS:
        _fail("decision must be STOP, not checked, or not applicable")

    reason_code = _validate_safe_text(selected_fields["reason_code"], field_name="reason_code", max_length=80)
    if not ALLOWED_REASON_RE.fullmatch(reason_code):
        _fail("reason_code must use lowercase safe identifier characters")

    return {
        "checked_commit": _validate_commit(selected_fields["checked_commit"]),
        "created_at": _validate_created_at(selected_fields["created_at"]),
        "decision": decision,
        "evidence_refs": _validate_evidence_refs(selected_fields["evidence_refs"]),
        "local_verify_job_id": _validate_run_or_job_id(
            selected_fields["local_verify_job_id"],
            field_name="local_verify_job_id",
        ),
        "local_verify_run_id": _validate_run_or_job_id(
            selected_fields["local_verify_run_id"],
            field_name="local_verify_run_id",
        ),
        "performed_actions": [],
        "reason_code": reason_code,
        "safe_summary": _validate_safe_text(selected_fields["safe_summary"], field_name="safe_summary"),
        "schema_version": SCHEMA_VERSION,
        "side_effect_class": SIDE_EFFECT_CLASS,
        "status": STATUS_NOT_RUN,
        "writer_class": WRITER_CLASS,
    }


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_temporary_output_path(output_path: Path, *, repo_root: Path | None = None) -> Path:
    """Ensure writer output cannot be a tracked repository artifact."""

    repo_root = (repo_root or repo_root_from_script()).resolve()
    resolved = output_path.resolve(strict=False)
    if output_path.suffix != ".json":
        _fail("temporary writer output must use .json suffix")
    if _is_relative_to(resolved, repo_root):
        _fail("temporary writer output must not be inside the repository")
    if resolved.exists():
        _fail("temporary writer output must not overwrite an existing file")
    return resolved


def write_not_run_record(
    selected_fields: Mapping[str, Any],
    output_path: Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Write a synthetic NOT_RUN JSON record to a temporary output path."""

    record = build_not_run_record(selected_fields)
    resolved = validate_temporary_output_path(output_path, repo_root=repo_root)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def cleanup_temporary_output(output_path: Path) -> str:
    """Delete temporary writer output and fail if cleanup is not proven."""

    if not output_path.exists():
        _fail("cleanup target is missing; cleanup cannot be proven")
    output_path.unlink()
    if output_path.exists():
        _fail("temporary writer output remains after cleanup")
    return "PASS"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write a synthetic Hermes git-push preflight NOT_RUN record to temporary JSON."
    )
    parser.add_argument("--fixture-json", required=True, help="Synthetic selected-field fixture JSON.")
    parser.add_argument("--output-json", required=True, help="Temporary output JSON path outside this repository.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        fixture = json.loads(Path(args.fixture_json).read_text(encoding="utf-8"))
        if not isinstance(fixture, dict):
            _fail("fixture JSON must be an object")
        write_not_run_record(fixture, Path(args.output_json))
    except (OSError, json.JSONDecodeError):
        print(
            json.dumps(
                {"status": "ENVIRONMENT BLOCKED", "reason": "fixture_unavailable_or_invalid_json"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    except WriterValidationError as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps({"status": "PASS", "writer_class": WRITER_CLASS}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
