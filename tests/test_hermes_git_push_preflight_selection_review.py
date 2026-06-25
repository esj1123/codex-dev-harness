from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO_ROOT / "docs" / "HERMES_GIT_PUSH_PREFLIGHT_CALLER_SELECTION_REVIEW.md"


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


def test_review_documents_selection_scope_and_basis() -> None:
    text = review_text()
    purpose = normalize_ws(section(text, "Purpose"))
    basis = section(text, "Basis")

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

    for basis_path in [
        "docs/HERMES_PREFLIGHT_USE_PLANNING_CONTRACT.md",
        "docs/HERMES_PREFLIGHT_SYNTHETIC_MATRIX_REVIEW.md",
        "docs/HERMES_PREFLIGHT_CALLER_IMPLEMENTATION_BOUNDARY.md",
        "docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md",
        "scripts/hermes_sidecar.py",
    ]:
        assert f"`{basis_path}`" in basis


def test_review_selects_git_push_and_defers_broader_candidates() -> None:
    text = review_text()
    matrix = normalize_ws(section(text, "Candidate Matrix"))
    decision = normalize_ws(section(text, "Decision"))

    assert "| `git_push` | selected first candidate |" in section(text, "Candidate Matrix")
    assert "Decision: `select_git_push_preflight_candidate`" in decision
    assert "standalone dry-run preflight" in decision
    assert "side-effect class: `git_push`" in decision
    assert "execution authority: none" in decision

    for deferred in [
        "`git_commit` | defer",
        "`artifact_generation` | defer",
        "`mcp_tool_execution` | defer",
        "`audit_generation` | defer",
        "`external_call` | defer",
        "`release_publication` | defer",
        "`downstream_mutation` | defer",
        "`persistent_process` | defer",
    ]:
        assert deferred in matrix


def test_review_names_later_candidate_files_as_historical_phase_9k_scope() -> None:
    text = review_text()
    decision = normalize_ws(section(text, "Decision"))

    assert "candidate script: `scripts/hermes_git_push_preflight.py`" in decision
    assert "candidate tests: `tests/test_hermes_git_push_preflight.py`" in decision
    assert "This review does not create those files." in decision


def test_review_requires_fail_closed_memory_only_non_executing_behavior() -> None:
    text = review_text()
    behavior = normalize_ws(section(text, "Required Future Behavior"))

    for required_rule in [
        "use fail-closed decisions only: `STOP` or `ADVISORY_ONLY`",
        "never define `ALLOW_EXECUTION`",
        "never run `git push`",
        "never run `git add`, `git commit`, `git tag`, or release commands",
        "never dispatch workflows",
        "execute MCP tools",
        "keep any Hermes result memory-only",
        "stop on missing approval",
        "unexpected schema",
        "non-empty `performed_actions`",
        "out-of-scope evidence references",
    ]:
        assert required_rule in behavior


def test_review_phase_9l_approval_requirements_are_exact() -> None:
    text = review_text()
    approval = normalize_ws(section(text, "Approval Requirements For Phase 9L"))

    for required_detail in [
        "exact script path",
        "exact test path",
        "exact CLI arguments",
        "exact result fields checked",
        "exact synthetic fixtures",
        "whether JSON output is allowed",
        "whether any output may be persisted",
        "cleanup rules for temporary outputs",
        "verification commands",
        "Approval to implement the dry-run preflight caller must not authorize a real push",
    ]:
        assert required_detail in approval


def test_review_non_goals_prevent_runtime_and_side_effect_expansion() -> None:
    text = review_text()
    non_goals = normalize_ws(section(text, "Non-goals"))

    for forbidden_scope in [
        "create `scripts/hermes_git_push_preflight.py`",
        "create `tests/test_hermes_git_push_preflight.py`",
        "implement a preflight caller or wrapper",
        "change `scripts/hermes_sidecar.py`",
        "connect Hermes to `scripts/quality_gate.py`, CI, MCP",
        "run `git push`, `git add`, `git commit`, `git tag`",
        "workflow dispatch",
        "artifact upload",
        "MCP execution",
        "audit generation",
        "receipt generation",
        "trace writing",
        "downstream mutation",
        "generate or regenerate artifacts, digests",
        "raw prompts",
        "unredacted tool-call bodies",
        "local absolute paths",
        "downstream raw evidence",
    ]:
        assert forbidden_scope in non_goals


def test_review_next_step_remains_separately_approval_gated() -> None:
    text = review_text()
    verification = normalize_ws(section(text, "Verification"))

    assert "Phase 9K is accepted as `PASS WITH NOTES`" in verification
    assert "commit and push this selection review, then run clean Local Verify" in verification
    assert "separately approve Phase 9L" in verification
    assert "minimal standalone dry-run git-push preflight caller" in verification
    assert "may stop at the documented boundary" in verification
