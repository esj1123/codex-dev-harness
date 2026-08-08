import json
from pathlib import Path
import subprocess

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


def write(path: Path, content: str = REQUIRED_DOC_CONTENT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_repo(root: Path) -> None:
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
            extra_safety = "  live_device_write: prohibited\n" if example_name == "plc_tool_minimal" else ""
            write(
                example_dir / relative,
                "project:\n"
                f"  name: {example_name}\n"
                "  status: seed\n"
                "profile:\n"
                f"  name: {profile}\n"
                "paths:\n"
                f"  target: examples/{example_name}\n"
                "safety:\n"
                f"{extra_safety}",
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
    assert len(docs_gate.BASELINE_REQUIRED_DOCS) == 76
    assert len(docs_gate.REQUIRED_DOCS) == 77
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
    policy = Path("docs/CI_POLICY.md").read_text(encoding="utf-8")
    impact_map = json.loads(
        Path("docs/VERIFICATION_IMPACT_MAP.json").read_text(encoding="utf-8")
    )

    assert "The V2 core is always" in policy
    assert "impact-required extras" in policy
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
        assert f"`{command_id}`" in policy


def test_readme_describes_installed_manual_local_verify_workflow() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "manual read-only `.github/workflows/local-verify.yml` workflow" in text
    assert "`workflow_dispatch` with a required exact commit SHA" in text
    assert "`contents: read`" in text
    assert "installed manual read-only Local Verify workflow is the verification hygiene" in text
    assert "next planned CI step is a read-only verification hygiene path" not in text


def test_operational_docs_match_current_core_and_release_state() -> None:
    status = Path("STATUS.md").read_text(encoding="utf-8")
    usage = Path("docs/LOCAL_USAGE.md").read_text(encoding="utf-8")
    checklist = Path("docs/LOCAL_PACKAGE_CHECKLIST.md").read_text(encoding="utf-8")
    runtime = Path("docs/PYTHON_RUNTIME_POLICY.md").read_text(encoding="utf-8")
    normalized_checklist = " ".join(checklist.split())

    assert "`CORE_HARNESS_READY`" in status
    assert "Review the verified P1 branch tip" in status
    assert "decide whether to promote it to `main`" in status
    assert "decide whether it should include an eval report" in status
    assert "Complete the core-only integration checks" not in status

    assert "manual read-only `.github/workflows/local-verify.yml`" in usage
    assert "`workflow_dispatch` with an exact commit SHA" in usage
    assert "is not automatic and is not a required check" in usage
    assert usage.index("full `python -m pytest tests`") < usage.index(
        "standalone `python scripts/run_eval.py`"
    ) < usage.index("core `python scripts/quality_gate.py`") < usage.index(
        "profile render dry-runs"
    )
    assert "requirements-dev.txt" in usage
    assert "requirements-dev.lock" in usage
    assert "python -m pip check" in usage

    assert "local release generators" in checklist
    assert "`HISTORICAL_INVALID / REFRESH_NOT_RUN`" in checklist
    assert (
        "separate artifact-regeneration and package-inclusion approval"
        in normalized_checklist
    )
    assert "This checklist does not run them" in checklist

    assert "focused development and narrow test commands" in runtime
    assert "exact V2 verification run" in runtime
    assert runtime.index("python -m pip install -r requirements-dev.lock") < runtime.index(
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
        "docs/RELEASE_AUTOMATION_CANDIDATE_CONTRACT.md",
        "docs/RELEASE_AUTOMATION_PROVENANCE_BOUNDARY_REVIEW.md",
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
    assert "Follow `STATUS.md` for the active" in roadmap
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


def test_acceptance_trace_is_historical_through_last_existing_checkpoint() -> None:
    text = Path("ACCEPTANCE_TRACE.md").read_text(encoding="utf-8")

    assert "AT-001 through AT-282 are preserved as historical" in text
    assert "`docs/AUTHORITY_MANIFEST.json`" in text
    assert "| AT-281 | current checkpoint |" in text
    assert text.count("| AT-282 | current checkpoint |") == 1
    assert "| AT-283 |" not in text


def test_local_verify_runs_console_eval_with_narrow_boundary() -> None:
    text = Path(".github/workflows/local-verify.yml").read_text(encoding="utf-8")
    tests_command = "run: python -m pytest tests --durations=50 -rs"
    eval_command = "run: python scripts/run_eval.py"
    quality_gate_command = "run: python scripts/quality_gate.py"

    assert "workflow_dispatch:" in text
    assert "expected_sha:" in text
    assert "required: true" in text
    assert "ref: ${{ inputs.expected_sha }}" in text
    assert "git rev-parse HEAD" in text
    assert "^[0-9a-f]{40}$" in text
    assert "permissions:\n  contents: read" in text
    assert "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09" in text
    assert "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1" in text
    assert "persist-credentials: false" in text
    assert 'python-version: "3.12.10"' in text
    assert "python-version-file:" not in text
    assert "check-latest: false" in text
    assert "python -m pip install -r requirements-dev.lock" in text
    assert "python -m pip check" in text
    assert 'PYTEST_DISABLE_PLUGIN_AUTOLOAD: "1"' in text
    assert 'PYTEST_ADDOPTS: ""' in text
    assert 'PYTEST_PLUGINS: ""' in text
    assert 'PYTHONPATH: ""' in text
    assert text.count(eval_command) == 1
    assert (
        text.index("python -m pip install -r requirements-dev.lock")
        < text.index("python -m pip check")
        < text.index(tests_command)
        < text.index(eval_command)
        < text.index(quality_gate_command)
    )
    for forbidden in [
        "--report",
        "--summary-report",
        "--cases-report",
        "upload-artifact",
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
    write(tmp_path / "README.md", "-----BEGIN " + "PRIVATE KEY-----\n")

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert "README.md" in result.messages[0]


def test_secret_scan_gate_ignores_local_workspace(tmp_path: Path) -> None:
    write(tmp_path / "local" / "scratch.md", "-----BEGIN " + "PRIVATE KEY-----\n")

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is True


def test_secret_scan_gate_checks_nested_local_named_folders(tmp_path: Path) -> None:
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
    write(tmp_path / relative_path, "api_key=" + "a" * 24 + "\n")

    result = secret_scan_gate.run(tmp_path)

    assert result.passed is False
    assert any(relative_path in message for message in result.messages)


@pytest.mark.parametrize("root_name", [".venv", "venv", "local"])
def test_secret_scan_gate_ignores_root_local_environments(
    tmp_path: Path, root_name: str
) -> None:
    write(
        tmp_path / root_name / "nested" / "config.json",
        "api_key=" + "a" * 24 + "\n",
    )

    assert secret_scan_gate.run(tmp_path).passed is True


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


def test_example_gate_requires_profile_phrases(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    example_dir = tmp_path / "examples" / "python_cli_minimal"
    for relative in example_gate.COMMON_REQUIRED_FILES:
        if relative == "template.config.yml":
            write(
                example_dir / relative,
                "project:\n  name: python_cli_minimal\n  status: seed\nprofile:\n  name: python_cli\npaths:\n  target: examples/python_cli_minimal\n",
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
        "project:\n  name: wrong_name\n  status: seed\nprofile:\n  name: python_cli\npaths:\n  target: examples/python_cli_minimal\n",
    )

    result = example_gate.run(tmp_path)

    assert result.passed is False
    assert any("project.name=python_cli_minimal" in message for message in result.messages)


def test_example_gate_requires_plc_live_write_prohibited(tmp_path: Path) -> None:
    minimal_repo(tmp_path)
    write_valid_example(tmp_path, "plc_tool_minimal", "plc_or_device_tool")
    write(
        tmp_path / "examples" / "plc_tool_minimal" / "template.config.yml",
        "project:\n  name: plc_tool_minimal\n  status: seed\nprofile:\n  name: plc_or_device_tool\npaths:\n  target: examples/plc_tool_minimal\nsafety:\n  live_device_write: allowed\n",
    )

    result = example_gate.run(tmp_path)

    assert result.passed is False
    assert any("safety.live_device_write=prohibited" in message for message in result.messages)


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
