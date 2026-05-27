# Eval Integration Decision

## Purpose

Record the Stage 3 decision for how the standalone local eval harness should
relate to routine verification, release verification, quality gates, and CI.

This is a decision document only. It does not modify eval code, quality gate
code, tests, CI workflows, release artifacts, application code, device code, or
live-write behavior.

## Current Eval State

Current status: KEEP STANDALONE BASELINE.

The repository has a local-only, non-LLM eval harness:

- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- 14 named cases under `evals/cases/`
- `evals/golden/render_structure_paths.txt`
- tests for the standalone runner and gate wrapper

Current coverage includes:

- render structure for base docs
- render structure for profile docs
- deterministic render path ordering
- approval-boundary policy language
- PASS / FAIL / NOT RUN / ENVIRONMENT BLOCKED honesty language
- PLC/device/live-write safety language
- absence of C# solution/project/source/XAML/build artifacts
- absence of live config and device-target artifacts
- obvious secret/private-value pattern scans
- prompt contract completeness
- release manifest shape
- checksum shape and self-reference exclusion
- minimal SPDX and CycloneDX SBOM shapes
- minimal local provenance JSONL shape

`scripts/run_release_verify.ps1` already runs `scripts/run_eval.py` when the
runner is present. That release-wrapper use remains console-only by default and
does not make evals part of `scripts/quality_gate.py`, CI, routine report
generation, or release publication.

## Options Evaluated

| option | decision | reason |
|---|---|---|
| Keep standalone baseline | APPROVED CURRENT STATE | Lowest-risk baseline; preserves fast local verification and keeps eval failures easy to interpret separately. |
| Add release-only execution through `run_release_verify.ps1` only | ALREADY PRESENT / KEEP CONSOLE-ONLY | The wrapper already runs the standalone eval command when present. No further release-blocking or report behavior is approved here. |
| Add opt-in quality gate flag, such as `quality_gate.py --include-eval` | DEFERRED | Useful later, but it requires code/tests and owner approval. Current evidence does not show repeated downstream failure modes that justify more coupling. |
| Add default `quality_gate.py` integration | NOT APPROVED | Default gate integration risks false positives, slower routine checks, and unclear ownership before repeated failures justify it. |
| Add CI integration | NOT APPROVED | CI remains not installed. Cloud CI introduces permission, artifact, retention, and publication concerns that need a separate owner decision. |

## Decision

Keep the eval harness standalone.

The safe next state is:

- `scripts/run_eval.py` remains the primary local eval command.
- `scripts/gates/eval_gate.py` remains standalone and separate from
  `scripts/quality_gate.py`.
- `scripts/run_release_verify.ps1` may continue running console-only evals as
  part of explicit local release verification.
- Routine `artifacts/eval-report.json` generation is not approved.
- `quality_gate.py` integration is not approved.
- CI integration is not approved.
- Release-blocking eval semantics are not approved.

This decision can be revisited if repeated downstream use shows concrete
failure modes that the current `quality_gate.py` checks do not catch.

## Current Limitations

- Evals are deterministic structural and policy checks, not semantic review.
- Evals do not use an LLM judge.
- Evals do not benchmark models.
- Evals do not validate downstream application behavior.
- Evals do not prove real C#, PLC/device, or live target behavior.
- Evals depend on current repository file shapes and policy phrases.
- Evals can catch missing required surfaces but cannot prove policy intent is
  sufficient for every downstream project.

## False Positive / False Negative Risks

False-positive risks:

- Policy phrase checks may fail after legitimate wording changes.
- Shape checks may fail during intentional manifest, checksum, SBOM, or
  provenance schema evolution.
- Render path checks may fail after intentional template additions.

False-negative risks:

- Phrase checks can pass while surrounding policy language is ambiguous.
- Forbidden artifact scans catch obvious baseline artifacts but cannot prove a
  downstream target is safe.
- Secret-pattern scans are heuristic and cannot prove absence of all sensitive
  data.
- Shape checks validate minimal structure, not full certification semantics.

## Approval Matrix

| future step | approval status | required owner approval |
|---|---|---|
| Add new repo-internal eval cases | Separate approval required | Name case files, safety scope, fixtures, and verification commands. |
| Generate `artifacts/eval-report.json` routinely | Not approved | Name when the report is generated, how checksums are refreshed, and whether the report is committed. |
| Make evals release-blocking | Not approved | Define failure policy, closeout wording, and release evidence impact. |
| Add `quality_gate.py --include-eval` | Not approved | Allow edits to `scripts/quality_gate.py`, tests, docs, and verification behavior. |
| Add default `quality_gate.py` eval integration | Not approved | Require repeated downstream failure evidence and a migration plan. |
| Add CI eval execution | Not approved | Require explicit `.github/workflows/` approval, permissions, triggers, artifact policy, and no-secret/no-publication boundaries. |

## Future Implementation Task If Approved

If the owner later approves opt-in quality-gate integration, the implementation
task should be narrow:

- Add an explicit `--include-eval` flag to `scripts/quality_gate.py`.
- Keep the default `scripts/quality_gate.py` behavior unchanged.
- Reuse `scripts/run_eval.py` or shared eval functions without changing case
  semantics.
- Add tests for default exclusion and opt-in inclusion.
- Update `docs/EVAL_POLICY.md`, `docs/VERIFICATION.md`, `STATUS.md`, and
  `ACCEPTANCE_TRACE.md`.
- Do not add CI workflows, routine report generation, release-blocking
  behavior, dependencies, application code, device code, or live-write behavior
  unless those are separately approved.

## Safety Confirmation

This decision does not add:

- eval integration into `scripts/quality_gate.py`
- CI workflows
- routine eval report generation
- release-blocking eval behavior
- release publication, archives, signing, upload, or tag movement
- RAG, model tooling, or audit log automation
- application code, C# source/project/XAML/build assets, PLC/device code, live
  configuration, or live-write behavior
