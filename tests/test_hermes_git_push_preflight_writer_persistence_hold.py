from __future__ import annotations

import json
from pathlib import Path

from scripts import hermes_git_push_preflight_writer as writer


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_WRITER_PERSISTENCE_HOLD_DECISION.md"


def decision_text() -> str:
    return DECISION_PATH.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def selected_fixture() -> dict[str, object]:
    return {
        "reason_code": "persistence_hold",
        "decision": "STOP",
        "evidence_refs": ["docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_IMPLEMENTATION_PLAN.md"],
        "safe_summary": "Phase 9T keeps the writer synthetic-only until a durable consumer is approved.",
        "checked_commit": "f19d3bd20e4f926b6e0e13a1336c19a04503dbc9",
        "local_verify_run_id": "28494811674",
        "local_verify_job_id": "84458787551",
        "created_at": "2026-07-01T05:04:50Z",
    }


def test_decision_documents_basis_and_documentation_only_scope() -> None:
    text = decision_text()
    purpose = normalize_ws(section(text, "Purpose"))
    basis = section(text, "Basis")

    for basis_path in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_EVIDENCE_DECISION.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_RECEIPT_TRACE_PLAN.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_SCHEMA_ALIGNMENT_REVIEW.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_CAPTURE_BOUNDARY_REVIEW.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_IMPLEMENTATION_PLAN.md",
        "scripts/hermes_git_push_preflight_writer.py",
        "tests/test_hermes_git_push_preflight_writer.py",
        "docs/JSON_EVIDENCE_POLICY.md",
        "audits/receipt-summary.schema.json",
        "audits/trace-event.schema.json",
    ]:
        assert f"`{basis_path}`" in basis

    for forbidden_scope in [
        "does not change `scripts/hermes_git_push_preflight_writer.py`",
        "implement `selected_fields_receipt_writer`",
        "implement `selected_fields_trace_writer`",
        "implement durable `manual_summary_only` persistence",
        "change receipt or trace schemas",
        "write receipt files",
        "write trace files",
        "persist preflight output",
        "run `git push` through Hermes",
        "wire quality-gate or CI integration",
        "edit downstream repositories",
    ]:
        assert forbidden_scope in purpose


def test_decision_holds_durable_persistence_until_consumer_is_approved() -> None:
    decision = normalize_ws(section(decision_text(), "Decision"))

    assert "`writer_persistence_hold_until_durable_consumer_is_approved`" in decision
    assert "remain a synthetic-only `not_run_record_only` skeleton" in decision
    assert "temporary JSON outside the repository for tests" in decision

    for forbidden_promotion in [
        "durable receipt writer",
        "trace writer",
        "manual summary persistence mechanism",
        "audit log writer",
        "artifact writer",
        "quality-gate producer",
        "CI producer",
        "MCP runtime",
        "release automation producer",
    ]:
        assert forbidden_promotion in decision

    assert "It is not a receipt, trace event, audit log" in decision
    assert "proof that a git push was attempted or completed through Hermes" in decision


def test_persistence_hold_conditions_require_exact_future_approval() -> None:
    hold = normalize_ws(section(decision_text(), "Persistence Hold Conditions"))

    for required_condition in [
        "the approved writer class",
        "the exact receipt or trace consumer",
        "the exact allowed output path or paths",
        "whether output is temporary, tracked, or externally consumed",
        "whether existing files may be overwritten",
        "the exact selected field source and fixture policy",
        "how `receipt_id`, `related_receipt_id`, and `receipt_evidence_key` are assigned or referenced",
        "how reviewed commit identifiers and Local Verify run/job identifiers are selected",
        "the cleanup policy for every temporary file",
        "the redaction checks before persistence",
        "the verification commands and Local Verify closeout requirements",
    ]:
        assert required_condition in hold

    assert "If any of these are absent, the durable writer must not run." in hold


def test_allowed_interim_work_keeps_outputs_temporary_and_untracked() -> None:
    interim = normalize_ws(section(decision_text(), "Allowed Interim Work"))

    for allowed in [
        "documentation-only boundary review",
        "focused synthetic tests",
        "temporary `tmp_path` output during tests",
        "cleanup-proven temporary output deletion",
        "read-only review of Local Verify evidence",
        "local verification commands",
    ]:
        assert allowed in interim

    for forbidden in [
        "tracked receipt files",
        "trace events",
        "audit logs",
        "artifact outputs",
        "generated evidence folders",
        "quality-gate or CI integration",
    ]:
        assert forbidden in interim


def test_capture_boundary_matches_current_not_run_writer_contract() -> None:
    capture = normalize_ws(section(decision_text(), "Capture Boundary"))

    assert writer.WRITER_CLASS == "not_run_record_only"
    assert writer.STATUS_NOT_RUN == "NOT_RUN"
    assert writer.SIDE_EFFECT_CLASS == "git_push"
    assert writer.FIXED_VALUES["performed_actions"] == []

    for field in writer.ALLOWED_FIELDS:
        assert f"`{field}`" in capture

    for forbidden_key in [
        "receipt_path",
        "trace_path",
        "audit_log_path",
        "artifact_path",
        "raw_stdout",
        "raw_command_log",
        "prompt",
        "approval_text",
        "tool_call_body",
        "local_absolute_path",
        "private_data",
        "downstream_raw_evidence",
    ]:
        assert forbidden_key in writer.FORBIDDEN_KEYS

    record = writer.build_not_run_record(selected_fixture())
    assert record["writer_class"] == "not_run_record_only"
    assert record["status"] == "NOT_RUN"
    assert record["performed_actions"] == []
    assert "receipt_id" not in record
    assert "trace_event_id" not in record
    assert "related_receipt_id" not in record
    assert "artifact_path" not in record

    serialized = json.dumps(record, sort_keys=True)
    assert "ALLOW_EXECUTION" not in serialized
    assert "PROCEED" not in serialized


def test_non_goals_block_runtime_schema_and_durable_writer_expansion() -> None:
    non_goals = normalize_ws(section(decision_text(), "Non-goals"))

    for forbidden_scope in [
        "change `scripts/hermes_git_push_preflight_writer.py`",
        "change `scripts/hermes_git_push_preflight.py`",
        "change `scripts/hermes_sidecar.py`",
        "change receipt or trace schemas",
        "change `scripts/gates/json_evidence_gate.py`",
        "implement `selected_fields_receipt_writer`",
        "implement `selected_fields_trace_writer`",
        "implement durable `manual_summary_only` persistence",
        "write or generate receipt files, trace files, audit logs",
        "connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP",
        "run real `git push`, `git add`, `git commit`, `git tag`",
        "workflow dispatch",
        "artifact upload",
        "receipt generation",
        "trace writing",
        "downstream mutation through Hermes",
    ]:
        assert forbidden_scope in non_goals
