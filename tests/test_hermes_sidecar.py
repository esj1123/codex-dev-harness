from __future__ import annotations

import ast
import json
from pathlib import Path

from scripts import hermes_sidecar as sidecar


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_no_side_effect_request_returns_advisory_no_op(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "EVIDENCE.md", "# Evidence\n")

    payload = sidecar.assess_request(
        task_summary="Review Phase 9D boundary",
        evidence_paths=["docs/EVIDENCE.md"],
        repo_root=tmp_path,
    )

    assert payload["status"] == "PASS_WITH_NOTES"
    assert payload["mode"] == "no_op"
    assert payload["reason_code"] == "insufficient_evidence"
    assert payload["performed_actions"] == []
    assert payload["evidence_refs"] == [{"path": "docs/EVIDENCE.md", "exists": True}]
    assert "no tool execution" in " ".join(payload["safety_notes"])


def test_side_effect_without_approval_is_blocked(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary="Prepare a documentation edit",
        side_effect="file_write",
        repo_root=tmp_path,
    )

    assert payload["status"] == "BLOCKED"
    assert payload["reason_code"] == "approval_blocked"
    assert payload["performed_actions"] == []
    assert payload["approval_ref_present"] is False


def test_side_effect_with_approval_remains_not_run_in_noop_runtime(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary="Prepare a documentation edit",
        side_effect="file_write",
        approval_ref="owner-approved-phase-9d",
        repo_root=tmp_path,
    )

    assert payload["status"] == "NOT_RUN"
    assert payload["reason_code"] == "policy_blocked"
    assert payload["performed_actions"] == []
    assert payload["approval_ref_present"] is True
    assert "separate executor task" in payload["next_step"]


def test_unsafe_task_summary_is_blocked_without_echoing_sensitive_text(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary=r"Use C:\Users\name\secret.txt token=abc123",
        repo_root=tmp_path,
    )
    text = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "BLOCKED"
    assert payload["reason_code"] == "unsafe_input"
    assert payload["safe_task_summary"] == "[blocked unsafe input]"
    assert "C:" not in text
    assert "abc123" not in text


def test_invalid_or_missing_evidence_paths_fail_closed(tmp_path: Path) -> None:
    invalid = sidecar.assess_request(
        task_summary="Review evidence",
        evidence_paths=["../outside.md"],
        repo_root=tmp_path,
    )
    missing = sidecar.assess_request(
        task_summary="Review evidence",
        evidence_paths=["docs/MISSING.md"],
        repo_root=tmp_path,
    )

    assert invalid["status"] == "BLOCKED"
    assert invalid["reason_code"] == "unsafe_input"
    assert missing["status"] == "BLOCKED"
    assert missing["reason_code"] == "source_basis_blocked"


def test_cli_emits_json_stdout_only(tmp_path: Path, monkeypatch, capsys) -> None:
    write(tmp_path / "docs" / "EVIDENCE.md", "# Evidence\n")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    exit_code = sidecar.main(
        [
            "--task-summary",
            "Review Phase 9D",
            "--evidence-path",
            "docs/EVIDENCE.md",
            "--json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert payload["schema_version"] == sidecar.SCHEMA_VERSION
    assert payload["status"] == "PASS_WITH_NOTES"


def test_script_uses_standard_library_only_and_no_background_runtime_imports() -> None:
    source = Path(sidecar.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )

    assert imports <= {"__future__", "argparse", "dataclasses", "json", "pathlib", "re", "typing"}
    for forbidden_runtime_import in ["subprocess", "socket", "http", "threading", "asyncio"]:
        assert forbidden_runtime_import not in imports
