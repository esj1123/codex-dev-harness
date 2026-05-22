# ADR-0003 Approval Gated Side Effect

## Status

Accepted.

## Context

Agentic development can cross important boundaries: writing files, overwriting target docs, mutating external services, enabling CI, publishing releases, or interacting with live targets.

The template must keep these actions explicit.

## Decision

Side-effecting actions are approval-gated.

Default behavior:
- read-only first
- dry-run first
- expected changes review
- explicit approval before mutation

## Consequences

- Render writes require an explicit target and should be preceded by dry-run.
- Profile additions require approval.
- CI workflow installation requires approval.
- GitHub Release publication requires approval.
- Live target write support remains out of scope for this template baseline.
