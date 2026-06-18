# Local RAG Retriever Usage Probe

## Purpose

Record a small review-only usage probe for the Phase 7C minimal local lexical
retriever.

This probe evaluates representative safe queries against
`scripts/local_rag_retriever.py`. It does not expand the retriever runtime,
change source eligibility, create an index, regenerate the corpus digest,
generate artifacts, or integrate retrieval with quality gate, CI, audit
automation, MCP/Hermes, AgentOps, memory runtime, release automation, or
downstream repositories.

## Basis

| item | value |
|---|---|
| repository commit | `1502ca55111f436579bd4a0f6292a13d9cae392a` |
| retriever script | `scripts/local_rag_retriever.py` |
| digest basis | `artifacts/corpus-digest.json` |
| output mode | JSON to stdout |
| max results used | `3` |
| probe status | PASS |

## Query Observations

| query | expected behavior | observed behavior | citation/hash check | boundary notes |
|---|---|---|---|---|
| `Phase 7B` | `found` | `found`; 3 matched sources | Returned repo-relative sources `STATUS.md`, `ACCEPTANCE_TRACE.md`, and `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`; each included a digest `content_hash` | Output was bounded to 3 results and 240-character excerpts |
| `current roadmap implementation order` | `found` | `found`; 3 matched sources | Returned repo-relative sources including `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`; each included a digest `content_hash` | Output was bounded and advisory |
| `qzjxvbn plmrtk` | `no_sufficient_evidence` | `no_sufficient_evidence`; 0 matched sources | No citations returned because no digest-listed source matched | Safe synthetic no-match query; no corpus expansion attempted |
| `08_Study raw notes` | `blocked` | `blocked`; 0 matched sources | No citations returned because the request crossed a forbidden raw-corpus boundary | Boundary reason stated that forbidden private/raw material was requested |

## Findings

- `found` behavior returned bounded advisory results with repo-relative
  `source_path` values and digest `content_hash` values.
- `no_sufficient_evidence` behavior returned no matched sources and did not
  broaden the digest-listed corpus.
- `blocked` behavior rejected a forbidden raw-corpus query before returning any
  matched source.
- Probe output did not include local absolute paths, secrets, live values,
  private/raw corpus material, raw prompts, model outputs, raw command logs,
  tool-call bodies, generated downstream source, or full source documents.
- No runtime patch is recommended from this probe.

## Safety Confirmation

No persistent index, `corpus/`, `retrieval/`, or `index/` folder, embeddings,
vector database, external service, quality-gate integration, CI integration,
audit automation, artifact regeneration, digest regeneration, release
automation, MCP/Hermes, AgentOps, memory runtime, downstream edit, or
private/raw corpus ingestion was added by this probe.

## Next Step

Phase 7C is ready for a separately approved downstream usage probe or Phase 7D
retrieval evidence planning. Any downstream or receipt integration must name
exact allowed files, commands, and evidence fields before implementation.
