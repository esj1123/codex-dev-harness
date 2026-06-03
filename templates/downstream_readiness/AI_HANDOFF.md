<!-- TEMPLATE ONLY: Replace placeholders before applying to a downstream repository. -->

# AI Handoff

## Purpose

This template defines handoff guidance for downstream docs-only readiness baseline work.

It is intended for `<REPO_NAME>` and must be customized before use. It tells future AI/Codex workers what is approved, what is blocked, and what remains out of scope.

Reference before applying:

- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`
- `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md`
- `docs/SAFETY_PATTERN_CHECKS.md`

## Placeholder Block

Replace these placeholders before applying this template:

- `<REPO_NAME>`
- `<REPO_ROOT>`
- `<APPROVED_WORKTREE_OR_CLONE_PATH>`
- `<BLOCKED_PATHS>`
- `<WORKING_BRANCH>`
- `<BASE_BRANCH>`
- `<SOURCE_REMOTE>`
- `<ALLOWED_FILES>`
- `<ALLOWED_WORK_TYPE>`
- `<DOMAIN_RISK_FLAGS>`
- `<NO_TOUCH_ZONES>`
- `<PROFILE_NAME>`
- `<LANGUAGE_PROFILE>`
- `<APP_PROFILE>`
- `<DOMAIN_PROFILE>`
- `<VERIFICATION_COMMANDS>`
- `<NOT_RUN_COMMANDS>`
- `<APPROVAL_REQUIRED_ACTIONS>`
- `<NEXT_PHASE>`
- `<CLOSEOUT_DATE>`

## Generic Baseline

Current approved work type: `<ALLOWED_WORK_TYPE>`

Future AI/Codex workers may:

- Read this handoff and approved docs.
- Work only in `<APPROVED_WORKTREE_OR_CLONE_PATH>`.
- Modify only `<ALLOWED_FILES>` when explicitly approved.
- Use path-only safety pattern checks.
- Record skipped commands as `not_run`.

Future AI/Codex workers must not:

- Modify blocked paths.
- Run build, test, package, hook, release, or workflow commands without separate approval.
- Implement product features.
- Create CI workflows.
- Add RAG, retrieval, embeddings, vector DB, model calls, or external services.
- Touch live targets, devices, PLCs, RSID, Outlook, broker, vault, or production systems.
- Copy private source, equipment values, credentials, customer data, live configuration, vault contents, or mail bodies.

## Profile-Specific Placeholder Section

Profile name: `<PROFILE_NAME>`

Language profile: `<LANGUAGE_PROFILE>`

Application profile: `<APP_PROFILE>`

Domain profile: `<DOMAIN_PROFILE>`

Profile-specific handoff notes:

```text
<PROFILE_SPECIFIC_HANDOFF_NOTES>
```

## Repo-Specific Placeholder Section

Repository: `<REPO_NAME>`

Repository root: `<REPO_ROOT>`

Approved worktree or clone path: `<APPROVED_WORKTREE_OR_CLONE_PATH>`

Base branch: `<BASE_BRANCH>`

Working branch: `<WORKING_BRANCH>`

Source remote: `<SOURCE_REMOTE>`

Allowed files:

```text
<ALLOWED_FILES>
```

Blocked paths:

```text
<BLOCKED_PATHS>
```

No-touch zones:

```text
<NO_TOUCH_ZONES>
```

Domain risk flags:

```text
<DOMAIN_RISK_FLAGS>
```

## Approval Boundary / NOT RUN

Actions requiring separate approval:

```text
<APPROVAL_REQUIRED_ACTIONS>
```

Commands intentionally not run:

```text
<NOT_RUN_COMMANDS>
```

Do not treat this handoff as approval for:

- writes outside `<ALLOWED_FILES>`
- implementation
- runtime verification
- push
- PR
- CI
- deployment
- live target action

## Closeout / Review Linkage

Before staging downstream changes, review the generated handoff against:

- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`
- `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md`
- `docs/SAFETY_PATTERN_CHECKS.md`

Closeout must include:

- files changed
- files intentionally not changed
- commands run
- commands intentionally not run
- safety pattern check result
- whether the generated docs are ready to stage
- risks and assumptions
- next phase: `<NEXT_PHASE>`
- closeout date: `<CLOSEOUT_DATE>`
