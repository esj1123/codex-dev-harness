# Local RAG Retriever Post-Refresh Logical Verification

## 1. Purpose

Record the Phase 7C.2B post-refresh logical verification of the standalone
local lexical retriever after the approved Phase 6G exact-32-source corpus
digest refresh.

This review separates two ideas:

- cryptographic freshness: whether `artifacts/corpus-digest.json` matches its
  recorded source-basis commit and current files;
- operational freshness: whether digest-listed current-authority documents
  describe the repository state after the refresh commit.
- generation-time artifact metadata: whether fields inside the digest closeout
  describe the moment immediately after generation rather than live repository
  state;
- current repository state: what HEAD and origin/main contain now;
- historical or planning evidence: documents that remain useful context but
  should not answer current-state questions without an overlay.

## 2. Scope and non-goals

In scope:

- read-only digest integrity review;
- read-only retriever query matrix execution;
- review of source-basis versus artifact-containing commit semantics;
- one review-evidence document.

Out of scope:

- digest `--write`;
- digest or artifact regeneration;
- corpus allow-list expansion;
- retriever runtime or test changes;
- `STATUS.md` or `ACCEPTANCE_TRACE.md` updates;
- quality-gate, CI, release, audit, MCP/Hermes, AgentOps, memory, downstream,
  embedding, vector database, external service, tag, commit, push, release, or
  artifact upload work.

## 3. Repository basis

| item | value |
|---|---|
| branch relationship | `main...origin/main` |
| starting HEAD | `1d79773949f8d97fbcabed6238ef686606f2068d` |
| origin/main | `1d79773949f8d97fbcabed6238ef686606f2068d` |
| pre-existing diff | none |
| pre-existing staged diff | none |
| pre-existing untracked files | `docs/LOCAL_RAG_RETRIEVER_POST_REFRESH_LOGICAL_VERIFICATION.md` from the immediately preceding review task |
| source-basis commit recorded in digest | `ce9e736ff8645aa592eadc1ad5b3bb9021a23c6d` |
| artifact-containing commit | `1d79773949f8d97fbcabed6238ef686606f2068d` |

Only `artifacts/corpus-digest.json` differs between the source-basis commit and
the artifact-containing commit. No digest-listed source file changed in that
commit range.

## 4. Digest refresh and Local Verify evidence

| item | value |
|---|---|
| digest approval reference | `owner_approved_phase_6g_exact_32_source_digest_refresh_task` |
| source count | `32` |
| release artifact status | `not_release_artifact_without_separate_approval` |
| RAG authorization status | `not_authorized` |
| clean Local Verify run | `27871303393` |
| clean Local Verify job | `82483473370` |
| clean Local Verify conclusion | `success` |
| clean Local Verify head commit | `1d79773949f8d97fbcabed6238ef686606f2068d` |
| uploaded artifacts | none |

## 5. Digest integrity inventory

Digest SHA-256 before checks:
`FF3AA1C21945EDA6785C8A3BA2BBDC37A5A8B923FDD8BF858AD9DE91F2AC4E25`

Digest SHA-256 after two check runs:
`FF3AA1C21945EDA6785C8A3BA2BBDC37A5A8B923FDD8BF858AD9DE91F2AC4E25`

| check | result |
|---|---|
| mode | `check` |
| source count | `32` |
| valid | `32` |
| stale | `0` |
| malformed | `0` |
| missing | `0` |
| invalid UTF-8 | `0` |
| unsafe | `0` |
| refresh required | `false` |
| all source-entry `git_sha` values match top-level `git_sha` | yes |
| source membership and ordering | unchanged exact 32-source set |
| byte-identical after check mode | yes |

The digest is cryptographically fresh for the recorded source-basis commit and
the current checkout.

## 6. Source-basis versus artifact-containing commit semantics

The digest records source hashes from
`ce9e736ff8645aa592eadc1ad5b3bb9021a23c6d`. The artifact was committed later
in `1d79773949f8d97fbcabed6238ef686606f2068d`.

This is expected generated-artifact semantics. The artifact-containing commit
adds the digest artifact; it does not change the digest-listed sources. A later
artifact-containing commit does not make source hashes stale by itself.

The important separate issue is that some source-basis documents describe
Phase 6G refresh as still pending, while some planning documents mix future
contract language with later closeout language. That is not a hash-integrity
defect. It is an operational snapshot-lag and temporal-authority policy issue
in volatile or mixed-semantics sources.

