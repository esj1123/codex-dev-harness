# Eval Policy

## Purpose

Define evaluation policy for codex-dev-harness eval work while preserving the
current documentation-first, local-first baseline.

This policy document is documentation-only. It records the current standalone
local eval harness boundary and does not by itself add new eval code, create
new fixture categories, add dependencies, integrate evals into quality gates,
or install CI.

## Current State

Eval planning is present in `docs/OPTIONAL_EVAL_HARNESS_PLAN.md`.

A minimal local-only eval harness is documented in
`docs/MINIMAL_EVAL_HARNESS_DESIGN.md` and implemented as a standalone local
runner.

The current implementation includes expanded named cases under `evals/cases/`,
`evals/golden/`, `scripts/run_eval.py`, `scripts/gates/eval_gate.py`, and
tests. It remains standalone: there is no eval integration in
`scripts/quality_gate.py`, no CI integration, no external service call, and no
LLM judge.

The default local runner discovers all `evals/cases/*.yml` files in
deterministic order. Current named cases cover render structure, render
determinism, approval boundaries, NOT RUN honesty, PLC/device safety, forbidden
C# artifacts, forbidden live config, forbidden secret patterns, prompt contract
completeness, release manifest shape, checksum shape, SBOM shape, and
provenance shape.

## Eval Principles

Eval work should be:

- optional until explicitly promoted
- local-first
- dry-run or read-only by default
- synthetic-fixture-only
- source-index driven
- narrow enough to explain failures
- separate from release publication
- recorded with PASS, FAIL, PARTIAL, or NOT RUN evidence

## Allowed Eval Subjects

Future evals may check documentation and template behavior, such as:

- rendered document structure
- forbidden artifact absence
- required safety phrases
- approval-gate presence
- prompt/task contract completeness
- downstream scaffold remains design-only
- deterministic render output path planning

## Prohibited Eval Inputs

Eval fixtures and records must not include:

- private raw input
- raw source bundles
- sensitive requirement text
- secrets, credentials, tokens, or account material
- equipment IPs, ports, tags, or live parameter values
- live configuration
- application source copied from downstream projects

## Implementation Approval

Separate explicit owner approval is required before:

- adding new eval fixture categories beyond the current synthetic/repo-internal cases
- adding grader code
- making eval report generation part of routine verification
- adding dependencies
- wiring evals into `quality_gate.py`
- adding evals to CI
- making evals release-blocking

## Eval Output

Future eval output should record:

- eval id
- purpose
- basis ref or commit
- input fixture category
- command run
- result
- evidence path
- NOT RUN reason when applicable
- prohibited-content check

The optional output path is `artifacts/eval-report.json`, as documented in
`docs/MINIMAL_EVAL_HARNESS_DESIGN.md`. That output path is not created by
default; it is produced only when `scripts/run_eval.py` is called with
`--report`.

The report format includes `schema_version`, `generated_at_utc`, `total_cases`,
`passed_cases`, `failed_cases`, and per-case results with stable case names.
The `--report` value must be a repo-internal relative path under `artifacts/`.
Absolute paths, parent traversal with `..`, and repo-internal non-artifact
paths are rejected so local eval evidence cannot be written outside the
approved evidence directory by the report option.

Generating an eval report remains explicit and optional. Making eval reports
routine, release-blocking, CI-driven, or part of `scripts/quality_gate.py`
requires separate approval.

## Non-Goals

This policy does not add release verification code, CI workflows, manifest artifacts, SBOM/provenance artifacts, profiles, examples, application code, C# project assets, PLC/device code, or live-write behavior.
