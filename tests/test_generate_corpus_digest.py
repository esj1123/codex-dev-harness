import json
import os
from pathlib import Path
import subprocess

import pytest

from scripts import generate_corpus_digest


APPROVAL_REF = "owner_approved_phase_6g_digest_refresh_task"
REPO_ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


def write_raw(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def digest_hash(content: str) -> str:
    return generate_corpus_digest.normalized_sha256(content)


def digest_entry(source_path: str, *, source_text: str = "", content_hash: str | None = None) -> dict[str, object]:
    return {
        "__source_text": source_text,
        "source_path": source_path,
        "git_sha": "old-basis",
        "section_title": source_path,
        "content_class": "repo_baseline",
        "risk_label": "approved_repo_policy",
        "allowed_for_digest": "approved",
        "allowed_for_release": "not_release_without_separate_approval",
        "redaction_status": "metadata_hash_only_no_source_text",
        "encoding_status": "utf8_readable",
        "digest_algorithm": "sha256",
        "content_hash": content_hash if content_hash is not None else digest_hash(source_text),
        "verified_at": "2026-01-01T00:00:00Z",
        "reviewer_or_approval_ref": "synthetic",
        "notes": "Metadata and hash only; source body omitted.",
    }


def source_set_entry(
    source_path: str,
    *,
    section_title: str | None = None,
    content_class: str = "repo_baseline",
    risk_label: str = "approved_repo_policy",
    temporal_class: str = "stable_current_authority",
    authority_level: str = "supporting_policy",
) -> dict[str, object]:
    return {
        "source_path": source_path,
        "section_title": section_title or source_path,
        "content_class": content_class,
        "risk_label": risk_label,
        "temporal_class": temporal_class,
        "authority_level": authority_level,
    }


def write_digest(
    root: Path,
    sources: list[dict[str, object]],
    *,
    initialize_git: bool = True,
) -> Path:
    materialized_sources: list[dict[str, object]] = []
    for source in sources:
        materialized = dict(source)
        source_text = materialized.pop("__source_text", "")
        source_path = str(materialized["source_path"])
        candidate = root.joinpath(*source_path.split("/"))
        if source_text and not candidate.exists():
            write(candidate, str(source_text))
        materialized_sources.append(materialized)
    sources = materialized_sources
    digest_path = root / "artifacts" / "corpus-digest.json"
    digest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "synthetic-v1",
        "artifact_type": "approved_corpus_digest",
        "artifact_path": "artifacts/corpus-digest.json",
        "repository": "synthetic/repo",
        "git_sha": "old-basis",
        "generated_at": "2026-01-01T00:00:00Z",
        "generation_approval_ref": "synthetic",
        "source_allow_list_ref": "synthetic",
        "digest_algorithm": "sha256",
        "normalization_policy": {
            "name": "utf8_text_lf_normalized_full_file",
            "content_unit": "full_file",
            "newline": "LF",
            "trim_trailing_whitespace": False,
            "hash_input": "UTF-8 decoded text with CRLF or CR normalized to LF",
        },
        "precheck_summary": {"source_count": len(sources), "boundary_phrase_match_count": 3},
        "release_artifact_status": "not_release_artifact_without_separate_approval",
        "rag_authorization_status": "not_authorized",
        "sources": sources,
        "closeout": {"status_label": "PASS WITH NOTES"},
    }
    digest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if initialize_git and not (root / ".git").exists():
        init_git_repo(root)
        commit_all(root)
    return digest_path


def write_source_set_spec(
    root: Path,
    sources: list[dict[str, object]],
    *,
    expected_source_count: int | None = None,
    excluded_volatile_sources: list[str] | None = None,
) -> Path:
    spec_path = root / "docs" / "source-set.json"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "2.0",
        "source_set_id": "synthetic_source_set",
        "human_contract_ref": "docs/SYNTHETIC_CONTRACT.md#source-set",
        "expected_source_count": expected_source_count if expected_source_count is not None else len(sources),
        "ordered_sources": sources,
        "excluded_volatile_sources": excluded_volatile_sources or ["STATUS.md", "ACCEPTANCE_TRACE.md"],
    }
    spec_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return spec_path


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def init_git_repo(root: Path) -> None:
    run_git(root, "init")
    run_git(root, "config", "user.email", "synthetic@example.invalid")
    run_git(root, "config", "user.name", "Synthetic Tester")


def commit_all(root: Path, message: str = "synthetic commit") -> str:
    run_git(root, "add", ".")
    run_git(root, "commit", "-m", message)
    source_basis = run_git(root, "rev-parse", "HEAD")
    digest_path = root / "artifacts" / "corpus-digest.json"
    if digest_path.exists():
        payload = json.loads(digest_path.read_text(encoding="utf-8"))
        if payload.get("git_sha") == "old-basis":
            generated_at = payload["generated_at"]
            approval_ref = payload["generation_approval_ref"]
            payload["git_sha"] = source_basis
            payload.setdefault("closeout", {})["source_count"] = len(
                payload["sources"]
            )
            for source in payload["sources"]:
                source["git_sha"] = source_basis
                source["verified_at"] = generated_at
                source["reviewer_or_approval_ref"] = approval_ref
                try:
                    blob = subprocess.run(
                        ["git", "show", f"{source_basis}:{source['source_path']}"],
                        cwd=root,
                        check=True,
                        capture_output=True,
                    ).stdout
                    source["content_hash"] = digest_hash(blob.decode("utf-8"))
                except (subprocess.CalledProcessError, UnicodeDecodeError):
                    pass
            digest_path.write_text(
                json.dumps(payload, indent=2) + "\n", encoding="utf-8"
            )
            run_git(root, "add", "artifacts/corpus-digest.json")
            run_git(root, "commit", "-m", "synthetic digest evidence")
    return run_git(root, "rev-parse", "HEAD")


