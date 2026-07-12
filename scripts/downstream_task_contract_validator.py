from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
from typing import Any, Iterable


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1"
VALIDATOR_ID = "standalone_downstream_task_contract_validator"
MAX_INPUT_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 8 * 1024
MAX_STRING_BYTES = 512
MAX_COMMANDS = 32
MAX_SCOPE_ITEMS = 64
MAX_REASON_CODES = 16
MAX_REPORTED_ISSUES = 32

HUMAN_CONTRACT_REF = (
    "docs/DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md#required-downstream-task-contract"
)
SYNTHETIC_FIXTURE_ID = "phase_11b_synthetic_downstream_task_contract"
SYNTHETIC_REASON_CODES = [
    "SYNTHETIC_CONTRACT_ONLY",
    "NO_DOWNSTREAM_TARGET_SELECTED",
    "NO_APPROVAL_REFERENCE",
]
EXPECTED_STATUSES = [
    "PASS",
    "PASS WITH NOTES",
    "BLOCKED",
    "FAIL",
    "NOT RUN",
    "ENVIRONMENT BLOCKED",
]
ALLOWED_ACCESS_CLASSES = [
    "local_read_only",
    "remote_read_only",
    "local_write",
    "remote_write",
]
SIDE_EFFECT_CLASSES = [
    "repository_access",
    "network_read",
    "local_write",
    "execute",
    "stage",
    "commit",
    "push",
    "pull_request",
    "merge",
    "workflow_dispatch",
    "artifact_upload",
    "tag",
    "release",
    "publish",
    "deploy",
    "live_action",
]
PERMISSION_CEILINGS = {
    "local_read_only": {"repository_access", "execute"},
    "remote_read_only": {"repository_access", "network_read", "execute"},
    "local_write": {"repository_access", "local_write", "execute", "stage", "commit"},
    "remote_write": set(SIDE_EFFECT_CLASSES),
}
ALLOWED_DATA_CLASSES = [
    "generalized_identifier",
    "repo_relative_reference",
    "commit_identifier",
    "bounded_status",
    "reason_code",
    "verification_outcome",
    "safe_summary",
]
FORBIDDEN_DATA_CLASSES = [
    "private_repository_identifier",
    "remote_url",
    "local_absolute_path",
    "raw_source",
    "full_diff",
    "patch",
    "prompt",
    "approval_text",
    "transcript",
    "stdout",
    "stderr",
    "command_log",
    "tool_call_body",
    "secret",
    "credential",
    "token",
    "private_data",
    "ip_address",
    "port",
    "endpoint",
    "live_configuration",
    "device_value",
    "downstream_raw_evidence",
]
STOP_CONDITIONS = [
    "MISSING_APPROVAL",
    "REPOSITORY_MISMATCH",
    "INSTRUCTION_CONFLICT",
    "DIRTY_STATE_MISMATCH",
    "ALLOWED_FILE_DRIFT",
    "UNSAFE_DATA",
    "UNAUTHORIZED_NETWORK",
    "UNEXPECTED_OUTPUT",
    "CLEANUP_FAILURE",
    "UNAPPROVED_REMOTE_OR_LIVE_SIDE_EFFECT",
]
REQUIRED_PLACEHOLDERS = {
    "<ACCESS_CLASS>",
    "<ALLOWED_FILE_LIST>",
    "<APPROVAL_REF>",
    "<APPROVED_WORKTREE>",
    "<BASE_COMMIT>",
    "<CLEANUP_PLAN>",
    "<CLEAN_OR_DIRTY_STATE>",
    "<COMMAND>",
    "<COMMAND_APPROVAL_REF>",
    "<DOWNSTREAM_REPO_ID>",
    "<EFFECT_CLASS>",
    "<HEAD_COMMIT>",
    "<NEXT_STEP>",
    "<NOT_RUN_ACTION>",
    "<NO_TOUCH_PATHS>",
    "<RETENTION_POLICY>",
    "<RISK_OR_ASSUMPTION>",
    "<ROLLBACK_PLAN>",
    "<SAFE_EVIDENCE_REF>",
    "<UPSTREAM_REF>",
    "<VERIFICATION_COMMAND>",
    "<WORKING_BRANCH>",
    "<WRITE_SCOPE>",
}

