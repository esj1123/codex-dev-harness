# Hermes Git Push Preflight Writer Persistence Hold Decision

## Purpose

Record the Phase 9T decision after the Phase 9S not-run writer skeleton and
Phase 9S.1 synthetic failure matrix.

Phase 9T is documentation and focused synthetic-test only. It does not change
`scripts/hermes_git_push_preflight_writer.py`, implement
`selected_fields_receipt_writer`, implement `selected_fields_trace_writer`,
implement durable `manual_summary_only` persistence, change receipt or trace
schemas, write receipt files, write trace files, create audit logs, persist
preflight output, run `git push` through Hermes, stage files as evidence, tag,
dispatch workflows through Hermes, upload artifacts, execute MCP tools, wire
quality-gate or CI integration, regenerate artifacts or digests, call external
services, add AgentOps or memory behavior, publish releases, or edit downstream
repositories.

## Basis

This decision depends on:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_EVIDENCE_DECISION.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_RECEIPT_TRACE_PLAN.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_SCHEMA_ALIGNMENT_REVIEW.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_CAPTURE_BOUNDARY_REVIEW.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_IMPLEMENTATION_PLAN.md`
- `scripts/hermes_git_push_preflight_writer.py`
- `tests/test_hermes_git_push_preflight_writer.py`
- `docs/JSON_EVIDENCE_POLICY.md`
- `audits/receipt-summary.schema.json`
- `audits/trace-event.schema.json`

Phase 9S implemented only the `not_run_record_only` writer class. Phase 9S.1
expanded synthetic failure coverage and kept output temporary, outside the
repository, and cleanup-proven.

The clean Local Verify evidence for Phase 9S.1 is run `28494811674`, job
`84458787551`, for commit `f19d3bd20e4f926b6e0e13a1336c19a04503dbc9`.

## Decision

Decision: `writer_persistence_hold_until_durable_consumer_is_approved`.

The current writer should remain a synthetic-only `not_run_record_only`
skeleton. It may validate selected synthetic fields and write temporary JSON
outside the repository for tests, but it must not be promoted to a durable
receipt writer, trace writer, manual summary persistence mechanism, audit log
writer, artifact writer, quality-gate producer, CI producer, MCP runtime, or
release automation producer without a separate owner-approved task.

The current writer record remains evidence of non-execution. It is not a
receipt, trace event, audit log, preflight stdout capture, approval transcript,
or proof that a git push was attempted or completed through Hermes.

## Persistence Hold Conditions

Durable Hermes git-push preflight writer work remains on hold until a later task
names all of the following:

- the approved writer class;
- the exact receipt or trace consumer;
- the exact allowed output path or paths;
- whether output is temporary, tracked, or externally consumed;
- whether existing files may be overwritten;
- the exact selected field source and fixture policy;
- how `receipt_id`, `related_receipt_id`, and `receipt_evidence_key` are
  assigned or referenced;
- how reviewed commit identifiers and Local Verify run/job identifiers are
  selected;
- the cleanup policy for every temporary file;
- the redaction checks before persistence;
- the verification commands and Local Verify closeout requirements.

If any of these are absent, the durable writer must not run.

## Allowed Interim Work

Before durable writer approval, allowed work is limited to:

- documentation-only boundary review;
- focused synthetic tests;
- temporary `tmp_path` output during tests;
- cleanup-proven temporary output deletion;
- read-only review of Local Verify evidence;
- local verification commands.

Interim work must not create tracked receipt files, trace events, audit logs,
artifact outputs, generated evidence folders, release files, downstream files,
or quality-gate or CI integration.

## Capture Boundary

The only selected fields approved for the current synthetic not-run record are:

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

The constrained values remain:

- `writer_class`: `not_run_record_only`
- `status`: `NOT_RUN`
- `side_effect_class`: `git_push`
- `performed_actions`: `[]`

Do not store raw preflight stdout, raw prompts, prompt transcripts, approval
conversation text, raw command logs, shell transcripts, model output
transcripts, unredacted tool-call request or response bodies, secrets,
credentials, tokens, account values, IPs, ports, endpoints, live config, device
values, local absolute paths, private raw corpus, `08_Study` raw notes, RSID raw
evidence, downstream raw evidence, or generated downstream source.

## Non-goals

Phase 9T does not:

- change `scripts/hermes_git_push_preflight_writer.py`;
- change `scripts/hermes_git_push_preflight.py`;
- change `scripts/hermes_sidecar.py`;
- change receipt or trace schemas;
- change `scripts/gates/json_evidence_gate.py`;
- implement `selected_fields_receipt_writer`;
- implement `selected_fields_trace_writer`;
- implement durable `manual_summary_only` persistence;
- write or generate receipt files, trace files, audit logs, preflight
  artifacts, release artifacts, or downstream evidence;
- connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP, audit
  automation, release automation, AgentOps, memory, external services, or
  downstream repositories;
- run real `git push`, `git add`, `git commit`, `git tag`, release publication,
  workflow dispatch, artifact upload, MCP execution, external calls, audit
  generation, receipt generation, trace writing, or downstream mutation through
  Hermes.

## Verification

Phase 9T is accepted as `PASS WITH NOTES` when this decision document and
focused synthetic tests pass local verification.

Recommended verification:

- `python -m pytest tests/test_hermes_git_push_preflight_writer_persistence_hold.py`
- `python -m pytest tests/test_hermes_git_push_preflight_writer.py`
- `python -m pytest tests/test_hermes_git_push_preflight.py`
- `python -m pytest tests/test_json_evidence_gate.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `git diff --check`
- `git ls-files --others --exclude-standard`

Clean GitHub Actions Local Verify evidence should be recorded separately after
this documentation and focused-test decision is committed and pushed.

## Next Step

After Phase 9T is committed and clean Local Verify passes, the next safe Hermes
step should be either:

- pause before durable writer, receipt, trace, audit, CI, MCP, or runtime
  expansion; or
- a separately approved durable writer proposal that names exact files, writer
  class, output paths, consumers, cleanup rules, verification commands, Local
  Verify requirements, and every permitted side effect.

Phase 9T does not authorize that later durable writer proposal by itself.
