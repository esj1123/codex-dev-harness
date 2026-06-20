import hashlib
import json
from pathlib import Path
import subprocess

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


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def init_git_repo(root: Path) -> None:
    run_git(root, "init")
    run_git(root, "config", "user.email", "synthetic@example.invalid")
    run_git(root, "config", "user.name", "Synthetic Tester")


def commit_all(root: Path, message: str = "synthetic commit") -> str:
    run_git(root, "add", ".")
    run_git(root, "commit", "-m", message)
    return run_git(root, "rev-parse", "HEAD").stdout.strip()


def make_git_overlay_repo(root: Path) -> str:
    init_git_repo(root)
    status_text = "# Status\n\nThe next recommended task is Phase 7C.3D overlay implementation.\n"
    trace_text = "# Acceptance Trace\n\nPhase 7C.3D current implementation evidence row is pending.\n"
    policy_text = "# Verification Policy\n\nLocal verification commands use pytest and quality gate.\n"
    write(root / "STATUS.md", status_text)
    write(root / "ACCEPTANCE_TRACE.md", trace_text)
    write(root / "docs" / "VERIFICATION.md", policy_text)
    write_digest(
        root,
        [
            digest_source("STATUS.md", source_text=status_text, content_class="repo_baseline"),
            digest_source("ACCEPTANCE_TRACE.md", source_text=trace_text, content_class="repo_baseline"),
            digest_source("docs/VERIFICATION.md", source_text=policy_text, content_class="verification_policy"),
        ],
    )
    return commit_all(root)


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


def test_exact_volatile_allow_list_accepts_only_status_and_trace() -> None:
    assert retriever.validate_volatile_source_path("STATUS.md") == ("STATUS.md", None)
    assert retriever.validate_volatile_source_path("ACCEPTANCE_TRACE.md") == ("ACCEPTANCE_TRACE.md", None)
    for path in (
        "README.md",
        "C:/tmp/STATUS.md",
        "/tmp/STATUS.md",
        "../STATUS.md",
        "docs/../STATUS.md",
        ".//STATUS.md",
        "STATUS.MD",
        "status.md",
        "STATUS.md ",
        r".\STATUS.md",
        r"docs\STATUS.md",
    ):
        normalized, reason = retriever.validate_volatile_source_path(path)
        assert normalized is None
        assert reason is not None


def test_query_classifier_is_deterministic_for_required_classes() -> None:
    cases = {
        "next recommended task": "current_state",
        "current implementation sequence": "current_state",
        "current approved corpus digest status": "current_state",
        "latest verification status": "current_state",
        "local verification commands": "durable_policy",
        "receipt redaction policy": "durable_policy",
        "safety policy": "durable_policy",
        "optional CI decision": "historical_decision",
        "release history": "historical_decision",
        "Phase 6G approved corpus digest refresh": "mixed_context",
        "unclassified lexical query": "durable_policy",
        "current release history": "mixed_context",
    }
    for query, expected in cases.items():
        assert retriever.classify_query(query) == expected
        assert retriever.classify_query(query) == expected


def test_current_state_reads_committed_head_overlay_and_metadata(tmp_path: Path) -> None:
    head = make_git_overlay_repo(tmp_path)

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=5)

    assert payload["status"] == "found"
    assert payload["query_class"] == "current_state"
    assert payload["observed_head_commit"] == head
    assert payload["stable_digest_ref"] == "artifacts/corpus-digest.json"
    status_result = payload["matched_sources"][0]
    assert status_result["source_path"] == "STATUS.md"
    assert status_result["temporal_class"] == "volatile_current_authority"
    assert status_result["authority_level"] == "current_operational_state"
    assert status_result["observed_head_commit"] == head
    assert len(status_result["volatile_content_hash"]) == 64
    assert status_result["operational_freshness"] == "unknown"
    assert status_result["section_authority"] == "unknown"
    assert "Phase 7C.3D" in status_result["evidence_excerpt"]


