from __future__ import annotations

from copy import deepcopy
import hashlib
import json

import pytest

from scripts.agent_quality_lib.adoption import build_baseline, compare_baseline
from scripts.agent_quality_lib.aggregation import aggregate_runs
from scripts.agent_quality_lib.contracts import sha256_json
from scripts.agent_quality_lib.fingerprint import normalize_fingerprint


ZERO_METRICS = {
    "critical_failure_count": 0,
    "scope_violation_count": 0,
    "safety_violation_count": 0,
    "postflight_block_count": 0,
    "contract_reopen_count": 0,
    "semantic_blocker_count": 0,
    "integration_fix_file_count": 0,
    "integration_fix_line_count": 0,
    "holdout_passed_count": 1,
    "holdout_failed_count": 0,
}

TASKS = (
    ("normal-a", "normal", 3),
    ("normal-b", "normal", 3),
    ("normal-c", "normal", 3),
    ("critical-a", "critical", 5),
    ("critical-b", "critical", 5),
)


def make_suite() -> dict:
    return {
        "schema_version": "1",
        "status": "READY",
        "suite_class": "agentic_regression",
        "suite_id": "agentic-regression-v1",
        "required_configuration": {
            "agent_adapter_id": "codex-subagent",
            "agent_adapter_version": "1.0",
            "environment_profile_id": "python-3.12",
            "model_id": "gpt-5.6-sol",
            "reasoning_profile": "high",
        },
        "target_checkpoint": "9" * 40,
        "total_trials": 19,
        "tasks": [
            {
                "task_id": task_id,
                "criticality": criticality,
                "invariant_grader_id": f"{task_id}-grader-v1",
                "lane": "feature",
                "required_invariant_ids": ["FOCUSED_CONTRACT_PRESERVED"],
                "source_basis": "2" * 40,
                "trials": trials,
                "verification_contract": {
                    "commands": [
                        {
                            "argv": [
                                "{PYTHON}",
                                "-m",
                                "pytest",
                                f"tests/test_{task_id}.py",
                                "-q",
                            ],
                            "command_id": "focused_pytest",
                        }
                    ],
                    "interpreter_id": "python-3.12.13-pytest-9.0.3",
                },
                "write_set": [f"src/{task_id}.py"],
            }
            for task_id, criticality, trials in TASKS
        ],
    }


def make_runs() -> list[dict]:
    runs = []
    tasks = {task["task_id"]: task for task in make_suite()["tasks"]}
    for task_id, criticality, trials in TASKS:
        task = tasks[task_id]
        verification_contract = task["verification_contract"]
        command_ids = [
            command["command_id"] for command in verification_contract["commands"]
        ]
        for trial_number in range(1, trials + 1):
            run_id = f"{task_id}-run-{trial_number}"
            fingerprint = normalize_fingerprint(
                {
                    "harness_commit": "1" * 40,
                    "target_base_commit": "2" * 40,
                    "contract_basis_sha": "2" * 40,
                    "work_package_plan_digest": hashlib.sha256(
                        task_id.encode("ascii")
                    ).hexdigest(),
                    "agent_adapter_id": "codex-subagent",
                    "agent_adapter_version": "1.0",
                    "model_id": "gpt-5.6-sol",
                    "reasoning_profile": "high",
                    "task_contract_hash": "4" * 64,
                    "tool_policy_hash": "5" * 64,
                    "skill_set_hash": "6" * 64,
                    "approved_corpus_digest": "7" * 64,
                    "dependency_lock_hash": "8" * 64,
                    "environment_profile_id": "python-3.12",
                    "verification_suite_id": "agentic-regression-v1",
                    "grader_version": "1.0",
                }
            )
            runs.append(
                {
                    "schema_version": "1",
                    "run_id": run_id,
                    "task_id": task_id,
                    "trial_id": f"trial-{trial_number}",
                    "suite_id": "agentic-regression-v1",
                    "task_class": "feature",
                    "criticality": criticality,
                    "fingerprint": fingerprint,
                    "execution": {
                        "status": "PASS",
                        "reason_codes": [],
                        "verification_contract_hash": sha256_json(
                            verification_contract
                        ),
                        "interpreter_id": verification_contract[
                            "interpreter_id"
                        ],
                        "required_command_ids": command_ids,
                        "completed_command_ids": command_ids,
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
                                "invariant_id": "FOCUSED_CONTRACT_PRESERVED",
                                "grader_id": task["invariant_grader_id"],
                                "status": "PASS",
                                "result_hash": hashlib.sha256(
                                    f"{run_id}:FOCUSED_CONTRACT_PRESERVED".encode(
                                        "ascii"
                                    )
                                ).hexdigest(),
                            }
                        ],
                    },
                    "metrics": deepcopy(ZERO_METRICS),
                    "evidence_refs": [],
                    "performed_actions": [],
                }
            )
    return runs


