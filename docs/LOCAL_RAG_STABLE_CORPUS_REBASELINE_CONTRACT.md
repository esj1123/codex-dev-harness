# Local RAG Stable Corpus Re-baseline Contract

## 1. Purpose

Define the Phase 6H.1 stable corpus re-baseline decision and exact future
source-set contract for `artifacts/corpus-digest.json`.

This contract follows the proven Phase 7C.3D committed-HEAD volatile authority
overlay and the Phase 7C.3E real-repository overlay verification. It separates
future stable corpus membership from volatile current-state authority, tooling
changes, real artifact writes, and later lexical ranking correction.

## 2. Scope and non-goals

In scope:

- exact future stable digest membership and ordering;
- removal decision for volatile current-authority files;
- addition decision for durable normative Local RAG policy and contract files;
- rejected source-set alternatives;
- temporal and authority classifications;
- future digest metadata contract for the four added sources;
- future machine-readable source-set specification boundary;
- current tooling-gap analysis;
- future Phase 6H.2, 6H.3, 6H.4, 7C.3F, 7C.4, and 7D sequence.

Non-goals:

- no digest write;
- no digest refresh;
- no artifact regeneration;
- no source membership modification in the current artifact;
- no generator modification;
- no retriever modification;
- no test modification;
- no `STATUS.md` modification;
- no `ACCEPTANCE_TRACE.md` modification;
- no approved corpus plan modification;
- no allow-list expansion beyond this exact future 34-source contract;
- no review or probe document inclusion;
- no quality-gate integration;
- no workflow edit or dispatch;
- no release verification;
- no manifest, checksum, SBOM, or provenance regeneration;
- no `corpus/`, `retrieval/`, or `index/` directory;
- no embeddings, vector database, external service, or LLM judge;
- no audit or receipt automation;
- no MCP/Hermes, AgentOps, or memory runtime;
- no downstream access;
- no raw `08_Study` notes, RSID raw evidence, private/raw corpus material, or
  downstream raw evidence;
- no commit, push, tag, release, publication, or artifact upload.

## 3. Evidence basis

| item | value |
|---|---|
| repository | `esj1123/codex-dev-harness` |
| branch | `main` |
| starting HEAD | `215d17b39f8313f9d2575f74f2ba551d610912a0` |
| starting `origin/main` | `215d17b39f8313f9d2575f74f2ba551d610912a0` |
| HEAD message | `Document Phase 7C.3E real repo overlay verification` |
| Phase 7C.3D implementation commit | `366497c83b8bf776e9836c3203ca3e97eae8bb5d` |
| Phase 7C.3E review | `docs/LOCAL_RAG_REAL_REPO_OVERLAY_VERIFICATION.md` |
| Phase 7C.3E decision | `phase_6h_stable_corpus_rebaseline_required_before_phase_7c4` |
| stable digest | `artifacts/corpus-digest.json` |
| current stable source count | `32` |
| current digest source-basis commit | `ce9e736ff8645aa592eadc1ad5b3bb9021a23c6d` |
| Phase 7C.3E Local Verify | run `27876011181`, job `82495511195`, conclusion `success` |

The current digest is cryptographically valid for its existing 32-source set:
`source_count=32`, `valid=32`, `stale=0`, and `refresh_required=false`.

## 4. Current stable/volatile corpus problem

The committed-HEAD volatile overlay is working for current-state and
mixed-context queries. For those query classes, the retriever can cite
`STATUS.md` and `ACCEPTANCE_TRACE.md` from committed `HEAD` with
`observed_head_commit`, `volatile_content_hash`, `temporal_class`, and
`authority_level`.

However, `STATUS.md` and `ACCEPTANCE_TRACE.md` still exist in the stable
digest. Durable-policy and historical-decision queries intentionally avoid the
volatile overlay and prefer stable digest citations. Therefore, the two
volatile documents can still be returned as stable citations for non-current
queries.

This is a source-membership problem. It is not the known short-token `CI`
collision, and it is not a general lexical ranking defect. Phase 7C.4 lexical
or authority ranking correction must remain deferred until stable corpus
membership is corrected and verified.

This contract does not claim the current digest is stale. The current digest is
valid for its current 32-source membership.

## 5. Alternatives considered

