# Downstream readiness improvement backlog

## 1. 결론

Scenario-Simulator docs-only readiness pilot은 구조적으로 유효했지만, 다음
downstream repository에 그대로 반복 적용하기에는 rough edge가 확인되었다.

가장 큰 결론은 Scenario-Simulator clone을 먼저 튜닝하는 것이 아니라,
`codex-dev-harness`에 downstream readiness 생성용 template, prompt, review
checklist를 먼저 보강해야 한다는 점이다.

이 backlog는 pilot 결과를 generic framework로 환원하기 위한 계획 문서다.
Scenario-specific 항목은 자동으로 범용 표준에 승격하지 않는다.

## 2. Scenario pilot에서 관찰된 문제

| 관찰된 문제 | 영향 |
|---|---|
| acceptance trace status가 모두 `Planned`로 생성됨 | 생성 직후 상태와 맞지 않아 staging 전 사람이 다시 조정해야 함 |
| safety/no-touch 문구가 여러 문서에 반복됨 | 안전성은 높지만 유지보수성과 일관성이 떨어질 수 있음 |
| branch와 local path 문구가 장기 문서에 고정됨 | branch/path staleness risk 발생 |
| generic no-touch zone과 repo-specific no-touch zone이 섞임 | 다른 downstream repo에 부적합한 표준이 될 수 있음 |
| safety pattern check가 policy wording을 다수 탐지함 | false positive 해석 규칙이 필요함 |
| line text를 출력할 수 있는 pattern command가 생성될 위험이 있음 | private value 출력 금지 원칙과 충돌할 수 있음 |
| build/test script 언급과 현재 phase 실행 금지가 공존함 | phase별 verification boundary가 더 명확해야 함 |
| staging 전 review checklist가 없음 | rough generated docs가 바로 commit될 위험이 있음 |
| Scenario phase naming이 자연스럽게 섞임 | `P1 WPF/MVVM`, `ScenarioStep` 등이 universal template에 섞일 수 있음 |

## 3. codex-dev-harness 개선 backlog

