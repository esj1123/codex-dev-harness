# Hermes Result Schema Artifact Decision

## Purpose

Record the Phase 9G decision about whether the Hermes no-op result contract
should become a machine-readable schema artifact.

Phase 9G is documentation-only. It does not create a JSON Schema file, change
`scripts/hermes_sidecar.py`, add tests, wire anything into `scripts/quality_gate.py`
or CI, implement MCP runtime, execute tools, start a server, create audit
automation, generate real receipt/log/trace files, call external services,
regenerate artifacts or digests, add AgentOps or memory behavior, publish
releases, or edit downstream repositories.

## Basis

The current basis is:

- `scripts/hermes_sidecar.py`
- `docs/HERMES_SIDECAR_RESULT_SCHEMA_CONTRACT.md`
- `tests/test_hermes_sidecar_result_schema_contract.py`
- `docs/HERMES_MCP_SECURITY_ALIGNMENT_REVIEW.md`
- `docs/MCP_TOOL_BOUNDARY_CONTRACT.md`
- `docs/JSON_EVIDENCE_POLICY.md`

Phase 9F already freezes the human-readable no-op result contract:

- required top-level fields;
- status values;
- reason codes;
- side-effect class semantics;
- evidence reference shape;
- redaction and non-persistence rules;
- schema evolution boundary.

## Decision

Decision: `schema_artifact_deferred_until_consumer_exists`.

A machine-readable Hermes result schema should not be added immediately. The
current result contract is useful, but there is not yet an approved consumer
that needs a durable schema artifact:

- no MCP adapter consumes Hermes output;
- no tool-filtering adapter consumes Hermes output;
- no quality gate validates Hermes output;
- no CI workflow validates Hermes output;
- no audit automation writes or validates Hermes results;
- no receipt, trace, release, AgentOps, memory, or downstream integration
  consumes Hermes output.

Creating a schema artifact now would add another durable surface without a real
integration point. The safer next move is to keep the contract human-readable
and synthetic-tested until a specific consumer is approved.

## Future Artifact Conditions

A later task may create a machine-readable schema only when it names:

- the exact schema path;
- the exact schema dialect or validation subset;
- the consumer that will read the schema;
- whether validation is manual, test-only, quality-gated, CI-gated, or
  runtime-enforced;
- the exact result samples or synthetic fixtures to validate;
- whether schema validation is advisory or blocking;
- migration behavior for `schema_version`;
- forbidden inputs and forbidden outputs;
- verification commands;
- cleanup and closeout requirements.

The initial artifact path should prefer `audits/hermes-sidecar-result.schema.json`
only if the owner approves adding Hermes output to the existing JSON evidence
surface. Otherwise, a documentation-local path should be chosen in the future
task.

## Non-goals

Phase 9G does not:

- create `audits/hermes-sidecar-result.schema.json`;
- create any other schema artifact;
- add schema validation code;
- wire Hermes output into `scripts/quality_gate.py`;
- wire Hermes output into GitHub Actions;
- change `scripts/hermes_sidecar.py`;
- execute MCP tools;
- start MCP or Hermes servers;
- generate receipts, traces, logs, digests, release artifacts, or downstream
  outputs;
- call external services;
- add dependencies.

## Risk Notes

Adding a schema too early could create drift if the runtime contract evolves
before a consumer exists. Adding it later is acceptable because Phase 9F already
locks the current no-op shape with synthetic tests.

The first future artifact task should remain schema-only unless it separately
approves validation wiring. Creating a schema file must not automatically
authorize quality-gate integration, CI integration, MCP runtime, audit
automation, or downstream use.

## Next Step

After Phase 9G is committed and clean Local Verify passes, the next safe Hermes
task is a separately approved preflight-use planning task. That task may define
how a future caller would use the no-op sidecar before side effects, but it
must still not execute MCP tools, start servers, write artifacts, create audit
records, or integrate with quality gates or CI by default.
