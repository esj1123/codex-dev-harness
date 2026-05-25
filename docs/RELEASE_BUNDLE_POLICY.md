# Release Bundle Policy

## Purpose

Define the release bundle evidence shape for codex-dev-harness.

The repository includes local-only generators for `release-manifest.json`,
`checksums.sha256`, minimal SBOMs, and minimal provenance. They produce
artifacts only when run explicitly. This policy does not create release
archives, eval reports, audit logs, GitHub Releases, tags, CI workflows,
application code, device code, or live-write behavior.

## Release Bundle Components

A future release bundle may contain:

- `release-manifest.json`
- `checksums.txt` or `checksums.sha256`
- `eval-report.json`, if the eval harness is explicitly included in the bundle
- `sbom.spdx.json`, optional local evidence
- `sbom.cdx.json`, optional local evidence
- `provenance.intoto.jsonl`, optional local evidence
- `closeout.md`, human-readable
- `audits/session-*.jsonl`, future optional and redacted only

These names are reserved as future evidence component names. Their presence in
this policy does not authorize generating them.

SBOM and provenance scope is documented in `docs/SBOM_PROVENANCE_PLAN.md`.
The minimal local implementation does not authorize dependencies, external
metadata resolution, CI workflows, release publication, signatures, or tag
movement.

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

Optional evidence such as eval reports and audit sessions must be included only
after separate owner approval. Minimal SBOM and provenance artifacts are allowed
only for tasks that explicitly name the local generators and artifact paths.

Future SBOM and provenance artifacts should relate back to
`release-manifest.json` and `checksums.sha256` rather than replacing them. The
manifest remains the file inventory and digest source; checksums remain the
integrity evidence for generated release artifacts.

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

## Local Artifact Path Boundary

The current local manifest and checksum generators are limited to repository
relative `artifacts/` paths. Manifest output, checksum input, and checksum
output must reject absolute paths, parent traversal, and repo-internal
non-artifact paths such as `STATUS.md`, `docs/foo.md`, or `scripts/foo.py`.

## Approval Boundary

Creating a local manifest, checksum file, SBOM, or provenance file is approved
only for tasks that explicitly allow the matching generator scripts and artifact
paths. Creating a broader release bundle, eval report, audit session entry,
release archive, GitHub Release, tag, signature, workflow, or externally
resolved metadata requires separate explicit owner approval.

This policy alone does not grant approval to generate or publish anything.

## Non-Goals

This policy does not add:

- release archive generation
- SBOM/provenance publication, signing, or external metadata lookup
- audit log generation
- CI workflows
- release publication
- tag creation or movement
- application/device/live-write code
