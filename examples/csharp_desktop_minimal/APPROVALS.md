# APPROVALS.md

## Purpose

Record approval decisions for `csharp_desktop_minimal`.

## Approval Table

| approval_id | requested action | side effect | approver | status | evidence | notes |
|---|---|---|---|---|---|---|
| APR-001 | Maintain docs-only skeleton | None | template maintainer | APPROVED | current example files | Regression example only |
| APR-002 | Add desktop runtime files | File creation | TBD | NOT REQUESTED | none | Downstream only |

## Approval Rules

- Dry-run before render writes.
- Do not add C# runtime files without downstream approval.
- Do not add private input or live configuration.

