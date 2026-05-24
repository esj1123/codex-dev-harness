# Eval Policy

## Purpose

Define how future eval work should be governed without implementing an eval harness in the current Stage 1 documentation closure.

This document is policy-only. It does not create `evals/`, `scripts/run_eval.py`, eval fixtures, graders, gate modules, dependencies, or CI integration.

## Current State

Eval harness status: DEFERRED.

The repository has an optional eval harness plan in `docs/OPTIONAL_EVAL_HARNESS_PLAN.md`, but no eval runner or eval corpus exists.

## Eval Scope Principles

Future evals should be:

- local-first
- synthetic-only unless separately approved
- deterministic where practical
- focused on repository governance behavior
- separate from real application validation
- explicit about NOT RUN results
- safe against private input, secrets, live values, and raw source bundles

## Candidate Eval Categories

| category | purpose | implementation status |
|---|---|---|
| render structure | Verify expected rendered documentation shape | deferred |
| forbidden artifact | Detect generated code, workflows, live config, or prohibited files | deferred |
| policy phrase | Check required safety and approval language | deferred |
| downstream scaffold | Check design-only downstream generated docs remain source-index driven | deferred |
| prompt contract | Check task contracts preserve scope, no-touch zones, and verification expectations | deferred |

## Approval Requirements

Separate owner approval is required before:

- creating an `evals/` directory
- creating eval fixtures or golden outputs
- creating `scripts/run_eval.py`
- adding an eval gate to `scripts/quality_gate.py`
- adding dependencies for eval work
- making evals release-blocking
- integrating evals into CI

## Eval Evidence Expectations

If approved later, eval output should record:

- eval run id
- repo commit
- case id
- input fixture identity
- expected result
- actual result
- PASS, FAIL, or NOT RUN status
- failure reason
- forbidden artifact hits, if any
- command used

## Non-Goals

This policy does not approve:

- eval harness implementation
- runtime or application tests
- model benchmarking
- private data fixtures
- live target validation
- CI workflow installation
