from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "docs" / "DOWNSTREAM_TASK_CONTRACT_SYNTHETIC_FIXTURE.json"
BOUNDARY_PATH = REPO_ROOT / "docs" / "DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md"

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
ALLOWED_DATA_CLASSES = {
    "generalized_identifier",
    "repo_relative_reference",
    "commit_identifier",
    "bounded_status",
    "reason_code",
    "verification_outcome",
    "safe_summary",
}
FORBIDDEN_DATA_CLASSES = {
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
}
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
    "<CLEAN_OR_DIRTY_STATE>",
    "<DOWNSTREAM_REPO_ID>",
    "<HEAD_COMMIT>",
    "<NO_TOUCH_PATHS>",
    "<UPSTREAM_REF>",
    "<WORKING_BRANCH>",
}
WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")
IPV4_VALUE = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")


def fixture_text() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


def load_fixture() -> dict[str, Any]:
    return json.loads(fixture_text())


def strings_in(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for child in value for item in strings_in(child)]
    if isinstance(value, dict):
        return [item for child in value.values() for item in strings_in(child)]
    return []


def validate_fixture(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if set(payload) != TOP_LEVEL_KEYS:
        errors.append("top-level keys")

    for section_name, expected_keys in NESTED_KEYS.items():
        section_value = payload.get(section_name)
        if not isinstance(section_value, dict) or set(section_value) != expected_keys:
            errors.append(f"{section_name} keys")

    repository = payload.get("repository", {})
    if isinstance(repository, dict):
        expected_repository_values = {
            "access_class": "<ACCESS_CLASS>",
            "base_commit": "<BASE_COMMIT>",
            "clean_state": "<CLEAN_OR_DIRTY_STATE>",
            "head_commit": "<HEAD_COMMIT>",
            "identifier": "<DOWNSTREAM_REPO_ID>",
            "upstream_ref": "<UPSTREAM_REF>",
            "working_branch": "<WORKING_BRANCH>",
            "worktree_boundary": "<APPROVED_WORKTREE>",
        }
        for key, expected in expected_repository_values.items():
            if repository.get(key) != expected:
                errors.append(f"repository placeholder: {key}")
        if repository.get("allowed_access_classes") != ALLOWED_ACCESS_CLASSES:
            errors.append("allowed access classes")

    if payload.get("synthetic") is not True:
        errors.append("synthetic flag")
    if payload.get("status") != "NOT RUN":
        errors.append("fixture status")
    if payload.get("performed_actions") != []:
        errors.append("performed actions")

    approvals = payload.get("approvals", {})
    if isinstance(approvals, dict) and any(
        approvals.get(key) is not False
        for key in [
            "owner_approval_present",
            "target_repository_approval_present",
            "target_rules_reviewed",
        ]
    ):
        errors.append("approval state")

    permissions = payload.get("side_effect_permissions")
    if not isinstance(permissions, list):
        errors.append("side-effect permissions")
    else:
        if [item.get("class") for item in permissions if isinstance(item, dict)] != SIDE_EFFECT_CLASSES:
            errors.append("side-effect classes")
        for item in permissions:
            if not isinstance(item, dict) or set(item) != {"approval_ref", "authorized", "class", "status"}:
                errors.append("side-effect permission keys")
                continue
            if item["authorized"] is not False or item["approval_ref"] is not None or item["status"] != "NOT RUN":
                errors.append("side-effect authorization")

    for value in strings_in(payload):
        if value.startswith(("http://", "https://", "ssh://", "git@")):
            errors.append("remote URL value")
        if value.startswith("/") or WINDOWS_ABSOLUTE_PATH.match(value):
            errors.append("absolute path value")
        if IPV4_VALUE.search(value):
            errors.append("IP-like value")

    return errors


def test_fixture_is_canonical_json_and_links_phase_11a() -> None:
    text = fixture_text()
    payload = json.loads(text)
    boundary = BOUNDARY_PATH.read_text(encoding="utf-8")

    assert text == json.dumps(payload, indent=2, sort_keys=True) + "\n"
    assert "\r" not in text
    assert payload["schema_version"] == "1"
    assert payload["fixture_id"] == "phase_11b_synthetic_downstream_task_contract"
    assert payload["human_contract_ref"] == (
        "docs/DOWNSTREAM_PRODUCT_INTEGRATION_BOUNDARY_REVIEW.md#required-downstream-task-contract"
    )
    assert payload["reason_codes"] == [
        "SYNTHETIC_CONTRACT_ONLY",
        "NO_DOWNSTREAM_TARGET_SELECTED",
        "NO_APPROVAL_REFERENCE",
    ]
    assert "synthetic downstream task-contract fixture" in boundary
    assert validate_fixture(payload) == []


def test_repository_scope_and_required_placeholders_are_complete() -> None:
    payload = load_fixture()
    repository = payload["repository"]
    scope = payload["scope"]

    assert repository["allowed_access_classes"] == ALLOWED_ACCESS_CLASSES
    assert repository["identifier"] == "<DOWNSTREAM_REPO_ID>"
    assert repository["worktree_boundary"] == "<APPROVED_WORKTREE>"
    assert repository["working_branch"] == "<WORKING_BRANCH>"
    assert scope == {
        "allowed_files": ["<ALLOWED_FILE_LIST>"],
        "no_touch_paths": ["<NO_TOUCH_PATHS>"],
        "write_scope": "<WRITE_SCOPE>",
    }
    assert REQUIRED_PLACEHOLDERS <= set(strings_in(payload))


def test_approvals_and_side_effect_permissions_are_all_not_authorized() -> None:
    payload = load_fixture()
    approvals = payload["approvals"]
    permissions = payload["side_effect_permissions"]

    assert approvals == {
        "approval_ref": "<APPROVAL_REF>",
        "owner_approval_present": False,
        "target_repository_approval_present": False,
        "target_rules_reviewed": False,
    }
    assert [item["class"] for item in permissions] == SIDE_EFFECT_CLASSES
    assert all(item["authorized"] is False for item in permissions)
    assert all(item["approval_ref"] is None for item in permissions)
    assert all(item["status"] == "NOT RUN" for item in permissions)
    assert payload["performed_actions"] == []


def test_data_policy_is_bounded_and_contains_no_live_values() -> None:
    payload = load_fixture()
    data_policy = payload["data_policy"]

    assert set(data_policy["allowed_classes"]) == ALLOWED_DATA_CLASSES
    assert set(data_policy["forbidden_classes"]) == FORBIDDEN_DATA_CLASSES
    assert not any(
        error in {"remote URL value", "absolute path value", "IP-like value"}
        for error in validate_fixture(payload)
    )


def test_verification_rollback_closeout_and_stop_conditions_are_complete() -> None:
    payload = load_fixture()

    assert payload["rollback_cleanup"] == {
        "cleanup_plan": "<CLEANUP_PLAN>",
        "overwrite_allowed": False,
        "retention_policy": "<RETENTION_POLICY>",
        "rollback_plan": "<ROLLBACK_PLAN>",
    }
    assert payload["verification"]["commands"] == ["<VERIFICATION_COMMAND>"]
    assert payload["verification"]["expected_statuses"] == [
        "PASS",
        "PASS WITH NOTES",
        "BLOCKED",
        "FAIL",
        "NOT RUN",
        "ENVIRONMENT BLOCKED",
    ]
    assert payload["verification"]["not_run_items"] == [
        {
            "action": "<NOT_RUN_ACTION>",
            "reason_code": "SEPARATE_APPROVAL_REQUIRED",
            "status": "NOT RUN",
        }
    ]
    assert payload["closeout"]["changed_files"] == []
    assert payload["closeout"]["commands_run"] == []
    assert payload["closeout"]["result"] == "NOT RUN"
    assert payload["stop_conditions"] == STOP_CONDITIONS


def test_validator_rejects_unsafe_synthetic_mutations() -> None:
    missing_identifier = copy.deepcopy(load_fixture())
    del missing_identifier["repository"]["identifier"]

    authorized_push = copy.deepcopy(load_fixture())
    next(item for item in authorized_push["side_effect_permissions"] if item["class"] == "push")[
        "authorized"
    ] = True

    remote_repository = copy.deepcopy(load_fixture())
    remote_repository["repository"]["identifier"] = "https://example.invalid/private"

    performed_action = copy.deepcopy(load_fixture())
    performed_action["performed_actions"] = ["push"]

    cases = [
        (missing_identifier, "repository keys"),
        (authorized_push, "side-effect authorization"),
        (remote_repository, "remote URL value"),
        (performed_action, "performed actions"),
    ]
    for payload, expected_error in cases:
        assert expected_error in validate_fixture(payload)
