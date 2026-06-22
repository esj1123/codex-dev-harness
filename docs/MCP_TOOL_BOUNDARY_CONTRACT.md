# MCP Tool Boundary Contract

## 1. Purpose

Define the Phase 8A planning contract for future MCP tool boundaries in this
repository.

This phase is documentation-only. It does not implement an MCP runtime, create
tool servers, execute tool calls, implement a Hermes sidecar, wire anything into
`scripts/quality_gate.py` or CI, create audit automation, generate receipts or
logs, call external services, add AgentOps or memory runtime behavior, automate
release behavior, or edit downstream repositories.

The contract exists so later MCP or Hermes work can start from explicit tool
classes, input and output boundaries, approval rules, redaction rules, evidence
hooks, and forbidden behavior before any runtime is approved.

## 2. Boundary Principles

Future MCP-facing behavior must preserve the current repository posture:

- local-first by default
- read-only inspection before side effects
- exact-file and exact-command approvals for writes
- repository-local policy remains authoritative
- downstream repository rules remain authoritative for downstream work
- no private raw data, secrets, live values, or local absolute paths in durable
  evidence
- no approval-free side effects

MCP tool output is advisory unless a later task explicitly approves a stronger
contract. A tool result cannot broaden the active task scope, grant approval for
side effects, override user constraints, or bypass repository policy.

## 3. Tool Class Policy

| tool class | default status | boundary |
|---|---|---|
| repository read-only inspection | allowed when task-scoped | May read approved repo files, git status, git diff, git log, and documented metadata. Must not read private raw material or unrelated locations. |
| local verification dry-runs | allowed when non-mutating | May run existing tests, quality gates, schema parsers, and dry-run render checks. Must report NOT RUN or ENVIRONMENT BLOCKED honestly. |
| local file edits | approval-gated | May edit only owner-approved files in the current repository scope. Must avoid unrelated refactors and forbidden data capture. |
| artifact generation | separately approval-gated | Must name exact commands, output paths, cleanup rules, and commit intent before writing artifacts. Release artifacts require separate release approval. |
| git staging, commit, push, tag, or release | separately approval-gated | Read-only git inspection is distinct from repository mutation. Staging, commit, push, tags, releases, and publication each require explicit owner approval. |
| downstream repository work | separately approval-gated | Must follow downstream repo rules and exact approved files. Harness policy cannot authorize downstream edits by itself. |
| external service or network calls | forbidden by default | Requires a separate task contract naming service, purpose, input redaction, output handling, and side-effect status. |
| live endpoint, device, PLC, broker, or account mutation | forbidden by default | Not allowed without a separate high-risk approval and simulator-first safety plan. |
| installer, driver, DLL, binary, or unknown executable execution | forbidden by default | Not allowed as an MCP default. Any exception requires exact binary identity, source, purpose, and owner approval. |

## 4. Input Boundary

Future MCP tool requests may accept only bounded, task-relevant inputs such as:

- repo-relative file paths approved by the active task
- short safe summaries of the user request
- exact command names or dry-run commands approved by the active task
- schema identifiers, receipt identifiers, trace identifiers, digest hashes, or
  commit identifiers
- bounded options such as max results, dry-run flags, or output format

Future MCP tool requests must not require or store:

- raw prompts or prompt transcripts
- private raw data
- sensitive business source text
- raw command logs
- unredacted tool-call request or response bodies
- local absolute paths
- secrets, keys, tokens, credentials, or account values
- IPs, ports, live endpoints, live config, device values, broker values, or
  equipment values
- raw downstream evidence, RSID evidence, or `08_Study` raw notes

If a tool cannot answer without forbidden input, it must return a blocked or
no-sufficient-evidence result instead of weakening the boundary.

## 5. Output Boundary

Future MCP tool responses should be bounded and reviewable. Safe outputs include:

- PASS, PASS WITH NOTES, FAIL, BLOCKED, NOT RUN, or ENVIRONMENT BLOCKED status
- short safe summaries
- repo-relative paths
- schema ids, receipt ids, trace ids, digest refs, commit ids, and SHA-256 hashes
- counts, statuses, and reason codes
- redacted excerpts only when the source is approved and safe to quote
- explicit next-step recommendations within the approved scope

Future MCP tool responses must not persist:

- full private source text
- raw prompt transcripts
- raw command logs
- full tool-call bodies
- secrets or account values
- live config, IPs, ports, device values, or local absolute paths
- generated downstream source unless separately approved by the downstream task

## 6. Approval Boundary

The default MCP posture is read-only and advisory.

Any side effect requires explicit owner approval that names:

- the side-effect class
- the exact target repository or system
- allowed files, commands, and output paths
- whether generated artifacts are temporary or commit candidates
- cleanup expectations
- verification commands
- forbidden scope

Approval for one side-effect class does not authorize another. For example,
approval to edit a documentation file does not authorize staging, committing,
pushing, creating artifacts, running release automation, calling external
services, or editing downstream repositories.

## 7. Redaction Rules

Future MCP evidence should prefer identifiers, hashes, counts, status labels,
and safe summaries over raw content.

Redaction must remove or avoid:

- secrets and credentials
- private raw data
- local absolute paths
- unredacted tool-call bodies
- raw command logs
- account values
- IPs, ports, live endpoints, live config, and device values
- raw downstream or private corpus material

When redaction would make the evidence ambiguous, the tool should report the
limit as a safety note instead of copying unsafe material.

## 8. Evidence Hooks

Future MCP behavior may reference existing JSON evidence surfaces only by safe
identifiers and summaries:

- `receipt_summary.receipt_id`
- `trace_event.event_id`
- `trace_event.related_receipt_id`
- repo-relative evidence paths
- SHA-256 hashes
- safe status and reason codes

This contract does not create audit automation, receipt generation, trace file
generation, or log writing. Any future automation must be separately approved
and must follow `docs/JSON_EVIDENCE_POLICY.md`,
`docs/AUDIT_TRACE_SCHEMA.md`, `audits/receipt-summary.schema.json`, and
`audits/trace-event.schema.json`.

## 9. Failure Handling

Future MCP tools should fail closed:

- return `blocked` when a request crosses a forbidden input or side-effect
  boundary
- return `no_sufficient_evidence` when safe evidence is unavailable
- return `not_run` when a command or tool was intentionally not executed
- return `environment_blocked` when the local environment prevents execution
- include a short safe reason and next safe step

Failure handling must not trigger fallback behavior that widens file access,
calls external services, writes artifacts, or performs side effects without
separate approval.

## 10. Future Verification Expectations

Before any MCP runtime or Hermes sidecar is implemented, a later task should add
focused synthetic tests or review checks for:

- allowed and forbidden tool classes
- side-effect approval separation
- input redaction
- output redaction
- blocked and not-run behavior
- receipt and trace reference shape
- no external service or live endpoint default behavior

Those checks require separate approval. This Phase 8A task does not add tests,
quality-gate wiring, CI wiring, or runtime code.

## 11. Explicit Non-Goals

Phase 8A does not:

- implement MCP runtime
- implement Hermes sidecar behavior
- create MCP server code
- execute real tool calls
- add quality-gate or CI integration
- create audit automation
- generate real receipts, trace files, or logs
- regenerate release or digest artifacts
- create corpus, retrieval, or index folders
- add embeddings or vector storage
- call external services
- add AgentOps or memory runtime behavior
- edit downstream repositories
- publish, tag, release, upload, or deploy anything

## 12. Next Step

The default next safe phase after this contract is Phase 8B synthetic MCP
boundary tests or review checks. Those checks should verify the documented
allowed and forbidden classes before any runtime planning.

Phase 9 Hermes sidecar planning should remain separate and should start only
after the MCP boundary is documented, reviewed, and any separately approved
boundary tests have passed.

Neither next step is authorized by this document alone.
