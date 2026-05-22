# ADR-0002 Base Template Over Domain Profile

## Status

Accepted.

## Context

The template may be used for many project types. Creating a profile for every downstream application type would make the repository harder to maintain and would blur the line between a template system and application-specific design.

Scenario simulator work is a downstream application candidate, not a built-in profile by default.

## Decision

Prefer base template extensions for broadly reusable governance controls.

Do not create a domain-specific profile unless repeated use proves a durable, safety-relevant workflow variant and the change is explicitly approved.

## Consequences

- `SOURCE_INDEX.md`, `PROJECT_BOUNDARY.md`, `DATA_SCOPE.md`, `PHASE_PLAN.md`, and `APPROVALS.md` are base templates.
- Existing profiles remain regression/example variants.
- Scenario simulator adaptation is documented as downstream usage.
- Profile additions are approval-gated side effects.
