<!-- PROMPT TEMPLATE ONLY: Replace all input slots before using with Codex. -->

# Downstream Readiness Baseline Prompt

Use this prompt to ask Codex to generate a downstream docs-only readiness baseline from the existing codex-dev-harness P0 foundation docs and template skeletons.

Do not use this prompt until every input slot has been replaced with explicit user-provided values.

## 1. Task Contract

Goal:
Create or update docs-only readiness baseline files for `<REPO_NAME>`.

Target repository:
- Repository name: `<REPO_NAME>`
- Approved repository root or clean clone path: `<REPO_ROOT_OR_CLONE_PATH>`
- Source remote: `<SOURCE_REMOTE>`
- Base branch: `<BASE_BRANCH>`
- Working branch: `<WORKING_BRANCH>`

Approved scope:
- Current phase: `<CURRENT_PHASE>`
- Next phase: `<NEXT_PHASE>`
- Allowed work type: `<ALLOWED_WORK_TYPE>`
- Allowed files: `<ALLOWED_FILES>`

Do not infer or guess repository-specific values. Use only the explicit user-provided inputs in this prompt.

## 2. Inputs

Required input slots:

- `<REPO_NAME>`
- `<REPO_ROOT_OR_CLONE_PATH>`
- `<SOURCE_REMOTE>`
- `<BASE_BRANCH>`
- `<WORKING_BRANCH>`
- `<ALLOWED_FILES>`
- `<ALLOWED_WORK_TYPE>`
- `<DOMAIN_RISK_FLAGS>`
- `<NO_TOUCH_ZONES>`
- `<BLOCKED_PATHS>`
- `<PROFILE_NAME>`
- `<LANGUAGE_PROFILE>`
- `<APP_PROFILE>`
- `<DOMAIN_PROFILE>`
- `<CURRENT_PHASE>`
- `<NEXT_PHASE>`
- `<SAFE_ROOT_DOCS_TO_READ>`
- `<DOCS_TO_CREATE_OR_UPDATE>`
- `<VERIFICATION_COMMANDS_ALLOWED>`
- `<COMMANDS_NOT_RUN>`
- `<APPROVAL_REQUIRED_ACTIONS>`
- `<CLOSEOUT_LANGUAGE>`

Before starting, inspect this prompt text. If any required input slot remains unresolved, stop and report the missing slots. Do not fill missing values from memory, local context, sibling repositories, or prior pilot work.

## 3. Read Order

Read safe root docs only from `<REPO_ROOT_OR_CLONE_PATH>`.

Approved safe docs to read:

```text
<SAFE_ROOT_DOCS_TO_READ>
```

Use these codex-dev-harness references as the source of structure and review rules:

- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`
- `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md`
- `docs/SAFETY_PATTERN_CHECKS.md`
- `templates/downstream_readiness/SAFETY_POLICY.md`
- `templates/downstream_readiness/ACCEPTANCE_TRACE.md`
- `templates/downstream_readiness/VERIFICATION.md`
- `templates/downstream_readiness/AI_HANDOFF.md`

Do not perform source deep review. Do not inspect private folders, raw data folders, generated artifacts, live configuration folders, vault folders, mail bodies, broker data, customer data, or blocked paths.

## 4. Allowed Work

Allowed:

- Create or update docs-only readiness files listed in `<DOCS_TO_CREATE_OR_UPDATE>`.
- Modify only files listed in `<ALLOWED_FILES>`.
- Use `templates/downstream_readiness/*` as the document structure.
- Keep generic, profile-specific, and repo-specific content clearly separated.
- Keep repo-specific values limited to explicit user-provided inputs.
- Record forbidden or skipped commands as `NOT RUN`.
- Produce closeout before any stage, commit, push, or PR decision.

Not allowed:

- Implementation work.
- Source code generation.
- Runtime feature changes.
- Changes outside `<ALLOWED_FILES>`.
- Writes to `<BLOCKED_PATHS>`.
- Any command listed in `<COMMANDS_NOT_RUN>`.
- Any action listed in `<APPROVAL_REQUIRED_ACTIONS>` without separate approval.

## 5. Template Application

Apply the generic downstream readiness template skeletons:

- `templates/downstream_readiness/SAFETY_POLICY.md`
- `templates/downstream_readiness/ACCEPTANCE_TRACE.md`
- `templates/downstream_readiness/VERIFICATION.md`
- `templates/downstream_readiness/AI_HANDOFF.md`

Template application rules:

- Replace placeholders only with explicit user-provided inputs.
- Keep unresolved or unknown repository-specific values as blockers, not guesses.
- Keep generic baseline sections generic.
- Keep profile-specific content under profile-specific sections.
- Keep repo-specific content under repo-specific sections.
- Do not promote a repo-specific risk, path, branch, tool, domain term, or pilot observation to a universal rule.
- Avoid Scenario-Simulator-specific values unless the target repo is explicitly Scenario-Simulator and the values are present in user-provided inputs.

## 6. Status Vocabulary Rules

Use `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md` for acceptance trace status values.

Allowed status values:

- `planned`
- `present`
- `ready_for_review`
- `verified`
- `not_run`
- `blocked`
- `deferred`
- `not_applicable`

Rules:

- Do not invent new status values.
- Do not leave generated or updated artifacts as `planned`.
- Use `present` when an artifact exists but has not passed review.
- Use `ready_for_review` when an artifact is ready for human or staging review.
- Use `verified` only when an explicit check has run and produced a concrete result.
- Use `not_run` for intentionally skipped commands or actions.
- Treat `not_run` as honest evidence, not failure.

## 7. Safety Pattern Rules

Use `docs/SAFETY_PATTERN_CHECKS.md` for safety pattern interpretation.

Safety rules:

- Run safety pattern checks only on newly created or modified allowed docs.
- Use path-only reporting by default.
- Report only file path, finding category, and interpretation.
- Do not print matched private values.
- Do not paste secrets, credentials, tokens, account values, endpoint values, equipment values, customer data, live configuration, vault contents, mail bodies, broker data, or private source text into closeout.
- Treat policy wording matches as review indicators, not automatic failures.
- Treat real-looking private values as stop conditions.
- State clearly that pattern checks are not proof that secrets or private data are absent.

Closeout finding format:

```text
<FILE_PATH>: <FINDING_CATEGORY>: <policy_wording_only | possible_private_value>
```

## 8. Pre-Stage Review

Before staging, use `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`.

Required review checks:

- Changed files are within `<ALLOWED_FILES>`.
- Generic, profile-specific, and repo-specific sections remain separated.
- Acceptance trace status values follow `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md`.
- Safety pattern findings follow `docs/SAFETY_PATTERN_CHECKS.md`.
- Forbidden commands are recorded as `NOT RUN`, not as passed.
- Implementation remains out of scope.
- Push and PR require separate approval.

Review result must be one of:

- `ready_to_stage`
- `needs_tuning`
- `regenerate_after_harness_update`
- `blocked`

Do not stage before producing this review result. Do not commit, push, or open a PR without separate approval.

## 9. Forbidden Actions

Do not:

- Modify Scenario-Simulator unless `<REPO_NAME>` is explicitly Scenario-Simulator and the user has approved that target.
- Use Scenario-Simulator-specific values as defaults for other repositories.
- Modify scanner implementation.
- Modify `scripts/quality_gate.py`.
- Modify codex-dev-harness templates while applying this downstream prompt.
- Add render integration.
- Add CI workflows.
- Add RAG, retrieval, embeddings, vector DB, model calls, external services, or generated artifacts.
- Run build, test, package, hook, release, or workflow commands unless separately approved.
- Run live target, device, PLC, RSID, Outlook, broker, vault, production system, or external system actions.
- Print matched private values in closeout.
- Stage, commit, push, or open a PR without separate approval.

## 10. Stop Conditions

Stop and report if:

- Any required input slot remains unresolved.
- `<REPO_ROOT_OR_CLONE_PATH>` does not match the approved target.
- `<SOURCE_REMOTE>`, `<BASE_BRANCH>`, or `<WORKING_BRANCH>` does not match the approved inputs.
- Any file outside `<ALLOWED_FILES>` would need modification.
- Any blocked path in `<BLOCKED_PATHS>` would need to be read or written.
- Source deep review is required to proceed.
- Build, test, package, hook, release, workflow, live target, or external system commands are needed.
- A real-looking private value appears.
- You would need to print a matched private value to explain a finding.
- Scenario-Simulator-specific content would be applied to a different repository.
- Git trust, ownership, permission, branch, path, or remote problems prevent safe work.
- Push or PR would be needed.

## 11. Verification

Allowed verification commands:

```text
<VERIFICATION_COMMANDS_ALLOWED>
```

Commands intentionally not run:

```text
<COMMANDS_NOT_RUN>
```

Verification rules:

- Run only commands explicitly allowed in `<VERIFICATION_COMMANDS_ALLOWED>`.
- Do not run downstream build, test, package, hook, release, or workflow commands unless separately approved.
- Do not run live target or external system commands.
- Mark skipped commands as `not_run`.
- Mark checks as `verified` only when they were actually run and produced an explicit result.

## 12. Closeout

Write closeout in `<CLOSEOUT_LANGUAGE>`.

Closeout must include:

- conclusion
- files changed
- files created
- files updated
- commands run
- commands intentionally not run
- verification result
- acceptance trace status summary
- safety pattern check result using path-only reporting
- confirmation that matched private values were not printed
- confirmation that pattern checks are not proof that secrets or private data are absent
- confirmation that no implementation work was done
- confirmation that no forbidden commands were run
- confirmation that no push or PR was performed
- risks and assumptions
- review result: `ready_to_stage`, `needs_tuning`, `regenerate_after_harness_update`, or `blocked`
- next recommended phase: `<NEXT_PHASE>`

Produce closeout before any stage, commit, push, or PR decision.
