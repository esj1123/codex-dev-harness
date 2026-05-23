# APPROVALS.md

## Purpose

Record approval decisions for `python_cli_minimal`.

## Approval Table

| approval_id | requested action | side effect | approver | status | evidence | notes |
|---|---|---|---|---|---|---|
| APR-001 | Maintain docs-only skeleton | None | template maintainer | APPROVED | current example files | Regression example only |
| APR-002 | Add runtime implementation | File creation | TBD | NOT REQUESTED | none | Downstream only |

## Approval Rules

- Dry-run before render writes.
- Do not add runtime code without downstream approval.
- Do not add private input or live configuration.

