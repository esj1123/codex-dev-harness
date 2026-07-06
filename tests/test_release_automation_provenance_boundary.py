from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "docs" / "RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md"


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


def test_phase_10a_scope_basis_and_decision_are_documented() -> None:
    text = boundary_text()
    purpose = normalize_ws(section(text, "Purpose"))
    allowed = section(text, "Allowed Files")
    basis = section(text, "Basis")
    decision = normalize_ws(section(text, "Boundary Decision"))

    assert "Phase 10A is documentation and focused synthetic-test only" in purpose
    assert "before any release automation" in purpose
    assert "`release_automation_provenance_boundary_documented_without_automation`" in decision
    assert "does not approve a GitHub Release" in decision

    for allowed_file in [
        "docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md",
        "tests/test_release_automation_provenance_boundary.py",
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
        "docs/RELEASE_BUNDLE_POLICY.md",
        "docs/RELEASE_MANIFEST_POLICY.md",
        "docs/SBOM_PROVENANCE_PLAN.md",
        "scripts/run_release_verify.ps1",
        "scripts/generate_manifest.py",
        "scripts/generate_checksums.py",
        "scripts/generate_sbom.py",
        "scripts/generate_provenance.py",
        "tests/test_generate_manifest.py",
        "tests/test_generate_checksums.py",
        "tests/test_generate_sbom.py",
        "tests/test_generate_provenance.py",
        "28827967885",
        "85495348285",
        "4be8839a3b36ab3be9fc0f92b468da2de28158e3",
    ]:
        assert f"`{basis_item}`" in basis


def test_existing_local_evidence_surfaces_are_inventory_only() -> None:
    surfaces = normalize_ws(section(boundary_text(), "Existing Local Evidence Surfaces"))

    for surface in [
        "artifacts/release-manifest.json",
        "artifacts/checksums.sha256",
        "artifacts/sbom.spdx.json",
        "artifacts/sbom.cdx.json",
        "artifacts/provenance.intoto.jsonl",
        "scripts/run_release_verify.ps1",
        "scripts/generate_manifest.py",
        "scripts/generate_checksums.py",
        "scripts/generate_sbom.py",
        "scripts/generate_provenance.py",
    ]:
        assert f"`{surface}`" in surfaces

    for forbidden_approval in [
        "regeneration",
        "publication",
        "upload",
        "tag movement",
        "signing",
        "release archives",
        "workflow installation",
        "external metadata lookup",
        "downstream mutation",
    ]:
        assert forbidden_approval in surfaces


def test_future_approval_requirements_fail_closed() -> None:
    requirements = normalize_ws(section(boundary_text(), "Future Approval Requirements"))

    for required_item in [
        "exact allowed files",
        "exact generated artifact paths",
        "exact commands",
        "created, overwritten, committed, uploaded, archived, signed, or discarded",
        "source-basis commit semantics",
        "artifact-containing commit semantics",
        "push, tag, release, and rollback behavior",
        "retention and cleanup rules",
        "CI workflow changes",
        "network, external metadata lookup, cloud attestation, or package registry calls",
        "eval, audit, retrieval, MCP, or Hermes evidence",
        "artifact upload policy",
        "private data, secrets, local absolute paths, live targets, publication, tags, downstream edits",
    ]:
        assert required_item in requirements

    assert "release automation or provenance expansion is `BLOCKED`" in requirements


def test_release_evidence_safety_rules_distinguish_state_and_block_raw_material() -> None:
    safety = normalize_ws(section(boundary_text(), "Local Evidence Safety Rules"))

    for forbidden_material in [
        "raw source bundles",
        "private inputs",
        "prompt or session transcripts",
        "raw command logs",
        "unredacted tool-call bodies",
        "secrets",
        "credential material",
        "account values",
        "local absolute paths",
        "IPs",
        "ports",
        "endpoints",
        "live configuration",
        "device values",
        "downstream raw evidence",
        "generated downstream source",
        "release publication tokens",
    ]:
        assert forbidden_material in safety

    for state in [
        "source-basis commit",
        "artifact-containing commit",
        "pushed commit",
        "tag target",
        "published release target",
        "generated but uncommitted local artifact",
        "committed local evidence artifact",
        "uploaded artifact",
    ]:
        assert state in safety

    assert 'single "released" status' in safety


def test_boundary_checks_verification_non_goals_and_next_step_are_bounded() -> None:
    text = boundary_text()
    checks = normalize_ws(section(text, "Boundary Checks"))
    failure = section(text, "Failure Modes")
    verification = section(text, "Verification")
    non_goals = normalize_ws(section(text, "Non-goals"))
    next_step = normalize_ws(section(text, "Next Step"))

    for expected in [
        "Existing local release evidence generators remain local-only",
        "Existing generated artifacts are not regenerated",
        "Release automation remains unapproved",
        "Publication, tag movement, artifact upload, signing, and release archives remain unapproved",
        "CI-generated provenance and release workflows remain unapproved",
        "External metadata lookup and package registry calls remain unapproved",
        "Downstream release behavior remains unapproved",
    ]:
        assert expected in checks

    for status in ["`PASS`", "`PASS WITH NOTES`", "`BLOCKED`", "`FAIL`", "`NOT RUN`", "`ENVIRONMENT BLOCKED`"]:
        assert status in failure

    for command in [
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

    assert "pause before any release automation" in next_step
    assert "separately approved Phase 10B task" in next_step
    assert "Phase 10A does not authorize release automation" in next_step
