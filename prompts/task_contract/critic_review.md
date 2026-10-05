# Critic Review Prompt

Review the requested task, document, diff, design, or repository state. Select
checks that affect that judgment; a document or explanation does not by itself
require executable tests, a work package, or a new evidence file. Required
independent review and governing project/global rules still apply.

This documentation template authorizes no edits or side effects.

## Goal

Review [target] and report correctness, safety, scope, and evidence gaps.

## Target

- Repository/path: [target path]
- Basis ref or diff: [branch, commit, PR, or local diff]
- Reviewed object/phase: [object, phase and exact ref covered by this review]
- Remaining coverage: [unreviewed next inputs/commands or acceptance steps; required evidence]
- Relevant documents or files: [list]

## Review Mode

Review-only. Do not edit files unless a separate task explicitly approves changes.

Independent review inspects the actual change and required original evidence.
Coordination review starts from candidate, verification, independent-review and
authority linkage plus remaining decisions. Follow-up review covers corrected
findings and their impact; expand to relevant originals for mismatches, gaps,
stale candidates or new concerns. A compact summary preserves these checks.

## Correctness Review

Check that the result addresses the user's request, uses the relevant sources
and existing format, and distinguishes evidence from assumptions. For document
work, inspect content, format, decisions, and open items; flag unrequested
authoring-system work. Missing tests are a finding only when the affected
behavior or applicable policy requires them.

- historical records are not rewritten as current facts
- each claimed blocker is required by this task's phase/acceptance conditions;
  later finalization and broader aggregate completion are reported separately
- the latest explicit scoped user/owner decision and retained interim limits
  are checked before repeating an approval question or execution; preserve the
  old record and decision evidence, with absent or different-scope approval
  still unapproved/unclear
- missing required approval, UNKNOWN required gates and candidate/evidence
  mismatches remain unresolved despite future/deferred labels; mechanical
  consistency and scoped acceptance are separate results
- bind each verdict to its reviewed object/phase; a code hash/reference does not
  establish review of a later execution input/command, and plan or qualification
  review does not establish candidate or publication acceptance

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
- when measurement is requested, check the named owner, actual milestone records,
  participant/phase coverage from coordination through implementation, review,
  fix and handoff, and source/key/cutoff and interval-versus-cumulative accounting
  from `verification_closeout.md`; include all retries, routing settings and
  mismatches, first-pass quality, defects/rework, and unexplained discrepancies

## Completion Report Format

1. Answer or scoped verdict, reviewed object/phase, and material findings
2. Missing required evidence, checks reviewed, and remaining decision or next action
3. Routing defects separately, when applicable

## Execution And Code Review

Use these checks for affected code, validators, package coordination, or executions.
They do not create an execution requirement for an inspection or document task.

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

## Routing Review

Apply the inherited model-routing policy where required. Report defects or
missing required evidence without repeating unchanged routing records.

Check the task contract's dispatch metadata against original runtime evidence:

- requested and actual model/reasoning effort are both recorded, with unavailable
  actual evidence marked unverified rather than inferred from self-report
- role, model, effort and one-line reason fit the task under the global `AGENTS.md`
  model-routing policy, including any task-specific exception reason
- a resumed same-role/same-scope choice was preserved unless an authorized,
  supported change was deliberate
- mismatches were recorded and corrected at the next safe boundary before scope
  expanded, while useful prior output/tests were preserved and no rerun merely
  relabeled earlier work
- permission or environment blocks received the actual remedy rather than a model
  escalation

Report routing defects separately from product, implementation and evidence findings.
