# Approved Corpus Digest Plan

## 1. Purpose

Plan Phase 6 approved corpus digest work before any local RAG, retrieval,
indexing, embedding, vector storage, or external service integration.

This document defines the safe allow-list model, metadata fields, hash policy,
risk labels, redaction rules, forbidden corpus, and future implementation
boundary for a future corpus digest. It is documentation-only. It does not
generate a digest artifact, create `corpus/`, `retrieval/`, or `index/`, add
scripts, build embeddings, create a vector database, call an external service,
or integrate with CI, quality gates, audit automation, MCP/Hermes, release
automation, or downstream repositories.

## 2. Current corpus baseline

The repository already contains planning and policy records that identify safe
candidate classes and forbidden corpus boundaries:

- `docs/APPROVED_CORPUS_RAG_PLAN.md`
- `docs/OPTIONAL_RAG_PILOT_DECISION.md`
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- `docs/AUDIT_TRACE_SCHEMA.md`
- `docs/EVAL_REPORT_INTEGRATION_PLAN.md`
- `docs/VERIFICATION.md`
- `STATUS.md`
- `ACCEPTANCE_TRACE.md`

Current state:

- approved-corpus planning exists;
- historical RAG pilot deferral is risk evidence, not a permanent blocker;
- approved corpus digest is the next roadmap target before local RAG;
- no digest artifact exists from this task;
- no retrieval, index, embedding, vector database, or RAG tooling is approved
  by this plan.

## 3. Relationship to RAG plan

`docs/APPROVED_CORPUS_RAG_PLAN.md` defines the future local RAG intent and
candidate source classes. This digest plan is the required predecessor to any
RAG implementation.

The order is:

1. approve corpus classes and forbidden corpus boundaries;
2. approve metadata, risk labels, redaction checks, encoding checks, and source
   path rules;
3. approve an exact allow-list and digest artifact format in a later task;
4. generate a digest artifact only if separately approved;
5. implement local retrieval only after digest discipline is proven.

RAG output, if implemented later, must remain advisory context. It must not
grant approval, broaden scope, authorize side effects, or override the current
task contract.

## 4. Approved corpus candidate classes

Initial approved corpus candidates are repo-owned documents intended to guide
repository operation, governance, and verification. Candidate status does not
authorize inclusion in a generated digest.

Candidate classes:

- root governance and project-state documents: `AGENTS.md`, `README.md`,
  `STATUS.md`, and `ACCEPTANCE_TRACE.md`;
- safety, verification, profile, architecture, and handoff policy documents
  under `docs/`;
- ADRs under `docs/adr/`;
- roadmap and capability planning documents;
- release records, release checklist, clean clone validation records, and
  local release evidence policies under `docs/`;
- CI policy and manual read-only workflow policy documents;
- audit / trace / receipt schema and audit policy documents;
- eval policy, eval decision, minimal eval design, and eval/report integration
  planning documents;
- approved-corpus and model-change planning documents;
- local target experiment records and downstream adoption records when they are
  already safe summaries in this repository.

Each future digest task must name exact repo-relative files or exact
repo-relative patterns. Broad class approval is not enough to generate a
digest.

### Exact candidate files and patterns for Phase 6B

The following entries are exact approved-corpus candidates for a future digest
task. This allow-list is candidate evidence only. It does not authorize digest
generation, generated corpus artifacts, indexing, retrieval, RAG,
embeddings, vector storage, external service calls, CI integration, or
quality-gate integration.

Exact candidate files:

- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- `docs/SAFETY_POLICY.md`
- `docs/VERIFICATION.md`
- `docs/CI_POLICY.md`
- `docs/AUDIT_TRACE_SCHEMA.md`
- `docs/AUDIT_LOG_POLICY.md`
- `docs/APPROVED_CORPUS_DIGEST_PLAN.md`
- `docs/APPROVED_CORPUS_RAG_PLAN.md`
- `docs/EVAL_REPORT_INTEGRATION_PLAN.md`
- `docs/EVAL_POLICY.md`
- `docs/EVAL_INTEGRATION_DECISION.md`
- `docs/OPTIONAL_RAG_PILOT_DECISION.md`
- `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md`
- `docs/AUDIT_RECEIPT_PILOT_REVIEW.md`
- `docs/MINIMAL_EVAL_HARNESS_DESIGN.md`
- `docs/AI_HANDOFF.md`
- `docs/CHANGE_CONTROL.md`
- `docs/HUMAN_APPROVALS.md`
- `docs/PROMPT_PATTERNS.md`

