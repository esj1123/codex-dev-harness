import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from scripts import generate_checksums
from scripts.gates import (
    docs_gate,
    example_gate,
    example_render_drift_gate,
    json_evidence_gate,
    rendered_golden_content_gate,
    repo_hygiene_gate,
    secret_scan_gate,
    template_schema_gate,
)
from scripts.quality_gate import run_quality_gate
from scripts.render_template import TemplateConfig


REQUIRED_DOC_CONTENT = "# doc\n"

POST_V0_1_GOVERNANCE_DOCS = {
    "LICENSE",
    "SECURITY.md",
    "docs/RELEASE_BUNDLE_POLICY.md",
    "docs/RELEASE_MANIFEST_POLICY.md",
    "docs/SBOM_PROVENANCE_PLAN.md",
    "docs/PYTHON_RUNTIME_POLICY.md",
    "docs/APPROVED_CORPUS_RAG_PLAN.md",
    "docs/MODEL_CHANGE_POLICY.md",
    "docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md",
    "docs/MINIMAL_EVAL_HARNESS_DESIGN.md",
    "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
}

PROFILE_TEMPLATE_NAMES = [
    "AGENTS.override.md",
    "README.profile.md",
    "SAFETY_POLICY.profile.md",
    "STATUS.profile.md",
    "VERIFICATION.profile.md",
]

AMBIENT_GIT_ROUTING_KEYS = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_CONFIG",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_SYSTEM",
    "GIT_DIR",
    "GIT_EXEC_PATH",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_SHALLOW_FILE",
    "GIT_TEMPLATE_DIR",
    "GIT_WORK_TREE",
}

FIXED_GIT_CONFIG = [
    ("commit.gpgSign", "false"),
    ("tag.gpgSign", "false"),
    ("core.hooksPath", None),
    ("core.fsmonitor", "false"),
    ("submodule.recurse", "false"),
    ("safe.directory", None),
]


