from __future__ import annotations

import json
from pathlib import Path

from scripts import hermes_git_push_preflight as preflight
from scripts import hermes_sidecar as sidecar


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_OUTPUT_CONTRACT.md"


def contract_text() -> str:
    return CONTRACT_PATH.read_text(encoding="utf-8")


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


def test_contract_documents_basis_and_documentation_only_scope() -> None:
    text = contract_text()
    purpose = normalize_ws(section(text, "Purpose"))
    basis = section(text, "Basis")

    for basis_path in [
        "scripts/hermes_git_push_preflight.py",
        "tests/test_hermes_git_push_preflight.py",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_CALLER_SELECTION_REVIEW.md",
        "docs/HERMES_PREFLIGHT_CALLER_IMPLEMENTATION_BOUNDARY.md",
        "docs/HERMES_PREFLIGHT_USE_PLANNING_CONTRACT.md",
        "docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md",
        "scripts/hermes_sidecar.py",
    ]:
        assert f"`{basis_path}`" in basis

    for forbidden_scope in [
        "does not change `scripts/hermes_git_push_preflight.py`",
        "change `scripts/hermes_sidecar.py`",
        "run `git push`",
        "wire quality-gate or CI integration",
        "edit downstream repositories",
    ]:
        assert forbidden_scope in purpose


def test_contract_lists_required_output_fields_and_stop_only_decision() -> None:
    text = contract_text()
    fields = section(text, "Required Top-level Fields")
    decisions = normalize_ws(section(text, "Caller Decision Values"))

    for field in [
        "schema_version",
        "mode",
        "decision",
        "side_effect_requested",
        "guarded_command",
        "would_run_git_push",
        "performed_actions",
        "safe_task_summary",
        "approval_ref_present",
        "checked_fields",
        "evidence_refs",
        "hermes_result",
        "safety_notes",
        "reason_code",
        "stop_reasons",
        "next_step",
    ]:
        assert f"`{field}`" in fields

    assert "Must be `hermes_git_push_preflight.v0`" in fields
    assert "Must be `dry_run`" in fields
    assert "Must be `STOP`" in fields
    assert "Must be `false`" in fields
    assert "`STOP`" in decisions
    assert "does not define `ALLOW_EXECUTION`, `PROCEED`, or `RUN`" in decisions


def test_contract_reason_codes_match_current_fail_closed_surface() -> None:
    text = contract_text()
    reason_codes = section(text, "Reason Codes")

    for reason_code in [
        "approval_blocked",
        "executor_not_approved",
        "unsafe_input",
        "source_basis_blocked",
        "unexpected_result_shape",
        "unexpected_schema_version",
        "unexpected_mode",
        "unexpected_status",
        "scope_conflict",
        "contract_violation",
        "unexpected_evidence_shape",
        "evidence_scope_blocked",
        "environment_blocked",
        "unexpected_advisory_result",
    ]:
        assert f"`{reason_code}`" in reason_codes

    assert "must remain fail-closed" in reason_codes
    assert "must not trigger fallback behavior" in reason_codes


def test_contract_redaction_non_persistence_and_non_goals_are_explicit() -> None:
    text = contract_text()
    hermes_summary = normalize_ws(section(text, "Nested Hermes Result Summary"))
    persistence = normalize_ws(section(text, "Non-persistence And Redaction"))
    non_goals = normalize_ws(section(text, "Non-goals"))

    for field in [
        "schema_version",
        "mode",
        "status",
        "reason_code",
        "side_effect_requested",
        "approval_ref_present",
    ]:
        assert f"`{field}`" in hermes_summary

    for forbidden_data in [
        "raw prompts",
        "private data",
        "raw command logs",
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
        assert forbidden_data in persistence or forbidden_data in hermes_summary

    for forbidden_scope in [
        "add a machine-readable JSON Schema artifact",
        "connect Hermes to `scripts/quality_gate.py`, CI, MCP",
        "run `git push`, `git add`, `git commit`, `git tag`",
        "workflow dispatch",
        "artifact upload",
        "MCP execution",
        "audit generation",
        "receipt generation",
        "trace writing",
        "downstream mutation",
        "generate or regenerate artifacts, digests",
    ]:
        assert forbidden_scope in non_goals


def test_representative_caller_output_matches_contract(tmp_path: Path, monkeypatch) -> None:
    write(tmp_path / "STATUS.md", "# Status\n")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    payload = preflight.run_preflight(
        task_summary="Push Phase 9M closeout",
        approval_ref="phase-9m-owner-approval",
        evidence_paths=["STATUS.md"],
    )

    required_fields = {
        "schema_version",
        "mode",
        "decision",
        "side_effect_requested",
        "guarded_command",
        "would_run_git_push",
        "performed_actions",
        "safe_task_summary",
        "approval_ref_present",
        "checked_fields",
        "evidence_refs",
        "hermes_result",
        "safety_notes",
        "reason_code",
        "stop_reasons",
        "next_step",
    }
    assert required_fields <= payload.keys()
    assert payload["schema_version"] == "hermes_git_push_preflight.v0"
    assert payload["mode"] == "dry_run"
    assert payload["decision"] == "STOP"
    assert payload["side_effect_requested"] == "git_push"
    assert payload["guarded_command"] == "git push"
    assert payload["would_run_git_push"] is False
    assert payload["performed_actions"] == []
    assert payload["reason_code"] == "executor_not_approved"
    assert payload["stop_reasons"] == ["executor_not_approved"]
    assert payload["evidence_refs"] == [{"path": "STATUS.md", "exists": True}]

    hermes_result = payload["hermes_result"]
    assert set(hermes_result) == {
        "schema_version",
        "mode",
        "status",
        "reason_code",
        "side_effect_requested",
        "approval_ref_present",
    }
    assert hermes_result["schema_version"] == sidecar.SCHEMA_VERSION
    assert hermes_result["mode"] == "no_op"
    assert hermes_result["status"] == "NOT_RUN"


def test_output_does_not_echo_forbidden_sensitive_input(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    payload = preflight.run_preflight(
        task_summary=r"Push C:\Users\name\private.txt token=abc123",
        approval_ref="phase-9m-owner-approval",
    )
    text = json.dumps(payload, sort_keys=True)

    assert payload["decision"] == "STOP"
    assert payload["reason_code"] == "unsafe_input"
    assert payload["safe_task_summary"] == "[blocked unsafe input]"
    assert "C:" not in text
    assert "abc123" not in text
