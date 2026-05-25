# STATUS.md

## Current Phase

Post v0.1.0 approved corpus and model change policy planning.

## Current State

The repository contains documentation, base templates, profile templates, render tooling, quality gates, tests, and minimal example skeletons.

## What Exists

- Core repo contract documents.
- Safety and verification policy documents.
- Release readiness documents:
  - `docs/ARCHITECTURE.md`
  - `docs/VALIDATION_SCOPE.md`
  - `docs/TEMPLATE_EXTENSION_POLICY.md`
  - `docs/DOMAIN_ADAPTATION_GUIDE.md`
  - `docs/adr/ADR-0001-local-first.md`
  - `docs/adr/ADR-0002-base-template-over-domain-profile.md`
  - `docs/adr/ADR-0003-approval-gated-side-effect.md`
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/KNOWN_LIMITATIONS.md`
  - `docs/CI_POLICY.md`
  - `docs/LOCAL_USAGE.md`
  - `docs/LOCAL_RELEASE_PACKAGE.md`
  - `docs/LOCAL_DOWNSTREAM_ADOPTION_PLAN.md`
  - `docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md`
  - `docs/DOWNSTREAM_DOC_REVIEW_CHECKLIST_v0.1.0.md`
  - `docs/DOWNSTREAM_FEEDBACK_v0.1.0_P2_DESIGN.md`
  - `docs/OPTIONAL_DESIGN_STAGE_PACK_PLAN.md`
  - `docs/OPTIONAL_DESIGN_STAGE_PACK_DECISION.md`
  - `docs/OPTIONAL_DESIGN_STAGE_PACK_USAGE.md`
  - `docs/OPTIONAL_DESIGN_STAGE_PACK_REVIEW.md`
  - `docs/OPTIONAL_DESIGN_STAGE_PACK_MANUAL_FEEDBACK_001.md`
  - `docs/OPTIONAL_DESIGN_STAGE_PACK_MANUAL_FEEDBACK_002.md`
  - `docs/OPTIONAL_DESIGN_STAGE_PACK_INTEGRATION_DECISION.md`
  - `docs/PROMPT_PATTERNS.md`
  - `docs/BUG_REVIEW_TEMPLATE.md`
  - `docs/SIMPLIFICATION_CHECKLIST.md`
  - `docs/POST_V0.1.0_ROADMAP.md`
  - `docs/RELEASE_PAGE_DECISION.md`
  - `docs/LOCAL_PACKAGE_CHECKLIST.md`
  - `docs/RELEASE_BUNDLE_POLICY.md`
  - `docs/RELEASE_MANIFEST_POLICY.md`
  - `docs/SBOM_PROVENANCE_PLAN.md`
  - `docs/PYTHON_RUNTIME_POLICY.md`
  - `docs/APPROVED_CORPUS_RAG_PLAN.md`
  - `docs/MODEL_CHANGE_POLICY.md`
  - `docs/OPTIONAL_EVAL_HARNESS_PLAN.md`
  - `docs/MINIMAL_EVAL_HARNESS_DESIGN.md`
  - `docs/CHANGE_CONTROL.md`
  - `docs/HUMAN_APPROVALS.md`
  - `docs/EVAL_POLICY.md`
  - `docs/AUDIT_LOG_POLICY.md`
  - `docs/P6_RELEASE_CLOSEOUT.md`
  - `docs/GITHUB_RELEASE_DRAFT_v0.1.0-rc2.md`
  - `docs/GITHUB_RELEASE_DRAFT_v0.1.0.md`
  - `docs/FORMAL_V0.1.0_CRITERIA.md`
  - `docs/RELEASE_NOTES_v0.1.0-rc1.md`
  - `docs/RELEASE_NOTES_v0.1.0-rc2.md`
  - `docs/RELEASE_RECORD_v0.1.0-rc1.md`
  - `docs/RELEASE_RECORD_v0.1.0-rc2.md`
  - `docs/RELEASE_RECORD_v0.1.0.md`
  - `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md`
  - `docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md`
  - `docs/CLEAN_CLONE_VALIDATION_v0.1.0.md`
  - `docs/LOCAL_TARGET_EXPERIMENT_python_cli_v0.1.0-rc1.md`
  - `docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md`
  - `docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md`
  - `docs/RC2_CANDIDATE_CLOSEOUT.md`
  - `docs/OPTIONAL_GITHUB_ACTIONS.md`
- Base markdown templates, including source index, project boundary, data scope, phase plan, and approvals templates.
- Experimental optional design-stage Markdown template pack under `templates/optional/design_stage/`.
- Profile templates for `python_cli`, `csharp_desktop`, and `plc_or_device_tool`.
- `scripts/render_template.py`.
- `scripts/quality_gate.py`.
- `scripts/run_eval.py`.
- `scripts/generate_manifest.py`.
- `scripts/generate_checksums.py`.
- `scripts/generate_sbom.py`.
- `scripts/generate_provenance.py`.
- `scripts/run_release_verify.ps1`.
- Python runtime/dependency reproducibility files:
  - `.python-version`
  - `requirements-dev.txt`
  - `requirements-dev.lock`
- Gate modules under `scripts/gates/`.
- Standalone eval gate wrapper: `scripts/gates/eval_gate.py`.
- Minimal local eval cases under `evals/cases/`.
- Eval golden path list under `evals/golden/`.
- Generated local release evidence under `artifacts/`:
  - `artifacts/release-manifest.json`
  - `artifacts/checksums.sha256`
  - `artifacts/sbom.spdx.json`
  - `artifacts/sbom.cdx.json`
  - `artifacts/provenance.intoto.jsonl`
- Example skeletons:
  - `examples/python_cli_minimal`
  - `examples/csharp_desktop_minimal`
  - `examples/plc_tool_minimal`
- Tests under `tests/`.
- Local verification wrapper: `scripts/run_local_verify.ps1`.
- Optional GitHub Actions template: `templates/ci/github-actions-local-verify.yml.template`.
- Reusable prompt contract templates under `prompts/task_contract/`.
- Minimal local-only eval harness design and implementation: `docs/MINIMAL_EVAL_HARNESS_DESIGN.md`, `scripts/run_eval.py`, `scripts/gates/eval_gate.py`, and `evals/cases/`.
- Audit log schema for future optional evidence: `audits/audit-log.schema.json`.
- Approved-corpus RAG planning: `docs/APPROVED_CORPUS_RAG_PLAN.md`.
- Model and prompt change planning: `docs/MODEL_CHANGE_POLICY.md`.

## What Does Not Exist Yet

- Real application code.
- Real PLC/device code.
- Live target write behavior.
- Real secret/config files.
- CI workflow.
- Release automation.
- Dedicated `scenario_simulator` profile.
- `examples/scenario_simulator_minimal`.
- Optional design-stage pack render integration.
- Optional design-stage pack gate integration.
- Optional design-stage pack example integration.
- Prompt execution automation.
- Eval integration in `scripts/quality_gate.py`.
- Eval CI integration.
- Routine eval report generation.
- Real audit session logs.
- Audit logging automation.
- Audit log validator or `quality_gate.py` integration.
- Retrieval indexes, embeddings, vector stores, or RAG tooling.
- Model comparison code, model observability tooling, prompt capture, or model
  output capture.
- SBOM/provenance external metadata resolution.
- SBOM/provenance signing or publication.
- Optional CI release verification template.

## Known Constraints

- YAML parsing is intentionally scalar-only.
- Examples are skeletons only.
- Runtime checks in examples may be marked NOT RUN when code or scripts do not exist.
- Render targets inside this repository are limited to `examples/<name>`.
- `requirements-dev.lock` pins exact development verification package versions
  but does not include wheel hashes.
- The current release manifest generator was not updated in this task to
  inventory `.python-version` or `requirements-dev.lock`.

## Latest Verification

Verified release tag target commit: `43bbf001e1d2770466b41d5b8366f289b972a00b`

Latest tag name: `v0.1.0`

Latest tag target commit: `43bbf001e1d2770466b41d5b8366f289b972a00b`

Latest tag object: `a5aed964f381fecdeff54d6c94a068ae21d1dcf9`

Previous tags:

- `v0.1.0-rc1`, object `9ca08efbd43cd2c5defba7875efbd7ca702c6166`, target `10bccadd15be9401847620eba61d3c8c4117962d`
- `v0.1.0-rc2`, object `569b992b390a672cd8a321963a963ff0cbe47976`, target `67ead73628c8ff7b15e91d2ba608efbdbb8de81e`

Stage 0 current-main gap review basis:

- Ref: `origin/main`
- Commit: `7add760e89b84106679461948e9db58223900e33`
- Fetched/checked timestamp: `2026-05-24T15:45:55.4078343+09:00`

| check | status | evidence |
|---|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1` | PASS | pytest 21 passed with `tests` as the explicit collection target, quality gate passed, and 3 render dry-runs passed |
| `python -m pytest` | PASS | 21 passed through the local Python runtime used by the verification wrapper |
| `python scripts/quality_gate.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed in this Codex desktop shell |
| local Python runtime `scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed; docs gate now requires 64 documents including Stage 1 policy docs |
| python_cli render dry-run | PASS | `examples/python_cli_minimal` dry-run succeeded |
| csharp_desktop render dry-run | PASS | `examples/csharp_desktop_minimal` dry-run succeeded |
| plc_tool render dry-run | PASS | `examples/plc_tool_minimal` dry-run succeeded |
| CI workflow | NOT RUN | Not included in this repository baseline |
| rc1 release tag | CREATED | `v0.1.0-rc1` points to `10bccadd15be9401847620eba61d3c8c4117962d` |
| rc2 release tag | CREATED | `v0.1.0-rc2` points to `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| formal v0.1.0 tag | CREATED | `v0.1.0` points to `43bbf001e1d2770466b41d5b8366f289b972a00b` |
| formal v0.1.0 clean clone validation | PASS | `docs/CLEAN_CLONE_VALIDATION_v0.1.0.md` |
| release notes | PRESENT | `docs/RELEASE_NOTES_v0.1.0-rc1.md` exists |
| rc2 release notes | PRESENT | `docs/RELEASE_NOTES_v0.1.0-rc2.md` exists |
| rc2 candidate closeout | PRESENT | `docs/RC2_CANDIDATE_CLOSEOUT.md` exists |
| rc1 release record | PRESENT | `docs/RELEASE_RECORD_v0.1.0-rc1.md` exists |
| rc2 release record | PRESENT | `docs/RELEASE_RECORD_v0.1.0-rc2.md` exists |
| formal v0.1.0 release record | PRESENT | `docs/RELEASE_RECORD_v0.1.0.md` exists |
| GitHub Release Draft | PRESENT | `docs/GITHUB_RELEASE_DRAFT_v0.1.0-rc2.md` exists; GitHub Release page not created |
| formal v0.1.0 GitHub Release Draft | PRESENT | `docs/GITHUB_RELEASE_DRAFT_v0.1.0.md` exists; GitHub Release page not created |
| local downstream adoption plan | PRESENT | `docs/LOCAL_DOWNSTREAM_ADOPTION_PLAN.md` exists; no downstream render executed |
| local downstream adoption run | PASS | `docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md` exists; base template rendered to separate local target |
| downstream doc review checklist | PRESENT | `docs/DOWNSTREAM_DOC_REVIEW_CHECKLIST_v0.1.0.md` exists; downstream docs not filled |
| post-v0.1.0 roadmap | PRESENT | `docs/POST_V0.1.0_ROADMAP.md` exists; planning only |
| release page decision | DEFERRED | `docs/RELEASE_PAGE_DECISION.md` exists; GitHub Release page not created |
| local package checklist | PRESENT | `docs/LOCAL_PACKAGE_CHECKLIST.md` exists; no package archive generated |
| optional eval harness plan | IMPLEMENTED MINIMAL STANDALONE | `docs/OPTIONAL_EVAL_HARNESS_PLAN.md` exists; minimal local-only runner is present |
| minimal local-only eval harness | PRESENT | `docs/MINIMAL_EVAL_HARNESS_DESIGN.md`, `evals/cases/`, `evals/golden/`, `scripts/run_eval.py`, `scripts/gates/eval_gate.py`, and tests exist; no quality-gate or CI integration added |
| known limitations refresh | PRESENT | `docs/KNOWN_LIMITATIONS.md` reflects current post-v0.1.0 limitations |
| architecture release/record plane refresh | PRESENT | `docs/ARCHITECTURE.md` reflects formal v0.1.0 and post-v0.1.0 records |
| architecture optional pack plane refresh | PRESENT | `docs/ARCHITECTURE.md` records optional design-stage pack as manual-use-only, not profile, and not base render |
| downstream P2 design feedback | CAPTURED | `docs/DOWNSTREAM_FEEDBACK_v0.1.0_P2_DESIGN.md` exists; downstream scenario content not copied |
| optional design-stage pack plan | TEMPLATE FILES CREATED | `docs/OPTIONAL_DESIGN_STAGE_PACK_PLAN.md` reflects experimental Markdown-only template files |
| optional design-stage pack decision | APPROVED FOR TEMPLATE FILES ONLY | `docs/OPTIONAL_DESIGN_STAGE_PACK_DECISION.md` records owner decision |
| optional design-stage template files | PRESENT | Seven Markdown-only templates exist under `templates/optional/design_stage/` |
| optional design-stage usage guide | PRESENT | `docs/OPTIONAL_DESIGN_STAGE_PACK_USAGE.md` documents manual use without integration |
| optional design-stage review record | REFRESHED | `docs/OPTIONAL_DESIGN_STAGE_PACK_REVIEW.md` reflects manual feedback 001 and 002 |
| optional design-stage usage refinements | PRESENT | usage guide includes mapping, skip/merge/review-only guidance, and prohibited scan examples |
| optional design-stage manual feedback 001 | PRESENT | refined usage guide was exercised against a downstream target in read-only mode |
| optional design-stage manual feedback 002 | PRESENT | ACCEPTANCE_EVIDENCE_PLAN and OPEN_QUESTIONS received downstream manual-use evidence |
| optional design-stage template review results | PASS | All seven optional templates have PASS manual-use review/evidence |
| optional design-stage integration decision | CLOSED | `docs/OPTIONAL_DESIGN_STAGE_PACK_INTEGRATION_DECISION.md` records KEEP MANUAL-USE-ONLY BASELINE |
| optional design-stage manual-use-only baseline | CLOSED | All seven optional templates have PASS evidence and remain manual-use-only |
| optional design-stage integrations | DEFERRED | Render, gate, and example integration are not implemented |
| lightweight governance docs | PRESENT | Prompt patterns, bug review template, and simplification checklist exist |
| prompt patterns | PRESENT | `docs/PROMPT_PATTERNS.md` documents task contract patterns |
| prompt contract templates | PRESENT | `prompts/task_contract/` contains task contract, critic review, verification closeout, and release summary prompt templates; documentation-only and non-executing |
| bug review template | PRESENT | `docs/BUG_REVIEW_TEMPLATE.md` documents evidence-based bug review |
| simplification checklist | PRESENT | `docs/SIMPLIFICATION_CHECKLIST.md` documents keep/simplify/merge/defer/remove/downstream-only decisions |
| known limitations optional pack refresh | PRESENT | `docs/KNOWN_LIMITATIONS.md` records manual-use-only and missing integration as current limitations |
| post-v0.1.0 roadmap optional pack refresh | PRESENT | `docs/POST_V0.1.0_ROADMAP.md` records closed manual-use-only baseline and deferred integration |
| template extension policy | REFRESHED | downstream feedback promotion and optional-pack placement criteria are documented |
| formal v0.1.0 criteria | SATISFIED | `docs/FORMAL_V0.1.0_CRITERIA.md` exists; formal tag created |
| optional GitHub Actions guide | PRESENT | guide and template exist, but no workflow is installed |
| Stage 0 current-main gap review basis | RECORDED | `origin/main` at `7add760e89b84106679461948e9db58223900e33`, checked `2026-05-24T15:45:55.4078343+09:00` |
| release manifest/checksum generator | PRESENT | `scripts/generate_manifest.py` and `scripts/generate_checksums.py`; local-only, standard-library-only, and restricted to repo-relative `artifacts/` paths |
| release manifest/checksum artifacts | PRESENT | `artifacts/release-manifest.json` and `artifacts/checksums.sha256`; no release archive, tag, release, or workflow generated |
| release evidence foundation | PARTIAL | Release records, clean clone validation, local package checklist, and release drafts exist |
| optional CI local verify template | DONE | `templates/ci/github-actions-local-verify.yml.template` exists and no workflow is installed |
| optional CI release verify template | MISSING / OPTIONAL | No release verification CI template or workflow exists |
| release bundle policy | PRESENT | `docs/RELEASE_BUNDLE_POLICY.md`; records the local manifest/checksum generator boundary and future release evidence exclusions |
| release manifest policy | PRESENT | `docs/RELEASE_MANIFEST_POLICY.md`; defines current manifest fields, deterministic ordering, exclusions, and checksum rules |
| SBOM/provenance plan | IMPLEMENTED MINIMAL LOCAL | `docs/SBOM_PROVENANCE_PLAN.md`; minimal local generators and artifacts exist; no dependencies, external services, CI, tags, signatures, or release publication |
| SBOM/provenance generators | PRESENT | `scripts/generate_sbom.py` and `scripts/generate_provenance.py`; standard-library-only, local-only, restricted to repo-relative `artifacts/` paths, and reject overlapping release-evidence output paths |
| SBOM/provenance artifacts | PRESENT | `artifacts/sbom.spdx.json`, `artifacts/sbom.cdx.json`, and `artifacts/provenance.intoto.jsonl`; no signing, publication, tag movement, release archive, workflow, application code, or live-write behavior |
| release verification wrapper | PRESENT | `scripts/run_release_verify.ps1`; local-only wrapper for local verification, standalone eval, manifest/checksum, SBOM, and provenance generation |
| Python runtime policy | PRESENT | `docs/PYTHON_RUNTIME_POLICY.md` documents the pinned local verification runtime and dependency update rule |
| Python runtime pin | PRESENT | `.python-version` pins Python `3.12.13` for local verification reproducibility |
| development dependency lock | PRESENT | `requirements-dev.txt` pins the direct pytest dependency and `requirements-dev.lock` records exact local verification dependency pins |
| approved-corpus RAG plan | PRESENT | `docs/APPROVED_CORPUS_RAG_PLAN.md`; planning-only approved corpus candidates, metadata, forbidden corpus, and approval checkpoint |
| model change policy | PRESENT | `docs/MODEL_CHANGE_POLICY.md`; planning-only model/prompt tracking, compare-before-adopt, eval/closeout evidence, and side-effect class controls |
| dedicated change control policy | PRESENT | `docs/CHANGE_CONTROL.md` |
| dedicated human approvals policy | PRESENT | `docs/HUMAN_APPROVALS.md` |
| dedicated eval policy | PRESENT | `docs/EVAL_POLICY.md`; minimal standalone eval implementation now exists |
| audit log policy and schema | PRESENT | `docs/AUDIT_LOG_POLICY.md` and `audits/audit-log.schema.json`; no real audit logs or logging automation added |
| Stage 1 policy docs gate coverage | PRESENT | `docs_gate` requires `CHANGE_CONTROL`, `HUMAN_APPROVALS`, `EVAL_POLICY`, and `AUDIT_LOG_POLICY` |
| local staging verification compatibility | PRESENT | `pytest.ini` and `run_local_verify.ps1` scope pytest to `tests`; hygiene and secret-scan gates ignore root `local/` |
| existing governance docs not recreated | CONFIRMED | `PROMPT_PATTERNS`, `BUG_REVIEW_TEMPLATE`, `SIMPLIFICATION_CHECKLIST`, `LOCAL_PACKAGE_CHECKLIST`, and `OPTIONAL_EVAL_HARNESS_PLAN` were preserved |

## Clean Clone Validation

### v0.1.0-rc1

| item | status | evidence |
|---|---|---|
| clean clone | PASS | Separate temporary clone created |
| checkout ref | PASS | `v0.1.0-rc1` checked out in detached HEAD |
| tag target | PASS | `v0.1.0-rc1` resolves to `10bccadd15be9401847620eba61d3c8c4117962d` |
| dependency install command | ENVIRONMENT BLOCKED | Bare `python.exe` launcher is unavailable in this Codex desktop shell |
| local Python runtime dependency check | PASS | `pytest` already satisfied for wrapper runtime |
| local verification wrapper | PASS | pytest, quality gate, and 3 render dry-runs passed |
| `.github/workflows` | ABSENT | No workflow installed |
| application/device/live-write scope | PASS | No real application code, PLC/device code, or live target write support added |

### v0.1.0-rc2

| item | status | evidence |
|---|---|---|
| clean clone | PASS | Separate temporary clone created |
| checkout ref | PASS | `v0.1.0-rc2` checked out in detached HEAD |
| tag target | PASS | `v0.1.0-rc2` resolves to `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| dependency install command | ENVIRONMENT BLOCKED | Bare `python.exe` launcher is unavailable in this Codex desktop shell |
| local Python runtime dependency check | PASS | `pytest` already satisfied for wrapper runtime |
| local verification wrapper | PASS | pytest 17 passed, quality gate passed, and 3 render dry-runs passed |
| example render drift gate | PASS | expected rendered example files present: 48 |
| `.github/workflows` | ABSENT | No workflow installed |
| application/device/live-write scope | PASS | No real application code, C# project files, PLC/device code, or live target write support added |

