# Local RAG Volatile Authority Policy

## 1. Purpose

Define Phase 7C.3A retrieval-authority policy for local RAG evidence.

This policy separates stable policy, volatile current state, mixed-temporal
documents, historical evidence, generation-time artifact snapshots, and live
repository state so future retrieval behavior can cite evidence without
pretending that every digest-listed source has the same authority.

## 2. Scope and non-goals

In scope:

- documentation-only authority vocabulary;
- initial source classification;
- retrieval precedence;
- conflict, partial, and no-answer rules;
- source-basis versus observed-HEAD semantics;
- generation-time versus live-status evidence;
- future phase boundaries.

Non-goals:

- no retriever patch;
- no digest change or digest refresh;
- no corpus allow-list change;
- no `STATUS.md` or `ACCEPTANCE_TRACE.md` change;
- no volatile overlay runtime;
- no config JSON or schema JSON;
- no test patch;
- no quality-gate integration;
- no CI workflow edit or CI integration;
- no receipt or audit automation;
- no release verification;
- no artifact regeneration;
- no `corpus/`, `retrieval/`, or `index/` directory;
- no embeddings, vector database, external service, or LLM judge;
- no MCP/Hermes, AgentOps, or memory runtime;
- no downstream access;
- no raw `08_Study` notes or private/raw corpus material;
- no commit or push for this policy document in this task;
- no tag, release, publication, or artifact upload.

## 3. Evidence basis

Gate 0 Local Verify for the Phase 7C.2B review commit passed before this
policy document was created.

| item | value |
|---|---|
| repository | `esj1123/codex-dev-harness` |
| branch | `main` |
| policy starting HEAD | `909b0071082b1bed7673749143ef2cb352e32cb6` |
| origin/main | `909b0071082b1bed7673749143ef2cb352e32cb6` |
| Phase 7C.2B evidence | `docs/LOCAL_RAG_RETRIEVER_POST_REFRESH_LOGICAL_VERIFICATION.md` |
| Gate 0 workflow | `Local Verify` |
| Gate 0 run | `27872762700` |
| Gate 0 job | `82487216926` |
| Gate 0 conclusion | `success` |
| artifact upload status | none |
| digest artifact | `artifacts/corpus-digest.json` |
| digest source-basis commit | `ce9e736ff8645aa592eadc1ad5b3bb9021a23c6d` |
| digest artifact-containing commit | `1d79773949f8d97fbcabed6238ef686606f2068d` |
| current digest integrity | `source_count=32`, `valid=32`, `stale=0`, `refresh_required=false` |

Gate 0 step results:

| step | result |
|---|---|
| Checkout | PASS |
| Set up Python | PASS |
| Show Python version | PASS |
| Install development requirements | PASS |
| Run tests | PASS |
| Run quality gate | PASS |
| Render python_cli example dry-run | PASS |
| Render csharp_desktop example dry-run | PASS |
| Render plc_tool example dry-run | PASS |
| Permissions | `contents: read` in `.github/workflows/local-verify.yml` |

## 4. Normative terminology

Temporal class and authority level are separate concepts.

A source can be cryptographically fresh but operationally lagging. A source can
be durable policy but not current operational state. A source can be
historically useful but unable to grant current approval.

Temporal classes:

- `stable_current_authority`: current rules expected to change slowly, such as
  operating contracts and verification policy.
- `volatile_current_authority`: current state that may change after commits,
  pushes, workflow runs, closeouts, or phase transitions.
- `mixed_temporal_evidence`: a document containing more than one temporal
  layer, such as future task contracts, completed closeouts, and current policy
  in one file.
- `historical_planning_evidence`: past decisions, probes, release records, and
  reviews that remain useful context but cannot grant current approval.
- `generation_time_snapshot`: metadata captured at artifact generation time,
  especially before later commit, push, CI, or review closeout.

Authority levels:

- `controlling_contract`: active task contract and explicit human approval.
- `current_operational_state`: current phase, current next step, current
  verification state, and current pushed/unpushed status.
- `durable_policy`: stable operating, safety, verification, schema, and
  roadmap rules.
- `supporting_policy`: policy context that helps interpret durable policy but
  may require section-level or temporal filtering.
- `historical_context`: prior decisions, risk evidence, release history, and
  completed reviews.
