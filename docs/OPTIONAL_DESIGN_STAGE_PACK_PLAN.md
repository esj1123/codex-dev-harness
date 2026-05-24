# Optional Design-Stage Pack Plan

## Purpose

Plan a future optional template pack for design-only phases.

The pack helps downstream projects structure design work before implementation is approved. This plan is now approved for experimental Markdown-only template files. It still does not approve render integration, gate implementation, profile creation, examples, runtime code, or implementation artifacts.

## Candidate Templates

| candidate template | intended role |
|---|---|
| `DESIGN_WORKPLAN.md.template` | Define approved design-only purpose, scope, source use, candidate outputs, and exit criteria |
| `CONCEPT_BOUNDARY.md.template` | Define concept boundaries and prohibited implementation/live-target scope |
| `CATEGORY_MAP.md.template` | Map generalized design categories, synthetic input categories, abstract output categories, and evidence references |
| `SYNTHETIC_FIXTURE_PLAN.md.template` | Plan synthetic fixture categories without real/private/live data |
| `ACCEPTANCE_EVIDENCE_PLAN.md.template` | Plan requirement-to-evidence coverage for design-stage outputs |
| `OPEN_QUESTIONS.md.template` | Track owner-review items, deferred source rows, risks, and blockers |
| `DESIGN_REVIEW_RECORD.md.template` | Record design-only, source-use, sensitive-information, and prohibited-artifact review results |

## Current State

- Experimental Markdown-only template files are created.
- Template files live under `templates/optional/design_stage/`.
- Render support is not added.
- Gate implementation is not added.
- Profile creation is not added.
- Example integration is not added.
- Runtime/code generation is not added.

## Promotion Criteria

An optional design-stage pack may be implemented only when all criteria are met:

- Repeated downstream use shows the same design-stage documents are useful.
- Wording can remain domain-neutral.
- The pack does not depend on sensitive source material.
- The pack does not require raw source copy.
- The pack does not require runtime or code generation.
- The pack does not require C# source/project assets, PLC/device code, live target write support, or cloud CI.
- The pack can be rendered as Markdown-only documentation.
- Template implementation is explicitly approved as a follow-up task.

## Base Template vs Optional Pack vs Downstream-Only

| placement | use when |
|---|---|
| base template | The control is broadly required for most governed local-first projects |
| optional pack | The control is reusable across multiple projects but not needed by every baseline target |
| downstream-only | The document reflects one project, one domain interpretation, or unresolved source-specific decisions |

## Non-Goals

- No profile creation.
- No `scenario_simulator` profile or example.
- No P2 implementation.
- No eval harness implementation.
- No SBOM/provenance work.
- No GitHub Actions workflow.
- No C# source, solution, project, XAML, or build assets.
- No PLC/device artifacts.
- No live target write support.
- No downstream source content or sensitive values.

## Next Step

Review the experimental template files and decide whether render integration, gate integration, or example integration should be separately approved. Until then, the pack remains template-files-only.
