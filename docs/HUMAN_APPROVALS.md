# Human Approvals

## Purpose

Define when human approval is required for codex-dev-harness work and what an approval record must contain.

This document is policy-only. It does not grant approval, create an approval database, add audit logging, or implement side-effect tooling.

## Approval Principle

Approval must be specific, reviewable, and tied to an expected change. Broad approval for undefined future work is not sufficient.

Default order:

1. Read-only inspection.
2. Dry-run or expected-change summary.
3. Human review of intended scope.
4. Explicit approval for the specific side effect.
5. Execution within approved scope.
6. Closeout with evidence.

## Approval Required

Explicit owner approval is required before:

- file delete, move, rename, or broad overwrite
- writing outside the approved repository scope
- rendering into a downstream target without prior dry-run review
- adding or modifying scripts, gates, eval runners, or release tooling
- creating audit schemas or durable audit logs
- generating release manifest, checksum, SBOM, or provenance artifacts
- installing GitHub Actions workflows
- publishing GitHub Releases
- creating, moving, or signing tags
- adding profiles or examples
- integrating optional packs into render, gate, or examples
- adding application, C#, PLC/device, or live target write behavior
- sending messages, mutating external services, or writing databases

## Approval Record Fields

Use these fields in documentation or downstream approval records:

| field | purpose |
|---|---|
| approval_id | Stable identifier for the approval decision |
| requested_action | Specific action being approved |
| side_effect_class | File write, external mutation, release action, workflow, live target, or other class |
| scope | Files, folders, commands, or target systems covered |
| approver | Person or owner granting approval |
| approval_status | Approved, denied, pending, or superseded |
| evidence | Dry-run output, expected-change summary, review note, or decision link |
| constraints | Limits that must be preserved during execution |
| expiry | Optional end condition or date for the approval |

## Deny By Default

If approval is missing, ambiguous, stale, or broader than the reviewed change, treat the action as not approved.

## Non-Goals

This policy does not approve or implement:

- an audit log schema
- audit log persistence
- release verification tooling
- eval harnesses
- workflow installation
- live target write support
- real application or device code
