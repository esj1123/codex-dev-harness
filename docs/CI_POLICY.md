# CI_POLICY.md

## Purpose

Define the current CI policy for codex-dev-harness after installing the
owner-approved read-only local verification GitHub Actions workflow.

## Current Policy

Local verification first, with one manual read-only GitHub Actions mirror.
Here, read-only means `contents: read` and no tracked-file, Git-ref, tag,
release, or remote mutation. Checkout, virtual-environment creation, dependency
installation, tests, and other runner-local filesystem writes still occur.

The repository now includes the owner-approved first implementation target:
`.github/workflows/local-verify.yml`. It is a manual `workflow_dispatch`
workflow with `permissions: contents: read` and no artifact upload,
publication, signing, tag movement, deployment, downstream checkout, or live
target behavior. Dispatch requires a lowercase 40-character `expected_sha`;
checkout uses that exact ref and fails before verification if the observed HEAD
does not match. Checkout and Python setup actions are pinned to immutable
commit SHAs, checkout credentials are not persisted, and hosted Windows
verification uses exact Python `3.12.10`. The preferred local runtime is the
same exact Python `3.12.10`, so `LOCAL_INTEGRATION (V2)` and
`HOSTED_EXACT_SHA (V3)` share one executable version contract. Tier meaning
and required evidence are defined only in `docs/VERIFICATION.md`.
A successful exact-SHA hosted run that executes every impact-required
integration command satisfies the underlying V2 integration scope; a separate
local Full run is not a prerequisite. The local pre-push path remains focused
or Routine feedback plus work-package checks. This offloads the expensive
integration run without weakening the locked environment, command set, or
exact-SHA evidence boundary.

The workflow also runs exactly `python scripts/run_eval.py` without report
flags after pytest and before the quality gate. This is console-only validation:
a nonzero exit fails that manually dispatched run, but does not create a
required check or release-blocking policy.

Release readiness remains verified locally with documented commands, local
release evidence, and recorded closeout evidence. The installed workflow is a
verification hygiene mirror, not release automation.

The current local evidence baseline includes:

- `scripts/run_local_verify.ps1`
- `scripts/run_release_verify.ps1`
- `scripts/verification_plan.py`
- local pytest and quality gate verification
- standalone local evals
- local release manifest, checksum, SBOM, provenance, and optional eval report
  artifacts

These local surfaces are the baseline that CI must mirror when approved. The
installed workflow mirrors the `Core` command set: core pytest, the
no-report standalone eval, all eight core quality gates, and three profile render
dry-runs.

The wrapper offers explicit local `Routine`, `Core`, and `Full` lanes. It is
non-authoritative and excludes only the exact held test-file inventory for
frozen Agent Quality and Local RAG plus held Hermes/MCP. The no-argument and
release verification wrappers remain `Full`; Hosted Integration Verify runs
`Core`. Routine PASS does not satisfy `LOCAL_INTEGRATION (V2)` or
`HOSTED_EXACT_SHA (V3)` and cannot be used as release or promotion evidence.
New tests remain in Routine unless the integration owner
explicitly adds their exact path to the held inventory.

Additional workflows, triggers, permissions, required-check policies, artifact
upload, release verification CI, signing, tag movement, deployment, downstream
integration, or live behavior require a separate owner-approved implementation
task.

The owner has now selected one such task:
`manual_github_release_evidence_export`. The selected contract preserves the
existing verification commands in `.github/workflows/local-verify.yml` and
permits only the separate `.github/workflows/release-evidence-export.yml`
exact-SHA manual export, one-day Actions artifact transport, and subsequent
local validation and commit. It does not select an automatic trigger, required
check, durable artifact distribution, release, signing, publication,
deployment, secret use, or `origin/main` mutation. `STATUS.md` records the
capability's current implementation state. Only the separate export workflow
may transport the six approved files with one-day retention.

## First CI Implementation Target

The first CI implementation target is now implemented as
`.github/workflows/local-verify.yml`. Per the capability implementation roadmap,
CI starts as a manual read-only workflow that only runs repository validation
checks. Read-only describes repository authority and Git side effects, not a
zero-write runner filesystem:

- `python -m pytest tests -m "not optional_agent_quality and not optional_hermes_mcp and not optional_local_rag" --durations=50 -rs`
- `python scripts/run_eval.py`
- `python scripts/quality_gate.py`
- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

The workflow installs development requirements from `requirements-dev.lock`
with `--require-hashes --only-binary=:all:`, runs `python -m pip check`, and
uses exact hosted Windows Python `3.12.10`. setup-python caches pip downloads
using `requirements-dev.lock` as the cache key source.
`LOCAL_INTEGRATION (V2)` and `HOSTED_EXACT_SHA (V3)` both remain on Python 3.12 and use the same locked
development dependencies. Core is the V2 default, while `full_pytest` is
added for optional capability, pytest-infrastructure, dependency-lock,
common-validator, and unclassified-path changes. Both local and hosted
verification clear ambient pytest and Python-path options,
disable third-party pytest plugin autoload, and report slow-test durations and
reviewed skip reasons.

