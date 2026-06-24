# Hermes Preflight Synthetic Matrix Review

## Purpose

Record the Phase 9I synthetic review of how a future approved caller should
interpret Hermes no-op sidecar results before any side-effecting step.

Phase 9I is documentation and focused synthetic-test only. It does not
implement a caller, wrapper, MCP runtime, tool execution bridge, server,
quality-gate hook, CI hook, audit automation, real receipt generation, real log
or trace writing, machine-readable schema artifact, artifact generation, digest
refresh, release automation, external service call, AgentOps or memory
runtime, or downstream integration.

## Review Basis

This review is based on:

- `docs/HERMES_PREFLIGHT_USE_PLANNING_CONTRACT.md`
- `docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md`
- `docs/HERMES_MCP_SECURITY_ALIGNMENT_REVIEW.md`
- `docs/MCP_TOOL_BOUNDARY_CONTRACT.md`
- `scripts/hermes_sidecar.py`

If a future caller sees a result that conflicts with these documents, the
caller must apply the narrower and safer rule and stop before side effects.

## Caller Decision Rule

A future caller may use a Hermes result as preflight context only. The caller
must not treat a result as permission to execute tools, write files, stage or
commit changes, push, generate artifacts, call external services, start
background work, create audit evidence, publish releases, or mutate downstream
repositories.

The caller decision should be:

- `ADVISORY_ONLY` when the result is the current no-side-effect advisory shape;
- `STOP` when the result is blocked, not run, environment blocked, malformed,
  unexpected, or outside the approved task scope.

No current result authorizes side-effect execution.

## Synthetic Decision Matrix

| case | representative result | future caller decision | reason |
|---|---|---|---|
| advisory/no side-effect request | `status=PASS_WITH_NOTES`, `side_effect_requested=none`, `performed_actions=[]` | `ADVISORY_ONLY` | Planning context only; no execution is requested or authorized. |
| missing approval for side-effect request | `status=BLOCKED`, `reason_code=approval_blocked` | `STOP` | Side-effect approval reference is missing. |
| approval present but executor absent | `status=NOT_RUN`, `reason_code=policy_blocked`, `approval_ref_present=true` | `STOP` | The no-op sidecar records the request boundary only; a separate executor task is still required. |
| unsafe/private/raw input | `status=BLOCKED`, `reason_code=unsafe_input` | `STOP` | Input is forbidden or unsafe and must not be echoed or acted on. |
| invalid or out-of-scope evidence path | `status=BLOCKED`, `reason_code=unsafe_input` or `source_basis_blocked` | `STOP` | Evidence is not an accepted safe repo-relative basis for action. |
| unexpected `schema_version` | any result with a schema version other than `hermes_sidecar_noop.v0` | `STOP` | Schema drift requires separate contract approval. |
| unexpected `mode` | any result with a mode other than `no_op` | `STOP` | Current preflight review only covers no-op output. |
| unexpected `status` | any result outside `PASS_WITH_NOTES`, `BLOCKED`, `NOT_RUN`, or `ENVIRONMENT_BLOCKED` | `STOP` | New status values require separate approval and interpretation rules. |
| non-empty `performed_actions` | any result with recorded actions | `STOP` | v0 must perform no actions; any action record is a contract violation. |
| evidence refs outside approved scope | any accepted-looking `evidence_refs` path outside the current approved task scope | `STOP` | Even safe repo-relative evidence must remain inside the active approval scope. |
| future side-effect request | any request that would execute after preflight | `STOP` until separately approved | Preflight approval context and execution approval remain separate. |

## Synthetic Result Checks

The focused Phase 9I tests should confirm:

- the matrix documents every required representative decision case;
- advisory no-side-effect output remains advisory only;
- missing side-effect approval blocks;
- approved side-effect requests remain `NOT_RUN`;
- unsafe input and invalid evidence stop the future caller;
- unexpected `schema_version`, `mode`, or `status` stops the future caller;
- non-empty `performed_actions` stops the future caller;
- evidence references outside an approved synthetic scope stop the future
  caller;
- side-effect execution still requires separate approval after preflight.

These checks may call the existing no-op classifier in memory and may construct
synthetic mutated result objects. They must not implement a production caller,
start servers, execute tools, write artifacts, create audit evidence, call
external services, wire quality gates or CI, or change sidecar runtime
behavior.

## Non-goals

Phase 9I does not:

- implement a preflight caller or wrapper;
- modify `scripts/hermes_sidecar.py`;
- add a machine-readable JSON Schema artifact;
- connect Hermes to MCP, quality gates, CI, audit automation, release
  automation, AgentOps, memory, external services, or downstream repositories;
- persist raw prompts, private data, raw command logs, model outputs,
  unredacted tool-call bodies, secrets, account values, IPs, ports, live
  config, device values, local absolute paths, private raw corpus, `08_Study`
  raw notes, RSID raw evidence, downstream raw evidence, or generated
  downstream source.

## Decision

Phase 9I is accepted as `PASS WITH NOTES` when this review and focused
synthetic tests pass local verification.

The next safe Hermes task after Phase 9I is to commit and push the matrix
review, then run clean Local Verify. Any later implementation of an actual
preflight caller remains separately approval-gated and must name exact files,
commands, result fields, persistence rules, cleanup rules, and verification
commands.
