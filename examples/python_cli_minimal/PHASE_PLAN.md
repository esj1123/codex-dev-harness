# PHASE_PLAN.md

## Purpose

Define phase-gated work for `python_cli_minimal`.

## Phase Table

| phase | goal | allowed work | verification | exit criteria | status |
|---|---|---|---|---|---|
| P0 | Docs skeleton | Rendered markdown only | quality gate | required docs exist | seed |
| P1 | Runtime planning | downstream-only plan | review | approval recorded | not started |
| P2 | Runtime implementation | out of this example | pytest and CLI smoke | downstream decision | not started |

## Current Phase

P0 docs skeleton.

## Phase Rules

- Do not add Python runtime code in this regression example.
- Keep pytest and CLI smoke as NOT RUN until a downstream project implements code.
- Use dry-run render before overwriting generated docs.