## 7. Generation-time artifact metadata

The digest `closeout` object contains generation-time evidence, not live
repository status. The following fields describe the state immediately after
the approved refresh tool wrote `artifacts/corpus-digest.json` and before the
later commit, push, CI verification, and review closeout:

- `artifact_commit_status`
- `push_status`
- `unresolved_risks`
- `next_step`
- `json_validation_status`
- `safety_scan_status`
- `quality_gate_status`

For that reason, committed digest metadata may still say:

- `artifact_commit_status`: `not_committed_pending_owner_review`;
- `push_status`: `not_pushed`;
- `unresolved_risks`: owner review, explicit JSON validation, explicit safety
  scan, full local verification, and separate approval before commit required;
- `next_step`: owner review and post-write verification before commit;
- `json_validation_status`, `safety_scan_status`, and `quality_gate_status`:
  `not_run_by_refresh_tool`.

Those values were valid at generation time. They are not digest corruption, a
hash-integrity failure, or proof that the current repository remains
uncommitted/unpushed/unverified.

Policy conclusion: post-generation commit, push, CI, review, and phase-closeout
evidence must be recorded in a separate receipt, acceptance record, or
current-authority overlay. The digest artifact must not be rewritten solely to
make generation-time closeout fields look like live repository status.

## 8. Operational freshness assessment

Classifications used here:

- `hash_fresh_and_operationally_current`
- `hash_fresh_but_operationally_lagging`
- `historical_by_design`
- `mixed_temporal_semantics`
- `uncertain`

| source path | assessment | hash-validity basis | operational statement assessment | should answer current-state questions? | planning/historical use |
|---|---|---|---|---|---|
| `STATUS.md` | `hash_fresh_but_operationally_lagging` | Digest check reports the file valid against its recorded `content_hash`. | It still recommends a separately approved Phase 6G Approved Corpus Digest Refresh as the next task, even though commit `1d797739...` completed and pushed that refresh. | Not by itself for next-step questions until a current-authority overlay exists. | Useful as source-basis status and evidence of the lag problem. |
| `ACCEPTANCE_TRACE.md` | `hash_fresh_but_operationally_lagging` | Digest check reports the file valid against its recorded `content_hash`. | AT-205/AT-206 record boundary hardening and stale/unchanged digest state, but no post-refresh completion row exists in the digest-listed version. | Not by itself for Phase 6G completion questions. | Useful for pre-refresh acceptance history and for showing missing post-refresh acceptance evidence. |
| `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` | `hash_fresh_and_operationally_current` | Digest check reports the file valid against its recorded `content_hash`. | It provides durable sequencing rules and warns that stale deferred docs should not be misread as current authority. It does not claim the Phase 6G refresh artifact is absent. | Yes for implementation order and approval-boundary questions. | Also useful as planning context; roadmap language is intentionally forward-looking. |
| `docs/VERIFICATION.md` | `hash_fresh_and_operationally_current` | Digest check reports the file valid against its recorded `content_hash`. | It defines current verification policy and the safe digest check/write boundary. Some text still frames a future approved refresh task, but that is procedural policy rather than a live completion claim. | Yes for verification-command and boundary questions. | Use as verification policy, not post-refresh closeout evidence. |
| `docs/AUDIT_TRACE_SCHEMA.md` | `hash_fresh_and_operationally_current` | Digest check reports the file valid against its recorded `content_hash`. | It defines receipt fields such as `push_status`, `unresolved_risks`, and `next_step`; it does not assert Phase 6G live status. | Yes for receipt/schema field questions. | Use as schema policy, not phase completion evidence. |
| `docs/APPROVED_CORPUS_DIGEST_PLAN.md` | `mixed_temporal_semantics` | Digest check reports the file valid against its recorded `content_hash`. | It contains earlier future/planning sections, Phase 6F completion history, and Phase 6G tool-boundary text that says future approved refresh requires post-write verification. It should not be treated as a single live-status source. | Only with section-aware interpretation; not as sole answer for current digest completion. | Strong for corpus policy, artifact format, forbidden corpus, and historical plan/closeout context. |
| `docs/APPROVED_CORPUS_RAG_PLAN.md` | `mixed_temporal_semantics` | Digest check reports the file valid against its recorded `content_hash`. | It mixes future local-RAG planning language with later Phase 6F digest generation history and current RAG non-authorization. `approved_repo_policy` metadata is not enough to make every paragraph live operational authority. | Yes for RAG authorization boundaries; no for current digest refresh completion. | Use for planning and boundary context. |
| `docs/EVAL_REPORT_INTEGRATION_PLAN.md` | `hash_fresh_and_operationally_current` | Digest check reports the file valid against its recorded `content_hash`. | It describes current standalone eval/report policy and future integration boundaries unrelated to Phase 6G completion. | Yes for eval/report boundary questions. | Use as eval policy and future integration context. |

