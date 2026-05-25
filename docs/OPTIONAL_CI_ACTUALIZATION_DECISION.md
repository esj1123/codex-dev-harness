# Optional CI Actualization Decision

## Purpose

Record the current decision for optional GitHub Actions release verification.

This document is planning and decision evidence. It does not install a workflow,
enable required checks, upload artifacts, publish releases, create or move tags,
deploy anything, or add application/device/live-write behavior.

## Decision

Decision: keep the repository baseline local-first and add only an optional
release verification workflow template.

The optional template is:

- `templates/ci/github-actions-release-verify.yml.template`

It is not active. It must be manually reviewed and copied into
`.github/workflows/` only after separate owner approval.

## Local-First Sufficiency

Local-first verification remains sufficient for the baseline.

Current local verification surfaces include:

- `scripts/run_local_verify.ps1`
- `scripts/run_release_verify.ps1`
- `python -m pytest`
- `python scripts/quality_gate.py`

These cover the current repository needs without requiring cloud CI.

## Release Verification Wrapper Coverage

`scripts/run_release_verify.ps1` covers the current local release verification
needs. It runs local verification, standalone eval when present,
manifest/checksum generation, available SBOM/provenance generation, final
checksum regeneration, and artifact path reporting.

The wrapper remains local-only. Running it in CI should be treated as a cloud
execution of the same local checks, not as release publication.

## Template-Only CI For Downstream Forks

Template-only CI is enough for downstream forks that want cloud verification
without changing this baseline. Fork owners can review the template, adapt it
to their risk posture, and install it manually.

The baseline repository should not install the workflow by default.

## Cloud CI Security Risks

Cloud CI changes the execution environment and can introduce risks:

- unreviewed pull request code may execute in a cloud runner
- logs may expose local paths or command output
- workflow permissions may be broadened accidentally
- future artifact upload can leak generated evidence or sensitive content
- secrets can be exposed if later added to the workflow
- cloud runners are not equivalent to local release evidence

The optional release verification template therefore uses read-only repository
permissions, requires no secrets, does not upload artifacts, and uses manual
`workflow_dispatch` by default.

## Artifact Upload Decision

Release artifacts should not be uploaded in CI by default.

The repository already treats release evidence as local-first. CI upload would
create a new publication and retention surface. Uploading artifacts requires a
separate owner-approved task that names the artifacts, retention rules,
redaction expectations, and safety checks.

## Installation Approval Boundary

Installing any workflow under `.github/workflows/` requires separate owner
approval.

Approval must identify:

- target workflow path
- trigger policy
- permission policy
- whether pull request execution is allowed
- whether artifacts are uploaded
- required checks, if any
- release, tag, publication, and signing exclusions
- verification expectations

This decision does not approve workflow installation.

## Non-Goals

This decision does not add:

- active GitHub Actions workflows
- required checks
- artifact upload
- deployment
- release publication
- signing
- tag creation or movement
- secrets
- application/device/live-write code
