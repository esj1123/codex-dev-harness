# Release Manifest Policy

## Purpose

Define a future machine-readable `release-manifest.json` contract for
codex-dev-harness release evidence without implementing a manifest generator.

The manifest is a future optional artifact. This policy does not create the
artifact, validate it, add scripts, install workflows, publish releases, or move
tags.

## Manifest Fields

A future `release-manifest.json` should include:

- `schema_version`
- `generated_at_utc`
- `repository`
- `git_ref`
- `git_commit`
- `git_tag`, if available
- `python_version`
- `included_roots`
- `excluded_patterns`
- `verification_commands`
- `quality_gates`
- `eval_summary`, if available
- `example_render_dry_runs`
- `files`

Each `files` entry should include:

- `path`
- `size_bytes`
- `sha256`

## Field Rules

`schema_version` should identify the manifest schema version.

`generated_at_utc` should use UTC and an unambiguous timestamp format.

`repository` should identify the repository, for example `owner/name`.

`git_ref`, `git_commit`, and `git_tag` should record the exact release basis.
`git_tag` is optional because local validation may happen before tagging.

`python_version` should record the runtime used for manifest generation or
verification.

`included_roots` should list approved repository roots included in the bundle.

`excluded_patterns` should record the exclusion policy applied to the bundle.

`verification_commands` should summarize commands used to validate the release
basis. Store command summaries and results, not raw private input or sensitive
logs.

`quality_gates` should record gate names and results.

`eval_summary` may be present only when eval evidence is separately approved
and available.

`example_render_dry_runs` should record example names, commands or command
summaries, and results.

`files` should be sorted deterministically by path.

## File Hash Rules

File hashes must use SHA-256.

The manifest should avoid self-reference problems:

- compute file hashes for bundle payload files before writing final checksums
- do not include a checksum file in its own checksum input
- define whether `release-manifest.json` is included in `checksums.txt`
- if the manifest is checksummed, write the manifest first, then checksum it
  from a final stable byte representation

## Determinism

Future manifest generation should use deterministic ordering for:

- included roots
- excluded patterns
- verification command records
- quality gate records
- eval summary entries
- example render dry-run entries
- file records

Volatile files and machine-local temporary paths should be excluded or
summarized in a stable, redacted form.

## Exclusion Policy

The manifest must record exclusions for:

- `.git/`
- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- raw source bundles
- private input
- live configuration
- downstream generated target output
- clean clone temporary folders
- secrets, credentials, tokens
- equipment connection details
- IP, port, tag, and live parameter values

## Approval Boundary

Generating `release-manifest.json`, `checksums.txt`,
`checksums.sha256`, SBOM files, provenance files, eval reports, audit session
logs, release archives, or GitHub Releases requires separate explicit owner
approval.

This policy does not authorize generator scripts or artifact creation.

## Non-Goals

This policy does not add:

- manifest generation code
- checksum generation code
- SBOM generation
- provenance generation
- eval report generation
- audit session generation
- release archive generation
- CI workflow installation
- tag creation or movement
- GitHub Release publication
