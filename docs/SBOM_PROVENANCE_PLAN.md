# SBOM And Provenance Plan

## Purpose

Define the local-first SBOM and provenance evidence boundary for
codex-dev-harness release bundles.

The current implementation is minimal and local-only. It generates SBOM and
provenance artifacts only when the local generator scripts are run explicitly.
It does not create release archives, signatures, tags, GitHub Releases, CI
workflows, dependencies, application code, device code, or live-write behavior.

## Why This Matters For A Template Repo

SBOM and provenance evidence can be useful even though this repository is a
template rather than an application:

- downstream adopters can see which files and development dependencies were
  present when a release evidence bundle was prepared
- reviewers can compare release-manifest file inventory with SBOM components
  and provenance materials
- local release evidence becomes easier to audit without copying private input,
  raw source bundles, or live configuration into the repository
- future distribution or compliance review can start from a documented boundary
  instead of inventing artifact shape during release closeout

## Relationship To Manifest And Checksums

The existing local release evidence baseline is:

- `artifacts/release-manifest.json`
- `artifacts/checksums.sha256`

SBOM and provenance artifacts build on that baseline:

- the release manifest remains the source for repository file inventory,
  file sizes, and SHA-256 file digests
- checksums remain the integrity evidence for generated release artifacts
- SBOM files should describe package/component inventory, not replace the
  release manifest
- provenance should describe how local evidence artifacts were produced, not
  claim cloud attestation or signed release status

## Minimal SPDX JSON Scope

`artifacts/sbom.spdx.json` includes only local, safe evidence:

- document metadata:
  - SPDX document name
  - SPDX version
  - data license
  - creation timestamp
  - creator tool name
- repository files:
  - path
  - SHA-256 digest when available from `release-manifest.json`
  - relationship to the repository package
- Python dev dependency metadata:
  - package names from `requirements-dev.txt`
  - version constraints when present
  - package download or registry metadata only if available locally or approved
- license fields:
  - known repository license value if the repository records one
  - `UNKNOWN` for unknown dependency licenses

The SPDX scope must not include private source, prompt/session text, tool-call
bodies, secrets, live configuration, or downstream generated target output.

## Minimal CycloneDX JSON Scope

`artifacts/sbom.cdx.json` includes:

- `bomFormat`, `specVersion`, and stable metadata fields
- metadata for this repository as the primary component
- tools metadata for the local generator
- components for repository-level and Python development dependency entries
- hashes where available from `release-manifest.json`
- optional future fields for services, models, or expanded provenance only
  after separate approval and only if they do not expose private or live target
  data

CycloneDX output should remain local-first and should not imply that this
template repository contains a deployable application service.

## Minimal In-Toto Provenance Scope

`artifacts/provenance.intoto.jsonl` describes local generation of release
evidence using a minimal in-toto-style statement:

- builder:
  - local generator identity
  - repository tool version or commit when available
- invocation:
  - command summaries
  - working repository reference
  - local-only execution context
- commands:
  - quality gate command summaries
  - manifest generation command
  - checksum generation command
  - SBOM/provenance generation commands if implemented later
- materials/input digests:
  - repository files from `release-manifest.json`
  - `requirements-dev.txt`
  - generator scripts
- products/output digests:
  - `artifacts/release-manifest.json`
  - `artifacts/checksums.sha256`
  - SBOM artifact digests when present

The provenance statement should not claim cloud attestation, CI generation,
signature status, release publication, or tag movement unless those actions are
explicitly approved and independently evidenced.

The provenance output does not include its own digest to avoid self-reference.

## Release Verification Wrapper

`scripts/run_release_verify.ps1` invokes the local SBOM and provenance
generators when they are present. Missing optional generators must be reported
as `SKIPPED` with a reason, not silently ignored.

The wrapper remains local-only. It must not call external services, publish
artifacts, sign artifacts, create release archives, install CI workflows, or
create or move tags.

## Output Path Safety

The local SBOM generator rejects output paths that would overwrite the input
manifest, checksum artifacts, the other SBOM output, or the provenance artifact.
The local provenance generator rejects output paths that would overwrite the
manifest, checksum artifacts, or SBOM artifacts.

## Current Implementation Files

- `scripts/generate_sbom.py`
- `scripts/generate_provenance.py`
- `artifacts/sbom.spdx.json`
- `artifacts/sbom.cdx.json`
- `artifacts/provenance.intoto.jsonl`

## Approval Boundary

The minimal local generators and artifacts are approved only for tasks that
explicitly name them. Expanding this implementation requires separate owner
approval. A future expansion approval should explicitly state:

- whether both SPDX and CycloneDX are required
- whether provenance is required
- whether generators must use Python standard library only
- whether generated artifacts are committed, ignored, or release-only outputs
- whether artifacts join any future expanded release verification wrapper
- whether any dependency or license metadata may be resolved from external
  sources

## Non-Goals

This plan does not add:

- cloud attestation
- registry publication
- signed release behavior
- CI-generated provenance
- GitHub Actions workflows
- tag creation or movement
- GitHub Release publication
- external dependency resolution
- aggressive license inference
- release archive creation
- artifact signing
- application, device, or live-write code
