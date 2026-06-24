# Hermes Sidecar Result Schema Contract

## Purpose

Record the Phase 9F result schema contract for the minimal no-op Hermes
sidecar.

This contract freezes the reviewable JSON result shape emitted by
`scripts/hermes_sidecar.py` before any MCP descriptor ingestion, tool filtering
adapter, local server startup, execution bridge, audit automation, or
downstream integration is considered.

Phase 9F is documentation and synthetic-test only. It does not change the
sidecar runtime, implement MCP runtime, execute tools, start a server, wire
quality-gate or CI integration, create audit automation, generate real receipt,
trace, or log files, call external services, regenerate artifacts or digests,
add AgentOps or memory behavior, publish releases, or edit downstream
repositories.

## Contract Basis

The contract is based on the current standalone no-op sidecar:

- `scripts/hermes_sidecar.py`
- `tests/test_hermes_sidecar.py`
- `docs/HERMES_SIDECAR_IMPLEMENTATION_BOUNDARY.md`
- `docs/HERMES_MCP_SECURITY_ALIGNMENT_REVIEW.md`
- `docs/MCP_TOOL_BOUNDARY_CONTRACT.md`
- `docs/JSON_EVIDENCE_POLICY.md`

If these documents conflict, the narrower and safer rule applies until a later
owner-approved task updates the contract explicitly.

## Required Top-level Fields

Every normal result from `assess_request()` must be a JSON-serializable object
with these top-level fields:

| field | type | contract |
|---|---|---|
| `schema_version` | string | Must be `hermes_sidecar_noop.v0` for the current no-op contract. |
| `mode` | string | Must be `no_op`. |
| `status` | string | Must use one of the documented status values for v0. |
| `reason_code` | string | Must use one of the documented reason codes for v0. |
| `side_effect_requested` | string | Must be `none`, one of the documented side-effect classes, or `unknown` for invalid side-effect input. |
| `approval_ref_present` | boolean | Records whether a safe approval reference was accepted. It is not execution authority. |
| `safe_task_summary` | string | Short sanitized task summary or a safe placeholder such as `[blocked unsafe input]`. |
| `evidence_refs` | array | Bounded list of safe evidence reference objects. |
| `performed_actions` | array | Must be an empty list in v0. |
| `safety_notes` | array | Safe short strings that describe no-op and non-execution boundaries. |
| `next_step` | string | Safe next action or approval guidance. |

The CLI must print this JSON result to stdout. The JSON output must not require
raw prompts, private data, raw command logs, unredacted tool-call bodies,
secrets, account values, IPs, ports, live config, device values, local absolute
paths, or private raw corpus material.

## Status Values

The current no-op contract allows these emitted statuses:

| status | meaning |
|---|---|
| `PASS_WITH_NOTES` | No side effect was requested; output is advisory planning context only. |
| `BLOCKED` | Policy, approval, safety, source basis, or input validation prevents the request from proceeding. |
| `NOT_RUN` | A side-effect boundary was approved as a request, but the no-op sidecar has no executor path and performed no action. |
| `ENVIRONMENT_BLOCKED` | Local environment inspection failed before a safe normal result could be produced. |

Future status values require a separately approved contract update before they
are treated as durable evidence.

## Reason Codes

The current no-op contract allows these emitted reason codes:

| reason_code | meaning |
|---|---|
| `insufficient_evidence` | No side effect was requested and the advisory result does not claim stronger evidence. |
| `approval_blocked` | The requested side-effect class lacks an accepted approval reference. |
| `policy_blocked` | The requested side-effect class remains non-executable in v0 even with an approval reference. |
| `unsafe_input` | Input contains forbidden raw, private, live, secret, local-path, transcript, or invalid-path material. |
| `source_basis_blocked` | A requested evidence path does not exist in the safe repository basis. |
| `scope_conflict` | The requested side-effect class is outside the documented class set. |
| `environment_blocked` | The local runtime could not safely inspect the repository basis. |

Reason codes must be narrow and fail-closed. They must not trigger fallback
behavior that widens file access, calls tools, starts servers, writes files,
creates artifacts, or performs any side effect.

## Side-effect Classes

The current no-op contract recognizes these side-effect classes:

- `none`
- `file_write`
- `git_stage`
- `git_commit`
- `git_push`
- `artifact_generation`
- `mcp_tool_execution`
- `audit_generation`
- `external_call`
- `release_publication`
- `downstream_mutation`
- `persistent_process`

Recognizing a side-effect class does not authorize execution. In v0, any class
other than `none` must either return `BLOCKED` without an approval reference or
`NOT_RUN` with an accepted approval reference.

## Evidence Reference Shape

Each item in `evidence_refs` must be an object with:

| field | type | contract |
|---|---|---|
| `path` | string | Existing safe repo-relative path using POSIX separators. |
| `exists` | boolean | Must be `true` for accepted evidence references. |

Evidence references must not use absolute paths, parent traversal, symlinks,
private/raw/local path classes, IP-like values, secret-like assignments, or
missing files as accepted evidence.

## Redaction And Non-persistence

The result must not persist or echo:

- raw prompts or prompt transcripts;
- private data;
- raw command logs;
- model output transcripts;
- unredacted tool-call request or response bodies;
- secrets, credentials, tokens, account values, or API keys;
- IPs, ports, live endpoints, live config, device values, broker values, or
  equipment values;
- local absolute paths;
- private raw corpus, `08_Study` raw notes, RSID raw evidence, downstream raw
  evidence, or generated downstream source.

When input is unsafe, `safe_task_summary` must use a safe placeholder instead
of echoing the unsafe value.

## Schema Evolution Rule

The current `schema_version` is `hermes_sidecar_noop.v0`.

Any later change that adds required fields, removes fields, changes status
values, changes reason codes, changes side-effect class semantics, changes
evidence reference shape, or allows execution behavior must be a separately
approved task. Such a task must name exact files, tests, migration behavior,
verification commands, and forbidden data classes.

Phase 9F does not add a machine-readable JSON Schema file and does not add this
contract to `scripts/quality_gate.py`. Those steps remain separately
approval-gated.

## Synthetic Verification

Focused tests for this contract should verify:

- the contract document lists required fields, statuses, reason codes,
  side-effect classes, evidence reference shape, redaction rules, and schema
  evolution rules;
- representative no-op, blocked, not-run, unsafe-input, source-basis-blocked,
  and invalid side-effect results include the required top-level fields;
- `performed_actions` remains empty for every representative result;
- `mode` remains `no_op`;
- `schema_version` remains `hermes_sidecar_noop.v0`;
- unsafe input is not echoed into the JSON result;
- the CLI emits parseable JSON with the contracted fields.

These tests must not instantiate MCP clients, execute tools, start servers, call
external services, write artifacts, generate receipts, write traces, refresh
digests, publish releases, or edit downstream repositories.

## Decision

Phase 9F is accepted as `PASS WITH NOTES` when this contract and focused tests
pass local verification.

The minimal Hermes sidecar remains a standalone no-op classifier. The next
separately approved Hermes task may review whether this contract should gain a
machine-readable schema artifact, but that must still not authorize MCP
execution, server startup, quality-gate or CI integration, audit automation,
release automation, external service calls, AgentOps, memory runtime behavior,
or downstream integration by default.
