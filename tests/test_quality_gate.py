from pathlib import Path

from scripts.gates import docs_gate, example_gate, example_render_drift_gate, repo_hygiene_gate, secret_scan_gate, template_schema_gate
from scripts.quality_gate import run_quality_gate


REQUIRED_DOC_CONTENT = "# doc\n"


def write(path: Path, content: str = REQUIRED_DOC_CONTENT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def minimal_repo(root: Path) -> None:
    for relative in docs_gate.REQUIRED_DOCS:
        write(root / relative)
    for relative in template_schema_gate.REQUIRED_BASE_TEMPLATES:
        write(root / relative)
    write(
        root / "template.config.example.yml",
        "project:\n  name: demo\n  status: seed\nprofile:\n  name: python_cli\n",
    )


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
