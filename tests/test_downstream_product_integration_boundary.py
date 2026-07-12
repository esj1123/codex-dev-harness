from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "docs" / "DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md"


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


def test_phase_11a_scope_basis_and_decision_are_documented() -> None:
    text = boundary_text()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = section(text, "Allowed Files")
    basis = section(text, "Basis")
    decision = normalize_ws(section(text, "Boundary Decision"))

    assert "Phase 11A is documentation and focused contract-test only" in purpose
    assert "No downstream repository, worktree, branch, path, remote" in purpose
    assert "`downstream_product_integration_boundary_documented_without_downstream_access`" in decision
    assert "does not authorize downstream access or integration" in decision

    for allowed_file in [
        "docs/DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md",
        "tests/test_downstream_product_integration_boundary.py",
    ]:
        assert f"`{allowed_file}`" in allowed

    for no_touch in [
        "`STATUS.md`",
        "`ACCEPTANCE_TRACE.md`",
        "`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`",
        "`.github/workflows`",
        "scripts",
        "schemas",
        "artifacts",
        "existing downstream records",
    ]:
        assert no_touch in allowed

    for basis_item in [
        "AGENTS.md",
        "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
        "docs/SAFETY_POLICY.md",
        "docs/AI_HANDOFF.md",
        "docs/LOCAL_DOWNSTREAM_ADOPTION_PLAN.md",
        "docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md",
        "docs/DOWNSTREAM_READINESS_PROMPT_USE_VALIDATION.md",
        "docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md",
        "docs/RELEASE_EVIDENCE_REFRESH_DECISION.md",
        "6aabb2a681528b1a2c6e02f2ecadb56b025bf66e",
        "29159465667",
        "86561923928",
    ]:
        assert f"`{basis_item}`" in basis


def test_authority_and_future_task_contract_fail_closed() -> None:
    text = boundary_text()
    authority = normalize_ws(section(text, "Authority Model"))
    contract = normalize_ws(section(text, "Required Downstream Task Contract"))

    for authority_rule in [
        "explicit owner approval",
        "downstream repository's local instructions",
        "downstream repository's branch, worktree, review, and release rules",
        "this harness boundary and its safety policies",
        "most restrictive applicable rule",
    ]:
        assert authority_rule in authority

    assert "Harness guidance cannot override or broaden downstream repository authority" in authority
    assert "Read access does not imply write access" in authority
    assert "push does not imply pull request, merge, release, deployment, or live action" in authority

    for required_item in [
        "owner-approved repository identifier",
        "access class: local read-only, remote read-only, local write, or remote write",
        "approved clone or worktree boundary",
        "expected branch, base commit, HEAD, upstream",
        "exact allowed files and explicit no-touch paths",
        "exact commands",
        "allowed data classes and forbidden private or live data",
        "target-repository approvals and the approval reference",
        "verification commands and truthful `NOT RUN` items",
        "rollback, cleanup, retention, and overwrite rules",
        "commit, push, pull request, merge, release, deployment",
        "closeout fields, safe evidence references, and stop conditions",
    ]:
        assert required_item in contract

    assert "downstream work is `BLOCKED` and no access occurs" in contract


def test_data_and_evidence_boundary_blocks_raw_or_sensitive_material() -> None:
    evidence = normalize_ws(section(boundary_text(), "Data And Evidence Boundary"))

    for allowed_summary in [
        "owner-approved generalized identifiers",
        "repo-relative file references",
        "commit identifiers",
        "bounded status and reason codes",
        "short safe summary",
    ]:
        assert allowed_summary in evidence

    for forbidden_material in [
        "private repository names or remote URLs",
        "local absolute paths or user/account identifiers",
        "raw source files, full diffs, patches, archives, or generated applications",
        "prompts, approval text, transcripts, raw stdout or stderr",
        "secrets, tokens, credentials, cookies, keys, connection strings",
        "customer, employee, account, broker, financial",
        "IP addresses, ports, endpoints, live configuration, device values",
        "raw audit, receipt, trace, RAG, RSID, or study evidence",
    ]:
        assert forbidden_material in evidence

    assert "without echoing a sensitive matched value" in evidence
    assert "not proof that private data or secrets are absent" in evidence
    assert "No downstream evidence is written to `artifacts/`" in evidence


