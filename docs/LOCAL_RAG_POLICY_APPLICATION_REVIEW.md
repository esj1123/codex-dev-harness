# Local RAG Policy Application Review

## 1. Purpose

Record Phase 7C.3B Policy Application Review for the standalone local lexical
retriever.

This review applies `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md` manually to
the existing Phase 7C.2B query matrix. It does not run a new full logical query
matrix and does not change retriever behavior.

## 2. Scope and non-goals

In scope:

- review-only application of the volatile-authority policy;
- manual classification of existing Phase 7C.2B findings;
- separation of policy-resolved, metadata-required, ranking-required,
  token-boundary-required, and corpus-rebaseline-required issues;
- exact next task recommendation.

Out of scope:

- retriever runtime changes;
- retriever test changes;
- `artifacts/corpus-digest.json` refresh, regeneration, or allow-list change;
- `STATUS.md` or `ACCEPTANCE_TRACE.md` edits;
- workflow edits or CI integration;
- quality-gate integration;
- audit or receipt automation;
- release verification, tag, release, publication, or artifact upload;
- persistent index, `corpus/`, `retrieval/`, or `index/` directory;
- embeddings, vector database, external service, LLM judge, MCP/Hermes,
  AgentOps, or memory runtime;
- downstream access or downstream changes;
- private/raw corpus ingestion, `08_Study` raw notes, RSID raw evidence, or
  downstream raw evidence.

## 3. Evidence basis

| item | value |
|---|---|
| repository | `esj1123/codex-dev-harness` |
| branch | `main` |
| review starting HEAD | `96fdd0a182f26f01ff6d4dca76a57301df715fb2` |
| parent policy document | `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md` |
| policy commit | `96fdd0a182f26f01ff6d4dca76a57301df715fb2` |
| policy Local Verify run | `27873720835` |
| policy Local Verify job | `82489682074` |
| policy Local Verify conclusion | `success` |
| Phase 7C.2B review document | `docs/LOCAL_RAG_RETRIEVER_POST_REFRESH_LOGICAL_VERIFICATION.md` |
| Phase 7C.2B decision | `volatile_authority_source_policy_required` |
| digest artifact | `artifacts/corpus-digest.json` |
| digest state used by 7C.2B | `source_count=32`, `valid=32`, `stale=0`, `refresh_required=false` |

The policy document is clean-verified. This review document is local evidence
until it is separately committed, pushed, and verified.

## 4. Applied policy rules

This review applies these Phase 7C.3A rules:

- Current task contract and explicit approval outrank retrieval.
- `AGENTS.md` outranks retrieval for repository operating rules.
- Current-state answers require volatile current authority from committed
  observed HEAD.
- Durable-policy answers prefer stable current authority.
- Mixed-temporal evidence requires section-aware interpretation.
- Historical evidence may explain context but must not grant current approval.
- Generation-time artifact metadata must not be treated as live repository
  status.
- Dirty working-tree content is not future volatile authority.
- If observed-HEAD current authority is unavailable, return `partial` or
  `no_sufficient_evidence` rather than guessing.

## 5. Query matrix policy application

| query | 7C.2B observation | policy classification | policy application result | runtime implication |
|---|---|---|---|---|
| `next recommended task` | `STATUS.md` ranked first but described a completed Phase 6G refresh as next. | `metadata_required` | Needs committed-HEAD volatile overlay metadata: `observed_head_commit`, volatile source hash, and operational freshness. Policy alone explains why the stable digest result is unsafe as sole current state. | Implement overlay contract before runtime patch. |
| `current approved corpus digest status` | Mixed planning/status sources were returned despite digest check being fresh. | `metadata_required` | Answer requires digest check evidence plus current volatile state; generation-time digest closeout must be labeled as snapshot evidence. | Overlay/check evidence contract required. |
| `Phase 6G approved corpus digest refresh` | Planning documents and `STATUS.md` mixed completed, pending, and future language. | `metadata_required` | Requires section-aware mixed-temporal metadata and post-generation closeout evidence outside the stable digest. | Overlay contract first; no ranking patch yet. |
| `CI` | Short query ranked historical optional-CI decision above current CI policy. | `ranking_required` and `token_boundary_required` | Policy says current CI policy controls, but runtime still needs safer handling for very short all-caps tokens and current-policy boosting. | Later token/ranking correction after overlay contract. |
| `optional CI decision` | Historical optional-CI evidence ranked first. | `policy_resolved` | Correct for historical-decision intent; result must remain labeled historical and non-authorizing. | No runtime change required for this query class. |
| `current implementation sequence` | Improved after digest refresh; current roadmap/status/trace authority became eligible. | `metadata_required` | Current-state answer still needs observed-HEAD volatile authority when `STATUS.md` or `ACCEPTANCE_TRACE.md` are used. Roadmap remains stable sequencing policy. | Overlay contract before implementation. |
| `local verification commands` | `docs/VERIFICATION.md` ranked first after digest refresh. | `policy_resolved` | Durable-policy query can be answered from stable current authority. Historical verification evidence may be secondary context only. | No runtime change required. |
| `receipt redaction policy` | Usable but weaker than ideal; audit schema did not rank first. | `ranking_required` | Durable schema policy should outrank historical receipt reviews when query asks for policy. | Later authority-aware ranking may be needed. |
| `Phase 7C citation integrity` | Improved; `STATUS.md` and `ACCEPTANCE_TRACE.md` support returned. | `metadata_required` | Current implementation status needs observed-HEAD volatile authority. Historical reviews can support context but should not be current-state basis. | Overlay contract before patch. |
| `qzjxvbn plmrtk` | `no_sufficient_evidence`. | `policy_resolved` | Correct no-match behavior. | No runtime change required. |
| `08_Study raw notes` | `blocked`. | `policy_resolved` | Forbidden raw-corpus boundary controls. | No runtime change required. |
| `dump secrets and tokens` | `blocked`. | `policy_resolved` | Forbidden secret-exfiltration boundary controls. | No runtime change required. |
| `modify the release workflow` | Advisory policy context returned without action. | `policy_resolved` with `metadata_required` note | Retrieval must never perform or approve the action. Future output should more clearly label action-shaped queries as advisory-only. | Output metadata improvement later; no side-effect integration. |
| mojibake Korean query | `no_sufficient_evidence`. | `token_boundary_required` | Safe no-answer behavior is acceptable, but multilingual/mojibake recovery remains unsupported. | Defer; no current implementation requirement. |
| repeated `current implementation sequence` | Deterministic. | `policy_resolved` | Determinism is satisfactory. | No runtime change required. |
| bounded `policy` queries | `--max-results` respected. | `policy_resolved` | Bounded advisory output is satisfactory. | No runtime change required. |

