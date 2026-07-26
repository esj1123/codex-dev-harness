from __future__ import annotations

import pytest

from scripts import repo_path_policy
from scripts.agent_quality_lib import contracts


@pytest.mark.parametrize(
    "value",
    [
        "AGENTS.md",
        ".github/workflows/local-verify.yml",
        "docs/agent_quality-v1.json",
    ],
)
def test_windows_safe_repo_paths_are_accepted(value: str) -> None:
    assert repo_path_policy.safe_repo_path(value, max_bytes=512)
    assert contracts.safe_repo_path(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "/absolute",
        "C:/absolute",
        "docs\\file.json",
        "docs/../file.json",
        "docs/file?.json",
        "docs/file*.json",
        "docs/file<name>.json",
        "docs/file|name.json",
        "docs/name:stream",
        "docs/file.",
        "CON",
        "docs/aux.txt",
        "docs/" + ("a" * 256),
    ],
)
def test_windows_unsafe_repo_paths_are_rejected(value: str) -> None:
    assert not repo_path_policy.safe_repo_path(value, max_bytes=512)
    assert not contracts.safe_repo_path(value)


def test_safe_repo_prefix_requires_one_trailing_slash() -> None:
    assert repo_path_policy.safe_repo_prefix("docs/agentic/", max_bytes=512)
    assert not repo_path_policy.safe_repo_prefix("docs/agentic", max_bytes=512)
    assert not repo_path_policy.safe_repo_prefix("docs/CON/", max_bytes=512)
