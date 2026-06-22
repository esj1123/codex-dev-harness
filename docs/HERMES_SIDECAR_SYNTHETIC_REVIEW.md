# Hermes Sidecar Synthetic Review

## Purpose

Record the Phase 9B synthetic review for the Hermes sidecar planning contract.

This review adds focused contract checks for
`docs/HERMES_SIDECAR_PLANNING_CONTRACT.md` without implementing Hermes sidecar
runtime behavior, creating a background daemon, starting a service, creating an
MCP runtime, executing tool calls, wiring checks into `scripts/quality_gate.py`,
changing CI workflows, creating audit automation, generating real receipts or
logs, calling external services, adding AgentOps or memory runtime behavior,
automating release behavior, regenerating artifacts or digests, or editing
downstream repositories.

## Review Basis

Phase 9A documented the planning contract. Phase 9B verifies that the contract
contains the minimum sidecar boundary surfaces needed before any sidecar runtime
implementation is considered:

- documentation-only current scope;
- explicit runtime and integration non-implementation;
- downstream relationship to the MCP tool boundary;
- consistency with safety, audit, JSON evidence, eval, local RAG, and retrieval
  receipt evidence policies;
- limited planning responsibility model;
- forbidden sensitive, live, private, and downstream inputs;
- bounded evidence-oriented output;
- side-effect approval separation;
- fail-closed and no-op behavior;
- future verification expectations before runtime behavior.

## Synthetic Checks

The focused tests in `tests/test_hermes_sidecar_planning_contract.py` parse the
contract as documentation and assert the expected boundary language. They do not
instantiate a sidecar, start a process, call tools, run a server, read external
services, write artifacts, or generate runtime evidence.

The checks cover:

| check area | expected behavior |
|---|---|
| current scope | Phase 9A remains planning-only and excludes sidecar runtime, background services, MCP runtime, tool execution, quality-gate/CI wiring, audit automation, external services, release mutation, persistent state, artifact generation, and dependency changes. |
| boundary relationship | The sidecar remains downstream of the MCP tool boundary and cannot widen MCP tool classes, input rules, output rules, approval rules, redaction rules, or evidence hooks. |
| policy consistency | The contract references the relevant safety, audit, JSON evidence, eval, local RAG, retrieval receipt evidence, and roadmap policies, with the safer rule prevailing on conflict. |
| responsibility model | Future sidecar behavior is limited to explicit local metadata, policy checks, dry-run plans, bounded status summaries, repo-relative evidence references, and fail-closed outcomes. |
| input boundary | Raw prompts, private data, raw command logs, model output transcripts, unredacted tool-call bodies, secrets, account values, IPs, ports, live config, device values, local absolute paths, private raw corpus, `08_Study` raw notes, RSID evidence, downstream raw evidence, and hidden environment state remain forbidden. |
| output boundary | Outputs stay bounded to status values, repo-relative paths, hashes, counts, redacted summaries, reason codes, approval state, and safe next steps; unsafe raw content remains forbidden. |
| approval boundary | Planning, dry-run output, documentation approval, or prior task approval cannot authorize file writes, git operations, external calls, MCP tool execution, downstream mutation, evidence generation, or persistent processes. |
| failure behavior | The default is no-op; out-of-approval requests return blocked or not-run style outcomes with minimum safe summaries. |
| future verification | Later work must add synthetic tests before runtime, cover dry-run/fail-closed/redaction/no-background/no-external/no-MCP-runtime/no-default-integration behavior, and keep artifact generation separately approval-gated. |
| runtime absence | Expected sidecar runtime entrypoints and workflow names are absent from the repository. |

## Verification Boundary

Phase 9B verification is limited to local tests and existing repository checks:

- `python -m pytest tests/test_hermes_sidecar_planning_contract.py`
- `python scripts/quality_gate.py`
- `python -m pytest tests`
- `git diff --check`

Clean GitHub Actions Local Verify evidence should be recorded separately after
the Phase 9B commit is pushed and the existing manual read-only workflow passes.

## Safety Notes

Phase 9B is synthetic and documentation/test-only. It does not:

- implement Hermes sidecar runtime
- create a background daemon, service manager, scheduler, socket server, or
  HTTP server
- implement MCP runtime or MCP server behavior
- execute real tool calls
- add quality-gate or CI integration
- create audit automation
- generate real receipt, trace, or log files
- regenerate digest, release, or other artifacts
- create corpus, retrieval, index, sidecar, or runtime folders
- add embeddings or vector storage
- call external services
- add AgentOps or memory runtime behavior
- edit downstream repositories
- publish, tag, release, upload, or deploy anything

## Next Step

After this review is committed and clean Local Verify passes, the next
separately approved task should be Phase 9C Hermes sidecar implementation
boundary planning. Phase 9C should still remain documentation-first unless the
owner explicitly approves exact runtime files, scripts, commands, safety tests,
and side-effect boundaries for a minimal no-op sidecar implementation.