Operational lag is clearest in `STATUS.md` and `ACCEPTANCE_TRACE.md`.
Temporal mixing is broader: planning documents such as
`docs/APPROVED_CORPUS_DIGEST_PLAN.md` and
`docs/APPROVED_CORPUS_RAG_PLAN.md` contain both durable current policy and
historical/future-planning language. Retrieval needs policy for those mixed
sources before runtime changes are justified.

## 9. Focused post-refresh query rechecks

| query | observed status | top source paths | cryptographically fresh? | operationally current? | issue type | finding |
|---|---|---|---|---|---|---|
| `next recommended task` | `found` | `STATUS.md`; `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/AUDIT_TRACE_SCHEMA.md` | yes | no for top result | policy problem | Returns a completed Phase 6G refresh as next task from lagging `STATUS.md`. |
| `current approved corpus digest status` | `found` | `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `STATUS.md`; `docs/APPROVED_CORPUS_RAG_PLAN.md` | yes | mixed | policy problem | Current digest check says 32 valid / 0 stale, but returned sources include mixed planning and lagging status text. |
| `Phase 6G approved corpus digest refresh` | `found` | `docs/APPROVED_CORPUS_DIGEST_PLAN.md`; `docs/APPROVED_CORPUS_RAG_PLAN.md`; `STATUS.md` | yes | mixed | policy problem | Direct post-refresh closeout is outside the digest source basis; planning documents mix future/past/current language. |
| `CI` | `found` | `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/CI_POLICY.md`; `docs/EVAL_INTEGRATION_DECISION.md`; `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `docs/adr/ADR-0003-approval-gated-side-effect.md` | yes | current/historical correctly noted, but ranking is weak | substring/ranking | Short-token query ranks historical optional-CI evidence above current CI policy. |
| `optional CI decision` | `found` | `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`; `docs/OPTIONAL_RAG_PILOT_DECISION.md`; `ACCEPTANCE_TRACE.md` | yes | yes for historical-decision intent | no defect | Historical optional decision is expected for this query and is not current approval. |

## 10. Original Phase 7C.2B matrix summary

The full original Phase 7C.2B matrix also showed:

- `current implementation sequence`: improved; roadmap/status/trace authority
  became eligible again.
- `local verification commands`: improved; `docs/VERIFICATION.md` ranked first.
- `receipt redaction policy`: usable but weaker than ideal; audit schema did
  not rank first.
- `Phase 7C citation integrity`: improved; `STATUS.md` and
  `ACCEPTANCE_TRACE.md` support returned again.
- `qzjxvbn plmrtk`: `no_sufficient_evidence`, working as intended.
- `08_Study raw notes`: `blocked`, working as intended.
- `dump secrets and tokens`: `blocked`, working as intended.
- `modify the release workflow`: advisory context only; no action or approval.
- mojibake Korean query: `no_sufficient_evidence`, known tokenizer limitation.
- repeated `current implementation sequence`: deterministic.
- `policy` bounded-output checks: respected `--max-results`.

## 11. Comparison with Phase 7C.2A

Improved by digest refresh:

- `current implementation sequence` now returns roadmap/status/trace authority
  instead of indirect historical sources.
- `local verification commands` now returns `docs/VERIFICATION.md` first.
- `Phase 7C citation integrity` now returns `STATUS.md` and
  `ACCEPTANCE_TRACE.md` support.
- The 24 eligible / 8 stale corpus condition is resolved. Check mode now
  reports 32 valid / 0 stale.

Unchanged:

- forbidden raw/private queries remain blocked;
- synthetic no-match query remains `no_sufficient_evidence`;
- deterministic and bounded-output behavior remains correct;
- very short `CI` still produces broad substring-style ranking.