def prepare_head_drift_repo(root: Path) -> tuple[Path, str, str]:
    source_text = "# Source at A\n"
    write(root / "docs" / "A.md", source_text)
    digest_path = write_digest(
        root,
        [digest_entry("docs/A.md", content_hash=digest_hash("# Stale\n"))],
        initialize_git=False,
    )
    init_git_repo(root)
    first_head = commit_all(root, "source A")
    write(root / "docs" / "A.md", "# Source at B\n")
    second_head = commit_all(root, "source B")
    run_git(root, "reset", "--hard", first_head)
    return digest_path, first_head, second_head


def move_head_ref_only(root: Path, new_head: str, expected_head: str) -> None:
    branch = run_git(root, "symbolic-ref", "--short", "HEAD")
    run_git(root, "update-ref", f"refs/heads/{branch}", new_head, expected_head)


def prepare_valid_digest(root: Path) -> Path:
    source_text = "# Recorded source\n"
    write(root / "docs" / "A.md", source_text)
    return write_digest(
        root, [digest_entry("docs/A.md", source_text=source_text)]
    )


def mutate_digest(digest_path: Path, mutation) -> bytes:
    before = digest_path.read_bytes()
    payload = json.loads(before.decode("utf-8"))
    mutation(payload)
    digest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return before


def make_junction(link: Path, target: Path) -> None:
    result = subprocess.run(
        ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def refreshed_from(root: Path, digest_path: Path) -> dict[str, object]:
    digest = generate_corpus_digest.load_digest(digest_path)
    checks = generate_corpus_digest.check_sources(root, digest)
    return generate_corpus_digest.build_refreshed_digest(
        digest,
        checks,
        git_sha="new-basis",
        generated_at="2026-02-01T00:00:00Z",
        approval_ref=APPROVAL_REF,
    )


def test_default_check_mode_is_read_only(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(tmp_path / "docs" / "A.md", "new content\n")
    digest_path = write_digest(
        tmp_path,
        [digest_entry("docs/A.md", content_hash=digest_hash("old content\n"))],
    )
    write(tmp_path / "docs" / "A.md", "changed after recorded basis\n")
    commit_all(tmp_path, "current source differs")
    before = digest_path.read_bytes()

    exit_code = generate_corpus_digest.main(["--repo-root", str(tmp_path), "--json"])
    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert exit_code == 0
    assert report["mode"] == "check"
    assert report["stale"] == 1
    assert digest_path.read_bytes() == before


def test_check_mode_does_not_write_digest(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "A.md", "new content\n")
    digest_path = write_digest(
        tmp_path,
        [digest_entry("docs/A.md", content_hash=digest_hash("old content\n"))],
    )
    write(tmp_path / "docs" / "A.md", "changed after recorded basis\n")
    commit_all(tmp_path, "current source differs")
    before = digest_path.read_bytes()

    report = generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert report["stale"] == 1
    assert report["refresh_required"] is True
    assert digest_path.read_bytes() == before


def test_write_rejects_empty_approval_reference(tmp_path: Path) -> None:
    text = "# Source\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", source_text=text)])

    with pytest.raises(ValueError, match="approval-ref"):
        generate_corpus_digest.write_refreshed_digest(tmp_path, digest_path, approval_ref="")


@pytest.mark.parametrize(
    "bad_path",
    [
        r"C:\temp\corpus-digest.json",
        "/tmp/corpus-digest.json",
        "../outside.json",
        "artifacts/../outside.json",
    ],
)
def test_write_rejects_absolute_and_parent_traversal_digest_paths(tmp_path: Path, bad_path: str) -> None:
    with pytest.raises(ValueError):
        generate_corpus_digest.validate_cli_digest_path(tmp_path, bad_path, write=True)


@pytest.mark.parametrize("bad_path", ["artifacts/other.json", "corpus-digest.json", "docs/corpus-digest.json", ""])
def test_write_rejects_repo_contained_noncanonical_output_paths(tmp_path: Path, bad_path: str) -> None:
    with pytest.raises(ValueError):
        generate_corpus_digest.validate_cli_digest_path(tmp_path, bad_path, write=True)


def test_write_accepts_only_canonical_digest_path(tmp_path: Path) -> None:
    resolved = generate_corpus_digest.validate_cli_digest_path(
        tmp_path,
        "artifacts/corpus-digest.json",
        write=True,
    )

    assert resolved == (tmp_path / "artifacts" / "corpus-digest.json").resolve(strict=False)


def test_missing_source_blocks_write(tmp_path: Path) -> None:
    digest_path = write_digest(tmp_path, [digest_entry("docs/MISSING.md", content_hash="0" * 64)])
    before = digest_path.read_bytes()

    with pytest.raises(ValueError, match="missing"):
        generate_corpus_digest.write_refreshed_digest(tmp_path, digest_path, approval_ref=APPROVAL_REF)

    assert digest_path.read_bytes() == before


def test_unsafe_source_blocks_write(tmp_path: Path) -> None:
    digest_path = write_digest(tmp_path, [digest_entry("raw/PRIVATE.md", content_hash="0" * 64)])

    with pytest.raises(ValueError, match="unsafe"):
        generate_corpus_digest.write_refreshed_digest(tmp_path, digest_path, approval_ref=APPROVAL_REF)


def test_invalid_utf8_blocks_write(tmp_path: Path) -> None:
    write_raw(tmp_path / "docs" / "BAD.md", b"# Bad\n\xff\xfe\n")
    digest_path = write_digest(tmp_path, [digest_entry("docs/BAD.md", content_hash="0" * 64)])

    with pytest.raises(ValueError, match="invalid UTF-8"):
        generate_corpus_digest.write_refreshed_digest(tmp_path, digest_path, approval_ref=APPROVAL_REF)


