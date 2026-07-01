# Hermes Git Push Preflight Tracked Receipt Generation Policy

## Purpose

Record the Phase 9W policy boundary for any future tracked Hermes git-push
preflight receipt generation.

Phase 9W is documentation and focused synthetic-test only. It does not generate
a tracked receipt, write a trace event, create an audit log, produce an
artifact, persist preflight stdout, change `scripts/hermes_git_push_preflight_receipt_writer.py`,
change `scripts/hermes_git_push_preflight_writer.py`, change receipt or trace
schemas, change `scripts/gates/json_evidence_gate.py`, edit workflows, wire
quality-gate or CI integration, run `git push` through Hermes, dispatch
workflows through Hermes, upload artifacts, execute MCP tools, publish releases,
or edit downstream repositories.

## Allowed Files

Phase 9W is limited to:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_TRACKED_RECEIPT_GENERATION_POLICY.md`
- `tests/test_hermes_git_push_preflight_tracked_receipt_policy.py`

`STATUS.md`, `ACCEPTANCE_TRACE.md`, scripts, schemas, JSON gates, workflows,
artifacts, audits, evals, templates, profiles, examples, dependencies, and
downstream repositories are intentionally excluded from this policy task.

## Basis

This policy depends on:

- `docs/HERMES_GIT_PUSH_PREFLIGHT_DURABLE_WRITER_PROPOSAL.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_SELECTED_RECEIPT_WRITER_IMPLEMENTATION_PLAN.md`
- `docs/HERMES_GIT_PUSH_PREFLIGHT_WRITER_PERSISTENCE_HOLD_DECISION.md`
- `audits/receipt-summary.schema.json`
- `scripts/hermes_git_push_preflight_receipt_writer.py`
- `tests/test_hermes_git_push_preflight_receipt_writer.py`

The clean Local Verify evidence for Phase 9V.1 is run `28498555756`, job
`84470173481`, for commit `31ee09d7db6bbe7ea079a6cc90a31b6029a19089`.

## Policy Decision

Decision: `tracked_receipt_generation_policy_documented_without_receipt_output`.

Phase 9W does not approve tracked receipt generation. It only defines the
approval, path, content, source, redaction, cleanup, and verification
requirements that a later task must satisfy before any generated receipt remains
in the repository.

The existing `selected_fields_receipt_writer` remains temporary-output only.
The existing `not_run_record_only` writer remains separate. Phase 9W does not
promote either writer into durable receipt, trace, audit, quality-gate, CI, MCP,
release, or downstream automation.

## Proposed Receipt Location Policy

A future tracked-receipt task may propose this repository-relative path pattern:

- `audits/receipts/hermes-git-push-preflight/<receipt_id>.json`

Phase 9W does not create `audits/receipts`, does not create
`audits/receipts/hermes-git-push-preflight`, and does not create any receipt
JSON file. The path pattern is a policy placeholder only.

A later task must name one exact repo-relative output path under
`audits/receipts/hermes-git-push-preflight/`, with a `.json` suffix, no parent
traversal, no local absolute path, no raw/private/log/secrets segment, and no
wildcard path. Existing output overwrite is forbidden unless a separate owner
approval names the exact existing file and replacement rule.

The later task must also state whether the receipt directory may be created. If
directory creation is not explicitly approved, generation is `BLOCKED`.

## Future Approval Requirements

Before any tracked receipt generation is allowed, a future task must explicitly
define:

- exact receipt id;
- exact repo-relative output path;
- whether the receipt directory may be created;
- overwrite policy;
- retention policy;
- cleanup/reversion policy;
- source fixture policy and selected fields;
- schema validation procedure;
- redaction review;
- owner approval evidence as a boolean or safe reference, not approval text;
- Local Verify run, job, and checked-out head commit requirements;
- artifact upload policy, expected to be `none` unless separately approved;
- staging, commit, push, and Local Verify closeout workflow;
- no downstream access.

If any required item is absent, tracked receipt generation is `BLOCKED`.

## Receipt Content Policy

A tracked receipt must be a full `receipt_summary` document that conforms to
`audits/receipt-summary.schema.json`, not the
`hermes_git_push_preflight_evidence` object alone.

The full receipt must include the schema-required top-level fields:

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

The optional `hermes_git_push_preflight_evidence` object may be included only
after selected fields are reviewed as safe and bounded. It must not replace the
full receipt summary.

## Source And Redaction Policy

Tracked receipt generation must use synthetic selected-field fixtures until a
future task separately names a reviewed source and redaction procedure. Real
`scripts/hermes_git_push_preflight.py` stdout capture remains unapproved.

The receipt must not include raw stdout, stderr, shell transcripts, command
logs, approval text, prompt text, prompt transcripts, tool-call bodies, model
output transcripts, tokens, account values, local absolute paths, IPs, ports,
endpoints, live config, device values, private data, raw `08_Study`, RSID raw
evidence, downstream raw evidence, generated downstream source, raw logs, or
secrets.

Approval may be represented only by safe summary fields, a boolean, or a safe
owner-approved reference. Approval conversation text must not be stored.

## Generation Workflow

A future generation task must fail closed:

1. Build any candidate receipt to a temporary path outside the repository first.
2. Validate deterministic JSON, sorted keys where practical, and final newline.
3. Validate against `audits/receipt-summary.schema.json`.
4. Run redaction review before repository copy.
5. Copy to the exact approved tracked path only after path, schema, redaction,
   overwrite, retention, and cleanup conditions pass.
6. Confirm `git ls-files --others --exclude-standard` shows only the explicitly
   approved receipt path before staging.
7. Confirm `git diff --name-status` shows only the explicitly approved receipt
   path before staging.
8. Keep artifact upload status `none` unless a separate task approves artifact
   upload by exact workflow and artifact name.

Missing cleanup, missing schema validation, missing redaction review, unexpected
untracked files, attempted overwrite, or any path outside the approved pattern is
`FAIL` or `BLOCKED`.

## Failure Modes

Future receipt-generation tooling and closeout must use explicit statuses:

- `PASS`
- `PASS WITH NOTES`
- `BLOCKED`
- `FAIL`
- `NOT RUN`
- `ENVIRONMENT BLOCKED`

Validation failure, forbidden fields, unsafe text, unexpected schema shape,
missing cleanup, attempted overwrite, repository-internal temporary output,
missing Local Verify evidence, missing owner approval, artifact upload drift,
and downstream access are not silent success.

## Verification

Phase 9W verification must include at least:

- `python -m pytest tests/test_hermes_git_push_preflight_tracked_receipt_policy.py`
- `python -m pytest tests/test_hermes_git_push_preflight_receipt_writer.py`
- `python -m pytest tests/test_json_evidence_gate.py`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- `git diff --check`
- `git ls-files --others --exclude-standard`

Clean GitHub Actions Local Verify evidence should be recorded separately after
this policy is committed and pushed.

## Non-goals

Phase 9W does not:

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

After Phase 9W is committed and clean Local Verify passes, the next safe Hermes
step should be either:

- pause before any generated receipt, trace, audit, CI, MCP, runtime, or
  downstream persistence; or
- a separately approved Phase 9X tracked receipt-generation contract that names
  the exact receipt id, exact output path, directory creation policy, source
  fixture policy, schema validation procedure, redaction review, cleanup rule,
  retention rule, and Local Verify evidence requirements.

Phase 9W does not authorize Phase 9X by itself.
