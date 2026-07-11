from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "docs" / "RELEASE_EVIDENCE_REFRESH_DECISION.md"


def decision_text() -> str:
    return DECISION_PATH.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[start:]
    return text[start:next_start]


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def test_decision_documents_exact_phase_10d_scope_and_basis() -> None:
    text = decision_text()
    purpose = normalize_ws(section(text, "Purpose"))
    basis = section(text, "Basis")

    assert "documentation and focused contract-test only" in purpose
    assert "`docs/RELEASE_EVIDENCE_REFRESH_DECISION.md`" in purpose
    assert "`tests/test_release_evidence_refresh_decision.py`" in purpose

    for basis_path in [
        "docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md",
        "docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md",
        "docs/RELEASE_AUTOMATION_PREFLIGHT_IMPLEMENTATION_PLAN.md",
        "docs/RELEASE_EVIDENCE_PREFLIGHT_USAGE_PROBE.md",
        "docs/RELEASE_BUNDLE_POLICY.md",
        "docs/RELEASE_MANIFEST_POLICY.md",
        "docs/SBOM_PROVENANCE_PLAN.md",
        "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
        "scripts/release_evidence_preflight.py",
        "scripts/run_release_verify.ps1",
    ]:
        assert f"`{basis_path}`" in basis

    assert "`7fa51a0cd44b8d35674b38513d9e1b39be87ad1a`" in basis
    assert "run `29156067497`, job `86553240545`" in normalize_ws(basis)


def test_decision_holds_refresh_until_stable_checkpoint() -> None:
    decision = normalize_ws(section(decision_text(), "Decision"))

    assert "`release_evidence_refresh_hold_until_stable_phase_10_checkpoint`" in decision
    assert "Status: `HOLD`" in decision
    for reason_code in [
        "HANDOFF_SYNCHRONIZATION_PENDING",
        "STABLE_SOURCE_BASIS_PENDING",
        "NO_RELEASE_PUBLICATION_TARGET",
    ]:
        assert f"`{reason_code}`" in decision

    assert "internally valid historical source-basis evidence" in decision
    assert "informational rather than a blocker" in decision
    assert "No release, tag, upload, publication, or downstream target" in decision


def test_proceed_conditions_require_exact_approval_and_stable_basis() -> None:
    proceed = normalize_ws(section(decision_text(), "Proceed Conditions"))

    for condition in [
        "the exact stable source-basis commit",
        "the exact approval reference and generation command",
        "completed `STATUS.md` and capability-roadmap handoff synchronization",
        "exact same-34-source corpus digest freshness commit",
        "successful Local Verify for the stable source checkpoint",
        "the exact five allowed release evidence output paths",
        "outside-repository backup and pre/post SHA-256 record",
        "overwrite and rollback rule",
        "`artifacts/eval-report.json` remains byte-for-byte unchanged",
        "separate approval for any push or workflow dispatch",
    ]:
        assert condition in proceed

    assert "the refresh must remain `HOLD` and no generator may run" in proceed


def test_future_refresh_boundary_names_only_five_outputs() -> None:
    boundary = section(decision_text(), "Future Refresh Artifact Boundary")

    expected_outputs = [
        "artifacts/release-manifest.json",
        "artifacts/checksums.sha256",
        "artifacts/sbom.spdx.json",
        "artifacts/sbom.cdx.json",
        "artifacts/provenance.intoto.jsonl",
    ]
    for output in expected_outputs:
        assert boundary.count(f"`{output}`") == 1

    normalized = normalize_ws(boundary)
    assert "`artifacts/eval-report.json` is a protected read-only checksum input" in normalized
    assert "`artifacts/corpus-digest.json` must already be valid" in normalized
    assert "No other artifact, audit, receipt, trace, schema, workflow" in normalized


def test_non_goals_block_refresh_and_publication_side_effects() -> None:
    non_goals = normalize_ws(section(decision_text(), "Non-goals"))

    for forbidden_scope in [
        "change release evidence generators, the preflight script",
        "regenerate the release manifest, checksums, SPDX SBOM, CycloneDX SBOM",
        "regenerate `artifacts/eval-report.json` or the approved corpus digest",
        "edit `STATUS.md`, `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`",
        "change schemas, quality gates, CI, or workflows",
        "create archives, signatures, attestations, tags, releases, or uploads",
        "call external metadata services or package registries",
        "access downstream repositories",
    ]:
        assert forbidden_scope in non_goals


def test_verification_and_next_step_keep_refresh_separately_approved() -> None:
    text = decision_text()
    verification = section(text, "Verification")
    next_step = normalize_ws(section(text, "Next Step"))

    for command in [
        "python -m pytest tests/test_release_evidence_refresh_decision.py",
        "python -m pytest tests/test_release_evidence_preflight.py",
        "python -m pytest tests",
        "python scripts/quality_gate.py",
        "python scripts/generate_checksums.py --verify",
        "python scripts/generate_corpus_digest.py --check --json",
        "git diff --check",
        "git ls-files --others --exclude-standard",
    ]:
        assert f"`{command}`" in verification

    assert "current-handoff synchronization task for `STATUS.md`" in next_step
    assert "same-34-source corpus digest freshness commit" in next_step
    assert "Release evidence regeneration still requires a separate exact-file, exact-command, owner-approved task" in next_step
