# Post v0.1.0 Roadmap

## Purpose

Record the post-v0.1.0 operating direction for codex-dev-harness without starting new implementation work.

This document is now historical operating context for the completed
post-v0.1.0 and Stage 5B baseline. Current capability implementation
sequencing is defined by `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`.

This document is planning-only. It does not create an active CI workflow,
release publication path, eval harness expansion, SBOM/provenance expansion,
RAG index, model comparison tool, new profile, example project, or application
code.

## Current Baseline

Current baseline: `v0.1.0`.

The formal v0.1.0 baseline is a local-first governed template for downstream project adoption. It includes base templates, selected profile templates, render tooling, quality gates, regression examples, local verification, release records, clean clone validation, and downstream adoption documentation.

## Next Priority

Next priority: follow `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`.

The first implementation target after the capability roadmap is read-only CI +
verification hygiene. The following targets are audit / trace / receipt schema,
eval/report integration, approved corpus digest, local RAG, MCP tool boundary,
Hermes sidecar, and later release automation / provenance plus downstream
product integration.

The earlier Stage 5B direction to keep `codex-dev-harness` frozen remains
historical risk evidence for avoiding broad or immediate automation. It is not
a permanent blocker to the roadmap targets.

The most useful post-v0.1.0 signal is how the base template behaves when applied to real downstream planning targets. Feedback should focus on documentation clarity, safety boundaries, approval gates, source indexing, and render ergonomics before adding new automation.

Stages 1-5A after the evidence baseline are complete:

- Stage 1 documentation drift cleanup.
- Stage 2 local post-v0.1.0 evidence baseline.
- Stage 3 eval integration decision: historical standalone runtime baseline.
- Stage 4 optional CI decision: historical template-only risk evidence.
- Stage 5A downstream transition decision.

The Stage 5A direction decision kept `codex-dev-harness` stable as the
local-first governed template baseline. Stage 5B superseded that default
next step by selecting `stock` as the first practical probe candidate, and the
Probe #1-#5 sequence is closed out in
`docs/STAGE_5B_STOCK_PRACTICAL_PROBE_CLOSEOUT.md`. Scenario-Simulator remains
deferred as an architecture/planning candidate. The `plc_or_device_tool` actual
target experiment remains deferred and is not the next default stage.

The Stage 5B follow-up Code Simplicity decision is complete. The decision added
a minimal documentation-only Code Simplicity Addendum in
`docs/SIMPLIFICATION_CHECKLIST.md` and a short Coding Simplicity Clause in
`docs/PROMPT_PATTERNS.md`.

The next default is not another `stock` probe and not stock Probe #6. The
current harness implementation sequence is now the capability roadmap. Each
implementation phase still requires a separate owner-approved task with exact
files, artifacts, dependencies, verification, and safety boundaries.

The optional design-stage pack is now a closed manual-use-only baseline. Its templates can be copied, merged, skipped, or used for review-only downstream work, but they are not part of the base render path.

The first lightweight governance docs are present:

- `docs/PROMPT_PATTERNS.md`
- `docs/BUG_REVIEW_TEMPLATE.md`
- `docs/SIMPLIFICATION_CHECKLIST.md`

The minimal local-only eval harness is present:

- `docs/MINIMAL_EVAL_HARNESS_DESIGN.md`
- `docs/EVAL_INTEGRATION_DECISION.md`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- `evals/cases/`
- `evals/golden/`

This is a standalone local implementation. It does not use an LLM judge, call
external services, install CI, generate reports by default, or join
`scripts/quality_gate.py`.

The Stage 3 eval integration decision keeps this standalone baseline. The
release verification wrapper may continue running console-only evals, but
routine report generation, `scripts/quality_gate.py` integration,
release-blocking evals, and CI integration remain unapproved.

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

The Stage 4 decision keeps local-first verification as the baseline and keeps
CI deferred and template-only. The optional local and release verification
templates are not installed under `.github/workflows/`, require no secrets, use
read-only permissions, do not upload artifacts, and do not publish, sign, tag,
deploy, or write to live targets.

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
12. Optional CI actualization decision and template-only local/release
    verification.
13. Additional local target experiment planning for existing profiles.
14. Post-v0.1.0 evidence baseline closeout.
15. Eval integration decision.
16. Optional CI decision refresh.
17. Stage 5A downstream transition decision.
18. Stage 5B target repo selection and practical probe plan.
19. Stage 5B stock practical probe closeout.
20. Capability implementation roadmap.

Each historical item was optional and approval-gated. The capability
implementation roadmap records the owner-intent shift from indefinite deferral
to ordered implementation targets. Planning a future capability still does not
authorize implementing it without a phase decision.

## Current Capability Implementation Sequence

The current sequence is:

1. Source of truth cleanup / repo state confirmation.
2. Capability Implementation Roadmap.
3. Read-only CI + verification hygiene.
4. Audit / trace / receipt schema.
5. Eval/report integration.
6. Approved corpus digest.
7. Local RAG.
8. MCP tool boundary.
9. Hermes sidecar.
10. Release automation / provenance.
11. Downstream product integration.

The first implementation target after the roadmap is read-only CI +
verification hygiene. It must not include secrets, artifact upload, release
publication, signing, tag movement, deployment, downstream edits, RAG/index
tooling, audit automation, eval quality-gate integration, MCP/Hermes
implementation, or live write.

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

`docs/EVAL_INTEGRATION_DECISION.md` records the historical standalone baseline
and current runtime boundary. Per
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, eval / report integration is the
third implementation target after audit / trace / receipt schema. No default
quality-gate integration, CI integration, routine eval report generation, or
release-blocking behavior is active now.

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

Status: HISTORICAL TEMPLATE-ONLY DECISION / FIRST ROADMAP TARGET.

`docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md` records the historical decision
that local-first verification was sufficient for the baseline and that
`scripts/run_release_verify.ps1` covered release verification needs. Under the
capability implementation roadmap, this decision is risk evidence: CI should
start as a read-only local verification mirror, not as artifact upload,
publication, signing, tag movement, deployment, or live write.

`templates/ci/github-actions-release-verify.yml.template` provides an optional
manual workflow template for downstream forks. It is not installed under
`.github/workflows/`, uses `workflow_dispatch`, uses read-only repository
permissions, requires no secrets, and does not upload artifacts, publish
releases, sign artifacts, create or move tags, deploy, or write to live targets.

`templates/ci/github-actions-local-verify.yml.template` provides an optional
manual workflow template for local verification checks. It is also not
installed under `.github/workflows/`.

Actual workflow installation, required checks, artifact upload, release
publication, signing, tag movement, or deployment still requires separate owner
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
record `NOT RUN`, `BLOCKED`, and `ENVIRONMENT BLOCKED` honestly. It is not the
next default stage and should not displace the selected stock probe without a
separate owner decision.

## Stage 5B Target Repo Selection

Status: CLOSED OUT.

`docs/STAGE_5B_TARGET_REPO_SELECTION_AND_PROBE_PLAN.md` records the historical
Stage 5B handoff. It froze `codex-dev-harness` as the local-first governed
baseline, deferred Scenario-Simulator as an architecture/planning candidate,
selected `stock` as the first practical probe candidate, and constrained that
first probe to test-only/dry-run evidence path safety coverage.

`docs/STAGE_5B_STOCK_PRACTICAL_PROBE_CLOSEOUT.md` records the completed
Probe #1-#5 evidence and decision implications. The closeout remains risk
evidence for small phases, verification hygiene, docs-only verification policy,
and temporary-output policy. It is not a permanent blocker to CI, RAG, audit
automation, release automation, eval integration, MCP/Hermes, or downstream
integration when those phases are separately approved.

The plan and closeout are documentation-only. They do not scan or modify
`stock` from this repository, run another target probe, add runtime code,
install CI, generate release artifacts, create RAG/index tooling, add audit
automation, or start Scenario-Simulator implementation.

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

Scenario simulator remains a downstream architecture/planning candidate, not a
built-in profile and not the first practical probe.

The base template surfaces, especially `SOURCE_INDEX`, `PROJECT_BOUNDARY`, `DATA_SCOPE`, `PHASE_PLAN`, and `APPROVALS`, are the intended mechanism for adapting to complex downstream projects without creating a dedicated profile for each domain.

Do not add `profiles/scenario_simulator` or
`examples/scenario_simulator_minimal` by default. The next Scenario-Simulator
work should happen in the Scenario-Simulator repository only after a separate
task selects architecture or planning work under that repository's own rules.

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
- Do not start Probe #6 or run further stock practical probes by default from
  this harness planning task.
- Do not add stock runtime, broker, order, account, scheduler, live market, or
  network behavior.
- Do not start Scenario-Simulator production implementation from this roadmap.
- Do not add application, C#, PLC/device, or live-write code.

## Next Review

Use `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` for the current
implementation handoff. The Stage 5B follow-up Code Simplicity decision remains
valid as a restraint principle, and stock Probe #6 is still not the next
default.

The next recommended task is read-only CI + verification hygiene. Keep
Scenario-Simulator production implementation, quality-gate eval integration,
release page publication, local packaging, release bundle expansion, audit log
generation, SBOM/provenance expansion or publication, optional design-stage
integration, approved-corpus RAG implementation, model comparison tooling,
MCP/Hermes implementation, and downstream product integration out of that task
unless the owner separately approves exact files, artifacts, dependencies,
verification, and safety boundaries.
