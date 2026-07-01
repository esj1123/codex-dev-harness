# Hermes Git Push Preflight Tracked Receipt Generation Contract

## Purpose

Record the Phase 9X contract for a future tracked Hermes git-push preflight
receipt generation task without generating that receipt.

Phase 9X is documentation and focused synthetic-test only. It does not create
`audits/receipts`, generate a receipt JSON file, write a trace event, create an
audit log, produce an artifact, persist preflight stdout, change
`scripts/hermes_git_push_preflight_receipt_writer.py`, change
`scripts/hermes_git_push_preflight_writer.py`, change receipt or trace schemas,
change `scripts/gates/json_evidence_gate.py`, edit workflows, wire quality-gate
or CI integration, run `git push` through Hermes, dispatch workflows through
Hermes, upload artifacts, execute MCP tools, publish releases, or edit
downstream repositories.

## Allowed Files

Phase 9X is limited to:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_CONTRACT.md`
- `tests/test_hermes_git_push_preflight_tracked_receipt_contract.py`

`STATUS.md`, `ACCEPTANCE_TRACE.md`, scripts, schemas, JSON gates, workflows,
artifacts, audits, evals, templates, profiles, examples, dependencies, and
downstream repositories are intentionally excluded from this contract task.

## Basis

This contract depends on:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_POLICY.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_SELECTED_RECEIPT_WRITER_IMPLEMENTATION_PLAN.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_PERSISTENCE_HOLD_DECISION.md`
- `audits/receipt-summary.schema.json`
- `scripts/hermes_git_push_preflight_receipt_writer.py`
- `tests/test_hermes_git_push_preflight_receipt_writer.py`

The clean Local Verify evidence for Phase 9W is run `28499585606`, job
`84473490892`, for commit `d48a6e311027ca21cbda44e206d95f6906787986`.

## Contract Decision

Decision: `tracked_receipt_generation_contract_documented_without_receipt_output`.

Phase 9X does not approve receipt generation by itself. It defines the exact
receipt id, output path, directory creation policy, source fixture policy,
schema validation procedure, redaction review, cleanup rule, retention rule, and
Local Verify evidence handling required before a later Phase 9Y task may leave a
tracked receipt in the repository.

The existing `selected_fields_receipt_writer` remains temporary-output only.
The future tracked receipt must be assembled by a separately approved task using
safe selected fields and the full receipt summary schema. Phase 9X does not
promote any writer into quality-gate, CI, MCP, audit, trace, release, or
downstream automation.

## Exact Future Receipt Target

The only Phase 9Y receipt target named by this contract is:

- receipt id: `phase-9y-hermes-git-push-preflight-tracked-receipt-synthetic-not-run`
- output path:
  `audits/receipts/hermes-git-push-preflight/phase-9y-hermes-git-push-preflight-tracked-receipt-synthetic-not-run.json`

The output path is repository-relative, has a `.json` suffix, is under
`audits/receipts/hermes-git-push-preflight/`, and must not include parent
traversal, local absolute path syntax, wildcard characters, raw/private/logs
segments, or secrets segments.

No alternate receipt id, alternate output path, batch output, generated folder,
trace path, audit log path, artifact path, or schema sidecar is approved by this
contract.

## Directory And Overwrite Policy

Phase 9X does not create any directory. A future Phase 9Y task may create only
this exact directory if the owner explicitly approves Phase 9Y:

- `audits/receipts/hermes-git-push-preflight`

The future task must not create any other directory under `audits`, `artifacts`,
`evals`, `templates`, `profiles`, `examples`, or downstream repositories.

The exact output path must not already exist before generation. If it exists,
Phase 9Y is `BLOCKED`; overwrite, replacement, append, merge, or in-place repair
is forbidden unless a separate owner approval names the exact existing file and
replacement rule.

## Retention And Cleanup Policy

If a future Phase 9Y task succeeds, the tracked receipt is retained as a normal
repository file until a separate approved task supersedes or removes it.

