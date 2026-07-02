from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "docs"
    / "HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_POST_GENERATION_BOUNDARY_REVIEW.md"
)
RECEIPT_ID = "phase-9y-hermes-git-push-preflight-tracked-receipt-synthetic-not-run"
RECEIPT_PATH = (
    REPO_ROOT
    / "audits"
    / "receipts"
    / "hermes-git-push-preflight"
    / f"{RECEIPT_ID}.json"
)
RECEIPT_RELATIVE_PATH = RECEIPT_PATH.relative_to(REPO_ROOT).as_posix()
PHASE_9Y_COMMIT = "7551cb2973ba545922bcb9edb55d8d4e3ca98f75"
PHASE_9Y_RUN_ID = "28561574671"
PHASE_9Y_JOB_ID = "84680140069"
PHASE_9Y1_RUN_ID = "28554625970"
PHASE_9Y1_JOB_ID = "84659286610"


def review_text() -> str:
    return REVIEW_PATH.read_text(encoding="utf-8")


def receipt_text() -> str:
    return RECEIPT_PATH.read_text(encoding="utf-8")


def receipt_json() -> dict[str, object]:
    return json.loads(receipt_text())


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def receipt_files() -> list[str]:
    receipts_root = REPO_ROOT / "audits" / "receipts"
    if not receipts_root.exists():
        return []
    return sorted(path.relative_to(REPO_ROOT).as_posix() for path in receipts_root.rglob("*") if path.is_file())


def test_review_documents_phase_9z_scope_basis_and_decision() -> None:
    text = review_text()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = section(text, "Allowed Files")
    basis = section(text, "Basis")
    decision = normalize_ws(section(text, "Review Decision"))

    assert "`tracked_receipt_post_generation_boundary_review_documented_without_receipt_edit`" in decision
    assert "does not approve a receipt refresh" in decision
    assert "documentation and focused synthetic-test only" in purpose
    assert "without editing that receipt" in purpose

    for allowed_file in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_POST_GENERATION_BOUNDARY_REVIEW.md",
        "tests/test_hermes_git_push_preflight_tracked_receipt_post_generation_review.py",
    ]:
        assert f"`{allowed_file}`" in allowed

    for no_touch in [
        "`STATUS.md`",
        "`ACCEPTANCE_TRACE.md`",
        "the Phase 9Y receipt file",
        "scripts",
        "schemas",
        "JSON gates",
        "workflows",
        "artifacts",
        "downstream repositories",
    ]:
        assert no_touch in allowed

    for basis_item in [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_POLICY.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_CONTRACT.md",
        "audits/receipt-summary.schema.json",
        "scripts/hermes_git_push_preflight_receipt_writer.py",
        "tests/test_hermes_git_push_preflight_tracked_receipt_policy.py",
        "tests/test_hermes_git_push_preflight_tracked_receipt_contract.py",
        RECEIPT_RELATIVE_PATH,
        PHASE_9Y_RUN_ID,
        PHASE_9Y_JOB_ID,
        PHASE_9Y_COMMIT,
    ]:
        assert f"`{basis_item}`" in basis


def test_review_names_exact_single_receipt_and_local_verify_closeout() -> None:
    text = review_text()
    reviewed_receipt = normalize_ws(section(text, "Reviewed Receipt"))
    local_verify = normalize_ws(section(text, "Post-Push Local Verify Evidence"))

    assert f"receipt id: `{RECEIPT_ID}`" in reviewed_receipt
    assert f"`{RECEIPT_RELATIVE_PATH}`" in reviewed_receipt
    assert "No alternate receipt id" in reviewed_receipt
    assert "schema sidecar" in reviewed_receipt

    for expected in [
        f"commit: `{PHASE_9Y_COMMIT}`",
        "workflow: `Local Verify`",
        f"run: `{PHASE_9Y_RUN_ID}`",
        f"job: `{PHASE_9Y_JOB_ID}`",
        "tests: passed with `398` cases",
        "contents permission: read-only",
        "artifact upload status: `none`",
        "must not be injected into the Phase 9Y receipt",
    ]:
        assert expected in local_verify

    assert receipt_files() == [RECEIPT_RELATIVE_PATH]


