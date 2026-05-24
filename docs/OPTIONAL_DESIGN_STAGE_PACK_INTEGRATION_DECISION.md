# Optional Design-Stage Pack Integration Decision

## Purpose

Record the decision point for whether the optional design-stage pack should remain manual-use-only or move toward render, gate, or example integration.

This document is decision-only. It does not implement render integration, gate support, example integration, profile creation, eval harness work, CI workflows, application code, C# assets, PLC/device artifacts, or live target write support.

## Current State

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
| owner decision | PENDING |
| render integration | PENDING |
| gate integration | PENDING |
| example integration | PENDING |
| status | PENDING |

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

Status: PENDING.

Integration remains not implemented. The manual-use-only baseline is ready for continued downstream use. Any render, gate, or example integration requires a separate explicit owner decision.
