from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import re
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
_GIT_SHA = re.compile(r"^[0-9a-f]{40,64}$")
_HASH = re.compile(r"^[0-9a-f]{64}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_SAFE_PATH = re.compile(r"^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$")
_SUITE_KEYS = {
    "schema_version",
    "status",
    "suite_class",
    "suite_id",
    "required_configuration",
    "target_checkpoint",
    "tasks",
    "total_trials",
}
_TASK_KEYS = {
    "criticality",
    "lane",
    "source_basis",
    "task_id",
    "trials",
    "work_package_plan_digest",
    "write_set",
}
_REQUIRED_CONFIGURATION_KEYS = {
    "agent_adapter_id",
    "agent_adapter_version",
    "environment_profile_id",
    "model_id",
    "reasoning_profile",
}
_AGGREGATE_KEYS = {
    "schema_version",
    "status",
    "reason_codes",
    "suite_id",
    "suite_manifest_hash",
    "configuration_id",
    "comparability",
    "source_basis",
    "task_count",
    "run_count",
    "metrics",
    "run_manifest_hash",
    "performed_actions",
}
_OPTIONAL_OPERATIONAL_KEYS = {"duration_seconds", "cost_units", "operational_metrics"}
_EXPECTED_HOLDOUTS_PER_RUN = 1


def _safe_path(value: Any) -> bool:
    if not isinstance(value, str) or not _SAFE_PATH.fullmatch(value):
        return False
    parts = value.split("/")
    return all(part not in {".", ".."} and not part.endswith(".") for part in parts)


def _safe_string_list(value: Any, *, path: bool = False) -> bool:
    if not isinstance(value, list) or not value or len(value) != len(set(value)):
        return False
    validator = _safe_path if path else lambda item: isinstance(item, str) and bool(_SAFE_ID.fullmatch(item))
    return all(validator(item) for item in value)


def _validated_run(run: Mapping[str, Any]) -> dict[str, Any]:
    candidate = dict(run)
    validated = validate_run(candidate)
    if validated is None:
        return candidate
    if not isinstance(validated, Mapping):
        raise ValueError("validate_run must return a mapping or None")
    return dict(validated)


def _suite_tasks(suite: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if set(suite) != _SUITE_KEYS:
        raise ValueError("suite key set is invalid")
    if suite.get("schema_version") != "1" or suite.get("status") != "READY":
        raise ValueError("suite metadata is invalid")
    if suite.get("suite_class") != "agentic_regression":
        raise ValueError("suite class is invalid")
    required_configuration = suite.get("required_configuration")
    if (
        not isinstance(required_configuration, Mapping)
        or set(required_configuration) != _REQUIRED_CONFIGURATION_KEYS
        or any(
            not isinstance(value, str) or not _SAFE_ID.fullmatch(value)
            for value in required_configuration.values()
        )
    ):
        raise ValueError("suite required_configuration is invalid")

    tasks = suite.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("suite tasks must be a non-empty list")

    by_id: dict[str, dict[str, Any]] = {}
    total_trials = 0
    for task in tasks:
        if not isinstance(task, Mapping):
            raise ValueError("suite task must be an object")
        lane = task.get("lane")
        expected_keys = _TASK_KEYS | ({"fixture_recipe"} if lane == "integration" else set())
        if set(task) != expected_keys:
            raise ValueError("suite task key set is invalid")
        task_id = task.get("task_id")
        trials = task.get("trials")
        criticality = task.get("criticality")
        if not isinstance(task_id, str) or not _SAFE_ID.fullmatch(task_id):
            raise ValueError("suite task_id must be a non-empty string")
        if task_id in by_id:
            raise ValueError(f"duplicate suite task_id: {task_id}")
        if not isinstance(trials, int) or isinstance(trials, bool) or trials <= 0:
            raise ValueError(f"invalid trial budget for task: {task_id}")
        if criticality not in {"normal", "critical"}:
            raise ValueError(f"invalid criticality for task: {task_id}")
        if lane not in {"feature", "integration"}:
            raise ValueError(f"invalid lane for task: {task_id}")
        if not isinstance(task.get("source_basis"), str) or not _GIT_SHA.fullmatch(
            task["source_basis"]
        ):
            raise ValueError(f"invalid source_basis for task: {task_id}")
        if not isinstance(task.get("work_package_plan_digest"), str) or not _HASH.fullmatch(
            task["work_package_plan_digest"]
        ):
            raise ValueError(f"invalid work-package digest for task: {task_id}")
        if not _safe_string_list(task.get("write_set"), path=True):
            raise ValueError(f"invalid write_set for task: {task_id}")
        if lane == "integration":
            recipe = task["fixture_recipe"]
            if (
                not isinstance(recipe, Mapping)
                or set(recipe) != {"base", "lane_commits"}
                or recipe.get("base") != task["source_basis"]
                or not isinstance(recipe.get("lane_commits"), list)
                or not recipe["lane_commits"]
                or len(recipe["lane_commits"]) != len(set(recipe["lane_commits"]))
                or any(
                    not isinstance(commit, str) or not _GIT_SHA.fullmatch(commit)
                    for commit in recipe["lane_commits"]
                )
            ):
                raise ValueError(f"invalid fixture_recipe for task: {task_id}")
        by_id[task_id] = dict(task)
        total_trials += trials

    declared_total = suite.get("total_trials")
    if declared_total != total_trials:
        raise ValueError("suite total_trials does not match task budgets")
    return by_id


def _validated_metrics(value: Any) -> dict[str, int | float]:
    expected = {"strict_pass_3_task_rate", "strict_pass_5_critical_rate", *_SUMMED_METRICS}
    if not isinstance(value, Mapping) or set(value) != expected:
        raise ValueError("aggregate metrics key set is invalid")
    metrics = dict(value)
    for field in ("strict_pass_3_task_rate", "strict_pass_5_critical_rate"):
        metric = metrics[field]
        if (
            not isinstance(metric, (int, float))
            or isinstance(metric, bool)
            or not 0.0 <= metric <= 1.0
        ):
            raise ValueError(f"aggregate metric is invalid: {field}")
    for field in _SUMMED_METRICS:
        metric = metrics[field]
        if not isinstance(metric, int) or isinstance(metric, bool) or metric < 0:
            raise ValueError(f"aggregate metric is invalid: {field}")
    return metrics


def validate_aggregate_record(
    record: Mapping[str, Any], *, allow_operational: bool = False
) -> dict[str, Any]:
    """Validate one safe aggregate record before adoption or comparison."""

    if not isinstance(record, Mapping):
        raise ValueError("aggregate must be an object")
    keys = set(record)
    optional = keys - _AGGREGATE_KEYS
    if keys - optional != _AGGREGATE_KEYS or (
        optional and (not allow_operational or not optional <= _OPTIONAL_OPERATIONAL_KEYS)
    ):
        raise ValueError("aggregate key set is invalid")
    if record.get("schema_version") != "1":
        raise ValueError("aggregate schema_version is invalid")
    for field in ("suite_id",):
        if not isinstance(record.get(field), str) or not _SAFE_ID.fullmatch(record[field]):
            raise ValueError(f"aggregate {field} is invalid")
    for field in ("suite_manifest_hash", "configuration_id", "run_manifest_hash"):
        if not isinstance(record.get(field), str) or not _HASH.fullmatch(record[field]):
            raise ValueError(f"aggregate {field} is invalid")
    if record.get("comparability") not in {"FULL", "PARTIAL"}:
        raise ValueError("aggregate comparability is invalid")
    source_basis = record.get("source_basis")
    if (
        not isinstance(source_basis, Mapping)
        or set(source_basis) != {"harness_commit", "target_commit"}
        or any(
            not isinstance(value, str) or not _GIT_SHA.fullmatch(value)
            for value in source_basis.values()
        )
    ):
        raise ValueError("aggregate source_basis is invalid")
    for field in ("task_count", "run_count"):
        value = record.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"aggregate {field} is invalid")

    metrics = _validated_metrics(record.get("metrics"))
    if metrics["holdout_passed_count"] + metrics["holdout_failed_count"] != record["run_count"]:
        raise ValueError("aggregate holdout count is incomplete")
    expected_reasons = _reason_codes(metrics)
    if record["comparability"] != "FULL":
        expected_reasons.append("CONFIGURATION_COMPARABILITY_NOT_FULL")
    if record.get("reason_codes") != expected_reasons:
        raise ValueError("aggregate reason_codes are inconsistent")
    expected_status = "PASS" if not expected_reasons else "HOLD"
    if record.get("status") != expected_status:
        raise ValueError("aggregate status is inconsistent")
    if record.get("performed_actions") != []:
        raise ValueError("aggregate performed_actions must be empty")

    if optional:
        for field in optional - {"operational_metrics"}:
            value = record[field]
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or value < 0
            ):
                raise ValueError(f"aggregate operational field is invalid: {field}")
        if "operational_metrics" in record:
            operational = record["operational_metrics"]
            if (
                not isinstance(operational, Mapping)
                or not set(operational) <= {"duration_seconds", "cost_units"}
                or any(
                    not isinstance(value, (int, float))
                    or isinstance(value, bool)
                    or value < 0
                    for value in operational.values()
                )
            ):
                raise ValueError("aggregate operational_metrics is invalid")
    return dict(record)


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
    target_checkpoint = suite.get("target_checkpoint")
    if not isinstance(target_checkpoint, str) or not _GIT_SHA.fullmatch(
        target_checkpoint
    ):
        raise ValueError("suite target_checkpoint must be a commit identifier")
    required_configuration = suite.get("required_configuration", {})
    tasks = _suite_tasks(suite)
    suite_manifest_hash = sha256_json(suite)

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
    harness_commits: set[str] = set()
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
        task = tasks[task_id]
        fingerprint = run["fingerprint"]
        if run["task_class"] != task["lane"]:
            raise ValueError(f"run task_class does not match task lane: {task_id}")
        if fingerprint["target_base_commit"] != task["source_basis"]:
            raise ValueError(f"run target basis does not match task: {task_id}")
        if fingerprint["contract_basis_sha"] != task["source_basis"]:
            raise ValueError(f"run contract basis does not match task: {task_id}")
        if fingerprint["work_package_plan_digest"] != task["work_package_plan_digest"]:
            raise ValueError(f"run plan digest does not match task: {task_id}")
        if fingerprint["verification_suite_id"] != suite_id:
            raise ValueError(f"run verification suite does not match: {task_id}")
        holdout_count = (
            run["metrics"]["holdout_passed_count"]
            + run["metrics"]["holdout_failed_count"]
        )
        if holdout_count != _EXPECTED_HOLDOUTS_PER_RUN:
            raise ValueError(f"run holdout count is incomplete: {task_id}")
        if run_id in run_ids:
            raise ValueError(f"duplicate run_id: {run_id}")
        trial_key = (task_id, trial_id)
        if trial_key in trial_keys:
            raise ValueError(f"duplicate task/trial pair: {task_id}/{trial_id}")
        run_ids.add(run_id)
        trial_keys.add(trial_key)
        runs_by_task[task_id].append(run)

        if fingerprint["comparability"] != "FULL":
            raise ValueError("all runs must have FULL comparability")
        for field, expected in required_configuration.items():
            if fingerprint.get(field) != expected:
                raise ValueError(f"run configuration mismatch: {field}")
        configuration_ids.add(fingerprint["configuration_id"])
        harness_commits.add(fingerprint["harness_commit"])
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
    if len(harness_commits) != 1:
        raise ValueError("runs must use exactly one harness_commit")

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
    result = {
        "schema_version": "1",
        "status": "PASS" if not reasons else "HOLD",
        "reason_codes": reasons,
        "suite_id": suite_id,
        "suite_manifest_hash": suite_manifest_hash,
        "configuration_id": configuration_ids.pop(),
        "comparability": "FULL",
        "source_basis": {
            "harness_commit": harness_commits.pop(),
            "target_commit": target_checkpoint,
        },
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
    return validate_aggregate_record(result)
