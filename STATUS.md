# STATUS.md

## Current State

`AGENT_QUALITY_BASELINE_NOT_ESTABLISHED`

The harness has completed its first governed greenfield application pilot,
work-package v2 hardening, and the standalone Agent Quality Stability control
layer. Current authority is defined by `docs/AUTHORITY_MANIFEST.json`;
historical phase and run details remain available in Git history and
`ACCEPTANCE_TRACE.md`.

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
- Manual agent-quality run validation, deterministic fingerprinting,
  aggregation, comparison, semantic review, and failure-lifecycle validation.

## Agent Quality Pilot

The first fixed-configuration suite completed all 19 planned trials across five
replay tasks. All critical 5-trial tasks passed, and no scope, safety,
postflight, or contract-reopen violation occurred. One of three numeric parser
trials rejected valid bounded finite Decimal forms in the owner-held holdout.

The aggregate result is `HOLD`:

- normal 3-trial task rate: `2/3`;
- critical 5-trial task rate: `1.0`;
- confirmed semantic blockers: `1`;
- holdout failures: `1`.

Safe run envelopes and the quarantined failure candidate remain ignored under
`local/agent-quality/`. Raw prompts, transcripts, model output, and holdout
fixtures are not tracked. The adoption conditions were not met, so
`artifacts/agent-quality-baseline.json` was not created.

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

- `NOT RUN`: the command or side effect was intentionally not executed.
- `ENVIRONMENT BLOCKED`: the required runtime or filesystem environment was
  unavailable.
- `NOT DONE`: required work remains incomplete and must not be reported as
  complete.

## Held Or Not Authorized

- Release evidence regeneration, tag, release, signing, upload, or publication.
- Automatic digest writes or release automation.
- MCP execution, Hermes execution bridges, AgentOps, or durable audit logging.
- New downstream access, render, write, commit, push, or workflow dispatch.
- Additional application capabilities without an owner-selected feature
  contract.
- Agent-quality baseline adoption until the observed numeric parser failure is
  sanitized, reproduced, reviewed, and the complete suite meets every
  adoption threshold.

## Next Recommended Step

Review the observed numeric parser failure, advance it only through the
approved failure lifecycle, and run a diagnostic parser replay if needed.
Tracked baseline creation remains blocked. If the configuration, prompt, tool
policy, grader, or task contract changes, run a new complete 19-trial suite
instead of replacing only the failed trial.
