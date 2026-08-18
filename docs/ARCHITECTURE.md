# Architecture

## Purpose

`codex-dev-harness` is a local-first control plane for governed AI-assisted
development. It provides reusable authority, planning, rendering, verification,
evidence, and handoff mechanisms. It is not a downstream application and does
not grant authority to perform side effects.

## Authority Plane

`docs/AUTHORITY_MANIFEST.json` is the machine-readable authority index. It
separates:

- current authority;
- durable policy;
- historical evidence;
- conditional read groups;
- integration-only paths; and
- bounded operational inputs consumed by specific tools; and
- the sole owner document for each protocol namespace.

`STATUS.md` is the current human sequencing summary. The capability roadmap is
consulted only when selecting work. Operational inputs are not current
authority and do not broaden task approval.

## Contract And Coordination Plane

Task contracts define goal, scope, no-touch areas, verification, and permitted
side effects. Work-package preflight and postflight add machine checks for:

- common base and contract basis;
- disjoint Windows-safe path ownership;
- frozen shared interfaces;
- dependency ordering;
- deterministic plan digests;
- actual Git change containment;
- verifier identity and command completion; and
- explicit separation of structural PASS from authorization.

Feature and contract lanes cannot modify integration-owned authority or
evidence surfaces. Contract changes return to the integration owner.

## Template And Render Plane

Base templates provide the common governance surface. Profiles add durable
workflow-specific guidance for:

- `python_cli`;
- `csharp_desktop`; and
- `plc_or_device_tool`.

The renderer supports `minimal`, `standard`, and `full` tiers, deterministic
file planning, generated Read Order closure, dry-run, provenance preview, and
diff preview. Repository-internal writes are restricted to controlled example
targets; real adoption uses a separately approved target.

Optional packs remain outside the base render path until explicitly integrated.

## Verification Plane

`docs/VERIFICATION.md` is the sole normative authority for verification tier
meaning. The execution layers are:

- focused tests for the changed contract or implementation;
- `LOCAL_INTEGRATION (V2)`: the official Core integration scope of core pytest,
  standalone eval, and the core quality gate;
- Full pytest as an impact-required extended regression for pytest
  infrastructure, dependency locks, common validators, and unclassified paths;
- other impact-required extras: checksum, corpus, render, or focused checks;
- the manual exact-SHA canonical Hosted verifier for approved
  `HOSTED_EXACT_SHA (V3)` evidence; and
- the separate release-evidence export workflow, which is artifact transport
  and generation evidence rather than Hosted verification.

`docs/VERIFICATION_IMPACT_MAP.json` is an operational input for advisory
planning. It selects commands but does not execute them or authenticate
approval.

## Agent Quality Plane

Agent Quality Stability supplements deterministic repository checks with
repeated agentic trials. It binds:

- canonical suite and task definitions;
- source and contract bases;
- work-package and tool policy hashes;
- model and environment fingerprint fields;
- exact verifier contracts;
- grader-bound invariant results;
- owner-held holdout summaries; and
- semantic review outcomes.

Raw prompts, transcripts, model output, private inputs, and holdout fixtures are
not tracked. Baseline creation is approval-gated and remains unavailable until
all comparability and quality thresholds pass.

## Evidence And Retrieval Plane

The repository keeps JSON evidence schemas, release evidence, an exact approved
corpus source set, a checkout-independent corpus digest, and a local read-only
retriever. Evidence is identifier-first and bounded. Retrieval is advisory and
cannot expand approval.

Release checksums and the approved corpus digest are separate integrity
surfaces. Regeneration requires an explicit write approval and a declared
source basis.

## Side-Effect Boundary

The default is read-only and dry-run first. File mutation, dependency
installation, network access, downstream access, staging, commit, push,
workflow dispatch, artifact upload, release, deploy, and live action are
independent side-effect classes.

No policy document, package, validator result, or historical approval grants
standing authority for those actions.

## Downstream Boundary

Downstream repositories have their own authority. Harness-facing contracts use
safe aliases and bounded summaries, not private raw data or persisted absolute
paths. In-place overwrite is not allowed without explicit target-specific
approval and collision review.

The completed greenfield pilot demonstrates the control model; it does not make
application code part of this repository.
