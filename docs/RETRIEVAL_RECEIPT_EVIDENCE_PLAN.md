# Retrieval Receipt Evidence Plan

## Purpose

Define how Phase 7 local retriever output may be referenced by JSON evidence,
receipt summaries, and trace events without creating runtime audit automation.

This plan is documentation and schema alignment only. It does not run
retrieval, generate receipts, write audit logs, create query-matrix automation,
wire retrieval into `scripts/quality_gate.py` or CI, refresh the corpus digest,
or change `scripts/local_rag_retriever.py`.

## Evidence Boundary

Retrieval evidence is advisory context. It can support a closeout by pointing to
bounded, safe retrieval results, but it cannot grant approval, broaden a task
scope, authorize side effects, or replace owner approval.

Allowed receipt evidence is limited to:

- retrieval status labels
- short sanitized query summaries
- source counts
- repo-relative source paths
- digest content hashes or committed-HEAD volatile content hashes
- safe citation summaries
- no-answer reasons
- safety notes
- digest and commit identifiers

Retrieval evidence must not store:

- raw prompts or prompt transcripts
- raw command logs
- raw retriever stdout dumps
- full retrieved documents
- raw private or downstream corpus material
- unredacted tool-call bodies
- secrets, account values, live config, device values, or local absolute paths

## Receipt Summary Contract

Receipt summaries may include an optional `retrieval_evidence` object. The
object is not required for every receipt and should appear only when retrieval
was explicitly run, explicitly reviewed, or intentionally recorded as not run.

The safe shape is:

- `retrieval_status`: machine status such as `found`, `partial`,
  `no_sufficient_evidence`, `blocked`, `not_run`, or `not_applicable`.
- `retrieval_mode`: whether evidence is absent, manually summarized, or derived
  from standalone retriever output.
- `query_summary`: short sanitized summary, not a prompt transcript.
- `query_class`: retriever query class when known.
- `source_count`: count of cited sources, bounded by the schema.
- `citations`: bounded source references with repo-relative `source_path`,
  SHA-256 hash, citation scope, and safe summary.
- `no_answer_reason`: safe explanation for blocked or insufficient evidence.
- `safety_notes`: safe notes about excluded sources and approval boundaries.
- `digest_ref`: repo-relative digest reference when stable digest evidence is
  cited.
- `digest_source_basis_commit`: source-basis commit for stable digest evidence.
- `observed_head_commit`: committed-HEAD basis for volatile authority evidence.
- `output_capture`: whether no output, redacted summary, or bounded citations
  were captured.
- `retrieval_integration_status`: confirms the evidence remains receipt-only or
  trace-only, not quality-gate or CI integration.

The receipt must cite split retrieval evidence by identifiers, paths, hashes,
counts, and summaries. It must not copy the full retriever JSON payload when
that payload contains unnecessary excerpts or raw command output.

## Trace Event Contract

Trace events may include an optional `retrieval_evidence_ref` object when a
trace event is associated with retrieval evidence. This object is a compact
trace-level pointer, not a retrieval transcript.

Trace events should keep `related_receipt_id` as the receipt linkage. If a
trace event is associated with retrieval evidence inside a receipt summary,
`related_receipt_id` should point to `receipt_summary.receipt_id`, and
`retrieval_evidence_ref` should repeat only safe status, count, digest, hash,
and summary information needed for trace review.

## Citation Rules

Stable digest citations use:

- `citation_scope`: `stable_digest`
- `source_path`: repo-relative path from the approved corpus digest
- `hash_kind`: `digest_content_hash`
- `hash`: the digest source `content_hash`
- `digest_ref`: normally `artifacts/corpus-digest.json`
- `digest_source_basis_commit`: the digest source-basis commit when known

Volatile current-authority citations use:

- `citation_scope`: `volatile_committed_head`
- `source_path`: a volatile allow-listed authority path
- `hash_kind`: `volatile_content_hash`
- `hash`: committed-HEAD source hash
- `observed_head_commit`: the committed HEAD used for the volatile read

Receipts must preserve the difference between stable digest citations and
volatile committed-HEAD citations. A volatile citation is not a digest refresh.

## No-Answer and Blocked Behavior

`no_sufficient_evidence` and `blocked` are valid evidence outcomes. They should
be recorded as safety-preserving behavior, not as failures to force a citation.

When retrieval is not run, use `retrieval_status: not_run` and explain the
reason in a safe summary. Do not invent citations or mark retrieval as found
without reviewed output.

## Verification Boundary

Phase 7D verification should check that:

- JSON schemas parse.
- Optional retrieval fields remain optional.
- Receipt and trace references use repo-relative paths and SHA-256 hashes.
- The quality gate still validates the JSON evidence bundle.
- Full tests still pass.
- No receipt files, trace files, audit logs, query matrices, digest artifacts,
  release artifacts, index folders, corpus folders, or retrieval folders are
  generated.

## Future Work

Any future task that writes actual receipt evidence, runs a retrieval query
matrix, integrates retrieval into CI or `scripts/quality_gate.py`, refreshes the
digest, creates persistent indexes, or changes retriever runtime behavior
requires separate approval with exact files, commands, artifacts, and safety
boundaries.