Exact candidate patterns:

- `docs/adr/*.md`
- `docs/RELEASE_RECORD_*.md`
- `docs/CLEAN_CLONE_VALIDATION_*.md`

Pattern matches remain subject to the forbidden-corpus rules below. A matching
file is not eligible for future digest generation if it contains forbidden
material, raw private data, unredacted live values, generated downstream source,
or external/private corpus material.

### Explicit excluded files and patterns

The following files and patterns are excluded by default:

- `.git/**`
- `.github/workflows/**`
- `artifacts/**`
- `local/**`
- `corpus/**`
- `retrieval/**`
- `index/**`
- `evals/golden/**`
- generated target output or generated downstream source under any path;
- RSID raw evidence or review output unless separately redacted and approved;
- `08_Study` raw note content unless separately curated into safe short
  summaries;
- downstream repository material unless separately approved as a redacted,
  repo-facing summary;
- binaries, installers, drivers, DLLs, archives, or unknown executable content;
- files containing secrets, tokens, credentials, account identifiers, real IPs,
  ports, live endpoints, device values, broker/account values, equipment
  parameters, or live configuration.

External, private, and downstream material remains excluded by default even if
it is referenced by a safe planning document. Future generated corpus artifacts
require separate owner approval and a separate verification closeout.

### Safe metadata example rows

These rows show the intended metadata shape only. They do not compute real
hashes, generate a digest, or approve release-facing corpus artifacts.

| `source_path` | `git_sha` | `section_title` | `content_class` | `risk_label` | `allowed_for_digest` | `allowed_for_release` | `redaction_status` | `encoding_status` | `digest_algorithm` | `content_hash` | `verified_at` | `reviewer_or_approval_ref` | `notes` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `AGENTS.md` | `<future_git_sha>` | `Current Phase Rule` | `governance` | `baseline_policy` | `candidate_only` | `candidate_only` | `pending_future_check` | `pending_future_check` | `sha256` | `<future_sha256>` | `<future_verified_at>` | `<future_approval_ref>` | Candidate row only; no digest generated. |
| `docs/VERIFICATION.md` | `<future_git_sha>` | `Approved Corpus Digest Planning Flow` | `verification` | `verification_policy` | `candidate_only` | `candidate_only` | `pending_future_check` | `pending_future_check` | `sha256` | `<future_sha256>` | `<future_verified_at>` | `<future_approval_ref>` | Future digest task must rerun safety scans. |
| `docs/AUDIT_TRACE_SCHEMA.md` | `<future_git_sha>` | `CI/run evidence fields` | `audit` | `approval_boundary` | `candidate_only` | `candidate_only` | `pending_future_check` | `pending_future_check` | `sha256` | `<future_sha256>` | `<future_verified_at>` | `<future_approval_ref>` | Receipt linkage only; no audit automation. |
| `docs/OPTIONAL_RAG_PILOT_DECISION.md` | `<future_git_sha>` | `Decision` | `planning` | `historical_risk_evidence` | `candidate_only` | `candidate_only` | `pending_future_check` | `pending_future_check` | `sha256` | `<future_sha256>` | `<future_verified_at>` | `<future_approval_ref>` | Historical evidence, not a blocker. |
| `docs/adr/ADR-0001-local-first.md` | `<future_git_sha>` | `<future_section_title>` | `architecture_decision` | `baseline_policy` | `candidate_only` | `candidate_only` | `pending_future_check` | `pending_future_check` | `sha256` | `<future_sha256>` | `<future_verified_at>` | `<future_approval_ref>` | Pattern candidate; include only if present and clean. |

## 5. Forbidden corpus

The approved corpus must exclude:

- private raw input;
- business source text;
- full prompt transcripts;
- model output transcripts;
- unredacted tool-call request or response bodies;
- secrets, tokens, credentials, or account identifiers;
- real IP, port, live endpoint, device value, broker/account value, or
  equipment parameter;
- live configuration;
- generated downstream target output;
- raw downstream implementation details;
- RSID raw evidence or review output unless separately redacted and approved;
- `08_Study` personal vault content unless separately curated into safe short
  summaries;
- binaries, installers, drivers, DLLs, or unknown executable content;
- local Windows absolute paths.

