# Render Tier Contract

## Purpose

Define the future minimal / standard / full render tier policy before any
render behavior changes.

## Current Scope

This contract is documentation and focused-test only. It does not authorize
changes to `scripts/render_template.py`, generated examples, templates,
profiles, quality gates, workflows, artifacts, release behavior, or downstream repositories.

## Tier Model

| tier | intent | included surface |
| --- | --- | --- |
| `minimal` | Small one-off tools where adoption cost must stay low. | Root orientation and safety-critical docs only: `AGENTS.md`, `README.md`, `PRODUCT.md`, `MVP.md`, `PROJECT_BOUNDARY.md`, plus selected profile safety and verification overlays when a profile is selected. |
| `standard` | Default for active project work needing handoff and verification. | `minimal` plus `STATUS.md`, `PHASE_PLAN.md`, `DATA_SCOPE.md`, `APPROVALS.md`, `VERIFICATION.profile.md`, and `SAFETY_POLICY.profile.md` when a profile is selected. |
| `full` | Current-compatible complete documentation skeleton. | All currently rendered base templates and all selected profile templates. |

## Default Compatibility

Until implementation is separately approved, the renderer keeps current
behavior. Future implementation must treat an omitted tier as `full` or as an
explicitly documented current-compatible default.

## Config Shape

Future config key: `render.tier`.

Allowed values:
- `minimal`
- `standard`
- `full`

Unknown values must fail closed before rendering or writing files. CLI override,
if added, should be explicit, for example `--tier`.

## Preview Integration

When implemented, tier selection must apply consistently to normal render,
`--dry-run`, `--provenance-preview`, and `--diff-preview`.

## Safety Rules

- no automatic target overwrite
- no downstream access in tests
- no raw target content in preview output
- target-relative paths only in diff preview summaries
- no local absolute paths in generated tier metadata or preview JSON
- no change to examples unless explicitly approved
- no quality gate, workflow, artifact, release, tag, or publication side effects
  by this contract alone

## Future Implementation Gate

A separate implementation task must name exact allowed files, selected default
behavior, included paths for each tier, test fixtures, verification commands,
and closeout evidence.