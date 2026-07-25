# Change Control

## Purpose

Define how codex-dev-harness changes are proposed, reviewed, applied, verified, and recorded after the `v0.1.0` local-first baseline.

This policy is enforced for parallel work-package shape and overlap by the
read-only `scripts/work_package_conflict_check.py` checker. The checker does not
grant approval, execute declared commands, create worktrees, or modify files.

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
- `lane`: `contract`, `feature`, or `integration`
- `depends_on`
- exact repo-relative `read_set` and `write_set`
- `generated_outputs`
- `verification_tier`
- `declared_side_effects`
- an optional safe `approval_ref`

Package declarations do not authenticate approval. They describe the intended
scope so the checker can detect overlap before independent tasks begin.

Packages may run in parallel only when they share one base SHA, have disjoint
write sets, and do not write another package's read set. A declared dependency
requires serialization. Duplicate task IDs, dependency cycles, missing
dependencies, unsafe paths, and undeclared read/write overlap are blockers.

## Lane Ownership

Contract and feature lanes must not write integration-only surfaces:

- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `docs/AI_HANDOFF.md`
- `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`
- `artifacts/`
- `.github/workflows/`
- `scripts/quality_gate.py` and `scripts/gates/`
- `evals/golden/`
- `docs/APPROVED_CORPUS_SOURCE_SET.v2.json`

The integration lane alone may merge feature work, update current authority,
refresh approved artifacts after separate approval, run full verification,
push a cumulative tip, or dispatch the existing Local Verify workflow.

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
