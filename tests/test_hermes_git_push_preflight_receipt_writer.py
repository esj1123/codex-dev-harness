from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from scripts import hermes_git_push_preflight_receipt_writer as writer


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_SELECTED_RECEIPT_WRITER_IMPLEMENTATION_PLAN.md"
RECEIPT_SCHEMA_PATH = REPO_ROOT / "audits" / "receipt-summary.schema.json"


def selected_fixture() -> dict[str, object]:
    return {
        "preflight_evidence_status": "stopped",
        "preflight_output_mode": "selected_fields",
        "caller_schema_version": "hermes_git_push_preflight.v0",
        "caller_mode": "dry_run",
        "decision": "STOP",
        "side_effect_requested": "git_push",
        "guarded_command": "git push",
        "would_run_git_push": False,
        "performed_actions_empty": True,
        "reason_code": "executor_not_approved",
        "stop_reasons": ["Hermes preflight remains fail-closed."],
        "approval_ref_present": True,
        "evidence_refs": ["docs/HERMES_GIT_PUSH_PREFLIGHT_DURABLE_WRITER_PROPOSAL.md"],
        "hermes_result_summary": "No executor is approved and no actions were performed.",
        "safe_task_summary": "Synthetic selected receipt evidence writer verification.",
        "safety_notes": ["Temporary selected-field output only; no receipt file is generated."],
        "observed_head_commit": "a101bc704acfdd7f34e1161275010c9a0bea3c19",
        "local_verify_run_id": "28496626209",
        "local_verify_job_id": "84464169619",
        "output_capture": "selected_fields",
        "preflight_integration_status": "receipt-summary-only",
    }


IP_LIKE_VALUE = "connect " + ".".join(["10", "0", "0", "1"])
WINDOWS_ABSOLUTE_VALUE = "C:" + "\\" + "Users" + "\\" + "name" + "\\" + "private.txt"
POSIX_ABSOLUTE_VALUE = "/" + "Users" + "/name/private.txt"
WINDOWS_ABSOLUTE_EVIDENCE_REF = "C:" + "\\" + "Users" + "\\" + "name" + "\\" + "evidence.md"
BACKSLASH_EVIDENCE_REF = "docs" + "\\" + "evidence.md"


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


def receipt_schema_evidence() -> dict[str, object]:
    schema = json.loads(RECEIPT_SCHEMA_PATH.read_text(encoding="utf-8"))
    return schema["properties"]["hermes_git_push_preflight_evidence"]


def test_plan_documents_phase_9v_scope_and_no_touch_areas() -> None:
    text = plan_text()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = normalize_ws(section(text, "Allowed Files"))

    assert "`selected_fields_receipt_writer`" in purpose
    assert "`receipt_summary.hermes_git_push_preflight_evidence` object" in purpose
    assert "temporary JSON outside the repository" in purpose
    for allowed_path in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_SELECTED_RECEIPT_WRITER_IMPLEMENTATION_PLAN.md",
        "scripts/hermes_git_push_preflight_receipt_writer.py",
        "tests/test_hermes_git_push_preflight_receipt_writer.py",
    ]:
        assert f"`{allowed_path}`" in allowed

    for excluded in [
        "`STATUS.md`",
        "`ACCEPTANCE_TRACE.md`",
        "schemas",
        "JSON gates",
        "workflows",
        "artifacts",
        "downstream repositories",
    ]:
        assert excluded in allowed


def test_plan_blocks_full_receipt_trace_audit_and_runtime_expansion() -> None:
    text = normalize_ws(
        section(plan_text(), "Writer Class")
        + section(plan_text(), "Input Policy")
        + section(plan_text(), "Output Policy")
        + section(plan_text(), "Non-goals")
    )

    for forbidden in [
        "full receipt summary",
        "trace event",
        "audit log",
        "real `scripts/hermes_git_push_preflight.py` stdout",
        "raw stdout",
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
        "receipt top-level fields",
        "trace top-level fields",
        "`receipt_id`",
        "`related_receipt_id`",
        "`receipt_evidence_key`",
        "No tracked receipt, trace, audit, or artifact output",
        "quality-gate or CI integration",
        "MCP",
        "downstream repositories",
    ]:
        assert forbidden in text


def test_build_receipt_evidence_emits_exact_schema_field_shape() -> None:
    record = writer.build_receipt_evidence(selected_fixture())
    schema_evidence = receipt_schema_evidence()
    schema_fields = set(schema_evidence["properties"])

    assert set(record) == writer.RECEIPT_EVIDENCE_FIELDS
    assert set(record) <= schema_fields
    assert record["preflight_evidence_status"] == "stopped"
    assert record["preflight_output_mode"] == "selected_fields"
    assert record["caller_schema_version"] == "hermes_git_push_preflight.v0"
    assert record["decision"] == "STOP"
    assert record["would_run_git_push"] is False
    assert record["performed_actions_empty"] is True
    assert record["output_capture"] == "selected_fields"
    assert record["preflight_integration_status"] == "receipt-summary-only"
    assert "receipt_id" not in record
    assert "related_receipt_id" not in record
    assert "receipt_evidence_key" not in record
    assert "raw_stdout" not in record


def test_schema_required_fields_are_present_and_output_has_no_extra_properties() -> None:
    record = writer.build_receipt_evidence(selected_fixture())
    schema_evidence = receipt_schema_evidence()

    assert schema_evidence["additionalProperties"] is False
    assert set(schema_evidence["required"]) <= set(record)
    assert set(record) <= set(schema_evidence["properties"])


