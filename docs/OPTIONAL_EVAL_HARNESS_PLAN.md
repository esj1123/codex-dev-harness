# Optional Eval Harness Plan

## Purpose

Record a future optional eval harness direction without implementing it.

This document is planning-only. It does not create `scripts/run_eval.py`, an `evals/` directory, grader code, test fixtures, or automation.

## Current State

Eval harness status: FUTURE OPTIONAL.

No eval harness is implemented in the `v0.1.0` baseline.

Minimal local-only design status: DOCUMENTED ONLY.

The design document is `docs/MINIMAL_EVAL_HARNESS_DESIGN.md`. It defines a
future local-only, machine-readable eval harness direction without creating
eval cases, fixtures, runner code, gate integration, reports, or CI.

## Candidate Evals

| eval | purpose | current state |
|---|---|---|
| render structure eval | Check expected files, forbidden extensions, approved output roots, and deterministic output path order | design only |
| policy phrase eval | Check required safety phrases, approval boundary language, and NOT RUN honesty language | design only |
| forbidden artifact eval | Check for generated code, workflows, live configs, secrets, and prohibited files such as solution/project artifacts | design only |
| regression/determinism eval | Repeat the same input, compare expected output path lists, and detect drift | design only |
| downstream scaffold eval | Check whether downstream target docs remain design-only and source-index driven | planned only |
| prompt/task contract eval | Check whether task prompts preserve no-touch zones and verification expectations | planned only |

## Proposed Future Files

These paths are proposed for a separate future implementation task only:

- `evals/cases/render_structure.yml`
- `evals/cases/policy_phrases.yml`
- `evals/cases/forbidden_artifacts.yml`
- `evals/golden/`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`

## Proposed Future Output

Future output, if implementation is separately approved:

- `artifacts/eval-report.json`

No report or `artifacts/` directory is created by the current plan/design
documents.

## Non-Goals

- Do not implement eval code now.
- Do not create `evals/`.
- Do not create `scripts/run_eval.py`.
- Do not create `scripts/gates/eval_gate.py`.
- Do not create eval fixtures.
- Do not generate eval reports.
- Do not add dependencies.
- Do not add CI.
- Do not convert eval planning into enforcement without approval.

## Approval Requirements

Implementation requires explicit approval.

Before implementation, decide:

- Which evals are required versus optional.
- Whether eval fixtures can be fully synthetic.
- How eval output should be recorded.
- Whether evals run locally only.
- Whether evals become part of `quality_gate.py` or remain separate.
- Whether `artifacts/eval-report.json` should be written or stdout-only output is enough.

## Recommendation

Keep eval harness implementation deferred until the owner explicitly approves a
Stage 4 implementation boundary. The safest next step is to review
`docs/MINIMAL_EVAL_HARNESS_DESIGN.md` and decide which candidate evals, if any,
are worth implementing as local-only checks.
