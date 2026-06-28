# Hermes Git Push Preflight Writer Implementation Plan

## Purpose

Define the Phase 9S implementation boundary for a minimal Hermes git-push
preflight writer skeleton.

Phase 9S implements only the `not_run_record_only` writer class. It validates
synthetic selected-field fixtures, rejects forbidden fields, emits a bounded
`NOT_RUN` JSON record to temporary test output, and proves cleanup. It is not
durable receipt or trace persistence.

## Allowed Files

Phase 9S implementation is limited to:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_IMPLEMENTATION_PLAN.md`
- `scripts/hermes_git_push_preflight_writer.py`
- `tests/test_hermes_git_push_preflight_writer.py`

`STATUS.md` and `ACCEPTANCE_TRACE.md` are intentionally excluded from the Phase
9S implementation commit to avoid recursive evidence commits.

## Writer Class

The only approved writer class for Phase 9S is:

- `not_run_record_only`

The writer must emit these constrained values:

- `writer_class`: `not_run_record_only`
- `status`: `NOT_RUN`
- `side_effect_class`: `git_push`
- `performed_actions`: `[]`

The writer must not implement `selected_fields_receipt_writer`,
`selected_fields_trace_writer`, or durable `manual_summary_only` persistence.

## Input Policy

Phase 9S accepts synthetic selected-field fixtures only. It must not capture or
parse live `scripts/hermes_git_push_preflight.py` stdout, stderr, shell
transcripts, command logs, approval text, prompts, tool-call bodies, tokens,
account values, local absolute paths, IPs, ports, endpoints, live config, device
values, private data, raw `08_Study`, RSID raw evidence, or downstream raw
evidence.

The fixture may contain only these selected fields:

- `schema_version`
- `writer_class`
- `status`
- `reason_code`
- `side_effect_class`
- `decision`
- `performed_actions`
- `evidence_refs`
- `safe_summary`
- `checked_commit`
- `local_verify_run_id`
- `local_verify_job_id`
- `created_at`

Unknown keys and explicit forbidden raw-capture keys must fail validation.

## Output Policy

Phase 9S output is temporary JSON only. Tests should use `tmp_path`; output must
not be written under `artifacts/`, `audits/receipts`, `audits/traces`, or any
tracked repository path.

Phase 9S does not create:

- tracked receipt files;
- tracked trace events;
- audit logs;
- generated artifacts under `artifacts/`;
- durable evidence under `audits/receipts` or `audits/traces`.

Cleanup must delete temporary output before closeout. Missing cleanup is a
failure, not a warning.

## Record Shape

The record uses deterministic JSON with sorted keys and a final newline. It
contains only the allowed selected fields. It does not store raw source payloads
or raw preflight output.

Allowed status and closeout labels for this layer are:

- `PASS`
- `PASS WITH NOTES`
- `BLOCKED`
- `FAIL`
- `NOT RUN`
- `ENVIRONMENT BLOCKED`

The emitted writer record itself remains `status = NOT_RUN`.

## Verification

Phase 9S verification must include at least:

- `python -m pytest tests/test_hermes_git_push_preflight_writer.py`
- `python -m pytest tests/test_hermes_git_push_preflight.py`
- `python -m pytest tests/test_json_evidence_gate.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `git diff --check`
- `git ls-files --others --exclude-standard`

## Non-goals

Phase 9S does not:

- edit schemas;
- edit `scripts/gates/json_evidence_gate.py`;
- wire quality-gate or CI integration;
- edit workflows;
- capture actual preflight stdout;
- write receipt, trace, or audit files;
- run real `git push`;
- stage, commit, tag, release, or publish through the writer;
- execute MCP tools;
- expand Hermes sidecar runtime behavior;
- add AgentOps or memory runtime behavior;
- access downstream repositories.

## Next Step

After Phase 9S is committed, pushed, and clean Local Verify passes, a later
task may separately review whether to keep the writer as a synthetic-only
skeleton, add more synthetic failure cases, or pause before any durable receipt
or trace persistence.
