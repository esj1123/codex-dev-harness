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
