from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts import downstream_task_contract_validator as validator


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "docs" / "DOWNSTREAM_TASK_CONTRACT_SYNTHETIC_FIXTURE.json"
PLAN_PATH = REPO_ROOT / "docs" / "DOWNSTREAM_TASK_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN.md"


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def set_permission(payload: dict[str, object], class_name: str, authorized: bool) -> None:
    permissions = payload["side_effect_permissions"]
    assert isinstance(permissions, list)
    item = next(item for item in permissions if isinstance(item, dict) and item["class"] == class_name)
    item["authorized"] = authorized
    item["approval_ref"] = f"approval-{class_name}" if authorized else None


def make_filled_contract(*, access_class: str = "local_read_only") -> dict[str, object]:
    payload = copy.deepcopy(load_fixture())
    payload["fixture_id"] = "phase-11d-filled-contract"
    payload["synthetic"] = False
    payload["reason_codes"] = []
    payload["repository"] = {
        "access_class": access_class,
        "allowed_access_classes": list(validator.ALLOWED_ACCESS_CLASSES),
        "base_commit": "a" * 40,
        "clean_state": "clean",
        "head_commit": "b" * 40,
        "identifier": "downstream/example",
        "upstream_ref": "origin/main",
        "working_branch": "main",
        "worktree_boundary": "approved-worktree",
    }
    payload["scope"] = {
        "allowed_files": ["docs/README.md"],
        "no_touch_paths": ["restricted/config.json"],
        "write_scope": "read_only",
    }
    payload["commands"] = [
        {
            "approval_ref": "approval-command-1",
            "command": "git status --short",
            "effect_classes": ["repository_access", "execute"],
            "status": "NOT RUN",
        }
    ]
    payload["approvals"] = {
        "approval_ref": "approval-phase-11d",
        "owner_approval_present": True,
        "target_repository_approval_present": True,
        "target_rules_reviewed": True,
    }
    payload["rollback_cleanup"] = {
        "cleanup_plan": "no cleanup required",
        "overwrite_allowed": False,
        "retention_policy": "no persistence",
        "rollback_plan": "no mutation to roll back",
    }
    payload["verification"] = {
        "commands": ["python -m pytest tests"],
        "expected_statuses": list(validator.EXPECTED_STATUSES),
        "not_run_items": [
            {
                "action": "downstream_write",
                "reason_code": "SEPARATE_APPROVAL_REQUIRED",
                "status": "NOT RUN",
            }
        ],
    }
    payload["closeout"] = {
        "changed_files": [],
        "commands_not_run": ["git status --short"],
        "commands_run": [],
        "next_step": "owner review",
        "result": "NOT RUN",
        "risks": ["external approval evidence not authenticated"],
        "safe_evidence_refs": ["evidence/checkpoint"],
    }
    set_permission(payload, "repository_access", True)
    set_permission(payload, "execute", True)
    return payload


def inspect_temp(tmp_path: Path, payload: object, kind: str) -> dict[str, object]:
    path = tmp_path / "contract.json"
    write_json(path, payload)
    return validator.inspect_contract(
        str(path),
        kind,
        repo_root=REPO_ROOT,
        temp_root=tmp_path,
    )


def test_implementation_plan_fixes_scope_cli_and_non_goals() -> None:
    text = PLAN_PATH.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    for path in [
        "docs/DOWNSTREAM_TASK_CONTRACT_VALIDATOR_IMPLEMENTATION_PLAN.md",
        "scripts/downstream_task_contract_validator.py",
        "tests/test_downstream_task_contract_validator.py",
    ]:
        assert f"`{path}`" in text
    assert (
        "python scripts/downstream_task_contract_validator.py --contract <JSON_PATH> "
        "--contract-kind synthetic|filled --dry-run [--json]"
    ) in text
    for boundary in [
        "does not inspect a downstream repository",
        "does not authenticate approval evidence",
        "does not create or persist a filled contract",
        "does not change eval behavior",
    ]:
        assert boundary in normalized


def test_current_synthetic_fixture_passes_with_notes() -> None:
    result = validator.inspect_contract(
        "docs/DOWNSTREAM_TASK_CONTRACT_SYNTHETIC_FIXTURE.json",
        "synthetic",
    )

    assert result["status"] == "PASS WITH NOTES"
    assert result["reason_codes"] == ["SYNTHETIC_CONTRACT_VALID"]
    assert result["validation_summary"]["issue_count"] == 0
    assert result["declared_permission_summary"] == {
        "authorized_count": 0,
        "unauthorized_count": 16,
        "authorized_classes": [],
    }
    assert result["performed_actions"] == []


