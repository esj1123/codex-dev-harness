# Acceptance Trace Status Vocabulary

## 결론

이 문서는 downstream docs-only readiness 작업에서 `ACCEPTANCE_TRACE.md`에 사용할 reusable status vocabulary를 정의한다.

핵심 규칙은 단순하다. 이미 생성되었거나 갱신된 artifact를 계속 `planned`로 남기지 않는다. `verified`는 명시적인 검증 결과가 있을 때만 사용한다. `not_run`은 실패가 아니라 실행하지 않았음을 정직하게 기록하는 상태이다.

## 사용 목적

- downstream docs-only readiness baseline의 acceptance trace status를 일관되게 작성한다.
- 생성된 문서, 검토 대기 문서, 검증 완료 문서, 실행하지 않은 검증을 구분한다.
- `Planned` 남용을 줄이고 stage 전 review 판단을 명확히 한다.
- closeout receipt와 review checklist에서 같은 status vocabulary를 재사용한다.

이 문서는 implementation approval, runtime verification, push, PR, release approval을 대체하지 않는다.

## 적용 대상

적용 대상:

- downstream docs-only readiness baseline
- generated or updated policy docs
- acceptance trace rows for documentation artifacts
- stage 전 human/staging review
- closeout receipt evidence

적용 대상이 아닌 항목:

- source code implementation status
- build or release readiness
- live target, device, PLC, RSID, Outlook, broker, vault, or production action status
- CI workflow status
- RAG, retrieval, embedding, vector DB, model call, or external service status

Repo-specific 값이 필요한 경우 placeholder를 사용한다.

- `<REPO_NAME>`
- `<ARTIFACT_PATH>`
- `<APPROVED_WORKTREE_OR_CLONE_PATH>`
- `<WORKING_BRANCH>`
- `<CHECK_COMMAND>`
- `<NOT_RUN_REASON>`

## status vocabulary table

| Status | Meaning | Use when | Do not use when |
| --- | --- | --- | --- |
| `planned` | Work is future-only and no artifact is present yet. | A document or evidence item is intentionally deferred to a later approved phase. | The file already exists or has been generated in the current phase. |
| `present` | The artifact exists, but review has not passed yet. | A generated or existing file is present and still needs content review. | The item has already passed explicit review or verification. |
| `ready_for_review` | The artifact was generated or updated and is ready for human/staging review. | The content is in allowed files and ready for pre-stage review. | The artifact has not been inspected for allowed file scope or safety boundaries. |
| `verified` | An explicit check result supports the row. | A named command, inspection, or checklist item completed successfully. | No explicit check was run, or the check result is unknown. |
| `not_run` | The check or action was intentionally not run. | A command is out of scope or requires separate approval. | The command failed after being attempted; use `blocked` or describe the failure. |
| `blocked` | Progress is stopped by approval, path, trust, missing input, or safety constraints. | Work cannot proceed safely without user input or external change. | The item is simply future work with no blocker; use `planned` or `deferred`. |
| `deferred` | Work is intentionally postponed to a later phase. | The item is valid but outside the current phase. | The item is permanently irrelevant; use `not_applicable`. |
| `not_applicable` | The item does not apply to this repo or approved scope. | A generic checklist row is irrelevant to `<REPO_NAME>`. | The item applies but was not performed; use `not_run`, `planned`, or `deferred`. |

## allowed status values

Use only these lowercase status values in downstream docs-only readiness acceptance traces unless the task explicitly approves a different vocabulary:

- `planned`
- `present`
- `ready_for_review`
- `verified`
- `not_run`
- `blocked`
- `deferred`
- `not_applicable`

Recommended formatting:

```text
| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| <REQUIREMENT> | <ARTIFACT_PATH> | ready_for_review | Generated in docs-only phase; pending staging review. |
```

## disallowed or discouraged status values

Avoid status values that blur evidence, approval, or execution.

| Value | Reason |
| --- | --- |
| `passed` | Too broad unless tied to a named check. Prefer `verified` with explicit evidence. |
| `complete` | Can be misread as implementation completion. Prefer `verified`, `ready_for_review`, or `deferred`. |
| `done` | Too vague for evidence discipline. |
| `approved` | Approval is separate from artifact state. |
| `safe` | Safety is bounded and evidence-specific, not absolute. |
| `ready` | Ambiguous. Prefer `ready_for_review` or a repo-specific conclusion outside the status column. |
| `failed` | Too broad. Prefer `blocked` with reason or keep command result in notes. |
| `unknown` | Prefer `blocked`, `not_run`, or `planned` with a reason. |

`Planned` should not be used for files that already exist unless the row truly refers to future-only work. If a file exists but has not passed review, use `present`. If it has been generated or updated and is ready for human/staging review, use `ready_for_review`.

