# AGENTS.md

## Purpose

This file defines the operating rules for AI/Codex work in this repository.

## Read Order

1. AGENTS.md
2. PRODUCT.md
3. MVP.md
4. STATUS.md
5. docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md
6. ACCEPTANCE_TRACE.md
7. docs/SAFETY_POLICY.md
8. docs/VERIFICATION.md
9. docs/PROFILE_MATRIX.md
10. docs/AI_HANDOFF.md

## Current Phase Rule

The historical P0 docs-only baseline and Stage 5B stock practical probe closeout are complete. The repository now includes documentation, profile templates, render tooling, quality gates, minimal example skeletons, and a capability implementation roadmap.

The current implementation sequencing source of truth is `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`. Historical optional/deferred decisions remain risk evidence and approval-boundary evidence, not permanent blockers to the roadmap targets.

Allowed:
- Edit documentation, markdown templates, profiles, examples, tests, and quality gate scripts within the requested scope.
- Keep render behavior dry-run first for examples.
- Preserve the safety boundary around private data and live targets.

Not allowed by default:
- Add real application code.
- Add PLC/device connection code.
- Add live device write, start, stop, reset, or mode-change behavior.
- Add secrets, private inputs, customer data, equipment details, credentials, keys, or tokens.
- Broaden render targets to arbitrary repo-internal directories outside `examples/<name>`.

## Task Contract

Before editing, identify:
- Goal.
- Scope.
- Files expected to change.
- Files and areas that must not be touched.
- Verification expected for the task.

## No-Touch Zones

Do not add or expose:
- Secrets or credentials.
- Private raw input.
- Sensitive business source text.
- Device addresses, equipment parameters, or live-control values.
- Generated application code outside an explicitly approved future phase.

## Side-Effect Policy

Default to read-only inspection first. File writes are allowed only for requested repository work. Delete, move, external send, database write, live target mutation, and device action require explicit confirmation.

## Verification Plan

For the current template repository, verify:
- README and AGENTS read order match.
- Required root documents exist.
- Base templates and profile templates are present.
- Render script supports dry-run example rendering.
- Quality gate includes docs, repo hygiene, template schema, secret scan, and example validation.
- No real application code or sensitive information was added.

## Handoff Rules

When work ends, report:
- Files changed.
- Commands or GitHub actions used.
- Verification result.
- Safety checks.
- Risks and assumptions.
- Next recommended step.

## Closeout Receipt

Every completed task should include outcome, changed files, verification result, safety checks, unresolved risks, and next step.
