# STATUS.md

## Current State

`CORE_HARNESS_READY`

The core template harness is ready for governed local use. Renderer application
now requires explicit `--apply`, release evidence generators are repaired, and
the default quality gate is limited to core verification. Current authority is
defined by `docs/AUTHORITY_MANIFEST.json`; historical phase and run details
remain available in Git history and `ACCEPTANCE_TRACE.md`.

The verification UX commits on the current feature line are `IMPLEMENTED ON
FEATURE BRANCH` but remain `PROPOSED / PENDING INTEGRATION`. This branch-local
status does not adopt them, integrate them into local `main`, or change the
current authority basis.

## Current Strategic Objective

Accumulate comparable Harness evidence across multiple repositories at
reviewed exact SHAs. Record executor, verification scope, duration, findings,
false positives or negatives, manual decisions, and local/remote baseline
state before selecting another core capability.

## Authority Basis

| Basis class | Exact ref or range | Authority state | Meaning |
|---|---|---|---|
| ADOPTED local basis | `main@965fb86de1a8a307c646874d17d44c60c5dd9cf8` | `ADOPTED` | Current local sequencing authority. |
| PROPOSED feature basis | `9a2ee297664e142c716654926a1cb30293c063ab..347ec27f810558a89b3d06242f3833c4eccede40` | `PROPOSED / PENDING INTEGRATION` | Verification UX implementation evidence awaiting an explicit integration-owner decision. |

`PASS`, `V2`, `V3`, postflight, a `plan_digest`, or a recommendation does not
promote the proposed feature basis. A branch-local `STATUS.md`, including this
H01 proposal, cannot supply its own `ADOPTED` evidence. Adoption requires an
explicit owner decision tied to an exact ref/SHA and an adopted `STATUS.md`
basis after the required cumulative verification, digest disposition, and
integration-owner disposition are recorded.

## Active Work

The only active work is `H02`, a bounded additive verification-contract
rework. It strengthens planner fail-closed behavior, corrects Core/Full and
installed-workflow documentation drift, and separates Harness Hosted evidence
from target-repository Hosted evidence. It does not change workflow or suite
execution behavior, adopt the verification UX, or integrate any feature commit
into local `main`.

- Interrupt reason: H01 closed at `68b5971325a8371a259c63db081d209fba005b96`
  as a local `DONE / PROPOSED CHECKPOINT`, exposing the bounded H02 rework
  without adopting the verification UX.
- Resume target: complete H02 as one additive local checkpoint, then begin H03
  digest disposition and final cumulative verification under a separate
  artifact-only package.
- Displaced-item disposition: multi-repository Harness evidence accumulation is
  preserved as the strategic objective and resumes after the H02/H03 sequence;
  no displaced capability, release, or runtime item is implicitly authorized.

## Completed Checkpoint

### H01 — Sequencing-authority proposal

- State: `DONE / PROPOSED CHECKPOINT / PENDING INTEGRATION`.
- Scope: `STATUS.md`, the verification closeout prompt, and their structural
  quality assertions only.
- Checkpoint: `68b5971325a8371a259c63db081d209fba005b96` (`docs: define
  verification sequencing authority`). H01 completion is not verification UX
  adoption or local-main integration.

## NOW

### H02 — Planner and Hosted-evidence separation rework

- State: `ACTIVE / PROPOSED / PENDING VERIFICATION`.
- Scope: exactly the H02 eight-file additive write set; workflow and suite
  execution behavior remain unchanged.
- Completion boundary: targeted and Routine checks pass, authority and planner
  checks pass, the actual diff remains in scope, and one local checkpoint is
  created without claiming completed V2/V3 verification.

## NEXT

### H03 — Artifact digest refresh and final cumulative verification

Use an artifact-only high package to disposition corpus digest freshness and
then run the integration owner's final cumulative command set at the exact
final SHA, including Local Full when the planner requires it. A freshness
failure is `HOLD` unless the H03 package separately authorizes the exact digest
artifact refresh.

## LATER

Resume the strategic multi-repository Harness evidence objective only after
H03 records the final cumulative verification and digest disposition. No
target repository, push, or Hosted execution is implied.

## HELD

- Release, tag, signing, publication, deployment, workflow/ref/remote mutation,
  and local-main integration require separate explicit approval.
- Verification UX adoption, push, and Harness or target Hosted execution remain
  `HOLD` pending exact-SHA cumulative evidence and explicit owner authority.
- Agent Quality/provider, Hermes, MCP, Local RAG, and target mutation remain
  held or separately approval-gated.
- Verification UX adoption is held pending an explicit integration-owner
  decision and the required exact-SHA cumulative evidence.

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

After H02 closes as one local proposed checkpoint, begin H03 under a separate
artifact-only high contract for digest disposition and final cumulative
verification. Do not treat the handoff, any structural PASS, or a branch-local
status as adoption, push authority, Hosted authorization, or local-main
integration. Preserve the multi-repository Harness evidence objective for
resumption after H03; all held surfaces remain `NOT RUN` or separately
approval-gated.