If a document mixes safe governance text with forbidden material, exclude it
until a separate task approves redaction and inclusion.

## 6. Required metadata fields

Future digest entries must include these fields:

| field | meaning |
|---|---|
| `source_path` | Repo-relative source path. |
| `git_sha` | Commit SHA used as the source basis. |
| `section_title` | Section heading or stable section label. |
| `content_class` | Candidate class such as governance, verification, audit, eval, release, or roadmap. |
| `risk_label` | Conservative risk label from this plan. |
| `allowed_for_digest` | Whether the entry is approved for digest inclusion. |
| `allowed_for_release` | Whether the entry is safe to reference in release-facing evidence. |
| `redaction_status` | Redaction check state. |
| `encoding_status` | Encoding check state. |
| `digest_algorithm` | Hash algorithm name, such as `sha256`. |
| `content_hash` | Hash of the approved normalized content unit. |
| `verified_at` | Verification timestamp or approved stable review timestamp. |
| `reviewer_or_approval_ref` | Approval pointer, not raw approval transcript. |
| `notes` | Short safe notes. |

Metadata must not copy raw private data, raw source text, tool-call bodies,
prompt transcripts, local absolute paths, or sensitive values.

## 7. Risk labels

Allowed risk labels:

| label | use |
|---|---|
| `baseline_policy` | Current repository policy or operating contract. |
| `safety_boundary` | Safety, redaction, live-target, or private-data boundary. |
| `approval_boundary` | Approval rule, side-effect gate, or human decision boundary. |
| `verification_policy` | Verification instructions or closeout rules. |
| `release_evidence` | Release record, clean-clone record, or release-evidence policy. |
| `historical_record` | Historical evidence that remains relevant. |
| `deprecated_or_historical` | Superseded or deferred material that must not be read as current approval. |
| `external_context_summary` | Separately approved safe summary of external context. |
| `forbidden_private_or_raw` | Material classified as excluded from corpus use. |

Historical records must receive labels that prevent old deferrals, old release
states, or probe records from being treated as current implementation approval.

## 8. Digest and hash policy

A future digest should use content hashes to support source traceability without
copying large source blocks into receipts or reports.

Policy:

- use `sha256` unless a later task approves another algorithm;
- hash only approved normalized content units;
- record the source basis commit in `git_sha`;
- keep source paths repo-relative;
- do not hash private raw data as a way to include it;
- do not treat a hash as redaction;
- do not generate digest artifacts in this task;
- do not update release checksums or release manifests as part of this plan.

Any future digest artifact must be separately approved with exact path,
format, input list, verification commands, and retention expectations.

## 9. Redaction and encoding checks

Before any source is approved for digest inclusion, a future task must check:

- no private raw input;
- no business source text;
- no prompt transcript or model output transcript;
- no unredacted tool-call request or response body;
- no secret, credential, token, account identifier, or assigned sensitive
  value;
- no real IP, port, live endpoint, broker/account value, device value, or
  equipment parameter;
- no local Windows absolute path;
- UTF-8 readable text or explicitly approved encoding handling;
- stable section boundaries suitable for metadata.

Encoding damage is a reason to exclude a source until a separate review resolves
it. Redaction must create safe summaries or identifiers, not partial raw-data
copies.

## 10. Source path policy

Digest metadata must use repo-relative paths only.

Allowed path forms:

- root files such as `AGENTS.md`;
- `docs/...` paths;
- `docs/adr/...` paths;
- other repo-owned documentation paths approved by exact file or pattern.

Forbidden path forms:

- local absolute paths;
- user home paths;
- drive-letter paths;
- external repository paths copied into metadata as local paths;
- URLs used as corpus source paths unless a later task approves an external
  context summary record.

The source path identifies a repository document. It must not identify private
vault content, a downstream checkout, or local machine-specific evidence.

## 11. 08_Study boundary

`08_Study` is not part of the approved corpus by default.

It may not be copied wholesale, indexed, digested, summarized from private
notes, or used as raw source material in this repository. If a later task needs
general knowledge-database context, it may propose a curated, short,
repository-owned summary only after separate approval.

Any approved summary must:

- avoid personal vault content;
- avoid business source text;
- avoid local absolute paths;
- avoid private identifiers and sensitive values;
- be labeled `external_context_summary`;
- cite only the approval record and safe summary, not raw note content.

## 12. RSID / downstream evidence boundary

