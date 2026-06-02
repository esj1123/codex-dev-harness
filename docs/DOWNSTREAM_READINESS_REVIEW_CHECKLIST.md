# Downstream Readiness Review Checklist

## 결론

이 문서는 downstream repository에 생성된 docs-only readiness baseline을 stage하기 전에 검토하기 위한 체크리스트이다.

목적은 생성물이 구조적으로 유용한지, repo별 조정이 필요한지, 또는 harness 쪽 template/prompt/checklist 개선 후 재생성해야 하는지를 판단하는 것이다. 이 체크리스트는 특정 pilot repository의 결과를 범용 표준으로 승격하지 않으며, repo-specific 값은 placeholder로 남긴다.

## 사용 목적

- generated docs-only readiness baseline의 staging 가능 여부를 판단한다.
- generic, profile-specific, repo-specific 내용을 분리했는지 확인한다.
- safety wording이 실제 검증 완료처럼 과장되지 않았는지 확인한다.
- forbidden implementation work, live target action, CI, RAG, model tooling이 섞이지 않았는지 확인한다.
- stage 전 closeout에 필요한 evidence와 `NOT RUN` 항목을 정리한다.

이 문서는 downstream repo에 쓰기 권한을 부여하거나 implementation work를 승인하지 않는다.

## 적용 대상

적용 대상은 명시적으로 승인된 downstream docs-only readiness baseline이다.

예상 입력:

- 승인된 downstream repository 이름: `<REPO_NAME>`
- 승인된 작업 경로: `<APPROVED_WORKTREE_OR_CLONE_PATH>`
- 승인된 branch: `<WORKING_BRANCH>`
- 승인된 allowed files: `<ALLOWED_FILE_LIST>`
- 승인된 work type: `docs-only readiness baseline`

적용 대상이 아닌 항목:

- application code
- build, test, package, hook, release, workflow execution
- CI workflow creation
- RAG, retrieval, embedding, vector DB, model call, external service integration
- live target, device, PLC, RSID, Outlook, broker, vault, or production system action

## stage 전 필수 확인 항목

Stage 전에 다음 항목을 모두 확인한다.

| 항목 | 확인 기준 | 판정 |
| --- | --- | --- |
| 승인된 repository | `<REPO_NAME>`이 명시 승인된 대상과 일치한다. | pass / fail |
| 승인된 경로 | 작업 경로가 `<APPROVED_WORKTREE_OR_CLONE_PATH>`와 일치한다. | pass / fail |
| 승인된 branch | 현재 branch가 `<WORKING_BRANCH>`와 일치한다. | pass / fail |
| 변경 파일 범위 | 변경 파일이 `<ALLOWED_FILE_LIST>` 안에만 있다. | pass / fail |
| implementation 없음 | source code, app feature, generated artifact 변경이 없다. | pass / fail |
| private value 없음 | raw private source, credentials, IP, port, live config, customer data를 포함하지 않는다. | pass / fail |
| verification honesty | 실행하지 않은 명령은 `NOT RUN`으로 기록되어 있다. | pass / fail |
| push/PR 미수행 | 별도 승인 없이 push 또는 PR을 수행하지 않았다. | pass / fail |

하나라도 `fail`이면 stage하지 않는다.

## allowed file list 확인

Allowed file list는 task contract에 명시된 파일만 사용한다.

검토 방법:

1. `git status --short --untracked-files=all`로 변경 파일을 확인한다.
2. `git diff --name-only`와 필요한 경우 `git diff --cached --name-only`로 변경 파일 목록을 확인한다.
3. 변경 파일이 `<ALLOWED_FILE_LIST>`에 없는 경우 stage를 중단한다.
4. 누락된 문서가 필요해 보이더라도 allowed list 밖이면 새 파일을 만들지 않는다.

판정 기준:

- `ready`: 모든 변경 파일이 allowed list 안에 있다.
- `needs_tuning`: allowed list 안이지만 문서 내용 조정이 필요하다.
- `blocked`: allowed list 밖 변경이 존재하거나 필수 변경에 allowed list 확장이 필요하다.

