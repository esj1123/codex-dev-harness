# Change Control

## Purpose

Define how codex-dev-harness changes are proposed, reviewed, applied, verified, and recorded after the `v0.1.0` local-first baseline.

This policy is enforced by the read-only
`scripts/work_package_conflict_check.py` preflight checker and
`scripts/work_package_postflight.py` completed-lane checker. Neither checker
grants approval, executes declared commands, creates worktrees, or modifies
files.

## Scope

This policy applies to durable repository changes, including:

- root contract documents
- policy and evidence documents under `docs/`
- templates and optional packs
- reusable prompt contract templates
- profile folders
- examples
- tests and quality gates
- release records and release-support material

Downstream project content remains downstream-only unless a separate approved task promotes generic, domain-neutral feedback into this repository.

## Change Classes

| class | examples | default path |
|---|---|---|
| documentation-only | policy docs, review records, checklists | safe when requested and scoped |
| prompt contract template | reusable prompt Markdown under `prompts/task_contract/` | safe when requested, scoped, and non-executing |
| template surface | base templates, optional templates | approval-gated when adding durable surface |
| validation surface | tests, gates, verification wrappers | separate implementation task |
| audit evidence schema | `audits/audit-log.schema.json`, audit policy fields | safe when explicitly approved, scoped, and non-logging |
| profile or example | new profile, new regression example | owner approval required |
| release surface | tags, GitHub Releases, manifests, checksums | separate release approval required |
| side-effecting behavior | workflows, external mutations, live/device actions | not allowed by default |

## Required Change Record

Before changing files, identify:

- goal
- basis ref or commit when relevant
- allowed files
- no-touch files and actions
- expected verification
- approval requirements
- completion report format

After changing files, record:

- files changed
- commands or systems touched
- verification result, including NOT RUN reasons
- safety checks
- unresolved risks and assumptions
- recommended next step

## Parallel Work Packages

Parallel repository work must use one JSON package per task under the ignored
`local/work-packages/` directory. The tracked
`docs/PARALLEL_WORK_PACKAGE_SYNTHETIC_FIXTURE.json` file is a format example,
not an approval or an executable task.

Each package must declare:

- `schema_version`
- `task_id`
- `base_sha`
- `contract_basis_sha`
- `contract_frozen_paths`
- `lane`: `contract`, `feature`, or `integration`
- `depends_on`
- exact repo-relative `read_set` and `write_set`
- `generated_outputs`
- `verification_tier`
- `verification_contract`, containing one safe `interpreter_id` and one or
  more command records with a unique `command_id` and exact argument list
- `declared_side_effects`
- an optional safe `approval_ref`

Work-package schema version `3` requires `contract_basis_sha` to equal
`base_sha`. It is independent of the `HOSTED_EXACT_SHA (V3)` verification tier;
`docs/AUTHORITY_MANIFEST.json` routes those namespaces to this document and
`docs/VERIFICATION.md` respectively. Feature
packages must declare a non-empty shared `contract_frozen_paths` list and include
that surface in `read_set`. Verification commands use argument arrays rather
than shell strings. `{PYTHON}` denotes the separately selected runtime whose
identity is recorded by `interpreter_id`; the package must not persist an
absolute interpreter path.

Package declarations do not authenticate approval. They describe the intended
scope so the checker can detect overlap before independent tasks begin. A
successful result therefore includes `authorization_status` set to
`NOT_AUTHENTICATED`; it is a structural plan result, not permission to execute
commands or side effects.

Every package declares `repository_access`. A non-empty verification command
set also declares `execute`; tracked or generated writes declare `local_write`;
and a contract or feature lane with a write set declares both `stage` and
`commit`. The checker rejects an incomplete side-effect declaration instead of
inferring permission from the lane or write set.

Packages may run in parallel only when they share one base SHA, have disjoint
write sets, and do not write another package's read set. A declared dependency
requires serialization. Duplicate task IDs, dependency cycles, missing
dependencies, unsafe paths, and undeclared read/write overlap are blockers.

Path ownership is Windows-safe and case-insensitive. Case variants such as
`docs/Policy.md` and `docs/policy.md` conflict. A declared directory owner and
any parent/child path below it also conflict, including write/write ownership
and write/read dependencies. Path components ending in a dot or space are
invalid.

The preflight result includes `plan_digest`, calculated as SHA-256 over the
package objects sorted by `task_id` and serialized as deterministic compact
JSON. Every lane in one batch must use the same package set and therefore the
same `plan_digest`. The digest binds the exact verification command arrays and
runtime identity. `approval_ref` remains part of the execution instance and
does not authenticate authorization.

After focused verification and one coherent lane commit, run the postflight
checker for that task. Postflight observes Git without writing and verifies:

- the package base is an ancestor of the current HEAD;
- feature and contract lanes contain exactly one commit;
- actual changed paths stay within `write_set`;
- actual non-ignored untracked paths stay within `generated_outputs`;
- tracked worktree state is clean;
- rename and delete operations are absent;
- `git diff --check` passes; and
- feature and contract lanes did not change integration-only paths; and
- actual tracked or generated changes do not overlap `contract_frozen_paths`;
- the observed verification runtime matches `interpreter_id`; and
- a `PASS` declares every required verification `command_id` complete.

