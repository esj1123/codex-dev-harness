# PHASE_PLAN.md

## Purpose

Define phase-gated work for `plc_tool_minimal`.

## Phase Table

| phase | goal | allowed work | verification | exit criteria | status |
|---|---|---|---|---|---|
| P0 | Docs skeleton | Rendered markdown only | quality gate | required docs exist | seed |
| P1 | Simulator/mock planning | downstream-only plan | review | approval recorded | not started |
| P2 | Runtime implementation | out of this example | simulator/mock checks | downstream decision | not started |

## Current Phase

P0 docs skeleton.

## Phase Rules

- Do not add device code in this regression example.
- Do not add live configuration.
- Keep live behavior prohibited.
- Use dry-run render before overwriting generated docs.

