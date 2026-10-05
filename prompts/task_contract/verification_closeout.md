# Verification Closeout Prompt

Lead with the requested result, changes, checks and their scope, and remaining
decisions. Use only applicable sections; do not print empty package, Hosted,
routing, or measurement rows for unselected workflows. Create a separate receipt
file only when the task or governing policy requires one. Required checks and
inherited global instructions still apply.

This documentation template runs nothing and approves no side effects.

Judge the current task against its declared phase and acceptance conditions.
Before requesting reapproval or rerun, check whether the latest explicit
user/owner decision applies to the same target, action and scope; retain its
evidence and the earlier record. A broader aggregate `completion=false`, past
status label or mechanical next-action code alone does not establish a current
blocker. Keep later finalization separate unless it is required for current
acceptance. Missing required approval, UNKNOWN required gates and candidate/
evidence mismatches remain unresolved; calling them future/deferred cannot
make them PASS. The reader's approval status and completion calculation stay
unchanged.

## Task Basis

- Goal: [task goal]
- Completion/decision basis: [conditions/status; uncertainty; reused evidence]
- Current task verdict/blockers: [phase and scoped result; unmet required conditions,
  or none; link each blocker to the acceptance condition]
- Applicable owner decision: [latest explicit decision and same-scope evidence;
  retained interim decisions/limits; none or unverified if unavailable]
- Later finalization: [open items, phase/owner and dependency on current acceptance]

## Changed Files

| file | change type | notes |
|---|---|---|
| [path] | ADDED / UPDATED / REMOVED | [summary] |

## Commands Run

Use this section for checks actually selected; document content checks may be
reported in prose without inventing executable commands.

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
- no unrelated refactor
- no secrets, private raw input, sensitive source text or live values
- no new profile, example, CI workflow, eval code, audit logging code, RAG code, release artifact, application code, device code, or live-write behavior unless explicitly approved
- side effects were not performed without approval
- `performed_actions` and actual commands agree with the closeout

## Unresolved Risks

- [risk or assumption]
- [risk or assumption]

## Closeout Result

Use a formal verdict when requested or required by the active contract.

Choose one:

- PASS
- PARTIAL
- BLOCKED
- NEEDS OWNER DECISION

## Next Step

[One next step, or `None`.] In scoped measurement, mark unmeasured tokens `NOT
MEASURED`; do not estimate savings. Stop at completion; cleanup is separate.

## Conditional Details

Use the following only for the selected package, execution, evidence-reader,
measurement, or adoption scope. Preserve every field required by that contract;
omitting unselected sections does not waive required evidence.

## Package And Workflow Basis

- Mechanical consistency: [candidate/input/receipt linkage result and aggregate
  selection scope; preserve reported completion and reason codes]
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

Apply each field only to the selected execution. Hosted, timing, and utility
fields do not make those activities prerequisites for ordinary document work.

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

When evaluation is requested, keep selected quality and usage measures in this closeout; link original evidence instead
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
For reused verification, link its original result and state the matching
candidate/input identities, command/runtime basis and acceptance scope.
Recheck affected dependencies when they change; never inherit PASS across a
different execution input or omit the cumulative checks required by policy.

If target-repository Hosted evidence was not executed and bound to the target
head SHA, record Target Hosted status/run as `NOT RUN`; do not inherit the
Harness result. Harness Hosted PASS does not establish target-repository Hosted
PASS.

## Package Safety Checks

For work using a package, confirm:

- untracked files stayed within declared generated outputs
- work-package conflicts were checked before parallel execution
- preflight/postflight used identical package bytes and package-root class, and the same `plan_digest`
- exact verification runtime matched and every required command ID completed
- rename/delete and commit-count checks passed
- frozen paths unchanged, else stop with `CONTRACT_CHANGE_REQUIRED`
- only integration lane changed integration-only files
- structural PASS was not treated as authenticated approval
- no absolute repository, package-root, host, account or runtime paths in JSON evidence

## Optional Evidence Reader

When the task contract selects closeout mechanization, use the existing
postflight's `--task-evidence-spec` hook with the start-declared input/runtime
roots. The hook reads only fixed inputs and supplies selected state,
candidate/receipt consistency and superseded claims. Use `runtime: []` and
omit the runtime root unless usage evaluation was explicitly selected; missing
usage is not a state/evidence or task-completion failure. Lead with the concise
decision output and retain process exit, spec/state SHA, scope and reason codes
in the existing task record. Link detailed JSON for mismatches or follow-up
inspection instead of repeatedly returning the entire result.
Target completion and mechanical consistency are separate results. Keep past
unresolved observations visible without silently changing them to PASS. The
target owner declares which gates are required for this task's acceptance;
the reader does not grant approval or decide that historical risks can be ignored.
For selected usage evaluation only, retain prefix SHA, cutoff and coverage;
do not repeat manual full-log selection or counter subtraction.
Call counts and app durations remain
UNKNOWN unless independent original evidence supplies them. Never treat
token events, usage timestamp spans or selected bytes as calls, active labor
or token savings. See
[Bounded closeout state and usage](../../docs/LOCAL_USAGE.md#bounded-closeout-state-and-usage).

For the two standalone Harness checkers, apply the sole caller example in
[Standalone checker JSON results](../../docs/LOCAL_USAGE.md#standalone-checker-json-results)
and lead their evidence with actual and reported exits, the checked JSON decision
and raw stdout/stderr references. Expand original source or output for gaps,
failures, contradictions or staleness. The task and impact policy still select
the required verification tier and independent review.

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
Historical H01/H02 note, relevant only when those records are referenced:
The H01 closeout itself remains `PROPOSED / PENDING INTEGRATION` and its
next-step authority remains `ADVISORY`.

H02 fields preserve H01 authority; they adopt neither H01, the verification UX
basis nor any next step.
