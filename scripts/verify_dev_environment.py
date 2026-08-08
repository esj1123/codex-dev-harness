"""Verify the exact local Python and development dependency contract."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER_ID = "verify_dev_environment"
SCHEMA_VERSION = "1"
MAX_INPUT_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 8 * 1024
MAX_PROCESS_BYTES = 1024 * 1024
LOCK_LINE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]{0,127})=="
    r"(?P<version>[A-Za-z0-9][A-Za-z0-9.!+_-]{0,127})$"
)
LOCK_HASH = re.compile(r"^--hash=sha256:(?P<digest>[0-9a-f]{64})$")
VERSION_LINE = re.compile(r"^\d+\.\d+\.\d+$")


class EnvironmentContractError(ValueError):
    def __init__(self, reason_codes: list[str] | tuple[str, ...]):
        self.reason_codes = sorted(set(reason_codes))
        super().__init__(", ".join(self.reason_codes))


@dataclass(frozen=True)
class LockedRequirement:
    name: str
    version: str
    hashes: tuple[str, ...]

    @property
    def requirement(self) -> str:
        return f"{self.name}=={self.version}"


def _resolve_repo_file(value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        raise EnvironmentContractError(("INPUT_PATH_INVALID",))
    try:
        resolved = (REPO_ROOT / candidate).resolve(strict=True)
        resolved.relative_to(REPO_ROOT.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise EnvironmentContractError(("INPUT_PATH_INVALID",)) from exc
    if resolved.is_symlink() or not resolved.is_file():
        raise EnvironmentContractError(("INPUT_NOT_REGULAR_FILE",))
    if resolved.stat().st_size > MAX_INPUT_BYTES:
        raise EnvironmentContractError(("INPUT_TOO_LARGE",))
    return resolved


def read_expected_version(path: Path) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError) as exc:
        raise EnvironmentContractError(("VERSION_FILE_INVALID",)) from exc
    if VERSION_LINE.fullmatch(value) is None:
        raise EnvironmentContractError(("VERSION_FILE_INVALID",))
    return value


def parse_lock(path: Path) -> dict[str, LockedRequirement]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise EnvironmentContractError(("LOCK_FILE_INVALID",)) from exc
    logical_lines: list[str] = []
    current = ""
    for raw in lines:
        line = raw.strip()
        if not line or (line.startswith("#") and not current):
            continue
        if line.endswith("\\"):
            current += line[:-1].rstrip() + " "
            continue
        logical_lines.append(current + line)
        current = ""
    if current:
        raise EnvironmentContractError(("LOCK_ENTRY_INVALID",))

    packages: dict[str, LockedRequirement] = {}
    for line in logical_lines:
        tokens = line.split()
        match = LOCK_LINE.fullmatch(tokens[0]) if tokens else None
        if match is None:
            raise EnvironmentContractError(("LOCK_ENTRY_INVALID",))
        hashes: list[str] = []
        for token in tokens[1:]:
            hash_match = LOCK_HASH.fullmatch(token)
            if hash_match is None:
                raise EnvironmentContractError(("LOCK_ENTRY_INVALID",))
            digest = hash_match.group("digest")
            if digest in hashes:
                raise EnvironmentContractError(("LOCK_HASH_DUPLICATE",))
            hashes.append(digest)
        if not hashes:
            raise EnvironmentContractError(("LOCK_HASH_MISSING",))
        normalized = re.sub(r"[-_.]+", "-", match.group("name")).lower()
        if normalized in packages:
            raise EnvironmentContractError(("LOCK_PACKAGE_DUPLICATE",))
        packages[normalized] = LockedRequirement(
            name=match.group("name"),
            version=match.group("version"),
            hashes=tuple(hashes),
        )
    if not packages:
        raise EnvironmentContractError(("LOCK_EMPTY",))
    return packages


def read_lock(path: Path) -> dict[str, str]:
    return {name: item.version for name, item in parse_lock(path).items()}


def run_pip_check() -> str:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            shell=False,
            check=False,
            capture_output=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "ENVIRONMENT BLOCKED"
    if len(result.stdout) > MAX_PROCESS_BYTES or len(result.stderr) > MAX_PROCESS_BYTES:
        return "FAIL"
    return "PASS" if result.returncode == 0 else "FAIL"


def inspect_environment(
    expected_version: str,
    packages: dict[str, str],
    *,
    version_only: bool,
) -> dict[str, Any]:
    observed_version = ".".join(str(item) for item in sys.version_info[:3])
    reason_codes: list[str] = []
    if observed_version != expected_version:
        reason_codes.append("PYTHON_VERSION_MISMATCH")

    matched = 0
    pip_status = "NOT RUN"
    if not version_only and not reason_codes:
        for name, expected in sorted(packages.items()):
            try:
                observed = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                reason_codes.append("LOCK_PACKAGE_MISSING")
                continue
            if observed != expected:
                reason_codes.append("LOCK_PACKAGE_VERSION_MISMATCH")
            else:
                matched += 1
        if not reason_codes:
            pip_status = run_pip_check()
            if pip_status == "FAIL":
                reason_codes.append("PIP_CHECK_FAILED")
            elif pip_status == "ENVIRONMENT BLOCKED":
                reason_codes.append("PIP_CHECK_ENVIRONMENT_BLOCKED")

    status = (
        "PASS"
        if not reason_codes
        else (
            "ENVIRONMENT BLOCKED"
            if "PIP_CHECK_ENVIRONMENT_BLOCKED" in reason_codes
            else "FAIL"
        )
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "checker_id": CHECKER_ID,
        "status": status,
        "reason_codes": sorted(set(reason_codes)),
        "environment": {
            "expected_python_version": expected_version,
            "observed_python_version": observed_version,
            "version_only": version_only,
            "lock_package_count": 0 if version_only else len(packages),
            "matched_lock_package_count": 0 if version_only else matched,
            "pip_check": pip_status,
        },
        "performed_actions": [],
    }


def json_bytes(result: dict[str, Any]) -> bytes:
    data = (
        json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")
    if len(data) > MAX_OUTPUT_BYTES:
        raise ValueError("OUTPUT_TOO_LARGE")
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-version-file", required=True)
    parser.add_argument("--lock", required=True)
    parser.add_argument("--version-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        expected = read_expected_version(_resolve_repo_file(args.expected_version_file))
        packages = (
            {}
            if args.version_only
            else read_lock(_resolve_repo_file(args.lock))
        )
        result = inspect_environment(
            expected, packages, version_only=args.version_only
        )
    except EnvironmentContractError as exc:
        result = {
            "schema_version": SCHEMA_VERSION,
            "checker_id": CHECKER_ID,
            "status": "FAIL",
            "reason_codes": exc.reason_codes,
            "environment": {
                "expected_python_version": "UNKNOWN",
                "observed_python_version": ".".join(
                    str(item) for item in sys.version_info[:3]
                ),
                "version_only": False,
                "lock_package_count": 0,
                "matched_lock_package_count": 0,
                "pip_check": "NOT RUN",
            },
            "performed_actions": [],
        }
    data = json_bytes(result)
    if "--json" in (argv or sys.argv[1:]):
        sys.stdout.buffer.write(data)
    else:
        print(
            f"{result['status']}: python="
            f"{result['environment']['observed_python_version']} "
            f"lock={result['environment']['matched_lock_package_count']}/"
            f"{result['environment']['lock_package_count']} "
            f"pip={result['environment']['pip_check']}"
        )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
