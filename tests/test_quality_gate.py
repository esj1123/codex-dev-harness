from pathlib import Path

from scripts.gates import docs_gate, secret_scan_gate, template_schema_gate
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


def test_quality_gate_passes_minimal_repo(tmp_path: Path) -> None:
    minimal_repo(tmp_path)

    summary = run_quality_gate(tmp_path)

    assert summary.passed is True
