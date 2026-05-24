"""Repository hygiene gate for the template repo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


IGNORED_PATH_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
}

ROOT_IGNORED_PATH_PARTS = {
    "local",
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


def run(repo_root: Path) -> GateResult:
    findings: list[str] = []
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