### v0.1.0

| item | status | evidence |
|---|---|---|
| clean clone | PASS | Separate temporary clone created |
| checkout ref | PASS | `v0.1.0` checked out in detached HEAD |
| tag object | PASS | `a5aed964f381fecdeff54d6c94a068ae21d1dcf9` |
| tag target | PASS | `v0.1.0` resolves to `43bbf001e1d2770466b41d5b8366f289b972a00b` |
| dependency install command | ENVIRONMENT BLOCKED | Bare `python.exe` launcher is blocked in this Codex desktop shell |
| local Python runtime dependency check | PASS | `pytest` already satisfied for wrapper runtime |
| local verification wrapper | PASS | pytest 17 passed, quality gate passed, and 3 render dry-runs passed |
| example render drift gate | PASS | expected rendered example files present: 48 |
| secret scan gate | PASS | no obvious secret/private patterns found |
| `.github/workflows` | ABSENT | No workflow installed |
| application/device/live-write scope | PASS | No real application code, C# project files, PLC/device code, or live target write support added |

## Local Target Experiment

| item | status | evidence |
|---|---|---|
| basis tag | PASS | `v0.1.0-rc1` |
| profile | PASS | `python_cli` |
| target folder | PASS | Separate temporary local target folder |
| pre-render verification | PASS | `scripts/run_local_verify.ps1` passed from tag checkout |
| dry-run render | PASS | 11 Markdown outputs planned |
| actual render | PASS | 11 Markdown docs generated after local target write permission was granted |
| generated runtime code | ABSENT | No application runtime code generated |
| private/secrets/live-write scope | PASS | No private input, secrets, or live target write support generated |

