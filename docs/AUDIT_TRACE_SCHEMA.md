# Audit Trace Schema

## 1. Purpose

Define the safe audit / trace / receipt schema for `codex-dev-harness` task
closeouts.

The schema is a documentation-level contract for future manual receipts and
future approval-gated automation. It records enough structured evidence to
support review of task outcome, repository state, verification, side effects,
approval boundaries, CI evidence, and next steps without storing raw private
content.

This document is schema-first. It does not create audit automation, write audit
entries, add a validator, install CI integration, generate artifacts, or change
runtime behavior.

## 2. Non-goals

This schema does not:

- create an audit logger
- write JSONL, Markdown, or database audit entries
- validate receipts in `scripts/quality_gate.py`
- integrate with CI, release verification, evals, RAG, MCP, or Hermes
- capture full prompt transcripts
- capture raw private input
- capture raw source bundles
- capture raw command logs by default
- capture unredacted tool-call request or response bodies
- capture generated downstream source
- authorize publication, tag movement, release creation, deployment, or live
  target actions

## 3. Receipt object overview

A receipt is a small structured closeout object for one task or phase. It should
be safe to read in repository-facing documentation, issue comments, pull request
summaries, or future audit records.

The receipt records:

- task identity
- repository and branch state
- changed file summary
- approval and side-effect class
- commands run and commands intentionally not run
- verification outcome
- safety exclusions
- local commit, push, tag, release, artifact, and CI evidence status
- unresolved risks
- next step

Receipts should prefer repo-relative paths, commit hashes, workflow run
identifiers, short summaries, and redacted status labels. A receipt should not
be a transcript.

## 4. Required fields

Every receipt must include:

| field | meaning |
|---|---|
| `task_id` | Stable task or phase identifier. |
| `repository` | Repository name, such as `owner/repo`. |
| `branch` | Current branch or detached reference. |
| `head_commit` | Local `HEAD` commit when available. |
| `origin_commit` | Remote comparison commit when available. |
| `local_remote_relationship` | Relationship between local branch and remote. |
| `changed_files` | Repo-relative changed files or an empty list. |
| `change_type` | Documentation, workflow, script, test, release, or other scoped type. |
| `approval_class` | Approval basis for the task. |
| `side_effect_class` | Side-effect class actually used. |
| `commands_run` | Commands run, with status labels and short notes. |
| `commands_not_run` | Commands intentionally not run, with reasons. |
| `verification_result` | Overall verification result. |
| `status_label` | One of the allowed status labels. |
| `safety_exclusions` | Explicitly excluded actions and content types. |
| `commit_hash` | Commit created by the task, or `null`. |
| `push_status` | Push state. |
| `tag_status` | Tag state. |
| `release_status` | Release publication state. |
| `artifact_upload_status` | Artifact upload state. |
| `unresolved_risks` | Residual risks, assumptions, or empty list. |
| `next_step` | Next recommended task or action. |

## 5. Optional fields

Optional fields may be added when relevant:

| field | meaning |
|---|---|
| `workflow_run_id` | CI or workflow run identifier. |
| `workflow_name` | CI or workflow name. |
| `workflow_trigger` | Trigger used, such as manual dispatch. |
| `workflow_conclusion` | CI conclusion. |
| `workflow_head_commit` | Commit used by the workflow run. |
| `job_summary` | Short per-job or per-step status summary. |
| `failed_step` | Failed step name when applicable. |
| `approval_id` | Pointer to a scoped approval record. |
| `receipt_schema_version` | Schema version for future compatibility. |
| `source_basis_commit` | Source basis commit for generated evidence. |
| `artifact_containing_commit` | Commit that contains generated artifacts. |
| `branch_ahead_count` | Local ahead count when checked. |
| `branch_behind_count` | Local behind count when checked. |
| `line_ending_notes` | LF/CRLF or related non-fatal hygiene notes. |
| `environment_notes` | Environment limitations, such as launcher failures. |
| `policy_only_scan_matches` | Sensitive-word matches that are policy text only. |
| `eval_command` | Eval command or stable eval command label, if eval evidence is relevant. |
| `eval_scope` | Eval case set or NOT RUN reason. |
| `eval_case_count` | Total eval case count when known. |
| `eval_pass_count` | Passed eval case count when known. |
| `eval_fail_count` | Failed eval case count when known. |
| `eval_report_path` | Repo-relative eval report path, only if explicitly generated. |
| `eval_report_generation_status` | Eval report generation state. |
| `eval_integration_status` | Eval integration state, such as standalone or receipt-summary-only. |
| `eval_gate_status` | Quality-gate relationship. |
| `release_blocking_status` | Release-blocking relationship. |
| `notes_or_failures_summary` | Short safe eval notes or failed case summary. |

