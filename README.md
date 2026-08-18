# codex-dev-harness

Reusable Agentic Development Repo Template for governed AI/Codex coding workflows.

This repository is a governed coding workflow template for projects that use AI/Codex to inspect, modify, verify, and hand off software work. The word harness is used as a short repo name, but the scope is broader than a test runner. The target system includes task contracts, agent instructions, side-effect boundaries, verification, example validation, and closeout discipline.

## Current State

The repository has moved beyond the historical P0 docs-only baseline. It currently includes:

- Root contract documents.
- Base markdown templates.
- Profile templates for `python_cli`, `csharp_desktop`, and `plc_or_device_tool`.
- A config-driven render script.
- A base quality gate.
- Minimal example skeletons under `examples/`.
- Tests for render and gate behavior.
- A compact capability-selection roadmap that records implemented, held, and
  candidate capabilities without duplicating phase history.
- Work-package v3 preflight/postflight controls with case-insensitive and
  parent/child path conflict detection, frozen contract surfaces, and explicit
  non-authentication of structural PASS results.
- An Agent Quality control plane with run fingerprints, suite-bound invariant
  evidence, safe aggregation, semantic review, and approval-gated baseline
  adoption.
- A completed first greenfield application pilot proving two disjoint feature
  lanes, integration, synthetic E2E evaluation, and cleanup.

No downstream application code, PLC/device code, live target configuration,
secrets, or private raw input is included in this harness repository.

## Historical P0 Scope

P0 was the initial docs-only baseline.

In scope at P0:
- Define the baseline repo contract.
- Define read order and AI/Codex operating rules.
- Define product, MVP, roadmap, status, acceptance trace, safety, verification, and handoff documents.
- Provide base markdown templates.

Out of scope at P0:
- Render scripts.
- Quality gate implementation.
- Example projects.
- Real application code.
- Secrets, private inputs, or live system configuration.

Those items are no longer described as current absence. Render script, quality gate, profile templates, and example skeletons now exist.

## Read Order

1. AGENTS.md
2. docs/AUTHORITY_MANIFEST.json
3. PRODUCT.md
4. MVP.md
5. STATUS.md
6. docs/SAFETY_POLICY.md

Load the manifest's conditional groups only when needed:

