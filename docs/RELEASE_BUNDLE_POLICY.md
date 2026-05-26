# Release Bundle Policy

## Purpose

Define the release bundle evidence shape for codex-dev-harness.

The repository includes local-only generators for `release-manifest.json`,
`checksums.sha256`, minimal SBOMs, and minimal provenance. They produce
artifacts only when run explicitly. This policy does not create release
archives, eval reports, audit logs, GitHub Releases, tags, CI workflows,
application code, device code, or live-write behavior.

The repository also includes a local release verification wrapper at
`scripts/run_release_verify.ps1`. The wrapper runs local verification, optional
standalone evals, and available local release evidence generators. It does not
publish, upload, sign, archive, tag, or install CI workflows.

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
- dependency declaration files such as `.python-version`,
  `requirements-dev.txt`, and `requirements-dev.lock`
- template configuration examples
- approved release evidence files

Optional evidence such as eval reports and audit sessions must be included only
after separate owner approval. Minimal SBOM and provenance artifacts are allowed
only for tasks that explicitly name the local generators and artifact paths.

Future SBOM and provenance artifacts should relate back to
`release-manifest.json` and `checksums.sha256` rather than replacing them. The
manifest remains the file inventory and digest source; checksums remain the
integrity evidence for generated release artifacts.

Release evidence should record the Python runtime and development dependency
basis where available. `.python-version` records the preferred local
verification runtime, `requirements-dev.txt` records direct development
dependencies, and `requirements-dev.lock` records exact local verification
dependency pins. The release manifest inventory should include those files when
present so runtime reproducibility evidence is covered by manifest file hashes.

## Source Basis And Committed Artifact Location

Committed release evidence artifacts are local evidence products. The
`git_commit` recorded in `artifacts/release-manifest.json` should be interpreted
as the source basis used to generate the evidence.

When generated artifacts are committed, their repository location may be a later
commit than the manifest source basis. Release closeout should explicitly state
whether it is citing:

- the source basis commit from `release-manifest.json`
- the artifact-containing commit
- a tag that points at either source or artifact evidence
- all of the above

This distinction is expected for committed generated artifacts and does not
authorize release publication, signing, tag movement, archive creation, CI
upload, or broader release automation.

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

Bundle checksums must:

- use SHA-256
- use deterministic file ordering
- exclude volatile files
- avoid self-reference problems by not hashing the checksum file into itself
- include `release-manifest.json`
- include present local SBOM and provenance evidence artifacts
- include optional `eval-report.json` only when it is explicitly generated and
  present
- be regenerated only after all included files are final

The current checksum generator records the full present local release evidence
bundle except the checksum file itself. The strict release evidence set requires:

- `artifacts/release-manifest.json`
- `artifacts/sbom.spdx.json`
- `artifacts/sbom.cdx.json`
- `artifacts/provenance.intoto.jsonl`

`artifacts/eval-report.json` is included only if it is present. This policy does
not make routine eval report generation part of the baseline.

The local release verification wrapper may run an intermediate checksum
generation step with explicit missing-artifact allowance after manifest
generation. Its final checksum regeneration runs after SBOM and provenance
generation and uses the strict full-bundle requirement.

## Local Artifact Path Boundary

The current local manifest and checksum generators are limited to repository
relative `artifacts/` paths. Manifest output, checksum input, and checksum
output must reject absolute paths, parent traversal, and repo-internal
non-artifact paths such as `STATUS.md`, `docs/foo.md`, or `scripts/foo.py`.

The local SBOM and provenance generators use the same repo-relative
`artifacts/` boundary and must also reject overlapping paths that would
overwrite release-manifest, checksum, SBOM, or provenance evidence artifacts.

## Approval Boundary

Creating a local manifest, checksum file, SBOM, or provenance file is approved
only for tasks that explicitly allow the matching generator scripts and artifact
paths. Creating a broader release bundle, eval report, audit session entry,
release archive, GitHub Release, tag, signature, workflow, or externally
resolved metadata requires separate explicit owner approval.

Running `scripts/run_release_verify.ps1` is approved only as a local verification
and evidence-generation action. It does not grant approval for release archive
creation, publication, signing, CI installation, tag creation, or tag movement.

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
