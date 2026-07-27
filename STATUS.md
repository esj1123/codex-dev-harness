# STATUS.md

## Current State

`AGENT_QUALITY_BASELINE_NOT_ESTABLISHED`

The harness has completed its first governed greenfield application pilot,
work-package v3 hardening, and the standalone Agent Quality Stability control
layer. Current authority is defined by `docs/AUTHORITY_MANIFEST.json`;
historical phase and run details remain available in Git history and
`ACCEPTANCE_TRACE.md`.

## Implemented Control Surface

- Render tiers: `minimal`, `standard`, and `full`, with closed Read Orders.
- Manual read-only Local Verify with pytest, standalone eval, quality gates,
  and three profile dry-runs, bound to a required exact checkout SHA.
- Exact 34-source approved corpus digest and read-only local retrieval.
- Read-only downstream contract validation and release-evidence preflight.
- Work-package preflight with deterministic `plan_digest`.
- Work-package postflight over actual Git changes.
- Authority manifest separating current, durable, and historical documents.
- Advisory verification-impact planning.
- Work-package schema v3:
  - case-insensitive and parent/child path ownership checks;
  - Windows trailing-dot and trailing-space rejection;
  - `contract_basis_sha` and shared `contract_frozen_paths`;
  - `CONTRACT_CHANGE_REQUIRED` stop/reopen behavior;
  - explicit `authorization_status=NOT_AUTHENTICATED`.
  - exact verification interpreter identity and argument arrays bound into the
    package plan digest;
  - postflight `PASS` requires every declared command ID to be complete.
- Fail-closed docs gate with runtime manifest validation.
- Manual agent-quality run validation, deterministic fingerprinting,
  aggregation, comparison, semantic review, and failure-lifecycle validation.
- Baseline adoption trust chain:
  - writer and candidate comparison recompute from the canonical suite and
    sanitized run directory;
  - safe per-run evidence manifests bind trial budget, holdout status, and
    strict-pass results;
  - suite/configuration comparability is decided before quality regression;
  - baseline shape is cross-checked against the canonical suite by the JSON
    evidence gate.
  - the current suite binds each required invariant to one grader ID and each
    current run must provide an exact status and result hash for every
    invariant before strict pass is possible.

## Agent Quality Pilot

A fresh fixed-configuration suite completed all 19 planned trials across five
replay tasks. No critical, scope, safety, postflight, or contract-reopen
violation occurred, but the aggregate remains `HOLD`:

- strict 3-trial task rate: `0.0`;
- strict 5-trial critical task rate: `0.0`;
- holdout results: `17 PASS / 2 FAIL`;
- confirmed semantic blockers: `5`.

The observed causes were two repeated malformed numeric-bound failures,
non-encodable Unicode handling gaps in two allowed-values parser trials,
required agent verification omitted in several otherwise owner-verified
trials, one historical-authority rewrite, and one malformed-schema regression
coverage gap.

The current suite now declares exact verification commands, failure-derived
invariant IDs, and invariant grader bindings. Execution-specific package
digests remain in run
evidence rather than the canonical suite, so a new approval reference does not
change the comparison contract. The previous suite and run envelopes remain
readable as historical evidence; they are not eligible for the new suite.

Safe run envelopes and failure candidates remain ignored under
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
- Standing local integration verification runs the V2 core followed by the
  three profile dry-runs through `scripts/run_local_verify.ps1`.
- `V2 impact-required extras`: checksum, corpus, and relevant render checks.
- `V3`: one approved push and one manual Local Verify whose required
  `expected_sha` is checked out and asserted before verification.

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
- Agent-quality baseline adoption until the numeric-bound and Unicode failures
  complete their required human/grader review, the owner-held graders match
  the hardened invariants, and a fresh complete suite meets every adoption
  threshold.

## Next Recommended Step

Keep baseline adoption at `HOLD`. Review the sanitized numeric-bound and
non-encodable-Unicode failure families against the frozen target contracts,
then decide whether a fresh complete suite should run under one fingerprint.
Current suite runs must use the declared grader-bound invariant evidence;
historical unbound runs remain reviewable but are not adoption inputs. Tracked
baseline creation remains blocked until every adoption condition passes.