## transition examples

Common docs-only transitions:

| Before | After | Trigger |
| --- | --- | --- |
| `planned` | `present` | `<ARTIFACT_PATH>` exists, but content review has not happened. |
| `planned` | `ready_for_review` | `<ARTIFACT_PATH>` was generated in allowed scope and is ready for pre-stage review. |
| `present` | `ready_for_review` | Existing artifact was updated or reviewed enough to begin staging review. |
| `ready_for_review` | `verified` | Explicit review command or checklist item passed. |
| `ready_for_review` | `needs_tuning` | Do not use this as a status value; record `present` or `ready_for_review` and put tuning need in notes or review result. |
| `planned` | `deferred` | Work remains valid but is postponed to a later approved phase. |
| `planned` | `not_applicable` | Generic checklist item does not apply to `<REPO_NAME>`. |
| any | `blocked` | Safety, branch, path, approval, or missing input prevents progress. |
| any | `not_run` | A command or action was intentionally not run in this phase. |

For review outcomes such as `ready_to_stage`, `needs_tuning`, `regenerate_after_harness_update`, or `blocked`, use the downstream review checklist result field rather than the acceptance trace status column.

## docs-only readiness examples

Example for a generated safety policy:

```text
| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| Safety boundary documented | docs/SAFETY_POLICY.md | ready_for_review | Docs-only baseline generated; pending pre-stage review. |
```

Example for an existing handoff doc:

```text
| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| AI handoff guidance present | docs/AI_HANDOFF.md | present | File exists; content review not yet completed. |
```

Example for an explicit verification check:

```text
| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| Whitespace check | git diff --check | verified | Command completed with no whitespace errors. |
```

Example for a command intentionally not run:

```text
| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| Build command | <CHECK_COMMAND> | not_run | NOT RUN: build commands require separate approval in docs-only phase. |
```

Example for a repo-specific non-applicable row:

```text
| Requirement | Evidence | Status | Notes |
| --- | --- | --- | --- |
| <PROFILE_SPECIFIC_REQUIREMENT> | <ARTIFACT_PATH> | not_applicable | This requirement does not apply to <REPO_NAME> under the approved scope. |
```

## NOT RUN relationship

`not_run` is an honest status, not a failure.

Use `not_run` when:

- a command was intentionally skipped because the phase is docs-only
- build/test/package/hook/release/workflow commands require separate approval
- push or PR requires separate approval
- live target, device, network, vault, broker, or external system checks are forbidden
- a runtime check would require modifying the downstream repo or environment

Do not replace `not_run` with `verified`. A skipped command has not verified behavior.

Recommended note format:

```text
NOT RUN: <COMMAND_OR_ACTION> was intentionally not run because <NOT_RUN_REASON>.
```

If a command was attempted and failed, do not mark it as `not_run`. Use `blocked` if the failure prevents progress, and put the failure category in notes without printing private values.

## closeout usage

Closeout should summarize acceptance trace status without overstating evidence.

Recommended closeout block:

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

Evidence note:
- `verified` rows are backed by explicit checks listed in Commands run.
- `not_run` rows were intentionally skipped and are not failures.
- Scanner or pattern-check output is not proof that secrets or private data are absent.
```

## review checklist integration

Use this vocabulary with `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`.

Checklist integration points:

- The `acceptance trace status 확인` step should verify that only allowed status values are used.
- Rows for existing generated files should not remain `planned`.
- `verified` rows must point to explicit checks, commands, or review evidence.
- `not_run` rows must include a clear reason.
- Review outcome values such as `ready_to_stage` belong in the review result, not in acceptance trace status.

If the acceptance trace uses unclear status values, the review result should be `needs_tuning` unless the issue blocks safe review.

## template/prompt integration notes

Future template and prompt work should reuse this vocabulary without hard-coding repo-specific content.

Template guidance:

- Include the allowed status values directly in downstream acceptance trace templates.
- Provide one example row for each common status.
- Keep repo-specific requirements as placeholders.
- Keep profile-specific requirements marked as profile-specific.
- Add a note that `planned` is for future-only work, not already created artifacts.

Prompt guidance:

- Ask the worker to update status after creating or updating docs.
- Ask the worker to mark generated docs as `ready_for_review`, not `planned`.
- Ask the worker to mark explicit command results as `verified` only when the command was run.
- Ask the worker to mark skipped commands as `not_run` with a reason.
- Ask the worker to avoid status values outside the approved vocabulary unless explicitly approved.

This document is a vocabulary reference only. It does not add templates, prompt templates, scanner logic, quality gate integration, CI, or downstream repository changes.
