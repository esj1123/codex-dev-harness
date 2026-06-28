from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import hermes_git_push_preflight_writer as writer


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_WRITER_IMPLEMENTATION_PLAN.md"


def selected_fixture() -> dict[str, object]:
    return {
        "reason_code": "writer_not_approved",
        "decision": "STOP",
        "evidence_refs": ["docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_CAPTURE_BOUNDARY_REVIEW.md"],
        "safe_summary": "Synthetic not-run writer skeleton validation only.",
        "checked_commit": "5f665343567fd87b69b41ab1097bc0e9e44b9e35",
        "local_verify_run_id": "28307218463",
        "local_verify_job_id": "83865467492",
        "created_at": "2026-06-28T01:23:45Z",
    }


IP_LIKE_VALUE = "connect " + ".".join(["10", "0", "0", "1"])
WINDOWS_ABSOLUTE_VALUE = "C:" + "\\" + "Users" + "\\" + "name" + "\\" + "private.txt"
POSIX_ABSOLUTE_VALUE = "/" + "Users" + "/name/private.txt"
WINDOWS_ABSOLUTE_EVIDENCE_REF = "C:" + "\\" + "Users" + "\\" + "name" + "\\" + "evidence.md"
BACKSLASH_EVIDENCE_REF = "docs" + "\\" + "evidence.md"


def read_plan() -> str:
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


def test_plan_documents_phase_9s_scope_and_status_trace_exclusion() -> None:
    text = read_plan()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = section(text, "Allowed Files")

    assert "`not_run_record_only`" in purpose
    assert "synthetic selected-field fixtures" in purpose
    assert "not durable receipt or trace persistence" in purpose
    for allowed_path in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_IMPLEMENTATION_PLAN.md",
        "scripts/hermes_git_push_preflight_writer.py",
        "tests/test_hermes_git_push_preflight_writer.py",
    ]:
        assert f"`{allowed_path}`" in allowed
    assert "`STATUS.md` and `ACCEPTANCE_TRACE.md` are intentionally excluded" in allowed


def test_plan_blocks_raw_capture_persistence_and_runtime_expansion() -> None:
    text = normalize_ws(
        section(read_plan(), "Input Policy")
        + section(read_plan(), "Output Policy")
        + section(read_plan(), "Non-goals")
    )

    for forbidden in [
        "live `scripts/hermes_git_push_preflight.py` stdout",
        "shell transcripts",
        "command logs",
        "approval text",
        "tool-call bodies",
        "tokens",
        "local absolute paths",
        "IP",
        "ports",
        "live config",
        "device values",
        "tracked receipt files",
        "tracked trace events",
        "audit logs",
        "generated artifacts under `artifacts/`",
        "edit schemas",
        "wire quality-gate or CI integration",
        "edit workflows",
        "execute MCP tools",
        "access downstream repositories",
    ]:
        assert forbidden in text


def test_build_not_run_record_emits_exact_bounded_shape() -> None:
    record = writer.build_not_run_record(selected_fixture())

    assert set(record) == writer.ALLOWED_FIELDS
    assert record["schema_version"] == writer.SCHEMA_VERSION
    assert record["writer_class"] == "not_run_record_only"
    assert record["status"] == "NOT_RUN"
    assert record["side_effect_class"] == "git_push"
    assert record["decision"] == "STOP"
    assert record["performed_actions"] == []
    assert record["evidence_refs"] == [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_CAPTURE_BOUNDARY_REVIEW.md"
    ]
    assert "raw_stdout" not in record
    assert "command_log" not in record


def test_fixed_fields_may_be_supplied_but_must_match() -> None:
    payload = selected_fixture()
    payload.update(
        {
            "schema_version": writer.SCHEMA_VERSION,
            "writer_class": "selected_fields_receipt_writer",
        }
    )

    with pytest.raises(writer.WriterValidationError, match="writer_class"):
        writer.build_not_run_record(payload)


