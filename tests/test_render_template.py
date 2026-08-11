import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
from types import SimpleNamespace

import pytest

from scripts import ai_readiness_scanner as scanner
from scripts import render_template as renderer
from scripts.render_template import (
    CANONICAL_READ_ORDER,
    MAX_DIFF_PREVIEW_PATHS,
    VALID_RENDER_TIERS,
    build_render_diff_preview,
    load_config,
    main,
    render_templates,
)


TIER_CONTRACT = Path(__file__).resolve().parents[1] / "docs" / "RENDER_TIER_CONTRACT.md"


def tier_contract_text() -> str:
    return TIER_CONTRACT.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


EXPECTED_BASE_OUTPUTS = {
    "minimal": (
        "AGENTS.md",
        "README.md",
        "PRODUCT.md",
        "MVP.md",
        "PROJECT_BOUNDARY.md",
    ),
    "standard": (
        "AGENTS.md",
        "README.md",
        "PRODUCT.md",
        "MVP.md",
        "PROJECT_BOUNDARY.md",
        "DATA_SCOPE.md",
        "APPROVALS.md",
        "PHASE_PLAN.md",
        "STATUS.md",
        "ACCEPTANCE_TRACE.md",
    ),
    "full": (
        "AGENTS.md",
        "README.md",
        "PRODUCT.md",
        "MVP.md",
        "PROJECT_BOUNDARY.md",
        "DATA_SCOPE.md",
        "APPROVALS.md",
        "PHASE_PLAN.md",
        "STATUS.md",
        "ACCEPTANCE_TRACE.md",
        "SOURCE_INDEX.md",
    ),
}

EXPECTED_PROFILE_OUTPUTS = {
    "minimal": (
        "AGENTS.override.md",
        "SAFETY_POLICY.profile.md",
        "VERIFICATION.profile.md",
    ),
    "standard": (
        "AGENTS.override.md",
        "STATUS.profile.md",
        "SAFETY_POLICY.profile.md",
        "VERIFICATION.profile.md",
    ),
    "full": (
        "AGENTS.override.md",
        "README.profile.md",
        "STATUS.profile.md",
        "SAFETY_POLICY.profile.md",
        "VERIFICATION.profile.md",
    ),
}

PROFILES = ("python_cli", "csharp_desktop", "plc_or_device_tool")


def populate_template_repo(repo: Path, profile: str | None = None) -> None:
    orientation = (
        "# {{ project.name }}\n\n"
        "## Read Order\n\n"
        "{{ render.read_order }}\n\n"
        "## Next\n\n"
        "Synthetic orientation.\n"
    )
    for name in EXPECTED_BASE_OUTPUTS["full"]:
        content = orientation if name in {"AGENTS.md", "README.md"} else f"# {name} for {{{{ project.name }}}}\n"
        write(repo / "templates" / "base" / f"{name}.template", content)

    if profile is None:
        return

    for name in EXPECTED_PROFILE_OUTPUTS["full"]:
        content = (
            orientation
            if name == "AGENTS.override.md"
            else f"# {name} for {{{{ profile.name }}}}\n"
        )
        write(repo / "profiles" / profile / f"{name}.template", content)


def write_config(path: Path, *, tier: str | None = None, profile: str | None = None) -> None:
    text = "project:\n  name: demo\n  status: seed\n"
    if profile is not None:
        text += f"profile:\n  name: {profile}\n"
    if tier is not None:
        text += f"render:\n  tier: {tier}\n"
    write(path, text)


def expected_output_names(tier: str, profile: str | None) -> set[str]:
    names = set(EXPECTED_BASE_OUTPUTS[tier])
    if profile is not None:
        names.update(EXPECTED_PROFILE_OUTPUTS[tier])
    return names


def read_order_entries(text: str) -> list[str]:
    section = text.split("## Read Order\n\n", 1)[1].split("\n\n##", 1)[0]
    entries: list[str] = []
    for expected_number, line in enumerate(section.splitlines(), start=1):
        number, name = line.split(". ", 1)
        assert number == str(expected_number)
        entries.append(name)
    return entries


def test_load_config_requires_seed_status(tmp_path: Path) -> None:
    config = tmp_path / "template.config.yml"
    write_config(config, profile="python_cli")

    loaded = load_config(config)

    assert loaded.project_name == "demo"
    assert loaded.project_status == "seed"
    assert loaded.profile == "python_cli"
    assert loaded.tier == "full"


def test_load_config_rejects_non_seed_status(tmp_path: Path) -> None:
    config = tmp_path / "template.config.yml"
    config.write_text("project:\n  name: demo\n  status: draft\n", encoding="utf-8")

    with pytest.raises(ValueError, match="status: seed"):
        load_config(config)


@pytest.mark.parametrize(
    "profile",
    [
        ".",
        "..",
        "../python_cli",
        "profiles/python_cli",
        "profiles\\python_cli",
        "C:\\profiles\\python_cli",
        "//server/share",
        "-leading",
        "a" * 65,
    ],
)
def test_load_config_rejects_path_like_or_invalid_profile_name(
    tmp_path: Path,
    profile: str,
) -> None:
    config = tmp_path / "template.config.yml"
    write_config(config, profile=profile)

    with pytest.raises(ValueError, match="profile name must match"):
        load_config(config)


@pytest.mark.parametrize("profile", ["Python_Cli", "PYTHON_CLI"])
def test_render_rejects_wrong_case_profile_alias_on_every_os(
    tmp_path: Path, profile: str
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo, "python_cli")
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal", profile=profile)
    target = tmp_path / "target"

    with pytest.raises(ValueError, match="exactly match profiles/ inventory"):
        render_templates(
            config_path=config,
            target=target,
            repo_root=repo,
            dry_run=False,
        )

    assert target.exists() is False