def test_dirty_working_tree_status_is_ignored_for_volatile_overlay(tmp_path: Path) -> None:
    make_git_overlay_repo(tmp_path)
    write(tmp_path / "STATUS.md", "# Dirty\n\nThe next recommended task is dirty working tree text.\n")

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=3)
    text = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "found"
    assert "Phase 7C.3D overlay implementation" in text
    assert "dirty working tree text" not in text


def test_staged_status_is_ignored_for_volatile_overlay(tmp_path: Path) -> None:
    make_git_overlay_repo(tmp_path)
    write(tmp_path / "STATUS.md", "# Staged\n\nThe next recommended task is staged text.\n")
    run_git(tmp_path, "add", "STATUS.md")

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=3)
    text = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "found"
    assert "Phase 7C.3D overlay implementation" in text
    assert "staged text" not in text


def test_volatile_hash_uses_lf_normalized_committed_bytes(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    status_lf = "# Status\n\nThe next recommended task uses CRLF normalized hashing.\n"
    write(tmp_path / "STATUS.md", status_lf.replace("\n", "\r\n"))
    write(tmp_path / "ACCEPTANCE_TRACE.md", "# Trace\n\nNo matching text.\n")
    write_digest(tmp_path, [])
    commit_all(tmp_path)

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=3)
    status_result = payload["matched_sources"][0]

    assert status_result["source_path"] == "STATUS.md"
    assert status_result["volatile_content_hash"] == digest_hash(status_lf)


def test_invalid_utf8_committed_volatile_blob_is_safely_rejected(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    write_raw(tmp_path / "STATUS.md", b"# Status\n\nnext recommended task \xff\n")
    write(tmp_path / "ACCEPTANCE_TRACE.md", "# Trace\n\nNo matching text.\n")
    write_digest(tmp_path, [])
    commit_all(tmp_path)

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=3)

    assert payload["status"] == "no_sufficient_evidence"
    assert "source is not UTF-8 text" in "\n".join(payload["safety_notes"])
    assert "local absolute" not in "\n".join(payload["safety_notes"]).lower()


def test_no_filesystem_fallback_when_git_read_fails_with_stable_evidence(tmp_path: Path) -> None:
    current_text = "# Stable\n\nThe next recommended task appears only in stable evidence.\n"
    write(tmp_path / "docs" / "CURRENT.md", current_text)
    write_digest(tmp_path, [digest_source("docs/CURRENT.md", source_text=current_text)])

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=3)

    assert payload["status"] == "partial"
    assert payload["matched_sources"][0]["source_path"] == "docs/CURRENT.md"
    assert "volatile current authority" in payload["no_answer_reason"]


def test_no_filesystem_fallback_when_git_read_fails_without_stable_evidence(tmp_path: Path) -> None:
    write_digest(tmp_path, [])

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=3)

    assert payload["status"] == "no_sufficient_evidence"
    assert payload["matched_sources"] == []
    assert "committed-HEAD volatile authority is unavailable" in payload["no_answer_reason"]


def test_same_path_duplicate_prefers_volatile_for_current_state(tmp_path: Path) -> None:
    make_git_overlay_repo(tmp_path)

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=10)
    paths = [source["source_path"] for source in payload["matched_sources"]]

    assert paths.count("STATUS.md") == 1
    status_result = next(source for source in payload["matched_sources"] if source["source_path"] == "STATUS.md")
    assert "volatile_content_hash" in status_result
    assert "content_hash" not in status_result


def test_durable_policy_preserves_stable_only_precedence(tmp_path: Path) -> None:
    make_git_overlay_repo(tmp_path)

    payload = retriever.retrieve(tmp_path, "local verification commands", max_results=5)

    assert payload["status"] == "found"
    assert payload["query_class"] == "durable_policy"
    assert "observed_head_commit" not in payload
    assert payload["matched_sources"][0]["source_path"] == "docs/VERIFICATION.md"
    assert "content_hash" in payload["matched_sources"][0]


