# AGENTS.md

## Purpose

This file defines the operating rules for AI/Codex work in this repository.

## Read Order

1. AGENTS.md
2. PRODUCT.md
3. MVP.md
4. STATUS.md
5. ACCEPTANCE_TRACE.md
6. docs/SAFETY_POLICY.md
7. docs/VERIFICATION.md
8. docs/PROFILE_MATRIX.md
9. docs/AI_HANDOFF.md

## P0 Docs-Only Rule

This repository is currently P0 docs-only.

Allowed:
- Edit documentation and markdown templates.
- Clarify contracts, profiles, safety policy, verification policy, and handoff policy.
- Keep changes small and reviewable.

Not allowed in P0:
- Implement render scripts.
- Implement quality gate scripts.
- Implement examples.
- Add real application code.
- Add secrets, private inputs, customer data, equipment details, credentials, keys, or tokens.

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
- Generated code outside the docs-only baseline.

## Side-Effect Policy

Default to read-only inspection first. File writes are allowed only for requested documentation work. Delete, move, external send, database write, live target mutation, and device action require explicit confirmation and are out of P0 scope unless the repository owner changes the phase.

## Verification Plan

For P0 documentation changes, verify:
- Requested files exist.
- README and AGENTS read order match.
- P0 docs-only scope is preserved.
- No executable code or sensitive information was added.
- Links and filenames are coherent.

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
