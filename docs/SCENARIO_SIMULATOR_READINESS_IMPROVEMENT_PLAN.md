# ScenarioSimulator readiness improvement plan

## 1. 결론

`C:\Users\KSLV-II\codex_projects\ScenarioSimulator`는
`AI_Readiness_Scanner_v0`의 첫 pilot 적용 대상이다. 이 문서는
ScenarioSimulator를 기준으로 범용 표준을 새로 정의하려는 문서가 아니다.
범용 AI readiness framework의 소유 위치는 `codex-dev-harness`이며,
ScenarioSimulator에서 나온 관찰 결과는 검토 없이 universal rule로 승격하면 안 된다.

ScenarioSimulator scan 결과는 11/16, `LIMITED_AI_ASSISTED_WORK_ALLOWED`였다.
다음 ScenarioSimulator 작업은 docs-only readiness improvement가 되어야 한다.
목적은 product feature 구현이 아니라 안전 경계, evidence discipline, 검증 표면,
handoff 기준을 보강하는 것이다.

WPF/MVVM shell, `ScenarioStep`, Excel parser, XML serialization, simulation engine,
RSID communication 같은 구현 작업은 이번 계획의 범위 밖이다. 이 계획은 현재
codex-dev-harness repository에 작성한 harness-side plan이며, ScenarioSimulator
repository에는 어떤 파일도 생성하거나 수정하지 않았다.

## 범용 체계와 파일럿 적용의 구분

`codex-dev-harness`가 범용 AI readiness framework를 소유한다.
`ScenarioSimulator`는 그 framework를 적용해 보는 첫 pilot application이다.
ScenarioSimulator에서 발견한 항목은 자동으로 universal rule이 되지 않는다.
공통 구조는 review를 거쳐 template 후보가 될 수 있지만, Scenario-specific 내용은
명확하게 ScenarioSimulator 전용으로 표시해야 한다.

| 항목 | 범용 readiness 구조 | ScenarioSimulator 전용 적용 | template 후보 여부 |
|---|---|---|---|
| Safety policy | read-only boundary, forbidden data/actions, no live mutation | RSID/device/network/live target 금지 범위 명시 | 구조는 후보, RSID 내용은 전용 |
| Acceptance trace | requirement, evidence, verification, status, closeout 연결 | P1 shell readiness와 ScenarioSimulator evidence 연결 | 구조는 후보 |
| Verification | local-only command, NOT RUN, forbidden commands 분리 | WPF/MVVM 관련 검증 명령은 후속 승인 후 정의 | 구조는 후보, 명령은 전용 |
| AI handoff | next worker read order, risks, boundaries, closeout format | ScenarioSimulator phase와 Git dubious ownership note 포함 | 구조는 후보, 경로/Git note는 전용 |
| Status / phase gate | phase, allowed work, blocked work, next decision | P1 WPF/MVVM shell 착수 조건 정의 | 구조는 후보, phase명은 전용 |
| No-touch zones | secrets, private data, live systems, generated artifacts 금지 | RSID UDP/network/device action, local path boundary | 구조는 후보, RSID action은 전용 |
| Synthetic fixture policy | private data 대신 dummy fixture 사용 | scenario/sample data를 synthetic-only로 제한 | 후보 |
| Closeout receipt | changed files, commands, verification, safety, risks, next step | ScenarioSimulator docs-only closeout 항목에 적용 | 후보 |

## Template 후보와 보류 항목

### A. Generic template candidates

- safety boundary structure
- acceptance trace structure
- verification command structure
- AI handoff closeout structure
- no-touch zone declaration
- NOT RUN honesty rule
- synthetic fixture policy

### B. Scenario-specific content

- RSID/device/live target boundary
- C# WPF/MVVM phase gate
- `ScenarioStep` / simulation engine phase naming
- forbidden RSID UDP/network/device actions
- ScenarioSimulator local path notes
- Git dubious ownership note

### C. Deferred items

- template generator
- render integration
- `quality_gate.py` integration
- CI workflow
- RAG/index/embedding
- automatic cross-repo standardization

## 표준 승격 조건

공통 구조는 ScenarioSimulator 하나만 근거로 범용 template에 승격하지 않는다.
최소 한두 개 이상의 추가 repository를 review한 뒤 공통성과 예외를 분리해야 한다.
후보 review 대상은 예를 들어 `RSID-Inspection`, `outlook-history-view`, `stock`,
또는 다른 C# / Python repository가 될 수 있다.

이 문장은 해당 repository들의 scan이나 modification이 이미 승인되었다는 뜻이 아니다.
각 repository에 대한 path 확인, read-only scan, 문서 변경, 구현 변경은 모두 별도
명시 승인이 필요하다.

## 2. 현재 readiness 결과 요약

AI readiness scan 결과:

| 항목 | 결과 |
|---|---|
| 대상 경로 | `C:\Users\KSLV-II\codex_projects\ScenarioSimulator` |
| 점수 | 11/16 |
| 판정 | `LIMITED_AI_ASSISTED_WORK_ALLOWED` |
| 부족 증거 | safety boundary, acceptance/evidence discipline |
| partial 증거 | verification script |

확인된 안전한 root/doc 문서 표면:

- `README.md`
- `AGENTS.md`
- `STATUS.md`
- `docs/CODEX_WORKFLOW.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/HARNESS.md`
- `docs/SECRETS_RULES.md`

확인되지 않은 readiness 핵심 문서:

- `ACCEPTANCE_TRACE.md`
- `docs/VERIFICATION.md`
- `docs/SAFETY_POLICY.md`
- `docs/AI_HANDOFF.md`

이전 경로 확인 단계에서 Git dubious ownership 경고가 관찰되었으므로,
ScenarioSimulator에서 Git 작업이 필요하면 별도 승인과 권한 판단이 먼저 필요하다.
이 계획 단계에서는 ScenarioSimulator 내부 Git 명령을 실행하지 않았고,
`safe.directory`를 추가하지 않았다.

## 3. 부족 항목

### Safety boundary

안전 경계가 독립 문서로 확인되지 않는다. 현재 문서 일부에 safety, no-touch,
secrets 관련 문구가 있지만, AI-assisted work 전에 참조할 수 있는 명시적
`docs/SAFETY_POLICY.md` 또는 동등 문서가 필요하다.

### Acceptance / evidence discipline

`ACCEPTANCE_TRACE.md`가 확인되지 않는다. P1 작업을 작은 batch로 진행하려면
요구사항, evidence, 검증 명령, closeout 결과를 연결하는 trace 문서가 필요하다.

### Verification script

검증 스크립트 이름은 확인되지만 readiness scanner 기준으로는 partial이다.
Codex 작업자가 실행 가능한 검증 명령, 실행 금지 명령, 실패 시 보고 방식,
NOT RUN 표기 규칙을 분리해서 명시해야 한다.

### Risk flags

감지된 conservative risk flags:

- `RSID`
- `CREDENTIALS_SECRETS`
- `GENERATED_ARTIFACTS`
- `EXTERNAL_SERVICES`
- `CI_RELEASE_DEPLOY`

이 플래그들은 자동 실패가 아니라 후속 작업 전 검토 지표다. 다만 RSID, 외부
서비스, release/deploy 관련 단어가 함께 존재하므로 live target, 장비값,
network, credential, customer data, Obsidian vault 경계를 더 엄격히 정의해야 한다.

## 4. 문서-only 보강 제안

ScenarioSimulator repository에서 후속 phase로 고려할 문서-only 변경:

1. `docs/SAFETY_POLICY.md` 추가 또는 동등 문서 보강
   - live RSID, device, network, broker, Outlook, vault, external service mutation 금지.
   - IP, port, equipment value, credential, token, customer data, mail body, private source
     출력 금지.
   - suspicious finding은 matched value 없이 path와 finding type만 기록.
   - symlink, `.git`, `.venv`, `node_modules`, `bin`, `obj`, `artifacts`, `raw`,
     `processed`, `exports`, `logs`, `attachments`, private/local/vault 폴더 기본 제외.

2. `ACCEPTANCE_TRACE.md` 추가
   - P1 WPF/MVVM shell의 acceptance item, evidence source, verification command,
     status, closeout note를 연결.
   - 구현 전 문서-only readiness 항목과 구현 후 smoke evidence를 분리.
   - NOT RUN 원칙을 포함해 실행하지 않은 검증을 성공처럼 쓰지 않도록 명시.

3. `docs/VERIFICATION.md` 추가 또는 검증 문서 보강
   - local-only 검증 명령을 명시.
   - build/test/package/release 명령 중 Codex가 자동 실행하면 안 되는 명령을 분리.
   - generated artifact 위치와 commit 여부 정책을 명확히 함.
   - Git dubious ownership 상태에서는 Git 명령을 실행하지 않는다는 조건을 기록.

4. `docs/AI_HANDOFF.md` 추가
   - 다음 AI/Codex worker가 읽을 순서, 현재 phase, no-touch zone, 검증 명령,
     risk flags, closeout format을 요약.
   - scanner 결과가 write authorization이 아니라는 점을 명시.

5. No-touch zone 보강
   - live RSID endpoint, device/network operation, production configuration,
     Obsidian vault, customer/private input, credentials, generated release artifacts,
     external service calls를 별도 금지 영역으로 문서화.

6. Synthetic fixture policy 추가
   - 테스트와 예시는 synthetic fixture만 사용.
   - 실제 장비값, 내부 설계 원문, live config, 고객 데이터, private source를 fixture로
     복사하지 않음.
   - fixture 이름과 값은 안전한 dummy data만 사용.

