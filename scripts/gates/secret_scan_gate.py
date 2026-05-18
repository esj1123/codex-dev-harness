"""Small secret and private-pattern scan for text files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


TEXT_SUFFIXES = {
    ".md",
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
    if path.name.endswith(".template"):
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def iter_text_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        relative_parts = path.relative_to(repo_root).parts
        if any(part in IGNORED_PATH_PARTS for part in relative_parts) or not path.is_file():
            continue
        if is_text_candidate(path):
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
