# Post v0.1.0 Evidence Baseline Closeout

## Purpose

This document closes the post-v0.1.0 evidence and governance baseline for
`esj1123/codex-dev-harness`.

It records what exists, what remains deferred, and what requires future owner
approval after the Priority 1-4 evidence tightening work. It is a durable
closeout record. It does not install CI, publish a release, move tags, add
application code, create device behavior, or enable live writes.

Current sequencing note: this closeout is historical evidence for the
post-v0.1.0 baseline. It no longer defines the active implementation sequence.
Use `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` for the current owner intent,
dependency order, phase gates, and first implementation target.

## Baseline Status

| item | status | evidence |
|---|---|---|
| repository | PRESENT | `esj1123/codex-dev-harness` |
| branch/ref at final artifact regeneration | PRESENT | `main` / `origin/main` |
| repository commit before Stage 2 evidence regeneration | PRESENT | `9ae69c5fbf65953db2b0efb82b4904098f8a7581` |
| source basis commit | PRESENT | `artifacts/release-manifest.json` records `9ae69c5fbf65953db2b0efb82b4904098f8a7581` |
| artifact-containing commit | PENDING UNTIL STAGE 2 EVIDENCE COMMIT | Regenerated artifacts and closeout updates are modified in the working tree and not yet committed |
| closeout alignment scope | DOCUMENTATION AND LOCAL EVIDENCE | This document, `STATUS.md`, `ACCEPTANCE_TRACE.md`, and local release evidence artifacts record closeout state |
| artifacts regenerated in this task | YES | `scripts/run_release_verify.ps1` passed after explicit eval report generation; generated local evidence only, not release publication |
| generator behavior changed | NO | Generator code was not edited |
| eval behavior changed | NO | Eval code and tests were not edited |
| docs_gate coverage changed | NO | This closeout document is not added to `docs_gate` in this task |

The artifact-containing commit for this Stage 2 refresh is not knowable until
the regenerated artifacts and closeout updates are committed. The previous
Stage 0 read-only review observed artifact-containing commit
`ab77ab0a0b44c2f1bd700820bfeb358c6ec1bbe7`, but the current regenerated
artifact source basis is `9ae69c5fbf65953db2b0efb82b4904098f8a7581`.

## Stage 5A Transition Position

Stages 1-4 after the evidence baseline are complete:

- Stage 1 documentation drift cleanup.
- Stage 2 local post-v0.1.0 evidence baseline.
- Stage 3 eval integration decision: historical standalone runtime baseline.
- Stage 4 optional CI decision: historical template-only risk evidence.

