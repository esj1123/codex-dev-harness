from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import work_package_conflict_check as preflight
from scripts.agent_quality_lib import capture
from scripts.agent_quality_lib.contracts import (
    AgentQualityValidationError,
    METRIC_KEYS,
    sha256_json,
    validate_run,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


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


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def fixture(tmp_path: Path) -> dict[str, object]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Synthetic")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    write(repo / ".gitignore", "/local/\n")
    write(repo / "contract.md", "frozen\n")
    git(repo, "add", ".gitignore", "contract.md")
    git(repo, "commit", "-m", "base")
    base_sha = git(repo, "rev-parse", "HEAD")

    profile = {
        "profile_id": "critical_implementer",
        "model_id": "gpt-5.6-sol",
        "reasoning_profile": "high",
        "lane": "feature",
        "read_only": False,
    }
    profiles = {
        "schema_version": "1",
        "profile_set_id": "role-profiles-v1",
        "profiles": [profile],
    }
    package = {
        "schema_version": "3",
        "task_id": "numeric-range-parser",
        "base_sha": base_sha,
        "contract_basis_sha": base_sha,
        "contract_frozen_paths": ["contract.md"],
        "lane": "feature",
        "depends_on": [],
        "read_set": ["contract.md"],
        "write_set": ["feature.py"],
        "generated_outputs": [],
        "verification_tier": "V1",
        "verification_contract": {
            "interpreter_id": "python-3.12.13",
            "commands": [
                {
                    "command_id": "focused_check",
                    "argv": ["{PYTHON}", "-c", "print('synthetic-canary')"],
                }
            ],
        },
        "declared_side_effects": ["local_write", "execute", "stage", "commit"],
        "approval_ref": "synthetic-approval",
        "agent_profile_id": profile["profile_id"],
        "agent_profile_hash": sha256_json(profile),
    }
    package_path = repo / "local" / "work-packages" / "numeric.json"
    write(package_path, json.dumps(package, indent=2, sort_keys=True) + "\n")
    write(repo / "feature.py", "VALUE = 1\n")
    git(repo, "add", "feature.py")
    git(repo, "commit", "-m", "feature")

    suite = {
        "schema_version": "2",
        "suite_id": "agentic-regression-v2",
        "profile_set_id": profiles["profile_set_id"],
        "profile_set_hash": sha256_json(profiles),
        "tasks": [
            {
                "task_id": package["task_id"],
                "source_basis": base_sha,
                "lane": "feature",
                "criticality": "normal",
                "agent_profile_id": profile["profile_id"],
                "invariant_grader_id": "numeric-rules-grader-v2",
                "required_invariant_ids": ["FINITE_DECIMAL_FORMS_ACCEPTED"],
            }
        ],
    }
    grader = tmp_path / "grader.py"
    grader_output = {
        "blocker_count": 0,
        "dimensions": {
            "functional_correctness": "PASS",
            "contract_adherence": "PASS",
            "scope_adherence": "PASS",
            "semantic_consistency": "PASS",
            "architectural_consistency": "PASS",
            "safety_compliance": "PASS",
            "reproducibility": "PASS",
        },
        "invariant_results": [
            {"invariant_id": "FINITE_DECIMAL_FORMS_ACCEPTED", "status": "PASS"}
        ],
        "metrics": {key: 0 for key in METRIC_KEYS},
    }
    grader_output["metrics"]["holdout_passed_count"] = 1
    write(
        grader,
        "import json\n"
        f"print(json.dumps({grader_output!r}, sort_keys=True))\n",
    )
    grader_manifest = {
        "schema_version": "1",
        "grader_id": "numeric-rules-grader-v2",
        "grader_version": "2.0.0",
        "grader_path": "grader.py",
        "argv": ["{PYTHON}", "{GRADER}", "--repo-root", "{REPO_ROOT}"],
        "required_invariant_ids": ["FINITE_DECIMAL_FORMS_ACCEPTED"],
        "timeout_seconds": 30,
    }
    launch = {
        "schema_version": "1",
        "status": "PASS",
        "agent_id": "safe-agent-id",
        "request_hash": "a" * 64,
        "agent_adapter_id": "codex-subagent",
        "agent_adapter_version": "2.0.0",
        "requested_profile_id": profile["profile_id"],
        "requested_profile_hash": sha256_json(profile),
        "tool_policy_hash": "b" * 64,
        "skill_set_hash": "c" * 64,
    }
    return {
        "repo": repo,
        "package": package,
        "package_path": package_path,
        "profiles": profiles,
        "suite": suite,
        "grader_manifest": grader_manifest,
        "grader_path": tmp_path / "grader-manifest.json",
        "launch": launch,
    }


def capture_fixture(tmp_path: Path) -> dict:
    values = fixture(tmp_path)
    write(
        values["grader_path"],
        json.dumps(values["grader_manifest"], indent=2, sort_keys=True) + "\n",
    )
    return capture.capture_run(
        suite=values["suite"],
        profiles=values["profiles"],
        package=values["package"],
        package_path=values["package_path"].relative_to(values["repo"]).as_posix(),
        task_id="numeric-range-parser",
        trial_id="trial-01",
        repo_root=values["repo"],
        launch_receipt=values["launch"],
        grader_manifest=values["grader_manifest"],
        grader_manifest_path=values["grader_path"],
        harness_root=REPO_ROOT,
    )


def test_capture_run_binds_machine_observations_without_raw_output(tmp_path: Path) -> None:
    run = capture_fixture(tmp_path)

    assert validate_run(run) == run
    assert run["schema_version"] == "2"
    assert run["execution"]["status"] == "PASS"
    assert run["execution"]["completed_command_ids"] == ["focused_check"]
    assert run["repository"]["commit_count"] == 1
    assert run["repository"]["changed_path_count"] == 1
    assert run["repository"]["dirty"] is False
    assert run["grading"]["status"] == "PASS"
    serialized = json.dumps(run, sort_keys=True)
    assert "synthetic-canary" not in serialized
    assert str(tmp_path) not in serialized
    assert "stdout" not in run["execution"]["command_results"][0]
    assert "stderr" not in run["execution"]["command_results"][0]


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("repository", "diff_sha256"),
        ("repository", "changed_path_set_hash"),
        ("execution", "postflight_result_hash"),
        ("grading", "stdout_sha256"),
    ],
)
def test_capture_hash_tampering_is_rejected(
    tmp_path: Path, section: str, field: str
) -> None:
    run = capture_fixture(tmp_path)
    run[section][field] = "not-a-hash"

    with pytest.raises(AgentQualityValidationError):
        validate_run(run)