def test_rejects_forbidden_and_unknown_keys_explicitly() -> None:
    forbidden = selected_fixture() | {"raw_stdout": "not allowed"}
    unknown = selected_fixture() | {"receipt_id": "R-1"}

    with pytest.raises(writer.WriterValidationError, match="forbidden selected-field keys"):
        writer.build_not_run_record(forbidden)
    with pytest.raises(writer.WriterValidationError, match="unknown selected-field keys"):
        writer.build_not_run_record(unknown)


@pytest.mark.parametrize(
    ("field", "bad_value", "match"),
    [
        ("safe_summary", "x" * (writer.SAFE_SUMMARY_MAX_LENGTH + 1), "exceeds bounded length"),
        ("safe_summary", "   ", "must not be empty"),
        ("safe_summary", "first line\nsecond line", "multiline raw content"),
        ("safe_summary", POSIX_ABSOLUTE_VALUE, "local absolute path"),
        ("safe_summary", WINDOWS_ABSOLUTE_VALUE, "local absolute path"),
        ("safe_summary", "token=abc123", "forbidden"),
        ("safe_summary", IP_LIKE_VALUE, "IP-like"),
        ("evidence_refs", ["../outside.md"], "parent traversal"),
        ("evidence_refs", [WINDOWS_ABSOLUTE_EVIDENCE_REF], "local absolute path"),
        ("evidence_refs", [BACKSLASH_EVIDENCE_REF], "POSIX separators"),
        ("evidence_refs", ["logs/raw.txt"], "private/raw/local"),
        ("evidence_refs", ["private/evidence.md"], "private/raw/local"),
        ("evidence_refs", ["raw/evidence.md"], "private/raw/local"),
        ("evidence_refs", ["secrets/evidence.md"], "private/raw/local"),
        ("evidence_refs", [f"docs/evidence-{i}.md" for i in range(writer.MAX_EVIDENCE_REFS + 1)], "bounded item count"),
        ("evidence_refs", "docs/evidence.md", "must be a list"),
        ("checked_commit", "5F665343567FD87B69B41AB1097BC0E9E44B9E35", "checked_commit"),
        ("checked_commit", 54846, "checked_commit must be a string"),
        ("local_verify_run_id", "run-28307218463", "local_verify_run_id"),
        ("local_verify_run_id", 28307218463, "local_verify_run_id must be a string"),
        ("local_verify_job_id", 83865467492, "local_verify_job_id must be a string"),
        ("created_at", "2026-06-28 01:23:45", "created_at"),
        ("created_at", 20260628, "created_at must be a string"),
    ],
)
def test_rejects_unsafe_or_malformed_selected_fields(field: str, bad_value: object, match: str) -> None:
    payload = selected_fixture()
    payload[field] = bad_value

    with pytest.raises(writer.WriterValidationError, match=match):
        writer.build_not_run_record(payload)


@pytest.mark.parametrize(
    "forbidden_key",
    ["receipt_path", "trace_path", "audit_log_path", "artifact_path"],
)
def test_rejects_forbidden_output_path_key_variants(forbidden_key: str) -> None:
    payload = selected_fixture() | {forbidden_key: "not allowed"}

    with pytest.raises(writer.WriterValidationError, match="forbidden selected-field keys"):
        writer.build_not_run_record(payload)


