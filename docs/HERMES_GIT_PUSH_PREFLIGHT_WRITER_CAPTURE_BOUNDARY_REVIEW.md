# Hermes Git Push Preflight Writer Capture Boundary Review

## Purpose

Record the Phase 9R boundary review for any future Hermes git-push preflight
writer or capture workflow.

Phase 9R is documentation-only and contract-only. It does not implement a
writer, add a capture script, create receipt files, create trace files, create
audit logs, persist preflight output, run `git push` through Hermes, stage files
as evidence, commit through Hermes, tag, dispatch workflows, upload artifacts,
execute MCP tools, wire quality-gate or CI integration, regenerate artifacts or
digests, call external services, add AgentOps or memory behavior, publish
releases, or edit downstream repositories.

## Basis

This review depends on:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_EVIDENCE_DECISION.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_RECEIPT_TRACE_PLAN.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_SCHEMA_ALIGNMENT_REVIEW.md`
- `docs/JSON_EVIDENCE_POLICY.md`
- `audits/receipt-summary.schema.json`
- `audits/trace-event.schema.json`
- `scripts/hermes_git_push_preflight.py`

The parked Phase 9R draft was reviewed read-only and rehydrated against current
HEAD after the Phase 9Q.1 status-only consistency remediation. The stash itself
is not a source of committed authority and does not authorize applying stale
tracked changes directly.

## Boundary Decision

Decision: `writer_capture_boundary_documented_without_writer`.

The schema can now describe selected Hermes git-push preflight evidence, but no
durable writer is approved. A later writer or capture task must start from a
fresh owner approval that names exact files, output paths, cleanup behavior,
verification commands, and whether any generated evidence may remain tracked.

## Approved Future Writer Classes

A later task may propose one of these writer classes only with separate
approval:

- `manual_summary_only`: human-written closeout text based on reviewed
  preflight output, without generated receipt or trace files.
- `selected_fields_receipt_writer`: a local script that writes only the
  `hermes_git_push_preflight_evidence` object into an approved receipt summary
  destination.
- `selected_fields_trace_writer`: a local script that writes only the compact
  `hermes_git_push_preflight_evidence_ref` pointer into an approved trace event
  destination.
- `not_run_record_only`: a safe record that the writer was intentionally not
  run.

No class may write raw preflight stdout, prompt transcripts, command logs,
approval conversation text, tool-call bodies, secrets, private data, live
configuration, local absolute paths, or downstream raw evidence.

## Output Policy Required Before Implementation

Any future writer approval must define:

- exact allowed output path or paths;
- whether output paths already exist or may be created;
- whether generated output is temporary or intended to be tracked;
- how temporary output is deleted after verification;
- the exact schema field set to write;
- the exact source of selected fields;
- how `receipt_id`, `related_receipt_id`, and `receipt_evidence_key` are
  assigned or referenced;
- how Local Verify run/job identifiers are reviewed before inclusion;
- how failed, blocked, not-run, and not-applicable outcomes are represented;
- how redaction is checked before persistence.

If any of these are absent, the writer must not run.

## Capture Policy

Allowed durable evidence is limited to selected schema fields, booleans, bounded
safe summaries, repo-relative evidence references, reviewed commit identifiers,
and reviewed Local Verify run/job identifiers.

Do not store:

- raw prompts or prompt transcripts;
- private data;
- raw command logs;
- raw preflight stdout dumps;
- model output transcripts;
- unredacted tool-call request or response bodies;
- secrets, credentials, tokens, account values, or API keys;
- IPs, ports, live endpoints, live config, device values, broker values, or
  equipment values;
- local absolute paths;
- private raw corpus, `08_Study` raw notes, RSID raw evidence, downstream raw
  evidence, or generated downstream source;
- full approval conversation text.

## Cleanup Policy

Future verification may create temporary writer output only if the task
approval names the temporary paths and cleanup steps.

Temporary output must be deleted before closeout unless the approval explicitly
states it is intended tracked evidence. Closeout must report:

- files created;
- files deleted;
- whether any receipt or trace file remains;
- whether `git ls-files --others --exclude-standard` is clean;
- whether tracked generated output is intentionally staged or left unstaged.

## Verification Required Before Any Future Writer Commit

A later writer implementation task must run, at minimum:

- JSON parsing for any generated receipt or trace file;
- focused writer tests using synthetic fixtures;
- `python scripts/quality_gate.py`;
- `python -m pytest tests`;
- `git diff --check`;
- `git ls-files --others --exclude-standard`;
- explicit cleanup checks for any temporary evidence files.

If a command cannot run, closeout must record `NOT RUN` or `ENVIRONMENT BLOCKED`
honestly.

## Non-goals

Phase 9R does not:

- change `scripts/hermes_git_push_preflight.py`;
- change `scripts/hermes_sidecar.py`;
- change receipt or trace schemas;
- change `scripts/gates/json_evidence_gate.py`;
- add a writer or capture script;
- write or generate receipt files, trace files, audit logs, preflight
  artifacts, release artifacts, or downstream evidence;
- connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP, audit
  automation, release automation, AgentOps, memory, external services, or
  downstream repositories;
- run real `git push`, `git add`, `git commit`, `git tag`, release publication,
  workflow dispatch, artifact upload, MCP execution, external calls, audit
  generation, receipt generation, trace writing, or downstream mutation through
  Hermes;
- persist raw prompts, private data, raw command logs, model outputs,
  unredacted tool-call bodies, secrets, account values, IPs, ports, live config,
  device values, local absolute paths, private raw corpus, `08_Study` raw notes,
  RSID raw evidence, downstream raw evidence, or generated downstream source.

## Next Step

After Phase 9R is committed, pushed, and clean Local Verify passes, the next safe
Hermes step should be either:

- a separately approved Phase 9S writer implementation task with exact allowed
  files, exact temporary or tracked output paths, cleanup policy, and
  verification commands; or
- a pause before any durable writer, CI integration, MCP integration, or
  caller/runtime expansion.