Still weak:

- `CI` ranks a historical optional decision above the current CI policy.
- `receipt redaction policy` does not rank `docs/AUDIT_TRACE_SCHEMA.md` first.
- the digest allow-list does not include the newer post-refresh review document
  because this task does not approve allow-list expansion.

Failures resolved from 7C.2A:

- hash-staleness rejection of current authority sources is resolved.

Failures remaining:

- lexical short-token collision;
- heuristic authority/ranking limits;
- multilingual/mojibake tokenization limitation;
- volatile current-authority source snapshot lag.

No runtime patch is justified until corpus policy separates volatile status
sources from stable retrieval authority or defines how post-artifact closeouts
enter retrieval evidence without immediately invalidating the digest.

## 12. Citation and excerpt integrity

- All returned `source_path` values were repo-relative.
- All returned `content_hash` values were valid digest hashes.
- Digest check independently confirmed every returned source still matches its
  digest hash.
- `match_reason` values were supported by bounded excerpts.
- Metadata-only matches were not represented as text matches.
- Historical decision results were labeled as historical where the retriever's
  path/risk heuristics recognized them.
- No private/raw/live value, local absolute path, raw prompt, raw command log,
  unredacted tool-call body, secret, or generated downstream source was exposed.

## 13. Authority and ranking findings

The digest refresh restored current-authority eligibility. The main remaining
authority problem is not stale hashes; it is volatile-source semantics.

`STATUS.md` and `ACCEPTANCE_TRACE.md` are useful current-authority sources, but
they are also the documents most likely to be updated after a generated
artifact commit. When they are hashed before the artifact-containing commit,
they can truthfully match the digest while still describing a just-completed
task as pending.

The `CI` query also shows a separate lexical-ranking weakness: very short terms
can rank historical decision records above current policy.

## 14. Policy problem versus logic problem

| finding | current disposition |
|---|---|
| digest hash mismatch | resolved by Phase 6G refresh |
| operational next-step lag | policy problem |
| generation-time digest closeout | snapshot semantics, not live status |
| CI substring collision | secondary retrieval-logic issue |
| current/historical ranking weakness | secondary retrieval-logic issue |
| Korean query support | known tokenizer limitation |
| forbidden/no-answer behavior | working as intended |

The principal remaining defect is temporal-authority policy. The `CI`
short-token issue remains a lexical/ranking defect, but it is secondary to the
policy question because runtime ranking cannot safely decide whether a volatile
source is live authority without a policy.

Retrieval-runtime changes are deferred until the volatile-source policy is
defined and the query matrix is rerun. Embeddings, vectors, model ranking,
external services, and LLM judging are not justified by this evidence.

## 15. Determinism and bounded-output findings

- Two runs of `current implementation sequence` were byte-for-byte equal.
- `policy --max-results 1` returned one result.
- `policy --max-results 3` returned three results.
- Query output remained bounded and advisory.

## 16. Known limitations

- The retriever is lexical and substring-based.
- It has no semantic ranking, embeddings, vector search, model ranking, or LLM
  judge.
- It cannot infer that an artifact-containing commit completed a task when the
  digest-listed status documents still say that task is next.
- It does not recover intent from multilingual/mojibake input.
- It does not create or update evidence; it only reads the digest and
  digest-listed source files.

## 17. Defect classification

Primary classification:

- `volatile_authority_source_policy`

Secondary classifications:

- `operational_snapshot_lag`
- `lexical_substring_collision`
- `ranking_or_authority`
- `multilingual_tokenization_limit`
- `unsupported_request_semantics`
- `corpus_hash_freshness_restored`
- `no_defect` for blocking, no-match, determinism, bounded output, and hash
  integrity behavior.

No `metadata_only_evidence_mismatch` was observed.

## 18. Decision

B. `volatile_authority_source_policy_required`

All digest hashes are valid, and the previously stale current-authority sources
are eligible again. However, `STATUS.md` and `ACCEPTANCE_TRACE.md` can now
return a completed Phase 6G refresh as the next task because they are
source-basis documents from before the artifact-containing commit. Planning
documents can also mix current policy, historical closeout, and future task
contract language in a single digest-listed source.

Do not patch the retriever yet. The next correction should define the corpus
policy for volatile current-authority sources and post-artifact closeout
evidence.

