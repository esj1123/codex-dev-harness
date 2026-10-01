from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import work_package_conflict_check as preflight
from scripts import work_package_postflight as postflight


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "docs" / "PARALLEL_WORK_PACKAGE_SYNTHETIC_FIXTURE.json"
V2_REQUIRED_COMMAND_IDS = ("core_pytest", "standalone_eval", "quality_gate")


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def write_text(repo: Path, relative: str, content: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def init_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Synthetic Test")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    write_text(repo, ".gitignore", "/local/\n")
    write_text(repo, "seed.txt", "seed\n")
    git(repo, "add", ".gitignore", "seed.txt")
    git(repo, "commit", "-m", "base")
    return repo, git(repo, "rev-parse", "HEAD")


def package(base_sha: str, *, task_id: str = "feature-a", lane: str = "feature") -> dict[str, object]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    payload.update(
        {
            "task_id": task_id,
            "base_sha": base_sha,
            "contract_basis_sha": base_sha,
            "contract_frozen_paths": ["seed.txt"],
            "lane": lane,
            "read_set": ["seed.txt"],
            "write_set": ["feature.txt"],
            "generated_outputs": [],
            "verification_tier": "V2" if lane == "integration" else "V1",
        }
    )
    if lane == "integration":
        payload["verification_contract"]["commands"] = [
            {
                "command_id": command_id,
                "argv": ["{PYTHON}", "-m", command_id],
            }
            for command_id in V2_REQUIRED_COMMAND_IDS
        ]
    return payload


def write_package(repo: Path, payload: dict[str, object], name: str = "feature.json") -> str:
    relative = f"local/work-packages/{name}"
    write_text(repo, relative, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return relative


def commit_file(repo: Path, relative: str, content: str, message: str = "feature") -> None:
    write_text(repo, relative, content)
    git(repo, "add", relative)
    git(repo, "commit", "-m", message)


def inspect(
    repo: Path,
    package_path: str,
    *,
    package_root: Path | None = None,
    task_id: str = "feature-a",
    verification_status: str = "PASS",
    verification_interpreter_id: str | None = None,
    completed_command_ids: list[str] | None = None,
) -> dict[str, object]:
    package_base = package_root if package_root is not None else repo
    payload = json.loads((package_base / package_path).read_text(encoding="utf-8"))
    contract = payload["verification_contract"]
    return postflight.inspect_postflight(
        [package_path],
        task_id=task_id,
        verification_status=verification_status,
        verification_interpreter_id=(
            verification_interpreter_id or contract["interpreter_id"]
        ),
        completed_command_ids=(
            completed_command_ids
            if completed_command_ids is not None
            else [command["command_id"] for command in contract["commands"]]
        ),
        repo_root=repo,
        package_root=package_root,
    )


def test_clean_single_commit_passes_and_matches_preflight_digest(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(repo, package_path)
    expected = preflight.inspect_payloads([payload])

    assert result["status"] == "PASS"
    assert result["plan_digest"] == expected["plan_digest"]
    assert result["verification"]["contract_hash"] == (
        preflight.verification_contract_hash(payload["verification_contract"])
    )
    assert result["verification"]["required_command_ids"] == ["focused_pytest"]
    assert result["verification"]["completed_command_ids"] == ["focused_pytest"]
    assert result["head_sha"] == git(repo, "rev-parse", "HEAD")
    assert result["actual_surface"] == {
        "changed_paths": ["feature.txt"],
        "untracked_paths": [],
        "commit_count": 1,
        "rename_count": 0,
        "delete_count": 0,
    }
    assert result["central_authority_changed"] is False
    assert result["authorization_status"] == "NOT_AUTHENTICATED"
    assert result["performed_actions"] == []
    assert "task_evidence" not in result
    assert postflight.text_summary(result) == (
        "status=PASS task=feature-a changed=1 untracked=0 commits=1 reasons=NONE"
    )


@pytest.mark.parametrize("summary_status", ["PASS", "FAIL"])
def test_opt_in_closeout_invokes_summary_and_retains_pending_target_state(tmp_path: Path, monkeypatch, summary_status) -> None:
    from scripts import task_evidence_summary
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n")
    calls = []
    def inspect_summary(spec, **kwargs):
        calls.append((spec, kwargs))
        return {"status": summary_status, "state": {"completion": False,
            "candidate_binding": "BOUND", "counts": {"completed": 0, "pending": 1, "unknown": 1},
            "gates": {"build": "PENDING", "review": "UNKNOWN"},
            "next_action": "TARGET_OWNER_COMPLETE_PENDING_GATES"}, "performed_actions": []}
    monkeypatch.setattr(task_evidence_summary, "inspect_summary", inspect_summary)
    result = postflight.inspect_postflight([package_path], task_id="feature-a",
        verification_status="PASS", verification_interpreter_id=payload["verification_contract"]["interpreter_id"],
        completed_command_ids=["focused_pytest"], repo_root=repo,
        task_evidence_spec="local/state-spec.json", task_evidence_input_root=tmp_path / "target")
    assert calls == [("local/state-spec.json", {"spec_root": repo, "input_root": tmp_path / "target", "runtime_root": None})]
    assert result["status"] == ("PASS" if summary_status == "PASS" else "BLOCKED")
    assert result["task_evidence"]["state"]["completion"] is False
    assert ("TASK_EVIDENCE_INVALID" in result["reason_codes"]) == (summary_status != "PASS")
    text = postflight.text_summary(result)
    assert text.splitlines()[1] == "task_evidence " + task_evidence_summary.text_summary(result["task_evidence"])
    assert "pending=build pending_omitted=0 unknown=review unknown_omitted=0" in text
    assert str(tmp_path) not in text


@pytest.mark.parametrize("json_mode", [False, True])
@pytest.mark.parametrize(("gate_state", "next_action", "exit_code"), [
    ("PASS", "TARGET_OWNER_REVIEW_COMPLETION", 0),
    ("UNKNOWN", "TARGET_OWNER_RESOLVE_UNKNOWN_GATES", 0),
    ("mismatch", "RESOLVE_EVIDENCE_MISMATCHES", 1),
])
def test_native_closeout_hook_projects_actual_state_without_runtime(
    tmp_path: Path, json_mode: bool, gate_state: str, next_action: str, exit_code: int,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n")
    target = tmp_path / "target"
    target.mkdir()
    private = "PRIVATE_BODY_MUST_NOT_APPEAR"
    write_text(target, "evidence/artifact.json", json.dumps({"private": private}))
    artifact_sha = hashlib.sha256((target / "evidence/artifact.json").read_bytes()).hexdigest()
    state = {"gates": {"build": "UNKNOWN" if gate_state == "UNKNOWN" else "PASS"},
             "evidence": [{"path": "artifact.json", "sha256": artifact_sha}], "private": private}
    write_text(target, "state.json", json.dumps(state))
    state_sha = hashlib.sha256((target / "state.json").read_bytes()).hexdigest()
    spec = {"schema_version": "1", "state": {"path": "state.json", "sha256": state_sha, "pointer": []},
        "evidence": {"root": "evidence", "pointer": ["evidence"]}, "identities": [], "links": [],
        "candidate": {"path": "evidence/artifact.json", "sha256": "b" * 64 if gate_state == "mismatch" else artifact_sha},
        "gates": [{"id": "build", "pointer": ["gates", "build"],
            "states": {"completed": ["PASS"], "pending": ["HOLD"], "unknown": ["UNKNOWN"]},
            "proofs": ["evidence/artifact.json"]}], "history": [], "runtime": []}
    write_text(repo, "local/state-spec.json", json.dumps(spec))
    before = {str(p.relative_to(target)): p.read_bytes() for p in target.rglob("*") if p.is_file()}
    args = [sys.executable, "-B", str(Path(postflight.__file__)), "--repo-root", str(repo),
        "--package", package_path, "--task-id", "feature-a", "--verification-status", "PASS",
        "--verification-interpreter-id", payload["verification_contract"]["interpreter_id"],
        "--completed-command-id", "focused_pytest"]
    if gate_state == "PASS" and not json_mode:
        legacy = subprocess.run(args, capture_output=True, check=False, timeout=30)
        assert legacy.returncode == 0 and not legacy.stderr
        assert legacy.stdout.decode().splitlines() == [
            "status=PASS task=feature-a changed=1 untracked=0 commits=1 reasons=NONE"]
    args += ["--task-evidence-spec", "local/state-spec.json", "--task-evidence-input-root", str(target)]
    if json_mode:
        args.append("--json")
    completed = subprocess.run(args, capture_output=True, check=False, timeout=30)
    assert completed.returncode == exit_code and not completed.stderr
    assert private.encode() not in completed.stdout and str(tmp_path).encode() not in completed.stdout
    assert len(completed.stdout) <= postflight.MAX_OUTPUT_BYTES
    if json_mode:
        report = json.loads(completed.stdout)
        evidence = report["task_evidence"]
        assert report["status"] == ("BLOCKED" if exit_code else "PASS")
        assert report["authorization_status"] == evidence["authorization_status"] == "NOT_AUTHENTICATED"
        assert evidence["state"]["next_action"] == next_action
        assert evidence["state"]["completion"] is (gate_state == "PASS")
        assert evidence["usage"] == [] and evidence["usage_totals"] is None
        assert evidence["performed_actions"] == []
    else:
        assert len(completed.stdout.splitlines()) == 2
        assert f"next_action={next_action}".encode() in completed.stdout
        assert f"completion={gate_state == 'PASS'}".encode() in completed.stdout
        if gate_state == "UNKNOWN":
            assert b"unknown=build unknown_omitted=0" in completed.stdout
        assert b"usage" not in completed.stdout and b"tokens" not in completed.stdout
    assert before == {str(p.relative_to(target)): p.read_bytes() for p in target.rglob("*") if p.is_file()}


def test_incomplete_closeout_arguments_fail_before_observation(monkeypatch) -> None:
    monkeypatch.setattr(postflight, "observe_repository", lambda *a: pytest.fail("unexpected observation"))
    result = postflight.inspect_postflight([], task_id="feature-a", verification_status="PASS",
        verification_interpreter_id="synthetic", completed_command_ids=[], task_evidence_spec="state.json")
    assert result["reason_codes"] == ["TASK_EVIDENCE_ARGUMENTS_INVALID"]


def test_changed_path_outside_write_set_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "outside.txt", "outside\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "WRITE_SET_EXCEEDED" in result["reason_codes"]


def test_declared_generated_output_may_remain_untracked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    payload["write_set"] = ["feature.txt", "generated/result.json"]
    payload["generated_outputs"] = ["generated/result.json"]
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n")
    write_text(repo, "generated/result.json", "{}\n")

    result = inspect(repo, package_path)

    assert result["status"] == "PASS"
    assert result["actual_surface"]["untracked_paths"] == ["generated/result.json"]


def test_undeclared_untracked_output_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "feature\n")
    write_text(repo, "unexpected.txt", "unexpected\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "GENERATED_OUTPUT_SET_EXCEEDED" in result["reason_codes"]


def test_tracked_dirty_state_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "feature\n")
    write_text(repo, "feature.txt", "dirty\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "TRACKED_WORKTREE_DIRTY" in result["reason_codes"]


@pytest.mark.parametrize(
    ("operation", "reason_code"),
    [
        ("rename", "RENAME_NOT_ALLOWED"),
        ("delete", "DELETE_NOT_ALLOWED"),
    ],
)
def test_rename_and_delete_are_blocked(tmp_path: Path, operation: str, reason_code: str) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    payload["contract_frozen_paths"] = [".gitignore"]
    payload["read_set"] = [".gitignore"]
    payload["write_set"] = ["seed.txt", "renamed.txt"]
    package_path = write_package(repo, payload)
    if operation == "rename":
        git(repo, "mv", "seed.txt", "renamed.txt")
    else:
        git(repo, "rm", "seed.txt")
    git(repo, "commit", "-m", operation)

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert reason_code in result["reason_codes"]


def test_feature_lane_requires_exactly_one_commit(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    payload["write_set"] = ["feature.txt", "second.txt"]
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n", "first")
    commit_file(repo, "second.txt", "second\n", "second")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "LANE_COMMIT_COUNT_INVALID" in result["reason_codes"]


def test_missing_lane_commit_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "LANE_COMMIT_COUNT_INVALID" in result["reason_codes"]


def test_base_that_is_not_an_ancestor_is_blocked(tmp_path: Path) -> None:
    repo, _ = init_repo(tmp_path)
    package_path = write_package(repo, package("a" * 40))
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["BASE_NOT_ANCESTOR"]


def test_feature_lane_cannot_change_integration_only_path(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "STATUS.md", "status\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "INTEGRATION_ONLY_PATH" in result["reason_codes"]


def test_actual_contract_surface_change_requires_contract_reopen(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    package_path = write_package(repo, payload)
    commit_file(repo, "seed.txt", "changed contract\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "CONTRACT_CHANGE_REQUIRED" in result["reason_codes"]
    assert "WRITE_SET_EXCEEDED" in result["reason_codes"]


def test_declared_parent_directory_covers_actual_child_path(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    payload["write_set"] = ["generated"]
    package_path = write_package(repo, payload)
    commit_file(repo, "generated/result.txt", "result\n")

    result = inspect(repo, package_path)

    assert result["status"] == "PASS"


def test_case_variant_declared_path_covers_actual_path(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha)
    payload["write_set"] = ["FEATURE.TXT"]
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(repo, package_path)

    assert result["status"] == "PASS"


@pytest.mark.parametrize(
    ("verification_status", "expected_status", "reason_code"),
    [
        ("FAIL", "FAIL", "VERIFICATION_FAILED"),
        ("NOT_RUN", "BLOCKED", "VERIFICATION_NOT_RUN"),
        ("ENVIRONMENT_BLOCKED", "ENVIRONMENT BLOCKED", "VERIFICATION_ENVIRONMENT_BLOCKED"),
    ],
)
def test_verification_status_controls_outcome(
    tmp_path: Path,
    verification_status: str,
    expected_status: str,
    reason_code: str,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(repo, package_path, verification_status=verification_status)

    assert result["status"] == expected_status
    assert reason_code in result["reason_codes"]


@pytest.mark.parametrize(
    ("kwargs", "reason_code"),
    [
        (
            {"verification_interpreter_id": "python-3.12.13-pytest-8.0.0"},
            "VERIFICATION_INTERPRETER_MISMATCH",
        ),
        (
            {"completed_command_ids": []},
            "VERIFICATION_COMMANDS_INCOMPLETE",
        ),
        (
            {"completed_command_ids": ["focused_pytest", "unknown"]},
            "VERIFICATION_COMMAND_SET_INVALID",
        ),
    ],
)
def test_pass_requires_exact_interpreter_and_complete_command_set(
    tmp_path: Path,
    kwargs: dict[str, object],
    reason_code: str,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(repo, package_path, **kwargs)

    assert result["status"] == "BLOCKED"
    assert reason_code in result["reason_codes"]


def test_postflight_inherits_v2_required_command_failure(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha, task_id="integration-a", lane="integration")
    payload["verification_contract"]["commands"] = [
        {
            "command_id": "full_pytest",
            "argv": ["{PYTHON}", "-m", "pytest", "tests"],
        }
    ]
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(
        repo,
        package_path,
        task_id="integration-a",
        completed_command_ids=["full_pytest"],
    )

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == ["V2_REQUIRED_COMMANDS_MISSING"]


@pytest.mark.parametrize(
    ("interpreter_id", "command_ids", "reason_code"),
    [
        ("C:/private/python.exe", [], "VERIFICATION_INTERPRETER_INVALID"),
        (
            "python-3.12.13-pytest-9.0.3",
            ["focused_pytest", "focused_pytest"],
            "VERIFICATION_COMMAND_ID_SET_INVALID",
        ),
        (
            "python-3.12.13-pytest-9.0.3",
            [f"command-{index}" for index in range(17)],
            "VERIFICATION_COMMAND_ID_SET_INVALID",
        ),
        (
            "python-3.12.13-pytest-9.0.3",
            ["C:/private/result"],
            "VERIFICATION_COMMAND_ID_SET_INVALID",
        ),
    ],
)
def test_invalid_verifier_inputs_fail_before_git_observation_without_reflection(
    tmp_path: Path,
    interpreter_id: str,
    command_ids: list[str],
    reason_code: str,
) -> None:
    result = postflight.inspect_postflight(
        ["missing.json"],
        task_id="feature-a",
        verification_status="PASS",
        verification_interpreter_id=interpreter_id,
        completed_command_ids=command_ids,
        repo_root=tmp_path,
    )
    serialized = postflight.safe_output_bytes(result).decode("ascii")

    assert result["status"] == "FAIL"
    assert result["reason_codes"] == [reason_code]
    assert "private" not in serialized
    assert "command-16" not in serialized


def test_safe_output_replaces_oversized_payload_with_bounded_failure() -> None:
    result = postflight.base_result()
    result["actual_surface"]["changed_paths"] = [
        f"generated/{index:04d}.txt" for index in range(2000)
    ]

    payload = postflight.safe_output_bytes(result)
    decoded = json.loads(payload)

    assert len(payload) <= postflight.MAX_OUTPUT_BYTES
    assert decoded["status"] == "FAIL"
    assert decoded["reason_codes"] == ["OUTPUT_TOO_LARGE"]
    assert decoded["actual_surface"]["changed_paths"] == []


def test_diff_check_failure_is_blocked(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "trailing whitespace \n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert "DIFF_CHECK_FAILED" in result["reason_codes"]


def test_crlf_line_endings_do_not_fail_diff_check(tmp_path: Path) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    git(repo, "config", "core.autocrlf", "false")
    (repo / "feature.txt").write_bytes(b"feature\r\n")
    git(repo, "add", "feature.txt")
    git(repo, "commit", "-m", "feature")

    result = inspect(repo, package_path)

    assert result["status"] == "PASS"
    assert "DIFF_CHECK_FAILED" not in result["reason_codes"]


def test_not_a_repository_is_environment_blocked(tmp_path: Path) -> None:
    payload = package("a" * 40)
    package_path = write_package(tmp_path, payload)

    result = inspect(tmp_path, package_path)

    assert result["status"] == "ENVIRONMENT BLOCKED"
    assert result["reason_codes"] == ["GIT_OBSERVATION_FAILED"]


def test_cli_json_is_deterministic_bounded_and_path_safe(
    tmp_path: Path,
    capsys,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha))
    commit_file(repo, "feature.txt", "feature\n")
    args = [
        "--repo-root",
        str(repo),
        "--package",
        package_path,
        "--task-id",
        "feature-a",
        "--verification-status",
        "PASS",
        "--verification-interpreter-id",
        "python-3.12.13-pytest-9.0.3",
        "--completed-command-id",
        "focused_pytest",
        "--json",
    ]

    first_exit = postflight.main(args)
    first = capsys.readouterr().out
    second_exit = postflight.main(args)
    second = capsys.readouterr().out

    assert first_exit == second_exit == 0
    assert first == second
    assert first.endswith("\n")
    assert len(first.encode("utf-8")) <= postflight.MAX_OUTPUT_BYTES
    assert str(tmp_path) not in first
    assert json.loads(first)["performed_actions"] == []
    assert json.loads(first)["authorization_status"] == "NOT_AUTHENTICATED"


def test_external_package_root_postflight_passes_with_preflight_digest(
    tmp_path: Path,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    control = tmp_path / "control"
    package_path = "work-packages/feature.json"
    payload = package(base_sha)
    target = control / package_path
    target.parent.mkdir(parents=True)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    commit_file(repo, "feature.txt", "feature\n")

    result = inspect(
        repo,
        package_path,
        package_root=control,
    )
    expected = preflight.inspect_packages(
        [package_path],
        repo_root=repo,
        package_root=control,
    )

    assert result["status"] == "PASS"
    assert result["plan_digest"] == expected["plan_digest"]
    encoded = json.dumps(result, sort_keys=True)
    assert str(repo) not in encoded
    assert str(control) not in encoded


def test_external_package_root_cli_is_deterministic_and_path_safe(
    tmp_path: Path,
    capsys,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    control = tmp_path / "control"
    package_path = "work-packages/feature.json"
    payload = package(base_sha)
    target = control / package_path
    target.parent.mkdir(parents=True)
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    commit_file(repo, "feature.txt", "feature\n")
    args = [
        "--repo-root",
        str(repo),
        "--package-root",
        str(control),
        "--package",
        package_path,
        "--task-id",
        "feature-a",
        "--verification-status",
        "PASS",
        "--verification-interpreter-id",
        "python-3.12.13-pytest-9.0.3",
        "--completed-command-id",
        "focused_pytest",
        "--json",
    ]

    assert postflight.main(args) == 0
    first = capsys.readouterr().out
    assert postflight.main(args) == 0
    second = capsys.readouterr().out

    assert first == second
    assert str(repo) not in first
    assert str(control) not in first
    assert json.loads(first)["status"] == "PASS"


@pytest.mark.parametrize("oversized", [False, True])
def test_native_json_exit_matches_pass_origin_envelope(oversized: bool) -> None:
    # Stub only the observation boundary. Exercise the real CLI, serializer,
    # stdout bytes and native process exit, not just safe_output_bytes().
    count = 2000 if oversized else 1
    driver = (
        "from scripts import work_package_postflight as checker\n"
        "result = checker.base_result()\n"
        "result['status'] = 'PASS'\n"
        f"result['actual_surface']['changed_paths'] = [f'generated/{{i:04d}}.txt' for i in range({count})]\n"
        "checker.inspect_postflight = lambda *args, **kwargs: result\n"
        "raise SystemExit(checker.main([\n"
        "    '--package', 'synthetic.json', '--task-id', 'synthetic',\n"
        "    '--verification-status', 'PASS',\n"
        "    '--verification-interpreter-id', 'synthetic-python', '--json'\n"
        "]))\n"
    )
    completed = subprocess.run(
        [sys.executable, "-B", "-c", driver],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        timeout=30,
    )
    report = json.loads(completed.stdout)

    assert len(completed.stdout) <= postflight.MAX_OUTPUT_BYTES
    assert len(completed.stdout.splitlines()) == 1
    assert report["authorization_status"] == "NOT_AUTHENTICATED"
    assert report["performed_actions"] == []
    if oversized:
        assert report["status"] == "FAIL"
        assert report["reason_codes"] == ["OUTPUT_TOO_LARGE"]
        assert report["actual_surface"]["changed_paths"] == []
        assert completed.returncode == 1
    else:
        assert report["status"] == "PASS"
        assert report["reason_codes"] == []
        assert report["actual_surface"]["changed_paths"] == ["generated/0000.txt"]
        assert completed.returncode == 0


@pytest.mark.parametrize("json_mode", [False, True])
@pytest.mark.parametrize("oversized", [False, True])
def test_native_closeout_size_limit_owns_text_and_json_exit(json_mode: bool, oversized: bool) -> None:
    count = 2000 if oversized else 1
    driver = (
        "from scripts import work_package_postflight as checker\n"
        "result = checker.base_result()\n"
        "result['status'] = 'PASS'\n"
        "result['task_evidence'] = {'status': 'PASS', 'state': {'candidate_binding': 'BOUND', "
        "'completion': True, 'counts': {'completed': 1, 'pending': 0, 'unknown': 0}, "
        "'gates': {'build': 'COMPLETED'}, 'next_action': 'TARGET_OWNER_REVIEW_COMPLETION'}, "
        f"'usage': ['PRIVATE_BODY_MUST_NOT_APPEAR' * {count}]}}\n"
        "checker.inspect_postflight = lambda *args, **kwargs: result\n"
        "args = ['--package', 'synthetic.json', '--task-id', 'synthetic', "
        "'--verification-status', 'PASS', '--verification-interpreter-id', 'synthetic-python']\n"
        f"args += {['--json'] if json_mode else []!r}\n"
        "raise SystemExit(checker.main(args))\n"
    )
    completed = subprocess.run([sys.executable, "-B", "-c", driver], cwd=REPO_ROOT,
                               capture_output=True, check=False, timeout=30)
    assert not completed.stderr and len(completed.stdout) <= postflight.MAX_OUTPUT_BYTES
    assert completed.returncode == (1 if oversized else 0)
    if json_mode:
        report = json.loads(completed.stdout)
        assert report["status"] == ("FAIL" if oversized else "PASS")
        if oversized:
            assert report["reason_codes"] == ["OUTPUT_TOO_LARGE"]
            assert "task_evidence" not in report
    else:
        assert b"PRIVATE_BODY_MUST_NOT_APPEAR" not in completed.stdout
        assert b"status=FAIL" in completed.stdout if oversized else b"status=PASS" in completed.stdout
        if oversized:
            assert b"reasons=OUTPUT_TOO_LARGE" in completed.stdout
            assert len(completed.stdout.splitlines()) == 1
        else:
            assert b"task_evidence status=PASS candidate_binding=BOUND completion=True" in completed.stdout
            assert len(completed.stdout.splitlines()) == 2


@pytest.mark.parametrize(
    ("lane", "relative"),
    [
        ("feature", "STATUS.md"),
        ("contract", "scripts/gates/new_review_fixture.py"),
    ],
)
def test_untracked_central_path_is_reported_and_blocked(
    tmp_path: Path, lane: str, relative: str,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    package_path = write_package(repo, package(base_sha, lane=lane))
    commit_file(repo, "feature.txt", "feature\n")
    write_text(repo, relative, "synthetic\n")

    result = inspect(repo, package_path)

    assert result["status"] == "BLOCKED"
    assert result["actual_surface"]["changed_paths"] == ["feature.txt"]
    assert result["actual_surface"]["untracked_paths"] == [relative]
    assert result["central_authority_changed"] is True
    assert "INTEGRATION_ONLY_PATH" in result["reason_codes"]
    assert "GENERATED_OUTPUT_SET_EXCEEDED" in result["reason_codes"]


@pytest.mark.parametrize("lane", ["feature", "contract", "integration"])
def test_declared_untracked_central_output_requires_integration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, lane: str,
) -> None:
    repo, base_sha = init_repo(tmp_path)
    payload = package(base_sha, lane=lane)
    relative = "scripts/gates/new_review_fixture.py"
    payload["write_set"] = ["feature.txt", "scripts"]
    payload["generated_outputs"] = [relative]
    package_path = write_package(repo, payload)
    commit_file(repo, "feature.txt", "feature\n")
    write_text(repo, relative, "synthetic\n")

    if lane != "integration":
        preflight_result = preflight.inspect_payloads([payload])
        assert preflight_result["status"] == "FAIL"
        assert "INTEGRATION_ONLY_PATH" in preflight_result["reason_codes"]
        # Keep postflight independently protective even if a prior/alternate
        # preflight accepted the broad declaration. Git observation is real.
        monkeypatch.setattr(
            postflight,
            "load_payloads",
            lambda *_args, **_kwargs: (
                [payload], {"plan_digest": preflight.plan_digest([payload])}
            ),
        )

    result = inspect(repo, package_path)

    assert result["central_authority_changed"] is True
    assert result["actual_surface"]["untracked_paths"] == [relative]
    assert "GENERATED_OUTPUT_SET_EXCEEDED" not in result["reason_codes"]
    assert result["authorization_status"] == "NOT_AUTHENTICATED"
    if lane == "integration":
        assert result["status"] == "PASS"
        assert result["reason_codes"] == []
    else:
        assert result["status"] == "BLOCKED"
        assert result["reason_codes"] == ["INTEGRATION_ONLY_PATH"]
