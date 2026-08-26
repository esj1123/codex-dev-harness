# AI_HANDOFF.md

## Purpose

Provide a compact handoff index without duplicating current authority.

## Authority

Read `docs/AUTHORITY_MANIFEST.json` for the machine-readable current state,
default Read Order, conditional read groups, document classifications, and the
sole normative owner of each protocol namespace.
Read `STATUS.md` for the current human summary, held items, and next
recommended action. Those two files are authoritative when older phase or run
records differ.

`ACCEPTANCE_TRACE.md` and phase-specific closeouts are historical evidence, not
default operating context.

## Control Surface

- Work-package planning and collision checks:
  `scripts/work_package_conflict_check.py`
- Actual-diff postflight:
  `scripts/work_package_postflight.py`
- Verification impact planning:
  `scripts/verification_plan.py`
- Agent Quality validation and aggregation:
  `scripts/agent_quality.py`
- Core-only quality gate:
  `scripts/quality_gate.py`
- Current `LOCAL_INTEGRATION (V2)` verification:
  `scripts/run_local_verify.ps1`
- Manual `HOSTED_EXACT_SHA (V3)` verification:
  `.github/workflows/local-verify.yml`
- Selected manual release-evidence export contract:
  `manual_github_release_evidence_export` (implementation state in `STATUS.md`)

Ignored package, trial, and checkpoint envelopes under `local/` remain local
control-plane evidence. They do not authenticate approval and must not contain
raw prompts, transcripts, private payloads, secrets, absolute paths, or command
logs.

Agent Quality remains optional and `FROZEN / NOT ADOPTED`. Provider execution
and role calibration v7 are `NOT RUN`; neither is implied by
`CORE_HARNESS_READY`.

## Post-M02 Reconciliation Checkpoint

- Harness current local authority basis is
  `acd39a3c3e73fa05e752964a75059809e6e16f71`; physical cleanup is complete,
  while Git GC and preservation packing remain `HOLD / NOT RUN`.
- Stock completed its target-owned verifier/evidence closeout at
  `bd434a200f4054f9b41eeea085183ff0df25c70b`.
- RSID completed its evidence-scope pilot at local
  `main@c0ffc1d5ddd40bb050d10c0f6e42f93b7d16858c`; GAP-013 remains unresolved.
- Launchpad adopted its authority rebaseline by local fast-forward at
  `main@1f9677a13044770bfb3be89ab910127674851d49`; its structural result remains
  `NOT_AUTHENTICATED` and does not authorize Office, transfer, or release work.
- AQ-R5K passed package-bound structural `LOCAL_INTEGRATION (V2)` for proposal
  `53de64a1a19ec5d50849ebda54bbec619e4097a1`: static `153 passed`, Core
  `841 passed / 10 skipped / 416 deselected`, standalone eval `15/15`, and
  quality gate `8/8`. AQ-R5F, AQ-R5H, AQ-R5I, and AQ-R5J remain historical
  `HOLD` results. The proposal remains `FROZEN / NOT_ADOPTED` under the
  `REDESIGN_BEFORE_TRIAL` decision.
- Provider/API/model execution, trial, role calibration v7, baseline/promotion,
  fetch, push, Hosted, release, and Git GC are `NOT RUN`.

The next governed sequence is an authority-only commit, a separate corpus
digest refresh if the approved-source digest is stale, exact-final-SHA planner
verification, and a separately approved guarded local-main decision. Do not
merge the Agent Quality proposal as part of authority reconciliation.

## Required Boundaries

- Structural PASS does not grant execution or side-effect permission.
- A frozen contract change stops with `CONTRACT_CHANGE_REQUIRED`.
- Agent-quality baseline creation remains separately approval-gated.
- Read `STATUS.md` for the tracked release bundle's current state. Keep the
  source-basis commit, artifact-containing commit, local Git state, transient
  transport context, and publication authority distinct.
- The selected manual GitHub export capability does not authorize automatic
  triggers, durable distribution, tag, signing, publication, deployment,
  `origin/main` mutation, or downstream access.
- Push, workflow dispatch, release, upload, downstream access, MCP/Hermes
  execution, and live/private data use require separate authority.
- Tracked authority does not store workflow run IDs.

## Task Handoff

Use the manifest's `handoff` conditional group for this file. Before continuing,
re-read `STATUS.md`, run the verification plan for the intended diff, and
report commands not executed as `NOT RUN`.
