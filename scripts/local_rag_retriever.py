"""Minimal local-only lexical retriever over the approved corpus digest.

The retriever is read-only: it loads the digest, reads only digest-listed
repo-owned source files, and prints bounded advisory JSON to stdout.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any


DEFAULT_DIGEST_PATH = "artifacts/corpus-digest.json"
DEFAULT_MAX_RESULTS = 5
MAX_RESULTS_LIMIT = 10
MAX_QUERY_LENGTH = 160
MAX_EXCERPT_LENGTH = 240
GIT_TIMEOUT_SECONDS = 5

VOLATILE_AUTHORITY_SOURCES = {
    "STATUS.md": {
        "temporal_class": "volatile_current_authority",
        "authority_level": "current_operational_state",
    },
    "ACCEPTANCE_TRACE.md": {
        "temporal_class": "volatile_current_authority",
        "authority_level": "current_operational_state",
    },
}

FORBIDDEN_PATH_PARTS = {
    ".git",
    "08_study",
    "attachments",
    "corpus",
    "credentials",
    "exports",
    "index",
    "local",
    "logs",
    "private",
    "processed",
    "raw",
    "retrieval",
    "secrets",
}

FORBIDDEN_PATH_PREFIXES = (
    ".github/workflows/",
    "artifacts/",
    "evals/golden/",
)

FORBIDDEN_METADATA_TERMS = (
    "private",
    "raw",
    "downstream",
    "rsid",
    "08_study",
    "generated_downstream",
)

FORBIDDEN_QUERY_PATTERNS = (
    re.compile(r"\b(dump|show|print|reveal|extract|exfiltrate|list)\b.{0,40}\b(secrets?|tokens?|credentials?|passwords?|keys?)\b", re.I),
    re.compile(r"\b(raw prompt|prompt transcript|model output|tool-call|tool call|raw command log)\b", re.I),
    re.compile(r"\b(08[_ -]?study|rsid raw|downstream raw|private raw|generated downstream)\b", re.I),
    re.compile(r"\b(live config|device value|account value|broker value|equipment value)\b", re.I),
)

WINDOWS_ABSOLUTE_RE = re.compile(r"[A-Za-z]:[\\/][^\s]*")
POSIX_ABSOLUTE_RE = re.compile(r"(^|\s)/(?:Users|home|etc|var|tmp|mnt|opt|root)\b[^\s]*")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ASSIGNMENT_SECRET_RE = re.compile(r"(?i)\b(secret|token|password|credential|api[_-]?key)\s*[:=]\s*\S+")
TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{1,}")
SHA256_HEX_RE = re.compile(r"^[0-9a-fA-F]{64}$")
FULL_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
ACTION_SHAPED_QUERY_RE = re.compile(
    r"\b(modify|change|edit|write|create|delete|remove|run|execute|push|commit|release|deploy|upload)\b",
    re.I,
)


@dataclass(frozen=True)
class SourceEntry:
    source_path: str
    section_title: str
    content_hash: str
    risk_label: str
    content_class: str
    full_path: Path
    text: str
    note: str


@dataclass(frozen=True)
class Match:
    score: int
    entry: SourceEntry
    matched_terms: tuple[str, ...]
    text: str
    first_position: int


@dataclass(frozen=True)
class VolatileSourceEntry:
    source_path: str
    section_title: str
    temporal_class: str
    authority_level: str
    observed_head_commit: str
    volatile_content_hash: str
    operational_freshness: str
    section_authority: str
    text: str


@dataclass(frozen=True)
class VolatileMatch:
    score: int
    entry: VolatileSourceEntry
    matched_terms: tuple[str, ...]
    text: str
    first_position: int


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def sanitize_query(query: str) -> str:
    return " ".join(query.strip().split())


def query_block_reason(query: str) -> str | None:
    sanitized = sanitize_query(query)
    if not sanitized:
        return "query is empty"
    if len(sanitized) > MAX_QUERY_LENGTH:
        return "query exceeds the short-query limit"
    if "\n" in query or "\r" in query:
        return "query appears to contain a prompt transcript or multiline content"
    if WINDOWS_ABSOLUTE_RE.search(sanitized) or POSIX_ABSOLUTE_RE.search(sanitized):
        return "query includes a local absolute path"
    for pattern in FORBIDDEN_QUERY_PATTERNS:
        if pattern.search(sanitized):
            return "query asks for forbidden private, raw, secret, live, or transcript material"
    return None


def classify_query(query: str) -> str:
    normalized = sanitize_query(query).lower()
    if not normalized:
        return "durable_policy"

    current_phrases = (
        "next recommended task",
        "current implementation sequence",
        "current approved corpus digest status",
        "latest verification status",
    )
    durable_phrases = (
        "local verification commands",
        "receipt redaction policy",
        "safety policy",
    )
    historical_phrases = (
        "optional ci decision",
        "release history",
    )
    mixed_phrases = (
        "phase 6g approved corpus digest refresh",
    )
    if any(phrase in normalized for phrase in mixed_phrases):
        return "mixed_context"
    has_current_signal = any(phrase in normalized for phrase in current_phrases) or "current" in normalized or "latest" in normalized
    has_historical_signal = any(phrase in normalized for phrase in historical_phrases) or "historical" in normalized or "history" in normalized
    if has_current_signal and has_historical_signal:
        return "mixed_context"
    if any(phrase in normalized for phrase in current_phrases):
        return "current_state"
    if any(phrase in normalized for phrase in durable_phrases):
        return "durable_policy"
    if any(phrase in normalized for phrase in historical_phrases):
        return "historical_decision"
    return "durable_policy"


def is_action_shaped_query(query: str) -> bool:
    return ACTION_SHAPED_QUERY_RE.search(sanitize_query(query)) is not None


def tokenize(text: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    return [token for token in tokens if len(token) >= 2]


def is_absolute_path_text(path_text: str) -> bool:
    return path_text.startswith("/") or path_text.startswith("\\") or bool(WINDOWS_ABSOLUTE_RE.match(path_text))


def validate_repo_relative_path(path_text: Any) -> tuple[str | None, str | None]:
    if not isinstance(path_text, str) or not path_text.strip():
        return None, "source path is missing"
    raw = path_text.strip()
    normalized = raw.replace("\\", "/")
    if is_absolute_path_text(raw) or is_absolute_path_text(normalized):
        return None, "source path is absolute"
    if normalized != raw:
        return None, "source path must use repo-relative POSIX separators"
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None, "source path uses parent traversal or an empty path part"
    lowered = normalized.lower()
    if any(lowered == prefix[:-1] or lowered.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
        return None, "source path is in a forbidden generated or workflow class"
    if any(part.lower() in FORBIDDEN_PATH_PARTS for part in parts):
        return None, "source path is in a forbidden private/raw/generated class"
    return normalized, None


def validate_volatile_source_path(path_text: Any) -> tuple[str | None, str | None]:
    if not isinstance(path_text, str) or not path_text:
        return None, "volatile source path is missing"
    raw = path_text
    if raw.strip() != raw:
        return None, "volatile source path must be exact"
    if "\\" in raw:
        return None, "volatile source path must not use backslash aliases"
    if is_absolute_path_text(raw):
        return None, "volatile source path is absolute"
    parts = PurePosixPath(raw).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None, "volatile source path uses parent traversal or dot aliases"
    if raw not in VOLATILE_AUTHORITY_SOURCES:
        return None, "volatile source path is not allow-listed"
    return raw, None


def metadata_reject_reason(item: dict[str, Any]) -> str | None:
    if item.get("allowed_for_digest") is False:
        return "digest entry is not allowed for digest use"
    metadata = " ".join(
        str(item.get(field, ""))
        for field in ("content_class", "risk_label", "notes", "section_title")
    ).lower()
    if any(term in metadata for term in FORBIDDEN_METADATA_TERMS):
        return "digest entry metadata identifies a forbidden private/raw/downstream class"
    return None


def normalize_source_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def validated_content_hash(value: Any) -> tuple[str | None, str | None]:
    if not isinstance(value, str) or SHA256_HEX_RE.fullmatch(value) is None:
        return None, "digest content_hash is malformed"
    return value.lower(), None


def read_normalized_source_text(path: Path) -> str:
    return normalize_source_text(path.read_bytes().decode("utf-8"))


def safe_git_failure_note(action: str) -> str:
    return f"volatile overlay unavailable: git {action} failed"


def run_git(repo_root: Path, args: list[str], *, text: bool = False) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=text,
        shell=False,
        timeout=GIT_TIMEOUT_SECONDS,
    )


def observed_head_commit(repo_root: Path) -> tuple[str | None, str | None]:
    try:
        result = run_git(repo_root, ["rev-parse", "--verify", "HEAD^{commit}"], text=True)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None, safe_git_failure_note("rev-parse")
    head = result.stdout.strip().lower()
    if FULL_COMMIT_RE.fullmatch(head) is None:
        return None, "volatile overlay unavailable: git head is not a full commit sha"
    return head, None


def read_committed_blob(repo_root: Path, source_path: str) -> tuple[bytes | None, str | None]:
    normalized, reason = validate_volatile_source_path(source_path)
    if reason is not None or normalized is None:
        return None, reason or "volatile source path is invalid"
    try:
        result = run_git(repo_root, ["cat-file", "blob", f"HEAD:{normalized}"], text=False)
    except subprocess.TimeoutExpired:
        return None, safe_git_failure_note("cat-file")
    except (OSError, subprocess.CalledProcessError):
        return None, safe_git_failure_note("cat-file")
    return result.stdout, None


def read_volatile_entries(repo_root: Path) -> tuple[list[VolatileSourceEntry], list[str], str | None]:
    head, head_reason = observed_head_commit(repo_root)
    if head_reason is not None or head is None:
        return [], [head_reason or "volatile overlay unavailable: git head unavailable"], None

    entries: list[VolatileSourceEntry] = []
    notes: list[str] = []
    for source_path, metadata in VOLATILE_AUTHORITY_SOURCES.items():
        blob, blob_reason = read_committed_blob(repo_root, source_path)
        if blob_reason is not None or blob is None:
            notes.append(blob_reason or f"volatile overlay unavailable: {source_path} cannot be read")
            continue
        try:
            text = normalize_source_text(blob.decode("utf-8"))
        except UnicodeDecodeError:
            notes.append(f"volatile overlay rejected {source_path}: source is not UTF-8 text")
            continue
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        entries.append(
            VolatileSourceEntry(
                source_path=source_path,
                section_title=source_path,
                temporal_class=metadata["temporal_class"],
                authority_level=metadata["authority_level"],
                observed_head_commit=head,
                volatile_content_hash=content_hash,
                operational_freshness="unknown",
                section_authority="unknown",
                text=text,
            )
        )
    return entries, notes, head


def load_digest(repo_root: Path, digest_relative_path: str = DEFAULT_DIGEST_PATH) -> dict[str, Any]:
    digest_path = repo_root / digest_relative_path
    with digest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("digest JSON must be an object")
    if not isinstance(payload.get("sources"), list):
        raise ValueError("digest JSON must contain a sources array")
    return payload


def source_entries(repo_root: Path, digest: dict[str, Any]) -> tuple[list[SourceEntry], list[str]]:
    root = repo_root.resolve()
    entries: list[SourceEntry] = []
    safety_notes: list[str] = []

    for item in digest.get("sources", []):
        if not isinstance(item, dict):
            safety_notes.append("rejected digest entry: source entry is not an object")
            continue
        normalized, path_reason = validate_repo_relative_path(item.get("source_path"))
        if path_reason is not None or normalized is None:
            safety_notes.append(f"rejected digest entry: {path_reason}")
            continue
        metadata_reason = metadata_reject_reason(item)
        if metadata_reason is not None:
            safety_notes.append(f"rejected {normalized}: {metadata_reason}")
            continue

        full_path = (root / normalized).resolve(strict=False)
        try:
            full_path.relative_to(root)
        except ValueError:
            safety_notes.append(f"rejected {normalized}: resolved path escapes repository")
            continue
        if not full_path.is_file():
            safety_notes.append(f"rejected {normalized}: source file is missing")
            continue
        if full_path.is_symlink():
            safety_notes.append(f"rejected {normalized}: source file is a symlink")
            continue
        content_hash, hash_reason = validated_content_hash(item.get("content_hash"))
        if hash_reason is not None or content_hash is None:
            safety_notes.append(f"rejected {normalized}: {hash_reason}")
            continue
        try:
            text = read_normalized_source_text(full_path)
        except UnicodeDecodeError:
            safety_notes.append(f"rejected {normalized}: source file is not UTF-8 text")
            continue
        except OSError:
            safety_notes.append(f"rejected {normalized}: source file cannot be read")
            continue
        computed_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if computed_hash.lower() != content_hash.lower():
            safety_notes.append(f"rejected {normalized}: source content_hash mismatch")
            continue

        entries.append(
            SourceEntry(
                source_path=normalized,
                section_title=str(item.get("section_title") or "unknown"),
                content_hash=content_hash,
                risk_label=str(item.get("risk_label") or "unknown"),
                content_class=str(item.get("content_class") or "unknown"),
                full_path=full_path,
                text=text,
                note=str(item.get("notes") or ""),
            )
        )

    return entries, safety_notes


def score_entry(entry: SourceEntry, query_terms: list[str], query_phrase: str) -> Match | None:
    text = entry.text
    if not text:
        return None

    metadata = " ".join([entry.source_path, entry.section_title, entry.risk_label, entry.content_class])
    haystack = f"{metadata}\n{text}".lower()
    score = 0
    matched_terms: list[str] = []
    first_position: int | None = None

    for term in query_terms:
        if term in haystack:
            matched_terms.append(term)
            metadata_hits = metadata.lower().count(term)
            text_hits = text.lower().count(term)
            score += metadata_hits * 4 + min(text_hits, 10)
            position = text.lower().find(term)
            if position >= 0 and (first_position is None or position < first_position):
                first_position = position

    if query_phrase and query_phrase.lower() in haystack:
        score += 8
        phrase_position = text.lower().find(query_phrase.lower())
        if phrase_position >= 0:
            first_position = phrase_position

    if score <= 0:
        return None
    return Match(
        score=score,
        entry=entry,
        matched_terms=tuple(dict.fromkeys(matched_terms)),
        text=text,
        first_position=first_position or 0,
    )


def score_volatile_entry(entry: VolatileSourceEntry, query_terms: list[str], query_phrase: str) -> VolatileMatch | None:
    text = entry.text
    if not text:
        return None

    metadata = " ".join([entry.source_path, entry.section_title, entry.temporal_class, entry.authority_level])
    haystack = f"{metadata}\n{text}".lower()
    score = 0
    matched_terms: list[str] = []
    first_position: int | None = None

    for term in query_terms:
        if term in haystack:
            matched_terms.append(term)
            metadata_hits = metadata.lower().count(term)
            text_hits = text.lower().count(term)
            score += metadata_hits * 5 + min(text_hits, 12)
            position = text.lower().find(term)
            if position >= 0 and (first_position is None or position < first_position):
                first_position = position

    if query_phrase and query_phrase.lower() in haystack:
        score += 10
        phrase_position = text.lower().find(query_phrase.lower())
        if phrase_position >= 0:
            first_position = phrase_position

    if score <= 0:
        return None
    return VolatileMatch(
        score=score,
        entry=entry,
        matched_terms=tuple(dict.fromkeys(matched_terms)),
        text=text,
        first_position=first_position or 0,
    )


def current_vs_historical_note(entry: SourceEntry) -> str:
    text = " ".join([entry.source_path, entry.risk_label, entry.content_class]).lower()
    if any(term in text for term in ("release", "historical", "deprecated", "clean_clone")):
        return "historical evidence; use only as context, not current approval"
    if any(term in text for term in ("roadmap", "policy", "status", "operating_rules", "governance")):
        return "current authority or current governance context"
    return "approved digest-listed source; authority depends on current task context"


def sanitize_excerpt(text: str) -> str:
    collapsed = " ".join(text.split())
    collapsed = WINDOWS_ABSOLUTE_RE.sub("[redacted-local-path]", collapsed)
    collapsed = POSIX_ABSOLUTE_RE.sub(" [redacted-local-path]", collapsed)
    collapsed = IPV4_RE.sub("[redacted-ip]", collapsed)
    collapsed = ASSIGNMENT_SECRET_RE.sub(lambda match: f"{match.group(1)}=[redacted]", collapsed)
    if len(collapsed) > MAX_EXCERPT_LENGTH:
        return collapsed[: MAX_EXCERPT_LENGTH - 3].rstrip() + "..."
    return collapsed


def evidence_excerpt(match: Match) -> str:
    text = match.text
    if not text:
        return ""
    start = max(match.first_position - 80, 0)
    end = min(start + MAX_EXCERPT_LENGTH * 2, len(text))
    return sanitize_excerpt(text[start:end])


def volatile_evidence_excerpt(match: VolatileMatch) -> str:
    text = match.text
    if not text:
        return ""
    start = max(match.first_position - 80, 0)
    end = min(start + MAX_EXCERPT_LENGTH * 2, len(text))
    return sanitize_excerpt(text[start:end])


def match_to_result(match: Match) -> dict[str, Any]:
    entry = match.entry
    terms = ", ".join(match.matched_terms) if match.matched_terms else "query phrase"
    return {
        "source_path": entry.source_path,
        "section_title": entry.section_title or "unknown",
        "content_hash": entry.content_hash,
        "risk_label": entry.risk_label,
        "content_class": entry.content_class,
        "match_reason": f"lexical match on: {terms}",
        "evidence_excerpt": evidence_excerpt(match),
        "current_vs_historical_note": current_vs_historical_note(entry),
    }


def volatile_match_to_result(match: VolatileMatch) -> dict[str, Any]:
    entry = match.entry
    terms = ", ".join(match.matched_terms) if match.matched_terms else "query phrase"
    return {
        "source_path": entry.source_path,
        "section_title": entry.section_title,
        "temporal_class": entry.temporal_class,
        "authority_level": entry.authority_level,
        "observed_head_commit": entry.observed_head_commit,
        "volatile_content_hash": entry.volatile_content_hash,
        "operational_freshness": entry.operational_freshness,
        "section_authority": entry.section_authority,
        "match_reason": f"volatile committed-HEAD lexical match on: {terms}",
        "evidence_excerpt": volatile_evidence_excerpt(match),
        "safety_notes": [
            "volatile source read from committed HEAD",
            "operational_freshness is unknown unless a deterministic rule proves currency",
        ],
    }


def matched_source_hash(result: dict[str, Any]) -> str | None:
    value = result.get("volatile_content_hash") or result.get("content_hash")
    return value if isinstance(value, str) else None


def merge_results(
    *,
    query_class: str,
    stable_results: list[dict[str, Any]],
    volatile_results: list[dict[str, Any]],
    max_results: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    prefer_volatile = query_class in {"current_state", "mixed_context"}
    ordered = [*volatile_results, *stable_results] if prefer_volatile else [*stable_results, *volatile_results]
    merged: list[dict[str, Any]] = []
    seen: dict[str, str | None] = {}
    conflict_notes: list[str] = []
    for result in ordered:
        source_path = result["source_path"]
        current_hash = matched_source_hash(result)
        if source_path in seen:
            previous_hash = seen[source_path]
            if previous_hash and current_hash and previous_hash.lower() != current_hash.lower():
                conflict_notes.append(f"{source_path}: stable and volatile hashes differ; preferred {'volatile' if prefer_volatile else 'stable'} citation")
            continue
        seen[source_path] = current_hash
        merged.append(result)
    return merged[:max_results], conflict_notes


def retrieve(repo_root: Path, query: str, max_results: int = DEFAULT_MAX_RESULTS) -> dict[str, Any]:
    sanitized_query = sanitize_query(query)
    query_class = classify_query(sanitized_query)
    blocked_reason = query_block_reason(query)
    base_safety_notes = [
        "local-only read-only lexical retrieval",
        "only digest-listed repo-owned source files are eligible",
        "no persistent index, embeddings, vector database, external service, or downstream source is used",
    ]
    if is_action_shaped_query(sanitized_query):
        base_safety_notes.extend(
            [
                "retrieval is advisory-only",
                "no action was performed",
                "retrieval grants no approval",
            ]
        )
    if blocked_reason is not None:
        return {
            "status": "blocked",
            "query": sanitized_query,
            "query_class": query_class,
            "matched_sources": [],
            "safety_notes": base_safety_notes,
            "no_answer_reason": blocked_reason,
        }

    bounded_max_results = max(1, min(int(max_results), MAX_RESULTS_LIMIT))
    digest = load_digest(repo_root)
    entries, source_safety_notes = source_entries(repo_root, digest)
    query_terms = tokenize(sanitized_query)
    query_phrase = sanitized_query.lower()

    matches = [match for entry in entries if (match := score_entry(entry, query_terms, query_phrase)) is not None]
    matches.sort(key=lambda match: (-match.score, match.entry.source_path))
    stable_results = [match_to_result(match) for match in matches]
    volatile_results: list[dict[str, Any]] = []
    volatile_safety_notes: list[str] = []
    observed_head: str | None = None
    if query_class in {"current_state", "mixed_context"}:
        volatile_entries, volatile_safety_notes, observed_head = read_volatile_entries(repo_root)
        volatile_matches = [
            match
            for entry in volatile_entries
            if (match := score_volatile_entry(entry, query_terms, query_phrase)) is not None
        ]
        volatile_matches.sort(key=lambda match: (-match.score, match.entry.source_path))
        volatile_results = [volatile_match_to_result(match) for match in volatile_matches]

    results, conflict_notes = merge_results(
        query_class=query_class,
        stable_results=stable_results,
        volatile_results=volatile_results,
        max_results=bounded_max_results,
    )

    safety_notes = base_safety_notes + volatile_safety_notes[:10] + source_safety_notes[:10]
    if results:
        status = "found"
        if query_class in {"current_state", "mixed_context"} and (volatile_safety_notes or not volatile_results):
            status = "partial"
        payload: dict[str, Any] = {
            "status": status,
            "query": sanitized_query,
            "query_class": query_class,
            "matched_sources": results,
            "safety_notes": safety_notes,
        }
        if stable_results:
            payload["stable_digest_ref"] = DEFAULT_DIGEST_PATH
            payload["source_basis_commit"] = str(digest.get("git_sha") or "unknown")
        if observed_head is not None and volatile_results:
            payload["observed_head_commit"] = observed_head
        if conflict_notes:
            payload["conflict_notes"] = conflict_notes
        if status == "partial":
            payload["no_answer_reason"] = "volatile current authority is incomplete or unmatched; returned bounded available evidence"
        return payload

    if query_class in {"current_state", "mixed_context"} and (volatile_safety_notes or observed_head is None):
        if stable_results:
            return {
                "status": "partial",
                "query": sanitized_query,
                "query_class": query_class,
                "matched_sources": stable_results[:bounded_max_results],
                "stable_digest_ref": DEFAULT_DIGEST_PATH,
                "source_basis_commit": str(digest.get("git_sha") or "unknown"),
                "safety_notes": safety_notes,
                "no_answer_reason": "volatile current authority is unavailable; stable evidence cannot fully answer current state",
            }
        return {
            "status": "no_sufficient_evidence",
            "query": sanitized_query,
            "query_class": query_class,
            "matched_sources": [],
            "safety_notes": safety_notes,
            "no_answer_reason": "committed-HEAD volatile authority is unavailable for current-state retrieval",
        }
    return {
        "status": "no_sufficient_evidence",
        "query": sanitized_query,
        "query_class": query_class,
        "matched_sources": [],
        "safety_notes": safety_notes,
        "no_answer_reason": "no digest-listed eligible source matched the sanitized query",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run local read-only lexical retrieval over the approved corpus digest.")
    parser.add_argument("--query", required=True, help="Short search query. Must not contain private/raw transcript data.")
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS, help="Maximum number of results to return.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout. JSON is the default and only output format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = retrieve(repo_root_from_script(), args.query, args.max_results)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        payload = {
            "status": "blocked",
            "query": sanitize_query(args.query),
            "query_class": classify_query(args.query),
            "matched_sources": [],
            "safety_notes": ["local-only read-only lexical retrieval failed before source search"],
            "no_answer_reason": "retrieval failed before source search",
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