def write(path: Path, content: str = REQUIRED_DOC_CONTENT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def init_git_repo(root: Path) -> None:
    subprocess.run(
        ["git", "init", "-q", str(root)], check=True, capture_output=True
    )


def create_directory_link(link: Path, target: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr or result.stdout
    else:
        link.symlink_to(target, target_is_directory=True)


def remove_directory_link(link: Path) -> None:
    if os.name == "nt":
        link.rmdir()
    else:
        link.unlink()


def minimal_repo(root: Path) -> None:
    init_git_repo(root)
    for relative in docs_gate.REQUIRED_DOCS:
        write(root / relative)
    write(
        root / docs_gate.MANIFEST_PATH,
        Path(docs_gate.MANIFEST_PATH).read_text(encoding="utf-8"),
    )
    manifest = json.loads(
        (root / docs_gate.MANIFEST_PATH).read_text(encoding="utf-8")
    )
    for relative in manifest["operational_inputs"]:
        write(root / relative, Path(relative).read_text(encoding="utf-8"))
    for relative in json_evidence_gate.BUNDLE_PATHS:
        write(root / relative, Path(relative).read_text(encoding="utf-8"))
    write(
        root / "STATUS.md",
        f"# STATUS.md\n\n## Current State\n\n`{manifest['current_state']}`\n",
    )
    for relative in template_schema_gate.REQUIRED_BASE_TEMPLATES:
        write(root / relative)
    for profile in sorted(set(example_gate.REQUIRED_EXAMPLES.values())):
        for template_name in PROFILE_TEMPLATE_NAMES:
            write(
                root / "profiles" / profile / f"{template_name}.template",
                "profile {{ profile.name }} for {{ project.name }}\n",
            )
    write(
        root / "template.config.example.yml",
        "project:\n  name: demo\n  status: seed\nprofile:\n  name: python_cli\nrender:\n  tier: full\n",
    )
    write_golden_render_fixture(root)
    write_checksum_fixture(root)
    for relative in json_evidence_gate.AGENT_QUALITY_SCHEMA_PATHS:
        source = Path(relative)
        write(root / relative, source.read_text(encoding="utf-8"))


def write_checksum_fixture(root: Path) -> None:
    for relative_path in generate_checksums.REQUIRED_RELEASE_ARTIFACTS:
        write(root / relative_path, "{}\n")
    manifest = root / generate_checksums.DEFAULT_MANIFEST_PATH
    output = root / generate_checksums.DEFAULT_CHECKSUMS_PATH
    generate_checksums.write_checksums(
        generate_checksums.build_checksum_lines(root, manifest, output),
        output,
    )


def write_golden_render_fixture(root: Path) -> None:
    config = TemplateConfig(
        project_name="golden_render_python_cli",
        project_status="seed",
        profile="python_cli",
        tier="full",
    )
    records = [
        {"path": path, "sha256": digest}
        for path, digest in rendered_golden_content_gate.rendered_file_hashes(root, config).items()
    ]
    fixture = {
        "schema_version": "1",
        "description": "Synthetic python_cli render content fixture for the quality gate.",
        "render": {
            "project_name": config.project_name,
            "project_status": config.project_status,
            "profile": config.profile,
            "tier": config.tier,
        },
        "hash_algorithm": "sha256",
        "newline_policy": "lf-normalized",
        "expected_files": records,
    }
    write(root / rendered_golden_content_gate.FIXTURE_RELATIVE, json.dumps(fixture, indent=2) + "\n")


def write_valid_example(root: Path, example_name: str, profile: str) -> None:
    example_dir = root / "examples" / example_name
    for relative in example_gate.COMMON_REQUIRED_FILES:
        if relative == "template.config.yml":
            write(
                example_dir / relative,
                "project:\n"
                f"  name: {example_name}\n"
                "  status: seed\n"
                "profile:\n"
                f"  name: {profile}\n"
                "render:\n"
                "  tier: full\n",
            )
        else:
            write(example_dir / relative, "# example\n")

    write(example_dir / "README.profile.md", "# example profile\n")
    write(example_dir / "STATUS.profile.md", "# example profile status\n")

    if profile == "python_cli":
        write(example_dir / "STATUS.md", "pytest NOT RUN\nCLI smoke NOT RUN\nsynthetic fixtures only\n")
    elif profile == "csharp_desktop":
        write(example_dir / "STATUS.md", "build NOT RUN\ntest NOT RUN\nsmoke NOT RUN\n")
        write(example_dir / "README.md", "no source code, solution file, project file, or script in skeleton\n")
    elif profile == "plc_or_device_tool":
        write(
            example_dir / "SAFETY_POLICY.profile.md",
            "simulator/mock first\nlive device write prohibited\nequipment IP ports tag live parameters\nstart stop reset mode change\n",
        )


def test_docs_gate_reports_missing_doc(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    (tmp_path / "README.md").unlink()

    result = docs_gate.run(tmp_path)

    assert result.passed is False
    assert any("README.md" in message for message in result.messages)


def test_docs_gate_requires_current_post_v0_1_governance_docs() -> None:
    required_docs = set(docs_gate.REQUIRED_DOCS)

    assert POST_V0_1_GOVERNANCE_DOCS <= required_docs
    assert docs_gate.MANIFEST_PATH in required_docs
    assert set(docs_gate.BASELINE_REQUIRED_DOCS) == required_docs - {docs_gate.MANIFEST_PATH}
    assert len(docs_gate.BASELINE_REQUIRED_DOCS) == 78
    assert len(docs_gate.REQUIRED_DOCS) == 79
    assert len(docs_gate.REQUIRED_DOCS) == len(required_docs)


@pytest.mark.parametrize("manifest_content", [None, "{"])
def test_docs_gate_fails_closed_for_missing_or_malformed_manifest(
    tmp_path: Path,
    manifest_content: str | None,
) -> None:
    minimal_repo(tmp_path)
    manifest_path = tmp_path / docs_gate.MANIFEST_PATH
    if manifest_content is None:
        manifest_path.unlink()
    else:
        manifest_path.write_text(manifest_content, encoding="utf-8")

    result = docs_gate.run(tmp_path)

    assert result.passed is False
    assert result.name == "docs_gate"
    assert len(result.messages) == 1
    assert result.messages[0].startswith("authority manifest invalid:")


def test_v2_policy_separates_core_from_impact_required_extras() -> None:
    verification = Path("docs/VERIFICATION.md").read_text(encoding="utf-8")
    ci_policy = Path("docs/CI_POLICY.md").read_text(encoding="utf-8")
    impact_map = json.loads(
        Path("docs/VERIFICATION_IMPACT_MAP.json").read_text(encoding="utf-8")
    )

    assert "## Verification Tiers" in verification
    assert "The V2 core is always" in verification
    assert "impact-required extras" in verification
    assert "## Verification Tiers" not in ci_policy
    assert "sole normative authority" in ci_policy
    assert impact_map["tier_command_ids"]["V2"][-3:] == [
        "full_pytest",
        "standalone_eval",
        "quality_gate",
    ]
    for command_id in [
        "checksum_verify",
        "corpus_digest_check",
        "render_dry_runs",
    ]:
        assert command_id in impact_map["command_ids"]
        assert f"`{command_id}`" in verification


def test_readme_describes_installed_manual_local_verify_workflow() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "manual read-only `.github/workflows/local-verify.yml` workflow" in text
    assert "`workflow_dispatch` with a required exact commit SHA" in text
    assert "`contents: read`" in text
    assert "installed manual read-only Local Verify workflow is the baseline verification" in text
    assert "`manual_github_release_evidence_export`" in text
    assert "See `STATUS.md` for its current implementation state" in text
    assert "next planned CI step is a read-only verification hygiene path" not in text


def test_operational_docs_match_current_core_and_release_state() -> None:
    status = Path("STATUS.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    handoff = Path("docs/AI_HANDOFF.md").read_text(encoding="utf-8")
    roadmap = Path("docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    usage = Path("docs/LOCAL_USAGE.md").read_text(encoding="utf-8")
    checklist = Path("docs/LOCAL_PACKAGE_CHECKLIST.md").read_text(encoding="utf-8")
    runtime = Path("docs/PYTHON_RUNTIME_POLICY.md").read_text(encoding="utf-8")
    normalized_status = " ".join(status.split())
    normalized_checklist = " ".join(checklist.split())
    held_marker = "\n## Held Or Not Authorized\n"
    next_step_marker = "\n## Next Recommended Step\n"
    assert status.count(held_marker) == 1
    assert status.count(next_step_marker) == 1
    normalized_held = " ".join(
        status.split(held_marker, 1)[1].split("\n## ", 1)[0].split()
    )
    normalized_next_step = " ".join(
        status.split(next_step_marker, 1)[1].split("\n## ", 1)[0].split()
    )
    transitional_next_step = (
        "Refresh only `artifacts/corpus-digest.json` under its separately approved serial "
        "work-package, then freeze that clean commit as release source basis `S`. Push "
        "`S` only to the existing feature branch and require an exact-SHA GitHub `verify` "
        "`HOSTED_EXACT_SHA (V3)` before the separately approved export run. The tracked "
        "release bundle remains "
        "`VALID ANCESTOR / REFRESH REQUIRED` until the exported six-file bundle is "
        "downloaded, validated, committed locally, and promoted to local `main`. Tag, "
        "release, signing, publication, deployment, `origin/main`, Agent Quality/provider, "
        "Hermes, MCP, and downstream mutation remain outside this selection."
    )
    final_next_step = (
        "Keep the current local release bundle frozen and review it through local Git. "
        "The bundle was generated from an exact-SHA GitHub manual export, downloaded, "
        "independently validated, committed locally, and promoted to local `main`; the "
        "transient Actions artifact is transport only and expires after one day. No "
        "remote publication was performed. Tag, GitHub Release, signing, publication, "
        "deployment, `origin/main`, Agent Quality/provider, Hermes, MCP, and downstream "
        "mutation remain `NOT RUN` or outside this release."
    )
    final_bundle_state = (
        "`CURRENT / LOCAL RELEASE / GITHUB-VERIFIED / TRANSIENT CI EXPORT / NOT PUBLISHED`"
    )

    assert "`CORE_HARNESS_READY`" in normalized_status
    assert (
        "Tracked release evidence regeneration until the eval-report inclusion policy "
        "and exact source basis are separately approved."
        not in normalized_held
    )
    assert "Tag, release, signing, publication, or durable remote distribution." in normalized_held
    assert "outside the selected manual GitHub release-evidence export contract" in normalized_held
    if final_bundle_state in normalized_status:
        assert normalized_next_step == final_next_step
    else:
        assert "`VALID ANCESTOR / REFRESH REQUIRED`" in normalized_status
        assert normalized_next_step == transitional_next_step
    release_state_docs = {
        "STATUS.md": status,
        "README.md": readme,
        "docs/AI_HANDOFF.md": handoff,
        "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md": roadmap,
        "docs/LOCAL_PACKAGE_CHECKLIST.md": checklist,
    }
    for path, text in release_state_docs.items():
        normalized_text = " ".join(text.split())
        assert "`HISTORICAL_INVALID / REFRESH_NOT_RUN`" not in normalized_text, path
        if path != "STATUS.md":
            assert "`STATUS.md`" in normalized_text, path
    assert "decide whether it should include an eval report" not in normalized_next_step
    assert "Review the verified verification-lane branch tip" not in normalized_status
    assert "decide whether to promote it to local `main`" not in normalized_status
    assert "have been promoted to local `main`" not in normalized_status
    assert "Complete the core-only integration checks" not in normalized_status

    assert "manual read-only `.github/workflows/local-verify.yml`" in usage
    assert "`workflow_dispatch` with an exact commit SHA" in usage
    assert "is not automatic and is not a required check" in usage
    assert "`manual_github_release_evidence_export`" in usage
    assert "default Local Verify path remains read-only" in " ".join(usage.split())
    assert usage.index("full `python -m pytest tests`") < usage.index(
        "standalone `python scripts/run_eval.py`"
    ) < usage.index("core `python scripts/quality_gate.py`") < usage.index(
        "profile render dry-runs"
    )
    assert "requirements-dev.txt" in usage
    assert "requirements-dev.lock" in usage
    assert "python -m pip check" in usage

    assert "local release generators" in checklist
    assert (
        "separate artifact-regeneration and package-inclusion approval"
        in normalized_checklist
    )
    assert "This checklist does not itself run them" in checklist
    release_boundary_clauses = {
        "README.md": "does not authorize an automatic trigger, tag, github release, signing, publication, deployment, secret use, or `origin/main` mutation.",
        "docs/AI_HANDOFF.md": "does not authorize automatic triggers, durable distribution, tag, signing, publication, deployment, `origin/main` mutation, or downstream access.",
        "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md": "publication still requires an explicit target and owner approval.",
        "docs/LOCAL_PACKAGE_CHECKLIST.md": "this checklist does not authorize its execution or package inclusion.",
    }
    for path, clause in release_boundary_clauses.items():
        normalized_text = " ".join(release_state_docs[path].split()).lower()
        assert clause in normalized_text, path

    assert "focused development and narrow test commands" in runtime
    assert "exact `LOCAL_INTEGRATION (V2)` verification run" in runtime
    install = "python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock"
    assert runtime.index(install) < runtime.index(
        "python -m pip check"
    )


def test_current_authority_is_manifest_driven() -> None:
    manifest = json.loads(Path(docs_gate.MANIFEST_PATH).read_text(encoding="utf-8"))
    handoff = Path("docs/AI_HANDOFF.md").read_text(encoding="utf-8")
    agents = Path("AGENTS.md").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")

    assert manifest["current_state"] == "CORE_HARNESS_READY"
    assert manifest["default_read_order"][0:2] == [
        "AGENTS.md",
        docs_gate.MANIFEST_PATH,
    ]
    assert set(manifest["default_read_order"]).issubset(set(manifest["current_authority"]))
    assert "ACCEPTANCE_TRACE.md" not in manifest["default_read_order"]
    assert "docs/PROFILE_MATRIX.md" not in manifest["default_read_order"]
    assert manifest["default_read_order"] == [
        "AGENTS.md",
        docs_gate.MANIFEST_PATH,
        "PRODUCT.md",
        "MVP.md",
        "STATUS.md",
        "docs/SAFETY_POLICY.md",
    ]
    assert manifest["conditional_read_order"]["handoff"] == [
        "docs/AI_HANDOFF.md"
    ]
    assert manifest["operational_inputs"] == [
        "docs/APPROVED_CORPUS_SOURCE_SET.v2.json",
        "docs/DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md",
        "docs/JSON_EVIDENCE_POLICY.md",
        "docs/VERIFICATION_IMPACT_MAP.json",
        "evals/agentic/agent-role-profiles.json",
        "evals/agentic/suites/agentic-regression-v2.json",
    ]
    assert (
        manifest["unlisted_document_policy"]
        == "non_authoritative_reference_only_except_declared_operational_inputs"
    )
    assert "Read `STATUS.md` for the current human summary" in handoff
    assert "## Current Phase" not in handoff
    assert "## Next Recommended Step" not in handoff
    expected_numbered = [
        f"{index}. {path}"
        for index, path in enumerate(manifest["default_read_order"], start=1)
    ]
    for line in expected_numbered:
        assert line in agents
        assert line in readme
    assert "GitHub Actions workflow is not installed" not in handoff
    assert "recommended next work is Phase 3" not in handoff


def test_top_level_architecture_and_capability_docs_are_current_and_compact() -> None:
    architecture = Path("docs/ARCHITECTURE.md").read_text(encoding="utf-8")
    spec = Path("docs/HARNESS_SPEC.md").read_text(encoding="utf-8")
    roadmap = Path("docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "GitHub Actions workflow is still NOT INSTALLED" not in architecture
    assert "no `.github/workflows` file is installed" not in architecture
    assert "Agent Quality Plane" in architecture
    assert "work-package" in spec
    assert len(roadmap.splitlines()) <= 200
    assert "## Capability Registry" in roadmap
    assert "### Phase " not in roadmap
    assert "No new capability implementation is currently selected" in roadmap
    assert "serial work-package schema v3" in roadmap
    assert "## Read-Only Validation" in readme
    assert "## Artifact-Writing Release Verification" in readme


def test_work_package_v2_policy_separates_plan_from_authorization() -> None:
    change_control = Path("docs/CHANGE_CONTROL.md").read_text(encoding="utf-8")

    for field in ["contract_basis_sha", "contract_frozen_paths"]:
        assert f"`{field}`" in change_control
    for phrase in [
        "case-insensitive",
        "parent/child",
        "CONTRACT_CHANGE_REQUIRED",
        "`authorization_status`",
        "`NOT_AUTHENTICATED`",
    ]:
        assert phrase in change_control


def test_protocol_namespace_ownership_is_unambiguous_in_current_policy() -> None:
    manifest = json.loads(
        Path("docs/AUTHORITY_MANIFEST.json").read_text(encoding="utf-8")
    )
    expected = {
        "agent_run_evidence_schema": "docs/AGENT_QUALITY_STABILITY_POLICY.md",
        "release_provenance_schema": "docs/SBOM_PROVENANCE_PLAN.md",
        "verification_tier": "docs/VERIFICATION.md",
        "work_package_schema": "docs/CHANGE_CONTROL.md",
    }
    assert manifest["namespace_authority"] == expected

    current_policy_paths = sorted(
        set(manifest["current_authority"]) | set(manifest["durable_policy"])
    )
    tier_table_owners = []
    for path in current_policy_paths:
        text = Path(path).read_text(encoding="utf-8")
        if "## Verification Tiers" in text:
            tier_table_owners.append(path)
        assert "work-package v3" not in text, path

    assert tier_table_owners == ["docs/VERIFICATION.md"]

    verification = Path("docs/VERIFICATION.md").read_text(encoding="utf-8")
    for semantic_name in [
        "CONTRACT_SCOPE",
        "FOCUSED_FEATURE",
        "LOCAL_INTEGRATION",
        "HOSTED_EXACT_SHA",
    ]:
        assert f"`{semantic_name}`" in verification

    status = Path("STATUS.md").read_text(encoding="utf-8")
    roadmap = Path("docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    assert "Exact-SHA export run `" not in status
    assert "Selected; contract frozen" not in roadmap
    assert "Hardened; refresh required" not in roadmap


def test_acceptance_trace_is_historical_through_last_existing_checkpoint() -> None:
    text = Path("ACCEPTANCE_TRACE.md").read_text(encoding="utf-8")

    assert "AT-001 through AT-282 are preserved as historical" in text
    assert "`docs/AUTHORITY_MANIFEST.json`" in text
    assert "| AT-281 | current checkpoint |" in text
    assert text.count("| AT-282 | current checkpoint |") == 1
    assert "| AT-283 |" not in text


def test_local_verify_runs_console_eval_with_narrow_boundary() -> None:
    text = Path(".github/workflows/local-verify.yml").read_text(encoding="utf-8")
    verify_job = text.split("  verify:\n", 1)[1].split("  release-evidence-export:\n", 1)[0]
    export_job = text.split("  release-evidence-export:\n", 1)[1]
    verify_python = r".\.venv\Scripts\python.exe"
    tests_command = f"run: {verify_python} -m pytest tests --durations=50 -rs"
    eval_command = f"run: {verify_python} scripts/run_eval.py"
    quality_gate_command = f"run: {verify_python} scripts/quality_gate.py"

    assert "workflow_dispatch:" in text
    assert "expected_sha:" in text
    assert "mode:" in text
    assert "default: verify" in text
    assert "- verify" in text
    assert "- release-evidence-export" in text
    assert "required: true" in text
    assert "ref: ${{ inputs.expected_sha }}" in text
    assert "git rev-parse HEAD" in text
    assert "workflow definition commit does not match expected_sha" in text
    assert "^[0-9a-f]{40}$" in text
    assert "permissions:\n  contents: read" in text
    assert "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09" in text
    assert "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1" in text
    assert "persist-credentials: false" in text
    assert 'python-version: "3.12.10"' in text
    assert "python-version-file:" not in text
    assert "check-latest: false" in text
    assert "run: python -m venv .venv" in text
    install = f"{verify_python} -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock"
    install_step = (
        "      - name: Install development requirements\n"
        "        run: |\n"
        f"          {install}\n"
    )
    assert install_step in text
    assert f"run: {install}" not in text
    assert verify_job.count(install) == 1
    assert export_job.count(install) == 1
    verifier = (
        f"{verify_python} scripts/verify_dev_environment.py "
        "--expected-version-file .python-version --lock requirements-dev.lock --json"
    )
    pip_check = f"{verify_python} -m pip check"
    assert verifier in verify_job
    assert pip_check in verify_job
    assert 'PYTEST_DISABLE_PLUGIN_AUTOLOAD: "1"' in text
    assert 'PYTEST_ADDOPTS: ""' in text
    assert 'PYTEST_PLUGINS: ""' in text
    assert 'PYTHONPATH: ""' in text
    assert verify_job.count(eval_command) == 1
    assert (
        verify_job.index(install)
        < verify_job.index(verifier)
        < verify_job.index(pip_check)
        < verify_job.index(tests_command)
        < verify_job.index(eval_command)
        < verify_job.index(quality_gate_command)
    )
    assert "if: inputs.mode == 'verify'" in verify_job
    assert "upload-artifact" not in verify_job
    assert "if: inputs.mode == 'release-evidence-export'" in export_job
    assert "scripts/run_release_verify.ps1 -EvidenceContext GitHubActionsManualExport" in export_job
    assert "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in export_job
    assert "retention-days: 1" in export_job
    assert "if-no-files-found: error" in export_job
    assert "include-hidden-files: false" in export_job
    assert "overwrite: false" in export_job
    assert "release wrapper changed paths outside the exact six-file contract" in export_job
    assert "release manifest git_ref does not match the dispatched branch" in export_job
    assert "GITHUB_SHA" in verify_job and "GITHUB_SHA" in export_job
    for forbidden in [
        "--report",
        "--summary-report",
        "--cases-report",
        "pull_request:",
        "push:",
        "secrets:",
    ]:
        assert forbidden not in text


def test_local_wrapper_runs_console_eval_and_release_refreshes_present_report() -> None:
    local = Path("scripts/run_local_verify.ps1").read_text(encoding="utf-8")
    release = Path("scripts/run_release_verify.ps1").read_text(encoding="utf-8")

    pytest_step = 'Invoke-PythonStep "pytest"'
    eval_step = 'Invoke-PythonStep "standalone eval" @("scripts/run_eval.py")'
    quality_step = 'Invoke-PythonStep "quality gate"'
    environment_step = 'Invoke-PythonStep "development environment"'
    assert local.count(eval_step) == 1
    assert (
        local.index(environment_step)
        < local.index(pytest_step)
        < local.index(eval_step)
        < local.index(quality_step)
    )
    assert "scripts/run_local_verify.ps1" in release
    report_refresh = (
        'Invoke-PythonStep "optional eval report refresh" '
        '@("scripts/run_eval.py", "--report", $EvalReportPath)'
    )
    assert release.count(report_refresh) == 1
    assert '[ValidateSet("Local", "GitHubActionsManualExport")]' in release
    assert '[string]$EvidenceContext = "Local"' in release
    assert '$env:GITHUB_ACTIONS -cne "true"' in release
    assert '$env:GITHUB_EVENT_NAME -cne "workflow_dispatch"' in release
    assert '$headCommit -cne $env:GITHUB_SHA' in release
    assert '$env:GITHUB_REF_TYPE -cne "branch"' in release
    assert 'git check-ref-format --branch $env:GITHUB_REF_NAME' in release
    assert 'git switch --create $env:GITHUB_REF_NAME $env:GITHUB_SHA' in release
    assert '$currentBranch -cne $env:GITHUB_REF_NAME' in release
    assert '@("--execution-context", "github_actions_manual_export")' in release
    assert "Test-Path -LiteralPath" in release
    selector = "$PythonCommand = Find-Python"
    propagation = "$env:PYTHON = $PythonCommand"
    local_verify = (
        'Invoke-PowerShellStep "local verification wrapper" '
        '(Join-Path $RepoRoot "scripts/run_local_verify.ps1")'
    )
    release_generation = 'Invoke-PythonStep "release manifest generation"'
    clean_tree = "Assert-CleanGitTree"
    sbom_generation = 'Invoke-OptionalPythonScript "optional SBOM generation"'
    provenance_generation = 'Invoke-OptionalPythonScript "optional provenance generation"'
    checksum_generation = 'Invoke-PythonStep "final checksum generation"'
    checksum_verification = 'Invoke-PythonStep "checksum verification"'
    assert release.count(selector) == 1
    assert (
        release.index(selector)
        < release.index(propagation)
        < release.rindex(clean_tree)
        < release.index(local_verify)
        < release.index(release_generation)
        < release.index(report_refresh)
        < release.index(sbom_generation)
        < release.index(provenance_generation)
        < release.index(checksum_generation)
        < release.index(checksum_verification)
    )
    assert "--allow-missing" not in release
    assert release.count("scripts/generate_checksums.py") == 2


def test_local_wrapper_defaults_to_full_and_routine_excludes_only_exact_held_files() -> None:
    local = Path("scripts/run_local_verify.ps1").read_text(encoding="utf-8")
    held_block = local.split("$RoutineHeldTestFiles = @(", 1)[1].split("\n)", 1)[0]
    expected_held = {
        "tests/test_agent_quality_aggregation.py",
        "tests/test_agent_quality_capture.py",
        "tests/test_agent_quality_cli.py",
        "tests/test_agent_quality_contracts.py",
        "tests/test_agent_quality_semantic_failure.py",
        "tests/test_agent_quality_trial_validation.py",
        "tests/test_agent_role_profiles.py",
        "tests/test_hermes_git_push_preflight.py",
        "tests/test_hermes_git_push_preflight_durable_writer_proposal.py",
        "tests/test_hermes_git_push_preflight_evidence_decision.py",
        "tests/test_hermes_git_push_preflight_output_contract.py",
        "tests/test_hermes_git_push_preflight_receipt_trace_plan.py",
        "tests/test_hermes_git_push_preflight_receipt_writer.py",
        "tests/test_hermes_git_push_preflight_schema_alignment.py",
        "tests/test_hermes_git_push_preflight_selection_review.py",
        "tests/test_hermes_git_push_preflight_tracked_receipt_contract.py",
        "tests/test_hermes_git_push_preflight_tracked_receipt_policy.py",
        "tests/test_hermes_git_push_preflight_tracked_receipt_post_generation_review.py",
        "tests/test_hermes_git_push_preflight_usage_probe.py",
        "tests/test_hermes_git_push_preflight_writer.py",
        "tests/test_hermes_git_push_preflight_writer_persistence_hold.py",
        "tests/test_hermes_mcp_security_alignment.py",
        "tests/test_hermes_preflight_caller_boundary.py",
        "tests/test_hermes_preflight_use_planning_contract.py",
        "tests/test_hermes_sidecar.py",
        "tests/test_hermes_sidecar_planning_contract.py",
        "tests/test_hermes_sidecar_result_schema_contract.py",
        "tests/test_local_rag_retriever.py",
        "tests/test_mcp_tool_boundary_contract.py",
    }
    declared_held = {
        line.strip().strip('\",')
        for line in held_block.splitlines()
        if line.strip().startswith('\"tests/')
    }

    assert '[ValidateSet("Full", "Routine")]' in local
    assert '[string]$Lane = "Full"' in local
    assert declared_held == expected_held
    assert "*" not in held_block
    assert '$Lane -eq "Routine"' in local
    assert '$PytestArgs += @("--ignore", $heldTestFile)' in local
    assert "Test-Path -LiteralPath $heldTestPath -PathType Leaf" in local
    assert 'Invoke-PythonStep "pytest" $PytestArgs' in local


def _wrapper_pytest_args(
    tmp_path: Path, lane: str, *, explicit: bool
) -> list[str]:
    invocation_kind = "explicit" if explicit else "default"
    argument_log = tmp_path / f"{lane.lower()}-{invocation_kind}-arguments.txt"
    python_shim = tmp_path / f"python-{lane.lower()}-{invocation_kind}.cmd"
    python_shim.write_text(
        '@echo off\r\n>>"%CODEX_TEST_ARGUMENT_LOG%" echo %*\r\nexit /b 0\r\n',
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["PYTHON"] = str(python_shim)
    environment["CODEX_TEST_ARGUMENT_LOG"] = str(argument_log)
    command = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "scripts/run_local_verify.ps1",
    ]
    if explicit:
        command.extend(["-Lane", lane])
    result = subprocess.run(
        command,
        cwd=Path.cwd(),
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    invocations = argument_log.read_text(encoding="utf-8").splitlines()
    pytest_invocation = next(
        invocation for invocation in invocations if invocation.startswith("-m pytest ")
    )
    return pytest_invocation.split()[2:]


def _parse_environment_probe(path: Path) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "BEGIN":
            current = {}
            continue
        if line == "END":
            assert current is not None
            records.append(current)
            current = None
            continue
        assert current is not None
        key, separator, value = line.partition("=")
        assert separator
        current[key] = value
    assert current is None
    return records


def _environment_probe_batch(log_variable: str, *, exit_code: int = 0) -> str:
    keys = [
        "ARGS",
        *sorted(AMBIENT_GIT_ROUTING_KEYS),
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_NOSYSTEM",
        "GIT_CONFIG_GLOBAL",
        "GIT_TERMINAL_PROMPT",
        "GCM_INTERACTIVE",
        "GIT_NO_REPLACE_OBJECTS",
        "GIT_OPTIONAL_LOCKS",
        *[
            name
            for index in range(7)
            for name in (f"GIT_CONFIG_KEY_{index}", f"GIT_CONFIG_VALUE_{index}")
        ],
        "PYTEST_ADDOPTS",
        "PYTEST_PLUGINS",
        "PYTHONPATH",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
    ]
    lines = ["@echo off", f'>>"%{log_variable}%" echo BEGIN']
    for key in keys:
        value = "%*" if key == "ARGS" else f"%{key}%"
        lines.append(f'>>"%{log_variable}%" echo {key}={value}')
    lines.extend([f'>>"%{log_variable}%" echo END', f"exit /b {exit_code}"])
    return "\r\n".join(lines) + "\r\n"


def _assert_hermetic_git_probe(
    record: dict[str, str], repo_root: Path
) -> None:
    for name in AMBIENT_GIT_ROUTING_KEYS:
        assert record[name] == ""
    assert record["GIT_CONFIG_COUNT"] == str(len(FIXED_GIT_CONFIG))
    assert record["GIT_CONFIG_NOSYSTEM"] == "1"
    assert record["GIT_CONFIG_GLOBAL"].casefold() in {"nul", os.devnull.casefold()}
    assert record["GIT_TERMINAL_PROMPT"] == "0"
    assert record["GCM_INTERACTIVE"] == "Never"
    assert record["GIT_NO_REPLACE_OBJECTS"] == "1"
    assert record["GIT_OPTIONAL_LOCKS"] == "0"
    for index, (expected_key, expected_value) in enumerate(FIXED_GIT_CONFIG):
        assert record[f"GIT_CONFIG_KEY_{index}"] == expected_key
        observed_value = record[f"GIT_CONFIG_VALUE_{index}"]
        if index == 2:
            hooks_path = Path(observed_value)
            assert hooks_path.is_absolute()
            assert not hooks_path.exists()
        elif index == 5:
            assert Path(observed_value) == repo_root.resolve()
        else:
            assert observed_value == expected_value
    assert record["GIT_CONFIG_KEY_6"] == ""
    assert record["GIT_CONFIG_VALUE_6"] == ""


def test_pytest_session_uses_hermetic_git_environment() -> None:
    for name in AMBIENT_GIT_ROUTING_KEYS:
        assert name not in os.environ
    assert os.environ["GIT_CONFIG_COUNT"] == str(len(FIXED_GIT_CONFIG))
    assert os.environ["GIT_NO_REPLACE_OBJECTS"] == "1"
    assert os.environ["GIT_OPTIONAL_LOCKS"] == "0"
    for index, (expected_key, expected_value) in enumerate(FIXED_GIT_CONFIG):
        assert os.environ[f"GIT_CONFIG_KEY_{index}"] == expected_key
        if expected_value is not None:
            assert os.environ[f"GIT_CONFIG_VALUE_{index}"] == expected_value


def test_local_wrapper_sanitizes_git_environment_for_every_child(
    tmp_path: Path,
) -> None:
    environment_log = tmp_path / "local-wrapper-environment.log"
    python_shim = tmp_path / "python-environment-probe.cmd"
    python_shim.write_text(
        _environment_probe_batch("CODEX_TEST_ENVIRONMENT_LOG"), encoding="utf-8"
    )
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHON": str(python_shim),
            "CODEX_TEST_ENVIRONMENT_LOG": str(environment_log),
            "GIT_DIR": str(tmp_path / "hostile.git"),
            "GIT_INDEX_FILE": str(tmp_path / "hostile.index"),
            "GIT_WORK_TREE": str(tmp_path / "hostile-worktree"),
            "GIT_CONFIG_PARAMETERS": "hostile",
            "GIT_CONFIG_COUNT": "9",
            "GIT_CONFIG_KEY_8": "core.hooksPath",
            "GIT_CONFIG_VALUE_8": str(tmp_path / "hostile-hooks"),
            "GIT_EXEC_PATH": str(tmp_path / "hostile-exec"),
            "GIT_NAMESPACE": "hostile",
            "PYTEST_ADDOPTS": "-k nonexistent",
            "PYTEST_PLUGINS": "hostile_plugin",
            "PYTHONPATH": str(tmp_path / "hostile-pythonpath"),
        }
    )
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "scripts/run_local_verify.ps1",
        ],
        cwd=Path.cwd(),
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    records = _parse_environment_probe(environment_log)
    assert len(records) == 8
    assert len({record["GIT_CONFIG_VALUE_2"] for record in records}) == 1
    for record in records:
        _assert_hermetic_git_probe(record, Path.cwd())
        assert record["PYTEST_ADDOPTS"] == ""
        assert record["PYTEST_PLUGINS"] == ""
        assert record["PYTHONPATH"] == ""
        assert record["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    pytest_record = next(record for record in records if record["ARGS"].startswith("-m pytest "))
    assert pytest_record["ARGS"].split() == ["-m", "pytest", "tests", "--durations=50", "-rs"]


def test_release_wrapper_sanitizes_environment_before_first_git_command(
    tmp_path: Path,
) -> None:
    scripts = tmp_path / "scripts"
    write(
        scripts / "run_release_verify.ps1",
        Path("scripts/run_release_verify.ps1").read_text(encoding="utf-8"),
    )
    write(
        scripts / "run_local_verify.ps1",
        Path("scripts/run_local_verify.ps1").read_text(encoding="utf-8"),
    )
    shim_dir = tmp_path / "shim"
    git_log = tmp_path / "release-git-environment.log"
    python_log = tmp_path / "release-python.log"
    write(
        shim_dir / "git.cmd",
        _environment_probe_batch("CODEX_TEST_GIT_LOG", exit_code=97),
    )
    write(
        shim_dir / "python.cmd",
        '@echo off\r\n>>"%CODEX_TEST_PYTHON_LOG%" echo %*\r\nexit /b 0\r\n',
    )
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": str(shim_dir) + os.pathsep + environment["PATH"],
            "PYTHON": str(shim_dir / "python.cmd"),
            "CODEX_TEST_GIT_LOG": str(git_log),
            "CODEX_TEST_PYTHON_LOG": str(python_log),
            "GIT_DIR": str(tmp_path / "hostile.git"),
            "GIT_INDEX_FILE": str(tmp_path / "hostile.index"),
            "GIT_WORK_TREE": str(tmp_path / "hostile-worktree"),
            "GIT_CONFIG_PARAMETERS": "hostile",
            "GIT_CONFIG_COUNT": "8",
            "GIT_CONFIG_KEY_7": "core.hooksPath",
            "GIT_CONFIG_VALUE_7": str(tmp_path / "hostile-hooks"),
        }
    )
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(scripts / "run_release_verify.ps1"),
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 97
    records = _parse_environment_probe(git_log)
    assert len(records) == 1
    assert records[0]["ARGS"] == "status --porcelain=v1 --untracked-files=all"
    _assert_hermetic_git_probe(records[0], tmp_path)
    python_invocations = python_log.read_text(encoding="utf-8").splitlines()
    assert len(python_invocations) == 1
    assert "scripts/verify_dev_environment.py" in python_invocations[0]
    assert not (tmp_path / "artifacts").exists()


def _collected_nodes(pytest_args: list[str]) -> set[str]:
    environment = os.environ.copy()
    for name in ["PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTHONPATH"]:
        environment.pop(name, None)
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            *pytest_args,
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
        cwd=Path.cwd(),
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return {
        line.replace("\\", "/")
        for line in result.stdout.splitlines()
        if line.startswith(("tests/", "tests\\")) and "::" in line
    }


def test_local_wrapper_lane_arguments_produce_exact_collection_difference(
    tmp_path: Path,
) -> None:
    default_full_args = _wrapper_pytest_args(tmp_path, "Full", explicit=False)
    explicit_full_args = _wrapper_pytest_args(tmp_path, "Full", explicit=True)
    routine_args = _wrapper_pytest_args(tmp_path, "Routine", explicit=True)
    assert default_full_args == explicit_full_args
    assert default_full_args == ["tests", "--durations=50", "-rs"]
    assert routine_args[:3] == default_full_args
    assert len(routine_args) == len(default_full_args) + (29 * 2)
    assert routine_args.count("--ignore") == 29
    assert all(
        routine_args[index] == "--ignore"
        for index in range(len(default_full_args), len(routine_args), 2)
    )

    full_nodes = _collected_nodes(default_full_args)
    routine_nodes = _collected_nodes(routine_args)
    held_files = {
        routine_args[index + 1].replace("\\", "/")
        for index, argument in enumerate(routine_args)
        if argument == "--ignore"
    }
    held_nodes = {
        node for node in full_nodes if node.split("::", 1)[0] in held_files
    }
    expected_routine_nodes = full_nodes - held_nodes

    assert held_nodes
    assert {node.split("::", 1)[0] for node in held_nodes} == held_files
    assert routine_nodes == expected_routine_nodes
    assert any(node.startswith("tests/test_quality_gate.py::") for node in routine_nodes)
    assert any(
        node.startswith("tests/test_json_evidence_gate.py::")
        for node in routine_nodes
    )
    assert any(
        node.startswith("tests/test_release_evidence_preflight.py::")
        for node in routine_nodes
    )
    assert any(
        node.startswith("tests/test_downstream_task_contract_validator.py::")
        for node in routine_nodes
    )


def test_local_wrapper_rejects_unknown_lane_before_execution(tmp_path: Path) -> None:
    argument_log = tmp_path / "unknown-lane-arguments.txt"
    python_shim = tmp_path / "python-unknown-lane.cmd"
    python_shim.write_text(
        '@echo off\r\n>>"%CODEX_TEST_ARGUMENT_LOG%" echo %*\r\nexit /b 0\r\n',
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["PYTHON"] = str(python_shim)
    environment["CODEX_TEST_ARGUMENT_LOG"] = str(argument_log)
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "scripts/run_local_verify.ps1",
            "-Lane",
            "Unknown",
        ],
        cwd=Path.cwd(),
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode != 0
    assert not argument_log.exists()


def test_release_and_hosted_verification_remain_full_only() -> None:
    release = Path("scripts/run_release_verify.ps1").read_text(encoding="utf-8")
    workflow = Path(".github/workflows/local-verify.yml").read_text(encoding="utf-8")

    assert "-Lane Routine" not in release
    assert "-Lane Routine" not in workflow
    assert ".\\.venv\\Scripts\\python.exe -m pytest tests --durations=50 -rs" in workflow


def test_eval_policy_docs_define_manual_console_integration_boundary() -> None:
    decision = Path("docs/EVAL_INTEGRATION_DECISION.md").read_text(encoding="utf-8")
    policy = Path("docs/EVAL_POLICY.md").read_text(encoding="utf-8")
    ci_policy = Path("docs/CI_POLICY.md").read_text(encoding="utf-8")
    report_plan = Path("docs/EVAL_REPORT_INTEGRATION_PLAN.md").read_text(encoding="utf-8")
    design = Path("docs/MINIMAL_EVAL_HARNESS_DESIGN.md").read_text(encoding="utf-8")
    verification = Path("docs/VERIFICATION.md").read_text(encoding="utf-8")
    limitations = Path("docs/KNOWN_LIMITATIONS.md").read_text(encoding="utf-8")

    assert "MANUAL_LOCAL_VERIFY_CONSOLE_EVAL_APPROVED" in decision
    assert "MANUAL_LOCAL_VERIFY_CONSOLE_EVAL_APPROVED" in policy
    for text in [decision, policy, ci_policy, report_plan, design, verification, limitations]:
        assert "python scripts/run_eval.py" in text
        assert "quality_gate.py" in text
    for text in [decision, policy, ci_policy, report_plan, verification]:
        assert "workflow_dispatch" in text
        assert "contents: read" in text
    for text in [decision, policy, ci_policy, report_plan, design, verification]:
        normalized = " ".join(text.lower().split())
        assert any(
            phrase in normalized
            for phrase in ["no report", "without report flags", "no eval report"]
        )
        assert "release-blocking" in text


def test_security_policy_defines_private_reporting_contract() -> None:
    text = Path("SECURITY.md").read_text(encoding="utf-8")

    for expected in [
        "security/advisories/new",
        "Do not open a public issue",
        "`main`",
        "`v0.1.0`",
        "7 calendar days",
        "14 calendar days",
        "downstream projects",
        "Do not submit secrets",
    ]:
        assert expected in text


def test_validation_scope_defines_curated_example_contract() -> None:
    text = Path("docs/VALIDATION_SCOPE.md").read_text(encoding="utf-8")

    assert "curated regression skeletons" in text
    assert "not byte-for-byte" in text
    assert "example_render_drift_gate" in text
    assert "file-set coverage only" in text
    assert "separate golden render fixture" in text
    assert "`evals/golden/`" in text
    assert "generated snapshots" in text
    assert "RENDER_PROVENANCE_AND_UPGRADE_PLAN.md" in text
    assert "blanket overwrite" in text


def test_render_provenance_upgrade_plan_defines_safe_update_path() -> None:
    text = Path("docs/RENDER_PROVENANCE_AND_UPGRADE_PLAN.md").read_text(encoding="utf-8")

    assert "harness_commit" in text
    assert "render_profile" in text
    assert "config_source" in text
    assert "generated snapshot basis" in text
    assert "user-editable project docs" in text
    assert "temporary directory" in text
    assert "Compare" in text or "compare" in text
    assert "Do not use blanket `--force` overwrite" in text
    assert "does not authorize" in text
    assert "downstream repository access" in text


def test_template_schema_gate_requires_seed_config(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(tmp_path / "template.config.example.yml", "project:\n  name: demo\n  status: draft\n")

    result = template_schema_gate.run(tmp_path)

    assert result.passed is False
    assert "status: seed" in result.messages[0]


def test_template_schema_gate_reports_full_render_tier(tmp_path: Path) -> None:
    minimal_repo(tmp_path)

    result = template_schema_gate.run(tmp_path)

    assert result.passed is True
    assert "render.tier=full" in result.messages


def test_template_schema_gate_rejects_unknown_render_tier(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(
        tmp_path / "template.config.example.yml",
        "project:\n  name: demo\n  status: seed\nrender:\n  tier: unknown\n",
    )

    result = template_schema_gate.run(tmp_path)

    assert result.passed is False
    assert "render tier must be one of" in result.messages[0]


def test_secret_scan_gate_detects_private_key(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    write(tmp_path / "README.md", "-----BEGIN " + "PRIVATE KEY-----\n")

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert "README.md" in result.messages[0]


def test_secret_scan_gate_ignores_local_workspace(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    write(tmp_path / "local" / "scratch.md", "-----BEGIN " + "PRIVATE KEY-----\n")

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is True


def test_secret_scan_gate_checks_nested_local_named_folders(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    write(tmp_path / "docs" / "local" / "scratch.md", "-----BEGIN " + "PRIVATE KEY-----\n")

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert any("docs" in message and "local" in message for message in result.messages)


@pytest.mark.parametrize(
    "relative_path",
    [
        "config.json",
        "events.jsonl",
        "script.ps1",
        "settings.ini",
        "requirements.lock",
        "checksums.sha256",
        ".gitattributes",
        ".gitignore",
        ".python-version",
        "LICENSE",
    ],
)
def test_secret_scan_gate_checks_expanded_text_surface(
    tmp_path: Path, relative_path: str
) -> None:
    init_git_repo(tmp_path)
    write(tmp_path / relative_path, "api_key=" + "a" * 24 + "\n")

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert any(relative_path in message for message in result.messages)


@pytest.mark.parametrize("root_name", [".venv", "venv", "local"])
def test_secret_scan_gate_ignores_root_local_environments(
    tmp_path: Path, root_name: str
) -> None:
    init_git_repo(tmp_path)
    write(
        tmp_path / root_name / "nested" / "config.json",
        "api_key=" + "a" * 24 + "\n",
    )

    assert secret_scan_gate.run(tmp_path).passed is True


@pytest.mark.parametrize(
    "relative_path",
    ["local/secret", ".venv/credential", "extensionless"],
)
def test_secret_scan_gate_checks_force_tracked_ignored_and_extensionless_files(
    tmp_path: Path, relative_path: str
) -> None:
    write(tmp_path / relative_path, "api_key=" + "a" * 24 + "\n")
    init_git_repo(tmp_path)
    subprocess.run(
        ["git", "add", "-f", "--", relative_path],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert any(relative_path in message for message in result.messages)


@pytest.mark.parametrize("routing_key", ["GIT_DIR", "GIT_INDEX_FILE"])
def test_git_inventory_gates_ignore_ambient_repository_routing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    routing_key: str,
) -> None:
    target = tmp_path / "target"
    alternate = tmp_path / "alternate"
    target.mkdir()
    alternate.mkdir()
    init_git_repo(target)
    init_git_repo(alternate)
    write(target / ".venv" / "pyvenv.cfg", "home = synthetic\n")
    write(target / "extensionless", "api_key=" + "a" * 24 + "\n")
    subprocess.run(
        ["git", "-C", str(target), "add", "-f", ".venv/pyvenv.cfg", "extensionless"],
        check=True,
        capture_output=True,
    )
    write(alternate / "benign.txt", "benign\n")
    subprocess.run(
        ["git", "-C", str(alternate), "add", "benign.txt"],
        check=True,
        capture_output=True,
    )
    hostile_value = (
        alternate / ".git"
        if routing_key == "GIT_DIR"
        else alternate / ".git" / "index"
    )
    monkeypatch.setenv(routing_key, str(hostile_value))

    secret_result = secret_scan_gate.run(target)
    hygiene_result = repo_hygiene_gate.run(target)

    assert secret_result.passed is False
    assert any("extensionless matched" in message for message in secret_result.messages)
    assert hygiene_result.passed is False
    assert hygiene_result.messages == [
        f"prohibited tracked root: {Path('.venv/pyvenv.cfg')}"
    ]


def test_secret_scan_gate_fails_closed_when_git_inventory_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_inventory(*_args, **_kwargs):
        raise OSError("synthetic git failure")

    monkeypatch.setattr(secret_scan_gate.subprocess, "run", fail_inventory)

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert result.messages == ["tracked file inventory failed"]


def test_secret_scan_gate_fails_closed_when_git_inventory_times_out(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def timeout_inventory(*args, **_kwargs):
        raise subprocess.TimeoutExpired(args[0], 30)

    monkeypatch.setattr(secret_scan_gate.subprocess, "run", timeout_inventory)

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert result.messages == ["tracked file inventory failed"]


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (
            SimpleNamespace(returncode=128, stdout=b"", stderr=b"synthetic"),
            "tracked file inventory failed",
        ),
        (
            SimpleNamespace(
                returncode=0,
                stdout=b"a" * (secret_scan_gate.MAX_GIT_OUTPUT_BYTES + 1),
                stderr=b"",
            ),
            "tracked file inventory exceeded output limit",
        ),
        (
            SimpleNamespace(returncode=0, stdout=b"\xff\0", stderr=b""),
            "tracked file inventory is not valid UTF-8",
        ),
        (
            SimpleNamespace(returncode=0, stdout=b"../outside\0", stderr=b""),
            "tracked file inventory contains an unsafe path",
        ),
    ],
)
def test_secret_scan_gate_rejects_invalid_git_inventory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    result: SimpleNamespace,
    expected: str,
) -> None:
    monkeypatch.setattr(
        secret_scan_gate.subprocess, "run", lambda *_args, **_kwargs: result
    )

    gate_result = secret_scan_gate.run(tmp_path)

    assert gate_result.passed is False
    assert gate_result.messages == [expected]


def test_secret_scan_gate_rejects_tracked_hardlink(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    tracked = tmp_path / "tracked.txt"
    write(tracked, "benign\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "tracked.txt"], check=True
    )
    alias = tmp_path / "local" / "alias.txt"
    alias.parent.mkdir()
    os.link(tracked, alias)

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert result.messages == ["tracked.txt is a multiply-linked file"]


def test_secret_scan_gate_rejects_tracked_parent_junction_or_symlink(
    tmp_path: Path,
) -> None:
    init_git_repo(tmp_path)
    tracked_parent = tmp_path / "linked"
    write(tracked_parent / "secret.txt", "benign\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "linked/secret.txt"], check=True
    )
    (tracked_parent / "secret.txt").unlink()
    tracked_parent.rmdir()
    target = tmp_path / "local" / "outside"
    write(target / "secret.txt", "api_key=" + "a" * 24 + "\n")
    create_directory_link(tracked_parent, target)
    try:
        result = secret_scan_gate.run(tmp_path)
    finally:
        remove_directory_link(tracked_parent)

    assert result.passed is False
    assert result.messages == [
        "linked/secret.txt uses a symlink or reparse point"
    ]


def test_secret_scan_gate_rejects_tracked_leaf_reparse_or_symlink(
    tmp_path: Path,
) -> None:
    init_git_repo(tmp_path)
    tracked = tmp_path / "tracked.txt"
    write(tracked, "benign\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "tracked.txt"], check=True
    )
    tracked.unlink()
    if os.name == "nt":
        target = tmp_path / "local" / "outside-directory"
        target.mkdir(parents=True)
        create_directory_link(tracked, target)
    else:
        target = tmp_path / "local" / "outside.txt"
        write(target, "api_key=" + "a" * 24 + "\n")
        tracked.symlink_to(target)
    try:
        result = secret_scan_gate.run(tmp_path)
    finally:
        if os.name == "nt":
            remove_directory_link(tracked)
        else:
            tracked.unlink()

    assert result.passed is False
    assert result.messages == ["tracked.txt uses a symlink or reparse point"]


def test_secret_scan_gate_rejects_tracked_identity_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_git_repo(tmp_path)
    tracked = tmp_path / "tracked.txt"
    write(tracked, "benign\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "tracked.txt"], check=True
    )
    original_identity = secret_scan_gate._path_identity
    identity_calls = 0

    def drifting_identity(path: Path) -> tuple[int, ...]:
        nonlocal identity_calls
        identity_calls += 1
        identity = original_identity(path)
        if identity_calls == 2:
            return (*identity[:-1], identity[-1] + 1)
        return identity

    monkeypatch.setattr(secret_scan_gate, "_path_identity", drifting_identity)

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert result.messages == ["tracked.txt identity changed while scanning"]


def test_secret_scan_gate_rejects_missing_tracked_file(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    tracked = tmp_path / "tracked.txt"
    write(tracked, "benign\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "tracked.txt"], check=True
    )
    tracked.unlink()

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert result.messages == ["tracked.txt could not be scanned"]


def test_secret_scan_gate_rejects_unreadable_tracked_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_git_repo(tmp_path)
    tracked = tmp_path / "tracked.txt"
    write(tracked, "benign\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "tracked.txt"], check=True
    )
    original_read_bytes = Path.read_bytes

    def fail_tracked_read(path: Path) -> bytes:
        if path == tracked:
            raise PermissionError("synthetic unreadable file")
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", fail_tracked_read)

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert result.messages == ["tracked.txt could not be scanned"]


def test_secret_scan_gate_rejects_oversize_tracked_file(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    tracked = tmp_path / "tracked.txt"
    write(tracked, "a" * (secret_scan_gate.MAX_TRACKED_TEXT_BYTES + 1))
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "tracked.txt"], check=True
    )

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert result.messages == ["tracked.txt exceeds tracked text scan limit"]


def test_secret_scan_gate_prunes_untracked_reparse_directory(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    target = tmp_path / "local" / "outside"
    write(target / "secret.txt", "api_key=" + "a" * 24 + "\n")
    link = tmp_path / "linked"
    create_directory_link(link, target)
    try:
        result = secret_scan_gate.run(tmp_path)
    finally:
        remove_directory_link(link)

    assert result.passed is True


def test_repo_hygiene_gate_ignores_local_workspace(tmp_path: Path) -> None:
    write(tmp_path / "local" / "scratch.pyc", "")

    result = repo_hygiene_gate.run(tmp_path)

    assert result.passed is True


def test_repo_hygiene_gate_ignores_untracked_root_venv(tmp_path: Path) -> None:
    write(tmp_path / ".venv" / "pyvenv.cfg", "home = synthetic\n")

    result = repo_hygiene_gate.run(tmp_path)

    assert result.passed is True


def test_repo_hygiene_gate_rejects_force_tracked_root_venv(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    write(tmp_path / ".venv" / "pyvenv.cfg", "home = synthetic\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "-f", ".venv/pyvenv.cfg"],
        check=True,
    )

    result = repo_hygiene_gate.run(tmp_path)

    assert result.passed is False
    assert result.messages == [
        f"prohibited tracked root: {Path('.venv/pyvenv.cfg')}"
    ]


def test_repo_hygiene_gate_checks_nested_local_named_folders(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "local" / "scratch.pyc", "")

    result = repo_hygiene_gate.run(tmp_path)

    assert result.passed is False
    assert any("docs" in message and "local" in message for message in result.messages)


def test_repo_hygiene_iter_preserves_rglob_path_order(tmp_path: Path) -> None:
    write(tmp_path / "root.txt", "root\n")
    write(tmp_path / "alpha" / "alpha.txt", "alpha\n")
    write(tmp_path / "alpha" / "deep" / "deep.txt", "deep\n")
    write(tmp_path / "beta" / "beta.txt", "beta\n")
    write(tmp_path / "docs" / "local" / "nested.pyc", "")
    write(tmp_path / "docs" / "__pycache__" / "ignored.pyc", "")
    write(tmp_path / "local" / "ignored.pyc", "")
    expected = []
    for path in tmp_path.rglob("*"):
        relative_parts = path.relative_to(tmp_path).parts
        if relative_parts and relative_parts[0] in repo_hygiene_gate.ROOT_IGNORED_PATH_PARTS:
            continue
        if any(
            part in repo_hygiene_gate.IGNORED_PATH_PARTS
            for part in relative_parts
        ):
            continue
        if path.is_file():
            expected.append(path)

    actual = repo_hygiene_gate.iter_repo_files(tmp_path)

    assert [path.relative_to(tmp_path) for path in actual] == [
        path.relative_to(tmp_path) for path in expected
    ]


def test_repo_hygiene_iter_prunes_ignored_directories_before_visit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for relative in [
        ".git/deep/ignored.pyc",
        ".pytest_cache/deep/ignored.pyc",
        ".venv/deep/ignored.pyc",
        "local/deep/ignored.pyc",
        "docs/__pycache__/deep/ignored.pyc",
    ]:
        write(tmp_path / relative, "")
    write(tmp_path / "docs" / "visible.txt", "visible\n")
    original_walk = repo_hygiene_gate.os.walk
    visited: list[Path] = []

    def recording_walk(*args, **kwargs):
        for item in original_walk(*args, **kwargs):
            visited.append(Path(item[0]))
            yield item

    monkeypatch.setattr(repo_hygiene_gate.os, "walk", recording_walk)

    files = repo_hygiene_gate.iter_repo_files(tmp_path)

    assert [path.relative_to(tmp_path).as_posix() for path in files] == [
        "docs/visible.txt"
    ]
    for path in visited:
        relative = path.relative_to(tmp_path)
        assert not any(
            part in repo_hygiene_gate.IGNORED_PATH_PARTS
            for part in relative.parts
        )
        assert not (
            relative.parts
            and relative.parts[0] in repo_hygiene_gate.ROOT_IGNORED_PATH_PARTS
        )


def test_repo_hygiene_gate_prunes_directory_link_and_keeps_sibling(
    tmp_path: Path,
) -> None:
    target = tmp_path / "local" / "outside"
    write(target / "linked.pyc", "")
    link = tmp_path / "linked"
    create_directory_link(link, target)
    write(tmp_path / "docs" / "sibling.pyc", "")
    try:
        result = repo_hygiene_gate.run(tmp_path)
    finally:
        remove_directory_link(link)

    assert result.passed is False
    assert result.messages == [
        f"prohibited file suffix: {Path('docs/sibling.pyc')}"
    ]


def test_example_gate_requires_profile_phrases(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    example_dir = tmp_path / "examples" / "python_cli_minimal"
    for relative in example_gate.COMMON_REQUIRED_FILES:
        if relative == "template.config.yml":
            write(
                example_dir / relative,
                "project:\n  name: python_cli_minimal\n  status: seed\nprofile:\n  name: python_cli\nrender:\n  tier: full\n",
            )
        else:
            write(example_dir / relative, "# example\n")

    result = example_gate.run(tmp_path)

    assert result.passed is False
    assert any("pytest NOT RUN" in message for message in result.messages)


def test_example_render_drift_gate_detects_missing_rendered_file(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write_valid_example(tmp_path, "python_cli_minimal", "python_cli")
    (tmp_path / "examples" / "python_cli_minimal" / "SOURCE_INDEX.md").unlink()

    result = example_render_drift_gate.run(tmp_path)

    assert result.passed is False
    assert any("SOURCE_INDEX.md" in message for message in result.messages)


def test_example_render_drift_gate_respects_explicit_minimal_tier(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write_valid_example(tmp_path, "python_cli_minimal", "python_cli")
    config_path = tmp_path / "examples" / "python_cli_minimal" / "template.config.yml"
    write(config_path, config_path.read_text(encoding="utf-8").replace("tier: full", "tier: minimal"))
    (tmp_path / "examples" / "python_cli_minimal" / "SOURCE_INDEX.md").unlink()

    expected = example_render_drift_gate.expected_rendered_files(
        tmp_path, "python_cli_minimal"
    )

    assert all(path.name != "SOURCE_INDEX.md" for path in expected)


def test_rendered_golden_content_gate_detects_content_drift(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write(tmp_path / "templates" / "base" / "README.md.template", "# changed\n")

    result = rendered_golden_content_gate.run(tmp_path)

    assert result.passed is False
    assert any("README.md" in message for message in result.messages)


def test_rendered_golden_content_gate_rejects_unknown_tier(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    fixture_path = tmp_path / rendered_golden_content_gate.FIXTURE_RELATIVE
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture["render"]["tier"] = "unknown"
    write(fixture_path, json.dumps(fixture, indent=2) + "\n")

    result = rendered_golden_content_gate.run(tmp_path)

    assert result.passed is False
    assert "render tier must be one of" in result.messages[0]


def test_rendered_golden_content_gate_rejects_examples_fixture_paths(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    fixture = {
        "schema_version": "1",
        "render": {
            "project_name": "golden_render_python_cli",
            "project_status": "seed",
            "profile": "python_cli",
        },
        "hash_algorithm": "sha256",
        "newline_policy": "lf-normalized",
        "expected_files": [
            {
                "path": "examples/python_cli_minimal/README.md",
                "sha256": "0" * 64,
            }
        ],
    }
    write(tmp_path / rendered_golden_content_gate.FIXTURE_RELATIVE, json.dumps(fixture, indent=2) + "\n")

    result = rendered_golden_content_gate.run(tmp_path)

    assert result.passed is False
    assert any("not examples/" in message for message in result.messages)


def test_example_gate_validates_config_values(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write_valid_example(tmp_path, "python_cli_minimal", "python_cli")
    write(
        tmp_path / "examples" / "python_cli_minimal" / "template.config.yml",
        "project:\n  name: wrong_name\n  status: seed\nprofile:\n  name: python_cli\nrender:\n  tier: full\n",
    )

    result = example_gate.run(tmp_path)

    assert result.passed is False
    assert any("project.name=python_cli_minimal" in message for message in result.messages)


def test_example_gate_requires_plc_live_write_prohibited_in_policy(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write_valid_example(tmp_path, "plc_tool_minimal", "plc_or_device_tool")
    write(
        tmp_path / "examples" / "plc_tool_minimal" / "SAFETY_POLICY.profile.md",
        "simulator/mock first\nequipment IP ports tag live parameters\nstart stop reset mode change\n",
    )

    result = example_gate.run(tmp_path)

    assert result.passed is False
    assert any("live device write prohibited" in message for message in result.messages)


def test_quality_gate_passes_minimal_repo(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    for example_name, profile in example_gate.REQUIRED_EXAMPLES.items():
        write_valid_example(tmp_path, example_name, profile)

    summary = run_quality_gate(tmp_path)

    assert summary.passed is True
    assert len(summary.results) == 8
    assert summary.results[-1].name == "json_evidence_gate"


def test_core_quality_gate_ignores_optional_release_and_agent_quality_defects(
    tmp_path: Path,
) -> None:
    minimal_repo(tmp_path)
    for example_name, profile in example_gate.REQUIRED_EXAMPLES.items():
        write_valid_example(tmp_path, example_name, profile)
    write(
        tmp_path / generate_checksums.REQUIRED_RELEASE_ARTIFACTS[-1],
        "changed after checksum\n",
    )
    write(
        tmp_path / json_evidence_gate.AGENT_QUALITY_SCHEMA_PATHS[0],
        "{}\n",
    )

    summary = run_quality_gate(tmp_path)

    assert summary.passed is True
    assert json_evidence_gate.run(tmp_path).passed is False
    checksums_path = tmp_path / generate_checksums.DEFAULT_CHECKSUMS_PATH
    passed, _ = generate_checksums.verify_checksums(
        tmp_path,
        tmp_path / generate_checksums.DEFAULT_MANIFEST_PATH,
        checksums_path,
    )
    assert passed is False