## generic / profile-specific / repo-specific 분리 확인

Generated docs는 다음 세 범주를 명확히 구분해야 한다.

| 범주 | 의미 | 예시 placeholder |
| --- | --- | --- |
| generic | 모든 downstream repo에 반복 적용 가능한 구조 | safety boundary table, acceptance trace layout, closeout receipt |
| profile-specific | 언어, framework, domain profile에 따라 달라지는 규칙 | `<LANGUAGE_PROFILE>`, `<APP_PROFILE>`, `<DOMAIN_PROFILE>` |
| repo-specific | 해당 repo의 approved scope와 known risk에만 해당하는 내용 | `<REPO_NAME>`, `<NO_TOUCH_PATHS>`, `<DOMAIN_RISK_FLAGS>` |

확인 기준:

- repo-specific 값을 generic template 문장처럼 쓰지 않는다.
- profile-specific 항목은 profile 후보로 표시하고, 즉시 범용 규칙으로 승격하지 않는다.
- downstream repo의 domain risk는 review indicator로 다루고 automatic failure로 취급하지 않는다.

## acceptance trace status 확인

Acceptance trace의 status vocabulary는 일관적이어야 한다.

권장 status:

- `PLANNED`: 아직 구현 또는 문서화되지 않았고 계획만 있다.
- `DOCS_BASELINE`: docs-only baseline으로 작성되었다.
- `VERIFIED_DOCS_ONLY`: 허용된 문서 검증만 통과했다.
- `NOT_RUN`: 명령 또는 검증을 실행하지 않았다.
- `BLOCKED`: 승인, 권한, missing input, unsafe scope 때문에 진행하지 않았다.
- `OUT_OF_SCOPE`: 현재 phase에서 명시적으로 제외되었다.

금지되는 표현:

- 실행하지 않은 검증을 `passed`로 기록한다.
- scanner 결과를 secrets 부재 증명으로 기록한다.
- docs-only baseline을 implementation approval처럼 기록한다.
- domain risk flag를 자동 실패로 기록한다.

## safety pattern check 해석

Safety pattern check는 private value 부재의 증명이 아니다.

해석 규칙:

- Check 대상은 새로 생성되거나 수정된 allowed docs로 제한한다.
- 의심 패턴이 발견되면 matched value를 출력하지 않고 file path와 finding type만 기록한다.
- 정책 문구에 포함된 `credential`, `secret`, `private`, `live` 같은 단어는 context상 policy wording인지 확인한다.
- 실제 private value처럼 보이는 match가 있으면 stage를 중단하고 사용자 확인을 요청한다.
- Scanner 또는 pattern check 결과는 secrets, credentials, customer data, live config가 없다는 보증으로 쓰지 않는다.

권장 closeout 표현:

```text
Safety pattern check: path-only review completed for modified allowed docs.
Findings were reviewed as policy wording only. This is not proof that secrets or private data are absent.
```

## branch/path stale risk 확인

Downstream docs generation은 branch와 path가 stale해질 수 있다.

확인 항목:

- 작업 경로가 승인된 clean clone 또는 worktree인지 확인한다.
- blocked path 또는 dubious ownership path를 사용하지 않았는지 확인한다.
- 현재 branch가 승인된 working branch와 일치하는지 확인한다.
- remote URL이 승인된 repository와 일치하는지 확인한다.
- baseline 생성 전후에 unexpected pre-existing changes가 없는지 확인한다.
- clone 상태가 오래된 경우 fetch/rebase/merge는 별도 승인 전에는 수행하지 않는다.

Stale risk가 있으면 `needs_tuning` 또는 `blocked`로 판정한다.

## NOT RUN honesty 확인

실행하지 않은 명령은 반드시 `NOT RUN`으로 남긴다.

적용 대상:

- build command
- test command
- package manager command
- hook command
- release command
- workflow command
- live target or device check
- push or PR action

권장 문구:

```text
NOT RUN: <COMMAND_OR_ACTION> was intentionally not run because this phase is docs-only and separate approval is required.
```

