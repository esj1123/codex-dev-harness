# Optional GitHub Actions

## Purpose

GitHub Actions support is optional for codex-dev-harness. The baseline remains local-first: users should be able to clone the repository, install requirements, run tests, run the quality gate, and dry-run renders without cloud CI.

## Current sequencing note

This record is historical CI policy evidence. It is superseded for
implementation sequencing by `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, which
makes read-only CI + verification hygiene the first implementation target. That
target is now implemented as `.github/workflows/local-verify.yml`, while the
no-secret, no-upload, no-release, no-tag, no-deploy, and no-live-write
boundaries recorded here remain active.

## Policy

- GitHub Actions are not required for the local-first baseline.
- The owner-approved local verification workflow is installed at
  `.github/workflows/local-verify.yml`.
- Optional workflow templates remain documentation support for additional
  owner-approved workflows, not automatic installation instructions.
- Historical decision at that time: keep CI deferred and template-only. Current
  roadmap decision: install only the first read-only local verification
  workflow.
- CI must not create real application code, PLC/device code, live target writes, secrets, or live config.
- CI should only run safe verification commands.
- Release verification CI must not publish, upload artifacts, sign, tag, deploy,
  or write to live targets.
- Artifact upload, release workflows, signing, tag movement, deployment, and
  required checks require separate owner approval.

## Templates

Optional local verification template:

`templates/ci/github-actions-local-verify.yml.template`

Optional release verification template:

`templates/ci/github-actions-release-verify.yml.template`

To use a template in a downstream fork or project, review it first and copy it
manually to an appropriate path under:

`.github/workflows/`

Do not copy templates automatically as part of this repository baseline. The
only installed repository workflow is the owner-approved
`.github/workflows/local-verify.yml`. Copying the release verification template
or adding any additional workflow still requires a separate explicit
owner-approved workflow installation task.

## Recommended Checks

The installed local verification workflow runs:

- dependency installation from `requirements-dev.txt`
- `python -m pytest tests`
- `python scripts/quality_gate.py`
- render dry-run for `examples/python_cli_minimal`
- render dry-run for `examples/csharp_desktop_minimal`
- render dry-run for `examples/plc_tool_minimal`

The optional release verification workflow should run:

- dependency installation from `requirements-dev.txt`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_release_verify.ps1`

The installed local verification workflow uses `workflow_dispatch`, read-only
permissions, and no secrets. It does not upload generated release evidence
artifacts. The release verification template remains optional and uninstalled.

## Actualization Decision

Historical decision at that time: keep CI deferred and template-only. Current
roadmap implementation decision: actualize only the manual read-only local
verification workflow.

`docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md` records why local-first
verification remains sufficient, why `scripts/run_release_verify.ps1` covers
current release verification needs, why no artifact upload is included by
default, and why owner approval is required before workflow installation. That
document is historical risk evidence for the installed local verification
workflow and remains an approval boundary for any additional CI surface.

Any future workflow installation should name the workflow path, trigger policy,
permissions, dependency setup, commands, and explicit exclusions for upload,
publication, signing, tag movement, deployment, secrets, and live-write
behavior.

## Boundary

The installed local verification workflow and optional templates are cloud
equivalents of local verification commands. They are not deployment workflows,
publication workflows, signing workflows, device workflows, live-write
workflows, or project generators.