7. P1 WPF/MVVM shell phase gate 정의
   - P1 착수 전 safety policy, acceptance trace, verification command, closeout
     receipt 요구사항이 준비되어야 함.
   - P1은 shell, navigation, view-model skeleton, synthetic data boundary만 허용하고
     live RSID/device/network 연결은 금지.

8. Closeout receipt 요구사항 추가
   - 변경 파일, 실행 명령, 검증 결과, NOT RUN 항목, 안전 체크, 위험과 가정,
     다음 작업을 매번 기록.

이 제안들은 ScenarioSimulator 적용안이다. 공통 구조는 향후 review를 통해
`codex-dev-harness` template 후보로 검토할 수 있지만, Scenario-specific 내용은
그대로 범용 표준에 편입하지 않는다.

## 5. 우선순위

1. `docs/SAFETY_POLICY.md` 또는 동등 안전 경계 문서 작성.
2. `ACCEPTANCE_TRACE.md` 작성.
3. `docs/VERIFICATION.md` 작성 또는 검증 표면 명확화.
4. `docs/AI_HANDOFF.md` 작성.
5. P1 WPF/MVVM shell phase gate와 synthetic fixture policy를 위 문서에 연결.
6. readiness scanner를 다시 읽기 전용으로 실행해 13/16 이상 readiness를 확인.

## 6. Codex 작업 전 안전경계

ScenarioSimulator에서 Codex 작업을 시작하기 전 기본 경계:

- Git dubious ownership 상태에서는 별도 승인 전 Git 명령을 실행하지 않는다.
- live RSID, device, PLC, network, broker, Outlook, vault, external service에 대한
  쓰기, 전송, 연결, release, deploy, workflow 실행을 금지한다.
- credentials, tokens, IPs, ports, account numbers, customer data, mail body,
  equipment values, live configuration, private source excerpts를 출력하거나 문서에
  복사하지 않는다.
- target repository scripts, builds, tests, package managers, hooks, releases,
  workflows는 명시 승인 전 실행하지 않는다.
- scanner 결과는 write authorization이 아니며, implementation scope는 별도 task
  contract로 승인해야 한다.

## 7. 구현 착수 전 완료 조건

P1 WPF/MVVM shell 구현을 시작하기 전 완료 조건:

- 안전 정책 또는 동등 문서가 존재한다.
- acceptance trace가 존재하고 P1 acceptance item을 추적한다.
- 검증 문서가 local-only command, 금지 command, NOT RUN 규칙을 명시한다.
- no-touch zone에 live RSID/device/network/external service/vault/customer/private
  data boundary가 포함된다.
- synthetic fixture policy가 명시된다.
- closeout receipt 형식이 정의된다.
- Git dubious ownership 처리 방침이 문서화되거나 Git 작업 없이 진행할 범위가
  명확하다.
- 후속 scanner run에서 부족 증거가 해소되었는지 확인한다.

## 8. 리스크 / 영향범위

- `RSID`: 실제 RSID, 장비값, live config와 혼동하지 않도록 synthetic boundary가
  필요하다.
- `CREDENTIALS_SECRETS`: secret policy는 있으나 후속 작업에서 값 출력과 fixture
  오염을 계속 방지해야 한다.
- `GENERATED_ARTIFACTS`: build/release 산출물 위치와 commit 정책이 불명확하면
  source와 artifact가 섞일 수 있다.
- `EXTERNAL_SERVICES`: API, MCP, network 관련 문서는 실제 호출과 문서 검토를
  분리해야 한다.
- `CI_RELEASE_DEPLOY`: CI, release, deploy는 별도 승인 전 설치하거나 실행하지
  않는다.
- Git dubious ownership: Git 명령이 필요한 phase에서는 권한/소유권 판단이 별도
  작업으로 필요하다.
- 표준 overfit: ScenarioSimulator 전용 제약을 범용 readiness rule로 승격하면
  다른 repository에 맞지 않는 표준이 될 수 있다.

## 9. 확인 필요 항목

- ScenarioSimulator에서 안전 정책 문서를 새로 만들지, 기존 AGENTS/CODEX workflow에
  통합할지.
- acceptance trace의 최소 항목과 P1 acceptance 기준.
- 공식 local verification command와 금지 command 목록.
- P1 WPF/MVVM shell에서 허용할 synthetic data 범위.
- RSID 관련 용어가 실제 live target 연결을 암시하지 않도록 하는 문서 문구.
- Git dubious ownership을 future Git 작업 전에 처리할지, 당분간 Git 없이
  read-only/doc-only 작업으로 제한할지.
- 후속 readiness scan을 언제 다시 실행할지.
- 어떤 구조를 `codex-dev-harness` generic template 후보로 검토할지.
