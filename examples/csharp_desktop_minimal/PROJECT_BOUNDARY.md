# PROJECT_BOUNDARY.md

## Purpose

Define the boundary for `csharp_desktop_minimal`.

## In Scope

- Docs-only rendered template skeleton.
- C# desktop profile policy notes.
- Phase gate expectations.
- Build/test/smoke status notes.

## Out Of Scope

- C# source code.
- Solution files.
- Project files.
- Build scripts.
- Test scripts.
- Smoke scripts.
- Desktop runtime behavior.

## No-Touch Zones

| zone | reason | approval path |
|---|---|---|
| Runtime implementation | This example is a skeleton | Downstream project approval required |
| Build pipeline files | No scripts in regression skeleton | Downstream project approval required |

## Approval-Required Changes

- Adding source, solution, or project files.
- Adding build, test, or smoke scripts.
- Writing outside this example folder.

