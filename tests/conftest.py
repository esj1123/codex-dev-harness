from __future__ import annotations

import os
from pathlib import Path
import re
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


OPTIONAL_AGENT_QUALITY_TEST_FILES = {
    "test_agent_quality_aggregation.py",
    "test_agent_quality_capture.py",
    "test_agent_quality_cli.py",
    "test_agent_quality_contracts.py",
    "test_agent_quality_semantic_failure.py",
    "test_agent_quality_trial_validation.py",
    "test_agent_role_profiles.py",
}


def _optional_marker_for_test(path: Path) -> str | None:
    name = path.name
    if name in OPTIONAL_AGENT_QUALITY_TEST_FILES:
        return "optional_agent_quality"
    if name.startswith(("test_hermes_", "test_mcp_")):
        return "optional_hermes_mcp"
    if name == "test_local_rag_retriever.py":
        return "optional_local_rag"
    return None

_AMBIENT_GIT_KEYS = (
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
)

_SKIPPED_REPORTS: list[pytest.TestReport] = []


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


def _apply_git_environment(
    monkeypatch: pytest.MonkeyPatch, disabled_hooks: Path
) -> None:
    for name in _AMBIENT_GIT_KEYS:
        monkeypatch.delenv(name, raising=False)
    for name in list(os.environ):
        if re.fullmatch(r"GIT_CONFIG_(?:KEY|VALUE)_[0-9]+", name):
            monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("GIT_CONFIG_COUNT", raising=False)

    disabled_hooks.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_TERMINAL_PROMPT", "0")
    monkeypatch.setenv("GCM_INTERACTIVE", "Never")
    monkeypatch.setenv("GIT_NO_REPLACE_OBJECTS", "1")
    monkeypatch.setenv("GIT_OPTIONAL_LOCKS", "0")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "6")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "commit.gpgSign")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "false")
    monkeypatch.setenv("GIT_CONFIG_KEY_1", "tag.gpgSign")
    monkeypatch.setenv("GIT_CONFIG_VALUE_1", "false")
    monkeypatch.setenv("GIT_CONFIG_KEY_2", "core.hooksPath")
    monkeypatch.setenv("GIT_CONFIG_VALUE_2", str(Path(disabled_hooks)))
    monkeypatch.setenv("GIT_CONFIG_VALUE_3", "false")
    monkeypatch.setenv("GIT_CONFIG_KEY_3", "core.fsmonitor")
    monkeypatch.setenv("GIT_CONFIG_KEY_4", "submodule.recurse")
    monkeypatch.setenv("GIT_CONFIG_VALUE_4", "false")
    monkeypatch.setenv("GIT_CONFIG_KEY_5", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_5", str(Path.cwd().resolve()))


@pytest.fixture(scope="session", autouse=True)
def isolate_git_process_environment(tmp_path_factory: pytest.TempPathFactory):
    monkeypatch = pytest.MonkeyPatch()
    disabled_hooks = tmp_path_factory.getbasetemp() / "disabled-git-hooks"
    _apply_git_environment(monkeypatch, disabled_hooks)
    yield
    monkeypatch.undo()



def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        marker_name = _optional_marker_for_test(Path(str(item.path)))
        if marker_name is not None:
            item.add_marker(getattr(pytest.mark, marker_name))


def pytest_sessionstart(session: pytest.Session) -> None:
    _SKIPPED_REPORTS.clear()


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.skipped:
        _SKIPPED_REPORTS.append(report)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    findings = _unexpected_skips(list(_SKIPPED_REPORTS))
    if not findings:
        return
    if reporter is not None:
        reporter.write_sep("=", "unexpected platform skips")
        for finding in findings:
            reporter.write_line(finding)
    session.exitstatus = pytest.ExitCode.TESTS_FAILED
