# Local RAG Post-Rebaseline Retrieval Verification

## 1. Purpose

Record Phase 7C.3F post-rebaseline real-repository retrieval verification
after the approved Phase 6H.3 stable corpus digest re-baseline and Phase 6H.4
documentation closeout.

This review checks whether durable and historical retrieval queries no longer
receive `STATUS.md` or `ACCEPTANCE_TRACE.md` as stable digest citations, while
current-state and mixed-context queries may still use those files through the
committed-HEAD volatile overlay.

## 2. Scope

In scope:

- read-only digest check;
- read-only real-repository retriever query matrix;
- stable digest membership review;
- volatile overlay behavior review;
- documentation-only evidence capture.

Out of scope:

- no digest write or refresh;
- no `artifacts/corpus-digest.json` regeneration;
- no retriever runtime or test change;
- no quality-gate or CI integration;
- no release automation;
- no audit automation or receipt generation;
- no persistent index, `corpus/`, `retrieval/`, or `index/` directory;
- no embeddings, vector database, external service, MCP/Hermes, AgentOps, or
  memory runtime;
- no downstream access or downstream edit;
- no private/raw corpus ingestion.

## 3. Repository Basis

| item | value |
|---|---|
| branch | `main` |
| reviewed HEAD | `54c1d755988dd6d5fe6d7e23a3c304705ab4a5c4` |
| HEAD message | `Record Phase 6H.4 documentation closeout` |
| branch relationship before review | `main...origin/main` |
| pre-existing tracked diff | none |
| pre-existing untracked files | none |
| previous clean Local Verify | run `27890704615`, job `82533579280` |

The previous clean Local Verify applies to the Phase 6H.4 documentation
closeout commit before this review document existed. Clean remote verification
for this review document is not run in this task.

## 4. Digest Check

Read-only digest check result:

| metric | value |
|---|---|
| mode | `check` |
| source count | `34` |
| valid | `34` |
| stale | `0` |
| missing | `0` |
| malformed | `0` |
| invalid UTF-8 | `0` |
| unsafe | `0` |
| refresh required | `false` |
| source-basis commit | `e35f4649dad430678980714c6827a63668b7b125` |
| RAG authorization status | `not_authorized` |
| release artifact status | `not_release_artifact_without_separate_approval` |

No digest write was run.

## 5. Stable Source Membership

Stable digest membership check:

| source | stable digest membership |
|---|---|
| `STATUS.md` | excluded |
| `ACCEPTANCE_TRACE.md` | excluded |
| `docs/LOCAL_RAG_DESIGN.md` | included |
| `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md` | included |
| `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md` | included |
| `docs/LOCAL_RAG_VOLATILE_OVERLAY_CONTRACT.md` | included |

This confirms the Phase 6H stable source-set decision is active in the current
artifact: volatile current-authority files are no longer stable digest sources.

## 6. Query Matrix

Representative read-only query results:

| query | status | query class | observed HEAD | top source paths | stable `STATUS` / trace citation |
|---|---|---|---|---|---|
| `current implementation sequence` | `found` | `current_state` | yes | `STATUS.md` [volatile]; `ACCEPTANCE_TRACE.md` [volatile]; `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` | no |
| `next recommended task` | `found` | `current_state` | yes | `STATUS.md` [volatile]; `ACCEPTANCE_TRACE.md` [volatile]; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/AUDIT_TRACE_SCHEMA.md` | no |
| `current approved corpus digest status` | `found` | `current_state` | yes | `STATUS.md` [volatile]; `ACCEPTANCE_TRACE.md` [volatile]; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/APPROVED_CORPUS_RAG_PLAN.md` | no |
| `Phase 6G approved corpus digest refresh` | `found` | `mixed_context` | yes | `STATUS.md` [volatile]; `ACCEPTANCE_TRACE.md` [volatile]; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/APPROVED_CORPUS_RAG_PLAN.md`; `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md` | no |
| `local verification commands` | `found` | `durable_policy` | no | `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/VERIFICATION.md`; `docs/AUDIT_TRACE_SCHEMA.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`; `docs/CI_POLICY.md` | no |
| `receipt redaction policy` | `found` | `durable_policy` | no | `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/AUDIT_RECEIPT_PILOT_REVIEW.md`; `docs/AUDIT_LOG_POLICY.md` | no |
| `safety policy` | `found` | `durable_policy` | no | `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/SAFETY_POLICY.md`; `docs/VERIFICATION.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` | no |
| `optional CI decision` | `found` | `historical_decision` | no | `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/EVAL_INTEGRATION_DECISION.md`; `docs/AI_HANDOFF.md` | no |
| `release history` | `found` | `historical_decision` | no | `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/RELEASE_RECORD_v0.1.0-rc1.md`; `docs/RELEASE_RECORD_v0.1.0-rc2.md`; `docs/RELEASE_RECORD_v0.1.0.md`; `docs/AI_HANDOFF.md` | no |
| `Phase 7C citation integrity` | `found` | `durable_policy` | no | `docs/LOCAL_RAG_VOLATILE_OVERLAY_CONTRACT.md`; `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/LOCAL_RAG_DESIGN.md`; `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md` | no |
| `CI` | `found` | `durable_policy` | no | `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/CI_POLICY.md`; `docs/EVAL_INTEGRATION_DECISION.md`; `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `docs/adr/ADR-0003-approval-gated-side-effect.md` | no |
| `qzjxvbn plmrtk` | `no_sufficient_evidence` | `durable_policy` | no | none | no |
| `08_Study raw notes` | `blocked` | `durable_policy` | no | none | no |
| `modify the release workflow` | `found` | `durable_policy` | no | `docs/AUDIT_TRACE_SCHEMA.md`; `docs/CI_POLICY.md`; `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`; `docs/VERIFICATION.md` | no |

