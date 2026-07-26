from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from scripts.agent_quality_lib.contracts import sha256_json, validate_run


_SUMMED_METRICS = (
    "critical_failure_count",
    "scope_violation_count",
    "safety_violation_count",
    "postflight_block_count",
    "contract_reopen_count",
    "semantic_blocker_count",
    "integration_fix_file_count",
    "integration_fix_line_count",
    "holdout_passed_count",
    "holdout_failed_count",
)

_STRICT_BLOCKERS = (
    "critical_failure_count",
    "scope_violation_count",
    "safety_violation_count",
    "postflight_block_count",
    "contract_reopen_count",
    "semantic_blocker_count",
    "holdout_failed_count",
)

_GRADE_FIELDS = (
    "functional_correctness",
    "contract_adherence",
    "scope_adherence",
    "semantic_consistency",
    "architectural_consistency",
    "safety_compliance",
    "reproducibility",
)


def _validated_run(run: Mapping[str, Any]) -> dict[str, Any]:
    candidate = dict(run)
    validated = validate_run(candidate)
    if validated is None:
        return candidate
    if not isinstance(validated, Mapping):
        raise ValueError("validate_run must return a mapping or None")
    return dict(validated)


def _suite_tasks(suite: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    tasks = suite.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("suite tasks must be a non-empty list")

    by_id: dict[str, dict[str, Any]] = {}
    total_trials = 0
    for task in tasks:
        if not isinstance(task, Mapping):
            raise ValueError("suite task must be an object")
        task_id = task.get("task_id")
        trials = task.get("trials")
        criticality = task.get("criticality")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("suite task_id must be a non-empty string")
        if task_id in by_id:
            raise ValueError(f"duplicate suite task_id: {task_id}")
        if not isinstance(trials, int) or isinstance(trials, bool) or trials <= 0:
            raise ValueError(f"invalid trial budget for task: {task_id}")
        if criticality not in {"normal", "critical"}:
            raise ValueError(f"invalid criticality for task: {task_id}")
        by_id[task_id] = dict(task)
        total_trials += trials

    declared_total = suite.get("total_trials")
    if declared_total != total_trials:
        raise ValueError("suite total_trials does not match task budgets")
    return by_id


def _is_strict_pass(run: Mapping[str, Any]) -> bool:
    if run["execution"]["status"] != "PASS":
        return False
    grading = run["grading"]
    if grading["blocker_count"] != 0:
        return False
    if any(grading[field] != "PASS" for field in _GRADE_FIELDS):
        return False
    metrics = run["metrics"]
    return all(metrics[field] == 0 for field in _STRICT_BLOCKERS)


def _rate_for_group(
    tasks: Mapping[str, Mapping[str, Any]],
    runs_by_task: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    trials: int,
    criticality: str,
) -> float:
    task_ids = [
        task_id
        for task_id, task in tasks.items()
        if task["trials"] == trials and task["criticality"] == criticality
    ]
    if not task_ids:
        raise ValueError(
            f"suite has no {criticality} tasks with a {trials}-trial budget"
        )
    strict_tasks = sum(
        all(_is_strict_pass(run) for run in runs_by_task[task_id])
        for task_id in task_ids
    )
    return strict_tasks / len(task_ids)


def _reason_codes(metrics: Mapping[str, int | float]) -> list[str]:
    reasons: list[str] = []
    if metrics["strict_pass_3_task_rate"] < 1.0:
        reasons.append("STRICT_PASS_3_TASK_RATE_BELOW_ONE")
    if metrics["strict_pass_5_critical_rate"] < 1.0:
        reasons.append("STRICT_PASS_5_CRITICAL_RATE_BELOW_ONE")
    for field, reason in (
        ("critical_failure_count", "CRITICAL_FAILURES_PRESENT"),
        ("scope_violation_count", "SCOPE_VIOLATIONS_PRESENT"),
        ("safety_violation_count", "SAFETY_VIOLATIONS_PRESENT"),
        ("postflight_block_count", "POSTFLIGHT_BLOCKS_PRESENT"),
        ("contract_reopen_count", "CONTRACT_REOPENS_PRESENT"),
        ("semantic_blocker_count", "SEMANTIC_BLOCKERS_PRESENT"),
        ("holdout_failed_count", "HOLDOUT_FAILURES_PRESENT"),
    ):
        if metrics[field] > 0:
            reasons.append(reason)
    return reasons


def aggregate_runs(
    suite: Mapping[str, Any], runs: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Aggregate one complete, comparable suite without retaining raw run data."""

    if not isinstance(suite, Mapping):
        raise ValueError("suite must be an object")
    if not isinstance(runs, Sequence) or isinstance(runs, (str, bytes, bytearray)):
        raise ValueError("runs must be a sequence")

    suite_id = suite.get("suite_id")
    if not isinstance(suite_id, str) or not suite_id:
        raise ValueError("suite_id must be a non-empty string")
    tasks = _suite_tasks(suite)

    validated_runs = [_validated_run(run) for run in runs]
    expected_total = sum(task["trials"] for task in tasks.values())
    if len(validated_runs) != expected_total:
        raise ValueError("run count does not match the suite trial budget")

    run_ids: set[str] = set()
    trial_keys: set[tuple[str, str]] = set()
    runs_by_task: dict[str, list[dict[str, Any]]] = {
        task_id: [] for task_id in tasks
    }
    configuration_ids: set[str] = set()
    manifest: list[dict[str, str]] = []

    for run in validated_runs:
        run_id = run["run_id"]
        task_id = run["task_id"]
        trial_id = run["trial_id"]
        if run["suite_id"] != suite_id:
            raise ValueError("run suite_id does not match the suite")
        if task_id not in tasks:
            raise ValueError(f"extra run task_id: {task_id}")
        if run["criticality"] != tasks[task_id]["criticality"]:
            raise ValueError(f"run criticality does not match task: {task_id}")
        if run_id in run_ids:
            raise ValueError(f"duplicate run_id: {run_id}")
        trial_key = (task_id, trial_id)
        if trial_key in trial_keys:
            raise ValueError(f"duplicate task/trial pair: {task_id}/{trial_id}")
        run_ids.add(run_id)
        trial_keys.add(trial_key)
        runs_by_task[task_id].append(run)

        fingerprint = run["fingerprint"]
        if fingerprint["comparability"] != "FULL":
            raise ValueError("all runs must have FULL comparability")
        configuration_ids.add(fingerprint["configuration_id"])
        manifest.append(
            {
                "run_hash": sha256_json(run),
                "run_id": run_id,
                "run_fingerprint_id": fingerprint["run_fingerprint_id"],
                "task_id": task_id,
                "trial_id": trial_id,
            }
        )

    if len(configuration_ids) != 1:
        raise ValueError("runs must use exactly one configuration_id")

    actual_counts = Counter(
        run["task_id"] for run in validated_runs
    )
    for task_id, task in tasks.items():
        if actual_counts[task_id] != task["trials"]:
            raise ValueError(f"missing or extra trials for task: {task_id}")

    metrics: dict[str, int | float] = {
        "strict_pass_3_task_rate": _rate_for_group(
            tasks, runs_by_task, trials=3, criticality="normal"
        ),
        "strict_pass_5_critical_rate": _rate_for_group(
            tasks, runs_by_task, trials=5, criticality="critical"
        ),
    }
    for field in _SUMMED_METRICS:
        metrics[field] = sum(run["metrics"][field] for run in validated_runs)

    reasons = _reason_codes(metrics)
    return {
        "schema_version": "1",
        "status": "PASS" if not reasons else "HOLD",
        "reason_codes": reasons,
        "suite_id": suite_id,
        "configuration_id": configuration_ids.pop(),
        "comparability": "FULL",
        "task_count": len(tasks),
        "run_count": len(validated_runs),
        "metrics": metrics,
        "run_manifest_hash": sha256_json(
            sorted(
                manifest,
                key=lambda item: (
                    item["task_id"],
                    item["trial_id"],
                    item["run_id"],
                ),
            )
        ),
        "performed_actions": [],
    }
