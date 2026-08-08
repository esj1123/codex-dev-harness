"""Small secret and private-pattern scan for text files."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess


TEXT_SUFFIXES = {
    ".ini",
    ".json",
    ".jsonl",
    ".lock",
    ".md",
    ".ps1",
    ".sha256",
    ".template",
    ".py",
    ".yml",
    ".yaml",
    ".txt",
}

IGNORED_PATH_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
}

EXACT_TEXT_NAMES = {
    ".gitattributes",
    ".gitignore",
    ".python-version",
    "LICENSE",
}

ROOT_IGNORED_PATH_PARTS = {
    ".venv",
    "local",
    "venv",
}

MAX_TRACKED_TEXT_BYTES = 1024 * 1024

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
]


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    messages: list[str]


def is_text_candidate(path: Path) -> bool:
    if path.name in EXACT_TEXT_NAMES:
        return True
    if path.name.endswith(".template"):
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def tracked_repo_files(repo_root: Path) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError:
        return set()
    if result.returncode != 0:
        return set()
    try:
        return {
            item.decode("utf-8")
            for item in result.stdout.split(b"\0")
            if item
        }
    except UnicodeDecodeError:
        return set()


def iter_text_files(
    repo_root: Path, tracked_files: set[str] | None = None
) -> list[Path]:
    tracked = tracked_files if tracked_files is not None else tracked_repo_files(repo_root)
    files: list[Path] = []
    for relative in sorted(tracked):
        path = repo_root / Path(relative)
        if path.is_file() and not path.is_symlink():
            files.append(path)
    for current_root, dir_names, file_names in os.walk(
        repo_root, topdown=True, followlinks=False
    ):
        current = Path(current_root)
        relative_parts = current.relative_to(repo_root).parts
        dir_names[:] = sorted(
            name
            for name in dir_names
            if name not in IGNORED_PATH_PARTS
            and not (
                not relative_parts and name in ROOT_IGNORED_PATH_PARTS
            )
        )
        for name in sorted(file_names):
            path = current / name
            relative = path.relative_to(repo_root).as_posix()
            if (
                relative not in tracked
                and path.is_file()
                and not path.is_symlink()
                and is_text_candidate(path)
            ):
                files.append(path)
    return files


def run(repo_root: Path) -> GateResult:
    findings: list[str] = []
    tracked = tracked_repo_files(repo_root)
    for path in iter_text_files(repo_root, tracked):
        relative = path.relative_to(repo_root).as_posix()
        try:
            data = path.read_bytes()
        except OSError:
            if relative in tracked:
                findings.append(f"{relative} could not be scanned")
            continue
        if len(data) > MAX_TRACKED_TEXT_BYTES:
            if relative in tracked:
                findings.append(f"{relative} exceeds tracked text scan limit")
            continue
        if b"\0" in data:
            continue
        text = data.decode("utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append(f"{relative} matched {pattern.pattern}")

    if findings:
        return GateResult("secret_scan_gate", False, findings)
    return GateResult("secret_scan_gate", True, ["no obvious secret/private patterns found"])