## Base Template Strengthening

| item | status | evidence |
|---|---|---|
| architecture model | PRESENT | `docs/ARCHITECTURE.md` defines control, template, profile, render, verification, side-effect, release, optional CI, and downstream application planes |
| validation scope | PRESENT | `docs/VALIDATION_SCOPE.md` separates regression examples from downstream candidates |
| extension policy | PRESENT | `docs/TEMPLATE_EXTENSION_POLICY.md` states that new profiles are approval-gated and should not be created for every project type |
| domain adaptation | PRESENT | `docs/DOMAIN_ADAPTATION_GUIDE.md` explains downstream use without raw source bulk copy or sensitive values |
| base governance templates | PRESENT | `SOURCE_INDEX`, `PROJECT_BOUNDARY`, `DATA_SCOPE`, `PHASE_PLAN`, and `APPROVALS` templates exist |
| scenario simulator treatment | DOWNSTREAM CANDIDATE | No dedicated profile or example was created |

## Regression Example Synchronization

| item | status | evidence |
|---|---|---|
| extended base docs in examples | PRESENT | Each regression example includes `SOURCE_INDEX`, `PROJECT_BOUNDARY`, `DATA_SCOPE`, `PHASE_PLAN`, and `APPROVALS` |
| example gate coverage | PRESENT | `scripts/gates/example_gate.py` requires the extended base docs |
| render drift check | PRESENT | `scripts/gates/example_render_drift_gate.py` checks expected rendered file presence |
| scenario simulator profile | ABSENT | No dedicated profile or example was created |

