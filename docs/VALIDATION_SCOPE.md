# VALIDATION_SCOPE.md

## Purpose

Define what the current validation suite proves, what it does not prove, and how broad downstream project types should be validated without creating a profile for every project type.

## Current Regression Coverage

Current regression examples:
- `python_cli_minimal`
- `csharp_desktop_minimal`
- `plc_tool_minimal`

These examples verify that the base template, profile overlays, safety policy, and quality gates remain coherent. They are not full applications.

## Regression Example Contract

The regression examples are curated regression skeletons, not byte-for-byte
rendered snapshots.

Each example must contain every file the renderer would produce for its
`template.config.yml`, but the example files may include reviewed,
profile-specific wording that differs from the raw template output.

`example_render_drift_gate` therefore verifies rendered file-set coverage only:
it checks that expected rendered paths exist and does not compare rendered file
content.

Future content-level drift enforcement must use a separate golden render
fixture or an explicitly approved example regeneration task. Do not point a
content-hash gate at the curated `examples/*_minimal` directories unless that
task also approves replacing their curated content with generated snapshots.

## Template-Level Validation

The template should support project types that need:
- source-index driven review
- data-scope controlled handling
- phase-gated development
- simulator/mock-first workflow
- side-effect bounded execution
- approval-gated mutation

These requirements belong in base templates when they are broadly useful across many domains.

## Downstream Candidates

Downstream candidates include:
- scenario simulator design
- local automation tool
- documentation-only planning repo
- data pipeline planning repo
- desktop tool planning repo

These candidates can be supported by the base template without becoming first-class profiles.

## Profile Rule

Do not create a profile for every project type.

Create a profile only when all are true:
- the shape repeats across multiple projects
- the safety boundary differs materially from the base template
- the repo can maintain a regression example for it
- the profile adds durable value beyond a domain-specific note
- the change has explicit approval

## Out Of Scope

Current validation does not prove:
- real application runtime behavior
- C# solution or project compilation
- PLC/device connectivity
- live target write behavior
- deployment behavior
- GitHub Actions execution

These remain downstream responsibilities.