def test_capture_rejects_profile_mismatch_before_execution(tmp_path: Path) -> None:
    values = fixture(tmp_path)
    values["launch"]["requested_profile_hash"] = "f" * 64

    with pytest.raises(
        AgentQualityValidationError, match="AGENT_PROFILE_MISMATCH"
    ):
        capture.capture_run(
            suite=values["suite"],
            profiles=values["profiles"],
            package=values["package"],
            package_path=values["package_path"].relative_to(values["repo"]).as_posix(),
            task_id="numeric-range-parser",
            trial_id="trial-01",
            repo_root=values["repo"],
            launch_receipt=values["launch"],
            grader_manifest=values["grader_manifest"],
            grader_manifest_path=values["grader_path"],
            harness_root=REPO_ROOT,
        )


def test_process_failures_and_timeouts_are_captured_without_exception(tmp_path: Path) -> None:
    failed = capture._run(
        [sys.executable, "-c", "raise SystemExit(7)"],
        cwd=tmp_path,
        timeout_seconds=5,
    )
    timed_out = capture._run(
        [sys.executable, "-c", "import time; time.sleep(2)"],
        cwd=tmp_path,
        timeout_seconds=1,
    )

    assert failed["status"] == "FAIL"
    assert failed["exit_code"] == 7
    assert timed_out["status"] == "ENVIRONMENT BLOCKED"
    assert timed_out["exit_code"] is None


def test_process_output_over_one_mib_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(AgentQualityValidationError, match="CAPTURE_OUTPUT_TOO_LARGE"):
        capture._run(
            [sys.executable, "-c", "print('x' * 1048577)"],
            cwd=tmp_path,
            timeout_seconds=10,
        )
