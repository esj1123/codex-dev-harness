# AGENTS.md

## Purpose

This file defines the operating rules for AI/Codex work in this repository.

## Read Order

1. AGENTS.md
2. docs/AUTHORITY_MANIFEST.json
3. PRODUCT.md
4. MVP.md
5. STATUS.md
6. docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md
7. docs/SAFETY_POLICY.md
8. docs/VERIFICATION.md
9. docs/AI_HANDOFF.md

## Current Phase Rule

The harness is `READY_FOR_PARALLEL_APPLICATION_DEVELOPMENT`. Its first
greenfield application pilot passed, and work-package schema v2 now enforces
Windows-safe path ownership, shared contract freeze, actual-diff postflight,
and explicit separation between structural PASS and owner authorization.

`docs/AUTHORITY_MANIFEST.json` separates current authority, durable policy, and
historical evidence. The current implementation sequencing source of truth is
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`. A feature lane that needs to
change `contract_frozen_paths` must stop with `CONTRACT_CHANGE_REQUIRED` and
return to the integration owner.

Allowed:
- Edit documentation, markdown templates, profiles, examples, tests, and quality gate scripts within the requested scope.
- Keep render behavior dry-run first for examples.
- Preserve the safety boundary around private data and live targets.
- Use separately approved disjoint feature lanes under the work-package v2 contract.

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
