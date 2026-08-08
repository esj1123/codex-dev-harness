from __future__ import annotations

import os
from pathlib import Path
import sys

import pytest


WINDOWS_ALLOWED_SKIPS = {
    "tests/test_render_template.py::test_render_force_preserves_mode_under_restrictive_umask": "POSIX mode regression",
    "tests/test_render_template.py::test_render_rejects_output_symlink_and_preserves_outside_file[False]": "file symlink creation is unavailable",
    "tests/test_render_template.py::test_render_rejects_output_symlink_and_preserves_outside_file[True]": "file symlink creation is unavailable",
    "tests/test_render_template.py::test_render_rejects_dangling_output_symlink[False]": "file symlink creation is unavailable",
    "tests/test_render_template.py::test_render_rejects_dangling_output_symlink[True]": "file symlink creation is unavailable",
    "tests/test_render_template.py::test_render_rejects_symlinked_target_parent_for_write_and_preview[False]": "directory symlink creation is unavailable",
    "tests/test_render_template.py::test_render_rejects_symlinked_target_parent_for_write_and_preview[True]": "directory symlink creation is unavailable",
    "tests/test_render_template.py::test_render_rejects_symlinked_template_source_before_writing": "file symlink creation is unavailable",
    "tests/test_render_template.py::test_render_rejects_profile_directory_symlink_outside_repo": "directory symlink creation is unavailable",
    "tests/test_render_template.py::test_render_rejects_base_source_directory_symlink_outside_repo": "directory symlink creation is unavailable",
}

POSIX_ALLOWED_SKIPS = {
    "tests/test_render_template.py::test_render_rejects_junction_target_parent": "Windows junction regression",
    "tests/test_render_template.py::test_render_rejects_profile_source_junction": "Windows junction regression",
}

_AMBIENT_GIT_KEYS = (
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_CONFIG",
    "GIT_CONFIG_SYSTEM",
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_WORK_TREE",
)


def _skip_reason(report: pytest.TestReport) -> str:
    longrepr = report.longrepr
    if isinstance(longrepr, tuple) and len(longrepr) >= 3:
        reason = str(longrepr[2])
    else:
        reason = str(longrepr)
    prefix = "Skipped: "
    return reason[len(prefix) :] if reason.startswith(prefix) else reason


def _unexpected_skips(reports: list[pytest.TestReport]) -> list[str]:
    allowed = WINDOWS_ALLOWED_SKIPS if sys.platform == "win32" else POSIX_ALLOWED_SKIPS
    findings: list[str] = []
    for report in reports:
        observed_reason = _skip_reason(report)
        expected_reason = allowed.get(report.nodeid)
        if expected_reason != observed_reason:
            findings.append(
                f"{report.nodeid}: expected={expected_reason!r} observed={observed_reason!r}"
            )
    return findings


@pytest.fixture(scope="session", autouse=True)
def isolate_git_process_environment(tmp_path_factory: pytest.TempPathFactory):
    monkeypatch = pytest.MonkeyPatch()
    for name in _AMBIENT_GIT_KEYS:
        monkeypatch.delenv(name, raising=False)

    disabled_hooks = tmp_path_factory.getbasetemp() / "disabled-git-hooks"
    disabled_hooks.mkdir(exist_ok=True)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_TERMINAL_PROMPT", "0")
    monkeypatch.setenv("GCM_INTERACTIVE", "Never")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "4")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "commit.gpgSign")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "false")
    monkeypatch.setenv("GIT_CONFIG_KEY_1", "tag.gpgSign")
    monkeypatch.setenv("GIT_CONFIG_VALUE_1", "false")
    monkeypatch.setenv("GIT_CONFIG_KEY_2", "core.hooksPath")
    monkeypatch.setenv("GIT_CONFIG_VALUE_2", str(Path(disabled_hooks)))
    monkeypatch.setenv("GIT_CONFIG_KEY_3", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_3", str(Path.cwd().resolve()))
    yield
    monkeypatch.undo()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    reports = [] if reporter is None else list(reporter.stats.get("skipped", []))
    findings = _unexpected_skips(reports)
    if not findings:
        return
    if reporter is not None:
        reporter.write_sep("=", "unexpected platform skips")
        for finding in findings:
            reporter.write_line(finding)
    session.exitstatus = pytest.ExitCode.TESTS_FAILED
