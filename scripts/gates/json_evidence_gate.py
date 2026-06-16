"""JSON evidence core bundle gate.

This gate validates only the policy and schema bundle for Phase 4B. It does
not validate generated receipts, write audit logs, or create artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


BUNDLE_PATHS = [
    "docs/JSON_EVIDENCE_POLICY.md",
    "audits/receipt-summary.schema.json",
    "audits/trace-event.schema.json",
]

MARKER_PATHS = [
    "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
    "STATUS.md",
]

MARKERS = [
    "json evidence core",
    "phase 4b",
]

POLICY_REQUIRED_PHRASES = [
    "Phase 4B JSON Evidence Core",
    "Evidence Serialization Policy",
    "repo-relative paths",
    "safe summaries",
    "hashes",
    "no audit automation",
    "no real audit logs",
    "no raw prompts",
    "no private data",
    "no raw command logs",
    "no unredacted tool-call bodies",
    "no local absolute paths",
]

STATUS_LABELS = {
    "PASS",
    "PASS WITH NOTES",
    "BLOCKED",
    "NOT RUN",
    "ENVIRONMENT BLOCKED",
    "FAIL",
}

SENSITIVE_VALUE_PATTERNS = [
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\b[A-Za-z]:[\\/][^\s`'\"]+"),
]


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def has_phase_marker(repo_root: Path) -> bool:
    for relative in MARKER_PATHS:
        path = repo_root / relative
        if not path.is_file():
            continue
        text = read_text(path).lower()
        if any(marker in text for marker in MARKERS):
            return True
    return False


def load_json(path: Path, repo_root: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"{path.relative_to(repo_root)} invalid JSON: {exc}"
    if not isinstance(loaded, dict):
        return None, f"{path.relative_to(repo_root)} must contain a JSON object"
    return loaded, None


def check_no_sensitive_values(repo_root: Path, relative_paths: list[str]) -> list[str]:
    findings: list[str] = []
    for relative in relative_paths:
        path = repo_root / relative
        if not path.is_file():
            continue
        text = read_text(path)
        for pattern in SENSITIVE_VALUE_PATTERNS:
            if pattern.search(text):
                findings.append(f"{relative} contains a forbidden sensitive value pattern")
    return findings


def check_policy(repo_root: Path) -> list[str]:
    policy_path = repo_root / "docs/JSON_EVIDENCE_POLICY.md"
    text = read_text(policy_path)
    lower_text = text.lower()
    findings = [
        f"docs/JSON_EVIDENCE_POLICY.md missing required phrase: {phrase}"
        for phrase in POLICY_REQUIRED_PHRASES
        if phrase.lower() not in lower_text
    ]
    return findings


def require_top_level_schema(schema: dict[str, Any], relative: str) -> list[str]:
    findings: list[str] = []
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        findings.append(f"{relative} must use JSON Schema draft 2020-12")
    if schema.get("type") != "object":
        findings.append(f"{relative} top-level type must be object")
    if schema.get("additionalProperties") is not False:
        findings.append(f"{relative} must set additionalProperties to false")
    if not isinstance(schema.get("properties"), dict):
        findings.append(f"{relative} must define top-level properties")
    if not isinstance(schema.get("required"), list):
        findings.append(f"{relative} must define top-level required fields")
    if not isinstance(schema.get("$defs"), dict):
        findings.append(f"{relative} must define $defs")
    return findings


def require_fields(schema: dict[str, Any], relative: str, required_fields: set[str]) -> list[str]:
    schema_required = set(schema.get("required", []))
    properties = set(schema.get("properties", {}).keys())
    missing_required = sorted(required_fields - schema_required)
    missing_properties = sorted(required_fields - properties)

    findings = [f"{relative} missing required field: {field}" for field in missing_required]
    findings.extend(f"{relative} missing property for required field: {field}" for field in missing_properties)
    return findings


def require_status_enum(schema: dict[str, Any], relative: str) -> list[str]:
    defs = schema.get("$defs", {})
    status_def = defs.get("status_label", {})
    enum_values = set(status_def.get("enum", []))
    missing = sorted(STATUS_LABELS - enum_values)
    if missing:
        return [f"{relative} status_label enum missing: {', '.join(missing)}"]
    return []


def require_redaction_status(schema: dict[str, Any], relative: str) -> list[str]:
    defs = schema.get("$defs", {})
    redaction = defs.get("redaction_status", {})
    required = set(redaction.get("required", []))
    if {"status", "notes"} <= required:
        return []
    return [f"{relative} redaction_status must require status and notes"]


def check_receipt_schema(schema: dict[str, Any]) -> list[str]:
    relative = "audits/receipt-summary.schema.json"
    required_fields = {
        "schema_version",
        "evidence_kind",
        "receipt_id",
        "task_id",
        "repository",
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
    }
    findings = require_top_level_schema(schema, relative)
    findings.extend(require_fields(schema, relative, required_fields))
    findings.extend(require_status_enum(schema, relative))
    findings.extend(require_redaction_status(schema, relative))
    evidence_kind = schema.get("properties", {}).get("evidence_kind", {})
    if evidence_kind.get("const") != "receipt_summary":
        findings.append(f"{relative} evidence_kind must be receipt_summary")
    return findings


def check_trace_schema(schema: dict[str, Any]) -> list[str]:
    relative = "audits/trace-event.schema.json"
    required_fields = {
        "schema_version",
        "evidence_kind",
        "event_id",
        "task_id",
        "sequence",
        "event_type",
        "event_summary",
        "status_label",
        "redaction_status",
        "payload_capture",
    }
    findings = require_top_level_schema(schema, relative)
    findings.extend(require_fields(schema, relative, required_fields))
    findings.extend(require_status_enum(schema, relative))
    findings.extend(require_redaction_status(schema, relative))
    evidence_kind = schema.get("properties", {}).get("evidence_kind", {})
    if evidence_kind.get("const") != "trace_event":
        findings.append(f"{relative} evidence_kind must be trace_event")
    payload_capture = schema.get("properties", {}).get("payload_capture", {})
    enum_values = set(payload_capture.get("enum", []))
    if not {"none", "redacted_summary_only"} <= enum_values:
        findings.append(f"{relative} payload_capture must allow none and redacted_summary_only")
    return findings


def run(repo_root: Path) -> GateResult:
    marker_present = has_phase_marker(repo_root)
    present_paths = [relative for relative in BUNDLE_PATHS if (repo_root / relative).is_file()]
    missing_paths = [relative for relative in BUNDLE_PATHS if relative not in present_paths]

    if not present_paths and not marker_present:
        return GateResult(
            "json_evidence_gate",
            True,
            ["JSON evidence bundle not applicable: no Phase 4B marker or bundle files present"],
        )

    if not present_paths and marker_present:
        return GateResult(
            "json_evidence_gate",
            False,
            [f"Phase 4B marker present but missing JSON evidence bundle file: {path}" for path in missing_paths],
        )

    if missing_paths:
        return GateResult(
            "json_evidence_gate",
            False,
            [f"incomplete JSON evidence bundle; missing: {path}" for path in missing_paths],
        )

    findings: list[str] = []
    findings.extend(check_no_sensitive_values(repo_root, BUNDLE_PATHS))
    findings.extend(check_policy(repo_root))

    receipt_schema, receipt_error = load_json(repo_root / "audits/receipt-summary.schema.json", repo_root)
    trace_schema, trace_error = load_json(repo_root / "audits/trace-event.schema.json", repo_root)
    for error in [receipt_error, trace_error]:
        if error:
            findings.append(error)

    if receipt_schema is not None:
        findings.extend(check_receipt_schema(receipt_schema))
    if trace_schema is not None:
        findings.extend(check_trace_schema(trace_schema))

    if findings:
        return GateResult("json_evidence_gate", False, findings)

    return GateResult(
        "json_evidence_gate",
        True,
        ["JSON evidence policy and core schemas validated"],
    )