- `non_authoritative_snapshot`: generated metadata that records one moment in
  time and must not be read as live state.

## 5. Authority classes

`stable_current_authority`:

- May answer durable-policy questions.
- May answer current-state questions only when the question is about the policy
  itself.
- May be sole basis for durable-policy answers.
- Must not grant or imply side-effect approval.
- Belongs in the stable digest when it is repo-owned, safe, and exact-file
  approved.

`volatile_current_authority`:

- May answer current-state questions.
- May answer durable-policy questions only when it cites or summarizes current
  state under an existing policy.
- May be sole basis for current-state answers only when read from committed
  observed HEAD and not in conflict.
- Must not grant or imply side-effect approval.
- Belongs in a future volatile committed-HEAD overlay, not as the sole stable
  digest authority.

`mixed_temporal_evidence`:

- May answer durable-policy questions only from current-policy sections.
- May not be sole basis for current-state answers unless section authority is
  known and current.
- Must not grant or imply approval from future task contracts or completed
  plan language.
- Belongs in the stable digest only with section-aware interpretation, or in a
  historical layer when section authority is unavailable.

`historical_planning_evidence`:

- May answer historical-decision questions.
- May support risk context.
- Must not be sole basis for current operational state or current approval.
- Belongs in the stable digest as labeled historical evidence when approved,
  or in a separate historical evidence layer.

`generation_time_snapshot`:

- May answer artifact-generation questions.
- Must not answer live repository state unless the question explicitly asks for
  generation-time metadata.
- Must not grant approval.
- Belongs inside generated artifacts or receipts as historical metadata.

## 6. Initial source classification

| source | temporal class | authority level | current-state answer? | durable-policy answer? | sole current basis? | approval implication? | future layer |
|---|---|---|---|---|---|---|---|
| `AGENTS.md` | `stable_current_authority` | `controlling_contract` | Only for repo operating rules | Yes | Yes for operating rules | No | stable digest |
| `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md` | `stable_current_authority` | `durable_policy` | Yes for sequencing policy | Yes | Yes for roadmap order | No | stable digest |
| `docs/SAFETY_POLICY.md` | `stable_current_authority` | `durable_policy` | Yes for safety policy | Yes | Yes for safety rules | No | stable digest |
| `docs/VERIFICATION.md` | `stable_current_authority` | `durable_policy` | Yes for verification policy | Yes | Yes for verification commands | No | stable digest |
| `docs/AUDIT_TRACE_SCHEMA.md` | `stable_current_authority` | `durable_policy` | Yes for schema policy | Yes | Yes for receipt fields | No | stable digest |
| `docs/LOCAL_RAG_DESIGN.md` | `stable_current_authority` | `supporting_policy` | Only for Phase 7A design boundary | Yes | No for live state | No | stable digest if approved |
| `docs/LOCAL_RAG_IMPLEMENTATION_CONTRACT.md` | `stable_current_authority` | `supporting_policy` | Only for Phase 7B contract boundary | Yes | No for live state | No | stable digest if approved |
| `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md` | `stable_current_authority` | `durable_policy` | Yes for authority policy | Yes | Yes for authority policy | No | stable digest only after separate re-baseline approval |
| `STATUS.md` | `volatile_current_authority` | `current_operational_state` | Yes from committed observed HEAD | No, except summarized status | Yes when not conflicting | No | volatile overlay |
| `ACCEPTANCE_TRACE.md` | `volatile_current_authority` | `current_operational_state` | Yes from committed observed HEAD | No, except acceptance status | Yes when not conflicting | No | volatile overlay |
| `docs/APPROVED_CORPUS_DIGEST_PLAN.md` | `mixed_temporal_evidence` | `supporting_policy` | Section-specific only | Yes for corpus policy | No for live status | No | stable digest with section policy |
| `docs/APPROVED_CORPUS_RAG_PLAN.md` | `mixed_temporal_evidence` | `supporting_policy` | Section-specific only | Yes for RAG boundary | No for live status | No | stable digest with section policy |
| completed phase plans with future-current wording | `mixed_temporal_evidence` | `supporting_policy` | Section-specific only | Sometimes | No | No | mixed/historical layer |
| `docs/OPTIONAL_RAG_PILOT_DECISION.md` | `historical_planning_evidence` | `historical_context` | No | Historical context only | No | No | historical evidence |
| `docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md` | `historical_planning_evidence` | `historical_context` | No | Historical context only | No | No | historical evidence |
| release records | `historical_planning_evidence` | `historical_context` | No, except release history | No | No | No | historical evidence |
| clean-clone records | `historical_planning_evidence` | `historical_context` | No, except validation history | No | No | No | historical evidence |
| Local RAG usage probes | `historical_planning_evidence` | `historical_context` | No | Evidence context only | No | No | historical evidence |
| logical-verification and post-refresh review documents | `historical_planning_evidence` | `historical_context` | No | Evidence context only | No | No | historical evidence |
| closeout fields inside `artifacts/corpus-digest.json` | `generation_time_snapshot` | `non_authoritative_snapshot` | No live status | Artifact-generation context only | No | No | artifact metadata |
| generated artifact metadata describing pre-commit or pre-push state | `generation_time_snapshot` | `non_authoritative_snapshot` | No live status | Artifact-generation context only | No | No | artifact metadata |

