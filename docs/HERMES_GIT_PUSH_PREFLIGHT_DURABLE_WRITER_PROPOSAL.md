# Hermes Git Push Preflight Durable Writer Proposal

## Purpose

Record the Phase 9U proposal for a future durable Hermes git-push preflight
writer without implementing that writer.

Phase 9U is documentation and focused synthetic-test only. It does not change
`scripts/hermes_git_push_preflight_writer.py`, implement
`selected_fields_receipt_writer`, implement `selected_fields_trace_writer`,
implement durable `manual_summary_only` persistence, change receipt or trace
schemas, change `scripts/gates/json_evidence_gate.py`, write receipt files,
write trace files, create audit logs, persist preflight output, run `git push`
through Hermes, stage files as evidence, tag, dispatch workflows through
Hermes, upload artifacts, execute MCP tools, wire quality-gate or CI
integration, regenerate artifacts or digests, call external services, add
AgentOps or memory behavior, publish releases, or edit downstream repositories.

## Basis

This proposal depends on:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_EVIDENCE_DECISION.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_RECEIPT_TRACE_PLAN.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_SCHEMA_ALIGNMENT_REVIEW.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_CAPTURE_BOUNDARY_REVIEW.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_IMPLEMENTATION_PLAN.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_PERSISTENCE_HOLD_DECISION.md`
- `scripts/hermes_git_push_preflight.py`
- `scripts/hermes_git_push_preflight_writer.py`
- `audits/receipt-summary.schema.json`
- `audits/trace-event.schema.json`

The clean Local Verify evidence for Phase 9T is run `28495663622`, job
`84461272582`, for commit `e2f882d9dad592db09f8a12c3a45458413949dbd`.

## Proposal Decision

Decision: `selected_fields_receipt_writer_proposed_without_implementation`.

The first future durable-writer candidate should be
`selected_fields_receipt_writer`, and it should target only the optional
`receipt_summary.hermes_git_push_preflight_evidence` object already described
by the Phase 9Q schema alignment work.

This proposal does not approve implementation. It only names the candidate
writer class, consumer, file scope, selected-field boundary, output policy,
cleanup expectations, and verification gate for a later separately approved
implementation task.

`selected_fields_trace_writer` remains deferred until a receipt writer exists
and an actual trace-linking consumer is approved. Durable `manual_summary_only`
persistence remains deferred because manual closeout text can be captured in
task closeout without creating a new writer surface.

## Future Implementation Scope

A later implementation task may use only these files unless the owner names a
different exact file set:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_SELECTED_RECEIPT_WRITER_IMPLEMENTATION_PLAN.md`
- `scripts/hermes_git_push_preflight_receipt_writer.py`
- `tests/test_hermes_git_push_preflight_receipt_writer.py`

That later task must not edit:

- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `audits/receipt-summary.schema.json`
- `audits/trace-event.schema.json`
- `scripts/gates/json_evidence_gate.py`
- `.github/workflows/local-verify.yml`
- artifacts, audits, evals, templates, profiles, examples, dependencies, or
  downstream repositories

Any change to those no-touch areas requires a separate task with exact
approval.

## Consumer And Output Policy

The only proposed durable consumer is the optional
`receipt_summary.hermes_git_push_preflight_evidence` field.

For the first implementation task, writer output must remain temporary JSON
only:

- tests should use `tmp_path`;
- CLI output, if added, must require an explicit `--output-json` path;
- output must be deterministic JSON with a final newline;
- output must not overwrite an existing file;
- output must not be written under `artifacts/`, `audits/receipts`,
  `audits/traces`, or any repository-internal path;
- cleanup must delete every temporary output file before closeout;
- `git ls-files --others --exclude-standard` must be clean after cleanup.

Tracked receipt output is not approved by Phase 9U. A later receipt-generation
task must name a concrete receipt id, repository path, retention rule, cleanup
rule, and review workflow before any generated receipt remains in the
repository.

## Selected Field Boundary

The future writer may write only the fields already present in
`receipt_summary.hermes_git_push_preflight_evidence`:

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

Constrained values for the first implementation proposal:

- `preflight_output_mode`: `selected_fields`
- `output_capture`: `selected_fields`
- `performed_actions_empty`: `true`
- `would_run_git_push`: `false`
- `preflight_integration_status`: `standalone_not_quality_gate_or_ci`

The writer must not write receipt top-level fields, trace top-level fields,
`hermes_git_push_preflight_evidence_ref`, `receipt_id`, `related_receipt_id`,
`receipt_evidence_key`, or any raw output field.

## Source Policy

Phase 9U does not approve capture from real
`scripts/hermes_git_push_preflight.py` stdout.

A later implementation task may use only synthetic selected-field fixtures
unless it separately names a reviewed source and redaction procedure. It must
not capture raw stdout, stderr, shell transcripts, command logs, approval text,
prompt text, tool-call bodies, model output transcripts, tokens, account
values, local absolute paths, IPs, ports, endpoints, live config, device values,
private data, raw `08_Study`, RSID raw evidence, downstream raw evidence, or
generated downstream source.

Reviewed commit identifiers and reviewed Local Verify run/job identifiers may
be included only as selected fields after the task closeout has verified them.

## Failure Modes

The later writer must classify outcomes with explicit statuses:

- `PASS`
- `PASS WITH NOTES`
- `BLOCKED`
- `FAIL`
- `NOT RUN`
- `ENVIRONMENT BLOCKED`

Validation failure, forbidden fields, unsafe text, unexpected schema shape,
missing cleanup, attempted overwrite, repository-internal output, and missing
consumer approval must be `FAIL` or `BLOCKED`, not silent success.

## Verification Gate

A later implementation task must run at least:

- `python -m pytest tests/test_hermes_git_push_preflight_receipt_writer.py`
- `python -m pytest tests/test_hermes_git_push_preflight_writer.py`
- `python -m pytest tests/test_hermes_git_push_preflight.py`
- `python -m pytest tests/test_json_evidence_gate.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `git diff --check`
- `git ls-files --others --exclude-standard`

Clean GitHub Actions Local Verify evidence must be recorded separately after
that implementation is committed and pushed.

## Non-goals

Phase 9U does not:

- implement a durable writer;
- change `scripts/hermes_git_push_preflight_writer.py`;
- change `scripts/hermes_git_push_preflight.py`;
- change `scripts/hermes_sidecar.py`;
- change receipt or trace schemas;
- change `scripts/gates/json_evidence_gate.py`;
- write or generate receipt files, trace files, audit logs, preflight
  artifacts, release artifacts, or downstream evidence;
- connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP, audit
  automation, release automation, AgentOps, memory, external services, or
  downstream repositories;
- run real `git push`, `git add`, `git commit`, `git tag`, release publication,
  workflow dispatch, artifact upload, MCP execution, external calls, audit
  generation, receipt generation, trace writing, or downstream mutation through
  Hermes.

## Next Step

After Phase 9U is committed and clean Local Verify passes, the next safe Hermes
step should be either:

- pause before any durable writer implementation; or
- a separately approved Phase 9V
  `selected_fields_receipt_writer` implementation task using the exact file
  scope, temporary output policy, source policy, cleanup checks, and
  verification gate from this proposal.

Phase 9U does not authorize Phase 9V by itself.
