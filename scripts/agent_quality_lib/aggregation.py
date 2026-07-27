from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import re
from typing import Any

from scripts.agent_quality_lib.contracts import sha256_json, validate_run
from scripts.repo_path_policy import safe_repo_path as shared_safe_repo_path


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
    "invariant_grader_id",
    "lane",
    "required_invariant_ids",
    "source_basis",
    "task_id",
    "trials",
    "verification_contract",
    "write_set",
}
_UNBOUND_TASK_KEYS = _TASK_KEYS - {"invariant_grader_id"}
_LEGACY_TASK_KEYS = {
    "criticality",
    "lane",
    "source_basis",
    "task_id",
    "trials",
    "work_package_plan_digest",
    "write_set",
}
_VERIFICATION_CONTRACT_KEYS = {"interpreter_id", "commands"}
_VERIFICATION_COMMAND_KEYS = {"command_id", "argv"}
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
    "run_evidence_manifest",
    "run_manifest_hash",
    "performed_actions",
}
_RUN_EVIDENCE_KEYS = {
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
_OPTIONAL_OPERATIONAL_KEYS = {"duration_seconds", "cost_units", "operational_metrics"}
_EXPECTED_HOLDOUTS_PER_RUN = 1
_SUITE_V2_KEYS = (
    _SUITE_KEYS
    - {"required_configuration"}
    | {
        "profile_set_id",
        "profile_set_hash",
        "semantic_review_profile_id",
        "semantic_review_profile_hash",
    }
)
_TASK_V2_PROFILE_KEYS = {"agent_profile_id", "agent_profile_hash"}
_ROLE_AGGREGATE_KEYS = (
    _AGGREGATE_KEYS
    - {"configuration_id"}
    | {
        "profile_set_hash",
        "role_configuration_manifest",
        "system_configuration_id",
    }
)
_ROLE_CONFIGURATION_KEYS = {
    "agent_profile_id",
    "agent_profile_hash",
    "configuration_id",
    "run_count",
}
_RUN_EVIDENCE_V2_KEYS = _RUN_EVIDENCE_KEYS | {
    "agent_profile_id",
    "configuration_id",
}


def _safe_path(value: Any) -> bool:
    return shared_safe_repo_path(value, max_bytes=512)


def _safe_string_list(value: Any, *, path: bool = False) -> bool:
    if not isinstance(value, list) or not value or len(value) != len(set(value)):
        return False
    validator = _safe_path if path else lambda item: isinstance(item, str) and bool(_SAFE_ID.fullmatch(item))
    return all(validator(item) for item in value)


def _verification_contract(value: Any, *, task_id: str) -> dict[str, Any]:
    if (
        not isinstance(value, Mapping)
        or set(value) != _VERIFICATION_CONTRACT_KEYS
        or not isinstance(value.get("interpreter_id"), str)
        or not _SAFE_ID.fullmatch(value["interpreter_id"])
    ):
        raise ValueError(f"invalid verification contract for task: {task_id}")
    commands = value.get("commands")
    if not isinstance(commands, list) or not commands or len(commands) > 16:
        raise ValueError(f"invalid verification commands for task: {task_id}")
    command_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for command in commands:
        if (
            not isinstance(command, Mapping)
            or set(command) != _VERIFICATION_COMMAND_KEYS
        ):
            raise ValueError(f"invalid verification command for task: {task_id}")
        command_id = command.get("command_id")
        argv = command.get("argv")
        if (
            not isinstance(command_id, str)
            or not _SAFE_ID.fullmatch(command_id)
            or command_id in command_ids
            or not isinstance(argv, list)
            or not argv
            or len(argv) > 32
            or any(
                not isinstance(token, str)
                or not token
                or len(token.encode("utf-8")) > 512
                or any(character in token for character in ("\x00", "\r", "\n", "\t"))
                or "://" in token
                or "\\" in token
                or re.match(r"^[A-Za-z]:", token)
                for token in argv
            )
        ):
            raise ValueError(f"invalid verification command for task: {task_id}")
        command_ids.add(command_id)
        normalized.append({"command_id": command_id, "argv": list(argv)})
    return {
        "interpreter_id": value["interpreter_id"],
        "commands": normalized,
    }


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
        fixture_key = {"fixture_recipe"} if lane == "integration" else set()
        expected_keys = _TASK_KEYS | fixture_key
        unbound_keys = _UNBOUND_TASK_KEYS | fixture_key
        legacy_keys = _LEGACY_TASK_KEYS | fixture_key
        task_keys = frozenset(task)
        if task_keys not in {
            frozenset(expected_keys),
            frozenset(unbound_keys),
            frozenset(legacy_keys),
        }:
            raise ValueError("suite task key set is invalid")
        legacy = task_keys == frozenset(legacy_keys)
        invariant_bound = task_keys == frozenset(expected_keys)
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
        if not _safe_string_list(task.get("write_set"), path=True):
            raise ValueError(f"invalid write_set for task: {task_id}")
        if legacy:
            if (
                not isinstance(task.get("work_package_plan_digest"), str)
                or not _HASH.fullmatch(task["work_package_plan_digest"])
            ):
                raise ValueError(f"invalid work-package digest for task: {task_id}")
        else:
            if not _safe_string_list(task.get("required_invariant_ids")):
                raise ValueError(f"invalid required invariants for task: {task_id}")
            if invariant_bound and (
                not isinstance(task.get("invariant_grader_id"), str)
                or not _SAFE_ID.fullmatch(task["invariant_grader_id"])
            ):
                raise ValueError(f"invalid invariant grader for task: {task_id}")
            _verification_contract(
                task.get("verification_contract"),
                task_id=task_id,
            )
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


def _suite_tasks_v2(suite: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if set(suite) != _SUITE_V2_KEYS:
        raise ValueError("suite v2 key set is invalid")
    if (
        suite.get("schema_version") != "2"
        or suite.get("status") != "READY"
        or suite.get("suite_class") != "agentic_regression"
        or not isinstance(suite.get("profile_set_id"), str)
        or not _SAFE_ID.fullmatch(suite["profile_set_id"])
        or not isinstance(suite.get("profile_set_hash"), str)
        or not _HASH.fullmatch(suite["profile_set_hash"])
        or not isinstance(suite.get("semantic_review_profile_id"), str)
        or not _SAFE_ID.fullmatch(suite["semantic_review_profile_id"])
        or not isinstance(suite.get("semantic_review_profile_hash"), str)
        or not _HASH.fullmatch(suite["semantic_review_profile_hash"])
    ):
        raise ValueError("suite v2 metadata is invalid")
    raw_tasks = suite.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise ValueError("suite v2 tasks must be a non-empty list")

    stripped_tasks: list[dict[str, Any]] = []
    profile_bindings: dict[str, tuple[str, str]] = {}
    for task in raw_tasks:
        if not isinstance(task, Mapping) or not _TASK_V2_PROFILE_KEYS <= set(task):
            raise ValueError("suite v2 task profile binding is missing")
        profile_id = task.get("agent_profile_id")
        profile_hash = task.get("agent_profile_hash")
        if (
            not isinstance(profile_id, str)
            or not _SAFE_ID.fullmatch(profile_id)
            or not isinstance(profile_hash, str)
            or not _HASH.fullmatch(profile_hash)
        ):
            raise ValueError("suite v2 task profile binding is invalid")
        stripped = {
            key: value
            for key, value in task.items()
            if key not in _TASK_V2_PROFILE_KEYS
        }
        stripped_tasks.append(stripped)
        profile_bindings[str(task.get("task_id"))] = (profile_id, profile_hash)

    surrogate = {
        "schema_version": "1",
        "status": suite["status"],
        "suite_class": suite["suite_class"],
        "suite_id": suite["suite_id"],
        "required_configuration": {
            "agent_adapter_id": "role-aware",
            "agent_adapter_version": "2.0.0",
            "environment_profile_id": "windows-python-3.12.13",
            "model_id": "role-aware",
            "reasoning_profile": "role-aware",
        },
        "target_checkpoint": suite["target_checkpoint"],
        "tasks": stripped_tasks,
        "total_trials": suite["total_trials"],
    }
    tasks = _suite_tasks(surrogate)
    for task_id, task in tasks.items():
        profile_id, profile_hash = profile_bindings[task_id]
        task["agent_profile_id"] = profile_id
        task["agent_profile_hash"] = profile_hash
    return tasks


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


def _validated_run_evidence_manifest(
    record: Mapping[str, Any],
) -> list[dict[str, Any]]:
    value = record.get("run_evidence_manifest")
    if not isinstance(value, list) or not value:
        raise ValueError("run evidence manifest must be a non-empty list")

    manifest: list[dict[str, Any]] = []
    run_ids: set[str] = set()
    trial_keys: set[tuple[str, str]] = set()
    for entry in value:
        if not isinstance(entry, Mapping) or set(entry) != _RUN_EVIDENCE_KEYS:
            raise ValueError("run evidence manifest entry key set is invalid")
        for field in ("run_id", "task_id", "trial_id"):
            if not isinstance(entry.get(field), str) or not _SAFE_ID.fullmatch(
                entry[field]
            ):
                raise ValueError(f"run evidence manifest {field} is invalid")
        for field in ("run_hash", "run_fingerprint_id"):
            if not isinstance(entry.get(field), str) or not _HASH.fullmatch(
                entry[field]
            ):
                raise ValueError(f"run evidence manifest {field} is invalid")
        if (
            not isinstance(entry.get("work_package_plan_digest"), str)
            or not _HASH.fullmatch(entry["work_package_plan_digest"])
        ):
            raise ValueError("run evidence manifest plan digest is invalid")
        if entry.get("criticality") not in {"normal", "critical"}:
            raise ValueError("run evidence manifest criticality is invalid")
        if not isinstance(entry.get("strict_pass"), bool):
            raise ValueError("run evidence manifest strict_pass is invalid")
        if entry.get("holdout_status") not in {"PASS", "FAIL"}:
            raise ValueError("run evidence manifest holdout_status is invalid")

        run_id = entry["run_id"]
        trial_key = (entry["task_id"], entry["trial_id"])
        if run_id in run_ids:
            raise ValueError("run evidence manifest has duplicate run_id")
        if trial_key in trial_keys:
            raise ValueError("run evidence manifest has duplicate task/trial")
        run_ids.add(run_id)
        trial_keys.add(trial_key)
        manifest.append(dict(entry))

    expected_order = sorted(
        manifest,
        key=lambda item: (item["task_id"], item["trial_id"], item["run_id"]),
    )
    if manifest != expected_order:
        raise ValueError("run evidence manifest ordering is invalid")
    if len(manifest) != record.get("run_count"):
        raise ValueError("run evidence manifest count is invalid")
    if sha256_json(manifest) != record.get("run_manifest_hash"):
        raise ValueError("run evidence manifest hash is invalid")
    return manifest


def validate_manifest_binding(
    record: Mapping[str, Any], suite: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Cross-check a safe aggregate or baseline manifest against its suite."""

    tasks = _suite_tasks(suite)
    manifest = _validated_run_evidence_manifest(record)
    if record.get("suite_id") != suite.get("suite_id"):
        raise ValueError("record suite_id does not match suite")
    if record.get("suite_manifest_hash") != sha256_json(suite):
        raise ValueError("record suite manifest hash does not match suite")
    if record.get("task_count") != len(tasks):
        raise ValueError("record task count does not match suite")
    if record.get("run_count") != suite.get("total_trials"):
        raise ValueError("record run count does not match suite")
    source_basis = record.get("source_basis")
    if (
        not isinstance(source_basis, Mapping)
        or source_basis.get("target_commit") != suite.get("target_checkpoint")
    ):
        raise ValueError("record target source basis does not match suite")

    entries_by_task: dict[str, list[dict[str, Any]]] = {
        task_id: [] for task_id in tasks
    }
    for entry in manifest:
        task_id = entry["task_id"]
        if task_id not in tasks:
            raise ValueError("run evidence manifest has unknown task")
        task = tasks[task_id]
        if entry["criticality"] != task["criticality"]:
            raise ValueError("run evidence manifest criticality does not match suite")
        entries_by_task[task_id].append(entry)

    for task_id, task in tasks.items():
        if len(entries_by_task[task_id]) != task["trials"]:
            raise ValueError("run evidence manifest trial budget does not match suite")

    metrics = _validated_metrics(record.get("metrics"))
    holdout_passes = sum(
        entry["holdout_status"] == "PASS" for entry in manifest
    )
    holdout_failures = len(manifest) - holdout_passes
    if (
        metrics["holdout_passed_count"] != holdout_passes
        or metrics["holdout_failed_count"] != holdout_failures
    ):
        raise ValueError("run evidence manifest holdout totals are inconsistent")

    for trials, criticality, metric_id in (
        (3, "normal", "strict_pass_3_task_rate"),
        (5, "critical", "strict_pass_5_critical_rate"),
    ):
        task_ids = [
            task_id
            for task_id, task in tasks.items()
            if task["trials"] == trials and task["criticality"] == criticality
        ]
        if not task_ids:
            raise ValueError("suite has no task group for strict rate")
        expected_rate = sum(
            all(entry["strict_pass"] for entry in entries_by_task[task_id])
            for task_id in task_ids
        ) / len(task_ids)
        if metrics[metric_id] != expected_rate:
            raise ValueError("run evidence manifest strict rate is inconsistent")
    return manifest


def validate_aggregate_record(
    record: Mapping[str, Any],
    *,
    suite: Mapping[str, Any] | None = None,
    allow_operational: bool = False,
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
    _validated_run_evidence_manifest(record)
    if suite is not None:
        validate_manifest_binding(record, suite)

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
    if "invariant_results" in grading and any(
        result["status"] != "PASS" for result in grading["invariant_results"]
    ):
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


def _aggregate_runs_v1(
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
    plan_digests_by_task: dict[str, set[str]] = {
        task_id: set() for task_id in tasks
    }
    manifest: list[dict[str, Any]] = []

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
        if fingerprint["verification_suite_id"] != suite_id:
            raise ValueError(f"run verification suite does not match: {task_id}")
        execution = run["execution"]
        if "verification_contract" in task:
            verification_contract = _verification_contract(
                task["verification_contract"],
                task_id=task_id,
            )
            expected_command_ids = [
                command["command_id"]
                for command in verification_contract["commands"]
            ]
            historical_unbound_execution = set(execution) == {
                "status",
                "reason_codes",
            }
            if not historical_unbound_execution and (
                set(execution)
                != {
                    "status",
                    "reason_codes",
                    "verification_contract_hash",
                    "interpreter_id",
                    "required_command_ids",
                    "completed_command_ids",
                }
                or execution["verification_contract_hash"]
                != sha256_json(verification_contract)
                or execution["interpreter_id"]
                != verification_contract["interpreter_id"]
                or execution["required_command_ids"] != expected_command_ids
            ):
                raise ValueError(
                    f"run verification contract does not match: {task_id}"
                )
            if "invariant_grader_id" in task:
                invariant_results = run["grading"].get("invariant_results")
                if invariant_results is None and historical_unbound_execution:
                    invariant_results = []
                elif not isinstance(invariant_results, list):
                    raise ValueError(
                        f"run invariant evidence is missing: {task_id}"
                    )
                required_invariants = task["required_invariant_ids"]
                if invariant_results and [
                    result["invariant_id"] for result in invariant_results
                ] != sorted(required_invariants):
                    raise ValueError(
                        f"run invariant evidence does not match task: {task_id}"
                    )
                if invariant_results and any(
                    result["grader_id"] != task["invariant_grader_id"]
                    for result in invariant_results
                ):
                    raise ValueError(
                        f"run invariant grader does not match task: {task_id}"
                    )
        elif (
            fingerprint["work_package_plan_digest"]
            != task["work_package_plan_digest"]
        ):
            raise ValueError(f"run plan digest does not match task: {task_id}")
        plan_digests_by_task[task_id].add(
            fingerprint["work_package_plan_digest"]
        )
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
                "criticality": run["criticality"],
                "holdout_status": (
                    "PASS"
                    if run["metrics"]["holdout_passed_count"] == 1
                    else "FAIL"
                ),
                "run_hash": sha256_json(run),
                "run_id": run_id,
                "run_fingerprint_id": fingerprint["run_fingerprint_id"],
                "work_package_plan_digest": fingerprint[
                    "work_package_plan_digest"
                ],
                "strict_pass": _is_strict_pass(run),
                "task_id": task_id,
                "trial_id": trial_id,
            }
        )

    if len(configuration_ids) != 1:
        raise ValueError("runs must use exactly one configuration_id")
    if len(harness_commits) != 1:
        raise ValueError("runs must use exactly one harness_commit")
    if any(len(digests) != 1 for digests in plan_digests_by_task.values()):
        raise ValueError("runs for one task must use one work-package plan digest")

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
    run_evidence_manifest = sorted(
        manifest,
        key=lambda item: (
            item["task_id"],
            item["trial_id"],
            item["run_id"],
        ),
    )
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
        "run_evidence_manifest": run_evidence_manifest,
        "run_manifest_hash": sha256_json(run_evidence_manifest),
        "performed_actions": [],
    }
    return validate_aggregate_record(result, suite=suite)


def _aggregate_runs_v2(
    suite: Mapping[str, Any], runs: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    tasks = _suite_tasks_v2(suite)
    validated_runs = [_validated_run(run) for run in runs]
    if len(validated_runs) != suite["total_trials"]:
        raise ValueError("run count does not match the suite trial budget")

    runs_by_task: dict[str, list[dict[str, Any]]] = {
        task_id: [] for task_id in tasks
    }
    run_ids: set[str] = set()
    trial_keys: set[tuple[str, str]] = set()
    harness_commits: set[str] = set()
    configurations: dict[str, set[str]] = {}
    profile_hashes: dict[str, set[str]] = {}
    manifest: list[dict[str, Any]] = []

    for run in validated_runs:
        if run.get("schema_version") != "2":
            raise ValueError("suite v2 requires agent-run-v2 evidence")
        task_id = run["task_id"]
        if run["suite_id"] != suite["suite_id"] or task_id not in tasks:
            raise ValueError("run does not belong to suite v2")
        task = tasks[task_id]
        fingerprint = run["fingerprint"]
        profile = run["agent_profile"]
        if (
            run["task_class"] != task["lane"]
            or run["criticality"] != task["criticality"]
            or fingerprint["target_base_commit"] != task["source_basis"]
            or fingerprint["contract_basis_sha"] != task["source_basis"]
            or fingerprint["verification_suite_id"] != suite["suite_id"]
            or profile["agent_profile_id"] != task["agent_profile_id"]
            or profile["agent_profile_hash"] != task["agent_profile_hash"]
        ):
            raise ValueError("run task or profile binding does not match suite v2")
        if fingerprint["comparability"] != "FULL":
            raise ValueError("suite v2 runs must have FULL comparability")
        verification = _verification_contract(
            task["verification_contract"], task_id=task_id
        )
        expected_ids = sorted(
            command["command_id"] for command in verification["commands"]
        )
        if (
            run["execution"]["verification_contract_hash"]
            != sha256_json(verification)
            or run["execution"]["interpreter_id"]
            != verification["interpreter_id"]
            or run["execution"]["required_command_ids"] != expected_ids
        ):
            raise ValueError("run verification evidence does not match suite v2")
        invariants = run["grading"]["invariant_results"]
        if (
            [item["invariant_id"] for item in invariants]
            != sorted(task["required_invariant_ids"])
            or any(
                item["grader_id"] != task["invariant_grader_id"]
                for item in invariants
            )
        ):
            raise ValueError("run grader evidence does not match suite v2")
        holdout_count = (
            run["metrics"]["holdout_passed_count"]
            + run["metrics"]["holdout_failed_count"]
        )
        if holdout_count != _EXPECTED_HOLDOUTS_PER_RUN:
            raise ValueError("run holdout count is incomplete")

        run_id = run["run_id"]
        trial_key = (task_id, run["trial_id"])
        if run_id in run_ids or trial_key in trial_keys:
            raise ValueError("duplicate suite v2 run or task/trial")
        run_ids.add(run_id)
        trial_keys.add(trial_key)
        runs_by_task[task_id].append(run)
        harness_commits.add(fingerprint["harness_commit"])
        role_configuration_id = sha256_json(
            {
                "agent_adapter_id": fingerprint["agent_adapter_id"],
                "agent_adapter_version": fingerprint["agent_adapter_version"],
                "model_id": profile["model_id"],
                "reasoning_profile": profile["reasoning_profile"],
                "tool_policy_hash": fingerprint["tool_policy_hash"],
                "skill_set_hash": fingerprint["skill_set_hash"],
                "dependency_lock_hash": fingerprint["dependency_lock_hash"],
                "environment_profile_id": fingerprint["environment_profile_id"],
            }
        )
        configurations.setdefault(profile["agent_profile_id"], set()).add(
            role_configuration_id
        )
        profile_hashes.setdefault(profile["agent_profile_id"], set()).add(
            profile["agent_profile_hash"]
        )
        manifest.append(
            {
                "agent_profile_id": profile["agent_profile_id"],
                "configuration_id": role_configuration_id,
                "criticality": run["criticality"],
                "holdout_status": (
                    "PASS"
                    if run["metrics"]["holdout_passed_count"] == 1
                    else "FAIL"
                ),
                "run_hash": sha256_json(run),
                "run_id": run_id,
                "run_fingerprint_id": fingerprint["run_fingerprint_id"],
                "work_package_plan_digest": fingerprint[
                    "work_package_plan_digest"
                ],
                "strict_pass": _is_strict_pass(run),
                "task_id": task_id,
                "trial_id": run["trial_id"],
            }
        )

    if len(harness_commits) != 1:
        raise ValueError("suite v2 runs must use one harness commit")
    if any(len(values) != 1 for values in configurations.values()):
        raise ValueError("one role must use exactly one configuration")
    if any(len(values) != 1 for values in profile_hashes.values()):
        raise ValueError("one role must use exactly one profile hash")
    for task_id, task in tasks.items():
        if len(runs_by_task[task_id]) != task["trials"]:
            raise ValueError(f"missing or extra trials for task: {task_id}")

    role_configuration_manifest = [
        {
            "agent_profile_id": profile_id,
            "agent_profile_hash": next(iter(profile_hashes[profile_id])),
            "configuration_id": next(iter(configuration_ids)),
            "run_count": sum(
                run["agent_profile"]["agent_profile_id"] == profile_id
                for run in validated_runs
            ),
        }
        for profile_id, configuration_ids in sorted(configurations.items())
    ]
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
    ordered_manifest = sorted(
        manifest,
        key=lambda item: (item["task_id"], item["trial_id"], item["run_id"]),
    )
    result = {
        "schema_version": "2",
        "status": "PASS" if not reasons else "HOLD",
        "reason_codes": reasons,
        "suite_id": suite["suite_id"],
        "suite_manifest_hash": sha256_json(suite),
        "profile_set_hash": suite["profile_set_hash"],
        "role_configuration_manifest": role_configuration_manifest,
        "system_configuration_id": sha256_json(role_configuration_manifest),
        "comparability": "FULL",
        "source_basis": {
            "harness_commit": harness_commits.pop(),
            "target_commit": suite["target_checkpoint"],
        },
        "task_count": len(tasks),
        "run_count": len(validated_runs),
        "metrics": metrics,
        "run_evidence_manifest": ordered_manifest,
        "run_manifest_hash": sha256_json(ordered_manifest),
        "performed_actions": [],
    }
    return validate_role_aggregate(result, suite=suite)


def validate_role_aggregate(
    record: Mapping[str, Any],
    *,
    suite: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(record, Mapping) or set(record) != _ROLE_AGGREGATE_KEYS:
        raise ValueError("role aggregate key set is invalid")
    if record.get("schema_version") != "2":
        raise ValueError("role aggregate schema version is invalid")
    for field in (
        "suite_manifest_hash",
        "profile_set_hash",
        "system_configuration_id",
        "run_manifest_hash",
    ):
        if not isinstance(record.get(field), str) or not _HASH.fullmatch(record[field]):
            raise ValueError(f"role aggregate {field} is invalid")
    roles = record.get("role_configuration_manifest")
    if not isinstance(roles, list) or not roles:
        raise ValueError("role configuration manifest is invalid")
    if any(not isinstance(item, Mapping) or set(item) != _ROLE_CONFIGURATION_KEYS for item in roles):
        raise ValueError("role configuration entry is invalid")
    if roles != sorted(roles, key=lambda item: item["agent_profile_id"]):
        raise ValueError("role configuration ordering is invalid")
    if len({item["agent_profile_id"] for item in roles}) != len(roles):
        raise ValueError("role configuration profile is duplicated")
    for item in roles:
        if (
            not _SAFE_ID.fullmatch(str(item["agent_profile_id"]))
            or not _HASH.fullmatch(str(item["agent_profile_hash"]))
            or not _HASH.fullmatch(str(item["configuration_id"]))
            or not isinstance(item["run_count"], int)
            or isinstance(item["run_count"], bool)
            or item["run_count"] <= 0
        ):
            raise ValueError("role configuration entry is invalid")
    if sha256_json(roles) != record["system_configuration_id"]:
        raise ValueError("system configuration ID is invalid")
    if record.get("comparability") != "FULL":
        raise ValueError("role aggregate comparability is invalid")
    metrics = _validated_metrics(record.get("metrics"))
    expected_reasons = _reason_codes(metrics)
    if record.get("reason_codes") != expected_reasons:
        raise ValueError("role aggregate reason codes are invalid")
    if record.get("status") != ("PASS" if not expected_reasons else "HOLD"):
        raise ValueError("role aggregate status is invalid")
    if record.get("performed_actions") != []:
        raise ValueError("role aggregate performed_actions must be empty")
    manifest = record.get("run_evidence_manifest")
    if (
        not isinstance(manifest, list)
        or len(manifest) != record.get("run_count")
        or any(
            not isinstance(item, Mapping) or set(item) != _RUN_EVIDENCE_V2_KEYS
            for item in manifest
        )
        or sha256_json(manifest) != record["run_manifest_hash"]
    ):
        raise ValueError("role aggregate run manifest is invalid")
    if sum(item["run_count"] for item in roles) != record["run_count"]:
        raise ValueError("role aggregate run totals are invalid")
    if suite is not None:
        tasks = _suite_tasks_v2(suite)
        if (
            record["suite_id"] != suite["suite_id"]
            or record["suite_manifest_hash"] != sha256_json(suite)
            or record["profile_set_hash"] != suite["profile_set_hash"]
            or record["task_count"] != len(tasks)
            or record["run_count"] != suite["total_trials"]
        ):
            raise ValueError("role aggregate does not bind to suite v2")
    return dict(record)


def compare_role_aggregates(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any]
) -> dict[str, Any]:
    baseline_record = validate_role_aggregate(baseline)
    if (
        not isinstance(candidate, Mapping)
        or set(candidate) != _ROLE_AGGREGATE_KEYS
        or not isinstance(candidate.get("profile_set_hash"), str)
        or not _HASH.fullmatch(candidate["profile_set_hash"])
    ):
        raise ValueError("candidate role aggregate is malformed")
    if baseline_record["profile_set_hash"] != candidate["profile_set_hash"]:
        return {
            "schema_version": "2",
            "status": "HOLD",
            "decision": "HOLD",
            "reason_codes": ["PROFILE_SET_MISMATCH"],
            "performed_actions": [],
        }
    candidate_record = validate_role_aggregate(candidate)
    if (
        baseline_record["system_configuration_id"]
        != candidate_record["system_configuration_id"]
    ):
        return {
            "schema_version": "2",
            "status": "HOLD",
            "decision": "HOLD",
            "reason_codes": ["SYSTEM_CONFIGURATION_MISMATCH"],
            "performed_actions": [],
        }
    regressions = []
    for field in _STRICT_BLOCKERS:
        if candidate_record["metrics"][field] > baseline_record["metrics"][field]:
            regressions.append(field.upper())
    for field in ("strict_pass_3_task_rate", "strict_pass_5_critical_rate"):
        if candidate_record["metrics"][field] < baseline_record["metrics"][field]:
            regressions.append(field.upper())
    return {
        "schema_version": "2",
        "status": "REJECT" if regressions else "PASS",
        "decision": "REJECT" if regressions else "ADOPT",
        "reason_codes": (
            ["COMPARABLE_QUALITY_REGRESSION"] if regressions else []
        ),
        "performed_actions": [],
    }


def aggregate_runs(
    suite: Mapping[str, Any], runs: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Dispatch to the historical v1 or role-aware v2 aggregate contract."""

    if isinstance(suite, Mapping) and suite.get("schema_version") == "2":
        return _aggregate_runs_v2(suite, runs)
    return _aggregate_runs_v1(suite, runs)