TOP_LEVEL_KEYS = {
    "approvals",
    "closeout",
    "commands",
    "data_policy",
    "fixture_id",
    "human_contract_ref",
    "performed_actions",
    "reason_codes",
    "repository",
    "rollback_cleanup",
    "schema_version",
    "scope",
    "side_effect_permissions",
    "status",
    "stop_conditions",
    "synthetic",
    "verification",
}
NESTED_KEYS = {
    "approvals": {
        "approval_ref",
        "owner_approval_present",
        "target_repository_approval_present",
        "target_rules_reviewed",
    },
    "closeout": {
        "changed_files",
        "commands_not_run",
        "commands_run",
        "next_step",
        "result",
        "risks",
        "safe_evidence_refs",
    },
    "data_policy": {"allowed_classes", "forbidden_classes"},
    "repository": {
        "access_class",
        "allowed_access_classes",
        "base_commit",
        "clean_state",
        "head_commit",
        "identifier",
        "upstream_ref",
        "working_branch",
        "worktree_boundary",
    },
    "rollback_cleanup": {
        "cleanup_plan",
        "overwrite_allowed",
        "retention_policy",
        "rollback_plan",
    },
    "scope": {"allowed_files", "no_touch_paths", "write_scope"},
    "verification": {"commands", "expected_statuses", "not_run_items"},
}
COMMAND_KEYS = {"approval_ref", "command", "effect_classes", "status"}
PERMISSION_KEYS = {"approval_ref", "authorized", "class", "status"}
NOT_RUN_ITEM_KEYS = {"action", "reason_code", "status"}

PLACEHOLDER_PATTERN = re.compile(r"^<[A-Z0-9_]+>$")
ANY_PLACEHOLDER_PATTERN = re.compile(r"<[A-Z0-9_]+>")
REASON_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
SAFE_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")
FIXTURE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
URL_PATTERN = re.compile(r"(?:https?|ssh)://|git@", re.IGNORECASE)
WINDOWS_ABSOLUTE_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")
IPV4_PATTERN = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")
PARENT_TRAVERSAL_PATTERN = re.compile(r"(?:^|[\\/])\.\.(?:[\\/]|$)")
SECRET_LIKE_PATTERN = re.compile(
    r"(?:api[_-]?key|password|passwd|bearer\s+[a-z0-9]|"
    r"-----BEGIN [A-Z ]+ PRIVATE KEY-----|(?:token|secret|credential)\s*[:=])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Issue:
    status: str
    code: str
    category: str


class InputIssue(RuntimeError):
    def __init__(self, status: str, reason_code: str):
        super().__init__(reason_code)
        self.status = status
        self.reason_code = reason_code


def base_result(*, contract_kind: str, dry_run: bool) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "dry_run": dry_run,
        "contract_kind": contract_kind,
        "status": "NOT RUN",
        "reason_codes": [],
        "validation_summary": {
            "input_status": "NOT RUN",
            "structure_status": "NOT RUN",
            "safety_status": "NOT RUN",
            "approval_status": "NOT RUN",
            "permission_status": "NOT RUN",
            "issue_count": 0,
        },
        "declared_permission_summary": {
            "authorized_count": 0,
            "unauthorized_count": len(SIDE_EFFECT_CLASSES),
            "authorized_classes": [],
        },
        "external_state": {
            "downstream_repository_access": "NOT RUN",
            "network_read": "NOT RUN",
            "command_execution": "NOT RUN",
            "downstream_write": "NOT RUN",
        },
        "performed_actions": [],
    }


def strings_in(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for child in value for item in strings_in(child)]
    if isinstance(value, dict):
        return [item for child in value.values() for item in strings_in(child)]
    return []


def add_issue(issues: list[Issue], status: str, code: str, category: str) -> None:
    if len(issues) >= MAX_REPORTED_ISSUES:
        return
    if not any(item.code == code for item in issues):
        issues.append(Issue(status, code, category))


