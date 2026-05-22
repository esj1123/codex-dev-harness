# DOMAIN_ADAPTATION_GUIDE.md

## Purpose

Explain how to adapt codex-dev-harness to a downstream project such as a scenario simulator design while keeping this repository generic and local-first.

## Adaptation Flow

1. Start from the base template.
2. Choose an existing profile only if it fits the workflow shape.
3. Render into a separate target folder using dry-run first.
4. Fill project-specific information in the downstream target, not in this template repo.
5. Keep raw sources, sensitive values, and live details out of generated template docs.
6. Use approval records before any mutation or side-effecting action.

## Scenario Simulator Candidate

A scenario simulator design can use the base template without a dedicated profile.

Recommended base files:
- `SOURCE_INDEX.md`
- `PROJECT_BOUNDARY.md`
- `DATA_SCOPE.md`
- `PHASE_PLAN.md`
- `APPROVALS.md`
- `ACCEPTANCE_TRACE.md`
- `STATUS.md`

The downstream project can describe simulation phases, data categories, acceptance evidence, and approval checkpoints without adding simulator-specific implementation code to this template.

## SOURCE_INDEX

Use `SOURCE_INDEX.md` to list source categories and references at a high level.

Do not bulk-copy raw source text. Summarize source role, trust level, ownership, and allowed use.

## PROJECT_BOUNDARY

Use `PROJECT_BOUNDARY.md` to separate:
- what the project will do
- what it will not do
- no-touch zones
- downstream-only implementation areas
- approval-required changes

## DATA_SCOPE

Use `DATA_SCOPE.md` to define data classes:
- public or synthetic data
- private input
- generated output
- derived summaries
- prohibited data

Do not include sensitive values, live configuration, account data, or equipment details.

## PHASE_PLAN

Use `PHASE_PLAN.md` for phase-gated work:
- planning
- scaffold
- dry-run validation
- implementation readiness
- release readiness

Each phase should define entry conditions, allowed work, verification, and exit criteria.

## APPROVALS

Use `APPROVALS.md` to record approval decisions for side-effecting work:
- file writes outside the target folder
- overwrite operations
- external service mutation
- live target interaction
- release or publication actions

## Prohibited Content

Do not record:
- raw source bulk copy
- sensitive requirements text
- IP addresses
- ports
- tags
- live parameters
- secrets
- private input
- live target configuration

## Conclusion

Use base template extensions for broad governance needs. Keep scenario simulator details in the downstream project unless repeated evidence justifies a new profile through the approval-gated profile process.
