# Optional GitHub Actions

## Purpose

GitHub Actions support is optional for codex-dev-harness. The baseline remains local-first: users should be able to clone the repository, install requirements, run tests, run the quality gate, and dry-run renders without cloud CI.

## Current sequencing note

This record is historical CI policy evidence. It is superseded for
implementation sequencing by `docs/CAPABILITY_IMPLEMENTATION_ROADMAP.md`, which
makes read-only CI + verification hygiene the first implementation target while
preserving the no-secret, no-upload, no-release, no-tag, no-deploy, and no-live
write boundaries recorded here.

## Policy

- GitHub Actions are not required for the local-first baseline.
- No workflow file is installed under `.github/workflows` by default.
- Optional workflow templates are documentation support, not an enabled CI system.
- Historical decision at that time: keep CI deferred and template-only.
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

Do not copy templates automatically as part of this repository baseline.
Creating `.github/workflows/` in this repository requires a separate explicit
owner-approved workflow installation task.

## Recommended Checks

The optional local verification workflow should run:

- dependency installation from `requirements-dev.txt`
- `python -m pytest`
- `python scripts/quality_gate.py`
- render dry-run for `examples/python_cli_minimal`
- render dry-run for `examples/csharp_desktop_minimal`
- render dry-run for `examples/plc_tool_minimal`

The optional release verification workflow should run:

- dependency installation from `requirements-dev.txt`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_release_verify.ps1`

Both templates use `workflow_dispatch` by default, read-only permissions, and no
secrets. They do not upload generated release evidence artifacts.

## Actualization Decision

Historical decision at that time: keep CI deferred and template-only.

`docs/OPTIONAL_CI_ACTUALIZATION_DECISION.md` records why local-first
verification remains sufficient, why `scripts/run_release_verify.ps1` covers
current release verification needs, why no artifact upload is included by
default, and why owner approval is required before workflow installation.

Future manual read-only workflow installation, if approved, should name the
workflow path, trigger policy, permissions, dependency setup, commands, and
explicit exclusions for upload, publication, signing, tag movement, deployment,
secrets, and live-write behavior.

## Boundary

The optional workflows are cloud equivalents of local verification commands.
They are not deployment workflows, publication workflows, signing workflows,
device workflows, live-write workflows, or project generators.
