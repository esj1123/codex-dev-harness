# Optional GitHub Actions

> **HISTORICAL TEMPLATE QUARANTINE - DO NOT COPY OR INSTALL.** The two files
> under `templates/ci/` are non-authoritative historical evidence. The
> canonical installed Hosted verifier is `.github/workflows/local-verify.yml`.
> The separately installed `.github/workflows/release-evidence-export.yml` is a
> release-evidence export workflow, not a Hosted verifier.

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
- The owner-approved canonical Hosted verification workflow is installed at
  `.github/workflows/local-verify.yml`.
- The separately approved release-evidence export workflow is installed at
  `.github/workflows/release-evidence-export.yml`; it does not establish
  `HOSTED_EXACT_SHA (V3)` evidence.
- The legacy workflow templates are historical evidence only. They are not
  installation instructions and must not be copied or installed.
- Historical decision at that time: keep CI deferred and template-only. Current
  roadmap decision: install only the first read-only local verification
  workflow.
- CI must not create real application code, PLC/device code, live target writes, secrets, or live config.
- CI should only run safe verification commands.
- Release verification CI must not publish, upload artifacts, sign, tag, deploy,
  or write to live targets.
- Artifact upload, release workflows, signing, tag movement, deployment, and
  required checks require separate owner approval.

## Historical Templates

Historical local verification template:

`templates/ci/github-actions-local-verify.yml.template`

Historical release verification template:

`templates/ci/github-actions-release-verify.yml.template`

Do not copy or install either template. Their action versions, dependency
commands, and safety comments describe an older design and are intentionally
not maintained as executable guidance. Any future workflow must be designed
from the current authority documents and separately approved; the existing
template bodies must not be used as a starting-point authority.

## Canonical Workflow Reference

The canonical installed Hosted verifier uses the exact dependency lock and
runs the current Core verify contract:

- dependency installation from `requirements-dev.lock` with hash and binary-only enforcement
- `python -m pytest tests -m "not optional_agent_quality and not optional_hermes_mcp and not optional_local_rag" --durations=50 -rs`
- `python scripts/run_eval.py` without report flags
- `python scripts/quality_gate.py`
- render dry-run for `examples/python_cli_minimal`
- render dry-run for `examples/csharp_desktop_minimal`
- render dry-run for `examples/plc_tool_minimal`

The installed Hosted Integration Verify workflow uses `workflow_dispatch`,
read-only repository permissions, and no secrets. It is the canonical Hosted
verifier and does not upload generated release evidence. The separately
installed `.github/workflows/release-evidence-export.yml` workflow is the only
approved export exception and transports the six approved files for one day.
That export is not Hosted verification. The release verification template
remains historical and uninstalled.

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
