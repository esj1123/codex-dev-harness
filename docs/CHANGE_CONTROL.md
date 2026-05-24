# Change Control

## Purpose

Define how changes to codex-dev-harness should be proposed, reviewed, verified, and closed without expanding the repository into an application project.

This document is policy-only. It does not create automation, release tooling, CI workflows, prompt templates, evals, audit schemas, or generated artifacts.

## Change Classes

| class | description | default path |
|---|---|---|
| documentation-only | Markdown policy, status, trace, guide, or decision updates | local review and documentation readback |
| template surface | Base template, profile template, or optional pack changes | explicit scope approval plus render dry-run |
| gate or script behavior | Render, quality gate, verification wrapper, or test changes | implementation approval plus tests and quality gate |
| release evidence | Manifest, checksum, SBOM, provenance, or release wrapper work | separate owner approval before implementation |
| profile or example expansion | New profile, new example, or optional pack integration | separate owner approval and validation plan |
| external side effect | Workflow installation, release publication, tag movement, external send, database write, or live target write | explicit owner approval for the specific action |

## Required Change Contract

Every non-trivial task should state:

- goal
- write scope
- expected files
- no-touch files and actions
- verification commands or readback checks
- closeout report fields

When scope is unclear, default to read-only review or documentation-only planning.

## Review Expectations

Before changing files:

- Read the applicable project contract documents.
- Identify likely touch files and likely no-touch files.
- Check whether an existing document can absorb the change.
- Confirm that the change does not require implementation approval.

After changing files:

- Report changed files.
- Report commands run.
- Report verification results.
- Report safety checks.
- Record unresolved risks or approval needs.

## Approval Gates

Separate owner approval is required before:

- adding or changing runtime scripts beyond a documentation-only task
- creating `evals/`, eval runners, or eval gates
- creating audit schema files or audit log writers
- generating release manifest, checksum, SBOM, or provenance artifacts
- adding release verification wrappers
- installing `.github/workflows`
- publishing a GitHub Release
- creating, moving, or signing tags
- adding profiles, examples, or optional pack render/gate/example integration
- adding real application, C#, PLC/device, or live-write behavior

## Non-Goals

This policy does not approve:

- release/eval/audit implementation
- prompt template files
- manifest/checksum/SBOM/provenance generators
- workflow installation
- new profiles or examples
- application code
- C# source, solution, project, or XAML files
- PLC/device code
- live target write support
