# Bug Review Template

## Purpose

Provide a lightweight template for tracking failures, bugs, or regressions without expanding the fix scope.

This template is documentation-only. It does not implement fixes, create tests, or approve runtime changes by itself.

## Issue Summary

- Issue id: TBD
- Date: TBD
- Reporter: TBD
- Affected area: TBD
- Severity: TBD

## Observed Behavior

Describe what happened using evidence. Avoid guessing.

## Expected Behavior

Describe the expected behavior or contract.

## Affected Files

| file | role | notes |
|---|---|---|
| TBD | TBD | TBD |

## Reproduction / Verification

| command or check | result | evidence |
|---|---|---|
| TBD | NOT RUN | TBD |

## Root Cause Hypothesis

State hypotheses only when supported by evidence.

| hypothesis | evidence | confidence |
|---|---|---|
| TBD | TBD | LOW |

## Fix Boundary

Define the smallest allowed fix.

- In scope: TBD
- Out of scope: TBD
- No-touch areas: TBD
- Approval required before broader changes: TBD

## Regression Risk

| risk | impact | mitigation |
|---|---|---|
| TBD | TBD | TBD |

## Follow-Up Prevention

- Add or update verification only when appropriate.
- Improve task contract if the bug came from unclear scope.
- Add documentation if the behavior is a policy or usage issue.
- Avoid adding broad abstractions unless repeated failures justify them.

## AI/Codex Review Rules

- Do not guess root cause.
- Do not state cause without evidence.
- Do not broaden fix scope without approval.
- Do not hide NOT RUN verification.
- Record commands and verification results.
- Preserve unrelated user changes.
- Keep sensitive values and private source content out of the review.

## Closeout

| item | status | notes |
|---|---|---|
| root cause supported by evidence | TBD | TBD |
| fix boundary respected | TBD | TBD |
| verification recorded | TBD | TBD |
| follow-up prevention identified | TBD | TBD |
