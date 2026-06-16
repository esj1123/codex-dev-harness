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

JSON evidence must not use local absolute paths, raw transcripts, raw command
logs, raw source bundles, or unredacted tool-call payloads.

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
- eval summary/cases split
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