def test_modified_digest_listed_tracked_source_blocks_write(tmp_path: Path) -> None:
    text = "# Clean\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", content_hash=digest_hash("old\n"))], initialize_git=False)
    init_git_repo(tmp_path)
    commit_all(tmp_path)
    write(tmp_path / "docs" / "A.md", "# Modified\n")

    with pytest.raises(ValueError, match="differs from HEAD: docs/A.md"):
        generate_corpus_digest.write_refreshed_digest(tmp_path, digest_path, approval_ref=APPROVAL_REF)


def test_staged_digest_listed_source_blocks_write(tmp_path: Path) -> None:
    text = "# Clean\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", content_hash=digest_hash("old\n"))], initialize_git=False)
    init_git_repo(tmp_path)
    commit_all(tmp_path)
    write(tmp_path / "docs" / "A.md", "# Staged\n")
    run_git(tmp_path, "add", "docs/A.md")

    with pytest.raises(ValueError, match="differs from HEAD: docs/A.md"):
        generate_corpus_digest.write_refreshed_digest(tmp_path, digest_path, approval_ref=APPROVAL_REF)


def test_clean_committed_digest_listed_source_permits_refresh_write(tmp_path: Path) -> None:
    text = "# Current source\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", content_hash=digest_hash("old\n"))], initialize_git=False)
    init_git_repo(tmp_path)
    head = commit_all(tmp_path)

    report = generate_corpus_digest.write_refreshed_digest(
        tmp_path,
        digest_path,
        approval_ref=APPROVAL_REF,
        generated_at="2026-02-01T00:00:00Z",
    )
    refreshed = json.loads(digest_path.read_text(encoding="utf-8"))

    assert report["valid"] == 1
    assert refreshed["git_sha"] == head
    assert refreshed["sources"][0]["git_sha"] == head
    assert refreshed["sources"][0]["content_hash"] == digest_hash(text)


def test_git_sha_override_cannot_weaken_source_basis_guard(tmp_path: Path) -> None:
    text = "# Current source\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", source_text=text)], initialize_git=False)
    init_git_repo(tmp_path)
    commit_all(tmp_path)

    with pytest.raises(ValueError, match="cannot override"):
        generate_corpus_digest.write_refreshed_digest(
            tmp_path,
            digest_path,
            approval_ref=APPROVAL_REF,
            git_sha="not-the-head-commit",
        )


def test_head_drift_between_source_check_and_clean_guard_blocks_refresh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest_path, _first_head, second_head = prepare_head_drift_repo(tmp_path)
    before = digest_path.read_bytes()
    original_check_sources = generate_corpus_digest.check_sources

    def check_then_advance(*args, **kwargs):
        checks = original_check_sources(*args, **kwargs)
        run_git(tmp_path, "reset", "--hard", second_head)
        return checks

    monkeypatch.setattr(generate_corpus_digest, "check_sources", check_then_advance)

    with pytest.raises(ValueError, match="HEAD changed during source-basis validation"):
        generate_corpus_digest.write_refreshed_digest(
            tmp_path, digest_path, approval_ref=APPROVAL_REF
        )

    assert digest_path.read_bytes() == before


def test_head_drift_before_write_blocks_refresh_without_writing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest_path, _first_head, second_head = prepare_head_drift_repo(tmp_path)
    before = digest_path.read_bytes()
    original_builder = generate_corpus_digest.build_refreshed_digest

    def build_then_advance(*args, **kwargs):
        refreshed = original_builder(*args, **kwargs)
        run_git(tmp_path, "reset", "--hard", second_head)
        return refreshed

    monkeypatch.setattr(
        generate_corpus_digest, "build_refreshed_digest", build_then_advance
    )

    with pytest.raises(ValueError, match="HEAD changed during pre-write validation"):
        generate_corpus_digest.write_refreshed_digest(
            tmp_path, digest_path, approval_ref=APPROVAL_REF
        )

    assert digest_path.read_bytes() == before


def test_head_drift_after_write_is_coherent_but_cli_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    digest_path, first_head, second_head = prepare_head_drift_repo(tmp_path)
    original_write_digest = generate_corpus_digest.write_digest

    def write_then_advance(digest, output_path, **kwargs):
        original_write_digest(digest, output_path, **kwargs)
        move_head_ref_only(tmp_path, second_head, first_head)

    monkeypatch.setattr(generate_corpus_digest, "write_digest", write_then_advance)

    with pytest.raises(SystemExit) as exc_info:
        generate_corpus_digest.main(
            [
                "--repo-root",
                str(tmp_path),
                "--write",
                "--approval-ref",
                APPROVAL_REF,
            ]
        )

    refreshed = json.loads(digest_path.read_text(encoding="utf-8"))
    assert exc_info.value.code == 2
    assert "HEAD changed during post-write validation" in capsys.readouterr().err
    assert refreshed["git_sha"] == first_head
    assert refreshed["sources"][0]["git_sha"] == first_head
    assert refreshed["sources"][0]["content_hash"] == digest_hash(
        "# Source at A\n"
    )


