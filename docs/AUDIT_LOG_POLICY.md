# Audit Log Policy

## Purpose

Define documentation-level audit log expectations for codex-dev-harness.

The repository includes `audits/audit-log.schema.json` as an optional future
evidence schema. The schema defines a safe record shape only. It does not create
real audit session logs, capture tool calls, store prompts, add logging
automation, create an audit database, or make audit logging required for the
current local-first baseline.

## Current Related Evidence

The repository already records audit-adjacent evidence in:

- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- release records under `docs/`
- clean clone validation records
- downstream adoption and feedback records
- decision and closeout records under `docs/`

These are related evidence foundations. They are not real audit session logs.

## Audit Event Fields

The optional schema defines these future fields:

- `schema_version`
- `task_id`
- `timestamp_utc`
- `actor`
- `repo`
- `repo_sha`
- `model_id`
- `prompt_template_id`
- `prompt_hash`
- `approved_corpus_digest`
- `side_effect_class`
- `approval_id`
- `files_changed`
- `commands_run`
- `verification_result`
- `outputs_hash`
- `safety_checks`
- `redaction_status`
- `notes`

These fields are optional future evidence fields. The schema is not wired into
`scripts/quality_gate.py`, CI, release tooling, RAG tooling, or model
observability.

## RAG And Model Change References

Future audit evidence may reference approved-corpus and model-change controls
without storing raw content:

- `model_id` should identify the model used or compared.
- `prompt_template_id` should identify a reusable prompt template when used.
- `prompt_hash` should be a hash only when prompt material is separately
  approved for hashing.
- `approved_corpus_digest` should identify the approved corpus basis without
  embedding source text.
- `side_effect_class` should identify the allowed action class without
  broadening approval.

Approved-corpus planning is documented in
`docs/APPROVED_CORPUS_RAG_PLAN.md`. Model and prompt change planning is
documented in `docs/MODEL_CHANGE_POLICY.md`.

These references do not approve retrieval tooling, indexing, prompt capture,
model output capture, external service calls, model observability tooling, or
automatic audit generation.

## Content Rules

Audit records must not contain:

- secrets, keys, tokens, credentials, or account material
- private raw input
- raw prompt text by default
- raw source bundles
- sensitive requirement text
- unredacted tool-call request or response bodies unless separately approved
  and redacted
- equipment IPs, ports, tags, or live parameter values
- live configuration
- private downstream implementation details

Use hashes, summaries, identifiers, and evidence paths instead of copying raw
content. Prompt hashes, approved corpus digests, output hashes, and command
summaries are preferred over raw prompts, private input, raw source, command
output, or tool-call bodies.

## When To Record Audit Evidence

Record audit evidence for:

- approval-gated changes
- release decisions
- tag or publication decisions
- optional pack integration decisions
- profile or example decisions
- eval harness decisions
- local package or release artifact decisions
- downstream feedback promotion decisions
- any task with NOT RUN verification that affects durable repo state

## Approval References

`approval_id` should reference an approval record governed by
`docs/HUMAN_APPROVALS.md`. Approval identifiers must not embed secrets, private
input, equipment details, live values, or raw source.

## Generation Approval Boundary

The schema may be used as a future manual evidence contract, but actual audit
log generation requires separate explicit owner approval.

Before creating real audit entries or tooling, decide:

- whether audit records are Markdown, JSON, or both
- where audit entries are stored
- whether entries are generated manually or by tooling
- whether schema validation belongs in `quality_gate.py`
- how prompts, private inputs, raw source, command output, and tool-call bodies
  are redacted or excluded

No current task may infer approval to create real audit logs from the existence
of the schema or this policy.

## Non-Goals

This policy and schema do not create real audit session logs, a validator,
database, workflow, release artifact, eval harness, RAG tooling, model
observability tooling, application code, C# project asset, PLC/device code, or
live-write behavior.
