"""Generate SHA-256 checksums for local release artifacts."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_repo_path(repo_root: Path, path_arg: str, flag_name: str) -> Path:
    raw_path = Path(path_arg)
    if raw_path.is_absolute() or raw_path.drive or raw_path.anchor:
        raise ValueError(f"{flag_name} must be a repo-internal relative path")
    if not raw_path.parts:
        raise ValueError(f"{flag_name} must name a file")
    if any(part == ".." for part in raw_path.parts):
        raise ValueError(f"{flag_name} must not contain parent traversal")
    resolved_root = repo_root.resolve()
    resolved_path = (resolved_root / raw_path).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{flag_name} must resolve inside the repository") from exc
    if resolved_path == resolved_root:
        raise ValueError(f"{flag_name} must name a file")
    return resolved_path


def build_checksum_lines(repo_root: Path, manifest_path: Path, output_path: Path) -> list[str]:
    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    output_path = output_path.resolve()
    if manifest_path == output_path:
        raise ValueError("--output must not overwrite --manifest")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest not found: {relpath(manifest_path, repo_root)}")

    artifacts = [manifest_path]
    lines = []
    for path in sorted(artifacts, key=lambda item: relpath(item, repo_root)):
        if path == output_path:
            continue
        lines.append(f"{sha256_file(path)}  {relpath(path, repo_root)}")
    return lines


def write_checksums(lines: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate SHA-256 checksums for local release artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--manifest", required=True, help="Repo-internal relative manifest path")
    parser.add_argument("--output", default="artifacts/checksums.sha256", help="Repo-internal relative output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        manifest_path = resolve_repo_path(repo_root, args.manifest, "--manifest")
        output_path = resolve_repo_path(repo_root, args.output, "--output")
        lines = build_checksum_lines(repo_root, manifest_path, output_path)
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))

    write_checksums(lines, output_path)
    print(f"Wrote checksums: {relpath(output_path, repo_root)}")
    print(f"Checksum entries: {len(lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
