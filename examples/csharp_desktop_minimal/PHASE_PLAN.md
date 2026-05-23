# PHASE_PLAN.md

## Purpose

Define phase-gated work for `csharp_desktop_minimal`.

## Phase Table

| phase | goal | allowed work | verification | exit criteria | status |
|---|---|---|---|---|---|
| P0 | Docs skeleton | Rendered markdown only | quality gate | required docs exist | seed |
| P1 | Desktop project planning | downstream-only plan | review | approval recorded | not started |
| P2 | Runtime implementation | out of this example | build/test/smoke | downstream decision | not started |

## Current Phase

P0 docs skeleton.

## Phase Rules

- Do not add C# source, solution, project, or script files in this regression example.
- Keep build, test, and smoke as NOT RUN.
- Use dry-run render before overwriting generated docs.

