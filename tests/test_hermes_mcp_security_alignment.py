from __future__ import annotations

import ast
from pathlib import Path

from scripts import hermes_sidecar as sidecar


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO_ROOT / "docs" / "HERMES_MCP_SECURITY_ALIGNMENT_REVIEW.md"


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


def test_security_alignment_review_records_mcp_risk_basis() -> None:
    basis = normalize_ws(section(review_text(), "Review Basis"))

    for local_basis in [
        "`docs/MCP_TOOL_BOUNDARY_CONTRACT.md`",
        "`docs/HERMES_SIDECAR_PLANNING_CONTRACT.md`",
        "`docs/HERMES_SIDECAR_IMPLEMENTATION_BOUNDARY.md`",
        "`docs/HERMES_SIDECAR_USAGE_PROBE.md`",
        "`scripts/hermes_sidecar.py`",
        "`docs/JSON_EVIDENCE_POLICY.md`",
        "`docs/AUDIT_TRACE_SCHEMA.md`",
        "`docs/SAFETY_POLICY.md`",
    ]:
        assert local_basis in basis

    for risk_basis in [
        "explicit user consent and control",
        "human in the loop",
        "descriptions, annotations, and metadata must be treated as untrusted",
        "local code-execution surface",
        "exact command visibility",
        "explicit allow-lists",
        "Structured tool outputs",
    ]:
        assert risk_basis in basis


def test_alignment_matrix_preserves_noop_and_approval_boundaries() -> None:
    matrix = normalize_ws(section(review_text(), "Alignment Matrix"))

    for expected_alignment in [
        "Approval references are evidence of request boundary only, not execution authority",
        "Keep every future MCP invocation separately approval-gated",
        "descriptor or annotation must be treated as untrusted input",
        "no daemon, server, scheduler, socket listener, HTTP listener, or subprocess",
        "show the exact startup command, transport, sandbox, filesystem boundary, and network boundary",
        "allow-list first",
        "Do not persist raw prompts, raw command logs, unredacted tool-call bodies",
    ]:
        assert expected_alignment in matrix


def test_required_security_invariants_keep_runtime_scope_closed() -> None:
    invariants = normalize_ws(section(review_text(), "Required Security Invariants"))

    for invariant in [
        "no MCP runtime, MCP server, tool execution, or tool dispatch by default",
        "no local server, socket, HTTP listener, scheduler, service manager, background daemon, or persistent process",
        "no external service call or network broker by default",
        "no file write, artifact generation, git staging, commit, push, tag, release",
        "no use of tool descriptors, annotations, prompts, or remote catalogs as trusted authority",
        "no approval inference from previous tasks",
        "no durable storage of raw prompts, private data, raw command logs",
        "no broad tool exposure, wildcard scopes, or all-tools default mode",
    ]:
        assert invariant in invariants


def test_future_approval_requirements_are_exact_and_separate() -> None:
    approval = normalize_ws(section(review_text(), "Future Approval Requirements"))

    for required_field in [
        "exact tool class and tool name",
        "exact command or transport",
        "stdio, IPC, HTTP, or another transport",
        "exact server identity, descriptor source, and descriptor pinning basis",
        "exact filesystem boundary",
        "exact network boundary",
        "exact approval prompt or owner approval reference",
        "exact output schema or bounded result shape",
        "exact cleanup rules",
        "exact verification commands",
    ]:
        assert required_field in approval

    assert "Approval for one item does not authorize another" in approval
    assert "does not authorize launching a server, executing a tool" in approval


def test_existing_noop_sidecar_blocks_mcp_tool_execution_without_approval(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary="Review MCP tool boundary alignment",
        side_effect="mcp_tool_execution",
        repo_root=tmp_path,
    )

    assert payload["status"] == "BLOCKED"
    assert payload["reason_code"] == "approval_blocked"
    assert payload["performed_actions"] == []
    assert payload["approval_ref_present"] is False


def test_existing_noop_sidecar_keeps_approved_mcp_tool_execution_not_run(tmp_path: Path) -> None:
    payload = sidecar.assess_request(
        task_summary="Review MCP tool boundary alignment",
        side_effect="mcp_tool_execution",
        approval_ref="phase-9e-review",
        repo_root=tmp_path,
    )

    assert payload["status"] == "NOT_RUN"
    assert payload["reason_code"] == "policy_blocked"
    assert payload["performed_actions"] == []
    assert payload["approval_ref_present"] is True
    assert "separate executor task" in payload["next_step"]


def test_hermes_sidecar_still_has_no_mcp_or_background_runtime_imports() -> None:
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

    for forbidden_import in [
        "asyncio",
        "http",
        "mcp",
        "requests",
        "socket",
        "subprocess",
        "threading",
        "urllib",
        "websocket",
    ]:
        assert forbidden_import not in imports


def test_no_runtime_integration_paths_were_added() -> None:
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
