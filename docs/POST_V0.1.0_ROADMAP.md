# Post v0.1.0 Roadmap

## Purpose

Record the post-v0.1.0 operating direction for codex-dev-harness without starting new implementation work.

This document is planning-only. It does not create an active CI workflow,
release publication path, eval harness expansion, SBOM/provenance expansion,
RAG index, model comparison tool, new profile, example project, or application
code.

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
paths. By themselves they do not create release archives, tags, release
publication, SBOM, provenance, or CI workflows. SBOM and provenance are handled
by separate minimal local generators described below.

SBOM/provenance planning and minimal local implementation are present:

- `docs/SBOM_PROVENANCE_PLAN.md`
- `scripts/generate_sbom.py`
- `scripts/generate_provenance.py`
- `artifacts/sbom.spdx.json`
- `artifacts/sbom.cdx.json`
- `artifacts/provenance.intoto.jsonl`

The plan defines SPDX, CycloneDX, and in-toto evidence scope. The minimal local
implementation is standard-library-only and does not add external metadata
resolution, CI workflows, signatures, tags, release publication, application
code, or live-write behavior.

Approved-corpus RAG and model/prompt change planning is present:

- `docs/APPROVED_CORPUS_RAG_PLAN.md`
- `docs/MODEL_CHANGE_POLICY.md`

These documents define future local approved-corpus and model-change evidence
boundaries. They do not create `retrieval/`, `index/`, embeddings, vector
storage, RAG dependencies, model comparison code, prompt capture, model output
capture, external service calls, CI workflows, application code, or live-write
behavior.

Optional CI actualization decision and release verification template planning
are present:

- `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`
- `templates/ci/github-actions-release-verify.yml.template`

The decision keeps local-first verification as the baseline and treats CI as
template-only support for downstream forks. The optional release verification
template is not installed under `.github/workflows/`, requires no secrets, uses
read-only permissions, does not upload artifacts, and does not publish, sign,
tag, deploy, or write to live targets.

Additional local target experiment plans are present:

- `docs/LOCAL_TARGET_EXPERIMENT_PLAN_csharp_desktop.md`
- `docs/LOCAL_TARGET_EXPERIMENT_PLAN_plc_tool.md`

These plans define future dry-run-first, approval-gated, separate temporary
target experiments for existing profile templates. They are planning-only and
do not execute target renders, create downstream target folders, add C# or
PLC/device code, create live configuration, generate release artifacts, or
install workflows.

The post-v0.1.0 evidence baseline closeout is present:

- `docs/POST_V0.1.0_EVIDENCE_BASELINE_CLOSEOUT.md`

The closeout summarizes completed Stage 0-14 evidence surfaces, current
verification state, deferred surfaces, and future approval boundaries. It is
documentation-only and does not regenerate artifacts or change generator, eval,
CI, release, target render, application, device, or live-write behavior.

## Optional Improvement Sequence

1. Release page decision.
2. Local package checklist.
3. Lightweight governance docs.
4. Eval harness plan and design.
5. Minimal standalone eval harness implementation.
6. Release bundle and manifest policy.
7. Release manifest/checksum generator.
8. SBOM/provenance planning.
9. SBOM/provenance expansion, signing, or publication decision, if separately approved.
10. Python runtime reproducibility.
11. Approved-corpus RAG and model-change policy planning.
12. Optional CI actualization decision and template-only release verification.
13. Additional local target experiment planning for existing profiles.
14. Post-v0.1.0 evidence baseline closeout.

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

Status: MINIMAL LOCAL IMPLEMENTATION PRESENT.

`docs/SBOM_PROVENANCE_PLAN.md` defines why SBOM/provenance can help even for a
template repository, how SBOM/provenance evidence should relate to
`release-manifest.json` and checksums, and minimal future scope for:

- SPDX JSON
- CycloneDX JSON
- in-toto provenance

Minimal local generators and artifacts exist. They do not add external metadata
lookup, signing, release publication, CI workflows, tag movement, application
code, device code, or live-write behavior.

## Approved Corpus RAG And Model Change Policy

Status: PLANNING PRESENT.

`docs/APPROVED_CORPUS_RAG_PLAN.md` defines candidate repository documents for a
future local approved corpus, required metadata, forbidden corpus material, and
the approval checkpoint required before expansion or indexing.