def test_post_write_refresh_required_is_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest_path, _first_head, _second_head = prepare_head_drift_repo(tmp_path)
    original_check_sources = generate_corpus_digest.check_sources
    call_count = 0

    def stale_after_write(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        checks = original_check_sources(*args, **kwargs)
        if call_count == 2:
            check = checks[0]
            return [
                generate_corpus_digest.SourceCheck(
                    check.source_path,
                    "stale",
                    "synthetic post-write drift",
                    check.recorded_hash,
                    check.current_hash,
                )
            ]
        return checks

    monkeypatch.setattr(generate_corpus_digest, "check_sources", stale_after_write)

    with pytest.raises(ValueError, match="post-write validation requires refresh"):
        generate_corpus_digest.write_refreshed_digest(
            tmp_path, digest_path, approval_ref=APPROVAL_REF
        )


def test_report_preserves_deterministic_source_order(tmp_path: Path) -> None:
    first = "# B\n"
    second = "# A\n"
    write(tmp_path / "docs" / "B.md", first)
    write(tmp_path / "docs" / "A.md", second)
    digest_path = write_digest(
        tmp_path,
        [
            digest_entry("docs/B.md", source_text=first),
            digest_entry("docs/A.md", source_text=second),
        ],
    )

    report = generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert [source["source_path"] for source in report["sources"]] == ["docs/B.md", "docs/A.md"]


def test_valid_and_stale_hash_counts(tmp_path: Path) -> None:
    valid = "# Valid\n"
    stale = "# Stale\n"
    write(tmp_path / "docs" / "VALID.md", valid)
    write(tmp_path / "docs" / "STALE.md", stale)
    digest_path = write_digest(
        tmp_path,
        [
            digest_entry("docs/VALID.md", source_text=valid),
            digest_entry("docs/STALE.md", content_hash=digest_hash("old stale\n")),
        ],
    )
    write(tmp_path / "docs" / "STALE.md", "# Changed after recorded basis\n")
    commit_all(tmp_path, "make one source stale")

    report = generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert report["source_count"] == 2
    assert report["valid"] == 1
    assert report["stale"] == 1
    assert report["refresh_required"] is True


def test_crlf_source_matches_lf_normalized_hash(tmp_path: Path) -> None:
    lf_text = "# CRLF\n\nline one\nline two\n"
    write(tmp_path / "docs" / "CRLF.md", lf_text.replace("\n", "\r\n"))
    digest_path = write_digest(tmp_path, [digest_entry("docs/CRLF.md", source_text=lf_text)])

    report = generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert report["valid"] == 1
    assert report["stale"] == 0


def test_refreshed_digest_preserves_exact_source_set_and_statuses(tmp_path: Path) -> None:
    first = "# First\n"
    second = "# Second\n"
    write(tmp_path / "docs" / "FIRST.md", first)
    write(tmp_path / "docs" / "SECOND.md", second)
    digest_path = write_digest(
        tmp_path,
        [
            digest_entry("docs/FIRST.md", source_text=first),
            digest_entry("docs/SECOND.md", content_hash=digest_hash("old second\n")),
        ],
    )

    refreshed = refreshed_from(tmp_path, digest_path)

    assert [source["source_path"] for source in refreshed["sources"]] == ["docs/FIRST.md", "docs/SECOND.md"]
    assert refreshed["sources"][1]["content_hash"] == digest_hash(second)


def test_not_run_scan_fields_are_not_reported_as_completed_zero_findings(tmp_path: Path) -> None:
    text = "# Source\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", source_text=text)])

    refreshed = refreshed_from(tmp_path, digest_path)
    precheck = refreshed["precheck_summary"]
    closeout = refreshed["closeout"]

    assert precheck["source_scan_status"] == "not_run_by_refresh_tool"
    assert precheck["safety_scan_status"] == "not_run_by_refresh_tool"
    assert precheck["local_path_match_count"] is None
    assert precheck["ip_like_match_count"] is None
    assert precheck["assignment_like_match_count"] is None
    assert precheck["boundary_phrase_match_count"] is None
    assert closeout["json_validation_status"] == "not_run_by_refresh_tool"
    assert closeout["safety_scan_status"] == "not_run_by_refresh_tool"
    assert closeout["quality_gate_status"] == "not_run_by_refresh_tool"
    assert closeout["status_label"] == "PASS WITH NOTES"


def test_release_artifact_and_rag_authorization_boundaries_are_preserved(tmp_path: Path) -> None:
    text = "# Source\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", source_text=text)])
    digest = json.loads(digest_path.read_text(encoding="utf-8"))

    refreshed = refreshed_from(tmp_path, digest_path)

    assert refreshed["release_artifact_status"] == digest["release_artifact_status"]
    assert refreshed["rag_authorization_status"] == digest["rag_authorization_status"]


def test_check_output_is_deterministic_for_same_inputs(tmp_path: Path) -> None:
    text = "# Source\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", source_text=text)])

    first = generate_corpus_digest.check_digest(tmp_path, digest_path)
    second = generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_report_does_not_copy_source_body(tmp_path: Path) -> None:
    body = "# Source\n\nUNIQUE_SYNTHETIC_SOURCE_BODY_SHOULD_NOT_APPEAR\n"
    write(tmp_path / "docs" / "A.md", body)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", source_text=body)])

    report = generate_corpus_digest.check_digest(tmp_path, digest_path)
    refreshed = refreshed_from(tmp_path, digest_path)

    assert "UNIQUE_SYNTHETIC_SOURCE_BODY_SHOULD_NOT_APPEAR" not in json.dumps(report)
    assert "UNIQUE_SYNTHETIC_SOURCE_BODY_SHOULD_NOT_APPEAR" not in json.dumps(refreshed)


def test_check_reads_exact_head_blob_not_working_tree_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    committed = "# Approved\n"
    write(tmp_path / "docs" / "A.md", committed)
    digest_path = write_digest(
        tmp_path, [digest_entry("docs/A.md", source_text=committed)]
    )
    write(tmp_path / "docs" / "A.md", "api_key=" + "p" * 24 + "\n")

    monkeypatch.setattr(
        generate_corpus_digest,
        "read_normalized_text",
        lambda _path: (_ for _ in ()).throw(AssertionError("working tree read")),
    )
    report = generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert report["valid"] == 1
    assert report["stale"] == 0
    assert "api_key" not in json.dumps(report)


