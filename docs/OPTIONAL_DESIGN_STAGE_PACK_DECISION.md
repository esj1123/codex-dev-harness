# Optional Design-Stage Pack Decision

## Purpose

Record the owner decision point for whether to implement an optional design-stage pack.

This document is a decision record only. It does not create optional pack templates, render integration, gate implementation, profile folders, examples, eval harness code, CI workflow, application code, C# assets, PLC/device artifacts, or live target write support.

## Current State

- Downstream P2 design feedback is captured in `docs/DOWNSTREAM_FEEDBACK_v0.1.0_P2_DESIGN.md`.
- Optional design-stage pack planning exists in `docs/OPTIONAL_DESIGN_STAGE_PACK_PLAN.md`.
- Implementation is not started.
- Current decision is PENDING.

## Implementation Options

| option | meaning | tradeoff |
|---|---|---|
| Keep planned only | Keep the plan as documentation without implementing templates | Lowest risk; preserves current scope |
| Implement experimental optional pack | Create an optional Markdown-only pack after explicit approval | Useful for repeatable design-stage work, but expands template surface |
| Wait for repeated downstream feedback | Defer implementation until more downstream cases confirm reuse | Stronger evidence before expansion; slower adoption |

## Recommendation

- Implement only if the owner explicitly approves.
- Start as an optional pack, not a base template change.
- Do not create a new profile.
- Do not create a scenario-specific example.
- Do not add runtime or code generation.
- Keep any future implementation Markdown-only unless a separate approval changes scope.

## Candidate Templates

| candidate | include decision |
|---|---|
| DESIGN_WORKPLAN | PENDING |
| CONCEPT_BOUNDARY | PENDING |
| CATEGORY_MAP | PENDING |
| SYNTHETIC_FIXTURE_PLAN | PENDING |
| ACCEPTANCE_EVIDENCE_PLAN | PENDING |
| OPEN_QUESTIONS | PENDING |
| DESIGN_REVIEW_RECORD | PENDING |

## Decision Fields

| field | current value | notes |
|---|---|---|
| owner decision | PENDING | Required before implementation |
| included templates | PENDING | Candidate list is not approved yet |
| render integration | PENDING | No render integration implemented |
| gate integration | PENDING | No gate implementation added |
| example integration | PENDING | No example added |
| status | PENDING | Decision document only |

## Current Decision

PENDING.

## Non-Goals

- No optional design-stage template files.
- No `templates/optional/design_stage` directory.
- No render integration.
- No gate implementation.
- No profile creation.
- No scenario-specific example.
- No eval harness implementation.
- No SBOM/provenance generation.
- No GitHub Actions workflow.
- No application code.
- No C# source, solution, project, XAML, or build assets.
- No PLC/device code.
- No live target write support.
- No raw source content or sensitive values.

## Approval Required Before Implementation

Before creating any optional design-stage pack files, the owner must decide:

- whether to implement or keep planned only;
- which candidate templates are included;
- whether render integration is in scope;
- whether gate integration is in scope;
- whether any example integration is in scope;
- whether implementation remains documentation-only.
