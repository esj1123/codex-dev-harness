# ADR-0001 Local First

## Status

Accepted.

Amended by the current verification policy: local inspection, focused checks,
render preview, and explicit write intent remain the baseline. The repository
now also installs a manual read-only Hosted Integration Verify workflow so an
approved exact SHA can run the integration command set without duplicating the
long Full run locally. This amendment does not add automatic CI, required
checks, release, publication, deployment, secrets, or live-write behavior.

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
- Manual hosted verification is installed but remains approval-gated and exact-SHA bound.
- Local verification records are first-class release evidence.
- Downstream users can adopt the template without cloud infrastructure.
