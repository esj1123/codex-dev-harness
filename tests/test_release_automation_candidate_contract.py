from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "docs" / "RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md"


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


def test_phase_10b_scope_basis_and_decision_are_documented() -> None:
    text = contract_text()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = section(text, "Allowed Files")
    basis = section(text, "Basis")
    decision = normalize_ws(section(text, "Candidate Decision"))

    assert "Phase 10B is documentation and focused synthetic-test only" in purpose
    assert "does not implement a script" in purpose
    assert "`local_release_evidence_preflight_dry_run_candidate_selected_without_implementation`" in decision
    assert "does not authorize implementation" in decision

    for allowed_file in [
        "docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md",
        "tests/test_release_automation_candidate_contract.py",
    ]:
        assert f"`{allowed_file}`" in allowed

    for no_touch in [
        "`STATUS.md`",
        "`ACCEPTANCE_TRACE.md`",
        "`.github/workflows`",
        "scripts",
        "generated artifacts",
        "tags",
        "releases",
        "downstream repositories",
    ]:
        assert no_touch in allowed

    for basis_item in [
        "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
        "docs/CI_POLICY.md",
        "docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md",
        "docs/RELEASE_BUNDLE_POLICY.md",
        "docs/RELEASE_MANIFEST_POLICY.md",
        "docs/SBOM_PROVENANCE_PLAN.md",
        "scripts/run_release_verify.ps1",
        "scripts/generate_manifest.py",
        "scripts/generate_checksums.py",
        "scripts/generate_sbom.py",
        "scripts/generate_provenance.py",
        "tests/test_release_automation_provenance_boundary.py",
        "tests/test_generate_manifest.py",
        "tests/test_generate_checksums.py",
        "tests/test_generate_sbom.py",
        "tests/test_generate_provenance.py",
        "28830639298",
        "85503573430",
        "ca8c065fa72c3b7097f300d01ba71ee6d69f37ab",
    ]:
        assert f"`{basis_item}`" in basis


def test_selected_candidate_is_local_dry_run_preflight_only() -> None:
    selected = normalize_ws(section(contract_text(), "Selected Candidate"))

    assert "Candidate id: `local_release_evidence_preflight_dry_run`" in selected
    for expected in [
        "inspect repository state",
        "inspect configured local release evidence paths",
        "report whether release evidence generation would be blocked, ready, or not run",
        "produce a bounded dry-run summary only",
        "preserve source-basis, artifact-containing, push, tag, release, upload, and downstream states",
        "local-only, standard-library-only, and dry-run-only by default",
        "must not execute release evidence generators or release verification wrappers",
    ]:
        assert expected in selected


def test_future_implementation_contract_names_exact_files_and_command_placeholder() -> None:
    implementation = normalize_ws(section(contract_text(), "Future Implementation Contract"))

    for future_file in [
        "docs/RELEASE_AUTOMATION_PREFLIGHT_IMPLEMENTATION_PLAN.md",
        "scripts/release_evidence_preflight.py",
        "tests/test_release_evidence_preflight.py",
    ]:
        assert f"`{future_file}`" in implementation

    assert "`python scripts/release_evidence_preflight.py --repo-root . --dry-run --json`" in implementation
    assert "contract placeholder only" in implementation
    assert "Phase 10B does not create that script" in implementation
    assert "must not edit unrelated release generators" in implementation


