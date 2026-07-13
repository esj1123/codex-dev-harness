import json
from pathlib import Path

from scripts import generate_checksums
from scripts.gates import (
    docs_gate,
    example_gate,
    example_render_drift_gate,
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

PYTHON_CLI_PROFILE_TEMPLATES = [
    "profiles/python_cli/AGENTS.override.md.template",
    "profiles/python_cli/README.profile.md.template",
    "profiles/python_cli/SAFETY_POLICY.profile.md.template",
    "profiles/python_cli/STATUS.profile.md.template",
    "profiles/python_cli/VERIFICATION.profile.md.template",
]


def write(path: Path, content: str = REQUIRED_DOC_CONTENT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_repo(root: Path) -> None:
    for relative in docs_gate.REQUIRED_DOCS:
        write(root / relative)
    for relative in template_schema_gate.REQUIRED_BASE_TEMPLATES:
        write(root / relative)
    for relative in PYTHON_CLI_PROFILE_TEMPLATES:
        write(root / relative, "profile {{ profile.name }} for {{ project.name }}\n")
    write(
        root / "template.config.example.yml",
        "project:\n  name: demo\n  status: seed\nprofile:\n  name: python_cli\n",
    )
    write_golden_render_fixture(root)
    write_checksum_fixture(root)


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
    config = TemplateConfig(project_name="golden_render_python_cli", project_status="seed", profile="python_cli")
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
    assert len(docs_gate.REQUIRED_DOCS) == len(required_docs)


def test_readme_describes_installed_manual_local_verify_workflow() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "manual read-only `.github/workflows/local-verify.yml` workflow" in text
    assert "`workflow_dispatch` with `contents: read`" in text
    assert "installed manual read-only Local Verify workflow is the verification hygiene" in text
    assert "next planned CI step is a read-only verification hygiene path" not in text


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


def test_repo_hygiene_gate_ignores_local_workspace(tmp_path: Path) -> None:
    write(tmp_path / "local" / "scratch.pyc", "")

    result = repo_hygiene_gate.run(tmp_path)

    assert result.passed is True


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
    assert len(summary.results) == 9
    assert summary.results[-1].name == "checksum_verify_gate"
