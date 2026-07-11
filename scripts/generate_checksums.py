"""Generate SHA-256 checksums for local release artifacts."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = "artifacts"
DEFAULT_MANIFEST_PATH = "artifacts/release-manifest.json"
DEFAULT_CHECKSUMS_PATH = "artifacts/checksums.sha256"
REQUIRED_RELEASE_ARTIFACTS = (
    "artifacts/release-manifest.json",
    "artifacts/sbom.spdx.json",
    "artifacts/sbom.cdx.json",
    "artifacts/provenance.intoto.jsonl",
)
OPTIONAL_RELEASE_ARTIFACTS = (
    "artifacts/eval-report.json",
)


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def canonical_text_bytes(data: bytes) -> bytes:
    text = data.decode("utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(canonical_text_bytes(path.read_bytes())).hexdigest()


def resolve_repo_path(repo_root: Path, path_arg: str, flag_name: str) -> Path:
    raw_path = Path(path_arg)
    if raw_path.is_absolute() or raw_path.drive or raw_path.anchor:
        raise ValueError(f"{flag_name} must be a repo-internal relative path")
    if not raw_path.parts:
        raise ValueError(f"{flag_name} must name a file")
    if any(part == ".." for part in raw_path.parts):
        raise ValueError(f"{flag_name} must not contain parent traversal")
    if raw_path.parts[0] != ARTIFACTS_ROOT or len(raw_path.parts) < 2:
        raise ValueError(f"{flag_name} must be under artifacts/")
    resolved_root = repo_root.resolve()
    resolved_path = (resolved_root / raw_path).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{flag_name} must resolve inside the repository") from exc
    if resolved_path == resolved_root:
        raise ValueError(f"{flag_name} must name a file")
    return resolved_path


def dedupe_paths(paths: list[Path]) -> list[Path]:
    seen = set()
    unique_paths = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        unique_paths.append(path)
    return unique_paths


def release_artifact_path(repo_root: Path, relative_path: str) -> Path:
    return (repo_root / relative_path).resolve()


def collect_release_artifacts(
    repo_root: Path,
    manifest_path: Path,
    output_path: Path,
    allow_missing: bool = False,
) -> list[Path]:
    reserved_paths = {
        release_artifact_path(repo_root, relative_path)
        for relative_path in REQUIRED_RELEASE_ARTIFACTS + OPTIONAL_RELEASE_ARTIFACTS
    }
    if output_path in reserved_paths or output_path == manifest_path:
        raise ValueError("--output must not overwrite a release evidence artifact")

    required_paths = [manifest_path]
    required_paths.extend(
        release_artifact_path(repo_root, relative_path)
        for relative_path in REQUIRED_RELEASE_ARTIFACTS
    )
    required_paths = dedupe_paths(required_paths)

    artifacts = []
    missing = []
    for path in required_paths:
        if path.is_file():
            artifacts.append(path)
        elif allow_missing:
            continue
        else:
            missing.append(relpath(path, repo_root))

    if missing:
        raise FileNotFoundError(
            "required release evidence artifact(s) not found: " + ", ".join(missing)
        )

    for relative_path in OPTIONAL_RELEASE_ARTIFACTS:
        path = release_artifact_path(repo_root, relative_path)
        if path.is_file():
            artifacts.append(path)

    return sorted(dedupe_paths(artifacts), key=lambda item: relpath(item, repo_root))


def build_checksum_lines(
    repo_root: Path,
    manifest_path: Path,
    output_path: Path,
    allow_missing: bool = False,
) -> list[str]:
    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    output_path = output_path.resolve()
    artifacts = collect_release_artifacts(repo_root, manifest_path, output_path, allow_missing)
    lines = []
    for path in artifacts:
        if path == output_path:
            continue
        lines.append(f"{sha256_file(path)}  {relpath(path, repo_root)}")
    return lines


def parse_checksum_lines(lines: list[str], source: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for index, line in enumerate(lines, start=1):
        digest, separator, relative_path = line.partition("  ")
        if (
            not separator
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or not relative_path
        ):
            raise ValueError(f"{source} line {index} is not a valid SHA-256 entry")
        if relative_path in entries:
            raise ValueError(f"{source} contains duplicate path: {relative_path}")
        entries[relative_path] = digest
    return entries


def verify_checksums(
    repo_root: Path,
    manifest_path: Path,
    output_path: Path,
    allow_missing: bool = False,
) -> tuple[bool, list[str]]:
    if not output_path.is_file():
        raise FileNotFoundError(f"checksum file not found: {relpath(output_path, repo_root)}")

    actual = parse_checksum_lines(
        build_checksum_lines(repo_root, manifest_path, output_path, allow_missing),
        "recomputed checksums",
    )
    expected = parse_checksum_lines(
        output_path.read_text(encoding="utf-8").splitlines(),
        relpath(output_path, repo_root),
    )

    findings: list[str] = []
    if list(expected) != sorted(expected):
        findings.append("checksum paths are not sorted")
    for relative_path in sorted(set(expected) | set(actual)):
        if relative_path not in expected:
            findings.append(f"MISSING checksum entry: {relative_path}")
        elif relative_path not in actual:
            findings.append(f"STALE checksum entry: {relative_path}")
        elif expected[relative_path] != actual[relative_path]:
            findings.append(
                f"MISMATCH {relative_path}: expected {expected[relative_path]}, "
                f"actual {actual[relative_path]}"
            )

    if findings:
        return False, findings
    messages = [f"MATCH {relative_path}" for relative_path in sorted(actual)]
    messages.append(f"verified checksum entries: {len(actual)}")
    return True, messages


def write_checksums(lines: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate SHA-256 checksums for local release artifacts.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root")
    parser.add_argument("--manifest", help="Repo-internal relative manifest path")
    parser.add_argument("--output", default=DEFAULT_CHECKSUMS_PATH, help="Repo-internal relative output path")
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Skip missing release evidence artifacts instead of failing",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Recompute and compare checksums without writing the output file",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    manifest_arg = args.manifest
    if manifest_arg is None:
        if args.verify:
            manifest_arg = DEFAULT_MANIFEST_PATH
        else:
            parser.error("--manifest is required unless --verify is used")
    try:
        manifest_path = resolve_repo_path(repo_root, manifest_arg, "--manifest")
        output_path = resolve_repo_path(repo_root, args.output, "--output")
        if args.verify:
            passed, messages = verify_checksums(
                repo_root,
                manifest_path,
                output_path,
                args.allow_missing,
            )
        else:
            lines = build_checksum_lines(repo_root, manifest_path, output_path, args.allow_missing)
    except (ValueError, FileNotFoundError) as exc:
        parser.error(str(exc))

    if args.verify:
        for message in messages:
            print(message)
        print("Checksum verification passed." if passed else "Checksum verification failed.")
        return 0 if passed else 1

    write_checksums(lines, output_path)
    print(f"Wrote checksums: {relpath(output_path, repo_root)}")
    print(f"Checksum entries: {len(lines)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
