from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from scripts import generate_checksums
from scripts import release_evidence_preflight as preflight


@dataclass(frozen=True)
class SyntheticRepo:
    root: Path
    source_commit: str
    artifact_commit: str


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def commit_all(root: Path, message: str) -> str:
    run_git(root, "add", ".")
    run_git(root, "commit", "-m", message)
    return run_git(root, "rev-parse", "HEAD")


def sync_upstream(root: Path, commit: str | None = None) -> None:
    target = commit or run_git(root, "rev-parse", "HEAD")
    run_git(root, "update-ref", "refs/remotes/origin/main", target)


def init_repo(root: Path) -> None:
    root.mkdir(parents=True)
    run_git(root, "init")
    run_git(root, "config", "core.autocrlf", "false")
    run_git(root, "config", "user.email", "synthetic@example.invalid")
    run_git(root, "config", "user.name", "Synthetic Tester")
    run_git(root, "branch", "-M", "main")


def configure_upstream(root: Path, commit: str) -> None:
    run_git(root, "remote", "add", "origin", "synthetic-remote")
    sync_upstream(root, commit)
    run_git(root, "branch", "--set-upstream-to=origin/main", "main")


def write_policy_inputs(root: Path) -> None:
    for relative_path in preflight.POLICY_PATHS:
        write(root / relative_path, f"# {Path(relative_path).stem}\n")


def canonical_manifest_digest(root: Path) -> str:
    path = root / preflight.MANIFEST_PATH
    data = generate_checksums.read_regular_file(root, path, "release manifest fixture")
    return hashlib.sha256(generate_checksums.canonical_text_bytes(data)).hexdigest()


def write_evidence(
    root: Path,
    source_commit: str,
    *,
    provenance_commit: str | None = None,
    repository: str | None = "example/repository",
    git_ref: str | None = "main",
) -> None:
    provenance_basis = provenance_commit or source_commit
    manifest: dict[str, object] = {
        "schema_version": "1",
        "git_commit": source_commit,
        "included_roots": ["LICENSE", "SECURITY.md"],
        "files": [{"path": "LICENSE"}, {"path": "SECURITY.md"}],
    }
    if repository is not None:
        manifest["repository"] = repository
    if git_ref is not None:
        manifest["git_ref"] = git_ref
    write_json(
        root / preflight.MANIFEST_PATH,
        manifest,
    )
    manifest_digest = canonical_manifest_digest(root)
    bound_repository = repository if repository is not None else "UNKNOWN"
    bound_git_ref = git_ref if git_ref is not None else "UNKNOWN"
    write_json(
        root / "artifacts/sbom.spdx.json",
        {
            "spdxVersion": "SPDX-2.3",
            "documentNamespace": (
                "https://example.invalid/codex-dev-harness/spdx/"
                f"{manifest_digest}"
            ),
            "annotations": [
                {
                    "comment": (
                        f"manifest={preflight.MANIFEST_PATH} "
                        f"sha256={manifest_digest}"
                    )
                }
            ],
            "packages": [
                {
                    "name": bound_repository,
                    "versionInfo": source_commit,
                    "licenseDeclared": "MIT",
                    "licenseConcluded": "MIT",
                    "copyrightText": "Copyright (c) 2026 esj1123",
                }
            ],
        },
    )
    write_json(
        root / "artifacts/sbom.cdx.json",
        {
            "bomFormat": "CycloneDX",
            "metadata": {
                "component": {
                    "name": bound_repository,
                    "version": source_commit,
                    "licenses": [{"license": {"id": "MIT"}}],
                    "properties": [
                        {"name": "git_ref", "value": bound_git_ref},
                        {"name": "manifest_path", "value": preflight.MANIFEST_PATH},
                        {"name": "manifest_sha256", "value": manifest_digest},
                    ],
                }
            },
        },
    )
    manifest_product = {
        "name": preflight.MANIFEST_PATH,
        "digest": {"sha256": manifest_digest},
    }
    write(
        root / "artifacts/provenance.intoto.jsonl",
        json.dumps(
            {
                "_type": "https://in-toto.io/Statement/v1",
                "subject": [manifest_product],
                "predicate": {
                    "repo": {
                        "repository": bound_repository,
                        "git_ref": bound_git_ref,
                        "git_commit": provenance_basis,
                    },
                    "input_manifest": {
                        "path": preflight.MANIFEST_PATH,
                        "digest": {"sha256": manifest_digest},
                    },
                    "products": [manifest_product],
                    "checksum_entries": [
                        {"path": preflight.MANIFEST_PATH, "sha256": manifest_digest}
                    ],
                },
            },
            sort_keys=True,
        )
        + "\n",
    )
    write_json(
        root / "artifacts/eval-report.json",
        {
            "schema_version": "1",
            "total_cases": 1,
            "passed_cases": 1,
            "failed_cases": 0,
        },
    )
    checksums_path = root / "artifacts/checksums.sha256"
    lines = generate_checksums.build_checksum_lines(
        root,
        root / "artifacts/release-manifest.json",
        checksums_path,
        allow_missing=False,
    )
    generate_checksums.write_checksums(lines, checksums_path)