def test_profile_inventory_rejects_casefold_collision_on_every_os() -> None:
    directories = [
        Path("profiles") / "python_cli",
        Path("profiles") / "PYTHON_CLI",
    ]

    with pytest.raises(ValueError, match="casefold collision"):
        renderer._select_profile_from_inventory("python_cli", directories)


@pytest.mark.parametrize("tier", VALID_RENDER_TIERS)
def test_load_config_accepts_explicit_render_tier(tmp_path: Path, tier: str) -> None:
    config = tmp_path / "template.config.yml"
    write_config(config, tier=tier)

    assert load_config(config).tier == tier


@pytest.mark.parametrize("tier", ["unknown", ""])
def test_load_config_rejects_invalid_render_tier(tmp_path: Path, tier: str) -> None:
    config = tmp_path / "template.config.yml"
    write_config(config, tier=tier)

    with pytest.raises(ValueError, match="render tier must be one of"):
        load_config(config)


def test_render_templates_dry_run_does_not_write(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo, "python_cli")
    config = tmp_path / "template.config.yml"
    write_config(config, profile="python_cli")
    target = tmp_path / "target"

    rendered = render_templates(config_path=config, target=target, repo_root=repo, dry_run=True)

    assert target.exists() is False
    assert len(rendered) == 16
    assert target / "README.md" in rendered
    assert "DRY-RUN render" in capsys.readouterr().out


