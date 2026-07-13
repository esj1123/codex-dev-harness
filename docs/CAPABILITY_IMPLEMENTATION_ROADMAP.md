# Capability Implementation Roadmap

## 1. Purpose

Record the owner intent that the deferred capability surfaces are final
implementation targets, and define the order needed to implement them safely.

The question is no longer whether CI, RAG, audit, eval integration, MCP,
Hermes, release automation, provenance, and downstream application are
justified at all. The question is what must come first so later capability
work has a verified source of truth, explicit approval boundary, redaction
model, and local-first safety basis.

This roadmap is documentation-only. It does not create workflows, install CI,
implement RAG, create embeddings, create a vector database, create retrieval or
index folders, automate audit logging, implement MCP, implement Hermes,
integrate evals into the quality gate, generate release artifacts, regenerate
artifacts, tag, push, publish, or edit downstream repositories.

## 2. Owner implementation intent

The owner intent is to eventually implement these capabilities in
`codex-dev-harness` and downstream repositories:

- CI.
- RAG.
- Audit / trace / receipt schema.
- Eval integration.
- MCP tool boundary.
- Hermes sidecar.
- Release automation / provenance.
- Downstream repo application.

Previous documents that deferred or rejected immediate implementation are not
permanent blockers. They are historical risk evidence, safety boundary
evidence, and sequencing evidence.

The intended implementation posture is:

- source-of-truth cleanup before automation;
- local-first by default;
- read-only review before side effects;
- exact-file and exact-artifact approvals;
- schema and metadata before automation;
- digest before retrieval;
- MCP boundary before sidecar behavior;
- release and downstream integration only after the earlier evidence chain is
  stable.

## 3. Historical decision records and reinterpretation

| record | historical decision | reinterpretation for implementation |
|---|---|---|
| `docs/OPTIONAL_RAG_PILOT_DECISION.md` | Do not start a RAG pilot at that time. | Not a permanent RAG blocker. It means RAG must start from approved corpus boundary, redaction, metadata, source digest, and local-first retrieval. |
| `docs/AUDIT_RECEIPT_PILOT_REVIEW.md` | Audit automation was not justified at that time. | Not a permanent audit blocker. It means audit automation must start schema-first, with redaction rules and no prompt or raw private-data capture. |
| `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md` | Keep CI deferred and template-only at that time. | Not a permanent CI blocker. It means CI must start as a read-only local verification mirror with no secrets, artifact upload, release, tag, deploy, or live write. |
| `docs/APPROVED_CORPUS_RAG_PLAN.md` | Plan approved-corpus retrieval without implementing it. | The corpus boundary is the precondition for digest and retrieval work. Candidate status does not authorize indexing. |
| `docs/EVAL_INTEGRATION_DECISION.md` | Keep evals standalone. | Eval output can become future evidence only after audit / trace / receipt fields are stable and integration scope is explicitly approved. |
| `docs/AUDIT_LOG_POLICY.md` | Define optional future audit fields without real logs or automation. | The schema is the natural starting point for trace and receipt work, but implementation must preserve redaction and identifier-first evidence. |
| `docs/PROMPT_PATTERNS.md` | Task contracts and closeout patterns are documentation-only. | Future implementation prompts should keep side-effect approval explicit and avoid bundling unrelated capabilities. |
| `docs/SIMPLIFICATION_CHECKLIST.md` | Add durable repo surface only with repeated evidence and approval. | Capability implementation should be phased, minimal, and nearest-surface first, not broad automation in one task. |
| `docs/STAGE_5B_STOCK_PRACTICAL_PROBE_CLOSEOUT.md` | Stock probe evidence did not justify immediate automation. | Stock practical sprint evidence is not a CI blocker. It is input for verification hygiene, docs-only verification policy, and temp-output policy. |

These records should be cited as a hazard log. They identify risks to control,
not capabilities to abandon.

## 4. Capability inventory

