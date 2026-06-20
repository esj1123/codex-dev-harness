# Local RAG Volatile Overlay Contract

## 1. Purpose

Define Phase 7C.3C Volatile Authority Overlay Contract for a future local RAG
retriever implementation.

This contract specifies how a future retriever may read a narrow set of
volatile current-authority files from committed `HEAD` without changing the
stable corpus digest. It is documentation-only and does not implement the
overlay.

## 2. Scope and non-goals

In scope:

- exact volatile authority allow-list;
- committed-HEAD read contract;
- volatile source hash contract;
- output metadata contract;
- merge and precedence rules between volatile overlay results and stable digest
  results;
- partial, no-answer, and conflict behavior;
- future implementation and verification boundaries.

Non-goals:

- no retriever runtime patch;
- no tests patch;
- no JSON config or schema artifact;
- no digest refresh or corpus re-baseline;
- no `artifacts/corpus-digest.json` write;
- no `STATUS.md` or `ACCEPTANCE_TRACE.md` edit;
- no quality-gate integration;
- no CI workflow edit or CI integration;
- no release verification, tag, release, publication, or upload;
- no audit or receipt automation;
- no persistent index, `corpus/`, `retrieval/`, or `index/` directory;
- no embeddings, vector database, external service, LLM judge, MCP/Hermes,
  AgentOps, or memory runtime;
- no downstream access or downstream edit;
- no private/raw corpus ingestion, `08_Study` raw notes, RSID raw evidence, or
  downstream raw evidence.

## 3. Evidence basis

| item | value |
|---|---|
| repository | `esj1123/codex-dev-harness` |
| branch | `main` |
| contract starting HEAD | `7dbe9c4` |
| previous phase | Phase 7C.3B Policy Application Review |
| previous phase commit | `7dbe9c4` |
| policy document | `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md` |
| policy application review | `docs/LOCAL_RAG_POLICY_APPLICATION_REVIEW.md` |
| stable digest artifact | `artifacts/corpus-digest.json` |
| stable digest source count | `32` |
| stable digest role | durable policy, approved historical evidence, and metadata/hash-only source basis |

This document uses the Phase 7C.3A architecture decision: stable digest plus
committed-HEAD volatile overlay plus separate post-generation evidence.

## 4. Volatile authority allow-list

Initial volatile overlay allow-list:

| source_path | temporal class | authority level | allowed query use | notes |
|---|---|---|---|---|
| `STATUS.md` | `volatile_current_authority` | `current_operational_state` | current phase, next step, current verification snapshot, current implementation state | Must be read from committed `HEAD`, not the working tree. |
| `ACCEPTANCE_TRACE.md` | `volatile_current_authority` | `current_operational_state` | acceptance state, phase evidence rows, verification evidence references | Must be read from committed `HEAD`, not the working tree. |

No other volatile source is authorized by this contract.

A future implementation must reject overlay reads for:

- paths absent from the exact allow-list;
- absolute paths;
- parent traversal;
- path aliases or alternate separators that do not canonicalize to an
  allow-listed repo-relative path;
- symlinks or filesystem fallback reads;
- generated artifacts;
- private/raw, downstream, RSID, or `08_Study` material.

## 5. Committed-HEAD read contract

A future implementation must read volatile authority from committed `HEAD`
content only.

Required behavior:

- establish `observed_head_commit` from `git rev-parse HEAD`;
- read source bytes from the commit object, for example
  `git show HEAD:<repo-relative-path>`;
- do not read dirty working-tree file contents for volatile authority;
- do not read staged-but-uncommitted content;
- do not silently fall back to the filesystem if committed-HEAD read fails;
- return `partial` or `no_sufficient_evidence` when committed-HEAD authority
  cannot be established;
- keep all paths repo-relative in outputs.

The overlay may use Git plumbing or another standard-library-compatible method
only if it preserves committed-HEAD semantics. A future implementation task
must name the exact mechanism before editing code.

## 6. Volatile hash contract

Every volatile citation must include a content hash computed from the exact
committed-HEAD bytes used for retrieval.

Required normalization:

- decode source bytes as UTF-8;
- reject invalid UTF-8;
- normalize CRLF and CR to LF;
- do not trim trailing whitespace;
- compute SHA-256 over normalized UTF-8 bytes;
- report the hash as lowercase 64-hex.

The volatile hash is not the stable digest `content_hash` unless the same file
also appears in the digest with identical normalized content. The output must
therefore distinguish:

- `content_hash`: stable digest hash for stable corpus citations;
- `volatile_content_hash`: observed-HEAD hash for volatile overlay citations;
- `source_basis_commit`: stable digest source basis;
- `observed_head_commit`: committed HEAD used by the volatile overlay.

## 7. Output metadata contract

Future overlay-backed matched source objects must include:

| field | requirement |
|---|---|
| `source_path` | Repo-relative allow-listed path. |
| `temporal_class` | Must be `volatile_current_authority`. |
| `authority_level` | Must be `current_operational_state`. |
| `observed_head_commit` | Full commit SHA used for committed-HEAD read. |
| `volatile_content_hash` | SHA-256 of normalized committed-HEAD content. |
| `operational_freshness` | `current`, `lagging`, or `unknown`. |
| `section_authority` | Section-level label when available; otherwise `unknown`. |
| `evidence_excerpt` | Bounded safe excerpt or summary. |
| `match_reason` | Short safe lexical or section match reason. |
| `safety_notes` | Boundary notes when the answer is partial or advisory only. |

Future combined retrieval output should include:

