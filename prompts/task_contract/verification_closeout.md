# Verification Closeout Prompt

Use to close a completed task with evidence.

This documentation template runs nothing and approves no side effects.

Lead with the candidate, changed behavior, verification scope/result, unresolved
items, next action and evidence locations. Link detailed logs and unchanged
records while retaining the required basis and safety fields below.

## Task Basis

- Goal: [task goal]
- Completion/decision basis: [conditions/status; uncertainty; reused evidence]
- Repository/path: [target path]
- Package location class: [same-root / external-local-control-plane]
- Basis ref or commit: [branch, tag, or commit]
- Work mode: [read-only, documentation-only, implementation, release record, other]
- Package task ID/lane: [package `task_id`] / [contract, feature, or integration]
- Codex task ID/state: [actual task ID] / [complete, blocked, or needs owner decision]
- Contract basis SHA: [40-character commit SHA]
- Contract frozen paths: [shared exact repo-relative paths]
- Declared verification tier: [V0 / V1 / V2 / V3]
- Verification runtime ID: [safe interpreter identity]
- Required/completed command IDs: [IDs only; no raw logs]
- Dependencies satisfied: [yes / no / not applicable]
- Plan digest: [SHA-256 from work-package preflight, or not applicable]
- Postflight status: [PASS / BLOCKED / FAIL / ENVIRONMENT BLOCKED / not applicable]
- Authorization status: [NOT_AUTHENTICATED plus separate approval evidence]
- Next-step authority: [ADVISORY / ADOPTED] (default: `ADVISORY`)
- Dispatch role: [coordination / retrieval / implementation / verification / review / integration]
- Requested model/reasoning effort/task-fit reason: [exact model] / [exact effort] / [one line]
- Actual model/reasoning effort and evidence: [original runtime evidence at start, resumption or settings change; otherwise unverified]
- Routing mismatch disposition: [none / corrected at safe boundary / unresolved, with preserved useful output/tests]


## Verification Execution

- Target repository safe alias: [redacted safe alias; no absolute path]
- Workflow repository identity: [safe owner/repository identity; no credentials]
- Harness workflow SHA: [40-character commit SHA]
- Harness Hosted executor/status/run: [github / PASS / FAIL / NOT RUN] / [workflow name and safe run ID]
- Target base/head SHA: [base SHA] / [head SHA]
- Target verification executor/status: [local / github] / [PASS / FAIL / NOT RUN / ENVIRONMENT BLOCKED]
- Target Hosted status/run: [PASS / FAIL / NOT RUN] / [workflow name and safe run ID, or reason]
- Verification scope: [focused / integration / extended]
- Reviewed coverage: [object/phase/ref and scoped verdict; unreviewed next inputs/commands or acceptance steps]
- Exact-SHA binding: [BOUND / NOT BOUND / not applicable]
- Setup/pytest/overall duration: [seconds] / [seconds] / [seconds]
- Artifact upload status: [NOT RUN / NONE / TRANSIENT EXPORT]
- Local Full status: [PASS / FAIL / NOT RUN] - [reason when NOT RUN]
- Actual findings: [defects found or none]
- False positives/false negatives: [observed items or none known]
- Manual judgment points: [decisions requiring human review]
- Local/remote baseline state: [local HEAD, reviewed remote ref, workflow head equality]
- Residual risk: [remaining uncertainty]
- Recovery/diagnosis/control, if applicable: [same-cause diagnosis; ownership;
  preselected async result location; ID/state/internal exit/core result/evidence
  or empty-body receipt; candidate/refs]
- Utility measurement, if scoped: [owner and existing milestone records;
  first-pass result and quality by stage, defects/rework/interventions;
  participant/phase coverage including coordination, implementation, review, fix
  and handoff, with requested/actual routing and mismatch disposition;
  input/cached-input/output tokens, calls, time, cutoff and gaps;
  otherwise NOT REQUESTED]

