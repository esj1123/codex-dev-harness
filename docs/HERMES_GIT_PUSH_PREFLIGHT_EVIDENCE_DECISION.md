# Hermes Git Push Preflight Evidence Decision

## Purpose

Record the Phase 9O decision about whether the standalone dry-run Hermes
git-push preflight caller should keep stdout-only output or begin receipt/trace
evidence linkage planning.

Phase 9O is documentation and focused synthetic-test only. It does not change
`scripts/hermes_git_push_preflight.py`, change `scripts/hermes_sidecar.py`,
create receipt or trace schemas, write receipt files, write trace files, create
audit automation, persist preflight output, run `git push`, stage files,
commit, tag, dispatch workflows, upload artifacts, execute MCP tools, wire
quality-gate or CI integration, regenerate artifacts or digests, call external
services, add AgentOps or memory behavior, publish releases, or edit downstream
repositories.

## Basis

This decision depends on:

- `scripts/hermes_git_push_preflight.py`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_OUTPUT_CONTRACT.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_USAGE_PROBE.md`
- `docs/HERMES_PREFLIGHT_CALLER_IMPLEMENTATION_BOUNDARY.md`
- `docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md`
- `docs/JSON_EVIDENCE_POLICY.md`
- `docs/AUDIT_TRACE_SCHEMA.md`
- `audits/receipt-summary.schema.json`
- `audits/trace-event.schema.json`

The current caller emits safe stdout JSON for the immediate invocation and
keeps the underlying Hermes result memory-only. Phase 9M defines that output as
a preflight decision record, not an execution receipt. Phase 9N verifies the
current caller remains fail-closed and non-executing.

## Decision

Decision: `stdout_only_retained_until_receipt_trace_consumer_is_approved`.

The standalone git-push preflight caller should remain stdout-only for the
current implementation. It should not write receipt files, trace files, audit
logs, JSON evidence artifacts, release artifacts, or temporary output files.

Receipt/trace linkage may be useful later, but adding it now would create a
durable evidence surface before there is an approved evidence consumer. There
is not yet:

- an approved receipt writer for Hermes preflight output;
- an approved trace writer for Hermes preflight output;
- an approved schema extension for Hermes preflight evidence;
- an approved quality-gate or CI consumer;
- an approved audit automation flow;
- an approved release, AgentOps, memory, MCP, or downstream consumer.

The safer current boundary is to keep preflight output ephemeral and visible on
stdout only, while requiring a separate planning task before any durable
receipt/trace linkage.

## Future Receipt/Trace Planning Conditions

A later task may plan Hermes git-push preflight receipt/trace evidence only
when it names:

- the exact receipt fields and whether they extend
  `audits/receipt-summary.schema.json`;
- the exact trace fields and whether they extend
  `audits/trace-event.schema.json`;
- whether evidence captures no output, a redacted summary, selected fields, or
  a bounded artifact reference;
- the allowed status and reason-code values;
- how `receipt_id` and `related_receipt_id` are assigned or referenced;
- whether evidence is manual-only, test-only, quality-gated, CI-gated, or
  runtime-generated;
- the exact writer, if any, and whether it is a script, manual process, or
  future integration;
- forbidden captured material;
- cleanup rules for any temporary files;
- verification commands;
- Local Verify and closeout requirements.

That planning task must still not write real receipts, real trace events, audit
logs, release artifacts, or downstream evidence unless separately approved.

## Evidence Boundary

If receipt/trace linkage is approved later, the durable evidence must remain a
safe summary. It may cite:

- `schema_version`;
- `mode`;
- `decision`;
- `side_effect_requested`;
- `guarded_command`;
- `would_run_git_push`;
- empty `performed_actions`;
- `reason_code`;
- bounded `stop_reasons`;
- bounded safe `evidence_refs`;
- sanitized nested Hermes summary fields;
- safe `safety_notes`;
- commit and Local Verify identifiers when they are already reviewed.

It must not store:

- raw prompts or prompt transcripts;
- private data;
- raw command logs;
- raw preflight stdout dumps when a smaller summary is sufficient;
- model output transcripts;
- unredacted tool-call request or response bodies;
- secrets, credentials, tokens, account values, or API keys;
- IPs, ports, live endpoints, live config, device values, broker values, or
  equipment values;
- local absolute paths;
- private raw corpus, `08_Study` raw notes, RSID raw evidence, downstream raw
  evidence, or generated downstream source.

## Non-goals

Phase 9O does not:

- change `scripts/hermes_git_push_preflight.py`;
- change `scripts/hermes_sidecar.py`;
- add receipt or trace schema fields;
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

## Verification

Phase 9O is accepted as `PASS WITH NOTES` when this decision document and
focused synthetic tests pass local verification.

Clean GitHub Actions Local Verify evidence should be recorded separately after
this documentation and focused-test decision is committed and pushed.

## Next Step

After Phase 9O is committed and clean Local Verify passes, the next safe Hermes
step should be either:

- a separately approved Phase 9P receipt/trace evidence planning task, if the
  owner wants durable evidence linkage; or
- a pause before any further caller/runtime expansion.

Any later task that writes evidence, persists preflight output, changes schema
files, runs `git push`, integrates with quality gates or CI, executes MCP
tools, creates audit automation, calls external services, adds AgentOps or
memory behavior, publishes releases, or touches downstream repositories must be
separately approved with exact files, commands, generated artifacts, cleanup
rules, and safety boundaries.
