# JSON Evidence Policy

## 1. Purpose

Define the Phase 4B JSON Evidence Core / Evidence Serialization Policy for
`codex-dev-harness`.

This policy turns the manual audit / trace / receipt field contract into a
small machine-readable foundation. It defines the repository-owned JSON schema
bundle and the serialization rules that future evidence may use after separate
approval.

This is a foundation only. It does not write audit entries, create real audit
logs, validate live task logs, generate release artifacts, integrate eval
reports, implement RAG, implement MCP/Hermes behavior, or edit downstream
repositories.

Boundary phrases for the quality gate: no audit automation; no real audit logs.

## 2. Required Bundle

The JSON evidence core bundle is:

- `docs/JSON_EVIDENCE_POLICY.md`
- `audits/receipt-summary.schema.json`
- `audits/trace-event.schema.json`

When `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` or `STATUS.md` names
`Phase 4B` or `JSON Evidence Core`, the full bundle is required.

If none of the bundle files exists and no Phase 4B or JSON Evidence Core marker
exists in the roadmap or status documents, the JSON evidence gate may treat the
repository as not applicable. This keeps small synthetic quality-gate fixtures
from needing the JSON evidence bundle.

If any bundle file exists, all bundle files must exist. Partial bundles fail.

## 3. Serialization Rules

JSON evidence must use:

- repo-relative paths
- stable identifiers
- status labels
- safe summaries
- hashes
- counts
- commit identifiers
- approved document references

Release-bundle checksums over repository-owned UTF-8 text artifacts must
canonicalize CRLF and CR to LF before SHA-256 hashing. This changes only
line-ending treatment; it does not authorize JSON reserialization, compact
serialization, schema changes, or regeneration of other evidence artifacts.

JSON evidence must not use local absolute paths, raw transcripts, raw command
logs, raw source bundles, or unredacted tool-call payloads.

`receipt_id` is the stable identifier for one receipt summary. It is distinct
from `task_id`, which identifies the broader task or phase. When a trace event
is associated with a receipt summary, `related_receipt_id` should point to
`receipt_summary.receipt_id`.

Phase 5B eval receipt alignment adds optional `eval_evidence` references to
receipt summaries. The eval summary JSON is safe summary evidence. The cases
JSONL is detailed evidence and must be referenced by repo-relative `cases_ref`
and `cases_sha256` rather than copied into a receipt. Receipts that cite split
eval evidence may also record the summary report path and SHA-256.

These eval references do not run evals, generate reports by default, wire evals
into `scripts/quality_gate.py`, add CI eval behavior, or create release-blocking
semantics.

Phase 7B local RAG implementation-contract evidence may describe future
retrieval citations using repo-relative source paths, digest content hashes,
safe summaries, and no-answer reasons. It must not store raw private corpus
content, full retrieved documents, local absolute paths, secrets, live values,
prompt transcripts, model outputs, or tool-call bodies.

These retrieval evidence references do not implement retrieval, create indexes,
generate corpus artifacts, add embeddings or vector storage, call external
services, integrate MCP/Hermes, or authorize downstream work.

Phase 7D retrieval receipt evidence alignment adds optional
`retrieval_evidence` references to receipt summaries and optional
`retrieval_evidence_ref` pointers to trace events. These fields may record
retrieval status, sanitized query summaries, bounded source counts,
repo-relative source paths, digest or volatile content hashes, safe citation
summaries, no-answer reasons, safety notes, and commit identifiers.

Stable digest citations must distinguish `stable_digest` references from
`volatile_committed_head` references. Stable citations use digest
`content_hash` values and the digest source-basis commit when known. Volatile
current-authority citations use committed-HEAD content hashes and the observed
HEAD commit. A volatile citation is not a digest refresh.

These Phase 7D references do not generate receipt files, write audit logs,
capture raw retriever output, run a query matrix, wire retrieval into
`scripts/quality_gate.py` or CI, regenerate `artifacts/corpus-digest.json`,
change retriever runtime behavior, create indexes, add embeddings or vector
storage, call external services, integrate MCP/Hermes, or authorize downstream
work.

Phase 9Q Hermes git-push preflight schema alignment adds optional
`hermes_git_push_preflight_evidence` references to receipt summaries and
optional `hermes_git_push_preflight_evidence_ref` pointers to trace events.
These fields may record selected fail-closed preflight fields such as
`preflight_evidence_status`, `decision`, `side_effect_requested`, safe reason
codes, repo-relative evidence references, booleans that confirm no git push
would run and no actions were performed, reviewed commit identifiers, and
reviewed Local Verify run/job identifiers.

Trace events should continue to use `related_receipt_id` to point to
`receipt_summary.receipt_id`; `hermes_git_push_preflight_evidence_ref` is a
compact pointer to the receipt evidence key, not a transcript or stdout dump.

These Phase 9Q references do not implement a writer, create receipt files,
write trace files, write audit logs, persist preflight output, execute real
`git push`, stage or commit files as evidence, wire Hermes preflight into
`scripts/quality_gate.py` or CI, execute MCP tools, regenerate artifacts or
digests, call external services, integrate AgentOps or memory, release
automation, or authorize downstream work.

Schema files must be plain JSON and parse with the Python standard library.
The quality gate checks schema presence and core shape only. It is not a
general-purpose JSON Schema validator for generated evidence records.

## 4. Status Labels

Allowed evidence status labels are:

- `PASS`
- `PASS WITH NOTES`
- `BLOCKED`
- `NOT RUN`
- `ENVIRONMENT BLOCKED`
- `FAIL`

Final closeouts should use the same honesty rules as
`docs/AUDIT_TRACE_SCHEMA.md`: do not imply success for a command, generated
artifact, release action, CI run, eval run, downstream action, or live target
action that did not run.

## 5. Redaction Rules

JSON evidence must prefer summaries and identifiers over content capture.

Forbidden content includes:

- no raw prompts
- no private data
- no raw command logs
- no unredacted tool-call bodies
- no secrets, credentials, keys, or tokens
- no account values
- no IPs, ports, live config, device values, broker values, or equipment values
- no local absolute paths
- no generated downstream source
- no external or private corpus material

If sensitive material is relevant to a future approved task, evidence must use
a safe summary, hash, approved identifier, or redacted status instead of copying
the material.

## 6. Non-Goals

Phase 4B does not implement:

- audit automation
- real audit logs
- JSONL audit writing
- generated receipt files
- generated trace files
- default eval summary/cases generation
- eval quality-gate integration
- RAG, embeddings, vector database, or retrieval
- MCP runtime
- Hermes sidecar
- AgentOps runtime
- memory runtime
- release automation
- release artifact generation or regeneration
- downstream repository integration

## 7. Gate Contract

`scripts/gates/json_evidence_gate.py` checks:

- whether the repository is not applicable, marker-bearing, partial, or bundled
- policy file presence and required safety language
- schema JSON parsing
- schema core shape
- required schema fields and status enums
- absence of local absolute path or IP-like values inside the JSON evidence
  bundle

The gate must not create files, write logs, generate artifacts, call external
services, run evals, scan downstream repositories, or validate runtime audit
records.

## 8. Verification

Required focused checks for this foundation are:

- `python -m json.tool audits/receipt-summary.schema.json`
- `python -m json.tool audits/trace-event.schema.json`
- `python -m pytest tests/test_json_evidence_gate.py`
- `python scripts/quality_gate.py`
- `python -m pytest tests`

If a command cannot run in the local environment, record `ENVIRONMENT BLOCKED`
or `NOT RUN` honestly.
