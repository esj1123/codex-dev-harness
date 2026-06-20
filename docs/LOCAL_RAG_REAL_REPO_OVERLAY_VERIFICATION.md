# Local RAG Real-Repository Overlay Verification

## 1. Purpose

Record Phase 7C.3E real-repository verification of the committed-HEAD
volatile authority overlay implemented in `scripts/local_rag_retriever.py`.

This review checks whether the overlay resolves the current-state authority
problem identified in Phase 7C.2B and Phase 7C.3B, and whether a separate
stable corpus re-baseline is needed before any later ranking correction.

## 2. Scope

In scope:

- read-only real-repository digest check;
- read-only representative retriever queries;
- review of stable digest results versus volatile overlay results;
- Phase 6H stable corpus re-baseline decision;
- documentation-only evidence capture.

Out of scope:

- no retriever runtime change;
- no test change;
- no digest refresh or digest write;
- no `artifacts/corpus-digest.json` regeneration;
- no `STATUS.md` or `ACCEPTANCE_TRACE.md` edit;
- no quality-gate or CI integration;
- no release automation;
- no audit automation or receipt generation;
- no persistent index, `corpus/`, `retrieval/`, or `index/` directory;
- no embeddings, vector database, external service, MCP/Hermes, AgentOps, or
  memory runtime;
- no downstream access or downstream edit;
- no private/raw corpus ingestion.

## 3. Repository basis

| item | value |
|---|---|
| branch | `main` |
| reviewed HEAD | `366497c83b8bf776e9836c3203ca3e97eae8bb5d` |
| HEAD message | `Implement Phase 7C.3D volatile authority overlay` |
| branch relation before review | `main...origin/main` |
| stable digest | `artifacts/corpus-digest.json` |
| stable digest source count | `32` |
| stable digest source basis | `ce9e736ff8645aa592eadc1ad5b3bb9021a23c6d` |
| previous clean Local Verify | run `27875241381`, job `82493540131` |

The previous clean Local Verify applies to the Phase 7C.3D implementation
commit before this review document existed. Clean remote verification for this
document is not run in this task.

## 4. Digest check

Read-only digest check result:

| metric | value |
|---|---|
| mode | `check` |
| source_count | `32` |
| valid | `32` |
| stale | `0` |
| missing | `0` |
| malformed | `0` |
| invalid_utf8 | `0` |
| unsafe | `0` |
| refresh_required | `false` |
| RAG authorization status | `not_authorized` |
| release artifact status | `not_release_artifact_without_separate_approval` |

No digest write was run.

## 5. Overlay metadata spot check

Query: `current implementation sequence`

With `--max-results 2`, the first two citations were:

| source_path | temporal_class | authority_level | observed_head_commit | hash field |
|---|---|---|---|---|
| `STATUS.md` | `volatile_current_authority` | `current_operational_state` | `366497c83b8bf776e9836c3203ca3e97eae8bb5d` | `volatile_content_hash` |
| `ACCEPTANCE_TRACE.md` | `volatile_current_authority` | `current_operational_state` | `366497c83b8bf776e9836c3203ca3e97eae8bb5d` | `volatile_content_hash` |

This confirms the real-repository current-state path is using committed
`HEAD` overlay metadata instead of stable digest citations for the same files.

## 6. Query matrix

Representative read-only query results:

