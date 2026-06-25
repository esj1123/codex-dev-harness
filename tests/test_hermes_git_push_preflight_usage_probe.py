from __future__ import annotations

import json
from pathlib import Path

from scripts import hermes_git_push_preflight as preflight
from scripts import hermes_sidecar as sidecar


REPO_ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_USAGE_PROBE.md"


def probe_text() -> str:
    return PROBE_PATH.read_text(encoding="utf-8")


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


def test_probe_documents_narrow_scope_and_forbidden_runtime_expansion() -> None:
    text = probe_text()
    scope = normalize_ws(section(text, "Scope"))

    for allowed in [
        "run the standalone caller in JSON dry-run mode",
        "review missing-approval behavior",
        "review approved-but-not-executable behavior",
        "review unsafe input blocking",
        "review invalid or missing evidence behavior",
        "review out-of-scope evidence handling through synthetic interpretation",
    ]:
        assert allowed in scope

    for forbidden in [
        "changing `scripts/hermes_git_push_preflight.py`",
        "changing `scripts/hermes_sidecar.py`",
        "running `git push`, `git add`, `git commit`, `git tag`",
        "wiring the caller into `scripts/quality_gate.py` or CI",
        "MCP runtime, MCP tool execution",
        "audit automation, real receipt generation, trace generation, or log writing",
        "external service calls",
        "AgentOps, memory runtime",
    ]:
        assert forbidden in scope


def test_probe_matrix_covers_current_fail_closed_usage_cases() -> None:
    matrix = section(probe_text(), "Probe Matrix")

    for expected in [
        "git-push request without approval reference",
        "git-push request with approval reference and existing evidence",
        "unsafe raw or local-path-like task summary",
        "missing evidence path",
        "parent traversal evidence path",
        "accepted-looking evidence outside caller-approved scope",
        "CLI invocation with JSON flag",
        "`approval_blocked`",
        "`executor_not_approved`",
        "`unsafe_input`",
        "`source_basis_blocked`",
        "`evidence_scope_blocked`",
    ]:
        assert expected in matrix


def test_probe_safety_findings_keep_caller_non_executing() -> None:
    safety = normalize_ws(section(probe_text(), "Safety Findings"))

    for invariant in [
        "decision` set to `STOP`",
        "would_run_git_push` as `false`",
        "performed_actions` as an empty list",
        "Approval references are boundary context only",
        "does not run Git commands",
        "write receipts",
        "write traces",
        "write audit logs",
        "call MCP tools",
        "call external services",
        "mutate downstream repositories",
        "Unsafe input is summarized by safe placeholder text",
    ]:
        assert invariant in safety


def test_representative_probe_outputs_remain_stop_only(tmp_path: Path, monkeypatch) -> None:
    write(tmp_path / "STATUS.md", "# Status\n")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    missing_approval = preflight.run_preflight(
        task_summary="Push Phase 9N usage probe",
        evidence_paths=["STATUS.md"],
    )
    approved_without_executor = preflight.run_preflight(
        task_summary="Push Phase 9N usage probe",
        approval_ref="phase-9n-owner-approval",
        evidence_paths=["STATUS.md"],
    )

    assert missing_approval["decision"] == "STOP"
    assert missing_approval["reason_code"] == "approval_blocked"
    assert approved_without_executor["decision"] == "STOP"
    assert approved_without_executor["reason_code"] == "executor_not_approved"

    for payload in [missing_approval, approved_without_executor]:
        assert payload["would_run_git_push"] is False
        assert payload["performed_actions"] == []
        assert payload["guarded_command"] == "git push"
        assert "ALLOW_EXECUTION" not in json.dumps(payload)


def test_probe_rejected_inputs_are_safe_and_bounded(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    unsafe = preflight.run_preflight(
        task_summary=r"Push C:\Users\name\secret.txt token=abc123",
        approval_ref="phase-9n-owner-approval",
    )
    missing = preflight.run_preflight(
        task_summary="Push Phase 9N usage probe",
        approval_ref="phase-9n-owner-approval",
        evidence_paths=["docs/MISSING.md"],
    )
    traversal = preflight.run_preflight(
        task_summary="Push Phase 9N usage probe",
        approval_ref="phase-9n-owner-approval",
        evidence_paths=["../outside.md"],
    )

    assert unsafe["decision"] == "STOP"
    assert unsafe["reason_code"] == "unsafe_input"
    assert unsafe["safe_task_summary"] == "[blocked unsafe input]"
    assert "abc123" not in json.dumps(unsafe)
    assert "C:" not in json.dumps(unsafe)
    assert missing["reason_code"] == "source_basis_blocked"
    assert traversal["reason_code"] == "unsafe_input"


def test_probe_out_of_scope_evidence_is_rejected_by_caller_interpretation() -> None:
    hermes_result = sidecar.assess_request(
        task_summary="Push Phase 9N usage probe",
        side_effect="git_push",
        approval_ref="phase-9n-owner-approval",
        evidence_paths=[],
        repo_root=REPO_ROOT,
    )
    hermes_result["evidence_refs"] = [{"path": "STATUS.md", "exists": True}]

    payload = preflight.interpret_hermes_result(
        hermes_result,
        approved_evidence_paths=["ACCEPTANCE_TRACE.md"],
    )

    assert payload["decision"] == "STOP"
    assert payload["reason_code"] == "evidence_scope_blocked"
    assert payload["evidence_refs"] == []


def test_probe_cli_emits_json_decision_record_only(tmp_path: Path, monkeypatch, capsys) -> None:
    write(tmp_path / "STATUS.md", "# Status\n")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    exit_code = preflight.main(
        [
            "--task-summary",
            "Push Phase 9N usage probe",
            "--approval-ref",
            "phase-9n-owner-approval",
            "--evidence-path",
            "STATUS.md",
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert payload["schema_version"] == preflight.SCHEMA_VERSION
    assert payload["decision"] == "STOP"
    assert payload["reason_code"] == "executor_not_approved"
    assert payload["would_run_git_push"] is False
    assert payload["performed_actions"] == []
