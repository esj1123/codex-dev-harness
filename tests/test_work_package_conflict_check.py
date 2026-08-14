from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import stat
from types import SimpleNamespace

import pytest

from scripts import work_package_conflict_check as checker


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "docs" / "PARALLEL_WORK_PACKAGE_SYNTHETIC_FIXTURE.json"
CHANGE_CONTROL_PATH = REPO_ROOT / "docs" / "CHANGE_CONTROL.md"
TASK_PROMPT_PATH = REPO_ROOT / "prompts" / "task_contract" / "task_contract.md"
CLOSEOUT_PROMPT_PATH = REPO_ROOT / "prompts" / "task_contract" / "verification_closeout.md"


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def package(task_id: str, *, lane: str = "feature", suffix: str = "") -> dict[str, object]:
    payload = copy.deepcopy(load_fixture())
    payload["task_id"] = task_id
    payload["lane"] = lane
    payload["read_set"] = [
        *payload["contract_frozen_paths"],
        f"scripts/input{suffix}.py",
    ]
    payload["write_set"] = [f"scripts/output{suffix}.py", f"tests/test_output{suffix}.py"]
    if lane == "integration":
        payload["verification_tier"] = "V2"
    return payload


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def test_tracked_synthetic_fixture_is_canonical_and_valid() -> None:
    payload = load_fixture()

    assert checker.package_issues(payload) == []
    assert FIXTURE_PATH.read_text(encoding="utf-8") == json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_parallel_contract_and_verification_tiers_are_documented() -> None:
    change_control = CHANGE_CONTROL_PATH.read_text(encoding="utf-8")
    task_prompt = TASK_PROMPT_PATH.read_text(encoding="utf-8")
    closeout_prompt = CLOSEOUT_PROMPT_PATH.read_text(encoding="utf-8")

    for field in [
        "task_id",
        "base_sha",
        "depends_on",
        "read_set",
        "write_set",
        "generated_outputs",
        "verification_tier",
        "verification_contract",
        "declared_side_effects",
    ]:
        assert f"`{field}`" in change_control
    for path in checker.INTEGRATION_ONLY_EXACT:
        assert f"`{path}`" in change_control
    assert "local/work-packages/" in task_prompt
    assert "scripts/work_package_conflict_check.py" in task_prompt
    assert "scripts/work_package_postflight.py" in task_prompt
    assert "plan_digest" in closeout_prompt
    assert "actual changed files remained within the declared write set" in closeout_prompt
    assert {"contract_basis_sha", "contract_frozen_paths"} <= checker.EXPECTED_KEYS
    assert {"agent_profile_id", "agent_profile_hash"} <= checker.PROFILE_BOUND_KEYS
    assert "`contract_basis_sha`" in change_control
    assert "`contract_frozen_paths`" in change_control
    assert "`authorization_status`" in change_control
    assert "`NOT_AUTHENTICATED`" in change_control
    assert "`verification_contract`" in change_control
    assert "`interpreter_id`" in change_control
    assert "exact argument list" in change_control


def test_disjoint_packages_are_parallelizable() -> None:
    packages = [
        package("feature-a", suffix="-a"),
        package("feature-b", suffix="-b"),
    ]
    result = checker.inspect_payloads(packages)

    assert result["status"] == "PASS"
    assert result["parallelizable"] is True
    assert result["plan_digest"] == checker.plan_digest(packages)
    assert len(result["plan_digest"]) == 64
    assert result["reason_codes"] == []
    assert result["authorization_status"] == "NOT_AUTHENTICATED"
    assert result["performed_actions"] == []


def test_plan_digest_is_order_independent_and_content_sensitive() -> None:
    left = package("feature-a", suffix="-a")
    right = package("feature-b", suffix="-b")

    forward = checker.inspect_payloads([left, right])
    reverse = checker.inspect_payloads([right, left])
    changed = copy.deepcopy(right)
    changed["write_set"] = ["scripts/changed.py"]
    changed_result = checker.inspect_payloads([left, changed])

    assert forward["plan_digest"] == reverse["plan_digest"]
    assert forward["plan_digest"] != changed_result["plan_digest"]


def test_plan_digest_binds_exact_verification_contract() -> None:
    original = package("feature-a")
    changed = copy.deepcopy(original)
    changed["verification_contract"]["commands"][0]["argv"] = [
        "{PYTHON}",
        "-m",
        "pytest",
        "tests/test_contracts.py",
        "-q",
    ]

    assert checker.plan_digest([original]) != checker.plan_digest([changed])