## Base Template Local Target Experiment

| item | status | evidence |
|---|---|---|
| basis commit | PASS | `c92f98097905846915719d13ee140f699e441d2f` |
| profile | NONE | Generic/base template target used no profile |
| target folder | PASS | Separate temporary local target folder |
| dry-run render | PASS | 11 base Markdown outputs planned |
| actual render | PASS | 11 base Markdown docs generated after target write permission was granted |
| extended base docs | PASS | `SOURCE_INDEX`, `PROJECT_BOUNDARY`, `DATA_SCOPE`, `PHASE_PLAN`, and `APPROVALS` generated |
| runtime/live-write artifacts | ABSENT | No application code, C# project files, PLC/device code, live write support, or live config generated |
| record | PRESENT | `docs/LOCAL_TARGET_EXPERIMENT_base_template_v0.1.0-rc2-candidate.md` |

## RC2 Candidate

| item | status | evidence |
|---|---|---|
| candidate closeout baseline | PASS | `3f1f192af09e511fc2a22f36e404f4d4e3759509` |
| tag target commit | PASS | `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| release notes | PRESENT | `docs/RELEASE_NOTES_v0.1.0-rc2.md` |
| closeout evidence | PRESENT | `docs/RC2_CANDIDATE_CLOSEOUT.md` |
| local verification | PASS | pytest 17 passed, quality gate passed, render dry-runs passed |
| rc1 tag | RETAINED | `v0.1.0-rc1` still points to `10bccadd15be9401847620eba61d3c8c4117962d` |
| rc2 tag | CREATED | `v0.1.0-rc2` object `569b992b390a672cd8a321963a963ff0cbe47976`, target `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| rc2 release record | PRESENT | `docs/RELEASE_RECORD_v0.1.0-rc2.md` |
| formal v0.1.0 | CREATED | `v0.1.0` object `a5aed964f381fecdeff54d6c94a068ae21d1dcf9`, target `43bbf001e1d2770466b41d5b8366f289b972a00b` |

