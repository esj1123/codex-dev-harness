# Downstream Doc Review Checklist v0.1.0

## Purpose

Define the manual review checklist and next-phase approval criteria for downstream docs generated from the `v0.1.0` local-first baseline. This document does not fill downstream docs and does not include raw source, sensitive values, live parameters, or implementation code.

## Review Scope

Review these 11 generated downstream documents:

- `SOURCE_INDEX.md`
- `PROJECT_BOUNDARY.md`
- `DATA_SCOPE.md`
- `PHASE_PLAN.md`
- `APPROVALS.md`
- `AGENTS.md`
- `PRODUCT.md`
- `MVP.md`
- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- `README.md`

## SOURCE_INDEX Review Criteria

- Use sanitized source summaries only.
- Record source categories and document roles, not raw source blocks.
- Do not bulk copy source text.
- Do not include operational values, connection details, private files, secrets, or account material.
- Mark unresolved source questions explicitly as TODO or pending review.

## PROJECT_BOUNDARY Review Criteria

- Define what the downstream target is allowed to describe at seed stage.
- Keep implementation, runtime behavior, live integration, and device writes out of scope unless separately approved.
- State that the current target is a scenario simulator design baseline, not a built-in codex-dev-harness profile.
- Confirm no `scenario_simulator` profile or example is required in the template repository.

## DATA_SCOPE Review Criteria

- Separate allowed synthetic/summarized inputs from prohibited private/raw inputs.
- State that generated docs may contain sanitized design summaries only.
- Prohibit secrets, credentials, live configs, device connection details, and sensitive operational values.
- Prohibit IP, port, tag, live parameter, and equipment-specific values.
- Keep raw source material outside the downstream repository.

## PHASE_PLAN Review Criteria

- Keep P1 limited to source, boundary, and data-scope manual fill.
- Require review before any simulator design expansion.
- Require separate approval before any implementation phase.
- Mark build, test, runtime integration, live connection, and device interaction as NOT STARTED unless approved.

## APPROVALS Review Criteria

- Record approval requirements for dry-run review, actual render, generated-doc review, and implementation phase entry.
- Require explicit approval before changing from documentation planning to implementation.
- Require explicit approval before introducing runtime code, C# project files, PLC/device logic, live target write support, or external mutation.
- Record rejected or deferred actions rather than silently omitting them.

## Sensitive Information Prohibition

The downstream docs must not contain:

- Raw source bulk copy.
- IFF/N3G raw source text.
- Sensitive values.
- IP addresses.
- Ports.
- Tags.
- Live parameters.
- Secrets, tokens, keys, credentials, or account details.
- Private input files or private output dumps.
- Equipment-specific connection or control details.

## Raw Source Bulk Copy Prohibition

- Summarize source intent and boundaries instead of copying source text.
- Use source index entries to point to sanitized source categories.
- Keep source excerpts out of generated docs unless a separate review explicitly approves a short, non-sensitive excerpt.
- If a source is too sensitive to summarize safely, record only that the source exists and needs human review.

## Actual Implementation Phase Approval Conditions

Actual implementation must not start until all of these conditions are met:

- P1 source, boundary, and data-scope manual fill is complete.
- Generated docs are reviewed and accepted by a human reviewer.
- `SOURCE_INDEX.md` contains no raw source bulk copy or sensitive values.
- `PROJECT_BOUNDARY.md` clearly defines allowed and prohibited scope.
- `DATA_SCOPE.md` clearly defines private/raw/live data prohibitions.
- `PHASE_PLAN.md` defines the next phase and its gate.
- `APPROVALS.md` records approval for the next phase.
- Runtime code, C# project files, PLC/device code, live target write support, and external mutation are still absent unless separately approved.

## Next Phase Recommendation

- P1: manually fill source, boundary, and data-scope docs with sanitized summaries only.
- P2: proceed to simulator design only after explicit approval.
- Implementation remains deferred until a separate phase approval.

## Review Outcome Values

- PASS: the document is acceptable for the next manual review step.
- PARTIAL: the document is usable but has unresolved questions.
- BLOCKED: sensitive content, raw source copy, live values, or scope ambiguity prevents proceeding.
- NOT REVIEWED: the document has not yet been manually reviewed.