금지되는 문구:

- 실행하지 않은 test를 passed로 표현한다.
- docs-only review를 runtime verification으로 표현한다.
- scanner score를 implementation readiness approval로 표현한다.

## implementation out-of-scope 확인

Docs-only readiness baseline에는 implementation work가 포함되면 안 된다.

Out-of-scope 확인 항목:

- source code 변경 없음
- generated application code 없음
- feature implementation 없음
- parser, serializer, engine, communication, integration 구현 없음
- live target command 또는 network/device action 없음
- package, dependency, build config 변경 없음
- CI workflow 추가 없음
- RAG, retrieval, embedding, vector DB, model call, external service 추가 없음

Implementation need가 발견되면 문서에 `deferred` 또는 `out of scope`로 남기고 stage 여부를 재검토한다.

## push/PR 승인 경계 확인

Stage, commit, push, PR은 서로 다른 승인 단계로 취급한다.

기본 경계:

- stage: generated docs가 검토를 통과한 뒤 별도 승인 필요
- commit: staged diff 확인 후 별도 승인 필요
- push: commit 이후 별도 승인 필요
- PR: push 이후 별도 승인 필요

Closeout에는 다음을 명시한다.

- `No push was performed.`
- `No PR was opened.`
- `Push/PR requires separate approval.`

## 결과 판정

검토 결과는 다음 중 하나로 기록한다.

### ready_to_stage

조건:

- 변경 파일이 allowed list 안에만 있다.
- generic, profile-specific, repo-specific 분리가 명확하다.
- private value 또는 live config가 포함되지 않았다.
- `NOT RUN` 항목이 정직하게 기록되어 있다.
- implementation work가 없다.
- stage만 진행해도 scope creep이 발생하지 않는다.

### needs_tuning

조건:

- 파일 범위는 맞지만 wording, status, closeout, safety boundary가 다듬어져야 한다.
- repo-specific 내용이 generic처럼 보일 위험이 있다.
- acceptance trace status가 불명확하다.
- safety pattern finding 해석이 누락되어 있다.

### regenerate_after_harness_update

조건:

- 생성물의 구조가 반복적으로 거칠다.
- prompt 또는 template 부재 때문에 여러 문서가 같은 방식으로 어긋난다.
- downstream repo에서 직접 고치는 것보다 harness template/prompt/checklist 개선 후 재생성하는 편이 낫다.

### blocked

조건:

- allowed list 밖 변경이 있다.
- private value, credential, live config, customer data 의심 항목이 있다.
- blocked path 또는 승인되지 않은 repository를 사용했다.
- Git trust, branch, remote, path 문제가 해결되지 않았다.
- implementation work가 섞였다.
- 추가 승인 없이는 stage 여부를 판단할 수 없다.

## closeout template

```text
결론:
- Result: <ready_to_stage | needs_tuning | regenerate_after_harness_update | blocked>
- Repository: <REPO_NAME>
- Path: <APPROVED_WORKTREE_OR_CLONE_PATH>
- Branch: <WORKING_BRANCH>

Files reviewed:
- <FILE_1>
- <FILE_2>

Allowed file list result:
- <PASS_OR_ISSUE>

Content review:
- Generic/profile-specific/repo-specific separation: <PASS_OR_ISSUE>
- Acceptance trace status: <PASS_OR_ISSUE>
- NOT RUN honesty: <PASS_OR_ISSUE>
- Implementation out-of-scope: <PASS_OR_ISSUE>

Safety pattern check:
- Scope: modified allowed docs only
- Result: <PASS_OR_FINDING_TYPE>
- Private values printed: no
- Note: This is not proof that secrets or private data are absent.

Commands run:
- <COMMAND_1>
- <COMMAND_2>

Commands intentionally NOT RUN:
- NOT RUN: build/test/package/hook/release/workflow commands require separate approval.
- NOT RUN: push/PR requires separate approval.

Risks / assumptions:
- <RISK_OR_ASSUMPTION>

Next recommended action:
- <stage | tune docs | improve harness then regenerate | request approval>
```