`docs/MODEL_CHANGE_POLICY.md` defines planning-level controls for `model_id`,
`prompt_template_id`, `eval_run_id`, `approved_corpus_digest`, and
`side_effect_class`, including compare-before-adopt and closeout expectations.

These policies are documentation-only. They do not implement retrieval, build
an index, add dependencies, capture prompts or outputs, compare models, call
external services, install CI, or add application/device/live-write behavior.

## Optional CI Actualization

Status: TEMPLATE-ONLY DECISION PRESENT.

`docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md` records the current decision that
local-first verification remains sufficient for the baseline and that
`scripts/run_release_verify.ps1` covers current release verification needs.

`templates/ci/github-actions-release-verify.yml.template` provides an optional
manual workflow template for downstream forks. It is not installed under
`.github/workflows/`, uses `workflow_dispatch`, uses read-only repository
permissions, requires no secrets, and does not upload artifacts, publish
releases, sign artifacts, create or move tags, deploy, or write to live targets.

Actual workflow installation, required checks, artifact upload, release
publication, signing, tag movement, or deployment requires separate owner
approval.

## Additional Local Target Experiment Planning

Status: PARTIAL EXECUTED.

The `csharp_desktop` and `plc_or_device_tool` profile templates have local
target experiment plans:

- `docs/LOCAL_TARGET_EXPERIMENT_PLAN_csharp_desktop.md`
- `docs/LOCAL_TARGET_EXPERIMENT_PLAN_plc_tool.md`

Each plan requires a separate temporary target, dry-run review first, docs-only
expected output, safety checks, and explicit owner approval before any actual
render write.

The `csharp_desktop` experiment has been executed once under explicit approval
and is recorded in
`docs/LOCAL_TARGET_EXPERIMENT_csharp_desktop_post_v0.1.0.md`. It generated
Markdown documentation only in an outside-repo temporary target. It did not add
C# source, solution, project, XAML, build assets, live configuration, secrets,
private input, or live-write behavior.

The `plc_or_device_tool` actual experiment remains deferred. Its plan defines
the evidence record to create after a future approved execution and how to
record `NOT RUN`, `BLOCKED`, and `ENVIRONMENT BLOCKED` honestly.

## Evidence Baseline Closeout

Status: PRESENT.

`docs/POST_V0.1.0_EVIDENCE_BASELINE_CLOSEOUT.md` records the current
post-v0.1.0 evidence baseline. It summarizes Stage 0-14 work, current evidence
surfaces, release evidence source-basis semantics, verification state, deferred
surfaces, approval boundaries, known limitations, and recommended next steps.

The closeout is documentation-only. It does not add gate coverage, regenerate
artifacts, modify generators, change eval behavior, install CI, create tags,
publish releases, create archives, run target renders, or add application,
device, or live-write behavior.

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
- Do not expand, sign, publish, externally enrich, or regenerate
  SBOM/provenance evidence outside an explicit release evidence task.
- Do not create retrieval indexes, embeddings, vector stores, or RAG tooling
  without separate approval.
- Do not capture prompts, model outputs, private input, or tool-call bodies.
- Do not adopt model or prompt changes without eval and closeout evidence once
  an applicable eval harness exists.
- Do not install GitHub Actions workflows.
- Do not upload release evidence artifacts from CI without separate approval.
- Do not make CI checks required without separate approval.
- Do not publish, sign, tag, deploy, or write to live targets from optional CI.
- Do not add a new profile.
- Do not add `profiles/scenario_simulator`.
- Do not add `examples/scenario_simulator_minimal`.
- Do not add optional design-stage render, gate, or example integration without separate approval.
- Do not add application, C#, PLC/device, or live-write code.

## Next Review

Review downstream adoption feedback, the lightweight governance docs, and the
standalone eval harness before deciding whether quality-gate integration,
release page publication, local packaging, release bundle generation, audit log
generation, SBOM/provenance expansion or publication, CI, or any optional
design-stage integration adds enough value to justify a follow-up task. Keep
approved-corpus RAG implementation and model comparison tooling deferred until
a separate owner approval names exact files, artifacts, dependencies,
verification, and safety boundaries. Keep optional CI workflow installation and
CI artifact upload deferred until a separate owner approval names the workflow
path, trigger policy, permissions, artifact retention, and
publication/signing/tag exclusions.
