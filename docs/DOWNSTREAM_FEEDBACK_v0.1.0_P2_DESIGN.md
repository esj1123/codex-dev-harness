# Downstream Feedback: v0.1.0 P2 Design

## Purpose

Capture template-level feedback from a v0.1.0 downstream P2 design-only adoption without copying downstream scenario content into this repository.

This record is about template improvement signals only. It does not import downstream domain details, raw source content, sensitive values, implementation logic, or project-specific simulator design.

## Feedback Source

- v0.1.0 downstream P2 design-only adoption.
- Base-template-only downstream target.
- No downstream profile.
- No implementation phase.

## Reviewed Downstream Doc Types

- Simulator concept boundary.
- Scenario category map.
- Synthetic fixture plan.

These doc types are referenced as patterns observed during downstream use. Their project-specific content is not copied here.

## Template-Level Observations

| observation | template implication |
|---|---|
| P2 design workplan helped prevent implementation drift | A design-stage workplan pattern is useful before allowing design outputs |
| Source-use decision helped prevent unsafe source use | Source rows should remain explicit and phase-aware |
| Synthetic fixture planning is reusable | Synthetic fixture planning may be useful beyond one downstream project |
| Review-before-expansion is useful | Design output creation should be followed by a review record before expanding scope |
| Design-only review surfaced phase wording drift | Phase/status documents should be refreshed during design-stage closeout |

## Gaps

- No standard optional design-stage pack exists yet.
- No standard P2 design review record template exists yet.
- No standard acceptance evidence plan template exists yet.
- No standard open questions template exists yet.
- No reusable guidance exists for promoting repeated downstream design-stage documents into optional packs.

## Non-Goals

- No IFF/N3G source content.
- No downstream raw source material.
- No sensitive values, IP values, port values, tag values, live parameters, equipment details, secrets, or live configuration.
- No `scenario_simulator` profile.
- No `examples/scenario_simulator_minimal`.
- No runtime code.
- No C# source, solution, or project files.
- No PLC/device code.
- No live target write support.
- No GitHub Actions workflow.

## Feedback Conclusion

The downstream P2 design-only adoption suggests a future optional design-stage pack may be useful, but the evidence is not sufficient to implement the pack immediately. The next step is review and explicit approval before creating any optional templates.