def make_aggregate() -> dict:
    return aggregate_runs(make_suite(), make_runs())


def make_baseline() -> dict:
    return build_baseline(
        make_aggregate(),
        suite=make_suite(),
        approval_ref="agent-quality-baseline-test",
        created_at="2026-07-26T12:00:00Z",
        evidence_refs=["local/agent-quality/safe-summary.json"],
    )


def test_aggregate_complete_suite_is_deterministic_and_safe() -> None:
    runs = make_runs()
    first = aggregate_runs(make_suite(), runs)
    second = aggregate_runs(make_suite(), list(reversed(runs)))

    assert first == second
    assert first["status"] == "PASS"
    assert first["reason_codes"] == []
    assert first["task_count"] == 5
    assert first["run_count"] == 19
    assert len(first["suite_manifest_hash"]) == 64
    assert first["metrics"]["strict_pass_3_task_rate"] == 1.0
    assert first["metrics"]["strict_pass_5_critical_rate"] == 1.0
    assert first["metrics"]["holdout_passed_count"] == 19
    assert first["source_basis"] == {
        "harness_commit": "1" * 40,
        "target_commit": "9" * 40,
    }
    assert first["performed_actions"] == []
    assert len(first["run_manifest_hash"]) == 64
    assert len(first["run_evidence_manifest"]) == 19
    assert first["run_manifest_hash"] == sha256_json(
        first["run_evidence_manifest"]
    )
    assert set(first["run_evidence_manifest"][0]) == {
        "run_id",
        "task_id",
        "trial_id",
        "criticality",
        "run_hash",
        "run_fingerprint_id",
        "work_package_plan_digest",
        "strict_pass",
        "holdout_status",
    }
    serialized = json.dumps(first, sort_keys=True)
    assert "evidence_refs" not in serialized
    assert "raw" not in serialized.lower()


def test_aggregate_preserves_read_only_legacy_suite_compatibility() -> None:
    suite = make_suite()
    runs = make_runs()
    plan_by_task = {
        run["task_id"]: run["fingerprint"]["work_package_plan_digest"]
        for run in runs
    }
    for task in suite["tasks"]:
        task.pop("invariant_grader_id")
        task.pop("required_invariant_ids")
        task.pop("verification_contract")
        task["work_package_plan_digest"] = plan_by_task[task["task_id"]]
    for run in runs:
        run["execution"] = {"status": "PASS", "reason_codes": []}
        run["grading"].pop("invariant_results")

    aggregate = aggregate_runs(suite, runs)

    assert aggregate["status"] == "PASS"
    assert aggregate["run_count"] == 19


