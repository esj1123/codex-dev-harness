# Release Bundle Policy

## Purpose

Define the future release bundle evidence shape for codex-dev-harness without
implementing generators or producing artifacts.

This policy is documentation-first. It does not create release archives,
release manifests, checksums, SBOMs, provenance, eval reports, audit logs,
GitHub Releases, tags, CI workflows, application code, device code, or
live-write behavior.

## Release Bundle Components

A future release bundle may contain:

- `release-manifest.json`
- `checksums.txt` or `checksums.sha256`
- `eval-report.json`, if the eval harness is explicitly included in the bundle
- `sbom.spdx.json`, future optional
- `sbom.cdx.json`, future optional
- `provenance.intoto.jsonl`, future optional
- `closeout.md`, human-readable
- `audits/session-*.jsonl`, future optional and redacted only

These names are reserved as future evidence component names. Their presence in
this policy does not authorize generating them.

## Required Boundaries

Future release bundles must preserve the local-first baseline:

- no raw source bundles
- no private input
- no live configuration
- no secrets, credentials, keys, tokens, or account material
- no equipment connection details
- no IP, port, tag, or live parameter values
- no downstream generated target output
- no real application code
- no C# source, solution, project, XAML, or build assets
- no PLC/device code
- no live target write support

## Inclusion Policy

Future bundles should include only repository-controlled, reviewed evidence:

- root contract documents
- `docs/`
- `templates/`
- `profiles/`
- `scripts/`
- `scripts/gates/`
- `examples/`
- `tests/`
- dependency declaration files
- template configuration examples
- approved release evidence files

Optional evidence such as eval reports, SBOMs, provenance, and audit sessions
must be included only after separate owner approval.

## Exclusion Policy

Future release bundles must exclude:

- `.git/`
- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- raw source bundles
- private input
- live configuration
- downstream generated target output
- clean clone temporary folders
- secrets, credentials, keys, tokens, and account material
- equipment connection details
- IP, port, tag, and live parameter values
- local temporary adoption targets
- generated release archives unless explicitly selected as distribution outputs

## Verification Evidence

Future release bundles should summarize local verification without embedding
raw command logs by default:

- verification commands run
- quality gate names and PASS/FAIL/NOT RUN/ENVIRONMENT BLOCKED results
- eval summary, if an eval report is separately approved and available
- example render dry-run summary
- unresolved risks and assumptions

Use summaries and evidence paths rather than raw logs when raw logs could
include private input, secrets, local paths, or sensitive operational details.

## Checksum Policy

Future bundle checksums must:

- use SHA-256
- use deterministic file ordering
- exclude volatile files
- avoid self-reference problems by not hashing the checksum file into itself
- clearly state whether the manifest is included in the checksum set
- be regenerated only after all included files are final

## Approval Boundary

Creating a release bundle, manifest, checksum file, SBOM, provenance file, eval
report, audit session entry, release archive, GitHub Release, tag, or workflow
requires separate explicit owner approval.

This policy alone does not grant approval to generate or publish anything.

## Non-Goals

This policy does not add:

- generator scripts
- release artifacts
- SBOM or provenance tooling
- audit log generation
- CI workflows
- release publication
- tag creation or movement
- application/device/live-write code
