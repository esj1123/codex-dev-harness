from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest

from scripts import verify_dev_environment as gate


def set_installed_distributions(
    monkeypatch: pytest.MonkeyPatch, packages: list[tuple[object, object]]
) -> None:
    distributions = [
        SimpleNamespace(metadata={"Name": name}, version=version)
        for name, version in packages
    ]
    monkeypatch.setattr(
        gate.importlib.metadata, "distributions", lambda: iter(distributions)
    )


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
    set_installed_distributions(
        monkeypatch,
        [("pytest", "9.0.3"), ("pluggy", "1.6.0"), ("pip", "25.0.1")],
    )
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

    installed = [(name, version) for name, version in observed.items()]
    set_installed_distributions(monkeypatch, installed + [("pip", "25.0.1")])
    result = gate.inspect_environment(
        "3.12.10", {"pytest": "9.0.3"}, version_only=False
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == [reason]
    assert result["environment"]["pip_check"] == "NOT RUN"


def test_unexpected_distribution_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))
    set_installed_distributions(
        monkeypatch,
        [("pytest", "9.0.3"), ("pip", "25.0.1"), ("wheel", "0.46.0")],
    )

    result = gate.inspect_environment(
        "3.12.10", {"pytest": "9.0.3"}, version_only=False
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["LOCK_PACKAGE_UNEXPECTED"]
    assert result["environment"]["pip_check"] == "NOT RUN"


def test_distribution_names_are_normalized_before_membership_check(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))
    set_installed_distributions(
        monkeypatch, [("Py_Test", "9.0.3"), ("PIP", "25.0.1")]
    )
    monkeypatch.setattr(gate, "run_pip_check", lambda: "PASS")

    result = gate.inspect_environment(
        "3.12.10", {"py-test": "9.0.3"}, version_only=False
    )

    assert result["status"] == "PASS"


def test_duplicate_normalized_distribution_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))
    set_installed_distributions(
        monkeypatch,
        [("Py_Test", "9.0.3"), ("py-test", "9.0.3"), ("pip", "25.0.1")],
    )

    result = gate.inspect_environment(
        "3.12.10", {"py-test": "9.0.3"}, version_only=False
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["LOCK_PACKAGE_DUPLICATE"]


def test_malformed_distribution_metadata_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))
    set_installed_distributions(
        monkeypatch,
        [(None, "9.0.3"), ("pytest", "9.0.3"), ("pip", "25.0.1")],
    )

    result = gate.inspect_environment(
        "3.12.10", {"pytest": "9.0.3"}, version_only=False
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["DISTRIBUTION_METADATA_INVALID"]


def test_missing_bootstrap_pip_fails_closed(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))
    set_installed_distributions(monkeypatch, [("pytest", "9.0.3")])

    result = gate.inspect_environment(
        "3.12.10", {"pytest": "9.0.3"}, version_only=False
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["BOOTSTRAP_PACKAGE_MISSING"]


def test_lock_parser_is_exact_and_deterministic(tmp_path: Path) -> None:
    valid = tmp_path / "valid.lock"
    valid.write_text(
        "# comment\n"
        "pytest==9.0.3 \\\n"
        f"    --hash=sha256:{'a' * 64}\n"
        "Pygments==2.20.0 \\\n"
        f"    --hash=sha256:{'b' * 64}\n",
        encoding="utf-8",
    )
    invalid = tmp_path / "invalid.lock"
    invalid.write_text("pytest>=9\n", encoding="utf-8")

    assert gate.read_lock(valid) == {"pytest": "9.0.3", "pygments": "2.20.0"}
    parsed = gate.parse_lock(valid)
    assert parsed["pytest"].requirement == "pytest==9.0.3"
    assert parsed["pytest"].hashes == ("a" * 64,)
    with pytest.raises(gate.EnvironmentContractError, match="LOCK_ENTRY_INVALID"):
        gate.read_lock(invalid)


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        ("pytest==9.0.3\n", "LOCK_HASH_MISSING"),
        ("pytest>=9 --hash=sha256:" + "a" * 64 + "\n", "LOCK_ENTRY_INVALID"),
        ("pytest==9.0.3 --hash=sha256:not-a-hash\n", "LOCK_ENTRY_INVALID"),
        (
            "pytest==9.0.3 --hash=sha256:"
            + "a" * 64
            + " --index-url=https://example.invalid\n",
            "LOCK_ENTRY_INVALID",
        ),
        (
            "pytest==9.0.3 --hash=sha256:"
            + "a" * 64
            + "\npytest==9.0.3 --hash=sha256:"
            + "b" * 64
            + "\n",
            "LOCK_PACKAGE_DUPLICATE",
        ),
        (
            "pytest==9.0.3 --hash=sha256:"
            + "a" * 64
            + " --hash=sha256:"
            + "a" * 64
            + "\n",
            "LOCK_HASH_DUPLICATE",
        ),
    ],
)
def test_lock_parser_rejects_unsafe_entries(
    tmp_path: Path, content: str, reason: str
) -> None:
    lock = tmp_path / "unsafe.lock"
    lock.write_text(content, encoding="utf-8")

    with pytest.raises(gate.EnvironmentContractError, match=reason):
        gate.parse_lock(lock)


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


