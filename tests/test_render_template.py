from pathlib import Path

import pytest

from scripts import ai_readiness_scanner as scanner
from scripts.render_template import load_config, render_templates


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_load_config_requires_seed_status(tmp_path: Path) -> None:
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\nprofile:\n  name: python_cli\n", encoding="utf-8")

    loaded = load_config(config)

    assert loaded.project_name == "demo"
    assert loaded.project_status == "seed"
    assert loaded.profile == "python_cli"


def test_load_config_rejects_non_seed_status(tmp_path: Path) -> None:
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: draft\n", encoding="utf-8")

    with pytest.raises(ValueError, match="status: seed"):
        load_config(config)


def test_render_templates_dry_run_does_not_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    write(repo / "profiles/python_cli/README.profile.md.template", "profile {{ profile.name }}\n")
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\nprofile:\n  name: python_cli\n", encoding="utf-8")
    target = tmp_path / "target"

    rendered = render_templates(config_path=config, target=target, repo_root=repo, dry_run=True)

    assert target.exists() is False
    assert target / "README.md" in rendered
    assert "DRY-RUN render" in capsys.readouterr().out


def test_render_templates_writes_base_and_profile(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    write(repo / "profiles/python_cli/README.profile.md.template", "profile {{ profile.name }}\n")
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\nprofile:\n  name: python_cli\n", encoding="utf-8")
    target = tmp_path / "target"

    render_templates(config_path=config, target=target, repo_root=repo, dry_run=False)

    assert (target / "README.md").read_text(encoding="utf-8") == "# demo\n"
    assert (target / "README.profile.md").read_text(encoding="utf-8") == "profile python_cli\n"


def test_render_refuses_repo_root_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# demo\n")
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="template repository itself"):
        render_templates(config_path=config, target=repo, repo_root=repo, dry_run=True)


def test_render_refuses_repo_internal_target_outside_examples(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# demo\n")
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside examples/<name>"):
        render_templates(config_path=config, target=repo / "src", repo_root=repo, dry_run=True)


def test_render_refuses_examples_root_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# demo\n")
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside examples/<name>"):
        render_templates(config_path=config, target=repo / "examples", repo_root=repo, dry_run=True)


def test_render_refuses_nested_examples_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# demo\n")
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="outside examples/<name>"):
        render_templates(config_path=config, target=repo / "examples" / "demo" / "nested", repo_root=repo, dry_run=True)


def test_render_allows_examples_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")
    target = repo / "examples" / "demo"

    rendered = render_templates(config_path=config, target=target, repo_root=repo, dry_run=True)

    assert target / "README.md" in rendered
    assert target.exists() is False


def test_rendered_profile_contract_matches_scanner_layout(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config = tmp_path / "template.config.yml"
    config.write_text(
        "project:\n  name: rendered_demo\n  status: seed\nprofile:\n  name: python_cli\n",
        encoding="utf-8",
    )
    target = tmp_path / "rendered_demo"

    render_templates(config_path=config, target=target, repo_root=repo_root, dry_run=False)

    rendered_files = {
        "AGENTS.override.md",
        "PRODUCT.md",
        "MVP.md",
        "PROJECT_BOUNDARY.md",
        "DATA_SCOPE.md",
        "APPROVALS.md",
        "PHASE_PLAN.md",
        "STATUS.md",
        "ACCEPTANCE_TRACE.md",
        "SOURCE_INDEX.md",
        "SAFETY_POLICY.profile.md",
        "VERIFICATION.profile.md",
    }
    assert all((target / relative).is_file() for relative in rendered_files)

    broken_refs = {
        "docs/SAFETY_POLICY.md",
        "docs/VERIFICATION.md",
        "docs/PROFILE_MATRIX.md",
        "docs/AI_HANDOFF.md",
    }
    for relative in ["AGENTS.md", "README.md", "AGENTS.override.md"]:
        text = (target / relative).read_text(encoding="utf-8")
        assert not any(reference in text for reference in broken_refs)
        assert "SAFETY_POLICY.profile.md" in text
        assert "VERIFICATION.profile.md" in text

    result = scanner.scan_target(target)
    safety = next(dimension for dimension in result.dimensions if dimension.name == "Safety boundary")
    verification = next(dimension for dimension in result.dimensions if dimension.name == "Verification script")
    assert result.score >= 13
    assert safety.status == "PASS"
    assert verification.status != "INSUFFICIENT_EVIDENCE"
