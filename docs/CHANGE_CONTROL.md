# Change Control

## Purpose

Define how codex-dev-harness changes are proposed, reviewed, applied, verified, and recorded after the `v0.1.0` local-first baseline.

This policy is documentation-only. It does not create automation, workflows, release artifacts, eval code, application code, device code, or live-write behavior.

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
- adding runtime/application code
- adding C# source, project, solution, XAML, or build assets
- adding PLC/device code or live target write behavior

## Verification

Use local verification when implementation or validation surfaces change:

- `powershell -ExecutionPolicy Bypass -File scripts/run_local_verify.ps1`

Documentation-only changes may use review-based verification when no executable behavior changes. If executable verification is not run, record `NOT RUN` with the reason.

## Evidence Locations

Use existing evidence surfaces first:

- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- release records under `docs/`
- closeout or decision records under `docs/`

A dedicated audit log schema is deferred unless explicitly approved.

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