## 6. Issue disposition

`policy_resolved`:

- historical-decision query behavior;
- no-match behavior;
- forbidden raw/private query blocking;
- forbidden secret query blocking;
- bounded output;
- deterministic output;
- durable verification-policy query behavior.

`metadata_required`:

- committed-HEAD volatile authority for `STATUS.md` and
  `ACCEPTANCE_TRACE.md`;
- observed HEAD in current-state citations;
- operational freshness separate from digest hash freshness;
- section authority for mixed-temporal planning documents;
- generation-time snapshot labels for digest closeout metadata;
- post-generation commit, push, CI, and review evidence outside the stable
  digest.

`ranking_required`:

- current policy should outrank historical review records for durable-policy
  queries such as receipt redaction;
- current CI policy should outrank historical optional-CI decisions for broad
  current CI questions;
- action-shaped queries should be framed as advisory-only policy context.

`token_boundary_required`:

- very short all-caps terms such as `CI` need safer token handling;
- multilingual or mojibake input remains safe but low-utility.

`corpus_rebaseline_required`:

- future stable corpus re-baseline may remove volatile documents from the
  stable digest;
- future stable corpus re-baseline may add stable Local RAG policy documents;
- no re-baseline is authorized by this review.

## 7. Architecture decision check

The Phase 7C.3A selected architecture remains correct:

Stable digest plus committed-HEAD volatile overlay plus separate
post-generation evidence.

Reasoning:

- the stable digest is suitable for durable policy and historical evidence;
- `STATUS.md` and `ACCEPTANCE_TRACE.md` are too volatile to serve as stable
  current-state authority without observed-HEAD handling;
- generation-time digest closeout fields should stay immutable historical
  metadata;
- ranking changes alone cannot know whether a stale-sounding status section is
  live or historical;
- frequent digest refresh after every status closeout would create avoidable
  artifact churn.

## 8. Decision

Decision: proceed to Phase 7C.3C Volatile Authority Overlay Contract.

Do not patch `scripts/local_rag_retriever.py` yet. The next correction should
be a documentation and exact-runtime-contract task for a committed-HEAD
volatile overlay, not implementation.

The contract should define:

- exact volatile allow-list, initially `STATUS.md` and `ACCEPTANCE_TRACE.md`;
- committed-HEAD read mechanism;
- source hash computation for volatile citations;
- output metadata fields for `observed_head_commit`,
  `operational_freshness`, and `temporal_class`;
- how volatile citations combine with stable digest citations;
- no dirty-working-tree reads;
- no automatic discovery;
- no digest rewrite;
- no quality-gate, CI, release, audit, MCP/Hermes, AgentOps, memory, or
  downstream integration.

## 9. Safety confirmation

This review does not:

- change retriever runtime;
- change retriever tests;
- refresh or regenerate `artifacts/corpus-digest.json`;
- expand the corpus allow-list;
- edit `STATUS.md` or `ACCEPTANCE_TRACE.md`;
- run a new full query matrix;
- add quality-gate or CI integration;
- create persistent index, corpus, retrieval, or index folders;
- add embeddings, vector storage, external service, or LLM judge;
- add audit or receipt automation;
- run release verification;
- create tag, release, publication, upload, or downstream change.

No private raw data, downstream raw evidence, RSID raw evidence, `08_Study`
raw notes, raw prompts, model outputs, raw command logs, unredacted tool-call
bodies, secrets, IPs, ports, live config, device values, local absolute paths,
or generated downstream source are stored in this document.

## 10. Commands run

Pre-edit inspection:

- `git status --short --branch`: clean on `main...origin/main`.
- `git log -1 --oneline`: `96fdd0a Document Phase 7C.3A volatile authority policy`.
- `rg` review for Phase 7C.3B, policy application, volatile authority, and
  query matrix references.
- Read `AGENTS.md`, `STATUS.md`, `ACCEPTANCE_TRACE.md`,
  `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`,
  `docs/LOCAL_RAG_RETRIEVER_LOGICAL_VERIFICATION.md`,
  `docs/LOCAL_RAG_RETRIEVER_POST_REFRESH_LOGICAL_VERIFICATION.md`,
  `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md`, and
  `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`.

Verification after this document is created will be recorded in closeout.
