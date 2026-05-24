# Minimal Eval Harness Design

## Purpose

Document the minimal, local-only eval harness for codex-dev-harness.

The harness provides machine-readable verification for template safety and
regression behavior. It checks whether generated or rendered template outputs
preserve expected file structure, required policy language, forbidden artifact
boundaries, and deterministic output path behavior.

The implementation is intentionally minimal and standalone. It does not use an
LLM judge, external services, private input, prompt/session capture, CI, release
artifacts, or live target behavior.

## Current State

Status: MINIMAL STANDALONE IMPLEMENTATION PRESENT.

The repository contains:

- `evals/cases/render_structure.yml`
- `evals/cases/policy_phrases.yml`
- `evals/cases/forbidden_artifacts.yml`
- `evals/golden/render_structure_paths.txt`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- `tests/test_run_eval.py`
- `tests/test_eval_gate.py`

The harness remains separate from `scripts/quality_gate.py`. CI eval integration
is not installed. No eval report is generated unless `scripts/run_eval.py` is
called with `--report`.

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
- Standalone first; promotion into `quality_gate.py` requires separate approval.

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

Implemented machine-readable fields:

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

Implemented machine-readable fields:

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

Implemented machine-readable fields:

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

Implemented machine-readable fields:

- eval id
- repeated input config path
- expected output path list
- comparison mode
- expected result
- evidence notes

## Implemented Files

These files are present in the minimal standalone implementation:

- `evals/cases/render_structure.yml`
- `evals/cases/policy_phrases.yml`
- `evals/cases/forbidden_artifacts.yml`
- `evals/golden/render_structure_paths.txt`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- `tests/test_run_eval.py`
- `tests/test_eval_gate.py`

## Optional Output

Optional output:

- `artifacts/eval-report.json`

The report should be machine-readable and should record:

- basis ref or commit
- eval ids
- command run
- PASS, FAIL, PARTIAL, NOT RUN, or ENVIRONMENT BLOCKED result
- evidence paths
- forbidden-content check result
- unresolved risks

The report is not written by default. It is produced only when `scripts/run_eval.py`
is called with `--report`.

## Approval Rule

Implementation of the minimal standalone runner is approved for this stage.
Further expansion requires separate explicit owner approval.

Approval must name the implementation surface, including whether the task may:

- modify `scripts/quality_gate.py`
- generate `artifacts/eval-report.json`
- add dependencies
- integrate with CI

Without that approval, the eval harness remains standalone and local-only.

## Future Boundary

The recommended next boundary is a promotion decision, not automatic expansion.

Before approving any expansion, decide:

- whether the runner remains separate from `quality_gate.py`
- whether report generation should become part of routine verification
- whether failed evals are advisory or blocking
- whether CI remains out of scope

## Safety Confirmation

This implementation does not add:

- eval reports by default
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