def test_valid_filled_contract_passes_internal_validation_only(tmp_path: Path) -> None:
    result = inspect_temp(tmp_path, make_filled_contract(), "filled")

    assert result["status"] == "PASS"
    assert result["reason_codes"] == []
    assert result["declared_permission_summary"] == {
        "authorized_count": 2,
        "unauthorized_count": 14,
        "authorized_classes": ["repository_access", "execute"],
    }
    assert set(result["external_state"].values()) == {"NOT RUN"}
    assert result["performed_actions"] == []


def test_missing_dry_run_returns_not_run_without_inspection(monkeypatch, capsys) -> None:
    def unexpected_inspection(*_args, **_kwargs):
        raise AssertionError("inspection must not run")

    monkeypatch.setattr(validator, "inspect_contract", unexpected_inspection)

    exit_code = validator.main(
        [
            "--contract",
            "missing.json",
            "--contract-kind",
            "filled",
            "--json",
        ]
    )
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert result["status"] == "NOT RUN"
    assert result["reason_codes"] == ["DRY_RUN_REQUIRED"]
    assert result["performed_actions"] == []


def test_repo_relative_and_temporary_root_paths_are_accepted(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    relative_path = repo / "contracts" / "synthetic.json"
    write_json(relative_path, load_fixture())
    relative = validator.inspect_contract(
        "contracts/synthetic.json",
        "synthetic",
        repo_root=repo,
        temp_root=tmp_path,
    )

    external_path = tmp_path / "external.json"
    write_json(external_path, make_filled_contract())
    external = validator.inspect_contract(
        str(external_path),
        "filled",
        repo_root=repo,
        temp_root=tmp_path,
    )

    assert relative["status"] == "PASS WITH NOTES"
    assert external["status"] == "PASS"


@pytest.mark.parametrize(
    ("raw_path", "expected_reason"),
    [
        ("https://example.invalid/contract.json", "UNSAFE_INPUT_PATH"),
        ("../contract.json", "UNSAFE_INPUT_PATH"),
        ("contracts/contract.txt", "INPUT_SUFFIX_INVALID"),
    ],
)
def test_unsafe_input_path_shapes_fail(tmp_path: Path, raw_path: str, expected_reason: str) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = validator.inspect_contract(
        raw_path,
        "synthetic",
        repo_root=repo,
        temp_root=tmp_path,
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == [expected_reason]


def test_absolute_path_outside_temp_root_is_rejected(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside.json"
    repo.mkdir()
    allowed.mkdir()
    write_json(outside, load_fixture())

    result = validator.inspect_contract(
        str(outside),
        "synthetic",
        repo_root=repo,
        temp_root=allowed,
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["UNSAFE_INPUT_PATH"]


def test_missing_and_directory_inputs_are_distinguished(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    directory = repo / "directory.json"
    directory.mkdir()

    missing = validator.inspect_contract(
        "missing.json",
        "synthetic",
        repo_root=repo,
        temp_root=tmp_path,
    )
    not_file = validator.inspect_contract(
        "directory.json",
        "synthetic",
        repo_root=repo,
        temp_root=tmp_path,
    )

    assert missing["status"] == "BLOCKED"
    assert missing["reason_codes"] == ["INPUT_NOT_FOUND"]
    assert not_file["status"] == "FAIL"
    assert not_file["reason_codes"] == ["INPUT_NOT_REGULAR_FILE"]


def test_reparse_input_is_rejected_without_reading(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    path = repo / "contract.json"
    write_json(path, load_fixture())
    monkeypatch.setattr(validator, "is_reparse_point", lambda candidate: candidate == path)

    result = validator.inspect_contract(
        "contract.json",
        "synthetic",
        repo_root=repo,
        temp_root=tmp_path,
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["REPARSE_INPUT_FORBIDDEN"]


def test_malformed_invalid_utf8_and_oversized_inputs_fail(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    malformed = repo / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    invalid_utf8 = repo / "invalid.json"
    invalid_utf8.write_bytes(b"\xff")
    oversized = repo / "oversized.json"
    oversized.write_bytes(b" " * (validator.MAX_INPUT_BYTES + 1))

    cases = [
        (malformed.name, "MALFORMED_JSON"),
        (invalid_utf8.name, "INVALID_UTF8_INPUT"),
        (oversized.name, "INPUT_SIZE_LIMIT_EXCEEDED"),
    ]
    for raw_path, expected_reason in cases:
        result = validator.inspect_contract(
            raw_path,
            "synthetic",
            repo_root=repo,
            temp_root=tmp_path,
        )
        assert result["status"] == "FAIL"
        assert result["reason_codes"] == [expected_reason]


def test_structure_rejects_unknown_missing_and_non_object_payloads() -> None:
    unknown = load_fixture()
    unknown["unexpected"] = True
    missing = load_fixture()
    del missing["repository"]

    unknown_issues, _ = validator.validate_contract(unknown, "synthetic")
    missing_issues, _ = validator.validate_contract(missing, "synthetic")
    root_issues, _ = validator.validate_contract([], "synthetic")

    assert "TOP_LEVEL_FIELDS_INVALID" in [item.code for item in unknown_issues]
    assert "TOP_LEVEL_FIELDS_INVALID" in [item.code for item in missing_issues]
    assert "CONTRACT_ROOT_INVALID" in [item.code for item in root_issues]


def test_synthetic_mode_rejects_kind_approval_permission_and_action_mutations(tmp_path: Path) -> None:
    payload = load_fixture()
    payload["synthetic"] = False
    payload["approvals"]["owner_approval_present"] = True
    payload["performed_actions"] = ["repository_access"]
    set_permission(payload, "repository_access", True)

    result = inspect_temp(tmp_path, payload, "synthetic")

    assert result["status"] == "FAIL"
    for reason in [
        "CONTRACT_KIND_MISMATCH",
        "PERFORMED_ACTIONS_NOT_EMPTY",
        "SYNTHETIC_APPROVAL_STATE_INVALID",
        "SYNTHETIC_PERMISSION_STATE_INVALID",
    ]:
        assert reason in result["reason_codes"]


def test_filled_mode_blocks_placeholders_and_missing_approvals(tmp_path: Path) -> None:
    payload = make_filled_contract()
    payload["repository"]["identifier"] = "<DOWNSTREAM_REPO_ID>"
    payload["approvals"]["target_rules_reviewed"] = False

    result = inspect_temp(tmp_path, payload, "filled")

    assert result["status"] == "BLOCKED"
    assert "UNRESOLVED_PLACEHOLDER" in result["reason_codes"]
    assert "REQUIRED_APPROVAL_MISSING" in result["reason_codes"]


@pytest.mark.parametrize(
    ("access_class", "extra_permission"),
    [
        ("local_read_only", "network_read"),
        ("remote_read_only", "local_write"),
        ("local_write", "push"),
    ],
)
def test_access_class_is_a_permission_ceiling(
    tmp_path: Path,
    access_class: str,
    extra_permission: str,
) -> None:
    payload = make_filled_contract(access_class=access_class)
    if access_class == "remote_read_only":
        set_permission(payload, "network_read", True)
    if access_class == "local_write":
        set_permission(payload, "local_write", True)
    set_permission(payload, extra_permission, True)

    result = inspect_temp(tmp_path, payload, "filled")

    assert result["status"] == "BLOCKED"
    assert "ACCESS_PERMISSION_CONFLICT" in result["reason_codes"]


def test_remote_write_keeps_each_permission_separately_approval_gated(tmp_path: Path) -> None:
    payload = make_filled_contract(access_class="remote_write")
    set_permission(payload, "push", True)
    payload["commands"][0]["effect_classes"].append("push")

    result = inspect_temp(tmp_path, payload, "filled")

    assert result["status"] == "PASS"
    assert result["declared_permission_summary"]["authorized_classes"] == [
        "repository_access",
        "execute",
        "push",
    ]


@pytest.mark.parametrize(
    ("effects", "expected_reason", "expected_status"),
    [
        (["repository_access", "push"], "COMMAND_PERMISSION_CONFLICT", "BLOCKED"),
        (["repository_access", "unknown"], "UNKNOWN_COMMAND_EFFECT", "FAIL"),
        (["repository_access", "repository_access"], "DUPLICATE_COMMAND_EFFECT", "FAIL"),
    ],
)
def test_command_effects_fail_closed(
    tmp_path: Path,
    effects: list[str],
    expected_reason: str,
    expected_status: str,
) -> None:
    payload = make_filled_contract()
    payload["commands"][0]["effect_classes"] = effects

    result = inspect_temp(tmp_path, payload, "filled")

    assert result["status"] == expected_status
    assert expected_reason in result["reason_codes"]


@pytest.mark.parametrize(
    ("unsafe_value", "expected_reason"),
    [
        ("https://example.invalid/private", "URL_VALUE_FORBIDDEN"),
        ("C:/private/contract", "ABSOLUTE_PATH_VALUE_FORBIDDEN"),
        ("private\\contract", "BACKSLASH_PATH_FORBIDDEN"),
        ("docs/../private", "PARENT_TRAVERSAL_VALUE_FORBIDDEN"),
        (".".join(["10", "20", "30", "40"]), "IP_VALUE_FORBIDDEN"),
        ("token=synthetic-value", "SECRET_LIKE_VALUE_FORBIDDEN"),
    ],
)
def test_unsafe_dynamic_values_are_rejected_without_echo(
    tmp_path: Path,
    unsafe_value: str,
    expected_reason: str,
) -> None:
    payload = make_filled_contract()
    payload["closeout"]["next_step"] = unsafe_value

    result = inspect_temp(tmp_path, payload, "filled")
    encoded = validator.json_bytes(result).decode("utf-8")

    assert result["status"] == "FAIL"
    assert expected_reason in result["reason_codes"]
    assert unsafe_value not in encoded


def test_scope_command_string_and_reason_code_bounds_are_enforced(tmp_path: Path) -> None:
    payload = make_filled_contract()
    payload["scope"]["allowed_files"] = [f"docs/file-{index}.md" for index in range(65)]
    payload["commands"] = copy.deepcopy(payload["commands"]) * 33
    payload["closeout"]["next_step"] = "x" * 513
    payload["reason_codes"] = [f"REASON_{index}" for index in range(17)]

    result = inspect_temp(tmp_path, payload, "filled")

    assert result["status"] == "FAIL"
    for reason in [
        "SCOPE_LIST_INVALID",
        "COMMANDS_INVALID",
        "VALUE_SIZE_LIMIT_EXCEEDED",
        "REASON_CODES_INVALID",
    ]:
        assert reason in result["reason_codes"]


def test_fixed_policy_and_side_effect_class_drift_is_rejected(tmp_path: Path) -> None:
    payload = make_filled_contract()
    payload["data_policy"]["allowed_classes"] = []
    payload["stop_conditions"] = []
    payload["side_effect_permissions"][0]["class"] = "unknown"

    result = inspect_temp(tmp_path, payload, "filled")

    assert result["status"] == "FAIL"
    assert "ALLOWED_DATA_CLASSES_INVALID" in result["reason_codes"]
    assert "STOP_CONDITIONS_INVALID" in result["reason_codes"]
    assert "SIDE_EFFECT_CLASSES_INVALID" in result["reason_codes"]


def test_json_output_is_deterministic_bounded_and_has_final_newline() -> None:
    result = validator.inspect_contract(
        "docs/DOWNSTREAM_TASK_CONTRACT_SYNTHETIC_FIXTURE.json",
        "synthetic",
    )

    first = validator.json_bytes(result)
    second = validator.json_bytes(result)

    assert first == second
    assert first.endswith(b"\n")
    assert len(first) <= validator.MAX_OUTPUT_BYTES
    assert first == (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def test_plain_and_json_cli_outputs_are_safe_and_non_persistent(capsys) -> None:
    args = [
        "--contract",
        "docs/DOWNSTREAM_TASK_CONTRACT_SYNTHETIC_FIXTURE.json",
        "--contract-kind",
        "synthetic",
        "--dry-run",
    ]
    before = FIXTURE_PATH.read_bytes()

    plain_exit = validator.main(args)
    plain = capsys.readouterr().out
    json_exit = validator.main([*args, "--json"])
    json_output = capsys.readouterr().out

    assert plain_exit == 0
    assert json_exit == 0
    assert "PASS WITH NOTES" in plain
    assert str(FIXTURE_PATH) not in plain
    assert str(FIXTURE_PATH) not in json_output
    assert "<DOWNSTREAM_REPO_ID>" not in plain
    assert "<DOWNSTREAM_REPO_ID>" not in json_output
    assert json.loads(json_output)["performed_actions"] == []
    assert FIXTURE_PATH.read_bytes() == before


def test_environment_input_issue_is_safely_reported(monkeypatch) -> None:
    def blocked_read(*_args, **_kwargs):
        raise validator.InputIssue("ENVIRONMENT BLOCKED", "INPUT_READ_FAILED")

    monkeypatch.setattr(validator, "read_contract", blocked_read)

    result = validator.inspect_contract("not-reported.json", "filled")

    assert result["status"] == "ENVIRONMENT BLOCKED"
    assert result["reason_codes"] == ["INPUT_READ_FAILED"]
    assert "not-reported.json" not in validator.json_bytes(result).decode("utf-8")


def test_validation_reads_only_the_selected_file_and_creates_no_output(tmp_path: Path) -> None:
    selected = tmp_path / "selected.json"
    sibling = tmp_path / "sibling.json"
    write_json(selected, make_filled_contract())
    sibling.write_text("not json", encoding="utf-8")
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir() if path.is_file()}

    result = validator.inspect_contract(
        str(selected),
        "filled",
        repo_root=REPO_ROOT,
        temp_root=tmp_path,
    )
    after = {path.name: path.read_bytes() for path in tmp_path.iterdir() if path.is_file()}

    assert result["status"] == "PASS"
    assert before == after
    assert sorted(path.name for path in tmp_path.iterdir()) == ["selected.json", "sibling.json"]
