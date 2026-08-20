# STATUS.md

## Current State

`CORE_HARNESS_READY`

The core template harness is ready for governed local use. Renderer application
now requires explicit `--apply`, release evidence generators are repaired, and
the default quality gate is limited to core verification. Current authority is
defined by `docs/AUTHORITY_MANIFEST.json`; historical phase and run details
remain available in Git history and `ACCEPTANCE_TRACE.md`.

The owner-approved exact local compare-and-swap completed from guarded old
`965fb86de1a8a307c646874d17d44c60c5dd9cf8` to verified adopted basis
`ffc90e0f0801979bf67de4a5b32aaf8fc2745a0d`. M00 authority alignment is now on
local `main` at `845e56d81d006de07d405cbf1fe6711afd444e04`. The M01 read-only
environment diagnostic is implemented on the integration branch at
`2cfb40d72eafdd40ff95e99fa35ded11b57496f6`, one linear commit ahead of that
local-main basis. This status records the observed local authority and
sequencing without self-authorizing a corpus-digest write, local-main mutation,
remote, release, publication, or target execution action.

## Current Strategic Objective

Keep authority, capability selection, mechanization, and downstream pilots in
one explicit order without collapsing historical proposal, partial, hold,
implementation, and verification states into one claim. H04R is complete as a
bounded Launchpad control-plane pilot, M00 authority alignment is complete, and
the M01 Harness diagnostic is implemented and locally verified. The immediate
checkpoint is the separately approved same-34-source corpus freshness repair;
only after cumulative closeout does the dirty-worktree checkpoint receive a
need decision. Later items remain queued and inherit no authorization.

## Authority Basis

| Basis class | Exact ref or range | Authority state | Meaning |
|---|---|---|---|
| Historical pre-local-adoption guard | `965fb86de1a8a307c646874d17d44c60c5dd9cf8` | `GUARDED OLD VALUE` | The historical observed local `main` value used by the completed owner-approved local compare-and-swap. It is not a self-updating assertion about the current ref. |
| Verified adopted implementation basis | `ffc90e0f0801979bf67de4a5b32aaf8fc2745a0d` | `LOCALLY ADOPTED / EXACT-SHA CORE+FULL VERIFIED` | Owner-approved local adoption after exact-SHA cumulative evidence; later documentation commits do not rewrite that verification claim. |
| M00 authority-alignment commit | `845e56d81d006de07d405cbf1fe6711afd444e04` | `CURRENT LOCAL MAIN / CLEAN AT M01 TASK START` | Exact local-main basis for M01. It completed the authority and priority alignment without authorizing later capability work. |
| M01 environment-diagnostic commit | `2cfb40d72eafdd40ff95e99fa35ded11b57496f6` | `IMPLEMENTED / EXACT-SHA CORE+FULL VERIFIED / PENDING LOCAL INTEGRATION` | Read-only environment diagnostics are implemented one linear commit ahead of local main. This is not corpus freshness, local-main adoption, or remote evidence. |

`PASS`, `V2`, `V3`, postflight, a `plan_digest`, or a recommendation remains
structural evidence rather than independent authorization. The completed local
adoption above required the owner decision and exact-SHA cumulative evidence;
it does not authorize a new mutation, push, Hosted execution, release, or
target action.

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
It did not itself constitute adoption, Hosted evidence, release evidence, or
permission to mutate local `main` or any remote.

### H04 closeout and recovery history

- H04LW recorded `Core PASS` at the adopted exact SHA. Its Full step remained
  `HOLD`; that session's Core PASS must not be rewritten as a Full PASS.
- H04LR stopped with a path-length `HOLD`; that environmental boundary remains
  preserved as historical evidence.
- H04LR2 recovered Full at the same adopted exact SHA with `Full PASS`.

### U05 whole-repository audit

- The whole-repository audit reviewed `7 commits/20 paths` with `GO`, observed
  `14 worktrees clean`, and found no rename, delete, or mode change.
- Its only current-authority finding was this P1 documentation mismatch. A
  cached `origin` observation is not represented as live remote state.

### H04R Launchpad downstream pilot

- H04R completed the external control-plane alignment against Harness
  `db748759ed1c4f1b7c5cbce84180c598eaa6cdb4` and Launchpad
  `be49a668b09a85c9316da17bd6c3c40192ee68ed`.
- Focused verification passed `11/11`; local Full passed `130` with one
  reviewed dependency skip. Preflight and postflight preserved one exact
  `plan_digest`, and both repositories ended clean at their recorded local
  refs.
- This is reusable local control-plane evidence only. Launchpad has no remote,
  Hosted verification was `NOT RUN`, and artifact-tool runtime remains
  `DEPENDENCY_HOLD` because `node_modules` is not the required Junction.

### M00 authority alignment and M01 environment diagnostic

- M00 completed at `845e56d81d006de07d405cbf1fe6711afd444e04`
  with the authority, mechanization, and downstream priority order aligned.
