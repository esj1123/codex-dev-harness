from __future__ import annotations

import json
from pathlib import Path

from scripts import hermes_git_push_preflight_writer as writer


REPO_ROOT = Path(__file__).resolve().parents[1]
PROPOSAL_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_DURABLE_WRITER_PROPOSAL.md"
RECEIPT_SCHEMA_PATH = REPO_ROOT / "audits" / "receipt-summary.schema.json"


def proposal_text() -> str:
    return PROPOSAL_PATH.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def receipt_evidence_properties() -> set[str]:
    schema = json.loads(RECEIPT_SCHEMA_PATH.read_text(encoding="utf-8"))
    evidence = schema["properties"]["hermes_git_push_preflight_evidence"]
    return set(evidence["properties"])


def test_proposal_documents_basis_and_proposal_only_scope() -> None:
    text = proposal_text()
    purpose = normalize_ws(section(text, "Purpose"))
    basis = section(text, "Basis")

    for basis_path in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_EVIDENCE_DECISION.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_RECEIPT_TRACE_PLAN.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_SCHEMA_ALIGNMENT_REVIEW.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_CAPTURE_BOUNDARY_REVIEW.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_IMPLEMENTATION_PLAN.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_PERSISTENCE_HOLD_DECISION.md",
        "scripts/hermes_git_push_preflight.py",
        "scripts/hermes_git_push_preflight_writer.py",
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


def test_proposal_selects_receipt_writer_without_implementation() -> None:
    decision = normalize_ws(section(proposal_text(), "Proposal Decision"))

    assert "`selected_fields_receipt_writer_proposed_without_implementation`" in decision
    assert "first future durable-writer candidate should be `selected_fields_receipt_writer`" in decision
    assert "`receipt_summary.hermes_git_push_preflight_evidence`" in decision
    assert "does not approve implementation" in decision
    assert "`selected_fields_trace_writer` remains deferred" in decision
    assert "Durable `manual_summary_only` persistence remains deferred" in decision


def test_future_implementation_scope_is_exact_and_excludes_no_touch_areas() -> None:
    scope = normalize_ws(section(proposal_text(), "Future Implementation Scope"))

    for allowed_file in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_SELECTED_RECEIPT_WRITER_IMPLEMENTATION_PLAN.md",
        "scripts/hermes_git_push_preflight_receipt_writer.py",
        "tests/test_hermes_git_push_preflight_receipt_writer.py",
    ]:
        assert f"`{allowed_file}`" in scope

    for no_touch in [
        "`STATUS.md`",
        "`ACCEPTANCE_TRACE.md`",
        "`audits/receipt-summary.schema.json`",
        "`audits/trace-event.schema.json`",
        "`scripts/gates/json_evidence_gate.py`",
        "`.github/workflows/local-verify.yml`",
        "artifacts, audits, evals, templates, profiles, examples, dependencies",
        "downstream repositories",
    ]:
        assert no_touch in scope


def test_consumer_output_and_source_policy_keep_phase_9u_non_durable() -> None:
    output = normalize_ws(section(proposal_text(), "Consumer And Output Policy"))
    source = normalize_ws(section(proposal_text(), "Source Policy"))

    for expected in [
        "only proposed durable consumer is the optional `receipt_summary.hermes_git_push_preflight_evidence` field",
        "writer output must remain temporary JSON only",
        "tests should use `tmp_path`",
        "must require an explicit `--output-json` path",
        "must not overwrite an existing file",
        "must not be written under `artifacts/`, `audits/receipts`, `audits/traces`, or any repository-internal path",
        "Tracked receipt output is not approved by Phase 9U",
    ]:
        assert expected in output

    for forbidden_source in [
        "does not approve capture from real `scripts/hermes_git_push_preflight.py` stdout",
        "synthetic selected-field fixtures",
        "raw stdout",
        "stderr",
        "shell transcripts",
        "approval text",
        "prompt text",
        "tool-call bodies",
        "local absolute paths",
        "08_Study",
        "downstream raw evidence",
    ]:
        assert forbidden_source in source


def test_selected_field_boundary_matches_receipt_schema_and_excludes_trace_fields() -> None:
    boundary = normalize_ws(section(proposal_text(), "Selected Field Boundary"))
    schema_fields = receipt_evidence_properties()

    expected_fields = {
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

    assert expected_fields <= schema_fields
    for field in expected_fields:
        assert f"`{field}`" in boundary

    for constrained_value in [
        "`preflight_output_mode`: `selected_fields`",
        "`output_capture`: `selected_fields`",
        "`performed_actions_empty`: `true`",
        "`would_run_git_push`: `false`",
        "`preflight_integration_status`: `standalone_not_quality_gate_or_ci`",
    ]:
        assert constrained_value in boundary

    for forbidden_field in [
        "`hermes_git_push_preflight_evidence_ref`",
        "`receipt_id`",
        "`related_receipt_id`",
        "`receipt_evidence_key`",
        "raw output field",
    ]:
        assert forbidden_field in boundary


def test_current_writer_remains_not_run_record_only() -> None:
    assert writer.WRITER_CLASS == "not_run_record_only"
    assert writer.STATUS_NOT_RUN == "NOT_RUN"
    assert writer.SIDE_EFFECT_CLASS == "git_push"
    assert writer.FIXED_VALUES["performed_actions"] == []
    assert "receipt_id" not in writer.ALLOWED_FIELDS
    assert "related_receipt_id" not in writer.ALLOWED_FIELDS
    assert "hermes_git_push_preflight_evidence" not in writer.ALLOWED_FIELDS
    assert "hermes_git_push_preflight_evidence_ref" not in writer.ALLOWED_FIELDS


def test_failure_modes_verification_non_goals_and_next_step_are_fail_closed() -> None:
    failure = normalize_ws(section(proposal_text(), "Failure Modes"))
    verification = normalize_ws(section(proposal_text(), "Verification Gate"))
    non_goals = normalize_ws(section(proposal_text(), "Non-goals"))
    next_step = normalize_ws(section(proposal_text(), "Next Step"))

    for status in ["`PASS`", "`PASS WITH NOTES`", "`BLOCKED`", "`FAIL`", "`NOT RUN`", "`ENVIRONMENT BLOCKED`"]:
        assert status in failure

    for required_command in [
        "python -m pytest tests/test_hermes_git_push_preflight_receipt_writer.py",
        "python -m pytest tests/test_hermes_git_push_preflight_writer.py",
        "python -m pytest tests/test_hermes_git_push_preflight.py",
        "python -m pytest tests/test_json_evidence_gate.py",
        "python -m pytest tests",
        "python scripts/quality_gate.py",
        "git diff --check",
        "git ls-files --others --exclude-standard",
    ]:
        assert required_command in verification

    for forbidden_scope in [
        "implement a durable writer",
        "change `scripts/hermes_git_push_preflight_writer.py`",
        "change receipt or trace schemas",
        "change `scripts/gates/json_evidence_gate.py`",
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

    assert "pause before any durable writer implementation" in next_step
    assert "separately approved Phase 9V" in next_step
    assert "Phase 9U does not authorize Phase 9V by itself" in next_step
