from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts import hermes_sidecar as sidecar


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO_ROOT / "docs" / "HERMES_PREFLIGHT_SYNTHETIC_MATRIX_REVIEW.md"
CONTRACT_PATH = REPO_ROOT / "docs" / "HERMES_PREFLIGHT_USE_PLANNING_CONTRACT.md"

ALLOWED_SCHEMA_VERSION = sidecar.SCHEMA_VERSION
ALLOWED_MODE = "no_op"
ALLOWED_STATUSES = {"PASS_WITH_NOTES", "BLOCKED", "NOT_RUN", "ENVIRONMENT_BLOCKED"}


def review_text() -> str:
    return REVIEW_PATH.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def synthetic_preflight_decision(
    payload: dict[str, Any], *, approved_evidence_scope: set[str] | None = None
) -> str:
    approved_evidence_scope = approved_evidence_scope or set()

    if payload.get("schema_version") != ALLOWED_SCHEMA_VERSION:
        return "STOP"
    if payload.get("mode") != ALLOWED_MODE:
        return "STOP"
    if payload.get("status") not in ALLOWED_STATUSES:
        return "STOP"
    if payload.get("performed_actions") != []:
        return "STOP"

    evidence_refs = payload.get("evidence_refs")
    if not isinstance(evidence_refs, list):
        return "STOP"
    for evidence_ref in evidence_refs:
        if not isinstance(evidence_ref, dict):
            return "STOP"
        if evidence_ref.get("path") not in approved_evidence_scope:
            return "STOP"

    if payload.get("status") in {"BLOCKED", "NOT_RUN", "ENVIRONMENT_BLOCKED"}:
        return "STOP"

    if (
        payload.get("status") == "PASS_WITH_NOTES"
        and payload.get("side_effect_requested") == "none"
    ):
        return "ADVISORY_ONLY"

    return "STOP"


def test_review_documents_required_preflight_matrix_cases() -> None:
    text = review_text()
    matrix = normalize_ws(section(text, "Synthetic Decision Matrix"))
    checks = normalize_ws(section(text, "Synthetic Result Checks"))

    for expected_case in [
        "advisory/no side-effect request",
        "missing approval for side-effect request",
        "approval present but executor absent",
        "unsafe/private/raw input",
        "invalid or out-of-scope evidence path",
        "unexpected `schema_version`",
        "unexpected `mode`",
        "unexpected `status`",
        "non-empty `performed_actions`",
        "evidence refs outside approved scope",
        "future side-effect request",
    ]:
        assert expected_case in matrix

    for required_decision in [
        "`ADVISORY_ONLY`",
        "`STOP`",
        "side-effect execution still requires separate approval",
    ]:
        assert required_decision in matrix or required_decision in checks


def test_review_preserves_phase_9h_contract_and_non_goals() -> None:
    text = review_text()
    basis = normalize_ws(section(text, "Review Basis"))
    non_goals = normalize_ws(section(text, "Non-goals"))
    contract = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "`docs/HERMES_PREFLIGHT_USE_PLANNING_CONTRACT.md`" in basis
    assert "The next safe Hermes task after Phase 9H is a synthetic preflight matrix review" in contract

    for forbidden_scope in [
        "implement a preflight caller or wrapper",
        "modify `scripts/hermes_sidecar.py`",
        "add a machine-readable JSON Schema artifact",
        "connect Hermes to MCP, quality gates, CI",
        "audit automation",
        "release automation",
        "downstream repositories",
        "raw prompts",
        "unredacted tool-call bodies",
        "local absolute paths",
    ]:
        assert forbidden_scope in non_goals


def test_advisory_no_side_effect_request_is_advisory_only(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary="Review preflight matrix",
        repo_root=tmp_path,
    )

    assert payload["status"] == "PASS_WITH_NOTES"
    assert payload["side_effect_requested"] == "none"
    assert payload["performed_actions"] == []
    assert synthetic_preflight_decision(payload) == "ADVISORY_ONLY"


def test_missing_approval_for_side_effect_stops_future_caller(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary="Prepare documentation edit",
        side_effect="file_write",
        repo_root=tmp_path,
    )

    assert payload["status"] == "BLOCKED"
    assert payload["reason_code"] == "approval_blocked"
    assert synthetic_preflight_decision(payload) == "STOP"


