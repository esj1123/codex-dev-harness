"""Synthetic selected-field receipt evidence writer for Hermes git-push preflight.

The Phase 9V writer accepts selected synthetic fields only and writes the
optional receipt_summary.hermes_git_push_preflight_evidence object to temporary
JSON. It never captures live preflight stdout, writes receipt/trace/audit files,
calls Git, executes MCP tools, or persists durable evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Mapping


WRITER_CLASS = "selected_fields_receipt_writer"
RECEIPT_EVIDENCE_KEY = "hermes_git_push_preflight_evidence"

RECEIPT_EVIDENCE_FIELDS = {
    "preflight_evidence_status",
    "preflight_output_mode",
    "caller_schema_version",
    "caller_mode",
    "decision",
    "side_effect_requested",
    "guarded_command",
    "would_run_git_push",
    "performed_actions_empty",
    "reason_code",
    "stop_reasons",
    "approval_ref_present",
    "evidence_refs",
    "hermes_result_summary",
    "safe_task_summary",
    "safety_notes",
    "observed_head_commit",
    "local_verify_run_id",
    "local_verify_job_id",
    "output_capture",
    "preflight_integration_status",
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
    "model_output_transcript",
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
    "generated_downstream_source",
    "receipt_id",
    "task_id",
    "basis",
    "approval",
    "side_effect_class",
    "changed_files",
    "commands",
    "verification",
    "safety",
    "artifacts",
    "status_label",
    "unresolved_risks",
    "next_step",
    "hermes_git_push_preflight_evidence_ref",
    "trace_event_id",
    "related_receipt_id",
    "receipt_evidence_key",
    "receipt_path",
    "trace_path",
    "audit_log_path",
    "artifact_path",
}

FIXED_VALUES = {
    "preflight_output_mode": "selected_fields",
    "output_capture": "selected_fields",
    "performed_actions_empty": True,
    "would_run_git_push": False,
    "preflight_integration_status": "receipt-summary-only",
}

ALLOWED_PRELIGHT_STATUSES = {"stopped", "blocked", "not_run", "not_applicable"}
ALLOWED_CALLER_SCHEMA_VERSIONS = {"hermes_git_push_preflight.v0", "not checked", "not applicable"}
ALLOWED_CALLER_MODES = {"dry_run", "not checked", "not applicable"}
ALLOWED_DECISIONS = {"STOP", "not checked", "not applicable"}
ALLOWED_SIDE_EFFECTS = {"git_push", "none", "not checked", "not applicable"}
ALLOWED_GUARDED_COMMANDS = {"git push", "not checked", "not applicable"}

SAFE_TEXT_MAX_LENGTH = 240
MAX_LIST_ITEMS = 20
MAX_EVIDENCE_REFS = 20

SAFE_REASON_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
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


class ReceiptWriterValidationError(ValueError):
    """Validation failure for the synthetic selected receipt writer."""


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def _fail(message: str) -> None:
    raise ReceiptWriterValidationError(f"FAIL: {message}")


def _sanitize_text(value: str) -> str:
    return " ".join(value.strip().split())


def _validate_safe_text(value: Any, *, field_name: str, max_length: int = SAFE_TEXT_MAX_LENGTH) -> str:
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


def _validate_safe_text_list(value: Any, *, field_name: str) -> list[str]:
    if not isinstance(value, list):
        _fail(f"{field_name} must be a list")
    if len(value) > MAX_LIST_ITEMS:
        _fail(f"{field_name} exceeds bounded item count")
    return [_validate_safe_text(item, field_name=f"{field_name} item") for item in value]


def _validate_repo_relative_path(path_text: Any) -> str:
    path = _validate_safe_text(path_text, field_name="evidence_refs item", max_length=260)
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


def _validate_enum(value: Any, *, field_name: str, allowed: set[str]) -> str:
    text = _validate_safe_text(value, field_name=field_name, max_length=120)
    if text not in allowed:
        _fail(f"{field_name} has an unsupported value")
    return text


def _validate_fixed_value(payload: Mapping[str, Any], field_name: str, expected: Any) -> Any:
    value = payload[field_name]
    if isinstance(expected, bool) and not isinstance(value, bool):
        _fail(f"{field_name} must be a boolean")
    if value != expected:
        _fail(f"{field_name} must be {expected!r}")
    return value


def _validate_boolean(value: Any, *, field_name: str) -> bool:
    if not isinstance(value, bool):
        _fail(f"{field_name} must be a boolean")
    return value


def _validate_reason_code(value: Any) -> str:
    text = _validate_safe_text(value, field_name="reason_code", max_length=80)
    if not SAFE_REASON_RE.fullmatch(text):
        _fail("reason_code must use lowercase safe identifier characters")
    return text


def _validate_commit(value: Any) -> str:
    text = _validate_safe_text(value, field_name="observed_head_commit", max_length=80)
    if text in {"unknown", "not checked", "not applicable"}:
        return text
    if not COMMIT_RE.fullmatch(text):
        _fail("observed_head_commit must be a lowercase commit id or known placeholder")
    return text


def _validate_run_or_job_id(value: Any, *, field_name: str) -> str:
    text = _validate_safe_text(value, field_name=field_name, max_length=80)
    if text in {"not checked", "not applicable"}:
        return text
    if not ID_RE.fullmatch(text):
        _fail(f"{field_name} must be a decimal identifier or not checked")
    return text


def _validate_no_forbidden_keys(payload: Mapping[str, Any]) -> None:
    keys = set(payload)
    forbidden = sorted(keys & FORBIDDEN_KEYS)
    if forbidden:
        _fail(f"forbidden selected-field keys present: {', '.join(forbidden)}")
    unknown = sorted(keys - RECEIPT_EVIDENCE_FIELDS)
    if unknown:
        _fail(f"unknown selected-field keys present: {', '.join(unknown)}")


def build_receipt_evidence(selected_fields: Mapping[str, Any]) -> dict[str, Any]:
    """Validate synthetic selected fields and return a receipt evidence object."""

    _validate_no_forbidden_keys(selected_fields)

    missing = sorted(field for field in RECEIPT_EVIDENCE_FIELDS if field not in selected_fields)
    if missing:
        _fail(f"missing required selected fields: {', '.join(missing)}")

    return {
        "approval_ref_present": _validate_boolean(
            selected_fields["approval_ref_present"],
            field_name="approval_ref_present",
        ),
        "caller_mode": _validate_enum(
            selected_fields["caller_mode"],
            field_name="caller_mode",
            allowed=ALLOWED_CALLER_MODES,
        ),
        "caller_schema_version": _validate_enum(
            selected_fields["caller_schema_version"],
            field_name="caller_schema_version",
            allowed=ALLOWED_CALLER_SCHEMA_VERSIONS,
        ),
        "decision": _validate_enum(selected_fields["decision"], field_name="decision", allowed=ALLOWED_DECISIONS),
        "evidence_refs": _validate_evidence_refs(selected_fields["evidence_refs"]),
        "guarded_command": _validate_enum(
            selected_fields["guarded_command"],
            field_name="guarded_command",
            allowed=ALLOWED_GUARDED_COMMANDS,
        ),
        "hermes_result_summary": _validate_safe_text(
            selected_fields["hermes_result_summary"],
            field_name="hermes_result_summary",
        ),
        "local_verify_job_id": _validate_run_or_job_id(
            selected_fields["local_verify_job_id"],
            field_name="local_verify_job_id",
        ),
        "local_verify_run_id": _validate_run_or_job_id(
            selected_fields["local_verify_run_id"],
            field_name="local_verify_run_id",
        ),
        "observed_head_commit": _validate_commit(selected_fields["observed_head_commit"]),
        "output_capture": _validate_fixed_value(selected_fields, "output_capture", "selected_fields"),
        "performed_actions_empty": _validate_fixed_value(selected_fields, "performed_actions_empty", True),
        "preflight_evidence_status": _validate_enum(
            selected_fields["preflight_evidence_status"],
            field_name="preflight_evidence_status",
            allowed=ALLOWED_PRELIGHT_STATUSES,
        ),
        "preflight_integration_status": _validate_fixed_value(
            selected_fields,
            "preflight_integration_status",
            "receipt-summary-only",
        ),
        "preflight_output_mode": _validate_fixed_value(
            selected_fields,
            "preflight_output_mode",
            "selected_fields",
        ),
        "reason_code": _validate_reason_code(selected_fields["reason_code"]),
        "safe_task_summary": _validate_safe_text(
            selected_fields["safe_task_summary"],
            field_name="safe_task_summary",
        ),
        "safety_notes": _validate_safe_text_list(selected_fields["safety_notes"], field_name="safety_notes"),
        "side_effect_requested": _validate_enum(
            selected_fields["side_effect_requested"],
            field_name="side_effect_requested",
            allowed=ALLOWED_SIDE_EFFECTS,
        ),
        "stop_reasons": _validate_safe_text_list(selected_fields["stop_reasons"], field_name="stop_reasons"),
        "would_run_git_push": _validate_fixed_value(selected_fields, "would_run_git_push", False),
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
        _fail("temporary receipt writer output must use .json suffix")
    if _is_relative_to(resolved, repo_root):
        _fail("temporary receipt writer output must not be inside the repository")
    if resolved.exists():
        _fail("temporary receipt writer output must not overwrite an existing file")
    return resolved


def write_receipt_evidence(
    selected_fields: Mapping[str, Any],
    output_path: Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Write a synthetic receipt evidence object to a temporary output path."""

    record = build_receipt_evidence(selected_fields)
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
        _fail("temporary receipt writer output remains after cleanup")
    return "PASS"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write synthetic Hermes git-push preflight receipt evidence to temporary JSON."
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
        write_receipt_evidence(fixture, Path(args.output_json))
    except (OSError, json.JSONDecodeError):
        print(
            json.dumps(
                {"status": "ENVIRONMENT BLOCKED", "reason": "fixture_unavailable_or_invalid_json"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    except ReceiptWriterValidationError as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps({"status": "PASS", "writer_class": WRITER_CLASS}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