def test_tracked_phase_9y_receipt_remains_exact_safe_not_run_receipt() -> None:
    receipt = receipt_json()
    evidence = receipt["hermes_git_push_preflight_evidence"]

    assert receipt["schema_version"] == "1.0"
    assert receipt["evidence_kind"] == "receipt_summary"
    assert receipt["receipt_id"] == RECEIPT_ID
    assert receipt["repository"] == "esj1123/codex-dev-harness"
    assert receipt["side_effect_class"] == "documentation_edit"
    assert receipt["status_label"] == "PASS WITH NOTES"
    assert receipt["artifacts"] == {
        "artifact_upload_status": "none",
        "generated": [],
        "release_artifact_status": "not generated",
    }
    assert receipt["changed_files"] == [
        {
            "change_type": "added",
            "path": RECEIPT_RELATIVE_PATH,
        }
    ]

    assert isinstance(evidence, dict)
    assert evidence["preflight_evidence_status"] == "not_run"
    assert evidence["preflight_output_mode"] == "selected_fields"
    assert evidence["caller_schema_version"] == "hermes_git_push_preflight.v0"
    assert evidence["caller_mode"] == "dry_run"
    assert evidence["decision"] == "STOP"
    assert evidence["side_effect_requested"] == "git_push"
    assert evidence["guarded_command"] == "git push"
    assert evidence["would_run_git_push"] is False
    assert evidence["performed_actions_empty"] is True
    assert evidence["output_capture"] == "selected_fields"
    assert evidence["preflight_integration_status"] == "receipt-summary-only"
    assert evidence["local_verify_run_id"] == PHASE_9Y1_RUN_ID
    assert evidence["local_verify_job_id"] == PHASE_9Y1_JOB_ID


def test_receipt_does_not_embed_recursive_phase_9y_post_push_local_verify() -> None:
    text = receipt_text()
    receipt = receipt_json()
    evidence = receipt["hermes_git_push_preflight_evidence"]

    assert PHASE_9Y_COMMIT not in text
    assert PHASE_9Y_RUN_ID not in text
    assert PHASE_9Y_JOB_ID not in text
    assert evidence["observed_head_commit"] != PHASE_9Y_COMMIT
    assert evidence["local_verify_run_id"] != PHASE_9Y_RUN_ID
    assert evidence["local_verify_job_id"] != PHASE_9Y_JOB_ID
    assert "future post-push Local Verify run" in text


def test_receipt_has_final_newline_and_safe_repo_relative_refs_only() -> None:
    text = receipt_text()
    receipt = receipt_json()
    evidence = receipt["hermes_git_push_preflight_evidence"]
    approval = receipt["approval"]
    safety = receipt["safety"]

    assert text.endswith("\n")
    assert "\r" not in text

    refs = evidence["evidence_refs"]
    assert refs == [
        "docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_POLICY.md",
        "docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_CONTRACT.md",
    ]
    assert all(isinstance(ref, str) for ref in refs)
    assert all(not ref.startswith(("/", "\\")) for ref in refs)
    assert all("\\" not in ref for ref in refs)
    assert all(".." not in Path(ref).parts for ref in refs)

    assert approval["approval_class"] == "owner_approved_local_commit"
    assert "\n" not in approval["approval_reference"]
    assert len(approval["approval_reference"]) <= 120
    assert safety["redaction_status"]["status"] == "approved_summary_only"
    assert "safe summaries" in safety["redaction_status"]["notes"]

    # The receipt may name excluded material in safety summaries, but it must
    # not store concrete local paths, URLs, account handles, or token-like data.
    assert ":\\" not in text
    assert "http://" not in text
    assert "https://" not in text
    assert "@" not in text
    assert "gho_" not in text
    assert "ghp_" not in text
    assert "sk-" not in text


def test_review_verification_failure_modes_non_goals_and_next_step_are_bounded() -> None:
    text = review_text()
    safety = normalize_ws(section(text, "Safety And Redaction Review"))
    boundary = normalize_ws(section(text, "Boundary Checks"))
    failure = section(text, "Failure Modes")
    verification = section(text, "Verification")
    non_goals = normalize_ws(section(text, "Non-goals"))
    next_step = normalize_ws(section(text, "Next Step"))

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
        assert forbidden_material in safety

    for expected in [
        "Exactly one tracked receipt exists",
        "exact Phase 9X-approved path",
        "not-run, `STOP` evidence",
        "No same-commit Local Verify identifiers",
        "not by mutating the receipt",
    ]:
        assert expected in boundary

    for status in ["`PASS`", "`PASS WITH NOTES`", "`BLOCKED`", "`FAIL`", "`NOT RUN`", "`ENVIRONMENT BLOCKED`"]:
        assert status in failure

    for command in [
        "python -m pytest tests/test_hermes_git_push_preflight_tracked_receipt_post_generation_review.py",
        "python -m pytest tests/test_hermes_git_push_preflight_tracked_receipt_contract.py",
        "python -m pytest tests/test_hermes_git_push_preflight_tracked_receipt_policy.py",
        "python -m pytest tests/test_json_evidence_gate.py",
        "python -m pytest tests",
        "python scripts/quality_gate.py",
        "git diff --check",
        "git ls-files --others --exclude-standard",
    ]:
        assert command in verification

    for forbidden_scope in [
        "edit the Phase 9Y receipt file",
        "generate or replace a receipt file",
        "change `STATUS.md` or `ACCEPTANCE_TRACE.md`",
        "change `scripts/hermes_git_push_preflight_receipt_writer.py`",
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

    assert "pause before any trace, audit, CI, MCP, runtime, release, artifact, or downstream persistence" in next_step
    assert "Phase 9Z does not authorize durable trace writing" in next_step