| option | source-set change | assessment |
|---|---|---|
| Option A: minimal 30-source set | Remove `STATUS.md` and `ACCEPTANCE_TRACE.md`; add nothing. | Rejected. It removes volatile current state from the stable digest but omits current normative Local RAG policy from stable retrieval. |
| Option B: balanced 34-source set | Remove `STATUS.md` and `ACCEPTANCE_TRACE.md`; add four normative Local RAG documents. | Selected. It separates live state from durable policy while preserving a bounded source set. |
| Option C: broad evidence set | Remove volatile sources; add normative policy plus review, probe, and verification documents. | Rejected. It confuses stable policy with historical review evidence and increases corpus noise. |

## 6. Selected source-set decision

Selected decision: Option B, balanced 34-source set.

Remove from future stable digest:

- `STATUS.md`
- `ACCEPTANCE_TRACE.md`

Keep those files as volatile current authority only:

- committed-HEAD overlay;
- exact volatile allow-list only;
- not stable digest sources.

Add to future stable digest:

- `docs/LOCAL_RAG_DESIGN.md`
- `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md`
- `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`
- `docs/LOCAL_RAG_VOLATILE_OVERLAY_CONTRACT.md`

Do not add review, probe, logical-verification, policy-application, real-repo
verification, or Phase 6H.1 contract documents to the stable digest.

## Exact approved Phase 6H stable source set

The future ordered stable source list must be exactly:

1. AGENTS.md
2. README.md
3. docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md
4. docs/SAFETY_POLICY.md
5. docs/VERIFICATION.md
6. docs/CI_POLICY.md
7. docs/AUDIT_TRACE_SCHEMA.md
8. docs/AUDIT_LOG_POLICY.md
9. docs/APPROVED_CORPUS_DIGEST_PLAN.md
10. docs/APPROVED_CORPUS_RAG_PLAN.md
11. docs/LOCAL_RAG_DESIGN.md
12. docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md
13. docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md
14. docs/LOCAL_RAG_VOLATILE_OVERLAY_CONTRACT.md
15. docs/EVAL_REPORT_INTEGRATION_PLAN.md
16. docs/EVAL_POLICY.md
17. docs/EVAL_INTEGRATION_DECISION.md
18. docs/OPTIONAL_RAG_PILOT_DECISION.md
19. docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md
20. docs/AUDIT_RECEIPT_PILOT_REVIEW.md
21. docs/MINIMAL_EVAL_HARNESS_DESIGN.md
22. docs/AI_HANDOFF.md
23. docs/CHANGE_CONTROL.md
24. docs/HUMAN_APPROVALS.md
25. docs/PROMPT_PATTERNS.md
26. docs/adr/ADR-0001-local-first.md
27. docs/adr/ADR-0002-base-template-over-domain-profile.md
28. docs/adr/ADR-0003-approval-gated-side-effect.md
29. docs/RELEASE_RECORD_v0.1.0-rc1.md
30. docs/RELEASE_RECORD_v0.1.0-rc2.md
31. docs/RELEASE_RECORD_v0.1.0.md
32. docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc1.md
33. docs/CLEAN_CLONE_VALIDATION_v0.1.0-rc2.md
34. docs/CLEAN_CLONE_VALIDATION_v0.1.0.md

Rules:

- exact membership;
- exact ordering;
- no glob expansion;
- no filesystem discovery;
- no path aliases;
- no additional review documents;
- no `STATUS.md`;
- no `ACCEPTANCE_TRACE.md`;
- no generated artifacts;
- no private/raw, downstream, RSID, or `08_Study` source.

## 8. Current-to-future source-set diff

Source-set arithmetic:

| metric | value |
|---|---:|
| current count | 32 |
| retained count | 30 |
| removed count | 2 |
| added count | 4 |
| final count | 34 |
| duplicate count | 0 |
| missing candidate count | 0 |
| unsafe candidate count | 0 |

Removed:

- `STATUS.md`
- `ACCEPTANCE_TRACE.md`

Added:

- `docs/LOCAL_RAG_DESIGN.md`
- `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md`
- `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`
- `docs/LOCAL_RAG_VOLATILE_OVERLAY_CONTRACT.md`

Read-only validation confirms all 34 future sources:

- exist at current committed HEAD;
- are regular repo-owned files;
- are UTF-8 readable;
- use repo-relative POSIX paths;
- do not fall under forbidden path classes.

## 9. Temporal and authority classifications

