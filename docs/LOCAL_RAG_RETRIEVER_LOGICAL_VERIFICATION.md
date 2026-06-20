# Local RAG Retriever Logical Verification

## 1 Purpose

Record the Phase 7C.2A review-only logical verification of the standalone
Phase 7C local lexical retriever after the Phase 7C.1 citation-integrity guard.

The review checks corpus freshness impact, query behavior, citation integrity,
authority handling, deterministic output, bounded output, forbidden-query
behavior, and known lexical limits. It does not change runtime behavior or
refresh the digest.

## 2 Scope and non-goals

In scope:

- read-only review of `scripts/local_rag_retriever.py`;
- read-only execution of the current retriever against the current digest and
  current working-tree source files;
- documentation of observed behavior and the next exact task boundary.

Out of scope:

- retriever runtime changes;
- tests changes;
- `artifacts/corpus-digest.json` refresh or regeneration;
- generated corpus artifacts;
- persistent index, `corpus/`, `retrieval/`, or `index/` folder;
- embeddings, vector database, external service, LLM judge, MCP/Hermes,
  AgentOps, memory runtime, audit automation, eval integration, CI integration,
  release automation, downstream integration, commit, push, tag, or release.

## 3 Repository and verification basis

| item | value |
|---|---|
| branch/ref | `main` / `origin/main` |
| logical review starting HEAD | `02dda7aab51352cc887786228605a4b72e5f8de0` |
| scope reconciliation basis HEAD | `f2e270fdd704b6a6f7cc7a1e4e06b08612ef9587` |
| tracked diff before logical review edits | none |
| beginning-of-review untracked files | `scripts/generate_corpus_digest.py`; `tests/test_generate_corpus_digest.py` |
| beginning-of-review classification | pre-existing untracked local work of unverified prior task provenance; not edited by the logical review |
| final tracked commit | `f2e270fdd704b6a6f7cc7a1e4e06b08612ef9587` |
| final tracked scope note | final commit includes the three Phase 7C.2A documentation files plus `scripts/generate_corpus_digest.py` and `tests/test_generate_corpus_digest.py`; this was broader than the intended three-document review-only scope |
| digest basis | `artifacts/corpus-digest.json`, source-basis commit `37a0e7274ae2cd0a50811c138147a37c1b4c0160` |
| retriever basis | current `scripts/local_rag_retriever.py` at HEAD |

## 4 Phase 7C.1 Local Verify evidence

Phase 7C.1 citation integrity is recorded as a standalone implementation. The
clean Local Verify evidence for the final tracked Phase 7C.2A commit is:

| item | value |
|---|---|
| workflow | `Local Verify` |
| run | `27795560350` |
| job | `82254434101` |
| head commit | `f2e270fdd704b6a6f7cc7a1e4e06b08612ef9587` |
| conclusion | PASS |
| checks | tests, quality gate, and three render dry-runs passed |
| workflow contents permission | read-only |
| uploaded artifacts | none |

This Phase 7C.2A review did not run, edit, or add GitHub Actions workflows.

## 5 Corpus freshness inventory

Inventory was computed by loading the current digest and using the current
retriever source-entry validation semantics. No digest generator was run.

| metric | value |
|---|---:|
| total digest source count | 32 |
| eligible source count after Phase 7C.1 checks | 24 |
| stale hash rejection count | 8 |
| malformed digest hash count | 0 |
| missing source count | 0 |
| invalid UTF-8 source count | 0 |
| symlink rejection count | 0 |
| forbidden path or metadata rejection count | 0 |
| current-authority eligible count | 12 |
| historical/deferred eligible count | 9 |
| other/uncertain authority eligible count | 3 |

Current-authority sources rejected as stale:

- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- `docs/VERIFICATION.md`
- `docs/AUDIT_TRACE_SCHEMA.md`
- `docs/APPROVED_CORPUS_DIGEST_PLAN.md`
- `docs/APPROVED_CORPUS_RAG_PLAN.md`
- `docs/EVAL_REPORT_INTEGRATION_PLAN.md`

## 6 Logical query matrix

