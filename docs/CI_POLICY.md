# CI_POLICY.md

## Purpose

Define the current CI policy for codex-dev-harness after installing the
owner-approved read-only local verification GitHub Actions workflow.

## Current Policy

Local verification first, with one manual read-only GitHub Actions mirror.

The repository now includes the owner-approved first implementation target:
`.github/workflows/local-verify.yml`. It is a manual `workflow_dispatch`
workflow with `permissions: contents: read` and no artifact upload,
publication, signing, tag movement, deployment, downstream checkout, or live
target behavior.

The workflow also runs exactly `python scripts/run_eval.py` without report
flags after pytest and before the quality gate. This is console-only validation:
a nonzero exit fails that manually dispatched run, but does not create a
required check or release-blocking policy.

Release readiness remains verified locally with documented commands, local
release evidence, and recorded closeout evidence. The installed workflow is a
verification hygiene mirror, not release automation.

The current local evidence baseline includes:

- `scripts/run_local_verify.ps1`
- `scripts/run_release_verify.ps1`
- local pytest and quality gate verification
- standalone local evals
- local release manifest, checksum, SBOM, provenance, and optional eval report
  artifacts

These local surfaces are the baseline that CI must mirror when approved. The
installed workflow mirrors only the non-release local verification subset.
Additional workflows, triggers, permissions, required-check policies, artifact
upload, release verification CI, signing, tag movement, deployment, downstream
integration, or live behavior require a separate owner-approved implementation
task.

## First CI Implementation Target

The first CI implementation target is now implemented as
`.github/workflows/local-verify.yml`. Per the capability implementation roadmap,
CI starts as a manual read-only workflow that only runs repository validation
checks:

- `python -m pytest tests`
- `python scripts/run_eval.py`
- `python scripts/quality_gate.py`
- `python scripts/render_template.py --config examples/python_cli_minimal/template.config.yml --target examples/python_cli_minimal --dry-run`
- `python scripts/render_template.py --config examples/csharp_desktop_minimal/template.config.yml --target examples/csharp_desktop_minimal --dry-run`
- `python scripts/render_template.py --config examples/plc_tool_minimal/template.config.yml --target examples/plc_tool_minimal --dry-run`

The workflow also installs development requirements from `requirements-dev.txt`
and reads the Python version from `.python-version`.

Release verification remains local-only unless separately approved and may use:

- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_release_verify.ps1`

The installed local verification workflow does not run release verification,
generate an eval report, or upload artifacts.

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
- RAG, retrieval index, embeddings, or vector database behavior.
- Audit logging automation or audit receipt generation.
- Eval quality-gate integration, automatic-trigger or additional eval CI
  execution, routine eval report generation, required-check semantics, or
  release-blocking eval policy.
- MCP tool server, Hermes sidecar, or downstream product integration behavior.

## Verification Hygiene

Verification closeouts must distinguish:

- source checks that were run locally
- manual CI checks that were run through `.github/workflows/local-verify.yml`
- checks that were not run
- generated artifacts that were intentionally regenerated
- release evidence that was intentionally not regenerated

Documentation-only or policy-only changes may use focused verification when
the omitted checks are marked `NOT RUN` with a reason. Tasks that touch
generated output, release evidence, render behavior, quality gates, examples,
or scripts should run broader local verification unless the task explicitly
excludes it.

Line-ending warnings, if any, should be recorded as repository hygiene notes
unless they affect executable behavior or generated artifact content. A local
commit is not a push, tag, release, artifact upload, deployment, or publication.

## Release Relationship

CI is not required before a documentation-level release tag. A release tag
should still record local verification evidence and known limitations.

Artifact upload, release workflows, signing workflows, deployment workflows,
and tag movement remain separate explicit release-publication decisions. The
optional CI templates do not grant that approval.
