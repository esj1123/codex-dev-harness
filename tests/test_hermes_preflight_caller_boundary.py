from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "docs" / "HERMES_PREFLIGHT_CALLER_IMPLEMENTATION_BOUNDARY.md"


def boundary_text() -> str:
    return BOUNDARY_PATH.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def test_boundary_documents_basis_and_documentation_only_scope() -> None:
    text = boundary_text()
    basis = section(text, "Boundary Basis")
    purpose = normalize_ws(section(text, "Purpose"))

    for basis_path in [
        "docs/HERMES_PREFLIGHT_USE_PLANNING_CONTRACT.md",
        "docs/HERMES_PREFLIGHT_SYNTHETIC_MATRIX_REVIEW.md",
        "docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md",
        "docs/HERMES_MCP_SECURITY_ALIGNMENT_REVIEW.md",
        "docs/MCP_TOOL_BOUNDARY_CONTRACT.md",
        "docs/JSON_EVIDENCE_POLICY.md",
        "scripts/hermes_sidecar.py",
    ]:
        assert f"`{basis_path}`" in basis

    for forbidden_scope in [
        "does not implement a caller",
        "execution bridge",
        "MCP runtime",
        "quality-gate hook",
        "CI hook",
        "audit automation",
        "real receipt generation",
        "external service call",
        "downstream integration",
    ]:
        assert forbidden_scope in purpose


def test_boundary_requires_exact_future_approval_details() -> None:
    text = boundary_text()
    shape = normalize_ws(section(text, "Future Caller Shape"))

    for required_detail in [
        "exact caller file or script",
        "exact side-effect class",
        "exact command or action",
        "exact result fields checked",
        "persistence rule",
        "cleanup rule",
        "verification commands",
        "forbidden inputs",
        "forbidden outputs",
        "must not execute the guarded action",
    ]:
        assert required_detail in shape


def test_boundary_lists_required_result_fields_and_fail_closed_decisions() -> None:
    text = boundary_text()
    required_fields = section(text, "Required Field Checks")
    decisions = normalize_ws(section(text, "Caller Decisions"))

    for field in [
        "schema_version",
        "mode",
        "status",
        "reason_code",
        "side_effect_requested",
        "approval_ref_present",
        "safe_task_summary",
        "evidence_refs",
        "performed_actions",
        "safety_notes",
        "next_step",
    ]:
        assert f"`{field}`" in required_fields

    assert "`ADVISORY_ONLY`" in decisions
    assert "`STOP`" in decisions
    assert "does not define an `ALLOW_EXECUTION` decision" in decisions


def test_boundary_stop_conditions_block_execution_and_fallbacks() -> None:
    text = boundary_text()
    stops = normalize_ws(section(text, "Stop Conditions"))

    for required_stop in [
        "`schema_version` is not the current approved no-op schema version",
        "`mode` is not `no_op`",
        "`status` is `BLOCKED`, `NOT_RUN`, `ENVIRONMENT_BLOCKED`",
        "`side_effect_requested` is anything other than `none`",
        "`approval_ref_present` is false",
        "`evidence_refs` contains missing, malformed, absolute, traversal",
        "`performed_actions` is non-empty",
        "must not fall back to looser parsing",
        "broader filesystem access",
        "tool execution",
        "external calls",
        "generated evidence",
    ]:
        assert required_stop in stops


def test_boundary_persistence_defaults_to_in_memory_and_sanitized_only() -> None:
    text = boundary_text()
    persistence = normalize_ws(section(text, "Persistence And Cleanup"))

    for required_rule in [
        "keep the Hermes result in memory only",
        "must not write receipt files",
        "trace files",
        "audit logs",
        "raw command logs",
        "generated reports",
        "digest artifacts",
        "release artifacts",
        "exact output path",
        "retention expectation",
        "redaction rule",
        "cleanup rule",
        "Temporary files",
        "removed or reported before closeout",
    ]:
        assert required_rule in persistence


def test_boundary_verification_and_non_goals_prevent_runtime_expansion() -> None:
    text = boundary_text()
    verification = normalize_ws(section(text, "Verification Requirements"))
    non_goals = normalize_ws(section(text, "Non-goals"))

    for required_case in [
        "advisory/no-side-effect output remains advisory only",
        "missing side-effect approval returns a stop decision",
        "approved side-effect requests still stop",
        "unsafe input and unsafe evidence stop",
        "unexpected `schema_version`, `mode`, `status`, `reason_code`",
        "non-empty `performed_actions` stops",
        "evidence outside the active approval scope stops",
        "no tool, MCP, Git, release, audit, external, downstream",
    ]:
        assert required_case in verification

    for forbidden_scope in [
        "implement a preflight caller or wrapper",
        "change `scripts/hermes_sidecar.py`",
        "add a machine-readable JSON Schema artifact",
        "connect Hermes to MCP, quality gates, CI",
        "execute tools",
        "start servers",
        "create background processes",
        "stage changes",
        "commit changes",
        "push changes",
        "generate receipt, trace, audit log, digest, release",
        "raw prompts",
        "unredacted tool-call bodies",
        "local absolute paths",
        "downstream raw evidence",
    ]:
        assert forbidden_scope in non_goals


def test_phase_9j_does_not_add_caller_runtime_or_integration_paths() -> None:
    forbidden_paths = [
        REPO_ROOT / "scripts" / "hermes_preflight_caller.py",
        REPO_ROOT / "scripts" / "hermes_preflight.py",
        REPO_ROOT / "scripts" / "hermes_mcp_server.py",
        REPO_ROOT / "scripts" / "mcp_server.py",
        REPO_ROOT / "hermes",
        REPO_ROOT / "sidecar",
        REPO_ROOT / "mcp_server",
        REPO_ROOT / ".github" / "workflows" / "hermes-preflight.yml",
        REPO_ROOT / ".github" / "workflows" / "hermes.yml",
        REPO_ROOT / ".github" / "workflows" / "mcp.yml",
    ]

    for forbidden_path in forbidden_paths:
        assert not forbidden_path.exists(), f"unexpected runtime path: {forbidden_path}"
