from __future__ import annotations

import ast
import json
from pathlib import Path

from scripts import hermes_git_push_preflight as preflight
from scripts import hermes_sidecar as sidecar


REPO_ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_missing_approval_stops_without_running_git_push(tmp_path: Path, monkeypatch) -> None:
    write(tmp_path / "docs" / "EVIDENCE.md", "# Evidence\n")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    payload = preflight.run_preflight(
        task_summary="Push Phase 9L branch",
        evidence_paths=["docs/EVIDENCE.md"],
    )

    assert payload["decision"] == "STOP"
    assert payload["reason_code"] == "approval_blocked"
    assert payload["side_effect_requested"] == "git_push"
    assert payload["guarded_command"] == "git push"
    assert payload["would_run_git_push"] is False
    assert payload["performed_actions"] == []
    assert payload["evidence_refs"] == [{"path": "docs/EVIDENCE.md", "exists": True}]
    assert "ALLOW_EXECUTION" not in json.dumps(payload)


def test_approval_present_still_stops_because_executor_is_not_approved(tmp_path: Path, monkeypatch) -> None:
    write(tmp_path / "STATUS.md", "# Status\n")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    payload = preflight.run_preflight(
        task_summary="Push Phase 9L closeout",
        approval_ref="phase-9l-owner-approval",
        evidence_paths=["STATUS.md"],
    )

    assert payload["decision"] == "STOP"
    assert payload["reason_code"] == "executor_not_approved"
    assert payload["approval_ref_present"] is True
    assert payload["hermes_result"]["status"] == "NOT_RUN"
    assert "does not authorize an executor" in payload["next_step"]
    assert payload["performed_actions"] == []


def test_unsafe_input_is_blocked_without_echoing_private_or_secret_text(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    payload = preflight.run_preflight(
        task_summary=r"Push C:\Users\name\private.txt token=abc123",
        approval_ref="phase-9l-owner-approval",
    )
    text = json.dumps(payload, sort_keys=True)

    assert payload["decision"] == "STOP"
    assert payload["reason_code"] == "unsafe_input"
    assert payload["safe_task_summary"] == "[blocked unsafe input]"
    assert "C:" not in text
    assert "abc123" not in text


def test_invalid_or_missing_evidence_fails_closed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    invalid = preflight.run_preflight(
        task_summary="Push Phase 9L",
        approval_ref="phase-9l-owner-approval",
        evidence_paths=["../outside.md"],
    )
    missing = preflight.run_preflight(
        task_summary="Push Phase 9L",
        approval_ref="phase-9l-owner-approval",
        evidence_paths=["docs/MISSING.md"],
    )

    assert invalid["decision"] == "STOP"
    assert invalid["reason_code"] == "unsafe_input"
    assert missing["decision"] == "STOP"
    assert missing["reason_code"] == "source_basis_blocked"


def valid_hermes_result() -> dict[str, object]:
    return sidecar.assess_request(
        task_summary="Push Phase 9L closeout",
        side_effect="git_push",
        approval_ref="phase-9l-owner-approval",
        evidence_paths=[],
        repo_root=REPO_ROOT,
    )


def test_unexpected_schema_mode_status_and_side_effect_stop() -> None:
    schema = valid_hermes_result()
    schema["schema_version"] = "future.schema"
    mode = valid_hermes_result()
    mode["mode"] = "execute"
    status = valid_hermes_result()
    status["status"] = "ALLOW"
    side_effect = valid_hermes_result()
    side_effect["side_effect_requested"] = "git_commit"

    assert preflight.interpret_hermes_result(schema)["reason_code"] == "unexpected_schema_version"
    assert preflight.interpret_hermes_result(mode)["reason_code"] == "unexpected_mode"
    assert preflight.interpret_hermes_result(status)["reason_code"] == "unexpected_status"
    assert preflight.interpret_hermes_result(side_effect)["reason_code"] == "scope_conflict"


def test_missing_required_field_and_non_empty_performed_actions_stop() -> None:
    missing = valid_hermes_result()
    missing.pop("next_step")
    actions = valid_hermes_result()
    actions["performed_actions"] = ["git push"]

    assert preflight.interpret_hermes_result(missing)["reason_code"] == "unexpected_result_shape"
    result = preflight.interpret_hermes_result(actions)
    assert result["decision"] == "STOP"
    assert result["reason_code"] == "contract_violation"
    assert result["performed_actions"] == []


def test_evidence_refs_outside_approved_scope_stop() -> None:
    result = valid_hermes_result()
    result["evidence_refs"] = [{"path": "STATUS.md", "exists": True}]

    payload = preflight.interpret_hermes_result(result, approved_evidence_paths=["ACCEPTANCE_TRACE.md"])

    assert payload["decision"] == "STOP"
    assert payload["reason_code"] == "evidence_scope_blocked"
    assert payload["evidence_refs"] == []


def test_cli_emits_json_stdout_only(tmp_path: Path, monkeypatch, capsys) -> None:
    write(tmp_path / "STATUS.md", "# Status\n")
    monkeypatch.setattr(sidecar, "repo_root_from_script", lambda: tmp_path)

    exit_code = preflight.main(
        [
            "--task-summary",
            "Push Phase 9L closeout",
            "--approval-ref",
            "phase-9l-owner-approval",
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


def test_script_uses_standard_library_and_local_sidecar_only() -> None:
    source = Path(preflight.__file__).read_text(encoding="utf-8")
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

    assert imports <= {"__future__", "argparse", "hermes_sidecar", "json", "scripts", "typing"}
    for forbidden_import in ["subprocess", "os", "socket", "http", "urllib", "threading", "asyncio"]:
        assert forbidden_import not in imports

    text = source.lower()
    for forbidden_call in ["git push", "git add", "git commit", "git tag", "workflow dispatch"]:
        assert f"subprocess" not in text
        assert f"system(" not in text
        assert f"popen(" not in text
        assert forbidden_call in text