@pytest.mark.parametrize(
    "mutation",
    ["hash", "interpreter", "required_commands", "incomplete"],
)
def test_aggregate_rejects_verification_contract_drift(mutation: str) -> None:
    runs = make_runs()
    execution = runs[0]["execution"]
    if mutation == "hash":
        execution["verification_contract_hash"] = "f" * 64
    elif mutation == "interpreter":
        execution["interpreter_id"] = "python-3.12.13-pytest-8.0.0"
    elif mutation == "required_commands":
        execution["required_command_ids"] = ["other"]
    else:
        execution["completed_command_ids"] = []

    with pytest.raises(ValueError):
        aggregate_runs(make_suite(), runs)


@pytest.mark.parametrize(
    "mutation",
    ["missing", "extra", "duplicate", "grader", "hash"],
)
def test_aggregate_binds_required_invariants_to_grader_evidence(
    mutation: str,
) -> None:
    runs = make_runs()
    results = runs[0]["grading"]["invariant_results"]
    if mutation == "missing":
        runs[0]["grading"].pop("invariant_results")
    elif mutation == "extra":
        results.append(
            {
                "invariant_id": "UNDECLARED_INVARIANT",
                "grader_id": results[0]["grader_id"],
                "status": "PASS",
                "result_hash": "a" * 64,
            }
        )
    elif mutation == "duplicate":
        results.append(deepcopy(results[0]))
    elif mutation == "grader":
        results[0]["grader_id"] = "other-grader"
    else:
        results[0]["result_hash"] = "not-a-hash"

    with pytest.raises((TypeError, ValueError)):
        aggregate_runs(make_suite(), runs)


@pytest.mark.parametrize("status", ["FAIL", "NOT RUN"])
def test_invariant_failure_or_not_run_blocks_strict_pass(status: str) -> None:
    runs = make_runs()
    runs[0]["grading"]["invariant_results"][0]["status"] = status

    aggregate = aggregate_runs(make_suite(), runs)

    assert aggregate["status"] == "HOLD"
    assert aggregate["metrics"]["strict_pass_3_task_rate"] == pytest.approx(2 / 3)
    assert aggregate["reason_codes"] == ["STRICT_PASS_3_TASK_RATE_BELOW_ONE"]


@pytest.mark.parametrize("unsafe_path", ["CON", "src/" + "a" * 256])
def test_suite_write_set_uses_shared_windows_safe_path_policy(
    unsafe_path: str,
) -> None:
    suite = make_suite()
    suite["tasks"][0]["write_set"] = [unsafe_path]

    with pytest.raises(ValueError, match="write_set"):
        aggregate_runs(suite, make_runs())


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "extra"])
def test_aggregate_rejects_invalid_trial_budget(mutation: str) -> None:
    runs = make_runs()
    if mutation == "duplicate":
        runs[-1] = deepcopy(runs[0])
    elif mutation == "missing":
        runs.pop()
    else:
        extra = deepcopy(runs[0])
        extra["run_id"] = "extra-run"
        extra["task_id"] = "extra-task"
        extra["trial_id"] = "extra-trial"
        runs.append(extra)

    with pytest.raises(ValueError):
        aggregate_runs(make_suite(), runs)


@pytest.mark.parametrize("mutation", ["partial", "second_configuration"])
def test_aggregate_requires_one_full_configuration(mutation: str) -> None:
    runs = make_runs()
    if mutation == "partial":
        runs[0]["fingerprint"]["comparability"] = "PARTIAL"
    else:
        runs[0]["fingerprint"]["configuration_id"] = "d" * 64

    with pytest.raises(ValueError):
        aggregate_runs(make_suite(), runs)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("target_base_commit", "a" * 40),
        ("contract_basis_sha", "b" * 40),
        ("work_package_plan_digest", "c" * 64),
        ("task_contract_hash", "d" * 64),
    ],
)
def test_aggregate_binds_run_fingerprint_to_declared_task(
    field: str, value: str
) -> None:
    runs = make_runs()
    base = {
        key: value
        for key, value in runs[0]["fingerprint"].items()
        if key
        not in {
            "configuration_id",
            "run_fingerprint_id",
            "comparability",
            "unknown_fields",
        }
    }
    base[field] = value
    runs[0]["fingerprint"] = normalize_fingerprint(base)

    with pytest.raises(ValueError):
        aggregate_runs(make_suite(), runs)