def test_plan_digest_binds_agent_profile_identity() -> None:
    original = package("feature-a")
    changed = copy.deepcopy(original)
    changed["agent_profile_id"] = "critical_implementer"
    changed["agent_profile_hash"] = "f" * 64

    assert checker.package_issues(original) == []
    assert checker.package_issues(changed) == []
    assert checker.plan_digest([original]) != checker.plan_digest([changed])


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("agent_profile_id", "UNKNOWN PROFILE", "AGENT_PROFILE_ID_INVALID"),
        ("agent_profile_hash", "not-a-hash", "AGENT_PROFILE_HASH_INVALID"),
    ],
)
def test_agent_profile_binding_is_validated(
    field: str, value: str, reason: str
) -> None:
    payload = package("feature-a")
    payload[field] = value

    assert reason in checker.package_issues(payload)


def test_write_write_conflict_is_blocked_without_disclosing_paths() -> None:
    left = package("feature-a", suffix="-a")
    right = package("feature-b", suffix="-b")
    right["write_set"] = list(left["write_set"])

    result = checker.inspect_payloads([left, right])

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["WRITE_SET_CONFLICT"]
    assert result["conflicts"] == [
        {"left_task_id": "feature-a", "right_task_id": "feature-b", "kind": "write_write"}
    ]
    assert "scripts/" not in json.dumps(result)


def test_undeclared_write_read_dependency_is_blocked() -> None:
    left = package("producer", suffix="-producer")
    right = package("consumer", suffix="-consumer")
    right["read_set"] = [
        *right["contract_frozen_paths"],
        left["write_set"][0],
    ]

    result = checker.inspect_payloads([left, right])

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["UNDECLARED_DEPENDENCY"]


def test_declared_dependency_requires_serialization() -> None:
    left = package("producer", suffix="-producer")
    right = package("consumer", suffix="-consumer")
    right["read_set"] = [
        *right["contract_frozen_paths"],
        left["write_set"][0],
    ]
    right["depends_on"] = ["producer"]

    result = checker.inspect_payloads([left, right])

    assert result["status"] == "PASS WITH NOTES"
    assert result["parallelizable"] is False
    assert result["reason_codes"] == ["SERIALIZATION_REQUIRED"]


@pytest.mark.parametrize(
    ("mutator", "reason_code"),
    [
        (lambda items: items[1].update(task_id=items[0]["task_id"]), "DUPLICATE_TASK_ID"),
        (
            lambda items: items[1].update(
                base_sha="b" * 40,
                contract_basis_sha="b" * 40,
            ),
            "BASE_SHA_MISMATCH",
        ),
        (lambda items: items[1].update(depends_on=["missing-task"]), "UNKNOWN_DEPENDENCY"),
        (
            lambda items: (
                items[0].update(depends_on=[items[1]["task_id"]]),
                items[1].update(depends_on=[items[0]["task_id"]]),
            ),
            "DEPENDENCY_CYCLE",
        ),
    ],
)
def test_package_group_failures_are_blocked(mutator, reason_code: str) -> None:
    items = [package("feature-a", suffix="-a"), package("feature-b", suffix="-b")]
    mutator(items)

    result = checker.inspect_payloads(items)

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == [reason_code]


def test_feature_lane_cannot_claim_integration_only_path() -> None:
    payload = package("feature-a")
    payload["write_set"] = ["STATUS.md"]

    assert checker.package_issues(payload) == ["INTEGRATION_ONLY_PATH"]


def test_integration_only_paths_match_authority_manifest() -> None:
    manifest = json.loads(
        Path("docs/AUTHORITY_MANIFEST.json").read_text(encoding="utf-8")
    )

    assert checker.INTEGRATION_ONLY_EXACT == set(manifest["integration_only_exact"])
    assert set(checker.INTEGRATION_ONLY_PREFIXES) == set(
        manifest["integration_only_prefixes"]
    )


def test_integration_lane_can_claim_central_paths() -> None:
    payload = package("integration-a", lane="integration")
    payload["write_set"] = [
        "STATUS.md",
        "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
        "artifacts/corpus-digest.json",
    ]

    result = checker.inspect_payloads([payload])

    assert result["status"] == "PASS"
    assert result["parallelizable"] is True