Optional fields must follow the same redaction rules as required fields.

## 6. Forbidden fields

Receipts must not contain:

- full prompt transcripts
- raw private data
- raw source bundles
- sensitive source text
- secrets, tokens, keys, credentials, or account identifiers
- real IP values, port values, live config, device values, broker values, or
  account values
- unredacted tool-call request bodies
- unredacted tool-call response bodies
- raw command logs by default
- local Windows absolute paths
- generated downstream source
- external or private corpus material

If a future task requires evidence derived from sensitive material, the receipt
must use an approved identifier, hash, safe summary, or redacted status instead
of copying the material.

## 7. Redaction rules

Receipts must use these redaction rules:

- Use repo-relative paths.
- Use commit hashes, workflow run identifiers, and document names instead of
  copying raw content.
- Summarize command output; do not copy full logs by default.
- Record scan outcomes without copying matched sensitive values.
- Mark sensitive-word matches as policy-only only when no value, assignment, or
  live configuration is present.
- Use `NOT RUN` with a reason instead of implying success.
- Use `ENVIRONMENT BLOCKED` when a command cannot run because of local tool or
  platform state.
- Use `null`, `not applicable`, or `not checked` explicitly when a field has no
  value.
- Keep approval identifiers as pointers to records, not approval text dumps.

## 8. Status labels

Allowed `status_label` values are:

| label | meaning |
|---|---|
| `PASS` | Requested work completed and requested verification passed. |
| `PASS WITH NOTES` | Work completed, but material caveats remain. |
| `BLOCKED` | Work cannot safely proceed without owner input or external state change. |
| `NOT RUN` | A command or check was intentionally not executed. |
| `ENVIRONMENT BLOCKED` | A command or check could not run because of local environment state. |

For command-level results, the same labels may be used. A receipt may also use
`FAIL` for an executed check that failed, but the final task closeout should
map that failure to `PASS WITH NOTES` or `BLOCKED` according to the task
contract.

## 9. Git state fields

Git state fields should distinguish:

- `head_commit`: local `HEAD`
- `origin_commit`: remote comparison commit
- `local_remote_relationship`: `equal`, `ahead`, `behind`, `diverged`, or
  `unknown`
- `branch_ahead_count`: optional numeric count
- `branch_behind_count`: optional numeric count
- `changed_files`: repo-relative paths and status
- `commit_hash`: task-created commit, or `null`
- `push_status`: `not pushed`, `pushed`, `not applicable`, or `unknown`
- `tag_status`: `not created`, `created`, `not applicable`, or `unknown`
- `release_status`: `not published`, `published`, `not applicable`, or
  `unknown`

Local commit, remote push, tag creation, and release publication are separate
states. Do not collapse them into a single "done" state.

## 10. Verification fields

`commands_run` entries should include:

- command or stable command label
- status label
- short evidence note
- approved fallback, if used

`commands_not_run` entries should include:

- command or check label
- `NOT RUN`
- reason

`verification_result` should summarize the evidence without overstating it.
Release verification, artifact regeneration, CI execution, eval runs, and
downstream checks must be marked `NOT RUN` unless they were actually executed
within the approved task scope.