| item | problem observed | generic improvement proposed | candidate file path | scope | priority | acceptance criteria |
|---|---|---|---|---|---|---|
| downstream readiness template pack | readiness docs를 매번 자유형으로 생성해 구조와 중복이 흔들림 | safety, acceptance trace, verification, handoff template pack 추가 | `templates/downstream_readiness/` | generic | P0 | 4개 핵심 문서 template이 있고 repo-specific placeholder가 generic placeholder와 분리됨 |
| readiness baseline prompt template | prompt가 길고 매번 수동 조정 필요 | downstream docs-only baseline 생성 prompt를 표준화 | `docs/prompts/downstream_readiness_baseline.md` | generic | P0 | clone path, branch, allowed files, forbidden implementation, private data boundary 입력 슬롯 포함 |
| generated docs before staging review checklist | generated docs를 바로 stage하면 rough text가 남을 수 있음 | downstream generated docs staging 전 checklist 추가 | `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md` | generic | P0 | allowed files, stale branch/path, status vocabulary, pattern checks, no implementation 확인 항목 포함 |
| acceptance trace status vocabulary | `Planned` status가 생성 후 상태와 맞지 않음 | readiness trace status set 정의 | `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md` | generic | P0 | `planned`, `present`, `ready_for_review`, `verified`, `not_run`, `blocked`, `deferred` 정의 |
| safety pattern path-only check recipe | matched value를 출력하는 command가 생성될 위험 | path-only pattern check recipe 표준화 | `docs/SAFETY_PATTERN_CHECKS.md` | generic | P0 | `rg -l` 기본, fallback도 value 출력 금지, closeout은 file path와 finding type만 |
| policy wording interpretation rule | policy docs 자체가 credential/live/customer 단어를 포함함 | policy wording match와 possible private value 구분 규칙 추가 | `docs/SAFETY_PATTERN_CHECKS.md` | generic | P0 | “policy wording only”와 “possible private value” 판정 기준 포함 |
| branch/path staleness checklist | handoff에 current branch/path가 고정되어 stale 가능 | branch/path 문구의 위치와 만료 조건을 review | `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md` | generic | P1 | long-lived docs에 branch/path를 넣을 때 stale risk 또는 manifest reference를 요구 |
| no-touch zone generic/repo-specific split | blocked path, RSID, Obsidian 등 전용 경계가 generic과 섞임 | no-touch zone template을 generic과 repo-specific section으로 분리 | `templates/downstream_readiness/SAFETY_POLICY.md` | generic | P0 | `Generic no-touch zones`와 `Repository-specific no-touch zones`가 분리됨 |
| NOT RUN honesty reusable block | NOT RUN 원칙이 문서마다 다르게 표현될 수 있음 | reusable NOT RUN block 작성 | `templates/snippets/not_run_honesty.md` | generic | P1 | “not executed means not passed” 원칙과 closeout 예시 포함 |
| allowed file list guard | generated docs가 approved file 밖으로 나갈 수 있음 | changed files가 approved list subset인지 확인하는 checklist 추가 | `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md` | generic | P0 | staging 전 changed files 대조 항목 포함 |
| docs-only / implementation verification split | build/test placeholders와 실행 금지가 한 문서에 혼재함 | current phase allowed checks와 future phase commands를 분리 | `templates/downstream_readiness/VERIFICATION.md` | generic | P1 | docs-only allowed commands와 future implementation commands가 별도 section으로 구분됨 |
| downstream closeout template | closeout 요구가 여러 문서에서 조금씩 다름 | downstream docs-only closeout format 표준화 | `templates/downstream_readiness/CLOSEOUT.md` | generic | P1 | files, commands, NOT RUN, safety checks, risks, next phase 포함 |
| C# desktop profile bridge | Scenario pilot에는 C# WPF/MVVM 문맥이 있음 | generic readiness와 `csharp_desktop` profile 연결 지점 정의 | `profiles/csharp_desktop/README.md` 또는 profile note | profile-specific | P2 | C# implementation phase는 별도 승인이라는 profile note 포함 |
| Scenario pilot record | Scenario-specific 관찰이 generic으로 섞일 위험 | pilot-specific note를 별도 보관 | `docs/pilots/SCENARIO_SIMULATOR_READINESS_PILOT.md` | scenario-specific | P1 | reusable / scenario-specific / deferred 항목 분류 기록 |
| scanner/checklist companion | scanner는 missing docs는 잡지만 generated docs 품질은 평가하지 않음 | scanner는 단순 유지, companion checklist 또는 validator 후보 분리 | `docs/AI_READINESS_SCANNER_v0.md`, future checklist doc | generic | P2 | scanner v0 read-only/simple principle 유지, quality review는 checklist로 분리 |

## 4. P0 / P1 / P2 우선순위

### P0

- downstream readiness template pack
- readiness baseline prompt template
- generated docs before staging review checklist
- acceptance trace status vocabulary
- safety pattern path-only check recipe
- policy wording interpretation rule
- no-touch zone generic/repo-specific split
- allowed file list guard

### P1

- NOT RUN honesty reusable block
- branch/path staleness checklist
- docs-only / implementation verification split
- downstream closeout template
- Scenario pilot record

### P2

- scanner/checklist companion improvement
- C# desktop profile bridge
- optional checklist validator script

## 5. template 후보

후보 template pack:

```text
templates/downstream_readiness/SAFETY_POLICY.md
templates/downstream_readiness/ACCEPTANCE_TRACE.md
templates/downstream_readiness/VERIFICATION.md
templates/downstream_readiness/AI_HANDOFF.md
templates/downstream_readiness/STATUS_UPDATE.md
templates/downstream_readiness/AGENTS_UPDATE.md
templates/downstream_readiness/CODEX_WORKFLOW_UPDATE.md
```

필수 placeholder 후보:

```text
{{REPO_NAME}}
{{REPO_PURPOSE}}
{{CURRENT_PHASE}}
{{ALLOWED_FILES}}
{{FORBIDDEN_IMPLEMENTATION_ITEMS}}
{{GENERIC_NO_TOUCH_ZONES}}
{{REPO_SPECIFIC_NO_TOUCH_ZONES}}
{{ALLOWED_VERIFICATION_COMMANDS}}
{{FORBIDDEN_COMMAND_CLASSES}}
{{SYNTHETIC_FIXTURE_POLICY}}
{{CLOSEOUT_REQUIREMENTS}}
```

`{{WORKING_BRANCH}}`와 local path placeholder는 optional이어야 한다. 장기 문서에
고정하면 stale risk가 있으므로 manifest 또는 closeout에서 확인하는 편이 안전하다.

## 6. prompt 후보

`docs/prompts/downstream_readiness_baseline.md` 후보가 필요하다.

Prompt가 받아야 할 입력:

- target repo path
- current branch
- source remote
- allowed files
- known existing docs
- missing readiness docs
- forbidden implementation items
- repo-specific no-touch zones
- generic no-touch zones
- verification commands allowed
- pattern check scope
- closeout requirements

Prompt가 강제해야 할 출력:

- docs-only changes only
- allowed files only
- no generated artifacts
- no private values
- no build/test/package/hook/release/workflow commands
- safety pattern checks are path-only
- stop conditions before editing
- closeout with ready-to-stage status

## 7. review checklist 후보

`docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md` 후보 항목:

- changed files are a subset of approved files
- required readiness docs exist
- acceptance trace status values are valid
- no `Planned` status remains for already-created evidence unless intentionally deferred
- no branch/path stale risk in long-lived docs
- no value-printing safety check command
- safety pattern matches are classified as policy wording or possible private value
- generic and repo-specific no-touch zones are separated
- NOT RUN rule is present
- implementation out-of-scope block is present
- build/test/package/hook/release/workflow commands were not run unless approved
- push/PR was not performed unless approved
- closeout reports line-ending warnings if present

## 8. scanner/checklist 개선 후보

Scanner v0는 계속 local-first, read-only, path/doc-surface 기반으로 유지한다.
Pilot에서 확인된 품질 문제는 scanner 자체에 모두 넣기보다 checklist로 분리하는 편이
안전하다.

후보 개선:

- scanner output에 “generated docs review checklist required before staging” 안내 추가
- optional checklist document로 stale branch/path, status vocabulary, allowed file list를 검토
- future validator script는 P2 이후 별도 승인으로 고려
- `quality_gate.py` 통합은 보류
- CI/workflow 통합은 보류

## 9. Scenario-specific으로 남길 항목

다음 항목은 generic template에 직접 넣지 않는다.

```text
N3G Scenario Simulator
RSID communication
WPF/MVVM shell
ScenarioStep
Excel parser
XML serialization
simulation engine
P0.5 / P1 / P2 phase naming
C:\Users\KSLV-II\codex_projects\ScenarioSimulator
Obsidian specific folder paths
codex/scenario-readiness-docs fixed branch
```

이 항목들은 pilot note 또는 repo-specific placeholder example로만 남긴다.

## 10. 다음 implementation phase 분해안

작게 나눈 docs-only implementation phase:

1. P0-A: `docs/DOWNSTREAM_READINESS_REVIEW_CHECKLIST.md` 추가
2. P0-B: `docs/ACCEPTANCE_TRACE_STATUS_VOCABULARY.md` 추가
3. P0-C: `docs/SAFETY_PATTERN_CHECKS.md` 추가
4. P0-D: `docs/prompts/downstream_readiness_baseline.md` 추가
5. P0-E: `templates/downstream_readiness/` template pack 초안 추가
6. P1-A: reusable `NOT RUN` snippet과 downstream closeout template 추가
7. P1-B: Scenario pilot record 추가
8. P2-A: scanner spec에 checklist companion 방향만 문서화
9. P2-B: optional validator script 여부 결정

각 phase는 downstream repository를 수정하지 않고 `codex-dev-harness` 내부 docs/templates만
변경해야 한다.
