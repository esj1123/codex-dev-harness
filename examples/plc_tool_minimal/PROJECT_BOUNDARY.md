# PROJECT_BOUNDARY.md

## Purpose

Define the boundary for `plc_tool_minimal`.

## In Scope

- Docs-only rendered template skeleton.
- Device-tool safety policy notes.
- Simulator/mock-first expectation.
- Read-only planning language.

## Out Of Scope

- Device code.
- Live device write behavior.
- Live configuration.
- Start, stop, reset, or mode-change behavior.
- External mutation.

## No-Touch Zones

| zone | reason | approval path |
|---|---|---|
| Live target interaction | Regression example must not touch live systems | Separate downstream safety approval required |
| Runtime implementation | This example is a skeleton | Downstream project approval required |

## Approval-Required Changes

- Adding device runtime code.
- Adding live configuration.
- Adding external mutation behavior.
- Writing outside this example folder.

