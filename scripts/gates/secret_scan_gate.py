"""Small secret and private-pattern scan for text files."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
import uuid


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
MAX_GIT_OUTPUT_BYTES = 4 * 1024 * 1024
GIT_TIMEOUT_SECONDS = 30

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


class SecretScanError(RuntimeError):
    pass


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
        raise SecretScanError("unable to isolate Git hooks")

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


def is_text_candidate(path: Path) -> bool:
    if path.name in EXACT_TEXT_NAMES:
        return True
    if path.name.endswith(".template"):
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def _is_reparse_point(observed: os.stat_result) -> bool:
    attributes = getattr(observed, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _path_identity(path: Path) -> tuple[int, ...]:
    observed = path.lstat()
    return (
        observed.st_dev,
        observed.st_ino,
        observed.st_mode,
        getattr(observed, "st_file_attributes", 0),
        observed.st_nlink,
        observed.st_size,
        observed.st_mtime_ns,
    )


def _validate_tracked_relative_path(raw: bytes) -> str:
    try:
        relative = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SecretScanError("tracked file inventory is not valid UTF-8") from exc
    if (
        not relative
        or "\\" in relative
        or relative.startswith(("/", "\\"))
        or re.match(r"^[A-Za-z]:", relative)
        or any(ord(character) < 32 or ord(character) == 127 for character in relative)
    ):
        raise SecretScanError("tracked file inventory contains an unsafe path")
    parts = PurePosixPath(relative).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise SecretScanError("tracked file inventory contains an unsafe path")
    return PurePosixPath(*parts).as_posix()


def tracked_repo_files(repo_root: Path) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=repo_root,
            shell=False,
            check=False,
            capture_output=True,
            timeout=GIT_TIMEOUT_SECONDS,
            env=_git_environment(repo_root),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SecretScanError("tracked file inventory failed") from exc
    if result.returncode != 0:
        raise SecretScanError("tracked file inventory failed")
    if (
        len(result.stdout) > MAX_GIT_OUTPUT_BYTES
        or len(result.stderr) > MAX_GIT_OUTPUT_BYTES
    ):
        raise SecretScanError("tracked file inventory exceeded output limit")
    return {
        _validate_tracked_relative_path(item)
        for item in result.stdout.split(b"\0")
        if item
    }


def _validate_tracked_file(
    repo_root: Path, relative: str
) -> tuple[Path, tuple[int, ...], int]:
    root = repo_root.absolute()
    try:
        root_state = root.lstat()
    except OSError as exc:
        raise SecretScanError("repository root could not be scanned") from exc
    if (
        stat.S_ISLNK(root_state.st_mode)
        or _is_reparse_point(root_state)
        or not stat.S_ISDIR(root_state.st_mode)
    ):
        raise SecretScanError("repository root is not a regular directory")

    parts = PurePosixPath(relative).parts
    current = root
    for index, part in enumerate(parts):
        current = current / part
        try:
            observed = current.lstat()
        except OSError as exc:
            raise SecretScanError(f"{relative} could not be scanned") from exc
        if stat.S_ISLNK(observed.st_mode) or _is_reparse_point(observed):
            raise SecretScanError(f"{relative} uses a symlink or reparse point")
        is_leaf = index == len(parts) - 1
        if not is_leaf and not stat.S_ISDIR(observed.st_mode):
            raise SecretScanError(f"{relative} has a non-directory parent")
        if is_leaf:
            if not stat.S_ISREG(observed.st_mode):
                raise SecretScanError(f"{relative} is not a regular file")
            if observed.st_nlink != 1:
                raise SecretScanError(f"{relative} is a multiply-linked file")
            if observed.st_size > MAX_TRACKED_TEXT_BYTES:
                raise SecretScanError(f"{relative} exceeds tracked text scan limit")
    return current, _path_identity(current), observed.st_size


def read_tracked_file(repo_root: Path, relative: str) -> bytes:
    path, before, _size = _validate_tracked_file(repo_root, relative)
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise SecretScanError(f"{relative} could not be scanned") from exc
    _path, after, _size = _validate_tracked_file(repo_root, relative)
    if after != before:
        raise SecretScanError(f"{relative} identity changed while scanning")
    return data


def _safe_untracked_directory(path: Path) -> bool:
    try:
        observed = path.lstat()
    except OSError:
        return False
    return (
        stat.S_ISDIR(observed.st_mode)
        and not stat.S_ISLNK(observed.st_mode)
        and not _is_reparse_point(observed)
    )


def iter_text_files(
    repo_root: Path, tracked_files: set[str] | None = None
) -> list[Path]:
    tracked = tracked_files if tracked_files is not None else tracked_repo_files(repo_root)
    files: list[Path] = []
    for relative in sorted(tracked):
        files.append(repo_root.joinpath(*PurePosixPath(relative).parts))
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
            and _safe_untracked_directory(current / name)
        )
        for name in sorted(file_names):
            path = current / name
            relative = path.relative_to(repo_root).as_posix()
            if relative in tracked or not is_text_candidate(path):
                continue
            try:
                observed = path.lstat()
            except OSError:
                continue
            if (
                stat.S_ISREG(observed.st_mode)
                and not stat.S_ISLNK(observed.st_mode)
                and not _is_reparse_point(observed)
            ):
                files.append(path)
    return files


def run(repo_root: Path) -> GateResult:
    findings: list[str] = []
    try:
        tracked = tracked_repo_files(repo_root)
    except SecretScanError as exc:
        return GateResult("secret_scan_gate", False, [str(exc)])
    for path in iter_text_files(repo_root, tracked):
        relative = path.relative_to(repo_root).as_posix()
        try:
            data = (
                read_tracked_file(repo_root, relative)
                if relative in tracked
                else path.read_bytes()
            )
        except (OSError, SecretScanError) as exc:
            if relative in tracked:
                findings.append(str(exc))
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
