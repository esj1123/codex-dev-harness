import json
from pathlib import Path

from scripts import local_rag_retriever as retriever


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def digest_source(
    source_path: str,
    *,
    content_hash: str = "abc123",
    content_class: str = "repo_policy",
    risk_label: str = "current_policy",
    allowed_for_digest: bool = True,
) -> dict[str, object]:
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
    write(root / "docs" / "CURRENT_POLICY.md", "# Current Policy\n\nPhase 7C allows lexical retrieval only.\n")
    write(root / "docs" / "HISTORICAL.md", "# Historical Record\n\nPhase 7B was contract only.\n")
    write_digest(
        root,
        [
            digest_source("docs/CURRENT_POLICY.md", content_hash="hash-current", content_class="repo_policy"),
            digest_source("docs/HISTORICAL.md", content_hash="hash-historical", risk_label="historical_record"),
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
    assert result["content_hash"] == "hash-current"
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


def test_rejects_parent_traversal_absolute_missing_and_non_digest_paths(tmp_path: Path) -> None:
    write(tmp_path / "docs" / "SAFE.md", "# Safe\n\napproved lexical source\n")
    absolute = str((tmp_path / "outside.md").resolve())
    write_digest(
        tmp_path,
        [
            digest_source("docs/SAFE.md", content_hash="hash-safe"),
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
    write(tmp_path / "docs" / "SAFE.md", "# Safe\n\napproved lexical source\n")
    write(tmp_path / "docs" / "NOT_IN_DIGEST.md", "# Not In Digest\n\nlexical source\n")
    write_digest(tmp_path, [digest_source("docs/SAFE.md", content_hash="hash-safe")])

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
