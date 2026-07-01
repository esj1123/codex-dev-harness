# Hermes Git Push Preflight Selected Receipt Writer Implementation Plan

## Purpose

Record the Phase 9V implementation boundary for a minimal
`selected_fields_receipt_writer`.

Phase 9V implements only a synthetic selected-field writer for the optional
`receipt_summary.hermes_git_push_preflight_evidence` object. It writes temporary
JSON outside the repository for tests and review. It does not write a full
receipt summary, write a trace event, create an audit log, persist preflight
stdout, run `git push` through Hermes, stage files as evidence, tag, dispatch
workflows through Hermes, upload artifacts, execute MCP tools, wire
quality-gate or CI integration, regenerate artifacts or digests, call external
services, add AgentOps or memory behavior, publish releases, or edit downstream
repositories.

## Allowed Files

Phase 9V implementation is limited to:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_SELECTED_RECEIPT_WRITER_IMPLEMENTATION_PLAN.md`
- `scripts/hermes_git_push_preflight_receipt_writer.py`
- `tests/test_hermes_git_push_preflight_receipt_writer.py`

`STATUS.md`, `ACCEPTANCE_TRACE.md`, schemas, JSON gates, workflows, artifacts,
audits, evals, templates, profiles, examples, dependencies, and downstream
repositories are intentionally excluded from this implementation task.

## Basis

This implementation depends on:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_DURABLE_WRITER_PROPOSAL.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_PERSISTENCE_HOLD_DECISION.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_SCHEMA_ALIGNMENT_REVIEW.md`
- `audits/receipt-summary.schema.json`
- `scripts/hermes_git_push_preflight_writer.py`

The clean Local Verify evidence for Phase 9U is run `28496626209`, job
`84464169619`, for commit `a101bc704acfdd7f34e1161275010c9a0bea3c19`.

## Writer Class

The only writer class implemented by Phase 9V is:

- `selected_fields_receipt_writer`

This writer emits the optional
`receipt_summary.hermes_git_push_preflight_evidence` object only. It must not
emit a full receipt summary, a trace event, receipt top-level fields, trace top-level fields,
`hermes_git_push_preflight_evidence_ref`, `receipt_id`, `related_receipt_id`,
`receipt_evidence_key`, raw stdout fields, or command-log fields.

Phase 9V does not implement `selected_fields_trace_writer` or durable
`manual_summary_only` persistence. The existing Phase 9S
`not_run_record_only` writer remains separate.

## Selected Field Set

The writer accepts these selected synthetic fields:

- `preflight_evidence_status`
- `preflight_output_mode`
- `caller_schema_version`
- `caller_mode`
- `decision`
- `side_effect_requested`
- `guarded_command`
- `would_run_git_push`
- `performed_actions_empty`
- `reason_code`
- `stop_reasons`
- `approval_ref_present`
- `evidence_refs`
- `hermes_result_summary`
- `safe_task_summary`
- `safety_notes`
- `observed_head_commit`
- `local_verify_run_id`
- `local_verify_job_id`
- `output_capture`
- `preflight_integration_status`

The writer output shape is deterministic and contains exactly that field set.

## Constrained Values

The initial selected receipt writer is bounded to non-executing, standalone
receipt-summary evidence:

- `preflight_output_mode`: `selected_fields`
- `output_capture`: `selected_fields`
- `performed_actions_empty`: `true`
- `would_run_git_push`: `false`
- `preflight_integration_status`: `receipt-summary-only`

`receipt-summary-only` is the existing schema value that represents standalone
receipt evidence without quality-gate or CI integration.

## Input Policy

Phase 9V accepts synthetic selected-field fixtures only. It must not capture
real `scripts/hermes_git_push_preflight.py` stdout or stderr.

Input must not include raw stdout, stderr, shell transcripts, command logs,
approval text, prompt text, prompt transcripts, tool-call bodies, model output
transcripts, tokens, account values, local absolute paths, IPs, ports,
endpoints, live config, device values, private data, raw `08_Study`, RSID raw
evidence, downstream raw evidence, or generated downstream source.

## Output Policy

Phase 9V output is temporary JSON only:

- output must use a `.json` suffix;
- output must be outside the repository;
- output must not overwrite an existing file;
- output must not be written under `artifacts/`, `audits/receipts`,
  `audits/traces`, or any repository-internal path;
- output must be deterministic JSON with sorted keys and a final newline;
- cleanup must delete every temporary output file and fail if cleanup cannot be
  proven.

No tracked receipt, trace, audit, or artifact output is approved by Phase 9V.

## Failure Modes

The writer reports:

- `PASS`
- `FAIL`
- `ENVIRONMENT BLOCKED`

Validation failure, forbidden keys, unknown keys, unsafe text, invalid enum
values, attempted overwrite, repository-internal output, non-JSON output paths,
and missing cleanup are `FAIL`. Fixture read or JSON parse failure is
`ENVIRONMENT BLOCKED`.

## Verification

Phase 9V verification must include at least:

- `python -m pytest tests/test_hermes_git_push_preflight_receipt_writer.py`
- `python -m pytest tests/test_hermes_git_push_preflight_writer.py`
- `python -m pytest tests/test_hermes_git_push_preflight.py`
- `python -m pytest tests/test_json_evidence_gate.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `git diff --check`
- `git ls-files --others --exclude-standard`

Clean GitHub Actions Local Verify evidence should be recorded separately after
this implementation is committed and pushed.

## Non-goals

Phase 9V does not:

- change `scripts/hermes_git_push_preflight_writer.py`;
- change `scripts/hermes_git_push_preflight.py`;
- change `scripts/hermes_sidecar.py`;
- change receipt or trace schemas;
- change `scripts/gates/json_evidence_gate.py`;
- write or generate full receipt files, trace files, audit logs, preflight
  artifacts, release artifacts, or downstream evidence;
- wire quality-gate or CI integration;
- connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP, audit
  automation, release automation, AgentOps, memory, external services, or
  downstream repositories;
- run real `git push`, `git add`, `git commit`, `git tag`, release publication,
  workflow dispatch, artifact upload, MCP execution, external calls, audit
  generation, receipt generation, trace writing, or downstream mutation through
  Hermes.

## Next Step

After Phase 9V is committed and clean Local Verify passes, the next safe Hermes
step should be either:

- pause before any generated receipt, trace, audit, CI, MCP, or runtime
  persistence; or
- a separately approved synthetic hardening task for the selected receipt
  writer.

Phase 9V does not authorize tracked receipt generation by itself.
