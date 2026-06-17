# Local RAG Design

## 1. Purpose

Define the Phase 7A design for a future local-only, read-only lexical
retriever over the approved corpus digest basis.

This design exists to make future local RAG implementation safer and more
traceable. It does not implement retrieval, create an index, regenerate the
digest, create a corpus folder, call a model, or authorize any side effect.

Phase 7B is documented separately in
`docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md`. It is an
implementation-contract-only bridge from this design to a possible later
prototype; it still does not implement retrieval.

## 2. Current corpus basis

The current approved corpus basis is the generated digest artifact:

- artifact path: `artifacts/corpus-digest.json`
- artifact type: `approved_corpus_digest`
- source count: 32
- artifact-containing commit:
  `df51aac8c3a9b001c4d036633897f176b87c304d`
- source-basis commit:
  `37a0e7274ae2cd0a50811c138147a37c1b4c0160`
- `release_artifact_status`:
  `not_release_artifact_without_separate_approval`
- `rag_authorization_status`: `not_authorized`

The digest records metadata and SHA-256 hashes only. It does not copy full
source text. The successful `Local Verify` evidence for the artifact-containing
commit is run `27522922010`, job `81344426960`.

Future retrieval may inspect only repo-owned source files listed in the digest,
and only after a later task separately approves implementation.

## 3. Non-goals

Phase 7A does not:

- implement a retriever;
- create `corpus/`, `retrieval/`, or `index/`;
- add embeddings, vector storage, or a vector database;
- call an external service or LLM judge;
- integrate with CI or `scripts/quality_gate.py`;
- add audit automation;
- regenerate `artifacts/corpus-digest.json`;
- generate eval reports or release artifacts;
- authorize MCP/Hermes, release automation, downstream integration, or live
  target behavior.

## 4. Local-first retrieval boundary

The first local RAG phase must be local-only and read-only.

Allowed future read surfaces, if separately approved:

- `artifacts/corpus-digest.json`;
- repo-owned source files whose paths appear in the digest `sources` list;
- metadata fields in the digest, including source path, section title, content
  class, risk label, and content hash.

Forbidden future read surfaces by default:

- private raw data;
- `08_Study` raw notes;
- RSID raw evidence or review output;
- downstream raw evidence or generated downstream output;
- prompt transcripts;
- model output transcripts;
- unredacted tool-call request or response bodies;
- live configuration, endpoint, device, broker, account, or equipment values.

## 5. Read-only lexical retriever concept

The first retriever concept is lexical and search-based. It should match query
terms against approved source text and digest metadata without embeddings,
vector search, model ranking, or external calls.

The retriever should:

- load the digest;
- restrict eligible source files to digest-listed paths;
- verify each source path is repo-relative and still present;
- read source text only for local matching;
- return bounded snippets or summaries, not copied documents;
- include citations and digest metadata for every result;
- preserve current task scope and approval boundaries.

## 6. Input schema

Future retrieval requests should accept a bounded input object with these
fields:

| field | required | meaning |
|---|---:|---|
| `query` | yes | Short user-facing search question or topic. |
| `allowed_source_paths` | no | Optional subset of digest-listed repo-relative paths. Empty means all eligible digest sources. |
| `max_results` | no | Positive bounded result limit. Default should be small. |
| `risk_label_filter` | no | Optional allowed risk labels, such as current policy or historical record. |
| `include_historical_records` | no | Whether historical and deferred records may be returned. |
| `require_current_authority` | no | Whether an answer must be grounded in current authority, not historical evidence alone. |
| `task_context_summary` | no | Short sanitized context summary. This must not be a full prompt transcript. |
| `side_effect_class` | no | Current task side-effect class, used only to enforce boundaries. |
| `citation_required` | yes | Must be true for retrieval-backed answers. |

The input must not include private raw data, prompts, secrets, credentials,
account identifiers, local absolute paths, raw downstream text, or live values.

## 7. Output schema

Future retrieval results should return a bounded output object with these
fields:

