# Audit Log Policy

## Purpose

Define the intended audit logging boundary for future codex-dev-harness work without creating an audit schema or audit log implementation.

This document is policy-only. It does not create `audits/`, `audit-log.schema.json`, JSONL files, log writers, telemetry, or persistence tooling.

## Current State

The repository records acceptance evidence in `ACCEPTANCE_TRACE.md`, status evidence in `STATUS.md`, and release evidence in Markdown records.

Machine-readable audit logging is not implemented.

## Audit Log Goals

Future audit records, if approved, should help answer:

- what task was requested
- what repository state was used
- what files changed
- what commands ran
- what approvals were required
- what approvals were granted
- what checks passed, failed, or were not run
- whether prohibited surfaces were avoided

## Minimum Future Record Fields

If an audit schema is approved later, it should consider:

| field | purpose |
|---|---|
| task_id | Stable task identifier |
| timestamp_utc | When the event occurred |
| repo_path | Repository or target path |
| repo_sha | Commit SHA when available |
| actor | Human or agent actor |
| model_id | AI model identifier when relevant |
| prompt_or_contract_id | Task contract or prompt reference |
| side_effect_class | Read-only, file write, release action, workflow, live target, or external mutation |
| approval_id | Approval record tied to the action |
| files_changed | Paths changed by the task |
| commands_run | Commands used for verification or execution |
| verification_result | PASS, FAIL, PARTIAL, BLOCKED, or NOT RUN |
| safety_checks | Scope and prohibited-content checks |
| output_hashes | Optional hashes for generated artifacts |

## Sensitive Content Rules

Audit records must not include:

- secrets, credentials, tokens, keys, or account material
- private raw input
- raw source bundles
- sensitive business source text
- equipment IPs, ports, tags, parameters, or live values
- full prompt content when it contains sensitive material
- live configuration

Use identifiers, summaries, hashes, or redacted references instead.

## Approval Requirements

Separate owner approval is required before:

- creating `audits/`
- creating `audit-log.schema.json`
- writing JSONL audit logs
- adding audit log writers to scripts
- adding telemetry or external logging
- making audit logs release-blocking

## Non-Goals

This policy does not approve or implement:

- audit schema files
- audit log storage
- telemetry
- eval logging
- release manifest generation
- SBOM/provenance generation
- live target trace capture
