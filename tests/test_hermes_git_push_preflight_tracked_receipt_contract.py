from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

import pytest

from scripts import hermes_git_push_preflight_receipt_writer as receipt_writer


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_CONTRACT.md"
RECEIPT_SCHEMA_PATH = REPO_ROOT / "audits" / "receipt-summary.schema.json"
RECEIPT_ID = "phase-9y-hermes-git-push-preflight-tracked-receipt-synthetic-not-run"
OUTPUT_PATH = f"audits/receipts/hermes-git-push-preflight/{RECEIPT_ID}.json"


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


def receipt_schema() -> dict[str, object]:
    return json.loads(RECEIPT_SCHEMA_PATH.read_text(encoding="utf-8"))



def assert_receipts_absent_or_exact_phase_9y_only() -> None:
    receipts_root = REPO_ROOT / "audits" / "receipts"
    if not receipts_root.exists():
        return

    files = sorted(path.relative_to(REPO_ROOT).as_posix() for path in receipts_root.rglob("*") if path.is_file())
    assert files == [OUTPUT_PATH]

def test_contract_documents_phase_9x_scope_basis_and_decision() -> None:
    text = contract_text()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = section(text, "Allowed Files")
    basis = section(text, "Basis")
    decision = normalize_ws(section(text, "Contract Decision"))

    assert "`tracked_receipt_generation_contract_documented_without_receipt_output`" in decision
    assert "does not approve receipt generation by itself" in decision
    assert "documentation and focused synthetic-test only" in purpose

    for allowed_file in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_CONTRACT.md",
        "tests/test_hermes_git_push_preflight_tracked_receipt_contract.py",
    ]:
        assert f"`{allowed_file}`" in allowed

    for no_touch in [
        "`STATUS.md`",
        "`ACCEPTANCE_TRACE.md`",
        "scripts",
        "schemas",
        "JSON gates",
        "workflows",
        "artifacts",
        "audits",
        "downstream repositories",
    ]:
        assert no_touch in allowed

    for basis_item in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_POLICY.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_SELECTED_RECEIPT_WRITER_IMPLEMENTATION_PLAN.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_PERSISTENCE_HOLD_DECISION.md",
        "audits/receipt-summary.schema.json",
        "scripts/hermes_git_push_preflight_receipt_writer.py",
        "tests/test_hermes_git_push_preflight_receipt_writer.py",
        "28499585606",
        "84473490892",
        "d48a6e311027ca21cbda44e206d95f6906787986",
    ]:
        assert f"`{basis_item}`" in basis


def test_exact_future_receipt_target_is_single_repo_relative_json_path() -> None:
    target = normalize_ws(section(contract_text(), "Exact Future Receipt Target"))

    assert f"receipt id: `{RECEIPT_ID}`" in target
    assert f"`{OUTPUT_PATH}`" in target
    assert "No alternate receipt id" in target
    assert "local absolute path syntax" in target

    pure_path = PurePosixPath(OUTPUT_PATH)
    assert not pure_path.is_absolute()
    assert pure_path.suffix == ".json"
    assert pure_path.parts[:3] == ("audits", "receipts", "hermes-git-push-preflight")
    assert ".." not in pure_path.parts
    assert_receipts_absent_or_exact_phase_9y_only()

    with pytest.raises(receipt_writer.ReceiptWriterValidationError, match="inside the repository"):
        receipt_writer.validate_temporary_output_path(REPO_ROOT / OUTPUT_PATH, repo_root=REPO_ROOT)


def test_directory_overwrite_retention_and_cleanup_policies_fail_closed() -> None:
    directory = normalize_ws(section(contract_text(), "Directory And Overwrite Policy"))
    cleanup = normalize_ws(section(contract_text(), "Retention And Cleanup Policy"))

    for expected in [
        "Phase 9X does not create any directory",
        "`audits/receipts/hermes-git-push-preflight`",
        "must not create any other directory",
        "must not already exist before generation",
        "Phase 9Y is `BLOCKED`",
        "overwrite, replacement, append, merge, or in-place repair is forbidden",
    ]:
        assert expected in directory

    for expected in [
        "retained as a normal repository file",
        "temporary candidate receipt must be written outside the repository first",
        "Temporary files must be deleted before closeout",
        "must not be copied into the repository",
        "unstage it",
        "delete the tracked output",
        "Cleanup failure is `FAIL`",
    ]:
        assert expected in cleanup


def test_source_fixture_contract_matches_existing_writer_fields_and_fixed_values() -> None:
    source = section(contract_text(), "Source Fixture Contract")
    normalized_source = normalize_ws(source)

    for field in sorted(receipt_writer.RECEIPT_EVIDENCE_FIELDS):
        assert f"`{field}`" in source

    for fixed_field, fixed_value in receipt_writer.FIXED_VALUES.items():
        expected = str(fixed_value).lower() if isinstance(fixed_value, bool) else str(fixed_value)
        assert f"`{fixed_field}`: `{expected}`" in source

    for required_pair in [
        "`preflight_evidence_status`: `not_run`",
        "`caller_schema_version`: `hermes_git_push_preflight.v0`",
        "`caller_mode`: `dry_run`",
        "`decision`: `STOP`",
        "`side_effect_requested`: `git_push`",
        "`guarded_command`: `git push`",
        "`reason_code`: `tracked_receipt_generation_contract_only`",
        "`approval_ref_present`: `true`",
    ]:
        assert required_pair in source

    for forbidden_key in [
        "`receipt_id`",
        "`task_id`",
        "`receipt_path`",
        "`trace_path`",
        "`audit_log_path`",
        "`artifact_path`",
        "raw stdout fields",
        "command-log fields",
        "approval text",
        "local absolute paths",
        "downstream raw evidence",
    ]:
        assert forbidden_key in normalized_source


