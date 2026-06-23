"""Minimal no-op Hermes sidecar v0.

This script is intentionally conservative: it classifies a bounded local
request and prints a safe JSON result. It does not execute tools, write files,
start a service, call a network, or generate artifacts.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any


SCHEMA_VERSION = "hermes_sidecar_noop.v0"
MAX_TASK_SUMMARY_LENGTH = 240
MAX_APPROVAL_REF_LENGTH = 120
MAX_EVIDENCE_PATHS = 10
MAX_EVIDENCE_PATH_LENGTH = 200

SIDE_EFFECT_NONE = "none"
SIDE_EFFECT_CHOICES = {
    SIDE_EFFECT_NONE,
    "file_write",
    "git_stage",
    "git_commit",
    "git_push",
    "artifact_generation",
    "mcp_tool_execution",
    "audit_generation",
    "external_call",
    "release_publication",
    "downstream_mutation",
    "persistent_process",
}

WINDOWS_ABSOLUTE_RE = re.compile(r"[A-Za-z]:[\\/][^\s]*")
POSIX_ABSOLUTE_RE = re.compile(r"(^|\s)/(?:Users|home|etc|var|tmp|mnt|opt|root)\b[^\s]*")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
SECRET_ASSIGNMENT_RE = re.compile(r"(?i)\b(secret|token|password|credential|api[_-]?key)\s*[:=]\s*\S+")
APPROVAL_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:#-]{0,119}$")
FORBIDDEN_TEXT_RE = re.compile(
    r"(?i)\b("
    r"raw prompt|prompt transcript|private data|raw command log|model output transcript|"
    r"tool-call body|tool call body|unredacted tool|secret|credential|password|api key|"
    r"live config|device value|account value|broker value|equipment value|"
    r"08[_ -]?study|rsid raw|downstream raw|private raw|generated downstream"
    r")\b"
)

FORBIDDEN_PATH_PARTS = {
    ".git",
    "08_study",
    "attachments",
    "credentials",
    "exports",
    "local",
    "logs",
    "private",
    "raw",
    "secrets",
}


@dataclass(frozen=True)
class EvidenceRef:
    path: str
    exists: bool


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def sanitize_summary(value: str) -> str:
    return " ".join(value.strip().split())


def unsafe_text_reason(value: str, *, field_name: str) -> str | None:
    if "\n" in value or "\r" in value:
        return f"{field_name} appears to contain multiline raw content"
    sanitized = sanitize_summary(value)
    if not sanitized:
        return f"{field_name} is empty"
    if len(sanitized) > MAX_TASK_SUMMARY_LENGTH:
        return f"{field_name} exceeds bounded summary length"
    if WINDOWS_ABSOLUTE_RE.search(sanitized) or POSIX_ABSOLUTE_RE.search(sanitized):
        return f"{field_name} contains a local absolute path"
    if IPV4_RE.search(sanitized):
        return f"{field_name} contains an IP-like value"
    if SECRET_ASSIGNMENT_RE.search(sanitized) or FORBIDDEN_TEXT_RE.search(sanitized):
        return f"{field_name} contains forbidden raw, private, live, secret, or transcript material"
    return None


def validate_approval_ref(value: str | None) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    sanitized = sanitize_summary(value)
    if not sanitized:
        return None, "approval_ref is empty"
    if len(sanitized) > MAX_APPROVAL_REF_LENGTH:
        return None, "approval_ref exceeds bounded length"
    if not APPROVAL_REF_RE.fullmatch(sanitized):
        return None, "approval_ref contains unsupported characters"
    if unsafe_text_reason(sanitized, field_name="approval_ref") is not None:
        return None, "approval_ref contains forbidden material"
    return sanitized, None


def validate_repo_relative_path(path_text: str) -> tuple[str | None, str | None]:
    if not path_text or not path_text.strip():
        return None, "evidence path is empty"
    raw = path_text.strip()
    if len(raw) > MAX_EVIDENCE_PATH_LENGTH:
        return None, "evidence path exceeds bounded length"
    if "\\" in raw:
        return None, "evidence path must use POSIX separators"
    if WINDOWS_ABSOLUTE_RE.match(raw) or raw.startswith("/") or raw.startswith("\\"):
        return None, "evidence path is absolute"
    if IPV4_RE.search(raw) or SECRET_ASSIGNMENT_RE.search(raw):
        return None, "evidence path contains forbidden material"
    parts = PurePosixPath(raw).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None, "evidence path uses dot or parent traversal"
    if any(part.lower() in FORBIDDEN_PATH_PARTS for part in parts):
        return None, "evidence path is in a forbidden private/raw/local class"
    return raw, None


def validate_evidence_paths(repo_root: Path, evidence_paths: list[str]) -> tuple[list[EvidenceRef], str | None]:
    if len(evidence_paths) > MAX_EVIDENCE_PATHS:
        return [], "too many evidence paths"
    root = repo_root.resolve()
    refs: list[EvidenceRef] = []
    for path_text in evidence_paths:
        normalized, reason = validate_repo_relative_path(path_text)
        if reason is not None or normalized is None:
            return [], reason or "evidence path is invalid"
        full_path = (root / normalized).resolve(strict=False)
        try:
            full_path.relative_to(root)
        except ValueError:
            return [], "evidence path escapes repository"
        if full_path.is_symlink():
            return [], "evidence path is a symlink"
        if not full_path.exists():
            return [], "evidence path does not exist in the repository basis"
        refs.append(EvidenceRef(path=normalized, exists=True))
    return refs, None


def base_payload(*, task_summary: str, side_effect: str, approval_ref: str | None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "no_op",
        "side_effect_requested": side_effect,
        "approval_ref_present": approval_ref is not None,
        "safe_task_summary": task_summary,
        "performed_actions": [],
        "safety_notes": [
            "local-only no-op Hermes sidecar",
            "advisory classification only",
            "no tool execution, file write, background process, network call, artifact generation, or downstream mutation",
        ],
    }


def blocked_payload(
    *,
    task_summary: str,
    side_effect: str,
    approval_ref: str | None,
    reason_code: str,
    next_step: str,
) -> dict[str, Any]:
    payload = base_payload(task_summary=task_summary, side_effect=side_effect, approval_ref=approval_ref)
    payload.update(
        {
            "status": "BLOCKED",
            "reason_code": reason_code,
            "evidence_refs": [],
            "next_step": next_step,
        }
    )
    return payload


def assess_request(
    *,
    task_summary: str,
    side_effect: str = SIDE_EFFECT_NONE,
    approval_ref: str | None = None,
    evidence_paths: list[str] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root or repo_root_from_script()
    evidence_paths = evidence_paths or []

    if side_effect not in SIDE_EFFECT_CHOICES:
        return blocked_payload(
            task_summary="[blocked unsafe input]",
            side_effect="unknown",
            approval_ref=None,
            reason_code="scope_conflict",
            next_step="Use one of the documented side-effect classes.",
        )

    summary_reason = unsafe_text_reason(task_summary, field_name="task_summary")
    if summary_reason is not None:
        return blocked_payload(
            task_summary="[blocked unsafe input]",
            side_effect=side_effect,
            approval_ref=None,
            reason_code="unsafe_input",
            next_step="Provide a short sanitized task summary without raw, private, live, secret, transcript, or local-path data.",
        )
    safe_summary = sanitize_summary(task_summary)

    safe_approval_ref, approval_reason = validate_approval_ref(approval_ref)
    if approval_reason is not None:
        return blocked_payload(
            task_summary=safe_summary,
            side_effect=side_effect,
            approval_ref=None,
            reason_code="unsafe_input",
            next_step="Use a bounded approval reference id without raw, private, live, secret, or path material.",
        )

    refs, evidence_reason = validate_evidence_paths(repo_root, evidence_paths)
    if evidence_reason is not None:
        reason_code = "source_basis_blocked" if "does not exist" in evidence_reason else "unsafe_input"
        return blocked_payload(
            task_summary=safe_summary,
            side_effect=side_effect,
            approval_ref=safe_approval_ref,
            reason_code=reason_code,
            next_step="Use existing safe repo-relative evidence paths only.",
        )

    payload = base_payload(task_summary=safe_summary, side_effect=side_effect, approval_ref=safe_approval_ref)
    payload["evidence_refs"] = [ref.__dict__ for ref in refs]

    if side_effect != SIDE_EFFECT_NONE and safe_approval_ref is None:
        payload.update(
            {
                "status": "BLOCKED",
                "reason_code": "approval_blocked",
                "next_step": "Provide explicit approval for this exact side-effect class, target, command, output, cleanup, and verification.",
            }
        )
        return payload

    if side_effect != SIDE_EFFECT_NONE:
        payload.update(
            {
                "status": "NOT_RUN",
                "reason_code": "policy_blocked",
                "next_step": "This no-op sidecar records the approved request boundary only; a separate executor task is required before any side effect can run.",
            }
        )
        return payload

    payload.update(
        {
            "status": "PASS_WITH_NOTES",
            "reason_code": "insufficient_evidence",
            "next_step": "No side effect was requested; use this advisory result as planning context only.",
        }
    )
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify a bounded Hermes sidecar request without executing side effects.")
    parser.add_argument("--task-summary", required=True, help="Short sanitized task summary.")
    parser.add_argument("--side-effect", default=SIDE_EFFECT_NONE, choices=sorted(SIDE_EFFECT_CHOICES), help="Requested side-effect class.")
    parser.add_argument("--approval-ref", help="Explicit approval reference for one side-effect class.")
    parser.add_argument("--evidence-path", action="append", default=[], help="Existing safe repo-relative evidence path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout. JSON is the only output format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = assess_request(
            task_summary=args.task_summary,
            side_effect=args.side_effect,
            approval_ref=args.approval_ref,
            evidence_paths=args.evidence_path,
        )
    except OSError:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "ENVIRONMENT_BLOCKED",
            "mode": "no_op",
            "reason_code": "environment_blocked",
            "side_effect_requested": SIDE_EFFECT_NONE,
            "approval_ref_present": False,
            "safe_task_summary": "[environment blocked]",
            "evidence_refs": [],
            "performed_actions": [],
            "safety_notes": ["local-only no-op Hermes sidecar could not inspect the repository basis"],
            "next_step": "Resolve the local environment and rerun the no-op classifier.",
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
