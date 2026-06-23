# Hermes Sidecar Implementation Boundary

## Purpose

Record the Phase 9C implementation boundary for a possible future Hermes
sidecar.

Phase 9C is documentation-only. It translates the Phase 9A planning contract
and Phase 9B synthetic review into an implementation boundary that must be
satisfied before any minimal sidecar runtime is approved.

This document does not implement the sidecar.

## Scope

Allowed in Phase 9C:

- define the smallest future no-op sidecar shape;
- define allowed and forbidden inputs;
- define bounded output and reason-code expectations;
- define approval gates for side effects;
- define future synthetic test expectations;
- preserve the relationship to the MCP tool boundary, JSON evidence, local RAG,
  retrieval receipt evidence, and repository safety policy.

Not allowed in Phase 9C:

- Hermes sidecar runtime;
- background daemon, service manager, scheduler, socket server, HTTP server, or
  always-on process;
- MCP runtime, MCP server, tool execution, or tool-call dispatch;
- quality-gate or CI integration;
- audit automation, real receipt generation, trace-event generation, or log
  writing;
- retrieval expansion, persistent index, corpus folder, retrieval folder, or
  embeddings;
- external service calls, network brokers, live endpoints, PLC/device/account
  integration, or downstream repository mutation;
- AgentOps, memory runtime, persistent execution state, or hidden background
  state;
- artifact, digest, release evidence, tag, publication, upload, or release
  generation;
- dependency changes.

## Boundary Basis

Any future sidecar implementation remains downstream of:

