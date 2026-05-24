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