| capability | current state | target state | main dependency |
|---|---|---|---|
| Source of truth cleanup / repo state confirmation | Current and historical docs both exist; some docs still describe deferred defaults. | Confirm branch, local changes, upstream state, source docs, and owner-intent shift before implementation work. | None. |
| Capability Implementation Roadmap | This document. | Durable owner-intent and sequencing record. | Source of truth cleanup. |
| Read-only CI + verification hygiene | Manual read-only local verification workflow is installed; release CI, artifact upload, required checks, and additional workflows remain separately approval-gated. | Read-only verification mirror for existing local checks, with no secrets, uploads, release, tag, deploy, or live write. | Roadmap and source-of-truth confirmation. |
| Audit / trace / receipt schema | Audit schema and manual receipt review exist; no automation. | Stable schema, redaction rules, receipt fields, validation plan, and manual examples before automation. | Read-only verification hygiene. |
| JSON Evidence Core / Evidence Serialization Policy | Manual receipt schema exists; machine-readable receipt and trace schemas are now the next serialization foundation. | Policy, core schemas, and a quality-gate bundle check exist before any audit automation or real logs. | Audit / trace / receipt schema. |
| Eval/report integration | Standalone local eval runner exists; no quality-gate or CI integration by default. | Evidence-aligned report integration that can cite audit and receipt identifiers. | JSON Evidence Core / Evidence Serialization Policy. |
| Approved corpus digest | Approved-corpus plan exists; no digest or index. | Exact allow-list, metadata, redaction checks, encoding checks, and digest contract. | Eval/report and audit identifiers. |
| Local RAG | Phase 7B contract, Phase 7C standalone local lexical retriever, Phase 7C.4 ranking correction, and Phase 7D retrieval receipt evidence planning are complete; retrieval remains local-only, read-only, advisory-only, and not integrated into CI, quality gates, release, audit automation, MCP/Hermes, AgentOps, memory, or downstream repositories. | Local-first retrieval over the approved corpus, with retrieval output treated as advisory context and any receipt evidence implementation separately approval-gated. | Approved corpus digest and JSON evidence policy. |
| MCP tool boundary | Phase 8A boundary contract is documented and Phase 8B synthetic contract tests/review checks are present; no MCP runtime, Hermes sidecar, tool execution, quality-gate or CI integration, audit automation, external service, release automation, or downstream integration. | Explicit allowed tool classes, input/output rules, approval boundaries, redaction rules, and audit hooks. | Local RAG and audit rules. |
| Hermes sidecar | Phase 9A planning contract, Phase 9B synthetic contract tests/review checks, and Phase 9C implementation boundary planning are present; no sidecar runtime, background daemon, MCP runtime, tool execution, quality-gate or CI integration, audit automation, external service, release automation, or downstream integration. | Local sidecar constrained by the MCP boundary, audit model, eval evidence, and approval rules. | MCP tool boundary. |
| Release automation / provenance | Phase 10A boundary review, Phase 10B candidate contract, Phase 10C standalone read-only preflight, Phase 10C.1 usage probe, and Phase 10D refresh `HOLD` decision are complete; local evidence generators remain unautomated and no publication exists. | Approval-gated release automation and provenance flow after a stable digest-valid Phase 10 checkpoint satisfies the Phase 10D Proceed Conditions. | Current handoff synchronization, exact same-34-source digest freshness, and separate owner approval. |
| Downstream product integration | Phase 11A authority/data/access boundary, Phase 11B placeholder-only JSON contract, Phase 11C validator candidate, Phase 11D standalone validator, and Phase 11D.1/D.2 synthetic usage probes are complete; no downstream repository has been selected or accessed. | Any product-specific integration must begin with a separately approved target-selection contract under downstream repo rules; synthetic approval fields are not execution authority. | Current handoff synchronization, exact same-34-source digest freshness, and separate owner target approval. |

## 5. Dependency order

Required implementation order:

1. Source of truth cleanup / repo state confirmation.
2. Capability Implementation Roadmap.
3. Read-only CI + verification hygiene.
4. Audit / trace / receipt schema.
4B. JSON Evidence Core / Evidence Serialization Policy.
5. Eval/report integration.
6. Approved corpus digest.
7. Local RAG.
8. MCP tool boundary.
9. Hermes sidecar.
10. Release automation / provenance.
11. Downstream product integration.

Steps 1 and 2 are governance preparation. The first implementation target after
this roadmap is read-only CI + verification hygiene.

The order matters:

- source-of-truth cleanup prevents stale deferred docs from being misread as
  current owner intent;
- the roadmap records the new owner intent before implementation starts;
- CI hygiene gives future phases a repeatable verification mirror;
- audit / trace / receipt schema defines what evidence future phases can cite;
- JSON Evidence Core defines the safe serialization bundle before logs or
  automation exist;
- eval/report integration should not precede the receipt fields it needs;
- approved corpus digest must precede retrieval;
- local RAG must precede tool-facing context integration;
- MCP tool boundaries must precede Hermes;
- release automation and downstream product integration come last because they
  carry the highest publication, retention, and product-coupling risks.

## 6. Phase plan

### Phase 1: source of truth cleanup / repo state confirmation

Goal:

- Confirm branch, upstream, local changes, staged state, and untracked state.
- Identify docs that still describe historical deferral.
- Record whether local commits are pushed, unpushed, or absent.
- Avoid treating `main` and `origin/main` as equivalent without checking.

Gate:

- `git status --short --branch` or equivalent is recorded.
- Any existing local changes are classified.
- No source-of-truth update broadens implementation approval by itself.

### Phase 2: Capability Implementation Roadmap

Goal:

- Create this document as the owner-intent and sequencing record.
- Reinterpret historical optional decisions as risk evidence.
- Define the first implementation target and later dependency order.

Gate:

- Only this roadmap changes unless a direct contradiction forces another docs
  edit.
- Required safety scans pass or policy-only matches are explained.
- Release verification and artifact regeneration remain `NOT RUN` by scope.

### Phase 3: read-only CI + verification hygiene

Goal:

- Implement the first capability target after this roadmap.
- Mirror existing local verification in a read-only CI or CI-adjacent hygiene
  path.
- Keep manual or explicitly approved triggers at first.

Must not include by default:

- secrets;
- artifact upload;
- release publication;
- signing;
- tag creation or movement;
- deployment;
- downstream repo access;
- RAG;
- audit automation;
- eval quality-gate integration;
- MCP or Hermes;
- live write.

Gate:

- Workflow or hygiene path is explicitly approved.
- Permissions, triggers, commands, and no-publication boundaries are recorded.
- CI output is treated as verification evidence, not release publication.

### Phase 4: audit / trace / receipt schema

Goal:

- Stabilize schema fields for task id, actor, repo basis, local/remote state,
  approval reference, files changed, commands run, verification result, safety
  exclusions, redaction status, eval run id, corpus digest, and side-effect
  class.
- Preserve manual receipt precision before any automation.

Must not include by default:

- raw prompt capture;
- raw private data capture;
- raw source bundles;
- unredacted tool-call bodies;
- command-output bulk capture;
- automatic audit logging.

Gate:

- Schema and examples use repo-relative paths, identifiers, summaries, and
  hashes.
- PASS, PASS WITH NOTES, BLOCKED, NOT RUN, and ENVIRONMENT BLOCKED semantics
  are explicit.
- Local commit, local branch-ahead, push, tag, and release states are
  distinguished.

### Phase 4B: JSON Evidence Core / Evidence Serialization Policy

Goal:

- Define the JSON evidence serialization policy for receipt summaries and trace
  events.
- Add the core machine-readable schemas for safe receipt summaries and trace
  events.
- Gate the policy and schema bundle through `scripts/quality_gate.py` without
  validating or writing real audit logs.

Must not include by default:

