# Hermes Git Push Preflight Usage Probe

## Purpose

Record the Phase 9N usage probe for the standalone dry-run Hermes git-push
preflight caller.

This probe reviews observable behavior of
`scripts/hermes_git_push_preflight.py` after the Phase 9M output contract
passed clean Local Verify. It does not expand caller runtime behavior and does
not authorize `git push` execution.

## Scope

Allowed in this probe:

- run the standalone caller in JSON dry-run mode;
- review missing-approval behavior;
- review approved-but-not-executable behavior;
- review unsafe input blocking;
- review invalid or missing evidence behavior;
- review out-of-scope evidence handling through synthetic interpretation;
- confirm stdout JSON remains a decision record, not an execution receipt;
- document safe summarized results.

Not allowed in this probe:

- changing `scripts/hermes_git_push_preflight.py`;
- changing `scripts/hermes_sidecar.py`;
- running `git push`, `git add`, `git commit`, `git tag`, workflow dispatch,
  artifact upload, release publication, or downstream mutation;
- wiring the caller into `scripts/quality_gate.py` or CI;
- MCP runtime, MCP tool execution, tool dispatch, or server startup;
- audit automation, real receipt generation, trace generation, or log writing;
- artifact, digest, release, tag, publication, or upload generation;
- external service calls;
- AgentOps, memory runtime, background process, scheduler, socket server, or
  HTTP server.

## Probe Matrix

| probe | expected behavior | observed caller decision | observed reason_code | notes |
|---|---|---|---|---|
| git-push request without approval reference | Stop before any guarded command. | `STOP` | `approval_blocked` | Underlying Hermes result blocks side-effect request without approval. |
| git-push request with approval reference and existing evidence | Stop because no executor is approved. | `STOP` | `executor_not_approved` | Underlying Hermes result is `NOT_RUN`; approval context is not execution authority. |
| unsafe raw or local-path-like task summary | Block without echoing unsafe material. | `STOP` | `unsafe_input` | Caller returns `[blocked unsafe input]` as the safe task summary. |
| missing evidence path | Stop on source-basis failure. | `STOP` | `source_basis_blocked` | Missing path is not accepted as evidence. |
| parent traversal evidence path | Stop before broad filesystem access. | `STOP` | `unsafe_input` | Unsafe evidence path is rejected by the underlying sidecar boundary. |
| accepted-looking evidence outside caller-approved scope | Stop during caller interpretation. | `STOP` | `evidence_scope_blocked` | The caller does not trust Hermes evidence references unless they match the approved caller scope. |
| CLI invocation with JSON flag | Emit parseable stdout JSON and no stderr. | `STOP` | `executor_not_approved` | JSON output is a preflight decision record only. |

## Safety Findings

- Every probe outcome stays fail-closed with `decision` set to `STOP`.
- Every probe outcome keeps `would_run_git_push` as `false`.
- Every probe outcome keeps top-level `performed_actions` as an empty list.
- Approval references are boundary context only; they do not authorize an
  executor or the guarded push.
- The caller does not run Git commands, stage files, commit, tag, dispatch
  workflows, upload artifacts, publish releases, write receipts, write traces,
  write audit logs, call MCP tools, call external services, start servers, or
  mutate downstream repositories.
- Unsafe input is summarized by safe placeholder text and is not echoed.
- Evidence references remain bounded to explicitly supplied repo-relative
  paths and are not used to broaden filesystem access.

## Verification

Local verification for this probe should include:

- `python -m pytest tests/test_hermes_git_push_preflight_usage_probe.py`
- `python scripts/hermes_git_push_preflight.py --task-summary "Push Phase 9N usage probe" --approval-ref phase-9n-owner-approval --evidence-path STATUS.md --json`
- `python scripts/quality_gate.py`
- `python -m pytest tests`
- `git diff --check`

Clean GitHub Actions Local Verify evidence should be recorded separately after
this documentation and focused-test probe is committed and pushed.

## Decision

Phase 9N is accepted as `PASS WITH NOTES` when this probe document and focused
synthetic tests pass local verification.

The standalone git-push preflight caller remains a dry-run fail-closed wrapper.
The next Hermes step should be separately approved before any output
persistence, receipt/trace linkage, quality-gate or CI integration, MCP
execution, audit automation, release automation, external service call,
AgentOps or memory behavior, downstream integration, or real `git push`
execution is considered.