Every temporary candidate receipt must be written outside the repository first.
Temporary files must be deleted before closeout. If validation or redaction
fails after the approved receipt directory is created, the candidate receipt must
not be copied into the repository, and any empty directory created only for the
failed attempt must be removed before closeout.

If the tracked output is staged and a later check fails, the future task must
unstage it, delete the tracked output, remove any empty newly-created receipt
directory, and return `FAIL` or `BLOCKED`. Cleanup failure is `FAIL`.

## Source Fixture Contract

Phase 9Y must use synthetic selected-field fixtures only. Real
`scripts/hermes_git_push_preflight.py` stdout capture remains unapproved.

The only allowed selected-field fixture keys are the existing
`selected_fields_receipt_writer` keys:

- `preflight_evidence_status`
- `preflight_output_mode`
- `caller_schema_version`
- `caller_mode`
- `decision`
- `side_effect_requested`
- `guarded_command`
- `would_run_git_push`
- `performed_actions_empty`
- `reason_code`
- `stop_reasons`
- `approval_ref_present`
- `evidence_refs`
- `hermes_result_summary`
- `safe_task_summary`
- `safety_notes`
- `observed_head_commit`
- `local_verify_run_id`
- `local_verify_job_id`
- `output_capture`
- `preflight_integration_status`

Required selected-field values:

- `preflight_evidence_status`: `not_run`
- `preflight_output_mode`: `selected_fields`
- `caller_schema_version`: `hermes_git_push_preflight.v0`
- `caller_mode`: `dry_run`
- `decision`: `STOP`
- `side_effect_requested`: `git_push`
- `guarded_command`: `git push`
- `would_run_git_push`: `false`
- `performed_actions_empty`: `true`
- `reason_code`: `tracked_receipt_generation_contract_only`
- `approval_ref_present`: `true`
- `output_capture`: `selected_fields`
- `preflight_integration_status`: `receipt-summary-only`

Required selected-field references:

- `evidence_refs` must include
  `docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_POLICY.md`
- `evidence_refs` must include
  `docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_CONTRACT.md`
- `observed_head_commit` must be the committed head reviewed by the future
  Phase 9Y task, or `not checked` before commit review.
- `local_verify_run_id` and `local_verify_job_id` may cite prerequisite clean
  Local Verify evidence already known before receipt generation, or `not checked`
  before that evidence is reviewed.

The selected fixture must not include receipt top-level fields, trace top-level
fields, `receipt_id`, `task_id`, `receipt_path`, `trace_path`,
`audit_log_path`, `artifact_path`, raw stdout fields, command-log fields, prompt
fields, approval text, local absolute paths, private data, or downstream raw
evidence.

## Receipt Summary Contract

The future tracked file must be a full `receipt_summary` document conforming to
`audits/receipt-summary.schema.json`. It must not be only the
`hermes_git_push_preflight_evidence` object.

The top-level receipt fields must include:

- `schema_version`
- `evidence_kind`
- `receipt_id`
- `task_id`
- `repository`
- `basis`
- `approval`
- `side_effect_class`
- `changed_files`
- `commands`
- `verification`
- `safety`
- `artifacts`
- `status_label`
- `unresolved_risks`
- `next_step`

Required receipt-level values:

- `schema_version`: `1.0`
- `evidence_kind`: `receipt_summary`
- `receipt_id`: `phase-9y-hermes-git-push-preflight-tracked-receipt-synthetic-not-run`
- `repository`: `esj1123/codex-dev-harness`
- `approval.approval_class`: `owner_approved_local_commit`
- `approval.approval_reference`: safe reference only, not approval text
- `side_effect_class`: `documentation_edit`
- `artifacts.release_artifact_status`: `not generated`
- `artifacts.artifact_upload_status`: `none`
- `status_label`: `PASS`, `PASS WITH NOTES`, `BLOCKED`, `FAIL`, `NOT RUN`, or
  `ENVIRONMENT BLOCKED`

The optional `hermes_git_push_preflight_evidence` object may be embedded only
after `selected_fields_receipt_writer` validation succeeds against the selected
fixture contract.

## Local Verify Evidence Policy

The tracked receipt must not claim clean Local Verify for the same receipt
commit inside that same commit. That would create recursive evidence.