def test_receipt_summary_contract_matches_schema_required_fields_and_safe_values() -> None:
    summary = section(contract_text(), "Receipt Summary Contract")
    schema = receipt_schema()

    assert "full `receipt_summary` document" in summary
    assert "`audits/receipt-summary.schema.json`" in summary
    assert "`hermes_git_push_preflight_evidence` object" in summary

    for field in schema["required"]:
        assert f"`{field}`" in summary

    for expected in [
        "`schema_version`: `1.0`",
        "`evidence_kind`: `receipt_summary`",
        f"`receipt_id`: `{RECEIPT_ID}`",
        "`repository`: `esj1123/codex-dev-harness`",
        "`approval.approval_class`: `owner_approved_local_commit`",
        "`approval.approval_reference`: safe reference only, not approval text",
        "`side_effect_class`: `documentation_edit`",
        "`artifacts.release_artifact_status`: `not generated`",
        "`artifacts.artifact_upload_status`: `none`",
    ]:
        assert expected in summary


def test_local_verify_policy_blocks_recursive_evidence_claims() -> None:
    policy = normalize_ws(section(contract_text(), "Local Verify Evidence Policy"))

    for expected in [
        "must not claim clean Local Verify for the same receipt commit inside that same commit",
        "recursive evidence",
        "Phase 9W run `28499585606`, job `84473490892`",
        "`d48a6e311027ca21cbda44e206d95f6906787986`",
        "must be recorded in the Phase 9Y task closeout after push",
        "not by editing the same tracked receipt in the same implementation commit",
    ]:
        assert expected in policy


def test_schema_redaction_verification_failure_modes_and_non_goals_are_bounded() -> None:
    schema_redaction = normalize_ws(section(contract_text(), "Schema And Redaction Procedure"))
    verification = section(contract_text(), "Phase 9Y Verification Gate")
    failure = section(contract_text(), "Failure Modes")
    non_goals = normalize_ws(section(contract_text(), "Non-goals"))
    next_step = normalize_ws(section(contract_text(), "Next Step"))

    for expected in [
        "temporary path outside the repository",
        "deterministic JSON and a final newline",
        "Validate the full receipt against `audits/receipt-summary.schema.json`",
        "selected_fields_receipt_writer",
        "Run redaction review before copying",
        "git ls-files --others --exclude-standard",
        "git diff --name-status",
    ]:
        assert expected in schema_redaction

    for forbidden_material in [
        "raw stdout",
        "stderr",
        "shell transcripts",
        "command logs",
        "approval text",
        "prompt text",
        "tool-call bodies",
        "tokens",
        "account values",
        "local absolute paths",
        "IPs",
        "ports",
        "endpoints",
        "live config",
        "device values",
        "private data",
        "raw `08_Study`",
        "RSID raw evidence",
        "downstream raw evidence",
        "generated downstream source",
        "raw logs",
        "secrets",
    ]:
        assert forbidden_material in schema_redaction

    for command in [
        "python -m pytest tests/test_hermes_git_push_preflight_tracked_receipt_contract.py",
        "python -m pytest tests/test_hermes_git_push_preflight_tracked_receipt_policy.py",
        "python -m pytest tests/test_hermes_git_push_preflight_receipt_writer.py",
        "python -m pytest tests/test_json_evidence_gate.py",
        "python -m pytest tests",
        "python scripts/quality_gate.py",
        "git diff --check",
        "git ls-files --others --exclude-standard",
    ]:
        assert command in verification

    for status in ["`PASS`", "`PASS WITH NOTES`", "`BLOCKED`", "`FAIL`", "`NOT RUN`", "`ENVIRONMENT BLOCKED`"]:
        assert status in failure

    for forbidden_scope in [
        "generate a receipt file",
        "create `audits/receipts`",
        "change `scripts/hermes_git_push_preflight_receipt_writer.py`",
        "change `scripts/hermes_git_push_preflight_writer.py`",
        "change receipt or trace schemas",
        "change `scripts/gates/json_evidence_gate.py`",
        "connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP",
        "run real `git push`, `git add`, `git commit`, `git tag`",
        "workflow dispatch",
        "artifact upload",
        "receipt generation",
        "trace writing",
        "downstream mutation through Hermes",
    ]:
        assert forbidden_scope in non_goals

    assert "separately approved Phase 9Y tracked receipt synthetic generation task" in next_step
    assert "Phase 9X does not authorize Phase 9Y by itself" in next_step
