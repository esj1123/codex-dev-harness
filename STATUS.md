# STATUS.md

## Current State

`CORE_HARNESS_READY`

The core template harness is ready for governed local use. Renderer application
now requires explicit `--apply`, release evidence generators are repaired, and
the default quality gate is limited to core verification. Current authority is
defined by `docs/AUTHORITY_MANIFEST.json`; historical phase and run details
remain available in Git history and `ACCEPTANCE_TRACE.md`.

## Operational Capability Status

| Surface | State | Meaning |
|---|---|---|
| Core template harness | `READY` | Core docs, templates, examples, tests, and local verification are supported. |
| Renderer apply | `READY` | No-flag and `--dry-run` are previews; writes require explicit `--apply`. |
| Release generator code | `HARDENED` | Clean-HEAD Git-blob lineage, hash-locked SBOM inputs, non-circular provenance/checksums, and physical output-path controls are implemented. |
| Tracked release bundle | `CURRENT / LOCAL RELEASE / GITHUB-VERIFIED / TRANSIENT CI EXPORT / NOT PUBLISHED` | The six tracked release artifacts were generated for exact source basis `438cc1def76666ee5431e1c5fcbf830f48bf0207`, exported through the approval-gated one-day Actions transport, independently validated, and committed for local release use. No remote release or publication is claimed. |
| Manual GitHub release-evidence export | `IMPLEMENTED / APPROVAL-GATED / COMPLETED` | Exact-SHA export run `31678866653` completed with hosted provenance v2, exact six-file validation, and one-day transient Actions transport. The upload is transport evidence only, not publication. |
| Agent Quality/provider | `FROZEN / NOT_ADOPTED` | Optional controls remain available for review, but provider execution and role adoption are held. |
| Role calibration v7 | `NOT RUN` | No calibration trial or review batch is authorized by core readiness. |
| Hermes/MCP | `HELD` | Runtime activation requires a selected repository use case and separate approval. |
| Local RAG | `ADVISORY / FROZEN` | Read-only retrieval remains optional and is not part of core verification. |

## Implemented Control Surface

- Render tiers: `minimal`, `standard`, and `full`, with closed Read Orders.
- Manual read-only Local Verify defaults to the authoritative `Full` lane with
  pytest, standalone eval, quality gates, and three profile dry-runs. Explicit
  `-Lane Routine` is non-authoritative feedback that excludes only the exact
  frozen/held Agent Quality, Hermes/MCP, and Local RAG test inventory.
- The core JSON evidence gate excludes frozen Agent Quality and held Hermes
  receipt/trace shapes; standalone full validation preserves both optional
  surfaces.
- Approved 34-source corpus contract and read-only local retrieval. Digest
  freshness remains an impact-required integration check.
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
- Machine-captured Agent Quality run evidence v2, deterministic fingerprinting,
  role-aware aggregation and comparison, semantic review, and
  failure-lifecycle validation. Historical v1 envelopes remain readable.
- Role profiles keep model selection at `gpt-5.6-sol` while binding contract,
  feature, critical, review, and integration work to explicit reasoning
  profiles. Requested model selection is recorded as adapter evidence and is
  not represented as independently observed provider state.
- Local verification rejects Python versions other than `3.12.10`, requires
  every locked development package at its exact version, and runs `pip check`
  before pytest.
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

## Historical Agent Quality Evidence

A fixed-configuration suite previously completed all 19 planned trials across
five replay tasks. No critical, scope, safety, postflight, or contract-reopen
violation occurred, but the historical aggregate remains `HOLD` and is not an
adopted baseline:

- strict 3-trial task rate: `0.0`;
- strict 5-trial critical task rate: `0.0`;
- holdout results: `17 PASS / 2 FAIL`;
- confirmed semantic blockers: `5`.

The observed causes were two repeated malformed numeric-bound failures,
non-encodable Unicode handling gaps in two allowed-values parser trials,
required agent verification omitted in several otherwise owner-verified
trials, one historical-authority rewrite, and one malformed-schema regression
coverage gap.

The tracked suite, schemas, and validation helpers remain preserved, but Agent
Quality/provider execution is frozen and not adopted. Previous suite and run
envelopes remain readable as historical evidence; they do not establish core
readiness, provider isolation, or a role-profile mapping.

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
- `Routine`: explicit non-authoritative local feedback only. It cannot satisfy
  V2, V3, promotion, or release evidence requirements.
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

- Tag, release, signing, publication, or durable remote distribution.
- Automatic digest writes, automatic release triggers, or release automation
  outside the selected manual GitHub release-evidence export contract.
- MCP execution, Hermes execution bridges, AgentOps, or durable audit logging.
- Agent Quality/provider execution and role calibration v7.
- New downstream access, render, write, commit, push, or workflow dispatch.
- Additional application capabilities without an owner-selected feature
  contract.
- Agent-quality baseline adoption until the numeric-bound and Unicode failures
  complete their required human/grader review, the owner-held graders match
  the hardened invariants, and a fresh complete suite meets every adoption
  threshold.

## Next Recommended Step

Keep the current local release bundle frozen and review it through local Git.
The bundle was generated from an exact-SHA GitHub manual export, downloaded,
independently validated, committed locally, and promoted to local `main`; the
transient Actions artifact is transport only and expires after one day. No
remote publication was performed. Tag, GitHub Release, signing, publication,
deployment, `origin/main`, Agent Quality/provider, Hermes, MCP, and downstream
mutation remain `NOT RUN` or outside this release.
