# VERIFICATION.md

## Purpose

Define verification expectations for this template repository.

## Current Verification Checklist

- Requested files exist.
- README and AGENTS read order match.
- Historical P0 docs-only scope is described as completed baseline.
- Render script exists and supports dry-run rendering.
- Quality gate implementation exists.
- Required root documents exist.
- Base templates exist.
- Profile templates exist.
- Example skeletons exist.
- Example skeletons include profile safety policy files.
- PLC/device example explicitly prohibits live device write and equipment detail exposure.
- No real application code exists.
- No real PLC/device code exists.
- No secrets or private data are included.

## Local Verification Flow

Recommended local command:

`powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`

The wrapper runs full pytest with the 50 slowest durations and skip reasons,
the no-report standalone eval, the quality gate, and all three example render
dry-runs in that order. It does not write rendered files and does not use
`--force`.

Before selecting Python, the wrapper removes ambient `PYTEST_ADDOPTS`,
`PYTEST_PLUGINS`, and `PYTHONPATH`, then disables third-party pytest plugin
autoload. The test session also isolates temporary Git repositories from
global config, signing, hooks, and interactive credential prompts. Platform
skips are limited to the reviewed node-and-reason policy in `tests/conftest.py`.

## Read-Only CI Verification Flow

The owner-approved first CI implementation target is installed at:

`.github/workflows/local-verify.yml`

The workflow is manual-only through `workflow_dispatch` and uses
`permissions: contents: read`. Dispatch requires a lowercase 40-character
`expected_sha`; checkout uses that ref and asserts the observed HEAD before
running checks. It mirrors the non-release local verification subset:

- `python -m pytest tests --durations=50 -rs`
- `python scripts/run_eval.py`
- `python scripts/quality_gate.py`
- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

It installs the exact development set from `requirements-dev.lock`, runs
`python -m pip check`, and uses Python `3.12.10`, the final Python 3.12 release
with Windows binary installers. Local V2 and hosted V3 both require that exact
patch version as declared in `.python-version`.
Third-party actions are pinned to immutable commit SHAs, checkout credentials
are not persisted, and the workflow retains only `contents: read`.

The eval step is console-only and runs without report flags after pytest and
before the quality gate. A nonzero eval exit fails only that manually dispatched
workflow run. It does not create a required check or release-blocking policy.

The workflow does not run release verification, generate release or eval report
artifacts, upload artifacts, publish releases, sign artifacts, move tags,
deploy, check out downstream repositories, run RAG/index tooling, run audit
automation, run MCP/Hermes code, or perform live-write behavior.

## Local Release Verification Flow

Recommended release evidence command:

`powershell -ExecutionPolicy Bypass -File scripts/run_release_verify.ps1`

The release wrapper is local-only. It runs, in order:

1. fail-closed clean tracked/untracked Git tree check
2. `scripts/run_local_verify.ps1`
3. `scripts/generate_manifest.py` from regular blobs in the exact `HEAD` tree
4. refresh `artifacts/eval-report.json` if that optional artifact is present
5. `scripts/generate_sbom.py`, if present
6. `scripts/generate_provenance.py`, if present
7. final checksum generation using the current full-bundle checksum policy
8. read-only `scripts/generate_checksums.py --verify`

There is no intermediate checksum. Provenance records the same canonical-LF
SHA-256 digests used by the final checksum for the manifest and present SBOM
products, excludes the checksum file and itself, and the final
checksum is written only after provenance. The checksum step is strict for the
current local release evidence bundle and covers all present release evidence
artifacts except `artifacts/checksums.sha256` itself. The following verify step
recomputes canonical LF hashes without writing and must match every entry. The
expected strict set is
`artifacts/release-manifest.json`, `artifacts/sbom.spdx.json`,
`artifacts/sbom.cdx.json`, and `artifacts/provenance.intoto.jsonl`.
If `artifacts/eval-report.json` is present when the wrapper runs, the wrapper
explicitly regenerates it after manifest generation and before the final
checksum. If it is absent, report generation is skipped and it is not included.

Optional steps are reported as `SKIPPED` with a reason when their scripts are
absent. The wrapper prints generated artifact paths and a PASS/FAIL/SKIPPED
summary. It does not call external services, publish or upload artifacts, create
or move tags, sign artifacts, create release archives, or install CI workflows.

Regenerating release evidence artifacts is a local write to `artifacts/` only.
It does not publish, sign, tag, archive, upload, or release anything.

If generated artifacts are committed, the manifest source-basis commit recorded
as `git_commit` may differ from the later artifact-containing commit. This is
expected for committed generated evidence. Verification closeout should record
that distinction honestly instead of treating it as a failure:

- source basis commit: value from `artifacts/release-manifest.json`
- artifact-containing commit or tag: repository ref that contains the committed
  artifacts

## Python Runtime And Dependencies

The preferred local verification runtime is pinned in `.python-version` and
documented in `docs/PYTHON_RUNTIME_POLICY.md`.

The hosted Windows V3 workflow and local V2 use exact Python `3.12.10`, the
final Python 3.12 release with Windows binary installers. Both use the same
exact development dependency lock and report the resolved runtime in their
console output.

Use `requirements-dev.txt` only when intentionally resolving the standard
local development requirement:

`python -m pip install -r requirements-dev.txt`

Use `requirements-dev.lock` for V2 and V3 exact verification:

`python -m pip install -r requirements-dev.lock`

The lock file is pip-compatible and limited to development verification
dependencies. It does not add runtime application, C#, PLC, device, cloud, or
live-target dependencies.

After installation, exact verification runs:

`python -m pip check`

The minimum post-V3 branch-protection contract enforces administrators and
linear history while disabling force pushes and branch deletion. It does not
add required status checks or pull-request review requirements. Applying or
changing that remote policy remains separately approval-gated.

## Manual Verification Flow

Run:

`python --version`

`python -m pip install -r requirements-dev.txt`

`python -m pytest`

`python scripts/quality_gate.py`

If bare `python.exe` is blocked in a Codex desktop Windows shell, use the
documented local verification runtime selected by `scripts/run_local_verify.ps1`.
The preferred local path is:

`.venv\Scripts\python.exe`

Report the bare Python command as ENVIRONMENT BLOCKED when this fallback is
needed.

## AI Readiness Scanner Flow

Focused scanner tests:

`python -m pytest tests/test_ai_readiness_scanner.py`

Full tests:

`python -m pytest`

Scanner Markdown output:

`python scripts/ai_readiness_scanner.py .`

Scanner JSON output:

`python scripts/ai_readiness_scanner.py --json .`

Quality gate:

`python scripts/quality_gate.py`

The scanner is standalone and local read-only. It is not wired into
`scripts/quality_gate.py`, does not create generated reports by default, does
not run target repository commands, and must not be used to authorize writes.
Scanner output is a readiness signal, not proof that secrets, private data, or
live configuration are absent. Domain risk flags are conservative path-level
indicators that require review.

## Local Eval Flow

Run the standalone local eval harness with:

`python scripts/run_eval.py`

The runner discovers named `evals/cases/*.yml` files in deterministic filename
order. It is local-only, non-LLM, and not wired into `scripts/quality_gate.py`
by default.

The manual `.github/workflows/local-verify.yml` workflow also runs exactly
`python scripts/run_eval.py` under `workflow_dispatch` with `contents: read`.
It uses no report flags and creates no eval artifact.

Phase 5 report-only planning is documented in
`docs/EVAL_REPORT_INTEGRATION_PLAN.md`. Eval evidence may be summarized in
audit / trace / receipt closeouts using the eval receipt fields in
`docs/AUDIT_TRACE_SCHEMA.md`.

To write an optional machine-readable report, run:

`python scripts/run_eval.py --report artifacts/eval-report.json`

The report path must remain under `artifacts/`. The report records
`schema_version`, `generated_at_utc`, `total_cases`, `passed_cases`,
`failed_cases`, and per-case results with stable case names. It must not contain
secrets, private input, raw prompts, raw source, tool-call bodies, model
outputs, or live target details.

If `artifacts/eval-report.json` is present, the checksum policy treats it as a
present optional release evidence artifact. Regenerate `artifacts/checksums.sha256`
and run `python scripts/generate_checksums.py --verify` after creating the
report when checksum coverage is being asserted.

Do not generate eval reports routinely. The approved CI boundary is only the
manual console step above. Do not make evals release-blocking, automatic,
required-check policy, report-producing in CI, or part of
`scripts/quality_gate.py` unless a separate task explicitly approves that
integration.

## Approved Corpus Digest Planning Flow

Phase 6 approved corpus digest planning is documented in:

`docs/APPROVED_CORPUS_DIGEST_PLAN.md`

The plan defines candidate corpus classes, forbidden corpus, required metadata,
risk labels, digest/hash policy, redaction and encoding checks, source path
rules, `08_Study` limits, and RSID/downstream evidence limits before any local
RAG work.

Planning tasks for this phase must verify that no digest artifact, `corpus/`,
`retrieval/`, `index/`, embeddings, vector database, external RAG service, CI
integration, quality-gate integration, audit automation, MCP/Hermes
implementation, release automation, artifact regeneration, downstream edit, or
eval report generation occurred unless a separate task explicitly approves it.