def test_aggregate_binds_run_task_class_to_declared_lane() -> None:
    runs = make_runs()
    runs[0]["task_class"] = "integration"

    with pytest.raises(ValueError):
        aggregate_runs(make_suite(), runs)


@pytest.mark.parametrize("count", [0, 2])
def test_aggregate_requires_exactly_one_holdout_per_run(count: int) -> None:
    runs = make_runs()
    runs[0]["metrics"]["holdout_passed_count"] = count

    with pytest.raises(ValueError, match="holdout"):
        aggregate_runs(make_suite(), runs)


@pytest.mark.parametrize("mutation", ["missing_suite_key", "missing_task_key", "extra_task_key"])
def test_aggregate_rejects_suite_contract_drift(mutation: str) -> None:
    suite = make_suite()
    if mutation == "missing_suite_key":
        suite.pop("status")
    elif mutation == "missing_task_key":
        suite["tasks"][0].pop("verification_contract")
    else:
        suite["tasks"][0]["unexpected"] = True

    with pytest.raises(ValueError):
        aggregate_runs(suite, make_runs())


def test_aggregate_computes_empirical_task_rates_and_summed_metrics() -> None:
    runs = make_runs()
    failed = next(run for run in runs if run["task_id"] == "normal-a")
    failed["execution"]["status"] = "FAIL"
    failed["metrics"]["scope_violation_count"] = 2

    aggregate = aggregate_runs(make_suite(), runs)

    assert aggregate["status"] == "HOLD"
    assert aggregate["metrics"]["strict_pass_3_task_rate"] == pytest.approx(2 / 3)
    assert aggregate["metrics"]["strict_pass_5_critical_rate"] == 1.0
    assert aggregate["metrics"]["scope_violation_count"] == 2
    assert aggregate["reason_codes"] == [
        "STRICT_PASS_3_TASK_RATE_BELOW_ONE",
        "SCOPE_VIOLATIONS_PRESENT",
    ]


def test_build_baseline_is_pure_and_schema_shaped(tmp_path) -> None:
    before = list(tmp_path.iterdir())
    baseline = make_baseline()

    assert list(tmp_path.iterdir()) == before
    assert baseline["decision"] == "PROVISIONAL_BASELINE_ACCEPTED"
    assert baseline["status"] == "PASS WITH NOTES"
    assert baseline["run_count"] == 19
    assert baseline["task_count"] == 5
    assert baseline["release_artifact"] is False
    assert baseline["performed_actions"] == ["local_write"]
    assert baseline["baseline_id"].startswith("agent-quality-")


def test_build_baseline_rejects_ineligible_aggregate() -> None:
    aggregate = make_aggregate()
    aggregate["metrics"]["strict_pass_5_critical_rate"] = 0.8

    with pytest.raises(ValueError, match="not eligible"):
        build_baseline(
            aggregate,
            suite=make_suite(),
            approval_ref="approval",
            created_at="2026-07-26T12:00:00Z",
        )


