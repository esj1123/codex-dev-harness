# Critic Review Prompt

Review a task, diff, design or repository state.

This documentation template authorizes no edits or side effects.

## Goal

Review [target] and report correctness, safety, scope, and evidence gaps.

## Target

- Repository/path: [target path]
- Basis ref or diff: [branch, commit, PR, or local diff]
- Relevant documents or files: [list]

## Review Mode

Review-only. Do not edit files unless a separate task explicitly approves changes.

Independent review inspects the actual change and required original evidence.
Coordination review starts from candidate, verification, independent-review and
authority linkage plus remaining decisions. Follow-up review covers corrected
findings and their impact; expand to relevant originals for mismatches, gaps,
stale candidates or new concerns. A compact summary preserves these checks.

## Correctness Review

Check:

- distinguish package/Codex task IDs and state/uncertainty
- for feature/artifact checks, goal and actual inputs/options/path agree; expectations
  come from requirements, templates or contracts, never output-matching adjustments
- representatives cover uncertain environment, call path or reproduction only
- validator/error tests accept known valid input, reject defects and trace production
  errors to the final result; label mock/actual scope; setters/messages alone are no flow PASS
- async/delegated work preselects a result location, binds ID/state, internal
  exit/core result/evidence, uses receipts for empty bodies, and readies candidate/refs
- after two evidence-based same-cause failures, diagnose with questions,
  evidence, and hypothesis; missing input/authority is not a reasoning gap
- recover missing output; shell success is no internal PASS; control only an
  owned process, since a shared environment proves nothing
- label unconfirmed execution `result not verified / NOT DONE`, not `NOT RUN`,
  `ENVIRONMENT BLOCKED`, or a new JSON enum; use statuses accurately
- historical records are not rewritten as current facts

## Safety Review

Check:

- no secrets, private raw input, sensitive source text, equipment details, live values, or credentials are introduced
- side-effect boundaries are explicit
- approval-gated actions remain approval-gated
- no live/device/runtime behavior is added without approval

## Scope Creep Review

Check:

- changed files match the allowed scope
- no unrelated refactor is included
- no new profile, example, CI workflow, eval harness, audit logging, RAG index, release artifact, or application/device code is added unless explicitly approved
- new reusable surface is justified by the task contract

## Missing Evidence Review

Check:

- verification commands were run or clearly marked NOT RUN / ENVIRONMENT BLOCKED
- list evidence; collisions get a new attempt, preserving receipts without
  regeneration or conversation copy
- update status/acceptance trace only for durable repo changes
- unresolved risks and assumptions are stated
- scale review to risk without weakening required or independent checks; repeat
  only for new failure, input, environment, contract or concern
- combine retries; collect usage only when requested

## Completion Report Format

1. Candidate/ref, scoped verdict and findings ordered by severity
2. Missing or weak evidence
3. Scope and safety assessment
4. Verification reviewed
5. Recommended next action
