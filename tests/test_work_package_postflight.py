from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from scripts import work_package_conflict_check as preflight
from scripts import work_package_postflight as postflight


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "docs" / "PARALLEL_WORK_PACKAGE_SYNTHETIC_FIXTURE.json"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def write_text(repo: Path, relative: str, content: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def init_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Synthetic Test")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    write_text(repo, ".gitignore", "/local/\n")
    write_text(repo, "seed.txt", "seed\n")
    git(repo, "add", ".gitignore", "seed.txt")
    git(repo, "commit", "-m", "base")
    return repo, git(repo, "rev-parse", "HEAD")


def package(base_sha: str, *, task_id: str = "feature-a", lane: str = "feature") -> dict[str, object]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    payload.update(
        {
            "task_id": task_id,
            "base_sha": base_sha,
            "lane": lane,
            "read_set": ["seed.txt"],
            "write_set": ["feature.txt"],
            "generated_outputs": [],
            "verification_tier": "V2" if lane == "integration" else "V1",
        }
    )
    return payload


def write_package(repo: Path, payload: dict[str, object], name: str = "feature.json") -> str:
    relative = f"local/work-packages/{name}"
    write_text(repo, relative, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return relative


def commit_file(repo: Path, relative: str, content: str, message: str = "feature") -> None:
    write_text(repo, relative, content)
    git(repo, "add", relative)
    git(repo, "commit", "-m", message)


def inspect(
    repo: Path,
    package_path: str,
    *,
    task_id: str = "feature-a",
    verification_status: str = "PASS",
) -> dict[str, object]:
    return postflight.inspect_postflight(
        [package_path],
        task_id=task_id,
        verification_status=verification_status,
        repo_root=repo,
    )


def test_clean_single_commit_passes_and_matches_preflight_digest(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(repo, package_path)
    expected = preflight.inspect_payloads([payload])

    assert result["status"] == "PASS"
    assert result["plan_digest"] == expected["plan_digest"]
    assert result["head_sha"] == git(repo, "rev-parse", "HEAD")
    assert result["actual_surface"] == {
        "changed_paths": ["feature.txt"],
        "untracked_paths": [],
        "commit_count": 1,
        "rename_count": 0,
        "delete_count": 0,
    }
    assert result["central_authority_changed"] is False
    assert result["performed_actions"] == []


def test_changed_path_outside_write_set_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "outside.txt", "outside\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "WRITE_SET_EXCEEDED" in result["reason_codes"]


def test_declared_generated_output_may_remain_untracked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    payload["write_set"] = ["feature.txt", "generated/result.json"]
    payload["generated_outputs"] = ["generated/result.json"]
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n")
    write_text(repo, "generated/result.json", "{}\n")

    result = inspect(repo, package_path)

    assert result["status"] == "PASS"
    assert result["actual_surface"]["untracked_paths"] == ["generated/result.json"]


def test_undeclared_untracked_output_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "feature\n")
    write_text(repo, "unexpected.txt", "unexpected\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "GENERATED_OUTPUT_SET_EXCEEDED" in result["reason_codes"]


def test_tracked_dirty_state_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "feature\n")
    write_text(repo, "feature.txt", "dirty\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "TRACKED_WORKTREE_DIRTY" in result["reason_codes"]


@pytest.mark.parametrize(
    ("operation", "reason_code"),
    [
        ("rename", "RENAME_NOT_ALLOWED"),
        ("delete", "DELETE_NOT_ALLOWED"),
    ],
)
def test_rename_and_delete_are_blocked(tmp_path: Path, operation: str, reason_code: str) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    payload["write_set"] = ["seed.txt", "renamed.txt"]
    package_path = write_package(repo, payload)
    if operation == "rename":
        git(repo, "mv", "seed.txt", "renamed.txt")
    else:
        git(repo, "rm", "seed.txt")
    git(repo, "commit", "-m", operation)

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert reason_code in result["reason_codes"]


def test_feature_lane_requires_exactly_one_commit(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    payload["write_set"] = ["feature.txt", "second.txt"]
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n", "first")
    commit_file(repo, "second.txt", "second\n", "second")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "LANE_COMMIT_COUNT_INVALID" in result["reason_codes"]


def test_missing_lane_commit_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "LANE_COMMIT_COUNT_INVALID" in result["reason_codes"]


def test_base_that_is_not_an_ancestor_is_blocked(tmp_path: Path) -> None:
    repo, _ = init_repo(tmp_path)
    package_path = write_package(repo, package("a" * 40))
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["BASE_NOT_ANCESTOR"]


def test_feature_lane_cannot_change_integration_only_path(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "STATUS.md", "status\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "INTEGRATION_ONLY_PATH" in result["reason_codes"]


@pytest.mark.parametrize(
    ("verification_status", "expected_status", "reason_code"),
    [
        ("FAIL", "FAIL", "VERIFICATION_FAILED"),
        ("NOT_RUN", "BLOCKED", "VERIFICATION_NOT_RUN"),
        ("ENVIRONMENT_BLOCKED", "ENVIRONMENT BLOCKED", "VERIFICATION_ENVIRONMENT_BLOCKED"),
    ],
)
def test_verification_status_controls_outcome(
    tmp_path: Path,
    verification_status: str,
    expected_status: str,
    reason_code: str,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(repo, package_path, verification_status=verification_status)

    assert result["status"] == expected_status
    assert reason_code in result["reason_codes"]


def test_diff_check_failure_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "trailing whitespace \n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "DIFF_CHECK_FAILED" in result["reason_codes"]


def test_not_a_repository_is_environment_blocked(tmp_path: Path) -> None:
    payload = package("a" * 40)
    package_path = write_package(tmp_path, payload)

    result = inspect(tmp_path, package_path)

    assert result["status"] == "ENVIRONMENT BLOCKED"
    assert result["reason_codes"] == ["GIT_OBSERVATION_FAILED"]


def test_cli_json_is_deterministic_bounded_and_path_safe(
    tmp_path: Path,
    capsys,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "feature\n")
    args = [
        "--repo-root",
        str(repo),
        "--package",
        package_path,
        "--task-id",
        "feature-a",
        "--verification-status",
        "PASS",
        "--json",
    ]

    first_exit = postflight.main(args)
    first = capsys.readouterr().out
    second_exit = postflight.main(args)
    second = capsys.readouterr().out

    assert first_exit == second_exit == 0
    assert first == second
    assert first.endswith("\n")
    assert len(first.encode("utf-8")) <= postflight.MAX_OUTPUT_BYTES
    assert str(tmp_path) not in first
    assert json.loads(first)["performed_actions"] == []