| field | requirement |
|---|---|
| `status` | `found`, `partial`, `no_sufficient_evidence`, or `blocked`. |
| `query_class` | `current_state`, `durable_policy`, `historical_decision`, or `mixed_context` when determinable. |
| `stable_digest_ref` | `artifacts/corpus-digest.json` when stable citations are present. |
| `source_basis_commit` | Stable digest source basis when stable citations are present. |
| `observed_head_commit` | Required when volatile citations are present. |
| `matched_sources` | Bounded merged stable and volatile citations. |
| `conflict_notes` | Required when sources disagree or temporal authority is mixed. |
| `no_answer_reason` | Required for `partial`, `no_sufficient_evidence`, or `blocked` when applicable. |

This contract does not create a JSON schema or config file.

## 8. Merge and precedence rules

For `current_state` queries:

1. Current task contract and explicit approval still control.
2. `AGENTS.md` still controls repository operating rules.
3. Volatile overlay citations from committed `HEAD` control current
   operational state.
4. Stable digest citations may provide durable policy and historical context.
5. Generation-time artifact metadata may only describe the generation moment.

For `durable_policy` queries:

1. Current task contract and `AGENTS.md` still control.
2. Stable current-authority policy citations should rank before volatile
   status citations.
3. Historical evidence may be returned only as context.

For `mixed_context` queries:

1. Use stable policy for rules.
2. Use volatile overlay for current completion or next-step state.
3. Label generation-time digest metadata as a snapshot.
4. Return `partial` when section-level temporal authority is unknown.

For `historical_decision` queries:

1. Historical evidence may be primary.
2. Volatile current authority may provide superseding context.
3. The answer must not imply current approval.

## 9. Conflict behavior

If volatile overlay and stable digest disagree about current state:

- volatile committed-HEAD state controls the current-state answer;
- stable digest remains valid for durable policy or historical context;
- output must include `conflict_notes`.

If `STATUS.md` and `ACCEPTANCE_TRACE.md` disagree:

- return `partial` when one useful current fact can be stated;
- return `no_sufficient_evidence` when resolving the conflict would require
  guessing;
- do not prefer one volatile source silently.

If committed-HEAD read fails:

- do not read the working tree as a fallback;
- return `partial` if stable policy still answers part of the query;
- return `no_sufficient_evidence` if current-state authority is required.

If the user asks the retriever to perform an action:

- return advisory evidence only when safe;
- never perform the action;
- never treat retrieval as side-effect approval.

## 10. Safety and privacy rules

Future overlay implementation must not output:

- full source documents;
- private raw data;
- prompt transcripts;
- model output transcripts;
- raw command logs;
- unredacted tool-call bodies;
- local absolute paths;
- secrets, tokens, keys, credentials, or account identifiers;
- real IPs, ports, live endpoints, live config, device values, broker values,
  account values, equipment values, or other live values;
- generated downstream source.

Forbidden material remains forbidden even if present in an allow-listed file.
If a future implementation detects forbidden material in an overlay candidate,
it must block or omit the unsafe excerpt and report a safe boundary note.

## 11. Future implementation boundary

A future Phase 7C.3D implementation may be considered only after separate
approval.

Likely allowed files for that future task:

- `scripts/local_rag_retriever.py`;
- `tests/test_local_rag_retriever.py`;
- this contract document only if a small clarification is needed.

Likely forbidden files for that future task unless separately named:

- `artifacts/corpus-digest.json`;
- `STATUS.md`;
- `ACCEPTANCE_TRACE.md`;
- `.github/workflows/**`;
- `scripts/quality_gate.py`;
- release artifacts;
- dependency files.

Future implementation must remain:

- standard-library-only unless a later task explicitly approves dependencies;
- local-only;
- read-only;
- advisory-only;
- bounded-output;
- deterministic enough for focused synthetic tests.

## 12. Future verification requirements

A future implementation must test:

- exact allow-list enforcement;
- rejection of absolute paths and parent traversal;
- committed-HEAD reads instead of working-tree reads;
- no fallback to dirty working tree;
- observed HEAD SHA included in volatile citations;
- volatile content hash computed from normalized committed-HEAD bytes;
- invalid UTF-8 rejection;
- `STATUS.md` and `ACCEPTANCE_TRACE.md` disagreement handling;
- stable digest plus volatile overlay merge behavior;
- current-state query behavior;
- durable-policy query behavior;
- historical-decision query behavior;
- bounded output;
- forbidden raw/private query blocking.

Synthetic fixtures should be used where practical. Tests must not ingest
private, downstream, RSID, or `08_Study` raw material.

## 13. Decision

Decision: contract ready for a separately approved Phase 7C.3D Minimal
Volatile Overlay Implementation task.

Do not implement Phase 7C.3D as part of this contract task.

The next task should name exact allowed files, confirm whether committed-HEAD
Git reads are allowed, and specify focused synthetic tests before editing
runtime code.

## 14. Commands run

Pre-edit inspection:

- `git status --short --branch`: clean on `main...origin/main`.
- `git log -3 --oneline --decorate`: confirmed `HEAD`, `origin/main`, and
  `origin/HEAD` at `7dbe9c4`.
- `git diff --name-only`: no output.
- `git diff --cached --name-only`: no output.
- `git ls-files --others --exclude-standard`: no output.
- `rg` review for Phase 7C.3C, volatile authority overlay, committed-HEAD,
  observed HEAD, and policy application references.
- Read `AGENTS.md`, `docs/LOCAL_RAG_POLICY_APPLICATION_REVIEW.md`, and
  `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`.

Verification after this document is created is recorded in task closeout.