The Stage 5A direction was to keep `codex-dev-harness` stable as the
local-first governed template baseline, perform only small harness refinements
when justified, and transition next to Scenario-Simulator P1 planning in the
downstream repository. That direction is now historical transition evidence.
The current implementation sequence is defined by
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`.

The `plc_or_device_tool` actual target experiment remains deferred and is not
the next default stage. Scenario-Simulator remains a downstream application
candidate, not a built-in harness profile or example.

## Completed Stage Summary

| Stage | Area | Outcome | Main evidence files | Implementation status | Deferred surfaces |
|---|---|---|---|---|---|
| 0 | Current-main gap review | Gap map and baseline review recorded | `STATUS.md`, `ACCEPTANCE_TRACE.md` | Documentation review complete | None for review |
| 1 | Governance policy closure | Change control, human approvals, eval, and audit policy surfaces present | `docs/CHANGE_CONTROL.md`, `docs/HUMAN_APPROVALS.md`, `docs/EVAL_POLICY.md`, `docs/AUDIT_LOG_POLICY.md` | Documentation implemented | Automation, logging, enforcement beyond docs |
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
| 14 | Local target experiment planning and csharp execution | `csharp_desktop` plan executed once under explicit approval; `plc_or_device_tool` remains planned only | `docs/LOCAL_TARGET_EXPERIMENT_PLAN_csharp_desktop.md`, `docs/LOCAL_TARGET_EXPERIMENT_csharp_desktop_post_v0.1.0.md`, `docs/LOCAL_TARGET_EXPERIMENT_PLAN_plc_tool.md` | One docs-only target experiment executed outside repo | `plc_or_device_tool` actual render/write |

Additional Priority 1-4 tightening now reflected in this baseline:

- Priority 1 regenerated local release evidence and aligned closeout records.
- Priority 2 expanded `artifacts/checksums.sha256` to cover the full present
  local release evidence bundle except the checksum file itself.
- Priority 3 expanded the standalone local non-LLM eval harness to 14 named
  cases and generated `artifacts/eval-report.json` explicitly.
- Priority 4 executed the approved `csharp_desktop` local target experiment in
  an outside-repo temporary target and recorded Markdown-only output evidence.

## Current Evidence Surfaces

| surface | status | evidence |
|---|---|---|
| Governance docs | IMPLEMENTED | Root docs, ADRs, `docs/CHANGE_CONTROL.md`, `docs/HUMAN_APPROVALS.md`, `docs/EVAL_POLICY.md`, `docs/AUDIT_LOG_POLICY.md` |
| Prompt templates | IMPLEMENTED / NON-EXECUTING | `prompts/task_contract/` |
| Eval harness | IMPLEMENTED STANDALONE | 14 named `evals/cases/`, `evals/golden/`, `scripts/run_eval.py` |
| Eval report | GENERATED LOCAL EVIDENCE / EXPLICIT | `artifacts/eval-report.json`; not generated by default |
| Eval gate | OPTIONAL / STANDALONE | `scripts/gates/eval_gate.py`; not wired into `scripts/quality_gate.py` |
| Audit schema/policy | PLANNING / OPTIONAL FUTURE EVIDENCE | `audits/audit-log.schema.json`, `docs/AUDIT_LOG_POLICY.md`; no real logs |
| Manifest/checksum artifacts | GENERATED LOCAL EVIDENCE | `artifacts/release-manifest.json`, `artifacts/checksums.sha256` |
| SBOM/provenance artifacts | GENERATED LOCAL EVIDENCE | `artifacts/sbom.spdx.json`, `artifacts/sbom.cdx.json`, `artifacts/provenance.intoto.jsonl` |
| Release verification wrapper | IMPLEMENTED LOCAL-ONLY | `scripts/run_release_verify.ps1` |
| Runtime pin/lock | IMPLEMENTED | `.python-version`, `requirements-dev.txt`, `requirements-dev.lock` |
| RAG/model planning | PLANNING-ONLY | `docs/APPROVED_CORPUS_RAG_PLAN.md`, `docs/MODEL_CHANGE_POLICY.md` |
| Optional CI templates | OPTIONAL / NOT INSTALLED | `templates/ci/github-actions-local-verify.yml.template`, `templates/ci/github-actions-release-verify.yml.template`; `.github/workflows/` absent |
| Local target experiment evidence | PARTIAL EXECUTED | `csharp_desktop` PASS record exists; `plc_or_device_tool` remains deferred |
| Closeout gate coverage | NOT ACTIVE | This closeout document is not added to `docs_gate` in this task |

## Release Evidence Semantics

`artifacts/release-manifest.json` records `git_commit` as the source basis
commit at generation time. In this final refresh, that value is
`9ae69c5fbf65953db2b0efb82b4904098f8a7581`.

When generated artifacts are committed, the artifact-containing commit may be
newer than the manifest `git_commit`. That difference is expected for committed
generated evidence and is not an error by itself.

Formal release closeout should cite both:

- source basis commit from `artifacts/release-manifest.json`
- artifact-containing commit or tag used for the final record

This closeout does not change manifest schema or generator behavior. A future
schema may split the current `git_commit` meaning into `source_basis_commit`
and `artifact_commit`, but that is a future schema evolution and is not
implemented here.

## Current Verification Snapshot

This snapshot records the Stage 2 final local post-v0.1.0 evidence baseline
refresh after the Stage 1 documentation drift cleanup.

| item | status | evidence |
|---|---|---|
| basis branch/ref | PRESENT | `main` / `origin/main` |
| current repository commit before Stage 2 evidence regeneration | PRESENT | `9ae69c5fbf65953db2b0efb82b4904098f8a7581` |
| manifest source basis commit | PRESENT | `artifacts/release-manifest.json` records `9ae69c5fbf65953db2b0efb82b4904098f8a7581` |
| artifact-containing commit | PENDING UNTIL STAGE 2 EVIDENCE COMMIT | Regenerated artifacts and closeout updates are modified in the working tree and not yet committed |
| manifest generated timestamp | PRESENT | `2026-05-26T23:51:44Z` |
| manifest files recorded | PRESENT | `211` |
| checksum coverage | PRESENT | 5 entries: `artifacts/eval-report.json`, `artifacts/provenance.intoto.jsonl`, `artifacts/release-manifest.json`, `artifacts/sbom.cdx.json`, `artifacts/sbom.spdx.json` |
| checksum self-reference | ABSENT | `artifacts/checksums.sha256` does not list itself |
| eval case count | PRESENT | 14 named local-only non-LLM cases |
| eval report | GENERATED | `artifacts/eval-report.json` was generated explicitly at `2026-05-26T23:51:23Z` and records 14 passed, 0 failed |
| `csharp_desktop` target experiment | PASS | `docs/LOCAL_TARGET_EXPERIMENT_csharp_desktop_post_v0.1.0.md` |
| `plc_or_device_tool` target experiment | DEFERRED | Separate approval required |
| Python runtime used for verification | PRESENT | bundled Codex Python `3.12.13` |
| bare `python.exe` | ENVIRONMENT BLOCKED | Existing Windows logon session error in this Codex desktop shell |
| bundled Python `python -m pytest` | PASS | 72 passed |
| bundled Python `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed |
| bundled Python `python scripts/run_eval.py` | PASS | 14 named cases passed |
| bundled Python `python scripts/run_eval.py --report artifacts/eval-report.json` | PASS | report generated explicitly |
| bundled Python `python scripts/gates/eval_gate.py` | PASS | standalone eval gate passed |
| `scripts/run_local_verify.ps1` | PASS | Run by `scripts/run_release_verify.ps1`; pytest, quality gate, and three render dry-runs passed |
| `scripts/run_release_verify.ps1` | PASS | Manifest, checksum, SBOM, provenance artifacts regenerated with final checksum coverage; no release publication occurred |
| CI workflow | NOT INSTALLED | `.github/workflows/` remains absent |
| release publication | NOT DONE | No GitHub Release publication in this task |
| tag movement/signing | NOT DONE | No tag created, moved, rewritten, or signed in this task |
| release archive | NOT DONE | No archive created in this task |
| target render/write in final refresh | NOT RUN | No additional target render/write was executed in this final refresh |