def test_repository_side_effects_and_failure_modes_stay_separate() -> None:
    text = boundary_text()
    side_effects = normalize_ws(section(text, "Repository And Side-Effect Boundary"))
    failure = normalize_ws(section(text, "Failure Modes"))

    for operation_class in [
        "locating or opening a local downstream repository",
        "cloning, fetching, pulling, checking out, or creating a worktree",
        "reading a private repository or calling a remote repository API",
        "installing dependencies, building, testing, executing hooks",
        "rendering, generating, editing, deleting, moving, or overwriting files",
        "staging, committing, amending, rebasing, resetting, or merging",
        "pushing, force-pushing, opening or updating a pull request",
        "dispatching workflows, uploading artifacts, signing, tagging, releasing",
        "calling MCP, Hermes, AgentOps, memory, external services",
    ]:
        assert operation_class in side_effects

    assert "must separately authorize each applicable class" in side_effects
    assert "remain forbidden unless an exact owner approval names the operation and target" in side_effects

    for status in [
        "`PASS`",
        "`PASS WITH NOTES`",
        "`BLOCKED`",
        "`FAIL`",
        "`NOT RUN`",
        "`ENVIRONMENT BLOCKED`",
    ]:
        assert status in failure

    for failure_mode in [
        "Missing approval",
        "wrong repository",
        "stale branch",
        "unexpected dirty state",
        "allowed-file drift",
        "instruction conflict",
        "unauthorized network access",
        "cleanup failure",
        "unapproved remote or live side effect",
    ]:
        assert failure_mode in failure


def test_verification_non_goals_and_next_step_remain_synthetic_only() -> None:
    text = boundary_text()
    checks = normalize_ws(section(text, "Boundary Checks"))
    verification = section(text, "Verification")
    non_goals = normalize_ws(section(text, "Non-goals"))
    next_step = normalize_ws(section(text, "Next Step"))

    for boundary_check in [
        "no downstream repository or product is selected",
        "downstream repository rules remain authoritative",
        "future task contracts fail closed",
        "downstream data is not copied into harness records",
        "permissions remain distinct",
        "release evidence refresh remains `HOLD`",
    ]:
        assert boundary_check in checks

    for command in [
        "python -m pytest tests/test_downstream_product_integration_boundary.py",
        "python -m pytest tests",
        "python scripts/quality_gate.py",
        "python scripts/generate_checksums.py --verify",
        "python scripts/generate_corpus_digest.py --check --json",
        "git diff --check",
        "git ls-files --others --exclude-standard",
    ]:
        assert f"`{command}`" in verification

    assert "`python scripts/run_eval.py` is `NOT RUN`" in verification

    for forbidden_scope in [
        "select, locate, clone, fetch, inspect, or modify a downstream repository",
        "render templates into a downstream target",
        "add a downstream profile or example",
        "read or persist private downstream data",
        "create a receipt, trace, audit log, artifact, report, or release archive",
        "regenerate the corpus digest, release evidence, or eval report",
        "change scripts, schemas, gates, workflows, templates, profiles, or examples",
        "execute MCP or Hermes",
        "stage, commit, push, open a pull request, tag, release, publish, deploy",
    ]:
        assert forbidden_scope in non_goals

    assert "separately approved Phase 11B task" in next_step
    for placeholder in [
        "<DOWNSTREAM_REPO_ID>",
        "<APPROVED_WORKTREE>",
        "<WORKING_BRANCH>",
        "<ALLOWED_FILE_LIST>",
    ]:
        assert f"`{placeholder}`" in next_step
    assert "must not locate, read, clone, fetch, render into, or modify a real downstream repository" in next_step
