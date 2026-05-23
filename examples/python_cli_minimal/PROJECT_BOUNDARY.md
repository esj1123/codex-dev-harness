# PROJECT_BOUNDARY.md

## Purpose

Define the boundary for `python_cli_minimal`.

## In Scope

- Docs-only rendered template skeleton.
- Python CLI profile policy notes.
- Local verification expectation notes.
- Synthetic fixture policy.

## Out Of Scope

- Real Python package implementation.
- CLI runtime behavior.
- Real input parsing.
- External service calls.
- Private input storage.

## No-Touch Zones

| zone | reason | approval path |
|---|---|---|
| Runtime implementation | This example is a skeleton | Downstream project approval required |
| Real user data | Regression example must stay synthetic | Keep outside repository |

## Approval-Required Changes

- Adding Python runtime code.
- Adding real CLI commands.
- Adding non-synthetic data.
- Writing outside this example folder.

