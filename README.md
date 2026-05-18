# codex-dev-harness

P0 docs-only baseline for a reusable Agentic Development Repo Template.

This repository is a governed coding workflow template for projects that use AI/Codex to inspect, modify, verify, and hand off software work. The word harness is used as a short repo name, but the scope is broader than a test runner. The target system includes task contracts, agent instructions, side-effect boundaries, verification, and closeout discipline.

## P0 Scope

P0 is documentation only.

In scope:
- Define the baseline repo contract.
- Define read order and AI/Codex operating rules.
- Define product, MVP, roadmap, status, acceptance trace, safety, verification, and handoff documents.
- Provide base markdown templates.

Out of scope:
- Render scripts.
- Quality gate implementation.
- Example project implementation.
- Real application code.
- Secrets, private inputs, or live system configuration.

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

## Repository Structure

- AGENTS.md
- README.md
- PRODUCT.md
- MVP.md
- ROADMAP.md
- STATUS.md
- ACCEPTANCE_TRACE.md
- code_review.md
- docs/HARNESS_SPEC.md
- docs/PROFILE_MATRIX.md
- docs/SAFETY_POLICY.md
- docs/AI_HANDOFF.md
- docs/VERIFICATION.md
- templates/base/AGENTS.md.template
- templates/base/README.md.template
- templates/base/PRODUCT.md.template
- templates/base/MVP.md.template
- templates/base/STATUS.md.template
- templates/base/ACCEPTANCE_TRACE.md.template

## Core Principles

- One-agent-first: begin with one accountable AI/Codex worker before adding orchestration.
- Read-only first: inspect and summarize before changing files.
- Explicit side-effect boundary: live writes, deletes, moves, external sends, database writes, and device actions require explicit confirmation.
- Verification mesh: tests, smoke checks, acceptance trace, policy validation, and audit evidence are separate but connected.
- Private data protection: use synthetic fixtures and summaries instead of private raw input.
- Closeout receipt: every completed task reports changed files, checks run, safety checks, risks, and next steps.

## Current Status

This repo is at P0 docs-only baseline. No scripts, generated examples, or executable project code are included yet.
