# Eval Report Integration Plan

## 1. Purpose

Plan Phase 5 eval/report integration against the audit / trace / receipt schema.

This plan defines how standalone eval evidence may be summarized in receipts
and, when explicitly approved, in manual report artifacts. It does not change
default eval runtime behavior, wire evals into `scripts/quality_gate.py`, make
evals release-blocking, or generate routine reports. A later owner decision
approves only console execution in the existing manual Local Verify workflow;
that command creates no report or other artifact.

## 2. Current eval baseline

Current eval status: standalone runner with manual Local Verify console
execution approved.

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

The existing `.github/workflows/local-verify.yml` invokes exactly
`python scripts/run_eval.py` without any report option.

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
- `workflow_run_id`, for an explicitly cited manual Local Verify run
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
- manual Local Verify may run the console-only command under its separately
  approved boundary
- no automatic-trigger, report-producing, or broader CI eval integration
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

Phase 5B implements eval receipt alignment / evidence closure:

- receipt summaries may cite explicitly generated split eval evidence without
  copying full case details into the receipt
- the eval summary JSON is safe summary evidence containing counts, pass/fail
  state, `cases_ref`, and `cases_sha256`
- the cases JSONL is detailed evidence and is referenced by repo-relative
  `cases_ref` plus the SHA-256 of the exact JSONL bytes
- receipts that cite split eval evidence should record the summary report path
  and SHA-256, plus `cases_ref` and `cases_sha256`
- eval remains standalone and reports remain explicit opt-in only

## 5. Eval receipt fields

When eval evidence is relevant, receipts should include:

| field | meaning |
|---|---|
| `eval_command` | Command or stable command label, such as `python scripts/run_eval.py`. |
| `eval_scope` | Case set or reason eval was scoped or not run. |
| `eval_case_count` | Total discovered or executed eval cases. |
| `eval_pass_count` | Passed case count. |
| `eval_fail_count` | Failed case count. |
| `eval_report_path` | Repo-relative report path, only if explicitly generated. |
| `eval_evidence` | Optional JSON receipt-summary object for Phase 5B eval evidence references; absent when eval evidence is not relevant. |
| `eval_evidence.summary_report_path` | Repo-relative split summary JSON path, only if explicitly generated and cited. |
| `eval_evidence.summary_report_sha256` | SHA-256 of the split summary JSON bytes, only if cited. |
| `eval_evidence.cases_ref` | Repo-relative cases JSONL path; should match the split summary report `cases_ref`. |
| `eval_evidence.cases_sha256` | SHA-256 of the cases JSONL bytes; should match the split summary report `cases_sha256`. |
| `eval_report_generation_status` | `not generated`, `generated`, `not run`, or `blocked`. |
| `eval_integration_status` | `standalone`, `receipt-summary-only`, `ci-approved`, or other approved state. |
| `eval_gate_status` | Quality-gate relationship, such as `not integrated`. |
| `release_blocking_status` | Release-blocking relationship, such as `not release-blocking`. |
| `notes_or_failures_summary` | Short safe summary of caveats or failed case names. |

These fields are receipt fields, not a new artifact format. They must remain
safe summaries and references; receipts must not copy the full cases JSONL rows.

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

Phase 5B receipt alignment treats the split summary report as the summary
evidence surface and the cases JSONL as detailed evidence. A receipt may cite
both by repo-relative path and SHA-256, but should not inline the per-case JSONL
records. The `cases_ref` and `cases_sha256` stored in a receipt should match
the values in the split summary report.

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

The later integration decision authorizes one narrow CI-visible use:

- workflow: `.github/workflows/local-verify.yml`
- trigger: manual `workflow_dispatch` only
- permissions: `contents: read`
- command: exactly `python scripts/run_eval.py`
- order: after pytest and before `python scripts/quality_gate.py`
- artifact policy: no report flags, artifact generation, or artifact upload
- failure semantics: a nonzero exit fails only that manual workflow run
- policy semantics: not a required check and not release-blocking

No automatic trigger, additional workflow, secret use, quality-gate
integration, report-producing CI execution, or release automation is approved.

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
5. Implement Phase 5B eval receipt alignment / evidence closure with optional
   receipt references to summary JSON and cases JSONL by repo-relative path and
   SHA-256.
6. If approved later, add example-only receipt snippets.
7. Record the later approval for manual console-only Local Verify execution
   while keeping quality-gate and broader CI behavior deferred.

Do not skip from planning directly to default quality-gate, CI, or
release-blocking behavior.

## 12. Success criteria

Phase 5 planning succeeds when:

- eval runner remains standalone
- eval evidence can be summarized in receipt fields
- explicit/manual report generation remains the only report path
- no eval report is generated by default
- no quality-gate integration is added
- CI-visible execution is limited to the exact manual console-only boundary
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
Review Phase 5B eval receipt alignment / evidence closure.

Goal:
Confirm receipt summaries can cite explicitly generated split eval evidence by
repo-relative path and SHA-256 without copying full cases JSONL details.

Read first:
- AGENTS.md
- STATUS.md
- docs/AUDIT_TRACE_SCHEMA.md
- docs/EVAL_REPORT_INTEGRATION_PLAN.md
- docs/EVAL_POLICY.md
- docs/VERIFICATION.md
- scripts/run_eval.py

Required boundaries:
- review/documentation-only unless separately approved
- eval runner remains standalone
- no scripts/quality_gate.py integration
- no CI eval integration beyond the exact approved manual console command
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
