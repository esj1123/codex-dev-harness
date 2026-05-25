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

The minimal local-only eval harness is present:

- `docs/MINIMAL_EVAL_HARNESS_DESIGN.md`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- `evals/cases/`
- `evals/golden/`

This is a standalone local implementation. It does not use an LLM judge, call
external services, install CI, generate reports by default, or join
`scripts/quality_gate.py`.

Release bundle and manifest policy is present:

- `docs/RELEASE_BUNDLE_POLICY.md`
- `docs/RELEASE_MANIFEST_POLICY.md`

Local manifest/checksum generation is also present:

- `scripts/generate_manifest.py`
- `scripts/generate_checksums.py`
- `artifacts/release-manifest.json`
- `artifacts/checksums.sha256`

These generators are local-only and restricted to repo-relative `artifacts/`
paths. They do not create release archives, tags, release publication, SBOM,
provenance, or CI workflows.

SBOM/provenance planning is present:

- `docs/SBOM_PROVENANCE_PLAN.md`

The plan defines future SPDX, CycloneDX, and in-toto evidence scope without
adding generators, dependencies, artifacts, CI workflows, signatures, tags,
release publication, application code, or live-write behavior.

## Optional Improvement Sequence

1. Release page decision.
2. Local package checklist.
3. Lightweight governance docs.
4. Eval harness plan and design.
5. Minimal standalone eval harness implementation.
6. Release bundle and manifest policy.
7. Release manifest/checksum generator.
8. SBOM/provenance planning.
9. SBOM/provenance implementation, if separately approved.
10. Optional CI actualization.

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

## Minimal Eval Harness

Status: MINIMAL STANDALONE IMPLEMENTATION PRESENT.

`docs/MINIMAL_EVAL_HARNESS_DESIGN.md` defines the local-only eval harness for
machine-readable verification of template safety and regression behavior.

The implementation covers:

- render structure eval
- policy phrase eval
- forbidden artifact eval
- regression/determinism eval

The runner remains standalone. Future expansion requires separate owner approval
before adding external services, an LLM judge, extra dependencies, routine eval
report generation, `scripts/quality_gate.py` integration, release-blocking evals,
or CI integration.

## Release Bundle And Manifest Policy

Status: POLICY AND LOCAL MANIFEST/CHECKSUM GENERATION PRESENT.

`docs/RELEASE_BUNDLE_POLICY.md` defines future bundle components such as
`release-manifest.json`, `checksums.sha256`, optional eval reports, optional
SBOM/provenance files, human-readable closeout, and optional redacted audit
sessions.

`docs/RELEASE_MANIFEST_POLICY.md` defines manifest fields including
repository basis, Python version, included roots, excluded patterns,
verification commands, quality gates, optional eval summary, example render
dry-runs, and per-file size/SHA-256 records.

`scripts/generate_manifest.py` and `scripts/generate_checksums.py` generate
local-only `artifacts/release-manifest.json` and `artifacts/checksums.sha256`
when explicitly run. They do not create a release archive, SBOM, provenance,
CI workflow, tag, or GitHub Release.

## SBOM And Provenance Plan

Status: PLANNING PRESENT.

`docs/SBOM_PROVENANCE_PLAN.md` defines why SBOM/provenance can help even for a
template repository, how future SBOM/provenance evidence should relate to
`release-manifest.json` and checksums, and minimal future scope for:

- SPDX JSON
- CycloneDX JSON
- in-toto provenance

This is documentation-only. No `scripts/generate_sbom.py`,
`scripts/generate_provenance.py`, `artifacts/sbom.spdx.json`,
`artifacts/sbom.cdx.json`, or `artifacts/provenance.intoto.jsonl` exists.

## Profile Policy

Do not add profiles casually.

A new profile should require repeated downstream reuse evidence, a stable tool/runtime boundary, and a clear difference from the base template plus existing profiles. One-off downstream projects should usually remain downstream candidates rather than built-in profiles.

## Scenario Simulator Status

Scenario simulator remains a downstream application candidate, not a built-in profile.

The base template surfaces, especially `SOURCE_INDEX`, `PROJECT_BOUNDARY`, `DATA_SCOPE`, `PHASE_PLAN`, and `APPROVALS`, are the intended mechanism for adapting to complex downstream projects without creating a dedicated profile for each domain.

## Non-Goals

- Do not add external-service evals.
- Do not add an LLM judge.
- Do not make evals release-blocking without approval.
- Do not wire evals into `scripts/quality_gate.py` without approval.
- Do not generate eval reports by default.
- Do not generate release bundles or release archives without approval.
- Do not regenerate release manifests or checksums outside an explicit release
  evidence task.
- Do not create SBOM/provenance artifacts or generators without separate
  approval.
- Do not install GitHub Actions workflows.
- Do not add a new profile.
- Do not add `profiles/scenario_simulator`.
- Do not add `examples/scenario_simulator_minimal`.
- Do not add optional design-stage render, gate, or example integration without separate approval.
- Do not add application, C#, PLC/device, or live-write code.

## Next Review

Review downstream adoption feedback, the lightweight governance docs, and the
standalone eval harness before deciding whether quality-gate integration,
release page publication, local packaging, release bundle generation, audit log
generation, SBOM/provenance implementation, CI, or any optional design-stage
integration adds enough value to justify a follow-up task.