def is_safe_token(value: Any) -> bool:
    return (
        isinstance(value, str)
        and SAFE_TOKEN_PATTERN.fullmatch(value) is not None
        and "//" not in value
        and not PARENT_TRAVERSAL_PATTERN.search(value)
    )


def is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and PLACEHOLDER_PATTERN.fullmatch(value) is not None


def safe_value_reason(value: str) -> str | None:
    if len(value.encode("utf-8")) > MAX_STRING_BYTES:
        return "VALUE_SIZE_LIMIT_EXCEEDED"
    if any(ord(char) < 32 for char in value):
        return "CONTROL_CHARACTER_FORBIDDEN"
    if URL_PATTERN.search(value):
        return "URL_VALUE_FORBIDDEN"
    if value.startswith(("/", "\\\\")) or WINDOWS_ABSOLUTE_PATTERN.match(value):
        return "ABSOLUTE_PATH_VALUE_FORBIDDEN"
    if "\\" in value:
        return "BACKSLASH_PATH_FORBIDDEN"
    if PARENT_TRAVERSAL_PATTERN.search(value):
        return "PARENT_TRAVERSAL_VALUE_FORBIDDEN"
    if IPV4_PATTERN.search(value):
        return "IP_VALUE_FORBIDDEN"
    if SECRET_LIKE_PATTERN.search(value):
        return "SECRET_LIKE_VALUE_FORBIDDEN"
    return None


def dynamic_values(payload: dict[str, Any]) -> list[str]:
    values: list[str] = []
    repository = payload.get("repository")
    if isinstance(repository, dict):
        for key, value in repository.items():
            if key != "allowed_access_classes":
                values.extend(strings_in(value))
    for name in ("scope", "rollback_cleanup"):
        values.extend(strings_in(payload.get(name)))
    approvals = payload.get("approvals")
    if isinstance(approvals, dict):
        values.extend(strings_in(approvals.get("approval_ref")))
    commands = payload.get("commands")
    if isinstance(commands, list):
        for command in commands:
            if isinstance(command, dict):
                values.extend(strings_in(command.get("approval_ref")))
                values.extend(strings_in(command.get("command")))
    verification = payload.get("verification")
    if isinstance(verification, dict):
        values.extend(strings_in(verification.get("commands")))
        values.extend(strings_in(verification.get("not_run_items")))
    closeout = payload.get("closeout")
    if isinstance(closeout, dict):
        for key in ("commands_not_run", "next_step", "risks", "safe_evidence_refs"):
            values.extend(strings_in(closeout.get(key)))
    return values


