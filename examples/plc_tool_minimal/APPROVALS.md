# APPROVALS.md

## Purpose

Record approval decisions for `plc_tool_minimal`.

## Approval Table

| approval_id | requested action | side effect | approver | status | evidence | notes |
|---|---|---|---|---|---|---|
| APR-001 | Maintain docs-only skeleton | None | template maintainer | APPROVED | current example files | Regression example only |
| APR-002 | Add device runtime behavior | Live side effect risk | TBD | NOT REQUESTED | none | Downstream only |

## Approval Rules

- Dry-run before render writes.
- Do not add live target behavior.
- Do not add device code or live configuration.

