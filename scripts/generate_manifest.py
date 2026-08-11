"""Generate a local release manifest for codex-dev-harness.

The manifest is local-only evidence. It records file metadata and verification
command placeholders; it does not run verification commands or contact external
services.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, BinaryIO
from urllib.parse import urlsplit

try:
    from scripts import generate_checksums as release_artifacts
except ImportError:  # Direct script execution from scripts/.
    import generate_checksums as release_artifacts


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1"
ARTIFACTS_ROOT = "artifacts"
GIT_TIMEOUT_SECONDS = 15
SHA1_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
REGULAR_BLOB_MODES = {"100644", "100755"}
_BATCH_HEADER_LIMIT_BYTES = 128
_BATCH_READ_CHUNK_BYTES = 1024 * 1024

INCLUDED_ROOTS = [
    ".python-version",
    "ACCEPTANCE_TRACE.md",
    "AGENTS.md",
    "LICENSE",
    "MVP.md",
    "PRODUCT.md",
    "README.md",
    "ROADMAP.md",
    "SECURITY.md",
    "STATUS.md",
    "audits",
    "code_review.md",
    "docs",
    "evals",
    "examples",
    "profiles",
    "prompts",
    "pytest.ini",
    "requirements-dev.lock",
    "requirements-dev.txt",
    "scripts",
    "template.config.example.yml",
    "templates",
    "tests",
]

EXCLUDED_PATTERNS = [
    ".git/",
    ".venv/",
    "__pycache__/",
    ".pytest_cache/",
    "artifacts/",
    "local/",
    "raw source bundles",
    "private input",
    "live configuration",
    "downstream generated target output",
    "clean clone temporary folders",
    "secrets, credentials, tokens",
    "equipment connection details",
    "IP/port/tag/live parameter values",
]

EXCLUDED_PATH_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
}

EXCLUDED_ROOTS = {
    "artifacts",
    "local",
}

EXCLUDED_SUFFIXES = {
    ".pyc",
    ".pyo",
}

VERIFICATION_COMMANDS = [
    "python -m pytest",
    "python scripts/quality_gate.py",
    "python scripts/generate_manifest.py --output artifacts/release-manifest.json",
    "python scripts/generate_checksums.py --manifest artifacts/release-manifest.json --output artifacts/checksums.sha256",
]

QUALITY_GATES = [
    "docs_gate",
    "repo_hygiene_gate",
    "template_schema_gate",
    "example_gate",
    "example_render_drift_gate",
    "rendered_golden_content_gate",
    "secret_scan_gate",
    "json_evidence_gate",
]

EXAMPLE_RENDER_DRY_RUNS = [
    {
        "example": "python_cli_minimal",
        "command": "python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run",
    },
    {
        "example": "csharp_desktop_minimal",
        "command": "python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run",
    },
    {
        "example": "plc_tool_minimal",
        "command": "python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run",
    },
]


def _freeze_json_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze_json_value(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json_value(item) for item in value)
    return value


@dataclass(frozen=True)
class ValidatedManifestSnapshot:
    manifest_path: Path
    manifest: Mapping[str, Any]
    canonical_sha256: str

    def __post_init__(self) -> None:
        if SHA256_PATTERN.fullmatch(self.canonical_sha256) is None:
            raise ValueError("manifest snapshot digest must be lowercase SHA-256")
        object.__setattr__(self, "manifest", _freeze_json_value(self.manifest))


def relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_exclude(path: Path, repo_root: Path) -> bool:
    relative_parts = path.relative_to(repo_root).parts
    if not relative_parts:
        return False
    if relative_parts[0] in EXCLUDED_ROOTS:
        return True
    if any(part in EXCLUDED_PATH_PARTS for part in relative_parts):
        return True
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    return False


def run_git_bytes(
    repo_root: Path,
    args: list[str],
    *,
    required: bool = True,
    input_bytes: bytes | None = None,
) -> bytes | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            check=False,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        if required:
            raise ValueError("Git repository inspection failed") from exc
        return None
    if completed.returncode != 0:
        if required:
            raise ValueError("Git repository inspection failed")
        return None
    return completed.stdout


def run_git_text(
    repo_root: Path,
    args: list[str],
    *,
    required: bool = True,
) -> str | None:
    raw = run_git_bytes(repo_root, args, required=required)
    if raw is None:
        return None
    try:
        value = raw.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ValueError("Git repository output is not UTF-8") from exc
    return value or None


def _validate_git_path(path: str) -> None:
    parts = PurePosixPath(path).parts
    if (
        not path
        or path.startswith("/")
        or "\\" in path
        or any(part in ("", ".", "..") for part in parts)
        or any(ord(character) < 32 or ord(character) == 127 for character in path)
    ):
        raise ValueError("Git tree contains an unsafe path")


def _parse_cat_file_batch(
    stream: BinaryIO,
    requested_object_ids: list[str],
) -> list[tuple[int, str]]:
    metadata: list[tuple[int, str]] = []
    for expected_object_id in requested_object_ids:
        header = stream.readline(_BATCH_HEADER_LIMIT_BYTES)
        if not header or not header.endswith(b"\n"):
            raise ValueError("Git cat-file batch output is malformed")
        try:
            object_id, object_type, raw_size = header[:-1].decode("ascii").split(" ")
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError("Git cat-file batch output is malformed") from exc
        if (
            object_id != expected_object_id
            or object_type != "blob"
            or not raw_size
            or not raw_size.isdecimal()
        ):
            raise ValueError("Git cat-file batch output is malformed")
        size = int(raw_size)
        remaining = size
        digest = hashlib.sha256()
        while remaining:
            read_size = min(_BATCH_READ_CHUNK_BYTES, remaining)
            chunk = stream.read(read_size)
            if not chunk or len(chunk) > read_size:
                raise ValueError("Git cat-file batch output is malformed")
            digest.update(chunk)
            remaining -= len(chunk)
        if stream.read(1) != b"\n":
            raise ValueError("Git cat-file batch output is malformed")
        metadata.append((size, digest.hexdigest()))
    if stream.read(1) != b"":
        raise ValueError("Git cat-file batch output is malformed")
    return metadata


def _run_git_cat_file_batch(
    repo_root: Path,
    requested_object_ids: list[str],
) -> list[tuple[int, str]]:
    batch_input = b"".join(
        object_id.encode("ascii") + b"\n" for object_id in requested_object_ids
    )
    try:
        batch_output = tempfile.TemporaryFile(mode="w+b")
    except OSError as exc:
        raise ValueError("Git repository inspection failed") from exc

    with batch_output:
        try:
            completed = subprocess.run(
                ["git", "-C", str(repo_root), "cat-file", "--batch"],
                check=False,
                input=batch_input,
                stdout=batch_output,
                stderr=subprocess.DEVNULL,
                timeout=GIT_TIMEOUT_SECONDS,
            )
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            raise ValueError("Git repository inspection failed") from exc
        if completed.returncode != 0:
            raise ValueError("Git repository inspection failed")
        try:
            batch_output.seek(0)
            return _parse_cat_file_batch(batch_output, requested_object_ids)
        except OSError as exc:
            raise ValueError("Git repository inspection failed") from exc


def git_tree_file_records(
    repo_root: Path,
    head_sha: str,
    included_roots: list[str] | None = None,
) -> list[dict[str, Any]]:
    roots = included_roots or INCLUDED_ROOTS
    raw = run_git_bytes(
        repo_root,
        ["ls-tree", "-rz", "--full-tree", head_sha, "--", *roots],
    )
    assert raw is not None
    requests: list[tuple[str, str]] = []
    paths: set[str] = set()
    casefold_paths: dict[str, str] = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        try:
            header, raw_path = entry.split(b"\t", 1)
            mode, object_type, object_id = header.decode("ascii").split(" ")
            path = raw_path.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError("Git tree entry is malformed") from exc
        _validate_git_path(path)
        relative = Path(*PurePosixPath(path).parts)
        if should_exclude(repo_root / relative, repo_root):
            continue
        if object_type != "blob" or mode not in REGULAR_BLOB_MODES:
            raise ValueError(f"Git tree entry is not a regular blob: {path}")
        if SHA1_PATTERN.fullmatch(object_id) is None:
            raise ValueError("Git tree entry is malformed")
        folded = path.casefold()
        if path in paths or (folded in casefold_paths and casefold_paths[folded] != path):
            raise ValueError("Git tree contains duplicate manifest paths")
        requests.append((path, object_id))
        paths.add(path)
        casefold_paths[folded] = path

    blob_metadata: list[tuple[int, str]] = []
    if requests:
        blob_metadata = _run_git_cat_file_batch(
            repo_root, [object_id for _, object_id in requests]
        )

    records: dict[str, dict[str, Any]] = {}
    for (path, _), (size, digest) in zip(
        requests, blob_metadata, strict=True
    ):
        records[path] = {
            "path": path,
            "size_bytes": size,
            "sha256": digest,
        }
    return [records[path] for path in sorted(records)]


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"release manifest contains duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_non_finite_json(value: str) -> None:
    raise ValueError(f"release manifest contains non-finite JSON number: {value}")


def _parse_manifest_bytes(data: bytes) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("release manifest is not strict UTF-8") from exc
    try:
        manifest = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_json_keys,
            parse_constant=_reject_non_finite_json,
        )
    except json.JSONDecodeError as exc:
        raise ValueError("release manifest is not valid JSON") from exc
    if not isinstance(manifest, dict):
        raise ValueError("release manifest must be a JSON object")
    return manifest


def _validated_manifest_file_records(
    files: Any,
) -> list[dict[str, Any]]:
    if not isinstance(files, list):
        raise ValueError("release manifest files must be an array")
    records: list[dict[str, Any]] = []
    paths: set[str] = set()
    casefold_paths: dict[str, str] = {}
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {
            "path",
            "size_bytes",
            "sha256",
        }:
            raise ValueError(
                "release manifest file records must contain only path, size_bytes, and sha256"
            )
        path = entry["path"]
        size = entry["size_bytes"]
        digest = entry["sha256"]
        if not isinstance(path, str):
            raise ValueError("release manifest file path must be a string")
        _validate_git_path(path)
        folded = path.casefold()
        if path in paths or (
            folded in casefold_paths and casefold_paths[folded] != path
        ):
            raise ValueError("release manifest contains duplicate file paths")
        if type(size) is not int or size < 0:
            raise ValueError("release manifest file size must be a non-negative integer")
        if not isinstance(digest, str) or SHA256_PATTERN.fullmatch(digest) is None:
            raise ValueError("release manifest file digest must be lowercase SHA-256")
        records.append({"path": path, "size_bytes": size, "sha256": digest})
        paths.add(path)
        casefold_paths[folded] = path
    if records != sorted(records, key=lambda item: item["path"]):
        raise ValueError("release manifest file records must be sorted by path")
    return records


def load_validated_manifest_snapshot(
    repo_root: Path,
    manifest_path: Path,
) -> ValidatedManifestSnapshot:
    root = repo_root.resolve()
    path = manifest_path.absolute()
    data = release_artifacts.read_regular_file(root, path, "--manifest")
    manifest = _parse_manifest_bytes(data)

    commit = manifest.get("git_commit")
    if not isinstance(commit, str) or SHA1_PATTERN.fullmatch(commit) is None:
        raise ValueError(
            "release manifest git_commit must be a lowercase 40-character SHA"
        )
    top_level = run_git_text(root, ["rev-parse", "--show-toplevel"])
    if top_level is None or Path(top_level).resolve() != root:
        raise ValueError("--repo-root must be the exact Git repository root")
    head = run_git_text(root, ["rev-parse", "--verify", "HEAD"])
    if head is None or SHA1_PATTERN.fullmatch(head) is None:
        raise ValueError("Git HEAD must be an exact 40-character commit")
    if commit != head:
        raise ValueError("release manifest git_commit must match current HEAD")

    if manifest.get("included_roots") != INCLUDED_ROOTS:
        raise ValueError("release manifest included_roots do not match policy")
    records = _validated_manifest_file_records(manifest.get("files"))
    expected = git_tree_file_records(root, commit, list(INCLUDED_ROOTS))
    actual_paths = {record["path"] for record in records}
    expected_paths = {record["path"] for record in expected}
    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)
        extra = sorted(actual_paths - expected_paths)
        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
        raise ValueError(
            "release manifest file inventory does not match commit tree: "
            + "; ".join(details)
        )
    if records != expected:
        mismatched = next(
            actual["path"]
            for actual, committed in zip(records, expected, strict=True)
            if actual != committed
        )
        raise ValueError(
            f"release manifest file metadata does not match commit tree: {mismatched}"
        )
    final_head = run_git_text(root, ["rev-parse", "--verify", "HEAD"])
    if final_head != head:
        raise ValueError("Git HEAD changed while validating release manifest")

    canonical_sha256 = hashlib.sha256(
        release_artifacts.canonical_text_bytes(data)
    ).hexdigest()
    return ValidatedManifestSnapshot(path, manifest, canonical_sha256)


def _remote_host_path(remote_url: str) -> tuple[str, str] | None:
    value = remote_url.strip()
    if not value or any(ord(character) < 32 or ord(character) == 127 for character in value):
        return None

    try:
        if "://" in value:
            parsed = urlsplit(value)
            host = parsed.hostname
            path = parsed.path
        else:
            match = re.fullmatch(
                r"(?:[^@/:\s]+@)?(?P<host>[^/:\s]+):(?P<path>[^?#]+)(?:[?#].*)?",
                value,
            )
            if match is None:
                return None
            host = match.group("host")
            path = match.group("path")
    except ValueError:
        return None

    if not host:
        return None
    normalized_path = path.replace("\\", "/").strip("/")
    if normalized_path.endswith(".git"):
        normalized_path = normalized_path[:-4]
    parts = normalized_path.split("/") if normalized_path else []
    if (
        not parts
        or any(part in ("", ".", "..") for part in parts)
        or any(any(ord(character) < 32 or ord(character) == 127 for character in part) for part in parts)
    ):
        return None
    return host.lower(), "/".join(parts)


def normalize_repository(remote_url: str | None) -> str:
    if not remote_url:
        return "UNKNOWN"
    parsed = _remote_host_path(remote_url)
    if parsed is None:
        return "UNKNOWN"
    host, path = parsed
    if host == "github.com":
        parts = path.split("/")
        return path if len(parts) == 2 else "UNKNOWN"
    identity = hashlib.sha256(f"{host}/{path}".encode("utf-8")).hexdigest()[:16]
    return f"external-repository/{identity}"


def git_metadata(repo_root: Path) -> dict[str, str | None]:
    resolved_root = repo_root.resolve()
    top_level = run_git_text(resolved_root, ["rev-parse", "--show-toplevel"])
    if top_level is None or Path(top_level).resolve() != resolved_root:
        raise ValueError("--repo-root must be the exact Git repository root")
    commit = run_git_text(resolved_root, ["rev-parse", "--verify", "HEAD"])
    if commit is None or SHA1_PATTERN.fullmatch(commit) is None:
        raise ValueError("Git HEAD must be an exact 40-character commit")
    status = run_git_bytes(
        resolved_root,
        ["status", "--porcelain=v1", "--untracked-files=all"],
    )
    if status:
        raise ValueError("Git repository must be clean, including untracked files")
    remote = run_git_text(
        resolved_root,
        ["config", "--get", "remote.origin.url"],
        required=False,
    )
    branch = run_git_text(
        resolved_root,
        ["branch", "--show-current"],
        required=False,
    )
    exact_tag = run_git_text(
        resolved_root,
        ["describe", "--tags", "--exact-match"],
        required=False,
    )

    return {
        "repository": normalize_repository(remote),
        "git_ref": branch or "UNKNOWN",
        "git_commit": commit,
        "git_tag": exact_tag,
    }


def command_metadata(command: str) -> dict[str, str]:
    return {
        "command": command,
        "result": "NOT_RUN",
        "notes": "Recorded as metadata only; this generator does not run verification commands.",
    }


def gate_metadata(name: str) -> dict[str, str]:
    return {
        "name": name,
        "result": "NOT_RUN",
        "notes": "Recorded as metadata only; run scripts/quality_gate.py for proof.",
    }


def render_metadata(entry: dict[str, str]) -> dict[str, str]:
    return {
        "example": entry["example"],
        "command": entry["command"],
        "result": "NOT_RUN",
        "notes": "Recorded as metadata only; dry-run command was not executed by this generator.",
    }


def build_manifest(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    metadata = git_metadata(repo_root)
    commit = str(metadata["git_commit"])
    if SHA1_PATTERN.fullmatch(commit) is None:
        raise ValueError("release source basis is UNKNOWN")
    files = git_tree_file_records(repo_root, commit)

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "repository": metadata["repository"],
        "git_ref": metadata["git_ref"],
        "git_commit": metadata["git_commit"],
        "git_tag": metadata["git_tag"],
        "python_version": platform.python_version(),
        "included_roots": INCLUDED_ROOTS,
        "excluded_patterns": EXCLUDED_PATTERNS,
        "verification_commands": [command_metadata(command) for command in VERIFICATION_COMMANDS],
        "quality_gates": [gate_metadata(name) for name in QUALITY_GATES],
        "eval_summary": None,
        "example_render_dry_runs": [render_metadata(entry) for entry in EXAMPLE_RENDER_DRY_RUNS],
        "files": files,
    }


def resolve_output_path(repo_root: Path, output_arg: str) -> Path:
    resolved_root = repo_root.resolve()
    output_path = release_artifacts.resolve_repo_path(
        resolved_root, output_arg, "--output"
    )
    release_artifacts.validate_release_output_path(
        resolved_root,
        output_path,
        allowed_reserved_paths=(release_artifacts.DEFAULT_MANIFEST_PATH,),
        flag_name="--output",
    )
    return output_path


def write_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    release_artifacts.write_artifact_bytes(
        output_path, (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a local release manifest.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help="Repository root to inspect")
    parser.add_argument("--output", default="artifacts/release-manifest.json", help="Repo-internal relative output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        output_path = resolve_output_path(repo_root, args.output)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        manifest = build_manifest(repo_root)
    except ValueError as exc:
        parser.error(str(exc))
    write_manifest(manifest, output_path)
    print(f"Wrote release manifest: {relpath(output_path, repo_root)}")
    print(f"Manifest files recorded: {len(manifest['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
