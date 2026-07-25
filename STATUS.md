# STATUS.md

## Current State

`READY_FOR_PARALLEL_APPLICATION_DEVELOPMENT`

The harness has completed its first governed greenfield application pilot and
the follow-up work-package v2 hardening. Current authority is defined by
`docs/AUTHORITY_MANIFEST.json`; historical phase and run details remain
available in Git history and `ACCEPTANCE_TRACE.md`.

## Implemented Control Surface

- Render tiers: `minimal`, `standard`, and `full`, with closed Read Orders.
- Manual read-only Local Verify with pytest, standalone eval, quality gates,
  and three profile dry-runs.
- Exact 34-source approved corpus digest and read-only local retrieval.
- Read-only downstream contract validation and release-evidence preflight.
- Work-package preflight with deterministic `plan_digest`.
- Work-package postflight over actual Git changes.
- Authority manifest separating current, durable, and historical documents.
- Advisory verification-impact planning.
- Work-package schema v2:
  - case-insensitive and parent/child path ownership checks;
  - Windows trailing-dot and trailing-space rejection;
  - `contract_basis_sha` and shared `contract_frozen_paths`;
  - `CONTRACT_CHANGE_REQUIRED` stop/reopen behavior;
  - explicit `authorization_status=NOT_AUTHENTICATED`.
- Fail-closed docs gate with runtime manifest validation.

## Application Pilot

The safe alias `local-data-quality-cli` was initialized in a separately
authorized local repository. Its governance render, modular rules/CSV lanes,
integration, full tests, synthetic E2E matrix, fresh-install smoke, and cleanup
completed successfully. No remote was configured, no private or live data was
used, and no post-E2E improvement patch was required.

This evidence shows that the harness can govern a small parallel application
batch. It does not authorize a new target, a new feature, or any remote side
effect.

## Verification Model

- `V0`: package, base, allowed-file, and diff review.
- `V1`: V0 plus focused lane tests.
- `V2 core`: full pytest, standalone eval, and all quality gates.
- `V2 impact-required extras`: checksum, corpus, and relevant render checks.
- `V3`: one approved push and one manual Local Verify for the final cumulative
  SHA.

PASS from preflight or postflight proves structural consistency only. It does
not authenticate approval.

## Held Or Not Authorized

- Release evidence regeneration, tag, release, signing, upload, or publication.
- Automatic digest writes or release automation.
- MCP execution, Hermes execution bridges, AgentOps, or durable audit logging.
- New downstream access, render, write, commit, push, or workflow dispatch.
- Additional application capabilities without an owner-selected feature
  contract.

## Next Recommended Step

After the current integration commit receives the approved same-source digest
refresh and one cumulative V2/V3 checkpoint, select the next
`local-data-quality-cli` feature contract. Freeze its public data model, reason
codes, module API, output schema, status priority, and exit codes before opening
new feature lanes.