def test_write_uses_deterministic_json_and_cleanup_proves_no_persistence(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    first_record = writer.write_not_run_record(selected_fixture(), first, repo_root=REPO_ROOT)
    second_record = writer.write_not_run_record(selected_fixture(), second, repo_root=REPO_ROOT)
    expected = json.dumps(first_record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    assert first_record == second_record
    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")
    assert first.read_text(encoding="utf-8") == expected
    assert writer.cleanup_temporary_output(first) == "PASS"
    assert writer.cleanup_temporary_output(second) == "PASS"
    assert not first.exists()
    assert not second.exists()


def test_output_path_without_json_suffix_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(writer.WriterValidationError, match=".json suffix"):
        writer.write_not_run_record(selected_fixture(), tmp_path / "record.txt", repo_root=REPO_ROOT)


def test_output_path_inside_repo_or_existing_file_is_rejected(tmp_path: Path) -> None:
    repo_output = REPO_ROOT / "_tmp_phase9s_writer_output.json"
    existing = tmp_path / "existing.json"
    existing.write_text("{}\n", encoding="utf-8")

    with pytest.raises(writer.WriterValidationError, match="inside the repository"):
        writer.write_not_run_record(selected_fixture(), repo_output, repo_root=REPO_ROOT)
    with pytest.raises(writer.WriterValidationError, match="overwrite"):
        writer.write_not_run_record(selected_fixture(), existing, repo_root=REPO_ROOT)


def test_missing_cleanup_is_fail(tmp_path: Path) -> None:
    with pytest.raises(writer.WriterValidationError, match="FAIL: cleanup target is missing"):
        writer.cleanup_temporary_output(tmp_path / "missing-phase-9s-output.json")


def test_cli_accepts_synthetic_fixture_and_stdout_is_summary_only(tmp_path: Path, capsys) -> None:
    fixture = tmp_path / "fixture.json"
    output = tmp_path / "record.json"
    fixture.write_text(json.dumps(selected_fixture(), sort_keys=True), encoding="utf-8")

    exit_code = writer.main(["--fixture-json", str(fixture), "--output-json", str(output)])
    captured = capsys.readouterr()
    record = json.loads(output.read_text(encoding="utf-8"))
    summary = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert summary == {"status": "PASS", "writer_class": "not_run_record_only"}
    assert record["status"] == "NOT_RUN"
    assert "raw_stdout" not in json.dumps(record, sort_keys=True)
    assert writer.cleanup_temporary_output(output) == "PASS"


def test_cli_invalid_json_returns_environment_blocked_and_creates_no_output(tmp_path: Path, capsys) -> None:
    fixture = tmp_path / "fixture.json"
    output = tmp_path / "record.json"
    fixture.write_text("{not valid json\n", encoding="utf-8")

    exit_code = writer.main(["--fixture-json", str(fixture), "--output-json", str(output)])
    captured = capsys.readouterr()
    error = json.loads(captured.err)

    assert exit_code == 2
    assert captured.out == ""
    assert error == {"status": "ENVIRONMENT BLOCKED", "reason": "fixture_unavailable_or_invalid_json"}
    assert not output.exists()


def test_cli_validation_failure_returns_fail_and_creates_no_output(tmp_path: Path, capsys) -> None:
    fixture = tmp_path / "fixture.json"
    output = tmp_path / "record.json"
    payload = selected_fixture() | {"artifact_path": "not allowed"}
    fixture.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    exit_code = writer.main(["--fixture-json", str(fixture), "--output-json", str(output)])
    captured = capsys.readouterr()
    error = json.loads(captured.err)

    assert exit_code == 2
    assert captured.out == ""
    assert error["status"] == "FAIL"
    assert "forbidden selected-field keys" in error["reason"]
    assert not output.exists()


def test_script_uses_standard_library_and_does_not_import_live_preflight_or_subprocess() -> None:
    source = Path(writer.__file__).read_text(encoding="utf-8")
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

    assert imports <= {"__future__", "argparse", "json", "pathlib", "re", "sys", "typing"}
    for forbidden in [
        "subprocess",
        "os",
        "socket",
        "http",
        "urllib",
        "threading",
        "asyncio",
        "scripts.hermes_git_push_preflight",
        "hermes_git_push_preflight",
    ]:
        assert forbidden not in imports

    lowered = source.lower()
    for forbidden_call in ["subprocess", "system(", "popen(", "git push", "workflow run"]:
        assert forbidden_call not in lowered
