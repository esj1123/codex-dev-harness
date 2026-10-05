# Capability Implementation Roadmap

## Purpose

Select the next bounded capability without duplicating current state, phase
history, or task closeout evidence.

- Current machine state: `docs/AUTHORITY_MANIFEST.json`
- Current human sequencing: `STATUS.md`
- Durable boundaries: the policy documents classified by the manifest
- Historical implementation detail: Git history and historical evidence

This roadmap does not authorize implementation or side effects.

## Selection Principles

1. Fix a demonstrated control gap before adding convenience automation.
2. Prefer read-only, local, standard-library, and deterministic surfaces.
3. Define schema and safety boundaries before persistence or execution.
4. Freeze shared contracts before parallel lanes.
5. Keep feature lanes disjoint and central authority integration-owned.
6. Require exact approval for artifact writes, remote actions, publication,
   downstream mutation, and live behavior.
7. Do not add a capability when an existing focused tool already covers the
   need.

## Capability Registry

| Capability | State | Next decision trigger |
|---|---|---|
| Engineering authoring, diagram and review skills | Three optional role sources with conditional references; see current STATUS closeout for verification, installation and loading | Select document family, perspective, stage and format as needed; real target utility remains unmeasured. |
| Education/knowledge and legacy analysis skills | Design only in `docs/PROMPT_PATTERNS.md` | Implement only for an owner-selected bounded target need. |
| Authority manifest and docs gate | Implemented | Change only when authority classes or required documents change. |
| Work-package preflight/postflight | Hardened; external control-plane package root validated | Use same-root by default or an explicitly declared physical-safe local package root; extend only for another reproduced coordination escape. |
| Verification impact planner | Implemented, advisory | Extend when a real changed path cannot be classified safely. |
| Tiered template rendering | Ready; explicit apply | Preview is the default; use `--apply` only after reviewing the complete plan. |
| Read-only Local Verify | Implemented | Keep manual and exact-SHA unless owner selects a different CI policy. |
| JSON evidence core | Ready | Core schema validation is in the default gate; optional bundles stay standalone. |
| Release evidence generators | Hardened | Re-run only after a new source basis and exact artifact-write approval are established. |
| Tracked release bundle | See `STATUS.md` | Keep source basis, artifact commit, local Git availability, transient transport, and publication state distinct. |
| Manual GitHub release-evidence export | Implemented; approval-gated | Preserve default `HOSTED_EXACT_SHA (V3)` verification, use one explicit exact-SHA export mode, one-day transient transport, and local evidence integration only. Read `STATUS.md` for the current run state. |
| Read-only verification environment diagnostic | Implemented; exact-SHA locally verified; locally adopted | Preserve safe `EnvironmentOnly / Json` observations without installation, persistence, suite execution, or target behavior. Hosted evidence remains separate. |
| Dirty-worktree package checkpoint | Deferred; implementation not selected | Require at least one demonstrated prevented error from a real target before implementing a read-only `NOT_FINAL` readiness result; never substitute for postflight. |
| Launchpad transfer and Junction attestation | Local authority rebaseline adopted | Launchpad local `main@1f9677a13044770bfb3be89ab910127674851d49`; structural V2 remains `NOT_AUTHENTICATED`. Office, transfer, Junction mutation, remote, and release are not authorized. |
| Downstream mechanization pilots | Stock and RSID local pilots complete | Stock evidence closeout is `bd434a200f4054f9b41eeea085183ff0df25c70b`; RSID evidence-scope pilot is `c0ffc1d5ddd40bb050d10c0f6e42f93b7d16858c`. Preserve repo-specific authority and unresolved RSID GAP-013. |
| Approved corpus and local retrieval | Advisory, frozen | Change source membership or retrieval behavior only through separate review. |
| Downstream contract validator | Implemented | Use only with target-specific authority and side-effect declarations. |
| Agent Quality/provider | Structural V2 passed; frozen, not adopted | AQ-R5K passed package-bound structural verification. The value decision is `REDESIGN_BEFORE_TRIAL`; demonstrated prevention, provider execution, calibration, baseline, promotion, and adoption remain unproven or not run. |
| MCP boundary | Held | Reconsider only for a selected repository tool-integration use case. |
| Hermes sidecar | Held | Reconsider only after an MCP-backed use case is justified. |
| Release publication automation | Held | The selected transient evidence transport is not publication; publication still requires an explicit target and owner approval. |
| Durable audit automation | Held | Requires a demonstrated need and retention/redaction contract. |

## Current Selection

No additional implementation capability is selected for executable infrastructure. Three optional documentation-only engineering skills and personal Codex/Claude copies are selected; `STATUS.md` owns their current closeout. The read-only verification environment diagnostic remains part of the locally adopted M01/M02 lineage,
and post-M02 reconciliation started from
`acd39a3c3e73fa05e752964a75059809e6e16f71`. Authority commit
`3d54823c557317d54811b9731b3198a41a647e0f`, assertion correction
`ac0efb08261a7c84828acff476d217ce9286b633`, and the separately verified and
locally adopted digest `80d1ac15d6c036f7d914bfe606664a7daac2378f`
close that local sequence. Physical cleanup and the Stock, RSID, and Launchpad
local checkpoints are complete. AQ-R5K supplies structural V2 evidence for
proposal
`53de64a1a19ec5d50849ebda54bbec619e4097a1`, while the proposal remains
`FROZEN / NOT_ADOPTED`; all earlier AQ HOLD/FAIL evidence remains historical.
The later boundary-fix sequence is also complete: owner-approved local adoption was
observed at `81fbc855c9db1db364ca22ef71ebc6211380b416`, followed by the separately approved
normal push and `HOSTED_EXACT_SHA (V3)` PASS at `bac6a13ef77e20554f67b38398fa65499828fba0`.
That approval is consumed; earlier remote/Hosted `NOT RUN / DEFERRED` records remain
historical, and any successor remote/Hosted action requires fresh authority. Git GC remains deferred.

