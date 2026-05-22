# ADR-0001 Local First

## Status

Accepted.

## Context

codex-dev-harness is intended to be cloned, inspected, verified, and rendered locally before any downstream adoption.

Cloud CI and release automation can be useful later, but they are not required for the baseline and can obscure the safety boundary if introduced too early.

## Decision

The baseline remains local-first.

Required workflow:
- clone locally
- install development requirements
- run local verification
- run render dry-runs
- review target paths
- render only after explicit local intent

## Consequences

- GitHub Actions remain optional.
- No `.github/workflows` file is installed by default.
- Local verification records are first-class release evidence.
- Downstream users can adopt the template without cloud infrastructure.
