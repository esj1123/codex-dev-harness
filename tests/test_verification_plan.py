from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
import subprocess
import sys

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
        verification_plan.CORPUS_SOURCE_SET_PATH,
        json.dumps(
            {
                "schema_version": "2.0",
                "expected_source_count": 1,
                "ordered_sources": [{"source_path": "docs/corpus-policy.md"}],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    write_text(
        repo,
        "artifacts/corpus-digest.json",
        json.dumps(
            {"sources": [{"source_path": "docs/generated-only.md"}]},
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


@pytest.fixture(scope="module")
def planner_seed_repo(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    return init_repo(tmp_path_factory.mktemp("planner-seed"))


@pytest.fixture
def planner_repo(tmp_path: Path, planner_seed_repo: tuple[Path, str]) -> tuple[Path, str]:
    seed, base_sha = planner_seed_repo
    repo = tmp_path / "repo"
    # Copy the Git directory too: tests must not share mutable refs or config.
    shutil.copytree(seed, repo)
    return repo, base_sha


def test_planner_repo_copies_isolate_commits_and_configuration(
    tmp_path: Path,
    planner_seed_repo: tuple[Path, str],
    planner_repo: tuple[Path, str],
) -> None:
    seed, base_sha = planner_seed_repo
    repo, copied_sha = planner_repo
    other = tmp_path / "other-copy"
    shutil.copytree(seed, other)
    assert copied_sha == base_sha
    original_map = (seed / "docs/VERIFICATION_IMPACT_MAP.json").read_bytes()
    original_config = (seed / ".git/config").read_bytes()
    for relative in ("docs/VERIFICATION_IMPACT_MAP.json", ".git/config"):
        assert not (seed / relative).samefile(repo / relative)
        assert not (seed / relative).samefile(other / relative)
        assert not (repo / relative).samefile(other / relative)

    changed_sha = commit_file(repo, "docs/VERIFICATION_IMPACT_MAP.json", "{}\n")
    git(repo, "config", "user.name", "Changed Copy")

    assert changed_sha != base_sha
    for untouched in (seed, other):
        assert git(untouched, "rev-parse", "HEAD").stdout.strip() == base_sha
        assert (untouched / "docs/VERIFICATION_IMPACT_MAP.json").read_bytes() == original_map
        assert (untouched / ".git/config").read_bytes() == original_config
        assert git(untouched, "status", "--porcelain").stdout == ""


def test_empty_diff_returns_v0_advisory_plan(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo

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


def test_alternate_head_uses_control_blobs_from_that_commit(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
    selected_head = commit_file(repo, "docs/guide.md", "# Guide\n")
    commit_file(repo, "docs/VERIFICATION_IMPACT_MAP.json", "{}\n")
    write_text(repo, verification_plan.CORPUS_SOURCE_SET_PATH, "{}\n")

    result = inspect(repo, base_sha, selected_head)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V1"
    assert result["matched_rule_ids"] == ["documentation"]


def test_impact_map_change_is_code_bootstrapped_to_v2(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
    payload = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    payload["rules"] = list(reversed(payload["rules"]))
    head_sha = commit_file(
        repo,
        "docs/VERIFICATION_IMPACT_MAP.json",
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
    )

    result = inspect(repo, base_sha, head_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert "verification_impact_map_bootstrap" in result["matched_rule_ids"]
    assert "full_pytest" in result["required_command_ids"]


def test_impact_map_bootstrap_preserves_full_when_map_removes_its_self_path(
    planner_repo: tuple[Path, str],
) -> None:
    repo, base_sha = planner_repo
    payload = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    full_rule = next(
        rule
        for rule in payload["rules"]
        if rule["rule_id"] == "pytest_infrastructure_full_regression"
    )
    full_rule["patterns"].remove(verification_plan.MAP_PATH)
    head_sha = commit_file(
        repo,
        verification_plan.MAP_PATH,
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
    )

    result = inspect(repo, base_sha, head_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert result["matched_rule_ids"] == ["verification_impact_map_bootstrap"]
    assert "core_pytest" in result["required_command_ids"]
    assert "full_pytest" in result["required_command_ids"]


def test_document_change_returns_v1(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "docs/guide.md", "# Guide\n")

    result = inspect(repo, base_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V1"
    assert result["matched_rule_ids"] == ["documentation"]
    assert "focused_pytest" in result["required_command_ids"]
    assert result["digest_check_required"] is False
    assert result["integration_owner_required"] is False



@pytest.mark.parametrize("relative_path", [
    "docs/workflows/harness-engineering-documents/SKILL.md",
    "docs/workflows/harness-engineering-diagrams/SKILL.md",
    "docs/workflows/harness-engineering-review/SKILL.md",
    "docs/workflows/harness-engineering-documents/references/design-derivation.md",
])
def test_existing_skill_guidance_edit_stays_v1(planner_repo, relative_path) -> None:
    repo, _ = planner_repo
    base_sha = commit_file(repo, relative_path, "# Existing guidance\n")
    commit_file(repo, relative_path, "# Clearer existing guidance\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert result["integration_owner_required"] is False
    assert "core_pytest" not in result["required_command_ids"]


def test_status_progress_update_stays_v1(planner_repo) -> None:
    repo, _ = planner_repo
    base_sha = commit_file(repo, "STATUS.md", "# STATUS\nNext: focused checks.\n")
    commit_file(repo, "STATUS.md", "# STATUS\nNext: report completed checks.\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert result["integration_owner_required"] is False
    assert "core_pytest" not in result["required_command_ids"]


@pytest.mark.parametrize("register", [False, True])
def test_new_skill_requires_integration_even_before_registration(planner_repo, register) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "docs/workflows/harness-new/SKILL.md", "# New selectable skill\n")
    if register:
        commit_file(repo, "docs/AUTHORITY_MANIFEST.json", '{"durable_policy": []}\n')

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert "workflow_skill_lifecycle" in result["matched_rule_ids"]
    assert {"core_pytest", "standalone_eval", "quality_gate"}.issubset(result["required_command_ids"])
    assert "full_pytest" not in result["required_command_ids"]


@pytest.mark.parametrize("rename", [False, True])
def test_skill_removal_or_rename_requires_integration(planner_repo, rename) -> None:
    repo, _ = planner_repo
    relative = "docs/workflows/harness-existing/SKILL.md"
    base_sha = commit_file(repo, relative, "# Existing skill\n")
    if rename:
        git(repo, "mv", relative, "docs/workflows/harness-existing/REFERENCE.md")
    else:
        git(repo, "rm", relative)
    git(repo, "commit", "-m", "remove selectable entrypoint")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert "workflow_skill_lifecycle" in result["matched_rule_ids"]


@pytest.mark.parametrize("relative_path", ["scripts/tool.py", "tests/test_tool.py"])
def test_script_and_test_changes_require_focused_tests(
    planner_repo: tuple[Path, str], relative_path: str
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, relative_path, "value = 1\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert "scripts_and_tests" in result["matched_rule_ids"]
    assert "focused_pytest" in result["required_command_ids"]
    assert "full_pytest" not in result["required_command_ids"]
    assert result["integration_owner_required"] is False


def test_renderer_change_escalates_to_v2_and_render_checks(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "scripts/render_template.py", "print('synthetic')\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["render_check_required"] is True
    assert "render_dry_runs" in result["required_command_ids"]
    assert result["matched_rule_ids"] == ["render_surface_exact"]


@pytest.mark.parametrize("relative_path", [
    "AGENTS.md", "docs/AUTHORITY_MANIFEST.json", "docs/SAFETY_POLICY.md",
    "docs/VERIFICATION.md", "docs/CHANGE_CONTROL.md", "docs/CI_POLICY.md",
    "docs/HUMAN_APPROVALS.md", "SECURITY.md",
])
def test_authority_change_requires_integration_owner(
    planner_repo: tuple[Path, str], relative_path: str,
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, relative_path, "# Changed policy contract\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert "central_authority_exact" in result["matched_rule_ids"]
    assert "core_pytest" in result["required_command_ids"]
    assert "full_pytest" not in result["required_command_ids"]


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
    planner_repo: tuple[Path, str],
    relative_path: str,
) -> None:
    repo, base_sha = planner_repo
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
        "tests/test_agent_quality_capture.py",
        "tests/test_agent_quality_trial_validation.py",
        "tests/test_agent_quality_aggregation.py",
        "tests/test_agent_quality_semantic_failure.py",
        "tests/test_agent_quality_cli.py",
        "tests/test_agent_role_profiles.py",
        "tests/test_json_evidence_gate.py",
        "-q",
    ]


@pytest.mark.parametrize(
    "relative_path",
    [
        "prompts/task_contract/task_contract.md",
        "prompts/task_contract/critic_review.md",
        "prompts/task_contract/verification_closeout.md",
    ],
)
def test_work_package_prompt_contracts_require_v2_integration_owner(
    planner_repo: tuple[Path, str],
    relative_path: str,
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, relative_path, "# Synthetic contract\n")

    result = inspect(repo, base_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert result["reason_codes"] == []
    assert result["matched_rule_ids"] == ["work_package_prompt_contracts"]
    assert {"core_pytest", "standalone_eval", "quality_gate"}.issubset(
        result["required_command_ids"]
    )
    assert "full_pytest" not in result["required_command_ids"]


def test_three_prompt_contracts_share_v2_without_unknown_escalation(
    planner_repo: tuple[Path, str],
) -> None:
    repo, base_sha = planner_repo
    for name in ("task_contract", "critic_review", "verification_closeout"):
        write_text(repo, f"prompts/task_contract/{name}.md", "# Contract\n")
    git(repo, "add", "prompts/task_contract")
    git(repo, "commit", "-m", "three prompt contracts")

    result = inspect(repo, base_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert result["reason_codes"] == []
    assert result["matched_rule_ids"] == ["work_package_prompt_contracts"]
    assert {"core_pytest", "standalone_eval", "quality_gate"}.issubset(
        result["required_command_ids"]
    )
    assert "full_pytest" not in result["required_command_ids"]


@pytest.mark.parametrize(
    ("relative_path", "extra_command", "flag", "unknown"),
    [
        ("prompts/task_contract/unclassified.md", "full_pytest", None, True),
        ("config/tool.cfg", "full_pytest", None, True),
        ("scripts/work_package_conflict_check.py", "full_pytest", None, False),
        ("pytest.ini", "full_pytest", None, False),
        ("docs/corpus-policy.md", "corpus_digest_check", "digest_check_required", False),
        ("scripts/render_template.py", "render_dry_runs", "render_check_required", False),
        ("artifacts/release-manifest.json", "checksum_verify", "checksum_check_required", False),
        ("scripts/hermes_sidecar.py", "hermes_mcp_static_check", None, False),
        ("scripts/local_rag_retriever.py", "local_rag_static_check", None, False),
    ],
)
def test_critic_review_mixed_changes_retain_other_path_requirements(
    planner_repo: tuple[Path, str], relative_path: str, extra_command: str,
    flag: str | None, unknown: bool,
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "prompts/task_contract/critic_review.md", "# Review\n")
    commit_file(repo, relative_path, "synthetic\n")

    result = inspect(repo, base_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert "work_package_prompt_contracts" in result["matched_rule_ids"]
    assert {"core_pytest", "standalone_eval", "quality_gate", extra_command}.issubset(
        result["required_command_ids"]
    )
    assert result["reason_codes"] == (["UNKNOWN_PATH_ESCALATED"] if unknown else [])
    if flag:
        assert result[flag] is True
    if extra_command != "full_pytest":
        assert "full_pytest" not in result["required_command_ids"]


def test_critic_review_and_map_change_preserve_code_bootstrapped_full(
    planner_repo: tuple[Path, str],
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "prompts/task_contract/critic_review.md", "# Review\n")
    payload = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    full_rule = next(
        rule for rule in payload["rules"]
        if rule["rule_id"] == "pytest_infrastructure_full_regression"
    )
    full_rule["patterns"].remove(verification_plan.MAP_PATH)
    commit_file(repo, verification_plan.MAP_PATH, json.dumps(payload) + "\n")

    result = inspect(repo, base_sha)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert result["reason_codes"] == []
    assert result["matched_rule_ids"] == [
        "verification_impact_map_bootstrap", "work_package_prompt_contracts"
    ]
    assert {"core_pytest", "standalone_eval", "quality_gate", "full_pytest"}.issubset(
        result["required_command_ids"]
    )


def test_critic_review_classification_uses_selected_head_not_later_or_dirty_map(
    planner_repo: tuple[Path, str],
) -> None:
    repo, base_sha = planner_repo
    selected_head = commit_file(repo, "prompts/task_contract/critic_review.md", "# Review\n")
    commit_file(repo, verification_plan.MAP_PATH, "{}\n")
    write_text(repo, verification_plan.MAP_PATH, "not json\n")
    write_text(repo, verification_plan.CORPUS_SOURCE_SET_PATH, "{}\n")

    result = inspect(repo, base_sha, selected_head)

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert result["reason_codes"] == []
    assert result["matched_rule_ids"] == ["work_package_prompt_contracts"]
    assert {"core_pytest", "standalone_eval", "quality_gate"}.issubset(
        result["required_command_ids"]
    )
    assert "full_pytest" not in result["required_command_ids"]


def test_corpus_source_change_requires_digest_check(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "docs/corpus-policy.md", "# Policy\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert result["digest_check_required"] is True
    assert "approved_corpus_sources" in result["matched_rule_ids"]
    assert "corpus_digest_check" in result["required_command_ids"]


def test_generated_digest_membership_does_not_define_corpus_sources(
    planner_repo: tuple[Path, str],
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "docs/generated-only.md", "# Generated-only member\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert result["digest_check_required"] is False
    assert result["matched_rule_ids"] == ["documentation"]
    assert "corpus_digest_check" not in result["required_command_ids"]


def test_corpus_digest_exact_rule_overrides_artifact_prefix(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "artifacts/corpus-digest.json", '{"changed": true}\n')

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert result["digest_check_required"] is True
    assert result["integration_owner_required"] is False
    assert result["matched_rule_ids"] == ["corpus_control_surface"]
    assert "corpus_digest_check" in result["required_command_ids"]


@pytest.mark.parametrize(
    "relative_path",
    [
        "artifacts/release-manifest.json",
        "artifacts/checksums.sha256",
        "artifacts/sbom.spdx.json",
        "artifacts/sbom.cdx.json",
        "artifacts/provenance.intoto.jsonl",
        "artifacts/eval-report.json",
    ],
)
def test_known_release_artifact_requires_v2_integration_owner(
    planner_repo: tuple[Path, str],
    relative_path: str,
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, relative_path, "synthetic\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["checksum_check_required"] is True
    assert result["integration_owner_required"] is True
    assert result["matched_rule_ids"] == ["release_artifact_control_surface"]
    assert "checksum_verify" in result["required_command_ids"]


def test_checksum_gate_keeps_v2_integration_owner_routing(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "scripts/gates/checksum_verify_gate.py", "value = 1\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["checksum_check_required"] is True
    assert result["integration_owner_required"] is True
    assert result["matched_rule_ids"] == ["release_artifact_control_surface"]


def test_unknown_artifact_fails_closed_to_v2_integration_owner(
    planner_repo: tuple[Path, str]
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "artifacts/unexpected.json", "{}\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert result["matched_rule_ids"] == ["central_integration_prefix"]


def test_multiple_paths_preserve_flags_and_select_highest_tier(
    planner_repo: tuple[Path, str]
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "artifacts/corpus-digest.json", '{"changed": true}\n')
    commit_file(repo, "artifacts/unexpected.json", "{}\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["digest_check_required"] is True
    assert result["integration_owner_required"] is True
    assert result["matched_rule_ids"] == [
        "central_integration_prefix",
        "corpus_control_surface",
    ]
    assert "corpus_digest_check" in result["required_command_ids"]
    assert "core_pytest" in result["required_command_ids"]
    assert "full_pytest" not in result["required_command_ids"]


def test_invalid_approved_source_set_fails_closed(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
    commit_file(
        repo,
        verification_plan.CORPUS_SOURCE_SET_PATH,
        json.dumps(
            {
                "schema_version": "2.0",
                "expected_source_count": 1,
                "ordered_sources": [{"source_path": "../outside.md"}],
            }
        )
        + "\n",
    )

    result = inspect(repo, base_sha)

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["CORPUS_SOURCE_SET_INVALID"]


@pytest.mark.parametrize(
    "relative_path",
    [
        "scripts/generate_manifest.py",
        "scripts/generate_sbom.py",
        "scripts/generate_provenance.py",
        "scripts/run_eval.py",
        "scripts/run_release_verify.ps1",
        "tests/test_run_eval.py",
    ],
)
def test_release_generator_change_requires_checksum_check(
    planner_repo: tuple[Path, str],
    relative_path: str,
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, relative_path, "print('synthetic')\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V1"
    assert result["checksum_check_required"] is True
    assert "release_checksum_surface" in result["matched_rule_ids"]
    assert "checksum_verify" in result["required_command_ids"]
    assert "full_pytest" not in result["required_command_ids"]
    assert result["integration_owner_required"] is False



@pytest.mark.parametrize(
    ("relative_path", "command_id"),
    [
        ("scripts/hermes_sidecar.py", "hermes_mcp_static_check"),
        ("tests/test_mcp_tool_boundary_contract.py", "hermes_mcp_static_check"),
        ("scripts/local_rag_retriever.py", "local_rag_static_check"),
    ],
)
def test_optional_surface_adds_its_focused_command(
    planner_repo: tuple[Path, str], relative_path: str, command_id: str
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, relative_path, "value = 1\n")

    result = inspect(repo, base_sha)

    assert command_id in result["required_command_ids"]


@pytest.mark.parametrize(
    "relative_path",
    [
        "pytest.ini",
        "tests/conftest.py",
        "requirements-dev.lock",
        "scripts/repo_path_policy.py",
        "scripts/verification_plan.py",
        "scripts/work_package_conflict_check.py",
        "scripts/generate_checksums.py",
    ],
)
def test_pytest_infrastructure_and_common_validator_require_full_regression(
    planner_repo: tuple[Path, str], relative_path: str
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, relative_path, "synthetic\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert "pytest_infrastructure_full_regression" in result["matched_rule_ids"]
    assert "core_pytest" in result["required_command_ids"]
    assert "full_pytest" in result["required_command_ids"]
    assert result["integration_owner_required"] is True
    if relative_path == "scripts/generate_checksums.py":
        assert result["checksum_check_required"] is True
        assert "release_checksum_surface" in result["matched_rule_ids"]

        assert "checksum_verify" in result["required_command_ids"]


def test_common_validators_mixed_diff_preserves_full_and_checksum(
    planner_repo: tuple[Path, str]
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, "scripts/work_package_conflict_check.py", "synthetic\n")
    commit_file(repo, "scripts/generate_checksums.py", "synthetic\n")

    result = inspect(repo, base_sha)

    assert result["minimum_tier"] == "V2"
    assert result["integration_owner_required"] is True
    assert result["checksum_check_required"] is True
    assert result["matched_rule_ids"] == [
        "pytest_infrastructure_full_regression",
        "release_checksum_surface",
    ]
    assert {"core_pytest", "full_pytest", "checksum_verify"}.issubset(
        result["required_command_ids"]
    )


def test_unknown_path_conservatively_escalates_to_v2(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
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


def test_missing_ref_is_blocked(planner_repo: tuple[Path, str]) -> None:
    repo, _ = planner_repo

    result = inspect(repo, "a" * 40)

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["BASE_REF_NOT_FOUND"]


def test_non_ancestor_base_is_blocked(planner_repo: tuple[Path, str]) -> None:
    repo, base_sha = planner_repo
    git(repo, "checkout", "--orphan", "other")
    for path in list(repo.iterdir()):
        if path.name != ".git":
            if path.is_dir():
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


def test_json_cli_is_deterministic_bounded_and_action_free(
    tmp_path: Path, planner_repo: tuple[Path, str], capsys
) -> None:
    repo, base_sha = planner_repo
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
    parsed = json.loads(first)
    assert set(parsed) == set(verification_plan.base_result())
    assert parsed["performed_actions"] == []


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


@pytest.mark.parametrize(
    "relative_path",
    ["tests/test_agent_quality_capture.py", "tests/test_agent_role_profiles.py"],
)
def test_changed_aq_module_is_in_its_required_static_command(
    planner_repo: tuple[Path, str], relative_path: str,
) -> None:
    repo, base_sha = planner_repo
    commit_file(repo, relative_path, "def test_regression():\n    assert False\n")

    result = inspect(repo, base_sha)
    contract = next(
        item for item in result["required_command_contracts"]
        if item["command_id"] == "agent_quality_static_check"
    )

    assert result["status"] == "PASS"
    assert result["minimum_tier"] == "V2"
    assert result["matched_rule_ids"] == ["agent_quality_test_surface"]
    assert relative_path in contract["argv"]
    assert "full_pytest" not in result["required_command_ids"]
    assert contract["argv"][:3] == ["python", "-m", "pytest"]
    assert contract["argv"][3:].count("-m") == 0


def _collect_aq_selection(pytest_args: list[str]) -> set[str]:
    environment = os.environ.copy()
    for name in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTHONPATH"):
        environment.pop(name, None)
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [
            sys.executable, "-B", "-m", "pytest", *pytest_args,
            "--collect-only", "-p", "no:cacheprovider",
        ],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return {
        line.replace("\\", "/")
        for line in completed.stdout.splitlines()
        if line.startswith(("tests/", "tests\\")) and "::" in line
    }


def test_aq_static_command_collects_every_marker_and_impact_test() -> None:
    impact_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    static_argv = impact_map["command_contracts"]["agent_quality_static_check"]["argv"]
    impact_tests = set(next(
        rule["patterns"] for rule in impact_map["rules"]
        if rule["rule_id"] == "agent_quality_test_surface"
    ))
    assert static_argv[:3] == ["python", "-m", "pytest"]

    marked_nodes = _collect_aq_selection(["tests", "-m", "optional_agent_quality", "-q"])
    selected_nodes = _collect_aq_selection(static_argv[3:])
    marked_files = {node.split("::", 1)[0] for node in marked_nodes}

    assert marked_nodes
    assert marked_files == impact_tests
    assert {
        "tests/test_agent_quality_capture.py", "tests/test_agent_role_profiles.py"
    } <= marked_files
    assert marked_nodes <= selected_nodes
