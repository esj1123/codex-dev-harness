# Hermes Git Push Preflight Receipt Trace Plan

## Purpose

Record the Phase 9P planning contract for optional receipt and trace evidence
references to Hermes git-push preflight decisions.

Phase 9P is documentation and focused synthetic-test only. It does not change
`scripts/hermes_git_push_preflight.py`, change `scripts/hermes_sidecar.py`,
modify `audits/receipt-summary.schema.json`, modify
`audits/trace-event.schema.json`, write receipt files, write trace files, write
audit logs, persist preflight output, run `git push`, stage files, commit, tag,
dispatch workflows, upload artifacts, execute MCP tools, wire quality-gate or
CI integration, regenerate artifacts or digests, call external services, add
AgentOps or memory behavior, publish releases, or edit downstream
repositories.

## Basis

This plan depends on:

- `scripts/hermes_git_push_preflight.py`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_OUTPUT_CONTRACT.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_USAGE_PROBE.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_EVIDENCE_DECISION.md`
- `docs/JSON_EVIDENCE_POLICY.md`
- `docs/AUDIT_TRACE_SCHEMA.md`
- `audits/receipt-summary.schema.json`
- `audits/trace-event.schema.json`

Phase 9O decided that current preflight output remains stdout-only until a
receipt/trace consumer is separately approved. Phase 9P records what such a
future evidence shape should preserve if schema alignment is approved later.

## Planning Decision

Decision: `receipt_trace_plan_documented_without_schema_or_writer`.

Hermes git-push preflight evidence may be useful as safe closeout context, but
it must remain distinct from execution evidence. A future receipt or trace
record may state that preflight stopped a push; it must not imply that a push
was authorized, attempted, or completed.

The current repository should not add receipt or trace schema fields in Phase
9P. Schema alignment, validation, writer behavior, quality-gate integration, CI
integration, audit automation, or any durable output requires a later explicit
approval with exact files and commands.

## Receipt Evidence Candidate

A future `receipt_summary` may include an optional
`hermes_git_push_preflight_evidence` object only when Hermes preflight evidence
was explicitly reviewed or intentionally recorded as not run.

Candidate safe fields are:

- `preflight_evidence_status`: machine status such as `stopped`, `blocked`,
  `not_run`, or `not_applicable`.
- `preflight_output_mode`: `stdout_only`, `manual_summary`, or
  `selected_fields`.
- `caller_schema_version`: expected value such as
  `hermes_git_push_preflight.v0`.
- `caller_mode`: expected value such as `dry_run`.
- `decision`: expected current value `STOP`.
- `side_effect_requested`: expected value `git_push`.
- `guarded_command`: label `git push`; not an executed command log.
- `would_run_git_push`: expected value `false`.
- `performed_actions_empty`: expected value `true`.
- `reason_code`: bounded caller reason code.
- `stop_reasons`: bounded list of caller stop reasons.
- `approval_ref_present`: boolean only; do not store the approval text.
- `evidence_refs`: bounded repo-relative paths already accepted by the caller.
- `hermes_result_summary`: selected safe nested Hermes fields only.
- `safe_task_summary`: sanitized summary, not a prompt transcript.
- `safety_notes`: bounded safe notes about non-execution and non-persistence.
- `observed_head_commit`: commit used when reviewing the preflight output.
- `local_verify_run_id` and `local_verify_job_id`: optional reviewed CI
  evidence identifiers when relevant.
- `output_capture`: `none`, `redacted_summary`, or `selected_fields`.

The receipt evidence must not copy full preflight stdout when selected fields
are sufficient.

## Trace Evidence Candidate

A future `trace_event` may include an optional
`hermes_git_push_preflight_evidence_ref` object when a trace event is
associated with Hermes preflight evidence.

Trace events should keep `related_receipt_id` as the receipt linkage. If a
trace event references Hermes git-push preflight evidence inside a receipt
summary, `related_receipt_id` should point to `receipt_summary.receipt_id`, and
`hermes_git_push_preflight_evidence_ref` should repeat only compact safe
review fields:

- `preflight_evidence_status`;
- `decision`;
- `reason_code`;
- `side_effect_requested`;
- `receipt_evidence_key`, expected to identify
  `hermes_git_push_preflight_evidence`;
- `observed_head_commit`;
- `summary`.

Trace-level evidence is a pointer, not a transcript or preflight stdout dump.

## Capture Policy

Allowed durable evidence is limited to bounded selected fields, safe summaries,
repo-relative evidence references, reviewed commit identifiers, and reviewed
Local Verify run/job identifiers.

Durable receipt or trace evidence must not store:

- raw prompts or prompt transcripts;
- private data;
- raw command logs;
- raw preflight stdout dumps when selected fields are sufficient;
- model output transcripts;
- unredacted tool-call request or response bodies;
- secrets, credentials, tokens, account values, or API keys;
- IPs, ports, live endpoints, live config, device values, broker values, or
  equipment values;
- local absolute paths;
- private raw corpus, `08_Study` raw notes, RSID raw evidence, downstream raw
  evidence, or generated downstream source.

Approval references may be represented only as booleans or safe identifiers
that were already approved for durable evidence. Do not store full approval
conversation text.

## Future Phase Split

The next possible phases remain separate:

- Phase 9Q schema-alignment review may propose exact changes to
  `audits/receipt-summary.schema.json`, `audits/trace-event.schema.json`,
  `scripts/gates/json_evidence_gate.py`, and focused tests.
- Phase 9R writer or capture review may propose a manual or script-based writer
  only after schema alignment is approved.
- Phase 9S integration review may consider quality-gate, CI, release,
  AgentOps, memory, MCP, or downstream consumers only after a writer and
  evidence contract exist.

Approving Phase 9P does not approve any of those later phases.

## Verification Boundary

Phase 9P verification should check:

- this plan and focused synthetic tests pass;
- `python scripts/quality_gate.py` passes;
- `python -m pytest tests` passes;
- `git diff --check` passes or records line-ending warnings honestly;
- no receipt files, trace files, audit logs, preflight artifacts, release
  artifacts, generated evidence, digest changes, schema changes, runtime
  changes, quality-gate or CI integration, MCP execution, or downstream
  changes are added.

Clean GitHub Actions Local Verify evidence should be recorded separately after
this documentation and focused-test plan is committed and pushed.

## Non-goals

Phase 9P does not:

- change `scripts/hermes_git_push_preflight.py`;
- change `scripts/hermes_sidecar.py`;
- modify `audits/receipt-summary.schema.json`;
- modify `audits/trace-event.schema.json`;
- add a machine-readable Hermes preflight schema artifact;
- write or generate receipt files, trace files, audit logs, preflight artifacts,
  release artifacts, or downstream evidence;
- connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP, audit
  automation, release automation, AgentOps, memory, external services, or
  downstream repositories;
- run `git push`, `git add`, `git commit`, `git tag`, release publication,
  workflow dispatch, artifact upload, MCP execution, external calls, audit
  generation, receipt generation, trace writing, or downstream mutation;
- persist raw prompts, private data, raw command logs, model outputs,
  unredacted tool-call bodies, secrets, account values, IPs, ports, live
  config, device values, local absolute paths, private raw corpus, `08_Study`
  raw notes, RSID raw evidence, downstream raw evidence, or generated
  downstream source.

## Next Step

After Phase 9P is committed and clean Local Verify passes, the next safe Hermes
step should be either:

- a separately approved Phase 9Q schema-alignment review using exact allowed
  files and field names; or
- a pause before any durable evidence or caller/runtime expansion.
