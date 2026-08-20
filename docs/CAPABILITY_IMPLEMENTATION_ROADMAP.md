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
| Authority manifest and docs gate | Implemented | Change only when authority classes or required documents change. |
| Work-package preflight/postflight | Hardened; external control-plane package root validated | Use same-root by default or an explicitly declared physical-safe local package root; extend only for another reproduced coordination escape. |
| Verification impact planner | Implemented, advisory | Extend when a real changed path cannot be classified safely. |
| Tiered template rendering | Ready; explicit apply | Preview is the default; use `--apply` only after reviewing the complete plan. |
| Read-only Local Verify | Implemented | Keep manual and exact-SHA unless owner selects a different CI policy. |
| JSON evidence core | Ready | Core schema validation is in the default gate; optional bundles stay standalone. |
| Release evidence generators | Hardened | Re-run only after a new source basis and exact artifact-write approval are established. |
| Tracked release bundle | See `STATUS.md` | Keep source basis, artifact commit, local Git availability, transient transport, and publication state distinct. |
| Manual GitHub release-evidence export | Implemented; approval-gated | Preserve default `HOSTED_EXACT_SHA (V3)` verification, use one explicit exact-SHA export mode, one-day transient transport, and local evidence integration only. Read `STATUS.md` for the current run state. |
| Read-only verification environment diagnostic | Selected; implementation pending | Add safe `EnvironmentOnly / Json` observations to the existing Local Verify boundary without installation, persistence, or suite execution. |
| Dirty-worktree package checkpoint | Queued after environment diagnostic | Reuse schema-v3 loading and path boundaries to report `NOT_FINAL` scope readiness; never substitute for postflight. |
| Launchpad transfer and Junction attestation | Queued; target-owned | Add separate read-only target adapters only after the Harness core items are exercised; never create, repair, retarget, or remove a Junction or rewrite a manifest. |
| Downstream mechanization pilots | Ordered evidence collection | Use Launchpad as the reference, stock first, and RSID second; preserve repo-specific adapters and static-only evidence boundaries. |
| Approved corpus and local retrieval | Advisory, frozen | Change source membership or retrieval behavior only through separate review. |
| Downstream contract validator | Implemented | Use only with target-specific authority and side-effect declarations. |
| Agent Quality/provider | Frozen, not adopted | Reopen only after a separate value decision; role calibration v7 is not run. |
| MCP boundary | Held | Reconsider only for a selected repository tool-integration use case. |
| Hermes sidecar | Held | Reconsider only after an MCP-backed use case is justified. |
| Release publication automation | Held | The selected transient evidence transport is not publication; publication still requires an explicit target and owner approval. |
| Durable audit automation | Held | Requires a demonstrated need and retention/redaction contract. |

## Current Selection

The selected capability is the Harness read-only verification environment
diagnostic. It follows the serial work-package schema v3 contract and is
implemented alone in the next package. Its selection does not authorize the
dirty-worktree checkpoint, Launchpad adapter
changes, downstream execution, durable evidence persistence, runtime repair,
or remote actions.

The authoritative order is:

1. close the current authority and priority alignment;
2. implement and exercise the Harness environment diagnostic;
3. decide the Harness dirty-worktree checkpoint from observed use;
4. implement Launchpad transfer verification and Junction attestation as
   separate target-owned read-only packages;
5. apply the established intake and evidence boundary to stock;
6. apply the Git-object static-only adapter to RSID Inspection; and
7. select evidence lint, stale-worktree audit, or local-ref planning only when
   the pilots demonstrate repeatable benefit.

Each item has its own work package, commit, verification, and approval boundary.
Later items are queued, not pre-authorized. Launchpad remains the reference
pilot; its artifact runtime is still dependency-held. Stock is a local/read-only
pilot until dependency and Hosted contracts are pinned. RSID remains static
Git-object evidence only and must not execute tracked binaries.

For Agent Quality work:

- historical unbound runs remain review evidence only;
- current runs must match the tracked suite, verifier contract, and
  grader-bound invariant evidence;
- baseline creation remains blocked until comparability is full and every
  adoption threshold passes;
- a diagnostic or repeated trial requires its own execution approval.

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
- new downstream repository access or mutation;
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

If the proposal changes public contracts, create a serial contract-freeze step
before parallel implementation. If the proposal only addresses local behavior,
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