## Closeout Verification Commands

| command | result | notes |
|---|---|---|
| `python -m pytest` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the existing Windows logon session error |
| `python scripts/quality_gate.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the existing Windows logon session error |
| `python scripts/run_eval.py` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the existing Windows logon session error |
| `python scripts/run_eval.py --report artifacts/eval-report.json` | ENVIRONMENT BLOCKED | Bare `python.exe` failed with the existing Windows logon session error |
| bundled Python `python scripts/run_eval.py --report artifacts/eval-report.json` | PASS | report generated explicitly before release wrapper regeneration |
| `powershell -ExecutionPolicy Bypass -File scripts/run_release_verify.ps1` | PASS | Local verification, standalone eval, manifest/checksum generation, SBOM/provenance generation, and final checksum regeneration passed |
| bundled Python `python scripts/run_eval.py` | PASS | 14 named cases passed |
| bundled Python `python -m pytest` | PASS | 72 passed |
| bundled Python `python scripts/quality_gate.py` | PASS | docs, hygiene, schema, examples, render drift, and secret scan passed |
| bundled Python `python scripts/gates/eval_gate.py` | PASS | standalone eval gate passed |
| `git diff --check` | PASS | LF-to-CRLF warnings only |

## Deferred / Not Implemented Surfaces

The following remain deferred or not implemented:

- Active `.github/workflows/` installation.
- CI artifact upload.
- Required CI checks.
- GitHub Release publication.
- Tag creation, movement, rewrite, or signing.
- Release archive creation.
- Signed release evidence.
- `eval_gate.py` integration into `scripts/quality_gate.py`.
- Routine eval report generation.
- Real audit log generation.
- Audit validator or quality-gate integration.
- RAG index, embeddings, vector DB, or retrieval tooling.
- Model comparison tooling.
- Prompt capture, model output capture, or model observability tooling.
- Optional design-stage pack render, gate, or example integration.
- `scenario_simulator` profile or example.
- Actual `plc_or_device_tool` target experiment execution.
- Additional target render/write in this final refresh.
- Application code, C# source/project/XAML/build assets, PLC/device code, live
  configuration, or live-write behavior.

## Approval Boundaries

Separate explicit owner approval is required before:

- Any additional target render/write.
- `plc_or_device_tool` actual target experiment.
- New profile or example creation.
- CI workflow installation.
- CI artifact upload.
- Release archive creation.
- GitHub Release publication.
- Tag creation, movement, rewrite, or signing.
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
eval reports, and this closeout do not grant approval by themselves.

## Known Limitations

- Release artifacts record source basis commit
  `9ae69c5fbf65953db2b0efb82b4904098f8a7581`; the artifact-containing commit
  for this Stage 2 refresh remains pending until the regenerated artifacts and
  closeout updates are committed.
- Stage 0 read-only review previously observed artifact-containing commit
  `ab77ab0a0b44c2f1bd700820bfeb358c6ec1bbe7`; that is historical evidence,
  not the current Stage 2 artifact-containing commit.
- `requirements-dev.lock` pins exact package versions but does not include
  wheel hashes.
- SBOM and provenance are minimal local-first evidence, not full certification,
  cloud attestation, signing, or publication workflows.
- The eval harness is standalone and not wired into `scripts/quality_gate.py`.
- `artifacts/eval-report.json` is explicit local evidence, not a routine
  default output.
- The optional CI templates are inert unless manually installed after approval.
- The `csharp_desktop` target experiment proves docs-only render behavior for
  one approved temporary target; it does not create or validate a real C#
  desktop application.
- The `plc_or_device_tool` actual target experiment remains deferred and is
  not the next default stage.
- This closeout document is not currently required by `docs_gate`.

## Recommended Next Steps

1. Keep the generated artifact source basis and artifact-containing commit
   semantics explicit in future closeouts.
2. Treat `docs/NEXT_DIRECTION_DECISION.md` as historical transition evidence.
3. Use `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` as the current
   implementation handoff.
4. Do not add `profiles/scenario_simulator` or
   `examples/scenario_simulator_minimal`.
5. Keep GitHub Release publication, active CI workflow installation, tag
   movement/signing, real audit logs, RAG/model tooling, release signing or
   archives, eval integration, audit automation, and `plc_or_device_tool`
   actual render deferred unless separately approved.