def test_build_baseline_rejects_fabricated_summary_and_manifest_drift() -> None:
    aggregate = make_aggregate()
    aggregate["task_count"] = 1
    aggregate["run_count"] = 1
    aggregate["metrics"]["holdout_passed_count"] = 1
    aggregate["run_evidence_manifest"] = aggregate["run_evidence_manifest"][:1]
    aggregate["run_manifest_hash"] = sha256_json(aggregate["run_evidence_manifest"])

    with pytest.raises(ValueError, match="not eligible"):
        build_baseline(
            aggregate,
            suite=make_suite(),
            approval_ref="approval",
            created_at="2026-07-26T12:00:00Z",
        )

    aggregate = make_aggregate()
    aggregate["run_evidence_manifest"][0]["strict_pass"] = False
    aggregate["run_manifest_hash"] = sha256_json(aggregate["run_evidence_manifest"])
    with pytest.raises(ValueError, match="not eligible"):
        build_baseline(
            aggregate,
            suite=make_suite(),
            approval_ref="approval",
            created_at="2026-07-26T12:00:00Z",
        )

    aggregate = make_aggregate()
    aggregate["metrics"]["holdout_passed_count"] = 1
    aggregate["metrics"]["holdout_failed_count"] = 0
    with pytest.raises(ValueError, match="not eligible"):
        build_baseline(
            aggregate,
            suite=make_suite(),
            approval_ref="approval",
            created_at="2026-07-26T12:00:00Z",
        )

    aggregate = make_aggregate()
    aggregate["metrics"]["holdout_passed_count"] = 0
    with pytest.raises(ValueError, match="not eligible"):
        build_baseline(
            aggregate,
            suite=make_suite(),
            approval_ref="approval",
            created_at="2026-07-26T12:00:00Z",
        )


def test_compare_adopts_equal_or_better_quality() -> None:
    baseline = make_baseline()
    candidate = make_aggregate()
    candidate["configuration_id"] = "d" * 64

    result = compare_baseline(baseline, candidate, suite=make_suite())

    assert result["decision"] == "ADOPT"
    assert result["status"] == "PASS"
    assert result["reason_codes"] == []
    assert result["performed_actions"] == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("critical_failure_count", 1),
        ("scope_violation_count", 1),
        ("safety_violation_count", 1),
        ("contract_reopen_count", 1),
        ("semantic_blocker_count", 1),
        ("strict_pass_3_task_rate", 0.5),
        ("postflight_block_count", 1),
        ("integration_fix_line_count", 1),
        ("holdout_failed_count", 1),
    ],
)
def test_compare_rejects_quality_regressions(field: str, value: int | float) -> None:
    baseline = make_baseline()
    candidate = make_aggregate()
    candidate["configuration_id"] = "d" * 64
    candidate["metrics"][field] = value
    reason_by_field = {
        "critical_failure_count": "CRITICAL_FAILURES_PRESENT",
        "scope_violation_count": "SCOPE_VIOLATIONS_PRESENT",
        "safety_violation_count": "SAFETY_VIOLATIONS_PRESENT",
        "contract_reopen_count": "CONTRACT_REOPENS_PRESENT",
        "semantic_blocker_count": "SEMANTIC_BLOCKERS_PRESENT",
        "strict_pass_3_task_rate": "STRICT_PASS_3_TASK_RATE_BELOW_ONE",
        "postflight_block_count": "POSTFLIGHT_BLOCKS_PRESENT",
        "holdout_failed_count": "HOLDOUT_FAILURES_PRESENT",
    }
    if field == "strict_pass_3_task_rate":
        candidate["metrics"][field] = 2 / 3
        for entry in candidate["run_evidence_manifest"]:
            if entry["task_id"] == "normal-a":
                entry["strict_pass"] = False
    if field == "holdout_failed_count":
        candidate["metrics"]["holdout_passed_count"] -= int(value)
        candidate["run_evidence_manifest"][0]["holdout_status"] = "FAIL"
    candidate["run_manifest_hash"] = sha256_json(
        candidate["run_evidence_manifest"]
    )
    if field in reason_by_field:
        candidate["status"] = "HOLD"
        candidate["reason_codes"] = [reason_by_field[field]]

    result = compare_baseline(baseline, candidate, suite=make_suite())

    assert result["decision"] == "REJECT"
    assert result["status"] == "REJECT"
    assert field in result["regression_metric_ids"]


