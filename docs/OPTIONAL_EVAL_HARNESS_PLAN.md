# Optional Eval Harness Plan

## Purpose

Record a future optional eval harness direction without implementing it.

This document is planning-only. It does not create `scripts/run_eval.py`, an `evals/` directory, grader code, test fixtures, or automation.

## Current State

Eval harness status: FUTURE OPTIONAL.

No eval harness is implemented in the `v0.1.0` baseline.

## Candidate Evals

| eval | purpose | current state |
|---|---|---|
| render structure eval | Check that rendered target docs have expected structure | planned only |
| forbidden artifact eval | Check for generated code, workflows, live configs, and prohibited files | planned only |
| policy phrase eval | Check whether required safety phrases and approval gates are present | planned only |
| downstream scaffold eval | Check whether downstream target docs remain design-only and source-index driven | planned only |
| prompt/task contract eval | Check whether task prompts preserve no-touch zones and verification expectations | planned only |

## Non-Goals

- Do not implement eval code now.
- Do not create `evals/`.
- Do not create `scripts/run_eval.py`.
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

## Recommendation

Keep eval harness work deferred until repeated downstream adoption creates concrete failure modes worth checking automatically.
