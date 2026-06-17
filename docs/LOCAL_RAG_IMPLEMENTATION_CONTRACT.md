# Local RAG Implementation Contract

## 1. Purpose

Define the Phase 7B implementation contract for a future local-only,
read-only lexical retriever over the approved corpus digest basis.

Phase 7B is implementation-contract-only. It does not implement retrieval,
create an index, create a corpus folder, create a retrieval folder, add
embeddings, add vector storage, call external services, implement MCP/Hermes,
add release automation, or edit downstream repositories.

This contract exists so a later Phase 7C task can implement the smallest safe
retriever only after separate owner approval.

## 2. Corpus Basis

The only approved future retrieval basis is:

- digest metadata: `artifacts/corpus-digest.json`
- source text: repo-owned source files listed in the digest `sources` array

The current digest metadata says:

- `artifact_type`: `approved_corpus_digest`
- `artifact_path`: `artifacts/corpus-digest.json`
- `repository`: `esj1123/codex-dev-harness`
- `digest_algorithm`: `sha256`
- source count: `32`
- `release_artifact_status`: `not_release_artifact_without_separate_approval`
- `rag_authorization_status`: `not_authorized`

The digest is metadata/hash-only. It does not copy full source text. Its
existence does not authorize retrieval implementation.

## 3. Allowed Inputs

A future retriever may read only these inputs after separate implementation
approval:

- `artifacts/corpus-digest.json`
- digest-listed repo-owned source files
- short sanitized user query text
- optional bounded filters over digest metadata, such as source path, risk
  label, content class, or current-vs-historical handling

Allowed source paths must be repo-relative and must appear in the digest. A
future retriever must reject source paths that are absent from the digest, use
parent traversal, point outside the repository, or identify generated/private
material.

## 4. Forbidden Inputs

A future retriever must not read, ingest, index, hash for retrieval, summarize,
or search:

- private raw data
- `08_Study` raw notes
- RSID raw evidence or review output
- downstream raw evidence
- generated downstream output
- external or private corpus material
- local absolute paths
- prompt transcripts
- model output transcripts
- unredacted tool-call request or response bodies
- secrets, tokens, keys, credentials, or account identifiers
- real IPs, ports, live endpoints, live config, device values, broker values,
  account values, equipment values, or other live values

Forbidden inputs remain forbidden even when a user query asks for them. If a
future task needs a new source class, it must first update the approved corpus
contract through a separate approval.

## 5. Retriever Boundary

A future implementation must be:

- local-only
- read-only
- lexical or search-based
- deterministic enough to test
- standard-library-first unless a later task explicitly approves dependencies
- advisory only

It must not:

- create or persist an index by default
- create `corpus/`, `retrieval/`, or `index/`
- add embeddings
- use vector storage or a vector database
- call external services
- use an LLM judge or model ranking
- run repository mutations
- broaden the active task contract
- grant approval for side effects
- override current repository policy with historical records

## 6. Future Request Shape

A future retrieval request should use a bounded object with these fields:

| field | required | contract |
|---|---:|---|
| `query` | yes | Short search query or question. Must not be a prompt transcript. |
| `allowed_source_paths` | no | Optional repo-relative subset of digest-listed paths. |
| `max_results` | no | Small positive integer limit. |
| `risk_label_filter` | no | Optional list of digest risk labels. |
| `content_class_filter` | no | Optional list of digest content classes. |
| `include_historical_records` | no | Whether historical records may be returned as context. |
| `require_current_authority` | no | Whether current authority is required for an answer. |
| `citation_required` | yes | Must be true for retrieval-backed output. |

The request object must not include raw private text, raw source documents,
local absolute paths, secrets, live values, downstream raw evidence, RSID raw
evidence, or `08_Study` raw notes.

## 7. Future Output Shape

A future retriever should return a bounded object with these fields:

| field | required | contract |
|---|---:|---|
| `status` | yes | `found`, `partial`, `no_sufficient_evidence`, or `blocked`. |
| `query` | yes | Sanitized query summary. |
| `matched_sources` | yes | Ordered source reference objects. Empty when no safe evidence is available. |
| `source_path` | per source | Repo-relative path from the digest. |
| `section_title` | per source | Digest section title or `unknown`. |
| `content_hash` | per source | SHA-256 content hash from the digest entry. |
| `risk_label` | per source | Digest risk label. |
| `content_class` | per source | Digest content class. |
| `match_reason` | per source | Short safe summary of why the source matched. |
| `evidence_excerpt` | per source | Bounded snippet or safe summary only. |
| `current_vs_historical_note` | per source | Whether the source is current authority, historical evidence, or deferred planning. |
| `safety_notes` | yes | Safe notes about excluded sources or boundary limits. |
| `no_answer_reason` | conditional | Required for `no_sufficient_evidence` or `blocked`. |

