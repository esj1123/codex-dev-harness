# Render Tier Contract

## Purpose

Define and enforce the minimal / standard / full render tier policy for
local template rendering. The contract is based on representative local project
shapes and a narrow review of established template-tool behavior.

## Decision Status

`render_tier_selection_implemented`

## Current Scope

The local renderer implements this contract for `minimal`, `standard`, and
`full` selection, including config/CLI precedence, exact file planning,
tier-specific Read Order generation, and focused readiness checks.

Implementation does not authorize curated example regeneration, workflow or release changes,
artifact generation, downstream repository access, hooks,
post-actions, network fetches, package installation, or external template
execution.

## Scenario Basis

The contract was checked against four read-only, anonymized local archetypes.
No repository identifier, absolute path, raw project content, or private value
is part of this contract.

| archetype | observed need | tier implication |
| --- | --- | --- |
| `minimal_meta_tool` | Low adoption cost and a short orientation path are more important than lifecycle records. | Start at `minimal`; add a profile only when its safety and verification overlays match the runtime. |
| `document_workflow` | Repeatable scripts, tests, and handoff state need explicit scope, verification, and acceptance records. | Start at `standard`; use `full` when source inventory is material. |
| `verified_protocol_tool` | Strong source/artifact boundaries and repeatable readiness checks justify the complete governance surface. | Prefer `full`. |
| `legacy_industrial_review` | Safety evidence may live in project-specific files and may not match scanner filename conventions. | Choose from actual dimensions and reference closure, not the aggregate scanner score alone. |

The readiness scanner remains advisory for real repositories. A filename-based
dimension may under-credit an equivalent project-specific boundary. Tier
evaluation must therefore retain dimension evidence and must treat broken Read
Order references as a hard failure regardless of the aggregate score.

## Tier Output Contract

The profile column lists files added only when a profile is selected. The
profiled total is the base count plus that column.

| tier | exact base outputs | exact selected-profile outputs | count |
| --- | --- | --- | --- |
| `minimal` | `AGENTS.md`, `README.md`, `PRODUCT.md`, `MVP.md`, `PROJECT_BOUNDARY.md` | `AGENTS.override.md`, `SAFETY_POLICY.profile.md`, `VERIFICATION.profile.md` | 5 base / 8 profiled |
| `standard` | `AGENTS.md`, `README.md`, `PRODUCT.md`, `MVP.md`, `PROJECT_BOUNDARY.md`, `DATA_SCOPE.md`, `APPROVALS.md`, `PHASE_PLAN.md`, `STATUS.md`, `ACCEPTANCE_TRACE.md` | `AGENTS.override.md`, `STATUS.profile.md`, `SAFETY_POLICY.profile.md`, `VERIFICATION.profile.md` | 10 base / 14 profiled |
| `full` | `AGENTS.md`, `README.md`, `PRODUCT.md`, `MVP.md`, `PROJECT_BOUNDARY.md`, `DATA_SCOPE.md`, `APPROVALS.md`, `PHASE_PLAN.md`, `STATUS.md`, `ACCEPTANCE_TRACE.md`, `SOURCE_INDEX.md` | `AGENTS.override.md`, `README.profile.md`, `STATUS.profile.md`, `SAFETY_POLICY.profile.md`, `VERIFICATION.profile.md` | 11 base / 16 profiled |

`full` is the current-compatible tier: it contains all currently rendered base
templates and all selected profile templates.

## Default And Selection Contract

The config shape is:

```yaml
render:
  tier: minimal
```

Allowed values are `minimal`, `standard`, and `full`. An omitted tier must be
treated as `full`. If the `--tier` CLI option is supplied, the CLI value
must override `render.tier`; otherwise the config value applies.

Unknown values fail closed before output planning, preview generation, or
file writing. The same resolved tier must apply to normal render, `--dry-run`,
`--provenance-preview`, and `--diff-preview` so every mode reports the same
planned file set.

The committed config example declares `full`, while configs that omit
`render.tier` remain full-compatible. Provenance and diff preview schemas remain
at v0 without a new tier key; dry-run render lines, rendered file counts, and
target-relative diff paths expose the selected plan. The golden Python CLI
fixture explicitly uses `full` under fixture schema version `1`.

## Read Order And Reference Closure

