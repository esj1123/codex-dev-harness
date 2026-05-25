# Post v0.1.0 Evidence Baseline Closeout

## Purpose

This document closes the post-v0.1.0 evidence and governance baseline for
`esj1123/codex-dev-harness`.

It records what exists, what remains deferred, and what requires future owner
approval. This is a durable closeout record for the staged post-v0.1.0 work. It
does not implement new behavior.

## Baseline Status

| item | status | evidence |
|---|---|---|
| repository | PRESENT | `esj1123/codex-dev-harness` |
| branch/ref at closeout drafting | PRESENT | `main` / `origin/main` |
| repository commit at closeout drafting | PRESENT | `03161f7d26ef70b5bdc4db90026d49479926cf97` |
| closeout scope | DOCUMENTATION ONLY | This document, `STATUS.md`, and `ACCEPTANCE_TRACE.md` record closeout state |
| artifacts regenerated in this task | NO | `scripts/run_release_verify.ps1` was not run |
| generator behavior changed | NO | Generator code was not edited |
| eval behavior changed | NO | Eval code and tests were not edited |
| docs_gate coverage changed | NO | The closeout document is not added to `docs_gate` in this task |

The closeout document itself is created after the commit above. The final
artifact-containing commit for this closeout will be known only after the
closeout changes are committed.

## Completed Stage Summary

| Stage | Area | Outcome | Main evidence files | Implementation status | Deferred surfaces |
|---|---|---|---|---|---|
| 0 | Current-main gap review | Gap map and baseline review recorded | `STATUS.md`, `ACCEPTANCE_TRACE.md` | Documentation review complete | None for review; follow-up stages handled gaps |
| 1 | Governance policy closure | Dedicated change control, human approvals, eval, and audit policy surfaces present | `docs/CHANGE_CONTROL.md`, `docs/HUMAN_APPROVALS.md`, `docs/EVAL_POLICY.md`, `docs/AUDIT_LOG_POLICY.md` | Documentation implemented | Automation, logging, and enforcement beyond docs |
| 2 | Prompt contract templates | Reusable AI/Codex task contract templates present | `prompts/task_contract/`, `docs/PROMPT_PATTERNS.md` | Markdown templates implemented | Prompt execution automation |
| 3 | Minimal eval design | Local-only non-LLM eval harness design documented | `docs/MINIMAL_EVAL_HARNESS_DESIGN.md`, `docs/OPTIONAL_EVAL_HARNESS_PLAN.md` | Design complete | CI and release-blocking eval adoption |
| 4 | Minimal eval implementation | Standalone non-LLM eval runner, cases, golden paths, wrapper, and tests present | `scripts/run_eval.py`, `scripts/gates/eval_gate.py`, `evals/cases/`, `evals/golden/`, `tests/test_run_eval.py`, `tests/test_eval_gate.py` | Implemented standalone | `quality_gate.py` integration, routine reports, CI |
| 5 | Audit schema and policy | Optional future audit schema and policy present | `audits/audit-log.schema.json`, `docs/AUDIT_LOG_POLICY.md` | Schema/policy only | Real audit logs, validators, automatic capture |
| 6 | Release bundle and manifest policy | Machine-readable release evidence policy present | `docs/RELEASE_BUNDLE_POLICY.md`, `docs/RELEASE_MANIFEST_POLICY.md` | Policy implemented | Broader bundle/archive publication |
| 7 | Manifest/checksum generation | Local manifest and checksum generators and artifacts present with path-boundary cleanup | `scripts/generate_manifest.py`, `scripts/generate_checksums.py`, `artifacts/release-manifest.json`, `artifacts/checksums.sha256` | Implemented local-only | Release archives, publication, tags, signing |
| 8 | SBOM/provenance planning | Minimal local SBOM/provenance plan present | `docs/SBOM_PROVENANCE_PLAN.md` | Planning complete | External metadata, signing, publication |
| 9 | SBOM/provenance generation | Minimal local SPDX, CycloneDX, and provenance generators and artifacts present with overlap guards | `scripts/generate_sbom.py`, `scripts/generate_provenance.py`, `artifacts/sbom.spdx.json`, `artifacts/sbom.cdx.json`, `artifacts/provenance.intoto.jsonl` | Implemented local-only | Certification workflows, cloud attestation, external lookup |
| 10 | Release verification wrapper | Local wrapper runs verification and local evidence generation when explicitly executed | `scripts/run_release_verify.ps1`, `docs/VERIFICATION.md` | Implemented local-only | Archive, publish, upload, sign, tag, CI installation |
| 11 | Runtime reproducibility | Python runtime pin and dependency files present | `.python-version`, `requirements-dev.txt`, `requirements-dev.lock`, `docs/PYTHON_RUNTIME_POLICY.md` | Implemented docs/files | Wheel-hash lock and alternate package managers |
| 12 | RAG/model policy planning | Approved-corpus RAG and model/prompt change policies present | `docs/APPROVED_CORPUS_RAG_PLAN.md`, `docs/MODEL_CHANGE_POLICY.md` | Planning-only | Retrieval/index tooling, embeddings, model comparison |
| 13 | Optional CI and docs gate alignment | Optional release verification CI template exists; docs gate covers current required governance/release docs | `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`, `templates/ci/github-actions-release-verify.yml.template`, `scripts/gates/docs_gate.py` | Template-only CI; docs gate aligned | Active workflows, required checks, artifact upload |
| 14 | Local target experiment planning | Future `csharp_desktop` and `plc_or_device_tool` experiment plans present | `docs/LOCAL_TARGET_EXPERIMENT_PLAN_csharp_desktop.md`, `docs/LOCAL_TARGET_EXPERIMENT_PLAN_plc_tool.md` | Planning-only | Actual target render/write and downstream target folders |

