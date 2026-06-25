from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_SCHEMA_ALIGNMENT_REVIEW.md"
RECEIPT_SCHEMA_PATH = REPO_ROOT / "audits" / "receipt-summary.schema.json"
TRACE_SCHEMA_PATH = REPO_ROOT / "audits" / "trace-event.schema.json"


RECEIPT_FIELD = "hermes_git_push_preflight_evidence"
TRACE_FIELD = "hermes_git_push_preflight_evidence_ref"

RECEIPT_REQUIRED_FIELDS = {
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
    "output_capture",
    "preflight_integration_status",
}

RECEIPT_EXPECTED_FIELDS = RECEIPT_REQUIRED_FIELDS | {
    "hermes_result_summary",
    "safe_task_summary",
    "safety_notes",
    "observed_head_commit",
    "local_verify_run_id",
    "local_verify_job_id",
}

TRACE_REQUIRED_FIELDS = {
    "preflight_evidence_status",
    "decision",
    "reason_code",
    "side_effect_requested",
    "receipt_evidence_key",
    "summary",
}

TRACE_EXPECTED_FIELDS = TRACE_REQUIRED_FIELDS | {"observed_head_commit"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def test_schema_alignment_review_documents_scope_and_decision() -> None:
    text = doc_text()
    purpose = normalize_ws(section(text, "Purpose"))
    decision = normalize_ws(section(text, "Alignment Decision"))

    assert "`hermes_git_push_preflight_schema_aligned_without_writer`" in decision
    assert "selected-field evidence only" in decision
    assert "does not implement a writer" in purpose
    assert "create receipt or trace files" in purpose
    assert "wire quality-gate or CI integration" in purpose
    assert "edit downstream repositories" in purpose


def test_receipt_schema_adds_optional_bounded_preflight_evidence() -> None:
    schema = load_json(RECEIPT_SCHEMA_PATH)
    properties = schema["properties"]
    evidence = properties[RECEIPT_FIELD]

    assert RECEIPT_FIELD not in schema["required"]
    assert evidence["type"] == "object"
    assert evidence["additionalProperties"] is False
    assert RECEIPT_REQUIRED_FIELDS <= set(evidence["required"])
    assert RECEIPT_EXPECTED_FIELDS <= set(evidence["properties"])
    assert evidence["properties"]["decision"]["enum"] == ["STOP", "not checked", "not applicable"]
    assert "git_push" in evidence["properties"]["side_effect_requested"]["enum"]
    assert evidence["properties"]["guarded_command"]["enum"] == ["git push", "not checked", "not applicable"]
    assert evidence["properties"]["would_run_git_push"]["type"] == "boolean"
    assert evidence["properties"]["performed_actions_empty"]["type"] == "boolean"
    assert evidence["properties"]["approval_ref_present"]["type"] == "boolean"
    assert evidence["properties"]["evidence_refs"]["items"]["$ref"] == "#/$defs/repo_relative_path"
    assert evidence["properties"]["observed_head_commit"]["$ref"] == "#/$defs/commit_or_unknown"


def test_trace_schema_adds_optional_compact_preflight_reference() -> None:
    schema = load_json(TRACE_SCHEMA_PATH)
    properties = schema["properties"]
    evidence_ref = properties[TRACE_FIELD]

    assert TRACE_FIELD not in schema["required"]
    assert evidence_ref["type"] == "object"
    assert evidence_ref["additionalProperties"] is False
    assert TRACE_REQUIRED_FIELDS <= set(evidence_ref["required"])
    assert TRACE_EXPECTED_FIELDS <= set(evidence_ref["properties"])
    assert evidence_ref["properties"]["receipt_evidence_key"]["const"] == RECEIPT_FIELD
    assert evidence_ref["properties"]["observed_head_commit"]["$ref"] == "#/$defs/commit_or_unknown"
    assert "receipt_summary.receipt_id" in evidence_ref["description"]


def test_policy_blocks_raw_capture_and_runtime_expansion() -> None:
    text = normalize_ws(section(doc_text(), "Capture Policy") + section(doc_text(), "Non-goals"))

    for forbidden in [
        "raw prompts",
        "private data",
        "raw command logs",
        "raw preflight stdout dumps",
        "unredacted tool-call",
        "secrets",
        "local absolute paths",
        "full approval conversation text",
        "write or generate receipt files",
        "connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP",
        "receipt generation",
        "trace writing",
        "downstream mutation",
    ]:
        assert forbidden in text


def test_next_phase_keeps_writer_separate() -> None:
    next_step = normalize_ws(section(doc_text(), "Next Step"))

    assert "Phase 9R writer or capture review" in next_step
    assert "exact allowed files" in next_step
    assert "cleanup policy" in next_step
    assert "pause before any durable evidence writer or caller/runtime expansion" in next_step
