# CI_POLICY.md

## Purpose

Define the current CI policy for codex-dev-harness without creating a GitHub Actions workflow.

## Current Policy

Local verification first.

The repository is not currently configured with active CI. Release readiness is
verified locally with documented commands, local release evidence, and recorded
closeout evidence.

Current decision: KEEP CI DEFERRED AND TEMPLATE-ONLY.

The current local evidence baseline includes:

- `scripts/run_local_verify.ps1`
- `scripts/run_release_verify.ps1`
- local pytest and quality gate verification
- standalone local evals
- local release manifest, checksum, SBOM, provenance, and optional eval report
  artifacts

These local surfaces are sufficient for the baseline. Active GitHub Actions
workflows remain deferred.

## Future Optional CI

GitHub Actions may be added in a future phase, but it is optional and requires
separate owner approval. If CI is introduced, it should start as a manual,
read-only workflow that only runs repository validation checks:

- `python -m pytest`
- `python scripts/quality_gate.py`
- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

Release verification may use:

- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_release_verify.ps1`

Installing any workflow under `.github/workflows/` is not approved by this
policy.

## CI Boundaries

CI must not introduce:

- Real application code.
- Real PLC/device code.
- Live target writes.
- Device start, stop, reset, or mode-change actions.
- Secret or live config generation.
- New profiles without a separate design and validation step.
- Artifact upload without a separate release-publication decision.
- Release publication, signing, tag creation, or tag movement.
- Deployment behavior.

## Release Relationship

CI is not required before a documentation-level release tag. A release tag
should still record local verification evidence and known limitations.

Artifact upload, release workflows, signing workflows, deployment workflows,
and tag movement remain separate explicit release-publication decisions. The
optional CI templates do not grant that approval.
