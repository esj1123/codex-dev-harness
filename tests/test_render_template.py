import json
from pathlib import Path

import pytest

from scripts import ai_readiness_scanner as scanner
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
