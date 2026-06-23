# Hermes MCP Security Alignment Review

## Purpose

Record the Phase 9E security alignment review between the current Hermes
sidecar boundary and MCP tool-safety expectations.

This review is documentation and synthetic-test only. It does not expand the
Hermes runtime and does not authorize MCP runtime behavior, tool execution,
tool dispatch, background services, quality-gate or CI integration, audit
automation, receipt generation, trace/log writing, external service calls,
release automation, AgentOps, memory runtime behavior, or downstream
integration.

## Review Basis

The review uses the repository-local contracts as the controlling source of
truth:

- `docs/MCP_TOOL_BOUNDARY_CONTRACT.md`
- `docs/HERMES_SIDECAR_PLANNING_CONTRACT.md`
- `docs/HERMES_SIDECAR_IMPLEMENTATION_BOUNDARY.md`
- `docs/HERMES_SIDECAR_USAGE_PROBE.md`
- `scripts/hermes_sidecar.py`
- `docs/JSON_EVIDENCE_POLICY.md`
- `docs/AUDIT_TRACE_SCHEMA.md`
- `docs/SAFETY_POLICY.md`

It also aligns the next Hermes boundary with current MCP security guidance:

- MCP hosts and clients need explicit user consent and control for data access
  and operations.
- MCP tools are model-invoked functions and should keep a human in the loop for
  tool invocation decisions.
- Tool descriptions, annotations, and metadata must be treated as untrusted
  unless they come from a trusted and approved server.
- Local MCP servers can create a local code-execution surface and require exact
  command visibility, consent, sandboxing, and least-privilege file/network
  access before use.
- Tool exposure should be minimized through explicit allow-lists, dynamic
  filtering, and narrow scope rather than broad default catalogs.
- Structured tool outputs should be bounded and schema-checkable before they
  become durable evidence or downstream input.

## Alignment Matrix

| MCP security concern | Hermes v0 boundary | Phase 9E decision |
|---|---|---|
| User consent and control | `scripts/hermes_sidecar.py` does not execute side effects and requires an approval reference before even recording an approved side-effect boundary. | Preserve no-op by default. Approval references are evidence of request boundary only, not execution authority. |
| Human-in-the-loop tool invocation | The no-op sidecar has no MCP tool call path and returns `NOT_RUN` for approved side-effect requests. | Keep every future MCP invocation separately approval-gated by exact tool class, target, command, output, cleanup, and verification. |
| Tool metadata trust | Current Hermes does not ingest MCP tool descriptors, annotations, or remote tool catalogs. | Any future descriptor or annotation must be treated as untrusted input unless the server and descriptor source are separately approved and pinned. |
| Local server compromise | Current Hermes starts no daemon, server, scheduler, socket listener, HTTP listener, or subprocess. | Preserve no persistent process by default. Any future local server task must show the exact startup command, transport, sandbox, filesystem boundary, and network boundary before execution. |
| Scope minimization | Current side-effect classes are explicit and default to blocked or not-run behavior. | Future exposure must be allow-list first. Broad tool catalogs, wildcard scopes, or implicit privilege bundles remain forbidden by default. |
| Structured output safety | Current output is bounded JSON with status, reason code, safe summary, evidence refs, performed actions, and next step. | Keep outputs schema-friendly and redacted. Do not persist raw prompts, raw command logs, unredacted tool-call bodies, secrets, account values, IPs, ports, live config, device values, local absolute paths, or private raw data. |

## Required Security Invariants

Future Hermes work must preserve these invariants unless a later task explicitly
approves a narrower and safer exception:

- no MCP runtime, MCP server, tool execution, or tool dispatch by default;
- no local server, socket, HTTP listener, scheduler, service manager,
  background daemon, or persistent process by default;
- no external service call or network broker by default;
- no file write, artifact generation, git staging, commit, push, tag, release,
  publication, upload, audit generation, receipt generation, trace generation,
  digest refresh, or downstream mutation without separate approval;
- no use of tool descriptors, annotations, prompts, or remote catalogs as
  trusted authority by default;
- no approval inference from previous tasks, documentation, planning text,
  probes, Local Verify evidence, or model output;
- no durable storage of raw prompts, private data, raw command logs,
  unredacted tool-call bodies, secrets, account values, IPs, ports, live
  config, device values, local absolute paths, or private raw corpus material;
- no broad tool exposure, wildcard scopes, or all-tools default mode.

## Future Approval Requirements

Any later task that proposes real MCP or sidecar execution must name:

- exact tool class and tool name;
- exact command or transport, including whether it is stdio, IPC, HTTP, or
  another transport;
- exact server identity, descriptor source, and descriptor pinning basis;
- exact filesystem boundary and whether writes are allowed;
- exact network boundary and whether outbound access is allowed;
- exact approval prompt or owner approval reference;
- exact output schema or bounded result shape;
- exact cleanup rules;
- exact verification commands;
- exact forbidden inputs and forbidden outputs.

Approval for one item does not authorize another. For example, approval to
review an MCP descriptor does not authorize launching a server, executing a
tool, writing files, creating receipts, refreshing digests, committing,
pushing, publishing, or calling external services.

## Synthetic Verification

The focused tests for this review should verify documentation and existing
runtime boundaries only. They may assert that:

- the review records human approval, untrusted tool metadata, local server
  compromise, scope minimization, and structured output boundaries;
- existing Hermes no-op behavior still blocks `mcp_tool_execution` without
  approval;
- existing Hermes no-op behavior returns `NOT_RUN` for approved
  `mcp_tool_execution`;
- the runtime still imports no background, network, subprocess, HTTP, socket,
  or async server modules;
- no MCP server, sidecar package, workflow, quality-gate integration, CI
  integration, audit automation, or receipt/log generation path exists.

These checks do not instantiate MCP clients, execute tools, start servers, call
external services, write artifacts, or generate real receipts, trace events, or
logs.

## Decision

Phase 9E is accepted as `PASS WITH NOTES` when the review document and focused
tests are committed and local verification passes.

The current Hermes sidecar remains a standalone no-op classifier. The next
separately approved Hermes task should harden or schema-lock the no-op result
contract before any MCP descriptor ingestion, tool filtering adapter, local
server startup, or execution bridge is considered.
