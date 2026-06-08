# Optional Eval Harness Plan

## Purpose

Record a future optional eval harness direction without implementing it.

This document is planning-only. It does not create `scripts/run_eval.py`, an `evals/` directory, grader code, test fixtures, or automation.

Current sequencing note: this plan is historical eval-planning evidence. The
current implementation sequence is defined by
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, where eval / report integration is
the third implementation target after read-only CI + verification hygiene and
audit / trace / receipt schema. The standalone runner remains the current
runtime boundary until that approved phase begins.

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

The Stage 3 integration decision is documented in
`docs/EVAL_INTEGRATION_DECISION.md`. The decision keeps the standalone baseline
and does not approve routine eval report generation, `scripts/quality_gate.py`
integration, release-blocking evals, or CI integration.

## Named Evals

The minimal standalone runner now uses expanded named local cases instead of a
small set of broad case files.

| eval case | purpose | current state |
|---|---|---|
| `render_structure_base_docs` | Check base rendered docs for minimal examples | implemented |
| `render_structure_profile_docs` | Check profile-specific rendered docs and safety docs | implemented |
| `render_determinism_paths` | Compare deterministic render path planning against the golden list | implemented |
| `policy_approval_boundary` | Check approval-gated side-effect language | implemented |
| `policy_not_run_honesty` | Check PASS/FAIL/NOT RUN/ENVIRONMENT BLOCKED honesty language | implemented |
| `policy_plc_safety` | Check PLC/device/live-write safety boundaries | implemented |
| `forbidden_csharp_artifacts` | Check absence of C# solution/project/source/XAML/build artifacts | implemented |
| `forbidden_live_config` | Check absence of live config, connection, tag-map, and device-target artifacts | implemented |
| `forbidden_secret_patterns` | Check safe text surfaces for obvious token/key/password/private-value patterns | implemented |
| `prompt_contract_completeness` | Check reusable prompt contract template completeness | implemented |
| `release_manifest_shape` | Check local release manifest JSON shape | implemented |
| `checksum_shape` | Check checksum format, ordering, coverage, and self-reference exclusion | implemented |
| `sbom_shape` | Check minimal SPDX and CycloneDX JSON shapes | implemented |
| `provenance_shape` | Check minimal local provenance JSONL shape | implemented |

## Proposed Future Files

These paths exist in the minimal standalone implementation:

- named case files under `evals/cases/`
- `evals/golden/`
- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`

## Proposed Future Output

Optional output:

- `artifacts/eval-report.json`

No report or `artifacts/` directory is created by default. `scripts/run_eval.py`
can write this report only when called with `--report`. The report path must be
a repo-internal relative path under `artifacts/`; absolute paths, parent
traversal with `..`, and repo-internal non-artifact paths are rejected.

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
- Whether optional report paths should remain limited to repo-internal relative paths.

## Recommendation

Keep `eval_gate.py` standalone until repeated local use proves it should become
part of `scripts/quality_gate.py`. Treat quality-gate integration, CI
integration, extra dependencies, report generation in routine checks, and
release-blocking evals as separate approval decisions.

Stage 3 confirms that recommendation as the current baseline decision.
