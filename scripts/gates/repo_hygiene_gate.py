"""Repository hygiene gate for the template repo."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import tempfile
import uuid


IGNORED_PATH_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
}

ROOT_IGNORED_PATH_PARTS = {
    ".venv",
    "local",
}

TRACKED_PROHIBITED_ROOTS = {
    ".venv",
}

MAX_GIT_OUTPUT_BYTES = 1024 * 1024

_AMBIENT_GIT_KEYS = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_CONFIG",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_SYSTEM",
    "GIT_DIR",
    "GIT_EXEC_PATH",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_SHALLOW_FILE",
    "GIT_TEMPLATE_DIR",
    "GIT_WORK_TREE",
}

PROHIBITED_PATH_PARTS = {
    ".env",
    ".venv",
}

PROHIBITED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".pem",
    ".key",
    ".pfx",
}


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def _git_environment(repo_root: Path) -> dict[str, str]:
    environment = os.environ.copy()
    for name in list(environment):
        if name in _AMBIENT_GIT_KEYS or re.fullmatch(
            r"GIT_CONFIG_(?:COUNT|KEY_[0-9]+|VALUE_[0-9]+)", name
        ):
            environment.pop(name, None)

    disabled_hooks = Path(tempfile.gettempdir()) / (
        f"codex-harness-disabled-hooks-{uuid.uuid4().hex}"
    )
    if disabled_hooks.exists():
        raise RuntimeError("unable to isolate Git hooks")

    fixed_config = [
        ("commit.gpgSign", "false"),
        ("tag.gpgSign", "false"),
        ("core.hooksPath", str(disabled_hooks)),
        ("core.fsmonitor", "false"),
        ("submodule.recurse", "false"),
        ("safe.directory", str(repo_root.resolve())),
    ]
    environment.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GCM_INTERACTIVE": "Never",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_CONFIG_COUNT": str(len(fixed_config)),
        }
    )
    for index, (key, value) in enumerate(fixed_config):
        environment[f"GIT_CONFIG_KEY_{index}"] = key
        environment[f"GIT_CONFIG_VALUE_{index}"] = value
    return environment


def iter_repo_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        relative_parts = path.relative_to(repo_root).parts
        if relative_parts and relative_parts[0] in ROOT_IGNORED_PATH_PARTS:
            continue
        if any(part in IGNORED_PATH_PARTS for part in relative_parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def tracked_prohibited_root_files(repo_root: Path) -> list[Path]:
    git_marker = repo_root / ".git"
    if not git_marker.exists():
        return []
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo_root),
                "ls-files",
                "-z",
                "--",
                *sorted(TRACKED_PROHIBITED_ROOTS),
            ],
            shell=False,
            check=False,
            capture_output=True,
            timeout=30,
            env=_git_environment(repo_root),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("tracked prohibited path inspection failed") from exc
    if result.returncode != 0 or len(result.stdout) > MAX_GIT_OUTPUT_BYTES:
        raise RuntimeError("tracked prohibited path inspection failed")
    return [Path(os.fsdecode(raw)) for raw in result.stdout.split(b"\0") if raw]


def run(repo_root: Path) -> GateResult:
    findings: list[str] = []
    try:
        tracked_prohibited = tracked_prohibited_root_files(repo_root)
    except RuntimeError as exc:
        return GateResult("repo_hygiene_gate", False, [str(exc)])
    for relative in tracked_prohibited:
        findings.append(f"prohibited tracked root: {relative}")
    for path in iter_repo_files(repo_root):
        relative = path.relative_to(repo_root)
        parts = set(relative.parts)
        if parts & PROHIBITED_PATH_PARTS:
            findings.append(f"prohibited path part: {relative}")
        if path.suffix.lower() in PROHIBITED_SUFFIXES:
            findings.append(f"prohibited file suffix: {relative}")

    if findings:
        return GateResult("repo_hygiene_gate", False, findings)
    return GateResult("repo_hygiene_gate", True, ["repo hygiene checks passed"])