Future removal of `STATUS.md` and `ACCEPTANCE_TRACE.md` from the stable digest
requires a separately approved corpus re-baseline task. This policy does not
change the digest now.

## 7. Control and retrieval precedence

Overall control precedence:

1. Current task contract and explicit human approval.
2. Repository operating contract such as `AGENTS.md`.
3. Volatile current-authority overlay for live state.
4. Stable current-authority corpus for durable rules.
5. Current-policy sections from mixed-temporal documents.
6. Historical/planning evidence.
7. Metadata-only evidence.

Retrieval must never:

- override the active task contract;
- grant side-effect approval;
- broaden allowed files;
- treat historical evidence as current authorization;
- infer approval from a phase plan, release record, or digest closeout.

## 8. Query intent classes

`current_state`:

- Examples: next recommended task, current phase, whether Phase 6G is complete,
  latest verification status.
- Required authority layer: volatile current authority from committed observed
  HEAD, plus task contract if relevant.
- Historical evidence may be returned only as context.
- Status must be `partial` when current sources conflict or only one volatile
  source is available for a disputed state.
- `no_sufficient_evidence` is required when committed observed-HEAD authority
  cannot be established.
- Conflicts must be disclosed directly.

`durable_policy`:

- Examples: local verification commands, safety policy, approval requirements,
  redaction rules.
- Required authority layer: stable current authority or current-policy section
  from mixed-temporal evidence.
- Historical evidence may be returned as context after current policy.
- Status must be `partial` when only historical policy is available.
- `no_sufficient_evidence` is required when no current policy source exists.
- Conflicts must identify which policy controls.

`historical_decision`:

- Examples: optional CI decision, why RAG was previously deferred, release
  history.
- Required authority layer: historical/planning evidence.
- Historical evidence is allowed and often primary.
- Status must not imply current approval.
- `no_sufficient_evidence` is required if only current summaries mention that a
  historical decision exists without enough detail.
- Conflicts must distinguish original decision from later superseding policy.

`mixed_context`:

- Examples: current corpus policy and its implementation history, current RAG
  authorization and prior planning.
- Required authority layer: stable policy plus section-aware mixed-temporal
  evidence; volatile state may be required for live completion.
- Historical evidence is allowed when labeled.
- Status must be `partial` when section authority is unknown.
- `no_sufficient_evidence` is required when current and historical claims
  cannot be separated.
- Conflicts must disclose temporal class and source basis.

## 9. Source-basis and observed-HEAD semantics

`source_basis_commit` is the commit whose normalized source content is
represented by a digest hash.

`observed_head_commit` is the committed repository HEAD observed at retrieval
time.

Rules:

- different commit IDs do not automatically mean hash staleness;
- current-state answers must disclose the observed HEAD;
- stable digest citations must disclose their source basis;
- volatile current authority must come from committed HEAD content;
- volatile overlay must not read dirty working-tree content;
- future implementation should use committed HEAD reads such as
  `git show HEAD:<repo-relative-path>`;
- missing or unreadable committed-HEAD authority must produce `partial` or
  `no_sufficient_evidence`, not a filesystem fallback.

