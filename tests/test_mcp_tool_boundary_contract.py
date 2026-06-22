from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "MCP_TOOL_BOUNDARY_CONTRACT.md"


def contract_text() -> str:
    return CONTRACT_PATH.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def tool_class_rows() -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    policy_section = section(contract_text(), "3. Tool Class Policy")
    for raw_line in policy_section.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells == ["tool class", "default status", "boundary"]:
            continue
        tool_class, default_status, boundary = cells
        rows[tool_class] = {
            "default_status": default_status,
            "boundary": boundary,
        }
    return rows


def test_tool_class_matrix_defines_default_statuses() -> None:
    rows = tool_class_rows()

    expected_statuses = {
        "repository read-only inspection": "allowed when task-scoped",
        "local verification dry-runs": "allowed when non-mutating",
        "local file edits": "approval-gated",
        "artifact generation": "separately approval-gated",
        "git staging, commit, push, tag, or release": "separately approval-gated",
        "downstream repository work": "separately approval-gated",
        "external service or network calls": "forbidden by default",
        "live endpoint, device, PLC, broker, or account mutation": "forbidden by default",
        "installer, driver, DLL, binary, or unknown executable execution": "forbidden by default",
    }

    assert rows.keys() >= expected_statuses.keys()
    for tool_class, expected_status in expected_statuses.items():
        assert rows[tool_class]["default_status"] == expected_status


def test_approval_gated_classes_do_not_inherit_unrelated_side_effects() -> None:
    text = contract_text()
    approval_section = section(text, "6. Approval Boundary")

    assert "Approval for one side-effect class does not authorize another" in approval_section
    for side_effect in [
        "staging",
        "committing",
        "pushing",
        "creating artifacts",
        "running release automation",
        "calling external",
        "editing downstream",
    ]:
        assert side_effect in approval_section


def test_input_boundary_rejects_sensitive_live_and_private_values() -> None:
    input_section = section(contract_text(), "4. Input Boundary")

    forbidden_inputs = [
        "raw prompts",
        "prompt transcripts",
        "private raw data",
        "sensitive business source text",
        "raw command logs",
        "unredacted tool-call request or response bodies",
        "local absolute paths",
        "secrets",
        "tokens",
        "credentials",
        "account values",
        "IPs",
        "ports",
        "live endpoints",
        "live config",
        "device values",
        "raw downstream evidence",
        "RSID evidence",
        "`08_Study` raw notes",
    ]

    for forbidden_input in forbidden_inputs:
        assert forbidden_input in input_section
    assert "blocked or\nno-sufficient-evidence" in input_section


def test_output_and_redaction_boundaries_prefer_safe_summaries() -> None:
    text = contract_text()
    output_section = section(text, "5. Output Boundary")
    redaction_section = section(text, "7. Redaction Rules")

    for safe_output in [
        "PASS, PASS WITH NOTES, FAIL, BLOCKED, NOT RUN, or ENVIRONMENT BLOCKED",
        "short safe summaries",
        "repo-relative paths",
        "schema ids, receipt ids, trace ids, digest refs, commit ids, and SHA-256 hashes",
        "counts, statuses, and reason codes",
    ]:
        assert safe_output in output_section

    for unsafe_output in [
        "full private source text",
        "raw prompt transcripts",
        "raw command logs",
        "full tool-call bodies",
        "secrets or account values",
        "live config, IPs, ports, device values, or local absolute paths",
    ]:
        assert unsafe_output in output_section

    assert "identifiers, hashes, counts, status labels,\nand safe summaries" in redaction_section
    assert "report the\nlimit as a safety note instead of copying unsafe material" in redaction_section


def test_evidence_hooks_reference_receipts_and_traces_without_automation() -> None:
    evidence_section = section(contract_text(), "8. Evidence Hooks")

    for reference in [
        "`receipt_summary.receipt_id`",
        "`trace_event.event_id`",
        "`trace_event.related_receipt_id`",
        "repo-relative evidence paths",
        "SHA-256 hashes",
        "safe status and reason codes",
    ]:
        assert reference in evidence_section

    for forbidden_automation in [
        "does not create audit automation",
        "receipt generation",
        "trace file\ngeneration",
        "log writing",
    ]:
        assert forbidden_automation in evidence_section


def test_failure_handling_fails_closed_without_unapproved_fallbacks() -> None:
    failure_section = section(contract_text(), "9. Failure Handling")

    for status in [
        "`blocked`",
        "`no_sufficient_evidence`",
        "`not_run`",
        "`environment_blocked`",
    ]:
        assert status in failure_section

    for forbidden_fallback in [
        "widens file access",
        "calls external services",
        "writes artifacts",
        "performs side effects without\nseparate approval",
    ]:
        assert forbidden_fallback in failure_section


def test_non_goals_keep_runtime_and_integrations_out_of_scope() -> None:
    non_goals = section(contract_text(), "11. Explicit Non-Goals")

    forbidden_scope = [
        "implement MCP runtime",
        "implement Hermes sidecar behavior",
        "create MCP server code",
        "execute real tool calls",
        "add quality-gate or CI integration",
        "create audit automation",
        "generate real receipts, trace files, or logs",
        "regenerate release or digest artifacts",
        "create corpus, retrieval, or index folders",
        "call external services",
        "add AgentOps or memory runtime behavior",
        "edit downstream repositories",
        "publish, tag, release, upload, or deploy anything",
    ]

    for item in forbidden_scope:
        assert item in non_goals


def test_phase_8b_remains_synthetic_before_runtime_planning() -> None:
    next_step = section(contract_text(), "12. Next Step")

    assert "Phase 8B synthetic MCP\nboundary tests or review checks" in next_step
    assert "before any runtime planning" in next_step
    assert "Phase 9 Hermes sidecar planning should remain separate" in next_step
    assert "Neither next step is authorized by this document alone" in next_step