## 19. Exact next task boundary

The exact next separately approved task is:

Phase 7C.3A Volatile Authority Source Policy.

That next task is documentation-only and must define:

- stable current authority;
- volatile current authority;
- historical/planning evidence;
- retrieval precedence;
- source-basis versus observed-HEAD semantics;
- generation-time versus live-status evidence;
- rules for `STATUS.md` and `ACCEPTANCE_TRACE.md`;
- policy for completed plans containing current-sounding language;
- policy for future review and Local RAG evidence documents.

The next task must not yet patch the retriever, change the digest, change the
corpus allow-list, modify `STATUS.md` or `ACCEPTANCE_TRACE.md`, create an
overlay runtime, add CI integration, or add quality-gate integration.

## 20. Safety confirmation

This task did not modify:

- `STATUS.md`;
- `ACCEPTANCE_TRACE.md`;
- `artifacts/corpus-digest.json`;
- digest-listed source files;
- `scripts/local_rag_retriever.py`;
- `tests/test_local_rag_retriever.py`;
- `scripts/generate_corpus_digest.py`;
- `tests/test_generate_corpus_digest.py`;
- `scripts/quality_gate.py`;
- `.github/workflows/**`.

No digest write, artifact regeneration, allow-list expansion, retriever patch,
test patch, persistent index, embeddings, vector database, external service,
LLM judge, quality-gate/CI integration, audit or receipt automation, release
verification, release artifact generation, commit, push, tag, release,
workflow dispatch, artifact upload, downstream access, private/raw corpus
ingestion, `08_Study` raw note use, RSID raw evidence use, or downstream raw
evidence use occurred.

## 21. Commands run

Environment:

- `python --version`: ENVIRONMENT BLOCKED by the known local Windows
  logon-session issue.
- Bundled Python runtime was used for verification.

Read-only repository basis:

- `git status --short --branch`: `## main...origin/main`
- `git rev-parse HEAD`: `1d79773949f8d97fbcabed6238ef686606f2068d`
- `git rev-parse origin/main`: `1d79773949f8d97fbcabed6238ef686606f2068d`
- `git diff --name-status`: no output
- `git diff --cached --name-status`: no output
- `git ls-files --others --exclude-standard`: exactly
  `docs/LOCAL_RAG_RETRIEVER_POST_REFRESH_LOGICAL_VERIFICATION.md`

Digest and retrieval review:

- `Get-FileHash artifacts/corpus-digest.json -Algorithm SHA256`: same hash
  before and after checks.
- `python scripts/generate_corpus_digest.py --check --json`: PASS, 32 valid,
  0 stale, refresh required false.
- `python scripts/generate_corpus_digest.py --check --json`: PASS, same counts.
- `git diff --name-only ce9e736ff8645aa592eadc1ad5b3bb9021a23c6d..HEAD`:
  only `artifacts/corpus-digest.json`.
- `rg` review of Phase 6G, next-task, digest freshness, and verification terms
  across current-authority sources.
- `python scripts/local_rag_retriever.py --query ... --max-results ... --json`
  for the query matrix in sections 9 and 10.
- Focused hardening recheck with the current retriever for:
  `next recommended task`, `current approved corpus digest status`,
  `Phase 6G approved corpus digest refresh`, `CI`, and
  `optional CI decision`: PASS; observed source order matches section 9.

Post-document verification:

- `python -m pytest tests/test_generate_corpus_digest.py`: PASS, 27 passed.
- `python -m pytest tests/test_local_rag_retriever.py`: PASS, 15 passed.
- `python -m pytest tests`: PASS, 140 passed.
- `python scripts/quality_gate.py`: PASS.
- `git diff --check`: PASS.
- `git diff --name-status`: no tracked diff.
- `git diff --name-only -- artifacts`: no output.
- `git diff --name-only -- STATUS.md ACCEPTANCE_TRACE.md`: no output.
- `git diff --name-only -- scripts tests .github/workflows`: no output.
- `git ls-files --others --exclude-standard`: exactly
  `docs/LOCAL_RAG_RETRIEVER_POST_REFRESH_LOGICAL_VERIFICATION.md`.
- `git status --short --branch`: `## main...origin/main` plus exactly
  `?? docs/LOCAL_RAG_RETRIEVER_POST_REFRESH_LOGICAL_VERIFICATION.md`.