- audit automation;
- real audit logs;
- generated receipt or trace files;
- raw prompt capture;
- raw private data capture;
- raw command log capture;
- unredacted tool-call bodies;
- eval summary/cases split;
- RAG, embeddings, vector database, retrieval, MCP runtime, Hermes sidecar,
  AgentOps runtime, memory runtime, release automation, or downstream changes.

Gate:

- `docs/JSON_EVIDENCE_POLICY.md`,
  `audits/receipt-summary.schema.json`, and
  `audits/trace-event.schema.json` form one required bundle when roadmap or
  status documents contain a Phase 4B or JSON Evidence Core marker.
- A synthetic repository with no bundle files and no marker may be treated as
  not applicable.
- Partial bundles fail.
- The quality gate parses the schemas and checks core shape and policy safety
  language using standard-library code only.

### Phase 5: eval/report integration

Goal:

- Connect standalone eval results to durable evidence after receipt fields are
  stable.
- Decide whether the first integration is report-only, opt-in gate, CI use, or
  another scoped mode.

Must not include by default:

- default quality-gate integration;
- release-blocking semantics;
- external services;
- LLM judge;
- routine report generation;
- CI integration beyond the approved phase.

Gate:

- Report fields align with audit / trace / receipt schema.
- False-positive and false-negative risks are documented.
- Default local eval behavior remains unchanged unless explicitly approved.

### Phase 6: approved corpus digest

Goal:

- Define exact corpus files or patterns, exclusions, metadata, risk labels,
  redaction checks, encoding checks, and digest format.
- Produce a digest contract before retrieval or indexing.

Must not include by default:

- private raw data;
- prompt/session transcripts;
- model outputs;
- downstream generated output;
- live configuration;
- sensitive values;
- retrieval/index folder;
- embeddings;
- vector database.

Gate:

- Owner approves the exact allow-list and forbidden corpus list.
- Digest input is repo-relative and release-safe.
- Historical records receive risk labels so deferred plans are not treated as
  approval.

### Phase 7: local RAG

Goal:

- Add local-first retrieval only after approved corpus digest discipline is
  proven.
- Treat retrieval output as advisory context, not approval.
- Keep the completed Phase 7B contract, Phase 7C standalone retriever, Phase
  7C.4 ranking correction, and Phase 7D receipt evidence planning separate from
  quality-gate, CI, release, audit automation, MCP/Hermes, AgentOps, memory, and
  downstream integration unless a later task explicitly approves those
  connections.

Must not include by default:

- external retrieval services;
- broad corpus ingestion;
- private or downstream raw data;
- approval bypass;
- live target permissions.

Gate:

- Retrieval uses only the approved corpus basis.
- Generated indexes or dependencies are exact-file and exact-command approved.
- Retrieval output cannot broaden the current task contract.
- Phase 7B defined allowed inputs, output shape, citation rules, no-answer
  behavior, and verification requirements; Phase 7C added only a standard
  library, read-only, advisory lexical retriever; Phase 7D aligned retrieval
  evidence references with JSON receipt and trace schemas.
- Phase 7 does not, by default, authorize a corpus folder, retrieval folder,
  index folder, embeddings, vector storage, external services, MCP/Hermes
  behavior, release automation, downstream integration, generated receipts, real
  audit logs, query-matrix automation, or quality-gate/CI integration.

### Phase 8: MCP tool boundary

Goal:

- Define allowed MCP tool classes, forbidden calls, input/output redaction,
  audit references, approval rules, and failure handling.
- Separate boundary definition from runtime implementation.
- Phase 8A documents the boundary contract in
  `docs/MCP_TOOL_BOUNDARY_CONTRACT.md` without implementing runtime behavior.
- Phase 8B adds synthetic contract tests and a review note without implementing
  runtime behavior.

Must not include by default:

- unknown executable execution;
- installer, driver, DLL, or binary execution;
- live endpoint calls;
- downstream mutation;
- release publication;
- approval-free side effects.

Gate:

- Read-only inspection, local generation, approval-gated side effects, and
  forbidden live behavior are distinct classes.
