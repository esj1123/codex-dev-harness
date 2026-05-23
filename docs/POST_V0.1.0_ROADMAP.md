# Post v0.1.0 Roadmap

## Purpose

Record the post-v0.1.0 operating direction for codex-dev-harness without starting new implementation work.

This document is planning-only. It does not create an eval harness, CI workflow, SBOM, provenance bundle, new profile, example project, or application code.

## Current Baseline

Current baseline: `v0.1.0`.

The formal v0.1.0 baseline is a local-first governed template for downstream project adoption. It includes base templates, selected profile templates, render tooling, quality gates, regression examples, local verification, release records, clean clone validation, and downstream adoption documentation.

## Next Priority

Next priority: downstream adoption feedback.

The most useful post-v0.1.0 signal is how the base template behaves when applied to real downstream planning targets. Feedback should focus on documentation clarity, safety boundaries, approval gates, source indexing, and render ergonomics before adding new automation.

## Optional Improvement Sequence

1. Release page decision.
2. Local package checklist.
3. Eval harness plan.
4. Release manifest/checksum.
5. SBOM/provenance.
6. Optional CI actualization.

Each item is optional and should remain approval-gated. Planning a future capability does not authorize implementing it.

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
- Do not add application, C#, PLC/device, or live-write code.

## Next Review

Review downstream adoption feedback first, then decide whether release page publication or local packaging adds enough value to justify a follow-up task.