- `docs/MCP_TOOL_BOUNDARY_CONTRACT.md`;
- `docs/HERMES_SIDECAR_PLANNING_CONTRACT.md`;
- `docs/HERMES_SIDECAR_SYNTHETIC_REVIEW.md`;
- `docs/JSON_EVIDENCE_POLICY.md`;
- `docs/AUDIT_TRACE_SCHEMA.md`;
- `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md`;
- `docs/RETRIEVAL_RECEIPT_EVIDENCE_PLAN.md`;
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`;
- `docs/SAFETY_POLICY.md`.

If these documents conflict, the future sidecar must follow the narrower and
safer rule unless a later owner-approved task updates the contract explicitly.

## Minimal Future Runtime Shape

A separately approved future runtime, if created, should start as a local,
standard-library-first, no-op coordinator.

The smallest acceptable runtime would:

- accept only explicit local task metadata;
- perform policy checks before proposing any action;
- produce dry-run plans and bounded status summaries;
- return reason-coded blocked results when approval, evidence, source basis, or
  safety boundaries are missing;
- reference existing repo-relative evidence paths, receipt identifiers, trace
  identifiers, commit hashes, and content hashes;
- avoid background execution by default.

The first runtime must not execute tools, mutate files, stage commits, push,
publish, upload, call external services, start a persistent server, generate
receipts, write traces, refresh digests, or create release artifacts unless a
later task approves exact files, commands, artifacts, cleanup rules, and
verification.

## Input Contract

Allowed future input classes:

| input class | boundary |
|---|---|
| task summary | Sanitized short summary only; not a raw prompt transcript. |
| repository basis | Repo-relative paths, commit hashes, digest hashes, receipt ids, and trace ids only. |
| approval reference | Explicit reference for one side-effect class and target only. |
| dry-run options | Bounded local options such as max results, output format, or no-op mode. |
| evidence references | Existing safe summaries, schema identifiers, and repo-relative evidence paths. |

Forbidden future input classes:

- raw prompts, private data, raw command logs, model output transcripts, or
  unredacted tool-call bodies;
- secrets, credentials, tokens, account values, IPs, ports, live endpoints,
  live config, device values, or local absolute paths;
- private raw corpus, `08_Study` raw notes, RSID raw evidence, or downstream raw
  evidence;
- hidden environment state that is not surfaced in the task contract;
- unapproved downstream repository files.

If the sidecar cannot proceed without forbidden input, it must return a blocked
or no-sufficient-evidence result.

## Output Contract

Allowed future output classes:

- `PASS`, `PASS_WITH_NOTES`, `BLOCKED`, `NOT_RUN`, `ENVIRONMENT_BLOCKED`,
  `NO_SUFFICIENT_EVIDENCE`, and `FAIL`;
- safe reason codes;
- short safe summaries;
- repo-relative evidence paths;
- receipt identifiers, trace identifiers, commit hashes, digest hashes, and
  SHA-256 hashes;
- counts and bounded status fields;
- exact next approval or evidence needed.

Forbidden future output classes:

- raw prompt transcripts;
- private data;
- raw command logs;
- unredacted tool-call bodies;
- secrets, account values, IPs, ports, live config, device values, local
  absolute paths, or live target details;
- generated downstream source unless separately approved by the downstream task.

## Failure Taxonomy

Future sidecar result reasons should be narrow and fail-closed:

| reason code | meaning |
|---|---|
| `approval_blocked` | The requested side effect lacks explicit approval for the exact class, target, command, output, cleanup, or verification. |
| `policy_blocked` | Repository policy forbids the requested input, output, command, artifact, integration, or side effect. |
| `source_basis_blocked` | Required repo basis, digest basis, receipt id, trace id, or commit evidence is missing, stale, or unsafe. |
| `environment_blocked` | The local environment prevents an approved command from running. |
| `verification_failed` | An executed check failed. |
| `scope_conflict` | The requested work crosses the active task scope or allowed file list. |
| `unsafe_input` | The request depends on forbidden raw, private, live, secret, or local absolute path data. |
| `insufficient_evidence` | Safe local evidence is not enough for a reliable advisory answer. |
| `external_permission_missing` | Network, external service, downstream, release, publication, or live-target permission is missing. |

These reason codes do not authorize implementation. They define the language a
future sidecar should use when it refuses or stops.

## Approval Gates

A future task must separately approve any side effect. Approval must name:

- exact files, commands, scripts, or directories;
- whether the operation is read-only, dry-run, temporary write, commit
  candidate, push, publication, or external call;
- allowed output paths;
- cleanup rules;
- verification commands;
- forbidden inputs and forbidden outputs;
- whether generated artifacts may be created, committed, uploaded, or published.

Approval for one side-effect class does not authorize another. For example,
approval to create a no-op runtime file does not authorize MCP tool execution,
quality-gate integration, CI integration, receipt generation, digest refresh,
git commit, push, release publication, downstream edits, or external calls.

## Future Test Expectations

Before any runtime is accepted, a later task should add focused synthetic tests
that prove:

- default behavior is no-op and advisory;
- forbidden raw, private, live, secret, local absolute path, and downstream
  inputs are rejected;
- missing approval returns `approval_blocked`;
- unsafe policy requests return `policy_blocked` or `unsafe_input`;
- missing or stale source basis returns `source_basis_blocked`;
- output uses safe summaries, identifiers, hashes, counts, and reason codes;
- no background process, daemon, scheduler, socket server, or HTTP server is
  started;
- no MCP runtime, MCP tool execution, quality-gate integration, CI integration,
  audit automation, artifact generation, external call, release automation, or
  downstream mutation occurs by default.

Any runtime task should also keep tests synthetic unless the owner separately
approves real repository side effects and cleanup rules.

## Non-goals

Phase 9C does not:

- create `scripts/hermes_sidecar.py` or any equivalent runtime entrypoint;
- create a sidecar package, service file, socket server, HTTP server, scheduler,
  or background process;
- modify `scripts/quality_gate.py`;
- modify GitHub Actions workflows;
- create real receipt, trace, log, digest, release, retrieval, or downstream
  artifacts;
- add dependencies;
- call external services;
- change local RAG, MCP, audit, eval, release, or downstream behavior.

## Next Step

After this document is committed and clean Local Verify passes, the next
separately approved Phase 9 task may define exact files and tests for a minimal
no-op Hermes sidecar runtime. That future task must still keep runtime behavior
local-only, no-op by default, fail-closed, and disconnected from MCP execution,
quality gates, CI, audit automation, release automation, external services, and
downstream mutation unless those connections are separately approved.
