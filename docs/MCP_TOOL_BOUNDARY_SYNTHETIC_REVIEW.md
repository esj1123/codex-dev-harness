# MCP Tool Boundary Synthetic Review

## Purpose

Record the Phase 8B synthetic review for the MCP tool boundary contract.

This review adds focused contract checks for `docs/MCP_TOOL_BOUNDARY_CONTRACT.md`
without implementing an MCP runtime, creating MCP server code, executing tool
calls, implementing Hermes sidecar behavior, wiring checks into
`scripts/quality_gate.py`, changing CI workflows, creating audit automation,
generating real receipts or logs, calling external services, adding AgentOps or
memory runtime behavior, automating release behavior, or editing downstream
repositories.

## Review Basis

Phase 8A documented the boundary contract. Phase 8B verifies that the contract
contains the minimum boundary surfaces needed before any runtime planning:

- allowed, approval-gated, separately approval-gated, and forbidden tool classes
- side-effect approval separation
- forbidden input classes
- safe output classes
- redaction expectations
- receipt and trace evidence references
- fail-closed behavior
- explicit non-goals
- Phase 8B-before-runtime sequencing

## Synthetic Checks

The focused tests in `tests/test_mcp_tool_boundary_contract.py` parse the
contract as documentation and assert the expected boundary language. They do not
instantiate tools, call tools, run a server, read external services, write
artifacts, or generate runtime evidence.

The checks cover:

| check area | expected behavior |
|---|---|
| tool class matrix | Read-only repo inspection and dry-runs are distinct from approval-gated, separately approval-gated, and forbidden classes. |
| approval separation | Approval for one side-effect class does not authorize staging, committing, pushing, artifact generation, release automation, external calls, or downstream edits. |
| input boundary | Raw prompts, private data, command logs, unredacted tool-call bodies, local absolute paths, secrets, account values, IPs, ports, live config, device values, downstream raw evidence, RSID evidence, and `08_Study` raw notes remain forbidden. |
| output and redaction | Outputs prefer status labels, safe summaries, repo-relative paths, identifiers, hashes, counts, and reason codes; unsafe raw content remains forbidden. |
| evidence hooks | Future evidence references use receipt and trace identifiers, repo-relative paths, hashes, and safe summaries without creating automation. |
| failure handling | Boundary failures use `blocked`, `no_sufficient_evidence`, `not_run`, or `environment_blocked` and fail closed without side-effect fallback. |
| non-goals | Runtime implementation, Hermes sidecar, tool execution, quality-gate/CI wiring, audit automation, artifact regeneration, external services, AgentOps, memory, downstream work, release, tag, publication, upload, and deployment remain out of scope. |

## Verification Boundary

Phase 8B verification is limited to local tests and existing repository checks:

- `python -m pytest tests/test_mcp_tool_boundary_contract.py`
- `python scripts/quality_gate.py`
- `python -m pytest tests`
- `git diff --check`

Clean GitHub Actions Local Verify evidence should be recorded separately after
the Phase 8B commit is pushed and the existing manual read-only workflow passes.

## Safety Notes

Phase 8B is synthetic and documentation/test-only. It does not:

- implement MCP runtime
- implement Hermes sidecar
- create MCP server code
- execute real tool calls
- add quality-gate or CI integration
- create audit automation
- generate real receipt, trace, or log files
- regenerate digest or release artifacts
- create corpus, retrieval, or index folders
- add embeddings or vector storage
- call external services
- add AgentOps or memory runtime behavior
- edit downstream repositories
- publish, tag, release, upload, or deploy anything

## Next Step

After this review is committed and clean Local Verify passes, the next
separately approved task should be Phase 8B closeout documentation or Phase 9
Hermes sidecar planning. Phase 9 planning should remain documentation-first and
must still not implement sidecar runtime behavior without a new approval.