## GitHub Release Draft

| item | status | evidence |
|---|---|---|
| release draft document | PRESENT | `docs/GITHUB_RELEASE_DRAFT_v0.1.0-rc2.md` |
| target tag | RECORDED | `v0.1.0-rc2` |
| tag target | RECORDED | `67ead73628c8ff7b15e91d2ba608efbdbb8de81e` |
| GitHub Release page | NOT CREATED | Draft document only |

## Local Downstream Adoption Plan

| item | status | evidence |
|---|---|---|
| adoption plan | PRESENT | `docs/LOCAL_DOWNSTREAM_ADOPTION_PLAN.md` |
| basis tag | RECORDED | `v0.1.0` |
| first adoption candidate | RECORDED | Scenario simulator design baseline |
| profile usage | NONE | Base template only |
| downstream render | NOT RUN | Plan only; no target project was generated |
| safety boundary | RECORDED | No raw source bulk copy, sensitive values, runtime code, device code, or live-write support |

## Local Downstream Adoption Run

| item | status | evidence |
|---|---|---|
| adoption run record | PRESENT | `docs/LOCAL_DOWNSTREAM_ADOPTION_RUN_v0.1.0.md` |
| basis tag | PASS | `v0.1.0` |
| source verification | PASS | `run_local_verify.ps1` passed from `v0.1.0` checkout |
| target type | PASS | Scenario simulator design baseline |
| profile | NONE | Base template only |
| dry-run render | PASS | 11 base Markdown outputs planned |
| actual render | PASS | 11 base Markdown docs generated after target write permission was granted |
| force mode | NOT USED | No `--force` render |
| safety scope | PASS | No workflow, profile/example, application code, C# project, PLC/device code, live-write support, private config, or raw sensitive values generated |