def test_exact_head_symlink_entry_is_not_read_as_corpus_source(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    digest_path = write_digest(
        tmp_path,
        [digest_entry("docs/LINK.md", source_text="../private.txt\n")],
        initialize_git=False,
    )
    blob = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        cwd=tmp_path,
        input="../private.txt\n",
        text=True,
        check=True,
        capture_output=True,
    ).stdout.strip()
    run_git(
        tmp_path,
        "update-index",
        "--add",
        "--cacheinfo",
        f"120000,{blob},docs/LINK.md",
    )
    commit_all(tmp_path, "synthetic symlink source")

    with pytest.raises(ValueError, match="recorded basis is missing"):
        generate_corpus_digest.check_digest(tmp_path, digest_path)


def test_phase_6h_source_set_spec_matches_exact_contract() -> None:
    spec = generate_corpus_digest.load_source_set_spec(
        REPO_ROOT / "docs" / "APPROVED_CORPUS_SOURCE_SET.v2.json"
    )
    paths = generate_corpus_digest.source_set_paths(spec)

    assert len(paths) == 34
    assert spec["expected_source_count"] == 34
    assert paths == [
        "AGENTS.md",
        "README.md",
        "docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md",
        "docs/SAFETY_POLICY.md",
        "docs/VERIFICATION.md",
        "docs/CI_POLICY.md",
        "docs/AUDIT_TRACE_SCHEMA.md",
        "docs/AUDIT_LOG_POLICY.md",
        "docs/APPROVED_CORPUS_DIGEST_PLAN.md",
        "docs/APPROVED_CORPUS_RAG_PLAN.md",
        "docs/LOCAL_RAG_DESIGN.md",
        "docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md",
        "docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md",
        "docs/LOCAL_RAG_VOLATILE_OVERLAY_CONTRACT.md",
        "docs/EVAL_REPORT_INTEGRATION_PLAN.md",
        "docs/EVAL_POLICY.md",
        "docs/EVAL_INTEGRATION_DECISION.md",
        "docs/OPTIONAL_RAG_PILOT_DECISION.md",
        "docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md",
        "docs/AUDIT_RECEIPT_PILOT_REVIEW.md",
        "docs/MINIMAL_EVAL_HARNESS_DESIGN.md",
        "docs/AI_HANDOFF.md",
        "docs/CHANGE_CONTROL.md",
        "docs/HUMAN_APPROVALS.md",
        "docs/PROMPT_PATTERNS.md",
        "docs/adr/ADR-0001-local-first.md",
        "docs/adr/ADR-0002-base-template-over-domain-profile.md",
        "docs/adr/ADR-0003-approval-gated-side-effect.md",
        "docs/RELEASE_RECORD_v0.1.0-rc1.md",
        "docs/RELEASE_RECORD_v0.1.0-rc2.md",
        "docs/RELEASE_RECORD_v0.1.0.md",
        "docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md",
        "docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md",
        "docs/CLEAN_CLONE_VALIDATION_v0.1.0.md",
    ]
    assert spec["excluded_volatile_sources"] == ["STATUS.md", "ACCEPTANCE_TRACE.md"]
    assert "STATUS.md" not in paths
    assert "ACCEPTANCE_TRACE.md" not in paths
    assert "docs/LOCAL_RAG_RETRIEVER_LOGICAL_VERIFICATION.md" not in paths


def test_rebaseline_check_is_read_only_and_reports_source_set_diff(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    keep = "# Keep\n"
    new = "# New\n"
    write(tmp_path / "docs" / "KEEP.md", keep)
    write(tmp_path / "docs" / "NEW.md", new)
    digest_path = write_digest(
        tmp_path,
        [
            digest_entry("docs/OLD.md", source_text="# Old\n"),
            digest_entry("docs/KEEP.md", source_text=keep),
        ],
    )
    spec_path = write_source_set_spec(
        tmp_path,
        [
            source_set_entry("docs/NEW.md"),
            source_set_entry("docs/KEEP.md"),
        ],
    )
    before = digest_path.read_bytes()

    exit_code = generate_corpus_digest.main(
        [
            "--repo-root",
            str(tmp_path),
            "--rebaseline-spec",
            "docs/source-set.json",
            "--json",
        ]
    )
    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert exit_code == 0
    assert report["mode"] == "rebaseline_check"
    assert report["source_count"] == 2
    assert report["valid"] == 2
    assert [source["source_path"] for source in report["sources"]] == ["docs/NEW.md", "docs/KEEP.md"]
    assert report["added_sources"] == ["docs/NEW.md"]
    assert report["removed_sources"] == ["docs/OLD.md"]
    assert report["source_set_spec_path"] == "docs/source-set.json"
    assert digest_path.read_bytes() == before
    assert spec_path.read_text(encoding="utf-8")


def test_rebaseline_write_with_spec_updates_membership_order_and_hashes(tmp_path: Path) -> None:
    keep = "# Keep\n"
    new = "# New\n"
    write(tmp_path / "docs" / "KEEP.md", keep)
    write(tmp_path / "docs" / "NEW.md", new)
    digest_path = write_digest(
        tmp_path,
        [
            digest_entry("docs/OLD.md", source_text="# Old\n"),
            digest_entry("docs/KEEP.md", content_hash=digest_hash("# stale keep\n")),
        ],
    )
    spec_path = write_source_set_spec(
        tmp_path,
        [
            source_set_entry("docs/NEW.md"),
            source_set_entry("docs/KEEP.md"),
        ],
    )
    init_git_repo(tmp_path)
    head = commit_all(tmp_path)

    report = generate_corpus_digest.write_rebaselined_digest(
        tmp_path,
        digest_path,
        spec_path,
        approval_ref=APPROVAL_REF,
        generated_at="2026-02-01T00:00:00Z",
    )
    rebaselined = json.loads(digest_path.read_text(encoding="utf-8"))

    assert report["mode"] == "rebaseline_write"
    assert report["valid"] == 2
    assert report["added_sources"] == ["docs/NEW.md"]
    assert report["removed_sources"] == ["docs/OLD.md"]
    assert rebaselined["git_sha"] == head
    assert rebaselined["source_allow_list_ref"] == "docs/SYNTHETIC_CONTRACT.md#source-set"
    assert [source["source_path"] for source in rebaselined["sources"]] == ["docs/NEW.md", "docs/KEEP.md"]
    assert rebaselined["sources"][0]["content_hash"] == digest_hash(new)
    assert rebaselined["sources"][1]["content_hash"] == digest_hash(keep)
    assert all("temporal_class" not in source for source in rebaselined["sources"])


def test_rebaseline_write_rejects_dirty_source_basis(tmp_path: Path) -> None:
    text = "# Clean\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/OLD.md", source_text="# Old\n")])
    spec_path = write_source_set_spec(tmp_path, [source_set_entry("docs/A.md")])
    init_git_repo(tmp_path)
    commit_all(tmp_path)
    before = digest_path.read_bytes()
    write(tmp_path / "docs" / "A.md", "# Dirty\n")

    with pytest.raises(ValueError, match="differs from HEAD: docs/A.md"):
        generate_corpus_digest.write_rebaselined_digest(
            tmp_path,
            digest_path,
            spec_path,
            approval_ref=APPROVAL_REF,
        )

    assert digest_path.read_bytes() == before


