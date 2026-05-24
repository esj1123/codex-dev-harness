# Eval Policy

## Purpose

Define evaluation policy for future codex-dev-harness eval work while preserving the current documentation-first, local-first baseline.

This policy is documentation-only. It does not implement an eval harness, create eval fixtures, add dependencies, integrate gates, or install CI.

## Current State

Eval planning is present in `docs/OPTIONAL_EVAL_HARNESS_PLAN.md`.

Minimal eval harness implementation remains missing and deferred. There is no `evals/` directory, no `scripts/run_eval.py`, no grader implementation, and no eval integration in `scripts/quality_gate.py`.

## Eval Principles

Future evals should be:

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

- creating `evals/`
- creating `scripts/run_eval.py`
- adding eval fixtures
- adding grader code
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

A dedicated machine-readable eval output format is deferred until implementation is approved.

## Non-Goals

This policy does not add eval code, release verification code, CI workflows, manifest artifacts, SBOM/provenance artifacts, profiles, examples, application code, C# project assets, PLC/device code, or live-write behavior.