## Downstream Doc Review Checklist

| item | status | evidence |
|---|---|---|
| review checklist | PRESENT | `docs/DOWNSTREAM_DOC_REVIEW_CHECKLIST_v0.1.0.md` |
| review target docs | RECORDED | 11 generated downstream docs listed |
| sensitive information rules | RECORDED | Raw source, sensitive values, IP, port, tag, live parameter, and secret prohibitions documented |
| next phase approval | RECORDED | P1 manual fill and P2 simulator design approval gates documented |
| downstream doc content fill | NOT DONE | This repo records the checklist only |

## Post v0.1.0 Operations Plan

| item | status | evidence |
|---|---|---|
| post-v0.1.0 roadmap | PRESENT | `docs/POST_V0.1.0_ROADMAP.md` |
| next priority | DOWNSTREAM FEEDBACK | Roadmap prioritizes downstream adoption feedback before automation |
| release page decision | DEFERRED | `docs/RELEASE_PAGE_DECISION.md`; GitHub Release page not created |
| local package checklist | PRESENT | `docs/LOCAL_PACKAGE_CHECKLIST.md`; no package archive generated |
| optional eval harness | MINIMAL STANDALONE IMPLEMENTED | `docs/OPTIONAL_EVAL_HARNESS_PLAN.md`; `scripts/run_eval.py`, `scripts/gates/eval_gate.py`, `evals/cases/`, and `evals/golden/` exist |
| known limitations | REFRESHED | `docs/KNOWN_LIMITATIONS.md` no longer lists completed CI policy or release tagging guidance as future work |
| architecture release/record plane | REFRESHED | `docs/ARCHITECTURE.md` lists current v0.1.0 and post-v0.1.0 evidence |
| architecture optional pack plane | REFRESHED | Optional design-stage pack is documented as manual-use-only, not profile, and not base render |
| downstream feedback | CAPTURED | `docs/DOWNSTREAM_FEEDBACK_v0.1.0_P2_DESIGN.md` captures template-level P2 design-only feedback |
| optional design-stage pack | TEMPLATE FILES PRESENT | Seven Markdown-only templates created; no render/gate/example integration |
| optional design-stage pack decision | APPROVED FOR TEMPLATE FILES ONLY | `docs/OPTIONAL_DESIGN_STAGE_PACK_DECISION.md`; further integration requires separate approval |
| optional design-stage pack usage | MANUAL ONLY | `docs/OPTIONAL_DESIGN_STAGE_PACK_USAGE.md` documents manual downstream use; render/gate/example integration remains deferred |
| optional design-stage pack review | REFRESHED | `docs/OPTIONAL_DESIGN_STAGE_PACK_REVIEW.md` reflects feedback 001/002 and records all seven templates as PASS |
| optional design-stage guide refinements | PRESENT | mapping table, skip/merge/review-only guidance, and manual scan examples added without integration |
| optional design-stage manual feedback 001 | CAPTURED | `docs/OPTIONAL_DESIGN_STAGE_PACK_MANUAL_FEEDBACK_001.md`; no downstream target modification or integration work |
| optional design-stage manual feedback 002 | CAPTURED | `docs/OPTIONAL_DESIGN_STAGE_PACK_MANUAL_FEEDBACK_002.md`; acceptance evidence and open-question templates validated as manual-use candidates |
| optional design-stage integration decision | CLOSED | `docs/OPTIONAL_DESIGN_STAGE_PACK_INTEGRATION_DECISION.md`; owner decision is KEEP MANUAL-USE-ONLY BASELINE |
| optional design-stage manual-use-only baseline | CLOSED | Render/gate/example integration remains deferred and requires separate owner approval |
| optional design-stage operating docs | REFRESHED | Architecture, known limitations, and roadmap reflect the closed manual-use-only baseline |
| lightweight governance docs | ADDED | `PROMPT_PATTERNS`, `BUG_REVIEW_TEMPLATE`, and `SIMPLIFICATION_CHECKLIST` are present; no implementation added |
| prompt contract templates | ADDED | Four reusable Markdown prompt templates exist under `prompts/task_contract/`; they do not execute prompts or grant approval |
| minimal eval harness | IMPLEMENTED | Standalone non-LLM local eval runner, cases, golden path list, gate wrapper, and tests added |
| release bundle policy | PRESENT | `docs/RELEASE_BUNDLE_POLICY.md`; records local manifest/checksum generation boundary and future release evidence components |
| release manifest/checksum generation | IMPLEMENTED | Local-only manifest and checksum scripts, path-boundary tests, and artifacts added; outputs and checksum inputs are restricted to repo-relative `artifacts/` paths; no SBOM/provenance, archive, CI, tag, release, application, or live-write behavior |
| SBOM/provenance generation | IMPLEMENTED MINIMAL LOCAL | Standard-library-only SPDX, CycloneDX, and in-toto-style provenance generators and artifacts added; output paths reject release-evidence overlap; no external metadata lookup, signing, archive, CI, tag, release publication, application, or live-write behavior |
| release verification wrapper | IMPLEMENTED LOCAL | `scripts/run_release_verify.ps1` runs local verification, optional standalone eval, manifest/checksum generation, optional SBOM/provenance generation, final checksum regeneration, and artifact path reporting; no archive, CI, signing, publication, tag movement, application, or live-write behavior |
| approved-corpus RAG planning | ADDED | `docs/APPROVED_CORPUS_RAG_PLAN.md` defines candidate safe corpus files, required metadata, forbidden corpus, and corpus-expansion approval checkpoints; no retrieval/index tooling added |
| model and prompt change planning | ADDED | `docs/MODEL_CHANGE_POLICY.md` defines model, prompt template, eval run, corpus digest, side-effect class, and compare-before-adopt controls; no model comparison or capture tooling added |
| Stage 1 change control policy | PRESENT | `docs/CHANGE_CONTROL.md`; documentation-only |
| Stage 1 human approvals policy | PRESENT | `docs/HUMAN_APPROVALS.md`; documentation-only |
| Stage 1 eval policy | PRESENT | `docs/EVAL_POLICY.md`; minimal standalone eval exists; no dependencies, quality-gate integration, or CI integration |
| audit log schema | PRESENT | `audits/audit-log.schema.json`; optional future evidence contract only, no real session logs or automation |
| Stage 1 docs gate alignment | PRESENT | `docs_gate` includes the four Stage 1 policy docs as required documentation |
| local staging verification compatibility | PRESENT | `pytest.ini` and `scripts/run_local_verify.ps1` scope pytest to `tests`; hygiene and secret-scan gates ignore root `local/` |
| Stage 4 implementation boundary | PRESERVED | Minimal standalone eval code, cases, golden path list, gate wrapper, and tests added; optional report paths are repo-internal relative only; no eval report generated by default, quality-gate integration, CI, manifest/checksum artifacts, SBOM/provenance artifacts, workflows, tags, releases, profiles, application code, C# source/project, PLC/device code, or live-write behavior added |
| scenario simulator treatment | DOWNSTREAM CANDIDATE | Remains downstream candidate, not a built-in profile |

