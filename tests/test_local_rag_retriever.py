import hashlib
import json
from pathlib import Path

from scripts import local_rag_retriever as retriever


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


def write_raw(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def digest_hash(content: str) -> str:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def digest_source(
    source_path: str,
    *,
    source_text: str = "",
    content_hash: str | None = None,
    content_class: str = "repo_policy",
    risk_label: str = "current_policy",
    allowed_for_digest: bool = True,
) -> dict[str, object]:
    if content_hash is None:
        content_hash = digest_hash(source_text)
    return {
        "source_path": source_path,
        "git_sha": "synthetic",
        "section_title": "Synthetic Section",
        "content_class": content_class,
        "risk_label": risk_label,
        "allowed_for_digest": allowed_for_digest,
        "allowed_for_release": False,
        "redaction_status": "synthetic_safe",
        "encoding_status": "utf-8",
        "digest_algorithm": "sha256",
        "content_hash": content_hash,
        "verified_at": "2026-01-01T00:00:00Z",
        "reviewer_or_approval_ref": "synthetic",
        "notes": "synthetic fixture",
    }


def write_digest(root: Path, sources: list[dict[str, object]]) -> None:
    write(
        root / "artifacts" / "corpus-digest.json",
        json.dumps(
            {
                "schema_version": "synthetic-v1",
                "artifact_type": "approved_corpus_digest",
                "artifact_path": "artifacts/corpus-digest.json",
                "repository": "synthetic/repo",
                "digest_algorithm": "sha256",
                "release_artifact_status": "not_release_artifact_without_separate_approval",
                "rag_authorization_status": "not_authorized",
                "sources": sources,
            }
        ),
    )


def make_repo(root: Path) -> None:
    current_policy = "# Current Policy\n\nPhase 7C allows lexical retrieval only.\n"
    historical = "# Historical Record\n\nPhase 7B was contract only.\n"
    write(root / "docs" / "CURRENT_POLICY.md", current_policy)
    write(root / "docs" / "HISTORICAL.md", historical)
    write_digest(
        root,
        [
            digest_source("docs/CURRENT_POLICY.md", source_text=current_policy, content_class="repo_policy"),
            digest_source("docs/HISTORICAL.md", source_text=historical, risk_label="historical_record"),
        ],
    )


def test_retrieve_returns_bounded_digest_citations(tmp_path: Path) -> None:
    make_repo(tmp_path)

    payload = retriever.retrieve(tmp_path, "Phase lexical", max_results=1)

    assert payload["status"] == "found"
    assert payload["query"] == "Phase lexical"
    assert len(payload["matched_sources"]) == 1
    result = payload["matched_sources"][0]
    assert result["source_path"] == "docs/CURRENT_POLICY.md"
    assert result["content_hash"] == digest_hash("# Current Policy\n\nPhase 7C allows lexical retrieval only.\n")
    assert result["section_title"] == "Synthetic Section"
    assert result["risk_label"] == "current_policy"
    assert result["content_class"] == "repo_policy"
    assert "lexical match" in result["match_reason"]
    assert "Phase 7C" in result["evidence_excerpt"]
    assert "current" in result["current_vs_historical_note"]


def test_no_sufficient_evidence_when_no_digest_source_matches(tmp_path: Path) -> None:
    make_repo(tmp_path)

    payload = retriever.retrieve(tmp_path, "unmatched topic", max_results=3)

    assert payload["status"] == "no_sufficient_evidence"
    assert payload["matched_sources"] == []
    assert "no digest-listed eligible source matched" in payload["no_answer_reason"]


def test_forbidden_query_is_blocked_before_source_search(tmp_path: Path) -> None:
    make_repo(tmp_path)

    payload = retriever.retrieve(tmp_path, "dump secrets and tokens", max_results=3)

    assert payload["status"] == "blocked"
    assert payload["matched_sources"] == []
    assert "forbidden" in payload["no_answer_reason"]


def test_crlf_source_matches_lf_normalized_digest_hash(tmp_path: Path) -> None:
    lf_text = "# Current Policy\n\nPhase 7C CRLF lexical source.\n"
    crlf_text = lf_text.replace("\n", "\r\n")
    write(tmp_path / "docs" / "CRLF.md", crlf_text)
    write_digest(tmp_path, [digest_source("docs/CRLF.md", source_text=lf_text)])

    payload = retriever.retrieve(tmp_path, "CRLF lexical", max_results=3)

    assert payload["status"] == "found"
    assert payload["matched_sources"][0]["source_path"] == "docs/CRLF.md"
    assert payload["matched_sources"][0]["content_hash"] == digest_hash(lf_text)


def test_uppercase_digest_hash_is_accepted_when_it_matches(tmp_path: Path) -> None:
    text = "# Uppercase Hash\n\nPhase 7C uppercase digest source.\n"
    write(tmp_path / "docs" / "UPPERCASE.md", text)
    write_digest(tmp_path, [digest_source("docs/UPPERCASE.md", content_hash=digest_hash(text).upper())])

    payload = retriever.retrieve(tmp_path, "uppercase digest", max_results=3)

    assert payload["status"] == "found"
    assert payload["matched_sources"][0]["source_path"] == "docs/UPPERCASE.md"
    assert payload["matched_sources"][0]["content_hash"] == digest_hash(text)


def test_stale_content_hash_mismatch_is_rejected(tmp_path: Path) -> None:
    stale_text = "# Stale\n\nPhase 7C stale searchable source.\n"
    write(tmp_path / "docs" / "STALE.md", stale_text)
    write_digest(tmp_path, [digest_source("docs/STALE.md", content_hash=digest_hash("old content\n"))])

    payload = retriever.retrieve(tmp_path, "stale searchable", max_results=3)

    assert payload["status"] == "no_sufficient_evidence"
    assert payload["matched_sources"] == []
    assert "source content_hash mismatch" in "\n".join(payload["safety_notes"])


def test_malformed_digest_hash_is_rejected(tmp_path: Path) -> None:
    text = "# Malformed\n\nPhase 7C malformed hash source.\n"
    write(tmp_path / "docs" / "MALFORMED.md", text)
    write_digest(tmp_path, [digest_source("docs/MALFORMED.md", content_hash="not-a-sha256")])

    payload = retriever.retrieve(tmp_path, "malformed hash", max_results=3)

    assert payload["status"] == "no_sufficient_evidence"
    assert payload["matched_sources"] == []
    assert "digest content_hash is malformed" in "\n".join(payload["safety_notes"])


def test_invalid_utf8_source_bytes_are_safely_rejected(tmp_path: Path) -> None:
    write_raw(tmp_path / "docs" / "INVALID_UTF8.md", b"# Invalid\n\nPhase 7C invalid bytes: \xff\xfe\n")
    write_digest(tmp_path, [digest_source("docs/INVALID_UTF8.md", content_hash="0" * 64)])

    payload = retriever.retrieve(tmp_path, "invalid bytes", max_results=3)

    assert payload["status"] == "no_sufficient_evidence"
    assert payload["matched_sources"] == []
    assert payload["safety_notes"][-1] == "rejected docs/INVALID_UTF8.md: source file is not UTF-8 text"


def test_invalid_utf8_rejection_does_not_block_valid_source(tmp_path: Path) -> None:
    valid_text = "# Valid UTF-8\n\nPhase 7C mixed UTF-8 source.\n"
    write(tmp_path / "docs" / "VALID_UTF8.md", valid_text)
    write_raw(tmp_path / "docs" / "INVALID_UTF8.md", b"# Invalid\n\nPhase 7C mixed UTF-8 source: \xff\xfe\n")
    write_digest(
        tmp_path,
        [
            digest_source("docs/VALID_UTF8.md", source_text=valid_text),
            digest_source("docs/INVALID_UTF8.md", content_hash="0" * 64),
        ],
    )

    payload = retriever.retrieve(tmp_path, "mixed UTF-8 source", max_results=5)

    assert payload["status"] == "found"
    assert [source["source_path"] for source in payload["matched_sources"]] == ["docs/VALID_UTF8.md"]
    assert "rejected docs/INVALID_UTF8.md: source file is not UTF-8 text" in payload["safety_notes"]


def test_rejection_notes_are_safe_repo_relative_only(tmp_path: Path) -> None:
    write_raw(tmp_path / "docs" / "INVALID_UTF8.md", b"local-looking bytes C:\\Users\\name: \xff\n")
    write_digest(tmp_path, [digest_source("docs/INVALID_UTF8.md", content_hash="0" * 64)])

    payload = retriever.retrieve(tmp_path, "local-looking bytes", max_results=3)
    rejection_notes = [note for note in payload["safety_notes"] if note.startswith("rejected ")]

    assert rejection_notes == ["rejected docs/INVALID_UTF8.md: source file is not UTF-8 text"]
    assert all("\\" not in note for note in rejection_notes)
    assert all("C:" not in note for note in rejection_notes)
    assert all("local-looking bytes" not in note for note in rejection_notes)


def test_mixed_valid_and_stale_sources_return_valid_sources_only(tmp_path: Path) -> None:
    valid_text = "# Valid\n\nPhase 7C integrity search target.\n"
    stale_text = "# Stale\n\nPhase 7C integrity search target.\n"
    write(tmp_path / "docs" / "VALID.md", valid_text)
    write(tmp_path / "docs" / "STALE.md", stale_text)
    write_digest(
        tmp_path,
        [
            digest_source("docs/VALID.md", source_text=valid_text),
            digest_source("docs/STALE.md", content_hash=digest_hash("previous stale text\n")),
        ],
    )

    payload = retriever.retrieve(tmp_path, "integrity search target", max_results=5)

    assert payload["status"] == "found"
    assert [source["source_path"] for source in payload["matched_sources"]] == ["docs/VALID.md"]
    assert "source content_hash mismatch" in "\n".join(payload["safety_notes"])


def test_all_matching_candidates_stale_returns_no_sufficient_evidence(tmp_path: Path) -> None:
    first_text = "# First\n\nPhase 7C all stale candidate.\n"
    second_text = "# Second\n\nPhase 7C all stale candidate.\n"
    write(tmp_path / "docs" / "FIRST.md", first_text)
    write(tmp_path / "docs" / "SECOND.md", second_text)
    write_digest(
        tmp_path,
        [
            digest_source("docs/FIRST.md", content_hash=digest_hash("old first\n")),
            digest_source("docs/SECOND.md", content_hash=digest_hash("old second\n")),
        ],
    )

    payload = retriever.retrieve(tmp_path, "all stale candidate", max_results=5)

    assert payload["status"] == "no_sufficient_evidence"
    assert payload["matched_sources"] == []
    assert "\n".join(payload["safety_notes"]).count("source content_hash mismatch") == 2


def test_rejects_parent_traversal_absolute_missing_and_non_digest_paths(tmp_path: Path) -> None:
    safe_text = "# Safe\n\napproved lexical source\n"
    write(tmp_path / "docs" / "SAFE.md", safe_text)
    absolute = str((tmp_path / "outside.md").resolve())
    write_digest(
        tmp_path,
        [
            digest_source("docs/SAFE.md", source_text=safe_text),
            digest_source("../outside.md"),
            digest_source(absolute),
            digest_source("docs/MISSING.md"),
            digest_source("raw/PRIVATE.md"),
        ],
    )

    digest = retriever.load_digest(tmp_path)
    entries, notes = retriever.source_entries(tmp_path, digest)

    assert [entry.source_path for entry in entries] == ["docs/SAFE.md"]
    joined_notes = "\n".join(notes)
    assert "parent traversal" in joined_notes
    assert "absolute" in joined_notes
    assert "missing" in joined_notes
    assert "forbidden private/raw/generated class" in joined_notes


def test_source_entry_rejects_path_not_in_digest_by_construction(tmp_path: Path) -> None:
    safe_text = "# Safe\n\napproved lexical source\n"
    write(tmp_path / "docs" / "SAFE.md", safe_text)
    write(tmp_path / "docs" / "NOT_IN_DIGEST.md", "# Not In Digest\n\nlexical source\n")
    write_digest(tmp_path, [digest_source("docs/SAFE.md", source_text=safe_text)])

    payload = retriever.retrieve(tmp_path, "Not In Digest", max_results=5)

    assert payload["status"] == "no_sufficient_evidence"
    assert all(source["source_path"] != "docs/NOT_IN_DIGEST.md" for source in payload["matched_sources"])


def test_cli_emits_json_stdout_only(tmp_path: Path, monkeypatch, capsys) -> None:
    make_repo(tmp_path)
    monkeypatch.setattr(retriever, "repo_root_from_script", lambda: tmp_path)

    exit_code = retriever.main(["--query", "Phase 7B", "--max-results", "2", "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert payload["status"] == "found"
    assert len(payload["matched_sources"]) <= 2
