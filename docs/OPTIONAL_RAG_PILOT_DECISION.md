# Optional RAG Pilot Decision

## 1. Purpose

Determine whether an optional approved-corpus RAG pilot is justified and safe for
`codex-dev-harness`.

Current sequencing note: this record is historical RAG risk evidence. It is
superseded for implementation sequencing by
`docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, which makes approved corpus digest
the required predecessor to local RAG and keeps retrieval local-first,
redaction-aware, metadata-backed, and approval-gated.

This record is documentation-only. It does not approve or implement retrieval,
indexing, embeddings, vector storage, an external RAG service, runtime code,
CI/audit/MCP integration, release evidence generation, downstream evidence
collection, Scenario-Simulator changes, tags, pushes, or private raw data
copying.

## 2. Source basis

Primary repository basis:

- `AGENTS.md`
- `PRODUCT.md`
- `MVP.md`
- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `docs/SAFETY_POLICY.md`
- `docs/VERIFICATION.md`
- `docs/PROFILE_MATRIX.md`
- `docs/AI_HANDOFF.md`
- `docs/POST_V0.1.0_ROADMAP.md`
- `docs/PROMPT_PATTERNS.md`
- `docs/SIMPLIFICATION_CHECKLIST.md`
- `docs/APPROVED_CORPUS_RAG_PLAN.md`
- `docs/MODEL_CHANGE_POLICY.md`

Read-only external context:

- RSID Inspection `README.md`
- RSID Inspection `review_outputs/n3g_application_plan.md`
- `08_Study` `README.md`

The external context was used only to assess source-use boundaries and retrieval
friction. No private raw content, implementation excerpts, environment values,
or detailed domain evidence from those contexts is copied into this record.

One source-quality limitation was observed: some external context text rendered
with character encoding damage in the shell. That is a reason to avoid treating
those files as direct corpus candidates without a separate encoding and
redaction review.

## 3. Approved corpus candidates

Future approved corpus candidates should remain limited to repository-owned
governance, policy, and evidence documents that are already intended to guide
Codex work. Candidate classes are:

- root contract files such as `AGENTS.md`, `README.md`, `STATUS.md`, and
  `ACCEPTANCE_TRACE.md`
- safety, verification, profile, architecture, and handoff policy docs under
  `docs/`
- ADRs under `docs/adr/`
- release records, clean clone validation records, and local target experiment
  records under `docs/`
- current RAG and model-change planning docs, only as planning context
- this decision record after review

Candidate status does not authorize indexing. A future task must name exact
files or exact glob patterns, required metadata, exclusion rules, redaction
checks, and verification before any corpus artifact or retrieval behavior is
created.

Required future metadata should include at least `source_path`, `git_sha`,
`section_title`, `verified_at`, `risk_label`, and `allowed_for_release`, using
repo-relative paths only.

## 4. Forbidden corpus

A future corpus must not collect password, passwd, pwd, token, api_key, secret,
or credential material.

It must also exclude:

- private raw input
- sensitive business source text
- live configuration
- device addresses, equipment parameters, or live-control values
- raw downstream implementation details
- generated downstream target output
- prompt/session transcripts
- model outputs
- unredacted tool-call request or response bodies
- legacy program source, binaries, installers, drivers, or vendor packages
- RSID review outputs as direct corpus material unless separately redacted and
  explicitly approved
- personal knowledge-vault notes such as `08_Study` content unless separately
  curated into a repository-owned safe summary

If a file mixes useful policy text with forbidden material, exclude the file
until a separate task approves redaction and inclusion.

## 5. Manual retrieval baseline questions

| question | manual result |
|---|---|
| What is the current RAG boundary? | Clear. Current docs say RAG planning exists, but retrieval indexes, embeddings, vector stores, and RAG tooling remain absent and deferred. |
| Which sources are plausible safe candidates? | Clear. Repository-owned governance, safety, verification, architecture, ADR, release, and local experiment records are plausible candidates. |
| Which sources are forbidden? | Clear. Private raw input, live config, sensitive values, prompts, model outputs, downstream implementation details, and external RSID or personal vault content are not safe corpus by default. |
| Can manual `rg` plus direct document reads answer the pilot-readiness question? | Yes. The required basis was recoverable without RAG. |
| Did manual retrieval show friction? | Yes. The basis is spread across many current and historical docs, and external context paths were ambiguous. |
| Did the friction justify implementation now? | No. The friction was manageable and does not overcome the safety and maintenance cost of adding RAG surface. |

## 6. Retrieval friction findings

Manual retrieval was sufficient, but not frictionless:

- `STATUS.md` and roadmap docs contain both current decisions and historical
  evidence; a retrieval layer would need risk labels to prevent historical or
  deferred plans from being treated as current approval.
- The existing approved-corpus plan already states candidate files and forbidden
  material, so a pilot would mostly operationalize a known policy rather than
  answer an unknown design question.
- External context lookup had naming and location ambiguity. That shows why
  source metadata matters, but it also shows why broad ingestion is unsafe.
- External RSID context includes legacy program, config, binary, driver, and
  implementation-reference boundaries. It is useful as read-only safety context
  but unsuitable as default corpus.
- The `08_Study` README describes a personal knowledge database and explicitly
  separates general study notes from business design and implementation source.
  It should not be treated as repository corpus.
- Encoding damage in external context could cause inaccurate retrieval if files
  were indexed without an encoding check.

The strongest retrieval improvement would be a curated, repo-relative
allow-list with metadata and risk labels. That improvement can remain
documentation-only until repeated tasks show manual lookup failures.

## 7. Privacy / sensitive-data boundary

The pilot boundary must preserve the repository's local-first and
private-data-safe model:

- use repository-owned policy and evidence summaries, not raw downstream data
- use repo-relative source paths, not absolute local paths
- prefer summaries, identifiers, and hashes over copied source text
- treat retrieval output as advisory context, not approval
- require human approval before corpus expansion, generated corpus artifacts,
  retrieval tooling, model comparison, prompt capture, or output capture
- keep external contexts read-only unless separately curated into safe,
  repository-owned summaries

No current need justifies copying private raw input, legacy source, live
configuration, external review outputs, personal vault notes, or tool-call
bodies into a corpus.

## 8. Pilot options

| option | summary | assessment |
|---|---|---|
| A. No pilot now | Keep manual retrieval and this decision record as the current boundary. | Preferred. Lowest scope and safety burden; enough for current needs. |
| B. Docs-only corpus allow-list refinement | Later add or update a Markdown-only allow-list and exclusion checklist. | Reasonable only if repeated retrieval friction appears. |
| C. Local keyword retrieval prototype | Later create local retrieval tooling over an exact approved allow-list. | Not approved now. Would add implementation surface, tests, and maintenance. |
| D. Embedding or vector RAG pilot | Build embeddings, vector storage, or external RAG integration. | Rejected for this baseline. Too much safety and maintenance burden for current evidence. |

## 9. Decision

Historical decision at that time: do not implement or start an optional RAG
pilot.

An optional RAG pilot was not justified at that time because manual retrieval
answered the readiness questions, the existing plan already defined the safe
candidate and forbidden corpus boundary, and the then-current repository
direction was to keep the harness stable as a local-first governed baseline.

A future pilot may be reconsidered only if repeated tasks show material manual
retrieval failure. Any future approval must be exact-file, local-only,
dry-run-first, redaction-aware, encoding-aware, and metadata-backed. It must not
broaden side-effect permissions or include external/private corpus material by
default.

## 10. Next step

Use this decision record as the current RAG readiness boundary. Continue manual
retrieval for future tasks.

If repeated evidence later justifies revisiting the topic, the next safe step is
a docs-only corpus allow-list refinement that names exact repo-owned files,
forbidden files, metadata fields, redaction checks, encoding checks,
verification commands, and closeout requirements. Do not create retrieval code,
indexes, embeddings, vector storage, external service calls, CI integration,
audit automation, release artifacts, downstream evidence collection, or
Scenario-Simulator changes without separate explicit approval.