Outputs must not include full documents, private raw content, prompt
transcripts, raw command logs, unredacted tool-call bodies, local absolute
paths, secrets, live values, or generated downstream source.

## 8. Citation Rules

Every retrieval-backed answer must cite:

- repo-relative source path
- section title or stable section label
- digest content hash
- risk label
- current-vs-historical status

Short snippets are allowed only when the source is digest-listed, repo-owned,
and safe to quote. Prefer summaries when quoting would copy too much source
text or risk exposing policy-only sensitive terms out of context.

## 9. No-Answer Behavior

Return `no_sufficient_evidence` when:

- no digest-listed source matches
- matching evidence exists only outside the digest
- only historical records match but current authority is required
- source text is missing or cannot be read safely
- answering would require private raw data, `08_Study` raw notes, RSID raw
  evidence, downstream raw evidence, external/private corpus, or live values
- answering would require unapproved side effects

Return `blocked` when the request asks the retriever to cross a forbidden input
boundary or to perform an action rather than return advisory evidence.

No-answer output should explain the boundary without revealing forbidden
content.

## 10. Current And Historical Authority

The retriever must distinguish current authority from historical risk evidence.

Current authority examples include current repository rules, current status,
current roadmap sequencing, current safety policy, and current verification
policy.

Historical evidence may explain why a boundary exists, but it must not override
current repository rules or grant implementation approval.

When `require_current_authority` is true, a result set based only on historical
or deferred records must return `no_sufficient_evidence` or `partial`.

## 11. Future Verification Requirements

A later Phase 7C implementation must prove:

- the retriever reads `artifacts/corpus-digest.json`
- every searched source path appears in the digest
- every searched source path is repo-relative
- forbidden path classes are rejected
- missing sources are handled without broadening scope
- output includes citations for every matched source
- output includes digest content hashes
- output is bounded by `max_results`
- no private raw data, local absolute paths, secrets, live values, prompt
  transcripts, model outputs, or tool-call bodies are returned
- no index, corpus artifact, embeddings, vector storage, external service, CI,
  quality-gate integration, audit automation, MCP/Hermes behavior, release
  automation, or downstream edit is added unless separately approved

Suggested future tests should use synthetic digest fixtures and synthetic
source files. They must not ingest private or downstream material.

## 12. Receipt Evidence Boundary

Future receipts may summarize retrieval evidence by recording:

- retrieval status
- sanitized query summary
- matched source count
- repo-relative citations
- digest path
- digest source-basis commit
- content hashes
- no-answer reason
- safety notes

Receipts must not store full retrieved documents, raw private data, prompt
transcripts, raw command logs, unredacted tool-call bodies, local absolute
paths, secrets, live values, or generated downstream source.

## 13. Closeout Requirements For Phase 7B

Phase 7B closeout must report:

- final status label
- changed files
- implementation contract summary
- allowed input boundary
- forbidden input boundary
- output shape summary
- citation and no-answer rules
- verification results
- safety checks
- confirmation that no RAG implementation, retrieval script, index, corpus
  folder, retrieval folder, embeddings, vector database, external service,
  MCP/Hermes, AgentOps, memory runtime, release automation, artifact
  regeneration, digest regeneration, downstream edit, or private/raw corpus
  ingestion occurred
- next recommended step

## 14. Next Task Prompt

```text
Repository:
esj1123/codex-dev-harness

Task:
Implement Phase 7C minimal local lexical retriever prototype.

Goal:
Implement the smallest local-only, read-only lexical retriever over
artifacts/corpus-digest.json and digest-listed repo-owned source files, using
the Phase 7B implementation contract.

Required boundaries:
- exact allowed files and scripts must be approved in the task
- local-only and read-only
- no persistent index unless separately approved
- no corpus folder, index folder, embeddings, vector DB, external service,
  MCP/Hermes, AgentOps, memory runtime, release automation, downstream edit, or
  digest regeneration
- no private raw data, 08_Study raw notes, RSID raw evidence, downstream raw
  evidence, prompt transcripts, model outputs, tool-call bodies, local absolute
  paths, secrets, IPs, ports, live config, or device values
```
