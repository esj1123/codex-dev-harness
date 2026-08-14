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
| Approved corpus and local retrieval | Advisory, frozen | Change source membership or retrieval behavior only through separate review. |
| Downstream contract validator | Implemented | Use only with target-specific authority and side-effect declarations. |
| Agent Quality/provider | Frozen, not adopted | Reopen only after a separate value decision; role calibration v7 is not run. |
| MCP boundary | Held | Reconsider only for a selected repository tool-integration use case. |
| Hermes sidecar | Held | Reconsider only after an MCP-backed use case is justified. |
| Release publication automation | Held | The selected transient evidence transport is not publication; publication still requires an explicit target and owner approval. |
| Durable audit automation | Held | Requires a demonstrated need and retention/redaction contract. |

## Current Selection

No new capability implementation is currently selected. Authority and release
evidence maintenance may use already implemented controls under their existing
approval gates, but it does not select a new capability. Follow `STATUS.md` for
current sequencing and the serial work-package schema v3 contract for scoped
repository changes.

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
- complete comparable trials before Agent Quality baseline adoption.

## Held Work

The following remain separate owner decisions:

- automatic CI triggers or required checks;
- baseline or release artifact creation outside the selected exact-SHA manual
  export and local-integration contract;
- tag, release, signing, durable upload, publish, or deploy;
- MCP or Hermes execution;
- automatic memory, RAG, audit, or failure promotion writes;
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