- Tool-call evidence avoids raw prompts, private data, raw source, live values,
  and secrets by default.
- Downstream repo rules remain authoritative for downstream work.

### Phase 9: Hermes sidecar

Goal:

- Implement the sidecar only after the MCP tool boundary is explicit and tested.
- Keep sidecar behavior local-first and approval-gated.
- Document the sidecar planning contract before any sidecar runtime behavior is
  implemented.
- Verify the planning contract with synthetic documentation tests before any
  runtime implementation is considered.
- Document the implementation boundary, failure taxonomy, and exact approval
  gates before any minimal no-op sidecar runtime is approved.

Must not include by default:

- product mutation;
- external sends;
- release publication;
- live target action;
- unapproved device behavior;
- unapproved downstream writes.

Gate:

- Sidecar inputs, outputs, logs, and evidence follow the audit and corpus
  rules.
- Failure modes are documented and tested.
- No sidecar behavior bypasses task contracts, approval records, or safety
  invariants.
- The first runtime task, if approved later, names exact files, commands,
  safety tests, cleanup rules, and side-effect boundaries.

### Phase 10: release automation / provenance

Goal:

- Automate approved release evidence and provenance steps only after CI,
  audit, eval, digest, RAG, MCP, and Hermes surfaces are stable.

Must not include by default:

- publication;
- signing;
- tag movement;
- artifact upload;
- archive generation;
- downstream product release.

Gate:

- Exact artifacts, retention, signing, publication, tag behavior, rollback, and
  verification commands are approved.
- Local source-basis commit, artifact-containing commit, push, tag, and release
  states are distinguished.

Current implementation state:

- Phase 10A records the release automation and provenance boundary without
  automation or publication.
- Phase 10B selects the local release evidence preflight dry-run candidate.
- Phase 10C implements the standalone standard-library, local-only, read-only
  preflight without generator execution or persistence.
- Phase 10C.1 records a synchronized-tip `PASS WITH NOTES` usage probe with
  `EVIDENCE_REFRESH_RECOMMENDED` and no runtime patch.
- Phase 10D keeps release evidence regeneration at `HOLD` until a stable Phase
  10 checkpoint satisfies every documented Proceed Condition.
- Tag movement, release creation, signing, upload, publication, workflow
  expansion, and downstream behavior remain separately approval-gated.

### Phase 11: downstream product integration

Goal:

- Apply the governed capability chain to downstream repositories under each
  downstream repository's rules.

Must not include by default:

- downstream edits from this roadmap task;
- downstream private data capture;
- live endpoint, broker, account, device, or equipment values;
- bypass of downstream approval records.

Gate:

- Downstream task contract names allowed files, forbidden actions, verification,
  and closeout requirements.
- Downstream evidence is summarized safely and does not copy raw sensitive
  content into `codex-dev-harness`.

Current implementation state:

- Phase 11A documents owner and downstream-repository authority precedence,
  selected-field evidence boundaries, access classes, side-effect separation,
  fail-closed behavior, and explicit non-goals without downstream access.
- Phase 11B adds a deterministic placeholder-only JSON task-contract fixture
  with 16 independent side-effect permission records fixed to unapproved and
  `NOT RUN`.
- Phase 11C selects and contracts a standalone validator without implementing or
  executing it.
- Phase 11D implements the standard-library-only, local-only, read-only,
  dry-run-only validator for one explicitly supplied JSON contract. It does not
  inspect a downstream repository, execute declared commands, authenticate
  approval evidence, persist output, or authorize side effects.
- Phase 11D.1 records `PASS WITH NOTES / SYNTHETIC_CONTRACT_VALID` for the
  tracked placeholder fixture with all permissions unauthorized and all
  external states `NOT RUN`.
- Phase 11D.2 records `PASS` for one temporary synthetic filled contract,
  proves cleanup, and confirms that a filled-mode validation result is internal
  consistency evidence rather than external authorization.
