<!-- TEMPLATE ONLY: Replace placeholders before applying to a downstream repository. -->

# Verification

## Purpose

This template defines verification boundaries for downstream docs-only readiness baseline work.

It is intended for `<REPO_NAME>` and must be customized before use. Verification in this document is limited to approved docs-only checks unless separate approval is granted.

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

Allowed verification:

- Check current repository status for approved docs-only changes.
- Check changed file list against `<ALLOWED_FILES>`.
- Run whitespace or diff hygiene checks that do not execute downstream code.
- Run path-only safety pattern checks on changed allowed docs.
- Record skipped commands as `not_run`.

Forbidden verification unless separately approved:

- Build commands.
- Test commands.
- Package manager commands.
- Hook commands.
- Release commands.
- Workflow commands.
- Live target, device, PLC, RSID, Outlook, broker, vault, or production system checks.
- RAG, retrieval, embeddings, vector DB, model calls, or external service calls.

## Profile-Specific Placeholder Section

Profile name: `<PROFILE_NAME>`

Language profile: `<LANGUAGE_PROFILE>`

Application profile: `<APP_PROFILE>`

Domain profile: `<DOMAIN_PROFILE>`

Profile-specific verification commands must be listed as placeholders until explicitly approved:

```text
<PROFILE_SPECIFIC_VERIFICATION_COMMANDS>
```

## Repo-Specific Placeholder Section

Repository: `<REPO_NAME>`

Repository root: `<REPO_ROOT>`

Approved path: `<APPROVED_WORKTREE_OR_CLONE_PATH>`

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

## Approval Boundary / NOT RUN

Approved docs-only verification commands:

```text
<VERIFICATION_COMMANDS>
```

Commands intentionally not run:

```text
<NOT_RUN_COMMANDS>
```

Approval-required actions:

```text
<APPROVAL_REQUIRED_ACTIONS>
```

Use `not_run` for commands that were intentionally skipped. Do not mark skipped commands as `verified`.

## Safety Pattern Checks

Use `docs/SAFETY_PATTERN_CHECKS.md` for path-only checks.

Required interpretation:

- Policy wording matches are not automatic failures.
- Possible private values require stop and report.
- Do not paste matched private values into closeout.
- Pattern checks are not proof that secrets or private data are absent.

## Closeout / Review Linkage

Before staging downstream changes, review verification evidence against:

- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`
- `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md`
- `docs/SAFETY_PATTERN_CHECKS.md`

Closeout must report:

- commands run
- commands intentionally not run
- verification result
- safety pattern check result
- final working tree status
- next phase: `<NEXT_PHASE>`
- closeout date: `<CLOSEOUT_DATE>`
