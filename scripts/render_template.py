"""Render codex-dev-harness markdown templates into a target folder.

P2 implementation constraints:
- No external network calls.
- No implicit live target writes: callers must pass --target and --apply.
- No project code generation beyond copying markdown templates.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import stat
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_PREVIEW_SCHEMA_VERSION = "render_provenance_preview.v0"
DIFF_PREVIEW_SCHEMA_VERSION = "render_diff_preview.v0"
MAX_DIFF_PREVIEW_PATHS = 50
VALID_RENDER_TIERS = ("minimal", "standard", "full")
REPARSE_POINT_FLAG = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)

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


@dataclass(frozen=True)
class RenderPlanItem:
    source: Path
    destination: Path
    rendered_text: str


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


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(path))


def _path_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        getattr(metadata, "st_file_attributes", 0),
    )


def _lstat_safe(path: Path, *, allow_directory: bool) -> os.stat_result:
    try:
        metadata = path.lstat()
        is_junction = getattr(path, "is_junction", lambda: False)()
    except OSError as exc:
        raise ValueError(f"unsafe render destination path: {path}") from exc
    if (
        path.is_symlink()
        or is_junction
        or bool(getattr(metadata, "st_file_attributes", 0) & REPARSE_POINT_FLAG)
    ):
        raise ValueError(f"unsafe render destination link: {path}")
    if allow_directory:
        if not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"unsafe render destination parent: {path}")
    elif (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
    ):
        raise ValueError(f"unsafe render destination file: {path}")
    return metadata


def _existing_path_chain(path: Path) -> list[Path]:
    path = _absolute_lexical(path)
    chain = [path, *path.parents]
    return [item for item in reversed(chain) if item.exists() or item.is_symlink()]


def _validate_destination_boundary(
    destination: Path,
    *,
    target: Path,
) -> tuple[Path, Path]:
    lexical_target = _absolute_lexical(target)
    lexical_destination = _absolute_lexical(destination)
    try:
        lexical_destination.relative_to(lexical_target)
    except ValueError as exc:
        raise ValueError("render destination escapes target root") from exc
    for parent in _existing_path_chain(lexical_destination.parent):
        _lstat_safe(parent, allow_directory=True)
    if lexical_destination.exists() or lexical_destination.is_symlink():
        _lstat_safe(lexical_destination, allow_directory=False)
    return lexical_target, lexical_destination


def _ensure_safe_destination_parent(
    destination: Path,
    *,
    target: Path,
) -> os.stat_result:
    lexical_target, lexical_destination = _validate_destination_boundary(
        destination,
        target=target,
    )
    missing: list[Path] = []
    current = lexical_destination.parent
    while not current.exists() and not current.is_symlink():
        missing.append(current)
        if current == current.parent:
            break
        current = current.parent
    for directory in reversed(missing):
        try:
            directory.mkdir()
        except FileExistsError:
            pass
        _lstat_safe(directory, allow_directory=True)
    try:
        lexical_destination.parent.relative_to(lexical_target)
    except ValueError as exc:
        raise ValueError("render destination escapes target root") from exc
    return _lstat_safe(lexical_destination.parent, allow_directory=True)


def _safe_destination_text(path: Path, *, target: Path) -> str:
    _, lexical_path = _validate_destination_boundary(path, target=target)
    before = _lstat_safe(lexical_path, allow_directory=False)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(lexical_path, flags)
    except OSError as exc:
        raise ValueError(f"unsafe render destination file: {lexical_path}") from exc
    try:
        observed = os.fstat(descriptor)
        if (
            _path_identity(observed) != _path_identity(before)
            or not stat.S_ISREG(observed.st_mode)
            or observed.st_nlink != 1
        ):
            raise ValueError(
                f"unsafe render destination identity drift: {lexical_path}"
            )
        with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
            descriptor = -1
            return stream.read()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _unlink_matching_regular_file(
    path: Path,
    expected_identity: tuple[int, int, int],
) -> bool:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return True
    except OSError:
        return False
    if (
        stat.S_ISLNK(metadata.st_mode)
        or not stat.S_ISREG(metadata.st_mode)
        or bool(
            getattr(metadata, "st_file_attributes", 0)
            & REPARSE_POINT_FLAG
        )
        or _path_identity(metadata) != expected_identity
    ):
        return False
    try:
        path.unlink()
    except OSError:
        return False
    return True


def _write_destination_text(
    destination: Path,
    text: str,
    *,
    target: Path,
    force: bool,
) -> None:
    _, lexical_destination = _validate_destination_boundary(
        destination,
        target=target,
    )
    destination_before: os.stat_result | None = None
    if lexical_destination.exists() or lexical_destination.is_symlink():
        destination_before = _lstat_safe(
            lexical_destination,
            allow_directory=False,
        )
        if not force:
            raise FileExistsError(
                f"refusing to overwrite existing file: {lexical_destination}"
            )
    parent_before = _ensure_safe_destination_parent(
        lexical_destination,
        target=target,
    )
    temporary = lexical_destination.parent / (
        f".{lexical_destination.name}.codex-{secrets.token_hex(12)}.tmp"
    )
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_BINARY", 0)
    )
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = -1
    temporary_metadata: os.stat_result | None = None
    linked_destination_identity: tuple[int, int, int] | None = None
    try:
        creation_mode = (
            0o666
            if destination_before is None
            else stat.S_IMODE(destination_before.st_mode)
        )
        descriptor = os.open(temporary, flags, creation_mode)
        temporary_metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(temporary_metadata.st_mode)
            or temporary_metadata.st_nlink != 1
        ):
            raise ValueError(
                f"unsafe render temporary identity: {temporary}"
            )
        if destination_before is not None and hasattr(os, "fchmod"):
            os.fchmod(
                descriptor,
                stat.S_IMODE(destination_before.st_mode),
            )
        encoded = text.encode("utf-8")
        offset = 0
        while offset < len(encoded):
            offset += os.write(descriptor, encoded[offset:])
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        observed_temporary = _lstat_safe(
            temporary,
            allow_directory=False,
        )
        if _path_identity(observed_temporary) != _path_identity(
            temporary_metadata
        ):
            raise ValueError(
                f"unsafe render temporary identity drift: {temporary}"
            )
        parent_after = _lstat_safe(
            lexical_destination.parent,
            allow_directory=True,
        )
        if _path_identity(parent_after) != _path_identity(parent_before):
            raise ValueError(
                f"unsafe render destination parent drift: {lexical_destination.parent}"
            )
        if destination_before is None:
            if lexical_destination.exists() or lexical_destination.is_symlink():
                raise FileExistsError(
                    f"refusing to overwrite existing file: {lexical_destination}"
                )
            try:
                os.link(
                    temporary,
                    lexical_destination,
                    follow_symlinks=False,
                )
                linked_destination_identity = _path_identity(
                    temporary_metadata
                )
            except FileExistsError as exc:
                raise FileExistsError(
                    f"refusing to overwrite existing file: {lexical_destination}"
                ) from exc
            except OSError as exc:
                raise ValueError(
                    f"unable to publish render destination: {lexical_destination}"
                ) from exc
            try:
                linked = lexical_destination.lstat()
                linked_is_junction = getattr(
                    lexical_destination,
                    "is_junction",
                    lambda: False,
                )()
            except OSError as exc:
                raise ValueError(
                    f"unsafe render destination identity drift: {lexical_destination}"
                ) from exc
            if (
                lexical_destination.is_symlink()
                or linked_is_junction
                or bool(
                    getattr(linked, "st_file_attributes", 0)
                    & REPARSE_POINT_FLAG
                )
                or not stat.S_ISREG(linked.st_mode)
                or linked.st_nlink != 2
                or _path_identity(linked) != _path_identity(temporary_metadata)
            ):
                raise ValueError(
                    f"unsafe render destination identity drift: {lexical_destination}"
                )
            if not _unlink_matching_regular_file(
                temporary,
                _path_identity(temporary_metadata),
            ):
                raise ValueError("render destination cleanup failed")
            temporary_metadata = None
            linked_destination_identity = None
        else:
            current = _lstat_safe(
                lexical_destination,
                allow_directory=False,
            )
            if _path_identity(current) != _path_identity(destination_before):
                raise ValueError(
                    f"unsafe render destination identity drift: {lexical_destination}"
                )
            os.replace(temporary, lexical_destination)
            temporary_metadata = None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        cleanup_failed = False
        if linked_destination_identity is not None:
            cleanup_failed = not _unlink_matching_regular_file(
                lexical_destination,
                linked_destination_identity,
            )
        if temporary_metadata is not None:
            cleanup_failed = (
                not _unlink_matching_regular_file(
                    temporary,
                    _path_identity(temporary_metadata),
                )
                or cleanup_failed
            )
        if cleanup_failed:
            raise ValueError("render destination cleanup failed")


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
        _validate_destination_boundary(destination, target=target)
        relative = target_relative_path(destination, target)
        if not destination.exists():
            missing_paths.append(relative)
            continue
        try:
            existing_text = _safe_destination_text(destination, target=target)
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


def _build_render_plan(
    *,
    base_dir: Path,
    profile_dir: Path | None,
    target: Path,
    config: TemplateConfig,
    force: bool,
    dry_run: bool,
) -> list[RenderPlanItem]:
    plan: list[RenderPlanItem] = []
    destinations: set[Path] = set()
    for source, source_root in iter_templates(base_dir, profile_dir, config.tier):
        destination = template_destination(source, source_root, target)
        _, lexical_destination = _validate_destination_boundary(
            destination,
            target=target,
        )
        if lexical_destination in destinations:
            raise ValueError(f"duplicate render destination: {lexical_destination}")
        destinations.add(lexical_destination)
        if (
            not dry_run
            and not force
            and (lexical_destination.exists() or lexical_destination.is_symlink())
        ):
            raise FileExistsError(
                f"refusing to overwrite existing file: {lexical_destination}"
            )
        plan.append(
            RenderPlanItem(
                source=source,
                destination=lexical_destination,
                rendered_text=render_text(source.read_text(encoding="utf-8"), config),
            )
        )
    return plan

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
    target = _absolute_lexical(target)
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

    plan = _build_render_plan(
        base_dir=base_dir,
        profile_dir=profile_dir,
        target=target,
        config=config,
        force=force,
        dry_run=dry_run,
    )
    rendered_paths = [item.destination for item in plan]
    expected_rendered = [
        (item.destination, item.rendered_text) for item in plan
    ]
    for item in plan:
        if dry_run:
            print(
                f"DRY-RUN render {item.source.relative_to(repo_root)} -> "
                f"{item.destination}"
            )
            continue
        _write_destination_text(
            item.destination,
            item.rendered_text,
            target=target,
            force=force,
        )
        print(f"rendered {item.source.relative_to(repo_root)} -> {item.destination}")

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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Explicitly write the fully preflighted render plan",
    )
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Compatibility alias for the default no-write preview",
    )
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

    if args.force and not args.apply:
        parser.error("--force requires --apply")
    if args.apply and args.provenance_preview:
        parser.error("--provenance-preview cannot be used with --apply")
    if args.apply and args.diff_preview:
        parser.error("--diff-preview cannot be used with --apply")

    config_path = Path(args.config).resolve()
    repo_root = Path(args.repo_root).resolve()
    target = _absolute_lexical(Path(args.target))
    render_templates(
        config_path=config_path,
        target=target,
        repo_root=repo_root,
        profile_override=args.profile,
        tier_override=args.tier,
        dry_run=not args.apply,
        force=args.force,
        provenance_preview=args.provenance_preview,
        diff_preview=args.diff_preview,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