def is_repo_relative_reference(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    if value.startswith("/") or any(char in value for char in "*?[]"):
        return False
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return False
    return value == str(path)


def validate_common_structure(payload: dict[str, Any], issues: list[Issue]) -> None:
    if set(payload) != TOP_LEVEL_KEYS:
        add_issue(issues, "FAIL", "TOP_LEVEL_FIELDS_INVALID", "structure")

    for name, expected_keys in NESTED_KEYS.items():
        value = payload.get(name)
        if not isinstance(value, dict) or set(value) != expected_keys:
            add_issue(issues, "FAIL", "NESTED_FIELDS_INVALID", "structure")

    if payload.get("schema_version") != SCHEMA_VERSION:
        add_issue(issues, "FAIL", "SCHEMA_VERSION_INVALID", "structure")
    if payload.get("human_contract_ref") != HUMAN_CONTRACT_REF:
        add_issue(issues, "FAIL", "HUMAN_CONTRACT_REF_INVALID", "structure")
    if not isinstance(payload.get("synthetic"), bool):
        add_issue(issues, "FAIL", "SYNTHETIC_FLAG_INVALID", "structure")
    if payload.get("status") != "NOT RUN":
        add_issue(issues, "FAIL", "CONTRACT_STATUS_INVALID", "structure")
    if payload.get("performed_actions") != []:
        add_issue(issues, "FAIL", "PERFORMED_ACTIONS_NOT_EMPTY", "structure")

    data_policy = payload.get("data_policy")
    if isinstance(data_policy, dict):
        if data_policy.get("allowed_classes") != ALLOWED_DATA_CLASSES:
            add_issue(issues, "FAIL", "ALLOWED_DATA_CLASSES_INVALID", "structure")
        if data_policy.get("forbidden_classes") != FORBIDDEN_DATA_CLASSES:
            add_issue(issues, "FAIL", "FORBIDDEN_DATA_CLASSES_INVALID", "structure")

    if payload.get("stop_conditions") != STOP_CONDITIONS:
        add_issue(issues, "FAIL", "STOP_CONDITIONS_INVALID", "structure")

    verification = payload.get("verification")
    if isinstance(verification, dict):
        if verification.get("expected_statuses") != EXPECTED_STATUSES:
            add_issue(issues, "FAIL", "EXPECTED_STATUSES_INVALID", "structure")
        commands = verification.get("commands")
        if not isinstance(commands, list) or not commands or len(commands) > MAX_COMMANDS:
            add_issue(issues, "FAIL", "VERIFICATION_COMMANDS_INVALID", "structure")
        not_run_items = verification.get("not_run_items")
        if not isinstance(not_run_items, list) or not not_run_items:
            add_issue(issues, "FAIL", "NOT_RUN_ITEMS_INVALID", "structure")
        else:
            for item in not_run_items:
                if not isinstance(item, dict) or set(item) != NOT_RUN_ITEM_KEYS:
                    add_issue(issues, "FAIL", "NOT_RUN_ITEM_FIELDS_INVALID", "structure")
                    continue
                if item.get("status") != "NOT RUN" or not REASON_CODE_PATTERN.fullmatch(
                    item.get("reason_code", "") if isinstance(item.get("reason_code"), str) else ""
                ):
                    add_issue(issues, "FAIL", "NOT_RUN_ITEM_INVALID", "structure")

    reason_codes = payload.get("reason_codes")
    if not isinstance(reason_codes, list) or len(reason_codes) > MAX_REASON_CODES:
        add_issue(issues, "FAIL", "REASON_CODES_INVALID", "structure")
    elif any(not isinstance(item, str) or REASON_CODE_PATTERN.fullmatch(item) is None for item in reason_codes):
        add_issue(issues, "FAIL", "REASON_CODES_INVALID", "structure")

    scope = payload.get("scope")
    if isinstance(scope, dict):
        for key in ("allowed_files", "no_touch_paths"):
            values = scope.get(key)
            if not isinstance(values, list) or not values or len(values) > MAX_SCOPE_ITEMS:
                add_issue(issues, "FAIL", "SCOPE_LIST_INVALID", "structure")

    commands = payload.get("commands")
    if not isinstance(commands, list) or not commands or len(commands) > MAX_COMMANDS:
        add_issue(issues, "FAIL", "COMMANDS_INVALID", "structure")
    else:
        for command in commands:
            if not isinstance(command, dict) or set(command) != COMMAND_KEYS:
                add_issue(issues, "FAIL", "COMMAND_FIELDS_INVALID", "structure")
                continue
            if command.get("status") != "NOT RUN":
                add_issue(issues, "FAIL", "COMMAND_STATUS_INVALID", "structure")
            if not isinstance(command.get("command"), str) or not command.get("command"):
                add_issue(issues, "FAIL", "COMMAND_VALUE_INVALID", "structure")
            effects = command.get("effect_classes")
            if not isinstance(effects, list) or not effects or len(effects) > len(SIDE_EFFECT_CLASSES):
                add_issue(issues, "FAIL", "COMMAND_EFFECTS_INVALID", "structure")

    permissions = payload.get("side_effect_permissions")
    if not isinstance(permissions, list) or len(permissions) != len(SIDE_EFFECT_CLASSES):
        add_issue(issues, "FAIL", "SIDE_EFFECT_PERMISSIONS_INVALID", "structure")
    else:
        classes = [item.get("class") for item in permissions if isinstance(item, dict)]
        if classes != SIDE_EFFECT_CLASSES:
            add_issue(issues, "FAIL", "SIDE_EFFECT_CLASSES_INVALID", "structure")
        for item in permissions:
            if not isinstance(item, dict) or set(item) != PERMISSION_KEYS:
                add_issue(issues, "FAIL", "PERMISSION_FIELDS_INVALID", "structure")
                continue
            if not isinstance(item.get("authorized"), bool) or item.get("status") != "NOT RUN":
                add_issue(issues, "FAIL", "PERMISSION_STATE_INVALID", "structure")

    rollback = payload.get("rollback_cleanup")
    if isinstance(rollback, dict) and rollback.get("overwrite_allowed") is not False:
        add_issue(issues, "FAIL", "OVERWRITE_POLICY_INVALID", "structure")

    closeout = payload.get("closeout")
    if isinstance(closeout, dict):
        for key in ("changed_files", "commands_not_run", "commands_run", "risks", "safe_evidence_refs"):
            if not isinstance(closeout.get(key), list):
                add_issue(issues, "FAIL", "CLOSEOUT_FIELD_TYPE_INVALID", "structure")


def validate_dynamic_safety(payload: dict[str, Any], issues: list[Issue]) -> None:
    for value in dynamic_values(payload):
        if PLACEHOLDER_PATTERN.fullmatch(value):
            continue
        reason = safe_value_reason(value)
        if reason:
            add_issue(issues, "FAIL", reason, "safety")


def validate_synthetic(payload: dict[str, Any], issues: list[Issue]) -> None:
    if payload.get("synthetic") is not True:
        add_issue(issues, "FAIL", "CONTRACT_KIND_MISMATCH", "structure")
    if payload.get("fixture_id") != SYNTHETIC_FIXTURE_ID:
        add_issue(issues, "FAIL", "SYNTHETIC_FIXTURE_ID_INVALID", "structure")
    if payload.get("reason_codes") != SYNTHETIC_REASON_CODES:
        add_issue(issues, "FAIL", "SYNTHETIC_REASON_CODES_INVALID", "structure")

    placeholders = {value for value in strings_in(payload) if PLACEHOLDER_PATTERN.fullmatch(value)}
    if not REQUIRED_PLACEHOLDERS <= placeholders:
        add_issue(issues, "FAIL", "SYNTHETIC_PLACEHOLDERS_INVALID", "structure")

    approvals = payload.get("approvals")
    expected_approvals = {
        "approval_ref": "<APPROVAL_REF>",
        "owner_approval_present": False,
        "target_repository_approval_present": False,
        "target_rules_reviewed": False,
    }
    if approvals != expected_approvals:
        add_issue(issues, "FAIL", "SYNTHETIC_APPROVAL_STATE_INVALID", "approval")

    permissions = payload.get("side_effect_permissions")
    if isinstance(permissions, list):
        for item in permissions:
            if not isinstance(item, dict):
                continue
            if item.get("authorized") is not False or item.get("approval_ref") is not None:
                add_issue(issues, "FAIL", "SYNTHETIC_PERMISSION_STATE_INVALID", "permission")


def validate_filled(payload: dict[str, Any], issues: list[Issue]) -> list[str]:
    authorized_classes: list[str] = []
    if payload.get("synthetic") is not False:
        add_issue(issues, "FAIL", "CONTRACT_KIND_MISMATCH", "structure")
    if any(ANY_PLACEHOLDER_PATTERN.search(value) for value in strings_in(payload)):
        add_issue(issues, "BLOCKED", "UNRESOLVED_PLACEHOLDER", "approval")

    fixture_id = payload.get("fixture_id")
    if not is_placeholder(fixture_id) and (
        not isinstance(fixture_id, str) or FIXTURE_ID_PATTERN.fullmatch(fixture_id) is None
    ):
        add_issue(issues, "FAIL", "FILLED_CONTRACT_ID_INVALID", "structure")

    approvals = payload.get("approvals")
    if isinstance(approvals, dict):
        if any(
            approvals.get(key) is not True
            for key in (
                "owner_approval_present",
                "target_repository_approval_present",
                "target_rules_reviewed",
            )
        ):
            add_issue(issues, "BLOCKED", "REQUIRED_APPROVAL_MISSING", "approval")
        if not is_safe_token(approvals.get("approval_ref")):
            add_issue(issues, "BLOCKED", "APPROVAL_REF_INVALID", "approval")

    repository = payload.get("repository")
    access_class: Any = None
    if isinstance(repository, dict):
        access_class = repository.get("access_class")
        if repository.get("allowed_access_classes") != ALLOWED_ACCESS_CLASSES:
            add_issue(issues, "FAIL", "ALLOWED_ACCESS_CLASSES_INVALID", "structure")
        if access_class not in ALLOWED_ACCESS_CLASSES:
            add_issue(issues, "BLOCKED", "ACCESS_CLASS_INVALID", "permission")
        for key in ("identifier", "upstream_ref", "working_branch", "worktree_boundary"):
            value = repository.get(key)
            if not is_placeholder(value) and not is_safe_token(value):
                add_issue(issues, "FAIL", "REPOSITORY_FIELD_INVALID", "safety")
        for key in ("base_commit", "head_commit"):
            value = repository.get(key)
            if not is_placeholder(value) and (
                not isinstance(value, str) or SHA_PATTERN.fullmatch(value) is None
            ):
                add_issue(issues, "FAIL", "COMMIT_IDENTIFIER_INVALID", "structure")
        if repository.get("clean_state") not in {"clean", "dirty_expected"}:
            add_issue(issues, "BLOCKED", "CLEAN_STATE_INVALID", "approval")

    scope = payload.get("scope")
    if isinstance(scope, dict):
        for key in ("allowed_files", "no_touch_paths"):
            values = scope.get(key)
            if isinstance(values, list):
                for value in values:
                    if not is_placeholder(value) and not is_repo_relative_reference(value):
                        add_issue(issues, "FAIL", "REPO_RELATIVE_REFERENCE_INVALID", "safety")
        if not isinstance(scope.get("write_scope"), str) or not scope.get("write_scope"):
            add_issue(issues, "FAIL", "WRITE_SCOPE_INVALID", "structure")

    closeout = payload.get("closeout")
    if isinstance(closeout, dict):
        if closeout.get("changed_files") != [] or closeout.get("commands_run") != []:
            add_issue(issues, "FAIL", "PRECOMPLETED_CLOSEOUT_INVALID", "structure")
        if closeout.get("result") != "NOT RUN":
            add_issue(issues, "FAIL", "CLOSEOUT_RESULT_INVALID", "structure")

    permissions = payload.get("side_effect_permissions")
    if isinstance(permissions, list):
        for item in permissions:
            if not isinstance(item, dict) or set(item) != PERMISSION_KEYS:
                continue
            class_name = item.get("class")
            authorized = item.get("authorized")
            approval_ref = item.get("approval_ref")
            if authorized is True:
                if class_name in SIDE_EFFECT_CLASSES:
                    authorized_classes.append(class_name)
                if not is_safe_token(approval_ref):
                    add_issue(issues, "BLOCKED", "PERMISSION_APPROVAL_REF_INVALID", "permission")
            elif authorized is False:
                if approval_ref is not None:
                    add_issue(issues, "FAIL", "UNAUTHORIZED_PERMISSION_REF_INVALID", "permission")

    if "repository_access" not in authorized_classes:
        add_issue(issues, "BLOCKED", "REPOSITORY_ACCESS_NOT_AUTHORIZED", "permission")
    ceiling = PERMISSION_CEILINGS.get(access_class)
    if ceiling is not None and not set(authorized_classes) <= ceiling:
        add_issue(issues, "BLOCKED", "ACCESS_PERMISSION_CONFLICT", "permission")

    commands = payload.get("commands")
    if isinstance(commands, list):
        for command in commands:
            if not isinstance(command, dict) or set(command) != COMMAND_KEYS:
                continue
            if not is_safe_token(command.get("approval_ref")):
                add_issue(issues, "BLOCKED", "COMMAND_APPROVAL_REF_INVALID", "approval")
            effects = command.get("effect_classes")
            if not isinstance(effects, list):
                continue
            if len(set(item for item in effects if isinstance(item, str))) != len(effects):
                add_issue(issues, "FAIL", "DUPLICATE_COMMAND_EFFECT", "permission")
            concrete_effects = [item for item in effects if not is_placeholder(item)]
            if any(item not in SIDE_EFFECT_CLASSES for item in concrete_effects):
                add_issue(issues, "FAIL", "UNKNOWN_COMMAND_EFFECT", "permission")
            if any(item not in authorized_classes for item in concrete_effects):
                add_issue(issues, "BLOCKED", "COMMAND_PERMISSION_CONFLICT", "permission")

    return [item for item in SIDE_EFFECT_CLASSES if item in authorized_classes]


def category_status(issues: Iterable[Issue], category: str) -> str:
    category_issues = [item for item in issues if item.category == category]
    if any(item.status == "FAIL" for item in category_issues):
        return "FAIL"
    if any(item.status == "BLOCKED" for item in category_issues):
        return "BLOCKED"
    return "PASS"


def validate_contract(payload: Any, contract_kind: str) -> tuple[list[Issue], list[str]]:
    issues: list[Issue] = []
    if not isinstance(payload, dict):
        add_issue(issues, "FAIL", "CONTRACT_ROOT_INVALID", "structure")
        return issues, []
    if contract_kind not in {"synthetic", "filled"}:
        add_issue(issues, "FAIL", "CONTRACT_KIND_INVALID", "structure")
        return issues, []

    validate_common_structure(payload, issues)
    validate_dynamic_safety(payload, issues)
    if contract_kind == "synthetic":
        validate_synthetic(payload, issues)
        authorized_classes: list[str] = []
    else:
        authorized_classes = validate_filled(payload, issues)
    return issues, authorized_classes


def is_reparse_point(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise InputIssue("ENVIRONMENT BLOCKED", "INPUT_INSPECTION_FAILED") from exc
    if stat.S_ISLNK(info.st_mode):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(reparse_flag and attributes & reparse_flag)


def ensure_no_reparse_components(root: Path, candidate: Path) -> None:
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise InputIssue("FAIL", "UNSAFE_INPUT_PATH") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if is_reparse_point(current):
            raise InputIssue("FAIL", "REPARSE_INPUT_FORBIDDEN")


def resolve_contract_path(
    raw_path: str,
    *,
    repo_root: Path = REPO_ROOT,
    temp_root: Path | None = None,
) -> Path:
    if not raw_path or URL_PATTERN.search(raw_path):
        raise InputIssue("FAIL", "UNSAFE_INPUT_PATH")
    candidate = Path(raw_path)
    if candidate.suffix.lower() != ".json":
        raise InputIssue("FAIL", "INPUT_SUFFIX_INVALID")

    try:
        resolved_repo = repo_root.resolve(strict=True)
        resolved_temp = (temp_root or Path(tempfile.gettempdir())).resolve(strict=True)
    except OSError as exc:
        raise InputIssue("ENVIRONMENT BLOCKED", "INPUT_ROOT_INSPECTION_FAILED") from exc

    if candidate.is_absolute():
        lexical = Path(os.path.abspath(candidate))
        allowed_root = resolved_temp
    else:
        if ".." in candidate.parts:
            raise InputIssue("FAIL", "UNSAFE_INPUT_PATH")
        lexical = Path(os.path.abspath(resolved_repo / candidate))
        allowed_root = resolved_repo

    try:
        lexical.relative_to(allowed_root)
    except ValueError as exc:
        raise InputIssue("FAIL", "UNSAFE_INPUT_PATH") from exc
    ensure_no_reparse_components(allowed_root, lexical)

    try:
        resolved = lexical.resolve(strict=False)
        resolved.relative_to(allowed_root)
    except (OSError, ValueError) as exc:
        raise InputIssue("FAIL", "UNSAFE_INPUT_PATH") from exc
    return resolved


def read_contract(
    raw_path: str,
    *,
    repo_root: Path = REPO_ROOT,
    temp_root: Path | None = None,
) -> dict[str, Any]:
    path = resolve_contract_path(raw_path, repo_root=repo_root, temp_root=temp_root)
    try:
        info = path.stat()
    except FileNotFoundError as exc:
        raise InputIssue("BLOCKED", "INPUT_NOT_FOUND") from exc
    except OSError as exc:
        raise InputIssue("ENVIRONMENT BLOCKED", "INPUT_INSPECTION_FAILED") from exc
    if not stat.S_ISREG(info.st_mode):
        raise InputIssue("FAIL", "INPUT_NOT_REGULAR_FILE")
    if info.st_size > MAX_INPUT_BYTES:
        raise InputIssue("FAIL", "INPUT_SIZE_LIMIT_EXCEEDED")

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise InputIssue("ENVIRONMENT BLOCKED", "INPUT_READ_FAILED") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InputIssue("FAIL", "INVALID_UTF8_INPUT") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputIssue("FAIL", "MALFORMED_JSON") from exc
    if not isinstance(payload, dict):
        raise InputIssue("FAIL", "CONTRACT_ROOT_INVALID")
    return payload


def inspect_contract(
    contract_path: str,
    contract_kind: str,
    *,
    repo_root: Path = REPO_ROOT,
    temp_root: Path | None = None,
) -> dict[str, Any]:
    result = base_result(contract_kind=contract_kind, dry_run=True)
    try:
        payload = read_contract(contract_path, repo_root=repo_root, temp_root=temp_root)
    except InputIssue as exc:
        result["status"] = exc.status
        result["reason_codes"] = [exc.reason_code]
        result["validation_summary"]["input_status"] = exc.status
        result["validation_summary"]["issue_count"] = 1
        return result

    issues, authorized_classes = validate_contract(payload, contract_kind)
    result["validation_summary"] = {
        "input_status": "PASS",
        "structure_status": category_status(issues, "structure"),
        "safety_status": category_status(issues, "safety"),
        "approval_status": category_status(issues, "approval"),
        "permission_status": category_status(issues, "permission"),
        "issue_count": len(issues),
    }
    result["declared_permission_summary"] = {
        "authorized_count": len(authorized_classes),
        "unauthorized_count": len(SIDE_EFFECT_CLASSES) - len(authorized_classes),
        "authorized_classes": authorized_classes,
    }

    if any(item.status == "FAIL" for item in issues):
        result["status"] = "FAIL"
        result["reason_codes"] = [item.code for item in issues]
    elif any(item.status == "BLOCKED" for item in issues):
        result["status"] = "BLOCKED"
        result["reason_codes"] = [item.code for item in issues]
    elif contract_kind == "synthetic":
        result["status"] = "PASS WITH NOTES"
        result["reason_codes"] = ["SYNTHETIC_CONTRACT_VALID"]
    else:
        result["status"] = "PASS"
        result["reason_codes"] = []
    return result


def json_bytes(result: dict[str, Any]) -> bytes:
    encoded = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(encoded) > MAX_OUTPUT_BYTES:
        raise ValueError("bounded JSON output exceeded")
    return encoded


def text_summary(result: dict[str, Any]) -> str:
    reasons = ",".join(result["reason_codes"]) or "NONE"
    return (
        f"{result['status']} {VALIDATOR_ID} kind={result['contract_kind']} "
        f"issues={result['validation_summary']['issue_count']} reasons={reasons}"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a downstream task contract without side effects.")
    parser.add_argument("--contract", required=True, help="Repo-relative or temporary-root JSON contract path")
    parser.add_argument("--contract-kind", required=True, choices=("synthetic", "filled"))
    parser.add_argument("--dry-run", action="store_true", help="Required read-only validation mode")
    parser.add_argument("--json", action="store_true", help="Emit bounded deterministic JSON stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.dry_run:
        result = inspect_contract(args.contract, args.contract_kind)
    else:
        result = base_result(contract_kind=args.contract_kind, dry_run=False)
        result["reason_codes"] = ["DRY_RUN_REQUIRED"]

    if args.json:
        try:
            sys.stdout.buffer.write(json_bytes(result))
        except ValueError:
            fallback = base_result(contract_kind=args.contract_kind, dry_run=bool(args.dry_run))
            fallback["status"] = "FAIL"
            fallback["reason_codes"] = ["OUTPUT_LIMIT_EXCEEDED"]
            fallback["validation_summary"]["issue_count"] = 1
            sys.stdout.buffer.write(json_bytes(fallback))
            return 1
    else:
        print(text_summary(result))

    if result["status"] in {"PASS", "PASS WITH NOTES"}:
        return 0
    if result["status"] == "NOT RUN":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
