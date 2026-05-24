# Post v0.1.0 Roadmap

## Purpose

Record the post-v0.1.0 operating direction for codex-dev-harness without starting new implementation work.

This document is planning-only. It does not create an eval harness, CI workflow, SBOM, provenance bundle, new profile, example project, or application code.

## Current Baseline

Current baseline: `v0.1.0`.

The formal v0.1.0 baseline is a local-first governed template for downstream project adoption. It includes base templates, selected profile templates, render tooling, quality gates, regression examples, local verification, release records, clean clone validation, and downstream adoption documentation.

## Next Priority

Next priority: downstream feedback or small governance refinements.

The most useful post-v0.1.0 signal is how the base template behaves when applied to real downstream planning targets. Feedback should focus on documentation clarity, safety boundaries, approval gates, source indexing, and render ergonomics before adding new automation.

The optional design-stage pack is now a closed manual-use-only baseline. Its templates can be copied, merged, skipped, or used for review-only downstream work, but they are not part of the base render path.

The first lightweight governance docs are present:

- `docs/PROMPT_PATTERNS.md`
- `docs/BUG_REVIEW_TEMPLATE.md`
- `docs/SIMPLIFICATION_CHECKLIST.md`

## Optional Improvement Sequence

1. Release page decision.
2. Local package checklist.
3. Lightweight governance docs.
4. Eval harness plan.
5. Release manifest/checksum.
6. SBOM/provenance.
7. Optional CI actualization.

Each item is optional and should remain approval-gated. Planning a future capability does not authorize implementing it.

## Optional Design-Stage Pack Status

Status: MANUAL-USE-ONLY BASELINE CLOSED.

- Template files exist under `templates/optional/design_stage/`.
- Usage guide exists.
- Review record is refreshed.
- Manual feedback 001 and 002 are documented.
- All seven optional design-stage templates have PASS manual-use evidence.
- Render integration is deferred.
- Gate integration is deferred.
- Example integration is deferred.
- Future integration requires separate owner approval.

Potential future integration should be considered only if repeated manual-use friction, repeated copy/rename errors, opt-in render demand, or optional-pack validation demand appears.

## Lightweight Governance Docs

Status: PRESENT.

- Prompt patterns: present.
- Bug review template: present.
- Simplification checklist: present.

These documents support better task contracts, evidence-based bug review, and restraint before adding new repo surface. They do not add code, gates, examples, eval harnesses, workflows, profiles, or runtime behavior.

## Profile Policy

Do not add profiles casually.

A new profile should require repeated downstream reuse evidence, a stable tool/runtime boundary, and a clear difference from the base template plus existing profiles. One-off downstream projects should usually remain downstream candidates rather than built-in profiles.

## Scenario Simulator Status

Scenario simulator remains a downstream application candidate, not a built-in profile.

The base template surfaces, especially `SOURCE_INDEX`, `PROJECT_BOUNDARY`, `DATA_SCOPE`, `PHASE_PLAN`, and `APPROVALS`, are the intended mechanism for adapting to complex downstream projects without creating a dedicated profile for each domain.

## Non-Goals

- Do not implement an eval harness in this step.
- Do not create `evals/` or `scripts/run_eval.py`.
- Do not create SBOM/provenance artifacts.
- Do not install GitHub Actions workflows.
- Do not add a new profile.
- Do not add `profiles/scenario_simulator`.
- Do not add `examples/scenario_simulator_minimal`.
- Do not add optional design-stage render, gate, or example integration without separate approval.
- Do not add application, C#, PLC/device, or live-write code.

## Next Review

Review downstream adoption feedback and use the lightweight governance docs before deciding whether release page publication, local packaging, audit log planning, eval harness work, SBOM/provenance, CI, or any optional design-stage integration adds enough value to justify a follow-up task.
