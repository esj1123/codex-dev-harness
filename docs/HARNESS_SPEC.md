# HARNESS_SPEC.md

## Purpose

Define what harness means in this repository.

## Definition

Harness is the repeatable execution and verification support layer inside a broader governed agentic development system. It is not the whole system.

## Broader System Layers

1. Task contract layer.
2. Instruction/profile layer.
3. Capability bus.
4. Side-effect boundary.
5. Verification mesh.
6. Governance/audit plane.

## Historical P0 Harness Scope

P0 defined the harness concept through documentation only.

At P0, the repo did not include:
- Runner implementation.
- Render script.
- Quality gate implementation.
- Test automation.
- Example application code.

## Current Harness Scope

The current repository includes:
- Documentation contracts.
- Base templates.
- Profile templates.
- Dry-run render support.
- Quality gate support.
- Example skeleton validation.

The current repository still does not include real application code, real PLC/device code, live target writes, or secret/config generation.

## Core Defaults

- One-agent-first.
- Read-only first.
- Dry-run before apply.
- Explicit confirmation for side effects.
- Evidence-driven closeout.
- Example validation before release readiness.