Phase 9Y may cite prerequisite evidence already available before generation,
such as Phase 9W run `28499585606`, job `84473490892`, and commit
`d48a6e311027ca21cbda44e206d95f6906787986`.

The Local Verify run for the Phase 9Y receipt commit must be recorded in the
Phase 9Y task closeout after push, not by editing the same tracked receipt in the
same implementation commit. A later evidence-refresh task would require a
separate approval if the repository owner wants the receipt file itself updated
with post-push Local Verify identifiers.

## Schema And Redaction Procedure

Phase 9Y must:

1. Write a candidate receipt to a temporary path outside the repository.
2. Validate deterministic JSON and a final newline.
3. Validate the full receipt against `audits/receipt-summary.schema.json`.
4. Validate the embedded `hermes_git_push_preflight_evidence` object through
   `selected_fields_receipt_writer`.
5. Run redaction review before copying into the repository.
6. Copy to the exact approved output path only after validation and redaction
   pass.
7. Confirm `git ls-files --others --exclude-standard` shows only the exact
   approved receipt path before staging.
8. Confirm `git diff --name-status` shows only the exact approved receipt path
   before staging.

The receipt must not include raw stdout, stderr, shell transcripts, command
logs, approval text, prompt text, prompt transcripts, tool-call bodies, model
output transcripts, tokens, account values, local absolute paths, IPs, ports,
endpoints, live config, device values, private data, raw `08_Study`, RSID raw
evidence, downstream raw evidence, generated downstream source, raw logs, or
secrets.

## Phase 9Y Verification Gate

A future Phase 9Y generation task must run at least:

- `python -m pytest tests/test_hermes_git_push_preflight_tracked_receipt_contract.py`
- `python -m pytest tests/test_hermes_git_push_preflight_tracked_receipt_policy.py`
- `python -m pytest tests/test_hermes_git_push_preflight_receipt_writer.py`
- `python -m pytest tests/test_json_evidence_gate.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `git diff --check`
- `git ls-files --others --exclude-standard`

After commit and push, the existing read-only Local Verify workflow must pass
for the receipt commit. Expected artifact upload status is `none`.

## Failure Modes

Future generation must use explicit statuses:

- `PASS`
- `PASS WITH NOTES`
- `BLOCKED`
- `FAIL`
- `NOT RUN`
- `ENVIRONMENT BLOCKED`

Missing exact owner approval, missing exact path, missing directory approval,
attempted overwrite, unexpected untracked files, schema validation failure,
selected-field validation failure, redaction failure, recursive Local Verify
claim, artifact upload drift, downstream access, and cleanup failure are not
silent success.

## Non-goals

Phase 9X does not:

- generate a receipt file;
- create `audits/receipts`;
- change `scripts/hermes_git_push_preflight_receipt_writer.py`;
- change `scripts/hermes_git_push_preflight_writer.py`;
- change `scripts/hermes_git_push_preflight.py`;
- change receipt or trace schemas;
- change `scripts/gates/json_evidence_gate.py`;
- write or generate trace files, audit logs, preflight artifacts, release
  artifacts, or downstream evidence;
- connect Hermes preflight output to `scripts/quality_gate.py`, CI, MCP, audit
  automation, release automation, AgentOps, memory, external services, or
  downstream repositories;
- run real `git push`, `git add`, `git commit`, `git tag`, release publication,
  workflow dispatch, artifact upload, MCP execution, external calls, audit
  generation, receipt generation, trace writing, or downstream mutation through
  Hermes.

## Next Step

After Phase 9X is committed and clean Local Verify passes, the next safe Hermes
step should be either:

- pause before any generated receipt, trace, audit, CI, MCP, runtime, or
  downstream persistence; or
- a separately approved Phase 9Y tracked receipt synthetic generation task using
  the exact receipt id, exact output path, directory policy, overwrite policy,
  selected-field fixture contract, schema validation procedure, redaction
  procedure, cleanup rule, retention rule, and Local Verify closeout policy from
  this contract.

Phase 9X does not authorize Phase 9Y by itself.
