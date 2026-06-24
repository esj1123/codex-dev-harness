# Hermes Git Push Preflight Caller Selection Review

## Purpose

Record the Phase 9K selection review for the first possible Hermes preflight
caller candidate.

Phase 9K is documentation and focused synthetic-test only. It does not
implement a caller, wrapper, execution bridge, MCP runtime, tool server,
quality-gate hook, CI hook, audit automation, real receipt generation, real log
or trace writing, machine-readable schema artifact, artifact generation, digest
refresh, release automation, external service call, AgentOps or memory runtime,
or downstream integration.

The question for this phase is whether the first actual preflight caller
candidate should be selected now, and if so which single side-effect class is
safe enough to plan next.

## Basis

This review depends on:

- `docs/HERMES_PREFLIGHT_USE_PLANNING_CONTRACT.md`
- `docs/HERMES_PREFLIGHT_SYNTHETIC_MATRIX_REVIEW.md`
- `docs/HERMES_PREFLIGHT_CALLER_IMPLEMENTATION_BOUNDARY.md`
- `docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md`
- `scripts/hermes_sidecar.py`

The current Hermes sidecar remains a standalone no-op classifier. A selected
candidate does not authorize implementation and does not authorize the guarded
side effect.

## Candidate Matrix

| side-effect class | selection | reason |
|---|---|---|
| `git_push` | selected first candidate | Push mutates remote state, is frequent in the current workflow, has a clear approval boundary, and can be preflighted without executing the push. |
| `git_commit` | defer | Commit mutates local history and is important, but it is less externally visible than push and should not be the first caller. |
| `artifact_generation` | defer | Artifact creation has path and retention risks, but current artifact work remains separately approval-gated and should not be coupled to Hermes first. |
| `mcp_tool_execution` | defer | MCP execution is broader and higher-risk; it should wait until a narrower caller pattern is proven. |
| `audit_generation` | defer | Audit generation would cross into evidence automation and real receipt/log boundaries, which remain out of scope. |
| `external_call` | defer | External calls require network and target-specific approval boundaries beyond the current local-only Hermes surface. |
| `release_publication` | defer | Release publication is high-impact and belongs after release automation/provenance boundaries are separately approved. |
| `downstream_mutation` | defer | Downstream mutation requires downstream repo rules and exact target approvals, so it is not a first Hermes caller candidate. |
| `persistent_process` | defer | Background or persistent processes remain outside the current no-op sidecar model. |

## Decision

Decision: `select_git_push_preflight_candidate`.

The first future caller candidate should be a standalone dry-run preflight
around the `git_push` side-effect class.

The later implementation candidate, if separately approved, should use:

- candidate script: `scripts/hermes_git_push_preflight.py`;
- candidate tests: `tests/test_hermes_git_push_preflight.py`;
- side-effect class: `git_push`;
- default output: stdout summary or JSON only;
- persistence: memory-only by default;
- integration: none by default;
- execution authority: none.

This review does not create those files.

## Required Future Behavior

A later `git_push` preflight caller must:

- inspect the current no-op Hermes result fields listed in
  `docs/HERMES_PREFLIGHT_CALLER_IMPLEMENTATION_BOUNDARY.md`;
- use fail-closed decisions only: `STOP` or `ADVISORY_ONLY`;
- never define `ALLOW_EXECUTION` in its first implementation;
- never run `git push`;
- never run `git add`, `git commit`, `git tag`, or release commands;
- never dispatch workflows, upload artifacts, publish releases, call external
  services, execute MCP tools, or mutate downstream repositories;
- keep any Hermes result memory-only unless a later task approves an exact
  sanitized output path and cleanup rule;
- stop on missing approval, unsafe input, invalid evidence, unexpected schema,
  unexpected mode, unexpected status, non-empty `performed_actions`, or
  out-of-scope evidence references.

The caller may only answer whether a human should stop before a separately
approved push step.

## Approval Requirements For Phase 9L

Any Phase 9L implementation approval must name:

- exact script path;
- exact test path;
- exact CLI arguments;
- exact result fields checked;
- exact synthetic fixtures;
- whether JSON output is allowed;
- whether any output may be persisted;
- cleanup rules for temporary outputs;
- verification commands;
- explicit non-goals for `git push`, staging, commit, tag, release, workflow
  dispatch, artifact upload, MCP execution, audit automation, external calls,
  persistent processes, downstream mutation, and dependency changes.

Approval to implement the dry-run preflight caller must not authorize a real
push. Approval to push must remain separate and explicit.

## Non-goals

Phase 9K does not:

- create `scripts/hermes_git_push_preflight.py`;
- create `tests/test_hermes_git_push_preflight.py`;
- implement a preflight caller or wrapper;
- change `scripts/hermes_sidecar.py`;
- connect Hermes to `scripts/quality_gate.py`, CI, MCP, audit automation,
  release automation, AgentOps, memory, external services, or downstream
  repositories;
- run `git push`, `git add`, `git commit`, `git tag`, release publication,
  workflow dispatch, artifact upload, MCP execution, external calls, audit
  generation, receipt generation, trace writing, or downstream mutation;
- generate or regenerate artifacts, digests, receipts, traces, logs, release
  files, or downstream evidence;
- persist raw prompts, private data, raw command logs, model outputs,
  unredacted tool-call bodies, secrets, account values, IPs, ports, live
  config, device values, local absolute paths, private raw corpus, `08_Study`
  raw notes, RSID raw evidence, downstream raw evidence, or generated
  downstream source.

## Verification

Phase 9K is accepted as `PASS WITH NOTES` when this review and focused
documentation tests pass local verification.

The next safe Hermes step after Phase 9K is to commit and push this selection
review, then run clean Local Verify. If that passes, the owner may separately
approve Phase 9L as a minimal standalone dry-run git-push preflight caller, or
may stop at the documented boundary.
