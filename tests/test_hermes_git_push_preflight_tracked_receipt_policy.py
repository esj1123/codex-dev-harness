from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import hermes_git_push_preflight_receipt_writer as receipt_writer


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_POLICY.md"
RECEIPT_SCHEMA_PATH = REPO_ROOT / "audits" / "receipt-summary.schema.json"
PROPOSED_PREFIX = "audits/receipts/hermes-git-push-preflight/"
APPROVED_PHASE_9Y_RECEIPT = (
    "audits/receipts/hermes-git-push-preflight/"
    "phase-9y-hermes-git-push-preflight-tracked-receipt-synthetic-not-run.json"
)


def policy_text() -> str:
    return POLICY_PATH.read_text(encoding="utf-8")


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
    assert files == [APPROVED_PHASE_9Y_RECEIPT]

def test_policy_documents_phase_9w_scope_basis_and_decision() -> None:
    text = policy_text()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = section(text, "Allowed Files")
    basis = section(text, "Basis")
    decision = normalize_ws(section(text, "Policy Decision"))

    assert "`tracked_receipt_generation_policy_documented_without_receipt_output`" in decision
    assert "does not approve tracked receipt generation" in decision
    assert "documentation and focused synthetic-test only" in purpose

    for allowed_file in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_POLICY.md",
        "tests/test_hermes_git_push_preflight_tracked_receipt_policy.py",
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
        "docs/HERMES_GIT_PUSH_PREFLIGHT_DURABLE_WRITER_PROPOSAL.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_SELECTED_RECEIPT_WRITER_IMPLEMENTATION_PLAN.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_PERSISTENCE_HOLD_DECISION.md",
        "audits/receipt-summary.schema.json",
        "scripts/hermes_git_push_preflight_receipt_writer.py",
        "tests/test_hermes_git_push_preflight_receipt_writer.py",
        "28498555756",
        "84470173481",
        "31ee09d7db6bbe7ea079a6cc90a31b6029a19089",
    ]:
        assert f"`{basis_item}`" in basis


def test_future_approval_requirements_are_explicit_and_fail_closed() -> None:
    requirements = normalize_ws(section(policy_text(), "Future Approval Requirements"))

    for required_item in [
        "exact receipt id",
        "exact repo-relative output path",
        "whether the receipt directory may be created",
        "overwrite policy",
        "retention policy",
        "cleanup/reversion policy",
        "source fixture policy and selected fields",
        "schema validation procedure",
        "redaction review",
        "owner approval evidence as a boolean or safe reference, not approval text",
        "Local Verify run, job, and checked-out head commit requirements",
        "artifact upload policy, expected to be `none` unless separately approved",
        "staging, commit, push, and Local Verify closeout workflow",
        "no downstream access",
    ]:
        assert required_item in requirements

    assert "If any required item is absent, tracked receipt generation is `BLOCKED`." in requirements


def test_proposed_location_is_policy_only_and_current_writer_still_rejects_repo_output() -> None:
    location = normalize_ws(section(policy_text(), "Proposed Receipt Location Policy"))

    assert f"`{PROPOSED_PREFIX}<receipt_id>.json`" in location
    assert "Phase 9W does not create `audits/receipts`" in location
    assert "path pattern is a policy placeholder only" in location
    assert "Existing output overwrite is forbidden" in location

    assert_receipts_absent_or_exact_phase_9y_only()

    repo_internal_output = REPO_ROOT / "audits" / "receipts" / "hermes-git-push-preflight" / "phase-9w.json"
    with pytest.raises(receipt_writer.ReceiptWriterValidationError, match="inside the repository"):
        receipt_writer.validate_temporary_output_path(repo_internal_output, repo_root=REPO_ROOT)


def test_receipt_content_policy_matches_required_schema_top_level_fields() -> None:
    content = section(policy_text(), "Receipt Content Policy")
    normalized = normalize_ws(content)
    schema = receipt_schema()
    required_fields = schema["required"]

    assert "full `receipt_summary` document" in content
    assert "`audits/receipt-summary.schema.json`" in content
    assert "`hermes_git_push_preflight_evidence` object alone" in content

    for field in required_fields:
        assert f"`{field}`" in content

    assert "`hermes_git_push_preflight_evidence`" in content
    assert "must not replace the full receipt summary" in normalized


def test_source_and_redaction_policy_blocks_raw_private_live_material() -> None:
    source = normalize_ws(section(policy_text(), "Source And Redaction Policy"))

    assert "synthetic selected-field fixtures" in source
    assert "Real `scripts/hermes_git_push_preflight.py` stdout capture remains unapproved" in source

    for forbidden_material in [
        "raw stdout",
        "stderr",
        "shell transcripts",
        "command logs",
        "approval text",
        "prompt text",
        "prompt transcripts",
        "tool-call bodies",
        "model output transcripts",
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
        assert forbidden_material in source

    assert "Approval conversation text must not be stored" in source


def test_generation_workflow_requires_temp_first_schema_redaction_and_no_artifacts() -> None:
    workflow = normalize_ws(section(policy_text(), "Generation Workflow"))

    for expected in [
        "temporary path outside the repository first",
        "deterministic JSON",
        "final newline",
        "Validate against `audits/receipt-summary.schema.json`",
        "Run redaction review before repository copy",
        "Copy to the exact approved tracked path only after path, schema, redaction, overwrite, retention, and cleanup conditions pass",
        "git ls-files --others --exclude-standard",
        "git diff --name-status",
        "artifact upload status `none`",
    ]:
        assert expected in workflow

    for failure in [
        "Missing cleanup",
        "missing schema validation",
        "missing redaction review",
        "unexpected untracked files",
        "attempted overwrite",
        "any path outside the approved pattern",
    ]:
        assert failure in workflow


def test_failure_modes_verification_non_goals_and_next_step_are_bounded() -> None:
    failure = section(policy_text(), "Failure Modes")
    verification = section(policy_text(), "Verification")
    non_goals = normalize_ws(section(policy_text(), "Non-goals"))
    next_step = normalize_ws(section(policy_text(), "Next Step"))

    for status in ["`PASS`", "`PASS WITH NOTES`", "`BLOCKED`", "`FAIL`", "`NOT RUN`", "`ENVIRONMENT BLOCKED`"]:
        assert status in failure

    for command in [
        "python -m pytest tests/test_hermes_git_push_preflight_tracked_receipt_policy.py",
        "python -m pytest tests/test_hermes_git_push_preflight_receipt_writer.py",
        "python -m pytest tests/test_json_evidence_gate.py",
        "python -m pytest tests",
        "python scripts/quality_gate.py",
        "git diff --check",
        "git ls-files --others --exclude-standard",
    ]:
        assert command in verification

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

    assert "separately approved Phase 9X tracked receipt-generation contract" in next_step
    assert "Phase 9W does not authorize Phase 9X by itself" in next_step