def test_runtime_identity_is_opt_in_and_path_free(monkeypatch) -> None:
    monkeypatch.setattr(gate.sys, "version_info", (3, 12, 10))
    set_installed_distributions(
        monkeypatch, [("pytest", "9.0.3"), ("pip", "25.0.1")]
    )
    monkeypatch.setattr(gate, "run_pip_check", lambda: "PASS")
    monkeypatch.setattr(
        gate,
        "runtime_identity",
        lambda: {
            "executable_sha256": "a" * 64,
            "pytest_version": "9.0.3",
        },
    )

    normal = gate.inspect_environment(
        "3.12.10", {"pytest": "9.0.3"}, version_only=False
    )
    diagnostic = gate.inspect_environment(
        "3.12.10",
        {"pytest": "9.0.3"},
        version_only=False,
        include_runtime_identity=True,
    )

    assert "runtime_identity" not in normal
    assert diagnostic["runtime_identity"] == {
        "executable_sha256": "a" * 64,
        "pytest_version": "9.0.3",
    }
    assert all("path" not in key for key in diagnostic["runtime_identity"])


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


def test_local_wrapper_clears_ambient_test_controls_before_python_selection() -> None:
    text = Path("scripts/run_local_verify.ps1").read_text(encoding="utf-8")
    clear_call = "\nSet-HermeticVerificationEnvironment\n"
    select_call = "\n$PythonCommand = Find-Python\n"

    for name in [
        "PYTEST_ADDOPTS",
        "PYTEST_PLUGINS",
        "PYTHONPATH",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
    ]:
        assert name in text
    assert text.index(clear_call) < text.index(select_call)


def test_git_test_environment_is_isolated() -> None:
    assert os.environ["GIT_CONFIG_NOSYSTEM"] == "1"
    assert os.environ["GIT_CONFIG_GLOBAL"] == os.devnull
    assert os.environ["GIT_TERMINAL_PROMPT"] == "0"
    assert os.environ["GCM_INTERACTIVE"] == "Never"
    assert os.environ["GIT_CONFIG_KEY_0"] == "commit.gpgSign"
    assert os.environ["GIT_CONFIG_VALUE_0"] == "false"
    assert os.environ["GIT_CONFIG_KEY_2"] == "core.hooksPath"
    assert os.environ["GIT_CONFIG_KEY_3"] == "core.fsmonitor"
    assert os.environ["GIT_CONFIG_VALUE_3"] == "false"
    assert os.environ["GIT_CONFIG_KEY_4"] == "submodule.recurse"
    assert os.environ["GIT_CONFIG_VALUE_4"] == "false"
    assert os.environ["GIT_CONFIG_KEY_5"] == "safe.directory"
    assert os.environ["GIT_CONFIG_VALUE_5"] == str(Path.cwd().resolve())


