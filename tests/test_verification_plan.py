from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from scripts import verification_plan


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = REPO_ROOT / "docs" / "VERIFICATION_IMPACT_MAP.json"


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def write_text(repo: Path, relative: str, content: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def commit_file(repo: Path, relative: str, content: str, message: str = "change") -> str:
    write_text(repo, relative, content)
    git(repo, "add", relative)
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def init_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Synthetic Test")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    write_text(repo, "docs/VERIFICATION_IMPACT_MAP.json", MAP_PATH.read_text(encoding="utf-8"))
    write_text(
        repo,
        "artifacts/corpus-digest.json",
        json.dumps(
            {"sources": [{"source_path": "docs/corpus-policy.md"}]},
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    write_text(repo, "seed.txt", "seed\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")
    return repo, git(repo, "rev-parse", "HEAD").stdout.strip()


def inspect(repo: Path, base_sha: str, head_sha: str | None = None) -> dict[str, object]:
    return verification_plan.inspect_plan(
        repo_root=repo,
        base_sha=base_sha,
        head_sha=head_sha,
    )


def test_empty_diff_returns_v0_advisory_plan(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)

    result = inspect(repo, base_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V0"
    assert result["changed_paths"] == []
    assert result["matched_rule_ids"] == []
    assert result["reason_codes"] == []
    assert result["performed_actions"] == []
    assert result["required_command_ids"] == sorted(
        ["work_package_preflight", "base_sha_check", "allowed_file_review", "git_diff_check"]
    )
    assert [item["command_id"] for item in result["required_command_contracts"]] == (
        result["required_command_ids"]
    )


def test_document_change_returns_v1(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, "docs/guide.md", "# Guide\n")

    result = inspect(repo, base_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V1"
    assert result["matched_rule_ids"] == ["documentation"]
    assert "focused_pytest" in result["required_command_ids"]
    assert result["digest_check_required"] is False
    assert result["integration_owner_required"] is False


@pytest.mark.parametrize("relative_path", ["scripts/tool.py", "tests/test_tool.py"])
def test_script_and_test_changes_require_focused_tests(tmp_path: Path, relative_path: str) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, relative_path, "value = 1\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert "scripts_and_tests" in result["matched_rule_ids"]
    assert "focused_pytest" in result["required_command_ids"]


def test_renderer_change_escalates_to_v2_and_render_checks(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, "scripts/render_template.py", "print('synthetic')\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["render_check_required"] is True
    assert "render_dry_runs" in result["required_command_ids"]
    assert {"render_surface_exact", "scripts_and_tests"} <= set(result["matched_rule_ids"])


def test_authority_change_requires_integration_owner(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, "STATUS.md", "# Current\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert "central_authority_exact" in result["matched_rule_ids"]
    assert "full_pytest" in result["required_command_ids"]


@pytest.mark.parametrize(
    "relative_path",
    [
        "scripts/agent_quality.py",
        "artifacts/agent-quality-baseline.json",
        "evals/agentic/suites/agentic-regression-v1.json",
        "prompts/task_contract/agent_quality_trial.md",
    ],
)
def test_agent_quality_surface_requires_manual_static_check(
    tmp_path: Path,
    relative_path: str,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, relative_path, "{}\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert "agent_quality_static_check" in result["required_command_ids"]
    static_contract = next(
        contract
        for contract in result["required_command_contracts"]
        if contract["command_id"] == "agent_quality_static_check"
    )
    assert static_contract["kind"] == "command"
    assert static_contract["argv"] == [
        "python",
        "-m",
        "pytest",
        "tests/test_agent_quality_contracts.py",
        "tests/test_agent_quality_trial_validation.py",
        "tests/test_agent_quality_aggregation.py",
        "tests/test_agent_quality_semantic_failure.py",
        "tests/test_agent_quality_cli.py",
        "tests/test_json_evidence_gate.py",
        "-q",
    ]


@pytest.mark.parametrize(
    "relative_path",
    [
        "prompts/task_contract/task_contract.md",
        "prompts/task_contract/verification_closeout.md",
    ],
)
def test_work_package_prompt_contracts_require_v2_integration_owner(
    tmp_path: Path,
    relative_path: str,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, relative_path, "# Synthetic contract\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert result["reason_codes"] == []
    assert "work_package_prompt_contracts" in result["matched_rule_ids"]


def test_corpus_source_change_requires_digest_check(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, "docs/corpus-policy.md", "# Policy\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert result["digest_check_required"] is True
    assert "approved_corpus_sources" in result["matched_rule_ids"]
    assert "corpus_digest_check" in result["required_command_ids"]


@pytest.mark.parametrize(
    "relative_path",
    [
        "scripts/generate_manifest.py",
        "scripts/generate_checksums.py",
        "scripts/generate_sbom.py",
        "scripts/generate_provenance.py",
        "scripts/run_eval.py",
        "scripts/run_release_verify.ps1",
        "tests/test_run_eval.py",
    ],
)
def test_release_generator_change_requires_checksum_check(
    tmp_path: Path,
    relative_path: str,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, relative_path, "print('synthetic')\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert result["checksum_check_required"] is True
    assert "release_checksum_surface" in result["matched_rule_ids"]
    assert "checksum_verify" in result["required_command_ids"]


def test_unknown_path_conservatively_escalates_to_v2(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, "config/tool.cfg", "synthetic=true\n")

    result = inspect(repo, base_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V2"
    assert result["matched_rule_ids"] == []
    assert result["reason_codes"] == ["UNKNOWN_PATH_ESCALATED"]
    assert "full_pytest" in result["required_command_ids"]


@pytest.mark.parametrize(
    "unsafe_path",
    ["docs/CON", "docs/nul.txt", "docs/file?.md", "docs/file:stream"],
)
def test_shared_windows_path_policy_rejects_unsafe_changed_paths(
    unsafe_path: str,
) -> None:
    assert verification_plan.safe_repo_path(unsafe_path) is False


def test_invalid_sha_fails_without_git_observation(tmp_path: Path) -> None:
    result = inspect(tmp_path, "invalid")

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["BASE_SHA_INVALID"]
    assert result["performed_actions"] == []


def test_missing_ref_is_blocked(tmp_path: Path) -> None:
    repo, _ = init_repo(tmp_path)

    result = inspect(repo, "a" * 40)

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["BASE_REF_NOT_FOUND"]


def test_non_ancestor_base_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    git(repo, "checkout", "--orphan", "other")
    for path in list(repo.iterdir()):
        if path.name != ".git":
            if path.is_dir():
                import shutil

                shutil.rmtree(path)
            else:
                path.unlink()
    write_text(repo, "other.txt", "other\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "other")
    other_sha = git(repo, "rev-parse", "HEAD").stdout.strip()

    result = inspect(repo, base_sha, other_sha)

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["BASE_NOT_ANCESTOR"]


def test_not_a_repository_is_environment_blocked(tmp_path: Path) -> None:
    result = inspect(tmp_path, "a" * 40)

    assert result["status"] == "ENVIRONMENT BLOCKED"
    assert result["reason_codes"] == ["GIT_COMMAND_FAILED"]


def test_json_cli_is_deterministic_bounded_and_action_free(tmp_path: Path, capsys) -> None:
    repo, base_sha = init_repo(tmp_path)
    commit_file(repo, "docs/guide.md", "# Guide\n")
    args = [
        "--repo-root",
        str(repo),
        "--base-sha",
        base_sha,
        "--json",
    ]

    first_exit = verification_plan.main(args)
    first = capsys.readouterr().out
    second_exit = verification_plan.main(args)
    second = capsys.readouterr().out

    assert first_exit == second_exit == 0
    assert first == second
    assert first.endswith("\n")
    assert len(first.encode("utf-8")) <= verification_plan.MAX_OUTPUT_BYTES
    assert str(tmp_path) not in first
    assert json.loads(first)["performed_actions"] == []


def test_map_and_runtime_are_bounded_read_only_contracts() -> None:
    payload = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    source = (REPO_ROOT / "scripts" / "verification_plan.py").read_text(encoding="utf-8")

    assert payload["schema_version"] == "1"
    assert payload["planner_id"] == "verification_plan"
    assert set(payload["tier_command_ids"]) == {"V0", "V1", "V2"}
    assert set(payload["command_contracts"]) == set(payload["command_ids"])
    assert all(
        set(contract) == {"kind", "argv"}
        for contract in payload["command_contracts"].values()
    )
    assert MAP_PATH.read_bytes().endswith(b"\n")
    assert "shell=False" in source
    assert "timeout=GIT_TIMEOUT_SECONDS" in source
    assert "subprocess.run(" in source
    assert "os.system" not in source
    assert "Popen(" not in source
    assert "write_text(" not in source
    assert "write_bytes(" not in source