This document defines policy only. It does not implement committed-HEAD reads.

## 10. Generation-time and live-status evidence

Artifact fields such as these describe generation-time evidence unless a later
schema explicitly defines otherwise:

- `artifact_commit_status`;
- `push_status`;
- `tag_status`;
- `release_status`;
- `unresolved_risks`;
- `next_step`;
- `json_validation_status`;
- `safety_scan_status`;
- `quality_gate_status`.

Rules:

- these fields must not be interpreted as live repository status;
- a digest must not be rewritten solely to update post-generation commit, push,
  CI, or review status;
- later commit/push/CI evidence belongs in a receipt, acceptance record, or
  volatile current-authority overlay;
- generation-time snapshots remain valid historical evidence.

## 11. Mixed-temporal and section-level semantics

Authority may be section-specific rather than file-wide.

For mixed documents:

- durable policy sections may remain supporting current authority;
- historical current-state sections must not answer live-state questions;
- future task contract sections must not be treated as proof that the task is
  still pending;
- when section authority is unavailable, a mixed-temporal source cannot be the
  sole basis for a current-state answer.

Policy-only metadata example:

```json
{
  "temporal_class": "mixed_temporal_evidence",
  "authority_level": "supporting_policy",
  "source_basis_commit": "<sha>",
  "observed_head_commit": "<sha>",
  "operational_freshness": "current|lagging|unknown",
  "section_authority": "stable_current|historical_snapshot|future_contract",
  "superseded_by": null
}
```

This is not a config file, schema, or runtime artifact.

## 12. Stable digest boundary

The stable digest should contain:

- durable policy;
- architecture decisions;
- stable operating contracts;
- approved historical evidence;
- metadata and hashes only.

The SHA-256 integrity guard remains mandatory for stable digest sources.
Digest inclusion is not approval to treat every source as current operational
state. Digest inclusion is not approval to implement retrieval, mutate files,
or broaden active task scope.

## 13. Volatile committed-HEAD overlay boundary

Recommended future volatile overlay rules:

- exact allow-list only;
- initial candidates: `STATUS.md` and `ACCEPTANCE_TRACE.md`;
- read-only;
- committed HEAD only;
- repo-relative paths only;
- no automatic discovery;
- no private/raw source;
- no dirty working-tree reads;
- citation must include `observed_head_commit` and a computed content hash.

The overlay is a future contract and implementation topic. This task does not
create it.

## 14. Historical and planning evidence rules

Historical and planning evidence may explain:

- why a capability was deferred;
- what risks were previously identified;
- what a release or clean-clone validation observed;
- how a previous logical review classified behavior.

Historical and planning evidence must not:

- grant current approval;
- override the current task contract;
- override `AGENTS.md`;
- answer current-state questions as the sole source;
- imply a completed task is still pending merely because a historical prompt or
  plan says it is next.

## 15. Conflict handling

If volatile state conflicts with stable policy, stable policy controls allowed
behavior and volatile state explains current status.

If volatile state conflicts with historical evidence, volatile state controls
current-state answers and historical evidence is labeled as context.

If two volatile sources disagree, return `partial` when some current evidence
is still useful, or `no_sufficient_evidence` when no safe current answer can be
formed.

If current state is absent but historical evidence exists, return
`no_sufficient_evidence` for current-state queries and optionally cite
historical context.

If a mixed document contains conflicting temporal sections, do not silently
rank one section away. Return `partial` unless section-level authority is
known.

If a digest source is hash-valid but operationally lagging, keep the citation
valid but label the current-state answer as lagging or insufficient.

If observed HEAD cannot be established, volatile authority is unavailable.
Return `partial` or `no_sufficient_evidence`; do not fall back to dirty
filesystem content.

## 16. Partial and no-answer behavior

Live state questions prefer volatile current authority. Durable rules prefer
stable policy. The explicit task contract and approval remain above retrieval.

Use `partial` when:

- current and historical evidence can be separated but the current answer is
  incomplete;
- volatile sources disagree but at least one current fact can be safely stated;
- mixed-temporal evidence has a likely current section but no section metadata.

Use `no_sufficient_evidence` when:

- current-state authority is absent;
- observed HEAD cannot be established for volatile authority;
- only historical evidence supports a current-state query;
- a conflict cannot be resolved without guessing;
- answering would require private/raw material or an unapproved side effect.

