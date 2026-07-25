# Verification Closeout Prompt

Use this prompt to close out a completed task with evidence.

This template is documentation-only. It does not run verification or approve side effects by itself.

## Task Basis

- Goal: [task goal]
- Repository/path: [target path]
- Basis ref or commit: [branch, tag, or commit]
- Work mode: [read-only, documentation-only, implementation, release record, other]
- Task ID and lane: [task ID] / [contract, feature, or integration]
- Declared verification tier: [V0 / V1 / V2 / V3]
- Dependencies satisfied: [yes / no / not applicable]

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
- work-package conflicts were checked before parallel execution
- integration-only files were changed only by the integration lane
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

## Next Step

[One concrete next step, or `None` if complete.]
