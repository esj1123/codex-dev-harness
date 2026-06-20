import json
from pathlib import Path
import subprocess

import pytest

from scripts import generate_corpus_digest


APPROVAL_REF = "owner_approved_phase_6g_digest_refresh_task"


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


def write_digest(root: Path, sources: list[dict[str, object]]) -> Path:
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
    return digest_path


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
    return run_git(root, "rev-parse", "HEAD")


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
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", content_hash=digest_hash("old\n"))])
    init_git_repo(tmp_path)
    commit_all(tmp_path)
    write(tmp_path / "docs" / "A.md", "# Modified\n")

    with pytest.raises(ValueError, match="differs from HEAD: docs/A.md"):
        generate_corpus_digest.write_refreshed_digest(tmp_path, digest_path, approval_ref=APPROVAL_REF)


def test_staged_digest_listed_source_blocks_write(tmp_path: Path) -> None:
    text = "# Clean\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", content_hash=digest_hash("old\n"))])
    init_git_repo(tmp_path)
    commit_all(tmp_path)
    write(tmp_path / "docs" / "A.md", "# Staged\n")
    run_git(tmp_path, "add", "docs/A.md")

    with pytest.raises(ValueError, match="differs from HEAD: docs/A.md"):
        generate_corpus_digest.write_refreshed_digest(tmp_path, digest_path, approval_ref=APPROVAL_REF)


def test_clean_committed_digest_listed_source_permits_refresh_write(tmp_path: Path) -> None:
    text = "# Current source\n"
    write(tmp_path / "docs" / "A.md", text)
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", content_hash=digest_hash("old\n"))])
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
    digest_path = write_digest(tmp_path, [digest_entry("docs/A.md", source_text=text)])
    init_git_repo(tmp_path)
    commit_all(tmp_path)

    with pytest.raises(ValueError, match="cannot override"):
        generate_corpus_digest.write_refreshed_digest(
            tmp_path,
            digest_path,
            approval_ref=APPROVAL_REF,
            git_sha="not-the-head-commit",
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