Release verification remains local-only unless separately approved and may use:

- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_release_verify.ps1`

The installed local verification workflow does not run release verification,
generate an eval report, or upload artifacts in its default `verify` job. The
separate explicit export job is the approved six-file, one-day exception.

Agent-quality stability validation is also standalone, frozen, and manual. Local Verify
does not execute agent trials, aggregate trial envelopes, compare model or
prompt candidates, generate an agent-quality baseline, or promote failures.
The core quality gate validates only the core JSON evidence bundle; optional
Agent Quality checks remain in their standalone static-check path.

## Minimum Branch Protection

After a successful `HOSTED_EXACT_SHA (V3)`, the separately approval-gated minimum policy
may enforce administrators and required linear history while disabling force
pushes and branch deletion. Required status checks, pull-request reviews,
restrictions, conversation resolution, branch locking, and fork syncing remain
disabled. This preserves direct non-force owner pushes and manual
`HOSTED_EXACT_SHA (V3)` while
prohibiting merge commits, force pushes, and branch deletion.

## CI Boundaries

CI must not introduce:

- Real application code.
- Real PLC/device code.
- Live target writes.
- Device start, stop, reset, or mode-change actions.
- Secret or live config generation.
- New profiles without a separate design and validation step.
- Artifact upload outside the separately selected six-file, one-day export
  contract or without another explicit decision.
- Release publication, signing, tag creation, or tag movement.
- Deployment behavior.
- RAG, retrieval index, embeddings, or vector database behavior.
- Audit logging automation or audit receipt generation.
- Eval quality-gate integration, automatic-trigger or additional eval CI
  execution, routine eval report generation, required-check semantics, or
  release-blocking eval policy.
- Agent trial execution, agent-quality baseline generation, candidate adoption,
  or failure promotion.
- MCP tool server, Hermes sidecar, or downstream product integration behavior.

## Verification Hygiene

Verification closeouts must distinguish:

- source checks that were run locally
- manual CI checks that were run through `.github/workflows/local-verify.yml`
- checks that were not run
- generated artifacts that were intentionally regenerated
- release evidence that was intentionally not regenerated

Documentation-only or policy-only changes may use focused verification when
the omitted checks are marked `NOT RUN` with a reason. Tasks that touch
generated output, release evidence, render behavior, quality gates, examples,
or scripts should run broader local verification unless the task explicitly
excludes it.

Line-ending warnings, if any, should be recorded as repository hygiene notes
unless they affect executable behavior or generated artifact content. A local
commit is not a push, tag, release, artifact upload, deployment, or publication.

## Verification Protocol Reference

`docs/VERIFICATION.md` is the sole normative authority for verification tier
identifiers, semantic names, required evidence, and the distinction between
the V2 core and impact-required extras. This CI policy owns only execution
environment, workflow permissions, and remote side-effect boundaries.

Feature and contract lanes do not run `LOCAL_INTEGRATION (V2)` or
`HOSTED_EXACT_SHA (V3)` by default. After approved feature and digest commits
are present, the integration owner selects one authoritative executor for the
complete command set: local integration for V2, or the hosted exact-SHA gate
for V3. A hosted V3 PASS discharges the included V2 scope without requiring the
same Full command set to run locally first. Digest writes remain separately
approval-gated; the read-only digest check runs on the final digest-containing
source basis.
A feature package may therefore close at `FOCUSED_FEATURE (V1)`, while the
integration owner must evaluate the complete base-to-tip diff and satisfy the
impact planner's cumulative minimum tier. Prior feature V1 evidence never
substitutes for a required cumulative V2 run.

## Verification Impact Planner

`scripts/verification_plan.py` is a standalone read-only advisory planner. It
observes the path diff between an approved base commit and a selected head,
then reports the minimum V0-V2 machine tier, required command identifiers and their
machine-readable argument-list contracts, plus integration-owner or
digest/checksum/render escalation flags from
`docs/VERIFICATION_IMPACT_MAP.json`. Parameterized commands retain safe
placeholders for the integration owner to resolve.

The planner does not execute commands, cache results, write a corpus digest,
dispatch `HOSTED_EXACT_SHA (V3)`, authenticate approval, or grant permission to run the checks it
names. An integration owner must still review the work-package contract and
obtain every required side-effect approval.

## Release Relationship

CI is not required before a documentation-level release tag. A release tag
should still record local verification evidence and known limitations.

Artifact upload, release workflows, signing workflows, deployment workflows,
and tag movement remain separate explicit release-publication decisions. The
optional CI templates do not grant that approval.