def test_cli_no_flag_and_dry_run_are_identical_preview(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"
    common = [
        "--repo-root",
        str(repo),
        "--config",
        str(config),
        "--target",
        str(target),
    ]

    assert main(common) == 0
    default_output = capsys.readouterr().out
    assert main([*common, "--dry-run"]) == 0
    explicit_output = capsys.readouterr().out

    assert default_output == explicit_output
    assert target.exists() is False


def test_cli_apply_writes_preflighted_plan(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"

    assert main(
        [
            "--repo-root",
            str(repo),
            "--config",
            str(config),
            "--target",
            str(target),
            "--apply",
        ]
    ) == 0

    assert (target / "README.md").is_file()


@pytest.mark.parametrize(
    "mode_args",
    [
        ("--apply", "--dry-run"),
        ("--apply", "--provenance-preview"),
        ("--apply", "--diff-preview"),
        ("--force",),
    ],
)
def test_cli_rejects_incompatible_apply_modes_before_writing(
    tmp_path: Path,
    mode_args: tuple[str, ...],
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "--repo-root",
                str(repo),
                "--config",
                str(config),
                "--target",
                str(target),
                *mode_args,
            ]
        )

    assert exc_info.value.code == 2
    assert target.exists() is False


def test_render_templates_dry_run_provenance_preview_is_safe_and_deterministic(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = repo / "template.config.yml"
    write_config(config)
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
        "rendered_file_count": 11,
        "schema_version": "render_provenance_preview.v0",
        "target_root": "examples/demo",
    }
    assert preview_json == json.dumps(preview, sort_keys=True, separators=(",", ":"))
    assert "render_tier" not in preview
    assert str(tmp_path) not in preview_json
    assert "\\" not in preview_json
    assert target.exists() is False


def test_render_templates_provenance_preview_summarizes_external_paths(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo, "python_cli")
    config = tmp_path / "external" / "template.config.yml"
    write_config(config, profile="python_cli")
    target = tmp_path / "external-target"

    render_templates(
        config_path=config,
        target=target,
        repo_root=repo,
        dry_run=True,
        provenance_preview=True,
    )

    output = capsys.readouterr().out
    preview_line = next(
        line for line in output.splitlines() if line.startswith("DRY-RUN provenance-preview ")
    )
    preview = json.loads(preview_line.removeprefix("DRY-RUN provenance-preview "))

    assert preview["config_source"] == "external_config"
    assert preview["target_root"] == "external_target"
    assert preview["render_profile"] == "python_cli"
    assert preview["rendered_file_count"] == 16
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


def test_render_template_cli_provenance_preview_uses_default_preview(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = repo / "template.config.yml"
    write_config(config, tier="minimal")

    target = tmp_path / "target"
    assert main(
        [
            "--repo-root",
            str(repo),
            "--config",
            str(config),
            "--target",
            str(target),
            "--provenance-preview",
        ]
    ) == 0
    assert target.exists() is False


def test_render_templates_dry_run_diff_preview_reports_summary_without_raw_content(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = repo / "template.config.yml"
    write_config(config, tier="minimal")
    target = repo / "examples" / "demo"
    write(target / "PRODUCT.md", "# PRODUCT.md for demo\n")
    write(target / "MVP.md", "PRIVATE RAW TARGET CONTENT\n")

    render_templates(config_path=config, target=target, repo_root=repo, dry_run=True, diff_preview=True)

    output = capsys.readouterr().out
    prefix = "DRY-RUN diff-preview "
    preview_line = next(line for line in output.splitlines() if line.startswith(prefix))
    preview_json = preview_line.removeprefix(prefix)
    preview = json.loads(preview_json)

    assert preview == {
        "changed_count": 1,
        "changed_paths": ["MVP.md"],
        "missing_count": 3,
        "missing_paths": ["AGENTS.md", "PROJECT_BOUNDARY.md", "README.md"],
        "mode": "DRY_RUN_PREVIEW",
        "output_policy": "no_files_written",
        "paths_truncated": False,
        "rendered_file_count": 5,
        "schema_version": "render_diff_preview.v0",
        "unchanged_count": 1,
    }
    assert preview_json == json.dumps(preview, sort_keys=True, separators=(",", ":"))
    assert "PRIVATE RAW TARGET CONTENT" not in preview_json
    assert str(tmp_path) not in preview_json
    assert "\\" not in preview_json
    assert (target / "MVP.md").read_text(encoding="utf-8") == "PRIVATE RAW TARGET CONTENT\n"
    assert (target / "AGENTS.md").exists() is False


def test_render_templates_diff_preview_normalizes_relative_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = repo / "template.config.yml"
    write_config(config, tier="minimal")
    monkeypatch.chdir(tmp_path)

    rendered = render_templates(
        config_path=config,
        target=Path("rendered"),
        repo_root=repo,
        dry_run=True,
        diff_preview=True,
    )

    assert rendered
    assert all(path.is_absolute() for path in rendered)
    assert (tmp_path / "rendered").exists() is False


def test_render_templates_dry_run_diff_preview_bounds_path_lists(tmp_path: Path) -> None:
    target = tmp_path / "target"
    expected_rendered = [
        (target / f"file_{index:02}.md", f"file {index}\n")
        for index in range(MAX_DIFF_PREVIEW_PATHS + 2)
    ]

    preview = build_render_diff_preview(expected_rendered=expected_rendered, target=target)

    assert preview["rendered_file_count"] == MAX_DIFF_PREVIEW_PATHS + 2
    assert preview["missing_count"] == MAX_DIFF_PREVIEW_PATHS + 2
    assert preview["changed_count"] == 0
    assert preview["unchanged_count"] == 0
    assert len(preview["missing_paths"]) == MAX_DIFF_PREVIEW_PATHS
    assert preview["changed_paths"] == []
    assert preview["paths_truncated"] is True
    assert str(tmp_path) not in json.dumps(preview)


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


def test_render_template_cli_diff_preview_uses_default_preview(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = repo / "template.config.yml"
    write_config(config, tier="minimal")

    target = tmp_path / "target"
    assert main(
        [
            "--repo-root",
            str(repo),
            "--config",
            str(config),
            "--target",
            str(target),
            "--diff-preview",
        ]
    ) == 0
    assert target.exists() is False


def test_render_tier_contract_records_implemented_scope() -> None:
    text = tier_contract_text()

    assert "`render_tier_selection_implemented`" in text
    for required_surface in [
        "config/CLI precedence",
        "exact file planning",
        "tier-specific Read Order generation",
        "focused readiness checks",
    ]:
        assert required_surface in text
    for blocked_surface in [
        "curated example regeneration",
        "workflow or release changes",
        "artifact generation",
        "downstream repository access",
        "external template execution",
    ]:
        assert blocked_surface in text


def test_render_tier_contract_defines_minimal_standard_full() -> None:
    text = tier_contract_text()

    expected_rows = [
        "| `minimal` | `AGENTS.md`, `README.md`, `PRODUCT.md`, `MVP.md`, `PROJECT_BOUNDARY.md` | "
        "`AGENTS.override.md`, `SAFETY_POLICY.profile.md`, `VERIFICATION.profile.md` | 5 base / 8 profiled |",
        "| `standard` | `AGENTS.md`, `README.md`, `PRODUCT.md`, `MVP.md`, `PROJECT_BOUNDARY.md`, "
        "`DATA_SCOPE.md`, `APPROVALS.md`, `PHASE_PLAN.md`, `STATUS.md`, `ACCEPTANCE_TRACE.md` | "
        "`AGENTS.override.md`, `STATUS.profile.md`, `SAFETY_POLICY.profile.md`, `VERIFICATION.profile.md` | "
        "10 base / 14 profiled |",
        "| `full` | `AGENTS.md`, `README.md`, `PRODUCT.md`, `MVP.md`, `PROJECT_BOUNDARY.md`, "
        "`DATA_SCOPE.md`, `APPROVALS.md`, `PHASE_PLAN.md`, `STATUS.md`, `ACCEPTANCE_TRACE.md`, "
        "`SOURCE_INDEX.md` | `AGENTS.override.md`, `README.profile.md`, `STATUS.profile.md`, "
        "`SAFETY_POLICY.profile.md`, `VERIFICATION.profile.md` | 11 base / 16 profiled |",
    ]
    for row in expected_rows:
        assert row in text
    assert "all currently rendered base\ntemplates and all selected profile templates" in text


def test_render_tier_contract_defines_selection_precedence_and_preview_consistency() -> None:
    text = tier_contract_text()

    for required_phrase in [
        "render:\n  tier: minimal",
        "An omitted tier must be\ntreated as `full`",
        "`--tier` CLI option",
        "must override `render.tier`",
        "Unknown values fail closed",
        "before output planning, preview generation, or\nfile writing",
        "`--dry-run`",
        "`--provenance-preview`",
        "`--diff-preview`",
        "same resolved tier",
        "same\nplanned file set",
    ]:
        assert required_phrase in text


def test_render_tier_contract_requires_tier_specific_reference_closure() -> None:
    text = tier_contract_text()
    read_order = text.split("## Read Order And Reference Closure", 1)[1].split("## Readiness Targets", 1)[0]

    expected_order = [
        "1. `AGENTS.md`",
        "2. `AGENTS.override.md`, when a profile is selected",
        "3. `README.md`",
        "4. `README.profile.md`, when a full-tier profile is selected",
        "5. `PRODUCT.md`",
        "6. `MVP.md`",
        "7. `PROJECT_BOUNDARY.md`",
        "8. `DATA_SCOPE.md`, when included",
        "9. `APPROVALS.md`, when included",
        "10. `PHASE_PLAN.md`, when included",
        "11. `STATUS.md`, when included",
        "12. `STATUS.profile.md`, when included",
        "13. `ACCEPTANCE_TRACE.md`, when included",
        "14. `SOURCE_INDEX.md`, when included",
        "15. `SAFETY_POLICY.profile.md`, when a profile is selected",
        "16. `VERIFICATION.profile.md`, when a profile is selected",
    ]
    positions = [read_order.index(entry) for entry in expected_order]
    assert positions == sorted(positions)
    for required_phrase in [
        "generates tier-specific Read Order content",
        "must list only files emitted",
        "numbering must be contiguous",
        "`AGENTS.override.md` follows `AGENTS.md`",
        "`README.profile.md` follows\n`README.md`",
        "`STATUS.profile.md` follows `STATUS.md`",
        "base-only render\nmust contain no profile-file references",
        "Reference closure is mandatory",
    ]:
        assert required_phrase in read_order


def test_render_tier_contract_records_scenarios_and_readiness_thresholds() -> None:
    text = tier_contract_text()

    for archetype in [
        "`minimal_meta_tool`",
        "`document_workflow`",
        "`verified_protocol_tool`",
        "`legacy_industrial_review`",
    ]:
        assert archetype in text
    for required_phrase in [
        "read-only, anonymized local archetypes",
        "No repository identifier, absolute path, raw project content, or private value",
        "readiness scanner remains advisory",
        "filename-based\ndimension may under-credit",
        "broken Read\nOrder references as a hard failure",
        "Reference closure applies to every base-only and profiled fixture",
        "thresholds below apply to a selected-profile fixture",
        "at least `LIMITED_AI_ASSISTED_WORK_ALLOWED`",
        "scanner verdict is `READY_FOR_AI_ASSISTED_WORK`",
    ]:
        assert required_phrase in text


def test_render_tier_contract_records_external_precedent_without_dependencies() -> None:
    text = tier_contract_text()

    for required_phrase in [
        "https://copier.readthedocs.io/en/stable/updating/",
        "https://cookiecutter.readthedocs.io/en/stable/advanced/replay.html",
        "https://cookiecutter.readthedocs.io/en/stable/advanced/nested_config_files.html",
        "https://github.com/dotnet/templating/wiki/Inside-the-Template-Engine",
        "remain compare-first",
        "exact tier-selected\n  file set before any write",
        "do not approve a Copier, Cookiecutter, or .NET dependency",
        "must not add hooks, post-actions, network fetches, package installation",
    ]:
        assert required_phrase in text


def test_render_tier_contract_preserves_safety_and_implementation_boundaries() -> None:
    text = tier_contract_text()

    for required_phrase in [
        "no automatic target overwrite",
        "no raw target content in preview output",
        "no local absolute paths",
        "no change to examples unless explicitly approved",
        "Implementation Acceptance Gate",
        "must not silently regenerate curated examples",
        "separate contract and approval boundary",
    ]:
        assert required_phrase in text


def test_render_templates_writes_base_and_profile(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo, "python_cli")
    config = tmp_path / "template.config.yml"
    write_config(config, profile="python_cli")
    target = tmp_path / "target"

    render_templates(config_path=config, target=target, repo_root=repo, dry_run=False)

    assert (target / "README.md").is_file()
    assert (target / "README.profile.md").read_text(encoding="utf-8") == (
        "# README.profile.md for python_cli\n"
    )


def test_render_refuses_existing_file_without_force_and_leaves_no_temp(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"
    write(target / "AGENTS.md", "preserve\n")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        render_templates(
            config_path=config,
            target=target,
            repo_root=repo,
            dry_run=False,
        )

    assert (target / "AGENTS.md").read_text(encoding="utf-8") == "preserve\n"
    assert not list(target.glob(".*.codex-*.tmp"))


def test_render_late_collision_preflight_leaves_all_outputs_unwritten(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"
    write(target / "README.md", "preserve\n")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        render_templates(
            config_path=config,
            target=target,
            repo_root=repo,
            dry_run=False,
        )

    assert (target / "README.md").read_text(encoding="utf-8") == "preserve\n"
    assert not (target / "AGENTS.md").exists()
    assert not (target / "MVP.md").exists()
    assert not list(target.glob(".*.codex-*.tmp"))


def test_render_force_atomically_replaces_regular_single_link_file(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"
    write(target / "AGENTS.md", "old\n")

    render_templates(
        config_path=config,
        target=target,
        repo_root=repo,
        dry_run=False,
        force=True,
    )

    rendered = target / "AGENTS.md"
    assert rendered.read_text(encoding="utf-8").startswith("# demo\n")
    assert rendered.stat().st_nlink == 1
    assert not list(target.glob(".*.codex-*.tmp"))


def test_render_new_file_uses_normal_creation_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    destination = target / "README.md"
    observed_modes: list[int] = []
    original_open = renderer.os.open

    def observe_open(path, flags, mode=0o777):
        if str(path).endswith(".tmp"):
            observed_modes.append(mode)
        return original_open(path, flags, mode)

    monkeypatch.setattr(renderer.os, "open", observe_open)
    renderer._write_destination_text(
        destination,
        "rendered\n",
        target=target,
        force=False,
    )

    assert observed_modes == [0o666]
    assert destination.read_text(encoding="utf-8") == "rendered\n"


def test_render_rolls_back_new_destination_on_link_validation_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    destination = target / "README.md"
    original_is_symlink = Path.is_symlink
    injected = False

    def report_one_unsafe_link(path: Path) -> bool:
        nonlocal injected
        if path == destination and path.exists() and not injected:
            injected = True
            return True
        return original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", report_one_unsafe_link)
    with pytest.raises(ValueError, match="identity drift"):
        renderer._write_destination_text(
            destination,
            "rendered\n",
            target=target,
            force=False,
        )

    assert injected is True
    assert not destination.exists()
    assert not list(target.glob(".*.codex-*.tmp"))


def test_render_preserves_noncollision_publish_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    destination = target / "README.md"

    def blocked_link(*_args, **_kwargs):
        raise PermissionError("synthetic hard-link denial")

    monkeypatch.setattr(renderer.os, "link", blocked_link)
    with pytest.raises(ValueError, match="unable to publish"):
        renderer._write_destination_text(
            destination,
            "rendered\n",
            target=target,
            force=False,
        )

    assert not destination.exists()
    assert not list(target.glob(".*.codex-*.tmp"))


def test_render_new_destination_collision_preserves_raced_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    destination = target / "README.md"
    original_link = renderer.os.link

    def collide(source, target_path, **kwargs):
        Path(target_path).write_text("raced\n", encoding="utf-8")
        return original_link(source, target_path, **kwargs)

    monkeypatch.setattr(renderer.os, "link", collide)
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        renderer._write_destination_text(
            destination,
            "rendered\n",
            target=target,
            force=False,
        )

    assert destination.read_text(encoding="utf-8") == "raced\n"
    assert not list(target.glob(".*.codex-*.tmp"))


def test_render_force_has_no_fallible_post_replace_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    destination = target / "README.md"
    destination.write_text("old\n", encoding="utf-8")
    replaced = False
    original_replace = renderer.os.replace
    original_lstat_safe = renderer._lstat_safe
    original_unlink_matching = renderer._unlink_matching_regular_file

    def observe_replace(source, target_path):
        nonlocal replaced
        original_replace(source, target_path)
        replaced = True

    def reject_postcheck(path: Path, *, allow_directory: bool):
        if replaced and path == destination:
            pytest.fail("destination must not be rechecked after replace")
        return original_lstat_safe(path, allow_directory=allow_directory)

    def reject_post_replace_cleanup(
        path: Path,
        identity: tuple[int, int, int],
    ) -> bool:
        if replaced:
            pytest.fail("temporary path must not be checked after replace")
        return original_unlink_matching(path, identity)

    monkeypatch.setattr(renderer.os, "replace", observe_replace)
    monkeypatch.setattr(renderer, "_lstat_safe", reject_postcheck)
    monkeypatch.setattr(
        renderer,
        "_unlink_matching_regular_file",
        reject_post_replace_cleanup,
    )
    renderer._write_destination_text(
        destination,
        "rendered\n",
        target=target,
        force=True,
    )

    assert replaced is True
    assert destination.read_text(encoding="utf-8") == "rendered\n"


@pytest.mark.skipif(os.name == "nt", reason="POSIX mode regression")
def test_render_force_preserves_mode_under_restrictive_umask(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    destination = target / "README.md"
    destination.write_text("old\n", encoding="utf-8")
    destination.chmod(0o664)
    original_umask = os.umask(0o077)
    try:
        renderer._write_destination_text(
            destination,
            "rendered\n",
            target=target,
            force=True,
        )
    finally:
        os.umask(original_umask)

    assert stat.S_IMODE(destination.stat().st_mode) == 0o664


def test_render_write_failure_cleans_opened_temporary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    destination = target / "README.md"

    def fail_write(*_args, **_kwargs):
        raise OSError("synthetic write failure")

    monkeypatch.setattr(renderer.os, "write", fail_write)
    with pytest.raises(OSError, match="synthetic write failure"):
        renderer._write_destination_text(
            destination,
            "rendered\n",
            target=target,
            force=False,
        )

    assert not destination.exists()
    assert not list(target.glob(".*.codex-*.tmp"))


def test_render_cleanup_failure_is_explicit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    destination = target / "README.md"
    original_unlink = renderer._unlink_matching_regular_file
    cleanup_attempts: list[tuple[Path, tuple[int, int, int]]] = []

    def fail_write(*_args, **_kwargs):
        raise OSError("synthetic write failure")

    def refuse_cleanup(
        path: Path,
        identity: tuple[int, int, int],
    ) -> bool:
        cleanup_attempts.append((path, identity))
        return False

    monkeypatch.setattr(renderer.os, "write", fail_write)
    monkeypatch.setattr(
        renderer,
        "_unlink_matching_regular_file",
        refuse_cleanup,
    )
    try:
        with pytest.raises(
            ValueError,
            match="render destination cleanup failed",
        ):
            renderer._write_destination_text(
                destination,
                "rendered\n",
                target=target,
                force=False,
            )
    finally:
        for path, identity in cleanup_attempts:
            original_unlink(path, identity)

    assert cleanup_attempts
    assert not destination.exists()
    assert not list(target.glob(".*.codex-*.tmp"))


@pytest.mark.parametrize("force", [False, True])
def test_render_rejects_output_symlink_and_preserves_outside_file(
    tmp_path: Path,
    force: bool,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    destination = target / "README.md"
    try:
        destination.symlink_to(outside)
    except OSError:
        pytest.skip("file symlink creation is unavailable")

    with pytest.raises(ValueError, match="unsafe render destination link"):
        renderer._write_destination_text(
            destination,
            "rendered\n",
            target=target,
            force=force,
        )

    assert outside.read_text(encoding="utf-8") == "outside\n"


@pytest.mark.parametrize("force", [False, True])
def test_render_rejects_dangling_output_symlink(
    tmp_path: Path,
    force: bool,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    outside = tmp_path / "missing-outside.md"
    destination = target / "README.md"
    try:
        destination.symlink_to(outside)
    except OSError:
        pytest.skip("file symlink creation is unavailable")

    with pytest.raises(ValueError, match="unsafe render destination link"):
        renderer._write_destination_text(
            destination,
            "rendered\n",
            target=target,
            force=force,
        )

    assert not outside.exists()


@pytest.mark.parametrize("diff_preview", [False, True])
def test_render_rejects_symlinked_target_parent_for_write_and_preview(
    tmp_path: Path,
    diff_preview: bool,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    real_target = tmp_path / "real-target"
    real_target.mkdir()
    target = tmp_path / "linked-target"
    try:
        target.symlink_to(real_target, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink creation is unavailable")

    with pytest.raises(ValueError, match="unsafe render destination link"):
        render_templates(
            config_path=config,
            target=target,
            repo_root=repo,
            dry_run=diff_preview,
            diff_preview=diff_preview,
        )

    assert not (real_target / "AGENTS.md").exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows junction regression")
def test_render_rejects_junction_target_parent(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    real_target = tmp_path / "real-target"
    real_target.mkdir()
    target = tmp_path / "junction-target"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(target), str(real_target)],
        check=False,
        capture_output=True,
    )
    if created.returncode != 0:
        pytest.skip("junction creation is unavailable")
    try:
        with pytest.raises(ValueError, match="unsafe render destination link"):
            render_templates(
                config_path=config,
                target=target,
                repo_root=repo,
                dry_run=True,
                diff_preview=True,
            )
    finally:
        target.rmdir()

    assert not (real_target / "AGENTS.md").exists()


@pytest.mark.parametrize("dry_run,diff_preview", [(False, False), (True, True)])
def test_render_rejects_hard_link_destination_for_write_and_preview(
    tmp_path: Path,
    dry_run: bool,
    diff_preview: bool,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"
    target.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    os.link(outside, target / "README.md")

    with pytest.raises(ValueError, match="unsafe render destination file"):
        render_templates(
            config_path=config,
            target=target,
            repo_root=repo,
            dry_run=dry_run,
            diff_preview=diff_preview,
            force=True,
        )

    assert outside.read_text(encoding="utf-8") == "outside\n"
    assert not (target / "AGENTS.md").exists()


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
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config)
    target = repo / "examples" / "demo"

    rendered = render_templates(config_path=config, target=target, repo_root=repo, dry_run=True)

    assert target / "README.md" in rendered
    assert len(rendered) == 11
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


@pytest.mark.parametrize("tier", VALID_RENDER_TIERS)
@pytest.mark.parametrize("profile", [None, *PROFILES])
def test_rendered_tier_file_matrix(tmp_path: Path, tier: str, profile: str | None) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config = tmp_path / "template.config.yml"
    write_config(config, tier=tier, profile=profile)
    target = tmp_path / "target"

    rendered = render_templates(config_path=config, target=target, repo_root=repo_root, dry_run=True)

    assert {path.name for path in rendered} == expected_output_names(tier, profile)
    assert target.exists() is False


@pytest.mark.parametrize("tier", VALID_RENDER_TIERS)
@pytest.mark.parametrize("profile", [None, *PROFILES])
def test_rendered_tier_read_order_closes_over_outputs(
    tmp_path: Path,
    tier: str,
    profile: str | None,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config = tmp_path / "template.config.yml"
    write_config(config, tier=tier, profile=profile)
    target = tmp_path / "target"

    render_templates(config_path=config, target=target, repo_root=repo_root, dry_run=False)

    output_names = expected_output_names(tier, profile)
    expected_order = [name for name in CANONICAL_READ_ORDER if name in output_names]
    orientation_files = ["AGENTS.md", "README.md"]
    if profile is not None:
        orientation_files.append("AGENTS.override.md")

    for name in orientation_files:
        text = (target / name).read_text(encoding="utf-8")
        assert read_order_entries(text) == expected_order
        assert "{{ render.read_order }}" not in text

    if profile is None:
        assert all(".profile.md" not in name and name != "AGENTS.override.md" for name in expected_order)


@pytest.mark.parametrize("tier", VALID_RENDER_TIERS)
@pytest.mark.parametrize("profile", PROFILES)
def test_profiled_tier_meets_readiness_target(
    tmp_path: Path,
    tier: str,
    profile: str,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config = tmp_path / "template.config.yml"
    write_config(config, tier=tier, profile=profile)
    target = tmp_path / "target"
    render_templates(config_path=config, target=target, repo_root=repo_root, dry_run=False)

    result = scanner.scan_target(target)

    if tier == "minimal":
        assert result.result in {
            "LIMITED_AI_ASSISTED_WORK_ALLOWED",
            "READY_FOR_AI_ASSISTED_WORK",
        }
    else:
        assert result.result == "READY_FOR_AI_ASSISTED_WORK"


@pytest.mark.parametrize("tier", VALID_RENDER_TIERS)
def test_render_modes_share_tier_plan(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    tier: str,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config = tmp_path / "template.config.yml"
    write_config(config, tier=tier, profile="python_cli")
    write_target = tmp_path / "write-target"
    preview_target = tmp_path / "preview-target"

    written = render_templates(
        config_path=config,
        target=write_target,
        repo_root=repo_root,
        dry_run=False,
    )
    previewed = render_templates(
        config_path=config,
        target=preview_target,
        repo_root=repo_root,
        dry_run=True,
        provenance_preview=True,
        diff_preview=True,
    )

    output = capsys.readouterr().out
    provenance_line = next(
        line for line in output.splitlines() if line.startswith("DRY-RUN provenance-preview ")
    )
    diff_line = next(
        line for line in output.splitlines() if line.startswith("DRY-RUN diff-preview ")
    )
    provenance = json.loads(provenance_line.removeprefix("DRY-RUN provenance-preview "))
    diff = json.loads(diff_line.removeprefix("DRY-RUN diff-preview "))
    expected = expected_output_names(tier, "python_cli")

    assert {path.name for path in written} == expected
    assert {path.name for path in previewed} == expected
    assert provenance["schema_version"] == "render_provenance_preview.v0"
    assert provenance["rendered_file_count"] == len(expected)
    assert "render_tier" not in provenance
    assert diff["schema_version"] == "render_diff_preview.v0"
    assert diff["rendered_file_count"] == len(expected)
    assert diff["missing_paths"] == sorted(expected)
    assert preview_target.exists() is False


def test_profile_and_tier_overrides_apply_together(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo, "python_cli")
    config = tmp_path / "template.config.yml"
    write_config(config, tier="standard")
    target = tmp_path / "target"

    result = main(
        [
            "--repo-root",
            str(repo),
            "--config",
            str(config),
            "--target",
            str(target),
            "--profile",
            "python_cli",
            "--tier",
            "minimal",
            "--dry-run",
        ]
    )

    render_lines = [
        line for line in capsys.readouterr().out.splitlines() if line.startswith("DRY-RUN render ")
    ]
    assert result == 0
    assert len(render_lines) == 8
    assert target.exists() is False


@pytest.mark.parametrize(
    "profile",
    ["../python_cli", "profiles/python_cli", "profiles\\python_cli", "C:\\python_cli"],
)
def test_cli_rejects_path_like_profile_override_before_writing(
    tmp_path: Path,
    profile: str,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo, "python_cli")
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"

    with pytest.raises(ValueError, match="profile name must match"):
        main(
            [
                "--repo-root",
                str(repo),
                "--config",
                str(config),
                "--target",
                str(target),
                "--profile",
                profile,
                "--apply",
            ]
        )

    assert target.exists() is False


def test_cli_rejects_unknown_tier_before_writing(tmp_path: Path) -> None:
    target = tmp_path / "target"

    with pytest.raises(SystemExit) as exc_info:
        main(["--target", str(target), "--tier", "unknown", "--dry-run"])

    assert exc_info.value.code == 2
    assert target.exists() is False


def test_missing_selected_template_fails_before_writing(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    (repo / "templates" / "base" / "MVP.md.template").unlink()
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"

    with pytest.raises(FileNotFoundError, match="MVP.md.template"):
        render_templates(config_path=config, target=target, repo_root=repo, dry_run=False)

    assert target.exists() is False


def test_render_rejects_symlinked_template_source_before_writing(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    outside = tmp_path / "outside.template"
    write(outside, "outside\n")
    source = repo / "templates" / "base" / "README.md.template"
    source.unlink()
    try:
        source.symlink_to(outside)
    except OSError:
        pytest.skip("file symlink creation is unavailable")
    target = tmp_path / "target"

    with pytest.raises(ValueError, match="unsafe render source link"):
        render_templates(config_path=config, target=target, repo_root=repo, dry_run=False)

    assert target.exists() is False


def test_render_rejects_hard_link_source_before_reading_any_template(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    outside = tmp_path / "outside.template"
    write(outside, "outside\n")
    source = repo / "templates" / "base" / "README.md.template"
    source.unlink()
    os.link(outside, source)
    reads: list[Path] = []
    original = renderer._safe_source_bytes

    def observe(path: Path, expected: os.stat_result) -> bytes:
        reads.append(path)
        return original(path, expected)

    monkeypatch.setattr(renderer, "_safe_source_bytes", observe)
    target = tmp_path / "target"

    with pytest.raises(ValueError, match="unsafe render source file"):
        render_templates(config_path=config, target=target, repo_root=repo, dry_run=False)

    assert reads == []
    assert target.exists() is False


def test_render_rejects_same_inode_same_size_source_mutation_before_read(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.template"
    source.write_bytes(b"before\n")
    expected = source.lstat()
    source.write_bytes(b"after!\n")
    os.utime(
        source,
        ns=(expected.st_atime_ns, expected.st_mtime_ns + 1_000_000),
    )
    observed = source.lstat()

    assert observed.st_dev == expected.st_dev
    assert observed.st_ino == expected.st_ino
    assert observed.st_size == expected.st_size
    with pytest.raises(ValueError, match="source identity drift"):
        renderer._safe_source_text(source, expected)


def test_render_rejects_metadata_drift_during_descriptor_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.template"
    source.write_bytes(b"stable\n")
    expected = source.lstat()
    original_fstat = renderer.os.fstat
    calls = 0

    def drifting_fstat(descriptor: int):
        nonlocal calls
        calls += 1
        observed = original_fstat(descriptor)
        if calls == 1:
            return observed
        return SimpleNamespace(
            st_dev=observed.st_dev,
            st_ino=observed.st_ino,
            st_file_attributes=getattr(observed, "st_file_attributes", 0),
            st_size=observed.st_size,
            st_mtime_ns=observed.st_mtime_ns + 1,
            st_ctime_ns=observed.st_ctime_ns,
            st_mode=observed.st_mode,
            st_nlink=observed.st_nlink,
        )

    monkeypatch.setattr(renderer.os, "fstat", drifting_fstat)

    with pytest.raises(ValueError, match="source identity drift"):
        renderer._safe_source_text(source, expected)

    assert calls == 2


def test_render_source_capture_preserves_universal_newline_behavior(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.template"
    source.write_bytes(b"first\r\nsecond\rthird\n")

    captured = renderer._safe_source_text(source, source.lstat())

    assert captured == "first\nsecond\nthird\n"


def test_render_rejects_profile_directory_symlink_outside_repo(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo, "python_cli")
    outside = tmp_path / "outside-profile"
    shutil.copytree(repo / "profiles" / "python_cli", outside)
    shutil.rmtree(repo / "profiles" / "python_cli")
    try:
        (repo / "profiles" / "python_cli").symlink_to(
            outside,
            target_is_directory=True,
        )
    except OSError:
        pytest.skip("directory symlink creation is unavailable")
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal", profile="python_cli")
    target = tmp_path / "target"

    with pytest.raises(ValueError, match="unsafe render source link"):
        render_templates(config_path=config, target=target, repo_root=repo, dry_run=False)

    assert target.exists() is False


def test_render_rejects_base_source_directory_symlink_outside_repo(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    outside = tmp_path / "outside-base"
    shutil.copytree(repo / "templates" / "base", outside)
    shutil.rmtree(repo / "templates" / "base")
    try:
        (repo / "templates" / "base").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlink creation is unavailable")
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"

    with pytest.raises(ValueError, match="unsafe render source link"):
        render_templates(config_path=config, target=target, repo_root=repo, dry_run=False)

    assert target.exists() is False


@pytest.mark.skipif(os.name != "nt", reason="Windows junction regression")
def test_render_rejects_profile_source_junction(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo, "python_cli")
    outside = tmp_path / "outside-profile"
    shutil.copytree(repo / "profiles" / "python_cli", outside)
    shutil.rmtree(repo / "profiles" / "python_cli")
    profile_dir = repo / "profiles" / "python_cli"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(profile_dir), str(outside)],
        check=False,
        capture_output=True,
    )
    if created.returncode != 0:
        pytest.skip("junction creation is unavailable")
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal", profile="python_cli")
    target = tmp_path / "target"
    try:
        with pytest.raises(ValueError, match="unsafe render source link"):
            render_templates(
                config_path=config,
                target=target,
                repo_root=repo,
                dry_run=False,
            )
    finally:
        profile_dir.rmdir()

    assert target.exists() is False


def test_unselected_extra_template_is_not_rendered(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo)
    write(repo / "templates" / "base" / "EXTRA.md.template", "# extra\n")
    config = tmp_path / "template.config.yml"
    write_config(config, tier="minimal")
    target = tmp_path / "target"

    rendered = render_templates(config_path=config, target=target, repo_root=repo, dry_run=True)

    assert {path.name for path in rendered} == set(EXPECTED_BASE_OUTPUTS["minimal"])
    assert target / "EXTRA.md" not in rendered


@pytest.mark.parametrize("profile", PROFILES)
def test_profile_render_captures_each_source_once_and_preserves_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    profile: str,
) -> None:
    repo = tmp_path / "repo"
    populate_template_repo(repo, profile)
    config_path = tmp_path / "template.config.yml"
    write_config(config_path, tier="full", profile=profile)
    config = load_config(config_path)
    target = tmp_path / "target"
    source_opens: dict[Path, int] = {}
    original_open = renderer.os.open

    def observe_open(path, flags, mode=0o777):
        candidate = Path(path)
        if candidate.suffix == ".template" and repo in candidate.parents:
            source_opens[candidate] = source_opens.get(candidate, 0) + 1
        return original_open(path, flags, mode)

    monkeypatch.setattr(renderer.os, "open", observe_open)

    rendered = render_templates(
        config_path=config_path,
        target=target,
        repo_root=repo,
        dry_run=False,
    )

    assert {path.name for path in rendered} == expected_output_names("full", profile)
    expected_sources = {
        repo / "templates" / "base" / f"{name}.template"
        for name in EXPECTED_BASE_OUTPUTS["full"]
    } | {
        repo / "profiles" / profile / f"{name}.template"
        for name in EXPECTED_PROFILE_OUTPUTS["full"]
    }
    assert set(source_opens) == expected_sources
    assert set(source_opens.values()) == {1}
    for destination in rendered:
        source_root = (
            repo / "profiles" / profile
            if destination.name in EXPECTED_PROFILE_OUTPUTS["full"]
            else repo / "templates" / "base"
        )
        source = source_root / f"{destination.name}.template"
        expected_text = renderer.render_text(
            source.read_text(encoding="utf-8"), config
        )
        assert destination.read_text(encoding="utf-8") == expected_text


@pytest.mark.parametrize(
    "example_name",
    ["python_cli_minimal", "csharp_desktop_minimal", "plc_tool_minimal"],
)
def test_existing_example_config_defaults_to_full(tmp_path: Path, example_name: str) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config = repo_root / "examples" / example_name / "template.config.yml"

    rendered = render_templates(
        config_path=config,
        target=tmp_path / example_name,
        repo_root=repo_root,
        dry_run=True,
    )

    assert len(rendered) == 16
