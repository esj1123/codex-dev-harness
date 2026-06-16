# Eval Report Integration Plan

## 1. Purpose

Plan Phase 5 eval/report integration against the audit / trace / receipt schema.

This plan defines how standalone eval evidence may be summarized in receipts
and, when explicitly approved, in manual report artifacts. It does not change
default eval runtime behavior, wire evals into `scripts/quality_gate.py`, make
evals release-blocking, generate routine reports, add CI eval integration, or
create artifacts except explicitly requested local eval report files.

## 2. Current eval baseline

Current eval status: standalone.

The current eval implementation includes:

- `scripts/run_eval.py`
- `scripts/gates/eval_gate.py`
- named cases under `evals/cases/`
- golden data under `evals/golden/`
- tests for the standalone runner and standalone gate wrapper

The runner discovers `evals/cases/*.yml` in deterministic filename order. The
current named cases cover render structure, render determinism, approval
boundaries, NOT RUN honesty, PLC/device safety, forbidden C# artifacts,
forbidden live config, forbidden secret patterns, prompt contract completeness,
release manifest shape, checksum shape, SBOM shape, and provenance shape.

The runner is local-only, non-LLM, standard-library-based, and separate from
`scripts/quality_gate.py`. It writes no report unless called with `--report`
or the paired Phase 5A split-output options `--summary-report` and
`--cases-report`.

## 3. Relationship to audit / trace / receipt schema

`docs/AUDIT_TRACE_SCHEMA.md` defines the manual receipt fields for task
closeouts. Eval/report integration should use that schema as the evidence
container instead of creating a new logging surface.

Eval evidence may be summarized in:

- `commands_run`
- `commands_not_run`
- `verification_result`
- `status_label`
- `safety_exclusions`
- `workflow_run_id`, if CI eval execution is separately approved later
- optional eval-specific receipt fields defined in this plan

Receipt summaries must not copy raw prompts, raw private data, raw command
logs by default, unredacted tool-call bodies, local Windows absolute paths, or
downstream source.

## 4. Report-only integration target

The first safe target is report-only integration at the receipt level:

- eval runner remains standalone
- eval command results may be summarized in receipts
- eval report generation remains explicit/manual only
- no default quality-gate integration
- no release-blocking behavior
- no routine report generation
- no CI eval integration unless separately approved
- no LLM judge or external service

This target improves closeout precision without coupling evals to routine
verification or release publication.

Phase 5A implements this target as report-only eval evidence optimization:

- existing `python scripts/run_eval.py` behavior remains unchanged
- existing `--report artifacts/eval-report.json` behavior remains
  backward-compatible
- split reports are generated only when both `--summary-report` and
  `--cases-report` are explicitly provided
- split summary reports contain `schema_version`, `generated_at_utc`,
  `total_cases`, `passed_cases`, `failed_cases`, `passed`, `cases_ref`, and
  `cases_sha256`
- split cases reports are JSONL with one safe case-result object per line
- `cases_sha256` is calculated from the exact cases JSONL bytes
- split output does not add quality-gate integration, CI eval integration,
  release-blocking behavior, routine report generation, audit automation, or
  release artifact regeneration

## 5. Required eval receipt fields

When eval evidence is relevant, receipts should include:

| field | meaning |
|---|---|
| `eval_command` | Command or stable command label, such as `python scripts/run_eval.py`. |
| `eval_scope` | Case set or reason eval was scoped or not run. |
| `eval_case_count` | Total discovered or executed eval cases. |
| `eval_pass_count` | Passed case count. |
| `eval_fail_count` | Failed case count. |
| `eval_report_path` | Repo-relative report path, only if explicitly generated. |
| `eval_report_generation_status` | `not generated`, `generated`, `not run`, or `blocked`. |
| `eval_integration_status` | `standalone`, `receipt-summary-only`, `ci-approved`, or other approved state. |
| `eval_gate_status` | Quality-gate relationship, such as `not integrated`. |
| `release_blocking_status` | Release-blocking relationship, such as `not release-blocking`. |
| `notes_or_failures_summary` | Short safe summary of caveats or failed case names. |

These fields are receipt fields, not a new artifact format.

## 6. Eval report formats

The existing monolithic report remains available only when explicitly generated
with `--report`. It keeps the existing report shape:

- `schema_version`
- `generated_at_utc`
- `total_cases`
- `passed_cases`
- `failed_cases`
- `passed`
- per-case objects with stable case names, pass/fail values, and summarized
  messages

The Phase 5A split summary report is available only when explicitly generated
with paired `--summary-report` and `--cases-report` options. The summary report
contains:

- `schema_version`
- `generated_at_utc`
- `total_cases`
- `passed_cases`
- `failed_cases`
- `passed`
- `cases_ref`
- `cases_sha256`

The Phase 5A cases report is JSONL with one safe case-result object per line:
stable case name, pass/fail value, and summarized messages. The summary
`cases_sha256` value is calculated from the exact cases JSONL bytes.

Optional future additions must remain safe summaries. They may include:

- `basis_commit`
- `eval_scope`
- `receipt_task_id`
- `receipt_status_label`

Adding fields to the report format requires a separate implementation task
with tests and verification.

## 7. Forbidden eval report content

Eval receipts and eval reports must not contain:

- private raw data
- raw prompts or prompt transcripts
- raw source bundles
- unredacted tool-call request or response bodies
- model outputs
- secrets, tokens, credentials, account identifiers, or private values
- real IP values, port values, live config, device values, broker values, or
  account values
- local Windows absolute paths
- generated downstream source
- external or private corpus material
- raw command logs by default

Use case names, counts, status labels, repo-relative paths, hashes, and safe
summaries instead.

## 8. CI-visible eval boundary

The current `Local Verify` workflow does not run evals. That remains the
current boundary.

CI-visible eval execution requires separate owner approval that names:

- workflow path
- trigger policy
- permissions
- command
- artifact policy
- failure semantics
- whether results are advisory or blocking

No CI eval integration is approved by this plan.

## 9. Quality-gate boundary

No `scripts/quality_gate.py` integration is approved by this plan.

The standalone eval gate wrapper remains separate:

- `scripts/gates/eval_gate.py`

Any future quality-gate integration must be separately approved and should
start, if approved, as an explicit opt-in mode before any default gate behavior.

## 10. Release-blocking boundary

No release-blocking eval behavior is approved by this plan.

An eval failure may be cited as evidence in a closeout, but it does not block
release publication unless a future release task explicitly approves that
policy. Release verification and artifact regeneration remain separate scopes.

## 11. Phase order

Recommended Phase 5 order:

1. Create this report-only integration plan.
2. Review receipt field alignment with `docs/AUDIT_TRACE_SCHEMA.md`.
3. Decide whether to add eval-specific optional receipt fields to the manual
   receipt schema.
4. Implement Phase 5A report-only split summary/cases outputs while preserving
   standalone behavior.
5. If approved later, add documentation examples for eval receipt summaries.
6. If approved later, consider opt-in quality-gate or CI behavior.

Do not skip from planning directly to default quality-gate, CI, or
release-blocking behavior.

## 12. Success criteria

Phase 5 planning succeeds when:

- eval runner remains standalone
- eval evidence can be summarized in receipt fields
- explicit/manual report generation remains the only report path
- no eval report is generated by default
- no quality-gate integration is added
- no CI eval integration is added
- no release-blocking behavior is added
- no LLM judge or external service is introduced
- no private raw data, prompt transcript, tool-call body, live value, or local
  absolute path is captured

## 13. Closeout requirements

Closeouts for eval/report integration tasks must report:

- final status label
- changed files
- whether eval runner behavior changed
- whether `scripts/quality_gate.py` changed
- whether evals ran
- eval receipt fields used or intentionally not used
- whether a report was generated
- report path, if explicitly generated
- quality-gate status
- CI status
- release-blocking status
- artifact regeneration status
- safety scan results
- unresolved risks
- next recommended task

If evals are not run, record `NOT RUN` with a reason. If an eval report is not
generated, record `eval_report_generation_status: not generated`.

## 14. Next task prompt

```text
Repository:
esj1123/codex-dev-harness

Task:
Implement the first report-only eval receipt alignment step.

Goal:
Use the Phase 5 eval/report integration plan to add or refine documentation
examples for summarizing standalone eval evidence in audit / trace / receipt
closeouts.

Read first:
- AGENTS.md
- STATUS.md
- docs/AUDIT_TRACE_SCHEMA.md
- docs/EVAL_REPORT_INTEGRATION_PLAN.md
- docs/EVAL_POLICY.md
- docs/VERIFICATION.md
- scripts/run_eval.py

Required boundaries:
- documentation-only unless separately approved
- eval runner remains standalone
- no scripts/quality_gate.py integration
- no CI eval integration
- no release-blocking eval behavior
- no routine eval report generation
- no artifact regeneration
- no LLM judge
- no external service
- no RAG, audit automation, MCP/Hermes, release automation, or downstream edit

Closeout:
- PASS / PASS WITH NOTES / BLOCKED
- changed files
- receipt field summary
- verification command results
- safety scan results
- whether report generation, push, tag, release, or artifact regeneration occurred
- next recommended task
```
