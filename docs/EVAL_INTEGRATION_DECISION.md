# Eval Integration Decision

## Purpose

Record the Stage 3 decision for how the standalone local eval harness should
relate to routine verification, release verification, quality gates, and CI.

This record accompanies a narrow update to the existing Local Verify workflow.
It does not modify eval code, quality gate code, release artifacts, application
code, device code, or live-write behavior.

Current sequencing note: this record is historical eval-integration risk
evidence. It is superseded for implementation sequencing by
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, which makes eval / report
integration the third implementation target after read-only CI + verification
hygiene and audit / trace / receipt schema. The runner remains standalone from
`scripts/quality_gate.py`, while the existing manual Local Verify workflow now
runs its console-only command. Phase 5 report-only planning is documented in
`docs/EVAL_REPORT_INTEGRATION_PLAN.md`.

## Current Eval State

Current status: MANUAL_LOCAL_VERIFY_CONSOLE_EVAL_APPROVED.

The repository has a local-only, non-LLM eval harness:

- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- 15 named cases under `evals/cases/`
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
runner is present. The manual `.github/workflows/local-verify.yml` workflow is
also approved to run exactly `python scripts/run_eval.py` after pytest and
before the quality gate. Both uses remain console-only and do not make evals
part of `scripts/quality_gate.py`, routine report generation, release
publication, or release-blocking policy.

A prior green manual Local Verify run did not prove eval health because the
workflow omitted the standalone command. A later direct eval detected a stale
render-determinism expectation. That concrete verification gap justifies this
narrow manual workflow integration without broadening any other boundary.

## Options Evaluated

| option | decision | reason |
|---|---|---|
| Keep standalone runner and gate boundary | APPROVED CURRENT STATE | The runner and gate remain separate from `scripts/quality_gate.py`; the manual workflow only invokes the console command. |
| Add release-only execution through `run_release_verify.ps1` only | ALREADY PRESENT / KEEP CONSOLE-ONLY | The wrapper already runs the standalone eval command when present. No further release-blocking or report behavior is approved here. |
| Add console-only execution to manual Local Verify | APPROVED CURRENT STATE | The exact command runs under `workflow_dispatch` with `contents: read`, no report flags, and no artifact upload. |
| Add opt-in quality gate flag, such as `quality_gate.py --include-eval` | DEFERRED | Useful later, but it requires code/tests and owner approval. Current evidence does not show repeated downstream failure modes that justify more coupling. |
| Add default `quality_gate.py` integration | NOT APPROVED | Default gate integration risks false positives, slower routine checks, and unclear ownership before repeated failures justify it. |
| Add automatic or report-producing CI integration | NOT APPROVED | Push/PR triggers, report artifacts, broader permissions, and required-check semantics remain separate owner decisions. |

## Decision

Keep the eval runner standalone and approve one console-only invocation in the
existing manual Local Verify workflow.

The current safe state is:

- `scripts/run_eval.py` remains the primary local eval command.
- `scripts/gates/eval_gate.py` remains standalone and separate from
  `scripts/quality_gate.py`.
- `scripts/run_release_verify.ps1` may continue running console-only evals as
  part of explicit local release verification.
- `.github/workflows/local-verify.yml` runs exactly
  `python scripts/run_eval.py` after pytest and before
  `python scripts/quality_gate.py`.
- The workflow remains `workflow_dispatch` only with `contents: read`, no
  secrets, no report flags, and no artifact generation or upload.
- A nonzero eval exit fails only that manually dispatched Local Verify run. It
  does not create a required check or release-blocking rule.
- Routine `artifacts/eval-report.json` generation is not approved.
- `quality_gate.py` integration is not approved.
- Automatic-trigger or additional CI eval integration is not approved.
- Release-blocking eval semantics are not approved.

Phase 5 planning in `docs/EVAL_REPORT_INTEGRATION_PLAN.md` allows eval evidence
to be summarized in audit / trace / receipt closeouts. The later approval
recorded here adds only manual console execution; it does not approve report
generation by default, quality-gate integration, automatic CI triggers, or
release-blocking behavior.

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
| Run console-only evals in manual Local Verify | Approved | Exact path, command, ordering, `workflow_dispatch`, `contents: read`, no-report policy, and failure scope are fixed by this decision. |
| Add any other CI eval execution | Not approved | Require explicit workflow approval, permissions, triggers, artifact policy, and no-secret/no-publication boundaries. |

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
- Do not add workflows or triggers beyond the approved manual Local Verify
  command, routine report generation, release-blocking behavior, dependencies,
  application code, device code, or live-write behavior unless those are
  separately approved.

## Safety Confirmation

This decision does not add:

- eval integration into `scripts/quality_gate.py`
- new CI workflows or automatic triggers
- eval report generation or artifact upload from Local Verify
- routine eval report generation
- release-blocking eval behavior
- release publication, archives, signing, upload, or tag movement
- RAG, model tooling, or audit log automation
- application code, C# source/project/XAML/build assets, PLC/device code, live
  configuration, or live-write behavior