Use `blocked` when the query asks for forbidden material or asks retrieval to
perform an action.

## 17. Proposed metadata fields

Future retrieval evidence may use these metadata fields:

| field | meaning |
|---|---|
| `temporal_class` | Stable, volatile, mixed, historical, or generation-time class. |
| `authority_level` | Control or support level for the source. |
| `source_basis_commit` | Digest or source commit represented by a stable citation. |
| `observed_head_commit` | Committed HEAD used for volatile authority. |
| `operational_freshness` | `current`, `lagging`, or `unknown`. |
| `section_authority` | Section-level authority such as stable current, historical snapshot, or future contract. |
| `superseded_by` | Optional newer evidence pointer. |
| `conflict_notes` | Safe summary of unresolved authority conflicts. |

These fields are policy examples only. This task creates no JSON config,
schema, generated artifact, or runtime behavior.

## 18. Policy-application scenarios

| query | query class | required authority class | expected precedence | historical evidence allowed | expected status | conflict behavior | implementation metadata required | policy-only resolution possible | runtime change potentially required |
|---|---|---|---|---|---|---|---|---|---|
| `current implementation sequence` | `current_state` | volatile current authority plus roadmap policy | task contract, `AGENTS.md`, volatile overlay, roadmap | context only | `found` or `partial` | disclose if status and roadmap disagree | observed HEAD, source basis, temporal class | yes | overlay later |
| `next recommended task` | `current_state` | volatile current authority | task contract, `STATUS.md`/trace overlay, stable policy | context only | `found` or `partial` | stale next-step text must not control | observed HEAD, operational freshness | yes | overlay later |
| `current approved corpus digest status` | `mixed_context` | volatile state plus digest check evidence plus corpus policy | task contract, volatile overlay, digest check, stable/mixed policy | yes when labeled | `found` or `partial` | disclose generation-time versus live status | source basis, observed HEAD, generation snapshot label | yes | overlay/check integration later |
| `Phase 6G approved corpus digest refresh` | `mixed_context` | volatile state plus post-generation evidence | task contract, volatile overlay, mixed policy | yes when labeled | `found` or `partial` | separate completed refresh from future tool boundary | temporal class, section authority | yes | overlay later |
| `local verification commands` | `durable_policy` | stable current authority | `AGENTS.md`, `docs/VERIFICATION.md`, stable digest | yes after current policy | `found` | current verification policy controls | source basis | yes | no |
| `receipt redaction policy` | `durable_policy` | stable current authority | `docs/AUDIT_TRACE_SCHEMA.md`, JSON evidence policy if in scope | yes after current policy | `found` or `partial` | schema policy controls over historical review | source basis, section authority | yes | ranking may improve later |
| `CI` | `mixed_context` | current CI policy plus historical decision context | current CI policy before optional decision history | yes when labeled | `found` or `partial` | short-token collision must not make history control | temporal class, authority level | partially | token/ranking fix may be needed |
| `optional CI decision` | `historical_decision` | historical planning evidence | historical decision first, current roadmap as superseding context | yes | `found` | label as historical and not current approval | temporal class, superseded-by if known | yes | no |

Do not run a new full logical-verification matrix in this task. Phase 7C.3B
will apply this policy manually to the existing query matrix.

## 19. Selected architecture decision

Selected architecture: B. Stable digest plus committed-HEAD volatile overlay
plus separate post-generation evidence.

Rationale:

- Frequent digest refresh after every status or closeout change would make
  volatile documents dominate digest maintenance and would repeatedly create
  source-basis/artifact-containing commit churn.
- Receipt-only current-state evidence would avoid runtime complexity, but it
  would leave retrieval unable to answer ordinary current-state questions
  without manual context.
- A stable digest plus a narrow committed-HEAD overlay preserves hash integrity
  for durable policy while allowing current-state questions to cite live
  committed repository evidence.

This is an architecture decision only. It does not approve runtime
implementation.

## 20. Future implementation phases

Phase 7C.3B: Policy Application Review.

- Review-only.
- Apply this policy manually to the existing query matrix.
- Classify issues as policy-resolved, metadata-required, ranking-required,
  token-boundary-required, or corpus-rebaseline-required.