def test_rejects_forbidden_and_unknown_keys_explicitly() -> None:
    forbidden = selected_fixture() | {"raw_stdout": "not allowed"}
    receipt_top_level = selected_fixture() | {"receipt_id": "receipt-1"}
    trace_pointer = selected_fixture() | {"receipt_evidence_key": "hermes_git_push_preflight_evidence"}
    unknown = selected_fixture() | {"writer_class": "selected_fields_receipt_writer"}

    for payload in [forbidden, receipt_top_level, trace_pointer]:
        with pytest.raises(writer.ReceiptWriterValidationError, match="forbidden selected-field keys"):
            writer.build_receipt_evidence(payload)
    with pytest.raises(writer.ReceiptWriterValidationError, match="unknown selected-field keys"):
        writer.build_receipt_evidence(unknown)


@pytest.mark.parametrize(
    ("field", "bad_value", "match"),
    [
        ("preflight_evidence_status", "executed", "unsupported value"),
        ("preflight_output_mode", "stdout_only", "preflight_output_mode"),
        ("caller_schema_version", "v0", "unsupported value"),
        ("caller_mode", "live", "unsupported value"),
        ("decision", "RUN", "unsupported value"),
        ("side_effect_requested", "release", "unsupported value"),
        ("guarded_command", "git push origin main", "unsupported value"),
        ("would_run_git_push", True, "would_run_git_push"),
        ("performed_actions_empty", False, "performed_actions_empty"),
        ("reason_code", "ExecutorNotApproved", "reason_code"),
        ("reason_code", "token=abc123", "forbidden"),
        ("stop_reasons", "not a list", "stop_reasons must be a list"),
        ("stop_reasons", ["x" for _ in range(writer.MAX_LIST_ITEMS + 1)], "bounded item count"),
        ("stop_reasons", ["first line\nsecond line"], "multiline raw content"),
        ("approval_ref_present", "yes", "approval_ref_present must be a boolean"),
        ("evidence_refs", "docs/evidence.md", "evidence_refs must be a list"),
        ("evidence_refs", ["../outside.md"], "parent traversal"),
        ("evidence_refs", [WINDOWS_ABSOLUTE_EVIDENCE_REF], "local absolute path"),
        ("evidence_refs", [BACKSLASH_EVIDENCE_REF], "POSIX separators"),
        ("evidence_refs", ["logs/raw.txt"], "private/raw/local"),
        ("evidence_refs", [f"docs/evidence-{i}.md" for i in range(writer.MAX_EVIDENCE_REFS + 1)], "bounded item count"),
        ("hermes_result_summary", POSIX_ABSOLUTE_VALUE, "local absolute path"),
        ("safe_task_summary", WINDOWS_ABSOLUTE_VALUE, "local absolute path"),
        ("safe_task_summary", IP_LIKE_VALUE, "IP-like"),
        ("safety_notes", "not a list", "safety_notes must be a list"),
        ("observed_head_commit", "A101BC704ACFDD7F34E1161275010C9A0BEA3C19", "observed_head_commit"),
        ("observed_head_commit", 12345, "observed_head_commit must be a string"),
        ("local_verify_run_id", "run-28496626209", "local_verify_run_id"),
        ("local_verify_run_id", 28496626209, "local_verify_run_id must be a string"),
        ("local_verify_job_id", 84464169619, "local_verify_job_id must be a string"),
        ("output_capture", "redacted_summary", "output_capture"),
        ("preflight_integration_status", "not integrated", "preflight_integration_status"),
    ],
)
def test_rejects_unsafe_or_malformed_selected_fields(field: str, bad_value: object, match: str) -> None:
    payload = selected_fixture()
    payload[field] = bad_value

    with pytest.raises(writer.ReceiptWriterValidationError, match=match):
        writer.build_receipt_evidence(payload)


def test_write_uses_deterministic_json_and_cleanup_proves_no_persistence(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    first_record = writer.write_receipt_evidence(selected_fixture(), first, repo_root=REPO_ROOT)
    second_record = writer.write_receipt_evidence(selected_fixture(), second, repo_root=REPO_ROOT)
    expected = json.dumps(first_record, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    assert first_record == second_record
    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")
    assert first.read_text(encoding="utf-8") == expected
    assert writer.cleanup_temporary_output(first) == "PASS"
    assert writer.cleanup_temporary_output(second) == "PASS"
    assert not first.exists()
    assert not second.exists()


def test_output_path_without_json_suffix_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(writer.ReceiptWriterValidationError, match=".json suffix"):
        writer.write_receipt_evidence(selected_fixture(), tmp_path / "record.txt", repo_root=REPO_ROOT)


def test_output_path_inside_repo_or_existing_file_is_rejected(tmp_path: Path) -> None:
    repo_output = REPO_ROOT / "_tmp_phase9v_receipt_writer_output.json"
    existing = tmp_path / "existing.json"
    existing.write_text("{}\n", encoding="utf-8")

    with pytest.raises(writer.ReceiptWriterValidationError, match="inside the repository"):
        writer.write_receipt_evidence(selected_fixture(), repo_output, repo_root=REPO_ROOT)
    with pytest.raises(writer.ReceiptWriterValidationError, match="overwrite"):
        writer.write_receipt_evidence(selected_fixture(), existing, repo_root=REPO_ROOT)


def test_missing_cleanup_is_fail(tmp_path: Path) -> None:
    with pytest.raises(writer.ReceiptWriterValidationError, match="FAIL: cleanup target is missing"):
        writer.cleanup_temporary_output(tmp_path / "missing-phase-9v-output.json")


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
    assert summary == {"status": "PASS", "writer_class": "selected_fields_receipt_writer"}
    assert record["preflight_integration_status"] == "receipt-summary-only"
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
    payload = selected_fixture() | {"receipt_id": "not allowed"}
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
    for forbidden_call in ["subprocess", "system(", "popen(", "git push origin", "workflow run"]:
        assert forbidden_call not in lowered
