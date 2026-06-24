from __future__ import annotations

import json
from pathlib import Path

from scripts import hermes_sidecar as sidecar


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md"

REQUIRED_FIELDS = {
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
}


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


def assert_result_contract(payload: dict[str, object]) -> None:
    assert REQUIRED_FIELDS <= payload.keys()
    assert payload["schema_version"] == sidecar.SCHEMA_VERSION
    assert payload["mode"] == "no_op"
    assert isinstance(payload["status"], str)
    assert isinstance(payload["reason_code"], str)
    assert isinstance(payload["side_effect_requested"], str)
    assert isinstance(payload["approval_ref_present"], bool)
    assert isinstance(payload["safe_task_summary"], str)
    assert isinstance(payload["evidence_refs"], list)
    assert payload["performed_actions"] == []
    assert isinstance(payload["safety_notes"], list)
    assert all(isinstance(note, str) for note in payload["safety_notes"])
    assert isinstance(payload["next_step"], str)
    json.dumps(payload, sort_keys=True)


def test_contract_documents_required_result_fields_and_values() -> None:
    text = contract_text()
    required_fields = normalize_ws(section(text, "Required Top-level Fields"))
    statuses = normalize_ws(section(text, "Status Values"))
    reason_codes = normalize_ws(section(text, "Reason Codes"))

    for field_name in sorted(REQUIRED_FIELDS):
        assert f"`{field_name}`" in required_fields

    for status in ["PASS_WITH_NOTES", "BLOCKED", "NOT_RUN", "ENVIRONMENT_BLOCKED"]:
        assert f"`{status}`" in statuses

    for reason_code in [
        "insufficient_evidence",
        "approval_blocked",
        "policy_blocked",
        "unsafe_input",
        "source_basis_blocked",
        "scope_conflict",
        "environment_blocked",
    ]:
        assert f"`{reason_code}`" in reason_codes

    assert "`hermes_sidecar_noop.v0`" in required_fields
    assert "approval_ref_present" in required_fields
    assert "not execution authority" in required_fields


def test_contract_documents_side_effects_evidence_redaction_and_evolution() -> None:
    text = contract_text()
    side_effects = normalize_ws(section(text, "Side-effect Classes"))
    evidence = normalize_ws(section(text, "Evidence Reference Shape"))
    redaction = normalize_ws(section(text, "Redaction And Non-persistence"))
    evolution = normalize_ws(section(text, "Schema Evolution Rule"))

    for side_effect in sorted(sidecar.SIDE_EFFECT_CHOICES):
        assert f"`{side_effect}`" in side_effects

    assert "must either return `BLOCKED`" in side_effects
    assert "`NOT_RUN` with an accepted approval reference" in side_effects
    assert "`path`" in evidence
    assert "`exists`" in evidence
    assert "Existing safe repo-relative path" in evidence
    assert "absolute paths" in evidence
    assert "raw prompts or prompt transcripts" in redaction
    assert "unredacted tool-call request or response bodies" in redaction
    assert "local absolute paths" in redaction
    assert "`08_Study` raw notes" in redaction
    assert "Any later change that adds required fields" in evolution
    assert "does not add this contract to `scripts/quality_gate.py`" in evolution


def test_representative_results_follow_required_contract(tmp_path: Path) -> None:
    evidence_path = tmp_path / "docs" / "EVIDENCE.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("# Evidence\n", encoding="utf-8")

    representative_payloads = [
        sidecar.assess_request(
            task_summary="Review no-op result contract",
            evidence_paths=["docs/EVIDENCE.md"],
            repo_root=tmp_path,
        ),
        sidecar.assess_request(
            task_summary="Prepare documentation edit",
            side_effect="file_write",
            repo_root=tmp_path,
        ),
        sidecar.assess_request(
            task_summary="Prepare documentation edit",
            side_effect="file_write",
            approval_ref="phase-9f-review",
            repo_root=tmp_path,
        ),
        sidecar.assess_request(
            task_summary=r"Use C:\Users\name\secret.txt token=abc123",
            repo_root=tmp_path,
        ),
        sidecar.assess_request(
            task_summary="Review missing evidence",
            evidence_paths=["docs/MISSING.md"],
            repo_root=tmp_path,
        ),
        sidecar.assess_request(
            task_summary="Review invalid side effect",
            side_effect="unknown_side_effect",
            repo_root=tmp_path,
        ),
    ]

    for payload in representative_payloads:
        assert_result_contract(payload)


def test_status_reason_and_approval_matrix_is_stable(tmp_path: Path) -> None:
    advisory = sidecar.assess_request(
        task_summary="Review no-op result contract",
        repo_root=tmp_path,
    )
    blocked = sidecar.assess_request(
        task_summary="Prepare documentation edit",
        side_effect="file_write",
        repo_root=tmp_path,
    )
    not_run = sidecar.assess_request(
        task_summary="Prepare documentation edit",
        side_effect="file_write",
        approval_ref="phase-9f-review",
        repo_root=tmp_path,
    )
    invalid = sidecar.assess_request(
        task_summary="Review invalid side effect",
        side_effect="unknown_side_effect",
        repo_root=tmp_path,
    )

    assert advisory["status"] == "PASS_WITH_NOTES"
    assert advisory["reason_code"] == "insufficient_evidence"
    assert advisory["side_effect_requested"] == "none"
    assert advisory["approval_ref_present"] is False

    assert blocked["status"] == "BLOCKED"
    assert blocked["reason_code"] == "approval_blocked"
    assert blocked["side_effect_requested"] == "file_write"
    assert blocked["approval_ref_present"] is False

    assert not_run["status"] == "NOT_RUN"
    assert not_run["reason_code"] == "policy_blocked"
    assert not_run["side_effect_requested"] == "file_write"
    assert not_run["approval_ref_present"] is True

    assert invalid["status"] == "BLOCKED"
    assert invalid["reason_code"] == "scope_conflict"
    assert invalid["side_effect_requested"] == "unknown"


def test_unsafe_input_is_not_echoed_in_result_json(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary=r"Use C:\Users\name\secret.txt token=abc123",
        repo_root=tmp_path,
    )
    encoded = json.dumps(payload, sort_keys=True)

    assert_result_contract(payload)
    assert payload["safe_task_summary"] == "[blocked unsafe input]"
    assert "C:" not in encoded
    assert "abc123" not in encoded
    assert "secret.txt" not in encoded


def test_cli_output_is_parseable_json_with_contracted_fields(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    evidence_path = tmp_path / "docs" / "EVIDENCE.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("# Evidence\n", encoding="utf-8")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    exit_code = sidecar.main(
        [
            "--task-summary",
            "Review no-op result contract",
            "--evidence-path",
            "docs/EVIDENCE.md",
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert_result_contract(payload)
    assert payload["evidence_refs"] == [{"path": "docs/EVIDENCE.md", "exists": True}]


def test_phase_9f_does_not_add_runtime_integration_paths() -> None:
    forbidden_paths = [
        REPO_ROOT / "hermes",
        REPO_ROOT / "sidecar",
        REPO_ROOT / "mcp_server",
        REPO_ROOT / "scripts" / "hermes_mcp_server.py",
        REPO_ROOT / "scripts" / "mcp_server.py",
        REPO_ROOT / ".github" / "workflows" / "hermes.yml",
        REPO_ROOT / ".github" / "workflows" / "mcp.yml",
    ]

    for forbidden_path in forbidden_paths:
        assert not forbidden_path.exists(), f"unexpected runtime path: {forbidden_path}"
