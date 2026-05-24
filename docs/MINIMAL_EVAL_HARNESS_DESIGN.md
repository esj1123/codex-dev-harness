# Minimal Eval Harness Design

## Purpose

Design a future minimal, local-only eval harness for codex-dev-harness without
implementing it.

The intended harness would provide machine-readable verification for template
safety and regression behavior. It would check whether generated or rendered
template outputs preserve expected file structure, required policy language,
forbidden artifact boundaries, and deterministic output path behavior.

This document is design-only. It does not create eval cases, golden files,
runner code, gate integration, CI integration, reports, fixtures, dependencies,
or release artifacts.

## Current State

Status: DESIGN ONLY.

No eval harness is implemented. The repository does not contain:

- `evals/`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- eval fixtures
- eval reports
- eval integration in `scripts/quality_gate.py`
- CI eval integration

## Design Principles

- Local-only by default.
- Deterministic checks before subjective review.
- Machine-readable case definitions and machine-readable output.
- Synthetic fixture input only.
- No private source capture.
- No prompt or session capture.
- No live target access.
- No release publication behavior.
- No CI integration by default.
- Separate owner approval before implementation.

## Non-Goals

- No LLM judge.
- No benchmark against external models.
- No private source capture.
- No prompt or session capture.
- No CI integration by default.
- No downstream application validation.
- No device, PLC, live target, or runtime behavior.
- No release manifest, checksum, SBOM, or provenance generation.
- No replacement for `scripts/quality_gate.py`.

## Candidate Eval 1: Render Structure Eval

Purpose: verify that a template render plan preserves expected structure before
or after rendering.

Planned checks:

- expected files are present in the output path list
- unexpected files are absent from the output path list
- forbidden extensions are rejected or reported
- output paths remain under the approved target root
- output path order is deterministic and stable

Candidate machine-readable fields:

- eval id
- target profile or base-template mode
- input config path
- expected output path list
- forbidden extension list
- expected result
- evidence notes

## Candidate Eval 2: Policy Phrase Eval

Purpose: verify that generated or maintained documents retain required safety
and closeout language.

Planned checks:

- required safety phrases are present
- required approval boundary language is present
- required NOT RUN honesty language is present
- prohibited approval-free live-write language is absent
- missing phrases are reported with document path and phrase id

Candidate machine-readable fields:

- eval id
- document path
- required phrase ids
- prohibited phrase ids
- expected result
- evidence notes

## Candidate Eval 3: Forbidden Artifact Eval

Purpose: verify that template use does not introduce files that would turn the
repository or generated output into a real application, live-device project, or
secret-bearing package.

Planned checks:

- no `.sln`
- no `.csproj`
- no source code files
- no live config
- no secrets
- no workflow files unless explicitly approved
- no device or live-write artifacts

Candidate machine-readable fields:

- eval id
- scan root
- forbidden path patterns
- forbidden extensions
- expected result
- evidence notes

## Candidate Eval 4: Regression / Determinism Eval

Purpose: detect render drift and nondeterministic output planning.

Planned checks:

- repeat the same input
- compare expected output path list across repeated runs
- detect path-list drift
- report added, removed, or reordered planned outputs
- keep content comparison optional and out of the minimal baseline

Candidate machine-readable fields:

- eval id
- repeated input config path
- expected output path list
- comparison mode
- expected result
- evidence notes

## Proposed Future Files

These files are proposed for a future implementation task only. They are not
created by this design step.

- `evals/cases/render_structure.yml`
- `evals/cases/policy_phrases.yml`
- `evals/cases/forbidden_artifacts.yml`
- `evals/golden/`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`

## Proposed Future Output

Future output, if implementation is approved:

- `artifacts/eval-report.json`

The report should be machine-readable and should record:

- basis ref or commit
- eval ids
- command run
- PASS, FAIL, PARTIAL, NOT RUN, or ENVIRONMENT BLOCKED result
- evidence paths
- forbidden-content check result
- unresolved risks

The report path is proposed only. No `artifacts/` directory or eval report is
created by this design step.

## Approval Rule

Implementation requires separate explicit owner approval.

Approval must name the implementation surface, including whether the task may:

- create `evals/`
- create eval case files
- create `evals/golden/`
- create `scripts/run_eval.py`
- create `scripts/gates/eval_gate.py`
- modify `scripts/quality_gate.py`
- generate `artifacts/eval-report.json`
- add dependencies
- integrate with CI

Without that approval, eval work remains documentation-only.

## Stage 4 Boundary

The recommended Stage 4 boundary is an implementation approval decision, not an
implementation by default.

Before approving implementation, decide:

- which candidate evals are required for the first local-only runner
- whether all fixtures can stay synthetic
- whether the runner remains separate from `quality_gate.py`
- whether report generation writes to `artifacts/` or uses stdout only
- whether failed evals are advisory or blocking
- whether CI remains out of scope

## Safety Confirmation

This design does not add:

- eval code
- eval fixtures
- eval reports
- audit logging code
- RAG tooling
- CI workflows
- release artifacts
- real application code
- C# source, solution, project, XAML, or build assets
- PLC/device code
- live target write support
- secrets, credentials, private input, raw source bundles, equipment details,
  IPs, ports, tags, or live parameter values