def test_max_results_applies_after_merge_and_dedup(tmp_path: Path) -> None:
    make_git_overlay_repo(tmp_path)

    payload = retriever.retrieve(tmp_path, "Phase 7C.3D current implementation", max_results=1)

    assert payload["status"] == "found"
    assert len(payload["matched_sources"]) == 1
    assert payload["matched_sources"][0]["source_path"] in {"STATUS.md", "ACCEPTANCE_TRACE.md"}


def test_action_shaped_query_remains_advisory_only(tmp_path: Path) -> None:
    make_repo(tmp_path)

    payload = retriever.retrieve(tmp_path, "modify the release workflow", max_results=3)

    assert "retrieval is advisory-only" in payload["safety_notes"]
    assert "no action was performed" in payload["safety_notes"]
    assert "retrieval grants no approval" in payload["safety_notes"]


def test_stable_only_non_git_repo_remains_backward_compatible(tmp_path: Path) -> None:
    make_repo(tmp_path)

    payload = retriever.retrieve(tmp_path, "Phase lexical", max_results=2)

    assert payload["status"] == "found"
    assert payload["query_class"] == "durable_policy"
    assert payload["matched_sources"][0]["source_path"] == "docs/CURRENT_POLICY.md"
    assert "observed_head_commit" not in payload


def test_current_state_output_is_deterministic(tmp_path: Path) -> None:
    make_git_overlay_repo(tmp_path)

    first = retriever.retrieve(tmp_path, "next recommended task", max_results=3)
    second = retriever.retrieve(tmp_path, "next recommended task", max_results=3)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_no_raw_git_stderr_or_local_absolute_path_in_failure_output(tmp_path: Path) -> None:
    write_digest(tmp_path, [])

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=3)
    text = json.dumps(payload, sort_keys=True)

    assert str(tmp_path) not in text
    assert "fatal:" not in text.lower()
    assert "usage:" not in text.lower()


def test_bounded_excerpts_for_volatile_sources(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    long_text = "# Status\n\nThe next recommended task is " + ("bounded " * 100) + "\n"
    write(tmp_path / "STATUS.md", long_text)
    write(tmp_path / "ACCEPTANCE_TRACE.md", "# Trace\n\nNo matching text.\n")
    write_digest(tmp_path, [])
    commit_all(tmp_path)

    payload = retriever.retrieve(tmp_path, "next recommended task", max_results=3)

    assert len(payload["matched_sources"][0]["evidence_excerpt"]) <= retriever.MAX_EXCERPT_LENGTH


def test_git_invocation_uses_argument_list_shell_false_and_timeout(tmp_path: Path, monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(args, **kwargs):
        calls.append({"args": args, **kwargs})
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="a" * 40 + "\n", stderr="")

    monkeypatch.setattr(retriever.subprocess, "run", fake_run)

    head, reason = retriever.observed_head_commit(tmp_path)

    assert reason is None
    assert head == "a" * 40
    assert isinstance(calls[0]["args"], list)
    assert calls[0]["shell"] is False
    assert calls[0]["timeout"] == retriever.GIT_TIMEOUT_SECONDS


def test_read_committed_blob_uses_cat_file_without_shell(tmp_path: Path, monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(args, **kwargs):
        calls.append({"args": args, **kwargs})
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=b"blob bytes", stderr=b"")

    monkeypatch.setattr(retriever.subprocess, "run", fake_run)

    blob, reason = retriever.read_committed_blob(tmp_path, "STATUS.md")

    assert reason is None
    assert blob == b"blob bytes"
    assert calls[0]["args"] == ["git", "cat-file", "blob", "HEAD:STATUS.md"]
    assert calls[0]["shell"] is False
    assert calls[0]["timeout"] == retriever.GIT_TIMEOUT_SECONDS