## Formal v0.1.0 GitHub Release Draft

| item | status | evidence |
|---|---|---|
| release draft document | PRESENT | `docs/GITHUB_RELEASE_DRAFT_v0.1.0.md` |
| target tag | RECORDED | `v0.1.0` |
| tag object | RECORDED | `a5aed964f381fecdeff54d6c94a068ae21d1dcf9` |
| tag target | RECORDED | `43bbf001e1d2770466b41d5b8366f289b972a00b` |
| GitHub Release page | NOT CREATED | Draft document only |

## Formal v0.1.0 Tag

| item | status | evidence |
|---|---|---|
| tag | CREATED | `v0.1.0` |
| tag object | RECORDED | `a5aed964f381fecdeff54d6c94a068ae21d1dcf9` |
| tag target commit | RECORDED | `43bbf001e1d2770466b41d5b8366f289b972a00b` |
| release record | PRESENT | `docs/RELEASE_RECORD_v0.1.0.md` |
| clean clone validation | PASS | `docs/CLEAN_CLONE_VALIDATION_v0.1.0.md` |
| GitHub Release page | NOT CREATED | Publication remains a separate decision |
| GitHub Actions workflow | NOT INSTALLED | Local-first baseline remains unchanged |

## Formal v0.1.0 Criteria

