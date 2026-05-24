# Optional Design-Stage Pack Integration Decision

## Purpose

Record the decision point for whether the optional design-stage pack should remain manual-use-only or move toward render, gate, or example integration.

This document is decision-only. It does not implement render integration, gate support, example integration, profile creation, eval harness work, CI workflows, application code, C# assets, PLC/device artifacts, or live target write support.

## Current Evidence

- Optional design-stage template files are present under `templates/optional/design_stage/`.
- Usage guide is present: `docs/OPTIONAL_DESIGN_STAGE_PACK_USAGE.md`.
- Review record is refreshed: `docs/OPTIONAL_DESIGN_STAGE_PACK_REVIEW.md`.
- Manual feedback 001 is documented: `docs/OPTIONAL_DESIGN_STAGE_PACK_MANUAL_FEEDBACK_001.md`.
- Manual feedback 002 is documented: `docs/OPTIONAL_DESIGN_STAGE_PACK_MANUAL_FEEDBACK_002.md`.
- All seven optional design-stage templates have PASS manual-use review evidence.
- Render integration is not implemented.
- Gate integration is not implemented.
- Example integration is not implemented.

## Integration Options

| option | description | tradeoff |
|---|---|---|
| 1. Keep manual-use-only | Keep optional templates available for manual copy, merge, skip, or review-only use | Lowest implementation risk; no automation support |
| 2. Limited opt-in render integration | Add a clearly requested opt-in render path for optional design-stage templates | More convenient, but render behavior and target safety need separate design |
| 3. Render + gate integration | Add opt-in render behavior plus validation that optional design-stage docs meet required boundaries | Stronger governance, but higher maintenance and schema complexity |
| 4. Render + gate + example integration | Add render behavior, validation, and a regression example | Highest coverage, but most likely to overfit unless repeated downstream demand exists |

## Recommended Default

Keep the optional design-stage pack manual-use-only unless the owner explicitly approves integration.

The current PASS evidence supports safe manual use. It does not by itself approve render, gate, or example integration.

## Owner Decision

| field | decision |
|---|---|
| owner decision | KEEP MANUAL-USE-ONLY BASELINE |
| render integration | DEFERRED |
| gate integration | DEFERRED |
| example integration | DEFERRED |
| status | MANUAL-USE-ONLY BASELINE CLOSED |

## Rationale

- Manual use is sufficient for the current evidence.
- Render, gate, and example integration would expand the maintenance surface.
- Any integration requires a separate explicit owner approval.
- The optional design-stage pack should not become part of the base template by accident.
- Keeping manual-use-only preserves the optional-pack boundary while still allowing downstream teams to copy, merge, skip, or review-only the templates.

## Future Triggers

Integration can be reconsidered if one or more of the following triggers appears:

- Repeated manual-use friction.
- Repeated copy or rename errors.
- Clear need for opt-in render support.
- Clear need for optional pack validation.
- Explicit owner approval for render, gate, or example integration.

## Possible Staged Path

| stage | name | scope | approval need |
|---|---|---|---|
| Stage I | Manual-use-only baseline | Templates, usage guide, review, and manual feedback records | Current state |
| Stage II | Limited opt-in render integration | Optional render path only, with explicit config selection and dry-run-first behavior | Separate owner approval |
| Stage III | Validation/gate support | Boundary checks for optional design-stage docs | Separate owner approval after Stage II |
| Stage IV | Example integration | Regression example for optional design-stage pack behavior | Separate owner approval after Stage III |

## Decision Fields

| field | decision |
|---|---|
| owner decision | KEEP MANUAL-USE-ONLY BASELINE |
| render integration | DEFERRED |
| gate integration | DEFERRED |
| example integration | DEFERRED |
| status | MANUAL-USE-ONLY BASELINE CLOSED |

## Non-Goals

- No `render_template.py` change.
- No `quality_gate.py` change.
- No `template_schema_gate.py` change.
- No `example_gate.py` change.
- No `example_render_drift_gate.py` change.
- No example integration.
- No scenario-specific profile or example.
- No eval harness.
- No workflow.
- No runtime implementation.
- No application code.
- No C# source, solution, project, XAML, or build asset.
- No PLC/device code.
- No live target write support.
- No raw source bulk copy.
- No sensitive values, private input, live config, credentials, accounts, or equipment details.

## Current Decision

Status: MANUAL-USE-ONLY BASELINE CLOSED.

Integration remains not implemented. The manual-use-only baseline is closed and ready for continued downstream use. Any future render, gate, or example integration requires a separate explicit owner decision.
