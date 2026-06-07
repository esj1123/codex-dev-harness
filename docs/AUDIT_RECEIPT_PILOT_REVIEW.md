# Audit Receipt Pilot Review

## 1. Purpose

Review whether recent task closeouts are consistent enough for the current
local-first `codex-dev-harness` baseline, and decide whether an audit receipt
pilot or audit automation is justified.

This review is documentation-only. It does not create audit automation,
JSONL logging, scripts, CI integration, RAG/index/retrieval tooling, MCP or
runtime-agent changes, release artifacts, tags, pushes, downstream edits, or
private raw data records.

## 2. Source basis

Primary source basis:

- `AGENTS.md`
- `STATUS.md`
- `docs/PROMPT_PATTERNS.md`
- `docs/SIMPLIFICATION_CHECKLIST.md`
- `docs/OPTIONAL_RAG_PILOT_DECISION.md`
- `docs/AUDIT_LOG_POLICY.md`
- `docs/CHANGE_CONTROL.md`
- `docs/HUMAN_APPROVALS.md`
- `prompts/task_contract/verification_closeout.md`

Recent local context:

- the committed optional RAG pilot decision record
- current-thread closeout summaries from the optional RAG decision work
- recent commit history showing the local RAG decision commit on `main`

This review uses only summarized closeout observations. It does not copy raw
tool output, private input, downstream source, live configuration, or local
absolute paths into the repository record.

## 3. Recent receipt friction

Recent closeouts were useful, but showed small recurring friction:

- repo-facing links can accidentally expose local absolute path shape when a
  relative repository path would be safer
- untracked, intent-to-add, staged, committed, and clean states need distinct
  wording
- `PASS` and `PASS WITH NOTES` are sometimes close enough that the note reason
  must be explicit
- verification command limitations, warnings, or approval-required command
  reruns need to be separated from verification failure
- no-push evidence should distinguish local branch-ahead status from remote
  publication

These are review-quality issues, not evidence that an audit logger is needed.

## 4. Receipt consistency findings

Current closeout practice is consistent enough for manual operation.

The strongest current patterns are:

- closeouts name outcome, changed files, verification, safety exclusions, and
  next step
- task contracts usually state allowed files and forbidden actions before work
- no-push, no-tag, no-release, no-artifact, and no-automation exclusions are
  usually reported when relevant
- `NOT RUN` is generally reported when release verification or broader checks
  are intentionally excluded

The main weakness is wording precision, not missing evidence. Reviewers need a
small checklist for state labels, command limitations, and scope exclusions.
That is lighter and safer than adding audit automation now.

## 5. Required closeout fields

Manual closeouts should include:

- result: `PASS`, `PASS WITH NOTES`, `BLOCKED`, or another task-specified
  result
- changed files or artifacts, using repo-relative paths where possible
- decision or behavior summary
- verification commands run, with result and material notes
- commands intentionally not run, with `NOT RUN` reason
- git state when git state is relevant
- safety exclusions, especially no push, no tag, no release, no artifacts, no
  CI, no audit automation, no RAG implementation, and no downstream edits
- unresolved risks or assumptions
- next step

For commit tasks, also include the commit hash and whether the branch is only
locally ahead or has been pushed.

## 6. Risky wording patterns

Avoid these patterns:

- saying "clean" when the file is only intent-to-add, staged, or committed but
  branch state has not been checked
- saying "only file changed" without distinguishing untracked files from
  modified tracked files
- saying "verification passed" when a command emitted a material warning or had
  to be rerun with approval
- implying an approval was created by a decision, closeout, or template
- treating local branch-ahead status as a push
- treating absence of matches in a narrow scan as proof that all private data is
  absent
- copying matched sensitive values, local absolute paths, or raw command output
  into repo-facing text
- using "not needed" where the accurate status is `NOT RUN` with a reason

Receipt text should prefer "passed with note", "not run by scope", "local
commit only", "branch ahead locally", and "policy-only match" when those are
the accurate facts.

## 7. PASS / PASS WITH NOTES / BLOCKED / NOT RUN usage

Use `PASS` when the requested work is complete, requested verification passed,
and there are no material warnings or caveats.

Use `PASS WITH NOTES` when the requested work is complete but the closeout needs
to preserve a caveat, such as a line-ending warning, approval-required rerun,
environment limitation, scoped verification only, or local branch-ahead status.

Use `BLOCKED` when the requested work cannot proceed without owner input,
missing required context, or an external state change. Do not use `BLOCKED`
just because a future optional improvement is deferred.

Use `NOT RUN` for a command or check that was intentionally not executed. Pair
it with a reason, such as "outside task scope", "release verification
forbidden", "artifact regeneration forbidden", or "not applicable to
documentation-only change".

## 8. Git state wording guide

Use precise git state language:

| state | wording |
|---|---|
| untracked file | "untracked file present" |
| intent-to-add | "intent-to-add set; file is visible in diff but not fully staged" |
| staged | "file staged for commit" |
| committed | "local commit created" |
| clean worktree | "working tree clean" |
| local branch ahead | "branch is ahead locally; no push occurred" |
| tagged | "tag exists" only when tag creation or lookup proves it |
| pushed | "pushed" only after an explicit push succeeds |

For generated evidence, distinguish source-basis commits from
artifact-containing commits. For docs-only tasks, do not imply artifact
regeneration when artifacts were not regenerated.

## 9. Automation decision

Decision: audit automation is not justified now.

The observed friction is minor and can be handled by a lightweight manual
receipt checklist. Adding audit automation would create new surface area,
approval burden, privacy risk, maintenance cost, and verification expectations
without enough repeated failure evidence.

Do not create an audit logger, JSONL audit entries, scripts, schema validators,
quality-gate integration, CI integration, RAG-assisted receipt generation, MCP
changes, release evidence, or automatic command-output capture from this
review.

Reconsider automation only after repeated receipt failures cause real review
cost or safety risk, and only under a separate task that names exact files,
stored fields, redaction rules, verification commands, and approval boundaries.

## 10. Next step

Use a lightweight manual receipt checklist for future closeouts:

- result label is precise
- changed files are repo-relative
- verification is command-by-command
- `NOT RUN` checks have reasons
- git state separates untracked, staged, committed, clean, ahead, tagged, and
  pushed states
- policy-only sensitive-word matches are identified without copying values
- safety exclusions are explicit
- no implementation approval is implied by the receipt

Keep manual closeouts as the baseline. Reconsider audit automation only after
repeated receipt failures create real review cost or safety risk.