def test_input_and_output_contracts_block_private_raw_and_persistent_outputs() -> None:
    input_contract = normalize_ws(section(contract_text(), "Input Contract"))
    output_contract = normalize_ws(section(contract_text(), "Output Contract"))

    for allowed_input in [
        "docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md",
        "docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md",
        "docs/RELEASE_BUNDLE_POLICY.md",
        "docs/RELEASE_MANIFEST_POLICY.md",
        "docs/SBOM_PROVENANCE_PLAN.md",
        "artifacts/release-manifest.json",
        "artifacts/checksums.sha256",
        "artifacts/sbom.spdx.json",
        "artifacts/sbom.cdx.json",
        "artifacts/provenance.intoto.jsonl",
    ]:
        assert f"`{allowed_input}`" in input_contract

    for forbidden_input in [
        "raw source bundles",
        "prompt transcripts",
        "shell transcripts",
        "raw command logs",
        "local temporary folders",
        "private inputs",
        "downstream repositories",
        "live configuration",
        "secrets",
        "credentials",
        "account values",
        "IPs",
        "ports",
        "endpoints",
        "device values",
        "release publication tokens",
    ]:
        assert forbidden_input in input_contract

    for output_rule in [
        "stdout summary only by default",
        "optional JSON stdout only when `--json` is provided",
        "no tracked output file",
        "no artifact under `artifacts/`",
        "no audit log",
        "no receipt file",
        "no trace file",
        "no release archive",
        "no upload",
        "no tag",
        "no release publication",
    ]:
        assert output_rule in output_contract

    assert "temporary output outside the repository" in output_contract


def test_status_contract_distinguishes_release_state_without_single_ready_flag() -> None:
    status = normalize_ws(section(contract_text(), "Status Contract"))

    for label in ["`PASS`", "`PASS WITH NOTES`", "`BLOCKED`", "`FAIL`", "`NOT RUN`", "`ENVIRONMENT BLOCKED`"]:
        assert label in status

    for state in [
        "source-basis commit",
        "artifact-containing commit",
        "local HEAD commit",
        "pushed commit",
        "tag target",
        "release target",
        "generated local evidence artifact",
        "uploaded artifact",
        "downstream release state",
    ]:
        assert state in status

    assert "single `released` or `ready` flag" in status


def test_failure_modes_verification_non_goals_and_next_step_are_bounded() -> None:
    text = contract_text()
    failure = section(text, "Failure Modes")
    verification = section(text, "Verification")
    non_goals = normalize_ws(section(text, "Non-goals"))
    next_step = normalize_ws(section(text, "Next Step"))

    for failure_mode in [
        "dirty worktree",
        "branch/upstream mismatch",
        "missing expected local release evidence",
        "unexpected untracked files",
        "unexpected generated artifact drift",
        "unsafe output path",
        "attempted artifact regeneration",
        "attempted workflow edit",
        "attempted tag creation or movement",
        "attempted artifact upload",
        "attempted release publication",
        "attempted signing",
        "attempted external metadata lookup",
        "attempted package registry call",
        "downstream access",
        "raw private or live material exposure",
        "cleanup failure",
    ]:
        assert failure_mode in failure

    for command in [
        "python -m pytest tests/test_release_automation_candidate_contract.py",
        "python -m pytest tests/test_release_automation_provenance_boundary.py",
        "python -m pytest tests/test_generate_manifest.py",
        "python -m pytest tests/test_generate_checksums.py",
        "python -m pytest tests/test_generate_sbom.py",
        "python -m pytest tests/test_generate_provenance.py",
        "python -m pytest tests",
        "python scripts/quality_gate.py",
        "git diff --check",
        "git ls-files --others --exclude-standard",
    ]:
        assert command in verification

    for forbidden_scope in [
        "implement `scripts/release_evidence_preflight.py`",
        "create `docs/RELEASE_AUTOMATION_PREFLIGHT_IMPLEMENTATION_PLAN.md`",
        "create `tests/test_release_evidence_preflight.py`",
        "run `scripts/run_release_verify.ps1`",
        "run release evidence generators",
        "regenerate `artifacts/release-manifest.json`",
        "regenerate `artifacts/checksums.sha256`",
        "regenerate `artifacts/sbom.spdx.json`",
        "regenerate `artifacts/sbom.cdx.json`",
        "regenerate `artifacts/provenance.intoto.jsonl`",
        "create release archives",
        "create or move tags",
        "create a GitHub Release",
        "upload artifacts",
        "sign artifacts",
        "add or edit workflows",
        "perform external metadata lookup",
        "publish, deploy, or mutate downstream repositories",
    ]:
        assert forbidden_scope in non_goals

    assert "separately approved Phase 10C implementation plan" in next_step
    assert "`local_release_evidence_preflight_dry_run` candidate" in next_step
    assert "Phase 10B does not authorize implementation or execution by itself" in next_step
