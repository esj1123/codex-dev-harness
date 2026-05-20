# codex-dev-harness

Reusable Agentic Development Repo Template for governed AI/Codex coding workflows.

This repository is a governed coding workflow template for projects that use AI/Codex to inspect, modify, verify, and hand off software work. The word harness is used as a short repo name, but the scope is broader than a test runner. The target system includes task contracts, agent instructions, side-effect boundaries, verification, example validation, and closeout discipline.

## Current State

The repository has moved beyond the historical P0 docs-only baseline. It currently includes:

- Root contract documents.
- Base markdown templates.
- Profile templates for `python_cli`, `csharp_desktop`, and `plc_or_device_tool`.
- A config-driven render script.
- A base quality gate.
- Minimal example skeletons under `examples/`.
- Tests for render and gate behavior.

No real application code, PLC/device code, live target configuration, secrets, or private raw input is included.

## Historical P0 Scope

P0 was the initial docs-only baseline.

In scope at P0:
- Define the baseline repo contract.
- Define read order and AI/Codex operating rules.
- Define product, MVP, roadmap, status, acceptance trace, safety, verification, and handoff documents.
- Provide base markdown templates.

Out of scope at P0:
- Render scripts.
- Quality gate implementation.
- Example projects.
- Real application code.
- Secrets, private inputs, or live system configuration.

Those items are no longer described as current absence. Render script, quality gate, profile templates, and example skeletons now exist.

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
- docs/
- templates/base/
- profiles/
- scripts/
- scripts/gates/
- examples/
- tests/
- template.config.example.yml

## Core Principles

- One-agent-first: begin with one accountable AI/Codex worker before adding orchestration.
- Read-only first: inspect and summarize before changing files.
- Explicit side-effect boundary: live writes, deletes, moves, external sends, database writes, and device actions require explicit confirmation.
- Verification mesh: tests, smoke checks, acceptance trace, policy validation, example validation, and audit evidence are separate but connected.
- Private data protection: use synthetic fixtures and summaries instead of private raw input.
- Closeout receipt: every completed task reports changed files, checks run, safety checks, risks, and next steps.

## Validation

Use the quality gate and dry-run renderer before treating the template as healthy:

- `python -m pip install -r requirements-dev.txt`
- `python -m pytest`
- `python scripts/quality_gate.py`
- `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`
- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

CI policy is documented in `docs/CI_POLICY.md`. No workflow is included in the current baseline.

## Local-First Usage

The intended baseline workflow is local-first:
- clone the repository
- install development requirements
- run local verification
- dry-run example rendering
- review expected target paths
- apply generated docs to a separate target project only after review

See `docs/LOCAL_USAGE.md` for the full local usage flow and `docs/LOCAL_RELEASE_PACKAGE.md` for local package boundaries.

CI remains optional and is not a baseline requirement.
