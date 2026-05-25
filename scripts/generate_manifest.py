"""Generate a local release manifest for codex-dev-harness.

The manifest is local-only evidence. It records file metadata and verification
command placeholders; it does not run verification commands or contact external
services.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1"
ARTIFACTS_ROOT = "artifacts"

INCLUDED_ROOTS = [
    ".python-version",
    "ACCEPTANCE_TRACE.md",
    "AGENTS.md",
    "MVP.md",
    "PRODUCT.md",
    "README.md",
    "ROADMAP.md",
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
    "secret_scan_gate",
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


def iter_manifest_files(repo_root: Path, included_roots: list[str] | None = None) -> list[Path]:
    roots = included_roots or INCLUDED_ROOTS
    files: dict[str, Path] = {}
    for root in roots:
        base = repo_root / root
        if not base.exists() or should_exclude(base, repo_root):
            continue
        candidates = [base] if base.is_file() else list(base.rglob("*"))
        for path in candidates:
            if not path.is_file() or should_exclude(path, repo_root):
                continue
            files[relpath(path, repo_root)] = path
    return [files[key] for key in sorted(files)]


def file_record(path: Path, repo_root: Path) -> dict[str, Any]:
    return {
        "path": relpath(path, repo_root),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def run_git(repo_root: Path, args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
    except (OSError, ValueError):
        return None
    if completed.returncode != 0:
        return None
    output = completed.stdout.strip()
    return output or None


def normalize_repository(remote_url: str | None) -> str:
    if not remote_url:
        return "UNKNOWN"
    value = remote_url.strip()
    if value.endswith(".git"):
        value = value[:-4]
    if "github.com/" in value:
        return value.split("github.com/", 1)[1]
    if value.startswith("git@github.com:"):
        return value.split(":", 1)[1]
    return value or "UNKNOWN"


def git_metadata(repo_root: Path) -> dict[str, str | None]:
    remote = run_git(repo_root, ["config", "--get", "remote.origin.url"])
    branch = run_git(repo_root, ["branch", "--show-current"])
    commit = run_git(repo_root, ["rev-parse", "HEAD"])
    exact_tag = run_git(repo_root, ["describe", "--tags", "--exact-match"])

    return {
        "repository": normalize_repository(remote),
        "git_ref": branch or "UNKNOWN",
        "git_commit": commit or "UNKNOWN",
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
    files = [file_record(path, repo_root) for path in iter_manifest_files(repo_root)]

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
    raw_path = Path(output_arg)
    if raw_path.is_absolute() or raw_path.drive or raw_path.anchor:
        raise ValueError("--output must be a repo-internal relative path")
    if not raw_path.parts:
        raise ValueError("--output must name a file")
    if any(part == ".." for part in raw_path.parts):
        raise ValueError("--output must not contain parent traversal")
    if raw_path.parts[0] != ARTIFACTS_ROOT or len(raw_path.parts) < 2:
        raise ValueError("--output must be under artifacts/")
    resolved_root = repo_root.resolve()
    output_path = (resolved_root / raw_path).resolve()
    try:
        output_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("--output must resolve inside the repository") from exc
    if output_path == resolved_root:
        raise ValueError("--output must name a file")
    return output_path


def write_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


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

    manifest = build_manifest(repo_root)
    write_manifest(manifest, output_path)
    print(f"Wrote release manifest: {relpath(output_path, repo_root)}")
    print(f"Manifest files recorded: {len(manifest['files'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
