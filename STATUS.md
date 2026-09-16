# STATUS.md

## Current State

`CORE_HARNESS_READY`

The core template harness is ready for governed local use. Renderer writes
require explicit `--apply`; release evidence generators are hardened; the
default quality gate verifies the core surface.

`docs/AUTHORITY_MANIFEST.json` defines current authority. This file owns the
current human summary and implementation sequencing. Source-bound SHA,
verification, recovery, and adoption records are preserved in
[Historical Local Checkpoints](ACCEPTANCE_TRACE.md#historical-local-checkpoints).
Those records are completed observations, not self-updating local or remote refs.

The owner-approved Harness boundary-fix fast-forward was observed at
`81fbc855c9db1db364ca22ef71ebc6211380b416` with a clean local `main` and all
11 implementation/test files matching the verified candidate. This is a
source-bound local adoption observation, not a self-updating assertion that a
later working tree, ref, remote, or Hosted run still has that value.

## NOW

Current action: `BOUNDARY-FIX ADOPTION AND HOSTED V3 CLOSEOUT COMPLETE`.

The earlier `POST-H4R3 LOCAL CLOSEOUT COMPLETE` state remains historical
checkpoint context. Preserve the completed authority reconciliation, separate
digest refresh, exact-final-SHA V2 verification, postflight, and owner-approved
local adoption as distinct checkpoints. Physical Harness cleanup and the Stock,
RSID, and Launchpad local checkpoints are complete. Their evidence grants no
new action.

A separately authorized boundary-fix package is locally adopted at
`81fbc855c9db1db364ca22ef71ebc6211380b416`. Its final source-bound local
evidence recorded focused `96 passed`; Core `1008 passed / 10 skipped / 414
deselected`; Full `1422 passed / 10 skipped`; standalone eval `PASS`; quality
gate `8/8`; checksum verification `5/5`; all three profile render dry-runs
`PASS`; cumulative impact planning at V2 plus Full/checksum; package postflight
`PASS`; and exact Git blob binding `11/11`. Independent follow-up review closed
F1-R1 as resolved with no additional actionable finding.

The separately approved normal push and existing exact-SHA Hosted verification
then completed at `bac6a13ef77e20554f67b38398fa65499828fba0`.
That exact SHA is the completed `HOSTED_EXACT_SHA (V3)` evidence basis: Hosted
Core passed `1017 passed / 1 skipped / 414 deselected`, the exact Python
`3.12.10` / pytest `9.0.3` dependency-locked runtime passed, and hosted eval,
quality gate, and all three render dry-runs passed. The push and Hosted approval
used for that checkpoint is consumed. This STATUS edit is a later local
documentation change; its eventual commit is not covered by the V3 result at
`bac6a13ef77e20554f67b38398fa65499828fba0` and is not itself claimed as pushed
or Hosted-verified here.

Agent Quality capability-v2 has AQ-R5K structural `LOCAL_INTEGRATION (V2)`
evidence and remains `FROZEN / NOT_ADOPTED` under `REDESIGN_BEFORE_TRIAL`.
Earlier HOLDs remain historical HOLDs. Structural PASS does not demonstrate
prevention or establish provider execution, trial, calibration, a baseline,
promotion, or adoption. Do not merge the proposal as an implied successor.

## NEXT

The post-H4R3 local sequence is closed. The boundary-fix adoption/push/Hosted
sequence is also closed. No additional implementation capability is selected.
A new Harness package requires a P0 safety or authority defect, an actual target
blocker, the same gap in two targets, or evidence that a verifier produced an
incorrect PASS or FAIL. Select an exact work package under fresh authority and
verification gates before additional implementation.

The one approved boundary-fix push and exact-SHA Hosted verification have been
used for the completed `bac6a13ef77e20554f67b38398fa65499828fba0`
checkpoint. Any later push, workflow dispatch, Hosted verification, remote
mutation, or remote policy change requires separate fresh authority; the prior
approval does not carry forward.

Remote, Hosted, release, provider, trial, calibration, baseline promotion,
and Agent Quality redesign or adoption remain separate owner decisions.
No tracked recommendation alone authorizes remote action, release/publication,
runtime repair, branch deletion, worktree removal, target mutation, or adoption.

## HELD

- Future Remote fetch/push, Harness or target Hosted workflow execution, export,
  tag, release, checksum, SBOM, provenance, signing, publication, deployment,
  durable remote distribution, target execution, and additional local-main
  mutation require exact repo-owned checkpoints and separate fresh authority.
  The completed normal push and exact-SHA Hosted V3 result at
  `bac6a13ef77e20554f67b38398fa65499828fba0` do not authorize a successor
  remote or Hosted action; future Remote and Hosted actions remain
  `HOLD / DEFERRED` by default.
- Agent Quality/provider/API/model execution, demonstrated-prevention trial,
  role calibration v7 or review batches, baseline creation/promotion/adoption,
  release, Git GC, and preservation packing remain held or `NOT RUN / DEFERRED`.
  Baseline adoption requires the numeric-bound and Unicode failures to complete
  human/grader review, owner-held graders to match the hardened invariants,
  and a fresh complete suite to meet every adoption threshold.
- Hermes/MCP activation, Hermes execution bridges, AgentOps, durable audit
  logging, Local RAG expansion, and target mutation remain held or separately
  approval-gated. Local RAG stays optional, read-only, advisory, and frozen.
- A generic command runner, inferred package fields, durable audit writer,
  automatic worktree prune, local-ref update, Junction repair, manifest
  rewrite, dependency installation, and EOL normalization remain `NO-GO`.
- Automatic digest writes, automatic release triggers, and release automation
  outside the selected manual GitHub release-evidence export contract are held.
  Completed manual export does not authorize another export or publication.
- New downstream access, render, write, commit, push, or workflow dispatch
  requires target-specific authority. Physical cleanup and the Stock-then-RSID
  sequence remain separate operational/target-owned checkpoints. RSID GAP-013
  owner/provenance remains unresolved; empty-root and merged-branch hygiene
  remains separate. Launchpad evidence does not authorize Office, transfer, or
  release work. No additional application capability has a selected contract.
- Hosted verification is an operational evidence checkpoint, not a new
  capability. The dirty-worktree checkpoint and P1 automation remain deferred.
- Agent Quality suites, schemas, and validation helpers remain preserved;
  historical envelopes do not establish core readiness, provider isolation,
  or role-profile mapping. Safe envelopes and failure candidates stay ignored
  under `local/agent-quality/`; raw prompts, transcripts, model output, and
  holdout fixtures are not tracked. Moving runtime/calibration archives does
  not adopt a baseline or change the tracked contract.

## Operational Capability Status

| Surface | State | Meaning |
|---|---|---|
| Core template harness | `READY` | Core docs, templates, examples, tests, and local verification are supported. |
| Renderer apply | `READY` | No-flag and `--dry-run` are previews; writes require explicit `--apply`. |
| Release generator code | `HARDENED` | Clean-HEAD Git-blob lineage, hash-locked SBOM inputs, non-circular provenance/checksums, and physical output-path controls are implemented. |
| Tracked release bundle | `CURRENT / LOCAL RELEASE / GITHUB-VERIFIED / TRANSIENT CI EXPORT / NOT PUBLISHED` | The six-file bundle was generated from its exact source basis by approved manual export, independently validated after download, and committed for local Git use. No remote release or publication is claimed. |
| Manual GitHub release-evidence export | `IMPLEMENTED / APPROVAL-GATED / COMPLETED` | Bounded one-day transport completed for the recorded source basis. Workflow run IDs stay in task closeout evidence. |
| External control-plane packages | `HARDENED / EXTERNAL CONTROL-PLANE ROOT VALIDATED` | Optional `--package-root` passed same-root, physical-safety, identity-drift, and downstream read-only acceptance. No new capability, approval, downstream remote action, or schema migration is granted. |
| Read-only environment diagnostic | `IMPLEMENTED / EXACT-SHA LOCALLY VERIFIED / LOCALLY ADOPTED` | Safe JSON diagnostics install nothing, persist no path, execute no verification suite, and perform no target behavior. Hosted evidence is separate. |
| Downstream target closeout | `STOCK / RSID / LAUNCHPAD LOCAL CHECKPOINTS COMPLETE` | Exact target SHA and result scopes are in Historical Local Checkpoints. Remote, Hosted, Office, transfer, and release remain unobserved or not authorized. |
| Agent Quality/provider | `STRUCTURAL V2 PASS / FROZEN / NOT_ADOPTED` | AQ-R5K structure passed; earlier HOLDs remain preserved. Provider, trial, calibration, baseline, promotion, and adoption remain held. |
| Role calibration v7 | `NOT RUN` | Core readiness authorizes no calibration trial or review batch. |
| Hermes/MCP | `HELD` | Runtime activation requires a selected repository use case and separate approval. |
| Local RAG | `ADVISORY / FROZEN` | Optional read-only retrieval is outside core verification. |


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
