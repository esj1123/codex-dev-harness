# Approved Corpus RAG Plan

## Purpose

Plan a future local-only approved-corpus retrieval approach for
codex-dev-harness.

This document is planning-only. It does not create retrieval code, an index,
embeddings, vector storage, external-service calls, model observability,
prompt/output capture, CI workflows, application code, device code, or
live-write behavior.

Current sequencing note: this plan is roadmap input, not authorization to index
or retrieve. `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` makes approved corpus
digest the fourth implementation target and local RAG the fifth implementation
target, after read-only CI, audit / trace / receipt schema, and eval / report
integration.

## Intended Use

An approved-corpus local RAG layer, if separately approved later, would help an
AI/Codex worker retrieve stable repository policy and evidence before proposing
changes. Its purpose would be to reduce stale-context mistakes and improve
evidence traceability, not to make autonomous decisions or bypass human
approval.

Any future retrieval result must be treated as supporting context. It must not
grant approval, expand write scope, authorize side effects, or override the
current task contract.

## Approved Corpus Candidates

Initial corpus candidates are limited to repository-owned governance and
evidence files:

- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `docs/ARCHITECTURE.md`
- `docs/SAFETY_POLICY.md`
- `docs/VERIFICATION.md`
- `docs/PROFILE_MATRIX.md`
- ADRs under `docs/adr/`
- release records under `docs/`
- clean clone validation records under `docs/`
- local target experiment records under `docs/`

These are candidates only. Inclusion in this plan does not create an index and
does not approve indexing. A future implementation task must name the exact
files or glob patterns to include.

## Required Metadata

Each future corpus entry should record:

- `source_path`
- `git_sha`
- `section_title`
- `verified_at`
- `risk_label`
- `allowed_for_release`

Metadata should support traceability without copying private input, raw source,
prompt text, model output, tool-call bodies, or sensitive values.

## Risk Labels

Future corpus entries should use conservative risk labels, for example:

- `baseline_policy`
- `release_evidence`
- `approval_boundary`
- `safety_boundary`
- `historical_record`
- `deprecated_or_historical`

The `risk_label` should help retrieval consumers avoid treating old release
records, historical baselines, or deferred plans as current authorization.

## Forbidden Corpus

A future approved corpus must not include:

- raw private source
- live configuration
- secrets, credentials, keys, tokens, or account material
- device details
- equipment IPs, ports, tags, or live parameter values
- downstream generated target output
- prompt/session transcripts
- model outputs
- unredacted tool-call request or response bodies
- private downstream implementation details

If a file mixes safe policy text with forbidden material, exclude the file until
it is redacted and separately approved.

## Approval Checkpoint Before Corpus Expansion

Corpus expansion requires separate owner approval before any implementation or
index generation. The approval should identify:

- exact files, directories, or patterns to add
- excluded files, directories, and patterns
- expected metadata fields
- redaction requirements
- whether generated corpus artifacts are allowed
- whether eval evidence is required before adoption
- closeout evidence and safety checks

Broad approval to improve retrieval, search, context, model behavior, or AI
quality is not enough to expand the corpus.

## Future Implementation Boundary

A future implementation task would need separate approval before creating any
of these or equivalent surfaces:

- `retrieval/`
- `index/`
- `scripts/build_index.py`
- embeddings
- vector databases
- Haystack or other RAG dependencies
- generated retrieval reports
- generated corpus digests
- quality-gate or CI integration

Future implementation must remain local-first unless a separate task explicitly
changes that boundary.

## Non-Goals

This plan does not add:

- retrieval code
- index files
- embeddings
- vector storage
- RAG dependencies
- prompt capture
- model output capture
- tool-call capture
- external-service calls
- CI workflows
- application/device/live-write code