Phase 7C.3C: Volatile Authority Overlay Contract.

- Documentation and exact runtime contract.
- No implementation unless separately approved.

Phase 7C.3D: Minimal Volatile Overlay Implementation.

- Only after contract approval.
- Exact allow-list and committed-HEAD reads.
- Focused synthetic tests.

Phase 6H: Stable Corpus Re-baseline.

- Remove volatile documents from stable digest if approved.
- Add stable Local RAG policy documents only through exact allow-list approval.

Phase 7C.4: Minimal Retriever Logic Correction.

- Only if policy and overlay do not resolve lexical/ranking defects.

Phase 7D: Retrieval Receipt Evidence.

- Only after authority precedence and operational freshness behavior are
  proven.

## 21. Safety and approval boundaries

This policy does not grant approval for:

- runtime retrieval changes;
- digest refresh or re-baseline;
- volatile overlay implementation;
- corpus allow-list expansion;
- workflow edits or dispatch beyond Gate 0;
- CI or quality-gate integration;
- audit or receipt automation;
- release verification, tag, release, publication, or upload;
- downstream access;
- private/raw corpus ingestion.

Every future phase requires exact files, commands, side-effect class,
verification, and closeout requirements.

## 22. Acceptance criteria

This policy is acceptable when:

- Gate 0 Local Verify passes for exact commit `909b007...`;
- authority and temporal classes are separate and explicit;
- stable, volatile, mixed, historical, and generation-time evidence are
  defined;
- retrieval precedence is normative;
- current-state and durable-policy query behavior are distinguished;
- source-basis and observed-HEAD semantics are defined;
- dirty working-tree content is excluded from future volatile authority;
- generation-time closeout fields are not treated as live state;
- mixed documents require section-aware interpretation;
- conflict, partial, and no-answer behavior are defined;
- architecture decision B is selected;
- the next Phase 7C.3B matrix is testable from this document;
- no runtime, digest, allow-list, authority source, workflow, script, test, or
  artifact change occurs.

## 23. Exact next task

Exact next separately approved task:

Phase 7C.3B Policy Application Review.

That task is review-only and must not implement the overlay, patch the
retriever, change the digest, edit `STATUS.md` or `ACCEPTANCE_TRACE.md`, edit
workflows, or run release verification unless separately approved.

## 24. Commands run

Pre-action repository basis:

- `git status --short --branch`: `## main...origin/main`
- `git rev-parse HEAD`: `909b0071082b1bed7673749143ef2cb352e32cb6`
- `git rev-parse origin/main`: `909b0071082b1bed7673749143ef2cb352e32cb6`
- `git diff --name-status`: no output
- `git diff --cached --name-status`: no output
- `git ls-files --others --exclude-standard`: no output

Gate 0:

- Existing Local Verify run checked: run `27872762700`, job `82487216926`,
  conclusion `success`.
- No new workflow dispatch was performed because successful verification for
  the exact commit already existed.
- Artifact query for run `27872762700`: no uploaded artifacts.

Post-document verification commands are recorded in closeout when run.

Post-document verification:

- `python --version`: ENVIRONMENT BLOCKED by the local Windows logon-session
  issue.
- Bundled Python `scripts/generate_corpus_digest.py --check --json`: PASS,
  `source_count=32`, `valid=32`, `stale=0`, `refresh_required=false`.
- Bundled Python `python -m pytest tests/test_local_rag_retriever.py`: PASS,
  15 passed.
- Bundled Python `python -m pytest tests/test_generate_corpus_digest.py`: PASS,
  27 passed.
- Bundled Python `python -m pytest tests`: PASS, 140 passed.
- Bundled Python `python scripts/quality_gate.py`: PASS.
- `git diff --check`: PASS.
- `git diff --name-status`: no tracked diff.
- `git diff --name-only -- artifacts`: no output.
- `git diff --name-only -- STATUS.md ACCEPTANCE_TRACE.md`: no output.
- `git diff --name-only -- scripts tests .github/workflows`: no output.
- `git ls-files --others --exclude-standard`: exactly
  `docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`.
- `git status --short --branch`: `## main...origin/main` plus exactly
  `?? docs/LOCAL_RAG_VOLATILE_AUTHORITY_POLICY.md`.