def make_repo(
    tmp_path: Path,
    *,
    provenance_commit: str | None = None,
    source_override: str | None = None,
    evidence_mutator: Callable[[Path], None] | None = None,
    repository: str | None = "example/repository",
    git_ref: str | None = "main",
) -> SyntheticRepo:
    root = tmp_path / "repo"
    init_repo(root)
    write_policy_inputs(root)
    source_commit = commit_all(root, "source basis")
    evidence_source = source_override or source_commit
    write_evidence(
        root,
        evidence_source,
        provenance_commit=provenance_commit,
        repository=repository,
        git_ref=git_ref,
    )
    if evidence_mutator is not None:
        evidence_mutator(root)
        regenerate_checksums(root)
    artifact_commit = commit_all(root, "release evidence")
    configure_upstream(root, artifact_commit)
    return SyntheticRepo(root, evidence_source, artifact_commit)


def regenerate_checksums(root: Path) -> None:
    checksums_path = root / "artifacts/checksums.sha256"
    lines = generate_checksums.build_checksum_lines(
        root,
        root / "artifacts/release-manifest.json",
        checksums_path,
        allow_missing=False,
    )
    generate_checksums.write_checksums(lines, checksums_path)


def mutate_evidence_binding(root: Path, mode: str) -> None:
    bad_digest = "0" * 64
    if mode == "manifest_bytes_changed":
        path = root / preflight.MANIFEST_PATH
        value = json.loads(path.read_text(encoding="utf-8"))
        value["fixture_note"] = "manifest bytes changed after bindings were generated"
        write_json(path, value)
        return

    if mode.startswith("spdx_"):
        path = root / "artifacts/sbom.spdx.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        if mode == "spdx_annotation_missing":
            value.pop("annotations")
        elif mode == "spdx_annotation_mismatch":
            value["annotations"][0]["comment"] = (
                f"manifest={preflight.MANIFEST_PATH} sha256={bad_digest}"
            )
        elif mode == "spdx_namespace_mismatch":
            value["documentNamespace"] = (
                "https://example.invalid/codex-dev-harness/spdx/" + bad_digest
            )
        else:  # pragma: no cover - protects the test helper contract.
            raise AssertionError(f"unknown mutation mode: {mode}")
        write_json(path, value)
        return

    if mode.startswith("cyclonedx_"):
        path = root / "artifacts/sbom.cdx.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        component = value["metadata"]["component"]
        properties = component["properties"]
        if mode == "cyclonedx_manifest_digest_missing":
            component["properties"] = [
                item for item in properties if item["name"] != "manifest_sha256"
            ]
        elif mode == "cyclonedx_manifest_digest_mismatch":
            next(item for item in properties if item["name"] == "manifest_sha256")["value"] = bad_digest
        elif mode == "cyclonedx_manifest_path_mismatch":
            next(item for item in properties if item["name"] == "manifest_path")["value"] = "artifacts/other.json"
        elif mode == "cyclonedx_repository_mismatch":
            component["name"] = "other/repository"
        elif mode == "cyclonedx_ref_mismatch":
            next(item for item in properties if item["name"] == "git_ref")["value"] = "other"
        else:  # pragma: no cover - protects the test helper contract.
            raise AssertionError(f"unknown mutation mode: {mode}")
        write_json(path, value)
        return

    path = root / "artifacts/provenance.intoto.jsonl"
    value = json.loads(path.read_text(encoding="utf-8"))
    predicate = value["predicate"]
    if mode == "provenance_input_missing":
        predicate.pop("input_manifest")
    elif mode == "provenance_input_mismatch":
        predicate["input_manifest"]["digest"]["sha256"] = bad_digest
    elif mode == "provenance_input_path_mismatch":
        predicate["input_manifest"]["path"] = "artifacts/other.json"
    elif mode == "provenance_subject_mismatch":
        value["subject"][0]["digest"]["sha256"] = bad_digest
    elif mode == "provenance_products_mismatch":
        predicate["products"][0]["digest"]["sha256"] = bad_digest
    elif mode == "provenance_checksum_mismatch":
        predicate["checksum_entries"][0]["sha256"] = bad_digest
    elif mode == "provenance_repository_mismatch":
        predicate["repo"]["repository"] = "other/repository"
    elif mode == "provenance_ref_mismatch":
        predicate["repo"]["git_ref"] = "other"
    else:  # pragma: no cover - protects the test helper contract.
        raise AssertionError(f"unknown mutation mode: {mode}")
    write(path, json.dumps(value, sort_keys=True) + "\n")


