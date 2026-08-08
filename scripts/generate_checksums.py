"""Generate SHA-256 checksums for local release artifacts."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import stat
import sys
import tempfile


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = "artifacts"
DEFAULT_MANIFEST_PATH = "artifacts/release-manifest.json"
DEFAULT_CHECKSUMS_PATH = "artifacts/checksums.sha256"
LEGACY_CHECKSUMS_PATHS = (
    "artifacts/checksums.txt",
)
REQUIRED_RELEASE_ARTIFACTS = (
    DEFAULT_MANIFEST_PATH,
    "artifacts/sbom.spdx.json",
    "artifacts/sbom.cdx.json",
    "artifacts/provenance.intoto.jsonl",
)
OPTIONAL_RELEASE_ARTIFACTS = (
    "artifacts/eval-report.json",
)
CHECKSUM_OUTPUT_PATHS = (DEFAULT_CHECKSUMS_PATH, *LEGACY_CHECKSUMS_PATHS)
RESERVED_RELEASE_ARTIFACTS = tuple(
    dict.fromkeys(
        (*REQUIRED_RELEASE_ARTIFACTS, *CHECKSUM_OUTPUT_PATHS, *OPTIONAL_RELEASE_ARTIFACTS)
    )
)


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def canonical_text_bytes(data: bytes) -> bytes:
    text = data.decode("utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    repo_root = infer_repo_root(path)
    return hashlib.sha256(canonical_text_bytes(read_regular_file(repo_root, path))).hexdigest()


def _is_reparse_point(stat_result: os.stat_result) -> bool:
    attributes = getattr(stat_result, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _path_identity(path: Path, *, include_content_state: bool = False) -> tuple[int, ...] | None:
    try:
        observed = path.lstat()
    except FileNotFoundError:
        return None
    values = [
        observed.st_dev,
        observed.st_ino,
        observed.st_mode,
        getattr(observed, "st_file_attributes", 0),
        observed.st_nlink,
    ]
    if include_content_state:
        values.extend([observed.st_size, observed.st_mtime_ns])
    return tuple(values)


def infer_repo_root(path: Path) -> Path:
    absolute = path.absolute()
    for parent in (absolute.parent, *absolute.parents):
        if parent.name == ARTIFACTS_ROOT:
            return parent.parent
    return absolute.parent


def validate_physical_path(
    repo_root: Path,
    path: Path,
    flag_name: str,
    *,
    require_file: bool = False,
    require_directory: bool = False,
) -> None:
    root = repo_root.resolve()
    candidate = path.absolute()
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{flag_name} must stay inside the repository") from exc

    current = root
    for index, part in enumerate(relative.parts):
        current = current / part
        try:
            observed = current.lstat()
        except FileNotFoundError:
            if require_file:
                raise FileNotFoundError(f"{flag_name} path component not found")
            return
        if stat.S_ISLNK(observed.st_mode) or _is_reparse_point(observed):
            raise ValueError(f"{flag_name} must not contain a symlink or reparse point")
        is_leaf = index == len(relative.parts) - 1
        if not is_leaf and not stat.S_ISDIR(observed.st_mode):
            raise ValueError(f"{flag_name} parent must be a regular directory")
        if is_leaf:
            if require_file and not stat.S_ISREG(observed.st_mode):
                raise ValueError(f"{flag_name} must be a regular file")
            if require_directory and not stat.S_ISDIR(observed.st_mode):
                raise ValueError(f"{flag_name} must be a regular directory")
            if stat.S_ISREG(observed.st_mode) and observed.st_nlink != 1:
                raise ValueError(f"{flag_name} must not be a multiply-linked file")


def read_regular_file(repo_root: Path, path: Path, flag_name: str = "input") -> bytes:
    validate_physical_path(repo_root, path, flag_name, require_file=True)
    before = _path_identity(path, include_content_state=True)
    data = path.read_bytes()
    validate_physical_path(repo_root, path, flag_name, require_file=True)
    if _path_identity(path, include_content_state=True) != before:
        raise ValueError(f"{flag_name} identity changed while reading")
    return data


def _replace_validated_temp(
    repo_root: Path,
    temp_path: Path,
    output_path: Path,
    parent_identity: tuple[int, ...],
    target_identity: tuple[int, ...] | None,
) -> None:
    validate_physical_path(
        repo_root, output_path.parent, "output parent", require_directory=True
    )
    if _path_identity(output_path.parent) != parent_identity:
        raise ValueError("output parent identity changed before replacement")
    if _path_identity(output_path, include_content_state=True) != target_identity:
        raise ValueError("output target identity changed before replacement")
    validate_physical_path(repo_root, output_path, "output", require_file=False)
    validate_physical_path(repo_root, temp_path, "temporary output", require_file=True)
    os.replace(temp_path, output_path)


def write_artifact_bytes(output_path: Path, data: bytes, repo_root: Path | None = None) -> None:
    root = (repo_root or infer_repo_root(output_path)).resolve()
    validate_physical_path(root, output_path, "output", require_file=False)
    if output_path.exists():
        validate_physical_path(root, output_path, "output", require_file=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    validate_physical_path(
        root, output_path.parent, "output parent", require_directory=True
    )
    validate_physical_path(root, output_path, "output", require_file=False)
    parent_identity = _path_identity(output_path.parent)
    target_identity = _path_identity(output_path, include_content_state=True)
    if parent_identity is None:
        raise ValueError("output parent is unavailable")
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        _replace_validated_temp(
            root,
            temp_path,
            output_path,
            parent_identity,
            target_identity,
        )
    finally:
        if temp_path.exists():
            temp_path.unlink()


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
    lexical_path = resolved_root / raw_path
    validate_physical_path(resolved_root, lexical_path, flag_name)
    resolved_path = lexical_path.resolve()
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
    path = repo_root.resolve() / relative_path
    validate_physical_path(repo_root, path, "release artifact")
    return path.resolve()


def validate_release_output_path(
    repo_root: Path,
    output_path: Path,
    *,
    allowed_reserved_paths: tuple[str, ...],
    flag_name: str,
) -> None:
    validate_physical_path(repo_root, output_path, flag_name)
    if output_path.exists():
        validate_physical_path(repo_root, output_path, flag_name, require_file=True)
    resolved_output = output_path.resolve()
    reserved_paths = {
        release_artifact_path(repo_root, relative_path)
        for relative_path in RESERVED_RELEASE_ARTIFACTS
    }
    allowed_paths = {
        release_artifact_path(repo_root, relative_path)
        for relative_path in allowed_reserved_paths
    }
    if resolved_output in reserved_paths and resolved_output not in allowed_paths:
        raise ValueError(f"{flag_name} must not overwrite a reserved release artifact")


def collect_release_artifacts(
    repo_root: Path,
    manifest_path: Path,
    output_path: Path,
    allow_missing: bool = False,
) -> list[Path]:
    validate_release_output_path(
        repo_root,
        output_path,
        allowed_reserved_paths=CHECKSUM_OUTPUT_PATHS,
        flag_name="--output",
    )
    if output_path == manifest_path:
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
        if path.exists():
            validate_physical_path(repo_root, path, "release artifact", require_file=True)
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
        if path.exists():
            validate_physical_path(repo_root, path, "optional release artifact", require_file=True)
            artifacts.append(path)

    return sorted(dedupe_paths(artifacts), key=lambda item: relpath(item, repo_root))


def build_checksum_lines(
    repo_root: Path,
    manifest_path: Path,
    output_path: Path,
    allow_missing: bool = False,
) -> list[str]:
    repo_root = repo_root.resolve()
    validate_physical_path(
        repo_root, manifest_path, "--manifest", require_file=True
    )
    validate_physical_path(repo_root, output_path, "--output")
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
        read_regular_file(repo_root, output_path, "checksum file")
        .decode("utf-8")
        .splitlines(),
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
    write_artifact_bytes(output_path, ("\n".join(lines) + "\n").encode("utf-8"))


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