Keep scoped quality and usage in this closeout; link original evidence instead
of copying logs. Identify the original usage source, unique event key, participant/
phase coverage and cutoff. Sum non-overlapping response usage once, or use explicit
cumulative deltas for the same counter and non-overlapping coverage; never add
cumulative snapshots as increments or mix both methods over the same usage.
Cached input and reasoning output are subsets, not additional totals. Preserve
unexplained discrepancies and mark missing or later coverage as unmeasured; carry
it to the next actual milestone without inventing a measurement-only step.
Make no savings claim or savings percentage without a defined comparator; expected
reductions in rework or total token use remain hypotheses to observe. Do not create
measurement-only cases, systems or model-occupancy tasks.

Bind each verdict to the reviewed object/phase. Plan/code review or hash/reference
linkage does not establish review of a later execution input/command or required
acceptance. Keep remaining review, evidence and authority visible in Next Step.

If target-repository Hosted evidence was not executed and bound to the target
head SHA, record Target Hosted status/run as `NOT RUN`; do not inherit the
Harness result. Harness Hosted PASS does not establish target-repository Hosted
PASS.

## Changed Files

| file | change type | notes |
|---|---|---|
| [path] | ADDED / UPDATED / REMOVED | [summary] |

## Commands Run

| command / owned execution ID | result / internal exit | core result or evidence |
|---|---|---|
| [command / ID] | PASS / FAIL / NOT RUN / ENVIRONMENT BLOCKED / [exit] | [result or reason] |

Recover execution before rerun; missing output alone is no rerun reason and
shell success is no internal PASS. An unconfirmed execution is human `result
not verified / NOT DONE`, not a new JSON enum, `NOT RUN`, or `ENVIRONMENT BLOCKED`.

## Evidence Paths

- [file or record path]
- [file or record path]

Reference unchanged receipts. On collision use a new attempt; avoid ritual
deletion/regeneration and transcript copies.

For feature/artifact checks, link goal, actual inputs/options/path and contract-
derived expectations. For validator/error-test changes, report known valid
acceptance, defect rejection and production error-to-final-result flow, with mock scope.

## Safety Checks

Confirm:

- actual changed files remained within the declared write set
- untracked files stayed within declared generated outputs
- work-package conflicts were checked before parallel execution
- preflight/postflight used identical package bytes and package-root class, and the same `plan_digest`
- exact verification runtime matched and every required command ID completed
- rename/delete and commit-count checks passed
- frozen paths unchanged, else stop with `CONTRACT_CHANGE_REQUIRED`
- only integration lane changed integration-only files
- structural PASS was not treated as authenticated approval
- no absolute repository, package-root, host, account or runtime paths in JSON evidence
- no unrelated refactor
- no secrets, private raw input, sensitive source text or live values
- no new profile, example, CI workflow, eval code, audit logging code, RAG code, release artifact, application code, device code, or live-write behavior unless explicitly approved
- side effects were not performed without approval
- `performed_actions` and actual commands agree with the closeout

## Unresolved Risks

- [risk or assumption]
- [risk or assumption]

## Closeout Result

Choose one:

- PASS
- PARTIAL
- BLOCKED
- NEEDS OWNER DECISION

## Next-Step Authority

Default is `ADVISORY`; `PASS`, `V2`, `V3`, postflight result, `plan_digest`, or a
recommendation neither adopts a next step nor authenticates authorization.

`ADOPTED` requires recorded:

- explicit owner decision;
- exact adopted ref/SHA;
- adopted `STATUS.md` basis;
- required cumulative verification disposition;
- required digest disposition; and
- integration-owner disposition.

A closeout, recommendation or branch-local `STATUS.md` cannot adopt itself.
The H01 closeout itself remains `PROPOSED / PENDING INTEGRATION` and its
next-step authority remains `ADVISORY`.

H02 fields preserve H01 authority; they adopt neither H01, the verification UX
basis nor any next step.

## Next Step

[One next step, or `None`.] In scoped measurement, mark unmeasured tokens `NOT
MEASURED`; do not estimate savings. Stop at completion; cleanup is separate.