The authoritative order is:

1. preserve M00 at `845e56d81d006de07d405cbf1fe6711afd444e04` as
   the historical M01 task-start basis;
2. record the completed owner adoption of the M01 sequence at
   `05027f899bb726e8a1717c35b1f10a712f1825e9` without making a self-updating
   assertion about a future local ref;
3. preserve completed M02 authority/digest evidence and local adoption at
   `2de218f0548c349c74151c0fcf8a79186f951d4c` without rewriting the original
   package BLOCKED result or later recovery PASS;
4. preserve the completed post-M02 reconciliation at
   `3d54823c557317d54811b9731b3198a41a647e0f`, assertion correction at
   `ac0efb08261a7c84828acff476d217ce9286b633`, and separate digest/local adoption
   at `80d1ac15d6c036f7d914bfe606664a7daac2378f`;
5. preserve earlier remote/Hosted `NOT RUN / DEFERRED` as historical, record the later
   approved push and Hosted exact-SHA V3 at `bac6a13ef77e20554f67b38398fa65499828fba0`, and keep successors on fresh-authority HOLD;
6. keep the dirty-worktree checkpoint deferred until a real target demonstrates
   at least one prevented error;
7. preserve the completed ignored-evidence archive, exact source deletion,
   detached-worktree removal, and merged-branch deletion receipts while keeping
   Git packing and GC held;
8. retain tracked Agent Quality contracts and proposal branch in
   `FROZEN / NOT_ADOPTED` state; AQ-R5K is structural V2 evidence, not trial,
   baseline, promotion, or adoption;
9. preserve Stock local closeout `bd434a200f4054f9b41eeea085183ff0df25c70b`
   without broker, order, account, network, credential, or live-vault behavior;
10. preserve the completed static-only RSID pilot
    `c0ffc1d5ddd40bb050d10c0f6e42f93b7d16858c` and Launchpad local adoption
    `1f9677a13044770bfb3be89ab910127674851d49`; and
11. add another Harness package only for a P0 safety/authority defect, an actual
    target blocker, the same gap in two targets, or a demonstrated verifier
    false PASS/FAIL.

Each item has its own work package, commit, verification, and approval boundary.
Harness cleanup and the target sequence completed under separately owned
checkpoints; none inherited authority from structural package PASS. Launchpad
remains the reference pilot and its authority rebaseline is adopted locally,
while Office/template/runtime acceptance remains separate.
Loxfs remains evidence-only by default.
The completed target order was Stock first and RSID second; any new target work
requires a new target-owned scope.

For Agent Quality work:

- historical unbound runs remain review evidence only;
- current runs must match the tracked suite, verifier contract, and
  grader-bound invariant evidence;
- baseline creation remains blocked until comparability is full and every
  adoption threshold passes;
- a diagnostic or repeated trial requires its own execution approval;
- keep tracked policy, schemas, validators, suites, and tests; archive the
  ignored `runtime-bootstrap-v1-20260728T040223Z` and
  `role-profile-calibration-v6-20260729T115311Z` groups outside the active repo
  only after exact inventory, safety, archive-entry, and SHA-256 verification.

For downstream work:

- select a safe repository alias and target authority;
- declare access class, exact read/write scope, no-touch paths, verification,
  cleanup, and each side-effect permission;
- do not persist an absolute target path in harness authority documents;
- do not treat a synthetic contract PASS as target authorization.

## Dependency Rules

The durable ordering constraints are:

- authority and source-of-truth before automation;
- evidence schema before evidence persistence;
- approved source set and digest before retrieval;
- MCP boundary before tool runtime or sidecar behavior;
- stable source basis before release evidence refresh;
- publication target before release automation;
- target contract and frozen interfaces before downstream feature lanes;
- authority alignment before mechanization, Harness core before target
  adapters, and target adapters before additional repo pilots;
- complete comparable trials before Agent Quality baseline adoption.

## Held Work

The following remain separate owner decisions:

- automatic CI triggers or required checks;
- baseline or release artifact creation outside the selected exact-SHA manual
  export and local-integration contract;
- tag, release, signing, durable upload, publish, or deploy;
- MCP or Hermes execution;
- automatic memory, RAG, audit, or failure promotion writes;
- a generic verification command runner, inferred package fields, automatic
  worktree prune, local-ref mutation, Junction repair, manifest rewrite,
  dependency installation, or repository-wide EOL normalization;
- downstream repository access or mutation outside the selected Stock-then-RSID
  target-owned checkpoints;
- private, customer, production, or live-system data;
- application capability expansion not justified by measured usage.

## Capability Proposal Contract

Before selecting a capability, record:

- observed problem and evidence;
- nearest existing tool or policy;
- exact scope and no-touch surfaces;
- public interface or schema effect;
- side-effect classes and approval requirements;
- focused and cumulative verification;
- rollback and cleanup;
- completion and stop conditions.

If the proposal changes public contracts, create a serial work-package schema v3
contract-freeze step before parallel implementation. If the proposal only addresses local behavior,
prefer one focused implementation commit and one cumulative verification gate.

## Closeout

Every capability task reports:

- outcome and decision state;
- exact files and systems touched;
- commands executed and truthful results;
- checks intentionally `NOT RUN`;
- artifact, commit, push, workflow, and publication state;
- safety exclusions;
- unresolved risks;
- the next owner decision.

Run IDs and volatile measurements stay in task closeout unless a durable policy
specifically requires tracked evidence.