def test_rebaseline_write_rejects_missing_spec_source(tmp_path: Path) -> None:
    digest_path = write_digest(tmp_path, [digest_entry("docs/OLD.md", source_text="# Old\n")])
    spec_path = write_source_set_spec(tmp_path, [source_set_entry("docs/MISSING.md")])
    before = digest_path.read_bytes()

    with pytest.raises(ValueError, match="missing"):
        generate_corpus_digest.write_rebaselined_digest(
            tmp_path,
            digest_path,
            spec_path,
            approval_ref=APPROVAL_REF,
        )

    assert digest_path.read_bytes() == before


def test_rebaseline_write_rejects_invalid_utf8_spec_source(tmp_path: Path) -> None:
    write_raw(tmp_path / "docs" / "BAD.md", b"# Bad\n\xff\xfe\n")
    digest_path = write_digest(tmp_path, [digest_entry("docs/OLD.md", source_text="# Old\n")])
    spec_path = write_source_set_spec(tmp_path, [source_set_entry("docs/BAD.md")])
    before = digest_path.read_bytes()

    with pytest.raises(ValueError, match="invalid UTF-8"):
        generate_corpus_digest.write_rebaselined_digest(
            tmp_path,
            digest_path,
            spec_path,
            approval_ref=APPROVAL_REF,
        )

    assert digest_path.read_bytes() == before


def test_rebaseline_spec_rejects_duplicate_sources(tmp_path: Path) -> None:
    spec_path = write_source_set_spec(
        tmp_path,
        [
            source_set_entry("docs/A.md"),
            source_set_entry("docs/A.md"),
        ],
    )

    with pytest.raises(ValueError, match="duplicate source paths"):
        generate_corpus_digest.load_source_set_spec(spec_path)


@pytest.mark.parametrize(
    "bad_source_path",
    [
        r"C:\repo\docs\A.md",
        "../docs/A.md",
        "artifacts/generated.md",
        "corpus/private.md",
    ],
)
def test_rebaseline_spec_rejects_unsafe_source_paths(tmp_path: Path, bad_source_path: str) -> None:
    spec_path = write_source_set_spec(tmp_path, [source_set_entry(bad_source_path)])

    with pytest.raises(ValueError, match="invalid source_path"):
        generate_corpus_digest.load_source_set_spec(spec_path)


def test_rebaseline_spec_expected_count_must_match_ordered_sources(tmp_path: Path) -> None:
    spec_path = write_source_set_spec(
        tmp_path,
        [source_set_entry("docs/A.md")],
        expected_source_count=2,
    )

    with pytest.raises(ValueError, match="expected_source_count"):
        generate_corpus_digest.load_source_set_spec(spec_path)


def test_rebaseline_spec_rejects_excluded_volatile_overlap(tmp_path: Path) -> None:
    spec_path = write_source_set_spec(
        tmp_path,
        [source_set_entry("STATUS.md")],
        excluded_volatile_sources=["STATUS.md"],
    )

    with pytest.raises(ValueError, match="excluded volatile"):
        generate_corpus_digest.load_source_set_spec(spec_path)


def test_rebaseline_git_sha_override_cannot_weaken_source_basis_guard(tmp_path: Path) -> None:
    text = "# Source\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/OLD.md", source_text="# Old\n")])
    spec_path = write_source_set_spec(tmp_path, [source_set_entry("docs/A.md")])
    init_git_repo(tmp_path)
    commit_all(tmp_path)

    with pytest.raises(ValueError, match="cannot override"):
        generate_corpus_digest.write_rebaselined_digest(
            tmp_path,
            digest_path,
            spec_path,
            approval_ref=APPROVAL_REF,
            git_sha="not-the-head-commit",
        )


