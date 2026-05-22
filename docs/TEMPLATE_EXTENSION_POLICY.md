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

## Absorb Or Profile Decision

Use this decision rule:
- If the need is broad governance, add it to the base template.
- If the need is a repeated workflow variant with different safety defaults, consider a profile.
- If the need is one project, keep it downstream.
- If the need requires live values, private source, or implementation code, keep it out of this repo.

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
