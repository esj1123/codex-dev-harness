# Optional Eval Harness Plan

## Purpose

Record a future optional eval harness direction without implementing it.

This document is planning-only. It does not create `scripts/run_eval.py`, an `evals/` directory, grader code, test fixtures, or automation.

## Current State

Eval harness status: MINIMAL STANDALONE IMPLEMENTATION PRESENT.

No eval harness was implemented in the `v0.1.0` baseline. A minimal local-only
standalone harness now exists after v0.1.0.

Minimal local-only implementation status: PRESENT.

The design and implementation boundary are documented in
`docs/MINIMAL_EVAL_HARNESS_DESIGN.md`. The implementation creates local
machine-readable cases, a golden path list, a standalone runner, a standalone
gate wrapper, and tests. It does not integrate with `scripts/quality_gate.py` or
CI by default.

## Candidate Evals

| eval | purpose | current state |
|---|---|---|
| render structure eval | Check expected files, forbidden extensions, approved output roots, and deterministic output path order | implemented |
| policy phrase eval | Check required safety phrases, approval boundary language, and NOT RUN honesty language | implemented |
| forbidden artifact eval | Check for generated code, workflows, live configs, secrets, and prohibited files such as solution/project artifacts | implemented |
| regression/determinism eval | Repeat the same input, compare expected output path lists, and detect drift | implemented |
| downstream scaffold eval | Check whether downstream target docs remain design-only and source-index driven | planned only |
| prompt/task contract eval | Check whether task prompts preserve no-touch zones and verification expectations | planned only |

## Proposed Future Files

These paths exist in the minimal standalone implementation:

- `evals/cases/render_structure.yml`
- `evals/cases/policy_phrases.yml`
- `evals/cases/forbidden_artifacts.yml`
- `evals/golden/`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`

## Proposed Future Output

Optional output:

- `artifacts/eval-report.json`

No report or `artifacts/` directory is created by default. `scripts/run_eval.py`
can write this report only when called with `--report`.

## Non-Goals

- Do not add external-service calls.
- Do not add an LLM judge.
- Do not add dependencies.
- Do not add CI.
- Do not wire evals into `quality_gate.py` without approval.
- Do not make evals release-blocking without approval.

## Approval Requirements

Further expansion requires explicit approval.

Before implementation, decide:

- Whether new evals are required versus optional.
- Whether new fixture categories remain fully synthetic.
- Whether eval output should stay console-only by default.
- Whether evals remain local-only.
- Whether evals become part of `quality_gate.py` or remain separate.
- Whether `artifacts/eval-report.json` should be written in routine verification.

## Recommendation

Keep `eval_gate.py` standalone until repeated local use proves it should become
part of `scripts/quality_gate.py`. Treat quality-gate integration, CI
integration, extra dependencies, report generation in routine checks, and
release-blocking evals as separate approval decisions.