def test_approved_side_effect_without_executor_stays_not_run(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary="Prepare documentation edit",
        side_effect="file_write",
        approval_ref="phase-9i-review",
        repo_root=tmp_path,
    )

    assert payload["status"] == "NOT_RUN"
    assert payload["reason_code"] == "policy_blocked"
    assert payload["approval_ref_present"] is True
    assert payload["performed_actions"] == []
    assert "separate executor task" in payload["next_step"]
    assert synthetic_preflight_decision(payload) == "STOP"


def test_unsafe_private_raw_input_stops_and_is_not_echoed(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary=r"Use C:\Users\name\secret.txt token=abc123",
        repo_root=tmp_path,
    )

    encoded = repr(payload)
    assert payload["status"] == "BLOCKED"
    assert payload["reason_code"] == "unsafe_input"
    assert payload["safe_task_summary"] == "[blocked unsafe input]"
    assert "abc123" not in encoded
    assert "secret.txt" not in encoded
    assert synthetic_preflight_decision(payload) == "STOP"


def test_invalid_or_out_of_scope_evidence_stops_future_caller(tmp_path: Path) -> None:
    missing_payload = sidecar.assess_request(
        task_summary="Review missing evidence",
        evidence_paths=["docs/MISSING.md"],
        repo_root=tmp_path,
    )
    invalid_payload = sidecar.assess_request(
        task_summary="Review invalid evidence",
        evidence_paths=["private/raw.md"],
        repo_root=tmp_path,
    )

    assert missing_payload["status"] == "BLOCKED"
    assert missing_payload["reason_code"] == "source_basis_blocked"
    assert invalid_payload["status"] == "BLOCKED"
    assert invalid_payload["reason_code"] == "unsafe_input"
    assert synthetic_preflight_decision(missing_payload) == "STOP"
    assert synthetic_preflight_decision(invalid_payload) == "STOP"


def test_unexpected_schema_mode_or_status_stops_future_caller(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary="Review preflight matrix",
        repo_root=tmp_path,
    )

    wrong_schema = dict(payload, schema_version="hermes_sidecar_noop.v1")
    wrong_mode = dict(payload, mode="execute")
    wrong_status = dict(payload, status="PASS")

    assert synthetic_preflight_decision(wrong_schema) == "STOP"
    assert synthetic_preflight_decision(wrong_mode) == "STOP"
    assert synthetic_preflight_decision(wrong_status) == "STOP"


def test_non_empty_performed_actions_is_contract_violation(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary="Review preflight matrix",
        repo_root=tmp_path,
    )
    mutated = dict(payload, performed_actions=["file_write"])

    assert synthetic_preflight_decision(mutated) == "STOP"


def test_evidence_refs_outside_approved_scope_stop_future_caller(tmp_path: Path) -> None:
    evidence_path = tmp_path / "docs" / "EVIDENCE.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("# Evidence\n", encoding="utf-8")

    payload = sidecar.assess_request(
        task_summary="Review preflight matrix",
        evidence_paths=["docs/EVIDENCE.md"],
        repo_root=tmp_path,
    )
    mutated = dict(payload, evidence_refs=[{"path": "docs/OTHER.md", "exists": True}])

    assert synthetic_preflight_decision(
        payload, approved_evidence_scope={"docs/EVIDENCE.md"}
    ) == "ADVISORY_ONLY"
    assert synthetic_preflight_decision(
        mutated, approved_evidence_scope={"docs/EVIDENCE.md"}
    ) == "STOP"


def test_phase_9i_does_not_add_runtime_or_integration_paths() -> None:
    forbidden_paths = [
        REPO_ROOT / "hermes",
        REPO_ROOT / "sidecar",
        REPO_ROOT / "mcp_server",
        REPO_ROOT / "scripts" / "hermes_preflight.py",
        REPO_ROOT / "scripts" / "hermes_mcp_server.py",
        REPO_ROOT / "scripts" / "mcp_server.py",
        REPO_ROOT / ".github" / "workflows" / "hermes.yml",
        REPO_ROOT / ".github" / "workflows" / "mcp.yml",
    ]

    for forbidden_path in forbidden_paths:
        assert not forbidden_path.exists(), f"unexpected runtime path: {forbidden_path}"