def assert_readiness(
    result: dict[str, object],
    *,
    refresh: str,
    release: str,
) -> None:
    assert result["schema_version"] == "2"
    assert result["refresh_readiness"] == refresh
    assert result["release_readiness"] == release
    assert result["readiness"] == refresh


def test_clean_evidence_passes_and_keeps_states_separate(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "PASS"
    assert_readiness(result, refresh="READY", release="READY")
    assert result["reason_codes"] == []
    assert result["repository_state"]["head_commit"] == repo.artifact_commit
    assert result["repository_state"]["pushed_commit"] == repo.artifact_commit
    assert result["repository_state"]["pushed_commit_basis"] == "local_tracking_ref"
    assert result["evidence_state"]["source_basis_commit"] == repo.source_commit
    assert result["evidence_state"]["artifact_containing_commit"] == repo.artifact_commit
    assert result["evidence_state"]["checksum_entry_count"] == 5
    assert result["evidence_state"]["checksum_status"] == "PASS"
    assert result["evidence_state"]["license_status"] == "PASS"
    assert result["performed_actions"] == []
    for key in ["release_target", "uploaded_artifact", "downstream_release"]:
        assert result["external_state"][key]["status"] == "NOT RUN"


def test_matching_slash_named_branch_and_upstream_pass(tmp_path: Path) -> None:
    branch = "codex/release-lineage"
    repo = make_repo(tmp_path, git_ref=branch)
    run_git(repo.root, "branch", "-m", branch)
    run_git(repo.root, "update-ref", f"refs/remotes/origin/{branch}", repo.artifact_commit)
    run_git(repo.root, "branch", "--unset-upstream")
    run_git(repo.root, "branch", f"--set-upstream-to=origin/{branch}", branch)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "PASS"
    assert result["reason_codes"] == []
    assert result["repository_state"]["branch"] == branch
    assert result["repository_state"]["upstream_ref"] == f"origin/{branch}"
    assert_readiness(result, refresh="READY", release="READY")


@pytest.mark.parametrize(
    "binding",
    [
        "manifest_bytes_changed",
        "spdx_annotation_missing",
        "spdx_annotation_mismatch",
        "spdx_namespace_mismatch",
        "cyclonedx_manifest_digest_missing",
        "cyclonedx_manifest_digest_mismatch",
        "cyclonedx_manifest_path_mismatch",
        "provenance_input_missing",
        "provenance_input_mismatch",
        "provenance_input_path_mismatch",
        "provenance_subject_mismatch",
        "provenance_products_mismatch",
        "provenance_checksum_mismatch",
    ],
)
def test_manifest_digest_bindings_fail_closed_with_valid_checksums(
    tmp_path: Path,
    binding: str,
) -> None:
    repo = make_repo(
        tmp_path,
        evidence_mutator=lambda root: mutate_evidence_binding(root, binding),
    )

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "FAIL"
    assert_readiness(result, refresh="BLOCKED", release="BLOCKED")
    assert result["reason_codes"] == [preflight.MANIFEST_DIGEST_MISMATCH]
    assert result["evidence_state"]["checksum_status"] == "PASS"
    assert result["evidence_state"]["artifact_containing_commit"] == repo.artifact_commit


@pytest.mark.parametrize(
    "binding",
    [
        "cyclonedx_repository_mismatch",
        "cyclonedx_ref_mismatch",
        "provenance_repository_mismatch",
        "provenance_ref_mismatch",
    ],
)
def test_generated_repository_and_ref_mismatch_fail_closed(
    tmp_path: Path,
    binding: str,
) -> None:
    repo = make_repo(
        tmp_path,
        evidence_mutator=lambda root: mutate_evidence_binding(root, binding),
    )

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "FAIL"
    assert_readiness(result, refresh="BLOCKED", release="BLOCKED")
    assert result["reason_codes"] == [preflight.REPOSITORY_METADATA_MISMATCH]
    assert result["evidence_state"]["checksum_status"] == "PASS"
    assert result["evidence_state"]["artifact_containing_commit"] == repo.artifact_commit


@pytest.mark.parametrize(
    ("repository", "git_ref"),
    [
        (None, "main"),
        ("UNKNOWN", "main"),
        ("example/repository", None),
        ("example/repository", "UNKNOWN"),
    ],
)
def test_manifest_requires_concrete_repository_and_ref(
    tmp_path: Path,
    repository: str | None,
    git_ref: str | None,
) -> None:
    repo = make_repo(tmp_path, repository=repository, git_ref=git_ref)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "FAIL"
    assert_readiness(result, refresh="BLOCKED", release="BLOCKED")
    assert result["reason_codes"] == [preflight.REPOSITORY_METADATA_MISMATCH]


def test_new_clean_source_commit_returns_pass_with_notes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write(repo.root / "docs/FOLLOW_UP.md", "# Follow-up\n")
    head = commit_all(repo.root, "follow-up source")
    sync_upstream(repo.root, head)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "PASS WITH NOTES"
    assert_readiness(result, refresh="READY", release="BLOCKED")
    assert result["reason_codes"] == ["EVIDENCE_REFRESH_RECOMMENDED"]
    assert result["repository_state"]["head_commit"] == head
    assert result["evidence_state"]["artifact_containing_commit"] == repo.artifact_commit


def test_missing_dry_run_is_not_run_and_does_not_inspect(monkeypatch, capsys) -> None:
    def unexpected_inspection(_repo_root: Path) -> dict[str, object]:
        raise AssertionError("inspection must not run")

    monkeypatch.setattr(preflight, "inspect_preflight", unexpected_inspection)

    exit_code = preflight.main(["--repo-root", "unused", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["status"] == "NOT RUN"
    assert_readiness(payload, refresh="NOT RUN", release="NOT RUN")
    assert payload["reason_codes"] == ["DRY_RUN_REQUIRED"]
    assert payload["performed_actions"] == []


@pytest.mark.parametrize(
    ("mode", "reason"),
    [
        ("dirty", "DIRTY_WORKTREE"),
        ("staged", "DIRTY_WORKTREE"),
        ("untracked", "UNTRACKED_FILES_PRESENT"),
    ],
)
def test_dirty_staged_and_untracked_states_are_blocked_without_path_echo(
    tmp_path: Path,
    mode: str,
    reason: str,
) -> None:
    repo = make_repo(tmp_path)
    marker = "sensitive-marker-value"
    if mode == "untracked":
        write(repo.root / f"{marker}.txt", "marker\n")
    else:
        write(repo.root / preflight.POLICY_PATHS[0], f"# Changed {marker}\n")
        if mode == "staged":
            run_git(repo.root, "add", preflight.POLICY_PATHS[0])

    result = preflight.inspect_preflight(repo.root)
    output = preflight.json_bytes(result).decode("utf-8")

    assert result["status"] == "BLOCKED"
    assert reason in result["reason_codes"]
    assert marker not in output
    assert str(repo.root) not in output


def test_missing_upstream_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    run_git(repo.root, "branch", "--unset-upstream")

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "BLOCKED"
    assert "UPSTREAM_MISSING" in result["reason_codes"]


def test_head_upstream_mismatch_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write(repo.root / "docs/LOCAL_ONLY.md", "# Local only\n")
    commit_all(repo.root, "local-only source")

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "BLOCKED"
    assert_readiness(result, refresh="BLOCKED", release="BLOCKED")
    assert "HEAD_UPSTREAM_MISMATCH" in result["reason_codes"]


def test_current_evidence_ahead_of_upstream_keeps_release_ready(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    sync_upstream(repo.root, repo.source_commit)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["HEAD_UPSTREAM_MISMATCH"]
    assert result["repository_state"]["head_commit"] == repo.artifact_commit
    assert result["evidence_state"]["artifact_containing_commit"] == repo.artifact_commit
    assert_readiness(result, refresh="BLOCKED", release="READY")


def test_missing_release_evidence_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    (repo.root / "artifacts/sbom.cdx.json").unlink()
    head = commit_all(repo.root, "remove evidence")
    sync_upstream(repo.root, head)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "BLOCKED"
    assert result["reason_codes"] == ["MISSING_RELEASE_EVIDENCE"]


@pytest.mark.parametrize(
    ("mode", "reason"),
    [
        ("malformed", "MALFORMED_RELEASE_EVIDENCE"),
        ("oversized", "INPUT_SIZE_LIMIT_EXCEEDED"),
    ],
)
def test_malformed_and_oversized_evidence_fail(tmp_path: Path, mode: str, reason: str) -> None:
    repo = make_repo(tmp_path)
    content = "{invalid\n" if mode == "malformed" else "x" * (preflight.MAX_INPUT_BYTES + 1)
    write(repo.root / "artifacts/release-manifest.json", content)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "FAIL"
    assert reason in result["reason_codes"]


def test_checksum_mismatch_fails(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_json(repo.root / "artifacts/eval-report.json", {"schema_version": "changed"})

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "FAIL"
    assert_readiness(result, refresh="BLOCKED", release="BLOCKED")
    assert "CHECKSUM_MISMATCH" in result["reason_codes"]
    assert result["evidence_state"]["checksum_status"] == "FAIL"


def test_source_basis_mismatch_fails(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, provenance_commit="1" * 40)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "FAIL"
    assert "SOURCE_BASIS_MISMATCH" in result["reason_codes"]


def test_artifact_commit_mismatch_fails_even_with_valid_checksums(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    spdx_path = repo.root / "artifacts/sbom.spdx.json"
    spdx = json.loads(spdx_path.read_text(encoding="utf-8"))
    spdx["documentComment"] = "synthetic update"
    write_json(spdx_path, spdx)
    regenerate_checksums(repo.root)
    head = commit_all(repo.root, "partial evidence update")
    sync_upstream(repo.root, head)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "FAIL"
    assert "ARTIFACT_COMMIT_MISMATCH" in result["reason_codes"]


def test_unknown_source_basis_is_not_accepted_as_ancestor(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, source_override="0" * 40)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "FAIL"
    assert "SOURCE_BASIS_NOT_ANCESTOR" in result["reason_codes"]


@pytest.mark.parametrize(
    "error",
    [FileNotFoundError(), subprocess.TimeoutExpired(cmd="git", timeout=1)],
)
def test_git_unavailable_or_timeout_is_environment_blocked(tmp_path: Path, monkeypatch, error: Exception) -> None:
    def fail_git(*_args, **_kwargs):
        raise error

    monkeypatch.setattr(preflight.subprocess, "run", fail_git)

    result = preflight.inspect_preflight(tmp_path)

    assert result["status"] == "ENVIRONMENT BLOCKED"
    assert_readiness(result, refresh="BLOCKED", release="BLOCKED")
    assert result["reason_codes"] == ["GIT_UNAVAILABLE"]


def test_cleanup_snapshot_change_is_fail(tmp_path: Path, monkeypatch) -> None:
    repo = make_repo(tmp_path)
    original = preflight.status_snapshot
    calls = 0

    def changed_snapshot(root: Path) -> tuple[str, int, int]:
        nonlocal calls
        calls += 1
        raw, tracked, untracked = original(root)
        if calls == 2:
            return raw + "synthetic-change\n", tracked + 1, untracked
        return raw, tracked, untracked

    monkeypatch.setattr(preflight, "status_snapshot", changed_snapshot)

    result = preflight.inspect_preflight(repo.root)

    assert result["status"] == "FAIL"
    assert "CLEANUP_VERIFICATION_FAILED" in result["reason_codes"]


def test_json_cli_output_is_deterministic_bounded_and_non_persistent(tmp_path: Path, capsys) -> None:
    repo = make_repo(tmp_path)
    before = run_git(repo.root, "status", "--porcelain=v1", "--untracked-files=normal")

    first_exit = preflight.main(["--repo-root", str(repo.root), "--dry-run", "--json"])
    first = capsys.readouterr().out
    second_exit = preflight.main(["--repo-root", str(repo.root), "--dry-run", "--json"])
    second = capsys.readouterr().out

    assert first_exit == second_exit == 0
    assert first == second
    assert first.endswith("\n")
    assert len(first.encode("utf-8")) <= preflight.MAX_OUTPUT_BYTES
    assert list(json.loads(first)) == sorted(json.loads(first))
    payload = json.loads(first)
    assert_readiness(payload, refresh="READY", release="READY")
    assert payload["performed_actions"] == []
    assert str(repo.root) not in first
    assert run_git(repo.root, "status", "--porcelain=v1", "--untracked-files=normal") == before


def test_plain_summary_and_local_tag_are_bounded(tmp_path: Path, capsys) -> None:
    repo = make_repo(tmp_path)
    run_git(repo.root, "tag", "synthetic-v1")

    exit_code = preflight.main(["--repo-root", str(repo.root), "--dry-run"])
    summary = capsys.readouterr().out
    result = preflight.inspect_preflight(repo.root)

    assert exit_code == 0
    assert summary.startswith("PASS local_release_evidence_preflight_dry_run")
    assert " readiness=READY " in summary
    assert " refresh_readiness=READY " in summary
    assert " release_readiness=READY " in summary
    assert len(summary.encode("utf-8")) < 512
    assert result["external_state"]["tag_target"] == "synthetic-v1"
    assert result["external_state"]["release_target"]["status"] == "NOT RUN"


def test_output_limit_fallback_blocks_both_readiness_fields(monkeypatch, capsys) -> None:
    original = preflight.json_bytes
    calls = 0

    def fail_once(result: dict[str, object]) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ValueError("synthetic output limit")
        return original(result)

    monkeypatch.setattr(preflight, "json_bytes", fail_once)

    exit_code = preflight.main(["--repo-root", "unused", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "FAIL"
    assert payload["reason_codes"] == ["OUTPUT_LIMIT_EXCEEDED"]
    assert_readiness(payload, refresh="BLOCKED", release="BLOCKED")
