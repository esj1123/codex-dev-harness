# AI Readiness Scanner v0

## Purpose

`AI_Readiness_Scanner_v0` is a standalone local-first scanner for checking
whether a repository is ready for AI-assisted work.

The scanner is intended to support future onboarding and review of repositories
such as:

- `codex-dev-harness`
- `Scenario-Simulator`
- `RSID-Inspection`
- `outlook-history-view`
- `stock`

The v0 scanner is read-only by design. Its job is to summarize readiness,
risks, missing governance surfaces, and next actions before an AI/Codex worker
starts implementation work.

Stage 5B may use scanner thinking for target-repo selection, but this document
does not execute a sibling-repository scan. The current Stage 5B handoff selects
`stock` as the first practical probe candidate and treats it as a broker/finance
risk target requiring stricter no-live-action boundaries.

## Non-goals

`AI_Readiness_Scanner_v0` does not include:

- product feature implementation
- application code generation
- live target writes
- PLC, device, RSID, Outlook, broker, or vault mutation
- CI workflow creation or installation
- RAG implementation
- vector databases, embeddings, model calls, or external service calls
- approval-free sibling repository scans

This document records scanner scope and boundaries. It does not authorize new
scanner code, generated reports, CI workflows, retrieval indexes, model tooling,
target writes, target command execution, or downstream implementation.

## Read-only boundary

The scanner may inspect safe repository metadata and selected policy documents.
It must default to local read-only behavior.

The scanner must not:

- modify the scanned target repository
- run target repository scripts, tests, package managers, hooks, builds, release
  commands, or deployment commands
- write files into the scanned target repository
- follow symlinks by default
- call external services or network APIs
- infer approval for future write work

If a later phase adds optional report output, the output path must be explicit
and must not be inside the scanned target repository unless separately
approved.

## Allowed inspection targets

The scanner may inspect these repository surfaces when they are present:

- `README.md`
- `AGENTS.md`
- `STATUS.md` or equivalent
- `ACCEPTANCE_TRACE.md`
- `docs/SAFETY_POLICY.md` or equivalent
- `docs/VERIFICATION.md` or equivalent
- local quality gate script names
- test or smoke script presence
- `.gitignore` presence
- safe path-level indicators only

The scanner may record whether expected files, directories, and script names
exist. It should prefer path-level and metadata-level evidence over file-content
excerpts.

## Forbidden inspection and output

The scanner must not inspect or print private raw source excerpts.

The scanner must not print:

- secrets, credentials, keys, or tokens
- account numbers
- email addresses or mail bodies
- IP addresses or ports
- equipment values, tags, device addresses, or live-control parameters
- live configuration
- broker data
- customer data
- private raw input

If a suspicious file or pattern is found, the scanner must report only the file
path and finding type. It must not include the matched value.

By default, the scanner must not scan:

- `.git`
- `.venv`
- `node_modules`
- `bin`
- `obj`
- `artifacts`
- `raw`
- `processed`
- `exports`
- `logs`
- `attachments`
- live vault folders
- known private folders

Future implementation may allow explicit safe include or exclude lists, but v0
must remain conservative.

## AI readiness score model

The v0 score is a 16-point model. Unknown evidence must be reported as
`INSUFFICIENT_EVIDENCE`, not guessed.

| dimension | points |
|---|---:|
| Purpose clarity | 0-2 |
| AI operating rules | 0-2 |
| Safety boundary | 0-2 |
| Verification script | 0-2 |
| Tests or smoke checks | 0-2 |
| Private data protection | 0-2 |
| Acceptance trace or evidence discipline | 0-2 |
| Next action clarity | 0-2 |

Score interpretation:

| score | result |
|---:|---|
| 13-16 | `READY_FOR_AI_ASSISTED_WORK` |
| 9-12 | `LIMITED_AI_ASSISTED_WORK_ALLOWED` |
| 5-8 | `NEEDS_DOCUMENTATION_OR_HARNESS_IMPROVEMENT` |
| 0-4 | `HOLD_BEFORE_AI_ASSISTED_WORK` |

Scoring should explain the evidence for each dimension. Missing or ambiguous
evidence should reduce confidence rather than be treated as a pass.

## Domain risk flags

The scanner should define conservative path- and keyword-based flags for:

- PLC, device, or live target
- Outlook or mail
- broker or finance
- vault or Obsidian
- RSID
- credentials or secrets
- generated artifacts
- external services
- CI, release, or deploy

These flags do not automatically block a repository. They require stricter
approval, clearer verification, and more explicit no-touch boundaries before
AI-assisted work proceeds.

## Report format

The user-facing report may be written in Korean. A v0 report should use this
template:

```markdown
# AI 준비도 점검 보고서

## 결론

- 판정:
- 총점:
- 요약:

## 근거

- 확인한 문서:
- 확인한 로컬 검증 표면:
- 확인한 안전 경계:

## 실행 체크리스트

- [ ] 읽기 전용 점검 완료
- [ ] 변경 금지 영역 확인
- [ ] 검증 명령 확인
- [ ] 다음 작업 범위 확인

## 리스크 / 영향범위

- 도메인 리스크 플래그:
- 외부 시스템 관련성:
- 민감 데이터 가능성:
- 승인 필요 작업:

## Repo 점수표

| 항목 | 점수 | 근거 | 상태 |
|---|---:|---|---|
| 목적 명확성 | 0-2 |  |  |
| AI 작업 규칙 | 0-2 |  |  |
| 안전 경계 | 0-2 |  |  |
| 검증 스크립트 | 0-2 |  |  |
| 테스트 또는 스모크 체크 | 0-2 |  |  |
| private data 보호 | 0-2 |  |  |
| acceptance trace / evidence discipline | 0-2 |  |  |
| 다음 작업 명확성 | 0-2 |  |  |

## 부족 항목

- 

## 다음 작업 우선순위

1. 
2. 
3. 

## 확인 필요 항목

- 
```

Reports must summarize evidence without copying sensitive values or private
source excerpts.

## Implementation status and future phases

Current status:

- `scripts/ai_readiness_scanner.py` exists as standalone local tooling.
- `tests/test_ai_readiness_scanner.py` exists and uses synthetic fixture
  repositories.
- Scanner output is stdout-only Markdown or JSON.
- The scanner is not wired into `scripts/quality_gate.py`, CI, release gates,
  RAG tooling, or model tooling.

Future phases remain approval-gated:

- optional local verification integration
- read-only scans of explicitly provided sibling repository paths
- optional generated reports outside the scanned target repository

Sibling repository scanning must be explicit, read-only, and path-specific.
Stage 5B target selection names `stock`, but does not itself run the scanner
against `stock`.

## Acceptance criteria for current scanner scope

- The spec exists.
- It clearly states read-only behavior.
- It defines score dimensions.
- It defines forbidden data and forbidden actions.
- It uses synthetic examples for tests.
- It preserves standalone operation.
- It does not authorize target writes or downstream implementation.