def test_compare_holds_partial_configuration() -> None:
    baseline = make_baseline()
    candidate = make_aggregate()
    candidate["configuration_id"] = "d" * 64
    candidate["comparability"] = "PARTIAL"
    candidate["status"] = "HOLD"
    candidate["reason_codes"] = ["CONFIGURATION_COMPARABILITY_NOT_FULL"]

    result = compare_baseline(baseline, candidate, suite=make_suite())

    assert result["decision"] == "HOLD"
    assert result["reason_codes"] == ["CONFIGURATION_COMPARABILITY_NOT_FULL"]


def test_compare_rejects_missing_comparability() -> None:
    baseline = make_baseline()
    candidate = make_aggregate()
    candidate.pop("comparability")

    with pytest.raises(ValueError, match="key set"):
        compare_baseline(baseline, candidate, suite=make_suite())


def test_compare_holds_suite_manifest_mismatch() -> None:
    baseline = make_baseline()
    candidate = make_aggregate()
    baseline["suite_manifest_hash"] = "d" * 64
    baseline["baseline_id"] = "agent-quality-" + sha256_json(
        {
            "configuration_id": baseline["configuration_id"],
            "created_at": baseline["created_at"],
            "run_manifest_hash": baseline["run_manifest_hash"],
            "suite_id": baseline["suite_id"],
            "suite_manifest_hash": baseline["suite_manifest_hash"],
        }
    )[:24]

    with pytest.raises(ValueError, match="suite manifest hash"):
        compare_baseline(baseline, candidate, suite=make_suite())


def test_compare_does_not_evaluate_regression_when_suite_mismatches() -> None:
    baseline = make_baseline()
    baseline["suite_manifest_hash"] = "d" * 64
    baseline["baseline_id"] = "agent-quality-" + sha256_json(
        {
            "configuration_id": baseline["configuration_id"],
            "created_at": baseline["created_at"],
            "run_manifest_hash": baseline["run_manifest_hash"],
            "suite_id": baseline["suite_id"],
            "suite_manifest_hash": baseline["suite_manifest_hash"],
        }
    )[:24]
    candidate = make_aggregate()
    candidate["metrics"]["scope_violation_count"] = 1
    candidate["status"] = "HOLD"
    candidate["reason_codes"] = ["SCOPE_VIOLATIONS_PRESENT"]

    with pytest.raises(ValueError, match="suite manifest hash"):
        compare_baseline(baseline, candidate, suite=make_suite())


def test_compare_rejects_self_consistent_manifest_for_wrong_suite_task() -> None:
    baseline = make_baseline()
    candidate = make_aggregate()
    baseline["run_evidence_manifest"][0]["task_id"] = "unknown-task"
    baseline["run_evidence_manifest"].sort(
        key=lambda item: (item["task_id"], item["trial_id"], item["run_id"])
    )
    baseline["run_manifest_hash"] = sha256_json(
        baseline["run_evidence_manifest"]
    )
    baseline["baseline_id"] = "agent-quality-" + sha256_json(
        {
            "configuration_id": baseline["configuration_id"],
            "created_at": baseline["created_at"],
            "run_manifest_hash": baseline["run_manifest_hash"],
            "suite_id": baseline["suite_id"],
            "suite_manifest_hash": baseline["suite_manifest_hash"],
        }
    )[:24]

    with pytest.raises(ValueError, match="unknown task"):
        compare_baseline(baseline, candidate, suite=make_suite())


@pytest.mark.parametrize("measurement", ["duration_seconds", "cost_units"])
def test_compare_routes_operational_measurements_to_owner(
    measurement: str,
) -> None:
    baseline = make_baseline()
    candidate = make_aggregate()
    candidate["configuration_id"] = "d" * 64
    candidate[measurement] = 1

    result = compare_baseline(baseline, candidate, suite=make_suite())

    assert result["decision"] == "HOLD"
    assert result["owner_decision_required"] is True
    assert result["reason_codes"] == ["OWNER_DECISION_REQUIRED"]
    assert measurement not in json.dumps(result)
