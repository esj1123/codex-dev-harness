<!-- TEMPLATE ONLY: Replace placeholders before applying to a downstream repository. -->

# Safety Policy

## Purpose

This template defines the safety boundary for a downstream docs-only readiness baseline.

It is intended for `<REPO_NAME>` and must be customized before use. It does not authorize implementation work, live target action, CI, RAG, retrieval, embeddings, model calls, external services, or generated artifacts.

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

The approved work type is `<ALLOWED_WORK_TYPE>`.

Allowed by default:

- Read approved docs and safe repository metadata.
- Create or update only `<ALLOWED_FILES>`.
- Keep all work local to `<APPROVED_WORKTREE_OR_CLONE_PATH>`.
- Keep findings path-only when safety checks may match sensitive wording.
- Use `not_run` for commands or actions that require separate approval.

Not allowed by default:

- Source code implementation.
- Build, test, package, hook, release, or workflow execution.
- Live target, device, PLC, RSID, Outlook, broker, vault, or production system action.
- CI workflow creation.
- RAG, retrieval, embeddings, vector DB, model calls, or external service integration.
- Copying private source text, equipment values, credentials, customer data, live configuration, vault contents, or mail bodies.

Pattern checks are not proof that secrets or private data are absent.

## Profile-Specific Placeholder Section

Profile name: `<PROFILE_NAME>`

Language profile: `<LANGUAGE_PROFILE>`

Application profile: `<APP_PROFILE>`

Domain profile: `<DOMAIN_PROFILE>`

Profile-specific rules must stay clearly marked. Do not promote profile-specific requirements to generic policy unless they have been reviewed across additional repositories.

## Repo-Specific Placeholder Section

Repository: `<REPO_NAME>`

Repository root: `<REPO_ROOT>`

Approved worktree or clone path: `<APPROVED_WORKTREE_OR_CLONE_PATH>`

Base branch: `<BASE_BRANCH>`

Working branch: `<WORKING_BRANCH>`

Source remote: `<SOURCE_REMOTE>`

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

Domain risk flags are conservative review indicators, not automatic failures.

## Approval Boundary / NOT RUN

Actions requiring separate approval:

```text
<APPROVAL_REQUIRED_ACTIONS>
```

Commands intentionally not run:

```text
<NOT_RUN_COMMANDS>
```

Use this wording for skipped commands:

```text
NOT RUN: <COMMAND_OR_ACTION> was intentionally not run because separate approval is required for this docs-only phase.
```

## Closeout / Review Linkage

Before staging downstream changes, review the generated document against:

- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`
- `docs/SAFETY_PATTERN_CHECKS.md`

Closeout must include:

- files changed
- commands run
- commands intentionally not run
- safety pattern check result using path-only reporting
- unresolved risks
- next phase: `<NEXT_PHASE>`
- closeout date: `<CLOSEOUT_DATE>`