| source class | temporal_class | authority_level | future layer | stable digest |
|---|---|---|---|---|
| `STATUS.md` | `volatile_current_authority` | `current_operational_state` | committed-HEAD volatile overlay | excluded |
| `ACCEPTANCE_TRACE.md` | `volatile_current_authority` | `current_operational_state` | committed-HEAD volatile overlay | excluded |
| `docs/LOCAL_RAG_DESIGN.md` | `stable_current_authority` | `supporting_policy` | stable digest | included |
| `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md` | `stable_current_authority` | `supporting_policy` | stable digest | included |
| `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md` | `stable_current_authority` | `durable_policy` | stable digest | included |
| `docs/LOCAL_RAG_VOLATILE_OVERLAY_CONTRACT.md` | `stable_current_authority` | `durable_policy` | stable digest | included |
| review and probe documents | `historical_planning_evidence` | `historical_context` | review or receipt evidence | excluded by this Phase 6H decision |
| generation-time fields inside artifacts | `generation_time_snapshot` | `non_authoritative_snapshot` | artifact metadata | not applicable |

Review/probe documents include usage probes, logical verification records,
post-refresh verification records, policy-application reviews, real-repository
overlay verification, and this Phase 6H.1 contract. They remain review or
receipt evidence, not stable digest sources.

## 10. Metadata contract for added sources

Future digest metadata for the four added sources:

| source_path | section_title | content_class | risk_label |
|---|---|---|---|
| `docs/LOCAL_RAG_DESIGN.md` | `Local RAG Design` | `corpus_planning` | `approved_repo_policy` |
| `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md` | `Local RAG Implementation Contract` | `repo_policy` | `approval_boundary` |
| `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md` | `Local RAG Volatile Authority Policy` | `repo_policy` | `approved_repo_policy` |
| `docs/LOCAL_RAG_VOLATILE_OVERLAY_CONTRACT.md` | `Local RAG Volatile Overlay Contract` | `repo_policy` | `approval_boundary` |

All future entries must retain:

- `allowed_for_digest`: `approved`;
- `allowed_for_release`: `not_release_without_separate_approval`;
- `redaction_status`: `metadata_hash_only_no_source_text`;
- `encoding_status`: `utf8_readable`;
- `digest_algorithm`: `sha256`;
- repo-relative `source_path`;
- normalized UTF-8 SHA-256 `content_hash`;
- source-basis `git_sha`;
- `verified_at`;
- `reviewer_or_approval_ref`;
- short safe notes only.

Do not compute or write new digest entries in Phase 6H.1.

## 11. Retained mixed-temporal sources

These sources remain in the future stable set:

- `docs/APPROVED_CORPUS_DIGEST_PLAN.md`
- `docs/APPROVED_CORPUS_RAG_PLAN.md`

They remain because they contain durable corpus and authorization policy.

Limitations:

- they are mixed-temporal evidence;
- they must not be the sole basis for live current-state answers;
- future retrieval may require section-aware authority handling;
- retaining them does not resolve the later ranking or section-authority task;
- Phase 7C.4 remains responsible only for minimal logic correction after
  re-baseline verification.

Do not remove them in Phase 6H.1.

## 12. Excluded review and probe evidence

The following classes remain excluded from the future stable digest:

- retriever usage probes;
- retriever logical verification documents;
- post-refresh logical verification documents;
- policy-application reviews;
- real-repository overlay verification reviews;
- Phase 6H.1 contract and closeout documents;
- any future review, receipt, or probe evidence unless separately approved.

Explicitly excluded examples:

- `docs/LOCAL_RAG_RETRIEVER_USAGE_PROBE.md`
- `docs/LOCAL_RAG_RETRIEVER_LOGICAL_VERIFICATION.md`
- `docs/LOCAL_RAG_RETRIEVER_POST_REFRESH_LOGICAL_VERIFICATION.md`
- `docs/LOCAL_RAG_POLICY_APPLICATION_REVIEW.md`
- `docs/LOCAL_RAG_REAL_REPO_OVERLAY_VERIFICATION.md`
- `docs/LOCAL_RAG_STABLE_CORPUS_REBASELINE_CONTRACT.md`

These documents may remain useful evidence. They must not become stable policy
corpus by implication.

## 13. Future source-set specification

Future digest `source_allow_list_ref`:

`docs/LOCAL_RAG_STABLE_CORPUS_REBASELINE_CONTRACT.md#exact-approved-phase-6h-stable-source-set`

