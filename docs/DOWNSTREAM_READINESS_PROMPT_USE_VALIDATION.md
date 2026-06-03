# Downstream Readiness Prompt Use Validation

## 결론

이 문서는 `templates/prompts/downstream_readiness_baseline.md`를 downstream repository에 적용하기 전에 사용하는 validation recipe이다.

목적은 prompt input이 충분히 준비되었는지, 적용 범위가 docs-only로 제한되었는지, downstream 파일을 수정하기 전에 중단해야 할 조건이 있는지 확인하는 것이다. 이 문서는 downstream repository 수정을 승인하지 않는다.

## 사용 목적

- Prompt template 사용 전에 required input slot 누락을 찾는다.
- Repo-specific 값을 추측하지 않도록 적용 계약을 고정한다.
- Downstream safety boundary가 충분히 명확한지 확인한다.
- Generic template skeleton, status vocabulary, safety pattern rule, pre-stage review checklist 연결을 확인한다.
- 첫 실행은 dry-run 또는 planning-only로 제한할지 판단한다.

## 적용 대상

적용 대상:

- `templates/prompts/downstream_readiness_baseline.md`
- 명시 승인된 downstream repository 또는 clean clone
- docs-only readiness baseline 적용 전 준비 단계

적용 대상이 아닌 항목:

- downstream source implementation
- downstream build/test/package/hook/release/workflow execution
- CI workflow creation
- RAG, retrieval, embeddings, vector DB, model calls, or external services
- generated artifacts
- live target, device, PLC, RSID, Outlook, broker, vault, or production system action

## prompt input readiness checklist

Prompt 사용 전 다음 조건을 확인한다.

| 항목 | 확인 기준 | Result |
| --- | --- | --- |
| target repo approved | `<REPO_NAME>`과 `<REPO_ROOT_OR_CLONE_PATH>`가 명시 승인되었다. | pass / fail |
| branch approved | `<BASE_BRANCH>`와 `<WORKING_BRANCH>`가 명시 승인되었다. | pass / fail |
| remote approved | `<SOURCE_REMOTE>`가 명시 승인되었다. | pass / fail |
| allowed files approved | `<ALLOWED_FILES>`가 구체적인 파일 목록이다. | pass / fail |
| work type approved | `<ALLOWED_WORK_TYPE>`가 docs-only readiness 범위이다. | pass / fail |
| no-touch zones defined | `<NO_TOUCH_ZONES>`와 `<BLOCKED_PATHS>`가 비어 있거나 명확히 기록되었다. | pass / fail |
| verification boundary defined | `<VERIFICATION_COMMANDS_ALLOWED>`와 `<COMMANDS_NOT_RUN>`가 구분되어 있다. | pass / fail |
| closeout language defined | `<CLOSEOUT_LANGUAGE>`가 지정되어 있다. | pass / fail |

하나라도 `fail`이면 prompt를 downstream repository에 적용하지 않는다.

## required input slot checklist

`templates/prompts/downstream_readiness_baseline.md` 사용 전 모든 input slot을 사용자 제공 값으로 채운다.

Required slots:

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

Rules:

- Do not infer missing values.
- Do not fill values from memory.
- Do not copy values from a prior pilot unless the target repo and user approval explicitly match.
- Do not use sibling repository paths unless explicitly approved.
- If any slot remains unresolved, result is `missing_inputs`.

## downstream repo safety boundary checklist

Before prompt use, confirm the downstream boundary.

| Boundary | Required statement |
| --- | --- |
| Read scope | Read safe root docs only: `<SAFE_ROOT_DOCS_TO_READ>`. |
| Write scope | Create or update only: `<DOCS_TO_CREATE_OR_UPDATE>`. |
| Allowed files | All writes must remain inside `<ALLOWED_FILES>`. |
| No-touch zones | Do not read or write `<NO_TOUCH_ZONES>` except where explicit safe docs are listed. |
| Blocked paths | Do not access `<BLOCKED_PATHS>`. |
| Verification | Run only `<VERIFICATION_COMMANDS_ALLOWED>`. |
| NOT RUN | Record `<COMMANDS_NOT_RUN>` as `not_run`, not as passed. |
| Approval-required | Do not perform `<APPROVAL_REQUIRED_ACTIONS>` without separate approval. |

## template reference checklist

Confirm the prompt references the current P0 foundation.

Required foundation docs:

- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`
- `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md`
- `docs/SAFETY_PATTERN_CHECKS.md`

Required template skeletons:

- `templates/downstream_readiness/SAFETY_POLICY.md`
- `templates/downstream_readiness/ACCEPTANCE_TRACE.md`
- `templates/downstream_readiness/VERIFICATION.md`
- `templates/downstream_readiness/AI_HANDOFF.md`

The prompt must use these as structure and review rules. It must not modify them during downstream application.

## stop conditions before prompt use

Stop before using the prompt if:

- Any required input slot is missing.
- Target path, branch, or remote has not been explicitly approved.
- Allowed files are vague or include implementation files.
- Safe root docs to read are not listed.
- No-touch zones or blocked paths are unclear.
- Verification commands include build/test/package/hook/release/workflow commands without separate approval.
- The task would require source deep review.
- The task would require reading private folders, raw data, mail bodies, vault contents, broker data, customer data, live configuration, or generated artifacts.
- The task would require CI, RAG, retrieval, embeddings, vector DB, model calls, or external services.
- The task would require push or PR.
- The target repository has trust, ownership, branch, remote, or permission issues.

## dry-run / planning-only first pass

For a new downstream repository, prefer a planning-only first pass.

Planning-only first pass should ask Codex to:

- Read only `<SAFE_ROOT_DOCS_TO_READ>`.
- Confirm `<ALLOWED_FILES>` and `<DOCS_TO_CREATE_OR_UPDATE>`.
- Identify missing inputs.
- Identify boundary risks.
- Propose the exact docs-only file change list.
- Produce no downstream file changes.

Proceed to actual docs-only application only after the planning result is `ready_to_apply` and the user separately approves.

## generated output review linkage

After generated downstream docs exist, review them against:

- `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md`
- `docs/SAFETY_PATTERN_CHECKS.md`
- `templates/downstream_readiness/*`

Generated output review must confirm:

- created or updated files are within `<ALLOWED_FILES>`
- acceptance trace status values are approved values only
- generated files are not left as `planned`
- `not_run` is used for skipped commands
- safety pattern checks are path-only
- matched private values are not printed
- pattern checks are not treated as proof of absence
- generic, profile-specific, and repo-specific sections remain separated

## pre-stage review linkage

Before staging downstream docs, use:

- `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md`

The review result must be one of:

- `ready_to_stage`
- `needs_tuning`
- `regenerate_after_harness_update`
- `blocked`

Do not stage, commit, push, or open PR before the review result is recorded and separately approved.

## closeout format

Use this closeout after prompt-use validation:

```text
결론:
- Result: <ready_to_apply | missing_inputs | needs_contract_revision | blocked>
- Target repo: <REPO_NAME>
- Target path: <REPO_ROOT_OR_CLONE_PATH>
- Working branch: <WORKING_BRANCH>

Input readiness:
- Required slots complete: <yes | no>
- Missing slots: <NONE_OR_LIST>
- Repo-specific values user-provided only: <yes | no>

Safety boundary:
- Safe root docs: <SAFE_ROOT_DOCS_TO_READ>
- Allowed files: <ALLOWED_FILES>
- No-touch zones: <NO_TOUCH_ZONES>
- Blocked paths: <BLOCKED_PATHS>
- Approval-required actions: <APPROVAL_REQUIRED_ACTIONS>

Prompt use plan:
- First pass: <planning-only | docs-only application>
- Downstream files to create/update: <DOCS_TO_CREATE_OR_UPDATE>
- Commands allowed: <VERIFICATION_COMMANDS_ALLOWED>
- Commands NOT RUN: <COMMANDS_NOT_RUN>

Risks / assumptions:
- <RISK_OR_ASSUMPTION>

Next step:
- <REQUEST_APPROVAL_OR_APPLY_PROMPT>
```

## result states

### ready_to_apply

Use when:

- all required input slots are complete
- target path, branch, remote, and allowed files are explicitly approved
- safety boundary is clear
- first pass mode is chosen
- no stop condition is present

### missing_inputs

Use when:

- one or more required input slots are unresolved
- repo-specific values would need to be guessed
- allowed files, safe docs, blocked paths, or verification boundary are incomplete

### needs_contract_revision

Use when:

- inputs exist but the approved scope is inconsistent
- allowed files are too broad or too narrow
- requested verification conflicts with docs-only safety
- generic/profile-specific/repo-specific split is unclear
- the prompt needs target-specific contract edits before safe use

### blocked

Use when:

- target path, branch, remote, or permissions are unsafe
- downstream repo has trust or ownership problems
- private value exposure risk is present
- source deep review or forbidden command execution would be required
- push, PR, CI, RAG, model tooling, external service, live target, or implementation work is required