| item | status | evidence |
|---|---|---|
| criteria document | PRESENT | `docs/FORMAL_V0.1.0_CRITERIA.md` |
| clean clone validation requirement | PASS | `v0.1.0-rc2` clean clone validation passed |
| downstream experiment requirement | PASS | `docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md` |
| formal v0.1.0 tag | CREATED | `docs/RELEASE_RECORD_v0.1.0.md` |

## Downstream Application Experiment

| item | status | evidence |
|---|---|---|
| downstream candidate | PASS | Scenario simulator design candidate tested as downstream target |
| profile | NONE | No profile used or created |
| target folder | PASS | Separate temporary local downstream target |
| dry-run render | PASS | 11 base Markdown outputs planned |
| actual render | PASS | 11 base Markdown docs generated after target write permission was granted |
| required docs | PASS | `SOURCE_INDEX`, `PROJECT_BOUNDARY`, `DATA_SCOPE`, `PHASE_PLAN`, `APPROVALS`, `AGENTS`, `PRODUCT`, `MVP`, `STATUS`, `ACCEPTANCE_TRACE`, and `README` generated |
| safety scope | PASS | No workflow, profile/example, runtime code, C# project files, device code, live-write support, private data, or live config generated |
| record | PRESENT | `docs/DOWNSTREAM_EXPERIMENT_scenario_simulator_design_base_template.md` |

## Next Recommended Step

Keep approved-corpus RAG implementation, retrieval/index generation, embeddings,
model comparison tooling, prompt/model output capture, eval integration into
`scripts/quality_gate.py`, CI integration, routine eval report generation, real
audit session log generation, audit logging automation, broader release bundle
or archive generation, SBOM/provenance expansion or publication, workflows,
profiles, and application/device/live-write behavior deferred unless separately
approved.