@pytest.mark.parametrize(
    ("left_path", "right_path"),
    [
        ("docs/Policy.md", "docs/policy.md"),
        ("package", "package/module.py"),
        ("package/module.py", "package"),
    ],
)
def test_windows_case_and_parent_child_write_conflicts_are_blocked(
    left_path: str,
    right_path: str,
) -> None:
    left = package("feature-a", suffix="-a")
    right = package("feature-b", suffix="-b")
    left["write_set"] = [left_path]
    right["write_set"] = [right_path]

    result = checker.inspect_payloads([left, right])

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["WRITE_SET_CONFLICT"]


def test_parent_child_write_read_requires_dependency() -> None:
    producer = package("producer", suffix="-producer")
    consumer = package("consumer", suffix="-consumer")
    producer["write_set"] = ["generated"]
    consumer["read_set"] = [
        *consumer["contract_frozen_paths"],
        "generated/result.json",
    ]

    blocked = checker.inspect_payloads([producer, consumer])
    consumer["depends_on"] = ["producer"]
    serialized = checker.inspect_payloads([producer, consumer])

    assert blocked["status"] == "BLOCKED"
    assert blocked["reason_codes"] == ["UNDECLARED_DEPENDENCY"]
    assert serialized["status"] == "PASS WITH NOTES"
    assert serialized["reason_codes"] == ["SERIALIZATION_REQUIRED"]


@pytest.mark.parametrize(
    "unsafe_path",
    [
        "docs/trailing.",
        "docs/trailing ",
        "docs/trailing./file.md",
        "docs/trailing /file.md",
    ],
)
def test_windows_trailing_dot_or_space_paths_are_rejected(unsafe_path: str) -> None:
    payload = package("feature-a")
    payload["write_set"] = [unsafe_path]

    assert checker.package_issues(payload) == ["WRITE_SET_PATH_INVALID"]


@pytest.mark.parametrize(
    "unsafe_path",
    [
        "docs/CON",
        "docs/nul.txt",
        "docs/file?.md",
        "docs/file:stream",
        "docs/" + "a" * 256,
    ],
)
def test_shared_windows_path_policy_rejects_unsafe_work_package_paths(
    unsafe_path: str,
) -> None:
    payload = package("feature-a")
    payload["write_set"] = [unsafe_path]

    assert checker.package_issues(payload) == ["WRITE_SET_PATH_INVALID"]


def test_case_variant_duplicates_are_rejected_within_path_sets() -> None:
    payload = package("feature-a")
    payload["read_set"] = [
        *payload["contract_frozen_paths"],
        "docs/Policy.md",
        "docs/policy.md",
    ]

    assert checker.package_issues(payload) == ["READ_SET_CANONICAL_DUPLICATE"]


def test_case_variant_integration_only_path_is_blocked() -> None:
    payload = package("feature-a")
    payload["write_set"] = ["status.md"]

    assert checker.package_issues(payload) == ["INTEGRATION_ONLY_PATH"]


def test_contract_basis_and_frozen_paths_are_enforced() -> None:
    missing = package("feature-a")
    missing["contract_frozen_paths"] = []
    mismatched = package("feature-b")
    mismatched["contract_basis_sha"] = "b" * 40
    not_read = package("feature-c")
    not_read["read_set"] = ["scripts/input.py"]
    changed = package("feature-d")
    changed["write_set"] = list(changed["contract_frozen_paths"])

    assert checker.package_issues(missing) == ["CONTRACT_FROZEN_PATHS_REQUIRED"]
    assert checker.package_issues(mismatched) == ["CONTRACT_BASIS_MISMATCH"]
    assert checker.package_issues(not_read) == ["CONTRACT_FROZEN_PATH_NOT_READ"]
    assert checker.package_issues(changed) == ["CONTRACT_CHANGE_REQUIRED"]


def test_batch_requires_one_canonical_frozen_contract_surface() -> None:
    left = package("feature-a", suffix="-a")
    right = package("feature-b", suffix="-b")
    right["contract_frozen_paths"] = ["docs/OTHER_INTERFACE.md"]
    right["read_set"] = [
        *right["contract_frozen_paths"],
        "scripts/input-b.py",
    ]

    result = checker.inspect_payloads([left, right])

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["CONTRACT_FROZEN_PATHS_MISMATCH"]


