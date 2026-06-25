from __future__ import annotations

import json
from pathlib import Path

from scripts import hermes_git_push_preflight as preflight
from scripts import hermes_sidecar as sidecar


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_RECEIPT_TRACE_PLAN.md"


def plan_text() -> str:
    return PLAN_PATH.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_plan_documents_basis_and_planning_only_scope() -> None:
    text = plan_text()
    purpose = normalize_ws(section(text, "Purpose"))
    basis = section(text, "Basis")

    for basis_path in [
        "scripts/hermes_git_push_preflight.py",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_OUTPUT_CONTRACT.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_USAGE_PROBE.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_EVIDENCE_DECISION.md",
        "docs/JSON_EVIDENCE_POLICY.md",
        "docs/AUDIT_TRACE_SCHEMA.md",
        "audits/receipt-summary.schema.json",
        "audits/trace-event.schema.json",
    ]:
        assert f"`{basis_path}`" in basis

    for forbidden_scope in [
        "does not change `scripts/hermes_git_push_preflight.py`",
        "change `scripts/hermes_sidecar.py`",
        "modify `audits/receipt-summary.schema.json`",
        "modify `audits/trace-event.schema.json`",
        "write receipt files",
        "write trace files",
        "run `git push`",
        "wire quality-gate or CI integration",
        "edit downstream repositories",
    ]:
        assert forbidden_scope in purpose


def test_planning_decision_defers_schema_writer_and_integration() -> None:
    decision = normalize_ws(section(plan_text(), "Planning Decision"))

    assert "`receipt_trace_plan_documented_without_schema_or_writer`" in decision
    assert "must remain distinct from execution evidence" in decision
    assert "must not imply that a push was authorized, attempted, or completed" in decision
    assert "should not add receipt or trace schema fields in Phase 9P" in decision
    assert "Schema alignment, validation, writer behavior, quality-gate integration, CI integration" in decision


def test_receipt_evidence_candidate_lists_safe_selected_fields() -> None:
    receipt = section(plan_text(), "Receipt Evidence Candidate")

    for field in [
        "hermes_git_push_preflight_evidence",
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
    ]:
        assert f"`{field}`" in receipt

    assert "must not copy full preflight stdout" in receipt


def test_trace_evidence_candidate_keeps_receipt_linkage_compact() -> None:
    trace = normalize_ws(section(plan_text(), "Trace Evidence Candidate"))

    for expected in [
        "`hermes_git_push_preflight_evidence_ref`",
        "`related_receipt_id` as the receipt linkage",
        "`related_receipt_id` should point to `receipt_summary.receipt_id`",
        "`receipt_evidence_key`",
        "`hermes_git_push_preflight_evidence`",
        "Trace-level evidence is a pointer",
        "not a transcript or preflight stdout dump",
    ]:
        assert expected in trace


def test_capture_policy_blocks_raw_private_and_execution_material() -> None:
    policy = normalize_ws(section(plan_text(), "Capture Policy"))

    for allowed in [
        "bounded selected fields",
        "safe summaries",
        "repo-relative evidence references",
        "reviewed commit identifiers",
        "reviewed Local Verify run/job identifiers",
    ]:
        assert allowed in policy

    for forbidden in [
        "raw prompts",
        "private data",
        "raw command logs",
        "raw preflight stdout dumps",
        "unredacted tool-call",
        "secrets",
        "IP",
        "ports",
        "live config",
        "device values",
        "local absolute paths",
        "08_Study",
        "downstream raw evidence",
        "full approval conversation text",
    ]:
        assert forbidden in policy


def test_future_phase_split_and_non_goals_prevent_scope_collapse() -> None:
    future = normalize_ws(section(plan_text(), "Future Phase Split"))
    non_goals = normalize_ws(section(plan_text(), "Non-goals"))

    for expected in [
        "Phase 9Q schema-alignment review",
        "`audits/receipt-summary.schema.json`",
        "`audits/trace-event.schema.json`",
        "`scripts/gates/json_evidence_gate.py`",
        "Phase 9R writer or capture review",
        "Phase 9S integration review",
        "Approving Phase 9P does not approve any of those later phases",
    ]:
        assert expected in future

    for forbidden in [
        "modify `audits/receipt-summary.schema.json`",
        "modify `audits/trace-event.schema.json`",
        "write or generate receipt files, trace files, audit logs",
        "connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP",
        "run `git push`, `git add`, `git commit`, `git tag`",
        "workflow dispatch",
        "artifact upload",
        "receipt generation",
        "trace writing",
        "downstream mutation",
    ]:
        assert forbidden in non_goals


def test_current_caller_output_can_be_safely_summarized_without_receipt_fields(tmp_path: Path, monkeypatch) -> None:
    write(tmp_path / "STATUS.md", "# Status\n")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    payload = preflight.run_preflight(
        task_summary="Push Phase 9P receipt trace plan",
        approval_ref="phase-9p-owner-approval",
        evidence_paths=["STATUS.md"],
    )

    candidate_summary = {
        "caller_schema_version": payload["schema_version"],
        "caller_mode": payload["mode"],
        "decision": payload["decision"],
        "side_effect_requested": payload["side_effect_requested"],
        "guarded_command": payload["guarded_command"],
        "would_run_git_push": payload["would_run_git_push"],
        "performed_actions_empty": payload["performed_actions"] == [],
        "reason_code": payload["reason_code"],
        "stop_reasons": payload["stop_reasons"],
        "evidence_refs": payload["evidence_refs"],
        "hermes_result_summary": payload["hermes_result"],
        "output_capture": "selected_fields",
    }

    assert candidate_summary["decision"] == "STOP"
    assert candidate_summary["would_run_git_push"] is False
    assert candidate_summary["performed_actions_empty"] is True
    assert "receipt_id" not in candidate_summary
    assert "trace_event_id" not in candidate_summary
    assert "related_receipt_id" not in candidate_summary
    assert "raw_stdout" not in candidate_summary
    assert "raw_command_log" not in candidate_summary

    serialized = json.dumps(candidate_summary, sort_keys=True)
    assert "ALLOW_EXECUTION" not in serialized
    assert "PROCEED" not in serialized
    assert candidate_summary["decision"] != "RUN"
