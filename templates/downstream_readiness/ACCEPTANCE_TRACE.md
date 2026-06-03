<!-- TEMPLATE ONLY: Replace placeholders before applying to a downstream repository. -->

# Acceptance Trace

## Purpose

This template defines an evidence trace for downstream docs-only readiness baseline work.

It is intended for `<REPO_NAME>` and must be customized before use. It records documentation readiness evidence only and does not authorize implementation, CI, deployment, RAG, external service use, or live target action.

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

Use only the status values defined in `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md`:

- `planned`
- `present`
- `ready_for_review`
- `verified`
- `not_run`
- `blocked`
- `deferred`
- `not_applicable`

Do not leave rows as `planned` when an artifact already exists unless the row is truly future-only.

## Profile-Specific Placeholder Section

Profile name: `<PROFILE_NAME>`

Language profile: `<LANGUAGE_PROFILE>`

Application profile: `<APP_PROFILE>`

Domain profile: `<DOMAIN_PROFILE>`

Profile-specific trace rows:

| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| `<PROFILE_SPECIFIC_REQUIREMENT>` | `<ARTIFACT_PATH>` | `planned` | Replace with a reviewed profile-specific row. |

## Repo-Specific Placeholder Section

Repository: `<REPO_NAME>`

Approved path: `<APPROVED_WORKTREE_OR_CLONE_PATH>`

Allowed files:

```text
<ALLOWED_FILES>
```

Domain risk flags:

```text
<DOMAIN_RISK_FLAGS>
```

No-touch zones:

```text
<NO_TOUCH_ZONES>
```

## Docs-Only Baseline Trace

| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| Safety boundary documented | `<SAFETY_POLICY_PATH>` | `ready_for_review` | Use `present` if the artifact exists but has not been reviewed. |
| Acceptance trace documented | `<ACCEPTANCE_TRACE_PATH>` | `ready_for_review` | Use approved status vocabulary only. |
| Verification boundary documented | `<VERIFICATION_PATH>` | `ready_for_review` | Verification commands must remain docs-only unless separately approved. |
| AI handoff documented | `<AI_HANDOFF_PATH>` | `ready_for_review` | Handoff must not authorize writes or implementation. |
| Allowed file list checked | `<ALLOWED_FILES>` | `ready_for_review` | Mark `verified` only after explicit check. |
| Safety pattern check planned | `docs/SAFETY_PATTERN_CHECKS.md` | `planned` | Mark `verified` only after path-only checks complete. |

## Approval Boundary / NOT RUN

| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| Build/test/package/hook/release/workflow commands | `<NOT_RUN_COMMANDS>` | `not_run` | NOT RUN: separate approval is required for this docs-only phase. |
| Push or PR | `<APPROVAL_REQUIRED_ACTIONS>` | `not_run` | NOT RUN: push and PR require separate approval. |
| Live target or external system action | `<NO_TOUCH_ZONES>` | `not_run` | NOT RUN: live target and external system actions are forbidden in this phase. |

## Closeout / Review Linkage

Before staging downstream changes, review this trace against:

- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`
- `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md`
- `docs/SAFETY_PATTERN_CHECKS.md`

Closeout summary:

```text
Acceptance trace status:
- planned: <COUNT_OR_ITEMS>
- present: <COUNT_OR_ITEMS>
- ready_for_review: <COUNT_OR_ITEMS>
- verified: <COUNT_OR_ITEMS>
- not_run: <COUNT_OR_ITEMS>
- blocked: <COUNT_OR_ITEMS>
- deferred: <COUNT_OR_ITEMS>
- not_applicable: <COUNT_OR_ITEMS>
```

Next phase: `<NEXT_PHASE>`

Closeout date: `<CLOSEOUT_DATE>`
