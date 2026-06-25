"""Standalone dry-run Hermes preflight caller for git push.

This caller is intentionally non-executing. It asks the existing no-op Hermes
sidecar to classify a bounded git_push request, then converts that result into
a fail-closed caller decision. It never runs Git commands or writes evidence.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

try:
    from scripts import hermes_sidecar
except ModuleNotFoundError:  # pragma: no cover - direct script execution path
    import hermes_sidecar  # type: ignore[no-redef]


SCHEMA_VERSION = "hermes_git_push_preflight.v0"
DECISION_STOP = "STOP"
SIDE_EFFECT = "git_push"
GUARDED_COMMAND = "git push"

REQUIRED_HERMES_FIELDS = (
    "schema_version",
    "mode",
    "status",
    "reason_code",
    "side_effect_requested",
    "approval_ref_present",
    "safe_task_summary",
    "evidence_refs",
    "performed_actions",
    "safety_notes",
    "next_step",
)

ALLOWED_HERMES_STATUSES = {
    "BLOCKED",
    "ENVIRONMENT_BLOCKED",
    "NOT_RUN",
    "PASS_WITH_NOTES",
}


def _safe_summary(value: Any) -> str:
    if isinstance(value, str) and value:
        return value
    return "[unavailable]"


def _base_payload(hermes_result: dict[str, Any] | None = None) -> dict[str, Any]:
    hermes_result = hermes_result or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "dry_run",
        "decision": DECISION_STOP,
        "side_effect_requested": SIDE_EFFECT,
        "guarded_command": GUARDED_COMMAND,
        "would_run_git_push": False,
        "performed_actions": [],
        "safe_task_summary": _safe_summary(hermes_result.get("safe_task_summary")),
        "approval_ref_present": bool(hermes_result.get("approval_ref_present", False)),
        "checked_fields": list(REQUIRED_HERMES_FIELDS),
        "evidence_refs": [],
        "hermes_result": {
            "schema_version": hermes_result.get("schema_version"),
            "mode": hermes_result.get("mode"),
            "status": hermes_result.get("status"),
            "reason_code": hermes_result.get("reason_code"),
            "side_effect_requested": hermes_result.get("side_effect_requested"),
            "approval_ref_present": hermes_result.get("approval_ref_present"),
        },
        "safety_notes": [
            "standalone dry-run git-push preflight caller",
            "fail-closed decision only",
            "no git push, git add, git commit, git tag, workflow dispatch, artifact upload, MCP execution, audit automation, or release command was run",
            "Hermes result remains memory-only and is summarized without raw command logs",
        ],
    }


def _stop_payload(
    *,
    hermes_result: dict[str, Any] | None,
    reason_code: str,
    next_step: str,
    evidence_refs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload = _base_payload(hermes_result)
    payload.update(
        {
            "reason_code": reason_code,
            "stop_reasons": [reason_code],
            "evidence_refs": evidence_refs or [],
            "next_step": next_step,
        }
    )
    return payload


def _validated_evidence_refs(
    hermes_result: dict[str, Any],
    approved_evidence_paths: set[str],
) -> tuple[list[dict[str, Any]], str | None]:
    raw_refs = hermes_result.get("evidence_refs")
    if not isinstance(raw_refs, list):
        return [], "unexpected_evidence_shape"

    refs: list[dict[str, Any]] = []
    for item in raw_refs:
        if not isinstance(item, dict):
            return [], "unexpected_evidence_shape"
        path = item.get("path")
        exists = item.get("exists")
        if not isinstance(path, str) or exists is not True:
            return [], "unexpected_evidence_shape"
        if path not in approved_evidence_paths:
            return [], "evidence_scope_blocked"
        refs.append({"path": path, "exists": True})
    return refs, None


def interpret_hermes_result(
    hermes_result: dict[str, Any],
    *,
    approved_evidence_paths: list[str] | None = None,
) -> dict[str, Any]:
    """Convert a no-op Hermes result into a fail-closed git-push decision."""

    approved_scope = set(approved_evidence_paths or [])

    missing_fields = [field for field in REQUIRED_HERMES_FIELDS if field not in hermes_result]
    if missing_fields:
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code="unexpected_result_shape",
            next_step="Stop before git push; Hermes result is missing required fields.",
        )

    if hermes_result.get("schema_version") != hermes_sidecar.SCHEMA_VERSION:
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code="unexpected_schema_version",
            next_step="Stop before git push; update the caller contract before interpreting this schema.",
        )

    if hermes_result.get("mode") != "no_op":
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code="unexpected_mode",
            next_step="Stop before git push; only no-op Hermes results are accepted.",
        )

    status = hermes_result.get("status")
    if status not in ALLOWED_HERMES_STATUSES:
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code="unexpected_status",
            next_step="Stop before git push; update the caller contract before interpreting this status.",
        )

    if hermes_result.get("side_effect_requested") != SIDE_EFFECT:
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code="scope_conflict",
            next_step="Stop before git push; this caller only handles git_push preflight results.",
        )

    performed_actions = hermes_result.get("performed_actions")
    if performed_actions != []:
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code="contract_violation",
            next_step="Stop before git push; Hermes v0 must not report performed actions.",
        )

    evidence_refs, evidence_reason = _validated_evidence_refs(hermes_result, approved_scope)
    if evidence_reason is not None:
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code=evidence_reason,
            next_step="Stop before git push; evidence must stay inside the approved preflight scope.",
        )

    if status == "ENVIRONMENT_BLOCKED":
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code="environment_blocked",
            next_step="Stop before git push; resolve the local environment and rerun preflight.",
            evidence_refs=evidence_refs,
        )

    if status == "BLOCKED":
        hermes_reason = hermes_result.get("reason_code")
        reason = hermes_reason if isinstance(hermes_reason, str) else "hermes_blocked"
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code=reason,
            next_step="Stop before git push; satisfy the Hermes approval, safety, or evidence requirement first.",
            evidence_refs=evidence_refs,
        )

    if status == "NOT_RUN":
        return _stop_payload(
            hermes_result=hermes_result,
            reason_code="executor_not_approved",
            next_step="Stop before git push; preflight does not authorize an executor or the guarded push.",
            evidence_refs=evidence_refs,
        )

    return _stop_payload(
        hermes_result=hermes_result,
        reason_code="unexpected_advisory_result",
        next_step="Stop before git push; advisory Hermes output is not execution authority.",
        evidence_refs=evidence_refs,
    )


def run_preflight(
    *,
    task_summary: str,
    approval_ref: str | None = None,
    evidence_paths: list[str] | None = None,
) -> dict[str, Any]:
    evidence_paths = evidence_paths or []
    hermes_result = hermes_sidecar.assess_request(
        task_summary=task_summary,
        side_effect=SIDE_EFFECT,
        approval_ref=approval_ref,
        evidence_paths=evidence_paths,
    )
    return interpret_hermes_result(hermes_result, approved_evidence_paths=evidence_paths)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a dry-run Hermes git-push preflight without executing git push."
    )
    parser.add_argument("--task-summary", required=True, help="Short sanitized task summary.")
    parser.add_argument("--approval-ref", help="Approval reference for the git_push boundary.")
    parser.add_argument("--evidence-path", action="append", default=[], help="Existing safe repo-relative evidence path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout. JSON is the only output format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_preflight(
        task_summary=args.task_summary,
        approval_ref=args.approval_ref,
        evidence_paths=args.evidence_path,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
