# TEMPLATE_EXTENSION_POLICY.md

## Purpose

Define when to extend the base template, when to add or modify a profile, and when to keep domain-specific material in a downstream project.

## Base Template Extension Criteria

Extend the base template when the new document or control:
- applies across many project types
- improves source traceability, boundaries, safety, verification, or handoff
- can be rendered into a target project without creating runtime code
- does not depend on domain-sensitive values
- does not require a new example application

Examples that belong in the base template:
- source index
- project boundary
- data scope
- phase plan
- approvals

## Profile Addition Criteria

Add a profile only when the workflow shape is durable and materially different from the base template.

A profile needs:
- repeated use across projects
- clear safety defaults
- distinct verification expectations
- a maintained minimal example
- explicit approval

Profile addition is an approval-gated side effect because it expands the public template surface.

## Domain-Specific Material

Keep material in a downstream project when it:
- describes one product only
- includes domain-specific source interpretation
- depends on private data or live configuration
- cannot be validated by this template repo
- would encourage copying raw source material into the template

Scenario simulator work belongs here as a downstream application candidate unless repeated use proves a durable profile is needed.

## Downstream Feedback Promotion Criteria

Downstream feedback may influence this template only when it is generalized before being recorded here.

Promotion requires:

- repeated downstream use, not a single project preference
- domain-neutral wording
- no raw source copy
- no sensitive source dependency
- no IP, port, tag, live parameter, equipment detail, secret, private input, or live configuration
- no runtime/code generation requirement
- no C# source/project, PLC/device code, live target write support, or cloud CI requirement
- explicit approval before creating new templates, packs, gates, profiles, or examples

Feedback may be documented before promotion, but documentation of feedback does not approve implementation.

## Base Template vs Optional Pack vs Downstream-Only

Use this placement rule:

| placement | choose when |
|---|---|
| base template | The control is required across most governed local-first projects |
| optional pack | The control is reusable across multiple projects but should not be part of every baseline render |
| downstream-only | The material is specific to one project, one domain interpretation, or unresolved source decisions |

Optional packs are appropriate for repeatable design-stage patterns that remain Markdown-only and domain-neutral. They should not be used to smuggle a domain profile into the base template.

## Absorb Or Profile Decision

Use this decision rule:
- If the need is broad governance, add it to the base template.
- If the need is a repeated workflow variant with different safety defaults, consider a profile.
- If the need is one project, keep it downstream.
- If the need requires live values, private source, or implementation code, keep it out of this repo.

## Profile As Last Resort

Profile creation is the last resort, not the default response to downstream feedback.

Before creating a profile, prefer this order:

1. Keep the material downstream when it is project-specific.
2. Document feedback when the pattern is promising but not proven.
3. Plan an optional pack when the pattern repeats and stays domain-neutral.
4. Extend the base template only when the control belongs in nearly every target.
5. Add a profile only when repeated use proves a durable workflow variant with distinct safety and verification defaults.

## Hard Boundaries

Do not add:
- real application code
- C# source, solution, or project files
- PLC/device code
- live target write support
- raw source bulk copies
- sensitive values
- equipment connection details
- project-specific profile folders without approval
