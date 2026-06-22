# Hermes Sidecar Planning Contract

## Purpose

This document records the Phase 9A planning contract for a possible future
Hermes sidecar.

Phase 9A is documentation-only. It defines the boundary, approval model, input
and output rules, failure behavior, and relationship to the MCP tool boundary
before any sidecar runtime is implemented.

## Current Scope

This contract may be used to plan later implementation work. It does not
authorize implementation.

Allowed in Phase 9A:

- document the sidecar responsibility model;
- document local-first constraints;
- document approval and no-op boundaries;
- document safe input and output evidence shapes;
- document failure modes and future verification expectations.

Not implemented in Phase 9A:

- Hermes sidecar runtime;
- background daemon, service manager, scheduler, socket server, or HTTP server;
- MCP runtime, MCP server, tool execution, or tool-call dispatch;
- quality-gate or CI integration;
- audit automation, real receipt generation, or real trace/log writing;
- external service call, network broker, or live endpoint integration;
- PLC, device, account, downstream repository, or release mutation;
- AgentOps, memory runtime, or persistent execution state;
- artifact, digest, release evidence, tag, publication, or upload generation;
- dependency changes.

## Relationship To Existing Boundaries

The sidecar must remain downstream of the MCP tool boundary. A future sidecar
cannot widen the allowed MCP tool classes, input rules, output rules, approval
rules, redaction rules, or evidence hooks defined by
`docs/MCP_TOOL_BOUNDARY_CONTRACT.md`.

The sidecar must also remain consistent with:

- `docs/SAFETY_POLICY.md`;
- `docs/AUDIT_TRACE_SCHEMA.md`;
- `docs/JSON_EVIDENCE_POLICY.md`;
- `docs/EVAL_REPORT_INTEGRATION_PLAN.md`;
- `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md`;
- `docs/RETRIEVAL_RECEIPT_EVIDENCE_PLAN.md`;
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`.

If those documents conflict with a future sidecar behavior, the safer and more
restrictive rule applies until the owner explicitly approves a narrower update.

## Responsibility Model

A future Hermes sidecar may coordinate local planning around already-approved
work. Its responsibility should be limited to:

- reading explicit local request metadata from approved inputs;
- checking policy boundaries before any proposed action;
- producing dry-run plans and bounded status summaries;
- referencing existing repo-relative evidence paths, commit identifiers, and
  hash identifiers;
- reporting fail-closed outcomes when evidence is missing, unsafe, stale, or
  outside the approved task contract.

A future sidecar must not become an implicit task runner. It must not infer
approval from prior tasks, perform hidden background work, or bypass user
approval, repository policy, downstream repository rules, or safety invariants.

## Input Boundary

Allowed future inputs should be explicit, bounded, and local:

- repo-relative paths to approved repository files;
- existing receipt or trace identifiers;
- commit hashes or documented artifact hashes;
- sanitized task summaries;
- owner approval references for a specific side effect;
- dry-run configuration values that do not expose live targets or secrets.

Forbidden inputs include:

- raw prompts, private data, raw command logs, model output transcripts, or
  unredacted tool-call bodies;
- secrets, credentials, tokens, account values, IPs, ports, live config, device
  values, or local absolute paths;
- private raw corpus, `08_Study` raw notes, RSID raw evidence, or downstream raw
  evidence;
- unapproved downstream repository files;
- hidden environment state that is not surfaced in the task contract.

## Output Boundary

Future sidecar output should be evidence-oriented and bounded:

- `PASS`, `PASS WITH NOTES`, `BLOCKED`, `NOT RUN`, `ENVIRONMENT BLOCKED`, or
  `FAIL`-style status values;
- repo-relative evidence paths;
- commit hashes and content hashes;
- counts, redacted summaries, and reason codes;
- explicit approval state for side effects;
- safe next-step recommendations.

Future sidecar output must not persist raw prompts, private data, raw command
logs, unredacted tool-call bodies, secrets, account values, IPs, ports, live
config, device values, local absolute paths, or generated downstream source.

## Approval Boundary

The sidecar may not treat planning, dry-run output, documentation approval, or
previous task approval as permission to perform a side effect.

Separate explicit approval is required for any future behavior that would:

- write files;
- stage, commit, push, tag, publish, upload, or release;
- run external network calls;
- call or execute MCP tools;
- mutate a downstream repository;
- generate audit receipts, trace events, logs, digests, or release artifacts;
- start a persistent process or background service.

Approval must be specific to the side effect, target, expected output, cleanup
rule, and verification rule.

## Failure And No-op Behavior

The default sidecar behavior must be no-op. If the requested action is outside
the current approval, the sidecar should return a blocked or not-run result
instead of attempting a partial action.

Expected future failure categories:

- `blocked`: policy, approval, source-basis, or safety boundary prevents action;
- `not_run`: the requested verification or side effect was not executed;
- `environment_blocked`: the local runtime cannot execute the requested command;
- `no_sufficient_evidence`: available local evidence is insufficient for a
  reliable advisory answer;
- `fail`: evidence contradicts the requirement or a check fails.

Failure output should include the minimum safe summary needed to explain the
state and the next approval or evidence needed.

## Future Verification Expectations

A later implementation task should add focused synthetic tests before any real
sidecar behavior is connected to workflows. Those tests should cover:

- dry-run only behavior;
- fail-closed approval handling;
- forbidden input rejection;
- bounded output and redaction;
- no background process or always-on service;
- no external call by default;
- no MCP runtime or tool execution unless separately approved;
- no quality-gate, CI, release, audit, or downstream integration by default.

Real repository verification should remain local-first and should not generate
receipt, trace, digest, release, or downstream artifacts unless a separate task
explicitly approves the exact artifact path, cleanup rule, and verification
rule.

## Next Step

The next separately approved Phase 9 task should be a synthetic review of this
contract. That review may add documentation-focused tests or review notes, but
it must still not implement Hermes sidecar runtime behavior.
