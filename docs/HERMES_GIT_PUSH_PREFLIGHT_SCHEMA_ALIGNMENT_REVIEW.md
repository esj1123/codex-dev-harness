# Hermes Git Push Preflight Schema Alignment Review

## Purpose

Record the Phase 9Q schema-alignment review for optional Hermes git-push
preflight evidence references in receipt summaries and trace events.

Phase 9Q changes only the JSON evidence schema shape, policy text, focused
tests, and trace/status documentation. It does not implement a writer, capture
preflight output, create receipt or trace files, create audit logs, persist
preflight output, run `git push`, stage files as evidence, dispatch workflows,
upload artifacts, execute MCP tools, wire quality-gate or CI integration,
regenerate artifacts or digests, call external services, add AgentOps or memory
behavior, publish releases, or edit downstream repositories.

## Basis

This review depends on:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_RECEIPT_TRACE_PLAN.md`
- `docs/JSON_EVIDENCE_POLICY.md`
- `audits/receipt-summary.schema.json`
- `audits/trace-event.schema.json`
- `scripts/gates/json_evidence_gate.py`
- `tests/test_json_evidence_gate.py`

## Alignment Decision

Decision: `hermes_git_push_preflight_schema_aligned_without_writer`.

Hermes git-push preflight evidence remains selected-field evidence only. The
receipt schema may describe a safe optional evidence object, and the trace
schema may describe a compact pointer to that receipt evidence. Neither schema
field authorizes durable output, preflight stdout persistence, a writer,
quality-gate or CI use, audit automation, real `git push`, MCP execution, or
downstream mutation.

## Receipt Schema Field

`receipt_summary` may include optional
`hermes_git_push_preflight_evidence`.

The field is optional and must not be part of the receipt top-level `required`
list. When present, it must set `additionalProperties` to `false` and use this
exact field set:

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

Allowed values keep current caller behavior fail-closed. `decision` is limited
to `STOP`, `not checked`, or `not applicable`; `side_effect_requested` is
limited to `git_push`, `none`, `not checked`, or `not applicable`;
`guarded_command` is a safe label such as `git push`, not a raw command log;
and `would_run_git_push` remains boolean evidence, not execution permission.

`evidence_refs` must be repo-relative paths. `observed_head_commit` must use
the existing commit-or-unknown pattern. Approval references are represented as
`approval_ref_present` only; do not store approval conversation text.

## Trace Schema Field

`trace_event` may include optional
`hermes_git_push_preflight_evidence_ref`.

The field is optional and must not be part of the trace top-level `required`
list. When present, it must set `additionalProperties` to `false` and use this
compact field set:

- `preflight_evidence_status`
- `decision`
- `reason_code`
- `side_effect_requested`
- `receipt_evidence_key`
- `observed_head_commit`
- `summary`

`receipt_evidence_key` must be
`hermes_git_push_preflight_evidence`. Trace events should continue to use
`related_receipt_id` to point to `receipt_summary.receipt_id`; the trace field
is only a compact pointer and safe summary, not a transcript or stdout dump.

## Gate Alignment

`scripts/gates/json_evidence_gate.py` checks that:

- the receipt field exists but is optional;
- the trace field exists but is optional;
- both objects set `additionalProperties` to `false`;
- required internal fields are present;
- `evidence_refs` uses repo-relative path references;
- observed commit fields reuse `commit_or_unknown`;
- the trace `receipt_evidence_key` is fixed to
  `hermes_git_push_preflight_evidence`.

The gate remains a focused bundle-shape check. It is not a full JSON Schema
Draft 2020-12 validator and it does not validate generated evidence records.

## Capture Policy

Allowed durable evidence remains limited to selected fields, booleans, bounded
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

## Verification Boundary

Phase 9Q verification should check:

- both JSON schemas parse;
- focused JSON evidence gate tests pass;
- focused Phase 9Q schema-alignment tests pass;
- `python scripts/quality_gate.py` passes;
- `python -m pytest tests` passes;
- `git diff --check` passes or records line-ending warnings honestly.

Clean GitHub Actions Local Verify evidence should be recorded separately after
this schema-alignment review is committed and pushed.

## Non-goals

Phase 9Q does not:

- change `scripts/hermes_git_push_preflight.py`;
- change `scripts/hermes_sidecar.py`;
- add a writer or capture script;
- write or generate receipt files, trace files, audit logs, preflight
  artifacts, release artifacts, or downstream evidence;
- connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP, audit
  automation, release automation, AgentOps, memory, external services, or
  downstream repositories;
- run real `git push`, `git add`, `git commit`, `git tag`, release publication,
  workflow dispatch, artifact upload, MCP execution, external calls, audit
  generation, receipt generation, trace writing, or downstream mutation;
- persist raw prompts, private data, raw command logs, model outputs,
  unredacted tool-call bodies, secrets, account values, IPs, ports, live
  config, device values, local absolute paths, private raw corpus, `08_Study`
  raw notes, RSID raw evidence, downstream raw evidence, or generated
  downstream source.

## Next Step

After Phase 9Q is committed and clean Local Verify passes, the next safe Hermes
step should be either:

- a separately approved Phase 9R writer or capture review using exact allowed
  files, output policy, cleanup policy, and verification commands; or
- a pause before any durable evidence writer or caller/runtime expansion.