This Phase 6H.1 contract is the human-readable approval boundary.

Future machine-readable ordered source-set specification:

`docs/APPROVED_CORPUS_SOURCE_SET.v2.json`

That JSON file must be created only in a separately approved Phase 6H.2 task.
It should contain:

- `schema_version`;
- `source_set_id`;
- `ordered_sources`;
- each `source_path`;
- `section_title`;
- `content_class`;
- `risk_label`;
- `temporal_class`;
- `authority_level`;
- `excluded_volatile_sources`;
- `expected_source_count`;
- `human_contract_ref`.

The future JSON source-set specification:

- must be canonical and deterministic;
- must not contain source bodies;
- must not contain local absolute paths;
- must not automatically discover files;
- must not itself be added to the stable digest unless separately approved.

Do not create this JSON file in Phase 6H.1.

## 14. Current tooling gap

The current digest tool:

- checks the current digest source entries;
- refreshes hashes and metadata for the existing source list;
- preserves existing source membership and ordering;
- does not perform approved source membership add, remove, or reorder
  re-baseline.

This gap is intentional. Refreshing hash metadata for the same source set is
not the same operation as approving a new stable corpus membership contract.

## 15. Future re-baseline tooling boundary

Next tool task:

Phase 6H.2 Re-baseline Tooling and Synthetic Tests.

That future task may:

- add a separate explicit re-baseline mode;
- read the approved machine-readable source-set specification;
- validate exact membership and ordering;
- preserve existing check and same-set refresh behavior;
- reject implicit discovery;
- reject unapproved source-set changes;
- use synthetic repositories for membership tests.

Recommended future CLI shape:

```text
python scripts/generate_corpus_digest.py \
  --rebaseline-spec docs/APPROVED_CORPUS_SOURCE_SET.v2.json \
  --write \
  --approval-ref <separate-owner-approval-ref> \
  --json
```

The exact CLI may be refined in Phase 6H.2, but it must:

- distinguish refresh from re-baseline;
- require explicit approval;
- restrict output to `artifacts/corpus-digest.json`;
- preserve clean source-basis checks;
- reject dirty source content;
- never infer source membership from the filesystem.

Do not modify the tool in Phase 6H.1.

## 16. Re-baseline verification requirements

Phase 6H.3 real digest re-baseline must be separately approved and must
include:

- exact artifact write authorization;
- JSON validation;
- independent hash verification;
- safety scan;
- focused digest-tool tests;
- focused retriever tests;
- full tests;
- quality gate;
- render dry-runs;
- artifact-only commit;
- clean Local Verify.

It must confirm:

- exact 34-source membership;
- exact ordering;
- no `STATUS.md`;
- no `ACCEPTANCE_TRACE.md`;
- no review or probe documents;
- no generated artifacts as sources;
- no private/raw, downstream, RSID, or `08_Study` material;
- no release artifact status change unless separately approved;
- no RAG authorization status change unless separately approved.

## 17. Future phase sequence

Phase 6H.1:

- exact source-set decision and contract;
- documentation only.

Single-file Phase 6H.1 closeout:

- commit and push the contract only;
- run clean Local Verify.

Phase 6H.2:

- create machine-readable exact source-set specification;
- add re-baseline tooling and synthetic tests;
- no real digest write.

Phase 6H.2 clean verification:

- commit and push approved tooling/spec files;
- run Local Verify.

Phase 6H.3:

- separately approved real 34-source digest re-baseline;
- exact artifact write authorization;
- JSON validation;
- independent hash verification;
- safety scan;
- focused and full tests;
- quality gate;
- render dry-runs;
- artifact-only commit;
- clean Local Verify.

Phase 6H.4:

- after `STATUS.md` and `ACCEPTANCE_TRACE.md` are no longer stable digest
  members, update them as volatile committed-HEAD closeout evidence;
- do not refresh the stable digest merely because volatile files changed.

Phase 7C.3F:

- post-rebaseline real-repository retrieval verification;
- prove durable and historical queries no longer receive `STATUS.md` or
  `ACCEPTANCE_TRACE.md` as stable citations.

Phase 7C.4:

- only then consider minimal lexical, token-boundary, or ranking correction;
- address the `CI` short-token collision;
- address durable-policy authority ranking;
- address metadata-only versus text-match handling.

Phase 7D:

- retrieval receipt evidence only after authority and ranking behavior are
  proven.