| query | status | query_class | observed HEAD | top source paths | assessment |
|---|---|---|---|---|---|
| `current implementation sequence` | `found` | `current_state` | yes | `STATUS.md`; `ACCEPTANCE_TRACE.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`; `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md` | Overlay correctly promotes volatile current authority and keeps stable policy context. |
| `next recommended task` | `found` | `current_state` | yes | `STATUS.md`; `ACCEPTANCE_TRACE.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/AUDIT_TRACE_SCHEMA.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` | Overlay works technically; semantic next-step currency still depends on committed status content. |
| `current approved corpus digest status` | `found` | `current_state` | yes | `STATUS.md`; `ACCEPTANCE_TRACE.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/APPROVED_CORPUS_RAG_PLAN.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` | Mixed live-state plus stable digest context is available. |
| `Phase 6G approved corpus digest refresh` | `found` | `mixed_context` | yes | `STATUS.md`; `ACCEPTANCE_TRACE.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/APPROVED_CORPUS_RAG_PLAN.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` | Mixed-context overlay behavior is consistent with the contract. |
| `local verification commands` | `found` | `durable_policy` | no | `docs/VERIFICATION.md`; `docs/AUDIT_TRACE_SCHEMA.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`; `docs/CI_POLICY.md`; `ACCEPTANCE_TRACE.md` | Durable policy path stays stable-digest-first, but stable digest still includes a volatile trace file. |
| `receipt redaction policy` | `found` | `durable_policy` | no | `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `ACCEPTANCE_TRACE.md`; `STATUS.md`; `docs/AUDIT_RECEIPT_PILOT_REVIEW.md` | Ranking remains noisy and stable digest still contains volatile files. |
| `CI` | `found` | `durable_policy` | no | `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/CI_POLICY.md`; `docs/EVAL_INTEGRATION_DECISION.md`; `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `docs/adr/ADR-0003-approval-gated-side-effect.md` | Short all-caps query ranking remains a later Phase 7C.4 issue. |
| `optional CI decision` | `found` | `historical_decision` | no | `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `ACCEPTANCE_TRACE.md`; `STATUS.md`; `docs/EVAL_INTEGRATION_DECISION.md` | Historical path remains stable-digest-first; volatile files still appear as stable citations. |
| `Phase 7C citation integrity` | `found` | `durable_policy` | no | `STATUS.md`; `ACCEPTANCE_TRACE.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`; `docs/APPROVED_CORPUS_RAG_PLAN.md` | Stable digest still makes volatile files eligible for durable-policy answers. |
| `qzjxvbn plmrtk` | `no_sufficient_evidence` | `durable_policy` | no | none | No-answer behavior is preserved. |
| `08_Study raw notes` | `blocked` | `durable_policy` | no | none | Forbidden raw/private corpus guard is preserved. |
| `modify the release workflow` | `found` | `durable_policy` | no | `ACCEPTANCE_TRACE.md`; `STATUS.md`; `docs/AUDIT_TRACE_SCHEMA.md`; `docs/CI_POLICY.md`; `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md` | Action-shaped query remains advisory-only, but stable digest volatile-file membership still affects ranking. |

## 7. Findings

1. The volatile overlay is functioning for real current-state and
   mixed-context queries. It returns committed-HEAD citations for `STATUS.md`
   and `ACCEPTANCE_TRACE.md` with `observed_head_commit`,
   `volatile_content_hash`, `temporal_class`, and `authority_level`.

2. No-answer and blocked behavior remain intact. The nonsensical query returns
   `no_sufficient_evidence`, and the raw `08_Study` query is blocked.

3. Durable and historical queries correctly avoid the overlay, but the current
   stable digest still includes `STATUS.md` and `ACCEPTANCE_TRACE.md`. Those
   volatile files can therefore still appear as stable citations for durable
   policy and historical-decision answers.

4. The short-token `CI` ranking issue remains unresolved. This is not caused
   by overlay availability and should stay deferred to a later Phase 7C.4
   ranking/token-boundary task.

5. The overlay proves source-basis identity for committed HEAD. It does not
   independently prove semantic freshness of the content, so
   `operational_freshness` may remain `unknown` unless a later deterministic
   rule is approved.

## 8. Decision

Decision: `phase_6h_stable_corpus_rebaseline_required_before_phase_7c4`.

Rationale:

- Phase 7C.3D resolved the immediate current-authority access problem for
  current-state and mixed-context queries.
- The stable digest still includes volatile current-authority files,
  specifically `STATUS.md` and `ACCEPTANCE_TRACE.md`.
- Because durable and historical query paths intentionally prefer stable
  digest citations, volatile files still influence non-current answers through
  the stable corpus.
- Ranking correction before stable corpus re-baseline would mix two concerns:
  lexical ranking defects and corpus-authority membership defects.

Phase 6H should be a separately approved stable corpus re-baseline task with
an exact allow-list, exact write permission for `artifacts/corpus-digest.json`,
and explicit verification. This review does not authorize or run that write.

## 9. Proposed Phase 6H decision points

A future Phase 6H task should decide, explicitly:

- whether to remove `STATUS.md` from the stable digest and rely on the volatile
  overlay for current operational state;
- whether to remove `ACCEPTANCE_TRACE.md` from the stable digest and rely on
  the volatile overlay for current acceptance state;
- whether to add stable Local RAG policy documents to the digest, such as
  `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`,
  `docs/LOCAL_RAG_POLICY_APPLICATION_REVIEW.md`, and
  `docs/LOCAL_RAG_VOLATILE_OVERLAY_CONTRACT.md`;
- whether this review document should remain review evidence only or become
  stable digest input in a later approval.

No source membership change is approved by this document.

## 10. Safety checks

This review did not:

- modify `artifacts/corpus-digest.json`;
- run digest write mode;
- change retriever runtime or tests;
- add quality-gate or CI integration;
- create a persistent index or retrieval folder;
- regenerate release artifacts;
- access private/raw corpus material;
- write audit logs, receipts, or trace artifacts;
- push, tag, publish, upload, or release anything.

## 11. Next step

Immediate next step:

Commit and push this single review-evidence document, then run clean Local
Verify for the document-containing commit.

Next separately approved implementation task:

Phase 6H Stable Corpus Re-baseline, with exact source membership, exact
artifact write authorization, digest validation, full local verification, and
post-push Local Verify review.