Additional alignment work completed during the staged baseline:

- Release manifest inventory now includes `.python-version`,
  `requirements-dev.txt`, and `requirements-dev.lock` when present.
- Release evidence source-basis semantics are documented in
  `docs/RELEASE_MANIFEST_POLICY.md`, `docs/RELEASE_BUNDLE_POLICY.md`, and
  `docs/VERIFICATION.md`.
- The closeout document is not made a required `docs_gate` document in this
  task. That can be done later in an explicit gate-alignment task.

## Current Evidence Surfaces

| surface | status | evidence |
|---|---|---|
| Governance docs | IMPLEMENTED | Root docs, ADRs, `docs/CHANGE_CONTROL.md`, `docs/HUMAN_APPROVALS.md`, `docs/EVAL_POLICY.md`, `docs/AUDIT_LOG_POLICY.md` |
| Prompt templates | IMPLEMENTED / NON-EXECUTING | `prompts/task_contract/` |
| Eval harness | IMPLEMENTED STANDALONE | `scripts/run_eval.py`, `evals/cases/`, `evals/golden/` |
| Eval gate | OPTIONAL / STANDALONE | `scripts/gates/eval_gate.py`; not wired into `scripts/quality_gate.py` |
| Audit schema/policy | PLANNING / OPTIONAL FUTURE EVIDENCE | `audits/audit-log.schema.json`, `docs/AUDIT_LOG_POLICY.md`; no real logs |
| Manifest/checksum artifacts | GENERATED LOCAL EVIDENCE | `artifacts/release-manifest.json`, `artifacts/checksums.sha256` |
| SBOM/provenance artifacts | GENERATED LOCAL EVIDENCE | `artifacts/sbom.spdx.json`, `artifacts/sbom.cdx.json`, `artifacts/provenance.intoto.jsonl` |
| Release verification wrapper | IMPLEMENTED LOCAL-ONLY | `scripts/run_release_verify.ps1` |
| Runtime pin/lock | IMPLEMENTED | `.python-version`, `requirements-dev.txt`, `requirements-dev.lock` |
| RAG/model planning | PLANNING-ONLY | `docs/APPROVED_CORPUS_RAG_PLAN.md`, `docs/MODEL_CHANGE_POLICY.md` |
| Optional CI templates | OPTIONAL / NOT INSTALLED | `templates/ci/github-actions-local-verify.yml.template`, `templates/ci/github-actions-release-verify.yml.template`; `.github/workflows/` absent |
| Local target experiment plans | PLANNING-ONLY | `docs/LOCAL_TARGET_EXPERIMENT_PLAN_csharp_desktop.md`, `docs/LOCAL_TARGET_EXPERIMENT_PLAN_plc_tool.md` |
| Closeout gate coverage | NOT ACTIVE | This closeout document is not added to `docs_gate` in this task |

## Release Evidence Semantics

`artifacts/release-manifest.json` records `git_commit` as the source basis
commit at generation time. It identifies the repository content inspected by
the local evidence generation process.

When generated artifacts are committed, the artifact-containing commit may be
newer than the manifest `git_commit`. That difference is expected for committed
generated evidence. It is not an error by itself.

Formal release closeout should cite both:

- source basis commit from `artifacts/release-manifest.json`
- artifact-containing commit or tag used for the final record

This closeout does not change manifest schema or generator behavior. A future
schema may split the current `git_commit` meaning into `source_basis_commit`
and `artifact_commit`, but that is a future schema evolution and is not
implemented here.

## Current Verification Snapshot

This snapshot uses known values from the repository state and `STATUS.md`.
No release evidence artifacts were regenerated for this closeout.

| item | status | evidence |
|---|---|---|
| basis branch/ref | PRESENT | `main` / `origin/main` |
| current repository commit at closeout drafting | PRESENT | `03161f7d26ef70b5bdc4db90026d49479926cf97` |
| manifest source basis commit | PRESENT | `artifacts/release-manifest.json` records `1b2e430f2a5df4dff9cc6e5a4008095e732a5a55` |
| manifest generated timestamp | PRESENT | `2026-05-25T05:34:23Z` |
| Python runtime used for verification | PRESENT | bundled Codex Python `3.12.13` |
| bare `python.exe` | ENVIRONMENT BLOCKED | Existing Windows logon session error in this Codex desktop shell |
| bundled Python `python -m pytest` | PASS | 61 passed in this closeout verification |
| bundled Python `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed in this closeout verification |
| `scripts/run_local_verify.ps1` | NOT RUN | Optional for this documentation-only closeout |
| `scripts/run_release_verify.ps1` | NOT RUN | Not run because it regenerates artifacts |
| CI workflow | NOT INSTALLED | `.github/workflows/` remains absent |
| release publication | NOT DONE | No GitHub Release publication in this task |
| tag movement/signing | NOT DONE | No tag created, moved, or signed in this task |
| release archive | NOT DONE | No archive created in this task |

## Deferred / Not Implemented Surfaces

The following remain deferred or not implemented:

- Active `.github/workflows/` installation.
- CI artifact upload.
- Required CI checks.
- GitHub Release publication.
- Tag creation, movement, or signing.
- Release archive creation.
- `eval_gate.py` integration into `scripts/quality_gate.py`.
- Routine eval report generation.
- Real audit log generation.
- Audit validator or quality-gate integration.
- RAG index, embeddings, vector DB, or retrieval tooling.
- Model comparison tooling.
- Prompt capture, model output capture, or model observability tooling.
- Optional design-stage pack render, gate, or example integration.
- `scenario_simulator` profile or example.
- Actual `csharp_desktop` or `plc_or_device_tool` target experiment execution.
- Downstream target folder creation for Stage 14 plans.
- Application code, C# source/project/XAML/build assets, PLC/device code, live
  configuration, or live-write behavior.

## Approval Boundaries

Separate explicit owner approval is required before:

- Actual target render write.
- New profile or example creation.
- CI workflow installation.
- CI artifact upload.
- Release archive creation.
- GitHub Release publication.
- Tag creation, movement, or signing.
- RAG index creation, corpus expansion, embeddings, vector DB, or retrieval
  tooling.
- Model or prompt adoption that changes governed behavior.
- Real audit log generation.
- Eval integration into `scripts/quality_gate.py`.
- Routine eval report generation.
- SBOM/provenance external metadata lookup, signing, publication, or expanded
  certification workflow.
- Application/device/live-write behavior.

Planning documents, prompt templates, policies, manifests, SBOMs, provenance,
and this closeout do not grant approval by themselves.

## Known Limitations

- Release artifacts may record a source basis commit earlier than the later
  artifact-containing commit.
- `requirements-dev.lock` pins exact package versions but does not include
  wheel hashes.
- SBOM and provenance are minimal local-first evidence, not full certification,
  cloud attestation, signing, or publication workflows.
- The eval harness is minimal and standalone.
- The optional CI templates are inert unless manually installed after approval.
- Stage 14 target experiments are planning-only and do not prove actual
  separate target render behavior.
- This closeout document is not currently required by `docs_gate`.

## Recommended Next Steps

1. Commit this closeout document with the related `STATUS.md` and
   `ACCEPTANCE_TRACE.md` updates.
2. Optionally add this closeout document to `docs_gate` in a separate or
   explicitly approved gate-alignment step.
3. Decide whether formal release evidence should be regenerated after the final
   commit.
4. If formal baseline evidence is desired, run `scripts/run_release_verify.ps1`
   in a separate artifact-regeneration task.
5. Otherwise, stop here and treat the repository as a post-v0.1.0 evidence
   baseline.