| field | required | meaning |
|---|---:|---|
| `status` | yes | One of `found`, `partial`, `no_sufficient_evidence`, or `blocked`. |
| `results` | yes | Ordered result objects. Empty when no safe evidence is available. |
| `source_path` | per result | Repo-relative source path from the digest. |
| `section_title` | per result | Digest section title when available, otherwise a local heading or `unknown`. |
| `content_hash` | per result | SHA-256 hash from the digest entry. |
| `risk_label` | per result | Digest risk label. |
| `relevance_reason` | per result | Short explanation of why the result matched. |
| `quote_or_summary_boundary` | per result | States whether the output is a bounded quote, summary, heading, or metadata-only citation. |
| `current_vs_historical_note` | per result | Explains whether the source is current authority, historical evidence, or deferred planning. |
| `safety_notes` | yes | Boundary notes such as excluded source classes or approval gaps. |
| `no_answer_reason` | conditional | Required when `status` is `no_sufficient_evidence` or `blocked`. |

The output must not include full source documents, raw private material,
unredacted command logs, prompt transcripts, model output transcripts, or
tool-call bodies.

## 8. Citation requirements

Every retrieval-backed answer must cite:

- repo-relative source path;
- section title or heading when available;
- digest `content_hash`;
- risk label;
- current-vs-historical status.

Answers should prefer concise summaries, source identifiers, and hash metadata.
Short quotes may be used only when needed for precision and only from approved
repo-owned sources. Long copying is out of scope.

## 9. Source eligibility rules

A source is eligible only when all of these are true:

- the source path appears in `artifacts/corpus-digest.json`;
- the source path is repo-relative;
- the source path does not match an excluded class;
- the digest entry has `allowed_for_digest` set consistently with inclusion;
- the source file is readable text;
- the source can be handled without copying forbidden raw material.

Excluded classes remain excluded even if a later query asks for them:

- `.git/**`;
- `.github/workflows/**`;
- `artifacts/**`;
- `local/**`;
- `corpus/**`;
- `retrieval/**`;
- `index/**`;
- `evals/golden/**`;
- generated target output;
- private, downstream, RSID, or `08_Study` raw evidence.

## 10. Redaction and safety rules

The retriever must treat sensitive and boundary terms as reasons to limit
output, not as material to expose.

Rules:

- do not return secrets, credentials, account identifiers, live values, or local
  absolute paths;
- do not return real endpoint, device, broker, equipment, or live configuration
  values;
- do not return private raw data or business source text;
- do not return prompt transcripts, model output transcripts, or tool-call
  bodies;
- classify policy-only sensitive-term matches without copying values;
- prefer metadata-only output when a safe summary would still risk exposure.

## 11. Query handling rules

The retriever should normalize user queries only enough for lexical matching.
It should not rewrite the task contract, infer new approvals, or broaden file
access.

If a query asks for prohibited material, the retriever should return `blocked`
or `no_sufficient_evidence` with a boundary reason. If a query asks for an
action, the retriever may return policy context but must not perform the action.

## 12. Result ranking concept

Initial ranking should be deterministic and explainable:

1. current authority sources matching exact terms;
2. current authority sources matching close lexical variants;
3. current status or verification evidence;
4. historical or deferred records, only when allowed;
5. metadata-only matches.

When `require_current_authority` is true, historical and deferred records may
support risk context but must not be returned as the sole basis for an answer.

## 13. No-answer / insufficient-evidence behavior

Return `no_sufficient_evidence` when:

- no approved digest source matches;
- only historical or deferred records match and current authority is required;
- evidence exists only outside the digest;
- answering would require private raw data, raw downstream evidence, RSID raw
  evidence, or `08_Study` raw notes;
- answering would require missing approval for side effects;
- the eligible source text cannot be read safely.

Use `blocked` when the query asks the retriever to cross a forbidden boundary.

## 14. Current-vs-historical record handling

The retriever must distinguish current policy from historical evidence.

Current authority examples:

- `AGENTS.md` current phase rule;
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`;
- current `STATUS.md` sequencing and closeout state;
- current safety and verification policies.

Historical or deferred examples:

- older release records;
- optional CI/RAG/audit/eval decision records;
- Stage 5B practical probe records;
- superseded roadmap records.

Historical evidence may explain why a boundary exists. It must not override the
current task contract or the current implementation roadmap.

## 15. Audit / receipt integration

Future retrieval-backed task receipts may summarize retrieval evidence without
copying full source text.

Suggested receipt fields:

- `retrieval_status`;
- `retrieval_query_summary`;
- `retrieval_source_count`;
- `retrieval_citations`;
- `retrieval_no_answer_reason`;
- `retrieval_safety_notes`;
- `retrieval_digest_path`;
- `retrieval_digest_commit`;
- `retrieval_rag_authorization_status`.

Receipts must not include raw prompt transcripts, raw command logs, raw source
documents, private data, or tool-call bodies.

## 16. Verification requirements

Phase 7A verification is documentation-only:

- confirm changed files are allowed;
- confirm no RAG code, retriever, index, embeddings, vector storage, external
  service, CI integration, quality-gate integration, audit automation, or
  downstream edit was added;
- confirm no digest regeneration occurred;
- run markdown diff checks and repository quality gate when available;
- scan changed files for local absolute paths, IP-like values, sensitive-term
  assignments, and forbidden implementation surfaces.

Future implementation verification must additionally prove that the retriever
reads only digest-listed repo-relative sources and returns citations for every
result.

## 17. Future implementation phases

Recommended future order:

1. Phase 7A: documentation-only local RAG design.
2. Phase 7B: implementation contract for a read-only lexical retriever.
3. Phase 7C: minimal local retriever prototype, if separately approved.
4. Phase 7D: retrieval verification and receipt evidence, still advisory.
5. Later phase: MCP boundary planning.
6. Later phase: Hermes sidecar planning.

Each phase requires separate owner approval. No phase may infer approval from
this design.

## 18. Forbidden implementation surfaces

Phase 7A forbids:

- RAG runtime code;
- retriever implementation;
- `corpus/`, `retrieval/`, or `index/`;
- embeddings;
- vector storage or vector database;
- external service calls;
- LLM judge behavior;
- MCP/Hermes implementation;
- CI integration;
- quality-gate integration;
- audit automation;
- release automation;
- downstream repository edits;
- corpus digest regeneration;
- generated corpus artifacts;
- eval report generation;
- prompt transcript, model output transcript, or tool-call body capture.

## 19. Success criteria

Phase 7A succeeds when:

- the digest artifact is identified as the approved source basis;
- the design is local-only, read-only, and lexical-first;
- input and output schema fields are defined;
- citation, no-answer, and current-vs-historical handling rules are explicit;
- `08_Study`, RSID, downstream, private, and live-value boundaries are explicit;
- no implementation or generated artifact is added.

## 20. Closeout requirements

Closeouts for Phase 7A must report:

- final status label;
- changed files;
- design summary;
- corpus digest basis;
- input schema summary;
- output schema summary;
- citation rules;
- no-answer behavior;
- current-vs-historical handling;
- `08_Study` boundary;
- RSID/downstream boundary;
- forbidden implementation surfaces;
- verification command results;
- safety scan results;
- whether a local commit was created;
- whether push, tag, release, artifact regeneration, digest regeneration,
  generated corpus artifact creation, eval report generation, RAG, retrieval,
  indexing, embeddings, vector storage, external service use, MCP/Hermes,
  release automation, or downstream edits occurred;
- next recommended task.

## 21. Next task prompt

```text
Repository:
esj1123/codex-dev-harness

Task:
Create Phase 7B local lexical retriever implementation contract.

Goal:
Define the smallest safe implementation contract for a future local-only,
read-only lexical retriever over artifacts/corpus-digest.json and digest-listed
repo-owned source files.

Required boundaries:
- documentation-first
- no runtime implementation unless separately approved in the task
- no embeddings
- no vector database
- no external service
- no LLM judge
- no CI or quality-gate integration
- no audit automation
- no digest regeneration
- no private raw data, 08_Study raw notes, RSID raw evidence, downstream raw
  evidence, prompt transcripts, model output transcripts, or tool-call bodies

Closeout:
- PASS / PASS WITH NOTES / BLOCKED
- changed files
- implementation contract summary
- allowed and forbidden input boundaries
- output shape, citation, and no-answer rules
- future implementation verification requirements
- source eligibility rules
- citation and no-answer rules
- verification plan
- safety exclusions
- whether any implementation, artifact regeneration, push, tag, release, or
  downstream edit occurred
```
