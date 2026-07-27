"""Machine-captured Agent Quality trial evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from scripts import work_package_conflict_check as preflight
from scripts import work_package_postflight as postflight

from .contracts import (
    AgentQualityValidationError,
    METRIC_KEYS,
    canonical_json_bytes,
    sha256_json,
    validate_run,
)
from .fingerprint import normalize_fingerprint


MAX_CAPTURE_BYTES = 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 120
PROFILE_KEYS = {
    "profile_id",
    "model_id",
    "reasoning_profile",
    "lane",
    "read_only",
}
PROFILE_DOCUMENT_KEYS = {"schema_version", "profile_set_id", "profiles"}
LAUNCH_RECEIPT_KEYS = {
    "schema_version",
    "status",
    "agent_id",
    "request_hash",
    "agent_adapter_id",
    "agent_adapter_version",
    "requested_profile_id",
    "requested_profile_hash",
    "tool_policy_hash",
    "skill_set_hash",
}
GRADER_MANIFEST_KEYS = {
    "schema_version",
    "grader_id",
    "grader_version",
    "grader_path",
    "argv",
    "required_invariant_ids",
    "timeout_seconds",
}
GRADER_OUTPUT_KEYS = {
    "blocker_count",
    "dimensions",
    "invariant_results",
    "metrics",
}
GRADE_KEYS = {
    "functional_correctness",
    "contract_adherence",
    "scope_adherence",
    "semantic_consistency",
    "architectural_consistency",
    "safety_compliance",
    "reproducibility",
}


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_id(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value.encode("utf-8")) <= 160
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", value) is not None
    )


def _run(
    argv: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            shell=False,
            check=False,
            capture_output=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        stdout = exc.stdout if isinstance(exc, subprocess.TimeoutExpired) else b""
        stderr = exc.stderr if isinstance(exc, subprocess.TimeoutExpired) else b""
        stdout = stdout if isinstance(stdout, bytes) else (stdout or "").encode("utf-8")
        stderr = stderr if isinstance(stderr, bytes) else (stderr or "").encode("utf-8")
        if len(stdout) > MAX_CAPTURE_BYTES or len(stderr) > MAX_CAPTURE_BYTES:
            raise AgentQualityValidationError(("CAPTURE_OUTPUT_TOO_LARGE",)) from exc
        return {
            "exit_code": None,
            "stdout": stdout,
            "stderr": stderr,
            "status": "ENVIRONMENT BLOCKED",
        }
    if len(completed.stdout) > MAX_CAPTURE_BYTES or len(completed.stderr) > MAX_CAPTURE_BYTES:
        raise AgentQualityValidationError(("CAPTURE_OUTPUT_TOO_LARGE",))
    return {
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
    }


def _git_bytes(repo_root: Path, *args: str) -> bytes:
    result = _run(
        ["git", *args],
        cwd=repo_root,
        timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    )
    if result["status"] != "PASS":
        raise AgentQualityValidationError(("GIT_OBSERVATION_FAILED",))
    return result["stdout"]


def _git_text(repo_root: Path, *args: str) -> str:
    try:
        return _git_bytes(repo_root, *args).decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise AgentQualityValidationError(("GIT_OUTPUT_UTF8_INVALID",)) from exc


def load_profiles(payload: Any) -> tuple[str, dict[str, dict[str, Any]]]:
    if not isinstance(payload, dict) or set(payload) != PROFILE_DOCUMENT_KEYS:
        raise AgentQualityValidationError(("PROFILE_DOCUMENT_INVALID",))
    if payload["schema_version"] != "1" or not _safe_id(payload["profile_set_id"]):
        raise AgentQualityValidationError(("PROFILE_DOCUMENT_INVALID",))
    profiles = payload["profiles"]
    if not isinstance(profiles, list) or not profiles or len(profiles) > 16:
        raise AgentQualityValidationError(("PROFILE_COUNT_INVALID",))
    result: dict[str, dict[str, Any]] = {}
    for profile in profiles:
        if not isinstance(profile, dict) or set(profile) != PROFILE_KEYS:
            raise AgentQualityValidationError(("PROFILE_INVALID",))
        if (
            not _safe_id(profile["profile_id"])
            or not _safe_id(profile["model_id"])
            or profile["reasoning_profile"] not in {"low", "medium", "high", "xhigh"}
            or profile["lane"] not in {"contract", "feature", "integration", "review"}
            or not isinstance(profile["read_only"], bool)
        ):
            raise AgentQualityValidationError(("PROFILE_INVALID",))
        if profile["profile_id"] in result:
            raise AgentQualityValidationError(("PROFILE_ID_DUPLICATE",))
        result[profile["profile_id"]] = dict(profile)
    return payload["profile_set_id"], result


def _validate_launch_receipt(
    payload: Any,
    *,
    profile_id: str,
    profile_hash: str,
) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != LAUNCH_RECEIPT_KEYS:
        raise AgentQualityValidationError(("LAUNCH_RECEIPT_INVALID",))
    if (
        payload["schema_version"] != "1"
        or payload["status"] != "PASS"
        or payload["requested_profile_id"] != profile_id
        or payload["requested_profile_hash"] != profile_hash
    ):
        raise AgentQualityValidationError(("AGENT_PROFILE_MISMATCH",))
    for key in ("agent_id", "agent_adapter_id", "agent_adapter_version"):
        if not _safe_id(payload[key]):
            raise AgentQualityValidationError(("LAUNCH_RECEIPT_INVALID",))
    for key in ("request_hash", "requested_profile_hash", "tool_policy_hash", "skill_set_hash"):
        if not isinstance(payload[key], str) or len(payload[key]) != 64:
            raise AgentQualityValidationError(("LAUNCH_RECEIPT_INVALID",))
    return dict(payload)


def _validate_grader_manifest(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != GRADER_MANIFEST_KEYS:
        raise AgentQualityValidationError(("GRADER_MANIFEST_INVALID",))
    if (
        payload["schema_version"] != "1"
        or not _safe_id(payload["grader_id"])
        or not _safe_id(payload["grader_version"])
        or not preflight.safe_repo_path(payload["grader_path"])
        or not isinstance(payload["timeout_seconds"], int)
        or not 1 <= payload["timeout_seconds"] <= 600
        or not isinstance(payload["argv"], list)
        or not payload["argv"]
        or len(payload["argv"]) > preflight.MAX_ARGV_ITEMS
        or not all(preflight.safe_argv_token(token) for token in payload["argv"])
        or not isinstance(payload["required_invariant_ids"], list)
        or not payload["required_invariant_ids"]
        or len(payload["required_invariant_ids"]) != len(set(payload["required_invariant_ids"]))
        or not all(_safe_id(item) for item in payload["required_invariant_ids"])
    ):
        raise AgentQualityValidationError(("GRADER_MANIFEST_INVALID",))
    return dict(payload)


def _resolve_argv(
    argv: list[str],
    *,
    repo_root: Path,
    grader_path: Path | None = None,
) -> list[str]:
    replacements = {
        "{PYTHON}": sys.executable,
        "{REPO_ROOT}": str(repo_root),
    }
    if grader_path is not None:
        replacements["{GRADER}"] = str(grader_path)
    return [replacements.get(token, token) for token in argv]


def _command_result(command: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    argv = _resolve_argv(command["argv"], repo_root=repo_root)
    observed = _run(argv, cwd=repo_root, timeout_seconds=DEFAULT_TIMEOUT_SECONDS)
    return {
        "command_id": command["command_id"],
        "argv_hash": sha256_json(argv),
        "exit_code": observed["exit_code"],
        "stdout_sha256": _hash_bytes(observed["stdout"]),
        "stdout_bytes": len(observed["stdout"]),
        "stderr_sha256": _hash_bytes(observed["stderr"]),
        "stderr_bytes": len(observed["stderr"]),
        "status": observed["status"],
    }


def _repository_evidence(repo_root: Path, base_sha: str) -> dict[str, Any]:
    head_sha = _git_text(repo_root, "rev-parse", "HEAD")
    tree_sha = _git_text(repo_root, "rev-parse", "HEAD^{tree}")
    diff = _git_bytes(repo_root, "diff", "--binary", f"{base_sha}..{head_sha}")
    changed_raw = _git_bytes(repo_root, "diff", "--name-only", "-z", f"{base_sha}..{head_sha}")
    changed = sorted(item.decode("utf-8") for item in changed_raw.split(b"\0") if item)
    untracked_raw = _git_bytes(
        repo_root, "ls-files", "--others", "--exclude-standard", "-z"
    )
    untracked = sorted(item.decode("utf-8") for item in untracked_raw.split(b"\0") if item)
    name_status = _git_text(repo_root, "diff", "--name-status", f"{base_sha}..{head_sha}")
    status = _git_bytes(repo_root, "status", "--porcelain=v1", "-z")
    return {
        "base_sha": base_sha,
        "head_sha": head_sha,
        "tree_sha": tree_sha,
        "commit_count": int(_git_text(repo_root, "rev-list", "--count", f"{base_sha}..{head_sha}")),
        "diff_sha256": _hash_bytes(diff),
        "changed_path_count": len(changed),
        "changed_path_set_hash": sha256_json(changed),
        "untracked_path_count": len(untracked),
        "untracked_path_set_hash": sha256_json(untracked),
        "rename_count": sum(line.startswith(("R", "C")) for line in name_status.splitlines()),
        "delete_count": sum(line.startswith("D") for line in name_status.splitlines()),
        "dirty": bool(status),
    }


def _grader_result(
    manifest: dict[str, Any],
    *,
    manifest_path: Path,
    repo_root: Path,
) -> tuple[dict[str, Any], dict[str, int]]:
    grader_path = (manifest_path.parent / manifest["grader_path"]).resolve(strict=True)
    if not grader_path.is_file() or grader_path.is_symlink():
        raise AgentQualityValidationError(("GRADER_PATH_INVALID",))
    argv = _resolve_argv(manifest["argv"], repo_root=repo_root, grader_path=grader_path)
    observed = _run(argv, cwd=repo_root, timeout_seconds=manifest["timeout_seconds"])
    parsed: Any = {}
    if observed["status"] != "ENVIRONMENT BLOCKED":
        try:
            parsed = json.loads(observed["stdout"].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            parsed = {}
    valid = (
        isinstance(parsed, dict)
        and set(parsed) == GRADER_OUTPUT_KEYS
        and isinstance(parsed.get("dimensions"), dict)
        and set(parsed["dimensions"]) == GRADE_KEYS
        and all(value in {"PASS", "FAIL", "NOT RUN"} for value in parsed["dimensions"].values())
        and isinstance(parsed.get("blocker_count"), int)
        and parsed["blocker_count"] >= 0
        and isinstance(parsed.get("invariant_results"), list)
        and isinstance(parsed.get("metrics"), dict)
        and set(parsed["metrics"]) == METRIC_KEYS
        and all(isinstance(value, int) and value >= 0 for value in parsed["metrics"].values())
    )
    invariant_results: list[dict[str, Any]] = []
    if valid:
        raw_results = parsed["invariant_results"]
        valid = all(
            isinstance(item, dict)
            and set(item) == {"invariant_id", "status"}
            and _safe_id(item["invariant_id"])
            and item["status"] in {"PASS", "FAIL", "NOT RUN"}
            for item in raw_results
        )
        if valid:
            ids = [item["invariant_id"] for item in raw_results]
            valid = (
                ids == sorted(set(ids))
                and ids == sorted(manifest["required_invariant_ids"])
            )
            invariant_results = [
                {
                    "invariant_id": item["invariant_id"],
                    "grader_id": manifest["grader_id"],
                    "status": item["status"],
                    "result_hash": sha256_json(
                        {
                            "grader_id": manifest["grader_id"],
                            "invariant_id": item["invariant_id"],
                            "status": item["status"],
                            "stdout_sha256": _hash_bytes(observed["stdout"]),
                        }
                    ),
                }
                for item in raw_results
            ]
    status = (
        "PASS"
        if observed["status"] == "PASS"
        and valid
        and parsed["blocker_count"] == 0
        and all(item["status"] == "PASS" for item in invariant_results)
        else observed["status"] if observed["status"] == "ENVIRONMENT BLOCKED" else "FAIL"
    )
    dimensions = parsed["dimensions"] if valid else {key: "FAIL" for key in GRADE_KEYS}
    metrics = parsed["metrics"] if valid else {key: 0 for key in METRIC_KEYS}
    if not valid:
        metrics["semantic_blocker_count"] = 1
    return (
        {
            **dimensions,
            "blocker_count": parsed["blocker_count"] if valid else 1,
            "invariant_results": invariant_results or [
                {
                    "invariant_id": invariant_id,
                    "grader_id": manifest["grader_id"],
                    "status": "FAIL",
                    "result_hash": sha256_json(
                        {"grader_id": manifest["grader_id"], "invariant_id": invariant_id}
                    ),
                }
                for invariant_id in sorted(manifest["required_invariant_ids"])
            ],
            "grader_id": manifest["grader_id"],
            "grader_version": manifest["grader_version"],
            "exit_code": observed["exit_code"],
            "stdout_sha256": _hash_bytes(observed["stdout"]),
            "stdout_bytes": len(observed["stdout"]),
            "stderr_sha256": _hash_bytes(observed["stderr"]),
            "stderr_bytes": len(observed["stderr"]),
            "status": status,
        },
        metrics,
    )


def capture_run(
    *,
    suite: dict[str, Any],
    profiles: dict[str, Any],
    package: dict[str, Any],
    package_path: str,
    task_id: str,
    trial_id: str,
    repo_root: Path,
    launch_receipt: dict[str, Any],
    grader_manifest: dict[str, Any],
    grader_manifest_path: Path,
    harness_root: Path,
) -> dict[str, Any]:
    """Execute declared verification and grader commands and return a v2 envelope."""

    tasks = {
        task["task_id"]: task
        for task in suite.get("tasks", [])
        if isinstance(task, dict) and _safe_id(task.get("task_id"))
    }
    task = tasks.get(task_id)
    if task is None or not _safe_id(trial_id):
        raise AgentQualityValidationError(("TASK_OR_TRIAL_INVALID",))
    profile_set_id, profile_map = load_profiles(profiles)
    if (
        suite.get("profile_set_id") != profile_set_id
        or suite.get("profile_set_hash") != sha256_json(profiles)
    ):
        raise AgentQualityValidationError(("PROFILE_SET_MISMATCH",))
    profile_id = task.get("agent_profile_id")
    profile = profile_map.get(profile_id)
    if profile is None:
        raise AgentQualityValidationError(("AGENT_PROFILE_UNKNOWN",))
    profile_hash = sha256_json(profile)
    launch = _validate_launch_receipt(
        launch_receipt, profile_id=profile_id, profile_hash=profile_hash
    )
    if (
        package.get("agent_profile_id") != profile_id
        or package.get("agent_profile_hash") != profile_hash
        or package.get("task_id") != task_id
        or package.get("lane") != task.get("lane")
    ):
        raise AgentQualityValidationError(("AGENT_PROFILE_MISMATCH",))

    preflight_result = preflight.inspect_payloads([package])
    if preflight_result["status"] != "PASS":
        raise AgentQualityValidationError(("WORK_PACKAGE_PREFLIGHT_FAILED",))
    manifest = _validate_grader_manifest(grader_manifest)
    if (
        manifest["grader_id"] != task.get("invariant_grader_id")
        or sorted(manifest["required_invariant_ids"])
        != sorted(task.get("required_invariant_ids", []))
    ):
        raise AgentQualityValidationError(("GRADER_BINDING_MISMATCH",))

    command_results = sorted(
        [
            _command_result(command, repo_root)
            for command in package["verification_contract"]["commands"]
        ],
        key=lambda item: item["command_id"],
    )
    required_ids = sorted(item["command_id"] for item in command_results)
    completed_ids = [
        item["command_id"] for item in command_results if item["status"] == "PASS"
    ]
    verification_status = (
        "PASS"
        if required_ids == completed_ids
        else (
            "ENVIRONMENT BLOCKED"
            if any(item["status"] == "ENVIRONMENT BLOCKED" for item in command_results)
            else "FAIL"
        )
    )
    postflight_result = postflight.inspect_postflight(
        [package_path],
        task_id=task_id,
        verification_status=verification_status,
        verification_interpreter_id=package["verification_contract"]["interpreter_id"],
        completed_command_ids=completed_ids,
        repo_root=repo_root,
    )
    repository = _repository_evidence(repo_root, package["base_sha"])
    grading, metrics = _grader_result(
        manifest, manifest_path=grader_manifest_path, repo_root=repo_root
    )
    execution_status = (
        "PASS"
        if verification_status == "PASS"
        and postflight_result["status"] == "PASS"
        else (
            "ENVIRONMENT BLOCKED"
            if verification_status == "ENVIRONMENT BLOCKED"
            else "FAIL"
        )
    )
    reason_codes = []
    if verification_status != "PASS":
        reason_codes.append("VERIFICATION_COMMAND_FAILED")
    if postflight_result["status"] != "PASS":
        reason_codes.append("POSTFLIGHT_FAILED")

    corpus_digest = _hash_bytes(
        (harness_root / "artifacts" / "corpus-digest.json").read_bytes()
    )
    lock_hash = _hash_bytes((harness_root / "requirements-dev.lock").read_bytes())
    fingerprint = normalize_fingerprint(
        {
            "harness_commit": _git_text(harness_root, "rev-parse", "HEAD"),
            "target_base_commit": task["source_basis"],
            "contract_basis_sha": task["source_basis"],
            "work_package_plan_digest": preflight_result["plan_digest"],
            "agent_adapter_id": launch["agent_adapter_id"],
            "agent_adapter_version": launch["agent_adapter_version"],
            "model_id": profile["model_id"],
            "reasoning_profile": profile["reasoning_profile"],
            "task_contract_hash": sha256_json(task),
            "tool_policy_hash": launch["tool_policy_hash"],
            "skill_set_hash": launch["skill_set_hash"],
            "approved_corpus_digest": corpus_digest,
            "dependency_lock_hash": lock_hash,
            "environment_profile_id": "windows-python-3.12.13",
            "verification_suite_id": suite["suite_id"],
            "grader_version": manifest["grader_version"],
        }
    )
    run = {
        "schema_version": "2",
        "run_id": f"{task_id}-{trial_id}",
        "task_id": task_id,
        "trial_id": trial_id,
        "suite_id": suite["suite_id"],
        "task_class": task["lane"],
        "criticality": task["criticality"],
        "agent_profile": {
            "agent_profile_id": profile_id,
            "agent_profile_hash": profile_hash,
            "model_id": profile["model_id"],
            "reasoning_profile": profile["reasoning_profile"],
            "model_selection_source": "ADAPTER_REQUEST",
            "model_observation_status": "NOT_INDEPENDENTLY_OBSERVABLE",
            "agent_id": launch["agent_id"],
            "request_hash": launch["request_hash"],
        },
        "fingerprint": fingerprint,
        "execution": {
            "status": execution_status,
            "reason_codes": sorted(reason_codes),
            "verification_contract_hash": preflight.verification_contract_hash(
                package["verification_contract"]
            ),
            "interpreter_id": package["verification_contract"]["interpreter_id"],
            "interpreter_version": ".".join(str(item) for item in sys.version_info[:3]),
            "required_command_ids": required_ids,
            "completed_command_ids": completed_ids,
            "command_results": command_results,
            "postflight_result_hash": sha256_json(postflight_result),
        },
        "repository": repository,
        "grading": grading,
        "metrics": metrics,
        "evidence_refs": [],
        "performed_actions": ["local_write", "execute"],
    }
    return validate_run(run)


def write_captured_run(path: Path, run: dict[str, Any]) -> None:
    data = json.dumps(run, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8") + b"\n"
    if len(data) > 64 * 1024:
        raise AgentQualityValidationError(("RUN_OUTPUT_TOO_LARGE",))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