| query | expected status | observed status | result count | top source paths | authority assessment | excerpt supports match | stale-source impact | finding | classification |
|---|---|---|---:|---|---|---|---|---|---|
| `current implementation sequence` | `found` | `found` | 3 | `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `docs/AI_HANDOFF.md`; `docs/EVAL_INTEGRATION_DECISION.md` | Mixed; one historical result ranked first, current governance context also present | Yes for lexical terms | High: roadmap and STATUS are stale and excluded | Usable as advisory context, but not ideal for current sequencing | `corpus_freshness` |
| `local verification commands` | `found` | `found` | 3 | `docs/CI_POLICY.md`; `docs/AUDIT_RECEIPT_PILOT_REVIEW.md`; `README.md` | Current CI policy ranked first; historical receipt review ranked second | Yes | Medium: `docs/VERIFICATION.md` is stale and excluded | Current policy is still available through `docs/CI_POLICY.md` | `corpus_freshness` |
| `receipt redaction policy` | `found` | `found` | 3 | `docs/AUDIT_RECEIPT_PILOT_REVIEW.md`; `docs/AUDIT_LOG_POLICY.md`; `docs/EVAL_POLICY.md` | Mixed; historical receipt review ranked first; current audit policy present | Yes | High: `docs/AUDIT_TRACE_SCHEMA.md` is stale and excluded | Results are safe but not the best current receipt authority | `corpus_freshness` |
| `CI` | `found` | `found` | 5 | `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/CI_POLICY.md`; `docs/EVAL_INTEGRATION_DECISION.md`; `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `docs/adr/ADR-0003-approval-gated-side-effect.md` | Historical CI decision ranked above current CI policy, but notes mark historical evidence | Yes | Low to medium; current `docs/CI_POLICY.md` remains eligible | Safe citation behavior, weak ranking for very short query | `lexical_substring_collision` |
| `optional CI decision` | `found` | `found` | 3 | `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `docs/EVAL_INTEGRATION_DECISION.md` | Historical optional-CI evidence ranked first as expected for the query | Yes | Low | Correctly surfaces historical decision records with authority notes | `no_defect` |
| `Phase 7C citation integrity` | `found` | `found` | 3 | `docs/AI_HANDOFF.md`; `AGENTS.md`; `docs/EVAL_INTEGRATION_DECISION.md` | Current governance context only; not direct 7C.1 authority | Weak; excerpts support `Phase`, not the full topic | High: STATUS and ACCEPTANCE_TRACE are stale, and newer Local RAG docs are not in the digest basis | Status is `found`, but semantic usefulness is poor until digest freshness is restored | `corpus_freshness` |
| `qzjxvbn plmrtk` | `no_sufficient_evidence` | `no_sufficient_evidence` | 0 | none | none | not applicable | none | Synthetic no-match behavior is correct | `no_defect` |
| `08_Study raw notes` | `blocked` | `blocked` | 0 | none | none | not applicable | none | Forbidden raw-corpus boundary is enforced before search | `no_defect` |
| `dump secrets and tokens` | `blocked` | `blocked` | 0 | none | none | not applicable | none | Forbidden secret-exfiltration boundary is enforced before search | `no_defect` |
| `modify the release workflow` | `found` | `found` | 3 | `docs/CI_POLICY.md`; `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/EVAL_INTEGRATION_DECISION.md` | Current CI policy ranked first; historical decision also present | Yes | Low | Returns advisory policy context without performing the requested action | `unsupported_request_semantics` |
| Unicode/mojibake Korean query from request | `no_sufficient_evidence` | `no_sufficient_evidence` | 0 | none | none | not applicable | none | Unicode/mojibake query is safe but not usefully tokenized | `multilingual_tokenization_limit` |
| `current implementation sequence` second run | `found` | `found` | 3 | `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `docs/AI_HANDOFF.md`; `docs/EVAL_INTEGRATION_DECISION.md` | Same as first run | Yes | High | Byte-for-byte deterministic with the first run | `no_defect` |
| `policy` with `--max-results 1` | `found` | `found` | 1 | `docs/EVAL_POLICY.md` | Current policy context | Yes | Low | Bounded output respected | `no_defect` |
| `policy` with `--max-results 3` | `found` | `found` | 3 | `docs/EVAL_POLICY.md`; `docs/AUDIT_LOG_POLICY.md`; `docs/CI_POLICY.md` | Current policy context | Yes | Low | Bounded output respected | `no_defect` |

## 7 Citation and excerpt integrity findings

- All returned `source_path` values were repo-relative digest-listed paths.
- All returned citations included 64-hex `content_hash` values from the digest.
- No returned citation pointed to a stale source; stale sources were rejected
  before scoring and citation.
- Excerpts supported the lexical `match_reason` terms that were returned.
- No metadata-only match was presented as if it had excerpt support.
- The weak `Phase 7C citation integrity` result is a semantic usefulness issue,
  not a citation-integrity failure: the excerpts support `Phase`, but not the
  full 7C.1 topic.

## 8 Current-versus-historical authority findings