If a digest artifact is not generated, report it as `NOT RUN` or `not
generated`. Do not imply digest generation or retrieval verification passed.

## Approved Corpus Digest Check Flow

Safe check-only command:

`python scripts/generate_corpus_digest.py --check --json`

This command checks the current `artifacts/corpus-digest.json` and its
digest-listed source files. It must not modify `artifacts/corpus-digest.json`,
create corpus artifacts, expand the allow-list, create `corpus/`,
`retrieval/`, or `index/`, or run release verification.

Do not run `--write` in a boundary-hardening or review-only task. Write mode is
guarded but requires a future separately approved Phase 6G digest refresh task
that explicitly names artifact write permission, approval reference,
source-basis expectations, post-write JSON validation, safety scan, full local
verification, retention, and commit decision.

Release verification and artifact checksum regeneration are not part of the
check command.

## Local RAG Design Planning Flow

Phase 7A local RAG design is documented in:

`docs/LOCAL_RAG_DESIGN.md`

The design defines a future local-only, read-only lexical retriever over
`artifacts/corpus-digest.json` and digest-listed repo-owned source files. It is
planning-only and advisory. It does not implement RAG, retrieval, indexing,
embeddings, vector storage, external service calls, CI integration,
quality-gate integration, audit automation, MCP/Hermes work, release
automation, downstream edits, or digest regeneration.

Verification for Phase 7A documentation tasks must confirm that changed files
stay within the approved documentation scope, no generated corpus artifact is
created, no digest artifact is regenerated, and no `corpus/`, `retrieval/`, or
`index/` folder is created.

The quality gate includes:
- Documentation presence.
- Repository hygiene.
- Template config/schema validation.
- Example skeleton validation.
- Rendered example file-set drift validation.
- Golden rendered-content validation.
- Secret/private-pattern scan.
- Core JSON evidence validation.

Agent Quality bundle validation remains in the full standalone
`json_evidence_gate.run()` path and `agent_quality_static_check`. Release
checksums remain in `generate_checksums.py --verify` and the release wrapper;
neither optional surface is part of the default core quality gate.

## Render Dry-Run Checks

Run:

- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

No mode flag is also a preview. An actual target write requires explicit
`--apply`; `--force` is valid only with `--apply`.

## Historical P0 Verification

P0 used policy-level verification only. At that time, render scripts, quality gates, and examples were intentionally absent. That is historical context, not the current state.

## Verification Mesh

Current and future verification layers may include:
- Unit tests.
- Smoke tests.
- Runtime trace.
- Acceptance trace.
- Policy validation.
- Example validation.
- Audit evidence.

## Audit / Trace / Receipt Evidence

Use `docs/AUDIT_TRACE_SCHEMA.md` as the field reference when a closeout needs a
structured audit-style receipt. Receipt evidence should summarize repository
state, changed files, approvals, side effects, commands run, commands not run,
verification result, safety exclusions, CI run evidence, artifact upload
status, unresolved risks, and next step.

Receipt evidence must not include full prompt transcripts, raw private data,
raw command logs by default, unredacted tool-call bodies, secrets, live values,
local Windows absolute paths, or generated downstream source.

The schema is manual evidence guidance only. It does not create audit logs,
schema validation, quality-gate integration, CI integration, release evidence,
or automation.

## Release Readiness

Use `docs/RELEASE_CHECKLIST.md` before tagging a reusable baseline. Known gaps and intentionally unsupported behavior are tracked in `docs/KNOWN_LIMITATIONS.md`.

Local package boundaries are documented in `docs/LOCAL_RELEASE_PACKAGE.md`.

CI policy is documented in `docs/CI_POLICY.md`. The current CI surface is a
manual read-only local verification workflow. It is not a release workflow,
required-check policy, artifact upload policy, signing policy, deployment
policy, tag policy, or publication mechanism.

## Verification Hygiene

Verification reports must state exactly what was run, what was not run, and why.
Focused verification is acceptable for narrow documentation or policy changes
when broader checks are explicitly out of scope and marked `NOT RUN`.

Generated-output-sensitive work must distinguish:

- temporary output produced outside the repository
- committed generated artifacts under `artifacts/`
- generated release evidence that was intentionally regenerated
- release evidence that was intentionally not regenerated

Do not imply that release verification passed unless `scripts/run_release_verify.ps1`
or an explicitly equivalent approved release verification flow was run.

Line-ending warnings, if present, should be reported as hygiene notes unless
they affect executable behavior or generated artifact content. A local commit is
not a push, tag, release, publication, artifact upload, or deployment.

## NOT RUN Principle

If a check was not executed, mark it as NOT RUN with a reason. Do not imply success for checks that were not run.