@pytest.mark.parametrize(
    ("key", "value", "reason_code"),
    [
        ("write_set", ["/absolute/file.py"], "WRITE_SET_PATH_INVALID"),
        ("write_set", ["../outside.py"], "WRITE_SET_PATH_INVALID"),
        ("write_set", ["scripts\\file.py"], "WRITE_SET_PATH_INVALID"),
        ("write_set", ["https://example.invalid/file.py"], "WRITE_SET_PATH_INVALID"),
        ("verification_tier", "V3", "FEATURE_VERIFICATION_TIER_INVALID"),
        ("declared_side_effects", ["push"], "REMOTE_SIDE_EFFECT_REQUIRES_INTEGRATION"),
    ],
)
def test_unsafe_or_inconsistent_package_fields_are_rejected(
    key: str,
    value: object,
    reason_code: str,
) -> None:
    payload = package("feature-a")
    payload[key] = value

    assert reason_code in checker.package_issues(payload)


@pytest.mark.parametrize(
    ("side_effect", "reason_code"),
    [
        ("repository_access", "REPOSITORY_ACCESS_SIDE_EFFECT_REQUIRED"),
        ("execute", "EXECUTE_SIDE_EFFECT_REQUIRED"),
        ("local_write", "LOCAL_WRITE_SIDE_EFFECT_REQUIRED"),
        ("stage", "STAGE_SIDE_EFFECT_REQUIRED"),
        ("commit", "COMMIT_SIDE_EFFECT_REQUIRED"),
    ],
)
def test_required_side_effect_classes_fail_closed(
    side_effect: str,
    reason_code: str,
) -> None:
    payload = package("feature-a")
    payload["declared_side_effects"].remove(side_effect)

    assert reason_code in checker.package_issues(payload)


@pytest.mark.parametrize(
    ("mutation", "reason_code"),
    [
        (
            lambda contract: contract.update(interpreter_id="Python 3.12"),
            "VERIFICATION_INTERPRETER_ID_INVALID",
        ),
        (
            lambda contract: contract.update(commands=[]),
            "VERIFICATION_COMMANDS_INVALID",
        ),
        (
            lambda contract: contract["commands"][0].update(
                argv=["C:\\Python312\\python.exe", "-m", "pytest"]
            ),
            "VERIFICATION_ARGV_INVALID",
        ),
        (
            lambda contract: contract.update(
                commands=[
                    contract["commands"][0],
                    copy.deepcopy(contract["commands"][0]),
                ]
            ),
            "VERIFICATION_COMMAND_ID_DUPLICATE",
        ),
    ],
)
def test_verification_contract_is_exact_bounded_and_path_safe(
    mutation,
    reason_code: str,
) -> None:
    payload = package("feature-a")
    mutation(payload["verification_contract"])

    assert checker.package_issues(payload) == [reason_code]


def test_generated_outputs_must_be_in_write_set() -> None:
    payload = package("feature-a")
    payload["generated_outputs"] = ["generated/result.json"]

    assert checker.package_issues(payload) == ["GENERATED_OUTPUT_OUTSIDE_WRITE_SET"]


def test_cli_reads_repo_relative_packages_and_emits_deterministic_json(
    tmp_path: Path,
    capsys,
) -> None:
    repo = tmp_path / "repo"
    package_path = repo / "local" / "work-packages" / "feature.json"
    write_json(package_path, package("feature-a"))

    args = [
        "--repo-root",
        str(repo),
        "--package",
        "local/work-packages/feature.json",
        "--json",
    ]
    first_exit = checker.main(args)
    first = capsys.readouterr().out
    second_exit = checker.main(args)
    second = capsys.readouterr().out

    assert first_exit == second_exit == 0
    assert first == second
    assert first.endswith("\n")
    assert len(first.encode("utf-8")) <= checker.MAX_OUTPUT_BYTES
    result = json.loads(first)
    assert result["status"] == "PASS"
    assert result["authorization_status"] == "NOT_AUTHENTICATED"
    assert result["performed_actions"] == []
    assert str(tmp_path) not in first


@pytest.mark.parametrize(
    ("relative", "content", "reason_code"),
    [
        ("missing.json", None, "PACKAGE_MISSING"),
        ("package.txt", "{}", "PACKAGE_PATH_INVALID"),
        ("package.json", "{", "PACKAGE_JSON_INVALID"),
    ],
)
def test_file_input_failures_are_bounded(
    tmp_path: Path,
    relative: str,
    content: str | None,
    reason_code: str,
) -> None:
    if content is not None:
        path = tmp_path / relative
        path.write_text(content, encoding="utf-8")

    result = checker.inspect_packages([relative], repo_root=tmp_path)

    assert result["status"] in ("BLOCKED", "FAIL")
    assert result["reason_codes"] == [reason_code]
    assert result["performed_actions"] == []


