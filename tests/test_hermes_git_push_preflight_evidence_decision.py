from __future__ import annotations

import json
from pathlib import Path

from scripts import hermes_git_push_preflight as preflight
from scripts import hermes_sidecar as sidecar


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_EVIDENCE_DECISION.md"


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


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_decision_documents_basis_and_documentation_only_scope() -> None:
    text = decision_text()
    purpose = normalize_ws(section(text, "Purpose"))
    basis = section(text, "Basis")

    for basis_path in [
        "scripts/hermes_git_push_preflight.py",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_OUTPUT_CONTRACT.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_USAGE_PROBE.md",
        "docs/HERMES_PREFLIGHT_CALLER_IMPLEMENTATION_BOUNDARY.md",
        "docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md",
        "docs/JSON_EVIDENCE_POLICY.md",
        "docs/AUDIT_TRACE_SCHEMA.md",
        "audits/receipt-summary.schema.json",
        "audits/trace-event.schema.json",
    ]:
        assert f"`{basis_path}`" in basis

    for forbidden_scope in [
        "does not change `scripts/hermes_git_push_preflight.py`",
        "change `scripts/hermes_sidecar.py`",
        "create receipt or trace schemas",
        "write receipt files",
        "write trace files",
        "run `git push`",
        "wire quality-gate or CI integration",
        "edit downstream repositories",
    ]:
        assert forbidden_scope in purpose


def test_decision_retains_stdout_only_until_consumer_is_approved() -> None:
    decision = normalize_ws(section(decision_text(), "Decision"))

    assert "`stdout_only_retained_until_receipt_trace_consumer_is_approved`" in decision
    assert "remain stdout-only for the current implementation" in decision
    assert "should not write receipt files, trace files, audit logs" in decision

    for missing_consumer in [
        "an approved receipt writer",
        "an approved trace writer",
        "an approved schema extension",
        "an approved quality-gate or CI consumer",
        "an approved audit automation flow",
        "an approved release, AgentOps, memory, MCP, or downstream consumer",
    ]:
        assert missing_consumer in decision


def test_future_receipt_trace_planning_conditions_are_explicit() -> None:
    planning = normalize_ws(section(decision_text(), "Future Receipt/Trace Planning Conditions"))

    for required_condition in [
        "the exact receipt fields",
        "the exact trace fields",
        "whether evidence captures no output, a redacted summary, selected fields, or a bounded artifact reference",
        "the allowed status and reason-code values",
        "how `receipt_id` and `related_receipt_id` are assigned or referenced",
        "whether evidence is manual-only, test-only, quality-gated, CI-gated, or runtime-generated",
        "the exact writer",
        "forbidden captured material",
        "cleanup rules",
        "verification commands",
        "Local Verify and closeout requirements",
    ]:
        assert required_condition in planning

    assert "must still not write real receipts, real trace events, audit logs" in planning


def test_evidence_boundary_is_summary_only_and_redacted() -> None:
    boundary = normalize_ws(section(decision_text(), "Evidence Boundary"))

    for allowed_summary in [
        "`schema_version`",
        "`mode`",
        "`decision`",
        "`side_effect_requested`",
        "`guarded_command`",
        "`would_run_git_push`",
        "empty `performed_actions`",
        "`reason_code`",
        "bounded `stop_reasons`",
        "bounded safe `evidence_refs`",
        "sanitized nested Hermes summary fields",
    ]:
        assert allowed_summary in boundary

    for forbidden_capture in [
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
    ]:
        assert forbidden_capture in boundary


def test_non_goals_block_runtime_schema_and_evidence_generation() -> None:
    non_goals = normalize_ws(section(decision_text(), "Non-goals"))

    for forbidden_scope in [
        "change `scripts/hermes_git_push_preflight.py`",
        "change `scripts/hermes_sidecar.py`",
        "add receipt or trace schema fields",
        "add a machine-readable Hermes preflight schema artifact",
        "write or generate receipt files, trace files, audit logs",
        "connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP",
        "run `git push`, `git add`, `git commit`, `git tag`",
        "workflow dispatch",
        "artifact upload",
        "receipt generation",
        "trace writing",
        "downstream mutation",
    ]:
        assert forbidden_scope in non_goals


def test_current_caller_output_has_no_durable_receipt_or_trace_fields(tmp_path: Path, monkeypatch) -> None:
    write(tmp_path / "STATUS.md", "# Status\n")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    payload = preflight.run_preflight(
        task_summary="Push Phase 9O evidence decision",
        approval_ref="phase-9o-owner-approval",
        evidence_paths=["STATUS.md"],
    )

    assert payload["decision"] == "STOP"
    assert payload["reason_code"] == "executor_not_approved"
    assert payload["would_run_git_push"] is False
    assert payload["performed_actions"] == []
    assert "receipt_id" not in payload
    assert "trace_event_id" not in payload
    assert "related_receipt_id" not in payload
    assert "audit_log_path" not in payload
    assert "artifact_path" not in payload

    serialized = json.dumps(payload, sort_keys=True)
    assert "ALLOW_EXECUTION" not in serialized
    assert "PROCEED" not in serialized
    assert payload["decision"] != "RUN"
