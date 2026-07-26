"""Small secret and private-pattern scan for text files."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re


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


def iter_text_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
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
            if path.is_file() and not path.is_symlink() and is_text_candidate(path):
                files.append(path)
    return files


def run(repo_root: Path) -> GateResult:
    findings: list[str] = []
    for path in iter_text_files(repo_root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match:
                findings.append(f"{path.relative_to(repo_root)} matched {pattern.pattern}")

    if findings:
        return GateResult("secret_scan_gate", False, findings)
    return GateResult("secret_scan_gate", True, ["no obvious secret/private patterns found"])
