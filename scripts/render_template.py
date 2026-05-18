"""Render codex-dev-harness markdown templates into a target folder.

P2 implementation constraints:
- No external network calls.
- No implicit live target writes: callers must pass --target, and --dry-run is supported.
- No project code generation beyond copying markdown templates.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TemplateConfig:
    project_name: str
    project_status: str
    profile: str | None


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
        if value:
            values[dotted] = value
        else:
            stack.append((indent, key))

    return values


def load_config(path: Path) -> TemplateConfig:
    values = parse_scalar_config(path)
    project_name = values.get("project.name", "").strip()
    project_status = values.get("project.status", "").strip()
    profile = values.get("profile.name", "").strip() or None

    if not project_name:
        raise ValueError("template config requires project.name")
    if project_status != "seed":
        raise ValueError("template config requires project.status: seed")

    return TemplateConfig(project_name=project_name, project_status=project_status, profile=profile)


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
    }
    for marker, value in replacements.items():
        text = text.replace(marker, value)
    return text


def iter_templates(base_dir: Path, profile_dir: Path | None) -> Iterable[tuple[Path, Path]]:
    for path in sorted(base_dir.rglob("*.template")):
        yield path, base_dir
    if profile_dir and profile_dir.exists():
        for path in sorted(profile_dir.rglob("*.template")):
            yield path, profile_dir


def validate_target(target: Path, repo_root: Path) -> None:
    resolved_target = target.resolve()
    resolved_repo = repo_root.resolve()
    if resolved_target == resolved_repo or resolved_repo in resolved_target.parents:
        raise ValueError("refusing to render into the template repository itself")


def render_templates(
    *,
    config_path: Path,
    target: Path,
    repo_root: Path = REPO_ROOT,
    profile_override: str | None = None,
    dry_run: bool = True,
    force: bool = False,
) -> list[Path]:
    config = load_config(config_path)
    if profile_override:
        config = TemplateConfig(config.project_name, config.project_status, profile_override)

    validate_target(target, repo_root)

    base_dir = repo_root / "templates" / "base"
    profile_dir = repo_root / "profiles" / config.profile if config.profile else None
    if not base_dir.exists():
        raise FileNotFoundError(f"missing base template directory: {base_dir}")
    if config.profile and (profile_dir is None or not profile_dir.exists()):
        raise FileNotFoundError(f"missing profile template directory: {profile_dir}")

    rendered_paths: list[Path] = []
    for source, source_root in iter_templates(base_dir, profile_dir):
        destination = template_destination(source, source_root, target)
        rendered_paths.append(destination)
        if dry_run:
            print(f"DRY-RUN render {source.relative_to(repo_root)} -> {destination}")
            continue
        if destination.exists() and not force:
            raise FileExistsError(f"refusing to overwrite existing file: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_text(source.read_text(encoding="utf-8"), config), encoding="utf-8")
        print(f"rendered {source.relative_to(repo_root)} -> {destination}")

    return rendered_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render markdown templates into a target folder.")
    parser.add_argument("--config", default="template.config.yml", help="Path to template.config.yml")
    parser.add_argument("--target", required=True, help="Target folder for rendered files")
    parser.add_argument("--profile", default=None, help="Override profile.name from config")
    parser.add_argument("--dry-run", action="store_true", help="Preview files without writing")
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
        dry_run=args.dry_run,
        force=args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
