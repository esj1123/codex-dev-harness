# Optional GitHub Actions

## Purpose

GitHub Actions support is optional for codex-dev-harness. The baseline remains local-first: users should be able to clone the repository, install requirements, run tests, run the quality gate, and dry-run renders without cloud CI.

## Policy

- GitHub Actions are not required for the local-first baseline.
- No workflow file is installed under `.github/workflows` by default.
- The optional workflow template is documentation support, not an enabled CI system.
- CI must not create real application code, PLC/device code, live target writes, secrets, or live config.
- CI should only run tests, the quality gate, and render dry-runs.

## Template

Optional template path:

`templates/ci/github-actions-local-verify.yml.template`

To use it in a downstream fork or project, review it first and copy it manually to:

`.github/workflows/local-verify.yml`

Do not copy it automatically as part of this repository baseline.

## Recommended Checks

The optional workflow should run:
- dependency installation from `requirements-dev.txt`
- `python -m pytest`
- `python scripts/quality_gate.py`
- render dry-run for `examples/python_cli_minimal`
- render dry-run for `examples/csharp_desktop_minimal`
- render dry-run for `examples/plc_tool_minimal`

## Boundary

The optional workflow is only a cloud equivalent of local verification. It is not a deployment workflow, release workflow, device workflow, or project generator.