def test_rebaseline_head_drift_after_candidate_check_blocks_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(tmp_path / "docs" / "A.md", "# Source at A\n")
    digest_path = write_digest(
        tmp_path,
        [digest_entry("docs/OLD.md", source_text="# Old\n")],
        initialize_git=False,
    )
    spec_path = write_source_set_spec(
        tmp_path, [source_set_entry("docs/A.md")]
    )
    init_git_repo(tmp_path)
    first_head = commit_all(tmp_path, "rebaseline source A")
    write(tmp_path / "docs" / "A.md", "# Source at B\n")
    second_head = commit_all(tmp_path, "rebaseline source B")
    run_git(tmp_path, "reset", "--hard", first_head)
    before = digest_path.read_bytes()
    original_check_sources = generate_corpus_digest.check_sources

    def check_then_advance(*args, **kwargs):
        checks = original_check_sources(*args, **kwargs)
        run_git(tmp_path, "reset", "--hard", second_head)
        return checks

    monkeypatch.setattr(generate_corpus_digest, "check_sources", check_then_advance)

    with pytest.raises(ValueError, match="HEAD changed during source-basis validation"):
        generate_corpus_digest.write_rebaselined_digest(
            tmp_path,
            digest_path,
            spec_path,
            approval_ref=APPROVAL_REF,
        )

    assert digest_path.read_bytes() == before


def test_write_requires_existing_canonical_digest(tmp_path: Path) -> None:
    digest_path = tmp_path / "artifacts" / "corpus-digest.json"
    digest_path.parent.mkdir()

    with pytest.raises(ValueError, match="canonical corpus digest is missing"):
        generate_corpus_digest.write_digest({"sources": []}, digest_path)


def test_parent_junction_is_rejected_without_changing_target(tmp_path: Path) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    before = digest_path.read_bytes()
    real_artifacts = tmp_path / "real-artifacts"
    digest_path.parent.rename(real_artifacts)
    make_junction(tmp_path / "artifacts", real_artifacts)

    with pytest.raises(ValueError, match="reparse point"):
        generate_corpus_digest.check_digest(tmp_path, tmp_path / "artifacts" / digest_path.name)

    assert (real_artifacts / digest_path.name).read_bytes() == before