Focused `--max-results 10` checks for durable and historical queries also
returned zero `STATUS.md` or `ACCEPTANCE_TRACE.md` citations.

## 7. Findings

1. The Phase 6H.3 stable corpus re-baseline resolved the stable-citation
   membership issue. `STATUS.md` and `ACCEPTANCE_TRACE.md` no longer appear as
   stable digest citations for durable or historical queries.

2. Current-state and mixed-context queries still use `STATUS.md` and
   `ACCEPTANCE_TRACE.md` through the committed-HEAD volatile overlay. Those
   citations include volatile metadata rather than digest `content_hash`
   metadata.

3. Digest integrity is intact. Check mode reports 34 valid sources, 0 stale
   sources, and `refresh_required=false`.

4. No-answer and blocked behavior remain intact. The synthetic no-match query
   returns `no_sufficient_evidence`, and the raw `08_Study` query is blocked.

5. Determinism remains intact for the repeated `current implementation
   sequence` query when comparing complete JSON output.

6. The short-token `CI` ranking issue remains. Historical optional-CI evidence
   still ranks above current CI policy for the `CI` query.

7. Durable-policy authority ranking remains imperfect. Some durable queries
   rank broad Local RAG authority-policy text above the narrower domain policy
   documents. This is a ranking/authority issue, not a stable volatile-file
   membership issue.

## 8. Decision

Decision: `phase_7c3f_pass_with_notes_ready_for_phase_7c4`.

Rationale:

- Phase 7C.3F successfully proves that durable and historical query paths no
  longer receive `STATUS.md` or `ACCEPTANCE_TRACE.md` as stable digest
  citations.
- Current-state and mixed-context behavior still preserves volatile current
  authority through committed HEAD.
- Remaining defects are the known Phase 7C.4 concerns: short-token collision,
  durable-policy authority ranking, and metadata/text ranking behavior.

## 9. Safety Checks

This review did not:

- modify `artifacts/corpus-digest.json`;
- run digest write mode;
- change retriever runtime or tests;
- add quality-gate or CI integration;
- create a persistent index or retrieval folder;
- regenerate release artifacts;
- access private/raw corpus material;
- write audit logs, receipts, or trace artifacts;
- push, tag, publish, upload, or release anything.

## 10. Commands Run

Environment:

- `python --version`: ENVIRONMENT BLOCKED by the known local Windows
  logon-session issue.
- Bundled Python runtime was used for digest and retrieval checks.

Read-only repository basis:

- `git status --short --branch`: `## main...origin/main`
- `git log -3 --oneline --decorate`
- `git diff --name-only`: no output
- `git ls-files --others --exclude-standard`: no output
- `git rev-parse HEAD`: `54c1d755988dd6d5fe6d7e23a3c304705ab4a5c4`

Digest and membership review:

- `python scripts/generate_corpus_digest.py --check --json`: PASS, 34 valid, 0
  stale, refresh required false.
- Digest membership spot check: 34 sources, `STATUS.md` absent,
  `ACCEPTANCE_TRACE.md` absent, four normative Local RAG policy/contract
  sources present.

Retrieval review:

- `python scripts/local_rag_retriever.py --query ... --max-results 5 --json`
  for the query matrix in section 6.
- Focused `--max-results 10` checks for durable and historical queries:
  PASS, zero `STATUS.md` or `ACCEPTANCE_TRACE.md` citations.
- Repeated `current implementation sequence` output comparison: PASS.

## 11. Next Step

Immediate next step:

Commit and push this review-evidence document together with the narrow status
and acceptance-trace closeout rows, then run clean Local Verify for the
document-containing commit.

Next separately approved implementation task:

Phase 7C.4 Minimal Retriever Logic Correction for the remaining `CI`
short-token collision, durable-policy authority ranking, and metadata/text
ranking behavior. Do not add embeddings, vector search, external services,
quality-gate integration, CI integration, release automation, or downstream
integration in that task.
