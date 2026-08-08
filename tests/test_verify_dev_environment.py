from __future__ import annotations

import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from scripts import verify_dev_environment as gate


def test_version_only_requires_exact_patch_version(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))
    passed = gate.inspect_environment("3.12.10", {}, version_only=True)
    failed = gate.inspect_environment("3.12.13", {}, version_only=True)

    assert passed["status"] == "PASS"
    assert passed["environment"]["pip_check"] == "NOT RUN"
    assert failed["status"] == "FAIL"
    assert failed["reason_codes"] == ["PYTHON_VERSION_MISMATCH"]


def test_lock_packages_and_pip_check_are_enforced(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))
    versions = {"pytest": "9.0.3", "pluggy": "1.6.0"}
    monkeypatch.setattr(gate.importlib.metadata, "version", versions.__getitem__)
    monkeypatch.setattr(gate, "run_pip_check", lambda: "PASS")

    result = gate.inspect_environment(
        "3.12.10", {"pytest": "9.0.3", "pluggy": "1.6.0"}, version_only=False
    )

    assert result["status"] == "PASS"
    assert result["environment"]["matched_lock_package_count"] == 2
    assert result["environment"]["pip_check"] == "PASS"


@pytest.mark.parametrize(
    ("observed", "reason"),
    [
        ({}, "LOCK_PACKAGE_MISSING"),
        ({"pytest": "8.0.0"}, "LOCK_PACKAGE_VERSION_MISMATCH"),
    ],
)
def test_missing_or_mismatched_lock_package_fails(
    monkeypatch, observed: dict[str, str], reason: str
) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))

    def version(name: str) -> str:
        if name not in observed:
            raise importlib.metadata.PackageNotFoundError(name)
        return observed[name]

    monkeypatch.setattr(gate.importlib.metadata, "version", version)
    result = gate.inspect_environment(
        "3.12.10", {"pytest": "9.0.3"}, version_only=False
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == [reason]
    assert result["environment"]["pip_check"] == "NOT RUN"


def test_lock_parser_is_exact_and_deterministic(tmp_path: Path) -> None:
    valid = tmp_path / "valid.lock"
    valid.write_text(
        "# comment\npytest==9.0.3\nPygments==2.20.0\n",
        encoding="utf-8",
    )
    invalid = tmp_path / "invalid.lock"
    invalid.write_text("pytest>=9\n", encoding="utf-8")

    assert gate.read_lock(valid) == {"pytest": "9.0.3", "pygments": "2.20.0"}
    with pytest.raises(gate.EnvironmentContractError, match="LOCK_ENTRY_INVALID"):
        gate.read_lock(invalid)


def test_json_cli_is_bounded_and_action_free(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))

    exit_code = gate.main(
        [
            "--expected-version-file",
            ".python-version",
            "--lock",
            "requirements-dev.lock",
            "--version-only",
            "--json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "PASS"
    assert payload["performed_actions"] == []
    assert len(gate.json_bytes(payload)) <= gate.MAX_OUTPUT_BYTES


def test_local_wrapper_gates_candidates_and_environment_before_pytest() -> None:
    text = Path("scripts/run_local_verify.ps1").read_text(encoding="utf-8")
    full_environment_command = (
        "scripts/verify_dev_environment.py --expected-version-file "
        ".python-version --lock requirements-dev.lock --json"
    )
    selector = text.split("function Find-Python", 1)[1].split(
        "$PythonCommand = Find-Python",
        1,
    )[0]
    environment_step = 'Invoke-PythonStep "development environment"'
    pytest_step = 'Invoke-PythonStep "pytest"'

    assert selector.count(full_environment_command) == 2
    assert selector.index('$env:PYTHON') < selector.index('$repoVenvPython')
    assert selector.index('$repoVenvPython') < selector.index('$candidates += "python"')
    assert "--version-only" not in selector
    assert (
        "No Python candidate satisfies .python-version and "
        "requirements-dev.lock"
    ) in selector
    assert environment_step in text
    assert text.index(environment_step) < text.index(pytest_step)
    assert '"--durations=50", "-rs"' in text


def release_selector_text() -> str:
    text = Path("scripts/run_release_verify.ps1").read_text(encoding="utf-8")
    body = text.split("function Find-Python", 1)[1].split(
        "function Invoke-PowerShellStep",
        1,
    )[0]
    return "function Find-Python" + body


def write_fake_python(
    path: Path,
    *,
    full_gate_passes: bool,
    argument_log: Path | None = None,
) -> None:
    lines = ["@echo off"]
    if argument_log is not None:
        lines.append(f'echo %* > "{argument_log}"')
    if full_gate_passes:
        lines.append("exit /b 0")
    else:
        lines.extend(
            [
                'if "%1"=="--version" exit /b 0',
                "exit /b 1",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.mark.skipif(
    shutil.which("powershell") is None,
    reason="PowerShell is unavailable",
)
def test_release_selector_rejects_version_only_candidate(
    tmp_path: Path,
) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    invalid = fake_bin / "invalid-python.cmd"
    selected_log = tmp_path / "selected-args.txt"
    write_fake_python(invalid, full_gate_passes=False)
    write_fake_python(
        fake_bin / "python.cmd",
        full_gate_passes=True,
        argument_log=selected_log,
    )
    harness = tmp_path / "selector.ps1"
    harness.write_text(
        "\n".join(
            [
                '$ErrorActionPreference = "Stop"',
                "$RepoRoot = Get-Location",
                (
                    "function Test-Path { "
                    "param([string]$LiteralPath) return $false }"
                ),
                release_selector_text(),
                "$selected = Find-Python",
                "Write-Output $selected",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    environment = dict(os.environ)
    environment["PYTHON"] = str(invalid)
    environment["PATH"] = str(fake_bin)
    result = subprocess.run(
        [
            shutil.which("powershell") or "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(harness),
        ],
        cwd=Path.cwd(),
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "python"
    assert selected_log.read_text(encoding="utf-8").strip() == (
        "scripts/verify_dev_environment.py --expected-version-file "
        ".python-version --lock requirements-dev.lock --json"
    )


@pytest.mark.skipif(
    shutil.which("powershell") is None,
    reason="PowerShell is unavailable",
)
def test_release_selector_stops_before_follow_on_steps_when_all_invalid(
    tmp_path: Path,
) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    invalid = fake_bin / "invalid-python.cmd"
    write_fake_python(invalid, full_gate_passes=False)
    write_fake_python(fake_bin / "python.cmd", full_gate_passes=False)
    write_fake_python(fake_bin / "py.cmd", full_gate_passes=False)
    follow_on = tmp_path / "follow-on-ran.txt"
    harness = tmp_path / "selector.ps1"
    harness.write_text(
        "\n".join(
            [
                '$ErrorActionPreference = "Stop"',
                "$RepoRoot = Get-Location",
                (
                    "function Test-Path { "
                    "param([string]$LiteralPath) return $false }"
                ),
                release_selector_text(),
                "$null = Find-Python",
                f'Set-Content -LiteralPath "{follow_on}" -Value "ran"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    environment = dict(os.environ)
    environment["PYTHON"] = str(invalid)
    environment["PATH"] = str(fake_bin)
    result = subprocess.run(
        [
            shutil.which("powershell") or "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(harness),
        ],
        cwd=Path.cwd(),
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode != 0
    assert not follow_on.exists()


def test_release_wrapper_reuses_one_fully_validated_python() -> None:
    text = Path("scripts/run_release_verify.ps1").read_text(encoding="utf-8")
    full_environment_command = (
        "scripts/verify_dev_environment.py --expected-version-file "
        ".python-version --lock requirements-dev.lock --json"
    )
    selector = text.split("function Find-Python", 1)[1].split(
        "function Invoke-PowerShellStep",
        1,
    )[0]
    select = "$PythonCommand = Find-Python"
    propagate = "$env:PYTHON = $PythonCommand"
    local_verify = (
        'Invoke-PowerShellStep "local verification wrapper" '
        '(Join-Path $RepoRoot "scripts/run_local_verify.ps1")'
    )
    generator = 'Invoke-PythonStep "release manifest generation"'

    assert selector.count(full_environment_command) == 2
    assert selector.index('$env:PYTHON') < selector.index('$repoVenvPython')
    assert selector.index('$repoVenvPython') < selector.index('$candidates += "python"')
    assert "--version *> $null" not in selector
    assert text.count(select) == 1
    assert text.index(select) < text.index(propagate) < text.index(local_verify)
    assert text.index(local_verify) < text.index(generator)