The renderer generates tier-specific Read Order content; filtering
the output files while retaining the current full-tier references is invalid.
Every Read Order in rendered `AGENTS.md`, `README.md`, and
`AGENTS.override.md` must list only files emitted for the resolved tier and
profile selection.

The canonical superset order is:

1. `AGENTS.md`
2. `AGENTS.override.md`, when a profile is selected
3. `README.md`
4. `README.profile.md`, when a full-tier profile is selected
5. `PRODUCT.md`
6. `MVP.md`
7. `PROJECT_BOUNDARY.md`
8. `DATA_SCOPE.md`, when included
9. `APPROVALS.md`, when included
10. `PHASE_PLAN.md`, when included
11. `STATUS.md`, when included
12. `STATUS.profile.md`, when included
13. `ACCEPTANCE_TRACE.md`, when included
14. `SOURCE_INDEX.md`, when included
15. `SAFETY_POLICY.profile.md`, when a profile is selected
16. `VERIFICATION.profile.md`, when a profile is selected

After omitted entries are removed, numbering must be contiguous. Profile docs
remain adjacent to the corresponding root orientation or state doc where one
exists: `AGENTS.override.md` follows `AGENTS.md`, `README.profile.md` follows
`README.md`, and `STATUS.profile.md` follows `STATUS.md`. A base-only render
must contain no profile-file references.

Reference closure is mandatory: every local Markdown path named by a rendered
Read Order must exist in the planned output set, and the output set must not
depend on an unrendered tier document.

## Readiness Targets

Reference closure applies to every base-only and profiled fixture. The scanner
thresholds below apply to a selected-profile fixture because the current
safety and verification surfaces are profile overlays. A base-only fixture must
still pass reference closure and receive per-dimension review.

| tier | required selected-profile synthetic fixture result |
| --- | --- |
| `minimal` | Reference closure passes and scanner verdict is at least `LIMITED_AI_ASSISTED_WORK_ALLOWED`. |
| `standard` | Reference closure passes and scanner verdict is `READY_FOR_AI_ASSISTED_WORK`. |
| `full` | Reference closure passes and scanner verdict is `READY_FOR_AI_ASSISTED_WORK`. |

These thresholds evaluate the generated fixture, not whether an arbitrary real
repository follows the scanner's preferred filenames. A real target with a low
aggregate score requires dimension review; it does not by itself invalidate the
tier contract.

## External Precedent

The implementation follows only these narrow principles:

- [Copier update behavior](https://copier.readthedocs.io/en/stable/updating/)
  persists template answers, regenerates for comparison, and requires manual
  review when an update conflicts with project changes. Harness upgrades should
  remain compare-first and must not blanket-overwrite curated target content.
- [Cookiecutter replay](https://cookiecutter.readthedocs.io/en/stable/advanced/replay.html)
  persists prior template input, and
  [nested template configuration](https://cookiecutter.readthedocs.io/en/stable/advanced/nested_config_files.html)
  makes template selection explicit in configuration. Harness tier selection
  should likewise be explicit and reproducible.
- The [.NET template engine](https://github.com/dotnet/templating/wiki/Inside-the-Template-Engine)
  exposes creation effects before creation and applies parameter conditions to
  template selection. Harness previews should report the exact tier-selected
  file set before any write.

These references do not approve a Copier, Cookiecutter, or .NET dependency.
Tier implementation remains standard-library/local-tooling based and
must not add hooks, post-actions, network fetches, package installation, or
external template execution.

## Safety Rules

- no automatic target overwrite
- no downstream access in tests
- no raw target content in preview output
- target-relative paths only in diff preview summaries
- no local absolute paths in generated tier metadata or preview JSON
- no change to examples unless explicitly approved
- no quality gate, workflow, artifact, release, tag, or publication side effects
  by this contract alone

## Implementation Acceptance Gate

The implemented renderer must keep the exact matrix and Read Order closure
above, preserve config/CLI precedence and invalid-value rejection, exercise
base-only and profiled fixtures for every tier, and verify the readiness
targets. Dry-run-first behavior and compare-first upgrade policy remain
unchanged.

Future changes must not silently regenerate curated examples, add an external
template dependency, widen downstream access, or change preview schemas without
a separate contract and approval boundary.
