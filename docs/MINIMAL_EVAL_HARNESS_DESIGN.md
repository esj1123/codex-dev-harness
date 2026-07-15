# Minimal Eval Harness Design

## Purpose

Document the minimal, local-only eval harness for codex-dev-harness.

The harness provides machine-readable verification for template safety and
regression behavior. It checks whether generated or rendered template outputs
preserve expected file structure, required policy language, forbidden artifact
boundaries, and deterministic output path behavior.

The implementation is intentionally minimal and standalone from the quality
gate. It does not use an LLM judge, external services, private input,
prompt/session capture, automatic CI triggers, release artifacts, or live
target behavior.

## Current State

Status: MINIMAL STANDALONE IMPLEMENTATION WITH MANUAL CONSOLE VERIFICATION.

The repository contains:

- expanded named case files under `evals/cases/`
- `evals/golden/render_structure_paths.txt`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- `tests/test_run_eval.py`
- `tests/test_eval_gate.py`

The harness remains separate from `scripts/quality_gate.py`. The existing
manual read-only Local Verify workflow runs exactly
`python scripts/run_eval.py` without report flags. No eval report is generated
unless the runner is called explicitly with `--report`.

The default runner discovers `evals/cases/*.yml` in deterministic filename
order. Each case must have a stable `name` so console output and optional JSON
reports can be compared across runs.

The Stage 3 integration decision is recorded in
`docs/EVAL_INTEGRATION_DECISION.md`. The current decision keeps the eval
runner and `scripts/gates/eval_gate.py` separate from
`scripts/quality_gate.py`, approves console-only execution in manual Local
Verify, and does not approve routine report generation, automatic CI triggers,
or release-blocking eval behavior.

## Design Principles

- Local-only by default.
- Deterministic checks before subjective review.
- Machine-readable case definitions and machine-readable output.
- Synthetic fixture input only.
- No private source capture.
- No prompt or session capture.
- No live target access.
- No release publication behavior.
- Manual console-only Local Verify execution; no automatic CI trigger.
- Standalone first; promotion into `quality_gate.py` requires separate approval.

## Non-Goals

- No LLM judge.
- No benchmark against external models.
- No private source capture.
- No prompt or session capture.
- No automatic, report-producing, required-check, or release-blocking CI
  integration.
- No downstream application validation.
- No device, PLC, live target, or runtime behavior.
- No release manifest, checksum, SBOM, or provenance generation.
- No replacement for `scripts/quality_gate.py`.

## Candidate Eval 1: Render Structure Eval

Purpose: verify that a template render plan preserves expected structure before
or after rendering.

Planned checks:

- expected files are present in the output path list
- unexpected files are absent from the output path list
- forbidden extensions are rejected or reported
- output paths remain under the approved target root
- output path order is deterministic and stable

Implemented machine-readable fields:

- eval id
- target profile or base-template mode
- input config path
- expected output path list
- forbidden extension list
- expected result
- evidence notes

## Candidate Eval 2: Policy Phrase Eval

Purpose: verify that generated or maintained documents retain required safety
and closeout language.

Planned checks:

- required safety phrases are present
- required approval boundary language is present
- required NOT RUN honesty language is present
- prohibited approval-free live-write language is absent
- missing phrases are reported with document path and phrase id

Implemented machine-readable fields:

- eval id
- document path
- required phrase ids
- prohibited phrase ids
- expected result
- evidence notes

## Candidate Eval 3: Forbidden Artifact Eval

Purpose: verify that template use does not introduce files that would turn the
repository or generated output into a real application, live-device project, or
secret-bearing package.

Planned checks:

- no `.sln`
- no `.csproj`
- no source code files
- no live config
- no secrets
- no workflow files unless explicitly approved
- no device or live-write artifacts

Implemented machine-readable fields:

- eval id
- scan root
- forbidden path patterns
- forbidden extensions
- expected result
- evidence notes

## Candidate Eval 4: Regression / Determinism Eval

Purpose: detect render drift and nondeterministic output planning.

Planned checks:

- repeat the same input
- compare expected output path list across repeated runs
- detect path-list drift
- report added, removed, or reordered planned outputs
- keep content comparison optional and out of the minimal baseline

Implemented machine-readable fields:

- eval id
- repeated input config path
- expected output path list
- comparison mode
- expected result
- evidence notes

## Implemented Files

These files are present in the minimal standalone implementation:

- `evals/cases/render_structure_base_docs.yml`
- `evals/cases/render_structure_profile_docs.yml`
- `evals/cases/render_determinism_paths.yml`
- `evals/cases/rendered_python_cli_readiness.yml`
- `evals/cases/policy_approval_boundary.yml`
- `evals/cases/policy_not_run_honesty.yml`
- `evals/cases/policy_plc_safety.yml`
- `evals/cases/forbidden_csharp_artifacts.yml`
- `evals/cases/forbidden_live_config.yml`
- `evals/cases/forbidden_secret_patterns.yml`
- `evals/cases/prompt_contract_completeness.yml`
- `evals/cases/release_manifest_shape.yml`
- `evals/cases/checksum_shape.yml`
- `evals/cases/sbom_shape.yml`
- `evals/cases/provenance_shape.yml`
- `evals/golden/render_structure_paths.txt`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- `tests/test_run_eval.py`
- `tests/test_eval_gate.py`

The 15 named cases cover base render docs, profile render docs, render path
determinism, rendered Python CLI readiness, approval policy, NOT RUN honesty,
PLC/device safety, forbidden C# artifacts, forbidden live config, forbidden
secret patterns, prompt contract completeness, release manifest shape,
checksum shape, SBOM shape, and provenance shape.

## Optional Output

Optional output:

- `artifacts/eval-report.json`

The report should be machine-readable and should record:

- `schema_version`
- `generated_at_utc`
- `total_cases`
- `passed_cases`
- `failed_cases`
- per-case result objects with stable case names, pass/fail values, and
  summarized messages

The report is not written by default. It is produced only when
`scripts/run_eval.py` is called with `--report`.

The `--report` argument must be a repo-internal relative path, such as
`artifacts/eval-report.json`, and must stay under `artifacts/`. Absolute paths,
parent traversal with `..`, and repo-internal non-artifact paths are rejected
before any report file or parent directory is created.

The report must not include secrets, private input, raw prompts, raw source,
tool-call bodies, model outputs, or machine/environment-sensitive details.

## Approval Rule

Implementation of the minimal standalone runner is approved for this stage.
Further expansion requires separate explicit owner approval.

Approval must name the implementation surface, including whether the task may:

- modify `scripts/quality_gate.py`
- generate `artifacts/eval-report.json`
- add dependencies
- integrate with CI

The current approval is limited to the exact manual Local Verify console
command. Every broader integration surface still requires separate approval.

## Future Boundary

The recommended next boundary is a promotion decision, not automatic expansion.

The current promotion decision is
MANUAL_LOCAL_VERIFY_CONSOLE_EVAL_APPROVED.

Before approving any expansion, decide:

- whether the runner remains separate from `quality_gate.py`
- whether report generation should become part of routine verification
- whether optional report paths remain limited to repo-internal relative paths
- whether failed evals are advisory or blocking
- whether CI remains limited to the current manual console-only command

## Safety Confirmation

This implementation does not add:

- eval reports by default
- audit logging code
- RAG tooling
- new CI workflows or automatic triggers
- eval report generation or artifact upload from Local Verify
- release artifacts
- real application code
- C# source, solution, project, XAML, or build assets
- PLC/device code
- live target write support
- secrets, credentials, private input, raw source bundles, equipment details,
  IPs, ports, tags, or live parameter values