RSID raw evidence, review output, implementation references, downstream review
outputs, generated downstream target output, and raw downstream implementation
details are excluded by default.

They may enter corpus planning only as separately approved safe summaries after
redaction. The summary must avoid raw source, environment values, device or
equipment values, live endpoints, local paths, private review text, and
implementation excerpts.

Downstream repositories remain governed by their own task contracts and
approval records. `codex-dev-harness` must not ingest downstream private
material as corpus data.

## 13. Future artifact boundary

No digest artifact is generated in this task.

A future artifact task must separately approve:

- artifact path;
- source allow-list;
- source exclusions;
- metadata schema;
- normalization rules;
- hash algorithm;
- redaction and encoding checks;
- whether artifact files may be committed;
- whether release checksums or manifests may reference the artifact;
- verification commands;
- closeout fields.

The future artifact must not be created by implication from this plan.

## 14. Future implementation order

Required order after this plan:

1. owner reviews and approves this documentation-only plan;
2. create an exact approved corpus allow-list and exclusion list;
3. define digest artifact format and review example metadata rows;
4. implement digest generation only if separately approved;
5. verify digest generation without RAG or index creation;
6. only then consider local RAG over the approved digest basis.

Do not create `corpus/`, `retrieval/`, `index/`, digest scripts, embeddings,
vector storage, external service integrations, CI integration, quality-gate
integration, or audit automation before the relevant phase is separately
approved.

## 15. Success criteria

Phase 6 planning succeeds when:

- corpus digest is documented as the predecessor to local RAG;
- approved candidate classes are limited to safe repo-owned policy,
  governance, verification, roadmap, architecture, ADR, release, CI, audit,
  eval, and approved-corpus planning documents;
- external, private, and downstream raw material is excluded by default;
- `08_Study` and RSID/downstream evidence boundaries are explicit;
- required metadata fields and risk labels are defined;
- redaction, encoding, source path, and hash policies are documented;
- no digest artifact, RAG code, retrieval folder, index folder, corpus folder,
  embeddings, vector database, external service, CI integration,
  quality-gate integration, audit automation, MCP/Hermes implementation,
  release automation, downstream edit, artifact regeneration, or eval report
  generation occurs.

## 16. Closeout requirements

Closeouts for approved corpus digest planning tasks must report:

- final status label;
- changed files;
- corpus digest plan summary;
- approved corpus candidate classes;
- forbidden corpus boundary;
- `08_Study` boundary;
- RSID/downstream evidence boundary;
- future implementation boundary;
- verification command results;
- safety scan results;
- whether a local commit was created;
- whether push, tag, release, artifact regeneration, digest generation, eval
  report generation, RAG, index, retrieval, embeddings, vector storage, or
  external service use occurred;
- next recommended task.

If a future task does not generate a digest artifact, record that as `NOT RUN`
or `not generated` rather than implying digest verification passed.

## 17. Next task prompt

```text
Repository:
esj1123/codex-dev-harness

Task:
Review and locally commit the approved corpus allow-list refinement.

Goal:
Complete final verification for the Phase 6B approved corpus allow-list and
metadata refinement, then create one local documentation commit only if the
owner approves the diff.

Read first:
- AGENTS.md
- STATUS.md
- docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md
- docs/APPROVED_CORPUS_DIGEST_PLAN.md
- docs/APPROVED_CORPUS_RAG_PLAN.md
- docs/OPTIONAL_RAG_PILOT_DECISION.md
- docs/AUDIT_TRACE_SCHEMA.md
- docs/VERIFICATION.md

Required boundaries:
- documentation-only
- no digest artifact
- no generated corpus artifact
- no RAG code
- no retrieval folder
- no index folder
- no corpus folder
- no embeddings
- no vector database
- no external service
- no CI or quality-gate integration
- no audit automation
- no MCP/Hermes implementation
- no release automation
- no downstream edit
- no private raw data, prompt transcript, tool-call body, live value, local
  absolute path, RSID raw evidence, or 08_Study raw note content

Closeout:
- PASS / PASS WITH NOTES / BLOCKED
- changed files
- exact allow-list summary
- excluded pattern summary
- metadata example summary
- forbidden corpus confirmation
- verification command results
- safety scan results
- whether a local commit was created
- whether digest generation, push, tag, release, artifact regeneration,
  generated corpus artifact creation, or eval report generation occurred
- next recommended task
```
