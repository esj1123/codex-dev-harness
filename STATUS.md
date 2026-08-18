# STATUS.md

## Current State

`CORE_HARNESS_READY`

The core template harness is ready for governed local use. Renderer application
now requires explicit `--apply`, release evidence generators are repaired, and
the default quality gate is limited to core verification. Current authority is
defined by `docs/AUTHORITY_MANIFEST.json`; historical phase and run details
remain available in Git history and `ACCEPTANCE_TRACE.md`.

The verification UX line through `5568442d96df40a99a22862d273dfc7b005e0a97`
is implemented and independently recovered under exact-runtime local
verification. This branch-local status records that evidence without adopting
the line, updating local `main`, or recording this closeout commit's own SHA.

## Current Strategic Objective

Close the verification UX integration sequence without collapsing historical
proposal, partial, hold, implementation, and verification states into one
claim. No new capability is selected. Comparable multi-repository Harness
evidence resumes only after the separately bounded U05 and H04R sequence.

## Authority Basis

| Basis class | Exact ref or range | Authority state | Meaning |
|---|---|---|---|
| Historical pre-H04L local-main guard | `965fb86de1a8a307c646874d17d44c60c5dd9cf8` | `GUARDED OLD VALUE` | The observed local `main` value before H04L. It is not a self-updating assertion about the current ref. |
| Reviewed verification UX predecessor range | `9a2ee297664e142c716654926a1cb30293c063ab..5568442d96df40a99a22862d273dfc7b005e0a97` | `IMPLEMENTED / LOCALLY VERIFIED / NOT ADOPTED` | Reviewed H01-H03 history and the exact H03R2 recovery basis; integration still requires the ref-conditional owner action below. |

`PASS`, `V2`, `V3`, postflight, a `plan_digest`, or a recommendation does not
promote the verification UX line. A branch-local `STATUS.md` cannot supply its
own `ADOPTED` evidence. Adoption requires an explicit owner decision tied to an
exact ref/SHA after cumulative verification, digest disposition, and
integration-owner disposition are recorded.

## Active Work

The active local work is H04L closeout sequencing: record the completed H01-H03
history, preserve H03R/H03R2 evidence boundaries, refresh the approved digest
from the clean closeout source basis, and verify the frozen final SHA. It does
not update local `main`, adopt the line, or authorize any remote action.

- Interrupt reason: the primary feature line reached exact `5568442` but its
  closeout writer could not safely apply the two-file documentation/test patch.
- Resume target: create a strict linear descendant in an isolated worktree,
  freeze its final digest-containing SHA, and run the cumulative exact-runtime
  verification once at that frozen tip.
- Displaced-item disposition: multi-repository evidence remains preserved for
  H04R after U05; no capability, release, Hosted, or target-repository item is
  implicitly authorized.

## Completed Checkpoint

### H01-H03 and recovery history

- H01 implementation completed at `68b5971325a8371a259c63db081d209fba005b96`
  (`docs: define verification sequencing authority`). Its execution-time state
  remained `PROPOSED / PENDING INTEGRATION`; completion did not adopt it.
- H02 implementation completed at
  `78100a50a1ff8013492b39023b2d6a77e8e4cbba` (`fix(verify): harden
  planning and hosted evidence boundaries`). Its original cumulative result
  remained `PARTIAL / HOLD`; implementation completion did not rewrite that
  result as a pass.
- H03 digest refresh completed at
  `5568442d96df40a99a22862d273dfc7b005e0a97` (`chore(corpus): refresh
  approved digest`) with `34/34` approved sources and `stale=0`. Its original
  runtime-selection attempt remained `HOLD` and is not rewritten by the digest
  commit.
- H03R stopped at preflight because its proposed interpreter ID was 70 bytes;
  the schema limit made that attempt `HOLD` before execution.
- H03R2 independently recovered the cumulative sequence at exact `5568442`:
  Core `837 passed / 10 skipped / 414 deselected`; Full `1251 passed / 10
  skipped`; eval `15/15`; quality gates `8/8`; three dry-run renders covering
  `48` paths; corpus `34/34` with `stale=0`; Python `3.12.10`; pytest `9.0.3`;
  dependency lock `6/6`; and `pip check` `PASS`.

H03R2 is structural local evidence with `authorization_status=NOT_AUTHENTICATED`.
It is not adoption, Hosted evidence, release evidence, or permission to mutate
local `main` or any remote.

## NOW

### H04L — Verification integration closeout

- State: `CLOSEOUT RECORDING / EXACT-F VERIFICATION REQUIRED`.
- Scope: one two-file status/test commit, one separately contracted corpus
  digest commit, and exact-runtime cumulative verification at the frozen final
  SHA.
- The tracked status intentionally omits its own final SHA. The final SHA and
  pass/fail observation belong to the task closeout and Git evidence.

## NEXT

### F — Ref-conditional integration-owner action

- If local `main` does not contain this tracked tree, the next action is a
  separately verified exact-F compare-and-swap integration decision.
- If local `main` already contains this tracked tree, the next action is U05
  whole-repository audit.

The historical pre-H04L `main` value above is only the guarded old value for
the first branch of this decision. It must not be treated as a current-ref
self-updating assertion.

## LATER

### U05 — Whole-repository audit

