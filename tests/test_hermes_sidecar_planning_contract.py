from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "HERMES_SIDECAR_PLANNING_CONTRACT.md"
MCP_CONTRACT_PATH = REPO_ROOT / "docs" / "MCP_TOOL_BOUNDARY_CONTRACT.md"


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


def test_current_scope_excludes_runtime_and_integrations() -> None:
    current_scope = normalize_ws(section(contract_text(), "Current Scope"))

    for allowed_planning_item in [
        "document the sidecar responsibility model",
        "document local-first constraints",
        "document approval and no-op boundaries",
        "document safe input and output evidence shapes",
        "document failure modes and future verification expectations",
    ]:
        assert allowed_planning_item in current_scope

    for forbidden_runtime_item in [
        "Hermes sidecar runtime",
        "background daemon, service manager, scheduler, socket server, or HTTP server",
        "MCP runtime, MCP server, tool execution, or tool-call dispatch",
        "quality-gate or CI integration",
        "audit automation, real receipt generation, or real trace/log writing",
        "external service call, network broker, or live endpoint integration",
        "PLC, device, account, downstream repository, or release mutation",
        "AgentOps, memory runtime, or persistent execution state",
        "artifact, digest, release evidence, tag, publication, or upload generation",
        "dependency changes",
    ]:
        assert forbidden_runtime_item in current_scope


def test_sidecar_stays_downstream_of_mcp_and_existing_policies() -> None:
    relationship = normalize_ws(
        section(contract_text(), "Relationship To Existing Boundaries")
    )

    assert MCP_CONTRACT_PATH.exists()
    assert "downstream of the MCP tool boundary" in relationship
    assert "cannot widen the allowed MCP tool classes" in relationship
    assert "approval rules, redaction rules, or evidence hooks" in relationship

    for policy_path in [
        "`docs/SAFETY_POLICY.md`",
        "`docs/AUDIT_TRACE_SCHEMA.md`",
        "`docs/JSON_EVIDENCE_POLICY.md`",
        "`docs/EVAL_REPORT_INTEGRATION_PLAN.md`",
        "`docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md`",
        "`docs/RETRIEVAL_RECEIPT_EVIDENCE_PLAN.md`",
        "`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`",
    ]:
        assert policy_path in relationship

    assert "safer and more restrictive rule applies" in relationship


def test_responsibility_model_is_planning_not_implicit_task_running() -> None:
    responsibility = normalize_ws(section(contract_text(), "Responsibility Model"))

    for limited_responsibility in [
        "reading explicit local request metadata",
        "checking policy boundaries",
        "producing dry-run plans and bounded status summaries",
        "repo-relative evidence paths",
        "commit identifiers",
        "hash identifiers",
        "reporting fail-closed outcomes",
    ]:
        assert limited_responsibility in responsibility

    for prohibited_behavior in [
        "must not become an implicit task runner",
        "must not infer approval from prior tasks",
        "perform hidden background work",
        "bypass user approval",
        "downstream repository rules",
        "safety invariants",
    ]:
        assert prohibited_behavior in responsibility


def test_input_boundary_forbids_sensitive_live_and_private_inputs() -> None:
    input_boundary = normalize_ws(section(contract_text(), "Input Boundary"))

    for allowed_input in [
        "repo-relative paths to approved repository files",
        "existing receipt or trace identifiers",
        "commit hashes or documented artifact hashes",
        "sanitized task summaries",
        "owner approval references for a specific side effect",
        "dry-run configuration values",
    ]:
        assert allowed_input in input_boundary

    for forbidden_input in [
        "raw prompts",
        "private data",
        "raw command logs",
        "model output transcripts",
        "unredacted tool-call bodies",
        "secrets",
        "credentials",
        "tokens",
        "account values",
        "IPs",
        "ports",
        "live config",
        "device values",
        "local absolute paths",
        "private raw corpus",
        "`08_Study` raw notes",
        "RSID raw evidence",
        "downstream raw evidence",
        "unapproved downstream repository files",
        "hidden environment state",
    ]:
        assert forbidden_input in input_boundary


def test_output_boundary_is_bounded_and_redacted() -> None:
    output_boundary = normalize_ws(section(contract_text(), "Output Boundary"))

    for safe_output in [
        "`PASS`, `PASS WITH NOTES`, `BLOCKED`, `NOT RUN`, `ENVIRONMENT BLOCKED`, or `FAIL`-style status values",
        "repo-relative evidence paths",
        "commit hashes and content hashes",
        "counts, redacted summaries, and reason codes",
        "explicit approval state for side effects",
        "safe next-step recommendations",
    ]:
        assert safe_output in output_boundary

    for forbidden_output in [
        "raw prompts",
        "private data",
        "raw command logs",
        "unredacted tool-call bodies",
        "secrets",
        "account values",
        "IPs",
        "ports",
        "live config",
        "device values",
        "local absolute paths",
        "generated downstream source",
    ]:
        assert forbidden_output in output_boundary


def test_approval_boundary_requires_explicit_side_effect_approval() -> None:
    approval = normalize_ws(section(contract_text(), "Approval Boundary"))

    assert (
        "may not treat planning, dry-run output, documentation approval, or previous task approval as permission"
        in approval
    )

    for side_effect in [
        "write files",
        "stage, commit, push, tag, publish, upload, or release",
        "run external network calls",
        "call or execute MCP tools",
        "mutate a downstream repository",
        "generate audit receipts, trace events, logs, digests, or release artifacts",
        "start a persistent process or background service",
    ]:
        assert side_effect in approval

    assert (
        "specific to the side effect, target, expected output, cleanup rule, and verification rule"
        in approval
    )


def test_failure_behavior_defaults_to_no_op_and_fails_closed() -> None:
    failure = normalize_ws(section(contract_text(), "Failure And No-op Behavior"))

    assert "The default sidecar behavior must be no-op" in failure
    assert "outside the current approval" in failure
    assert "blocked or not-run result" in failure

    for status in [
        "`blocked`",
        "`not_run`",
        "`environment_blocked`",
        "`no_sufficient_evidence`",
        "`fail`",
    ]:
        assert status in failure

    assert "minimum safe summary" in failure


def test_future_verification_remains_synthetic_before_runtime() -> None:
    verification = normalize_ws(
        section(contract_text(), "Future Verification Expectations")
    )
    next_step = normalize_ws(section(contract_text(), "Next Step"))

    for expected_check in [
        "focused synthetic tests before any real sidecar behavior",
        "dry-run only behavior",
        "fail-closed approval handling",
        "forbidden input rejection",
        "bounded output and redaction",
        "no background process or always-on service",
        "no external call by default",
        "no MCP runtime or tool execution unless separately approved",
        "no quality-gate, CI, release, audit, or downstream integration by default",
    ]:
        assert expected_check in verification

    assert (
        "should not generate receipt, trace, digest, release, or downstream artifacts"
        in verification
    )
    assert "synthetic review of this contract" in next_step
    assert "must still not implement Hermes sidecar runtime behavior" in next_step


def test_no_runtime_sidecar_entrypoints_are_present() -> None:
    forbidden_paths = [
        REPO_ROOT / "scripts" / "hermes_sidecar.py",
        REPO_ROOT / "scripts" / "hermes.py",
        REPO_ROOT / "hermes",
        REPO_ROOT / "sidecar",
        REPO_ROOT / "mcp_server",
        REPO_ROOT / ".github" / "workflows" / "hermes.yml",
    ]

    for forbidden_path in forbidden_paths:
        assert not forbidden_path.exists(), f"unexpected runtime path: {forbidden_path}"