def test_leaf_reparse_is_rejected_without_changing_previous_bytes(
    tmp_path: Path,
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    before = digest_path.read_bytes()
    previous = digest_path.with_name("previous-corpus-digest.json")
    digest_path.rename(previous)
    target_directory = tmp_path / "junction-target"
    target_directory.mkdir()
    make_junction(digest_path, target_directory)

    with pytest.raises(ValueError, match="reparse point"):
        generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert previous.read_bytes() == before


def test_digest_hardlink_is_rejected_without_changing_bytes(tmp_path: Path) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    before = digest_path.read_bytes()
    os.link(digest_path, digest_path.with_name("digest-alias.json"))

    with pytest.raises(ValueError, match="exactly one hard link"):
        generate_corpus_digest.write_refreshed_digest(
            tmp_path, digest_path, approval_ref=APPROVAL_REF
        )

    assert digest_path.read_bytes() == before


def test_rebaseline_spec_hardlink_is_rejected_without_digest_write(
    tmp_path: Path,
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    write(tmp_path / "docs" / "B.md", "# B\n")
    spec_path = write_source_set_spec(
        tmp_path, [source_set_entry("docs/B.md")]
    )
    commit_all(tmp_path, "add source set")
    before = digest_path.read_bytes()
    os.link(spec_path, spec_path.with_name("source-set-alias.json"))

    with pytest.raises(ValueError, match="exactly one hard link"):
        generate_corpus_digest.write_rebaselined_digest(
            tmp_path,
            digest_path,
            spec_path,
            approval_ref=APPROVAL_REF,
        )

    assert digest_path.read_bytes() == before


def test_directory_leaf_and_non_directory_parent_are_rejected(
    tmp_path: Path,
) -> None:
    (tmp_path / "artifacts").mkdir()
    directory_leaf = tmp_path / "artifacts" / "corpus-digest.json"
    directory_leaf.mkdir()
    with pytest.raises(ValueError, match="not a regular file"):
        generate_corpus_digest._validate_physical_file(
            tmp_path, directory_leaf, label="canonical corpus digest"
        )

    other = tmp_path / "other"
    other.write_text("not a directory", encoding="utf-8")
    with pytest.raises(ValueError, match="non-directory parent"):
        generate_corpus_digest._validate_physical_file(
            tmp_path, other / "corpus-digest.json", label="canonical corpus digest"
        )


def test_pre_replace_target_identity_drift_preserves_existing_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    before = digest_path.read_bytes()
    payload = json.loads(before.decode("utf-8"))
    original = generate_corpus_digest._validate_physical_file
    target_checks = 0

    def drift_on_recheck(repo_root, path, *, label):
        nonlocal target_checks
        identity = original(repo_root, path, label=label)
        if label == "canonical corpus digest":
            target_checks += 1
            if target_checks == 2:
                return generate_corpus_digest.FileIdentity(
                    identity.device,
                    identity.inode + 1,
                    identity.mode,
                    identity.attributes,
                    identity.link_count,
                    identity.size,
                    identity.modified_ns,
                )
        return identity

    monkeypatch.setattr(
        generate_corpus_digest, "_validate_physical_file", drift_on_recheck
    )

    with pytest.raises(ValueError, match="identity changed"):
        generate_corpus_digest.write_digest(payload, digest_path)

    assert digest_path.read_bytes() == before


def test_target_replacement_after_read_is_rejected_before_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    before = digest_path.read_bytes()
    original_builder = generate_corpus_digest.build_refreshed_digest

    def replace_target_after_read(*args, **kwargs):
        candidate = original_builder(*args, **kwargs)
        replacement = digest_path.with_name("replacement-digest.json")
        replacement.write_bytes(before)
        os.replace(replacement, digest_path)
        return candidate

    monkeypatch.setattr(
        generate_corpus_digest,
        "build_refreshed_digest",
        replace_target_after_read,
    )

    with pytest.raises(ValueError, match="changed since it was read"):
        generate_corpus_digest.write_refreshed_digest(
            tmp_path,
            digest_path,
            approval_ref=APPROVAL_REF,
        )

    assert digest_path.read_bytes() == before


def test_pre_replace_parent_identity_drift_preserves_existing_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    before = digest_path.read_bytes()
    payload = json.loads(before.decode("utf-8"))
    monkeypatch.setattr(
        generate_corpus_digest, "_same_physical_object", lambda *_args: False
    )

    with pytest.raises(ValueError, match="parent identity changed"):
        generate_corpus_digest.write_digest(payload, digest_path)

    assert digest_path.read_bytes() == before


def test_pre_replace_temporary_identity_drift_preserves_existing_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    before = digest_path.read_bytes()
    payload = json.loads(before.decode("utf-8"))
    original = generate_corpus_digest._validate_physical_file
    temporary_checks = 0

    def drift_on_final_temp_check(repo_root, path, *, label):
        nonlocal temporary_checks
        identity = original(repo_root, path, label=label)
        if label == "corpus digest temporary file":
            temporary_checks += 1
            if temporary_checks == 3:
                return generate_corpus_digest.FileIdentity(
                    identity.device,
                    identity.inode + 1,
                    identity.mode,
                    identity.attributes,
                    identity.link_count,
                    identity.size,
                    identity.modified_ns,
                )
        return identity

    monkeypatch.setattr(
        generate_corpus_digest,
        "_validate_physical_file",
        drift_on_final_temp_check,
    )

    with pytest.raises(ValueError, match="temporary file identity changed"):
        generate_corpus_digest.write_digest(payload, digest_path)

    assert digest_path.read_bytes() == before


@pytest.mark.parametrize(
    "bad_sha",
    ["A" * 40, "a" * 39, "f" * 40],
)
def test_malformed_or_missing_recorded_sha_fails_closed(
    tmp_path: Path, bad_sha: str
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    before = mutate_digest(
        digest_path, lambda payload: payload.__setitem__("git_sha", bad_sha)
    )

    with pytest.raises(ValueError, match="git_sha"):
        generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert digest_path.read_bytes() != before


def test_invalid_provenance_uses_existing_cli_exit_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    mutate_digest(
        digest_path, lambda payload: payload.__setitem__("git_sha", "A" * 40)
    )

    with pytest.raises(SystemExit) as exc_info:
        generate_corpus_digest.main(["--repo-root", str(tmp_path), "--json"])

    assert exc_info.value.code == 2
    assert "git_sha" in capsys.readouterr().err


def test_non_ancestor_recorded_sha_fails_closed(tmp_path: Path) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    unrelated = tmp_path.parent / f"{tmp_path.name}-unrelated"
    unrelated.mkdir()
    write(unrelated / "unrelated.txt", "unrelated\n")
    init_git_repo(unrelated)
    unrelated_sha = commit_all(unrelated, "unrelated")
    mutate_digest(
        digest_path, lambda payload: payload.__setitem__("git_sha", unrelated_sha)
    )

    with pytest.raises(ValueError, match="missing or is not an ancestor"):
        generate_corpus_digest.check_digest(tmp_path, digest_path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("generated_at", "2026-02-30T00:00:00Z", "generated_at"),
        ("generation_approval_ref", "bad\nref", "control characters"),
        ("source_allow_list_ref", "x" * 257, "1 to 256"),
        ("artifact_path", "artifacts/other.json", "artifact_path"),
    ],
)
def test_top_level_provenance_metadata_fails_closed(
    tmp_path: Path, field: str, value: str, message: str
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    mutate_digest(digest_path, lambda payload: payload.__setitem__(field, value))

    with pytest.raises(ValueError, match=message):
        generate_corpus_digest.check_digest(tmp_path, digest_path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("git_sha", "0" * 40, "git_sha is inconsistent"),
        ("verified_at", "2026-01-02T00:00:00Z", "verified_at is inconsistent"),
        ("reviewer_or_approval_ref", "other", "reviewer_or_approval_ref is inconsistent"),
        ("content_hash", "0" * 64, "hash does not match recorded basis"),
    ],
)
def test_per_source_provenance_mismatch_fails_closed(
    tmp_path: Path, field: str, value: str, message: str
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    mutate_digest(
        digest_path,
        lambda payload: payload["sources"][0].__setitem__(field, value),
    )

    with pytest.raises(ValueError, match=message):
        generate_corpus_digest.check_digest(tmp_path, digest_path)


@pytest.mark.parametrize("casefold_only", [False, True])
def test_duplicate_source_paths_fail_closed(
    tmp_path: Path, casefold_only: bool
) -> None:
    digest_path = prepare_valid_digest(tmp_path)

    def duplicate(payload):
        item = dict(payload["sources"][0])
        if casefold_only:
            item["source_path"] = "DOCS/A.md"
        payload["sources"].append(item)
        payload["precheck_summary"]["source_count"] = 2
        payload["closeout"]["source_count"] = 2

    mutate_digest(digest_path, duplicate)
    expected = "casefold-duplicate" if casefold_only else "duplicate source paths"

    with pytest.raises(ValueError, match=expected):
        generate_corpus_digest.check_digest(tmp_path, digest_path)


@pytest.mark.parametrize("container", ["precheck_summary", "closeout"])
def test_source_count_mismatch_fails_closed(
    tmp_path: Path, container: str
) -> None:
    digest_path = prepare_valid_digest(tmp_path)
    mutate_digest(
        digest_path,
        lambda payload: payload[container].__setitem__("source_count", 99),
    )

    with pytest.raises(ValueError, match="source_count is inconsistent"):
        generate_corpus_digest.check_digest(tmp_path, digest_path)
