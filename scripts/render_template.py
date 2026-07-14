"""Render codex-dev-harness markdown templates into a target folder.

P2 implementation constraints:
- No external network calls.
- No implicit live target writes: callers must pass --target, and --dry-run is supported.
- No project code generation beyond copying markdown templates.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_PREVIEW_SCHEMA_VERSION = "render_provenance_preview.v0"
DIFF_PREVIEW_SCHEMA_VERSION = "render_diff_preview.v0"
MAX_DIFF_PREVIEW_PATHS = 50
VALID_RENDER_TIERS = ("minimal", "standard", "full")

BASE_OUTPUTS_BY_TIER = {
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

PROFILE_OUTPUTS_BY_TIER = {
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

CANONICAL_READ_ORDER = (
    "AGENTS.md",
    "AGENTS.override.md",
    "README.md",
    "README.profile.md",
    "PRODUCT.md",
    "MVP.md",
    "PROJECT_BOUNDARY.md",
    "DATA_SCOPE.md",
    "APPROVALS.md",
    "PHASE_PLAN.md",
    "STATUS.md",
    "STATUS.profile.md",
    "ACCEPTANCE_TRACE.md",
    "SOURCE_INDEX.md",
    "SAFETY_POLICY.profile.md",
    "VERIFICATION.profile.md",
)


@dataclass(frozen=True)
class TemplateConfig:
    project_name: str
    project_status: str
    profile: str | None
    tier: str = "full"


def parse_scalar_config(path: Path) -> dict[str, str]:
    """Parse a small, scalar-only YAML subset used by template.config.yml."""
    values: dict[str, str] = {}
    stack: list[tuple[int, str]] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if ":" not in stripped or stripped.startswith("-"):
            continue

        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        value = raw_value.strip().strip('"').strip("'")

        while stack and stack[-1][0] >= indent:
            stack.pop()

        dotted = ".".join([part for _, part in stack] + [key])
        values[dotted] = value
        if not value:
            stack.append((indent, key))

    return values


def load_config(path: Path) -> TemplateConfig:
    values = parse_scalar_config(path)
    project_name = values.get("project.name", "").strip()
    project_status = values.get("project.status", "").strip()
    profile = values.get("profile.name", "").strip() or None
    tier = values.get("render.tier", "full").strip()

    if not project_name:
        raise ValueError("template config requires project.name")
    if project_status != "seed":
        raise ValueError("template config requires project.status: seed")
    validate_render_tier(tier)

    return TemplateConfig(
        project_name=project_name,
        project_status=project_status,
        profile=profile,
        tier=tier,
    )


def validate_render_tier(tier: str) -> None:
    if tier not in VALID_RENDER_TIERS:
        allowed = ", ".join(VALID_RENDER_TIERS)
        raise ValueError(f"render tier must be one of: {allowed}")


def selected_output_names(config: TemplateConfig) -> tuple[str, ...]:
    validate_render_tier(config.tier)
    outputs = list(BASE_OUTPUTS_BY_TIER[config.tier])
    if config.profile:
        outputs.extend(PROFILE_OUTPUTS_BY_TIER[config.tier])
    return tuple(outputs)


def render_read_order(config: TemplateConfig) -> str:
    selected = set(selected_output_names(config))
    ordered = [name for name in CANONICAL_READ_ORDER if name in selected]
    return "\n".join(f"{index}. {name}" for index, name in enumerate(ordered, start=1))


def template_destination(template_path: Path, source_root: Path, target_root: Path) -> Path:
    relative = template_path.relative_to(source_root)
    name = relative.name
    if name.endswith(".template"):
        name = name[: -len(".template")]
    return target_root / relative.parent / name


def render_text(text: str, config: TemplateConfig) -> str:
    replacements = {
        "{{ project.name }}": config.project_name,
        "{{ project.status }}": config.project_status,
        "{{ profile.name }}": config.profile or "",
        "{{ render.read_order }}": render_read_order(config),
    }
    for marker, value in replacements.items():
        text = text.replace(marker, value)
    return text


def iter_templates(
    base_dir: Path,
    profile_dir: Path | None,
    tier: str = "full",
) -> Iterable[tuple[Path, Path]]:
    validate_render_tier(tier)
    planned = [
        (base_dir / f"{name}.template", base_dir)
        for name in BASE_OUTPUTS_BY_TIER[tier]
    ]
    if profile_dir is not None:
        planned.extend(
            (profile_dir / f"{name}.template", profile_dir)
            for name in PROFILE_OUTPUTS_BY_TIER[tier]
        )

    missing = [path.name for path, _ in planned if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing selected tier template(s): {', '.join(sorted(missing))}")

    yield from sorted(planned, key=lambda item: item[0].name)


def validate_target(target: Path, repo_root: Path) -> None:
    resolved_target = target.resolve()
    resolved_repo = repo_root.resolve()
    if resolved_target == resolved_repo:
        raise ValueError("refusing to render into the template repository itself")
    if resolved_repo in resolved_target.parents:
        examples_root = resolved_repo / "examples"
        if resolved_target.parent != examples_root:
            raise ValueError("refusing to render into the template repository outside examples/<name>")


def safe_repo_relative_or_summary(path: Path, repo_root: Path, external_summary: str) -> str:
    resolved_path = path.resolve()
    resolved_root = repo_root.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix() or "."
    except ValueError:
        return external_summary


def current_git_commit(repo_root: Path) -> str:
    if not (repo_root / ".git").exists():
        return "UNKNOWN"

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"

    commit = result.stdout.strip()
    if result.returncode == 0 and len(commit) == 40 and all(char in "0123456789abcdefABCDEF" for char in commit):
        return commit.lower()
    return "UNKNOWN"


def build_render_provenance_preview(
    *,
    config: TemplateConfig,
    config_path: Path,
    target: Path,
    repo_root: Path,
    rendered_file_count: int,
) -> dict[str, str | int]:
    return {
        "schema_version": PROVENANCE_PREVIEW_SCHEMA_VERSION,
        "mode": "DRY_RUN_PREVIEW",
        "harness_commit": current_git_commit(repo_root),
        "render_profile": config.profile or "base",
        "config_source": safe_repo_relative_or_summary(config_path, repo_root, "external_config"),
        "target_root": safe_repo_relative_or_summary(target, repo_root, "external_target"),
        "rendered_file_count": rendered_file_count,
        "output_policy": "no_provenance_stamp_written",
    }


def print_render_provenance_preview(preview: dict[str, str | int]) -> None:
    payload = json.dumps(preview, sort_keys=True, separators=(",", ":"))
    print(f"DRY-RUN provenance-preview {payload}")


def target_relative_path(path: Path, target: Path) -> str:
    return path.relative_to(target).as_posix()


def build_render_diff_preview(*, expected_rendered: list[tuple[Path, str]], target: Path) -> dict[str, object]:
    missing_paths: list[str] = []
    changed_paths: list[str] = []
    unchanged_count = 0

    for destination, rendered_text in expected_rendered:
        relative = target_relative_path(destination, target)
        if not destination.exists():
            missing_paths.append(relative)
            continue
        if not destination.is_file():
            changed_paths.append(relative)
            continue
        try:
            existing_text = destination.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            changed_paths.append(relative)
            continue
        if existing_text == rendered_text:
            unchanged_count += 1
        else:
            changed_paths.append(relative)

    path_count = len(missing_paths) + len(changed_paths)
    return {
        "schema_version": DIFF_PREVIEW_SCHEMA_VERSION,
        "mode": "DRY_RUN_PREVIEW",
        "rendered_file_count": len(expected_rendered),
        "missing_count": len(missing_paths),
        "changed_count": len(changed_paths),
        "unchanged_count": unchanged_count,
        "missing_paths": missing_paths[:MAX_DIFF_PREVIEW_PATHS],
        "changed_paths": changed_paths[:MAX_DIFF_PREVIEW_PATHS],
        "paths_truncated": path_count > MAX_DIFF_PREVIEW_PATHS,
        "output_policy": "no_files_written",
    }


def print_render_diff_preview(preview: dict[str, object]) -> None:
    payload = json.dumps(preview, sort_keys=True, separators=(",", ":"))
    print(f"DRY-RUN diff-preview {payload}")

def render_templates(
    *,
    config_path: Path,
    target: Path,
    repo_root: Path = REPO_ROOT,
    profile_override: str | None = None,
    tier_override: str | None = None,
    dry_run: bool = True,
    force: bool = False,
    provenance_preview: bool = False,
    diff_preview: bool = False,
) -> list[Path]:
    config = load_config(config_path)
    if profile_override:
        config = replace(config, profile=profile_override)
    if tier_override is not None:
        validate_render_tier(tier_override)
        config = replace(config, tier=tier_override)

    validate_target(target, repo_root)
    if provenance_preview and not dry_run:
        raise ValueError("provenance preview is dry-run only")
    if diff_preview and not dry_run:
        raise ValueError("diff preview is dry-run only")

    base_dir = repo_root / "templates" / "base"
    profile_dir = repo_root / "profiles" / config.profile if config.profile else None
    if not base_dir.exists():
        raise FileNotFoundError(f"missing base template directory: {base_dir}")
    if config.profile and (profile_dir is None or not profile_dir.exists()):
        raise FileNotFoundError(f"missing profile template directory: {profile_dir}")

    rendered_paths: list[Path] = []
    expected_rendered: list[tuple[Path, str]] = []
    for source, source_root in iter_templates(base_dir, profile_dir, config.tier):
        destination = template_destination(source, source_root, target)
        rendered_paths.append(destination)
        rendered_text = ""
        if diff_preview or not dry_run:
            rendered_text = render_text(source.read_text(encoding="utf-8"), config)
        if diff_preview:
            expected_rendered.append((destination, rendered_text))
        if dry_run:
            print(f"DRY-RUN render {source.relative_to(repo_root)} -> {destination}")
            continue
        if destination.exists() and not force:
            raise FileExistsError(f"refusing to overwrite existing file: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered_text, encoding="utf-8")
        print(f"rendered {source.relative_to(repo_root)} -> {destination}")

    if dry_run and diff_preview:
        print_render_diff_preview(
            build_render_diff_preview(expected_rendered=expected_rendered, target=target)
        )

    if dry_run and provenance_preview:
        print_render_provenance_preview(
            build_render_provenance_preview(
                config=config,
                config_path=config_path,
                target=target,
                repo_root=repo_root,
                rendered_file_count=len(rendered_paths),
            )
        )

    return rendered_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render markdown templates into a target folder.")
    parser.add_argument("--config", default="template.config.yml", help="Path to template.config.yml")
    parser.add_argument("--target", required=True, help="Target folder for rendered files")
    parser.add_argument("--profile", default=None, help="Override profile.name from config")
    parser.add_argument(
        "--tier",
        choices=VALID_RENDER_TIERS,
        default=None,
        help="Override render.tier from config",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview files without writing")
    parser.add_argument(
        "--provenance-preview",
        action="store_true",
        help="With --dry-run, print safe render provenance metadata without writing a stamp",
    )
    parser.add_argument(
        "--diff-preview",
        action="store_true",
        help="With --dry-run, print bounded target-relative render diff metadata without writing",
    )
    parser.add_argument("--force", action="store_true", help="Allow overwriting existing files")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Template repo root")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_path = Path(args.config).resolve()
    repo_root = Path(args.repo_root).resolve()
    target = Path(args.target).resolve()
    render_templates(
        config_path=config_path,
        target=target,
        repo_root=repo_root,
        profile_override=args.profile,
        tier_override=args.tier,
        dry_run=args.dry_run,
        force=args.force,
        provenance_preview=args.provenance_preview,
        diff_preview=args.diff_preview,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
