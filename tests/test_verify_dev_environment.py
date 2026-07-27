from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path

import pytest

from scripts import verify_dev_environment as gate


def test_version_only_requires_exact_patch_version(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 13))
    passed = gate.inspect_environment("3.12.13", {}, version_only=True)
    failed = gate.inspect_environment("3.12.10", {}, version_only=True)

    assert passed["status"] == "PASS"
    assert passed["environment"]["pip_check"] == "NOT RUN"
    assert failed["status"] == "FAIL"
    assert failed["reason_codes"] == ["PYTHON_VERSION_MISMATCH"]


def test_lock_packages_and_pip_check_are_enforced(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 13))
    versions = {"pytest": "9.0.3", "pluggy": "1.6.0"}
    monkeypatch.setattr(gate.importlib.metadata, "version", versions.__getitem__)
    monkeypatch.setattr(gate, "run_pip_check", lambda: "PASS")

    result = gate.inspect_environment(
        "3.12.13", {"pytest": "9.0.3", "pluggy": "1.6.0"}, version_only=False
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
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 13))

    def version(name: str) -> str:
        if name not in observed:
            raise importlib.metadata.PackageNotFoundError(name)
        return observed[name]

    monkeypatch.setattr(gate.importlib.metadata, "version", version)
    result = gate.inspect_environment(
        "3.12.13", {"pytest": "9.0.3"}, version_only=False
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
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 13))

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
    version_command = (
        "scripts/verify_dev_environment.py --expected-version-file "
        ".python-version --lock requirements-dev.lock --version-only --json"
    )
    environment_step = 'Invoke-PythonStep "development environment"'
    pytest_step = 'Invoke-PythonStep "pytest"'

    assert text.count(version_command) == 2
    assert environment_step in text
    assert text.index(environment_step) < text.index(pytest_step)
