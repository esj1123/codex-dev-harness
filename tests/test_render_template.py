import json
from pathlib import Path

import pytest

from scripts import ai_readiness_scanner as scanner
from scripts.render_template import MAX_DIFF_PREVIEW_PATHS, load_config, main, render_templates


TIER_CONTRACT = Path(__file__).resolve().parents[1] / "docs" / "RENDER_TIER_CONTRACT.md"


def tier_contract_text() -> str:
    return TIER_CONTRACT.read_text(encoding="utf-8")


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


def test_render_templates_dry_run_provenance_preview_is_safe_and_deterministic(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    config = repo / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")
    target = repo / "examples" / "demo"

    render_templates(
        config_path=config,
        target=target,
        repo_root=repo,
        dry_run=True,
        provenance_preview=True,
    )

    output = capsys.readouterr().out
    prefix = "DRY-RUN provenance-preview "
    preview_line = next(line for line in output.splitlines() if line.startswith(prefix))
    preview_json = preview_line.removeprefix(prefix)
    preview = json.loads(preview_json)

    assert preview == {
        "config_source": "template.config.yml",
        "harness_commit": "UNKNOWN",
        "mode": "DRY_RUN_PREVIEW",
        "output_policy": "no_provenance_stamp_written",
        "render_profile": "base",
        "rendered_file_count": 1,
        "schema_version": "render_provenance_preview.v0",
        "target_root": "examples/demo",
    }
    assert preview_json == json.dumps(preview, sort_keys=True, separators=(",", ":"))
    assert str(tmp_path) not in preview_json
    assert "\\" not in preview_json
    assert target.exists() is False


def test_render_templates_provenance_preview_summarizes_external_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    write(repo / "profiles/python_cli/README.profile.md.template", "profile {{ profile.name }}\n")
    config = tmp_path / "external" / "template.config.yml"
    write(config, "project:\n  name: demo\n  status: seed\nprofile:\n  name: python_cli\n")
    target = tmp_path / "external-target"

    render_templates(
        config_path=config,
        target=target,
        repo_root=repo,
        dry_run=True,
        provenance_preview=True,
    )

    output = capsys.readouterr().out
    preview_line = next(line for line in output.splitlines() if line.startswith("DRY-RUN provenance-preview "))
    preview = json.loads(preview_line.removeprefix("DRY-RUN provenance-preview "))

    assert preview["config_source"] == "external_config"
    assert preview["target_root"] == "external_target"
    assert preview["render_profile"] == "python_cli"
    assert str(tmp_path) not in preview_line
    assert target.exists() is False


def test_render_templates_provenance_preview_is_dry_run_only(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    config = repo / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="provenance preview is dry-run only"):
        render_templates(
            config_path=config,
            target=tmp_path / "target",
            repo_root=repo,
            dry_run=False,
            provenance_preview=True,
        )


def test_render_template_cli_provenance_preview_requires_dry_run(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    config = repo / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="provenance preview is dry-run only"):
        main(
            [
                "--repo-root",
                str(repo),
                "--config",
                str(config),
                "--target",
                str(tmp_path / "target"),
                "--provenance-preview",
            ]
        )


def test_render_templates_dry_run_diff_preview_reports_summary_without_raw_content(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/GUIDE.md.template", "expected {{ project.name }}\n")
    write(repo / "templates/base/MISSING.md.template", "missing {{ project.name }}\n")
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    config = repo / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")
    target = repo / "examples" / "demo"
    write(target / "README.md", "# demo\n")
    write(target / "GUIDE.md", "PRIVATE RAW TARGET CONTENT\n")

    render_templates(config_path=config, target=target, repo_root=repo, dry_run=True, diff_preview=True)

    output = capsys.readouterr().out
    prefix = "DRY-RUN diff-preview "
    preview_line = next(line for line in output.splitlines() if line.startswith(prefix))
    preview_json = preview_line.removeprefix(prefix)
    preview = json.loads(preview_json)

    assert preview == {
        "changed_count": 1,
        "changed_paths": ["GUIDE.md"],
        "missing_count": 1,
        "missing_paths": ["MISSING.md"],
        "mode": "DRY_RUN_PREVIEW",
        "output_policy": "no_files_written",
        "paths_truncated": False,
        "rendered_file_count": 3,
        "schema_version": "render_diff_preview.v0",
        "unchanged_count": 1,
    }
    assert preview_json == json.dumps(preview, sort_keys=True, separators=(",", ":"))
    assert "PRIVATE RAW TARGET CONTENT" not in preview_json
    assert str(tmp_path) not in preview_json
    assert "\\" not in preview_json
    assert (target / "GUIDE.md").read_text(encoding="utf-8") == "PRIVATE RAW TARGET CONTENT\n"
    assert (target / "MISSING.md").exists() is False


def test_render_templates_dry_run_diff_preview_bounds_path_lists(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    for index in range(MAX_DIFF_PREVIEW_PATHS + 2):
        write(repo / "templates/base" / f"file_{index:02}.md.template", f"file {index}\n")
    config = repo / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")
    target = repo / "examples" / "demo"

    render_templates(config_path=config, target=target, repo_root=repo, dry_run=True, diff_preview=True)

    output = capsys.readouterr().out
    preview_line = next(line for line in output.splitlines() if line.startswith("DRY-RUN diff-preview "))
    preview = json.loads(preview_line.removeprefix("DRY-RUN diff-preview "))

    assert preview["rendered_file_count"] == MAX_DIFF_PREVIEW_PATHS + 2
    assert preview["missing_count"] == MAX_DIFF_PREVIEW_PATHS + 2
    assert preview["changed_count"] == 0
    assert preview["unchanged_count"] == 0
    assert len(preview["missing_paths"]) == MAX_DIFF_PREVIEW_PATHS
    assert preview["changed_paths"] == []
    assert preview["paths_truncated"] is True
    assert str(tmp_path) not in preview_line


def test_render_templates_diff_preview_is_dry_run_only(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    config = repo / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="diff preview is dry-run only"):
        render_templates(
            config_path=config,
            target=tmp_path / "target",
            repo_root=repo,
            dry_run=False,
            diff_preview=True,
        )


def test_render_template_cli_diff_preview_requires_dry_run(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write(repo / "templates/base/README.md.template", "# {{ project.name }}\n")
    config = repo / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: seed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="diff preview is dry-run only"):
        main(
            [
                "--repo-root",
                str(repo),
                "--config",
                str(config),
                "--target",
                str(tmp_path / "target"),
                "--diff-preview",
            ]
        )


def test_render_tier_contract_is_docs_only_before_implementation() -> None:
    text = tier_contract_text()

    assert "documentation and focused-test only" in text
    for blocked_surface in [
        "`scripts/render_template.py`",
        "generated examples",
        "quality gates",
        "workflows",
        "artifacts",
        "downstream repositories",
    ]:
        assert blocked_surface in text


def test_render_tier_contract_defines_minimal_standard_full() -> None:
    text = tier_contract_text()

    for tier in ["`minimal`", "`standard`", "`full`"]:
        assert tier in text
    for minimal_doc in [
        "`AGENTS.md`",
        "`README.md`",
        "`PRODUCT.md`",
        "`MVP.md`",
        "`PROJECT_BOUNDARY.md`",
    ]:
        assert minimal_doc in text
    assert "All currently rendered base templates and all selected profile templates" in text


def test_render_tier_contract_preserves_default_preview_and_safety_rules() -> None:
    text = tier_contract_text()

    for required_phrase in [
        "`render.tier`",
        "omitted tier as `full`",
        "Unknown values must fail closed",
        "`--dry-run`",
        "`--provenance-preview`",
        "`--diff-preview`",
        "no automatic target overwrite",
        "no raw target content in preview output",
        "no local absolute paths",
    ]:
        assert required_phrase in text

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
