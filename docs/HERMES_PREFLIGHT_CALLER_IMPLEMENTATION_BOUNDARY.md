# Hermes Preflight Caller Implementation Boundary

## Purpose

Record the Phase 9J implementation boundary for any future Hermes preflight
caller.

Phase 9J is documentation and focused synthetic-test only. It does not
implement a caller, wrapper, execution bridge, MCP runtime, tool server,
quality-gate hook, CI hook, audit automation, real receipt generation, real log
or trace writing, machine-readable schema artifact, artifact generation, digest
refresh, release automation, external service call, AgentOps or memory runtime,
or downstream integration.

The goal is to define what a later, separately approved caller implementation
must name and verify before it may use the no-op Hermes sidecar result as
fail-closed preflight context.

## Boundary Basis

This boundary depends on:

- `docs/HERMES_PREFLIGHT_USE_PLANNING_CONTRACT.md`
- `docs/HERMES_PREFLIGHT_SYNTHETIC_MATRIX_REVIEW.md`
- `docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md`
- `docs/HERMES_MCP_SECURITY_ALIGNMENT_REVIEW.md`
- `docs/MCP_TOOL_BOUNDARY_CONTRACT.md`
- `docs/JSON_EVIDENCE_POLICY.md`
- `scripts/hermes_sidecar.py`

If these records conflict, a future caller must follow the narrower and safer
rule and stop before side effects.

## Future Caller Shape

A later caller implementation must be separately approved and must name the
exact caller file or script before any code is added. The approval must also
name the exact side-effect class, exact command or action that would be
guarded, exact result fields checked, persistence rule, cleanup rule,
verification commands, forbidden inputs, and forbidden outputs.

The first future caller shape, if approved, should remain local-only,
standard-library-only by default, and no-op with respect to guarded side
effects. It may classify whether a later step should stop, but it must not
execute the guarded action.

No broad approval to "use Hermes", "add an agent wrapper", "connect MCP", or
"improve automation" is enough to implement a caller.

## Required Field Checks

A future caller must inspect these fields before deciding anything:

- `schema_version`
- `mode`
- `status`
- `reason_code`
- `side_effect_requested`
- `approval_ref_present`
- `safe_task_summary`
- `evidence_refs`
- `performed_actions`
- `safety_notes`
- `next_step`

The caller must treat missing, malformed, unexpected, or newly introduced
fields as a stop condition until a separately approved contract update defines
their meaning.

## Caller Decisions

The current no-op result contract supports only these future caller decisions:

- `ADVISORY_ONLY`: the result is safe planning context and no side effect is
  requested.
- `STOP`: the caller must stop before side effects.

Phase 9J does not define an `ALLOW_EXECUTION` decision. Any later execution
decision requires a separate implementation approval and a separate approval
for the guarded side effect itself.

## Stop Conditions

A future caller must return or record a stop decision before side effects when
any of these conditions are true:

- `schema_version` is not the current approved no-op schema version.
- `mode` is not `no_op`.
- `status` is `BLOCKED`, `NOT_RUN`, `ENVIRONMENT_BLOCKED`, missing, malformed,
  or unknown.
- `reason_code` is missing, malformed, unknown, or policy-blocking.
- `side_effect_requested` is anything other than `none` unless a later task
  separately defines and approves an execution path.
- `approval_ref_present` is false for a side-effect request.
- `evidence_refs` contains missing, malformed, absolute, traversal,
  out-of-scope, private, raw, or non-repo-relative evidence.
- `performed_actions` is non-empty.
- `safe_task_summary`, `safety_notes`, or `next_step` contains forbidden raw,
  private, live, local-path, command-log, tool-call, account, secret, IP, port,
  config, device, or downstream content.

The caller must not fall back to looser parsing, broader filesystem access,
tool execution, external calls, or generated evidence when a stop condition is
encountered.

## Persistence And Cleanup

By default, a future caller must keep the Hermes result in memory only. It must
not write receipt files, trace files, audit logs, raw command logs, generated
reports, digest artifacts, release artifacts, or downstream evidence.

If a later task approves persistence, that task must name the exact output path,
schema, retention expectation, redaction rule, cleanup rule, and verification
command. Persisted output must remain sanitized and must not include raw
prompts, private data, raw command logs, unredacted tool-call bodies, secrets,
account values, IPs, ports, live config, device values, local absolute paths,
private raw corpus, `08_Study` raw notes, RSID raw evidence, downstream raw
evidence, or generated downstream source.

Temporary files, if ever approved, must be exact-path scoped and removed or
reported before closeout.

## Verification Requirements

Any future caller implementation must include focused synthetic tests before it
is used for real side effects. Those tests must cover:

- advisory/no-side-effect output remains advisory only;
- missing side-effect approval returns a stop decision;
- approved side-effect requests still stop when no executor is approved;
- unsafe input and unsafe evidence stop without echoing forbidden content;
- unexpected `schema_version`, `mode`, `status`, `reason_code`, or field shape
  stops;
- non-empty `performed_actions` stops;
- evidence outside the active approval scope stops;
- no tool, MCP, Git, release, audit, external, downstream, persistent-process,
  or artifact side effect occurs during tests.

Full repository verification remains the existing local quality gate and test
suite unless a later owner-approved task names narrower or broader commands.

## Non-goals

Phase 9J does not:

- implement a preflight caller or wrapper;
- change `scripts/hermes_sidecar.py`;
- add a machine-readable JSON Schema artifact;
- connect Hermes to MCP, quality gates, CI, audit automation, release
  automation, AgentOps, memory, external services, or downstream repositories;
- execute tools, start servers, create background processes, stage changes,
  commit changes, push changes, tag releases, publish releases, upload
  artifacts, or mutate downstream repositories;
- generate receipt, trace, audit log, digest, release, or downstream evidence
  files;
- persist raw prompts, private data, raw command logs, model outputs,
  unredacted tool-call bodies, secrets, account values, IPs, ports, live
  config, device values, local absolute paths, private raw corpus, `08_Study`
  raw notes, RSID raw evidence, downstream raw evidence, or generated
  downstream source.

## Decision

Phase 9J is accepted as `PASS WITH NOTES` when this boundary document and
focused synthetic tests pass local verification.

The next safe Hermes step after Phase 9J is to commit and push this boundary
record, then run clean Local Verify. Any later preflight caller implementation
remains separately approval-gated and must name exact files, commands, result
fields, persistence rules, cleanup rules, verification commands, and forbidden
side effects.
