# Release Manifest Policy

## Purpose

Define the machine-readable `release-manifest.json` contract for
codex-dev-harness release evidence.

The repository includes a local-only manifest generator at
`scripts/generate_manifest.py`. The generator writes a manifest only when run
explicitly. It does not install workflows, publish releases, move tags, call
external services, or generate SBOM/provenance artifacts by itself.

The local release verification wrapper at `scripts/run_release_verify.ps1` may
run the manifest and checksum generators together with separately approved
local SBOM/provenance generators when those scripts are present.

## Manifest Fields

`release-manifest.json` includes:

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
Runtime reproducibility evidence such as `.python-version`,
`requirements-dev.txt`, and `requirements-dev.lock` should be included when
present.

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

## Source Basis And Artifact Commit Semantics

`release-manifest.json` records `git_commit` as the source basis commit at
generation time. It identifies the repository content that the local evidence
generation process inspected.

When generated evidence artifacts are later committed to the repository, the
artifact-containing commit may be newer than the manifest `git_commit`. This is
expected unless the repository introduces a separate artifact commit field in a
future schema.

Formal release evidence should state both:

- the source basis commit recorded in `release-manifest.json`
- the artifact-containing commit or tag used for the final record

Regenerating artifacts after a final source commit can still produce a newer
artifact-containing commit if those generated artifacts are committed afterward.
That follow-on commit should not be treated as a mismatch by itself; closeout
records should describe which commit is the source basis and which commit or
tag contains the artifacts.

A future manifest schema may split the current `git_commit` meaning into
`source_basis_commit` and `artifact_commit`. This policy documents the
semantics only and does not change the manifest schema.

## File Hash Rules

File hashes must use SHA-256.

The manifest should avoid self-reference problems:

- compute file hashes for bundle payload files before writing final checksums
- do not include a checksum file in its own checksum input
- include `release-manifest.json` in the local release evidence checksum set
- write the manifest, SBOM, and provenance evidence first, then write
  `checksums.sha256` from their final stable byte representation

`checksums.sha256` covers the present local release evidence bundle and excludes
itself. The release manifest file inventory still excludes generated artifacts
under `artifacts/` by policy; artifact integrity is represented by the checksum
file rather than by the manifest payload inventory.

## Path Boundary

Manifest and checksum generation must write only to explicit repository-local
artifact paths:

- `generate_manifest.py --output` must be repo-relative and under `artifacts/`.
- `generate_checksums.py --manifest` must be repo-relative and under
  `artifacts/`.
- `generate_checksums.py --output` must be repo-relative and under
  `artifacts/`.

Generators must reject absolute paths, parent traversal, and repo-internal
non-artifact paths such as `STATUS.md`, `docs/foo.md`, or `scripts/foo.py`.

## Determinism

Manifest generation uses deterministic ordering for:

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

Generating `release-manifest.json` and `checksums.sha256` is approved only for
the local generator or release verification task that explicitly names those
outputs. Generating eval reports beyond existing standalone eval behavior,
audit session logs, release archives, or GitHub Releases requires separate
explicit owner approval.

This policy does not authorize CI integration, tag creation or movement, release
publication, external metadata lookup, artifact signing, or release archive
creation.

## Non-Goals

This policy does not add:

- SBOM/provenance external metadata lookup
- SBOM/provenance publication or signing
- eval report generation
- audit session generation
- release archive generation
- CI workflow installation
- tag creation or movement
- GitHub Release publication