## 11. Side-effect and approval fields

`approval_class` should identify the approval basis, such as:

- `read_only`
- `documentation_only`
- `owner_approved_local_edit`
- `owner_approved_local_commit`
- `owner_approved_push`
- `owner_approved_workflow_dispatch`
- `release_publication_approved`
- `not_applicable`

`side_effect_class` should identify what happened, such as:

- `read_only_inspection`
- `documentation_edit`
- `local_git_commit`
- `remote_push`
- `manual_workflow_dispatch`
- `artifact_generation`
- `release_publication`
- `downstream_edit`
- `live_target_action`

The receipt may record a side effect only when it actually happened. Recording
an approval class or side-effect class does not grant approval for future
tasks.

## 12. CI/run evidence fields

When CI evidence is relevant, include:

- `workflow_name`
- `workflow_run_id`
- `workflow_trigger`
- `workflow_head_commit`
- `workflow_conclusion`
- `job_summary`
- `failed_step`
- `artifact_upload_status`

CI evidence must distinguish:

- workflow dispatch from push
- CI success from release publication
- artifact upload from no artifact upload
- read-only workflow permissions from broader permissions
- standard masked CI tokens from task-authored secret usage

If artifacts were not uploaded, record `artifact_upload_status: none`. If the
task did not check artifacts, record `artifact_upload_status: not checked`.

## 13. Future automation boundary

Future automation may use this schema only after a separate owner-approved
implementation task.

That future task must decide:

- storage format
- storage path
- schema versioning
- validator behavior
- quality-gate relationship
- CI relationship
- redaction implementation
- command-output retention policy
- prompt, private input, source, and tool-call exclusion rules

This schema does not approve audit log generation, receipt file creation,
schema validation scripts, CI integration, RAG integration, eval quality-gate
integration, MCP/Hermes implementation, release automation, or downstream
edits.

## 14. Example minimal receipt

```yaml
receipt_schema_version: "manual-v1"
task_id: "phase-04-audit-trace-schema"
repository: "esj1123/codex-dev-harness"
branch: "main"
head_commit: "<head-commit>"
origin_commit: "<origin-main-commit>"
local_remote_relationship: "equal"
changed_files:
  - path: "docs/AUDIT_TRACE_SCHEMA.md"
    status: "added"
change_type: "documentation-only"
approval_class: "documentation_only"
side_effect_class: "documentation_edit"
commands_run:
  - command: "git status --short --branch"
    status: "PASS"
    note: "working tree state recorded"
  - command: "python scripts/quality_gate.py"
    status: "ENVIRONMENT BLOCKED"
    note: "fallback runtime used"
commands_not_run:
  - command: "scripts/run_release_verify.ps1"
    status: "NOT RUN"
    reason: "release verification outside scope"
verification_result: "PASS WITH NOTES"
status_label: "PASS WITH NOTES"
safety_exclusions:
  - "no raw prompt transcript"
  - "no raw private data"
  - "no audit automation"
  - "no release artifact generation"
commit_hash: null
push_status: "not pushed"
tag_status: "not created"
release_status: "not published"
workflow_run_id: null
artifact_upload_status: "none"
unresolved_risks:
  - "future automation requires separate approval"
next_step: "eval/report integration planning"
```

The example is illustrative only. It does not create a receipt file or approve
automation.

## 15. Closeout requirements

Any task using this schema should close out with:

- final status label
- changed files
- schema or behavior summary
- forbidden capture boundaries
- command-by-command verification results
- safety scan results
- local commit status
- push status
- tag status
- release status
- artifact generation or upload status
- unresolved risks
- next recommended task

Closeouts must explicitly report when no commit, push, tag, release, artifact
generation, artifact upload, downstream edit, audit automation, RAG integration,
eval quality-gate integration, MCP/Hermes implementation, or live-write
behavior occurred.