- M01 completed its bounded implementation at
  `2cfb40d72eafdd40ff95e99fa35ded11b57496f6`. Focused environment tests passed
  `32`; focused quality-contract tests passed `84`; Core passed `840` with `10`
  skipped and `414` deselected; Full passed `1254` with `10` skipped; eval,
  eight quality gates, and all three render dry-runs passed.
- The `EnvironmentOnly / Json` smoke result was `PASS` with the repo virtual
  environment, Python `3.12.10`, pytest `9.0.3`, dependency lock `6/6`, and pip
  check `PASS`. It installed nothing, ran no verification suite, persisted no
  path, and reported no performed action.
- The corpus digest was not changed by M00 or M01. Its current read-only check
  is `32/34` valid with two stale approved sources and no missing, malformed,
  unsafe, or invalid UTF-8 source. Freshness therefore remains pending a
  separately approved exact-path write and commit sequence.

## NOW

### Corpus freshness approval checkpoint

- State: `PENDING OWNER APPROVAL / NOT AUTHORIZED`.
- Scope: after this authority closeout has an exact clean commit, refresh only
  `artifacts/corpus-digest.json` against the unchanged ordered 34-source set.
- The write, post-write verification, artifact commit, and local-main
  compare-and-swap remain distinct checkpoints. No source rebaseline, release
  artifact, remote action, RAG action, or downstream action is implied.

## NEXT

### Dirty-worktree package checkpoint decision

After exact corpus freshness and cumulative integration closeout, review the
observed package workflow and decide whether a read-only `NOT_FINAL`
dirty-worktree checkpoint prevents a demonstrated error. This is a decision
checkpoint, not implementation approval. Launchpad adapters, stock, RSID, and
other P1 work remain later repo-specific decisions.

## HELD

- Remote fetch/push, Hosted workflow execution, export, tag, release, checksum,
  SBOM, provenance, signing, publication, deployment, target execution, and
  additional local-main mutation remain `HOLD` and require separate explicit
  approval.
- Agent Quality/provider, Hermes, MCP, Local RAG, and target mutation remain
  held or separately approval-gated.
- A generic command runner, inferred package fields, durable audit writer,
  automatic worktree prune, local-ref update, Junction repair, manifest
  rewrite, dependency installation, and EOL normalization remain `NO-GO`.
- No additional implementation capability is selected. Corpus freshness is an
  approval-gated integration repair, not a new capability. The dirty-worktree
  checkpoint, Launchpad transfer/Junction checks, stock pilot, RSID static
  pilot, and P1 automation are queued without implementation or inherited
  approval.

## Operational Capability Status

| Surface | State | Meaning |
|---|---|---|
| Core template harness | `READY` | Core docs, templates, examples, tests, and local verification are supported. |
| Renderer apply | `READY` | No-flag and `--dry-run` are previews; writes require explicit `--apply`. |
| Release generator code | `HARDENED` | Clean-HEAD Git-blob lineage, hash-locked SBOM inputs, non-circular provenance/checksums, and physical output-path controls are implemented. |
| Tracked release bundle | `CURRENT / LOCAL RELEASE / GITHUB-VERIFIED / TRANSIENT CI EXPORT / NOT PUBLISHED` | The tracked six-file bundle was generated from the exact source basis by the approval-gated GitHub manual export, independently validated after download, and committed for local Git use. No remote release or publication is claimed. |
| Manual GitHub release-evidence export | `IMPLEMENTED / APPROVAL-GATED / COMPLETED` | The bounded one-day transport completed for the current source basis. Workflow run IDs remain task closeout evidence rather than tracked authority. |
| External control-plane packages | `HARDENED / EXTERNAL CONTROL-PLANE ROOT VALIDATED` | Optional local `--package-root` support passed same-root compatibility, physical-safety, identity-drift, and real downstream read-only acceptance. It adds no capability, approval, downstream remote action, or schema migration. |
| Read-only environment diagnostic | `IMPLEMENTED / EXACT-SHA LOCALLY VERIFIED / PENDING INTEGRATION` | Safe JSON diagnostics are implemented without installation, persistence, verification execution, or target-repository behavior; corpus freshness and local-main adoption remain separate. |
| Downstream mechanization queue | `ORDERED / NOT AUTHORIZED FOR IMPLEMENTATION` | Decide the dirty-worktree checkpoint from observed use, then keep Launchpad read-only adapters, stock, RSID Git-object static work, and any P1 work in separate packages. |
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
- Push, fetch, Harness or target Hosted execution, and target execution remain
  `HOLD` pending separate explicit owner authority.
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

The next executable action after this authority closeout is a separately
approved exact same-34-source corpus digest freshness commit. Validate the
write before commit, obtain the required commit approval, then run cumulative
exact-SHA integration verification before any approved local-main
compare-and-swap. After real use, evaluate the dirty-worktree checkpoint; then
keep Launchpad adapter work, stock, and RSID in separate repo-specific packages.
No item in that queue authorizes fetch, push, Hosted execution, export, release,
publication, target mutation, runtime repair, or target execution. Structural
PASS and a plan digest remain distinct from future approvals.