- No downstream repository, path, branch, remote, source, private data, render,
  write, workflow, release, deploy, or live action is selected or executed.
- Any Phase 11E work must first select `HOLD` or define a separately approved
  target-selection contract before any real downstream access.

## 7. Safety invariants

All phases preserve these invariants:

- local-first by default;
- read-only review first;
- explicit side-effect boundary;
- no unapproved live write;
- no private raw data;
- no secrets, tokens, credentials, account identifiers, or real config values;
- no real IP, port, device value, live endpoint, broker/account value, or
  equipment parameter in repo-facing text;
- no unknown executable, installer, driver, DLL, or binary execution;
- no broad refactor;
- no implementation without phase decision;
- do not mark unrun verification as PASS;
- report PASS, PASS WITH NOTES, BLOCKED, NOT RUN, and ENVIRONMENT BLOCKED
  honestly;
- distinguish local commit from remote push;
- distinguish source-basis commit from artifact-containing commit when release
  evidence is involved;
- do not let historical records silently grant approval for current side
  effects.

## 8. Approval boundaries

Each implementation phase requires a separate owner approval.

Approval must identify:

- target phase and capability;
- exact files, directories, workflows, scripts, schemas, artifacts, or
  downstream repositories in scope;
- side-effect class;
- allowed commands;
- forbidden commands and forbidden actions;
- whether generated artifacts may be created or committed;
- whether network, cloud CI, external services, MCP calls, or sidecars are
  allowed;
- whether reports, audit entries, corpus digests, indexes, retrieval outputs,
  or release evidence may be generated;
- verification commands;
- closeout criteria;
- explicit exclusions for private data, secrets, live targets, publication,
  tags, pushes, release artifacts, and downstream edits.

Broad approval to improve automation, context, quality, reliability, release
confidence, or agent integration is not enough to cross these boundaries.

## 9. First implementation target

The first implementation target after this roadmap was:

- read-only CI + verification hygiene.

That target is now installed as the manual read-only Local Verify workflow. The
completed sequence has since advanced through audit/trace/receipt schema, JSON
Evidence Core, eval/report evidence, approved corpus digest, and standalone
local RAG work. The current next recommended task is tracked in `STATUS.md`.

The dependency targets remain:

- second: audit / trace / receipt schema;
- Phase 4B: JSON Evidence Core / Evidence Serialization Policy;
- third: eval/report integration;
- fourth: approved corpus digest;
- fifth: local RAG;
- sixth: MCP tool boundary;
- seventh: Hermes sidecar;
- later: release automation and downstream product integration.

The first target should verify current repository hygiene without adding
release behavior. It should mirror local checks, keep permissions read-only,
avoid secrets, avoid artifact upload, avoid tags, avoid deployment, and avoid
live write. It should also improve closeout precision by reporting local and
remote state clearly.

## 10. Per-capability success criteria