def test_git_test_environment_rejects_config_parameters_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    policy = sys.modules["conftest"]
    monkeypatch.setenv("GIT_CONFIG_PARAMETERS", "'commit.gpgSign=true'")

    policy._apply_git_environment(monkeypatch, tmp_path / "disabled-hooks")

    assert "GIT_CONFIG_PARAMETERS" not in os.environ
    result = subprocess.run(
        ["git", "config", "--get", "commit.gpgSign"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "false"


def test_unreviewed_skip_is_rejected_by_session_policy() -> None:
    policy = sys.modules["conftest"]
    report = SimpleNamespace(
        nodeid="tests/test_synthetic.py::test_unreviewed_skip",
        longrepr=("synthetic.py", 1, "Skipped: synthetic reason"),
    )

    assert policy._unexpected_skips([report]) == [
        "tests/test_synthetic.py::test_unreviewed_skip: "
        "expected=None observed='synthetic reason'"
    ]


def test_unreviewed_skip_fails_without_terminal_reporter(monkeypatch) -> None:
    policy = sys.modules["conftest"]
    report = SimpleNamespace(
        nodeid="tests/test_synthetic.py::test_unreviewed_skip",
        longrepr=("synthetic.py", 1, "Skipped: synthetic reason"),
        skipped=True,
    )
    session = SimpleNamespace(
        config=SimpleNamespace(
            pluginmanager=SimpleNamespace(get_plugin=lambda _name: None)
        ),
        exitstatus=pytest.ExitCode.OK,
    )
    monkeypatch.setattr(policy, "_SKIPPED_REPORTS", [report])

    policy.pytest_sessionfinish(session, int(pytest.ExitCode.OK))

    assert session.exitstatus == pytest.ExitCode.TESTS_FAILED


def test_unreviewed_skip_fails_in_subprocess_without_terminal_reporter(
    tmp_path: Path,
) -> None:
    synthetic_test = tmp_path / "test_unreviewed_skip.py"
    synthetic_test.write_text(
        "import pytest\n\n"
        "def test_unreviewed_skip():\n"
        "    pytest.skip('synthetic unexpected skip')\n",
        encoding="utf-8",
    )
    environment = dict(os.environ)
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:terminal",
            "-p",
            "conftest",
            str(synthetic_test),
        ],
        cwd=Path.cwd(),
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == int(pytest.ExitCode.TESTS_FAILED), result.stderr


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


@pytest.mark.skipif(
    shutil.which("powershell") is None,
    reason="PowerShell is unavailable",
)
def test_release_selector_uses_python_312_launcher(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    argument_log = tmp_path / "launcher-args.txt"
    launcher = fake_bin / "py.cmd"
    launcher.write_text(
        "\n".join(
            [
                "@echo off",
                f'echo %* > "{argument_log}"',
                'if "%1"=="-3.12" exit /b 0',
                "exit /b 1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    harness = tmp_path / "selector.ps1"
    harness.write_text(
        "\n".join(
            [
                '$ErrorActionPreference = "Stop"',
                "$RepoRoot = Get-Location",
                "function Test-Path { param([string]$LiteralPath) return $false }",
                release_selector_text(),
                "$selected = Find-Python",
                "Write-Output $selected",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    environment = dict(os.environ)
    environment.pop("PYTHON", None)
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
    assert result.stdout.strip() == "py"
    assert argument_log.read_text(encoding="utf-8").strip().startswith(
        "-3.12 scripts/verify_dev_environment.py"
    )


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


def test_python_launcher_fallback_is_minor_version_scoped() -> None:
    for script in [
        Path("scripts/run_local_verify.ps1"),
        Path("scripts/run_release_verify.ps1"),
    ]:
        text = script.read_text(encoding="utf-8")
        assert text.count("& py -3.12") == 2
        assert "& py -3 " not in text


def test_local_wrapper_environment_only_json_is_action_free_and_path_safe(
    tmp_path: Path,
) -> None:
    environment = os.environ.copy()
    environment["PYTHON"] = sys.executable
    command = [
        shutil.which("powershell") or "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "scripts/run_local_verify.ps1",
        "-EnvironmentOnly",
        "-Json",
        "-PytestBaseTempRoot",
        str(tmp_path),
    ]

    result = subprocess.run(
        command,
        cwd=Path.cwd(),
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert payload["status"] == "PASS"
    assert payload["candidate_class"] == "explicit_env"
    assert payload["interpreter_id"].startswith("py3.12.10-pytest9.0.3-")
    assert len(payload["interpreter_id"].encode("utf-8")) <= 64
    assert len(payload["executable_sha256"]) == 64
    assert payload["pytest_version"] == "9.0.3"
    assert payload["lock_package_count"] == 6
    assert payload["matched_lock_package_count"] == 6
    assert payload["pip_check"] == "PASS"
    assert payload["basetemp_readiness"] == "READY"
    assert payload["reason_codes"] == []
    assert payload["performed_actions"] == []
    assert str(Path.cwd()) not in result.stdout
    assert str(tmp_path) not in result.stdout
    assert "==> pytest" not in result.stdout
    assert "standalone eval" not in result.stdout
    assert list(tmp_path.iterdir()) == []


def test_environment_only_json_rejects_unsafe_basetemp_without_reflection() -> None:
    environment = os.environ.copy()
    environment["PYTHON"] = sys.executable
    unsafe_value = "private-relative-root"
    result = subprocess.run(
        [
            shutil.which("powershell") or "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "scripts/run_local_verify.ps1",
            "-EnvironmentOnly",
            "-Json",
            "-PytestBaseTempRoot",
            unsafe_value,
        ],
        cwd=Path.cwd(),
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert result.stderr == ""
    assert payload["status"] == "FAIL"
    assert payload["basetemp_readiness"] == "BLOCKED"
    assert payload["reason_codes"] == ["PYTEST_BASETEMP_ROOT_INVALID"]
    assert payload["performed_actions"] == []
    assert unsafe_value not in result.stdout
