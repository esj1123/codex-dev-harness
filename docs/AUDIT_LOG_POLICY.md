# Audit Log Policy

## Purpose

Define documentation-level audit log expectations for codex-dev-harness without creating a schema artifact or audit database.

This policy is the preferred Stage 1 audit step. A machine-readable schema such as `audits/audit-log.schema.json` is deferred unless explicitly approved in a separate task.

## Current Related Evidence

The repository already records audit-adjacent evidence in:

- `STATUS.md`
- `ACCEPTANCE_TRACE.md`
- release records under `docs/`
- clean clone validation records
- downstream adoption and feedback records
- decision and closeout records under `docs/`

These are related evidence foundations. They are not a dedicated audit log schema.

## Audit Event Fields

A future audit log entry should be able to capture:

- event id
- timestamp
- actor role or tool surface
- repository and basis ref
- requested action
- change class
- affected files or systems
- approval requirement
- approval evidence, if applicable
- commands or systems touched
- verification result
- safety checks
- result status
- evidence paths
- unresolved risks

## Content Rules

Audit records must not contain:

- secrets, keys, tokens, credentials, or account material
- private raw input
- raw source bundles
- sensitive requirement text
- equipment IPs, ports, tags, or live parameter values
- live configuration
- private downstream implementation details

Use summaries, identifiers, and evidence paths instead of copying sensitive content.

## When To Record Audit Evidence

Record audit evidence for:

- approval-gated changes
- release decisions
- tag or publication decisions
- optional pack integration decisions
- profile or example decisions
- eval harness decisions
- local package or release artifact decisions
- downstream feedback promotion decisions
- any task with NOT RUN verification that affects durable repo state

## Schema Deferral

Do not add `audits/audit-log.schema.json` in Stage 1 unless explicitly approved.

Before adding a schema, decide:

- whether audit records are Markdown, JSON, or both
- whether the schema is advisory or gate-enforced
- where audit entries are stored
- whether entries are generated manually or by tooling
- whether schema validation belongs in `quality_gate.py`

## Non-Goals

This policy does not create an audit directory, JSON schema, validator, database, workflow, release artifact, eval harness, application code, C# project asset, PLC/device code, or live-write behavior.
