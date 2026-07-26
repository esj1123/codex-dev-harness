"""Shared Windows-safe repository-relative path validation."""

from __future__ import annotations

from pathlib import PurePosixPath
import re
from typing import Any


SAFE_PATH_PATTERN = re.compile(r"^[A-Za-z0-9._/-]+$")
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def safe_repo_path(value: Any, *, max_bytes: int) -> bool:
    """Return whether value is a bounded Windows-safe POSIX repo path."""

    if (
        not isinstance(value, str)
        or not value
        or not value.isascii()
        or len(value.encode("utf-8")) > max_bytes
        or value.startswith("/")
        or value.endswith("/")
        or "\\" in value
        or "://" in value
        or SAFE_PATH_PATTERN.fullmatch(value) is None
    ):
        return False

    candidate = PurePosixPath(value)
    if candidate.is_absolute() or candidate.as_posix() != value:
        return False
    for part in candidate.parts:
        if (
            part in {"", ".", ".."}
            or len(part.encode("utf-8")) > 255
            or part.endswith((".", " "))
            or part.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES
        ):
            return False
    return True


def safe_repo_prefix(value: Any, *, max_bytes: int) -> bool:
    """Return whether value is one safe repo path followed by one slash."""

    return (
        isinstance(value, str)
        and value.endswith("/")
        and safe_repo_path(value[:-1], max_bytes=max_bytes - 1)
    )
