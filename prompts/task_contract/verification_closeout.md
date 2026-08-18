# Verification Closeout Prompt

Use this prompt to close out a completed task with evidence.

This template is documentation-only. It does not run verification or approve side effects by itself.

## Task Basis

- Goal: [task goal]
- Repository/path: [target path]
- Package location class: [same-root / external-local-control-plane]
- Basis ref or commit: [branch, tag, or commit]
- Work mode: [read-only, documentation-only, implementation, release record, other]
- Task ID and lane: [task ID] / [contract, feature, or integration]
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


## Verification Execution

- Target repository safe alias: [redacted safe alias; no absolute path]
- Harness SHA: [40-character commit SHA]
- Target base/head SHA: [base SHA] / [head SHA]
- Verification scope/executor: [focused / integration / extended] / [local / github]
- Exact-SHA binding: [BOUND / NOT BOUND / not applicable]
- Workflow name/run ID/conclusion: [name] / [safe run ID] / [PASS / FAIL / NOT RUN]
- Setup/pytest/overall duration: [seconds] / [seconds] / [seconds]
- Artifact upload status: [NOT RUN / NONE / TRANSIENT EXPORT]
- Local Full status: [PASS / FAIL / NOT RUN] - [reason when NOT RUN]
- Actual findings: [defects found or none]
- False positives/false negatives: [observed items or none known]
- Manual judgment points: [decisions requiring human review]
- Local/remote baseline state: [local HEAD, reviewed remote ref, workflow head equality]
- Residual risk: [remaining uncertainty]

## Changed Files

| file | change type | notes |
|---|---|---|
| [path] | ADDED / UPDATED / REMOVED | [summary] |

## Commands Run

| command | result | notes |
|---|---|---|
| [command] | PASS / FAIL / NOT RUN / ENVIRONMENT BLOCKED | [evidence or reason] |

## Evidence Paths

- [file or record path]
- [file or record path]

## Safety Checks

Confirm:

- allowed files only
- actual changed files remained within the declared write set
- actual untracked files remained within declared generated outputs
- work-package conflicts were checked before parallel execution
- preflight and postflight used the same `plan_digest`
- preflight and postflight used identical package bytes and package-root class
- exact verification runtime matched and every required command ID completed
- rename/delete and commit-count checks passed
- frozen contract paths were unchanged, or the batch stopped with `CONTRACT_CHANGE_REQUIRED`
- integration-only files were changed only by the integration lane
- structural PASS was not treated as authenticated approval
- no absolute repository, package-root, host, account, or runtime executable path was persisted in JSON evidence
- no unrelated refactor
- no secrets or private raw input
- no sensitive source text or live values
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

The default is `ADVISORY`. A `PASS`, `V2`, `V3`, postflight result,
`plan_digest`, or recommendation does not make a next step `ADOPTED` and does
not authenticate authorization.

Use `ADOPTED` only when the closeout records all of the following:

- explicit owner decision;
- exact adopted ref/SHA;
- adopted `STATUS.md` basis;
- required cumulative verification disposition;
- required digest disposition; and
- integration-owner disposition.

A closeout, recommendation, or branch-local `STATUS.md` cannot adopt itself.
The H01 closeout itself remains `PROPOSED / PENDING INTEGRATION` and its
next-step authority remains `ADVISORY`.

H01 does not add or infer separate Harness Hosted PASS and target Hosted PASS
fields. That field separation is reserved for the separately bounded H02 work.

## Next Step

[One concrete next step, or `None` if complete.]