Run the separately scoped whole-repository audit only after the exact-F
integration disposition.

### H04R — Multi-repository evidence resumption

Resume multi-repository Harness evidence only after U05 and a separate H04R
authorization. No target repository, push, or Hosted execution is implied.

## HELD

- Remote fetch/push, Hosted workflow execution, export, tag, release, checksum,
  SBOM, provenance, signing, publication, deployment, and local-main mutation
  remain `HOLD` and require separate explicit approval.
- Verification UX adoption, push, and Harness or target Hosted execution remain
  `HOLD` pending exact-SHA cumulative evidence and explicit owner authority.
- Agent Quality/provider, Hermes, MCP, Local RAG, and target mutation remain
  held or separately approval-gated.
- Multi-repository evidence is held until U05 and a separate H04R; no new
  capability selection is made by this closeout.

## Operational Capability Status

| Surface | State | Meaning |
|---|---|---|
| Core template harness | `READY` | Core docs, templates, examples, tests, and local verification are supported. |
| Renderer apply | `READY` | No-flag and `--dry-run` are previews; writes require explicit `--apply`. |
| Release generator code | `HARDENED` | Clean-HEAD Git-blob lineage, hash-locked SBOM inputs, non-circular provenance/checksums, and physical output-path controls are implemented. |
| Tracked release bundle | `CURRENT / LOCAL RELEASE / GITHUB-VERIFIED / TRANSIENT CI EXPORT / NOT PUBLISHED` | The tracked six-file bundle was generated from the exact source basis by the approval-gated GitHub manual export, independently validated after download, and committed for local Git use. No remote release or publication is claimed. |
| Manual GitHub release-evidence export | `IMPLEMENTED / APPROVAL-GATED / COMPLETED` | The bounded one-day transport completed for the current source basis. Workflow run IDs remain task closeout evidence rather than tracked authority. |
| External control-plane packages | `HARDENED / EXTERNAL CONTROL-PLANE ROOT VALIDATED` | Optional local `--package-root` support passed same-root compatibility, physical-safety, identity-drift, and real downstream read-only acceptance. It adds no capability, approval, downstream remote action, or schema migration. |
| Agent Quality/provider | `FROZEN / NOT_ADOPTED` | Optional controls remain available for review, but provider execution and role adoption are held. |
| Role calibration v7 | `NOT RUN` | No calibration trial or review batch is authorized by core readiness. |
| Hermes/MCP | `HELD` | Runtime activation requires a selected repository use case and separate approval. |
| Local RAG | `ADVISORY / FROZEN` | Read-only retrieval remains optional and is not part of core verification. |

## Implemented Control Surface

- Render tiers: `minimal`, `standard`, and `full`, with closed Read Orders.
- Manual read-only Local Verify preserves the no-argument `Full` extended
  lane. `-Lane Core` is the official integration scope; explicit `-Lane
  Routine` remains non-authoritative feedback with the exact frozen/held Agent
  Quality, Hermes/MCP, and Local RAG file exclusions.
- The core JSON evidence gate excludes frozen Agent Quality and held Hermes
  receipt/trace shapes; standalone full validation preserves both optional
  surfaces.
- Approved 34-source corpus contract and read-only local retrieval. Digest
  freshness remains an impact-required integration check.
- Read-only downstream contract validation and release-evidence preflight.
- Work-package preflight with deterministic `plan_digest`.
- Work-package postflight over actual Git changes.
- Physical-safe external control-plane package roots are implemented and
  validated while all Git observation remains in the downstream target.
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

`docs/VERIFICATION.md` is the sole normative authority for verification tier
meaning and required evidence. Current execution maps the explicit Core
command set to `LOCAL_INTEGRATION (V2)`, retains Full as its extended regression
superset, and maps the exact-SHA GitHub `verify` job to
`HOSTED_EXACT_SHA (V3)`. V3 is an integration-scope run on GitHub bound to the
final exact SHA, not a product-version successor to V2. When it runs every
required integration command, it satisfies the included V2 scope without a
duplicate local Full run. Routine remains local feedback; Full remains
impact-required for pytest infrastructure, dependency locks, common validators,
and unclassified paths. The separate release
evidence export workflow is transport and generation evidence, not V3.

PASS from preflight or postflight proves structural consistency only. It does
not authenticate approval.

- `NOT RUN`: the command or side effect was intentionally not executed.
- `ENVIRONMENT BLOCKED`: the required runtime or filesystem environment was
  unavailable.
- `NOT DONE`: required work remains incomplete and must not be reported as
  complete.

## Held Or Not Authorized

- Tag, release, signing, publication, or durable remote distribution.
- Verification UX adoption, push, and Harness or target Hosted execution remain
  `HOLD` pending exact-SHA cumulative evidence and explicit owner authority.
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

After the digest-containing final SHA is frozen and exact-runtime cumulative
verification is recorded, inspect local `main` without mutating it. If `main`
does not contain this tracked tree, the next action is a separately authorized
verified exact-F compare-and-swap integration decision. If it already contains
the tree, proceed to the separately scoped U05 whole-repository audit. Resume
multi-repository evidence only after U05 and a separate H04R. Structural PASS,
a branch-local status, or a plan digest does not grant adoption, push, Hosted,
release, or deployment authority.