Postflight accepts bounded command IDs, not raw logs. It validates the
interpreter identity and completed-command ID set before loading packages or
observing Git. Invalid, duplicate, or excessive verifier input fails closed and
is not reflected in output. It does not execute the commands or infer success
from an owner rerun. The caller must report a missing agent command as
incomplete even when an integration owner later verifies the same code
successfully.

Postflight emits deterministic bounded JSON to stdout. If a result cannot be
serialized safely within the output limit, it emits a minimal fail-closed
envelope instead. A caller may store output under ignored
`local/checkpoints/<checkpoint-id>/` only when local evidence writing is
approved. No result envelope is tracked.

## Contract Freeze And Reopen

`contract_frozen_paths` identify the shared interface basis for one package
batch. All packages in the batch use the same canonical frozen set and the same
contract/base SHA. A feature lane cannot write a frozen path directly or through
parent/child ownership. Preflight or postflight reports
`CONTRACT_CHANGE_REQUIRED` when the declared or actual change crosses that
boundary.

`CONTRACT_CHANGE_REQUIRED` is not a defect override. Stop the affected lanes,
return to the integration owner, revise the shared contract in a separate
approved contract task, run verification for that contract commit, and create a
new package batch from the new base SHA. Do not mutate the active batch package
or reuse its `plan_digest`.

## Lane Ownership

Contract and feature lanes must not write integration-only surfaces:

- `AGENTS.md`
- `README.md`
- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `docs/AUTHORITY_MANIFEST.json`
- `docs/AI_HANDOFF.md`
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- `artifacts/`
- `.github/workflows/`
- `scripts/agent_quality.py` and `scripts/agent_quality_lib/`
- `scripts/quality_gate.py` and `scripts/gates/`
- `evals/agentic/`
- `evals/golden/`
- `docs/APPROVED_CORPUS_SOURCE_SET.v2.json`
- `docs/VERIFICATION_IMPACT_MAP.json`

The integration lane alone may merge feature work, update current authority,
refresh approved artifacts after separate approval, run full verification,
push a cumulative tip, or dispatch the existing Local Verify workflow.

The selected `manual_github_release_evidence_export` capability is a bounded
integration-only exception to the previous no-upload CI policy. It does not
exist until its workflow implementation commit passes its own work-package schema v3
postflight. When implemented, its exact branch push, manual dispatch, one
transient artifact upload/download, and local artifact integration remain
separate declared side effects. It does not authorize automatic triggers,
required checks, tags, releases, signing, publication, deployment,
`origin/main` mutation, or downstream access.

## Commit And Checkpoint Policy

One approved local task may include edits within its exact write set, focused
verification, staging, and one coherent local commit. Separate micro-commits
are not required for a contract, an implementation, or a no-change usage probe
unless their approval or side-effect boundaries differ.

Current authority, acceptance checkpoints, generated digest freshness, push,
and remote Local Verify are integration-checkpoint work. A no-change usage
probe stays in task closeout evidence unless it changes a durable decision,
reveals a defect, or is explicitly approved as a tracked record.

The integration lane should normally produce:

1. one or more feature commits;
2. one cumulative integration commit;
3. one digest-only commit only when approved source content is stale;
4. one push and one Local Verify run for the final cumulative tip.

## Approval Gates

Separate explicit owner approval is required before:

- adding or changing profiles
- adding examples
- integrating optional packs into render, gates, or examples
- converting prompt contract templates into automation
- installing `.github/workflows`
- publishing GitHub Releases
- creating, moving, or signing tags
- generating release manifests, checksums, SBOMs, or provenance artifacts
- implementing an eval harness
- generating real audit logs or adding audit logging automation
- adding runtime/application code
- adding C# source, project, solution, XAML, or build assets
- adding PLC/device code or live target write behavior

## Verification

Use the verification tier declared by the work package. The cumulative
integration checkpoint must run the broader local verification defined in
`docs/CI_POLICY.md`.

Feature lanes run focused checks only. They do not refresh the corpus digest,
push, dispatch workflows, or record remote verification evidence.

A lane is not ready for integration until preflight and postflight report the
same `plan_digest`, the declared verification status is `PASS`, and postflight
reports `PASS` for the exact `interpreter_id` and complete command-ID set.
Those PASS values establish consistency only. The separate
`authorization_status=NOT_AUTHENTICATED` result means owner approval and every
side-effect permission still require external evidence.

Documentation-only changes may use review-based verification when no executable behavior changes. If executable verification is not run, record `NOT RUN` with the reason.

## Evidence Locations

Use existing evidence surfaces first:

- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- release records under `docs/`
- closeout or decision records under `docs/`

The dedicated audit log schema exists at `audits/audit-log.schema.json` as an
optional future evidence contract. It does not authorize real audit log
generation, prompt capture, tool-call body capture, private input capture, or
automation. Any actual audit log entry generation requires separate explicit
approval.

## Non-Goals

This policy does not authorize:

- real application code
- C# source, solution, project, XAML, or build assets
- PLC/device code
- live target write support
- workflow installation
- release publication
- manifest, checksum, SBOM, or provenance artifact generation
- eval harness implementation
- audit logging automation or real audit session log generation
