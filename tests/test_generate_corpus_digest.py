import json
from pathlib import Path

from scripts import generate_corpus_digest


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


def test_invalid_utf8_is_reported_without_writing(tmp_path: Path) -> None:
    write_raw(tmp_path / "docs" / "BAD.md", b"# Bad\n\xff\xfe\n")
    digest_path = write_digest(tmp_path, [digest_entry("docs/BAD.md", content_hash="0" * 64)])

    report = generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert report["invalid_utf8"] == 1
    assert report["refresh_required"] is True
    assert report["sources"][0]["source_path"] == "docs/BAD.md"


def test_missing_and_unsafe_paths_are_reported(tmp_path: Path) -> None:
    digest_path = write_digest(
        tmp_path,
        [
            digest_entry("docs/MISSING.md", content_hash="0" * 64),
            digest_entry("../ESCAPE.md", content_hash="0" * 64),
        ],
    )

    report = generate_corpus_digest.check_digest(tmp_path, digest_path)

    assert report["missing"] == 1
    assert report["unsafe"] == 1
    assert report["refresh_required"] is True


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
    digest = generate_corpus_digest.load_digest(digest_path)
    checks = generate_corpus_digest.check_sources(tmp_path, digest)

    refreshed = generate_corpus_digest.build_refreshed_digest(
        digest,
        checks,
        git_sha="new-basis",
        generated_at="2026-02-01T00:00:00Z",
        approval_ref="owner_approved_phase_6g_digest_refresh_task",
    )

    assert [source["source_path"] for source in refreshed["sources"]] == ["docs/FIRST.md", "docs/SECOND.md"]
    assert refreshed["release_artifact_status"] == digest["release_artifact_status"]
    assert refreshed["rag_authorization_status"] == digest["rag_authorization_status"]
    assert refreshed["sources"][1]["content_hash"] == digest_hash(second)
    assert refreshed["sources"][1]["git_sha"] == "new-basis"


def test_write_requires_explicit_approval_and_updates_only_template_sources(tmp_path: Path) -> None:
    text = "# Refresh me\n"
    write(tmp_path / "docs" / "REFRESH.md", text)
    write(tmp_path / "docs" / "NOT_IN_DIGEST.md", "not approved\n")
    digest_path = write_digest(
        tmp_path,
        [digest_entry("docs/REFRESH.md", content_hash=digest_hash("old text\n"))],
    )

    try:
        generate_corpus_digest.write_refreshed_digest(tmp_path, digest_path, approval_ref="")
    except ValueError as exc:
        assert "approval-ref" in str(exc)
    else:
        raise AssertionError("write should require explicit approval")

    report = generate_corpus_digest.write_refreshed_digest(
        tmp_path,
        digest_path,
        approval_ref="owner_approved_phase_6g_digest_refresh_task",
        git_sha="new-basis",
        generated_at="2026-02-01T00:00:00Z",
    )
    refreshed = json.loads(digest_path.read_text(encoding="utf-8"))

    assert report["valid"] == 1
    assert report["refresh_required"] is False
    assert [source["source_path"] for source in refreshed["sources"]] == ["docs/REFRESH.md"]
    assert refreshed["sources"][0]["content_hash"] == digest_hash(text)
    assert refreshed["git_sha"] == "new-basis"
    assert refreshed["generation_approval_ref"] == "owner_approved_phase_6g_digest_refresh_task"
