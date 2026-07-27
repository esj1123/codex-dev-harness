from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts.agent_quality_lib import aggregation
from scripts.agent_quality_lib.contracts import METRIC_KEYS, sha256_json
from scripts.agent_quality_lib.fingerprint import normalize_fingerprint


PROFILES_PATH = Path("evals/agentic/agent-role-profiles.json")
SUITE_PATH = Path("evals/agentic/suites/agentic-regression-v2.json")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_role_profiles_are_canonical_and_exact() -> None:
    payload = load_json(PROFILES_PATH)
    profiles = {item["profile_id"]: item for item in payload["profiles"]}

    assert PROFILES_PATH.read_text(encoding="utf-8") == (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    assert {
        "contract_planner",
        "feature_implementer",
        "critical_implementer",
        "semantic_reviewer",
        "integration_owner",
    } == set(profiles)
    assert {item["model_id"] for item in profiles.values()} == {"gpt-5.6-sol"}
    assert profiles["feature_implementer"]["reasoning_profile"] == "medium"
    assert profiles["semantic_reviewer"]["reasoning_profile"] == "xhigh"
    assert profiles["contract_planner"]["read_only"] is True
    assert profiles["semantic_reviewer"]["read_only"] is True


def test_suite_v2_binds_exact_role_mapping_and_profile_hashes() -> None:
    profiles_payload = load_json(PROFILES_PATH)
    profiles = {item["profile_id"]: item for item in profiles_payload["profiles"]}
    suite = load_json(SUITE_PATH)
    mapping = {task["task_id"]: task["agent_profile_id"] for task in suite["tasks"]}

    assert suite["profile_set_hash"] == sha256_json(profiles_payload)
    assert mapping == {
        "numeric-range-parser": "critical_implementer",
        "numeric-range-evaluator": "critical_implementer",
        "allowed-values-parser": "feature_implementer",
        "allowed-values-evaluator": "feature_implementer",
        "allowed-values-integration": "integration_owner",
    }
    for task in suite["tasks"]:
        assert task["agent_profile_hash"] == sha256_json(
            profiles[task["agent_profile_id"]]
        )
    assert suite["semantic_review_profile_id"] == "semantic_reviewer"
    assert suite["semantic_review_profile_hash"] == sha256_json(
        profiles["semantic_reviewer"]
    )
    assert aggregation._suite_tasks_v2(suite)


def mini_suite() -> dict:
    tasks = []
    for task_id, trials, criticality, profile_id, reasoning in (
        ("normal-task", 3, "normal", "feature_implementer", "medium"),
        ("critical-task", 5, "critical", "critical_implementer", "high"),
    ):
        profile = {
            "profile_id": profile_id,
            "model_id": "gpt-5.6-sol",
            "reasoning_profile": reasoning,
            "lane": "feature",
            "read_only": False,
        }
        tasks.append(
            {
                "agent_profile_hash": sha256_json(profile),
                "agent_profile_id": profile_id,
                "criticality": criticality,
                "invariant_grader_id": f"{task_id}-grader",
                "lane": "feature",
                "required_invariant_ids": [f"{task_id.upper()}_INVARIANT"],
                "source_basis": "a" * 40,
                "task_id": task_id,
                "trials": trials,
                "verification_contract": {
                    "commands": [
                        {"argv": ["{PYTHON}", "-V"], "command_id": "focused_check"}
                    ],
                    "interpreter_id": "python-3.12.13",
                },
                "write_set": [f"src/{task_id}.py"],
            }
        )
    return {
        "schema_version": "2",
        "status": "READY",
        "suite_class": "agentic_regression",
        "suite_id": "mini-agentic-v2",
        "profile_set_id": "mini-role-profiles",
        "profile_set_hash": "b" * 64,
        "semantic_review_profile_id": "semantic_reviewer",
        "semantic_review_profile_hash": "c" * 64,
        "target_checkpoint": "d" * 40,
        "tasks": tasks,
        "total_trials": 8,
    }


def make_run(task: dict, trial: int) -> dict:
    reasoning = (
        "medium" if task["agent_profile_id"] == "feature_implementer" else "high"
    )
    fingerprint = normalize_fingerprint(
        {
            "harness_commit": "e" * 40,
            "target_base_commit": task["source_basis"],
            "contract_basis_sha": task["source_basis"],
            "work_package_plan_digest": sha256_json(
                {"task_id": task["task_id"]}
            ),
            "agent_adapter_id": "codex-subagent",
            "agent_adapter_version": "2.0.0",
            "model_id": "gpt-5.6-sol",
            "reasoning_profile": reasoning,
            "task_contract_hash": sha256_json(task),
            "tool_policy_hash": "1" * 64,
            "skill_set_hash": "2" * 64,
            "approved_corpus_digest": "3" * 64,
            "dependency_lock_hash": "4" * 64,
            "environment_profile_id": "windows-python-3.12.13",
            "verification_suite_id": "mini-agentic-v2",
            "grader_version": "2.0.0",
        }
    )
    command = task["verification_contract"]["commands"][0]
    metrics = {key: 0 for key in METRIC_KEYS}
    metrics["holdout_passed_count"] = 1
    return {
        "schema_version": "2",
        "run_id": f"{task['task_id']}-run-{trial}",
        "task_id": task["task_id"],
        "trial_id": f"trial-{trial:02d}",
        "suite_id": "mini-agentic-v2",
        "task_class": "feature",
        "criticality": task["criticality"],
        "agent_profile": {
            "agent_profile_id": task["agent_profile_id"],
            "agent_profile_hash": task["agent_profile_hash"],
            "model_id": "gpt-5.6-sol",
            "reasoning_profile": reasoning,
            "model_selection_source": "ADAPTER_REQUEST",
            "model_observation_status": "NOT_INDEPENDENTLY_OBSERVABLE",
            "agent_id": f"agent-{trial}",
            "request_hash": sha256_json(
                {"task": task["task_id"], "trial": trial}
            ),
        },
        "fingerprint": fingerprint,
        "execution": {
            "status": "PASS",
            "reason_codes": [],
            "verification_contract_hash": sha256_json(
                task["verification_contract"]
            ),
            "interpreter_id": "python-3.12.13",
            "interpreter_version": "3.12.13",
            "required_command_ids": ["focused_check"],
            "completed_command_ids": ["focused_check"],
            "command_results": [
                {
                    "command_id": "focused_check",
                    "argv_hash": sha256_json(command["argv"]),
                    "exit_code": 0,
                    "stdout_sha256": "5" * 64,
                    "stdout_bytes": 1,
                    "stderr_sha256": "6" * 64,
                    "stderr_bytes": 0,
                    "status": "PASS",
                }
            ],
            "postflight_result_hash": "7" * 64,
        },
        "repository": {
            "base_sha": "a" * 40,
            "head_sha": "b" * 40,
            "tree_sha": "c" * 40,
            "commit_count": 1,
            "diff_sha256": "8" * 64,
            "changed_path_count": 1,
            "changed_path_set_hash": "9" * 64,
            "untracked_path_count": 0,
            "untracked_path_set_hash": "0" * 64,
            "rename_count": 0,
            "delete_count": 0,
            "dirty": False,
        },
        "grading": {
            "functional_correctness": "PASS",
            "contract_adherence": "PASS",
            "scope_adherence": "PASS",
            "semantic_consistency": "PASS",
            "architectural_consistency": "PASS",
            "safety_compliance": "PASS",
            "reproducibility": "PASS",
            "blocker_count": 0,
            "invariant_results": [
                {
                    "invariant_id": task["required_invariant_ids"][0],
                    "grader_id": task["invariant_grader_id"],
                    "status": "PASS",
                    "result_hash": "a" * 64,
                }
            ],
            "grader_id": task["invariant_grader_id"],
            "grader_version": "2.0.0",
            "exit_code": 0,
            "stdout_sha256": "b" * 64,
            "stdout_bytes": 1,
            "stderr_sha256": "c" * 64,
            "stderr_bytes": 0,
            "status": "PASS",
        },
        "metrics": metrics,
        "evidence_refs": [],
        "performed_actions": ["local_write", "execute"],
    }


def test_role_aware_aggregation_is_deterministic() -> None:
    suite = mini_suite()
    runs = [
        make_run(task, trial)
        for task in suite["tasks"]
        for trial in range(1, task["trials"] + 1)
    ]

    first = aggregation.aggregate_runs(suite, runs)
    second = aggregation.aggregate_runs(suite, list(reversed(runs)))

    assert first == second
    assert first["schema_version"] == "2"
    assert first["status"] == "PASS"
    assert len(first["role_configuration_manifest"]) == 2
    assert first["metrics"]["strict_pass_3_task_rate"] == 1.0
    assert first["metrics"]["strict_pass_5_critical_rate"] == 1.0


def test_profile_set_mismatch_holds_without_metric_comparison() -> None:
    suite = mini_suite()
    runs = [
        make_run(task, trial)
        for task in suite["tasks"]
        for trial in range(1, task["trials"] + 1)
    ]
    baseline = aggregation.aggregate_runs(suite, runs)
    candidate = copy.deepcopy(baseline)
    candidate["profile_set_hash"] = "f" * 64
    candidate["metrics"]["critical_failure_count"] = 99

    result = aggregation.compare_role_aggregates(baseline, candidate)

    assert result["status"] == "HOLD"
    assert result["reason_codes"] == ["PROFILE_SET_MISMATCH"]