## 18. Safety and privacy boundaries

This contract does not authorize:

- digest write or refresh;
- artifact regeneration;
- runtime retrieval changes;
- source membership changes in the current artifact;
- quality-gate or CI integration;
- release verification or release evidence generation;
- audit or receipt automation;
- external services;
- downstream access;
- private/raw corpus ingestion.

Future stable corpus sources must not include raw prompts, prompt transcripts,
model outputs, raw command logs, unredacted tool-call bodies, secrets, account
values, IPs, ports, live config, device values, local absolute paths, generated
downstream source, RSID raw evidence, downstream raw evidence, or raw
`08_Study` notes.

## 19. Acceptance criteria

This Phase 6H.1 contract is acceptable when:

1. Starting state matches `215d17b39f8313f9d2575f74f2ba551d610912a0`.
2. Current digest remains `32` valid / `0` stale.
3. The future `34`-source set is exact and ordered.
4. Set arithmetic is `30` retained, `2` removed, `4` added.
5. `STATUS.md` and `ACCEPTANCE_TRACE.md` are overlay-only in the future
   design.
6. Four normative Local RAG documents are added to the stable set.
7. Review and probe documents remain excluded.
8. Metadata for all four new stable sources is explicit.
9. Mixed-temporal corpus/RAG plans are retained with limitations documented.
10. Future human-readable and machine-readable source-set contracts are
    defined.
11. The current refresh/re-baseline tooling gap is explicit.
12. The Phase 6H.2, 6H.3, 6H.4, 7C.3F, 7C.4, and 7D sequence is explicit.
13. No runtime, digest, source, test, or workflow change occurs.
14. Tests and quality gate pass.
15. Only this new contract document remains untracked.
16. No forbidden action occurs.

## 20. Exact next task

Immediate next step after owner review:

Commit and push only
`docs/LOCAL_RAG_STABLE_CORPUS_REBASELINE_CONTRACT.md`, then run clean Local
Verify.

Next separately approved implementation task:

Phase 6H.2 Re-baseline Tooling and Synthetic Tests.

Do not perform Phase 6H.2 in Phase 6H.1.

## 21. Commands run

Starting-state checks:

- `git status --short --branch`: `## main...origin/main`
- `git rev-parse HEAD`: `215d17b39f8313f9d2575f74f2ba551d610912a0`
- `git rev-parse origin/main`: `215d17b39f8313f9d2575f74f2ba551d610912a0`
- `git diff --name-status`: no output
- `git diff --cached --name-status`: no output
- `git ls-files --others --exclude-standard`: no output

Read-only pre-document checks:

- `python --version`: ENVIRONMENT BLOCKED by the local Windows logon-session
  issue.
- Bundled Python `scripts/generate_corpus_digest.py --check --json`: PASS,
  `source_count=32`, `valid=32`, `stale=0`, `refresh_required=false`.
- Bundled Python inline source-set validation: PASS, `current_count=32`,
  `retained_count=30`, `removed_count=2`, `added_count=4`,
  `final_count=34`, `duplicate_count=0`, `missing_candidate_count=0`,
  `unsafe_candidate_count=0`, `invalid_utf8_count=0`.

Post-document verification:

- Bundled Python `python -m pytest tests/test_generate_corpus_digest.py`:
  PASS, 27 passed.
- Bundled Python `python -m pytest tests/test_local_rag_retriever.py`:
  PASS, 34 passed.
- Bundled Python `python scripts/quality_gate.py`: PASS.
- Bundled Python `python -m pytest tests`: PASS, 159 passed.
- `git add --intent-to-add docs/LOCAL_RAG_STABLE_CORPUS_REBASELINE_CONTRACT.md`:
  PASS; used only for new-file diff verification.
- `git diff --check`: PASS WITH NOTES; LF/CRLF warning only.
- `git diff -- docs/LOCAL_RAG_STABLE_CORPUS_REBASELINE_CONTRACT.md`: PASS;
  reviewed as one new documentation file.
- `git reset -- docs/LOCAL_RAG_STABLE_CORPUS_REBASELINE_CONTRACT.md`: PASS;
  restored the file to untracked state.
- `git diff --name-status`: no tracked diff.
- `git diff --name-only -- artifacts`: no output.
- `git diff --name-only -- STATUS.md ACCEPTANCE_TRACE.md`: no output.
- `git diff --name-only -- scripts tests .github/workflows`: no output.
