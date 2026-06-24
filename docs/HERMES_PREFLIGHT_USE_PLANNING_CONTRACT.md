# Hermes Preflight Use Planning Contract

## Purpose

Record the Phase 9H planning contract for using the minimal no-op Hermes
sidecar as a future preflight check before side effects.

Phase 9H is documentation-only. It does not change `scripts/hermes_sidecar.py`,
add tests, execute MCP tools, start servers, write artifacts, create audit
records, generate receipts, write traces or logs, refresh digests, publish
releases, call external services, add AgentOps or memory behavior, wire
quality-gate or CI integration, or edit downstream repositories.

## Basis

This contract depends on:

- `scripts/hermes_sidecar.py`
- `docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md`
- `docs/HERMES_RESULT_SCHEMA_ARTIFACT_DECISION.md`
- `docs/HERMES_MCP_SECURITY_ALIGNMENT_REVIEW.md`
- `docs/MCP_TOOL_BOUNDARY_CONTRACT.md`
- `docs/JSON_EVIDENCE_POLICY.md`

The sidecar remains a standalone no-op classifier. A preflight caller may use
its result as policy and approval context only. The result does not execute the
requested action and does not grant permission to bypass the active task
contract.

## Intended Future Use

A future approved caller may run Hermes before a side-effecting step to answer:

- Is the task summary bounded and sanitized?
- Is the requested side-effect class known?
- Is a side-effect approval reference present when required?
- Are evidence paths repo-relative, existing, and safe?
- Does the no-op result say the request is blocked, not run, or only advisory?
- What exact approval or evidence is still needed?

The preflight result is advisory and fail-closed. It may stop a later step, but
it must not silently authorize a later step.

## Preflight Flow

The future preflight sequence should be:

1. Caller prepares a short sanitized task summary, requested side-effect class,
   optional approval reference, and optional repo-relative evidence paths.
2. Caller invokes the no-op sidecar and captures the JSON result in memory or a
   temporary test fixture only when separately approved.
3. Caller checks `schema_version`, `mode`, `status`, `reason_code`,
   `side_effect_requested`, `approval_ref_present`, `evidence_refs`,
   `performed_actions`, and `next_step`.
4. Caller treats any `BLOCKED`, `NOT_RUN`, `ENVIRONMENT_BLOCKED`, unsafe input,
   missing evidence, or unknown side-effect result as a stop condition for real
   side effects.
5. Caller proceeds to a side effect only when a later task separately approves
   an executor, exact command, exact target, cleanup rule, and verification
   rule.

In the current repository state, step 5 has no implementation path.

## Allowed Future Caller Inputs

Future callers may pass only:

- short sanitized task summaries;
- documented side-effect classes;
- bounded approval reference ids;
- safe repo-relative evidence paths;
- bounded local options such as JSON output mode.

Future callers must not pass raw prompts, private data, raw command logs,
model output transcripts, unredacted tool-call bodies, secrets, credentials,
tokens, account values, IPs, ports, live endpoints, live config, device values,
local absolute paths, private raw corpus, `08_Study` raw notes, RSID raw
evidence, downstream raw evidence, or generated downstream source.

## Stop Conditions

A future caller must stop before side effects when Hermes returns:

- `BLOCKED`;
- `NOT_RUN`;
- `ENVIRONMENT_BLOCKED`;
- `reason_code` of `approval_blocked`, `policy_blocked`, `unsafe_input`,
  `source_basis_blocked`, `scope_conflict`, or `environment_blocked`;
- non-empty `performed_actions`;
- unexpected `schema_version`;
- unexpected `mode`;
- evidence references outside the approved task scope.

For v0, `performed_actions` must always be empty. A non-empty value is a
contract violation and must stop the caller.

## Non-goals

Phase 9H does not:

- implement a preflight caller;
- add a wrapper script;
- add a quality-gate hook;
- add a CI workflow hook;
- add a machine-readable schema artifact;
- create real receipts, traces, logs, digests, release artifacts, or
  downstream outputs;
- execute MCP tools;
- start MCP or Hermes servers;
- call external services;
- authorize automated staging, committing, pushing, tagging, publishing,
  uploading, or releasing anything.

## Future Approval Requirements

Any later implementation of a preflight caller must name:

- exact caller file or script;
- exact side-effect class in scope;
- exact command or action that would be guarded;
- exact result fields checked;
- whether results may be persisted, and where;
- cleanup rules for temporary outputs;
- verification commands;
- forbidden inputs and forbidden outputs;
- whether failure is advisory or blocking.

Approval to implement a preflight caller does not authorize the guarded side
effect itself. Approval to run a side effect must remain separate.

## Decision

Phase 9H is accepted as `PASS WITH NOTES` when this planning contract is
committed and local verification passes.

The next safe Hermes task after Phase 9H is a synthetic preflight matrix review
that documents representative caller decisions without adding a caller,
executing tools, starting servers, writing artifacts, or wiring Hermes into
quality gates or CI.
