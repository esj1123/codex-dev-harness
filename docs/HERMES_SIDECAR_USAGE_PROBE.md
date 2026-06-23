# Hermes Sidecar Usage Probe

## Purpose

Record the Phase 9D.1 usage probe for the minimal no-op Hermes sidecar.

This probe reviews observable behavior of `scripts/hermes_sidecar.py` after the
Phase 9D clean Local Verify. It does not expand the sidecar runtime and does
not authorize execution behavior.

## Scope

Allowed in this probe:

- run the sidecar in no-op JSON mode;
- check advisory no-side-effect behavior;
- check side-effect approval blocking;
- check approved side-effect requests remain `NOT_RUN`;
- check unsafe input is blocked without echoing the unsafe material;
- check missing evidence references fail closed;
- document safe summarized results.

Not allowed in this probe:

- changing `scripts/hermes_sidecar.py`;
- changing tests;
- wiring the sidecar into `scripts/quality_gate.py` or CI;
- MCP runtime, MCP tool execution, or tool dispatch;
- audit automation, real receipt generation, trace generation, or log writing;
- artifact, digest, release, tag, publication, or upload generation;
- external service calls;
- AgentOps, memory runtime, background process, scheduler, socket server, or
  HTTP server;
- downstream repository mutation.

## Probe Matrix

| probe | expected behavior | observed status | observed reason_code | notes |
|---|---|---|---|---|
| advisory no-op request with existing evidence path | Return bounded advisory JSON and perform no action. | `PASS_WITH_NOTES` | `insufficient_evidence` | Evidence path was repo-relative and existed. |
| file-write side effect without approval | Fail closed before any action. | `BLOCKED` | `approval_blocked` | `performed_actions` stayed empty. |
| file-write side effect with approval reference | Record boundary but still do not execute. | `NOT_RUN` | `policy_blocked` | v0 has no executor path. |
| unsafe raw/transcript-like input | Block and replace the summary with a safe placeholder. | `BLOCKED` | `unsafe_input` | Unsafe input was not echoed in the result. |
| missing evidence reference | Block on source basis. | `BLOCKED` | `source_basis_blocked` | Missing path was not treated as evidence. |

## Safety Findings

- All probe commands exited successfully while returning no-op JSON.
- Every result kept `mode` as `no_op`.
- Every result kept `performed_actions` as an empty list.
- No file write, tool execution, background process, network call, artifact
  generation, release action, or downstream mutation occurred.
- Side-effect approval text was not treated as permission to execute.
- Unsafe input was summarized only as `[blocked unsafe input]`.
- Missing evidence did not fall back to broader filesystem inspection.

## Verification

Local verification for this probe should include:

- `python scripts/quality_gate.py`
- `python -m pytest tests`
- `git diff --check`

Clean GitHub Actions Local Verify evidence should be recorded separately after
this documentation-only probe is committed and pushed.

## Decision

Phase 9D.1 is accepted as `PASS WITH NOTES`.

The minimal Hermes sidecar remains a standalone no-op classifier. Additional
Hermes work still requires separate owner approval and exact files, commands,
tests, cleanup rules, integration targets, and forbidden scope. By default, no
MCP execution, background service behavior, quality-gate or CI integration,
audit automation, release automation, external service, memory/AgentOps
behavior, or downstream integration is authorized.