- verification: `docs/VERIFICATION.md`, `docs/CI_POLICY.md`
- capability selection: `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- handoff: `docs/AI_HANDOFF.md`

The manifest also lists bounded operational inputs used by specific tools.
Other unlisted documents are non-authoritative reference material.

## Repository Structure

- AGENTS.md
- README.md
- LICENSE
- SECURITY.md
- PRODUCT.md
- MVP.md
- ROADMAP.md
- STATUS.md
- ACCEPTANCE_TRACE.md
- docs/AUTHORITY_MANIFEST.json
- docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md
- code_review.md
- .github/workflows/
- artifacts/
- audits/
- docs/
- evals/
- templates/base/
- profiles/
- prompts/
- scripts/
- scripts/gates/
- examples/
- tests/
- template.config.example.yml

## Core Principles

- One-agent-first: begin with one accountable AI/Codex worker before adding orchestration.
- Read-only first: inspect and summarize before changing files.
- Explicit side-effect boundary: live writes, deletes, moves, external sends, database writes, and device actions require explicit confirmation.
- Verification mesh: tests, smoke checks, acceptance trace, policy validation, example validation, and audit evidence are separate but connected.
- Private data protection: use synthetic fixtures and summaries instead of private raw input.
- Closeout receipt: every completed task reports changed files, checks run, safety checks, risks, and next steps.
- Authority separation: the manifest distinguishes current authority, durable
  policy, and historical evidence before work is planned.

## Read-Only Validation

The default operating loop is Local Quick, an approved non-force push of the
reviewed exact SHA, Hosted Integration Verify for that SHA, and a comparable
closeout. Verification scope, executor, source binding, and evidence export are
independent attributes; `V3` is hosted exact-SHA evidence, not the next product
version. A hosted run that executes the complete integration command set may
satisfy the V2 integration scope without duplicating the Full run locally.
Push and workflow dispatch remain separate approval-gated side effects.
Use `scripts/run_local_verify.ps1 -Lane Core` for the official
`LOCAL_INTEGRATION (V2)` pytest scope. The no-argument `Full` lane remains the
compatible extended regression superset. Tier meaning is defined only in
`docs/VERIFICATION.md`:

- `python --version`
- `python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock`
- `python -m pip check`
- `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1 -Lane Routine`
- `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1 -Lane Core`
- extended compatibility: `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`
- optional external pytest root: `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1 -PytestBaseTempRoot D:\Codex\_tmp\CODEX-HARNESS`

The wrapper runs the selected Routine, Core, or Full pytest lane, standalone
eval without report flags, the eight core
quality gates, and the three profile dry-runs. Impact planning may additionally
require checksum, corpus, render, or focused checks. The optional pytest root
must already exist outside the repository; the wrapper allocates a unique
run-specific child and does not remove it automatically. Verification may write
runner-side temporary files, but it does not mutate tracked files, Git refs, or
remotes.

## Artifact-Writing Release Verification

`scripts/run_release_verify.ps1` is a separate, explicit artifact-writing
workflow. It first calls the standing local verification wrapper and then
generates approved release evidence under `artifacts/`. Run it only when the
task explicitly authorizes those artifact writes. It does not publish a
release, move tags, sign artifacts, create archives, or install workflows.
`STATUS.md` is the sole current-state authority for the tracked release bundle.
Keep its source-basis commit, artifact-containing commit, local Git availability,
transient transport context, and publication state distinct.

Python runtime and dependency reproducibility are documented in
`docs/PYTHON_RUNTIME_POLICY.md`. The local verification runtime is pinned in
`.python-version`, direct development dependencies are declared in
`requirements-dev.txt`, and exact local verification pins are recorded in
`requirements-dev.lock`. Exact verification installs are hash-checked and
restricted to the approved binary wheels.

CI policy is documented in `docs/CI_POLICY.md`. The repository includes the
manual read-only `.github/workflows/local-verify.yml` Hosted Integration Verify
workflow. It uses `workflow_dispatch` with a required exact commit SHA and
`contents: read`. Here, read-only describes repository permissions and the
absence of tracked-file, ref, or remote mutation; normal runner filesystem
writes still occur. It performs no artifact upload.

The owner has selected a bounded `manual_github_release_evidence_export`
extension at `.github/workflows/release-evidence-export.yml`. It allows only a
separate exact-SHA, manual, one-day evidence transport after explicit approval
and is not a verification result. It does not authorize an automatic trigger,
tag, GitHub Release, signing, publication, deployment, secret use, or
`origin/main` mutation.

## Local-First Usage

The intended baseline workflow is local-first:
- clone the repository
- install development requirements
- run local verification
- preview example rendering (no flag or `--dry-run`)
- review expected target paths
- apply generated docs to a separate target project only after review with
  explicit `--apply`

See `docs/LOCAL_USAGE.md` for the full local usage flow and `docs/LOCAL_RELEASE_PACKAGE.md` for local package boundaries.

CI remains approval-gated and is not a baseline runtime requirement. The
installed Hosted Integration Verify workflow is the baseline hosted
verification path. The separate manual transient release-evidence export
workflow remains approval-gated; broader triggers, required checks, durable
artifact distribution, release publication, and deployment remain separately
approval-gated. See `STATUS.md` for its current implementation state.

## AI Readiness Scanner

`AI_Readiness_Scanner_v0` is a standalone local read-only scanner for checking
whether a repository has enough purpose, AI operating rules, safety boundaries,
verification, evidence discipline, and next-action clarity for AI-assisted
work.

Run from the repository root:

- `python scripts/ai_readiness_scanner.py .`
- `python scripts/ai_readiness_scanner.py --json .`

If bare `python.exe` is blocked in a Codex desktop Windows shell, use the
documented local verification runtime selected by `scripts/run_local_verify.ps1`
and recorded in `docs/PYTHON_RUNTIME_POLICY.md`.

The scanner prints Markdown by default and JSON with `--json`. It is not wired
into `scripts/quality_gate.py`, does not write generated reports, does not run
target repository scripts, and does not authorize implementation work. Domain
risk flags are conservative path-level indicators for review; they are not
automatic failures.

## Security

Report suspected vulnerabilities through the private process in
[`SECURITY.md`](SECURITY.md). Do not disclose vulnerability details in a public
issue.

## License

This repository is licensed under the [MIT License](LICENSE). That license
applies to the harness repository itself; a rendered or adapted downstream
project must select and record its own license.