def test_oversized_package_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "package.json"
    path.write_bytes(b" " * (checker.MAX_INPUT_BYTES + 1))

    result = checker.inspect_packages(["package.json"], repo_root=tmp_path)

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["PACKAGE_TOO_LARGE"]


def test_external_package_root_preserves_same_root_result_and_cli_output(
    tmp_path: Path,
    capsys,
) -> None:
    target = tmp_path / "target"
    control = tmp_path / "control"
    target.mkdir()
    relative = "work-packages/feature.json"
    write_json(control / relative, package("feature-a"))

    same_root = checker.inspect_packages([relative], repo_root=control)
    external = checker.inspect_packages(
        [relative],
        repo_root=target,
        package_root=control,
    )

    assert external == same_root
    args = [
        "--repo-root",
        str(target),
        "--package-root",
        str(control),
        "--package",
        relative,
        "--json",
    ]
    assert checker.main(args) == 0
    output = capsys.readouterr().out
    assert json.loads(output) == external
    assert str(target) not in output
    assert str(control) not in output


@pytest.mark.parametrize("relative", ["../package.json", "C:/package.json", "package.txt"])
def test_external_package_name_fails_closed(tmp_path: Path, relative: str) -> None:
    control = tmp_path / "control"
    control.mkdir()

    result = checker.inspect_packages(
        [relative],
        repo_root=tmp_path,
        package_root=control,
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["PACKAGE_PATH_INVALID"]


def test_unc_and_unsafe_physical_package_roots_fail_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    control = tmp_path / "control"
    write_json(control / "package.json", package("feature-a"))

    unc = checker.inspect_packages(
        ["package.json"],
        repo_root=tmp_path,
        package_root=Path(r"\\server\share"),
    )
    assert unc["reason_codes"] == ["PACKAGE_ROOT_INVALID"]

    monkeypatch.setattr(checker, "_is_unsafe_link", lambda _info: True)
    unsafe = checker.inspect_packages(
        ["package.json"],
        repo_root=tmp_path,
        package_root=control,
    )
    assert unsafe["reason_codes"] == ["PACKAGE_ROOT_UNSAFE"]


@pytest.mark.parametrize(
    "mode,attributes",
    [
        (stat.S_IFLNK, 0),
        (stat.S_IFDIR, 0x400),
    ],
)
def test_symlink_and_junction_reparse_metadata_are_unsafe(
    mode: int,
    attributes: int,
) -> None:
    info = SimpleNamespace(st_mode=mode, st_file_attributes=attributes)

    assert checker._is_unsafe_link(info) is True


def test_external_package_hardlink_is_rejected(tmp_path: Path) -> None:
    control = tmp_path / "control"
    source = control / "package.json"
    alias = control / "alias.json"
    write_json(source, package("feature-a"))
    os.link(source, alias)

    result = checker.inspect_packages(
        ["package.json"],
        repo_root=tmp_path,
        package_root=control,
    )

    assert result["reason_codes"] == ["PACKAGE_MULTIPLE_LINKS"]


@pytest.mark.parametrize("drift_field", ["st_mtime_ns", "st_ctime_ns"])
def test_external_package_metadata_drift_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    drift_field: str,
) -> None:
    control = tmp_path / "control"
    write_json(control / "package.json", package("feature-a"))
    original_fstat = checker.os.fstat
    calls = 0

    def drifting_fstat(fd: int):
        nonlocal calls
        calls += 1
        info = original_fstat(fd)
        if calls != 2:
            return info
        values = {
            "st_dev": info.st_dev,
            "st_ino": info.st_ino,
            "st_mode": info.st_mode,
            "st_nlink": info.st_nlink,
            "st_size": info.st_size,
            "st_mtime_ns": info.st_mtime_ns,
            "st_ctime_ns": info.st_ctime_ns,
            "st_file_attributes": getattr(info, "st_file_attributes", 0),
        }
        values[drift_field] += 1
        return SimpleNamespace(**values)

    monkeypatch.setattr(checker.os, "fstat", drifting_fstat)
    result = checker.inspect_packages(
        ["package.json"],
        repo_root=tmp_path,
        package_root=control,
    )

    assert result["reason_codes"] == ["PACKAGE_IDENTITY_DRIFT"]
