# Optional Design-Stage Pack Decision

## Purpose

Record the owner decision point for whether to implement an optional design-stage pack.

This document records the approval to create optional pack template files only. It does not approve render integration, gate implementation, profile folders, examples, eval harness code, CI workflow, application code, C# assets, PLC/device artifacts, or live target write support.

## Current State

- Downstream P2 design feedback is captured in `docs/DOWNSTREAM_FEEDBACK_v0.1.0_P2_DESIGN.md`.
- Optional design-stage pack planning exists in `docs/OPTIONAL_DESIGN_STAGE_PACK_PLAN.md`.
- Owner decision is IMPLEMENT EXPERIMENTAL OPTIONAL PACK.
- Experimental Markdown-only template files are created under `templates/optional/design_stage/`.
- Render integration is DEFERRED.
- Gate integration is DEFERRED.
- Example integration is DEFERRED.
- Status is APPROVED FOR TEMPLATE FILES ONLY.

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
| DESIGN_WORKPLAN | APPROVED |
| CONCEPT_BOUNDARY | APPROVED |
| CATEGORY_MAP | APPROVED |
| SYNTHETIC_FIXTURE_PLAN | APPROVED |
| ACCEPTANCE_EVIDENCE_PLAN | APPROVED |
| OPEN_QUESTIONS | APPROVED |
| DESIGN_REVIEW_RECORD | APPROVED |

## Decision Fields

| field | current value | notes |
|---|---|---|
| owner decision | IMPLEMENT EXPERIMENTAL OPTIONAL PACK | Approved for template files only |
| included templates | APPROVED | Seven Markdown-only templates included |
| render integration | DEFERRED | No render integration implemented |
| gate integration | DEFERRED | No gate implementation added |
| example integration | DEFERRED | No example added |
| status | APPROVED FOR TEMPLATE FILES ONLY | Experimental optional pack templates created |

## Current Decision

APPROVED FOR TEMPLATE FILES ONLY.

## Non-Goals

- No render integration.
- No gate implementation.
- No example integration.
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

## Approval Required Before Further Implementation

Before adding render, gate, example, or workflow integration, the owner must decide:

- whether render integration is in scope;
- whether gate integration is in scope;
- whether any example integration is in scope;
- whether implementation remains documentation-only.