| capability | success criteria |
|---|---|
| Source of truth cleanup / repo state confirmation | Branch, upstream, local changes, staged state, untracked state, and local-vs-remote status are reported before implementation. Historical deferral docs are classified as historical risk evidence. |
| Capability Implementation Roadmap | This document exists, records owner intent, lists the dependency order, and sets read-only CI + verification hygiene as the first implementation target. |
| Read-only CI + verification hygiene | Approved verification path runs existing local checks in read-only mode, with no secrets, artifact upload, release, tag, deploy, downstream edit, or live write. |
| Audit / trace / receipt schema | Schema and manual examples capture outcome, git state, approvals, files, commands, verification, safety exclusions, redaction status, and NOT RUN reasons without raw private data. |
| JSON Evidence Core / Evidence Serialization Policy | Policy and core schemas define safe receipt-summary and trace-event JSON serialization, are checked by the quality gate, and do not create audit automation or real logs. |
| Eval/report integration | Eval reports cite stable receipt fields, remain non-LLM and local unless separately approved, and do not become default gate or release-blocking behavior without explicit approval. |
| Approved corpus digest | Exact safe corpus allow-list, forbidden corpus list, metadata, risk labels, redaction checks, encoding checks, and digest format are approved and verified. |
| Local RAG | Phase 7B contract defines digest-only inputs, repo-relative citations, no-answer behavior, and future verification requirements; Phase 7C provides a standalone read-only lexical retriever over the approved corpus digest; Phase 7D defines receipt evidence references without creating receipts or audit logs. Retrieval remains local-first, limited to the approved corpus basis, advisory only, and unable to broaden approval or side-effect permissions. |
| MCP tool boundary | Tool classes, inputs, outputs, logs, redaction, approvals, and forbidden behavior are documented and tested before sidecar implementation. |
| Hermes sidecar | Sidecar behavior is local-first, constrained by MCP boundary and audit rules, has tested failure modes, uses bounded reason codes, and cannot bypass task or downstream repo contracts. |
| Release automation / provenance | Automation names exact artifacts and publication-adjacent behavior, distinguishes local commit from push/tag/release, and does not publish or move tags without explicit approval. |
| Downstream product integration | Downstream repo work uses repo-local rules, safe summaries, explicit approvals, and no private raw data or live values in harness-facing records. |

## 11. Closeout criteria

Every phase closeout must report:

- PASS, PASS WITH NOTES, BLOCKED, NOT RUN, or ENVIRONMENT BLOCKED where
  applicable;
- changed files and files intentionally not touched;
- commands run and command-by-command results;
- commands intentionally not run and reasons;
- generated artifacts, or confirmation that none were generated;
- local commit state, push state, tag state, and release state when relevant;
- safety exclusions checked;
- approval basis;
- unresolved risks or assumptions;
- next recommended task.

For this roadmap task, closeout must confirm:

- only `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` changed;
- no `.github/workflows` creation occurred;
- no CI installation occurred;
- no RAG code, embeddings, vector database, retrieval/index folder, audit
  automation, MCP implementation, Hermes implementation, or eval quality-gate
  integration was added;
- no release artifacts were created or regenerated;
- no release verification was run;
- no tag, push, release publication, commit, or downstream repo edit occurred
  unless separately requested and approved;
- path, sensitive-term, and IP-like scans were run and results were reported
  honestly.

## 12. Current sequencing handoff

The current locally verified implementation source baseline is Phase 11D.2
commit `0734a87b554eb1da8812e20346305dcdb2a2ae2e`. The active cumulative closeout
sequence is:

1. the Phase 11D.2 temporary synthetic filled-contract probe source commit;
2. this documentation-only current handoff synchronization commit;
3. an exact same-34-source corpus digest freshness commit;
4. a digest-valid stable checkpoint confirmation;
5. an owner decision to keep downstream integration on `HOLD` or separately
   approve a Phase 11E downstream target-selection contract.

The handoff commit may change only `STATUS.md` and this roadmap. `STATUS.md` is
excluded from the approved stable corpus; this roadmap is included. The expected
post-handoff digest state is therefore 34 sources, 33 valid sources, and this
roadmap as the only stale source.

The digest refresh must preserve exact source membership, ordering, and the
allow-list. Only the final digest-valid cumulative tip should be pushed and used
for Local Verify. Run and job identifiers belong in closeout evidence rather
than another roadmap edit.

Phase 11E must remain target-contract-first. Synthetic approval booleans and
permission records are not authenticated authority. A future task must name the
target authority, safe repository alias, access class, exact commands, allowed
files, no-touch paths, verification, cleanup, and each permitted side effect
before selecting or accessing a real downstream repository. It must not widen
schema, quality-gate, workflow, release, MCP, Hermes, audit, or live behavior
without separate approval.

Release evidence regeneration remains `HOLD` after digest freshness. A later
refresh still requires a separate owner-approved exact-file and exact-command
task. This sequence does not authorize release publication, signing, tag
movement, artifact upload, workflow expansion, audit automation, MCP or Hermes
runtime expansion, downstream access, deployment, or live behavior.
