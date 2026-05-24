# Optional Design-Stage Pack Usage

## Purpose

This guide explains how to manually use the optional design-stage pack without render integration, gate integration, or example integration.

The pack is intended for documentation-only design phases where a downstream project needs stronger scope control before any implementation is approved.

## Current State

- Optional design-stage template files exist under `templates/optional/design_stage/`.
- Render integration is DEFERRED.
- Gate integration is DEFERRED.
- Example integration is DEFERRED.
- The pack is Markdown-only and manual-use-only.
- The pack does not create profiles, examples, runtime code, CI workflows, or live target support.

## When To Use

Use the optional design-stage pack when:

- the downstream project is in a P2 design-only phase;
- implementation must remain deferred until a later approval;
- design scope needs to be controlled before runtime work starts;
- source-use decisions are needed before source summaries can be used;
- synthetic fixture planning is needed without real, private, or live data;
- a design review record is needed before expanding the design surface.

## When Not To Use

Do not use this pack when:

- the project is simple enough for the base template alone;
- the downstream target does not need design-stage source-use decisions;
- runtime or code generation is the actual goal;
- an implementation phase has already been approved and another workflow is required;
- copying optional templates would add process overhead without reducing risk.

## Recommended Manual Use Order

1. `DESIGN_WORKPLAN`
2. `CONCEPT_BOUNDARY`
3. `CATEGORY_MAP`
4. `SYNTHETIC_FIXTURE_PLAN`
5. `ACCEPTANCE_EVIDENCE_PLAN`
6. `OPEN_QUESTIONS`
7. `DESIGN_REVIEW_RECORD`

## Downstream Naming Map

The mapping below is a manual-use aid only. Template names in this repository remain domain-neutral. Downstream-specific naming is allowed only inside the downstream target.

| optional template | possible downstream equivalent | use mode | notes |
|---|---|---|---|
| `DESIGN_WORKPLAN` | `DESIGN_WORKPLAN` or phase-specific design plan | copy, merge, or review-only | Use when the downstream target needs explicit phase scope, source-use decisions, candidate outputs, and exit criteria |
| `CONCEPT_BOUNDARY` | `CONCEPT_BOUNDARY` or project-specific concept boundary | copy, merge, or review-only | Use when concept scope and prohibited implementation/live-target boundaries need to be explicit |
| `CATEGORY_MAP` | `CATEGORY_MAP` or domain-specific category map | copy, merge, or review-only | Use for generalized category mapping with synthetic input and abstract output categories |
| `SYNTHETIC_FIXTURE_PLAN` | `SYNTHETIC_FIXTURE_PLAN` | copy, merge, or review-only | Use when synthetic fixture categories are needed without creating fixture files |
| `ACCEPTANCE_EVIDENCE_PLAN` | `ACCEPTANCE_EVIDENCE_PLAN` or phase-specific evidence plan | copy, merge, or review-only | Use when design-stage requirements need evidence categories before runtime validation exists |
| `OPEN_QUESTIONS` | `OPEN_QUESTIONS` or phase-specific open questions | copy, merge, or review-only | Use when owner-review source rows, deferred decisions, or approval blockers must be tracked |
| `DESIGN_REVIEW_RECORD` | `DESIGN_REVIEW_RECORD` or phase-specific review record | copy or review-only | Use after design-stage documents exist to record source-use, sensitive-information, and prohibited-artifact review |

## Skip, Merge, Or Review-Only Guidance

- Skip a template when the downstream target already has an equivalent document and it already records design-only scope, source-use decisions, prohibited content, approval boundary, and review checklist.
- Merge a template when an existing downstream document is useful but lacks source-use rules, prohibited-content boundaries, owner-review handling, or explicit integration deferral.
- Use review-only mode when downstream design documents are already written and the optional template should be used only as a checklist for compliance review.
- Do not copy optional templates into a downstream target just to increase document count. Use them only when they reduce ambiguity or risk.
- Keep any renamed downstream document within the downstream target only. Do not rename the template files in this repository for domain-specific usage.

## Manual Adoption Flow

1. Prepare a downstream target from the base template.
2. Confirm that the current phase approval allows design-only documentation work.
3. Manually copy the optional design-stage templates into the downstream target.
4. Rename copied files only in the downstream target when creating project documents.
5. Replace project placeholders with domain-neutral summaries only.
6. Apply source-use decisions before using any source row in design content.
7. Keep owner-review source rows unused until they are accepted, revised, or deferred.
8. Keep excluded source rows outside repository and target content.
9. Run a prohibited content scan or manual review before sharing or packaging.
10. Write the design review record after the design-stage documents are drafted.

## Source-Use Rules

- Use only generalized source categories and approved source summaries.
- Do not bulk-copy raw source material.
- Mark owner-review sources as pending until the owner decides how they may be used.
- Mark excluded sources as unavailable for repository or downstream target content.
- Keep unresolved source questions in `OPEN_QUESTIONS` or the downstream equivalent.

## Prohibited Content

Do not add:

- raw source bulk copy;
- IP, port, tag, or live parameter values;
- secret, private, or live config values;
- C# source, solution, project, XAML, or build assets;
- PLC/device code;
- live target write support;
- GitHub Actions or cloud CI workflow files;
- scenario-specific profile or example creation;
- runtime implementation artifacts.

## Prohibited Content Scan Examples

The commands below are examples for manual review. They are not gate integration and they do not replace human review. Adjust paths for the downstream target before running them.

```powershell
rg -n "<IP address regex>" <downstream-target>
rg -n -i "password|secret|token|api_key" <downstream-target>
rg -n -i "connection string|port|tag|live parameter" <downstream-target>
rg --files <downstream-target> -g "*.sln" -g "*.csproj" -g "*.cs" -g "*.xaml"
rg --files <downstream-target> -g ".github/workflows/**" -g ".env" -g "*.exe" -g "*.dll"
```

Interpret matches conservatively:

- Policy-only mentions may be acceptable when they do not include real values.
- Any value-like match should be reviewed before packaging or sharing.
- Runtime, C#, PLC/device, workflow, executable, and live configuration artifacts require separate approval or removal.

## Future Integration Boundary

- Render integration requires separate owner approval.
- Gate integration requires separate owner approval.
- Example integration requires separate owner approval.
- Any runtime/code generation support requires a separate phase decision and remains out of scope for this guide.

## Review Checklist

- The target started from the base template.
- Phase approval permits design-only work.
- Optional templates were copied manually.
- Placeholders were replaced with generalized, non-sensitive content only.
- Owner-review source rows were not used before owner decision.
- Excluded source rows remain outside repository and target content.
- No prohibited runtime, device, live-write, CI, secret, or private-data artifacts were added.
- `DESIGN_REVIEW_RECORD` or the downstream equivalent records the review result.
