# Simplification Checklist

## Purpose

Prevent the template repository from growing larger or more automated than necessary.

Use this checklist before adding files, templates, gates, profiles, examples, optional packs, or automation.

## Core Questions

| question | answer |
|---|---|
| Is this file, template, or gate necessary now? | TBD |
| Can an existing document cover the need? | TBD |
| Is this base template material, optional pack material, or downstream-only material? | TBD |
| Does this require a profile, or can the base template handle it? | TBD |
| Is manual-use sufficient instead of automation? | TBD |
| Does this increase safety or verification burden? | TBD |
| Does repeated downstream evidence justify the addition? | TBD |
| Is there an explicit owner approval for the added surface? | TBD |

## Placement Decision

| placement | use when |
|---|---|
| base template | The need is broad, repeated, domain-neutral, and safety-relevant |
| optional pack | The need is reusable but phase-specific or situational |
| profile | The need is a durable repeated runtime/tooling variant with validation value |
| downstream-only | The need is project-specific or not yet repeated |
| documentation-only | A policy, decision, checklist, or review record is enough |

## Automation Check

Before adding automation, ask:

- Is manual-use already sufficient?
- Is the manual step causing repeated errors?
- Is the desired automation opt-in and dry-run-first?
- Does automation introduce new side effects?
- Does automation require new tests or gates?
- Does automation risk making optional content look like base behavior?

## Profile Check

Before adding a profile, ask:

- Is this repeated across downstream projects?
- Is the tool/runtime boundary stable?
- Is it meaningfully different from base templates plus existing profiles?
- Does it need a regression example?
- Does it add safety or verification value?
- Is owner approval explicit?

## Safety And Verification Burden

Any new surface may require:

- documentation updates
- acceptance trace rows
- status updates
- tests
- quality gate updates
- secret/private pattern checks
- downstream adoption guidance
- release/closeout evidence

If the burden is not justified, simplify or defer.

## Conclusion Options

| option | meaning |
|---|---|
| keep | Keep the proposed surface as-is |
| simplify | Reduce scope or remove unnecessary parts |
| merge | Fold into an existing document or template |
| defer | Wait for more evidence or owner approval |
| remove | Delete the proposed addition before it becomes durable |
| downstream-only | Keep the need outside codex-dev-harness |

## Closeout

Record the chosen conclusion, rationale, and evidence before adding durable repo surface.