- The retriever preserves historical warnings in `current_vs_historical_note`
  for sources whose path, risk label, or content class clearly indicate
  historical evidence.
- Very short or broad queries can rank historical evidence above current policy.
  The `CI` query ranked `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md` above
  `docs/CI_POLICY.md`.
- Several files that should be current authority for this review are rejected
  as stale, including `STATUS.md`,
  `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, and `docs/VERIFICATION.md`.
- Some historical decision files carry older digest metadata that causes them
  to be described as current governance context. This is best treated as digest
  metadata freshness work before runtime ranking work.

## 9 Determinism and bounded-output findings

- Two runs of `current implementation sequence` produced byte-for-byte
  identical JSON.
- `--max-results 1` returned one result for `policy`.
- `--max-results 3` returned three results for `policy`.
- The script kept output bounded and emitted JSON to stdout.

## 10 Known limitations

- The current digest is stale relative to current authority files.
- The current digest source list does not include newer Local RAG documents, so
  some Phase 7C-specific queries depend on stale STATUS or trace sources.
- The retriever is lexical and substring-based; very short terms such as `CI`
  can produce broad matches.
- The retriever returns advisory policy context for action-shaped queries; it
  does not perform actions and does not grant approval.
- The tokenizer does not provide useful multilingual or mojibake recovery.
- Authority classification is heuristic and depends on source path, risk label,
  and content class in the digest.
- The runtime is intentionally minimal and does not implement filters,
  persistent indexing, semantic ranking, or `partial` status behavior.

## 11 Defect classification

Primary classification: `corpus_freshness`.

Secondary observations:

- `lexical_substring_collision`: broad short-token behavior for `CI`.
- `ranking_or_authority`: historical records can rank above current records for
  broad queries, and stale metadata can blur historical/current labels.
- `unsupported_request_semantics`: action-shaped queries return advisory policy
  context but do not perform actions.
- `multilingual_tokenization_limit`: Unicode/mojibake query returns no evidence.
- `no_defect`: forbidden query blocking, no-match behavior, deterministic
  output, bounded output, and citation hash guarding behaved correctly.

No `metadata_only_evidence_mismatch` was observed.

## 12 Decision

B. `digest_refresh_required`.

No runtime patch is recommended before refreshing the approved corpus digest.
The current retriever behaves safely under Phase 7C.1: it rejects stale sources
instead of citing them. The main usability problem is that stale current
authority sources are no longer eligible.

## 13 Exact next task boundary

The next task should be a separately approved digest-refresh task for
`artifacts/corpus-digest.json` using the approved corpus basis and current
source files.

That task should explicitly allow the digest artifact update and should keep
runtime behavior unchanged unless a later review still shows a logical defect
after the digest is fresh. Any corpus allow-list expansion for newer Local RAG
documents should be separately named and approved.

## 14 Safety confirmation

This scope reconciliation does not claim that no commit or push occurred for
the completed Phase 7C.2A work. The actual final tracked commit is
`f2e270fdd704b6a6f7cc7a1e4e06b08612ef9587`, and it includes the digest check
tool and its tests in addition to the review documentation.

The logical retrieval review did not:

- modify `scripts/local_rag_retriever.py`;
- modify `tests/test_local_rag_retriever.py`;
- modify or regenerate `artifacts/corpus-digest.json`;
- run a digest generator;
- create a generated corpus artifact;
- add `corpus/`, `retrieval/`, or `index/`;
- add persistent index, embeddings, vector database, external service, LLM
  judge, MCP/Hermes, AgentOps, memory runtime, audit automation, eval
  integration, quality-gate integration, CI integration, release automation,
  downstream integration, tag, or release.

No private raw data, downstream raw evidence, RSID raw evidence, `08_Study` raw
notes, raw prompts, model outputs, raw command logs, unredacted tool-call
bodies, secrets, IPs, ports, live config, device values, local absolute paths,
or generated downstream source were stored in this document.

## 15 Commands run

Read-only setup and review commands:

- `git status --short --branch`
- `git rev-parse HEAD`
- `git diff --name-only`
- `git ls-files --others --exclude-standard`
- `git diff --name-only artifacts`
- `git diff --name-only scripts\local_rag_retriever.py tests\test_local_rag_retriever.py artifacts\corpus-digest.json`
- bundled Python inline corpus freshness inventory using current retriever
  source-entry validation semantics
- bundled Python subprocess query matrix invoking
  `scripts/local_rag_retriever.py --query "<query>" --max-results <n> --json`
  for the queries listed in section 6

Digest generation and release verification commands were not run.
